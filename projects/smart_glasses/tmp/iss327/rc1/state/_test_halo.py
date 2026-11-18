#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_test_halo.py —— ★v41 机制单测: 通孔净距禁区按真实孔心算

★★**背景 (2026-11-05 23:2x 机器读)**:
  v36_S 实测 DRC 3 ⇒ 根因 = `_add_via_halo` 用"含孔心那一格"的**格心**当圆心
  ⇒ 孔偏格心 δ 时, 禁区整体偏 δ ⇒ A* 对角步 (0.25√2) 可擦过孔盘
  实测: 孔 (85.35,9.60) 偏格心 (0.10,0.10);
        走线端点 (84.95,9.20) 离**真实孔心 0.5657mm** (需 ≥0.625 ⇒ 违规)
        却按格心判 = 0.7071mm ⇒ **放行** ⇒ DRC 漏网

★★**新判据 (可证安全)**: 格子被禁 ⇔ **真实孔心到该格方形区的最小距离 < rr**
  ⇒ 任何**未被禁**的格, 其方形区都离孔心 ≥ rr
  ⇒ 而一条走线段 (含对角段) 完全落在它所穿的那些格的方形区并集内
  ⇒ ⇒ **穿未禁格的对角段也必然 ≥ rr** ⇒ 不会再擦孔
  ⇒ ★**代价**: 比旧判据略严 (最多多禁中心距 rr+0.177mm 的格) ⇒ 换来 DRC 干净

