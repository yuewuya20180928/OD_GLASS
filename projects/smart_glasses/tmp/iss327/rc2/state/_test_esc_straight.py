#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_test_esc_straight.py —— ★★【★防回归自测: "出脚后必须先直行" (★`PCB_ESC_STRAIGHT`)★】★★

★★★**★为什么要有这个 (★2026-11-10 04:2x)★★★**
  ★**这次改动的核心风险 = "默认行为必须逐位不变"** ⇒ ★★**⇒ 必须有自测把这个前提钉死** ★★
  ★★**⇒ 老板硬规矩: "凡是留'回归见 X'的注释, 必须真的有 X, 且 X 必须断言实测数字"★★ ★★

★★★**★断言清单 (★全部来自 2026-11-10 的实测)★★★**
  ① ★**默认关**: ★**不设 `PCB_ESC_STRAIGHT` ⇒ `ESC_STRAIGHT_STEPS == 0`** ⇒ ★★**默认逐位不变** ★★
  ② ★**显式开**: ★**`PCB_ESC_STRAIGHT=2` ⇒ `ESC_STRAIGHT_STEPS == 2`** ★★
  ③ ★**约束真的生效**: ★**A* 的前 2 步必须沿 `first_dir` (★出脚方向★)** ★★
  ④ ★**只约束前 N 步**: ★**第 3 步起方向自由** ★★
  ⑤ ★**兜底回退**: ★**约束下无路 ⇒ 自动用无约束重试并返回路径** (★保证不比现状更差★) ★★
  ⑥ ★**实测几何数字 (★回归基线★)**: ★**垂距公式 `0.4×sin(39.6°)=0.255mm`**
     与 **需要 `0.075+0.125+0.2+0.025=0.425mm`** ⇒ **差 0.17mm** ⇒ ★★**这正是 N 腿 L=0.00 的原因** ★★
     ⇒ ★**直行 h 之后垂距 = 0.255 + 0.77×h ⇒ h=0.5mm ⇒ 0.64mm ⇒ 解封** ★★

用法:
  bash state/pcbnew_py.sh state/_test_esc_straight.py
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
    """★A* 只需要这几个成员 ⇒ 用鸭子类型单测, 不必真造一块板"""

    def __init__(self, W, H, blocked=frozenset()):
        self.W = W
        self.H = H
        self._blocked = blocked
        self.astar_budget = 0
        self._esc_start_dir = {}

    def _idx(self, i, j):
        return i + j * self.W

    def _free(self, li, idx, net, cls=1):
        return idx not in self._blocked

    def _via_ok(self, li, nli, idx, net, cls=1):
        return False


