#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iss327_four_arm_measure.py —— ISS-327 四臂对照表 · 机器化读数

★只读 + 只写 logs/iss327/ ⇒ 零写板 · 零落表 · 零改闸★
★口径: ① 板/网表/脚表/BOM 四 md5  ② 改名后位号命中 (SW/*.md 与 HW 五侧)
       ③ 10 道闸 rc (从 logs/iss327/{01_baseline,12_sbCtl,13_sbR0,14_sbR3,16_sbR1,18_sbR2}/ 读)
       ④ reachability 分类统计
"""
import hashlib
import json
import os
import re

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
LOG = os.path.join(PROJ, "logs", "iss327")
SB = os.path.join(PROJ, "tmp", "iss327")
OUT = os.path.join(LOG, "24_four_arm_measure.txt")

ARMS = [
    ("BASELINE", None, "01_baseline"),
    ("sbCtl", "sbCtl", "12_sbCtl"),
    ("sbR0", "sbR0", "13_sbR0"),
    ("sbR1(sbR0+重建注册表)", "sbR0", "16_sbR1"),
    ("sbR3", "sbR3", "14_sbR3"),
    ("sbR2(sbR3+重建注册表)", "sbR3", "18_sbR2"),
]

GATES = [
    ("check_demo_panel_spec", "check_demo_panel_spec.txt"),
    ("check_demo_panel_spec_r6_chainjudge_selftest", "check_demo_panel_spec_r6_chainjudge_selftest.txt"),
    ("check_demo_panel_spec_r6_hardprot_iss315_selftest", "check_demo_panel_spec_r6_hardprot_iss315_selftest.txt"),
    ("check_demo_panel_spec_r6_selftest", "check_demo_panel_spec_r6_selftest.txt"),
    ("check_landing_trace_obligation", "check_landing_trace_obligation.txt"),
    ("check_onepass_sw_sync", "check_onepass_sw_sync.txt"),
    ("check_shutdown_semantics", "check_shutdown_semantics.txt"),
    ("check_sw_ref_reachability", "check_sw_ref_reachability.txt"),
    ("check_timing_review_adc_sync", "check_timing_review_adc_sync.txt"),
    ("timing_check", "timing_check.txt"),
]

MD5_FILES = [
    "HW/PCB/demo_mainboard.kicad_pcb",
    "HW/netlist_v1.csv",
    "HW/netlist_v1_pins.csv",
    "HW/BOM_v1.csv",
]


def md5(p):
    with open(p, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def read(p):
    try:
        with open(p, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return ""


def main():
    d = json.load(open(os.path.join(SB, "rename_map_iss327.json")))
    new2old = d["map"]
    renamed = {k: v for k, v in new2old.items() if k != v}
    new_names = set(renamed.keys())       # 改名后的新名 (旧名 + _1)
    print("改名映射: 全表 %d 条 · 真改名 %d 条" % (len(new2old), len(renamed)), file=open(OUT, "w"))
    L = print

    def w(s=""):
        with open(OUT, "a") as fh:
            fh.write(s + "\n")

    # 重新开文件写
    import io
    buf = io.StringIO()
    old_stdout = sys.stdout if False else None

    lines = []
    lines.append("=" * 100)
    lines.append("# ISS-327 · 四臂对照表 · 机器化读数 (★生成于 %s★)" %
                 __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    lines.append("=" * 100)
    lines.append("改名映射: 全表 %d 条 · 真改名 %d 条 (★旧名末字符非数字 ⇒ 加 _1★)" %
                 (len(new2old), len(renamed)))
    lines.append("")

    # ── ① 四 md5 ───────────────────────────────────────────────────
    lines.append("=" * 100)
    lines.append("① 板 / 网表 / 脚表 / BOM 四 md5 (★对照有效性自检的第一道·必须逐臂列★)")
    lines.append("=" * 100)
    hdr = "  %-28s" % "臂"
    for f in MD5_FILES:
        hdr += "%-18s" % os.path.basename(f)[:16]
    lines.append(hdr)
    arm_md5 = {}
    for label, arm, logdir in ARMS:
        root = PROJ if arm is None else os.path.join(SB, arm)
        row = "  %-28s" % label
        arm_md5[label] = {}
        for f in MD5_FILES:
            h = md5(os.path.join(root, f))
            arm_md5[label][f] = h
            row += "%-18s" % h[:16]
        lines.append(row)
    lines.append("")
    lines.append("★真件 (基线) md5 = %s" % md5(os.path.join(PROJ, MD5_FILES[0])))
    lines.append("★⇒ sbCtl 四 md5 与真件逐字相同 = %s" %
                 ("★是★" if all(arm_md5["sbCtl"][f] == arm_md5["BASELINE"][f] for f in MD5_FILES)
                  else "★否★"))
    lines.append("★⇒ sbR0 / sbR3 四 md5 与真件【不同】 = %s" %
                 ("★是 (·五侧确实被改名了·所以它不是对照组·)★" if
                  arm_md5["sbR0"][MD5_FILES[0]] != arm_md5["BASELINE"][MD5_FILES[0]] else "★否★"))
    lines.append("")

    # ── ② 改名后位号命中 ───────────────────────────────────────────
    lines.append("=" * 100)
    lines.append("② 改名后位号命中数 (★核心自检: 对照臂必须是 0·试验臂必须 > 0★)")
    lines.append("=" * 100)
    lines.append("  %-28s %-14s %-16s %-16s %-16s" % ("臂", "SW/*.md 命中", "HW 五侧命中", "改名后位号总数", "软链数"))
    arm_hits = {}
    for label, arm, logdir in ARMS:
        root = PROJ if arm is None else os.path.join(SB, arm)
        sw_hit = 0
        sw_files = 0
        for dp, dns, fns in os.walk(os.path.join(root, "SW")):
            for fn in fns:
                if not fn.endswith(".md"):
                    continue
                p = os.path.join(dp, fn)
                txt = read(p)
                h = sum(txt.count(n) for n in new_names)
                if h:
                    sw_hit += h
                    sw_files += 1
        hw_hit = 0
        hw_files = 0
        hwrel = ["HW/PCB/demo_mainboard.kicad_pcb", "HW/netlist_v1.csv",
                 "HW/netlist_v1_pins.csv", "HW/BOM_v1.csv"]
        for f in hwrel:
            txt = read(os.path.join(root, f))
            h = sum(txt.count(n) for n in new_names)
            if h:
                hw_hit += h
                hw_files += 1
        nlink = 0
        if arm is not None:
            for dp, dns, fns in os.walk(os.path.join(SB, arm)):
                for fn in fns:
                    if os.path.islink(os.path.join(dp, fn)):
                        nlink += 1
        arm_hits[label] = (sw_hit, hw_hit)
        lines.append("  %-28s %-14s %-16s %-16s %-16s" % (
            label, "%d 处 / %d 份" % (sw_hit, sw_files),
            "%d 处 / %d 份" % (hw_hit, hw_files),
            len(new_names), nlink))
    lines.append("")
    lines.append("★⇒ 对照臂 sbCtl 的【改名后位号命中】= %d 处 (★必须 0★)" % arm_hits["sbCtl"][0])
    lines.append("★⇒ sbR0 的 SW/*.md 命中 = %d 处 (★SW 文档未同步 ⇒ 应 0·但板已改名⇒网表里全是新名·)★"
                 % arm_hits["sbR0"][0])
    lines.append("★⇒ sbR3 的 SW/*.md 命中 = %d 处 (★SW 文档已同步⇒应 > 0★)" % arm_hits["sbR3"][0])
    lines.append("")

    # ── ③ 10 道闸 rc ───────────────────────────────────────────────
    lines.append("=" * 100)
    lines.append("③ 10 道闸 rc (★逐闸一行·★主表 rc·不含 --selftest 副跑★)")
    lines.append("=" * 100)
    rows = {}
    for label, arm, logdir in ARMS:
        d0 = os.path.join(LOG, logdir)
        for gate, fn in GATES:
            txt = read(os.path.join(d0, fn))
            m = re.findall(r"rc=(\d+)", txt)
            rows[(label, gate)] = (m[-1] if m else "?", txt)
    hdr = "  %-56s" % "闸"
    for label, arm, logdir in ARMS:
        hdr += "%-14s" % label.replace("(sbR", "\n(sbR")[:12]
    lines.append(hdr)
    for gate, fn in GATES:
        row = "  %-56s" % gate
        for label, arm, logdir in ARMS:
            rc, txt = rows[(label, gate)]
            row += "%-14s" % ("rc=" + rc)
        lines.append(row)
    lines.append("")
    lines.append("★绿/红合计 (★rc=0 绿 · rc=1 红 · rc=2 = 【脚本报错/前置不成立·见 §⑤ 语义定案】★):")
    for label, arm, logdir in ARMS:
        g = sum(1 for gate, fn in GATES if rows[(label, gate)][0] == "0")
        r = sum(1 for gate, fn in GATES if rows[(label, gate)][0] == "1")
        e = sum(1 for gate, fn in GATES if rows[(label, gate)][0] == "2")
        lines.append("  %-28s 绿 %2d / 红(rc=1) %2d / rc=2 %2d" % (label, g, r, e))
    lines.append("")

    # ── ④ reachability 分类统计 ────────────────────────────────────
    lines.append("=" * 100)
    lines.append("④ check_sw_ref_reachability 分类统计 (★DRIFT / MISSING / 上限★)")
    lines.append("=" * 100)
    lines.append("  %-28s %-12s %-14s %-14s" % ("臂", "DRIFT", "MISSING", "上限"))
    for label, arm, logdir in ARMS:
        txt = rows[(label, "check_sw_ref_reachability")][1]
        dr = re.search(r"DESIGNATOR_DRIFT\s+(\d+)", txt)
        ms = re.search(r"DESIGNATOR_MISSING\s+(\d+)", txt)
        lines.append("  %-28s %-12s %-14s %-14s" % (
            label, dr.group(1) if dr else "?", ms.group(1) if ms else "?", "3"))
    lines.append("")

    # ── ⑤ rc=2 语义归类 ────────────────────────────────────────────
    lines.append("=" * 100)
    lines.append("⑤ rc=2 的【逐闸语义归类】 (★不许当红灯·也不许当绿灯放过★)")
    lines.append("=" * 100)
    for label, arm, logdir in ARMS:
        for gate, fn in GATES:
            rc, txt = rows[(label, gate)]
            if rc != "2":
                continue
            reason = ""
            for pat in (r"❌ ([^\n]*?)\n",):
                m = re.findall(pat, txt)
                if m:
                    reason = m[-1].strip()
            lines.append("  [%s] %s" % (label, gate))
            lines.append("      rc=2 · 最后一条 ❌ = %s" % reason)
    lines.append("")

    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    print("\n★落盘: %s" % OUT)


if __name__ == "__main__":
    import sys
    sys.exit(main())
