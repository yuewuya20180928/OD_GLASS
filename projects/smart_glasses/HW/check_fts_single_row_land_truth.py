#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_fts_single_row_land_truth.py  ·  ISS-387 闸 K0~K6
「J_DEBUG / J_UART 单排直插 Samtec FTS 原厂 land 几何」真相页自检闸

用法:
    python3 HW/check_fts_single_row_land_truth.py             # 正向跑, rc=0 全绿
    python3 HW/check_fts_single_row_land_truth.py --selftest  # 自测, 末行 ALL TESTS PASS

★纪律:
  · fail-closed —— 任一条不满足 ⇒ 该条红 ⇒ 整体 rc=1
  · 每条闸至少一条反向用例 (--selftest 里把入参改坏 ⇒ 必须判红)
  · ★零写板 · 零落表 · 零挂链 · 只读 (本闸只读盘 + 只写自己的沙盒 tmp/iss387_sbx/)
  · ★本闸【不许挂进 state/gate_check.py】(挂链是 main 的地界) ⇒ 只交脚本 + 路径 + 建议
  · ★本闸【不许写死任何一个数】—— 全部数从真相页 §7.2 机器块读 ⇒ 改页即红 (这是设计, 不是 bug)

闸定义 (口径照抄真相页 §4 / §4.1 / §5-①):
  K0  真相页在盘 + §7.2 机器块在盘 + json.loads 能解析 + 机器块无空字段
      ([0数据] 允许, 空字符串 / 空列表 / 空字典 不允许)
  K1  ★命门★ positions_rows 必须是【1 排】(FTSH 是双排, 族不同 ⇒ 写成 2 排必须判红);
      且官网 prose 原句必须含 "1 Row"; 且 value_anchors 必须登记 ["1 排"]
  K2  copper_x_width / copper_y_width 必须【与盘上通用件实测值一致】或【[0数据] 且 degrade_refs
      有对应条目】⇒ 两种都合法; 第三种 (既不等于通用件、又非 [0数据]、又无降级条目) 必须判红
      ★通用件的数从机器块 generic_part_measured 读, 本闸不许写死 4.8100 / 2.2700
  K3  ★命门★ deviation_vs_generic_part.status 必须是 registered; 凡 copper_x_width 与通用件不一致,
      必须逐条登记 (part / field / samtec_value / generic_value), 且影响面清单必须点名 MECH 那几行
      ⇒ 没登记就判红 (不许默默写一个不同的数)
  K4  ★命门★ 不许拿 FTSH 的数顶替 FTS: FTS 料号字段里出现 FTSH / 同字段两族并列 / 机器块里多出
      FTSH 料号条目 ⇒ 判红
  K5  证据分级白名单 ([官网]/[媒体]/[实测]/[推算]/[0数据]) + 零挂起措辞 + 判据句与事实句分开
      (事实句必须锚到官网逐字原句; 判据句必须落在 §4 / §4.1, 不许混进 §2 / §3 事实抄录节)
  K6  板三项指纹未动 (md5 / size / mtime) + 零落表 (网表 / 脚表 / BOM 三件 md5 与基线同)
      + 零挂链 (state/gate_check.py 命中数 = 0) + 机器块 board_write / table_write /
      mech_files_touched 三个字段必须是 none

★沙盒纪律 (★本机已踩过的坑★):
  现役 SW/tools/check_debug_pin_order_contract.py 默认写系统 /tmp ⇒ 本机 10/11 FAIL;
  TMPDIR=$PWD/tmp ⇒ 11/11 PASS ⇒ 本闸的沙盒一律落【项目盘】tmp/iss387_sbx/,
  路径从本闸自己的 ROOT 推, 不许依赖系统 /tmp 的深度。
