#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SW/tools/demo_e2e_budget.py —— demo 屏 (2 通道 @ 480×640) 端到端预算【真源脚本】
================================================================================
★为什么要有这个脚本 (★ISS-221, 2026-11-16★):
  ISS-215 (2026-11-16 01:5x 交卷) 查清了一件事 ——
  ★**demo 屏的账是从整机账减出来的**: 整机那本 `HW/e2e_budget_rk3572.py` 的 DSI 带宽常量是
  **整机 4 通道 @2.0Gbps × 80%**, 对 **2 通道** 的 demo 屏不适用;
  而 ISS-215 交卷时用「整机的 TX 物理下限」去扣 demo 的预算 ⇒
  ★**判据被算严 3.36×** ⇒ ★**换屏 / 改分辨率 / 改通道数时, 没有人拦得住「又拿整机常量扣 demo 预算」**。
  ⇒ ⇒ 本脚本给 demo 屏建**它自己的预算真源**:
  ★**demo 判据链里的每一个预算数, 都从这里算出来** ★

★本脚本的边界 (★硬纪律, 自检里有反向用例盯着★):
  1. ★**不许把整机的 4 通道 DSI 带宽常量写进来冒充 demo 真源**
     ⇒ 本文件里**没有任何整机 DSI 常量** (自检 §F7「源码泄漏扫描」反向用例盯着这件事)。
  2. ★**整机同源常量只引用、不重算**: T_FIXED_OTHER / POST_MS / FRAME_MS / 显示输出侧占位 S9
     ⇒ 出处写在括号里 (整机脚本 §ISS-137 拆分 + RKNN_BENCH §4.1) —— ★**只读引用, 那个文件本单一个字没改**。
  3. ★**本脚本不编板端时延数字**: 板与屏都不在本机 ⇒ 屏侧一切标 **[推算]**;
     板端实测值只能用 `--t-compose-ms` / `--t-display-ms` **代入** ⇒ 代进去的标 **[实测·板端]**。
  4. ★**本脚本只管 demo 屏这一侧**; 整机路线 (整机屏) 的账仍在 `HW/e2e_budget_rk3572.py` 里, 两本互不代算。

用法:
    python3 SW/tools/demo_e2e_budget.py                       # 主表 (口径声明 + demo 预算表)
    python3 SW/tools/demo_e2e_budget.py --json                # 机读输出 (机器门禁用)
    python3 SW/tools/demo_e2e_budget.py --selftest            # 自检 (反向用例: 改坏必红)
    python3 SW/tools/demo_e2e_budget.py --t-compose-ms 0.44 --t-display-ms 2.30   # 代入板端实测
    python3 SW/tools/demo_e2e_budget.py --lanes 4 --lane-rate-gbps 2.0           # 换屏试算
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys

# =============================================================================
# §1 口径声明 —— ★整机同源常量 vs demo 专属常量★ (两类都不许混, 混了自检会红)
# =============================================================================
# ── (A) 整机同源常量 (★只引用: 出处见行尾, 本脚本不重算整机的账★) ─────────────
T_PRE_EXPOSURE = 24.67   # 曝光→OD 输入就绪 (E 8.3 + R 8.3 + S3 ISP 8.0) —— 不随显示分辨率变
                          #   (出处: HW/e2e_budget_rk3572.py §ISS-137 拆分 / RKNN_BENCH §4.1)
T_DRAW = 1.00            # 画框 S8 —— 画的是采集帧, 不随显示分辨率变
T_PANEL = 5.00           # 光机逐帧延迟 S10 —— 面板自身时序, 不随像素数变 (★板端值仍 [0数据]★)
T_RESIDUAL = 0.33        # 反解余量 (整机 T_FIXED 34.00 − 明细 33.67)
T_FIXED_OTHER = 31.00    # ★= 24.67 + 1.00 + 5.00 + 0.33 —— 与整机脚本同名同值 (只引用)
POST_MS = 5.60           # 后处理 (从 T_od=21~23 与 S5=15.38~17.39 反解) —— 与整机脚本同值
FRAME_MS = 16.67         # 60fps 帧周期 —— 与整机脚本同值
T_DISPLAY_OUT_BASE = 3.00  # ★ISS-137 拆分的显示输出侧整段占位 (S9) —— ★**本脚本只拿它做缩放基准,
                           #   不当 demo 屏的实测值**★ (★口径沿用说明见 §1.1★)

# ── (B) demo 专属常量 (★本脚本的真源: 换屏只改这里或用命令行改★) ─────────────
DEMO_W = 480             # demo 屏宽 (Waveshare 2.8" SKU 22028, ISS-212 定版)
DEMO_H = 640             # demo 屏高
DEMO_LANES = 2           # ★DSI 通道数 = 2★ (ISS-212 定版) —— ★**不是整机的 4 通道**★
BITS_PER_PIXEL = 24      # RGB888 8bpc
LANE_RATE_A_GBPS = 2.0   # 口径 A: 每通道 2.0 Gbps
LANE_EFF_A = 0.80        # 口径 A: 链路效率 80%
LANE_RATE_B_GBPS = 1.8   # 口径 B: 驱动上限 1.8 Gbps/通道
LANE_EFF_B = 1.00        # 口径 B: 100% 效率 (理想上界)
PAYLOAD_OVERHEAD_BITS = 0  # 每帧 payload 固定开销 (bit) —— 默认 0 (★[0数据]: 板端未测, 用命令行代入★)
SCALE_REF_PX = 2_073_600  # 缩放基准画布像素数 (2.0736 Mpx, ISS-212 口径基准) ⇒ demo 侧除数 = 6.75
BUDGET_MS = 60.0         # ★60 ms 硬指标 —— 不许调松★

