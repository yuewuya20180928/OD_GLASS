#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-364 · 腿 B (网表节点具名) 作业包 + 两条腿的 C1/C4 影响 · 深算

★ 零写板 · 零落表 · 只读真源 + 只写 logs/iss364/
★ 输出 logs/iss364/12_legB_jobs.json / 13_legB_jobs.txt

核心口径 (与 state/check_pcb_nets.py 同源, 独立实现):
  · 网表行按 board 列过滤 ⇒ 只留 MAIN_PCB (C4 只看 MAIN_PCB)
  · bare 节点串 "DEV" ⇒ 占位脚号 (按【该器件 bare 网首次出现顺序】1..M)
  · 具名 "DEV pinN" ⇒ 真实脚号 N; 若该器件已有任一 pinN ⇒ 裸端续号 = max(pinN)+1
  · 真脚号真值来源 = HW/netlist_v1_pins.csv 的 `pin` 栏 (★表头名定位, 不写死列号★)
"""
import csv
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "logs", "iss361"))
import iss361_board_read as R  # noqa: E402

BOM = os.path.join(ROOT, "HW", "BOM_v1.csv")
NET = os.path.join(ROOT, "HW", "netlist_v1.csv")
PINS = os.path.join(ROOT, "HW", "netlist_v1_pins.csv")
PCB = os.path.join(ROOT, "HW", "PCB", "demo_mainboard.kicad_pcb")
OUT_JSON = os.path.join(HERE, "12_legB_jobs.json")
OUT_TXT = os.path.join(HERE, "13_legB_jobs.txt")

PSEUDO = ("RAIL_", "NET_")
BOARD_FILTER = "MAIN_PCB"


def main():
    bom_rows = R.load_bom(BOM)
    bom = {r["ref"]: r for r in bom_rows}
    main_t, chg_t, total_t = R.iss356_targets(bom_rows)
    ph, per_ref, notes = R.netlist_placeholder(NET)
    board = R.read_board(PCB)
    c4 = set(ph)
    inter = c4 & set(total_t)
    gap = R.coverage_gap(bom_rows, c4)
    targets = sorted(inter) + sorted(gap)

    # ---- 脚表: (ref, net) -> pin  (★按表头名取栏, 不写死列号★)
    with open(PINS, encoding="utf-8") as fh:
        preader = csv.DictReader(fh)
        pin_hdr = preader.fieldnames
        assert "pin" in pin_hdr and "ref" in pin_hdr and "net" in pin_hdr, pin_hdr
        pin_of = {}
        pins_by_ref = {}
        for r in preader:
            ref = (r.get("ref") or "").strip()
            pin = (r.get("pin") or "").strip()
            net = (r.get("net") or "").strip()
            if not ref or not pin:
                continue
            pin_of.setdefault((ref, net), set()).add(pin)
            pins_by_ref.setdefault(ref, []).append({"pin": pin, "net": net})

    # ---- 网表行
    with open(NET, encoding="utf-8") as fh:
        nreader = csv.DictReader(fh)
        net_hdr = nreader.fieldnames
        all_rows = list(nreader)
    for i, r in enumerate(all_rows):
        r["_lineno"] = i + 2          # CSV 物理行号 (含表头行)
        r["_datarow"] = i + 1        # 数据行序号 (1-based)

    jobs = []
    for ref in targets:
        bd = board.get(ref)
        # ---- 板面 pad -> net
        board_pads = []
        for p in (bd["pads"] if bd else []):
            board_pads.append({"num": p[0], "net": p[1]})
        # ---- 该器件在网表里所有以 bare 形态出现的行
        # ★★只取 board==MAIN_PCB 的行★★ (state/check_pcb_nets.py 的 C4 口径先按 board 列过滤 ⇒
        #   CHG_BOARD 行的行序不参与占位脚号编号) ⇒ 跨板行的存在必须单独登记
        bare_hits = []
        offboard_hits = []
        for r in all_rows:
            for col in ("node1", "node2"):
                node = (r.get(col) or "").strip()
                if not node:
                    continue
                comp, tail = R.split_node(node)
                if comp != ref:
                    continue
                if tail and R.is_pad_name(tail):
                    continue
                if tail:
                    continue
                rec = {"lineno": r["_lineno"], "datarow": r["_datarow"],
                       "col": col, "net": (r.get("net") or "").strip(),
                       "board": (r.get("board") or "MAIN_PCB").strip(),
                       "node_other": (r.get("node2" if col == "node1" else "node1") or "").strip()}
                if rec["board"] == BOARD_FILTER:
                    bare_hits.append(rec)
                else:
                    offboard_hits.append(rec)
        # ---- 占位脚号顺序: bare 网首次出现顺序 (去重后) ⇒ 1..M
        order = []
        for h in bare_hits:
            if h["net"] not in order:
                order.append(h["net"])
        # ---- 具名脚真值 (脚表)
        truth = sorted(pins_by_ref.get(ref, []), key=lambda x: (len(x["pin"]), x["pin"]))
        truth_map = {t["net"]: t["pin"] for t in truth}
        # ---- 逐 bare 命中给出改名指令 (★每一处 bare 出现都要改名★ ——
        #      同一 (ref,net) 出现多次时全部改成同一个 pinN: 网表侧按 (器件,网) 去重,
        #      重复的裸端若已被编号脚覆盖会被自动吸收 ⇒ 不会多占焊盘)
        renames = []
        for h in bare_hits:
            pins = sorted(pin_of.get((ref, h["net"]), []))
            if not pins:
                renames.append({**h, "new_node": None, "pin": None,
                                "note": "★脚表里没有 (ref,net) 这一行 ⇒ 需人工定 pin"})
                continue
            renames.append({**h, "new_node": "%s pin%s" % (ref, pins[0]), "pin": pins[0],
                            "all_pins": pins})
        # ---- 脚表有、但网表里该器件没以 bare 形态出现的脚 ⇒ 需补行
        add_rows = []
        bare_nets = set(order)
        for t in truth:
            if t["net"] in bare_nets:
                continue
            # 该脚在网表里以什么形态存在? 找 node1/node2 含该 ref 但已具名/或完全缺失
            add_rows.append({"net": t["net"], "pin": t["pin"], "ref": ref,
                             "suggest_node1": "%s pin%s" % (ref, t["pin"]),
                             "suggest_node2": "GND" if t["net"] == "GND" else "<该网另一端器件>",
                             "board": bom[ref]["board"],
                             "value": bom[ref]["value"], "type": bom[ref]["type"],
                             "footprint": "", "opn": bom[ref]["opn"]})
        # ---- 板面 pad 序 vs 脚表 pin 序 (★按【焊盘号 → 脚号 → 真值网】比对★)
        net_of_pin = {}
        for t in truth:
            net_of_pin[t["pin"]] = t["net"]
        pad_vs_truth = []
        for bp in board_pads:
            want = net_of_pin.get(bp["num"])
            pad_vs_truth.append({"pad": bp["num"], "net": bp["net"],
                                 "truth_net_of_this_pad": want,
                                 "match": (want == bp["net"]) if want is not None else None})
        # ---- 占位脚序 (网表) vs 板面 pad 序
        occ = []
        for i, n in enumerate(order, start=1):
            occ.append({"occ_pad": i, "net": n})
        occ_vs_board = []
        for o in occ:
            bp = next((x for x in board_pads if x["net"] == o["net"]), None)
            occ_vs_board.append({"occ_pad": o["occ_pad"], "net": o["net"],
                                 "board_pad": bp["num"] if bp else None,
                                 "match": (bp is not None and bp["num"] == str(o["occ_pad"]))})
        jobs.append({
            "ref": ref,
            "bucket": "靶内" if ref in inter else "缺口",
            "c4_placeholder_pads": ph.get(ref, 0),
            "board_pad_n": len(board_pads),
            "board_pads": board_pads,
            "bare_nets_order": order,
            "truth_pins": truth,
            "renames": renames,
            "add_rows": add_rows,
            "offboard_hits": offboard_hits,
            "pad_vs_truth": pad_vs_truth,
            "occ_vs_board": occ_vs_board,
            "n_rename": len([x for x in renames if x.get("new_node")]),
            "n_add": len(add_rows),
            "n_total_legs": len([x for x in renames if x.get("new_node")]) + len(add_rows),
        })

    data = {"counts": {"c4_total": len(c4), "targets": len(targets),
                       "inter": len(inter), "gap": len(gap)},
            "pin_table_header": pin_hdr,
            "netlist_header": net_hdr,
            "jobs": jobs}
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=1)

    T = []
    A = T.append
    A("=== ISS-364 腿 B 作业包 (逐件) ===")
    A("脚表表头: %s" % pin_hdr)
    A("网表表头: %s" % net_hdr)
    A("")
    tot_r = tot_a = 0
    mismatch = []
    for j in jobs:
        A("--- %s (%s) · 占位脚 %d · 板 pad %d" % (j["ref"], j["bucket"],
                                                    j["c4_placeholder_pads"], j["board_pad_n"]))
        A("    板 pad→网: %s" % ", ".join("%s=%s" % (b["num"], b["net"]) for b in j["board_pads"]))
        A("    脚表 pin→网: %s" % ", ".join("pin%s=%s" % (t["pin"], t["net"]) for t in j["truth_pins"]))
        A("    占位序(网表首现行序): %s" % ", ".join("%d=%s" % (i, n)
                                                   for i, n in enumerate(j["bare_nets_order"], 1)))
        for r in j["renames"]:
            A("    改名 行%-4s %-6s %-24s → %-24s (net %s)"
              % (r["lineno"], r["col"], r["node_other"] and "", r["new_node"] or "★人工定★", r["net"])
              if False else
              "    改名 行%-4s %-6s '%s' → '%s' (net %s)"
              % (r["lineno"], r["col"], r["col"], r["new_node"] or "★人工定★", r["net"]))
        for a in j["add_rows"]:
            A("    ★补行 net=%-16s node1='%s'  node2='%s'  (脚表 pin%s)"
              % (a["net"], a["suggest_node1"], a["suggest_node2"], a["pin"]))
        # 板 pad 序 vs 脚表 pin 序
        bad = [x for x in j["pad_vs_truth"] if x["match"] is False]
        if bad:
            mismatch.append((j["ref"], bad))
            A("    ★★pad↔net 序不符: %s"
              % ", ".join("pad%s(%s) 应为 %s" % (x["pad"], x["net"], x["truth_net_of_this_pad"])
                          for x in bad))
        # ★占位序 vs 板 pad 号不一致
        ob = [x for x in j["occ_vs_board"] if x["match"] is False]
        if ob:
            A("    ★占位序 vs 板 pad 号不一致: %s"
              % ", ".join("占位%d(%s) 板pad=%s" % (x["occ_pad"], x["net"], x["board_pad"]) for x in ob))
        if j.get("offboard_hits"):
            A("    ★非 MAIN_PCB 行的同名裸端 (不参与 C4 · 本单只登记): %s"
              % ", ".join("行%d/%s(%s)" % (x["lineno"], x["col"], x["net"])
                          for x in j["offboard_hits"]))
        tot_r += j["n_rename"]
        tot_a += j["n_add"]
    A("")
    A("=== 汇总: 改名指令 %d 条 · 补行 %d 条 · 合计 %d 条" % (tot_r, tot_a, tot_r + tot_a))
    A("=== pad↔net 序不符的件 (%d): %s" % (len(mismatch), [m[0] for m in mismatch]))
    with open(OUT_TXT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(T) + "\n")
    print("\n".join(T[-8:]))
    print("[build] 已写 %s" % OUT_JSON)
    return 0


if __name__ == "__main__":
    sys.exit(main())
