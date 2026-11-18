#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20261116_2150_verify257_open258_259.py
★main (moli) 2026-11-16 21:5x (cron 775d9893 ARS45 继续执行后继计划)★
★① ISS-257 (hw-lead) 交卷独立复验 ⇒ 落 verified  ② 新开 ISS-258 (sw-lead) / ISS-259 (mech-lead) = H-1 重锚第 6 跳★

★★**为什么做这件事 (★main 本轮 21:36~21:5x 自己实跑, 不抄任何交卷报告★)** ★★
· ★**`python3 state/advance.py --json` ⇒ internal = []** ⇒ ★**三个总工名下没有 status=open 的单** ⇒
  ★**但实测三个名额全空**: hw-lead 的 ISS-257 会话 21:45 **status=done** (已交卷) · sw-lead / mech-lead 无在飞会话 ★
· ★**而 ISS-257 这次落表把 SW/MECH 两侧的 md5 锚点打红了 (★H-1 第 6 跳★)** ⇒ ★**这是主线内 (原理图/网表侧) 的活, 不是 PCB 类** ★
· ★**main 21:4x 实跑的三条红 (★原样 rc★)**:
  · `python3 SW/tools/check_demo_panel_spec.py` ⇒ **rc=1** (R6 红 2 条: 盘上网表 `e06c1dd6…` ≠ 锚点 `16ac89f7…` · 盘上脚表 `287e7861…` ≠ 锚点 `ef436a37…`)
  · `python3 SW/tools/timing_check.py` ⇒ **rc=1** (SELFTEST **69/71**)
  · `python3 SW/tools/check_demo_panel_spec.py --selftest` ⇒ **rc=1** (**15/16** · 报「基线就不绿 ⇒ 台账对账自测不成立」)
  · `python3 MECH/check_demo_struct_truth.py` ⇒ **rc=2** (**21/23** · FAIL **G5b + C21**)
  · `python3 MECH/check_demo_struct_truth.py --selftest` ⇒ **rc=2** (报「基线就不绿 ⇒ 门禁本身有问题, 自测不成立」)
· ★**根因 = 上游合法落表 (ISS-257) ⇒ 锚点过期, 不是真源被换** ⇒ ★**只重锚, 判据逻辑 0 改动** ★

★★**ISS-257 为什么能落 verified (★main 21:4x 本机实跑 14 条 rc★)** ★★
· `state/check_netlist.py` **rc=0** · `state/check_netlist_pins.py` **rc=0** · `state/check_sch_erc.py` **rc=0** (ERC=0)
· `state/check_sch_pinfull.py` **rc=0** (图上 584 脚 = 表里 584 脚 · K=0 · 218 器件/153 网)
· `HW/check_g1a7_selection_landed.py` **rc=0** (★本单新门禁 6 判据全绿★) · `--selftest` **rc=0** (★11/11 反向用例全抓到, ★含 M4「evidence 写成 `[官网]` 必须红」= 本轮 P0 坑进闸★)
· `HW/check_netlist_selfconsistency.py` **rc=0** · `--expect-resolved` **rc=1 且仍 18 条 (一条没上升)** ⇒ ★**V-2/V-3/V-4 一条没代拍** ★
· `state/check_stage_g1a.py` **rc=1** ⇒ ★**G1a-5 由红转 ✅ + G1a-7 转 ✅** (仍红 G1a-4 / G1a-8 = ★**预期, 那两条卡在老板拍板 + PCB 类★**)
· `state/check_chain_content_anchor.py` **rc=0** (四环: ① 网表 ✅ ② 原理图 ✅ ④ BOM ✅ · ★**③ PCB 仍红 = 真红, 板那一趟没做, 保持红**★)
· `state/check_chain_content_anchor.py --selftest` **rc=0** (14/14)
· `state/merge.py` **rc=0** (冲突 0) · `state/gate_check.py` **rc=0** (Q1 18/18)
· ★**受保护 md5 跑前跑后逐字节不变**: 板 `611b869e13518c3c023fb178f91a0075` · `.kicad_pro` `3e504d2be83152e337949723e909be1b` ★
  (★网表 `e06c1dd633566aa44732762c2ff99d1c` · 脚表 `287e7861a0d1007748d92d9fbecdd490` · BOM `94642d07a69e8d60dd2af57f69b93607` = ★**本单合法落表后的新值**★)
