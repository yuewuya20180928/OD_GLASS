#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_ISS-330 订正 · ★main 自验违反「验证分离」⇒ 落到 `fixed` 而不是 `verified`★

★**为什么有这一单 (★main 自己抓到的自错·不是被谁打回★)** ★:
  ★**main 20:3x 第一次落表时把 ISS-330 直接落成 `verified` 且 `verify_by = main`** ★
  ⇒ ★`state/issue_check.py` 的 **C3 ★验证分离★** 当场判红 (★`verify_by == owner == main`★) ⇒ **issue_check rc=1** ★
  ⇒ ★**本单把它改回合规态** ★

★**为什么落 `fixed` 而不是 `verified` (★项目既有口径·不是本单新发明★)** ★:
  ★**`issue_check.py` C3 的原文**: 「closed 必须: verify_result==pass 且 **verify_by != owner** (修复人不能自验)」★
  ⇒ ★**C3 只对 `verified` / `closed` 生效** ⇒ ★**`fixed` = 「修完了, 待独立验收」** ★
  ★**项目里 20 条 owner=main 的 verified 单 ⇒ `verify_by` 全部是【别人】** (★hw-lead 9 · sw-lead 7 · boss 4·**零例外**★)
    ⇒ ★**main 自办的活, 签字人必须是第三方** ★
  ★**同类先例 (★owner=main + status=fixed + verify_by=None★)**: ★**ISS-252** (★2026-11-16 19:4x main 建的 `check_stage_g1a.py` 闸★)
    ⇒ ★**同型: main 自建的机制闸 ⇒ 落 `fixed` 待第三方签收★ ★

★**★为什么本轮不立刻找第三方签 (★不然就是自欺欺人★)** ★:
  ★**三个总工此刻各有一条 `fixing` 在飞 (★hw-lead ISS-328 的后台链 PID 1130653/1130654 还在跑 · sw-lead ISS-332 会话在跑 · mech-lead ISS-333 待收卷★)**
    ⇒ ★**按「一个 agent 同时只能有一个写会话」的铁律, 现在派任何一个总工去签 ISS-330 都会与它在飞的那条抢同一个分片**
    ⇒ ★**R18 压测实证: 两个并发写会话 ⇒ 合并丢 12%~38%** ⇒ ★**本轮【不派】是纪律, 不是偷懒** ★
  ★**⇒ 落 `fixed` + verify_by=None + 把「谁签」写成显式待办 ⇒ 等有人签时一步到位** ★

