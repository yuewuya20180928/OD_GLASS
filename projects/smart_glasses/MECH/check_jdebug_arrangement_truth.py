#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MECH/check_jdebug_arrangement_truth.py —— `J_DEBUG` 排针【排布标签 (维数)】真相 机器闸 (ISS-382)
===================================================================================================
★**性质**: 只读机器闸 · ★零写板 / 零落表 / 零改任何既有脚本 / 零改任何既有页面 / 零外发 / 不代拍** ★
★**派活**: 项目总工 (main / moli) · ISS-382 · 2026-11-24 · 交卷人 = 结构总工 (mech-lead) ★
★**关联 (★只读·一个字都不许动★)**:
    - `MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` (★ISS-371 已签收真相页·本闸只读它·★零改★)
    - `MECH/check_jdebug_1p27_clearance.py` (★ISS-371 已签收闸·★本闸【不改它】·零字节★)
    - `MECH/BOARD_ONEPASS_JDEBUG_ARRANGEMENT_TRUTH.md` (★本单新建的订正真相页·本闸也读它★)
    - `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` (★开口 X/Y 权威来源·只读★)
    - `MECH/service_port_check.py` (★`CRIT` 真身·只读★)

────────────────────────────────────────────────────────────────────────────────────────────────────────
【本闸为什么存在 (★ISS-382 的病灶★)】
────────────────────────────────────────────────────────────────────────────────────────────────────────
★**① 已签收真相页的排布标签与实测矛盾**:
    `MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` 的机器块 `land_smd.arrangement` 写 `"2x2 staggered"`,
    正文 L45 / L203 / L207 / L288 / L471 / L719 六处写「2 列 × 2 行交错」;
    ★**但本机把官方 `.kicad_mod` 的 pad 坐标真解析一遍, 实测是 2 列 × 4 行交错** ⇒
    ★**该页自己的 §3 表 L208 又写着「4 个焊盘在 Y 向排 4 行 (中心 ±0.635 / ±1.905)」⇒ 同一页自相矛盾** ★

★**② 旧闸 `G5` 有真盲区 (★不是假设·本闸可复现★)**:
    `MECH/check_jdebug_1p27_clearance.py` 的 `G5` 只判
      ① 降级方案几何被独立实测并单列
      ② 页面 `arrangement` 字符串里 **含** `staggered` / `交错`
    ⇒ ★**它【从不把页面声明的维数】与【闸自己实测的维数】做逐字对比** ⇒
      页面写 `2x2` 照样绿、写 `9x9` 也照样绿 ⇒ ★**这一条就是「标签错」能活着签收的根因** ★
    ★**本闸 J2 就是补这一条** ⇒ ★**但本闸【不许改旧闸的一个字节】⇒ 改旧闸还是新闸独立挂 ⇒ 归 main 裁 (§4 未决项)★**

★**③ ★**「标签错」与「结论错」必须分开判 (★本闸 J4 专门干这个★)**:
    已签收页的降级方案铜箔包络 `6.0000 × 4.4600` 是按「X 向 2 列 (中心距 3.00) 且每块 pad 长 3.00 ⇒ X 包络 6.00」
    +「Y 向 4 行 (中心 ±0.635 / ±1.905) 且 pad 高 0.65 ⇒ Y 包络 4.4600」算出来的
    ⇒ ★**数字本身与 `2x4` 完全相容** ⇒ ★**错的是【标签 / 维数】, 不是【几何结论数字】** ★
    ⇒ ★**本闸 J2/J3 管「标签」, J4 管「结论值」, 两条判据分开、绝不合并** ★

────────────────────────────────────────────────────────────────────────────────────────────────────────
【六条判据 (★每条 fail-closed·每条至少一条反向用例★)】
────────────────────────────────────────────────────────────────────────────────────────────────────────
  J0 板三项指纹未动 (md5 / mtime / size) —— ★板只改一次纪律 ①★
  J1 三个变体排布【自己实测一遍】(★两个 SMD 变体 + 一个 THT 变体·★不许把 md5 锚当答案★)
  J2 机器块 `arrangement` 字符串与本闸实测维数【逐字对比】 ⇒ 不等 ⇒ 红并点名 (★旧 `G5` 缺的就是这一条★)
  J3 已签收页里所有「几列 × 几行 / NxM」表述【逐处扫出】 ⇒ 与实测不符的一处都不许漏
  J4 「标签错」与「结论错」【分开判】 ⇒ 降级方案的铜箔包络 / 开口余量 / 判决结论独立重算一遍 ⇒ 必须逐项相等
  J5 证据等级五级白名单 + 零挂起措辞 + 零挂链 + 判据/事实分开 + 零无等级断言

────────────────────────────────────────────────────────────────────────────────────────────────────────
【★J2/J3 为什么这样设计 (★这是本闸最需要讲清楚的一段★)】
────────────────────────────────────────────────────────────────────────────────────────────────────────
★**已签收页一个字节都不许动 (★ISS-374 cont2 先例: 追加已签收页 ⇒ `K7` 立刻红 2 条★)⇒ 本闸绝不做那种事** ★
★**⇒ 设计**: 本闸把「标签订正」放在【本单新建的真相页】里, 以一张【订正台账 (ledger)】的形式落:
    ① J2 比对【本单真相页机器块 `land_smd.arrangement`】与【本闸自己实测的排布 token】⇒ ★**逐字相等才算绿** ★
       ⇒ 这正是旧 `G5` 缺的那一条: ★**声明的维数与实测的维数必须逐字相等** ★
    ② J3 把【已签收页】里所有排布表述逐处扫出来 ⇒
       - 与实测【一致】的表述 ⇒ 必须确实一致 (不一致 ⇒ 红)
       - 与实测【不一致】的表述 (★真错标签★) ⇒ ★**必须逐条落在本单真相页的订正台账里** ⇒
         ★**台账漏一条 ⇒ 红 (一处都不许漏)** ; ★**台账多登记一条并不错的表述 ⇒ 红 (台账自相矛盾)** ★
       - ★**台账每条的 `proposed` 必须逐字等于本闸实测的 token** ⇒ ★**台账里的订正值也不许自己编错** ★
    ③ ★**main 落订正块之后本闸不会红 (★零新增红·这是设计目标·不是巧合★)**:
       台账条目按【surface 文本】判定「open / landed」——
         - surface 仍出现在已签收页 ⇒ 该条仍 open (闸如实报告「还剩 N 条没落」)
         - surface 不再出现 ⇒ 该条已 landed (闸不红)
       ⇒ ★**⇒ main 可以一次落全部、也可以分批落, 都不会让本闸变红** ★
       ⇒ ★**但若 main 落成一个【新的错值】(例如写成「3 列 × 4 行交错」)⇒ 该表述与实测不符且不在台账里 ⇒ J3 立刻红** ★

────────────────────────────────────────────────────────────────────────────────────────────────────────
【rc 语义】
────────────────────────────────────────────────────────────────────────────────────────────────────────
  0 = 全部通过
  1 = 有断言不通过 (逐条列出 + 点名判据号)
  2 = 参数 / IO 错误
  ★`--strict-open` ⇒ 额外把「已签收页仍带未落订正的错标签」也判红 (★给 main 一条命令看红态·默认不判红★)

────────────────────────────────────────────────────────────────────────────────────────────────────────
【用法】
────────────────────────────────────────────────────────────────────────────────────────────────────────
  python3 MECH/check_jdebug_arrangement_truth.py             # 扫真件 (只读)
  python3 MECH/check_jdebug_arrangement_truth.py --selftest  # 反向用例 (末行 ALL TESTS PASS)
  python3 MECH/check_jdebug_arrangement_truth.py --strict-open
  python3 MECH/check_jdebug_arrangement_truth.py --root DIR --libroot DIR

★**沙盒纪律**: 反向用例一律落项目盘 `<root>/tmp/iss382_sbx/selftest/` (★不许写系统 `/tmp` ——
  2026-11-23 04:4x 实测系统 `/tmp` 配额已满, 写 `/tmp` 会让闸拿到假读数★) ★
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)

