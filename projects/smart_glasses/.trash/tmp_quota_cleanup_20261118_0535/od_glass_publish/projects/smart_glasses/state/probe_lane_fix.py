#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe_lane_fix.py —— ★验证: 交叉能否靠**摆放/旋转**吃掉 (而不是写 crossover 代码)

★★★**核心洞察 (机器读得出)**:
  每条 lane 的 P 和 N 之间夹着**两个分立的 2 脚器件**:
     `C_AC_CSI_D0_D3_P` (pad1=SRC网, pad2=POST网)   ← 只走 P
     `C_AC_CSI_D0_D3_N` (pad1=SRC网, pad2=POST网)   ← 只走 N
  ⇒ ★**P 网和 N 网是两条完全独立的网** (不是一条差分铜)
  ⇒ ⇒ "lane 一定要交叉" **不是硬约束**! 交叉可以在**器件摆放 + 旋转**里吃掉

★★**几何论证**:
  设 P 侧器件 pad1(SoM侧)=p1, pad2(连接器侧)=p2 ; N 侧同理 n1, n2
  ★**器件旋转 180° ⇒ 它的 pad1/pad2 的 x 互换**
  要让两段都不交叉:
     段1 (SoM→器件SRC脚): SoM 端 P在左 ⇒ 要求 **p1 < n1**
     段2 (器件POST脚→连接器): 连接器端 N在左 ⇒ 要求 **p2 > n2**
  若 P 侧器件 pad2 在 pad1 右侧 (p2 = p1 + 1.6), N 侧器件**旋转 180°** (n1 = n0+1.6, n2 = n0):
     p1 < n1 ⇔ p1 < n0+1.6
     p2 > n2 ⇔ p1+1.6 > n0 ⇔ p1 > n0-1.6
  ⇒ **两者可同时满足** (n0-1.6 < p1 < n0+1.6) ⇒ ★**交叉被吃掉, 全程 P/N 平行!**
  ⇒ ★**不需要 crossover 代码, 不需要换层, 差分耦合还更好 (两个器件贴一起)**

★**本脚本**: 用官方板真实焊盘坐标, 逐 lane 检查
     ① 当前摆放下两段各自是否一致 (⇒ 现有 inversion 在哪)
     ② 旋转 N 侧器件后能否同时满足
     ③ 顺带检查 POST 网里的 TP/ESD 焊盘 x 序 (它们也在同一条网上)
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
        nets[p.GetNetname()].append(dict(ref=ref, num=p.GetNumber(),
                                         x=pos.x / 1e6, y=pos.y / 1e6))

def lane_of(net):
    m = re.match(r'^(CSI|DSI)_D0_(D\d|CK)_(P|N)(_SRC)?$', net)
    return (m.group(1), m.group(2), m.group(3), bool(m.group(4))) if m else None

