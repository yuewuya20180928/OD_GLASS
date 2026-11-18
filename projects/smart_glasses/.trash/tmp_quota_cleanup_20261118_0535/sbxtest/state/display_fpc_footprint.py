#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
display_fpc_footprint.py —— ★demo 主板显示 FPC 座 (CONN_LIGHT) 的**官方封装**生成

★★ 为什么单独一个模块: 板生成器 (`state/gen_pcb_netlist_board.py`) 与网表生成器常被别人改
   ⇒ 把"22p 座的封装几何 + 位置"做成**独立可测模块**, 只留一行调用接口 ⇒ 冲突面最小
   (与 `som_btb_footprint.py` 同套路)。

★★ 几何真值 (全部抄 Raspberry Pi 官方 CM4IO/CM5IO KiCad 设计文件里的官方封装, 见
   HW/PCB/display_fpc_params.json):
  · 座 = **HIROSE FH12-22S-0.5SH(55)** —— 22 脚 / 0.5mm pitch / 右角(水平) / 表面贴装 / 底接触 / 1 固定柱
  · 焊盘 0.3 × 1.3mm 矩形, pitch 0.5mm, y = -1.85 (本体前方), **pad1 在 +x 端** (x=+5.25) ⇒ pad22 在 x=-5.25
  · 本体 F.Fab: x -7.05..+7.05, y -1.2..+3.4; Courtyard ±8.55 × -3.0..+4.9
  · FFC 插入方向 = **-y** (焊盘在本体前方 ⇒ 线从 -y 方向水平插入)

★★**针序不是本模块的事**: 针号 = 网表里的真实针号 (Pi5 DISPLAY 座口径, 见 HW/PCB/PI5_DSI_22P_PINOUT.md),
   本模块只负责"焊盘号 → 位置"。

用法:
  from display_fpc_footprint import add_display_fpc
  add_display_fpc(board, netmap, params_path, pin_net, x, y)   # 在 gen_pcb_netlist_board.py 里调用
"""
import json
import os

import pcbnew

MM = 1000000


def V(x, y):
    return pcbnew.VECTOR2I(int(round(x * MM)), int(round(y * MM)))


def load_params(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def _mkpad(fp, num, net, px, py, w, l, netmap):
    pad = pcbnew.PAD(fp)
    pad.SetNumber(str(num))
    pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
    pad.SetShape(pcbnew.PAD_SHAPE_RECT)
    pad.SetSize(V(w, l))
    pad.SetPosition(V(px, py))
    pad.SetLayerSet(pad.SMDMask())
    if net in netmap:
        pad.SetNet(netmap[net])
    fp.Add(pad)
    return pad


def _seg(fp, x0, y0, x1, y1, layer, width=0.1):
    s = pcbnew.PCB_SHAPE(fp)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetLayer(layer)
    s.SetStart(V(x0, y0))
    s.SetEnd(V(x1, y1))
    s.SetWidth(int(width * MM))
    fp.Add(s)


def _rect(fp, x0, y0, x1, y1, layer, width=0.1):
    _seg(fp, x0, y0, x1, y0, layer, width)
    _seg(fp, x1, y0, x1, y1, layer, width)
    _seg(fp, x1, y1, x0, y1, layer, width)
    _seg(fp, x0, y1, x0, y0, layer, width)


def _circle(fp, cx, cy, r, layer, width=0.12):
    c = pcbnew.PCB_SHAPE(fp)
    c.SetShape(pcbnew.SHAPE_T_CIRCLE)
    c.SetLayer(layer)
    c.SetCenter(V(cx, cy))
    c.SetEnd(V(cx + r, cy))
    c.SetWidth(int(width * MM))
    fp.Add(c)


def add_display_fpc(board, netmap, params_path, pin_net, x=None, y=None,
                    ref="CONN_LIGHT", value="HIROSE FH12-22S-0.5SH(55) 22p 0.5mm"):
    """在板上放 22p 显示 FPC 座。

    pin_net: {1: "GND", 2: "DSI_D0_D1_N", ...} —— 针号 → 网络
    返回 (ref, 焊盘数)
    """
    P = load_params(params_path)
    pl = P.get('placement', {})
    x = pl.get('x', 138.0) if x is None else x
    y = pl.get('y', 14.0) if y is None else y

    fp = pcbnew.FOOTPRINT(board)
    fp.SetReference(ref)
    fp.SetValue(value)
    try:
        fp.Reference().SetLayer(pcbnew.F_Fab)
        fp.Reference().SetVisible(False)
        fp.Value().SetLayer(pcbnew.F_Fab)
        fp.Value().SetVisible(False)
    except Exception:
        pass

    # --- 焊盘 (官方: 22 个, 0.3×1.3, pitch 0.5, y=-1.85, pad1 在 +x 端) ---
    n = int(P['circuits'])
    pitch = float(P['pitch'])
    x1 = float(P['pad1_x'])
    for i in range(n):
        num = i + 1
        px = x1 - i * pitch
        net = pin_net.get(num)
        _mkpad(fp, num, net, px, float(P['pad_y']),
               float(P['pad_w']), float(P['pad_l']), netmap)

    # --- 本体 (F.Fab) + 固定柱 ---
    fx0, fy0, fx1, fy1 = P['fab_body']
    _rect(fp, fx0, fy0, fx1, fy1, pcbnew.F_Fab)
    qx0, qy0, qx1, qy1 = P['fab_post']
    _rect(fp, qx0, qy0, qx1, qy1, pcbnew.F_Fab)
    _rect(fp, -qx1, qy0, -qx0, qy1, pcbnew.F_Fab)
    cx, cy, r = P['post_circle']
    _circle(fp, cx, cy, r, pcbnew.F_Fab, 0.1)

    # --- 丝印: ★**照官方封装逐段画** (官方丝印**不是整框**: 前沿只在焊盘区外有线,
    #     两侧也留断口 ⇒ 否则前沿会横穿 22 个焊盘 ⇒ DRC 报 silk_over_copper) ---
    sx0, sy0, sx1, sy1 = P['silk']
    _seg(fp, sx0, sy0, sx0, 0.04, pcbnew.F_SilkS, 0.12)            # 左前沿
    _seg(fp, sx0, 2.76, sx0, sy1, pcbnew.F_SilkS, 0.12)             # 左后沿
    _seg(fp, sx0, sy1, sx1, sy1, pcbnew.F_SilkS, 0.12)             # 后沿
    _seg(fp, 5.66, sy0, sx1, sy0, pcbnew.F_SilkS, 0.12)            # 右前沿 (焊盘区外)
    _seg(fp, sx1, sy0, sx1, 0.04, pcbnew.F_SilkS, 0.12)            # 右侧上段
    _seg(fp, sx1, sy1, sx1, 2.76, pcbnew.F_SilkS, 0.12)            # 右侧下段
    _seg(fp, -5.66, sy0, sx0, sy0, pcbnew.F_SilkS, 0.12)           # 左前沿 (焊盘区外)
    _seg(fp, -5.66, sy0, -5.66, -2.5, pcbnew.F_SilkS, 0.12)        # pin1 侧标记
    _circle(fp, cx, cy, r, pcbnew.F_SilkS, 0.12)                   # pin1 标记圈

    # --- Courtyard ---
    cx0, cy0, cx1_, cy1_ = P['courtyard']
    _rect(fp, cx0, cy0, cx1_, cy1_, pcbnew.F_CrtYd, 0.05)

    fp.SetPosition(V(x, y))
    board.Add(fp)
    return (ref, n)
