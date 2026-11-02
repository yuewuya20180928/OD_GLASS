#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-047 复核脚本 —— 「对角半角」不能用来判垂直俯角
=====================================================================
为什么有这个脚本:
    老板 2026-10-25 基线里, 结构侧 MECH §1.5 拿「半对角 50°/60°」减俯角再减
    10° 余量, 推出「可接受最大偏置 ≤40°/≤50°」, 并把 **垂直俯角** 和
    **水平偏置** 混在一张表里。hw-lead 指出: **垂直俯角只能由垂直半视场决定**
    (16:9 对角 100° → 垂直半视场只有 30.30°, 不是 50°)。
    另一条同样重要: **「对角 120°」不是一个自洽的数** —— 直行 (r=f·tanθ) 与
    等距/鱼眼 (r=f·θ) 差 10.9° 的垂直半视场。

本脚本做四件事 (全部可复现, 无外部依赖, 无实测数据):
    §1 口径核验: 复现 hw-lead 的「16:9 对角 100° → 垂直半视场 30.30°」,
       并证明「半对角 50° − 俯角 − 余量 10° → ≤40°」不成立。
    §2 完整五数对应表: 对角FOV / 水平FOV / 垂直FOV / 垂直半视场 / 俯角余量,
       覆盖 4 种读出窗口 × 2 种投影模型 × 3 档对角 FOV, 每个俯角标注
       「正前方是否在画面内」。
    §3 俯角上限 → 结构高度 h_max (d = 30/32/35mm), 三档判据 A/B/C。
    §4 路线映射: ISS-138 的 A/B/C/D 四条路线 → 结构侧俯角上限与 h_max,
       并标出 hw-lead 路线 C 那一行的口径不一致。

投影模型:
    直行 (rectilinear): r = f·tanθ      → θ = atan(r/f)
    等距 (equidistant/鱼眼): r = f·θ     → θ = r/f
俯角余量:
    margin = 垂直半视场 − 俯角; margin ≥ 0 ⇒ 正前方在画面内。
    有效余量 = margin − 边框遮挡角 (前顶点凹进 1.0mm @ d=30 → 1.91°, 沿用
    MECH §1.5.1 口径; 该遮挡吃的是**上半视场**, 正好是「正前方」那一侧)。

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

# ------------------------------------------------------------------ 传感器
# name: (宽px, 高px, 像元µm, 备注)
WINDOWS = {
    "OV04C10 全幅 2688x1520": (2688, 1520, 1.998, "16:9 (1.7684), 旧基线: 老板 11-02 定 1080p60 直出后**不再是工作模式**"),
    "OV04C10 1080p 1920x1080": (1920, 1080, 1.998, "16:9 (1.7778), ★**老板 11-02 02:04 定的工作模式** (全幅裁切, 像元距不变)"),
    "AR0234CS 全幅 1920x1200": (1920, 1200, 3.000, "16:10 (1.6), 原生态"),
    "AR0234CS 1080p 1920x1080": (1920, 1080, 3.000, "16:9, ISS-138 路线 D 的裁高取图"),
}
GRADES = (100, 110, 120)
MODELS = (("rectilinear", "直行 r=f·tanθ"), ("equidistant", "等距(鱼眼) r=f·θ"))
TILTS = (15.0, 20.0, 25.0, 28.0, 30.0, 32.0)

