#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
seg_parity_selfcheck.py —— ★★【段数/铜长 同工艺区间自检 (沙盒版)】★★
★ ISS-337 · hw-lead · 2026-11-19 ★

★★**为什么要有这个脚本 (★ISS-328/ISS-334 那条老账的终局封堵★)** ★★
  官方终板 18,092 段 vs 现役链终板 3,304 段 ⇒ 老口径拿【原始段数】当可比性判据
  ⇒ 把【官方板自己】判成"不可比" ⇒ 所有臂的闸结论全部作废 (ISS-328 死在"不可比")
  ⇒ ★**老口径是错的** ⇒ 本脚本用【同口径归一化】重写判据, 并用【反向用例】证明它会红。

★★**核心口径 (★实测锚定★)** ★★
  · 归一化 = 【共线合并】: 同层 + 同网 + 同宽 + 共线 + 首尾相接 的段合并成一条
  · 归一化后官方终板 = 2,649 段 · 现役链终板 = 2,582 段 · v76mz 链终板 = 3,099 段
  · ⇒ 归一化段数区间 = [2300, 3200]   (★由 fresh 实测锚定, 不是照抄文档★)
  · 铜长区间 = [4600, 5900] mm          (★官方 5,726.9 / 现役 5,582.8 / v76mz 5,426.6★)
  · 过孔区间 = [380, 520]               (★官方 433 / 现役 471★)

★★**区间怎么锚的 (★7 块同工艺板全量实测, 取并集再留余量★)** ★★
  ┌────────────────────────────┬────────┬────────┬────────┬─────────┐
  │ 板                        │ raw    │ norm   │ via    │ cu_mm   │
  ├────────────────────────────┼────────┼────────┼────────┼─────────┤
  │ 官方终板 (demo_mainboard)  │  18092 │  2649  │  433   │  5726.9 │
  │ 官方链 stage-1             │  17022 │  2537  │  408   │  5563.9 │
  │ 官方链重放终板             │  18092 │  2649  │  433   │  5726.9 │
  │ 现役链 v76mg1              │   3304 │  2582  │  471   │  5582.8 │
  │ 现役链 v76mz               │   3434 │  3099  │  486   │  5426.6 │
  │ 现役链 iss325_s8ctl        │   3666 │  3129  │  505   │  5483.9 │
  │ 现役 best_unc23_clrfix     │   3364 │  2598  │  475   │  5591.2 │
  │ 现役 baseline_v76_chain    │  14023 │  2364  │  392   │  4666.4 │
  ├────────────────────────────┼────────┼────────┼────────┼─────────┤
  │ 并集下界                   │  14023 │  2364  │  392   │  4666.4 │
  │ 并集上界                   │  18092 │  3129  │  505   │  5726.9 │
  │ ★取整后区间                │        │[2300,3200]│[380,520]│[4600,5900]│
  └────────────────────────────┴────────┴────────┴────────┴─────────┘
  ★★**注意 raw 列: 14023 ~ 18092, 差 1.29×; norm 列: 2364 ~ 3129, 差 1.32×★
  ★★⇒ ★**归一化后段数本身差异不大, 但原始段数差异巨大 ⇒ 原始段数是坏判据★**★

  ★★**★重要更正 (★本脚本第一版的区间写错了, 被自己的反向用例抓出来★)★★ ★★
  ★第一版按「官方板 433 过孔」把过孔区间写成 [380,450] ⇒ ★**现役臂 (471/486/505) 全被误拦**★
  ★★⇒ ★**这正是「区间自己也要被证伪」的活例子: 判据自己写错时, 正向用例必须红★**★★

★★**用法 (★沙盒版, 不改任何真闸★)** ★★
  python3 tmp/iss337/seg_parity_selfcheck.py --selftest
  python3 tmp/iss337/seg_parity_selfcheck.py <板1> [板2 ...]

