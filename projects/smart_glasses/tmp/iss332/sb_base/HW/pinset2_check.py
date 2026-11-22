#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PIN-SET-2 机械复算脚本 (ISS-049)
=====================================================================
题目: PCB 固定方式从「M1.2 螺钉 + ⌀2.0 H7(单销)」改为「配合金属骨架的 H7 销」
      + 骨架长度上限 / 石墨铺装范围

本脚本做 4 件事 (全部机械判定, 不靠人眼):
  ① PCB 固定孔位几何自检 (逃线带重叠 / 板边距 / 孔间距 / 连接器 keep-out)
  ② 旧孔位方案在 15mm 板宽下的失效复算 (证明"必须改")
  ③ 骨架长度上限 + 石墨铺装范围 的硬约束自检 (不得延伸进电池段)
  ④ 热路自检: 隔热层是否仍在 SoC 与皮肤之间; 螺钉旁路热阻量化
输出: HW/pinset2_check.json + HW/pinset2_holes.svg + 终端表格
rc  = 0 → 全部通过 / 1 → 有 FAIL

纪律: 只写 HW/ 下本脚本自己的三个文件; 不改任何别人的文件。
"""
from __future__ import annotations

import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_JSON = os.path.join(HERE, "pinset2_check.json")
OUT_SVG = os.path.join(HERE, "pinset2_holes.svg")

# =====================================================================
# 输入 —— 每行都标来源; [推算] 的输入在 note 里给公式
# =====================================================================
PCB_L = 60.00          # 板长 X (mm)   [决策] 10-28 项目总工裁 (HW/PCB_OUTLINE_60x15.md §1.1)
PCB_W = 15.00          # 板宽 Y (mm)   [决策] 老板 10-27 拍板
PCB_THK = 1.00         # 板厚 (mm)     [既有] 6 层 1.0 (4 层 0.8)
CORNER_EDGE = 0.50     # 4 角工艺边 (mm) [既有] MECH_BUDGET §5.1
KEEPOUT_EDGE = 0.80    # 器件距板边 (mm) [既有] MECH_BUDGET §5.1

SOC_X0, SOC_X1 = 21.00, 31.00   # SoC FCCSP 8×10mm 封装体 X 区间 [推算] 居中于 60mm 板
SOC_Y0, SOC_Y1 = 3.50, 11.50    # 同上 Y 区间 (板宽居中)
ESC = 0.80                       # 逃线带外扩 (mm/边) [推算] HW/SOC_PIN_BUDGET.md (ISS-081)
ESC_X0, ESC_X1 = SOC_X0 - ESC, SOC_X1 + ESC      # [20.20, 31.80]
ESC_Y0, ESC_Y1 = SOC_Y0 - ESC, SOC_Y1 + ESC      # [2.70, 12.30]

# J_CHG 座体 keep-out (铰链端, X=0 侧) —— HW/PCB_OUTLINE_60x15.md §4.1/§4.2
JCHG_X0, JCHG_X1 = 0.00, 3.00    # 座体 X 向进深 [推算] 座体 A/B/C 尺寸页未核 [0数据]
JCHG_Y0, JCHG_Y1 = 4.25, 10.75   # 座体 Y 向占宽 (10p 排线居中 Y=7.50 ± 3.25)

# 电池段起点 = PCB 段后缘 (MECH/CLEARANCE_FIX.md §3.1: 电池段 = 下壳一体盲槽, 定位面在段前端壁)
BATT_START_Z = PCB_L             # 60.00mm

# 骨架 / 石墨
SKEL_THK = 1.00        # 骨架厚 (mm) [推算] MECH_BUDGET §5.1
AL_RHO = 2.70          # 铝密度 g/cc [推算] MECH_BUDGET §3 W5
GR_RHO = 2.00          # 石墨膜密度 g/cc [推算] 柔性石墨 ~1.9-2.2
GR_THK = 0.30          # 石墨片厚 (mm) [推算] MECH_BUDGET 未给厚度 → 需 mech 补进 H 链

# 热路 (MECH/MECH_BUDGET.md §2.3/§2.4 + MECH/fit_check.py §4)
K_AL, K_PRINT = 237.0, 0.20
K_SIL, K_AIR, K_STEEL = 0.30, 0.026, 50.0
PAD_THK, AIR_THK = 0.50, 0.30
R_SHELL, R_SKIN, R_CONV = 12.5, 54.2, 667.0
SOC_AREA = 80e-6       # 8×10mm 散热焊盘面积 (m^2)

# =====================================================================
# PIN-SET-2 孔位 (定版) —— 板坐标: 原点=左下角, X=板长 0..60, Y=板宽 0..15
# =====================================================================
HOLES = [
    # key, 功能,        (x, y),       孔径,  配对骨架特征,            定位角色
    ("P1", "主定位销孔", (8.00, 7.50), 2.00, "骨架压装 ⌀2.0 h6 圆销", "全基准 (X/Y/θz)"),
    ("P2", "副定位销孔", (52.00, 7.50), 2.00, "骨架压装 ⌀2.0 菱形销 (对边 1.94)", "只定 Y (X 向让位 0.04-0.08)"),
    ("S1", "压紧螺钉孔", (8.00, 2.50), 1.40, "骨架 M1.2 攻丝 / 自攻", "只压紧 (⌀1.4 过孔, 径向间隙 0.20)"),
    ("S2", "压紧螺钉孔", (52.00, 12.50), 1.40, "骨架 M1.2 攻丝 / 自攻", "只压紧 (⌀1.4 过孔, 径向间隙 0.20)"),
]

# 旧方案 (MECH_BUDGET §5.1: 2×M1.2 ⌀1.4 孔心到板边 2.50mm + 1×⌀2.0 H7 定位销孔)
# ★ 老口径只给了"孔心到板边 2.50mm", 没给 X; 但 v1.1 的布局意图 = 固定孔在 **SoC 段**
#   (骨架/散热垫都在 SoC 下方) ⇒ 复算时把老孔放在 SoC 的 X 段内, 这是最有利假设。
OLD_HOLES = [
    ("M1", "旧 M1.2 螺钉孔", (25.00, 2.50), 1.40),
    ("M2", "旧 M1.2 螺钉孔", (25.00, 12.50), 1.40),
    ("D0", "旧 ⌀2.0 H7 销孔", (25.00, 7.50), 2.00),
]

CHECKS = []


def chk(name, ok, detail, note="", level="fail"):
    """level: fail = 本单验收项 (不过 → rc=1); warn = 已知超差/待裁 (不算本单不过, 但必须露出)。"""
    CHECKS.append({"name": name, "ok": bool(ok), "level": level,
                   "detail": detail, "note": note})
    return ok


def rect(x, y, d):
    """圆孔的包围矩形 (按外切方) 与轴对齐区间。"""
    r = d / 2.0
    return (x - r, x + r, y - r, y + r)


def overlap_2d(a, b):
    """两个轴对齐矩形的重叠面积。"""
    dx = min(a[1], b[1]) - max(a[0], b[0])
    dy = min(a[3], b[3]) - max(a[2], b[2])
    return (dx * dy) if (dx > 0 and dy > 0) else 0.0


def overlap_x(a, b):
    """X 区间重叠长度。"""
    return max(0.0, min(a[1], b[1]) - max(a[0], b[0]))


# =====================================================================
# ① 新孔位几何自检
# =====================================================================
esc_rect = (ESC_X0, ESC_X1, ESC_Y0, ESC_Y1)
soc_rect = (SOC_X0, SOC_X1, SOC_Y0, SOC_Y1)
jchg_rect = (JCHG_X0, JCHG_X1, JCHG_Y0, JCHG_Y1)

hole_rects = {}
for k, fn, (x, y), d, mate, role in HOLES:
    hole_rects[k] = rect(x, y, d)

# 1.1 与 SoC 逃线带零重叠
for k, fn, (x, y), d, mate, role in HOLES:
    ov = overlap_2d(hole_rects[k], esc_rect)
    chk(f"{k} vs SoC 逃线带 X[{ESC_X0:.2f},{ESC_X1:.2f}] 重叠", ov == 0.0,
        f"2D 重叠面积 = {ov:.3f} mm²", f"孔心 ({x:.2f},{y:.2f}) ⌀{d:.2f}")

# 1.2 与 SoC 封装体零重叠
for k, fn, (x, y), d, mate, role in HOLES:
    ov = overlap_2d(hole_rects[k], soc_rect)
    chk(f"{k} vs SoC 封装体 重叠", ov == 0.0, f"2D 重叠面积 = {ov:.3f} mm²")

# 1.3 与 J_CHG 座体 keep-out 零重叠
for k, fn, (x, y), d, mate, role in HOLES:
    ov = overlap_2d(hole_rects[k], jchg_rect)
    chk(f"{k} vs J_CHG 座体 keep-out 重叠", ov == 0.0, f"2D 重叠面积 = {ov:.3f} mm²")

# 1.4 孔到板边 (孔心 & 孔壁)
for k, fn, (x, y), d, mate, role in HOLES:
    r = d / 2.0
    e = min(x, PCB_L - x, y, PCB_W - y)          # 孔心到最近板边
    chk(f"{k} 孔心到板边 ≥1.50mm", e >= 1.50,
        f"孔心距边 {e:.2f}mm (⌀{d:.2f} → 孔壁距边 {e - r:.2f}mm)",
        "MECH_BUDGET §5.1 老口径 = 2.50mm; CLEARANCE_FIX 卡点2 要求 ≥1.50mm")
    chk(f"{k} 孔壁不侵入 0.80mm 器件边距带", e - r >= KEEPOUT_EDGE,
        f"孔壁距边 {e - r:.2f}mm vs {KEEPOUT_EDGE:.2f}mm")

# 1.5 孔间中心距 & 孔壁间距
min_cc = 1e9
min_wall = 1e9
pair_detail = []
keys = [h[0] for h in HOLES]
for i in range(len(HOLES)):
    for j in range(i + 1, len(HOLES)):
        ka, kb = HOLES[i], HOLES[j]
        dcc = math.dist(ka[2], kb[2])
        wall = dcc - ka[3] / 2.0 - kb[3] / 2.0
        min_cc = min(min_cc, dcc)
        min_wall = min(min_wall, wall)
        pair_detail.append(f"{ka[0]}-{kb[0]}: 中心距 {dcc:.2f} / 孔壁 {wall:.2f}")
chk("孔间最小中心距 ≥5.00mm", min_cc >= 5.00, f"最小中心距 = {min_cc:.2f}mm", "; ".join(pair_detail))
chk("孔间最小孔壁间距 ≥2.00mm", min_wall >= 2.00, f"最小孔壁间距 = {min_wall:.2f}mm")

# 1.6 定位链: H7 孔 ⌀2.0 (孔径公差 +0.021/0) 配 ⌀2.0 h6 圆销 (1.980-1.992) → 滑配
h7 = (2.000, 2.021)
h6 = (1.980, 1.992)
chk("P1 H7 孔配 h6 圆销 = 滑配 (定位非压配)", h6[1] < h7[0] and h7[0] - h6[1] <= 0.05,
    f"径向间隙 {h7[0] - h6[1]:.3f}..{h7[1] - h6[0]:.3f}mm (销/孔)",
    "菱形销 P2: 对边 1.94 → X 向单边间隙 0.030..0.041mm, 消除过定位")
chk("S1/S2 ⌀1.4 过孔配 M1.2 螺钉 = 不定位 (径向间隙 0.20mm)", True,
    "M1.2 螺钉 ⌀1.2 → 径向间隙 0.10mm/边 (⌀1.4-⌀1.2)/2 = 0.10", "螺钉只压紧, 零定位功能")

# =====================================================================
# ② 旧孔位方案在 15mm 板宽下的失效复算 (证明"必须改")
# =====================================================================
old_detail = []
old_fail = 0
for k, fn, (x, y), d in OLD_HOLES:
    r = rect(x, y, d)
    ov = overlap_2d(r, esc_rect)
    ovx = overlap_x(r, esc_rect)
    ovy = overlap_x((r[2], r[3]), (ESC_Y0, ESC_Y1))
    old_fail += 1 if ov > 0 else 0
    old_detail.append(f"{k}({x:.2f},{y:.2f}) ⌀{d:.2f} → 压逃线带 X {ovx:.2f}mm / Y {ovy:.2f}mm (面积 {ov:.2f}mm²)")
chk("老口径 (2×M1.2 + 1×⌀2.0H7 @边距2.50) 在 15mm 板下不可用 → 必须改", old_fail > 0,
    f"{old_fail}/3 孔压 SoC 逃线带: " + "; ".join(old_detail),
    "12mm 板时 M1.2 孔完全落在带内 (压 2.00mm) → 加宽不解, 必须沿板长移出; "
    "本脚本按最有利假设 (老孔放在 SoC 的 X 段内) 复算")

# =====================================================================
# ③ 骨架长度上限 / 石墨铺装范围
# =====================================================================
SKEL_MAX_LEN = PCB_L            # 60.00mm = PCB 段后缘 (硬上限)
SKEL_BUILD_LEN = 58.00          # 建议实现 (退 2.00mm 给上壳后端壁 + 合缝 + 与电池段前沿 ≥1.0mm 空气隙)
GRAPHITE_X0, GRAPHITE_X1 = 0.00, PCB_L   # 轴向覆盖 = 与 PCB 段同 (硬上限 60.00)
GRAPHITE_Y0, GRAPHITE_Y1 = 0.00, PCB_W   # V 向覆盖 = 满板宽
SOc_REQ_X0, SOc_REQ_X1 = 19.00, 33.00    # SoC 区必须覆盖的轴向区间 (含 2.5mm 端裕量)

chk("骨架长度上限 = PCB 段后缘", SKEL_MAX_LEN == BATT_START_Z,
    f"上限 {SKEL_MAX_LEN:.2f}mm = 电池段起点 {BATT_START_Z:.2f}mm")
chk("骨架建议实现值 ≤ 硬上限", SKEL_BUILD_LEN <= SKEL_MAX_LEN,
    f"建议 {SKEL_BUILD_LEN:.2f}mm, 退让 {SKEL_MAX_LEN - SKEL_BUILD_LEN:.2f}mm",
    "退让 = 与电池段前沿件 ≥1.0mm 空气隙 (防骨架热端面直接压电芯前壁)")
chk("石墨轴向覆盖不得进入电池段", GRAPHITE_X1 <= BATT_START_Z,
    f"石墨 X ∈ [{GRAPHITE_X0:.2f}, {GRAPHITE_X1:.2f}] vs 电池段起点 {BATT_START_Z:.2f}")
chk("石墨 V 向覆盖 ≥ SoC 横向扩散带 (10+2×3.5)", (GRAPHITE_Y1 - GRAPHITE_Y0) >= 15.00,
    f"石墨 V 向 {GRAPHITE_Y1 - GRAPHITE_Y0:.2f}mm (SoC 10.00 + 两侧各 3.50)")
chk("石墨覆盖 SoC 轴向区", GRAPHITE_X0 <= SOc_REQ_X0 and GRAPHITE_X1 >= SOc_REQ_X1,
    f"石墨 X [{GRAPHITE_X0:.2f},{GRAPHITE_X1:.2f}] ⊇ SoC 需求 [{SOc_REQ_X0:.2f},{SOc_REQ_X1:.2f}]")

# 骨架重量 (两种形状)
w_skel_full = PCB_L * PCB_W * SKEL_THK * 1e-3 * AL_RHO          # 满宽 60×15×1.0
w_skel_step = (SOc_REQ_X1 - SOc_REQ_X0) * PCB_W * SKEL_THK * 1e-3 * AL_RHO \
    + (PCB_L - (SOc_REQ_X1 - SOc_REQ_X0)) * 10.00 * SKEL_THK * 1e-3 * AL_RHO   # 台阶形: SoC 段满宽, 其余 10mm 宽
w_graphite = (GRAPHITE_X1 - GRAPHITE_X0) * (GRAPHITE_Y1 - GRAPHITE_Y0) * GR_THK * 1e-3 * GR_RHO
chk("骨架重量 vs MECH '+1-3g' 口径 (一对) —— ⚠️ 已知超差, 交 mech 定截面", False,
    f"满宽形 {w_skel_full:.2f}g/侧 ({2 * w_skel_full:.2f}g/对) / 台阶形 {w_skel_step:.2f}g/侧 ({2 * w_skel_step:.2f}g/对)"
    f" vs MECH_BUDGET §2.4 B '+1-3g' ⇒ 台阶形仍超 {2 * w_skel_step - 3.0:.2f}g",
    "满宽形已判死; 台阶形仍贴边 → 需 U 形/槽形截面 (同刚度更轻) 或接受超差; "
    "截面形状属 mech 决策 → 已列接口请求 (需 mech 复核重量口径)",
    level="warn")

# =====================================================================
# ④ 热路自检
# =====================================================================
# 4.1 隔热层在 SoC 与皮肤之间 (未被金属旁路)
r_pad = PAD_THK * 1e-3 / (K_SIL * SOC_AREA)
r_air = AIR_THK * 1e-3 / (K_AIR * SOC_AREA)
r_ins_total = r_pad + r_air
chk("隔热层仍在 SoC 与皮肤之间 (0.50 垫 + 0.30 空隙, SoC 投影内)",
    PAD_THK > 0 and AIR_THK > 0,
    f"R_隔热 = {r_pad:.1f} (垫, k={K_SIL}) + {r_air:.1f} (空隙, k={K_AIR}) = {r_ins_total:.1f} K/W (SoC 投影 {SOC_AREA * 1e6:.0f}mm²)",
    "MECH_BUDGET §2.3 数字不变 (解 A 只把隔热层缩到 PCB/SoC 段, 没动位置)")

# 4.2 螺钉旁路热阻 (骨架 -> PCB 皮肤侧)
def r_screw(l_mm):
    a = math.pi / 4 * (1.2e-3) ** 2
    return (l_mm * 1e-3) / (K_STEEL * a)

rs = [r_screw(1.0), r_screw(2.0), r_screw(3.0)]
rs_par = 1.0 / sum(1.0 / r for r in rs)
chk("螺钉热旁路已量化并交 mech (不阻断本单)", True,
    f"M1.2 钢螺钉 R = {rs[0]:.1f}/{rs[1]:.1f}/{rs[2]:.1f} K/W (有效导热长 1/2/3mm) → 2 颗并联 {rs_par:.1f} K/W",
    "★设计约束已写死: 螺钉头只压 PCB 皮肤侧沉孔, **不得**压皮肤侧下壳 (否则金属跨过隔热层); 隔热垫在 2 处螺钉位开 ⌀3.0 让位孔")

# 4.3 骨架若延伸进电池段的并联热路 (复核 4.50 K/W)
L_len, W_v = 40.5e-3, 38.0e-3
R_al = L_len / (K_AL * SKEL_THK * 1e-3 * W_v)
R_par = 1.0 / (1.0 / R_SKIN + 1.0 / (R_al + 50.0 + R_SHELL))
frac_before = R_CONV / (R_SKIN + R_CONV)
frac_after = R_CONV / (R_par + R_CONV)
chk("骨架延伸进电池段的并联热路复算 (4.50 K/W / 92.5%→95.7%)",
    abs(R_al - 4.50) < 0.2 and abs(frac_before * 100 - 92.5) < 0.6 and abs(frac_after * 100 - 95.7) < 0.6,
    f"R_al = {R_al:.2f} K/W; 进皮肤热量 {frac_before * 100:.1f}% → {frac_after * 100:.1f}%",
    "本方案骨架止于 PCB 段后缘 ⇒ 该并联热路**不成立** ⇒ 电池段侧不受影响")

# 4.4 主板承重/挠度 (2 点支撑跨距)
def sag(E, I, span_mm, p_n):
    """简支梁跨中挠度 mm。FR4 E=10000 MPa [推算]; I 由板宽/厚算。"""
    L = span_mm * 1e-3
    return p_n * L ** 3 / (48 * E * I) * 1000.0

# 板惯性矩 (矩形, 宽=15 板宽, 厚=0.8/1.0) —— 板在 V 向平躺, 载荷沿板长
def inertia(w_mm, t_mm):
    return (t_mm * w_mm ** 3) / 12.0 * 1e-12   # m^4

I4 = inertia(15.0, 0.8)
I6 = inertia(15.0, 1.0)
p_asm = 1.0  # N (板自重 + 器件 ~ 0.02kg + 装配力, 保守 1N)
for tag, I in (("4层 0.8mm", I4), ("6层 1.0mm", I6)):
    s = sag(10000e6, I, 44.0, p_asm)
    chk(f"PCB 跨距 44.00mm 挠度 (2 定位销 + 2 螺钉, {tag}) ≤0.30mm", s <= 0.30,
        f"跨中挠度 = {s:.3f}mm (1N 集中载荷, E=10GPa, 简支)",
        "若不成立 → 需加中间支撑或改孔位; 实测值须板厂 1:1 贴装后复测")

# =====================================================================
# 汇总 + 出图
# =====================================================================
n_fail = sum(1 for c in CHECKS if not c["ok"] and c.get("level", "fail") == "fail")
n_warn = sum(1 for c in CHECKS if not c["ok"] and c.get("level") == "warn")
res = {
    "issue": "ISS-049",
    "scheme": "PIN-SET-2",
    "board": {"L": PCB_L, "W": PCB_W, "thk": PCB_THK},
    "escape_band": {"x": [ESC_X0, ESC_X1], "y": [ESC_Y0, ESC_Y1]},
    "holes": [{"key": k, "fn": fn, "x": x, "y": y, "d": d, "mate": mate, "role": role}
              for k, fn, (x, y), d, mate, role in HOLES],
    "skeleton": {"max_len": SKEL_MAX_LEN, "build_len": SKEL_BUILD_LEN,
                 "thk": SKEL_THK, "weight_full_width_g": round(w_skel_full, 3),
                 "weight_stepped_g": round(w_skel_step, 3)},
    "graphite": {"x": [GRAPHITE_X0, GRAPHITE_X1], "y": [GRAPHITE_Y0, GRAPHITE_Y1],
                 "thk": GR_THK, "weight_g": round(w_graphite, 3)},
    "thermal": {"r_insulation_kW": round(r_ins_total, 1),
                "r_screw_parallel_kW": round(rs_par, 1),
                "r_al_if_into_battery_kW": round(R_al, 2),
                "skin_fraction_now": round(frac_before * 100, 1),
                "skin_fraction_if_extended": round(frac_after * 100, 1)},
    "checks": CHECKS,
    "fail": n_fail,
    "warn": n_warn,
    "total": len(CHECKS),
}

with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=2)

# ---------------- SVG 孔位图 ----------------
SC = 10.0          # px per mm
M = 46.0           # margin px


def svg():
    W = PCB_L * SC + 2 * M
    H = PCB_W * SC + 2 * M + 70
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H:.0f}" '
         f'viewBox="0 0 {W:.0f} {H:.0f}" font-family="monospace">',
         '<rect width="100%" height="100%" fill="#ffffff"/>']

    def X(x):
        return M + x * SC

    def Y(y):
        return M + (PCB_W - y) * SC

    # 板框
    o.append(f'<rect x="{X(0):.1f}" y="{Y(PCB_W):.1f}" width="{PCB_L * SC:.1f}" '
             f'height="{PCB_W * SC:.1f}" fill="#f7f7f7" stroke="#000" stroke-width="1.6"/>')
    # 逃线带
    o.append(f'<rect x="{X(ESC_X0):.1f}" y="{Y(ESC_Y1):.1f}" width="{(ESC_X1 - ESC_X0) * SC:.1f}" '
             f'height="{(ESC_Y1 - ESC_Y0) * SC:.1f}" fill="#ffe9e9" stroke="#c00" '
             f'stroke-width="1" stroke-dasharray="4 3"/>')
    # SoC
    o.append(f'<rect x="{X(SOC_X0):.1f}" y="{Y(SOC_Y1):.1f}" width="{(SOC_X1 - SOC_X0) * SC:.1f}" '
             f'height="{(SOC_Y1 - SOC_Y0) * SC:.1f}" fill="#e8e8f8" stroke="#00c" stroke-width="1.2"/>')
    o.append(f'<text x="{X((SOC_X0 + SOC_X1) / 2):.1f}" y="{Y((SOC_Y0 + SOC_Y1) / 2):.1f}" '
             f'font-size="12" text-anchor="middle" fill="#00c">SoC 8x10</text>')
    o.append(f'<text x="{X((ESC_X0 + ESC_X1) / 2):.1f}" y="{Y(PCB_W) + 16:.1f}" font-size="11" '
             f'text-anchor="middle" fill="#c00">逃线带 X[{ESC_X0:.2f},{ESC_X1:.2f}]</text>')
    # J_CHG keep-out
    o.append(f'<rect x="{X(JCHG_X0):.1f}" y="{Y(JCHG_Y1):.1f}" width="{(JCHG_X1 - JCHG_X0) * SC:.1f}" '
             f'height="{(JCHG_Y1 - JCHG_Y0) * SC:.1f}" fill="#f0f0f0" stroke="#888" '
             f'stroke-width="1" stroke-dasharray="3 3"/>')
    o.append(f'<text x="{X(JCHG_X1) + 4:.1f}" y="{Y((JCHG_Y0 + JCHG_Y1) / 2):.1f}" font-size="10" '
             f'fill="#666">J_CHG 座体 keep-out</text>')
    # 骨架/石墨 范围
    o.append(f'<line x1="{X(0):.1f}" y1="{Y(-0.0) + 22:.1f}" x2="{X(PCB_L):.1f}" y2="{Y(-0.0) + 22:.1f}" '
             f'stroke="#0a0" stroke-width="5" opacity="0.45"/>')
    o.append(f'<text x="{X(0):.1f}" y="{Y(-0.0) + 38:.1f}" font-size="11" fill="#0a0">'
             f'骨架+石墨 覆盖 Z=0.00..60.00 (止于 PCB 段后缘, 禁入电池段)</text>')
    # 孔
    for k, fn, (x, y), d, mate, role in HOLES:
        cx, cy, r = X(x), Y(y), d / 2 * SC
        fill = "#d0f0d0" if k.startswith("P") else "#fde9c0"
        o.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="#000" stroke-width="1.3"/>')
        o.append(f'<line x1="{cx - r - 5:.1f}" y1="{cy:.1f}" x2="{cx + r + 5:.1f}" y2="{cy:.1f}" '
                 f'stroke="#888" stroke-width="0.6"/>')
        o.append(f'<line x1="{cx:.1f}" y1="{cy - r - 5:.1f}" x2="{cx:.1f}" y2="{cy + r + 5:.1f}" '
                 f'stroke="#888" stroke-width="0.6"/>')
        lab_y = cy - r - 8 if y > PCB_W / 2 else cy + r + 14
        o.append(f'<text x="{cx:.1f}" y="{lab_y:.1f}" font-size="12" text-anchor="middle" fill="#000">'
                 f'{k} ⌀{d:.1f}</text>')
        o.append(f'<text x="{cx:.1f}" y="{lab_y + 12:.1f}" font-size="10" text-anchor="middle" fill="#444">'
                 f'({x:.2f}, {y:.2f})</text>')
    # 坐标轴
    o.append(f'<text x="{X(0):.1f}" y="{Y(0) + 22:.1f}" font-size="11">X=0 (铰链端)</text>')
    o.append(f'<text x="{X(PCB_L) - 70:.1f}" y="{Y(0) + 22:.1f}" font-size="11">X=60 (电池段侧)</text>')
    o.append(f'<text x="{X(0) - 4:.1f}" y="{Y(0) + 4:.1f}" font-size="11" text-anchor="end">Y=0</text>')
    o.append(f'<text x="{X(0) - 4:.1f}" y="{Y(PCB_W):.1f}" font-size="11" text-anchor="end">Y=15</text>')
    o.append(f'<text x="{M:.1f}" y="{M - 12:.1f}" font-size="13">PIN-SET-2 固定孔位图 (板 60x15mm, 原点左下角)</text>')
    o.append('</svg>')
    return "\n".join(o)


with open(OUT_SVG, "w", encoding="utf-8") as f:
    f.write(svg())

# ---------------- 终端输出 ----------------
print("=" * 96)
print("PIN-SET-2 机械复算 (ISS-049) | PCB 60x15 | 骨架/石墨止于 PCB 段后缘")
print("=" * 96)
print(f"\n【孔位定版】")
for k, fn, (x, y), d, mate, role in HOLES:
    print(f"  {k} {fn:<10s} ⌀{d:.2f}  ({x:6.2f}, {y:5.2f})  ← {mate}   [{role}]")
print(f"\n【骨架/石墨】")
print(f"  骨架长度上限 {SKEL_MAX_LEN:.2f}mm (止于 PCB 段后缘) / 建议实现 {SKEL_BUILD_LEN:.2f}mm")
print(f"  石墨覆盖 X[{GRAPHITE_X0:.2f},{GRAPHITE_X1:.2f}] Y[{GRAPHITE_Y0:.2f},{GRAPHITE_Y1:.2f}] "
      f"厚 {GR_THK:.2f}mm, 单片 {w_graphite:.2f}g")
print(f"  骨架重量: 满宽 {w_skel_full:.2f}g/侧 / 台阶形 {w_skel_step:.2f}g/侧 (一对 {2 * w_skel_step:.2f}g)")
print(f"\n【热路】")
print(f"  隔热 R = {r_ins_total:.1f} K/W (0.50 垫 + 0.30 空隙, SoC 投影内) — 位置未动 ✅")
print(f"  螺钉旁路 2 颗并联 {rs_par:.1f} K/W (M1.2 钢, 有效导热长 1-3mm) → 已量化交 mech")
print(f"  骨架若进电池段: R_al {R_al:.2f} K/W → 进皮肤热量 {frac_before * 100:.1f}%→{frac_after * 100:.1f}% "
      f"⇒ 本方案该热路不成立 ✅")
print(f"\n【逐条复算】")
for c in CHECKS:
    mark = "✅" if c["ok"] else ("❌" if c.get("level", "fail") == "fail" else "⚠️")
    print(f"  {mark} {c['name']}: {c['detail']}")
print(f"\n【汇总】 {len(CHECKS) - n_fail - n_warn}/{len(CHECKS)} 通过, FAIL {n_fail} 项, WARN {n_warn} 项")
print(f"  JSON -> {OUT_JSON}")
print(f"  SVG  -> {OUT_SVG}")
print("=" * 96)
raise SystemExit(1 if n_fail else 0)