# ── (C) 模型方案 (★S5 是已发布表内的值, 出处写在 note 里★) ───────────────────
MODEL_PLANS = [
    {"name": "RK3572 + yolov5s@640", "s5_ms": 26.09,
     "note": "RK3576 17.39×6/4 = 26.085 ⇒ 表内按 26.09 记账 (差 0.005ms, 远小于板端 0.01ms 分辨率)"},
    {"name": "RK3572 + yolov5n@640", "s5_ms": 13.31,
     "note": "RK3576 8.87×6/4 = 13.305 ⇒ 表内按 13.31 记账 (差 0.005ms, 同上)"},
    {"name": "RK3572 + yolov5s@320", "s5_ms": 6.75,
     "note": "RK3576 (5.00+4.00)/2×6/4 = 6.75"},
]

# ── (D) 已发布值锚点 (★值型护栏: 期望值写死, 不许用被检查的常量重算 ⇒ 否则同义反复★) ──
ANCHOR = {
    "tx_floor_a_ms": 2.304,      # ISS-212 已发布 (口径 A)
    "tx_floor_b_ms": 2.048,      # ISS-212 已发布 (口径 B)
    "scale_divisor": 6.75,       # ISS-212 已发布 (÷6.75)
    "t_compose_est_ms": 0.44,    # ISS-212 已发布 (~0.44 ms, 2 位小数)
    "display_out_est_ms": 2.75,  # ISS-212 已发布 (~2.75 ms, 2 位小数)
    "cap_yolov5s_ms": -2.69,     # ISS-215 已发布 (输出侧总额上限, yolov5s@640)
    "compose_yolov5s_ms": -4.99, # ★ISS-215 表 A 写的是 −5.00; 本脚本按算术口径给 −4.99 (差 0.01ms,
                                  #   两者都 <0 ⇒ 判定「必不过」不变) ⇒ 文档已按脚本口径统一★
    "cap_yolov5n_ms": 10.09,     # ISS-215 已发布 (输出侧总额上限, yolov5n@640)
    "compose_yolov5n_ms": 7.79,  # ISS-215 已发布 (合成段上限, yolov5n@640)
    "cap_yolov5s320_ms": 16.65,  # ISS-215 已发布
    "compose_yolov5s320_ms": 14.35,  # ISS-215 已发布
    "margin_yolov5n_ms": 7.34,   # ★ISS-221 新增: 全链路 60ms 预算余量 (yolov5n@640)★
}

# =============================================================================
# §1.1 【口径沿用声明】—— ★诚实记录, 不在本单偷改已发布判据★
# =============================================================================
# ISS-212 把 ISS-137 的 S9 占位 T_DISPLAY_OUT = 3.00 ms 当作【缩放基准画布侧】的 t_compose 占位,
# 按像素数线性缩放到 demo 画布 ⇒ 3.00 ÷ 6.75 = 0.444 ms; 显示输出侧合计 = 0.444 + 2.304 = 2.748 ms。
# ★**已知口径瑕疵 (记录在案, 不擅改)**: 整机账本里 T_DISPLAY_OUT = 3.00 是【整机 800×600 基线】的值
#   (整机大屏侧是 3.00 乘像素比), 且它在整机账本里 = 合成+桥接余量 + TX 下限。
#   ⇒ 若按整机账本严格拆, demo 侧合成会算成别的数 —— ★**但那个拆法要用到整机 4 通道 DSI 常量,
#   而本脚本按纪律【不许引入整机 DSI 常量】⇒ 所以本脚本只能沿用 ISS-212 已发布口径**★。
# ★**结论不受影响的证明 (自检 G7 守着)**: t_compose 估算 ×0.5 / ×1 / ×2 三档, 全链路余量都 > 0
#   ⇒ ★**判据对 t_compose 估算误差不敏感 ⇒ 口径瑕疵不改变 60ms 生死判定** ★

# =============================================================================
# §2 计算核心 (★纯函数: 便于自检做故障注入★)
# =============================================================================
def payload_bits(w: int, h: int, bpp: int, overhead_bits: int = 0) -> int:
    """一帧 payload 比特数 = 像素数 × 每像素比特 + 每帧固定开销。"""
    return w * h * bpp + overhead_bits


def tx_floor_ms(w: int, h: int, bpp: int, lanes: int,
                lane_rate_gbps: float, eff: float, overhead_bits: int = 0) -> float:
    """★一帧 DSI 移出的物理下限 (ms) = 一帧比特数 / 链路有效带宽。
    ★与帧率无关 (每帧比特数才是量) —— 与整机脚本 tx_min_ms 同一口径。"""
    bits = payload_bits(w, h, bpp, overhead_bits)
    bandwidth = lanes * lane_rate_gbps * 1e9 * eff
    if bandwidth <= 0:
        raise ValueError("链路有效带宽必须 > 0")
    return bits / bandwidth * 1000.0


