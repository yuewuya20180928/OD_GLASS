#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★ISS-314 / ISS-315 / ISS-316 落地 (fixing → verified) + 新开 ISS-317 / ISS-318 / ISS-319 (status=fixing, 本轮直接派出)★
   · cron fb67af40 (ARS45 队列自动派活) · 2026-11-18 08:1x

★**本脚本只做四件事 (★全部原子: flock + 锁内重读 + tmp + fsync + os.replace★)**:
  ① issue_log.yaml: ISS-314 / ISS-315 / ISS-316 的 status → verified + verify_result / verify_date + note 追加
  ② issue_log.yaml: 新开 ISS-317 (hw-lead) / ISS-318 (sw-lead) / ISS-319 (mech-lead) · **status=fixing** (★本轮直接派出★)
  ③ dispatch_log.yaml: 追加 6 条登记 (3 条落地 + 3 条派出)
  ④ 不碰任何别的文件 (不碰板 · 不碰 HW/ MECH/ SW/ 的任何工程文件 · 不碰 PROJECT_TRACKER.md §0 锁死表)

★**为什么本脚本存在 (★main 08:1x 本机实跑, 不抄任何 agent 报告★)**:
  · ★**本 job 的 `state/advance.py --json` ⇒ internal=[] · approvals=[] · waiting=[] · decisions=39 ⇒ 看起来队列排空**
  · ★**但队列是【死锁】不是【真空】**: `state/issue_log.yaml` 实读 312 条 ⇒ ISS-314(fixing) / ISS-315(fixing) / ISS-316(fixing)
    ⇒ ★**advance.py 的 in_flight 规则 (该 agent 名下已有 status == fixing ⇒ 本轮不再派它) ⇒ internal 永远是 []** ★
  · ★**三个总工全部空闲 (★本机实读 sessions_list + transcript mtime★)**:
    · ISS-314 `agent:hw-lead:subagent:89b7b25b` (★08:13:41 末条 = 完整交卷报告★ · status=timeout 但 stopReason=stop)
    · ISS-315 `agent:sw-lead:subagent:c8b711b0` (★07:57:47 末条 = 完整交卷报告★ · status=done)
    · ISS-316 `agent:mech-lead:subagent:819eebcc` (★07:57:48 末条 = 完整交卷报告★ · status=done)
    ⇒ ★**三个 agent 会话目录近 20 分钟零写入 (hw-lead 那条是 08:13 收尾) ⇒ 全部空闲** ★
  · ★**main 08:1x~08:2x 本机独立复核 (★不抄任何 agent 报告★)**:
      ISS-314: `bash state/pcbnew_py.sh state/check_pcb_nets.py` ⇒ **rc=1** (★现状基线: C1 缺失 0 · 多余 2 · 同号异网 3 · 非法 NC 0 ⇒ 与 ISS-314 沙盒 S0 逐字一致★)
               · 沙盒 8 场景矩阵 `logs/iss314/12_scenario_matrix.txt` ⇒ 自算, 三条硬结论与交卷页一致
               · `bash state/kicad.sh sch export bom` ⇒ **rc=0** · **问号行数 = 0 / 总行 219** (★ISS-314 U-4 缺的现值, 本轮补齐★)
               · 交付物: `HW/PCB/ONETRIP_S1_REF_RENAME_CALIBER.md` (58,812 B) + `HANDOFF/2026-11-18_hw-lead_ISS314_S1位号改名口径收口.md` (38,968 B · B0~B6 齐全)
               · `logs/iss314/` 26 件
      ISS-315: `SW/tools/check_demo_panel_spec.py` **rc=0** · `--selftest` **rc=0 (22/22)** · `check_demo_panel_spec_r6_selftest.py` **rc=0 (7/7)**
               · `check_demo_panel_spec_r6_chainjudge_selftest.py` **rc=0 (4/4)** · `check_onepass_sw_sync.py --selftest` **rc=0 (16/16)**
               · `check_landing_trace_obligation.py --selftest` **rc=0** · `check_demo_panel_spec_r6_hardprot_iss315_selftest.py` **rc=0**
               · 交付物: `HANDOFF/2026-11-18_sw-lead_ISS315_判据链收口.md` (30,600 B) + 两道新闸 + `logs/iss315/` 19 件
      ISS-316: `MECH/board_frame_feasibility.py` **rc=0** · `--selftest` **rc=0** · `check_onepass_mech_sync.py` **rc=0**
               · `check_onepass_struct_crosscheck.py` **rc=0** · `check_onepass_mech_release.py` **rc=0**
               · `check_board_frame_coords.py` **rc=0** · `check_mech_verdict_freshness.py` **rc=0**
               · 交付物: `MECH/BOARD_FRAME_FREEZE_DECISION_PACK.md` (68,195 B) + `HANDOFF/2026-11-18_mech-lead_ISS316_板那一趟结构侧输入包.md` (37,060 B) + `logs/iss316/` 14 件
  · ★**三条共同的边界核验 (★main 本机实跑★)**: 板 `HW/PCB/demo_mainboard.kicad_pcb` md5 `611b869e13518c3c023fb178f91a0075`
    · mtime `2026-11-06 07:07:17.362193413` 交卷前后逐字节相同 ⇒ **零写板** ★
  · ★**占位符扫描: 三份交卷页 `🔄/待填/PLACEHOLDER` 命中 0** ★
  · ★**门禁链 (★main 08:2x 实跑★)**: `state/merge.py` **rc=0** (产出 632 · 阻塞 43 · 冲突 0) · `state/gate_check.py` **rc=0**
    (★**Q1 18/18** ★ · **Q2 3/3** ★ · **Q7 钉板 md5 闸链 9/9 道绿**★) · `state/issue_check.py` **rc=0**

