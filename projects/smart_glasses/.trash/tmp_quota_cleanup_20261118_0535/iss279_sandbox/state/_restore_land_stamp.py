#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_restore_land_stamp.py —— ★回滚官方板后, 把 .layout_landed.json / .layout_done.json 一起改成**实测真值**

★**为什么**: 这两个文件被阶段门 G1 / chain_gate / 进展播报读
⇒ ★**留旧数 ⇒ 门禁和播报都读着错数** (★11-06 实测: 回滚后播报还报 unconnected=56 · DRC=1)
⇒ ⇒ ★**所以这里必须自己跑一次 fresh DRC, 把真数写进去**

用法: python3 state/_restore_land_stamp.py <板路径> [note]
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)


def measure(pcb):
    """★fresh DRC ⇒ (违规数, 未连接数) · ★取不到 ⇒ (999, 999) ⇒ 宁可报警也不写假数"""
    out = "/tmp/_restore_stamp_drc.json"
    try:
        subprocess.run(["bash", os.path.join(PROJ, "state", "kicad.sh"), "pcb", "drc",
                        "--output", out, "--severity-error", "--severity-warning",
                        "--format", "json", pcb],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=PROJ)
        d = json.load(open(out))
        return (len(d.get("violations") or []), len(d.get("unconnected_items") or []))
    except Exception:
        return (999, 999)


def main():
    p = sys.argv[1]
    note = sys.argv[2] if len(sys.argv) > 2 else "rollback"
    seg = via = 0
    for l in open(p, encoding="utf-8", errors="ignore"):
        s = l.lstrip()
        if s.startswith("(segment"):
            seg += 1
        elif s.startswith("(via"):
            via += 1
    st = int(os.stat(p).st_mtime)
    drc, unc = measure(p)
    d = os.path.dirname(p)
    json.dump({"at": st, "tracks": seg, "vias": via,
               "pcb": os.path.basename(p), "landed_at": st, "note": note},
              open(os.path.join(d, ".layout_landed.json"), "w", encoding="utf-8"))
    json.dump({"unconnected": unc, "drc_violations": drc, "tracks": seg, "vias": via,
               "at": st, "verified_by": "main (%s) · fresh DRC" % note},
              open(os.path.join(d, ".layout_done.json"), "w", encoding="utf-8"), indent=1)
    print("    落盘印已按实测回写: 段=%d 孔=%d DRC=%s unconnected=%s (note=%s)"
          % (seg, via, drc, unc, note))
    return 0


if __name__ == "__main__":
    sys.exit(main())
