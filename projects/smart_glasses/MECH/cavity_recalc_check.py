#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-209 机器门禁 —— 镜框正中区光学腔体按眼盒硬约束重排 (d × A_e 参数化)

交卷人: 结构总工 (mech-lead, 带散热) 🔩 · 2026-11-15 · 单号 ISS-209
交卷件: MECH/CENTER_CAVITY_RECALC.md (参数化重排表 + 冲突量化)
本脚本: **本单每一个 mm / mm² / g / °C 数字的唯一来源** —— 文档里的数不许手算,
        全部由本脚本算出来, 门禁再把文档回读逐格比对 (改一个数立刻变红)。

用法:
    python3 MECH/cavity_recalc_check.py             -> rc=0 全过 / rc=1 并点名是哪一条
    python3 MECH/cavity_recalc_check.py --selftest  -> rc=0, >=5 个反向用例全被抓
    python3 MECH/cavity_recalc_check.py --emit-rows -> 打印 9 行参数表 (生成文档用)

边界:
  * 本脚本**只读** MECH_BUDGET.md / CENTER_CAVITY_RECALC.md / 判据文件 / 分片, 不写任何文件
    (--selftest 只在临时目录里做副本, 真文件一个字节不动)
  * 本单 [实测] 实物 = 0 条 (本机无样件/无量具) —— 全部几何数 = [推算], 出处见 CENTER_CAVITY_RECALC.md §0
  * 本脚本**不判**波导归属 / 屏路线 / FOV (老板级), 只落参数化占位与冲突量