# ------------------------------------------------------------------ 结构侧常数
D_EYE = (30.0, 32.0, 35.0)     # 镜片到眼点距离 d (mm)
RECESS_DESIGN = 1.0            # 前镜片顶点相对镜框上沿外表面凹进 (mm), MECH §1.5.2
MARGIN_A, MARGIN_B, MARGIN_C = 0.0, 4.0, 10.0   # 三档余量判据 (度)

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
    """边框遮挡角 (吃掉上半视场)。沿用 MECH §1.5.1 口径: atan(凹进/d)。"""
    return D(math.atan(recess / d))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    out = {}
    occ = occlusion_deg()

    print("=" * 96)
    print("§1  口径核验: 「半对角 50°」能不能用来判垂直俯角?")
    print("=" * 96)
    # 16:9 理想比例, 对角 100°, 直行
    ar = 16.0 / 9.0
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
    print("  ★ 顺带: 旧表把「垂直俯角」和「水平偏置」放同一列比 —— 二者由不同量决定")
    print("    (垂直俯角 → 垂直半视场; 水平偏置 → 水平半视场), 物理上不可互换。")
    out["calib_16x9_100"] = {"h_half": h16, "v_half": v16}

    print()
    print("=" * 96)
    print("§2  ★ 完整五数对应表 (对角FOV / 水平FOV / 垂直FOV / 垂直半视场 / 俯角余量)")
    print("=" * 96)
    print("  口径: 镜头按**读出窗口**的对角线设计到目标对角 FOV; 俯角余量 = 垂直半视场 − 俯角;")
    print("        余量 < 0 ⇒ 正前方**掉出画面**; 括号内 = 扣掉边框遮挡 %.2f° 后的有效余量。" % occ)
    print()
    tbl = {}
    for wname, (w, h, px, memo) in WINDOWS.items():
        g = win_geom(w, h, px)
        print(f"● {wname}  —— 读出窗口 {w}x{h}px @ {px}µm = {g['W']:.4f} x {g['H']:.4f}mm, "
              f"对角 {g['d']:.4f}mm  [{memo}]")
        for model, mname in MODELS:
            print(f"  -- 投影模型: {mname}")
            print(f"     {'对角FOV':>7} {'f(mm)':>7} {'水平FOV':>9} {'垂直FOV':>9} {'垂直半视场':>10} "
                  f"{'水平半视场':>10} {'偏置10°余量':>11}")
            for gr in GRADES:
                r = row_for(w, h, px, model, gr)
                print(f"     {gr:>6}° {r['f']:>7.3f} {r['h_fov']:>8.2f}° {r['v_fov']:>8.2f}° "
                      f"{r['v_half']:>9.2f}° {r['h_half']:>9.2f}° {r['h_half'] - 10.0:>+10.2f}°")
            print()
            # 俯角余量 + 正前方是否在画面内
            print(f"     {'对角FOV':>7} {'垂直半视场':>10}  " +
                  "  ".join(f"{'俯%g°' % t:>14}" for t in TILTS))
            for gr in GRADES:
                r = row_for(w, h, px, model, gr)
                cells = []
                for t in TILTS:
                    m = r["v_half"] - t
                    me = m - occ
                    tag = "在画面内" if me >= 0 else ("临界" if m >= 0 else "掉出")
                    cells.append(f"{m:>+7.2f} {tag:<6}")
                print(f"     {gr:>6}° {r['v_half']:>9.2f}°  " + "  ".join(cells))
            print()
            tbl.setdefault(wname, {})[model] = [row_for(w, h, px, model, gr) for gr in GRADES]
    out["table"] = tbl

    print("=" * 96)
    print("§3  俯角上限 → 结构侧硬约束: 摄像头光轴中心高于用户视线的高度 h_max")
    print("=" * 96)
    print("  俯角 = atan(h/d) ⇒ h_max = d · tan(俯角上限); d = 镜片到眼点距离\n")
    key = {
        "路线C 等距 120° (OV04C10 1080p)": ("OV04C10 1080p 1920x1080", "equidistant", 120),
        "路线D 等距 (AR0234CS 1080p 裁高)": ("AR0234CS 1080p 1920x1080", "equidistant", 120),
        "旧基线 等距 120° (OV04C10 全幅)": ("OV04C10 全幅 2688x1520", "equidistant", 120),
    }
    lim = {}
    for label, (wname, model, gr) in key.items():
        w, h, px, _ = WINDOWS[wname]
        r = row_for(w, h, px, model, gr)
        vh = r["v_half"]
        a, b, c = vh, vh - MARGIN_B, vh - MARGIN_C
        print(f"● {label}: 垂直半视场 {vh:.2f}°  ⇒ 判据A(余量0) ≤{a:.2f}° | "
              f"B(余量4°) ≤{b:.2f}° | C(余量10°) ≤{c:.2f}°")
        for d in D_EYE:
            print(f"      d={d:>4.1f}mm → h_max(A) {d * math.tan(R(a)):>6.2f} | "
                  f"h_max(B) {d * math.tan(R(b)):>6.2f} | h_max(C) {d * math.tan(R(c)):>6.2f} mm")
        lim[label] = {"v_half": vh, "A": a, "B": b, "C": c}
        print()
    out["tilt_limits"] = lim

    print("=" * 96)
    print("§4  路线映射 (ISS-138): 四条路线 → 结构侧结论")
    print("=" * 96)
    routes = {
        "A. OV04C10 全幅 2688x1520@60 + 鱼眼 f=2.9459 (旧基线)": ("OV04C10 全幅 2688x1520", "equidistant", 120),
        "B. OV04C10 1080p60 + 同一颗镜头 f=2.9459": ("OV04C10 1080p 1920x1080", "equidistant", None),
        "C. OV04C10 1080p60 + 镜头改短 (保住 120°)": ("OV04C10 1080p 1920x1080", "equidistant", 120),
        "D. AR0234CS 1920x1200@60 + 裁高到 1080": ("AR0234CS 1080p 1920x1080", "equidistant", 120),
    }
    print(f"  {'路线':<46} {'垂直半视场':>10} {'俯角上限(B)':>12} {'h_max@32mm':>12}  结构侧判定")
    for label, (wname, model, gr) in routes.items():
        w, h, px, _ = WINDOWS[wname]
        if gr is None:  # 路线 B: 镜头不变 (f 固定), FOV 由读出窗口裁切决定
            g = win_geom(w, h, px)
            f_fixed = 2.9459  # 旧基线镜头
            v_half = D((g["H"] / 2.0) / f_fixed)
            v_fov = 2 * v_half
            h_half = D((g["W"] / 2.0) / f_fixed)
            diag = 2 * D(math.hypot(g["W"] / 2.0, g["H"] / 2.0) / f_fixed)
            r = {"v_half": v_half, "v_fov": v_fov, "h_fov": 2 * h_half, "h_half": h_half,
                 "f": f_fixed, "d": g["d"]}
        else:
            r = row_for(w, h, px, model, gr)
            diag = gr
        b = r["v_half"] - MARGIN_B
        hmax = 32.0 * math.tan(R(b))
        judge = "✅ 结构成立" if b >= 20.0 else "⚠️ 结构上几乎不成立"
        print(f"  {label:<46} {r['v_half']:>9.2f}° {b:>11.2f}° {hmax:>11.2f}mm  {judge}")
        print(f"  {'':<46} 对角 {diag:.2f}° | 水平 {r['h_fov']:.2f}° | 垂直 {r['v_fov']:.2f}° | "
              f"俯角 25° 余量 {r['v_half'] - 25.0:+.2f}° | 俯角 28° 余量 {r['v_half'] - 28.0:+.2f}°")
    print()
    print("  ★ 口径提示 (ISS-138 路线 C 那一行): 「f=1.2704mm」是**直行**口径算出来的焦距")
    g = win_geom(1920, 1080, 1.998)
    f_eq = f_for(g["d"], 120.0, "equidistant")
    f_rt = f_for(g["d"], 120.0, "rectilinear")
    print(f"    (OV04C10 1080p 窗口对角 {g['d']:.4f}mm): 直行 120° → f={f_rt:.4f}mm; "
          f"等距 120° → f={f_eq:.4f}mm")
    print(f"    ⇒ 两者差 {f_eq - f_rt:.4f}mm; **f=1.2704mm 只能是直行口径**。若把它当等距镜头")
    print(f"      用, 实际对角 FOV 会是 {2 * D(math.hypot(g['W'] / 2.0, g['H'] / 2.0) / f_rt):.1f}° (不是 120°)。")
    print("    ⇒ 结构侧只按「投影模型 + 读出窗口 + 对角 FOV」三个量取数, 不引用单点焦距。")
    rec(abs(f_rt - 1.2704) < 0.01,
        f"核实: 路线 C 的 f=1.2704mm = 直行口径 ({f_rt:.4f}mm) ✅ 一致 ⇒ 该行需补投影模型标注")
    out["routeC_f"] = {"rectilinear": f_rt, "equidistant": f_eq}

    print()
    print("=" * 96)
    print("§5  自检")
    print("=" * 96)
    # 路线 D 的关键数必须与 SW/tools/fov_scale_check.py 一致 (116.75 / 28.62 / 50.88)
    rD = row_for(1920, 1080, 3.000, "equidistant", 120)
    diagD = 2 * D(math.hypot(2.88, 1.62) / f_for(rD["d"], 120.0, "equidistant"))
    rec(abs(rD["v_half"] - 28.62) < 0.02 and abs(rD["h_half"] - 50.88) < 0.02 and abs(diagD - 116.75) < 0.05,
        f"路线D 与 SW fov_scale_check.py 一致: 对角 {diagD:.2f}° / 垂直半 {rD['v_half']:.2f}° / 水平半 {rD['h_half']:.2f}°")
    # 旧基线全幅等距 120° 与 MECH §B5.2 表一致
    rA = row_for(2688, 1520, 1.998, "equidistant", 120)
    rec(abs(rA["v_half"] - 29.53) < 0.02,
        f"旧基线 OV04C10 全幅 等距 120°: 垂直半视场 {rA['v_half']:.2f}° (MECH §B5.2 = 29.53°) ✅")
    # 路线 B 必须掉出画面
    gB = win_geom(1920, 1080, 1.998)
    vB = D((gB["H"] / 2.0) / 2.9459)
    rec(vB - 25.0 < 0, f"路线B 俯角 25° 余量 {vB - 25.0:+.2f}° < 0 ⇒ 正前方掉出画面 ✅ (结构不成立)")
    # 路线 C 俯角 25° 必须成立
    rC = row_for(1920, 1080, 1.998, "equidistant", 120)
    rec(rC["v_half"] - 25.0 >= MARGIN_B,
        f"路线C 俯角 25° 余量 {rC['v_half'] - 25.0:+.2f}° ≥ 判据B 4° ✅")
    rec(rD["v_half"] - 25.0 < MARGIN_B,
        f"路线D 俯角 25° 余量 {rD['v_half'] - 25.0:+.2f}° **< 判据B 4°** ⇒ 俯角上限要压到 {rD['v_half'] - MARGIN_B:.2f}°")
    # 旧基线 h_max 上界
    h25 = 35.0 * math.tan(R(25.0))
    rec(h25 < 20.0, f"俯角 25° 时 h_max(d=35) = {h25:.2f}mm < MECH 原上界 20mm ⇒ 镜框上沿要压")
    out["checks"] = {"routeD_diag": diagD, "routeD_v_half": rD["v_half"],
                     "routeB_v_half": vB, "routeC_v_half": rC["v_half"]}

    print()
    print("=" * 96)
    print(f"判定: FAIL {len(FAIL)} | WARN {len(WARN)}")
    for f in FAIL:
        print("  FAIL:", f)
    for w in WARN:
        print("  WARN:", w)
    print("=" * 96)
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2, default=str))
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
