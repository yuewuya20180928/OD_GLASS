#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main: 落 3 个 verified (ISS-215 / ISS-217 / ISS-219) + 新开 3 单 (ISS-220 hw-lead / ISS-221 sw-lead / ISS-222 mech-lead)
=========================================================================================
★**为什么这次是"落账 + 开单"而不是"再派一轮规格" (★2026-11-16 02:2x 队列自动派活 job fb67af40 实测★)** ★
· ★**`advance.py --json` 的 A 段 (internal) = 0 条** ⇒ 不是没活, 是三个总工名额全被 `fixing` 占住 ★
· ★**逐个会话实查 (★`sessions_list` 实查 + 盘上实物实查★)**:
  - ISS-215 (sw-lead) · `agent:sw-lead:subagent:6a8a7c62` (8ce94e13) → **status=done @01:59:16** ★
    ⇒ ★**盘上交付物真在**: `SW/DEMO_60MS_DISPLAY_REANCHOR_TRIAGE.md` (17519 B, 01:57) ·
    `HANDOFF/2026-11-16_sw-lead_ISS215_demo60ms判据链显示侧重锚.md` (14108 B, 01:58) · `state/fragments/sw.yaml` mtime 01:58 ★
  - ISS-217 (hw-lead) · `agent:hw-lead:subagent:ae224ea7` (22182228) → **status=done @02:00:35** ★
    ⇒ ★**盘上交付物真在**: `HW/SCHEMATIC_LANDING_WORKPACKET_V1.md` (154104 B, 01:57) ·
    `HANDOFF/2026-11-16_hw-lead_ISS217_落表作业包v1.md` (31803 B, 01:58) · `state/fragments/hw.yaml` mtime 01:59 ★
  - ISS-219 (mech-lead) · `agent:mech-lead:subagent:5740c977` (14c40934) → **status=done @01:58:15** ★
    ⇒ ★**盘上交付物真在**: `MECH/CENTER_CAVITY_REBALANCE_V2.md` (37385 B, 02:01) · `MECH/cavity_recalc_check.py` (56909 B, 02:01) ·
    `HANDOFF/2026-11-16_mech-lead_ISS219_正中区第2轮重排与k口径.md` (6266 B, 02:02) · `state/fragments/mech.yaml` mtime 02:03 ★
· ★**三条与上一轮的"僵尸 fixing" (session=done 但盘上 0 件) 形态不同 ⇒ 这一轮是【真交付·只差落账】★**
  ⇒ 本 job 的活 = ①main 独立复核 (自己跑门禁 + 自己 md5) ⇒ 落 `verified` ②放出 3 个名额 ★
    ③★**但光放名额还是断线** (三个总工名下 `open` 单 = 0 条) ⇒ 必须开新单 ★
· ★**开单的三条依据 (全部来自刚 verified 的三条交卷里"只报不改、登记 need 给 main"的账)**:
  - hw-lead: ISS-217 交卷明写"这是【作业包】不是执行记录, 网表一个字节都没改" ⇒ ★**规格侧已经到头了** ★
    ⇒ 第 4 轮规格只是加页 ⇒ ★**主线要的是落表 (第 2 步)** ⇒ ISS-220 ★
  - sw-lead: ISS-215 交卷明写"demo 口径 (2-lane@480×640) **没有对应预算脚本**" ⇒ 现在 demo 的 60ms 预算全是"整机脚本减出来的" ⇒ ISS-221 ★
  - mech-lead: ISS-219 交卷的 C-7/C-8 两条 need 的前置 **结构侧自己能算** ⇒ 不该继续挂在 main 身上变阻塞 ⇒ ISS-222 ★

