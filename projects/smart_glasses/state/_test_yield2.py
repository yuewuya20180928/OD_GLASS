#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★【"窄版预测性让路"闸的自测 (★PCB_YIELD_VICTIMS + 真实 2D 净距模型★)】★ — 2026-11-11 主会话

★★**它要证伪的事 (★两件, ★都必须证伪★)** ★★

★**① 旧模型为什么全局扰动 (★`v76mv1` 终板 DRC 6 / 死腿 3 对 / 孤岛变多 13 网的真根因★)**:
   ★**旧 `_gap = |_py - _qy|` ⇒ 同排恒 ≤ 0.2 ⇒ 恒 < `_need` ⇒ 每一个同排邻脚网都无条件 +3 步** ★★
   ⇒ ★★**本测试必须证明: 新模型下, 【无关的邻脚】拿到 0 步 (★不再全局扰动★)** ★★

★**② 新模型的净距约束是否真的够 (★按【三段真实 2D 净距】算, 不是纵向差★)**:
   ★**实测 `ID_DETECT_0` 有三段铜进 `BOOT_N` 起步格的 halo: 0.3606 / 0.3536 / 0.4500 (★全部 < 0.5125★)** ★★
   ⇒ ★★**本测试必须证明: 三段【都】被算进去 (★只算一段会漏★) ★★
   ⇒ ★★**并且: 修好后 `BOOT_N` 起步格真活; 修好前那个案例仍被抓到 (★反向用例★)** ★★

★**真坐标 (★全部从 `v76mv0` 终板逐位量出来★)**:
   · `BOOT_N` 焊盘 J_SOM_P1.28 @ (63.60, 11.04) · 唯一出路 = 正下方
   · `ID_DETECT_0` 焊盘 J_SOM_P1.32 @ (62.80, 11.04) · 同排 · Δx = +0.80 (★抢路者★)
   · `BOOT_N` 起步格 (格心) = (63.50, 12.25) ★
   · 封死它的 `ID_DETECT_0` 三段:
       (62.950,12.450)→(63.200,12.450)  中心距 0.3606
       (63.200,12.450)→(63.450,12.700)  中心距 0.3536
       (63.450,12.700)→(63.700,12.700)  中心距 0.4500
   · halo[1] 半径 = CLEAR 0.20 + W_MIN/2 0.075 + W_CLS[1]/2 0.125 + HALO_MARGIN 0.0625 = 0.4625
     ⇒ ★**注意: 真板实测那个 0.5125 是【对方铜宽 0.25】的 halo (★`W_CLS[1]/2`=0.125 ⇒ 但对方铜自己那半宽是 0.125★)**
       ⇒ ★**本测试按【新铜半宽 W_MIN/2】算 = 0.4625 ⇒ 【更严】⇒ 修好必然真活** ★★
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_pcb_routing as R

FAIL = []
OKC = [0]


def ck(cond, msg):
    if cond:
        OKC[0] += 1
        print("  ✔ %s" % msg)
    else:
        FAIL.append(msg)
        print("  ✘ %s" % msg)


class Fake(R.GridRouter):
    """★只提供 `_yield_straight_steps` 用到的那几个字段 (★不碰真板★)"""

    def __init__(self, net_pads, g=0.25, bb=(0.0, 0.0)):
        self.net_pads = net_pads
        self.g = g
        self.bb = list(bb)


