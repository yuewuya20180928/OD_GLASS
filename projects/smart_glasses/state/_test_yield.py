#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★【"预测性让路"闸的自测 (★PCB_YIELD_STRAIGHT★)】★ — 2026-11-10 主会话

★★**它要证伪的事**: ★★**"同排相邻脚的出脚道 ⇒ 我必须先直行到让开它为止" 这条机制
   是不是真的能解决 `BOOT_N` 起步格被封死这件事**★★

★**测试用真坐标 (★从 v76ml 终板逐位量出来★)**:
   · `BOOT_N` 焊盘 J_SOM_P1.28 @ (63.60, 11.04) · 唯一出路 = 正下方
   · `ID_DETECT_0` 焊盘 J_SOM_P1.32 @ (62.80, 11.04) · 同排 · Δx = -0.80
   · 挡 `BOOT_N` 起步格 (63.50, 12.25) 的是 `ID_DETECT_0` 的拐弯链 (63.45,12.70)→(63.70,12.70) w=0.25
     ⇒ 中心距 0.450mm < halo[1] 半径 0.5125mm ⇒ 差 0.0125mm
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


def main():
    print("═══ 几何自测 (★真坐标★) ═══")
    # ★★**① 算出"预测性让路"需要的步数 ★★**
    class Fake(R.GridRouter):
        def __init__(self):
            self.net_pads = {
                "ID_DETECT_0": [("J_SOM_P1", "32", 62.80, 11.04, (0,))],
                "BOOT_N": [("J_SOM_P1", "28", 63.60, 11.04, (0,))],
            }
            self.g = R.GRID

    f = Fake()
    R.YIELD_STRAIGHT = True
    # ★★**`ID_DETECT_0` 出脚方向 = 下 (0,+1) ⇒ 它的拐弯不得进入 `BOOT_N` 的预测出脚道 halo ★★**
    steps = f._yield_straight_steps("ID_DETECT_0", ("J_SOM_P1", "32", 62.80, 11.04, (0,)), 0, 1)
    ck(steps >= 2, "★`ID_DETECT_0` 必须被判【先直行 ≥2 步】(★实测得 %d★)" % steps)
    ck(steps >= 3, "★步数要够 (★halo 半径 0.5125 ⇒ 0.450 的缺口要 3 步·实测 %d★)" % steps)

    # ★★**② 校验算出来的步数【真的】让开了邻居的预测出脚道 ★★**
    py, qy = 11.04, 11.04
    my_turn_y = py + 1 * (R.ESC_LEN + steps * f.g)
    q_end_y = qy + 1 * R.ESC_LEN
    need = R.CLEAR + R.W_MIN / 2.0 + R.W_CLS[1] / 2.0 + R.HALO_MARGIN
    ck(abs(my_turn_y - q_end_y) >= need - 1e-9,
       "★让开后的垂直间距 %.4f ≥ halo 半径 %.4f ★" % (abs(my_turn_y - q_end_y), need))

    # ★★**③ 反向用例: ★不在同一排 ⇒ 不得约束 (★闸不许乱杀★)★★**
    f2 = Fake()
    f2.net_pads = {"FOO": [("U", "1", 62.80, 13.50, (0,))],
                   "ID_DETECT_0": [("J_SOM_P1", "32", 62.80, 11.04, (0,))]}
    s3 = f2._yield_straight_steps("ID_DETECT_0", ("J_SOM_P1", "32", 62.80, 11.04, (0,)), 0, 1)
    ck(s3 == 0, "★不同排的邻居 ⇒ 【不得】加约束 (★实测 %d★)" % s3)

    # ★★**④ 反向用例: ★同排但 Δx 太大 (不是相邻 pitch) ⇒ 不得约束 ★★**
    f3 = Fake()
    f3.net_pads = {"FOO": [("U", "1", 65.00, 11.04, (0,))],
                   "ID_DETECT_0": [("J_SOM_P1", "32", 62.80, 11.04, (0,))]}
    s4 = f3._yield_straight_steps("ID_DETECT_0", ("J_SOM_P1", "32", 62.80, 11.04, (0,)), 0, 1)
    ck(s4 == 0, "★Δx=2.2mm (★非相邻 pitch★)⇒ 不得加约束 (★实测 %d★)" % s4)

    # ★★**⑤ 开关关 ⇒ 必须【逐位不变】(★返回 0·不写任何约束★)★★
    R.YIELD_STRAIGHT = False
    s5 = f._yield_straight_steps("ID_DETECT_0", ("J_SOM_P1", "32", 62.80, 11.04, (0,)), 0, 1)
    ck(s5 == 0, "★开关关 ⇒ 返回 0 (★逐位不变★)")

    # ★★**⑥ 水平出脚 ⇒ 不处理 (★只治垂直出脚的真情形★)★★
    R.YIELD_STRAIGHT = True
    s6 = f._yield_straight_steps("ID_DETECT_0", ("J_SOM_P1", "32", 62.80, 11.04, (0,)), 1, 0)
    ck(s6 == 0, "★水平出脚 ⇒ 不加约束 (★实测 %d★)" % s6)

    # ★★**⑦ 【真臂板证据】: ★`BOOT_N` 的起步格现在【不再】被 `ID_detect_0` 的 halo 封死 ★★
    #   ★**修好后的 `ID_DETECT_0` 走线**: ★【出脚直道 (62.80,11.04)→(62.80,12.24)★ ⇒ ★再直行 steps 步到 y★ ⇒ ★然后右拐】
    #   ★**`BOOT_N` 的起步格 = (63.50, 12.25) (★格心★) ⇒ 算它到新铜的最近距离 ⇒ 必须 ≥ halo 半径 ★★
    f4 = Fake()
    steps4 = f4._yield_straight_steps("ID_DETECT_0", ("J_SOM_P1", "32", 62.80, 11.04, (0,)), 0, 1)
    turn_y = 11.04 + R.ESC_LEN + steps4 * R.GRID          # ★新拐弯高度★
    halo_r = R.CLEAR + R.W_MIN / 2.0 + R.W_CLS[1] / 2.0 + R.HALO_MARGIN
    # ★**新铜的三段: 竖 (62.80,11.04)→(62.80,12.24) · 竖 (62.80,12.24)→(62.80,turn_y) · 横 (62.80,turn_y)→(70.20,turn_y)★★
    segs = [(62.80, 11.04, 62.80, 12.24), (62.80, 12.24, 62.80, turn_y), (62.80, turn_y, 70.20, turn_y)]
    bx, by = 63.50, 12.25                                # ★BOOT_N 的起步格心★
    d = min(R._pt_seg_dist(bx, by, a, b, c, e) for (a, b, c, e) in segs)
    ck(d >= halo_r - 1e-9,
       "★修好后: `BOOT_N` 起步格 (63.50,12.25) 到 `ID_DETECT_0` 新铜的距离 %.4f ≥ halo 半径 %.4f ★"
       % (d, halo_r))
    # ★★**对照: 修好前 (★拐在 y=12.70★) 的同一距离 ⇒ 必须【小于】halo 半径 ⇒ ⇒ 证明这修法真的治那个病 ★★
    segs_old = [(62.80, 11.04, 62.80, 12.24), (62.80, 12.24, 63.45, 12.70), (63.45, 12.70, 63.70, 12.70)]
    d_old = min(R._pt_seg_dist(bx, by, a, b, c, e) for (a, b, c, e) in segs_old)
    ck(d_old < halo_r - 1e-9,
       "★修好前: 同一距离只有 %.4f < halo 半径 %.4f ⇒ ⇒ 【这就是病根】★" % (d_old, halo_r))

    print("\n═══ %s (★%d 项★) ═══" % ("ALL PASS" if not FAIL else "失败 %d 项" % len(FAIL), OKC[0] + len(FAIL)))
    for m in FAIL:
        print("   ✘ %s" % m)
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
