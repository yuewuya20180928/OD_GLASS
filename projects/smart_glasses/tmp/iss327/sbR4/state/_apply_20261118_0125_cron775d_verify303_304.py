#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
state/_apply_20261118_0125_cron775d_verify303_304.py
================================================================================
★**cron 775d9893 (ARS45 继续执行后继计划) · 2026-11-18 01:2x · 本机实跑** ★

本脚本在同一个 flock 内原子完成两件事 (★兄弟 job fb67af40 不会撞车★):

  ① **ISS-303 验签** (mech-lead): `fixing` → `verified`
  ② **ISS-304 验签** (hw-lead):   `fixing` → `verified`

★**为什么本轮能签两条 (★上一轮不能★)**:
  · ISS-303 · mech-lead · 会话 `agent:mech-lead:subagent:9d1a4f90…` status=**done**
    ⇒ 交卷物在盘 (HANDOFF 27,063 B + logs/iss303/ + 分片 16 条) ⇒ 判「真交卷」
  · ISS-304 · hw-lead · 会话 `agent:hw-lead:subagent:15263ad3…` status=**timeout**
    (abortedLastRun=true · 最后一句停在「Now the fragment write (atomic, via frag_write.py)」)
    ⇒ ★**但交卷物在盘** ⇒ 判「真交卷」不判「僵尸」
    (★MEMORY 铁律③: 「磁盘上已落表」与「这一单交卷了」是两件事 ⇒ 判定看【交卷单填实 + 分片写 + 闸复跑 rc 落盘】· 不看会话 status 单点★)

★**依据 = main 本机实跑 (★不抄 agent 报告·原样 rc★)**

