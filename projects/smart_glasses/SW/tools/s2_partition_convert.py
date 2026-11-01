#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s2_partition_convert.py —— S2 救砖链路 · 分区表「扇区 ↔ 字节」换算 + 一致性守卫 (ISS-123)

================================================================================
它解决什么
--------------------------------------------------------------------------------
ISS-123 指出的 ★**最容易静默错** 的地方:

    ★ 瑞芯微 `parameter.txt` 的分区尺寸单位是**扇区 (512B)**, 而我方
      `partition_layout.partitions[].size` 是**字节** ⇒ 两者**差 512 倍**。
      ★ 而且这个错**不会报错**: 转录出来的表照样"合法", 照样能写进 flash 文件,
      只是写出来的东西完全不是那回事 ⇒ **必须机械拦住**, 不能靠人肉小心。

本工具把这件事做成三段:

    ① 换算器  —— 读模组厂给的 `parameter.txt` (或等价的扇区表), 用**显式的
                  sector_size 参数**换算成字节表。★ 不手工转录 (手工转录就是
                  512 倍错的来源)。

    ② 守卫    —— `check_layout()` 对任何分区表做 6 条机械检查:
                  ① 单位必须是 bytes      ② sector_size 必须显式存在
                  ③ 合计不得超出存储容量  ④ 合计必须等于声明的期望值
                  ⑤ 每个分区必须对齐      ⑥ 扇区来源必须声明已换算
                  ★ 第③④⑤ 三条各自能抓住 **×512** 与 **÷512** 两个方向的错。

    ③ 自测    —— 含**两条 512 倍反例** (反例 A: 把扇区数当字节; 反例 B: 把字节数
                  当扇区数再乘 512) ⇒ 两条都必须**被守卫抓住**, 且**必须报得出来**。

★ 纪律 (ISS-080 / ISS-123 口径):
  - 我方内部单位**恒为字节**。扇区只是"对方的表里的单位", 换算完就丢掉。
  - `sector_size` 是**显式参数**, 不写死 512 —— 因为瑞芯微的 `parameter.txt`
    有**两种方言** (见 `parse_parameter_txt`), 方言不同单位就不同。
  - 守卫报出问题 ⇒ **拒绝写入 / 拒绝判过**, 不许"看着差不多就放行"。

用法
--------------------------------------------------------------------------------
    # ① 解析模组厂的 parameter.txt → 字节表 (可直接粘进 s2_rescue_config)
    python3 SW/tools/s2_partition_convert.py --parse vendor_parameter.txt \
        --sector-size 512 --out /tmp/partitions.json

    # ② 查配置里的分区表有没有毛病 (rc=0 无问题 / rc=1 有问题)
    python3 SW/tools/s2_partition_convert.py --check SW/tools/s2_rescue_config.json

    # ③ 离线自测 (含 512 倍反例; 期望 rc=0)
    python3 SW/tools/s2_partition_convert.py --selftest

退出码
--------------------------------------------------------------------------------
    0 = 没问题 (或自测全过)
    1 = 守卫发现问题 (单位/容量/对齐/换算没做)
    2 = 参数或环境错误
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

# ------------------------------------------------------------------ 常量

#: 瑞芯微 `parameter.txt` 的 CMDLINE 里 mtdparts 的两种方言 (★ 决定单位)
#:   hex-sector  : 0x00002000@0x00004000(uboot)   → 数值单位 = 扇区
#:   suffix-bin  : 8M@9M(boot)                    → 数值单位 = 字节 (M=MiB)
#: ★ 官方依据 (2026-11-01 独立查证):
#:   九鼎 Rockchip 官方文档英译 "The unit of all values is sector, and one sector is 512 bytes."
#:   armsom "All values use sectors of 512Bytes."
#:   Vicharak Rockchip Parameter File (RK3399 parameter.txt 实例)
#: ⇒ 默认 sector_size=512 只在 **hex-sector 方言**下成立 ⇒ 必须显式声明。
DEFAULT_SECTOR_SIZE = 512

#: 瑞芯微分区表的对齐要求: "every partition start must be aligned to 32KB
#: (64 sectors), and its size must be a multiple of 32KB" (armsom 引 Rockchip 官方)
VENDOR_MIN_ALIGN = 32768

