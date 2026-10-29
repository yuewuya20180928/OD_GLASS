#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-118 板宽 15→30mm 硬件连带重算 (机械复算器)
=====================================================================
题目: 老板 10-29 19:16 放宽板宽到 ≤30mm; 主控从 ARS45 换成 RK3588 / RK3576
      ⇒ 板框 60×15 → 60×30mm, 定位孔位/逃线带/面积账/跨铰链排布/散热输入全部重算

本脚本做 6 件事 (全部机械判定, 不靠人眼):
  ① 板框与板重 (60×30 vs 60×15) + 镜脚 V 向余量 (★板宽是 V 向尺寸!)
  ② 逃线带 (沿用 HW/SOC_PIN_BUDGET.md 的 band() 模型, 扩展到 p=0.65 / p=0.60)
     + 逃线深度 (球阵列圈数) → 所需布线层数 (对 "4-6 层" 锁死的影响)
  ③ 面积账: 旧基线 (ARS45, 655mm²) → RK3588 / RK3576 两版 (逐项台账, 可审计)
  ④ 定位孔位 (PIN-SET-2 在 30mm 宽下) —— 用 ISS-049 那套 2D 重叠法
  ⑤ 跨铰链连接器排布复核 (54 触点 @0.5mm = 27mm 的真实含义 + 30mm 宽下排得下吗)
  ⑥ 散热模型输入 (铜箔面积 / 散热路径长度 / 骨架石墨) —— **只给输入, 不算皮肤温度**

输出: HW/pcb60x30_check.json + 终端表格
rc  = 0 → 全部算完 (含"某项超差"的 WARN, 不算本单失败) / 1 → 有硬 FAIL

