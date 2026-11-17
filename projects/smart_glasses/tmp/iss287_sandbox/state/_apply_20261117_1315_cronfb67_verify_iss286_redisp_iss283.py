#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""state/_apply_20261117_1315_cronfb67_verify_iss286_redisp_iss283.py

★main 2026-11-17 13:1x (cron fb67af40 队列自动派活)★

★**为什么有这一趟**: ★`advance.py --json` 实测 `internal: []` (三个名额全被 `fixing` 占着) ⇒
  ★**盘面 ≠ 名单**: 实查两种状态完全相反 ★
  ① **ISS-286 (mech-lead)**: 会话 `agent:mech-lead:subagent:ea2ee0d7` 实测 **status=done (12:47 交卷)**,
     交付物全在盘 ⇒ ★**但 status 还挂在 `fixing` ⇒ mech-lead 名额被一条已经干完的单占着 ⇒ 队列静默断线** ★
  ② **ISS-283 (hw-lead)**: 会话 `agent:hw-lead:subagent:adfd437a` 实测 **status=timeout (12:51 被 abort)**,
     交卷单只 8105 B (B2/B3/⑩/⑪/③/收尾/自检 全「⏳」) · 分片 `state/fragments/hw.yaml` grep `iss283` = **0** ⇒
     ★**半落地僵尸** ⇒ 而且 abort 前最后一次编辑把 ⑪ C6 那道闸留在【半成品】状态 ⇒
     ★`HW/check_board_frame_caliber.py --selftest` 实测 **rc=1 · 12 条失败 2 条 (⑤b / ⑤c)** ★ ⇒
     ★**盘上现在有一道红的闸没人管** ★

★**本脚本做两件事**: ①**ISS-286 落 verified** (★main 本机独立实跑复验, 不抄交卷报告★)
  ②**ISS-283 记续做重派** (★status 保持 `fixing` ⇒ 不动, 免得下一轮 cron 重复派同一 agent★; 只补 dispatched_at/note★)

★**边界**: 只写 state/issue_log.yaml + state/dispatch_log.yaml; 不碰板/网表/脚表/BOM;
  不写任何分片; 不替老板拍板; 零外发。★
