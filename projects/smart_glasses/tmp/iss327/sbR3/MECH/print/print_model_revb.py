#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rev B 打印包 **解析模型** (MECH/print/print_model_revb.py)
================================================================================
为什么单独一个模型文件:
  · 生成器 (gen_print_pack_revb.py) 出的 STL 由 **很多块** 拼成 (条带法切孔 ⇒ 同一块被切成
    几十个小盒), 网格的三角形绕向也 **不统一** ⇒ 用 "射线奇偶法" 直接量 STL 极易被
    "共面内部面 / 绕向不一致" 弄错 (本轮已实测踩了 4 次坑)。
  · ⇒ 改成: **生成器同时记录一份解析图元表** (盒 / 圆柱 / 圆管 / 沿 Y 的棱柱),
    自检脚本用 **解析几何精确算** 各种尺寸, 再用 **点在实体内测试 (射线奇偶, 只判内外)**
    把解析模型与 STL **逐点互验** ⇒ 既精确又能证明"STL = 规格"。

图元表 (MODEL) 记录格式:
  ('box',    x0, x1, y0, y1, z0, z1)
  ('cylz',   cx, cy, r, z0, z1)              # 沿 Z 的实心圆柱
  ('tubez',  cx, cy, r_out, r_in, z0, z1)    # 沿 Z 的圆管 (r_in 是通孔)
  ('prism_y', [(x,z), ...], y0, y1)          # 沿 Y 拉伸、截面在 XZ 平面的多边形

