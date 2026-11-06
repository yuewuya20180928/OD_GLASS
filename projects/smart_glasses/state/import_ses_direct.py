#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""import_ses_direct.py -- ★★★**直接解析 Specctra SES 并落到 KiCad 板 (2026-11-06 09:4x)**

★★★**为什么不用 KiCad 的 `ImportSpecctraSES` (★实测它失败)**:
  ① freerouting 2.1.0 生成的 SES 用 `(network_out ...)` 块
  ② KiCad 10 的 `ImportSpecctraSES` 对它返回 **False** (★实测: 板写出来了但 **0 段 0 孔**)
  ⇒ ★**不能靠 KiCad 导 ⇒ 自己解析**

★★★**SES 结构 (★实测, freerouting 2.1.0)**:
  ```
  (session fr_board
    (placement ... (component (place REF x y front 0) ...) ...)
    (network_out
      (net NETNAME
        (wire (path LAYER WIDTH x1 y1 x2 y2 ...))
        (via (net NETNAME (via LAYER x y) ...))   ★或 (via (via ...) ...)
      )
    )
  )
  ```
  ★**坐标单位**: SES 里的坐标是 **1/10 µm** (0.1µm) ⇒ ÷10 得 µm ⇒ ÷1000 得 mm
  ★**板坐标**: Specctra 的 y 轴向上, KiCad 的 y 轴向下 ⇒ ★**必须 y' = -y**
  ★**坐标基准**: Specctra 以板原点为基准, KiCad 以左下角为基准 ⇒ ★**y 还要加板高**

★★★**安全**: 只写 --out; 不动输入板

用法:
  bash state/pcbnew_py.sh state/import_ses_direct.py <板> <SES> --out <新板>
"""
import sys
import os
import re

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import pcbnew  # noqa: E402

MM = 1e6


def V(x, y):
    return pcbnew.VECTOR2I(int(round(x * MM)), int(round(y * MM)))


LAYER_MAP = {
    "F.Cu": pcbnew.F_Cu,
    "B.Cu": pcbnew.B_Cu,
    "In1.Cu": pcbnew.In1_Cu,
    "In2.Cu": pcbnew.In2_Cu,
    "In3.Cu": pcbnew.In3_Cu,
    "In4.Cu": pcbnew.In4_Cu,
    "In5.Cu": pcbnew.In5_Cu,
    "In6.Cu": pcbnew.In6_Cu,
    "In7.Cu": pcbnew.In7_Cu,
    "In8.Cu": pcbnew.In8_Cu,
    "In9.Cu": pcbnew.In9_Cu,
    "In10.Cu": pcbnew.In10_Cu,
}


def parse_ses(path):
    """★**解析 SES ⇒ [(kind, net, layer, width, pts)]**"""
    s = open(path, encoding="utf-8", errors="ignore").read()
    out = []

    # ★**走线**: (wire (path LAYER WIDTH x1 y1 x2 y2 ...))
    for m in re.finditer(
            r"\(wire\s*\(path\s+(\S+)\s+(\d+)\s+((?:-?\d+\s+-?\d+\s*)+)\)\s*\)", s):
        lay = m.group(1)
        wid = int(m.group(2))
        nums = [int(x) for x in m.group(3).split()]
        pts = [(nums[k] / 10.0 / 1000.0, nums[k + 1] / 10.0 / 1000.0)
               for k in range(0, len(nums) - 1, 2)]
        if len(pts) >= 2:
            out.append(("seg", None, lay, wid / 10.0 / 1000.0, pts))

    # ★**过孔 (★freerouting 2.1.0 的实际格式, 实测)**:
    #   `(via "Via[0-5]_600:300_um" 379336 -643739)`  ★**带引号的类型名, 没有层名!**
    #   ⇒ ★**类型名里 [0-5] = 跨哪几层** · `600:300` = 盘径:钻孔
    #   ⇒ ★**按 "Via[0-5]" ⇒ 通孔 (F.Cu..B.Cu)**
    for m in re.finditer(r'\(via\s+"([^"]+)"\s+(-?\d+)\s+(-?\d+)', s):
        typ = m.group(1)
        x = int(m.group(2)) / 10.0 / 1000.0
        y = int(m.group(3)) / 10.0 / 1000.0
        # ★**从类型名里解析盘径/钻孔** (★如 "Via[0-5]_600:300_um" ⇒ 0.6mm 盘 / 0.3mm 钻)
        dia = drill = 0.6
        mm = re.search(r"_(\d+):(\d+)_um", typ)
        if mm:
            dia = int(mm.group(1)) / 1000.0
            drill = int(mm.group(2)) / 1000.0
        out.append(("via", None, "THRU", dia, [(x, y, drill)]))
    return out


def main():
    a = sys.argv[1:]
    if len(a) < 2:
        print(__doc__)
        return 2
    boardp, sesp = a[0], a[1]
    outp = None
    i = 2
    while i < len(a):
        if a[i] == "--out":
            outp = a[i + 1]; i += 2
        else:
            i += 1
    if not outp:
        print("★必须给 --out")
        return 2

    board = pcbnew.LoadBoard(boardp)
    for z in board.Zones():
        z.UnFill()

    # ★**板高 (Specctra y 轴向上 ⇒ 要翻转)**
    bb = board.GetBoardEdgesBoundingBox()
    board_h = (bb.GetBottom() - bb.GetTop()) / MM
    print("═══ 直接导入 SES: %s ═══" % sesp)
    print("═══ 板高 %.3fmm · ★**坐标变换 = (x, -y)** (★实测: SES 的 place y 是负的, 板面是正的 ⇒ 直接取负, 不加板高) ═══" % board_h)

    items = parse_ses(sesp)
    print("═══ 解析到 %d 个图元 ═══" % len(items))

    # ★**网名 → 板上 netcode**
    nets = {}
    for code, info in board.GetNetsByNetcode().items():
        nets[info.GetNetname()] = code

    nseg = nvia = nskip = 0
    for (kind, net, lay, wid, pts) in items:
        if kind == "via":
            lid = pcbnew.F_Cu          # ★通孔 (★层对在落板时用 SetLayerPair 设)
        else:
            lid = LAYER_MAP.get(lay)
            if lid is None:
                nskip += 1
                continue
        if kind == "seg":
            # ★**分段: 每个相邻点对一段**
            for k in range(len(pts) - 1):
                x1, y1 = pts[k]
                x2, y2 = pts[k + 1]
                seg = pcbnew.PCB_TRACK(board)
                seg.SetStart(V(x1, -y1))
                seg.SetEnd(V(x2, -y2))
                seg.SetWidth(pcbnew.FromMM(wid if wid > 0 else 0.25))
                seg.SetLayer(lid)
                board.Add(seg)
                nseg += 1
        else:
            x, y = pts[0][0], pts[0][1]
            drill = pts[0][2] if len(pts[0]) > 2 else 0.3
            via = pcbnew.PCB_VIA(board)
            via.SetPosition(V(x, -y))
            via.SetWidth(pcbnew.FromMM(wid if wid > 0 else 0.6))
            via.SetDrill(pcbnew.FromMM(drill))
            via.SetViaType(pcbnew.VIATYPE_THROUGH)
            via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
            board.Add(via)
            nvia += 1

    print("── 落板: 走线 %d 段 / 过孔 %d 个 (跳过 %d 个未知层)" % (nseg, nvia, nskip))
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    board.Save(outp)
    print("── 已写出: %s (%d B)" % (outp, os.path.getsize(outp)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
