#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""stage_gate.py 决策判据自测 (2026-10-28)
====================================================================
背景:
  G0 长期显示"缺 4 项, 老板拍板项未答 (q1_latency_scope / q4_battery_scope /
  q17_display_fps / q16_aspect_ratio)" —— 但这 4 项老板 **10-25 19:16 就拍过板了**
  (原话见 session 记录), pm.yaml 里 4 条 needs_from 全都带 `decision` 字段。
  根因: merge.py 认 `decision` 字段 (判 answered), **stage_gate.py 的
  decision_done() 只查 needs×answers 配对, 不看 decision** ⇒ 两个工具判据不一致
  ⇒ G0 被 4 个**已答**问题假性卡死 3 天。

修法: stage_gate.py 的 decision_done 加第 ① 条判据 (有 decision 字段即已答)。

★本测试的意义: 修判据 = 放松关卡, 必须证明
  (a) 真答了的能过
  (b) **没答的还是过不了** (判据没被改宽成橡皮章)
  (c) 配对路径仍有效 (老机制没被我改坏)

跑法: python3 state/test_stage_gate_decisions.py
"""
from __future__ import annotations

import copy
import os
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from stage_gate import decision_done  # noqa: E402  ★直接 import 真实判据, 不复制

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


# ---- 判据来自 stage_gate.py 真实实现 (不复制) ----

def main() -> int:
    print("\n=== T1: 老板已拍板 (needs_from 带 decision 字段) → 判已答 ===")
    pm = {"needs_from": [
        {"key": "q1_latency_scope", "to": "boss", "since": "2026-10-25",
         "decision": "A (曝光开始→出光, 最严口径)。老板 10-25 19:16 拍板: 选 A。",
         "decided_at": "2026-10-25", "decided_by": "boss (项目总工代录)"},
    ]}
    dd = lambda k: decision_done(pm, k)
    check("T1 带 decision → 已答", dd("q1_latency_scope") is True)

    print("\n=== T2: ★没拍板 (无 decision, 无 answers 配对) → 必须判未答 (判据没被改宽) ===")
    pm2 = {"needs_from": [
        {"key": "q2_unanswered", "to": "boss", "since": "2026-10-25"},
    ], "answers": []}
    dd2 = lambda k: decision_done(pm2, k)
    check("T2 未拍板 → 未答", dd2("q2_unanswered") is False)

    print("\n=== T3: answers 配对路径仍有效 (老机制没被改坏) ===")
    pm3 = {
        "needs_from": [{"key": "q3_paired", "to": "boss", "since": "2026-10-25"}],
        "answers": [{"key": "q3_paired", "to": "main", "by": "boss",
                     "value": "按需触发", "ref": "老板 10-25 19:16"}],
    }
    dd3 = lambda k: decision_done(pm3, k)
    check("T3 配对闭合 → 已答", dd3("q3_paired") is True)

    print("\n=== T4: key 不存在 → 未答 (不能凭空算过) ===")
    dd4 = lambda k: decision_done(pm3, k)
    check("T4 未知 key → 未答", dd4("q99_nonexistent") is False)

    print("\n=== T5: ★decision 字段存在但为空字符串 → 仍算未答 (防空壳字段蒙混过关) ===")
    pm5 = {"needs_from": [{"key": "q5_empty", "to": "boss", "decision": ""}], "answers": []}
    dd5 = lambda k: decision_done(pm5, k)
    check("T5 空 decision → 未答", dd5("q5_empty") is False)

    print("\n=== T6: ★decision 字段必须是实质决策 (只有一个空格不算) ===")
    pm6 = {"needs_from": [{"key": "q6_space", "to": "boss", "decision": " "}], "answers": []}
    dd6 = lambda k: decision_done(pm6, k)
    check("T6 空白 decision → 未答", dd6("q6_space") is False)

    print("\n=== T7: 真库回归 —— 4 个曾假性卡住 G0 的决策现在应判已答 ===")
    real_pm = yaml.safe_load(open(os.path.join(HERE, "fragments", "pm.yaml"), encoding="utf-8"))
    dd_real = lambda k: decision_done(real_pm, k)
    for k in ("q1_latency_scope", "q4_battery_scope", "q17_display_fps", "q16_aspect_ratio"):
        n = [x for x in real_pm["needs_from"] if x.get("key") == k]
        has_dec = bool(n and n[0].get("decision"))
        check(f"T7 {k} 已答 (pm.yaml 带 decision={has_dec})", dd_real(k) is True)

    print("\n=== T8: 真库回归 —— 未拍板的决策仍是未答 (不能全放行) ===")
    unanswered = [n.get("key") for n in real_pm.get("needs_from") or []
                  if not n.get("decision")
                  and n.get("to") == "boss"
                  and not any(a.get("key") == n.get("key") and a.get("by") == "boss"
                              for a in real_pm.get("answers") or [])]
    print(f"  仍待老板拍板: {unanswered}")
    check("T8 至少还有 1 项真待拍板 (证明判据没变成橡皮章)", len(unanswered) >= 1, str(unanswered))
    for k in unanswered:
        check(f"T8 {k} 判未答", dd_real(k) is False)

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