· ★**交付物 5 件全在盘**: `HW/SCHEMATIC_LANDING_V1_LANDED.md` §18 (L919-1250) · `HW/check_g1a7_selection_landed.py` (25 KB · 21:35)
  · `HANDOFF/2026-11-16_hw-lead_ISS257_G1a7选型落表.md` (21 KB · 21:43 · B1~B6 齐全) · `HW/ISS257_g1a7_reverse_proof_sandbox.log` (21:40) · `state/fragments/hw.yaml` (20 处 ISS-257 登记)

★★**ISS-258 / ISS-259 的任务书 (★brief 全文落盘, 台账只放路径 + 摘要★)** ★★
· ISS-258 → sw-lead · brief: `state/dispatch_briefs/ISS-258_sw_h1_reanchor_jump6.md` · ★**只改 `SW/SW_MD5_BASELINE_LEDGER.md` §1 那两条 entries + landing_records + 追加 R-09** ★
· ISS-259 → mech-lead · brief: `state/dispatch_briefs/ISS-259_mech_h1_reanchor_jump6.md` · ★**只改 `MECH/HW_CROSS_REVIEW_TRIAGE.md` §1 那两条 entries + landing_records + 追加 R-06** ★
· ★**新锚点 (两边一样)**: 网表 `md5=e06c1dd633566aa44732762c2ff99d1c` · `prev_md5=16ac89f77c25a3f61834cc7ebcd78a7f` · `by=ISS-257` · `landed_at=2026-11-16 21:22`
  ⇒ 脚表 `md5=287e7861a0d1007748d92d9fbecdd490` · `prev_md5=ef436a37412ac9b6eac3c9f41f1edca4` · `by=ISS-257` · `landed_at=2026-11-16 21:22`
  ⇒ ★**依据 = `HW/SCHEMATIC_LANDING_V1_LANDED.md` §18.4 L1069/L1070 (单号+文件名+新旧 md5 四项同行)** ★