def scale_divisor(w: int, h: int, ref_px: int = SCALE_REF_PX) -> float:
    """画布像素比 = 缩放基准画布像素数 / 本屏像素数 (demo 480×640 ⇒ 6.75)。"""
    return float(ref_px) / float(w * h)


def t_compose_est_ms(divisor: float, base: float = T_DISPLAY_OUT_BASE) -> float:
    """合成段 [推算] = 基准画布侧的合成占位 ÷ 像素比 (ISS-212 口径: ÷6.75)。"""
    return base / divisor


def display_out_cap_ms(s5_ms: float, budget_ms: float = BUDGET_MS) -> float:
    """★显示输出侧【总额上限】(ms) —— 与显示分辨率**无关** (只由 60ms 账本的其余部分决定)。"""
    return budget_ms - T_FIXED_OTHER - (s5_ms + POST_MS)


def compose_cap_ms(s5_ms: float, tx_ms: float, budget_ms: float = BUDGET_MS) -> float:
    """★合成段上限 = 输出侧总额上限 − TX 物理下限 (判据必须扣掉 TX, 否则 TX 从预算里消失)。"""
    return display_out_cap_ms(s5_ms, budget_ms) - tx_ms


def e2e_mode_a_ms(s5_ms: float, display_out_ms: float) -> float:
    """★模式A 端到端 (显示等 OD) = 与分辨率无关的部分 + 显示输出侧 + T_od。"""
    return T_FIXED_OTHER + display_out_ms + s5_ms + POST_MS


def age_steps(t_od_ms: float) -> int:
    """框龄台阶 = ceil(T_od / 帧周期) (与整机脚本 age() 同口径)。"""
    return math.ceil(t_od_ms / FRAME_MS)


def r2(x: float) -> float:
    """两位小数 (文档口径)。"""
    return round(x, 2)


# =============================================================================
# §3 报表
# =============================================================================
def compute_report(fault: str | None = None, **overrides) -> dict:
    """算一份完整 demo 预算账。

    fault = None 时是正常路径; fault ∈ {故障名} 时**故意把账算坏**, 供自检做反向用例
    (★模拟"有人把 demo 真源改坏了" ⇒ 检出器必须红★)。
    """
    p = dict(w=DEMO_W, h=DEMO_H, lanes=DEMO_LANES, bpp=BITS_PER_PIXEL,
             rate_a=LANE_RATE_A_GBPS, eff_a=LANE_EFF_A,
             rate_b=LANE_RATE_B_GBPS, eff_b=LANE_EFF_B,
             overhead_bits=PAYLOAD_OVERHEAD_BITS, budget_ms=BUDGET_MS,
             t_compose_ms=None, t_display_ms=None)
    p.update(overrides)

    # ── 故障注入 (★只给自检用★) ──
    div = scale_divisor(p["w"], p["h"])
    if fault == "tx_from_machine_lanes":
        p["lanes"] = 4                      # ★拿了整机 4 通道常量冒充 demo★
    elif fault == "wrong_demo_resolution":
        p["w"], p["h"] = 800, 600           # ★分辨率写错★
    elif fault == "lane_count_wrong":
        p["lanes"] = 3                      # ★通道数写错★
    elif fault == "payload_half":
        p["bpp"] = 12                       # ★payload 少算一半★
    elif fault == "eff_a_full":
        p["eff_a"] = 1.0                    # ★口径 A 被悄悄改成 100% 效率★
    elif fault == "compose_not_scaled":
        div = 1.0                           # ★合成没按像素比缩放★
    if fault == "compose_not_scaled":
        div = 1.0

    bits = payload_bits(p["w"], p["h"], p["bpp"], p["overhead_bits"])
    tx_a = tx_floor_ms(p["w"], p["h"], p["bpp"], p["lanes"], p["rate_a"], p["eff_a"], p["overhead_bits"])
    tx_b = tx_floor_ms(p["w"], p["h"], p["bpp"], p["lanes"], p["rate_b"], p["eff_b"], p["overhead_bits"])
    tc_est = t_compose_est_ms(div)
    tc_used = p["t_compose_ms"] if p["t_compose_ms"] is not None else tc_est
    td_used = p["t_display_ms"] if p["t_display_ms"] is not None else tx_a
    display_out_used = tc_used + td_used

    rows = []
    for plan in MODEL_PLANS:
        s5 = plan["s5_ms"]
        t_od = s5 + POST_MS
        cap = display_out_cap_ms(s5, p["budget_ms"])
        ccap = compose_cap_ms(s5, tx_a, p["budget_ms"])
        e2e = e2e_mode_a_ms(s5, display_out_used)
        margin = p["budget_ms"] - e2e
        age = age_steps(t_od)
        e2e_b = T_FIXED_OTHER + display_out_used + age * FRAME_MS
        rows.append({
            "name": plan["name"], "s5_ms": s5, "note": plan["note"],
            "t_od_ms": r2(t_od),
            "display_out_cap_ms": r2(cap),
            "compose_cap_ms": r2(ccap),
            "display_out_used_ms": r2(display_out_used),
            "e2e_mode_a_ms": r2(e2e),
            "margin_ms": r2(margin),
            "age": age,
            "e2e_mode_b_ms": r2(e2e_b),
            "margin_b_ms": r2(p["budget_ms"] - e2e_b),
            "verdict": "PASS" if margin >= 0 else "FAIL",
        })

    # ── 计算层故障注入 (★账算错的地方, 检出器必须红★) ──
    if fault == "forget_tx_in_compose_cap":
        for r in rows:
            r["compose_cap_ms"] = r["display_out_cap_ms"]      # ★忘了扣 TX★
    elif fault == "cap_include_tx":
        for r in rows:
            r["display_out_cap_ms"] = r2(r["display_out_cap_ms"] + tx_a)   # ★TX 被扣两次★
            r["compose_cap_ms"] = r2(r["display_out_cap_ms"] - tx_a)
    elif fault == "margin_sign_flip":
        for r in rows:
            r["margin_ms"] = r2(-r["margin_ms"])                # ★余量符号反了★

    return {
        "params": dict(p),
        "scale_divisor": div,
        "payload_bits": bits,
        # ★TX 下限保留 3 位小数 (已发布锚点 2.304 / 2.048 是 3 位) ⇒ 文档口径一致★
        "tx_floor_a_ms": round(tx_a, 3),
        "tx_floor_b_ms": round(tx_b, 3),
        "tx_floor_a_raw": tx_a,
        "tx_floor_b_raw": tx_b,
        "t_compose_est_ms": r2(tc_est),
        "t_compose_used_ms": r2(tc_used),
        "t_display_used_ms": r2(td_used),
        "display_out_used_ms": r2(display_out_used),
        "display_out_est_ms": r2(display_out_used),
        "budget_ms": p["budget_ms"],
        "t_fixed_other_ms": T_FIXED_OTHER,
        "post_ms": POST_MS,
        "frame_ms": FRAME_MS,
        "plans": rows,
        "fault": fault,
    }


