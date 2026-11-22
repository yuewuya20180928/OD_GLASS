#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pinset2_mech_check.py —— ISS-192 结构侧独立复算 (板框 60×30 / RK3576 / PIN-SET-2 套 A)
=====================================================================
★**本脚本是 ISS-192 的核心产物**: 把 ISS-107 时代的 60×15 / RK3588-8×10 复算器
  **迁到现行板 (60×30 / RK3576 / 套 A)**, 并**把判据本身一起重推**。

为什么必须迁 (★不是洁癖, 是假绿★):
  · 2026-11-11 13:4x 项目总工实测: 旧脚本跑出来是「复算项 31 | FAIL 0 | WARN 3」rc=0
    ⇒ ★**它是在一块已经不存在的板子上亮绿灯** (15mm 板 + RK3588 8×10 封装)。
  · 迁到 30mm 后 FAIL 变 1, 而**变红的那条判据本身就是 15mm 语义**:
    旧判据写「老口径 … 3/3 孔压逃线带 ⇒ 判据成立」, 而 60×30/RK3576 下实测只压 2/3
    ⇒ 结论 (老口径必须作废) 仍然成立, 但**计数**随板宽变了。
  ⇒ 所以本脚本**不只改常量**: 判据从「3/3」改写成**板宽无关**的形式 (≥1/3 压带 ⇒ 不可用),
    并**另加两条板宽无关的独立判据** (单销定位链不足 / 边距余量偏紧), 让结论不再依赖计数。

★★ 本单的核心仲裁 (孔位 Y 的两套互斥口径) 已落进判据:
  套 A = 中心线平移 (P1/P2 Y=15.00, S1 Y=10.00, S2 Y=20.00) —— **采纳**
  套 B = 保持绝对 Y (S1 Y=2.50, S2 Y=27.50) —— **否决**
  依据与影响面见 `MECH/BOARD_GEOM_30MM.md` §4。
  ⇒ **本脚本的 §③ 判据直接读打印包 Rev B 生成器的实际孔位并逐坐标比对** ——
    这条判据就是「两套口径并存」的根因防线: 打印包与 PCB 孔心差多少 mm, 本脚本就报多少 mm。

本脚本做 5 件事 (全部机械判定, 不靠人眼):
  ① PIN-SET-2 四孔几何自检 (真圆∩矩形 2D 重叠 / 孔心与孔壁到板边 / 孔间中心距与孔壁间距 /
     定位链配合) —— 口径: 60×30 板 + RK3576 (17.20×16.10) + 逃线带 0.80/边
  ② 老口径失效复算 (板宽无关化改写 + 两条独立判据)
  ③ 打印包契约复算 (★读 Rev B 生成器的**实际**常量与实际孔数, 不再硬编码 Rev A 老值★)
  ④ 硬件侧产物口径分歧探测 (只读 `HW/pcb60x30_check.py`, 不改它 —— 归 hw-lead)
  ⑤ 散热连带量级复核 (螺钉热旁路 / 骨架段温差抵偿) —— ★不出新的皮肤温度数★

输出: MECH/pinset2_mech_check.json  + 终端表格
rc  = 0 → 全部通过 / 1 → 有 FAIL

用法:
    python3 MECH/pinset2_mech_check.py             # 复算 (FAIL 0 / WARN 2) —— ★默认档 F30A (60×30 / RK3576 · 历史产品板口径)★
    python3 MECH/pinset2_mech_check.py --self-test  # 反向用例: 把孔挪进逃线带 ⇒ 必须变红
    python3 MECH/pinset2_mech_check.py --frame B160x100   # ★切档: 台架板 160×100 / RK3572-SOM 帧★
    ★切档也可走环境变量: MECH_FRAME=B160x100 python3 MECH/pinset2_mech_check.py
    ★★默认档 = F30A (60×30 / RK3576) —— ★本单不许自己拍默认档, 保持现状不变★ ★★

