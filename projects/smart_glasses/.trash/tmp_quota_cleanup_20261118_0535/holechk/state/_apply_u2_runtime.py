#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""U2 裁决结果回写 (2026-10-28 08:5x, 项目总工)
====================================================================
把 §(1.34) 的 U2 口径裁决应用到各处仍写旧续航数的文档:
  ① SW/POWER_STATE_SEMANTICS.md   (sw-lead 产出, 会话已 done ⇒ 可改)
  ② SW/SW_REQUIREMENTS.md          (sw-lead 产出, 会话已 done ⇒ 可改)
  ③ PROJECT_TRACKER.md §0 锁死表 + 进展节里的旧数
  ④ state/fragments/sw.yaml 的 sw_standby_runtime 声明值

★原则: 旧值**保留并标 [旧口径·已作废]** (留变更痕迹), 不删。
  ⚠️ 分片写入走 state/frag_write.py (原子写), 不用 open(p,"w")。
"""
from __future__ import annotations

import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
sys.path.insert(0, HERE)


def atomic_write(path: str, text: str) -> None:
    d = os.path.dirname(path) or "."
    fd, tmp = tempfile.mkstemp(prefix=os.path.basename(path) + ".", suffix=".tmp", dir=d)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def apply_repl(path: str, repl: list[tuple[str, str]], label: str) -> int:
    with open(path, encoding="utf-8") as f:
        s = f.read()
    hit = 0
    for old, new in repl:
        if old in s:
            s = s.replace(old, new)
            hit += 1
    if hit:
        atomic_write(path, s)
    print(f"  {label}: {hit}/{len(repl)} 处替换")
    return hit


print("① SW/POWER_STATE_SEMANTICS.md")
apply_repl(
    os.path.join(PROJ, "SW", "POWER_STATE_SEMANTICS.md"),
    [
        # 状态表: 待机行
        ("| **0.15 W** [推算, V2 口径] | **420mAh → 2.8 h** (锁定口径, 复核见 U2) [推算] |",
         "| **0.15 W** [推算, V2 口径] | **420mAh → ~9.3 h** (U2 裁决口径 A; 旧值 2.8h [旧口径·已作废]) [推算] |"),
        # 状态表: 运行行
        ("| 满载 **1.22 W** / 按需触发 **0.23 W** [推算] | 满载 20 min / 按需触发 1.8 h (锁定口径, 复核见 U2) [推算] |",
         "| 满载 **1.22 W** / 按需触发 **0.23 W** [推算] | 满载 **~1.15 h** / 按需触发 **~6.1 h** "
         "(U2 裁决口径 A; 旧值 20min / 1.8h [旧口径·已作废]) [推算] |"),
        # §6 续航两行分列
        ("| **待机** | **2.8 h**", "| **待机** | **~9.3 h** (420mAh)"),
        ("| **关机** | **5-11 个月**", "| **关机** | **5-11 个月** (不变)"),
    ],
    "SW/POWER_STATE_SEMANTICS.md",
)

print("② SW/SW_REQUIREMENTS.md")
apply_repl(
    os.path.join(PROJ, "SW", "SW_REQUIREMENTS.md"),
    [
        ("原\"深度休眠\" [旧称·已作废] 0.15W 达不到那个数, 现称「待机」且续航单列 2.8h。",
         "原\"深度休眠\" [旧称·已作废] 0.15W 达不到那个数, 现称「待机」且续航单列 "
         "**~9.3h (420mAh)** (旧值 2.8h [旧口径·已作废], 是漏除 3.7V×DoD 的错算式, 2026-10-28 U2 裁决更正)。"),
    ],
    "SW/SW_REQUIREMENTS.md",
)

print("③ PROJECT_TRACKER.md")
apply_repl(
    os.path.join(PROJ, "PROJECT_TRACKER.md"),
    [
        ('| **"待机"口径** | ⟡ **深度休眠保留, 改名"待机"** (10-27 老板拍板): 0.15W ⇒ 420mAh 只撑 **2.8h**; '
         '与"关机"严格区分, 售后话术/续航口径分别单列 | 老板拍板 + 功耗预算 V3 |',
         '| **"待机"口径** | ⟡ **深度休眠保留, 改名"待机"** (10-27 老板拍板): 0.15W ⇒ 420mAh 撑 **~9.3h** '
         '(★旧值 2.8h [旧口径·已作废], 漏除 3.7V×DoD 的错算式, 10-28 U2 裁决更正); '
         '与"关机"严格区分, 售后话术/续航口径分别单列 | 老板拍板 + 功耗预算 V3 + §(1.34) U2 裁决 |'),
        ("+ 关机静态 **~0.4mW** (深睡 0.15W 只撑 2.8h ⇒ 深睡改名\"待机\")",
         "+ 关机静态 **~0.4mW** (深睡 0.15W 撑 ~9.3h, 但仍不叫\"关机\" ⇒ 深睡改名\"待机\")"),
        ("(深睡 0.15W 达不到, 深睡现在叫\"待机\"且续航口径单列 2.8h)。",
         "(深睡 0.15W 达不到, 深睡现在叫\"待机\"且续航口径单列 ~9.3h ★旧值 2.8h 已作废, 见 §(1.34))。"),
        ('"**待机** = 深度休眠, 2.8h"', '"**待机** = 深度休眠, ~9.3h"'),
    ],
    "PROJECT_TRACKER.md",
)

print("④ state/fragments/sw.yaml (走 frag_write 原子写)")
from frag_write import update_fragment  # noqa: E402


def mutate(d: dict) -> None:
    for c in d.get("interface_claims") or []:
        if c.get("key") == "sw_standby_runtime":
            c["value"] = "9.3h"
            c["note"] = ("420mAh 电芯待机续航 ~9.3h [推算] (★U2 裁决口径 A: t=Cap×DoD×V/P = 420×0.9×3.7/0.15; "
                         "旧值 2.8h [旧口径·已作废] 是漏除 3.7V 与 DoD 的错算式, 偏低 3.33 倍; "
                         "340mAh 无桥档 ~7.6h)。关机 5-11 个月用真电流 108µA 算, 不受影响。")
            c["ref"] = "SW/POWER_STATE_SEMANTICS.md#6 + PROJECT_TRACKER.md#(1.34)"
            break


update_fragment("sw-lead", mutate)
print("  sw.yaml: sw_standby_runtime → 9.3h ✅")
