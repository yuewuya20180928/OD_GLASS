#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20261116_1720_verify243_244_open245_246_247.py
★main (moli) · 2026-11-16 17:2x (cron 775d9893 继续执行后继计划)★

★★**本脚本做三件事 (★全部基于 main 本轮自己实跑, 不抄任何交卷报告★)** ★★
① ★**ISS-243 (hw-lead) / ISS-244 (sw-lead) 复验落 verified** —— 两条的会话都**已结束** (status=done),
   但 issue_log 里还挂着 `fixing` ⇒ ★**advance.py 的「一个 agent 同时只允许一个在飞任务」锁被这两个僵尸
   `fixing` 占着 ⇒ internal 段空 ⇒ 三个总工一个都派不出去** ⇒ 本脚本先复验 + 落 verified 释放名额 ★
② ★**新开 3 条内部活 (★全部在「原理图/网表侧」主线内, 一条 PCB 布线/布局类都没有★)** ★
③ ★**零落表 (★真盘 md5 一个字节都不动★)** ⇒ ★**不会与同批的重锚活互相打架** ★

★★**为什么不开「F1 直接落表」而只开「作业包 (沙盒)」★** ★★
· ISS-242 F1 (C_VBUS_OUT/C_VBUS_GND 的 node2 写错) 改的是 `state/gen_netlist.py` L369/L381 ⇒ **会改网表 md5** ★
· ★**同批再派两条「重锚」活 ⇒ 重锚锚的是【重锚那一刻】的 md5 ⇒ 而落表可能落在重锚之后 ⇒ 锚点当场又过期** ★
  ⇒ ★**本轮只出作业包 (沙盒实跑, 真盘零写入) ⇒ 等老板拍完 A1/A2/A3, 下一批一次落** ★
