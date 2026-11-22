#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe_lane_order.py —— ★逐 lane 判定 P/N 左右序 (全焊盘, pcbnew 直读)

★★**要回答的唯一问题**:
  每个 lane 的两个网 (P / N) 在**每一端**的 x 序是什么?
  ⇒ 序一致 ⇒ 该段**不需要交叉**
  ⇒ 序相反 ⇒ 该段**几何上必须交换** (⇒ 两个网会撞 ⇒ 必有一个布不出来)

★★**为什么这决定 v38 存废**:
  cron 说 "CSI 5 对缺铜 ⇒ 下 crossover 刀" ⇒ ★**但缺铜 ≠ 需要交叉**
  ⇒ 审计实测: **P 侧基本通了 / N 侧基本没通** ⇒ 也可能是纯拥塞
  ⇒ ★**更关键**: P/N 之间夹着**两个分立的 2 脚器件** (C_AC_CSI_xx_P / _N, R_SEL_xx_P / _N)
  ⇒ ⇒ "lane" 实际被拆成**两条独立的网** ⇒ ★**中间器件的摆放就能决定要不要交叉**
  ⇒ ⇒ ★**可能根本不需要写 crossover 代码, 改摆放就够了**
"""
import sys, re, collections
import pcbnew

PCB = sys.argv[1] if len(sys.argv) > 1 else \
    "/home/yuewuya/.openclaw/workspace/projects/smart_glasses/HW/PCB/demo_mainboard.kicad_pcb"

b = pcbnew.LoadBoard(PCB)
nets = collections.defaultdict(list)
for f in b.GetFootprints():
    ref = f.GetReference()
    for p in f.Pads():
        pos = p.GetPosition()
        nets[p.GetNetname()].append((ref, p.GetNumber(), pos.x / 1e6, pos.y / 1e6))

def lane_of(net):
    m = re.match(r'^(CSI|DSI)_D0_(D\d|CK)_(P|N)(_SRC)?$', net)
    if not m:
        return None
    return m.group(1), m.group(2), m.group(3), bool(m.group(4))

print("═══ 板: %s ═══" % PCB)
for kind in ("CSI", "DSI"):
    lanes = collections.defaultdict(lambda: {"P": [], "N": []})
    for net, pads in nets.items():
        r = lane_of(net)
        if not r or r[0] != kind:
            continue
        _, lane, pol, src = r
        for pd in pads:
            lanes[lane][pol].append((pd[0], pd[1], pd[2], pd[3], net))

    print("\n" + "=" * 84)
    print("═══ %s: 每 lane 的 P/N 全焊盘 (按 x 排) ═══" % kind)
    print("=" * 84)
    for lane in sorted(lanes):
        d = lanes[lane]
        print("\n──── %s_%s ────" % (kind, lane))
        for pol in ("P", "N"):
            ps = sorted(d[pol], key=lambda t: t[2])
            print("  %s 侧:" % pol)
            for (ref, num, x, y, net) in ps:
                print("     %-16s pad %-4s @(%7.2f,%7.2f)   net=%s" % (ref, num, x, y, net))
        # 分组: _SRC 腿 (SoM→中途器件) vs 后段 (中途器件→连接器)
        def split(pol):
            src = [t for t in d[pol] if t[4].endswith("_SRC")]
            dst = [t for t in d[pol] if not t[4].endswith("_SRC")]
            return src, dst
        for legname, want_src in (("SoM→中途器件", True), ("中途器件→连接器", False)):
            Ps, _ = split("P"); Ns, _ = split("N")
            _, Pd = split("P"); _, Nd = split("N")
            P = Ps if want_src else Pd
            N = Ns if want_src else Nd
            if not P or not N:
                print("  %-16s : %s" % (legname, "★有一侧无焊盘"))
                continue
            # 端点序: 用每个网的 "最靠外" 焊盘 (SoM 端 = y 最小; 连接器端 = 特定 ref)
            def outer(pl):
                # SoM 端取 J_SOM_*, 连接器端取 CONN_*/TP_*
                som = [t for t in pl if t[0].startswith("J_SOM")]
                con = [t for t in pl if t[0].startswith("CONN_") or t[0].startswith("TP_")]
                return (som[0] if som else (con[0] if con else pl[0]))
            op, on = outer(P), outer(N)
            if op[2] < on[2]:
                order = "★P 在左"
            elif op[2] > on[2]:
                order = "★N 在左"
            else:
                order = "同 x"
            conflict = "  ★★★ **必须交换 (几何冲突!) **" if op[2] != on[2] else "  ⇒ 序一致, 不需交叉"
            print("  %-16s : P端 %s @x=%.2f   N端 %s @x=%.2f  ⇒ %s%s" %
                  (legname, op[0] + "." + op[1], op[2], on[0] + "." + on[1], on[2], order, conflict))
