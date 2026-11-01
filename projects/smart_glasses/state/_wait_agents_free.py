#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""周交付窗口 · 守候三个总工的在跑写会话结束 (防同一 agent 两个写会话互相覆盖分片)

判据: 该 agent 的 session jsonl 文件
      ① 最后一条 assistant 消息带 stopReason == "stop" (即子代理已交卷)
      ② 且文件 mtime 静默 >= 60s (不再有写入)
两条都满足才算"该 agent 空闲, 可以派周更新"。
用法: python3 state/_wait_agents_free.py [超时秒] [轮询秒]
"""
import os, sys, json, time, glob

BASE = "/home/yuewuya/.openclaw/agents"
AGENTS = ("hw-lead", "sw-lead", "mech-lead")
TIMEOUT = int(sys.argv[1]) if len(sys.argv) > 1 else 1800
POLL = int(sys.argv[2]) if len(sys.argv) > 2 else 20
QUIET = 60  # 秒


def newest_session(agent):
    fs = [f for f in glob.glob(f"{BASE}/{agent}/sessions/*.jsonl")
          if ".trajectory" not in f and ".checkpoint" not in f]
    if not fs:
        return None
    return max(fs, key=os.path.getmtime)


def finished(agent):
    f = newest_session(agent)
    if not f:
        return None
    age = time.time() - os.path.getmtime(f)
    if age < QUIET:
        return None
    try:
        lines = open(f, errors="replace").read().strip().split("\n")
    except Exception:
        return None
    for l in reversed(lines[-12:]):
        l = l.strip()
        if not l.startswith("{"):
            continue
        try:
            r = json.loads(l)
        except Exception:
            continue
        m = r.get("message") or {}
        if m.get("role") == "assistant" and m.get("stopReason"):
            # ★ 只有 stopReason == "stop" 才是交卷; toolUse = 还在干活 (可能在等慢工具)
            if m.get("stopReason") != "stop":
                return None
            return (f, age, m.get("stopReason"))
    return None


t0 = time.time()
free = set()
while time.time() - t0 < TIMEOUT:
    for a in AGENTS:
        if a in free:
            continue
        r = finished(a)
        if r:
            free.add(a)
            print(f"[{time.strftime('%H:%M:%S')}] {a} 空闲 (session={os.path.basename(r[0])}, 静默 {int(r[1])}s, stop={r[2]})", flush=True)
    if len(free) == len(AGENTS):
        print(f"ALL_FREE after {int(time.time()-t0)}s -> {' '.join(AGENTS)}", flush=True)
        sys.exit(0)
    time.sleep(POLL)

print(f"TIMEOUT after {int(time.time()-t0)}s; free={sorted(free)}", flush=True)
sys.exit(3)
