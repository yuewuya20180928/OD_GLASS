#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-354 · hw-lead · 「demo 主板可制造性收口」只读判定闸 (★本单自带的闸★)
=================================================================================================
派活: state/dispatch_briefs/ISS-354_hw_demo_board_manufacturability_closure.md (项目总工 2026-11-23)

★**本闸守的是「收口有没有真的落到文档里」, 不是板** ⇒ ★**零写板 · 零落表 · 零改既有闸** ★

四条判据 (★每条都要能当场判红, 不许是装饰★):
  C1 ★**5 个 ref 逐条点名**★ : 现封装 (★从板文件实读★) vs 查得的应为封装 (★从作业包改项清单读★)
                              ⇒ ★**逐条点名, 状态只认「已定位」/「仍未定位」**★
                              ⇒ ★**现封装必须与板文件逐字节吻合** ⇒ 文档过期 ⇒ 判红
  C2 ★**BOM 里 OPN 仍 `[0数据]` 的器件【名单】**★ : ★**列名单, 不许只报数**★
                              ⇒ 且与作业包 §9-6-5 登记的名单 ★**双向逐个比对**★ ⇒ 名单漂了判红
  C3 ★**预检页含「下料前一票否决项」**★ : `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 的 ISS-354 追加段
  C4 ★**作业包追加段含改项清单**★   : `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` 的 ISS-354 追加段

退出码: 0 = 四条判据全过 · 1 = 有不通过项 (★闸红★) · 2 = 用法错
用法:
  python3 HW/check_iss354_mfg_closure.py              # 主模式
  python3 HW/check_iss354_mfg_closure.py --selftest   # 反向用例 (★故意改坏临时副本·必须被抓出来★)

★**只读自证 (★本闸自己不许写项目盘·只读 + 只写 /tmp★)**★:
  ① 本脚本【只 open(..., "r")】读项目文件, ★**从不写**★ ⇒ 跑完项目盘零变化
  ② --selftest 的所有反向用例都在 ★**tempfile 临时副本**★ 上做 ⇒ 不碰项目盘
  ③ 本闸【不 import / 不修改】任何既有闸 (`state/gate_check.py` / `state/merge.py` /
     `HW/check_onepass_preflight_coverage.py` / `HW/check_preflight_regen_idempotent.py` 一个字未改)

★**自检用 env 覆盖 (★让 --selftest 能换到临时副本★)**:
  ISS354_PCB       板文件     (默认 = PROJ/HW/PCB/demo_mainboard.kicad_pcb)
  ISS354_WORKPACKET 作业包页   (默认 = PROJ/HW/PCB/BOARD_ONEPASS_WORKPACKET.md)
  ISS354_PREFLIGHT  预检页     (默认 = PROJ/HW/PCB/BOARD_ONEPASS_PREFLIGHT.md)
  ISS354_BOM        BOM 表     (默认 = PROJ/HW/BOM_v1.csv)
"""
from __future__ import annotations

import argparse
import csv
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)

PCB = os.environ.get("ISS354_PCB") or os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb")
WORKPACKET = os.environ.get("ISS354_WORKPACKET") or os.path.join(PROJ, "HW", "PCB", "BOARD_ONEPASS_WORKPACKET.md")
PREFLIGHT = os.environ.get("ISS354_PREFLIGHT") or os.path.join(PROJ, "HW", "PCB", "BOARD_ONEPASS_PREFLIGHT.md")
BOM = os.environ.get("ISS354_BOM") or os.path.join(PROJ, "HW", "BOM_v1.csv")

# ★**本单点名的 5 个 ref (★顺序 = 交卷页里的点名顺序·不许只报数★)** ★
REFS = ("Q1", "Q2", "U_BATPROT", "U_LDO_S28", "U_SUPV")

# ★**ISS-354 追加段的锚点 (★作业包 / 预检页两边各一个★)** ★
WP_SECTION = "§9-6"
WP_CHANGELIST_TOKEN = "改项清单"
PF_VETO_TOKEN = "下料前一票否决项"
ISS_TAG = "ISS-354"

ok = True


def _fail(msg):
    global ok
    ok = False
    print("  FAIL  %s" % msg)


def _pass(msg):
    print("  OK    %s" % msg)


# ==============================================================================
# 板文件读取 (★只读·自绘封装逐参数实测★)
# ==============================================================================
def read_board_footprints(path):
    """★把板文件里每个封装的焊盘数 / 焊盘编号 / 焊盘尺寸 / 外形尺寸读出来 ★

    ★**只读**: 纯 open(path, "r") ⇒ 项目盘零写入 ★
    """
    with open(path, encoding="utf-8", errors="replace") as fh:
        lines = fh.read().split("\n")
    starts = [i for i, l in enumerate(lines) if l.strip().startswith("(footprint ")]
    out = {}
    for si in starts:
        depth = 0
        ei = si
        for j in range(si, len(lines)):
            s = lines[j]
            depth += len(re.findall(r"\(", s)) - len(re.findall(r"\)", s))
            if depth == 0 and j > si:
                ei = j
                break
        blk = "\n".join(lines[si:ei + 1])
        m = re.search(r'\(property "Reference" "([^"]+)"', blk)
        if not m:
            continue
        ref = m.group(1)
        pads = re.findall(
            r'\(pad "([^"]+)" (\S+) (\S+)\s*\n\s*\(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)'
            r'\s*\n\s*\(size ([-\d.]+) ([-\d.]+)\)', blk)
        vals = re.search(r'\(property "Value" "([^"]*)"', blk)
        out[ref] = {
            "pads": [(p[0], float(p[3]), float(p[4]), p[6], p[7]) for p in pads],
            "value": vals.group(1) if vals else "",
        }
    return out


# ==============================================================================
# 作业包 / 预检页读取
# ==============================================================================
def read_text(path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def workpacket_section(text):
    """★切出作业包页的 ISS-354 追加段 (★从 §9-6 到文末 / 到下一个 #### 段★) ★"""
    i = text.find(WP_SECTION)
    if i < 0:
        return ""
    m = re.search(r"\n#### §9-7", text[i:])
    if m:
        return text[i:i + m.start()]
    return text[i:]


def workpacket_ref_chunk(section, ref):
    """★切出作业包里某个 ref 的改项清单小节 (★`##### … `REF` …` 到下一个 `#####`★) ★"""
    pat = re.compile(r"^#####.*`%s`" % re.escape(ref), re.M)
    m = pat.search(section)
    if not m:
        return ""
    rest = section[m.end():]
    m2 = re.search(r"^#####", rest, re.M)
    return section[m.start(): m.end() + (m2.start() if m2 else len(rest))]