"""
from __future__ import annotations

import argparse
import hashlib
import math
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

# ======================================================================
# §0 常量 —— 全部有出处 (MECH/CENTER_CAVITY_RECALC.md §0 同一张表)
#     只引用, 不许改判据阈值 (62 / 15-20 / 0.1234 / 1500 / 4000 / 50C / 60C)
# ======================================================================
AE_MAX_MM2 = 62.0          # MECH_BUDGET §1.7 X-1 (V2 C-4/C-5)
D_LIST_MM = (15.0, 18.0, 20.0)   # §1.7 X-2 评估距离 d (V2 §3 ⑤-b; 同类公开 18mm)
AE_LIST_MM2 = (25.0, 40.0, 62.0)
EPS_BAND_MM = 3.0          # V2 §3 ⑤ 降级方案: 出瞳面可前后调 ±3 mm
T_OLD_MM = 11.8            # §1.4.5 正中区旧数 (走鹃Ⅱ 口径, 已作废, 只报不改)
T_TGT_LO_MM = 10.0         # §1.4.5 镜框厚度汇总: 上沿区 >=10-12mm
T_TGT_HI_MM = 12.0

# 器件区占位 (§1.4.5 正中区分解 / §1.3 M5·M6)
TC_MM = 4.8                # 耦合光学轴向占用 (占位, 走鹃Ⅱ 光机口径 → 仅作量级占位)
TS_MM = 6.0                # 分光件轴向占用 (§1.3 M6 ~14×10×6, 含 2 转向棱镜)
MARGIN_MM = 1.0            # 装配余量 (§1.4.5)

# 面板 (现行口径, 视涯 0.49" SiOLED)
PANEL_W_MM = 10.783
PANEL_H_MM = 6.065
AP_MM2 = PANEL_W_MM * PANEL_H_MM          # 65.40 mm² 有效显示面积

# 分光件 (§1.3 M6 / §1.2 推算)
SPL_W_MM = 14.0
SPL_H_MM = 10.0
SPL_PLATE_MM = 10.0        # 45° 半透半反平板 10×10×1.5 (§1.2)
SPL_PLATE_T_MM = 1.5
SPL_PRISM_MM = 8.0         # 转向棱镜 8×8×5 ×2 (§1.2)
SPL_PRISM_T_MM = 5.0
SPL_V_CC = 0.79            # §1.3 M6 分光组件体积
SPL_W4_G_LO, SPL_W4_G_HI = 3.0, 6.0       # §3 W4 重量带
GLASS_RHO_G_CC = 2.5       # §3 W4 玻璃密度 2.5 g/cc

# 重量 (§3 W9)
FRAME_WALL_MM = 1.2        # §3 W9 镜框 1.2mm 壁
PA_CF_RHO_G_CC = 1.2       # [推算·通用] 3D 打印 PA-CF 实体密度
W9_LO_G, W9_HI_G = 9.0, 14.0

# 鼻梁区热 (MECH/STRUCT_REVIEW_ISS065.md §2.3 输入)
NOSE_L_MM = 12.0           # L_bridge 节点→鼻梁接触面
NOSE_A_MM2 = 150.0         # A_bridge
K_PRINT = 0.2              # 打印件 k (W/m·K)
A_NOSE_MM2 = 140.0         # A_nose 鼻梁接触面积 [0数据·u8 未定]
A_CONV_MM2 = 1000.0        # A_conv 镜框正中段外露对流面 [0数据·u8 未定]
H_SKIN = 75.0              # W/m²K
H_CONV = 10.0              # W/m²K
T_BASE_C = 35.0            # 环境+体温基准
P_SOC_W = 0.55             # SoC 域发热 (ISS-065 §2.3, ISS-055 修正后)
P_PANEL_W = 0.468          # 面板 468 mW (V2 §3 ③-d datasheet)
R_BREAK_KW = 1000.0        # 鼻梁侧热断 (ISS-065 B5)
R_BREAK_MIN_KW = 578.0     # 保 43°C 所需最小 R_bridge (ISS-065 反解表)

# 装配判据 (本项目通用)
FIT_JUDGE_MM = 0.60        # FDM 单边公差 ×2 的通用判据

# 受保护文件 md5 (本单不许动)
MD5_EXPECTED = {
    "MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md": "96239070dc7c0ec00edb1b758a698769",
    "MECH/hinge_usb_check.py": "3425bc141508de8a35f34c7cf7b803e8",
    "MECH/service_port_check.py": "9b24bf985764880f0105aee677fba6a8",
    "MECH/hw_cross_review_check.py": "e521387b87b0fcdf9f22d56f14199967",
    "MECH/display_biosafety_v2_check.py": "29c77fc3fc823048b1d96c9500d28dd7",
}

DOC_REL = "MECH/CENTER_CAVITY_RECALC.md"
BUDGET_REL = "MECH/MECH_BUDGET.md"
FRAG_REL = "state/fragments/mech.yaml"

# ======================================================================
# §0b ★ISS-219 (2026-11-16) 新增常量 —— 第 2 轮重排 (C-6 / C-7 / C-C / X-3 / k=201)
# ======================================================================
V2_REL = "MECH/CENTER_CAVITY_REBALANCE_V2.md"
VB_REL = "MECH/verify_budget.py"
ENDPOINT_REL = "MECH/ENDPOINT_METAL_PATH_MASS_TEMPLATE.md"

# ---- 金属热路材料 (ISS-219 订正: 237 → 201 官方保守侧) ----
K_AL_6063_T6 = 201.0          # W/m·K [官网] Hydro EN AW-6063 'Hydro 6063_Rev.4 – 03/2023' (T6 = 201)
K_AL_6063_T6_LEGACY = 237.0   # W/m·K [旧口径·已订正] 只留追溯, 不许当活口径
RHO_AL_G_MM3 = 2.70e-3        # g/mm³ [官网] 2.70 g/cm³
R_PATH_MAX_KW = 70.0          # K/W [推算] ISS-216 §3 注 / ISS-218 §1.1 硬指标

# ---- 尺 B (ISS-213/ISS-216/ISS-218 口径): 集热面对流 R = 1/(10 W/m²K × A[mm²]) ----
R_COL_KW_NUM = 100000.0       # ⇒ R_conv = 100000 / A[mm²]
ENDPOINT_COL_W_MM = 20.0      # 端件截面另一边 (ISS-213 几何 30×20; V 高 = u8)

# ---- TIM 占位 (通用导热垫) ----
TIM_T_MM = 0.2                # mm [推算·通用]
TIM_K = 6.0                   # W/m·K [推算·通用]

# ---- 判据 (只引用, 一个字不许改) ----
T_CAV_LIMIT_C = 50.0          # °C X-3 腔体红线
T_COL_LIMIT_C = 60.0          # °C 端件外表面判据 (ISS-216)
H_CONV_COL = 10.0             # W/m²K [推算] 集热面对流
P_COL_05W = 0.50              # W [推算] ISS-216 代表值
T_AMBIENT_COL = 35.0          # °C [推算] 基准 (与 T_BASE_C 同)

# ---- u8 情景 (ISS-218 沿用) ----
U8_LIST_MM = (30.0, 33.0, 35.0, 38.0, 40.0)

# ---- C-7 三条候选 (金属段: 铝 6063-T6, k=201) ----
CAND_V2 = [
    dict(cid="P1", name="细铝条 4×3 + 仅端件集热", am=12.0, L=50.0),
    dict(cid="P2", name="粗铝条 6×5 + 端件 + 框上沿局部带", am=30.0, L=50.0),
    dict(cid="P3", name="粗铝条 6×5 + 镜框上沿大面集热", am=30.0, L=50.0),
]
# 集热面构成 (端件 u8×20 + 框上沿带)
SINK_BAND_MM2 = {"P1": 0.0, "P2": 50.0 * 30.0, "P3": 120.0 * 30.0}


def sink_area_mm2(cid: str, u8: float) -> float:
    """候选 cid 在 u8 下的集热面总面积 (mm²)"""
    return u8 * ENDPOINT_COL_W_MM + SINK_BAND_MM2[cid]


# ======================================================================
# §0c ★ISS-222 (2026-11-16) 新增常量 —— 第 3 轮落地 (C-6 落表 / C-7 实算 / C-8 轴向口径)
#     依据: MECH/CENTER_CAVITY_REBALANCE_V3.md §0 (口径声明 + 常量表)
# ======================================================================
V3_REL = "MECH/CENTER_CAVITY_REBALANCE_V3.md"

# ---- C-6 落地规格 (ISS-222 把 ISS-209/219 的新口径写进 §1.3 M6) ----
SPL_PLATE_A_V3 = 11.0       # 45° 半透半反平板边长 (C-6)
SPL_PLATE_T_V3 = 1.5     # 平板厚
SPL_PRISM_A_V3 = 9.0     # 转向棱镜边长 (C-6)
SPL_PRISM_T_V3 = 5.0     # 转向棱镜厚
SPL_V_CC_V3 = 0.9697       # 分光组件体积 (连续口径) [推算]
SPL_V_CC_V3_ENG = 0.9915    # 工程取值 (11×11×1.5 + 2×9×9×5)
SPL_W4_V3_LO, SPL_W4_V3_HI = 3.68, 7.36   # §3 W4 新带 (连续口径)

# ---- C-8 轴向口径 (45° 平板的轴向投影) ----
S45 = math.sin(math.radians(45.0))
C45 = math.cos(math.radians(45.0))
#: ★轴向口径 t_s = 边长·sin45° + 板厚·cos45° (任何左右分光构型都成立)
TS_AXIAL_MM = SPL_PLATE_A_V3 * S45 + SPL_PLATE_T_V3 * C45
TS_PLATE_PROJ_MM = SPL_PLATE_A_V3 * S45          # 不含板厚贡献 (偏乐观)
TS_LEGACY_MM = 6.0                                # 旧口径 (M6 包络第三维)
TS_V2_VERTICAL_MM = 11.0                          # ISS-219 §2.5 口径 (竖向 = 边长)
TS_WITH_PRISM_MM = TS_AXIAL_MM + SPL_PRISM_T_V3   # + 转向棱镜串在轴向链上
#: 器件区 = t_c (4.8) + t_s + 装配余量 (1.0);  可动余量 = T - 器件区 - ±3 带双向行程 (6.0)
TS_STACK_TC_MM = 4.8
TS_STACK_MARGIN_MM = 1.0
BAND_TRAVEL_MM = 2.0 * EPS_BAND_MM               # 6.0 mm

# ---- C-7 集热面 (镜框上沿外表面) ----
SINK_LX_MM = 120.0        # 沿 X 长度 (框宽 ~140 - 端件/铰链区 2×10) [推算·占位]
SINK_WRIM_MM = 30.0       # 沿 Y (前后) 宽 [0数据·框截面未定义]
CAM_BUMP_X_MM = 14.0      # 摄像头位局部加高凸包 沿 X 占位
CAM_BUMP_Y_MM = 12.0      # 摄像头位局部加高凸包 沿 Y 占位 (加厚带 10.11-10.41)
DECOR_AREA_MM2 = 0.0      # 装饰件 (包胶/铭牌) [0数据] ⇒ 不扣, 留风险
# 打印件 (PA-CF) 沿上沿的传导参数 [推算·通用]
K_PRINT_RIM = 0.2         # W/m·K
RIM_WALL_MM = 1.2         # 打印件壁厚 (§3 W9)
RIM_HEIGHT_MM = 10.4      # 上沿竖向高 (摄像头位垂直净高 ≥10.36 mm, ISS-052 B3.2)
RIM_WALLS_N = 4           # 上下左右四面壁并联
# 铝制集热背板 (降级路径 a)
BACKPLATE_T_MM = 1.0
BACKPLATE_M_G = SINK_LX_MM * SINK_WRIM_MM * BACKPLATE_T_MM * RHO_AL_G_MM3
# 端件整条金属化 (降级路径 c) —— ENDPOINT 模板 表 A 的质量区间
ENDPOINT_FULL_MASS_LO, ENDPOINT_FULL_MASS_HI = 11.34, 22.68
# 面板功耗降档 (降级路径 b)
P_PANEL_LOW_W = 0.415


# ======================================================================
# §0d ★ISS-227 (2026-11-16) 新增常量 —— C-7b 集热面口径修正 + 三档重算
#     依据: MECH/CENTER_CAVITY_REBALANCE_V3.md §2.5 (口径修正独立节)
#     ★★本节改的是【假设/口径】(集热面材质), 不是【阈值】:
#        腔体 50 °C / 鼻梁 43 °C / 端件 60 °C / k=201 / P3 几何 120×30 一个不许动
# ======================================================================

#: ★活口径的集热面材质 —— 必须【金属】。打印件 (PA-CF) 顶面是「名义面积」(假同温):
#: 沿上沿热阻 3610 K/W ⇒ 有效热导 R=57.12 K/W vs 同面积直接对流 47.6 K/W (差 8.4 倍)
#: ⇒ 实算腔体 53.60 °C ❌ (ISS-222 §2.3) ⇒ 打印件顶面**不许**被当成集热面。
SINK_SURFACE_MATERIAL = "aluminum"              # ★活口径: 铝制集热背板 120×30×1.0
SINK_SURFACE_MATERIAL_CN = "铝 6063-T6"           # 中文名 (写进文档 + 门禁回读)

#: 集热面材质白名单 (金属) —— 判据「打印件顶面不许被当成集热面」的**机械判据**
SINK_SURFACE_METAL_ALLOWED = ("aluminum", "aluminium", "metal", "copper", "magnesium", "steel")

#: ★已作废口径 (只许留痕, 不许当活口径)
SINK_SURFACE_MATERIAL_LEGACY = "print"           # 打印件 PA-CF 顶面 (假面积)

#: 打印件关键词 —— 出现在【活口径】的材质格里 ⇒ 门禁红
PRINT_MATERIAL_KEYWORDS = ("打印", "PA-CF", "PA_CF", "ABS", "塑料", "print", "FDM")

#: 金属关键词 —— 出现在【活口径】的材质格里才放行
METAL_MATERIAL_KEYWORDS = ("铝", "金属", "metal", "aluminum", "aluminium", "copper", "镁")

#: C-7b 三档重算的 d (判据 §1.7 X-2, 只引用, 一个不许动)
C7B_D_LIST_MM = (15.0, 18.0, 20.0)

#: C-7b 三档重算的 u8 口径 (端件截面 V 高; ISS-218 沿用) —— 主口径取**保守端**
C7B_U8_MAIN_MM = 30.0
C7B_U8_HI_MM = 40.0

#: C-7b 活口径背板几何 (P3 几何 120×30, 一个不许动)
C7B_BACKPLATE_GEOM = (120.0, 30.0, 1.0)        # 长 × 前后宽 × 厚 (mm)


# ======================================================================
# §0e ★ISS-237 (2026-11-16 · 闭环轮) 新增常量 —— C-7c:
#     「镜框上沿前后宽 W_rim」这个 C-7 的唯一前置, 用**活口径** (鳍模型) 重新实算门槛
#     + 集热背板的质量账 + 整机重量影响
#     依据: MECH/CENTER_CAVITY_REBALANCE_V3.md §2.6
#     ★★改的是【口径的适用范围】(门槛在哪个功耗下成立), 不是【阈值】:
#        腔体 50 °C / k=201 / 120×30×1.0 / 0.468 W / 0.50 W 一个不许动
# ======================================================================

#: C-7c 的 W_rim 扫描点 (mm) —— ① 面板功耗门槛点 ② ISS-222 已登记的 23.30
#:   ③ 0.50 W 代表负载门槛点 ④ 现占位 30.00 (30 mm 本身在项目内查无出处)
C7C_W_LIST_MM = (22.15, 23.30, 25.63, 30.00)

#: C-7c 的 u8 口径 (端件截面 V 高) —— 沿用 ISS-227 的主口径 30 (保守端)
C7C_U8_MM = 30.0

#: 整机重量锚点 (ISS-222 C-6 落地后的 §3 合计, 387 mAh 配置) —— 只引用, 一个数不许改
C7C_DOC_WEIGHT = (50.78, 75.36)

#: 摄像头凸包占位 (mm²) —— 与 C-7 / C-7b 活口径共用 (不在本节新造)


# ======================================================================
# §1 计算 —— 文档里所有数都从这里出来
# ======================================================================
def compute() -> dict:
    dp = math.sqrt(4.0 * AP_MM2 / math.pi)          # 面板等效直径
    stack = TC_MM + TS_MM + MARGIN_MM                # 器件区 (旧口径串联占位)
    assert abs(stack - T_OLD_MM) < 1e-9, "器件区占位必须等于 §1.4.5 的 11.8"
    band_travel = 2.0 * EPS_BAND_MM                  # 出瞳面 ±3 mm 双向行程

    rows = []
    for d in D_LIST_MM:
        for ae in AE_LIST_MM2:
            de = math.sqrt(4.0 * ae / math.pi)        # 眼盒等效直径
            m_ratio = de / dp                          # 中继放大率 = FOV 折减系数
            t_band = d + EPS_BAND_MM                   # 含 ±3 带的腔体深度需求
            slack = t_band - stack - band_travel       # 可动余量
            delta_hi = t_band - T_TGT_HI_MM            # vs 目标上沿 12
            delta_lo = t_band - T_TGT_LO_MM            # vs 目标下沿 10
            delta_old = t_band - T_OLD_MM              # vs 旧数 11.8 (本单预算口径)
            c1 = d - T_OLD_MM                          # §1.7.1 C-1 同口径冲突量
            # 镜框重量增量: 正中区块加厚 Δ 处的侧壁材料
            depth_growth = t_band - T_OLD_MM
            add_cc = depth_growth * (2.0 * (SPL_W_MM + SPL_H_MM)) * FRAME_WALL_MM / 1000.0
            w_frame_g = add_cc * PA_CF_RHO_G_CC
            # 判定
            over_target = delta_hi > 0.0
            fit_ok = slack >= FIT_JUDGE_MM
            if over_target or not fit_ok:
                verdict = "超差" + ("" if fit_ok else "·装配不可行")
            else:
                verdict = "可行"
            rows.append(dict(
                d=d, ae=ae, de=de, dp=dp, m_ratio=m_ratio,
                fov_loss_pct=(1.0 - m_ratio) * 100.0,
                panel_margin_mm=dp - de,
                tc=TC_MM, ts=TS_MM, margin=MARGIN_MM, stack=stack,
                t_band=t_band, slack=slack,
                delta_hi=delta_hi, delta_lo=delta_lo, delta_old=delta_old, c1=c1,
                band_travel=band_travel,
                w_frame_g=w_frame_g,
                w9_lo=W9_LO_G + w_frame_g, w9_hi=W9_HI_G + w_frame_g,
                eye_ok=(ae <= AE_MAX_MM2),
                verdict=verdict,
                evidence="[推算]",
                source="X-1/X-2 + §1.4.5 + V2 C-4/C-5",
            ))

    # 分光件随眼盒重算 (光束口径必须 >= 眼盒)
    splitter = {}
    for ae in AE_LIST_MM2:
        de = math.sqrt(4.0 * ae / math.pi)
        diag_legacy = de / math.sin(math.radians(45.0))      # §1.2 的推算式
        diag_strict = de * math.sqrt(3.0)                    # 矩形包含 (严格)
        side = de * math.sqrt(3.0 / 2.0)                     # 正方形平板最小边长
        plate_cc = side * side * SPL_PLATE_T_MM / 1000.0
        p_side = max(SPL_PRISM_MM, math.ceil(de * 10.0) / 10.0)
        prism_cc = p_side * p_side * SPL_PRISM_T_MM / 1000.0
        total_cc = plate_cc + 2.0 * prism_cc
        dv = total_cc - SPL_V_CC
        dm_glass = dv * GLASS_RHO_G_CC
        w4_lo = SPL_W4_G_LO * total_cc / SPL_V_CC
        w4_hi = SPL_W4_G_HI * total_cc / SPL_V_CC
        splitter[ae] = dict(
            de=de, diag_legacy=diag_legacy, diag_strict=diag_strict, side=side,
            plate_cc=plate_cc, prism_cc=prism_cc, total_cc=total_cc,
            dv_cc=dv, dm_glass_g=dm_glass, w4_lo=w4_lo, w4_hi=w4_hi,
            plate_fits_legacy=diag_legacy <= SPL_PLATE_MM * math.sqrt(2.0),
            plate_fits_strict=diag_strict <= SPL_PLATE_MM * math.sqrt(2.0),
        )

    # 鼻梁区热 (ISS-065 §2.3 模型, 功耗输入换成现行 468 mW 面板)
    r_interface = 1.0 / (H_SKIN * A_NOSE_MM2 * 1e-6)
    r_bridge = (NOSE_L_MM * 1e-3) / (K_PRINT * NOSE_A_MM2 * 1e-6)   # L 换算成 m ⇒ 400 K/W
    r_skin_branch = r_bridge + r_interface

    def nose_case(p_w: float, a_conv: float, r_br: float) -> dict:
        r_amb = 160000.0 / a_conv                       # ISS-065: A_conv=1000 ⇒ 160 K/W
        r_eff = 1.0 / (1.0 / r_skin_branch + 1.0 / r_amb)
        t_node = T_BASE_C + p_w * r_eff
        q_skin = (t_node - T_BASE_C) / (r_br + r_interface)
        t_patch = T_BASE_C + q_skin * r_interface
        return dict(r_amb=r_amb, r_eff=r_eff, t_node=t_node, q_skin_w=q_skin,
                    t_patch=t_patch, r_bridge=r_br)

    def r_bridge_min(p_w: float, a_conv: float, t_limit: float = 43.0) -> float:
        """求让鼻梁接触面 <= t_limit 所需的最小 R_bridge (二分)"""
        lo, hi = 1.0, 100000.0
        for _ in range(200):
            mid = (lo + hi) / 2.0
            if nose_case(p_w, a_conv, mid)["t_patch"] > t_limit:
                lo = mid
            else:
                hi = mid
        return hi

    thermal = []
    for d in D_LIST_MM:
        t_band = d + EPS_BAND_MM
        depth_growth = t_band - T_OLD_MM
        a_conv = A_CONV_MM2 + (2.0 * (SPL_W_MM + SPL_H_MM)) * depth_growth
        p_total = P_SOC_W + P_PANEL_W
        case = nose_case(p_total, a_conv, r_bridge)
        case_break = nose_case(p_total, a_conv, R_BREAK_KW)
        case_panel_only = nose_case(P_PANEL_W, a_conv, r_bridge)
        # 保 43°C 允许的最大功耗 (带热断)
        r_eff_break = 1.0 / (1.0 / (R_BREAK_KW + r_interface) + 1.0 / case_break["r_amb"])
        p_max = (43.0 - T_BASE_C) / (r_eff_break * r_interface / (R_BREAK_KW + r_interface))
        thermal.append(dict(
            d=d, a_conv=a_conv, p_total=p_total,
            r_bridge=r_bridge, r_interface=r_interface, r_skin_branch=r_skin_branch,
            t_patch_pcb=case["t_patch"], t_node_pcb=case["t_node"],
            t_patch_pcb_break=case_break["t_patch"],
            t_patch_panel_only=case_panel_only["t_patch"],
            t_cavity_panel=case_panel_only["t_node"],
            p_max_with_break=p_max,
            r_bridge_min_panel=r_bridge_min(P_PANEL_W, a_conv, 43.0),
            r_bridge_min_pcb=r_bridge_min(p_total, a_conv, 43.0),
            margin_pcb=case["t_patch"] - 43.0,
            margin_break=case_break["t_patch"] - 43.0,
        ))

    # 腔体 50°C 红线所需被动散热面 (X-3)
    cavity_req = []
    for th in thermal:
        r_amb = th["a_conv"] and 160000.0 / th["a_conv"]
        r_eff_max = (50.0 - T_BASE_C) / P_PANEL_W
        inv_amb = 1.0 / r_eff_max - 1.0 / r_skin_branch
        r_amb_req = 1.0 / inv_amb
        a_req = 160000.0 / r_amb_req
        cavity_req.append(dict(d=th["d"], a_conv=th["a_conv"], a_req=a_req,
                               t_cavity=th["t_cavity_panel"]))

    return dict(rows=rows, splitter=splitter, thermal=thermal, cavity=cavity_req,
                dp=dp, ap=AP_MM2, stack=stack, band_travel=band_travel,
                r_bridge=r_bridge, r_interface=r_interface)


def compute_v2(c: dict | None = None) -> dict:
    """★ISS-219: 第 2 轮重排的全部数 (C-6 分光件 / C-7 散热出路 / 鼻梁 R_bridge 反解 / k=201)。

    沿用 ISS-209 的尺 A (腔体节点网络, h_eff=6.25 ⇒ 160000/A) + ISS-218 的尺 B
    (集热面/金属段, h=10 ⇒ 100000/A + R_热路 ≤ 70 K/W) —— 两把尺各用各的域, 不混算。
    """
    if c is None:
        c = compute()
    r_sb = c["r_bridge"] + c["r_interface"]          # 495.238 K/W (ISS-065 口径, 不改)
    a_conv_by_d = {t["d"]: t["a_conv"] for t in c["thermal"]}

    # ---------------- C-6: 分光件随眼盒重算 (第 2 轮新规格) ----------------
    spl2 = {}
    for ae in AE_LIST_MM2:
        de = math.sqrt(4.0 * ae / math.pi)
        diag_legacy = de / math.sin(math.radians(45.0))
        diag_strict = de * math.sqrt(3.0)
        side = de * math.sqrt(3.0 / 2.0)
        p_side = math.ceil(de * 10.0) / 10.0
        plate_cc = side * side * SPL_PLATE_T_MM / 1000.0
        prism_cc = p_side * p_side * SPL_PRISM_T_MM / 1000.0
        total_cc = plate_cc + 2.0 * prism_cc
        # 工程取值 (可加工整数尺寸)
        plate_i = int(math.ceil(side))
        prism_i = int(math.ceil(p_side))
        eng_cc = plate_i * plate_i * SPL_PLATE_T_MM / 1000.0 \
            + 2.0 * prism_i * prism_i * SPL_PRISM_T_MM / 1000.0
        spl2[ae] = dict(
            de=de, diag_legacy=diag_legacy, diag_strict=diag_strict, side=side,
            plate_i=plate_i, plate_diag=plate_i * math.sqrt(2.0),
            prism_i=prism_i,
            total_cc=total_cc, dv_cc=total_cc - SPL_V_CC, eng_cc=eng_cc,
            w4_lo=SPL_W4_G_LO * total_cc / SPL_V_CC,
            w4_hi=SPL_W4_G_HI * total_cc / SPL_V_CC,
            m_ratio=de / c["dp"],
        )

    # ---------------- C-7: 三条散热出路候选 ----------------
    cand = {}
    for cfg in CAND_V2:
        am, L, cid = cfg["am"], cfg["L"], cfg["cid"]
        r_metal = (L * 1e-3) / (K_AL_6063_T6 * am * 1e-6)
        r_metal_leg = (L * 1e-3) / (K_AL_6063_T6_LEGACY * am * 1e-6)
        r_tim = (TIM_T_MM * 1e-3) / (TIM_K * am * 1e-6)
        cand[cid] = dict(
            cid=cid, name=cfg["name"], am=am, L=L,
            r_metal=r_metal, r_tim=r_tim, r_path=r_metal + r_tim,
            r_path_leg=r_metal_leg + r_tim,
            dt468=P_PANEL_W * (r_metal + r_tim),
            dt50=P_COL_05W * (r_metal + r_tim),
            mass_g=RHO_AL_G_MM3 * am * L,
            ok70=(r_metal + r_tim) <= R_PATH_MAX_KW,
        )

    def cavity(d: float, p_w: float, cid: str, u8: float) -> dict:
        """腔体节点 + 集热面 (d / 功率 / 候选 / u8)"""
        a_cav = a_conv_by_d[d]
        r_amb = 160000.0 / a_cav
        ht = cand[cid]["r_path"]
        a_col = sink_area_mm2(cid, u8)
        r_conv = R_COL_KW_NUM / a_col
        r_branch = ht + r_conv
        r_eff = 1.0 / (1.0 / r_sb + 1.0 / r_amb + 1.0 / r_branch)
        t_cav = T_BASE_C + p_w * r_eff
        q_col = p_w * r_eff / r_branch
        t_col = T_BASE_C + q_col * r_conv
        # 反解: 腔体节点刚好 50 °C 时需要的集热面
        inv = p_w / (T_CAV_LIMIT_C - T_BASE_C) - 1.0 / r_sb - 1.0 / r_amb
        r_branch_req = 1.0 / inv
        a_req = R_COL_KW_NUM / (r_branch_req - ht)
        return dict(a_cav=a_cav, r_amb=r_amb, a_col=a_col, r_conv=r_conv,
                    r_branch=r_branch, r_eff=r_eff, t_cav=t_cav, t_col=t_col,
                    a_req=a_req, q_col=q_col)

    rows_t = []
    for cfg in CAND_V2:
        cid = cfg["cid"]
        for u8 in U8_LIST_MM:
            a = cavity(15.0, P_PANEL_W, cid, u8)
            b = cavity(15.0, P_COL_05W, cid, u8)
            rows_t.append(dict(cid=cid, u8=u8, a_col=a["a_col"], r_branch=a["r_branch"],
                               t_cav468=a["t_cav"], t_cav50=b["t_cav"], t_col=a["t_col"],
                               a_req=a["a_req"], ok=(a["t_cav"] <= T_CAV_LIMIT_C)))
    rows_d = []
    for cfg in CAND_V2:
        cid = cfg["cid"]
        for d in D_LIST_MM:
            a = cavity(d, P_PANEL_W, cid, U8_LIST_MM[-1])
            b = cavity(d, P_COL_05W, cid, U8_LIST_MM[-1])
            rows_d.append(dict(cid=cid, d=d, a_col=a["a_col"], r_branch=a["r_branch"],
                               t_cav468=a["t_cav"], t_cav50=b["t_cav"], t_col=a["t_col"],
                               a_req=a["a_req"], ok=(a["t_cav"] <= T_CAV_LIMIT_C)))
    rows_u8 = []
    for u8 in U8_LIST_MM:
        a = cavity(15.0, P_PANEL_W, "P3", u8)
        b = cavity(15.0, P_COL_05W, "P3", u8)
        rows_u8.append(dict(u8=u8, a_end=u8 * ENDPOINT_COL_W_MM, a_col=a["a_col"],
                            end_pct=(u8 * ENDPOINT_COL_W_MM) / a["a_col"] * 100.0,
                            t_cav468=a["t_cav"], t_cav50=b["t_cav"],
                            spl_vert=float(spl2[AE_MAX_MM2]["plate_i"]),
                            ok=(float(spl2[AE_MAX_MM2]["plate_i"]) <= u8)))

    # ---------------- k 口径对拍 ----------------
    Lg, Ag = 70.0, 180.0
    ktab = [
        dict(kid="K-01", k=K_AL_6063_T6, R=Lg * 1000.0 / (K_AL_6063_T6 * Ag),
             dt=P_COL_05W * Lg * 1000.0 / (K_AL_6063_T6 * Ag),
             a_min=Lg * 1000.0 / (K_AL_6063_T6 * R_PATH_MAX_KW), ok=True),
        dict(kid="K-02", k=K_AL_6063_T6_LEGACY, R=Lg * 1000.0 / (K_AL_6063_T6_LEGACY * Ag),
             dt=P_COL_05W * Lg * 1000.0 / (K_AL_6063_T6_LEGACY * Ag),
             a_min=Lg * 1000.0 / (K_AL_6063_T6_LEGACY * R_PATH_MAX_KW), ok=True),
        dict(kid="K-03", k=K_PRINT, R=Lg * 1000.0 / (K_PRINT * Ag),
             dt=P_COL_05W * Lg * 1000.0 / (K_PRINT * Ag),
             a_min=0.0, ok=False),
    ]

    # ---------------- 鼻梁 R_bridge 反解 (ISS-209 口径逐字沿用) ----------------
    nose = []
    for t in c["thermal"]:
        nose.append(dict(d=t["d"], r_min_panel=t["r_bridge_min_panel"],
                         r_min_pcb=t["r_bridge_min_pcb"],
                         t_patch_pcb=t["t_patch_pcb"], t_patch_panel=t["t_patch_panel_only"]))

    return dict(spl2=spl2, cand=cand, rows_t=rows_t, rows_d=rows_d, rows_u8=rows_u8,
                ktab=ktab, nose=nose, r_sb=r_sb, a_conv_by_d=a_conv_by_d)


# ======================================================================
# §1b ★ISS-222: 第 3 轮落地的全部数 (C-6 落表 / C-7 实算 / C-8 轴向口径)
# ======================================================================
def compute_v3(c: dict | None = None, cv2: dict | None = None) -> dict:
    """★ISS-222: C-6 落表 + C-8 轴向口径 (t_s) + C-7 镜框上沿可外露净集热面积。

    沿用 ISS-209 的尺 A (腔体节点网络) + ISS-218 的尺 B (集热面/金属段) —— 两把尺各用各的域。
    """
    if c is None:
        c = compute()
    if cv2 is None:
        cv2 = compute_v2(c)
    r_sb = cv2["r_sb"]                 # 495.238 K/W (ISS-065 口径, 不改)
    a_conv_by_d = cv2["a_conv_by_d"]

    # ---------------- C-6: 分光件落表 (规格 / 体积 / 重量 / FOV) ----------------
    s62 = cv2["spl2"][AE_MAX_MM2]
    c6 = dict(
        de=s62["de"], diag_strict=s62["diag_strict"],
        plate_i=SPL_PLATE_A_V3, plate_t=SPL_PLATE_T_V3,
        plate_diag=SPL_PLATE_A_V3 * math.sqrt(2.0),
        prism_i=SPL_PRISM_A_V3, prism_t=SPL_PRISM_T_V3,
        prism_margin=s62["prism_i"] and (SPL_PRISM_A_V3 - s62["de"]),
        v_cc=SPL_V_CC_V3, v_eng=SPL_V_CC_V3_ENG,
        dv_cc=SPL_V_CC_V3 - SPL_V_CC, dv_eng=SPL_V_CC_V3_ENG - SPL_V_CC,
        w4_lo=SPL_W4_V3_LO, w4_hi=SPL_W4_V3_HI,
        m_ratio=s62["m_ratio"], fov_loss=(1.0 - s62["m_ratio"]) * 100.0,
        v_sum=0.18 + SPL_V_CC_V3,
    )

    # ---------------- C-8: t_s 轴向口径 + 三档 T 的后果 ----------------
    def stack_of(ts: float) -> float:
        return TS_STACK_TC_MM + ts + TS_STACK_MARGIN_MM

    def slack_of(ts: float, t: float) -> float:
        return t - stack_of(ts) - BAND_TRAVEL_MM

    ts_cands = [
        ("TS-1", "旧口径 (M6 包络第三维 · 已作废)", TS_LEGACY_MM, False),
        ("TS-2", "45° 平板轴向投影 (不含板厚)", TS_PLATE_PROJ_MM, False),
        ("TS-3", "★轴向口径 (本单采用)", TS_AXIAL_MM, True),
        ("TS-4", "ISS-219 §2.5 口径 (竖向 = 边长 · 已作废)", TS_V2_VERTICAL_MM, False),
        ("TS-5", "轴向口径 + 转向棱镜 5mm 串在轴向链上", TS_WITH_PRISM_MM, False),
        ("TS-6", "★降级: 器件区并排化 (max(t_c, t_s) + 余量)", TS_AXIAL_MM, True),
    ]
    ts_rows = []
    for rid, name, ts, adopted in ts_cands:
        if rid == "TS-6":
            stack = max(TS_STACK_TC_MM, TS_AXIAL_MM) + TS_STACK_MARGIN_MM
        else:
            stack = stack_of(ts)
        sl = [slack_of(ts, t) if rid != "TS-6" else t - stack - BAND_TRAVEL_MM
              for t in (18.0, 21.0, 23.0)]
        ts_rows.append(dict(
            rid=rid, name=name, ts=ts, stack=stack, slack=sl,
            ok=[s >= FIT_JUDGE_MM for s in sl],
            adopted=adopted,
            all_ok=all(s >= FIT_JUDGE_MM for s in sl),
            all_dead=all(s < FIT_JUDGE_MM for s in sl),
        ))

    # ---------------- C-7: 镜框上沿可外露净集热面积 ----------------
    a_nominal = SINK_LX_MM * SINK_WRIM_MM
    a_cam = CAM_BUMP_X_MM * CAM_BUMP_Y_MM
    a_net = a_nominal - a_cam - DECOR_AREA_MM2
    # 需求 (P3 反解, 沿用 compute_v2 的 cavity())
    a_req = {r["d"]: r["a_req"] for r in cv2["rows_d"] if r["cid"] == "P3"}
    # 充要条件: 上沿前后宽 W_rim 门槛 (净面积口径)
    w_req = {d: (a_req[d] + a_cam) / SINK_LX_MM for d in a_req}

    # ---- 打印件顶面的真实热学 (C-7b: 连通性修正) ----
    # 铝条覆盖段 (50mm) 的打印顶面直接对流 + 未覆盖段按鳍处理
    bar_len_mm = 50.0
    a_base_mm2 = bar_len_mm * SINK_WRIM_MM
    r_base = R_COL_KW_NUM / a_base_mm2
    a_c_rim = 2.0 * RIM_WALL_MM * SINK_WRIM_MM + 2.0 * RIM_WALL_MM * RIM_HEIGHT_MM   # 96.96 mm²
    per_rim = SINK_WRIM_MM + 2.0 * RIM_WALL_MM            # 暴露周长 (mm)
    l_ext = (SINK_LX_MM - bar_len_mm) * 1e-3             # 延伸段长度 (m)
    m_rim = math.sqrt(H_CONV_COL * per_rim * 1e-3 / (K_PRINT_RIM * a_c_rim * 1e-6))
    g_rim = math.sqrt(H_CONV_COL * per_rim * 1e-3 * K_PRINT_RIM * a_c_rim * 1e-6) \
        * math.tanh(m_rim * l_ext)
    r_fin_rim = 1.0 / g_rim
    r_print = 1.0 / (1.0 / r_base + 1.0 / r_fin_rim)
    r_along_rim = l_ext / (K_PRINT_RIM * a_c_rim * 1e-6)   # K/W (沿上沿直流, 70mm 段)

    # ---- 铝制集热背板 (路径 a) 的鳍模型 ----
    a_c_bp = SINK_WRIM_MM * BACKPLATE_T_MM                # mm²
    per_bp = SINK_WRIM_MM                                # 只有顶面对外
    m_bp = math.sqrt(H_CONV_COL * per_bp * 1e-3 / (K_AL_6063_T6 * a_c_bp * 1e-6))
    g_bp = math.sqrt(H_CONV_COL * per_bp * 1e-3 * K_AL_6063_T6 * a_c_bp * 1e-6) \
        * math.tanh(m_bp * SINK_LX_MM * 1e-3)
    r_bp_fin = 1.0 / g_bp
    r_bp_iso = (SINK_LX_MM * 1e-3) / (K_AL_6063_T6 * a_c_bp * 1e-6)   # 等温模型

    # ---- 腔体节点 (尺 A + 尺 B) ----
    def cavity2(r_branch: float, d: float, p_w: float) -> float:
        r_amb = 160000.0 / a_conv_by_d[d]
        r_eff = 1.0 / (1.0 / r_sb + 1.0 / r_amb + 1.0 / r_branch)
        return T_BASE_C + p_w * r_eff

    ht = cv2["cand"]["P3"]["r_path"]        # R_热路 = 9.40 K/W (铝条 + TIM)
    u8_lo, u8_hi = U8_LIST_MM[0], U8_LIST_MM[-1]
    r_end_lo = R_COL_KW_NUM / (u8_lo * ENDPOINT_COL_W_MM)
    r_end_hi = R_COL_KW_NUM / (u8_hi * ENDPOINT_COL_W_MM)

    # 路径 (a): 铝背板 (鳍) ∥ 端件外表面
    r_bp_par_lo = 1.0 / (1.0 / r_bp_fin + 1.0 / r_end_lo)
    r_bp_par_hi = 1.0 / (1.0 / r_bp_fin + 1.0 / r_end_hi)
    r_branch_a_lo = ht + r_bp_par_lo
    r_branch_a_hi = ht + r_bp_par_hi
    # 打印件顶面 (V2 名义同温口径)
    r_branch_print_nom = ht + R_COL_KW_NUM / a_net
    # 打印件顶面 + 连通性修正 (C-7b)
    r_branch_print_real = ht + r_print
    # 路径 (c): 端件整条金属化 (集热面只有端件外表面)
    r_branch_c_lo = ht + r_end_lo
    r_branch_c_hi = ht + r_end_hi

    d0 = 15.0
    t_a_lo = cavity2(r_branch_a_lo, d0, P_PANEL_W)
    t_a_hi = cavity2(r_branch_a_hi, d0, P_PANEL_W)
    t_a_lo_50 = cavity2(r_branch_a_lo, d0, P_COL_05W)
    t_print_nom = cavity2(r_branch_print_nom, d0, P_PANEL_W)
    t_print_real = cavity2(r_branch_print_real, d0, P_PANEL_W)
    t_print_real_415 = cavity2(r_branch_print_real, d0, P_PANEL_LOW_W)
    t_c_lo = cavity2(r_branch_c_lo, d0, P_PANEL_W)
    t_c_hi = cavity2(r_branch_c_hi, d0, P_PANEL_W)
    # 路径 (a) 的 P_max (d=15, u8=30)
    r_amb0 = 160000.0 / a_conv_by_d[d0]
    def a_req_at(d: float, p_w: float) -> float:
        inv = p_w / (T_CAV_LIMIT_C - T_BASE_C) - 1.0 / r_sb - 1.0 / (160000.0 / a_conv_by_d[d])
        return R_COL_KW_NUM / (1.0 / inv - ht)
    a_req_415 = {d: a_req_at(d, P_PANEL_LOW_W) for d in a_req}
    p_max_a = (T_CAV_LIMIT_C - T_BASE_C) * (1.0 / r_sb + 1.0 / r_amb0 + 1.0 / r_branch_a_lo)

    # ================= ★ISS-227: C-7b 集热面口径修正 + 三档重算 =================
    # ★★改的是【假设/口径】(集热面材质), 不是【阈值】(50 °C / k=201 / 120×30 一个没动)

    def _rb_backplate(u8: float) -> float:
        """★活口径 (C7B-04): 铝制集热背板 120×30×1.0 (鳍模型, 根部与铝条同温) ∥ 端件外表面 u8×20"""
        r_end = R_COL_KW_NUM / (u8 * ENDPOINT_COL_W_MM)
        return ht + 1.0 / (1.0 / r_bp_fin + 1.0 / r_end)

    def _rb_print_nom_old(u8: float) -> float:
        """旧口径 (C7B-01 · ISS-219 名义同温): 打印件顶面 120×30 (3600, 假同温) ∥ 端件"""
        return ht + R_COL_KW_NUM / (SINK_LX_MM * SINK_WRIM_MM + u8 * ENDPOINT_COL_W_MM)

    def _rb_print_net_old(u8: float) -> float:
        """旧口径 (C7B-02 · ISS-222 §2.3 名义): 净 3432 单面, 不含端件并联"""
        return ht + R_COL_KW_NUM / a_net

    def _rb_print_real_old(u8: float) -> float:
        """旧口径 (C7B-03 · ISS-222 §2.3 连通性修正): 打印件顶面有效热阻 (鳍模型) 单面"""
        return ht + r_print

    def _three_tier(rb_fn, u8: float) -> dict:
        rb = rb_fn(u8)
        t468 = {d: cavity2(rb, d, P_PANEL_W) for d in C7B_D_LIST_MM}
        t50 = {d: cavity2(rb, d, P_COL_05W) for d in C7B_D_LIST_MM}
        return dict(r_branch=rb, t468=t468, t50=t50,
                    ok={d: t468[d] <= T_CAV_LIMIT_C for d in C7B_D_LIST_MM},
                    ok50={d: t50[d] <= T_CAV_LIMIT_C for d in C7B_D_LIST_MM})

    u8_main, u8_hi = C7B_U8_MAIN_MM, C7B_U8_HI_MM

    def _row(rid: str, material: str, material_cn: str, caliber: str, area: float,
             rb_fn, active: bool) -> dict:
        tt = _three_tier(rb_fn, u8_main)
        return dict(rid=rid, material=material, material_cn=material_cn, caliber=caliber,
                    area=area, u8=u8_main, active=active, **tt)

    c7b_rows = [
        _row("C7B-01", SINK_SURFACE_MATERIAL_LEGACY, "打印件 PA-CF",
             "旧口径 · ISS-219 名义同温: 打印件顶面 120×30 当与铝条同温 + 端件并联 · u8=30",
             SINK_LX_MM * SINK_WRIM_MM + u8_main * ENDPOINT_COL_W_MM, _rb_print_nom_old, False),
        _row("C7B-02", SINK_SURFACE_MATERIAL_LEGACY, "打印件 PA-CF",
             "旧口径 · ISS-222 §2.3 名义: 净 3432 单面 (不含端件并联) · u8 不参与",
             a_net, _rb_print_net_old, False),
        _row("C7B-03", SINK_SURFACE_MATERIAL_LEGACY, "打印件 PA-CF",
             "旧口径 · ISS-222 §2.3 连通性修正: 打印件顶面有效热阻 (鳍模型) 单面 · u8 不参与",
             a_net, _rb_print_real_old, False),
        _row("C7B-04", SINK_SURFACE_MATERIAL, SINK_SURFACE_MATERIAL_CN,
             "★新口径 (本单采用): 铝制集热背板 120×30×1.0 (鳍模型, 根部与铝条同温) ∥ 端件 u8×20 · u8=30",
             SINK_LX_MM * SINK_WRIM_MM + u8_main * ENDPOINT_COL_W_MM, _rb_backplate, True),
    ]

    # ---- u8 敏感度 (活口径: 铝背板) ----
    c7b_u8_rows = []
    for u8 in U8_LIST_MM:
        tt = _three_tier(_rb_backplate, u8)
        pm = {d: (T_CAV_LIMIT_C - T_BASE_C)
              * (1.0 / r_sb + 1.0 / (160000.0 / a_conv_by_d[d]) + 1.0 / tt["r_branch"])
              for d in C7B_D_LIST_MM}
        c7b_u8_rows.append(dict(u8=u8, r_branch=tt["r_branch"], t468=tt["t468"], t50=tt["t50"],
                                ok=tt["ok"], p_max=pm))

    # ---- 需求侧: 50 °C 下 R_支路 (含集热支路) 的允许上限 ----
    c7b_req = {}
    for d in C7B_D_LIST_MM:
        r_amb_d = 160000.0 / a_conv_by_d[d]
        inv = P_PANEL_W / (T_CAV_LIMIT_C - T_BASE_C) - 1.0 / r_sb - 1.0 / r_amb_d
        rbr_req = 1.0 / inv
        c7b_req[d] = dict(r_branch_req=rbr_req, r_sink_req=rbr_req - ht)

    # ---- 活口径的 lumped 等效集热面面积 (与 §2.2 的 a_req 同一口径, 可直接比) ----
    c7b_aeq = {u8: R_COL_KW_NUM / (_rb_backplate(u8) - ht) for u8 in U8_LIST_MM}
    c7b_margin = []
    for d in C7B_D_LIST_MM:
        tt = _three_tier(_rb_backplate, u8_main)
        a_eq = c7b_aeq[u8_main]
        a_need = a_req[d]
        pm = (T_CAV_LIMIT_C - T_BASE_C) \
            * (1.0 / r_sb + 1.0 / (160000.0 / a_conv_by_d[d]) + 1.0 / tt["r_branch"])
        c7b_margin.append(dict(d=d, r_branch_req=c7b_req[d]["r_branch_req"],
                               a_eq=a_eq, a_need=a_need, d_area=a_eq - a_need,
                               d_area_pct=(a_eq - a_need) / a_need * 100.0,
                               d_t=T_CAV_LIMIT_C - tt["t468"][d], d_p=pm - P_PANEL_W))

    # ---- 保守上界 (不推翻活口径, 只给边界) ----
    # ① 背板在摄像头凸包处局部让位 ⇒ 有效集热面 3432 (G 按面积比缩)
    r_bp_fin_relief = r_bp_fin / (a_net / (SINK_LX_MM * SINK_WRIM_MM))
    r_branch_relief_lo = ht + 1.0 / (1.0 / r_bp_fin_relief + 1.0 / r_end_lo)
    # ② 等温上界 (假设整块背板与铝条同温 ⇒ 19.90 K/W)
    r_branch_iso_lo = ht + 1.0 / (1.0 / r_bp_iso + 1.0 / r_end_lo)
    r_branch_iso_hi = ht + 1.0 / (1.0 / r_bp_iso + 1.0 / r_end_hi)
    # ③ 打印件口径若把端件外表面也并联进来 (比 ISS-222 已发布口径更宽松)
    r_branch_print_real_par = ht + 1.0 / (1.0 / r_print + 1.0 / r_end_lo)

    return dict(
        c6=c6, ts_rows=ts_rows, ts_axial=TS_AXIAL_MM,
        c7b_rows=c7b_rows, c7b_u8_rows=c7b_u8_rows, c7b_req=c7b_req,
        c7b_aeq=c7b_aeq, c7b_margin=c7b_margin,
        c7b_u8_main=u8_main, c7b_u8_hi=u8_hi,
        r_bp_fin_relief=r_bp_fin_relief,
        r_branch_relief_lo=r_branch_relief_lo,
        r_branch_iso_lo=r_branch_iso_lo, r_branch_iso_hi=r_branch_iso_hi,
        r_branch_print_real_par=r_branch_print_real_par,
        a_nominal=a_nominal, a_cam=a_cam, a_net=a_net, a_req=a_req, w_req=w_req,
        r_base=r_base, r_fin_rim=r_fin_rim, r_print=r_print, r_along_rim=r_along_rim,
        a_c_rim=a_c_rim, per_rim=per_rim, g_rim=g_rim,
        r_bp_fin=r_bp_fin, r_bp_iso=r_bp_iso, g_bp=g_bp, backplate_g=BACKPLATE_M_G,
        r_branch_a_lo=r_branch_a_lo, r_branch_a_hi=r_branch_a_hi,
        r_branch_print_nom=r_branch_print_nom, r_branch_print_real=r_branch_print_real,
        r_branch_c_lo=r_branch_c_lo, r_branch_c_hi=r_branch_c_hi,
        t_a_lo=t_a_lo, t_a_hi=t_a_hi, t_a_lo_50=t_a_lo_50,
        t_print_nom=t_print_nom, t_print_real=t_print_real, t_print_real_415=t_print_real_415,
        t_c_lo=t_c_lo, t_c_hi=t_c_hi, p_max_a=p_max_a,
        a_req_415=a_req_415,
        end_mass_lo=ENDPOINT_FULL_MASS_LO, end_mass_hi=ENDPOINT_FULL_MASS_HI,
    )


# ======================================================================
# ★ISS-237 (2026-11-16 · 闭环轮): C-7c —— W_rim 门槛 (鳍模型) + 背板质量账
# ======================================================================
def compute_c7c(c: dict | None = None, cv2: dict | None = None,
                 v3: dict | None = None) -> dict:
    """★ISS-237 闭环轮: 把 C-7 的唯一前置「镜框上沿前后宽 W_rim」用**活口径** (鳍模型) 实算成门槛。

    ★★为什么必须再算一遍 (不是重复劳动):
      ISS-222 §2.2 给的门槛 **W_rim ≥ 23.30 mm** 来自 **lumped (集热面当等温面)** 模型
      + **0.468 W 面板功耗**; 而 ISS-227 §2.5 已经把活口径换成**鳍模型**
      (背板 120×30×1.0, 沿长度方向有温差) ⇒ **同一条门槛在两个口径下不是一个数**
      ⇒ 而 ISS-216 的**代表负载是 0.50 W** ⇒ 按 23.30 裁框截面 ⇒ 0.50 W 下腔体会摸/破红线。

    口径 (全部沿用上面的尺 A / 尺 B / 鳍模型, 一个公式没新造):
      · 背板: 长 120 mm × 前后宽 W_rim × 厚 1.0 mm (6063-T6, k=201, ρ=2.70)
      · 鳍模型: m = sqrt(h·P/(k·A_c)), G = sqrt(h·P·k·A_c)·tanh(m·L), R = 1/G
      · 摄像头凸包让位: 有效面积 = 120×W_rim − 168 ⇒ G 按面积比缩 (与 §2.5.4 保守上界 ① 同款)
      · 并联支路: 背板 ∥ 端件外表面 u8×20; R_支路 = R_热路(9.403) + 并联集热支路
      · 腔体节点: 尺 A (R_skin 495.238 / R_amb 160000/A_conv(d) / 基准 35 °C)
    """
    if c is None:
        c = compute()
    if cv2 is None:
        cv2 = compute_v2(c)
    if v3 is None:
        v3 = compute_v3(c, cv2)
    r_sb = cv2["r_sb"]
    a_conv_by_d = cv2["a_conv_by_d"]
    ht = cv2["cand"]["P3"]["r_path"]          # R_热路 9.403 K/W (铝条 + TIM)
    u8 = C7C_U8_MM
    r_end = R_COL_KW_NUM / (u8 * ENDPOINT_COL_W_MM)
    a_cam = CAM_BUMP_X_MM * CAM_BUMP_Y_MM      # 168 mm²
    bar_len_mm = 50.0

    # ---- 背板鳍模型 (深度 = W_rim) ----
    def bp_fin(depth: float, relief: bool = True) -> float:
        a_c = depth * BACKPLATE_T_MM
        per = depth
        m = math.sqrt(H_CONV_COL * per * 1e-3 / (K_AL_6063_T6 * a_c * 1e-6))
        g = math.sqrt(H_CONV_COL * per * 1e-3 * K_AL_6063_T6 * a_c * 1e-6) \
            * math.tanh(m * SINK_LX_MM * 1e-3)
        r = 1.0 / g
        if relief:
            a_nom = SINK_LX_MM * depth
            r = r * (a_nom / (a_nom - a_cam))     # G 按面积比缩 ⇒ R 按比例放大
        return r

    def rb_of(depth: float, relief: bool = True) -> float:
        return ht + 1.0 / (1.0 / bp_fin(depth, relief) + 1.0 / r_end)

    def cav(r_branch: float, d: float, p_w: float) -> float:
        r_amb = 160000.0 / a_conv_by_d[d]
        r_eff = 1.0 / (1.0 / r_sb + 1.0 / r_amb + 1.0 / r_branch)
        return T_BASE_C + p_w * r_eff

    def t15(depth: float, p_w: float, relief: bool = True) -> float:
        return cav(rb_of(depth, relief), 15.0, p_w)

    def w_min(p_w: float, relief: bool = True):
        """T@15 ≤ 50 °C 的最小 W_rim (二分; 背板深度 = W_rim, 越宽越凉)"""
        lo, hi = 5.0, 60.0
        if t15(hi, p_w, relief) > T_CAV_LIMIT_C:
            return None
        for _ in range(100):
            mid = (lo + hi) / 2.0
            if t15(mid, p_w, relief) <= T_CAV_LIMIT_C:
                hi = mid
            else:
                lo = mid
        return hi

    # ---- 打印件顶面路径 (对照: 同一个 W_rim 下打印件更差) ----
    def r_print_at(depth: float) -> float:
        a_base = bar_len_mm * depth
        r_base = R_COL_KW_NUM / a_base
        a_c_rim = 2.0 * RIM_WALL_MM * depth + 2.0 * RIM_WALL_MM * RIM_HEIGHT_MM
        per_rim = depth + 2.0 * RIM_WALL_MM
        l_ext = (SINK_LX_MM - bar_len_mm) * 1e-3
        m = math.sqrt(H_CONV_COL * per_rim * 1e-3 / (K_PRINT_RIM * a_c_rim * 1e-6))
        g = math.sqrt(H_CONV_COL * per_rim * 1e-3 * K_PRINT_RIM * a_c_rim * 1e-6) \
            * math.tanh(m * l_ext)
        return 1.0 / (1.0 / r_base + 1.0 / (1.0 / g))

    r_amb15 = 160000.0 / a_conv_by_d[15.0]
    rows = []
    for w in C7C_W_LIST_MM:
        rb = rb_of(w, True)
        m_bp = SINK_LX_MM * w * BACKPLATE_T_MM * RHO_AL_G_MM3
        rows.append(dict(
            w=w, a_bp=SINK_LX_MM * w, m_bp=m_bp,
            r_fin=bp_fin(w, True), r_branch=rb,
            t468={d: cav(rb, d, P_PANEL_W) for d in C7B_D_LIST_MM},
            t50=cav(rb, 15.0, P_COL_05W),
            p_max=(T_CAV_LIMIT_C - T_BASE_C) * (1.0 / r_sb + 1.0 / r_amb15 + 1.0 / rb),
            w_total_lo=C7C_DOC_WEIGHT[0] + m_bp, w_total_hi=C7C_DOC_WEIGHT[1] + m_bp,
            t_print=cav(ht + r_print_at(w), 15.0, P_PANEL_W),
        ))

    w_min_468 = w_min(P_PANEL_W, True)
    w_min_500 = w_min(P_COL_05W, True)
    w_min_468_nr = w_min(P_PANEL_W, False)
    w_min_500_nr = w_min(P_COL_05W, False)

    return dict(rows=rows, u8=u8, r_end=r_end, ht=ht, a_cam=a_cam,
                w_min_468=w_min_468, w_min_500=w_min_500,
                w_min_468_no_relief=w_min_468_nr, w_min_500_no_relief=w_min_500_nr,
                m_bp_per_mm=RHO_AL_G_MM3 * SINK_LX_MM * BACKPLATE_T_MM,
                doc_weight=C7C_DOC_WEIGHT)


def fmt(x: float, nd: int = 2) -> str:
    s = f"{x:.{nd}f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s or "0"


def row_cells(r: dict) -> list:
    """R 行 14 列 (不含行号列) —— 顺序即文档表格列序, 门禁逐格比对"""
    return [
        f"{fmt(r['d'])}", f"{fmt(r['ae'])}", f"{fmt(r['tc'])}", f"{fmt(r['ts'])}",
        f"{fmt(r['margin'])}", f"{fmt(r['stack'])}", f"{fmt(r['t_band'])}",
        f"{fmt(r['delta_hi'])}", f"{fmt(r['delta_old'])}", f"{fmt(r['c1'])}",
        f"{fmt(r['band_travel'])}", f"{fmt(r['slack'])}", r["verdict"],
        f"{r['evidence']} / {r['source']}",
    ]


def band_cells(c: dict) -> list:
    """B 行 (出瞳面 ±3 mm 装配公差带) 8 列"""
    sl = {d: next(r for r in c["rows"] if r["d"] == d)["slack"] for d in D_LIST_MM}
    verdicts = []
    for d in D_LIST_MM:
        verdicts.append(f"d={fmt(d)}: 装下但只剩 {fmt(sl[d])} mm "
                        f"({'超' if sl[d] < FIT_JUDGE_MM else '过'}判据 {fmt(FIT_JUDGE_MM)})")
    return [
        "出瞳面 ±3 mm 装配公差带 (V2 §3 ⑤ 降级方案)",
        f"{fmt(c['band_travel'])}",
        f"{fmt(sl[15.0])}", f"{fmt(sl[18.0])}", f"{fmt(sl[20.0])}",
        " ; ".join(verdicts),
        f"[推算] / V2 §3 ⑤ + X-2 ③ + §1.4.5",
    ]


def splitter_cells(ae: float, c: dict) -> list:
    """S 行 (分光件随眼盒重算) 9 列"""
    s = c["splitter"][ae]
    return [
        f"{fmt(ae)}",
        f"{fmt(s['de'], 3)}",
        f"{fmt(s['de'] / c['dp'], 4)}",
        f"{fmt(s['diag_legacy'], 2)}",
        f"{fmt(s['diag_strict'], 2)}",
        f"{fmt(s['total_cc'], 3)}",
        f"{fmt(s['dv_cc'], 3)}",
        f"{fmt(s['w4_lo'], 2)}-{fmt(s['w4_hi'], 2)}",
        ("45° 平板 10×10 (对角 14.14) 按 §1.2 式够; 严格矩形包含口径 "
         + ("也够 (余 %.2f mm)" % (10.0 * math.sqrt(2.0) - s["diag_strict"])
            if s["plate_fits_strict"] else
            "不够 (差 %.2f mm)" % (s["diag_strict"] - 10.0 * math.sqrt(2.0)))),
    ]


def emit_rows() -> str:
    c = compute()
    out = ["| # | d (mm) | A_e (mm²) | 耦合光学 t_c (mm) | 分光件 t_s (mm) | "
           "装配余量 m (mm) | 器件区合计 (mm) | **正中区轴向厚度预算 T (mm, 含 ±3 带)** | "
           "Δ vs 目标上沿 12 (mm) | Δ vs 旧数 11.8 (mm) | **C-1 冲突量 d−11.8 (mm)** | "
           "±3 带占用 (mm) | 可动余量 (mm) | 判定 | 证据 / 出处 |"]
    for i, r in enumerate(c["rows"], 1):
        out.append("| " + " | ".join([f"R{i}"] + row_cells(r)) + " |")
    out.append("")
    out.append("| # | 项 | 行程/占用 (mm) | d=15 可动余量 (mm) | d=18 (mm) | d=20 (mm) | 判定 | 证据 / 出处 |")
    out.append("| " + " | ".join(["B1"] + band_cells(c)) + " |")
    out.append("")
    out.append("| # | A_e (mm²) | 眼盒等效直径 D_e (mm) | 中继比 M = D_e/D_p (FOV 折减) | "
               "45° 平板所需对角 (宽松口径, mm) | 所需对角 (严格口径, mm) | 分光组件体积 (cc) | "
               "Δ vs §1.3 M6 的 0.79 cc (cc) | W4 重量重估 (g) | 备注 |")
    for ae in AE_LIST_MM2:
        out.append("| " + " | ".join([f"S{fmt(ae)}"] + splitter_cells(ae, c)) + " |")
    return "\n".join(out)


# ======================================================================
# §2 门禁检查
# ======================================================================
def _read(root: str, rel: str) -> str:
    p = os.path.join(root, rel)
    if not os.path.exists(p):
        return ""
    with open(p, "r", encoding="utf-8") as f:
        return f.read()


def _md5(root: str, rel: str) -> str:
    p = os.path.join(root, rel)
    if not os.path.exists(p):
        return "MISSING"
    h = hashlib.md5()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _num(cell: str):
    cell = cell.strip().replace("−", "-").replace("—", "")
    m = re.match(r"^[-+]?\d+(?:\.\d+)?$", cell)
    return float(m.group(0)) if m else None


def parse_rows(doc: str) -> list:
    """抓所有 | R# | / | B# | / | S## | 开头的表格行 (行号列之后 = 若干单元格)"""
    rows = []
    for line in doc.splitlines():
        m = re.match(r"^\|\s*([A-Z]+\d*)\s*\|(.*)\|\s*$", line)
        if not m:
            continue
        rid = m.group(1)
        if not re.match(r"^(R\d+|B\d+|S\d+)$", rid):
            continue
        cells = [c.strip() for c in m.group(2).split("|")]
        rows.append(dict(idx=rid, cells=cells))
    return rows


