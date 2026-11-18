#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-047 复核脚本 —— 「对角半角」不能用来判垂直俯角 (2026-11-02)
=====================================================================
为什么有这个脚本:
    ① 老板 10-25 基线里, 结构侧 MECH §1.5 拿「半对角 50°/60°」减俯角再减 10° 余量,
       推出「可接受最大偏置 ≤40°/≤50°」, 并把 **垂直俯角** 和 **水平偏置** 混在一张表里。
       hw-lead 指出: **垂直俯角只能由垂直半视场决定** (16:9 对角 100° → 垂直半视场只有
       30.30°, 不是 50°)。⇒ 本脚本 §1 复现这个数并量化旧结论高估多少。
    ② 「对角 120°」不是一个自洽的数 —— 直行 (r=f·tanθ) 与 等距/鱼眼 (r=f·θ) 的垂直半视场
       差 10.9°。⇒ 表里任何 FOV 数必须连**投影模型**一起说。
    ③ 11-02 09:41 老板拍板 sensor = onsemi **AR0234CS 1920×1200@60 整幅不裁剪** ⇒
       现行基线的靶面/窗口/对角 FOV 全部变了, 旧表要重算 (ISS-052 那版是 10-29 的基线)。

本脚本做五件事 (全部可复现, 无外部依赖, **0 条实测数据**):
    §1 口径核验: 复现 hw-lead 的「16:9 对角 100° → 垂直半视场 30.30°」; 量化旧 ≤40° 结论。
    §2 完整五数对应表: 对角FOV / 水平FOV / 垂直FOV / 垂直半视场 / 俯角余量,
       覆盖 4 种读出窗口 × 2 种投影模型 × 3 档对角 FOV。
    §3 「正前方是否在画面内」判定表 (每个俯角一个标记), 含**边框遮挡**后的有效余量。
    §4 俯角上限 → 结构硬约束 h_max (d = 30/32/35mm), 三档判据 A/B/C。
    §5 路线映射 (ISS-138 A/B/C/D) → 结构侧结论 + 与上游口径不一致的 2 处。

投影模型:
    直行 (rectilinear):  r = f·tanθ   → θ = atan(r/f)
    等距 (equidistant):  r = f·θ      → θ = r/f
俯角余量:
    名义余量 = 垂直半视场 − 俯角                    (名义余量 < 0 ⇒ 正前方掉出画面)
    有效余量 = 名义余量 − 边框遮挡角                 (遮挡角吃的是**上半视场** = 正前方那一侧)
    边框遮挡角 = atan(凹进量 / d), 凹进 1.0mm, d=30 → 1.91°  (沿用 MECH §1.5.1 口径)

用法:
    python3 MECH/iss047_fov_table.py            # 全量复算 + 判定 (rc=0 = 全部自检过)
    python3 MECH/iss047_fov_table.py --json     # 机器可读
