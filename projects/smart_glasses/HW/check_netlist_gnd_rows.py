#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HW/check_netlist_gnd_rows.py —— ISS-366 新机器闸 ★「网表有没有独立的 net=GND 接地行」★

================================================================================
★为什么要有这道闸 (★ISS-366 实测出来的根因★) ★
  网表 CSV 的语义是「一行 = 一根连接」, 行里 `net` 栏写的是**这根连接属于哪个网**。
  · 板生成器 `state/gen_pcb_netlist_board.py::derive_pads()` 按 **(器件, 网名)** 去重登记裸端
  · 所以「器件的接地端」**只能**由一行 `net=GND` 的行来登记 ⇒
    ★★若某器件的接地行把 `net` 栏误写成**信号网名**, 该器件就只会登记到 1 个网 ⇒
    ★★板面只长出 1 个 land ⇒ **接地端物理不存在** ★★

  ★ISS-366 实测的 4 件 (★全部在 `HW/netlist_v1.csv` L183/L313/L318/L323★):
    `C_KEY_PWR` / `C_KEY_VM` / `C_KEY_VP` / `R_BAT_DET_2`
    ⇒ 板面各只有 1 个 land (脚表 pin2=GND 是对的 ⇒ **是板面错, 不是脚表错**)
    ⇒ 3 颗 100nF 去耦/消抖电容**接地端悬空** + `R_BAT_DET_2` **分压下臂未接地**
    ⇒ **这是能出厂的坏板**

  ★现有闸为什么没抓到 (★本闸存在的理由★) ★
    `state/check_pcb_nets.py` 的 C1/C3 比的是「**板面** vs **网表推导**」
    ⇒ ★两侧都按同一套 (器件,网名) 去重 ⇒ **同源错误互相抵消 ⇒ C1/C3 全绿** ★
    ⇒ 只有【本闸】才独立地从「网表文本本身」判定「有没有一条独立的 net=GND 接地行」

★判据 (★机器可判 · 不挂 md5 锚★) ★
  ★**共同前提**: 「伪网名」= `RAIL_*` / `NET_*` / 裸 `GND` (★它们是网别名, 不是器件★)
  ★**共同前提**: 「脚表有 GND 脚」= `HW/netlist_v1_pins.csv` 里该 ref 至少有一行 net=GND

  D1 ★**接地行必须是「有效接地行」**: 一条 `net=GND` 的行, 若它的 `ref` 是**真实器件**
     (非伪名), 则该 ref **必须**出现在本行的 node1/node2 里 ⇒ 否则「这行声称接地某器件,
     却没提到它」⇒ 红
     (★`ref` 本身是伪名的行 = 纯网别名声明行 (如 `RAIL_GND`), 不算缺陷 ⇒ 不报★)

  D2 ★**脚表⇄网表双向一致 (★本闸的主判据★)**: 凡脚表判定「该器件有 GND 脚」的器件,
     在 `HW/netlist_v1.csv` 里**必须**能找到一条 `net=GND` 且该器件出现在 node1/node2 的行
     ⇒ 否则 ★**脚表说有 GND 脚, 网表却没有接地行 ⇒ 板生成器按 (器件,网名) 去重时
     登记不出接地端 ⇒ 板面接地 land 物理缺失** ⇒ 红
     (★**这正是 ISS-366 实测的 4+1 件的形态**: `C_KEY_PWR`/`C_KEY_VM`/`C_KEY_VP`/
     `C_KEY_CAM`/`R_BAT_DET_2`★)

  D3 ★**信号行里的裸 GND 必须是「无接地行器件」的形态**: 若某条**非** `net=GND` 的行
     在 node1/node2 里写了裸 `GND`, 则本行涉及的那个**真实器件**必须**另有**一条
     `net=GND` 的接地行 ⇒ 否则 ★**这行是「把信号网当成接地行用」** ⇒ 红
     (★`Q1`/`Q2` 那种「源极接地」写法是**合法**的 (它们另有 net=GND 行) ⇒ 不报★)

  D4 ★**反向一致**: 凡 `net=GND` 行里出现的**真实器件**, 脚表里**必须**也有 GND 脚
     ⇒ 否则「网表接地了, 脚表却说没接」⇒ 两张表打架 ⇒ 红

★rc 语义 ★
  rc=0 ⇒ 全过 (★每件 2 脚器件都有独立接地行, 无空接地行, 无信号行乱写 GND★)
  rc=1 ⇒ 有缺陷 (逐条点名 ref + 行号 + 期望/实际)
  rc=2 ⇒ 用法/环境错误 (文件缺失等)

