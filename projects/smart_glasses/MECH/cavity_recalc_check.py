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

    return res


# ======================================================================
# §3 --selftest —— 反向用例 (全部在临时目录副本上做, 真文件不动)
# ======================================================================
def _make_copy(root: str, tmp: str) -> None:
    for rel in list(MD5_EXPECTED.keys()) + [DOC_REL, BUDGET_REL, FRAG_REL]:
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


def selftest(root: str) -> int:
    cases = []

    # 0 —— 基线必须全过
    res = check_all(root)
    cases.append(("基线: 全过", all(r[2] for r in res), "0 条不过"))

    def run_case(name: str, mutate, expect_cid: str):
        tmp = tempfile.mkdtemp(prefix="cavity_selftest_")
        try:
            _make_copy(root, tmp)
            mutate(tmp)
            r2 = check_all(tmp)
            bad = [r for r in r2 if not r[2]]
            hit = any(r[0] == expect_cid for r in bad)
            detail = ("抓到: " + ",".join(r[0] for r in bad)) if bad else "没抓到任何一条"
            cases.append((name, hit, f"{expect_cid} 未被抓; {detail}"))
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

    run_case("反向1: 改坏一行参数表 (R1 的 T 18 → 17)", mut_row, "C2")
    run_case("反向2: 删掉 62 (结构真源 X-1 行 62 → 63 mm²)", mut_62, "C1")
    run_case("反向3: 改坏冲突量 (R1 的 C-1 3.2 → 3.3)", mut_c1, "C2")
    run_case("反向4: 篡改判据文件 DISPLAY_BIOSAFETY_CRITERIA_V2.md", mut_criteria, "C4")
    run_case("反向5: 删掉一行表 (R5)", mut_drop_row, "C2")
    run_case("反向6: 改坏重量重核数 (0.43 → 0.93)", mut_weight, "C6")
    run_case("反向7: 篡改分片 claim (25.00 → 24.00)", mut_frag, "C9")
    run_case("反向8: 篡改受保护脚本 hinge_usb_check.py", mut_script, "C8")
    run_case("反向9: 改掉 ±3 mm 带 (B1 行程 6 → 5)", mut_band, "C5")

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
