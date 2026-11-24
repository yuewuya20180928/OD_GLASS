#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_seat_part_verdict_propagation.py  ·  ISS-394 闸 K0~K6
「一条结论被推翻后, 它的活副本必须被点名并被改掉」—— 传播自守闸

用法:
    python3 HW/check_seat_part_verdict_propagation.py             # 正向跑 (★现状 K1/K2/K3 红 = 预期★)
    python3 HW/check_seat_part_verdict_propagation.py --selftest  # 自测, 末行 ALL TESTS PASS
    python3 HW/check_seat_part_verdict_propagation.py --emit      # 打印真相页机器块 (json, 可解析)

★纪律:
  · fail-closed —— 任一条不满足 ⇒ 该条红 ⇒ 整体 rc=1
  · 每条闸至少一条反向用例 (--selftest 里把入参改坏 ⇒ 必须判红, 且只红那一条)
  · ★零写板 · 零落表 · 零挂链 · 零改既有闸 · 零改既有页面正文 · 只读 (本闸只读盘 + 自写沙盒 tmp/iss394_sbx/)
  · ★本闸【不许挂进 state/gate_check.py】(挂链是 main 的地界) ⇒ 只交脚本 + 路径 + 建议
  · ★本闸【只读既有件】—— 那 3 个闸和那 3 个页都是已签收件 ⇒ 一个字都不许改 ⇒ 本闸只读它们

★本闸要判的是什么 (★一句话★):
  一条选型结论 (FTSH-104-01-F-DV / FTSH-102-01-F-DV) 已被官网单品页推翻, 但推翻只写在
  state/issue_log.yaml 的 note_addendum 里 ⇒ 活页面 / 分片 / 已签收闸源码 仍在说旧话 ⇒
  「板只改一次」那一趟的读数面是错的 ⇒ 本闸把「活副本必须被点名并被改掉」变成机器可判。

闸定义 (★口径照抄真相页 §1 / §2 / §4 / §6★):
  K0  板三项 + 三张表指纹未动 (md5 / mtime / size 都要比)
  K1  ★命门★ 被推翻的料号【不许再以「首选 / 板侧真值档」身份活在任何活副本里】
      ⇒ 扫白名单扫描面 (真相页 / 型号真相页 / hw.yaml / 已签收闸源码) ⇒ 逐行判
      ⇒ ★记账语境 (行内有证伪标记) 与【当首选语境】必须能分开 —— 否则本单自己的记账页会把自己打成红
      ⇒ 附: 台账 (机器块 live_copies) 指向的 file+line 必须真的存在
  K2  任何【已闭】的 need, 其答案不许指向被推翻的料号 (扫 hw.yaml 的 answers 段)
  K3  任何【未答】的 need, 它的选项里必须至少有一个【满足板侧真值档】的选项
      (扫 hw.yaml 的 needs_from 段 · to=main · 无 answers)
      ⇒ ★现状【必然红】: 那条 need 的三个选项没有一个满足 1×4/1×2 · 单排 · 直插
      ⇒ ⇒ 这是【本单要暴露的现状】, 不是闸故障 ⇒ 不许为了让它绿而放宽判据
  K4  正确结论必须被登记 (且带证据等级) + 全部裁决字段 = not_decided_here (不许代拍)
  K5  证据分级白名单 + 零挂起措辞 + 零挂链 + 判据句与事实句分开
  K6  既有件零扰动自证 (6 件已签收件的 md5 与机器块 protected_files 同) + 机器块三字段 none

★沙盒纪律 (★本机已踩过的坑★):
  沙盒一律落【项目盘】tmp/iss394_sbx/, 路径从本闸自己的 ROOT 推, 不许依赖系统 /tmp 的深度。
