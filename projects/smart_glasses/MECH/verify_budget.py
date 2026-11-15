#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MECH_BUDGET.md 关键数字自证脚本 (交接单 B6 用)
======================================================================
用途: 别人一条命令复算我的空间 / 散热 / 重量 / 摄像头 关键数字,
      并自动对表 MECH_BUDGET.md 里发布的数字 (不一致就打印 ⚠ 并把 rc 置 2)。

用法:
    cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
    python3 MECH/verify_budget.py                 # 复算 + 逐项对表 (全绿 rc=0)
    python3 MECH/verify_budget.py --selftest       # 反向用例: 改坏口径必须变红

★ISS-216 (2026-11-16) 新增: **充电耗散口径自检**
  · 旧口径: `P_CHARGE = 0.8` (线性充电 IC 公式 (5−4.2)V × 1A) ⇒ **对板上真实
    器件 BQ25896 (开关型 buck) 不适用, 已判死**;
  · 新口径: `P_CHARGE = 0.50` (buck, 耗散 = Pin − Pout + P_DCR), 区间 **0.45-0.57 W**;
  · §8 组自检 (C1~C9) 盯着"口径 = buck 而不是线性": 脚本常量 + MECH_BUDGET.md
    正文两处都要对 ⇒ 任何一处退回线性口径 ⇒ 立刻变红;
  · `--selftest` 6 个反向用例 (把常量改回 0.8 / 改区间 / 改拓扑标识 / 改文档内容 …)
    必须全部被抓到。

原则:
  * 纯 Python3, 无第三方依赖, 无网络
  * 所有输入参数在文件里显式列出 (可逐项核对), 不藏魔法数
  * 推算项标 [推算]; 直接取自官网的标 [官网]; 网表实读的标 [实测]
  * 退出码: 0 = 全部对拍一致 + 口径自检全过 (门禁绿);
            2 = 有对拍不一致 / 口径自检不过 / 脚本自身算错 (门禁红)

作者: mech-lead (结构和散热) · 2026-10-25 第二轮整改
     · 2026-11-16 ISS-216: 充电耗散口径 线性 0.8W → buck 0.45-0.57W (代表值 0.50W)