"""
from __future__ import annotations

import argparse
import json
import math

D = math.degrees
R = math.radians

# ------------------------------------------------------------------ 读出窗口
# name: (宽px, 高px, 像元µm, 备注)
WINDOWS = {
    "AR0234CS 整幅 1920x1200": (1920, 1200, 3.000,
        "★现行定案 (11-02 09:41 老板拍板「使用D」) + 老板 10-25「禁止 ROI/crop」⇒ 整幅不裁剪"),
    "OV04C10 1080p 1920x1080": (1920, 1080, 1.998,
        "备选 (11-02 02:04 老板一度定 OV) @1080p60 直出 = 全幅裁到 1080p ⇒ 镜头必须按**裁切窗口**重算"),
    "OV04C10 整幅 2688x1520": (2688, 1520, 1.998,
        "OV04C10 全画幅 (若选 OV 且坚持不裁剪)"),
    "AR0234CS 裁1080p 1920x1080": (1920, 1080, 3.000,
        "★作废口径 (老板 10-25「禁止 ROI/crop」): AR0234CS 16:10 裁到 16:9 ⇒ 垂直半视场 31.80→28.62"),
}
GRADES = (100, 110, 120)
MODELS = (("rectilinear", "直行 r=f·tanθ"), ("equidistant", "等距(鱼眼) r=f·θ"))
TILTS = (15.0, 20.0, 25.0, 28.0, 30.0, 32.0)

# ------------------------------------------------------------------ 结构侧常数
D_EYE = (30.0, 32.0, 35.0)     # 镜片到眼点距离 d (mm)
RECESS_DESIGN = 1.0            # 前镜片顶点相对镜框上沿外表面凹进 (mm), MECH §1.5.2
MARGIN_A, MARGIN_B, MARGIN_C = 0.0, 4.0, 10.0   # 三档余量判据 (度)
TILT_BASELINE = 25.0           # PM/hw-lead 工作基线俯角 (MECH §1.5.2)

FAIL: list[str] = []
WARN: list[str] = []


def rec(ok: bool, msg: str, warn: bool = False) -> None:
    tag = "OK  " if ok else ("WARN" if warn else "FAIL")
    print(f"  [{tag}] {msg}")
    if not ok:
        (WARN if warn else FAIL).append(msg)


def win_geom(w, h, px):
    W, H = w * px / 1000.0, h * px / 1000.0
    return {"W": W, "H": H, "d": math.hypot(W, H), "px": px}


def f_for(diag_mm: float, diag_fov: float, model: str) -> float:
    """按读出窗口对角线 + 目标对角 FOV 反算焦距。"""
    half = R(diag_fov / 2.0)
    return (diag_mm / 2.0) / (math.tan(half) if model == "rectilinear" else half)


def row_for(w, h, px, model, grade):
    g = win_geom(w, h, px)
    f = f_for(g["d"], grade, model)
    if model == "rectilinear":
        h_half = D(math.atan((g["W"] / 2.0) / f))
        v_half = D(math.atan((g["H"] / 2.0) / f))
    else:
        h_half = D((g["W"] / 2.0) / f)
        v_half = D((g["H"] / 2.0) / f)
    return {"f": f, "h_fov": 2 * h_half, "h_half": h_half,
            "v_fov": 2 * v_half, "v_half": v_half, "d": g["d"]}


def occlusion_deg(recess: float = RECESS_DESIGN, d: float = 30.0) -> float:
    """边框遮挡角 (吃掉上半视场 = 正前方那一侧)。沿用 MECH §1.5.1 口径: atan(凹进/d)。"""
    return D(math.atan(recess / d))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    out = {}
    occ = occlusion_deg()

    print("=" * 100)
    print("§1  口径核验: 「半对角 50°」能不能用来判垂直俯角?")
    print("=" * 100)
    # 16:9 理想比例, 对角 100°, 直行
    dnorm = math.hypot(16.0, 9.0)
    f16 = (dnorm / 2.0) / math.tan(R(50.0))
    v16 = D(math.atan((9.0 / 2.0) / f16))
    h16 = D(math.atan((16.0 / 2.0) / f16))
    print(f"  16:9 理想靶面, 对角 100°, 直行:  水平半视场 {h16:.2f}° | 垂直半视场 {v16:.2f}°")
    rec(abs(v16 - 30.30) < 0.05,
        f"复现 hw-lead 的数: 16:9 对角 100° → 垂直半视场 {v16:.2f}° (他说 30.3°) ✅ 一致")
    print(f"  ★ 旧表算法: 半对角 50° − 俯角 − 余量 10° ⇒ 「可接受最大偏置 ≤40°」")
    print(f"    真实上限 (判据 A, 余量 0): 俯角 ≤ {v16:.2f}°; (判据 B, 余量 4°): ≤ {v16 - 4:.2f}°")
    rec(v16 < 40.0, f"旧结论 40° 比真实上限高 {40.0 - v16:.2f}° ⇒ **整表作废** (ISS-047 成立)")
    print("  ★ 旧表第二个错: 把「垂直俯角」和「水平偏置」放同一列比 —— 二者由不同量决定")
    print("    (垂直俯角 → 垂直半视场; 水平偏置 → 水平半视场), 物理上不可互换。")
    print("  ★ 旧表第三个错: 「对角 FOV」没带投影模型 —— 直行 vs 等距同一'对角120°'差 10.9° 垂直半视场。")
    out["calib_16x9_100"] = {"h_half": h16, "v_half": v16}

    print()
    print("=" * 100)
    print("§2  ★ 完整五数对应表 (对角FOV / 水平FOV / 垂直FOV / 垂直半视场 / 俯角余量)")
    print("=" * 100)
    print("  口径: 镜头按**读出窗口**的对角线设计到目标对角 FOV; 俯角余量 = 垂直半视场 − 俯角;")
    print(f"        余量 < 0 ⇒ 正前方**掉出画面**; 有效余量 = 名义余量 − 边框遮挡 {occ:.2f}° (凹进 1.0mm @d=30)。")
    print()
    tbl = {}
    for wname, (w, h, px, memo) in WINDOWS.items():
        g = win_geom(w, h, px)
        print(f"● {wname}  —— 读出窗口 {w}x{h}px @ {px}µm = {g['W']:.4f} x {g['H']:.4f}mm, "
              f"对角 {g['d']:.4f}mm")
        print(f"    {memo}")
        for model, mname in MODELS:
            print(f"  -- 投影模型: {mname}")
            print(f"     {'对角FOV':>7} {'f(mm)':>7} {'水平FOV':>9} {'垂直FOV':>9} {'垂直半视场':>10} "
                  f"{'水平半视场':>10} {'偏置10°余量':>11}")
            for gr in GRADES:
                r = row_for(w, h, px, model, gr)
                print(f"     {gr:>6}° {r['f']:>7.3f} {r['h_fov']:>8.2f}° {r['v_fov']:>8.2f}° "
                      f"{r['v_half']:>9.2f}° {r['h_half']:>9.2f}° {r['h_half'] - 10.0:>+10.2f}°")
            print()
            tbl.setdefault(wname, {})[model] = [row_for(w, h, px, model, gr) for gr in GRADES]
    out["table"] = tbl

    print("=" * 100)
    print("§3  ★★ 「正前方是否在画面内」判定表 (每个俯角一个标记)")
    print("=" * 100)
    print("  名义余量 = 垂直半视场 − 俯角; 有效余量 = 名义余量 − 边框遮挡角 (遮挡吃上半视场 = 正前方侧)")
    print("  标记: [在画面内] / [临界 有效<0] / [掉出 名义<0] / [遮挡后掉出 名义>0 但有效<0]")
    print()
    verdict = {}
    for wname in ("AR0234CS 整幅 1920x1200", "OV04C10 1080p 1920x1080",
                  "OV04C10 整幅 2688x1520", "AR0234CS 裁1080p 1920x1080"):
        w, h, px, _ = WINDOWS[wname]
        for model, mname in MODELS:
            print(f"● {wname} · {mname}")
            for gr in GRADES:
                r = row_for(w, h, px, model, gr)
                cells = []
                for t in TILTS:
                    m = r["v_half"] - t
                    me = m - occ
                    if m < 0:
                        tag = "掉出"
                    elif me < 0:
                        tag = "遮挡后掉出"
                    elif me < MARGIN_B:
                        tag = "临界"
                    else:
                        tag = "在画面内"
                    cells.append(f"{m:>+6.2f}/{me:>+6.2f} {tag}")
                print(f"   对角 {gr:>3}° 垂直半视场 {r['v_half']:>6.2f}° | " + " | ".join(cells))
                verdict[f"{wname}|{model}|{gr}"] = {
                    "v_half": r["v_half"],
                    "margins": {t: {"nominal": r["v_half"] - t, "eff": r["v_half"] - t - occ}
                                for t in TILTS}}
            print()
    out["verdict"] = verdict

    print("=" * 100)
    print("§4  俯角上限 → 结构侧硬约束: 摄像头光轴中心高于用户视线的高度 h_max")
    print("=" * 100)
    print("  俯角 = atan(h/d) ⇒ h_max = d · tan(俯角上限); d = 镜片到眼点距离\n")
    key = {
        "★现行定案 AR0234CS 整幅 等距 120°": ("AR0234CS 整幅 1920x1200", "equidistant", 120),
        "备选 OV04C10 1080p 等距 120°": ("OV04C10 1080p 1920x1080", "equidistant", 120),
        "旧基线 OV04C10 整幅 等距 120°": ("OV04C10 整幅 2688x1520", "equidistant", 120),
    }
    lim = {}
    for label, (wname, model, gr) in key.items():
        w, h, px, _ = WINDOWS[wname]
        r = row_for(w, h, px, model, gr)
        vh = r["v_half"]
        a = vh                      # 判据A: 名义余量 >= 0
        b = vh - MARGIN_B           # 判据B: 名义余量 >= 4°
        c = vh - MARGIN_C           # 判据C: 名义余量 >= 10°
        a_eff = vh - occ            # 硬上限: 扣掉边框遮挡后余量 = 0
        b_eff = vh - occ - MARGIN_B  # 判据B': **有效**余量 >= 4° (遮挡后还剩 4°)
        print(f"● {label}: 垂直半视场 {vh:.2f}° (扣边框遮挡 {occ:.2f}° 后有效半视场 {a_eff:.2f}°)")
        print(f"    判据A 名义余量>=0  ⇒ 俯角 ≤{a:>6.2f}°   h_max(d=30/32/35) = "
              + "/".join(f"{d * math.tan(R(a)):.2f}" for d in D_EYE) + " mm")
        print(f"    判据B 名义余量>=4° ⇒ 俯角 ≤{b:>6.2f}°   h_max(d=30/32/35) = "
              + "/".join(f"{d * math.tan(R(b)):.2f}" for d in D_EYE) + " mm")
        print(f"    ★判据B' 有效余量>=4° ⇒ 俯角 ≤{b_eff:>6.2f}°   h_max(d=30/32/35) = "
              + "/".join(f"{d * math.tan(R(b_eff)):.2f}" for d in D_EYE) + " mm  ← 含边框遮挡")
        print(f"    判据C 名义余量>=10°⇒ 俯角 ≤{c:>6.2f}°   h_max(d=30/32/35) = "
              + "/".join(f"{d * math.tan(R(c)):.2f}" for d in D_EYE) + " mm")
        print(f"    ⇒ 硬上限(考虑遮挡) ≤{a_eff:.2f}°;  工程基线俯角 {TILT_BASELINE:.0f}° "
              f"(PM/hw-lead 基线) ⇒ h_max = " +
              " / ".join(f"{d * math.tan(R(TILT_BASELINE)):.2f}" for d in D_EYE) + " mm (d=30/32/35)")
        lim[label] = {"v_half": vh, "v_half_eff": a_eff, "A": a, "B": b, "B_eff": b_eff, "C": c}
        print()
    out["tilt_limits"] = lim

    print("=" * 100)
    print("§5  路线映射 (ISS-138): 四条路线 → 结构侧结论")
    print("=" * 100)
    routes = {
        "A. OV04C10 整幅 2688x1520@60 + 鱼眼 f=2.9459": ("OV04C10 整幅 2688x1520", "equidistant", None),
        "B. OV04C10 1080p60 + 同一颗镜头 f=2.9459": ("OV04C10 1080p 1920x1080", "equidistant", None),
        "C. OV04C10 1080p60 + 镜头改短 (保住 120°)": ("OV04C10 1080p 1920x1080", "equidistant", 120),
        "★D. AR0234CS 1920x1200@60 整幅不裁剪 (已定案)": ("AR0234CS 整幅 1920x1200", "equidistant", 120),
    }
    print(f"  {'路线':<48} {'垂直半视场':>10} {'硬上限(扣遮挡)':>14} {'俯角25°余量':>12}  结构侧判定")
    for label, (wname, model, gr) in routes.items():
        w, h, px, _ = WINDOWS[wname]
        if gr is None:  # 镜头不变 (f 固定), FOV 由读出窗口裁切决定
            g = win_geom(w, h, px)
            f_fixed = 2.9459
            v_half = D((g["H"] / 2.0) / f_fixed)
            h_half = D((g["W"] / 2.0) / f_fixed)
            diag = 2 * D(math.hypot(g["W"] / 2.0, g["H"] / 2.0) / f_fixed)
            r = {"v_half": v_half, "v_fov": 2 * v_half, "h_fov": 2 * h_half, "h_half": h_half,
                 "f": f_fixed, "d": g["d"]}
        else:
            r = row_for(w, h, px, model, gr)
            diag = gr
        hard = r["v_half"] - occ
        judge = "✅ 结构成立" if hard >= TILT_BASELINE else "⚠️ 结构上几乎不成立"
        print(f"  {label:<48} {r['v_half']:>9.2f}° {hard:>13.2f}° {r['v_half'] - 25.0:>+11.2f}°  {judge}")
        print(f"  {'':<48} 对角 {diag:.2f}° | 水平 {r['h_fov']:.2f}° | 垂直 {r['v_fov']:.2f}° | "
              f"俯角 28° 余量 {r['v_half'] - 28.0:+.2f}° | 俯角 32° 余量 {r['v_half'] - 32.0:+.2f}°")
    print()
    print("  ★ 与上游口径不一致的 2 处 (已按本脚本口径重算, 需上游回写):")
    g = win_geom(1920, 1080, 1.998)
    f_eq = f_for(g["d"], 120.0, "equidistant")
    f_rt = f_for(g["d"], 120.0, "rectilinear")
    print(f"    ① ISS-138 路线 C 的 'f=1.2704mm' 是**直行**口径的焦距 (等距 120° 需 f={f_eq:.4f}mm);")
    print(f"       且该行的垂直半视场 29.53° 取自 OV04C10 **全幅** (1080p 裁切窗口应为 29.42°)")
    print(f"       ⇒ 三个数混了两个口径。★路线 C 已被 11-02 09:41 的 D 取代, 不追, 但下游别引用。")
    rC = row_for(1920, 1080, 1.998, "equidistant", 120)
    print(f"    ② ISS-138 路线 D 原写 '对角 116.75° / 垂直半 28.62°' = AR0234CS **裁到 1080p** 的数;")
    print(f"       现行定案是**整幅不裁剪** ⇒ 对角 120.00° / 垂直半 {row_for(1920,1200,3.0,'equidistant',120)['v_half']:.2f}° (见上表)")
    out["routeC_f"] = {"rectilinear": f_rt, "equidistant": f_eq, "routeC_v_half_correct": rC["v_half"]}

    print()
    print("=" * 100)
    print("§6  自检")
    print("=" * 100)
    # 现行定案路线 D 必须与 SW/tools/fov_scale_check.py 一致
    rD = row_for(1920, 1200, 3.000, "equidistant", 120)
    rec(abs(rD["v_half"] - 31.80) < 0.02 and abs(rD["h_half"] - 50.88) < 0.02 and abs(rD["f"] - 3.2432) < 0.001,
        f"现行定案 AR0234CS 整幅 等距 120°: f={rD['f']:.4f}mm / 水平半 {rD['h_half']:.2f}° / "
        f"垂直半 {rD['v_half']:.2f}° —— 与 SW fov_scale_check.py (31.80/50.88/f=3.2432) 一致 ✅")
    # hw-lead 的 lens_fov_basis 数值
    rec(abs(rD["f"] - 3.2432) < 0.001,
        "hw-lead 分片 sensor_lens_focal_equidistant=3.2432mm 与本脚本一致 ✅")
    # 旧基线全幅等距 120° 与 MECH §B5.2 (10-29) 表一致
    rA = row_for(2688, 1520, 1.998, "equidistant", 120)
    rec(abs(rA["v_half"] - 29.53) < 0.02,
        f"旧基线 OV04C10 整幅 等距 120°: 垂直半视场 {rA['v_half']:.2f}° (MECH §B5.2 = 29.53°) ✅")
    # 路线 B 必须掉出画面
    gB = win_geom(1920, 1080, 1.998)
    vB = D((gB["H"] / 2.0) / 2.9459)
    rec(vB - 25.0 < 0, f"路线B 俯角 25° 名义余量 {vB - 25.0:+.2f}° < 0 ⇒ 正前方掉出画面 ✅ (结构不成立)")
    # 现行定案: 俯角 25° 必须成立, 32° 必须掉出 (名义)
    rec(rD["v_half"] - 25.0 >= MARGIN_B,
        f"现行定案 俯角 25° 名义余量 {rD['v_half'] - 25.0:+.2f}° ≥ 判据B 4° ✅")
    rec(rD["v_half"] - 32.0 < 0,
        f"现行定案 俯角 32° 名义余量 {rD['v_half'] - 32.0:+.2f}° < 0 ⇒ 正前方掉出画面 ✅ (旧 20-32° 区间上段作废)")
    # 遮挡把 30° 推出去
    rec(rD["v_half"] - 30.0 - occ < 0,
        f"现行定案 俯角 30° 名义余量 {rD['v_half'] - 30.0:+.2f}° 但扣边框遮挡后 {rD['v_half'] - 30.0 - occ:+.2f}° "
        f"⇒ **正前方被镜框上沿遮掉** (旧表没算这一项)")
    # h_max 上界
    h25 = 35.0 * math.tan(R(TILT_BASELINE))
    rec(h25 < 20.0, f"俯角 {TILT_BASELINE:.0f}° 时 h_max(d=35) = {h25:.2f}mm < MECH 原上界 20mm ⇒ 镜框上沿要压")
    # 硬上限 (零余量) 是物理边界, 不是设计点 —— 设计点看判据B'
    hard_h35 = 35.0 * math.tan(R(rD["v_half"] - occ))
    b_eff_h35 = 35.0 * math.tan(R(rD["v_half"] - occ - MARGIN_B))
    rec(b_eff_h35 < 20.0,
        f"现行定案 判据B'(有效余量>=4°) 允许俯角 ≤{rD['v_half'] - occ - MARGIN_B:.2f}° ⇒ "
        f"h_max(d=35) = {b_eff_h35:.2f}mm < 旧 MECH 上界 20mm ✅")
    print(f"  ※ 硬上限(零余量) {rD['v_half'] - occ:.2f}° ⇒ h_max(d=35) = {hard_h35:.2f}mm, "
          f"比旧 MECH 上界 20mm 高 {hard_h35 - 20.0:.2f}mm ⇒ **零余量位置镜框上沿做不到**, "
          f"设计点必须留余量 (判据B' ⇒ {b_eff_h35:.2f}mm)")
    # 判据B' (有效余量 4°) 必须 >= 工程基线 25° —— 否则基线本身站不住
    b_eff_now = rD["v_half"] - occ - MARGIN_B
    rec(b_eff_now >= TILT_BASELINE,
        f"现行定案 判据B'(有效余量>=4°) 允许俯角 ≤{b_eff_now:.2f}° ≥ 基线 {TILT_BASELINE:.0f}° "
        f"⇒ 基线在遮挡后仍剩 {rD['v_half'] - TILT_BASELINE - occ:+.2f}° ✅")
    out["checks"] = {"routeD": rD, "routeB_v_half": vB, "old_v_half": rA["v_half"],
                     "hard_limit_deg": rD["v_half"] - occ, "B_eff": b_eff_now}

    print()
    print("=" * 100)
    print(f"判定: FAIL {len(FAIL)} | WARN {len(WARN)}")
    for f in FAIL:
        print("  FAIL:", f)
    for w in WARN:
        print("  WARN:", w)
    print("=" * 100)
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2, default=str))
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
