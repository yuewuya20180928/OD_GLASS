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
    """★**当前在跑的布线/发布相关进程**

    ★★2026-11-06 23:2x (★兄弟实测抓到): ★**这一行以前会把自己数进去**
      · pgrep 的模式串里有 `publish_github` ⇒ ★**任何 cmdline 含这四个词的进程都会被数成"在跑"**
      · ★**而承载调用脚本的那个 bash, 命令行里恰好含这个模式串 (★我们为了查它写了模式串) ⇒ 自己命中自己**
      · ⇒ ★**这一行的数值取决于"谁在跑脚本", 不完全反映板面**
    ★**修法: 排除"自己这条命令链" (★自身 pid + 祖先链) + 排除含本脚本名的进程**
      ⇒ ★**不依赖调用方 ⇒ 数值稳定**
    ★**注: 这一行 ★**从不参与**"板面变了没"的判定 (★`bcast_facts.sh` 只取 `[板]` 行的指纹) ⇒ 只是显示层的诚实性**
    """
    try:
        r = subprocess.run(["pgrep", "-af", "gen_pcb_netlist_board|gen_pcb_routing|fix_gnd_stitch|publish_github"],
                           capture_output=True, text=True, timeout=10)
        # ★**自己的 pid 祖先链** (★调用方的 shell 也在链上 ⇒ 一并排除)
        skip = set()
        try:
            pid = os.getpid()
            for _ in range(12):
                if pid <= 0:
                    break
                skip.add(pid)
                with open("/proc/%d/stat" % pid, encoding="utf-8") as f:
                    pid = int(f.read().split(") ", 1)[1].split()[1])
        except Exception:
            pass
        out = []
        for l in (r.stdout or "").splitlines():
            if "pgrep" in l:
                continue
            parts = l.split(" ", 1)
            if not parts:
                continue
            try:
                p_ = int(parts[0])
            except ValueError:
                p_ = -1
            if p_ in skip:
                continue
            # ★**本脚本自身 / 承载它的 shell (★命令里会带 board_progress.py) 一律排除**
            if "board_progress.py" in l or "bcast_facts.sh" in l:
                continue
            out.append(l)
        return out
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
