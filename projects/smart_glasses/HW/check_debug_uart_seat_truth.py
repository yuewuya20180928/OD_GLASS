#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_debug_uart_seat_truth.py  ·  ISS-380 闸 K0~K5
「J_DEBUG / J_UART 座体厂商型号 + 座体真实高度 + 厂商 keepout 图纸」真相页自检闸

用法:
    python3 HW/check_debug_uart_seat_truth.py            # 正向跑, rc=0 全绿
    python3 HW/check_debug_uart_seat_truth.py --selftest  # 自测, 末行 ALL TESTS PASS

★纪律:
  · fail-closed —— 任一条不满足 ⇒ 该条红 ⇒ 整体 rc=1
  · 每条闸一条反向用例 (--selftest 里把入参改坏 ⇒ 必须判红)
  · ★零写板 · 零落表 · 零挂链 · 只读
  · ★本闸【不许挂进 state/gate_check.py】(挂链是 main 的地界) ⇒ 只交脚本 + 路径 + 建议

闸定义:
  K0  板侧脚数真值 与 BOM / 脚表 / 盘上封装 三方一致 (J_DEBUG=1×4 四脚, J_UART=1×2 两脚)
  K1  真相页 §2 每条厂商型号候选都带「料号 + 证据等级 + URL」, 且两类各 ≥2 条
  K2  真相页每条 [0数据] 都配了降级方案
  K3  真相页 §4 的 keepout 对象 (J_SOM_P1..P4 + J_USB_C) 全部登记, 且每个都有来源或降级
  K4  板三项指纹未动 (md5 / size / mtime)
  K5  真相页每条断言都带证据等级