"""

import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import sys

try:
    import yaml
except Exception:  # noqa: BLE001
    yaml = None

# ---------------------------------------------------------------------------
# 路径 (★全部从本闸自己的位置推 ⇒ 与 cwd 无关★)
# ---------------------------------------------------------------------------
PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(PROJ, "HW", "PCB", "BOARD_ONEPASS_SEAT_PART_VERDICT_PROPAGATION.md")
PART_TRUTH = os.path.join(PROJ, "HW", "PCB", "BOARD_ONEPASS_DEBUG_UART_SEAT_PART_TRUTH.md")
HW_FRAG = os.path.join(PROJ, "state", "fragments", "hw.yaml")
ALIGN_GATE = os.path.join(PROJ, "HW", "check_debug_uart_seat_alignment.py")
BOARD = os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb")
NETLIST = os.path.join(PROJ, "HW", "netlist_v1.csv")
PINS = os.path.join(PROJ, "HW", "netlist_v1_pins.csv")
BOM = os.path.join(PROJ, "HW", "BOM_v1.csv")
GATE_CHECK = os.path.join(PROJ, "state", "gate_check.py")
SANDBOX = os.path.join(PROJ, "tmp", "iss394_sbx")

# ---------------------------------------------------------------------------
# 基线指纹 (★与 main 2026-11-24 14:5x 本机实跑基线同★)
# ---------------------------------------------------------------------------
EXP_BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"
EXP_BOARD_SIZE = 4940213
EXP_BOARD_MTIME = "2026-11-06 07:07:17.362193"
EXP_NETLIST_MD5 = "6aee500e60ba0732f83a9cf557ba90ab"
EXP_PINS_MD5 = "9174309df1ec9411ac8e8d9e80ee386a"
EXP_BOM_MD5 = "5b9993992405904a60ac96a020b375d8"
GATE_NAME = "check_seat_part_verdict_propagation"

# ---------------------------------------------------------------------------
# 词表
# ---------------------------------------------------------------------------
GRADES = ("[官网]", "[媒体]", "[实测]", "[推算]", "[0数据]")
ZERO_DATA = "[0数据]"
EVIDENCE_LABELS = ("官网", "媒体", "实测", "推算", "0数据", "0 数据", "官方")

# 被推翻的料号 (★truth 真相页 §1 · 本机实抓官网单品页标题逐字核对过★)
REFUTED_PARTS = ("FTSH-104-01-F-DV", "FTSH-102-01-F-DV")

# ★断言标记 (★当首选语境★): 行里出现这些 ⇒ 该行在【主张】这颗料号可用
ASSERT_MARKERS = (
    "首选", "唯一同时满足", "推荐", "落表件", "建议采用", "应当采用",
    "定为", "就选", "选型结论是",
)
# ★口径断言标记: 行里出现这些 ⇒ 该行在【主张】这颗料号满足板侧真值档 (1×4/1×2 · 单排 · 直插)
CALIBER_MARKERS = (
    "1×4", "1×2", "1x4", "1x2", "单排", "直插", "THT", "排针",
)
# ★证伪标记 (★记账语境★): 行里出现这些 ⇒ 该行在【记录/否定】它, 不是在主张它
REFUTE_MARKERS = (
    "推翻", "已证伪", "不得", "不许", "禁", "作废", "错三格", "全错",
    "不可直接落表", "refuted", "证伪", "已被推翻", "已推翻", "不是单排",
    "双排贴片", "不得当", "已被证伪", "非单排",
)

# 零挂起措辞 (K5)
HANG_STRONG = (
    "等原厂回信", "等原厂确认", "待外部确认", "等外部确认",
    "等回复", "pending reply", "awaiting reply",
    "等官网恢复", "等厂商确认", "待厂商", "等厂家", "原厂回信后",
    "等原厂", "待原厂",
)
HANG_WEAK = ("待确认", "悬置", "挂起", "等确认", "未答复", "待复")
NEGATION_MARKS = (
    "不许", "不得", "禁", "不写", "不挂起", "零挂起", "不是", "没有",
    "≠", "而不是", "已消除", "零等待", "不靠", "不依赖", "不许外发",
    "不再外发", "查不到就写",
)
STATUS_OF_FACT_MARKS = ("现盘上", "盘上", "现状", "当前", "目前", "仍「", "行 71", "行 77")

# 判据句 / 事实句分开 (K5)
VERDICT_WORDS = ("应采用", "已决定", "已拍", "裁决", "应该采用", "选定", "拍板")

# 厂商料号形态 (★用于 K3 从 need 文本里抽候选料号★)
# ★Samtec 形态: PREFIX-POS-LEAD-PLATING-ROW (例 FTSH-104-01-F-DV / FTS-104-01-F-S) ⇒ 4 段★
# ★Würth 形态: 11 位纯数字 (例 61300411121) ⇒ 另收★
PART_RE = re.compile(
    r"\b(?:[A-Z]{2,6}-[0-9]{2,4}-[0-9]{2}-[A-Z]-[A-Z0-9]{1,3}|[0-9]{11})\b")
# 板侧真值档关键词 (★K3 的文本级兜底判据★)
CALIBER_TEXT = ("单排", "直插", "1×4", "1×2", "1x4", "1x2")

CN_TZ = datetime.timezone(datetime.timedelta(hours=8))


# =========================================================================
# 工具
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


def prose_only(page):
    """去掉 ```json 机器块, 只留正文 —— 机器块里的 quote 字段是【逐字引用的原文】,
    那是记账不是主张 ⇒ 不许拿它去判「当首选」。"""
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


def parse_machine_block(page_text):
    """从真相页里抽出 §6.2 的 json 机器块。返回 (dict, err)。"""
    blocks = re.findall(r"```json\s*\n(.*?)\n```", page_text, re.S)
    if not blocks:
        return None, "真相页里找不到 ```json 机器块"
    parsed = []
    for b in blocks:
        try:
            parsed.append(json.loads(b))
        except Exception:  # noqa: BLE001
            continue
    if not parsed:
        return None, "机器块 json.loads 解析失败 (共 %d 个 json 块)" % len(blocks)
    for d in parsed:
        if isinstance(d, dict) and str(d.get("schema", "")) == "hw.seat_part.verdict_propagation":
            return d, ""
    return parsed[-1], ""


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


# =========================================================================
# ★K1 的核心: 逐行判【记账语境】 vs 【当首选语境】★
# =========================================================================
def line_verdict(line):
    """返回 (is_violation, reasons)。"""
    if not any(p in line for p in REFUTED_PARTS):
        return False, []
    has_assert = any(m in line for m in ASSERT_MARKERS)
    has_caliber = any(m in line for m in CALIBER_MARKERS)
    if not (has_assert or has_caliber):
        return False, []          # 只是提到这颗料号, 没主张它 ⇒ 不是违规
    if any(m in line for m in REFUTE_MARKERS):
        return False, ["exempt:含证伪标记 (记账语境)"]
    return True, ["断言标记=%s 口径标记=%s 无证伪标记" % (has_assert, has_caliber)]


def scan_assertions(text):
    """扫一段文本, 返回 [(行号, 该行截断, 原因列表)]。"""
    out = []
    for i, line in enumerate(text.split("\n"), 1):
        bad, why = line_verdict(line)
        if bad:
            out.append((i, line.strip()[:150], why))
    return out


def collect(page_text=None, part_truth_text=None, frag_text=None,
            align_text=None, facts=None):
    """把闸要用的全部入参收成 dict —— 自测时逐项替换即可制造反向用例。"""
    ctx = {}
    ctx["page"] = read_text(PAGE) if page_text is None else page_text
    ctx["page_exists"] = os.path.exists(PAGE) or page_text is not None
    ctx["part_truth"] = read_text(PART_TRUTH) if part_truth_text is None else part_truth_text
    ctx["frag"] = read_text(HW_FRAG) if frag_text is None else frag_text
    ctx["align"] = read_text(ALIGN_GATE) if align_text is None else align_text
    if facts is None:
        facts = {
            "board_md5": md5_of(BOARD),
            "board_size": os.path.getsize(BOARD),
            "board_mtime": mtime_iso(BOARD),
            "netlist_md5": md5_of(NETLIST),
            "pins_md5": md5_of(PINS),
            "bom_md5": md5_of(BOM),
            "chain_hits": count_chain_hits(),
            "protected_md5": {},
        }
    ctx["facts"] = facts
    mb, err = parse_machine_block(ctx["page"])
    ctx["mb"] = mb
    ctx["mb_error"] = err
    return ctx


# =========================================================================
# K0  板三项 + 三张表指纹未动
# =========================================================================
def k0(ctx):
    fails = []
    f = ctx["facts"]
    if f.get("board_md5") != EXP_BOARD_MD5:
        fails.append("K0 板 md5 = %r ≠ 基线 %s ⇒ 写板了"
                     % (f.get("board_md5"), EXP_BOARD_MD5))
    if f.get("board_size") != EXP_BOARD_SIZE:
        fails.append("K0 板 size = %r ≠ 基线 %d" % (f.get("board_size"), EXP_BOARD_SIZE))
    if f.get("board_mtime") != EXP_BOARD_MTIME:
        fails.append("K0 板 mtime = %r ≠ 基线 %s" % (f.get("board_mtime"), EXP_BOARD_MTIME))
    for key, exp, name in (
            ("netlist_md5", EXP_NETLIST_MD5, "HW/netlist_v1.csv"),
            ("pins_md5", EXP_PINS_MD5, "HW/netlist_v1_pins.csv"),
            ("bom_md5", EXP_BOM_MD5, "HW/BOM_v1.csv")):
        if f.get(key) != exp:
            fails.append("K0 %s md5 = %r ≠ 基线 %s ⇒ 落表了" % (name, f.get(key), exp))
    return fails