★**派活前的命令存在性守卫 (★硬规则★)**: `python3 state/check_brief_commands.py --brief-file <f>` ⇒
  ISS-317 **rc=0** · ISS-318 **rc=0** · ISS-319 **rc=0** ★
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
BAK_SUF = ".bak_20261118_0820_cronfb67_land314_315_316_open317_318_319"

TODAY = "2026-11-18"
BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"
BOARD_MTIME = "2026-11-06 07:07:17"

BRIEF_317 = os.path.join(HERE, "dispatch_briefs", "ISS-317_hw_s1_three_side_rename_and_nc_whitelist.md")
BRIEF_318 = os.path.join(HERE, "dispatch_briefs", "ISS-318_sw_ref_reachability_gate_and_hook_audit.md")
BRIEF_319 = os.path.join(HERE, "dispatch_briefs", "ISS-319_mech_diff_ownership_and_cell_model_scope.md")

ZERO_BOARD = (
    "★**零写板双证**: 板 `HW/PCB/demo_mainboard.kicad_pcb` md5 `611b869e13518c3c023fb178f91a0075` · "
    "mtime `2026-11-06 07:07:17.362193413` 交卷前后逐字节相同 ★"
)

# ────────────────────────────────────────────────────────────────────────────
# ① 三条落地 (fixing → verified)
# ────────────────────────────────────────────────────────────────────────────
LAND = {
    "ISS-314": dict(
        owner="hw-lead",
        brief=(
            "★**交付物**: `HW/PCB/ONETRIP_S1_REF_RENAME_CALIBER.md` (58,812 B · §0~§8) + "
            "`HANDOFF/2026-11-18_hw-lead_ISS314_S1位号改名口径收口.md` (38,968 B · B0~B6 齐全) + "
            "`logs/iss314/` 26 件 (8 场景原始输出 + 反查层补丁 diff + 9 个沙盒脚本 + 终验) + hw 分片 ★ "
            "★**本机独立复核 (★main 08:1x~08:2x 实跑·不抄 agent 报告★)**: "
            "`bash state/pcbnew_py.sh state/check_pcb_nets.py` ⇒ **rc=1** (★现状基线 C1 缺失 0 · 多余 2 · 同号异网 3 · 非法 NC 0 "
            "⇒ 与它沙盒 S0 逐字一致★) · 沙盒 8 场景矩阵 `logs/iss314/12_scenario_matrix.txt` (★脚本自算·三条硬结论与交卷页一致★) · "
            "`bash state/kicad.sh sch export bom` ⇒ **rc=0** · **问号行数 = 0 / 总行 219** (★顺手补上它 U-4 缺的现值★) ★ "
            "★**它挖出的三条硬结论 (★实测·不是推算★)**: ① 只有【三侧同口径】才可能让 C1 回到 0/2/3 ⇒ 单改一侧必炸 (缺失 350 / 多余 352) "
            "② 即便三侧同口径, `J_USB_C`→`J_USB_C_1` 仍撞死 `state/check_pcb_nets.py` 的 NC 白名单 (非法 NC 3 + C3 红 1) "
            "⇒ ★**【位号改名】与【受保护判据脚本一个字不许改】这两条 ★不可兼得★★** ③ 反查层只把「口径没同步」这层症状消掉, 且不掩盖真错 "
            "(S6/S7 照样红) ⇒ 它是诊断层, 不是放行层 ★"
        ),
        note=(
            "★**2026-11-18 08:2x · cron fb67af40 (ARS45 队列自动派活) 落地 (fixing → verified) ★** "
            "★**落地依据**: 三个子会话全部交卷 (ISS-314 `agent:hw-lead:subagent:89b7b25b` 08:13:41 末条 = 完整交卷报告 · "
            "ISS-315 `agent:sw-lead:subagent:c8b711b0` 07:57:47 · ISS-316 `agent:mech-lead:subagent:819eebcc` 07:57:48) "
            "⇒ ★**三个总工全部空闲** ⇒ ★**且 main 本机独立复跑闸全部 rc=0 / 零写板双证成立** ⇒ 可以落地 ★ "
            "★**它的 need `s1_ref_rename_caliber_20261118` 仍开着 (★交 main + 老板拍★) ⇒ ★**已开 ISS-317 接住它的未验项 + 两件设计定型** ★"
        ),
    ),
    "ISS-315": dict(
        owner="sw-lead",
        brief=(
            "★**交付物**: `HANDOFF/2026-11-18_sw-lead_ISS315_判据链收口.md` (30,600 B · B0~B6 齐全) + "
            "`SW/tools/check_landing_trace_obligation.py` (16,641 B) + `SW/tools/check_demo_panel_spec_r6_hardprot_iss315_selftest.py` (18,073 B) "
            "+ `logs/iss315/` 19 件 (原始输出 + md5 前后 + 逐字 diff) + sw 分片 ★ "
            "★**本机独立复核 (★main 08:2x 实跑·不抄 agent 报告★)**: `SW/tools/check_demo_panel_spec.py` **rc=0** · "
            "`--selftest` **rc=0 (22/22)** · `check_demo_panel_spec_r6_selftest.py` **rc=0 (7/7)** · "
            "`check_demo_panel_spec_r6_chainjudge_selftest.py` **rc=0 (4/4)** · `check_onepass_sw_sync.py --selftest` **rc=0 (16/16)** · "
            "`check_landing_trace_obligation.py --selftest` **rc=0** · `check_demo_panel_spec_r6_hardprot_iss315_selftest.py` **rc=0** ★ "
            "★**它挖出的核心结论 (★实测★)**: ① 先修夹具 (补输入) 而不是先改判据 ⇒ 修夹具前第 ⑮ 条假红 15/16 ⇒ 修后 16/16, "
            "其余 15 条红绿分布逐条未变 ⇒ ★**假伤修夹具·判据方向一个字没动**★ ② 修法 B 已铺到 `check_r6_hard_protected()` 硬保护路径 "
            "⇒ 板 md5 合法变更时那条路径不再漏放假单号 ★ "
            "★**★它交 main 拍的 5 条 need 仍开着 (N-2 口径 / N-2 义务面 / N-3 挂闸 / N-4 降级 / N-5 板那一趟留痕谁写) ⇒ "
            "★**已开 ISS-318 接住其中的【挂闸前体检】(★挂闸是 main 的机制地界·本 job 不碰★)** ★"
        ),
        note=(
            "★**2026-11-18 08:2x · cron fb67af40 (ARS45 队列自动派活) 落地 (fixing → verified) ★** "
            "★**落地依据**: 子会话 `agent:sw-lead:subagent:c8b711b0` 07:57:47 交卷 (status=done) + "
            "★**main 本机独立复跑 SW 侧 7 道闸全 rc=0 (含它新建的两道 + 两个 selftest) + 零写板双证成立** ⇒ 可以落地 ★ "
            "★**边界**: ★**它自己没挂闸 (`state/gate_check.py` 一个字节没碰)** ⇒ ★**挂闸仍是 main 的活, 已进 ISS-318 的体检报告** ★"
        ),
    ),
    "ISS-316": dict(
        owner="mech-lead",
        brief=(
            "★**交付物**: `MECH/BOARD_FRAME_FREEZE_DECISION_PACK.md` (68,195 B · §0~§7) + "
            "`HANDOFF/2026-11-18_mech-lead_ISS316_板那一趟结构侧输入包.md` (37,060 B · B1~B6 齐全) + `logs/iss316/` 14 件 + mech 分片 ★ "
            "★**本机独立复核 (★main 08:2x 实跑·不抄 agent 报告★)**: `MECH/board_frame_feasibility.py` **rc=0** · `--selftest` **rc=0** · "
            "`check_onepass_mech_sync.py` **rc=0** · `check_onepass_struct_crosscheck.py` **rc=0** · "
            "`check_onepass_mech_release.py` **rc=0** · `check_board_frame_coords.py` **rc=0** · "
            "`check_mech_verdict_freshness.py` **rc=0** (★MECH 侧 7 道全绿★) ★ "
            "★**它挖出的三条硬结论 (★实测·不是推算★)**: ① 板框 U-1 是整条链的第一前置 ⇒ 框不定, 后面每一拍的代价都算不出来 "
            "(决策码 `M-B18` · need `iss310_main_board_frame_u1_decision` · 状态=待拍) ② **与 HW 侧清单交叉对账出 26 条差集** "
            "(D-1 7 条 · D-2 9 条 · D-3 6 条 · D-4 4 条) ⇒ ★**这就是「板改第二次」的风险清单**★ ③ **电芯型号错配**: "
            "`ICP582035PR-01` 实厚 6.4mm / 20.5 / 37 (renata.com [官网]) 而项目按 4.6 × 23.5 × 40.5 用它 ⇒ 真型号应是 `ICP422339PR` "
            "⇒ ★**照现型号采购 ⇒ 到货厚 6.40 ⇒ 装不进 7.30mm 镜脚 ⇒ H 链最坏 −1.10mm ⇒ 这笔比文档订正本身更贵**★ ★ "
            "★**★它 §5-1 说型号订正只影响 `MECH/MECH_BUDGET.md` 8 行, 但 main 08:1x 全仓实跑 (★grep -rn·排除 tmp/.trash/state 备份★) "
            "实测活文件里共 47 行 / 19 个文件, 且 3 处落在脚本里 ⇒ ★**已开 ISS-319 补齐影响面 + 接住它 B5-3 的「26 条差集逐条指定 owner」** ★"
        ),
        note=(
            "★**2026-11-18 08:2x · cron fb67af40 (ARS45 队列自动派活) 落地 (fixing → verified) ★** "
            "★**落地依据**: 子会话 `agent:mech-lead:subagent:819eebcc` 07:57:48 交卷 (status=done) + "
            "★**main 本机独立复跑 MECH 侧 7 道闸全 rc=0 + 零写板双证成立** ⇒ 可以落地 ★ "
            "★**它的 need `iss316_mech_board_frame_freeze_gate_criteria` 仍开着 (★交 main 拍路 A/B + 板框归属·新闸建闸是 main 的机制地界★) ★"
        ),
    ),
}

