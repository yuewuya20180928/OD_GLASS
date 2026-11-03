#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tmp117_footprint.py —— ★TI TMP117 (WSON-6, DRV0006B) 的官方 land pattern 封装生成

★★ 为什么要单独一个模块: 板生成器里的**通用 IC 封装是"假封装"** (1.27mm pitch 的两排焊盘),
   而 TMP117 是 **2×2mm WSON-6 / 0.65mm 脚距 / 每脚 0.45×0.30mm** ⇒ 两者完全不是一回事。

★★ 几何真值 (出处: Texas Instruments TMP117 datasheet SNOSD82D, 图纸号 **4223922/A 09/2017**):
  · 封装: **WSON (6) = DRV0006B**, 2.00 × 2.00 mm, 0.8mm max height
  · 脚位 (datasheet §5 Table 5-1 "Pin Functions"):
      1 = SCL   2 = GND   3 = ALERT   4 = ADD0   5 = V+   6 = SDA
  · 脚距: **0.65mm** (原图 "4X (0.65)" = 两列各 2 个间距)
  · 焊盘: 每脚 **0.45 × 0.30mm** (原图 "6X (0.45)" / "6X (0.3)")
  · 两列焊盘中心间距: **1.95mm** (原图 "(1.95)")
  · 散热焊盘 (EP): 原厂明确 **"The package thermal pad is not connected to the device ground and
    should be left unsoldered for best measurement accuracy"** (datasheet §10) ⇒
    ★**本封装不画 EP 焊盘** (按原厂建议留空不焊 ⇒ 温度精度最好; 皮肤侧测温尤其要这样)
  · 尺寸复核: 图纸矢量测量 (页 41 矢量路径, 比例 59.48 pt/mm, 由 (1.95) 与 0.65 两处标注互证):
    列中心 x = ±0.975mm, 行中心 y = 0 / ±0.65mm ✔ 与标注一致

用法 (由 gen_pcb_netlist_board.py 调用):
  from tmp117_footprint import add_tmp117
  add_tmp117(board, netmap, pins, x, y)      # pins = [(焊盘号, 网络, 类型)]
"""
import pcbnew

MM = 1000000

# ---- 官方几何 (单位 mm) ----
PAD_W = 0.45          # 径向 (x)
PAD_H = 0.30          # 切向 (y)
COL_X = 0.975         # 列中心距原点 (两列中心相距 1.95)
ROW_Y = (0.65, 0.0, -0.65)
BODY = 2.00           # 本体 2.0 x 2.0
# 焊盘号 → (x, y) —— ★按 TI Figure 5-1 (从顶面看, 1 号在左上, 逆时针)
#   KiCad 的 +y 指向屏幕下方 ⇒ y=-0.65 是"上"
PAD_POS = {
    "1": (-COL_X, -ROW_Y[0]),   # SCL   左上
    "2": (-COL_X, -ROW_Y[1]),   # GND   左中
    "3": (-COL_X, -ROW_Y[2]),   # ALERT 左下
    "4": (COL_X, ROW_Y[2]),     # ADD0  右下
    "5": (COL_X, ROW_Y[1]),     # V+    右中
    "6": (COL_X, ROW_Y[0]),     # SDA   右上
}


def V(x, y):
    return pcbnew.VECTOR2I(int(round(x * MM)), int(round(y * MM)))


def _seg(fp, x0, y0, x1, y1, layer, width=0.1):
    s = pcbnew.PCB_SHAPE(fp)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetLayer(layer)
    s.SetStart(V(x0, y0))
    s.SetEnd(V(x1, y1))
    s.SetWidth(int(width * MM))
    fp.Add(s)


def add_tmp117(board, netmap, pins, x, y, ref="U_TEMP",
               value="TI TMP117 (WSON-6 DRV0006B, 2x2mm)"):
    """放 TMP117 封装。pins = [(焊盘号, 网络, 类型)]"""
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

    # 本体 (F.Fab) 2.0 x 2.0 + 1 号角的标记 (原厂 PIN 1 INDEX AREA)
    b = BODY / 2.0
    _seg(fp, -b, -b, b, -b, pcbnew.F_Fab)
    _seg(fp, b, -b, b, b, pcbnew.F_Fab)
    _seg(fp, b, b, -b, b, pcbnew.F_Fab)
    _seg(fp, -b, b, -b, -b + 0.35, pcbnew.F_Fab)          # 1 号角切角
    _seg(fp, -b, -b + 0.35, -b + 0.35, -b, pcbnew.F_Fab)

    # 焊盘
    for (num, net, _kind) in pins:
        num = str(num)
        if num not in PAD_POS:
            continue
        px, py = PAD_POS[num]
        pad = pcbnew.PAD(fp)
        pad.SetNumber(num)
        pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
        pad.SetShape(pcbnew.PAD_SHAPE_RECT)
        pad.SetSize(V(PAD_W, PAD_H))
        pad.SetPosition(V(px, py))
        pad.SetLayerSet(pad.SMDMask())
        if net in netmap:
            pad.SetNet(netmap[net])
        fp.Add(pad)

    # Courtyard (本体 + 焊盘外扩 0.25)
    c = BODY / 2.0 + 0.25
    _seg(fp, -c, -c, c, -c, pcbnew.F_CrtYd, 0.05)
    _seg(fp, c, -c, c, c, pcbnew.F_CrtYd, 0.05)
    _seg(fp, c, c, -c, c, pcbnew.F_CrtYd, 0.05)
    _seg(fp, -c, c, -c, -c, pcbnew.F_CrtYd, 0.05)

    fp.SetPosition(V(x, y))
    board.Add(fp)
    return fp