"""
import os
import shutil
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG_P = os.path.join(HERE, "issue_log.yaml")
DL_P = os.path.join(HERE, "dispatch_log.yaml")
TODAY = "2026-11-17"


def main() -> int:
    # ---------- 备份 ----------
    bak = os.path.join(HERE, ".bak_iss286_283_1315")
    os.makedirs(bak, exist_ok=True)
    for p in (LOG_P, DL_P):
        shutil.copy2(p, os.path.join(bak, os.path.basename(p) + ".bak_1315"))

    log = yaml.safe_load(open(LOG_P, encoding="utf-8"))
    issues = log["issues"]
    by_id = {it["id"]: it for it in issues}

    changed = []

    # ---------- ① ISS-286 落 verified (main 本机独立实跑复验) ----------
    i286 = by_id["ISS-286"]
    assert i286["status"] == "fixing", i286["status"]
    i286["status"] = "verified"
    i286["verify_by"] = "main"
    i286["verify_date"] = TODAY
    i286["fix_ref"] = "HANDOFF/2026-11-17_mech-lead_ISS286_坐标归一闸台账化.md"
    i286["verify_result"] = (
        "★main 2026-11-17 13:0x~13:1x 本机独立实跑复验 (不抄交卷报告)★ "
        "⇒ `python3 MECH/check_board_frame_coords.py` **rc=0** (C1~C4 全过 · 实读输出: 板/`.kicad_pro` 两行写死基线 MATCH "
        "⇒ 网表/脚表/BOM 三件【判决源 = 落表台账链头】⇒ 37f62ac3f0b8 / a4270120454a / 5d02bece9477 (★by ISS-283★ · 台账记录 10 条)) "
        "⇒ `python3 MECH/check_board_frame_coords.py --selftest` **rc=0 【自检结论 ✅ 一致】** (★12 条全抓到★: 合法落表⇒绿 / "
        "台账查不到登记⇒红 / 盘上≠链头⇒红 / 台账手改(单号不齐·文件名不对·前 md5 假值)⇒红 / 链头不唯一⇒红 / 受保护件被改⇒红 / "
        "真件 6 件跑完自检后仍逐字节不变) "
        "⇒ `python3 MECH/check_demo_struct_truth.py` **rc=0 (23/23 组检查通过 · FAIL 0 组)** "
        "⇒ `python3 state/merge.py` **rc=0** (STATE.yaml 已刷新) "
        "⇒ `python3 state/gate_check.py` **rc=0** (★全部检查项通过 · Q1 18/18★) "
        "⇒ 板 `611b869e13518c3c023fb178f91a0075` + `.kicad_pro` `3e504d2be83152e337949723e909be1b` **逐字节未变** "
        "⇒ 交付物在盘: 交卷单 21916 B (★B1~B6 六块齐全 · grep「施工中/待填」= 0 处残留★) · 分片 `state/fragments/mech.yaml` "
        "grep `iss286` = 3 (含 1 条 need) · 原始日志 `logs/iss286/acceptance_01..05.log` 五份 "
        "⇒ ★**C4 的判决源已从【写死 md5 基线】换成【落表台账链头】⇒ 合法落表不再红 (40 分钟内红了三遍那个病根拔掉), "
        "偷换真源仍红 (fail-closed 五条一条没放宽)★** "
        "⇒ ★**遗留 (agent 自己主动交代, main 认可): 「台账被改得完全自洽」这一路仍绿 ⇒ 更上游的「落表授权通道」归 HW 侧/main, 不在本单范围** ★"
    )
    i286["note"] = (i286.get("note") or "") + (
        " | 2026-11-17 13:1x (cron fb67af40 队列自动派活) ★main 独立复验通过 ⇒ 落 verified★ "
        "⇒ 依据 = 本机实跑 check_board_frame_coords.py rc=0 + --selftest rc=0(12/12 一致) + check_demo_struct_truth.py rc=0(23/23) "
        "+ merge rc=0 + gate_check rc=0(Q1 18/18) + 板/.kicad_pro md5 逐字节未变 "
        "⇒ ★**mech-lead 名额已释放 (★但 mech-lead 名下无 open 待办 ⇒ 仍不派·不为了凑数乱派★)** ★"
    )
    changed.append("ISS-286 fixing → verified (main 独立复验)")

    # ---------- ② ISS-283 记续做重派 (status 保持 fixing) ----------
    i283 = by_id["ISS-283"]
    assert i283["status"] == "fixing", i283["status"]
    i283["dispatched_at"] = "2026-11-17 13:1x (cron fb67af40 续做重派 cont2)"
    i283["note"] = (i283.get("note") or "") + (
        " | 2026-11-17 13:1x (cron fb67af40) ★**上一趟 (会话 adfd437a) 12:51 被 abort ⇒ 半落地僵尸 ⇒ 续做重派 cont2** ★ "
        "⇒ main 实测盘面: A3 (V-2=1) 真落 12:16:08 rc=0 ✔ · B1 守卫 + `--migrate-id-str` + T17/T18 ✔ · "
        "★**但 B2/B3/⑩/⑪/③/收尾/交卷自检 全「⏳」+ 分片 grep iss283 = 0 ⇒ 交卷不成立** ★ "
        "⇒ ★**且 abort 前最后一次编辑把 `HW/check_board_frame_caliber.py` ⑪ C6 留在半成品 ⇒ `--selftest` rc=1 · 12 条失败 2 条 "
        "(⑤b 突变没咬到目标 ⇒ md5 没变 / ⑤c 突变真改到了但 C6 仍绿 ⇒ 判据缺一路) ⇒ 盘上现在有一道红的闸** ★ "
        "⇒ 任务书 `state/dispatch_briefs/ISS-283_cont2_v2_continue.md` (15279 B · 派活前 check_brief_commands rc=0 零告警) "
        "⇒ ★**板 611b869e… / .kicad_pro 3e504d2b… 逐字节未变 ⇒ 板仍是「旧网表的板」⇒ Gerber/投产包一律不许用** ★"
    )
    changed.append("ISS-283 保持 fixing (续做重派 cont2 · 已记 dispatched_at/note)")

    # ---------- 落盘 ----------
    with open(LOG_P, "w", encoding="utf-8") as f:
        yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)

    dl = yaml.safe_load(open(DL_P, encoding="utf-8")) if os.path.exists(DL_P) else {"dispatches": []}
    dl.setdefault("dispatches", []).extend([
        {"issue": "ISS-286", "agent": "mech-lead", "at": TODAY,
         "brief": "★main 13:1x 独立复验 rc=0 + selftest 12/12 + demo_struct_truth 23/23 + merge 0 + gate_check 0 ⇒ 落 verified "
                  "(释放 mech-lead 名额; ★名下无 open 待办 ⇒ 不派★)"},
        {"issue": "ISS-283", "agent": "hw-lead", "at": TODAY,
         "brief": "★续做重派 cont2 (★上一趟 adfd437a 12:51 被 abort ⇒ 半落地★): 任务书 "
                  "state/dispatch_briefs/ISS-283_cont2_v2_continue.md (15279 B · check_brief_commands rc=0) "
                  "⇒ 续做 ⑪ C6 (--selftest 现在 rc=1 · 失败 2 条: ⑤b 突变没咬到 / ⑤c 判据缺一路) + B2 Q_PG 写法A 落表 + "
                  "B3 LED 亮度档落表 + ⑩ 两道过期闸收口 + ③ 板侧清单 §③ + 收尾全套 rc + 分片 ⇒ 零写板"},
    ])
    with open(DL_P, "w", encoding="utf-8") as f:
        yaml.safe_dump(dl, f, allow_unicode=True, sort_keys=False, width=200)

    print("=== 已落 ===")
    for c in changed:
        print(" ·", c)
    print("备份 →", bak)
    return 0


if __name__ == "__main__":
    sys.exit(main())