# =========================================================================
# K1  ★命门★ 被推翻的料号不许再以「首选 / 板侧真值档」身份活在活副本里
# =========================================================================
SCAN_SURFACE_KEY = "scan_surface"
# ★必扫面 (★白名单·硬编码在本闸里★): 少扫一个 = 闸自己漏 ⇒ 判红
REQUIRED_SCAN_SURFACE = (
    "HW/PCB/BOARD_ONEPASS_DEBUG_UART_SEAT_PART_TRUTH.md",
    "state/fragments/hw.yaml",
    "HW/check_debug_uart_seat_alignment.py",
    "HW/PCB/BOARD_ONEPASS_SEAT_PART_VERDICT_PROPAGATION.md",
)


def k1(ctx):
    fails = []
    if ctx["mb_error"]:
        return fails
    mb = ctx["mb"]
    surface = mb.get(SCAN_SURFACE_KEY) or []
    if not isinstance(surface, list) or not surface:
        fails.append("K1 机器块缺 `%s` (白名单扫描面) ⇒ 闸不知道该扫哪 ⇒ 判红" % SCAN_SURFACE_KEY)
        return fails
    # ★防漏扫: 扫描面必须与本闸的必扫面完全一致 (少一个 = 漏扫 ⇒ 判红)★
    missing = [x for x in REQUIRED_SCAN_SURFACE if x not in surface]
    extra = [x for x in surface if x not in REQUIRED_SCAN_SURFACE]
    if missing:
        fails.append("K1 ★命门★ 扫描面少了 %s ⇒ 闸会漏扫 ⇒ 判红 (★必扫面 = %s★)"
                     % (missing, list(REQUIRED_SCAN_SURFACE)))
    if extra:
        fails.append("K1 扫描面多了 %s ⇒ 本闸读不了那个文件 ⇒ 判红" % extra)

    # 本单自己登记的活副本 (台账) 与扫描面的一致性
    live = mb.get("live_copies") or []
    for entry in live:
        f = entry.get("file")
        ln = entry.get("line")
        if not isinstance(ln, int) or ln < 1:
            fails.append("K1 台账 live_copies 条目 (file=%r) 的 line = %r 非法 ⇒ "
                         "台账写错 ⇒ 判红" % (f, ln))
            continue
        if not os.path.exists(os.path.join(PROJ, f)):
            fails.append("K1 台账 live_copies 指向的文件不存在: %s (line %s)" % (f, ln))
            continue
        try:
            with open(os.path.join(PROJ, f), "r", encoding="utf-8", errors="replace") as fh:
                lines = fh.read().split("\n")
        except Exception:  # noqa: BLE001
            fails.append("K1 台账 live_copies 指向的文件读不了: %s" % f)
            continue
        if ln > len(lines):
            fails.append("K1 台账 live_copies 指向 %s L%d ⇒ 但那文件只有 %d 行 ⇒ "
                         "台账行号漂移了" % (f, ln, len(lines)))
            continue
        if not any(p in "\n".join(lines) for p in REFUTED_PARTS):
            fails.append("K1 台账 live_copies 指向 %s L%d ⇒ 但那文件里【一个被推翻的料号都没有】"
                         " ⇒ 台账与盘面不一致 (要么盘面被改了, 要么台账写错了)" % (f, ln))

    # 扫描面: 逐个文件扫 (★正文视图 —— 机器块里的 quote 是逐字引用, 属记账★)
    bodies = {
        "HW/PCB/BOARD_ONEPASS_DEBUG_UART_SEAT_PART_TRUTH.md": ctx["part_truth"],
        "state/fragments/hw.yaml": ctx["frag"],
        "HW/check_debug_uart_seat_alignment.py": ctx["align"],
        "HW/PCB/BOARD_ONEPASS_SEAT_PART_VERDICT_PROPAGATION.md": ctx["page"],
    }
    for f in surface:
        if f not in bodies:
            fails.append("K1 扫描面 %s 不在本闸的读取清单里 ⇒ 要么改扫描面, 要么改闸 ⇒ 判红" % f)
            continue
        text = prose_only(bodies[f])
        for ln, snippet, why in scan_assertions(text):
            fails.append("K1 ★命门★ %s L%d 仍以【首选 / 板侧真值档】的身份主张被推翻的料号 "
                         "⇒ 判红 (%s) | %s" % (f, ln, "; ".join(why), snippet))
    return fails


# =========================================================================
# K2  任何【已闭】的 need, 其答案不许指向被推翻的料号
# =========================================================================
def k2(ctx):
    fails = []
    if yaml is None:
        return ["K2 本机没有 PyYAML ⇒ 判红 (fail-closed)"]
    try:
        data = yaml.safe_load(ctx["frag"])
    except Exception as exc:  # noqa: BLE001
        return ["K2 state/fragments/hw.yaml 解析失败 ⇒ 判红: %s" % exc]
    if not isinstance(data, dict):
        return ["K2 state/fragments/hw.yaml 顶层不是 dict ⇒ 判红"]
    answers = data.get("answers") or []
    for a in answers:
        if not isinstance(a, dict):
            continue
        key = a.get("key")
        txt = " ".join(str(a.get(f) or "") for f in ("value", "note", "ref"))
        if not any(p in txt for p in REFUTED_PARTS):
            continue
        has_assert = any(m in txt for m in ASSERT_MARKERS)
        has_caliber = any(m in txt for m in CALIBER_MARKERS)
        has_refute = any(m in txt for m in REFUTE_MARKERS)
        if (has_assert or has_caliber) and not has_refute:
            fails.append("K2 ★命门★ 已闭答案 key=%r 仍指向被推翻的料号且把它当首选/真值档 ⇒ "
                         "判红 (★已决且决错比未决更危险★) | %s"
                         % (key, txt.strip()[:160]))
    return fails


# =========================================================================
# K3  任何【未答】的 need, 它的选项里必须至少有一个满足板侧真值档的选项
# =========================================================================
def correct_parts_of(ctx):
    if ctx["mb_error"]:
        return []
    cp = ctx["mb"].get("correct_parts")
    return [str(x) for x in cp] if isinstance(cp, list) else []