"""

import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import sys

# ---------------------------------------------------------------------------
# 路径 (★全部从本闸自己的位置推 ⇒ 与 cwd 无关★)
# ---------------------------------------------------------------------------
PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(PROJ, "HW", "PCB", "BOARD_ONEPASS_FTS_SINGLE_ROW_LAND_TRUTH.md")
BOARD = os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb")
NETLIST = os.path.join(PROJ, "HW", "netlist_v1.csv")
PINS = os.path.join(PROJ, "HW", "netlist_v1_pins.csv")
BOM = os.path.join(PROJ, "HW", "BOM_v1.csv")
GATE_CHECK = os.path.join(PROJ, "state", "gate_check.py")
SANDBOX = os.path.join(PROJ, "tmp", "iss387_sbx")

# ---------------------------------------------------------------------------
# 基线指纹 (★与 main 2026-11-24 10:4x 本机实跑基线同★)
# ---------------------------------------------------------------------------
EXP_BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"
EXP_BOARD_SIZE = 4940213
EXP_BOARD_MTIME = "2026-11-06 07:07:17.362193"
EXP_NETLIST_MD5 = "6aee500e60ba0732f83a9cf557ba90ab"
EXP_PINS_MD5 = "9174309df1ec9411ac8e8d9e80ee386a"
EXP_BOM_MD5 = "5b9993992405904a60ac96a020b375d8"
GATE_NAME = "check_fts_single_row_land_truth"

# ---------------------------------------------------------------------------
# 词表
# ---------------------------------------------------------------------------
GRADES = ("[官网]", "[媒体]", "[实测]", "[推算]", "[0数据]")
ZERO_DATA = "[0数据]"

# FTS 族料号形态 (4 位 1 排直插) —— FTSH 不在此形态内
FTS_PART_RE = re.compile(r"^FTS-\d{3}-\d{2}-F-S$")
FTSH_RE = re.compile(r"FTSH", re.I)      # ★不分大小写 ⇒ URL 里的小写 ftsh- 也算族别混用★

# 证据等级白名单里的完整标签 (K5 用)
EVIDENCE_LABELS = ("官网", "媒体", "实测", "推算", "0数据", "0 数据")

# 零挂起措辞 (K5)
# ★强挂起词 = 全页扫 (带「否定语境」豁免)
HANG_STRONG = (
    "等原厂回信", "等原厂确认", "待外部确认", "等外部确认",
    "等回复", "pending reply", "awaiting reply",
    "等官网恢复", "等厂商确认", "待厂商", "等厂家", "原厂回信后",
)
# ★弱挂起词 = 只在【本单自身产出面】扫 (机器块 + §6 降级方案 + §7);
#   正文中转引 A2 原文的「待确认项」是【描述别人的清单】, 不算本单挂起
#   ★注: 「待定」不入表 —— 本项目里「待定」是 BOM 型号栏现状字段名 (§6-③ / §7.1-7-8
#     引的是 HW/BOM_v1.csv 第 71/77 行的原文), 那是【事实】不是挂起
HANG_WEAK = ("待确认", "悬置", "挂起", "等确认", "未答复", "待复")
# 否定语境标记 (出现任一 ⇒ 该处的挂起词是【禁止令 / 反例引用】, 不算挂起)
NEGATION_MARKS = (
    "不许", "不得", "禁", "不写", "不挂起", "零挂起", "不是", "没有",
    "≠", "而不是", "已消除", "零等待", "不靠", "不依赖",
)
# 现状描述标记 (引的是盘上现状 ⇒ 该行的挂起词是【被描述的对象】, 不是本单的挂起)
STATUS_OF_FACT_MARKS = ("现盘上", "盘上", "现状", "当前", "目前", "仍「", "行 71", "行 77")

# 判据句 / 事实句分开 (K5) —— 裁决语不许出现在事实字段里
VERDICT_WORDS = ("应采用", "已决定", "已拍", "裁决", "应该采用", "选定", "拍板")

CN_TZ = datetime.timezone(datetime.timedelta(hours=8))


# =========================================================================
# 入参采集 (全部只读)
# =========================================================================
def read_text(path):
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read()


def md5_of(path):
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def mtime_iso(path):
    return datetime.datetime.fromtimestamp(
        os.stat(path).st_mtime, CN_TZ).strftime("%Y-%m-%d %H:%M:%S.%f")


def collect(page_text=None, facts=None):
    """把闸要用的全部入参收成 dict —— 自测时逐项替换即可制造反向用例。"""
    ctx = {}
    ctx["page"] = read_text(PAGE) if page_text is None else page_text
    ctx["page_exists"] = os.path.exists(PAGE) or page_text is not None
    if facts is None:
        facts = {
            "board_md5": md5_of(BOARD),
            "board_size": os.path.getsize(BOARD),
            "board_mtime": mtime_iso(BOARD),
            "netlist_md5": md5_of(NETLIST),
            "pins_md5": md5_of(PINS),
            "bom_md5": md5_of(BOM),
            "chain_hits": count_chain_hits(),
        }
    ctx["facts"] = facts
    mb, err = parse_machine_block(ctx["page"])
    ctx["mb"] = mb
    ctx["mb_error"] = err
    return ctx


def count_chain_hits():
    """state/gate_check.py 里命中本闸名的行数 (零挂链 = 0)。"""
    if not os.path.exists(GATE_CHECK):
        return -1
    n = 0
    with open(GATE_CHECK, "r", encoding="utf-8", errors="replace") as fh:
        for ln in fh:
            if GATE_NAME in ln:
                n += 1
    return n


def parse_machine_block(page_text):
    """从真相页里抽出 §7.2 的 json 机器块。返回 (dict, err)。"""
    blocks = re.findall(r"```json\s*\n(.*?)\n```", page_text, re.S)
    if not blocks:
        return None, "真相页里找不到 ```json 机器块"
    parsed = []
    for b in blocks:
        try:
            parsed.append(json.loads(b))
        except Exception as exc:  # noqa: BLE001
            continue
    if not parsed:
        return None, "机器块 json.loads 解析失败 (共 %d 个 json 块)" % len(blocks)
    for d in parsed:
        if isinstance(d, dict) and str(d.get("schema", "")).startswith(
                "hw.fts.single_row.land_truth"):
            return d, ""
    return parsed[-1], ""


def prose_only(page):
    """去掉 ```json 机器块, 只留正文 —— 事实句锚点必须在【正文】里出现,
    只在机器块里自说自话不算 (否则「原句」判据会退化成回声)。"""
    return re.sub(r"```json\s*\n.*?\n```", "", page, flags=re.S)


def sec_body(page, start_marker, end_marker=None):
    """从 start_marker 到下一个 '## ' (或 end_marker) 之间的正文。"""
    i = page.find(start_marker)
    if i < 0:
        return ""
    rest = page[i + len(start_marker):]
    j = rest.find("\n## ")
    k = rest.find(end_marker) if end_marker else -1
    ends = [x for x in (j, k) if x >= 0]
    return rest[:min(ends)] if ends else rest


def walk_empty(node, path="$"):
    """递归找空字段 (空字符串 / 空列表 / 空字典)。"""
    out = []
    if isinstance(node, dict):
        for k, v in node.items():
            out += walk_empty(v, "%s.%s" % (path, k))
    elif isinstance(node, list):
        if len(node) == 0:
            out.append("%s (空列表)" % path)
        for i, v in enumerate(node):
            out += walk_empty(v, "%s[%d]" % (path, i))
    elif isinstance(node, str):
        if node.strip() == "":
            out.append("%s (空字符串)" % path)
    if isinstance(node, dict) and len(node) == 0:
        out.append("%s (空字典)" % path)
    return out


def generic_of(mb, part):
    """按 pad_count 匹配盘上通用件 (★从机器块推, 不写死★)。"""
    parts = mb.get("parts") or {}
    spec = parts.get(part) or {}
    pos = spec.get("positions")
    gm = mb.get("generic_part_measured") or {}
    for ref, info in gm.items():
        if not isinstance(info, dict):
            continue
        if info.get("pad_count") == pos:
            return ref, info
    return None, None


def num_eq(a, b):
    """字符串数值比较 (允许 '4.8100' == '4.81')。"""
    try:
        return abs(float(a) - float(b)) < 1e-9
    except (TypeError, ValueError):
        return str(a).strip() == str(b).strip()


# =========================================================================
# K0  真相页在盘 + 机器块在盘 + 可解析 + 无空字段
# =========================================================================
REQUIRED_TOP_KEYS = (
    "schema", "issue", "agent", "updated", "truth_doc",
    "landing_part_decision", "board_write", "table_write", "mech_files_touched",
    "parts", "generic_part_measured", "deviation_vs_generic_part",
    "degrade_refs", "open_items",
)
REQUIRED_PARTS = ("FTS-104-01-F-S", "FTS-102-01-F-S")


def k0(ctx):
    fails = []
    if not ctx["page_exists"] or not ctx["page"].strip():
        fails.append("K0 真相页不在盘或为空: %s" % PAGE)
        return fails
    if ctx["mb_error"]:
        fails.append("K0 %s" % ctx["mb_error"])
        return fails
    mb = ctx["mb"]
    if not isinstance(mb, dict):
        fails.append("K0 机器块不是 dict")
        return fails
    for key in REQUIRED_TOP_KEYS:
        if key not in mb:
            fails.append("K0 机器块缺顶层字段 `%s`" % key)
    for p in REQUIRED_PARTS:
        if p not in (mb.get("parts") or {}):
            fails.append("K0 机器块 parts 缺 FTS 料号 `%s`" % p)
    if "### §7.2" not in ctx["page"]:
        fails.append("K0 真相页里找不到 `### §7.2` 机器块小节")
    empties = walk_empty(mb)
    for e in empties:
        fails.append("K0 机器块有空字段: %s" % e)
    return fails