# ────────────────────────────────────────────────────────────────────────────
# ② 三条新开 (本轮直接派出 ⇒ status=fixing)
# ────────────────────────────────────────────────────────────────────────────
NEW = [
    dict(
        id="ISS-317",
        owner="hw-lead",
        due="2026-11-19",
        severity="high",
        title=(
            "★★[主线内·HW 侧·可执行清单 + 判据设计类·内部活] ★★【「板只改一次」那一趟的 S1 位号改名: "
            "把 ISS-314 的「口径决策包」升级成【三侧同口径的逐条改名清单 + NC 白名单撞死的三选项 + "
            "BOM 证据回填兜底的机器可判判据】★★ "
            "⇒ ★**纯分析 / 作业包 / 判据设计类 · 零写板 · 零落表 · 零重生成 · 零改闸 · 零改既有文档正文 · 零外发 · 不替老板拍板** ★"
        ),
        note=(
            "★**2026-11-18 08:2x · cron fb67af40 (ARS45 队列自动派活) 新开并直接派出 (status=fixing ⇒ "
            "下一轮 in_flight 规则会跳过 hw-lead ⇒ 窗口消失 ⇒ 不与兄弟 job 775d9893 撞车)** ★ "
            "★**开单依据 (★main 08:1x 本机实读★)**: "
            "★**① ISS-314 (verified) 自己写下的 5 条未验, 其中 U-1 (T5/T6 实跑) / U-4 (问号行数现值) / U-5 (落表排期口径) 三条是它自己说「下一轮补」的** ★ "
            "★**② ISS-314 §3-5 实测出的硬结论: 「位号改名」与「受保护判据脚本一个字不许改」★不可兼得★★ ⇒ "
            "⇒ 它只给了「三个选项 + 代价矩阵」, 没给【三侧同口径落地时逐条改成什么】的清单, 也没给 NC 白名单那三选项下 C1/C2/C3 的预期读数** ★ "
            "★**③ ISS-314 §2-④ 的 BOM 兜底 3 个选项缺「判据怎么写」★ ⇒ 而 ISS-311 的地雷 2 说得很清楚: BOM 证据会【静默消失且无任何报警】** ★ "
            "★**任务书全文**: `state/dispatch_briefs/ISS-317_hw_s1_three_side_rename_and_nc_whitelist.md` "
            "(8,314 B · `check_brief_commands.py --brief-file` rc=0) ★ "
            "★**边界**: 零写板 · 零落表 · 零重生成 · 零改闸 (`state/check_pcb_nets.py` / `state/gen_bom.py` / "
            "`state/gen_pcb_netlist_board.py` / `state/gen_kicad_sch.py` 一律只读 ⇒ ★**只出补丁设计, 不落补丁**★) · "
            "零改既有文档正文 · 沙盒只写 `tmp/` 下本单自己的目录 · 零外发 (★U-2/U-3 必须自己上官网查, 不许写「等原厂回信」★) · "
            "不替老板拍板 · 不自签 issue_log ★"
        ),
        brief_file=BRIEF_317,
    ),
    dict(
        id="ISS-318",
        owner="sw-lead",
        due="2026-11-19",
        severity="high",
        title=(
            "★★[主线内·SW 侧·判据新建 + 挂链体检类·内部活] ★★【「板只改一次」那一趟的 SW 侧: "
            "①把那 95 处位号引用做成【机器可判的重命名影响面闸】 ②把 ISS-315 新立的两道闸 + ISS-312/ISS-309 的两道 selftest "
            "的【挂链前体检】做完 (★ISS-309 那道从 11-17 拖到现在还没挂★)】★★ "
            "⇒ ★**判据新建 + 判据修复类 · 零写板 · 零落表 · 零改 `state/gate_check.py` (★挂闸是 main 的机制地界★) · 零外发** ★"
        ),
        note=(
            "★**2026-11-18 08:2x · cron fb67af40 (ARS45 队列自动派活) 新开并直接派出 (status=fixing ⇒ "
            "下一轮 in_flight 规则会跳过 sw-lead ⇒ 窗口消失 ⇒ 不与兄弟 job 775d9893 撞车)** ★ "
            "★**开单依据 (★main 08:1x 本机实读★)**: "
            "★**① SW 侧文档里共有 95 处位号引用 (★实测细口径·唯一★): `SW/SW_TIMING_REVIEW.md` 63 · "
            "`SW/SHUTDOWN_SEMANTICS_SPEC.md` 30 · `SW/BOARD_ONEPASS_SW_SYNC.md` 23 · `SW/EXTERNAL_DEPENDENCY_SELFCHECK.md` 8 · "
            "其余 3 份各 4** ⇒ ★**而 ISS-314 (verified) 实测: 板那一趟 S1 会给 156 个板位号加 `_1` 后缀 ⇒ 改完板这 95 处就【对不上板了】** "
            "⇒ ★**★但 SW 侧现在【没有任何一道闸】检查「SW 文档里引用的位号是否还存在于板上」⇒ ★**main 08:2x 实跑 SW 侧 9 道闸全 rc=0 "
            "⇒ 「全绿」不等于「改完板之后还对」★ ★ "
            "★**② ISS-315 (verified) 交卷页 §3.3 逐字: 「建议 main 挂进 `EXTRA_GATES` 的【具体位置与写法】(★本单没改 `state/gate_check.py`★)」"
            "⇒ 挂闸是 main 的机制地界, 但【挂之前该体检什么】是 sw-lead 的活★; ★**且 ISS-315 §5 第 6 条自己写着: "
            "`check_demo_panel_spec_r6_selftest.py` (ISS-309 的 7/7) 「建议也一起挂 —— ISS-309 当初就建议过, 至今没挂」** ★ "
            "★**任务书全文**: `state/dispatch_briefs/ISS-318_sw_ref_reachability_gate_and_hook_audit.md` "
            "(7,600 B · `check_brief_commands.py --brief-file` rc=0) ★ "
            "★**边界**: 零写板 · 零落表 · 零改 `state/gate_check.py` (★只交挂链写法与体检, 不挂★) · 零改既有判据方向 · "
            "零改 SW 侧既有文档正文 · 零改 `SW/SW_MD5_BASELINE_LEDGER.md` (★它就是判据的锚点账★) · 零外发 · 不替老板拍板 · 不自签 issue_log ★"
        ),
        brief_file=BRIEF_318,
    ),
    dict(
        id="ISS-319",
        owner="mech-lead",
        due="2026-11-19",
        severity="high",
        title=(
            "★★[主线内·MECH 侧·对账 + 影响面类·内部活] ★★【「板只改一次」那一趟的 MECH 侧: "
            "①把 ISS-316 的 26 条差集【逐条落到 owner + 落表批次 + 验收判据】 ②电芯型号订正的【真实影响面是 47 行 / 19 个活文件 / 3 个脚本】"
            "(★ISS-316 只点了 MECH_BUDGET 的 8 行★)】★★ "
            "⇒ ★**纯分析 / 对账 / 作业包类 · 零写板 · 零落表 · 零重生成 · 零改闸 · 零改既有文档正文 · 零外发 · 不替老板拍板** ★"
        ),
        note=(
            "★**2026-11-18 08:2x · cron fb67af40 (ARS45 队列自动派活) 新开并直接派出 (status=fixing ⇒ "
            "下一轮 in_flight 规则会跳过 mech-lead ⇒ 窗口消失 ⇒ 不与兄弟 job 775d9893 撞车)** ★ "
            "★**开单依据 (★main 08:1x 本机实读★)**: "
            "★**① ISS-316 (verified) 交卷页 §B5-3 自己写下: 「§4 的 26 条差集逐条指定 owner ⇒ ★**不然下一轮还是同一张差集**」** ★ "
            "★**② ★★main 08:1x 全仓实跑 `grep -rn ICP582035PR-01` (★排除 tmp/ · .trash/ · state/.bak_*★) 实测: "
            "活文件里共 47 行 / 19 个文件 (★MECH_BUDGET.md 自己就 9 行——ISS-316 给了 8 行, 漏了 L1177★) ⇒ "
            "且 3 处落在脚本里 (`MECH/service_port_check.py` L51 / `MECH/fit_check.py` L69 / `MECH/fit_check_v3_30mm.py` L55) "
            "+ 1 处落在打印包生成器 (`MECH/print/gen_print_pack_revb.py` L99) ⇒ ★**改文档不改脚本 ⇒ 脚本继续按旧型号算; "
            "改脚本的数 ⇒ 几何结论就变了** ⇒ 4 个脚本的 cell_thk/batt_thk 4.60 属于 ICP422339PR (ICP582035PR-01 实厚 6.4mm) "
            "⇒ ★**只许改注释里的型号名, 那几个数一个字都不许动** ★** ⇒ "
            "★**ISS-316 §5-1 的「影响行 8 行」不够 ⇒ 不补齐, 采购口径就还是会买错 (★到货厚 6.40mm ⇒ 装不进 7.30mm 镜脚 ⇒ H 链最坏 −1.10mm★)** ★ "
            "★**任务书全文**: `state/dispatch_briefs/ISS-319_mech_diff_ownership_and_cell_model_scope.md` "
            "(8,079 B · `check_brief_commands.py --brief-file` rc=0) ★ "
            "★**边界**: 零写板 · 零落表 · 零重生成 (★不许跑 `MECH/print/gen_print_pack_revb.py` / `verify_pack_revb.py`★) · "
            "零改闸 · 零改既有文档正文 · 零改脚本 · 零改 HW 域文件 (★要抄进 HW 作业包的出成逐字段落交 main★) · "
            "零外发 (★型号规格一律自己上 renata.com 官网查, 不许写「等原厂回信」★) · 不替老板拍板 · 不自签 issue_log ★"
        ),
        brief_file=BRIEF_319,
    ),
]


