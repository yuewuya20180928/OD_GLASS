#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
boot_rescue_probe.py —— S2 救砖链路第 1 步的"识别"探针 (BOOT 模式探测)

================================================================================
它解决什么
--------------------------------------------------------------------------------
S2 = 进 BOOT 模式 → 用下载工具识别设备 → 刷回来。**第一步最容易被忽略**:
"我怎么知道板子真的进了 BOOT 模式?" 而不是"我以为它进了"。

判据不能靠感觉。本探针给出 3 条**互相独立**的证据, 任一条成立即可判定"进了 BOOT":
    E1  USB 枚举特征变了 (VID:PID / product 字符串与正常态不同) —— 最强证据
    E2  串口 log 出现 bootloader / download / fastboot / dfu 字样
    E3  BOOT 引脚电平实测 (由硬件侧提供, 本脚本只接收结论, 不假装能测)

★ 重要边界: 本脚本**不知道** ARS45 的 VID:PID (那是 P3 = [0数据])。
  配置里的签名表默认只有 3 条**通用示例**(其它平台常见下载模式), 明确标了
  source=generic-example —— 严禁把示例当 ARS45 的真值。ARS45 的签名必须来自
  原厂 (P3) 或空板阶段的协议分析仪抓包 (见 §4.5.5 L2)。

用法
--------------------------------------------------------------------------------
    # 0) 自测 (不需要任何硬件, 用来证明脚本本身的判定逻辑是对的)
    python3 SW/tools/boot_rescue_probe.py --selftest

    # 1) 无板时: 检查配置参数齐不齐 + 跑自测 (参数不齐就明确报, 不假装能跑)
    python3 SW/tools/boot_rescue_probe.py --dry-run --config SW/tools/s2_rescue_config.example.json

    # 2) 有板时: 扫描本机 USB, 判断是否处于 BOOT 模式
    python3 SW/tools/boot_rescue_probe.py --config SW/tools/s2_rescue_config.example.json \
        --out /tmp/s2_probe.json

退出码
--------------------------------------------------------------------------------
    0 = 已识别到 BOOT 模式设备 (或 --selftest / --dry-run 全部通过)
    1 = 未识别到 BOOT 模式设备
    2 = 参数不全 / 环境错误
    3 = 自测失败
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys

BOOT_LOG_KEYWORDS = ["bootloader", "u-boot", "fastboot", "dfu", "download mode",
                     "rom code", "enter download", "usb boot"]
USB_ID_RE = re.compile(r"^([0-9a-fA-F]{4}):([0-9a-fA-F]{4})$")


# ----------------------------------------------------------------------------- 采集
def enumerate_sysfs() -> list[dict]:
    """从 /sys/bus/usb/devices 枚举 USB 设备 (Linux, 无需 root)。"""
    base = "/sys/bus/usb/devices"
    out: list[dict] = []
    if not os.path.isdir(base):
        return out
    for entry in sorted(os.listdir(base)):
        path = os.path.join(base, entry)
        if not os.path.isdir(path):
            continue
        vid = _read(path, "idVendor")
        pid = _read(path, "idProduct")
        if not vid or not pid:
            continue  # interface / hub 类节点
        out.append({
            "node": entry,
            "vid": vid.lower(),
            "pid": pid.lower(),
            "product": _read(path, "product"),
            "manufacturer": _read(path, "manufacturer"),
            "serial": _read(path, "serial"),
            "bcdDevice": _read(path, "bcdDevice"),
            "busnum": _read(path, "busnum"),
            "devnum": _read(path, "devnum"),
        })
    return out


def _read(path: str, name: str) -> str:
    try:
        with open(os.path.join(path, name), "r", encoding="utf-8", errors="replace") as f:
            return f.read().strip()
    except OSError:
        return ""


def enumerate_lsusb() -> list[dict]:
    """lsusb 兜底 (部分环境 /sys 里看不到的产品名更全)。"""
    try:
        raw = subprocess.run(["lsusb"], capture_output=True, text=True, timeout=10).stdout
    except (OSError, subprocess.SubprocessError):
        return []
    out = []
    for line in raw.splitlines():
        m = re.search(r"Bus \d+ Device \d+: ID ([0-9a-fA-F]{4}):([0-9a-fA-F]{4})\s*(.*)", line)
        if m:
            out.append({"vid": m.group(1).lower(), "pid": m.group(2).lower(),
                        "product": m.group(3).strip(), "node": "lsusb"})
    return out


