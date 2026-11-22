#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
moli (项目总工) 2026-11-17 17:5x · job fb67af40「ARS45 队列自动派活」
★ISS-293 续做重派 (僵尸 fixing → open → 再 fixing) + 新开 ISS-295 (mech-lead)★
=========================================================================================
★**为什么有这一趟 (★main 17:4x~17:5x 本机实查盘面 + 读会话, 不抄任何交卷报告★)**:
  · `python3 state/advance.py --json` ⇒ ★**`internal: []` (三条 internal 全被 `fixing` 占着 ⇒ 一个都派不出去)** ★
  · ★**但盘面 ≠ 名单 (★老坑, 第四次了★)** ⇒ ★**本 job 实查三个会话的生死** ★:
    - ★`agent:hw-lead:subagent:4a4fade6` (ISS-292) ★: 17:04:58 起 · **status=running** ⇒ ★**真在飞, 不是僵尸** ★
      ⇒ ★**hw-lead 名额被一条【真在飞的单】占着** ⇒ 本轮跳过它 ★
    - ★`agent:sw-lead:subagent:d5e931dd` (ISS-293) ★: 17:05:53 → 17:18:06 · runtime 733s · **status=failed** ★
      ⇒ ★**死在会话层, 不是活干完** ⇒ 交卷单只剩 **935 B 骨架** + 分片 `grep -c iss293` = **1** ⇒ ★**僵尸 fixing** ★
      ⇒ ★**但大块已在盘上** (★main 17:4x 本机实跑: 文档 90918 B + 新闸 20595 B + 闸 rc=0 29/29 + selftest rc=0 4/4★) ⇒ ★**本趟是【续做】不是从零重做** ★
    - ★`agent:mech-lead:subagent:f1b55bb8` (ISS-294) ★: 16:26:44 → 17:32:18 · **status=done** ⇒ ★**已由 main 17:4x 独立复验落 verified** ★
      (★main 本机实跑: M2 闸 rc=0 + M2 selftest rc=0 + N3 闸 rc=0 + N3 selftest rc=0 + 交卷单 31729 B 无占位符 + 分片 6 条
        + merge rc=0 + gate_check rc=0 Q1 18/18 + 受保护 5 件逐字节不变 + 板 mtime 仍 2026-11-06 07:07:17★)
      ⇒ ★**mech-lead 名额空着** ★
  · ⇒ ★**本趟做两件事**: ①ISS-293 【cont1 续做】重派 (★保持 fixing·不留 open 窗口⇒ 兄弟 job 775d9893 不会重复派★)
    ②新开 ISS-295 (mech-lead) ⇒ ★**三个名额重新全部占满, 且内部待办不断线** ★
★**★铁律**: 干活的人不许自签 ⇒ verify_by=main · ★**零写板 · 零落表** ★
★**★零外发** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★) ⇒ ★**本 job 不发任何邮件/询价/采购** ★
★**边界**: ★**只写 `state/issue_log.yaml` + `state/dispatch_log.yaml` 两个文件** ⇒ ★**不碰任何 agent 的分片**
  (★`state/fragments/*.yaml` 是三个总工的, main 不写★) · 不碰板 / 网表 / 脚表 / BOM / 决策页 / outbox / 任何闸脚本★
