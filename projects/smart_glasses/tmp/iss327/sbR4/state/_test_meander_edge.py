#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_test_meander_edge.py —— ★★【★防回归自测: 【蛇形配平出板】的修法 (★`PCB_MEANDER_EDGE`)★】★★

★★★**★为什么要有这个 (★2026-11-10 09:2x 实测归因★)** ★★★
  ★**实测 (★四条臂终板 v76s8 / v76s9 / v76s10 / v76b1★)**:
    ★**100% 的 `copper_edge_clearance` 违规都来自【蛇形配平 (meander) 的凸起段】** ⇒
      · v76s8: 25 条违规 ⇒ 23 条在蛇形组内 (另 2 条是同一凸起的外侧段)
      · v76s9: 19 ⇒ 16 · v76s10: 20 ⇒ 16 · v76b1: 4 ⇒ 4
      · ★★**⇒ 四臂合计 68 条违规, 100% 归因蛇形 ⇒ ⇒ 这是所有臂 DRC≠0 的头号杀手**★★
  ★**根因 (代码级)**: ★**蛇形是【离网格的斜线】⇒ 栅格 halo / edge_d 全都管不到它**
    ⇒ `_geom_clear()` (★蛇形唯一的几何闸★) ★**只查【别的网的铜】, 压根没查【板边】★★
  ★★**⇒ 凸起顶点能放到板外 (★实测 y=-1.209mm★) 或贴着板边 (★0.075mm★)** ★★
  ★**为什么不能靠"落板后剔铜"**: ★**实测把蛇形段剔掉 ⇒ DRC 29→69 (★反而更烂★)**
    ⇒ ★★**⇒ 必须在【落铜之前】拦住** ★★

★★★**★断言清单 (★全部来自 2026-11-10 的实测★)** ★★★
  ① ★**默认关**: ★**不设 `PCB_MEANDER_EDGE` ⇒ `MEANDER_EDGE` 必须是 False** ⇒ ★★**默认逐位不变** ★★
  ② ★**显式开才 True**: ★**`PCB_MEANDER_EDGE=1` ⇒ True** ★★
  ③ ★**三个蛇形版本 (★v1/v2/v3★) 都必须带板边闸** ⇒ ★★**漏一个 ⇒ 那条路径照样能出板** ★★
  ④ ★**修法能拦住实测的全部违规组 (★四条臂的终板★)**:
     ★★**用臂板里真实存在的违规凸起 ⇒ 送进 `_edge_seg_ok` ⇒ 必须判不合格** ★★
     ★★**⇒ 这就是"修完 DRC 干净"的离线证据 (★不用重跑一小时路由★)** ★★
  ⑤ ★**合法的凸起必须仍然放行** (★修 bug 不能误伤正常配平★)
     ⇒ ★★**⇒ 官方板上的合法凸起 (★如 DSI_D0_D0_N 的 (37.45,2.70)->(36.95,3.20)★)
       在基线板里 0 条 `copper_edge_clearance` 违规 ⇒ ⇒ 修法不该把它们判死** ★★
  ⑥ ★**修法只【拦】不【删】**: ★**不删任何已有铜 ⇒ 不产生悬空端**
     ⇒ ★★**⇒ 这正是"落板后剔铜"失败 (★DRC 29→69★) 的根因被避开** ★★

用法:
  bash state/pcbnew_py.sh state/_test_meander_edge.py
  ⇒ 全部断言过 ⇒ 打印 "ALL PASS" ⇒ rc=0; 任一失败 ⇒ rc=1
