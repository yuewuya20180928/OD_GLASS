#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s2_board_selftest.py —— 板端启动自检 6 项 (CB-04) + 版本串 (CB-03) + 标定 (CB-07) + 日志扫错 (CB-09)

================================================================================
它解决什么
--------------------------------------------------------------------------------
EVT_TEMPLATE.md §11.2 的 CB-04 写的是"启动自检 6 项", 但 §11.8 的 BR-R3 一直挂着
"板端自检程序尚未编写"。投板那天现场写脚本 = 现场发明 = 现场出错。

本脚本把那 6 项**参数化**成配置文件里的 6 条命令, 跑完落一份机器可读 JSON,
交给 s2_board_judge.py 判 CB-03 / CB-04 / CB-07 / CB-09。

    1. DDR 自检        2. sensor 枚举     3. 光机 I2C 应答
    4. NPU 模型加载    5. OD 跑通 1 帧     6. 版本块回显

★ 三条纪律 (ISS-080 口径):
  1) 命令没配 ⇒ 该项判 **UNVERIFIED (未验)**, 不许跳过、不许默认过。
  2) 命令跑了但返回码非 0 ⇒ 判 **FAIL**; 返回 0 但输出为空 ⇒ 判 **FAIL**
     (防止"命令存在但什么都没干"被当成过)。
  3) 模型 sha8 没实测到 ⇒ CB-03 的 R3 判未验; **不许拿版本串里写的 sha8 反推自己**。

执行位置
--------------------------------------------------------------------------------
  本机 + adb (默认): adb shell <命令> 逐条跑
  板上直接跑:        把本脚本 push 到板子, 用板端 python3 跑 (--remote 表示命令已在本板执行)
  离线自测:          --selftest (合成数据, 不需要板)

退出码
--------------------------------------------------------------------------------
  0 = 6 项全过 / 1 = 有项不通过 / 2 = 有项未验 / 3 = 环境错误