def cell(chunk, label):
    """★从一个 markdown 表格行里取第 2 格 (★行首是 `| 标签 |`★) ★"""
    for line in chunk.split("\n"):
        if line.strip().startswith("|") and label in line:
            parts = [p.strip() for p in line.strip().strip("|").split("|")]
            if len(parts) >= 2:
                return parts[1]
    return ""


def workpacket_bom_list(section):
    """★从作业包 §9-6-5 的表里读出登记的 `[0数据]` 器件名单 ★"""
    names = []
    for line in section.split("\n"):
        m = re.match(r"^\|\s*(\d+)\s*\|\s*`([A-Za-z0-9_]+)`\s*\|", line)
        if m:
            names.append(m.group(2))
    return names


# ==============================================================================
# C1 · 5 个 ref 逐条点名
# ==============================================================================
def check_c1(board, wp_section):
    print("\n[C1] ★5 个 ref 逐条点名 (★现封装 [实测·板文件] vs 应为封装 [查得]★)★")
    if not wp_section:
        _fail("作业包里找不到 ISS-354 追加段 (★锚点 `%s`·★追加段被冲掉了★)" % WP_SECTION)
        return
    located, unlocated = [], []
    for ref in REFS:
        fp = board.get(ref)
        if not fp:
            _fail("%s: ★板文件里找不到这个封装★" % ref)
            unlocated.append(ref)
            continue
        nums = ",".join(p[0] for p in fp["pads"])
        sizes = sorted(set((p[3], p[4]) for p in fp["pads"]))
        chunk = workpacket_ref_chunk(wp_section, ref)
        if not chunk:
            _fail("%s: ★作业包改项清单里没有这一条★ ⇒ 仍未定位" % ref)
            unlocated.append(ref)
            print("        现封装[实测] = %d 焊盘 编号 %s 焊盘 %s" % (len(fp["pads"]), nums, sizes))
            continue
        cur = cell(chunk, "现封装 (板文件实测)")
        should = cell(chunk, "应为封装")
        must = cell(chunk, "下料前必须核对")
        # ★现封装必须与盘面吻合 (★文档过期 ⇒ 红★)
        stale = []
        if nums not in cur:
            stale.append("焊盘编号(%s) 与盘面不符" % nums)
        for (w, h) in sizes:
            if w not in cur or h not in cur:
                stale.append("焊盘尺寸(%sx%s) 与盘面不符" % (w, h))
        if stale:
            _fail("%s: ★现封装与板文件实测不符 ⇒ %s★ (★清单页已过期·不许当板侧输入★)" % (ref, "; ".join(stale)))
        if not should.strip():
            _fail("%s: ★「应为封装」为空 ⇒ 仍未定位★" % ref)
            unlocated.append(ref)
        elif "是" not in must:
            _fail("%s: ★「下料前必须核对」不是「是」⇒ 仍未定位★" % ref)
            unlocated.append(ref)
        else:
            located.append(ref)
            _pass("%s: 已定位 (★现封装 %d 焊盘 / 编号 %s / 焊盘 %s·★与盘面吻合★)" % (ref, len(fp["pads"]), nums, sizes))
        print("        应为封装 = %s" % (should[:110] + ("…" if len(should) > 110 else "")))
    print("  ---- C1 小计: 已定位 %d 个 (%s) / 仍未定位 %d 个 (%s)"
          % (len(located), ",".join(located) or "-", len(unlocated), ",".join(unlocated) or "-"))
    if unlocated:
        _fail("C1 判红: ★仍有 %d 个 ref 仍未定位: %s★" % (len(unlocated), ", ".join(unlocated)))
    else:
        _pass("C1 通过: ★5 个 ref 全部已定位且现封装与盘面吻合★")