print("═══ 板: %s ═══" % PCB)
fixable = 0
total = 0
for kind in ("CSI", "DSI"):
    lanes = collections.defaultdict(lambda: collections.defaultdict(list))
    for net, pads in nets.items():
        r = lane_of(net)
        if not r or r[0] != kind:
            continue
        _, lane, pol, src = r
        for pd in pads:
            lanes[lane][(pol, src)].append(pd)

    print("\n" + "=" * 92)
    print("═══ %s 逐 lane: SRC 段 / POST 段 的 P/N x 序 ═══" % kind)
    print("=" * 92)
    for lane in sorted(lanes):
        d = lanes[lane]
        total += 1
        print("\n──── %s_%s ────" % (kind, lane))
        info = {}
        for src in (True, False):
            P = d[("P", src)]
            N = d[("N", src)]
            if not P or not N:
                print("   %-5s : ★缺一侧" % ("SRC" if src else "POST"))
                continue
            tag = "SRC" if src else "POST"
            # 按角色分: SoM端 / 器件脚 / 其它(TP/ESD/CONN)
            def role(pd):
                if pd["ref"].startswith("J_SOM"): return "som"
                if pd["ref"].startswith(("C_AC_CSI", "R_SEL")): return "dev"
                if pd["ref"].startswith("CONN_"): return "conn"
                if pd["ref"].startswith("TP_"): return "tp"
                if "ESD" in pd["ref"] or "ESD" in pd["num"]: return "esd"
                return "other:" + pd["ref"]
            def pick(pl, rl):
                c = [q for q in pl if role(q) == rl]
                return sorted(c, key=lambda q: q["x"])
            somP, somN = pick(P, "som"), pick(N, "som")
            devP, devN = pick(P, "dev"), pick(N, "dev")
            connP, connN = pick(P, "conn"), pick(N, "conn")
            otherP = sorted([q for q in P if role(q) not in ("som", "dev", "conn")], key=lambda q: q["x"])
            otherN = sorted([q for q in N if role(q) not in ("som", "dev", "conn")], key=lambda q: q["x"])

            if src:
                print("   ── SRC 段 (SoM → 器件pad1) ──")
                if somP and somN:
                    print("      SoM 端  : P %s @%.2f   N %s @%.2f  ⇒ %s" %
                          (somP[0]["ref"], somP[0]["x"], somN[0]["ref"], somN[0]["x"],
                           "P在左" if somP[0]["x"] < somN[0]["x"] else "N在左"))
                if devP and devN:
                    print("      器件端  : P %s.pad%s @%.2f   N %s.pad%s @%.2f  ⇒ %s" %
                          (devP[0]["ref"], devP[0]["num"], devP[0]["x"], devN[0]["ref"], devN[0]["num"], devN[0]["x"],
                           "P在左" if devP[0]["x"] < devN[0]["x"] else "N在左"))
                    info["dev_src"] = (devP[0], devN[0])
                # 其它焊盘 (TP/ESD) 在 SRC 网?
                if otherP or otherN:
                    print("      SRC网其它: P=%s N=%s" %
                          ([("%s@%.2f" % (q["ref"], q["x"])) for q in otherP],
                           [("%s@%.2f" % (q["ref"], q["x"])) for q in otherN]))
            else:
                print("   ── POST 段 (器件pad2 → 连接器) ──")
                if devP and devN:
                    print("      器件端  : P %s.pad%s @%.2f   N %s.pad%s @%.2f  ⇒ %s" %
                          (devP[0]["ref"], devP[0]["num"], devP[0]["x"], devN[0]["ref"], devN[0]["num"], devN[0]["x"],
                           "P在左" if devP[0]["x"] < devN[0]["x"] else "N在左"))
                    info["dev_post"] = (devP[0], devN[0])
                if connP and connN:
                    print("      连接器端: P %s.pad%s @%.2f   N %s.pad%s @%.2f  ⇒ %s" %
                          (connP[0]["ref"], connP[0]["num"], connP[0]["x"], connN[0]["ref"], connN[0]["num"], connN[0]["x"],
                           "P在左" if connP[0]["x"] < connN[0]["x"] else "N在左"))
                    info["conn"] = (connP[0], connN[0])
                if otherP or otherN:
                    print("      POST网其它: P=%s" % [("%s@%.2f" % (q["ref"], q["x"])) for q in otherP])
                    print("                  N=%s" % [("%s@%.2f" % (q["ref"], q["x"])) for q in otherN])

        # ── 判定 + 修法可行性 ──
        if "dev_src" in info and "dev_post" in info and "conn" in info:
            p1, n1 = info["dev_src"]       # SRC 脚
            p2, n2 = info["dev_post"]      # POST 脚
            cP, cN = info["conn"]
            # 段1 要求: SoM 端序 == 器件SRC脚序
            somP = [q for q in d[("P", True)] if q["ref"].startswith("J_SOM")]
            somN = [q for q in d[("N", True)] if q["ref"].startswith("J_SOM")]
            if somP and somN:
                seg1_need_Pleft = somP[0]["x"] < somN[0]["x"]
                seg1_have_Pleft = p1["x"] < n1["x"]
                seg2_need_Pleft = cP["x"] < cN["x"]
                seg2_have_Pleft = p2["x"] < n2["x"]
                bad = (seg1_need_Pleft != seg1_have_Pleft) or (seg2_need_Pleft != seg2_have_Pleft)
                print("   ★★ 段1(SoM→SRC脚) 需要 P在左=%s 实测=%s  |  段2(POST脚→连接器) 需要 P在左=%s 实测=%s"
                      % (seg1_need_Pleft, seg1_have_Pleft, seg2_need_Pleft, seg2_have_Pleft))
                if not bad:
                    print("   ⇒ ★★ 两段都一致 ⇒ **不需交叉, 也不需交叉代码**")
                else:
                    # 旋转 N 侧器件 180° 后: n1<->n2 互换 ⇒ 段1/段2 的"器件端序"同时翻转
                    flip1 = (n1["x"] > n2["x"])   # 旋转后 SRC脚 和 POST脚 换位
                    new1 = (p1["x"] < (n2["x"] if flip1 else n1["x"]))
                    new2 = (p2["x"] > (n1["x"] if flip1 else n2["x"]))
                    ok = (new1 == seg1_need_Pleft) and (new2 == seg2_need_Pleft)
                    print("   ⇒ ★旋转 N 侧器件 %s 后: 段1 %s / 段2 %s  ⇒ %s" %
                          ("180°" if flip1 else "(本已反序)",
                           "OK" if new1 == seg1_need_Pleft else "仍冲突",
                           "OK" if new2 == seg2_need_Pleft else "仍冲突",
                           "★**可行: 旋转即可吃掉交叉**" if ok else "仍冲突 ⇒ 需要别的手段"))
                    if ok:
                        fixable += 1

print("\n" + "=" * 92)
print("═══ 汇总: %d 条 lane 中, **%d 条**可靠'旋转/摆放'吃掉交叉 (不必写 crossover 代码) ═══"
      % (total, fixable))