★★**主线口径 (★老板 2026-11-11 10:07: 先解决原理图绘制的问题, PCB 布线/布局类一律不派★)** ★★
★★**本轮新开的 3 条 = 原理图落表 / 软件时序 / 结构口径 ⇒ 没有一条是 PCB 布线/布局类** ★★
★★**零外发** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★) ⇒ 本脚本不碰 `state/outbox/` ★★
★铁律: 干活的人不许自签 ⇒ verify_by=main (main 独立复核后落账)
★不碰: PROJECT_TRACKER.md §0 / 任何分片 / 任何真源文件 (板/网表/脚表/原理图/BOM) / outbox
"""
import fcntl
import os
import shutil

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
BAK = LOG + ".bak_20261116_0225_verify215_217_219_open220_221_222"

TODAY = "2026-11-16"
DUE = "2026-11-19"

# ==================================================================
# ① 落 verified: ISS-215 / ISS-217 / ISS-219 (main 独立复核)
# ==================================================================
VERIFY = {
    "ISS-215": (
        "★main 独立复核通过 (★2026-11-16 02:2x, 只看盘上实物 + 自己跑门禁★):\n"
        "  · SW/tools/demo_timing_check.py → rc=0 (34/34, 含 ISS-215 那 6 条新断言全绿)\n"
        "  · SW/tools/demo_timing_check.py --selftest → rc=0 (ISS-215 反例 5 条全抓到 ⇒ 门禁不是假绿)\n"
        "  · SW/tools/check_demo_panel_spec.py → rc=0 (R1~R6 全过, ISS-212 门禁未被改红)\n"
        "  · 交付物在盘: SW/DEMO_60MS_DISPLAY_REANCHOR_TRIAGE.md (17519 B, 01:57) · "
        "HANDOFF/2026-11-16_sw-lead_ISS215_demo60ms判据链显示侧重锚.md (14108 B, 01:58) · "
        "state/fragments/sw.yaml mtime 01:58\n"
        "  · md5 逐字节未变: 网表 c78f991283cc82d56c8e3dd31657c785 · 脚表 4814617e22b567d76164e56bc5e39dc8 · "
        "板 611b869e13518c3c023fb178f91a0075 · .kicad_pro 3e504d2be83152e337949723e909be1b\n"
        "★**板端 [实测] = 0 条** (板不在本机) ⇒ 显示侧预算数一律 [推算] ★\n"
        "★**main 已复核的关键结论**: ① 10.09 ms 是【显示输出侧总额上限】(与分辨率无关), 不是 1080p 专属数 ⇒ "
        "机器门禁改成强制它带「输出侧上限」身份 (而不是把它禁掉) ② 判据被算严的根因只有一处 = 用整机 TX 下限 7.776 去扣 demo 预算 (倍率 3.36×) "
        "③ yolov5n@640 行的判定方向由 ❌ 翻成 ✅[推算] ⇒ **显示侧不再是 60ms 账本的瓶颈** ★",
        "2026-11-16 02:2x",
    ),
    "ISS-217": (
        "★main 独立复核通过 (★2026-11-16 02:2x, 只看盘上实物 + 自己跑门禁★):\n"
        "  · HW/check_netlist_selfconsistency.py → rc=0 (★现状守卫 + 作业包完整性 + 三方对齐 全过★)\n"
        "  · HW/check_netlist_selfconsistency.py --selftest → rc=0 (自检结果: 19/19 通过)\n"
        "  · HW/check_netlist_selfconsistency.py --expect-resolved → rc=1 (★翻面口径未通过 = 缺陷尚未落表 = 预期状态★)\n"
        "  · state/check_netlist.py → rc=0 (全过, 原理图 V1.1 可进交叉评审)\n"
        "  · state/check_netlist_pins.py → rc=0 (每个针脚归属唯一)\n"
        "  · state/check_sch_erc.py → rc=0 (ERC 违规数 = 0)\n"
        "  · 交付物在盘: HW/SCHEMATIC_LANDING_WORKPACKET_V1.md (154104 B, 01:57 · 28 条作业条目 × 8 栏齐) · "
        "HANDOFF/2026-11-16_hw-lead_ISS217_落表作业包v1.md (31803 B, 01:58 · B1~B6 齐) · state/fragments/hw.yaml mtime 01:59\n"
        "  · md5 逐字节未变: 网表 c78f991283cc82d56c8e3dd31657c785 · 脚表 4814617e22b567d76164e56bc5e39dc8 · "
        "板 611b869e13518c3c023fb178f91a0075 · .kicad_pro 3e504d2be83152e337949723e909be1b\n"
        "★**这是【作业包】不是执行记录** ⇒ 网表/脚表/板/生成器 一个字节都没改 (main 实测 md5 一致) ★\n"
        "★**6 条待裁 (V-1~V-6) 一条没代拍** ⇒ 其中 V-4 (R_ILIM 档位) 已在 `DECISION_PENDING_2026-11-16.md` §3 作为老板待拍项 ⇒ "
        "⇒ **落表那一趟 (本 job 新开的 ISS-220) 只能落不依赖 V-1~V-6 的条目** ★",
        "2026-11-16 02:2x",
    ),
    "ISS-219": (
        "★main 独立复核通过 (★2026-11-16 02:2x, 只看盘上实物 + 自己跑门禁★):\n"
        "  · MECH/cavity_recalc_check.py → rc=0 (17/17)\n"
        "  · MECH/cavity_recalc_check.py --selftest → rc=0 (15/15, 既有 9 + 新增 5 反向用例全抓到)\n"
        "  · MECH/verify_budget.py → rc=0 (★门禁绿: 充电耗散 = buck 口径, 没被改回线性 0.8W★; C17 反向用例证明 k=201 口径不许漂回 237)\n"
        "  · MECH/check_demo_struct_truth.py → rc=0 (20/20 组检查通过 · FAIL 0 组)\n"
        "  · 交付物在盘: MECH/CENTER_CAVITY_REBALANCE_V2.md (37385 B, 02:01) · MECH/cavity_recalc_check.py (56909 B, 02:01) · "
        "HANDOFF/2026-11-16_mech-lead_ISS219_正中区第2轮重排与k口径.md (6266 B, 02:02) · state/fragments/mech.yaml mtime 02:03\n"
        "  · md5 逐字节未变: 网表 c78f991283cc82d56c8e3dd31657c785 · 板 611b869e13518c3c023fb178f91a0075 · "
        ".kicad_pro 3e504d2be83152e337949723e909be1b · 4 个受保护 check 脚本全部一致\n"
        "★**main 已复核的关键结论**: ① C-6 分光件放大后 C-8 (t_s=6.0 与 45° 平板竖向投影不自洽) 是**本单自己查出的新冲突** ⇒ 三档 T=18/21/23 需重算 "
        "② C-7 结论翻转: 金属热路不是瓶颈 (R_热路 9.40-23.51 ≪ 70 K/W), **瓶颈是集热面面积** (d=15 需 ≈2628 vs 端件 600-800) ⇒ 只有 P3 方案三档全达标 "
        "③ u8 只占集热面 14.3-18.2% ⇒ **不阻塞** ★\n"
        "★**3 条新 need 挂 main** (C-8 轴口径 / C-7 集热面 3600mm² 可行性 / M6 落地裁) ⇒ ★**其中 C-7、C-8 结构侧自己能算 ⇒ 本 job 新开 ISS-222 承接** ★",
        "2026-11-16 02:2x",
    ),
}

FIX_REF = {
    "ISS-215": "HANDOFF/2026-11-16_sw-lead_ISS215_demo60ms判据链显示侧重锚.md",
    "ISS-217": "HANDOFF/2026-11-16_hw-lead_ISS217_落表作业包v1.md",
    "ISS-219": "HANDOFF/2026-11-16_mech-lead_ISS219_正中区第2轮重排与k口径.md",
}

NOTE_TAIL = (
    "\n★**2026-11-16 02:2x 队列自动派活 job (fb67af40) 落 `verified`**: 子会话 status=done ⇒ ★**main 不采信状态位, 只看盘上实物 + 自己跑门禁 + 自己 md5** "
    "⇒ 交付物在盘 + 门禁全绿 ⇒ 落 `verified` (★不是 closed★) ⇒ 放出该总工名额 ★\n"
    "★**边界**: 不改 §0 锁死表 · 不写任何子总工的分片 · 不发信 · 网表/脚表/板/原理图/BOM 一个字节未动 ★"
)

# ==================================================================
# ② 新开 ISS-220 → hw-lead (原理图主线 · 落表第 2 步)
# ==================================================================
TITLE_220 = (
    "★★★[主线内·原理图/网表侧·内部活] 【整链重出 第 2 步 · 原理图侧落表执行】把 ISS-217 作业包 28 条里"
    "「不依赖 6 条待裁 V-1~V-6」的条目真的落进真源 (SPEC.json / gen_netlist.py / gen_schematic_pages.py / CHARGE_BOARD_SPEC.md 等) "
    "+ 重生成网表/脚表 + 让机器门禁的「未落表条数」实打实下降 (50 → N) + 逐条标出哪些条目落表后需要板侧同步 "
    "(★允许改真源 = 这是主线核心★ · 不许碰板/PCB 布线布局 · 不许代拍 V-1~V-6)"
)

DESC_220 = (
    "★**ISS-211 → ISS-214 → ISS-217 三轮已经把「网表/规格自己跟自己打架」定成了 28 条机器可判的作业条目** "
    "(★作业包 `HW/SCHEMATIC_LANDING_WORKPACKET_V1.md`, 154 KB, 11:57 落盘; 门禁已扩到「作业包漏一条就红 + 三方对齐 + R9 阈值 3.0mm」, 自检 19/19★) "
    "⇒ ★**规格这一侧已经到头了** (再写第 4 轮规格只是加页) ⇒ ★**老板 2026-11-11 10:07 主线「先解决原理图绘制的问题」要的下一步是【落表】, 不是再写规格** ★ "
    "★**本单是作业包的下一步 = 执行那一趟**: 逐条按 ④栏(真修法在哪个真源) / ⑤栏(改成什么字面值) / ⑥栏(改完跑哪条命令) / ⑦栏(翻面判据 R#) 落表 ★ "
    "★**依赖 6 条待裁 (V-1~V-6) 的条目一律标 BLOCKED 不落** (★V-4 R_ILIM 档位已是 `DECISION_PENDING_2026-11-16.md` §3 的老板待拍项, 其余 V-1/V-2/V-3/V-5/V-6 是 main/老板级裁决 ⇒ "
    "★**本单不许代拍**, 也不许把整机路线占位区里的数当 demo 真值★) ★ "
    "★**落表若触发板侧同步需求 (位号/封装/网络改动) ⇒ 只报告条数与行号, 由 main 另派 PCB 单 (老板 10:07 口径: PCB 布线/布局类一律不派)★ ★ "
    "★**零外发** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★) ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ★"
)

BRIEF_220 = (
    "★★**目标 (★内部活·不是 PCB 布线/布局类·不是老板级拍板★)**: 把 ★**ISS-217 交卷的作业包 `HW/SCHEMATIC_LANDING_WORKPACKET_V1.md` 里"
    "「不依赖 6 条待裁 V-1~V-6」的作业条目, 真的落进真源文件**★ ⇒ 出 ★**(1) 一份逐条落表记录 (改哪个真源的哪一行 · 改前/改后字面值 · 落表后跑的命令与输出行 · 未落的写明 BLOCKED 于哪条 V-x) "
    "· (2) 真源改动 + 重生成网表/脚表 · (3) 机器门禁「未落表条数」的前后对比 · (4) 一份交接单**★ "
    "⇒ ★**本单允许改真源 (这是主线核心, 与前三轮「只出规格不许改网表」不同)**, 但 ★**不许碰板 / PCB 布线 / 布局 / 板框**★ ⇒ ★**零外发** ★\n\n"
    "★★**为什么是现在 (★main 2026-11-16 02:2x 实测, 不是推测★)** ★★\n"
    "· ★**ISS-217 (11-16 01:57 交卷, 本 job 02:2x 已落 verified) 把 12 组「网表/规格自相矛盾」定成了 28 条机器可判的作业条目** "
    "(作业包 154 KB · 28 条 × 8 栏齐 · 门禁扩项后自检 19/19 · `--expect-resolved` 现状 rc=1 报「50 条未落表」) ★\n"
    "· ★**那份文件自己第一行就写明「这是【作业包】, 不是执行记录 ⇒ 网表 / 脚表 / BOM / 板 / 生成器 一个字节都没改」** ★\n"
    "· ⇒ ★**规格侧三轮 (ISS-211 / ISS-214 / ISS-217) 已经做到头了 ⇒ 第 4 轮规格只是加页** ★\n"
    "· ⇒ ★**老板 2026-11-11 10:07 主线 = 「先解决原理图绘制的问题, 再解决 PCB 绘制的问题」⇒ 这一步必须是【落表】** ★\n"
    "· ⇒ ★**本单是三个总工名额里唯一能直接推进主线的一条 (sw-lead 那条是软件时序侧, mech-lead 那条是结构侧)** ★\n\n"
    "★★**交付物 (4 件, 少一件即无效) ★★\n"
    "① ★**落表记录 `HW/SCHEMATIC_LANDING_V1_LANDED.md`** ★ ⇒ 逐条 (作业包条目号 d1..d11 / 附带 #1..#8 / 补差 A/B/C → 改了哪个真源文件的哪一行 → 改前/改后字面值 → "
    "落表后跑的命令与输出行 → 证据等级) ⇒ ★**未落的条目必须写明「BLOCKED 于 V-x」并给出它需要谁拍** ⇒ ★**不许留「待定」** ★\n"
    "② ★**真源改动 + 重生成** ⇒ 只许改作业包 ④ 栏点名的真源 (`HW/SCHEMATIC_V1_SPEC.json` / `state/gen_netlist.py` / `state/gen_schematic_pages.py` / "
    "`HW/CHARGE_BOARD_SPEC.md` / 作业包 ④ 栏点名的其他文件) ⇒ 改完用 `python3 state/gen_netlist.py` 重生成网表/脚表 ⇒ ★**不许手工编辑生成产物 (CSV)★** ★\n"
    "③ ★**机器门禁前后对比** ⇒ 把 `python3 HW/check_netlist_selfconsistency.py --expect-resolved` 的输出**改前/改后两次都贴出来** (★重点是「未落表条数」从 50 降到多少★) ⇒ "
    "★**落表不许靠删条目/改判据达成 ⇒ 门禁的 EXPECT 锚点组 d1..d11 一个不许减** ★\n"
    "④ ★**交接单 `HANDOFF/2026-11-16_hw-lead_ISS220_落表第1批.md`** (★B1~B6 六块齐全★) + ★**分片 `state/fragments/hw.yaml` (★必须走 `python3 state/frag_write.py` 原子写★)** ★\n"
    "⑤ ★**落表后需要板侧同步的清单** ⇒ 逐条列 (条目号 / 需要改板上的什么 / 行号) ⇒ ★**只报告, 不许改板** ★\n\n"
    "★★**边界 (★违反一条即本单无效★) ★★\n"
    "· ★**不许改** `HW/PCB/demo_mainboard.kicad_pcb` / `HW/PCB/demo_mainboard.kicad_pro` / ★**不许碰 PCB 布线 / 布局 / 板框** (★老板 2026-11-11 10:07 口径★) ★\n"
    "· ★**不许代拍 V-1~V-6** ⇒ 依赖它们的条目一律标 BLOCKED ⇒ ★**V-4 (R_ILIM 档位) 已在 `DECISION_PENDING_2026-11-16.md` §3 是老板待拍项** ★\n"
    "· ★**不许改** `MECH/` 下任何文件 / `SW/` 下任何文件 / `state/issue_log.yaml` / `PROJECT_TRACKER.md` §0 / `state/outbox/` / 别人的分片 / "
    "`MECH/hinge_usb_check.py` / `MECH/service_port_check.py` / `MECH/hw_cross_review_check.py` / `MECH/display_biosafety_v2_check.py` ★\n"
    "· ★**开工前先给每个要改的真源文件留一份 `.bak_iss220` 副本** (★便于回滚★) ⇒ 交卷时贴出每个真源文件的 md5 前/后对照 ★\n"
    "· ★**不许改判据阈值** (★门禁的 EXPECT / R1~R11 判据 / 现有阈值一律不许为了让门禁变绿而放松★) ★\n"
    "· ★**零外发** (★不发邮件 / 询价 / 问询 / 采购 / 原厂问询★) ⇒ 缺口一律【自己网上查】+ 标 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` + ★**查不到必须写降级方案** ★\n"
    "· ★**本单实物 [实测] = 0 条** (板不在本机) ⇒ 标 [实测] 的只允许是「本机脚本 / 本机文件实读」 ★\n"
    "· ★**不许自签 issue_log** (★status 留给 main 落 verified★) ★\n\n"
    "★★**交卷前必须实跑并把输出原样贴进回复 (★命令都已实测存在★) ★★\n"
    "```\n"
    "python3 HW/check_netlist_selfconsistency.py                    # rc=0 (现状守卫 + 作业包完整性 + 三方对齐)\n"
    "python3 HW/check_netlist_selfconsistency.py --selftest          # rc=0 (反向用例全抓到, 19/19 或更多)\n"
    "python3 HW/check_netlist_selfconsistency.py --expect-resolved   # ★rc=1 是预期 (还有 BLOCKED 条目) ⇒ 必须贴「未落表条数」的前后对比\n"
    "python3 state/check_netlist.py                                  # rc=0 (全过)\n"
    "python3 state/check_netlist_pins.py                             # rc=0 (每个针脚归属唯一)\n"
    "python3 state/check_sch_erc.py                                  # rc=0 (ERC 违规数 = 0)\n"
    "python3 state/merge.py && python3 state/gate_check.py           # rc=0 且 【Q1 交付齐备率】 18/18\n"
    "```\n"
    "★**落表若导致上面某条门禁变红 ⇒ 不许放松门禁, 也不许回退已落表的条目来凑绿 ⇒ 交卷报红并说明原因 (★main 复核)**★"
)

# ==================================================================
# ③ 新开 ISS-221 → sw-lead (demo 口径预算真源)
# ==================================================================
TITLE_221 = (
    "★★[主线内·软件/时序侧·内部活] demo 屏 (2-lane@480×640) 自己的 60ms 预算真源脚本 `SW/tools/demo_e2e_budget.py` "
    "+ 把 demo 判据链的数字从「整机脚本减出来的」换成「demo 真源算出来的」 + 机器断言 (判据链不许再引用整机 4-lane 常量) "
    "+ 收口 SW/RKNN_BENCH.md 的 S9 注记分叉 (不改 HW·不改任何板端实测数字)"
)

DESC_221 = (
    "★**ISS-212 已把 demo 屏规格钉死 (480×640 / 2-lane / 无 DCS / I2C_B ≤ 100 kHz)**, ★**ISS-215 (11-16 01:5x 交卷, 本 job 02:2x 已落 verified) 把显示侧口径重锚到 demo**, "
    "并查清两件事: ① ★**10.09 ms 是「显示输出侧总额上限」, 与分辨率无关** (依据 `HW/e2e_budget_rk3572.py` 的 `T_FIXED_OTHER = 31.00 # 与显示分辨率无关的部分` + "
    "`display_out_max_for()`) ② ★**判据被算严的根因只有一处 = 用整机的 TX 下限 7.776 去扣 demo 的预算 (倍率 3.36×)**, 与 ISS-212 Q-5「余量 2.32→7.79」逐位吻合 ★ "
    "★**但 demo 那侧至今没有一个自己的预算真源**: 整机那本 `HW/e2e_budget_rk3572.py` 的 DSI 带宽常量是 **4-lane @ 2.0 Gbps × 80%**, 对 2-lane 的 demo 屏不适用 ⇒ "
    "⇒ 现在 demo 的每一个预算数都是「整机脚本减出来的」⇒ ★**同一个坑会被再咬一次** (换屏/改分辨率/改 lane 数时, 没人拦得住) ⇒ 本单把 demo 预算真源补上 ★ "
    "★**外加 ISS-215 交卷点名的遗留分叉**: `SW/RKNN_BENCH.md` §4.1 L273 的 S9 注记仍是整机原文, 与 `SW/tools/rknn_bench.py` L258 的 demo 口径注记分叉 (★S9 = 3.0 这个数值两边都没动, 只是措辞分叉★) ★ "
    "★**零外发** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★)"
)

BRIEF_221 = (
    "★★**目标 (★内部活·不是 PCB 布线/布局类·不是老板级拍板★)**: 给 demo 屏 (★2-lane @ 480×640★) 建 ★**它自己的 60 ms 预算真源脚本**★, "
    "并把 demo 判据链引用的数字 ★**从「整机脚本减出来的」换成「demo 真源算出来的」**★ ⇒ 出 ★**(1) 一份 demo 预算脚本 (含反向自检) · (2) 两份规格文件里的 demo 数字换成脚本输出 · "
    "(3) 一个机器断言「demo 判据链不许再引用整机 4-lane 常量」 · (4) 一份交接单**★ ⇒ ★**本单不许改 `HW/` 下任何文件**★ ⇒ ★**零外发** ★\n\n"
    "★★**为什么是现在 (★main 2026-11-16 02:2x 实测, 不是推测★)** ★★\n"
    "· ★**ISS-215 (11-16 01:5x 交卷, 本 job 02:2x 已落 verified) 交卷里明写: 「demo 口径 (2-lane @480×640) 目前没有对应的预算脚本 —— 整机那本 `HW/e2e_budget_rk3572.py` 的 "
    "DSI 带宽常量是 4-lane@2.0Gbps×80%, 对 2-lane demo 屏不适用」⇒ ★**已登记 need 给 main** ★\n"
    "· ★**ISS-215 同时查清**: 10.09 ms 是「输出侧总额上限」(与分辨率无关), 根因是「用整机 TX 下限 7.776 去扣 demo 预算」(倍率 3.36×) ⇒ ★**现在 demo 的账是从整机账减出来的** ★\n"
    "· ⇒ ★**换屏 / 改分辨率 / 改 lane 数时, 没有人拦得住「又拿整机常量扣 demo 预算」** ⇒ ★**所以这一步是补真源, 不是补文档** ★\n"
    "· ⇒ ★**本单是三个总工名额里唯一能推进 demo 板 60ms 生死判定链的软件侧一条** ★\n\n"
    "★★**交付物 (4 件, 少一件即无效) ★★\n"
    "① ★**`SW/tools/demo_e2e_budget.py`** (★新建★) ⇒ 输入 demo 屏参数 (宽/高/通道数/lane 数/lane 速率/每帧 payload/post 固定开销) ⇒ 输出 ★**TX 下限 / compose 上限 / 显示输出侧上限 / "
    "全链路 60ms 预算余量**★ ⇒ ★**口径必须写清: 哪些是整机同源常量 (★如 `T_FIXED_OTHER`★), 哪些是 demo 专属 (★lane 数 / 分辨率 / payload★)★ ⇒ "
    "★**必须带 `--selftest` 反向用例 (改坏必红)★** ⇒ ★**不许把整机的 4-lane 常量写死进本脚本冒充 demo 真源** ★\n"
    "② ★**`SW/DEMO_OD_TIMING_SPEC.md` + `SW/DEMO_BOARD_60MS_VERDICT_PLAN.md` 里的 demo 数字换成脚本输出** ⇒ ★**不许硬抄数字, 必须能追到脚本** ⇒ "
    "★**整机路线占位区的数一个不许删 (ISS-212 L-08/L-16 的规矩: 行级豁免标记 + 块级分区标记, 两套机制不变)★ ★\n"
    "③ ★**机器门禁扩项**: `SW/tools/demo_timing_check.py` 加断言 (★demo 判据链引用的数字 == demo 预算脚本输出, 且不许出现「整机 4-lane DSI 带宽常量」这类引用★) + 反向用例 ⇒ "
    "★**改坏必红** ★\n"
    "④ ★**交接单 `HANDOFF/2026-11-16_sw-lead_ISS221_demo预算真源.md`** (★B1~B6 六块齐全★) + ★**分片 `state/fragments/sw.yaml` (★必须走 `python3 state/frag_write.py` 原子写★)** ★\n"
    "⑤ ★**收口 ISS-215 的遗留分叉**: `SW/RKNN_BENCH.md` §4.1 L273 的 S9 注记 (★本单允许改这个文件, 但★**★只许改那一行注记, S9 = 3.0 这个数值和周边所有数字一个不许动**★) ⇒ "
    "★**改完 md5 前后对照贴出来** ★\n\n"
    "★★**边界 (★违反一条即本单无效★) ★★\n"
    "· ★**不许改** `HW/` 下任何文件 (★`HW/e2e_budget_rk3572.py` 只许只读引用, 一个字节不许动★) ★\n"
    "· ★**不许改** `SW/DEMO_OD_PIPELINE_SPEC.md` / `SW/RKNN_BENCH.md` 里除 §4.1 L273 那一行注记以外的任何内容 / `SW/tools/rknn_bench.py` 除必要的注记外不许改 (★S9 = 3.0 逐字节不许动★) ★\n"
    "· ★**不许改** `MECH/` 下任何文件 / `state/issue_log.yaml` / `PROJECT_TRACKER.md` §0 / `state/outbox/` / 别人的分片 ★\n"
    "· ★**板端 [实测] = 0 条** (★板与屏不在本机 ⇒ 全部预算数一律标 `[推算]`★) ⇒ 标 [实测] 的只允许是「本机脚本 / 本机文件实读」 ★\n"
    "· ★**不许编造板端时延数字** ⇒ ★**不许把整机 1080p 的数当 demo 的数写进任何文件** ★\n"
    "· ★**零外发** (★不发邮件 / 询价 / 问询 / 采购★) ⇒ 缺口一律【自己网上查】+ 标证据等级 + ★**查不到必须写降级方案** ★\n"
    "· ★**不许自签 issue_log** (★status 留给 main 落 verified★) ★\n\n"
    "★★**交卷前必须实跑并把输出原样贴进回复 (★命令都已实测存在★) ★★\n"
    "```\n"
    "python3 SW/tools/demo_e2e_budget.py                # rc=0 (新建★)\n"
    "python3 SW/tools/demo_e2e_budget.py --selftest     # rc=0 (反向用例全抓到)\n"
    "python3 SW/tools/demo_timing_check.py               # rc=0 (含本单新增断言)\n"
    "python3 SW/tools/demo_timing_check.py --selftest    # rc=0 (ISS-215 那 5 条反向用例不许被改红)\n"
    "python3 SW/tools/check_demo_panel_spec.py          # rc=0 (ISS-212 门禁不许被改红)\n"
    "python3 SW/tools/check_demo_panel_spec.py --selftest # rc=0\n"
    "python3 state/merge.py && python3 state/gate_check.py # rc=0 且 【Q1 交付齐备率】 18/18\n"
    "```"
)

# ==================================================================
# ④ 新开 ISS-222 → mech-lead (C-6 / C-7 / C-8 落地 + 集热面自算)
# ==================================================================
TITLE_222 = (
    "★★[主线内·结构侧·内部活] ISS-219 的 C-6 / C-7 / C-8 三条「只报不改」落进结构真源: C-6 分光件 11×11×1.5 + 2×9×9×5 (0.9697cc / W4 3.68-7.36g) 替换旧 M6 14×10×6 "
    "+ C-8 t_s=6.0 与 45° 平板竖向投影不自洽 ⇒ 自己实算 t_s 并重算三档 T=18/21/23 + C-7 集热面 3600mm² 可行性自己实算 + 机器门禁扩项 (不改 HW·不碰 PCB 布线布局·不预扣 §3 重量)"
)

DESC_221_NOTE = ""

BRIEF_222 = (
    "★★**目标 (★内部活·不是 PCB 布线/布局类·不是老板级拍板★)**: 把 ★**ISS-219 (11-16 02:0x 交卷, 本 job 02:2x 已落 verified) 交卷里那三条「只报不改、已登记 need 给 main」的冲突 "
    "真的落进结构真源**★ ⇒ ★**C-6** (分光件放大后的规格落文档) + ★**C-8** (★自己实算★ t_s 轴向口径 ⇒ 重算三档 T=18/21/23) + ★**C-7** (★自己实算★ 镜框上沿 3600mm² 集热面可不可行) "
    "⇒ 出 ★**(1) 一份落表后的结构口径记录 · (2) 三个真源文件的同步 · (3) 机器门禁扩项 · (4) 一份交接单**★ ⇒ ★**本单不许改 `HW/` 下任何文件**★ ⇒ ★**零外发** ★\n\n"
    "★★**为什么是现在 (★main 2026-11-16 02:2x 实测, 不是推测★)** ★★\n"
    "· ★**ISS-219 交卷明写**: C-8 是★**本单自己查出的新冲突**★ (★`t_s=6.0` 取自 §1.3 M6 包络的第三维 (14×10×6), 但 45° 平板必须覆盖整个光束直径 ⇒ "
    "任何左右分光构型下平板的竖向投影 ≥ 光束直径 ⇒ ★**修正后三档 T=18/21/23 全废**★) ⇒ 只报归 main ★\n"
    "· ★**ISS-219 交卷明写**: C-7 的唯一前置是「镜框上沿**可外露**的集热面面积能不能做到 120×30 = 3600 mm² (波导压框 / 摄像头 / 装饰件会遮)」⇒ ★**这条前置结构侧自己能算** "
    "(★它自己的几何★) ⇒ 不该继续挂在 main 身上变成阻塞 ★\n"
    "· ⇒ ★**三条都停在「只报」状态, 没有一条落成可执行规格** ⇒ ★**本单是第 3 轮** ★\n"
    "· ⇒ ★**本单是三个总工名额里唯一能推进的一条结构侧活** (★6 个 PCB 类 FAIL 仍按老板 2026-11-11 10:07 口径排队等原理图定稿, 一个没派★) ★\n\n"
    "★★**交付物 (4 件, 少一件即无效) ★★\n"
    "① ★**落表后的结构口径记录** (★建议落在 `MECH/CENTER_CAVITY_REBALANCE_V3.md`★) ⇒ 逐条 (C-6 / C-7 / C-8 → 改了哪个文件的哪一节 → 改前/改后字面值 → "
    "算式与输入 → 证据等级 → 若不可行则降级路径) ⇒ ★**每条都要有结论, 不许留「待定」** ★\n"
    "② ★**C-6 落地**: 把分光件规格 ★**平板 11×11×1.5 (对角 15.56 ≥ 严格口径 15.39) + 转向棱镜 2× 9×9×5**★ / 体积 0.9697 cc / W4 3.68-7.36 g / FOV 折减 2.63% "
    "落到 ★**`MECH/MECH_BUDGET.md` §1.3 M6 (替掉旧的 14×10×6 / 0.79cc / 3-6g 那几行) + `MECH/ENDPOINT_METAL_PATH_MASS_TEMPLATE.md` + 打印包若含 M6** ★\n"
    "③ ★**C-8 自己实算**: 用 45° 平板的★**竖向投影**关系 + 光束直径 8.885 mm + 平板对角 15.39/15.56 mm ⇒ 算出 t_s 该取多少 (★三个候选值都算, 选一个并说明理由★) ⇒ "
    "★**重算三档 T=18/21/23 的后果** (★若三档全废 ⇒ 就写「全废」+ 给出能活的那档或降级路径, 不许把旧数留着✓★) ⇒ ★**同步 `MECH/verify_budget.py` / `MECH/cavity_recalc_check.py` 的对应常量与门禁锚点** ★\n"
    "④ ★**C-7 自己实算**: 对照波导压框 / 摄像头 / 装饰件占位 ⇒ 给出「镜框上沿**实际可外露**的净集热面积」的值 (★[推算] 或 [实测] 标明★) ⇒ "
    "★**能不能做到 3600mm² 给明确结论** ★ ⇒ ★**做不到就给降级路径** (★ISS-219 已列: (a) 铝制集热背板 120×30×1.x · (b) 功耗降到 ≤ 0.415 W · (c) 端件整条金属化 11.3-22.7 g 不可接受 —— "
    "★这三条必须给量化对照, 不许只说「不可接受」★) ⇒ ★**不得触碰 `DECISION_PENDING_2026-11-16.md` (那是老板的页面)** ★\n"
    "⑤ ★**机器门禁扩项**: `MECH/cavity_recalc_check.py` 加断言 (★C-6 规格不许漂回 14×10×6 · C-8 的 t_s 与三档 T 自洽 · C-7 的结论有据★) + 反向用例 ⇒ ★**改坏必红** ★\n"
    "⑥ ★**交接单 `HANDOFF/2026-11-16_mech-lead_ISS222_C6C7C8落地.md`** (★B1~B6 六块齐全★) + ★**分片 `state/fragments/mech.yaml` (★必须走 `python3 state/frag_write.py` 原子写★)** ★\n\n"
    "★★**边界 (★违反一条即本单无效★) ★★\n"
    "· ★**不许改** `HW/` 下任何文件 / ★**不许碰 PCB 布线 / 布局 / 板框** (★老板 2026-11-11 10:07 口径★) ★\n"
    "· ★**不许改判据阈值** (★皮肤 43 °C / 端件 60 °C / cavity_req 4.50 / CRIT 0.60 / cav_v 38.00 / duct_v 6.00 / 板框四数 一个不许动★) ★\n"
    "· ★**不许预扣 `MECH/MECH_BUDGET.md` §3 的现有重量** (★口径 ≠ 质量; 端件金属化质量仍待 u8 ⇒ 只进模板, 不进 §3 合计★) ★\n"
    "· ★**不许替老板拍** u8 / M6 落地取舍 / 整机屏路线 / 波导归属 / FOV / 板长 ⇒ ★**只报给 main** ★\n"
    "· ★**不许改** `state/issue_log.yaml` / `PROJECT_TRACKER.md` §0 / `DECISION_PENDING_2026-11-16.md` / `state/outbox/` / 别人的分片 / "
    "`MECH/hinge_usb_check.py` / `MECH/service_port_check.py` / `MECH/hw_cross_review_check.py` / `MECH/display_biosafety_v2_check.py` / `MECH/check_demo_struct_truth.py` ★\n"
    "· ★**实物 [实测] = 0 条** (★本机跨网段不可达 / 无切片器 / 无量具 ⇒ 打印件收缩比等仍 [0数据]★) ⇒ 标 [实测] 的只允许是「本机脚本 / 本机文件实读」 ★\n"
    "· ★**零外发** (★不发邮件 / 询价 / 问询 / 采购★) ⇒ 缺口一律【自己网上查】+ 标证据等级 + ★**查不到必须写降级方案** (★如 PA-CF 收缩比 ⇒ 降级取官网补偿公式★) ★\n"
    "· ★**不许自签 issue_log** (★status 留给 main 落 verified★) ★\n\n"
    "★★**交卷前必须实跑并把输出原样贴进回复 (★命令都已实测存在★) ★★\n"
    "```\n"
    "python3 MECH/cavity_recalc_check.py             # rc=0 (17/17 或更多)\n"
    "python3 MECH/cavity_recalc_check.py --selftest  # rc=0 (反向用例全抓到)\n"
    "python3 MECH/verify_budget.py                    # rc=0 (★充电耗散仍 = buck 口径, 阈值一个没松★)\n"
    "python3 MECH/verify_budget.py --selftest         # rc=0\n"
    "python3 MECH/check_demo_struct_truth.py          # rc=0 (20/20 组检查通过 · FAIL 0 组)\n"
    "python3 MECH/print/verify_pack.py                # rc=0 (Rev A 基线未变红)\n"
    "python3 MECH/print/verify_pack_revb.py           # rc=0 (Rev B 基线未变红)\n"
    "python3 state/merge.py && python3 state/gate_check.py # rc=0 且 【Q1 交付齐备率】 18/18\n"
    "```"
)

NEW_ISSUES = [
    {
        "id": "ISS-220",
        "title": TITLE_220,
        "severity": "high",
        "source_blocker": "ISS-217",
        "desc": DESC_220,
        "owner": "hw-lead",
        "task_brief": BRIEF_220,
        "note": (
            "2026-11-16 02:2x 队列自动派活 job (fb67af40) 新开 ★**依据 = ISS-217 交卷件自己的第一行「这是【作业包】, 不是执行记录 ⇒ 网表/脚表/板/生成器一个字节都没改」** "
            "⇒ ★**规格侧三轮 (ISS-211/ISS-214/ISS-217) 已到头 ⇒ 主线 (老板 2026-11-11 10:07「先解决原理图绘制的问题」) 要的下一步是【落表】** ★\n"
            "★**依据 = ISS-217 交卷里的 6 条待裁 V-1~V-6 一条没代拍** ⇒ ★**本单只落「不依赖这 6 条」的条目, 依赖的一律 BLOCKED** "
            "(★V-4 R_ILIM 档位已在 `DECISION_PENDING_2026-11-16.md` §3 作为老板待拍项★) ★\n"
            "★**依据 = ISS-215 交卷查清「demo 的 60ms 预算全是整机脚本减出来的」(2-lane vs 4-lane 常量不适用)** ⇒ ★**落表必须钉住「不许拿整机常量扣 demo 账」** ★\n"
            "★**本单属原理图主线内部活, 不碰 PCB 布线/布局/板框 (老板 10:07 口径) ⇒ 可派** ★\n"
            "★**hw-lead 名额的上一条 ISS-217 已于本轮 02:2x 落 verified ⇒ 名额空出来 ⇒ 本单是第 5 轮** ★"
        ),
    },
    {
        "id": "ISS-221",
        "title": TITLE_221,
        "severity": "high",
        "source_blocker": "ISS-215",
        "desc": (
            "★**ISS-212 已把 demo 屏规格钉死 (480×640 / 2-lane / 无 DCS / I2C_B ≤ 100 kHz)**, ★**ISS-215 (11-16 01:5x 交卷, 本 job 02:2x 已落 verified) 把显示侧口径重锚到 demo**, "
            "并查清两件事: ① ★**10.09 ms 是「显示输出侧总额上限」, 与分辨率无关** (依据 `HW/e2e_budget_rk3572.py` 的 `T_FIXED_OTHER = 31.00 # 与显示分辨率无关的部分` + "
            "`display_out_max_for()`) ② ★**判据被算严的根因只有一处 = 用整机的 TX 下限 7.776 去扣 demo 的预算 (倍率 3.36×)**, 与 ISS-212 Q-5「余量 2.32→7.79」逐位吻合 ★ "
            "★**但 demo 那侧至今没有一个自己的预算真源**: 整机那本 `HW/e2e_budget_rk3572.py` 的 DSI 带宽常量是 **4-lane @ 2.0 Gbps × 80%**, 对 2-lane 的 demo 屏不适用 ⇒ "
            "⇒ 现在 demo 的每一个预算数都是「整机脚本减出来的」⇒ ★**同一个坑会被再咬一次** (换屏/改分辨率/改 lane 数时, 没人拦得住) ⇒ 本单把 demo 预算真源补上 ★ "
            "★**外加 ISS-215 交卷点名的遗留分叉**: `SW/RKNN_BENCH.md` §4.1 L273 的 S9 注记仍是整机原文, 与 `SW/tools/rknn_bench.py` L258 的 demo 口径注记分叉 (★S9 = 3.0 这个数值两边都没动, 只是措辞分叉★) ★ "
            "★**零外发** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★)"
        ),
        "owner": "sw-lead",
        "task_brief": BRIEF_221,
        "note": (
            "2026-11-16 02:2x 队列自动派活 job (fb67af40) 新开 ★**依据 = ISS-215 交卷里 need「demo 口径 (2-lane@480×640) 目前没有对应的预算脚本 —— 整机那本 `HW/e2e_budget_rk3572.py` 的 "
            "DSI 带宽常量是 4-lane@2.0Gbps×80%, 对 2-lane demo 屏不适用」** ⇒ ★**这是软件/时序侧的真源缺口, 不是文档缺口** ⇒ 本单建 demo 预算真源 + 机器断言「判据链不许再引用整机常量」 ★\n"
            "★**依据 = ISS-215 交卷的遗留分叉**: `SW/RKNN_BENCH.md` §4.1 L273 的 S9 注记仍是整机原文 ⇒ 本单一并收口 (★只许改那一行注记, S9 = 3.0 数值不许动★) ★\n"
            "★**本单属软件/时序侧内部活, 不碰 PCB 布线/布局, 不碰 HW/★ ⇒ 可派** ★\n"
            "★**sw-lead 名额的上一条 ISS-215 已于本轮 02:2x 落 verified ⇒ 名额空出来 ⇒ 本单是第 6 轮** ★"
        ),
    },
    {
        "id": "ISS-222",
        "title": TITLE_222,
        "severity": "high",
        "source_blocker": "ISS-219",
        "desc": (
            "★**ISS-219 (11-16 02:0x 交卷, 本 job 02:2x 已落 verified) 交卷里那三条「只报不改、已登记 need 给 main」的冲突至今只停在「只报」状态** ⇒ 本单把它们落进结构真源 ★\n"
            "· ★**C-6**: 分光件按 A_e ≤ 62 mm² 眼盒口径放大 (★平板 11×11×1.5 · 对角 15.56 ≥ 严格口径 15.39; 转向棱镜 2× 9×9×5 —— 8×8×5 装不下 8.885 光束★) "
            "/ 体积 0.79 → 0.9697 cc / W4 3-6 → 3.68-7.36 g / FOV 折减 2.63% ⇒ ★**要替换 `MECH/MECH_BUDGET.md` §1.3 M6 的旧行 (14×10×6 / 0.79cc / 3-6g)** ★\n"
            "· ★**C-8 (ISS-219 自己查出的新冲突)**: `t_s=6.0` 取自 §1.3 M6 包络第三维, 但 45° 平板必须覆盖整个光束直径 ⇒ 竖向投影 ≥ 光束直径 ⇒ ★**修正后三档 T=18/21/23 全废** ⇒ "
            "★**结构侧自己实算 t_s 并重算三档** ★\n"
            "· ★**C-7**: 面板 468 mW vs 腔体 50 °C 红线 ⇒ 结论已翻转为「瓶颈是集热面面积」 (d=15 需 ≈2628 mm² vs 端件 600-800 mm²) ⇒ ★**唯一前置「镜框上沿可外露 3600 mm² 能不能做到」结构侧自己能算** "
            "(★波导压框 / 摄像头 / 装饰件占位★) ⇒ ★**做不到就给降级路径的量化对照** ★\n"
            "★**本单不许改 `HW/` 下任何文件 / 不许碰 PCB 布线布局 / 不许改判据阈值 / 不许预扣 §3 现有重量 (端件金属化质量待 u8)** ⇒ ★**零外发** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★) ★"
        ),
        "owner": "mech-lead",
        "task_brief": BRIEF_222,
        "note": (
            "2026-11-16 02:2x 队列自动派活 job (fb67af40) 新开 ★**依据 = ISS-219 交卷里的 3 条 need** "
            "(★C-8 轴口径 / C-7 集热面 3600mm² 可行性 / M6 落地裁★) ⇒ ★**其中 C-7、C-8 的前置结构侧自己能算 ⇒ 不该继续挂在 main 身上变成阻塞** ★\n"
            "★**本单属结构侧内部活, 不碰 PCB 布线/布局/板框 (老板 10:07 口径) ⇒ 可派** ★\n"
            "★**mech-lead 名额的上一条 ISS-219 已于本轮 02:2x 落 verified ⇒ 名额空出来 ⇒ 本单是第 7 轮** ★\n"
            "★**边界**: 不改 §0 锁死表 · 不写任何子总工的分片 · 不发信 · 网表/脚表/板/原理图/BOM 一个字节未动 ★"
        ),
    },
]


def main():
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        with open(LOG, encoding="utf-8") as f:
            log = yaml.safe_load(f)
        issues = log["issues"]
        by_id = {it["id"]: it for it in issues}

        # ① 落 verified
        for iid, (vres, vdate) in VERIFY.items():
            hit = by_id.get(iid)
            if hit is None:
                print("⚠ %s 不存在 ⇒ 跳过" % iid)
                continue
            if hit.get("status") == "verified":
                print("⚠ %s 已是 verified ⇒ 幂等跳过" % iid)
                continue
            if hit.get("status") != "fixing":
                print("⚠ %s status=%s (不是 fixing) ⇒ 不动" % (iid, hit.get("status")))
                continue
            hit["status"] = "verified"
            hit["fixed_at"] = TODAY
            hit["verify_date"] = vdate
            hit["verify_result"] = vres
            hit["fix_ref"] = FIX_REF.get(iid) or hit.get("fix_ref")
            hit["note"] = (hit.get("note") or "") + NOTE_TAIL
            print(" - %s fixing → verified (main 独立复核通过)" % iid)

        # ② 新开
        for spec in NEW_ISSUES:
            iid = spec["id"]
            if iid in by_id:
                print("⚠ %s 已存在 ⇒ 幂等跳过" % iid)
                continue
            new = {
                "id": iid,
                "title": spec["title"],
                "severity": spec["severity"],
                "source_blocker": spec["source_blocker"],
                "desc": spec["desc"],
                "owner": spec["owner"],
                "reporter": "main",
                "raised": TODAY,
                "due": DUE,
                "status": "open",
                "external": False,
                "need_keys": [],
                "fix_ref": None,
                "verify_by": "main",
                "verify_result": None,
                "verify_date": None,
                "note": spec["note"],
                "task_brief": spec["task_brief"],
                "dispatched_at": None,
            }
            issues.append(new)
            print(" + 新开 %s → %s (status=open, 等 advance.py --apply 落 fixing 再 spawn)" % (iid, spec["owner"]))

        shutil.copy2(LOG, BAK)
        tmp = LOG + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)
        os.replace(tmp, LOG)
        fcntl.flock(lk, fcntl.LOCK_UN)
    print("备份: %s" % BAK)


if __name__ == "__main__":
    main()
