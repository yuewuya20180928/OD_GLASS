#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20261116_1125_verify_iss238_redispatch_172_239.py
★main (moli) 2026-11-16 11:2x (cron 775d9893 继续执行后继计划)★
★① ISS-238 (mech-lead) 交卷独立复验 ⇒ 落 verified  ② ISS-172 / ISS-239 两条僵尸 fixing 重派★

★★**为什么做这件事 (★main 本轮 11:19~11:2x 自己实跑, 不抄任何交卷报告★)** ★★
· ★**`python3 state/advance.py --json` ⇒ internal = [] · approvals = [] · decisions = 42 条 · waiting = []** ⇒ rc=1 (★脚本自己写的: 0=有可执行动作 1=无可执行动作(全在等)★) ★
  ⇒ ★**根因 = 三个总工名额全被【僵尸 fixing】占着**: ISS-172(sw-lead) / ISS-238(mech-lead) / ISS-239(hw-lead) status 全是 fixing ★
  ⇒ ★**但三条的会话全都死了 (main 11:2x 实测 sessions_list + ps)** ★
    · ISS-172: `agent:sw-lead:subagent:561e2e3c` (session bc0aaa6d) 10:56:25 结束 · status=**timeout** · runtime 594s ★
    · ISS-238: `agent:mech-lead:subagent:d64594ac` (session 1be85c8d) 11:02:28 结束 · status=done ✔ (★真交卷★) ★
    · ISS-239: `agent:hw-lead:subagent:d251e953` (session a1f900f2) 11:02:31 结束 · status=**timeout** · runtime 569s ★
  ⇒ ★**ps 实测: 盘上没有任何 openclaw agent 写会话在跑 (只有 gateway + tui) ⇒ 三个名额现在都是空的** ★
· ★**main 逐字节复核 (11:2x 实跑)**: ★**ISS-172 / ISS-239 两条 = 零交付物** ★
    · `SW/LOAD_SWITCH_SELECTION_FACTS.md` 不在盘 · `SW/tools/check_load_switch_selection.py` 不在盘 ★
    · `HW/check_pin_function_labels.py` 不在盘 · `HW/PIN_FUNCTION_TABLE_CLOSEOUT.md` 不在盘 ★
    · ★**10:40 之后全仓被写的文件里, SW/ 目录 0 个 · HW/ 只有 PCB/STACKUP.md + LAYOUT_RULES.md (★那是别的 agent 并发自检链重生成, 不是这两条单的活★)** ★
  ⇒ ★**两条 = 僵尸 fixing (占着名额却没人干活) ⇒ 正是 advance.py in_flight 规则把 internal 段吃空的原因** ★
· ★**死因 = 默认 run timeout (~600s) 而非 529** (★ISS-237 那轮是 529 过载; 这两条 runtime 594s/569s = 撞 600s 默认超时★)
  ⇒ ★**处置 = 重派时把 runTimeout 提到 5400s (90 分钟), 沿用 ISS-237 重派时的同一手法** ★

★★**ISS-238 为什么能落 verified (★main 自己实跑, 逐条贴数★)** ★★
· `python3 MECH/display_biosafety_v2_check.py` ⇒ ★**rc=0 · 5/5 全 PASS** ★ (C1 活动口径 **5 → 0** · 历史沿革 **31 → 36** · 逐文件 MECH_BUDGET.md **5/23 → 0/28**) ★
  ⇒ ★**算术自证 = 正好 5 行翻转** (活动 -5 / 历史 +5 ⇒ 其余 4 份文档 PROTOTYPE_PLAN 0/3 · SOC_CARRIER_EVAL 0/1 · STRUCT_REVIEW_ISS065 0/3 · CLEARANCE_FIX 0/1 一条没动 ⇒ 总历史 31→36 = +5) ★
· `python3 MECH/display_biosafety_v2_check.py --selftest` ⇒ ★**rc=0 · 6/6** ★ (受保护脚本自己的用例一条没删没改) ★
· `python3 MECH/check_zoujuan_marker_consistency.py` ⇒ ★**rc=0 · K1~K5 5/5** ★ (K1 走鹃 36 行 / 带 canonical 36 / 活动口径 0 · K2 canonical 串自身在位 · K3 裸走鹃 0 · K4 形态 4 种双向一致 · K5 受保护 4 md5 未变) ★
· `python3 MECH/check_zoujuan_marker_consistency.py --selftest` ⇒ ★**rc=0 · 9/9** ★ ★
· `python3 MECH/check_demo_struct_truth.py` ⇒ ★**rc=0 · 23/23 · FAIL 0 组** ★ · `python3 MECH/cavity_recalc_check.py` ⇒ ★**rc=0 · 23/23** ★ ★
· ★**受保护 md5 (main 11:2x 实测, 逐字节与 brief 基线一致)** ★
  `96239070… MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md` · `bda4a294… MECH/JBD_ROLE_NARROWING.md` · `fa9b59e5… MECH/check_demo_struct_truth.py` · `29c77fc3… MECH/display_biosafety_v2_check.py` ·
  `34132f7e… HW/netlist_v1.csv` · `b21b743a… HW/netlist_v1_pins.csv` · `c195a117… HW/BOM_v1.csv` · `611b869e… HW/PCB/demo_mainboard.kicad_pcb` · `3e504d2b… HW/PCB/demo_mainboard.kicad_pro` ★