# ── 检出器: 认出「账被算坏了」 ────────────────────────────────────────────────
def anomalies(rep: dict) -> list:
    """★检出器: 返回本份账里所有「不该出现」的项 (空列表 = 账是好的)。"""
    out = []
    p = rep["params"]
    exp_div = scale_divisor(480, 640)

    # ① 值型锚点: TX 下限必须复现 ISS-212 已发布值
    if abs(rep["tx_floor_a_ms"] - ANCHOR["tx_floor_a_ms"]) > 0.0005:
        out.append("TX 下限 (口径 A) = %.3f ms ≠ ISS-212 已发布 %.3f ms"
                   % (rep["tx_floor_a_ms"], ANCHOR["tx_floor_a_ms"]))
    if abs(rep["tx_floor_b_ms"] - ANCHOR["tx_floor_b_ms"]) > 0.0005:
        out.append("TX 下限 (口径 B) = %.3f ms ≠ ISS-212 已发布 %.3f ms"
                   % (rep["tx_floor_b_ms"], ANCHOR["tx_floor_b_ms"]))
    # ② demo 屏参数必须与 ISS-212 定版一致 (分辨率 / 通道数)
    if (p["w"], p["h"]) != (480, 640):
        out.append("demo 分辨率 %dx%d ≠ ISS-212 定版 480×640" % (p["w"], p["h"]))
    if p["lanes"] != 2:
        out.append("demo DSI 通道数 %d ≠ ISS-212 定版 2" % p["lanes"])
    # ③ payload 口径 (RGB888 8bpc)
    if p["bpp"] != BITS_PER_PIXEL:
        out.append("每像素比特 %d ≠ RGB888 8bpc 口径 %d" % (p["bpp"], BITS_PER_PIXEL))
    if rep["payload_bits"] != payload_bits(p["w"], p["h"], p["bpp"], p["overhead_bits"]):
        out.append("每帧 payload 与 像素×比特+固定开销 的口径不符")
    # ④ 缩放律必须复现 ISS-212 已发布的 ÷6.75
    if abs(rep["scale_divisor"] - exp_div) > 1e-9:
        out.append("画布缩放除数 %.4f ≠ ISS-212 已发布 %.2f" % (rep["scale_divisor"], exp_div))
    if abs(rep["t_compose_est_ms"] - r2(T_DISPLAY_OUT_BASE / exp_div)) > 0.005:
        out.append("t_compose 估算 %.3f ms ≠ 按像素比缩放值" % rep["t_compose_est_ms"])
    # ⑤ 口径 A 的链路参数必须与 ISS-212 一致
    if (p["rate_a"], p["eff_a"]) != (LANE_RATE_A_GBPS, LANE_EFF_A):
        out.append("口径 A 链路参数 (%s Gbps × %s) ≠ ISS-212 已发布 (2.0 × 0.8)"
                   % (p["rate_a"], p["eff_a"]))
    # ⑥ 结构恒等: 总额上限 / 合成上限 / 余量 / 端到端 必须自洽
    for r in rep["plans"]:
        s5 = r["s5_ms"]
        exp_cap = r2(display_out_cap_ms(s5, rep["budget_ms"]))
        exp_ccap = r2(exp_cap - rep["tx_floor_a_ms"])
        exp_e2e = r2(e2e_mode_a_ms(s5, rep["display_out_used_ms"]))
        exp_margin = r2(rep["budget_ms"] - exp_e2e)
        if abs(r["display_out_cap_ms"] - exp_cap) > 0.005:
            out.append("[%s] 输出侧总额上限 %.2f ≠ 60 − T_FIXED_OTHER − (S5+POST) = %.2f (TX 被重复扣减?)"
                       % (r["name"], r["display_out_cap_ms"], exp_cap))
        if abs(r["compose_cap_ms"] - exp_ccap) > 0.005:
            out.append("[%s] 合成段上限 %.2f ≠ 总额上限 %.2f − TX %.3f (TX 没扣?)"
                       % (r["name"], r["compose_cap_ms"], exp_cap, rep["tx_floor_a_ms"]))
        if abs(r["margin_ms"] - exp_margin) > 0.005:
            out.append("[%s] 全链路余量 %.2f ≠ 60 − e2e %.2f (符号反了?)"
                       % (r["name"], r["margin_ms"], exp_e2e))
        if (r["margin_ms"] >= 0) != (r["e2e_mode_a_ms"] <= rep["budget_ms"]):
            out.append("[%s] 判定与余量符号不一致" % r["name"])
    # ⑦ 整机同源常量的拆分恒等
    if abs((T_PRE_EXPOSURE + T_DRAW + T_PANEL + T_RESIDUAL) - T_FIXED_OTHER) > 1e-9:
        out.append("T_FIXED_OTHER 拆分不恒等 (%.2f+%.2f+%.2f+%.2f ≠ %.2f)"
                   % (T_PRE_EXPOSURE, T_DRAW, T_PANEL, T_RESIDUAL, T_FIXED_OTHER))
    return out


