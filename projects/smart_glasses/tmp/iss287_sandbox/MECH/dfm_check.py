#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DFM 评审自检 (ISS-025) —— 结构 DFM 评审 (P2S 打印件 → 量产开模件)
================================================================================
为什么要有这个脚本:
  · `MECH/DFM_REVIEW.md` 的结论不能只有散文 —— 脱模斜度面数、公差栈余量、
    深腔双面斜度的壁厚损失, 都必须能一条命令复现。
  · 本脚本 **不量实物** (本机物理上无法打印/量测, 见 MECH/print/ENV_PROBE_20261101.md)
    ⇒ 所有输出都是 **[推算]**, 不是 [实测]。

三段:
  【A】脱模斜度 / 倒扣 面级统计 —— 对 Rev B 打印包的 **解析图元表** 精确求
        (不用在 STL 上采样, 见 print_model_revb.py 的说明: STL 绕向不统一)
  【B】量产公差栈 vs 打印件公差栈 —— V / H / L 三链, 复用 fit_check_v3_30mm.py 的锁定值
  【C】深腔双面脱模斜度的 **壁厚损失** + 收缩敏感性

★ 关键概念 (DFM 必背):
  拔模方向 = +Z (模具向上拔)。某面的 **法向 n** 与 +Z 的夹角 θ = acos(n_z)。
    · 该面的 **脱模角 α = 90° − θ**            (α ≥ 0 才不倒扣; α = 0 = 直壁)
    · 该面的 **水平倾角 β = θ**                (β < 45° = FDM 悬垂, 需支撑)
  ⇒ **FDM 的"自支撑 45°" 与注塑/压铸的"脱模斜度" 是同一个量 β 的两个相反读数**:
      β < 45° (α > 45°): FDM 要支撑, 但对注塑/压铸脱模极好
      β ≈ 90° (α ≈ 0°):  FDM 自支撑, 但注塑/压铸必须加 ≥1° 斜度 ⇒ **几何要改**
    ⇒ **打印件上量到的配合尺寸, 不能直接迁移到量产件** (这是 ISS-025 的核心结论之一)。