"""

import argparse
import datetime
import hashlib
import os
import re
import sys

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(PROJ, "HW", "PCB", "BOARD_ONEPASS_DEBUG_UART_SEAT_PART_TRUTH.md")
PCB = os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb")
PINS = os.path.join(PROJ, "HW", "netlist_v1_pins.csv")
BOM = os.path.join(PROJ, "HW", "BOM_v1.csv")

# ---- 板三项指纹 (期望值) -------------------------------------------------
EXP_MD5 = "611b869e13518c3c023fb178f91a0075"
EXP_SIZE = 4940213
EXP_MTIME_ISO = "2026-11-06 07:07:17.362193"

# ---- 证据等级词表 --------------------------------------------------------
GRADES = ("[实测]", "[官网]", "[媒体]", "[推算]", "[0数据]")
# 降级方案标记 (K2 用)
DEGRADE_MARKS = ("降级", "上界", "保守", "索取机械图", "DNP", "改设计路径")

KEEP_OUT_TARGETS = ("J_SOM_P1", "J_SOM_P2", "J_SOM_P3", "J_SOM_P4", "J_USB_C")

CN_TZ = datetime.timezone(datetime.timedelta(hours=8))


# =========================================================================
# 入参采集 (全部只读)
# =========================================================================
def read_text(path):
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read()


def collect(page_text=None, pins_text=None, bom_text=None, pcb_md5=None,
            pcb_size=None, pcb_mtime_iso=None):
    """把闸要用的全部入参收成 dict —— 自测时逐项替换即可制造反向用例。"""
    ctx = {}
    ctx["page"] = read_text(PAGE) if page_text is None else page_text
    ctx["pins"] = read_text(PINS) if pins_text is None else pins_text
    ctx["bom"] = read_text(BOM) if bom_text is None else bom_text
    if pcb_md5 is None or pcb_size is None or pcb_mtime_iso is None:
        raw = open(PCB, "rb").read()
        md5 = hashlib.md5(raw).hexdigest()
        size = len(raw)
        mtime_iso = datetime.datetime.fromtimestamp(
            os.stat(PCB).st_mtime, CN_TZ).strftime("%Y-%m-%d %H:%M:%S.%f")
    else:
        md5, size, mtime_iso = pcb_md5, pcb_size, pcb_mtime_iso
    ctx["md5"] = md5
    ctx["size"] = size
    ctx["mtime"] = mtime_iso
    return ctx


def section(text, start_marker, end_marker=None):
    """截取 §start_marker 到下一个 §标题(或 end_marker)之间的正文。"""
    i = text.find(start_marker)
    if i < 0:
        return ""
    j = text.find("\n## ", i + len(start_marker))
    if end_marker:
        k = text.find(end_marker, i)
        if k >= 0:
            j = min(x for x in (j, k) if x >= 0)
    return text[i:j if j >= 0 else len(text)]


def _is_sep(cells):
    return bool(cells) and all((not c) or set(c) <= set("-: ") for c in cells)


def table_rows(text):
    """抽出表格里的数据行 (跳过表头行 / 分隔行)。"""
    out = []
    lines = text.split("\n")
    for i, ln in enumerate(lines):
        s = ln.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if not cells:
            continue
        if _is_sep(cells):
            continue          # 分隔行
        if cells[0] in ("#", "项", "段"):
            continue          # 表头行
        nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""
        if nxt.startswith("|"):
            nxt_cells = [c.strip() for c in nxt.strip("|").split("|")]
            if _is_sep(nxt_cells):
                continue      # 下一行是分隔行 ⇒ 本行是表头行
        out.append((cells, s))
    return out


def strip_bt(s):
    return s.replace("`", "").replace("*", "")


def has_grade(s):
    t = strip_bt(s)
    return any(g in t for g in GRADES)


def has_degrade(s):
    t = strip_bt(s)
    return any(m in t for m in DEGRADE_MARKS)


def footprint_block(pcb_text, ref):
    """取板上某个 ref 所在的 footprint 块 (按括号配平, 不越到下一颗)。"""
    m = re.search(r'\(property "Reference" "%s"' % re.escape(ref), pcb_text)
    if not m:
        return None
    start = pcb_text.rfind("(footprint", 0, m.start())
    if start < 0:
        return None
    depth = 0
    for idx in range(start, len(pcb_text)):
        ch = pcb_text[idx]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return pcb_text[start:idx + 1]
    return None


def sec_body(page, sec_id):
    """§N 一节的正文 (从 '## §N' 到下一个 '## ' 或 '### ' 之前), 含子节。"""
    m = re.search(r"^## §%s\b" % re.escape(sec_id), page, re.M)
    if not m:
        return ""
    rest = page[m.end():]
    nxt = re.search(r"^## ", rest, re.M)
    return rest[:nxt.start()] if nxt else rest


# =========================================================================
# K0  板侧脚数真值与 BOM / 脚表 / 盘上封装 三方一致
# =========================================================================
def k0(ctx):
    fails = []
    bom_lines = ctx["bom"].split("\n")
    for ref, n, spec in (("J_DEBUG", 4, "1×4"), ("J_UART", 2, "1×2")):
        rows = [l for l in bom_lines if l.split(",")[0].strip() == ref]
        if len(rows) != 1:
            fails.append("K0 BOM 行 `%s` 找到 %d 条 (应恰好 1 条)" % (ref, len(rows)))
            continue
        cells = [c.strip() for c in rows[0].split(",")]
        val = cells[2] if len(cells) > 2 else ""
        if spec not in val:
            fails.append("K0 BOM `%s` value 不含 `%s` (实读 %r)" % (ref, spec, val))
        if "1.27mm" not in val:
            fails.append("K0 BOM `%s` value 不含 `1.27mm` (实读 %r)" % (ref, val))
        # 脚表: 脚数 + pin1 信号名
        pin_rows = [l for l in ctx["pins"].split("\n")
                    if l.split(",")[0].strip().startswith(ref + ".pin")]
        if len(pin_rows) != n:
            fails.append("K0 脚表 `%s` 脚数 %d (应 %d)" % (ref, len(pin_rows), n))
        pin1 = [l for l in pin_rows if l.split(",")[0].strip() == ref + ".pin1"]
        if not pin1:
            fails.append("K0 脚表缺 `%s.pin1`" % ref)
        else:
            net = pin1[0].split(",")[1].strip()
            want = "JTAG_TCK" if ref == "J_DEBUG" else "UART_TX"
            if net != want:
                fails.append("K0 `%s.pin1` 网络 = %r (应 %r)" % (ref, net, want))
    # 盘上封装 pad 数
    pcb = read_text(PCB)
    for ref, n in (("J_DEBUG", 4), ("J_UART", 2)):
        blk = footprint_block(pcb, ref)
        if blk is None:
            fails.append("K0 盘上找不到封装 `%s`" % ref)
            continue
        pads = re.findall(r'\(pad "([^"]*)" (\w+) (\w+)', blk)
        smd = [p for p in pads if p[1] != "np_thru_hole"]
        if len(smd) != n:
            fails.append("K0 盘上 `%s` 非 NPTH pad 数 %d (应 %d)" % (ref, len(smd), n))
    return fails


# =========================================================================
# K1  §2 每条厂商型号候选 带 料号 + 证据等级 + URL, 且两类各 ≥2 条
# =========================================================================
PART_ROW = re.compile(r"^\|\s*(D|U)-(\d+)\s*\|")


def k1(ctx):
    fails = []
    s2 = sec_body(ctx["page"], "2")
    if not s2:
        return ["K1 真相页找不到 §2 一节"]
    cand = {"D": [], "U": []}
    for cells, raw in table_rows(s2):
        m = PART_ROW.match(raw.strip())
        if not m:
            continue
        kind = m.group(1)
        cand[kind].append((cells, raw))
        # 料号: 至少一个被反引号包住的、含数字与字母的料号
        pns = [c for c in cells if re.search(r"`[A-Za-z0-9][A-Za-z0-9\-/\.]{5,}`", c)]
        if not pns:
            fails.append("K1 §2 候选 `%s` 行没有像样的完整料号" % m.group(0).strip())
        if "http" not in raw:
            fails.append("K1 §2 候选 `%s` 行缺官网 URL" % m.group(0).strip())
        if not has_grade(raw):
            fails.append("K1 §2 候选 `%s` 行缺证据等级" % m.group(0).strip())
    for kind, label, need in (("D", "J_DEBUG", 2), ("U", "J_UART", 2)):
        if len(cand[kind]) < need:
            fails.append("K1 §2 %s 候选只有 %d 条 (应 ≥%d)" % (label, len(cand[kind]), need))
    return fails


# =========================================================================
# K2  每条 [0数据] 都配了降级方案
# =========================================================================
def k2(ctx):
    fails = []
    body = ctx["page"]
    hits = 0
    for i, ln in enumerate(body.split("\n"), 1):
        if "[0数据]" not in strip_bt(ln):
            continue
        s = ln.strip()
        if s.startswith("#") or (s and all(ch in "-= " for ch in s)):
            continue          # 标题行 / 分隔行 不算断言
        hits += 1
        if not has_degrade(ln):
            fails.append("K2 第 %d 行的 [0数据] 没配降级方案: %s" % (i, ln.strip()[:70]))
    if hits == 0:
        fails.append("K2 真相页里一条 [0数据] 都没有 (本页应当至少登记 [0数据] 项)")
    if "降级方案" not in body:
        fails.append("K2 真相页没有「降级方案」总节")
    return fails


# =========================================================================
# K3  §4 keepout 对象全部登记, 且每个都有来源或降级
# =========================================================================
def k3(ctx):
    fails = []
    s4 = sec_body(ctx["page"], "4")
    if not s4:
        return ["K3 真相页找不到 §4 一节"]
    for ref in KEEP_OUT_TARGETS:
        rows = [raw for cells, raw in table_rows(s4) if ref in raw]
        if not rows:
            fails.append("K3 §4 缺 keepout 对象 `%s` 的登记行" % ref)
            continue
        if not any(("http" in r) or has_degrade(r) for r in rows):
            fails.append("K3 §4 `%s` 既无来源 URL 也无降级方案" % ref)
    # 至少要有一行明确写「禁布区 / keepout」来源
    if not re.search(r"禁布区|keepout|Keepout|KEEPOUT", s4, re.I):
        fails.append("K3 §4 没写任何禁布区/keepout 来源")
    return fails


# =========================================================================
# K4  板三项指纹未动
# =========================================================================
def k4(ctx):
    fails = []
    if ctx["md5"] != EXP_MD5:
        fails.append("K4 板 md5 = %s (应 %s)" % (ctx["md5"], EXP_MD5))
    if int(ctx["size"]) != EXP_SIZE:
        fails.append("K4 板 size = %s (应 %d)" % (ctx["size"], EXP_SIZE))
    if ctx["mtime"] != EXP_MTIME_ISO:
        fails.append("K4 板 mtime = %s (应 %s)" % (ctx["mtime"], EXP_MTIME_ISO))
    # 真相页也要把板指纹写进去 (否则 §1-10 与板脱钩)
    if EXP_MD5 not in ctx["page"]:
        fails.append("K4 真相页里没写板 md5 (期望值 %s)" % EXP_MD5)
    return fails


# =========================================================================
# K5  每条断言都带证据等级
# =========================================================================
def k5(ctx):
    fails = []
    for sid in ("0", "1", "2", "3", "4", "5", "6"):
        body = sec_body(ctx["page"], sid)
        if not body:
            fails.append("K5 真相页找不到 §%s 一节" % sid)
            continue
        for cells, raw in table_rows(body):
            if not has_grade(raw):
                fails.append("K5 §%s 表格行缺证据等级: %s" % (sid, raw.strip()[:80]))
        for i, ln in enumerate(body.split("\n"), 1):
            s = ln.strip()
            if not s or s.startswith("#") or s.startswith(">"):
                continue
            if all(ch in "-= " for ch in s):
                continue      # 表格分隔行
            if not (s.startswith("-") or s.startswith("*") or s.startswith("★")):
                continue
            if not has_grade(s):
                fails.append("K5 §%s 正文行缺证据等级: %s" % (sid, s[:80]))
    return fails


CHECKS = [
    ("K0", "板侧脚数真值与 BOM/脚表/盘上封装一致", k0),
    ("K1", "§2 厂商型号候选 带 料号+证据等级+URL", k1),
    ("K2", "每条 [0数据] 配降级方案", k2),
    ("K3", "§4 keepout 对象全部登记且有来源/降级", k3),
    ("K4", "板三项指纹未动", k4),
    ("K5", "每条断言都带证据等级", k5),
]


def run_all(ctx):
    res = []
    for code, desc, fn in CHECKS:
        try:
            fails = fn(ctx)
        except Exception as exc:                      # fail-closed
            fails = ["%s 抛异常: %r" % (code, exc)]
        res.append((code, desc, fails))
    return res


# =========================================================================
# 自测: 每条闸一条反向用例 (改坏入参 ⇒ 必须判红)
# =========================================================================
def selftest():
    base = collect()
    ok = True

    # --- 正常基线必须全绿 ---
    base_fails = run_all(base)
    for code, desc, fails in base_fails:
        if fails:
            ok = False
            print("[SELFTEST][FAIL] 基线 %s 不绿: %s" % (code, fails))
    if ok:
        print("[SELFTEST] 基线 K0~K5 全绿")

    # --- 反向用例 ---
    cases = []

    # K0: 把 J_DEBUG 脚数改坏 (脚表里删掉 pin4)
    p = base["pins"].split("\n")
    bad = "\n".join(l for l in p if not l.startswith("J_DEBUG.pin4"))
    cases.append(("K0", "脚表 J_DEBUG 少一脚", collect(pins_text=bad)))

    # K1: 把某条候选行的 URL 抹掉
    lines = base["page"].split("\n")
    out = []
    hit = False
    for l in lines:
        if (not hit) and l.strip().startswith("| D-1 |"):
            hit = True
            l = re.sub(r"https?://\S+", "<URL-REMOVED>", l)
        out.append(l)
    cases.append(("K1", "D-1 行 URL 被抹", collect(page_text="\n".join(out))))

    # K2: 把某条 [0数据] 行的降级标记抹掉
    out = []
    hit = False
    for l in lines:
        if (not hit) and "[0数据]" in l and "降级" in l:
            hit = True
            l = l.replace("降级", "<DEGRADE-REMOVED>")
        out.append(l)
    if not hit:
        # 兜底: 抹掉全文第一处 [0数据] 行上的任一降级标记
        out = []
        hit = False
        for l in lines:
            if (not hit) and "[0数据]" in l:
                hit = True
                for mk in DEGRADE_MARKS:
                    if mk in l:
                        l = l.replace(mk, "<REMOVED>", 1)
                        break
            out.append(l)
    cases.append(("K2", "某条 [0数据] 行的降级方案被抹", collect(page_text="\n".join(out))))

    # K3: 删掉 §4 里 J_USB_C 的登记行 (★只许在 §4 一节内动手, 别误伤 §3.2 那行★)
    sec_a = next((i for i, l in enumerate(lines) if l.startswith("## §4")), None)
    sec_b = next((i for i, l in enumerate(lines) if l.startswith("## §5")), len(lines))
    out = []
    hit = False
    for i, l in enumerate(lines):
        if sec_a is not None and sec_a <= i < sec_b:
            if (not hit) and l.strip().startswith("|") and "`J_USB_C`" in l and "GCT" in l:
                hit = True
                continue
        out.append(l)
    if not hit:
        print("[SELFTEST][FAIL] K3 反向用例造不出来 (§4 里没找到 J_USB_C 行)")
        ok = False
    cases.append(("K3", "§4 的 J_USB_C 登记行被删", collect(page_text="\n".join(out))))

    # K4: 改板 md5
    cases.append(("K4", "板 md5 被改", collect(pcb_md5="0" * 32,
                                            pcb_size=EXP_SIZE,
                                            pcb_mtime_iso=EXP_MTIME_ISO)))

    # K5: 把某条表格行的【所有】证据等级抹掉 (只抹一个会漏 —— 行里往往还藏着别的等级词)
    out = []
    hit = False
    for l in lines:
        if (not hit) and l.strip().startswith("| 1-1 |"):
            hit = True
            for g in GRADES:
                l = l.replace(g, "<GRADE-REMOVED>")
        out.append(l)
    if not hit:
        print("[SELFTEST][FAIL] K5 反向用例造不出来 (没找到 | 1-1 | 行)")
        ok = False
    cases.append(("K5", "表格行证据等级被抹", collect(page_text="\n".join(out))))

    for code, name, ctx in cases:
        fails = []
        for c, _d, fn in CHECKS:
            if c != code:
                continue
            try:
                fails = fn(ctx)
            except Exception as exc:
                fails = ["异常 %r" % exc]
        if fails:
            print("[SELFTEST][OK] %s 反向用例判红: %s" % (code, name))
        else:
            ok = False
            print("[SELFTEST][FAIL] %s 反向用例没判红: %s" % (code, name))

    if ok:
        print("ALL TESTS PASS")
        return 0
    print("SELFTEST FAILED")
    return 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    ctx = collect()
    res = run_all(ctx)
    red = 0
    print("=== ISS-380 闸 · check_debug_uart_seat_truth ===")
    for code, desc, fails in res:
        if fails:
            red += 1
            print("[RED ] %s  %s" % (code, desc))
            for f in fails:
                print("        - %s" % f)
        else:
            print("[GRN ] %s  %s" % (code, desc))
    print("--- 板指纹: md5=%s size=%s mtime=%s" % (ctx["md5"], ctx["size"], ctx["mtime"]))
    if red:
        print("RESULT: %d 条红" % red)
        return 1
    print("RESULT: K0~K5 全绿 (6/6)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