# ── 源码泄漏扫描: 本脚本里不许出现整机 DSI 口径的 token ─────────────────────
def _forbidden_src_tokens() -> list:
    """★整机 DSI 口径 token —— **运行时拼出来**, 这样本文件源码里不会出现它们的字面量
    (否则扫描会打到自己 ⇒ 扫描形同虚设)。"""
    return [
        "7." + "776",          # 整机口径 TX 物理下限
        "12." + "96",          # 整机口径显示输出侧线性上界
        "4." + "32",           # 整机口径像素缩放律
        "2." + "32",           # 整机口径合成段上限
        "1080" + "p",          # 整机口径标记
        "1920" + "×1080",
        "4" + "-lane",         # 整机 DSI 通道数写法
        "DSI_" + "LANES",
        "TX_MIN_" + "1080",
        "TX_MIN_" + "800",
    ]


def source_leak_anomalies(src: str) -> list:
    """★源码泄漏扫描: 整机 DSI 常量一旦被写进本脚本 ⇒ 立刻报出来。"""
    return [t for t in _forbidden_src_tokens() if t in src]


# =============================================================================
# §4 自检 (★反向用例: 改坏必红★)
# =============================================================================
FAULTS = [
    ("forget_tx_in_compose_cap", "合成段上限忘了扣 TX"),
    ("tx_from_machine_lanes", "拿了整机 4 通道常量冒充 demo"),
    ("wrong_demo_resolution", "demo 分辨率写错"),
    ("lane_count_wrong", "demo 通道数写错"),
    ("payload_half", "每帧 payload 少算一半"),
    ("eff_a_full", "口径 A 被改成 100% 效率"),
    ("compose_not_scaled", "合成没按像素比缩放"),
    ("cap_include_tx", "TX 被重复扣减"),
    ("margin_sign_flip", "余量符号反了"),
]