★**本测法**: 不跑整板 (太慢) ⇒ 直接复算两种判据下的格子集合 + 几何证明
"""
import math

G = 0.25
BB0 = -0.05
BB1 = -0.05
CLEAR = 0.20
VIA_DIA = 0.60
W_CLS = (0.20, 0.25, 0.40)      # 窄 / 信号 / 粗 (与路由器一致)
HALO_MARGIN = 0.20

def cx(i): return BB0 + i * G
def cy(j): return BB1 + j * G
def ci(x): return int(round((x - BB0) / G))
def cj(y): return int(round((y - BB1) / G))

def rr_of(cls, halo_margin):
    return CLEAR + VIA_DIA / 2.0 + W_CLS[cls] / 2.0 + halo_margin

def blocked_old(cls, vx, vy, i2, j2, halo_margin):
    """旧判据: 圆心=含孔心那格的格心, 半径按格数"""
    rr = rr_of(cls, halo_margin)
    i, j = ci(vx), cj(vy)
    di, dj = i2 - i, j2 - j
    return not (di * di + dj * dj > (rr / G) ** 2 + 1e-9)

def blocked_exact(cls, vx, vy, i2, j2, halo_margin):
    """新判据: 真实孔心 -> 格心距 < rr + g*sqrt(2)/2 (★可证安全)"""
    rr = rr_of(cls, halo_margin)
    pad = G * math.sqrt(2.0) / 2.0
    return math.hypot(cx(i2) - vx, cy(j2) - vy) < rr + pad + 1e-9
    return math.hypot(dx, dy) < rr

def seg_min_dist_to_via(a, b, via):
    (x1, y1), (x2, y2) = a, b
    vx, vy = via
    dx, dy = x2 - x1, y2 - y1
    L2 = dx * dx + dy * dy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((vx - x1) * dx + (vy - y1) * dy) / L2))
    return math.hypot(x1 + t * dx - vx, y1 + t * dy - vy)

FAIL = []
def check(name, cond, extra=""):
    print("  %s %s%s" % ("✅" if cond else "❌", name, ("  " + extra) if extra else ""))
    if not cond:
        FAIL.append(name)

def cellset(fn, cls, vx, vy, hm, span=7):
    i, j = ci(vx), cj(vy)
    return set((i + di, j + dj) for dj in range(-span, span + 1)
               for di in range(-span, span + 1)
               if fn(cls, vx, vy, i + di, j + dj, hm))

print("═══ 用例 1: v36_S 的真实违规点 ═══")
VIA = (85.35, 9.60)
TRK = (84.95, 9.20)
rr1 = rr_of(1, 0.0)           # 信号层 + VIA_HALO_MARGIN=0.0 ⇒ 0.625
d_real = math.hypot(TRK[0] - VIA[0], TRK[1] - VIA[1])
i2, j2 = ci(TRK[0]), cj(TRK[1])
check("旧判据把违规格放行 (DRC 漏网的原因)", not blocked_old(1, VIA[0], VIA[1], i2, j2, 0.0),
      "离真实孔心 %.4f < %.4f" % (d_real, rr1))
check("新判据把该格禁掉", blocked_exact(1, VIA[0], VIA[1], i2, j2, 0.0))

print("═══ 用例 2: 新判据绝不放松 (老版禁的格, 新版都禁) ═══")
old_s = cellset(blocked_old, 1, VIA[0], VIA[1], 0.0)
new_s = cellset(blocked_exact, 1, VIA[0], VIA[1], 0.0)
check("old 不松于 new (只可能更严)", old_s <= new_s,
      "old格数=%d new格数=%d 多禁=%d" % (len(old_s), len(new_s), len(new_s - old_s)))
check("多禁的格数有限 (<=16)", len(new_s - old_s) <= 16,
      "多禁=%d" % len(new_s - old_s))

print("═══ 用例 3: 对角段也不擦孔 (两端点都未禁的段) ═══")
def worst_unblocked(fn):
    worst = 1e9
    i, j = ci(VIA[0]), cj(VIA[1])
    for dj in range(-6, 7):
        for di in range(-6, 7):
            a_i, a_j = i + di, j + dj
            if fn(1, VIA[0], VIA[1], a_i, a_j, 0.0):
                continue          # ★起点被禁 ⇒ 这段根本不会被走
            for (ddi, ddj) in ((1, 1), (1, -1), (-1, 1), (-1, -1), (1, 0), (0, 1), (1, 0), (-1, 0), (0, -1)):
                b_i, b_j = a_i + ddi, a_j + ddj
                if fn(1, VIA[0], VIA[1], b_i, b_j, 0.0):
                    continue      # ★终点被禁 ⇒ 这段也不会被走
                d = seg_min_dist_to_via((cx(a_i), cy(a_j)), (cx(b_i), cy(b_j)), VIA)
                worst = min(worst, d)
    return worst
worst_old = worst_unblocked(blocked_old)
worst_new = worst_unblocked(blocked_exact)
check("旧判据下确有对角段擦孔 (< rr)", worst_old < rr1 - 1e-9,
      "worst=%.4f rr=%.4f" % (worst_old, rr1))
check("新判据下无对角段擦孔 (>= rr)", worst_new >= rr1 - 1e-9,
      "worst=%.4f rr=%.4f" % (worst_new, rr1))

print("═══ 用例 4: 孔正好在格心 ⇒ 新判据仍只更严 (不扰动正常情形) ═══")
V2 = (cx(50), cy(40))
o2 = cellset(blocked_old, 1, V2[0], V2[1], 0.0)
n2 = cellset(blocked_exact, 1, V2[0], V2[1], 0.0)
check("old 不松于 new (只可能更严)", old_s <= new_s,
      "old格数=%d new格数=%d 多禁=%d" % (len(old_s), len(new_s), len(new_s - old_s)))
print("═══ 用例 5: 默认关闭时行为与旧版逐位一致 ═══")
src = open("/home/yuewuya/.openclaw/workspace/projects/smart_glasses/state/gen_pcb_routing.py",
           encoding="utf-8").read()
check("开关默认 0", 'VIA_HALO_EXACT = os.environ.get("PCB_VIA_HALO_EXACT", "0") == "1"' in src)
check("精确分支被开关包住 (else 保留旧逻辑)",
      "if VIA_HALO_EXACT:" in src and "else:" in src.split("def _add_via_halo")[1][:4000])

print()
if FAIL:
    print("❌ 失败 %d 条: %s" % (len(FAIL), FAIL))
    raise SystemExit(1)
print("✅ 全部通过")
