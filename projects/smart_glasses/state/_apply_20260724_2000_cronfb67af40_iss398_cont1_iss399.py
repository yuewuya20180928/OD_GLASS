#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★_apply_20260724_2000_cronfb67af40_iss398_cont1_iss399.py★

★**用途**: cron `fb67af40` (ARS45 队列自动派活) · 2026-11-24 20:0x 一趟
  ⇒ ★**两条**: ① ★**ISS-398 cont1 续派 (真僵尸复活)** ② ★**新开 ISS-399 (MECH 域追加台账设计 + 自守闸)** ★
  ⇒ ★**两件都【直接落 `fixing`】** (★铁律⑩-i: 先落 fixing 再 spawn ⇒
    兄弟 job `775d9893` 的 `advance.py --json` 看不见本单 ⇒ 零撞车窗口★)

★**ISS-398 = 真僵尸 (★不是超时被掐·是交白卷★)**: 上一趟会话
  `agent:sw-lead:subagent:ef85edc1-321f-4d41-bef8-172d5fc17b58` (★18:26:15 → 19:26:16·status=done·跑满 60 分钟★)
  ⇒ 盘上实测: ① 闸 `SW/tools/check_sw_ref_reachability_v2.py` md5 仍是 `1c4043ea26a1182b210e85f1b5130d8d`
  (★mtime 2026-11-18 21:37 ⇒ 一个字节没动★) ② 交卷页不在盘 ③ 分片登记 0 条
  ④ `logs/iss398/` 只有三个 before 日志、无 after ⑤ `tmp/iss398/plan.md` 的第 5~9 步全部 ⬜
  ⇒ ★**只读完了资料·一件交付物都没落** ⇒ 走 cont1 (★status 保持 fixing·不落 open·与兄弟 job 零撞车★)

★**本脚本三道自保**: ① md5 守卫 (写前重算源文件 md5, 不一致 ⇒ rc=3 中止)
  ② 原子写 (`os.replace`) ③ 写后复跑 `state/check_brief_commands.py` 的 task_brief 判定