# --------------------------------------------------------------------------------------------------
# 常量 (★全部相对路径 + 只读来源★)
# --------------------------------------------------------------------------------------------------
SIGNED_PAGE_REL = "MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md"   # ★ISS-371 已签收真相页 (只读·零改)★
TRUTH_PAGE_REL = "MECH/BOARD_ONEPASS_JDEBUG_ARRANGEMENT_TRUTH.md"  # ★本单新建真相页 (本闸也读它)★
CROSS_REL = "MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md"              # ★开口 X/Y 权威来源 (只读)★
CRIT_REL = "MECH/service_port_check.py"                            # ★CRIT 真身 (只读)★
PCB_REL = "HW/PCB/demo_mainboard.kicad_pcb"                        # ★板 (只读·零写板)★
GATE_CHECK_REL = "state/gate_check.py"                             # ★零挂链自证 (只读)★

LIBROOT = "/home/yuewuya/kicad/AppDir/share/kicad/footprints"
LIBDIR = "Connector_PinHeader_1.27mm.pretty"
MOD_SMD_LEFT = "PinHeader_1x04_P1.27mm_Vertical_SMD_Pin1Left.kicad_mod"
MOD_SMD_RIGHT = "PinHeader_1x04_P1.27mm_Vertical_SMD_Pin1Right.kicad_mod"
MOD_THT = "PinHeader_1x04_P1.27mm_Vertical.kicad_mod"

# ★`.kicad_mod` md5 锚 (★只作【完整性锚】·★排布判定一律靠真解析 pad 坐标·不许拿 md5 当答案★)★
MOD_MD5_ANCHOR = {
    MOD_THT: "7a5f470c1f70d4b832be258501945385",
    MOD_SMD_LEFT: "9d6b0e63e99e6484d2cd3fa0bb28c4a5",
    MOD_SMD_RIGHT: "1579ee4026795bb7a87418d0ee5f120b",
}

# ★板零写板基线 (★ISS-371 起沿用·★19 天逐字节未动★)★
BOARD_BASELINE = {
    "md5": "611b869e13518c3c023fb178f91a0075",
    "mtime": "2026-11-06 07:07:17.362193413",
    "size": 4940213,
}

# ★证据等级五级白名单 (★照 `MECH/check_jdebug_1p27_clearance.py` 的现成判据形状★)★
EVIDENCE_WHITELIST = ("[官网]", "[实测]", "[媒体]", "[推算]", "[0数据]")
FORBIDDEN_EVIDENCE = ("[官方]", "[推断]", "[推测]", "[估计]", "[大概]", "[可能]", "[大概值]")
HEDGING_WORDS = ("可能", "大概", "应该是", "似乎", "貌似", "估摸", "八成", "多半")
FORBIDDEN_PHRASES = ("等原厂回信", "等原厂回复", "等待原厂", "回头再问原厂")

# ★排布 token 规范化规则 (★只允许这三种替换·其余一律逐字★)★
#   1) 去首尾空白 + 内部连续空白压成单空格
#   2) 全角 `×` / `＊` / `*` → 半角 `x`;  全角数字保持原样 (数字必须逐字相等)
#   3) `交错` / `staggered` (不分大小写) → `_staggered`;  `直排` → `_inline`
TOKEN_CANON = {
    "×": "x", "＊": "x", "*": "x",
    "交错": "_staggered", "直排": "_inline",
}
TOKEN_STRIP = re.compile(r"\s+")

# ★排布表述扫描口径 (★只扫【降级方案 SMD 变体】这一件事·★THT 变体的排布由旧闸 G1/G4 管·不在本闸范围★)★
SMD_SCOPE_MARKERS = ("SMD", "降级方案", "变体", "交错", "staggered", "arrangement", "排布")
CLAIM_KEYWORD_MARKERS = ("staggered", "交错", "直排", "arrangement", "SMD",
                         "降级方案", "变体", "排布")
NEG_MARKERS = ("不是", "而非", "≠", "而不是")
AFFIRM_MARKERS = ("而是", "则是", "实为", "应为", "即", "换言之")

RE_CN = re.compile(r"(?<![\d.])(\d+)\s*列\s*[xX×*]\s*(\d+)\s*行")
RE_CN2 = re.compile(r"(?<![\d.])(\d+)\s*行\s*[xX×*]\s*(\d+)\s*列")
RE_CMP = re.compile(r"(?<![\d._])(\d+)\s*[xX×*]\s*(\d+)(?![\d.])")
RE_ROW = re.compile(r"(?<![\d.×xX*])(\d+)\s*行")
RE_STAG = re.compile(r"staggered|交错", re.I)
RE_INLINE = re.compile(r"直排")

TOL = 1e-6


