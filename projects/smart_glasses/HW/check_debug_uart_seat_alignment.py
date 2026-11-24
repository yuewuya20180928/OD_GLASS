#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_debug_uart_seat_alignment.py  ·  ISS-383 闸 K0~K4
「J_DEBUG / J_UART 座体选型四方对齐作业包」对齐表 / 冲突显形 / BOM 型号栏草案 自检闸

用法:
    python3 HW/check_debug_uart_seat_alignment.py            # 正向跑, rc=0 全绿
    python3 HW/check_debug_uart_seat_alignment.py --selftest  # 自测, 末行 ALL TESTS PASS

★纪律:
  · fail-closed —— 任一条不满足 ⇒ 该条红 ⇒ 整体 rc=1
  · 每条闸一条反向用例 (--selftest 里把入参改坏 ⇒ 必须判红)
  · ★零写板 · 零落表 · 零挂链 · 只读
  · ★本闸【不许挂进 state/gate_check.py】(挂链是 main 的地界) ⇒ 只交脚本 + 路径 + 建议
  · ★本闸【不许改】HW/check_debug_uart_seat_truth.py (ISS-380 交卷闸)
    与 HW/check_juart_land_fit.py (ISS-379 交卷闸) 的任何一行

闸定义:
  K0  板三项指纹未动 (md5 / size / mtime) + 已签收件 (ISS-380 真相页 + ISS-380 闸) md5 未动
  K1  四方口径对齐表在页里且四行齐全 (逐行点名, 不许只比数量)
  K2  「口径冲突」必须被显式登记 (逐格点名 + 必须写清后果) —— ★本闸的命门: 让冲突显形, 不是让冲突消失★
  K3  §4 的 BOM 型号栏草案料号与 §1 候选件表逐字一致 + BOM 真源型号栏此刻仍应是「待定」(防越界)
  K4  证据等级 + 零挂起 + 零挂链 + 判据/事实分开