def parse_rows_pat(doc: str, pat: str) -> list:
    """★ISS-219: 按行号模式抓表格行 (V2 交卷件用 C6-xx / P1 / T-xx / D-xx / U8-xx / K-xx)。
    行号格与数据格里的 markdown 粗体标记 (**) 会被剥掉, 免得 **P1** 这种写法解析不出来。"""
    out = []
    for line in doc.splitlines():
        m = re.match(r"^\|\s*(\*\*)?(" + pat + r")(\*\*)?\s*\|(.*)\|\s*$", line)
        if not m:
            continue
        cells = [c.strip().replace("**", "").strip() for c in m.group(4).split("|")]
        out.append(dict(idx=m.group(2).strip(), cells=cells))
    return out


def _heading_hits(doc: str, keys, min_level: int = 1):
    """★ISS-227 续做: 找出正文里所有「标题同时含 keys 全部关键字」的标题。

    返回 [(行下标, 标题层级, 标题全文)]。

    ★★**min_level 是本函数存在的理由** (2026-11-16 05:1x main 实测抓到的真缺陷):
      文档 H1 大标题**常常也含这些关键字** (本文件第 1 行就同时含 "C-7b" 与
      "集热面口径修正") ⇒ 若不排除 H1, 「节存在性」断言会变成**永远为真**
      (抓到的"节" = 整篇 349 行文档) ⇒ ★**门禁可被"删掉整个 C-7b 节"绕过** ★
      —— 这是反向 19 抓不到任何一条的**根因**。
    ⇒ 判定「独立成节」只认 **level >= min_level (默认 2 = 非文档标题)** 的标题。
    """
    lines = doc.splitlines()
    out = []
    for i, ln in enumerate(lines):
        m = re.match(r"^(#{1,6})\s+(.*)$", ln)
        if not m:
            continue
        lvl = len(m.group(1))
        if lvl < min_level:
            continue
        head = m.group(2)
        if all(k in head for k in keys):
            out.append((i, lvl, head))
    return out