# ==============================================================================
# C2 · BOM 里 OPN 仍 [0数据] 的器件名单
# ==============================================================================
def check_c2(wp_section):
    print("\n[C2] ★BOM 里 OPN 仍 `[0数据]` 的器件【名单】(★列名单·不许只报数★)★")
    if not os.path.exists(BOM):
        _fail("BOM 文件不存在: %s" % BOM)
        return
    with open(BOM, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    names = [r["ref"] for r in rows if (r.get("opn") or "").strip() == "[0数据]"]
    print("  ---- 盘面名单 (%d 个): %s" % (len(names), ", ".join(names)))
    reg = workpacket_bom_list(wp_section)
    if not reg:
        _fail("★作业包 §9-6-5 里没有登记 `[0数据]` 名单 ⇒ 判红★")
        return
    print("  ---- 作业包登记名单 (%d 个): %s" % (len(reg), ", ".join(reg)))
    miss = [n for n in names if n not in reg]
    extra = [n for n in reg if n not in names]
    if miss:
        _fail("★盘面有、作业包没登记: %s★" % ", ".join(miss))
    if extra:
        _fail("★作业包登记了、盘面已不是 `[0数据]`: %s★" % ", ".join(extra))
    if not miss and not extra:
        _pass("C2 通过: ★盘面与作业包登记的 `[0数据]` 名单逐个一致★")


# ==============================================================================
# C3 / C4 · 预检页一票否决项 / 作业包改项清单
# ==============================================================================
def check_c3():
    print("\n[C3] ★预检页追加段是否含「下料前一票否决项」★")
    txt = read_text(PREFLIGHT)
    if ISS_TAG not in txt:
        _fail("★预检页里找不到 %s 追加段 (★追加段被冲掉了·★必须经 sidecar 通道落地·不许手写进生成器产物页★)" % ISS_TAG)
        return
    if PF_VETO_TOKEN not in txt:
        _fail("★预检页的 %s 追加段里没有「%s」★" % (ISS_TAG, PF_VETO_TOKEN))
        return
    n = txt.count(PF_VETO_TOKEN)
    _pass("C3 通过: ★预检页含「%s」(%d 处)★" % (PF_VETO_TOKEN, n))


def check_c4(wp_section):
    print("\n[C4] ★作业包追加段是否含改项清单★")
    if not wp_section:
        _fail("★作业包里找不到 ISS-354 追加段★")
        return
    if WP_CHANGELIST_TOKEN not in wp_section:
        _fail("★作业包追加段里没有「%s」★" % WP_CHANGELIST_TOKEN)
        return
    missing = [r for r in REFS if not workpacket_ref_chunk(wp_section, r)]
    if missing:
        _fail("★作业包改项清单里缺这些 ref 的逐条行: %s★" % ", ".join(missing))
        return
    _pass("C4 通过: ★作业包追加段含改项清单 + 5 个 ref 的逐条行★")


# ==============================================================================
# --selftest (★故意在临时副本里改坏一条 ⇒ 必须被抓出来★)
# ==============================================================================
def mutate_cell(text, ref, label, new_cell):
    """★把作业包里某个 ref 的某一格 (第 2 格) 改掉 ⇒ 返回新文本 (★改不到就原样返回·让用例自己失败★) ★

    ★**按行精确改**: 找到 `##### … `REF` …` 小节里第 1 个含 `label` 的表格行, 把它的第 2 格换成 `new_cell` ★
    """
    lines = text.split("\n")
    # ★先定位 ref 的小节起止 (★小节头 = `#####` 且含 `REF`★) ★
    start = None
    for i, l in enumerate(lines):
        if l.startswith("#####") and ("`%s`" % ref) in l:
            start = i
            break
    if start is None:
        return text
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("#####"):
            end = j
            break
    for i in range(start, end):
        l = lines[i]
        if l.strip().startswith("|") and label in l:
            parts = l.split("|")
            # ★markdown 行 = ['', cell1, cell2, ..., ''] ⇒ 第 2 格 = parts[2] ★
            if len(parts) >= 4:
                parts[2] = " " + new_cell + " "
                lines[i] = "|".join(parts)
                break
    return "\n".join(lines)


def selftest():
    print("=" * 100)
    print("  ISS-354 · 只读判定闸 · --selftest 反向用例 (★全部在临时副本上做·项目盘零写入★)")
    print("=" * 100)
    cases = []

    # R1: 删掉 Q1 的改项清单行 ⇒ C1 必须抓出「仍未定位」
    cases.append(("R1 删掉 `Q1` 的改项清单小节 ⇒ C1 判红", "c1_q1_missing", "Q1"))
    # R2: 把 U_LDO_S28 的「应为封装」清空 ⇒ C1 必须抓出
    cases.append(("R2 清空 `U_LDO_S28` 的「应为封装」⇒ C1 判红", "c1_should_empty", "U_LDO_S28"))
    # R3: 把 U_SUPV 的现封装改成与盘面不符 ⇒ C1 必须抓出「清单页过期」
    cases.append(("R3 把 `U_SUPV` 的现封装改成与盘面不符 ⇒ C1 判红 (★防清单页过期★)", "c1_stale", "U_SUPV"))
    # R4: 从预检页里删掉「下料前一票否决项」⇒ C3 必须抓出
    cases.append(("R4 删掉预检页里的「下料前一票否决项」⇒ C3 判红", "c3_token", None))
    # R5: 从作业包追加段里删掉「改项清单」⇒ C4 必须抓出
    cases.append(("R5 删掉作业包里的「改项清单」⇒ C4 判红", "c4_token", None))
    # R6: 从作业包登记名单里删掉一个 BOM 名字 ⇒ C2 必须抓出
    cases.append(("R6 从作业包登记的 `[0数据]` 名单里删掉一个 ⇒ C2 判红", "c2_missing", None))

    board = read_board_footprints(PCB)
    base_ok = run_all_quiet()
    print("\n  ---- 正例: 未改坏时必须 rc=0 ⇒ %s" % ("✔" if base_ok == 0 else "✘ 失败"))
    if base_ok != 0:
        print("  FAIL  ★正例就不绿 ⇒ selftest 无意义★")
        return 1

    for name, kind, ref in cases:
        with tempfile.TemporaryDirectory(prefix="iss354_selftest_") as td:
            wp = os.path.join(td, "wp.md")
            pf = os.path.join(td, "pf.md")
            bm = os.path.join(td, "bom.csv")
            shutil.copyfile(WORKPACKET, wp)
            shutil.copyfile(PREFLIGHT, pf)
            shutil.copyfile(BOM, bm)
            txt = open(wp, encoding="utf-8").read()
            if kind == "c1_q1_missing":
                i = txt.find("##### ① `Q1`")
                j = txt.find("##### ② `Q2`")
                txt = txt[:i] + txt[j:]
            elif kind == "c1_should_empty":
                txt = mutate_cell(txt, "U_LDO_S28", "应为封装", "")
            elif kind == "c1_stale":
                txt = mutate_cell(txt, "U_SUPV", "现封装 (板文件实测)", "★完全不对的数字 1,9,9★")
            elif kind == "c2_missing":
                txt = re.sub(r"^\|\s*\d+\s*\|\s*`X1`\s*\|.*$", "", txt, flags=re.M)
            elif kind == "c3_token":
                pf_txt = open(pf, encoding="utf-8").read()
                with open(pf, "w", encoding="utf-8") as fh:
                    fh.write(pf_txt.replace(PF_VETO_TOKEN, "被删掉"))
            elif kind == "c4_token":
                txt = txt.replace(WP_CHANGELIST_TOKEN, "被删掉")
            open(wp, "w", encoding="utf-8").write(txt)

            env = dict(os.environ)
            env["ISS354_WORKPACKET"] = wp
            env["ISS354_PREFLIGHT"] = pf
            env["ISS354_BOM"] = bm
            rc = run_in_env(env)
            verdict = "✔ 被抓出来" if rc != 0 else "✘ ★漏掉了★"
            print("  ---- %-58s ⇒ rc=%d  %s" % (name, rc, verdict))
            if rc == 0:
                print("  FAIL  ★反向用例没被抓出来 ⇒ 闸是装饰★")
                return 1
    print("\n  ✅ rc=0: ★正例绿 + %d 条反向用例全部被抓出来 (★闸不是装饰★)★" % len(cases))
    return 0


def run_all_quiet():
    """★跑一遍主模式 (★只回 rc·不打印·给 selftest 用★) ★"""
    global ok
    ok = True
    try:
        board = read_board_footprints(PCB)
        wp = workpacket_section(read_text(WORKPACKET))
        check_c1(board, wp)
        check_c2(wp)
        check_c3()
        check_c4(wp)
    except Exception as e:                      # noqa: BLE001
        ok = False
        print("  FAIL  闸自身异常: %r" % (e,))
    return 0 if ok else 1


def run_in_env(env):
    """★在给定 env 下跑主模式 (★子进程·不污染当前进程的 os.environ★) ★"""
    import subprocess
    p = subprocess.run([sys.executable, "-B", os.path.abspath(__file__)],
                       cwd=PROJ, env=env, capture_output=True, text=True)
    return p.returncode


def main():
    ap = argparse.ArgumentParser(description="ISS-354 demo 主板可制造性收口 · 只读判定闸")
    ap.add_argument("--selftest", action="store_true", help="★反向用例 (★故意改坏临时副本·必须被抓出来★)")
    args = ap.parse_args()

    print("=" * 100)
    print("  ISS-354 · 「demo 主板可制造性收口」只读判定闸 (★零写板·零落表·零改既有闸★)")
    print("=" * 100)
    print("  PCB        = %s" % PCB)
    print("  WORKPACKET = %s" % WORKPACKET)
    print("  PREFLIGHT  = %s" % PREFLIGHT)
    print("  BOM        = %s" % BOM)

    if args.selftest:
        return selftest()

    board = read_board_footprints(PCB)
    wp = workpacket_section(read_text(WORKPACKET))
    check_c1(board, wp)
    check_c2(wp)
    check_c3()
    check_c4(wp)

    print("\n" + "-" * 100)
    if ok:
        print("  ✅ rc=0: ★★C1 5 个 ref 全已定位 · C2 `[0数据]` 名单一致 · C3 一票否决项在场 · C4 改项清单在场 ★★")
        return 0
    print("  ❌ rc=1: ★★有判据不通过 (★见上·逐条点名★)★★")
    return 1


if __name__ == "__main__":
    sys.exit(main())