★自检 ★
  `python3 HW/check_netlist_gnd_rows.py --selftest`
  ⇒ ★每条反向用例都自证「红的是目标那一条, 其余仍绿」★

★★纪律 ★★
  ★只读: 本脚本**不写任何项目文件** (自检只动临时目录里的副本) ★
  ★不挂链: 本闸**不在** `state/gate_check.py` / `state/daily_check.py` / 任何 EXTRA_GATES 里
            (★挂不挂由 main 签收时定★)
"""
from __future__ import annotations

import argparse
import csv
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
CSV_PATH = os.path.join(HERE, "netlist_v1.csv")
PINS_PATH = os.path.join(HERE, "netlist_v1_pins.csv")

# ★网表里的伪网名 (★不算真实器件★)
PSEUDO_PREFIX = ("RAIL_", "NET_")
# ★2 脚无源件前缀 (★电阻/电容/电感/二极管★)
PASSIVE_2P = ("R_", "C_", "L_", "FB_", "D_")


def _is_pseudo(name: str) -> bool:
    n = (name or "").strip()
    return (not n) or n == "GND" or n.startswith(PSEUDO_PREFIX)


def _ref_of(node: str) -> str:
    """node 串 → 器件名 (★去掉 ' pinN' 后缀★)"""
    n = (node or "").strip()
    if not n:
        return ""
    return n.split(" ", 1)[0].strip()


def _read_csv(path: str) -> list[dict]:
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


class Finding:
    __slots__ = ("code", "ref", "line", "expect", "actual")

    def __init__(self, code: str, ref: str, line: int, expect: str, actual: str):
        self.code = code
        self.ref = ref
        self.line = line
        self.expect = expect
        self.actual = actual

    def __str__(self) -> str:
        return ("[%s] %s (CSV 第 %d 行): 期望 %s / 实际 %s"
                % (self.code, self.ref, self.line, self.expect, self.actual))


def collect_gnd_refs(rows: list[dict]) -> tuple[dict, dict]:
    """扫网表 → (net=GND 行里出现的器件 → 行号集合, 所有行里出现过的器件 → 行号集合)"""
    gnd_refs: dict[str, set] = {}
    all_refs: dict[str, set] = {}
    for i, r in enumerate(rows):
        ln = i + 2          # ★CSV 物理行号 (表头 = 第 1 行)★
        net = (r.get("net") or "").strip()
        refs_here = []
        for k in ("node1", "node2"):
            nm = _ref_of(r.get(k) or "")
            if nm and not _is_pseudo(nm):
                refs_here.append(nm)
        for nm in refs_here:
            all_refs.setdefault(nm, set()).add(ln)
        if net == "GND":
            for nm in refs_here:
                gnd_refs.setdefault(nm, set()).add(ln)
    return gnd_refs, all_refs


def run_checks(csv_path: str = CSV_PATH, pins_path: str = PINS_PATH) -> tuple[int, list]:
    findings: list[Finding] = []
    rows = _read_csv(csv_path)
    pins = _read_csv(pins_path) if os.path.exists(pins_path) else []

    # ---- 扫描网表: 收集 接地行 / 接地行里出现的器件 / 各器件出现的行号 ----
    gnd_rows_of: dict[str, set] = {}      # 器件 → 它出现在 net=GND 行的行号
    gnd_row_refs: list[tuple[int, str, list]] = []   # (行号, ref, node 里的真实器件)
    all_rows_of: dict[str, set] = {}      # 器件 → 它出现的所有行号
    sig_rows_with_gnd: list[tuple[int, str, list]] = []  # (行号, net, node 里的真实器件)
    for i, r in enumerate(rows):
        ln = i + 2                      # ★CSV 物理行号 (表头 = 第 1 行)★
        net = (r.get("net") or "").strip()
        devs = []
        for k in ("node1", "node2"):
            nm = _ref_of(r.get(k) or "")
            if nm and not _is_pseudo(nm):
                devs.append(nm)
        for nm in devs:
            all_rows_of.setdefault(nm, set()).add(ln)
        if net == "GND":
            for nm in devs:
                gnd_rows_of.setdefault(nm, set()).add(ln)
            gnd_row_refs.append((ln, _ref_of(r.get("ref") or ""), devs))
        else:
            if (r.get("node1") or "").strip() == "GND" or (r.get("node2") or "").strip() == "GND":
                sig_rows_with_gnd.append((ln, net, devs))

    # ---- 脚表: 哪些器件有 GND 脚 ----
    pin_gnd_refs: dict[str, set] = {}
    pin_all_refs: set = set()
    pin_dnp: dict[str, str] = {}
    for r in pins:
        ref = (r.get("ref") or "").strip()
        if not ref or _is_pseudo(ref):
            continue
        pin_all_refs.add(ref)
        pin_dnp.setdefault(ref, (r.get("dnp") or "").strip())
        if (r.get("net") or "").strip() == "GND":
            pin_gnd_refs.setdefault(ref, set()).add((r.get("pin") or "").strip())

    # ---------- D1: 接地行的 ref 是真实器件 ⇒ 必须在本行的 node 里 ----------
    for ln, ref, devs in gnd_row_refs:
        if not ref or _is_pseudo(ref):
            continue                      # ★纯网别名行 (RAIL_GND 之类) ⇒ 不算缺陷★
        if ref not in devs:
            findings.append(Finding(
                "D1", ref, ln,
                "net=GND 行声称接地 %s ⇒ %s 必须出现在本行 node1/node2" % (ref, ref),
                "本行 node 里只有 %s" % (devs,)))

    # ---------- D2: 脚表有 GND 脚 ⇒ 网表必须有独立接地行 ----------
    for ref, pin_ids in sorted(pin_gnd_refs.items()):
        if ref in gnd_rows_of:
            continue
        findings.append(Finding(
            "D2", ref, 0,
            "脚表里 %s 有 GND 脚 (%s) ⇒ 网表须有一条 net=GND 且含 %s 的行"
            % (ref, ",".join(sorted(pin_ids)), ref),
            "网表全表没有 net=GND 且含 %s 的行 ⇒ 板面不会长出接地 land" % ref))

    # ---------- D3: 信号行写裸 GND ⇒ 该器件必须另有 net=GND 行 ----------
    for ln, net, devs in sig_rows_with_gnd:
        for nm in devs:
            if nm in gnd_rows_of:
                continue                  # ★合法 (Q1/Q2 源极接地写法) ⇒ 不报★
            findings.append(Finding(
                "D3", nm, ln,
                "信号网 %s 的行里写了裸 GND ⇒ %s 必须另有独立的 net=GND 接地行" % (net, nm),
                "%s 没有 net=GND 行 ⇒ 接地端登记不出来 (板面缺接地 land)" % nm))

    # ---------- D4: 网表接地了 ⇒ 脚表也得有 GND 脚 ----------
    if not os.path.exists(pins_path):
        findings.append(Finding(
            "D4", "-", 0, "脚表存在 (%s)" % pins_path, "缺文件 ⇒ D2/D4 无法判定"))
    else:
        for ln, ref, devs in gnd_row_refs:
            for nm in devs:
                if nm in pin_gnd_refs:
                    continue
                if pin_dnp.get(nm) == "DNP":
                    # ★DNP 件: 脚表不列它的 GND 脚是**现状设计选择** (不装 ⇒ 不逐脚登记)
                    #   ⇒ 本闸只管【必装】件 ⇒ 不报 (★免得把 DNP 的现状差异算成缺陷★)
                    continue
                findings.append(Finding(
                    "D4", nm, ln,
                    "网表 net=GND 行接地了 %s ⇒ 脚表里 %s 也必须有 GND 脚" % (nm, nm),
                    "脚表里 %s 没有 GND 脚 ⇒ 两张表打架" % nm))

    if findings:
        findings.sort(key=lambda f: (f.code, f.line, f.ref))
        return 1, findings
    return 0, findings


def do_selftest() -> int:
    """★反向用例: 每条自证「红的是目标那一条, 其余仍绿」★"""
    tmpd = tempfile.mkdtemp(prefix="iss366_gnd_selftest_")
    try:
        base_csv = _read_csv(CSV_PATH)
        base_pins = _read_csv(PINS_PATH) if os.path.exists(PINS_PATH) else []

        def write_case(name: str, rows: list[dict], pins: list[dict] | None = None):
            d = os.path.join(tmpd, name)
            os.makedirs(d, exist_ok=True)
            cp = os.path.join(d, "netlist_v1.csv")
            pp = os.path.join(d, "netlist_v1_pins.csv")
            with open(cp, "w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
                w.writeheader()
                for r in rows:
                    w.writerow(r)
            with open(pp, "w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=list((pins or base_pins)[0].keys()))
                w.writeheader()
                for r in (pins if pins is not None else base_pins):
                    w.writerow(r)
            return cp, pp

        def mutate(rows: list[dict], fn):
            out = [dict(r) for r in rows]
            fn(out)
            return out

        cases = []

        # ---- M0: 基线 (现行网表) ⇒ 必须红, 且 D2 点名那 5 件 (4 必装 + C_KEY_CAM) ----
        rc0, f0 = run_checks(CSV_PATH, PINS_PATH)
        d0 = {f.ref for f in f0 if f.code == "D2"}
        want0 = {"C_KEY_PWR", "C_KEY_VM", "C_KEY_VP", "C_KEY_CAM", "R_BAT_DET_2"}
        cases.append((
            "M0", "基线网表 ⇒ D2 精确点名 5 件 (4 必装 + C_KEY_CAM)",
            rc0 == 1 and d0 == want0,
            "rc=%d, D2=%s" % (rc0, sorted(d0))))

        # ---- M1: 反向用例 = 把 5 件的接地行 net 栏改成 GND ⇒ 必须转绿 ----
        #   ★注意: 改 net 栏会让该行变成「net=GND, node1=<器件>, node2=GND」⇒ 合法接地行
        #   ★且 D3 (信号行写裸 GND) 也随之清掉 ⇒ rc 应为 0
        def fix5(out):
            for r in out:
                if r.get("ref") in want0 and (r.get("net") or "") != "GND":
                    r["net"] = "GND"
        cp, pp = write_case("m1", mutate(base_csv, fix5))
        rc1, f1 = run_checks(cp, pp)
        d1 = {f.ref for f in f1}
        cases.append((
            "M1", "★反向: 5 件接地行 net 栏改回 GND ⇒ 全部判据清 ⇒ rc=0",
            rc1 == 0 and not d1,
            "rc=%d, 残留=%s" % (rc1, sorted(d1))))

        # ---- M2: 反向用例 = 只修 1 件 (C_KEY_PWR) ⇒ 必须【只红那 4 件】, C_KEY_PWR 转绿 ----
        def fix1(out):
            for r in out:
                if r.get("ref") == "C_KEY_PWR" and (r.get("net") or "") != "GND":
                    r["net"] = "GND"
        cp, pp = write_case("m2", mutate(base_csv, fix1))
        rc2, f2 = run_checks(cp, pp)
        d2 = {f.ref for f in f2 if f.code == "D2"}
        want2 = want0 - {"C_KEY_PWR"}
        cases.append((
            "M2", "★反向: 只修 C_KEY_PWR ⇒ 红的【只有】另外 4 件, C_KEY_PWR 已绿",
            rc2 == 1 and d2 == want2 and "C_KEY_PWR" not in d2,
            "rc=%d, D2=%s" % (rc2, sorted(d2))))

        # ---- M3: 反向用例 = 注入一条「ref 是真实器件但不在 node 里」的接地行 ⇒ D1 必红 ----
        def bad_gnd_ref(out):
            r = dict(out[0])
            r.update({"net": "GND", "node1": "GND", "node2": "GND", "ref": "C_DET_BAT"})
            out.insert(0, r)
        cp, pp = write_case("m3", mutate(base_csv, bad_gnd_ref))
        rc3, f3 = run_checks(cp, pp)
        d1_hits = [f for f in f3 if f.code == "D1"]
        cases.append((
            "M3", "★反向: 接地行声称接地 C_DET_BAT 却没写它 ⇒ D1 必红 (且不掩盖 D2)",
            rc3 == 1 and d1_hits and any(f.code == "D2" for f in f3),
            "rc=%d, D1 命中 %d 条" % (rc3, len(d1_hits))))

        # ---- M4: 反向用例 = 在信号网行里写 GND 字面量 ⇒ D3 必红 ----
        def sig_gnd(out):
            for r in out:
                if r.get("net") == "KEY_PWR" and r.get("ref") == "C_KEY_PWR":
                    r["node2"] = "GND"
                    break
        cp, pp = write_case("m4", mutate(base_csv, sig_gnd))
        rc4, f4 = run_checks(cp, pp)
        d3_hits = [f for f in f4 if f.code == "D3"]
        cases.append((
            "M4", "★反向: 信号网行里写 GND ⇒ D3 必红 (且 D2 仍红)",
            rc4 == 1 and d3_hits and any(f.code == "D2" for f in f4),
            "rc=%d, D3 命中 %d 条" % (rc4, len(d3_hits))))

        # ---- M5: 反向用例 = 脚表说某件有 GND 脚, 网表却没有接地行 ⇒ D2 必须点名它 ----
        #   ★用 C_DET_BAT (★必装 + 脚表 pin2=GND + 网表 L185 有 net=GND 行★)
        #     ⇒ 删掉它的 net=GND 行 ⇒ 脚表仍说有 GND 脚, 网表却没有 ⇒ D2 必点名它
        def drop_gnd_row(out):
            out[:] = [r for r in out
                      if not (r.get("ref") == "C_DET_BAT" and (r.get("net") or "") == "GND")]
        cp, pp = write_case("m5", mutate(base_csv, drop_gnd_row))
        rc5, f5 = run_checks(cp, pp)
        d2_m5 = {f.ref for f in f5 if f.code == "D2"}
        cases.append((
            "M5", "★反向: 删掉 C_DET_BAT 的 net=GND 行 ⇒ D2 必点名它 (脚表仍说有 GND 脚)",
            rc5 == 1 and "C_DET_BAT" in d2_m5,
            "rc=%d, D2=%s" % (rc5, sorted(d2_m5))))

        # ---- M6: 反向用例 = 网表接地了但脚表说没接 ⇒ D4 必须红 ----
        #   ★把脚表里 C_DET_BAT 的 GND 脚改成别的网 ⇒ 网表还接地着 ⇒ 两表打架 ⇒ D4 红
        pins_m6 = [dict(r) for r in base_pins]
        for r in pins_m6:
            if r.get("ref") == "C_DET_BAT" and (r.get("net") or "") == "GND":
                r["net"] = "BAT_DET"      # ★脚表改成「没有 GND 脚」★
        cp, pp = write_case("m6", base_csv, pins_m6)
        rc6, f6 = run_checks(cp, pp)
        d4_hits = [f for f in f6 if f.code == "D4"]
        cases.append((
            "M6", "★反向: 脚表把 C_DET_BAT 的 GND 脚改掉 ⇒ D4 必红 (网表还接地着)",
            rc6 == 1 and d4_hits,
            "rc=%d, D4 命中 %d 条" % (rc6, len(d4_hits))))

        print("=" * 78)
        print("  ISS-366 机器闸 check_netlist_gnd_rows.py --selftest")
        print("=" * 78)
        ok = True
        for cid, desc, passed, detail in cases:
            flag = "PASS" if passed else "FAIL"
            if not passed:
                ok = False
            print("  [%s] %s :: %s" % (flag, cid, desc))
            print("         ⇒ %s" % detail)
        n_ok = sum(1 for c in cases if c[2])
        print("-" * 78)
        if ok:
            print("SELFTEST %d/%d 全过 (每条都自证「红的是目标那一条, 其余仍绿」)"
                  % (n_ok, len(cases)))
            print("ALL TESTS PASS")
            return 0
        print("SELFTEST %d/%d ★有失败★" % (n_ok, len(cases)))
        return 1
    finally:
        shutil.rmtree(tmpd, ignore_errors=True)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="ISS-366 网表独立 net=GND 接地行门禁")
    ap.add_argument("--selftest", action="store_true", help="跑反向用例自检")
    ap.add_argument("--csv", default=CSV_PATH, help="网表 CSV 路径")
    ap.add_argument("--pins", default=PINS_PATH, help="脚表 CSV 路径")
    args = ap.parse_args(argv)
    if args.selftest:
        return do_selftest()
    if not os.path.exists(args.csv):
        print("❌ 缺网表: %s" % args.csv, file=sys.stderr)
        return 2
    rc, findings = run_checks(args.csv, args.pins)
    print("=" * 78)
    print("  ISS-366 网表【独立 net=GND 接地行】门禁")
    print("  ★判据: D1 空接地行 / D2 脚表有 GND 脚但网表无接地行 / D3 信号行写 GND")
    print("=" * 78)
    if rc == 0:
        print("  ✅ 全过 —— 每件脚表带 GND 脚的器件, 网表里都有独立的 net=GND 接地行")
        print("     ⇒ 板生成器按 (器件,网名) 去重时, 这些器件能登记出 2 个裸端 ⇒ 接地 land 会出现")
    else:
        for f in findings:
            print("  ❌ %s" % f)
        print("-" * 78)
        print("  ❌ %d 条缺陷 ⇒ ★接地 land 会在板面缺失 ⇒ 电气损伤 (去耦失效 / 分压悬浮)★" % len(findings))
    return rc


if __name__ == "__main__":
    sys.exit(main())