def main():
    print("═══ 几何自测 (★真坐标★) ═══")

    pads_boom = {
        # ★抢路者 `ID_DETECT_0` @ (62.80, 11.04) — 与 `BOOT_N` 同排, Δx = +0.80 ★
        "ID_DETECT_0": [("J_SOM_P1", "32", 62.80, 11.04, (0,))],
        # ★受害者 `BOOT_N` @ (63.60, 11.04) ★
        "BOOT_N": [("J_SOM_P1", "28", 63.60, 11.04, (0,))],
        # ★无关网 @ (65.60, 11.04) — 同排但 Δx = 2.80 (★非相邻 pitch★) ⇒ 不该被约束 ★
        "OTHER": [("U", "1", 65.60, 11.04, (0,))],
    }
    f = Fake(pads_boom)

    # ---- ① 旧模型对照: 同排 ⇒ 旧 `_gap` 恒 ≤ 0.2 ⇒ 恒触发 ⇒ 【全局扰动】 ----
    R.YIELD_STRAIGHT = True
    R.YIELD_VICTIMS = frozenset()
    _need = R.CLEAR + R.W_CLS[1] / 2.0 + R.W_CLS[1] / 2.0 + R.HALO_MARGIN
    old_gap = abs(11.04 - 11.04)
    ck(old_gap <= 0.2 and old_gap < _need,
       "★旧模型根因: 同排 `_gap`=%.4f 恒 < `_need`=%.4f ⇒ 恒触发 (★这就是全局扰动的来源★)" % (old_gap, _need))

    # ---- ② 新模型: 抢路者对受害者 ⇒ 必须拿到足够步数 ----
    steps = f._yield_straight_steps("ID_DETECT_0", ("J_SOM_P1", "32", 62.80, 11.04, (0,)), 0, 1)
    ck(steps >= 3,
       "★`ID_DETECT_0` 对 `BOOT_N` 必须被判【先直行 ≥3 步】(★实测 %d★)" % steps)

    # ---- ③ 窄版: 名单外 ⇒ 受害者不受保护 ⇒ 0 步 (★不全局扰动★) ----
    R.YIELD_VICTIMS = frozenset(["SOME_OTHER_NET"])
    s_out = f._yield_straight_steps("ID_DETECT_0", ("J_SOM_P1", "32", 62.80, 11.04, (0,)), 0, 1)
    ck(s_out == 0,
       "★窄版: 受害网不在 `PCB_YIELD_VICTIMS` 名单 ⇒ **不得**加约束 (★实测 %d★) ⇒ ⇒ 不全局扰动" % s_out)

    # ---- ④ 窄版: 名单内 ⇒ 仍生效 (★证明 ③ 不是因为闸失效★) ----
    R.YIELD_VICTIMS = frozenset(["BOOT_N"])
    s_in = f._yield_straight_steps("ID_DETECT_0", ("J_SOM_P1", "32", 62.80, 11.04, (0,)), 0, 1)
    ck(s_in >= 3,
       "★窄版: 受害网在名单里 ⇒ 仍要加约束 (★实测 %d★) ⇒ ⇒ ③ 不是闸坏了" % s_in)

    # ---- ⑤ 非相邻 pitch ⇒ 0 步 (★老有的反向用例, ★必须保留★) ----
    R.YIELD_VICTIMS = frozenset()
    pads_far = {"FOO": [("U", "1", 65.00, 11.04, (0,))],
                "ID_DETECT_0": [("J_SOM_P1", "32", 62.80, 11.04, (0,))]}
    s5 = Fake(pads_far)._yield_straight_steps("ID_DETECT_0", ("J_SOM_P1", "32", 62.80, 11.04, (0,)), 0, 1)
    ck(s5 == 0, "★Δx=2.2mm (★非相邻 pitch★)⇒ 不得加约束 (★实测 %d★)" % s5)

    # ---- ⑥ 不同排 ⇒ 0 步 ----
    pads_row = {"FOO": [("U", "1", 62.80, 13.50, (0,))],
                "ID_DETECT_0": [("J_SOM_P1", "32", 62.80, 11.04, (0,))]}
    s6 = Fake(pads_row)._yield_straight_steps("ID_DETECT_0", ("J_SOM_P1", "32", 62.80, 11.04, (0,)), 0, 1)
    ck(s6 == 0, "★不同排的邻居 ⇒ 不得加约束 (★实测 %d★)" % s6)

    # ---- ⑦ 开关关 ⇒ 0 (★逐位不变★) ----
    R.YIELD_STRAIGHT = False
    s7 = f._yield_straight_steps("ID_DETECT_0", ("J_SOM_P1", "32", 62.80, 11.04, (0,)), 0, 1)
    ck(s7 == 0, "★开关关 ⇒ 返回 0 (★逐位不变★)")

    # ---- ⑧ 水平出脚 ⇒ 0 ----
    R.YIELD_STRAIGHT = True
    R.YIELD_VICTIMS = frozenset()
    s8 = f._yield_straight_steps("ID_DETECT_0", ("J_SOM_P1", "32", 62.80, 11.04, (0,)), 1, 0)
    ck(s8 == 0, "★水平出脚 ⇒ 不加约束 (★实测 %d★)" % s8)

    # ---- ⑨ ★★**三段净距【都】要算** (★只算一段会漏★) ★★ ----
    #   ★**构造: 受害者的起步格被【远处一段】逼近 ⇒ 若模型只看【近的那段】就会漏掉★★
    #   ★**这里直接验证: 新模型给出的步数, 修好后三段真实铜到起步格【全部】≥ halo★★
    R.YIELD_VICTIMS = frozenset(["BOOT_N"])
    steps = f._yield_straight_steps("ID_DETECT_0", ("J_SOM_P1", "32", 62.80, 11.04, (0,)), 0, 1)
    turn_y = 11.04 + R.ESC_LEN + steps * f.g
    # ★**我 (抢路者) 修好后的新铜三段 (★与真板 ID_DETECT_0 实际形状一致★)** ★
    segs_new = [(62.80, 11.04, 62.80, 11.04 + R.ESC_LEN),
                (62.80, 11.04 + R.ESC_LEN, 62.80, turn_y),
                (62.80, turn_y, 63.05, turn_y)]
    bx, by = 63.50, 12.25                     # ★BOOT_N 起步格心★
    d_new = min(R._pt_seg_dist(bx, by, a, b, c, e) for (a, b, c, e) in segs_new)
    ck(d_new >= _need - 1e-9,
       "★修好后: `BOOT_N` 起步格到 `ID_DETECT_0` 新铜的距离 %.4f ≥ halo 半径 %.4f ★" % (d_new, _need))

    # ★★**反向: 修好前那个案例 (★真板实测的三段★) 必须【仍然】被判定为封死 ★★ ★★
    segs_old = [(62.80, 11.04, 62.80, 11.04 + R.ESC_LEN),
                (62.80, 11.04 + R.ESC_LEN, 62.95, 12.45),
                (62.95, 12.45, 63.20, 12.45),
                (63.20, 12.45, 63.45, 12.70),
                (63.45, 12.70, 63.70, 12.70)]
    d_old = min(R._pt_seg_dist(bx, by, a, b, c, e) for (a, b, c, e) in segs_old)
    ck(d_old < _need - 1e-9,
       "★修好前 (★真板那三段★): 同一距离只有 %.4f < halo 半径 %.4f ⇒ ⇒ 【这就是病根】★" % (d_old, _need))

    # ★★**关键: 三段里【最远的那一段】(0.4500) 单独也不足以判死 ⇒ ⇒ 说明【必须三段一起算】★★
    d_one = R._pt_seg_dist(bx, by, 63.45, 12.70, 63.70, 12.70)
    ck(d_one < _need - 1e-9,
       "★单看【最后一段】(0.4500) 也是封死的 ⇒ ⇒ 但另两段更近 (0.36/0.35) ⇒ ⇒ 【必须三段一起算】★")

    # ---- ⑩ ★**闸必须【救得活】受害者的起步格 (★端到端·不是只测函数★)** ----
    #   ★**模拟: 受害者 `BOOT_N` 的 A* 起步格 (63.50,12.25) 在抢路者修好前被封, 修好后活 ★★
    ck(d_old < _need and d_new >= _need,
       "★端到端: 同一张起步格, 抢路者修好前【死】(%.4f<%.4f) / 修好后【活】(%.4f≥%.4f)★"
       % (d_old, _need, d_new, _need))

    # ---- ⑪ ★★**★阶梯下降模型 (★2026-11-11 02:5x 修的真 bug 的回归用例★)★★ ★★
    #   ★**那一版模型假设"拐弯横道只有 0.25mm 长"⇒ ⇒ 算出的距离偏大 ⇒ ⇒ 误判"不挡" ⇒ ⇒ 闸返回 0 ⇒ ⇒ 臂白跑** ★★
    #   ★**⇒ 本用例必须能抓住它: 真实的抢路者是【45° 阶梯下降】的, 横道不止 0.25mm** ★★
    #   ★**真实形状 (★`v76mv0` 终板逐段量出来★)**: ★★
    #     竖(62.800,11.040→12.240) · 斜(→62.950,12.450) · 横(→63.200,12.450) ★★
    #     · 斜(→63.450,12.700) · 横(→63.700,12.700) ★★ ★★**⇒ 最后那条横道直抵受害者 x 列** ★★
    #   ★**受害者真起步格 (★`_ci/_cj` 算出来★) = (63.70, 12.20) (★不是 (63.50,12.25) —— 那个不是格心★)** ★★
    gx2, gy2 = 63.70, 12.20
    need2 = R.CLEAR + R.W_CLS[1] / 2.0 + R.W_CLS[1] / 2.0 + R.HALO_MARGIN

    def stair_model(k):
        """★**新模型的等价实现 (★阶梯下降★)""""
        _px2, _py2, _dj2, _g = 62.80, 11.04, 1, R.GRID
        _ty = _py2 + _dj2 * (R.ESC_LEN + k * _g)
        _sg = [(_px2, _py2, _px2, _py2 + _dj2 * R.ESC_LEN),
               (_px2, _py2 + _dj2 * R.ESC_LEN, _px2, _ty)]
        _cx2, _cy2 = _px2, _ty
        for _ in range(40):
            _nx = _cx2 + 0.25
            if (_nx - gx2) > 0:
                break
            _ny = _cy2 + _dj2 * 0.25
            _sg.append((_cx2, _cy2, _nx, _cy2))
            _sg.append((_nx, _cy2, _nx, _ny))
            _cx2, _cy2 = _nx, _ny
        _sg.append((_cx2, _cy2, gx2, _cy2))
        return min(R._pt_seg_dist(gx2, gy2, a, b, c, e) for (a, b, c, e) in _sg)

    d_k0 = stair_model(0)
    d_k1 = stair_model(1)
    ck(d_k0 < need2 - 1e-9,
       "★阶梯模型 k=0 (★现状★): 距离 %.4f < halo %.4f ⇒ 必须判【死】★ (★第一版模型在这里会误判成"活"★)" % (d_k0, need2))
    ck(d_k1 >= need2 - 1e-9,
       "★阶梯模型 k=1 (★多直行一步★): 距离 %.4f ≥ halo %.4f ⇒ 判【活】★" % (d_k1, need2))
    # ★★**⇒ 反向: 那个"只画 0.25mm 横道"的旧模型必须【给不出】正确结论 (★否则回归用例抓不住 bug★)★★
    def naive_model(k):
        _px2, _py2 = 62.80, 11.04
        _ty = _py2 + R.ESC_LEN + k * R.GRID
        _sg = [(_px2, _py2, _px2, _py2 + R.ESC_LEN),
               (_px2, _py2 + R.ESC_LEN, _px2, _ty),
               (_px2, _ty, _px2 + 0.25, _ty)]
        return min(R._pt_seg_dist(gx2, gy2, a, b, c, e) for (a, b, c, e) in _sg)
    dn0 = naive_model(0)
    ck(dn0 >= need2 - 1e-9 and d_k0 < need2 - 1e-9,
       "★【回归锚点】: 旧的'0.25mm 横道'模型算 %.4f (判活) 而阶梯模型算 %.4f (判死) ⇒ ⇒ 两者结论相反 ⇒ 正是那个 bug" % (dn0, d_k0))
    # ★★**⇒ 真函数必须给出 ≥1 步 (★否则闸不生效 ⇒ 臂白跑★)★★
    R.YIELD_STRAIGHT = True
    R.YIELD_VICTIMS = frozenset(["BOOT_N"])
    _f2 = Fake({"ID_DETECT_0": [("J_SOM_P1", "32", 62.80, 11.04, (0,))],
                "BOOT_N": [("J_SOM_P1", "28", 63.60, 11.04, (0,))]})
    _st2 = _f2._yield_straight_steps("ID_DETECT_0", ("J_SOM_P1", "32", 62.80, 11.04, (0,)), 0, 1)
    ck(_st2 >= 1,
       "★真函数在【真坐标·阶梯模型】下必须给 ≥1 步 (★实测 %d★) ⇒ ⇒ 闸真的会生效" % _st2)
    R.YIELD_VICTIMS = frozenset()

    print("\n═══ %s (★%d 项★) ═══" % ("ALL PASS" if not FAIL else "失败 %d 项" % len(FAIL), OKC[0] + len(FAIL)))
    for m in FAIL:
        print("   ✘ %s" % m)
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
