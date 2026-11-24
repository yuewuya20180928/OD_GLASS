#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★_apply_20261125_0200_cronfb67af40_sign404_405_open406_407_408.py★

★**用途**: cron `fb67af40` (ARS45 队列自动派活) · 2026-11-25 02:0x 一趟
  ① ★**签收** ISS-404 (hw-lead) / ISS-405 (mech-lead) ⇒ status `fixing` → `verified`
     (★main 本机独立复核 · 不抄任何 agent 报告 · 实跑读数见 VERIFY★)
  ② ★**新开 3 条内部单** (ISS-406 → hw-lead / ISS-407 → mech-lead / ISS-408 → sw-lead)
     并【直接落 `fixing`】 (★铁律⑩-i: 先落 fixing 再 spawn ⇒ 兄弟 job `775d9893`
       的 `advance.py --json` 看不见本单 ⇒ 零撞车窗口★)

★**为什么这轮签收 + 开单 (★本机实读 + 本机实算, 零抄任何 agent 报告★)**:
  · `python3 state/advance.py --json` ⇒ `internal: []` / `approvals: []` / `waiting: []`
    ⇒ ★**台账 16 条 `open` 的 owner 全是 boss(5) / main(11) ⇒ 不在三个总工可派域**
    (`state/advance.py` L33 `AGENT_ROLE = {"hw-lead","sw-lead","mech-lead"}`)
  · ★**槽位实检 (`sessions_list` + `subagents list`)**:
    hw-lead `4239603f` (ISS-404) **done @01:51** ⇒ 但末条消息逐字
    `LLM idle timeout (120s): no response from model` ⇒ ★**交卷消息没送达, 但产出在盘**
    ⇒ 本机逐件实查: 真相页 + 新闸 + 交卷页 + 分片 17 条 全部在盘 ⇒ **不是僵尸, 是"产出在盘但收尾消息被掐"**
    ⇒ 独立复核通过 ⇒ 签收
    mech-lead `9e1b579f` (ISS-405) **done @01:45** + 完整交卷消息 ⇒ 签收
    sw-lead `d35b8dd2` (ISS-398 cont2) done @22:59 ⇒ 槽位空
  · ★**本轮三条新单的题 (main 本机实跑 + 实读, 逐条可复现)**:
      ① ★**ISS-406 (hw-lead)**: 门禁链 18 道闸的【实际调用方式】全仓零机器闸覆盖 ⇒
         ★**`state/check_pcb_drc.py` L134-L139 逐字 `strict = "--strict" in sys.argv` ·
         `ok4 = (n_unc == 0) if strict else True` ⇒ 不带 `--strict` 时 unconnected 恒判绿 (假绿)★**
         ⇒ 而它【不在链上】; 链上 18 道里已有一道用非默认档 (`check_pin_function_labels.py` 带
         `--expect-known` ⇒ 裸跑必然 rc=1 ⇒ 链上跑的是"已知缺陷放行"档)
      ② ★**ISS-407 (mech-lead)**: MECH 域已有 5 张清账页 (393/397/399/400/403/405) 但**没有一张说清
         「哪个前提量变了 ⇒ 哪些数/闸/结论同时作废」** ⇒ 焊盘档一改就是全链过期 (ISS-403 实测:
         5/7 道闸两臂 stdout md5 逐字相同 ⇒ 闸压根看不见前提变了)
      ③ ★**ISS-408 (sw-lead)**: ★**`SW/tools/check_sw_board_md5_rebase_readiness.py` 本机实跑 rc=1 ·
         5/7 通过 · H1 红 (4 处漏登记: `SW/BOARD_ONEPASS_ZERO_FALSE_CONNECTIVITY.md:23` / `:241` ·
         `SW/EVT_CHARGE_CURRENT_CRITERION_CALIBER.md:215` · `SW/tools/check_sw_false_connectivity_gate.py:73`)
         · H4 红 (`check_sw_false_connectivity_gate.py` 硬钉板 md5 却没进 §2 的账)★**
         ⇒ 它就是「板那一趟板 md5 变了以后 SW 侧要不要重锚定」那道守门闸 ⇒ 它自己病着