"""
import os
import shutil

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
LOG = os.path.join(HERE, "issue_log.yaml")
BAK = LOG + ".bak_20261116_1720_verify243_244_open245_246_247"
TODAY = "2026-11-16"

# ================================================================================
# ① 复验落表: ISS-243 / ISS-244
# ================================================================================
VERIFY_243 = (
    "★main (moli) 2026-11-16 17:0x~17:2x **独立实跑复验** (★不抄交卷报告★) ⇒ **落 verified** ★\n"
    "· ★**门禁**: `python3 HW/check_iss243_cregn.py` ⇒ **rc=0 · 8/8 PASS** (C1~C8) · "
    "`--selftest` ⇒ **rc=0 · 8/8 反向用例全过** (★每条都自证「变红集合 = 期望集合, 其余仍绿」★)\n"
    "· ★**落表内容亲核 (★main 自己 grep 盘上文件★)**: `HW/netlist_v1.csv` L44/L45 = 「4.7µF ±10% (10V)」 + "
    "opn `GRM21BR71C475KA73L` · `HW/netlist_v1_pins.csv` L132/L133 同值 · `HW/BOM_v1.csv` L43 = "
    "「4.7µF ±10% (10V)」/ 0805 / `GRM21BR71C475KA73L` ⇒ ★**三处齐, 无第四处遗留 1µF** ★\n"
    "· ★**受保护 md5**: 板 `611b869e…` ★**逐字节不变** ★ · `.kicad_pro` `3e504d2b…` ★**逐字节不变** ★ ⇒ "
    "★**板侧零改动** (★`C_REGN` 的 board 列 = `CHG_BOARD` ⇒ **它根本不在 demo 主板 `demo_mainboard.kicad_pcb` 上** "
    "⇒ main 实跑 `grep -n C_REGN HW/PCB/demo_mainboard.kicad_pcb` = **0 命中** ⇒ ★**不产生网表↔板封装不一致**★) ★\n"
    "· ★**基线未动**: `check_netlist_selfconsistency.py --expect-resolved` ⇒ 仍 **18 条未落表** (★与 07:2x/09:3x 两次 "
    "独立复核逐位一致 ⇒ **一个 V 值都没落**★) · `--selftest` ⇒ **21/21** · `check_netlist` / `check_netlist_pins` / "
    "`check_sch_erc` (ERC=0) / `check_sch_pinfull` ⇒ 全 rc=0 · `check_netlist_contradiction_r3` ⇒ rc=1 **恰 3 条** "
    "(★= ISS-242 那 3 条, 与本单无关★) · `check_part_selection_matrix` ⇒ rc=0 · `merge.py` + `gate_check.py` ⇒ rc=0 (Q1 18/18)\n"
    "· ★**★本单引发的下游后果 (★main 本轮实跑, 铁律: 后果必须留痕, 不许装作没有★)**: ISS-243 落表把网表/脚表/BOM 的 md5 "
    "从 `34132f7e…`/`b21b743a…`/`c195a117…` 换成 `611c3ba3…`/`ef436a37…`/`2a730574…` ⇒ ★**SW 侧与 MECH 侧的 §1 锚点当场过期** ⇒ "
    "`SW/tools/check_demo_panel_spec.py` **rc=1 (R6 两条红)** · `SW/tools/timing_check.py` **rc=1 (69/71)** · "
    "`MECH/check_demo_struct_truth.py` **rc=1 (21/23, G5b/C21 两组红)** ⇒ ★**已分别开 ISS-245 (sw-lead) / ISS-246 (mech-lead) "
    "按 H-1 流程重锚** ★\n"
    "· ★**边界**: 零外发 (一次 curl 都没发) · 实物 [实测] = 0 条 (★本机无板; 这里的「实测」= 文件/网表实读 + 脚本实跑★) · "
    "没碰 PCB 布线/布局 · 没写别人分片 · 没自签 issue_log (★本行就是 main 的签★)"
)

VERIFY_244 = (
    "★main (moli) 2026-11-16 17:1x~17:2x **独立实跑复验** (★不抄交卷报告★) ⇒ **落 verified** ★\n"
    "· ★**门禁**: `python3 HW/check_part_selection_gaps.py` ⇒ **rc=0 · 7/7 PASS** (C0~C6) · `--selftest` ⇒ "
    "**rc=0 · 8/8 反向用例全过** (★每条打印「变异落地 / 目标那条变红 / 其余仍绿」三项自证★)\n"
    "· ★**交卷件在盘**: `HW/PART_SELECTION_GAPS_CLOSEOUT.md` (84.6 KB) + `HANDOFF/2026-11-16_sw-lead_ISS244_*.md` (24.1 KB, B1~B6 齐)\n"
    "· ★**本单自曝的并发事实 (★main 核对无误★)**: sw-lead 自查期间 (11-16 15:45:45) 网表/脚表/BOM 被 **ISS-243 的落表批次**改过 ⇒ "
    "`C_REGN` 当场闭合 ⇒ 本单把件数控写成**双源** (★登记范围 22 = ISS-241 矩阵基准块 `expected_refs` / 当前待落 21 = BOM 实跑★) ⇒ "
    "★**main 实跑确认**: 盘上 `HW/BOM_v1.csv` 的 `C_REGN` 行 = 「4.7µF ±10% (10V)」+ opn 已填 ⇒ ★**登记 22 / 待落 21 = 属实** ★\n"
    "· ★**政策符合性 (★老板 2026-11-12 02:02「不再发信, 全靠自己查资料」★)**: 收口页 10 条缺口**零条**挂「等回复/等原厂回信」"
    "⇒ 门禁 C4 实跑通过 ⇒ ★**每条要么带官方出处, 要么写清降级方案** ★\n"
    "· ★**只出依据一条没代拍**: G-1 (Q_PG 源漏两种写法的电学后果都算出来: 写法A VGS=−4.2V 导通自洽 / 写法B PG 高低都关 ⇒ 开机路径彻底不通) · "
    "G-5 (1mA 工作点只剩 20mA 标称亮度的 4.8%~7.2% ⇒ 暗 14~21 倍) · G-10 (官方公式 V_IT=(1+R1/R2)×0.405V, R1+R2=4MΩ + 三档 E96 候选) · "
    "G-3/G-4 (业界 = 差分对正负两根都要护) ⇒ ★**四条全部登记成待拍项, main 一条没代拍** ★\n"
    "· ★**基线未动**: `--expect-resolved` 仍 18 条 · `check_part_selection_matrix` rc=0 · `merge.py` + `gate_check.py` rc=0\n"
    "· ★**边界**: 零外发 · 实物 [实测] = 0 条 · 没碰 PCB 布线/布局 · 没写别人分片"
)

# ================================================================================
# ② 新开 3 条内部活
# ================================================================================
TITLE_245 = (
    "★★[主线内·SW 侧·跨域重锚·内部活] ★★ISS-243 落表把网表/脚表 md5 换掉 ⇒ **SW 侧 §1 锚点当场过期** ⇒ "
    "`SW/tools/check_demo_panel_spec.py` rc=1 (R6 两条红) + `SW/tools/timing_check.py` rc=1 (69/71) ⇒ **按 H-1 流程重锚**"
)

DESC_245 = (
    "★main 2026-11-16 17:0x~17:2x **自己实跑**核出来的 (★不是抄任何交卷报告★) ★\n"
    "★**① 病灶 (main 实跑, 逐条可复现)**: ★\n"
    "· `python3 SW/tools/check_demo_panel_spec.py` ⇒ ★**rc=1** · 「❌ ISS-212 demo 显示侧口径门禁: 2 项不通过」★\n"
    "  · ★**R6 盘上真源 md5 `HW/netlist_v1.csv` = `611c3ba3db3dc7de7213063375b96d01` ≠ 锚点登记 `34132f7e40a241e1fae1476be0eafbd5`** ★\n"
    "  · ★**R6 盘上真源 md5 `HW/netlist_v1_pins.csv` = `ef436a37412ac9b6eac3c9f41f1edca4` ≠ 锚点登记 `b21b743a7702d30729f0d653c15392df`** ★\n"
    "· `python3 SW/tools/timing_check.py` ⇒ ★**rc=1 · SELFTEST 69/71 通过** ⇒ ★**掉的 2 条正是同源的两条 md5 锚点断言** ★\n"
    "★**② 根因 (不是「真源被换了」, 是【合法落表后的锚点过期】)**: ★\n"
    "· ★**ISS-243 (hw-lead) 于 2026-11-16 15:45 合法落表** (★`C_REGN` 1µF → 4.7µF ±10% (10V), 官方值, 无需拍板★) ⇒ "
    "网表/脚表/BOM 三个文件被重生成 ⇒ md5 全变 ★\n"
    "· ★**真源没被动过**: 板 `611b869e…` 与 `.kicad_pro` `3e504d2b…` ★**逐字节不变** ★ ⇒ ★**这是「上游合法落表 ⇒ 下游锚点过期」"
    "的教科书案例, 不是缺陷** ★\n"
    "· ★**落表凭据齐全 (★C21 判据要的 4 项都在同一处★)**: `HW/SCHEMATIC_LANDING_V1_LANDED.md` §16 (★单号 `ISS-243` + "
    "文件名 + 新旧 md5 + 改前改后逐行★) ⇒ ★**C21 (落表台账绑定) 这一侧是绿的, 红的只是「锚点数字」** ★\n"
    "★**③ 修法 = H-1 重锚 (★ISS-223 → ISS-233 → ISS-229 已有 3 跳先例★)**: ★\n"
    "· ★**改 `SW/SW_MD5_BASELINE_LEDGER.md` §1 锚点那两条的 4 个字段**: `md5` → `611c3ba3db3dc7de7213063375b96d01` (网表) / "
    "`ef436a37412ac9b6eac3c9f41f1edca4` (脚表) · `prev_md5` → 上一跳的值 (`34132f7e…` / `b21b743a…`) · `by` → `ISS-243` · "
    "`landed_at` → 落表时刻 (★以落表台账 §16 登记的时刻为准, 别自己编★) ★\n"
    "· ★**追加一条「已修复 (留痕)」行 (★本表是追加式留痕账 ⇒ 历史行一个字不改, 与 §2 S-03 同口径★)** ⇒ ★**第 4 跳** ★\n"
    "· ★**判据逻辑一个字不许动** ★**(--skip-md5 不许设成默认跳过)** ⇒ ★**R6 的 6 条判据 / R7 的判据逻辑原样保留** ★\n"
    "· ★**HW/ 下 0 字节写入** (★你只写 SW 台账 + `state/fragments/sw.yaml`★) ★\n"
    "★**④ 本单【不许落表】**: ★**网表/脚表/BOM 一个字都不许改** (★本轮的重锚目标就是「锚点 = 盘上真值」, 落表会把锚点再顶过期★) ★"
)

BRIEF_245 = """★★**目标 (★内部活·不是 PCB 布线/布局类·不是老板级拍板★)**: 把 ★**SW 侧 §1 锚点重锚到 ISS-243 落表后的盘上真值**★ ⇒ ★**把 `check_demo_panel_spec.py` 从 rc=1 拉回 rc=0、`timing_check.py` 从 69/71 拉回 71/71**★ ⇒ ★**零落表 · 零外发 · HW/ 目录 0 字节写入**★