def k3(ctx):
    fails = []
    if yaml is None:
        return ["K3 本机没有 PyYAML ⇒ 判红 (fail-closed)"]
    try:
        data = yaml.safe_load(ctx["frag"])
    except Exception as exc:  # noqa: BLE001
        return ["K3 state/fragments/hw.yaml 解析失败 ⇒ 判红: %s" % exc]
    if not isinstance(data, dict):
        return ["K3 state/fragments/hw.yaml 顶层不是 dict ⇒ 判红"]
    correct = set(correct_parts_of(ctx))
    needs = data.get("needs_from") or []
    for n in needs:
        if not isinstance(n, dict):
            continue
        if n.get("to") != "main":
            continue
        if n.get("answers"):          # 已答 ⇒ 不是本判据的对象
            continue
        item = str(n.get("item") or "")
        if "J_DEBUG" not in item and "J_UART" not in item:
            continue
        cands = sorted(set(PART_RE.findall(item)))
        if not cands:
            continue                # ★没列候选料号 ⇒ 不属于「列出来的候选全错」那一类★
        text_ok = all(t in item for t in ("单排", "直插")) or \
            ("单排" in item and "直插" in item)
        good = []
        for c in cands:
            if c in correct:
                good.append(c)
            elif c not in REFUTED_PARTS and text_ok:
                good.append(c)
        if not good:
            fails.append(
                "K3 ★命门★ 未答 need key=%r 的选项里【没有一个满足板侧真值档 (1×4/1×2 · 单排 · 直插)】"
                " ⇒ 判红 (★这条 need 现在只能被答错★) | 候选=%s" % (n.get("key"), cands))
    return fails


# =========================================================================
# K4  正确结论必须被登记 (且带证据等级) + 全部裁决字段 = not_decided_here
# =========================================================================
REQUIRED_CORRECT = ("FTS-104-01-F-S", "FTS-102-01-F-S")
REQUIRED_TOP_KEYS = (
    "schema", "issue", "agent", "updated", "truth_doc",
    "refuted_parts", "refuted_reason", "correct_parts", "correct_parts_evidence",
    "live_copies", "closed_need_key", "unanswered_need_key",
    "board_md5", "netlist_md5", "pins_md5", "bom_md5",
    "evidence_grades", "degradation_plan", "not_decided_here",
    "protected_files", "scan_surface", "board_write", "table_write",
    "existing_gates_touched", "existing_pages_touched", "chain_hits", "outbound",
)


def k4(ctx):
    fails = []
    if ctx["mb_error"]:
        return ["K4 %s" % ctx["mb_error"]]
    mb = ctx["mb"]
    if not isinstance(mb, dict):
        return ["K4 机器块不是 dict"]
    for key in REQUIRED_TOP_KEYS:
        if key not in mb:
            fails.append("K4 机器块缺顶层字段 `%s`" % key)
    cp = [str(x) for x in (mb.get("correct_parts") or [])]
    for p in REQUIRED_CORRECT:
        if p not in cp:
            fails.append("K4 ★命门★ 机器块 correct_parts 缺正确料号 `%s` ⇒ "
                         "正确结论没被登记 ⇒ 判红" % p)
    ev = mb.get("correct_parts_evidence") or {}
    for p in REQUIRED_CORRECT:
        spec = ev.get(p)
        if not isinstance(spec, str) or not spec.strip():
            fails.append("K4 `%s` 没有证据登记 (correct_parts_evidence 缺或为空)" % p)
            continue
        if not any(g in spec for g in GRADES):
            fails.append("K4 `%s` 的证据登记里没有五级白名单中的证据等级 ⇒ %s" % (p, list(GRADES)))
    rp = [str(x) for x in (mb.get("refuted_parts") or [])]
    for p in REFUTED_PARTS:
        if p not in rp:
            fails.append("K4 机器块 refuted_parts 缺被推翻料号 `%s`" % p)
    if mb.get("not_decided_here") != "not_decided_here":
        fails.append("K4 not_decided_here = %r (应 'not_decided_here') ⇒ 本单不许代拍"
                     % mb.get("not_decided_here"))
    decisions = mb.get("decisions")
    if not isinstance(decisions, dict) or not decisions:
        fails.append("K4 机器块缺 `decisions` 段 (★每条裁决字段都要写成 not_decided_here★)")
    else:
        for k, v in decisions.items():
            if v != "not_decided_here":
                fails.append("K4 ★命门★ decisions.%s = %r ≠ 'not_decided_here' ⇒ "
                             "本单代拍了 ⇒ 判红" % (k, v))
    for bad in ("selected_part", "chosen_part", "landed_part", "decision"):
        if bad in mb and mb.get(bad) != "not_decided_here":
            fails.append("K4 机器块顶层 `%s` = %r ≠ 'not_decided_here' ⇒ 本单代拍了"
                         % (bad, mb.get(bad)))
    return fails


# =========================================================================
# K5  证据等级 + 零挂起 + 零挂链 + 判据句与事实句分开
# =========================================================================
def k5(ctx):
    fails = []
    if ctx["mb_error"]:
        return fails
    mb = ctx["mb"]
    page = ctx["page"]

    # 5-1 证据分级白名单 (★只查白名单内的标签, 别的一律不认★)
    for p in REQUIRED_CORRECT:
        spec = (mb.get("correct_parts_evidence") or {}).get(p)
        if not isinstance(spec, str):
            continue
        for g in GRADES:
            if g in spec:
                break
        else:
            fails.append("K5 `%s` 的证据登记没有白名单等级" % p)
    found = [g for g in GRADES if g in page]
    if len(found) < 3:
        fails.append("K5 真相页里出现的证据等级只有 %d 种 (%s) ⇒ 至少要 3 种"
                     % (len(found), found))
    # 页面上出现的所有 [xxx] 标签, 若像证据等级就必须在白名单里
    for tag in set(re.findall(r"\[[^\[\]]{1,8}\]", page)):
        if tag in GRADES:
            continue
        if tag.strip("[]") in EVIDENCE_LABELS:
            fails.append("K5 证据等级标签 `%s` 不在白名单 %s" % (tag, list(GRADES)))

    # 5-2 零挂起措辞 (强挂起词 = 全页扫; 弱挂起词 = 本单自身产出面扫)
    for i, ln in enumerate(page.split("\n"), 1):
        for h in HANG_STRONG:
            if h in ln and not any(m in ln for m in NEGATION_MARKS):
                fails.append("K5 第 %d 行出现挂起措辞 `%s` ⇒ 零挂起判红" % (i, h))
    own_out = "\n".join([
        sec_body(page, "## §3"),
        sec_body(page, "## §4"),
        sec_body(page, "## §5"),
        sec_body(page, "## §6"),
        json.dumps(mb, ensure_ascii=False),
    ])
    for i, ln in enumerate(own_out.split("\n"), 1):
        if any(m in ln for m in STATUS_OF_FACT_MARKS):
            continue
        for h in HANG_WEAK:
            if h in ln and not any(m in ln for m in NEGATION_MARKS):
                fails.append("K5 本单产出面 (§3~§6 / 机器块) 第 %d 行出现挂起措辞 `%s` ⇒ 零挂起判红"
                             % (i, h))

    # 5-3 零挂链
    if ctx["facts"].get("chain_hits") != 0:
        fails.append("K5 state/gate_check.py 里命中本闸 %r 次 (应 0) ⇒ 挂链了 (挂链是 main 的地界)"
                     % ctx["facts"].get("chain_hits"))
    if mb.get("chain_hits") not in (0, "0", "none"):
        fails.append("K5 机器块 chain_hits = %r (应 0 / none)" % mb.get("chain_hits"))

    # 5-4 判据句与事实句分开
    # (甲) 事实字段里不许混进裁决语
    for p, spec in (mb.get("correct_parts_evidence") or {}).items():
        if isinstance(spec, str):
            for w in VERDICT_WORDS:
                if w in spec:
                    fails.append("K5 ★`correct_parts_evidence.%s` 事实字段里混进裁决语 `%s` ⇒ "
                                 "判据句与事实句混成一句" % (p, w))
    if isinstance(mb.get("refuted_reason"), str):
        for w in VERDICT_WORDS:
            if w in mb["refuted_reason"]:
                fails.append("K5 `refuted_reason` 事实字段里混进裁决语 `%s`" % w)
    # (乙) 官网原句锚点必须在正文里出现 (不许只在机器块里自说自话)
    body = prose_only(page)
    for p in REQUIRED_CORRECT:
        spec = (mb.get("correct_parts_evidence") or {}).get(p)
        if not isinstance(spec, str):
            continue
        m = re.search(r"['\"]([^'\"]{12,})['\"]", spec)
        if not m:
            continue
        anchor = m.group(1)
        if anchor not in body:
            fails.append("K5 `%s` 的官网原句锚点 `%s` 在真相页正文里找不到 ⇒ "
                         "事实句没有原文背书" % (p, anchor))
    # (丙) 判据句必须落在 §4 / §5, 不许混进 §1 / §2 / §3 的事实抄录节
    s4 = sec_body(page, "## §4")
    s5 = sec_body(page, "## §5")
    if "判据" not in (s4 + s5):
        fails.append("K5 §4/§5 里没有「判据」字样 ⇒ 判据句没单独落地")
    for name, sec in (("§1", sec_body(page, "## §1", "## §2")),
                      ("§2", sec_body(page, "## §2", "## §3")),
                      ("§3", sec_body(page, "## §3", "## §4"))):
        if "判据" in sec:
            fails.append("K5 判据句混进了 %s 事实抄录节 ⇒ 判据句与事实句混成一句" % name)
    return fails


