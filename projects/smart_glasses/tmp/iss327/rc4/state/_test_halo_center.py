# -*- coding: utf-8 -*-
"""★_test_halo_center.py -- 证明 PCB_VIA_HALO_CENTER 只比 legacy 多封极少格, 却堵住实测违规节点
   (★纯几何, 不依赖 pcbnew ⇒ 快且可复现)"""
import math, os, sys, ast

SRC = "state/gen_pcb_routing.py"
src = open(SRC, encoding="utf-8").read()
ast.parse(src)                      # 源码必须能解析
assert "PCB_VIA_HALO_CENTER" in src, "缺少 PCB_VIA_HALO_CENTER 开关"
assert "VIA_HALO_CENTER" in src, "缺少 VIA_HALO_CENTER 常量"

G = 0.25
CLEAR = 0.20
VIA_DIA = 0.60
W_CLS = (0.20, 0.25, 0.50)
MARGIN = 0.0        # ★官方 env: PCB_VIA_HALO_MARGIN=0.0

def cells_legacy(i, j, rr, x, y, bb0, bb1):
    """★旧版: 圆心 = 含孔那格的格心 (格索引距离 <= rr/g)"""
    out = set()
    ri = int(math.ceil(rr / G))
    for dj in range(-ri, ri + 1):
        for di in range(-ri, ri + 1):
            if di * di + dj * dj > (rr / G) ** 2 + 1e-9:
                continue
            out.add((i + di, j + dj))
    return out

def cells_center(i, j, rr, x, y, bb0, bb1):
    """★新版: 圆心 = 真实孔心, 半径不变 (不加对角余量)"""
    out = set()
    ri = int(math.ceil(rr / G)) + 1
    for dj in range(-ri, ri + 1):
        for di in range(-ri, ri + 1):
            cx2 = bb0 + (i + di) * G
            cy2 = bb1 + (j + dj) * G
            if math.hypot(cx2 - x, cy2 - y) >= rr + 1e-6:
                continue
            out.add((i + di, j + dj))
    return out

def cells_exact(i, j, rr, x, y, bb0, bb1):
    """★v41: 真实孔心 + 对角余量 g*sqrt(2)/2 (★实测多封 11 格 ⇒ 未通 57->63)"""
    out = set()
    pad = G * math.sqrt(2.0) / 2.0
    ri = int(math.ceil(rr / G)) + 2
    for dj in range(-ri, ri + 1):
        for di in range(-ri, ri + 1):
            cx2 = bb0 + (i + di) * G
            cy2 = bb1 + (j + dj) * G
            if math.hypot(cx2 - x, cy2 - y) >= rr + pad + 1e-9:
                continue
            out.add((i + di, j + dj))
    return out

# ★实测案例 (v40_R 唯一 DRC 违规): GND via @(85.35,13.60) vs ID_DETECT_1 端点 (84.95,13.20)
BB0, BB1 = 0.2, 0.2
VX, VY = 85.35, 13.60
BAD_NODE = (84.95, 13.20)      # ★违规的那个网格节点
i = int(round((VX - BB0) / G)); j = int(round((VY - BB1) / G))
print("via 格索引 = (%d,%d) ⇒ 格心 = (%.3f,%.3f) ⇒ 偏移 = (%.3f,%.3f) = %.4fmm"
      % (i, j, BB0 + i * G, BB1 + j * G,
         VX - (BB0 + i * G), VY - (BB1 + j * G),
         math.hypot(VX - (BB0 + i * G), VY - (BB1 + j * G))))
bi = int(round((BAD_NODE[0] - BB0) / G)); bj = int(round((BAD_NODE[1] - BB1) / G))
d_true = math.hypot(BAD_NODE[0] - VX, BAD_NODE[1] - VY)
print("违规节点 %s 距真实孔心 = %.4fmm (需 >= 0.6250)" % (str(BAD_NODE), d_true))
assert d_true < 0.625, "测试案例前提错了"

rr1 = CLEAR + VIA_DIA / 2.0 + W_CLS[1] / 2.0 + MARGIN
print("cls=1 (0.25mm 线) 的 rr = %.4fmm" % rr1)
cl = cells_legacy(i, j, rr1, VX, VY, BB0, BB1)
cc = cells_center(i, j, rr1, VX, VY, BB0, BB1)
ce = cells_exact(i, j, rr1, VX, VY, BB0, BB1)
print("封格数: legacy=%d  ★CENTER=%d  (v41 EXACT=%d)" % (len(cl), len(cc), len(ce)))
assert (bi, bj) not in cl, "★legacy 居然封了这个节点 ⇒ 前提错"
assert (bi, bj) in cc, "★CENTER 没封住违规节点 ⇒ 修法无效"
assert len(cc) - len(cl) <= 3, "★CENTER 多封太多格 (会像 v41 一样变亏)"
assert len(cc) < len(ce), "★CENTER 应该比 EXACT 少封很多格"
print("✔ legacy 放行违规节点 / CENTER 封住它 / CENTER 只多封 %d 格 (EXACT 多封 %d 格)"
      % (len(cc) - len(cl), len(ce) - len(cl)))

# ★随机位置扫 200 次: CENTER 平均多封几格
import random
random.seed(7)
tot_c = tot_e = tot_l = 0
N = 200
for _ in range(N):
    x = BB0 + random.uniform(0, 40); y = BB1 + random.uniform(0, 40)
    ii = int(round((x - BB0) / G)); jj = int(round((y - BB1) / G))
    tot_l += len(cells_legacy(ii, jj, rr1, x, y, BB0, BB1))
    tot_c += len(cells_center(ii, jj, rr1, x, y, BB0, BB1))
    tot_e += len(cells_exact(ii, jj, rr1, x, y, BB0, BB1))
print("随机 %d 个孔位平均封格: legacy=%.1f  CENTER=%.1f (+%.1f)  EXACT=%.1f (+%.1f)"
      % (N, tot_l / N, tot_c / N, (tot_c - tot_l) / N, tot_e / N, (tot_e - tot_l) / N))
assert (tot_c - tot_l) / N <= 2.0, "★CENTER 平均多封太多格"

# ★源码级回归: 三个分支互斥且默认关
assert 'VIA_HALO_CENTER = os.environ.get("PCB_VIA_HALO_CENTER", "0") == "1"' in src
assert "if VIA_HALO_CENTER:" in src and "elif VIA_HALO_EXACT:" in src
print("✔ 源码: 三分支互斥 (CENTER / EXACT / legacy) + 默认关")
print("ALL TESTS PASS")