def _section_spans(doc: str, keys, min_level: int = 2):
    """★ISS-227 续做: 同 _heading_hits, 但把每个命中标题的**正文范围**也切出来。

    返回 [(标题行下标, 结束行下标(不含), 标题全文, 节正文)] —— 结束于下一个
    **同级或更高级**标题 (level <= 本标题 level)。
    """
    lines = doc.splitlines()
    out = []
    for i, lvl, head in _heading_hits(doc, keys, min_level):
        end = len(lines)
        for j in range(i + 1, len(lines)):
            m2 = re.match(r"^(#{1,6})\s", lines[j])
            if m2 and len(m2.group(1)) <= lvl:
                end = j
                break
        out.append((i, end, head, "\n".join(lines[i:end])))
    return out


def _section_text(doc: str, keys, min_level: int = 1) -> str:
    """★ISS-227: 抓出标题里同时含 keys 全部关键字的那一节正文 (到下一个同级或更高级标题为止)。

    用于门禁回读「C-7b 集热面口径修正」独立节 —— 找不到 = 节被删了 = 门禁红。

    ★★**min_level 默认 1 是为兼容旧调用; 但 C21/C22 一律显式传 min_level=2** ★★
    ⇒ 否则会命中 H1 文档标题 ⇒ 抓到整篇文档 ⇒ "节存在性"断言变成空断言。
    """
    spans = _section_spans(doc, keys, min_level)
    return spans[0][3] if spans else ""


def _first_int(cell: str):
    m = re.search(r"\d+(?:\.\d+)?", cell)
    return float(m.group(0)) if m else None


def _cmp(v2: dict, cell: str, want: float, nd: int = 2, tol: float = 0.005) -> str | None:
    """数值格比对: 返回 None = 一致, 否则返回差异描述"""
    got = _num(cell)
    if got is None:
        return f"{cell!r} 不是数字 (应 {fmt(want, nd)})"
    if abs(got - want) > tol:
        return f"{got} ≠ 脚本 {fmt(want, nd)}"
    return None


