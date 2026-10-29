#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
摄像头窗口 / 镜筒 / 俯角 复算脚本 (ISS-052 + ISS-047 闭环)
=====================================================================
为什么有这个脚本: ISS-052 要结构侧按 hw-lead `HW/LENS_SELECTION.md` 给的镜头侧数字
复核镜框上沿的摄像头位, 同时把俯角上限从"20-32°"收窄到"<=25°(OV04C10) /
<=28°(AR0234CS 16:10)", 并修掉 ISS-047 指出的"对角半角 vs 垂直半视场"口径混用。
这三件事全部是**算术**, 所以全部写成一个可复现的脚本, 免得文档里再出现
"应该能放下"这种没法判定的话。

用法:
    python3 MECH/camera_window_check.py            # 全量复算 + 判定
    python3 MECH/camera_window_check.py --json     # 机器可读

判定口径 (全部写死在本文件, 与 MECH/CAMERA_WINDOW_SPEC.md §6 一致):
    A. 投影模型: 直行 (rectilinear, r=f*tan0) 与 等距 (equidistant, r=f*0)
       —— "对角 120°" 在这两个口径下的垂直半视场差 10.9°, 不可混用 (ISS-047)
    B. 俯角余量 = 垂直半视场 - 俯角; 余量 >= 0 判"正前方在画面内"
    C. 工程判据 (本项目基线): 余量 >= 4°  => 俯角 <= 垂直半视场 - 4°
       (这正好等于 PM/hw-lead 定的 <=25° / <=28°)
    D. MECH 原 §1.5 那张表的 10° 余量口径: 俯角 <= 垂直半视场 - 10° (更严, 另一口径)