★**幂等**: 只在 ISS-330 的 status == "verified" 且 verify_by == "main" 时才动手 ⇒ 双跑安全
★**原子性**: 与兄弟 job 共用 `state/.issue_log.lock` 的 flock
"""
from __future__ import annotations

import fcntl
import os

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")

NOW = "2026-11-18"

RESULT = (
    "★**main 2026-11-18 20:1x~20:3x 本机实跑 · 独立复核 · 不抄任何 agent 报告 · 修完了但【还没签】** ★\n"
    "★**① 闸脚本已挂进 `state/gate_check.py` 的 EXTRA_GATES (第 8 道 · 追加在末尾 · 既有 7 道一行未动)** ★\n"
    "   ★挂闸前备份: `state/.bak_gate_check_20261118_2020_pre_iss330_hook` ★\n"
    "★**② 挂完三道闸原样 rc**: `merge.py` rc=0 · `gate_check.py` rc=0 · `issue_check.py` rc=0 ★\n"
    "★**③ 新闸真在链上且绿 (★`--json` 读法·不靠猜★)**: `extra_gates` 共 8 道 ⇒ 第 8 道 = 「MECH 侧位号引用可达性闸 (ISS-326 设计稿 / ISS-333 实现)」\n"
    "   ok=True rc=0 · `summary['extra_gate_ok::MECH 侧位号引用可达性闸 (ISS-326 设计稿 / ISS-333 实现)']` = True ★\n"
    "★**④ ISS-330 的 5 条硬要求逐条实测复核**: \n"
    "   ① **fail-closed 三条** ⇒ 闸内 F1 板读不到 / F2 网表读不到 / F3 扫描面半残 三条各一条反向用例 (MC-10 / MC-11 / MC-9) 且全部判红\n"
    "      ⇒ 闸内 `InputError` ⇒ 走 `[FAIL] fail-closed:` ⇒ rc=2 (★不是「取不到就当过」★) ★\n"
    "   ② **建闸日基线 MECH 侧自己 fresh 测** ⇒ 实测 `BASELINE_COUNT = 10` (★**不抄 SW 侧的 3**★) · 10 条真隐患逐条带出处\n"
    "      ⇒ **基线只许收紧不许放宽** 由 `BASELINE_COUNT_BUILDDAY = 10` 机械化成一条闸自己会判红的检查 (★MC-12: 改成 11 ⇒ 判红★) ★\n"
    "   ③ **反向用例 ≥ 5 条** ⇒ 实跑 `--selftest` = **14/14 通过** (★含「假绿」MC-14「判据分支匹配不上必须红」★) ★\n"
    "   ④ **扫描面 `MECH/**/*.py` + `MECH/**/*.md` 递归** ⇒ 实测 **48 md + 65 py = 113 份** (★与 ISS-330 要求逐字一致★)\n"
    "      ⇒ 抽出 246 个唯一标识符 · ★**闸自身排除在扫描面外** (`SELF_GATE_REL`)★ ★\n"
    "   ⑤ **收紧要逐条写明哪一条被解掉了** ⇒ `MECH_NON_DESIGNATOR_REGISTRY` (C17) 与 `BASELINE_TOKENS` 两张表逐条带书面理由\n"
    "      ⇒ ★**main 逐条抽查了实物证据 (★不许只信脚本自述★)**: `R_DCR` ⇒ `MECH/verify_budget.py:84 CHG_R_DCR = 0.050 # Ω` (★铜损热阻不是位号★) ·\n"
    "      `R_ILIM_VALUES` ⇒ `MECH/HINGE_POWER_CALC.md:250` (★档表常量名★) · `R_TIM` ⇒ `MECH/CENTER_CAVITY_REBALANCE_V2.md:40 R_TIM = 33.333 / A_m` (★导热垫热阻 K/W★) ·\n"
    "      `LED_G_WINDOW` ⇒ `MECH/BOARD_ONEPASS_MECH_SYNC.md:293 \"id\": \"LED_G_WINDOW\"` (★JSON 场景 id·同对象的 `ref` 才是位号★) ·\n"
    "      `J_CHG_SELECTION` ⇒ 盘上确有同名文档 `HW/J_CHG_SELECTION.md` (⇒ 走 C4「文档互引」不是 C17) ★\n"
    "★**⑤ main 独立复算了 16→10 这条「收紧」的算术 (★ISS-326 设计稿说 16 · 闸脚本交 10 · 不许只信一方★)**:\n"
    "   从 `logs/iss326/gate_design/mech_gate_baseline.json` 重算设计稿的 16 条 (= md_hit ∧ 非本单产物 ∧ 非 py_only)\n"
    "   ⇒ **交付的 10 条里 9 条 ∈ 设计稿那 16 条 · 另 1 条 `D_ESD_CHG` 是设计稿当时按「py-only 粗口径」扫掉的 (★本闸口径把它捡回来 = 收紧不是放宽★)**\n"
    "   ⇒ **净效果 = 上限从 16 收到 10 (★收紧 6 条★) 且同时把一条 py 里的真隐患纳入基线 (★多抓一条★)** ⇒ 方向正确 ★\n"
    "★**⑥ 反向验证 (★证明这道闸不是「挂着好看」★)**: 把闸脚本临时挪走 ⇒ `gate_check.py --json` 读到 `ok=False` 且 detail =\n"
    "   「★闸脚本不存在 … ⇒ 视为闸红 (不许静默跳过)」⇒ **链当场红 + gaps 记一条「★新闸红: MECH 侧位号引用可达性闸」** ⇒ ★**fail-closed 在真链上生效**\n"
    "   ⇒ 随后已原样恢复 (md5 回到 `e105a08fd7d40fed770b63f6fb206f6c`) ★\n"
    "★**⑦ 为什么【不】把它的 `--selftest` 也挂进链 (★main 的判据·不是省事★)**: ★**live 模式里已经内建 17/17 判据分支探针** ⇒\n"
    "   「判据分支匹配不上 ⇒ 判红」这条【假绿护栏】在 live 路径上就已生效 (★`probe_failures` ⇒ rc≠0★) ⇒ 再挂一遍 selftest 只是把链的耗时白翻一倍 (★单跑 21s★)·**不增判据覆盖** ★\n"
    "★**⑧ 零写板双证 (★挂完实测★)**: 板 `HW/PCB/demo_mainboard.kicad_pcb` md5 = `611b869e13518c3c023fb178f91a0075` ·\n"
    "   mtime = `2026-11-06 07:07:17.362193413` ⇒ **逐字节未动 (12 天)** · `MECH/` 树 **114 份文件跑闸前后逐字节未变** (★md5 清单 diff 为空★)\n"
    "   · 网表 `HW/netlist_v1.csv` md5 未变 ★\n"
    "★**⑨ 边界自证**: ★**零写板 · 零落表 (除本单自身) · 零改 `state/merge.py` / `state/issue_check.py` / `state/check_*.py` · 零改 `MECH/**` 任何文件 ·\n"
    "   零改 `SW/tools/check_sw_ref_reachability.py` (★只被闸只读 import·零改动★) · 零改别的 agent 的分片 · 零改 `PROJECT_TRACKER.md` §0 ·\n"
    "   零外发 (★不发信 · 不联系供应商 · 不下单★)** ★\n"
    "★**唯一改动**: `state/gate_check.py` 的 `EXTRA_GATES` 末尾追加 1 个元组 ★\n"
    "★**★为什么状态是 `fixed` 不是 `verified` (★本条最重要的一句★)** ★: ★**main 既是修复人又是本单的唯一执行人 ⇒ 按「修复人不能自验」的铁律 (C3) ★\n"
    "   ⇒ ★**main 不给自己签字** ⇒ ★**落 `fixed` 待第三方签收** ⇒ ★**签字人建议: 任一在飞单已交卷的总工 (hw-lead / sw-lead / mech-lead) 或老板** ★\n"
    "   ⇒ ★**签收所需的全部读数上面 ①~⑨ 已全部给齐 ⇒ 谁签都只需要跑一遍 `python3 state/gate_check.py --json` 看第 8 道 + 挪脚本复现 fail-closed** ★"
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
        if it.get("status") == "verified" and it.get("verify_by") == "main":
            it["status"] = "fixed"
            it["verify_by"] = None
            it["verify_result"] = RESULT
            it["verify_date"] = None
            it["note"] = (
                str(it.get("note") or "")
                + "\n★**2026-11-18 20:3x main 订正**: ★**main 20:3x 第一次落表时误把本单直接落成 `verified` 且 `verify_by=main` "
                "⇒ 被 `state/issue_check.py` 的 C3「验证分离」当场判红 (issue_check rc=1) ⇒ 改落 `fixed` 待第三方签收** ★\n"
                "★**签字人建议**: 任一在飞单已交卷的总工 (hw-lead / sw-lead / mech-lead) 或老板 · ★**签收所需读数已全部给齐 (见 verify_result ①~⑨)** ★"
            )
            with open(LOG, "w", encoding="utf-8") as fh:
                yaml.safe_dump(log, fh, allow_unicode=True, sort_keys=False, width=100000)
            print("· ISS-330 verified(main) → fixed (★自验违反 C3·改待第三方签收★)")
        else:
            print(f"· ISS-330 当前 {it.get('status')}/{it.get('verify_by')} (跳过·幂等)")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