★★**边界 (本脚本)★★ ★★
· ★**只写 `state/issue_log.yaml`** (ISS-257 → verified + 新开 ISS-258/ISS-259) ★
· ★**不改 PROJECT_TRACKER.md** · ★**不写任何 agent 的分片** (★分片由 agent 自己走 frag_write.py★) ★
· ★**不碰板 / 布线 / 布局** · ★**零外发** · ★**不替老板拍板** ★
· ★**新单 owner = sw-lead / mech-lead ⇒ advance.py 的「一 agent 同时只 1 条 fixing」铁律自动生效 (★本轮只有 hw-lead 那条 fixing, 已随 ISS-257 关单清掉★)** ★
"""
import fcntl
import os
import shutil
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
IL = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
TODAY = "2026-11-16"

VERIFY_257 = (
    "★main 2026-11-16 21:4x 独立复验 (★自己实跑 14 条 rc, 不抄交卷报告★) ⇒ **落 verified** ★\n"
    "· `state/check_netlist.py` **rc=0** · `state/check_netlist_pins.py` **rc=0** · `state/check_sch_erc.py` **rc=0** (ERC=0) · "
    "`state/check_sch_pinfull.py` **rc=0** (584=584 · K=0 · 218 器件/153 网)\n"
    "· `HW/check_g1a7_selection_landed.py` **rc=0** (★本单新门禁 6 判据全绿★) · `--selftest` **rc=0** (★11/11 反向用例全抓到, "
    "★含 M4「evidence 写成 `[官网]` 必须红」= 本轮 P0 那个坑已经进闸★)\n"
    "· `HW/check_netlist_selfconsistency.py` **rc=0** · `--expect-resolved` **rc=1 且仍 18 条 (一条没上升)** ⇒ ★**V-2/V-3/V-4 一条没代拍** ★\n"
    "· `state/check_stage_g1a.py` **rc=1** ⇒ ★**G1a-5 由红转 ✅ + G1a-7 转 ✅** (仍红 G1a-4 / G1a-8 = ★**预期: 那两条卡在老板拍板 + PCB 类★**)\n"
    "· `state/check_chain_content_anchor.py` **rc=0** (四环: ① 网表 ✅ ② 原理图 ✅ ④ BOM ✅ · ★**③ PCB 仍红 = 真红, 板那一趟没做, 必须保持红**★)\n"
    "· `state/check_chain_content_anchor.py --selftest` **rc=0** (14/14) · `state/merge.py` **rc=0** (冲突 0) · `state/gate_check.py` **rc=0** (Q1 18/18)\n"
    "· ★**受保护 md5 跑前跑后逐字节不变**: 板 `611b869e13518c3c023fb178f91a0075` · `.kicad_pro` `3e504d2be83152e337949723e909be1b** ★\n"
    "  (★网表 `e06c1dd633566aa44732762c2ff99d1c` · 脚表 `287e7861a0d1007748d92d9fbecdd490` · BOM `94642d07a69e8d60dd2af57f69b93607` = ★**本单合法落表后的新值**★)\n"
    "· ★**交付物 5 件全在盘**: 台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` §18 (L919-1250) · 新门禁 `HW/check_g1a7_selection_landed.py` (25 KB · 21:35) · "
    "交卷单 `HANDOFF/2026-11-16_hw-lead_ISS257_G1a7选型落表.md` (21 KB · 21:43 · B1~B6 齐全) · 自证日志 `HW/ISS257_g1a7_reverse_proof_sandbox.log` (21:40) · "
    "分片 `state/fragments/hw.yaml` (20 处 ISS-257 登记)\n"
    "· ★**本单遗留 (交 main 处置, 不在本单范围)**: ① SW/MECH 侧 md5 锚点被打红 ⇒ 已另派 ISS-258 / ISS-259 (H-1 重锚第 6 跳) ② "
    "`R_SER_CSI_MCLK` 必装但 value 仍 `[待原厂]` (登记成 need 交 main) ③ `U_PWR_SW` 落成 `TPS22991RAA` 待老板一句追认 (need 交 main) ④ "
    "③ PCB / ⑤ 投产包两条红 = PCB·投产那一趟 (★排队不派, 按老板 11-11 10:07★)"
)

NOTE_257_EXTRA = (
    "\n\n★2026-11-16 21:5x (cron 775d9893 ARS45 继续执行后继计划) ★**交卷独立复验 + 关单** ★ ★\n"
    "· ★**main 21:4x 本机实跑 14 条 rc (★不抄交卷报告★)** ⇒ ★**G1a-5 由红转 ✅ · G1a-7 转 ✅ · `--expect-resolved` 仍 18 条一条没上升** ★\n"
    "· ★**落 verified** (★verify_by = main ≠ owner = hw-lead ⇒ 验证分离成立★) ★\n"
    "· ★**连带后果 (★已另派单, 不藏账★)**: ★**本次落表把网表 md5 `16ac89f7…`→`e06c1dd6…` · 脚表 `ef436a37…`→`287e7861…` ⇒ "
    "SW 侧 `check_demo_panel_spec.py` rc=1 (R6 红 2 条) + `timing_check.py` rc=1 (69/71) + MECH 侧 `check_demo_struct_truth.py` rc=2 (G5b+C21) ⇒ "
    "⇒ ★**H-1 重锚第 6 跳**: ISS-258 (sw-lead) + ISS-259 (mech-lead)★ ★\n"
    "· ★**新锚点依据 = `HW/SCHEMATIC_LANDING_V1_LANDED.md` §18.4 L1069/L1070 (单号+文件名+新旧 md5 四项同行)** ★"
)

BRIEF_258 = (
    "★**SW 侧 H-1 重锚 (第 6 跳)** ★\n"
    "★**病灶 (★main 21:4x 本机实跑★)**: `SW/tools/check_demo_panel_spec.py` **rc=1** (R6 红 2 条) · `SW/tools/timing_check.py` **rc=1** (SELFTEST 69/71) · "
    "`--selftest` **rc=1** (15/16 · 报「基线就不绿」) ⇒ ★**根因 = ISS-257 合法落表 ⇒ 锚点过期, 不是真源被换** ★\n"
    "★**只改 `SW/SW_MD5_BASELINE_LEDGER.md` §1 `source_ledger.entries[]` 那两条 (网表 + 脚表) 的 4 个字段 + `landing_records` 追加 ISS-257 交接单位置 + §3 追加 R-09 留痕行** ★\n"
    "★**新锚点**: 网表 `md5=e06c1dd633566aa44732762c2ff99d1c` · `prev_md5=16ac89f77c25a3f61834cc7ebcd78a7f` · `by=ISS-257` · `landed_at=2026-11-16 21:22` ⇒ "
    "脚表 `md5=287e7861a0d1007748d92d9fbecdd490` · `prev_md5=ef436a37412ac9b6eac3c9f41f1edca4` · `by=ISS-257` · `landed_at=2026-11-16 21:22` "
    "(★依据 = `HW/SCHEMATIC_LANDING_V1_LANDED.md` §18.4 L1069/L1070★)\n"
    "★**验收**: `check_demo_panel_spec.py` rc=0 (R1~R7) · `timing_check.py` rc=0 (71/71) · `--selftest` rc=0 (16/16) + ★**反向用例 (锚点改回旧 md5 ⇒ 必须变红)★** ★\n"
    "★**边界**: 零落表 · 零外发 · 不碰 `HW/` 与 `MECH/` · 不改判据阈值 · 不替老板拍板 · 不自签 issue_log ★\n"
    "★**brief 全文**: `state/dispatch_briefs/ISS-258_sw_h1_reanchor_jump6.md` ★"
)

BRIEF_259 = (
    "★**MECH 侧 H-1 重锚 (第 6 跳)** ★\n"
    "★**病灶 (★main 21:4x 本机实跑★)**: `MECH/check_demo_struct_truth.py` **rc=2** (21/23 · FAIL **G5b + C21**) · `--selftest` **rc=2** (报「基线就不绿 ⇒ 自测不成立」) "
    "⇒ ★**根因 = ISS-257 合法落表 ⇒ 锚点过期, 不是真源被换** ★\n"
    "★**只改 `MECH/HW_CROSS_REVIEW_TRIAGE.md` §1 `MECH_ANCHORS` 的 `source_ledger.entries[]` 那两条 (网表 + 脚表) 的 4 个字段 + `landing_records` 追加 ISS-257 交接单位置 + §3.1 追加 R-06 留痕行** ★\n"
    "★**新锚点**: 网表 `md5=e06c1dd633566aa44732762c2ff99d1c` · `prev_md5=16ac89f77c25a3f61834cc7ebcd78a7f` · `by=ISS-257` · `landed_at=2026-11-16 21:22` ⇒ "
    "脚表 `md5=287e7861a0d1007748d92d9fbecdd490` · `prev_md5=ef436a37412ac9b6eac3c9f41f1edca4` · `by=ISS-257` · `landed_at=2026-11-16 21:22` "
    "(★依据 = `HW/SCHEMATIC_LANDING_V1_LANDED.md` §18.4 L1069/L1070★)\n"
    "★**验收**: `check_demo_struct_truth.py` rc=0 (23/23 · FAIL 0) · `--selftest` rc=0 (14/14 一条没删) + ★**反向用例 (锚点改回旧 md5 ⇒ 必须变红)★** ★\n"
    "★**边界**: 零落表 · 零外发 · 不碰 `HW/` 与 `SW/` · 不改判据阈值 (G5b/C21 判据逻辑 0 改动) · 不碰布线/布局/板框 · 不替老板拍板 · 不自签 issue_log ★\n"
    "★**brief 全文**: `state/dispatch_briefs/ISS-259_mech_h1_reanchor_jump6.md` ★"
)


def _atomic_write(path: str, data: str) -> None:
    fd, tmp = tempfile.mkstemp(dir=HERE, prefix=".tmp_write.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        shutil.move(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def main() -> int:
    with open(LOCK, "w", encoding="utf-8") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        log = yaml.safe_load(open(IL, encoding="utf-8")) or {}
        issues = log.get("issues") or []
        by_id = {i.get("id"): i for i in issues}
        changed = []

        # ---- ① ISS-257 → verified ----
        i257 = by_id.get("ISS-257")
        if not i257:
            raise SystemExit("ISS-257 不在台账")
        if i257.get("status") == "verified":
            print("ISS-257 已是 verified ⇒ 跳过")
        else:
            i257["status"] = "verified"
            i257["verify_result"] = "pass"
            i257["verify_by"] = "main"
            i257["verify_date"] = TODAY
            i257["fix_ref"] = (
                "HW/SCHEMATIC_LANDING_V1_LANDED.md §18 (L919-1250) · HW/check_g1a7_selection_landed.py · "
                "HANDOFF/2026-11-16_hw-lead_ISS257_G1a7选型落表.md · HW/ISS257_g1a7_reverse_proof_sandbox.log"
            )
            i257["note"] = (i257.get("note") or "") + VERIFY_257 + NOTE_257_EXTRA
            changed.append("ISS-257 → verified")

        # ---- ② 新开 ISS-258 (sw-lead) / ISS-259 (mech-lead) ----
        new_issues = [
            {
                "id": "ISS-258",
                "title": (
                    "★★[主线内·SW 侧·H-1 重锚·内部活] ★★`SW/tools/check_demo_panel_spec.py` rc=1 (R6 红 2 条) + "
                    "`SW/tools/timing_check.py` rc=1 (SELFTEST 69/71) + `--selftest` rc=1 (15/16) ⇒ ★**ISS-257 合法落表 ⇒ md5 锚点过期** ★ ⇒ "
                    "★**只重锚网表 + 脚表那两条 (第 6 跳), 判据逻辑 0 改动** ★"
                ),
                "severity": "medium",
                "source_blocker": "ISS-257",
                "source_agent": "hw-lead",
                "desc": (
                    "★main 2026-11-16 21:4x 本机实跑 ⇒ `check_demo_panel_spec.py` rc=1 (R6: 盘上网表 `e06c1dd6…` ≠ 锚点 `16ac89f7…` · "
                    "盘上脚表 `287e7861…` ≠ 锚点 `ef436a37…`) · `timing_check.py` rc=1 (69/71) · `--selftest` rc=1 (15/16 · 报「基线就不绿 ⇒ "
                    "台账对账自测不成立」) ⇒ ★**根因 = 上游合法落表 (ISS-257), 不是真源被换** ⇒ ★**只重锚** ★\n"
                    "★**新锚点**: 网表 `md5=e06c1dd633566aa44732762c2ff99d1c` · `prev_md5=16ac89f77c25a3f61834cc7ebcd78a7f` · `by=ISS-257` · "
                    "`landed_at=2026-11-16 21:22` ⇒ 脚表 `md5=287e7861a0d1007748d92d9fbecdd490` · `prev_md5=ef436a37412ac9b6eac3c9f41f1edca4` · "
                    "`by=ISS-257` · `landed_at=2026-11-16 21:22` ⇒ ★**依据 = `HW/SCHEMATIC_LANDING_V1_LANDED.md` §18.4 L1069/L1070 (四项同行)** ★\n"
                    "★**本单 = 主线内 (原理图/网表侧·门禁口径) · 不是 PCB 布线/布局类** ★"
                ),
                "owner": "sw-lead",
                "reporter": "main",
                "raised": TODAY,
                "due": "2026-11-19",
                "status": "fixing",
                "external": False,
                "need_keys": [],
                "fix_ref": None,
                "dispatched_at": TODAY,
                "note": (
                    "★**main 2026-11-16 21:5x 实测派单** ⇒ SW 侧三盏灯同时红 (R6 / timing_check 2 条 / selftest 基线)\n"
                    "★**根因 = 上游合法落表 (ISS-257) ⇒ 锚点过期, 不是真源被换** ⇒ ★**只重锚** ★\n"
                    "★**只许改**: `SW/SW_MD5_BASELINE_LEDGER.md` §1 `source_ledger.entries[]` 那两条 (网表 + 脚表) 的 4 个字段 + "
                    "`landing_records` 追加 ISS-257 交接单位置 + §3 追加 R-09 留痕行\n"
                    "★**brief 全文**: `state/dispatch_briefs/ISS-258_sw_h1_reanchor_jump6.md`\n"
                    "★**验收**: check_demo_panel_spec rc=0 (R1~R7) · timing_check rc=0 (71/71) · --selftest rc=0 (16/16) + 反向用例\n"
                    "★**边界**: 零落表 · 零外发 · 不碰 HW/ 与 MECH/ · 不改判据阈值 · 不替老板拍板 · 不自签 issue_log ★"
                ),
                "task_brief": BRIEF_258,
            },
            {
                "id": "ISS-259",
                "title": (
                    "★★[主线内·MECH 侧·H-1 重锚·内部活] ★★`MECH/check_demo_struct_truth.py` rc=2 (21/23 · FAIL G5b + C21) + "
                    "`--selftest` rc=2 (「基线就不绿 ⇒ 自测不成立」) ⇒ ★**ISS-257 合法落表 ⇒ md5 锚点过期** ★ ⇒ "
                    "★**只重锚网表 + 脚表那两条 (第 6 跳), 判据逻辑 0 改动** ★"
                ),
                "severity": "medium",
                "source_blocker": "ISS-257",
                "source_agent": "hw-lead",
                "desc": (
                    "★main 2026-11-16 21:4x 本机实跑 ⇒ `MECH/check_demo_struct_truth.py` rc=2 (21/23 · FAIL G5b + C21) · `--selftest` rc=2 "
                    "(报「基线就不绿 ⇒ 门禁本身有问题, 自测不成立」) ⇒ ★**根因 = 上游合法落表 (ISS-257), 不是真源被换** ⇒ ★**只重锚** ★\n"
                    "★**新锚点**: 网表 `md5=e06c1dd633566aa44732762c2ff99d1c` · `prev_md5=16ac89f77c25a3f61834cc7ebcd78a7f` · `by=ISS-257` · "
                    "`landed_at=2026-11-16 21:22` ⇒ 脚表 `md5=287e7861a0d1007748d92d9fbecdd490` · `prev_md5=ef436a37412ac9b6eac3c9f41f1edca4` · "
                    "`by=ISS-257` · `landed_at=2026-11-16 21:22` ⇒ ★**依据 = `HW/SCHEMATIC_LANDING_V1_LANDED.md` §18.4 L1069/L1070 (四项同行)** ★\n"
                    "★**本单 = 主线内 (原理图/网表侧·结构侧锚点) · 不是 PCB 布线/布局类** ★"
                ),
                "owner": "mech-lead",
                "reporter": "main",
                "raised": TODAY,
                "due": "2026-11-19",
                "status": "fixing",
                "external": False,
                "need_keys": [],
                "fix_ref": None,
                "dispatched_at": TODAY,
                "note": (
                    "★**main 2026-11-16 21:5x 实测派单** ⇒ MECH 侧两盏灯红 (G5b + C21) + selftest 基线不绿\n"
                    "★**根因 = 上游合法落表 (ISS-257) ⇒ 锚点过期, 不是真源被换** ⇒ ★**只重锚** ★\n"
                    "★**只许改**: `MECH/HW_CROSS_REVIEW_TRIAGE.md` §1 `MECH_ANCHORS` 的 `source_ledger.entries[]` 那两条 (网表 + 脚表) 的 4 个字段 + "
                    "`landing_records` 追加 ISS-257 交接单位置 + §3.1 追加 R-06 留痕行\n"
                    "★**brief 全文**: `state/dispatch_briefs/ISS-259_mech_h1_reanchor_jump6.md`\n"
                    "★**验收**: check_demo_struct_truth rc=0 (23/23 · FAIL 0) · --selftest rc=0 (14/14) + 反向用例\n"
                    "★**边界**: 零落表 · 零外发 · 不碰 HW/ 与 SW/ · 不改判据阈值 (G5b/C21 判据逻辑 0 改动) · 不碰布线/布局/板框 · 不替老板拍板 · 不自签 issue_log ★"
                ),
                "task_brief": BRIEF_259,
            },
        ]
        for ni in new_issues:
            if ni["id"] in by_id:
                print(f"{ni['id']} 已在台账 ⇒ 不重复开")
                continue
            issues.append(ni)
            changed.append(f"{ni['id']} → 开单 (owner={ni['owner']}, status=fixing)")

        _atomic_write(IL, yaml.safe_dump(log, allow_unicode=True, sort_keys=False, width=200))
        print("已写入:")
        for c in changed:
            print("  ·", c)
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