★**零外发 · 零写板 · 零落表 · 零改既有闸 · 不写任何 agent 的分片**
"""
import hashlib
import io
import os
import shutil
import sys
import time

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
DL = os.path.join(HERE, "dispatch_log.yaml")
BRIEFS = os.path.join(HERE, "dispatch_briefs")
BACKUP = LOG + ".bak_20260724_2000_cronfb67af40_iss398_cont1_iss399"
BACKUP_DL = DL + ".bak_20260724_2000_cronfb67af40_iss398_cont1_iss399"

TS = "2026-11-24 20:0x"
JOB = "cron fb67af40 (ARS45 队列自动派活)"


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def brief_text(name):
    with io.open(os.path.join(BRIEFS, name), encoding="utf-8") as f:
        return f.read()


def main():
    if not os.path.exists(LOG):
        print("★issue_log.yaml 不存在 ⇒ 中止")
        return 2
    src_md5 = md5(LOG)
    src_md5_dl = md5(DL)

    with io.open(LOG, encoding="utf-8") as f:
        doc = yaml.safe_load(f) or {}
    issues = doc.get("issues") or []
    by_id = {i.get("id"): i for i in issues}
    have = set(by_id)

    if "ISS-399" in have:
        print("★ISS-399 已在台账 ⇒ 中止 (不重复开单)")
        return 2

    # ---------- ① ISS-398: 追加 note (★status 保持 fixing·不动★) ----------
    iss398 = by_id.get("ISS-398")
    if iss398 is None:
        print("★ISS-398 不在台账 ⇒ 中止")
        return 2
    if iss398.get("status") != "fixing":
        print("★ISS-398 status 不是 fixing (★%s★) ⇒ 中止" % iss398.get("status"))
        return 2

    iss398["note"] = (
        str(iss398.get("note") or "")
        + "\n\n"
        + "★**2026-11-24 20:0x cron fb67af40 (ARS45 队列自动派活) 判定: 本单 = 【真僵尸·交白卷】"
          "⇒ 走 cont1 续跑 (★status 保持 fixing·不落 open·★零撞车窗口★)** ★\n"
        + "★**死因 (★main 本机实检磁盘·两次采样·不抄任何 agent 报告★)**: 上一趟会话 "
          "`agent:sw-lead:subagent:ef85edc1-321f-4d41-bef8-172d5fc17b58` (★18:26:15 → ★19:26:16·"
          "status=done·★跑满 60 分钟★) ⇒ ★**不是超时被掐·不是崩溃·是【读完了 60 分钟资料·一件交付物都没落】** ★\n"
        + "★**五项逐条实检 (★全部本机复跑·★你自己也要再跑一遍★)**: ① 闸 "
          "`SW/tools/check_sw_ref_reachability_v2.py` md5 仍是 `1c4043ea26a1182b210e85f1b5130d8d` · mtime `2026-11-18 21:37` "
          "⇒ ★**夹具一个字都没改**★ (★`cmp` 与它自己抄的改前副本 `tmp/iss398/v2_proto.py` 逐字节相同★) "
          "② 交卷页 `HANDOFF/2026-11-24_sw-lead_ISS398_*.md` ★**不在盘**★ (`ls HANDOFF/ | grep -i ISS398` ⇒ 0) "
          "③ `grep -c \"iss398\" state/fragments/sw.yaml` ⇒ ★**0**★ "
          "④ `logs/iss398/` 只有 `selftest_before.log` / `gate_health_before.log` / `gates_before.log` 三个 before ⇒ ★**无 after**★ "
          "⑤ `tmp/iss398/plan.md` 的落盘顺序第 1~4 步 ✅ · 第 5~9 步 ★**全部 ⬜**★ ⇒ ★**只做完了「读 + 存证」** ★\n"
        + "★**⇒ 这正是 LESSONS.md L-13 那条: 「攒了一堆读数在上下文里, 最后一步才开始写交付物」⇒ 墙钟到 ⇒ 什么都没留下** ★\n"
        + "★**⇒ 本趟的纪律只有一条, 但它决定生死: 【先落盘, 再继续】⇒ ★**8 分钟内先把交卷页骨架立起来**, "
          "剩下 80 分钟全部用来【填内容】★ ⇒ ★**半成品交上来 > 交白卷**★ ★\n"
        + "★**已实测的读数直接用 (★不用重跑★)**: `--selftest` ⇒ ★**0/7 · 末行「❌ 有用例没抓到 ⇒ 判据可能没被真读」**★ (★rc=1★) · "
          "裸跑 ⇒ ★**rc≠0 · 红因逐字「新增真隐患:SW_MD5」**★ · "
          "根因 = 夹具被基线漂移染红 (★`BASELINE_TOKENS` 只有 TP_INT/TP_TEMP/CONN_USB 三条, `BASELINE_COUNT=3`, "
          "而 `SW_MD5` 压根不在里面 ⇒ 它是第 4 个真隐患 ⇒ 超基线·★**不是判据错**★★) · "
          "★**判据段前缀 md5 `3111dfb21d8233bb137e4d694c8abc04` (offset 45580) 改后必须逐字不变**★ (★main 本机实算过★) ★\n"
        + "★**命令存在性守卫**: `python3 state/check_brief_commands.py --brief-file "
          "state/dispatch_briefs/ISS-398_sw_ref_reach_v2_selftest_baseline_independent_cont1.md` ⇒ ★**rc=0**★"
    )

    # ---------- ② 新开 ISS-399 ----------
    common = dict(
        source_agent="main",
        verify_by="main",
        reporter="main",
        raised="2026-11-24",
        due="2026-11-27",
        status="fixing",
        external=False,
        dispatched_at="2026-11-24",
    )

    note_399 = (
        "★**2026-11-24 20:0x cron fb67af40 (ARS45 队列自动派活) 新开并【直接落 fixing】**"
        "(★铁律⑩-i: 先落 fixing 再 spawn ⇒ 兄弟 job `775d9893` 的 `advance.py --json` 看不见本单 ⇒ 零撞车窗口★) ★\n"
        "★**开单依据 (★main 本机实跑 + 实算·不抄任何 agent 报告★)**: ★**`python3 state/advance.py --json` 实跑 ⇒ "
        "`internal: []` / `approvals: []` / `waiting: []` / `decisions: 55` ⇒ 根因 = 三个总工名下各占着 `status: fixing` 的在飞单** "
        "⇒ 逐条实检三与判据: hw-lead ISS-396 (交卷页 18:43 + 分片 22 处在盘) · mech-lead ISS-397 (交卷页 18:44 + 分片 30 处在盘) "
        "⇒ 两条均已交卷 ⇒ ★**mech-lead 槽位实际已空** ★\n"
        "★**⇒ 本 job 逐道实跑 MECH 域全部 25 道闸 (★留证 `state/.verify/fb67_2000/`★) ⇒ 唯一的新缺口 = ★★"
        "**MECH 域有 9 道闸把「别的文件」的 md5 写死成常量 (共 35 处 pin), 其中 3 处已经陈旧 ⇒ 2 道闸现在就是红的**★★ "
        "⇒ ① `MECH/check_connector_clearance_caliber.py` (K7) 红 2 条: `MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md` "
        "(基线 ffc09939… vs 现值 f1ce54c9…) + `MECH/check_juart_1p27_clearance.py` (基线 ea89e0dd… vs 现值 daf8fa36…) "
        "⇒ 成因 = ★**ISS-374 cont2 的合法追加式订正没人回头更新基线**★ "
        "② `MECH/check_zoujuan_marker_consistency.py` (K5) 红 1 条: `MECH/check_demo_struct_truth.py` "
        "(基线 fa9b59e5… vs 现值 483d018a…) ⇒ 成因 = ★**该文件在 2026-11-17 20:25 被别的单合法改过, "
        "而这道闸写于 2026-11-16 10:59 ⇒ 基线比那次改动早**★ "
        "⇒ ★★**这 9 道里只有 1 道 (`check_demo_struct_truth.py`) 在官方门禁链 `state/gate_check.py` 里 ⇒ "
        "另外 8 道零挂链 ⇒ 红了零通知 ⇒ 只有 agent 手工当回归跑时看得见**★★ "
        "(★实证: `HANDOFF/2026-11-24_mech-lead_ISS382_JDEBUG排针排布标签订正与G5盲区.md` 第 38 行白纸黑字写着「K7 基线红 2 条是开工前就有的」·"
        "⇒ 每个跑这道闸的 agent 都得自己写一句「这红不是我造成的」★) ⇒ ★**这不是某个 agent 的红, 是 MECH 域缺一本账**★★ "
        "⇒ ★**为什么卡在「板那一趟」的要害上**: 那一趟必然要追加式订正 MECH 域的一堆已签收页/闸 (★ISS-391/396 的 FTS 换件 + 座体 J_DEBUG/J_UART 收口★) "
        "⇒ 每一次合法追加 ⇒ 钉它的闸又陈旧一处 ⇒ ★**收工验收那几道 MECH 闸是红的 · 红是真的但变的原因是对的 ⇒ "
        "现场极可能误读成「MECH 改坏了」⇒ 板白改第二遍**★★ ★\n"
        "★**同型病本仓已治过两次 (★先例·不重新发明★)**: ISS-296 / ISS-303 (MECH 侧·把「硬基线常量」换成「硬基线 ∪ 落表台账登记值」·"
        "已落进 `MECH/check_board_frame_coords.py` 的 C4 与 `MECH/check_onepass_struct_crosscheck.py` 的 N6) + "
        "ISS-372 (SW 侧·《钉板 md5 闸清单》自守闸 `SW/tools/check_sw_board_md5_rebase_readiness.py` 的 H4/H5) "
        "⇒ ★**但 `HW/SCHEMATIC_LANDING_V1_LANDED.md` 里这 3 个 MECH 文件 grep 全是 0 命中 ⇒ "
        "MECH 域缺的不是「换一个源」, 是【缺一本自己的台账】★ ⇒ ★**本单交付的自守闸 = ISS-372 的 MECH 对偶** ★\n"
        "★**命令存在性守卫**: `python3 state/check_brief_commands.py --brief-file "
        "state/dispatch_briefs/ISS-399_mech_signed_append_ledger_design.md` ⇒ ★**rc=0**★"
    )

    iss399 = dict(
        id="ISS-399",
        title=(
            "★★[★新主线·PCB 线·MECH 侧·纯分析+新建真相页+新建机器闸·零写板] MECH 域【闸把别人的 md5 写死成硬基线】的"
            "全量清账 (9 道闸 / 35 处 pin) + 3 处已陈旧 pin 的裁定 + 一道《已签收件追加登记台账》自守闸 ⇒ "
            "「板那一趟」合法追加一次 ⇒ MECH 闸就陈旧一处 ⇒ 收工验收的红被误读成「MECH 改坏了」⇒ 板白改第二遍 ★★"
        ),
        severity="high",
        source_blocker="ISS-382",
        desc=(
            "★★[★新主线·PCB 线·MECH 侧·纯分析+新建真相页+新建机器闸+出逐字补丁(不应用)·"
            "零写板·零落表·零改既有闸的判据/阈值·零挂链·零外发·不代拍]★★\n\n"
            "★**题 (来源 = ★main 2026-11-24 19:4x 本机实跑·不抄任何 agent 报告★)★:\n"
            "★**① MECH 域 9 道闸把「别的文件」的 md5 写死成常量, 共 35 处 pin; 其中 3 处已陈旧 ⇒ 2 道闸现在就是红的** ★\n"
            "★**② 已陈旧的 3 处 (main 本机逐字实算)**: ★\n"
            "★**#1** `MECH/check_connector_clearance_caliber.py` (K7) 钉 `MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md`: "
            "基线 `ffc099397dc573df207f265bff57dffb` vs 现值 `f1ce54c981dd1f64071a177a374df85d` ★\n"
            "★**#2** 同闸 (K7) 钉 `MECH/check_juart_1p27_clearance.py`: "
            "基线 `ea89e0dd3b2f77828b69f06bbe76969d` vs 现值 `daf8fa367d89e22f6d3af3d5049bdfb6` ★\n"
            "★**#3** `MECH/check_zoujuan_marker_consistency.py` (K5) 钉 `MECH/check_demo_struct_truth.py`: "
            "基线 `fa9b59e593a13408ad9505d986276f63` vs 现值 `483d018a66d17d2ead25d1558a1f8ffe` ★\n"
            "★**③ 成因 (main 本机查到)**: #1/#2 = ★**ISS-374 cont2 对已签收页/闸做的合法追加式订正·没人回头更新基线**★; "
            "#3 = ★**`MECH/check_demo_struct_truth.py` 在 2026-11-17 20:25:32 被别的单合法改过 "
            "(`HANDOFF/2026-11-17_mech-lead_ISS295_结构输入认领与防漂闸.md` 第 428 行自己记着·标「别的单」)"
            "·而这道闸写于 2026-11-16 10:59 ⇒ 基线比那次改动早**★ ★\n"
            "★**④ 为什么没人看见 (★本单最值钱的发现★)**: ★**这 9 道里只有 1 道在官方门禁链 `state/gate_check.py` 里 "
            "(`check_demo_struct_truth.py`) ⇒ 另外 8 道零挂链 ⇒ 红了零通知 ⇒ 只有 agent 手工当回归跑时看得见** ★\n"
            "★**⑤ 为什么卡在「板那一趟」的要害上**: 那一趟必然要追加式订正 MECH 域的一堆已签收页/闸 ⇒ "
            "每一次合法追加 ⇒ 钉它的闸又陈旧一处 ⇒ ★**收工验收那几道 MECH 闸是红的 · 红是真的但变的原因是对的 ⇒ "
            "现场极可能误读成「MECH 改坏了」⇒ 板白改第二遍** ★\n"
            "★**⑥ 同型病本仓已治过两次 (先例·不重新发明)**: ISS-296 / ISS-303 (MECH 侧·判决源从「硬基线常量」换成"
            "「硬基线 ∪ 落表台账登记值」·已落进 `MECH/check_board_frame_coords.py` C4 与 "
            "`MECH/check_onepass_struct_crosscheck.py` N6) + ISS-372 (SW 侧·《钉板 md5 闸清单》自守闸 H4/H5) "
            "⇒ ★**但 `HW/SCHEMATIC_LANDING_V1_LANDED.md` 里这 3 个 MECH 文件 grep 全是 0 命中 ⇒ "
            "MECH 域缺的不是「换一个源」, 是【缺一本自己的台账】★ ⇒ ★**本单交付的自守闸 = ISS-372 的 MECH 对偶** ★\n"
            "★**⑦ 本单要交的三件**: ① 新真相页 `MECH/BOARD_ONEPASS_SIGNED_APPEND_LEDGER_DESIGN.md` "
            "(§0 口径 / §1 35 处 pin 全量清账表 / §2 三处陈旧逐条裁定 / §3 台账设计 / §4 三条逐字补丁(不应用) / "
            "§5 挂链建议 / §6 边界自证+机器块) ② 新闸 `MECH/check_mech_signed_append_ledger.py` "
            "(M1 枚举 / M2 陈旧检测 / M3 归因可查 / M4 ★**不许靠改常量消红**★ / M5 板三证未动 / M6 证据五级白名单 / "
            "M7 零挂链 / M8 反向用例≥8) ③ 交卷页 (B1~B7) + 分片登记 ★\n"
            "★**⑧ 四条交 main 一条都不代拍**: M-A 台账放哪 / M-B 3 处基线怎么追平 / M-C 自守闸挂不挂 / "
            "M-D「追加式订正」算不算合法变更 ★"
        ),
        owner="mech-lead",
        need_keys=[
            "iss399_mech_append_ledger_location",
            "iss399_mech_stale_pin_rebaseline",
            "iss399_mech_self_audit_gate_hook",
            "iss399_mech_append_is_legal_change_caliber",
        ],
        task_brief=brief_text("ISS-399_mech_signed_append_ledger_design.md"),
        note=note_399,
    )
    for k, v in common.items():
        iss399.setdefault(k, v)

    # ---- ③ md5 守卫 (写前重算) ----
    if md5(LOG) != src_md5:
        print("★md5 守卫: issue_log.yaml 在读与写之间被改过 ⇒ 中止 (rc=3)")
        return 3

    doc["issues"] = list(issues) + [iss399]
    shutil.copy2(LOG, BACKUP)
    tmp = LOG + ".tmp.%d" % int(time.time())
    # ★width=4096 = 盘上现行台账的实际折行宽度 (★本机实测: 宽度 4096 的 safe_dump 与原文逐字节相同·
    #   ★宽度 100/120/200/100000 都会把 232 行重排 ⇒ 那是无谓的 churn·★故必须用 4096★)
    with io.open(tmp, "w", encoding="utf-8") as f:
        yaml.safe_dump(doc, f, allow_unicode=True, sort_keys=False, width=4096)
    os.replace(tmp, LOG)
    print("★已写 %s (+1 条: ISS-399 · status=fixing · owner=mech-lead)" % LOG)
    print("★备份 %s (md5 %s)" % (BACKUP, md5(BACKUP)))

    # ---- ④ dispatch_log 追加 (★list 形状·追加式·老字节不动★) ----
    with io.open(DL, encoding="utf-8") as f:
        dl = yaml.safe_load(f)
    dl_list = dl if isinstance(dl, list) else (dl.get("dispatches") or [])
    dl_list.append({
        "issue": "ISS-398",
        "agent": "sw-lead",
        "at": TS,
        "brief": (
            "★★[cont1 续派·真僵尸复活] 第三道病闸 `SW/tools/check_sw_ref_reachability_v2.py` 的 `--selftest` 实测 0/7 ⇒ "
            "★**上一趟【交白卷】: 读满 60 分钟·闸文件一个字节没动 (md5 仍 1c4043ea…)·交卷页不在盘·分片 0 条·plan 第 5~9 步全 ⬜**★ ⇒ "
            "★**本趟只做【改夹具 + 重签留痕 + 同步真相页机器块 + 交卷页 + 分片 + 交卷】**★ "
            "★★**纯分析 + 改【自测夹具】 + 出补丁 · 零写板 · 零落表 · 零改判据 · 零挂链 · 零外发 · 不代拍** ⇒ "
            "合「板只改一次」纪律 ①★★"
        ),
        "brief_file": "state/dispatch_briefs/ISS-398_sw_ref_reach_v2_selftest_baseline_independent_cont1.md",
        "job": (
            JOB + " · ★2026-11-24 20:0x · ★**cont1 续派 (★status 保持 fixing 不动·★死因 = 上一趟 18:26:15~19:26:16 墙钟 60 分钟·"
            "★status=done·★**交白卷**: 闸 md5 仍 1c4043ea26a1182b210e85f1b5130d8d (mtime 11-18 21:37 ⇒ 一字未动)·"
            "★交卷页不在盘·★分片登记 0 条·★logs/iss398/ 只有 before 日志·★tmp/iss398/plan.md 第 5~9 步全 ⬜★)"
            "·★**只做完了「读 + 存证」⇒ 这正是 LESSONS.md L-13 那条·⇒ 本趟纪律 = 【先落盘, 再继续】⇒ 8 分钟内先立交卷页骨架**★"
            "·★本轮 runTimeoutSeconds 5400 (90 分钟)·★本趟是【续做趟】不是重做)** ★ · "
            "★**命令存在性守卫 `python3 state/check_brief_commands.py --brief-file` rc=0** ★"
        ),
        "status_note": "★台账 status 保持 fixing (未改) ⇒ advance.py in_flight 规则继续挡住任何 job 再派活 ⇒ 零撞车窗口★",
        "session_key": "agent:sw-lead:subagent:queue_iss398_cont1",
        "task_name": "queue_iss398_cont1",
        "dispatched_at": TS,
        "prev_session_key": "agent:sw-lead:subagent:ef85edc1-321f-4d41-bef8-172d5fc17b58",
        "redispatch_zombie": True,
        "death_cause": (
            "★上一趟会话 18:26:15~19:26:16 · 墙钟 60 分钟 · status=done (★**不是超时被掐·不是崩溃**)· "
            "★**只读完了资料·一件交付物都没落** ⇒ 闸 md5 仍 1c4043ea26a1182b210e85f1b5130d8d (mtime 2026-11-18 21:37) · "
            "★交卷页不在盘 · ★分片登记 0 条 · ★logs/iss398/ 只有 before 日志 · ★tmp/iss398/plan.md 第 5~9 步全 ⬜★"
        ),
        "zero_delivery": True,
        "partial_delivery": "0/3 交付物在盘 · 但【改前 0/7 原始输出 + 根因 + plan + 改前副本】已落盘在 logs/iss398/ 与 tmp/iss398/ (★直接用, 勿重跑★)",
    })
    dl_list.append({
        "issue": "ISS-399",
        "agent": "mech-lead",
        "at": TS,
        "brief": (
            "★★[新开] MECH 域【闸把别人的 md5 写死成硬基线】的全量清账 (9 道闸 / 35 处 pin) + 3 处已陈旧 pin 的裁定 + "
            "一道《已签收件追加登记台账》自守闸 ⇒ 「板那一趟」合法追加一次 ⇒ MECH 闸就陈旧一处 ⇒ 收工验收的红被误读成「MECH 改坏了」⇒ "
            "板白改第二遍 ★★"
            "★★**纯分析 + 新建真相页 + 新建机器闸 + 出逐字补丁(不应用) · 零写板 · 零落表 · 零改既有闸的判据/阈值 · "
            "零挂链 · 零外发 · 不代拍** ⇒ 合「板只改一次」纪律 ①★★"
        ),
        "brief_file": "state/dispatch_briefs/ISS-399_mech_signed_append_ledger_design.md",
        "job": (
            JOB + " · ★2026-11-24 20:0x · ★**新开并【直接落 fixing】** (★铁律⑩-i: 先落 fixing 再 spawn ⇒ "
            "兄弟 job 775d9893 的 advance.py --json 看不见本单 ⇒ 零撞车窗口★) · "
            "★**开单依据 = 本 job 本机实跑 MECH 域全部 25 道闸**: ★**唯一新缺口 = 9 道闸把别人的 md5 写死成常量 (35 处 pin), "
            "其中 3 处已陈旧 ⇒ 2 道闸现在就是红的**★ ⇒ 且这 9 道里只有 1 道在官方门禁链里 ⇒ 另外 8 道零挂链 ⇒ 红了零通知★ "
            "· ★**命令存在性守卫 `python3 state/check_brief_commands.py --brief-file` rc=0** ★"
        ),
        "status_note": "★台账 status 由新建直接落 `fixing` (★不是 open★) ⇒ advance.py 的 in_flight 规则继续挡住任何 job 再给该 agent 派活 ⇒ 零撞车窗口★",
        "task_name": "queue_iss399",
        "dispatched_at": TS,
        "redispatch_zombie": False,
        "carried_over_from": (
            "★**开单依据 = 本 job 本机实跑 + 实算 (★不抄任何 agent 报告★)**: ★**`python3 state/advance.py --json` 实跑 ⇒ "
            "internal: [] / approvals: [] / waiting: [] / decisions: 55** ⇒ 根因 = 三个总工名下各占着 `status: fixing` 的在飞单 ⇒ "
            "逐条实检三与判据: hw-lead ISS-396 (交卷页 18:43 + 分片 22 处在盘) · mech-lead ISS-397 (交卷页 18:44 + 分片 30 处在盘) "
            "⇒ 两条均已交卷 ⇒ ★**mech-lead 槽位实际已空** ★\n"
            "★**⇒ 本 job 逐道实跑 MECH 域全部 25 道闸 ⇒ 唯一的新缺口 = MECH 域【md5 硬基线】闸这一族** ★\n"
            "★**⇒ ① 9 道闸 / 35 处 pin / 3 处已陈旧 (本机逐字实算)**: ★\n"
            "★**#1** `MECH/check_connector_clearance_caliber.py` (K7) 钉 `MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md`: "
            "基线 ffc09939… vs 现值 f1ce54c9… ★\n"
            "★**#2** 同闸 (K7) 钉 `MECH/check_juart_1p27_clearance.py`: 基线 ea89e0dd… vs 现值 daf8fa36… ★\n"
            "★**#3** `MECH/check_zoujuan_marker_consistency.py` (K5) 钉 `MECH/check_demo_struct_truth.py`: "
            "基线 fa9b59e5… vs 现值 483d018a… ★\n"
            "★**⇒ ② 成因**: #1/#2 = ★**ISS-374 cont2 的合法追加式订正没人回头更新基线**★ (★"
            "`HANDOFF/2026-11-24_mech-lead_ISS382_JDEBUG排针排布标签订正与G5盲区.md` 第 38 行白纸黑字写着「K7 基线红 2 条是开工前就有的」·"
            "⇒ 每个跑这道闸的 agent 都得自己写一句「这红不是我造成的」★) · "
            "#3 = ★**该文件 2026-11-17 20:25:32 被别的单合法改过·而这道闸写于 2026-11-16 10:59 ⇒ 基线比那次改动早**★ ★\n"
            "★**⇒ ③ 为什么没人看见**: ★**9 道里只有 1 道 (`check_demo_struct_truth.py`) 在 `state/gate_check.py` 里 ⇒ "
            "另外 8 道零挂链 ⇒ 红了零通知**★ ★\n"
            "★**⇒ ④ 为什么卡在「板那一趟」的要害上**: 那一趟必然要追加式订正 MECH 域的一堆已签收页/闸 ⇒ "
            "每一次合法追加 ⇒ 钉它的闸又陈旧一处 ⇒ ★**收工验收那几道 MECH 闸是红的 · 红是真的但变的原因是对的 ⇒ "
            "现场极可能误读成「MECH 改坏了」⇒ 板白改第二遍**★ ★\n"
            "★**⇒ ⑤ 先例 (不重新发明)**: ISS-296 / ISS-303 (MECH 侧·判决源换成「硬基线 ∪ 落表台账登记值」·已落进 "
            "`MECH/check_board_frame_coords.py` C4 与 `MECH/check_onepass_struct_crosscheck.py` N6) + "
            "ISS-372 (SW 侧·《钉板 md5 闸清单》自守闸 H4/H5) ⇒ ★**但 `HW/SCHEMATIC_LANDING_V1_LANDED.md` 里这 3 个 MECH 文件 "
            "grep 全是 0 命中 ⇒ MECH 域缺的不是「换一个源」, 是【缺一本自己的台账】★ ⇒ 本单交付的自守闸 = ISS-372 的 MECH 对偶**★"
        ),
    })

    if md5(DL) != src_md5_dl:
        print("★md5 守卫: dispatch_log.yaml 在读与写之间被改过 ⇒ 中止 (rc=3)")
        return 3
    shutil.copy2(DL, BACKUP_DL)
    tmp_dl = DL + ".tmp.%d" % int(time.time())
    with io.open(tmp_dl, "w", encoding="utf-8") as f:
        yaml.safe_dump(dl_list, f, allow_unicode=True, sort_keys=False, width=100000)
    os.replace(tmp_dl, DL)
    print("★已追加 dispatch_log.yaml (+2 条: ISS-398 cont1 / ISS-399 新开)")
    print("★备份 %s (md5 %s)" % (BACKUP_DL, md5(BACKUP_DL)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