#: 我方内部单位 —— 恒为字节 (换算完就只剩这个)
CANONICAL_UNIT = "bytes"

_HEX_SIZE = re.compile(r"^0[xX]([0-9a-fA-F]+)$")
_SUFFIX_SIZE = re.compile(r"^(\d+)\s*([KMGTkmgt])?$")
_MTD_ITEM = re.compile(r"^(?P<size>[^@]+)@(?P<offset>[^@]+)\((?P<name>[^)]*)\)$")


class ConvertError(Exception):
    """换算/解析失败 (⇒ rc=2)。"""


# ------------------------------------------------------------------ 基础换算

def sectors_to_bytes(sectors: int, sector_size: int = DEFAULT_SECTOR_SIZE) -> int:
    """扇区 → 字节。★ sector_size 是显式参数, 不写死。"""
    if int(sector_size) <= 0:
        raise ConvertError(f"sector_size 非法: {sector_size!r} (必须 > 0)")
    return int(sectors) * int(sector_size)


def suffix_to_bytes(value: str) -> int:
    """`8M` / `512K` / `1G` → 字节 (后缀方言)。"""
    m = _SUFFIX_SIZE.match(str(value).strip())
    if not m:
        raise ConvertError(f"看不懂的尺寸写法: {value!r}")
    mult = {"": 1, "K": 1024, "M": 1024 ** 2, "G": 1024 ** 3, "T": 1024 ** 4}
    return int(m.group(1)) * mult[(m.group(2) or "").upper()]


# ------------------------------------------------------------------ 解析 parameter.txt

def parse_parameter_txt(path: str, sector_size: int = DEFAULT_SECTOR_SIZE) -> dict:
    """
    解析瑞芯微 `parameter.txt`, 返回分区表 (字节) + 方言判定 + 来源信息。

    返回:
        {
          "source_file": ..., "dialect": "hex-sector" | "suffix-bin" | "unknown",
          "sector_size": <本次用的显式参数>,
          "sector_size_applies": True/False,   # ★ 后缀方言时 sector_size 不参与
          "device_hint": "mmcblk0" 等,
          "partitions": [{"name","size_bytes","offset_bytes","size_raw","offset_raw"}],
          "total_bytes": int,
          "warnings": [str, ...],
          "evidence": "[官方·瑞芯微分区文档] ...",
        }
    """
    if not os.path.exists(path):
        raise ConvertError(f"文件不存在: {path}")
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()

    cmdline = None
    for line in text.splitlines():
        if "CMDLINE:" in line:
            cmdline = line.split("CMDLINE:", 1)[1].strip()
            break
    if not cmdline:
        raise ConvertError("这个文件里没有 CMDLINE: 行 —— 不是瑞芯微 parameter.txt 格式")

    if "mtdparts=" not in cmdline:
        raise ConvertError(f"CMDLINE 里没有 mtdparts= 分区描述: {cmdline[:120]!r}")

    spec = cmdline.split("mtdparts=", 1)[1].strip()
    device_hint = ""
    if ":" in spec:
        device_hint, spec = spec.split(":", 1)
    items = [s for s in spec.split(",") if s.strip()]
    if not items:
        raise ConvertError("mtdparts 后面是空的")

    parts: list[dict] = []
    dialects: set[str] = set()
    warnings: list[str] = []
    for raw in items:
        raw = raw.strip()
        m = _MTD_ITEM.match(raw)
        if not m:
            warnings.append(f"看不懂的分区项, 已跳过: {raw!r}")
            continue
        size_raw, off_raw, name = m.group("size"), m.group("offset"), m.group("name")
        if _HEX_SIZE.match(size_raw) and _HEX_SIZE.match(off_raw):
            dialects.add("hex-sector")
            size_sectors = int(_HEX_SIZE.match(size_raw).group(1), 16)
            off_sectors = int(_HEX_SIZE.match(off_raw).group(1), 16)
            size_bytes = sectors_to_bytes(size_sectors, sector_size)
            off_bytes = sectors_to_bytes(off_sectors, sector_size)
        else:
            dialects.add("suffix-bin")
            size_bytes = suffix_to_bytes(size_raw)
            off_bytes = suffix_to_bytes(off_raw)
        parts.append({
            "name": name.strip(),
            "size_bytes": size_bytes,
            "offset_bytes": off_bytes,
            "size_raw": size_raw,
            "offset_raw": off_raw,
        })

    if not parts:
        raise ConvertError("一个分区项都没解析出来")

    if len(dialects) > 1:
        raise ConvertError(f"★ 同一个文件里混了两种方言 {sorted(dialects)} —— 单位不明, 拒绝换算")
    dialect = dialects.pop()

    if dialect == "suffix-bin":
        warnings.append(
            "★ 该文件用的是**后缀方言** (8M@9M) ⇒ 数值单位是**字节** (M=MiB), "
            f"sector_size={sector_size} 在本文件里**不参与换算** —— "
            "★ 别拿 512 去乘, 那是 ×512 的反向坑")
    else:
        warnings.append(
            f"★ 该文件用的是**十六进制扇区方言** ⇒ 数值单位 = 扇区, 已按显式参数 "
            f"sector_size={sector_size} 换算成字节")

    return {
        "source_file": os.path.basename(path),
        "dialect": dialect,
        "sector_size": sector_size,
        "sector_size_applies": dialect == "hex-sector",
        "device_hint": device_hint,
        "partitions": parts,
        "total_bytes": sum(p["size_bytes"] for p in parts),
        "warnings": warnings,
        "evidence": ("[官方·瑞芯微分区文档] 九鼎 Rockchip 官方文档英译 / armsom / Vicharak "
                     "三处独立一致: mtdparts 十六进制写法的单位 = 扇区, 1 扇区 = 512 字节"),
    }


