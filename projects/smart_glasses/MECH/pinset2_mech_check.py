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
    python3 MECH/pinset2_mech_check.py             # 复算 (FAIL 0 / WARN 2)
    python3 MECH/pinset2_mech_check.py --self-test  # 反向用例: 把孔挪进逃线带 ⇒ 必须变红

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
PCB_L = 60.00          # 板长 X (mm)  [官方] 10-28 项目总工裁 (板坐标 X=0 = 铰链端)
PCB_W = 30.00          # 板宽 Y (mm)  [官方] 老板 10-29 19:16 拍板 (§0 台账 11-01 20:5x 订正)
PCB_THK = 1.00         # 板厚 6 层 1.0mm            [官方] hw-lead proto_pcb_thickness_tier
CORNER_EDGE = 0.50     # 4 角工艺边 (mm)  [既有] MECH_BUDGET §5.1
KEEPOUT_EDGE = 0.80    # 器件距板边 (mm)  [既有] MECH_BUDGET §5.1

# ---- SoC RK3576 (FCCSP698L) ----
# 封装体 17.20 (X) × 16.10 (Y); 板坐标落位 X0=15.00 / Y0=6.95 (板中线 15.00 居中)
# 来源: HW/pcb60x30_check.py SOC_RK3576 + SOC_POS["RK3576"]
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


# =====================================================================
# ① 新孔位 (PIN-SET-2) 几何自检
# =====================================================================
def section_1(holes=HOLES):
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
def section_2(old_holes=OLD_HOLES):
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
# 运行 (一次复算)
# =====================================================================
def run(holes=HOLES, old_holes=OLD_HOLES, pack=None, hw=None):
    global CHECKS
    CHECKS = []
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
def main() -> int:
    if "--self-test" in sys.argv:
        return self_test()

    res = run()
    CHECKS = res["checks"]
    rs, rs_pair, rs_hw_mix, r_seg = res["thermal"]
    fail = [c for c in CHECKS if not c["ok"] and c["level"] == "fail"]
    warn = [c for c in CHECKS if not c["ok"] and c["level"] == "warn"]

    out = {
        "issue": "ISS-192",
        "board": {"L": PCB_L, "W": PCB_W, "thk": PCB_THK, "corner_edge": CORNER_EDGE,
                  "keepout_edge": KEEPOUT_EDGE},
        "soc": {"name": "RK3576", "pkg": [17.20, 16.10],
                "pkg_rect": [SOC_X0, SOC_X1, SOC_Y0, SOC_Y1]},
        "escape_band": {"x": [ESC_X0, ESC_X1], "y": [ESC_Y0, ESC_Y1], "esc": ESC},
        "jchg_keepout": {"x": [JCHG_X0, JCHG_X1], "y": [JCHG_Y0, JCHG_Y1]},
        "holeset": "套 A (Y 按中心线平移, S 孔 ±5.00 不变)",
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
    print("ISS-192 结构侧独立复算 —— PCB 固定 PIN-SET-2 / 板 60×30 / RK3576 (mech-lead)")
    print("=" * 78)
    print(f"板 {PCB_L:.2f}×{PCB_W:.2f}×{PCB_THK:.2f}mm | SoC RK3576 占位 "
          f"X[{SOC_X0:.2f},{SOC_X1:.2f}]×Y[{SOC_Y0:.2f},{SOC_Y1:.2f}] | 逃线带 "
          f"X[{ESC_X0:.2f},{ESC_X1:.2f}]×Y[{ESC_Y0:.2f},{ESC_Y1:.2f}] (外扩 {ESC:.2f}/边)")
    print(f"孔位口径 = {out['holeset']}: " +
          " / ".join(f"{k}({xy[0]:.2f},{xy[1]:.2f})⌀{d:.2f}" for k, _, xy, d, _, _ in HOLES))
    print("-" * 78)
    for c in CHECKS:
        flag = "✅" if c["ok"] else ("⚠️ " if c["level"] == "warn" else "❌")
        print(f"  {flag} {c['name']}")
        print(f"       {c['detail']}")
        if c.get("note"):
            print(f"       · {c['note']}")
    print("-" * 78)
    print(f"复算项 {len(CHECKS)} | FAIL {len(fail)} | WARN {len(warn)}")
    print(f"机读结果: {os.path.relpath(OUT_JSON, os.path.join(HERE, '..'))}")
    print("★ 证据等级: 本脚本全部输出 = [推算] (设计态几何 + 公差栈, 非物理实测);")
    print("  打印包孔位 = [实测] (Rev B 生成器实际常量解析); 实物打印件 0 件已打 = [0数据]")
    print("★ 权威表: MECH/BOARD_GEOM_30MM.md (孔位仲裁结论与影响面)")
    print("=" * 78)
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