# =========================================================================
# K1  positions_rows 必须 1 排 (★族别辨析的命门★)
# =========================================================================
def rows_of(value):
    """从 '1 排' / '2 排' / '1 Row' 这类串里取出排数; 取不出返回 None。"""
    m = re.search(r"(\d+)\s*(?:排|Row)", str(value))
    return int(m.group(1)) if m else None


def k1(ctx):
    fails = []
    if ctx["mb_error"]:
        return fails
    mb = ctx["mb"]
    for p in REQUIRED_PARTS:
        spec = (mb.get("parts") or {}).get(p)
        if not isinstance(spec, dict):
            continue
        val = spec.get("positions_rows")
        n = rows_of(val)
        if n is None:
            fails.append("K1 `%s` positions_rows = %r ⇒ 解析不出排数" % (p, val))
        elif n != 1:
            fails.append(
                "K1 ★命门★ `%s` positions_rows = %r ⇒ %d 排 ⇒ 判红 "
                "(FTS 单排直插 = 1 排; FTSH 是双排, 族不同, 不许顶替)" % (p, val, n))
        anchors = (spec.get("value_anchors") or {}).get("positions_rows")
        if anchors != ["1 排"]:
            fails.append("K1 `%s` value_anchors.positions_rows = %r (应 ['1 排'])"
                         % (p, anchors))
        prose = spec.get("prose_anchors") or []
        if not any(re.search(r"\b1\s+Row\b", str(a)) for a in prose):
            fails.append("K1 `%s` prose_anchors 里没有官网原句 `1 Row` 锚点 ⇒ "
                         "排数这条事实没有官网原句背书" % p)
        for a in prose:
            if re.search(r"\b2\s+Rows?\b", str(a)):
                fails.append("K1 `%s` prose_anchors 出现 `2 Row` ⇒ 与 FTS 单排冲突" % p)
    return fails