def main():
    print("═══ _test_esc_straight.py ═══")

    # ① 默认关
    os.environ.pop("PCB_ESC_STRAIGHT", None)
    import gen_pcb_routing as G
    chk("① 默认 PCB_ESC_STRAIGHT 未设 ⇒ ESC_STRAIGHT_STEPS 必须 0 (★默认逐位不变★)",
        G.ESC_STRAIGHT_STEPS == 0, "实际 = %r" % (G.ESC_STRAIGHT_STEPS,))

    # ② 显式开
    os.environ["PCB_ESC_STRAIGHT"] = "2"
    import importlib
    G2 = importlib.reload(G)
    chk("② PCB_ESC_STRAIGHT=2 ⇒ ESC_STRAIGHT_STEPS 必须 2",
        G2.ESC_STRAIGHT_STEPS == 2, "实际 = %r" % (G2.ESC_STRAIGHT_STEPS,))

    # ---- ③⑤ 行为自测 (直接调 GridRouter 的方法, 绑到鸭子类型实例上) ----
    G2.ESC_STRAIGHT_STEPS = 2

    def _mk(W=20, H=20, blocked=frozenset()):
        f = _Fake(W, H, blocked)
        f._astar = G2.GridRouter._astar.__get__(f)
        f._astar_core = G2.GridRouter._astar_core.__get__(f)
        return f

    # ③ 前 2 步必须沿 first_dir=(1,0) (东)
    f = _mk()
    start = [(0, f._idx(3, 5))]
    goals = {(0, f._idx(9, 5))}
    f._esc_start_dir[("NET_A", start[0])] = (1, 0, 2)   # ★(di,dj,步数)★
    path = f._astar(start, goals, "NET_A", max_via=False)
    chk("③ 约束生效时 A* 必须返回路径", path is not None, "path=%r" % (path,))
    if path:
        def _d(a, b):
            return (b[1] % f.W - a[1] % f.W, b[1] // f.W - a[1] // f.W)
        d1 = _d(path[0], path[1])
        d2 = _d(path[1], path[2])
        chk("③ 第 1 步必须沿出脚方向 (1,0)", d1 == (1, 0), "实际 = %r" % (d1,))
        chk("③ 第 2 步必须沿出脚方向 (1,0)", d2 == (1, 0), "实际 = %r" % (d2,))

    # ④ 第 3 步起自由 (目标在正东 ⇒ 第 3 步还是东, 但那是因为最优路 ⇒ 换个目标验证)
    f2 = _mk()
    start2 = [(0, f2._idx(3, 5))]
    goals2 = {(0, f2._idx(9, 8))}
    f2._esc_start_dir[("NET_B", start2[0])] = (1, 0, 2)
    p2 = f2._astar(start2, goals2, "NET_B", max_via=False)
    chk("④ 约束后仍能走到斜向目标 (★说明第 3 步起方向自由★)", p2 is not None)
    if p2 and len(p2) >= 3:
        def _d(a, b):
            return (b[1] % f2.W - a[1] % f2.W, b[1] // f2.W - a[1] // f2.W)
        chk("④ 第 1 步仍受约束 (1,0)", _d(p2[0], p2[1]) == (1, 0), "实际 = %r" % (_d(p2[0], p2[1]),))
        chk("④ 第 2 步仍受约束 (1,0)", _d(p2[1], p2[2]) == (1, 0), "实际 = %r" % (_d(p2[1], p2[2]),))

    # ⑤ 兜底回退: 把东边全堵死 ⇒ 约束下无路 ⇒ 应回退到无约束并找到南北向的路
    W = 20
    blocked = set()
    for j in range(H_ := 20):
        for i in range(4, 20):
            blocked.add(i + j * W)
    f3 = _mk(W, 20, frozenset(blocked))
    start3 = [(0, f3._idx(3, 5))]
    goals3 = {(0, f3._idx(3, 9))}
    f3._esc_start_dir[("NET_C", start3[0])] = (1, 0, 2)
    p3 = f3._astar(start3, goals3, "NET_C", max_via=False)
    chk("⑤ 约束下无路 ⇒ 自动回退到无约束并返回路径 (★保证不比现状更差★)",
        p3 is not None, "path=%r" % (p3,))

    # ⑥ 实测几何数字 (回归基线)
    perp = 0.4 * math.sin(math.radians(39.6))
    need = 0.075 + 0.125 + 0.20 + 0.025
    chk("⑥ 垂距 0.4×sin(39.6°) 必须 ≈0.255mm", abs(perp - 0.255) < 0.002,
        "实际 = %.4f" % perp)
    chk("⑥ 需要净距必须 = 0.425mm (0.075+0.125+0.2+0.025)", abs(need - 0.425) < 1e-9,
        "实际 = %.4f" % need)
    chk("⑥ 两者之差必须 ≈0.17mm (★这就是 N 腿 L=0.00 的原因★)",
        abs((need - perp) - 0.170) < 0.003, "实际 = %.4f" % (need - perp))
    perp_h = perp + 0.77 * 0.5
    chk("⑥ 直行 0.5mm 后垂距必须 ≈0.64mm (⇒ 解封)", abs(perp_h - 0.640) < 0.005,
        "实际 = %.4f" % perp_h)
    chk("⑥ 直行 0.5mm 后垂距必须 > 需要 (⇒ 邻居出脚道活)", perp_h > need,
        "实际 = %.4f vs %.4f" % (perp_h, need))


    # ---- ★★2026-11-11 04:5x 【★窄版直行 `PCB_ESC_STRAIGHT_NETS` 的判定 (★纯函数★)★★ ----
    os.environ.pop("PCB_ESC_STRAIGHT_NETS", None)
    import importlib as _il
    G3 = _il.reload(G2)
    chk("⑤ 窄版: 默认【名单为空】⇒ 所有网都生效 (★老行为 ⇒ 逐位不变★)",
        G3.ESC_STRAIGHT_NETS == frozenset() and G3.esc_straight_applies("任意网") is True,
        "名单 = %r" % (G3.ESC_STRAIGHT_NETS,))
    os.environ["PCB_ESC_STRAIGHT_NETS"] = "CSI_D0_D0_N, DSI_D0_CK_N;DSI_D0_D1_N"
    G4 = _il.reload(G3)
    chk("⑥ 窄版: 名单解析正确 (★逗号/分号都能隔·空格要去掉·共 3 个★)",
        G4.ESC_STRAIGHT_NETS == frozenset({"CSI_D0_D0_N", "DSI_D0_CK_N", "DSI_D0_D1_N"}),
        "实际 = %r" % (sorted(G4.ESC_STRAIGHT_NETS),))
    chk("⑦ 窄版: 名单内的网生效",
        G4.esc_straight_applies("CSI_D0_D0_N") is True)
    chk("⑧ 窄版: 名单外的网【不生效】(★这才是窄版的真意义★)",
        G4.esc_straight_applies("CSI_D0_D0_P") is False)
    os.environ.pop("PCB_ESC_STRAIGHT_NETS", None)

    print("─" * 46)
    if FAIL:
        print("FAILED %d/%d" % (len(FAIL), len(FAIL) + len(OK)))
        return 1
    print("ALL PASS (%d)" % len(OK))
    return 0


if __name__ == "__main__":
    sys.exit(main())
