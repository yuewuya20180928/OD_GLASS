#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-251 · MECH 侧三处老账口径门禁 (充电耗散 / 铝 k / 检修口板宽)
======================================================================
用途: 机械判定「ISS-251 三处老账的**口径**有没有漂回去」——
      A. 充电耗散口径 = **buck** 0.45-0.57 W (代表值 0.50 W)   (ISS-216)
      B. 金属热路 k 口径 = **201 W/m·K** (6063-T6 官方保守侧)   (ISS-219)
      C. 检修口文档板宽口径 = **60×30** (套 A 基准)            (ISS-206 / ISS-251)

★**本脚本只判口径, 不判别的域**:
  · 空间/散热/重量的**数值对拍** = `MECH/verify_budget.py` 的活 (本脚本不重复算)
  · 板 / PCB / 网表 / BOM = **hw-lead 的地界** (本脚本一个字节不碰)
  · `MECH/check_demo_struct_truth.py` / `MECH/service_port_check.py` /
    `MECH/hinge_usb_check.py` = **受保护脚本**, 本脚本只**读**, 不改
  · 判定依据**全部是文本锚点** (常量值 / 文档行 / 出处串), 不含任何"应该能放下"式推断

★**判定规则 (三条通用律)**:
  R1 活口径常量必须**逐字等于**已定值 (不许"差不多"): 0.50 / 0.45-0.57 / 201.0 / 60×30 / 15.00 / 20.00
  R2 旧口径值**只许出现在已明确标注作废/订正/未迁的行里** (历史沿革可追溯, 但不许当活口径用)
  R3 每条口径必须带**依据出处** (厂商/官方出处 + 证据标签) ⇒ 删掉出处 ⇒ 门禁红

用法:
    cd projects/smart_glasses
    python3 MECH/check_budget_caliber.py             # 口径门禁 (rc=0 = 绿)
    python3 MECH/check_budget_caliber.py --selftest   # 反向用例 (改坏口径必须变红)

退出码: 0 = 全部口径一致 (门禁绿) / 2 = 有口径漂移 (门禁红) / 2 = 反向用例没抓全