# =========================================================================
# K2  copper_x_width / copper_y_width 必须「等于通用件」或「[0数据] + 降级条目」
# =========================================================================
COPPER_FIELDS = ("copper_x_width", "copper_y_width")


def k2(ctx):
    fails = []
    if ctx["mb_error"]:
        return fails
    mb = ctx["mb"]
    degrade = mb.get("degrade_refs") or {}
    for p in REQUIRED_PARTS:
        spec = (mb.get("parts") or {}).get(p)
        if not isinstance(spec, dict):
            continue
        ref, ginfo = generic_of(mb, p)
        if not ginfo:
            fails.append("K2 `%s` 在 generic_part_measured 里找不到 pad_count=%r 的通用件 ⇒ 无法比对"
                         % (p, (spec or {}).get("positions")))
            continue
        for field in COPPER_FIELDS:
            val = spec.get(field)
            gval = (ginfo or {}).get(field)
            if gval is None:
                fails.append("K2 通用件 `%s` 没有 `%s` 字段" % (ref, field))
                continue
            if val is None:
                fails.append("K2 `%s` 缺字段 `%s`" % (p, field))
                continue
            if num_eq(val, gval):
                continue                                  # 情形 A: 与通用件一致
            if str(val).strip() == ZERO_DATA:
                if field not in degrade or not str(degrade.get(field, "")).strip():
                    fails.append("K2 `%s.%s` = [0数据] 但 degrade_refs 里没有 `%s` 的降级条目"
                                 % (p, field, field))
                continue                                  # 情形 B: [0数据] + 降级
            # 情形 C: 既不等于通用件, 又不是 [0数据] ⇒ 判红
            fails.append(
                "K2 ★`%s.%s` = %r 既不等于盘上通用件 `%s` 的 %r, 又不是 [0数据] ⇒ "
                "第三种情形, 判红 (不许默默写一个来源不明的数)"
                % (p, field, val, ref, gval))
    return fails


# =========================================================================
# K3  偏离必须显式登记 + 影响面必须点名 MECH 那几行
# =========================================================================
MECH_SCRIPT_TARGET = "MECH/check_debug_seat_3d_fit.py"
MECH_PAGE_TARGET = "MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md"
MECH_NUMBERS = ("6.6100", "4.0700", "0.1350", "2.6950", "0.7700")
MECH_OI = ("OI-5", "OI-12")


def k3(ctx):
    fails = []
    if ctx["mb_error"]:
        return fails
    mb = ctx["mb"]
    dev = mb.get("deviation_vs_generic_part")
    if not isinstance(dev, dict):
        fails.append("K3 机器块缺 deviation_vs_generic_part")
        return fails
    if dev.get("status") != "registered":
        fails.append("K3 ★命门★ deviation_vs_generic_part.status = %r (应 'registered') ⇒ "
                     "偏离没登记就判红" % dev.get("status"))
    diffs = dev.get("differing_values")
    if not isinstance(diffs, list):
        fails.append("K3 deviation_vs_generic_part.differing_values 不是列表")
        diffs = []
    targets = dev.get("impact_targets")
    if not isinstance(targets, list):
        fails.append("K3 deviation_vs_generic_part.impact_targets 不是列表")
        targets = []

    # 3-1 每个 FTS 件的 copper_x_width 偏离必须逐条登记
    for p in REQUIRED_PARTS:
        spec = (mb.get("parts") or {}).get(p)
        if not isinstance(spec, dict):
            continue
        _, ginfo = generic_of(mb, p)
        if not ginfo:
            continue
        sval = spec.get("copper_x_width")
        gval = ginfo.get("copper_x_width")
        if gval is None or sval is None:
            continue
        if num_eq(sval, gval):
            continue                       # 无偏离 (与通用件一致) ⇒ 本条不适用
        hit = [d for d in diffs
               if isinstance(d, dict) and d.get("part") == p
               and d.get("field") == "copper_x_width"]
        if not hit:
            fails.append("K3 ★命门★ `%s.copper_x_width` = %r 与通用件 %r 不一致, "
                         "但 differing_values 里没有登记这条 ⇒ 判红"
                         % (p, sval, gval))
            continue
        d = hit[0]
        if not num_eq(d.get("generic_value"), gval):
            fails.append("K3 `%s.copper_x_width` 登记的 generic_value = %r ≠ 通用件实测 %r"
                         % (p, d.get("generic_value"), gval))
        if not num_eq(d.get("samtec_value"), sval):
            fails.append("K3 ★命门★ `%s.copper_x_width` 登记的 samtec_value = %r ≠ "
                         "机器块里实际写的 %r ⇒ 登记与事实对不上 ⇒ 判红"
                         % (p, d.get("samtec_value"), sval))

    # 3-2 影响面清单必须点名 MECH 那几行
    ttext = "\n".join(str(t) for t in targets)
    if MECH_SCRIPT_TARGET not in ttext:
        fails.append("K3 影响面清单里没有点名 `%s`" % MECH_SCRIPT_TARGET)
    if MECH_PAGE_TARGET not in ttext:
        fails.append("K3 影响面清单里没有点名 `%s`" % MECH_PAGE_TARGET)
    for n in MECH_NUMBERS:
        if n not in ttext:
            fails.append("K3 影响面清单里没有点名 MECH 侧的数 `%s`" % n)
    for o in MECH_OI:
        if o not in ttext:
            fails.append("K3 影响面清单里没有点名 `%s`" % o)
    # 3-3 影响面点名的文件必须真实存在 (不许写空气)
    for t in targets:
        s = str(t)
        if ":" not in s:
            continue
        path = s.rsplit(":", 1)[0]
        if path.startswith("MECH/") or path.startswith("HW/"):
            if not os.path.exists(os.path.join(PROJ, path)):
                fails.append("K3 影响面点名的文件不存在: %s" % path)
    return fails