★★**① 病灶 (★main 2026-11-16 17:0x~17:2x 自己实跑, 不是推测★)** ★★
· `python3 SW/tools/check_demo_panel_spec.py` ⇒ ★**rc=1** · 「❌ ISS-212 demo 显示侧口径门禁: **2 项不通过**」
  · R6 盘上真源 md5 `HW/netlist_v1.csv` = `611c3ba3db3dc7de7213063375b96d01` ≠ 锚点登记 `34132f7e40a241e1fae1476be0eafbd5`
  · R6 盘上真源 md5 `HW/netlist_v1_pins.csv` = `ef436a37412ac9b6eac3c9f41f1edca4` ≠ 锚点登记 `b21b743a7702d30729f0d653c15392df`
· `python3 SW/tools/timing_check.py` ⇒ ★**rc=1 · SELFTEST 69/71 通过** (★掉的 2 条 = 同源的两条 md5 锚点断言★)

★★**② 根因: 这是【上游合法落表后的锚点过期】, 不是「真源被换」★** ★★
· ★**ISS-243 (hw-lead) 2026-11-16 15:45 合法落表** (`C_REGN` 1µF → 4.7µF ±10% (10V), ★TI 官方硬要求, 无需拍板★) ⇒ 网表/脚表/BOM 被重生成 ⇒ md5 全变 ★
· ★**板 `611b869e…` + `.kicad_pro` `3e504d2b…` 逐字节不变** ⇒ ★**真源没被动过** ★
· ★**落表凭据齐全**: `HW/SCHEMATIC_LANDING_V1_LANDED.md` §16 (★单号 + 文件名 + 新旧 md5 + 逐行改前改后★) ⇒ ★**C21 那一侧是绿的, 红的只是锚点数字** ★

★★**③ 修法 = H-1 重锚 (★ISS-223 → ISS-233 → ISS-229 已有 3 跳先例, 你走第 4 跳★)** ★★
· ★**改 `SW/SW_MD5_BASELINE_LEDGER.md` §1 锚点里那两条的 4 个字段**: `md5` / `prev_md5` / `by` / `landed_at` ★
  · 网表: `md5` = `611c3ba3db3dc7de7213063375b96d01` · `prev_md5` = `34132f7e40a241e1fae1476be0eafbd5` · `by` = `ISS-243` · `landed_at` = ★**以落表台账 §16 登记的时刻为准, 别自己编** ★
  · 脚表: `md5` = `ef436a37412ac9b6eac3c9f41f1edca4` · `prev_md5` = `b21b743a7702d30729f0d653c15392df` · `by` = `ISS-243` · `landed_at` = 同上 ★
· ★**追加一条「✅ 已修复 (留痕)」行** (★本表是【追加式】留痕账 ⇒ **历史行一个字不改** ★ ⇒ 改历史 = 改事实 = 禁止★) ⇒ 记清: 跳数 / 谁改的 / 哪个单号 / 新旧 md5 / 复现命令 ★
· ★**判据逻辑一个字不许动** ★**(--skip-md5 不许设成默认跳过)** ⇒ ★**R6 的 6 条判据 / R7 的判据逻辑原样保留** ★