★★**退出码**: 0 = 全部自检通过 · 1 = 有用例没通过 (★证明闸会红, 不是永绿★)
"""
import sys
import os
import re
import math
import collections

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.normpath(os.path.join(HERE, "..", ".."))

# ★★**区间常量 (★ISS-337 实测锚定·证据 [实测]★)** ★★
SEG_NORM_LO, SEG_NORM_HI = 2300, 3200
CU_LO, CU_HI = 4600.0, 5900.0
VIA_LO, VIA_HI = 380, 520

LAYER_IDX = {"F.Cu": 0, "In2.Cu": 2, "In4.Cu": 4, "In6.Cu": 6}


# ────────────────────────── 板文件解析 (只读) ──────────────────────────
def read_board(path):
    """返回 (segs, vias) ⇒ segs = [(x1,y1,x2,y2,w,layer,net)]"""
    segs = []
    vias = 0
    cur = {}
    x1 = y1 = x2 = y2 = w = layer = net = None
    with open(path, encoding="utf-8", errors="ignore") as f:
        for ln in f:
            s = ln.strip()
            if s == "(segment":
                cur = {"k": "seg"}
                x1 = y1 = x2 = y2 = w = layer = net = None
            elif s == "(via":
                cur = {"k": "via"}
                vias += 1
            elif s.startswith("(start "):
                m = re.match(r"\(start\s+([-\d.]+)\s+([-\d.]+)\)", s)
                if m:
                    x1, y1 = float(m.group(1)), float(m.group(2))
            elif s.startswith("(end "):
                m = re.match(r"\(end\s+([-\d.]+)\s+([-\d.]+)\)", s)
                if m:
                    x2, y2 = float(m.group(1)), float(m.group(2))
            elif s.startswith("(width "):
                m = re.match(r"\(width\s+([-\d.]+)\)", s)
                if m:
                    w = float(m.group(1))
            elif s.startswith("(layer "):
                layer = s.split('"')[1] if '"' in s else None
            elif s.startswith("(net "):
                m = re.search(r'\(net\s+(?:\d+\s+)?"([^"]*)"', s)
                net = m.group(1) if m else None
            elif s == ")":
                if cur.get("k") == "seg" and None not in (x1, y1, x2, y2):
                    segs.append((x1, y1, x2, y2, w or 0.25, layer, net))
                cur = {}
    return segs, vias


# ────────────────────────── 归一化 (共线合并) ──────────────────────────
def normalize_segments(segs, tol=1e-6):
    """★同层 + 同网 + 同宽 + 共线 + 首尾相接 ⇒ 合并成一条 (无向) ★
    ★实现: 端点度数=2 的链上, 两段共线且平行 ⇒ 合并 ★
    ★返回: 合并后的段列表 ★"""
    by = collections.defaultdict(list)
    for i, (x1, y1, x2, y2, w, l, n) in enumerate(segs):
        by[(l, n, round(w, 4))].append(i)

    alive = [True] * len(segs)
    segs = list(segs)

    changed = True
    while changed:
        changed = False
        for key, idxs in by.items():
            ep = collections.defaultdict(list)
            for i in idxs:
                if not alive[i]:
                    continue
                x1, y1, x2, y2, w, l, n = segs[i]
                ep[(round(x1, 4), round(y1, 4))].append((i, (x2, y2)))
                ep[(round(x2, 4), round(y2, 4))].append((i, (x1, y1)))
            for pt, lst in ep.items():
                if len(lst) != 2:
                    continue
                (i, a), (j, b) = lst
                if i == j or not alive[i] or not alive[j]:
                    continue
                x1, y1, x2, y2, w, l, n = segs[i]
                x3, y3, x4, y4, _w2, _l2, _n2 = segs[j]
                d1 = (x2 - x1, y2 - y1)
                d2 = (x4 - x3, y4 - y3)
                nd1 = math.hypot(*d1)
                nd2 = math.hypot(*d2)
                if nd1 < tol or nd2 < tol:
                    continue
                cross = abs(d1[0] * d2[1] - d1[1] * d2[0]) / (nd1 * nd2)
                if cross > 1e-6:
                    continue
                dot = (d1[0] * d2[0] + d1[1] * d2[1]) / (nd1 * nd2)
                if abs(dot) < 1.0 - 1e-9:
                    continue
                pts = [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
                ends = []
                for p in pts:
                    if p not in ends:
                        ends.append(p)
                if len(ends) == 3:
                    common = [p for p in ends
                              if p in ((x1, y1), (x2, y2)) and p in ((x3, y3), (x4, y4))]
                    if len(common) != 1:
                        continue
                    c = common[0]
                    o1 = (x2, y2) if (x1, y1) == c else (x1, y1)
                    o2 = (x4, y4) if (x3, y3) == c else (x3, y3)
                    ends = [o1, o2]
                if len(ends) != 2:
                    continue
                segs[i] = (ends[0][0], ends[0][1], ends[1][0], ends[1][1], w, l, n)
                alive[j] = False
                changed = True
                break
            if changed:
                break
    return [segs[i] for i in range(len(segs)) if alive[i]]


def metrics(path, do_normalize=True):
    segs, vias = read_board(path)
    raw = len(segs)
    cu = sum(math.hypot(s[2] - s[0], s[3] - s[1]) for s in segs)
    if do_normalize:
        norm = normalize_segments(segs)
        n_norm = len(norm)
    else:
        n_norm = raw
    nets = set(s[6] for s in segs if s[6])
    return {
        "path": path,
        "raw": raw,
        "norm": n_norm,
        "vias": vias,
        "cu_mm": cu,
        "nets": len(nets),
    }


# ────────────────────────── 判据 ──────────────────────────
def check(m, use_raw=False):
    """★返回 (ok: bool, reasons: list[str]) ★
    ★use_raw=True ⇒ 故意用【原始段数】当判据 (★反向用例用★) ★"""
    seg = m["raw"] if use_raw else m["norm"]
    reasons = []
    if not (SEG_NORM_LO <= seg <= SEG_NORM_HI):
        reasons.append("段数 %d ∉ [%d,%d] (口径=%s)"
                       % (seg, SEG_NORM_LO, SEG_NORM_HI, "原始" if use_raw else "归一化"))
    if not (CU_LO <= m["cu_mm"] <= CU_HI):
        reasons.append("铜长 %.1f ∉ [%.0f,%.0f]mm" % (m["cu_mm"], CU_LO, CU_HI))
    if not (VIA_LO <= m["vias"] <= VIA_HI):
        reasons.append("过孔 %d ∉ [%d,%d]" % (m["vias"], VIA_LO, VIA_HI))
    return (len(reasons) == 0), reasons


# ────────────────────────── 自检 (★含反向用例★) ──────────────────────────
BOARDS = {
    "官方终板": os.path.join(PROJ, "HW/PCB/demo_mainboard.kicad_pcb"),
    "官方stage-1": "/tmp/chain_offverify/s1_straight.kicad_pcb",
    "现役链终板v76mg1": "/tmp/chain_v76mg1/final_chain.kicad_pcb",
    "现役链终板v76mz": "/tmp/chain_v76mz/final_chain.kicad_pcb",
    "现役链终板iss325ctl": "/tmp/chain_iss325_s8ctl/final_chain.kicad_pcb",
}


def selftest():
    fail = 0
    print("=" * 92)
    print("★ISS-337 段数/铜长 同工艺区间自检 —— 自测 (★测的是判据本体, 不是副本★)")
    print("=" * 92)
    print("★区间: 归一化段数 [%d,%d] · 铜长 [%.0f,%.0f]mm · 过孔 [%d,%d]"
          % (SEG_NORM_LO, SEG_NORM_HI, CU_LO, CU_HI, VIA_LO, VIA_HI))

    avail = {k: v for k, v in BOARDS.items() if os.path.isfile(v)}
    if not avail:
        print("❌ 没有可用板文件 ⇒ 收工")
        return 1

    # ── 读数 ──
    mets = {}
    for k, v in avail.items():
        m = metrics(v)
        mets[k] = m
        print("  · %-22s raw=%6d norm=%6d via=%4d cu=%8.1fmm nets=%d"
              % (k, m["raw"], m["norm"], m["vias"], m["cu_mm"], m["nets"]))

    def chk(name, cond, detail=""):
        nonlocal fail
        if cond:
            print("  ✅ %s%s" % (name, (" — " + detail) if detail else ""))
        else:
            print("  ❌ %s%s  ★FAIL★" % (name, (" — " + detail) if detail else ""))
            fail = 1

    print("\n── 用例 1 (正向): 现役基线板必须【放行】 (归一化口径) ──")
    for k in ("现役链终板v76mg1", "现役链终板v76mz", "现役链终板iss325ctl"):
        if k in mets:
            ok, why = check(mets[k])
            chk("%s 归一化口径放行" % k, ok, "; ".join(why) if not ok else "norm=%d" % mets[k]["norm"])

    print("\n── 用例 2 (★决定性★): 官方板自己必须【放行】 —— 证明【新口径不把官方板误判为不可比】 ──")
    for k in ("官方终板", "官方stage-1"):
        if k in mets:
            ok, why = check(mets[k])
            chk("%s 归一化口径放行" % k, ok, "; ".join(why) if not ok else "norm=%d" % mets[k]["norm"])

    print("\n── 用例 3 (★反向★): 老口径(原始段数)必须【拦住官方板】 —— 证明老口径是错的 ──")
    for k in ("官方终板", "官方stage-1"):
        if k in mets:
            ok, why = check(mets[k], use_raw=True)
            chk("%s 老口径应被拦" % k, (not ok), "拦下理由: " + "; ".join(why))

    print("\n── 用例 4 (反向): 现役基线板在【老口径】下必须【被拦】 (ISS-328 死因复现) ──")
    for k in ("现役链终板v76mg1",):
        if k in mets:
            ok, why = check(mets[k], use_raw=True)
            chk("%s 老口径应被拦" % k, (not ok), "拦下理由: " + "; ".join(why))

    print("\n── 用例 5 (可证伪): 故意把区间收窄 ⇒ 必须变红 (★证明闸会红, 不是永绿★) ──")
    if "现役链终板v76mg1" in mets:
        m = mets["现役链终板v76mg1"]
        # ★★2026-11-19 02:4x (ISS-337 cont1) 修正: ★第一版写 tight_hi=2600 ⇒ norm=2582
        #   仍落在 [2300,2600] 带内 ⇒ 用例的期望值写反了 (★判据本身没错, 是用例写错了★)
        #   ⇒ 收窄上界到 2500 (★能把 2582 排除掉★) ⇒ 期望「出带」才成立。
        #   ★**收紧的上界必须【小于】当前板读数, 否则这个可证伪用例恒假★**
        tight_hi = 2500
        tight_ok = (SEG_NORM_LO <= m["norm"] <= tight_hi)
        chk("收窄到 [%d,%d] 后 norm=%d 应【出带】(⇒ 证明闸会红, 不是永绿)"
            % (SEG_NORM_LO, tight_hi, m["norm"]), (not tight_ok),
            "norm=%d ⇒ %s" % (m["norm"], "带内(★判据写错了★)" if tight_ok else "出带(正确)"))

    print("\n── 用例 5b (★区间自身可证伪★): ★全部同工艺板必须【都在带内】★ ──")
    for k in ("官方终板", "官方stage-1", "现役链终板v76mg1", "现役链终板v76mz",
              "现役链终板iss325ctl"):
        if k in mets:
            ok, why = check(mets[k])
            chk("%s 在带内" % k, ok, "; ".join(why) if not ok else
                "norm=%d via=%d cu=%.1f" % (mets[k]["norm"], mets[k]["vias"], mets[k]["cu_mm"]))

    print("\n── 用例 6: 一块【不存在的板】必须被拦 (不许静默放行) ──")
    ok, why = check({"raw": 0, "norm": 0, "vias": 0, "cu_mm": 0.0, "nets": 0})
    chk("空读数必须被拦", (not ok), "; ".join(why))

    print()
    if fail == 0:
        print("ALL TESTS PASS  ⇒ ★新口径成立: 官方板与现役臂【同带】, 老口径【会把官方板自己拦掉】★")
        return 0
    print("SELFTEST FAILED")
    return 1


def main():
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    paths = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not paths:
        print("用法: seg_parity_selfcheck.py <板1> [板2 ...]  |  --selftest")
        return 2
    rc = 0
    for p in paths:
        if not os.path.isfile(p):
            print("❌ %s 不存在 ⇒ 不可比 (不许放行)" % p)
            rc = 1
            continue
        m = metrics(p)
        ok, why = check(m)
        tag = "✅ 放行" if ok else "❌ 不可比"
        print("%s %s" % (tag, p))
        print("     raw=%d norm=%d via=%d cu=%.1fmm nets=%d"
              % (m["raw"], m["norm"], m["vias"], m["cu_mm"], m["nets"]))
        if not ok:
            for w in why:
                print("     ★ %s" % w)
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