纪律: 只写 HW/ 下本脚本自己的两个文件; 不改任何别人的文件; 不碰 state/ / MECH/。
"""
from __future__ import annotations

import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_JSON = os.path.join(HERE, "pcb60x30_check.json")

# =====================================================================
# 输入 —— 每行都标来源
# =====================================================================

# ---- 板框 ----
PCB_L = 60.00          # 板长 X (mm)  [决策] 10-28 项目总工裁; ISS-118 沿用
PCB_W_OLD = 15.00      # 旧板宽 Y     [决策] 老板 10-27 (本单被 30 取代)
PCB_W_NEW = 30.00      # 新板宽 Y     [决策] 老板 10-29 19:16 "板宽可以放到 30mm 以内"
PCB_THK = 1.00         # 板厚 (6 层)  [既有] 4-6 层锁死
PCB_THK_4L = 0.80      # 板厚 (4 层)
FR4_RHO = 1.85         # FR4 密度 g/cc  [推算] MECH_BUDGET §3 W5
AL_RHO = 2.70          # 铝密度 g/cc   [推算] MECH_BUDGET §3 W5
GR_RHO = 2.00          # 柔性石墨密度  [推算]
GR_THK = 0.30          # 石墨片厚      [推算] ISS-049

# ---- 镜脚内腔 (结构侧; ★板宽是 V 向尺寸 ⇒ 这一段决定板宽的物理上限) ----
CAV_H = 7.30           # 镜脚前后厚  [推算] MECH_BUDGET §1.6.2 (老板 10-27 Q4 锁死 7.3mm)
CAV_V = 38.00          # 镜脚根部净高 [推算] MECH_BUDGET §1.6.2
CAV_L = 130.00         # 镜脚内腔长   [推算]
CELL_L = 40.50         # 电芯长       [推算] 解A
CELL_V = 23.50         # 电芯高       [推算]
DUCT_V = 6.00          # 走线槽 V 占位 [推算] MECH_BUDGET §5.6.2
CONN_MARGIN = 15.00    # 连接器/弯折余量 [推算] §1.4.2
CRIT = 0.60            # 装配余量判据 = 2 × FDM 0.30 [推算] fit_check §0
MAX_BOARD_L = CAV_L - CELL_L - CONN_MARGIN   # 板长物理上限 (电芯 40.5 + 余量 15)

# ---- 旧基线 (ARS45 方案) 面积账 —— HW/PCB_FORM_FACTOR_RECHECK.md §5.3 ----
OLD_LAND_DRAWN = 246.0      # netlist 已画 (146 器件)      [推算] 旧 §5.3
OLD_LAND_UNDRAWN = 296.0    # 未画入必需件                   [推算] 旧 §5.3
OLD_SOC_ESCAPE = 113.0      # SoC 8×10 + 逃线框 9.6×11.6    [推算] 旧 §5.3
OLD_LAND_TOTAL = OLD_LAND_DRAWN + OLD_LAND_UNDRAWN + OLD_SOC_ESCAPE   # 655
OLD_BOARD_AREA = 900.0
UTIL_2SIDE = 0.72          # 双面贴 land 占比 [推算] 旧 §5.3
UTIL_1SIDE = 0.60          # 单面贴 land 占比 [推算] 旧 §5.3
UTIL_OPTIMISTIC = 0.78     # 最乐观口径 (旧 §5.3 自述上限)

# ---- 新 SoC 封装 ----
# ★RK3588 官方封装: FCBGA1088L, body 23mm x 23mm, ball 0.36mm, pitch 0.65mm
#   [官方] Rockchip "RK3588 Datasheet" Rev 1.9 / V2.2 §1.2 + §2.3:
#          "Package Type FCBGA1088L (body: 23mm x 23mm; ball size: 0.36mm;
#           ball pitch: 0.65mm)"
#   ★**项目库里的 "~21×21mm" 是 [推算] 且错的** (HW/SOC_BACKUP_SCORE_15.md /
#     HW/CHIP_SCORING_RESULT.md / HW/CHIP_SELECTION_DECISION.md 都抄了这个数)
#   ★球数 1088 = 32 × 34 —— 与 0.65mm pitch / 23mm body 自洽 (32×0.65 = 20.8 + 边距 ≈ 23mm)
SOC_RK3588 = dict(
    name="RK3588",
    pkg_w=23.00, pkg_h=23.00,      # X, Y 方向封装体 (mm)  [官方]
    pitch=0.65,                     # 球间距 (mm)              [官方]
    n_balls=1088,                   # FCBGA1088L 总球数        [官方]
    arr_x=32, arr_y=34,             # 32×34 = 1088            [推算]
    ddr_chips=2,                    # 64-bit ⇒ 2× 32-bit 器件   [推算]
    ddr_pkg=(10.00, 14.50),         # 200-ball TFBGA            [官方] Micron/Alliance
    ddr_note="64-bit (Quad-channel x16bit) ⇒ 2× 32-bit 器件 (4× x16 则 580mm², 更差)",
)
# ★RK3576 官方封装: FCCSP698L 16.1 × 17.2mm, pitch 0.6mm, 698 球
#   [官方] Rockchip "RK3576 Brief Datasheet" V1.2 §Package Information:
#          "FCCSP698L (16.1 x 17.2mm, pitch: 0.6mm)"
#   ★落位方向: 17.2 沿板长 X / 16.1 沿板宽 Y (省板宽)
SOC_RK3576 = dict(
    name="RK3576",
    pkg_w=17.20, pkg_h=16.10,      # X, Y 方向封装体 (mm)  [官方]
    pitch=0.60,
    n_balls=698,
    arr_x=28, arr_y=26,             # ≈28×26 = 728 ≥ 698     [推算]
    ddr_chips=1,                    # 32-bit ⇒ 1× 32-bit 器件   [推算]
    ddr_pkg=(10.00, 14.50),
    ddr_note="32-bit ⇒ 1× 32-bit 器件 (2× x16 则 290mm², 多占 145mm²)",
)

# ---- 逃线模型 (沿用 HW/SOC_PIN_BUDGET.md 的 ESCAPE / band()) ----
ESCAPE = {
    0.65: dict(ball_pad=0.30, trace=0.30, via_pad=0.40, via_drill=0.20,
                tech="常规机械钻 0.20mm", cls="常规板可做单排逃线"),
    0.60: dict(ball_pad=0.30, trace=0.30, via_pad=0.40, via_drill=0.20,
                tech="常规机械钻 0.20mm", cls="常规板可做单排逃线"),
}
ROW_CLEAR = 0.05
MIN_ELEC_CLEAR = 0.075

# ---- 定位孔位 (PIN-SET-2, ISS-049) 在 60×30 下的新坐标 ----
#   X 坐标沿用 ISS-049 (骨架 X 位置不变 ⇒ 骨架不用重新开孔); 只改 Y
HOLES = [
    ("P1", "主定位销孔", (8.00, 15.00), 2.00, "全基准 (X/Y/θz)"),
    ("P2", "副定位销孔", (52.00, 15.00), 2.00, "只定 Y (骨架配菱形销)"),
    ("S1", "压紧螺钉孔", (8.00, 2.50), 1.40, "只压紧"),
    ("S2", "压紧螺钉孔", (52.00, 27.50), 1.40, "只压紧"),
]
# SoC 落位 (板坐标, 原点左下角; X=板长 0..60, Y=板宽 0..30)
SOC_POS = {
    "RK3588": dict(x0=15.00, y0=3.50),    # 23×23 居中于 30mm 宽 ⇒ 每边 3.50
    "RK3576": dict(x0=15.00, y0=6.95),    # 16.1 居中 ⇒ 每边 6.95
}
# J_CHG 座体 keep-out (铰链端) —— 30mm 宽下居中于 Y=15
JCHG_RECT = (0.00, 3.00, 11.75, 18.25)

# ---- 跨铰链连接器 (ISS-085 / ISS-091) ----
# ★54 触点 @0.5mm = 27mm: 这个 27mm **同时**是两个量, 必须分清:
#   (a) PCB 侧: 4 条连接器触点排宽度之和 (若沿板宽并排铺)
#   (b) 铰链区: 4 条 FPC 排线的**竖向堆叠高度** (ISS-091 §N6: 27.0 任务锚点 /
#       DECISIONS.md 记 26.5, 两数不一致, 取 27.0 保守) —— 对比镜脚根部净高 37.0mm
HINGE_LINKS = [("CONN_CAM", 18), ("CONN_LIGHT", 22), ("CONN_USB", 4), ("J_CHG", 10)]
HINGE_PITCH = 0.50
HINGE_NET_HEIGHT = 37.00    # 镜脚根部净高 (ISS-091 口径) [推算] MECH_BUDGET §1.4.2
HINGE_STACK_ANCHOR = 27.0   # 任务锚点 [推算] HINGE_POWER_CALC §N6
HINGE_STACK_DECISIONS = 26.5   # DECISIONS.md 记的值 [推算]

# ---- 散热 (只给输入) ----
GRAPHITE_X = (0.00, PCB_L)
OLD_GRAPHITE_Y = (0.00, PCB_W_OLD)
NEW_GRAPHITE_Y = (0.00, PCB_W_NEW)
SKEL_THK = 1.00
SKEL_REST_W = 10.00       # 非 SoC 段骨架宽度 [推算] ISS-049 §4

CHECKS = []


def chk(name, ok, detail, note="", level="fail"):
    CHECKS.append({"name": name, "ok": bool(ok), "level": level,
                   "detail": detail, "note": note})
    return ok


def band(p: float, rows: int = 1) -> float:
    """逃线带/边 (从封装外廓量起) —— 抄 HW/SOC_PIN_BUDGET.md 的 band()。"""
    e = ESCAPE[p]
    row_pitch = e["via_pad"] + ROW_CLEAR
    return (p / 2 + 0.05 + e["trace"] + (rows - 1) * row_pitch + e["via_pad"] / 2)


def rect(x, y, d):
    r = d / 2.0
    return (x - r, x + r, y - r, y + r)


def overlap_2d(a, b):
    dx = min(a[1], b[1]) - max(a[0], b[0])
    dy = min(a[3], b[3]) - max(a[2], b[2])
    return (dx * dy) if (dx > 0 and dy > 0) else 0.0


def max_rows_in_band(p: float, half_space: float) -> int:
    """在给定半宽空间内, 单排堆叠的逃线最多能放几排 (band(p,R) <= half_space)。"""
    r = 1
    while band(p, r + 1) <= half_space and r < 64:
        r += 1
    return r


# =====================================================================
# ① 板框 / 板重 / 镜脚 V 向余量
# =====================================================================
def sec1():
    out = {}
    for tag, w in (("60x15 (旧)", PCB_W_OLD), ("60x30 (新)", PCB_W_NEW)):
        area = PCB_L * w
        v_pcb = w + DUCT_V
        v_cell = CELL_V + DUCT_V
        v_need = max(v_pcb, v_cell)
        out[tag] = dict(
            area=area,
            weight_6l_g=round(area * PCB_THK * 1e-3 * FR4_RHO, 3),
            weight_4l_g=round(area * PCB_THK_4L * 1e-3 * FR4_RHO, 3),
            v_pcb=v_pcb, v_cell=v_cell, v_need=v_need,
            v_margin=CAV_V - v_need,
            v_margin_worst=(CAV_V - v_need) - 2 * 0.30,
            l_need=CELL_L + PCB_L + CONN_MARGIN,
            l_margin=CAV_L - (CELL_L + PCB_L + CONN_MARGIN),
            max_board_len=MAX_BOARD_L,
        )
    chk("板重 (裸板 FR4, 6 层 1.0mm): 60×15 → 60×30", True,
        f"{out['60x15 (旧)']['weight_6l_g']:.2f}g → {out['60x30 (新)']['weight_6l_g']:.2f}g/侧 "
        f"(+{out['60x30 (新)']['weight_6l_g'] - out['60x15 (旧)']['weight_6l_g']:.2f}g/侧, "
        f"+{(out['60x30 (新)']['weight_6l_g'] - out['60x15 (旧)']['weight_6l_g']) * 2:.2f}g/对)",
        "板重随板宽线性增长 ⇒ 整机重量账 (MECH_BUDGET §3.1 目标 48.9-74.0g) 必须重算")
    chk("镜脚 V 向余量 (★板宽是 V 向尺寸, 不是 H) —— 30mm 板宽只剩 2.00mm",
        out["60x30 (新)"]["v_margin"] >= CRIT,
        f"PCB 段 V 需求 {out['60x30 (新)']['v_pcb']:.2f}mm (板宽 {PCB_W_NEW:.0f} + 走线槽 {DUCT_V:.0f}) "
        f"vs 净高 {CAV_V:.2f} → 余量 {out['60x30 (新)']['v_margin']:.2f}mm "
        f"(对抗性最坏 {out['60x30 (新)']['v_margin_worst']:.2f}mm); "
        f"15mm 板宽时是 {out['60x15 (旧)']['v_margin']:.2f}mm",
        "★ 板宽在镜脚里是 **垂直 V 向** 尺寸 (MECH/BOARD_WIDTH_15MM.md §1.2) ⇒ 板宽 15→30 "
        "直接吃镜脚净高。判据 ≥0.60 仍过, 但余量从 8.50 掉到 2.00mm。⇒ 若净高 38.00 不变, "
        "板宽硬顶 = 38.00-6.00-0.60 = 31.40mm (30mm 刚好在顶)",
        level="warn")
    chk("镜脚 L 向余量 (板长 60 不变) + 板长物理上限", out["60x30 (新)"]["l_margin"] >= CRIT,
        f"L 需求 {out['60x30 (新)']['l_need']:.2f}mm vs 内长 {CAV_L:.2f} → 余量 {out['60x30 (新)']['l_margin']:.2f}mm; "
        f"板长物理上限 = {CAV_L:.0f} - {CELL_L:.1f}(电芯) - {CONN_MARGIN:.0f}(余量) = {MAX_BOARD_L:.1f}mm",
        "★ L 余量决定 **面积不够时能不能加长**: 60 → 最多 74.5mm (+14.5mm)")
    return out


# =====================================================================
# ② 逃线带 + 逃线深度 → 所需层数
# =====================================================================
def sec2(socs):
    out = {}
    for k, soc in socs.items():
        p = soc["pitch"]
        e = ESCAPE[p]
        b1 = band(p, 1)
        clear = p - e["via_pad"]
        rows_deep = (max(soc["arr_x"], soc["arr_y"]) + 1) // 2   # 中心到边缘的球圈数
        # 规则 [推算/媒体]: 全阵列 BGA 每增加 1 个布线层, 多逃 2 圈球
        #   (AtlasPCB "BGA Escape Routing": every 2 rows that can't escape on the
        #    current layer need one additional routing layer)
        sig_layers = -(-rows_deep // 2)
        total_layers = sig_layers + 2
        # 板宽 30mm 下, SoC 边到板边的半宽空间只能放几排逃线
        half_space = (PCB_W_NEW - soc["pkg_w"]) / 2
        rows_in_edge = max_rows_in_band(p, half_space)
        out[k] = dict(
            band_1row=round(b1, 3),
            band_2row=round(band(p, 2), 3),
            band_4row=round(band(p, 4), 3),
            same_row_via_clear=round(clear, 3),
            min_elec_clear_ok=clear >= MIN_ELEC_CLEAR,
            rows_deep=rows_deep,
            signal_layers_needed=sig_layers,
            total_layers_needed=total_layers,
            fits_4_6_layer=total_layers <= 6,
            edge_half_space=round(half_space, 2),
            rows_escapable_in_edge=rows_in_edge,
            edge_band_for_that=round(band(p, rows_in_edge), 3),
        )
        chk(f"{soc['name']} 逃线带 (p={p}, 常规机械钻 0.20mm)", clear >= MIN_ELEC_CLEAR,
            f"单排逃线带 {b1:.2f}mm/边; 同排过孔净间隙 {clear:.3f}mm (判据 ≥{MIN_ELEC_CLEAR})",
            f"2 排 {band(p, 2):.2f}mm / 4 排 {band(p, 4):.2f}mm/边")
        chk(f"{soc['name']} 逃线深度 → 所需层数 (对 '4-6 层' 锁死)", total_layers <= 6,
            f"≈{soc['arr_x']}×{soc['arr_y']} 阵列 ({soc['n_balls']} 球) ⇒ 中心到边 {rows_deep} 圈 "
            f"⇒ 需 {sig_layers} 布线层 + 2 参考面 = **{total_layers} 层**",
            "★ 对比旧方案: ARS45 只按 C-base 57 球 / C-max 91 球设计 (HW/SOC_PIN_BUDGET.md), "
            "逃 1 排即可 ⇒ 4-6 层轻松。两颗新 SoC 是 **全阵列**, 球数是旧方案的 12-19 倍 "
            "⇒ 4-6 层常规板大概率不可行。解法只有 (a) 加层 (b) via-in-pad HDI "
            "(破 '不含 HDI' 锁死, 价 2-3× + 交期 +1-2 周, 见 HW/PCB_FORM_FACTOR_RECHECK.md §6) "
            "⇒ **需 PCB 厂 DFM 报告定案**")
        chk(f"{soc['name']} 30mm 板宽下 SoC 边到板边的逃线空间", True,
            f"SoC 边→板边半宽 {half_space:.2f}mm ⇒ 只够排 {rows_in_edge} 排逃线 "
            f"(占 {band(p, rows_in_edge):.2f}mm/边)",
            f"⇒ 剩下 {rows_deep - rows_in_edge} 圈球**必须靠内层布线层往外走** "
            "⇒ 这是 ② 层数结论的独立佐证")
    return out


# =====================================================================
# ③ 面积账 (旧基线 → 两版) —— 逐项台账, 可审计
# =====================================================================
def sec3(socs, esc):
    out = {}
    for k, soc in socs.items():
        ef = esc[soc["name"]]["escape_frame"]
        new_soc = ef[0] * ef[1]
        dw, dh = soc["ddr_pkg"]
        ddr_area = soc["ddr_chips"] * dw * dh

        # 台账: 每项 (名称, mm², 依据) —— 全部是"绝对值", 不是增量, 可直接加总
        items = [
            ("netlist 已画器件 (旧 146 器件口径, 换芯后待重画)",
             OLD_LAND_DRAWN, "[推算] 旧 §5.3; ★SoC 侧 157 行 TBD 待重画 (ISS-119), 此处保留旧值"),
            ("未画入必需件 (旧口径: DCDC/LDO/PD/晶振/ESD/去耦/连接器/存储/桥接)",
             OLD_LAND_UNDRAWN, "[推算] 旧 §5.3"),
            ("SoC 封装 + 逃线框 (换新封装)",
             new_soc,
             f"[官方] {soc['pkg_w']}×{soc['pkg_h']} @p={soc['pitch']} + 单排逃线带 "
             f"{esc[soc['name']]['band_1row']:.2f}mm/边 ⇒ {ef[0]:.2f}×{ef[1]:.2f} = {new_soc:.1f}mm² "
             f"(旧 113mm²)"),
            ("删 U_BRIDGE (QFN6×6 + AC 耦合 + 串阻)",
             -52.0, "RK3588/RK3576 原生 MIPI-DSI TX ⇒ 不做桥接 (CHIP_SELECTION_DECISION §5)"),
            (f"外挂 LPDDR4 {soc['ddr_chips']} 片 (200-ball FBGA {dw}×{dh})",
             ddr_area,
             f"[官方] Micron/Alliance 200-ball TFBGA 10×14.5mm = 145mm²/片; {soc['ddr_note']}. "
             "★**换芯打破 §0 锁死 #5 'DDR 512MB, 不外挂'** (两颗新 SoC 都无内置 DRAM)"),
            ("eMMC 5.1 FBGA153 (11.5×13.0) 替 SPI-NOR SOIC-8",
             149.5 - 28.0,
             "[官方] eMMC 5.1 153-ball 11.5×13.0 = 149.5mm² (FLEXXON/Exascend); "
             "旧存储口径 28mm² 是 SPI-NOR SOIC-8"),
            ("DDR 周边去耦/体电容 (0402+0603)",
             20.0 if soc["name"] == "RK3588" else 10.0,
             "[推算] LPDDR4 需 VDDQ 体电容 + 每颗电源域去耦; RK3588 4 通道 ⇒ 更多"),
            ("电源树 6A 级余量 (电感/大电流铜箔/额外 LDO)",
             15.0 if soc["name"] == "RK3588" else 10.0,
             "[推算] CHIP_SELECTION_DECISION D2 '电源树按 6A 级设计'"),
            ("外置 PMIC (8×8 QFN + 周边) —— 两颗新 SoC 都无内置 PMIC",
             90.0, "[推算] RK3588/RK3576 需外置 PMIC (RK806 类); 8×8 = 64mm² + 周边 ≈ 90mm²"),
            ("SoC 去耦电容增加 (电源域变多)",
             15.0 if soc["name"] == "RK3588" else 5.0,
             "[推算] 旧 30 颗 = 30mm²; 新 SoC 电源域更多 ⇒ 35~45 颗"),
        ]
        land_total = sum(v for _, v, _ in items)
        area = PCB_L * PCB_W_NEW
        need_2s = land_total / UTIL_2SIDE
        need_1s = land_total / UTIL_1SIDE
        need_opt = land_total / UTIL_OPTIMISTIC
        dev_land = land_total - new_soc
        # 板长要加到多少才装得下
        need_len = need_2s / PCB_W_NEW
        need_len_opt = need_opt / PCB_W_NEW
        out[k] = dict(
            soc_escape_frame=round(new_soc, 1),
            device_land=round(dev_land, 1),
            land_total=round(land_total, 1),
            board_area=area,
            raw_spare=round(area - land_total, 1),
            need_2side=round(need_2s, 1),
            need_1side=round(need_1s, 1),
            need_optimistic=round(need_opt, 1),
            verdict_2side=("✅ 装得下 (余 %.1fmm²)" % (area - need_2s) if need_2s <= area
                           else "❌ 缺 %.1fmm²" % (need_2s - area)),
            verdict_1side=("✅ 装得下" if need_1s <= area else "❌ 缺 %.1fmm²" % (need_1s - area)),
            verdict_optimistic=("✅ 装得下 (余 %.1fmm²)" % (area - need_opt) if need_opt <= area
                                else "❌ 缺 %.11fmm²" % (need_opt - area)),
            land_fraction=round(land_total / area, 3),
            need_len_at_w30=round(need_len, 1),
            need_len_at_w30_optimistic=round(need_len_opt, 1),
            max_board_len=MAX_BOARD_L,
            items=[(n, round(v, 1), note) for n, v, note in items],
        )
        chk(f"{soc['name']} 面积账 (60×30, 双面贴利用率 0.72)", need_2s <= area,
            f"land 合计 {land_total:.1f}mm² ⇒ 需板面积 {need_2s:.0f}mm² vs 可用 {area:.0f}mm² "
            f"→ {out[k]['verdict_2side']}",
            f"器件占位 {dev_land:.1f} + SoC 逃线框 {new_soc:.1f} = {land_total:.1f}mm² "
            f"(占板面 {land_total / area * 100:.1f}%); 单面贴口径 {need_1s:.0f}mm² ({out[k]['verdict_1side']}); "
            f"最乐观 0.78 口径 {need_opt:.0f}mm² ({out[k]['verdict_optimistic']})")
        chk(f"{soc['name']} 面积账 (板长加到物理上限 {MAX_BOARD_L:.1f}mm 时)", need_len <= MAX_BOARD_L,
            f"板宽 {PCB_W_NEW:.0f}mm 时按 0.72 利用率需板长 {need_len:.1f}mm vs 上限 {MAX_BOARD_L:.1f}mm "
            f"⇒ {'✅ 加长装得下 (余 %.1fmm)' % (MAX_BOARD_L - need_len) if need_len <= MAX_BOARD_L else '❌ 加长也装不下'}",
            f"最乐观 0.78 口径需板长 {need_len_opt:.1f}mm ⇒ "
            f"{'✅ 装得下 (余 %.1fmm)' % (MAX_BOARD_L - need_len_opt) if need_len_opt <= MAX_BOARD_L else '❌ 装不下'}; "
            "板长上限 = 内长 130 - 电芯 40.5 - 余量 15")
    return out


# =====================================================================
# ④ 定位孔位 (30mm 宽) —— ISS-049 那套 2D 重叠法
# =====================================================================
def sec4(socs, esc):
    out = {}
    for k, soc in socs.items():
        pos = SOC_POS[soc["name"]]
        b = esc[soc["name"]]["band_1row"]
        pkg = (pos["x0"], pos["x0"] + soc["pkg_w"], pos["y0"], pos["y0"] + soc["pkg_h"])
        escb = (pkg[0] - b, pkg[1] + b, pkg[2] - b, pkg[3] + b)
        holes = {}
        for hk, fn, (x, y), d, role in HOLES:
            hr = rect(x, y, d)
            ov_esc = overlap_2d(hr, escb)
            ov_pkg = overlap_2d(hr, pkg)
            ov_j = overlap_2d(hr, JCHG_RECT)
            edge = min(x, PCB_L - x, y, PCB_W_NEW - y)
            holes[hk] = dict(
                fn=fn, x=x, y=y, d=d, role=role,
                ov_escape_band=round(ov_esc, 4),
                ov_pkg=round(ov_pkg, 4),
                ov_jchg_keepout=round(ov_j, 4),
                edge_to_center=round(edge, 2),
                edge_wall=round(edge - d / 2, 2),
            )
            chk(f"{soc['name']} {hk} vs SoC 逃线带 2D 重叠", ov_esc == 0.0,
                f"2D 重叠面积 = {ov_esc:.4f} mm² (孔心 ({x:.2f},{y:.2f}) ⌀{d:.2f})",
                f"逃线带 X[{escb[0]:.2f},{escb[1]:.2f}] Y[{escb[2]:.2f},{escb[3]:.2f}]")
            chk(f"{soc['name']} {hk} vs SoC 封装体 2D 重叠", ov_pkg == 0.0,
                f"2D 重叠面积 = {ov_pkg:.4f} mm²")
            chk(f"{soc['name']} {hk} vs J_CHG 座体 keep-out 2D 重叠", ov_j == 0.0,
                f"2D 重叠面积 = {ov_j:.4f} mm²")
            chk(f"{soc['name']} {hk} 孔心到板边 ≥1.50mm / 孔壁 ≥0.80mm",
                edge >= 1.50 and edge - d / 2 >= 0.80,
                f"孔心距边 {edge:.2f}mm / 孔壁距边 {edge - d / 2:.2f}mm",
                "判据: CLEARANCE_FIX 卡点2 孔心 ≥1.50mm; 器件边距 ≥0.80mm")
        min_cc, min_wall = 1e9, 1e9
        for i in range(len(HOLES)):
            for j in range(i + 1, len(HOLES)):
                a, b2 = HOLES[i], HOLES[j]
                dcc = math.dist(a[2], b2[2])
                wall = dcc - a[3] / 2 - b2[3] / 2
                min_cc = min(min_cc, dcc)
                min_wall = min(min_wall, wall)
        chk(f"{soc['name']} 孔间中心距 ≥5.00 / 孔壁间距 ≥2.00", min_cc >= 5.0 and min_wall >= 2.0,
            f"最小中心距 {min_cc:.2f}mm / 最小孔壁间距 {min_wall:.2f}mm")
        out[k] = dict(soc_pkg=[round(v, 2) for v in pkg],
                      escape_band=[round(v, 2) for v in escb],
                      holes=holes,
                      min_center_dist=round(min_cc, 2),
                      min_wall_dist=round(min_wall, 2))
    diag = math.dist(HOLES[2][2], HOLES[3][2])
    diag_old = math.dist((8.00, 2.50), (52.00, 12.50))
    chk("螺钉对角跨距 (30mm 宽下抗扭几何更好)", True,
        f"S1→S2 对角距离 {diag:.2f}mm (30mm 宽) vs {diag_old:.2f}mm (15mm 宽) ⇒ 抗扭力臂 +{diag - diag_old:.2f}mm",
        "ISS-049 用对角分布抗扭; 板宽翻倍后 Y 向力臂从 10mm 变 25mm ⇒ 这是板宽翻倍的**正收益**")
    chk("骨架 X 位置不变 (只改 Y)", True,
        "P1/P2/S1/S2 的 X = 8.00 / 52.00 与 ISS-049 完全一致 ⇒ 金属骨架的销孔/攻丝孔 X 坐标不用改",
        "★ 换板宽时**只动 Y** ⇒ 骨架件不用重新开孔 ⇒ 结构侧改动最小")
    return out


# =====================================================================
# ⑤ 跨铰链连接器排布复核
# =====================================================================
def sec5():
    total_pins = sum(n for _, n in HINGE_LINKS)
    stack = total_pins * HINGE_PITCH
    per_conn = [(nm, n, round(n * HINGE_PITCH, 2),
                 round(n * HINGE_PITCH + 2 * 0.80, 2)) for nm, n in HINGE_LINKS]
    widest = max(c[2] for c in per_conn)
    need_single = stack + 2 * 0.80
    out = dict(
        total_pins=total_pins,
        pad_row_sum=round(stack, 2),
        per_connector=[(nm, n, r, rk) for nm, n, r, rk in per_conn],
        widest_row=round(widest, 2),
        widest_row_with_keepout=round(widest + 1.60, 2),
        stack_vs_netheight=round(stack, 2),
        stack_margin_vs_37=round(HINGE_NET_HEIGHT - stack, 2),
        stack_margin_vs_decisions=round(HINGE_NET_HEIGHT - HINGE_STACK_DECISIONS, 2),
        stack_anchor=HINGE_STACK_ANCHOR,
        stack_decisions=HINGE_STACK_DECISIONS,
        declared_stack=49.62, converged_stack=24.00,
        pcb_single_row_need=round(need_single, 2),
        pcb_fits_15mm=need_single <= PCB_W_OLD,
        pcb_fits_30mm=need_single <= PCB_W_NEW,
    )
    chk("跨铰链 54 触点 @0.5mm = 27mm —— 真义是 **FPC 竖向堆叠**, 与板宽无关", True,
        f"4 条排线宽度之和 = ({' + '.join(str(n) for _, n in HINGE_LINKS)}) × {HINGE_PITCH} = "
        f"{stack:.2f}mm (铰链区竖向堆叠) vs 镜脚根部净高 {HINGE_NET_HEIGHT:.2f}mm → 余 "
        f"{HINGE_NET_HEIGHT - stack:.2f}mm (按 DECISIONS.md 的 26.5 则余 {HINGE_NET_HEIGHT - HINGE_STACK_DECISIONS:.2f}mm)",
        "★ ISS-091/HINGE_POWER_CALC 记 27.0 (任务锚点) / DECISIONS.md 记 26.5 —— 两数不一致 "
        "(ISS-091 §N6 已列), 结论方向不变 (都 < 37.0)。⇒ **板宽 15→30 一分不改这条结论**: "
        "堆叠高度由触点数×pitch 决定, 与 PCB 板宽无关")
    chk("PCB 侧 27mm 焊盘排在 30mm 板宽下排得下 (15mm 排不下)", need_single <= PCB_W_NEW,
        f"27.00mm 焊盘排 + 2×0.80mm 器件边距 = {need_single:.2f}mm ⇒ "
        f"15mm 板宽 {'✅' if need_single <= PCB_W_OLD else '❌'} / 30mm 板宽 {'✅' if need_single <= PCB_W_NEW else '❌'}",
        "★ 这才是 ISS-105 F-2 ('54 触点焊盘排 vs 板宽') 的正解: 板宽翻倍把 **PCB 侧** 从装不下变成装得下; "
        "但 **铰链区竖向堆叠** 27mm 一分没变 ⇒ **板宽翻倍不能解决 ISS-091 那条超差**")
    chk("4 条连接器沿板长 X 展开时, 板宽需求 (更省的排法)", widest + 1.60 <= PCB_W_NEW,
        f"最宽一条 CONN_LIGHT 22p = {widest:.2f}mm + 2×0.80 边距 = {widest + 1.60:.2f}mm ⇒ "
        f"15mm 板宽 {'✅' if widest + 1.60 <= PCB_W_OLD else '❌'} / 30mm 板宽 {'✅' if widest + 1.60 <= PCB_W_NEW else '❌'}",
        "沿 X 展开 (4 条占不同 X 段) 时的板宽需求 —— 30mm 宽下 4 条都有充裕的 Y 向空间; "
        "代价是吃板长 (铰链端 X 段), 板长上限 74.5mm")
    return out


# =====================================================================
# ⑥ 散热模型输入 (只给输入, 不算皮肤温度)
# =====================================================================
def sec6(socs, esc, area):
    out = {}
    for k, soc in socs.items():
        pos = SOC_POS[soc["name"]]
        b = esc[soc["name"]]["band_1row"]
        pkg_w, pkg_h = soc["pkg_w"], soc["pkg_h"]
        cx = pos["x0"] + pkg_w / 2
        cy = pos["y0"] + pkg_h / 2
        lat_ch = (PCB_W_NEW - pkg_w) / 2
        g_old = (GRAPHITE_X[1] - GRAPHITE_X[0]) * (OLD_GRAPHITE_Y[1] - OLD_GRAPHITE_Y[0]) * GR_THK * 1e-3 * GR_RHO
        g_new = (GRAPHITE_X[1] - GRAPHITE_X[0]) * (NEW_GRAPHITE_Y[1] - NEW_GRAPHITE_Y[0]) * GR_THK * 1e-3 * GR_RHO
        w_full = PCB_L * PCB_W_NEW * SKEL_THK * 1e-3 * AL_RHO
        soc_seg = pkg_w + 2 * b            # SoC 段轴向 = 封装 + 两端逃线带
        w_step = (soc_seg * PCB_W_NEW + (PCB_L - soc_seg) * SKEL_REST_W) * SKEL_THK * 1e-3 * AL_RHO
        usable_side = lat_ch - b
        out[k] = dict(
            soc_top_pad_projection=round(pkg_w * pkg_h, 1),
            soC_center=[round(cx, 2), round(cy, 2)],
            lateral_copper_channel=round(lat_ch, 2),
            lateral_usable_after_escape=round(usable_side, 2),
            heat_path_Y_to_edge=round(min(cy, PCB_W_NEW - cy), 2),
            heat_path_X_to_hinge=round(cx, 2),
            heat_path_X_to_tail=round(PCB_L - cx, 2),
            board_area=PCB_L * PCB_W_NEW,
            device_land=area[k]["device_land"],
            free_area_per_side=round((PCB_L * PCB_W_NEW) - area[k]["device_land"], 1),
            graphite_weight_old=round(g_old, 3),
            graphite_weight_new=round(g_new, 3),
            skeleton_weight_full=round(w_full, 3),
            skeleton_weight_step=round(w_step, 3),
            skeleton_soc_seg_len=round(soc_seg, 2),
            skeleton_step_note=f"SoC 段 {soc_seg:.2f}mm 满板宽 + 其余 {PCB_L - soc_seg:.1f}mm 宽 {SKEL_REST_W:.0f}mm",
        )
        chk(f"{soc['name']} 散热输入已就绪 (只给输入, 不算皮肤温度)", True,
            f"SoC 顶面投影 {pkg_w * pkg_h:.0f}mm² / 横向铜箔通道 {lat_ch:.2f}mm/边 "
            f"(扣逃线带余 {usable_side:.2f}mm) / Y 向路径 {min(cy, PCB_W_NEW - cy):.2f}mm / "
            f"X 向 {cx:.1f}+{PCB_L - cx:.1f}mm",
            "★ 这些是 mech 热模型的输入; 皮肤温度仍由 mech 用本项目的 R_皮肤/R_隔热 模型算, 本单不越界")
        chk(f"{soc['name']} 石墨片重量 (Y 向覆盖 15→30mm)", True,
            f"{g_old:.2f}g/片 → {g_new:.2f}g/片 (+{g_new - g_old:.2f}g)",
            "石墨 V 向覆盖必须跟板宽一起加, 否则 SoC 横向扩散通道白加")
        chk(f"{soc['name']} 金属骨架重量 (满宽 / 台阶形)", True,
            f"满宽 60×30×1.0 铝 = {w_full:.2f}g/侧 ({w_full * 2:.2f}g/对); "
            f"台阶形 (SoC 段 {soc_seg:.1f}mm 满宽 + 其余 {SKEL_REST_W:.0f}mm 宽) = {w_step:.2f}g/侧 "
            f"({w_step * 2:.2f}g/对) vs MECH_BUDGET §2.4 B '+1-3g'",
            f"★ 满宽形在 30mm 宽下 **判死得更彻底** (旧 15mm 满宽已 4.86g/对 判死); "
            f"台阶形 {w_step * 2:.2f}g/对 仍超 MECH 口径 "
            f"{max(0.0, w_step * 2 - 3.0):.2f}g ⇒ 截面形状是 mech 的决策, 本单只给数字")
    return out


# =====================================================================
def main() -> int:
    socs = {"RK3588": SOC_RK3588, "RK3576": SOC_RK3576}
    print("=" * 102)
    print("ISS-118 板宽 15→30mm 硬件连带重算 | 板框 60×30 | RK3588 / RK3576 两版")
    print("=" * 102)

    s1 = sec1()
    print("\n【① 板框 / 板重 / 镜脚 V 向余量】")
    for tag, v in s1.items():
        print(f"  {tag}: 面积 {v['area']:.0f}mm² | 裸板重 {v['weight_6l_g']:.2f}g(6L)/{v['weight_4l_g']:.2f}g(4L)"
              f" | PCB段V {v['v_pcb']:.2f} → V余量 {v['v_margin']:+.2f} (最坏 {v['v_margin_worst']:+.2f})"
              f" | L余量 {v['l_margin']:+.2f}")

    esc = sec2(socs)
    print("\n【② 逃线带 / 逃线深度 → 层数】")
    for k, v in esc.items():
        print(f"  {socs[k]['name']}: p={socs[k]['pitch']} | 单排逃线带 {v['band_1row']:.2f}mm/边 | "
              f"同排过孔净间隙 {v['same_row_via_clear']:.3f} | 阵列 {socs[k]['arr_x']}×{socs[k]['arr_y']} "
              f"⇒ 逃线深度 {v['rows_deep']} 圈 ⇒ 需 {v['signal_layers_needed']} 布线层 + 2 参考面 "
              f"= {v['total_layers_needed']} 层 ({'✅ ≤6' if v['fits_4_6_layer'] else '❌ 破 4-6 层锁死'})"
              f" | 30mm 宽下边带只够排 {v['rows_escapable_in_edge']} 排")

    area = sec3(socs, esc)
    print("\n【③ 面积账 (60×30 = 1800mm²) —— 台账】")
    for k, v in area.items():
        print(f"  ▸ {socs[k]['name']}: 器件占位 {v['device_land']:.1f} + SoC 逃线框 {v['soc_escape_frame']:.1f} "
              f"= land {v['land_total']:.1f}mm² (占板面 {v['land_fraction'] * 100:.1f}%)")
        for nm, vv, _ in v["items"]:
            print(f"        {vv:>8.1f}  {nm}")
        print(f"      需板面积: 双面贴 0.72 → {v['need_2side']:.0f}mm² {v['verdict_2side']} | "
              f"单面贴 0.60 → {v['need_1side']:.0f}mm² {v['verdict_1side']} | "
              f"最乐观 0.78 → {v['need_optimistic']:.0f}mm² {v['verdict_optimistic']}")
        print(f"      板宽 30 时需板长: 0.72 口径 {v['need_len_at_w30']:.1f}mm | "
              f"0.78 口径 {v['need_len_at_w30_optimistic']:.1f}mm (上限 {v['max_board_len']:.1f}mm)")

    holes = sec4(socs, esc)
    print("\n【④ 定位孔位 (PIN-SET-2 @60×30) —— 2D 重叠复算】")
    for k, v in holes.items():
        print(f"  ▸ {socs[k]['name']}: SoC 封装 X{v['soc_pkg'][0]:.2f}..{v['soc_pkg'][1]:.2f} "
              f"Y{v['soc_pkg'][2]:.2f}..{v['soc_pkg'][3]:.2f} | 逃线带 "
              f"X{v['escape_band'][0]:.2f}..{v['escape_band'][1]:.2f} "
              f"Y{v['escape_band'][2]:.2f}..{v['escape_band'][3]:.2f}")
        for hk, h in v["holes"].items():
            print(f"      {hk} ({h['x']:.2f},{h['y']:.2f}) ⌀{h['d']:.2f}: 压逃线带 {h['ov_escape_band']:.3f}mm² | "
                  f"压封装 {h['ov_pkg']:.3f}mm² | 压J_CHG {h['ov_jchg_keepout']:.3f}mm² | "
                  f"孔心距边 {h['edge_to_center']:.2f}mm")

    hinge = sec5()
    print("\n【⑤ 跨铰链连接器排布复核】")
    print(f"  54 触点 @0.5mm = {hinge['pad_row_sum']:.2f}mm "
          f"(真义: 铰链区 FPC 竖向堆叠) vs 净高 {HINGE_NET_HEIGHT:.1f} → 余 {hinge['stack_margin_vs_37']:.2f}mm "
          f"【板宽无关】")
    print(f"  PCB 侧单排焊盘 {hinge['pad_row_sum']:.2f}+边距 = {hinge['pcb_single_row_need']:.2f}mm ⇒ "
          f"15mm 板宽 {'✅' if hinge['pcb_fits_15mm'] else '❌'} / 30mm 板宽 {'✅' if hinge['pcb_fits_30mm'] else '❌'}")
    print(f"  沿 X 展开: 最宽一条 {hinge['widest_row']:.2f}+边距 = {hinge['widest_row_with_keepout']:.2f}mm")

    th = sec6(socs, esc, area)
    print("\n【⑥ 散热模型输入 (只给输入)】")
    for k, v in th.items():
        print(f"  ▸ {socs[k]['name']}: 顶面投影 {v['soc_top_pad_projection']:.0f}mm² | "
              f"横向铜箔通道 {v['lateral_copper_channel']:.2f}mm/边 (扣逃线带 {v['lateral_usable_after_escape']:.2f}) | "
              f"路径 Y {v['heat_path_Y_to_edge']:.2f} X {v['heat_path_X_to_hinge']:.1f}+{v['heat_path_X_to_tail']:.1f}mm")
        print(f"      石墨 {v['graphite_weight_old']:.2f}→{v['graphite_weight_new']:.2f}g | "
              f"骨架 满宽 {v['skeleton_weight_full']:.2f}g/侧 / 台阶 {v['skeleton_weight_step']:.2f}g/侧")

    n_fail = sum(1 for c in CHECKS if not c["ok"] and c.get("level", "fail") == "fail")
    n_warn = sum(1 for c in CHECKS if not c["ok"] and c.get("level") == "warn")
    res = {
        "issue": "ISS-118",
        "board": {"L": PCB_L, "W_old": PCB_W_OLD, "W_new": PCB_W_NEW,
                  "area_new": PCB_L * PCB_W_NEW},
        "sec1_frame_weight_cavity": s1,
        "sec2_escape": esc,
        "sec3_area": area,
        "sec4_holes": holes,
        "sec5_hinge": hinge,
        "sec6_thermal_inputs": th,
        "checks": CHECKS,
        "fail": n_fail, "warn": n_warn, "total": len(CHECKS),
    }
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)

    print("\n【逐条复算】")
    for c in CHECKS:
        mark = "✅" if c["ok"] else ("❌" if c.get("level", "fail") == "fail" else "⚠️")
        print(f"  {mark} {c['name']}: {c['detail']}")
    print(f"\n【汇总】 {len(CHECKS) - n_fail - n_warn}/{len(CHECKS)} 通过, FAIL {n_fail}, WARN {n_warn}")
    print(f"  JSON -> {OUT_JSON}")
    print("=" * 102)
    return 1 if n_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