# =========================================================================
# K4  不许拿 FTSH 的数顶替 FTS
# =========================================================================
def k4(ctx):
    fails = []
    if ctx["mb_error"]:
        return fails
    mb = ctx["mb"]
    parts = mb.get("parts") or {}
    for p, spec in parts.items():
        if FTSH_RE.search(str(p)):
            fails.append("K4 ★命门★ 机器块 parts 里出现 FTSH 料号 `%s` ⇒ "
                         "FTSH 是另一个族 (双排贴片), 不许顶替 FTS" % p)
            continue
        if not FTS_PART_RE.match(str(p)):
            fails.append("K4 parts 里的料号 `%s` 不符合 FTS 单排直插形态 FTS-xxx-xx-F-S" % p)
        if not isinstance(spec, dict):
            continue
        for field, val in spec.items():
            if isinstance(val, str) and FTSH_RE.search(val):
                fails.append("K4 ★命门★ `%s.%s` 里出现 FTSH ⇒ 族别混用判红 (实读 %r)"
                             % (p, field, val))
    # 页面侧: 族别辨析必须被显式登记过 (不是不许提 FTSH, 是不许拿它的数顶替)
    if "FTSH" not in ctx["page"]:
        fails.append("K4 真相页里根本没有 FTSH 的族别辨析登记 ⇒ 族边界没写下来")
    if "族别辨析" not in ctx["page"]:
        fails.append("K4 真相页里找不到「族别辨析」字样 ⇒ 族边界没写下来")
    return fails


# =========================================================================
# K5  证据分级 + 零挂起 + 判据句与事实句分开
# =========================================================================
def k5(ctx):
    fails = []
    if ctx["mb_error"]:
        return fails
    mb = ctx["mb"]
    page = ctx["page"]

    # 5-1 证据分级白名单
    for p in REQUIRED_PARTS:
        spec = (mb.get("parts") or {}).get(p)
        if not isinstance(spec, dict):
            continue
        ev = spec.get("evidence")
        if ev not in GRADES:
            fails.append("K5 `%s` evidence = %r 不在白名单 %s" % (p, ev, list(GRADES)))
    found = [g for g in GRADES if g in page]
    if len(found) < 3:
        fails.append("K5 真相页里出现的证据等级只有 %d 种 (%s) ⇒ 至少要 3 种"
                     % (len(found), found))

    # 5-2 零挂起措辞 (强挂起词 = 全页扫; 弱挂起词 = 本单自身产出面扫)
    for i, ln in enumerate(page.split("\n"), 1):
        for h in HANG_STRONG:
            if h in ln and not any(m in ln for m in NEGATION_MARKS):
                fails.append("K5 第 %d 行出现挂起措辞 `%s` ⇒ 零挂起判红" % (i, h))
    own_out = "\n".join([
        sec_body(page, "## §6"),
        sec_body(page, "## §7"),
        json.dumps(mb, ensure_ascii=False),
    ])
    for i, ln in enumerate(own_out.split("\n"), 1):
        if any(m in ln for m in STATUS_OF_FACT_MARKS):
            continue                      # 现状描述行 (引的是盘上现状, 不是本单的挂起)
        for h in HANG_WEAK:
            if h in ln and not any(m in ln for m in NEGATION_MARKS):
                fails.append("K5 本单产出面 (§6 / §7 / 机器块) 第 %d 行出现挂起措辞 `%s` ⇒ 零挂起判红"
                             % (i, h))

    # 5-3 判据句与事实句分开
    # (甲) 事实句必须锚到官网逐字原句 (★只在正文里找, 不许只在机器块里自说自话★)
    body = prose_only(page)
    for p in REQUIRED_PARTS:
        spec = (mb.get("parts") or {}).get(p)
        if not isinstance(spec, dict):
            continue
        for a in (spec.get("prose_anchors") or []):
            if str(a) not in body:
                fails.append("K5 `%s` 的官网原句锚点 `%s` 在真相页正文里找不到 ⇒ "
                             "事实句没有原文背书" % (p, a))
    # (乙) 事实字段里不许混进裁决语
    for p, spec in (mb.get("parts") or {}).items():
        if not isinstance(spec, dict):
            continue
        for field, val in spec.items():
            if isinstance(val, str):
                for w in VERDICT_WORDS:
                    if w in val:
                        fails.append("K5 ★`%s.%s` 事实字段里混进裁决语 `%s` ⇒ "
                                     "判据句与事实句混成一句" % (p, field, w))
    if mb.get("landing_part_decision") != "not_decided_here":
        fails.append("K5 landing_part_decision = %r (应 'not_decided_here') ⇒ 本单不许代拍"
                     % mb.get("landing_part_decision"))
    # (丙) 判据句必须落在 §4 / §4.1, 不许混进 §2 / §3 的事实抄录节
    s4 = sec_body(page, "## §4")
    s2 = sec_body(page, "## §2", "## §3")
    s3 = sec_body(page, "## §3", "## §4")
    if "判据" not in s4:
        fails.append("K5 §4 对比表里没有「判据」字样 ⇒ 判据句没单独落地")
    for name, body in (("§2", s2), ("§3", s3)):
        if "判据" in body:
            fails.append("K5 判据句混进了 %s 事实抄录节 ⇒ 判据句与事实句混成一句" % name)
    return fails