"""

import argparse
import datetime
import hashlib
import os
import re
import sys

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(PROJ, "HW", "PCB", "BOARD_ONEPASS_DEBUG_UART_SEAT_ALIGNMENT.md")
PCB = os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb")
BOM = os.path.join(PROJ, "HW", "BOM_v1.csv")
GATE_CHECK = os.path.join(PROJ, "state", "gate_check.py")
TRUTH_PAGE = os.path.join(PROJ, "HW", "PCB", "BOARD_ONEPASS_DEBUG_UART_SEAT_PART_TRUTH.md")
TRUTH_GATE = os.path.join(PROJ, "HW", "check_debug_uart_seat_truth.py")

# ---- 板三项指纹 (期望值) -------------------------------------------------
EXP_MD5 = "611b869e13518c3c023fb178f91a0075"
EXP_SIZE = 4940213
EXP_MTIME_ISO = "2026-11-06 07:07:17.362193"

# ---- 已签收件 md5 (ISS-380 交卷件, 只读) --------------------------------
EXP_TRUTH_PAGE_MD5 = "1a9ade1bde85530c09054e2fdb8d5adb"
EXP_TRUTH_GATE_MD5 = "274f759101ca4bc131f25633dc209b0c"

# ---- 证据等级词表 --------------------------------------------------------
GRADES = ("[实测]", "[官网]", "[媒体]", "[推算]", "[0数据]")

# ---- 零挂起词表 (K4 用) -------------------------------------------------
HANG = ("TODO", "TBD", "FIXME", "XXX", "待补", "???")

# ---- 四方对齐表必须有的四行 (K1 逐行点名) ------------------------------
ALIGN_ROWS = ("① BOM 描述栏", "② 板面实际封装", "③ 结构侧模型", "④ E-1 板决策")

# ---- 必须逐格登记冲突的四格 (K2 用) --------------------------------------
GRID_NAMES = ("排距", "脚数", "排布", "型态")

# ---- BOM 里与「厂商型号」相关的列 (K3 用) -------------------------------
MODEL_COLS = ("tbd", "footprint", "opn", "tolerance", "alt_part")
MODEL_EMPTY_OK = ("", "待定")

# ---- 料号识别口径 (K3 用): 至少一个连字符, 或 11 位纯数字 (Würth 式) ----
PN_RE = re.compile(r"^[A-Z0-9]+(?:-[A-Z0-9]+)+$")
PN_NUM_RE = re.compile(r"^[0-9]{11}$")


# =========================================================================
# 小工具
# =========================================================================
def read_text(path):
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read()


def md5_of(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def section(text, start_pat, end_pat):
    """取两个标题之间的正文 (含 start 标题行本身)。"""
    m = re.search(start_pat, text, re.M)
    if not m:
        return ""
    rest = text[m.start():]
    m2 = re.search(end_pat, rest[1:], re.M)
    return rest if not m2 else rest[: m2.start() + 1]


def numbered_sections(text):
    """按 `## §N` 标题切段 ⇒ [(num, heading, body)]。"""
    heads = list(re.finditer(r"(?m)^##\s*§(\d+)\b(.*)$", text))
    out = []
    for i, h in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        out.append((h.group(1), h.group(2).strip(), text[h.start():end]))
    return out


def is_sep_row(line):
    """表格分隔行 (|---|---|) 或纯装饰行 —— 不算数据行。"""
    core = line.replace("|", "").replace("-", "").replace(":", "").replace(" ", "")
    return core == ""


def table_data_rows(text):
    """抽出表格数据行 (排除分隔行与表头行)。"""
    lines = text.splitlines()
    out = []
    for i, ln in enumerate(lines):
        s = ln.strip()
        if not s.startswith("|"):
            continue
        if is_sep_row(s):
            continue
        # 表头行 = 紧邻下一行是分隔行
        if i + 1 < len(lines) and is_sep_row(lines[i + 1].strip()):
            continue
        out.append(s)
    return out


# =========================================================================
# 入参采集 (全部只读)
# =========================================================================
def collect(page_text=None, bom_text=None, board_md5=None, board_size=None,
            board_mtime_iso=None, truth_page_md5=None, truth_gate_md5=None,
            gate_check_text=None):
    ctx = {}
    ctx["page"] = read_text(PAGE) if page_text is None else page_text
    ctx["bom"] = read_text(BOM) if bom_text is None else bom_text
    if board_md5 is None or board_size is None or board_mtime_iso is None:
        raw = open(PCB, "rb").read()
        if board_md5 is None:
            board_md5 = hashlib.md5(raw).hexdigest()
        if board_size is None:
            board_size = len(raw)
        if board_mtime_iso is None:
            board_mtime_iso = datetime.datetime.fromtimestamp(
                os.path.getmtime(PCB)).strftime("%Y-%m-%d %H:%M:%S.%f")[:26]
    ctx["md5"] = board_md5
    ctx["size"] = board_size
    ctx["mtime"] = board_mtime_iso
    ctx["truth_page_md5"] = md5_of(TRUTH_PAGE) if truth_page_md5 is None else truth_page_md5
    ctx["truth_gate_md5"] = md5_of(TRUTH_GATE) if truth_gate_md5 is None else truth_gate_md5
    ctx["gate_check"] = read_text(GATE_CHECK) if gate_check_text is None else gate_check_text
    return ctx


def bom_rows(text):
    """极简 CSV 行解析 (本 BOM 无嵌入逗号引号场景, 但仍做一次引号剥离)。"""
    rows = []
    for ln in text.splitlines():
        if not ln.strip():
            continue
        cells = [c.strip().strip('"') for c in ln.split(",")]
        rows.append(cells)
    return rows


# =========================================================================
# 闸
# =========================================================================
def k0(ctx):
    fails = []
    if ctx["md5"] != EXP_MD5:
        fails.append("板 md5 漂移: 期望 %s 实得 %s" % (EXP_MD5, ctx["md5"]))
    if int(ctx["size"]) != EXP_SIZE:
        fails.append("板 size 漂移: 期望 %d 实得 %s" % (EXP_SIZE, ctx["size"]))
    if ctx["mtime"] != EXP_MTIME_ISO:
        fails.append("板 mtime 漂移: 期望 %s 实得 %s" % (EXP_MTIME_ISO, ctx["mtime"]))
    if ctx["truth_page_md5"] != EXP_TRUTH_PAGE_MD5:
        fails.append("已签收件 BOARD_ONEPASS_DEBUG_UART_SEAT_PART_TRUTH.md md5 漂移: 期望 %s 实得 %s"
                     % (EXP_TRUTH_PAGE_MD5, ctx["truth_page_md5"]))
    if ctx["truth_gate_md5"] != EXP_TRUTH_GATE_MD5:
        fails.append("已签收件 check_debug_uart_seat_truth.py md5 漂移: 期望 %s 实得 %s"
                     % (EXP_TRUTH_GATE_MD5, ctx["truth_gate_md5"]))
    return fails


def k1(ctx):
    """四方对齐表四行齐全 —— 逐行点名, 不许只比数量。"""
    fails = []
    s3 = section(ctx["page"], r"^##\s*§3\b", r"^##\s*§4\b")
    if not s3:
        return ["页里找不到 §3 四方口径对齐表"]
    for row in ALIGN_ROWS:
        if row not in s3:
            fails.append("§3 对齐表缺这一行: %s" % row)
    return fails


def _grid_lines(ctx):
    out = []
    for ln in ctx["page"].splitlines():
        ln = ln.strip()
        if ln.startswith("GRID|"):
            out.append(ln)
    return out


def _conflict_lines(ctx):
    out = []
    for ln in ctx["page"].splitlines():
        s = ln.strip()
        if s.startswith("CONFLICT|"):
            out.append(s)
    return out


def k2(ctx):
    """口径冲突必须被显式登记 —— 逐格点名 + 必须写清后果。"""
    fails = []
    grids = _grid_lines(ctx)
    if not grids:
        return ["页里找不到 MACHINELINE 口径块 (GRID|... 四行) —— K2 无法判定, fail-closed"]
    required = []
    for g in grids:
        parts = g.split("|")
        if len(parts) < 3:
            fails.append("MACHINELINE 行格式不对: %s" % g)
            continue
        name = parts[1]
        vals = []
        for kv in parts[2:]:
            if "=" not in kv:
                continue
            k, v = kv.split("=", 1)
            v = v.strip()
            if v in ("", "unset"):
                continue
            vals.append((k.strip(), v))
        if len(set(v for _, v in vals)) > 1:
            required.append(name)
    if not required:
        fails.append("MACHINELINE 里四格没有任何一格出现口径分歧 —— 与 §3.1 自相矛盾, fail-closed")
    conflicts = _conflict_lines(ctx)
    for name in required:
        hit = [c for c in conflicts if c.split("|")[1:2] == [name]]
        if not hit:
            fails.append("口径冲突没被显式登记: 格「%s」在四个口径之间不一致, 但 CONFLICT 登记里没有这一格" % name)
            continue
        for c in hit:
            if "后果" not in c:
                fails.append("冲突登记「%s」没写清后果: %s" % (name, c[:80]))
    return fails


def k3(ctx):
    """§4 草案料号必须与 §1 候选件表逐字一致 + BOM 真源型号栏此刻仍应是「待定」。"""
    fails = []
    page = ctx["page"]
    s1 = section(page, r"^##\s*§1\b", r"^##\s*§2\b")
    s4 = section(page, r"^##\s*§4\b", r"^##\s*§5\b")
    if not s1:
        fails.append("页里找不到 §1 候选件真实规格表")
    if not s4:
        fails.append("页里找不到 §4 BOM 型号栏草案")
    if s1 and s4:
        pns = []
        for tok in re.findall(r"`([^`\n]+)`", s4):
            t = tok.strip()
            if PN_RE.match(t) or PN_NUM_RE.match(t):
                if t not in pns:
                    pns.append(t)
        if not pns:
            fails.append("§4 型号栏草案里一个可识别的料号都没有 —— 草案不成其为草案")
        for t in pns:
            if t not in s1:
                fails.append("§4 草案里冒出一颗 §1 没查过的料号: %s" % t)
    # BOM 真源: 型号栏必须仍是「待定」(本单零落表 ⇒ 防越界)
    rows = bom_rows(ctx["bom"])
    if not rows:
        fails.append("BOM_v1.csv 读不到行")
        return fails
    header = rows[0]
    colmap = {}
    for i, h in enumerate(header):
        key = h.strip().strip('"')
        if key in MODEL_COLS:
            colmap[key] = i
    for key in MODEL_COLS:
        if key not in colmap:
            fails.append("BOM_v1.csv 表头里找不到列「%s」" % key)
    for ref in ("J_DEBUG", "J_UART"):
        hit = [r for r in rows[1:] if r and r[0].strip().strip('"') == ref]
        if not hit:
            fails.append("BOM_v1.csv 里找不到 ref「%s」" % ref)
            continue
        row = hit[0]
        for key, idx in colmap.items():
            if idx >= len(row):
                continue
            val = row[idx].strip()
            if val not in MODEL_EMPTY_OK:
                fails.append("BOM 真源已被改动: %s 的「%s」列 = 「%s」, 本单零落表, 此刻必须是空或「待定」"
                             % (ref, key, val))
    return fails


def k4(ctx):
    """证据等级 + 零挂起 + 零挂链 + 判据/事实分开。"""
    fails = []
    page = ctx["page"]
    for num, _heading, body in numbered_sections(page):
        if num not in ("1", "2", "3", "4", "5"):
            continue
        for row in table_data_rows(body):
            if not any(g in row for g in GRADES):
                fails.append("表格断言没有证据等级: %s" % row[:90])
    for h in HANG:
        if h in page:
            fails.append("页里有挂起标记「%s」" % h)
    if "check_debug_uart_seat_alignment" in ctx["gate_check"]:
        fails.append("state/gate_check.py 里已经挂上了本闸 —— 挂链是 main 的地界, 本单零挂链")
    if not re.search(r"^#{2,4}\s*.*判据.*事实", page, re.M):
        fails.append("页里没有把「判据」与「事实」分开的段")
    if "★**判据" not in page or "★**事实" not in page:
        fails.append("页里没有逐条列出判据与事实")
    return fails


GATES = (
    ("K0", "板三项指纹 + 已签收件 md5 未动", k0),
    ("K1", "四方口径对齐表四行齐全 (逐行点名)", k1),
    ("K2", "口径冲突必须被显式登记 (逐格点名 + 写清后果)", k2),
    ("K3", "§4 草案料号与 §1 一致 + BOM 型号栏仍「待定」", k3),
    ("K4", "证据等级 + 零挂起 + 零挂链 + 判据/事实分开", k4),
)


def run_all(ctx):
    out = []
    for code, desc, fn in GATES:
        try:
            fails = fn(ctx)
        except Exception as exc:            # fail-closed: 闸自己炸了也算红
            fails = ["闸内部异常 (fail-closed): %r" % (exc,)]
        out.append((code, desc, fails))
    return out


# =========================================================================
# 自测 (每条闸一条反向用例)
# =========================================================================
def selftest():
    base = collect()
    cases = []

    # K0 反向: 板 md5 漂移
    c = collect(board_md5="deadbeef" * 4)
    cases.append(("K0", "板 md5 漂移", k0(c), True))

    # K1 反向: 删掉「④ E-1 板决策」这一行
    p = base["page"].replace("④ E-1 板决策", "④ (已删除)")
    c = collect(page_text=p)
    cases.append(("K1", "对齐表缺「④ E-1 板决策」行", k1(c), True))

    # K1 反向: 只留三行也必须红 (不许只比数量)
    p = base["page"]
    for r in ALIGN_ROWS:
        p = p.replace(r, r.replace("① ", "").replace("② ", "").replace("③ ", "").replace("④ ", ""))
    c = collect(page_text=p)
    cases.append(("K1", "对齐表四行被抹掉 (只比数量会漏)", k1(c), True))

    # K2 反向: 删掉「型态」那一格的 CONFLICT 登记
    p = "\n".join(ln for ln in base["page"].splitlines()
                  if not ln.strip().startswith("CONFLICT|型态|"))
    c = collect(page_text=p)
    cases.append(("K2", "型态格的冲突没登记", k2(c), True))

    # K2 反向: 登记了但不写后果
    p = base["page"].replace(
        "CONFLICT|排距|① BOM描述栏 1.27mm vs ② 板面实际封装 0.50mm|后果:",
        "CONFLICT|排距|① BOM描述栏 1.27mm vs ② 板面实际封装 0.50mm|说明:")
    c = collect(page_text=p)
    cases.append(("K2", "冲突登记没写清后果", k2(c), True))

    # K3 反向: §4 草案冒出一颗 §1 没有的料号
    p = base["page"].replace(
        "### §4.1 `J_DEBUG` 行型号栏草案",
        "### §4.1 `J_DEBUG` 行型号栏草案\n\n ★**伪造料号** `ZZZZ-999-01-X-Y`")
    c = collect(page_text=p)
    cases.append(("K3", "§4 冒出一颗 §1 没查过的料号", k3(c), True))

    # K3 反向: BOM 真源被落表 (型号栏被填上料号)
    bom = base["bom"].replace(
        "J_DEBUG,1,1×4 1.27mm 排针 (JTAG),CONN,必装,镜脚主 PCB,P8,[推算],,待定,",
        "J_DEBUG,1,1×4 1.27mm 排针 (JTAG),CONN,必装,镜脚主 PCB,P8,[推算],,Samtec FTSH-104-01-F-DV,")
    c = collect(bom_text=bom)
    cases.append(("K3", "BOM 真源被落表 (型号栏被填上料号)", k3(c), True))

    # K4 反向: 表格断言去掉证据等级
    p = base["page"].replace("| `[官网]` + `[媒体]` |", "| |", 1)
    c = collect(page_text=p)
    cases.append(("K4", "表格断言无证据等级", k4(c), True))

    # K4 反向: 页里出现挂起标记
    p = base["page"] + "\nTODO: 待补\n"
    c = collect(page_text=p)
    cases.append(("K4", "页里有挂起标记", k4(c), True))

    # K4 反向: 闸被挂进 state/gate_check.py
    c = collect(gate_check_text=base["gate_check"] + "\n# check_debug_uart_seat_alignment.py\n")
    cases.append(("K4", "闸被挂进 gate_check.py", k4(c), True))

    # K4 反向: 判据/事实没分开
    p = re.sub(r"^#{2,4}\s*.*判据.*事实.*$", "## §3.3 别的标题", base["page"], flags=re.M)
    c = collect(page_text=p)
    cases.append(("K4", "判据/事实没分开", k4(c), True))

    # 正向: 原样必须全绿
    pos = run_all(base)
    ok = True
    for code, desc, fails in pos:
        if fails:
            ok = False
            print("[SELFTEST][FAIL] %s 正向用例没全绿: %s" % (code, desc))
            for f in fails[:5]:
                print("        - %s" % f)

    for code, name, fails, expect_red in cases:
        red = bool(fails)
        if red != expect_red:
            ok = False
            print("[SELFTEST][FAIL] %s 反向用例判定不对: %s (期望 %s)"
                  % (code, name, "红" if expect_red else "绿"))
        else:
            print("[SELFTEST][OK  ] %s %s" % (code, name))

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
    print("=== ISS-383 闸 · check_debug_uart_seat_alignment ===")
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
    print("RESULT: K0~K4 全绿 (5/5)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
