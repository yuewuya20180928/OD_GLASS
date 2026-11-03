#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
som_btb_footprint.py —— ★SoM 承载板上 4 组 100pin BTB 座 (Hirose DF40C-100DS) 的封装生成

★★ 为什么单独一个模块: 板生成器 (`state/gen_pcb_netlist_board.py`) 与网表生成器都在被别人改
   ⇒ 把"4 个座的封装 + 位置"做成**独立可测模块**, 只留一行调用接口 ⇒ 冲突面最小。

★★ 几何真值 (全部来自公开资料, 逐条列在 HW/PCB/som_btb_params.json):
  · 座 = **Hirose DF40C-100DS-0.4V(51)** (载板侧插座; SoM 侧是 DF40C-100DP-0.4V(51))
    - 手册 §5 给的 "载板侧 A=22.6 B=19.6 C=3.2 D=1.45" 与 Hirose 目录的 DF40C-100DS 行**逐字一致** ✓
  · 脚号编排: **双排, 奇数脚 = 一排, 偶数脚 = 另一排** (与手册 §2.6.2 的"奇脚表/偶脚表"结构一致
    ⇒ 与 SoM 侧 DF40C-100DP 的编号惯例同源 ⇒ ★**我们的焊盘 n 正好对插 SoM 的 n 脚**)
  · ★**行距 / 焊盘长度**在公开目录里只给了 2.38 / 3.78 两个综合尺寸 ⇒ 取自洽解
    (焊盘长 1.4 ⇒ 2.38 + 1.4 = 3.78 = 焊盘图形总宽) ⇒ ★**下料前必须用原厂工程图核对**

用法:
  from som_btb_footprint import add_som_connectors
  add_som_connectors(board, netmap, params_path)   # 在 gen_pcb_netlist_board.py 里调用
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


def _fab_rect(fp, x0, y0, x1, y1, layer=None):
    layer = layer or pcbnew.F_Fab
    pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]
    for i in range(4):
        seg = pcbnew.PCB_SHAPE(fp)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetLayer(layer)
        seg.SetStart(V(*pts[i]))
        seg.SetEnd(V(*pts[i + 1]))
        seg.SetWidth(int(0.1 * MM))
        fp.Add(seg)


def add_som_connectors(board, netmap, params_path, pin_net):
    """在板上放 4 组 100pin BTB 座。

    pin_net: { "P1": {1: "NET_NAME", 2: ..., ...}, ... } —— 每个座每个脚的网络
    返回 [(ref, 脚数), ...]
    """
    P = load_params(params_path)
    contacts = P['contacts']
    rows = P['rows']
    pitch = P['pitch']
    pw = P['pad_w']
    pl = P['pad_l']
    rp = P['row_pitch']
    ox, oy = P['som_origin']
    out = []

    for conn in ('P1', 'P2', 'P3', 'P4'):
        cx, cy = P['conn_centers'][conn]
        # ★SoM 上的座坐标 → 主板坐标 (主板把 SoM 放在 som_origin, 座中心随之平移)
        px = ox + cx
        py = oy + cy
        fp = pcbnew.FOOTPRINT(board)
        fp.SetReference(f'J_SOM_{conn}')
        fp.SetValue(f'Hirose DF40C-100DS-0.4V(51) 100pin 0.4mm (SOM {conn}) '
                    f'★几何待原厂图纸核对')
        for fld in (fp.Reference(), fp.Value()):
            try:
                fld.SetLayer(pcbnew.F_Fab)
                fld.SetVisible(False)
            except Exception:
                pass
        # 座外形 (F.Fab): 22.6 长 (沿 x) × 3.2 宽 (沿 y)
        bl = P['body_len'] / 2.0
        bw = P['body_w'] / 2.0
        _fab_rect(fp, -bl, -bw, bl, bw)
        # 焊盘: 双排 · 奇数脚排 A (y = -rp/2), 偶数脚排 B (y = +rp/2)
        #   排内第 k 个脚 (k=0..49) 的 x = (k - 24.5) * pitch  (50 脚跨距 19.6mm)
        half = contacts // rows          # 50
        for n in range(1, contacts + 1):
            if n % 2 == 1:               # 奇数脚 → 排 A
                k = (n - 1) // 2
                row_y = -rp / 2.0
            else:                         # 偶数脚 → 排 B
                k = (n - 2) // 2
                row_y = +rp / 2.0
            x = (k - (half - 1) / 2.0) * pitch
            net = pin_net.get(conn, {}).get(n)
            _mkpad(fp, n, net, x, row_y, pw, pl, netmap)
        fp.SetPosition(V(px, py))
        board.Add(fp)
        out.append((f'J_SOM_{conn}', len(pin_net.get(conn, {}))))
    return out