★★**④ 验收标准 (★全部要你实跑并把原样输出贴进交卷单★)** ★★
1. `python3 SW/tools/check_demo_panel_spec.py` ⇒ ★**rc=0** ★
2. `python3 SW/tools/timing_check.py` ⇒ ★**rc=0 · 71/71** ★
3. `python3 SW/tools/check_demo_panel_spec.py --selftest` ⇒ ★**rc=0** (★反向用例一条不许删★)
4. `python3 SW/tools/timing_check.py --selftest` ⇒ ★**rc=0** ★
5. ★**反向自证 (必做)**: 在 `/tmp` 沙盒里把锚点改回旧 md5 (`34132f7e…`) ⇒ ★**R6 那两条必须重新变红** ⇒ 装回去 ⇒ 又绿 ⇒ ★**证明这条判据不是摆设** ★
6. `python3 state/merge.py && python3 state/gate_check.py` ⇒ ★**rc=0** ★
7. ★**HW/ 下 5 个受保护 md5 逐字节不变**: 网表 `611c3ba3…` · 脚表 `ef436a37…` · BOM `2a730574…` · 板 `611b869e…` · `.kicad_pro` `3e504d2b…` ★
8. ★**分片走 `python3 state/frag_write.py --agent sw-lead ...` 原子写** (★不许手改 yaml★) ★

★★**⑤ 边界 (★逐条自证★)** ★★
· ★**零落表**: 网表/脚表/BOM **一个字都不许改** ★** (★本轮重锚的目标就是「锚点 = 盘上真值」★)
· ★**零外发** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★) ⇒ 缺口一律自己网上查 + 标证据等级 + 查不到写降级方案
· ★**不许碰 PCB 布线/布局/板框** (★板那一趟按老板 11-11 10:07 口径继续排队★) ★
· ★**不许碰 `HW/` 下任何文件** (★只读, 用来核 md5★) ★**不许碰 MECH/ 分片** (★那是 ISS-246 mech-lead 的活★)
· ★**不许改判据逻辑** ★**不许删反向用例** ★**不许把红灯调没** (★改锚点数字是「重锚」, 改判据是「作弊」★)
· ★**不改 `PROJECT_TRACKER.md` §0 锁死表** · ★**不替老板拍板** (★V-2/V-3/V-4 一条没拍★) · ★**`state/issue_log.yaml` 不自改** (★verify 留给 main★)

★★**⑥ 交卷物 (4 件)** ★★
1. ★**`SW/SW_MD5_BASELINE_LEDGER.md`** (§1 锚点 2 条 + 追加第 4 跳留痕行) ★
2. ★**`HANDOFF/2026-11-16_sw-lead_ISS245_SW侧H1重锚第4跳.md`** (★B1 结论摘要 / B2 验收标准自评 / B3 证据分级 / B4 接口取值声明 / B5 验收命令原样输出 / B6 边界审计 —— ★`gate_check.py` 按【标题行】认块, 标题照这 6 个语义写★) ★
3. ★**`state/fragments/sw.yaml`** (★走 `frag_write.py` 原子写: +artifact / +claim (新 md5 + 跳数 + by) / +need (留给 main 的, 如果有)★) ★
4. ★**可选**: 锚点变更前后对照表 (贴在交卷单 B5 后面) ★
"""

TITLE_246 = (
    "★★[主线内·MECH 侧·跨域重锚·内部活] ★★ISS-243 落表把网表/脚表 md5 换掉 ⇒ **MECH 侧 §3.1 锚点当场过期** ⇒ "
    "`MECH/check_demo_struct_truth.py` rc=1 (21/23, G5b/C21 两组红) ⇒ **按 H-1 流程重锚**"
)

DESC_246 = (
    "★main 2026-11-16 17:0x~17:2x **自己实跑**核出来的 (★不是抄任何交卷报告★) ★\n"
    "★**① 病灶 (main 实跑)**: `python3 MECH/check_demo_struct_truth.py` ⇒ ★**rc=1 · 21/23 组检查通过 · FAIL 2 组** ★\n"
    "  (★那 2 组 = 门禁自己标名的 ★**G5b / C21** ★ ⇒ 即「md5 锚点」与「落表台账绑定」这一对★) ★\n"
    "★**② 根因**: ★**ISS-243 (hw-lead) 2026-11-16 15:45 合法落表** (`C_REGN` 1µF → 4.7µF ±10% (10V)) ⇒ "
    "网表/脚表 md5 变 ⇒ ★**MECH/HW_CROSS_REVIEW_TRIAGE.md §3.1 的锚点还停在 `34132f7e…` / `b21b743a…`** ★\n"
    "  ⇒ ★**板 `611b869e…` / `.kicad_pro` `3e504d2b…` 逐字节不变 ⇒ 真源没被动过 ⇒ 这是锚点过期, 不是缺陷** ★\n"
    "★**③ 先例**: §3.1 里已有 R-02 (ISS-223 第 1 跳) + R-03 (ISS-233 并发第 2 跳) ⇒ ★**你走第 3 跳** ★\n"
    "★**④ 修法**: 改 §3.1 锚点那两条的 `md5` / `prev_md5` / `by` / `landed_at` (★`by` = `ISS-243`★) + "
    "追加一条 §3.1 留痕行 ⇒ ★**不许动 G5b / C21 的判据逻辑, 不许删 §2 的 PIN-MISMATCH 行, 不许删 §3.1 的已修复节** ★"
)

BRIEF_246 = """★★**目标 (★内部活·不是 PCB 布线/布局类·不是老板级拍板★)**: 把 ★**MECH 侧 §3.1 的 md5 锚点重锚到 ISS-243 落表后的盘上真值**★ ⇒ ★**把 `MECH/check_demo_struct_truth.py` 从 rc=1 (21/23) 拉回 rc=0 (23/23)**★ ⇒ ★**零落表 · 零外发 · HW/ 目录 0 字节写入**★