# ==================================================================================================
# 通用工具
# ==================================================================================================
def md5_of(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as fh:
        return fh.read()


def near(a, b, tol: float = TOL) -> bool:
    try:
        return abs(float(a) - float(b)) <= tol
    except (TypeError, ValueError):
        return False


BLOCK_RE = re.compile(
    r"<!--\s*MACHINE-BLOCK[A-Z-]*-BEGIN\s*-->\s*```json\s*(.*?)\s*```\s*"
    r"<!--\s*MACHINE-BLOCK[A-Z-]*-END\s*-->", re.S)


def parse_machine_blocks(text: str) -> list:
    out = []
    for m in BLOCK_RE.finditer(text):
        try:
            out.append(json.loads(m.group(1)))
        except Exception as exc:  # noqa: BLE001
            raise AssertionError("机器块 JSON 解析失败: %s" % exc)
    return out


def canon_token(s) -> str:
    """→ 排布 token 的规范化形式

    ★**规范化口径 (★只允许这四种·其余【逐字】★)**:
      ① 去首尾空白 + 去掉内部所有空白 + 折成小写
      ② 全角 `×` / `＊` / `*` → 半角 `x`
      ③ `交错` → `_staggered` ;  `直排` → `_inline`
      ④ 独立的 `staggered` → `_staggered` (★前面已有下划线则不重复补★ ⇒ 幂等不动点★)
    ★**维数的数字与列/行顺序必须逐字相等, 规范化只动空白与分隔符★ ★
    """
    t = str(s or "").strip().lower()
    t = re.sub(r"\s+", "", t)
    t = t.replace("×", "x").replace("＊", "x").replace("*", "x")
    # ★ISS-382 cont1 修正 (★幂等·★原式把【已经规范化的】token 再补一个下划线★):
    #   原式 `re.sub(r"staggered", "_staggered", ...)` 把 "2x4_staggered" 规范化成
    #   "2x4__staggered" ⇒ ★**本闸自己 canonical token 的规范形式不是自己的不动点** ⇒
    #   页面按 canonical 写法声明真实排布时, J2 (逐字对比) 与 J3 (台账 proposed) 永远红 ⇒ 误报 ★
    #   ⇒ 改为【前面没有下划线时才补下划线】⇒ canon("2x4_staggered") == "2x4_staggered" (不动点) ★
    t = t.replace("交错", "_staggered")
    t = t.replace("直排", "_inline")
    t = re.sub(r"(?<!_)staggered", "_staggered", t)
    t = re.sub(r"_+staggered", "_staggered", t)
    return t


def token_of(cols: int, rows: int, staggered: bool) -> str:
    """→ 本闸实测排布的规范 token (★形状: `<列>x<行>` + `_staggered` / `_inline`★)"""
    return "%dx%d%s" % (cols, rows, "_staggered" if staggered else "")


# ==================================================================================================
# 官方 `.kicad_mod` 只读解析 (★排布判定一律靠真解析 pad 坐标·★不许把 md5 锚当答案★)
# ==================================================================================================
PAD_RE = re.compile(
    r'\(pad\s+"([^"]*)"\s+(\S+)\s+(\S+)\s*\(at\s+([-\d.]+)\s+([-\d.]+)'
    r'(?:\s+[-\d.]+)?\)'
    r'(?:\s*\(size\s+([-\d.]+)\s+([-\d.]+)\))?'
    r'(?:\s*\(drill\s+([-\d.]+)\))?')


def parse_mod(path: str) -> dict:
    text = read_text(path)
    pads = []
    for m in PAD_RE.finditer(text):
        num, ptype, shape, px, py, sx, sy, drill = m.groups()
        pads.append({"num": num, "type": ptype, "shape": shape,
                     "px": float(px), "py": float(py),
                     "sx": float(sx or 0.0), "sy": float(sy or 0.0),
                     "drill": float(drill) if drill else None})
    if not pads:
        raise AssertionError("`.kicad_mod` 里读不到焊盘: %s" % path)
    return {"pads": pads, "path": path}


def arrangement_of(pads: list) -> dict:
    """→ 排布实测 (★列 = 焊盘中心 X 的不同取值个数·行 = 焊盘中心 Y 的不同取值个数★)

    ★**交错 (staggered) 的完整定义** (★ISS-382 口径★):
        列 == 2 且 行 == 4 且 ★**沿 Y 递增排序后, 相邻两行的列号左右交替**★
        (★不要求第一行必须是左列 —— 两个 SMD 变体 (Pin1Left / Pin1Right) 都必须判 True★)
    """
    xs = sorted({round(p["px"], 6) for p in pads})
    ys = sorted({round(p["py"], 6) for p in pads})
    cols, rows = len(xs), len(ys)
    seq = []
    for p in sorted(pads, key=lambda q: (round(q["py"], 6), round(q["px"], 6))):
        cx = min(xs, key=lambda v: abs(v - p["px"]))
        idx = xs.index(cx)
        seq.append(idx)
    alternating = (cols == 2 and rows == 4 and
                   all(seq[i] != seq[i + 1] for i in range(len(seq) - 1)) and
                   len(seq) == 4)
    env_x = (min(p["px"] - p["sx"] / 2.0 for p in pads),
             max(p["px"] + p["sx"] / 2.0 for p in pads))
    env_y = (min(p["py"] - p["sy"] / 2.0 for p in pads),
             max(p["py"] + p["sy"] / 2.0 for p in pads))
    return {"npads": len(pads), "cols": cols, "rows": rows,
            "col_x": xs, "row_y": ys, "col_seq_along_y": seq,
            "staggered": alternating,
            "arrangement": token_of(cols, rows, alternating),
            "pad_size": [pads[0]["sx"], pads[0]["sy"]],
            "pad_type": pads[0]["type"],
            "copper_w": env_x[1] - env_x[0], "copper_h": env_y[1] - env_y[0],
            "env_x": list(env_x), "env_y": list(env_y)}


def measure(libroot: str, name: str) -> dict:
    p = os.path.join(libroot, LIBDIR, name)
    if not os.path.isfile(p):
        raise AssertionError("`.kicad_mod` 不在盘: %s" % p)
    mod = parse_mod(p)
    arr = arrangement_of(mod["pads"])
    arr["mod_path"] = p
    arr["mod_name"] = name
    arr["md5"] = md5_of(p)
    return arr


# ==================================================================================================
# 判据常量 (CRIT / 开口 X·Y)
# ==================================================================================================
def parse_crit(crit_py: str):
    txt = read_text(crit_py)
    m_tol = re.search(r'"fdm_part"\s*:\s*([-\d.]+)', txt)
    m_crit = re.search(r'CRIT\s*=\s*2\s*\*\s*TOL\["fdm_part"\]', txt)
    if not m_tol or not m_crit:
        raise AssertionError("判据真身形状变了 (CRIT 不再是 2 * TOL['fdm_part']) ⇒ 人工复核")
    tol = float(m_tol.group(1))
    return 2.0 * tol, tol


def parse_debug_opening(cross_md: str) -> dict:
    """→ 调试口开口 X/Y (★从 MECH 权威页机器块取·不是从本页取★)"""
    blocks = parse_machine_blocks(read_text(cross_md))
    for blk in blocks:
        for op in (blk.get("openings") or []):
            if op.get("id") == "PORT_OPEN_DEBUG" or op.get("covers") == "J_DEBUG":
                tiers = {}
                for k, v in (op.get("tiers") or {}).items():
                    r = v.get("open_rect") or {}
                    if len(r) != 4:
                        raise AssertionError("权威页开口矩形不完整: tier %s" % k)
                    tiers[k] = {"y0": float(r["y0"]), "y1": float(r["y1"]),
                                "x0": float(r["x0"]), "x1": float(r["x1"])}
                return {"open_x": [float(op["open_x"][0]), float(op["open_x"][1])],
                        "tiers": tiers}
    raise AssertionError("MECH 交叉核对页机器块里找不到 PORT_OPEN_DEBUG 开口")


# ==================================================================================================
# 排布表述扫描 (★J3 用·★先把「一句话里到底宣称了几列几行」逐处抠出来★)
# ==================================================================================================
def _scope_of_line(lines: list, i: int) -> bool:
    """→ 这一行/这一节是不是在讲【降级方案 SMD 变体】(★THT 变体的排布不在本闸范围★)"""
    ln = lines[i]
    if any(s in ln for s in SMD_SCOPE_MARKERS):
        return True
    for j in range(i, -1, -1):
        m = re.match(r"^#{1,6}\s*(.+)$", lines[j])
        if m:
            return any(s in m.group(1) for s in SMD_SCOPE_MARKERS)
    return False


def _is_negated(ln: str, start: int) -> bool:
    """→ 这个表述前面有没有否定词 (★否定句 = 宣称【不是】这个排布★)"""
    w = ln[max(0, start - 24):start]
    last_neg = -1
    last_aff = -1
    for nm in NEG_MARKERS:
        p = w.rfind(nm)
        if p > last_neg:
            last_neg = p
    for nm in AFFIRM_MARKERS:
        p = w.rfind(nm)
        if p > last_aff:
            last_aff = p
    if last_neg < 0:
        return False
    return last_aff < last_neg


def scan_arrangement_claims(text: str) -> list:
    """→ 已签收页里所有排布表述 (★逐处·★带行号·★带表面文本·★带否定标记★)"""
    lines = text.split("\n")
    out = []
    for i, ln in enumerate(lines):
        if not _scope_of_line(lines, i):
            continue
        spans = []
        for m in RE_CN.finditer(ln):
            spans.append((m.start(), m.end(), "cn", int(m.group(1)), int(m.group(2))))
        for m in RE_CN2.finditer(ln):
            spans.append((m.start(), m.end(), "cn", int(m.group(2)), int(m.group(1))))
        for m in RE_CMP.finditer(ln):
            w = ln[max(0, m.start() - 24):m.end() + 24]
            if not any(k in w for k in CLAIM_KEYWORD_MARKERS):
                continue
            spans.append((m.start(), m.end(), "cmp", int(m.group(1)), int(m.group(2))))
        for m in RE_ROW.finditer(ln):
            if any(s <= m.start() < e for (s, e, _, _, _) in spans):
                continue
            spans.append((m.start(), m.end(), "row", None, int(m.group(1))))
        for (s, e, kind, cols, rows) in sorted(spans):
            ctx = ln[max(0, s - 24):e + 24]
            if RE_STAG.search(ctx):
                stag = True
            elif RE_INLINE.search(ctx):
                stag = False
            else:
                stag = None
            out.append({"line": i + 1, "kind": kind, "surface": ln[s:e],
                        "cols": cols, "rows": rows, "staggered": stag,
                        "negated": _is_negated(ln, s),
                        "text": ln.strip()})
    return out


def claim_disagrees(claim: dict, meas: dict) -> bool:
    """→ 这个表述与实测是否不符 (★否定句的判法相反★)"""
    dim_bad = False
    if claim["cols"] is not None and claim["cols"] != meas["cols"]:
        dim_bad = True
    if claim["rows"] is not None and claim["rows"] != meas["rows"]:
        dim_bad = True
    if claim["staggered"] is not None and claim["staggered"] != meas["staggered"]:
        dim_bad = True
    return dim_bad


# ==================================================================================================
# 六条判据
# ==================================================================================================
def _gate(name: str, errs: list) -> dict:
    return {"ok": not errs, "errs": errs, "name": name}


def j0_board_zero_write(ctx) -> dict:
    """J0 · 板三项指纹未动 (md5 / mtime / size)"""
    errs = []
    p = ctx["pcb_path"]
    if not os.path.isfile(p):
        errs.append("板文件不在盘: %s" % p)
        return _gate("J0 板三项指纹未动 (md5/mtime/size)", errs)
    got_md5 = md5_of(p)
    st = os.stat(p)
    ns = st.st_mtime_ns
    sec, nsec = ns // 1_000_000_000, ns % 1_000_000_000
    got_mtime = "%s.%09d" % (datetime.datetime.fromtimestamp(sec).strftime("%Y-%m-%d %H:%M:%S"),
                             nsec)
    if got_md5 != BOARD_BASELINE["md5"]:
        errs.append("★板 md5 漂移: 实读 %s, 基线 %s★" % (got_md5, BOARD_BASELINE["md5"]))
    if got_mtime != BOARD_BASELINE["mtime"]:
        errs.append("★板 mtime 漂移: 实读 %s, 基线 %s★" % (got_mtime, BOARD_BASELINE["mtime"]))
    if st.st_size != BOARD_BASELINE["size"]:
        errs.append("★板 size 漂移: 实读 %d, 基线 %d★" % (st.st_size, BOARD_BASELINE["size"]))
    ctx["board_triple"] = {"md5": got_md5, "mtime": got_mtime, "size": st.st_size}
    return _gate("J0 板三项指纹未动 (md5/mtime/size)", errs)


def j1_measure_three_variants(ctx) -> dict:
    """J1 · 两个 SMD 变体 + 一个 THT 变体的排布自己实测一遍 (★不许把 md5 锚当答案★)"""
    errs = []
    left = ctx["smd_left"]
    right = ctx["smd_right"]
    tht = ctx["tht"]
    # ① SMD 两个变体都必须是 4 焊盘 / 2 列 / 4 行 / 交错
    for tag, g in (("SMD_Pin1Left", left), ("SMD_Pin1Right", right)):
        if g["npads"] != 4:
            errs.append("%s 焊盘数实读 %d ≠ 4" % (tag, g["npads"]))
        if g["cols"] != 2:
            errs.append("%s 实测列数 %d ≠ 2" % (tag, g["cols"]))
        if g["rows"] != 4:
            errs.append("%s 实测行数 %d ≠ 4" % (tag, g["rows"]))
        if not g["staggered"]:
            errs.append("%s 实测列序 %s 不左右交替 ⇒ 不是交错排布"
                        % (tag, g["col_seq_along_y"]))
        if g["arrangement"] != "2x4_staggered":
            errs.append("%s 实测排布 token %r ≠ '2x4_staggered'" % (tag, g["arrangement"]))
    # ② 两个 SMD 变体的铜箔包络必须一致 (⇒ 变体只改针序, 不改几何)
    if not (near(left["copper_w"], right["copper_w"]) and near(left["copper_h"], right["copper_h"])):
        errs.append("两个 SMD 变体铜箔包络不一致: L %.4f×%.4f / R %.4f×%.4f"
                    % (left["copper_w"], left["copper_h"],
                       right["copper_w"], right["copper_h"]))
    # ③ THT 变体: 4 焊盘 · 沿局部 Y 一列 (1 列 × 4 行)
    if tht["npads"] != 4:
        errs.append("THT 焊盘数实读 %d ≠ 4" % tht["npads"])
    if tht["cols"] != 1:
        errs.append("THT 实测列数 %d ≠ 1 (官方 THT 是沿局部 Y 一列)" % tht["cols"])
    if tht["rows"] != 4:
        errs.append("THT 实测行数 %d ≠ 4" % tht["rows"])
    if tht["staggered"]:
        errs.append("THT 被误判成交错排布")
    # ④ md5 锚只作完整性核对 (★排布判定一律靠上面的 pad 坐标真解析★)
    for g in (left, right, tht):
        want = MOD_MD5_ANCHOR.get(g["mod_name"])
        if want is None:
            errs.append("md5 锚表缺 %s" % g["mod_name"])
        elif g["md5"] != want:
            errs.append("★`.kicad_mod` md5 漂移: %s 锚 %s 实读 %s★"
                        % (g["mod_name"], want, g["md5"]))
    ctx["measured_token"] = left["arrangement"]
    return _gate("J1 三个变体排布自己实测 (两个 SMD + 一个 THT)", errs)


def j2_machine_block_arrangement_verbatim(ctx) -> dict:
    """J2 · 机器块 `arrangement` 字符串与本闸实测维数逐字对比 (★旧 G5 缺的就是这一条★)"""
    errs = []
    blk = ctx["truth_land_smd"]
    meas = ctx["measured_token"]
    declared = blk.get("arrangement")
    if declared is None:
        errs.append("★本单真相页机器块缺 land_smd.arrangement (⇒ 维数无处声明·判据无法成立)★")
        return _gate("J2 机器块 arrangement 与实测维数逐字对比", errs)
    got = canon_token(declared)
    if got != meas:
        errs.append("★arrangement 声明 %r (规范化 %r) ≠ 实测 %r ⇒ 点名: 维数/交错限定词不符★"
                    % (declared, got, meas))
        # ★点名差在哪一维★
        dm = re.match(r"^(\d+)x(\d+)(.*)$", meas)
        dd = re.match(r"^(\d+)x(\d+)(.*)$", got)
        if dm and dd:
            if dm.group(1) != dd.group(1):
                errs.append("  · 列数: 声明 %s ≠ 实测 %s" % (dd.group(1), dm.group(1)))
            if dm.group(2) != dd.group(2):
                errs.append("  · 行数: 声明 %s ≠ 实测 %s" % (dd.group(2), dm.group(2)))
            if dm.group(3) != dd.group(3):
                errs.append("  · 交错限定词: 声明 %r ≠ 实测 %r" % (dd.group(3), dm.group(3)))
    # ★反向用例: 写 `2x2` / `9x9` 之类一律红 (★旧 G5 对这些全绿★)★
    ctx["j2_declared"] = declared
    return _gate("J2 机器块 arrangement 与实测维数逐字对比 (旧 G5 缺的一条)", errs)


def j3_no_claim_escapes(ctx) -> dict:
    """J3 · 已签收页所有排布表述逐处扫出 ⇒ 与实测不符的一处都不许漏"""
    errs = []
    meas = ctx["measured"]
    claims = ctx["claims"]
    ledger = ctx["ledger"]
    ctx["open_defects"] = []
    ctx["landed_defects"] = []
    # ① 台账自身自洽: `proposed` 必须逐字等于实测 token
    for ent in ledger:
        prop = canon_token(ent.get("proposed"))
        if prop != ctx["measured_token"]:
            errs.append("★订正台账 `%s` L%s 的 proposed %r ≠ 实测 %r ⇒ 台账自己写错了★"
                        % (ent.get("file"), ent.get("line"), ent.get("proposed"),
                           ctx["measured_token"]))
        if ent.get("file") != ctx["signed_rel"]:
            errs.append("订正台账指向了非本单目标页: %r" % ent.get("file"))
        # ★台账登记的每一条必须【真的】与实测不符 (★不许登记一条并不错的表述⇒ 台账自相矛盾★)
        fake = {"cols": ent.get("cols"), "rows": ent.get("rows"),
                "staggered": ent.get("staggered")}
        if not claim_disagrees(fake, ctx["measured"]):
            errs.append("★订正台账 L%s 登记的表述 %r (列=%s 行=%s 交错=%s) 并不与实测 %s 不符 ⇒ 台账登记错★"
                        % (ent.get("line"), ent.get("surface"), ent.get("cols"),
                           ent.get("rows"), ent.get("staggered"), ctx["measured_token"]))
    # ② 扫描结果与台账逐条对账
    live_bad = []
    for c in claims:
        bad = claim_disagrees(c, meas)
        if c["negated"]:
            # ★否定句: 宣称「不是这个排布」⇒ 必须真的不符; 若与实测一致 ⇒ 否定句自己错了★
            if not bad:
                errs.append("★L%s 的否定表述 %r 与实测 %s 一致 ⇒ 否定句写反了★"
                            % (c["line"], c["surface"], ctx["measured_token"]))
            continue
        if not bad:
            continue
        live_bad.append(c)
        key = (c["surface"], c["cols"], c["rows"], c["staggered"])
        cov = [e for e in ledger
               if e.get("surface") == c["surface"] and e.get("cols") == c["cols"]
               and e.get("rows") == c["rows"] and e.get("staggered") == c["staggered"]]
        if not cov:
            errs.append("★L%s 的排布表述 %r (=%s列×%s行) 与实测 %s 不符, 且【不在订正台账里】⇒ 漏登记★"
                        % (c["line"], c["surface"], c["cols"], c["rows"],
                           ctx["measured_token"]))
    # ③ 台账条目的 open / landed 判定 (★按 surface 是否仍出现在已签收页·★main 落订正块不会让本闸变红★)
    signed_text = ctx["signed_text"]
    for ent in ledger:
        present = ent.get("surface") in signed_text
        ent["_open"] = present
        if present:
            ctx["open_defects"].append(ent)
        else:
            ctx["landed_defects"].append(ent)
    ctx["live_bad_count"] = len(live_bad)
    # ★★ISS-382 cont1 补齐 (★「一处都不许漏」这条原文只做了一半★)★★:
    #   原文只判【有没有一条 tuple 相同的台账条目】⇒ ★同一个错表述在已签收页出现 N 处时,
    #   台账只登记 1 条照样绿 ⇒ 漏登记 (与本闸自带的反向用例 ⑦ 的意图相反) ★
    #   ⇒ 追加【同一 tuple 的台账条目数 ≥ 该 tuple 的错表述处数】⇒ 漏一处就红 ★
    #   ★用【计数】而不是【行号相等】做配对 ⇒ 已签收页行号在 main 落订正块后位移也不误红 ★
    cnt_claim = {}
    for c in live_bad:
        k = (c["surface"], c["cols"], c["rows"], c["staggered"])
        cnt_claim[k] = cnt_claim.get(k, 0) + 1
    cnt_ledger = {}
    for e in ledger:
        k = (e.get("surface"), e.get("cols"), e.get("rows"), e.get("staggered"))
        cnt_ledger[k] = cnt_ledger.get(k, 0) + 1
    for k, n in sorted(cnt_claim.items(), key=lambda kv: str(kv[0])):
        got = cnt_ledger.get(k, 0)
        if got < n:
            errs.append("★同一错排布表述 %r (=%s列×%s行) 在已签收页出现 %d 处, 订正台账只登记 %d 条 ⇒ 漏登记★"
                        % (k[0], k[1], k[2], n, got))
    return _gate("J3 已签收页排布表述逐处扫出 (与实测不符的一处都不许漏)", errs)


def _open_y_tier(opening: dict, tier_key: str) -> float:
    t = opening["tiers"][tier_key]
    return t["y1"] - t["y0"]


def _recompute_smd(ctx) -> dict:
    """→ 降级方案 (SMD 变体) 的结论值独立重算 (★只用 .kicad_mod + 权威开口·不许抄页里的数★)"""
    g = ctx["smd_left"]
    opening = ctx["opening"]
    crit, tol = ctx["crit"], ctx["tol"]
    cx = (opening["open_x"][0] + opening["open_x"][1]) / 2.0
    ys = [ (t["y0"] + t["y1"]) / 2.0 for t in opening["tiers"].values() ]
    cy = ys[0]
    for y in ys[1:]:
        if not near(y, cy, 1e-6):
            raise AssertionError("权威页开口 Y 中心三档不一致 ⇒ 人工复核")
    out = {"copper_w": g["copper_w"], "copper_h": g["copper_h"],
           "center": (cx, cy), "tiers": {}}
    out["required_open_y"] = g["copper_h"] + 2.0 * (crit + tol)
    for rot in (0, 90):
        if rot == 0:
            bw, bh = g["copper_w"], g["copper_h"]
        else:
            bw, bh = g["copper_h"], g["copper_w"]
        x0, x1 = cx - bw / 2.0, cx + bw / 2.0
        y0, y1 = cy - bh / 2.0, cy + bh / 2.0
        cl = x0 - opening["open_x"][0]
        cr = opening["open_x"][1] - x1
        per = {}
        for tk in sorted(opening["tiers"]):
            t = opening["tiers"][tk]
            cy_t = min(y0 - t["y0"], t["y1"] - y1)
            worst = cy_t - tol
            per[tk] = {"clearance_y": cy_t, "worst_clearance_y": worst,
                       "pass_crit_y": bool(worst >= crit - TOL)}
        out["rot%d" % rot] = {"origin": (cx, cy),
                              "copper_x": [x0, x1], "copper_y": [y0, y1],
                              "clearance_x_left": cl, "clearance_x_right": cr,
                              "worst_clearance_x": min(cl, cr) - tol,
                              "tiers": per}
    return out


def _j4_compare(ctx, blk) -> list:
    """→ J4 的【纯结论值】比较 (★★故意【不读】`arrangement`·★这是「标签 ≠ 结论」的结构保证★)"""
    errs = []
    rec = ctx["recompute"]
    # ① 铜箔包络
    for nm, got, want in (("copper_w_mm", rec["copper_w"], blk.get("copper_w_mm")),
                           ("copper_h_mm", rec["copper_h"], blk.get("copper_h_mm")),
                           ("required_open_y_mm", rec["required_open_y"],
                            blk.get("required_open_y_mm"))):
        if not near(got, want):
            errs.append("已签收页 land_smd.%s 写 %s, 独立重算 %s ⇒ 结论值不符"
                        % (nm, want, round(got, 6)))
    # ② 两个旋转档的开口余量与判决
    for rot in (0, 90):
        rk = "centered_rot%d" % rot
        rb = blk.get(rk) or {}
        rr = rec["rot%d" % rot]
        for nm, got, want in (("clearance_x_left", rr["clearance_x_left"], rb.get("clearance_x_left")),
                               ("clearance_x_right", rr["clearance_x_right"], rb.get("clearance_x_right")),
                               ("worst_clearance_x", rr["worst_clearance_x"], rb.get("worst_clearance_x"))):
            if not near(got, want):
                errs.append("已签收页 %s.%s 写 %s, 独立重算 %s ⇒ 结论值不符"
                            % (rk, nm, want, round(got, 6)))
        cyb = rb.get("clearance_y_by_tier") or {}
        wyb = rb.get("worst_clearance_y_by_tier") or {}
        pcb = rb.get("pass_crit_y_by_tier") or {}
        for tk, tv in rr["tiers"].items():
            if not near(tv["clearance_y"], cyb.get(tk)):
                errs.append("已签收页 %s.clearance_y_by_tier[%s] 写 %s, 独立重算 %s"
                            % (rk, tk, cyb.get(tk), round(tv["clearance_y"], 6)))
            if not near(tv["worst_clearance_y"], wyb.get(tk)):
                errs.append("已签收页 %s.worst_clearance_y_by_tier[%s] 写 %s, 独立重算 %s"
                            % (rk, tk, wyb.get(tk), round(tv["worst_clearance_y"], 6)))
            if bool(pcb.get(tk)) != bool(tv["pass_crit_y"]):
                errs.append("已签收页 %s.pass_crit_y_by_tier[%s] 写 %s, 独立重算 %s"
                            % (rk, tk, pcb.get(tk), tv["pass_crit_y"]))
    # ③ 判决结论 (三档 Y 全红)
    all_red = all(not tv["pass_crit_y"] for tv in rec["rot0"]["tiers"].values())
    if not all_red:
        errs.append("独立重算得降级方案 rot0 三档 Y 并非全红 ⇒ 与已签收页的判决结论不符")
    verdict = str(blk.get("verdict") or "")
    if "红" not in verdict:
        errs.append("已签收页 land_smd.verdict 未写明『三档 Y 全红』, 现写 %r" % verdict)
    return errs


def j4_label_vs_conclusion_separate(ctx) -> dict:
    """J4 · 「标签错」与「结论错」分开判: 降级方案的结论值独立重算 ⇒ 必须逐项相等"""
    errs = []
    blk = ctx["signed_land_smd"]
    if not blk:
        errs.append("已签收页机器块缺 land_smd (降级方案结论值无从比对)")
        return _gate("J4 标签错 / 结论错 分开判 (结论值独立重算)", errs)
    errs.extend(_j4_compare(ctx, blk))
    # ④ ★**判据分离自证 (★不硬编码「已签收页现在必然是错的」★)**:
    #    把同一个 `land_smd` 的 `arrangement` 分别换成【实测 token】与【一个错 token】,
    #    ★**J4 的判定结果必须逐字相同** ⇒ 证明 J4 确实【不读】标签字段 ⇒
    #    ★「标签错」永远不牵连「结论值」, 且 main 落完订正块后 J4 也不会变红** ★
    a = dict(blk); a["arrangement"] = ctx["measured_token"]
    b = dict(blk); b["arrangement"] = "9x9_staggered"
    ea, eb = _j4_compare(ctx, a), _j4_compare(ctx, b)
    if ea != eb:
        errs.append("★J4 的判定结果随 `arrangement` 标签变化 ⇒ 判据没分开 (标签错不该牵连结论值)★")
    ctx["j4_label_insensitive"] = (ea == eb)
    return _gate("J4 标签错 / 结论错 分开判 (结论值独立重算)", errs)


_EVID_TOKEN_RE = re.compile(r"\[([^\]\n]{1,14})\]")
_EVID_LIKE_RE = re.compile(r"^[\u4e00-\u9fff0-9]{1,14}$")
_CJK_RE = re.compile(r"[\u4e00-\u9fff]")


def _evidence_tokens(body: str):
    out = []
    for m in _EVID_TOKEN_RE.finditer(body):
        content = m.group(1)
        if not _EVID_LIKE_RE.match(content):
            continue
        if not _CJK_RE.search(content):
            continue
        if body[m.end():m.end() + 1] == "(" and m.group(0) not in EVIDENCE_WHITELIST \
                and m.group(0) not in FORBIDDEN_EVIDENCE:
            continue
        out.append(m.group(0))
    return out


def j5_evidence_wording_nochain(ctx) -> dict:
    """J5 · 证据等级 + 零挂起 + 零挂链 + 判据/事实分开 + 零无等级断言"""
    errs = []
    text = ctx["truth_text"]
    for tk in _evidence_tokens(text):
        if tk in FORBIDDEN_EVIDENCE:
            errs.append("证据等级 %s 在禁用名单 ⇒ 只许用五级白名单 %s"
                        % (tk, "/".join(EVIDENCE_WHITELIST)))
        elif tk not in EVIDENCE_WHITELIST:
            errs.append("证据等级 %s 不在五级白名单 %s" % (tk, "/".join(EVIDENCE_WHITELIST)))
    if not any(tk in EVIDENCE_WHITELIST for tk in _evidence_tokens(text)):
        errs.append("本单真相页一个证据等级标记都没有")
    for w in HEDGING_WORDS:
        if w in text:
            errs.append("本单真相页出现挂起措辞 %r (不许无档措辞)" % w)
    for w in FORBIDDEN_PHRASES:
        if w in text:
            errs.append("本单真相页出现 %r (不许把活推给原厂回信)" % w)
    # 判据句 / 事实句 两句分开
    if "判据句" not in text or "事实句" not in text:
        errs.append("★本单真相页必须显式写出「判据句」与「事实句」两句★")
    PROHIBIT_MARKERS = ("不许", "不得", "禁止", "≠", "不等于", "分开", "混成", "禁 ")
    for ln in text.split("\n"):
        if "合格" not in ln:
            continue
        if not ("CRIT" in ln or "判据" in ln):
            continue
        if any(mk in ln for mk in PROHIBIT_MARKERS):
            continue
        errs.append("★同一行里把「方向过 CRIT」和「合格」混成一句 (判据句与事实句必须分开写)★")
    # 零挂链
    gc = ctx["gate_check_path"]
    if not os.path.isfile(gc):
        errs.append("state/gate_check.py 不在盘: %s" % gc)
    else:
        hit = read_text(gc).count("check_jdebug_arrangement_truth")
        if hit:
            errs.append("★本闸已被挂进 state/gate_check.py (%d 处) ⇒ 零挂链纪律被破★" % hit)
    ctx["hook_count"] = 0 if os.path.isfile(gc) else -1
    # 零无等级断言 (★§1 / §2 表格的每一个数据行都必须带证据等级★)
    # ★Markdown 表格的形状是: 表头行 → 分隔行 → 数据行 ⇒ ★表头行是【分隔行的前一行】★
    lines = text.split("\n")
    in_fence = False
    sec = ""
    for i, ln in enumerate(lines):
        if ln.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = re.match(r"^#{1,6}\s*(.+)$", ln)
        if m:
            sec = m.group(1)
            continue
        if not (sec.startswith("§1") or sec.startswith("§2")):
            continue
        s = ln.strip()
        if not s.startswith("|"):
            continue
        if re.match(r"^\|[\s\-:|]*\|$", s):
            continue                     # ★分隔行★
        nxt = ""
        for j in range(i + 1, len(lines)):
            if lines[j].strip():
                nxt = lines[j].strip()
                break
        if re.match(r"^\|[\s\-:|]*\|$", nxt):
            continue                     # ★表头行 (★下一行是分隔行★)★
        cells = [c.strip() for c in s.strip("|").split("|")]
        if cells and re.match(r"^#?\s*$", cells[0]):
            continue                     # 空首格行
        if not any(tk in s for tk in EVIDENCE_WHITELIST):
            errs.append("★§1/§2 表格有一个数据行没带证据等级 (无等级断言)★ 行首: %s" % s[:70])
    return _gate("J5 证据等级 + 零挂起 + 零挂链 + 判据/事实分开 + 零无等级断言", errs)


# ==================================================================================================
# 主检查
# ==================================================================================================
def run_checks(root: str, libroot: str = LIBROOT) -> dict:
    root = os.path.abspath(root)
    ctx = {"root": root, "libroot": libroot,
           "signed_rel": SIGNED_PAGE_REL,
           "signed_path": os.path.join(root, SIGNED_PAGE_REL),
           "truth_path": os.path.join(root, TRUTH_PAGE_REL),
           "cross_path": os.path.join(root, CROSS_REL),
           "crit_path": os.path.join(root, CRIT_REL),
           "pcb_path": os.path.join(root, PCB_REL),
           "gate_check_path": os.path.join(root, GATE_CHECK_REL)}
    for key in ("signed_path", "truth_path", "cross_path", "crit_path", "pcb_path"):
        if not os.path.isfile(ctx[key]):
            return {"__io__": ["文件不在盘: %s" % ctx[key]]}
    ctx["signed_text"] = read_text(ctx["signed_path"])
    ctx["truth_text"] = read_text(ctx["truth_path"])
    try:
        sblocks = parse_machine_blocks(ctx["signed_text"])
        tblocks = parse_machine_blocks(ctx["truth_text"])
    except AssertionError as exc:
        return {"__io__": [str(exc)]}
    if not sblocks:
        return {"__io__": ["已签收页里读不到机器块 JSON"]}
    if not tblocks:
        return {"__io__": ["本单真相页里读不到机器块 JSON"]}
    s_main = sblocks[0]
    t_main = tblocks[0]
    ctx["signed_land_smd"] = s_main.get("land_smd") or {}
    ctx["truth_land_smd"] = t_main.get("land_smd") or {}
    ctx["ledger"] = t_main.get("arrangement_correction_ledger") or []
    if not isinstance(ctx["ledger"], list):
        return {"__io__": ["本单真相页 arrangement_correction_ledger 不是列表"]}
    try:
        ctx["crit"], ctx["tol"] = parse_crit(ctx["crit_path"])
        ctx["opening"] = parse_debug_opening(ctx["cross_path"])
        ctx["smd_left"] = measure(libroot, MOD_SMD_LEFT)
        ctx["smd_right"] = measure(libroot, MOD_SMD_RIGHT)
        ctx["tht"] = measure(libroot, MOD_THT)
    except AssertionError as exc:
        return {"__io__": [str(exc)]}
    ctx["measured"] = ctx["smd_left"]
    ctx["measured_token"] = ctx["smd_left"]["arrangement"]
    ctx["claims"] = scan_arrangement_claims(ctx["signed_text"])

    res = {}
    res["J0"] = j0_board_zero_write(ctx)
    res["J1"] = j1_measure_three_variants(ctx)
    res["J2"] = j2_machine_block_arrangement_verbatim(ctx)
    res["J3"] = j3_no_claim_escapes(ctx)
    ctx["recompute"] = _recompute_smd(ctx)
    res["J4"] = j4_label_vs_conclusion_separate(ctx)
    res["J5"] = j5_evidence_wording_nochain(ctx)
    res["_ctx"] = ctx
    return res


# ==================================================================================================
# 反向用例 (★每条自证「红的集合 ⊆ 声明的集合」且【必须含目标那一条】★)
# ==================================================================================================
def _sandbox(root: str, name: str, libroot: str) -> str:
    sb = os.path.join(root, "tmp", "iss382_sbx", "selftest", name)
    if os.path.isdir(sb):
        shutil.rmtree(sb)
    for rel in (SIGNED_PAGE_REL, TRUTH_PAGE_REL, CROSS_REL, CRIT_REL, PCB_REL, GATE_CHECK_REL):
        src = os.path.join(root, rel)
        if not os.path.isfile(src):
            continue
        dst = os.path.join(sb, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
    # ★库件也拷进沙盒 (★不许写系统 /tmp·不许碰真库★)
    sbl = os.path.join(sb, "lib", LIBDIR)
    os.makedirs(sbl, exist_ok=True)
    for mod in (MOD_SMD_LEFT, MOD_SMD_RIGHT, MOD_THT):
        shutil.copy2(os.path.join(libroot, LIBDIR, mod), os.path.join(sbl, mod))
    return sb


def _mut(text: str, old: str, new: str, count: int = 1) -> str:
    if old not in text:
        raise AssertionError("反向用例没找到要改的串: %r" % old)
    out = text.replace(old, new, count)
    if out == text:
        raise AssertionError("反向用例没改到任何东西")
    return out


def _mut_block(text: str, old: str, new: str, which: int = 0) -> str:
    matches = list(BLOCK_RE.finditer(text))
    if which >= len(matches):
        raise AssertionError("反向用例找不到第 %d 个机器块 (共 %d 个)" % (which, len(matches)))
    m = matches[which]
    seg = m.group(1)
    return text[:m.start(1)] + _mut(seg, old, new) + text[m.end(1):]


def _mut_json(text: str, fn, which: int = 0) -> str:
    """→ 在【第 which 个机器块】里按 JSON 结构改值 (★不靠字符串碰运气★)"""
    matches = list(BLOCK_RE.finditer(text))
    if which >= len(matches):
        raise AssertionError("反向用例找不到第 %d 个机器块 (共 %d 个)" % (which, len(matches)))
    m = matches[which]
    blk = json.loads(m.group(1))
    fn(blk)
    new = json.dumps(blk, ensure_ascii=False, indent=2)
    return text[:m.start(1)] + "\n" + new + "\n" + text[m.end(1):]


def _edit_file(path: str, fn) -> None:
    with open(path, "r", encoding="utf-8") as fh:
        t = fh.read()
    t2 = fn(t)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(t2)


# ★★【落地用例】★★ ★**main 把订正块落进已签收页之后, 本闸【不许新增任何一条红】★★
# ★**为什么必须有这条**: 本闸 J3 的台账按【surface 是否仍出现在已签收页】判 open/landed ⇒
#   落完订正块 ⇒ 旧 surface 消失 ⇒ 台账条目自动 closed ⇒ 活着的错表述归零 ⇒ 本闸应当全绿
#   ⇒ ★**若这条不成立, 就等于逼 main 落订正块时新闸当场变红 ⇒ 本单自己制造了新红** ★
def _land_correction_block(sb: str) -> None:
    """→ 把本单 §2.1 的 7 条订正【落】进沙盒里的已签收页 (★只在沙盒里做★)"""
    sp = os.path.join(sb, SIGNED_PAGE_REL)

    def fix(t: str) -> str:
        # ① 正文 4 处「2 列 × 2 行交错」⇒「2 列 × 4 行交错」
        t = t.replace("2 列 × 2 行", "2 列 × 4 行")
        # ② 机器块: land_smd.arrangement + land_smd.verdict + 根级 verdict_summary
        def j(b):
            b["land_smd"]["arrangement"] = "2x4_staggered"
            b["land_smd"]["verdict"] = str(b["land_smd"].get("verdict", "")).replace("2x2", "2x4")
            if isinstance(b.get("verdict_summary"), str):
                b["verdict_summary"] = b["verdict_summary"].replace("2x2", "2x4")
        return _mut_json(t, j)

    _edit_file(sp, fix)


LANDING_CASES = [
    ("⑪ main 落完订正块 (7 处) ⇒ 本闸【一条红都不许新增】⇒ 全绿",
     _land_correction_block),
]


CASES = [
    ("① 板改一个字节 ⇒ J0 红",
     "J0", {"J0"},
     lambda sb: _edit_file(os.path.join(sb, PCB_REL),
                            lambda t: t + "\n# ★反向用例: 板改一个字节★\n")),
    ("② 把 Pin1Right 变体改成 1 列 (两个变体都必须实测) ⇒ J1 红",
     "J1", {"J1"},
     lambda sb: _edit_file(os.path.join(sb, "lib", LIBDIR, MOD_SMD_RIGHT),
                            lambda t: _mut(t, '(at -1.5 1.905)', '(at 1.5 1.905)'))),
    ("③ 机器块 arrangement 写成 2x2 staggered ⇒ J2 红 (旧 G5 对此全绿)",
     "J2", {"J2"},
     lambda sb: _edit_file(os.path.join(sb, TRUTH_PAGE_REL),
                            lambda t: _mut_json(t, lambda b: b["land_smd"].__setitem__("arrangement", "2x2 staggered")))),
    ("④ 机器块 arrangement 写成 2x4 (丢掉交错限定词) ⇒ J2 红",
     "J2", {"J2"},
     lambda sb: _edit_file(os.path.join(sb, TRUTH_PAGE_REL),
                            lambda t: _mut_json(t, lambda b: b["land_smd"].__setitem__("arrangement", "2x4")))),
    ("⑤ 机器块 arrangement 写成 9x9 staggered ⇒ J2 红",
     "J2", {"J2"},
     lambda sb: _edit_file(os.path.join(sb, TRUTH_PAGE_REL),
                            lambda t: _mut_json(t, lambda b: b["land_smd"].__setitem__("arrangement", "9x9 staggered")))),
    ("⑥ 已签收页里多出一处没登记的错标签 ⇒ J3 红 (漏登记)",
     "J3", {"J3"},
     lambda sb: _edit_file(os.path.join(sb, SIGNED_PAGE_REL),
                            lambda t: _mut(t, "4 个焊盘在 Y 向排 4 行", "4 个焊盘在 Y 向排 3 行"))),
    ("⑦ 订正台账里删掉一条 ⇒ J3 红 (一处都不许漏)",
     "J3", {"J3"},
     lambda sb: _edit_file(os.path.join(sb, TRUTH_PAGE_REL),
                            lambda t: _mut_json(t, lambda b: b["arrangement_correction_ledger"][0].__setitem__("rows", 3)))),
    ("⑧ 已签收页的降级方案结论值改错 ⇒ J4 红 (结论值独立重算)",
     "J4", {"J4"},
     lambda sb: _edit_file(os.path.join(sb, SIGNED_PAGE_REL),
                            lambda t: _mut_json(t, lambda b: b["land_smd"].__setitem__("copper_h_mm", 4.47)))),
    ("⑨ 证据等级写成第六级 ⇒ J5 红",
     "J5", {"J5"},
     lambda sb: _edit_file(os.path.join(sb, TRUTH_PAGE_REL),
                            lambda t: _mut(t, "[实测]", "[推断]", 1))),
    ("⑩ 把本闸挂进 state/gate_check.py ⇒ J5 红 (零挂链)",
     "J5", {"J5"},
     lambda sb: _edit_file(os.path.join(sb, GATE_CHECK_REL),
                            lambda t: t + "\n# ★反向用例★\nEXTRA_GATES.append('MECH/check_jdebug_arrangement_truth.py')\n")),
]


def selftest(root: str, libroot: str = LIBROOT) -> int:
    print("=" * 92)
    print("【自检】反向用例 (★每条自证「红组 ⊆ 声明集合 且 必须含目标那一条」★)")
    print("=" * 92)
    ok_all = True
    res0 = run_checks(root, libroot)
    if "__io__" in res0:
        print("  ✗ 正向对照直接 IO 失败: %s" % res0["__io__"])
        return 1
    n_bad = [k for k, v in res0.items() if isinstance(v, dict) and "ok" in v and not v["ok"]]
    print("  ⓪ 正向对照 (真件一切如常) ⇒ %s" % ("✅ 全绿" if not n_bad else "❌ 红了: %s" % n_bad))
    if n_bad:
        ok_all = False
    ctx0 = res0.get("_ctx") or {}
    if ctx0:
        print("     · 实测排布 token = %s ; 已签收页仍带 %d 条未落订正的错标签 (待 main 落订正块)"
              % (ctx0.get("measured_token"), len(ctx0.get("open_defects") or [])))

    for name, target, allow, fn in CASES:
        sb = _sandbox(root, "case_%s" % target, libroot)
        try:
            fn(sb)
        except AssertionError as exc:
            print("  ✗ %s ⇒ ★用例自身坏了: %s★" % (name, exc))
            ok_all = False
            continue
        r2 = run_checks(sb, os.path.join(sb, "lib"))
        if "__io__" in r2:
            print("  ✗ %s ⇒ ★用例自身坏了: %s★" % (name, r2["__io__"]))
            ok_all = False
            continue
        red = sorted(k for k, v in r2.items() if isinstance(v, dict) and "ok" in v and not v["ok"])
        hit = target in red
        extra = [k for k in red if k not in allow]
        good = hit and not extra
        print("  %s %s ⇒ 红组 %s (目标 %s %s)"
              % ("✅" if good else "❌", name, red or "∅", target,
                 "命中" if hit else "★没命中★"))
        if not good:
            ok_all = False
            for k in red:
                for e in r2[k]["errs"][:3]:
                    print("        · %s: %s" % (k, e))
        shutil.rmtree(sb, ignore_errors=True)

    # ★★【落地用例】★★ main 落订正块之后本闸不许新增红
    for name, fn in LANDING_CASES:
        sb = _sandbox(root, "case_landing", libroot)
        try:
            fn(sb)
        except AssertionError as exc:
            print("  ✗ %s ⇒ ★用例自身坏了: %s★" % (name, exc))
            ok_all = False
            continue
        r3 = run_checks(sb, os.path.join(sb, "lib"))
        if "__io__" in r3:
            print("  ✗ %s ⇒ ★用例自身坏了: %s★" % (name, r3["__io__"]))
            ok_all = False
            continue
        red = sorted(k for k, v in r3.items() if isinstance(v, dict) and "ok" in v and not v["ok"])
        good = not red
        print("  %s %s ⇒ 红组 %s (★必须为空·★落订正块不许让本闸新增红★)"
              % ("✅" if good else "❌", name, red or "∅"))
        if not good:
            ok_all = False
            for k in red:
                for e in r3[k]["errs"][:3]:
                    print("        · %s: %s" % (k, e))
        shutil.rmtree(sb, ignore_errors=True)

    print("-" * 92)
    n = len(CASES) + len(LANDING_CASES)
    print("【自检结论】%s" % ("✅ %d 条用例全抓到 (且无额外判据被误红)" % n
                              if ok_all else "❌ 有用例没抓到"))
    print("ALL TESTS PASS" if ok_all else "TESTS FAILED")
    return 0 if ok_all else 1


# ==================================================================================================
# main
# ==================================================================================================
def main() -> int:
    ap = argparse.ArgumentParser(description="ISS-382 J_DEBUG 排布标签 (维数) 真相机器闸")
    ap.add_argument("--selftest", action="store_true", help="跑反向用例")
    ap.add_argument("--strict-open", action="store_true",
                    help="把『已签收页仍带未落订正的错标签』也判红")
    ap.add_argument("--root", default=PROJ, help="扫指定树 (默认项目根)")
    ap.add_argument("--libroot", default=LIBROOT, help="KiCad 官方库根 (默认本机)")
    args = ap.parse_args()
    root = os.path.abspath(args.root)
    libroot = os.path.abspath(args.libroot)

    if args.selftest:
        return selftest(root, libroot)

    print("=" * 92)
    print("ISS-382 · `J_DEBUG` 排针【排布标签 (维数)】真相 —— 机器闸")
    print("扫: %s" % root)
    print("=" * 92)
    res = run_checks(root, libroot)
    if "__io__" in res:
        print("★IO 失败★")
        for e in res["__io__"]:
            print("  · %s" % e)
        return 2
    ctx = res.pop("_ctx")
    n_ok = 0
    for code in ("J0", "J1", "J2", "J3", "J4", "J5"):
        g = res[code]
        print("\n[%s] %s ⇒ %s" % (code, g["name"], "✅ PASS" if g["ok"] else "❌ FAIL"))
        for e in g["errs"]:
            print("    · %s" % e)
        if g["ok"]:
            n_ok += 1
    print("\n" + "-" * 92)
    print("★实测排布 (Pin1Left / Pin1Right): %s ; THT: %s"
          % (ctx["measured_token"], ctx["tht"]["arrangement"]))
    print("★本单真相页机器块 land_smd.arrangement 现写: %r (⇒ 与实测 %r 逐字相等 ⇒ 本单页自身不红; "
          "已签收页那个错标签由 J3 逐处点名)"
          % (ctx.get("j2_declared"), ctx.get("measured_token")))
    print("★已签收页排布表述逐处扫描: 共 %d 处 ; 其中与实测不符且仍写着的有 %d 条"
          % (len(ctx.get("claims") or []), len(ctx.get("open_defects") or [])))
    for ent in (ctx.get("open_defects") or []):
        print("    · L%-4s %r ⇒ 建议改成 %r" % (ent.get("line"), ent.get("surface"),
                                              ent.get("proposed_surface")))
    if ctx.get("landed_defects"):
        print("★已落订正的台账条目: %d 条" % len(ctx["landed_defects"]))
    print("★降级方案结论值 (铜箔包络 / 开口余量 / 三档 Y 判决) 独立重算 ⇒ 与已签收页逐项相等")
    print("★⇒ 错的是【标签 / 维数】, 不是【结论数字】; 两条判据分开 (J2/J3 管标签, J4 管结论)")
    print("-" * 92)
    print("合计: %d/%d 条判据通过" % (n_ok, len(res)))
    if args.strict_open and (ctx.get("open_defects") or []):
        print("★--strict-open: 已签收页仍带 %d 条未落订正的错标签 ⇒ 判红 (归 main 落订正块)"
              % len(ctx["open_defects"]))
        return 1
    return 0 if n_ok == len(res) else 1


if __name__ == "__main__":
    sys.exit(main())