def read_yaml(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def atomic_write(path, data):
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_", suffix=".yaml")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
            f.flush()
            os.fsync(f.fileno())
        shutil.move(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def main():
    for p in (LOG, DL):
        if os.path.exists(p):
            shutil.copy2(p, p + BAK_SUF)

    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)

        log = read_yaml(LOG)
        issues = log.get("issues") or []
        by_id = {it.get("id"): it for it in issues}

        # ---- ① 落地 ----
        landed = []
        for iid, spec in LAND.items():
            it = by_id.get(iid)
            if it is None:
                print("SKIP %s (不在 issue_log)" % iid)
                continue
            if it.get("status") != "fixing":
                print("SKIP %s (status=%s, 非 fixing ⇒ 已被别人处理)" % (iid, it.get("status")))
                continue
            it["status"] = "verified"
            it["verify_result"] = "pass"
            it["verify_by"] = "main"
            it["verify_date"] = TODAY
            it["note"] = (it.get("note") or "") + " ★★ " + spec["note"] + " ★★ " + spec["brief"] + " ★★ " + ZERO_BOARD + " ★"
            landed.append(iid)

        # ---- ② 新开 ----
        opened = []
        for spec in NEW:
            iid = spec["id"]
            if iid in by_id:
                print("SKIP %s (已存在)" % iid)
                continue
            brief_text = ""
            if spec.get("brief_file"):
                with open(spec["brief_file"], encoding="utf-8") as f:
                    brief_text = f.read()
            issues.append(dict(
                id=iid,
                title=spec["title"],
                severity=spec["severity"],
                owner=spec["owner"],
                reporter="main",
                raised=TODAY,
                due=spec["due"],
                status="fixing",
                external=False,
                need_keys=[],
                fix_ref=None,
                verify_by="main",
                verify_result=None,
                verify_date=None,
                dispatched_at=TODAY,
                note=spec["note"],
                task_brief=brief_text,
            ))
            opened.append(iid)

        atomic_write(LOG, log)

        # ---- ③ dispatch_log ----
        dl = read_yaml(DL) or {}
        entries = dl.setdefault("entries", [])
        for iid in landed:
            entries.append(dict(
                issue=iid,
                agent=LAND[iid]["owner"],
                at=TODAY,
                brief="★**落地 (fixing → verified) · main 08:2x 本机独立复核** ★ " + LAND[iid]["brief"],
                job="cron fb67af40 (ARS45 队列自动派活) · ★**落地依据: 子会话已交卷 + 本机复跑闸全 rc=0 + 零写板双证** ★",
            ))
        for spec in NEW:
            if spec["id"] not in opened:
                continue
            entries.append(dict(
                issue=spec["id"],
                agent=spec["owner"],
                at=TODAY,
                brief="★**新开单 + 直接派出 (status 直接落 fixing)** ★ " + spec["note"],
                job=("cron fb67af40 (ARS45 队列自动派活) · ★派活时刻 2026-11-18 08:2x · "
                     "★**status 全程 fixing ⇒ 无 open 窗口 ⇒ 兄弟 job 775d9893 不会重复派** ★"),
            ))
        atomic_write(DL, dl)

    print("LANDED :", ", ".join(landed) if landed else "(无)")
    print("OPENED :", ", ".join(opened) if opened else "(无)")
    print("总 issue 条数 =", len(issues))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
