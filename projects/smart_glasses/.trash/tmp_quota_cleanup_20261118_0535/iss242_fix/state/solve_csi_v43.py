#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""solve_csi_v43.py -- 解出"CSI N 侧 AC 电容旋转 180 度 + 移到 P 侧旁"的**具体坐标**
  (依据: state/probe_lane_fix.py 的机器读结论)
  ★**几何推导** (P 侧 rot=0, N 侧 rot=180):
     N 侧旋转 180 => pad1 在右, pad2 在左 (pad1 = ox, pad2 = ox-1.6)
     段1 (SoM->SRC脚): SoM 端 P 在左 => 要求 P.pad1 < N.pad1  => px < ox
     段2 (POST脚->连接器): 连接器端 N 在左 => 要求 N.pad2 < P.pad2 => ox-1.6 < px+1.6 => ox < px+3.2
     => **px < ox < px+3.2**
  ★**为什么把 N 电容放到第二行 (y=56.9) 而不是同一行**:
     同行时 P.pad1 / N.pad2 / P.pad2 / N.pad1 会交错, 焊盘边缘净距只剩 0.20mm (零裕量)
     => 改放到 y=56.9 行 (AC 电容行 y=58.6 与 TP 行 y=55.2 之间, 上下各留 0.7/0.9mm) => 净距充裕
  ★**TP 也要跟着镜像**: TP 在 POST 网上, 原约定 pad1+0.2; 旋转后镜像 => pad2+1.4 = ox-0.2
