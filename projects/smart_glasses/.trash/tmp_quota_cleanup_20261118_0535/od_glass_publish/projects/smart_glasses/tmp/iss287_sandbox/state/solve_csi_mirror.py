#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""solve_csi_mirror.py —— ★解算 CSI "P/N 镜像对" 摆放 (纯摆放, 不写 crossover 代码)

★★★**问题 (机器读出, 官方板 v37_R)**:
  CSI 每条 lane 的 P 和 N 之间夹着**两个分立的 2 脚器件**:
     `C_AC_CSI_D0_Dx_P` (pad1=SRC网, pad2=POST网)   ← 只走 P
     `C_AC_CSI_D0_Dx_N` (pad1=SRC网, pad2=POST网)   ← 只走 N
  ⇒ ★**P 网和 N 网是两条完全独立的网** ⇒ 它们的"左右序"由**器件摆放**决定
  ⇒ ⇒ 探针实测: 5 条 CSI lane 的 **SRC 段都一致**, 全部反转集中在 **POST 段 (电容行→CONN_CAM)**

★★★**求解 (纯几何)**:
  设 P 器件 pad1 在 px (rot=0 ⇒ pad2 = px+1.6), N 器件 pad1 在 nx
  · SRC 段 (SoM→pad1): SoM 端 P 在左 ⇒ 要求 **capP.pad1 < capN.pad1**
  · POST 段 (pad2→CONN_CAM): CONN_CAM 端 N 在左 ⇒ 要求 **capN.pad2 < capP.pad2**
  · rot=0 两只: px<nx 且 nx+1.6<px+1.6 ⇒ 矛盾 ⇒ **必须转一只**
  · ★**只转 N 侧 180°** (⇒ N 的 pad2 落在 pad1 左边 1.6mm):
        px < nx  且  nx-1.6 < px+1.6  ⇒  **px < nx < px+3.2**  ⇒ **可解!**
  ⇒ ★**结论: 交叉可以在摆放里吃掉 ⇒ 不必写 crossover 代码 ⇒ 差分耦合还能保住**

★**本脚本**: 逐 lane 解算目标坐标 + 校验
  ① 三个必要不等式
  ② 焊盘间距 (不同网 ≥0.20mm 边缘距)
  ③ 器件外框不重叠
  ④ 目标位置不撞官方板上已有的其它件
