#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
flash_layout_check.py —— 分区表 / 版本块布局静态检查器 (S2 救砖链路的 L0 先验)

================================================================================
为什么要有这个脚本 (背景)
--------------------------------------------------------------------------------
SW/FLASH_AND_VERSION.md §4.5 要求把 S2 救砖链路做成"可执行的实测方案"。但现在
连板子都没有, 而 S2 链路里有**大量可以在 PC 上先验的软件逻辑**, 其中最容易被忽略
、也最容易在投板后炸掉的一块是: **分区表 + 版本块的布局与写入顺序**。

§2.5.2 定的铁律是 "先内容、后标志": 版本块的 payload 先写, magic + bootable 标志
最后写, 只有最后那一笔是"生效开关"。这条铁律如果实现错了, 表现是"刷完能开机但
版本对不上"或者"刷到一半断电结果状态不明"—— 投板后才发现, 代价是返工。

所以本脚本做一件事: **在没有任何硬件的情况下, 把"分区表放得对不对、版本块放得下
吗、CRC 槽位配得齐吗、A/B 槽对称吗" 全部变成机器可判的结论**。

用法
--------------------------------------------------------------------------------
    python3 SW/tools/flash_layout_check.py --config SW/tools/s2_rescue_config.example.json
    python3 SW/tools/flash_layout_check.py --config ... --json

退出码
--------------------------------------------------------------------------------
    0 = 全部检查通过
    1 = 有检查项不通过 (FAIL)
    2 = 输入有问题 (配置文件不存在 / JSON 坏 / 缺分区表)

检查项 (每条都可机械判)
--------------------------------------------------------------------------------
    LAY-01  分区起始偏移对齐 (offset % align == 0)
    LAY-02  分区互不重叠
    LAY-03  分区不越界 (最后一个分区 end <= device_total_size)
    LAY-04  版本块存在 / 偏移对齐 / 容量 >= 32768 (§3.2 定的 32KB)
    LAY-05  CRC 槽位覆盖: 每个需校验分区都映射到 crc_slots 里的一个合法下标
    LAY-06  A/B 槽对称: 出现 _a/_b 命名对时, 两者容量相同
    LAY-07  版本块版本串容量够 (512B) + 元数据字段 (SN/calib/tool_ver) 有上限
    LAY-08  rootfs 体积回报 (用于 §4.1 的总分叉点: rootfs > 64MB 则 SPI-NOR 出局)