# =========================================================================
# K6  板三项指纹 + 零落表 + 零挂链 + 机器块三字段 none
# =========================================================================
def k6(ctx):
    fails = []
    f = ctx["facts"]
    if f.get("board_md5") != EXP_BOARD_MD5:
        fails.append("K6 板 md5 = %r ≠ 基线 %s ⇒ 写板了"
                     % (f.get("board_md5"), EXP_BOARD_MD5))
    if f.get("board_size") != EXP_BOARD_SIZE:
        fails.append("K6 板 size = %r ≠ 基线 %d" % (f.get("board_size"), EXP_BOARD_SIZE))
    if f.get("board_mtime") != EXP_BOARD_MTIME:
        fails.append("K6 板 mtime = %r ≠ 基线 %s" % (f.get("board_mtime"), EXP_BOARD_MTIME))
    for key, exp, name in (
            ("netlist_md5", EXP_NETLIST_MD5, "HW/netlist_v1.csv"),
            ("pins_md5", EXP_PINS_MD5, "HW/netlist_v1_pins.csv"),
            ("bom_md5", EXP_BOM_MD5, "HW/BOM_v1.csv")):
        if f.get(key) != exp:
            fails.append("K6 %s md5 = %r ≠ 基线 %s ⇒ 落表了" % (name, f.get(key), exp))
    if f.get("chain_hits") != 0:
        fails.append("K6 state/gate_check.py 里命中本闸 %r 次 (应 0) ⇒ 挂链了 (挂链是 main 的地界)"
                     % f.get("chain_hits"))
    if not ctx["mb_error"]:
        mb = ctx["mb"]
        for key in ("board_write", "table_write", "mech_files_touched"):
            if mb.get(key) != "none":
                fails.append("K6 机器块 %s = %r (应 'none')" % (key, mb.get(key)))
    return fails


# =========================================================================
# 闸编排
# =========================================================================
CHECKS = (
    ("K0", k0, "真相页 + 机器块在盘 / 可解析 / 无空字段"),
    ("K1", k1, "positions_rows 必须 1 排 (族别辨析命门)"),
    ("K2", k2, "铜箔宽: 等于通用件 或 [0数据]+降级"),
    ("K3", k3, "偏离必须登记 + 影响面点名 MECH"),
    ("K4", k4, "不许拿 FTSH 顶替 FTS"),
    ("K5", k5, "证据分级 / 零挂起 / 判据与事实分开"),
    ("K6", k6, "零写板 / 零落表 / 零挂链"),
)


def run_all(ctx):
    results = []
    for code, fn, desc in CHECKS:
        fails = fn(ctx)
        results.append((code, desc, fails))
    return results


def report(results, title):
    print("── %s" % title)
    nfail = 0
    for code, desc, fails in results:
        if fails:
            nfail += 1
            print("  [%s] ✘ RED  %s" % (code, desc))
            for f in fails:
                print("        · %s" % f)
        else:
            print("  [%s] ✔ GREEN  %s" % (code, desc))
    print("── %s: %d/%d 条绿" % (title, len(results) - nfail, len(results)))
    return nfail


# =========================================================================
# 自测 (★沙盒落项目盘 tmp/iss387_sbx/ ⇒ 与系统 /tmp 无关★)
# =========================================================================
def _mutate(mb_text, old, new):
    """在 json 文本上做一次替换 (只用于自测制造反向用例)。"""
    if old not in mb_text:
        raise AssertionError("自测用例前提不成立: 机器块里找不到 `%s`" % old)
    return mb_text.replace(old, new, 1)


def _rebuild_page(page_text, mb_text):
    """把页面里的机器块换掉 (只用于自测)。"""
    blocks = list(re.finditer(r"```json\s*\n(.*?)\n```", page_text, re.S))
    if not blocks:
        raise AssertionError("自测用例前提不成立: 页面里没有 json 块")
    last = blocks[-1]
    return page_text[:last.start(1)] + mb_text + page_text[last.end(1):]