def check_all(root: str) -> list:
    """返回 [(cid, 名称, ok, 详情)]"""
    c = compute()
    res = []
    doc = _read(root, DOC_REL)
    budget = _read(root, BUDGET_REL)

    # C1 —— §1.7 X-1 / X-2 在结构真源里在位 (关键词 + 数值 62 / 15 / 20)
    ok = True
    det = []
    x1 = [ln for ln in budget.splitlines() if "**X-1**" in ln]
    x2 = [ln for ln in budget.splitlines() if "**X-2**" in ln]
    if not x1:
        ok = False; det.append("结构真源找不到 X-1 行")
    elif not re.search(r"A_e\s*≤\s*62\s*mm²", x1[0]):
        ok = False; det.append(f"X-1 行里没有 'A_e ≤ 62 mm²' (实际: {x1[0][:80]}...)")
    if not x2:
        ok = False; det.append("结构真源找不到 X-2 行")
    else:
        if "15" not in x2[0] or "20" not in x2[0]:
            ok = False; det.append("X-2 行里没有 15 / 20 (评估距离)")
    if "62 mm²" not in budget:
        ok = False; det.append("结构真源缺 '62 mm²'")
    if not re.search(r"d\s*=\s*15[–\-—]20\s*mm", budget):
        ok = False; det.append("缺 'd = 15-20 mm'")
    if "11.8" not in budget:
        ok = False; det.append("缺 '11.8'")
    if "10-12" not in budget and "10–12" not in budget:
        ok = False; det.append("缺 '10-12'")
    res.append(("C1", "§1.7 X-1/X-2 在结构真源在位 (62 / 15-20 / 11.8 / 10-12)", ok,
                "; ".join(det) if det else "X-1/X-2/62/15-20/11.8/10-12 全部在位"))

    # C2 —— 参数表 9 行齐全 + 每格与脚本一致
    prs = [r for r in parse_rows(doc) if r["idx"].startswith("R")]
    ok = len(prs) == 9
    det = [] if ok else [f"R 行数 {len(prs)} ≠ 9"]
    seen = set()
    exp = c["rows"]
    if ok:
        for r in prs:
            if len(r["cells"]) != 14:
                ok = False; det.append(f"{r['idx']} 列数 {len(r['cells'])} ≠ 14"); break
            want = exp[int(r["idx"][1:]) - 1] if 1 <= int(r["idx"][1:]) <= 9 else None
            if want is None:
                ok = False; det.append(f"{r['idx']} 行号越界"); break
            cells = row_cells(want)
            seen.add((r["cells"][0], r["cells"][1]))
            for ci in range(12):   # 0..11 全数值列
                got = _num(r["cells"][ci])
                if got is None:
                    ok = False; det.append(f"{r['idx']} 第{ci+1}列不是数: {r['cells'][ci]!r}"); break
                if abs(got - float(cells[ci])) > 0.005:
                    ok = False
                    det.append(f"{r['idx']} 第{ci+1}列 {got} ≠ 脚本 {cells[ci]}"); break
            if not ok:
                break
            if r["cells"][12].split("·")[0].strip() != want["verdict"].split("·")[0].strip():
                ok = False; det.append(f"{r['idx']} 判定 {r['cells'][12]!r} ≠ {want['verdict']!r}"); break
            if r["cells"][13] != cells[13]:
                ok = False; det.append(f"{r['idx']} 证据/出处不一致"); break
    if ok:
        want_set = {(fmt(x), fmt(y)) for x in D_LIST_MM for y in AE_LIST_MM2}
        if seen != want_set:
            ok = False
            det.append(f"维度覆盖不全: 缺 {sorted(want_set - seen)}")
    res.append(("C2", "参数表 9 行齐全 (3 d × 3 A_e) 且每格与脚本一致", ok,
                "; ".join(det) if det else "9/9 行, 3×3 维度覆盖完整, 12 列数值逐格一致"))

    # C3 —— 冲突量与脚本一致 (d=15 => 3.2 / d=20 => 8.2), 且文档逐字出现
    e15 = next(r for r in c["rows"] if r["d"] == 15.0)
    e20 = next(r for r in c["rows"] if r["d"] == 20.0)
    ok = abs(e15["c1"] - 3.2) < 1e-9 and abs(e20["c1"] - 8.2) < 1e-9
    det = [] if ok else [f"脚本算出 d=15 => {fmt(e15['c1'])} (应 3.2), d=20 => {fmt(e20['c1'])} (应 8.2)"]
    if ok:
        for lit in ("3.2", "8.2"):
            if lit not in doc:
                ok = False; det.append(f"文档里没有逐字出现 '{lit}'")
    res.append(("C3", "§1.7.1 C-1 冲突量一致 (d=15 ⇒ 3.2mm · d=20 ⇒ 8.2mm)", ok,
                "; ".join(det) if det else "d=15 ⇒ 3.2 / d=18 ⇒ 6.2 / d=20 ⇒ 8.2, 文档逐字在位"))

    # C4 —— 判据文件 md5 未变
    md5 = _md5(root, "MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md")
    ok = md5 == MD5_EXPECTED["MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md"]
    res.append(("C4", "判据文件 DISPLAY_BIOSAFETY_CRITERIA_V2.md md5 未变", ok,
                f"md5={md5}"))

    # C5 —— ±3 mm 出瞳面可调带: 单独成行 (B1) + 数值一致
    brows = [r for r in parse_rows(doc) if r["idx"] == "B1"]
    ok = bool(brows)
    det = [] if ok else ["文档里没有 B1 (±3 mm 带) 独立行"]
    if ok:
        cells = brows[0]["cells"]
        want = band_cells(c)
        if len(cells) != 7:
            ok = False; det.append(f"B1 列数 {len(cells)} ≠ 7")
        else:
            if "±3" not in cells[0]:
                ok = False; det.append("B1 行标题没有 ±3")
            for ci in (1, 2, 3, 4):
                got = _num(cells[ci])
                if got is None or abs(got - float(want[ci])) > 0.005:
                    ok = False
                    det.append(f"B1 第{ci+1}列 {cells[ci]!r} ≠ 脚本 {want[ci]}"); break
            if ok and "±3" not in doc:
                ok = False; det.append("全文没有 '±3'")
    res.append(("C5", "出瞳面 ±3 mm 装配公差带单独成行且占用量一致", ok,
                "; ".join(det) if det else f"带占用 {fmt(c['band_travel'])} mm, 9 行全部标注"))

    # C6 —— 重量重核 (W9) 数值与脚本一致
    w15 = next(r for r in c["rows"] if r["d"] == 15.0)
    w20 = next(r for r in c["rows"] if r["d"] == 20.0)
    ok = True; det = []
    for lit in (fmt(w15["w_frame_g"], 2), fmt(w20["w_frame_g"], 2)):
        if lit not in doc:
            ok = False; det.append(f"文档缺重量增量 {lit} g")
    if f"{fmt(w15['w9_lo'])}" not in doc:
        ok = False; det.append(f"文档缺 W9 重核下限 {fmt(w15['w9_lo'])}")
    res.append(("C6", "镜框重量重核 (W9) 数值与脚本一致", ok,
                "; ".join(det) if det else
                f"ΔW 镜框 +{fmt(w15['w_frame_g'])}~+{fmt(w20['w_frame_g'])} g; "
                f"W9 → {fmt(w15['w9_lo'])}-{fmt(w15['w9_hi'])} g (d=15)"))

    # C7 —— 鼻梁区热路径长度与 43°C 余量
    t0 = c["thermal"][0]
    ok = True; det = []
    for lit in ("12.0", fmt(t0["t_patch_pcb"], 1), fmt(t0["margin_pcb"], 1),
                fmt(t0["t_patch_panel_only"], 1)):
        if lit not in doc:
            ok = False; det.append(f"文档缺鼻梁热数 {lit}")
    res.append(("C7", "鼻梁区热路径 (mm) 与 43°C 余量一致", ok,
                "; ".join(det) if det else
                f"热路径 {fmt(NOSE_L_MM,1)} mm; PCB 进镜框 ⇒ T_patch {fmt(t0['t_patch_pcb'],1)} °C "
                f"(余量 {fmt(t0['margin_pcb'],1)} °C)"))

    # C8 —— 受保护脚本 md5 未变 (4 个)
    bad = []
    for rel, want in MD5_EXPECTED.items():
        if rel.startswith("MECH/DISPLAY"):
            continue
        got = _md5(root, rel)
        if got != want:
            bad.append(f"{rel} md5={got}")
    res.append(("C8", "四个受保护 check 脚本 md5 未变", not bad,
                "; ".join(bad) if bad else "4/4 md5 一致"))

    # C9 —— 分片 claim mech_hinge_stack_fixed_mm = 25.00 (U-3 订正)
    frag = _read(root, FRAG_REL)
    ok = bool(re.search(r"key:\s*mech_hinge_stack_fixed_mm\s*\n\s*value:\s*'?25\.00'?", frag))
    res.append(("C9", "分片 mech_hinge_stack_fixed_mm = 25.00 (U-3)", ok,
                "25.00" if ok else "没找到 value: 25.00"))

    # C10 —— 判据阈值一个不许松 (0.1234 / 1500 / 4000 / 50 / 60 / 0.011)
    ok = True; det = []
    for token in ("0.1234", "1500", "4000", "62 mm²", "15–20", "0.011"):
        if token not in budget:
            ok = False; det.append(f"结构真源缺 '{token}'")
    res.append(("C10", "结构真源判据阈值未松 (0.1234/1500/4000/62/15-20/0.011)", ok,
                "; ".join(det) if det else "阈值全部在位"))

    # C11 —— 分光件随眼盒重算的冲突量 (体积 / 重量) 与脚本一致 (S 行逐格比对)
    srows = {r["idx"]: r for r in parse_rows(doc) if r["idx"].startswith("S")}
    ok = len(srows) == 3
    det = [] if ok else [f"S 行数 {len(srows)} ≠ 3"]
    if ok:
        for ae in AE_LIST_MM2:
            rid = f"S{fmt(ae)}"
            r = srows.get(rid)
            if r is None:
                ok = False; det.append(f"缺 {rid} 行"); break
            want = splitter_cells(ae, c)
            cells = r["cells"]
            if len(cells) != 9:
                ok = False; det.append(f"{rid} 列数 {len(cells)} ≠ 9"); break
            for ci in (0, 1, 2, 3, 4, 5, 6):
                got = _num(cells[ci])
                if got is None or abs(got - float(want[ci])) > 0.005:
                    ok = False
                    det.append(f"{rid} 第{ci+1}列 {cells[ci]!r} ≠ 脚本 {want[ci]}"); break
            if not ok:
                break
    res.append(("C11", "分光件随眼盒重算的体积/重量冲突量一致", ok,
                "; ".join(det) if det else
                f"A_e=62 ⇒ {fmt(c['splitter'][62.0]['total_cc'],3)} cc "
                f"(Δ {fmt(c['splitter'][62.0]['dv_cc'],3)}); "
                f"A_e=25 ⇒ {fmt(c['splitter'][25.0]['total_cc'],3)} cc"))

    # C12 —— 边界: 不替老板拍板 + 口径声明 + 降级方案
    ok = True; det = []
    for token in ("不替老板", "降级", "口径 B"):
        if token not in doc:
            ok = False; det.append(f"文档缺 '{token}'")
    res.append(("C12", "边界声明齐全 (不替老板拍板 / 降级方案 / 口径 B)", ok,
                "; ".join(det) if det else "三项在位"))

    # ================= ★ISS-219 新增 5 项判据 (只增, 既有 12 项一条没删) =================
    v2 = _read(root, V2_REL)
    cv2 = compute_v2(c)

    # C13 —— C-6 分光件新规格 vs 光束口径 8.885 相容
    ok = True
    det = []
    rows6 = {r["idx"]: r for r in parse_rows_pat(v2, r"C6-\d+")}
    if len(rows6) != 3:
        ok = False
        det.append(f"C6 行数 {len(rows6)} ≠ 3")
    else:
        for ae in AE_LIST_MM2:
            rid = f"C6-{fmt(ae, 0)}"
            r = rows6.get(rid)
            if r is None:
                ok = False; det.append(f"缺 {rid} 行"); break
            w = cv2["spl2"][ae]
            cells = r["cells"]
            if len(cells) != 14:
                ok = False; det.append(f"{rid} 列数 {len(cells)} ≠ 14"); break
            # 数值格: A_e / D_e / 对角·宽松 / 对角·严格 / 等效方边长 / 平板新对角 /
            #         体积 / Δ / W4下 / W4上 / 工程体积 / 中继比
            want = [ae, w["de"], w["diag_legacy"], w["diag_strict"], w["side"], None,
                    w["plate_diag"], None, w["total_cc"], w["dv_cc"], w["w4_lo"], w["w4_hi"],
                    w["eng_cc"], w["m_ratio"]]
            for ci, wv in enumerate(want):
                if wv is None:
                    continue
                e = _cmp(cv2, cells[ci], wv, 4 if ci in (1, 4, 13) else 2)
                if e:
                    ok = False
                    det.append(f"{rid} 第{ci+1}列 {e}"); break
            if not ok:
                break
            # 平板新规格: 边长 >= 光束口径, 且对角 >= 严格口径
            ps = _first_int(cells[5])
            prs = _first_int(cells[7])
            if ps is None or prs is None:
                ok = False; det.append(f"{rid} 平板/棱镜规格格解析失败: {cells[5]!r} / {cells[7]!r}"); break
            if ps < w["de"]:
                ok = False; det.append(f"{rid} 平板边长 {ps} < 光束口径 {fmt(w['de'],3)}"); break
            if prs < w["de"]:
                ok = False; det.append(f"{rid} 棱镜边长 {prs} < 光束口径 {fmt(w['de'],3)}"); break
            if w["plate_diag"] < w["diag_strict"] - 1e-9:
                ok = False; det.append(f"{rid} 平板对角 {fmt(w['plate_diag'],2)} < 严格口径 {fmt(w['diag_strict'],2)}"); break
    # 与 X-1 的一致性: 光束口径 = 眼盒等效直径, 且不突破 62
    s62 = cv2["spl2"][AE_MAX_MM2]
    if abs(s62["de"] - math.sqrt(4.0 * AE_MAX_MM2 / math.pi)) > 1e-9:
        ok = False; det.append("A_e=62 的 D_e 与脚本不符")
    if "62 mm²" not in budget:
        ok = False; det.append("结构真源缺 '62 mm²'")
    res.append(("C13", "C-6 分光件新规格 vs 光束口径 8.885 相容 (平板对角/棱镜/体积/重量/M)", ok,
                "; ".join(det) if det else
                f"A_e=62 ⇒ 平板 {s62['plate_i']}×{s62['plate_i']}×1.5 (对角 {fmt(s62['plate_diag'],2)} ≥ "
                f"{fmt(s62['diag_strict'],2)}) + 棱镜 {s62['prism_i']}×{s62['prism_i']}×5; "
                f"{fmt(s62['total_cc'],4)} cc / {fmt(s62['w4_lo'],2)}-{fmt(s62['w4_hi'],2)} g; M={fmt(s62['m_ratio'],4)}"))

    # C14 —— C-7 散热出路候选的 R_热路 / ΔT / 散热面对拍 (含 k=201)
    ok = True
    det = []
    # (a) 候选规格表 P1/P2/P3
    rows_p = {}
    for r in parse_rows_pat(v2, r"P\d"):
        rows_p.setdefault(r["idx"], r)      # 首次出现优先 (规格表在降级表之前)
    if len(rows_p) != 3:
        ok = False
        det.append(f"候选规格表行数 {len(rows_p)} ≠ 3")
    else:
        for cid, w in cv2["cand"].items():
            r = rows_p.get(cid)
            if r is None:
                ok = False; det.append(f"缺候选行 {cid}"); break
            cells = r["cells"]
            if len(cells) != 11:
                ok = False; det.append(f"{cid} 列数 {len(cells)} ≠ 11"); break
            want = [w["am"], w["L"], w["r_metal"], w["r_tim"], w["r_path"], w["dt468"],
                    w["dt50"], w["mass_g"], w["r_path_leg"]]
            for ci, wv in enumerate(want):
                e = _cmp(cv2, cells[ci + 1], wv, 2)
                if e:
                    ok = False
                    det.append(f"{cid} 第{ci+2}列 {e}"); break
            if not ok:
                break
            if "✅" not in cells[10]:
                ok = False; det.append(f"{cid} R_热路≤70 判定列不对: {cells[10]!r}"); break
    # (b) u8 表 T-01..T-15
    if ok:
        rows_t = parse_rows_pat(v2, r"T-\d+")
        if len(rows_t) != 15:
            ok = False; det.append(f"T 行数 {len(rows_t)} ≠ 15")
        else:
            for i, r in enumerate(rows_t):
                w = cv2["rows_t"][i]
                cells = r["cells"]
                if len(cells) != 9:
                    ok = False; det.append(f"{r['idx']} 列数 {len(cells)} ≠ 9"); break
                if cells[0] != w["cid"]:
                    ok = False; det.append(f"{r['idx']} 候选 {cells[0]!r} ≠ {w['cid']}"); break
                for ci, wv in ((1, w["u8"]), (2, w["a_col"]), (3, w["r_branch"]),
                               (4, w["t_cav468"]), (5, w["t_cav50"]), (6, w["t_col"]),
                               (7, w["a_req"])):
                    e = _cmp(cv2, cells[ci], wv, 1 if ci == 7 else 2, 0.06 if ci == 7 else 0.005)
                    if e:
                        ok = False; det.append(f"{r['idx']} 第{ci+1}列 {e}"); break
                if not ok:
                    break
                want_mark = "✅" if w["ok"] else "❌"
                if cells[8] != want_mark:
                    ok = False; det.append(f"{r['idx']} 判定 {cells[8]!r} ≠ {want_mark}"); break
    # (c) d 表 D-01..D-09
    if ok:
        rows_d = parse_rows_pat(v2, r"D-\d+")
        if len(rows_d) != 9:
            ok = False; det.append(f"D 行数 {len(rows_d)} ≠ 9")
        else:
            for i, r in enumerate(rows_d):
                w = cv2["rows_d"][i]
                cells = r["cells"]
                if len(cells) != 9:
                    ok = False; det.append(f"{r['idx']} 列数 {len(cells)} ≠ 9"); break
                if cells[0] != w["cid"]:
                    ok = False; det.append(f"{r['idx']} 候选 {cells[0]!r} ≠ {w['cid']}"); break
                for ci, wv in ((1, w["d"]), (2, w["a_col"]), (3, w["r_branch"]),
                               (4, w["t_cav468"]), (5, w["t_cav50"]), (6, w["t_col"]),
                               (7, w["a_req"])):
                    e = _cmp(cv2, cells[ci], wv, 1 if ci == 7 else 2, 0.06 if ci == 7 else 0.005)
                    if e:
                        ok = False; det.append(f"{r['idx']} 第{ci+1}列 {e}"); break
                if not ok:
                    break
                want_mark = "✅" if w["ok"] else "❌"
                if cells[8] != want_mark:
                    ok = False; det.append(f"{r['idx']} 判定 {cells[8]!r} ≠ {want_mark}"); break
    # (d) u8 总表 U8-01..U8-05
    if ok:
        rows_u = parse_rows_pat(v2, r"U8-\d+")
        if len(rows_u) != 5:
            ok = False; det.append(f"U8 行数 {len(rows_u)} ≠ 5")
        else:
            for i, r in enumerate(rows_u):
                w = cv2["rows_u8"][i]
                cells = r["cells"]
                if len(cells) != 8:
                    ok = False; det.append(f"{r['idx']} 列数 {len(cells)} ≠ 8"); break
                for ci, wv in ((0, w["u8"]), (1, w["a_end"]), (2, w["a_col"]),
                               (3, w["end_pct"]), (4, w["t_cav468"]), (5, w["t_cav50"]),
                               (6, w["spl_vert"])):
                    e = _cmp(cv2, cells[ci], wv, 1 if ci == 3 else 2, 0.06 if ci == 3 else 0.005)
                    if e:
                        ok = False; det.append(f"{r['idx']} 第{ci+1}列 {e}"); break
                if not ok:
                    break
                if cells[7] != ("✅" if w["ok"] else "❌"):
                    ok = False; det.append(f"{r['idx']} C-6 装得下判定不对: {cells[7]!r}"); break
    # (e) k=201 对拍: 三条候选的 R_热路 必须用 k=201 (不是 237)
    if ok:
        for cid, w in cv2["cand"].items():
            if abs(w["r_path"] - w["r_path_leg"]) < 1e-9:
                ok = False; det.append(f"{cid} R_热路 与旧口径相同 ⇒ 没换成 k=201"); break
    res.append(("C14", "C-7 散热出路候选的 R_热路 / ΔT / 散热面对拍 (含 k=201, 3+15+9+5 行逐格)", ok,
                "; ".join(det) if det else
                f"P1/P2/P3 的 R_热路 = {fmt(cv2['cand']['P1']['r_path'],2)} / "
                f"{fmt(cv2['cand']['P2']['r_path'],2)} / {fmt(cv2['cand']['P3']['r_path'],2)} K/W (k=201, 全 ≪70); "
                f"P3 腔体 {fmt(cv2['rows_t'][10]['t_cav468'],2)}-{fmt(cv2['rows_t'][14]['t_cav468'],2)} °C ✅"))

    # C15 —— 鼻梁 R_bridge 反解值 (454.8 / 1101.2) 对拍
    ok = True
    det = []
    for n in cv2["nose"]:
        for key, nd in (("r_min_panel", 1), ("r_min_pcb", 1)):
            lit = fmt(n[key], nd)
            if lit not in v2:
                ok = False
                det.append(f"V2 交卷件缺 d={fmt(n['d'],0)} 的 {key} = {lit}")
    # ISS-209 的两个主值必须逐字在位
    for lit in ("454.8", "1101.2"):
        if lit not in v2:
            ok = False
            det.append(f"V2 交卷件缺 '{lit}'")
    # 且脚本复算必须与 ISS-209 已发布的值一致 (不推翻)
    if abs(cv2["nose"][0]["r_min_panel"] - 454.8) > 0.05:
        ok = False; det.append(f"脚本复算 d=15 的 R_bridge_min(仅面板) = {fmt(cv2['nose'][0]['r_min_panel'],2)} ≠ 454.8")
    if abs(cv2["nose"][0]["r_min_pcb"] - 1101.2) > 0.05:
        ok = False; det.append(f"脚本复算 d=15 的 R_bridge_min(含 SoC) = {fmt(cv2['nose'][0]['r_min_pcb'],2)} ≠ 1101.2")
    res.append(("C15", "鼻梁 R_bridge 反解值 (454.8 / 1101.2 及三档) 对拍", ok,
                "; ".join(det) if det else
                f"d=15/18/20: 仅面板 {fmt(cv2['nose'][0]['r_min_panel'],1)}/{fmt(cv2['nose'][1]['r_min_panel'],1)}/"
                f"{fmt(cv2['nose'][2]['r_min_panel'],1)} K/W; 含 SoC {fmt(cv2['nose'][0]['r_min_pcb'],1)}/"
                f"{fmt(cv2['nose'][1]['r_min_pcb'],1)}/{fmt(cv2['nose'][2]['r_min_pcb'],1)} K/W"))

    # C16 —— X-3 限定语在位 (原句不许删)
    x3 = [ln for ln in budget.splitlines() if "**X-3**" in ln]
    ok = True
    det = []
    if not x3:
        ok = False
        det.append("结构真源找不到 X-3 行")
    else:
        ln = x3[0]
        if "不进皮肤热路径" not in ln:
            ok = False; det.append("X-3 原句「不进皮肤热路径」被删了 (不许删)")
        if "限定语" not in ln:
            ok = False; det.append("X-3 行缺「限定语」")
        for lit in ("454.8", "1101.2"):
            if lit not in ln:
                ok = False; det.append(f"X-3 行缺依据 '{lit}'")
        if "R_bridge" not in ln:
            ok = False; det.append("X-3 行缺热断要求 R_bridge")
    res.append(("C16", "X-3 限定语在位 (原句保留 + 限定语 + 依据 454.8/1101.2)", ok,
                "; ".join(det) if det else "限定语 + 依据在位, 原句「不进皮肤热路径」未删"))

    # C17 —— k=201 口径不许漂回 237
    ok = True
    det = []
    vb = _read(root, VB_REL)
    m = re.search(r"K_AL_6063_T6\s*=\s*([0-9.]+)", vb)
    if not m:
        ok = False
        det.append("verify_budget.py 里找不到 K_AL_6063_T6 常量")
    elif abs(float(m.group(1)) - 201.0) > 1e-9:
        ok = False
        det.append(f"verify_budget.py 的 K_AL_6063_T6 = {m.group(1)} (应 201.0)")
    if "k=**201**" not in budget:
        ok = False
        det.append("结构真源缺 'k=**201**'")
    live = []
    for line in budget.splitlines():
        if "237" not in line:
            continue
        if not any(w in line for w in ("判死", "作废", "已死", "旧口径", "已订正", "订正", "只留追溯")):
            live.append(line.strip()[:100])
    if live:
        ok = False
        det.append(f"结构真源有未标注的 237 残留: {live}")
    ep = _read(root, ENDPOINT_REL)
    if "现项目内口径" not in ep:
        ok = False
        det.append("ENDPOINT 模板缺「现项目内口径」标注")
    if "Hydro 6063_Rev.4" not in ep:
        ok = False
        det.append("ENDPOINT 模板缺 6063-T6 官方来源 (Hydro Rev.4)")
    res.append(("C17", "k=201 口径不许漂回 237 (脚本常量 / 结构真源 / ENDPOINT 模板三处)", ok,
                "; ".join(det) if det else
                f"verify_budget.py K_AL_6063_T6=201.0 · 结构真源 k=**201** 无活口径 237 · "
                f"ENDPOINT 模板已标「现项目内口径」"))

    # ================= ★ISS-222 新增 3 项判据 (只增, 既有 17 项一条没删) =================
    v3 = _read(root, V3_REL)
    cv3 = compute_v3(c, cv2)
    bn = budget.replace("−", "-").replace("—", "-").replace("**", "")
    v3n = v3.replace("−", "-").replace("—", "-").replace("**", "")

    # C18 —— C-6 落表: 规格不许漂回 14×10×6 / 0.79cc / 3-6g
    ok = True
    det = []
    m6 = [ln for ln in budget.splitlines() if ln.strip().startswith("| M6 |")]
    if not m6:
        ok = False
        det.append("结构真源找不到 §1.3 M6 行")
    else:
        row = m6[0]
        for lit in ("11 × 11 × 1.5", "0.9697"):
            if lit not in row:
                ok = False
                det.append(f"M6 行缺新规格 '{lit}'")
        if "14 × 10 × 6" in row and not any(w in row for w in ("作废", "旧值", "旧行")):
            ok = False
            det.append("M6 行里旧值 14×10×6 没标作废")
    w4 = [ln for ln in budget.splitlines() if ln.strip().startswith("| W4 |")]
    if not w4:
        ok = False
        det.append("结构真源找不到 §3 W4 行")
    elif "3.68-7.36" not in w4[0].replace("**", ""):
        ok = False
        det.append(f"§3 W4 行没有 3.68-7.36: {w4[0][:100]}")
    if "50.78 - 75.36" not in bn:
        ok = False
        det.append("结构真源 §3 合计没有 50.78 - 75.36")
    m = re.search(r"DOC_WEIGHT\s*=\s*\(([0-9.]+),\s*([0-9.]+)\)", vb)
    if not m:
        ok = False
        det.append("verify_budget.py 里找不到 DOC_WEIGHT")
    elif abs(float(m.group(1)) - 50.78) > 1e-9 or abs(float(m.group(2)) - 75.36) > 1e-9:
        ok = False
        det.append(f"verify_budget.py 的 DOC_WEIGHT = ({m.group(1)}, {m.group(2)}) (应 50.78, 75.36)")
    if "3.68, 7.36" not in vb:
        ok = False
        det.append("verify_budget.py 的 WEIGHT_ITEMS 里 W4 不是 (3.68, 7.36)")
    rows6 = {r["idx"]: r for r in parse_rows_pat(v3, r"C6-\d+")}
    if "C6-62" not in rows6:
        ok = False
        det.append("V3 交卷件缺 C6-62 行")
    else:
        cells = rows6["C6-62"]["cells"]
        if len(cells) != 9:
            ok = False
            det.append(f"C6-62 列数 {len(cells)} ≠ 9")
        else:
            w = cv3["c6"]
            if "11 × 11 × 1.5" not in cells[0]:
                ok = False
                det.append(f"C6-62 平板规格格 {cells[0]!r} ≠ 11 × 11 × 1.5")
            if "9 × 9 × 5" not in cells[2]:
                ok = False
                det.append(f"C6-62 棱镜规格格 {cells[2]!r} ≠ 9 × 9 × 5")
            want = [(1, w["plate_diag"], 4), (3, w["v_cc"], 4), (4, w["v_eng"], 4),
                    (5, w["w4_lo"], 2), (6, w["w4_hi"], 2), (7, w["m_ratio"], 4),
                    (8, w["fov_loss"], 2)]
            for ci, wv, nd in want:
                e = _cmp(cv3, cells[ci], wv, nd)
                if e:
                    ok = False
                    det.append(f"C6-62 第{ci+1}列 {e}")
                    break
    res.append(("C18", "C-6 落表不许漂回 (M6 11×11×1.5 / 0.9697 · W4 3.68-7.36 · 合计 50.78-75.36)", ok,
                "; ".join(det) if det else
                f"M6 = 平板 11×11×1.5 + 棱镜 2×9×9×5 · {fmt(cv3['c6']['v_cc'],4)} cc · "
                f"W4 {fmt(cv3['c6']['w4_lo'],2)}-{fmt(cv3['c6']['w4_hi'],2)} g · "
                f"DOC_WEIGHT (50.78, 75.36) · FOV 折减 {fmt(cv3['c6']['fov_loss'],2)}%"))

    # C19 —— C-8: t_s 轴向口径 + 三档 T 自洽 (活口径不许回退 6.0 / 11.0)
    ok = True
    det = []
    if abs(TS_AXIAL_MM - (SPL_PLATE_A_V3 * S45 + SPL_PLATE_T_V3 * C45)) > 1e-12:
        ok = False
        det.append("脚本常量 TS_AXIAL_MM 与 11·sin45°+1.5·cos45° 不符")
    rows8 = {r["idx"]: r for r in parse_rows_pat(v3, r"TS-\d")}
    if len(rows8) != 6:
        ok = False
        det.append(f"TS 行数 {len(rows8)} ≠ 6")
    else:
        for w in cv3["ts_rows"]:
            r = rows8.get(w["rid"])
            if r is None:
                ok = False
                det.append(f"缺 {w['rid']} 行")
                break
            cells = r["cells"]
            if len(cells) != 8:
                ok = False
                det.append(f"{w['rid']} 列数 {len(cells)} ≠ 8")
                break
            for ci, wv, nd in ((1, w["ts"], 4), (2, w["stack"], 4),
                               (3, w["slack"][0], 2), (4, w["slack"][1], 2), (5, w["slack"][2], 2)):
                e = _cmp(cv3, cells[ci], wv, nd, 0.006)
                if e:
                    ok = False
                    det.append(f"{w['rid']} 第{ci+1}列 {e}")
                    break
            if not ok:
                break
            if cells[6].strip() != str(sum(1 for x in w["ok"] if x)):
                ok = False
                det.append(f"{w['rid']} 活档数 {cells[6]!r} ≠ {sum(1 for x in w['ok'] if x)}")
                break
    if ok:
        # 旧口径必须标作废
        for rid, kw in (("TS-1", "作废"), ("TS-4", "作废")):
            cells = rows8[rid]["cells"]
            if kw not in cells[7]:
                ok = False
                det.append(f"{rid} 的处置列没写「{kw}」: {cells[7]!r}")
                break
    if ok:
        for lit in ("8.84", "-2.64", "0.36", "2.36", "2.16", "5.16", "7.16"):
            if lit not in bn:
                ok = False
                det.append(f"结构真源 §1.10.2 缺 '{lit}'")
                break
    if ok and "iss209_mech_d_value_decision" not in v3:
        ok = False
        det.append("V3 交卷件没带 d 取值的 need")
    res.append(("C19", "C-8 轴向口径 t_s 与三档 T 自洽 (活口径 8.84, 不许回退 6.0/11.0)", ok,
                "; ".join(det) if det else
                f"t_s = {fmt(TS_AXIAL_MM,4)} mm (45° 平板轴向投影) ⇒ 串联器件区 "
                f"{fmt(cv3['ts_rows'][2]['stack'],4)} ⇒ 余量 "
                f"{fmt(cv3['ts_rows'][2]['slack'][0],2)}/{fmt(cv3['ts_rows'][2]['slack'][1],2)}/"
                f"{fmt(cv3['ts_rows'][2]['slack'][2],2)}; 并排化 ⇒ 三档全活"))

    # C20 —— C-7: 净可外露面积 + 三条降级路径 + C-7b 结论有据
    ok = True
    det = []
    rowsa = {r["idx"]: r for r in parse_rows_pat(v3, r"A3-\d+")}
    if len(rowsa) != 5:
        ok = False
        det.append(f"A3 行数 {len(rowsa)} ≠ 5")
    else:
        want_a = {"A3-01": (cv3["a_nominal"], 120.0, 30.0),
                  "A3-02": (cv3["a_cam"], 14.0, 12.0),
                  "A3-03": (0.0, 0.0, 0.0),
                  "A3-04": (0.0, 0.0, 0.0),
                  "A3-05": (cv3["a_net"], 120.0, 30.0)}
        for rid, (area, ax, ay) in want_a.items():
            r = rowsa.get(rid)
            if r is None:
                ok = False
                det.append(f"缺 {rid} 行")
                break
            cells = r["cells"]
            if len(cells) != 5:
                ok = False
                det.append(f"{rid} 列数 {len(cells)} ≠ 5")
                break
            for ci, wv in ((1, ax), (2, ay), (3, area)):
                e = _cmp(cv3, cells[ci], wv, 2, 0.06)
                if e:
                    ok = False
                    det.append(f"{rid} 第{ci+1}列 {e}")
                    break
            if not ok:
                break
    if ok:
        rowsd = {r["idx"]: r for r in parse_rows_pat(v3, r"D3-\d+")}
        if len(rowsd) != 6:
            ok = False
            det.append(f"D3 行数 {len(rowsd)} ≠ 6")
        else:
            want_d = {
                "D3-01": (3600.0, 0.468, 9.72, cv3["t_a_lo"]),
                "D3-02": (3600.0, 0.50, 9.72, cv3["t_a_lo_50"]),
                "D3-03": (cv3["a_net"], 0.468, 0.0, cv3["t_print_nom"]),
                "D3-04": (cv3["a_net"], 0.468, 0.0, cv3["t_print_real"]),
                "D3-05": (cv3["a_req_415"][15.0], 0.415, 0.0, cv3["t_print_real_415"]),
                "D3-06": (600.0, 0.468, cv3["end_mass_lo"], cv3["t_c_lo"]),
            }
            for rid, (area, pw, mass, tc) in want_d.items():
                r = rowsd.get(rid)
                if r is None:
                    ok = False
                    det.append(f"缺 {rid} 行")
                    break
                cells = r["cells"]
                if len(cells) != 7:
                    ok = False
                    det.append(f"{rid} 列数 {len(cells)} ≠ 7")
                    break
                for ci, wv, nd, tol in ((1, area, 2, 0.06), (2, pw, 3, 0.0006),
                                        (3, mass, 2, 0.006), (4, tc, 2, 0.006)):
                    e = _cmp(cv3, cells[ci], wv, nd, tol)
                    if e:
                        ok = False
                        det.append(f"{rid} 第{ci+1}列 {e}")
                        break
                if not ok:
                    break
    if ok:
        for lit in ("3432", "23.30", "53.60"):
            if lit not in bn:
                ok = False
                det.append(f"结构真源 §1.10.3 缺 '{lit}'")
                break
    res.append(("C20", "C-7 结论有据 (净可外露 3432mm² · 三条路径逐格 · C-7b 53.60°C)", ok,
                "; ".join(det) if det else
                f"净可外露 {fmt(cv3['a_net'],0)} mm² (名义 {fmt(cv3['a_nominal'],0)} 的 "
                f"{fmt(cv3['a_net']/cv3['a_nominal']*100,1)}%); 铝背板 {fmt(cv3['t_a_lo'],2)} °C ✅ / "
                f"打印件+连通性 {fmt(cv3['t_print_real'],2)} °C ❌; W_rim ≥ "
                f"{fmt(cv3['w_req'][15.0],2)} mm"))

    # ================= ★ISS-227 新增 1 项判据 (只增, 既有 20 项一条没删) =================
    # C21 —— C-7b 集热面口径修正: 「打印件顶面不许被当成集热面」(材质字段必须是金属)
    #       + 三档 (d=15/18/20) 重算逐格 + u8 口径 + 旧数留痕 + 阈值不许动
    ok = True
    det = []

    # (1) 脚本常量侧: 活口径集热面材质必须是金属, 且不许是 print
    if SINK_SURFACE_MATERIAL not in SINK_SURFACE_METAL_ALLOWED:
        ok = False
        det.append(f"脚本活口径集热面材质 {SINK_SURFACE_MATERIAL!r} 不在金属白名单里")
    if SINK_SURFACE_MATERIAL == SINK_SURFACE_MATERIAL_LEGACY:
        ok = False
        det.append("脚本活口径集热面材质被改成了打印件 (print)")

    # (2) 判据阈值不许动 (脚本常量侧)
    if T_CAV_LIMIT_C != 50.0:
        ok = False
        det.append(f"腔体红线被改了: {T_CAV_LIMIT_C} (应 50.0)")
    if K_AL_6063_T6 != 201.0:
        ok = False
        det.append(f"铝 k 被改了: {K_AL_6063_T6} (应 201.0)")
    if (SINK_LX_MM, SINK_WRIM_MM) != C7B_BACKPLATE_GEOM[:2]:
        ok = False
        det.append(f"P3 几何被改了: {SINK_LX_MM}×{SINK_WRIM_MM} (应 120×30)")

    # (3) 文档侧: C-7b「集热面口径修正」必须独立成节
    # ★★2026-11-16 05:1x 续做修正 (main 实测抓到的真缺陷):
    #   原实现用 _section_text(doc, ["C-7b","集热面口径修正"]) ⇒ **命中的是 H1 文档标题**
    #   (第 1 行同时含这两个关键字) ⇒ 抓到的"节" = 整篇 349 行文档 ⇒
    #   「节存在性」断言变成**永远为真** ⇒ 反向 19「删掉整个 C-7b 节」抓不到任何一条
    #   ⇒ **门禁可被删节绕过**。⇒ 现在只认 **level>=2** 的小节标题 (min_level=2)。
    spans_c7b = _section_spans(v3, ["C-7b", "集热面口径修正"], min_level=2)
    if not spans_c7b:
        ok = False
        det.append("V3 交卷件缺 C-7b「集热面口径修正」独立节 (level>=2 的小节标题都没了)")
    elif len(spans_c7b) > 1:
        ok = False
        det.append(f"V3 里 C-7b「集热面口径修正」小节出现 {len(spans_c7b)} 次 (应唯一) ⇒ "
                   f"口径分叉: {[s[2][:40] for s in spans_c7b]}")
    sec = spans_c7b[0][3] if spans_c7b else ""

    if sec:
        # (4) 口径前后对比表: 4 行齐全
        rowsb = {r["idx"]: r for r in parse_rows_pat(sec, r"C7B-\d+")}
        if len(rowsb) != 4:
            ok = False
            det.append(f"C7B 行数 {len(rowsb)} ≠ 4")
        else:
            for w in cv3["c7b_rows"]:
                r = rowsb.get(w["rid"])
                if r is None:
                    ok = False
                    det.append(f"缺 {w['rid']} 行")
                    break
                cells = r["cells"]
                if len(cells) != 10:
                    ok = False
                    det.append(f"{w['rid']} 列数 {len(cells)} ≠ 10")
                    break
                mat = cells[1]
                if w["active"]:
                    # ★★机械判据: 活口径的集热面材质字段必须是金属, 打印件 ⇒ 红
                    if not any(k in mat for k in METAL_MATERIAL_KEYWORDS):
                        ok = False
                        det.append(f"{w['rid']} 活口径的集热面材质 {mat!r} 不是金属")
                        break
                    if any(k in mat for k in PRINT_MATERIAL_KEYWORDS):
                        ok = False
                        det.append(f"{w['rid']} 活口径的集热面材质 {mat!r} 出现打印件字样 "
                                   f"⇒ 打印件顶面不许被当成集热面")
                        break
                    if "活口径" not in cells[8]:
                        ok = False
                        det.append(f"{w['rid']} 活口径行没标「活口径」: {cells[8]!r}")
                        break
                else:
                    if not any(k in mat for k in PRINT_MATERIAL_KEYWORDS):
                        ok = False
                        det.append(f"{w['rid']} 旧口径行没写明是打印件 ({mat!r})")
                        break
                    if "已修正" not in cells[8] or "留痕" not in cells[8]:
                        ok = False
                        det.append(f"{w['rid']} 旧口径行没标「已修正 (留痕)」: {cells[8]!r}")
                        break
                for ci, wv, nd, tol in ((2, w["area"], 2, 0.06), (3, w["r_branch"], 2, 0.006),
                                        (4, w["t468"][15.0], 2, 0.006), (5, w["t468"][18.0], 2, 0.006),
                                        (6, w["t468"][20.0], 2, 0.006)):
                    e = _cmp(cv3, cells[ci], wv, nd, tol)
                    if e:
                        ok = False
                        det.append(f"{w['rid']} 第{ci+1}列 {e}")
                        break
                if not ok:
                    break
                mark = "✅" if all(w["ok"].values()) else "❌"
                if mark not in cells[7]:
                    ok = False
                    det.append(f"{w['rid']} 判定列 {cells[7]!r} 不含 {mark}")
                    break

        # (5) 三档重算的 u8 敏感度表 (5 行)
        if ok:
            rowsu = {r["idx"]: r for r in parse_rows_pat(sec, r"U8-\d+")}
            if len(rowsu) != 5:
                ok = False
                det.append(f"U8 行数 {len(rowsu)} ≠ 5")
            else:
                for i, w in enumerate(cv3["c7b_u8_rows"]):
                    rid = f"U8-0{i + 1}"
                    r = rowsu.get(rid)
                    if r is None:
                        ok = False
                        det.append(f"缺 {rid} 行")
                        break
                    cells = r["cells"]
                    if len(cells) != 9:
                        ok = False
                        det.append(f"{rid} 列数 {len(cells)} ≠ 9")
                        break
                    for ci, wv, nd, tol in ((0, w["u8"], 0, 1e-9), (1, w["r_branch"], 2, 0.006),
                                            (2, w["t468"][15.0], 2, 0.006), (3, w["t468"][18.0], 2, 0.006),
                                            (4, w["t468"][20.0], 2, 0.006), (5, w["t50"][15.0], 2, 0.006),
                                            (6, w["p_max"][15.0], 4, 0.00006)):
                        e = _cmp(cv3, cells[ci], wv, nd, tol)
                        if e:
                            ok = False
                            det.append(f"{rid} 第{ci+1}列 {e}")
                            break
                    if not ok:
                        break

        # (6) 需求侧余量表 (R7B-01~03): 三档余量逐格
        if ok:
            rowsm = {r["idx"]: r for r in parse_rows_pat(sec, r"R7B-\d+")}
            if len(rowsm) != 3:
                ok = False
                det.append(f"R7B 行数 {len(rowsm)} ≠ 3")
            else:
                for i, w in enumerate(cv3["c7b_margin"]):
                    rid = f"R7B-0{i + 1}"
                    r = rowsm.get(rid)
                    if r is None:
                        ok = False
                        det.append(f"缺 {rid} 行")
                        break
                    cells = r["cells"]
                    if len(cells) != 9:
                        ok = False
                        det.append(f"{rid} 列数 {len(cells)} ≠ 9")
                        break
                    for ci, wv, nd, tol in ((0, w["d"], 0, 1e-9), (1, w["r_branch_req"], 2, 0.006),
                                            (2, w["a_eq"], 2, 0.006), (3, w["a_need"], 2, 0.006),
                                            (4, w["d_area"], 2, 0.006), (5, w["d_area_pct"], 2, 0.06),
                                            (6, w["d_t"], 2, 0.006), (7, w["d_p"], 4, 0.00006)):
                        e = _cmp(cv3, cells[ci], wv, nd, tol)
                        if e:
                            ok = False
                            det.append(f"{rid} 第{ci+1}列 {e}")
                            break
                    if not ok:
                        break

        # (7) u8 口径必须写清
        if ok:
            for lit in ("u8 = 30", "30, 33, 35, 38, 40"):
                if lit not in sec:
                    ok = False
                    det.append(f"C-7b 节没写清 u8 口径 (缺 {lit!r})")
                    break

        # (8) 旧数不许被悄悄换掉 —— 留痕字面值必须在位
        if ok:
            for lit in ("53.60", "45.95", "46.63", "47.77", "已修正", "留痕"):
                if lit not in sec:
                    ok = False
                    det.append(f"C-7b 节缺留痕 / 新口径字面值 {lit!r}")
                    break

        # (9) 判据阈值字面不许被改
        if ok:
            if "50 °C" not in sec:
                ok = False
                det.append("C-7b 节没写腔体红线 50 °C")
            elif "55 °C" in sec or "55°C" in sec:
                ok = False
                det.append("C-7b 节出现 55 °C ⇒ 判据被改了")
            for lit in ("120×30", "k=201"):
                if lit not in sec:
                    ok = False
                    det.append(f"C-7b 节缺 {lit!r}")
                    break

    _c7b = {w["rid"]: w for w in cv3["c7b_rows"]}
    res.append(("C21", "C-7b 集热面口径修正 (材质必须金属 · 三档重算逐格 · u8 口径 · 旧数留痕 · 阈值不许动)", ok,
                "; ".join(det) if det else
                f"活口径 = {SINK_SURFACE_MATERIAL_CN} 背板 120×30×1.0 (鳍 R={fmt(cv3['r_bp_fin'],2)} K/W) ⇒ "
                f"d=15/18/20 = {fmt(_c7b['C7B-04']['t468'][15.0],2)}/{fmt(_c7b['C7B-04']['t468'][18.0],2)}/"
                f"{fmt(_c7b['C7B-04']['t468'][20.0],2)} °C ✅ (u8=30); "
                f"旧口径 打印件顶面 = {fmt(_c7b['C7B-03']['t468'][15.0],2)} °C ❌ (已修正·留痕)"))

    # ================= ★ISS-227 续做新增 1 项判据 (只增, 既有 21 项一条没删) =================
    # C22 —— C-7b「集热面口径修正」**整节存在性** (专查「删掉整节」这个绕过口子)
    #   ★★为什么必须有这一项 (2026-11-16 05:1x main 实测抓到的真缺陷):
    #     C21 原本用 _section_text(doc, ["C-7b","集热面口径修正"]) 抓节 ⇒ 命中的是
    #     **H1 文档标题** (第 1 行也同时含这两个关键字) ⇒ 抓到的是**整篇 349 行文档**
    #     ⇒ 「节存在性」断言变成**永远为真** ⇒ 反向 19「删掉整个 C-7b 节」一条都抓不到
    #     ⇒ ★**门禁可被删节绕过** ★
    #   ⇒ 现在 C21/C22 一律用 min_level=2 (只认真小节标题, 不认 H1), 且 C22 专查四件事:
    #     ① 该小节在文档里**唯一** (不许口径分叉) ② 12 行关键表行**住在节内**
    #     ③ 留痕/新口径关键字面值**住在节内** ④ 旧→新对比两边的材料**都在节内**
    ok22 = True
    det22 = []
    want22 = ({"C7B-01", "C7B-02", "C7B-03", "C7B-04"}
              | {f"U8-0{i}" for i in range(1, 6)}
              | {f"R7B-0{i}" for i in range(1, 4)})
    spans22 = _section_spans(v3, ["C-7b", "集热面口径修正"], min_level=2)
    if not spans22:
        ok22 = False
        det22.append("V3 交卷件里没有 level>=2 的「C-7b 集热面口径修正」小节 "
                      "⇒ 整节被删 / 被改名 / 被降级成正文")
    elif len(spans22) > 1:
        ok22 = False
        det22.append(f"「C-7b 集热面口径修正」小节出现 {len(spans22)} 次 ⇒ 口径分叉")
    else:
        sec22 = spans22[0][3]
        ids22 = set()
        for _pat in (r"C7B-\d+", r"U8-\d+", r"R7B-\d+"):
            for _r in parse_rows_pat(sec22, _pat):
                ids22.add(_r["idx"])
        miss22 = sorted(want22 - ids22)
        if miss22:
            ok22 = False
            det22.append(f"§2.5 节里缺关键表行 {miss22} ⇒ {len(want22)} 行关键表必须住在节内")
        for lit in ("53.60", "47.77", "u8 = 30", "120×30", "k=201", "已修正", "留痕"):
            if lit not in sec22:
                ok22 = False
                det22.append(f"§2.5 节里缺关键字面值 {lit!r}")
                break
        for lit in ("打印件", "铝制集热背板"):
            if lit not in sec22:
                ok22 = False
                det22.append(f"§2.5 节里缺 {lit!r} ⇒ 旧→新口径对比不全")
                break
    res.append(("C22", "C-7b 整节存在性 (小节唯一 · 12 行关键表住节内 · 留痕字面值在节内 · 旧→新对比齐)", ok22,
                "; ".join(det22) if det22 else
                f"§2.5 小节唯一在位 · {len(want22)} 行关键表 (C7B×4 / U8×5 / R7B×3) + "
                f"留痕与新口径字面值全住在节内"))

    # ================= ★ISS-237 闭环轮新增 1 项判据 (只增, 既有 22 项一条没删) =================
    # C23 —— C-7c: C-7 的唯一前置「W_rim」用活口径 (鳍模型) 实算的门槛 + 背板质量/整机重量账
    #   ★★为什么必须有这一项:
    #     ISS-222 §2.2 登记的 C-7 硬门槛 W_rim ≥ 23.30 mm 来自 lumped 模型 + 只按 0.468 W;
    #     ISS-227 已把活口径换成鳍模型 ⇒ 门槛在两个口径下不是一个数;
    #     而 ISS-216 的代表负载是 0.50 W ⇒ 按 23.30 裁框截面 ⇒ 0.50 W 下 50.67 °C ❌
    #     ⇒ ⇒ 门槛必须**两档** (面板功耗 / 代表负载) 且必须**进机器门禁**。
    ok23 = True
    det23 = []
    cc = compute_c7c(c, cv2, cv3)

    # (1) 阈值不许动 (脚本常量侧)
    if T_CAV_LIMIT_C != 50.0:
        ok23 = False
        det23.append(f"腔体红线被改了: {T_CAV_LIMIT_C} (应 50.0)")
    if K_AL_6063_T6 != 201.0:
        ok23 = False
        det23.append(f"铝 k 被改了: {K_AL_6063_T6} (应 201.0)")
    if (SINK_LX_MM, SINK_WRIM_MM, BACKPLATE_T_MM) != C7B_BACKPLATE_GEOM:
        ok23 = False
        det23.append(f"背板几何被改了: {SINK_LX_MM}×{SINK_WRIM_MM}×{BACKPLATE_T_MM} (应 120×30×1.0)")
    if abs(P_PANEL_W - 0.468) > 1e-9 or abs(P_COL_05W - 0.50) > 1e-9:
        ok23 = False
        det23.append(f"面板/代表负载被改了: {P_PANEL_W} / {P_COL_05W} (应 0.468 / 0.50)")

    # (2) §2.6 「C-7c」必须独立成节 (level>=2, 唯一)
    spans23 = _section_spans(v3, ["C-7c", "W_rim"], min_level=2)
    if not spans23:
        ok23 = False
        det23.append("V3 交卷件里没有 level>=2 的「C-7c」小节 ⇒ 整节被删 / 被改名")
    elif len(spans23) > 1:
        ok23 = False
        det23.append(f"「C-7c」小节出现 {len(spans23)} 次 ⇒ 口径分叉")
    sec23 = spans23[0][3] if spans23 else ""

    if sec23:
        # (3) 门槛表 W7T-01~05: 两档门槛逐格 + 旧登记门槛留痕
        rowst = {r["idx"]: r for r in parse_rows_pat(sec23, r"W7T-\d+")}
        want_t = {
            "W7T-01": (P_PANEL_W, cc["w_min_468"]),
            "W7T-02": (P_COL_05W, cc["w_min_500"]),
            "W7T-03": (P_PANEL_W, cc["w_min_468_no_relief"]),
            "W7T-04": (P_COL_05W, cc["w_min_500_no_relief"]),
        }
        if len(rowst) != 5:
            ok23 = False
            det23.append(f"W7T 行数 {len(rowst)} ≠ 5")
        else:
            for rid, (p_w, wmin) in want_t.items():
                r = rowst.get(rid)
                if r is None:
                    ok23 = False
                    det23.append(f"缺 {rid} 行")
                    break
                cells = r["cells"]
                if len(cells) != 5:
                    ok23 = False
                    det23.append(f"{rid} 列数 {len(cells)} ≠ 5")
                    break
                for ci, wv, nd, tol in ((1, p_w, 2, 0.006), (2, wmin, 2, 0.02)):
                    e = _cmp(cc, cells[ci], wv, nd, tol)
                    if e:
                        ok23 = False
                        det23.append(f"{rid} 第{ci+1}列 {e}")
                        break
                if not ok23:
                    break
            # 旧登记门槛 23.30 (只报不改 · 留痕)
            if ok23:
                r05 = rowst.get("W7T-05")
                if r05 is None or "23.30" not in r05["cells"][2]:
                    ok23 = False
                    det23.append("W7T-05 行缺 ISS-222 已登记的 23.30 (留痕)")
                elif "留痕" not in r05["cells"][3] and "留痕" not in r05["cells"][4]:
                    ok23 = False
                    det23.append("W7T-05 行没标「只报不改 (留痕)」")

        # (4) W_rim 扫描表 W7C-01~04: 逐格
        if ok23:
            rowsc = {r["idx"]: r for r in parse_rows_pat(sec23, r"W7C-\d+")}
            if len(rowsc) != 4:
                ok23 = False
                det23.append(f"W7C 行数 {len(rowsc)} ≠ 4")
            else:
                for i, w in enumerate(cc["rows"]):
                    rid = f"W7C-0{i + 1}"
                    r = rowsc.get(rid)
                    if r is None:
                        ok23 = False
                        det23.append(f"缺 {rid} 行")
                        break
                    cells = r["cells"]
                    if len(cells) != 11:
                        ok23 = False
                        det23.append(f"{rid} 列数 {len(cells)} ≠ 11")
                        break
                    for ci, wv, nd, tol in (
                            (0, w["w"], 2, 0.006), (1, w["a_bp"], 0, 0.6),
                            (2, w["m_bp"], 2, 0.006), (3, w["r_fin"], 2, 0.006),
                            (4, w["r_branch"], 2, 0.006), (5, w["t468"][15.0], 2, 0.006),
                            (6, w["t468"][18.0], 2, 0.006), (7, w["t468"][20.0], 2, 0.006),
                            (8, w["t50"], 2, 0.006), (9, w["p_max"], 4, 0.00006)):
                        e = _cmp(cc, cells[ci], wv, nd, tol)
                        if e:
                            ok23 = False
                            det23.append(f"{rid} 第{ci+1}列 {e}")
                            break
                    if not ok23:
                        break

        # (5) 背板质量 ⇒ 整机重量表 W7M-01~04: 逐格
        if ok23:
            rowsm = {r["idx"]: r for r in parse_rows_pat(sec23, r"W7M-\d+")}
            if len(rowsm) != 4:
                ok23 = False
                det23.append(f"W7M 行数 {len(rowsm)} ≠ 4")
            else:
                for i, w in enumerate(cc["rows"]):
                    rid = f"W7M-0{i + 1}"
                    r = rowsm.get(rid)
                    if r is None:
                        ok23 = False
                        det23.append(f"缺 {rid} 行")
                        break
                    cells = r["cells"]
                    if len(cells) != 5:
                        ok23 = False
                        det23.append(f"{rid} 列数 {len(cells)} ≠ 5")
                        break
                    for ci, wv, nd, tol in ((0, w["w"], 2, 0.006), (1, w["m_bp"], 2, 0.006),
                                            (2, w["w_total_lo"], 2, 0.006),
                                            (3, w["w_total_hi"], 2, 0.006)):
                        e = _cmp(cc, cells[ci], wv, nd, tol)
                        if e:
                            ok23 = False
                            det23.append(f"{rid} 第{ci+1}列 {e}")
                            break
                    if not ok23:
                        break

        # (6) 关键口径字面值必须住在节内 (门槛两档 + 旧登记门槛 + 质量线 + 打印件对照)
        if ok23:
            for lit in (fmt(cc["w_min_468"], 2), fmt(cc["w_min_500"], 2),
                        "23.30", "0.324", "50.67", "56.53"):
                if lit not in sec23:
                    ok23 = False
                    det23.append(f"§2.6 节里缺关键字面值 {lit!r}")
                    break
    res.append(("C23", "C-7c W_rim 门槛两档 (面板/0.5W) · 扫描表 · 背板质量与整机重量账 · 阈值不许动", ok23,
                "; ".join(det23) if det23 else
                f"W_rim 门槛 {fmt(cc['w_min_468'],2)} mm @0.468W / {fmt(cc['w_min_500'],2)} mm @0.50W; "
                f"背板 {fmt(cc['m_bp_per_mm'],3)} g/mm ⇒ 整机 {fmt(cc['rows'][0]['w_total_lo'],2)}-"
                f"{fmt(cc['rows'][-1]['w_total_hi'],2)} g"))

    return res


