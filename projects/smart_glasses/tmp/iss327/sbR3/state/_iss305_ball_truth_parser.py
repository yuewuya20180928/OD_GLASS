#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
state/_iss305_ball_truth_parser.py
================================================================================
★**ISS-305 · 真判别式 (ball → pin 名集合) 解析器** ★
★**owner = hw-lead · 2026-11-18 02:0x · 只读 · 零写板 · 零落表 · 零外发** ★

★**为什么要有这个脚本 (★复验的价值所在★)**:
  被复验对象 `state/_iss131_crosscheck_rk3572_caliber.py` 的球位判据是
  「ball 锚点 ±3 行窗口内出现该信号名」⇒ ★**非排他** ⇒ 同一窗口里躺着 3~7 个候选信号名
  ⇒ ★**换成相邻球位的信号名一样会被判通过** ⇒ 「11/11 逐条一致」这条结论比它看起来弱。
  ⇒ 本脚本建【真判别式】: 把 datasheet 球位表解析成 (ball → 该球位全部 pin 名集合),
    再做【排他归属】判定 ⇒ ★**换相邻球位必须判红**。

★**口径 (★交卷单必须写清★)**:
  R1  ★**只解析 §2.6 Pin Number List** (自动定位: "2.6 Pin Number List" → "Chapter 3")
      ⇒ 不含电源球表 / Chapter 3 电气规格 / Chapter 1 特性表
  R2  ★**文本解析 (pdftotext 产物) ⇒ 排版依赖**: PDF 重排版 ⇒ 解析结果可能变
  R3  ★**表行几何**: 球位表每行 = 3 个文本行 【左列名·第1段】/【右列 ball+Abbr】/【左列名·第2段】
      ⇒ 行距实测恒为 3 (锚点间隔) ⇒ 本脚本按「锚点 ±1 行」切行
      ⇒ ★**实测证据: 锚点间隔 = 3 的锚点串覆盖 L1436/1460/1510/1609 全表**
  R4  ball 锚点 = 满足 BALL_RE 且 (前面 2+ 空格) 且 (后面 2+ 空格 或 行尾) 的 token
  R5  pin 名 token = `^[A-Z][A-Z0-9_]*$` 且 不在停用词表 ⇒ ★**并按 '/' 拆开** (同球双名!)
  R6  ★**只做归属判定** ⇒ 不判电气属性 (电压 / 驱动能力 / 复用优先级)

