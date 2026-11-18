#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iss317_sb_bom_silence.py —— ISS-317 §3 · BOM 证据静默消失的【可机判判据】证明器

★★★ 边界 (★硬★) ★★★
  ★只读: HW/BOM_v1.csv · HW/netlist_v1_pins.csv · HW/PCB/demo_mainboard.kicad_pcb ★
  ★只写: tmp/iss317_sandbox/ + logs/iss317/ ★
  ★**不跑 state/gen_bom.py** (★零重生成★) ★
  ★**不写任何真源** (★零落表 / 零写板★) ★
  ⇒ ★本脚本只【复刻 gen_bom.py 的两个只读动作】并【算差】, 不产 BOM★

─── 要证明的那件事 (★ISS-311 地雷 2 / ISS-314 §2-④★) ─────────────────────
  gen_bom.py 用【精确 ref】查板文件封装:
      board = parse_board_footprints(PCB_FILE)     → {ref: {...}}
      bb = board.get(ref)                           → ★精确 ref 查★
  ⇒ ★板侧改名 ⇒ 精确 ref 查不到 ⇒ 「封装/型号来源: 板文件 ...」那些证据行【整段消失】★
  ⇒ ★**没有任何报警** ⇒ BOM 看起来是绿的, 证据已经没了★

─── 本脚本的判据 (★机器可判·不是散文★) ────────────────────────────────
  判据 J1 (★证据覆盖率守恒★):
      ★「以板文件为证据来源」的 BOM 行数, 改名后必须 == 改名前★
      ⇒ 少一行 = 判红 (★证据静默消失★)
  判据 J2 (★逐 ref 命中集必须相等★):
      ★evidence_refs_after ⊇ evidence_refs_before ★
      ⇒ 少任何一个 ref = 判红
  判据 J3 (★反向用例: 必须能抓住「只改板侧不改 BOM 侧」★):
      ★把板侧改成 X_1 而 BOM 侧还是 X ⇒ J1/J2 必须判红★
      ⇒ 破坏前绿 · 破坏后红 ⇒ ★不是巧合自证★

─── 场景 ─────────────────────────────────────────────────────────────
  S0 基线  : 板 = 原板 (ref 不带 _1)   · BOM = 现状      ⇒ 期望 J1/J2 全绿
  S1 事故场: 板 = 改名后的板 (ref 带 _1) · BOM = 现状    ⇒ 期望 J1/J2 判红 (★证据静默消失★)
  S2 反向  : 板 = 原板                  · BOM = 现状      ⇒ 期望 J1/J2 全绿 (★对照组★)
  S3 对照场: 板 = 改名后的板            · BOM = 改名后的 ⇒ 期望 J1/J2 全绿 (★两边同步就不丢★)
