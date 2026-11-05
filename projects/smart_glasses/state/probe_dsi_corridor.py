#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe_dsi_corridor.py -- 查清 DSI 那条腿到底被什么挡住
(官方板 v37_R; SoM DSI 脚 y=7.96 -> CONN_LIGHT y=60.15 之间要绕 SoM)"""
import sys, collections
import pcbnew
PCB = sys.argv[1] if len(sys.argv)>1 else \
  "/home/yuewuya/.openclaw/workspace/projects/smart_glasses/HW/PCB/demo_mainboard.kicad_pcb"
b = pcbnew.LoadBoard(PCB)
mm = 1e6
def R(x0,y0,x1,y1):
    # KiCad7 python: BOX2I (左上 + 尺寸)
    return pcbnew.BOX2I(pcbnew.VECTOR2I(int(x0*mm), int(y0*mm)),
                        pcbnew.VECTOR2I(int(x1*mm), int(y1*mm)))

# 1) 区域内有哪些封装 (含 bbox)
regions = {
  "左走道 x0..8  y6..57": (0,6,8,57),
  "左下角 x0..25 y50..62": (0,50,25,62),
  "带间 x24..40 y50..62": (24,50,40,62),
  "顶带 x0..42 y0..6":    (0,0,42,6),
}
for name,(x0,y0,x1,y1) in regions.items():
    rr = R(x0,y0,x1,y1)
    fps = []
    for f in b.GetFootprints():
        bb = f.GetBoundingBox()
        if bb.Intersects(rr):
            fps.append((f.GetReference(),
                        bb.GetLeft()/mm, bb.GetTop()/mm, bb.GetRight()/mm, bb.GetBottom()/mm))
    print("\n=== 区域: %s ===" % name)
    if not fps:
        print("   ★ 无封装")
    for ref,l,t,r,bo in sorted(fps, key=lambda z:z[1]):
        print("   %-18s x %7.2f..%7.2f  y %7.2f..%7.2f" % (ref,l,r,t,bo))

# 2) 左走道 x0..8 的铜: 按网统计 track 段数
print("\n=== 左走道 (x<8) 的铜 (按网, 只列 top10) ===")
cnt = collections.Counter(); vias=[]
for t in b.GetTracks():
    if t.GetClass()=="PCB_VIA":
        p=t.GetPosition()
        if p.x/mm < 8.5: vias.append((t.GetNetname(), p.x/mm, p.y/mm))
    else:
        for p in (t.GetStart(), t.GetEnd()):
            if p.x/mm < 8.5:
                cnt[t.GetNetname()]+=1; break
for n,c in cnt.most_common(10):
    print("   %-24s %d 段" % (n,c))
print("   -- 左走道里的过孔 %d 个 (前12):" % len(vias))
for n,x,y in sorted(vias,key=lambda z:z[2])[:12]:
    print("      %-22s (%.2f, %.2f)" % (n,x,y))
