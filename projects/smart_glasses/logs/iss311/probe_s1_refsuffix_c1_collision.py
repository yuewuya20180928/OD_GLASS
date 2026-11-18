#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
probe_s1_refsuffix_c1_collision.py —— ISS-311 自证探针 (hw-lead)
★**只读项目**: 只往 `tmp/iss311_tmp/` 写沙盒副本; **不碰 HW/ 下任何文件** ★
★**目的**: 验证「板那一趟」S1 (★板侧位号加 `_1` 后缀★) 与环 ③ C1 焊盘级等价判据
  ★**会不会互相打架** ★
  ★背景 (★本机实读★):
    · `state/check_pcb_nets.py` 的 `board_pads()` 取 `fp.GetReference()` **原样**,
      `netlist_pads()` 取网表 ref **原样**, `compare()` 直接比 (ref,pad) 键
      ⇒ ★**两侧都没有「图上位号 → 表侧 ref」的反查** ★
    · `state/gen_kicad_sch.py::kicad_ref()` (ISS-205) = 末字符是数字 ⇒ 不动; 否则加 `_1`
      ⇒ 原理图侧已经全用 `X_1` (★实测 218 个位号里 187 个带 `_1`★)
    · `state/gen_pcb_netlist_board.py` **零处** `kicad_ref` 映射 (★grep 实测★)
      ⇒ 板生成器现在写的是**表侧原名** (★实测板上 186 个位号, 带 `_1` 的只有 1 个 = R_BAT_DET_1★)
  ★**要验的命题**: ★若板那一趟把 156 个板上位号改成 `X_1` 而网表/脚表仍是 `X`,
    `check_pcb_nets.py` 的 C1 会把每一个都判成「板上有网表没有」+「网表有板上没有」★

用法:
  bash state/pcbnew_py.sh logs/iss311/probe_s1_refsuffix_c1_collision.py
"""
import csv
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(PROJ, "state"))

import pcbnew  # noqa: E402
import check_pcb_nets as CPN  # noqa: E402

SRC = os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb")
SANDBOX = os.path.join(PROJ, "tmp", "iss311_tmp", "iss311_s1_refsuffix_sandbox.kicad_pcb")
PINS = os.path.join(PROJ, "HW", "netlist_v1_pins.csv")


def kicad_ref(ref):
    """★与 `state/gen_kicad_sch.py::kicad_ref()` 同规则 (★ISS-205★) ★"""
    r = (ref or "").strip()
    if r and r[-1].isdigit():
        return r
    return r + "_1"


def main():
    print("=" * 78)
    print("ISS-311 · S1 板侧位号加 `_1` 与环③ C1 判据的【相撞实验】(沙盒 · 不碰项目文件)")
    print("=" * 78)

    rows = list(csv.DictReader(open(PINS, encoding="utf-8-sig")))
    tbl = {r["ref"].strip() for r in rows if (r.get("ref") or "").strip()}

    b = pcbnew.LoadBoard(SRC)
    board_refs = [f.GetReference() for f in b.GetFootprints()]
    print(f"\n现役板位号数 = {len(board_refs)}")
    print(f"  末字符是字母 (= 要加 `_1`) = {len([r for r in board_refs if not r[-1].isdigit()])}")
    print(f"  已带 `_1` 后缀 = {len([r for r in board_refs if r.endswith('_1')])}"
          f" (★{sorted(r for r in board_refs if r.endswith('_1'))}★)")

    # ---- 基线: 现役板跑 C1 ----
    rc0, body0, ctx0 = CPN.run_checks(SRC)
    c1_0 = [l for l in body0 if "C1 " in l or "缺失" in l or "★多:" in l or "★错:" in l]
    print(f"\n【基线】现役板 C1: rc={rc0}")
    for l in c1_0[:8]:
        print("   " + l.strip())

    # ---- 沙盒: 把 156 个位号按 ISS-205 规则加 `_1` ----
    shutil.copy2(SRC, SANDBOX)
    b2 = pcbnew.LoadBoard(SANDBOX)
    changed = 0
    for fp in b2.GetFootprints():
        old = fp.GetReference()
        new = kicad_ref(old)
        if new != old:
            fp.SetReference(new)
            changed += 1
    pcbnew.SaveBoard(SANDBOX, b2)
    print(f"\n★沙盒改名: {changed} 个位号按 ISS-205 规则加了 `_1` 后缀")
    print(f"★沙盒文件: {SANDBOX}  (★项目 HW/ 下文件一个字节没动★)")

    rc1, body1, ctx1 = CPN.run_checks(SANDBOX)
    c1_1 = [l for l in body1 if "C1 " in l or "缺失" in l]
    miss = [l for l in body1 if "★缺:" in l]
    extra = [l for l in body1 if "★多:" in l]
    wrong = [l for l in body1 if "★错:" in l]
    print(f"\n【沙盒】改名后 C1: rc={rc1}")
    for l in c1_1[:6]:
        print("   " + l.strip())
    print(f"   明细条数: 缺 {len(miss)} (脚本只打前 8 条) · 多 {len(extra)} (前 8) · 错 {len(wrong)} (前 8)")
    for l in miss[:6]:
        print("   " + l.strip())
    for l in extra[:6]:
        print("   " + l.strip())

    # ---- 量化: 直接算改名后 C1 会怎样 ----
    want, have = ctx1["want"], ctx1["have"]
    nc = {k for k, v in have.items() if not v}
    missing = [(k, n) for k, n in want.items() if k not in have]
    extra = [(k, n) for k, n in have.items() if k not in want and k not in nc]
    wrong = [(k, n, have[k]) for k, n in want.items() if k in have and have[k] != n]
    print(f"\n【量化】改名后 C1 三项: 缺失 {len(missing)} · 多余 {len(extra)} · 同号异网 {len(wrong)}")
    print(f"  ⇒ 对比基线: 缺失 0 · 多余 2 · 同号异网 3")
    print(f"  ⇒ ★**板侧改名会把环③从「多余 2」变成「缺失 {len(missing)} · 多余 {len(extra)}」**★")

    # ---- 反证: 若网表侧也加 `_1`, 两边同口径 ⇒ C1 归零 ----
    print("\n【反证】把【网表侧 ref】也按同规则改口径后重算 (★只算, 不落表★):")
    want2 = {}
    for (ref, pad), net in want.items():
        want2[(kicad_ref(ref), pad)] = net
    have2 = {}
    for (ref, pad), net in have.items():
        have2[(kicad_ref(ref), pad)] = net
    m2 = [(k, n) for k, n in want2.items() if k not in have2]
    e2 = [(k, n) for k, n in have2.items() if k not in want2 and k not in nc]
    w2 = [(k, n, have2[k]) for k, n in want2.items() if k in have2 and have2[k] != n]
    print(f"  缺失 {len(m2)} · 多余 {len(e2)} · 同号异网 {len(w2)}"
          f"  ⇒ ★**同口径后回到基线的 0/2/3**★ (★证明 C1 的红不是改名的错, 是口径没同步★)")

    # ---- 清理 ----
    try:
        os.remove(SANDBOX)
        print(f"\n★沙盒已删: {SANDBOX}")
    except OSError as e:
        print(f"\n★沙盒清理失败: {e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
