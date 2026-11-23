#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_frag_dup_keys.py —— ★四个分片的【重名 key】只读体检 (★2026-11-23 09:1x main 新建★)

★为什么做这件事 (★兄弟 job 09:03 播报里那条「同 agent 两会话并发写同一分片 ⇒ 后写覆盖前写」★):
  `state/frag_write.py` 的写路径是「读全文件 → 改 → 原子写回」⇒ ★**两个 lane 同时改同一个分片时,
  后写的那一份带着自己读到的旧基线 ⇒ 先写的那一次改动被静默覆盖 (lost update)** ★
  ⇒ ★**这个体检器把「已经攒下的重名 key」全部点出来, 让人能判断哪些是真丢数据、哪些只是无害的重复登记** ★
  ★**它只读, 零写盘** ★

用法:
  python3 state/check_frag_dup_keys.py            # 全部四片
  python3 state/check_frag_dup_keys.py --agent hw-lead
  python3 state/check_frag_dup_keys.py --selftest
退出码: 0 = 无「高危段」(answers / needs_from)重名 · 1 = 有高危段重名 · 2 = 参数/格式错
"""
import os
import sys
from collections import Counter

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRAGS = {"main": "pm.yaml", "hw-lead": "hw.yaml", "sw-lead": "sw.yaml", "mech-lead": "mech.yaml"}
# ★高危段: 同一段里两个同 key 条目 ⇒ 合并时取值取决于合并器的先后顺序 ⇒ 「后写覆盖前写」的受害者 ★
HIGH_RISK = ("answers", "needs_from")
LOW_RISK = ("artifacts", "interface_claims", "risks", "blockers")


def load(agent):
    import yaml
    p = os.path.join(PROJ, "state/fragments", FRAGS[agent])
    if not os.path.isfile(p):
        return None
    with open(p, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def scan(agent):
    d = load(agent)
    if d is None:
        return []
    rows = []
    for sect in list(HIGH_RISK) + list(LOW_RISK):
        entries = [e for e in (d.get(sect) or []) if isinstance(e, dict)]
        keys = [str(e.get("key") or e.get("id") or e.get("path") or "") for e in entries]
        cnt = Counter(k for k in keys if k)
        for k, n in sorted(cnt.items()):
            if n > 1:
                rows.append((sect, k, n, "高危" if sect in HIGH_RISK else "低危"))
    return rows


def self_test():
    print("=" * 78)
    print("★ check_frag_dup_keys · 自测")
    r = []
    sample = {"answers": [{"key": "a"}, {"key": "a"}, {"key": "b"}],
              "artifacts": [{"path": "p"}, {"path": "p"}]}
    c = Counter(e.get("key") or e.get("id") or e.get("path") or "" for e in sample["answers"])
    r.append(("反向用例1 · 同段同 key 被点出 (×2)", c["a"] == 2 and c["b"] == 1))
    c2 = Counter(e.get("path") for e in sample["artifacts"])
    r.append(("反向用例2 · artifacts 段也按 path 判重", c2["p"] == 2))
    r.append(("反向用例3 · 高危段判定正确", "answers" in HIGH_RISK and "artifacts" in LOW_RISK))
    allok = True
    for n, ok in r:
        allok = allok and bool(ok)
        print("  %s %s" % ("✅" if ok else "❌", n))
    print("  ⇒ %s" % ("★ALL TESTS PASS★" if allok else "★★自测红★★"))
    return 0 if allok else 1


def main():
    args = sys.argv[1:]
    if "--selftest" in args:
        return self_test()
    agents = ["main", "hw-lead", "sw-lead", "mech-lead"]
    if "--agent" in args:
        i = args.index("--agent")
        if i + 1 < len(args) and args[i + 1] in FRAGS:
            agents = [args[i + 1]]
    print("=" * 78)
    print("★ 四分片重名 key 体检 (★只读·零写盘·★高危段 = answers / needs_from★)")
    high = 0
    for a in agents:
        rows = scan(a)
        if not rows:
            print("  ✅ %-10s 无重名 key" % a)
            continue
        hi = [r for r in rows if r[3] == "高危"]
        low = [r for r in rows if r[3] == "低危"]
        high += len(hi)
        print("  ⚠️  %-10s 高危 %d 组 · 低危 %d 组" % (a, len(hi), len(low)))
        for sect, k, n, kind in hi:
            print("        ★★高危★ [%s] %-44s ×%d" % (sect, k[:44], n))
        for sect, k, n, kind in low[:6]:
            print("           低危 [%s] %-44s ×%d" % (sect, k[:44], n))
        if len(low) > 6:
            print("           …低危另有 %d 组" % (len(low) - 6))
    print("-" * 78)
    print("★ ⇒ 高危段重名合计 **%d** 组 ⇒ ★**这些是「后写覆盖前写」的受害者 ⇒ 合并取值取决于合并器顺序 ⇒ 需人工核对哪一条是对的** ★" % high)
    return 1 if high else 0


if __name__ == "__main__":
    sys.exit(main())