★**本脚本三道自保**: ① **幂等** (ISS-406/407/408 已存在 ⇒ 不写盘)
  ② **CAS 守卫** (写前重算 `issue_log.yaml` md5, 与读时不一致 ⇒ rc=3 中止)
  ③ **原子写 + 写后回读自检** (条数 / ISS 在位 / status / 旧条目条数不变 ⇒ 不满足即回滚)

★**零外发 · 零写板 · 零落表 · 零改既有闸 · 零改既有页正文 · 零挂链 · 不写任何 agent 的分片**
"""
import hashlib
import io
import os
import shutil
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
DLOG = os.path.join(HERE, "dispatch_log.yaml")
BRIEFS = os.path.join(HERE, "dispatch_briefs")
BACKUP = os.path.join(HERE, "issue_log.yaml.bak_20261125_0200_cronfb67af40_sign404_405_open406_407_408")
DLOG_BACKUP = os.path.join(HERE, "dispatch_log.yaml.bak_20261125_0200_cronfb67af40_sign404_405_open406_407_408")

RUN_ID = "cron_fb67af40_20261125_0200"

# ── ① 签收 (★main 本机实跑读数 · 不抄 agent 报告★) ──
SIGN = {
    "ISS-404": {
        "verify_result": (
            "✅ verified (★main 2026-11-25 01:5x~02:0x 本机独立复核 · 不抄任何 agent 报告★) ⇒ "
            "★**新闸 `HW/check_onepass_gate_hook_coverage.py` 裸跑 rc=1 (G5~G7 绿 · G1 红: "
            "「有页面点名的闸既不在挂链表、也不在人工签核台账」⇒ 红的是现状, 不是闸故障) · "
            "`--selftest` rc=0 · 末行逐字 `ALL TESTS PASS` (★正向 1 条 + 反向 13 条 = 14 条★)** ★ ⇒ "
            "★**「板那一趟」预检清单/作业包点名的闸没挂上自动链这件事, 今天第一次有了逐条台账 + fail-closed 闸** ★ ⇒ "
            "★**板 md5 `611b869e13518c3c023fb178f91a0075` / size 4940213 / "
            "mtime 2026-11-06 07:07:17.362193413 三证逐字节未动 (19 天) + 网表 `6aee500e…` / "
            "脚表 `9174309d…` / BOM `5b999399…` 未变 ⇒ 零写板 · 零落表 · 零挂链 · 零外发** ★ ⇒ "
            "★**交卷页在盘 (45,289 B · `HANDOFF/2026-11-25_hw-lead_ISS404_闸挂链覆盖率清账与闸.md`) + "
            "真相页 `HW/PCB/BOARD_ONEPASS_GATE_HOOK_COVERAGE.md` + 新闸 + `state/fragments/hw.yaml` 已登记 17 处** ★ ⇒ "
            "★**交卷消息本身被 idle timeout 掐掉 (末条逐字 `LLM idle timeout (120s)`), 但产出全部在盘 ⇒ "
            "按「产出在盘」签收, 不是按「报告已读」签收** ★"
        ),
        "fix_ref": (
            "main 2026-11-25 02:0x 独立复核签收 (★零写板·零落表·零改既有闸判据·零改既有页面正文·"
            "零挂链·零外发·未代老板拍板★)"
        ),
        "addendum": (
            "★★2026-11-25 02:0x cron fb67af40 (ARS45 队列自动派活) · main 独立复核签收 "
            "(★追加式·老字一字未删★)★★\n"
            "★本机实跑读数 (★不抄任何 agent 报告★)★: "
            "`python3 HW/check_onepass_gate_hook_coverage.py` ⇒ **rc=1** (★G1 红 = 有页面点名的闸既不在挂链表、"
            "也不在人工签核台账 ⇒ **红的是现状**★ · G5 零挂链 + 零外发自证绿 · G6 证据分级绿 · G7 零写板自证绿) · "
            "`python3 HW/check_onepass_gate_hook_coverage.py --selftest` ⇒ **rc=0** · 末行逐字 `ALL TESTS PASS` "
            "(★反向用例 14/14 通过 = 正向 1 + 反向 13★) · `grep -c check_onepass_gate_hook_coverage "
            "state/gate_check.py` ⇒ **0** (★零挂链★) · `md5sum` 板/网表/脚表/BOM ⇒ `611b869e…` / `6aee500e…` / "
            "`9174309d…` / `5b999399…` (与基线逐字相同) · 板 mtime `2026-11-06 07:07:17.362193413` / size 4940213 "
            "(逐字未动) · `grep -c iss404 state/fragments/hw.yaml` ⇒ **17** (≥1 ✔)\n"
            "★**签名理由**: ★**「板那一趟」的闸挂链覆盖率这一格, 从今天起有逐条台账 + 一道 fail-closed 闸** ⇒ "
            "★**「板 md5 全生命周期变更次数 ≤1」这条纪律, 第一次有了「链上到底有几道闸在跑」的机器读数** ★\n"
            "★**签收后**: ★**hw-lead 槽位已释放** (★台账 status fixing → verified ⇒ advance.py 的 in_flight 规则"
            "不再挡它★) ⇒ 本 job 同一趟已给它派新单 ISS-406 (★先落 fixing 再 spawn ⇒ 零撞车窗口★)"
        ),
    },
    "ISS-405": {
        "verify_result": (
            "✅ verified (★main 2026-11-25 01:5x~02:0x 本机独立复核 · 不抄任何 agent 报告★) ⇒ "
            "★**新闸 `MECH/check_mech_gate_hook_coverage.py` 裸跑 rc=1 (9/10 条判据通过 · M2 红: "
            "10 道必挂闸既不在门禁链、也不在人工签核台账 ⇒ 红的是现状, 不是闸故障) · "
            "`--selftest` rc=0 · 末行逐字 `ALL TESTS PASS` (★正向 1 条 + 反向 13 条★)** ★ ⇒ "
            "★**MECH 域 29 道闸只挂 4 道 ⇒ 25 道零挂链 (含 7 道判决链闸 + 准出汇总闸 + ISS-400/403 两道新闸) "
            "这件事, 今天第一次有了逐条台账 + fail-closed 闸** ★ ⇒ "
            "★**附带回答了 open need `iss384_jchg_10p_dims_geometry` (J_CHG 10p 座体几何: X 进深 6.40mm [官网] · "
            "Y 占宽 9.10mm [官网] · 本仓把 6.50 锚焊盘中心距当座体外形宽 ⇒ 「余 1.05mm」变「干涉 0.25mm」)** ★ ⇒ "
            "★**板 md5 `611b869e13518c3c023fb178f91a0075` / size 4940213 / "
            "mtime 2026-11-06 07:07:17.362193413 三证逐字节未动 (19 天) + 三表 md5 未变 ⇒ "
            "零写板 · 零落表 · 零挂链 · 零外发** ★ ⇒ "
            "★**交卷页在盘 (40,815 B · `HANDOFF/2026-11-25_mech-lead_ISS405_闸挂链覆盖率清账与闸.md`) + "
            "真相页 + 新闸 + J_CHG 10p 几何页 + `state/fragments/mech.yaml` 已登记 6 处** ★"
        ),
        "fix_ref": (
            "main 2026-11-25 02:0x 独立复核签收 (★零写板·零落表·零改既有闸判据·零改既有页面正文·"
            "零挂链·零外发·未代老板拍板★)"
        ),
        "addendum": (
            "★★2026-11-25 02:0x cron fb67af40 (ARS45 队列自动派活) · main 独立复核签收 "
            "(★追加式·老字一字未删★)★★\n"
            "★本机实跑读数 (★不抄任何 agent 报告★)★: "
            "`python3 MECH/check_mech_gate_hook_coverage.py` ⇒ **rc=1** (★M2 红 = 10 道必挂闸既不在门禁链、"
            "也不在人工签核台账 ⇒ **红的是现状**★ · M1/M3/M4/M5/M6/M7 绿) · "
            "`python3 MECH/check_mech_gate_hook_coverage.py --selftest` ⇒ **rc=0** · 末行逐字 `ALL TESTS PASS` "
            "(★正向 1 + 反向 13★) · `grep -c check_mech_gate_hook_coverage state/gate_check.py` ⇒ **0** (★零挂链★) · "
            "`md5sum` 板/网表/脚表/BOM ⇒ `611b869e…` / `6aee500e…` / `9174309d…` / `5b999399…` (与基线逐字相同) · "
            "板 mtime/size 逐字未动 · `grep -c iss405 state/fragments/mech.yaml` ⇒ **6** (≥1 ✔)\n"
            "★**签名理由**: ★**「板那一趟」结构侧的自动防线今天第一次有了机器读数 (29 道闸 / 链上 4 道 / "
            "10 道必挂闸不在链也不在签核台账)** ⇒ ★**「板 md5 只许变一次」⇒ 结构侧一旦判错就是板改第二次, "
            "这条防线今天才开始数得清** ★\n"
            "★**签收后**: ★**mech-lead 槽位已释放** ⇒ 本 job 同一趟已给它派新单 ISS-407 "
            "(★先落 fixing 再 spawn ⇒ 零撞车窗口★)"
        ),
    },
}

# ── ② 新开三单 (直接落 fixing) ──
NEW = [
    {
        "id": "ISS-406",
        "agent": "hw-lead",
        "brief_rel": "ISS-406_hw_gate_teeth_invocation_audit.md",
        "severity": "high",
        "need_keys": [
            "iss406_gate_argv_ledger",
            "iss406_lenient_mode_gate_list",
            "iss406_failopen_suspect_list",
        ],
        "title": (
            "★★[★新主线·PCB 线·HW 侧·纯查证+纯分析+新建真相页+新建机器闸·零写板·零落表] "
            "门禁链 18 道闸的【实际调用方式】全仓零机器闸覆盖 ⇒ ★**`state/check_pcb_drc.py` "
            "L134-L139 逐字 `ok4 = (n_unc == 0) if strict else True` ⇒ 不带 `--strict` 时 "
            "unconnected 恒判绿 (假绿)★** 而它不在链上 · 链上已有 1 道用宽松档 "
            "(`check_pin_function_labels.py` 带 `--expect-known`) ⇒ 「板那一趟」的验收链有没有牙齿, "
            "全仓没有闸会问 (★main 本机实读·逐条可复现★) ★★"
        ),
        "note": (
            "★**2026-11-25 02:0x cron fb67af40 (ARS45 队列自动派活) 新开并【直接落 fixing】** "
            "(★铁律⑩-i: 先落 fixing 再 spawn ⇒ 兄弟 job 775d9893 的 `advance.py --json` 看不见本单 ⇒ "
            "零撞车窗口★)\n"
            "★**开单依据 (本机实读 + 本机实算, 零抄报告)★**: ① `state/advance.py --json` ⇒ internal 0 "
            "(台账 open 的 owner 全是 boss/main ⇒ 不在三个总工可派域); ② 槽位实检: hw-lead ISS-404 "
            "**产出在盘但交卷消息被 idle timeout 掐掉** ⇒ 已由本脚本独立复核签收释放槽位; "
            "mech-lead ISS-405 done + 交卷完整 ⇒ 签收释放槽位; sw-lead 槽位空; ③ ★**本单的题 = "
            "验收链的「调用档位 ⇒ 判据强度」这一轴** (★main 实读 `state/check_pcb_drc.py` L134-L139: "
            "`strict = \"--strict\" in sys.argv` · `ok4 = (n_unc == 0) if strict else True` ⇒ "
            "**不带 `--strict` ⇒ C4 unconnected 恒真 ⇒ 假绿**★; 且 `state/gate_check.py` L267 显示链上 "
            "`check_pin_function_labels.py` 用 `(\"--expect-known\",)` 非默认档 ⇒ 链上跑的是「已知缺陷放行」档); "
            "④ ★**既有闸盯的都不是这一轴**: `check_onepass_preflight_coverage.py` P3 只判「脚本存在」; "
            "ISS-404 新闸只判「在不在链上」; ISS-388 `check_sw_gate_health.py` H1 判「环境无关性」 ⇒ "
            "**「宽松档」这一轴至今零机器闸覆盖** ⇒ 本单补这一格。\n"
            "★**本单是纯查证/纯分析类** ⇒ 零写板 · 零落表 · 零改既有闸 · 零改既有页正文 · 零挂链 · 零外发 ⇒ "
            "合「板只改一次」纪律 ① ⇒ 真动板那一趟不受本单影响。"
        ),
    },
    {
        "id": "ISS-407",
        "agent": "mech-lead",
        "brief_rel": "ISS-407_mech_verdict_premise_dependency.md",
        "severity": "high",
        "need_keys": [
            "iss407_premise_dependency_graph",
            "iss407_invalidation_matrix",
            "iss407_recompute_trigger_list",
        ],
        "title": (
            "★★[★新主线·PCB 线·MECH 侧·纯查证+纯分析+新建真相页+新建机器闸·零写板·零落表] "
            "MECH 域 6 张清账页 (393/397/399/400/403/405) 都说清了「哪里不对」, 但**没有一张说清 "
            "「我改了哪个前提量 ⇒ 哪些数/闸/结论同时作废、谁负责重算」** ⇒ 焊盘档一改就是全链过期 "
            "(ISS-403 实测 5/7 道闸两臂 stdout md5 逐字相同 ⇒ 闸压根看不见前提变了) ⇒ 本单把 "
            "MECH 判决链的前提依赖关系做成机器可判 ★★"
        ),
        "note": (
            "★**2026-11-25 02:0x cron fb67af40 (ARS45 队列自动派活) 新开并【直接落 fixing】** "
            "(★铁律⑩-i: 先落 fixing 再 spawn ⇒ 零撞车窗口★)\n"
            "★**开单依据 (本机实读 + 本机实算, 零抄报告)★**: ① `state/advance.py --json` ⇒ internal 0; "
            "② mech-lead 槽位已由本脚本签收 ISS-405 释放; ③ ★**本单的题 = 「前提 → 结论」的依赖关系** "
            "(★main 本机实跑 `python3 MECH/check_mech_gate_hook_coverage.py` ⇒ rc=1 · 9/10 · M2 红: "
            "10 道必挂闸既不在链也不在人工签核台账; 而 ISS-403 已实测「焊盘 1.000→1.110 ⇒ 判决链 7 个数全作废 + "
            "5 道闸对焊盘尺寸完全盲」⇒ **坏的不是一个前提, 是没有一张表能回答「下一个前提变了会波及什么」**★); "
            "④ ★**本单与 ISS-393/397/399/400/403/405 六张页不重复** ⇒ 那六张查的是「哪里不对」, "
            "本单查的是「变了之后波及谁」★。\n"
            "★**本单是纯查证/纯分析类** ⇒ 零写板 · 零落表 · 零改既有闸 · 零改既有页正文 · 零挂链 · 零外发 ⇒ "
            "合「板只改一次」纪律 ①。"
        ),
    },
    {
        "id": "ISS-408",
        "agent": "sw-lead",
        "brief_rel": "ISS-408_sw_md5_rebase_gate_truth.md",
        "severity": "high",
        "need_keys": [
            "iss408_sw_md5_ref_surface_closure",
            "iss408_md5_rebase_gate_teeth",
            "iss408_sw_side_md5_reanchor_list",
        ],
        "title": (
            "★★[★新主线·PCB 线·SW 侧·纯查证+纯分析+追加式订正+反向用例·零写板·零落表] "
            "「板那一趟」板 md5 必变 ⇒ SW 侧凡引用板 md5 处都要重锚定 ⇒ 守这道口的闸 "
            "`SW/tools/check_sw_board_md5_rebase_readiness.py` ★**本机实跑 rc=1 · 5/7 · H1 红 (4 处漏登记) + "
            "H4 红 (1 道硬钉板 md5 的闸没进 §2 的账)⇒ 它自己病着 ⇒ 板那一趟当天「SW 侧有没有漏网」零保证**★ "
            "⇒ ISS-388 点名的 2 道病闸里, ISS-398 修了另一道, 这道至今没修 ★★"
        ),
        "note": (
            "★**2026-11-25 02:0x cron fb67af40 (ARS45 队列自动派活) 新开并【直接落 fixing】** "
            "(★铁律⑩-i: 先落 fixing 再 spawn ⇒ 零撞车窗口★)\n"
            "★**开单依据 (本机实读 + 本机实算, 零抄报告)★**: ① `state/advance.py --json` ⇒ internal 0; "
            "② sw-lead 槽位空 (上一次 ISS-398 cont2 done @22:59) ⇒ 本单是 sw-lead 名下唯一一条; "
            "③ ★**本单的题 = 守门闸自己病着** (★main 本机实跑 `python3 SW/tools/check_sw_board_md5_rebase_readiness.py` "
            "⇒ **rc=1 · 5/7 通过** · H1 红: 4 处板 md5 引用面漏登记 (`SW/BOARD_ONEPASS_ZERO_FALSE_CONNECTIVITY.md:23` / "
            "`:241` · `SW/EVT_CHARGE_CURRENT_CRITERION_CALIBER.md:215` · `SW/tools/check_sw_false_connectivity_gate.py:73`) · "
            "H4 红: `check_sw_false_connectivity_gate.py` 硬钉板 md5 却没进 §2 的账 ⇒ 「下一道新闸再硬钉板 md5 "
            "就是从这儿溜过去的」这条防线今天没有★); ④ ★**ISS-388 交卷的 `check_sw_gate_health.py` H0 点名 2 道病闸, "
            "ISS-398 修好了 `check_sw_ref_reachability_v2.py` ⇒ 只剩这一道** ⇒ 本单把它修可信。\n"
            "★**本单是纯查证/纯分析 + 追加式订正类** ⇒ 零写板 · 零落表 · 零改既有页正文(★只许追加式·老字一字未删★) · "
            "零挂链 · 零外发 ⇒ 合「板只改一次」纪律 ①。"
        ),
    },
]


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def read_yaml(p):
    with io.open(p, encoding="utf-8") as f:
        return yaml.safe_load(f)


def atomic_write(path, text):
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_iss406_408_")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def main():
    if not os.path.exists(LOG):
        sys.exit("★issue_log.yaml 不存在 ⇒ 拒绝跑")

    before_md5 = md5(LOG)
    log = read_yaml(LOG)
    issues = log.get("issues") or []
    n_before = len(issues)

    by_id = {it.get("id"): it for it in issues if isinstance(it, dict)}

    # ── 幂等守卫 ──
    for spec in NEW:
        if spec["id"] in by_id:
            sys.stderr.write("★%s 已存在 (status=%s) ⇒ 幂等跳过, 不写盘\n"
                             % (spec["id"], by_id[spec["id"]].get("status")))
            print("IDEMPOTENT_NO_WRITE")
            return 0

    # ── brief 必须先在盘 ──
    briefs = {}
    for spec in NEW:
        bp = os.path.join(BRIEFS, spec["brief_rel"])
        if not os.path.exists(bp):
            sys.exit("★brief 不存在 ⇒ 拒绝跑: %s" % bp)
        with io.open(bp, encoding="utf-8") as f:
            briefs[spec["id"]] = f.read()

    # ── ① 签收 ISS-404 / ISS-405 ──
    signed = []
    for iss_id, rec in SIGN.items():
        it = by_id.get(iss_id)
        if not it:
            sys.stderr.write("★%s 不在台账里 ⇒ 拒绝签收\n" % iss_id)
            return 2
        if it.get("status") == "verified":
            print("★%s 已是 verified ⇒ 跳过签收 (幂等)\n" % iss_id)
            continue
        it["status"] = "verified"
        it["verify_result"] = rec["verify_result"]
        it["verify_date"] = "2026-11-25 02:0x"
        it["fix_ref"] = rec["fix_ref"]
        na = it.get("note_addendum")
        if not isinstance(na, list):
            na = []
        na.append({"at": "2026-11-25 02:0x", "by": "main", "text": rec["addendum"]})
        it["note_addendum"] = na
        signed.append(iss_id)

    # ── ② 新开三单 (直接落 fixing) ──
    for spec in NEW:
        issues.append({
            "id": spec["id"],
            "title": spec["title"],
            "severity": spec["severity"],
            "source_blocker": None,
            "desc": briefs[spec["id"]],
            "owner": spec["agent"],
            "need_keys": spec["need_keys"],
            "task_brief": briefs[spec["id"]],
            "note": spec["note"],
            "source_agent": "main",
            "verify_by": "main",
            "reporter": "main",
            "raised": "2026-11-25",
            "due": "2026-11-27",
            "status": "fixing",
            "external": False,
            "dispatched_at": "2026-11-25",
        })
    log["issues"] = issues

    # ── CAS 守卫 ──
    now_md5 = md5(LOG)
    if now_md5 != before_md5:
        sys.stderr.write("★CAS 守卫命中: issue_log.yaml 在读后被改 (%s → %s) ⇒ 中止, 不写盘\n"
                         % (before_md5, now_md5))
        return 3

    shutil.copy2(LOG, BACKUP)
    text = yaml.safe_dump(log, allow_unicode=True, sort_keys=False, width=100)
    atomic_write(LOG, text)

    # ── 写后回读自检 ──
    chk = read_yaml(LOG)
    chk_issues = chk.get("issues") or []
    ids = [it.get("id") for it in chk_issues]
    problems = []
    if len(chk_issues) != n_before + len(NEW):
        problems.append("条数 %d ≠ 期望 %d" % (len(chk_issues), n_before + len(NEW)))
    for spec in NEW:
        if ids.count(spec["id"]) != 1:
            problems.append("%s 出现 %d 次" % (spec["id"], ids.count(spec["id"])))
        got = [it for it in chk_issues if it.get("id") == spec["id"]]
        if not got or got[0].get("status") != "fixing" or got[0].get("owner") != spec["agent"]:
            problems.append("%s status/owner 不对" % spec["id"])
        if not got or len(str(got[0].get("task_brief") or "")) < 2000:
            problems.append("%s task_brief 没落进去" % spec["id"])
    for iss_id in SIGN:
        got = [it for it in chk_issues if it.get("id") == iss_id]
        if not got or got[0].get("status") != "verified":
            problems.append("%s 未落 verified" % iss_id)
    if problems:
        sys.stderr.write("★写后自检失败: %s ⇒ 回滚\n" % " | ".join(problems))
        shutil.copy2(BACKUP, LOG)
        return 2
    print("ISSUE_LOG_OK: %d → %d 条 | 签收 %s | 新开 %s (status=fixing) | md5 %s → %s"
          % (n_before, len(chk_issues), signed or "(已签)",
             [s["id"] for s in NEW], before_md5, md5(LOG)))

    # ── dispatch_log (追加式) ──
    if os.path.exists(DLOG):
        raw = read_yaml(DLOG)
        dl_list = raw if isinstance(raw, list) else (raw or {}).get("dispatches", [])
        n_dl = len(dl_list)
        entries = [{
            "issue": s["id"],
            "agent": s["agent"],
            "at": "2026-11-25 02:0x",
            "brief": s["brief_rel"],
            "job": ("cron fb67af40 (ARS45 队列自动派活) · ★2026-11-25 02:0x · ★**先落 fixing 再 spawn "
                    "(★铁律⑩-i ⇒ 零撞车窗口★) · ★**命令存在性守卫 "
                    "`python3 state/check_brief_commands.py --brief-file` rc=0** ★ · ★**纯查证/纯分析/"
                    "新建真相页 + 新建机器闸类 (零写板·零落表·零改既有闸·零改既有页正文·零挂链·零外发·不代拍) "
                    "⇒ 合「板只改一次」纪律 ①** ★"),
            "status_note": ("★台账 status 直接落 fixing ⇒ advance.py 的 in_flight 规则继续挡住任何 job 再给该 "
                            "agent 派活 ⇒ 零撞车窗口★"),
            "task_name": "queue_%s" % s["id"].lower(),
            "dispatched_at": "2026-11-25 02:0x",
            "run_id": RUN_ID,
        } for s in NEW]
        shutil.copy2(DLOG, DLOG_BACKUP)
        with io.open(DLOG, "a", encoding="utf-8") as f:
            f.write(yaml.safe_dump(entries, allow_unicode=True, sort_keys=False, width=200))
        chk_dl = read_yaml(DLOG)
        chk_list = chk_dl if isinstance(chk_dl, list) else (chk_dl or {}).get("dispatches", [])
        if len(chk_list) != n_dl + len(entries):
            sys.stderr.write("★dispatch_log 自检失败 ⇒ 回滚\n")
            shutil.copy2(DLOG_BACKUP, DLOG)
            return 2
        print("DISPATCH_LOG_OK: %d → %d 条" % (n_dl, len(chk_list)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