def dmesg_tail(lines: int = 200) -> tuple[list[str], str]:
    """抓 dmesg 尾部 (可能需要权限; 抓不到不算失败, 只是少一条证据)。"""
    try:
        raw = subprocess.run(["dmesg", "--level=err,warn,info", "--since", "10 min ago"],
                             capture_output=True, text=True, timeout=10)
        text = raw.stdout or ""
    except (OSError, subprocess.SubprocessError):
        return [], "dmesg 不可用 (权限或命令缺失) —— E2 证据缺失"
    if not text:
        try:
            text = subprocess.run(["dmesg"], capture_output=True, text=True, timeout=10).stdout
        except (OSError, subprocess.SubprocessError):
            return [], "dmesg 不可用 (权限或命令缺失) —— E2 证据缺失"
    tail = text.strip().splitlines()[-lines:]
    return tail, ""


# ----------------------------------------------------------------------------- 判定
def match_signature(dev: dict, signatures: list[dict]) -> dict | None:
    """把一个 USB 设备与签名表比对, 命中返回签名, 否则 None。"""
    for sig in signatures:
        if sig.get("vid", "").lower() == dev.get("vid", "").lower() and \
           sig.get("pid", "").lower() == dev.get("pid", "").lower():
            return sig
    return None


def scan_log_for_boot(log_lines: list[str]) -> list[str]:
    hits = []
    for line in log_lines:
        low = line.lower()
        for kw in BOOT_LOG_KEYWORDS:
            if kw in low:
                hits.append(f"[{kw}] {line.strip()}")
                break
    return hits


def check_params(cfg: dict) -> list[dict]:
    """4 个 0 数据项是否已填 (P1..P4)。"""
    params = cfg.get("params", {}) or {}
    out = []
    for key in ("P1_BOOT_ENTER_SPEC", "P2_DL_TOOL", "P3_USB_PHY", "P4_BOOT_STORE"):
        p = params.get(key, {}) or {}
        val = p.get("value")
        filled = val not in (None, "", [], {})
        out.append({
            "key": key,
            "filled": filled,
            "status": p.get("status", "TODO"),
            "owner": p.get("owner", ""),
            "need_key": p.get("need_key", ""),
        })
    return out


def verdict(devices: list[dict], signatures: list[dict], log_hits: list[str]) -> dict:
    matched = []
    for d in devices:
        sig = match_signature(d, signatures)
        if sig:
            matched.append({"device": d, "signature": sig})
    if matched:
        return {"verdict": "BOOT_IDENTIFIED", "matched": matched, "log_hits": log_hits}
    if log_hits:
        return {"verdict": "BOOT_SUSPECTED_BY_LOG", "matched": [], "log_hits": log_hits}
    return {"verdict": "NOT_IDENTIFIED", "matched": [], "log_hits": log_hits}


# ----------------------------------------------------------------------------- 自测
def selftest() -> int:
    """纯逻辑单元自测 (不需要硬件)。这是"无板先验"里唯一能 100% 机械判的部分。"""
    cases = []

    sigs = [{"vid": "0451", "pid": "6146", "label": "TI DFU"},
            {"vid": "0483", "pid": "df11", "label": "STM32 DFU"}]

    # T1: 精确命中
    cases.append(("T1 精确命中 VID:PID",
                  match_signature({"vid": "0451", "pid": "6146"}, sigs) is not None))
    # T2: 十六进制大小写不敏感
    cases.append(("T2 VID/PID 十六进制大小写不敏感",
                  match_signature({"vid": "1d6b", "pid": "0002"},
                                  [{"vid": "1D6B", "pid": "0002"}]) is not None))
    # T3: PID 不同不能命中
    cases.append(("T3 PID 不符不命中",
                  match_signature({"vid": "0451", "pid": "1234"}, sigs) is None))
    # T4: 空签名表不命中
    cases.append(("T4 空签名表不命中",
                  match_signature({"vid": "0451", "pid": "6146"}, []) is None))
    # T5: 日志关键字命中
    cases.append(("T5 日志关键字命中 (fastboot)",
                  len(scan_log_for_boot(["U-Boot 2019.04", "fastboot mode entered"])) == 2))
    # T6: 无关日志不命中
    cases.append(("T6 无关日志不命中",
                  scan_log_for_boot(["xhci_hcd 0000:00:14.0: xhci URBC BC"]) == []))
    # T7: 参数检查: 4 个 0 数据项未填时必须报 unfilled
    empty_cfg = {"params": {"P1_BOOT_ENTER_SPEC": {"value": None},
                            "P2_DL_TOOL": {"value": None},
                            "P3_USB_PHY": {"value": None},
                            "P4_BOOT_STORE": {"value": None}}}
    cases.append(("T7 4 个 0 数据项未填 -> 全部 unfilled",
                  all(not p["filled"] for p in check_params(empty_cfg))))
    # T8: 参数填了就不再报 unfilled
    filled_cfg = {"params": {"P1_BOOT_ENTER_SPEC": {"value": "x"}, "P2_DL_TOOL": {"value": "y"},
                             "P3_USB_PHY": {"value": "z"}, "P4_BOOT_STORE": {"value": "w"}}}
    cases.append(("T8 4 个 0 数据项填齐 -> 全部 filled",
                  all(p["filled"] for p in check_params(filled_cfg))))
    # T9: verdict 在无命中时给 NOT_IDENTIFIED
    v = verdict([{"vid": "1111", "pid": "2222"}], sigs, [])
    cases.append(("T9 无匹配 -> NOT_IDENTIFIED", v["verdict"] == "NOT_IDENTIFIED"))
    # T10: verdict 在命中时给 BOOT_IDENTIFIED
    v = verdict([{"vid": "0451", "pid": "6146"}], sigs, [])
    cases.append(("T10 命中 -> BOOT_IDENTIFIED", v["verdict"] == "BOOT_IDENTIFIED"))

    print("=" * 78)
    print("boot_rescue_probe 自测 (纯逻辑, 无需硬件)")
    print("=" * 78)
    n_fail = 0
    for name, ok in cases:
        print(f"{'✅' if ok else '❌'} {name}")
        if not ok:
            n_fail += 1
    print("-" * 78)
    print(f"结论: {'PASS' if n_fail == 0 else 'FAIL'} ({len(cases) - n_fail}/{len(cases)} 通过)")
    print("证据: [实测] PC 侧自测 (脚本判定逻辑), 不代表板端已通")
    return 0 if n_fail == 0 else 3