· 交付物在盘: `MECH/MECH_BUDGET.md` (mtime 10:52) · `MECH/DISPLAY_BIOSAFETY_V2_MARKER_POLICY_PROPOSAL.md` (21375 B, 11:12) · `MECH/check_zoujuan_marker_consistency.py` (21874 B, 10:59) · `HANDOFF/2026-11-16_mech-lead_ISS238_走鹃旧口径C1门禁红.md` (31762 B, 11:12) · 分片 `state/fragments/mech.yaml` L2231 `iss238_mech_marker_policy_decision` ✔ ★
· ★**该单留了两个待 main 裁的点 (交卷单 B4/B5 自陈)**: ① 判据放宽走 P1/P2/P3 哪个 (★受保护脚本 `display_biosafety_v2_check.py` 一个字没改★) ② 新门禁要不要挂进 `state/daily_check.py` (★现在 0 命中 ⇒ 巡检看不见这一盏★) ★

★★**边界 (本脚本)★★ ★★
· ★**只写 `state/issue_log.yaml` (ISS-238 status→verified + 两条 note 追加) + `state/dispatch_log.yaml` (追加两条续派记录)★** ★
· ★**不改 ISS-172 / ISS-239 的 status** (★本来就是 fixing, 本轮不重复标★) ★
· ★**不碰 PROJECT_TRACKER.md §0** · ★**不写任何 agent 的分片** · ★**不碰板 / 布线 / 布局** · ★**零外发** · ★**不替老板拍板** ★
"""
import fcntl
import os
import shutil
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
DL = os.path.join(HERE, "dispatch_log.yaml")
IL = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".dispatch_log.lock")
TODAY = "2026-11-16"

VERIFY_238 = (
    "★main 2026-11-16 11:2x 独立复验 (★自己实跑, 不抄交卷报告★) ⇒ **落 verified** ★\n"
    "· `python3 MECH/display_biosafety_v2_check.py` ⇒ ★**rc=0 · 5/5 全 PASS**★ (C1 活动口径 **5 → 0** · 历史沿革 **31 → 36** · MECH_BUDGET.md **5/23 → 0/28**) ⇒ ★**算术自证 = 正好 5 行翻转**, 其余 4 份文档计数一条没动 (PROTOTYPE_PLAN 0/3 · SOC_CARRIER_EVAL 0/1 · STRUCT_REVIEW_ISS065 0/3 · CLEARANCE_FIX 0/1) ⇒ 总历史 31→36 = **+5** ★\n"
    "· `python3 MECH/display_biosafety_v2_check.py --selftest` ⇒ ★**rc=0 · 6/6**★ (受保护脚本自己的用例一条没删没改) ★\n"
    "· `python3 MECH/check_zoujuan_marker_consistency.py` ⇒ ★**rc=0 · K1~K5 5/5**★ (K1 走鹃 36 行/带 canonical 36/活动口径 0 · K2 canonical 串自身在位 · K3 裸走鹃 0 · K4 形态 4 种双向一致 · K5 受保护 4 md5 未变) ★\n"
    "· `python3 MECH/check_zoujuan_marker_consistency.py --selftest` ⇒ ★**rc=0 · 9/9**★ ★\n"
    "· `python3 MECH/check_demo_struct_truth.py` ⇒ ★**rc=0 · 23/23 · FAIL 0 组**★ · `python3 MECH/cavity_recalc_check.py` ⇒ ★**rc=0 · 23/23**★ ★\n"
    "· ★**受保护 md5 (main 11:2x 实测, 与 brief 基线逐字节一致)**: `96239070…` DISPLAY_BIOSAFETY_CRITERIA_V2.md · `bda4a294…` JBD_ROLE_NARROWING.md · `fa9b59e5…` check_demo_struct_truth.py · `29c77fc3…` display_biosafety_v2_check.py · `34132f7e…` netlist_v1.csv · `b21b743a…` netlist_v1_pins.csv · `c195a117…` BOM_v1.csv · `611b869e…` demo_mainboard.kicad_pcb · `3e504d2b…` demo_mainboard.kicad_pro ★\n"
    "· 交付物在盘: MECH_BUDGET.md (mtime 10:52) · DISPLAY_BIOSAFETY_V2_MARKER_POLICY_PROPOSAL.md (21375 B, 11:12) · check_zoujuan_marker_consistency.py (21874 B, 10:59) · HANDOFF/2026-11-16_mech-lead_ISS238_走鹃旧口径C1门禁红.md (31762 B, 11:12) · 分片 mech.yaml L2231 `iss238_mech_marker_policy_decision` ✔ ★\n"
    "· ★**该盏隐形红结清 (它原本不在 daily_check 链上 ⇒ 巡检看不见)**, 受保护脚本一个字没改 ⇒ 判据放宽只交提案给 main ★\n"
    "★**两个待 main 裁的点 (交卷单自陈, 不代拍)**: ① 判据放宽走 P1/P2/P3 哪个 ② 新门禁 `check_zoujuan_marker_consistency.py` 要不要挂进 `state/daily_check.py` (现在 0 命中 ⇒ 巡检仍看不见这一盏) ★"
)

NOTE_172 = (
    "\n\n★2026-11-16 11:2x (cron 775d9893 继续执行后继计划) ★**僵尸 fixing 复活 + 重派**★ ★\n"
    "· ★**上一轮会话 = 僵尸**: `agent:sw-lead:subagent:561e2e3c` (session bc0aaa6d) ★**status=timeout · runtime 594s (★撞 600s 默认 run timeout★)** ⇒ ★**main 11:2x 逐字节复核: 零交付物** (`SW/LOAD_SWITCH_SELECTION_FACTS.md` 不在盘 · `SW/tools/check_load_switch_selection.py` 不在盘 · 10:40 后 SW/ 目录 0 个文件被写)★ ⇒ ★**占着 sw-lead 名额却没人干活** ★\n"
    "· ★**main 11:2x 实测 `ps`: 盘上没有任何 openclaw agent 写会话在跑 (只有 gateway + tui) ⇒ 三个总工名额全空** ★\n"
    "· ★**处置**: 重派 sw-lead (taskName=queue_iss172 · ★**runTimeout=5400s 绕开 600s 默认超时★**) ⇒ ★**status 保持 fixing** ★\n"
    "· ★**ISS-238 已于本轮 11:2x 落 verified (main 自己实跑 4 盏闸全绿) ⇒ mech-lead 名额也空出来了** ★\n"
    "· ★**零外发** · ★**未替老板拍型号/优先级序 (★决策页 §A5: 老板先拍优先级序, 不是拍型号★)** ★"
)

NOTE_239 = (
    "\n\n★2026-11-16 11:2x (cron 775d9893 继续执行后继计划) ★**僵尸 fixing 复活 + 重派**★ ★\n"
    "· ★**上一轮会话 = 僵尸**: `agent:hw-lead:subagent:d251e953` (session a1f900f2) ★**status=timeout · runtime 569s (★撞 600s 默认 run timeout★)** ⇒ ★**main 11:2x 逐字节复核: 零交付物** (`HW/check_pin_function_labels.py` 不在盘 · `HW/PIN_FUNCTION_TABLE_CLOSEOUT.md` 不在盘 · 10:40 后 HW/ 只有 PCB/STACKUP.md + LAYOUT_RULES.md (★别的 agent 并发自检链重生成, 不是本单的活★))★ ⇒ ★**占着 hw-lead 名额却没人干活** ★\n"
    "· ★**main 11:2x 实测 `ps`: 盘上没有任何 openclaw agent 写会话在跑 ⇒ 三个总工名额全空** ★\n"
    "· ★**处置**: 重派 hw-lead (taskName=queue_iss239 · ★**runTimeout=5400s 绕开 600s 默认超时★**) ⇒ ★**status 保持 fixing** ★\n"
    "· ★**ISS-238 已于本轮 11:2x 落 verified (main 自己实跑 4 盏闸全绿) ⇒ mech-lead 名额空出来; sw-lead 同时在跑 ISS-172 ⇒ ★**你一个 SW/ 文件都不许碰 (★连新建都不许★)**★ ★\n"
    "· ★**零外发** · ★**未代拍 V-2/V-3/V-4** ★"
)

DISPATCH_172 = (
    "★**续做派活 (★main 2026-11-16 11:2x 实测: 上一轮 10:5x 的 spawn 撞 600s 默认 run timeout ⇒ ISS-172 是僵尸 fixing·"
    "本轮重派·runTimeout 5400s·上一轮零写盘 ⇒ 本单等于从零开始★)** ★"
)
DISPATCH_239 = (
    "★**续做派活 (★main 2026-11-16 11:2x 实测: 上一轮 11:0x 的 spawn 撞 600s 默认 run timeout ⇒ ISS-239 是僵尸 fixing·"
    "本轮重派·runTimeout 5400s·上一轮零写盘 ⇒ 本单等于从零开始★)** ★"
)


def _atomic_write(path: str, data: str) -> None:
    fd, tmp = tempfile.mkstemp(dir=HERE, prefix=".tmp_write.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(data)
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def main() -> int:
    shutil.copy2(DL, DL + ".bak_20261116_1125_iss238_verify_redispatch")
    shutil.copy2(IL, IL + ".bak_20261116_1125_iss238_verify_redispatch")

    lock_fh = open(LOCK, "a+")
    try:
        fcntl.flock(lock_fh, fcntl.LOCK_EX)

        # ---- dispatch_log: 追加两条续派记录 ----
        dl = yaml.safe_load(open(DL, encoding="utf-8")) if os.path.exists(DL) else {"dispatches": []}
        dl.setdefault("dispatches", []).append({
            "issue": "ISS-172", "agent": "sw-lead", "at": TODAY,
            "brief": DISPATCH_172, "redispatch": True,
            "reason": "★上一轮 status=timeout (runtime 594s, 撞 600s 默认 run timeout) ⇒ 零交付物 ⇒ 僵尸 fixing★",
        })
        dl.setdefault("dispatches", []).append({
            "issue": "ISS-239", "agent": "hw-lead", "at": TODAY,
            "brief": DISPATCH_239, "redispatch": True,
            "reason": "★上一轮 status=timeout (runtime 569s, 撞 600s 默认 run timeout) ⇒ 零交付物 ⇒ 僵尸 fixing★",
        })
        fd, tmp2 = tempfile.mkstemp(dir=HERE, prefix=".dispatch_log.", suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                yaml.safe_dump(dl, f, allow_unicode=True, sort_keys=False, width=200)
            os.replace(tmp2, DL)
        except Exception:
            if os.path.exists(tmp2):
                os.unlink(tmp2)
            raise

        # ---- issue_log: ISS-238 落 verified + 两条 note 追加 (status 不动) ----
        il = yaml.safe_load(open(IL, encoding="utf-8"))
        hit = {"ISS-238": 0, "ISS-172": 0, "ISS-239": 0}
        for it in il.get("issues") or []:
            iid = it.get("id")
            if iid == "ISS-238":
                it["status"] = "verified"
                it["verify_by"] = "main"
                it["verify_date"] = TODAY
                it["verify_result"] = VERIFY_238
                it["note"] = (it.get("note") or "") + (
                    "\n\n2026-11-16 11:2x (cron 775d9893 继续执行后继计划) ★**main 独立复验后落 verified** ★ "
                    "(★实测: display_biosafety_v2_check rc=0 5/5 (活动口径 5→0) · --selftest 6/6 · "
                    "check_zoujuan_marker_consistency rc=0 K1~K5 5/5 · --selftest 9/9 · check_demo_struct_truth rc=0 23/23 · "
                    "cavity_recalc rc=0 23/23 · 受保护 9 个 md5 逐字节未变★) ★"
                    "★**两个待裁点留给 main**: 判据放宽 P1/P2/P3 选哪个 + 新门禁要不要挂进 daily_check.py★"
                )
                hit["ISS-238"] += 1
            elif iid == "ISS-172":
                it["note"] = (it.get("note") or "") + NOTE_172
                it["dispatched_at"] = TODAY
                hit["ISS-172"] += 1
            elif iid == "ISS-239":
                it["note"] = (it.get("note") or "") + NOTE_239
                it["dispatched_at"] = TODAY
                hit["ISS-239"] += 1
        if any(v != 1 for v in hit.values()):
            raise SystemExit("★命中数异常 = %s ⇒ 中止" % hit)
        _atomic_write(IL, yaml.safe_dump(il, allow_unicode=True, sort_keys=False, width=100000))
    finally:
        fcntl.flock(lock_fh, fcntl.LOCK_UN)
        lock_fh.close()

    chk = yaml.safe_load(open(IL, encoding="utf-8"))
    for iid in ("ISS-238", "ISS-172", "ISS-239"):
        st = [i.get("status") for i in chk["issues"] if i.get("id") == iid][0]
        print("   %s status = %s" % (iid, st))
    print("✅ dispatch_log.yaml 已原子写: 追加 ISS-172 → sw-lead / ISS-239 → hw-lead 续派记录")
    print("✅ issue_log.yaml 已原子写: ISS-238 → verified (verify_by=main) + 两条 note 追加")
    print("★**零外发 · 未替老板拍板 · 不碰 PCB 布线/布局/板 · 不写别人的分片** ★")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
