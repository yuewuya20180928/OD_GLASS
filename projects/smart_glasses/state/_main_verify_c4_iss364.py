#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_main_verify_c4_iss364.py
==================================================
main (项目总工) 的【独立复核脚本 · ISS-364 核心数字】
★哲学: 不抄 agent 的表, 自己用【真闸代码】重算 ★
★做法: 只 import `state/check_pcb_nets.py` 的 `netlist_pads()` (★真闸的一个字节不抄★)
  ⇒ ① 真网表  ⇒ C4 占位脚号器件数  = 158 (基线)
  ⇒ ② 腿 B 网表副本 (tmp/iss364_sbx/netlist_v1_legB.csv) ⇒ C4 = 68
  ⇒ ③ 四桶分解 (TP / DNP / 靶内 / 缺口) 由 main 自己算, 不抄 ISS-361 的表
★必须用 KiCad python 跑: bash state/pcbnew_py.sh state/_main_verify_c4_iss364.py
★零写板 / 零落表 (只读真件 + 只读沙盒副本)
"""
import collections
import csv
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(PROJ, "state"))

spec = importlib.util.spec_from_file_location("cpn", os.path.join(HERE, "check_pcb_nets.py"))
cpn = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cpn)


def c4_of(net_path):
    rows = list(csv.DictReader(open(net_path, encoding="utf-8")))
    # ★与真闸同口径: 只算 board == MAIN_PCB 的行 (★demo 主板口径·充电链/跨铰链的件不在板上★)
    rows = [r for r in rows if (r.get("board") or "MAIN_PCB").strip() == cpn.BOARD_FILTER]
    _per, _num, placeholder, _notes = cpn.netlist_pads(rows)
    return placeholder


def buckets(placeholder):
    bom = {r["ref"]: r for r in csv.DictReader(open(os.path.join(PROJ, "HW", "BOM_v1.csv"), encoding="utf-8"))}
    b = collections.Counter()
    missing = []
    for ref in placeholder:
        r = bom.get(ref)
        if not r:
            missing.append(ref)
            continue
        if (r.get("type") or "").strip() == "TP":
            b["TP"] += 1
        elif (r.get("dnp") or "").strip() == "DNP":
            b["DNP"] += 1
        elif (r.get("footprint") or "").strip() == "待定":
            b["靶内"] += 1
        else:
            b["缺口"] += 1
    return b, missing


real_net = os.path.join(PROJ, "HW", "netlist_v1.csv")
legb_net = os.path.join(PROJ, "tmp", "iss364_sbx", "netlist_v1_legB.csv")

ph_real = c4_of(real_net)
print("REAL_NET_C4=%d" % len(ph_real))
if os.path.isfile(legb_net):
    ph_legb = c4_of(legb_net)
    print("LEGB_NET_C4=%d" % len(ph_legb))
else:
    print("LEGB_NET_C4=MISSING(%s)" % legb_net)
    ph_legb = None

b, missing = buckets(ph_real)
print("BUCKETS=%s SUM=%d BOM_MISSING=%d" % (
    dict(b), sum(b.values()), len(missing)))
if ph_legb is not None:
    bl, _m = buckets(ph_legb)
    print("LEGB_BUCKETS=%s SUM=%d" % (dict(bl), sum(bl.values())))

ok = (len(ph_real) == 158 and ph_legb is not None and len(ph_legb) == 68
      and b["TP"] == 42 and b["DNP"] == 26 and b["靶内"] == 77 and b["缺口"] == 13
      and sum(b.values()) == 158)
print("VERIFY=%s" % ("OK" if ok else "MISMATCH"))
sys.exit(0 if ok else 1)