★★**① 病灶 (★main 2026-11-16 17:0x~17:2x 自己实跑★)** ★★
· `python3 MECH/check_demo_struct_truth.py` ⇒ ★**rc=1 · 21/23 组检查通过 · FAIL 2 组** ★
· ★**那 2 组 = 门禁自己标名的 G5b / C21** (★即「md5 锚点」+「落表台账绑定」这一对★) ⇒ ★**不是几何/公差栈的问题** ★

★★**② 根因: 上游合法落表 ⇒ 下游锚点过期 (★不是「真源被换」★)** ★★
· ★**ISS-243 (hw-lead) 2026-11-16 15:45 合法落表** (`C_REGN` 1µF → 4.7µF ±10% (10V), ★TI 官方硬要求★) ⇒ 网表/脚表 md5 变 ★
· ★**板 `611b869e…` + `.kicad_pro` `3e504d2b…` 逐字节不变** ⇒ ★**真源没被动过** ★
· ★**落表凭据**: `HW/SCHEMATIC_LANDING_V1_LANDED.md` §16 (★单号 + 文件名 + 新旧 md5 + 逐行改前改后 ⇒ ★**C21 要的 4 项齐全★) ★

★★**③ 先例 (★你走第 3 跳★)**: §3.1 里已有 ★**R-02** (ISS-223 第 1 跳) + ★**R-03** (ISS-233 并发第 2 跳) ★

★★**④ 修法 (★照 R-02 / R-03 的格式, 别自创★)** ★★
· 改 `MECH/HW_CROSS_REVIEW_TRIAGE.md` ★**§3.1 锚点里那两条** 的 `md5` / `prev_md5` / `by` / `landed_at` ★
  · 网表: `md5` = `611c3ba3db3dc7de7213063375b96d01` · `prev_md5` = `34132f7e40a241e1fae1476be0eafbd5` · `by` = `ISS-243` · `landed_at` = ★**以落表台账 §16 登记的时刻为准, 别自己编** ★
  · 脚表: `md5` = `ef436a37412ac9b6eac3c9f41f1edca4` · `prev_md5` = `b21b743a7702d30729f0d653c15392df` · `by` = `ISS-243` · `landed_at` = 同上 ★
· ★**追加一条 §3.1 留痕行 (★追加式 ⇒ 历史行一个字不改★)** ⇒ 记清: 跳数 / 谁改的 / 哪个单号 / 新旧 md5 / 复现命令 ★
· ★**三条不许动的**: ★**G5b / C21 的判据逻辑一个字不许动** ★**§2 第 05 行的 PIN-MISMATCH 行不许删** ★**§3.1 的「已修复 (留痕)」节不许删** ★
  (★这三条都有门禁在守 ⇒ 删了就红★)

★★**⑤ 验收标准 (★全部要你实跑并把原样输出贴进交卷单★)** ★★
1. `python3 MECH/check_demo_struct_truth.py` ⇒ ★**rc=0 · 23/23** ★
2. `python3 MECH/check_demo_struct_truth.py --selftest` ⇒ ★**rc=0 · 14/14** (★反向用例一条不许删★)
3. ★**反向自证 (必做)**: 在 `/tmp` 沙盒里把 §3.1 锚点改回旧 md5 (`34132f7e…`) ⇒ ★**G5b/C21 那 2 组必须重新红** ⇒ 装回去 ⇒ 又绿 ⇒ ★**证明这两组不是摆设** ★
4. `python3 state/merge.py && python3 state/gate_check.py` ⇒ ★**rc=0** ★
5. ★**HW/ 下 5 个受保护 md5 逐字节不变**: 网表 `611c3ba3…` · 脚表 `ef436a37…` · BOM `2a730574…` · 板 `611b869e…` · `.kicad_pro` `3e504d2b…` ★
6. ★**分片走 `python3 state/frag_write.py --agent mech-lead ...` 原子写** (★不许手改 yaml★) ★

★★**⑥ 边界 (★逐条自证★)** ★★
· ★**零落表**: 网表/脚表/BOM/板 **一个字都不许改** ★
· ★**零外发** (★老板 2026-11-11 19:31 + 2026-11-12 02:02★)
· ★**不许碰 PCB 布线/布局/板框** (★板那一趟按老板 11-11 10:07 口径继续排队★) ★
· ★**不许碰 `HW/` 下任何文件** (★只读, 用来核 md5★) ★**不许碰 SW 分片 / SW 台账** (★那是 ISS-245 sw-lead 的活★)
· ★**不许改判据逻辑** ★**不许把红灯调没** ★
· ★**不改 `PROJECT_TRACKER.md` §0 锁死表** · ★**不替老板拍板** · ★**`state/issue_log.yaml` 不自改** (★verify 留给 main★)