"""
from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys

PASS, FAIL, UNVER = "PASS", "FAIL", "UNVERIFIED"

ITEMS = [
    ("ddr", "DDR 自检"),
    ("sensor", "sensor 枚举"),
    ("i2c", "光机 I2C 应答"),
    ("npu", "NPU 模型加载"),
    ("od", "OD 跑通 1 帧"),
    ("version", "版本块回显"),
]

ERR_CODES = ["E_MODEL_MISMATCH", "E_CALIB_MISSING", "E_SN_MISMATCH"]
ERR_PREFIX = "E_VER_"


def load_cfg(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_cmd(cmd, remote: bool, timeout: int = 120) -> tuple[int, str]:
    """跑一条命令。remote=True 表示命令在板子上直接执行 (不经 adb 转发)。"""
    if isinstance(cmd, str):
        cmd = shlex.split(cmd)
    if not cmd:
        return 127, ""
    argv = list(cmd)
    if not remote and argv[0] not in ("adb",):
        argv = ["adb", "shell"] + argv
    try:
        p = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
        return p.returncode, ((p.stdout or "") + (p.stderr or ""))
    except subprocess.TimeoutExpired:
        return 124, f"[超时] 超过 {timeout}s"
    except Exception as e:  # noqa: BLE001
        return 127, f"[调用失败] {e}"


def board_version(cfg: dict, remote: bool, log_lines: list[str]) -> tuple[str, str]:
    """读版本串 (CB-03/CB-07 的输入)。优先跑配置里的命令, 其次读版本文件。"""
    st = ((cfg.get("board_test") or {}).get("selftest") or {})
    cmd = st.get("version")
    if cmd:
        rc, out = run_cmd(cmd, remote)
        if rc == 0 and out.strip():
            for line in out.splitlines():
                line = line.strip()
                if line.startswith("ARS45-SW"):
                    return line, "selftest.version 命令"
            return out.strip().splitlines()[0] if out.strip() else "", "selftest.version 命令"
    vf = st.get("version_file") or "/etc/version"
    if not remote:
        rc, out = run_cmd(["cat", vf], remote)
        if rc == 0 and out.strip():
            return out.strip().splitlines()[0], f"adb shell cat {vf}"
    else:
        try:
            with open(vf, "r", encoding="utf-8", errors="replace") as f:
                return f.read().strip().splitlines()[0], f"直接读 {vf}"
        except OSError:
            pass
    return "", "[0数据] 版本串没读到"


def model_sha8(cfg: dict, remote: bool) -> str | None:
    """板上模型文件的 sha256 前 8 位 (CB-03 的 R3)。★ 读不到就 None, 不许猜。"""
    mp = ((cfg.get("board_test") or {}).get("selftest") or {}).get("model_path")
    if not mp:
        return None
    rc, out = run_cmd(["sha256sum", mp], remote)
    if rc == 0 and out.strip():
        h = out.strip().split()[0]
        if len(h) >= 8:
            return h[:8]
    return None


def scan_log(lines: list[str]) -> dict:
    """扫错误码 (CB-09)。"""
    errors = []
    for line in lines:
        for code in ERR_CODES:
            if code in line:
                errors.append(f"{code}: {line.strip()[:160]}")
        for tok in line.split():
            if tok.startswith(ERR_PREFIX) and tok not in errors:
                errors.append(f"{tok}: {line.strip()[:160]}")
    seen = set()
    uniq = []
    for e in errors:
        if e not in seen:
            seen.add(e)
            uniq.append(e)
    return {"scanned_lines": len(lines), "errors": uniq}


def do_selftest(cfg: dict, remote: bool, break_item: str = "") -> dict:
    """跑 6 项。命令没配 → UNVERIFIED; 跑了但 rc≠0 或输出空 → FAIL。"""
    st = ((cfg.get("board_test") or {}).get("selftest") or {})
    results = {}
    log_lines = []
    for key, name in ITEMS:
        if break_item == key:
            results[key] = {"status": UNVER, "detail": "自测注入: 本项未验"}
            continue
        cmd = st.get(key)
        if not cmd:
            results[key] = {"status": UNVER, "detail": f"{name}: 命令未配置 (board_test.selftest.{key})"}
            continue
        rc, out = run_cmd(cmd, remote)
        log_lines.extend(out.splitlines())
        if rc != 0:
            results[key] = {"status": FAIL, "detail": f"{name}: rc={rc} ({out.strip()[:120] or '无输出'})"}
        elif not out.strip():
            results[key] = {"status": FAIL, "detail": f"{name}: rc=0 但输出为空 —— 什么都没干, 不算过"}
        else:
            results[key] = {"status": PASS, "detail": f"{name}: rc=0, 输出 {len(out)} 字节"}
    return {"selftest": results, "log_lines": log_lines}


def synth_selftest(break_item: str = "") -> dict:
    """自测用的合成数据 (不跑任何命令)。"""
    results = {}
    for key, name in ITEMS:
        if break_item == key:
            results[key] = {"status": UNVER, "detail": "自测注入: 本项未验"}
        else:
            results[key] = {"status": PASS, "detail": f"{name}: rc=0, 输出 42 字节"}
    return results


def synth_version() -> str:
    return ("ARS45-SW 1.0.0+g1234abc board=EVT1 sn=ARS45-EVT1-0007 build=20261030T0000+0800 "
            "boot=0.0.0 kern=5.10.0-gdeadbee rootfs=R20261030.1 app=1.0.0+g1234abc "
            "model=yolov5s-int8-ag2-1a2b3c4d isp=ISP-CALIB-0003-r2 mode=prod calib=ISP-CALIB-0003-r2")


def selftest_mode(break_item: str = "") -> int:
    """离线自测: 合成数据 → 判 rc。不需要板子。"""
    res = synth_selftest(break_item)
    statuses = [v["status"] for v in res.values()]
    if FAIL in statuses:
        rc = 1
    elif UNVER in statuses:
        rc = 2
    else:
        rc = 0
    print("=" * 78)
    print("s2_board_selftest 自测 (纯逻辑, 无需硬件)")
    print("=" * 78)
    for k, v in res.items():
        print(f"  {v['status']:<11} {k:<9} {v['detail']}")
    print("-" * 78)
    print(f"结论: rc={rc} (0=全过 1=有项不通过 2=有项未验)")
    print("证据: [实测] PC 侧合成自测 (判定逻辑), 不代表板端 S2 已通")
    return rc


def main() -> int:
    ap = argparse.ArgumentParser(description="S2 板端启动自检 6 项 (CB-04)")
    ap.add_argument("--config", default="SW/tools/s2_rescue_config.json")
    ap.add_argument("--out", default=None, help="结果 JSON 输出路径")
    ap.add_argument("--log", default=None, help="板端日志落盘路径")
    ap.add_argument("--remote", action="store_true", help="命令在板子上直接执行 (不经 adb 转发)")
    ap.add_argument("--selftest", action="store_true", help="离线自测")
    ap.add_argument("--break", dest="break_item", default="",
                    help="自测注入: 指定某项未验 (自测用)")
    args = ap.parse_args()

    if args.selftest:
        return selftest_mode(args.break_item)

    if not os.path.exists(args.config):
        print(f"❌ 配置不存在: {args.config}", file=sys.stderr)
        return 3
    cfg = load_cfg(args.config)

    data = do_selftest(cfg, args.remote)
    log_lines = data.pop("log_lines")
    ver, ver_src = board_version(cfg, args.remote, log_lines)
    sha8 = model_sha8(cfg, args.remote)
    scan = scan_log(log_lines)

    rec = {
        "tool": "s2_board_selftest.py",
        "selftest": data["selftest"],
        "version_string": ver,
        "version_source": ver_src,
        "model_sha8": sha8,
        "log_scan": scan,
        "evidence": "[实测] 板端命令实际输出; 未配命令判 UNVERIFIED, 不许默认过",
    }
    text = json.dumps(rec, ensure_ascii=False, indent=2)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text)
    if args.log:
        with open(args.log, "w", encoding="utf-8") as f:
            f.write("\n".join(log_lines))
    print(text)

    statuses = [v["status"] for v in rec["selftest"].values()]
    if FAIL in statuses:
        return 1
    if UNVER in statuses:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