作者: mech-lead (结构和散热) · 2026-11-16 ISS-251 续做轮
"""
from __future__ import annotations

import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)

F_VERIFY = os.path.join(HERE, "verify_budget.py")
F_BUDGET = os.path.join(HERE, "MECH_BUDGET.md")
F_SERVICE = os.path.join(HERE, "SERVICE_PORT_ISS092.md")
F_TEMPLATE = os.path.join(HERE, "ENDPOINT_METAL_PATH_MASS_TEMPLATE.md")

FILES = {
    "vb": (F_VERIFY, "MECH/verify_budget.py"),
    "budget": (F_BUDGET, "MECH/MECH_BUDGET.md"),
    "sp": (F_SERVICE, "MECH/SERVICE_PORT_ISS092.md"),
    "tpl": (F_TEMPLATE, "MECH/ENDPOINT_METAL_PATH_MASS_TEMPLATE.md"),
}

# ====================================================================== 通用律
# ★R2: 旧口径允许出现的条件 —— 该行必须明确写了"死/废/订正/未迁/迁移"
DEAD_MARKERS = (
    "判死", "作废", "已死", "旧口径", "不再适用", "历史沿革",   # ← verify_budget.py 同款 (C7/C11)
    "已订正", "未迁", "本单不改", "改到", "已改", "只留追溯", "已失效",
)

# ★A 组: 旧线性充电 IC 口径标记 (对板上真实器件 BQ25896 不适用, ISS-216 已判死)
LEGACY_LINEAR_MARKERS = (
    "线性充电 IC",
    "(5−4.2)V × 1A",
    "0.8 W @ 1A",
    "MP26029",
    "MP2710",
    "MP2721",
)

# ★C 组: 旧 15mm 板口径标记 (板宽 15 ⇒ 现行 30.00, ISS-206 已订正)
LEGACY_BOARD_MARKERS = (
    "板宽 15",
    "板宽15",
    "15mm 板",
    "board_width_15mm",
    "7.50 / 12.50",
    "+17.00",
)


def norm(text: str) -> str:
    """归一化: 各种减号/乘号/空白 ⇒ 统一字符, 免得"看着一样、字节不同"漏判。"""
    for a, b in (("−", "-"), ("–", "-"), ("—", "-"), ("×", "x"),
                 (" ", " "), ("　", " ")):
        text = text.replace(a, b)
    return text


def read(path: str) -> str:
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def load_all() -> dict:
    return {k: read(p) for k, (p, _rel) in FILES.items()}


def const(text: str, name: str):
    """从脚本源码里抠一个顶层常量 (按行匹配, 不用 import ⇒ 可被文本变异用例驱动)。

    ★允许行尾注释 (真实源码里 `K_AL_6063_T6 = 201.0   # W/m·K [官网] …` 这种)。"""
    m = re.search(rf"^{re.escape(name)}\s*=\s*([0-9.]+)\s*(?:#.*)?$", text, re.M)
    return float(m.group(1)) if m else None


def const_str(text: str, name: str):
    m = re.search(rf'^{re.escape(name)}\s*=\s*"([^"]*)"\s*(?:#.*)?$', text, re.M)
    return m.group(1) if m else None


def live_legacy_lines(text: str, markers) -> list:
    """找出"命中旧口径标记、但没标注已死/已废/已订正"的行 ⇒ 旧口径被当活口径用。"""
    out = []
    for line in text.splitlines():
        if not any(m in line for m in markers):
            continue
        if not any(d in line for d in DEAD_MARKERS):
            out.append(line.strip()[:130])
    return out


def has_line_with(text: str, *needles) -> bool:
    """存在**同一行**同时含全部 needles 的行。"""
    for line in text.splitlines():
        if all(n in line for n in needles):
            return True
    return False


def fixture_y_scan(text: str, tag: str, expected: float):
    """扫检修口文档里**夹具基准孔**的 Y 取值 (P2 ⇒ 15.00 / S2 ⇒ 20.00, 30mm 板套 A)。

    ★做法: 逐行找 `<tag>` 出现处, 取到**下一个基准孔标签**之间的片段, 抽 `Y=<数>` 形态的值。
      · 值 == 期望 ⇒ 现行基准, 合法;
      · 值 != 期望 ⇒ 只有在**上下文里有"旧"字样** (明确标成旧口径) 时才允许 ⇒ 否则 = 口径漂移。
    返回 (违规行列表, 命中现行值的个数)。
    """
    tags = ("P1", "P2", "S1", "S2")
    bad, good = [], 0
    pat_y = re.compile(r"Y=\**([0-9]+\.[0-9]+)\**")
    for line in text.splitlines():
        for m in re.finditer(rf"\b{tag}\b", line):
            seg_start = m.end()
            seg = line[seg_start:]
            cut = len(seg)
            for t in tags:
                if t == tag:
                    continue
                nxt = re.search(rf"\b{t}\b", seg)
                if nxt and nxt.start() < cut:
                    cut = nxt.start()
            seg = seg[:cut]
            for ym in pat_y.finditer(seg):
                val = float(ym.group(1))
                if abs(val - expected) < 1e-9:
                    good += 1
                else:
                    # 绝对位置: 值前面 70 字里必须有"旧" (明确标成旧口径) 才允许
                    abs_pos = seg_start + ym.start()
                    ctx = line[max(0, abs_pos - 70):abs_pos]
                    if "旧" not in ctx:
                        bad.append(f"{tag} Y={val} (期望 {expected:.2f}) @ {line.strip()[:110]}")
    return bad, good


# ====================================================================== 检查组
def caliber_checks(src: dict) -> list:
    """口径门禁组 (A1-A6 / B1-B6 / C1-C5)。返回 [(编号, 名称, ok, 明细)]。"""
    out = []
    vb = src.get("vb", "")
    budget = src.get("budget", "")
    sp = src.get("sp", "")
    tpl = src.get("tpl", "")
    nb, nsp, ntpl = norm(budget), norm(sp), norm(tpl)

    # ---------------------------------------------------------- A: 充电耗散口径 (buck)
    topo = const_str(vb, "CHG_TOPOLOGY")
    ic = const_str(vb, "CHG_IC")
    pch = const(vb, "P_CHARGE")
    mlohi = re.search(r"^P_CHARGE_LO,\s*P_CHARGE_HI\s*=\s*([0-9.]+),\s*([0-9.]+)\s*(?:#.*)?$",
                       vb, re.M)
    lo = float(mlohi.group(1)) if mlohi else None
    hi = float(mlohi.group(2)) if mlohi else None

    out.append(("A1", "脚本口径标识 = buck (不许漂回线性充电 IC 公式)",
                topo == "buck",
                f"CHG_TOPOLOGY={topo!r} (活口径必须是 'buck')"))
    out.append(("A2", "脚本充电器件 = BQ25896 (板上真实开关型充电 IC)",
                ic == "BQ25896",
                f"CHG_IC={ic!r} (实读网表 P10: U_CHG/SW/L_CHG/C_BST/PMID ⇒ 开关型)"))
    out.append(("A3", "活代表值 P_CHARGE = 0.50 W (ISS-213 机器门禁锚点, 逐字相等)",
                pch is not None and abs(pch - 0.50) < 1e-9,
                f"P_CHARGE={pch} W (必须 == 0.50)"))
    out.append(("A4", "已定耗散区间 = 0.45-0.57 W (ISS-213 §5.3 / ISS-089 自-4, 逐字相等)",
                lo is not None and abs(lo - 0.45) < 1e-9 and abs(hi - 0.57) < 1e-9,
                f"区间 = [{lo}, {hi}] W (必须 == [0.45, 0.57])"))

    row = ""
    for line in budget.splitlines():
        if "峰值" in line and "充电" in line and line.strip().startswith("|"):
            row = line
            break
    row_ok = bool(row) and all(s in row for s in ("BQ25896", "buck", "0.45-0.57", "Pin", "Pout"))
    out.append(("A5", "文档 §2.1 峰值充电行 = 真器件 + buck + 公式 + 新区间",
                row_ok,
                f"§2.1 行: {(row[:120] if row else '(找不到)')}"))

    live_a = live_legacy_lines(budget, LEGACY_LINEAR_MARKERS)
    out.append(("A6", "文档里旧线性口径标记只存在于已判死/作废的行 (不许当活口径)",
                not live_a,
                f"未标注作废的残留: {live_a or '无'}"))

    # ---------------------------------------------------------- B: 金属热路 k 口径 (201)
    k_live = const(vb, "K_AL_6063_T6")
    k_legacy = const(vb, "K_AL_6063_T6_LEGACY")
    out.append(("B1", "脚本活 k = 201.0 W/m·K (6063-T6 官方保守侧, 逐字相等)",
                k_live is not None and abs(k_live - 201.0) < 1e-9,
                f"K_AL_6063_T6={k_live} W/m·K (必须 == 201.0)"))
    out.append(("B2", "旧 k = 237 只作追溯保留 (常量还在, 但只许当 legacy)",
                k_legacy is not None and abs(k_legacy - 237.0) < 1e-9
                and "只留追溯" in vb,
                f"K_AL_6063_T6_LEGACY={k_legacy} W/m·K + 注释须含 '只留追溯'"))

    b_live = has_line_with(budget, "k=**201**", "[官网]")
    out.append(("B3", "MECH_BUDGET.md 活口径行 = k=**201** W/m·K 且带 [官网] 标签",
                b_live,
                "找到带 [官网] 的 k=**201** 活口径行" if b_live
                else "找不到带 [官网] 的 k=**201** 活口径行 (口径漂了或出处被删)"))

    live_b = live_legacy_lines(budget, ("237",))
    out.append(("B4", "MECH_BUDGET.md 里 237 只出现在已订正/旧口径行 (不许当活口径)",
                not live_b,
                f"未标注的 237 残留: {live_b or '无'}"))

    tpl_live = has_line_with(tpl, "现项目内口径", "201")
    tpl_legacy = has_line_with(tpl, "旧项目内口径", "237")
    out.append(("B5", "ENDPOINT_METAL_PATH_MASS_TEMPLATE.md 现口径 = 201 / 旧口径行 = 237",
                tpl_live and tpl_legacy,
                f"模板现口径行 201: {'有' if tpl_live else '无'} · 旧口径行 237: "
                f"{'有' if tpl_legacy else '无'}"))

    prov_vb = all(s in vb for s in ("Hydro", "Aalco", "Kaiser",
                                    "hydro.com", "aalco.co.uk", "kaiseraluminum.com"))
    prov_md = all(s in budget for s in ("Hydro EN AW-6063", "Aalco", "Kaiser", "[官网]"))
    out.append(("B6", "依据出处: k=201 必须带三家厂商互证 (Hydro/Aalco/Kaiser + 官网标签)",
                prov_vb and prov_md,
                f"脚本出处三链接: {'齐' if prov_vb else '缺'} · 文档出处串: {'齐' if prov_md else '缺'}"))

    # ---------------------------------------------------------- C: 检修口板宽口径 (60×30)
    c_board = has_line_with(sp, "| PCB |", "60 (L)", "30 (V)")
    out.append(("C1", "检修口文档板宽口径 = 60×30 (板长 60 / 板宽 30)",
                c_board,
                "§1 边界表 PCB 行 = 60 (L) × 30 (V) (现行)" if c_board
                else "找不到现行 60 (L) × 30 (V) 板口径行 (口径漂了)"))

    p2_bad, p2_good = fixture_y_scan(sp, "P2", 15.00)
    s2_bad, s2_good = fixture_y_scan(sp, "S2", 20.00)
    out.append(("C2", "夹具基准 = 30mm 板套 A (P2 Y=15.00 / S2 Y=20.00, 旧值只许标成旧口径)",
                (not p2_bad) and (not s2_bad) and p2_good >= 1 and s2_good >= 1,
                f"P2 现行命中 {p2_good} 次 / 违规 {p2_bad or '无'} · "
                f"S2 现行命中 {s2_good} 次 / 违规 {s2_bad or '无'}"))

    v_row = ""
    for line in sp.splitlines():
        if line.strip().startswith("| **V PCB 段**"):
            v_row = line
            break
    v_ok = bool(v_row) and all(s in v_row for s in ("36.00", "+2.00", "+1.40"))
    out.append(("C3", "§5.1 V PCB 段余量 = 需求 36.00 / 余 +2.00 / 最坏 +1.40",
                v_ok,
                f"§5.1 行: {(v_row[:130] if v_row else '(找不到)')}"))

    live_c = live_legacy_lines(sp, LEGACY_BOARD_MARKERS)
    out.append(("C4", "检修口文档里旧 15mm 板口径标记只存在于已作废/已订正/未迁的行",
                not live_c,
                f"未标注的旧口径残留: {live_c or '无'}"))

    c_src = ("BOARD_GEOM_30MM.md" in sp) and ("[官方]" in sp) and ("§3" in sp)
    out.append(("C5", "依据出处: 检修口基准必须指向 MECH/BOARD_GEOM_30MM.md §3 [官方]",
                c_src,
                f"指针 BOARD_GEOM_30MM.md: {'有' if 'BOARD_GEOM_30MM.md' in sp else '无'} · "
                f"[官方]: {'有' if '[官方]' in sp else '无'}"))

    return out


# ====================================================================== 跑
def hr(t):
    print("\n" + "=" * 78)
    print(t)
    print("=" * 78)


def run(src: dict | None = None, verbose: bool = True) -> dict:
    src = src if src is not None else load_all()
    checks = caliber_checks(src)
    bad = [c[0] for c in checks if not c[2]]
    if verbose:
        hr("ISS-251 口径门禁 —— 三处老账 (A 充电耗散 / B 铝 k / C 检修口板宽)")
        for cid, name, ok, det in checks:
            print(f"  {'✅' if ok else '❌'} {cid:<4} {name}")
            print(f"       {det}")
        hr("小结")
        print(f"  检查项 {len(checks)} | 通过 {len(checks) - len(bad)} | 红 {len(bad)}")
        if bad:
            print(f"  ❌ 门禁红: {bad}")
        else:
            print("  ✅ 门禁绿: 三处老账口径一致 (A=buck 0.50W · B=k201 官方保守侧 · C=60×30 套A)")
    return {"checks": checks, "bad": bad}


# ====================================================================== selftest
def _mutate(text: str, old: str, new: str) -> str:
    """文本变异 (只在内存里, **不碰盘上真文件**)。old 不存在 ⇒ 直接抛。"""
    if old not in text:
        raise AssertionError(f"★变异锚点没找到: {old!r}")
    return text.replace(old, new)


def selftest() -> int:
    """反向用例: 改坏任一口径锚点 ⇒ 必须变红。

    ★四类必测 (ISS-251 brief):
      ① 改回旧口径   ② 改数字   ③ 删依据出处   ④ 改文档数字
    """
    base = load_all()

    hr("ISS-251 口径门禁 —— 基线")
    base_res = run(base, verbose=False)
    base_bad = base_res["bad"]
    if base_bad:
        print(f"❌ 基线就不绿: {base_bad} ⇒ 门禁本身有问题, 自测不成立")
        for cid, name, ok, det in base_res["checks"]:
            if not ok:
                print(f"   ❌ {cid} {name} :: {det}")
        return 2
    print(f"  ✅ 基线全绿 (检查项 {len(base_res['checks'])}/{len(base_res['checks'])})")

    def case(name, expect, mutate):
        s = dict(base)
        mutate(s)
        red = run(s, verbose=False)["bad"]
        hit = expect in red
        print(f"  {'✅' if hit else '❌'} {name:<58} 期望红组 {expect:<5} 实际红组 {red or '无'}")
        return hit

    ok = 0
    n = 0

    # ---- ① 改回旧口径 ----
    n += 1
    ok += case("① 改回旧口径: 脚本 CHG_TOPOLOGY buck → linear",
               "A1",
               lambda s: s.__setitem__("vb", _mutate(s["vb"], 'CHG_TOPOLOGY = "buck"',
                                                     'CHG_TOPOLOGY = "linear"')))
    n += 1
    ok += case("① 改回旧口径: 文档 §2.1 行退回 线性充电 IC / 0.8W (未标作废)",
               "A6",
               lambda s: s.__setitem__("budget", _mutate(
                   s["budget"],
                   "**开关型 buck 充电 IC (BQ25896)** | **0.45-0.57 W** (代表值 **0.50 W**)",
                   "**线性充电 IC** | **0.8 W @ 1A**")))
    n += 1
    ok += case("① 改回旧口径: 文档 k=**201** → k=**237**",
               "B3",
               lambda s: s.__setitem__("budget", _mutate(s["budget"], "k=**201**", "k=**237**")))
    n += 1
    ok += case("① 改回旧口径: 检修口板口径 60×30 → 50×15 (旧 15mm 板)",
               "C1",
               lambda s: s.__setitem__("sp", _mutate(s["sp"], "60 (L) × 30 (V)", "50 (L) × 15 (V)")))

    # ---- ② 改数字 (脚本常量) ----
    n += 1
    ok += case("② 改数字: 脚本 P_CHARGE 0.50 → 0.55",
               "A3",
               lambda s: s.__setitem__("vb", _mutate(s["vb"], "P_CHARGE = 0.50", "P_CHARGE = 0.55")))
    n += 1
    ok += case("② 改数字: 脚本耗散区间 0.45-0.57 → 0.30-0.60",
               "A4",
               lambda s: s.__setitem__("vb", _mutate(
                   s["vb"], "P_CHARGE_LO, P_CHARGE_HI = 0.45, 0.57",
                   "P_CHARGE_LO, P_CHARGE_HI = 0.30, 0.60")))
    n += 1
    ok += case("② 改数字: 脚本 K_AL_6063_T6 201.0 → 237.0",
               "B1",
               lambda s: s.__setitem__("vb", _mutate(s["vb"], "K_AL_6063_T6 = 201.0",
                                                     "K_AL_6063_T6 = 237.0")))
    n += 1
    ok += case("② 改数字: 检修口夹具基准 P2 Y 15.00 → 7.50",
               "C2",
               lambda s: s.__setitem__("sp", _mutate(s["sp"], "Y=**15.00**", "Y=**7.50**")))

    # ---- ③ 删依据出处 ----
    n += 1
    ok += case("③ 删依据出处: 脚本里 Aalco 互证出处两行删掉",
               "B6",
               lambda s: s.__setitem__("vb", _mutate(
                   s["vb"],
                   "#   · Aalco: Aluminium Alloy 6063 - T6 Extrusions datasheet (Spec BS EN 755-2:2008)\n"
                   "#     https://www.aalco.co.uk/datasheets/Aluminium-Alloy-6063-T6-Extrusions_158.ashx\n",
                   "")))
    n += 1
    ok += case("③ 删依据出处: 检修口文档 BOARD_GEOM_30MM.md §3 指针全删",
               "C5",
               lambda s: s.__setitem__("sp", _mutate(s["sp"], "MECH/BOARD_GEOM_30MM.md", "")))

    # ---- ④ 改文档数字 ----
    n += 1
    ok += case("④ 改文档数字: §2.1 行区间 0.45-0.57 → 0.80-0.90",
               "A5",
               lambda s: s.__setitem__("budget", _mutate(s["budget"], "**0.45-0.57 W**",
                                                         "**0.80-0.90 W**")))
    n += 1
    ok += case("④ 改文档数字: §5.1 V PCB 段余量 +2.00/+1.40 → +17.00 (旧 15mm 板口径)",
               "C3",
               lambda s: s.__setitem__("sp", _mutate(
                   s["sp"], "**36.00** | 38.00 | **+2.00** | **+1.40**",
                   "**21.00** | 38.00 | **+17.00** | **+17.00**")))
    n += 1
    ok += case("④ 改文档数字: 文档里未标注的 237 残留 (拿掉旧口径/只留追溯标注)",
               "B4",
               lambda s: s.__setitem__("budget", _mutate(
                   s["budget"], "订正; 旧口径 237 只留追溯", "; 237")))

    print("-" * 78)
    print(f"反向用例: {ok}/{n} 抓到了")
    return 0 if ok == n else 2


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true", help="反向用例: 改坏任一口径锚点必须变红")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    res = run()
    return 2 if res["bad"] else 0


if __name__ == "__main__":
    sys.exit(main())