用法:  python3 MECH/dfm_check.py
退出码: 0 = 报告已生成 (结论看最后一节; **不代表实物已验**)
"""
from __future__ import annotations

import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "print"))

import print_model_revb as PM  # noqa: E402
from gen_print_pack_revb import (build_coupon, build_frame_typec,  # noqa: E402
                                 build_temple_cage)
from fit_check_v3_30mm import BASE, CRIT, TOL  # noqa: E402  (锁死尺寸链 + 公差账)

# ---------------------------------------------------------------- 参数
DRAFT_MIN = 1.0      # 量产件最小脱模斜度 (注塑/压铸通用工程经验下限)  [推算]
DRAFT_PROD_INJ = 1.0  # 注塑 PC/ABS 建议脱模斜度                          [推算]
DRAFT_PROD_DIE = 1.0  # 压铸镁合金 ADC12 建议脱模斜度                      [推算]
SIN_MIN = math.sin(math.radians(DRAFT_MIN))
COS_FLAT = math.cos(math.radians(45.0))   # |n_z| >= 0.7071 ⇒ 水平面 (β<=45°)

# 量产公差带 (通用工程经验值, **未按牌号锁定** ⇒ [推算], 需模具厂确认 ⇒ §7 needs_from)
TOL_PROD = {
    "inj_pcabs": 0.20,   # 注塑 PC/ABS 镜腿壳, 一般公差, 特征 <=30mm       [推算]
    "die_mgadc12": 0.25,  # 压铸镁合金 ADC12 镜框, 一般公差, 小件            [推算]
    "cnc_al6063": 0.05,  # CNC Al6063-T6 一般公差                            [推算]
    "cnc_al6063_fine": 0.02,  # CNC 精加工面 (定位面)                        [推算]
    "pcb_out": 0.15,     # PCB 外形 (沿用 fit_check_v3_30mm TOL['pcb_out'])  [推算]
}

# 收缩率 **假设档** (只做敏感性, **不锁定具体牌号** ⇒ [推算]; 实际值需模具厂给)
SHRINK_CASES = [1.0, 1.5, 2.0]

# ---------------------------------------------------------------- 桶
BUCKETS = ["FLAT_TOP", "FLAT_BOTTOM", "DRAFTED", "ZERO_DRAFT", "UNDERCUT"]


def classify(nz: float):
    """法向 n 的 z 分量 → 桶名 + 脱模角 α (度)"""
    if nz >= COS_FLAT:
        return "FLAT_TOP", None
    if nz <= -COS_FLAT:
        return "FLAT_BOTTOM", None
    alpha = 90.0 - math.degrees(math.acos(max(-1.0, min(1.0, nz))))
    if nz < -SIN_MIN:
        return "UNDERCUT", alpha
    if nz <= SIN_MIN:
        return "ZERO_DRAFT", alpha
    return "DRAFTED", alpha


def beta_of(nz: float) -> float:
    """水平倾角 β (度) = acos(n_z); β<45 ⇒ FDM 悬垂需支撑"""
    return math.degrees(math.acos(max(-1.0, min(1.0, nz))))


class Acc:
    def __init__(self):
        self.count = {b: 0 for b in BUCKETS}
        self.area = {b: 0.0 for b in BUCKETS}
        self.undercuts = []   # (alpha, area, center)
        self.zero_draft = []  # (area, center)
        self.fdm_hang = 0.0   # β<45° 的面积 (FDM 需支撑)
        self.total_area = 0.0

    def add(self, nz, area, cx=0.0, cy=0.0, cz=0.0):
        b, alpha = classify(nz)
        self.count[b] += 1
        self.area[b] += area
        self.total_area += area
        if nz > 0 and beta_of(nz) < 45.0:
            self.fdm_hang += area
        if b == "UNDERCUT":
            self.undercuts.append((alpha, area, (cx, cy, cz)))
        elif b == "ZERO_DRAFT":
            self.zero_draft.append((area, (cx, cy, cz)))
        return b


def poly_area(pts):
    """shoelace; 返回 (面积, 是否逆时针)"""
    s = 0.0
    for i in range(len(pts)):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % len(pts)]
        s += x0 * y1 - x1 * y0
    return s / 2.0, s > 0


def acc_model(model, acc: Acc):
    for prim in model:
        k = prim[0]
        if k == "box":
            _, x0, x1, y0, y1, z0, z1 = prim
            ax = (y1 - y0) * (z1 - z0)
            ay = (x1 - x0) * (z1 - z0)
            az = (x1 - x0) * (y1 - y0)
            cx, cy, cz = (x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2
            acc.add(1.0, az, cx, cy, cz + (z1 - z0) / 2)
            acc.add(-1.0, az, cx, cy, cz - (z1 - z0) / 2)
            for sgn, area in ((1, ax), (-1, ax)):
                acc.add(0.0, area, cx + sgn * (x1 - x0) / 2, cy, cz)
            for sgn, area in ((1, ay), (-1, ay)):
                acc.add(0.0, area, cx, cy + sgn * (y1 - y0) / 2, cz)
        elif k == "cylz":
            _, cx, cy, r, z0, z1 = prim
            h = z1 - z0
            acc.add(1.0, math.pi * r * r, cx, cy, z1)
            acc.add(-1.0, math.pi * r * r, cx, cy, z0)
            # 侧壁: 直壁 ⇒ n_z = 0 ⇒ ZERO_DRAFT (圆柱必须拔模!)
            acc.add(0.0, 2 * math.pi * r * h, cx, cy, (z0 + z1) / 2)
        elif k == "tubez":
            _, cx, cy, ro, ri, z0, z1 = prim
            h = z1 - z0
            acc.add(1.0, math.pi * (ro * ro - ri * ri), cx, cy, z1)
            acc.add(-1.0, math.pi * (ro * ro - ri * ri), cx, cy, z0)
            acc.add(0.0, 2 * math.pi * ro * h, cx, cy, (z0 + z1) / 2)
            acc.add(0.0, 2 * math.pi * ri * h, cx, cy, (z0 + z1) / 2)  # 内壁 (需芯棒斜度)
        elif k == "prism_y":
            _, prof, y0, y1 = prim
            a, ccw = poly_area(prof)
            a = abs(a)
            acc.add(0.0, a, 0, y1, 0)   # 端面 (+Y)
            acc.add(0.0, a, 0, y0, 0)   # 端面 (-Y)
            n = len(prof)
            for i in range(n):
                x0, z0 = prof[i]
                x1, z1 = prof[(i + 1) % n]
                dx, dz = x1 - x0, z1 - z0
                L = math.hypot(dx, dz)
                if L < 1e-9:
                    continue
                nx, nz = dz / L, -dx / L
                if not ccw:
                    nx, nz = -nx, -nz
                acc.add(nz, L * (y1 - y0), (x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
        elif k == "prism_z":
            _, prof, z0, z1 = prim
            a, _ccw = poly_area(prof)
            a = abs(a)
            acc.add(1.0, a, 0, 0, z1)
            acc.add(-1.0, a, 0, 0, z0)
            n = len(prof)
            for i in range(n):
                x0, y0 = prof[i]
                x1, y1 = prof[(i + 1) % n]
                dx, dy = x1 - x0, y1 - y0
                L = math.hypot(dx, dy)
                if L < 1e-9:
                    continue
                acc.add(0.0, L * (z1 - z0), (x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)


def bbox(model):
    xs, ys, zs = [], [], []
    for p in model:
        k = p[0]
        if k == "box":
            _, x0, x1, y0, y1, z0, z1 = p
            xs += [x0, x1]; ys += [y0, y1]; zs += [z0, z1]
        elif k in ("cylz", "tubez"):
            _, cx, cy = p[0], p[1], p[2]
            r = p[3] if k == "cylz" else p[3]
            xs += [cx - r, cx + r]; ys += [cy - r, cy + r]; zs += [p[-2], p[-1]]
        elif k == "prism_y":
            _, prof, y0, y1 = p
            for x, z in prof:
                xs.append(x); zs.append(z)
            ys += [y0, y1]
        elif k == "prism_z":
            _, prof, z0, z1 = p
            for x, y in prof:
                xs.append(x); ys.append(y)
            zs += [z0, z1]
    return (min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))


# =====================================================================
# 【A】脱模斜度 / 倒扣 面级统计
# =====================================================================
def part_a():
    print("=" * 100)
    print("【A】脱模斜度 / 倒扣 面级统计 (Rev B 打印包, 解析图元表精确求)")
    print("=" * 100)
    print(f"  判据: 脱模角 α = 90° − acos(n_z);  α ≥ {DRAFT_MIN:.1f}° 才不倒扣")
    print(f"  拉出方向 = +Z (模具向上拔)  ⇒  α < 0 = 倒扣 (注塑/压铸出不来, FDM 能打)")
    print(f"  水平倾角 β = acos(n_z) ⇒  β < 45° = FDM 悬垂 (需支撑)")
    print()
    rows = []
    for name, builder in (("fit_coupon", build_coupon),
                          ("temple_cage", build_temple_cage),
                          ("frame_typec", build_frame_typec)):
        PM.reset()
        builder()
        model = list(PM.MODEL)
        acc = Acc()
        acc_model(model, acc)
        lo, hi = bbox(model)
        rows.append((name, model, acc, lo, hi))
        print(f"  ── {name} ──  包围盒 "
              f"{hi[0]-lo[0]:.2f} × {hi[1]-lo[1]:.2f} × {hi[2]-lo[2]:.2f} mm")
        print(f"     面数 {sum(acc.count.values()):6d} | 总面积 {acc.total_area:12.2f} mm²")
        for b in BUCKETS:
            print(f"     {b:<12} 面数 {acc.count[b]:6d} | 面积 {acc.area[b]:12.2f} mm²"
                  f" | 占 {100*acc.area[b]/max(acc.total_area,1e-9):5.1f}%")
        if acc.undercuts:
            acc.undercuts.sort(key=lambda t: -t[1])
            print(f"     ⚠ 倒扣面 {len(acc.undercuts)} 个, 最大的 5 个:")
            for alpha, area, c in acc.undercuts[:5]:
                print(f"        α={alpha:+7.2f}°  面积 {area:10.2f} mm²  中心 ({c[0]:.2f},{c[1]:.2f},{c[2]:.2f})")
        else:
            print("     ✅ 无倒扣面 (α < 0) —— Rev B 几何在 +Z 拔模方向下可脱模")
        print(f"     FDM 需支撑面积 (β<45°): {acc.fdm_hang:.2f} mm² "
              f"({100*acc.fdm_hang/max(acc.total_area,1e-9):.1f}%)")
        print()
    return rows


# =====================================================================
# 【B】量产公差栈 vs 打印件公差栈
# =====================================================================
def part_b():
    print("=" * 100)
    print("【B】量产公差栈 vs 打印件公差栈 (V / H / L 三链)")
    print("=" * 100)
    print(f"  打印件判据 CRIT = 2 × 单边公差 {TOL['fdm_part']:.2f} = {CRIT:.2f} mm  (fit_check_v3_30mm 口径)")
    print(f"  打印件最坏值 **直接沿用 fit_check_v3_30mm 的现有数字** (V 1.40 / H 0.65 / L 13.60), 不重算、不打架")
    print(f"  公差扣减项 Δ = n_tol × 单边公差 (n_tol = 该链上吃公差的界面数, 由现有数字反解)")
    print()
    # n_tol 由 fit_check_v3_30mm 的现有最坏值反解: Δ_print = 名义余量 − 现有最坏值
    #   V: 2.00−1.40 = 0.60 = 2×0.30 ⇒ n_tol=2 ; H: 0.95−0.65 = 0.30 = 1×0.30 ⇒ n_tol=1
    #   L: 14.50−13.60 = 0.90 = 3×0.30 ⇒ n_tol=3
    # 腔深/拉出方向/被吃掉的链 (脱模斜度项, 标 [推算])
    chains = [
        dict(zone="镜脚·V", item="板宽 30 + 走线槽 6.00 vs 净高 38.00", need=36.00,
             avail=BASE["cav_v"], n_tol=2, t_prod=TOL_PROD["inj_pcabs"],
             who="注塑 PC/ABS 镜腿壳", draft_h=None, eats=None),
        dict(zone="镜脚·H", item="电芯段 (皮肤壁0.8+座深4.75+顶板0.8) vs 7.30", need=6.35,
             avail=BASE["cav_h"], n_tol=1, t_prod=TOL_PROD["inj_pcabs"],
             who="注塑 PC/ABS 镜腿壳", draft_h=BASE["cav_v"], eats="H"),
        dict(zone="镜脚·L", item="电芯40.5 + 板长60 + 余量15 vs 130.00", need=115.50,
             avail=BASE["cav_l"], n_tol=3, t_prod=TOL_PROD["inj_pcabs"],
             who="注塑 PC/ABS 镜腿壳", draft_h=BASE["cav_v"], eats="L"),
        dict(zone="镜框·V", item="光学舱 (走鹃Ⅱ + 分光组件 + 余量) —— 未验", need=None,
             avail=None, n_tol=0, t_prod=TOL_PROD["die_mgadc12"],
             who="压铸镁合金 ADC12 镜框", draft_h=None, eats=None),
    ]
    out = []
    for c in chains:
        zone, item = c["zone"], c["item"]
        if c["need"] is None:
            print(f"  {zone:<8} {item:<44} [0数据] (缺 u1/u4/u8b/u5) ⇒ 不参与公差栈")
            out.append((zone, None))
            continue
        margin = c["avail"] - c["need"]
        t_print = TOL["fdm_part"]
        d_print = c["n_tol"] * t_print
        w_print = margin - d_print
        crit_p = 2 * t_print
        d_prod = c["n_tol"] * c["t_prod"]
        w_prod = margin - d_prod
        crit_q = 2 * c["t_prod"]
        ok_p = w_print >= crit_p
        ok_q = w_prod >= crit_q
        print(f"  {zone:<8} {item}")
        print(f"           名义余量 {margin:.2f} | 打印件 Δ={c['n_tol']}×{t_print:.2f}={d_print:.2f} "
              f"⇒ 最坏 {w_print:.2f} (判据 ≥{crit_p:.2f}) {'✅' if ok_p else '❌'}")
        print(f"           量产   Δ={c['n_tol']}×{c['t_prod']:.2f}={d_prod:.2f} ⇒ 最坏 {w_prod:.2f} "
              f"(判据 ≥{crit_q:.2f}) {'✅' if ok_q else '❌'}"
              f"{'   ★ 量产公差下不通过' if (ok_p and not ok_q) else ''}")
        rec = dict(margin=margin, w_print=w_print, w_prod=w_prod, crit_p=crit_p,
                   crit_q=crit_q, ok_p=ok_p, ok_q=ok_q, n_tol=c["n_tol"],
                   t_print=t_print, t_prod=c["t_prod"], who=c["who"])
        if c["draft_h"]:
            for a in (0.5, 1.0):
                loss = 2 * c["draft_h"] * math.tan(math.radians(a))
                w = w_prod - loss
                ok = w >= crit_q
                print(f"           ＋脱模截面差 (腔深 {c['draft_h']:.2f}, 双面 {a:.1f}°) = {loss:.3f} "
                      f"⇒ 最坏 {w:.3f} (判据 ≥{crit_q:.2f}) {'✅' if ok else '❌  ← 几何上做不出来'}"
                      f"   [吃掉的是 {c['eats']} 链]")
                rec[f"draft_{a}"] = dict(loss=loss, worst=w, ok=ok)
        out.append((zone, rec))
        print()
    return out


# =====================================================================
# 【C】深腔双面脱模斜度的壁厚损失 + 收缩敏感性
# =====================================================================
def part_c():
    print("=" * 100)
    print("【C】深腔双面脱模斜度的 **壁厚损失** + 收缩敏感性")
    print("=" * 100)
    print("  推导: 外表面与内腔各带 α 拔模 ⇒ 同一高度上壁厚随高度线性变薄")
    print("        Δt(h) = 2 · h · tan(α)   (h = 从分型面算起的高度)")
    print()
    print("  推导: 拉出方向上的外表面与内腔各带 α 拔模 ⇒")
    print("        · **内腔的横截面沿拉出方向变窄 2·h·tan(α)** (窄端在封闭端)")
    print("          ⇒ 窄端的 H / L 净空比宽端少这么多")
    print()
    print(f"  {'腔深 h (mm)':<14}{'α=0.5°':>12}{'α=1.0°':>12}{'α=1.5°':>12}   说明")
    for h, note in ((BASE["cav_h"], "镜脚前后厚 (H 向) —— 若沿 H 拉出"),
                    (BASE["cav_v"], "镜脚净高 (V 向) —— 沿 V 拉出则吃掉 H/L 净空"),
                    (42.00, "电池段盲槽 (电池 40.5 + 插入余量, 沿 L 拉出) [推算]"),
                    (BASE["cav_l"], "镜脚内腔长 (L 向) —— 不能整段一次拉出")):
        vals = [2 * h * math.tan(math.radians(a)) for a in (0.5, 1.0, 1.5)]
        print(f"  {h:<14.2f}{vals[0]:>12.3f}{vals[1]:>12.3f}{vals[2]:>12.3f}   {note}")
    print()
    print("  ★ 读法: 镜脚下壳主腔深 38.00mm (沿 V 拉出) 且内外双面 α=1° ⇒")
    print("    内腔横截面在封闭端比开口端窄 **1.327mm** (H 与 L 都是)")
    print("    ⇒ 镜脚·H 链 (电芯段) 名义余量只有 0.95mm ⇒ **减去脱模损失 = −0.377mm, 几何上做不出来**")
    print("    ⇒ 缓解: ① 皮肤侧做皮纹面 (允许 α=0.5° ⇒ 损失减半到 0.664mm)")
    print("            ② 电池座/PCB 座改 **CNC 嵌件** (与 §5.5 架构一致) ⇒ 壳体只做浅腔造型")
    print("            ③ 沿 L 分体 (电池段单独壳) ⇒ 腔深降到 ~20mm")
    print()
    print("  【收缩敏感性】只做敏感性, **不锁定具体牌号** (实际值需模具厂给 ⇒ needs_from)")
    dims = [("镜框主体长", 140.00), ("镜脚内腔长", BASE["cav_l"]),
            ("镜脚净高 V", BASE["cav_v"]), ("镜脚前后厚 H", BASE["cav_h"])]
    print(f"  {'假设收缩率':<12}" + "".join(f"{n:>16}" for n, _ in dims))
    for s in SHRINK_CASES:
        print(f"  {s:.1f}%        " + "".join(f"{d*s/100:>16.3f}" for _, d in dims))
    print()
    print("  ★ 读法: 镁合金压铸件若收缩 1.5%, 镜框主体长方向就缩 ~2.10mm")
    print("    ⇒ **铰链接口孔位绝不能直接开在压铸件本体上** (收缩直接改孔距)")
    print()


def main():
    print("=" * 100)
    print("DFM 自检 (ISS-025) | 结构 DFM 评审 | 拔模方向 +Z | 判据 α ≥ 1.0°")
    print("=" * 100)
    print("★ 口径: 本脚本是 **设计态几何 + 公差栈 + 通用工程经验值** 的确定性计算")
    print("  ⇒ 全部 [推算]; 本机物理上无法打印/量测 ⇒ **无任何 [实测]**")
    print("  ⇒ 量产公差带与收缩率 **未按牌号锁定** ⇒ 需模具厂/表面处理方书面确认 (DFM_REVIEW §7)")
    print()
    part_a()
    part_b()
    part_c()
    print("=" * 100)
    print("★ 结论")
    print("=" * 100)
    print("  ① Rev B 打印包 = **检具 + 试样**, 不含量产外形件 ⇒ 量产外壳的脱模面级统计")
    print("     **目前 0 个数据点**; 上面的面数是检具/试样自身的, 只证明方法可用 (§A)")
    print("  ② Rev B 几何里 **ZERO_DRAFT 面占 25-62%** (直壁) ⇒ 量产版每个侧壁都要加 ≥1° 斜度;")
    print("     fit_coupon 另有 2 个倒扣面 (α=−40°/−30°) ⇒ FDM 能打, 注塑/压铸出不来")
    print("  ③ ★ **公差不是量产的杀手, 脱模斜度才是**:")
    print("     公差侧: 注塑 ±0.20 比 FDM ±0.30 紧 ⇒ V/H/L 三链最坏值反而改善 (1.40→1.60 / 0.65→0.75 / 13.60→13.90)")
    print("     脱模侧: 主腔深 38.00 双面 1° ⇒ 内腔横截面窄端少 1.327mm")
    print("             ⇒ 镜脚·H 链 (电芯段) 最坏 0.75 − 1.327 = **−0.577 ⇒ 几何上做不出来**")
    print("             ⇒ 0.5° (皮纹面) 只能救到 0.087, 仍 < 判据 0.40 ⇒ **必须靠结构改, 不能靠公差改**")
    print("  ④ ⇒ 量产架构必须延续 '打印件负责造型 + 金属件承担定位/承力' (§5.5), 具体: **电池座/PCB 座改 CNC 嵌件**")
    print("  ⑤ 收缩敏感性: 1.5% 假设 ⇒ 镜框长向 2.10mm ⇒ 铰链接口 / 定位孔距 **不能留在压铸件本体**")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