# ======================================================================
# §3 --selftest —— 反向用例 (全部在临时目录副本上做, 真文件不动)
# ======================================================================
def _make_copy(root: str, tmp: str) -> None:
    for rel in list(MD5_EXPECTED.keys()) + [DOC_REL, BUDGET_REL, FRAG_REL,
                                            V2_REL, VB_REL, ENDPOINT_REL, V3_REL]:
        src = os.path.join(root, rel)
        dst = os.path.join(tmp, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if os.path.exists(src):
            shutil.copy2(src, dst)


def _mutate_text(path: str, old: str, new: str, count: int = 1) -> None:
    with open(path, "r", encoding="utf-8") as f:
        t = f.read()
    if old not in t:
        raise AssertionError(f"变异点没找到: {old!r} @ {path}")
    t = t.replace(old, new, count)
    with open(path, "w", encoding="utf-8") as f:
        f.write(t)


def _set_row_cell(rel: str, rid: str, col: int, new_val: str, tmp: str = "") -> None:
    """按行号 + 数据列号改 V2 交卷件的一个单元格 (col = 0 起, 不含行号列)"""
    p = os.path.join(tmp, rel) if tmp else rel
    lines = open(p, encoding="utf-8").read().splitlines(True)
    for i, ln in enumerate(lines):
        if re.match(r"^\|\s*(\*\*)?" + re.escape(rid) + r"(\*\*)?\s*\|", ln):
            fields = ln.rstrip("\n").split("|")
            # fields[0] = '' · fields[1] = 行号 · fields[2] = 数据列 0
            fields[col + 2] = f" {new_val} "
            lines[i] = "|".join(fields) + "\n"
            break
    else:
        raise AssertionError(f"行 {rid} 没找到 @ {rel}")
    open(p, "w", encoding="utf-8").write("".join(lines))


def selftest(root: str) -> int:
    cases = []

    # 0 —— 基线必须全过
    res = check_all(root)
    cases.append(("基线: 全过", all(r[2] for r in res), "0 条不过"))

    def run_case(name: str, mutate, expect_cid):
        """expect_cid: str 或可迭代的 str 集合 ⇒ 命中其中任一条即算抓到。"""
        tmp = tempfile.mkdtemp(prefix="cavity_selftest_")
        try:
            _make_copy(root, tmp)
            mutate(tmp)
            r2 = check_all(tmp)
            bad = [r for r in r2 if not r[2]]
            exp = {expect_cid} if isinstance(expect_cid, str) else set(expect_cid)
            hit = any(r[0] in exp for r in bad)
            detail = ("抓到: " + ",".join(r[0] for r in bad)) if bad else "没抓到任何一条"
            cases.append((name, hit, f"{'/'.join(sorted(exp))} 未被抓; {detail}"))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def _set_field(tmp: str, rel: str, rid: str, field_index: int, new_val: str) -> None:
        """按表格行号 + 列号改一个单元格 (| R1 | d | A_e | ... |)"""
        p = os.path.join(tmp, rel)
        lines = open(p, encoding="utf-8").read().splitlines(True)
        for i, ln in enumerate(lines):
            if re.match(r"^\|\s*" + rid + r"\s*\|", ln):
                fields = ln.rstrip("\n").split("|")
                if field_index >= len(fields):
                    raise AssertionError(f"{rid} 没有第 {field_index} 列")
                fields[field_index] = f" {new_val} "
                lines[i] = "|".join(fields) + "\n"
                break
        else:
            raise AssertionError(f"行 {rid} 没找到 @ {rel}")
        open(p, "w", encoding="utf-8").write("".join(lines))

    def mut_row(tmp):
        _set_field(tmp, DOC_REL, "R1", 8, "17")          # T: 18 → 17

    def mut_62(tmp):
        p = os.path.join(tmp, BUDGET_REL)
        lines = open(p, encoding="utf-8").read().splitlines(True)
        for i, ln in enumerate(lines):
            if "**X-1**" in ln:
                assert "62 mm²" in ln
                lines[i] = ln.replace("62 mm²", "63 mm²")
                break
        else:
            raise AssertionError("X-1 行没找到")
        open(p, "w", encoding="utf-8").write("".join(lines))

    def mut_c1(tmp):
        _set_field(tmp, DOC_REL, "R1", 11, "3.3")        # C-1 冲突量: 3.2 → 3.3

    def mut_criteria(tmp):
        p = os.path.join(tmp, "MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md")
        with open(p, "a", encoding="utf-8") as f:
            f.write("\n<!-- tampered -->\n")

    def mut_drop_row(tmp):
        p = os.path.join(tmp, DOC_REL)
        lines = open(p, encoding="utf-8").read().splitlines(True)
        out = [ln for ln in lines if not re.match(r"^\|\s*R5\s*\|", ln)]
        assert len(out) < len(lines)
        open(p, "w", encoding="utf-8").write("".join(out))

    def mut_weight(tmp):
        p = os.path.join(tmp, DOC_REL)
        t = open(p, encoding="utf-8").read()
        t2 = t.replace("0.43", "0.93")
        assert t2 != t
        open(p, "w", encoding="utf-8").write(t2)

    def mut_frag(tmp):
        p = os.path.join(tmp, FRAG_REL)
        _mutate_text(p, "value: '25.00'", "value: '24.00'")

    def mut_script(tmp):
        p = os.path.join(tmp, "MECH/hinge_usb_check.py")
        with open(p, "a", encoding="utf-8") as f:
            f.write("\n# tampered\n")

    def mut_band(tmp):
        _set_field(tmp, DOC_REL, "B1", 2, "5")           # 带行程: 6 → 5

    # ---- ★ISS-219 新增 5 条反向用例 (既有 9 条一条没删) ----
    def mut_c6_vol(tmp):
        _set_row_cell(V2_REL, "C6-62", 8, "0.9999", tmp)   # 分光组件体积 0.9697 → 0.9999 cc

    def mut_c7_temp(tmp):
        _set_row_cell(V2_REL, "T-11", 4, "44.00", tmp)   # 腔体 @0.468W 46.63 → 44.00 °C

    def mut_rbridge(tmp):
        p = os.path.join(tmp, V2_REL)
        with open(p, "r", encoding="utf-8") as f:
            t = f.read()
        t2 = t.replace("454.8", "454.7")
        assert t2 != t
        with open(p, "w", encoding="utf-8") as f:
            f.write(t2)

    def mut_x3_qualifier(tmp):
        p = os.path.join(tmp, BUDGET_REL)
        lines = open(p, encoding="utf-8").read().splitlines(True)
        for i, ln in enumerate(lines):
            if "**X-3**" in ln:
                assert "454.8" in ln
                lines[i] = ln.replace("454.8", "—")
                break
        else:
            raise AssertionError("X-3 行没找到")
        open(p, "w", encoding="utf-8").write("".join(lines))

    def mut_k_back_237(tmp):
        _mutate_text(os.path.join(tmp, VB_REL), "K_AL_6063_T6 = 201.0", "K_AL_6063_T6 = 237.0")
        _mutate_text(os.path.join(tmp, BUDGET_REL), "k=**201**", "k=**237**")

    # ---- ★ISS-222 新增 3 条反向用例 (既有 14 条一条没删) ----
    def mut_c6_spec_drift(tmp):
        p = os.path.join(tmp, BUDGET_REL)
        lines = open(p, encoding="utf-8").read().splitlines(True)
        for i, ln in enumerate(lines):
            if ln.strip().startswith("| M6 |"):
                lines[i] = ln.replace("11 × 11 × 1.5", "10 × 10 × 1.5")
                break
        else:
            raise AssertionError("M6 行没找到")
        open(p, "w", encoding="utf-8").write("".join(lines))

    def mut_c8_slack(tmp):
        _set_row_cell(V3_REL, "TS-3", 3, "-2.00", tmp)     # 余量 @T=18: -2.64 → -2.00

    def mut_c7_area(tmp):
        _set_row_cell(V3_REL, "A3-05", 3, "3600", tmp)    # 净可外露: 3432 → 3600 mm²

    # ---- ★ISS-227 新增 4 条反向用例 (既有 17 条一条没删) ----
    def mut_c7b_material(tmp):
        # 活口径的集热面材质改回打印件 ⇒ 打印件顶面不许被当成集热面 ⇒ 红
        _set_row_cell(V3_REL, "C7B-04", 1, "打印件 PA-CF", tmp)

    def mut_c7b_drop_section(tmp):
        # ★删掉整个 C-7b「集热面口径修正」节 ⇒ 红
        # ★★2026-11-16 05:1x 续做修正 (原实现是**假用例**):
        #   原实现用 `"C-7b" in ln and "集热面口径修正" in ln` 找起点 ⇒ **先命中 H1 文档标题**
        #   (第 1 行也含这两个关键字) ⇒ 实际删掉的是**文档头部** (§0 之前那十几行),
        #   **§2.5 节根本没被删** ⇒ 门禁当然一条红都没有 ⇒ ★反向用例形同虚设★
        #   ⇒ 现在用 **level>=2 的真小节标题** 定位, 删到下一个同级/更高级标题为止。
        p = os.path.join(tmp, V3_REL)
        lines = open(p, encoding="utf-8").read().splitlines(True)
        start = None
        lvl = None
        for i, ln in enumerate(lines):
            m = re.match(r"^(#{2,6})\s+(.*)$", ln)
            if not m:
                continue
            head = m.group(2)
            if "C-7b" in head and "集热面口径修正" in head:
                start = i
                lvl = len(m.group(1))
                break
        assert start is not None, "C-7b 小节没找到"
        end = len(lines)
        for j in range(start + 1, len(lines)):
            m2 = re.match(r"^(#{1,6})\s", lines[j])
            if m2 and len(m2.group(1)) <= lvl:
                end = j
                break
        out = lines[:start] + lines[end:]
        assert len(out) < len(lines)
        # ★自证: 确认真的删掉了 §2.5 (而不是删错了地方)
        #   ★★2026-11-16 07:4x (ISS-237 闭环轮) 修正: 原来判 "C7B-04 还在" ⇒
        #   §2.6 的正文里也会**引用** C7B-04 (对照说明) ⇒ 断言会误报 ⇒
        #   改成只判「**表格行**还在」 (行首是 | C7B-04 / **C7B-04**)。
        assert not any(re.match(r"^\|\s*(\*\*)?C7B-04", ln) for ln in out), \
            "C7B-04 表格行还在 ⇒ 删错地方了"
        open(p, "w", encoding="utf-8").write("".join(out))

    def mut_c7b_drop_table(tmp):
        # ★删掉 §2.5 里的**关键表行** (C7B-01~04) 但**留着节标题** ⇒ 红
        #   (这一条抓的是「节还在但表没了」这种半吊子删改)
        p = os.path.join(tmp, V3_REL)
        lines = open(p, encoding="utf-8").read().splitlines(True)
        out = [ln for ln in lines if not re.match(r"^\|\s*(\*\*)?C7B-\d+", ln)]
        assert len(out) < len(lines)
        open(p, "w", encoding="utf-8").write("".join(out))

    def mut_c7b_rename_section(tmp):
        # ★把 §2.5 的**节标题改名** (内容留着, 但不再叫「集热面口径修正」) ⇒ 红
        p = os.path.join(tmp, V3_REL)
        lines = open(p, encoding="utf-8").read().splitlines(True)
        done = False
        for i, ln in enumerate(lines):
            m = re.match(r"^(#{2,6})\s+(.*)$", ln)
            if m and "C-7b" in m.group(2) and "集热面口径修正" in m.group(2):
                lines[i] = m.group(1) + " 2.5 ★ C-7b 热学口径小结\n"
                done = True
                break
        assert done, "C-7b 小节标题没找到"
        open(p, "w", encoding="utf-8").write("".join(lines))

    def mut_c7b_threshold(tmp):
        # 把腔体红线 50 °C 改成 55 °C ⇒ 判据阈值不许动 ⇒ 红
        p = os.path.join(tmp, V3_REL)
        t = open(p, encoding="utf-8").read()
        t2 = t.replace("50 °C", "55 °C")
        assert t2 != t
        open(p, "w", encoding="utf-8").write(t2)

    def mut_c7b_temp(tmp):
        # 改坏活口径三档重算的 d=15 温度 (47.77 → 47.00 °C) ⇒ 红
        _set_row_cell(V3_REL, "C7B-04", 4, "47.00", tmp)

    # ---- ★ISS-237 闭环轮新增 3 条反向用例 (既有 23 条一条没删) ----
    def _mutate_in_section(tmp: str, rel: str, keys, min_level: int,
                           old: str, new: str, count: int = 1) -> None:
        """在指定小节**内部**改字面值 (不许误伤别的节)

        ★★行下标 vs 字符下标 (2026-11-16 07:5x 自己踩的坑):
          _section_spans 返回的 (i0, i1) 是**行下标** ⇒ 必须按行切片;
          之前写成 text[:i0] + sec2 + text[i1:] (当字符下标用) ⇒ 文件被截断成乱码
          ⇒ 反而一条红都不报 (反向用例形同虚设) ⇒ 现在按行拼。
        """
        p = os.path.join(tmp, rel)
        lines = open(p, encoding="utf-8").read().splitlines(True)
        text = "".join(lines)
        spans = _section_spans(text, keys, min_level=min_level)
        assert spans, f"小节 {keys} 没找到"
        i0, i1, head, _sec = spans[0]
        body = "".join(lines[i0:i1])
        assert old in body, f"变异点 {old!r} 不在 §{head[:30]!r} 节内"
        body2 = body.replace(old, new, count)
        out = lines[:i0] + [body2] + lines[i1:]
        open(p, "w", encoding="utf-8").write("".join(out))

    def mut_c7c_threshold(tmp):
        # 改坏 C-7c 的 W_rim 门槛 (面板功耗档 22.15 → 20.00) ⇒ 红
        _mutate_in_section(tmp, V3_REL, ["C-7c"], 2, "22.15", "20.00")

    def mut_c7c_weight(tmp):
        # 改坏 C-7c 的整机重量数 (60.50 → 60.00) ⇒ 红
        _mutate_in_section(tmp, V3_REL, ["C-7c"], 2, "60.50", "60.00")

    def mut_c7c_drop_section(tmp):
        # ★删掉整个 §2.6「C-7c」节 ⇒ 红 (自证: 确认真的删掉了 §2.6)
        p = os.path.join(tmp, V3_REL)
        lines = open(p, encoding="utf-8").read().splitlines(True)
        start = None
        lvl = None
        for i, ln in enumerate(lines):
            m = re.match(r"^(#{2,6})\s+(.*)$", ln)
            if not m:
                continue
            if "C-7c" in m.group(2):
                start = i
                lvl = len(m.group(1))
                break
        assert start is not None, "C-7c 小节没找到"
        end = len(lines)
        for j in range(start + 1, len(lines)):
            m2 = re.match(r"^(#{1,6})\s", lines[j])
            if m2 and len(m2.group(1)) <= lvl:
                end = j
                break
        out = lines[:start] + lines[end:]
        assert len(out) < len(lines)
        assert not any(("W7C-04" in ln) for ln in out), "W7C-04 行还在 ⇒ 删错地方了"
        open(p, "w", encoding="utf-8").write("".join(out))

    run_case("反向1: 改坏一行参数表 (R1 的 T 18 → 17)", mut_row, "C2")
    run_case("反向2: 删掉 62 (结构真源 X-1 行 62 → 63 mm²)", mut_62, "C1")
    run_case("反向3: 改坏冲突量 (R1 的 C-1 3.2 → 3.3)", mut_c1, "C2")
    run_case("反向4: 篡改判据文件 DISPLAY_BIOSAFETY_CRITERIA_V2.md", mut_criteria, "C4")
    run_case("反向5: 删掉一行表 (R5)", mut_drop_row, "C2")
    run_case("反向6: 改坏重量重核数 (0.43 → 0.93)", mut_weight, "C6")
    run_case("反向7: 篡改分片 claim (25.00 → 24.00)", mut_frag, "C9")
    run_case("反向8: 篡改受保护脚本 hinge_usb_check.py", mut_script, "C8")
    run_case("反向9: 改掉 ±3 mm 带 (B1 行程 6 → 5)", mut_band, "C5")
    run_case("反向10: 改坏 C-6 分光件体积 (0.9697 → 0.9999 cc)", mut_c6_vol, "C13")
    run_case("反向11: 改坏 C-7 腔体温度 (T-11 的 46.63 → 44.00 °C)", mut_c7_temp, "C14")
    run_case("反向12: 改坏鼻梁 R_bridge 反解值 (454.8 → 454.7 K/W)", mut_rbridge, "C15")
    run_case("反向13: 删掉 X-3 限定语里的依据 (454.8 → —)", mut_x3_qualifier, "C16")
    run_case("反向14: 把 k 口径漂回 237 (脚本常量 + 结构真源)", mut_k_back_237, "C17")
    run_case("反向15: 把 C-6 的 M6 规格漂回旧平板 (11×11×1.5 → 10×10×1.5)", mut_c6_spec_drift, "C18")
    run_case("反向16: 改坏 C-8 的 t_s 三档余量 (TS-3 的 -2.64 → -2.00)", mut_c8_slack, "C19")
    run_case("反向17: 改坏 C-7 的净可外露面积 (A3-05 的 3432 → 3600 mm²)", mut_c7_area, "C20")
    run_case("反向18: 把活口径的集热面材质改回打印件 (C7B-04 → 打印件 PA-CF)", mut_c7b_material, "C21")
    run_case("反向19: 删掉整个 C-7b「集热面口径修正」节", mut_c7b_drop_section, ("C21", "C22"))
    run_case("反向20: 把腔体红线 50 °C 改成 55 °C", mut_c7b_threshold, "C21")
    run_case("反向21: 改坏活口径三档重算的 d=15 温度 (C7B-04 的 47.77 → 47.00 °C)", mut_c7b_temp, "C21")
    # ---- ★ISS-227 续做新增 2 条反向用例 (既有 21 条一条没删) ----
    run_case("反向22: 删掉 §2.5 里的关键表行 (C7B-01~04 四行) 但留着节标题", mut_c7b_drop_table, "C22")
    run_case("反向23: 把 §2.5 的节标题改名 (内容留着, 但不再叫「集热面口径修正」)", mut_c7b_rename_section, "C22")
    # ---- ★ISS-237 闭环轮新增 3 条反向用例 (既有 23 条一条没删) ----
    run_case("反向24: 改坏 C-7c 的 W_rim 门槛 (面板功耗档 22.15 → 20.00)", mut_c7c_threshold, "C23")
    run_case("反向25: 改坏 C-7c 的整机重量数 (60.50 → 60.00)", mut_c7c_weight, "C23")
    run_case("反向26: 删掉整个 §2.6「C-7c」节", mut_c7c_drop_section, "C23")

    npass = sum(1 for _, ok, _ in cases if ok)
    print("=== cavity_recalc_check --selftest ===")
    for name, ok, detail in cases:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}  ({detail})")
    print(f"=== {npass}/{len(cases)} ===")
    return 0 if npass == len(cases) else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--emit-rows", action="store_true")
    ap.add_argument("--root", default=REPO)
    args = ap.parse_args()
    if args.emit_rows:
        print(emit_rows())
        return 0
    if args.selftest:
        return selftest(args.root)
    res = check_all(args.root)
    print("=== cavity_recalc_check ===")
    npass = 0
    for cid, name, ok, det in res:
        npass += 1 if ok else 0
        print(f"  [{'PASS' if ok else 'FAIL'}] {cid} {name} :: {det}")
    print(f"=== {npass}/{len(res)} ===")
    return 0 if npass == len(res) else 1


if __name__ == "__main__":
    sys.exit(main())