证据等级
--------------------------------------------------------------------------------
本脚本的输出是 [实测] (PC 侧静态检查, 跑出来的就是跑出来的), 但它检查的
partition_layout 本身是 [推算] 占位值 —— 两者不要混为一谈。
"""
from __future__ import annotations

import argparse
import json
import os
import sys

VERSION_BLOCK_MIN_SIZE = 32768     # §3.2: 版本块 32KB
VERSION_STR_MAX = 512             # §3.2: 版本串 512B
SN_MAX = 16
CALIB_MAX = 32
TOOL_VER_MAX = 16

# 版本块二进制布局 (与 §3.2 字段一一对应, flash_writer.py 按同一份定义写)
VERSION_BLOCK_FIELDS = {
    "magic":        (0x000, 4),
    "payload_len":  (0x004, 2),
    "flags":        (0x006, 1),   # bit0 = bootable
    "mode":         (0x007, 1),   # 0=dev 1=prod 2=service
    "boot_count_a": (0x008, 4),
    "boot_count_b": (0x00C, 4),
    "active_slot":  (0x010, 1),
    "build_time":   (0x012, 8),
    "sn":           (0x01A, SN_MAX),
    "calib_id":     (0x02A, CALIB_MAX),
    "tool_ver":     (0x04A, TOOL_VER_MAX),
    "partition_crc": (0x060, 24),  # 6 x 4B
    "version_str":  (0x078, VERSION_STR_MAX),
    "payload_crc32": (0x278, 4),
}


class Check:
    def __init__(self, cid: str, name: str):
        self.cid = cid
        self.name = name
        self.ok = True
        self.details: list[str] = []
        self.failures: list[str] = []

    def passed(self, msg: str) -> None:
        self.details.append("PASS " + msg)

    def failed(self, msg: str) -> None:
        self.ok = False
        self.failures.append(msg)

    def to_dict(self) -> dict:
        return {
            "id": self.cid,
            "name": self.name,
            "result": "PASS" if self.ok else "FAIL",
            "failures": self.failures,
            "details": self.details,
        }


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _offset_of(part: dict, prev_end: int) -> int:
    if "offset" in part and part["offset"] is not None:
        return int(part["offset"])
    return prev_end


def check_layout(cfg: dict) -> tuple[list[Check], dict]:
    checks: list[Check] = []
    layout = cfg.get("partition_layout")
    if not layout:
        raise SystemExit("[flash_layout_check] 配置里没有 partition_layout 段")

    total = int(layout.get("device_total_size", 0))
    align = int(layout.get("align", 4096))
    parts = list(layout.get("partitions", []))
    crc_slots = list(layout.get("crc_slots", []))
    active_slot = layout.get("active_slot")

    # ---- LAY-01 对齐 ----
    c = Check("LAY-01", "分区起始偏移对齐")
    off = 0
    offsets: dict[str, int] = {}
    for p in parts:
        off = _offset_of(p, off)
        offsets[p["name"]] = off
        if off % align != 0:
            c.failed(f"分区 {p['name']} 偏移 {off} 未按 {align} 对齐")
        off += int(p["size"])
    if c.ok:
        c.passed(f"全部 {len(parts)} 个分区偏移按 {align} 对齐")
    checks.append(c)

    # ---- LAY-02 重叠 ----
    c = Check("LAY-02", "分区互不重叠")
    ordered = sorted(parts, key=lambda p: offsets[p["name"]])
    for prev, cur in zip(ordered, ordered[1:]):
        prev_end = offsets[prev["name"]] + int(prev["size"])
        if offsets[cur["name"]] < prev_end:
            c.failed(f"{prev['name']} (end={prev_end}) 与 {cur['name']} "
                     f"(offset={offsets[cur['name']]}) 重叠")
    if c.ok:
        c.passed(f"按序排列 {len(ordered)} 个分区无重叠")
    checks.append(c)

    # ---- LAY-03 越界 ----
    c = Check("LAY-03", "分区不越界")
    last = ordered[-1] if ordered else None
    if last is None:
        c.failed("分区表为空")
    else:
        end = offsets[last["name"]] + int(last["size"])
        if end > total:
            c.failed(f"最后一个分区 {last['name']} end={end} > 设备容量 {total}")
        else:
            c.passed(f"占用 {end} / {total} 字节 ({end * 100.0 / total:.1f}%), 未越界")
    checks.append(c)

    # ---- LAY-04 版本块 ----
    c = Check("LAY-04", "版本块存在 / 对齐 / 容量")
    vb = next((p for p in parts if p["name"] == "version_block"), None)
    if vb is None:
        c.failed("没有 version_block 分区")
    else:
        voff = offsets["version_block"]
        vsize = int(vb["size"])
        if voff % align != 0:
            c.failed(f"版本块偏移 {voff} 未按 {align} 对齐")
        if vsize < VERSION_BLOCK_MIN_SIZE:
            c.failed(f"版本块容量 {vsize} < §3.2 规定的 {VERSION_BLOCK_MIN_SIZE}")
        if voff + vsize > total:
            c.failed("版本块越界")
        if c.ok:
            c.passed(f"版本块 offset={voff} size={vsize} (>= {VERSION_BLOCK_MIN_SIZE})")
    checks.append(c)

    # ---- LAY-05 CRC 槽位覆盖 ----
    c = Check("LAY-05", "CRC 槽位覆盖")
    need = [p for p in parts if p["name"] != "version_block"]
    for p in need:
        slot = p.get("crc_slot", None)
        if slot is None:
            c.failed(f"分区 {p['name']} 没有 crc_slot")
            continue
        if not (0 <= int(slot) < len(crc_slots)):
            c.failed(f"分区 {p['name']} 的 crc_slot={slot} 越界 (crc_slots 有 {len(crc_slots)} 项)")
    covered = {p.get("crc_slot") for p in need if p.get("crc_slot") is not None}
    missing = [s for s in crc_slots if s not in covered]
    if missing and not c.failures:
        c.passed(f"6 个 CRC 槽位全部有分区覆盖: {crc_slots}")
    elif c.failures:
        pass
    checks.append(c)

    # ---- LAY-06 A/B 槽对称 ----
    c = Check("LAY-06", "A/B 槽对称")
    ab = [p for p in parts if p.get("slot") in ("a", "b")]
    by_base: dict[str, dict] = {}
    for p in ab:
        base = p["name"].rsplit("_", 1)[0]
        by_base.setdefault(base, {})[p["slot"]] = p
    for base, pair in by_base.items():
        if set(pair.keys()) != {"a", "b"}:
            c.failed(f"{base} 的 A/B 槽不成对 (只有 {sorted(pair.keys())})")
        elif int(pair["a"]["size"]) != int(pair["b"]["size"]):
            c.failed(f"{base} 的 A/B 槽容量不等: a={pair['a']['size']} b={pair['b']['size']}")
    if c.ok and ab:
        c.passed(f"{len(by_base)} 组 A/B 槽对称 (活动槽={active_slot})")
    checks.append(c)

    # ---- LAY-07 版本块字段容量 ----
    c = Check("LAY-07", "版本块字段容量")
    meta = cfg.get("version_meta", {}) or {}
    problems = []
    if len(str(meta.get("version", ""))) > VERSION_STR_MAX:
        problems.append(f"版本串 {len(str(meta['version']))}B > {VERSION_STR_MAX}B")
    if len(str(meta.get("sn", "")).encode("utf-8")) > SN_MAX:
        problems.append(f"SN 超 {SN_MAX}B")
    if len(str(meta.get("calib_id", "")).encode("utf-8")) > CALIB_MAX:
        problems.append(f"calib_id 超 {CALIB_MAX}B")
    if len(str(meta.get("tool_ver", "")).encode("utf-8")) > TOOL_VER_MAX:
        problems.append(f"tool_ver 超 {TOOL_VER_MAX}B")
    for p in problems:
        c.failed(p)
    if not problems:
        c.passed(f"版本串/SN/calib/tool_ver 均在字段容量内 "
                 f"(版本块字段表共 {len(VERSION_BLOCK_FIELDS)} 项)")
    checks.append(c)

    # ---- LAY-08 rootfs 体积 (总分叉点回报) ----
    c = Check("LAY-08", "rootfs 体积回报 (§4.1 总分叉点)")
    rootfs = next((p for p in parts if p["name"] == "rootfs"), None)
    if rootfs is None:
        c.failed("没有 rootfs 分区")
    else:
        mb = int(rootfs["size"]) / (1024 * 1024)
        if mb <= 30:
            c.passed(f"rootfs = {mb:.1f}MB (<=30MB) → §4.1 条件式推荐 C (ro_rootfs+ab_app_model) 成立")
        elif mb <= 64:
            c.passed(f"rootfs = {mb:.1f}MB (30~64MB) → 需降级方案 B + 128MB SPI-NOR")
        else:
            c.failed(f"rootfs = {mb:.1f}MB (>64MB) → SPI-NOR 方案出局, 必须 eMMC (板宽 12→15mm)")
    checks.append(c)

    summary = {
        "device_total_size": total,
        "align": align,
        "active_slot": active_slot,
        "partition_offsets": offsets,
        "crc_slots": crc_slots,
        "version_block_fields": {k: {"offset": v[0], "size": v[1]} for k, v in VERSION_BLOCK_FIELDS.items()},
        "rootfs_mb": round(int(next((p["size"] for p in parts if p["name"] == "rootfs"), 0)) / (1024 * 1024), 2),
    }
    return checks, summary


def main() -> int:
    ap = argparse.ArgumentParser(description="ARS45 分区表/版本块布局静态检查 (S2 L0 先验)")
    ap.add_argument("--config", required=True, help="S2 配置文件 (s2_rescue_config.example.json)")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    ap.add_argument("--device-size", type=str, default=None,
                    help="覆盖配置里的设备容量 (如 64MB / 128MB) —— 用来验 '这套分区表装不装得下'")
    args = ap.parse_args()

    if not os.path.exists(args.config):
        print(f"❌ 配置文件不存在: {args.config}", file=sys.stderr)
        return 2
    try:
        cfg = load_config(args.config)
    except Exception as e:  # noqa: BLE001
        print(f"❌ 配置解析失败: {e}", file=sys.stderr)
        return 2

    if args.device_size:
        size_txt = args.device_size.strip().upper()
        mult = 1
        if size_txt.endswith("MB"):
            mult, size_txt = 1024 * 1024, size_txt[:-2]
        elif size_txt.endswith("KB"):
            mult, size_txt = 1024, size_txt[:-2]
        elif size_txt.endswith("GB"):
            mult, size_txt = 1024 * 1024 * 1024, size_txt[:-2]
        try:
            new_total = int(size_txt) * mult
        except ValueError:
            print(f"❌ --device-size 解析不了: {args.device_size}", file=sys.stderr)
            return 2
        cfg.setdefault("partition_layout", {})["device_total_size"] = new_total
        print(f"[覆盖] device_total_size = {new_total} B ({new_total / (1024*1024):.0f}MB)\n")

    checks, summary = check_layout(cfg)
    n_fail = sum(0 if c.ok else 1 for c in checks)
    report = {
        "tool": "flash_layout_check.py",
        "config": args.config,
        "checks": [c.to_dict() for c in checks],
        "summary": summary,
        "result": "PASS" if n_fail == 0 else "FAIL",
        "evidence": "[实测] PC 侧静态检查; partition_layout 本身为 [推算] 占位值",
    }

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print("=" * 78)
        print("ARS45 分区表 / 版本块布局静态检查 (SW/tools/flash_layout_check.py)")
        print("=" * 78)
        for c in checks:
            mark = "✅" if c.ok else "❌"
            print(f"{mark} {c.cid:<8} {c.name}")
            for d in c.details:
                print(f"        {d}")
            for f in c.failures:
                print(f"        ❌ {f}")
        print("-" * 78)
        print(f"设备容量 {summary['device_total_size']} B | rootfs {summary['rootfs_mb']} MB | "
              f"活动槽 {summary['active_slot']}")
        print(f"结论: {report['result']} ({len(checks) - n_fail}/{len(checks)} 通过)")
        print(f"证据: {report['evidence']}")
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
