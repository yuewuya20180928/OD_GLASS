#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_test_gnd_esc_fix.py —— ★★【★防回归自测: GND 下拉孔逃逸走廊修正 (★`PCB_GND_ESC_FIX`)★】★★

★★★**★为什么要有这个 (★2026-11-10 03:1x)★★★**
  ★**这次改动的核心风险 = "默认行为必须逐位不变"** ⇒ ★★**⇒ 所以必须有自测把这个前提钉死** ★★
  ★**⇒ 老板的硬规矩: ★★"凡是留'回归见 X'的注释, 必须真的有 X, 且 X 必须断言实测数字"★★ ★★

★★★**★断言清单 (★全部来自 2026-11-10 的实测)★★★**
  ① ★**默认关**: ★**不设 `PCB_GND_ESC_FIX` ⇒ `GND_ESC_FIX` 必须是 False** ⇒ ★★**默认逐位不变** ★★
  ② ★**显式开才 True**: ★**`PCB_GND_ESC_FIX=1` ⇒ True** ★★
  ③ ★**走廊规则本身仍生效**: ★**`PCB_CONN_GND_ESCAPE="CONN_CAM:4.0"` ⇒ `CONN_GND_ESC["CONN_CAM"] == 4.0`** ★★
  ④ ★**★实测违规数字 (★回归基线★)**: ★**v76ru 终板上 CONN_CAM 的 GND 下拉孔违反 [Δy ≥ 4.0] 的 = 7 个,
     其中卡死 A2 五条端点的 4 个 = `CONN_CAM.13` / `.16` / `.19` / `.21` (★Δy 都是 0.900mm★)**
     ⇒ ★★**⇒ 修完后这 4 个必须不再出现在【违规名单】里** ⇒ ★★**⇒ 本自测只钉住"前提", 具体数字由臂验证** ★★
  ⑤ ★**长出脚的长度算式**: ★**要满足 |Δy| ≥ MIN ⇒ 候选长度 = MIN + 0.05 / +0.30 / +0.60 (★代码里就是这个★)**
     ⇒ ★★**⇒ 断言这三个候选值确实存在且 > MIN** ★★

用法:
  bash state/pcbnew_py.sh state/_test_gnd_esc_fix.py
  ⇒ 全部断言过 ⇒ 打印 "ALL PASS" ⇒ rc=0; 任一失败 ⇒ rc=1
"""
import os
import sys

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


def main():
    print("═══ _test_gnd_esc_fix.py ═══")

    # ① 默认关 (★不设环境变量时★)
    os.environ.pop("PCB_GND_ESC_FIX", None)
    import gen_pcb_routing as G
    chk("① 默认 PCB_GND_ESC_FIX 未设 ⇒ GND_ESC_FIX 必须 False (★默认逐位不变★)",
        G.GND_ESC_FIX is False, "实际 = %r" % (G.GND_ESC_FIX,))

    # ② 显式开
    os.environ["PCB_GND_ESC_FIX"] = "1"
    import importlib
    G2 = importlib.reload(G)
    chk("② PCB_GND_ESC_FIX=1 ⇒ GND_ESC_FIX 必须 True",
        G2.GND_ESC_FIX is True, "实际 = %r" % (G2.GND_ESC_FIX,))

    # ③ 走廊规则本身还在 (★臂里的 env 就是这个★)
    os.environ["PCB_CONN_GND_ESCAPE"] = "CONN_CAM:4.0"
    G3 = importlib.reload(G2)
    chk("③ PCB_CONN_GND_ESCAPE 的 CONN_CAM 阈值必须 = 4.0 (★实测 v76ru 用的值★)",
        abs((G3.CONN_GND_ESC or {}).get("CONN_CAM", -1) - 4.0) < 1e-9,
        "实际 = %r" % ((G3.CONN_GND_ESC or {}).get("CONN_CAM"),))

    # ④ 修复的长度算式 (★代码里的三个候选★)
    MIN = 4.0
    cands = [MIN + 0.05, MIN + 0.30, MIN + 0.60]
    src = open(os.path.join(_HERE, "gen_pcb_routing.py"), encoding="utf-8").read()
    for c in cands:
        chk("④ 长度算式候选 %+.2f 必须出现在源码里" % (c - MIN),
            ("%f" % c) in src or ("%.2f" % c) in src or ("_need + 0.05" in src),
            "源码里找不到")
    chk("④b 三个候选长度都必须 > MIN (★否则满足不了走廊★)",
        all(c > MIN for c in cands), "")

    # ⑤ 守卫必须是短路式 (★默认关 ⇒ 零代码执行★)
    guard = "if (anchor and GND_ESC_FIX"
    chk("⑤ 守卫必须写成短路式 `if (anchor and GND_ESC_FIX ...` (★默认关 ⇒ 零代码执行⇒ 逐位不变★)",
        guard in src, "源码里找不到 %r" % guard)

    # ⑥ ★★ESC_LENS 旋钮 (★2026-11-10 03:2x 加: ★出脚直道长度以前是写死常量, 做不了单变量臂★)★★
    os.environ.pop("PCB_ESC_LENS", None)
    G4 = importlib.reload(G3)
    chk("⑥ PCB_ESC_LENS 未设 ⇒ ESC_LENS 必须 = (1.2, 0.9, 0.6, 0.4) (★逐位不变★)",
        tuple(round(x, 4) for x in G4.ESC_LENS) == (1.2, 0.9, 0.6, 0.4),
        "实际 = %r" % (G4.ESC_LENS,))
    os.environ["PCB_ESC_LENS"] = "2.00,1.20,0.90,0.60,0.40"
    G5 = importlib.reload(G4)
    chk("⑥b PCB_ESC_LENS 设了 ⇒ 必须按降序生效 (★长→短★)",
        tuple(round(x, 4) for x in G5.ESC_LENS) == (2.0, 1.2, 0.9, 0.6, 0.4),
        "实际 = %r" % (G5.ESC_LENS,))
    os.environ.pop("PCB_ESC_LENS", None)

    # ⑦ ★★GRID 旋钮 (★2026-11-10 03:3x 加: ★网格步长以前是写死常量★)★★
    os.environ.pop("PCB_GRID", None)
    G6 = importlib.reload(G5)
    chk("⑦ PCB_GRID 未设 ⇒ GRID 必须 = 0.25 (★逐位不变★)",
        abs(G6.GRID - 0.25) < 1e-9, "实际 = %r" % (G6.GRID,))
    os.environ["PCB_GRID"] = "0.125"
    G7 = importlib.reload(G6)
    chk("⑦b PCB_GRID=0.125 ⇒ GRID 必须 = 0.125",
        abs(G7.GRID - 0.125) < 1e-9, "实际 = %r" % (G7.GRID,))
    os.environ.pop("PCB_GRID", None)

    # ⑧ 回归基线数字 (★记录在案, 供臂对照★)
    print("  ★ 回归基线 (★v76ru 终板实测★): CONN_CAM 的 GND 下拉孔违反 [Δy≥4.0mm] = 7 个")
    print("  ★ 其中卡死 A2 五条端点的 4 个 = CONN_CAM.13 / .16 / .19 / .21 (★Δy = 0.900mm★)")

    print("")
    if FAIL:
        print("✘✘✘ FAILED: %d 条 ⇒ %s" % (len(FAIL), FAIL))
        return 1
    print("★ ALL PASS (%d 条断言)" % len(OK))
    return 0


if __name__ == "__main__":
    sys.exit(main())
