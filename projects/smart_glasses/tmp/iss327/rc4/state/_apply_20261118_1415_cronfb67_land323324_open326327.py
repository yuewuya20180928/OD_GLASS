#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-323 / ISS-324 落地 (fixing → verified) + 新开 ISS-326 (mech-lead) / ISS-327 (sw-lead)

   · cron fb67af40 (ARS45 队列自动派活) · 2026-11-18 14:1x ★

★**为什么有本脚本** (★main 14:0x~14:2x 本机实读·不抄 agent 报告★):

  · ISS-323 (sw-lead) 子会话 `agent:sw-lead:subagent:f756a302-…` 12:5x 起 → **13:05:07 跑完 (status=done)**
    ⇒ main 14:0x 独立复核:
      - 主交付物 `SW/ONETRIP_SW_SAMEBATCH_RENAME_LIST.md` = **73,568 B** · §0~§6 七节全在 · 占位符 **0**
      - 交卷页 `HANDOFF/2026-11-18_sw-lead_ISS323_SW侧同批改动可执行清单.md` = **35,175 B** · B0~B6 齐全 · 占位符 **0**
      - `logs/iss323/` = **109 件** (80 份 raw_rootS* 场景输出 + 沙盒脚本 + 证据)
      - 分片 `state/fragments/sw.yaml` 命中 `iss323` = **14** (已写) · artifacts 220 条 / needs 129 条 / claims 284 条
      - ★**零写板双证**: 板 md5 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413` 逐字节未变
      - ★**闸链本机实跑 (main 自己跑·不抄它的报告)**:
          `SW/tools/check_sw_ref_reachability.py` ⇒ **rc=0** (「✔ 绿 (rc=0): SW 侧引用的位号全部可达, 真隐患在基线内」)
          `SW/tools/check_demo_panel_spec.py` ⇒ **rc=0** · `--selftest` ⇒ **rc=0 (SELFTEST 22/22)**
          `SW/tools/timing_check.py` ⇒ **rc=0 (SELFTEST 85/85)**
          `SW/tools/check_onepass_sw_sync.py --selftest` ⇒ **rc=0**
        ⇒ 交卷判据 (主文档 + 交卷页 + 占位符 0 + 悬空引用 0 + 分片已写 + 零写板 + 闸链全绿) ⇒ 落 verified

  · ISS-324 (mech-lead) 子会话 `agent:mech-lead:subagent:1330ac00-…` 12:5x 起 → **13:03 跑完 (status=done)**
    ⇒ main 14:1x 独立复核:
      - 主交付物 `MECH/ONETRIP_D_LED_G_PLACEMENT_CALIBER.md` = **63,552 B** · §0~§9 · 占位符 **0**
      - 交卷页 `HANDOFF/2026-11-18_mech-lead_ISS324_D_LED_G落位口径.md` = **35,686 B** · 占位符 **0**
      - `logs/iss324/` = **31 件** (12 份编号日志 + 9 个探针脚本)
      - 分片 `state/fragments/mech.yaml` 命中 `iss324` = **5** (已写)
      - ★**零写板双证**: 板 md5 + mtime 逐字节未变
      - ★**MECH 侧 5 道闸本机实跑全绿**: `board_frame_feasibility.py --selftest` rc=0 ·
        `check_onepass_mech_sync.py --selftest` rc=0 · `check_board_frame_coords.py` rc=0 ·
        `check_demo_struct_truth.py` rc=0 · `check_onepass_mech_release.py` rc=0
      - ★**它挖出并订正的真问题 (main 已核)**: ① `05_candidates.log` 里 C1/C4 的「净距 0.000」是 M1 铜箔口径,
        真值 M3 焊盘边缘距也是 0.000, 但要分同网/异网 (`R_LED_G`.2↔`D_LED_G`.1 同网 ⇒ 合法;
        `C_KEY_CAM`.1↔`D_LED_G`.2 异网 ⇒ < netclass 0.20 ⇒ 板 DRC 必红 ⇒ C1/C4 淘汰)
        ② `LED_G_D` 从 93.492727 mm 压到 1.477 mm (首选封装原点 (8.420, 64.200)) ⇒ 根因 = 排版器按功能排落位
        ③ 「结构侧零规定」不成立 (MECH 域实读 115 行, 不是 149)
      ⇒ 交卷判据齐 ⇒ 落 verified

★**为什么新开 ISS-326 / ISS-327 (而不是让 main 自己干)**:
  · ★**ISS-326 (mech-lead)**: ★**main 本轮实跑发现一个【从来没人做过的体检】**: S1 改名会动 218 行里 186 个 ref,
    而 MECH 域有 10+ 个判据脚本**硬编**了其中至少 18 个 (`J_DEBUG` / `J_UART` / `J_USB_C` / `J_CHG` / `CONN_CAM` /
    `CONN_LIGHT` / `D_LED_G` / `R_LED_G` / `R_SEL_D0_N` / `R_SEL_D1_N` …) ⇒ ★**`MECH/check_board_frame_coords.py` L999
    是 `fps[LED_REF]` (直接下标 ⇒ 改名后 KeyError) 而 L963 是 `fps.get(LED_REF)` (安全)** ⇒ **崩溃点不在直觉上**;
    ★**`MECH/check_onepass_struct_crosscheck.py` L1107/L1129 是 `t["ref"] == "R_SEL_D0_N"` ⇒ 改名后【永不匹配】= 假绿 (更坏)**;
    ★**★而 MECH 域【连位号可达性闸都没有】(SW 侧有 ISS-318 建的 `check_sw_ref_reachability.py`, 且它的 `DOC_GLOB`
    = `SW/*.md` + `AUX_PY_DIRS` = SW/tools·state·HW ⇒ 【`MECH/*.py` 完全不在它的扫描面】)** ⇒ **MECH 侧是真空** ★
    ⇒ 这是「板只改一次」那一趟的**真拦路虎**: 不体检 ⇒ 板改完才发现 MECH 闸崩 ⇒ 那一趟出不来 ⇒ 板改两次
  · ★**ISS-327 (sw-lead)**: ★**SW 侧的同类问题另一半**: `check_sw_ref_reachability.py` 有 C2 `DESIGNATOR_DRIFT`
    (建闸日冻结注册表) ⇒ 改名后必然漂移; ★**`--freeze-registry` 这条重建路径【已经存在但从来没被验证过】** ⇒
    板那一趟当天到底能不能靠它回绿, 现在是 [0数据] ⇒ 交一份【改名后 10 道闸的真实读数表 + 当天 SOP + 真隐患不被洗白的反向用例】

★**为什么这两条都【零写板】**: 老板 2026-11-17 00:43「接下来的目标是绘制 PCB 图」⇒ PCB 类可派;
  但「板只改一次」铁律 ⇒ ★**先派【纯分析/沙盒验证】类 (不动板)**, 真动板那一趟必须一次做完 ★
"""
from __future__ import annotations

import fcntl
import os
import shutil
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
LOG = os.path.join(HERE, "issue_log.yaml")
DL = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
NOW = "2026-11-18"
STAMP = "20261118_1415"

BRIEF_326 = open(
    os.path.join(HERE, "dispatch_briefs", "ISS-326_mech_s1_rename_safety_audit.md"),
    encoding="utf-8").read()
BRIEF_327 = open(
    os.path.join(HERE, "dispatch_briefs", "ISS-327_sw_postrename_gate_sop.md"),
    encoding="utf-8").read()

TITLE_326 = (
    "★★[主线内·MECH 侧·判据安全性体检类·内部活] ★★【S1 位号改名「MECH 侧」安全性体检: "
    "MECH 域 10+ 个判据脚本硬编了 218 行改名表里 186 个待改名 ref 中的至少 18 个 "
    "(J_DEBUG/J_UART/J_USB_C/J_CHG/CONN_CAM/CONN_LIGHT/D_LED_G/R_LED_G/R_SEL_D0_N/R_SEL_D1_N …) "
    "⇒ 区分【崩】(check_board_frame_coords.py L999 `fps[LED_REF]` 直接下标) vs 【假绿】"
    "(check_onepass_struct_crosscheck.py L1107/L1129 `t[\"ref\"] == \"R_SEL_D0_N\"` 改名后永不匹配) "
    "⇒ 再补 MECH 域【从没有过】的位号可达性闸设计稿 (只给设计, 不挂链)】★★ "
    "⇒ ★**纯体检 + 沙盒实证 · 零写板 · 零落表 · 零改闸** ★"
)

NOTE_326 = (
    "★**2026-11-18 14:1x · cron fb67af40 (ARS45 队列自动派活) 新开并直接派出 "
    "(status 直接落 fixing ⇒ 下一轮 in_flight 规则会跳过 mech-lead ⇒ 窗口消失 ⇒ 不与兄弟 job 775d9893 撞车)** ★ "
    "★**开单依据 (★main 14:0x~14:1x 本机实读·不抄任何 agent 报告★)**: "
    "★**① 改名表逐行解析 (main 自己写的 python)**: `HW/PCB/ONETRIP_S1_THREE_SIDE_RENAME_LIST.md` §1 = **218 行 "
    "⇒ 改名 186 / 不动 32** ★ ⇒ **这 186 个里 MECH 域硬编过的至少 18 个** "
    "(`J_DEBUG`→`_1` · `J_UART`→`_1` · `J_USB_C`→`_1` · `J_CHG`→`_1` · `CONN_CAM`→`_1` · `CONN_LIGHT`→`_1` · "
    "`D_LED_G`→`_1` · `R_LED_G`→`_1` · `D_LED_B`/`D_LED_R`/`R_LED_B`/`R_LED_R`/`TP_LED_B`/`TP_LED_R` 各加 `_1` · "
    "`R_SEL_D0_N`→`_1` · `R_SEL_D1_N`→`_1`) ★ ★**不动的那 32 个里有 `J_SOM_P1..P4` ⇒ `SOM_REFS` 不是风险 (不许误报)** ★ "
    "★**② MECH 域硬编位号的文件 (main 全仓 grep 逐文件数出来的)**: "
    "`check_board_frame_coords.py` (D_LED_G/J_DEBUG/J_UART/R_LED_G) · `check_onepass_struct_crosscheck.py` "
    "(J_CHG/J_DEBUG/J_UART/J_USB_C/R_SEL_D0_N/R_SEL_D1_N) · `check_demo_struct_truth.py` (CONN_CAM/CONN_LIGHT/J_CHG) · "
    "`board_port_opening_s6_check.py` (D_LED_B/G/R + J_CHG + J_DEBUG + J_UART + R_LED_B/G/R) · "
    "`check_onepass_mech_sync.py` (J_DEBUG/J_UART/J_USB_C) · `check_hinge_fpc_truth.py` · `hinge_usb_check.py` · "
    "`jd_y0_feasibility.py` · `service_port_check.py` · `check_mech_verdict_freshness.py` "
    "★**③ ★★MECH 域【没有位号可达性闸】★★**: `ls MECH/` 里无任何 reach/ref/drift/designator 文件; "
    "而 SW 侧那道 `SW/tools/check_sw_ref_reachability.py` 的 `DOC_GLOB` = `SW/*.md` + `AUX_PY_DIRS` = SW/tools·state·HW "
    "⇒ ★**`MECH/*.py` 完全不在它的扫描面** ⇒ **MECH 侧是真空** ★ "
    "★**④ 两处真崩溃/假绿点 (main 读源码确认, 任务书要求 agent 实跑出来)**: "
    "`check_board_frame_coords.py` **L999 `fps[LED_REF]` (直接下标 ⇒ KeyError)** vs **L963 `fps.get(LED_REF)` (安全)** "
    "⇒ ★**同一个文件两种写法 ⇒ 崩溃点不在直觉上**; "
    "`check_onepass_struct_crosscheck.py` **L1107/L1129 `if t[\"ref\"] == \"R_SEL_D0_N\":`** ⇒ 改名后【永不匹配】 "
    "⇒ ★**不是崩, 是那条判据从此不生效 = 假绿 (更坏的一类)** ★ "
    "★**⑤ MECH 域位号字面量规模 (main 实测顶层 `MECH/*.md` + `MECH/*.py`)**: **571 处** "
    "(前 5: `BOARD_ONEPASS_STRUCT_CROSSCHECK.md` 174 · `BOARD_ONEPASS_MECH_SYNC.md` 129 · "
    "`ONETRIP_D_LED_G_PLACEMENT_CALIBER.md` 120 · `BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` 116 · "
    "`BOARD_ONEPASS_MECH_CLAIMS.md` 74) ⇒ ★**任务书要求 agent 给【递归全量】的数 (对不上顶层数就说明漏了子目录)** ★ "
    "★**⑥ 为什么这件事卡「板只改一次」**: 不体检 ⇒ 板改完才发现 MECH 闸崩 ⇒ 那一趟出不来 ⇒ **板改两次** "
    "⇒ ★**这正是「板只改一次」铁律要防的事** ⇒ 体检必须【在动板之前】做完 ★ "
    "★**任务书全文**: `state/dispatch_briefs/ISS-326_mech_s1_rename_safety_audit.md` "
    "(★`python3 state/check_brief_commands.py --brief-file <它>` ⇒ rc=0·★派活前已过命令存在性守卫★) ★ "
    "★**边界**: 零写板 · 零落表 · 零改闸 (`MECH/*.py` 一个字不许改·只出体检 + 设计稿) · 零改既有文档正文 · "
    "沙盒只写 `tmp/iss326/` + `logs/iss326/` · 只写 `state/fragments/mech.yaml` · "
    "零改 `state/gate_check.py` (★挂闸归 main★) · 零外发 (★老板 2026-11-11 19:31 + 2026-11-12 02:02: "
    "不再发信, 全靠自己查资料·需要外部资料一律自己网上查 + 标证据等级 + 查不到写降级方案★) · "
    "不替老板拍板 · 不自签 issue_log ★"
)

TITLE_327 = (
    "★★[主线内·SW 侧·沙盒验证 + 当天 SOP 类·内部活] ★★【S1 位号改名「SW 侧」改名后【闸链复活】验证: "
    "在沙盒里把整棵树改名后跑完 10 道 SW 闸 ⇒ 交【改名前 / 改名后·重建注册表前 / 改名后·重建注册表后】三列读数表 "
    "+「板那一趟」当天的 SW 侧可执行 SOP (每步命令 + 期望读数 + 回滚三档) "
    "+ 「真隐患不许被 --freeze-registry 洗白」的反向用例 + 判据设计稿 (只给设计, 不挂链)】★★ "
    "⇒ ★**纯沙盒验证 · 零写板 · 零落表 · 零改闸** ★"
)

NOTE_327 = (
    "★**2026-11-18 14:1x · cron fb67af40 (ARS45 队列自动派活) 新开并直接派出 "
    "(status 直接落 fixing ⇒ 下一轮 in_flight 规则会跳过 sw-lead ⇒ 窗口消失 ⇒ 不与兄弟 job 775d9893 撞车)** ★ "
    "★**开单依据 (★main 14:0x~14:1x 本机实读·不抄任何 agent 报告★)**: "
    "★**① `SW/tools/check_sw_ref_reachability.py` 的判定机制 (main 读源码确认)**: 三类 "
    "`DESIGNATOR_OK`(C1 · 现在找得到) · `DESIGNATOR_DRIFT`(C2 · ★**建闸时是真位号, 现在找不到了 = 改名漂移**) · "
    "`DESIGNATOR_MISSING`(C14 · 形状像位号但板/网表里从来没有过 = 真隐患); "
    "**它有建闸日冻结注册表 `DESIGNATOR_REGISTRY` (C2 的判决源)** ⇒ ★**改名之后, 每个被改名的 ref 在文档里都会变成 "
    "`DESIGNATOR_DRIFT` ⇒ 红灯数 = 改名涉及的 SW 文档引用数** ★ "
    "★**② 它自己写着**: 建闸日 `DESIGNATOR_MISSING` 基线 = **3 条** (`TP_TEMP` / `TP_INT` / `CONN_USB`), "
    "**允许上限 = 建闸日实测数 ⇒ 超了才红** ⇒ ★**改名后基线会漂, 而上限不会跟着漂 ⇒ 必须实测** ★ "
    "★**③ 重建命令已经存在但【从来没被验证过】**: `--freeze-registry` (源码 L834) ⇒ "
    "★**「改名后靠重建注册表能不能让 SW 侧 10 道闸全部回绿」今天是 [0数据] ⇒ 这就是本单要产的实测读数** ★ "
    "★**④ main 本轮实跑确认的基线**: `python3 SW/tools/check_sw_ref_reachability.py --dump-classification` "
    "⇒ **rc=0 绿 · `DESIGNATOR_MISSING` = 3 条** ⇒ **今天改名还没发生, 所以看不出来** ★ "
    "★**⑤ 10 道 SW 闸的清单** (★照 `logs/iss323/iss323_sb_run_all.sh`·一个不许少★): "
    "`check_demo_panel_spec.py` · `check_demo_panel_spec_r6_chainjudge_selftest.py` · "
    "`check_demo_panel_spec_r6_hardprot_iss315_selftest.py` · `check_demo_panel_spec_r6_selftest.py` · "
    "`check_landing_trace_obligation.py` · `check_onepass_sw_sync.py` · `check_shutdown_semantics.py` · "
    "`check_sw_ref_reachability.py` · `check_timing_review_adc_sync.py` · `timing_check.py` ★ "
    "★**⑥ 与 ISS-321 的关系**: ISS-321 已实测「S4 vs S8 对照组同样红 ⇒ 那三道 R6 selftest 的红**不是改名特有**」 "
    "⇒ ★**本单不许拿「改名引起」当借口把闸调软** ★ "
    "★**任务书全文**: `state/dispatch_briefs/ISS-327_sw_postrename_gate_sop.md` "
    "(★`python3 state/check_brief_commands.py --brief-file <它>` ⇒ rc=0·★派活前已过命令存在性守卫★) ★ "
    "★**边界**: 零写板 · 零落表 · 零改闸 (`SW/tools/*.py` 一个字不许改) · 零改既有文档正文 · "
    "沙盒只写 `tmp/iss327/` + `logs/iss327/` · 只写 `state/fragments/sw.yaml` · "
    "零改 `state/gate_check.py` (★挂闸归 main★) · 零外发 (★老板 2026-11-11 19:31 + 2026-11-12 02:02: "
    "不再发信, 全靠自己查资料·需要外部资料一律自己网上查 + 标证据等级 + 查不到写降级方案★) · "
    "不替老板拍板 · 不自签 issue_log ★"
)

VERIFY_323 = (
    "✅ verified (★main 2026-11-18 14:0x 独立复核·不抄 agent 报告★) ⇒ "
    "★**交卷物在盘**: `SW/ONETRIP_SW_SAMEBATCH_RENAME_LIST.md` (**73,568 B** · §0~§6 七节全在 · 占位符 **0**) + "
    "`HANDOFF/2026-11-18_sw-lead_ISS323_SW侧同批改动可执行清单.md` (**35,175 B** · B0~B6 齐全 · 占位符 **0**) + "
    "`logs/iss323/` (**109 件**: 80 份 raw_rootS* 场景输出 + 沙盒脚本 + 证据) + "
    "`state/fragments/sw.yaml` (★`iss323` 命中 **14**·已写·artifacts 220 / needs 129 / claims 284 条★) ★ "
    "⇒ ★**悬空引用 = 0** (★main 实测: 交付页引 21 个 `logs/iss323/` 路径 + 交卷页引 18 个 ⇒ 全部真实存在★ "
    "⇒ 唯 3 处「悬空」是**通配/区间写法** (`logs/iss323/raw_rootS` 是 `raw_rootS*.txt` 的前缀 · "
    "`logs/iss324/01`~`12` 是区间 · `logs/iss324/1*` 是通配) ⇒ 逐条核过 ⇒ 真悬空 **0**★) ★ "
    "⇒ ★**零写板双证**: 板 md5 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413` 交卷前后逐字节不变 ★ "
    "⇒ ★**闸链本机实跑 (main 自己跑)**: `SW/tools/check_sw_ref_reachability.py` ⇒ **rc=0** («✔ 绿 (rc=0): "
    "SW 侧引用的位号全部可达, 真隐患在基线内») · `check_demo_panel_spec.py` ⇒ **rc=0** · `--selftest` ⇒ **rc=0 (22/22)** · "
    "`timing_check.py` ⇒ **rc=0 (SELFTEST 85/85)** · `check_onepass_sw_sync.py --selftest` ⇒ **rc=0** · "
    "`state/merge.py` ⇒ rc=0 (产出 660 · 阻塞 43 · 未闭合需求 330 · 冲突 0) · `state/gate_check.py` ⇒ **rc=0** "
    "(Q1 18/18 · Q7 钉板 md5 闸链 9/9 全绿) · `state/issue_check.py` ⇒ **rc=0** ★ "
    "★**★本单最值钱的三条结论 (★main 已逐条核过★)**: "
    "★**① 「24 份 md / 834 处」这个数字是错的, 真值 = 41 份 / 10 份有命中 / 671 处** (★834 是三元组行数口径, "
    "iss321_sw_docs_bulk_24files need 已按真值改写★) ★ "
    "★**② 留证文档【不改】⇒ 闸红 (28 条漂移 + 2 条新增真隐患, 两条 = `R_CHG_LED` / `R_SER_USB_D_N`); "
    "【改】⇒ 闸绿但历史记录被改写 ⇒ 三方案 (甲/乙/丙) 已逐条实测并交 need, 不代拍** ★ "
    "★**③ 「改名特有炸点只有 3 道」+ 7 件逐件名** ⇒ 与 ISS-321 的「改名后 `timing_check.py` L1113 崩」互为印证 ★ "
    "★**4 条 need 交 main (只给建议默认值 + 不批的后果, 不代拍)**: "
    "`iss321_decide_rename_batch_scope` · `iss321_decide_r6_selftest_fixture_after_reboard` · "
    "`iss321_sw_docs_bulk_24files` · `iss321_decide_rename_doc_notation` ★"
)

VERIFY_324 = (
    "✅ verified (★main 2026-11-18 14:1x 独立复核·不抄 agent 报告★) ⇒ "
    "★**交卷物在盘**: `MECH/ONETRIP_D_LED_G_PLACEMENT_CALIBER.md` (**63,552 B** · §0~§9 · 占位符 **0**) + "
    "`HANDOFF/2026-11-18_mech-lead_ISS324_D_LED_G落位口径.md` (**35,686 B** · 占位符 **0**) + "
    "`logs/iss324/` (**31 件**: 12 份编号日志 + 9 个探针脚本) + "
    "`state/fragments/mech.yaml` (★`iss324` 命中 **5**·已写★) ★ "
    "⇒ ★**零写板双证**: 板 md5 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413` 逐字节不变 ★ "
    "⇒ ★**MECH 侧 5 道闸本机实跑全绿**: `board_frame_feasibility.py --selftest` rc=0 · "
    "`check_onepass_mech_sync.py --selftest` rc=0 · `check_board_frame_coords.py` rc=0 · "
    "`check_demo_struct_truth.py` rc=0 · `check_onepass_mech_release.py` rc=0 ★ "
    "★**★本单最值钱的三条结论 (★main 已核过★)**: "
    "★**① `D_LED_G` 落位: 首选封装原点 (8.420, 64.200) ⇒ `LED_G_D` 从 93.492727 mm 压到 1.477 mm "
    "(缩短 92.016 mm / 98.42%)** ★ 排序 = C3 首选 → C2 (8.050,63.900) 次选 → C5 (8.250,66.000) 备选 → "
    "C6 (2.500,60.000) 假设 B 专属 → **C1/C4 淘汰** ⇒ 根因 = 93.49 里 99.794% 是 X 向 ⇒ 排版器按功能排落位 "
    "把限流电阻和 LED 分居板子两端 ⇒ 板子够大 (角落 5.50 mm² 就够), 要改的是排版规则 ★ "
    "★**② 「结构侧零规定」不成立** — MECH 域实读 **115 行** (不是任务书说的 149), 分桶 A32/B6/C22/D37/E18; "
    "A 类里 F30A 专属 8 行 / 现役台架板专属 13 行 ⇒ 精确表述 = **【有空间与条件 · 无点位】**; "
    "最险的是 `BOARD_PORT_OPENING_S6_FRAME_CALIBER.md:32/:138` 的首选窗口数字**不带帧标**, 而同文件 `:99` 标 F30A "
    "⇒ 喂进现役板压 `J_SOM_P3` 10 焊盘 (机器已证, `check_board_frame_coords.py` C3 ✅) ★ "
    "★**③ 它订正了 main 上一轮的读数**: `05_candidates.log` 里 C1/C4 的「净距 0.000」**不是测量假象** — "
    "那是 M1 铜箔外框口径, 它另建 M2/M3 复算证明 **M3 焊盘边缘距也真是 0.000**, 但要分同网/异网: "
    "`R_LED_G`.2↔`D_LED_G`.1 同网 ⇒ 合法; `C_KEY_CAM`.1↔`D_LED_G`.2 异网 ⇒ < netclass 0.20 ⇒ **板 DRC 必红** ⇒ C1/C4 淘汰; "
    "顺带订正 main 12:1x 那个 1.273 (★是拿错 pad2 算的, 真值 M2=1.082 / M3=0.000★) ★ "
    "★**它交回 main / 老板的 need**: `iss324_d_led_g_placement_decision` (★to=boss · due=2026-11-18 · "
    "一句话问法「`D_LED_G` 落在板上哪个点 + 亮度档已拍后是否还要动器件位置」· 建议默认值 = 假设 B (无光孔/位置不动)★) "
    "★**并声明改亮度档只改器件值、不改器件位置 ⇒ 两件事独立**; 另交 3 条 interface_claims 给 hw-lead "
    "(候选坐标行 + 网长判据 + 净距判据) + §8 的 D1~D7 新闸设计 + 9 条反向用例 (★只给设计不建闸, 建议放 `HW/` 归 hw-lead★) ★"
)


def atomic_write(path: str, text: str) -> None:
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_", suffix=".yaml")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def main() -> int:
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        # ★锁内重读 (★不许用锁外读到的旧内容写回★)
        log = yaml.safe_load(open(LOG, encoding="utf-8")) or {}
        issues = log.get("issues") or []
        idx = {i.get("id"): i for i in issues}
        applied = []

        # ---------- ① ISS-323 → verified ----------
        i323 = idx.get("ISS-323")
        if i323 and i323.get("status") != "verified":
            i323["status"] = "verified"
            i323["verify_date"] = NOW
            i323["verify_by"] = "main"
            i323["verify_result"] = VERIFY_323
            i323["note"] = (i323.get("note") or "") + (
                f"\n★**{NOW} 14:0x · cron fb67af40 (ARS45 队列自动派活) 落地 verified** ★ "
                "★**独立复核**: 主文档 73,568 B §0~§6 + 交卷页 35,175 B B0~B6 + 占位符 0/0 + 悬空引用 0 + "
                "`logs/iss323/` 109 件 + 分片命中 14 + 板 md5/mtime 逐字节不变 + "
                "★**闸链本机实跑全绿 (check_sw_ref_reachability rc=0 · check_demo_panel_spec rc=0 + selftest 22/22 · "
                "timing_check rc=0 85/85 · check_onepass_sw_sync --selftest rc=0 · gate rc=0 Q1 18/18 Q7 9/9 · "
                "merge rc=0 · issue_check rc=0)** ★ "
                "★**它订正了一个错数字**: 「24 份 md / 834 处」⇒ 真值 **41 份 / 10 份有命中 / 671 处** ★ "
                "★**4 条 need 交 main (不代拍)** ⇒ **续单已开 = ISS-327 (SW 侧改名后闸链复活验证)** ★")
            applied.append("ISS-323 fixing → verified (main 独立复核)")
        elif i323:
            applied.append("ISS-323 已是 verified (跳过)")

        # ---------- ② ISS-324 → verified ----------
        i324 = idx.get("ISS-324")
        if i324 and i324.get("status") != "verified":
            i324["status"] = "verified"
            i324["verify_date"] = NOW
            i324["verify_by"] = "main"
            i324["verify_result"] = VERIFY_324
            i324["note"] = (i324.get("note") or "") + (
                f"\n★**{NOW} 14:1x · cron fb67af40 (ARS45 队列自动派活) 落地 verified** ★ "
                "★**独立复核**: 主文档 63,552 B §0~§9 + 交卷页 35,686 B + 占位符 0/0 + `logs/iss324/` 31 件 + "
                "分片命中 5 + 板 md5/mtime 逐字节不变 + "
                "★**MECH 侧 5 道闸本机实跑全绿 (board_frame_feasibility --selftest / check_onepass_mech_sync --selftest / "
                "check_board_frame_coords / check_demo_struct_truth / check_onepass_mech_release 全部 rc=0)** ★ "
                "★**它订正了 main 上一轮的一个错读数**: C1/C4 的「净距 0.000」不是测量假象 ⇒ "
                "M3 焊盘边缘距也真是 0.000, 但要分同网/异网 (`C_KEY_CAM`.1↔`D_LED_G`.2 异网 ⇒ 板 DRC 必红 ⇒ C1/C4 淘汰); "
                "main 12:1x 那个 1.273 是拿错 pad2 算的, 真值 M2=1.082 / M3=0.000 ★ "
                "★**need `iss324_d_led_g_placement_decision` 交老板 (due 2026-11-18)** ⇒ "
                "★**续单已开 = ISS-326 (MECH 侧 S1 改名安全性体检)** ★")
            applied.append("ISS-324 fixing → verified (main 独立复核)")
        elif i324:
            applied.append("ISS-324 已是 verified (跳过)")

        # ---------- ③ ISS-325 状态说明 (不动 status: 仍 fixing ⇒ hw-lead 仍被 in_flight 挡住) ----------
        i325 = idx.get("ISS-325")
        if i325:
            i325["note"] = (i325.get("note") or "") + (
                f"\n★**{NOW} 14:2x · cron fb67af40 状态说明 (★status 保持 fixing·**不改**★)**: "
                "★**hw-lead 的子会话 `agent:hw-lead:subagent:a1789e10-…` 于 13:35 被父 cron run 连带 abort** "
                "(status=timeout · abortedLastRun=true · runtimeMs=2118969) ⇒ "
                "★**但它启动的两条沙盒臂仍在后台真跑 (PID 1043798 / 1044628 · 各吃满一个核 · "
                "日志 `/tmp/iss325_s8lu_R.log` / `/tmp/iss325_s8ctl_R.log` · 产物 `/tmp/iss325_s8lu_R.kicad_pcb` 等)** ⇒ "
                "★**⇒ 本单 [零写板] 仍然成立 (板 md5 `611b869e13518c3c023fb178f91a0075` + mtime 逐字节未变)★** ★ "
                "★**⇒ 但交付页还有 4 处占位符没填 (`__FLIP__` / `__TOTAL__` / `__UNC__` / `__ZEROREACH__`) "
                "+ 交卷页缺 B1/B2/B4/B5 + 分片 `hw.yaml` 命中 `iss325` = 0 (未写) ⇒ **本单尚未交卷** ★ "
                "★**⇒ 处置: status 保持 fixing (★不回滚成 open ⇒ 下一轮 in_flight 规则继续跳过 hw-lead ⇒ "
                "无重复派活窗口·也不会跟兄弟 job 775d9893 撞车★)** ⇒ "
                "★**下一轮 (臂跑完之后) 再派 cont1 收卷** ★")
            applied.append("ISS-325 保持 fixing (★已留痕·臂仍在跑·下一轮收卷★)")

        # ---------- ④ 新开 ISS-326 (mech-lead · status 直接落 fixing) ----------
        if "ISS-326" not in idx:
            issues.append({
                "id": "ISS-326",
                "title": TITLE_326,
                "owner": "mech-lead",
                "status": "fixing",
                "severity": "high",
                "reporter": "main",
                "raised": NOW,
                "due": "2026-11-19",
                "created_at": NOW,
                "dispatched_at": NOW,
                "verify_by": "main",
                "source_blocker": "ISS-317",
                "task_brief": BRIEF_326,
                "note": NOTE_326,
                "need_keys": [
                    "iss326_mech_rename_hardcode_inventory",
                    "iss326_mech_ref_reachability_gate_design",
                ],
            })
            applied.append("ISS-326 开单 (status=fixing ⇒ 已派)")
        else:
            applied.append("ISS-326 已存在 (跳过)")

        # ---------- ⑤ 新开 ISS-327 (sw-lead · status 直接落 fixing) ----------
        if "ISS-327" not in idx:
            issues.append({
                "id": "ISS-327",
                "title": TITLE_327,
                "owner": "sw-lead",
                "status": "fixing",
                "severity": "high",
                "reporter": "main",
                "raised": NOW,
                "due": "2026-11-19",
                "created_at": NOW,
                "dispatched_at": NOW,
                "verify_by": "main",
                "source_blocker": "ISS-318",
                "task_brief": BRIEF_327,
                "note": NOTE_327,
                "need_keys": [
                    "iss327_sw_postrename_gate_readings",
                    "iss327_sw_drift_registry_disposition",
                ],
            })
            applied.append("ISS-327 开单 (status=fixing ⇒ 已派)")
        else:
            applied.append("ISS-327 已存在 (跳过)")

        # ---------- ⑥ 落盘 issue_log (原子) ----------
        out = dict(log)
        out["issues"] = issues
        shutil.copy2(LOG, LOG + ".bak_cronfb67_%s_land323324_open326327" % STAMP)
        atomic_write(LOG, yaml.safe_dump(out, allow_unicode=True, sort_keys=False, width=100000))

        # ---------- ⑦ dispatch_log ----------
        dl = yaml.safe_load(open(DL, encoding="utf-8")) or {}
        disp = dl.get("dispatches") or []
        for iid, agent, note in (
            ("ISS-323", "sw-lead",
             "★**落地 (fixing → verified)** ★ ★**main 14:0x 本机独立复核**: 主文档 73,568 B §0~§6 + 交卷页 35,175 B "
             "B0~B6 + 占位符 0/0 + 悬空引用 0 + `logs/iss323/` 109 件 + 分片命中 14 + 板 md5/mtime 逐字节不变 + "
             "★**闸链本机实跑全绿 (check_sw_ref_reachability rc=0 · check_demo_panel_spec rc=0 + selftest 22/22 · "
             "timing_check rc=0 85/85 · check_onepass_sw_sync --selftest rc=0 · gate rc=0 Q1 18/18 Q7 9/9 · merge rc=0 · "
             "issue_check rc=0)** ★ ★**它订正了「24 份 md / 834 处」⇒ 真值 41 份 / 10 份有命中 / 671 处** ★ "
             "★**4 条 need 交 main (不代拍)** ★"),
            ("ISS-324", "mech-lead",
             "★**落地 (fixing → verified)** ★ ★**main 14:1x 本机独立复核**: 主文档 63,552 B §0~§9 + 交卷页 35,686 B + "
             "占位符 0/0 + `logs/iss324/` 31 件 + 分片命中 5 + 板 md5/mtime 逐字节不变 + "
             "★**MECH 侧 5 道闸本机实跑全绿** ★ ★**它订正了 main 上一轮的错读数 (1.273 ⇒ M2=1.082 / M3=0.000)** ★ "
             "★**need `iss324_d_led_g_placement_decision` 交老板 (due 2026-11-18)** ★"),
            ("ISS-325", "hw-lead",
             "★**状态说明 (status 保持 fixing·不改)** ★ ★**hw-lead 子会话 13:35 被父 run 连带 abort, "
             "但两条沙盒臂仍在后台真跑 (PID 1043798/1044628)** ⇒ 零写板仍成立 (板 md5/mtime 逐字节未变) ⇒ "
             "★**但交付页有 4 处占位符没填 + 交卷页缺 B1/B2/B4/B5 + 分片未写 ⇒ 尚未交卷** ⇒ "
             "★**下一轮 (臂跑完) 派 cont1 收卷** ★"),
            ("ISS-326", "mech-lead",
             "★**新开并直接派出** (★status=fixing ⇒ 下一轮 in_flight 规则跳过 mech-lead ⇒ 无重复派活窗口★) ★ "
             "★**依据: main 14:0x 实读发现 MECH 域 10+ 判据脚本硬编了 218 行改名表里 186 个待改名 ref 中的至少 18 个 "
             "⇒ 崩 (check_board_frame_coords.py L999 `fps[LED_REF]`) vs 假绿 "
             "(check_onepass_struct_crosscheck.py L1107 `t[\"ref\"] == \"R_SEL_D0_N\"`) ⇒ "
             "★**且 MECH 域【连位号可达性闸都没有】(SW 那道的扫描面不含 `MECH/*.py`) ⇒ 真空** ★ "
             "★**这正是「板只改一次」要防的事: 不体检 ⇒ 板改完才发现闸崩 ⇒ 板改两次** ★"),
            ("ISS-327", "sw-lead",
             "★**新开并直接派出** (★status=fixing ⇒ 下一轮 in_flight 规则跳过 sw-lead ⇒ 无重复派活窗口★) ★ "
             "★**依据: main 14:0x 实读 `check_sw_ref_reachability.py` 的 C2 `DESIGNATOR_DRIFT` (建闸日冻结注册表) "
             "⇒ 改名后必然漂移; `--freeze-registry` 重建路径【已存在但从没被验证过】⇒ "
             "★**「改名后靠它能不能让 10 道 SW 闸全部回绿」今天是 [0数据]** ⇒ 本单产实测读数表 + 当天 SOP + "
             "★**「真隐患不许被重建洗白」的反向用例** ★"),
        ):
            if not any(isinstance(d, dict) and d.get("issue") == iid and "14:1x" in str(d.get("brief"))
                       for d in disp):
                disp.append({
                    "issue": iid, "agent": agent, "at": NOW, "brief": note,
                    "job": ("cron fb67af40 (ARS45 队列自动派活) · ★派活时刻 2026-11-18 14:1x · "
                            "★**status 全程 fixing ⇒ 无 open 窗口 ⇒ 兄弟 job 775d9893 不会重复派** ★"),
                })
                applied.append("dispatch_log 追加 %s" % iid)
        dl["dispatches"] = disp
        shutil.copy2(DL, DL + ".bak_cronfb67_%s_land323324_open326327" % STAMP)
        atomic_write(DL, yaml.safe_dump(dl, allow_unicode=True, sort_keys=False, width=100000))

        for a in applied:
            print("· %s" % a)
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
