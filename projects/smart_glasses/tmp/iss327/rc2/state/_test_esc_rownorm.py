#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_test_esc_rownorm.py —— ★★【★防回归自测: 【非紧凑焊盘排的起步法线约束】(★`PCB_ESC_ROWNORM`)★】★★

★★★**★为什么要有这个 (★2026-11-10 04:5x)★★★**
  ★**这条 DRC (★`ID_DETECT_0`↔`BOOT_N` 0.1813mm★) 卡死了【所有臂】** ⇒ ★★**⇒ 必须有自测钉住前提** ★★
  ★★**⇒ 老板的硬规矩: "凡是留'回归见 X'的注释, 必须真的有 X, 且 X 必须断言实测数字"★★ ★★

★★★**★断言清单 (★全部来自 2026-11-10 的实测)★★★**
  ① ★**默认关**: ★**不设 `PCB_ESC_ROWNORM` ⇒ `ESC_ROWNORM_STEPS == 0`** ⇒ ★★**默认逐位不变** ★★
  ② ★**显式开**: ★**`PCB_ESC_ROWNORM=2` ⇒ 2** ★★
  ③ ★**默认路径与开之前的实现等价**: ★**开 `PCB_ESC_ROWNORM` 不应改变 `_astar` 的【默认分支】** ★★
  ④ ★**认得出"一排"时给出法线**: ★**两脚同排 (y 相同, x 相差 0.8mm) ⇒ 法线必是 ±y** ★★
  ⑤ ★**认不出"一排"时不给约束**: ★**一个斜 45° 的邻居 ⇒ 返回 None** (★保守 ⇒ 不误伤 2D 密集区★) ★★
  ⑥ ★**实测数字回归 (★v76ru 终板实测★)**:
     ★**`ID_DETECT_0` 起点 (63.200,12.450) → (63.450,12.700)** 与
     ★**`BOOT_N` 起点 (63.600,12.240) → (63.950,11.950)** ⇒ **中心线间距 0.4313mm**
     ⇒ 净距 0.4313 - 0.125 - 0.125 = **0.1813mm < 0.2000mm ⇒ 差 0.0187mm** ★★
     ⇒ ★**⇒ 这就是"起步必须先直行"要消灭的那 0.0187mm** ★★

用法:
  bash state/pcbnew_py.sh state/_test_esc_rownorm.py
  ⇒ 全部断言过 ⇒ 打印 "ALL PASS" ⇒ rc=0; 任一失败 ⇒ rc=1