★★**⑦ 交卷物 (3 件)** ★★
1. ★**`MECH/HW_CROSS_REVIEW_TRIAGE.md`** (§3.1 锚点 2 条 + 追加第 3 跳留痕行) ★
2. ★**`HANDOFF/2026-11-16_mech-lead_ISS245_MECH侧H1重锚第3跳.md`** (★B1~B6, 标题照 `gate_check.py` 认的 6 个语义写★) ★
3. ★**`state/fragments/mech.yaml`** (★走 `frag_write.py` 原子写★) ★
"""

TITLE_247 = (
    "★★[主线内·原理图/网表侧·内部活] ★★ISS-242 F1 落表作业包 v1 (★**只出作业包 + 沙盒实跑, 真盘零写入**★) —— "
    "`C_VBUS_OUT`/`C_VBUS_GND` 两颗 2 脚电容的 node2 写错 ⇒ 导出后一脚悬空 / 串联对地混在一颗上 ⇒ "
    "★**改法落在 `state/gen_netlist.py` L369/L381 两行** (★真源改法, 不许手改 CSV★)"
)

DESC_247 = (
    "★main 2026-11-16 17:1x **自己实跑 + 逐行读盘**核出来的 (★不是抄任何交卷报告★) ★\n"
    "★**① 病灶 (ISS-242 已交卷、已落 verified; 但 F1 至今【没落表】⇒ 对应门禁仍红)**: ★\n"
    "· ★**网表 4 行, 每颗 2 脚件落进 3 个网**: `HW/netlist_v1.csv` ★**L8** (`C_VBUS_OUT` = FB_VBUS 后级侧) · ★**L9** "
    "(★`node1` 写的是它自己的信号网 `VBUS_5V_F1` ★) · ★**L10** (`C_VBUS_GND` 对地脚) · ★**L11** (★`C_VBUS_OUT` 串联到 "
    "`U_CHG pin1`★) · ★**L12** (★★`node2` 写的是 `C_VBUS_OUT` 而不是 `C_VBUS_GND` ⇒ ★**`C_VBUS_GND` 的一脚在网表里被写成了另一颗器件**★★) ★\n"
    "· ⇒ ★**导出后一脚悬空 / 串联对地混在一颗上** ⇒ ★**这是 ISS-211/214/217「网表自相矛盾」同一族的第 3 轮** ★\n"
    "· ★**当前门禁状态 (main 本轮实跑)**: `python3 HW/check_netlist_contradiction_r3.py` ⇒ ★**rc=1 · 恰 3 条** ★\n"
    "  (★= F1 (本单) + F2 (J_CHG 位号消歧, ★**要位号消歧 ⇒ 牵板那一趟★) + F3 (板侧 DNP 标记, ★**改板文件★**)★) ★\n"
    "★**② 为什么本单【只出作业包, 不落真盘】**: ★\n"
    "· ★**F1 改的是 `state/gen_netlist.py` ⇒ 会改网表 md5** ⇒ ★**若本轮落表, 同一批在跑的 ISS-245 (SW 重锚) / ISS-246 "
    "(MECH 重锚) 锚的就是【落表前】的 md5 ⇒ 锚完当场又过期** ⇒ ★**本轮先出作业包 (沙盒实跑), 等老板拍完 A1/A2/A3, "
    "下一批一次落** ★\n"
    "· ★**ISS-236 的一键落表器 (`state/land_v_values.py`) 已经把 V-2/V-3/V-4 的落表路径铺好** ⇒ ★**F1 应当【并进同一批】落, "
    "而不是单独落一次再重锚一次** ★\n"
    "★**③ 派单里那个错值 (★必须订正, 不许照抄★)**: 上一轮派单写「把 `node2` 改成 `C_VBUS_GND`」⇒ ★**那是错值** "
    "(★ISS-242 自己在沙盒里实跑证明: 那样改照样红★) ⇒ ★**真改法在 `state/gen_netlist.py` L369/L381 两行 (★`node2` 槽混用了两种绑定约定★)** ★\n"
    "★**④ 本单要做的事**: ★**① 自己在沙盒 (/tmp) 跑出真改法并给出【改前 → 改后】逐字字符串 ② 出「落表作业包 v1」"
    "(★含: 改哪一行 / 改前改后逐字 / 影响面 (网表/脚表/BOM/`.net`/SCHEMATIC_V1.md 各变几行) / 新旧 md5 / 复现命令 / 回滚方法★) "
    "③ 出「下一批落表清单 v1」: ★**F1 + V-2/V-3/V-4 的落表顺序与互斥关系 (★谁改哪一行, 有没有撞车★) ④ 自建一个能判「F1 是否已落」的机器门禁 + `--selftest` ⑤ 交卷单 + 分片** ★"
)

BRIEF_247 = """★★**目标 (★内部活·不是 PCB 布线/布局类·不是老板级拍板★)**: 把 ★**ISS-242 的 F1 (网表自相矛盾第 1 条) 做成一份【可直接照着落表的作业包 v1】+ 一份【下一批落表清单 v1】**★ ⇒ ★**★本单【真盘零写入】★** ⇒ ★**零外发** ★

★★**① 病灶 (★main 2026-11-16 17:1x 自己逐行读盘核出来★)** ★★
· ★**`HW/netlist_v1.csv` 里两颗 2 脚电容各落进 3 个网**: ★
  · **L8** = `C_VBUS_OUT` (FB_VBUS 后级侧) · **L9** = ★**`node1` 写的是它自己的信号网 `VBUS_5V_F1`** ★
  · **L10** = `C_VBUS_GND` 对地脚 · **L11** = ★**`C_VBUS_OUT` 串联到 `U_CHG pin1`** ★
  · **L12** = ★★**`node2` 写的是 `C_VBUS_OUT` 而不是 `C_VBUS_GND` ⇒ `C_VBUS_GND` 的一脚在网表里被写成了另一颗器件**★★ ★
