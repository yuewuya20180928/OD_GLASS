#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
moli (项目总工) 2026-11-17 21:4x · job fb67af40「ARS45 队列自动派活」
★★① ISS-296 / ISS-297 两条交卷单【main 独立复核签字】★★
★★② 新开 ISS-299 (hw-lead) / ISS-300 (mech-lead) 两条主线内单 + 直接落 fixing★★
=========================================================================================
★**本 job 本轮实测依据 (★全部 main 本机实跑, 不抄任何 agent 报告★)**:
· ★**① ISS-296 (mech-lead) = 交卷物在盘 (★上一趟 cont2 会话 `agent:mech-lead:subagent:f432bd1c`
  (sessionId 103d07b1) 20:34:51 → 21:12:52 · runtime 1079s · status=timeout / abortedLastRun=true
  ⇒ 子会话被 harness 中止 ⇒ 但【交卷物在盘】★)**:
  - `MECH/check_board_frame_coords.py` rc=0 · `--selftest` rc=0 (末行「【自检结论】✅ 一致」)
  - `MECH/check_demo_struct_truth.py` rc=0 · `--selftest` rc=0 (反向用例 28/28 抓到)
  - `MECH/check_onepass_mech_sync.py` rc=0 · `MECH/check_onepass_struct_crosscheck.py` rc=0
  - `MECH/board_port_opening_s6_check.py` rc=0 · `MECH/check_mech_verdict_freshness.py` rc=0 (F1~F6 全绿)
  - `HANDOFF/2026-11-17_mech-lead_ISS296_合法改板机制与收工重锚.md` = 43,468 B (B1~B5 六块齐全 + §7 最终复核轮)
  - `state/fragments/mech.yaml`: `grep -c iss296` = 20 · interface_claims 带 iss296 的 5 条 · needs_from 4 条
    · status = {phase: delivered, progress_pct: 100, health: 绿}
  - `python3 state/merge.py` rc=0 (产出 545 / 阻塞 43 / 冲突 0) · `python3 state/gate_check.py` rc=0
    (Q1 18/18 · mech-lead 6/6 · 计分交接单 = ISS-296 那份本身)
  - 受保护 5 件 md5 + 板 mtime 逐字节不变 (板 `611b869e…` mtime 仍 2026-11-06 07:07:17.362193413)
· ★**② ISS-297 (hw-lead) = 交卷物在盘 (★上一趟 cont3 会话 `agent:hw-lead:subagent:1e146906`
  (sessionId 56d373ea) 20:55:18 → 21:02:21 · status=done (正常结束)★)**:
  - 6 道 HW 闸: fsin_rootcause rc=0 · g1a7_selection_landed rc=0 · onepass_commit_order rc=0 ·
    onepass_preflight_coverage rc=0 · workpack_state_values rc=0 (★前 5 道 `--selftest` 也全 rc=0, 通道 10/10★)
  - `HW/board_reboard.py --selftest` rc=0 (10/10)
  - ★**第 5 道 `HW/check_pin_function_labels.py` rc=1 = 18 条既有缺陷基线 (★main 本轮实跑核过:
    15 条脚表功能缺陷 + 3 条 `MD5_CHANGED`·基线常量还停在 ISS-257 旧值·真盘自 ISS-283 落表起已变★)
    ⇒ 且 ★**它的 `--selftest` 也是 rc=1 (T5/T11「前提不成立: 正常基线本应干净」)⇒ 它是 9 道里
    唯一「自检也不绿」的一道★ ⇒ 【不掩盖·如实登记·已开 ISS-299 去重锚第 2 跳】★**
  - `HANDOFF/2026-11-17_hw-lead_ISS297_合法改板通道.md` = 33,843 B (B1~B6 + ⑰ 交卷后追记)
  - `state/fragments/hw.yaml`: `grep -c iss297` = 14 · interface_claims 带 iss297 的 3 条 · needs_from 3 条
    · status = {phase: delivered, progress_pct: 100, health: 绿}
  - ★**一条如实登记的读数差**: `state/gate_check.py` 对【最新一份 ISS-297 交卷单】判「缺 B2/B3/B4」
    ⇒ 本次 Q1 18/18 是【回退到 ISS-283 那份】计出来的 ⇒ 该交卷单标题不含标准关键词 ⇒ 已写进 ISS-299 附带修★
  - 受保护 5 件 md5 + 板 mtime 逐字节不变
