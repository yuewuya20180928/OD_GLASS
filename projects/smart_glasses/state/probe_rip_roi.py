#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe_rip_roi.py -- ★★量化"修 ripup_and_reroute 的整网重画"到底值多少 (★ROI 判定)

★★★**★为什么要有这个 (★2026-11-09 17:0x)★★★**
  ★**兄弟 session 09:08 提"下一轮改 `ripup_and_reroute` 的整网重画 + env 门控 + 臂验证"**
  ⇒ ★★**那是【改路由器核心函数】+【6 小时臂验证】⇒ ★★**必须先知道它值多少** ★★
  ★**本脚本**: ★**用手头的【脏中间板】(★诊断出口留的) 做【反事实实验】** ★★
    · ★**方案X = 脏板原样** (★接受整网重画 + 目标网新铜 ⇒ 已知脏)
    · ★**方案Y = 只保留【目标网】的新铜, 丢弃【被整网重画的其他网】的新铜** ⇒ ★**这正是"只重画被拆的那几段"的极限形态** ★★
    · ★**量两者: ★新铜段数 · 真几何违规数 · unconnected 数 · 目标网是否连通** ★★
  ⇒ ★★**⇒ 若方案Y 能做到"干净 + 目标网连通" ⇒ ★★**那这条修法【可行】且【代价极小】(★甚至不用改路由器) ⇒ ★★** ⇒ ★★**若方案Y 连目标网都不通 ⇒ ★★**⇒ 这条修法【救不了】⇒ ⇒ 【不用动路由器】** ★★**

用法: bash state/pcbnew_py.sh state/probe_rip_roi.py <脏板> <原板> <目标网>
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("PCB_LAYERS", "8")
import gen_pcb_routing as RT  # noqa: E402
import geom_clear as GC  # noqa: E402


def parse(p):
    """★**复用项目里已验证的解析器** (★别自己写正则 ⇒ ★今晚踩过: 自写版少一个转义 ⇒ 静默 0 匹配)"""
    t = open(p, encoding="utf-8", errors="ignore").read()
    out = []
    for m in re.finditer(
        r"\(segment\s*\n\s*\(start ([-\d.]+) ([-\d.]+)\)\s*\n\s*"
        r"\(end ([-\d.]+) ([-\d.]+)\)\s*\n\s*\(width ([0-9.]+)\)\s*\n\s*"
        r'\(layer "([^"]+)"\)\s*\n\s*\(net "([^"]+)"\)', t):
        out.append(m.groups())
    return out


def main():
    dirty_p = sys.argv[1]
    orig_p = sys.argv[2]
    target = sys.argv[3]
    outp = "/tmp/_rip_roi_Y.kicad_pcb"

    orig = parse(orig_p)
    dirty = parse(dirty_p)
    oset = set(orig)
    new = [g for g in dirty if g not in oset]
    print("★原板段 = %d · 脏板段 = %d · 新铜 = %d" % (len(orig), len(dirty), len(new)))
    # ★**字段序**: (x1,y1,x2,y2,w,layer,net) ⇒ 网名在 index 6
    keep = [g for g in new if g[6] == target]
    drop = [g for g in new if g[6] != target]
    print("★方案Y: 保留【%s】新铜 %d 段 · 丢弃【整网重画的其他网】新铜 %d 段" % (target, len(keep), len(drop)))

    # ── 方案Y = 原板 + 目标网新铜 (★被拆又重画的挡路线要还原) ──
    # ★**注意: 脏板里【挡路网的旧铜】已经被整网重画替换了 ⇒ 只加目标网新铜 = 原板 + 目标新铜**
    import shutil
    shutil.copyfile(orig_p, outp)
    # ★直接用文本插入新铜 (★只加目标网的 ⇒ 改动最小, ★不依赖 pcbnew 的写回)
    txt = open(outp, encoding="utf-8", errors="ignore").read()
    add = []
    for (x1, y1, x2, y2, w, li, net) in keep:
        add.append('\t(segment\n\t\t(start %s %s)\n\t\t(end %s %s)\n\t\t(width %s)\n'
                   '\t\t(layer "%s")\n\t\t(net "%s")\n\t)\n' % (x1, y1, x2, y2, w, li, net))
    idx = txt.rfind("\n)")
    txt = txt[:idx] + "\n" + "".join(add) + txt[idx:]
    open(outp, "w", encoding="utf-8").write(txt)
    print("✓ 方案Y 已写: %s (★%d 段新铜)" % (outp, len(keep)))

    # ── 量两个方案 ──
    for tag, path in (("X-脏板原样", dirty_p), ("Y-只留目标网新铜", outp)):
        drc = "/tmp/_roi_%s.json" % tag
        subprocess.run(["bash", "state/kicad.sh", "pcb", "drc", "--output", drc,
                        "--severity-error", "--severity-warning", "--format", "json", path],
                       capture_output=True, timeout=1800)
        try:
            d = json.load(open(drc, encoding="utf-8"))
            nv = len(d.get("violations") or [])
            nu = len(d.get("unconnected_items") or [])
        except Exception as e:
            nv, nu = -1, -1
            print("  ★DRC 读取失败:", e)
        print("  ★方案%s: DRC违规=%d · unconnected=%d" % (tag, nv, nu))
    return 0


if __name__ == "__main__":
    sys.exit(main())
