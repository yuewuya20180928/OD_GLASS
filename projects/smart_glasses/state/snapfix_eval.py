#!/usr/bin/env python3
# ★★★★★★2026-11-11 05:6x 【★端点吸附实验的评估器 (★三把尺一起出★)】★★★★★★
#   ★**为什么要有**: ★铁律: ★**DRC / 未连接 / 名单闸 三个维度必须一起打印** ⇒ 少一个维度就下结论 = 误判 ★★
#   ★**铁律**: ★**每块板都必须 fresh DRC** ⇒ 不许信目录里的同名 json (★实测踩过: 里面装的是上一步输入板的 DRC★)
import collections
import json
import math
import os
import re
import subprocess
import sys

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"


def fresh_drc(board, out):
    subprocess.run(["bash", "state/kicad.sh", "pcb", "drc", "--output", out,
                    "--severity-error", "--severity-warning", "--format", "json", board],
                   cwd=PROJ, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return out if os.path.exists(out) else None


def load(p):
    j = json.load(open(p, encoding="utf-8"))
    unc = j.get("unconnected_items") or []
    vio = j.get("violations") or []
    nets = []
    sigs = set()
    for it in unc:
        its = it.get("items") or []
        names = []
        for a in its:
            m = re.search(r"\[([^\]]+)\]", a.get("description") or "")
            names.append(m.group(1) if m else "?")
        if names:
            nets.append(names[0])
        sigs.add("|".join(names))
    kinds = collections.Counter(v.get("type") or "?" for v in vio)
    return {"vio": len(vio), "kinds": dict(kinds), "unc": len(unc),
            "nets": sorted(set(nets)), "sigs": sigs, "ncnt": collections.Counter(nets)}


def segs(p):
    n = 0
    with open(p, encoding="utf-8", errors="ignore") as f:
        for l in f:
            if l.lstrip().startswith("(segment"):
                n += 1
    return n


def main():
    if len(sys.argv) < 2:
        print("用法: python3 state/snapfix_eval.py <板1> [板2 ...] [--baseline <基线板>]")
        return 2
    args = sys.argv[1:]
    base = None
    if "--baseline" in args:
        i = args.index("--baseline")
        base = args[i + 1]
        args = args[:i] + args[i + 2:]
    base_set = None
    if base:
        bp = "/tmp/snapfix/_base.drc.json"
        fresh_drc(base, bp)
        b = load(bp)
        base_set = b["sigs"]
        print("★基线 %s" % os.path.basename(base))
        print("   DRC %d · unc %d 条 / %d 网名 · 段 %d"
              % (b["vio"], b["unc"], len(b["nets"]), segs(base)))
        if b["kinds"]:
            print("   违规类型: %s" % b["kinds"])
        print()
    for p in args:
        if not os.path.exists(p):
            print("❌ 不存在: %s" % p)
            continue
        d = "/tmp/snapfix/_%s.drc.json" % os.path.basename(p).replace(".kicad_pcb", "")
        fresh_drc(p, d)
        r = load(d)
        print("▌%s" % os.path.basename(p))
        print("   DRC %d %s · unc %d 条 / %d 网名 · 段 %d"
              % (r["vio"], ("(%s)" % r["kinds"]) if r["kinds"] else "", r["unc"], len(r["nets"]), segs(p)))
        if base_set is not None:
            only_c = r["sigs"] - base_set
            only_b = base_set - r["sigs"]
            print("   名单制: 仅本板 %d · 仅基线 %d  ⇒ %s"
                  % (len(only_c), len(only_b),
                     ("✅ 纯赚 %d 个签名" % len(only_b)) if not only_c else
                     ("❌ 新断 %d 个签名" % len(only_c))))
            if only_b:
                print("     ★仅基线有(救回): %s" % sorted(only_b))
            if only_c:
                print("     ★仅本板有(新断): %s" % sorted(only_c))
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
