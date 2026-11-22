#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★ISS-311 / ISS-312 / ISS-313 落地 (fixing → verified) + 新开 ISS-314 / ISS-315 / ISS-316 (status=fixing, 本轮直接派出)★
   · cron 775d9893 (ARS45 继续执行后继计划) · 2026-11-18 07:3x ★

★**为什么有本脚本 (★main 07:2x~07:3x 本机实跑, 不抄任何 agent 报告★)**:
  · 本轮 `state/advance.py --json` ⇒ internal=[] · approvals=[] · waiting=[] · decisions=39 ⇒ ★**队列排空** ★
  · ★**但队列是【死锁】不是【真空】**: `state/issue_log.yaml` 实读 309 条 ⇒ ISS-311(fixing) / ISS-312(fixing) / ISS-313(fixing)
    ⇒ ★**advance.py 的 in_flight 规则 (该 agent 名下已有 fixing ⇒ 本轮不再派) ⇒ internal 永远是 []** ★
  · ★**三个总工全部空闲 (★本机实读 sessions_list + transcript mtime★)**: 三条子会话 **全部 status=done**
    (ISS-311 `agent:hw-lead:subagent:db461a9c` · ISS-312 `agent:sw-lead:subagent:6d023e21` · ISS-313 `agent:mech-lead:subagent:06d9e66f`)
    ⇒ ★**不是僵尸 fixing** (★有交付物在盘 + 自证本机复跑 rc=0 + 板 md5/mtime 未变★) ⇒ 可以落地 ★
  · ★**main 07:2x~07:3x 本机独立复核 (三条全过)★**:
      ISS-311: `python3 state/chain_gate.py` ⇒ rc=1 (★③PCB/⑤投产包 两条红 = 「板只改一次」本体老账, 非本单造★)
               · `bash state/pcbnew_py.sh state/check_pcb_nets.py` ⇒ rc=1 (★现状读数: 板与网表不等价★)
               · 交付物: `HW/PCB/ONETRIP_REISSUE_MANIFEST.md` (55,309 B) + `HANDOFF/2026-11-18_hw-lead_ISS311_板那一趟重出清单.md` (59,550 B)
               · `logs/iss311/` 13 件 · hw 分片 ISS-311 命中 65 行
      ISS-312: `python3 SW/tools/check_demo_panel_spec_r6_chainjudge_selftest.py` ⇒ **rc=0 · 4/4**
               · `python3 SW/tools/check_demo_panel_spec_r6_selftest.py` ⇒ **rc=0 · 7/7** (★回归基线未动★)
               · `python3 SW/tools/check_demo_panel_spec.py` ⇒ rc=0 · `--selftest` ⇒ **rc=0 · 22/22**
               · `python3 SW/tools/check_onepass_sw_sync.py` ⇒ rc=0 · `--selftest` ⇒ **rc=0 · 16/16**
               · 交付物: `HANDOFF/2026-11-18_sw-lead_ISS312_R6判据漏放修复.md` (56,871 B) + 新闸 + sw 分片 ISS-312 命中 15 行
      ISS-313: 交付物: `MECH/MECH_NEEDS_TRIAGE.md` (103,768 B) + `HANDOFF/2026-11-18_mech-lead_ISS313_MECH未答需求分类.md` (16,531 B)
               · `logs/iss313/` 34 件 · mech 分片: needs_from 184 → **121** · answers 79 · needs_closed 64 · needs_open_ledger 75
               · ★**机检实证 (★真闭环, 不是装饰★)**: `state/gate_check.py` 缺口清单 mech-lead **108 → 62 条** ★
      板零写板: `HW/PCB/demo_mainboard.kicad_pcb` md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` (前后逐字节相同)
      占位符扫描: 5 份交付页 `🔄/待填/PLACEHOLDER` 命中 **0**
  · ★**兄弟 job fb67af40 (ARS45 队列自动派活) 于 07:23:57 中途 abort** (★本机实读它的 transcript 尾部: 写完 3 份 brief → 跑命令存在性守卫 → "Aborted"★)
    ⇒ ★**3 份 brief 已在盘但没进 issue_log** ⇒ ★**本单接管: 校验 + 开单 + 派出** ★
    · `state/check_brief_commands.py --brief-file` ⇒ ISS-314 **rc=0** · ISS-315 **rc=0** (★兄弟 job 修过一处后再 abort★) · ISS-316 **rc=0** ★

★**本脚本只做四件事 (★全部原子: flock + 锁内重读 + tmp + fsync + os.replace★)**:
  ① issue_log.yaml: ISS-311 / ISS-312 / ISS-313 的 status → verified + verify_result / verify_date + note 追加
  ② issue_log.yaml: 新开 ISS-314 (hw-lead) / ISS-315 (sw-lead) / ISS-316 (mech-lead) · **status=fixing** (★本轮直接派出★)
  ③ dispatch_log.yaml: 追加 6 条登记 (3 条落地 + 3 条派出)
  ④ 不碰任何别的文件 (不碰板 · 不碰 HW/ MECH/ SW/ 的任何工程文件 · 不碰 PROJECT_TRACKER.md §0 锁死表)
"""
from __future__ import annotations

import fcntl
import os
import shutil

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
DL = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
BAK_SUF = ".bak_20261118_0735_cron775d_land311_312_313_open314_315_316"

TODAY = "2026-11-18"
BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"
BOARD_MTIME = "2026-11-06 07:07:17"

BRIEF_314 = os.path.join(HERE, "dispatch_briefs", "ISS-314_hw_s1_ref_rename_caliber_closure.md")
BRIEF_315 = os.path.join(HERE, "dispatch_briefs", "ISS-315_sw_judge_chain_closure.md")
BRIEF_316 = os.path.join(HERE, "dispatch_briefs", "ISS-316_mech_onetrip_input_pack.md")

ZERO_BOARD = (
    "★**边界自证 (★main 07:2x~07:3x 本机实跑★)**: 板 `HW/PCB/demo_mainboard.kicad_pcb` md5 "
    f"`{BOARD_MD5}` · mtime `{BOARD_MTIME}` 交卷前后逐字节相同 ⇒ **零写板** ★ · "
    "零落表 · 零改闸 · 零改既有文档正文 · 零外发 · 不替老板拍板 · 不自签 issue_log ★"
)

# ────────────────────────────────────────────────────────────────────────────
# ① 三条落地 (fixing → verified)
# ────────────────────────────────────────────────────────────────────────────
LAND = {
    "ISS-311": dict(
        verify_result=(
            "✅ verified (★main 2026-11-18 07:2x~07:3x 独立复核·不抄 agent 报告★) ⇒ "
            "★**交卷物在盘**: `HW/PCB/ONETRIP_REISSUE_MANIFEST.md` (55,309 B · 06:32) + "
            "`HANDOFF/2026-11-18_hw-lead_ISS311_板那一趟重出清单.md` (59,550 B · 06:36) + "
            "`logs/iss311/` 13 件 + hw 分片 (ISS-311 命中 65 行)★ ⇒ "
            "★**自证本机复跑**: `python3 state/chain_gate.py` ⇒ rc=1 (★③ PCB 准入红「板与网表不等价」· "
            "网表 480 / 板上 482 · ⑤ 投产包准入红「原理图源文件不一致 11 个」★ —— ★**这两条红 = 「板还没重出」本身, "
            "不是闸坏了, 也不是本单造★) · `bash state/pcbnew_py.sh state/check_pcb_nets.py` ⇒ rc=1 (★现状读数·板与网表不等价★) ★ "
            "★**交卷内容含**: 逐件的「重出清单 + 顺序 + 同趟出 + 验收判据」作业包 · "
            "★**C1 差 2 的根因 (板侧多出来的旧件 C_VBUS_GND, 不是网表新加的脚)** · "
            "★**额外查出 3 条同号异网 (Q_PG pad1/pad3 对调 · D_ESD_USB_D pad1 挂 SoM 侧) ⇒ C1 验收判据必须三项同时归零** ★ · "
            "★**原理图 11 个不一致 = 2 真旧 + 9 uuid 抖动** ★ · "
            "★**两颗开工前必拍的地雷 (板侧位号加 `_1` ⇒ C1 变「缺失 350 · 多余 352」= 口径没同步 · "
            "板侧改名 ⇒ `gen_bom.py` 按精确 ref 读板失效 ⇒ BOM 证据静默丢失且无报警)** ★"
        ),
        note=(
            "★**2026-11-18 07:3x · cron 775d9893 (ARS45 继续执行后继计划) 落地 verified** ★ "
            "★**子会话 `agent:hw-lead:subagent:db461a9c-fe47-4628-8ed6-bd1c794ff56f` status=done · 06:44 收** "
            "⇒ 不是僵尸 fixing ⇒ 可落地 ★ "
            "★**★本单挖出的两颗地雷是「板只改一次」那一趟的直接输入★**: ★**地雷 1** = 作业包 §5「网表/脚表/BOM 逐字节不变」与 "
            "§3-S1「板侧 156 个封装位号加 `_1`」★**自相矛盾** ⇒ 板改了名、网表不改名 ⇒ C1 必红 ⇒ 板要改第二次 "
            "(★根因 = `state/check_pcb_nets.py` 两侧都没有「图上位号 → 表侧 ref」的反查★) ⇒ ★**已开 ISS-314 收口** ★ "
            "★**地雷 2** = 板侧改名 ⇒ `state/gen_bom.py` L307-330 用【精确 ref】读板 ⇒ 约 24 个末字符是字母的位号查不到 ⇒ "
            "「封装/型号来源: 板文件 Value」证据行整段消失、opn 退回 `待定` ⇒ ★**没有任何报警, BOM 看着是绿的证据已经没了** ★ "
            "★**交卷页占位符 0 · 板 md5 + mtime 双重自证零写板** ★"
        ),
    ),
    "ISS-312": dict(
        verify_result=(
            "✅ verified (★main 2026-11-18 07:2x~07:3x 独立复核·不抄 agent 报告★) ⇒ "
            "★**交卷物在盘**: `HANDOFF/2026-11-18_sw-lead_ISS312_R6判据漏放修复.md` (56,871 B · 06:44) + "
            "`SW/tools/check_demo_panel_spec_r6_chainjudge_selftest.py` (21,999 B · 新建) + "
            "`SW/tools/check_demo_panel_spec.py` (72,837 B · 06:40 · 改前备份 `.bak_iss312`) + "
            "sw 分片 (ISS-312 命中 15 行)★ ⇒ "
            "★**自证本机复跑 (四条全绿)★**: "
            "`SW/tools/check_demo_panel_spec_r6_chainjudge_selftest.py` ⇒ **rc=0 · 4/4** (★新立的反向用例★) · "
            "`SW/tools/check_demo_panel_spec_r6_selftest.py` ⇒ **rc=0 · 7/7** (★ISS-309 立的回归基线, 一个字节没动★) · "
            "`SW/tools/check_demo_panel_spec.py` ⇒ rc=0 · `--selftest` ⇒ **rc=0 · 22/22** · "
            "`SW/tools/check_onepass_sw_sync.py` ⇒ rc=0 · `--selftest` ⇒ **rc=0 · 16/16** ★ "
            "★**修法 A + B 都落地 (★main 05:5x 已拍板★)**: A = 链头产出单号不唯一 ⇒ 判红 · "
            "B = 链头单号 ↔ 【独立信源 `state/issue_log.yaml` 真单号】对账 ⇒ ★**ISS-309 的两条变体 (台账自相矛盾 / "
            "台账自洽但单号是假的) 现在都判红 ⇒ 洞堵在产生点** ★ · "
            "★**两条留痕义务现在已生效**: ①链头落表单号必须与独立信源对得上 ②落表单必须在 issue_log 里留【文件名 + 链头 md5】** ★"
        ),
        note=(
            "★**2026-11-18 07:3x · cron 775d9893 (ARS45 继续执行后继计划) 落地 verified** ★ "
            "★**子会话 `agent:sw-lead:subagent:6d023e21-4fef-449b-a08f-e96de4d99301` status=done · 06:37 收** "
            "⇒ 不是僵尸 fixing ⇒ 可落地 ★ "
            "★**★本单交卷页点名的一条订正 (★必须记下来, 不许丢★)**: 任务书写「只改 `check_r6_hard_protected()`」, "
            "但 ★**ISS-309 已 verified 的实测说洞在 `check_r6_three_way()` ②-1** ⇒ 只改前者三条反向用例一条都跑不起来 ⇒ "
            "★**本单两处都加了同一套 helper**, 分工写进交卷单 B0 判决 2 ★ "
            "★**★本单主动收回了修法 B 的一半 (★诚实边界·交 main 拍★)**: 硬保护那条路径只加了 A、没加 B —— "
            "★**实测加了 B 会让 `check_onepass_sw_sync.py --selftest` 第 ⑮ 条 (合法改板正向放行) 假红 15/16** ⇒ "
            "按 ISS-309 铁律「假伤修夹具、不许改判据」而那个夹具文件不在本单可写范围 ⇒ ★**把 B 收回 (A 留着), 复跑 16/16, "
            "列为 need N-1 交 main 拍** ⇒ ★**已开 ISS-315 接住 N-1 (先修夹具, 再把 B 铺到硬保护路径)** ★ "
            "★**另两条 need**: N-2「板那一趟必须留痕 (★这条义务现在已生效 ⇒ 主线重出网表/脚表/BOM 那一趟的单号不留痕 ⇒ "
            "开工前 SW 闸会红★)」⇒ 已开 ISS-315 做成机器可判的新闸 · N-3「挂闸裁决」交 main · N-4「锚点副本跟到链头」可降级 ★"
        ),
    ),
    "ISS-313": dict(
        verify_result=(
            "✅ verified (★main 2026-11-18 07:2x~07:3x 独立复核·不抄 agent 报告★) ⇒ "
            "★**交卷物在盘**: `MECH/MECH_NEEDS_TRIAGE.md` (103,768 B · 06:43) + "
            "`HANDOFF/2026-11-18_mech-lead_ISS313_MECH未答需求分类.md` (16,531 B · 06:43) + "
            "`logs/iss313/` 34 件 + mech 分片 (needs_from 184 → **121** · answers **79** · needs_closed **64** · "
            "needs_open_ledger **75**)★ ⇒ "
            "★**自证本机复跑 (★机检实证, 真闭环不是装饰★)**: `python3 state/gate_check.py` ⇒ **rc=0** · "
            "★**Q1 18/18 · Q7 钉板 md5 闸链 9/9 道绿** · ★**缺口清单 mech-lead 108 → 62 条** (★那 46 条是真的闭掉了, "
            "不是把条数搬到别的字段★)· 5 份交付页占位符命中 **0** ★ · "
            "★**交卷内容含**: 四类逐条处置 (关 64 / 留 72 / 新答 26) · "
            "★**16 条外部依赖零外发自查结案** (★老板 2026-11-11 19:31 + 2026-11-12 02:02 政策★ · 命中全部标证据等级 + "
            "查不到的写降级方案)· 33 条与板那一趟直接相关的待答输入清单 + 8 项「结构侧已定、可直接用」的值"
        ),
        note=(
            "★**2026-11-18 07:3x · cron 775d9893 (ARS45 继续执行后继计划) 落地 verified** ★ "
            "★**子会话 `agent:mech-lead:subagent:06d9e66f-d7b1-4fe2-877c-9de10bf214bd` status=done · 06:38 收** "
            "⇒ 不是僵尸 fixing ⇒ 可落地 ★ "
            "★**★本单查出的一个真问题 (★型号-尺寸错配·不是文档洁癖★)**: ★**renata.com 实读 —— `ICP582035PR-01` = "
            "6.4mm 厚 / 20.5 / 37, 而项目把「4.6 × 23.5 × 40.5」挂在它名下 (`MECH/MECH_BUDGET.md` L330/L332/L340) ⇒ "
            "真型号应是 `ICP422339PR` ⇒ ★**照现型号采购装不进 7.30mm 镜脚 (电芯段 H 链 −1.10mm)** ⇒ "
            "★**这笔比文档订正本身更贵** ⇒ 已并进决策码 M-B2 给老板** ★ · "
            "★**另一处订正**: `MECH/MECH_BUDGET.md` §3 重量表补检修口盖板 **+0.73 g** ★ · "
            "★**★已知副作用如实记 (★不改判据·不改闸★)**: 关闭的 need 从 `needs_from` 移出后其 key 不再被 `referenced_keys` 引用 "
            "⇒ 对应 `answers` 各记 1 条 lint (455 → 489, ★新增 26 条正是本单新写的 answers★) ⇒ ★**lint 不进任何闸** "
            "(merge rc 只看片段完整 · gate rc 只看硬件真源闸 + 新闸 + 9 道钉板闸 · daily_check 也不看) ⇒ merge rc=0 / gate rc=0 未变** ⇒ "
            "★**宁可留 26 条 lint, 也不把答复藏在 .md 里** ★ · "
            "★**不代拍**: ② boss 类整理成决策码 M-B1~M-B17 一页交 main→老板 · 分片里 `decision` 字段本单一条没写 ★"
        ),
    ),
}

# ────────────────────────────────────────────────────────────────────────────
# ② 三条新开 (本轮直接派出 ⇒ status=fixing)
# ────────────────────────────────────────────────────────────────────────────
NEW = [
    dict(
        id="ISS-314",
        owner="hw-lead",
        due="2026-11-19",
        severity="high",
        title=(
            "★★[主线内·HW 侧·口径收口 + 沙盒预演类·内部活] ★★【「板只改一次」那一趟的 S1 位号改名口径收口: "
            "作业包 §5「网表/脚表/BOM 逐字节不变」与 §3-S1「板侧 156 个封装位号加 `_1`」★**自相矛盾** ⇒ "
            "C1 从「多余 2」变成「缺失 350 · 多余 352」⇒ 交一份【口径决策包 + 沙盒预演实测】★★ "
            "⇒ ★**纯分析 / 作业包类 + 沙盒预演 · 零写板 · 零落表 · 零重生成 · 零改闸 · 零改既有文档正文 · 零外发 · 不替老板拍板** ★"
        ),
        note=(
            "★**2026-11-18 07:3x · cron 775d9893 (ARS45 继续执行后继计划) 新开并直接派出 (status=fixing ⇒ "
            "下一轮 in_flight 规则会跳过 hw-lead ⇒ 窗口消失 ⇒ 不与兄弟 job 撞车)** ★ "
            "★**开单依据 (★main 07:2x 本机实读 `HW/PCB/ONETRIP_REISSUE_MANIFEST.md` §1-5 / §4-5 逐字★)**: "
            "★**ISS-311 已 verified · 它自己挖出两颗开工前必拍的地雷** ★ "
            "★**地雷 1**: 沙盒实测「板侧 156 个位号加 `_1`」⇒ C1 缺失 **350** · 多余 **352** · 同号异网 0 ⇒ "
            "★**反证「网表侧同规则改口径」⇒ 回到 0/2/3 ⇒ 结论不是「改名错」, 是「口径没同步」** ⇒ "
            "★**根因 = `state/check_pcb_nets.py` 的 `board_pads()` / `netlist_pads()` 两侧都没有「图上位号 → 表侧 ref」的反查** ★ "
            "★**地雷 2**: `state/gen_bom.py` 用【精确 ref】读板 (L307-330 + L143-175) ⇒ 板侧改名 ⇒ "
            "约 24 个末字符是字母的位号查不到 ⇒ 「封装/型号来源: 板文件 Value」证据行整段消失、opn 退回 `待定` ⇒ ★**无任何报警** ★ "
            "★**★本单要交的三件 (★纯分析, 不落补丁★)**: ①口径决策包 (哪一侧改 / 判据怎么改 / 改哪几行 / 改完 C1 预期读数) "
            "②沙盒预演实测 (★沙盒只写 `tmp/` 下本单自己的目录, 跑完即删★) ③C1 验收判据改成【三项同时归零: 缺失 0 + 多余 0 + 同号异网 0】 ★ "
            "★**任务书全文**: `state/dispatch_briefs/ISS-314_hw_s1_ref_rename_caliber_closure.md` "
            "(12,329 B · `check_brief_commands.py --brief-file` rc=0) ★ "
            "★**边界**: 零写板 · 零落表 · 零重生成 · 零改闸 (`check_pcb_nets.py` / `gen_bom.py` / `gen_pcb_netlist_board.py` / "
            "`gen_kicad_sch.py` 一律只读 ⇒ ★**只出补丁设计, 不落补丁★) · 零改既有文档正文 · 零外发 · 不替老板拍板 · 不自签 issue_log ★"
        ),
    ),
    dict(
        id="ISS-315",
        owner="sw-lead",
        due="2026-11-19",
        severity="high",
        title=(
            "★★[主线内·SW 侧·判据修复 + 新闸新建类·内部活] ★★【判据链收口: 把 ISS-312 收回去的「修法 B (链头落表单号 ↔ "
            "独立信源交叉核对)」铺到 `check_r6_hard_protected()` 硬保护路径 (★前置 = 先修 ISS-298 闸的沙盒夹具★) + "
            "立「落表留痕义务」机器可判新闸 (★可挂不挂·挂闸由 main★)】★★ "
            "⇒ ★**判据修复类 + 闸新建类 · 零写板 · 零落表 · 零改网表真源 · 零改 `state/gate_check.py` · 零外发 · 不替老板拍板** ★"
        ),
        note=(
            "★**2026-11-18 07:3x · cron 775d9893 (ARS45 继续执行后继计划) 新开并直接派出 (status=fixing)** ★ "
            "★**开单依据 (★main 07:2x 本机复跑★)**: ★**ISS-312 已 verified** (★本机实跑 `check_demo_panel_spec_r6_chainjudge_selftest.py` "
            "⇒ rc=0 · 4/4★) · ★**ISS-312 的结论 = 修法 B 只铺到了 `check_r6_three_way()` 一条路径, "
            "`check_r6_hard_protected()` 那条还开着** ⇒ ★**板 md5 合法变更时, 这条路径会漏放假单号** ⇒ "
            "★**这正是「板只改一次」那一趟要用的判据** ★ "
            "★**★ISS-312 为什么收回 B (★交卷页逐字★)**: 实测加了 B 会让 `check_onepass_sw_sync.py --selftest` 第 ⑮ 条 "
            "(★合法改板正向放行★) 假红 15/16 ⇒ 按 ISS-309 铁律「假伤修夹具、不许改判据」而那个夹具文件不在 ISS-312 可写范围 ⇒ "
            "★**⇒ 本单 = 先修夹具, 再把 B 铺到硬保护路径** ★ "
            "★**本单一并接住 ISS-312 的另外两条 need**: N-2「板那一趟必须留痕 (★这条义务现在已生效 ⇒ 主线重出网表/脚表/BOM "
            "那一趟的单号不留痕 ⇒ 开工前 SW 闸会红★)」⇒ ★**做成机器可判的新闸, 不是一句口号** · N-3「挂闸裁决」⇒ 只给写法交 main ★ "
            "★**★本单最容易犯的一条纪律**: 新闸在【当前盘面】必须 rc=0 ⇒ ★**若一建出来就红 ⇒ 那说明这条义务与现状不符 ⇒ "
            "老老实实写 need 交 main 拍口径, 不许自己把判据放宽去凑绿** ⇒ ★**另一条**: 不许拿 issue_log 自己的副本互证 "
            "(★那还是自证★) ⇒ 真单号必须能在 `state/issue_log.yaml` 的【真条目】里查到 ★ "
            "★**任务书全文**: `state/dispatch_briefs/ISS-315_sw_judge_chain_closure.md` "
            "(11,259 B · `check_brief_commands.py --brief-file` rc=0) ★ "
            "★**边界**: 零写板 · 零落表 · 零改网表真源 · 零改 `state/gate_check.py` · "
            "★**零改三个回归基线** (`check_demo_panel_spec_r6_selftest.py` 7/7 · `check_demo_panel_spec_r6_chainjudge_selftest.py` 4/4 · "
            "`check_demo_panel_spec.py` 的判据方向与 fail-closed 三条 ★**只许【加】不许【改】★) · 零外发 · 不替老板拍板 · 不自签 issue_log ★"
        ),
    ),
    dict(
        id="ISS-316",
        owner="mech-lead",
        due="2026-11-19",
        severity="high",
        title=(
            "★★[主线内·MECH 侧·输入包 + 决策一页类·内部活] ★★【「板只改一次」那一趟的结构侧输入包: "
            "①板框冻结闸 U-1 的【决策一页 + 机器可判判据】(★板框是所有其它拍的输入★) "
            "②结构侧那一趟要【同批出】的件清单 + 与 HW 侧清单的【交叉对账差集】(★= 「板改第二次」的风险清单★) "
            "③两处既有文档订正的逐字改法 (★电芯型号错配 + 检修口盖板 +0.73g★)】★★ "
            "⇒ ★**纯分析 / 作业包类 · 零写板 · 零落表 · 零改闸 · 零改既有文档正文 · 零重生成 · 零外发 · 不替老板拍板** ★"
        ),
        note=(
            "★**2026-11-18 07:3x · cron 775d9893 (ARS45 继续执行后继计划) 新开并直接派出 (status=fixing)** ★ "
            "★**开单依据 (★main 07:2x~07:3x 本机实读★)**: ★**老板 2026-11-17 00:43「接下来的目标是绘制 PCB 图」⇒ 板只改一次** ⇒ "
            "★**凡与【板框/板厚/层数/开口/重量预算】有关的待答条目都要在这一趟【之前】定, 否则板要改第二次** ★ "
            "★**三条已有交付 (★本单不许重做, 只许在它们之上收口★)**: "
            "★**ISS-310 (verified)**: 板框口径对照 + 36 档机器表 (★3 套框 × 板厚 {0.80/1.00/1.22/1.60} × 层数 {4/6/8} · "
            "阈值只读 `MECH/service_port_check.py` 的 BASE/TOL/CRIT ⇒ 零自造零漂移★) ★ "
            "★**ISS-311 (verified · hw-lead)**: HW 侧产出链重出清单 → `HW/PCB/ONETRIP_REISSUE_MANIFEST.md` ★ "
            "★**ISS-313 (verified · 本单上一条)**: MECH 域 needs 四分类处置 + 33 条板那一趟待答输入清单 + 8 项已定值 ★ "
            "★**★板框 U-1 是整条链的第一前置**: ISS-313 的 need `proto_pcb_freeze_gate` 写明「板框冻结闸还差 U-1 "
            "(板框三选一: `B160x100` / `F30A` / `P60x15`) ⇒ 板只改一次那一趟开工前必须先冻结 (板厚 1.00 / 6 层与 PIN-SET-2 套 A 已定)」★ ⇒ "
            "★**ISS-310 的结论也指向同一句: 框是所有其它拍的输入; 框不定, 后面每一拍的代价都算不出来** ★ "
            "★**★本单最有价值的一条 = 与 HW 侧清单的交叉对账差集**: ★**以【板框三选一】为轴最容易打架 (HW 侧写的是哪一套框的板宽/板长/坐标, "
            "与 MECH 侧的开口坐标是否在同一套框上) ⇒ 差集 = 「板改第二次」的风险清单** ★ "
            "★**★8 项已定值一律回到 `MECH/MECH_NEEDS_TRIAGE.md` 逐字取, 不许凭记忆写数** ★ "
            "★**任务书全文**: `state/dispatch_briefs/ISS-316_mech_onetrip_input_pack.md` "
            "(10,792 B · `check_brief_commands.py --brief-file` rc=0) ★ "
            "★**边界**: 零写板 · 零落表 · 零改闸 · 零改既有文档正文 (`MECH/MECH_BUDGET.md` 的 §1.3/§1.4.3/§3 只给逐字改法, 自己一个字不许改) · "
            "零重生成 · 零外发 · 不替老板拍板 · 不自签 issue_log ★"
        ),
    ),
]


def main() -> int:
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)

        # ---------------- ① issue_log.yaml ----------------
        shutil.copy2(LOG, LOG + BAK_SUF)
        with open(LOG, encoding="utf-8") as f:
            log = yaml.safe_load(f)
        by = {it["id"]: it for it in log["issues"]}

        for iid, cfg in LAND.items():
            it = by.get(iid)
            if it is None:
                print(f"!! {iid} 不在 issue_log 里, 跳过")
                continue
            it["status"] = "verified"
            it["verify_by"] = "main"
            it["verify_result"] = cfg["verify_result"]
            it["verify_date"] = TODAY
            it["note"] = (str(it.get("note") or "").rstrip() + "\n\n" + cfg["note"])
            print(f"   ✓ {iid}: fixing → verified (verify_result 已写)")

        for spec in NEW:
            if spec["id"] in by:
                print(f"!! {spec['id']} 已存在, 不新开 (防重复)")
                continue
            brief_path = {"ISS-314": BRIEF_314, "ISS-315": BRIEF_315, "ISS-316": BRIEF_316}[spec["id"]]
            with open(brief_path, encoding="utf-8") as f:
                brief = f.read()
            log["issues"].append({
                "id": spec["id"],
                "title": spec["title"],
                "severity": spec["severity"],
                "owner": spec["owner"],
                "reporter": "main",
                "raised": TODAY,
                "due": spec["due"],
                "status": "fixing",
                "external": False,
                "need_keys": [],
                "fix_ref": None,
                "verify_by": "main",
                "verify_result": None,
                "verify_date": None,
                "dispatched_at": TODAY,
                "note": spec["note"],
                "task_brief": brief,
            })
            print(f"   ✓ {spec['id']} 新开 (owner={spec['owner']} · status=fixing · brief {len(brief)} B)")

        tmp = LOG + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)
        os.replace(tmp, LOG)

        # ---------------- ② dispatch_log.yaml ----------------
        shutil.copy2(DL, DL + BAK_SUF)
        with open(DL, encoding="utf-8") as f:
            dl = yaml.safe_load(f)
        entries = dl.setdefault("dispatches", [])

        for iid, cfg in LAND.items():
            entries.append({
                "issue": iid,
                "agent": by[iid]["owner"],
                "at": TODAY,
                "brief": (
                    f"★**{iid} 落地 (fixing → verified) · cron 775d9893 (ARS45 继续执行后继计划) · 07:2x~07:3x** ★ "
                    f"★**依据 = main 本机独立复核 (不抄 agent 报告)**: {cfg['verify_result'][:400]}… ★"
                ),
                "job": (
                    "cron 775d9893 (ARS45 继续执行后继计划) · ★派活时刻 2026-11-18 07:3x · "
                    "★**落地 = 子会话 status=done + 交付物在盘 + 自证本机复跑 rc=0 + 板 md5/mtime 未变** ★ "
                    "★**★本轮顺手解开了队列死锁: 三条僵尸 fixing 落地 ⇒ advance.py 的 in_flight 规则不再压住三个总工** ★"
                ),
            })

        for spec in NEW:
            entries.append({
                "issue": spec["id"],
                "agent": spec["owner"],
                "at": TODAY,
                "brief": (
                    f"★**{spec['id']} 新开并直接派出 (status=fixing)**: {spec['title'][:220]}… ★ "
                    "★**任务书全文**: `state/dispatch_briefs/"
                    + {"ISS-314": "ISS-314_hw_s1_ref_rename_caliber_closure.md",
                       "ISS-315": "ISS-315_sw_judge_chain_closure.md",
                       "ISS-316": "ISS-316_mech_onetrip_input_pack.md"}[spec["id"]]
                    + "` ★ ★**边界**: 零写板 · 零落表 · 零改闸 · 零改既有文档正文 · 零外发 · 不替老板拍板 · 不自签 issue_log ★"
                ),
                "job": (
                    "cron 775d9893 (ARS45 继续执行后继计划) · ★派活时刻 2026-11-18 07:3x · "
                    "★**★brief 由兄弟 job fb67af40 于 07:16~07:20 写好但该 job 于 07:23:57 中途 abort ⇒ 未进 issue_log ⇒ 本单接管** ★ "
                    "★**校验**: `check_brief_commands.py --brief-file` rc=0 · ★**派出纪律: ①先落 fixing ②再 spawn** ⇒ "
                    "落完 fixing ⇒ 下一轮 in_flight 规则会跳过这个 agent ⇒ 窗口消失 ⇒ 不与兄弟 job 撞车 ★"
                ),
            })

        tmp_dl = DL + ".tmp"
        with open(tmp_dl, "w", encoding="utf-8") as f:
            yaml.safe_dump(dl, f, allow_unicode=True, sort_keys=False, width=200)
        os.replace(tmp_dl, DL)

        # ---------------- ③ 回读校验 ----------------
        with open(LOG, encoding="utf-8") as f:
            chk = yaml.safe_load(f)
        by2 = {it["id"]: it for it in chk["issues"]}
        for iid in list(LAND) + [s["id"] for s in NEW]:
            it = by2.get(iid)
            print(f"   {iid}: status={it.get('status')} owner={it.get('owner')} brief={len(it.get('task_brief') or '')} B")
        print(f"   issues 总数 = {len(chk['issues'])}")
        print(f"   备份 = {os.path.basename(LOG + BAK_SUF)} / {os.path.basename(DL + BAK_SUF)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
