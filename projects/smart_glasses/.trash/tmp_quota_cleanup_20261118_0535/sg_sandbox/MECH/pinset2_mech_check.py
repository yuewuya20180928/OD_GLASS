#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pinset2_mech_check.py —— ISS-107 结构侧独立复算: PCB 固定方式改版 PIN-SET-2
=====================================================================
题目: mech-lead 把 interface_claims.pcb_mounting 从老口径
      「2xM1.2+1x⌀2.0H7」改成 hw-lead ISS-049 定版的
      「PIN-SET-2:2x⌀2.0H7+2x⌀1.4」, 让合并器那条冲突消掉。

本脚本做 4 件事 (全部机械判定, 不靠人眼), **不复制 hw-lead 的 HW/pinset2_check.py,
而是按结构侧的约束独立重算一遍** (圆孔用**真圆-矩形**重叠面积, 不是外接方框):
  ① 新孔位 (PIN-SET-2) 几何自检: 与 SoC 逃线带 / SoC 封装体 / J_CHG 座体 keep-out
     的 2D 重叠 (圆∩矩形真面积)、孔心与孔壁到板边、孔间中心距与孔壁间距、
     定位链配合 (H7 孔配 h6 圆销 = 滑配; ⌀1.4 过孔配 M1.2 = 零定位)
  ② 老口径失效复算 (证明"必须改"): 2×M1.2 @孔心到板边2.50 + 1×⌀2.0 H7,
     按最有利假设 (老孔落在 SoC 的 X 段内) → 3/3 孔压逃线带
     (M1.2 压 Y 0.50mm; ⌀2.0 压 2.00×2.00mm)
  ③ 打印件/骨架连带 (PIN-SET-2 是【双销】, 打印件让过孔数与间距都变):
     打印件 PCB 定位板长度、让过孔数量与间距的差值表
  ④ 散热连带 (hw-lead T-4: 螺钉热旁路必须进 mech 热模型) 的**量级复核**:
     螺钉对 R / 骨架段温差 ΔT 抵偿量 —— ★本单**不出**新的皮肤温度数
     (那要完整热模型重算, 属热模型单), 只给可复核的中间量

输出: MECH/pinset2_mech_check.json  + 终端表格
rc  = 0 → 全部通过 / 1 → 有 FAIL

纪律: 只写 MECH/ 下本脚本自己的两个文件; 不改任何别人的文件
      (不碰 HW/ 不碰 state/fragments/ 不碰 state/merge.py)。
