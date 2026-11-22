#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-174 机器门禁 —— 触控中断 (TP_INT) 连通性缺口复核
================================================================================
★**本脚本只读**: 不写任何项目文件 (自检用临时目录, 绝不碰仓库里的真文件)。

★**它守的是「ISS-174 判真伪的结论 + 规格里点名的候选脚」这两件事**:

  ① `CONN_LIGHT` 的 22 个脚在网表里各自连到什么 (逐脚给行号)
  ② `NET_TP_INT` / `TP_RESET` 的现状 (存在与否 + 落点)
  ③ `HW/PCB/som_pin_assign.json` 的 GPIO 池剩余可用脚数
  ④ 规格里点名的候选脚 (J_SOM_P4 pin62 等) 确实在网表里空着

★**rc 语义**:
  - `rc=0` ⇒ 现状与 `HW/PCB/TP_INT_REMAP_SPEC.md` 的规格一致
  - `rc=1` ⇒ 不一致, 并**点名**是哪一条 (哪一脚 / 哪个网 / 哪个候选脚被占了)
  - `rc=2` ⇒ 用法/环境错误 (文件缺失等)

★**为什么 rc=1 要点名而不是只报个错**: 本项目 2026-11-03 换屏那次
(`Radxa 8HD 39p` → `Waveshare 2.8" 22p`) 就是因为「issue 描述的旧架构没人清」
⇒ 同一类事故的机械防线就在这里。

用法:
    python3 HW/check_tp_int_gap.py             # 复核, rc=0 = 一致
    python3 HW/check_tp_int_gap.py --verbose   # 打印 22 脚全表 + 候选池明细
    python3 HW/check_tp_int_gap.py --selftest  # 自检 (>=2 用例, 改临时副本)
    python3 HW/check_tp_int_gap.py --root DIR   # 指定工程根 (自检/复现用)
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ROOT = os.path.dirname(HERE)  # HW/ 的上一级 = 工程根

# ─────────────────────────────────────────────────────────────────────────────
# ★基准 (★全部来自 HW/PCB/TP_INT_REMAP_SPEC.md 的判真伪结论; 改了规格就要改这里★)
# ─────────────────────────────────────────────────────────────────────────────

#: `CONN_LIGHT` 22 脚在 `HW/netlist_v1_pins.csv` 里**应当**连到的网
#: ★来源: HW/netlist_v1_pins.csv 第 36..57 行 (实测) + HW/PCB/PI5_DSI_22P_PINOUT.md §3
EXPECTED_CONN_LIGHT: dict[int, str] = {
    1: "GND", 2: "DSI_D0_D1_N", 3: "DSI_D0_D1_P", 4: "GND",
    5: "DSI_D0_CK_N", 6: "DSI_D0_CK_P", 7: "GND", 8: "DSI_D0_D0_N",
    9: "DSI_D0_D0_P", 10: "GND", 11: "I2C_B_SCL", 12: "I2C_B_SDA",
    13: "GND", 14: "LIGHT_3V3", 15: "LIGHT_3V3", 16: "DSI_D0_D2_N",
    17: "DSI_D0_D2_P", 18: "DSI_D0_D3_N", 19: "DSI_D0_D3_P", 20: "GND",
    21: "GND", 22: "GND",
}

#: ★**现行架构下【不得存在】的网名** (判真伪结论 (b)/(c): 屏侧 22p 座无触控/复位脚)
#: `TP_RESET` 也不许是网名 —— 它在现行网表里是**测试点位号**, 属 `RESET_N` 链
FORBIDDEN_NETS = ("NET_TP_INT", "TP_INT", "NET_TP_RESET", "TP_RESET")

#: `TP_RESET` 这个**位号**在现行网表里必须挂在 `RESET_N` 上 (SoM 复位链的测试点)
EXPECTED_TP_RESET_NET = "RESET_N"

#: ★规格里点名的候选脚 (SoM 侧预留给"带独立触控中断脚的屏"的 GPIO)
#: ★主选 = P4_62 (GPIO2_D7_z, ball B7) ★备选 = 下面 5 个 ★
#: ★它们**必须**在网表里空着 —— 一旦被占, 说明别人拿走了这个预留位
PRIMARY_CANDIDATE = ("P4", 62)
CANDIDATE_PINS: tuple[tuple[str, int], ...] = (
    ("P4", 62), ("P4", 60), ("P4", 58), ("P4", 56), ("P4", 54), ("P4", 52),
)