# =========================================================================
# K6  既有件零扰动自证
# =========================================================================
def k6(ctx):
    fails = []
    if ctx["mb_error"]:
        return fails
    mb = ctx["mb"]
    live = ctx["facts"].get("protected_md5") or {}
    pf = mb.get("protected_files") or {}
    if not isinstance(pf, dict) or not pf:
        fails.append("K6 机器块缺 `protected_files` (★6 件已签收件的 md5 基线★)")
    else:
        for path, exp in pf.items():
            full = os.path.join(PROJ, path)
            if not os.path.exists(full):
                fails.append("K6 已签收件不在盘: %s" % path)
                continue
            got = live.get(path) or md5_of(full)
            if got != exp:
                fails.append("K6 已签收件 %s md5 = %r ≠ 基线 %r ⇒ 被动了 ⇒ 判红"
                             " (★main 落订正时须在同一批更新机器块里这一项的 md5★)"
                             % (path, got, exp))
    for key in ("board_write", "table_write"):
        if mb.get(key) != "none":
            fails.append("K6 机器块 %s = %r (应 'none')" % (key, mb.get(key)))
    for key in ("existing_gates_touched", "existing_pages_touched"):
        if mb.get(key) != "none":
            fails.append("K6 机器块 %s = %r (应 'none')" % (key, mb.get(key)))
    if mb.get("outbound") != "none":
        fails.append("K6 机器块 outbound = %r (应 'none' ⇒ 零外发)" % mb.get("outbound"))
    return fails