· ⇒ ★**导出后一脚悬空 / 串联对地混在一颗上** ★
· ★**当前门禁**: `python3 HW/check_netlist_contradiction_r3.py` ⇒ ★**rc=1 · 恰 3 条** ★
  (★= **F1 (本单)** + F2 (J_CHG 位号消歧 ⇒ ★**要位号消歧, 牵板那一趟**) + F3 (板侧 DNP 标记 ⇒ ★**改板文件**)★) ★

★★**② 为什么本单【只出作业包, 不落真盘】 (★这条是硬约束, 不许自作主张落表★)** ★★
· ★**F1 改的是 `state/gen_netlist.py` ⇒ 会改网表 md5** ⇒ ★**若本轮落表, 同一批在跑的 ISS-245 (SW 重锚) / ISS-246 (MECH 重锚) 锚的就是【落表前】的 md5 ⇒ 锚完当场又过期** ⇒ ★**本轮先出作业包 (沙盒实跑), 等老板拍完 A1/A2/A3, 下一批一次落** ★
· ★**`state/land_v_values.py` (ISS-236 的一键落表器) 已经把 V-2/V-3/V-4 的落表路径铺好** ⇒ ★**F1 应当【并进同一批】落** ★

★★**③ ★★派单里那个错值必须订正 (★不许照抄★)★★** ★★
· 上一轮派单写「把 `node2` 改成 `C_VBUS_GND`」⇒ ★**那是错值** (★ISS-242 自己在沙盒里实跑证明: 那样改照样红★) ★
· ★**真改法在 `state/gen_netlist.py` L369/L381 两行** (★`node2` 槽混用了两种绑定约定★) ⇒ ★**你自己核一遍, 不许抄结论** ★

★★**④ 本单要交的 5 件** ★★
1. ★**落表作业包 v1** (★落进 `HW/SCHEMATIC_LANDING_WORKPACKET_V1.md` 或新建独立作业包文件, 随你, 但要说清★): ★
   · ★**改哪一行 (行号) · 改前逐字 → 改后逐字 (★要能直接 copy 的字符串★) · 影响面: 网表/脚表/BOM/`.net`/`SCHEMATIC_V1.md` 各变几行 · 新旧 md5 · 复现命令 · 回滚方法** ★
   · ★**必须在 `/tmp` 沙盒整树实跑过** (★真盘 5 个 md5 交卷前后逐字节不变★) ⇒ ★**把你沙盒实跑的【改前 → 改后】diff 贴进交卷单** ★
2. ★**下一批落表清单 v1**: ★**F1 + V-2/V-3/V-4 的落表顺序 + 互斥关系 (★谁改哪一行, 有没有撞车★) + 各自的前置条件 (★哪条要先拍板才能落★)** ★
3. ★**机器门禁**: 新建一个能判「**F1 是否已落**」的脚本 + `--selftest` (★≥5 条反向用例, 每条自证「真的改到了目标」★) ⇒ ★**不许挂在 md5 上** (★md5 会随别的批次变★) ⇒ ★**要挂在【语义】上 (★比如: `C_VBUS_GND` 的 `node2` 必须等于它自己的网名★) ★
4. ★**交卷单**: `HANDOFF/2026-11-16_hw-lead_ISS247_F1落表作业包v1.md` (★B1~B6, 标题照 `gate_check.py` 认的 6 个语义写★) ★
5. ★**分片**: `state/fragments/hw.yaml` (★走 `python3 state/frag_write.py --agent hw-lead ...` 原子写★) ★

★★**⑤ 验收标准 (★全部要你实跑并把原样输出贴进交卷单★)** ★★
1. ★**沙盒实跑**: 在 `/tmp` 副本上按你的改法落 ⇒ ★**`python3 HW/check_netlist_contradiction_r3.py` 在沙盒里从 3 条降到 2 条 (★且失败的正是 F1 那条★)** ★
   · ★**沙盒里脚表 md5 逐字节不变 + R3-A1/R3-A2 双绿** (★ISS-242 已实测过这个口径, 你要自己再核一遍★) ★
2. ★**真盘零写入**: 交卷前后真盘 5 个受保护 md5 逐字节不变 (★网表 `611c3ba3…` · 脚表 `ef436a37…` · BOM `2a730574…` · 板 `611b869e…` · `.kicad_pro` `3e504d2b…`★) ★
3. ★**你的新门禁**: 正向 rc=0 + `--selftest` rc=0 (★≥5/5★) ★
4. ★**不碰已有门禁**: `check_netlist_selfconsistency.py` (含 `--expect-resolved` 仍 **18 条**) · `check_netlist` · `check_netlist_pins` · `check_sch_erc` (ERC=0) · `check_sch_pinfull` · `check_netlist_contradiction_r3` (真盘仍 **恰 3 条**) · `check_part_selection_matrix` ⇒ ★**全 rc=0 或保持既有红数不变 (★不许把红灯调没★)** ★
5. `python3 state/merge.py && python3 state/gate_check.py` ⇒ ★**rc=0** ★