#: `som_pin_assign.json` 之外**还**要扣除的官方「不可用」标记 (Forlinx 手册原文)
UNAVAILABLE_MARK = "not available"

#: ★基准池容量 (★实测于 2026-11-15: P4=22 / P1=13 / P2=1 / P3=0 ⇒ 合计 36★)
EXPECTED_FREE_POOL = 36
EXPECTED_FREE_POOL_BY_CONN = {"P1": 13, "P2": 1, "P4": 22, "P3": 0}

REL = {
    "netlist": os.path.join("HW", "netlist_v1.csv"),
    "pins": os.path.join("HW", "netlist_v1_pins.csv"),
    "assign": os.path.join("HW", "PCB", "som_pin_assign.json"),
    "sompins": os.path.join("HW", "PCB", "FET3572C_PIN_TABLE.csv"),
}


class CheckError(Exception):
    """rc=2: 环境/用法错误"""


def _path(root: str, key: str) -> str:
    return os.path.join(root, REL[key])


def _read_csv(path: str) -> list[dict]:
    if not os.path.exists(path):
        raise CheckError(f"★缺文件: {path}")
    with open(path, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _read_rows(path: str) -> list[dict]:
    """带行号 (CSV 物理行号, 1-based, 表头 = 第 1 行) 的读取。"""
    rows = _read_csv(path)
    out = []
    for i, r in enumerate(rows):
        r = dict(r)
        r["_line"] = i + 2  # 表头占第 1 行
        out.append(r)
    return out


# ─────────────────────────────────────────────────────────────────────────────
# 各项检查
# ─────────────────────────────────────────────────────────────────────────────

def check_conn_light(root: str, verbose: bool) -> tuple[list[str], list[str]]:
    """① CONN_LIGHT 22 脚落点全表 + 一致性。返回 (errors, report_lines)。"""
    errors: list[str] = []
    report: list[str] = []
    rows = _read_rows(_path(root, "pins"))

    got: dict[int, tuple[str, int]] = {}
    for r in rows:
        if (r.get("ref") or "").strip() != "CONN_LIGHT":
            continue
        raw = (r.get("pin") or "").strip()
        m = re.fullmatch(r"pin(\d+)", raw)
        if not m:
            continue
        p = int(m.group(1))
        if p in got:
            errors.append(
                f"★CONN_LIGHT pin{p} 在 {REL['pins']} 出现多次 "
                f"(行 {got[p][1]} 与 {r['_line']}) ⇒ 脚位表自相矛盾")
            continue
        got[p] = ((r.get("net") or "").strip(), r["_line"])

    if verbose:
        report.append(f"── ① CONN_LIGHT 22 脚落点全表 (来源 {REL['pins']}) ──")
    for p in range(1, 23):
        exp = EXPECTED_CONN_LIGHT[p]
        if p not in got:
            errors.append(f"★CONN_LIGHT pin{p} 在 {REL['pins']} 里**找不到** ⇒ 22 脚表不齐")
            if verbose:
                report.append(f"   pin{p:<2} = <缺失>   (期望 {exp})")
            continue
        net, line = got[p]
        flag = "OK" if net == exp else "★★不一致★★"
        if net != exp:
            errors.append(
                f"★CONN_LIGHT pin{p} 实际网名 = {net!r} (行 {line}), 期望 {exp!r} "
                f"⇒ 与 HW/PCB/TP_INT_REMAP_SPEC.md §2 不符")
        if verbose:
            report.append(f"   pin{p:<2} = {net:<14} 行 {line:<4} 期望 {exp:<14} {flag}")

    extra = sorted(set(got) - set(range(1, 23)))
    if extra:
        errors.append(f"★CONN_LIGHT 出现表外的脚: {extra} ⇒ 座型或针序被改过")
    return errors, report


def check_tp_int(root: str, verbose: bool) -> tuple[list[str], list[str]]:
    """② NET_TP_INT / TP_RESET 现状。返回 (errors, report_lines)。"""
    errors: list[str] = []
    report: list[str] = []

    net_rows = _read_rows(_path(root, "netlist"))
    pin_rows = _read_rows(_path(root, "pins"))

    net_names: dict[str, list[int]] = {}
    for r in net_rows:
        n = (r.get("net") or "").strip()
        net_names.setdefault(n, []).append(r["_line"])
    for r in pin_rows:
        n = (r.get("net") or "").strip()
        net_names.setdefault(n, []).append(r["_line"])

    if verbose:
        report.append(f"── ② NET_TP_INT / TP_RESET 现状 ──")
    for bad in FORBIDDEN_NETS:
        if bad in net_names:
            lines = sorted(set(net_names[bad]))
            errors.append(
                f"★网名 {bad!r} 现在**存在** (行 {lines}) ⇒ 现行架构 (22p 屏座) 不该有它; "
                f"若确要接 TP_INT ⇒ 必须先改 HW/PCB/TP_INT_REMAP_SPEC.md 并走整链重出")
            if verbose:
                report.append(f"   {bad:<14} 存在 (行 {lines})  ★应不存在★")
        elif verbose:
            report.append(f"   {bad:<14} 不存在  OK")

    # TP_RESET 作为「位号」必须挂在 RESET_N 上
    tp_refs = [r for r in pin_rows if (r.get("ref") or "").strip() == "TP_RESET"]
    if not tp_refs:
        errors.append(f"★位号 TP_RESET 在 {REL['pins']} 里找不到 ⇒ 规格里的复位链测试点没了")
    else:
        for r in tp_refs:
            net = (r.get("net") or "").strip()
            if net != EXPECTED_TP_RESET_NET:
                errors.append(
                    f"★位号 TP_RESET 现在挂在网 {net!r} (行 {r['_line']}), "
                    f"期望 {EXPECTED_TP_RESET_NET!r} ⇒ TP_RESET 是 SoM 复位链的测试点, 不是屏复位线")
            if verbose:
                report.append(f"   TP_RESET (位号) 行 {r['_line']} 挂网 = {net}  "
                              f"{'OK' if net == EXPECTED_TP_RESET_NET else '★★不一致★★'}")
    return errors, report


def check_pool(root: str, verbose: bool) -> tuple[list[str], list[str], list[tuple[str, int]]]:
    """③ GPIO 池剩余可用脚数 (+ 池成员)。返回 (errors, report_lines, pool)。"""
    errors: list[str] = []
    report: list[str] = []

    som = _read_csv(_path(root, "sompins"))
    with open(_path(root, "assign"), encoding="utf-8") as fh:
        asg = json.load(fh)

    assigned: set[tuple[str, int]] = set()
    for v in asg.get("assign", {}).values():
        assigned.add((v["conn"], int(v["num"])))
    fixed: set[tuple[str, int]] = set()
    for v in asg.get("fixed", {}).values():
        for tok in (v if isinstance(v, list) else [v]):
            p, n = tok.split("_")
            fixed.add((p, int(n)))

    used: dict[tuple[str, int], set[int]] = {}
    for r in _read_rows(_path(root, "netlist")):
        for node in (r.get("node1") or "", r.get("node2") or ""):
            for m in re.finditer(r"J_SOM_(P[1-4])\s+pin(\d+)", node):
                used.setdefault((m.group(1), int(m.group(2))), set()).add(r["_line"])

    pool: list[tuple[str, int]] = []
    for r in som:
        conn = (r.get("conn") or "").strip()
        if conn not in ("P1", "P2", "P3", "P4"):
            continue
        key = (conn, int(r["num"]))
        if key in assigned or key in fixed or used.get(key):
            continue
        if UNAVAILABLE_MARK in (r.get("desc") or "").lower():
            continue
        if not re.fullmatch(r"(GPIO[0-3]_[A-D][0-7])(?:_[duz])?", (r.get("gpio") or "").strip()):
            continue
        if "3.3V" not in (r.get("vol") or ""):
            continue
        pool.append(key)
    pool.sort()

    by_conn: dict[str, int] = {}
    for c, _ in pool:
        by_conn[c] = by_conn.get(c, 0) + 1

    if verbose:
        report.append("── ③ SoM GPIO 池 (空闲 / 3.3V / 官方可用) ──")
        report.append(f"   合计 = {len(pool)}   分座 = "
                      f"{ {c: by_conn.get(c, 0) for c in ('P1', 'P2', 'P3', 'P4')} }")

    if len(pool) != EXPECTED_FREE_POOL:
        errors.append(
            f"★GPIO 池剩余可用脚数 = {len(pool)}, 规格基准 = {EXPECTED_FREE_POOL} "
            f"(差 {len(pool) - EXPECTED_FREE_POOL:+d}) ⇒ 有脚被占用了 (或规格该更新)")
    for c, exp in EXPECTED_FREE_POOL_BY_CONN.items():
        got = by_conn.get(c, 0)
        if got != exp:
            errors.append(f"★GPIO 池 {c} 座可用脚数 = {got}, 规格基准 = {exp}")
    return errors, report, pool


def check_candidates(root: str, pool: list[tuple[str, int]], verbose: bool) -> tuple[list[str], list[str]]:
    """④ 规格点名的候选脚确实空着。返回 (errors, report_lines)。"""
    errors: list[str] = []
    report: list[str] = []

    net_rows = _read_rows(_path(root, "netlist"))
    pin_rows = _read_rows(_path(root, "pins"))

    def hits(conn: str, num: int) -> list[int]:
        pat = re.compile(rf"J_SOM_{conn}\s+pin{num}(?!\d)")
        out = []
        for r in net_rows:
            for node in (r.get("node1") or "", r.get("node2") or ""):
                if pat.search(node):
                    out.append(r["_line"])
                    break
        for r in pin_rows:
            if (r.get("ref") or "").strip() == f"J_SOM_{conn}" and (r.get("pin") or "").strip() == f"pin{num}":
                out.append(r["_line"])
        return sorted(set(out))

    if verbose:
        report.append("── ④ 规格点名的候选脚 (必须空着) ──")
    for conn, num in CANDIDATE_PINS:
        h = hits(conn, num)
        in_pool = (conn, num) in pool
        mark = "★主选★" if (conn, num) == PRIMARY_CANDIDATE else "备选"
        if h:
            errors.append(
                f"★候选脚 J_SOM_{conn} pin{num} ({mark}) 已被占用 (行 {h}) "
                f"⇒ 预留位被抢; 要换脚就改 HW/PCB/TP_INT_REMAP_SPEC.md §3 并重跑本门禁")
        if not in_pool:
            errors.append(f"★候选脚 J_SOM_{conn} pin{num} ({mark}) 不在空闲 GPIO 池里 ⇒ 池/候选表不一致")
        if verbose:
            report.append(f"   J_SOM_{conn} pin{num:<3} {mark}  占用行={h or '无'}  "
                          f"在池={'是' if in_pool else '否'}")
    return errors, report


# ─────────────────────────────────────────────────────────────────────────────
# 主流程
# ─────────────────────────────────────────────────────────────────────────────

def run_check(root: str, verbose: bool = False) -> tuple[int, list[str]]:
    errors: list[str] = []
    report: list[str] = []
    try:
        e, r = check_conn_light(root, verbose); errors += e; report += r
        e, r = check_tp_int(root, verbose); errors += e; report += r
        e, r, pool = check_pool(root, verbose); errors += e; report += r
        e, r = check_candidates(root, pool, verbose); errors += e; report += r
    except CheckError as exc:
        return 2, [str(exc)]

    if report:
        print("\n".join(report))
    if errors:
        print("\n★★ rc=1: 现状与 HW/PCB/TP_INT_REMAP_SPEC.md 不一致 (%d 条) ★★" % len(errors))
        for i, msg in enumerate(errors, 1):
            print(f"  [{i}] {msg}")
        return 1, errors
    print("\n✅ rc=0: 现状与 HW/PCB/TP_INT_REMAP_SPEC.md 一致 "
          f"(CONN_LIGHT 22 脚齐 / 无 TP_INT 网 / TP_RESET 仍挂 RESET_N / "
          f"GPIO 池 {EXPECTED_FREE_POOL} 脚 / 候选脚全空)")
    return 0, errors


# ─────────────────────────────────────────────────────────────────────────────
# 自检 (--selftest): 用临时副本注入假占用, 必须被抓出来
# ─────────────────────────────────────────────────────────────────────────────

def _copy_fixture(root: str, dst: str) -> str:
    for rel in REL.values():
        src = os.path.join(root, rel)
        if not os.path.exists(src):
            raise CheckError(f"★缺文件: {src}")
        d = os.path.join(dst, rel)
        os.makedirs(os.path.dirname(d), exist_ok=True)
        shutil.copy2(src, d)
    return dst


def _run_case(name: str, root: str, mutate, expect_rc: int, expect_kw: str) -> tuple[bool, str]:
    tmp = tempfile.mkdtemp(prefix="tpint_selftest_")
    try:
        _copy_fixture(root, tmp)
        mutate(tmp)
        rc, errs = run_check(tmp, verbose=False)
        blob = "\n".join(errs)
        ok = (rc == expect_rc) and (expect_kw in blob)
        detail = f"rc={rc} (期望 {expect_rc}); 抓到的信息含 {expect_kw!r}: {expect_kw in blob}"
        return ok, f"{name}: {detail}"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def selftest(root: str) -> int:
    print("── ISS-174 门禁自检 (用临时副本, 绝不改仓库文件) ──")
    cases: list[tuple] = []

    # 用例 0: 基线必须是干净的 (rc=0) —— 否则后面的「抓到」没有意义
    tmp = tempfile.mkdtemp(prefix="tpint_selftest_")
    try:
        _copy_fixture(root, tmp)
        rc, _ = run_check(tmp, verbose=False)
        cases.append((rc == 0, f"用例0 基线干净: rc={rc} (期望 0)"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 用例 1: 故意塞一条假占用 —— 主选脚 J_SOM_P4 pin62 被别人拿去挂网
    def mutate_occupancy(tmp: str) -> None:
        p = os.path.join(tmp, REL["netlist"])
        with open(p, encoding="utf-8") as fh:
            txt = fh.read()
        txt += ('P4,FAKE_TP_INT,J_SOM_P4 pin62,CONN_LIGHT pin22,NET_FAKE_TP_INT,'
                'FAKE,NET,必装,[推算],,"★自检注入的假占用",,MAIN_PCB,,\n')
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(txt)
    cases.append(_run_case("用例1 假占用(主选脚 J_SOM_P4 pin62 被占)", root,
                            mutate_occupancy, 1, "J_SOM_P4 pin62"))

    # 用例 2: 故意塞一条 TP_INT 网 —— 违背「现行架构无触控中断脚」结论
    def mutate_tpint_net(tmp: str) -> None:
        p = os.path.join(tmp, REL["netlist"])
        with open(p, encoding="utf-8") as fh:
            txt = fh.read()
        txt += ('P4,NET_TP_INT,J_SOM_P4 pin62,CONN_LIGHT pin22,NET_TP_INT,'
                'TP_INT,NET,必装,[推算],,"★自检注入的假 TP_INT 网",,MAIN_PCB,,\n')
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(txt)
    cases.append(_run_case("用例2 假 TP_INT 网名凭空出现", root,
                            mutate_tpint_net, 1, "NET_TP_INT"))

    # 用例 3: 把 CONN_LIGHT pin22 从 GND 改成别的网 ⇒ 22 脚表对不上
    def mutate_cl_pin(tmp: str) -> None:
        p = os.path.join(tmp, REL["pins"])
        with open(p, encoding="utf-8") as fh:
            txt = fh.read()
        txt = txt.replace("CONN_LIGHT.pin22,GND,CONN_LIGHT,pin22,P4,GND,",
                          "CONN_LIGHT.pin22,DSI_D0_D3_P,CONN_LIGHT,pin22,P4,GND,")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(txt)
    cases.append(_run_case("用例3 CONN_LIGHT pin22 被改网名", root,
                            mutate_cl_pin, 1, "CONN_LIGHT pin22"))

    # 用例 4: 把候选脚从池里吃掉 (占掉一个备选 P4_60) ⇒ 池容量对不上
    def mutate_pool(tmp: str) -> None:
        p = os.path.join(tmp, REL["netlist"])
        with open(p, encoding="utf-8") as fh:
            txt = fh.read()
        txt += ('P4,FAKE2,J_SOM_P4 pin60,R_PU_RESET_N,NET_FAKE2,FAKE,NET,必装,[推算],,'
                '"★自检注入的假占用",,MAIN_PCB,,\n')
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(txt)
    cases.append(_run_case("用例4 备选脚 J_SOM_P4 pin60 被占 ⇒ 池容量 -1", root,
                            mutate_pool, 1, "J_SOM_P4 pin60"))

    failed = 0
    for ok, msg in cases:
        print(("  ✅ " if ok else "  ❌ ") + msg)
        if not ok:
            failed += 1
    print(f"\n{'✅' if failed == 0 else '❌'} 自检: {len(cases) - failed}/{len(cases)} 通过")
    return 0 if failed == 0 else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="ISS-174 TP_INT 连通性缺口门禁")
    ap.add_argument("--root", default=DEFAULT_ROOT, help="工程根目录 (默认 = 本文件的上级)")
    ap.add_argument("--selftest", action="store_true", help="跑自检 (>=2 用例, 用临时副本)")
    ap.add_argument("--verbose", "-v", action="store_true", help="打印 22 脚全表 + 候选池明细")
    args = ap.parse_args(argv)

    root = os.path.abspath(args.root)
    if args.selftest:
        return selftest(root)
    try:
        rc, _ = run_check(root, verbose=args.verbose)
    except CheckError as exc:
        print(f"★rc=2: {exc}", file=sys.stderr)
        return 2
    return rc


if __name__ == "__main__":
    sys.exit(main())
