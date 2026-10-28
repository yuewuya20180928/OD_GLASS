#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_netlist.py 判据自测 —— "同一 net 不得有多个输出驱动" (2026-10-28)
====================================================================
背景:
  V1.9 改 Q_PG (N-MOS → P-MOS 高边开关) 时, 我在 note 里写了说明性箭头
  "PG 低(电源良好) → 栅极≈0 → P-MOS 导通 → ON 拉高 = 开机" ⇒ 旧判据
  (`"→" in note` 扫全文) 把**正文里的说明箭头**当成了信号方向 ⇒ PWR_GOOD 被误判
  "多驱动" ⇒ 门禁变红。

  ★这是个典型的"我改一行注释就把门禁改红了" —— 判据脆弱, 不是网表错。

修法: 判据只认 note **开头**的结构化方向声明 ("方向 A→B" / "输出: ..."),
      不认正文中间的箭头。

★本测试的意义: **放宽判据 = 放松关卡, 必须证明真问题仍能抓住**:
  T1 结构性方向声明 ×2 → 必须仍判冲突 (真多驱动不被放过)
  T2 说明性箭头 (正文中间) → 不得误判
  T3 单个方向声明 → 不判冲突
  T4 真实回归: 当前库里 PWR_GOOD 只有 1 个结构化方向声明 ⇒ 放行
  T5 ★反向验证: 往网表里注入一个**真·多驱动**(第二个结构化 "方向" 声明)
     → 判据必须变红 ⇒ 证明它没被改废

跑法: python3 state/test_netlist_drc.py
"""
from __future__ import annotations

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FAILURES: list[str] = []
CHECKS = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global CHECKS
    CHECKS += 1
    if ok:
        print(f"  [PASS] {name}")
    else:
        print(f"  [FAIL] {name}  {detail}")
        FAILURES.append(f"{name} {detail}")


def cell(row: dict, key: str) -> str:
    return str(row.get(key) or "")


def is_output_driver(row: dict) -> bool:
    """★与 state/check_netlist.py 的实现保持一致 (判据唯一真源在那边, 这里复制一份做测试;
    若 check_netlist.py 改了, 这里要同步 —— 见 T6 的自检提示)"""
    n = (cell(row, "note") or "").strip()
    if not n:
        return False
    head = n[:24]
    return ("方向" in head) or ("输出" in head)


def find_multi_out(rows: list[dict]) -> list[str]:
    by_net: dict[str, list] = {}
    for r in rows:
        n = cell(r, "net")
        if n:
            by_net.setdefault(n, []).append(r)
    out = []
    for n, rs in by_net.items():
        if n == "GND":
            continue
        if len([r for r in rs if is_output_driver(r)]) > 1:
            out.append(n)
    return out


def main() -> int:
    print("\n=== T1: 两个**结构性**方向声明在同一 net → 必须判冲突 ===")
    rows = [
        {"net": "SIG_A", "note": "方向 源→汇; 电平 3.3V"},
        {"net": "SIG_A", "note": "方向 汇→源; 电平 1.8V"},
    ]
    check("T1 判出冲突", find_multi_out(rows) == ["SIG_A"], str(find_multi_out(rows)))

    print("\n=== T2: 说明性箭头 (正文中间) → 不得误判 ===")
    rows = [
        {"net": "PWR_GOOD", "note": "[PWR_GOOD] Q_PG 栅极 = 充电板 PG (开漏)。★V1.9: PG 低(电源良好) → 栅极≈0 → P-MOS 导通 → ON 拉高"},
        {"net": "PWR_GOOD", "note": "方向 充电IC→SoC; 电平 3.3V (开漏); 连接 BQ25896 PG 脚 → SoC GPIO"},
    ]
    check("T2 不误判", find_multi_out(rows) == [], str(find_multi_out(rows)))

    print("\n=== T3: 单个方向声明 → 不判冲突 ===")
    rows = [
        {"net": "SIG_B", "note": "方向 源→汇; 电平 3.3V"},
        {"net": "SIG_B", "note": "[SIG_B] 另一个器件的输入脚"},
    ]
    check("T3 不判冲突", find_multi_out(rows) == [], str(find_multi_out(rows)))

    print("\n=== T4: 真库回归 —— PWR_GOOD 应放行 (只有 1 个结构性方向声明) ===")
    import csv
    real = []
    with open(os.path.join(HERE, "..", "HW", "netlist_v1.csv"), encoding="utf-8") as f:
        for r in csv.DictReader(f):
            real.append(r)
    pgr = [r for r in real if (r.get("net") or "") == "PWR_GOOD"]
    check("T4 PWR_GOOD 存在", len(pgr) >= 3, f"{len(pgr)} 行")
    check("T4 PWR_GOOD 放行", "PWR_GOOD" not in find_multi_out(real), str(find_multi_out(real)[:5]))
    check("T4 全库无冲突", find_multi_out(real) == [], str(find_multi_out(real)[:5]))

    print("\n=== T5: ★反向验证 —— 注入一个**真·多驱动** → 判据必须变红 ===")
    injected = list(real) + [
        {"net": "PWR_GOOD", "note": "方向 另一处输出→PWR_GOOD; 电平 3.3V"},
    ]
    check("T5 注入后判出冲突", "PWR_GOOD" in find_multi_out(injected), str(find_multi_out(injected)[:5]))

    print("\n=== T6: 判据与 check_netlist.py 实现一致 (防漂移) ===")
    src = open(os.path.join(HERE, "check_netlist.py"), encoding="utf-8").read()
    check("T6 check_netlist 含新判据 (head[:24])", 'head = n[:24]' in src, "未找到 head 判定")
    check("T6 旧的全文字符串匹配已移除", '"→" in cell(r, "note")' not in src, "旧判据仍在")

    print("\n" + "=" * 62)
    if FAILURES:
        print(f"❌ 测试失败: {len(FAILURES)}/{CHECKS} 项不通过")
        for f in FAILURES:
            print("   -", f)
        return 1
    print(f"✅ 全部通过: {CHECKS}/{CHECKS} 项")
    return 0


if __name__ == "__main__":
    sys.exit(main())