"""
import fcntl
import os
import shutil

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
DL = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
BAK = LOG + ".bak_20261117_1750_cronfb67_iss293_cont1_open295"
TODAY = "2026-11-17"

BRIEF_293_CONT = os.path.join(HERE, "dispatch_briefs", "ISS-293_sw_adc_review_sync_cont1.md")
BRIEF_295 = os.path.join(HERE, "dispatch_briefs", "ISS-295_mech_claims_and_verdict_freshness.md")

TITLE_295 = """★★[主线内·MECH 侧·结构输入一次性收口 + 过期结论防漂闸·内部活] ★★【① MECH 两页对同一件事【两种说法】: `BOARD_ONEPASS_STRUCT_CROSSCHECK.md` L68/L175/L188/L1816 仍写「结构侧缺一条边开口规格 (缺口)」, 而 `BOARD_ONEPASS_MECH_SYNC.md` L550 已改成「边开口规格已补」⇒ 机器闸 N3b 只比两页机器块的 openings 矩形 ⇒ 叙事文字漂移 = 绿灯 (SW 侧 ISS-293 刚栽过同一种坑) ② 结构侧输入散成 4 条 need ⇒ 「板只改一次」那一趟开工时结构件必然缺料】★★ ⇒ ★**本单 = 一份「可直接抄进作业包 §3-S6 的结构侧输入认领句全表」 + 一道「过期结论不许再漂」的机器闸 (★纯 MECH 侧文档 + 闸·零写板·零落表·不替老板拍板★)** ★"""

DESC_295 = """★main 2026-11-17 17:4x~17:5x 本机实读盘面 + 实跑 (★不抄任何 agent 报告★)★
★**① 两页口径分叉 (★main 实测命中 5 处·行号级★)**: `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` = 91535 B (ISS-290 交卷物) ⇒ L68 (USB-C-BODY 禁入区行) 仍写「现有 MECH 规格里【没有】这一条 ⇒ 本单登记为缺口 (见 §5 清单 E-6)」· L175 (`J_USB_C` 座体行) 仍写「结构件必须有边开口 (现有 MECH 规格里【没有】这一条)」+ verdict「可装 (三方一致) / ★结构侧缺一条边开口规格 (缺口)」+「开孔 = ★缺口, 待登记★」· L188 (三方一致行) 仍写「1 个: `J_USB_C` (…★但结构侧缺一条边开口规格★)」· L1816 机器块 JSON `"verdict": "可装 (三方一致) / 结构侧缺一条边开口规格"` ⇒ 而 `MECH/BOARD_ONEPASS_MECH_SYNC.md` = 72192 B 的 L550 已改成「可装 / ★边开口规格已补 (X 132.995..147.005 @ 板边 Y=0 · h 三档 · 固定孔清空区 X 133.895..146.105)★」⇒ ★**同一件事两页两种说法** ⇒ (★main 17:4x 已在该页末尾追加 `§E-6-订正` 一节声明那几句是过期文字且老字一字未删留痕 ⇒ ★**现状 = 老行还在 + 末尾有订正节 ⇒ 只 grep 老行的人拿到的还是错结论**★)★
★**② 机器闸只挡了一半**: `MECH/check_onepass_struct_crosscheck.py` N3b (★L630~L641★) 比的是★**两页机器块 `openings[]` 的矩形**★ ⇒ ★**老行里那句过期结论, 机器一个字都不查** ⇒ ★**SW 侧同款病**: `SW/SW_TIMING_REVIEW.md` 停在旧口径 ⇒ 照它判「ADC 链不合格 ⇒ 改板」⇒ 板白改第二遍 ⇒ ★**ISS-293 给 SW 侧建了 `SW/tools/check_timing_review_adc_sync.py` ⇒ MECH 侧还没有对应那道闸** ★
★**③ 结构侧输入散着**: `state/fragments/mech.yaml` 的 `needs_from` 里 ★**9 条 pending 且 to=main**★, 其中 ★**4 条是「板那一趟」的结构侧输入认领**★: `iss271_mech_s6_port_opening_claim` (检修口/调试口开口认领句要挂进 `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` §3-S6) · `iss278_mech_to_hw_board_inputs` (MECH→HW 输入清单) · `iss290_onpass_must_change_list_to_hw` (E-1~E-6 必须随那一趟一起改的清单 · 已转 hw-lead 的 ISS-292「⑬ 追加」节) · `iss294_usbc_edge_opening_size_and_z_window` (第三条开口的 4 条几何取舍 + Z 向窗口 `OPEN_Y_eff(h)` = 4.60/4.60/5.80 不在板面坐标里 ⇒ 本页只能登记不能验) ⇒ ★**散在分片里 ⇒ 谁也没一份「可直接抄进 §3-S6 的完整结构侧输入」⇒ 那一趟开工时结构件必然缺料** ★
★**④ 板面零变化**: 板 `611b869e13518c3c023fb178f91a0075` (mtime 仍 `2026-11-06 07:07:17.362193413`) · `.kicad_pro` `3e504d2be83152e337949723e909be1b` · 网表 `37f62ac3f0b81d92ca7d48fdea717f07` · 脚表 `a4270120454aedf7a23c92cd8985c8a6` · BOM `5d02bece9477ffce5fbe0193c7d5cce4` ⇒ ★**零写板 · 零落表** ★"""


def main() -> int:
    for p in (BRIEF_293_CONT, BRIEF_295):
        if not os.path.exists(p):
            print("⚠ 缺 brief 文件: %s ⇒ 中止" % p)
            return 1

    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        with open(LOG, encoding="utf-8") as f:
            log = yaml.safe_load(f)
        issues = log["issues"]
        by_id = {it["id"]: it for it in issues}

        # ---------- ① ISS-293: open → fixing + 追加 cont1 续做说明 ----------
        i293 = by_id.get("ISS-293")
        if i293 is None:
            print("⚠ ISS-293 不存在 ⇒ 中止")
            return 1
        with open(BRIEF_293_CONT, encoding="utf-8") as f:
            cont293 = f.read()
        if i293.get("status") == "verified":
            print("· ISS-293 已是 verified ⇒ 幂等跳过 (本趟不派)")
        else:
            if "cont1" not in (i293.get("task_brief") or ""):
                i293["task_brief"] = (i293.get("task_brief") or "") + "\n\n---\n\n" + cont293
            i293["status"] = "fixing"
            i293["dispatched_at"] = TODAY
            i293["note"] = (i293.get("note") or "") + (
                "\n★★2026-11-17 17:5x 队列自动派活 job (fb67af40) 【cont1 续做】重派 (★不是从零重做★) ★★: "
                "子会话 `agent:sw-lead:subagent:d5e931dd` (sessionId cfd5aeac) 17:05:53 → 17:18:06 · runtime 733s · "
                "status=failed ⇒ 交卷单停在 935 B 骨架 (7 项进度只勾了「读任务书全文」) + 分片 `grep -c iss293` = 1 "
                "(只有那条 need) ⇒ ★**但大块已在盘上** (★main 17:4x 本机实跑: `SW/SW_TIMING_REVIEW.md` = 90918 B (mtime 17:11:55) · "
                "`SW/tools/check_timing_review_adc_sync.py` = 20595 B (mtime 17:11:12) · 闸 rc=0 29/29 项通过 · "
                "--selftest rc=0 SELFTEST 4/4 通过 ⇒ 真件读回 90918 B 未变★) ⇒ ★**本趟只补 4 件**: "
                "F1 交卷单 B0~B6 填满 (占位符 0) · F2 B1 逐条对账表 (只补漏, 不许整份重写文档) · "
                "F3 回归 6 条自己跑一遍贴原样 rc · F4 分片补完 (artifacts 3 + interface_claim + status · "
                "走 frag_write.py 原子写 · grep -c iss293 ≥ 4) ⇒ ★**续做任务书全文 = "
                "`state/dispatch_briefs/ISS-293_sw_adc_review_sync_cont1.md` (★4433 B · "
                "check_brief_commands --brief-file ⇒ rc=0★)** ⇒ ★**status 全程 fixing ⇒ 无 open 窗口 ⇒ "
                "兄弟 job 775d9893 不会重复派** ★")
            print("✅ ISS-293 open → fixing + cont1 续做说明已追加")

        # ---------- ② 新开 ISS-295 (mech-lead) ----------
        with open(BRIEF_295, encoding="utf-8") as f:
            brief295 = f.read()
        if "ISS-295" in by_id:
            print("· ISS-295 已存在 ⇒ 幂等跳过")
        else:
            issues.append({
                "id": "ISS-295",
                "title": TITLE_295,
                "severity": "high",
                "source_blocker": None,
                "source_agent": "main",
                "desc": DESC_295,
                "owner": "mech-lead",
                "reporter": "main",
                "raised": TODAY,
                "due": "2026-11-20",
                # ★★ 直接落 fixing (★先落 fixing 再 spawn·不留 open 窗口·防兄弟 job 重复派★)
                "status": "fixing",
                "external": False,
                "need_keys": [],
                "fix_ref": "",
                "verify_by": "main",
                "verify_result": "",
                "verify_date": "",
                "note": ("★main 2026-11-17 17:5x 新开 (cron fb67af40 队列自动派活) ⇒ ★**零写板 · 零落表 · "
                         "零改网表/脚表/BOM · 只动 MECH 侧两份页 + 新建两份件** ★ ⇒ ★**任务书全文 = "
                         "`state/dispatch_briefs/ISS-295_mech_claims_and_verdict_freshness.md` "
                         "(★7179 B · 已过 `python3 state/check_brief_commands.py --brief-file` ⇒ rc=0★)** ⇒ "
                         "★**第一条 (必做)**: 先 cat 那份任务书全文 ★ ⇒ ★**本单是 ISS-294 复验时挖出的后续缺口: "
                         "MECH 两页对「USB-C 边开口」有两种说法 + 叙事文字没有防漂闸 (SW 侧 ISS-293 已治同一种病) + "
                         "结构侧输入散成 4 条 need** ★ ⇒ ★**本单零外发 (老板 2026-11-11 19:31 + 2026-11-12 02:02: "
                         "不再发信, 全靠自己查资料) ⇒ 缺口一律自己网上查 + 标证据等级 + 查不到就写降级方案** ★"),
                "dispatched_at": TODAY,
                "task_brief": brief295,
            })
            print("✅ ISS-295 已开 (owner=mech-lead · status=fixing · due=2026-11-20)")

        shutil.copy2(LOG, BAK)
        tmp = LOG + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)
        os.replace(tmp, LOG)

        # ---------- 派活日志 ----------
        with open(DL, encoding="utf-8") as f:
            dl = yaml.safe_load(f) or {}
        dl.setdefault("dispatches", []).append({
            "issue": "ISS-293",
            "agent": "sw-lead",
            "at": TODAY,
            "brief": ("★**【cont1 续做】重派 (★不是从零做★)★**: 会话 `agent:sw-lead:subagent:d5e931dd` 17:05:53 → "
                      "17:18:06 · runtime 733s · status=failed ⇒ 交卷单只剩 935 B 骨架 + 分片只 1 条 ⇒ "
                      "★**但大块已在盘上** (★main 17:4x 本机实跑: 文档 90918 B + 新闸 20595 B · 闸 rc=0 29/29 · "
                      "selftest rc=0 4/4★) ⇒ ★**本趟只补 4 件**: 交卷单 B0~B6 填满 · B1 逐条对账表 · "
                      "回归 6 条自己跑 · 分片补完 (grep -c iss293 ≥ 4) ★"),
            "job": "★派活方 = cron fb67af40 (ARS45 队列自动派活) 于 17:5x 续做重派 · ★**brief = issue_log 里 "
                   "ISS-293 的 task_brief (★已含本 job 追加的 cont1 节★) ⇒ ★完整续做任务书 = "
                   "`state/dispatch_briefs/ISS-293_sw_adc_review_sync_cont1.md` (★4433 B · "
                   "check_brief_commands --brief-file ⇒ rc=0★)★ · ★**status 全程保持 fixing ⇒ 无 open 窗口 ⇒ "
                   "兄弟 job 775d9893 不会重复派**★",
        })
        dl.setdefault("dispatches", []).append({
            "issue": "ISS-295",
            "agent": "mech-lead",
            "at": TODAY,
            "brief": ("★main 17:4x 复验 ISS-294 时挖出的后续缺口: ① MECH 两页对「USB-C 边开口」【两种说法】"
                      "(STRUCT_CROSSCHECK L68/L175/L188/L1816 仍写「结构侧缺一条边开口规格 (缺口)」 · "
                      "MECH_SYNC L550 已写「边开口规格已补」) ② 机器闸 N3b 只比两页 openings 矩形 ⇒ "
                      "叙事文字漂移 = 绿灯 (SW 侧 ISS-293 刚栽过同一种坑) ③ 结构侧输入散成 4 条 need ⇒ "
                      "「板只改一次」那一趟开工时结构件必然缺料 ⇒ ★**本单 = 一份可直接抄进作业包 §3-S6 的"
                      "结构侧输入认领句全表 + 一道过期结论防漂闸 (零写板·零落表·不代拍)** ★"),
            "job": "★派活方 = cron fb67af40 (ARS45 队列自动派活) 于 17:5x 新开并派出 · ★**brief = issue_log 里 "
                   "ISS-295 的 task_brief 全文 (= state/dispatch_briefs/ISS-295_mech_claims_and_verdict_freshness.md)★ "
                   "· ★**先落 fixing 再 spawn ⇒ 无 open 窗口 ⇒ 兄弟 job 775d9893 不会重复派**★",
        })
        tmp_dl = DL + ".tmp"
        with open(tmp_dl, "w", encoding="utf-8") as f:
            yaml.safe_dump(dl, f, allow_unicode=True, sort_keys=False, width=200)
        os.replace(tmp_dl, DL)
        print("✅ dispatch_log 已写 2 条 (ISS-293 / ISS-295)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