★**边界**: 零写板 · 零落表 · 零改网表/脚表/BOM · 零外发 · 不替老板拍板 · 不自签别的单
"""
from __future__ import annotations

import fcntl
import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")

TODAY = "2026-11-18"

VERIFY_NOTE_303 = (
    "★**main 2026-11-18 01:2x 验签 (cron 775d9893 本机实跑, 不抄 agent 报告)** ★\n"
    "⇒ ★**会话状态**: `agent:mech-lead:subagent:9d1a4f90-0d8a-4d6c-9c99-bb59e1e87d9f` status=**done** (★runtime 858,413 ms · "
    "spawnedBy=fb67af40 那轮) ⇒ ★**真交卷** ★\n"
    "⇒ ★**交付物验收通过 (main 自己数的·不抄交卷单)★**: 交卷单 `HANDOFF/2026-11-18_mech-lead_ISS303_N6合法落表跳.md` = **27,063 B** · "
    "★**真判据 `grep -cE \"🔄 待填\"` = 0** ✔ (★注: 命中「占位符」6 条里那 2 条全是【机制描述 + 自检说明】本身·不是没填的坑★) · "
    "B0/B1/B2/B3/B4/B5/B6 + 交卷声明 = **七块齐全** ★ · "
    "分片 `grep -c iss303 state/fragments/mech.yaml` = **16** (≥5 ✔) · hw/sw/pm 三个分片 **0 命中** ⇒ ★**没写别人的分片** ✔ · "
    "交卷物 4 件齐: 交卷单 + 闸本体 `MECH/check_onepass_struct_crosscheck.py` (改前备份 `.bak_20261118` 留档) + `logs/iss303/` + 分片 ★\n"
    "⇒ ★**main 独立复跑的闸 (★01:2x 实跑·原样 rc★)★**:\n"
    "  · `MECH/check_onepass_struct_crosscheck.py` = **rc=0** (★【绿】N1~N6 全过★ · ★**N6 那条红的已转绿**★)\n"
    "  · `MECH/check_onepass_struct_crosscheck.py --selftest` = **rc=0** (★【自检结果】0 条问题 · 收尾真件 md5 仍逐字节不变★)\n"
    "  · `MECH/check_onepass_mech_release.py` = **rc=0** (★**汇总 6 道闸: 绿 6 / 红 0** ⇒ ★MECH 侧结构可以出 Gerber★)\n"
    "  · `state/gate_check.py` = **rc=0** (★Q7 钉板 md5 闸链 **9/9** ★)\n"
    "⇒ ★**沙盒反向用例 8/8 PASS** (★`logs/iss303/03_sandbox_reverse_cases.log` 原样: ①网表假 md5 红 ②脚表假 md5 红 ③删 ISS-302 行(链断) 红 "
    "④链头不唯一 红 ⑤台账伪造 md5 盘上不符 红 ⑥台账缺失 红(3 条) ⑦改板文件 红(★ISS-296 那条没放松★) ⑧正向对照 rc=0 (★证明不是恒红★)★) ⇒ "
    "★**判据方向没被放宽**: 盘上 md5 ∉ 合法集合 ⇒ 仍然红 ✔ · fail-closed 五条全在 (台账读不到/找不到文件/链头不唯一/链断/链头无单号) ✔\n"
    "⇒ ★**★零写板 / 零落表 (md5 + mtime 双证·main 本机实读·不抄 agent 报告)★**:\n"
    "  · 板 `HW/PCB/demo_mainboard.kicad_pcb` = **611b869e13518c3c023fb178f91a0075** · mtime 仍 **2026-11-06 07:07:17** (★停在本单开工前一周·未动★)\n"
    "  · `.kicad_pro` = **3e504d2be83152e337949723e909be1b** · mtime 仍 **2026-11-04 23:47:30** ✔\n"
    "  · 网表 `6aee500e…` / 脚表 `9174309d…` / BOM `5b999399…` / 台账 `d1a7765b…` 的 mtime = **00:21~00:22** (★那是 ISS-302 的合法落表时刻·早于本单开工 00:5x ⇒ 本单零落表✔★)\n"
    "⇒ ★**★「验签 ≠ 板那一趟可以开工」(★MEMORY 铁律②·本单必须写全三样★)★**:\n"
    "  · 交付时刻 (01:0x) `MECH/check_onepass_mech_release.py` rc=1 (★汇总 绿 5 / 红 1★) ⇒ 红的那道 = N6 ⇒ ★**归属 ISS-303 本单** ⇒ ★**现在 (01:2x) 已转绿 rc=0** ★\n"
    "  · 现在读数: ★**MECH 侧 6 道闸全绿** ⇒ ★**结构侧准出闸链已通** ★\n"
    "  · ★**但 G1 仍不许投板**: ① `stage_gate.py` rc=1 · 当前 **G1** · 还差 **1 项** = ★**PCB 布线 unconnected 45→0 + DRC 0** (ISS-181 · deferred)★ "
    "② 原理图 G1a 还差 **2 条** (G1a-4 / G1a-8) ⇒ ★**这一趟不许开工的真正理由与本单无关** ★\n"
    "⇒ ★**不替老板拍板**: 本单只是【闸机制】修复 (★把「合法落表跳」接进 N6 的判决源·不放宽判据方向★) ⇒ 不新增任何裁决 ★\n"
    "⇒ ★**它自提的 3 条 hint main 已收下 (★登记·不代拍·下一轮随板那一趟处理★)★**: "
    "① `iss303_mech_n6_depends_on_cfc_ledger_api` (本闸依赖 `MECH/check_board_frame_coords.py` 的 5 个名字·改名 ⇒ 本闸 fail-closed 恒红) "
    "② `iss303_mech_n6_membership_vs_equality_caliber` (★N6 成员判定 vs C4 等值判定·台账出现链上历史值时两闸可能分歧·本单按任务书字面口径实现★) "
    "③ ★**本闸对板 2 件仍是纯 md5 硬保护** (★ISS-296 通道只接在 C4 里·没接进本闸★) ⇒ 若板那一趟合法改板一次 ⇒ 本闸 N6 对板会红 ⇒ ★**建议另开一单把通道接进本闸** ★\n"
    "⇒ ★**mech-lead 名额释放** (★此前它以 fixing 占位 ⇒ advance.py 的 in_flight 把 mech-lead 名下所有 open 单全挡住★)"
)

VERIFY_NOTE_304 = (
    "★**main 2026-11-18 01:2x 验签 (cron 775d9893 本机实跑, 不抄 agent 报告)** ★\n"
    "⇒ ★**会话状态**: `agent:hw-lead:subagent:15263ad3-13d9-450c-b433-b7652c5f1585` status=**timeout** (★runtime 821,219 ms · "
    "abortedLastRun=true · 最后一句停在「Now the fragment write (atomic, via frag_write.py)」⇒ ★**会话尾巴没写完就断了**★) ⇒ "
    "★**但交卷物在盘 ⇒ 判「真交卷」不判「僵尸」** (★MEMORY 铁律③: 判定看【交卷单填实 + 分片写 + 闸复跑 rc 落盘】·不看会话 status 单点★) ★\n"
    "⇒ ★**交付物验收通过 (main 自己数的·不抄交卷单)★**: 交卷单 `HANDOFF/2026-11-18_hw-lead_ISS304_作业包现状值重锚.md` = **25,715 B** · "
    "★**真判据 `grep -cE \"🔄 待填\"` = 0** ✔ (★命中「占位符」6 条全是【占位符机制描述 + 自检说明】本身·不是没填的坑★) · "
    "B0/B1/B2/B3/B4/B5/B6 + 附(自证清单) = **齐全** ★ · "
    "分片 `grep -c iss304 state/fragments/hw.yaml` = **9** (≥5 ✔) · mech/sw/pm 三个分片 **0 命中** ⇒ ★**没写别人的分片** ✔ · "
    "`logs/iss304/` **13 个日志齐** (01_before_md5 → 13_q7_final) ★\n"
    "⇒ ★**main 独立复跑的闸 (★01:2x 实跑·原样 rc★)★**:\n"
    "  · `HW/check_workpack_state_values.py` = **rc=0** (★**V4 现状值==盘面实测 那 4 条红已全绿**★ · W10C_MD5_BOM / C07_B26_MD5_LEDGER 等全部 ✔)\n"
    "  · `state/gate_check.py` = **rc=0** (★Q1 18/18 · ★**Q7 钉板 md5 闸链 9/9 全绿** ★)\n"
    "  · `state/merge.py` = **rc=0** · `state/issue_check.py` = **rc=0** (★300 条 · 逾期 0 · 违规 0★)\n"
    "⇒ ★**幂等 (main 读了它自己的日志 + 可复现)★**: ★**真页幂等** (`logs/iss304/05_idempotent_real.log`): 三件 md5 跑前=跑后 **逐字节相同** "
    "(PREFLIGHT `9f9743c8…` / WORKPACKET `0b6fc2f8…` / sidecar `1684c0b0…`) ⇒ ★**跑第二遍不会把页改花** ★ · "
    "★**沙盒两次跑** (`logs/iss304/11_sandbox_two_runs_md5.log`): 沙盒根 `tmp/iss304/sbxT` · 第 1 次 gen rc=0 / sync rc=0 · 第 2 次 rc=0/rc=0 · "
    "★**两次跑完三件 md5 逐字节相同且与真盘一致 ⇒ 真盘零写** ★ · 沙盒反向用例 5 条 (`logs/iss304/10_sbx_tests.log` rc=0) ★\n"
    "⇒ ★**★零写板 / 零落表 (md5 + mtime 双证·main 本机实读·不抄 agent 报告)★**:\n"
    "  · 板 `HW/PCB/demo_mainboard.kicad_pcb` = **611b869e13518c3c023fb178f91a0075** · mtime 仍 **2026-11-06 07:07:17** ✔\n"
    "  · `.kicad_pro` = **3e504d2be83152e337949723e909be1b** · mtime 仍 **2026-11-04 23:47:30** ✔\n"
    "  · 网表 `6aee500e…` / 脚表 `9174309d…` / BOM `5b999399…` mtime = **00:21:08** · 台账 `d1a7765b…` mtime = **00:22:44** "
    "(★那是 ISS-302 的合法落表时刻·早于本单开工 01:09 ⇒ 本单零落表✔★)\n"
    "  · ★**受保护 5 件 md5 逐字节不变** (由 `HW/check_workpack_state_values.py` V6 段独立复核 ✔)\n"
    "⇒ ★**★「验签 ≠ 板那一趟可以开工」(★MEMORY 铁律②·本单必须写全三样★)★**:\n"
    "  · 交付时刻 (01:0x) `HW/check_workpack_state_values.py` rc=1 · ★**V4 4 条红** (W10_MD5_NETLIST / W10B_MD5_PINS / W10C_MD5_BOM / C07_B26_MD5_LEDGER★) ⇒ "
    "★**归属 ISS-304 本单** ⇒ ★**现在 (01:2x) 已转绿 rc=0** ★ · `state/gate_check.py` 交付时刻 rc=1 (Q7 **8/9**) ⇒ 现在 rc=0 (Q7 **9/9**) ★\n"
    "  · ★**但 G1 仍不许投板**: ① `stage_gate.py` rc=1 · 当前 **G1** · 还差 **1 项** = ★**PCB 布线 unconnected 45→0 + DRC 0** (ISS-181 · deferred · "
    "★等老板那 6 个字母·真动板那一趟不许提前开★) ★ ② 原理图 G1a 还差 **2 条** (G1a-4 落表 / G1a-8 关机语义+负载开关) ⇒ ★**与本单无关** ★\n"
    "⇒ ★**本单自提的 need (★登记·不代拍★)★**: `iss304_reanchor_flow_into_f1` (落表后重锚流程两条命令: ① `python3 state/_iss277_build_preflight.py` "
    "② `python3 state/_iss304_sync_state_baseline_md5.py`) · `iss304_25_hardcoded_entries` (★还有 25 处硬编码现值待查·本单没动·留给下一棒★) ★\n"
    "⇒ ★**hw-lead 名额释放** (★此前它以 fixing 占位 ⇒ advance.py 的 in_flight 把 hw-lead 名下所有 open 单全挡住★)"
)


def main() -> int:
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)

        with open(LOG, encoding="utf-8") as f:
            log = yaml.safe_load(f) or {}
        issues = log.get("issues") or []

        signed = []
        for iid, note in (("ISS-303", VERIFY_NOTE_303), ("ISS-304", VERIFY_NOTE_304)):
            for it in issues:
                if it.get("id") != iid:
                    continue
                st = it.get("status")
                if st == "verified":
                    print("★%s 已是 verified ⇒ 跳过 (幂等)" % iid)
                    break
                if st != "fixing":
                    print("★%s status=%s ≠ fixing ⇒ 不签" % (iid, st))
                    break
                it["status"] = "verified"
                it["verify_result"] = "pass"
                it["verify_date"] = TODAY
                it["note"] = (it.get("note") or "") + "\n\n" + note
                signed.append(iid)
                print("✅ %s fixing → verified (verify_result=pass, verify_date=%s)" % (iid, TODAY))
                break

        if signed:
            tmp = LOG + ".tmp.%d" % os.getpid()
            with open(tmp, "w", encoding="utf-8") as f:
                yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)
            os.replace(tmp, LOG)
            print("✅ issue_log.yaml 已原子写回 · 签字 %d 条: %s" % (len(signed), ",".join(signed)))

        fcntl.flock(lk, fcntl.LOCK_UN)
    return 0


if __name__ == "__main__":
    sys.exit(main())
