#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★ISS-319 落地 (fixing → verified) + ISS-317 / ISS-318 续做重派 cont1 (status 保持 fixing) + 新开 ISS-320 (mech-lead · status 直接落 fixing = 立即派出)
   · cron fb67af40 (ARS45 队列自动派活) · 2026-11-18 09:1x★

★**本脚本只做四件事 (★全部原子: flock + 锁内重读 + tmp + fsync + os.replace★)**:
  ① issue_log.yaml: ISS-319 的 status → verified + verify_result / verify_date + note 追加
  ② issue_log.yaml: ISS-317 / ISS-318 的 task_brief 追加 cont1 续做说明 (★原 brief 全文保留, 不删一个字★)
                     + note 追加本轮事实 + status 走一遍 open → fixing (★同一把锁内完成 ⇒ 不留 open 窗口★)
  ③ issue_log.yaml: ★**新开 ISS-320 (owner=mech-lead · status 直接落 fixing = 本轮立即派出)** ★
  ④ dispatch_log.yaml: 追加 6 条登记 (3 条落地/续做 + 3 条派出) · 不碰任何别的文件 (不碰板 · 不碰 HW/ MECH/ SW/ 的任何工程文件)

★**为什么有本脚本 (★main 09:1x 本机实读, 不抄任何 agent 报告★)**:
  · `state/advance.py --json` ⇒ internal=[] · approvals=[] · waiting=[] · decisions=39 ⇒ 看起来队列排空
  · ★**但队列是【死锁】不是【真空】**: `state/issue_log.yaml` 实读 315 条 ⇒ ISS-317(hw-lead) / ISS-318(sw-lead) / ISS-319(mech-lead) 三条 fixing
    ⇒ advance.py 的 in_flight 规则 (源码 L60-64) ⇒ 三个总工各被自己那条 fixing 压住 ⇒ internal 永远是 []
  · ★**三个子会话全部已死 (★sessions_list + transcript 尾逐字实读★)**:
    · ISS-317 ⇒ `agent:hw-lead:subagent:6d3d6815` 08:39:03 起 · 08:49:57 死 · status=timeout · abortedLastRun=true · runtimeMs=651204
    · ISS-318 ⇒ `agent:sw-lead:subagent:9a69ba4d` 08:39:23 起 · 08:56:05 死 · status=failed (末尾 toolResult = 「Aborted」) · runtimeMs=1001857
    · ISS-319 ⇒ `agent:mech-lead:subagent:3648fe86` 08:39:41 起 · 08:49:56 死 · status=timeout · abortedLastRun=true · runtimeMs=612715
    ⇒ ★**根因 = 父 cron run 结束时子会话被连带 abort (★与 ISS-308 / ISS-309 同一个死法★) ⇒ 不是三个总工的错** ★
    ⇒ ★**`subagents list` 实读 total=0 · active=[] ⇒ 三个总工现在全空闲** ★
  · ★**main 09:1x 本机独立复核 (★不抄任何 agent 报告★)**:
      ISS-319: MECH 侧 7 道闸 **全 rc=0** (board_frame_feasibility / check_onepass_mech_sync / check_onepass_struct_crosscheck /
               check_onepass_mech_release / check_board_frame_coords / check_mech_verdict_freshness / service_port_check)
               · 交卷页 `HANDOFF/2026-11-18_mech-lead_ISS319_差集归属与电芯订正影响面.md` (90,826 B · **B0~B6 齐全**)
               · `MECH/ONETRIP_MECH_DIFF_OWNERSHIP.md` (93,477 B) · `logs/iss319/` 22 件
               · `state/fragments/mech.yaml` mtime 08:46:20 · status 段已换 ISS-319 交卷摘要 · needs 124 · artifacts 184
               · ★**零写板**: 板 md5 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413` 交卷前后逐字节相同
      ISS-317: ★**交卷页不存在** (`HANDOFF/` 下 ISS317 命中 0) · `state/fragments/hw.yaml` mtime 08:05:34 (仍 ISS-305) ⇒ **0 件交付物落地**
               · ★**但成果在盘上**: `logs/iss317/rename_list_raw.txt` (58,695 B) + `iss317_gen_rename_list.py` (18,666 B)
                 + `iss317_sb_make_t5t6.py` (15,242 B·写到一半) + `01_c1_baseline_full.txt` + `02_bom_export_raw.txt` (★只有 121 B·没跑完★)
               ⇒ ★**按【续做, 不是从零重做】处理** ★
      ISS-318: ★**新闸本体已经合格** (★main 本机实跑★): `SW/tools/check_sw_ref_reachability.py` 裸跑 **rc=0** (「✔ 绿」) · `--selftest` **rc=0 (7/7)**
               (含 RC-2/RC-3 改名漂移反向用例 + RC-4/RC-5 fail-closed + RC-6/RC-7 正向对照)
               · 挂链前体检 `logs/iss318/healthcheck_with_tmpdir.txt` ⇒ ★**三道 selftest 闸必须【不带 --selftest】裸跑 (带了 rc=2 usage 错误)★**
               · R3 基线 `logs/iss318/r3_baseline_table.md` ⇒ 40 份 SW/*.md · 107 个唯一标识符 ⇒ 现在只有 **3 条**对不上
               · ★**但交卷页只有 906 B 骨架 (末尾写着「(施工中 · 逐条回填)」) ⇒ sw 分片 mtime 07:51 (仍 ISS-315) ⇒ 没交卷** ★
               ⇒ ★**Q1 齐备率现在被顶住**: gate_check 写「sw-lead 用了【回退】⇒ 最新一份 ISS318 缺块, 按老的 ISS315 计分」 ⇒ ★**补齐交卷页才能回 18/18** ★
  · ★**派活前的命令存在性守卫 (★硬规则★)**: `python3 state/check_brief_commands.py --brief-file <f>` ⇒ 三份新 brief 全 rc=0
"""
from __future__ import annotations

import fcntl
import os
import shutil
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
DL = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
BAK_SUF = ".bak_20261118_0915_cronfb67_land319_cont317_cont318_open320"

TODAY = "2026-11-18"
BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"
BOARD_MTIME = "2026-11-06 07:07:17"

BRIEF_317 = os.path.join(HERE, "dispatch_briefs", "ISS-317_hw_s1_three_side_rename_and_nc_whitelist.md")
BRIEF_317C = os.path.join(HERE, "dispatch_briefs", "ISS-317_hw_s1_three_side_rename_and_nc_whitelist_cont1.md")
BRIEF_318 = os.path.join(HERE, "dispatch_briefs", "ISS-318_sw_ref_reachability_gate_and_hook_audit.md")
BRIEF_318C = os.path.join(HERE, "dispatch_briefs", "ISS-318_sw_ref_reachability_gate_and_hook_audit_cont1.md")
BRIEF_320 = os.path.join(HERE, "dispatch_briefs", "ISS-320_mech_cell_model_rename_apply.md")

ZERO_BOARD = (
    "★**零写板双证**: 板 `HW/PCB/demo_mainboard.kicad_pcb` md5 `611b869e13518c3c023fb178f91a0075` · "
    "mtime `2026-11-06 07:07:17.362193413` 交卷前后逐字节相同 ★"
)


def read_text(p: str) -> str:
    with open(p, encoding="utf-8") as f:
        return f.read()


# ────────────────────────────────────────────────────────────────────────────
# ① ISS-319 落地 (fixing → verified)
# ────────────────────────────────────────────────────────────────────────────
LAND_319 = dict(
    verify_result=(
        "★**PASS (★main 09:1x 本机独立复核, 不抄 agent 报告★)** ★ "
        "★**交付物 (★main 本机实读★)**: `MECH/ONETRIP_MECH_DIFF_OWNERSHIP.md` (93,477 B) + "
        "`HANDOFF/2026-11-18_mech-lead_ISS319_差集归属与电芯订正影响面.md` (90,826 B · ★**B0~B6 齐全**★) + "
        "`logs/iss319/` 22 件 (三支取数脚本 + 47 行全量扫描原始输出 + 26 条逐条归属原始输出 + 9 个脚本常量归属核对 + md5/mtime 前后 + 占位符扫描) + "
        "`state/fragments/mech.yaml` (★mtime 08:46:20 · status 段已换 ISS-319 交卷摘要 · needs 124 · artifacts 184★) ★ "
        "★**本机复跑的 MECH 侧 7 道闸 ⇒ 全 rc=0 (★main 09:1x 实跑★)**: "
        "`MECH/board_frame_feasibility.py` rc=0 · `MECH/check_onepass_mech_sync.py` rc=0 · "
        "`MECH/check_onepass_struct_crosscheck.py` rc=0 · `MECH/check_onepass_mech_release.py` rc=0 · "
        "`MECH/check_board_frame_coords.py` rc=0 · `MECH/check_mech_verdict_freshness.py` rc=0 · `MECH/service_port_check.py` rc=0 ★ "
        "★**它交卷的三条硬结论 (★main 已读过交卷页正文★)**: ① 26 条差集逐条给了 owner + 落表批次 + 验收判据 "
        "(★必须同批 17 / 单独批 9 / 已作废·留证不改 0 · owner = mech-lead 10 / main 9 / hw-lead 5 / boss 2 / sw-lead 0 · 6 条带「必须早于 S1 开工」的前置★) "
        "② ★**电芯型号订正的真实影响面 = 47 行 / 22 个活文件 (★.md 13 文件 35 行 · .py 9 文件 12 行★)**, 其中 36 行可改 + 11 行留证/对照行; "
        "★**36 行可改行的数字指纹逐位相同 ⇒ 「几何与重量结论零变化」是机器判的★** ③ 9 个脚本逐个说清「哪个常量是哪个型号的」"
        "(★`cell_thk/batt_thk` 4.60/23.50/40.50 属于 ICP422339PR ⇒ 脚本算的几何一直是对的, 错的只是它引用的型号名★) "
        "★**并实测更正了 ISS-316 的一处**: `gen_print_pack_revb.py` 只写 4 个 .stl ⇒ 「打印包重出带上新型号」只对 stdout 成立 ⇒ 真正的手工改法在 `MECH/print/MEASURE_CHECKLIST.md` L221 ★ "
        "★**它交 main 的 2 条 need**: `iss316_mech_diff_ownership` + `iss319_cell_model_rename_scope` ⇒ ★**后者已由 main 拍「现在做」并开 ISS-320 接住★** ★ "
        "★**边界核验 (★main 本机实读★)**: " + ZERO_BOARD + " · `state/issue_log.yaml` 未自签 · 零外发 · 不替老板拍板 ★"
    ),
    note=(
        "★**2026-11-18 09:1x · cron fb67af40 (ARS45 队列自动派活) 落地 (fixing → verified) ★** "
        "★**落地依据**: 子会话 `agent:mech-lead:subagent:3648fe86` 于 08:49:56 死 (★status=timeout · abortedLastRun=true · runtimeMs=612715 · "
        "★根因 = 父 cron run 结束时子会话被连带 abort ⇒ 不是 mech-lead 的错★) ⇒ ★**但它的成果已全部落盘** "
        "(★交卷页 90,826 B · B0~B6 齐全 · MECH/ONETRIP_MECH_DIFF_OWNERSHIP.md 93,477 B · logs/iss319/ 22 件 · mech 分片已换 ISS-319★) "
        "⇒ ★**且 main 09:1x 本机独立复跑 MECH 侧 7 道闸全 rc=0 + 零写板双证成立** ⇒ 可以落地 ★ "
        "★**它交 main 拍的 need `iss319_cell_model_rename_scope` ⇒ main 已拍「现在做」⇒ ★**已开 ISS-320 (mech-lead) 接住电芯型号订正的实做** ★ "
        "★**它开的 need `iss316_mech_diff_ownership` 仍开着 (★交 main + 老板拍★)** ★"
    ),
)

# ────────────────────────────────────────────────────────────────────────────
# ② ISS-317 / ISS-318 续做重派 cont1 (status 全程 fixing ⇒ 不留 open 窗口)
# ────────────────────────────────────────────────────────────────────────────
CONT_317 = dict(
    cont_file=BRIEF_317C,
    note=(
        "★**2026-11-18 09:1x · cron fb67af40 (ARS45 队列自动派活) 僵尸 fixing 续做重派 cont1 (★不是从零重做★)** ★ "
        "★**上一趟子会话**: `agent:hw-lead:subagent:6d3d6815` (taskName `queue_iss317`) 08:39:03 起 · 08:49:57 死 · "
        "runtimeMs=651204 · status=timeout · abortedLastRun=true ⇒ ★**根因 = 父 cron run 结束时子会话被连带 abort "
        "(★与 ISS-308 / ISS-309 同一个死法★) ⇒ 不是 hw-lead 的错** ★ "
        "★**0 件交付物落地** (★main 09:1x 实读★): `HANDOFF/` 下 ISS317 命中 0 · `state/fragments/hw.yaml` mtime 08:05:34 · status 段仍 ISS-305 ⇒ "
        "★**但成果【已经在盘上】**: `logs/iss317/rename_list_raw.txt` (58,695 B · §A 四侧现值盘点 + §B 改名口径分组计数) + "
        "`logs/iss317/iss317_gen_rename_list.py` (18,666 B · 只读口径单源 = `state/gen_kicad_sch.py::kicad_ref()`) + "
        "`logs/iss317/iss317_sb_make_t5t6.py` (15,242 B · ★写到一半·T5 造法待补★) + `logs/iss317/01_c1_baseline_full.txt` (7,130 B) + "
        "`logs/iss317/02_bom_export_raw.txt` (★只有 121 B·几乎肯定没跑完★) ⇒ ⇒ **本轮按【续做, 不是从零重做】处理** ★ "
        "★**★main 09:1x 从 `rename_list_raw.txt` 实读出的关键数字 (★已写进 cont1 任务书, 仍要 hw-lead 独立复核★)**: "
        "脚表 218 ref / 网表 ref 列 291 (含伪器件 75) / BOM 218 / 原理图 218 / 板侧 186 封装 ⇒ "
        "★**「要改 186 / 不动 32」是表侧口径 (ISS-314 说的 30 个不动是【板侧】口径) ⇒ ⇒ 「S1 位号改名」要动的是【五侧】"
        "(板 156 + 网表/脚表/BOM/原理图 各 186), 不是三侧 ★** ⇒ ★**且 `J_USB_C` 末字符是字母 ⇒ 它必被改成 `J_USB_C_1` ⇒ "
        "★**即便五侧同口径, 仍撞死 `state/check_pcb_nets.py` 的 NC 白名单 (ISS-314 实测: 非法 NC 3 + C3 红 1)★** ★ "
        "★**cont1 任务书全文**: `state/dispatch_briefs/ISS-317_hw_s1_three_side_rename_and_nc_whitelist_cont1.md` ★"
    ),
)

CONT_318 = dict(
    cont_file=BRIEF_318C,
    note=(
        "★**2026-11-18 09:1x · cron fb67af40 (ARS45 队列自动派活) 僵尸 fixing 续做重派 cont1 (★不是从零重做★)** ★ "
        "★**上一趟子会话**: `agent:sw-lead:subagent:9a69ba4d` (taskName `queue_iss318`) 08:39:23 起 · 08:56:05 死 · "
        "runtimeMs=1001857 · status=failed (末尾两条 toolResult = 「Aborted」) ⇒ ★**根因 = 父 cron run 结束时子会话被连带 abort "
        "(★与 ISS-308 / ISS-309 同一个死法★) ⇒ 不是 sw-lead 的错** ★ "
        "★**★但成果【已经在盘上, 而且新闸本体已经合格】(★main 09:1x 本机实跑, 不是抄 agent 报告★)**: "
        "★**`SW/tools/check_sw_ref_reachability.py` (41,350 B) 裸跑 rc=0 (★判决「✔ 绿: SW 侧引用的位号全部可达, 真隐患在基线内」★) · "
        "`--selftest` rc=0 (★反向用例 7/7★ · 含 RC-2/RC-3 改名漂移 · RC-4/RC-5 fail-closed · RC-6/RC-7 正向对照)★** ⇒ "
        "★**挂链前体检 `logs/iss318/healthcheck_with_tmpdir.txt` ⇒ 三道 selftest 闸【必须不带 --selftest 裸跑】(带了 ⇒ rc=2 usage 错误)★** · "
        "★**R3 基线 `logs/iss318/r3_baseline_table.md` ⇒ 40 份 SW/*.md · 107 个唯一标识符 · 现在只有 3 条位号引用对不上 (= `BASELINE_COUNT` 上限)★** · "
        "★**板那一趟留痕义务 E-0~E-3 实测在 `logs/iss318/probe_landing_trace_board_trip.txt`★** ⇒ "
        "★**⇒ 本轮按【续做, 不是从零重做】处理: 闸本体不重做, 补交卷页 + 挂链逐字写法 + sw 分片** ★ "
        "★**★交卷页没交 (★main 09:1x 实读★)**: `HANDOFF/2026-11-18_sw-lead_ISS318_SW位号引用闸与挂链体检.md` 只有 **906 B** · "
        "末尾写着「(施工中 · 逐条回填)」⇒ ★**而且这张骨架页已经把 Q1 齐备率顶住了**: gate_check 现在写「sw-lead 用了【回退】⇒ "
        "最新一份 ISS318 缺块, 按老的 ISS315 计分」⇒ ★**补齐 B0~B6 才能回 18/18** ★ · `state/fragments/sw.yaml` mtime 07:51:05 (仍 ISS-315) ★ "
        "★**cont1 任务书全文**: `state/dispatch_briefs/ISS-318_sw_ref_reachability_gate_and_hook_audit_cont1.md` ★"
    ),
)

# ────────────────────────────────────────────────────────────────────────────
# ③ 新开 ISS-320 (mech-lead · status 直接落 fixing = 本轮立即派出)
# ────────────────────────────────────────────────────────────────────────────
ISS320 = dict(
    id="ISS-320",
    title=(
        "★★[主线内·MECH 侧·受限文本订正类·内部活] ★★【电芯型号订正【实做】: 把 ISS-319 查清的那 47 行里的 33 行"
        "【真改掉】(MECH 域 19 个文件·含 9 个脚本) —— 只把 `ICP582035PR-01` 替换成 `ICP422339PR`, "
        "★**一个尺寸/重量/容量常量都不许动** · 11 行留证/对照行一行都不许碰 ★**】★★ "
        "⇒ ★**受限文本订正类 · 零写板 · 零落表 · 零重生成 · 零改闸 · 零外发 · 不替老板拍板** ★ "
        "⇒ ★**为什么现在做 (★main 已拍★)**: 照现型号采购 ⇒ 到货厚 6.40mm (不是 4.60) ⇒ 装不进 7.30mm 镜脚 ⇒ "
        "电芯段 H 链最坏 −1.10mm ⇒ ★**这笔比文档订正本身更贵, 且与 U-1 板框决策完全无关 ⇒ 可并行走, 越早越省钱**★"
    ),
    severity="high",
    owner="mech-lead",
    reporter="main",
    raised=TODAY,
    due="2026-11-19",
    status="fixing",
    external=False,
    need_keys=[],
    fix_ref=None,
    verify_by="main",
    verify_result=None,
    verify_date=None,
    dispatched_at=TODAY,
    note=(
        "★**2026-11-18 09:1x · cron fb67af40 (ARS45 队列自动派活) 新开并直接派出 (status=fixing ⇒ 下一轮 in_flight 规则会跳过 mech-lead ⇒ "
        "窗口消失 ⇒ 不与兄弟 job 775d9893 撞车)** ★ "
        "★**开单依据 (★main 09:1x 本机实读·不抄任何 agent 报告★)**: ★**① ISS-319 (verified · 本轮刚落地) 把影响面查清了** ⇒ "
        "全量扫描 = 47 行 / 22 个活文件 (★.md 13 文件 35 行 · .py 9 文件 12 行★) ⇒ 其中 36 行「可改行」+ 11 行「留证/对照行」⇒ "
        "★**36 行可改行的数字指纹逐位相同 ⇒ 「几何与重量结论零变化」是机器判的** ★ "
        "★**② main 已拍 ISS-319 交上来的 need `iss319_cell_model_rename_scope` = 【现在做】(★理由: 照现型号 `ICP582035PR-01` 下采购单 ⇒ "
        "到货厚 6.40mm ⇒ 装不进 7.30mm 镜脚 ⇒ H 链最坏 −1.10mm ⇒ 这笔损失远大于任何文档订正本身★) ★ "
        "★**③ 归属切分**: HW 域那 3 行 (`HW/POWER_BUDGET_V3.md` L27/L259 · `HW/NETLIST_SELF_CONSISTENCY_SPEC.md` L1046) ★**由 main 自己改** "
        "(★main 09:1x 本机实读: 这两个文件没有被任何 md5 闸钉住·可安全改★) ⇒ ★**本单 = MECH 域 33 行 / 19 个 MECH 文件**★ ★ "
        "★**④ 官网读数 (★`[官网]`·renata.com 锂聚合物电池页·零外发★)**: `ICP422339PR` = 340 mAh / 4.6mm / 23.5 / 40.5 (★真型号·项目一直按它的尺寸在算★) · "
        "`ICP582035PR-01` = 340 mAh / **6.4**mm / 20.5 / 37 (★项目把 4.6×23.5×40.5 错挂在它名下★) ★ "
        "★**任务书全文**: `state/dispatch_briefs/ISS-320_mech_cell_model_rename_apply.md` ★ "
        "★**边界**: 零写板 · 零落表 · 零重生成 (★不许跑 `MECH/print/gen_print_pack_revb.py` / `verify_pack_revb.py` / 任何 `state/gen_*.py`★) · "
        "零改闸 · ★**只许改那 33 行, 其余一个字都不许动 (★特别是 11 行留证行★)★** · ★**不许改任何尺寸/重量/容量常量**★ · "
        "★**HW 域那 3 行不许碰 (★那是 main 的活★)★** · 零外发 · 不替老板拍板 · 不自签 issue_log ★"
    ),
)


def atomic_write(path: str, data) -> None:
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_", suffix=".yaml")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False, width=10 ** 6)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def main() -> int:
    os.makedirs(HERE, exist_ok=True)
    with open(LOCK, "a", encoding="utf-8") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        log = yaml.safe_load(open(LOG, encoding="utf-8"))
        dl = yaml.safe_load(open(DL, encoding="utf-8"))

        by_id = {i.get("id"): i for i in log["issues"]}
        out = []
        notes = []

        # ── ① ISS-319 落地 ──────────────────────────────────────────────
        it = by_id["ISS-319"]
        if it.get("status") == "fixing":
            it["status"] = "verified"
            it["verify_result"] = LAND_319["verify_result"]
            it["verify_date"] = TODAY
            it["note"] = (it.get("note") or "") + " " + LAND_319["note"]
            notes.append("ISS-319 fixing → verified")
        else:
            notes.append("★ISS-319 已是 %s ⇒ 不重复落地★" % it.get("status"))

        # ── ② ISS-317 / ISS-318 续做 (open → fixing 同一把锁内完成) ──────
        for iid, spec, orig_file in (("ISS-317", CONT_317, BRIEF_317),
                                     ("ISS-318", CONT_318, BRIEF_318)):
            it = by_id[iid]
            orig = it.get("task_brief") or read_text(orig_file)
            cont = read_text(spec["cont_file"])
            if "cont1 续做说明" not in orig:
                it["task_brief"] = orig + "\n\n---\n\n" + cont
                it["note"] = (it.get("note") or "") + " " + spec["note"]
                it["dispatched_at"] = TODAY
                notes.append("%s task_brief += cont1 (★原 brief 全文保留★) · status 走 open→fixing" % iid)
            else:
                notes.append("★%s task_brief 已含 cont1 ⇒ 不重复追加★" % iid)
            it["status"] = "fixing"   # ★全程 fixing ⇒ 不留 open 窗口★

        # ── ③ 新开 ISS-320 (status 直接落 fixing = 立即派出) ─────────────
        if "ISS-320" not in by_id:
            rec = dict(ISS320)
            rec["task_brief"] = read_text(BRIEF_320)
            log["issues"].append(rec)
            notes.append("ISS-320 新开 (owner=mech-lead · status=fixing · 立即派出)")
        else:
            notes.append("★ISS-320 已存在 ⇒ 不重复开单★")

        # ── ④ dispatch_log 登记 ────────────────────────────────────────
        disp = dl.setdefault("dispatches", [])
        ents = dl.setdefault("entries", [])
        reg = [
            dict(issue="ISS-319", agent="mech-lead", at=TODAY,
                 brief="★**落地 (fixing → verified)** ★ ★**依据**: 子会话 08:49:56 被父 run 连带 abort, 但成果已全落盘 (★交卷页 90,826 B · B0~B6 · MECH/ONETRIP_MECH_DIFF_OWNERSHIP.md 93,477 B · logs/iss319/ 22 件 · mech 分片已换★) + ★**main 09:1x 本机复跑 MECH 侧 7 道闸全 rc=0 + 零写板双证成立★** ★ **它的 need `iss319_cell_model_rename_scope` ⇒ main 已拍「现在做」⇒ 已开 ISS-320 接住** ★",
                 job="cron fb67af40 (ARS45 队列自动派活) · ★派活时刻 2026-11-18 09:1x ★"),
            dict(issue="ISS-317", agent="hw-lead", at=TODAY,
                 brief="★**僵尸 fixing 续做重派 cont1 (★不是从零重做★)** ★ 上一趟 `agent:hw-lead:subagent:6d3d6815` 08:49:57 死 (★timeout · abortedLastRun · 根因 = 父 run 连带 abort★) ⇒ 0 件交卷落地, ★**但 `logs/iss317/` 5 件在盘上 (含 58,695 B 的逐条改名清单 + 两支脚本)★** ⇒ 本轮只补: T5/T6 沙盒实跑 · 五侧逐条改名对照表 · NC 白名单三选项的沙盒读数 · BOM 证据回填判据 · ISS-314 的 5 条未验 · 交卷页 B0~B6 + hw 分片 ★ **cont1 任务书**: `state/dispatch_briefs/ISS-317_hw_s1_three_side_rename_and_nc_whitelist_cont1.md` ★",
                 job="cron fb67af40 (ARS45 队列自动派活) · ★status 全程 fixing ⇒ 无 open 窗口 ⇒ 兄弟 job 775d9893 不会重复派** ★"),
            dict(issue="ISS-318", agent="sw-lead", at=TODAY,
                 brief="★**僵尸 fixing 续做重派 cont1 (★不是从零重做★)** ★ 上一趟 `agent:sw-lead:subagent:9a69ba4d` 08:56:05 死 (★failed · Aborted · 根因 = 父 run 连带 abort★) ⇒ ★**但新闸本体已经合格 (★main 09:1x 本机实跑: 裸跑 rc=0 · --selftest 7/7★) + 挂链前体检 + R3 基线都在盘上** ⇒ 本轮只补: 交卷页从 906 B 骨架补成 B0~B6 (★现在 Q1 被这张骨架页顶住·gate_check 写「sw-lead 用了回退」★) + 挂链逐字写法 (★三道 selftest 闸必须裸跑·带 --selftest 会 rc=2★) + md5 前后 + 占位符扫描 + sw 分片 ★ **cont1 任务书**: `state/dispatch_briefs/ISS-318_sw_ref_reachability_gate_and_hook_audit_cont1.md` ★",
                 job="cron fb67af40 (ARS45 队列自动派活) · ★status 全程 fixing ⇒ 无 open 窗口 ⇒ 兄弟 job 775d9893 不会重复派** ★"),
            dict(issue="ISS-320", agent="mech-lead", at=TODAY,
                 brief="★**新开单 + 直接派出 (status 直接落 fixing)** ★ ★**2026-11-18 09:1x · cron fb67af40 (ARS45 队列自动派活)** ★ ★**开单依据**: ★**① ISS-319 (verified·本轮刚落地) 查清影响面 = 47 行 / 22 个活文件 (36 行可改 + 11 行留证)·数字指纹逐位相同⇒几何与重量结论零变化** ★ ★**② main 已拍 ISS-319 的 need `iss319_cell_model_rename_scope` = 现在做 (★照现型号采购 ⇒ 厚 6.40mm ⇒ 装不进 7.30mm 镜脚 ⇒ H 链最坏 −1.10mm★)** ★ ★**③ 归属切分: HW 域 3 行归 main · MECH 域 33 行 / 19 个文件归本单** ★ ★**任务书全文**: `state/dispatch_briefs/ISS-320_mech_cell_model_rename_apply.md` ★ ★**边界**: 零写板 · 零落表 · 零重生成 · 零改闸 · 只许改那 33 行 (★11 行留证行一行都不许碰★) · 不许改任何尺寸/重量/容量常量 · 零外发 · 不替老板拍板 · 不自签 issue_log ★",
                 job="cron fb67af40 (ARS45 队列自动派活) · ★status 全程 fixing ⇒ 无 open 窗口 ⇒ 兄弟 job 775d9893 不会重复派** ★"),
        ]
        disp.extend(reg)
        ents.extend(reg)

        shutil.copy2(LOG, LOG + BAK_SUF)
        shutil.copy2(DL, DL + BAK_SUF)
        atomic_write(LOG, log)
        atomic_write(DL, dl)
        print("=== apply done ===")
        for n in notes:
            print("  -", n)
        print("=== dispatches=%d entries=%d issues=%d ===" % (len(disp), len(ents), len(log["issues"])))
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
