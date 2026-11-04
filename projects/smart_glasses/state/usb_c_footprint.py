#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
usb_c_footprint.py —— ★demo 主板 USB Type-C 电源口 (J_USB_C) 的**自绘封装** (GCT USB4105-16p)

★★ 为什么必须单独画 (2026-11-04 19:5x 抓到的投板级缺陷):
  原先 J_USB_C 用的是**通用 CONN 假封装** (8 脚) ⇒ ★**物理上插不了 USB 线** (网表写的是 USB4105 16p,
  板上却是 8 脚假封装) ⇒ 而且它被摆在**板中央** (130.55, 46.20; 板 160×100) ⇒ ★**更插不了** ⇒
  ★**demo 板靠这个 Type-C 供电 ⇒ 座不对 = 板子做出来也上不了电**。

★★ 几何真值 (★全部抄 GCT USB4105 原厂图纸 Sheet 1 "Recommended PCB Layout", Rev B3 24/02/23;
   图纸 PDF: https://media.digikey.com/pdf/Data%20Sheets/GCT%20PDFs/USB4105.pdf):
  · **16 个焊盘单排一行**, pitch **0.50mm**, 焊盘长 **1.15mm** (深度方向), 宽 **0.30mm** (12 个) / **0.60mm** (4 个 VBUS 脚)
  · ★**从元件面看, 左→右焊盘顺序**: `A1 B12 A4 B9 B8 A5 B7 A6 A7 B6 A8 B5 B4 A9 B1 A12` (A/B 交错)
  · 焊盘行**中心跨度 7.50mm** (= 15 × 0.50; ★与图纸 "焊料尾总长 8.34±0.06" 互证: 7.50 + 2×0.42 尾长 = 8.34 ✔)
  · **2 × Ø0.65mm 壳体固定孔** (图纸 "2x Ø0.65"), 横向 ±5.78mm (图纸 "5.78")
  · 焊盘区 8.64 × 6.40mm; 图纸另有 "PCB Edge 8.94" ⇒ 见下方"★定位口径"说明
  · ★GCT USB4105 **无现成 KiCad 封装** ⇒ 必须自绘 (与 `HW/PCB/pinout_footprint.json` 登记一致)

★★**定位口径 (★有一处必须与实物复核, 已写进文档)**:
  图纸 "8.94 PCB Edge" 的基准面有两种读法:
    (a) 板边 → 焊盘行中心 ⇒ 座心离板边 8.94mm
    (b) 板边 → 焊料尾外缘 ⇒ 座心离板边 ≈ 9.36mm
  ⇒ ★**本模块按"**插头面与板边齐平**"摆放** (本地坐标: 焊盘行中心 y=0, 插头面在 y=−5.25, 即焊料区深度 6.40 − 焊盘长 1.15)
  ⇒ 这是**唯一保证"插头能插进去"**的口径 ⇒ 两种读法的差 (≤0.42mm) 不影响可插性 (壳体本来就悬出板边)
  ⇒ ★**投板前须与实物/图纸复核**: ① 壳体孔的纵向位置 (图纸 "2x 2.10 / 2x 1.70 / 2x 2.60 / 2x 3.68 / 2x 1.80 / 2x 1.40" 是壳体柱尺寸, 不是孔位) ② 焊盘区 6.40 的基准面

用法:
  from usb_c_footprint import add_usb_c
  add_usb_c(board, netmap, pin_nets, x, y, rot=0)
  · pin_nets: {"A6+B6": "NET_USB_D_P_TYPEC", "A4+A9+B4+B9": "RAIL_DEMO_5V", ...} (网表里的合并脚名)
"""
import math

import pcbnew

MM = 1000000

# ★原厂图纸 Sheet 1 的焊盘顺序 (元件面看, 左→右)
PAD_ORDER = ["A1", "B12", "A4", "B9", "B8", "A5", "B7", "A6", "A7", "B6",
             "A8", "B5", "B4", "A9", "B1", "A12"]
WIDE_PADS = {"A4", "A9", "B4", "B9"}       # VBUS 脚 = 0.60mm 宽
PITCH = 0.50                               # mm
PAD_LEN = 1.15                             # mm (深度方向)
W_NARROW = 0.30
W_WIDE = 0.60
SHELL_HOLE_D = 0.65                        # Ø mm
SHELL_HOLE_X = 5.78                        # 焊盘行中心 → 壳体孔中心
FRONT_OFFSET = 5.25                        # 焊盘行中心 → 插头面 (焊料区深 6.40 − 焊盘长 1.15)
SOLDER_W = 8.64                            # 焊盘区宽
SOLDER_D = 6.40                            # 焊料区深


def V(x, y):
    return pcbnew.VECTOR2I(int(round(x * MM)), int(round(y * MM)))


def _pad_net(pin_nets, pad):
    """pad 名 → 网络 (网表里是 'A6+B6' 这种合并脚名 ⇒ 一个物理脚可能对应多个网名)"""
    for key, net in (pin_nets or {}).items():
        for part in str(key).split("+"):
            if part.strip().upper() == pad:
                return net
    return None


def add_usb_c(board, netmap, pin_nets, x, y, rot=0):
    """在 (x, y) 处放 J_USB_C 封装 (原点在焊盘行中心); 返回 footprint"""
    fp = pcbnew.FOOTPRINT(board)
    fp.SetReference("J_USB_C")
    fp.SetValue("GCT USB4105-16P USB-C 电源口 (自绘, 原厂图纸 Rev B3)")
    fp.SetPosition(V(x, y))
    if rot:
        fp.SetOrientationDegrees(rot)
    board.Add(fp)

    n = len(PAD_ORDER)
    x0 = -(n - 1) * PITCH / 2.0          # A1 在 -3.75, A12 在 +3.75
    for i, pad in enumerate(PAD_ORDER):
        px = x0 + i * PITCH
        w = W_WIDE if pad in WIDE_PADS else W_NARROW
        p = pcbnew.PAD(fp)
        p.SetNumber(pad)
        p.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
        p.SetShape(pcbnew.PAD_SHAPE_RECT)
        p.SetSize(V(w, PAD_LEN))
        p.SetPosition(V(px, 0))
        p.SetLayerSet(p.SMDMask())
        net = _pad_net(pin_nets, pad)
        if net and net in netmap:
            p.SetNet(netmap[net])
        fp.Add(p)

    # 2 个 Ø0.65 壳体固定孔 (通孔, 无网)
    for hx in (-SHELL_HOLE_X, SHELL_HOLE_X):
        h = pcbnew.PAD(fp)
        h.SetNumber("")
        h.SetAttribute(pcbnew.PAD_ATTRIB_NPTH)
        h.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
        h.SetSize(V(SHELL_HOLE_D, SHELL_HOLE_D))
        h.SetPosition(V(hx, -FRONT_OFFSET / 2.0))
        h.SetLayerSet(pad_all_copper := pcbnew.LSET())
        fp.Add(h)

    # F.Fab 本体轮廓 (焊料区 + 壳体固定孔) 与 Courtyard
    def _rect(x0_, y0_, x1_, y1_, layer):
        s = pcbnew.PCB_SHAPE(fp)
        s.SetShape(pcbnew.SHAPE_T_RECT)
        s.SetLayer(layer)
        s.SetStart(V(x0_, y0_))
        s.SetEnd(V(x1_, y1_))
        s.SetWidth(int(0.05 * MM))
        fp.Add(s)
        return s

    fab_x = SOLDER_W / 2.0
    _rect(-fab_x, -FRONT_OFFSET, fab_x, SOLDER_D - FRONT_OFFSET, pcbnew.F_Fab)
    _rect(-fab_x - 0.5, -FRONT_OFFSET - 0.5, fab_x + 0.5, SOLDER_D - FRONT_OFFSET + 0.5,
          pcbnew.F_CrtYd)
    return fp