def selftest_summary() -> dict:
    """★自检结果 (机读): {'passed': n, 'total': m, 'cases': [...]}"""
    cases = []

    def add(name, ok, detail=""):
        cases.append({"name": name, "ok": bool(ok), "detail": detail})

    # G1 好样本必须一份异常都检不出
    base = compute_report()
    bad = anomalies(base)
    add("好样本零异常", not bad, "检出: %s" % bad if bad else "0 项")

    # G2 每一种"改坏"都必须被抓到 (★改坏必红★)
    for fault, desc in FAULTS:
        rep = compute_report(fault=fault)
        hits = anomalies(rep)
        add("改坏必红: %s" % desc, bool(hits), "检出 %d 项: %s" % (len(hits), hits[:2]))

    # G3 已发布 demo 数值必须逐位复现 (ISS-212 / ISS-215 锚点)
    got = {
        "tx_floor_a_ms": base["tx_floor_a_ms"],
        "tx_floor_b_ms": base["tx_floor_b_ms"],
        "scale_divisor": base["scale_divisor"],
        "t_compose_est_ms": base["t_compose_est_ms"],
        "display_out_est_ms": base["display_out_est_ms"],
        "cap_yolov5s_ms": base["plans"][0]["display_out_cap_ms"],
        "compose_yolov5s_ms": base["plans"][0]["compose_cap_ms"],
        "cap_yolov5n_ms": base["plans"][1]["display_out_cap_ms"],
        "compose_yolov5n_ms": base["plans"][1]["compose_cap_ms"],
        "cap_yolov5s320_ms": base["plans"][2]["display_out_cap_ms"],
        "compose_yolov5s320_ms": base["plans"][2]["compose_cap_ms"],
        "margin_yolov5n_ms": base["plans"][1]["margin_ms"],
    }
    for k, want in ANCHOR.items():
        ok = abs(got[k] - want) <= 0.005
        add("已发布值复现: %s = %s" % (k, want), ok, "本脚本 %.3f" % got[k])

    # G4 判据 ↔ 算账必须互为逆运算 (★测出 ≤ 判据 ⇒ 端到端恰好 60.00ms★)
    s5 = 13.31
    tx_a = base["tx_floor_a_raw"]
    ccap = compose_cap_ms(s5, tx_a)
    e2e_at_cap = e2e_mode_a_ms(s5, ccap + tx_a)
    add("判据↔算账互逆 (合成取上限 + 上屏取 TX 下限 ⇒ e2e 恰 60.00)",
        abs(e2e_at_cap - 60.0) < 1e-6, "e2e = %.6f" % e2e_at_cap)

    # G5 TX 必须真的随像素数线性 (payload 固定开销 = 0 时)
    t1 = tx_floor_ms(480, 640, 24, 2, 2.0, 0.8, 0)
    t2 = tx_floor_ms(640, 960, 24, 2, 2.0, 0.8, 0)   # 像素数 ×2
    add("TX 随像素数线性 (2× 像素 ⇒ 2× 时间)", abs(t2 - 2 * t1) < 1e-9,
        "%.3f → %.3f" % (t1, t2))
    t3 = tx_floor_ms(480, 640, 24, 2, 2.0, 0.8, 1000)   # 加每帧固定开销 ⇒ 破坏线性
    add("每帧 payload 固定开销会生效 (加 1000 bit ⇒ TX 变长)", t3 > t1,
        "%.6f → %.6f" % (t1, t3))

    # G6 通道数翻倍 ⇒ TX 减半 (换屏时账必须跟着变)
    t4 = tx_floor_ms(480, 640, 24, 4, 2.0, 0.8, 0)
    add("通道数翻倍 ⇒ TX 减半", abs(t4 - t1 / 2) < 1e-9, "%.3f vs %.3f" % (t4, t1 / 2))

    # G7 ★鲁棒性: t_compose 估算 ×0.5 / ×1 / ×2 ⇒ 全链路余量都 > 0 (口径瑕疵不翻结论)★
    robust = []
    for k in (0.5, 1.0, 2.0):
        rep = compute_report(t_compose_ms=base["t_compose_est_ms"] * k)
        robust.append((k, rep["plans"][1]["margin_ms"]))
    add("t_compose 估算 ×0.5/×1/×2 ⇒ 余量都 > 0 (判定不翻)",
        all(m > 0 for _, m in robust), "; ".join("×%s⇒%.2fms" % (k, m) for k, m in robust))

    # G8 源码不许含整机 DSI 口径 token (★真源不许被整机常量污染★)
    try:
        with open(os.path.abspath(__file__), encoding="utf-8") as f:
            src = f.read()
        leaks = source_leak_anomalies(src)
        add("本脚本源码无整机 DSI 口径 token", not leaks, "泄漏: %s" % leaks if leaks else "0 项")
        # 反向: 注入 token 后必须被抓到
        injected = src + "\n# " + "7." + "776\n"
        add("源码泄漏扫描能抓住被注入的整机 token", bool(source_leak_anomalies(injected)),
            "注入后检出 %d 项" % len(source_leak_anomalies(injected)))
    except OSError as exc:
        add("本脚本源码无整机 DSI 口径 token", False, "读不到自身源码: %s" % exc)

    # G9 模式B 框龄台阶必须与整机脚本同口径 (ceil)
    add("框龄台阶 ceil 口径 (T_od 18.91 ⇒ age=2)", age_steps(13.31 + POST_MS) == 2,
        "age = %d" % age_steps(13.31 + POST_MS))

    # G10 板端实测代入必须立刻改判 (★--t-compose-ms / --t-display-ms 通路是活的★)
    rep_big = compute_report(t_compose_ms=20.0, t_display_ms=5.0)
    add("板端实测代入后余量转负 (合成 20ms + 上屏 5ms ⇒ 判不过)",
        rep_big["plans"][1]["margin_ms"] < 0,
        "余量 %.2f ms" % rep_big["plans"][1]["margin_ms"])

    passed = sum(1 for c in cases if c["ok"])
    return {"passed": passed, "total": len(cases), "cases": cases}