· ★**③ 本轮新开两条 (★依据 = main 21:3x 实跑出的真缺口★)**:
  - ISS-299 → hw-lead: 「板只改一次」那一趟开工前最后一道硬前置 = 【9 道钉板 md5 闸挂进门禁链】
    ⇒ 卡在第 5 道 (上面那条) ⇒ 本单 = H-1 重锚第 2 跳 (★重锚【脚本里的基线常量】, 不是重锚文件★)
  - ISS-300 → mech-lead: 「板那一趟」当天 MECH 侧要连跑 6 道闸 (★其中 2 道是钉板 md5 闸·当天必然假红★)
    ⇒ 现在是 6 条人工命令 ⇒ 漏一条没人知道 ⇒ 新建一道 fail-closed 汇总闸
★**铁律**: 干活的人不许自签 ⇒ verify_by=main · ★**不碰**: 任何真源文件 / 任何分片 / 板 / 网表 / 脚表 / BOM / 决策页 / outbox
"""
import fcntl
import os
import shutil

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
LOG = os.path.join(HERE, "issue_log.yaml")
DL = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
TODAY = "2026-11-17"

VERIFY = [
    ("ISS-296", "mech-lead",
     "HANDOFF/2026-11-17_mech-lead_ISS296_合法改板机制与收工重锚.md (43,468 B · B1~B5 + §7 最终复核轮) · "
     "MECH/check_board_frame_coords.py (rc=0 · --selftest rc=0) · MECH/check_demo_struct_truth.py "
     "(rc=0 · --selftest rc=0 · 28/28) · MECH/check_onepass_mech_sync.py (rc=0) · "
     "MECH/check_onepass_struct_crosscheck.py (rc=0) · MECH/board_port_opening_s6_check.py (rc=0) · "
     "MECH/check_mech_verdict_freshness.py (rc=0 · F1~F6) · state/fragments/mech.yaml (grep -c iss296 = 20)",
     "★**2026-11-17 21:3x~21:4x 项目总工独立复核 (★不采信自述·全部本机实跑★)**\n"
     "★**① 闸本体 6 道全绿**: `MECH/check_board_frame_coords.py` rc=0 + `--selftest` rc=0 (末行「【自检结论】✅ 一致」) · "
     "`MECH/check_demo_struct_truth.py` rc=0 + `--selftest` rc=0 (反向用例 28/28 抓到) · "
     "`MECH/check_onepass_mech_sync.py` rc=0 · `MECH/check_onepass_struct_crosscheck.py` rc=0 · "
     "`MECH/board_port_opening_s6_check.py` rc=0 · `MECH/check_mech_verdict_freshness.py` rc=0 (F1~F6 全绿)★\n"
     "★**② 交卷物在盘**: 交卷单 43,468 B (B1~B5 六块齐全 + §7 最终复核轮) · `state/fragments/mech.yaml` "
     "`grep -c iss296` = 20 · interface_claims 带 iss296 的 5 条 · needs_from 4 条 · "
     "status = {delivered / 100 / 绿}★\n"
     "★**③ 门禁链**: `python3 state/merge.py` rc=0 (产出 545 / 阻塞 43 / 冲突 0) · "
     "`python3 state/gate_check.py` rc=0 (Q1 18/18 · mech-lead 6/6 · ★计分交接单 = ISS-296 那份本身·"
     "不是回退到别的单★)★\n"
     "★**④ 零写板零落表 (md5 + mtime 双证)**: 板 `611b869e13518c3c023fb178f91a0075` (mtime 仍 "
     "2026-11-06 07:07:17.362193413) · `.kicad_pro` `3e504d2be83152e337949723e909be1b` · "
     "网表 `37f62ac3f0b81d92ca7d48fdea717f07` · 脚表 `a4270120454aedf7a23c92cd8985c8a6` · "
     "BOM `5d02bece9477ffce5fbe0193c7d5cce4` ⇒ 六件逐字节不变★\n"
     "★**⑤ 诚实边界 (★不掩盖★)**: ① 交卷单 §B4-2 里 gate_check 那一行写的是「最新一份 ISS-296 缺 B1~B5」"
     "= ★**那是它补满之前的旧读数**·main 21:3x 复跑后最新一份自己也 6/6⇒ 不影响结论★ · "
     "② B2 的 M2-6「帧标 id 统一 (`B160x100` vs `160x100-bench` vs `F30A`)」= ★**待 main → 老板 (U-274-6)·"
     "本单只登记·没代裁**★ (已在 mech.yaml 登记 need) · ③ 实物 `[实测]` = 0 条 · "
     "④ ★**子会话是被 harness 中止的 (status=timeout / abortedLastRun=true)·但交卷物在盘 ⇒ 判「真交卷」·"
     "不判僵尸**★\n"
     "★**⑥ 本单没做的事 (留给下一棒)**: 「板只改一次」那一趟开工前, 【9 道钉板 md5 闸挂进门禁链】"
     "仍是硬前置 (★main 21:3x 实测: `state/gate_check.py` 的 `EXTRA_GATES` 只有 2 条 ⇒ 9 道里只有 SW 那 1 道在链上★"
     "⇒ 挂闸是 main 的活·闸本体修绿是各域的活⇒ 已开 ISS-299/ISS-300 分别落在 hw-lead / mech-lead 名下★)★"),

    ("ISS-297", "hw-lead",
     "HANDOFF/2026-11-17_hw-lead_ISS297_合法改板通道.md (33,843 B · B1~B6 + ⑰ 交卷后追记) · "
     "HW/board_reboard.py (rc=0 · --selftest 10/10) · HW/check_fsin_rootcause.py (rc=0 · --selftest rc=0) · "
     "HW/check_g1a7_selection_landed.py (rc=0 · --selftest rc=0) · HW/check_onepass_commit_order.py "
     "(rc=0 · --selftest rc=0) · HW/check_onepass_preflight_coverage.py (rc=0 · --selftest rc=0) · "
     "HW/check_workpack_state_values.py (rc=0 · --selftest rc=0) · "
     "state/fragments/hw.yaml (grep -c iss297 = 14)",
     "★**2026-11-17 21:3x~21:4x 项目总工独立复核 (★不采信自述·全部本机实跑★)**\n"
     "★**① HW 侧 6 道闸**: `HW/check_fsin_rootcause.py` rc=0 + `--selftest` rc=0 (25/25) · "
     "`HW/check_g1a7_selection_landed.py` rc=0 + `--selftest` rc=0 (通道 10/10 · 合计 21/21) · "
     "`HW/check_onepass_commit_order.py` rc=0 + `--selftest` rc=0 (通道 10/10) · "
     "`HW/check_onepass_preflight_coverage.py` rc=0 + `--selftest` rc=0 (通道 10/10) · "
     "`HW/check_workpack_state_values.py` rc=0 + `--selftest` rc=0 (通道 10/10 · 合计 20/20) · "
     "`HW/board_reboard.py --selftest` rc=0 (10/10) ⇒ ★**「合法改板」通道在 HW 侧 6 道全建齐★**★\n"
     "★**② 第 5 道 `HW/check_pin_function_labels.py`: rc=1 (18 条既有缺陷基线) ⇒ ★**如实登记·本单没把它算绿★**"
     " ⇒ ★**main 21:3x 实跑拆开看 = 15 条脚表功能缺陷 (14 串号 + 1 缺脚) + 3 条 `MD5_CHANGED`**"
     " (★基线常量还停在 ISS-257 落表时的旧值 `94642d07…` / `e06c1dd6…` / `287e7861…`·而真盘自 ISS-283 "
     "合法落表 (台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` §16.2 链头 L1353 · 2026-11-17 12:30:23) 起已是 "
     "`5d02bece…` / `37f62ac3…` / `a4270120…`★) ⇒ ★**且它的 `--selftest` 也是 rc=1 "
     "(❌T5 前提不成立: 正常基线本应干净 + ❌T11 前提不成立: 正常基线本应干净·通道用例 10/10 通过)"
     "⇒ 它是 9 道钉板 md5 闸里【唯一「自检也不绿」的一道】⇒ 【已开 ISS-299 = H-1 重锚第 2 跳去修它】★**★\n"
     "★**③ 交卷物在盘**: 交卷单 33,843 B (B1~B6 + ⑰ 追记) · `state/fragments/hw.yaml` `grep -c iss297` = 14 · "
     "interface_claims 带 iss297 的 3 条 · needs_from 3 条 · status = {delivered / 100 / 绿}★\n"
     "★**④ 门禁链**: `python3 state/merge.py` rc=0 (产出 545 / 阻塞 43 / 冲突 0) · "
     "`python3 state/gate_check.py` rc=0 (Q1 18/18) ⇒ ★**但一条读数差如实登记: 该闸对【最新一份 ISS-297 交卷单】"
     "判「缺 B2/B3/B4」(★标题不含标准关键词★)⇒ 本次 Q1 18/18 是回退到 ISS-283 那份计出来的 ⇒ "
     "★**已写进 ISS-299 的附带修 (只追加 3 行标准标题行·不许改 B0~B6 老字)★**★\n"
     "★**⑤ 零写板零落表 (md5 + mtime 双证)**: 板 `611b869e13518c3c023fb178f91a0075` (mtime 仍 "
     "2026-11-06 07:07:17.362193413) · `.kicad_pro` `3e504d2be83152e337949723e909be1b` · "
     "网表 `37f62ac3f0b81d92ca7d48fdea717f07` · 脚表 `a4270120454aedf7a23c92cd8985c8a6` · "
     "BOM `5d02bece9477ffce5fbe0193c7d5cce4` ⇒ 六件逐字节不变★\n"
     "★**⑥ 诚实边界**: ① 实物 `[实测]` = 0 条 · ② 它的 3 条 `needs_from` (B5①②③) = ★**待 main 裁·本单没代拍**★ · "
     "③ ★**它给 main 的一条现场观察 (⑰-7) 已收下: `HW/PCB/` 下 4 个 KiCad 派生产物被并发 main 进程重生成过"
     "·⇒ 零写板自证要盯那 5 件本身·别盯 `HW/PCB/` 目录 mtime★**"),
]

NEW = [
    ("ISS-299", "hw-lead", "high", "2026-11-20",
     "★★[主线内·HW 侧·重锚类·零写板] ★★【H-1 重锚第 2 跳: 让 9 道「钉板 md5 闸」里唯一红的那一道能挂进门禁链】★★ "
     "⇒ ★**第 5 道 `HW/check_pin_function_labels.py` 现在 rc=1 (18 条既有缺陷 = 15 条脚表功能缺陷 + 3 条 "
     "`MD5_CHANGED`·基线常量还停在 ISS-257 旧值·真盘自 ISS-283 落表起已变) ⇒ 且它的 `--selftest` 也是 rc=1 "
     "(T5/T11「前提不成立: 正常基线本应干净」)⇒ 它是 9 道里唯一「自检也不绿」的一道** ⇒ ⇒ ★**main 因此不能把它挂进 "
     "`state/gate_check.py` 的 `EXTRA_GATES` (挂上去链当场红) ⇒ 「9 道闸通道齐 = 板那一趟开工前最后一道硬前置」"
     "现在卡在它身上** ★ ⇒ ★**本单 = 把 `PROTECTED_MD5` 里网表/脚表/BOM 三个基线重锚到 ISS-283 落表后的真盘实测值 "
     "+ `MD5_ANCHOR_CHAIN` 追加第 2 跳 (★重锚的是【脚本里的基线常量】·不是那三个文件本身★) + 目标读数 "
     "「缺陷 18→15 · `--expect-known` rc=0 · `--selftest` rc=0」** ★ ⇒ ★**附带一条小修: ISS-297 交卷单标题不含 "
     "`gate_check.py` 标准 B2/B3/B4 关键词 ⇒ 最新一份自己评不满 6/6 (现在靠回退到 ISS-283 计分) ⇒ 末尾追加 3 行"
     "标准标题行 (只追加·不许改老字)** ★ ⇒ ★**纯重锚类·零写板·零落表·不碰 `state/gate_check.py`** ★",
     "state/dispatch_briefs/ISS-299_hw_h1_reanchor_hop2.md",
     "★**派活依据 = main 2026-11-17 21:3x 本机实跑** (★不是抄任何 agent 报告★): "
     "`HW/check_pin_function_labels.py` rc=1 (18 条) · `--expect-known` rc=1 · `--selftest` rc=1 (T5/T11 前提不成立·"
     "通道用例 10/10 通过) ⇒ ★**真因 = 基线常量陈旧 (ISS-257 旧值 vs ISS-283 落表后真盘值)·不是判据坏了**★ ⇒ "
     "⇒ ★**main 已拍: 属【重锚】不是【改判据】·判据方向一个字不变·fail-closed 三条一条不许动**★ ⇒ "
     "⇒ ★**挂闸与重锚必须同批 (顺序 ①②③) ⇒ 本单做完 ⇒ main 才能把 9 道挂进 `EXTRA_GATES`**★"),

    ("ISS-300", "mech-lead", "high", "2026-11-20",
     "★★[主线内·MECH 侧·准出闸类·零写板] ★★【「板只改一次」那一趟的 MECH 侧【准出汇总闸】: 一条命令出「S6 重出板后"
     "能不能出 Gerber」的结构侧结论】★★ ⇒ ★**那一趟当天 MECH 侧必跑 6 道闸 (main 21:3x 实跑今天全 rc=0): "
     "`MECH/check_board_frame_coords.py` · `MECH/check_demo_struct_truth.py` · `MECH/check_onepass_mech_sync.py` · "
     "`MECH/check_onepass_struct_crosscheck.py` · `MECH/board_port_opening_s6_check.py` · "
     "`MECH/check_mech_verdict_freshness.py`** ⇒ ★**现在这 6 道是人工一条条跑 ⇒ 漏一条就没人知道 ⇒ 而这 6 道里有 2 道是"
     "【钉板 md5 闸】(板那一趟当天必然从绿转红·只有合法改板通道能走绿·ISS-296 已把通道建好) ⇒ 当天最容易误读成"
     "「板改坏了」⇒ 去改板凑绿 ⇒ 板 md5 变第二次 ⇒ 整趟白跑** ★ ⇒ ★**本单 = 新建一道 fail-closed 汇总闸 "
     "`MECH/check_onepass_mech_release.py` (逐条打印每道 rc + 汇总 rc + 脚本不存在/跑不起来/超时一律算红 + "
     "必须点名是哪一道红了) + ≥3 条反向用例 (沙盒里把任一道弄红 ⇒ 汇总必红且点名) + `--selftest` 模式** ★ ⇒ "
     "★**纯门禁类·零写板·零落表·不许改那 6 道闸本体·不许改 `state/gate_check.py` (挂闸是 main 的活)** ★",
     "state/dispatch_briefs/ISS-300_mech_onepass_release_gate.md",
     "★**派活依据 = main 2026-11-17 21:3x 本机实跑** (★不是抄任何 agent 报告★): MECH 侧 6 道必跑闸今天全 rc=0 "
     "(逐条实跑) ⇒ ★**「当天人工连跑 6 条 + 其中 2 条必然假红」= 板那一趟最容易现场误读 ⇒ 改板凑绿 ⇒ 板 md5 变第二次**★ "
     "⇒ ★**一条命令 + fail-closed 语义 = 当天不会漏、不会误读**★ ⇒ ★**这正是 MEMORY 铁律④「新闸交卷后第一件事不是"
     "验收通过, 是挂进门禁链 + 让它真跑一次」**★"),
]


def main() -> int:
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        with open(LOG, encoding="utf-8") as f:
            log = yaml.safe_load(f)
        issues = log["issues"]
        by_id = {it["id"]: it for it in issues}

        # ---------- ① 两条交卷单签字 ----------
        for iid, owner, fix_ref, vnote in VERIFY:
            it = by_id.get(iid)
            if it is None:
                print("⚠ %s 不存在 ⇒ 中止" % iid)
                return 1
            assert it.get("status") == "fixing", "%s 期望 fixing, 实得 %s" % (iid, it.get("status"))
            it["status"] = "verified"
            it["verify_by"] = "main"
            it["verify_result"] = "pass"
            it["verify_date"] = TODAY
            it["fix_ref"] = fix_ref
            it["note"] = (it.get("note") or "") + "\n\n★" + vnote
            print("✅ %s (%s) → verified (verify_by=main)" % (iid, owner))

        # ---------- ② 新开两条 (open → fixing 同一个锁内原子完成 ⇒ 不留 open 窗口) ----------
        for iid, owner, sev, due, title, brief_file, note in NEW:
            if iid in by_id:
                print("⚠ %s 已存在 ⇒ 中止 (防撞号)" % iid)
                return 1
            brief_path = os.path.join(PROJ, brief_file)
            if not os.path.exists(brief_path):
                print("⚠ 缺 brief 文件: %s ⇒ 中止" % brief_path)
                return 1
            with open(brief_path, encoding="utf-8") as f:
                brief = f.read()
            new_it = {
                "id": iid,
                "title": title,
                "severity": sev,
                "source_blocker": None,
                "source_agent": "main",
                "owner": owner,
                "reporter": "main",
                "raised": TODAY,
                "due": due,
                "status": "open",
                "external": False,
                "need_keys": [],
                "fix_ref": "",
                "verify_by": "main",
                "verify_result": "",
                "verify_date": "",
                "note": ("2026-11-17 21:4x 队列自动派活 job (fb67af40) 新开 ★★: %s ★★ ⇒ ★**符合老板 "
                         "2026-11-17 00:43「PCB 类先派【纯分析 / 作业包 / 门禁机制】类」纪律 (★本单零写板·零落表·"
                         "不动板·不动网表真源★)** ★ ⇒ ★**零外发 (老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, "
                         "全靠自己查资料) ⇒ 缺口一律自己网上查 + 标证据等级 + 查不到就写降级方案 ⇒ 没有「批一句可以发」"
                         "这个选项** ★ ⇒ ★**任务书全文 = `%s` (★已过 `python3 state/check_brief_commands.py "
                         "--brief-file` ⇒ rc=0★)** ★ ⇒ ★**status 全程 fixing ⇒ 无 open 窗口 ⇒ 兄弟 job 775d9893 "
                         "不会重复派** ★" % (note, brief_file)),
                "dispatched_at": TODAY,
                "task_brief": brief,
            }
            new_it["status"] = "fixing"   # ★同锁内 open→fixing ⇒ 兄弟 job 看不到 open 窗口★
            issues.append(new_it)
            by_id[iid] = new_it
            print("✅ %s (%s) 新开 + 落 fixing · brief=%s" % (iid, owner, brief_file))

        shutil.copy2(LOG, LOG + ".bak_20261117_2140_cronfb67_verify296_297_open299_300")
        tmp = LOG + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)
        os.replace(tmp, LOG)

        # ---------- 派活日志 ----------
        with open(DL, encoding="utf-8") as f:
            dl = yaml.safe_load(f) or {}
        for iid, owner, _sev, _due, _title, brief_file, note in NEW:
            dl.setdefault("dispatches", []).append({
                "issue": iid,
                "agent": owner,
                "at": TODAY,
                "brief": ("★派活方 = cron fb67af40 (ARS45 队列自动派活) 于 21:4x ★ · ★**依据 = main 21:3x 本机实跑"
                          "(不抄任何 agent 报告)** ★ · ★**零写板 · 零落表 · 零外发** ★ · "
                          "★**status 全程 fixing ⇒ 无 open 窗口 ⇒ 兄弟 job 775d9893 不会重复派** ★ · "
                          "★**brief = issue_log 里 %s 的 task_brief (★= `state/dispatch_briefs/%s` 全文·已过命令存在性闸 rc=0★)** ★"
                          % (iid, brief_file)),
                "note": note,
            })
        tmp_dl = DL + ".tmp"
        with open(tmp_dl, "w", encoding="utf-8") as f:
            yaml.safe_dump(dl, f, allow_unicode=True, sort_keys=False, width=200)
        os.replace(tmp_dl, DL)
        print("✅ dispatch_log 已写 %d 条" % len(NEW))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
