#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
board_progress.py —— ★当前任务进展速览 (2026-11-05 01:3x 老板要求: 每 5 分钟输出进展)

用法: python3 state/board_progress.py
输出: 一屏 10 行以内的事实 (不含任何判断) ⇒ 心跳/定时播报直接用它
"""
import json
import os
import re
import subprocess
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
PCB = os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb")
STAMP = os.path.join(PROJ, "HW", "PCB", ".layout_done.json")
TASK = os.path.join(HERE, "CURRENT_TASK.md")


def board_facts():
    out = {}
    try:
        st = os.stat(PCB)
        out["mtime"] = time.strftime("%m-%d %H:%M:%S", time.localtime(st.st_mtime))
        out["size_mb"] = st.st_size / 1e6
    except Exception:
        return out
    seg = via = 0
    try:
        with open(PCB, encoding="utf-8") as f:
            for line in f:
                s = line.lstrip()
                if s.startswith("(segment"):
                    seg += 1
                elif s.startswith("(via"):
                    via += 1
    except Exception:
        pass
    out["tracks"] = seg
    out["vias"] = via
    try:
        out["stamp"] = json.load(open(STAMP, encoding="utf-8"))
    except Exception:
        out["stamp"] = None
    return out


def running():
    try:
        r = subprocess.run(["pgrep", "-af", "gen_pcb_netlist_board|gen_pcb_routing|fix_gnd_stitch|publish_github"],
                           capture_output=True, text=True, timeout=10)
        lines = [l for l in (r.stdout or "").splitlines() if "pgrep" not in l]
        return lines
    except Exception:
        return []


def task_head():
    """返回 (当前在做, 待办清单)"""
    try:
        txt = open(TASK, encoding="utf-8").read()
        lines = [l.strip() for l in txt.splitlines()
                 if l.strip() and not l.strip().startswith("#")]
    except Exception:
        return ["(无 state/CURRENT_TASK.md)"], []
    cur = lines[0] if lines else "(空)"
    todos = [l for l in lines[1:] if not l.startswith("★")]
    return cur, todos


def main():
    now = time.strftime("%m-%d %H:%M:%S")
    b = board_facts()
    st = b.get("stamp") or {}
    print(f"=== 进展播报 {now} ===")
    print(f"[板] {b.get('mtime','?')} · {b.get('size_mb',0):.1f}MB · {b.get('tracks',0)} 段走线 · {b.get('vias',0)} 过孔")
    print(f"[布线] 上次实测 unconnected={st.get('unconnected','?')} · DRC违规={st.get('drc_violations','?')} · 留证 {st.get('at','?')}")
    rs = running()
    print(f"[在跑] {len(rs)} 个进程" + ("" if not rs else " ⇒ " + "; ".join(x.split()[1] if len(x.split())>1 else x for x in rs[:2])))
    cur, todos = task_head()
    print(f"[当前在做] {cur}")
    print("[待办]")
    for l in todos[:9]:
        print("  - " + l)


if __name__ == "__main__":
    main()