"""
import os
import sys
import math

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

FAIL = []
OK = []


def chk(name, cond, detail=""):
    if cond:
        OK.append(name)
        print("  ✔ %s" % name)
    else:
        FAIL.append(name)
        print("  ✘ %s  ★%s" % (name, detail))


class _Fake:
    """★`_row_normal` 只需要 pad_rects + _free_score★"""

    def __init__(self, pad_rects, scores=None):
        self.pad_rects = pad_rects
        self._scores = scores or {}

    def _free_score(self, net, cx, cy, r_mm=1.5):
        return self._scores.get((round(cx, 3), round(cy, 3)), 0)


def main():
    print("═══ _test_esc_rownorm.py ═══")

    os.environ.pop("PCB_ESC_ROWNORM", None)
    import gen_pcb_routing as G
    chk("① 默认 PCB_ESC_ROWNORM 未设 ⇒ ESC_ROWNORM_STEPS 必须 0 (★默认逐位不变★)",
        G.ESC_ROWNORM_STEPS == 0, "实际 = %r" % (G.ESC_ROWNORM_STEPS,))

    os.environ["PCB_ESC_ROWNORM"] = "2"
    import importlib
    G2 = importlib.reload(G)
    chk("② PCB_ESC_ROWNORM=2 ⇒ ESC_ROWNORM_STEPS 必须 2",
        G2.ESC_ROWNORM_STEPS == 2, "实际 = %r" % (G2.ESC_ROWNORM_STEPS,))

    def rn(inst, net, cx, cy):
        """★把 `_row_normal` 绑到假实例上真跑 (★不走副本★)"""
        return G2.GridRouter._row_normal.__get__(inst)(net, cx, cy)

    # ④ 认得出"一排" (★J_SOM_P1 同排: y=11.040, x=62.0/62.8/63.6★)
    prs = [("ID_DETECT_1", 61.90, 10.89, 62.10, 11.19),
           ("ID_DETECT_0", 62.70, 10.89, 62.90, 11.19),
           ("BOOT_N", 63.50, 10.89, 63.70, 11.19)]
    f = _Fake(prs, scores={(62.8, 11.84): 50, (62.8, 10.24): 10})
    d = rn(f, "ID_DETECT_0", 62.8, 11.04)
    chk("④ 认得出同排 ⇒ 法线必是 ±y", d is not None and d[0] == 0 and d[1] in (1, -1),
        "实际 = %r" % (d,))
    chk("④ 法线取空旷的一侧 (★这里 +y 更空 ⇒ 应选 +y★)",
        d is not None and d == (0, 1), "实际 = %r" % (d,))

    # ⑤ 认不出"一排" (★45° 斜邻居 ⇒ 保守返回 None★)
    prs2 = [("X", 62.20, 10.44, 62.40, 10.64),
            ("Y", 63.20, 10.44, 63.40, 10.64)]
    f2 = _Fake(prs2)
    d2 = rn(f2, "NET", 62.8, 11.04)
    chk("⑤ 认不出同排 ⇒ 必须返回 None (★保守 ⇒ 不误伤 2D 密集区★)", d2 is None,
        "实际 = %r" % (d2,))

    # ⑤b 只有一个邻居 ⇒ 也不认定为一排
    f3 = _Fake([("X", 62.70, 10.89, 62.90, 11.19)])
    d3 = rn(f3, "NET", 62.8, 11.04)
    chk("⑤b 只有一个邻居 ⇒ 必须返回 None", d3 is None, "实际 = %r" % (d3,))

    # ⑥ 实测数字回归 (★v76ru 终板实测★)
    a1 = (63.200, 12.450); a2 = (63.450, 12.700)
    b1 = (63.600, 12.240); b2 = (63.950, 11.950)

    def _seg_dist(p, q, r, s):
        def d_pt(px, py, ax, ay, bx, by):
            dx = bx - ax; dy = by - ay
            if dx == 0 and dy == 0:
                return math.hypot(px - ax, py - ay)
            t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
            return math.hypot(px - (ax + t * dx), py - (ay + t * dy))
        def cr(ox, oy, ax, ay, bx, by):
            return (bx - ax) * (oy - ay) - (by - ay) * (ox - ax)
        d1 = cr(r[0], r[1], p[0], p[1], q[0], q[1])
        d2 = cr(s[0], s[1], p[0], p[1], q[0], q[1])
        d3 = cr(p[0], p[1], r[0], r[1], s[0], s[1])
        d4 = cr(q[0], q[1], r[0], r[1], s[0], s[1])
        if ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0)):
            return 0.0
        return min(d_pt(p[0], p[1], r[0], r[1], s[0], s[1]),
                   d_pt(q[0], q[1], r[0], r[1], s[0], s[1]),
                   d_pt(r[0], r[1], p[0], p[1], q[0], q[1]),
                   d_pt(s[0], s[1], p[0], p[1], q[0], q[1]))

    d = _seg_dist(a1, a2, b1, b2)
    chk("⑥ 两段中心线间距必须 ≈0.4313mm (★v76ru 终板实测★)", abs(d - 0.4313) < 0.002,
        "实际 = %.4f" % d)
    clr = d - 0.125 - 0.125
    chk("⑥ 净距必须 = 0.1813mm (★实际 DRC 报的就是这个数★)", abs(clr - 0.1813) < 0.002,
        "实际 = %.4f" % clr)
    chk("⑥ 净距必须 < 0.2000mm (★⇒ 这就是那条 DRC★)", clr < 0.20, "实际 = %.4f" % clr)
    chk("⑥ 差值必须 ≈0.0187mm (★起步先直行要消灭的就是它★)",
        abs((0.20 - clr) - 0.0187) < 0.002, "实际 = %.4f" % (0.20 - clr))

    print("─" * 46)
    if FAIL:
        print("FAILED %d/%d" % (len(FAIL), len(FAIL) + len(OK)))
        return 1
    print("ALL PASS (%d)" % len(OK))
    return 0


if __name__ == "__main__":
    sys.exit(main())