# ----------------------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser(description="ARS45 S2 救砖链路 BOOT 模式识别探针")
    ap.add_argument("--config", default=None, help="S2 配置文件")
    ap.add_argument("--selftest", action="store_true", help="只跑纯逻辑自测")
    ap.add_argument("--dry-run", action="store_true", help="无板模式: 检查参数齐不齐 + 跑自测")
    ap.add_argument("--out", default=None, help="JSON 报告输出路径")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    if not args.config:
        print("❌ 需要 --config (或用 --selftest)", file=sys.stderr)
        return 2
    if not os.path.exists(args.config):
        print(f"❌ 配置文件不存在: {args.config}", file=sys.stderr)
        return 2
    with open(args.config, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    params = check_params(cfg)
    unfilled = [p for p in params if not p["filled"]]
    sigs = (cfg.get("usb_signatures", {}) or {}).get("entries", []) or []

    if args.dry_run:
        rc = selftest()
        print("-" * 78)
        print("参数齐备性 (P1..P4 = 原厂 4 个 0 数据项):")
        for p in params:
            mark = "✅" if p["filled"] else "⬜"
            print(f"{mark} {p['key']:<22} status={p['status']:<6} need={p['need_key']}")
        if unfilled:
            print(f"结论: ⬜ 参数不全 ({len(unfilled)}/4 未填) → **现在还不能真跑 S2**, "
                  f"但 L0/L1 先验可做")
            print("      (未填项一律标 [0数据], 严禁用通用示例冒充真值)")
            return 3 if rc else 2
        print("结论: ✅ 参数齐备, 可以跑真实 S2 探测")
        return rc

    devices = enumerate_sysfs()
    lsusb_devs = enumerate_lsusb()
    seen = {(d["vid"], d["pid"], d["node"]) for d in devices}
    for d in lsusb_devs:
        if (d["vid"], d["pid"], d["node"]) not in seen:
            devices.append(d)
    log_lines, log_err = dmesg_tail()
    log_hits = scan_log_for_boot(log_lines)
    v = verdict(devices, sigs, log_hits)

    report = {
        "tool": "boot_rescue_probe.py",
        "config": args.config,
        "devices": devices,
        "signatures_loaded": sigs,
        "signature_note": "签名表里 source=generic-example 的条目是通用示例, 不是 ARS45 真值",
        "log_hits": log_hits,
        "log_error": log_err,
        "verdict": v["verdict"],
        "matched": v["matched"],
        "params_filled": {p["key"]: p["filled"] for p in params},
        "unfilled_params": [p["key"] for p in unfilled],
        "evidence": "[实测] PC 侧探测; ARS45 的真实 VID:PID = [0数据] (P3)",
    }
    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text)
    if args.json:
        print(text)
    else:
        print("=" * 78)
        print(f"BOOT 模式探测: 判定 = {v['verdict']}")
        print("=" * 78)
        print(f"USB 设备 {len(devices)} 个:")
        for d in devices:
            print(f"   {d['vid']}:{d['pid']}  {d.get('product', '')} "
                  f"[{d.get('manufacturer', '')}]  node={d['node']}")
        print(f"日志命中 {len(log_hits)} 条:")
        for h in log_hits[:10]:
            print(f"   {h}")
        if log_err:
            print(f"   (注: {log_err})")
        print(f"未填参数: {report['unfilled_params'] or '无'}")
        print(f"证据: {report['evidence']}")

    if v["verdict"] == "BOOT_IDENTIFIED":
        return 0
    # BOOT_SUSPECTED_BY_LOG 也不能算过 —— 证据不足, 必须靠枚举特征确认
    return 1


if __name__ == "__main__":
    sys.exit(main())