# ------------------------------------------------------------------ 守卫

def check_layout(layout: dict) -> list[dict]:
    """
    分区表一致性守卫。返回问题清单 (空 = 没问题)。

    ★ 每条: {"code", "level", "msg"}
      level = "error" ⇒ 写入/判定必须拒绝
            "warn"  ⇒ 提示, 不拦
    """
    problems: list[dict] = []

    def err(code, msg):
        problems.append({"code": code, "level": "error", "msg": msg})

    def warn(code, msg):
        problems.append({"code": code, "level": "warn", "msg": msg})

    if not isinstance(layout, dict) or not layout:
        err("LAYOUT_EMPTY", "partition_layout 为空")
        return problems

    # ① 单位必须是我方内部单位 (字节)
    unit = str(layout.get("size_unit", CANONICAL_UNIT)).strip().lower()
    if unit != CANONICAL_UNIT:
        err("UNIT_NOT_BYTES",
            f"size_unit={unit!r} —— 我方内部单位恒为 {CANONICAL_UNIT!r}; "
            "扇区表必须先换算 (用 s2_partition_convert.py --parse)")

    # ② sector_size 必须显式存在 (不许代码写死默认值)
    ss = layout.get("sector_size")
    if ss in (None, "", 0):
        err("SECTOR_SIZE_MISSING",
            "partition_layout.sector_size 缺失 —— 扇区↔字节的换算参数必须显式写出来, "
            "不许靠默认值蒙对")
    else:
        try:
            if int(ss) <= 0:
                err("SECTOR_SIZE_BAD", f"sector_size={ss!r} 非法 (必须 > 0)")
        except (TypeError, ValueError):
            err("SECTOR_SIZE_BAD", f"sector_size={ss!r} 不是整数")

    parts = layout.get("partitions") or []
    if not parts:
        err("NO_PARTITIONS", "分区表里一个分区都没有")
        return problems

    total = 0
    for p in parts:
        try:
            total += int(p.get("size", 0))
        except (TypeError, ValueError):
            err("SIZE_NOT_INT", f"分区 {p.get('name')!r} 的 size 不是整数: {p.get('size')!r}")

    dev = int(layout.get("device_total_size", 0) or 0)

    # ③ 合计不得超出存储容量 (★ 抓住 ×512 方向: 字节被当扇区再乘 512)
    if dev and total > dev:
        err("TOTAL_EXCEEDS_DEVICE",
            f"分区表合计 {total} B > 存储容量 {dev} B (超出 {total / dev:.4g}×) —— "
            "★ 典型症状: 把**字节数**当成了**扇区数**再乘 sector_size (×512 的错)")

    # ④ 合计必须等于声明的期望值 (★ 抓住 ÷512 方向: 扇区数被当字节直接填)
    exp = layout.get("expected_total_bytes")
    if exp not in (None, ""):
        try:
            exp_i = int(exp)
        except (TypeError, ValueError):
            exp_i = None
        if exp_i is not None and total != exp_i:
            err("TOTAL_MISMATCH_EXPECTED",
                f"分区表合计 {total} B ≠ 声明的期望合计 {exp_i} B (差 {total / exp_i:.6g}×) —— "
                "★ 典型症状: 把**扇区数**当成了**字节数**直接填 (÷512 的错); "
                "或分区项漏抄/多抄")

    # ⑤ 对齐 (★ 抓住 ÷512 方向: 2048 扇区当字节 = 2048 B, 不是 4096 的倍数)
    align = int(layout.get("align", 0) or 0)
    if align:
        for p in parts:
            try:
                sz = int(p.get("size", 0))
            except (TypeError, ValueError):
                continue
            if sz % align:
                err("ALIGN_VIOLATION",
                    f"分区 {p.get('name')!r} 大小 {sz} B 不是对齐 {align} B 的整数倍 "
                    f"(余 {sz % align}) —— ★ 典型症状: 把**扇区数**当成了**字节数**")

    # ⑥ 扇区来源必须声明已换算, 且换算用的 sector_size 与当前一致
    vendor_unit = str(layout.get("vendor_size_unit", "") or "").strip().lower()
    prov = layout.get("provenance") or {}
    if vendor_unit in ("sector", "sectors", "hex-sector", "512b-sector"):
        if not prov.get("converted"):
            err("SECTOR_TABLE_NOT_CONVERTED",
                f"vendor_size_unit={vendor_unit!r} 但 provenance.converted 不为真 —— "
                "扇区表还没换算成字节, 不许直接用")
        else:
            used = prov.get("converted_with_sector_size")
            try:
                used_i = int(used)
            except (TypeError, ValueError):
                used_i = None
            if used_i is not None and ss not in (None, "") and int(ss) != used_i:
                err("SECTOR_SIZE_PROVENANCE_MISMATCH",
                    f"分区表是用 sector_size={used_i} 换算的, 但配置里现在写的是 {ss} —— "
                    "★ 两者必须一致 (换算时用的和记录的不是同一个 ⇒ 表就是错的)")
        tot_conv = prov.get("converted_total_bytes")
        if tot_conv not in (None, ""):
            try:
                if int(tot_conv) != total:
                    err("PROVENANCE_TOTAL_MISMATCH",
                        f"provenance.converted_total_bytes={tot_conv} ≠ 实际合计 {total} —— "
                        "分区表在换算之后被改过 (或抄漏了)")
            except (TypeError, ValueError):
                pass

    # ⑦ 软提示: 合计远小于容量 (expected_total_bytes 没填时的兜底)
    if dev and total and exp in (None, "") and total * 16 < dev:
        warn("TOTAL_RATIO_SUSPICIOUS",
             f"分区表合计只有存储容量的 {total / dev:.4%} —— 若 expected_total_bytes "
             "未声明, 请人工确认这不是单位错 (÷512 会长这样)")

    return problems


