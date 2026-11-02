#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-047 文档一致性检查 —— MECH/ISS047_FOV_TABLE.md 的每个数 vs MECH/iss047_fov_table.py
=====================================================================
为什么有这个脚本: 本项目的规矩是「数字不许靠人眼核对」。ISS-047 的交付物是一张
**有 100 多个数的表**, 所以必须有一条命令能复算并确认文档里的数与脚本一致。

做法: 把文档里的关键数抽成 (标签, 期望值) 清单, 现场重算, 逐条比。
任何一条对不上 ⇒ rc=1。

用法:
    python3 MECH/iss047_doc_check.py          # rc=0 = 文档与脚本一致
    python3 MECH/iss047_doc_check.py --show   # 打印每一条的比对过程

退出码: 0 = 全部一致 / 1 = 有不一致 / 2 = 文档缺文件
"""
from __future__ import annotations

import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DOC = os.path.join(HERE, "ISS047_FOV_TABLE.md")

D = math.degrees
R = math.radians

OCC = D(math.atan(1.0 / 30.0))       # 边框遮挡角 (凹进 1.0mm @ d=30)


def win(w, h, px):
    W, H = w * px / 1000.0, h * px / 1000.0
    return W, H, math.hypot(W, H)


def row(w, h, px, model, grade):
    W, H, d = win(w, h, px)
    half = R(grade / 2.0)
    f = (d / 2.0) / (math.tan(half) if model == "rectilinear" else half)
    if model == "rectilinear":
        hh = D(math.atan((W / 2.0) / f))
        vh = D(math.atan((H / 2.0) / f))
    else:
        hh = D((W / 2.0) / f)
        vh = D((H / 2.0) / f)
    return {"f": f, "h_fov": 2 * hh, "h_half": hh, "v_fov": 2 * vh, "v_half": vh}


# (标签, 实测值, 文档里写的值, 容差)
CHECKS: list[tuple[str, float, float, float]] = []


def add(label, got, want, tol=0.011):
    CHECKS.append((label, got, want, tol))


# ---------------------------------------------------------------- §1 口径核验
f16 = (math.hypot(16.0, 9.0) / 2.0) / math.tan(R(50.0))
add("16:9 对角100° 垂直半视场", D(math.atan(4.5 / f16)), 30.30)
add("16:9 对角100° 水平半视场", D(math.atan(8.0 / f16)), 46.09)
add("旧结论40° 高估量", 40.0 - D(math.atan(4.5 / f16)), 9.70)
add("对角半角50° vs 垂直半视场 差", 50.0 - D(math.atan(4.5 / f16)), 19.70)

# ---------------------------------------------------------------- §B3.1 现行定案
AR = (1920, 1200, 3.000)
for grade, fh, hv, fv, vh, hh in (
        (100, 2.850, 90.60, 64.56, 32.28, 45.30),
        (110, 2.378, 100.91, 74.25, 37.12, 50.45),
        (120, 1.961, 111.50, 85.10, 42.55, 55.75)):
    r = row(*AR, "rectilinear", grade)
    add(f"AR整幅 直行{grade}° f", r["f"], fh)
    add(f"AR整幅 直行{grade}° 水平FOV", r["h_fov"], hv)
    add(f"AR整幅 直行{grade}° 垂直FOV", r["v_fov"], fv)
    add(f"AR整幅 直行{grade}° 垂直半视场", r["v_half"], vh)
    add(f"AR整幅 直行{grade}° 水平半视场", r["h_half"], hh)
for grade, fh, hv, fv, vh, hh in (
        (100, 3.892, 84.80, 53.00, 26.50, 42.40),
        (110, 3.538, 93.28, 58.30, 29.15, 46.64),
        (120, 3.243, 101.76, 63.60, 31.80, 50.88)):
    r = row(*AR, "equidistant", grade)
    add(f"AR整幅 等距{grade}° f", r["f"], fh)
    add(f"AR整幅 等距{grade}° 水平FOV", r["h_fov"], hv)
    add(f"AR整幅 等距{grade}° 垂直FOV", r["v_fov"], fv)
    add(f"AR整幅 等距{grade}° 垂直半视场", r["v_half"], vh)
    add(f"AR整幅 等距{grade}° 水平半视场", r["h_half"], hh)

# §B3.1 俯角余量表 (等距, 现行定案): 名义/有效
for grade, vh_doc, cells in (
        (100, 26.50, [(11.50, 9.59), (6.50, 4.59), (1.50, -0.41), (-1.50, -3.41),
                      (-3.50, -5.41), (-5.50, -7.41)]),
        (110, 29.15, [(14.15, 12.24), (9.15, 7.24), (4.15, 2.24), (1.15, -0.76),
                      (-0.85, -2.76), (-2.85, -4.76)]),
        (120, 31.80, [(16.80, 14.89), (11.80, 9.89), (6.80, 4.89), (3.80, 1.89),
                      (1.80, -0.11), (-0.20, -2.11)])):
    r = row(*AR, "equidistant", grade)
    add(f"AR整幅 等距{grade}° 垂直半视场(余量表)", r["v_half"], vh_doc)
    for i, (t, (mn, me)) in enumerate(zip((15.0, 20.0, 25.0, 28.0, 30.0, 32.0), cells)):
        add(f"AR整幅 等距{grade}° 俯{int(t)}° 名义余量", r["v_half"] - t, mn)
        add(f"AR整幅 等距{grade}° 俯{int(t)}° 有效余量", r["v_half"] - t - OCC, me)

# 直行 120° 现行定案 的俯角 25/32
r = row(*AR, "rectilinear", 120)
add("AR整幅 直行120° 俯25° 名义", r["v_half"] - 25.0, 17.55)
add("AR整幅 直行120° 俯25° 有效", r["v_half"] - 25.0 - OCC, 15.64)
add("AR整幅 直行120° 俯32° 名义", r["v_half"] - 32.0, 10.55)
add("AR整幅 直行120° 俯32° 有效", r["v_half"] - 32.0 - OCC, 8.64)

# ---------------------------------------------------------------- §B3.2 OV04C10 1080p
OV1080 = (1920, 1080, 1.998)
for grade, fh, hv, fv, vh, hh in (
        (100, 1.847, 92.18, 60.59, 30.30, 46.09),
        (110, 1.541, 102.44, 70.00, 35.00, 51.22),
        (120, 1.271, 112.96, 80.67, 40.34, 56.48)):
    r = row(*OV1080, "rectilinear", grade)
    add(f"OV1080 直行{grade}° f", r["f"], fh)
    add(f"OV1080 直行{grade}° 水平FOV", r["h_fov"], hv)
    add(f"OV1080 直行{grade}° 垂直FOV", r["v_fov"], fv)
    add(f"OV1080 直行{grade}° 垂直半视场", r["v_half"], vh)
    add(f"OV1080 直行{grade}° 水平半视场", r["h_half"], hh)
for grade, fh, hv, fv, vh, hh in (
        (100, 2.522, 87.16, 49.03, 24.51, 43.58),
        (110, 2.293, 95.87, 53.93, 26.96, 47.94),
        (120, 2.102, 104.59, 58.83, 29.42, 52.29)):
    r = row(*OV1080, "equidistant", grade)
    add(f"OV1080 等距{grade}° f", r["f"], fh)
    add(f"OV1080 等距{grade}° 水平FOV", r["h_fov"], hv)
    add(f"OV1080 等距{grade}° 垂直FOV", r["v_fov"], fv)
    add(f"OV1080 等距{grade}° 垂直半视场", r["v_half"], vh)
    add(f"OV1080 等距{grade}° 水平半视场", r["h_half"], hh)
for grade, vh_doc, cells in (
        (100, 24.51, [(9.51, 7.60), (4.51, 2.60), (-0.49, -2.40), (-3.49, -5.40),
                      (-5.49, -7.40), (-7.49, -9.40)]),
        (110, 26.96, [(11.96, 10.06), (6.96, 5.06), (1.96, 0.06), (-1.04, -2.94),
                      (-3.04, -4.94), (-5.04, -6.94)]),
        (120, 29.42, [(14.42, 12.51), (9.42, 7.51), (4.42, 2.51), (1.42, -0.49),
                      (-0.58, -2.49), (-2.58, -4.49)])):
    r = row(*OV1080, "equidistant", grade)
    add(f"OV1080 等距{grade}° 垂直半视场(余量表)", r["v_half"], vh_doc)
    for t, (mn, me) in zip((15.0, 20.0, 25.0, 28.0, 30.0, 32.0), cells):
        add(f"OV1080 等距{grade}° 俯{int(t)}° 名义余量", r["v_half"] - t, mn)
        add(f"OV1080 等距{grade}° 俯{int(t)}° 有效余量", r["v_half"] - t - OCC, me)

# ---------------------------------------------------------------- §B3.3 旧基线
OVFULL = (2688, 1520, 1.998)
for grade, fh, hv, fv, vh in (
        (100, 2.589, 92.10, 60.79, 30.40),
        (110, 2.160, 102.37, 70.21, 35.11),
        (120, 1.781, 112.89, 80.90, 40.45)):
    r = row(*OVFULL, "rectilinear", grade)
    add(f"OV整幅 直行{grade}° f", r["f"], fh)
    add(f"OV整幅 直行{grade}° 水平FOV", r["h_fov"], hv)
    add(f"OV整幅 直行{grade}° 垂直FOV", r["v_fov"], fv)
    add(f"OV整幅 直行{grade}° 垂直半视场", r["v_half"], vh)
for grade, fh, hv, fv, vh in (
        (100, 3.535, 87.05, 49.22, 24.61),
        (110, 3.214, 95.75, 54.15, 27.07),
        (120, 2.946, 104.46, 59.07, 29.53)):
    r = row(*OVFULL, "equidistant", grade)
    add(f"OV整幅 等距{grade}° f", r["f"], fh)
    add(f"OV整幅 等距{grade}° 水平FOV", r["h_fov"], hv)
    add(f"OV整幅 等距{grade}° 垂直FOV", r["v_fov"], fv)
    add(f"OV整幅 等距{grade}° 垂直半视场", r["v_half"], vh)

# ---------------------------------------------------------------- §B3.4 裁切口径
r = row(1920, 1080, 3.000, "equidistant", 120)
add("AR裁1080p 等距120° f", r["f"], 3.155)
add("AR裁1080p 等距120° 水平FOV", r["h_fov"], 104.59)
add("AR裁1080p 等距120° 垂直FOV", r["v_fov"], 58.83)
add("AR裁1080p 等距120° 垂直半视场", r["v_half"], 29.42)
add("AR裁1080p 等距120° 俯25° 名义", r["v_half"] - 25.0, 4.42)
add("AR裁1080p 等距120° 俯25° 有效", r["v_half"] - 25.0 - OCC, 2.51)
add("裁切损失 (整幅31.80 - 裁切29.42)", 31.80 - r["v_half"], 2.38)

# ---------------------------------------------------------------- §B4 判据 + h_max
rAR = row(*AR, "equidistant", 120)
rOV = row(*OVFULL, "equidistant", 120)
r1080 = row(*OV1080, "equidistant", 120)

add("边框遮挡角", OCC, 1.91)
for tag, r, lim_doc, h30, h32, h35 in (
        ("现行AR整幅", rAR, 31.80, 18.60, 19.84, 21.70),
        ("旧基线OV整幅", rOV, 29.53, 17.00, 18.13, 19.83),
        ("OV1080备选", r1080, 29.42, 16.91, 18.04, 19.73)):
    add(f"{tag} 判据A 俯角上限", r["v_half"], lim_doc)
    add(f"{tag} 判据A h_max d=30", 30.0 * math.tan(R(r["v_half"])), h30)
    add(f"{tag} 判据A h_max d=32", 32.0 * math.tan(R(r["v_half"])), h32)
    add(f"{tag} 判据A h_max d=35", 35.0 * math.tan(R(r["v_half"])), h35)

add("现行AR 判据B 俯角上限", rAR["v_half"] - 4.0, 27.80)
add("现行AR 判据B h_max d=30", 30.0 * math.tan(R(rAR["v_half"] - 4.0)), 15.82)
add("现行AR 判据B h_max d=32", 32.0 * math.tan(R(rAR["v_half"] - 4.0)), 16.87)
add("现行AR 判据B h_max d=35", 35.0 * math.tan(R(rAR["v_half"] - 4.0)), 18.45)
add("现行AR 判据B' 俯角上限", rAR["v_half"] - OCC - 4.0, 25.89)
add("现行AR 判据B' h_max d=30", 30.0 * math.tan(R(rAR["v_half"] - OCC - 4.0)), 14.56)
add("现行AR 判据B' h_max d=32", 32.0 * math.tan(R(rAR["v_half"] - OCC - 4.0)), 15.53)
add("现行AR 判据B' h_max d=35", 35.0 * math.tan(R(rAR["v_half"] - OCC - 4.0)), 16.99)
add("现行AR 判据C 俯角上限", rAR["v_half"] - 10.0, 21.80)
add("现行AR 判据C h_max d=30", 30.0 * math.tan(R(rAR["v_half"] - 10.0)), 12.00)
add("现行AR 判据C h_max d=32", 32.0 * math.tan(R(rAR["v_half"] - 10.0)), 12.80)
add("现行AR 判据C h_max d=35", 35.0 * math.tan(R(rAR["v_half"] - 10.0)), 14.00)
add("现行AR 硬上限(零余量)", rAR["v_half"] - OCC, 29.89)
add("现行AR 硬上限 h_max d=35", 35.0 * math.tan(R(rAR["v_half"] - OCC)), 20.12)
add("旧基线 硬上限 h_max d=35", 35.0 * math.tan(R(rOV["v_half"] - OCC)), 18.31)
add("旧基线 判据B' 俯角上限", rOV["v_half"] - OCC - 4.0, 23.62)
add("旧基线 判据B' h_max d=35", 35.0 * math.tan(R(rOV["v_half"] - OCC - 4.0)), 15.31)

for d, doc in ((30.0, 13.99), (32.0, 14.92), (35.0, 16.32)):
    add(f"基线俯角25° h_max d={int(d)}", d * math.tan(R(25.0)), doc)

# §B4.2 差值
add("垂直半视场 现行-旧基线", rAR["v_half"] - rOV["v_half"], 2.27)
add("俯25° 名义余量 现行", rAR["v_half"] - 25.0, 6.80)
add("俯25° 名义余量 旧基线", rOV["v_half"] - 25.0, 4.53)
add("俯25° 有效余量 现行", rAR["v_half"] - 25.0 - OCC, 4.89)
add("俯25° 有效余量 旧基线", rOV["v_half"] - 25.0 - OCC, 2.62)
add("D路线 vs C路线 有效余量差", (rAR["v_half"] - 25.0 - OCC) - (r1080["v_half"] - 25.0 - OCC), 2.38)

# §B4.3 水平
add("AR整幅 水平偏置10° 余量", rAR["h_half"] - 10.0, 40.88)
add("OV1080 水平偏置10° 余量", r1080["h_half"] - 10.0, 42.29)

# §B6 口径不一致两条
add("路线C 等距120° 正确 f", row(*OV1080, "equidistant", 120)["f"], 2.1015, 0.001)
add("路线C 直行120° f", row(*OV1080, "rectilinear", 120)["f"], 1.2706, 0.001)


def main() -> int:
    if not os.path.exists(DOC):
        print(f"❌ 文档不存在: {DOC}")
        return 2
    show = "--show" in sys.argv
    bad = []
    for label, got, want, tol in CHECKS:
        ok = abs(got - want) <= tol
        if show:
            print(f"  [{'OK  ' if ok else 'FAIL'}] {label}: 实算 {got:.4f} vs 文档 {want:.4f}")
        if not ok:
            bad.append((label, got, want))
    print()
    print(f"文档一致性检查: {len(CHECKS)} 条, 一致 {len(CHECKS) - len(bad)}, 不一致 {len(bad)}")
    for label, got, want in bad:
        print(f"  FAIL: {label}: 实算 {got:.4f} vs 文档 {want:.4f}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