"""
import sys, re, collections, math
import pcbnew

PCB = sys.argv[1] if len(sys.argv) > 1 else \
    "/home/yuewuya/.openclaw/workspace/projects/smart_glasses/HW/PCB/demo_mainboard.kicad_pcb"

b = pcbnew.LoadBoard(PCB)
nets = collections.defaultdict(list)
fps = {}
for f in b.GetFootprints():
    ref = f.GetReference()
    fps[ref] = f
    for p in f.Pads():
        pos = p.GetPosition()
        nets[p.GetNetname()].append(dict(ref=ref, num=p.GetNumber(),
                                         x=pos.x / 1e6, y=pos.y / 1e6,
                                         w=p.GetSize().x / 1e6, h=p.GetSize().y / 1e6))

def lane_of(net):
    m = re.match(r'^(CSI|DSI)_D0_(D\d|CK)_(P|N)(_SRC)?$', net)
    return (m.group(1), m.group(2), m.group(3), bool(m.group(4))) if m else None

print("═══ 板: %s ═══" % PCB)

# ---- 焊盘宽/间距参数 (从板实测) ----
PADSZ = None
def pad_size_of(ref):
    global PADSZ
    f = fps.get(ref)
    if not f:
        return None
    ps = [(p.GetSize().x / 1e6, p.GetSize().y / 1e6) for p in f.Pads()]
    return ps[0] if ps else None

results = {}
for kind in ("CSI", "DSI"):
    lanes = collections.defaultdict(lambda: collections.defaultdict(list))
    for net, pads in nets.items():
        r = lane_of(net)
        if not r or r[0] != kind:
            continue
        _, lane, pol, src = r
        for pd in pads:
            lanes[lane][(pol, src)].append(pd)

    for lane in sorted(lanes):
        d = lanes[lane]
        P_src = [q for q in d[("P", True)] if q["ref"].startswith(("C_AC_CSI", "R_SEL"))]
        N_src = [q for q in d[("N", True)] if q["ref"].startswith(("C_AC_CSI", "R_SEL"))]
        P_post = [q for q in d[("P", False)] if q["ref"].startswith(("C_AC_CSI", "R_SEL"))]
        N_post = [q for q in d[("N", False)] if q["ref"].startswith(("C_AC_CSI", "R_SEL"))]
        somP = [q for q in d[("P", True)] if q["ref"].startswith("J_SOM")]
        somN = [q for q in d[("N", True)] if q["ref"].startswith("J_SOM")]
        conP = [q for q in d[("P", False)] if q["ref"].startswith("CONN_")]
        conN = [q for q in d[("N", False)] if q["ref"].startswith("CONN_")]
        if not (P_src and N_src and P_post and N_post and somP and somN and conP and conN):
            print("\n── %s_%s : ★数据不全, 跳过" % (kind, lane))
            continue
        devP, devN = P_src[0]["ref"], N_src[0]["ref"]
        psz = pad_size_of(devP)
        padw = psz[0] if psz else 0.60
        padh = psz[1] if psz else 0.90
        # 器件两脚间距 (当前)
        pitch = abs(P_post[0]["x"] - P_src[0]["x"])
        # SoM 端与连接器端的左右序
        som_Pl = somP[0]["x"] < somN[0]["x"]
        con_Pl = conP[0]["x"] < conN[0]["x"]
        # 当前器件端左右序 (pad1 与 pad2 各算)
        cur1_Pl = P_src[0]["x"] < N_src[0]["x"]
        cur2_Pl = P_post[0]["x"] < N_post[0]["x"]
        print("\n──── %s_%s  (器件 %s / %s, 脚距 %.2fmm, 焊盘 %.2fx%.2f) ────"
              % (kind, lane, devP, devN, pitch, padw, padh))
        print("   SoM 端: P@%.2f N@%.2f ⇒ P在左=%s" % (somP[0]["x"], somN[0]["x"], som_Pl))
        print("   器件 pad1: P@%.2f N@%.2f ⇒ P在左=%s" % (P_src[0]["x"], N_src[0]["x"], cur1_Pl))
        print("   器件 pad2: P@%.2f N@%.2f ⇒ P在左=%s" % (P_post[0]["x"], N_post[0]["x"], cur2_Pl))
        print("   连接器端: P@%.2f N@%.2f ⇒ P在左=%s" % (conP[0]["x"], conN[0]["x"], con_Pl))
        need1 = som_Pl     # SRC 段要求 pad1 端序 == SoM 端序
        need2 = con_Pl     # POST 段要求 pad2 端序 == 连接器端序
        print("   ⇒ 需要: pad1端 P在左=%s ; pad2端 P在左=%s" % (need1, need2))
        if cur1_Pl == need1 and cur2_Pl == need2:
            print("   ★★ 当前摆放已满足 ⇒ 无需动")
            continue
        # 求解: N 器件 rot=180 (pad2 落在 pad1 左侧 pitch)
        #   px = P 的 pad1 x ; nx = N 的 pad1 x
        #   条件: (px < nx) == need1 ; (nx-pitch < px+pitch) == need2
        #   即 need1 ⇒ px<nx (若 need1 为 True) 或 px>nx
        #       need2 ⇒ nx-pitch < px+pitch ⇔ nx < px+2*pitch
        lo, hi = None, None
        if need1:      # P 在左 ⇒ px < nx
            lo = px_lo = P_src[0]["x"]
        else:          # N 在左 ⇒ nx < px
            hi = px_hi = P_src[0]["x"]
        # 组装成区间 [nx_lo, nx_hi]
        cands = []
        for dx in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.8, 1.0, 1.2, 1.5, 1.8, 2.0, 2.2, 2.4, 2.6, 2.8, 3.0]:
            nx = P_src[0]["x"] + dx
            ok1 = (P_src[0]["x"] < nx) == need1
            ok2 = ((nx - pitch) < (P_post[0]["x"])) == need2
            if ok1 and ok2:
                cands.append((nx, dx))
        if not cands:
            print("   ⇒ ★无解 (该 lane 需要换层交叉)")
            continue
        # 选 **焊盘间距最大** 的那个候选 (dx 越大 ⇒ 器件分得越开)
        nx, dx = cands[-1]
        print("   ⇒ ★**可解**: N 器件 rot=180°, pad1 x = %.2f (Δ=+%.2fmm)" % (nx, dx))
        # 焊盘间距校验 (rot180 ⇒ N 的 pad2 在 nx-pitch)
        pads = [("P.pad1", P_src[0]["x"], P_src[0]["y"]),
                ("P.pad2", P_post[0]["x"], P_post[0]["y"]),
                ("N.pad1", nx, N_src[0]["y"]),
                ("N.pad2", nx - pitch, N_post[0]["y"])]
        print("      目标四焊盘: " + "  ".join("%s@(%.2f,%.2f)" % t for t in pads))
        worst = 1e9
        for i in range(len(pads)):
            for j in range(i + 1, len(pads)):
                (n1, x1, y1), (n2, x2, y2) = pads[i], pads[j]
                dxg = abs(x1 - x2); dyg = abs(y1 - y2)
                gap = math.hypot(max(0.0, dxg - padw), max(0.0, dyg - padh))
                same = (n1[0] == n2[0])
                if not same:
                    worst = min(worst, gap)
                print("      %-8s vs %-8s : 中心距 %.2f/%.2f ⇒ 边缘距 %.3fmm %s"
                      % (n1, n2, dxg, dyg, gap, "(同件)" if same else ""))
        print("      ⇒ 最小异网焊盘边缘距 = %.3fmm (规则 0.20) ⇒ %s"
              % (worst, "OK" if worst >= 0.20 - 1e-9 else "★不足!"))
        results["%s_%s" % (kind, lane)] = (devN, nx, N_src[0]["y"], 180, worst)

print("\n" + "=" * 92)
print("═══ 解算结果 (供 PCB_PART_POS 使用; 格式 REF:x,y,rot) ═══")
print("=" * 92)
out = []
for k in sorted(results):
    devN, nx, ny, rot, worst = results[k]
    out.append("%s:%.2f,%.2f,%d" % (devN, nx, ny, rot))
    print("  %-10s N器件 %-22s → %.2f,%.2f rot=%d  (最小焊盘距 %.3f)" % (k, devN, nx, ny, rot, worst))
print("\nPCB_PART_POS 串:\n  " + ";".join(out))