def layout_has_error(problems: list[dict]) -> bool:
    return any(p.get("level") == "error" for p in problems)


# ------------------------------------------------------------------ 自测

def _ref_table() -> list[dict]:
    """[推算] 占位表 (与 SW/tools/s2_rescue_config.json 一致), 单位 = 字节。"""
    return [
        {"name": "bootloader", "size": 1048576, "file": "bootloader.bin", "crc_slot": 0, "slot": None},
        {"name": "kernel", "size": 8388608, "file": "kernel.bin", "crc_slot": 1, "slot": None},
        {"name": "rootfs", "size": 31457280, "file": "rootfs.squashfs", "crc_slot": 2, "slot": None},
        {"name": "app_a", "size": 8388608, "file": "app_a.bin", "crc_slot": 3, "slot": "a"},
        {"name": "app_b", "size": 8388608, "file": "app_b.bin", "crc_slot": 3, "slot": "b"},
        {"name": "model_a", "size": 15728640, "file": "model_a.bin", "crc_slot": 4, "slot": "a"},
        {"name": "model_b", "size": 15728640, "file": "model_b.bin", "crc_slot": 4, "slot": "b"},
        {"name": "isp", "size": 1048576, "file": "isp.bin", "crc_slot": 5, "slot": None},
        {"name": "version_block", "size": 32768, "file": None, "crc_slot": None, "slot": None},
    ]