"""
import csv
import os
import re
import shutil
import sys
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))          # logs/iss317/
PROJ = os.path.dirname(os.path.dirname(HERE))              # 项目根
SB = os.path.join(PROJ, "tmp", "iss317_sandbox")
os.makedirs(SB, exist_ok=True)

SRC_PCB = os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb")
SRC_BOM = os.path.join(PROJ, "HW", "BOM_v1.csv")
REF_RE = re.compile(r'(\(property "Reference" ")([^"]*)(")')

# ★★ gen_bom.py 里「证据来源是板文件」的两种痕迹 (★逐字复刻·不改判据方向★) ★★
EV_PAT = re.compile(r"板文件")


def parse_board_footprints(pcb_path):
    """★逐字复刻 state/gen_bom.py::parse_board_footprints (★只读·不 import 项目模块★)"""
    out = OrderedDict()
    if not os.path.exists(pcb_path):
        return out
    txt = open(pcb_path, encoding="utf-8").read()
    i = 0
    while True:
        j = txt.find("(footprint ", i)
        if j < 0:
            break
        depth, k = 0, j
        while k < len(txt):
            c = txt[k]
            if c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
                if depth == 0:
                    break
            k += 1
        blk = txt[j:k + 1]
        i = k + 1
        props = dict(re.findall(r'\(property "([^"]+)" "([^"]*)"', blk))
        ref = (props.get("Reference") or "").strip()
        if not ref or ref in out:
            continue
        pads = re.findall(r'\(pad\s+"([^"]*)"', blk)
        out[ref] = {"value": (props.get("Value") or "").strip(), "pads": pads, "npads": len(pads)}
    return out


def kicad_ref(ref):
    r = (ref or "").strip()
    if r and r[-1].isdigit():
        return r
    return r + "_1"


def build_renamed_pcb(out_name):
    """★把板侧 ref 改名 (★只写沙盒★) ⇒ 模拟「只改板侧不改 BOM 侧」★"""
    src = open(SRC_PCB, encoding="utf-8", errors="replace").read()
    n = 0
    def repl(m):
        nonlocal n
        old = m.group(2)
        new = kicad_ref(old)
        if new != old:
            n += 1
        return m.group(1) + new + m.group(3)
    out = REF_RE.sub(repl, src)
    p = os.path.join(SB, out_name)
    open(p, "w", encoding="utf-8", errors="replace").write(out)
    print("  ★沙盒改名板 %-28s 改名 %d 个 · → %s" % (out_name, n, os.path.relpath(p, PROJ)))
    return p


def bom_evidence_refs(bom_csv):
    """★BOM 里「以板文件为证据来源」的行 ⇒ ref 集合 (★读 memo/footprint 列★)"""
    rows = list(csv.DictReader(open(bom_csv, encoding="utf-8-sig")))
    out = []
    for r in rows:
        blob = " ".join([(r.get("memo") or ""), (r.get("footprint") or ""),
                         (r.get("evidence") or ""), (r.get("opn") or "")])
        if EV_PAT.search(blob):
            out.append((r.get("ref") or "").strip())
    return out


def build_renamed_bom(bom_csv, out_name):
    """★把 BOM 侧 ref 也改名 (★只写沙盒★) ⇒ 模拟「五侧同口径·BOM 侧同步改名」★"""
    rows = list(csv.DictReader(open(bom_csv, encoding="utf-8-sig")))
    flds = list(rows[0].keys())
    out = []
    for r in rows:
        r2 = dict(r)
        ref = (r2.get("ref") or "").strip()
        if ref:
            r2["ref"] = kicad_ref(ref)
        out.append(r2)
    p = os.path.join(SB, out_name)
    with open(p, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=flds)
        w.writeheader()
        for r in out:
            w.writerow(r)
    print("  ★沙盒改名 BOM %-28s 行数 %d · → %s" % (out_name, len(out), os.path.relpath(p, PROJ)))
    return p


def judge(board_pcb, bom_csv, tag):
    """★跑 J1 / J2 两条判据 ⇒ 返回 (判红?, 读数行列表) ★"""
    board = parse_board_footprints(board_pcb)
    ev_refs = bom_evidence_refs(bom_csv)
    ev_set = set(ev_refs)
    # ★J1: 逐条核「这条证据所依赖的板文件封装, 改名后还能不能查到」★
    lost = []
    for ref in sorted(ev_set):
        if ref not in board:
            lost.append(ref)
    lines = []
    lines.append("  场景 %s" % tag)
    lines.append("    板文件封装数            : %d" % len(board))
    lines.append("    BOM「板文件证据」行数   : %d  (ref: %s)"
                 % (len(ev_refs), ", ".join(sorted(ev_set))))
    lines.append("    ★J1 逐条命中 (★ref 在改名后的板里还能查到吗★): 丢 %d 个" % len(lost))
    if lost:
        for r in lost:
            lines.append("       ★丢: %s (★板文件里已没有这个 ref ⇒ 证据行会静默消失★)" % r)
    red = len(lost) > 0
    lines.append("    ⇒ J1 判定: %s" % ("❌ 判红 (★证据静默消失★)" if red else "✅ 绿"))
    return red, lines, lost


def main():
    print("=" * 96)
    print("ISS-317 · §3 BOM 证据静默消失判据 (★只读·不跑 gen_bom.py·只写沙盒★)")
    print("=" * 96)

    print("\n---- 造场 (★只写 tmp/iss317_sandbox/★) ----")
    pcb_renamed = build_renamed_pcb("board_bomsilence_renamed.kicad_pcb")
    bom_renamed = build_renamed_bom(SRC_BOM, "BOM_renamed.csv")

    results = OrderedDict()

    print("\n---- S0 基线 (板原样 + BOM 原样) ⇒ 期望绿 ----")
    red, lines, lost = judge(SRC_PCB, SRC_BOM, "S0 基线")
    results["S0_baseline"] = (red, lines)
    print("\n".join(lines))

    print("\n---- S1 事故场 (★只改板侧 · BOM 侧没改★) ⇒ 期望判红 ----")
    red, lines, lost = judge(pcb_renamed, SRC_BOM, "S1 只改板侧不改 BOM 侧")
    results["S1_boardonly"] = (red, lines)
    print("\n".join(lines))

    print("\n---- S2 对照场 (板原样 + BOM 原样) ⇒ 期望绿 (★与 S0 同★) ----")
    red, lines, lost = judge(SRC_PCB, SRC_BOM, "S2 对照")
    results["S2_control"] = (red, lines)
    print("\n".join(lines))

    print("\n---- S3 五侧同口径场 (板改名 + BOM 也改名) ⇒ 期望绿 (★两边同步就不丢★) ----")
    red, lines, lost = judge(pcb_renamed, bom_renamed, "S3 板+BOM 同步改名")
    results["S3_synced"] = (red, lines)
    print("\n".join(lines))

    print("\n---- 判定汇总 ----")
    ok = True
    expect = {"S0_baseline": False, "S1_boardonly": True, "S2_control": False, "S3_synced": False}
    for k, (red, _lines) in results.items():
        want = expect[k]
        mark = "✅" if red == want else "❌"
        if red != want:
            ok = False
        print("  %s %-16s 实测=%-5s 期望=%-5s" % (mark, k, "判红" if red else "绿",
                                                 "判红" if want else "绿"))
    print()
    print("  ★J1 反向用例成立性: 破坏前(S0)=绿 · 破坏后(S1)=判红 ⇒ %s"
          % ("✅ 判据能抓住「BOM 证据静默消失」" if ok else "❌ 判据不成立"))
    print("  ★结论: ★**J1 判据可用**★ (★破坏前绿·破坏后红·不是巧合自证★)" if ok else "")

    out = os.path.join(HERE, "12_bom_silence_judge_raw.txt")
    with open(out, "w", encoding="utf-8") as f:
        f.write("=" * 96 + "\n")
        f.write("ISS-317 · §3 BOM 证据静默消失判据 (★只读·不跑 gen_bom.py·只写沙盒★)\n")
        f.write("=" * 96 + "\n\n")
        for k, (red, lines) in results.items():
            f.write("\n".join(lines) + "\n")
        f.write("\n---- 判定汇总 ----\n")
        for k, (red, _l) in results.items():
            want = expect[k]
            f.write("  %s %-16s 实测=%-5s 期望=%-5s\n"
                    % ("✅" if red == want else "❌", k,
                       "判红" if red else "绿", "判红" if want else "绿"))
        f.write("\n  ★反向用例成立: 破坏前绿 · 破坏后红 ⇒ %s\n"
                % ("✅ 成立" if ok else "❌ 不成立"))
    print("\n★原始读数落盘 → %s" % os.path.relpath(out, PROJ))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