# =========================================================================
# 闸编排
# =========================================================================
CHECKS = (
    ("K0", k0, "板三项 + 三张表指纹未动"),
    ("K1", k1, "★命门★ 被推翻的料号不许再以「首选/真值档」身份活在活副本里"),
    ("K2", k2, "★命门★ 已闭 need 的答案不许指向被推翻的料号"),
    ("K3", k3, "★命门★ 未答 need 的选项里必须至少有一个满足板侧真值档"),
    ("K4", k4, "正确结论已登记 + 带证据等级 + 全部 not_decided_here"),
    ("K5", k5, "证据分级 / 零挂起 / 零挂链 / 判据与事实分开"),
    ("K6", k6, "既有件零扰动 + 机器块三字段 none"),
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
# 自测 (★沙盒落项目盘 tmp/iss394_sbx/ ⇒ 与系统 /tmp 无关★)
# =========================================================================
def _synth_corrected_frag(correct_parts=("FTS-104-01-F-S", "FTS-102-01-F-S"),
                           answered_keys=()):
    """造一份【已订正】的 hw.yaml 文本 (★K2/K3 的自测底座★):
    - 一条已闭答案, 值里写正确料号 (⇒ K2 绿)
    - 一条未答 need, 选项里含正确料号 (⇒ K3 绿)
    """
    need_item = ("板那一趟的 BOM 型号栏: J_DEBUG/J_UART 按板侧真值档 "
                 "(%s / %s) 还是别的档?" % (correct_parts[0], correct_parts[1]))
    ans_val = ("OI-10 已闭: J_DEBUG 首选 Samtec %s (1×4 1.27mm 单排直插), "
               "J_UART 首选 Samtec %s (1×2 1.27mm 单排直插)" % correct_parts)
    lines = [
        "agent: hw-lead",
        "answers:",
        "- key: iss377_oi10_vendor_part_numbers",
        "  to: main",
        "  value: '%s'" % ans_val,
        "  ref: HW/PCB/BOARD_ONEPASS_DEBUG_UART_SEAT_PART_TRUTH.md",
        "needs_from:",
        "- key: iss380_board_trip_bom_part_fill",
        "  to: main",
        "  item: '%s'" % need_item,
        "  since: '2026-11-24'",
    ]
    return "\n".join(lines) + "\n"


def _synth_asserting_frag():
    """造一份【仍在说旧话】的 hw.yaml 文本 (★(乙)(丙) 的病灶★)。"""
    return (
        "agent: hw-lead\n"
        "answers:\n"
        "- key: iss377_oi10_vendor_part_numbers\n"
        "  to: main\n"
        "  value: 'OI-10 已闭: J_DEBUG 首选 Samtec FTSH-104-01-F-DV (1×4 1.27mm 直插), "
        "J_UART 首选 Samtec FTSH-102-01-F-DV (1×2 1.27mm 直插)'\n"
        "  ref: HW/PCB/BOARD_ONEPASS_DEBUG_UART_SEAT_PART_TRUTH.md\n"
        "needs_from:\n"
        "- key: iss380_board_trip_bom_part_fill\n"
        "  to: main\n"
        "  item: '板那一趟的 BOM 型号栏: J_DEBUG/J_UART 按板侧真值档 "
        "(FTSH-104-01-F-DV / FTSH-102-01-F-DV) 还是 Cortex-10 2×5 档 (FTSH-105-01-L-DV-K)?'\n"
        "  since: '2026-11-24'\n"
    )


def _synth_clean_page_part_truth():
    """造一份【已订正】的型号真相页文本 (★(甲) 已订正的形态★)。"""
    return (
        "# 型号真相页 (沙盒合成件)\n"
        "| D-1 | **Samtec** | **`FTSH-104-01-F-DV`** | ... | ★**已被推翻 (ISS-394 §1) ⇒ "
        "不得当落表件** | ... |\n"
        "| U-1 | **Samtec** | **`FTSH-102-01-F-DV`** | ... | ★**已被推翻 ⇒ 不得当落表件** | ... |\n"
    )


def _synth_clean_align():
    """造一份【已订正】的已签收闸源码文本 (★(丁) 已订正的形态★)。"""
    return (
        "    bom = base[\"bom\"].replace(\n"
        "        \"J_DEBUG,1,1×4 1.27mm 排针 (JTAG),CONN,必装,镜脚主 PCB,P8,[推算],,待定,\",\n"
        "        \"J_DEBUG,1,1×4 1.27mm 排针 (JTAG),CONN,必装,镜脚主 PCB,P8,[推算],,Samtec FTS-104-01-F-S,\")\n"
    )


def _synth_asserting_align():
    return (
        "    bom = base[\"bom\"].replace(\n"
        "        \"J_DEBUG,1,1×4 1.27mm 排针 (JTAG),CONN,必装,镜脚主 PCB,P8,[推算],,待定,\",\n"
        "        \"J_DEBUG,1,1×4 1.27mm 排针 (JTAG),CONN,必装,镜脚主 PCB,P8,[推算],,Samtec FTSH-104-01-F-DV,\")\n"
    )


def _synth_asserting_part_truth():
    return (
        "# 型号真相页 (沙盒合成件)\n"
        "| D-1 | **Samtec** | **`FTSH-104-01-F-DV`** | https://www.samtec.com/products/ftsh | "
        "1.27 mm 直插 THT | ★**排距 ✓ 脚数 ✓ · 直插 ✓** ⇒ ★**首选候选** | ... |\n"
        "| U-1 | **Samtec** | **`FTSH-102-01-F-DV`** | ... | 1.27 mm 直插 THT | "
        "★**首选候选** | ... |\n"
    )


def selftest():
    os.makedirs(SANDBOX, exist_ok=True)
    base_page = read_text(PAGE)
    base_mb, err = parse_machine_block(base_page)
    if err:
        print("SELFTEST ABORT: %s" % err)
        return 1
    facts = collect()["facts"]
    cases = []          # (用例名, 期望红的那一条, ctx)

    # ---------------- 底座: 全部外部文件都换成【已订正】的合成件 ----------------
    clean_frag = _synth_corrected_frag()
    clean_part = _synth_clean_page_part_truth()
    clean_align = _synth_clean_align()
    clean_ctx = collect(page_text=base_page, part_truth_text=clean_part,
                        frag_text=clean_frag, align_text=clean_align, facts=facts)

    # --- 反向用例 1: (甲) 型号真相页被改成仍在说旧话 ⇒ K1 红 ---
    ctx1 = collect(page_text=base_page, part_truth_text=_synth_asserting_part_truth(),
                   frag_text=clean_frag, align_text=clean_align, facts=facts)
    cases.append(("① (甲) 型号真相页回到「首选候选」⇒ K1 红", "K1", ctx1, None,
                  ["K0", "K2", "K3", "K4", "K5", "K6"]))

    # --- 反向用例 2: (丁) 已签收闸源码里的硬编码样本回到被推翻料号 ⇒ K1 红 ---
    ctx2 = collect(page_text=base_page, part_truth_text=clean_part,
                   frag_text=clean_frag, align_text=_synth_asserting_align(), facts=facts)
    cases.append(("② (丁) 已签收闸源码硬编码样本回到被推翻料号 ⇒ K1 红", "K1", ctx2, None,
                  ["K0", "K2", "K3", "K4", "K5", "K6"]))

    # --- 反向用例 3: (乙)(戊) 分片的已闭答案回到「首选」⇒ K1 红 + K2 红 ---
    bad_frag = _synth_asserting_frag()
    ctx3 = collect(page_text=base_page, part_truth_text=clean_part,
                   frag_text=bad_frag, align_text=clean_align, facts=facts)
    cases.append(("③ (乙)(戊) 已闭答案回到「首选被推翻料号」⇒ K1+K2 红 (★K1 与 K2 读同一份文本 ⇒ 同源共红★)",
                  "K2", ctx3, None, ["K0", "K4", "K5", "K6"]))

    # --- 反向用例 4: K3 专属 —— 未答 need 的选项全错 ⇒ K3 红 ---
    frag_k3 = _synth_corrected_frag().replace(
        "(FTS-104-01-F-S / FTS-102-01-F-S)",
        "(FTSH-104-01-F-DV / FTSH-102-01-F-DV)")
    ctx4 = collect(page_text=base_page, part_truth_text=clean_part,
                   frag_text=frag_k3, align_text=clean_align, facts=facts)
    cases.append(("④ 未答 need 的选项被换成两个被推翻的料号 ⇒ K3 红", "K3", ctx4, None,
                  ["K0", "K1", "K2", "K4", "K5", "K6"]))

    # --- 反向用例 5: ★K1 自指陷阱★ 把匹配式放宽成「出现 FTSH 就红」必须被抓住 ---
    #   做法: 造一份【纯记账】的片段 (行内有证伪标记) 塞进扫描面 ⇒
    #   正确的匹配式 ⇒ 不红; 放宽成「出现就红」的匹配式 ⇒ 会红
    ledger_only = ("# 沙盒合成件\n"
                   "| D-1 | Samtec | `FTSH-104-01-F-DV` | ★**已被推翻 (ISS-394 §1) ⇒ "
                   "不得当落表件** | ✔ |\n")
    ctx5 = collect(page_text=base_page, part_truth_text=ledger_only,
                   frag_text=clean_frag, align_text=clean_align, facts=facts)
    cases.append(("⑤ K1 宽匹配陷阱: 纯记账语境的片段必须【不红】(★放成「出现 FTSH 就红」会被这条抓住★)",
                  None, ctx5, "K1"))

    # --- 反向用例 6: ★K1 反向陷阱★ 本单真相页里塞一句【纯断言】必须被抓 ---
    inject = ("\n★**故意注入的断言行**: `FTSH-104-01-F-DV` 是 J_DEBUG 的首选候选, 1×4 单排直插。\n")
    ctx6 = collect(page_text=base_page + inject, part_truth_text=clean_part,
                   frag_text=clean_frag, align_text=clean_align, facts=facts)
    cases.append(("⑥ K1 反向陷阱: 本单记账页里塞一句纯断言必须被抓住 ⇒ K1 红", "K1", ctx6, None,
                  ["K0", "K2", "K3", "K4", "K5", "K6"]))

    # --- 反向用例 7: 板 md5 被动过 ⇒ K0 红 ---
    bad_facts = dict(facts)
    bad_facts["board_md5"] = "00000000000000000000000000000000"
    ctx7 = collect(page_text=base_page, part_truth_text=clean_part,
                   frag_text=clean_frag, align_text=clean_align, facts=bad_facts)
    cases.append(("⑦ 板 md5 被动过 ⇒ K0 红", "K0", ctx7, None,
                  ["K1", "K2", "K3", "K4", "K5", "K6"]))

    # --- 反向用例 8: BOM 被落表 ⇒ K0 红 ---
    bad_facts = dict(facts)
    bad_facts["bom_md5"] = "11111111111111111111111111111111"
    ctx8 = collect(page_text=base_page, part_truth_text=clean_part,
                   frag_text=clean_frag, align_text=clean_align, facts=bad_facts)
    cases.append(("⑧ BOM 被落表 ⇒ K0 红", "K0", ctx8, None,
                  ["K1", "K2", "K3", "K4", "K5", "K6"]))

    # --- 反向用例 9: 机器块 correct_parts 缺正确料号 ⇒ K4 红 ---
    mb9 = json.loads(json.dumps(base_mb))
    mb9["correct_parts"] = [p for p in mb9.get("correct_parts", []) if p != "FTS-102-01-F-S"]
    page9 = base_page.replace(
        '"correct_parts": [\n  "FTS-104-01-F-S",\n  "FTS-102-01-F-S"\n ],',
        '"correct_parts": [\n  "FTS-104-01-F-S"\n ],')
    if page9 == base_page:
        page9 = _replace_json_key(base_page, "correct_parts", ["FTS-104-01-F-S"])
    ctx9 = collect(page_text=page9, part_truth_text=clean_part,
                   frag_text=clean_frag, align_text=clean_align, facts=facts)
    cases.append(("⑨ 机器块 correct_parts 缺正确料号 ⇒ K4 红", "K4", ctx9, None,
                  ["K0", "K1", "K2", "K3", "K5", "K6"]))

    # --- 反向用例 10: decisions 里有字段不是 not_decided_here ⇒ K4 红 ---
    mb10 = json.loads(json.dumps(base_mb))
    mb10.setdefault("decisions", {})["selected_part"] = "FTS-104-01-F-S"
    page10 = _replace_json_key(base_page, "decisions", mb10["decisions"])
    ctx10 = collect(page_text=page10, part_truth_text=clean_part,
                    frag_text=clean_frag, align_text=clean_align, facts=facts)
    cases.append(("⑩ decisions 里有一项不是 not_decided_here ⇒ K4 红", "K4", ctx10, None,
                  ["K0", "K1", "K2", "K3", "K5", "K6"]))

    # --- 反向用例 11: 机器块里混入挂起措辞 ⇒ K5 红 ---
    page11 = base_page.replace(
        "## §5 复跑命令 (★原样可粘贴★)", "## §5 复跑命令 (★原样可粘贴★)\n等原厂回信后再补")
    if page11 == base_page:
        raise AssertionError("自测用例 11 前提不成立: 找不到 §5 标题")
    ctx11 = collect(page_text=page11, part_truth_text=clean_part,
                    frag_text=clean_frag, align_text=clean_align, facts=facts)
    cases.append(("⑪ §5 里塞一句「等原厂回信」⇒ K5 红", "K5", ctx11, [], ["K0", "K1", "K2", "K3", "K4", "K6"]))

    # --- 反向用例 12: 挂链计数非 0 ⇒ K5 红 ---
    bad_facts = dict(facts)
    bad_facts["chain_hits"] = 1
    ctx12 = collect(page_text=base_page, part_truth_text=clean_part,
                    frag_text=clean_frag, align_text=clean_align, facts=bad_facts)
    cases.append(("⑫ state/gate_check.py 命中本闸 1 次 ⇒ K5 红", "K5", ctx12, None,
                  ["K0", "K1", "K2", "K3", "K4", "K6"]))

    # --- 反向用例 13: 已签收件 md5 与基线不同 ⇒ K6 红 ---
    bad_facts = dict(facts)
    bad_facts["protected_md5"] = {"HW/check_debug_uart_seat_alignment.py": "deadbeef"}
    ctx13 = collect(page_text=base_page, part_truth_text=clean_part,
                    frag_text=clean_frag, align_text=clean_align, facts=bad_facts)
    cases.append(("⑬ 已签收闸 md5 与基线不同 ⇒ K6 红", "K6", ctx13, None,
                  ["K0", "K1", "K2", "K3", "K4", "K5"]))

    # --- 反向用例 14: 机器块 board_write 被改成 yes ⇒ K6 红 ---
    page14 = _replace_json_key(base_page, "board_write", "yes")
    ctx14 = collect(page_text=page14, part_truth_text=clean_part,
                    frag_text=clean_frag, align_text=clean_align, facts=facts)
    cases.append(("⑭ 机器块 board_write 改成 yes ⇒ K6 红", "K6", ctx14, None,
                  ["K0", "K1", "K2", "K3", "K4", "K5"]))

    # --- 反向用例 15: 判据句混进 §1 事实节 ⇒ K5 红 ---
    page15 = base_page.replace(
        "## §1 被推翻的结论是什么 (★附证据等级 + 出处★)",
        "## §1 被推翻的结论是什么 (★附证据等级 + 出处★)\n\n★判据: 该料号不得落表。")
    ctx15 = collect(page_text=page15, part_truth_text=clean_part,
                    frag_text=clean_frag, align_text=clean_align, facts=facts)
    cases.append(("⑮ 判据句混进 §1 事实抄录节 ⇒ K5 红", "K5", ctx15, None,
                  ["K0", "K1", "K2", "K3", "K4", "K6"]))

    # --- 反向用例 16: 官网原句锚点被从正文删掉 ⇒ K5 红 (★只删正文, 机器块不动★) ---
    page16 = _replace_in_prose(base_page, "4 Pin, 1 Row, Through Hole", "4 Pin, Through Hole")
    if page16 == base_page:
        raise AssertionError("自测用例 16 前提不成立: 找不到官网原句锚点")
    ctx16 = collect(page_text=page16, part_truth_text=clean_part,
                    frag_text=clean_frag, align_text=clean_align, facts=facts)
    cases.append(("⑯ 官网原句锚点被从正文删掉 ⇒ K5 红", "K5", ctx16, [], ["K0", "K1", "K2", "K3", "K4", "K6"]))

    # --- 反向用例 17: 证据等级标签不在白名单 ⇒ K5 红 (★只动页面标签, 不动机器块★) ---
    page17 = base_page.replace(
        "## §0 一句话结论",
        "## §0 一句话结论\n\n★证据等级标记: [官方] (★HW 侧白名单是 [官网], 不是 [官方]★)")
    if page17 == base_page:
        raise AssertionError("自测用例 17 前提不成立: 找不到 §0 标题")
    ctx17 = collect(page_text=page17, part_truth_text=clean_part,
                    frag_text=clean_frag, align_text=clean_align, facts=facts)
    cases.append(("⑰ 页面里冒出白名单外的证据等级标签 [官方] ⇒ K5 红", "K5", ctx17,
                  [], ["K0", "K1", "K2", "K3", "K4", "K6"]))

    # --- 反向用例 18: 台账 live_copies 指向不存在的文件 ⇒ K1 红 ---
    mb18 = json.loads(json.dumps(base_mb))
    mb18["live_copies"][0]["file"] = "HW/PCB/__NO_SUCH_FILE__.md"
    page18 = _rebuild_json_block(base_page, mb18)
    ctx18 = collect(page_text=page18, part_truth_text=clean_part,
                    frag_text=clean_frag, align_text=clean_align, facts=facts)
    cases.append(("⑱ 台账 live_copies 指向不存在的文件 ⇒ K1 红", "K1", ctx18, None,
                  ["K0", "K2", "K3", "K4", "K5", "K6"]))

    # --- 反向用例 19: 扫描面被删掉一个文件 ⇒ K1 红 (防漏扫) ---
    mb19 = json.loads(json.dumps(base_mb))
    mb19["scan_surface"] = [x for x in mb19.get("scan_surface", [])
                             if "check_debug_uart_seat_alignment.py" not in x]
    page19 = _rebuild_json_block(base_page, mb19)
    ctx19 = collect(page_text=page19, part_truth_text=clean_part,
                    frag_text=clean_frag, align_text=clean_align, facts=facts)
    cases.append(("⑲ 扫描面里删掉已签收闸源码 ⇒ K1 红 (防漏扫)", "K1", ctx19, None,
                  ["K0", "K2", "K3", "K4", "K5", "K6"]))

    # --- 反向用例 20: ★正向对照★ 全部外部文件合成【已订正】件 ⇒ K1/K2/K3 绿 ---
    cases.append(("⑳ 正向对照 (三份外部文件全换成已订正的合成件) ⇒ K1/K2/K3 全绿",
                  None, clean_ctx, None, ["K1", "K2", "K3"]))

    npass = 0
    ntotal = len(cases)
    for case in cases:
        name = case[0]
        want_red = case[1]
        ctx = case[2]
        forbid = case[3] if len(case) > 3 else None
        must_green = case[4] if len(case) > 4 else []
        results = run_all(ctx)
        reds = [code for code, _d, fails in results if fails]
        ok = True
        detail = []
        if want_red is None:
            if forbid:
                ok = forbid not in reds
                detail.append("期望 %s 【不红】" % forbid)
            else:
                ok = not reds
                detail.append("期望全绿")
        else:
            ok = want_red in reds
            detail.append("期望 %s 红" % want_red)
        if must_green:
            bad = [c for c in must_green if c in reds]
            ok = ok and not bad
            detail.append("期望其余绿 (%s)%s"
                          % (must_green, ("· 但红了 " + str(bad)) if bad else ""))
        detail.append("实际红: %s" % (reds or "无"))
        print("  [%s] %s" % ("PASS" if ok else "FAIL", name))
        print("        %s" % " · ".join(detail))
        if ok:
            npass += 1
    print("── selftest: %d/%d PASS" % (npass, ntotal))
    if npass == ntotal:
        print("ALL TESTS PASS")
        return 0
    print("SELFTEST FAILED")
    return 1


def _replace_json_key(page_text, key, new_value):
    """把机器块里某个顶层键的值换成 new_value (只用于自测)。"""
    mb, err = parse_machine_block(page_text)
    if err:
        raise AssertionError("自测前提不成立: %s" % err)
    mb[key] = new_value
    return _rebuild_json_block(page_text, mb)


def _replace_in_prose(page_text, old, new):
    """只在【正文】里替换 (机器块不动) —— 只用于自测制造反向用例。"""
    marker = "```json"
    idx = page_text.rfind(marker)
    if idx < 0:
        raise AssertionError("自测前提不成立: 页面里没有 json 块")
    prose = page_text[:idx]
    if old not in prose:
        raise AssertionError("自测前提不成立: 正文里找不到 `%s`" % old)
    return prose.replace(old, new) + page_text[idx:]


def _rebuild_json_block(page_text, mb):
    """把页面里的机器块换掉 (只用于自测)。"""
    blocks = list(re.finditer(r"```json\s*\n(.*?)\n```", page_text, re.S))
    if not blocks:
        raise AssertionError("自测前提不成立: 页面里没有 json 块")
    last = blocks[-1]
    txt = json.dumps(mb, ensure_ascii=False, indent=1)
    return page_text[:last.start(1)] + txt + page_text[last.end(1):]


# =========================================================================
# main
# =========================================================================
def main():
    ap = argparse.ArgumentParser(description="ISS-394 座体选型结论传播自守闸")
    ap.add_argument("--selftest", action="store_true", help="跑自测 (反向用例)")
    ap.add_argument("--emit", action="store_true", help="打印真相页机器块 (json)")
    args = ap.parse_args()
    if args.emit:
        ctx = collect()
        if ctx["mb_error"]:
            print(json.dumps({"error": ctx["mb_error"]}, ensure_ascii=False, indent=1))
            return 1
        print(json.dumps(ctx["mb"], ensure_ascii=False, indent=1))
        return 0
    if args.selftest:
        return selftest()
    ctx = collect()
    results = run_all(ctx)
    nfail = report(results, "ISS-394 座体选型结论传播自守闸")
    if nfail:
        print("❌ 有 %d 条判据红" % nfail)
        print("★红的是【现状】, 不是闸故障:")
        print("  K1 = 被推翻的料号仍以「首选/真值档」身份活在活副本里 ⇒ 要 main 落订正块")
        print("  K2 = 已闭 need 的答案仍指向被推翻的料号 ⇒ 要 main 落订正块")
        print("  K3 = 未答 need 的选项全错 ⇒ 要 main 改选项 (改选项 ≠ 答这条 need)")
        print("★main 落完那 5 处订正 + 把机器块 protected_files / live_copies 同步 ⇒ 同一条命令即转绿")
        return 1
    print("✅ 全绿")
    return 0


if __name__ == "__main__":
    sys.exit(main())
