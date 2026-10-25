#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打印包自检 (模型级实测) —— verify_pack.py
=====================================================================
对交付的 STL 做 **光线投射实测** (不是"我以为标称是多少"): 把每个关键配合特征的
**实体几何真值** 量出来, 与标称值对表。

⚠️ 口径声明 (重要, 别误读):
  本脚本量的是 **模型网格**, 不是打印出来的实物。
  → 它证明"交付的 STL 尺寸是对的" (v1.1 的数字被正确实体化);
  → 它**不能**替代 M-PRINT (实物打印件实测尺寸) —— 实物还有 FDM 工艺偏差;
  → 因此 M-PRINT 在 measurements.yaml 里仍是 [推算]/未测, 阶段门照样不认。
  实物实测清单见 MECH/print/MEASURE_CHECKLIST.md

用法: python3 MECH/print/verify_pack.py
退出码: 0 = 模型与标称一致; 1 = 有偏差 (说明 STL 与 v1.1 不同步)
"""
from __future__ import annotations

import math
import os
import struct
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from gen_print_pack import (GAPS, OVERHANGS, P, WALLS,  # noqa: E402
                            build_coupon, build_temple_cage, v)


# ---------------------------------------------------------------- STL 读取
def load_stl(path):
    with open(path, "rb") as f:
        f.read(80)
        n = struct.unpack("<I", f.read(4))[0]
        raw = np.frombuffer(f.read(n * 50), dtype=np.uint8).reshape(n, 50)
        fl = raw[:, :48].copy().view(np.float32).reshape(n, 4, 3).astype(np.float64)
    return fl


# ---------------------------------------------------------------- 光线投射
def ray_hits(tris, origin, direction, tmin=1e-7):
    """Möller–Trumbore, 返回沿射线方向的命中距离 (已排序)"""
    v0, v1, v2 = tris[:, 1, :], tris[:, 2, :], tris[:, 3, :]
    e1, e2 = v1 - v0, v2 - v0
    d = np.asarray(direction, dtype=float)
    h = np.cross(np.broadcast_to(d, e2.shape), e2)
    a = np.einsum("ij,ij->i", e1, h)
    ok = np.abs(a) > 1e-14
    f = np.zeros_like(a)
    f[ok] = 1.0 / a[ok]
    s = np.asarray(origin, dtype=float) - v0
    u = f * np.einsum("ij,ij->i", s, h)
    q = np.cross(s, e1)
    vv = f * np.einsum("j,ij->i", d, q)
    t = f * np.einsum("ij,ij->i", e2, q)
    hit = ok & (u >= -1e-9) & (vv >= -1e-9) & (u + vv <= 1 + 1e-9) & (t > tmin)
    ts = np.sort(t[hit])
    # 合并重复命中 (射线正好打在棱边上时会命中两次)
    out = []
    for x in ts:
        if not out or x - out[-1] > 1e-6:
            out.append(float(x))
    return np.array(out)


def intervals(hits):
    """命中序列 → 实体区间 [(a,b), ...] (射线从实体外出发时成立)"""
    return [(float(hits[i]), float(hits[i + 1])) for i in range(0, len(hits) - 1, 2)]


def gaps(iv):
    """相邻实体区间之间的空腔 [(a,b), ...]"""
    return [(iv[i][1], iv[i + 1][0]) for i in range(len(iv) - 1)]


def nearest(items, pos, key="mid"):
    """从候选区间里挑离 pos 最近的一个"""
    if not items:
        return None
    if key == "mid":
        return min(items, key=lambda g: abs((g[0] + g[1]) / 2 - pos))
    return min(items, key=lambda g: abs(g[0] - pos))


# ---------------------------------------------------------------- 探针
class Probe:
    def __init__(self, part, item, nominal, unit, measured, tol=0.01, note=""):
        self.part, self.item, self.nominal = part, item, nominal
        self.unit, self.measured, self.tol, self.note = unit, measured, tol, note

    @property
    def ok(self):
        return self.measured is not None and abs(self.measured - self.nominal) <= self.tol

    @property
    def delta(self):
        return None if self.measured is None else self.measured - self.nominal


def build_probes():
    out = []
    coupon = load_stl(os.path.join(HERE, "fit_coupon_340.stl"))
    cage = load_stl(os.path.join(HERE, "temple_cage_340.stl"))

    # ---- (1) 壁厚阶梯: 沿 +Y, 量实体段长 (探针避开三角面对角线) ----
    for i, t in enumerate(WALLS):
        x = 4 + i * 9 + 3.1
        iv = intervals(ray_hits(coupon, (x, 0.0, 8.0), (0, 1, 0)))
        meas = (iv[0][1] - iv[0][0]) if iv else None
        out.append(Probe("fit_coupon", f"壁厚阶梯 #{i+1}", t, "mm", meas, 0.005,
                         "沿 +Y 射线量实体段 (0.4 喷嘴下能否成型)"))

    # ---- (2) 间隙梳: 沿 +X, 量相邻肋条之间的空腔 (命中值是相对射线原点的距离) ----
    OX = 50.0
    hits = ray_hits(coupon, (OX, 10.0, 8.0), (1, 0, 0))
    g_all = gaps(intervals(hits))
    x = 52.0
    for i, g in enumerate(GAPS):
        gg = nearest(g_all, (x + 3.0 + g / 2) - OX)
        meas = (gg[1] - gg[0]) if gg else None
        out.append(Probe("fit_coupon", f"间隙梳 #{i+1} (肋间名义间隙)", g, "mm", meas,
                         0.005, "沿 +X 量空腔; 0.4 喷嘴多半填死 → 那就是实测结论"))
        x += 3.0 + g

    # ---- (3) 螺钉柱孔径: 沿 +X, 量柱内孔 (相邻实体段之间的空腔) ----
    hits = ray_hits(coupon, (0.0, 26.0, 8.0), (1, 0, 0))
    g_all = gaps(intervals(hits))
    bosses = [(20.0, v("hole_m12"), "M1.2 螺钉柱 ⌀2.4 未开槽"),
              (30.0, v("hole_m12") + v("split_slot"), "⌀2.4 沿 Z 开槽螺钉柱 (含 0.6 槽)"),
              (40.0, v("hole_m12"), "⌀3.0 螺钉柱"),
              (50.0, v("dowel_h7"), "⌀4.0 定位销柱 ⌀2.0")]
    for cx, nom, name in bosses:
        gg = nearest(g_all, cx)
        meas = (gg[1] - gg[0]) if gg else None
        out.append(Probe("fit_coupon", f"螺钉柱孔 {name}", nom, "mm", meas, 0.02,
                         "沿 +X 量柱内空腔"))

    # ---- (4) 配作孔: 沿 +X, Y=40 ----
    hits = ray_hits(coupon, (0.0, 40.0, 8.0), (1, 0, 0))
    g_all = gaps(intervals(hits))
    for cx, d in ((10.0, 2.0), (18.0, 2.1), (26.0, 2.2)):
        gg = nearest(g_all, cx)
        meas = (gg[1] - gg[0]) if gg else None
        out.append(Probe("fit_coupon", f"配作孔 ⌀{d}", d, "mm", meas, 0.01,
                         "打印件与金属骨架配作孔"))

    # ---- (5) 悬空角: 两个高度各打一条 +X 射线, 由 x 位置差反算斜面角 ----
    for i, ang in enumerate(OVERHANGS):
        x0 = 62 + i * 17
        a = math.radians(ang)
        dx, dz = 16.0 * math.cos(a), 16.0 * math.sin(a)
        z1, z2 = 2.0 + 0.3 * dz, 2.0 + 0.7 * dz
        h1 = ray_hits(coupon, (x0 - 2.0, 36.0, z1), (1, 0, 0))
        h2 = ray_hits(coupon, (x0 - 2.0, 36.0, z2), (1, 0, 0))
        if len(h1) and len(h2):
            x1 = x0 - 2.0 + float(h1[0])
            x2 = x0 - 2.0 + float(h2[0])
            meas = math.degrees(math.atan2(abs(z2 - z1), abs(x2 - x1)))
        else:
            meas = None
        out.append(Probe("fit_coupon", f"悬空试样 {ang}° 下表面斜角", float(ang), "deg",
                         meas, 0.5, "两点拟合下表面斜角"))

    # ---- (6) 标定块: 自 +Z 向下量阶梯高 ----
    for x, nom, name in ((122.0, 5.0, "5mm 步"), (127.0, 10.0, "10mm 步"), (132.0, 20.0, "20mm 步")):
        h = ray_hits(coupon, (x, 70.0, 1e3), (0, 0, -1))
        meas = (1e3 - float(h[0]) - 2.0) if len(h) else None
        out.append(Probe("fit_coupon", f"标定块 {name}", nom, "mm", meas, 0.01,
                         "自 +Z 向下量, 底板面 z=2.0"))

    # ---- (7) 波导卡槽单边间隙: 沿 +Y ----
    x = 6.0
    for g in (0.10, 0.12, 0.15):
        iv = intervals(ray_hits(coupon, (x + 4.0, 60.0, 4.0), (0, 1, 0)))
        gg = gaps(iv)
        meas = (gg[0][1] - gg[0][0]) if gg else None
        out.append(Probe("fit_coupon", f"波导卡槽单边间隙 {g:.2f}", g, "mm", meas, 0.005,
                         "沿 +Y 量槽底与对侧壁之间空腔"))
        x += 14

    # ===================== temple_cage =====================
    clr = v("clr_metal")
    # 电池槽长: 沿 +X 从槽口 (X=0) 打到端挡
    h = ray_hits(cage, (0.0, 3.5, 12.0), (1, 0, 0))
    meas = float(h[0]) if len(h) else None
    out.append(Probe("temple_cage", "电池槽长度", v("batt_l") + 2 * clr, "mm", meas, 0.01,
                     "沿 +X 自槽口打到端挡"))

    # 电池槽高: 沿 +Z 自下方打到槽底顶面/侧挡底面
    h = ray_hits(cage, (20.0, 3.5, -5.0), (0, 0, 1))
    meas = (float(h[2]) - float(h[1])) if len(h) >= 3 else None
    out.append(Probe("temple_cage", "电池槽高度", v("batt_v") + 2 * clr, "mm", meas, 0.01,
                     "沿 +Z 量槽底面到侧挡底面"))

    # 电池槽厚: 沿 +Y 量两挡板之间
    iv = intervals(ray_hits(cage, (20.0, -5.0, 12.0), (0, 1, 0)))
    gg = gaps(iv)
    meas = (gg[0][1] - gg[0][0]) if gg else None
    out.append(Probe("temple_cage", "电池槽厚度", v("batt_thk") + 2 * clr, "mm", meas, 0.01,
                     "沿 +Y 量两挡板之间"))

    # 配作销孔
    iv = intervals(ray_hits(cage, (0.0, 68.0, 10.0), (1, 0, 0)))
    g_all = gaps(iv)
    for cx, nom, name in ((6.0, v("hole_m12"), "M1.2 配作销"),
                          (16.0, v("dowel_h7"), "⌀2.0 H7 定位销"),
                          (26.0, 2.1, "打印件配作孔 ⌀2.1"),
                          (36.0, 2.2, "打印件配作孔 ⌀2.2")):
        gg = nearest(g_all, cx)
        meas = (gg[1] - gg[0]) if gg else None
        out.append(Probe("temple_cage", f"配作销 {name}", nom, "mm", meas, 0.01, "沿 +X 量孔"))

    # 走线槽 6 x 2: 槽宽 = 两壁净宽; 槽高 = 槽壁总高 - 槽底厚
    iv = intervals(ray_hits(cage, (30.0, 95.0, 3.0), (0, 1, 0)))
    gg = gaps(iv)
    meas = (gg[0][1] - gg[0][0]) if gg else None
    out.append(Probe("temple_cage", "走线槽宽", v("duct_w"), "mm", meas, 0.01, "沿 +Y 量两壁净宽"))
    h_wall = ray_hits(cage, (30.0, 100.5, -5.0), (0, 0, 1))
    h_floor = ray_hits(cage, (30.0, 104.0, -5.0), (0, 0, 1))
    meas = None
    if len(h_wall) >= 2 and len(h_floor) >= 2:
        meas = (float(h_wall[-1]) - float(h_floor[-1]))
    out.append(Probe("temple_cage", "走线槽高", v("duct_h"), "mm", meas, 0.01,
                     "槽壁总高 - 槽底厚"))

    # Type-C 面板开孔 (板厚沿 Y 120..123)
    iv = intervals(ray_hits(cage, (-5.0, 121.5, 3.0), (1, 0, 0)))
    gg = gaps(iv)
    meas = (gg[0][1] - gg[0][0]) if gg else None
    out.append(Probe("temple_cage", "Type-C 开口宽", v("tc_open_w"), "mm", meas, 0.01, "沿 +X 量开口"))
    h = ray_hits(cage, (6.0, 121.5, -5.0), (0, 0, 1))
    iv = intervals(h)
    gg = gaps(iv)
    meas = (gg[0][1] - gg[0][0]) if gg else None
    out.append(Probe("temple_cage", "Type-C 开口高", v("tc_open_h"), "mm", meas, 0.01, "沿 +Z 量开口"))
    iv = intervals(ray_hits(cage, (-5.0, 121.5, 3.0), (1, 0, 0)))
    meas = (iv[0][1] - iv[0][0]) if iv else None
    out.append(Probe("temple_cage", "Type-C 面板侧壁厚", v("tc_wall_min"), "mm", meas, 0.01,
                     "沿 +X 量实体段 (承力壁 ≥1.5)"))
    return out


def main():
    print("=" * 100)
    print("打印包模型自检 (光线投射实测 STL 网格) —— ⚠️ 模型级, 不等于实物打印实测")
    print("=" * 100)
    probes = build_probes()
    ok = 0
    cur = None
    for p in probes:
        if p.part != cur:
            cur = p.part
            print(f"\n【{cur}】")
        m = "None" if p.measured is None else f"{p.measured:.3f}"
        d = "—" if p.delta is None else f"{p.delta:+.3f}"
        flag = "✅" if p.ok else ("⚠️ " if p.measured is not None else "❌")
        if p.ok:
            ok += 1
        print(f"  {flag} {p.item:<42} 标称 {p.nominal:>7.3f} {p.unit:<3} "
              f"实测 {m:>8} {p.unit:<3} Δ {d:>8}  {p.note}")
    print("\n" + "-" * 100)
    print(f"模型与标称一致: {ok}/{len(probes)}")
    print("★ 口径: 上面是 **模型真值** (证明 STL 把 v1.1 的数字实体化对了)。")
    print("  M-PRINT (实物打印件实测尺寸) 仍为 0 数据 —— 必须实物打印 + 卡尺实测, 见")
    print("  MECH/print/MEASURE_CHECKLIST.md")
    return 0 if ok == len(probes) else 1


if __name__ == "__main__":
    sys.exit(main())