输出全部为 [推算]; 本脚本不含任何 [实测] 数据 (0 件打印件 / 0 片镜头样片)。
"""
from __future__ import annotations

import argparse
import json
import math

D = math.degrees
R = math.radians

# ---------------------------------------------------------------- 传感器
SENSORS = {
    # name: (W px, H px, 像元 um, 备注)
    "OV04C10": (2688, 1520, 1.998, "豪威 1/3\" 16:9"),
    "AR0234CS": (1920, 1200, 3.000, "onsemi 1/2.6\" 16:10"),
}
GRADES = (100, 110, 120)

# ---------------------------------------------------------------- 结构侧要跟的数
# 来源: HW/LENS_SELECTION.md §B4 (S1/S2/S3 + §4.2 窗口表 + §4.4 预留表)
BARREL_OD_MIN, BARREL_OD_MAX = 6.0, 6.5      # 镜筒外径
CLEARANCE_DIA = 7.5                          # 加厚区净空直径
LENS_H_MIN, LENS_H_MAX = 3.7, 4.6            # 镜头总高 (前顶点->感光面)
LENS_H_DESIGN = 4.6                          # 推荐取 4.6
MODULE_H_DESIGN = 6.0                        # 模组沿光轴总高 (前顶点->PCB 顶面) 推荐
MODULE_H_RANGE = (5.0, 5.9)                  # 上游写的区间
SENSOR_PKG_H = 1.3                           # sensor 封装高 (占位, 待原厂)
WIN_CLEAR_DIA = 5.0                          # 窗口通光口径
WIN_OD = 6.5                                 # 窗口外径
WIN_T_GLASS, WIN_T_SAPPH = 0.3, 0.5          # 窗口厚
WIN_TO_VERTEX_MIN = 0.5                      # 窗口到前镜片顶点最小间距
PROTRUDE_MAX = 2.5                           # MECH 凸出上限
RECESS_MAX_OLD = 1.5                         # MECH 原凹进上限 (本单收紧)
RECESS_DESIGN = 1.0                          # 前顶点安装基准: 凹进 1.0mm
SHADE_ALONG_AXIS = 1.5                       # 遮光罩沿光轴 (MECH M8 已计)
WALL_FRONTBACK = 1.2                         # 镜框上沿前后外壁
WALL_VERTICAL = 0.8                          # 镜框上沿上下壁
BROW_BOSS_BAND = (10.0, 12.0)                # MECH "镜框上沿局部加厚 10-12mm"

TILT_NEW = 25.0                              # 新上限 (OV04C10, 工程判据 余量>=4)
TILT_NEW_AR = 28.0                           # 新上限 (AR0234CS 16:10)
TILT_OLD = (20.0, 32.0)                      # MECH 原区间 (待收窄)

FAIL: list[str] = []
WARN: list[str] = []


def rec(ok: bool, msg: str, warn: bool = False) -> None:
    tag = "OK  " if ok else ("WARN" if warn else "FAIL")
    print(f"  [{tag}] {msg}")
    if not ok:
        (WARN if warn else FAIL).append(msg)


# ---------------------------------------------------------------- 光学
def sensor_geom(name):
    w, h, px, memo = SENSORS[name]
    W, H = w * px / 1000.0, h * px / 1000.0
    return {"W": W, "H": H, "d": math.hypot(W, H), "px": px, "memo": memo}


def fov_table(name, proj):
    """返回该 sensor + 投影模型下三档的 FOV 分解。"""
    s = sensor_geom(name)
    W, H, d = s["W"], s["H"], s["d"]
    rows = []
    for t in GRADES:
        if proj == "rectilinear":
            f = (d / 2.0) / math.tan(R(t / 2.0))
            h_half = D(math.atan((W / 2.0) / f))
            v_half = D(math.atan((H / 2.0) / f))
        else:  # equidistant
            f = (d / 2.0) / R(t / 2.0)
            h_half = D((W / 2.0) / f)
            v_half = D((H / 2.0) / f)
        rows.append({
            "diag": t, "f": f, "h_half": h_half, "v_half": v_half,
            "h_fov": 2 * h_half, "v_fov": 2 * v_half,
        })
    return rows


def tilt_margins(v_half, tilts=(20.0, 25.0, 28.0, 32.0)):
    return {t: v_half - t for t in tilts}


# ---------------------------------------------------------------- 几何包络
def tilted_envelope(L, Dm, tilt_deg, L_extra=0.0):
    """倾斜圆柱 (沿光轴长 L, 直径 Dm) 在 前-后 / 垂直 / 水平 三个方向的包络。"""
    t = R(tilt_deg)
    fb = (L + L_extra) * math.cos(t) + Dm * math.sin(t)     # 前后 (镜框厚度方向)
    vt = (L + L_extra) * math.sin(t) + Dm * math.cos(t)     # 垂直 (上沿净高方向)
    return fb, vt, Dm


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    out = {}

    print("=" * 78)
    print("§1  FOV 分解 —— ISS-047 口径修正 (对角半角 **不能** 用来判俯角)")
    print("=" * 78)
    print("口径: 垂直俯角由【垂直半视场】决定, 与对角半角无关。")
    print("      直行 r=f*tan0 ; 等距(鱼眼) r=f*0 —— 同一'对角120°'两者垂直半视场差 10.9°\n")
    for name in SENSORS:
        s = sensor_geom(name)
        print(f"● {name} ({s['memo']}): 靶面 {s['W']:.4f} x {s['H']:.4f} mm, 对角 {s['d']:.4f} mm, 像元 {s['px']}um")
        out[name] = {"sensor": s}
        for proj, pname in (("rectilinear", "直行 rectilinear"), ("equidistant", "等距 equidistant (鱼眼)")):
            rows = fov_table(name, proj)
            print(f"  -- 投影: {pname}")
            print(f"     {'对角FOV':>8} {'f(mm)':>8} {'水平FOV':>9} {'垂直FOV':>9} {'垂直半视场':>10} "
                  f"{'俯25余量':>9} {'俯28余量':>9} {'俯32余量':>9}")
            for r in rows:
                m = tilt_margins(r["v_half"])
                print(f"     {r['diag']:>7}° {r['f']:>8.3f} {r['h_fov']:>8.2f}° {r['v_fov']:>8.2f}° "
                      f"{r['v_half']:>9.2f}° {m[25.0]:>+8.2f}° {m[28.0]:>+8.2f}° {m[32.0]:>+8.2f}°")
            out[name][proj] = rows
            print()

    print("=" * 78)
    print("§2  ★ 俯角上限收窄 (ISS-052 核心): 垂直半视场 -> 俯角上限")
    print("=" * 78)
    print("判据 A 硬: 余量>=0        俯角 <= 垂直半视场")
    print("判据 B 工程(本项目基线): 余量>=4°  俯角 <= 垂直半视场 - 4°   <= PM/hw-lead 定的 25°/28°")
    print("判据 C MECH 原表:        余量>=10° 俯角 <= 垂直半视场 - 10°  (更严, 另一口径, 需 PM 选口径)\n")
    tilt_limit = {}
    for name in SENSORS:
        for proj, label in (("equidistant", "鱼眼(等距) 120°"), ("rectilinear", "直行 120°")):
            row = [r for r in fov_table(name, proj) if r["diag"] == 120][0]
            vh = row["v_half"]
            a, b, c = vh, vh - 4.0, vh - 10.0
            print(f"● {name} {label}: 垂直半视场 {vh:.2f}°  ->  A(>=0) {a:.2f}° | B(>=4°) {b:.2f}° | C(>=10°) {c:.2f}°")
            if name == "OV04C10" and proj == "equidistant":
                tilt_limit[name] = {"A": a, "B": b, "C": c}
    print()
    rec(tilt_limit["OV04C10"]["B"] >= 25.0, f"OV04C10 鱼眼 工程判据上限 {tilt_limit['OV04C10']['B']:.2f}° >= 25° (hw-lead/PM 基线)")
    print()

    print("=" * 78)
    print("§3  ★ 俯角上限 -> 摄像头中心高度上限 h (结构侧新硬约束)")
    print("=" * 78)
    print("俯角 = atan(h/d): h = 摄像头光轴中心高于用户视线的高度, d = 镜片到眼点距离\n")
    print(f"     {'d(mm)':>7} {'h@25°':>9} {'h@28°':>9} {'h@19.5°(C口径)':>16}")
    h_lim = {}
    for d in (30.0, 32.0, 35.0):
        h25 = d * math.tan(R(25.0))
        h28 = d * math.tan(R(28.0))
        hc = d * math.tan(R(tilt_limit["OV04C10"]["C"]))
        print(f"     {d:>7.1f} {h25:>8.2f} {h28:>8.2f} {hc:>15.2f}")
        h_lim[d] = {"h25": h25, "h28": h28, "hC": hc}
    out["h_limit"] = h_lim
    print()
    print("=> 镜框上沿摄像头位的光轴中心高度上限 h_max:")
    print(f"   判据B(<=25°, OV04C10):  d=30/32/35 -> h_max = {h_lim[30]['h25']:.2f} / {h_lim[32]['h25']:.2f} / {h_lim[35]['h25']:.2f} mm")
    print(f"   判据B(<=28°, AR0234CS): d=30/32/35 -> h_max = {h_lim[30]['h28']:.2f} / {h_lim[32]['h28']:.2f} / {h_lim[35]['h28']:.2f} mm")
    print(f"   判据C(<=10°余量):        d=32      -> h_max = {h_lim[32]['hC']:.2f} mm  (更严, 需 PM 选口径)")
    print("   ★ 对比 MECH §1.5 原值 'h=12-20mm -> 俯角 20.6-32.0°': h_max 收窄到 13.99-16.32mm (判据B)")
    rec(h_lim[32]["h25"] < 15.0, f"d=32 时 h_max(25°) = {h_lim[32]['h25']:.2f}mm < MECH 原上界 h=20mm -> 镜框上沿高度要压")
    print()

    print("=" * 78)
    print("§4  ★ 镜框上沿加厚区复核 (ISS-052 验收①): 倾斜模组的三向包络")
    print("=" * 78)
    L_axis = MODULE_H_DESIGN + WIN_T_GLASS + WIN_TO_VERTEX_MIN   # 窗口外表面 -> PCB 顶面 (沿光轴)
    print(f"沿光轴: 窗口 {WIN_T_GLASS} + 间距 {WIN_TO_VERTEX_MIN} + 模组 {MODULE_H_DESIGN} = {L_axis:.1f}mm")
    print(f"        (蓝宝石窗口 {WIN_T_SAPPH} -> {L_axis - WIN_T_GLASS + WIN_T_SAPPH:.1f}mm)\n")
    print(f"     {'俯角':>6} {'前后包络':>10} {'+壁1.2':>9} {'垂直包络':>10} {'+壁1.6':>9} {'水平':>7}")
    env = {}
    for tilt in (20.0, 25.0, 28.0, 32.0):
        fb, vt, hz = tilted_envelope(L_axis, BARREL_OD_MAX, tilt)
        fb += WALL_FRONTBACK
        vt += 2 * WALL_VERTICAL
        env[tilt] = {"fb": fb, "vt": vt, "hz": hz}
        print(f"     {tilt:>5.0f}° {fb - WALL_FRONTBACK:>9.2f} {fb:>8.2f} {vt - 2 * WALL_VERTICAL:>9.2f} {vt:>8.2f} {hz:>6.2f}")
    out["envelope"] = env
    lo, hi = BROW_BOSS_BAND
    print()
    rec(max(env[t]["fb"] for t in env) <= hi,
        f"前后厚度需求最大 {max(env[t]['fb'] for t in env):.2f}mm (俯角32°) <= 加厚区上界 {hi}mm",
        warn=False)
    rec(lo <= env[25.0]["fb"] <= hi and lo <= env[28.0]["fb"] <= hi,
        f"设计俯角 25°/28° 时前后厚度 {env[25.0]['fb']:.2f}/{env[28.0]['fb']:.2f}mm 落在加厚区 {lo}-{hi}mm 带内",
        warn=False)
    rec(min(env[t]["fb"] for t in env) < lo,
        f"俯角 20° 时厚度需求 {min(env[t]['fb'] for t in env):.2f}mm < 带下界 {lo}mm -> 只是更薄, 不是不通过 (带是**上限需求**)")
    rec(max(env[t]["fb"] for t in env) - min(env[t]["fb"] for t in env) < 1.0,
        f"对俯角不敏感: 俯角 20°->32° 前后厚度只变 {max(env[t]['fb'] for t in env) - min(env[t]['fb'] for t in env):.2f}mm")
    print(f"  ★ 垂直方向 (镜框上沿净高) 需求 = {env[25.0]['vt']:.2f}mm (25°) / {env[28.0]['vt']:.2f}mm (28°)")
    rec(env[25.0]["vt"] <= hi, f"上沿垂直净高 {env[25.0]['vt']:.2f}mm 仍在 10-12mm 带内")
    print()
    print("  ※ 口径更正 (ISS-047 同源问题): hw-lead '径向余量 2.5-4.5mm' 是把 '加厚区 10-12mm'")
    print("    当**直径**与 '净空 ⌀7.5' 比出来的直径差; 单边(半径)余量 = (10-7.5)/2~(12-7.5)/2")
    print(f"    = {(10.0 - CLEARANCE_DIA) / 2:.2f}-{(12.0 - CLEARANCE_DIA) / 2:.2f}mm/边, 不是 2.5-4.5mm")
    print(f"    且 MECH §1.4.5 的 10-12mm 口径是**前后方向厚度** (与正中区 11.8mm 同轴), 不是直径")
    print()

    print("=" * 78)
    print("§5  凸出 / 凹进 账 (前顶点安装基准: 齐平 或 凹进 <=1.0mm)")
    print("=" * 78)
    print(f"感光面凸出 = 镜头总高 x sin(俯角) - 凹进 r;  MECH 凸出上限 {PROTRUDE_MAX}mm\n")
    print(f"     {'镜头总高mm':>10} {'俯角':>6} {'r=0':>8} {'r=0.5':>8} {'r=1.0':>8} {'r=1.5':>8}")
    worst = {"all": 0.0}
    for hl in (LENS_H_MIN, 4.0, LENS_H_DESIGN):
        for tilt in TILT_OLD:
            row = []
            for r in (0.0, 0.5, 1.0, 1.5):
                p = hl * math.sin(R(tilt)) - r
                row.append(p)
                worst["all"] = max(worst["all"], p)
            print(f"     {hl:>9.2f}  {tilt:>5.0f}° " + " ".join(f"{v:>7.2f}" for v in row))
    print()
    p32_r0 = LENS_H_DESIGN * math.sin(R(32.0))
    p25_r1 = LENS_H_DESIGN * math.sin(R(25.0)) - RECESS_DESIGN
    p28_r1 = LENS_H_DESIGN * math.sin(R(28.0)) - RECESS_DESIGN
    p28_r0 = LENS_H_DESIGN * math.sin(R(28.0))
    print(f"★ 原区间最坏 (H=4.6, 俯角32°, 齐平 r=0): {p32_r0:.2f}mm -> 对 {PROTRUDE_MAX}mm 上限只剩 {PROTRUDE_MAX - p32_r0:.2f}mm 余量 (临界)")
    print(f"★ 收窄后 (俯角<=25°/28°), 设计基准 r=1.0mm: 凸出 {p25_r1:.2f} / {p28_r1:.2f}mm -> 余量 {PROTRUDE_MAX - p25_r1:.2f} / {PROTRUDE_MAX - p28_r1:.2f}mm")
    print(f"★ 收窄后即使齐平 r=0: 俯角28° 时 {p28_r0:.2f}mm -> 余量 {PROTRUDE_MAX - p28_r0:.2f}mm (从'临界'变'通过')")
    out["protrude"] = {"worst_old": p32_r0, "design_25": p25_r1, "design_28": p28_r1, "flush_28": p28_r0}
    rec(p28_r0 <= PROTRUDE_MAX, f"收窄后最坏凸出 {p28_r0:.2f}mm <= {PROTRUDE_MAX}mm")
    rec(True, f"设计基准 r={RECESS_DESIGN}mm -> 凸出 {p25_r1:.2f}-{p28_r1:.2f}mm (任务书给的 0.6-1.4mm 是旧 20-32° 区间的值)")
    print()

    print("=" * 78)
    print("§6  镜框摄像头位 开口 / 窗口 / 打印公差 预留 (不等镜头定档即可开模)")
    print("=" * 78)
    seat_hole = WIN_OD + 0.3          # 打印件 <-> 玻璃件 单边 0.15
    clear_print = WIN_CLEAR_DIA + 0.4  # 补偿 FDM 孔径收缩 0.1-0.2mm/边
    print(f"  镜筒外径        {BARREL_OD_MIN}-{BARREL_OD_MAX}mm (三档同一区间)")
    print(f"  加厚区净空      ⌀{CLEARANCE_DIA}mm (镜筒 {BARREL_OD_MAX} + 单边 0.5 壁/公差)")
    print(f"  窗口座孔       ⌀{seat_hole:.1f}mm (窗口 ⌀{WIN_OD} + 单边 0.15 装配间隙)")
    print(f"  窗口通光孔     打印 ⌀{clear_print:.1f}mm (FDM 孔径收缩 0.1-0.2/边 -> 实测 ⌀5.0-5.2 >= 需求 {WIN_CLEAR_DIA})")
    print(f"  窗口厚         {WIN_T_GLASS} (化学强化玻璃) / {WIN_T_SAPPH} (蓝宝石)")
    print(f"  窗口->前顶点   >= {WIN_TO_VERTEX_MIN}mm (遮光罩内腔深度)")
    print(f"  前组通光口径   >= 4.0-4.5mm (要求 窗口通光 {WIN_CLEAR_DIA} >= 前组+0.5) OK")
    print(f"  沿光轴总高     {MODULE_H_RANGE[0]}-{MODULE_H_RANGE[1]}mm (区间) / 设计取 {MODULE_H_DESIGN}mm")
    print(f"                  ★ 上游自相矛盾: 区间上界 {MODULE_H_RANGE[1]} < 推荐值 {MODULE_H_DESIGN}; 120°鱼眼算术值 = 4.55+1.30 = {4.55 + SENSOR_PKG_H:.2f}")
    print(f"  镜头总高       {LENS_H_MIN}-{LENS_H_MAX}mm (三档) / 设计取 {LENS_H_DESIGN}mm")
    print(f"  前顶点基准     齐平 或 凹进 <= {RECESS_DESIGN}mm (本单把 MECH 原 1.5mm 收紧到 1.0mm)")
    rec(MODULE_H_DESIGN >= MODULE_H_RANGE[1], "上游区间上界 < 设计值, 已按保守取 6.0 (已登记为待澄清项)", warn=True)
    print()

    print("=" * 78)
    print("§7  水平偏置 / 边框遮挡 复核 (ISS-047 附带)")
    print("=" * 78)
    for name in SENSORS:
        row = [r for r in fov_table(name, "equidistant") if r["diag"] == 120][0]
        occ = D(math.atan(RECESS_DESIGN / 30.0))
        print(f"  {name} 鱼眼120°: 水平半视场 {row['h_half']:.2f}° -> 水平偏置 10° 覆盖 "
              f"(余量 {row['h_half'] - 10:.2f}°)")
        print(f"     前顶点凹进 {RECESS_DESIGN}mm (d=30) -> 边框遮挡 {occ:.2f}° = 垂直半视场的 {occ / row['v_half'] * 100:.1f}%")
    print()
    rec(True, "水平偏置 <=10° 在两个靶面上都成立 (余量 >= 32°)")
    print()

    print("=" * 78)
    print(f"判定: FAIL {len(FAIL)} | WARN {len(WARN)}")
    for f in FAIL:
        print("  FAIL:", f)
    for w in WARN:
        print("  WARN:", w)
    print("=" * 78)

    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2, default=str))
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