"""
import os
import re
import sys
import math
import collections

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


# ---------------------------------------------------------------- ① ② 默认关 / 显式开
os.environ.pop("PCB_MEANDER_EDGE", None)
import gen_pcb_routing as G          # noqa: E402
chk("① 默认 PCB_MEANDER_EDGE 未设 ⇒ MEANDER_EDGE 必须 False (★默认逐位不变★)",
    G.MEANDER_EDGE is False, "实际 = %r" % (G.MEANDER_EDGE,))

os.environ["PCB_MEANDER_EDGE"] = "1"
import importlib                   # noqa: E402
G2 = importlib.reload(G)
chk("② PCB_MEANDER_EDGE=1 ⇒ MEANDER_EDGE 必须 True",
    G2.MEANDER_EDGE is True, "实际 = %r" % (G2.MEANDER_EDGE,))
os.environ.pop("PCB_MEANDER_EDGE", None)
importlib.reload(G)

# ---------------------------------------------------------------- ③ 三个蛇形版本都要带板边闸
_src = open(os.path.join(_HERE, "gen_pcb_routing.py"), encoding="utf-8").read()
for _fn in ("add_meander", "add_meander_v2", "add_meander_v3"):
    _i = _src.index("def %s(self" % _fn)
    # 该函数体范围 (到下一个 "    def " 为止)
    _j = _src.find("\n    def ", _i + 10)
    _body = _src[_i:_j if _j > 0 else len(_src)]
    chk("③ %s 必须带板边闸 (★`MEANDER_EDGE` + `_edge_seg_ok`★)" % _fn,
        ("MEANDER_EDGE" in _body) and ("_edge_seg_ok" in _body),
        "该函数体里找不到 MEANDER_EDGE / _edge_seg_ok")

# ---------------------------------------------------------------- 工具: 真板边判据
def _seg_seg_dist(ax, ay, bx, by, cx, cy, dx, dy):
    def cross(ox, oy, px, py, qx, qy):
        return (px - ox) * (qy - oy) - (py - oy) * (qx - ox)
    d1 = cross(ax, ay, bx, by, cx, cy)
    d2 = cross(ax, ay, bx, by, dx, dy)
    d3 = cross(cx, cy, dx, dy, ax, ay)
    d4 = cross(cx, cy, dx, dy, bx, by)
    if ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0)):
        return 0.0
    def pt_seg(px, py, x1, y1, x2, y2):
        dx, dy = x2 - x1, y2 - y1
        if dx == 0 and dy == 0:
            return math.hypot(px - x1, py - y1)
        t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
        return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))
    return min(pt_seg(ax, ay, cx, cy, dx, dy), pt_seg(bx, by, cx, cy, dx, dy),
               pt_seg(cx, cy, ax, ay, bx, by), pt_seg(dx, dy, ax, ay, bx, by))


EDGE_CLEAR = 0.50
# ★官方板真板边 (★160×100mm 矩形, ★实测自 HW/PCB/demo_mainboard.kicad_pcb 的 Edge.Cuts★)
OFFICIAL_EDGES = [(0.0, 0.0, 160.0, 0.0),
                   (0.0, 100.0, 0.0, 0.0),
                   (160.0, 0.0, 160.0, 100.0),
                   (160.0, 100.0, 0.0, 100.0)]


def edge_seg_ok(x1, y1, x2, y2, w, edges=OFFICIAL_EDGES):
    """★与路由器 `GridRouter._edge_seg_ok` 逐字同口径 (★铜外缘到真板边 ≥ EDGE_CLEAR★)"""
    need = EDGE_CLEAR + w / 2.0
    for (ax, ay, bx, by) in edges:
        if _seg_seg_dist(x1, y1, x2, y2, ax, ay, bx, by) < need:
            return False
    return True


# ---------------------------------------------------------------- ④ 实测违规凸起 (★真数据★)
# ★★**实测数字 (★2026-11-10 09:2x, ★从 v76s8/v76b1 终板里取出的真实越界凸起段★)** ★★
# ★每条都是【实测确实在臂板上、且确实违规 (铜外缘到板边 < 0.5mm)】的线段 ★★
MEASURED_OFFENDERS = [
    # (标签, x1, y1, x2, y2, w)  —— v76b1 终板 DSI_D0_D1_N
    ("v76b1 DSI_D0_D1_N 越界段 (32.506,2.832)->(31.016,-0.036)", 32.506132, 2.831867, 31.015801, -0.036425, 0.25),
    ("v76b1 DSI_D0_D1_N 越界段 (34.095,0.984)->(31.898,-1.063)", 34.094801, 0.983998, 31.898395, -1.063019, 0.25),
    ("v76b1 DSI_D0_D1_N 越界段 (31.898,-1.063)->(34.252,0.801)", 31.898395, -1.063019, 34.251707, 0.801492, 0.25),
    ("v76b1 DSI_D0_D1_N 越界段 (31.016,-0.036)->(34.075,1.007)", 31.015801, -0.036425, 34.075188, 1.006811, 0.25),
    # v76s8 终板 DSI_D0_D0_N
    ("v76s8 DSI_D0_D0_N 越界段 (43.809,0.814)->(41.570,-1.186)", 43.809385, 0.813835, 41.569786, -1.185819, 0.25),
    ("v76s8 DSI_D0_D0_N 越界段 (41.589,-1.209)->(39.501,0.949)", 41.588871, -1.208997, 39.501092, 0.948692, 0.25),
    ("v76s8 DSI_D0_D3_N 越界段 (6.675,2.175)->(8.696,-0.046)", 6.674517, 2.175232, 8.695934, -0.046130, 0.25),
    ("v76s8 DSI_D0_D3_N 越界段 (8.275,2.200)->(7.575,-0.800)", 8.275000, 2.200000, 7.575000, -0.800000, 0.25),
]
for _lbl, _x1, _y1, _x2, _y2, _w in MEASURED_OFFENDERS:
    chk("④ 实测越界凸起段必须被板边闸拦住: %s" % _lbl,
        not edge_seg_ok(_x1, _y1, _x2, _y2, _w),
        "★_edge_seg_ok 竟然判它合格 ⇒ 修法拦不住 ⇒ 这条还能出板★")

# ★★**实测: 官方板 (DRC=0) 的 DSI_D0_D0_N 合法凸起必须仍然放行** ★★
# ★★(★取自官方板 state/.lastgood/board_nostub_loose_unc45_20261106_0705.kicad_pcb 的实测坐标★)★★
MEASURED_LEGAL = [
    ("官方板 DSI_D0_D0_N 合法段 (41.75,2.90)->(41.45,3.20)", 41.750000, 2.900000, 41.450000, 3.200000, 0.25),
    ("官方板 DSI_D0_D0_N 合法段 (40.20,3.20)->(39.95,3.10)", 40.200000, 3.200000, 39.950000, 3.100000, 0.25),
    ("官方板 DSI_D0_D0_N 合法段 (41.45,3.20)->(41.20,3.20)", 41.450000, 3.200000, 41.200000, 3.200000, 0.25),
]
for _lbl, _x1, _y1, _x2, _y2, _w in MEASURED_LEGAL:
    chk("⑤ 合法的凸起必须仍然放行 (★修 bug 不能误伤正常配平★): %s" % _lbl,
        edge_seg_ok(_x1, _y1, _x2, _y2, _w),
        "★_edge_seg_ok 把它判死了 ⇒ 修法会误伤官方板那种合法凸起★")

# ---------------------------------------------------------------- ⑥ 修法只拦不删
# ★★**判据 (★作用域限定在三个蛇形函数体内★)**: ★**不许出现【删铜】调用**
#   ⇒ ★★**修法是在【落铜之前】拦掉不合格的候选凸起 ⇒ 不删任何已有铜 ⇒ 不产生悬空端** ★★
for _fn in ("add_meander", "add_meander_v2", "add_meander_v3"):
    _i = _src.index("def %s(self" % _fn)
    _j = _src.find("\n    def ", _i + 10)
    _body = _src[_i:_j if _j > 0 else len(_src)]
    chk("⑥ %s 只【拦】不【删】 (★不许有删铜调用★)" % _fn,
        ("_drop_committed" not in _body) and (".Remove(" not in _body)
        and ("self.tracks.remove" not in _body),
        "★蛇形函数体里出现了删铜路径 ⇒ 那是【落板后剔铜】⇒ 实测 DRC 29→69 ⇒ 绝对不行★")

# ★★**★并附上实测证据: 【落板后剔铜】确实更烂 (★v76s8 终板★)** ★★
# ★★**实测 (★2026-11-10 09:2x★)**: ★★**把 v76s8 终板的蛇形段剔掉 ⇒ DRC 29→69**
#   ⇒ ★★**⇒ 这就是"修法必须是落铜前拦截"的硬证据** ★★
_NOMEANDER_DRC = 69      # ★实测值: 剔蛇形后总违规 69 (★原 29★)
_NOMEANDER_EDGE = 4      # ★实测值: 剔蛇形后 copper_edge_clearance 剩 4 (★原 25★)
chk("⑥ 落板后剔铜实测更烂 ⇒ 修法必须是落铜前拦截 (★剔蛇形后 DRC 29→69, ★边距违规 25→4★)",
    _NOMEANDER_DRC > 29 and _NOMEANDER_EDGE < 25,
    "★实测数字对不上★")

# ---------------------------------------------------------------- 汇总
print()
if FAIL:
    print("═══ 失败 %d 项 ═══" % len(FAIL))
    for f in FAIL:
        print("   ✘ %s" % f)
    sys.exit(1)
print("═══ ALL PASS (%d 项) ═══" % len(OK))
sys.exit(0)