"""
import sys, collections
import pcbnew
BOARD = sys.argv[1] if len(sys.argv)>1 else \
  "/home/yuewuya/.openclaw/workspace/projects/smart_glasses/HW/PCB/demo_mainboard.kicad_pcb"
b = pcbnew.LoadBoard(BOARD)
mm = 1e6

LANES = ["D3","D2","CK","D1","D0"]
parts = {}
for f in b.GetFootprints():
    ref = f.GetReference()
    pads = []
    for p in f.Pads():
        pos = p.GetPosition()
        sz  = p.GetSize()
        pads.append(dict(num=p.GetNumber(), net=p.GetNetname(),
                         x=pos.x/mm, y=pos.y/mm,
                         w=sz.x/mm, h=sz.y/mm,
                         bbox=f.GetBoundingBox()))
    parts[ref] = dict(f=f, pads=pads,
                       bb=(f.GetBoundingBox().GetLeft()/mm, f.GetBoundingBox().GetTop()/mm,
                           f.GetBoundingBox().GetRight()/mm, f.GetBoundingBox().GetBottom()/mm))

def find(ref, num):
    if ref not in parts: return None
    for p in parts[ref]["pads"]:
        if p["num"]==num: return p
    return None

print("═══ 源板: %s ═══" % BOARD)
print("\n── 现状 (官方板) ──")
sol = []
for ln in LANES:
    P  = "C_AC_CSI_D0_%s_P" % ln
    N  = "C_AC_CSI_D0_%s_N" % ln
    TPP = "TP_CSI_%s_P" % ln
    TPN = "TP_CSI_%s_N" % ln
    p1, p2 = find(P,"1"), find(P,"2")
    n1, n2 = find(N,"1"), find(N,"2")
    tpp, tpn = find(TPP,"1"), find(TPN,"1")
    if not (p1 and p2 and n1 and n2):
        print("  ★ %s 缺件, 跳过" % ln); continue
    has_tp = (tpn is not None)
    if not has_tp:
        tpn_x = None
    px = p1["x"]; ox = p1["x"] + 2.4          # ★新 N 侧原点 x
    oy = 57.0                                  # ★新 N 侧原点 y (第二行)
    tpn_x = ox - 0.2                            # ★TP 镜像
    # 焊盘矩形 (rot=180: pad1 在 ox, pad2 在 ox-1.6;  pad 中心 y = oy-0.1)
    n_new = [dict(num="1", x=ox,     y=oy-0.1, w=0.60, h=0.90),
             dict(num="2", x=ox-1.6, y=oy-0.1, w=0.60, h=0.90)]
    tpn_new = dict(num="1", x=(tpn_x if tpn_x is not None else -999), y=55.20, w=0.18, h=0.90)
    print("\n  lane %s" % ln)
    print("    P  电容 pad1@%.2f pad2@%.2f  (SRC=pad1, POST=pad2)" % (p1["x"], p2["x"]))
    print("    N  电容 现 pad1@%.2f pad2@%.2f  => 新(rot180) pad1@%.2f pad2@%.2f  y=%.2f"
          % (n1["x"], n2["x"], ox, ox-1.6, oy-0.1))
    if has_tp:
        print("    TP_N 现@%.2f (y=%.2f) => 新@%.2f (镜像: pad2+1.4)" % (tpn["x"], tpn["y"], tpn_x))
    else:
        print("    TP_N: 该 lane 无测试点 (只有 CK/D0 有)")
    # ★**序检查 (机器读)**
    ok1 = p1["x"] < ox          # 段1: P.pad1 < N.pad1
    ok2 = (ox-1.6) < p2["x"]    # 段2: N.pad2 < P.pad2
    print("    ★段1 需 P在左(SoM) : P.pad1 %.2f < N.pad1 %.2f => %s" % (p1["x"], ox, ok1))
    print("    ★段2 需 N在左(连接器): N.pad2 %.2f < P.pad2 %.2f => %s" % (ox-1.6, p2["x"], ok2))
    sol.append((ln, N, ox, oy, (TPN if has_tp else None), tpn_x, ok1 and ok2))

# ★**焊盘净距校验 (新 N 电容 + 新 TP vs 全板所有异网焊盘)**
print("\n── 焊盘边缘净距校验 (异网, 需 >= 0.20mm) ──")
allpads = []
for ref, d in parts.items():
    for p in d["pads"]:
        allpads.append((ref, p["num"], p["net"], p["x"], p["y"], p["w"], p["h"]))
worst = []
for ln, N, ox, oy, TPN, tpn_x, ok in sol:
    newpads = [(N,"1","CSI_D0_%s_N_SRC"%ln, ox, oy-0.1, 0.60, 0.90),
               (N,"2","CSI_D0_%s_N"%ln, ox-1.6, oy-0.1, 0.60, 0.90)]
    if TPN is not None:
        newpads.append((TPN,"1","CSI_D0_%s_N"%ln, tpn_x, 55.20, 0.18, 0.90))
    for (nref,nnum,nnet,nx,ny,nw,nh) in newpads:
        for (oref,onum,onet,ox_,oy_,ow,oh) in allpads:
            if onet == nnet: continue
            if oref == nref: continue
            if oref.startswith("TP_CSI_") and oref == TPN: continue
            dx = max(0.0, abs(nx-ox_) - (nw+ow)/2.0)
            dy = max(0.0, abs(ny-oy_) - (nh+oh)/2.0)
            gap = (dx*dx+dy*dy) ** 0.5
            if gap < 0.45:
                worst.append((gap, "%s.%s(%s)@%.2f,%.2f"%(nref,nnum,nnet,nx,ny),
                              "%s.%s(%s)@%.2f,%.2f"%(oref,onum,onet,ox_,oy_)))
worst.sort()
if not worst:
    print("   ★ 无 <0.45mm 的异网焊盘对")
for g,a,c in worst[:14]:
    flag = "  ★★违规" if g < 0.20 else ""
    print("   净距 %.3fmm : %s  vs  %s%s" % (g,a,c,flag))

# ★**输出 PCB_PART_POS**
print("\n── 建议的 PCB_PART_POS (仅 CSI N 侧, DSI 部分沿用 v40) ──")
seg = []
for ln, N, ox, oy, TPN, tpn_x, ok in sol:
    seg.append("%s:%.2f,%.2f,180" % (N, ox, oy))
    if TPN is not None:
        seg.append("%s:%.2f,55.2" % (TPN, tpn_x))
print(";".join(seg))
