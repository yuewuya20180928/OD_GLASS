#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
★【让路配方的量化分析器】★ — 2026-11-10 主会话

★**目的**: 把"官方板靠牺牲 `ID_DETECT_0` 的那个脚来换 `BOOT_N` 走通"这句话,
   ★**从"我看到的"变成"机器可复算的"** ⇒ 三方对照:
     ★ ① 官方板 (★45 条 unc / 42 网★)
     ★ ② `v76ml` 终板 (★29 条 / 24 网·当前最好的臂★)
     ★ ③ 同 env 闸关对照臂 `v76mj0` 终板 (★28 条 / 23 网★)

★**输出**:
   ★ A. 三方在 `BOOT_N` / `ID_DETECT_0` / `ID_DETECT_1` 这三个网上的【逐条对照】
   ★ B. 官方板"牺牲"了哪些网 (★官方板 unc 有·臂板没有 ⇒ 说明臂板把它救活了★)
   ★ C. 臂板"新引入"的断点 (★臂板 unc 有·官方板没有 ⇒ 说明臂板把它打死了★)
"""
import json
import sys
import collections

OFFICIAL = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses/state/official_18092_unc.drc.json"
ML = "/tmp/chain_v76ml/final_chain.kicad_pcb.drc.json.fresh"
MJ0 = "/tmp/chain_v76mj0/final_chain.kicad_pcb.drc.json.fresh"


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def unc_map(path):
    """⇒ {网名: [每条 unc 的描述, ...]}"""
    d = load(path)
    out = collections.defaultdict(list)
    for it in (d.get("unconnected_items") or []):
        desc = ""
        for sub in (it.get("items") or []):
            dd = sub.get("description") or ""
            if "[" in dd and "]" in dd:
                desc = dd
                break
        if "[" in desc and "]" in desc:
            net = desc.split("[")[1].split("]")[0]
        else:
            net = "<未知:%s>" % desc[:40]
        out[net].append(desc)
    return out, d


def main():
    paths = {"官方板": OFFICIAL, "v76ml(候选)": ML, "v76mj0(对照)": MJ0}
    data = {}
    for name, p in paths.items():
        try:
            data[name] = unc_map(p)
        except Exception as e:
            print("★ 读不到 %s (%s): %s" % (name, p, e))
            return 1

    print("═══ A. 三方在关键三网上的逐条对照 ═══")
    KEY = ["BOOT_N", "ID_DETECT_0", "ID_DETECT_1"]
    for net in KEY:
        print("\n── %s ──" % net)
        for name, (m, d) in data.items():
            items = m.get(net, [])
            print("  %-14s unc %d 条 %s" % (
                name, len(items),
                ("· " + " | ".join(x[:78] for x in items)) if items else "★**已连通**"))

    print("\n═══ B. 官方板断·臂板通 (⇒ 臂板救活的网) ═══")
    off, _ = data["官方板"]
    ml, _ = data["v76ml(候选)"]
    saved = sorted(set(off) - set(ml))
    print("  ★ 官方板断 %d 个网, 臂板已通 %d 个 ⇒ 救活率 %d%%" % (
        len(off), len(saved), round(100.0 * len(saved) / max(1, len(off)))))
    for n in saved:
        print("    ★ %-24s 官方板断 %d 处" % (n, len(off[n])))

    print("\n═══ C. 臂板新引入的断点 (⇒ 臂板打死的网) ═══")
    broke = sorted(set(ml) - set(off))
    print("  ★ 臂板新断 %d 个网" % len(broke))
    for n in broke:
        print("    ✘ %-24s 官方板 %s ⇒ 臂板断 %d 处" % (
            n, ("断 %d 处" % len(off[n])) if n in off else "★**本就连通**", len(ml[n])))

    print("\n═══ D. 候选 vs 同 env 对照臂 (★净账, ★决定晋级与否的就是这个差★) ═══")
    mj0, _ = data["v76mj0(对照)"]
    only_ml = sorted(set(ml) - set(mj0))
    only_mj0 = sorted(set(mj0) - set(ml))
    print("  ★ 只有候选臂断的网 (%d): %s" % (len(only_ml), ", ".join(only_ml) or "—"))
    print("  ★ 只有对照臂断的网 (%d): %s" % (len(only_mj0), ", ".join(only_mj0) or "—"))
    print("  ★⇒ ⇒ 候选臂相对同 env 对照臂【唯一多出来的】= %s ⇒ ★这就是晋级闸卡住的那一个" % (
        ", ".join(only_ml) or "—"))

    # ★★**⇒ 让路配方判定 ★★**
    print("\n═══ E. 让路配方判定: 官方板牺牲了谁, 换来了谁 ═══")
    for n in KEY:
        o = len(off.get(n, []))
        m = len(ml.get(n, []))
        if o > 0 and m == 0:
            print("  ★★★ %-14s 官方板【主动断掉 %d 处】, 臂板【已通】⇒ ⇒ ★★【官方板在这里是『牺牲方』★★" % (n, o))
        elif o == 0 and m > 0:
            print("  ★★★ %-14s 官方板【通的】, 臂板【断 %d 处】⇒ ⇒ ★★【臂板在这里是『牺牲方』★★" % (n, m))
        elif o > 0 and m > 0:
            print("      %-14s 两边都断 (官方 %d 处 / 臂 %d 处)" % (n, o, m))
        else:
            print("      %-14s 两边都通" % n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
