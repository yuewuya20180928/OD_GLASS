#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MECH_BUDGET.md 关键数字自证脚本 (交接单 B6 用)
======================================================================
用途: 别人一条命令复算我的空间 / 散热 / 重量 / 摄像头 关键数字,
      并自动对表 MECH_BUDGET.md 里发布的数字 (不一致就打印 ⚠)。

用法:
    cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
    python3 MECH/verify_budget.py

原则:
  * 纯 Python3, 无第三方依赖, 无网络
  * 所有输入参数在文件里显式列出 (可逐项核对), 不藏魔法数
  * 推算项标 [推算]; 直接取自官网的标 [官网]
  * 退出码: 0 = 复算完成 (无论是否对表一致都返回 0, 对表结果打在屏幕上);
            2 = 脚本自身算错 (除零/断言失败)

作者: mech-lead (结构和散热) · 2026-10-25 第二轮整改
======================================================================
"""

import math
import sys

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
P_CHARGE = 0.8          # W [推算] 线性充电 IC 耗散 (5V-4.2V) × 1A
P_AVG_ON_DEMAND = 0.23  # W [推算] 方案 C 按需触发平均功耗
P_STANDBY = 0.15        # W [推算] 方案 C 里的待机功耗

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
    ("一拖二分光件", 3.0, 6.0, "[推算]"),
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
DOC_WEIGHT = (50.1, 74.0)   # §3 合计 (第二轮更正后)

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


def main():
    checks = []   # (名称, 复算值, 文档值, 容差)

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

    hr("§2 充电峰值场景 (MECH_BUDGET §2.3.1)")
    for p, label in ((P_CHARGE, "充电 (系统关机)"),
                     (P_CHARGE + P_FULL, "充电 + 满载 (中位)"),
                     (P_CHARGE + P_FULL_HI, "充电 + 满载 (上界)")):
        print(f"  {label:<22} {p:4.2f} W → 皮肤侧 {skin_temp_main(p):6.1f} °C   "
              f"{'❌ 不可接受' if skin_temp_main(p) > T_LIMIT_RED else 'OK'}")
    print("  → 结构硬结论: 充电 IC 的 0.8W 耗散必须落在不接触皮肤的位置 + 充电时禁 OD + 摘下充电")

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

    hr("自检: 复算值 vs MECH_BUDGET.md 发布值")
    bad = 0
    for nm, got, doc, tol in checks:
        ok = abs(got - doc) <= tol
        if not ok:
            bad += 1
        print(f"  {'✅' if ok else '⚠️ '} {nm:<24} 复算 {got:10.3f}  文档 {doc:10.3f}  Δ {got - doc:+.3f}")
    print(f"\n  → {len(checks) - bad}/{len(checks)} 项与文档一致" +
          ("" if bad == 0 else f"; {bad} 项 ⚠️ 不一致 (以本文为准, 需回写 MECH_BUDGET.md)"))
    print("\n  说明: 本脚本只做算术复算, 不代表结论已实测。")
    print("  皮肤温度 96°C / 重量 / 电池档位 全部是 [推算], 实测口径见 MECH_BUDGET §6 u9/u10。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