REF_TOTAL_BYTES = 90210304          # 上面那张表的字节合计
REF_TOTAL_SECTORS = REF_TOTAL_BYTES // 512   # 176192


def _to_sector_table() -> list[dict]:
    """把 [推算] 字节表换写成"模组厂会给的扇区表" (即正确换算的输入)。"""
    out = []
    for p in _ref_table():
        out.append({"name": p["name"], "size_sectors": p["size"] // 512, "file": p.get("file")})
    return out


def selftest() -> int:
    """离线自测。★ 核心是两条 512 倍反例。"""
    cases: list[tuple[str, bool, str]] = []

    def case(name, ok, detail=""):
        cases.append((name, bool(ok), detail))

    # ---------- 准备: 扇区表 (模组厂给的东西) 与正确换算结果 ----------
    sector_tbl = _to_sector_table()
    sector_sum = sum(e["size_sectors"] for e in sector_tbl)

    # T1 正确换算: 扇区 → 字节 (sector_size=512) ⇒ 合计等于已知 [推算] 表合计
    conv = [dict(e, size=e["size_sectors"] * 512) for e in sector_tbl]
    total = sum(e["size"] for e in conv)
    case("T1 正确换算 (sector_size=512) → 字节合计 == %d" % REF_TOTAL_BYTES,
         total == REF_TOTAL_BYTES,
         f"实得 {total}, 期望 {REF_TOTAL_BYTES}, 扇区合计 {sector_sum}")

    # T2 守卫对正确换算后的表: 无 error
    lay_ok = {
        "device_total_size": 134217728, "align": 4096,
        "sector_size": 512, "size_unit": "bytes",
        "expected_total_bytes": REF_TOTAL_BYTES,
        "vendor_size_unit": "sector",
        "provenance": {"converted": True, "converted_with_sector_size": 512,
                       "converted_total_bytes": REF_TOTAL_BYTES},
        "partitions": conv,
    }
    probs_ok = check_layout(lay_ok)
    case("T2 守卫对正确换算后的表 → 0 个 error",
         not layout_has_error(probs_ok),
         "; ".join(p["msg"] for p in probs_ok) or "无问题")

    # ---------- ★ 反例 A: 把扇区数当字节直接填 (÷512) ----------
    bad_a = [dict(e, size=e["size_sectors"]) for e in sector_tbl]   # ★ 没乘 512
    lay_a = dict(lay_ok, partitions=bad_a,
                 provenance={"converted": False})
    probs_a = check_layout(lay_a)
    codes_a = {p["code"] for p in probs_a if p["level"] == "error"}
    case("T3 ★反例A (扇区数当字节, ÷512) → 守卫必须报错",
         layout_has_error(probs_a),
         "命中 error: " + ",".join(sorted(codes_a)))
    case("T4 ★反例A 必须被 TOTAL_MISMATCH_EXPECTED 抓住 (差 512 倍)",
         "TOTAL_MISMATCH_EXPECTED" in codes_a,
         "合计 %d vs 期望 %d" % (sum(e['size'] for e in bad_a), REF_TOTAL_BYTES))
    case("T5 ★反例A 必须被 ALIGN_VIOLATION 抓住 (2048 B 不是 4096 的倍数)",
         "ALIGN_VIOLATION" in codes_a,
         "命中: " + ",".join(sorted(codes_a)))
    case("T6 ★反例A 必须被 SECTOR_TABLE_NOT_CONVERTED 抓住 (没换算就说换算了)",
         "SECTOR_TABLE_NOT_CONVERTED" in codes_a,
         "命中: " + ",".join(sorted(codes_a)))

    # ---------- ★ 反例 B: 把字节数当扇区数再乘 512 (×512) ----------
    bad_b = [dict(e, size=e["size_sectors"] * 512 * 512) for e in sector_tbl]  # ★ 多乘了一次
    lay_b = dict(lay_ok, partitions=bad_b,
                 provenance={"converted": True, "converted_with_sector_size": 512,
                             "converted_total_bytes": sum(e["size"] for e in bad_b)})
    probs_b = check_layout(lay_b)
    codes_b = {p["code"] for p in probs_b if p["level"] == "error"}
    case("T7 ★反例B (字节数当扇区数再乘 512, ×512) → 守卫必须报错",
         layout_has_error(probs_b),
         "命中 error: " + ",".join(sorted(codes_b)))
    case("T8 ★反例B 必须被 TOTAL_EXCEEDS_DEVICE 抓住 (合计爆容量)",
         "TOTAL_EXCEEDS_DEVICE" in codes_b,
         "合计 %d vs 容量 %d" % (sum(e['size'] for e in bad_b), 134217728))

    # ---------- T9: sector_size 缺省 ⇒ 必须报错 (不许靠默认值蒙对) ----------
    lay_noss = dict(lay_ok)
    lay_noss.pop("sector_size")
    codes_noss = {p["code"] for p in check_layout(lay_noss) if p["level"] == "error"}
    case("T9 sector_size 缺失 → 守卫报错 (SECTOR_SIZE_MISSING)",
         "SECTOR_SIZE_MISSING" in codes_noss,
         "命中: " + ",".join(sorted(codes_noss)))

    # ---------- T10: 换算参数与 provenance 不一致 ⇒ 报错 ----------
    lay_mix = dict(lay_ok, sector_size=4096)
    codes_mix = {p["code"] for p in check_layout(lay_mix) if p["level"] == "error"}
    case("T10 换算用的 sector_size 与配置里写的不一致 → 报错",
         "SECTOR_SIZE_PROVENANCE_MISMATCH" in codes_mix,
         "命中: " + ",".join(sorted(codes_mix)))

    # ---------- T11: parameter.txt 解析 (十六进制扇区方言) ----------
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        pf = os.path.join(td, "parameter.txt")
        with open(pf, "w", encoding="utf-8") as f:
            f.write("FIRMWARE_VER: 1.0 MACHINE_MODEL: RK3576 MAGIC: 0x5041524B\n"
                    "TYPE: GPT\n"
                    "CMDLINE: mtdparts=mmcblk0:0x00002000@0x00004000(uboot),"
                    "0x00020000@0x00006000(boot),0x00030000@0x00026000(rootfs)\n")
        try:
            parsed = parse_parameter_txt(pf, 512)
            ok = (parsed["dialect"] == "hex-sector"
                  and parsed["partitions"][0]["size_bytes"] == 0x2000 * 512
                  and parsed["total_bytes"] == (0x2000 + 0x20000 + 0x30000) * 512)
            detail = (f"dialect={parsed['dialect']} total={parsed['total_bytes']} "
                      f"(期望 {(0x2000 + 0x20000 + 0x30000) * 512})")
        except ConvertError as e:
            ok, detail = False, f"解析抛错: {e}"
        case("T11 解析十六进制扇区方言 parameter.txt → 换算正确", ok, detail)

    # ---------- T12: parameter.txt 解析 (后缀方言) ⇒ sector_size 不参与 ----------
    with tempfile.TemporaryDirectory() as td:
        pf = os.path.join(td, "parameter2.txt")
        with open(pf, "w", encoding="utf-8") as f:
            f.write("CMDLINE: mtdparts=mmcblk0:0@1M(uboot),8M@9M(boot)\n")
        try:
            parsed = parse_parameter_txt(pf, 512)
            ok = (parsed["dialect"] == "suffix-bin"
                  and parsed["sector_size_applies"] is False
                  and parsed["partitions"][1]["size_bytes"] == 8 * 1024 * 1024)
            detail = (f"dialect={parsed['dialect']} sector_size_applies="
                      f"{parsed['sector_size_applies']} boot={parsed['partitions'][1]['size_bytes']}")
        except ConvertError as e:
            ok, detail = False, f"解析抛错: {e}"
        case("T12 解析后缀方言 parameter.txt → 认得 8M=8MiB, 且不拿 512 去乘",
             ok, detail)

    # ---------- T13: 混用两种方言 ⇒ 拒绝换算 (单位不明) ----------
    with tempfile.TemporaryDirectory() as td:
        pf = os.path.join(td, "parameter3.txt")
        with open(pf, "w", encoding="utf-8") as f:
            f.write("CMDLINE: mtdparts=mmcblk0:0x00002000@0x00004000(uboot),8M@9M(boot)\n")
        try:
            parse_parameter_txt(pf, 512)
            ok, detail = False, "没抛错 —— 混用方言本该拒绝"
        except ConvertError as e:
            ok, detail = True, f"按预期拒绝: {e}"
        case("T13 同一文件混用两种方言 → 拒绝换算 (单位不明)", ok, detail)

    # ---------- T14: 本仓库真配置 → 0 个 error ----------
    cfg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "s2_rescue_config.json")
    try:
        with open(cfg_path, "r", encoding="utf-8") as f:
            real = json.load(f)
        probs_real = check_layout(real.get("partition_layout") or {})
        case("T14 本仓库 s2_rescue_config.json 的分区表 → 0 个 error",
             not layout_has_error(probs_real),
             "; ".join(p["msg"] for p in probs_real) or "无问题")
    except Exception as e:  # noqa: BLE001
        case("T14 本仓库 s2_rescue_config.json 的分区表 → 0 个 error", False, f"读取失败: {e}")

    # ---------- 打印 ----------
    print("=" * 78)
    print("s2_partition_convert 自测 (纯逻辑, 无需硬件) —— ★ 含 512 倍反例")
    print("=" * 78)
    n_fail = 0
    for name, ok, detail in cases:
        print(f"{'✅' if ok else '❌'} {name}")
        if detail:
            print(f"      {detail}")
        if not ok:
            n_fail += 1
    print("-" * 78)
    print(f"结论: {'PASS' if n_fail == 0 else 'FAIL'} ({len(cases) - n_fail}/{len(cases)} 通过)")
    print("证据: [实测] PC 侧合成自测 (换算与守卫逻辑), 不代表板端 S2 已通")
    print("★ 512 倍差 = 扇区↔字节单位错; 本单把它做成**守卫**而不是靠人肉小心。")
    print("=" * 78)
    return 0 if n_fail == 0 else 3


# ------------------------------------------------------------------ CLI

def main() -> int:
    ap = argparse.ArgumentParser(
        description="S2 分区表 扇区↔字节 换算 + 一致性守卫 (ISS-123)")
    ap.add_argument("--parse", metavar="PARAMETER_TXT", default=None,
                    help="解析瑞芯微 parameter.txt → 字节分区表")
    ap.add_argument("--sector-size", type=int, default=DEFAULT_SECTOR_SIZE,
                    help="★ 显式的扇区大小 (字节)。默认 512, 仅适用于十六进制扇区方言")
    ap.add_argument("--check", metavar="CONFIG_JSON", default=None,
                    help="对配置文件里的 partition_layout 做一致性守卫")
    ap.add_argument("--out", default=None, help="输出 JSON 路径")
    ap.add_argument("--selftest", action="store_true", help="离线自测 (含 512 倍反例)")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    if args.parse:
        try:
            res = parse_parameter_txt(args.parse, args.sector_size)
        except ConvertError as e:
            print(f"❌ 解析失败: {e}", file=sys.stderr)
            return 2
        text = json.dumps(res, ensure_ascii=False, indent=2)
        if args.out:
            with open(args.out, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"✅ 已落盘: {args.out}")
        else:
            print(text)
        for w in res.get("warnings") or []:
            print(f"⚠️  {w}")
        return 0

    if args.check:
        if not os.path.exists(args.check):
            print(f"❌ 配置不存在: {args.check}", file=sys.stderr)
            return 2
        with open(args.check, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        probs = check_layout(cfg.get("partition_layout") or {})
        if not probs:
            print("✅ 分区表一致性守卫: 无问题")
            return 0
        print("=" * 78)
        print("分区表一致性守卫")
        print("=" * 78)
        for p in probs:
            mark = "❌" if p.get("level") == "error" else "⚠️ "
            print(f"{mark} [{p.get('code')}] {p.get('msg')}")
        n_err = sum(1 for p in probs if p.get("level") == "error")
        print("-" * 78)
        print(f"结论: {n_err} 个 error, {len(probs) - n_err} 个 warn")
        return 1 if n_err else 0

    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