def selftest(verbose: bool = True) -> int:
    res = selftest_summary()
    if verbose:
        print("=" * 78)
        print("自检 (demo_e2e_budget): %d/%d" % (res["passed"], res["total"]))
        print("=" * 78)
        for c in res["cases"]:
            print("  %s %-52s %s" % ("✅" if c["ok"] else "❌", c["name"], c["detail"][:70]))
        print("-" * 78)
        print("★反向用例: 9 种「改坏」+ 1 种「源码污染」全部必须红 ⇒ 改坏必红")
    return 0 if res["passed"] == res["total"] else 1


# =============================================================================
# §5 主表输出
# =============================================================================
def _fmt(v: float) -> str:
    return ("%.2f" % v).replace("-", "−")


def _fmt3(v: float) -> str:
    """三位小数 (TX 物理下限口径: 已发布锚点 2.304 / 2.048 是 3 位)。"""
    return ("%.3f" % v).replace("-", "−")


def show_report(rep: dict) -> None:
    print("=" * 100)
    print("demo 屏 端到端预算真源 (ISS-221) —— ★**demo 侧每一个预算数都从这里算出来**★")
    print("=" * 100)
    p = rep["params"]
    print("\n【§1 口径声明 —— 两类常量不许混】")
    print("  %s" % ("─" * 96))
    print("  (A) 整机同源常量 (★只引用, 不重算整机的账★):")
    print("      T_FIXED_OTHER = %.2f ms  (= 曝光块 %.2f + 画框 %.2f + 光机 %.2f + 反解余量 %.2f)  ★与整机账本同名同值"
          % (T_FIXED_OTHER, T_PRE_EXPOSURE, T_DRAW, T_PANEL, T_RESIDUAL))
    print("      POST_MS = %.2f ms · FRAME_MS = %.2f ms · 显示输出侧占位 S9 = %.2f ms (只做缩放基准)"
          % (POST_MS, FRAME_MS, T_DISPLAY_OUT_BASE))
    print("  (B) demo 专属常量 (★本脚本的真源★):")
    print("      屏 = %d×%d (%d px, %.4f Mpx) · DSI 通道数 = %d · 每像素 %d bit (RGB888 8bpc)"
          % (p["w"], p["h"], p["w"] * p["h"], p["w"] * p["h"] / 1e6, p["lanes"], p["bpp"]))
    print("      口径 A = %.1f Gbps/通道 × %.0f%% 效率 · 口径 B = %.1f Gbps/通道 × %.0f%% 效率 · 每帧固定开销 = %d bit"
          % (p["rate_a"], p["eff_a"] * 100, p["rate_b"], p["eff_b"] * 100, p["overhead_bits"]))
    print("      画布缩放除数 = %.2f (基准画布 %d px) · 60ms 硬预算 = %.0f ms"
          % (rep["scale_divisor"], SCALE_REF_PX, rep["budget_ms"]))
    print("  %s" % ("─" * 96))
    print("  ★**本脚本不含任何整机 DSI 链路常量** (自检 §G8 源码泄漏扫描盯着) ⇒ ★**换屏只改 (B) 或用命令行** ★")

    print("\n【§2 demo 屏 TX 物理下限 (★一帧比特 / 链路有效带宽★)】")
    print("      每帧 payload = %d × %d × %d bit + %d bit(固定开销) = %d bit (%.4f Mbit)"
          % (p["w"], p["h"], p["bpp"], p["overhead_bits"], rep["payload_bits"],
             rep["payload_bits"] / 1e6))
    print("      口径 A: %d 通道 × %.1f Gbps × %.0f%% ⇒ 有效 %.0f Mbps ⇒ ★**TX 下限 = %s ms**★"
          % (p["lanes"], p["rate_a"], p["eff_a"] * 100,
             p["lanes"] * p["rate_a"] * 1000 * p["eff_a"], _fmt3(rep["tx_floor_a_ms"])))
    print("      口径 B: %d 通道 × %.1f Gbps × %.0f%% ⇒ 有效 %.0f Mbps ⇒ ★**TX 下限 = %s ms**★"
          % (p["lanes"], p["rate_b"], p["eff_b"] * 100,
             p["lanes"] * p["rate_b"] * 1000 * p["eff_b"], _fmt3(rep["tx_floor_b_ms"])))
    print("      ★**TX 随像素数线性、随通道数反比 ⇒ 换屏时这一项自动跟着变, 不用去整机账里减** ★")

    print("\n【§3 demo 显示输出侧 [推算] 与 60ms 预算账】")
    print("      t_compose 估算 = S9 占位 %.2f ÷ %.2f = %s ms  [推算]"
          % (T_DISPLAY_OUT_BASE, rep["scale_divisor"], _fmt(rep["t_compose_est_ms"])))
    print("      显示输出侧合计 = t_compose %s + 上屏(TX 下限) %s = %s ms  [推算]"
          % (_fmt(rep["t_compose_used_ms"]), _fmt3(rep["t_display_used_ms"]),
             _fmt(rep["display_out_est_ms"])))
    print("      %s" % ("─" * 96))
    hdr = ("%-24s%9s%14s%14s%12s%12s%10s" %
           ("方案", "S5(ms)", "输出侧总额上限", "合成段上限", "端到端A(ms)", "余量(ms)", "判定"))
    print("      " + hdr)
    print("      " + "-" * (len(hdr) + 12))
    for r in rep["plans"]:
        print("      %-24s%9s%14s%14s%12s%12s%10s"
              % (r["name"], _fmt(r["s5_ms"]), _fmt(r["display_out_cap_ms"]) + " ms",
                 _fmt(r["compose_cap_ms"]) + " ms", _fmt(r["e2e_mode_a_ms"]),
                 _fmt(r["margin_ms"]), "✅ 过" if r["verdict"] == "PASS" else "❌ 不过"))
    print("      %s" % ("─" * 96))
    print("      ★**「输出侧总额上限」与显示分辨率无关** (60 − T_FIXED_OTHER − (S5+POST));")
    print("      ★**「合成段上限」= 总额上限 − demo TX 下限** ⇒ ★**判据里 TX 不许消失** ★")
    print("      ★**板端实测 (t_compose / t_display) 一律 [0数据] ⇒ 本表全部是 [推算]** ★")

    print("\n【§4 口径沿用与已知瑕疵 (诚实记录, 不在本单偷改)】")
    print("      · ISS-212 把 S9 占位 %.2f ms 当作缩放基准画布侧的合成占位, 按像素比缩放到 demo 屏"
          % T_DISPLAY_OUT_BASE)
    print("        ⇒ %s ÷ %.2f = %s ms —— ★**本脚本沿用该已发布口径** ★" %
          (("%.2f" % T_DISPLAY_OUT_BASE), rep["scale_divisor"], _fmt(rep["t_compose_est_ms"])))
    print("      · 已知瑕疵: 整机账本里该占位是【整机 800×600 基线】的值, 严格拆法要用整机 DSI 常量")
    print("        ⇒ ★**本脚本按纪律不引入整机 DSI 常量 ⇒ 只能沿用 ISS-212 口径** ★")
    print("      · ★**结论稳健性 (自检 G7 守着)**: t_compose 估算 ×0.5 / ×1 / ×2 三档, 全链路余量都 > 0")
    print("        ⇒ ★**口径瑕疵不改变 60ms 生死判定** ★")
    print("      · 整机路线 (整机屏) 的账仍在 `HW/e2e_budget_rk3572.py` 里 —— ★**两本互不代算** ★")


