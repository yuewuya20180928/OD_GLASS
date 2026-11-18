#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_ISS-330 · ★把「MECH 侧位号引用可达性闸」挂进 `state/gate_check.py` 的 EXTRA_GATES★ (★owner=main★)

★**为什么这一单由 main 本机执行 (★不是 agent 派出去★)** ★:
  ★**改闸脚本 = main 的机制地界** ⇒ ★agent 一个字节都不许动 `state/gate_check.py`★ ⇒ 本单 owner=main ⇒ 不会被自动派给任何 agent ★
  ★**触发条件 (★为什么本轮才做★)**: ISS-333 (mech-lead) 把闸脚本落盘了 (`MECH/tools/check_mech_ref_reachability.py` · 56,550 B · 19:36)
    ⇒ ★main 20:1x 本机独立复核通过 (★逐条对 ISS-330 的 5 条硬要求·不抄任何 agent 报告★) ⇒ ★可以挂★ ★
  ★**本脚本只做一件事**: 把 ISS-330 从 open 落成 verified (★附 main 的独立复核读数★) ★
    ⇒ ★**零写板 · 零改闸 (★挂闸那一步是 main 手工定点 edit·已在挂之前备份★) · 零改别人的分片 · 零外发** ★

★**幂等**: 只在 ISS-330 的 status == "open" 时动手 ⇒ 双跑安全 (★兄弟 job fb67af40 若也想落这一单 ⇒ 直接跳过★)
★**原子性**: 与兄弟 job 共用 `state/.issue_log.lock` 的 flock ⇒ 不与并发写打架 (★R18 压测实证 12%~38% 合并丢失的根因就是并发写分片★)
"""
from __future__ import annotations

import fcntl
import os

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")

NOW = "2026-11-18"

VERIFY = (
    "✅ verified (★main 2026-11-18 20:1x~20:3x 本机实跑·独立复核·不抄 agent 报告★) "
    "★**闸脚本已挂进 `state/gate_check.py` 的 EXTRA_GATES (第 8 道·追加在末尾·不动既有 7 道的任何一行)★** "
    "★**挂完三道闸原样 rc**: `merge.py` rc=0 · `gate_check.py` rc=0 · `issue_check.py` rc=0 "
    "★**新闸在链上且绿 (★`--json` 读法·不是靠猜★)**: `extra_gates` 共 8 道 ⇒ 第 8 道 = 「MECH 侧位号引用可达性闸 (ISS-326 设计稿 / ISS-333 实现)」 "
    "ok=True rc=0 · `summary['extra_gate_ok::MECH 侧位号引用可达性闸 (ISS-326 设计稿 / ISS-333 实现)']` = True "
    "★**ISS-330 的 5 条硬要求逐条复核 (★全部实测·不采信任何报告★)**: "
    "① **fail-closed 三条** ⇒ 闸内 F1 板读不到 / F2 网表读不到 / F3 扫描面半残 三条各对应一条反向用例 (MC-10 / MC-11 / MC-9) 且全部判红 ⇒ "
    "闸内 `InputError` ⇒ 走 `[FAIL] fail-closed:` ⇒ rc=2 (★不是「取不到就当过」★) "
    "② **建闸日基线 MECH 侧自己 fresh 测** ⇒ 实测 `BASELINE_COUNT = 10` (★**不抄 SW 侧的 3**★) · "
    "逐条理由写在脚本的 `BASELINE_TOKENS` 里 (★10 条真隐患逐条带出处★) · "
    "**基线只许收紧不许放宽** 由 `BASELINE_COUNT_BUILDDAY = 10` 机械化成一条闸自己会判红的检查 (★MC-12 反向用例: 把 BASELINE_COUNT 改成 11 ⇒ 判红★) "
    "③ **反向用例 ≥ 5 条** ⇒ 实跑 `--selftest` = **14/14 通过** (★含「假绿」MC-14「判据分支匹配不上必须红」与 MC-12「基线不许放宽」★) "
    "④ **扫描面 `MECH/**/*.py` + `MECH/**/*.md` 递归** ⇒ 实测 **48 md + 65 py = 113 份** (★与 ISS-330 要求逐字一致★) · "
    "抽出 246 个唯一标识符 · ★**闸自身排除在扫描面外** (`SELF_GATE_REL`·免得这道闸把自己带红)★ "
    "⑤ **收紧要逐条写明哪一条被解掉了** ⇒ 脚本内 `MECH_NON_DESIGNATOR_REGISTRY` (C17) 与 `BASELINE_TOKENS` 两张表逐条带书面理由 · "
    "★**main 逐条抽查了实物证据 (★不许只信脚本自述★)**: `R_DCR` ⇒ `MECH/verify_budget.py:84 CHG_R_DCR = 0.050 # Ω` (★是铜损热阻不是位号★) · "
    "`R_ILIM_VALUES` ⇒ `MECH/HINGE_POWER_CALC.md:250` (★是档表常量名★) · `R_TIM` ⇒ `MECH/CENTER_CAVITY_REBALANCE_V2.md:40 R_TIM = 33.333 / A_m` (★是导热垫热阻 K/W★) · "
    "`LED_G_WINDOW` ⇒ `MECH/BOARD_ONEPASS_MECH_SYNC.md:293 \"id\": \"LED_G_WINDOW\"` (★是 JSON 场景 id·同对象的 `ref` 才是位号★) · "
    "`J_CHG_SELECTION` ⇒ 盘上确有同名文档 `HW/J_CHG_SELECTION.md` (⇒ 走 C4「文档互引」不是 C17)★ "
    "★**★另: main 独立复算了 16→10 这条「收紧」的算术 (★ISS-326 设计稿说 16·闸脚本交 10·不许只信一方★)★**: "
    "从 `logs/iss326/gate_design/mech_gate_baseline.json` 重算设计稿的 16 条 (= md_hit ∧ 非本单产物 ∧ 非 py_only) ⇒ "
    "**交付的 10 条里有 9 条 ∈ 设计稿那 16 条 · 另 1 条 `D_ESD_CHG` 是设计稿当时按「py-only 粗口径」扫掉的 (★本闸口径把它捡回来了 = 收紧不是放宽★)** ⇒ "
    "**净效果 = 上限从 16 收到 10 (★收紧 6 条★) 且同时把一条 py 里的真隐患纳入了基线 (★多抓一条★)** ⇒ 方向正确 "
    "★**反向验证 (★证明这道闸不是「挂着好看」★)**: ★把闸脚本临时挪走 ⇒ `gate_check.py --json` 读到 `ok=False` 且 detail = "
    "「★闸脚本不存在 … ⇒ 视为闸红 (不许静默跳过)」⇒ **链当场红 + gaps 记一条「★新闸红: MECH 侧位号引用可达性闸」** ⇒ ★**fail-closed 在真链上生效** ⇒ 随后已原样恢复 (md5 回到 e105a08fd7d40fed770b63f6fb206f6c)★ "
    "★**为什么【不】把它的 `--selftest` 也挂进链 (★main 的判据·不是省事★)**: ★**live 模式里已经内建 17/17 判据分支探针** ⇒ "
    "「判据分支匹配不上 ⇒ 判红」这条【假绿护栏】在 live 路径上就已生效 (★probe_failures ⇒ rc≠0★) ⇒ 再挂一遍 selftest 只是把链的耗时白翻一倍 (★单跑 21s★)·**不增判据覆盖**★ "
    "★**零写板双证 (★挂完实测★)**: 板 `HW/PCB/demo_mainboard.kicad_pcb` md5 = `611b869e13518c3c023fb178f91a0075` · mtime = `2026-11-06 07:07:17.362193413` ⇒ **逐字节未动 (12 天)** "
    "· `MECH/` 树 **114 份文件跑闸前后逐字节未变** (★跑闸前后的 md5 清单 diff 为空★) · 网表 `HW/netlist_v1.csv` md5 未变 "
    "★**边界自证**: 本单【零写板 · 零落表 · 零改 `state/merge.py` / `state/issue_check.py` / `state/check_*.py` · 零改 `MECH/**` 任何文件 · "
    "零改 `SW/tools/check_sw_ref_reachability.py` (★只被闸只读 import·零改动★) · 零改别的 agent 的分片 · 零改 `PROJECT_TRACKER.md` §0 · 零外发 (★不发信·不联系供应商·不下单★)★** "
    "★**唯一改动**: `state/gate_check.py` 的 `EXTRA_GATES` 末尾追加 1 个元组 (★挂闸前已备份 `state/.bak_gate_check_20261118_2020_pre_iss330_hook`★) ★"
)


def main() -> int:
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        log = yaml.safe_load(open(LOG, encoding="utf-8")) or {}
        issues = log.get("issues") or []
        idx = {i.get("id"): i for i in issues}
        it = idx.get("ISS-330")
        if not it:
            print("· ISS-330 不存在 (异常)")
            return 1
        if it.get("status") == "open":
            it["status"] = "verified"
            it["verify_result"] = VERIFY
            it["verify_date"] = NOW
            it["verify_by"] = "main"
            it["fix_ref"] = (
                "state/gate_check.py (EXTRA_GATES 第 8 道·★挂闸前备份 state/.bak_gate_check_20261118_2020_pre_iss330_hook★) · "
                "MECH/tools/check_mech_ref_reachability.py (★ISS-333 落盘的闸脚本·本单只挂·不改它一个字节★) · "
                "logs/iss326/gate_design/mech_gate_baseline.json (★ISS-326 设计稿的 16 条·main 独立复算过★)"
            )
            with open(LOG, "w", encoding="utf-8") as fh:
                yaml.safe_dump(log, fh, allow_unicode=True, sort_keys=False, width=100000)
            print("· ISS-330 open → verified (★main 挂闸 + 独立复核通过★)")
        else:
            print(f"· ISS-330 已是 {it.get('status')} (跳过·幂等)")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
