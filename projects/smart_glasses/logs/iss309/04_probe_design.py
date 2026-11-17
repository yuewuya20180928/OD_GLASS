#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-309 · sw-lead · 设计验证探针 (★只在 /tmp 临时树上跑 · 真盘零写★)

场景:
  P0 修前 R4 现状复现 (合成台账只放网表行+脚表行)      ⇒ 期望红 (硬保护查不到)
  P1 R4 修法: 合成台账补上【板 / .kicad_pro 保护基线登记】 ⇒ 期望绿
  P2 R5a 新设计: 合成台账 + 锚点副本对齐到链头 + 改坏链头落表单号 ⇒ 期望红 (锚点副本落表单号对不上)
  P3 ★覆盖缺口★: 真台账 + 锚点副本停在历史值 + 改坏链头落表单号 ⇒ 期望绿 (★漏放★)
"""
import copy
import importlib.util
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(HERE))          # .../smart_glasses


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


gate = _load("gate", os.path.join(PROJ, "SW", "tools", "check_demo_panel_spec.py"))
st = _load("st", os.path.join(PROJ, "SW", "tools", "check_demo_panel_spec_r6_selftest.py"))

NET = "HW/netlist_v1.csv"
PINS = "HW/netlist_v1_pins.csv"
BOARD = "HW/PCB/demo_mainboard.kicad_pcb"
PRO = "HW/PCB/demo_mainboard.kicad_pro"


def build(tmp, root, name):
    work = os.path.join(tmp, name)
    for rel in st.TREE_FILES:
        src = os.path.join(root, rel)
        dst = os.path.join(work, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
    return work


def anchor_entry(anchors, rel):
    for e in ((anchors.get("source_ledger") or {}).get("entries") or []):
        if str(e.get("file") or "") == rel:
            return e
    raise AssertionError("no anchor entry %s" % rel)


def synth_ledger(pairs, tag, hard_rows):
    lines = ["# %s落表台账 (★仅供反向用例★)" % tag, ""]
    for rel, recs in pairs:
        for i, r in enumerate(recs):
            iss = r.get("iss") or "★无单号★"
            lines.append("| %s %d | `%s` | `%s` | `%s` | %s | 说明 |"
                         % (tag, i, rel, r["prev"], r["new"], iss))
    for rel, base in hard_rows:
        lines.append("| %s h | `%s` | `%s` | `%s` | ★保护基线 (逐字节不变)★ | 说明 |"
                     % (tag, rel, base, base))
    return "\n".join(lines) + "\n"


def hard_rows_of(anchors):
    out = []
    for e in (anchors.get("hard_protected") or []):
        rel = str(e.get("file") or "")
        base = str(e.get("md5") or "")
        if rel and base:
            out.append((rel, base))
    return out


def corrupt_head_ticket(text, rel, bogus="ISS-999"):
    """把【产出链头的那些行】的落表单号全部改坏 ⇒ 链头产出单号里不再有原单号。"""
    base = os.path.basename(rel)
    head = gate.sw_ledger_state(rel, text)["head"]
    lines = text.splitlines()
    heading_idx = -1
    touched = []
    for i, ln in enumerate(lines):
        s = ln.strip()
        if s.startswith("#"):
            heading_idx = i
            continue
        if not (s.startswith("|") and (rel in s or base in s)):
            continue
        prev, new = st.rec_of_line(ln)
        if new != head:
            continue
        if re.search(r"ISS-\d+", s):
            touched.append(("row", i))
        else:
            touched.append(("head", heading_idx))
    out = list(lines)
    seen = set()
    for kind, idx in touched:
        if idx < 0 or (kind, idx) in seen:
            continue
        seen.add((kind, idx))
        out[idx] = re.sub(r"ISS-\d+", bogus, out[idx], count=1)
    return ("\n".join(out) + "\n", len(touched), head)


def show(tag, fails):
    print("  %s ⇒ %s" % (tag, ("★绿 (无红项)★" if not fails else "")))
    for f in fails:
        print("      - %s" % f)


def main():
    root = PROJ
    base_led = gate.read_text(root, gate.LEDGER_CANON)
    recs_net = gate.sw_ledger_records(base_led, NET)
    recs_pins = gate.sw_ledger_records(base_led, PINS)
    stt = gate.sw_ledger_state(NET, base_led)
    head = stt["head"]
    print("链头 = %s · producer[head] = %s · 记录数 net=%d pins=%d"
          % (head, sorted(stt["producer"][head]), len(recs_net), len(recs_pins)))
    for r in recs_net:
        if r["new"] == head:
            print("  产出链头的记录: iss=%s prev=%s row=%s" % (r["iss"], r["prev"], r["row"][:110]))
    with tempfile.TemporaryDirectory(prefix="iss309_probe_") as tmp:
        # ---------------- P0: 修前 R4 现状 ----------------
        work = build(tmp, root, "p0")
        anchors, err = gate.load_sw_anchor(work)
        synth = synth_ledger([(NET, list(reversed(recs_net))), (PINS, list(reversed(recs_pins)))],
                             "乱序", [])
        st.rd  # noqa
        with open(os.path.join(work, gate.LEDGER_CANON), "w", encoding="utf-8") as f:
            f.write(synth)
        show("P0 修前 R4 现状 (合成台账缺保护基线登记)", gate.run_all(work, skip_md5=False,
                                                                  anchor=copy.deepcopy(anchors)))
        # ---------------- P1: R4 修法 ----------------
        work = build(tmp, root, "p1")
        anchors, err = gate.load_sw_anchor(work)
        synth = synth_ledger([(NET, list(reversed(recs_net))), (PINS, list(reversed(recs_pins)))],
                             "乱序", hard_rows_of(anchors))
        with open(os.path.join(work, gate.LEDGER_CANON), "w", encoding="utf-8") as f:
            f.write(synth)
        s2 = gate.sw_ledger_state(NET, synth)
        s2p = gate.sw_ledger_state(PINS, synth)
        print("  P1 自证: 乱序后链头 net=%s pins=%s (原 %s / %s)"
              % (s2["head"], s2p["head"], head, gate.sw_ledger_state(PINS, base_led)["head"]))
        show("P1 R4 修法 (补上保护基线登记)", gate.run_all(work, skip_md5=False,
                                                        anchor=copy.deepcopy(anchors)))
        # ---------------- P2: R5a 新设计 ----------------
        work = build(tmp, root, "p2")
        anchors, err = gate.load_sw_anchor(work)
        hr = hard_rows_of(anchors)
        synth = synth_ledger([(NET, recs_net), (PINS, recs_pins)], "改单号", hr)
        # 锚点副本对齐到链头 (= 一次刚落完表的状态)
        e = anchor_entry(anchors, NET)
        orig = sorted(gate.sw_ledger_state(NET, synth)["producer"][head])
        head_rec = next(r for r in recs_net if r["new"] == head)
        e["md5"] = gate.md5_of(work, NET)
        e["by"] = orig[0]
        e["prev_md5"] = head_rec["prev"]
        print("  P2 自证: 锚点副本已对齐到链头 (md5=%s by=%s prev=%s) · producer[head]=%s"
              % (e["md5"][:12], e["by"], e["prev_md5"], orig))
        show("P2a 对齐后 (改坏之前) 应绿", gate.run_all(work, skip_md5=False,
                                                    anchor=copy.deepcopy(anchors)))
        broken, n, h2 = corrupt_head_ticket(synth, NET)
        print("  P2 改坏处数 = %d" % n)
        with open(os.path.join(work, gate.LEDGER_CANON), "w", encoding="utf-8") as f:
            f.write(broken)
        s3 = gate.sw_ledger_state(NET, broken)
        print("  P2 自证: 链头=%s · producer[head]=%s · head_iss=%s"
              % (s3["head"], sorted(s3["producer"][s3["head"]]), s3["head_iss"]))
        show("P2b R5a 新设计 (改坏链头落表单号)", gate.run_all(work, skip_md5=False,
                                                          anchor=copy.deepcopy(anchors)))
        # ---------------- P3: 覆盖缺口 (锚点副本停在历史值) ----------------
        work = build(tmp, root, "p3")
        anchors, err = gate.load_sw_anchor(work)
        broken3, n3, h3 = corrupt_head_ticket(base_led, NET)
        print("  P3 真台账改坏处数 = %d · 原 producer[head]=%s"
              % (n3, sorted(stt["producer"][head])))
        with open(os.path.join(work, gate.LEDGER_CANON), "w", encoding="utf-8") as f:
            f.write(broken3)
        s4 = gate.sw_ledger_state(NET, broken3)
        print("  P3 自证: 链头=%s · producer[head]=%s"
              % (s4["head"], sorted(s4["producer"][s4["head"]])))
        show("P3 ★覆盖缺口★: 锚点副本停在历史值 + 链头落表单号被改坏",
             gate.run_all(work, skip_md5=False, anchor=copy.deepcopy(anchors)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