★**用法**: `python3 state/_iss305_ball_truth_parser.py` ⇒ 打印判决 + 写 logs/iss305/07_*.log
★**边界**: 本脚本【不写任何工程文件】⇒ 板 / 网表 / 脚表 / BOM 一个字节都不动
"""
from __future__ import annotations

import csv
import os
import re
import sys
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
DS_TXT = os.path.join(PROJ, "HW", "RK3572_PIN_TABLE", "rk3572_datasheet_V1.1.txt")
BALLTAB = os.path.join(PROJ, "HW", "PCB", "FET3572C_PIN_TABLE.csv")
NETLIST = os.path.join(PROJ, "HW", "netlist_v1.csv")
REFCSV = os.path.join(PROJ, "HW", "RK3572_PIN_TABLE", "rk3572_pins.csv")

OUT: list[str] = []


def p(s: str = "") -> None:
    OUT.append(s)
    print(s)


BALL_RE = re.compile(r"^(?:\d{1,2})?[A-Z]{1,2}\d{1,2}$")
# ★pin 名 = 全大写主体 + 可选的小写后缀 (GPIO 复用名 GPIO3_C6_d / GPIO1_A0_u)★
PINNAME_RE = re.compile(r"^[A-Z][A-Z0-9_]*(_[a-z])?$")
STOP = {"PIN", "NAME", "ABBR", "RK3572", "DATASHEET", "REV", "COPYRIGHT", "BALL",
        "FUNCTION", "TYPE", "IO", "VOLTAGE"}

raw = open(DS_TXT, encoding="utf-8").read()
ds_lines = raw.split("\n")
if ds_lines and ds_lines[-1] == "":
    ds_lines = ds_lines[:-1]

# ---------------------------------------------------------------- 定位 §2.6 球位表
# ★取 Chapter 2 / Chapter 3 的【最后一次】出现 ⇒ 避开目录里的同名行 (L47/L48)★
ch2 = [i for i, ln in enumerate(ds_lines, start=1)
       if re.match(r"^\s*Chapter\s+2\s+Package\s+Information\s*$", ln)]
ch3 = [i for i, ln in enumerate(ds_lines, start=1)
       if re.match(r"^\s*Chapter\s+3\s+Electrical\s+Specification\s*$", ln)]
sec26 = [i for i, ln in enumerate(ds_lines, start=1)
          if re.match(r"^\s*2\.6\s+Pin\s+Number\s+List\s*$", ln)]
if not (ch2 and ch3 and sec26):
    p("★★ 定位 §2.6 失败: ch2=%s ch3=%s sec26=%s" % (ch2, ch3, sec26))
    sys.exit(2)
start = sec26[-1]
end = ch3[-1] - 1
assert start < end

p("=== ISS-305 · 真判别式 (ball → pin 名集合) 解析 ===")
p("datasheet            : %s" % DS_TXT)
p("总行数(split '\\n')   : %d" % len(ds_lines))
p("★§2.6 球位表行区间    : L%d .. L%d  (★自动定位: '2.6 Pin Number List' → 'Chapter 3'★)"
  % (start, end))
p()


def toks_of(line: str):
    """→ [(token, gap_before)]"""
    out = []
    for m in re.finditer(r"(\s*)(\S+)", line):
        out.append((m.group(2), len(m.group(1))))
    return out


def split_names(tok: str):
    """按 '/' 拆开同球双名"""
    return [x for x in tok.split("/") if x]


def find_anchor(clean: str):
    """返回 [(idx_in_tokens, ball)]"""
    if not clean.strip():
        return []
    tk = toks_of(clean)
    # 每个 token 的起始列
    starts = []
    pos = 0
    for _t, _g in tk:
        idx = clean.find(_t, pos)
        starts.append(idx)
        pos = idx + len(_t)
    cands = []
    for i, (tok, gap) in enumerate(tk):
        if not BALL_RE.match(tok):
            continue
        if i > 0 and gap < 2:
            continue
        if i + 1 < len(tk):
            gap_after = starts[i + 1] - (starts[i] + len(tok))
            if gap_after < 2:
                continue
        cands.append((i, tok))
    return cands


# ---------------------------------------------------------------- 切块 + 切行
seg = []          # [(ball, [line_no...], row_text)]
cur = []
for idx in range(start, end + 1):
    clean = ds_lines[idx - 1].replace("\f", "").rstrip()
    if clean.strip() == "":
        if cur:
            seg.append(cur)
            cur = []
        continue
    cur.append((idx, clean))
if cur:
    seg.append(cur)

ball2names: "OrderedDict[str, set]" = OrderedDict()
ball2lines: dict[str, list] = {}
multi = []
for blk in seg:
    anchors = []
    for k, (ln_no, clean) in enumerate(blk):
        for i, tok in find_anchor(clean):
            anchors.append((k, ln_no, i, tok))
    if not anchors:
        continue
    if len(anchors) > 1:
        multi.append([(a[1], a[3]) for a in anchors])
    k_anchor = [a[0] for a in anchors]
    for j, (k, ln_no, ti, ball) in enumerate(anchors):
        if len(anchors) == 1:
            lo, hi = 0, len(blk) - 1
        else:
            lo = max(0, k - 1)
            hi = min(len(blk) - 1, k + 1)
            if j + 1 < len(anchors):
                hi = min(hi, k_anchor[j + 1] - 2)     # 不越到下一行
            if j > 0:
                lo = max(lo, k_anchor[j - 1] + 2)      # 不压到上一行
        # ★左列是【一个连续字符串】被 PDF 折成 3 行 ⇒ 必须【无分隔符拼接】★
        # (★实测: B10 行 "…/SAI0_SDI2_M" + "0/SDMMC0_D1_M1/…" ⇒ 中间断在 token 里★)
        cell_parts = []
        for m in range(lo, hi + 1):
            _ln, clean2 = blk[m]
            if m == k:
                # 锚点行: 只取 ball 之前的左列文本 (ball 之后是 Abbr 列)
                tk = toks_of(clean2)
                if ti < len(tk):
                    _tok, _g = tk[ti]
                    _st = clean2.find(_tok)
                    cell_parts.append(clean2[:_st].rstrip())
                else:
                    cell_parts.append("")
            else:
                cell_parts.append(clean2.rstrip())
        cell_text = "".join(cell_parts)
        names = set()
        for part in cell_text.split("/"):
            part = part.strip()
            if PINNAME_RE.match(part) and part not in STOP:
                names.add(part)
        # ★Abbr 列 = 该球位的默认功能名 (dense 区才有) ⇒ 一并算作该球位的 pin 名★
        if k == len(blk) - 1 or True:
            tk = toks_of(blk[k][1])
            if ti + 1 < len(tk):
                abbr = tk[ti + 1][0]
                if PINNAME_RE.match(abbr) and abbr not in STOP:
                    names.add(abbr)
        ball2names.setdefault(ball, set()).update(names)
        ball2lines.setdefault(ball, []).append(ln_no)

p("解析出的球位数        : %d" % len(ball2names))
p("★多锚点块(几何自洽)  : %d   (★锚点间隔实测: %s★)"
  % (len(multi), [m[1][0] - m[0][0] for m in multi[:8]]))
p()

# ---------------------------------------------------------------- 与项目自带解析器交叉验证
ref = {}
if os.path.exists(REFCSV):
    with open(REFCSV, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            b = (r.get("ball") or "").strip()
            if b:
                ref[b] = (r.get("name") or "")
    same = 0
    diff = []
    for b, ns in ball2names.items():
        if b not in ref:
            continue
        refn = set(x for x in ref[b].split("/") if x)
        if refn <= ns:
            same += 1
        else:
            diff.append((b, sorted(refn - ns)))
    p("=== 与项目自带解析器 `HW/RK3572_PIN_TABLE/rk3572_pins.csv` 交叉验证 ===")
    p("  ref 球位数=%d · 本脚本球位数=%d" % (len(ref), len(ball2names)))
    p("  ★ref 的 name 集合【完全被本脚本覆盖】的球位 = %d / %d" % (same, len(ref)))
    if diff:
        p("  ★未被覆盖的 (ball, 缺的名字) 前 10 条:")
        for b, miss in diff[:10]:
            p("      %s : %s" % (b, miss))
    p()
    # ★★关键分歧: 同一 pin 名在两套解析里落在【不同球位】★★
    p("=== ★★关键分歧: 同一 pin 名在 ref 与本脚本里落在不同球位★★ ===")
    mine_owner = {}
    for b, ns in ball2names.items():
        for n in ns:
            mine_owner.setdefault(n, []).append(b)
    ref_owner = {}
    for b, ns in ref.items():
        for n in (ns or "").split("/"):
            if n:
                ref_owner.setdefault(n, []).append(b)
    conflict = []
    for n in sorted(set(mine_owner) & set(ref_owner)):
        if sorted(mine_owner[n]) != sorted(ref_owner[n]):
            conflict.append((n, sorted(ref_owner[n]), sorted(mine_owner[n])))
    p("  ★冲突 pin 名个数 = %d" % len(conflict))
    for n, rb, mb in conflict[:20]:
        p("      %-32s ref=%-12s 本脚本=%-12s" % (n, rb, mb))
    p()
    p("=== ★11 条落位: ref 与本脚本逐条一致? ===")
    for key in ("AM32", "A20", "B20", "A19", "B19", "1B14", "1C14", "A22", "B22", "A23", "B23"):
        r2 = set(x for x in (ref.get(key) or "").split("/") if x)
        mn = ball2names.get(key, set())
        p("  %-5s 一致=%-6s ref=%s" % (key, r2 == mn, sorted(r2)))
        if r2 != mn:
            p("        ★本脚本=%s" % sorted(mn))
    p()

# ---------------------------------------------------------------- 复验对象: 11 条
ball_rows = {}
with open(BALLTAB, encoding="utf-8") as f:
    for r in csv.DictReader(f):
        conn = (r.get("conn") or "").strip()
        num = (r.get("num") or "").strip()
        ball = (r.get("ball") or "").strip()
        sig = (r.get("signal") or "").strip()
        if conn and num:
            ball_rows[(conn, num)] = (ball, sig)

som_hits = []
with open(NETLIST, encoding="utf-8") as f:
    for r in csv.DictReader(f):
        blob = " ".join(str(v or "") for v in r.values())
        for m in re.finditer(r"J_SOM_(P2|P4)\s+pin(\d+)", blob):
            toks = set(re.findall(r"(?:NET_)?CSI_[A-Z0-9_]+", blob))
            som_hits.append((m.group(1), m.group(2), sorted(toks), blob))
csi_hits = [(c, n, t, b) for (c, n, t, b) in som_hits if t and any("CSI" in x for x in t)]

p("=== 11 条 CSI/MCLK 落位 · 真判别式重判 ===")
p("T1 归属 : ball ∈ 解析结果 且 该信号 ∈ names(ball)")
p("T2 排他 : 该信号的归属球位集合 == {ball} (★换相邻球位必须判红★)")
p("T3 同球双名 : names(ball) 允许含多个名字 (A22 = CSI0_D2P + CSI1_D0P)")
p()

rows_out = []
t1_pass = t2_pass = 0
for conn, num, toks, blob in csi_hits:
    key = (conn, num)
    if key not in ball_rows:
        continue
    ball, sig = ball_rows[key]
    names = ball2names.get(ball)
    if names is None:
        p("  %s pin%-3s ball=%-5s sig=%-30s ⇒ ✗ T1 解析结果里【没有该球位】"
          % (conn, num, ball, sig))
        rows_out.append((conn, num, ball, sig, False, False, 0, [], ""))
        continue
    hit = sig in names
    owners = sorted(b for b, ns in ball2names.items() if sig in ns)
    excl = (owners == [ball])
    lines = ball2lines.get(ball, [])
    if hit:
        t1_pass += 1
    if hit and excl:
        t2_pass += 1
    p("  %s pin%-3s ball=%-5s sig=%-30s ⇒ T1 %s · T2 %s · 归属球位=%s · 行号=%s"
      % (conn, num, ball, sig, "✔" if hit else "✗", "✔" if excl else "✗",
         owners, lines))
    if hit:
        sib = sorted(n for n in names if "MIPI_DPHY_CSI" in n or "CAM_CLK" in n)
        p("        ★该球位全部 MIPI_DPHY_CSI / CAM_CLK pin 名 = %s" % sib)
    else:
        p("        ★names(%s) = %s" % (ball, sorted(names)))
    rows_out.append((conn, num, ball, sig, hit, excl, len(owners), lines, ""))

p()
p("★T1 归属通过 = %d / %d" % (t1_pass, len(csi_hits)))
p("★T2 排他通过 = %d / %d" % (t2_pass, len(csi_hits)))
p()

# ---------------------------------------------------------------- 判别力对照实验
p("=== 判别力对照实验: 【真判别式】vs 【被审脚本的 ±3 行窗口】 ===")
p("做法(counterfactual): 把落位的信号名换成【同 D-PHY 组内相邻球位的信号名】")
p("      真判别式 ⇒ 必须判红 ; ±3 窗口 ⇒ 若仍判绿 ⇒ 判据非排他")
p()

ds_splitlines = raw.splitlines()
WIN_BALL_RE = re.compile(r"(?<![0-9A-Za-z_])([0-9]?[A-Z]{1,2}[0-9]{1,2})(?![0-9A-Za-z_])")


def win_window(ball: str, span: int = 3) -> str:
    out = []
    for i, ln in enumerate(ds_splitlines):
        if WIN_BALL_RE.fullmatch(ball) and re.search(
                r"(?<![0-9A-Za-z_])%s(?![0-9A-Za-z_])" % re.escape(ball), ln):
            for j in range(max(0, i - span), min(len(ds_splitlines), i + span + 1)):
                out.append(ds_splitlines[j])
    return "\n".join(out)


mis = []
for (conn, num, ball, sig, hit, excl, nown, lines, _x) in rows_out:
    names = ball2names.get(ball) or set()
    win = win_window(ball)
    # 窗口里出现的所有 pin 名 (被审脚本能接受的一切候选)
    win_names = set()
    for n in re.findall(r"[A-Z][A-Z0-9_]*(?:_[a-z])?", win):
        if n not in STOP:
            win_names.add(n)
    # ★其中【属于别的球位】的名字 ⇒ 窗口判据会误放行、真判别式会判红★
    wrong = []
    for n in sorted(win_names):
        if n == sig or n in names:
            continue
        owners = sorted(b for b, ns in ball2names.items() if n in ns)
        if owners and ball not in owners:
            wrong.append((n, owners))
    # 挑一个【相邻球位】的 CSI/MCLK 名做显式冒名 (★最狠的 counterfactual★)
    neigh = None
    for n, owners in wrong:
        if "MIPI_DPHY_CSI" in n or "CAM_CLK" in n:
            neigh = (n, owners)
            break
    if neigh is None and wrong:
        neigh = wrong[0]
    win_pass = truth_pass = None
    if neigh:
        n, owners = neigh
        win_pass = (n in win)
        truth_pass = (n in names)
    mis.append((conn, num, ball, sig, neigh, wrong, win_pass, truth_pass))
    p("  %s pin%-3s ball=%-5s 真信号=%-28s" % (conn, num, ball, sig))
    p("        ★±3 窗口里【属于别的球位】的 pin 名 = %d 个 ⇒ %s"
      % (len(wrong), [w[0] for w in wrong][:8]))
    if neigh:
        n, owners = neigh
        p("        ⇒ 显式冒名: 把本球位的信号说成 %-28s (它真正属于 %s)" % (n, owners))
        p("           ±3 窗口判据: %-18s ★真判别式: %s"
          % ("★仍判绿(非排他)★" if win_pass else "判红",
             "★仍判绿★" if truth_pass else "判红"))
p()
n_win = sum(1 for m in mis if m[6])
n_tru = sum(1 for m in mis if m[7])
p("★counterfactual 条数 = %d" % len(mis))
p("★±3 行窗口 判绿 = %d / %d  ⇒ ★**该判据非排他**★" % (n_win, len(mis)))
p("★真判别式   判绿 = %d / %d  ⇒ ★**该判据排他**★" % (n_tru, len(mis)))
p()

# ---------------------------------------------------------------- 同球双名簇
p("=== 同球双名簇 (A22/B22/A23/B23) 逐球位名单 ===")
for b in ("A22", "B22", "A23", "B23"):
    ns = sorted(n for n in (ball2names.get(b) or set()) if "MIPI_DPHY_CSI" in n)
    p("  ball=%-5s 行号=%s  CSI pin 名 = %s" % (b, ball2lines.get(b), ns))
p()

# ---------------------------------------------------------------- D-PHY 分组
p("=== datasheet 球位表里的 D-PHY 分组 (★判 B 的佐证★) ===")
grp = {}
for b, ns in ball2names.items():
    for n in ns:
        m = re.match(r"^MIPI_DPHY_(CSI\d)_RX_(D\d[PN]|CLK[PN])$", n)
        if m:
            grp.setdefault(m.group(1), []).append((b, n))
for g in sorted(grp):
    p("  %s : %s" % (g, sorted(grp[g])))
p()

logdir = os.path.join(PROJ, "logs", "iss305")
os.makedirs(logdir, exist_ok=True)
logpath = os.path.join(logdir, "07_ball_truth_parse.log")
with open(logpath, "w", encoding="utf-8") as f:
    f.write("\n".join(OUT) + "\n")
print()
print("[written] %s" % logpath)

ok = (t1_pass == len(csi_hits) and t2_pass == len(csi_hits) and n_tru == 0)
sys.exit(0 if ok else 1)