用法: 由 gen_print_pack_revb.py 填充; verify_pack_revb.py 读取。
"""
from __future__ import annotations

import math

import numpy as np

MODEL = []


def reset():
    MODEL.clear()


# ---------------------------------------------------------------- 记录
def add_box(x0, x1, y0, y1, z0, z1):
    MODEL.append(("box", float(x0), float(x1), float(y0), float(y1), float(z0), float(z1)))


def add_cylz(cx, cy, r, z0, z1):
    MODEL.append(("cylz", float(cx), float(cy), float(r), float(z0), float(z1)))


def add_tubez(cx, cy, r_out, r_in, z0, z1):
    MODEL.append(("tubez", float(cx), float(cy), float(r_out), float(r_in), float(z0), float(z1)))


def add_prism_y(profile, y0, y1):
    MODEL.append(("prism_y", [(float(a), float(b)) for a, b in profile], float(y0), float(y1)))


def add_prism_z(profile, z0, z1):
    """profile 在 XY 平面 (顶点 (x,y)), 沿 Z 拉伸"""
    MODEL.append(("prism_z", [(float(a), float(b)) for a, b in profile], float(z0), float(z1)))


def arc_profile(cx, cy, r_out, r_in, a0, a1, seg=32):
    """沿 Z 的 **部分圆环** 截面 (XY 平面): 外弧 a0→a1 + 内弧 a1→a0。
    用于 "沿 Z 开槽的螺钉柱" (两个半环 + 中间 0.6 槽)。"""
    pts = []
    for i in range(seg + 1):
        a = math.radians(a0 + (a1 - a0) * i / seg)
        pts.append((cx + r_out * math.cos(a), cy + r_out * math.sin(a)))
    for i in range(seg + 1):
        a = math.radians(a1 + (a0 - a1) * i / seg)
        pts.append((cx + r_in * math.cos(a), cy + r_in * math.sin(a)))
    return pts


# ---------------------------------------------------------------- 区间工具
def _merge(iv):
    iv = sorted(iv)
    out = []
    for (a, b) in iv:
        if out and a <= out[-1][1] + 1e-9:
            out[-1] = (out[-1][0], max(out[-1][1], b))
        else:
            out.append((a, b))
    return out


def _sub(iv, cut):
    ca, cb = cut
    out = []
    for (a, b) in iv:
        if cb <= a or ca >= b:
            out.append((a, b))
            continue
        if a < ca:
            out.append((a, ca))
        if cb < b:
            out.append((cb, b))
    return out


def _clip(iv, cuts):
    for c in cuts:
        iv = _sub(iv, c)
    return iv


# ---------------------------------------------------------------- 多边形 ∩ 直线
_PLANE_AXES = {"xy": ("x", "y"), "xz": ("x", "z"), "yz": ("y", "z")}


def poly_line(poly, plane, cut_axis, val):
    """多边形 (在 plane 平面, 顶点 (u,v)) 与直线 **cut_axis=val** 相交
    → 返回 [(lo,hi), ...] (沿 **另一坐标** 的区间)。

    ★ 顶点计数用 **半开区间规则** ((a0 > val) != (a1 > val)):
      若用严格 "<0" 判据, 直线正好穿过顶点时该顶点被漏计 ⇒ 交点少一个 ⇒ 区间错。
      (圆心线 / 圆边界线正好命中顶点是常态 —— 例如圆孔 ⌀ 切线与采样线齐平。)
    """
    (ua, va) = _PLANE_AXES[plane]
    # 顶点存的是 (u, v) ⇒ idx_u=0, idx_v=1
    if cut_axis == ua:
        idx_cut, idx_out = 0, 1
    elif cut_axis == va:
        idx_cut, idx_out = 1, 0
    else:
        raise ValueError(f"cut_axis={cut_axis} 不在平面 {plane} 的坐标 {ua}/{va} 里")
    n = len(poly)
    xs = []
    for i in range(n):
        p0 = poly[i]
        p1 = poly[(i + 1) % n]
        a0 = p0[idx_cut]
        a1 = p1[idx_cut]
        if (a0 > val) != (a1 > val):
            if abs(a1 - a0) < 1e-15:
                xs.append(p0[idx_out])
            else:
                t = (val - a0) / (a1 - a0)
                xs.append(p0[idx_out] + t * (p1[idx_out] - p0[idx_out]))
    xs.sort()
    out = []
    i = 0
    while i < len(xs) - 1:
        if xs[i + 1] - xs[i] > 1e-12:
            out.append((xs[i], xs[i + 1]))
            i += 2
        else:
            i += 1
    return out


def poly_line_xy(poly, cut_axis, val):
    return poly_line(poly, "xy", cut_axis, val)


def poly_line_xz(poly, cut_axis, val):
    return poly_line(poly, "xz", cut_axis, val)


def _point_in_poly(poly, pu, pv, plane="xz"):
    """射线法判点是否在多边形内 (多边形在 plane 平面, 顶点 (u,v))"""
    (ua, va) = _PLANE_AXES[plane]
    iu, iv = (0, 1)
    inside = False
    n = len(poly)
    for i in range(n):
        p0 = poly[i]
        p1 = poly[(i + 1) % n]
        a0 = p0[iv]
        a1 = p1[iv]
        b0 = p0[iu]
        b1 = p1[iu]
        if (a0 > pv) != (a1 > pv):
            t = (pv - a0) / (a1 - a0)
            if pu < b0 + t * (b1 - b0):
                inside = not inside
    return inside


# ---------------------------------------------------------------- 沿轴射线求覆盖区间
def cover_x(y, z):
    """沿 +X 的射线 (固定 y,z) → 实体覆盖区间 [(x0,x1), ...] (已合并)。"""
    iv = []
    for p in MODEL:
        if p[0] == "box":
            _, x0, x1, y0, y1, z0, z1 = p
            if y0 - 1e-9 <= y <= y1 + 1e-9 and z0 - 1e-9 <= z <= z1 + 1e-9:
                iv.append((x0, x1))
        elif p[0] == "cylz":
            _, cx, cy, r, z0, z1 = p
            if z0 - 1e-9 <= z <= z1 + 1e-9:
                d = r * r - (y - cy) ** 2
                if d >= 0:
                    s = math.sqrt(d)
                    iv.append((cx - s, cx + s))
        elif p[0] == "tubez":
            _, cx, cy, r_out, r_in, z0, z1 = p
            if z0 - 1e-9 <= z <= z1 + 1e-9:
                d_out = r_out * r_out - (y - cy) ** 2
                d_in = r_in * r_in - (y - cy) ** 2
                if d_out >= 0:
                    s_out = math.sqrt(d_out)
                    if d_in >= 0:
                        s_in = math.sqrt(d_in)
                        iv.append((cx - s_out, cx - s_in))
                        iv.append((cx + s_in, cx + s_out))
                    else:
                        iv.append((cx - s_out, cx + s_out))
        elif p[0] == "prism_y":
            _, poly, y0, y1 = p
            if y0 - 1e-9 <= y <= y1 + 1e-9:
                for (xa, xb) in poly_line_xz(poly, "z", z):
                    iv.append((xa, xb))
        elif p[0] == "prism_z":
            _, poly, z0, z1 = p
            if z0 - 1e-9 <= z <= z1 + 1e-9:
                for (xa, xb) in poly_line_xy(poly, "y", y):
                    iv.append((xa, xb))
    return _merge(iv)


def cover_y(x, z):
    """沿 +Y 的射线 (固定 x,z) → 实体覆盖区间 [(y0,y1), ...]。"""
    iv = []
    for p in MODEL:
        if p[0] == "box":
            _, x0, x1, y0, y1, z0, z1 = p
            if x0 - 1e-9 <= x <= x1 + 1e-9 and z0 - 1e-9 <= z <= z1 + 1e-9:
                iv.append((y0, y1))
        elif p[0] == "cylz":
            _, cx, cy, r, z0, z1 = p
            if z0 - 1e-9 <= z <= z1 + 1e-9:
                d = r * r - (x - cx) ** 2
                if d >= 0:
                    s = math.sqrt(d)
                    iv.append((cy - s, cy + s))
        elif p[0] == "tubez":
            _, cx, cy, r_out, r_in, z0, z1 = p
            if z0 - 1e-9 <= z <= z1 + 1e-9:
                d_out = r_out * r_out - (x - cx) ** 2
                d_in = r_in * r_in - (x - cx) ** 2
                if d_out >= 0:
                    s_out = math.sqrt(d_out)
                    if d_in >= 0:
                        s_in = math.sqrt(d_in)
                        iv.append((cy - s_out, cy - s_in))
                        iv.append((cy + s_in, cy + s_out))
                    else:
                        iv.append((cy - s_out, cy + s_out))
        elif p[0] == "prism_y":
            _, poly, y0, y1 = p
            if _point_in_poly(poly, x, z, "xz"):
                iv.append((y0, y1))
        elif p[0] == "prism_z":
            _, poly, z0, z1 = p
            if z0 - 1e-9 <= z <= z1 + 1e-9:
                for (ya, yb) in poly_line_xy(poly, "x", x):
                    iv.append((ya, yb))
    return _merge(iv)


def cover_z(x, y):
    """沿 +Z 的射线 (固定 x,y) → 实体覆盖区间 [(z0,z1), ...]。"""
    iv = []
    for p in MODEL:
        if p[0] == "box":
            _, x0, x1, y0, y1, z0, z1 = p
            if x0 - 1e-9 <= x <= x1 + 1e-9 and y0 - 1e-9 <= y <= y1 + 1e-9:
                iv.append((z0, z1))
        elif p[0] == "cylz":
            _, cx, cy, r, z0, z1 = p
            d = r * r - (x - cx) ** 2 - (y - cy) ** 2
            if d >= 0:
                iv.append((z0, z1))
        elif p[0] == "tubez":
            _, cx, cy, r_out, r_in, z0, z1 = p
            d_out = r_out * r_out - (x - cx) ** 2 - (y - cy) ** 2
            d_in = r_in * r_in - (x - cx) ** 2 - (y - cy) ** 2
            if d_out >= 0 and d_in < 0:
                iv.append((z0, z1))
        elif p[0] == "prism_y":
            _, poly, y0, y1 = p
            if y0 - 1e-9 <= y <= y1 + 1e-9:
                for (za, zb) in poly_line_xz(poly, "x", x):
                    iv.append((za, zb))
        elif p[0] == "prism_z":
            _, poly, z0, z1 = p
            if _point_in_poly(poly, x, y, "xy"):
                iv.append((z0, z1))
    return _merge(iv)


def voids(cover):
    """覆盖区间 → 空档区间 [(a,b), ...] (起点到第一段之间也算空档)。"""
    out = []
    cur = None
    for (a, b) in cover:
        if cur is not None and a > cur:
            out.append((cur, a))
        cur = b
    return out


def inside(x, y, z):
    """点是否在实体内 (解析判定)。"""
    for p in MODEL:
        if p[0] == "box":
            _, x0, x1, y0, y1, z0, z1 = p
            if x0 - 1e-9 <= x <= x1 + 1e-9 and y0 - 1e-9 <= y <= y1 + 1e-9 and z0 - 1e-9 <= z <= z1 + 1e-9:
                return True
        elif p[0] == "cylz":
            _, cx, cy, r, z0, z1 = p
            if z0 - 1e-9 <= z <= z1 + 1e-9 and (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                return True
        elif p[0] == "tubez":
            _, cx, cy, r_out, r_in, z0, z1 = p
            if z0 - 1e-9 <= z <= z1 + 1e-9:
                d2 = (x - cx) ** 2 + (y - cy) ** 2
                if r_in * r_in <= d2 <= r_out * r_out:
                    return True
        elif p[0] == "prism_y":
            _, poly, y0, y1 = p
            if y0 - 1e-9 <= y <= y1 + 1e-9 and _point_in_poly(poly, x, z, "xz"):
                return True
        elif p[0] == "prism_z":
            _, poly, z0, z1 = p
            if z0 - 1e-9 <= z <= z1 + 1e-9 and _point_in_poly(poly, x, y, "xy"):
                return True
    return False


# ---------------------------------------------------------------- STL 点在实体内 (射线奇偶)
def stl_inside(tris, point, direction=(1.0, 0.0, 0.0), tmax=1e4):
    """从 point 沿 direction 打到无穷, 与三角网求交; **交点数为奇数 ⇒ 在实体内**。
    ★ 只用奇偶判内外, 不用绕向 ⇒ 网格绕向不一致也不影响结果。
    """
    o = [point[0], point[1], point[2]]
    d = list(direction)
    v0 = tris[:, 1, :]
    v1 = tris[:, 2, :]
    v2 = tris[:, 3, :]
    e1 = v1 - v0
    e2 = v2 - v0
    h = np.cross(np.broadcast_to(np.asarray(d, dtype=float), e2.shape), e2)
    a = np.einsum("ij,ij->i", e1, h)
    ok = np.abs(a) > 1e-14
    f = np.zeros_like(a)
    f[ok] = 1.0 / a[ok]
    s = np.array(o) - v0
    u = f * np.einsum("ij,ij->i", s, h)
    q = np.cross(s, e1)
    vv = f * np.einsum("j,ij->i", d, q)
    t = f * np.einsum("ij,ij->i", e2, q)
    hit = ok & (u >= -1e-9) & (vv >= -1e-9) & (u + vv <= 1 + 1e-9) & (t > 1e-7) & (t < tmax)
    return int(hit.sum()) % 2 == 1