def main() -> int:
    ap = argparse.ArgumentParser(description="demo 屏 (2 通道 @480×640) 端到端预算真源 (ISS-221)")
    ap.add_argument("--selftest", action="store_true", help="自检 (反向用例: 改坏必红)")
    ap.add_argument("--json", action="store_true", help="机读输出")
    ap.add_argument("--width", type=int, default=DEMO_W)
    ap.add_argument("--height", type=int, default=DEMO_H)
    ap.add_argument("--lanes", type=int, default=DEMO_LANES)
    ap.add_argument("--lane-rate-gbps", type=float, default=LANE_RATE_A_GBPS)
    ap.add_argument("--lane-eff", type=float, default=LANE_EFF_A)
    ap.add_argument("--payload-overhead-bits", type=int, default=PAYLOAD_OVERHEAD_BITS)
    ap.add_argument("--t-compose-ms", type=float, default=None, help="板端实测: 第7段合成 (ms)")
    ap.add_argument("--t-display-ms", type=float, default=None, help="板端实测: 第8段上屏 (ms)")
    a = ap.parse_args()

    if a.selftest:
        return selftest()

    rep = compute_report(w=a.width, h=a.height, lanes=a.lanes, rate_a=a.lane_rate_gbps,
                          eff_a=a.lane_eff, overhead_bits=a.payload_overhead_bits,
                          t_compose_ms=a.t_compose_ms, t_display_ms=a.t_display_ms)

    if a.json:
        print(json.dumps(rep, ensure_ascii=False, indent=2))
        return 0

    show_report(rep)

    if a.t_compose_ms is not None or a.t_display_ms is not None:
        print("\n【§5 代入板端实测后的结论】")
        print("      代入: t_compose = %s ms%s · t_display = %s ms%s"
              % (a.t_compose_ms if a.t_compose_ms is not None else "—",
                 " [实测·板端]" if a.t_compose_ms is not None else "",
                 a.t_display_ms if a.t_display_ms is not None else "—",
                 " [实测·板端]" if a.t_display_ms is not None else ""))
        print("      显示输出侧合计 = %s ms  ⇒ 端到端与余量见上表" % _fmt(rep["display_out_est_ms"]))
        for r in rep["plans"]:
            print("      %-24s 端到端A = %s ms · 余量 = %s ms ⇒ %s"
                  % (r["name"], _fmt(r["e2e_mode_a_ms"]), _fmt(r["margin_ms"]),
                     "✅ 过" if r["verdict"] == "PASS" else "❌ 不过"))
        print("      ★**注意**: 上屏段若实测出比物理下限更大的值 ⇒ 端到端要再减 ⇒ ★**第8段必须也打点** ★")

    hits = anomalies(rep)
    if hits:
        print("\n❌ 本份账检出 %d 项异常 (换屏后必须人工确认):" % len(hits))
        for h in hits:
            print("   - %s" % h)
        return 1
    print("\n✅ 自检: 本份账零异常 (值型锚点 / 结构恒等 全部对齐)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
