#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-320 / ISS-321 落地 (fixing → verified) + 新开 ISS-323 (sw-lead) / ISS-324 (mech-lead)
   · cron fb67af40 (ARS45 队列自动派活) · 2026-11-18 11:4x ★

★**为什么有本脚本** (★main 11:4x 本机实读·不抄 agent 报告★):
  · ISS-320 (mech-lead) 子会话 `agent:mech-lead:subagent:474f4de9-...` 10:38 起 · **11:29:56 跑完 (status=done)**
    ⇒ main 11:4x 独立复核:
      - 交卷页 `HANDOFF/2026-11-18_mech-lead_ISS320_电芯型号订正实做.md` = 23,810 B · **293 行** · B0~B6 六块齐全
      - 占位符扫描 = 0
      - `logs/iss320/` = **23 件** (含 VERIFY_REPORT.txt + 2 个 apply/verify 脚本 + md5_ALL_BEFORE.txt 4 MB + 台账 ledger_state.json)
      - 台账 `logs/iss320/ledger_state.json`: **rows 32 条 (实做) + keep 12 条 (11 留证 + 1 撤回) = 33 行对得上**
      - 受保护脚本 `MECH/service_port_check.py` md5 = `db58ff6a2afc28b8bf517e3c57c56bc1` (★= 钉板闸⑧ 的基线 ⇒ 闸⑧ 绿★)
      - 分片 `state/fragments/mech.yaml` 命中 `iss320|ISS-320` = **8** (已写)
      - ★零写板双证: 板 md5 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413` 逐字节未变
    ⇒ 交卷判据 (交卷页 B0~B6 + 台账逐行对上 + 分片已写 + 受保护脚本回基线) 四件齐 ⇒ 落 verified

  · ISS-321 (sw-lead) 子会话 `agent:sw-lead:subagent:e0dffb46-...` 10:41 起 · **11:14:32 跑完 (status=done)**
    ⇒ main 11:4x 独立复核:
      - 交卷页 `HANDOFF/2026-11-18_sw-lead_ISS321_SW侧改名安全性体检.md` = 28,416 B · **330 行** · B0~B7 七块齐全
      - 交付页 `SW/ONETRIP_SW_RENAME_SAFETY.md` = 34,339 B · **447 行** · §0~§6
      - 占位符扫描 = 0 / 0
      - `logs/iss321/` = **104 件** (含 14 个机器脚本 · 8 场景 × 10 闸 = 80 次实跑原始读数)
      - 分片 `state/fragments/sw.yaml` 命中 `iss321|ISS-321` = **28** (已写)
      - ★**闸链本机实跑回绿**: `python3 state/gate_check.py` ⇒ **rc=0** · Q1 **18/18** · Q7 钉板 md5 闸链 **9/9 全绿**
        (★11:0x 那轮唯一红项「ISS-318 SW 侧位号引用可达性闸」18 条真隐患 ⇒ ISS-321 交卷后已消★)
      - ★零写板双证: 同上
    ⇒ 交卷判据四件齐 ⇒ 落 verified

★**为什么这两个 agent 现在能接新单**: ISS-320 / ISS-321 落 verified ⇒ 两个 agent 名下无 fixing
  ⇒ ★**新开 ISS-323 / ISS-324 直接落 fixing ⇒ 下一轮 in_flight 规则仍会跳过它们 ⇒ 无 open 窗口 ⇒ 不与兄弟 job 775d9893 撞车** ★
★**hw-lead 本轮不派**: ISS-322 子会话 `agent:hw-lead:subagent:b3cb742d-...` **11:4x 实测 status=running** (★还在跑终验★)
  ⇒ ★**铁律「一个 agent 同时只允许一个写会话」⇒ 本轮跳过 hw-lead (★它交卷后下一轮落地+再派★)** ★
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
STAMP = "20261118_1145"

BRIEF_323 = open(
    os.path.join(HERE, "dispatch_briefs", "ISS-323_sw_s1_samebatch_rename_list.md"),
    encoding="utf-8").read()

BRIEF_324 = open(
    os.path.join(HERE, "dispatch_briefs", "ISS-324_mech_d_led_g_placement.md"),
    encoding="utf-8").read()

TITLE_323 = (
    "★★[主线内·SW 侧·逐字可执行清单类·内部活] ★★【「板只改一次」那一趟的 SW 侧: "
    "7 件必须同批改的活 (ISS-321 执行顺序表 #1~#7) 做成【逐字可执行清单】: "
    "每件给 改哪个文件 / 改前逐字 / 改后逐字 / 行号锚点 / 验收命令 / 归属 / 不改的后果 / 时序】★★ "
    "⇒ ★**纯分析 / 作业包 / 判据设计类** ★ ⇒ ★**零写板 · 零落表 · 零改闸 · 零改既有文档正文** ★"
)

NOTE_323 = (
    "★**2026-11-18 11:4x · cron fb67af40 (ARS45 队列自动派活) 新开并直接派出 "
    "(status 直接落 fixing ⇒ 下一轮 in_flight 规则会跳过 sw-lead ⇒ 窗口消失 ⇒ 不与兄弟 job 775d9893 撞车)** ★ "
    "★**开单依据 (★main 11:4x 本机实读·不抄任何 agent 报告★)**: "
    "★**① ISS-321 已 verified (11:3x)** ⇒ 它交的是【发现 + 改法】, ★**缺的是【像 ISS-317 那样的逐字可执行清单】** ★ "
    "★**② ISS-321 §4-6 执行顺序表给出「必须同批 7 件」+「可板后补 1 件」** ⇒ ★**这 7 件就是本单主体** ★ "
    "★**③ 改名特有炸的 3 道闸已定位**: `SW/tools/timing_check.py` (★崩在 L1113·TypeError★) · "
    "`SW/tools/check_timing_review_adc_sync.py` (★上游 fail-closed ⇒ rc=2★) · "
    "`SW/tools/check_demo_panel_spec_r6_chainjudge_selftest.py` ⇒ F-1 (25 处定点替换) / F-2 (3 条现状探针改成"
    "「从网表实读」) / F-3 (`DESIGNATOR_REGISTRY` 重建) 三条改法**都已在 ISS-321 沙盒里验证过** ⇒ ★**本单不重做沙盒, 只把改法变成可执行清单** ★ "
    "★**④ 第 4 件跨域** (`HW/check_netlist_selfconsistency.py` 16 个位号 / 116 处) 属 ★**hw-lead 的域** ⇒ ★**sw-lead 只准给逐字改法 + 交 need** ★ "
    "★**⑤ 第 7 件的量**: 24 份 md / 834 处位号字面量 ⇒ 不改 ⇒ 漂移闸判 58 条改名漂移 ⇒ ★**清单要交【怎么机器化改 + 怎么验】, 不是抄 834 行** ★ "
    "★**⑥ 闸链现状**: `python3 state/gate_check.py` ⇒ **rc=0** · Q1 18/18 · Q7 9/9 全绿 (★ISS-321 交卷后 SW 侧那道红已回绿·main 11:2x 实测★) "
    "⇒ ★**交卷时 rc 必须是 0, 若红必须逐字归因** ★ "
    "★**任务书全文**: `state/dispatch_briefs/ISS-323_sw_s1_samebatch_rename_list.md` "
    "(★`python3 state/check_brief_commands.py --brief-file <它>` ⇒ rc=0·★派活前已过命令存在性守卫★) ★ "
    "★**边界**: 零写板 · 零落表 · 零改闸 (★`SW/tools/*.py` 是受保护资产·只给逐字改法★) · 零改既有文档正文 · "
    "沙盒只写 `tmp/` + `logs/iss323/` · 只写 `state/fragments/sw.yaml` · 零外发 (★老板 2026-11-11 19:31 + "
    "2026-11-12 02:02: 不再发信, 全靠自己查资料·需要外部资料一律自己网上查 + 标证据等级 + 查不到写降级方案★) · "
    "不替老板拍板 · 不自签 issue_log ★"
)

TITLE_324 = (
    "★★[主线内·MECH 侧·落位口径 + 候选坐标类·内部活] ★★【`D_LED_G` 落位口径一页 (G12 的前置): "
    "93.492727mm 复算与根因分解 + 双板框假设坐标空间 + 出光孔有孔/无孔两假设 + G-5 亮度档事实订正 + "
    "≥3 个候选落位点 + 给 hw-lead 的 `PCB_PART_POS` 候选行 + 机器可判判据建议】★★ "
    "⇒ ★**纯分析 / 作业包 / 判据设计类** ★ ⇒ ★**零写板 · 零落表 · 零改闸 · 零改既有文档正文** ★"
)

NOTE_324 = (
    "★**2026-11-18 11:4x · cron fb67af40 (ARS45 队列自动派活) 新开并直接派出 "
    "(status 直接落 fixing ⇒ 下一轮 in_flight 规则会跳过 mech-lead ⇒ 窗口消失 ⇒ 不与兄弟 job 775d9893 撞车)** ★ "
    "★**开单依据 (★main 11:4x 本机实读·不抄任何 agent 报告★)**: "
    "★**① need `iss322_s8_d_led_g_pos` (G12)** = 「`D_LED_G` 落在板上的哪个点? (现状 `LED_G_D` 直线 93.49mm)」 · "
    "★**建议默认值 = 挪到 `R_LED_G` 同侧 (直线 < 20mm)** · ★**谁答 = mech-lead + 老板** ⇒ ★**MECH 侧没落位 ⇒ 这一条永远答不完** ★ "
    "★**② main 11:4x 本机 pcbnew 实读焊盘**: `R_LED_G.2` @ (7.50, 62.60) ↔ `D_LED_G.1` @ (100.80, 56.60) ⇒ "
    "★**直距 93.492727mm, 其中 X 向 93.30mm (99.794%)** ⇒ ★**根因 = 排版器按功能排, 不是板子不够大** ⇒ ★**两种挪法都能解** ★ "
    "★**③ 结构侧对 LED 位置零规定 = `[0数据]`** (★ISS-271 逐条 grep 实证★) ⇒ ★**这是本单要自己查掉的那条** ★ "
    "★**④ 出光孔 (结构侧光孔/导光窗) = `[0数据]`** ⇒ 有孔 / 无孔 两假设各一份 (★ISS-316 交回的待办★) ★ "
    "★**⑤ 板框 U-1 未拍** (① B160x100 台架板 / ② F30A 60×30 产品板 / ③ P60x15 已作废) ⇒ ★**坐标空间必须双假设各出一份** ★ "
    "★**⑥ ★★G-5 亮度档【已经拍了】★★**: ★**老板 2026-11-17 09:49 拍板 (ISS-283) 选项② = 改 R 到 20 mA 档** ⇒ "
    "★**绿 `R_LED_G` = 55Ω ±1% · 红 `R_LED_R` = 68Ω ±1%** (★`HW/netlist_v1.csv` 已带这条批注★) ⇒ "
    "★**⇒ ISS-271 当年记的「隐藏前置 (亮度档未拍 ⇒ 会破板只改一次)」这条已被拍板消掉** ★ ⇒ "
    "★**但板面器件值仍是旧的 `1k ±1%` (三个 LED 串阻封装都是 1k) ⇒ 【板那一趟要同步器件值】, 本单零落表, 只写进影响链** ★ "
    "★**⑦ 任务书全文**: `state/dispatch_briefs/ISS-324_mech_d_led_g_placement.md` "
    "(★`python3 state/check_brief_commands.py --brief-file <它>` ⇒ rc=0·★派活前已过命令存在性守卫★) ★ "
    "★**边界**: 零写板 · 零落表 · 零改闸 (★`MECH/*.py` 有 md5 钉死的受保护判据脚本★) · 零改既有文档正文 · "
    "沙盒只写 `tmp/` + `logs/iss324/` · 只写 `state/fragments/mech.yaml` · 零外发 (★老板 2026-11-11 19:31 + "
    "2026-11-12 02:02: 不再发信, 全靠自己查资料·结构件/LED 官网资料一律自己网上查 + 标证据等级 + 查不到写降级方案★) · "
    "不替老板拍板 (★只给候选坐标, 不给决定★) · 不自签 issue_log ★"
)

VERIFY_320 = (
    "✅ verified (★main 2026-11-18 11:4x 独立复核·不抄 agent 报告★) ⇒ "
    "★**交卷物在盘**: `HANDOFF/2026-11-18_mech-lead_ISS320_电芯型号订正实做.md` (23,810 B · **293 行** · B0~B6 齐全 · 占位符 0) + "
    "`MECH/ONETRIP_CELL_MODEL_RENAME_APPLY.md` (33 行台账) + `logs/iss320/` (**23 件**: VERIFY_REPORT.txt + 2 个 apply/verify 脚本 + "
    "`md5_ALL_BEFORE.txt` 4,063,564 B + `ledger_state.json` 41,892 B) + `state/fragments/mech.yaml` (★`iss320|ISS-320` 命中 **8**·已写★) ★ "
    "⇒ ★**台账逐行对上 (main 实读 `logs/iss320/ledger_state.json`)**: `rows` = **32 条 (实做)** + `keep` = **12 条 (11 留证 + 1 撤回)** "
    "= **33 行与任务书完全对得上** ★ "
    "⇒ ★**受保护判据脚本已回基线**: `MECH/service_port_check.py` md5 = `db58ff6a2afc28b8bf517e3c57c56bc1` "
    "(★= `MECH/check_demo_struct_truth.py` 的 `MD5_EXPECTED_SCRIPTS` 钉死基线 ⇒ 钉板闸⑧ G5b 绿★) ⇒ "
    "★**那 1 行改不动的 (`L51` 注释里的型号名) 是【可接受的已知不一致】, 跟板那一趟同批走合法改板通道** ★ "
    "⇒ ★**零写板双证**: 板 md5 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413` 交卷前后逐字节不变 ★ "
    "⇒ ★**闸链本机实跑**: `python3 state/gate_check.py` ⇒ **rc=0** · Q1 **18/18** · Q7 钉板 md5 闸链 **9/9 全绿** · "
    "`python3 state/issue_check.py` ⇒ **rc=0** · `python3 state/merge.py` ⇒ **rc=0** (产出 655 · 阻塞 43 · 未闭合需求 330 · 冲突 0) ★ "
    "★**交卷页自己声明的未完项如实留账 (不装完成)**: ① 采购单型号什么时候改 (★照旧型号买 ⇒ 到货厚 6.40mm ⇒ 装不进 7.30mm 镜脚 ⇒ "
    "H 链最坏 −1.10mm ⇒ 归 D-2-9 / owner = boss, 本单没拍板★) ② 那 1 行跟板那一趟同批走 (★不改零后果★) ★"
)

VERIFY_321 = (
    "✅ verified (★main 2026-11-18 11:4x 独立复核·不抄 agent 报告★) ⇒ "
    "★**交卷物在盘**: `SW/ONETRIP_SW_RENAME_SAFETY.md` (34,339 B · **447 行** · §0~§6) + "
    "`HANDOFF/2026-11-18_sw-lead_ISS321_SW侧改名安全性体检.md` (28,416 B · **330 行** · B0~B7 齐全 · 占位符 0) + "
    "`logs/iss321/` (**104 件**: 14 个机器脚本 · 8 场景 × 10 闸 = 80 次实跑原始读数) + "
    "`state/fragments/sw.yaml` (★`iss321|ISS-321` 命中 **28**·已写★) ★ "
    "⇒ ★**闸链本机实跑回绿**: `python3 state/gate_check.py` ⇒ **rc=0** · Q1 **18/18** · Q7 钉板 md5 闸链 **9/9 全绿** ★ "
    "★**这是本单最值钱的一条**: 11:0x 那轮 `gate_check.py` 的唯一红项 = 「ISS-318 SW 侧位号引用可达性闸」· 18 条真隐患全部来自 "
    "`SW/ONETRIP_SW_RENAME_SAFETY.md` (★sw-lead 10:47 写的★) ⇒ ★**ISS-321 交卷后该红项已消 ⇒ 闸链回到 rc=0** ★ "
    "⇒ ★**零写板双证**: 板 md5 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413` 交卷前后逐字节不变 ★ "
    "⇒ ★**核心结论 (main 实读交付页 §0/§4-6)**: 改名特有炸 3 道闸 (`timing_check.py` 崩在 L1113 · `check_timing_review_adc_sync.py` rc=2 · "
    "三道 R6 selftest 之一) ⇒ F-1 (25 处定点替换) / F-2 (3 条现状探针改成「从网表实读」) / F-3 (`DESIGNATOR_REGISTRY` 重建) "
    "三条改法沙盒已验证 (★改后 `timing_check` rc=0 · SELFTEST 65/85 → 85/85★) ⇒ ★**「板只改一次」那一趟的 SW 侧必须同批做 7 件, "
    "只有 1 件 (3 条基线隐患) 可板后补** ★ "
    "★**交卷页自己声明的未完项如实留账 (不装完成)**: 4 条 need (`iss321_decide_rename_batch_scope` · "
    "`iss321_decide_r6_selftest_fixture_after_reboard` · `iss321_sw_docs_rename_bulk_24files` · `iss321_decide_rename_doc_notation`) "
    "⇒ **归 main + 老板**, 本单不代拍 ⇒ ★**续单已开 = ISS-323 (把 7 件做成逐字可执行清单)· 11:4x 直接派出** ★"
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

        # ---------- ① ISS-320 → verified ----------
        i320 = idx.get("ISS-320")
        if i320 and i320.get("status") != "verified":
            i320["status"] = "verified"
            i320["verify_date"] = NOW
            i320["verify_by"] = "main"
            i320["verify_result"] = VERIFY_320
            i320["note"] = (i320.get("note") or "") + (
                f"\n★**{NOW} 11:4x · cron fb67af40 (ARS45 队列自动派活) 落地 verified** ★ "
                "★**独立复核**: 交卷页 293 行 B0~B6 + 台账 33 行 (32 实做 + 11 留证 + 1 撤回) 逐行对上 + "
                "`logs/iss320/` 23 件 + 分片命中 8 + 受保护脚本回基线 `db58ff6a…` + 板 md5/mtime 逐字节不变 ★ "
                "★**未完项如实留账**: 采购型号最终选哪颗 (D-2-9 · owner=boss) + 那 1 行跟板那一趟同批走 ★")
            applied.append("ISS-320 verified")
        elif i320:
            applied.append("ISS-320 已是 verified (跳过)")

        # ---------- ② ISS-321 → verified ----------
        i321 = idx.get("ISS-321")
        if i321 and i321.get("status") != "verified":
            i321["status"] = "verified"
            i321["verify_date"] = NOW
            i321["verify_by"] = "main"
            i321["verify_result"] = VERIFY_321
            i321["note"] = (i321.get("note") or "") + (
                f"\n★**{NOW} 11:4x · cron fb67af40 (ARS45 队列自动派活) 落地 verified** ★ "
                "★**独立复核**: 交付页 447 行 + 交卷页 330 行 B0~B7 + 占位符 0/0 + `logs/iss321/` 104 件 + 分片命中 28 + "
                "★**闸链本机实跑回绿 rc=0 (Q1 18/18 · Q7 9/9)** ★ + 板 md5/mtime 逐字节不变 ★ "
                "★**未完项如实留账**: 4 条 need 归 main + 老板 (不代拍) ⇒ 续单 ISS-323 已开并派出 ★")
            applied.append("ISS-321 verified")
        elif i321:
            applied.append("ISS-321 已是 verified (跳过)")

        # ---------- ③ 新开 ISS-323 (sw-lead · status 直接落 fixing) ----------
        if "ISS-323" not in idx:
            issues.append({
                "id": "ISS-323",
                "title": TITLE_323,
                "owner": "sw-lead",
                "status": "fixing",
                "severity": "high",
                "reporter": "main",
                "raised": NOW,
                "due": "2026-11-19",
                "created_at": NOW,
                "dispatched_at": NOW,
                "verify_by": "main",
                "source_blocker": "ISS-321",
                "task_brief": BRIEF_323,
                "note": NOTE_323,
                "need_keys": [
                    "iss321_decide_rename_batch_scope",
                    "iss321_decide_r6_selftest_fixture_after_reboard",
                    "iss321_sw_docs_rename_bulk_24files",
                    "iss321_decide_rename_doc_notation",
                ],
            })
            applied.append("ISS-323 开单 (status=fixing ⇒ 已派)")
        else:
            applied.append("ISS-323 已存在 (跳过)")

        # ---------- ④ 新开 ISS-324 (mech-lead · status 直接落 fixing) ----------
        if "ISS-324" not in idx:
            issues.append({
                "id": "ISS-324",
                "title": TITLE_324,
                "owner": "mech-lead",
                "status": "fixing",
                "severity": "high",
                "reporter": "main",
                "raised": NOW,
                "due": "2026-11-19",
                "created_at": NOW,
                "dispatched_at": NOW,
                "verify_by": "main",
                "source_blocker": "ISS-271",
                "task_brief": BRIEF_324,
                "note": NOTE_324,
                "need_keys": [
                    "iss324_d_led_g_placement_decision",
                    "iss324_led_optical_window_assumption",
                ],
            })
            applied.append("ISS-324 开单 (status=fixing ⇒ 已派)")
        else:
            applied.append("ISS-324 已存在 (跳过)")

        # ---------- ⑤ 落盘 issue_log (原子) ----------
        out = dict(log)
        out["issues"] = issues
        shutil.copy2(LOG, LOG + ".bak_cronfb67_%s_land320321_open323324" % STAMP)
        atomic_write(LOG, yaml.safe_dump(out, allow_unicode=True, sort_keys=False, width=100000))

        # ---------- ⑥ dispatch_log ----------
        dl = yaml.safe_load(open(DL, encoding="utf-8")) or {}
        disp = dl.get("dispatches") or []
        for iid, agent, note in (("ISS-323", "sw-lead", NOTE_323), ("ISS-324", "mech-lead", NOTE_324)):
            if not any(isinstance(d, dict) and d.get("issue") == iid for d in disp):
                disp.append({
                    "issue": iid,
                    "agent": agent,
                    "at": NOW,
                    "brief": note,
                    "job": ("cron fb67af40 (ARS45 队列自动派活) · ★派活时刻 2026-11-18 11:4x · "
                            "★**status 全程 fixing ⇒ 无 open 窗口 ⇒ 兄弟 job 775d9893 不会重复派** ★"),
                })
                applied.append("dispatch_log 追加 %s" % iid)
        dl["dispatches"] = disp
        shutil.copy2(DL, DL + ".bak_cronfb67_%s_land320321_open323324" % STAMP)
        atomic_write(DL, yaml.safe_dump(dl, allow_unicode=True, sort_keys=False, width=100000))

        for a in applied:
            print("· %s" % a)
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