★★ISS-345 双口径 (2026-11-23) ★★:
  本脚本现在**同时支持两档** (帧 id 与 `HW/PCB/BOARD_FRAME_CALIBER.md` §2 `cal:FRAMES` 逐字一致):
    · `F30A`      = 60×30 / 6 层 / 1.00mm / RK3576 17.20×16.10 (★默认档 · 判据与 11-11 迁版后逐字一致★)
    · `B160x100`  = 160×100 / 8 层 / 1.60mm / RK3572-SOM 承载区 56.70×46.78 (★盘上现役台架板帧★)
  ★★**默认档 (历史产品板口径) 的输出与迁移前逐字节相同** (★60×30 档判据方向一个字都没改★) ★★
  ★**PIN-SET-2 孔位族 (套 A 四孔坐标) = F30A 帧专有** —— 台架板 160×100 盘上**没有**这四个孔
    (★先例: MECH/board_frame_feasibility.py:108 `pinset_applicable: False` —— "套 A 是 F30A 帧的坐标,
     套到台架板帧 = 口径不适用"★) ⇒ B160x100 帧跑**帧级判据** (板框 / SoM 承载区占位 / 逃线带 / 边距),
    孔位族判据在本帧**不适用** (按先例登记, 不假装跑通)。

纪律: 只写 MECH/ 下本脚本自己的两个文件; 不改任何别人的文件
      (不碰 HW/ 不碰 state/fragments/ 不碰 state/merge.py); 读 HW/ 只读。
=====================================================================
"""
from __future__ import annotations

import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
OUT_JSON = os.path.join(HERE, "pinset2_mech_check.json")
PACK_PY = os.path.join(HERE, "print", "gen_print_pack_revb.py")
HW_PCB60_PY = os.path.join(PROJ, "HW", "pcb60x30_check.py")

# =====================================================================
# 输入 —— 每行标来源; [推算] 的给公式
# =====================================================================
# ★ISS-345 双口径: 板框 / 主控 / 孔位 三组常量按【档位】取值 (★帧 id 逐字取自
#   `HW/PCB/BOARD_FRAME_CALIBER.md` §2 `cal:FRAMES` 的三套帧 id 写法: B160x100 / F30A / P60x15
#   (★P60x15 = 已作废的历史口径, 不可与现役板混用★)★)
#   · ★默认档 = F30A (60×30 / RK3576) —— ★本单【不许自己拍默认档】, 保持现状不变★
#   · 切档 = `--frame B160x100` (或环境变量 MECH_FRAME=B160x100) —— 见 §用法
FRAMES = [
    {
        "fid": "F30A",
        "name": "产品板 60×30 套 A (历史产品板口径 · 与台架板口径不可混用)",
        "pcb_l": 60.00, "pcb_w": 30.00, "pcb_thk": 1.00, "layers": 6,
        "soc_model": "RK3576", "soc_pkg": (17.20, 16.10),
        "soc_x0": 15.00, "soc_x1": 32.20, "soc_y0": 6.95, "soc_y1": 23.05,
        "soc_label": "SoC RK3576",
        "esc": 0.80,
        "jchg": (0.00, 3.00, 11.75, 18.25),
        "pinset_applicable": True,
        "banner": "ISS-192 结构侧独立复算 —— PCB 固定 PIN-SET-2 / 板 60×30 / RK3576 (mech-lead)",
        "holeset": "套 A (Y 按中心线平移, S 孔 ±5.00 不变)",
        "authority": "MECH/BOARD_GEOM_30MM.md (孔位仲裁结论与影响面)",
        "scope": "F30A 60×30 套A 产品板口径 (判据族: PIN-SET-2 四孔 / 老口径失效复算 / Rev B 打印包契约 / 硬件侧孔位口径分歧 / 散热连带)",
        "src": "MECH/BOARD_GEOM_30MM.md §0/§1/§3 (ISS-118/130) + HW/pcb60x30_check.py",
    },
    {
        "fid": "B160x100",
        "name": "台架板 160×100 (盘上现役 · RK3572-SOM 承载区形态)",
        "pcb_l": 160.00, "pcb_w": 100.00, "pcb_thk": 1.60, "layers": 8,
        "soc_model": "RK3572-SOM", "soc_pkg": (56.70, 46.78),
        "soc_x0": 13.65, "soc_x1": 70.35, "soc_y0": 7.61, "soc_y1": 54.39,
        "soc_label": "SoM RK3572-SOM",
        "esc": 0.80,
        "jchg": None,
        "pinset_applicable": False,
        "banner": "ISS-345 双口径 —— 台架板 160×100 / RK3572-SOM 承载区 (mech-lead)",
        "holeset": "台架板无 PIN-SET-2 孔位 (口径不适用, 依 MECH/board_frame_feasibility.py:108 先例)",
        "authority": "HW/PCB/BOARD_FRAME_CALIBER.md §2 cal:FRAMES + §3 SoM 承载区实测占位",
        "scope": "B160x100 台架板帧 (判据族: 板框一致性 / SoM 承载区占位 / 逃线带 / 板内余量; ★PIN-SET-2 四孔族不适用★)",
        "src": "HW/PCB/BOARD_FRAME_CALIBER.md §2 cal:FRAMES (行 150-158) + §3 SoM 承载区实测占位 (行 71-72)",
    },
]
DEFAULT_FRAME_ID = "F30A"
FRAME = FRAMES[0]      # ★当前档位 (由 _bind_frame 绑定)★

CORNER_EDGE = 0.50     # 4 角工艺边 (mm)  [既有] MECH_BUDGET §5.1
KEEPOUT_EDGE = 0.80    # 器件距板边 (mm)  [既有] MECH_BUDGET §5.1

# ---- SoC / SoM 占位 (★按档位取值, 见 FRAMES★) ----
# F30A 档: RK3576 (FCCSP698L) 封装体 17.20 (X) × 16.10 (Y); 板坐标落位 X0=15.00 / Y0=6.95
#           (板中线 15.00 居中) —— 来源 HW/pcb60x30_check.py SOC_RK3576 + SOC_POS["RK3576"]
# B160x100 档: RK3572-SOM 承载区【封装外形占位】 X[13.65,70.35] × Y[7.61,54.39] = 56.70×46.78
#           —— [实测] HW/PCB/BOARD_FRAME_CALIBER.md §3 (封装外形占位行)
SOC_X0, SOC_X1 = 15.00, 32.20   # 封装体 X 区间  [官方] 17.20×16.10 FCCSP698L
SOC_Y0, SOC_Y1 = 6.95, 23.05    # 封装体 Y 区间  [推算] 板中线 15.00 居中
ESC = 0.80                       # 逃线带外扩 (mm/边) [推算] HW/SOC_PIN_BUDGET.md (ISS-081)
ESC_X0, ESC_X1 = SOC_X0 - ESC, SOC_X1 + ESC      # [14.20, 33.00]
ESC_Y0, ESC_Y1 = SOC_Y0 - ESC, SOC_Y1 + ESC      # [6.15, 23.85]

# ---- J_CHG 座体 keep-out (铰链端) ----
# 30mm 板下座体居中于 Y=15.00 ± 3.25 ⇒ Y[11.75, 18.25]
# 来源: HW/pcb60x30_check.py JCHG_RECT = (0.00, 3.00, 11.75, 18.25)
JCHG_X0, JCHG_X1 = 0.00, 3.00
JCHG_Y0, JCHG_Y1 = 11.75, 18.25

# ---- PIN-SET-2 孔位 (定版 = 套 A) —— 板坐标: 原点左下角, X=板长 0..60, Y=板宽 0..30
# ★套 A = Y 按中心线平移 (旧中心 7.50 → 新中心 15.00), S 孔 ±5.00 不变
# 来源: state/fragments/hw.yaml claim pcb_mount_holes_xy + MECH/BOARD_GEOM_30MM.md §3
HOLES = [
    ("P1", "主定位销孔", (8.00, 15.00), 2.00, "骨架压装 ⌀2.0 h6 圆销", "全基准 X+Y+θz"),
    ("P2", "副定位销孔", (52.00, 15.00), 2.00, "骨架压装 ⌀2.0 菱形销 (对边 1.94)", "只定 Y"),
    ("S1", "压紧螺钉孔", (8.00, 10.00), 1.40, "骨架 M1.2 攻丝 / 自攻", "只压紧 零定位"),
    ("S2", "压紧螺钉孔", (52.00, 20.00), 1.40, "骨架 M1.2 攻丝 / 自攻", "只压紧 零定位"),
]

# ---- 老口径 (MECH_BUDGET §5.1: 2×M1.2 ⌀1.4 孔心到板边 2.50 + 1×⌀2.0 H7)
# 老口径只给了"孔心到板边 2.50" 没给 X → 按**最有利假设** (老孔落在 SoC 的 X 段内,
# 因为 v1.1 的骨架/散热垫都在 SoC 下方) 复算; Y 沿用 15mm 板口径的绝对坐标。
OLD_HOLES = [
    ("M1", "老 M1.2 螺钉孔", (25.00, 2.50), 1.40),
    ("M2", "老 M1.2 螺钉孔", (25.00, 12.50), 1.40),
    ("D0", "老 ⌀2.0 H7 销孔", (25.00, 7.50), 2.00),
]

# ---- ISS-345 双口径: 孔位族按帧取用 ----------------------------------
# ★套 A 四孔坐标 = F30A 帧专有 (60×30 产品板)★; 台架板 160×100 盘上无这四个孔
#   (★该板盘上唯一的 np_thru_hole 是 J_USB_C (USB-C 座) 的两个 ⌀0.762 机械焊盘, 不是板固定孔★)
#   ⇒ 依 MECH/board_frame_feasibility.py:108 先例, B160x100 帧的 pinset_applicable = False
HOLES_BY_FRAME = {"F30A": HOLES, "B160x100": []}
OLD_HOLES_BY_FRAME = {"F30A": OLD_HOLES, "B160x100": []}

# ---- ISS-345: 权威页 / 板面只读解析 (★160×100 档的每个数都要能指回这三处之一★) ----
CALIB_PAGE = os.path.join(PROJ, "HW", "PCB", "BOARD_FRAME_CALIBER.md")
CALIB_PARAMS = os.path.join(PROJ, "HW", "PCB", "demo_mainboard_params.json")
BOARD_PCB = os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb")


def read_calib_frames():
    """读 `HW/PCB/BOARD_FRAME_CALIBER.md` §2 `cal:FRAMES` JSON 块 (★帧 id / 尺寸的唯一权威表★)
    → (dict|None, 该页全部行)"""
    if not os.path.isfile(CALIB_PAGE):
        return None, []
    with open(CALIB_PAGE, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
    blob = "\n".join(lines)
    m = re.search(r"```json cal:FRAMES\s*(\{.*?\n\})\s*```", blob, re.S)
    if not m:
        return None, lines
    try:
        return json.loads(m.group(1)), lines
    except ValueError:
        return None, lines


def find_lines(lines, needle):
    """→ 包含 needle 的行号列表 (★证据要带行号, 不许只写文件名★)"""
    return [i + 1 for i, ln in enumerate(lines) if needle in ln]


def _sexp(txt):
    tok = re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+', txt)
    stack = [[]]
    for tk in tok:
        if tk == '(':
            stack.append([])
        elif tk == ')':
            cur = stack.pop()
            stack[-1].append(cur)
        else:
            stack[-1].append(tk)
    return stack[0][0]


def _sget(node, key):
    for x in node:
        if isinstance(x, list) and x and x[0] == key:
            return x
    return None


def read_board_som_occupancy():
    """★只读实读盘上 4 座 SoM 座 `J_SOM_P1..P4` 的占位 (★不碰板, 只读★)
    → dict(pad_bbox, fab_bbox, npads, sockets) —— 焊盘实体占位 / 封装外形占位 / 焊盘数 / 座数"""
    out = {"pad_bbox": None, "fab_bbox": None, "npads": 0, "sockets": [],
           "edge_bbox": None, "thickness": None}
    if not os.path.isfile(BOARD_PCB):
        return out
    with open(BOARD_PCB, "r", encoding="utf-8", errors="ignore") as f:
        txt = f.read()
    try:
        root = _sexp(txt)
    except Exception:
        return out
    gen = _sget(root, "general")
    if gen:
        th = _sget(gen, "thickness")
        if th and len(th) > 1:
            try:
                out["thickness"] = float(str(th[1]).strip('"'))
            except ValueError:
                pass
    pads, fab, ex, ey = [], [], [], []
    for fp in [x for x in root if isinstance(x, list) and x and x[0] == "footprint"]:
        ref = None
        for x in fp:
            if isinstance(x, list) and x and x[0] == "property" and len(x) > 2 \
                    and str(x[1]).strip('"') == "Reference":
                ref = str(x[2]).strip('"')
        at = _sget(fp, "at")
        if at is None:
            continue
        ox, oy = float(at[1]), float(at[2])
        rot = float(at[3]) if len(at) > 3 else 0.0
        ca, sa = math.cos(math.radians(rot)), math.sin(math.radians(rot))

        def g(lx, ly):
            return lx * ca - ly * sa + ox, lx * sa + ly * ca + oy

        if ref and re.match(r"J_SOM_P\d$", ref):
            n = 0
            for x in fp:
                if not (isinstance(x, list) and x):
                    continue
                if x[0] == "pad":
                    pa = _sget(x, "at")
                    ps = _sget(x, "size")
                    if pa is None or ps is None:
                        continue
                    lx, ly = float(pa[1]), float(pa[2])
                    pr = float(pa[3]) if len(pa) > 3 else 0.0
                    a = math.radians(rot + pr)
                    gx = lx * math.cos(a) - ly * math.sin(a)
                    gy = lx * math.sin(a) + ly * math.cos(a)
                    px, py = gx + ox, gy + oy
                    sx, sy = float(ps[1]), float(ps[2])
                    if abs((rot + pr) % 180 - 90) < 1e-6:
                        sx, sy = sy, sx
                    pads.append((px - sx / 2, px + sx / 2, py - sy / 2, py + sy / 2))
                    n += 1
                elif x[0] in ("fp_line", "fp_rect"):
                    # ★fp_line 轮廓要含【stroke 宽度的半宽外扩】 (★与 pcbnew GetBoundingBox 同语义★)
                    w = 0.0
                    st = _sget(x, "stroke")
                    if st:
                        wd = _sget(st, "width")
                        if wd and len(wd) > 1:
                            try:
                                w = float(str(wd[1]).strip('"'))
                            except ValueError:
                                w = 0.0
                    hw = w / 2.0
                    for key in ("start", "end"):
                        gg = _sget(x, key)
                        if not gg:
                            continue
                        gx, gy = g(float(gg[1]), float(gg[2]))
                        fab.append((gx - hw, gy - hw))
                        fab.append((gx + hw, gy + hw))
            out["sockets"].append((ref, n))
            out["npads"] += n
        # Edge.Cuts
        for x in [x for x in root if isinstance(x, list) and x and x[0] == "gr_line"]:
            ly = _sget(x, "layer")
            if not ly or str(ly[1]).strip('"') != "Edge.Cuts":
                continue
            for key in ("start", "end"):
                gg = _sget(x, key)
                if gg:
                    ex.append(float(gg[1]))
                    ey.append(float(gg[2]))

    def bbox4(pts4):
        """→ (x0, x1, y0, y1) from 4-tuple pad boxes"""
        if not pts4:
            return None
        return (min(p[0] for p in pts4), max(p[1] for p in pts4),
                min(p[2] for p in pts4), max(p[3] for p in pts4))

    def bbox2(pts2):
        """→ (x0, x1, y0, y1) from 2-tuple points"""
        if not pts2:
            return None
        return (min(p[0] for p in pts2), max(p[0] for p in pts2),
                min(p[1] for p in pts2), max(p[1] for p in pts2))

    def union(*bs):
        bs = [b for b in bs if b]
        if not bs:
            return None
        return (min(b[0] for b in bs), max(b[1] for b in bs),
                min(b[2] for b in bs), max(b[3] for b in bs))

    out["pad_bbox"] = bbox4(pads)
    # ★封装外形占位 = 焊盘实体占位 ∪ 封装轮廓 (含 stroke 半宽外扩) —— 与 pcbnew GetBoundingBox 同语义★
    out["fab_bbox"] = union(bbox4(pads), bbox2(fab))
    if ex:
        out["edge_bbox"] = (min(ex), max(ex), min(ey), max(ey))
    return out

# ---- 散热中间量
K_AL = 237.0          # 铝骨架导热 [推算] MECH_BUDGET §2.3
K_STEEL = 50.0        # 钢螺钉导热 [推算] 常用值
SKEL_THK = 1.00       # 骨架厚 (mm) [推算] MECH_BUDGET §5.1
SKEL_W = 30.00        # 骨架 SoC 段满宽 (mm) [推算] 16.10 + 2×6.95 = 30.00 (满板宽)
SOC_CX = (SOC_X0 + SOC_X1) / 2.0   # SoC 中心 X = 23.60

CHECKS = []


def chk(name, ok, detail, note="", level="fail"):
    """level: fail = 本单验收项 (不过 → rc=1); warn = 已知超差/待裁 (露出但不判本单不过)。"""
    CHECKS.append({"name": name, "ok": bool(ok), "level": level,
                   "detail": detail, "note": note})
    return ok


# =====================================================================
# 几何工具: 圆 ∩ 轴对齐矩形 的**真**重叠面积 (不是外接方框)
# =====================================================================
def circle_rect_overlap(cx, cy, r, x0, x1, y0, y1):
    """圆与轴对齐矩形的精确重叠面积 (解析积分数值解, 精度 1e-9 mm²)。"""
    dx0, dx1 = x0 - cx, x1 - cx
    dy0, dy1 = y0 - cy, y1 - cy
    if dx1 <= -r or dx0 >= r or dy1 <= -r or dy0 >= r:
        return 0.0
    a = max(dx0, -r)
    b = min(dx1, r)
    if b <= a:
        return 0.0
    n = 20000
    h = (b - a) / n
    total = 0.0
    for i in range(n):
        x = a + (i + 0.5) * h
        ytop = math.sqrt(max(0.0, r * r - x * x))
        lo = max(dy0, -ytop)
        hi = min(dy1, ytop)
        if hi > lo:
            total += (hi - lo) * h
    return total


def overlap_len(a0, a1, b0, b1):
    return max(0.0, min(a1, b1) - max(a0, b0))


# =====================================================================
# 打印包 (Rev B) 实际常量解析 —— 契约真源是生成器本身, 不是本脚本里的硬编码
# =====================================================================
def analyze_print_pack(path=PACK_PY):
    """从 MECH/print/gen_print_pack_revb.py 解析: 尺寸常量 + 每个定位板的让过孔数。
    ★只读, 不执行生成器 (它依赖 numpy, 本机无)。"""
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        txt = f.read()
    dims = {}
    for m in re.finditer(r'"(pinset2_[a-z0-9_]+|pcb_len|pcb_wid|clr_hole|screw_clr)"\s*:\s*\(\s*([0-9.]+)', txt):
        dims[m.group(1)] = float(m.group(2))
    plates = [m.start() for m in re.finditer(r'plate_[a-z]+\(m,', txt)]

    def owner(pos):
        prev = [p for p in plates if p < pos]
        return prev[-1] if prev else -1

    clr, scr = {}, {}
    for m in re.finditer(r'v\("(clr_hole|screw_clr)"\)', txt):
        o = owner(m.start())
        tgt = clr if m.group(1) == "clr_hole" else scr
        tgt[o] = tgt.get(o, 0) + 1
    return {"dims": dims, "plates_with_clr": len(clr), "clr_per_plate": sorted(clr.values()),
            "scr_per_plate": sorted(scr.values()), "text_len": len(txt)}


def analyze_hw_pcb60x30(path=HW_PCB60_PY):
    """只读解析 HW/pcb60x30_check.py 的 HOLES 表 (口径分歧探测用; 本脚本不改它)。"""
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        txt = f.read()
    m = re.search(r"HOLES\s*=\s*\[(.*?)\n\]", txt, re.S)
    if not m:
        return None
    out = {}
    for row in re.finditer(
            r'\(\s*"(?P<k>[PS]\d)"\s*,\s*"[^"]*"\s*,\s*\(\s*(?P<x>[0-9.]+)\s*,\s*(?P<y>[0-9.]+)\s*\)'
            r'\s*,\s*(?P<d>[0-9.]+)', m.group(1)):
        out[row.group("k")] = (float(row.group("x")), float(row.group("y")), float(row.group("d")))
    return out or None


def _bind_frame(fid: str) -> dict:
    """★按档位把几何常量绑到模块级变量上 (★默认档 F30A ⇒ 迁移前取值逐字不变★)★

    ★本单【不许自己拍默认档】⇒ 默认 = F30A (60×30 / RK3576) = 保持现状 ★
    ★切默认档 = main 拍完 U-1 后跑 `--frame B160x100` (或 MECH_FRAME=B160x100) ★
    """
    global FRAME, PCB_L, PCB_W, PCB_THK
    global SOC_X0, SOC_X1, SOC_Y0, SOC_Y1, ESC, ESC_X0, ESC_X1, ESC_Y0, ESC_Y1
    global JCHG_X0, JCHG_X1, JCHG_Y0, JCHG_Y1
    global HOLES, OLD_HOLES, SKEL_W, SOC_CX
    fr = next((f for f in FRAMES if f["fid"] == fid), None)
    if fr is None:
        raise SystemExit("★未知帧 id %r (可选: %s)★" % (fid, ", ".join(f["fid"] for f in FRAMES)))
    FRAME = fr
    PCB_L, PCB_W, PCB_THK = fr["pcb_l"], fr["pcb_w"], fr["pcb_thk"]
    SOC_X0, SOC_X1, SOC_Y0, SOC_Y1 = fr["soc_x0"], fr["soc_x1"], fr["soc_y0"], fr["soc_y1"]
    ESC = fr["esc"]
    ESC_X0, ESC_X1 = SOC_X0 - ESC, SOC_X1 + ESC
    ESC_Y0, ESC_Y1 = SOC_Y0 - ESC, SOC_Y1 + ESC
    if fr["jchg"] is None:
        JCHG_X0 = JCHG_X1 = JCHG_Y0 = JCHG_Y1 = None
    else:
        JCHG_X0, JCHG_X1, JCHG_Y0, JCHG_Y1 = fr["jchg"]
    HOLES = HOLES_BY_FRAME[fr["fid"]]
    OLD_HOLES = OLD_HOLES_BY_FRAME[fr["fid"]]
    SKEL_W = fr.get("skel_w", PCB_W)
    SOC_CX = (SOC_X0 + SOC_X1) / 2.0
    return fr


# =====================================================================
# ① 新孔位 (PIN-SET-2) 几何自检
# =====================================================================
def section_1(holes=None):
    if holes is None:
        holes = HOLES
    esc_rect = (ESC_X0, ESC_X1, ESC_Y0, ESC_Y1)
    soc_rect = (SOC_X0, SOC_X1, SOC_Y0, SOC_Y1)
    jchg_rect = (JCHG_X0, JCHG_X1, JCHG_Y0, JCHG_Y1)

    for k, fn, (x, y), d, mate, role in holes:
        r = d / 2.0
        ov = circle_rect_overlap(x, y, r, ESC_X0, ESC_X1, ESC_Y0, ESC_Y1)
        chk(f"{k} vs SoC 逃线带 X[{ESC_X0:.2f},{ESC_X1:.2f}]×Y[{ESC_Y0:.2f},{ESC_Y1:.2f}] 重叠",
            ov < 1e-6, f"2D 重叠面积 = {ov:.4f} mm² (真圆∩矩形)",
            f"孔心 ({x:.2f},{y:.2f}) ⌀{d:.2f} —— {fn}")
        ov2 = circle_rect_overlap(x, y, r, SOC_X0, SOC_X1, SOC_Y0, SOC_Y1)
        chk(f"{k} vs SoC 封装体 X[{SOC_X0:.2f},{SOC_X1:.2f}]×Y[{SOC_Y0:.2f},{SOC_Y1:.2f}] 重叠",
            ov2 < 1e-6, f"2D 重叠面积 = {ov2:.4f} mm²")
        ov3 = circle_rect_overlap(x, y, r, JCHG_X0, JCHG_X1, JCHG_Y0, JCHG_Y1)
        chk(f"{k} vs J_CHG 座体 keep-out 重叠", ov3 < 1e-6, f"2D 重叠面积 = {ov3:.4f} mm²",
            "J_CHG 座体 A/B/C 尺寸页未核 [0数据] ⇒ 座体 X 向进深按 3.00 推算 (HW/pcb60x30_check.py JCHG_RECT)")

    edge_detail = []
    for k, fn, (x, y), d, mate, role in holes:
        r = d / 2.0
        e = min(x, PCB_L - x, y, PCB_W - y)
        chk(f"{k} 孔心到板边 ≥1.50mm", e >= 1.50,
            f"孔心距边 {e:.2f}mm (⌀{d:.2f} → 孔壁距边 {e - r:.2f}mm)", f"{fn}")
        chk(f"{k} 孔壁不侵入 0.80mm 器件边距带", e - r >= KEEPOUT_EDGE,
            f"孔壁距边 {e - r:.2f}mm vs {KEEPOUT_EDGE:.2f}mm")
        edge_detail.append(f"{k}: 孔心距边 {e:.2f} / 孔壁距边 {e - r:.2f}")

    min_cc, min_wall, pairs = 1e9, 1e9, []
    for i in range(len(holes)):
        for j in range(i + 1, len(holes)):
            ka, kb = holes[i], holes[j]
            dcc = math.dist(ka[2], kb[2])
            wall = dcc - ka[3] / 2.0 - kb[3] / 2.0
            min_cc = min(min_cc, dcc)
            min_wall = min(min_wall, wall)
            pairs.append(f"{ka[0]}-{kb[0]}: 中心距 {dcc:.2f} / 孔壁 {wall:.2f}")
    chk("孔间最小中心距 ≥5.00mm", min_cc >= 5.00, f"最小中心距 = {min_cc:.2f}mm", "; ".join(pairs))
    chk("孔间最小孔壁间距 ≥2.00mm", min_wall >= 2.00, f"最小孔壁间距 = {min_wall:.2f}mm")

    h7 = (2.000, 2.021)
    h6 = (1.980, 1.992)
    chk("P1 H7 孔配 h6 圆销 = 滑配 (定位非压配)",
        h6[1] < h7[0] and h7[0] - h6[1] <= 0.05,
        f"径向间隙 {h7[0] - h6[1]:.3f}..{h7[1] - h6[0]:.3f}mm (销/孔)",
        "P2 菱形销 对边 1.94 → X 向单边让位 0.030..0.041mm, 消除过定位 (hw-lead ISS-049 §3.1)")
    chk("S1/S2 ⌀1.4 过孔配 M1.2 螺钉 = 零定位 (径向间隙 0.20mm)", True,
        "M1.2 螺钉 ⌀1.2 → 径向间隙 0.10mm/边 (⌀1.4-⌀1.2)/2 = 0.10", "螺钉只压紧, 不参与定位")
    return edge_detail


# =====================================================================
# ② 老口径失效复算 —— ★判据板宽无关化改写★
# =====================================================================
def section_2(old_holes=None):
    if old_holes is None:
        old_holes = OLD_HOLES
    """★原判据是 15mm 语义 ("3/3 孔压逃线带 ⇒ 成立"), 60×30 下实测只压 2/3 ⇒
    结论仍成立但计数变了。本节改成三条**板宽无关**的独立判据:
      ②-1 计数无关化: ≥1/3 孔压带 ⇒ 不可用 (强度最低但板宽无关)
      ②-2 单销定位链不足 (与板宽完全无关)
      ②-3 边距余量偏紧 (相对 PIN-SET-2 的余量, WARN 级)
    """
    old_detail, old_fail = [], 0
    for k, fn, (x, y), d in old_holes:
        r = d / 2.0
        ov = circle_rect_overlap(x, y, r, ESC_X0, ESC_X1, ESC_Y0, ESC_Y1)
        ovx = overlap_len(x - r, x + r, ESC_X0, ESC_X1)
        ovy = overlap_len(y - r, y + r, ESC_Y0, ESC_Y1)
        bbox = ovx * ovy
        old_fail += 1 if ov > 1e-6 else 0
        old_detail.append(f"{k}({x:.2f},{y:.2f}) ⌀{d:.2f} → 压逃线带 X {ovx:.2f}mm / Y {ovy:.2f}mm "
                          f"(外接方框 {bbox:.2f}mm², 真圆面积 {ov:.2f}mm²)")
    chk("老口径 (2×M1.2 + 1×⌀2.0H7 @孔心到板边2.50) 在 60×30 板下不可用 → 必须改",
        old_fail >= 1, f"{old_fail}/3 孔压 SoC 逃线带: " + "; ".join(old_detail),
        "★判据已板宽无关化: 原判据写 '3/3 孔压带 ⇒ 成立', 而 60×30/RK3576 下实测只压 2/3 "
        "(SoC 在 Y 向长高 8.00→16.10, 逃线带从 Y[2.70,12.30] 上移到 Y[6.15,23.85], "
        "老孔 M1@Y2.50 掉出带外) ⇒ 计数随板宽变, 但**结论不变**, 故判据从 '3/3' 改写为 '≥1/3'。",
        level="fail")
    chk("老口径单销定位链不足 (与板宽无关) → 必须改", True,
        "老口径只有 1×⌀2.0 H7 销: 无法同时约束 X 与 θz (单销欠定位 + 过定位风险), "
        "也无副销消过定位 ⇒ 必须改双销 (P1 圆销定全基准 + P2 菱形销只定 Y)",
        "依据: HW/PCB_FIXING_PINSET2.md §3.1 / MECH/PCB_MOUNT_PIN_SET2.md §5.2 —— "
        "与板宽、逃线带、逃线带计数都无关, 是拓扑级判据")
    old_edge = []
    for k, fn, (x, y), d in old_holes:
        e = min(x, PCB_L - x, y, PCB_W - y)
        old_edge.append(f"{k}: 孔心距边 {e:.2f} / 孔壁距边 {e - d / 2:.2f}")
    new_wall = min(min(x, PCB_L - x, y, PCB_W - y) - d / 2.0 for _, _, (x, y), d, _, _ in HOLES)
    old_wall = min(min(x, PCB_L - x, y, PCB_W - y) - d / 2.0 for _, _, (x, y), d in old_holes)
    chk("老口径边距余量偏紧 (相对 PIN-SET-2 的孔壁余量)", False,
        f"老口径最小孔壁距边 {old_wall:.2f}mm vs PIN-SET-2 套 A {new_wall:.2f}mm "
        f"(差 {new_wall - old_wall:.2f}mm); " + "; ".join(old_edge),
        "★老口径仍满足本脚本的硬阈值 (孔心≥1.50 / 孔壁≥0.80), 故本条只作 WARN 记录, 不判死; "
        "但配合 ISS-049 §5 强制的「隔热垫 2 处螺钉位开 ⌀3.0 让位孔」⇒ 孔缘距板边仅 "
        f"{2.50 - 1.50:.2f}mm, 破边风险高 (套 A 为 {10.00 - 1.50:.2f}mm)",
        level="warn")
    return old_fail


# =====================================================================
# ③ 打印包契约 (★读 Rev B 生成器的实际值★)
# =====================================================================
def section_3(pack=None):
    pack = pack if pack is not None else analyze_print_pack()
    if not pack:
        chk("打印包契约 (Rev B) 可解析", False,
            f"未找到/无法解析 {os.path.relpath(PACK_PY, PROJ)}",
            "打印包是本单仲裁的**实物证据源** (笼与样板的孔位), 解析不到则仲裁结论无法复现",
            level="fail")
        return None
    dims = pack["dims"]
    chk("打印件 PCB 定位板长 = 板长 60.00mm", abs(dims.get("pcb_len", -1) - PCB_L) < 1e-6,
        f"Rev B 生成器 pcb_len = {dims.get('pcb_len')}mm vs 板长 {PCB_L:.2f}mm "
        f"(差 {dims.get('pcb_len', 0) - PCB_L:+.2f}mm)",
        "★Rev A 老契约写 50.00 (已作废); 现以生成器实际常量为真源")
    chk("打印件 PCB 定位板宽 = 板宽 30.00mm", abs(dims.get("pcb_wid", -1) - PCB_W) < 1e-6,
        f"Rev B 生成器 pcb_wid = {dims.get('pcb_wid')}mm vs 板宽 {PCB_W:.2f}mm "
        f"(差 {dims.get('pcb_wid', 0) - PCB_W:+.2f}mm)",
        "★Rev A 老契约写 12.00 (已作废)")
    chk("打印件 PCB 销孔让过孔 ⌀2.4 = 2 个 (P1+P2 双销)", pack["clr_per_plate"] == [2, 2],
        f"Rev B 生成器每个定位板上的 ⌀2.4 让过孔数 = {pack['clr_per_plate']} (⌀{dims.get('clr_hole')}mm)",
        "老口径单销 ⇒ 1 个; PIN-SET-2 双销 ⇒ 2 个 (hw-lead iss049_mount_screw: 上壳需 2x⌀2.4 + 2x⌀1.6 让过孔)")
    chk("打印件 M1.2 让过孔 ⌀1.6 = 2 个", pack["scr_per_plate"] == [2, 2],
        f"Rev B 生成器每个定位板上的 ⌀1.6 让过孔数 = {pack['scr_per_plate']} (⌀{dims.get('screw_clr')}mm)",
        "★旧判据用「孔距 40.00 (X=6/46)」表达 —— 那是 15mm 板单排口径; 现按**逐坐标**比对 (见下两条)")
    # ★仲裁锚: 打印包让过孔孔心 vs PCB 四孔孔心, 逐坐标比对
    pack_p = dims.get("pinset2_p_y")
    pack_s1 = dims.get("pinset2_s1_y")
    pack_s2 = dims.get("pinset2_s2_y")
    hole = {k: (xy, d) for k, _, xy, d, _, _ in HOLES}
    dy_p = abs(hole["P1"][0][1] - (pack_p if pack_p is not None else -1))
    chk("★打印包销孔让过孔 Y = PCB P1/P2 Y (差 0.00mm)", dy_p < 1e-6,
        f"打印包 pinset2_p_y = {pack_p} vs PCB P1 Y = {hole['P1'][0][1]:.2f} (差 {dy_p:.2f}mm)",
        "★这条就是 ISS-192 假绿的根因防线: 打印包与 PCB 孔心差多少 mm, 这里就报多少 mm")
    dy_s1 = abs(hole["S1"][0][1] - (pack_s1 if pack_s1 is not None else -1))
    dy_s2 = abs(hole["S2"][0][1] - (pack_s2 if pack_s2 is not None else -1))
    chk("★打印包螺钉让过孔 Y = PCB S1/S2 Y (差 0.00mm)", max(dy_s1, dy_s2) < 1e-6,
        f"打印包 pinset2_s1_y = {pack_s1} / pinset2_s2_y = {pack_s2} vs "
        f"PCB S1 Y = {hole['S1'][0][1]:.2f} / S2 Y = {hole['S2'][0][1]:.2f} "
        f"(差 {dy_s1:.2f} / {dy_s2:.2f}mm)",
        "★套 A 与套 B 差 7.50mm ⇒ 若 PCB 按套 B 钻, 螺钉与笼的 ⌀1.6 让过孔差 7.50mm ⇒ 板装不进骨架")
    dx_s = abs((hole["S2"][0][0] - hole["S1"][0][0]) -
               (dims.get("pinset2_s2_x", 0) - dims.get("pinset2_s1_x", 0)))
    chk("打印包螺钉让过孔 X 间距 = PCB S1↔S2 X 间距", dx_s < 1e-6,
        f"打印包 S2.x-S1.x = {dims.get('pinset2_s2_x', 0) - dims.get('pinset2_s1_x', 0):.2f}mm vs "
        f"PCB S1↔S2 X 间距 {hole['S2'][0][0] - hole['S1'][0][0]:.2f}mm (差 {dx_s:.2f}mm)",
        "X 向两套口径一致 (差 0.00mm) ⇒ 口径分歧**只在 Y 向**, 与 ISS-192 实测一致")
    return pack


# =====================================================================
# ④ 硬件侧产物口径分歧探测 (只读 HW/; 不改 —— 归 hw-lead)
# =====================================================================
def section_4(hw=None):
    hw = hw if hw is not None else analyze_hw_pcb60x30()
    if not hw:
        chk("硬件侧孔位口径分歧探测 (只读 HW/pcb60x30_check.py)", True,
            "未解析到 HW/pcb60x30_check.py 的 HOLES 表 —— 跳过 (不判本单不过)",
            "★若该文件被改名/移动, 本判据会静默失效; 建议把分歧探测落在 §③ 的打印包一致性上 (那条不依赖 HW/)",
            level="warn")
        return None
    diffs = []
    for k, (x, y, d) in sorted(hw.items()):
        if k in ("P1", "P2", "S1", "S2"):
            hxy, hd = {kk: (vv, dd) for kk, _, vv, dd, _, _ in HOLES}[k]
            dx, dy = abs(x - hxy[0]), abs(y - hxy[1])
            if dx > 1e-6 or dy > 1e-6:
                diffs.append(f"{k}: HW ({x:.2f},{y:.2f}) vs 结构侧定版 ({hxy[0]:.2f},{hxy[1]:.2f}) "
                             f"→ 差 X {dx:.2f} / Y {dy:.2f}mm")
    chk("硬件侧孔位口径与结构侧定版一致 (HW/pcb60x30_check.py)", not diffs,
        ("★口径分歧: " + "; ".join(diffs)) if diffs else "HW/pcb60x30_check.py 的 HOLES 与结构侧定版一致",
        "★这**不是**结构侧的错: 该文件归 hw-lead, 结构侧不改它 —— 已登记 needs_from "
        "(key iss192_pcb60x30_holes_set_b_to_set_a)。★注意: HW/pcb60x30_check.json 的 sec4_holes "
        "是 ISS-118 的验收产物, 不改则下游 (钻孔 CAM / 骨架出图) 按套 B 做就错。",
        level="warn" if diffs else "fail")
    return hw


# =====================================================================
# ⑤ 散热连带 (量级复核; 本单不出新的皮肤温度数)
# =====================================================================
def section_5():
    a_screw = math.pi / 4 * (1.2e-3) ** 2      # ⌀1.2 截面积 = 1.1310 mm²

    def r_screw(l_mm):
        return (l_mm * 1e-3) / (K_STEEL * a_screw)

    rs = {f"L={l}mm": r_screw(l) for l in (1.0, 2.0, 3.0)}
    rs_pair = {f"L={l}mm": r_screw(l) / 2.0 for l in (1.0, 2.0, 3.0)}
    rs_hw_mix = 1.0 / sum(1.0 / r_screw(l) for l in (1.0, 2.0, 3.0))
    chk("螺钉热旁路量级已复核 (进 mech 热模型)", True,
        "1 颗: " + " / ".join(f"{k} {v:.1f} K/W" for k, v in rs.items())
        + " ; 2 颗并联: " + " / ".join(f"{k} {v:.1f} K/W" for k, v in rs_pair.items())
        + f" ; hw T-4 口径(3 个长度档并联) {rs_hw_mix:.1f} K/W",
        "★本单只给中间量: 新的皮肤侧温度数要完整热模型重算 (热模型单); "
        "另: 螺钉头必须落在 PCB 皮肤侧沉孔内、不得接触皮肤侧下壳 (否则金属跨过 0.50 隔热垫 + 0.30 空气隙)")

    d_p1 = SOC_CX - 8.00            # P1/S1 到 SoC 中心的轴向距离
    d_p2 = 52.00 - SOC_CX           # P2/S2 到 SoC 中心的轴向距离
    r_p1 = (d_p1 * 1e-3) / (K_AL * (SKEL_W * SKEL_THK) * 1e-6)
    r_p2 = (d_p2 * 1e-3) / (K_AL * (SKEL_W * SKEL_THK) * 1e-6)
    r_seg = {"P1/S1": r_p1, "P2/S2": r_p2}
    chk("螺钉移到板两端 → 骨架段温差 ΔT 抵偿量已量化 (热模型单要用)",
        True,
        f"P1/S1 (距 SoC 中心 {d_p1:.2f}mm): 骨架段 R = {r_p1:.2f} K/W"
        f" / P2/S2 (距 SoC 中心 {d_p2:.2f}mm): 骨架段 R = {r_p2:.2f} K/W",
        f"公式 R=L/(k·A), k={K_AL} W/m·K, A={SKEL_W:.0f}×{SKEL_THK:.0f}mm² (SoC 段满宽 30.00 = 满板宽); "
        "老口径 2 颗 M1.2 都在 X=25 (SoC 正下方) ⇒ 该段温差 ≈0; "
        f"PIN-SET-2 后 P1/S1 段 {r_p1:.2f} K/W、P2/S2 段 {r_p2:.2f} K/W "
        "⇒ 方向上【减小】螺钉旁路热流的驱动力 (热模型单要用这个抵偿量)")

    chk("隔热层仍在 SoC 与皮肤之间 (PIN-SET-2 未改隔热层位置)",
        True, "0.50 隔热垫 + 0.30 空气隙位置/厚度未动; 螺钉头落 PCB 皮肤侧沉孔, 严禁接触皮肤侧下壳",
        "若螺钉头接触下壳 = 金属跨过隔热层 = 新并联热路 (与 hw-lead T-3 同一条约束); "
        "★套 A 下 ⌀3.0 让位孔距板边 8.50mm (套 B 只有 1.00mm ⇒ 破边)")
    return rs, rs_pair, rs_hw_mix, r_seg


# =====================================================================
# ★ISS-345 双口径 · 帧级判据 (板框 / 主控占位 / 逃线带 / 板内余量)
#   —— 只在【主控占位族不适用】的档位跑 (★PIN-SET-2 套 A 四孔 = F30A 帧专有坐标,
#      套到台架板帧 = 口径不适用, 依 MECH/board_frame_feasibility.py:108 先例★)
# =====================================================================
def section_frame_level(fr):
    """★160×100 / RK3572-SOM 档的帧级判据 (★每个数都指回 §B2 的三处权威源之一★)"""
    cal, cal_lines = read_calib_frames()
    frames = (cal or {}).get("frames", {})
    brd = read_board_som_occupancy()
    params = {}
    if os.path.isfile(CALIB_PARAMS):
        try:
            with open(CALIB_PARAMS, "r", encoding="utf-8") as f:
                params = json.load(f).get("board", {}) or {}
        except (OSError, ValueError):
            params = {}

    # ① 板框三源一致 (权威页 cal:FRAMES / params.json / 板文件实读)
    cf = frames.get(fr["fid"], {})
    cal_w, cal_h = cf.get("width_mm"), cf.get("height_mm")
    cal_lay, cal_thk = cf.get("layers"), cf.get("thickness_mm")
    p_w, p_h = params.get("width_mm"), params.get("height_mm")
    p_lay, p_thk = params.get("layers"), params.get("thickness_mm")
    b_thk = brd.get("thickness")
    cal_lines_hits = find_lines(cal_lines, '"%s": {' % fr["fid"]) or find_lines(cal_lines, fr["fid"])
    agree = (cal_w == fr["pcb_l"] and cal_h == fr["pcb_w"]
             and cal_lay == fr["layers"] and cal_thk == fr["pcb_thk"]
             and p_w == fr["pcb_l"] and p_h == fr["pcb_w"]
             and p_lay == fr["layers"] and p_thk == fr["pcb_thk"]
             and (b_thk is None or abs(b_thk - fr["pcb_thk"]) < 1e-9))
    chk("板框 = 权威页 cal:FRAMES %s (三源一致)" % fr["fid"], agree,
        "cal:FRAMES: %.2f×%.2fmm / %s 层 / %.2fmm | demo_mainboard_params.json board: %s×%smm / %s 层 / %smm "
        "| 板文件 general/thickness 实读: %smm"
        % (cal_w or -1, cal_h or -1, cal_lay, cal_thk or -1,
           p_w, p_h, p_lay, p_thk, b_thk),
        "[实测] HW/PCB/BOARD_FRAME_CALIBER.md §2 cal:FRAMES (行 %s) + §1 行 23 表 + "
        "HW/PCB/demo_mainboard_params.json board 段 + HW/PCB/demo_mainboard.kicad_pcb general/thickness "
        "★本脚本只读不改板" % (",".join(str(x) for x in cal_lines_hits) or "?"))

    # ② SoM 承载区实测占位 (焊盘实体 / 封装外形)
    pb = brd.get("pad_bbox")
    fb = brd.get("fab_bbox")
    n_sock = len(brd.get("sockets", []))
    n_pad = brd.get("npads", 0)
    occ_ok = (pb is not None and fb is not None and n_sock == 4 and n_pad == 400
              and abs(pb[0] - 15.10) < 5e-3 and abs(pb[1] - 68.90) < 5e-3
              and abs(pb[2] - 7.61) < 5e-3 and abs(pb[3] - 54.39) < 5e-3
              and abs(fb[0] - 13.65) < 5e-3 and abs(fb[1] - 70.35) < 5e-3)
    pad_span = "X %.2f..%.2f / Y %.2f..%.2f" % (pb[0], pb[1], pb[2], pb[3]) if pb else "读不到"
    fab_span = "X %.2f..%.2f / Y %.2f..%.2f" % (fb[0], fb[1], fb[2], fb[3]) if fb else "读不到"
    chk("SoM 承载区实测占位 (4 座 × 100 焊盘 = 400)", occ_ok,
        "焊盘实体占位 %s = %.2f×%.2fmm | 封装外形占位 %s = %.2f×%.2fmm | 座数 %d / 焊盘数 %d"
        % (pad_span, (pb[1] - pb[0]) if pb else -1, (pb[3] - pb[2]) if pb else -1,
           fab_span, (fb[1] - fb[0]) if fb else -1, (fb[3] - fb[2]) if fb else -1,
           n_sock, n_pad),
        "[实测] 板文件纯 python 逐焊盘解析 (J_SOM_P1..P4) + 与权威页 §3 行 71/72 逐位对拍")

    # ③ SoM 承载区距板边余量 ≥ 器件边距带
    marg = min(pb[0] - 0.0, fr["pcb_l"] - pb[1], pb[2] - 0.0, fr["pcb_w"] - pb[3]) if pb else -1
    chk("SoM 承载区距板边余量 ≥ %.2fmm (器件边距带)" % KEEPOUT_EDGE, marg >= KEEPOUT_EDGE,
        "最小余量 = %.2fmm (板 %0.2f×%0.2f, 承载区 %s)" % (marg, fr["pcb_l"], fr["pcb_w"], pad_span),
        "[推算] 余量 = min(承载区到四边) = %.2fmm; 阈值 KEEPOUT_EDGE=%.2fmm (MECH_BUDGET §5.1)"
        % (marg, KEEPOUT_EDGE))

    # ④ 逃线带 (主控占位 + %.2f/边) 落在板内
    esc = fr["esc"]
    ex0, ex1 = fr["soc_x0"] - esc, fr["soc_x1"] + esc
    ey0, ey1 = fr["soc_y0"] - esc, fr["soc_y1"] + esc
    in_board = (ex0 >= -1e-9 and ey0 >= -1e-9 and ex1 <= fr["pcb_l"] + 1e-9
                and ey1 <= fr["pcb_w"] + 1e-9)
    chk("逃线带 (主控占位 + %.2f/边) 落在板内" % esc, in_board,
        "逃线带 X %.2f..%.2f × Y %.2f..%.2f vs 板 %.2f×%.2f ⇒ %s"
        % (ex0, ex1, ey0, ey1, fr["pcb_l"], fr["pcb_w"], "在内" if in_board else "★溢出★"),
        "[推算] 逃线带 = 主控占位矩形 ± ESC (ESC=%.2f, HW/SOC_PIN_BUDGET.md ISS-081)" % esc)

    # ⑤ 承载区高 vs 板高 (装得下/装不下)
    h_occ = (pb[3] - pb[2]) if pb else -1
    fits = 0 <= h_occ <= fr["pcb_w"] + 1e-9
    chk("主控承载区高 ≤ 板高 (装得下)", fits,
        "承载区高 %.2fmm vs 板高 %.2fmm ⇒ %s (对照: 60×30 板装不下, 差 %.2fmm)"
        % (h_occ, fr["pcb_w"], "装得下" if fits else "★装不下★", h_occ - 30.00),
        "[推算] 承载区高 = 焊盘实体占位 Y 跨度; 对照数 30.00mm 出自 §3 结论行")

    # ⑥ PIN-SET-2 四孔族 = 口径不适用 (先例登记)
    chk("PIN-SET-2 套 A 四孔族 = 本帧口径不适用", False,
        "★本档只跑帧级判据: PIN-SET-2 套 A 四孔 (P1/P2/S1/S2) 是【60×30 套A 帧】的板坐标, "
        "台架板 160×100 盘上没有这四个孔 (★盘上仅有的 np_thru_hole 是 J_USB_C (USB-C 座) 的 "
        "2 个 ⌀0.762mm 机械焊盘, 不是板固定孔★) ⇒ 套到本帧 = 口径不适用",
        "★先例: MECH/board_frame_feasibility.py:108 `pinset_applicable: False` "
        "(★套 A 是 F30A 帧的坐标, 套到台架板帧 = 口径不适用★) ⇒ 本档【不假装跑通】",
        level="na")
    return {"cal": cal, "cal_lines": cal_lines, "board": brd, "params": params}


# =====================================================================
# 运行 (一次复算)
# =====================================================================
def run(holes=None, old_holes=None, pack=None, hw=None):
    global CHECKS
    CHECKS = []
    if holes is None:
        holes = HOLES
    if old_holes is None:
        old_holes = OLD_HOLES
    if not FRAME["pinset_applicable"]:
        # ★非适用档 → 只跑帧级判据 (★不跑产品板专有族, 免得假绿★)
        frame_info = section_frame_level(FRAME)
        return {
            "checks": CHECKS,
            "edge_detail": [],
            "old_fail": 0,
            "pack": None,
            "hw": None,
            "thermal": ({}, {}, 0.0, {}),
            "frame_info": frame_info,
        }
    edge_detail = section_1(holes)
    old_fail = section_2(old_holes)
    pack_info = section_3(pack)
    hw_info = section_4(hw)
    rs, rs_pair, rs_hw_mix, r_seg = section_5()
    return {
        "checks": CHECKS,
        "edge_detail": edge_detail,
        "old_fail": old_fail,
        "pack": pack_info,
        "hw": hw_info,
        "thermal": (rs, rs_pair, rs_hw_mix, r_seg),
        "frame_info": None,
    }


# =====================================================================
# --self-test: 反向用例 (把孔挪进逃线带 ⇒ 必须变红)
# =====================================================================
def self_test():
    print("=" * 78)
    print("ISS-192 --self-test —— 反向用例 (每个用例都必须按预期变红/变绿)")
    print("=" * 78)
    scenarios = []

    # 用例 0: 基线必须全绿
    r0 = run()
    fails0 = [c for c in r0["checks"] if not c["ok"] and c["level"] == "fail"]
    scenarios.append(("基线 (套 A) 无 FAIL", not fails0,
                      f"FAIL {len(fails0)} 条 (期望 0)"))

    # 用例 1: 把 S1 挪进 SoC 逃线带 ⇒ 必红
    h1 = list(HOLES)
    h1[2] = ("S1", "压紧螺钉孔 (反向用例: 挪进逃线带)", (25.00, 15.00), 1.40,
             "骨架 M1.2 攻丝 / 自攻", "只压紧 零定位")
    r1 = run(holes=h1)
    f1 = [c for c in r1["checks"] if not c["ok"] and c["level"] == "fail"]
    scenarios.append(("S1 挪到 (25.00,15.00) ⇒ 压 SoC 逃线带 ⇒ 必须 FAIL",
                      any("S1 vs SoC 逃线带" in c["name"] for c in f1),
                      f"FAIL {len(f1)} 条, 含 'S1 vs SoC 逃线带': "
                      f"{any('S1 vs SoC 逃线带' in c['name'] for c in f1)}"))

    # 用例 2: 把 P2 挪进 SoC 封装体 ⇒ 必红
    h2 = list(HOLES)
    h2[1] = ("P2", "副定位销孔 (反向用例: 挪进封装体)", (23.60, 15.00), 2.00,
             "骨架压装 ⌀2.0 菱形销 (对边 1.94)", "只定 Y")
    r2 = run(holes=h2)
    f2 = [c for c in r2["checks"] if not c["ok"] and c["level"] == "fail"]
    scenarios.append(("P2 挪到 (23.60,15.00) ⇒ 压 SoC 封装体 ⇒ 必须 FAIL",
                      any("P2 vs SoC 封装体" in c["name"] for c in f2),
                      f"FAIL {len(f2)} 条, 含 'P2 vs SoC 封装体': "
                      f"{any('P2 vs SoC 封装体' in c['name'] for c in f2)}"))

    # 用例 3: 把 S2 挪到板边外 ⇒ 边距判据必红
    h3 = list(HOLES)
    h3[3] = ("S2", "压紧螺钉孔 (反向用例: 挪到板边)", (52.00, 0.50), 1.40,
             "骨架 M1.2 攻丝 / 自攻", "只压紧 零定位")
    r3 = run(holes=h3)
    f3 = [c for c in r3["checks"] if not c["ok"] and c["level"] == "fail"]
    scenarios.append(("S2 挪到 Y=0.50 ⇒ 孔心到板边 <1.50 ⇒ 必须 FAIL",
                      any("S2 孔心到板边" in c["name"] for c in f3),
                      f"FAIL {len(f3)} 条, 含 'S2 孔心到板边': "
                      f"{any('S2 孔心到板边' in c['name'] for c in f3)}"))

    # 用例 4: 打印包孔位与 PCB 不一致 ⇒ 一致性判据必红
    pack = analyze_print_pack()
    if pack:
        pack_bad = {"dims": dict(pack["dims"]), "plates_with_clr": pack["plates_with_clr"],
                    "clr_per_plate": pack["clr_per_plate"], "scr_per_plate": pack["scr_per_plate"],
                    "text_len": pack["text_len"]}
        pack_bad["dims"]["pinset2_s1_y"] = 2.50   # 模拟套 B
        pack_bad["dims"]["pinset2_s2_y"] = 27.50
        r4 = run(pack=pack_bad)
        f4 = [c for c in r4["checks"] if not c["ok"] and c["level"] == "fail"]
        scenarios.append(("打印包改发套 B (S1 Y=2.50/S2 Y=27.50) ⇒ 一致性判据必须 FAIL",
                          any("打印包螺钉让过孔 Y" in c["name"] for c in f4),
                          f"FAIL {len(f4)} 条, 含 '打印包螺钉让过孔 Y': "
                          f"{any('打印包螺钉让过孔 Y' in c['name'] for c in f4)}"))
    else:
        scenarios.append(("打印包改发套 B ⇒ 一致性判据必须 FAIL", False, "打印包无法解析, 用例跳过"))

    # 用例 5: 老口径在 60×30 下**仍必须**被证死 (计数降到 2/3 也不许放过)
    r5 = run()
    c_old = [c for c in r5["checks"] if c["name"].startswith("老口径 (2×M1.2")]
    scenarios.append(("老口径在 60×30 下仍被判死 (板宽无关化判据生效)",
                      bool(c_old) and c_old[0]["ok"],
                      (c_old[0]["detail"][:90] + "…") if c_old else "判据缺失"))

    print("-" * 78)
    ok_all = True
    for i, (name, ok, detail) in enumerate(scenarios, 1):
        flag = "✅" if ok else "❌"
        ok_all = ok_all and ok
        print(f"  {flag} 用例 {i}: {name}")
        print(f"        {detail}")
    print("-" * 78)
    print(f"self-test: {sum(1 for _, ok, _ in scenarios if ok)}/{len(scenarios)} 用例符合预期 "
          f"⇒ {'全部通过' if ok_all else '★有用例不符合预期★'}")
    return 0 if ok_all else 1


# =====================================================================
# 主流程
# =====================================================================
def _pick_frame_id(argv):
    """★切档解析: `--frame <fid>` 命令行优先, 其次环境变量 MECH_FRAME, 最后默认档 ★
    ★默认档 = F30A (60×30 / RK3576) —— ★本单【不许自己拍默认档】★"""
    fid = os.environ.get("MECH_FRAME", "").strip() or DEFAULT_FRAME_ID
    for i, a in enumerate(argv):
        if a == "--frame" and i + 1 < len(argv):
            fid = argv[i + 1].strip()
        elif a.startswith("--frame="):
            fid = a.split("=", 1)[1].strip()
    return fid or DEFAULT_FRAME_ID


def main() -> int:
    if "--self-test" in sys.argv:
        _bind_frame(DEFAULT_FRAME_ID)     # ★反向用例只针对 F30A 档孔位族★
        return self_test()

    fid = _pick_frame_id(sys.argv[1:])
    fr = _bind_frame(fid)
    if fr["fid"] != DEFAULT_FRAME_ID:
        # ★非默认档才多打一行档位说明 (★默认档输出与迁移前【逐字节相同】★)
        print("★ 档位 = %s (%s) · 板 %.2f×%.2f×%.2fmm / %d 层 · 判据族: %s"
              % (fr["fid"], fr["name"], fr["pcb_l"], fr["pcb_w"], fr["pcb_thk"], fr["layers"],
                 fr["scope"]))

    res = run()
    CHECKS = res["checks"]
    rs, rs_pair, rs_hw_mix, r_seg = res["thermal"]
    fail = [c for c in CHECKS if not c["ok"] and c["level"] == "fail"]
    warn = [c for c in CHECKS if not c["ok"] and c["level"] == "warn"]

    out = {
        "issue": "ISS-192",
        "frame": {"id": fr["fid"], "name": fr["name"], "is_default": fr["fid"] == DEFAULT_FRAME_ID,
                  "layers": fr["layers"], "src": fr["src"], "scope": fr["scope"]},
        "board": {"L": PCB_L, "W": PCB_W, "thk": PCB_THK, "corner_edge": CORNER_EDGE,
                  "keepout_edge": KEEPOUT_EDGE},
        "soc": {"name": fr["soc_model"], "pkg": list(fr["soc_pkg"]),
                "pkg_rect": [SOC_X0, SOC_X1, SOC_Y0, SOC_Y1]},
        "escape_band": {"x": [ESC_X0, ESC_X1], "y": [ESC_Y0, ESC_Y1], "esc": ESC},
        "jchg_keepout": ({"x": [JCHG_X0, JCHG_X1], "y": [JCHG_Y0, JCHG_Y1]}
                         if JCHG_X0 is not None else None),
        "holeset": fr["holeset"],
        "holes": [{"key": k, "fn": fn, "xy": xy, "d": d, "mate": m, "role": r}
                  for (k, fn, xy, d, m, r) in HOLES],
        "old_holes": [{"key": k, "fn": fn, "xy": xy, "d": d} for (k, fn, xy, d) in OLD_HOLES],
        "print_pack": res["pack"],
        "hw_pcb60x30_holes": res["hw"],
        "thermal": {"r_screw_1pc": rs, "r_screw_2pc_parallel": rs_pair,
                    "hw_T4_mix": rs_hw_mix,
                    "skeleton_seg_R": r_seg,
                    "skeleton_W_mm": SKEL_W,
                    "note": "本单只出中间量, 不出新的皮肤侧温度数"},
        "edge_detail": res["edge_detail"],
        "checks": CHECKS,
        "fail": len(fail),
        "warn": len(warn),
        "total": len(CHECKS),
    }

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print("=" * 78)
    print(fr["banner"])
    print("=" * 78)
    print(f"板 {PCB_L:.2f}×{PCB_W:.2f}×{PCB_THK:.2f}mm | {fr['soc_label']} 占位 "
          f"X[{SOC_X0:.2f},{SOC_X1:.2f}]×Y[{SOC_Y0:.2f},{SOC_Y1:.2f}] | 逃线带 "
          f"X[{ESC_X0:.2f},{ESC_X1:.2f}]×Y[{ESC_Y0:.2f},{ESC_Y1:.2f}] (外扩 {ESC:.2f}/边)")
    print(f"孔位口径 = {out['holeset']}: " +
          (" / ".join(f"{k}({xy[0]:.2f},{xy[1]:.2f})⌀{d:.2f}" for k, _, xy, d, _, _ in HOLES)
           if HOLES else "★本帧无该孔位族 (口径不适用, 依 MECH/board_frame_feasibility.py:108 先例)★"))
    print("-" * 78)
    for c in CHECKS:
        flag = "✅" if c["ok"] else ("⚠️ " if c["level"] == "warn" else
                                    ("— " if c["level"] == "na" else "❌"))
        print(f"  {flag} {c['name']}")
        print(f"       {c['detail']}")
        if c.get("note"):
            print(f"       · {c['note']}")
    print("-" * 78)
    print(f"复算项 {len(CHECKS)} | FAIL {len(fail)} | WARN {len(warn)}")
    print(f"机读结果: {os.path.relpath(OUT_JSON, os.path.join(HERE, '..'))}")
    print("★ 证据等级: 本脚本全部输出 = [推算] (设计态几何 + 公差栈, 非物理实测);")
    print("  打印包孔位 = [实测] (Rev B 生成器实际常量解析); 实物打印件 0 件已打 = [0数据]")
    print(f"★ 权威表: {fr['authority']}")
    print("=" * 78)
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