def selftest():
    os.makedirs(SANDBOX, exist_ok=True)
    base_page = read_text(PAGE)
    base_mb, err = parse_machine_block(base_page)
    if err:
        print("SELFTEST ABORT: %s" % err)
        return 1
    base_mb_text = json.dumps(base_mb, ensure_ascii=False, indent=1)

    # 沙盒里落一份真相页副本 (★只落项目盘★)
    sb_page = os.path.join(SANDBOX, "BOARD_ONEPASS_FTS_SINGLE_ROW_LAND_TRUTH.md")
    with open(sb_page, "w", encoding="utf-8") as fh:
        fh.write(base_page)

    facts = collect()["facts"]
    cases = []          # (用例名, 期望红的那条, 页面文本)

    # --- 正向对照: 原页面必须全绿 -------------------------------------
    ctx0 = collect(page_text=base_page, facts=facts)
    cases.append(("正向对照 (原页面)", None, base_page))

    # --- 反向用例 1: positions_rows 1 排 → 2 排 ⇒ K1 红 -------------
    t = _mutate(base_mb_text, '"positions_rows": "1 排",\n   "mount_style"',
                '"positions_rows": "2 排",\n   "mount_style"')
    cases.append(("① 把 FTS-104 的 positions_rows 从 1 排改成 2 排 ⇒ K1 红",
                  "K1", _rebuild_page(base_page, t)))

    # --- 反向用例 2: copper_x_width 改成与通用件不同的数, 且影响面里抹掉 MECH ⇒ K3 红
    mb2 = json.loads(base_mb_text)
    mb2["parts"]["FTS-104-01-F-S"]["copper_x_width"] = "9.9900"
    for d in mb2["deviation_vs_generic_part"]["differing_values"]:
        if d.get("part") == "FTS-104-01-F-S" and d.get("field") == "copper_x_width":
            d["samtec_value"] = "9.9900"
    mb2["deviation_vs_generic_part"]["impact_targets"] = [
        t for t in mb2["deviation_vs_generic_part"]["impact_targets"]
        if MECH_PAGE_TARGET not in t]
    cases.append(("② copper_x_width 改成 9.9900 且影响面抹掉 MECH 那几行 ⇒ K3 红",
                  "K3", _rebuild_page(base_page, json.dumps(mb2, ensure_ascii=False, indent=1))))

    # --- 反向用例 3: deviation status registered → not_registered ⇒ K3 红
    t = _mutate(base_mb_text, '"status": "registered"', '"status": "not_registered"')
    cases.append(("③ deviation_vs_generic_part.status 从 registered 改掉 ⇒ K3 红",
                  "K3", _rebuild_page(base_page, t)))

    # --- 反向用例 4: 把 FTSH-104-01-F-DV 塞进 FTS 料号字段 ⇒ K4 红
    t = _mutate(base_mb_text,
                '"datasheet_url": "https://www.samtec.com/products/fts-104-01-f-s"',
                '"datasheet_url": "https://www.samtec.com/products/ftsh-104-01-f-dv"')
    cases.append(("④ 把 FTSH-104-01-F-DV 塞进 FTS 料号字段 ⇒ K4 红",
                  "K4", _rebuild_page(base_page, t)))

    # --- 反向用例 5: 机器块里多出一个 FTSH 料号条目 ⇒ K4 红
    mb5 = json.loads(base_mb_text)
    mb5["parts"]["FTSH-104-01-F-DV"] = dict(mb5["parts"]["FTS-104-01-F-S"])
    mb5["parts"]["FTSH-104-01-F-DV"]["positions_rows"] = "2 排"
    cases.append(("⑤ 机器块里多出 FTSH-104-01-F-DV 条目 ⇒ K4 红",
                  "K4", _rebuild_page(base_page, json.dumps(mb5, ensure_ascii=False, indent=1))))

    # --- 反向用例 6: copper_y_width 写成第三种数 (既非通用件也非 [0数据]) ⇒ K2 红
    t = _mutate(base_mb_text, '"copper_y_width": "[0数据]"', '"copper_y_width": "2.0000"')
    cases.append(("⑥ copper_y_width 写成 2.0000 (第三种情形) ⇒ K2 红",
                  "K2", _rebuild_page(base_page, t)))

    # --- 反向用例 7: [0数据] 但 degrade_refs 里没有对应条目 ⇒ K2 红
    mb7 = json.loads(base_mb_text)
    mb7["degrade_refs"].pop("copper_x_width", None)
    cases.append(("⑦ copper_x_width 仍是 [0数据] 但 degrade_refs 里删掉降级条目 ⇒ K2 红",
                  "K2", _rebuild_page(base_page, json.dumps(mb7, ensure_ascii=False, indent=1))))

    # --- 反向用例 8: 证据等级不在白名单 ⇒ K5 红
    t = _mutate(base_mb_text, '"evidence": "[官网]"', '"evidence": "官网(无括号)"')
    cases.append(("⑧ evidence 写成「官网(无括号)」不在白名单 ⇒ K5 红",
                  "K5", _rebuild_page(base_page, t)))

    # --- 反向用例 9: §6 里塞一句挂起措辞 ⇒ K5 红
    hang_page = base_page.replace(
        "### 6-④ ★「直插档座体外形尺寸 (keepout 几何)」的降级",
        "### 6-④ ★「直插档座体外形尺寸 (keepout 几何)」的降级\n等原厂回信", 1)
    cases.append(("⑨ §6 里塞一句「等原厂回信」⇒ K5 红", "K5", hang_page))

    # --- 反向用例 10: 判据句混进 §2 事实抄录节 ⇒ K5 红
    mix_page = base_page.replace(
        "## §2 `FTS-104-01-F-S` (4 位) 官网单品页逐项抄录",
        "## §2 `FTS-104-01-F-S` (4 位) 官网单品页逐项抄录\n\n"
        "★判据: 铜箔 X 宽若不一致则影响 MECH L491。", 1)
    cases.append(("⑩ 判据句混进 §2 事实抄录节 ⇒ K5 红", "K5", mix_page))

    # --- 反向用例 11: 机器块 json 解析失败 ⇒ K0 红
    broken = base_mb_text.replace('"schema":', '"schema"', 1)
    cases.append(("⑪ 机器块 json 被改坏 ⇒ K0 红", "K0", _rebuild_page(base_page, broken)))

    # --- 反向用例 12: 机器块里出现空字符串字段 ⇒ K0 红
    mb12 = json.loads(base_mb_text)
    mb12["parts"]["FTS-102-01-F-S"]["mount_style"] = ""
    cases.append(("⑫ 机器块里出现空字符串字段 ⇒ K0 红",
                  "K0", _rebuild_page(base_page, json.dumps(mb12, ensure_ascii=False, indent=1))))

    # --- 反向用例 13: 机器块 board_write 改成 yes ⇒ K6 红
    t = _mutate(base_mb_text, '"board_write": "none"', '"board_write": "yes"')
    cases.append(("⑬ 机器块 board_write 改成 yes ⇒ K6 红", "K6", _rebuild_page(base_page, t)))

    # --- 反向用例 14: 板 md5 指纹被动过 ⇒ K6 红
    bad_facts = dict(facts)
    bad_facts["board_md5"] = "00000000000000000000000000000000"
    ctx14 = collect(page_text=base_page, facts=bad_facts)
    cases.append(("⑭ 板 md5 被动过 ⇒ K6 红", "K6", ("FACTS", ctx14)))

    # --- 反向用例 15: landing_part_decision 代拍 ⇒ K5 红
    t = _mutate(base_mb_text, '"landing_part_decision": "not_decided_here"',
                '"landing_part_decision": "decided_fts"')
    cases.append(("⑮ landing_part_decision 改成 decided_fts ⇒ K5 红",
                  "K5", _rebuild_page(base_page, t)))

    # --- 反向用例 16: 官网原句锚点在正文里被删掉 ⇒ K5 红
    drop_page = base_page.replace("4 Pin, 1 Row, Through Hole", "4 Pin, Through Hole", 1)
    cases.append(("⑯ 官网原句锚点被从正文删掉 ⇒ K5 红", "K5", drop_page))

    npass = 0
    ntotal = len(cases)
    for name, want_red, payload in cases:
        if isinstance(payload, tuple) and payload and payload[0] == "FACTS":
            ctx = payload[1]
        else:
            ctx = collect(page_text=payload, facts=facts)
        results = run_all(ctx)
        reds = [code for code, _d, fails in results if fails]
        if want_red is None:
            ok = not reds
            detail = "全绿 (期望) · 实际红: %s" % (reds or "无")
        else:
            ok = want_red in reds
            detail = "期望 %s 红 · 实际红: %s" % (want_red, reds or "无")
        # 把沙盒副本落盘 (★项目盘内, 供人工复核★)
        if isinstance(payload, str):
            with open(os.path.join(SANDBOX, "case_%02d.md" % (npass + 1)), "w",
                      encoding="utf-8") as fh:
                fh.write(payload)
        print("  [%s] %s" % ("PASS" if ok else "FAIL", name))
        print("        %s" % detail)
        if ok:
            npass += 1
    print("── selftest: %d/%d PASS" % (npass, ntotal))
    if npass == ntotal:
        print("ALL TESTS PASS")
        return 0
    print("SELFTEST FAILED")
    return 1


# =========================================================================
# main
# =========================================================================
def main():
    ap = argparse.ArgumentParser(description="ISS-387 FTS 单排直插原厂 land 几何真相页闸")
    ap.add_argument("--selftest", action="store_true", help="跑自测 (反向用例)")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    ctx = collect()
    results = run_all(ctx)
    nfail = report(results, "ISS-387 FTS 单排直插 land 真相页闸")
    if nfail:
        print("❌ 有 %d 条判据红" % nfail)
        return 1
    print("✅ 全绿")
    return 0


if __name__ == "__main__":
    sys.exit(main())