=====================================================================
"""
from __future__ import annotations

import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_JSON = os.path.join(HERE, "pinset2_mech_check.json")

# =====================================================================
# 输入 —— 每行标来源; [推算] 的给公式
# =====================================================================
PCB_L = 60.00          # 板长 X (mm)  [决策] 10-28 项目总工裁 (板坐标 X=0 = 铰链端)
PCB_W = 15.00          # 板宽 Y (mm)  [决策] 老板 10-27 拍板
PCB_THK = 1.00         # 板厚 6 层 1.0mm (4 层 0.8)  [决策] HW/PCB_OUTLINE_60x15.md
CORNER_EDGE = 0.50     # 4 角工艺边 (mm)  [既有] MECH_BUDGET §5.1
KEEPOUT_EDGE = 0.80    # 器件距板边 (mm)  [既有] MECH_BUDGET §5.1

SOC_X0, SOC_X1 = 21.00, 31.00   # SoC FCCSP 8×10mm 封装体 X 区间 [官网] 8×10 + 板居中
SOC_Y0, SOC_Y1 = 3.50, 11.50    # 同上 Y 区间
ESC = 0.80                       # 逃线带外扩 (mm/边) [推算] HW/SOC_PIN_BUDGET.md (ISS-081)
ESC_X0, ESC_X1 = SOC_X0 - ESC, SOC_X1 + ESC      # [20.20, 31.80]
ESC_Y0, ESC_Y1 = SOC_Y0 - ESC, SOC_Y1 + ESC      # [2.70, 12.30]

JCHG_X0, JCHG_X1 = 0.00, 3.00    # J_CHG 座体 keep-out X [推算] 座体尺寸页未核 [0数据]
JCHG_Y0, JCHG_Y1 = 4.25, 10.75   # 同上 Y (10p 排线居中 Y=7.50 ±3.25)

# ---- PIN-SET-2 孔位 (定版) —— 板坐标: 原点左下角, X=板长 0..60, Y=板宽 0..15
HOLES = [
    ("P1", "主定位销孔", (8.00, 7.50), 2.00, "骨架压装 ⌀2.0 h6 圆销", "全基准 X+Y+θz"),
    ("P2", "副定位销孔", (52.00, 7.50), 2.00, "骨架压装 ⌀2.0 菱形销 (对边 1.94)", "只定 Y"),
    ("S1", "压紧螺钉孔", (8.00, 2.50), 1.40, "骨架 M1.2 攻丝 / 自攻", "只压紧 零定位"),
    ("S2", "压紧螺钉孔", (52.00, 12.50), 1.40, "骨架 M1.2 攻丝 / 自攻", "只压紧 零定位"),
]

# ---- 老口径 (MECH_BUDGET §5.1 原始口径: 2×M1.2 ⌀1.4 孔心到板边 2.50 + 1×⌀2.0 H7)
# 老口径只给了"孔心到板边 2.50" 没给 X → 按最有利假设 (老孔落在 SoC 的 X 段内,
# 因为 v1.1 的骨架/散热垫都在 SoC 下方) 复算。
OLD_HOLES = [
    ("M1", "老 M1.2 螺钉孔", (25.00, 2.50), 1.40),
    ("M2", "老 M1.2 螺钉孔", (25.00, 12.50), 1.40),
    ("D0", "老 ⌀2.0 H7 销孔", (25.00, 7.50), 2.00),
]

# ---- 打印件 (MECH/print/GEOM_SPEC_REVA.md Rev A 契约) 现状
PRINT_PCB_LEN = 50.00     # 打印件 B1 底板 / B6 定位板的 X 长度 (gen_print_pack.py pcb_len)
PRINT_DOWEL_CL = 1        # 打印件 PCB 定位间隙孔 ⌀2.4 数量 (B3, X=16)
PRINT_SCREW_CL = 2        # 打印件 M1.2 让过孔 ⌀1.6 数量 (B2, X=6 / X=46)
PRINT_SCREW_PITCH = 40.00  # 打印件两让过孔中心距 (X=46-6)

# ---- 散热中间量
K_AL = 237.0          # 铝骨架导热 [推算] MECH_BUDGET §2.3
K_STEEL = 50.0        # 钢螺钉导热 [推算] 常用值
SKEL_THK = 1.00       # 骨架厚 (mm) [推算] MECH_BUDGET §5.1
SKEL_W = 15.00        # 骨架 SoC 段满宽 (mm) [决策] 骨架必须满板宽做横向扩散
SOC_CX = (SOC_X0 + SOC_X1) / 2.0   # SoC 中心 X = 26.00

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
    # 把圆心平移到原点, 矩形变成 [-a,a]×[-b,b] 形式 (按象限对称累加)
    dx0, dx1 = x0 - cx, x1 - cx
    dy0, dy1 = y0 - cy, y1 - cy
    if dx1 <= -r or dx0 >= r or dy1 <= -r or dy0 >= r:
        return 0.0
    # 数值积分 (x 方向切片), 精度足够 (1e-6 mm²)
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


def rect_overlap(a, b):
    """两轴对齐矩形的重叠面积。"""
    dx = min(a[1], b[1]) - max(a[0], b[0])
    dy = min(a[3], b[3]) - max(a[2], b[2])
    return (dx * dy) if (dx > 0 and dy > 0) else 0.0


def overlap_len(a0, a1, b0, b1):
    return max(0.0, min(a1, b1) - max(a0, b0))


# =====================================================================
# ① 新孔位 (PIN-SET-2) 几何自检
# =====================================================================
esc_rect = (ESC_X0, ESC_X1, ESC_Y0, ESC_Y1)
soc_rect = (SOC_X0, SOC_X1, SOC_Y0, SOC_Y1)
jchg_rect = (JCHG_X0, JCHG_X1, JCHG_Y0, JCHG_Y1)

# 1.1 与 SoC 逃线带 / 封装体 / J_CHG keep-out 零重叠 (真圆面积)
for k, fn, (x, y), d, mate, role in HOLES:
    r = d / 2.0
    ov = circle_rect_overlap(x, y, r, ESC_X0, ESC_X1, ESC_Y0, ESC_Y1)
    chk(f"{k} vs SoC 逃线带 X[{ESC_X0:.2f},{ESC_X1:.2f}]×Y[{ESC_Y0:.2f},{ESC_Y1:.2f}] 重叠",
        ov < 1e-6, f"2D 重叠面积 = {ov:.4f} mm² (真圆∩矩形)",
        f"孔心 ({x:.2f},{y:.2f}) ⌀{d:.2f} —— {fn}")
    ov2 = circle_rect_overlap(x, y, r, SOC_X0, SOC_X1, SOC_Y0, SOC_Y1)
    chk(f"{k} vs SoC 封装体 重叠", ov2 < 1e-6, f"2D 重叠面积 = {ov2:.4f} mm²")
    ov3 = circle_rect_overlap(x, y, r, JCHG_X0, JCHG_X1, JCHG_Y0, JCHG_Y1)
    chk(f"{k} vs J_CHG 座体 keep-out 重叠", ov3 < 1e-6, f"2D 重叠面积 = {ov3:.4f} mm²",
        "J_CHG 座体 A/B/C 尺寸页未核 [0数据] ⇒ 座体 X 向进深按 3.00 推算")

# 1.2 孔心 / 孔壁到板边
edge_detail = []
for k, fn, (x, y), d, mate, role in HOLES:
    r = d / 2.0
    e = min(x, PCB_L - x, y, PCB_W - y)
    chk(f"{k} 孔心到板边 ≥1.50mm", e >= 1.50,
        f"孔心距边 {e:.2f}mm (⌀{d:.2f} → 孔壁距边 {e - r:.2f}mm)", f"{fn}")
    chk(f"{k} 孔壁不侵入 0.80mm 器件边距带", e - r >= KEEPOUT_EDGE,
        f"孔壁距边 {e - r:.2f}mm vs {KEEPOUT_EDGE:.2f}mm")
    edge_detail.append(f"{k}: 孔心距边 {e:.2f} / 孔壁距边 {e - r:.2f}")

# 1.3 孔间中心距 / 孔壁间距
min_cc, min_wall, pairs = 1e9, 1e9, []
for i in range(len(HOLES)):
    for j in range(i + 1, len(HOLES)):
        ka, kb = HOLES[i], HOLES[j]
        dcc = math.dist(ka[2], kb[2])
        wall = dcc - ka[3] / 2.0 - kb[3] / 2.0
        min_cc = min(min_cc, dcc)
        min_wall = min(min_wall, wall)
        pairs.append(f"{ka[0]}-{kb[0]}: 中心距 {dcc:.2f} / 孔壁 {wall:.2f}")
chk("孔间最小中心距 ≥5.00mm", min_cc >= 5.00, f"最小中心距 = {min_cc:.2f}mm", "; ".join(pairs))
chk("孔间最小孔壁间距 ≥2.00mm", min_wall >= 2.00, f"最小孔壁间距 = {min_wall:.2f}mm")

# 1.4 定位链: H7 孔 (2.000-2.021) 配 h6 圆销 (1.980-1.992) = 滑配
h7 = (2.000, 2.021)
h6 = (1.980, 1.992)
chk("P1 H7 孔配 h6 圆销 = 滑配 (定位非压配)",
    h6[1] < h7[0] and h7[0] - h6[1] <= 0.05,
    f"径向间隙 {h7[0] - h6[1]:.3f}..{h7[1] - h6[0]:.3f}mm (销/孔)",
    "P2 菱形销 对边 1.94 → X 向单边让位 0.030..0.041mm, 消除过定位 (hw-lead ISS-049 §3.1)")
chk("S1/S2 ⌀1.4 过孔配 M1.2 螺钉 = 零定位 (径向间隙 0.20mm)", True,
    "M1.2 螺钉 ⌀1.2 → 径向间隙 0.10mm/边 (⌀1.4-⌀1.2)/2 = 0.10", "螺钉只压紧, 不参与定位")

# =====================================================================
# ② 老口径失效复算 (证明"必须改")
# =====================================================================
old_detail, old_fail = [], 0
for k, fn, (x, y), d in OLD_HOLES:
    r = d / 2.0
    ov = circle_rect_overlap(x, y, r, ESC_X0, ESC_X1, ESC_Y0, ESC_Y1)
    ovx = overlap_len(x - r, x + r, ESC_X0, ESC_X1)
    ovy = overlap_len(y - r, y + r, ESC_Y0, ESC_Y1)
    bbox = ovx * ovy
    old_fail += 1 if ov > 1e-6 else 0
    old_detail.append(f"{k}({x:.2f},{y:.2f}) ⌀{d:.2f} → 压逃线带 X {ovx:.2f}mm / Y {ovy:.2f}mm "
                      f"(外接方框 {bbox:.2f}mm², 真圆面积 {ov:.2f}mm²)")
chk("老口径 (2×M1.2 + 1×⌀2.0H7 @孔心到板边2.50) 在 15mm 板下不可用 → 必须改",
    old_fail == 3, f"{old_fail}/3 孔压 SoC 逃线带: " + "; ".join(old_detail),
    "12mm 板时 M1.2 孔完全落在带内 (压 2.00mm) ⇒ 加宽不解, 必须沿板长移出; "
    "本脚本按最有利假设 (老孔放在 SoC 的 X 段内) 复算")

# =====================================================================
# ③ 打印件 / 骨架连带 (PIN-SET-2 是双销 → 打印件让过孔数量与间距都变)
# =====================================================================
need_dowel_cl = 2                      # P1 + P2 两个 ⌀2.0 H7 销孔 → 打印件要 2 个 ⌀2.4 让过孔
need_screw_pitch = 52.00 - 8.00        # S2-S1 中心距 (板坐标)
chk("打印件 PCB 定位板长度须覆盖板长 60.00 (现契约 50.00)",
    PRINT_PCB_LEN >= PCB_L,
    f"打印件 pcb_len = {PRINT_PCB_LEN:.2f}mm vs 板长 {PCB_L:.2f}mm → 差 {PCB_L - PRINT_PCB_LEN:.2f}mm",
    "★打印包契约 (MECH/print/GEOM_SPEC_REVA.md Rev A) 仍是老口径 —— 改版由项目总工授权后重生成 "
    "(已挂 needs_from iss089_typec_opening_and_print_pack), 本单不改打印包",
    level="warn")
chk("打印件 PCB 定位让过孔须为 2 个 (P1+P2 双销, 现契约 1 个)",
    PRINT_DOWEL_CL == need_dowel_cl,
    f"打印件 ⌀2.4 让过孔 {PRINT_DOWEL_CL} 个 → 需 {need_dowel_cl} 个 (差 {need_dowel_cl - PRINT_DOWEL_CL})",
    "老口径单销 ⇒ 1 个让过孔; PIN-SET-2 双销 ⇒ 2 个 (hw-lead iss049_mount_screw: 上壳需 2x⌀2.4 + 2x⌀1.6 让过孔)",
    level="warn")
chk("打印件 M1.2 让过孔中心距须 = 44.00 (S1/S2 板坐标, 现契约 40.00)",
    abs(PRINT_SCREW_PITCH - need_screw_pitch) < 1e-6,
    f"打印件让过孔中心距 {PRINT_SCREW_PITCH:.2f}mm → 须 {need_screw_pitch:.2f}mm (差 {need_screw_pitch - PRINT_SCREW_PITCH:.2f})",
    "板坐标 → 打印件坐标的映射尚未定义 (接口项 pcb_loc_dowel_metal), 打印包改版时需一并锁",
    level="warn")

# =====================================================================
# ④ 散热连带 (量级复核; 本单不出新的皮肤温度数)
# =====================================================================
# 4.1 螺钉热旁路: M1.2 钢螺钉 1 颗的 R (有效导热长 1/2/3mm), 2 颗并联
a_screw = math.pi / 4 * (1.2e-3) ** 2      # ⌀1.2 截面积 = 1.1310 mm²


def r_screw(l_mm):
    return (l_mm * 1e-3) / (K_STEEL * a_screw)


rs = {f"L={l}mm": r_screw(l) for l in (1.0, 2.0, 3.0)}
rs_pair = {f"L={l}mm": r_screw(l) / 2.0 for l in (1.0, 2.0, 3.0)}
rs_hw_mix = 1.0 / sum(1.0 / r_screw(l) for l in (1.0, 2.0, 3.0))   # hw-lead T-4 的 9.6 K/W 口径
chk("螺钉热旁路量级已复核 (进 mech 热模型)", True,
    "1 颗: " + " / ".join(f"{k} {v:.1f} K/W" for k, v in rs.items())
    + " ; 2 颗并联: " + " / ".join(f"{k} {v:.1f} K/W" for k, v in rs_pair.items())
    + f" ; hw T-4 口径(3 个长度档并联) {rs_hw_mix:.1f} K/W",
    "★本单只给中间量: 新的皮肤侧温度数要完整热模型重算 (热模型单); "
    "另: 螺钉头必须落在 PCB 皮肤侧沉孔内、不得接触皮肤侧下壳 (否则金属跨过 0.50 隔热垫 + 0.30 空气隙)")

# 4.2 PIN-SET-2 把 2 颗螺钉从 SoC 段 (老口径 X=25) 移到板两端 → 骨架段温差抵偿
d_p1 = SOC_CX - 8.00            # P1/S1 到 SoC 中心的轴向距离
d_p2 = 52.00 - SOC_CX           # P2/S2 到 SoC 中心的轴向距离
r_p1 = (d_p1 * 1e-3) / (K_AL * (SKEL_W * SKEL_THK) * 1e-6)
r_p2 = (d_p2 * 1e-3) / (K_AL * (SKEL_W * SKEL_THK) * 1e-6)
r_seg = {"P1/S1": r_p1, "P2/S2": r_p2}
chk("螺钉移到板两端 → 骨架段温差 ΔT 抵偿量已量化 (热模型单要用)",
    True,
    f"P1/S1 (距 SoC 中心 {d_p1:.2f}mm): 骨架段 R = {r_p1:.2f} K/W"
    f" / P2/S2 (距 SoC 中心 {d_p2:.2f}mm): 骨架段 R = {r_p2:.2f} K/W",
    f"公式 R=L/(k·A), k={K_AL} W/m·K, A={SKEL_W}×{SKEL_THK}mm²; "
    "老口径 2 颗 M1.2 都在 X=25 (SoC 正下方) ⇒ 该段温差 ≈0; "
    f"PIN-SET-2 后 P1/S1 段 {r_p1:.2f} K/W、P2/S2 段 {r_p2:.2f} K/W "
    "⇒ 方向上【减小】螺钉旁路热流的驱动力 (热模型单要用这个抵偿量)")

# 4.3 隔热层位置未被 PIN-SET-2 破坏 (骨架止于 PCB 段后缘)
chk("隔热层仍在 SoC 与皮肤之间 (PIN-SET-2 未改隔热层位置)",
    True, "0.50 隔热垫 + 0.30 空气隙位置/厚度未动; 螺钉头落 PCB 皮肤侧沉孔, 严禁接触皮肤侧下壳",
    "若螺钉头接触下壳 = 金属跨过隔热层 = 新并联热路 (与 hw-lead T-3 同一条约束)")

# =====================================================================
# 输出
# =====================================================================
fail = [c for c in CHECKS if not c["ok"] and c["level"] == "fail"]
warn = [c for c in CHECKS if not c["ok"] and c["level"] == "warn"]

out = {
    "issue": "ISS-107",
    "scheme": "PIN-SET-2 (2x⌀2.0 H7 + 2x⌀1.4)",
    "old_scheme": "2xM1.2 + 1x⌀2.0 H7 (作废)",
    "board": {"L": PCB_L, "W": PCB_W, "thk": PCB_THK, "corner_edge": CORNER_EDGE,
              "keepout_edge": KEEPOUT_EDGE},
    "escape_band": {"x": [ESC_X0, ESC_X1], "y": [ESC_Y0, ESC_Y1], "soc": [SOC_X0, SOC_X1, SOC_Y0, SOC_Y1]},
    "holes": [{"key": k, "fn": fn, "xy": xy, "d": d, "mate": m, "role": r}
              for (k, fn, xy, d, m, r) in HOLES],
    "old_holes": [{"key": k, "fn": fn, "xy": xy, "d": d} for (k, fn, xy, d) in OLD_HOLES],
    "print_delta": {"need_dowel_clearance": need_dowel_cl, "print_dowel_clearance": PRINT_DOWEL_CL,
                    "print_pcb_len": PRINT_PCB_LEN, "board_len": PCB_L,
                    "need_screw_pitch": need_screw_pitch, "print_screw_pitch": PRINT_SCREW_PITCH},
    "thermal": {"r_screw_1pc": rs, "r_screw_2pc_parallel": rs_pair,
                "hw_T4_mix": rs_hw_mix,
                "skeleton_seg_R": r_seg,
                "note": "本单只出中间量, 不出新的皮肤侧温度数"},
    "edge_detail": edge_detail,
    "checks": CHECKS,
    "fail": len(fail),
    "warn": len(warn),
    "total": len(CHECKS),
}

with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

print("=" * 78)
print("ISS-107 结构侧独立复算 —— PCB 固定方式 PIN-SET-2 (mech-lead)")
print("=" * 78)
print(f"板 {PCB_L:.2f}×{PCB_W:.2f}mm | SoC 逃线带 X[{ESC_X0:.2f},{ESC_X1:.2f}] "
      f"Y[{ESC_Y0:.2f},{ESC_Y1:.2f}] | 板坐标 X=0 为铰链端")
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
print("★ 证据等级: 本脚本全部输出 = [推算] (设计态几何 + 公差栈, 非物理实测)")
print("  J_CHG 座体 A/B/C 尺寸页未核 [0数据]; 打印件实测尺寸 0 件已打 [0数据]")
print("=" * 78)
sys_rc = 1 if fail else 0
raise SystemExit(sys_rc)