======================================================================
"""

import argparse
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
BUDGET_MD = os.path.join(HERE, "MECH_BUDGET.md")

# ======================================================================
# 0. 输入参数 (全部显式列出, 与 MECH_BUDGET.md 表格一一对应)
# ======================================================================

# ---- 热模型 (§2.3) ----
T_AMB = 35.0            # [推算] 环境/体温基准, MECH_BUDGET §2.3
T_WALL = 0.0008         # m   [推算] 外壳壁厚 0.8mm (P2S 4 圈 0.4 喷嘴)
K_WALL = 0.2            # W/m·K [推算] PA-CF/PC-CF 打印件 k=0.2
A_SKIN = 320e-6         # m²  [推算] 皮肤接触面积 40×8mm
H_SKIN = 75.0           # W/m²·K [推算] 皮肤界面换热系数
A_CONV = 150e-6         # m²  [推算] 镜腿外表面自然对流面积
H_CONV = 10.0           # W/m²·K [推算] 自然对流
T_LIMIT_RED = 43.0      # °C  [官网] ISO 13732-1 / CENELEC Guide 29 Table A.1 (8h+ 接触)
T_LIMIT_DESIGN = 40.0   # °C  [推算] 本项目设计目标 (留 3-5°C 裕量)

# ---- 功耗场景 (§2.1) ----
P_FULL = 1.22           # W [推算] 持续满载中位 (0.85-1.52W)
P_FULL_HI = 1.52        # W [推算] 持续满载上界
P_AVG_ON_DEMAND = 0.23  # W [推算] 方案 C 按需触发平均功耗
P_STANDBY = 0.15        # W [推算] 方案 C 里的待机功耗

# ======================================================================
# 0b. ★充电耗散口径 (ISS-216 · 2026-11-16) — 板上真实拓扑 = 开关型 buck
# ----------------------------------------------------------------------
# ★**旧口径 (0.8 W) 已判死**: (5−4.2)V × 1A 是**线性充电 IC** 的公式。
#   板上充电板 P10 装的是 **TI BQ25896** ([实测] 网表 HW/netlist_v1.csv P10:
#   U_CHG / SW / L_CHG / C_BST / PMID ⇒ 开关型变换器) ⇒ 耗散必须按
#   **P = Pin − Pout + P_DCR** 算, 不存在 (Vin−Vout)·I 这种线性压降项。
# ★**器件本体是 buck-boost (4 开关)**, 但本项目 VBUS=5V / VBAT=3.7-4.2V 工况下
#   占空比 D = VBAT/VBUS = 0.74-0.84 < 1 ⇒ **工作在降压 (buck) 档** ⇒
#   功率守恒式 Pout = η·Pin 成立, 耗散口径按 buck 计。
# ======================================================================
CHG_IC = "BQ25896"               # 板上真实充电 IC [实测] 网表 P10
CHG_TOPOLOGY = "buck"            # ★口径标识 (自检 C1 盯着它)
CHG_VBUS = 5.0                   # V  [官网] Type-C 默认 5V 档
CHG_VBAT = 3.70                  # V  [官网] 单节锂电 CC 段起始 (耗散最坏工况)
CHG_VBAT_CV = 4.20               # V  [官网] 单节锂电 CV 段终止
CHG_ETA = 0.90                   # [官网] BQ25896 充电效率 (92.5%@2A / 90.5%@3A ⇒ 1A 档保守取 0.90)
CHG_R_ILIM = 390.0               # Ω  [实测] 网表 R_ILIM = 390Ω
CHG_K_ILIM = (320.0, 355.0, 390.0)   # A·Ω [官网] BQ25896 KILIM (min/typ/max), IINMAX = KILIM/RILIM
CHG_R_DCR = 0.050                # Ω  [推算] 充电电感/磁珠 DCR ≤ 50 mΩ (HW/CHARGE_BOARD_SPEC 待选型-3)
# ★**已定耗散区间** (ISS-213 §5.3 / ISS-089 自-4): 0.45-0.57 W
P_CHARGE_LO, P_CHARGE_HI = 0.45, 0.57
# ★**代表值 = 0.50 W** = ISS-213 机器门禁锚点 (MECH/check_demo_struct_truth.py
#   anchors.thermal.p_buck_w = 0.50 ⇒ ΔT 83.33K ⇒ 端件表面 108.33°C)
P_CHARGE = 0.50

# ---- 端件外表面 (ISS-213 §5.3, 只引用不改) ----
ENDPIECE_R_CONV = 166.667        # K/W [推算] 1/(10 W/m²K × 0.030×0.020 m²)
ENDPIECE_T_AMBIENT = 25.0        # °C  [推算]
ENDPIECE_T_LIMIT = 60.0          # °C  [推算] 端件外表面判据 (烫手)
ENDPIECE_P_MAX = 0.21            # W  [推算] (60−25)/166.667

# ---- ★ISS-219 (2026-11-16) 金属热路 k 口径订正: 237 → 201 (官方保守侧) ----
# 旧口径 k=237 (项目内乐观值) 已于 ISS-219 订正为 **201 W/m·K** (6063-T6 官方值)。
# 官方来源 (三家独立厂商官网互证, [官网]):
#   · Hydro Innovation & Technology: "Hydro 6063_Rev.4 – 03/2023",
#     Technical datasheet - Extruded products, Alloy EN AW-6063 [AlMg0.7Si]
#     https://www.hydro.com/globalassets/08-about-hydro/hydro-worldwide/austria/nenzing/
#       alloy-data-sheets/hydro-en-aw-6063.pdf
#     (T6: Thermal Conductivity 201 W/m·K, Density 2.70 g/cm³; 依 EN 755-2:2016 /
#      EN-573-3:2013; 参考 MNC Handbok nr 12 version 2, SIS 1989)
#   · Aalco: Aluminium Alloy 6063 - T6 Extrusions datasheet (Spec BS EN 755-2:2008)
#     https://www.aalco.co.uk/datasheets/Aluminium-Alloy-6063-T6-Extrusions_158.ashx
#   · Kaiser Aluminum: Tube & Pipe Alloy 6063 Technical Data Rev. 05/06
#     https://online.kaiseraluminum.com/depot/PublicProductInformation/Document/1066/
#       Kaiser_Aluminum_6063_Tube_and_Pipe.pdf
K_AL_6063_T6 = 201.0             # W/m·K [官网] 6063-T6 (ISS-219 订正; 旧口径 237 已作废)
K_AL_6063_T6_LEGACY = 237.0      # W/m·K [旧口径·已订正] 只留追溯, 不许当活口径用
RHO_AL_6063_T6 = 2.70e-3         # g/mm³ [官网] 2.70 g/cm³
ENDPOINT_GEOM_L_MM = 70.0        # mm  沿臂长 (ISS-213 §5.4 同几何口径)
ENDPOINT_GEOM_A_MM2 = 180.0      # mm² 同几何截面积
# ★**只改口径, 不改结论**: 同几何 R 1.641 → 1.935 K/W; 打印件 PA6-CF 1944 K/W 仍然出局;
#   R_热路 ≤ 70 K/W ⇒ 截面积 A ≥ 4.9751 mm² (201 侧; 旧 237 侧 4.2194) ⇒ 2.0×2.0 铝条仍不合格。
R_AL_201 = ENDPOINT_GEOM_L_MM * 1000.0 / (K_AL_6063_T6 * ENDPOINT_GEOM_A_MM2)      # K/W
R_AL_237 = ENDPOINT_GEOM_L_MM * 1000.0 / (K_AL_6063_T6_LEGACY * ENDPOINT_GEOM_A_MM2)  # K/W
R_PRINT_6063 = ENDPOINT_GEOM_L_MM * 1000.0 / (K_WALL * ENDPOINT_GEOM_A_MM2)        # K/W (打印件)
A_MIN_R70_201 = ENDPOINT_GEOM_L_MM * 1000.0 / (K_AL_6063_T6 * 70.0)                 # mm²
A_MIN_R70_237 = ENDPOINT_GEOM_L_MM * 1000.0 / (K_AL_6063_T6_LEGACY * 70.0)          # mm²
R_PATH_MAX_KW = 70.0            # K/W [推算] ISS-216 §3 注 / ISS-218 §1.1 硬指标

# ---- 电池三档位 (§1.6.2 / §1.6.3) ----
# 电池厚度/长度: 340mAh 用 Renata ICP582035PR-01 [官网] 4.6×23.5×40.5
#                 575/675mAh 尚无具体型号 -> 厚度/长度为 [推算] 输入假设 (脚本里已标)
PCB_L, PCB_W, PCB_T = 50.0, 12.0, 0.8      # mm
PCB_CC = PCB_L * PCB_W * PCB_T / 1000.0    # cc
CB_L, CB_CC = 25.0, 0.20                   # 充电板 25×10×0.8mm [推算]
TYPEC_CC, CONN_CC = 0.02, 0.15             # Type-C 座 + BTB/FPC 连接器 [推算]
WIRE_CHANNEL = 6.0 * 2.0 * 130.0 / 1000.0  # cc 走线槽 6×2mm × 130mm
ASSY_FACTOR = 1.15                        # 装配公差/隔热/散热间隙 +15% [推算]
SHELL_WALL = 0.8                          # mm  外壳单壁
TIM_PAD = 0.3                             # mm  导热垫 (仅 SoC 区)
LEN_MARGIN = 15.0                         # mm  连接器/弯折/插拔余量
CAVITY_LEN = 130.0                        # mm  镜脚内腔长度基准

TIERS = [
    # 名,        电池厚mm, 电池长mm, 电池体积cc(min,max), 文档内腔cc, 文档厚, 文档长含CB, 文档长挪CB后
    # 340mAh: Renata ICP582035PR-01 4.6×23.5×40.5 [官网] → 厚度是实测官网值
    # 575/675mAh: 尚无具体型号 → 厚度/长度是 [推算] 输入假设 (与 §1.6.2 的叠层反推一致)
    ("340mAh", 4.6, 40.5, (3.3, 4.4), (7.0, 7.6), 7.3, 130, 106),
    ("575mAh", 6.0, 45.0, (5.6, 6.5), (8.3, 9.0), 8.7, 135, 110),
    ("675mAh", 8.5, 43.0, (6.6, 7.7), (10.7, 11.4), 11.2, 132, 108),
]

# ---- 重量表 (§3) ----
WEIGHT_ITEMS = [
    # 名, 单重g(min,max), 证据
    ("光机 走鹃Ⅱ", 0.5, 0.5, "[官网]"),
    ("衍射光波导 ×2", 7.0, 9.4, "[展会]/[官网]"),
    ("摄像头模组", 1.5, 3.0, "[推算]"),
    ("一拖二分光件", 3.68, 7.36, "[推算] (ISS-222 C-6 落地: 0.9697 cc)"),
    ("ARS45 主 PCB", 5.0, 7.0, "[推算]"),
    ("充电板+Type-C+屏蔽罩", 2.0, 3.0, "[推算]"),
    ("电池 420mAh", 6.0, 6.0, "[推算]"),
    ("FPC+BTB 连接器", 2.0, 3.0, "[推算]"),
    ("镜框 (打印)", 9.0, 14.0, "[推算]"),
    ("镜腿 ×2 (打印+骨架+石墨)", 12.0, 18.0, "[推算]"),
    ("石墨膜+导热垫+隔热垫", 1.0, 2.0, "[推算]"),
    ("紧固件/螺钉/UV胶/泡棉", 1.0, 2.0, "[推算]"),
    ("MEMS 麦克风 ×2", 0.1, 0.1, "[推算]"),
]
DOC_WEIGHT = (50.78, 75.36)   # §3 合计 (第二轮更正后 + ISS-222 C-6 落地: W4 3-6 → 3.68-7.36 g)

# ---- ★ISS-222 (2026-11-16) C-6 落地常量 (分光件规格不许漂回 14×10×6 / 0.79cc / 3-6g) ----
SPL_PLATE_V3 = (11.0, 11.0, 1.5)     # 45° 半透半反平板 (C-6)
SPL_PRISM_V3 = (9.0, 9.0, 5.0)       # 转向棱镜 ×2 (C-6)
SPL_V_CC_V3 = 0.9697                 # 分光组件体积 (连续口径)
SPL_V_CC_V3_ENG = 0.9915             # 工程取值 (11×11×1.5 + 2×9×9×5)
SPL_W4_V3 = (3.68, 7.36)             # §3 W4 新带
SPL_PLATE_DIAG_V3 = 15.5563          # 11√2 (≥ 严格口径 15.3890)
FOV_LOSS_PCT_V3 = 2.63               # (1 − M) × 100, M = 0.9737
#: ★ISS-222 C-8: 分光件在正中区前后向 (轴向) 的占位 = 45° 平板的轴向投影
TS_AXIAL_MM_V3 = 11.0 * math.sin(math.radians(45.0)) + 1.5 * math.cos(math.radians(45.0))

# ---- 摄像头几何 (§1.5) ----
CAM_D = 32.0                # mm 镜头到眼点距离 (镜眼距12-14 + 镜片/镜框厚度)
CAM_H = (12.0, 15.0, 20.0)  # mm 镜头中心高于视线
DIAG_FOV = (100.0, 110.0, 120.0)
ASPECT = (16, 9)
DOC_TILT = {12.0: 20.6, 15.0: 25.1, 20.0: 32.0}
DOC_FOV_SPLIT = {100.0: (92.2, 60.6), 110.0: (102.4, 70.0), 120.0: (113.0, 80.7)}
RECESS_MM = (0.0, 1.5, 3.0, 5.0)
D_OCCLUDE = 30.0            # mm §1.5.1 遮挡计算用的 d (文档口径 25-35mm 取中值 30)
DOC_OCCLUDE = {1.5: 2.9, 3.0: 5.7, 5.0: 9.5}

# ---- 截面 / 长度叠层 (§1.4.2) ----
BAT_T420 = 4.3              # mm 丰江 432243 [官网]
DOC_STACK_H = 7.0
DOC_STACK_V = 37.0
DOC_LEN_STACK = 133.5

# ---- 分光件角度公差 (§1.2) ----
ARM_L = 40.0                # mm 臂长
TOL_DEG = (0.25, 0.5, 1.0)
DOC_TOL_MM = {0.25: 0.175, 0.5: 0.349, 1.0: 0.698}

# ======================================================================
# 1. 稳态热模型 (§2.3)
# ======================================================================
R_WALL = T_WALL / (K_WALL * A_SKIN)      # 壳壁热阻
R_SKIN_IF = 1.0 / (H_SKIN * A_SKIN)       # 皮肤界面热阻
R_SKIN_PATH = R_WALL + R_SKIN_IF          # 结/壳 -> 皮肤 总热阻
R_CONV = 1.0 / (H_CONV * A_CONV)          # 对流热阻
FRAC_SKIN = R_CONV / (R_SKIN_PATH + R_CONV)   # 进入皮肤的热量比例


def skin_temp_main(p):
    """主模型 (与 MECH_BUDGET §2.3 表一致): 壳壁热阻计入皮肤侧 -> 偏保守"""
    return T_AMB + p * R_SKIN_PATH * FRAC_SKIN


def skin_temp_var(p):
    """变体 (敏感性): 壳壁热阻从皮肤侧剥离, 只算皮肤界面 41.7 K/W"""
    return T_AMB + (p * FRAC_SKIN) * R_SKIN_IF


def power_for_limit(model_fn, limit):
    """反解: 皮肤侧温度 = limit 时的持续功耗上限"""
    return (limit - T_AMB) / ((R_SKIN_PATH * FRAC_SKIN) if model_fn is skin_temp_main
                              else (FRAC_SKIN * R_SKIN_IF))


# ======================================================================
# 1b. ★buck 充电耗散模型 (ISS-216) —— P = Pin − Pout + P_DCR
# ======================================================================
def charge_dissipation(i_in, v_bat=None, eta=None, r_dcr=None):
    """开关型 buck 充电耗散。

    返回 (P_diss, ICHG, Pin, Pout, P_DCR):
      ICHG = eta · VBUS · IIN / VBAT   (功率守恒, 降压 ⇒ ICHG > IIN)
      Pin  = VBUS · IIN
      Pout = VBAT · ICHG = eta · Pin
      P_DCR = ICHG² · R_DCR            (充电电感铜损)
    ★线性口径 (Vin−Vout)·I 不适用 (那是线性稳压器公式)。

    ★注意: 默认值必须在**调用时**解析 (不能写成 def f(x, eta=CHG_ETA) —— 那会在 def 时
      就把全局值冻住 ⇒ --selftest 的反向用例改不动它 ⇒ 门禁形同虚设)。
    """
    if v_bat is None:
        v_bat = CHG_VBAT
    if eta is None:
        eta = CHG_ETA
    if r_dcr is None:
        r_dcr = CHG_R_DCR
    i_chg = eta * CHG_VBUS * i_in / v_bat
    p_in = CHG_VBUS * i_in
    p_out = v_bat * i_chg
    p_dcr = i_chg * i_chg * r_dcr
    return p_in - p_out + p_dcr, i_chg, p_in, p_out, p_dcr


def iin_from_rilim(k_ilim, r_ilim=CHG_R_ILIM):
    """IINMAX = KILIM / RILIM  [官网] BQ25896"""
    return k_ilim / r_ilim


def charge_band():
    """三档 IIN (min/typ/max, 由 KILIM 与 RILIM 决定) 下的 buck 耗散。"""
    rows = []
    for tag, k in zip(("min", "typ", "max"), CHG_K_ILIM):
        i_in = iin_from_rilim(k)
        p, i_chg, p_in, p_out, p_dcr = charge_dissipation(i_in)
        rows.append(dict(tag=tag, k=k, i_in=i_in, i_chg=i_chg,
                         p_in=p_in, p_out=p_out, p_dcr=p_dcr, p=p))
    return rows


def charge_ratio(v_bat):
    """ICHG / IIN = eta · VBUS / VBAT (规格书里写的 0.822/0.933 是倒数)"""
    return CHG_ETA * CHG_VBUS / v_bat


# ======================================================================
# 2. 电池档位 (§1.6.2 / §1.6.3)
# ======================================================================
def tier_rows():
    rows = []
    for name, thk, blen, vol, doc_cav, doc_thk, doc_len_cb, doc_len_nocb in TIERS:
        stack_h = SHELL_WALL + TIM_PAD + PCB_T + thk + SHELL_WALL   # 前后厚
        cav_lo = (vol[0] + PCB_CC + CB_CC + TYPEC_CC + CONN_CC) * ASSY_FACTOR + WIRE_CHANNEL
        cav_hi = (vol[1] + PCB_CC + CB_CC + TYPEC_CC + CONN_CC) * ASSY_FACTOR + WIRE_CHANNEL
        area_hi = cav_hi / CAVITY_LEN * 1000.0                        # mm² @130mm
        len_cb = blen + PCB_L + CB_L + LEN_MARGIN
        len_nocb = blen + PCB_L + LEN_MARGIN
        rows.append(dict(name=name, thk=thk, blen=blen, stack_h=stack_h,
                          cav=(cav_lo, cav_hi), area_hi=area_hi,
                          len_cb=len_cb, len_nocb=len_nocb,
                          doc_cav=doc_cav, doc_thk=doc_thk,
                          doc_len_cb=doc_len_cb, doc_len_nocb=doc_len_nocb))
    return rows


# ======================================================================
# 3. 摄像头几何 (§1.5)
# ======================================================================
def tilt_deg(h, d=CAM_D):
    return math.degrees(math.atan(h / d))


def fov_split(diag):
    """对角 FOV → 水平/垂直 FOV (矩形成像: tan(θ半) = tan(θ对角半) × 边长/对角长)"""
    td = math.radians(diag / 2.0)
    w, h = ASPECT
    norm = math.hypot(w, h)
    th = math.degrees(math.atan(math.tan(td) * w / norm))
    tv = math.degrees(math.atan(math.tan(td) * h / norm))
    return 2 * th, 2 * tv


def occlusion_deg(recess, d=D_OCCLUDE):
    return math.degrees(math.atan(recess / d))


def tilt_delta_per_mm(h, d=CAM_D):
    """镜头每向前凸出 1mm (d 减小 1mm) 带来的俯角增量 (正数)"""
    return math.degrees(math.atan(h / (d - 1.0)) - math.atan(h / d))


# ======================================================================
# 4. 输出
# ======================================================================
def hr(t):
    print("\n" + "=" * 72)
    print(t)
    print("=" * 72)


# ---- 口径自检 (§8): 只读 MECH_BUDGET.md 正文, 盯着"口径 = buck 而不是线性" ----
LEGACY_LINEAR_MARKERS = (
    "线性充电 IC",          # 旧口径的拓扑说法
    "(5−4.2)V × 1A",        # 旧口径的公式
    "0.8 W @ 1A",           # 旧口径的发布值
    "MP26029",              # 旧口径引的 MPS 线性料
    "MP2710",
    "MP2721",
)

# ★旧标记允许出现的条件 (该行必须明确写了“旧口径已判死/作废”) —— 历史沿革要可追溯,
#   但**不许把旧口径当活口径用**。
LEGACY_DEAD_MARKERS = ("判死", "作废", "已死", "旧口径", "不再适用", "历史沿革")


def read_budget_md():
    if not os.path.exists(BUDGET_MD):
        return ""
    with open(BUDGET_MD, "r", encoding="utf-8") as f:
        return f.read()


def budget_charge_row(text):
    """抓 §2.1 峰值充电那一行 (含 '峰值' 与 '充电')。"""
    for line in text.splitlines():
        if "峰值" in line and "充电" in line and line.strip().startswith("|"):
            return line
    return ""


def caliber_checks(text):
    """★口径自检组 (C1~C9)。返回 [(编号, 名称, ok, 明细)]。"""
    out = []
    band = charge_band()
    p_lo = min(r["p"] for r in band)
    p_hi = max(r["p"] for r in band)
    row = budget_charge_row(text)

    out.append(("C1", "脚本口径标识 = buck + 器件 = BQ25896",
                CHG_TOPOLOGY == "buck" and CHG_IC == "BQ25896",
                f"CHG_TOPOLOGY={CHG_TOPOLOGY!r} · CHG_IC={CHG_IC!r}"))

    out.append(("C2", "P_CHARGE 落在已定 buck 区间 (0.45-0.57W)",
                P_CHARGE_LO <= P_CHARGE <= P_CHARGE_HI,
                f"P_CHARGE={P_CHARGE:.3f}W vs 区间 [{P_CHARGE_LO:.2f}, {P_CHARGE_HI:.2f}]W"))

    out.append(("C3", "P_CHARGE 不是线性稳压器公式值 (5−4.2)V×1A = 0.8W",
                abs(P_CHARGE - 0.8) > 1e-9,
                f"P_CHARGE={P_CHARGE:.3f}W (线性口径 = 0.800W ⇒ 已判死)"))

    out.append(("C4", "按公式复算的三档耗散落在已定区间内 (含电感铜损)",
                p_lo >= P_CHARGE_LO - 0.01 and p_hi <= P_CHARGE_HI + 0.01,
                f"复算 {p_lo:.4f}-{p_hi:.4f}W (IIN min/max 档) vs 区间 "
                f"[{P_CHARGE_LO:.2f}, {P_CHARGE_HI:.2f}]W"))

    out.append(("C5", "代表值 = ISS-213 机器门禁锚点 0.50W (端件温升口径一致)",
                abs(P_CHARGE - 0.50) < 1e-9,
                f"P_CHARGE={P_CHARGE:.3f}W vs 门禁 anchors.thermal.p_buck_w=0.50W"))

    out.append(("C6", "文档 §2.1 峰值充电行带 buck 口径标识 + 真器件 + 公式",
                ("BQ25896" in row) and ("buck" in row.lower())
                and ("Pin" in row and "Pout" in row),
                f"§2.1 行: {row[:110] if row else '(找不到该行)'}"))

    legacy = [m for m in LEGACY_LINEAR_MARKERS if m in text]
    # ★旧标记只允许出现在**已明确判死/作废**的行里 (历史沿革可追溯, 但不许当活口径)
    live = []
    for line in text.splitlines():
        hit = [m for m in LEGACY_LINEAR_MARKERS if m in line]
        if not hit:
            continue
        if not any(w in line for w in LEGACY_DEAD_MARKERS):
            live.append((hit, line.strip()[:110]))
    out.append(("C7", "文档里旧线性口径标记只存在于已判死/作废的行 (不许当活口径)",
                not live,
                f"未标注作废的残留: {live or '无'} (全文命中标记 {legacy or '无'})"))

    out.append(("C8", "文档 §2.1 行不再出现 0.8W 充电耗散",
                ("0.8 W" not in row) and ("0.8W" not in row),
                f"§2.1 行内 0.8W 残留: {'有' if ('0.8 W' in row or '0.8W' in row) else '无'}"))

    r37, r42 = charge_ratio(CHG_VBAT), charge_ratio(CHG_VBAT_CV)
    out.append(("C9", "功率守恒 ICHG/IIN = eta·Vbus/Vbat (规格书 0.822/0.933 是倒数)",
                abs(r37 - 1.216) < 5e-4 and abs(r42 - 1.071) < 5e-4,
                f"3.70V ⇒ {r37:.3f} · 4.20V ⇒ {r42:.3f}"))

    out.append(("C10", "已定区间边界不许被放松 (ISS-213 §5.3 / ISS-089 自-4: 0.45-0.57W)",
                abs(P_CHARGE_LO - 0.45) < 1e-9 and abs(P_CHARGE_HI - 0.57) < 1e-9,
                f"区间 = [{P_CHARGE_LO:.2f}, {P_CHARGE_HI:.2f}]W (已定 0.45-0.57W)"))
    # ★C11 (ISS-219): 金属热路的 k 口径 = 6063-T6 官方 201 W/m·K, 不许漂回旧乐观值 237
    live_237 = []
    for line in text.splitlines():
        if "237" not in line:
            continue
        if not any(w in line for w in LEGACY_DEAD_MARKERS):
            live_237.append(line.strip()[:110])
    out.append(("C11", "金属热路 k 口径 = 6063-T6 官方 201 W/m·K (不许漂回旧口径 237)",
                abs(K_AL_6063_T6 - 201.0) < 1e-9
                and "k=**201**" in text
                and not live_237,
                f"K_AL_6063_T6={K_AL_6063_T6:.1f} (201) · 旧口径 237 只许出现在已标注作废/订正的行里; "
                f"未标注的 237 残留: {live_237 or '无'}"))
    # ★C12 (ISS-222): C-6 落表 —— 分光件规格不许漂回旧口径 (14×10×6 / 0.79cc / 3-6g)
    c12_det = []
    m6 = [ln for ln in text.splitlines() if ln.strip().startswith("| M6 |")]
    w4 = [ln for ln in text.splitlines() if ln.strip().startswith("| W4 |")]
    if not m6:
        c12_det.append("结构真源找不到 §1.3 M6 行")
    else:
        for lit in ("11 × 11 × 1.5", "0.9697"):
            if lit not in m6[0]:
                c12_det.append(f"§1.3 M6 行缺新规格 '{lit}'")
    if not w4:
        c12_det.append("结构真源找不到 §3 W4 行")
    elif "3.68-7.36" not in w4[0].replace("**", ""):
        c12_det.append(f"§3 W4 行没有 3.68-7.36: {w4[0][:80]}")
    if "50.78 - 75.36" not in text.replace("−", "-").replace("—", "-"):
        c12_det.append("§3 合计没有 50.78 - 75.36")
    if abs(SPL_V_CC_V3 - 0.9697) > 1e-9:
        c12_det.append(f"脚本常量 SPL_V_CC_V3 = {SPL_V_CC_V3} (应 0.9697)")
    if abs(DOC_WEIGHT[0] - 50.78) > 1e-9 or abs(DOC_WEIGHT[1] - 75.36) > 1e-9:
        c12_det.append(f"DOC_WEIGHT = {DOC_WEIGHT} (应 50.78, 75.36)")
    out.append(("C12", "C-6 落表 (平板 11×11×1.5 + 棱镜 2×9×9×5 / 0.9697cc / W4 3.68-7.36g) 不许漂回旧口径",
                not c12_det,
                "M6 行 / §3 W4 行 / 合计 50.78-75.36 / 脚本常量 全部在位" if not c12_det
                else "; ".join(c12_det)))
    return out


def run(verbose=True):
    """跑全量复算 + 逐项对拍 + 口径自检。返回 dict(checks, caliber, bad)。"""
    checks = []   # (名称, 复算值, 文档值, 容差)
    band = charge_band()
    text = read_budget_md()

    hr("§1 稳态热模型 (MECH_BUDGET §2.3) — 贴皮肤镜腿")
    print(f"R_壳壁      = {R_WALL:.2f} K/W     (文档 12.5)")
    print(f"R_皮肤界面  = {R_SKIN_IF:.2f} K/W     (文档 41.7)")
    print(f"R_skin_path = {R_SKIN_PATH:.2f} K/W     (文档 54.2)")
    print(f"R_conv      = {R_CONV:.1f} K/W     (文档 667)")
    print(f"进入皮肤的热量比例 = {FRAC_SKIN * 100:.1f} %   (文档 92%)")
    print()
    print("  功耗      主模型温度   变体温度(壳壁剥离)   vs 红线 43°C")
    for p in (0.10, 0.15, 0.16, 0.20, P_AVG_ON_DEMAND, 0.30, 0.50, 0.80, P_FULL):
        t1 = skin_temp_main(p)
        t2 = skin_temp_var(p)
        flag = "❌" if t1 > T_LIMIT_RED else ("⚠️" if t1 > T_LIMIT_DESIGN else "✅")
        print(f"  {p:5.2f} W   {t1:6.1f} °C      {t2:6.1f} °C          {flag}")
    p_red = power_for_limit(skin_temp_main, T_LIMIT_RED)
    p_red_v = power_for_limit(skin_temp_var, T_LIMIT_RED)
    p_des = power_for_limit(skin_temp_main, T_LIMIT_DESIGN)
    print()
    print(f"  >>> 43°C 红线对应的持续功耗上限: 主模型 {p_red:.3f} W / 变体 {p_red_v:.3f} W"
          f"  → 区间 {min(p_red, p_red_v):.2f}-{max(p_red, p_red_v):.2f} W  (文档 0.15-0.2W)")
    print(f"  >>> 40°C 设计目标对应: {p_des:.3f} W")
    print(f"  >>> 1.22W 持续满载: 主模型 {skin_temp_main(P_FULL):.1f} °C / 变体 {skin_temp_var(P_FULL):.1f} °C"
          f"  → 超红线 {skin_temp_main(P_FULL) - T_LIMIT_RED:.1f} / {skin_temp_var(P_FULL) - T_LIMIT_RED:.1f} °C")
    print(f"  >>> ⚠️ 方案 C (按需触发 {P_AVG_ON_DEMAND}W): 主模型 {skin_temp_main(P_AVG_ON_DEMAND):.1f} °C"
          f" / 变体 {skin_temp_var(P_AVG_ON_DEMAND):.1f} °C  → 两种算法都 > 43°C")
    checks += [
        ("热 0.15W", skin_temp_main(0.15), 42.5, 0.15),
        ("热 0.30W", skin_temp_main(0.30), 50.0, 0.15),
        ("热 0.50W", skin_temp_main(0.50), 60.0, 0.15),
        ("热 0.80W", skin_temp_main(0.80), 75.1, 0.15),
        ("热 1.22W", skin_temp_main(P_FULL), 96.1, 0.15),
        ("热 0.23W (方案C)", skin_temp_main(P_AVG_ON_DEMAND), 46.5, 0.15),
        ("红线功耗上限", p_red, 0.16, 0.01),
    ]

    # ---------------- §2 充电峰值场景 (MECH_BUDGET §2.3.1) ----------------
    hr("§2 充电峰值场景 (MECH_BUDGET §2.3.1) — ★buck 口径 (ISS-216)")
    print(f"  器件 = {CHG_IC} [实测 网表 P10: SW/L_CHG/C_BST/PMID] · 拓扑 = {CHG_TOPOLOGY} "
          f"(5V→{CHG_VBAT}-{CHG_VBAT_CV}V, D<1 ⇒ 降压档)")
    print(f"  公式: P = Pin − Pout + P_DCR   (eta={CHG_ETA:.2f} · R_DCR={CHG_R_DCR*1000:.0f}mΩ · "
          f"R_ILIM={CHG_R_ILIM:.0f}Ω)")
    print()
    print("  档位   IIN      ICHG     Pin      Pout     P_DCR    P=Pin−Pout+DCR")
    for r in band:
        print(f"  {r['tag']:<5} {r['i_in']:.3f} A  {r['i_chg']:.3f} A  {r['p_in']:.3f} W  "
              f"{r['p_out']:.3f} W  {r['p_dcr']:.4f} W  {r['p']:.4f} W")
    p_lo = min(r["p"] for r in band)
    p_hi = max(r["p"] for r in band)
    print(f"  ⇒ buck 耗散区间 {p_lo:.2f}-{p_hi:.2f} W (已定 {P_CHARGE_LO:.2f}-{P_CHARGE_HI:.2f} W) · "
          f"代表值 P_CHARGE = {P_CHARGE:.2f} W")
    print(f"  ⇒ 功率守恒 ICHG/IIN: {charge_ratio(CHG_VBAT):.3f} ({CHG_VBAT}V) / "
          f"{charge_ratio(CHG_VBAT_CV):.3f} ({CHG_VBAT_CV}V)  (规格书 0.822/0.933 是倒数)")
    print()
    print("  场景                              功率      皮肤侧温升    皮肤侧温度 (基准 35°C)")
    for p, label in ((P_CHARGE, "充电 (系统关机)"),
                     (P_CHARGE + P_FULL, "充电 + 满载 (中位)"),
                     (P_CHARGE + P_FULL_HI, "充电 + 满载 (上界)")):
        print(f"  {label:<30} {p:4.2f} W   +{p * R_SKIN_PATH * FRAC_SKIN:6.1f} °C   "
              f"{skin_temp_main(p):6.1f} °C   "
              f"{'❌ 不可接受' if skin_temp_main(p) > T_LIMIT_RED else 'OK'}")
    print(f"  区间档 ({P_CHARGE_LO:.2f}W / {P_CHARGE_HI:.2f}W) 皮肤侧 "
          f"{skin_temp_main(P_CHARGE_LO):.1f} °C / {skin_temp_main(P_CHARGE_HI):.1f} °C")
    print()
    print(f"  → 结构硬结论: 充电板 (buck, {P_CHARGE_LO:.2f}-{P_CHARGE_HI:.2f}W) 的耗散"
          f"**必须落在不接触皮肤的位置** + 充电时禁 OD + 摘下充电")
    print(f"  → 端件外表面 (ISS-213 §5.3): R_conv {ENDPIECE_R_CONV:.2f} K/W ⇒ "
          f"ΔT {P_CHARGE * ENDPIECE_R_CONV:.1f}K ⇒ 表面 "
          f"{ENDPIECE_T_AMBIENT + P_CHARGE * ENDPIECE_R_CONV:.1f}°C; "
          f"60°C 判据 ⇒ P_max {ENDPIECE_P_MAX:.2f}W ⇒ 超 {P_CHARGE / ENDPIECE_P_MAX:.2f}× ⇒ 必须金属热路")
    checks += [
        ("充电耗散 IINmin档", band[0]["p"], 0.46, 0.005),
        ("充电耗散 IINtyp档", band[1]["p"], 0.52, 0.005),
        ("充电耗散 IINmax档", band[2]["p"], 0.57, 0.005),
        ("充电耗散代表值", P_CHARGE, 0.50, 0.001),
        ("充电皮肤温度(关机)", skin_temp_main(P_CHARGE), 60.0, 0.15),
        ("充电皮肤温度(区间下限)", skin_temp_main(P_CHARGE_LO), 57.5, 0.15),
        ("充电皮肤温度(区间上限)", skin_temp_main(P_CHARGE_HI), 63.6, 0.15),
        ("充电+满载皮肤温度", skin_temp_main(P_CHARGE + P_FULL), 121.2, 0.15),
        ("充电+满载上界皮肤温度", skin_temp_main(P_CHARGE + P_FULL_HI), 136.2, 0.15),
        ("ICHG/IIN @3.70V", charge_ratio(CHG_VBAT), 1.216, 0.001),
        ("ICHG/IIN @4.20V", charge_ratio(CHG_VBAT_CV), 1.071, 0.001),
        ("端件 ΔT @0.50W", P_CHARGE * ENDPIECE_R_CONV, 83.33, 0.05),
        ("端件表面温度 @0.50W", ENDPIECE_T_AMBIENT + P_CHARGE * ENDPIECE_R_CONV, 108.33, 0.05),
        ("端件 P_max @60°C", (ENDPIECE_T_LIMIT - ENDPIECE_T_AMBIENT) / ENDPIECE_R_CONV, 0.21, 0.005),
    ]

    hr("§3 电池三档位 (MECH_BUDGET §1.6.2 / §1.6.3)")
    print("  档位      前后厚    内腔需求(cc)   截面@130mm   长度(含CB)   长度(挪CB后)   判定")
    for r in tier_rows():
        verdict = "❌ 形态否决" if r["stack_h"] > 9.0 else ("⚠️ 紧 (超华为1.4倍)" if r["stack_h"] > 8.0 else "✅")
        print(f"  {r['name']:<9} {r['stack_h']:5.1f}mm   "
              f"{r['cav'][0]:5.2f}-{r['cav'][1]:5.2f}      {r['area_hi']:5.1f}mm²   "
              f"{r['len_cb']:6.1f}mm      {r['len_nocb']:6.1f}mm        {verdict}")
        checks += [
            (f"电池{r['name']} 厚", r["stack_h"], r["doc_thk"], 0.05),
            (f"电池{r['name']} 长度(挪CB后)", r["len_nocb"], r["doc_len_nocb"], 0.6),
            (f"电池{r['name']} 长度(含CB)", r["len_cb"], r["doc_len_cb"], 1.1),
            (f"电池{r['name']} 内腔需求(上界)", r["cav"][1], r["doc_cav"][1], 1.1),
        ]
    print(f"  走线槽 {WIRE_CHANNEL:.2f} cc (6×2mm×130mm) + 净物料×{ASSY_FACTOR}")
    print("  基准: 华为 AI 眼镜镜腿厚 6.25mm [媒体] → 675mAh 档 11.2mm = 1.79 倍")

    hr("§4 重量表求和 (MECH_BUDGET §3)")
    tot_min = sum(a for _, a, _, _ in WEIGHT_ITEMS)
    tot_max = sum(b for _, _, b, _ in WEIGHT_ITEMS)
    for nm, a, b, ev in WEIGHT_ITEMS:
        print(f"  {nm:<26} {a:5.2f} - {b:5.2f} g   {ev}")
    print(f"  {'合计':<26} {tot_min:5.2f} - {tot_max:5.2f} g   (文档 {DOC_WEIGHT[0]}-{DOC_WEIGHT[1]})")
    print(f"  >>> 超 30-40g 目标: {(tot_min / 40 - 1) * 100:.0f}% ~ {(tot_max / 30 - 1) * 100:.0f}%")
    checks.append(("重量下限", tot_min, DOC_WEIGHT[0], 0.05))
    checks.append(("重量上限", tot_max, DOC_WEIGHT[1], 0.05))

    hr("§5 摄像头几何 (MECH_BUDGET §1.5)")
    for h in CAM_H:
        t = tilt_deg(h)
        print(f"  镜头中心高于视线 {h:4.1f}mm, d={CAM_D:.0f}mm → 俯角 {t:.1f}°   (文档 {DOC_TILT[h]}°)")
        checks.append((f"俯角 h={h}", t, DOC_TILT[h], 0.06))
    print()
    for dg in DIAG_FOV:
        hf, vf = fov_split(dg)
        print(f"  对角 FOV {dg:.0f}° (16:9) → 水平 {hf:.1f}° / 垂直 {vf:.1f}°   "
              f"(文档 {DOC_FOV_SPLIT[dg][0]}/{DOC_FOV_SPLIT[dg][1]})")
        checks.append((f"FOV{dg:.0f} 水平", hf, DOC_FOV_SPLIT[dg][0], 0.15))
        checks.append((f"FOV{dg:.0f} 垂直", vf, DOC_FOV_SPLIT[dg][1], 0.15))
    print()
    for r in RECESS_MM:
        o = occlusion_deg(r)
        d = f"   (文档 {DOC_OCCLUDE[r]}°)" if r in DOC_OCCLUDE else ""
        print(f"  凹进 {r:3.1f}mm (d={D_OCCLUDE:.0f}mm) → 遮挡 {o:4.1f}°{d}")
        if r in DOC_OCCLUDE:
            checks.append((f"遮挡 {r}mm", o, DOC_OCCLUDE[r], 0.1))
    print()
    for h in (15.0, 20.0):
        print(f"  凸出 1mm 引起的俯角增量 (h={h:.0f}, d={CAM_D:.0f}): {tilt_delta_per_mm(h):.2f}°/mm "
              f"→ 凸出 3mm: {tilt_deg(h, CAM_D - 3):.1f}° (原 25.1° → 27.3°, 不是 30°)")
    print("  ⚠️ 更正: 文档写的 '1.8°/mm' 用的是 Δθ≈Δh/d (把凸出量当成高度增量), 实际偏大 ~2 倍")

    hr("§6 截面 / 长度叠层 (MECH_BUDGET §1.4.2)")
    stack = SHELL_WALL + TIM_PAD + PCB_T + BAT_T420 + SHELL_WALL
    stack_v = 22.0 + 12.0 + 3.0
    len_stack = 43.5 + PCB_L + CB_L + LEN_MARGIN
    print(f"  前后方向: {SHELL_WALL} (皮肤侧壁) + {TIM_PAD} (导热垫) + {PCB_T} (PCB) + "
          f"{BAT_T420} (电池) + {SHELL_WALL} (外侧壁) = {stack:.1f} mm   (文档 {DOC_STACK_H})")
    print(f"  垂直方向: 22 (电池) + 12 (PCB) + 3 (走线) = {stack_v:.0f} mm   (文档 {DOC_STACK_V})")
    print(f"  长度方向: 43.5 + {PCB_L:.0f} + {CB_L:.0f} + {LEN_MARGIN:.0f} = {len_stack:.1f} mm   "
          f"(文档 {DOC_LEN_STACK})")
    checks += [("截面叠层", stack, DOC_STACK_H, 0.05),
               ("垂直叠层", stack_v, DOC_STACK_V, 0.05),
               ("长度叠层", len_stack, DOC_LEN_STACK, 0.05)]

    hr("§7 分光件角度公差 (§1.2)")
    for d in TOL_DEG:
        mm = ARM_L * math.tan(math.radians(d))
        print(f"  Δθ {d:.2f}° @臂长 {ARM_L:.0f}mm → 位置误差 {mm:.3f} mm   (文档 {DOC_TOL_MM[d]})")
        checks.append((f"公差 {d}°", mm, DOC_TOL_MM[d], 0.002))

    # ---------------- §8 口径自检 (ISS-216) ----------------
    hr("§8 ★充电耗散口径自检 (ISS-216) — 口径 = buck, 不是线性 0.8W")
    caliber = caliber_checks(text)
    for code, name, ok, detail in caliber:
        print(f"  {'✅' if ok else '❌'} {code:<3} {name}")
        print(f"        {detail}")

    # ---------------- §2b 金属热路 k 口径 (ISS-219) ----------------
    hr("§2b 金属热路 k 口径 (ISS-219) — 6063-T6 官方 201 W/m·K (旧口径 237 已订正)")
    print(f"  k = {K_AL_6063_T6:.0f} W/m·K  [官网] Hydro EN AW-6063 'Hydro 6063_Rev.4 – 03/2023'")
    print(f"      (T6 Thermal Conductivity 201 W/m·K · Density 2.70 g/cm³) + Aalco + Kaiser 三家互证")
    print(f"  旧口径 {K_AL_6063_T6_LEGACY:.0f} W/m·K (项目内乐观值) ⇒ ★已订正, 只留追溯, 不许当活口径")
    print()
    print(f"  同几何 (L={ENDPOINT_GEOM_L_MM:.0f}mm, A={ENDPOINT_GEOM_A_MM2:.0f}mm²):")
    print(f"    铝 6063-T6 @ k=201 ⇒ R = {R_AL_201:.3f} K/W ⇒ 0.50 W 下 ΔT = {0.5 * R_AL_201:.2f} K  ✅")
    print(f"    (旧口径 k=237 ⇒ R = {R_AL_237:.3f} K/W ⇒ ΔT = {0.5 * R_AL_237:.2f} K) —— 只留追溯")
    print(f"    打印件 PA6-CF @ k=0.2 ⇒ R = {R_PRINT_6063:.1f} K/W ⇒ 0.50 W 下 ΔT = {0.5 * R_PRINT_6063:.0f} K  ❌")
    print()
    print(f"  R_热路 ≤ {R_PATH_MAX_KW:.0f} K/W ⇒ 截面积 A ≥ {A_MIN_R70_201:.4f} mm² (k=201 侧; 旧 237 侧 "
          f"{A_MIN_R70_237:.4f})")
    print(f"  ⇒ 2.0×2.0 = 4.0 mm² 铝条 R = {ENDPOINT_GEOM_L_MM * 1000.0 / (K_AL_6063_T6 * 4.0):.2f} K/W "
          f"❌ 不合格 ⇒ **热路必须是铝/铜件, 不能是打印件** (结论方向未变)")
    print()

    hr("自检: 复算值 vs MECH_BUDGET.md 发布值")
    bad = 0
    for nm, got, doc, tol in checks:
        ok = abs(got - doc) <= tol
        if not ok:
            bad += 1
        print(f"  {'✅' if ok else '⚠️ '} {nm:<24} 复算 {got:10.3f}  文档 {doc:10.3f}  Δ {got - doc:+.3f}")
    print(f"\n  → {len(checks) - bad}/{len(checks)} 项与文档一致" +
          ("" if bad == 0 else f"; {bad} 项 ⚠️ 不一致 (以本文为准, 需回写 MECH_BUDGET.md)"))
    bad_cal = [c for c in caliber if not c[2]]
    print(f"  → 口径自检 {len(caliber) - len(bad_cal)}/{len(caliber)} 项通过" +
          ("" if not bad_cal else f"; 红组 {[c[0] for c in bad_cal]}"))
    print("\n  说明: 本脚本只做算术复算, 不代表结论已实测。")
    print("  皮肤温度 / 重量 / 电池档位 全部是 [推算], 实测口径见 MECH_BUDGET §6 u9/u10。")
    print("  ★充电耗散 0.45-0.57W 是 buck 口径 [推算] (器件与拓扑 [实测] 网表 / KILIM 与效率 [官网] TI)。")

    all_bad = [("数值", nm) for nm, got, doc, tol in checks if abs(got - doc) > tol]
    all_bad += [("口径", c[0]) for c in bad_cal]
    return {"checks": checks, "caliber": caliber, "bad": all_bad}


# ====================================================================== selftest
def _quiet_run():
    """跑一遍全量对拍 (吞掉 stdout), 返回 res dict。"""
    import contextlib
    import io
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        res = run()
    return res


def _quiet_caliber(text):
    """只跑口径自检 (给'文档没改'类反向用例用), 返回红组名单。"""
    return [c[0] for c in caliber_checks(text) if not c[2]]


def selftest() -> int:
    """反向用例: 改坏任一口径锚点 ⇒ 必须变红。写法照 MECH/check_demo_struct_truth.py --selftest。"""
    global P_CHARGE, CHG_TOPOLOGY, CHG_K_ILIM, CHG_R_DCR, CHG_ETA, P_CHARGE_LO, P_CHARGE_HI
    saved = (P_CHARGE, CHG_TOPOLOGY, CHG_K_ILIM, CHG_R_DCR, CHG_ETA, P_CHARGE_LO, P_CHARGE_HI)

    def restore():
        global P_CHARGE, CHG_TOPOLOGY, CHG_K_ILIM, CHG_R_DCR, CHG_ETA, P_CHARGE_LO, P_CHARGE_HI
        (P_CHARGE, CHG_TOPOLOGY, CHG_K_ILIM, CHG_R_DCR, CHG_ETA, P_CHARGE_LO, P_CHARGE_HI) = saved

    def set_pcharge(v):
        global P_CHARGE
        P_CHARGE = v

    def set_topology(v):
        global CHG_TOPOLOGY
        CHG_TOPOLOGY = v

    def set_kilim(v):
        global CHG_K_ILIM
        CHG_K_ILIM = v

    def set_dcr(v):
        global CHG_R_DCR
        CHG_R_DCR = v

    def set_eta(v):
        global CHG_ETA
        CHG_ETA = v

    def set_lo(v):
        global P_CHARGE_LO
        P_CHARGE_LO = v

    # (名称, 施加的改动, 期望红组)
    cases = [
        ("反向1: P_CHARGE 0.50 → 0.80 (退回线性充电 IC 口径)",
         lambda: set_pcharge(0.80), "C2"),
        ("反向2: P_CHARGE 0.50 → 0.40 (跌出 buck 区间)",
         lambda: set_pcharge(0.40), "C2"),
        ("反向3: 口径标识 buck → linear (拓扑写反)",
         lambda: set_topology("linear"), "C1"),
        ("反向4: P_CHARGE 0.50 → 0.55 (改代表值, 与门禁 0.50W 不一致)",
         lambda: set_pcharge(0.55), "C5"),
        ("反向5: 电感铜损 R_DCR 0.050 → 0.000 (漏掉 DCR 项)",
         lambda: set_dcr(0.000), "C4"),
        ("反向6: 区间下限 0.45 → 0.30 (放松区间, 让 0.8W 蒙混过关)",
         lambda: set_lo(0.30), "C10"),
        ("反向7: K_ILIM 全取 320 (把输入电流上限压到 0.82A)",
         lambda: set_kilim((320.0, 320.0, 320.0)), "充电耗散 IINmax档"),
        ("反向8: 效率 eta 0.90 → 1.00 (理想电源, 转换耗散算成 0)",
         lambda: set_eta(1.00), "C4"),
    ]

    # 文档类反向用例 (不改真文件, 只喂一份被改坏的文本)
    doc_cases = [
        ("反向9: 文档 §2.1 行仍是旧口径 (线性充电 IC / 0.8 W @ 1A / MP26029)",
         "| **B. 峰值: 充电** | Type-C 输入 (5V) + 线性充电 IC | **0.8 W @ 1A** (IC 自身耗散 = "
         "(5−4.2)V × 1A) | `[推算]`; 充电 IC 拓扑参考 MPS MP26029/MP2710/MP2721 资料 `[官网]` |",
         "C6"),
        ("反向10: 文档里残留旧的线性口径标记 (整行没删干净, 没标作废)",
         "| **B. 峰值: 充电** | Type-C 输入 (5V) + 开关型 buck 充电 IC (**BQ25896**) | "
         "**0.45-0.57 W** (代表值 **0.50 W**) — 耗散 = **Pin − Pout + P_DCR** | `[推算]`; "
         "旧公式 (5−4.2)V × 1A = 0.8 W @ 1A 留档 |",
         "C7"),
        ("反向11: 文档里的 C-6 规格漂回旧口径 (M6 回到 10×10×1.5 / 0.79cc · W4 回到 3-6 g)",
         "| M6 | **一拖二分光件** (平板 + 2 转向棱镜) | [框] | 10 × 10 × 1.5 | 0.79 | 旧口径 | 0.02 | 旧 | `[推算]` |\n"
         "| W4 | 一拖二分光件 (平板+2棱镜) | 1 | 3-6 | **3-6** | 旧口径 | `[推算]` |",
         "C12"),
    ]

    print("=" * 100)
    print("ISS-216 机器门禁 —— 反向用例 (改坏任一充电耗散口径锚点必须变红)")
    print("=" * 100)
    restore()
    base_res = _quiet_run()
    base_red = [b[1] for b in base_res["bad"]]
    if base_red:
        print(f"❌ 基线就不绿: {base_red} ⇒ 门禁本身有问题, 自测不成立")
        return 2
    print(f"  ✅ 基线全绿 (数值对拍 {len(base_res['checks'])}/{len(base_res['checks'])} + "
          f"口径自检 {len(base_res['caliber'])}/{len(base_res['caliber'])})")
    ok = 0
    for name, fn, expect in cases:
        restore()
        fn()
        red = [b[1] for b in _quiet_run()["bad"]]
        hit = expect in red
        flag = "✅" if hit else "❌"
        if hit:
            ok += 1
        print(f"  {flag} {name:<52} 期望红组 {expect:<8} 实际红组 {red or '无'}")
    for name, bad_row, expect in doc_cases:
        restore()
        red = _quiet_caliber(bad_row)
        hit = expect in red
        flag = "✅" if hit else "❌"
        if hit:
            ok += 1
        print(f"  {flag} {name:<52} 期望红组 {expect:<8} 实际红组 {red or '无'}")
    restore()
    n = len(cases) + len(doc_cases)
    print("-" * 100)
    print(f"反向用例: {ok}/{n} 抓到了")
    return 0 if ok == n else 2


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true",
                    help="反向用例: 改坏任一充电耗散口径锚点必须变红")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    res = run()
    bad = res["bad"]
    if bad:
        print(f"\n  ❌ 门禁红: {len(bad)} 项不过 (数值 {[b[1] for b in bad if b[0]=='数值']} / "
              f"口径 {[b[1] for b in bad if b[0]=='口径']})")
        return 2
    print("\n  ✅ 门禁绿: 全部数值对拍一致 + 充电耗散口径 = buck (非线性 0.8W)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