★★**⑥ 边界 (★逐条自证★)** ★★
· ★**★真盘零写入★**: 网表/脚表/BOM/板/`.kicad_pro`/`HW/PCB/` 下任何文件 **一个字都不许改** ⇒ ★**沙盒实跑完必须把沙盒清掉, 并把「真盘 md5 前后对照」贴进交卷单** ★
· ★**零外发** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★) ⇒ 查不到就写降级方案, 不许挂「等回复」 ★
· ★**不许碰 PCB 布线/布局/板框** (★板那一趟按老板 11-11 10:07 口径继续排队★) ★**不许碰 F2 (J_CHG 位号消歧) / F3 (板侧 DNP 标记) —— 那两条本单只登记, 不做** ★
· ★**不许碰 SW/MECH 分片与台账** (★那两条是 ISS-245 / ISS-246 的活★) ★
· ★**不许改已有门禁脚本的判据逻辑** ★**不许把红灯调没** ★
· ★**不改 `PROJECT_TRACKER.md` §0 锁死表** · ★**不替老板拍板** (★V-2/V-3/V-4 一条没拍★) · ★**`state/issue_log.yaml` 不自改** (★verify 留给 main★)

★★**⑦ 交卷物 (5 件)** ★★
1. ★**落表作业包 v1** (★含沙盒 diff + 影响面 + 新旧 md5 + 复现命令 + 回滚方法★) ★
2. ★**下一批落表清单 v1** (★F1 + V-2/V-3/V-4 的顺序与撞车分析★) ★
3. ★**机器门禁 + `--selftest`** ★
4. ★**交卷单** (★B1~B6★) ★
5. ★**分片** (★`frag_write.py` 原子写★) ★
"""


def main() -> None:
    with open(LOG, "r", encoding="utf-8") as f:
        log = yaml.safe_load(f)
    issues = log["issues"]

    by_id = {i["id"]: i for i in issues}

    # ---- ① 复验落 verified ----
    for iid, res in (("ISS-243", VERIFY_243), ("ISS-244", VERIFY_244)):
        it = by_id[iid]
        it["status"] = "verified"
        it["verify_by"] = "main"
        it["verify_date"] = TODAY
        it["verify_result"] = res
        it["fix_ref"] = "HANDOFF/2026-11-16_hw-lead_ISS243_C_REGN官方值落表与4条落表前置.md" if iid == "ISS-243" \
            else "HANDOFF/2026-11-16_sw-lead_ISS244_选型缺口自查补全与OPN回填清单.md"

    # ---- ② 新开 3 条 ----
    new = [
        {
            "id": "ISS-245",
            "title": TITLE_245,
            "severity": "high",
            "source_blocker": "ISS-243",
            "source_agent": "main",
            "desc": DESC_245,
            "owner": "sw-lead",
            "reporter": "main",
            "raised": TODAY,
            "due": "2026-11-20",
            "status": "open",
            "external": False,
            "need_keys": [],
            "fix_ref": None,
            "verify_by": "main",
            "verify_result": None,
            "verify_date": None,
            "note": "★main 2026-11-16 17:0x 实跑复验 ISS-243 时发现: 落表把网表/脚表 md5 换掉 ⇒ SW 侧 §1 锚点过期 ⇒ check_demo_panel_spec rc=1 + timing_check 69/71 ★",
            "dispatched_at": None,
            "task_brief": BRIEF_245,
        },
        {
            "id": "ISS-246",
            "title": TITLE_246,
            "severity": "high",
            "source_blocker": "ISS-243",
            "source_agent": "main",
            "desc": DESC_246,
            "owner": "mech-lead",
            "reporter": "main",
            "raised": TODAY,
            "due": "2026-11-20",
            "status": "open",
            "external": False,
            "need_keys": [],
            "fix_ref": None,
            "verify_by": "main",
            "verify_result": None,
            "verify_date": None,
            "note": "★main 2026-11-16 17:0x 实跑复验 ISS-243 时发现: 落表把网表/脚表 md5 换掉 ⇒ MECH 侧 §3.1 锚点过期 ⇒ check_demo_struct_truth rc=1 (21/23, G5b/C21) ★",
            "dispatched_at": None,
            "task_brief": BRIEF_246,
        },
        {
            "id": "ISS-247",
            "title": TITLE_247,
            "severity": "high",
            "source_blocker": "ISS-242",
            "source_agent": "main",
            "desc": DESC_247,
            "owner": "hw-lead",
            "reporter": "main",
            "raised": TODAY,
            "due": "2026-11-20",
            "status": "open",
            "external": False,
            "need_keys": [],
            "fix_ref": None,
            "verify_by": "main",
            "verify_result": None,
            "verify_date": None,
            "note": "★main 2026-11-16 17:1x 实跑: check_netlist_contradiction_r3 仍恰 3 条, F1 未落 ⇒ 出作业包 (沙盒实跑, 真盘零写入) ⇒ 与 ISS-245/246 重锚同批不打架 ★",
            "dispatched_at": None,
            "task_brief": BRIEF_247,
        },
    ]

    for n in new:
        assert n["id"] not in by_id, "ISS already exists: %s" % n["id"]
        issues.append(n)

    shutil.copy2(LOG, BAK)
    with open(LOG, "w", encoding="utf-8") as f:
        yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=10000)

    print("OK: ISS-243/ISS-244 -> verified; ISS-245 (sw-lead) / ISS-246 (mech-lead) / ISS-247 (hw-lead) opened")
    print("backup: %s" % BAK)


if __name__ == "__main__":
    main()
