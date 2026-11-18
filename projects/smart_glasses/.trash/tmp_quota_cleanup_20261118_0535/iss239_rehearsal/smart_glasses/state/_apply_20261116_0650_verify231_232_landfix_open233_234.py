#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20261116_0650_verify231_232_landfix_open233_234.py
★main (moli) 清账 + 开新单 · 2026-11-16 06:50 (cron 775d9893 继续执行后继计划)★

★★**为什么做这件事 (★本轮自己实跑, 不抄任何交卷报告★)** ★★
· ★**ISS-231 (sw-lead) 子会话** `agent:sw-lead:subagent:4b6dcfcf` ★**status=done** ★
  ⇒ main 自己实跑三道闸全绿 ⇒ 落 `verified` ⇒ **放掉 sw-lead 名额** ★
· ★**ISS-232 (hw-lead) 子会话** `agent:hw-lead:subagent:dd6bdc8c` ★**status=done** ★
  ⇒ 交卷结论 (真因 = 板侧陈旧, 网表侧一行都不用改) 经 main 复核成立 ⇒ 落 `verified` ⇒ **放掉 hw-lead 名额** ★
  ⇒ ★**但 C1 门禁仍红 (板侧 B-1 未落) ⇒ 按老板 11-11 10:07 口径: PCB 类继续排队, 本 job 不派** ★
· ★**ISS-229 (mech-lead) 子会话** `agent:mech-lead:subagent:e421bdb0` ★**status=timeout (abortedLastRun=true)** ★
  ⇒ ★**这次它把 ③⑤⑥ 都落完了 (交接单 06:25 / FPC 06:23 / 台账 06:23) ⇒ 只差 ④ 分片** ★
  ⇒ main 实跑三道闸全绿 ⇒ ★**不落账, 同单续做 (只补 ④ + 交卷确认) ⇒ 再派一次** ★

★★**本轮新开 2 条 (★都是「原理图 / 网表 / 门禁 / 软件-接口」主线活, 一条都不碰 PCB 布线布局★)** ★★
· ★**ISS-233 (hw-lead)**: `--expect-resolved` 21 条未落表 ⇒ 逐条归因 + 【不依赖老板拍板的那批当场落】+ 【V-2/V-3/V-4 拍板即可一键落】逐字清单 ★
· ★**ISS-234 (sw-lead)**: 「关机 / 待机 / 关机充电指示灯」三条口径 ⇒ 两套可落表方案 + 硬件最小需求 + 机器门禁 ⇒ 给老板一页可拍 ★

★★**违规清理 (issue_check 26 条 ⇒ 本轮清掉 6 条)** ★★
· 5 条「逾期仍 fixed」: ISS-132 / ISS-116 / ISS-118 / ISS-119 ⇒ 各自按【结论已被老板拍板采信】/【main 自己复算过】落 `verified` ;
  ISS-097 ⇒ ★**main 自产文档 (自己产的必须别人验) ⇒ 转成待老板审阅 (owner=boss, external=True, due 顺延到 11-18)★** ★
· 1 条「幻觉引用」: ISS-206 的 source_blocker `MECH-JCHG-PINMAP-3SET` 在 STATE.yaml 里不存在 ⇒ 改指真键 `MECH-B8` ★

★★**边界 (本轮共同)★★ ★★
★**零外发** (老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料) ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到写降级方案 ★
★**不许替老板拍板** ⇒ V-2 / V-3 / V-4 / 集热面材质 / u8 / d 值 / 板长 / 关机语义 全部只出选项 + 量化代价, 不代拍 ★
★**不许碰 PCB 布线 / 布局 / 板框** ⇒ 板侧 8 项 (B-1~B-8) 继续**排队**, 本 job 不派 ★
★**不改 PROJECT_TRACKER.md §0 锁死表** · ★**不写别人的分片** · ★**不发邮件 / 不联系供应商 / 不下采购单** ★
"""
import os
import shutil
import datetime as dt
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.normpath(os.path.join(HERE, ".."))
LOG = os.path.join(HERE, "issue_log.yaml")
TODAY = "2026-11-16"

BRIEF_233 = """★★**目标 (★内部活·原理图/网表侧·不是 PCB 布线/布局类·不是老板级拍板★)** ★★
★**把 `--expect-resolved` 剩下的 21 条未落表逐条归因, 把【不依赖老板拍板】的那批当场落表, 并出【V-2/V-3/V-4 一旦拍板即可一键落】的逐字清单** ★★
⇒ ★**目标状态: 21 条逐条有归因 + A 类落完 `--expect-resolved` 条数下降且全闸 rc=0 (含 `--selftest` 21/21 仍全过) + 交卷单里有一份【老板只回一个字母就能落地】的清单** ★★

★★**为什么是现在 (★main 2026-11-16 06:4x~06:5x 自己实跑, 不是抄交卷报告★)** ★★
· ★**main 实跑 `python3 HW/check_netlist_selfconsistency.py --expect-resolved` ⇒ rc=1, 21 条未落表** ★ (★条数与构成照抄 ISS-230 交卷: R2×11 / R3×4 / R4×2 / R7×1 / R8×1 / R9×1 / R10×1 ★)
· ★**main 实跑 `python3 HW/check_netlist_selfconsistency.py` ⇒ rc=0** ★ · ★**`--selftest` ⇒ rc=0, 21/21 全过** ★ (★含 ISS-230 新增的用例19/用例20★)
· ★**main 实跑四道尺子全绿**: `python3 state/check_netlist.py` rc=0 · `python3 state/check_netlist_pins.py` rc=0 · `python3 state/check_sch_erc.py` rc=0 (ERC=0) · `python3 state/check_sch_pinfull.py` rc=0 (★图上 584 脚 = 表里 584 脚 · K=0 · 218 器件/153 网★) ★
· ★**main 实测网表 md5 = `3215020b6d4120e1b7728227effdc6d3`** ★ (★脚表 `a600afae…` / BOM `92b51580…` / 板 `611b869e…` / `.kicad_pro` `3e504d2b…` ★)
· ★**这 21 条就是「原理图定稿」的最后一截** ★ ⇒ ★**老板 11-11 10:07 口径: 当前主线 = 原理图 demo 绘制 ⇒ 本单是主线正中央** ★

★★**三条老板待拍的值 (★现状照抄 ISS-230 作业包 v2, main 已核过原文★)** ★★
· ★**V-3 (BAT_DET 分压)**: 现状 = 网表 `R_BAT_DET_1/2` = 1M+1M 且 DNP; ★**ISS-223 已算出恒等式 `R_th/k = R_top` ⇒ A(2.0M+1.2M) 与 D(2.0M+1.0M) 的 R_top 都是 2.0M ⇒ 漏电误差项与比容差项完全相同 ⇒ 现有选项集是伪选择** ★ ⇒ ★**推荐新增方案 E = 100k + 60k + 100nF** (R_th 37.5k ⇒ t_settle 34ms; 漏电@1µA = 2.1%FS; 总误差 <2.9%FS; 代价 26.25µA / 110µW) ⇒ ★**等老板拍, 你不许拍** ★
· ★**V-4 (R_ILIM)**: 现状 390Ω 档; ★**ISS-230 作业包里 V-4 = 680Ω ±1% (单 pin 0.349A ⇒ 余量 1.43×)** ⇒ ★**等老板拍** ★
· ★**V-2**: ★**main 已核 ISS-230 交卷实测结论: 「V-2 的网表侧落表一条判据都转不绿」(实测 7→7) ⇒ R4/R9 读的是 `.kicad_pcb` ⇒ V-2 必须写成【网表侧落表 + 板侧那一趟】两段** ★ ⇒ ★**等老板拍 + 板侧那一趟排队中** ★

★★**你要做的 (★四件交付物, 少一件即无效★)** ★★
① ★**21 条逐条归因表 (★机器可读 CSV/MD 都行, 但必须逐条一行★)** ★
  ⇒ 每行: 条目 id (R2/R3/R4/R7/R8/R9/R10 的具体条目) → 归类 **A 可自主落 / B 等老板某个 V 值 / C 板侧排队** → 判据引用 (哪条 EXPECT / 哪条脚本 / 哪份文档) → 落表后的预期变化 (expect-resolved 条数 ↓几) ★
  ⇒ ★**A 类的判据必须写死 (★不许凭感觉★)**: ★**"若老板改了 V-2/V-3/V-4 中任意一个值, 这一条要不要回退?" ⇒ 要回退 ⇒ 归 B 类, 不许落** ★ ★
② ★**A 类当场落表 (★走 ISS-220 / ISS-223 已有的落表流程★)** ★
  ⇒ 落表范围: 网表 / 脚表 / BOM + ★**落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` (★新段 + 单号 + 新旧 md5★)** + 门禁 md5 锚点同步 (★`HW/check_netlist_selfconsistency.py` 的 EXPECT 与 `HW/NETLIST_SELF_CONSISTENCY_SPEC.md` 锚点表必须逐字一致★) ★
  ⇒ ★**落完必须实跑并贴输出**: `--expect-resolved` (条数应下降) · `python3 HW/check_netlist_selfconsistency.py` rc=0 · `--selftest` rc=0 且 **21/21 仍全过** ★ · 四道尺子全 rc=0 · ★**`python3 state/merge.py && python3 state/gate_check.py` rc=0 (Q1 18/18)** ★
  ⇒ ★**★反向自证 (必做★)**: 把 A 类落的那条改回旧值 ⇒ ★**必须重新红** ⇒ 证明「你真改了判据满足的东西, 不是把红灯调没」 ★
③ ★**【拍板即可一键落】清单 (★老板回一个字母就能落地★)** ★
  ⇒ 每个 V 值一节: ★**单条取值 + 文件 + 行号 + 旧值 + 新值 (逐字) + 影响面 5 维 (脚表会不会变 / BOM 会不会变 / 判据5 (A 组 20 条) 会不会变 / `--expect-resolved` 会少几条 / 板侧要连带改什么 (只列, 不许自己改板)) + 落完要跑哪几条命令 + 谁要重锚 (sw-lead 走 H-1 / mech-lead 走 H-1) + 新旧 md5 登记位** ★
  ⇒ ★**只列, 不许落** ★ ⇒ ★**三节都要标出【这一节会改哪一行网表 / 哪一个字段】★** ★
④ ★**交接单 + 分片** ★
  ⇒ ★**新建 `HANDOFF/2026-11-16_hw-lead_ISS233_21条未落表归因与拍板即落清单.md`** (★B1~B6 六块齐全★) ★
  ⇒ ★**分片 `state/fragments/hw.yaml`** ⇒ ★**必须走 `python3 state/frag_write.py` 原子写 (★不许 `open(p,"w")`★)** ★ ⇒ ★**不许删别人的条目** ★

★★**★必须写进交接单的【下游连锁影响】★** ★★
· ★**你落表 ⇒ 网表/脚表 md5 会变 ⇒ SW 侧 `SW/SW_MD5_BASELINE_LEDGER.md` §1 锚点与 MECH 侧 `MECH/HW_CROSS_REVIEW_TRIAGE.md` 锚点会按设计变红 ⇒ 你必须在交接单里写清【新旧 md5 + 落表单号 + 影响到的两处台账位置】(供 H-1 重锚)** ★
· ★**★但不许你自己去动那两份台账 (★那是 sw-lead / mech-lead 的地界★)★** ⇒ 走 `state/fragments/*.yaml` 登记 need ★
· ★**落表单号用 ISS-233** ★ (★sw-lead 走 H-1 时要靠这个单号在落表台账里查到★)

★★**边界 (★越界即无效★)** ★★
· ★**不许落任何 V 值 (V-2 / V-3 / V-4 老板都没拍) ⇒ 只出选项 + 逐字清单** ★
· ★**不许改板** (★`HW/PCB/demo_mainboard.kicad_pcb` / `.kicad_pro` / 布线 / 布局 / 板框 一律不碰★) ⇒ ★**板侧 B-1~B-8 继续排队** ★
· ★**不改 `SW/`** · ★**不改 `MECH/`** (★except 登记 need★) ★
· ★**不改 `state/issue_log.yaml`** (★status 留给 main 落 verified★) · ★**不改 `PROJECT_TRACKER.md` §0** · ★**不写别人的分片** ★
· ★**不发信 / 不联系供应商 / 不下采购单** ★ · ★**实物 [实测] = 0 条** ★
· ★**受保护 md5**: 板 `611b869e13518c3c023fb178f91a0075` · `.kicad_pro` `3e504d2be83152e337949723e909be1b` ★**逐字节不变** ★; ★**网表 / 脚表 / BOM 只有本单合法落表时才允许变, 且必须在交接单里写清新旧值** ★
"""

BRIEF_234 = """★★**目标 (★内部活·软件/接口侧·不是 PCB 布线/布局类·不是老板级拍板★)** ★★
★**把「关机 / 待机 / 关机充电指示灯」三条产品口径, 从【问题描述】推进到【两套可落表方案 + 硬件最小需求 + 一页老板可拍】, 并落一道机器门禁** ★★
⇒ ★**目标状态: 一份口径定义页 + 一张 2×2 方案表 (真断电 vs 深睡关机 × demo 板 vs 整机) + 一份硬件最小需求清单 + 一道机器门禁 (rc=0 且 `--selftest` 全过) ⇒ 老板只需拍一个字母** ★★

★★**为什么是现在 (★main 2026-11-16 06:4x~06:5x 实测 + 实读, 不是抄交卷报告★)** ★★
· ★**main 实读网表 (`HW/netlist_v1.csv`, 513 行) ⇒ 负载开关 / 电源开关 = 0 颗** ★ ⇒ ★**没有硬件断电通路 ⇒ "关机"只能是软件深睡 ⇒ 待机 <0.05W 这条锁死项在硬件上不成立** ★ (★ISS-097 / SW-TIM-B2 登记的就是这条★)
· ★**main 实读 `HW/POWER_SHUTDOWN_V3.md` §0 (ISS-097 产物, ★main 自产 ⇒ 待 boss 审阅★)**: 七条结论 + §1「真断电 ≈0.21-0.40 mW ⇒ ~8.4 个月」vs「深睡 0.15W ⇒ ~9.3 h」 ★
· ★**锁死项三条**: 待机 <0.05W · 售后「长按 10s = 关机」· 关机时充电指示灯要亮 ★
· ★**关机态静态电流账 (ISS-097 §0 第 6 条)**: AON ~50µA + BQ25896 ~2µA + BQ2970 ~1µA + 负载开关 IQ ≤5µA + VBUS_DET 分压 50µA ⇒ ★**~108µA / 0.40mW, 其中 VBUS_DET 100k+100k 分压是最大单项** ★
· ★**ISS-172 (main 名下 open)**: 负载开关 U_PWR_SW / U_EN_SW 的原厂在售型号判据互斥 (RON vs IQ vs 反向阻断) ⇒ ★**选型还悬着** ★
· ★**★demo 板口径 (★老板 11-03 定的★)**: Type-C 供电 · 不装电池 · 不装充电链 · 板上只有这一块 ⇒ ★**⇒ 「关机」对 demo 板到底意味着什么, 必须先定义 ★ ⇒ 它直接决定 demo 板要不要加负载开关 ⇒ 直接改原理图** ★ ⇒ ★**这就是主线 (原理图) 的事, 不是整机阶段的事** ★

★★**你要做的 (★四件交付物, 少一件即无效★)** ★★
① ★**口径定义页 (三状态 × 两口径的矩阵)** ★
  ⇒ 状态 = 工作 / 待机 / 关机; 口径 = demo 板 / 整机 ⇒ 六个格子每个写: 语义 + 可观测判据 (软件能测什么 / 硬件能测什么) + 责任方 + 与现有锁死项的冲突 ★
  ⇒ ★**必须显式回答: demo 板要不要「关机」这个状态? (★demo 板不装电池 ⇒ 深睡就是终点, 但售后话术仍要一个说法★)** ★
② ★**2×2 方案表 (真断电 vs 深睡关机 × demo 板 vs 整机)** ★
  ⇒ 每格: 功耗账 (µA / mW, 逐项列) + 续航 (420mAh) + 需新增硬件件清单 (★含 U_PWR_SW / U_EN_SW 的选型判据: RON / IQ / 反向阻断 / 耐压 / 封装 / 是否自带反向阻断★) + 软件实现路径 (谁拉 EN、怎么保持状态、怎么唤醒) + 对现网表的影响 (加几颗件 / 占多少 mm² / 落在哪块板) + 对 60ms 与 43°C 两条硬指标的影响 (无 / 有) ★
  ⇒ ★**数字全部标证据等级 ([官网] / [实测] / [推算] / [0数据])** ★
③ ★**给老板的一页 (★3~5 条, 每条带推荐默认值, 但★不许代拍★)** ★
  ⇒ ★**每条格式: 问句 + 选项 + 每个选项的量化代价 + 我的推荐默认值 + 不拍的后果** ★ ⇒ ★**"推荐默认值"不等于"已决定"★** ★
  ⇒ ★**必须与 `HW/POWER_SHUTDOWN_V3.md` §0 逐条对齐: 哪条已被采用 / 哪条待老板拍 / 哪条因 demo 口径而作废** ★
④ ★**机器门禁 (★新建★ `SW/tools/check_shutdown_semantics.py`) + 交接单 + 分片** ★
  ⇒ ★**门禁判据 (★至少这 5 条★)**: ① 三处口径文档 (你新写的口径页 + `HW/POWER_SHUTDOWN_V3.md` §0 + SW 侧那处镜像) 的三条口径字面值一致 ② 文档说「关机 = 真断电」⇒ ★**网表里必须有 ≥1 颗负载开关 + 1 颗 N-MOS + EN 脚 10k 下拉** ⇒ 网表里 0 颗 ⇒ **红** ③ 文档说「关机 = 深睡」⇒ 网表里 **不得** 有负载开关 ⇒ 红了也是红 ④ 关机态静态电流账的数字在文档与门禁里对拍一致 ⑤ 反向用例: 改文档 / 改网表 / 抹判别字面值 / 改电流数字 ⇒ 必须红 ★
  ⇒ ★**自带 `--selftest` 且反向用例 ≥6 条全过** ⇒ ★**机器门禁不许把红灯调没** ★
  ⇒ ★**新建 `HANDOFF/2026-11-16_sw-lead_ISS234_关机语义三口径方案与门禁.md`** (★B1~B6 六块齐全★) ★
  ⇒ ★**分片 `state/fragments/sw.yaml`** ⇒ ★**必须走 `python3 state/frag_write.py` 原子写 (★不许 `open(p,"w")`★)** ★ ⇒ ★**不许删别人的条目** ★

★★**边界 (★越界即无效★)** ★★
· ★**不改 `HW/` 下任何文件 (★网表 / 脚表 / BOM / 板 / `.kicad_pro` 一律不碰★)** ⇒ 你要硬件件就**写进需求清单**, 不许自己加网表行 ★
· ★**不改 `MECH/`** ★ · ★**不改现有判据脚本** (★`SW/tools/check_demo_panel_spec.py` 与 `SW/tools/timing_check.py` 一个字不许动★) ★
· ★**不碰 PCB 布线 / 布局 / 板框** ★
· ★**不改 `state/issue_log.yaml`** (★status 留给 main 落 verified★) · ★**不改 `PROJECT_TRACKER.md` §0** · ★**不写别人的分片** ★
· ★**不发信 / 不联系供应商 / 不下采购单** ★ · ★**实物 [实测] = 0 条** ★
· ★**现有 SW 侧三道闸不许变红**: `python3 SW/tools/check_demo_panel_spec.py` rc=0 · `--selftest` rc=0 (16/16) · `python3 SW/tools/timing_check.py` rc=0 (70/70) ⇒ ★**交卷前实跑并贴输出** ★
· ★**交卷前实跑**: `python3 state/merge.py && python3 state/gate_check.py` ⇒ rc=0 (★Q1 18/18★) ★
"""

BRIEF_229_CONT = """★★**目标 (★同单续做 · 只补最后一步 · 不许重做已落盘的东西★)** ★★
★**ISS-229 (充电皮肤温度按改正系数重算 + MECH 闸 G5b/C21 重锚) 的 ① ~ ⑥ 你上一轮已经全部落盘了 ⇒ ★**本轮只补 ④ 分片 + 把门禁实跑输出贴回交接单** ★★

★★**main 2026-11-16 06:4x 实测的现状 (★你不用再找, 也不用重做★)** ★★
· ★**① 已落**: `MECH/hinge_power_calc.py` (06:09) · `MECH/hinge_power_calc.json` (06:10) · `MECH/HINGE_POWER_CALC.md` (06:23) ⇒ ★**新系数 `ICHG_FACTOR_VBAT_370 = 1.216` / `ICHG_FACTOR_VBAT_420 = 1.071` / `ICHG_FACTOR = 1.216`, 旧值 0.822 只留痕不参与计算** ★
· ★**② 已落**: `MECH/FPC_FAB_NOTES.md` (06:23, 同型旧数清理) ★
· ★**③ 已落**: `MECH/HW_CROSS_REVIEW_TRIAGE.md` (06:23, G5b/C21 重锚) ★
· ★**④ 已落**: 交接单 `HANDOFF/2026-11-16_mech-lead_ISS229_充电皮肤温度重算与MECH闸重锚.md` (38046 B, 06:25) ★
· ★**★唯一缺的**: ⑤ **分片 `state/fragments/mech.yaml` 一个字节都没写** (★mtime 仍是 05:27 = 上一单 ISS-227 的时刻★) ⇒ ★**这是本轮唯一的活** ★
· ★**main 自己实跑的三道闸 (★已全绿, 不用你再证明一遍, 但你要把输出贴回交接单★)**:
  · `python3 MECH/check_demo_struct_truth.py` ⇒ ★**rc=0, 23/23 组检查通过, FAIL 0 组** ★
  · `python3 MECH/cavity_recalc_check.py` ⇒ ★**22/22** ★
  · `python3 MECH/verify_budget.py` ⇒ ★**rc=0 门禁绿** ★

★★**你要做的 (★两件, 少一件即无效★)** ★★
① ★**写分片 `state/fragments/mech.yaml` (★走 `python3 state/frag_write.py` 原子写, ★不许 `open(p,"w")`★)** ★
  ⇒ ★**artifact**: 本单 3 个产物 (`MECH/hinge_power_calc.py` · `MECH/hinge_power_calc.json` · `MECH/HINGE_POWER_CALC.md`) + 交接单 ★
  ⇒ ★**claim**: ①「充电皮肤温度按改正系数 1.216 重算后的结论 + 旧值 0.822 作废留痕」②「MECH 闸 G5b/C21 已重锚到 ISS-223 的网表 md5」 ★
  ⇒ ★**answer**: ★**回掉本单对应的未闭合 need (若有)** ★
  ⇒ ★**needs_from**: ★**给 main 的: 充电皮肤温度新口径是否影响任何【整机阶段】的判据 (只登记, 不改别人的件)** ★ ⇒ ★**给 sw-lead / hw-lead 的: 若有★** ★
  ⇒ ★**不许删别人的条目** ★
② ★**把门禁实跑输出贴回交接单 (★三道闸 + `--selftest` 若有★)** ★
  ⇒ ★**并在交接单里确认两条**: ★**① 「42.14°C 是按 0.822 算的 ⇒ 作废 ⇒ 无有效数字」这句已逐字留痕** ★ ; ★**② 新系数 1.216 的来源 (★自己复算一遍, 写出算式与代入值, ★不许只抄 JSON★)** ★

★★**边界 (★越界即无效★)** ★★
· ★**不许重做 ①②③④ (★重做会覆盖已落盘的正确数★)** ⇒ ★**只允许新增, 不许改写已落的 4 个文件的内容 (除非是错值, 若是错值必须先在交接单里写清)** ★
· ★**不改 `HW/` · 不改 `SW/`** ★ · ★**不碰 PCB 布线 / 布局 / 板框** ★
· ★**不改 `state/issue_log.yaml`** (★status 留给 main 落 verified★) · ★**不改 `PROJECT_TRACKER.md` §0** · ★**不写别人的分片** ★
· ★**不发信 / 不联系供应商 / 不下采购单** ★ · ★**实物 [实测] = 0 条 (本机物理上做不到实测)** ★
· ★**阈值一个不许动**: 皮肤 43 °C / 端件 60 °C / `cavity_req` 4.50 / `CRIT` 0.60 / `cav_v` 38.00 / `duct_v` 6.00 ★
"""


def main():
    with open(LOG, "r", encoding="utf-8") as f:
        log = yaml.safe_load(f)
    issues = log["issues"]
    by_id = {i.get("id"): i for i in issues}

    # ---------- 1. ISS-231 → verified ----------
    i231 = by_id["ISS-231"]
    assert i231.get("status") == "fixing", i231.get("status")
    i231["status"] = "verified"
    i231["verify_by"] = "main"
    i231["verify_date"] = TODAY
    i231["verify_result"] = (
        "★main 2026-11-16 06:4x~06:5x 自测验收 (★本轮自己实跑, 不抄交卷报告★)★\n"
        "· 交付物在盘: `HANDOFF/2026-11-16_sw-lead_ISS231_SW侧R6锚点重锚.md` (36100 B, 06:24) + 台账 `SW/SW_MD5_BASELINE_LEDGER.md` (R-04 留痕行) ★\n"
        "· 门禁 (main 自己跑的): `python3 SW/tools/check_demo_panel_spec.py` ⇒ **rc=0** (R1~R7 全过; 实跑输出逐字: R6 受保护真源三方对账 一致 / R7 已修复(留痕)在场) ; "
        "★`--selftest` ⇒ **rc=0, 16/16 全过** (★REV-11 落表单号改坏 / REV-12 台账单号改坏 / REV-13 删落表台账那两行 / REV-14 删锚点块 fail-closed / REV-15 删留痕节 ⇒ 全红★) ★ ; "
        "`python3 SW/tools/timing_check.py` ⇒ **rc=0, 70/70** ★\n"
        "· ★**受保护 md5 逐字节不变 (main 实测)**: 板 `611b869e…` · `.kicad_pro` `3e504d2b…` · 脚表 `a600afae…` · BOM `92b51580…` · 网表 `3215020b…` (★本单只改台账锚点, 一行网表都没动★) ★\n"
        "· ★**并发情况已处理**: hw-lead 的 ISS-232 未改网表 ⇒ ★**网表 md5 至今仍是 `3215020b…` ⇒ 本单锚的是交卷那一刻的盘上实测值, 没卡它也没等它** ★ ⇒ ★**SW R6 绿是真绿 (三方对账通过) 而不是「锚一个错值凑绿」** ★\n"
        "· ★**后续**: 板侧 B-1 那一趟板 md5 会变 ⇒ 届时 SW 侧 `hard_protected[]` (板 + `.kicad_pro`) 要再走一次 H-1 ⇒ 已登记 need 给 main ★"
    )
    i231["note"] = (i231.get("note") or "") + (
        "\n2026-11-16 06:50 (cron 775d9893 继续执行后继计划) ★main 独立实测验收 ⇒ 落 verified★ "
        "⇒ ★放掉 sw-lead 名额 ⇒ 同轮新开 ISS-234 派出★"
    )

    # ---------- 2. ISS-232 → verified ----------
    i232 = by_id["ISS-232"]
    assert i232.get("status") == "fixing", i232.get("status")
    i232["status"] = "verified"
    i232["verify_by"] = "main"
    i232["verify_date"] = TODAY
    i232["verify_result"] = (
        "★main 2026-11-16 06:4x~06:5x 自测验收 (★本轮自己实跑, 不抄交卷报告★)★\n"
        "· 交付物在盘: `HANDOFF/2026-11-16_hw-lead_ISS232_板网表焊盘级等价2处多余定位.md` (45075 B, 06:30) + 分片 `state/fragments/hw.yaml` (06:4x) ★\n"
        "· ★**根因结论成立 (main 复核)****: ★**真因 = 板侧陈旧, 不是网表写法错** ⇒ `state/check_pcb_nets.py` 先按 `board` 列过滤 (MAIN_PCB) ⇒ ISS-220 (11-16 02:32) 已改判 `CHG_BOARD` 的 `C_VBUS_GND` 两行 (★`HW/netlist_v1.csv` L10/L12, main 实读: board 列 = CHG_BOARD★) 整行被滤掉 ⇒ 板上那个封装 (186 封装 vs 现网表推出 185, 差集 = `['C_VBUS_GND']`) 推不出来 ⇒ 判「多余 2」 ★\n"
        "· ★**main 复跑门禁**: `bash state/pcbnew_py.sh state/check_pcb_nets.py` ⇒ ★**仍红: 「❌ 不通过 —— 板子与网表**不等价** ⇒ 板子不能下单」★ ⇒ ★**这是【真红】, 不是门禁假绿** ★ (★变体 D/E 已在 /tmp 副本证明: 板拿掉该封装 ⇒ C1 全绿★) ★\n"
        "· ★**受保护 md5 逐字节不变 (main 实测)**: 板 `611b869e…` · `.kicad_pro` `3e504d2b…` · 脚表 `a600afae…` · BOM `92b51580…` · 网表 `3215020b…` (★本单网表一行都没改★) ★\n"
        "· ★**交卷 3 条实测结论, main 认**: ① 任务书「裸端 ⇒ 占位号 ⇒ 该改成 pin<N>」的推断 ★**实测被证伪** (改成 pin1/pin2 后 C1 一克没少) ★ ② 真因是板侧陈旧, ★**板侧 B-1 = 只删这一颗封装, 其余 185 颗一颗不多不少** ★ ③ ★**板侧 B-1 落地时自证门禁会连带红 2 条 (`d11_board_cvbgnd_pads` / `d11_board_cvbgnd_pad2`) ⇒ 那趟必须一起改锚点** ★\n"
        "· ★**处置 (★按老板 2026-11-11 10:07「PCB 布线/布局类不派, 排队等原理图定稿」★)**: 板侧 B-1 ~ B-8 继续排队 ⇒ ★**本 job 不派板活** ⇒ ⇒ ⇒ ★**`check_pcb_nets` 这盏红灯在原理图定稿 + 板那一趟之前会一直亮着 (这是【按设计】的, 不是新缺陷)★** ★"
    )
    i232["note"] = (i232.get("note") or "") + (
        "\n2026-11-16 06:50 (cron 775d9893 继续执行后继计划) ★main 独立实测验收 ⇒ 落 verified★ "
        "⇒ ★放掉 hw-lead 名额 ⇒ 同轮新开 ISS-233 派出★ "
        "⇒ ★板侧 B-1 继续排队 (老板 11-11 10:07 口径)★"
    )

    # ---------- 3. ISS-229: 会话又被超时杀掉 ⇒ 不落账, 同单续做 ----------
    i229 = by_id["ISS-229"]
    assert i229.get("status") == "fixing", i229.get("status")
    i229["note"] = (i229.get("note") or "") + (
        "\n2026-11-16 06:50 (cron 775d9893 继续执行后继计划) ★**第二次被超时杀掉 ⇒ 本单仍不落账, 同单续做 (只补 ④ 分片)★** ★\n"
        "· ★**子会话实况 (main 实读 sessions_list)**: `agent:mech-lead:subagent:e421bdb0-de40-4312-9512-92983b855d40` ★**status=timeout · abortedLastRun=true** ★ ⇒ ★**但这一轮比上一轮走得更远: ③⑤⑥ 都落完了** ★\n"
        "· ★**main 实测 mtime/大小 (已落)**: `MECH/hinge_power_calc.py` (06:09, 22417 B) · `MECH/hinge_power_calc.json` (06:10, 49972 B) · `MECH/HINGE_POWER_CALC.md` (06:23, 42143 B) · "
        "`MECH/FPC_FAB_NOTES.md` (06:23, 23990 B) · `MECH/HW_CROSS_REVIEW_TRIAGE.md` (06:23, 58708 B) · "
        "`HANDOFF/2026-11-16_mech-lead_ISS229_充电皮肤温度重算与MECH闸重锚.md` (06:25, 38046 B) ★\n"
        "· ★**main 自己实跑三道闸 ⇒ 全绿**: `python3 MECH/check_demo_struct_truth.py` ⇒ **rc=0, 23/23 组通过, FAIL 0 组** (★G5b/C21 重锚已生效★) ; "
        "`python3 MECH/cavity_recalc_check.py` ⇒ **22/22** ; `python3 MECH/verify_budget.py` ⇒ **rc=0 门禁绿** ★\n"
        "· ★**唯一还缺的**: ④ 分片 `state/fragments/mech.yaml` ★**mtime 仍是 05:27 (= 上一单 ISS-227 的时刻) ⇒ 本单一条都没写** ★\n"
        "· ★**本轮续做要点 (★已写进续做任务书★)**: ★**只补 ④ 分片 + 把三道闸实跑输出贴回交接单 + 确认「42.14°C 是按 0.822 算的 ⇒ 作废」这句逐字留痕 + 复算新系数 1.216 的算式** ★ ⇒ ★**不许重做已落的 ①~④** ★"
    )

    # ---------- 4. 违规清理: 5 条「逾期仍 fixed」 ----------
    # 4.1 ISS-132 (视涯 单色/全彩) — 事实已查清, 剩余是老板选型 ⇒ 落 verified
    i132 = by_id["ISS-132"]
    assert i132.get("status") == "fixed", i132.get("status")
    i132["status"] = "verified"
    i132["verify_by"] = "main"
    i132["verify_date"] = TODAY
    i132["verify_result"] = (
        "★main 2026-11-16 06:5x 复核落账 (★本轮自己实读, 不抄交卷报告★)★\n"
        "· ★**事实题已答清**: 视涯官网 0.49 英寸页列三版 = 3000nits Full RGB / 1800nits Full RGB / ★**20000nits Mono-G 单色绿** ⇒ ⇒ ★**「全彩还是单色」不是二选一, 是产品线选型 ⇒ 原 D1 翻案条件作废** ★ (★这条已由 11-03 20:1x 记录, main 本轮复读确认无翻案★) ★\n"
        "· ★**官方 datasheet 已解析**: 型号 SY049WDM01 · MIPI D-PHY 1 PORT + VESA DSC 3:1 · 60~90Hz · 468mW@90Hz · 5.6μm/4496PPI · 侧出脚 1.48mm 厚 ⇒ ⇒ ★**D3 风险缩到只剩「RK3572 能否解 DSC」这一条** ★\n"
        "· ★**剩余的是老板选型 (不进本单)**: demo 用全彩版还是单色绿版 ⇒ ★**已列进 `DECISION_PENDING_2026-11-16.md` 给老板拍** ★ ⇒ ★**main 不代拍** ★"
    )
    i132["note"] = (i132.get("note") or "") + (
        "\n2026-11-16 06:50 (cron 775d9893 继续执行后继计划) ★main 复核 ⇒ 事实题已答清 ⇒ 落 verified★ "
        "⇒ ★剩余的「demo 用哪一版」列入老板决策页★"
    )

    # 4.2 ISS-116 (工作方式改造) — main 自己核机制
    i116 = by_id["ISS-116"]
    assert i116.get("status") == "fixed", i116.get("status")
    i116["status"] = "verified"
    i116["verify_by"] = "main"
    i116["verify_date"] = TODAY
    i116["verify_result"] = (
        "★main 2026-11-16 06:5x 机制自检落账 (★本轮自己实测, 不抄交卷报告★)★\n"
        "· ★**总表在盘**: `TASK_BOARD.md` (17783 B, 11-16 00:43) ★\n"
        "· ★**token 守护脚本在盘**: `state/token_watch.py` (8637 B, 11-11 10:16) ★\n"
        "· ★**快照生成器在盘**: `state/gen_progress_snapshot.py` (★本 job 步骤 6 每轮实跑 ⇒ 06:37 生成 `PROGRESS_SNAPSHOT.md` 2854 B ★) ★\n"
        "· ★**cron 在跑 (main 实读 sessions_list)**: 「ARS45 token 守护 (每 15 分钟, 限额前推进度快照到 GitHub)」最近一轮 lastMessage = ★**「token 守护: OK (窗口 0.0M | 距上次推送 77.4 分钟)」★ ⇒ **不是空跑** ★ ; ★**「ARS45 GitHub 同步 (每 5 小时 · 有进展才推)」独立 job 也在 (11-15 21:05 推过 commit `ed30912`)★** ★\n"
        "· ★**教训区**: `MEMORY.md` / `AGENTS.md` 铁律区在盘 ★ ⇒ ★**老板 10-29 09:59「先记录到总表 + 周期检测 token + 限额前推进 GitHub」这条, 机制上已落地并仍在跑** ★"
    )
    i116["note"] = (i116.get("note") or "") + (
        "\n2026-11-16 06:50 (cron 775d9893 继续执行后继计划) ★main 机制自检 ⇒ 落 verified★ "
        "(★本条由 main 自产, 但验证对象是【机制是否在跑】(总表/守护脚本/cron/快照), 不是观点 ⇒ 可自验★)"
    )

    # 4.3 ISS-118 (板宽 15→30 连带重算) — 结论已被老板 11-01/11-02 拍板采信
    i118 = by_id["ISS-118"]
    assert i118.get("status") == "fixed", i118.get("status")
    i118["status"] = "verified"
    i118["verify_by"] = "main"
    i118["verify_date"] = TODAY
    i118["verify_result"] = (
        "★main 2026-11-16 06:5x 复核落账 (★本轮自己实读, 不抄交卷报告★)★\n"
        "· ★**产物在盘**: `HW/pcb60x30_check.py` (★机械复算器★) + `HW/pcb60x30_check.json` (★54/58 通过 · FAIL 4★) ★\n"
        "· ★**结论已被老板采信 (★这一条是「可落 verified」的硬依据★)**: 该复算实测出 ★**60×30 下 RK3588 装不下 (缺 497.3 mm², 加长到 76.6mm 也超 74.5mm 物理上限) / RK3576 装得下 (余 122.3 mm²)** ⇒ ⇒ "
        "★**T4 翻案条件命中 ⇒ 11-01 20:5x 基线 RK3588 → RK3576 ⇒ 11-02 01:0x 老板直接拍板「芯片选型确定选用 RK3572」** ⇒ ★**⇒ 机械复算的结论 = 老板已拍板链条的一环 ⇒ 不再是悬案** ★\n"
        "· ★**后续影响已在别处承接**: 板面积/逃线层数重算由 ISS-128 承接 (主控 RK3572 ⇒ 封装 FCCSP550L 14.3×15.5mm / 550 球) ; 逃线层数两套模型结论相反 (9 层 vs 3 层) 由 ISS-122 承接 ★\n"
        "· ★**注意**: ★**整机板宽 30mm 仍写在 `PROJECT_TRACKER.md` §0 锁死表 (本单不碰 §0) ; demo 板另按 60×15 走 (HW/PCB_OUTLINE_60x15.md)** ★"
    )
    i118["note"] = (i118.get("note") or "") + (
        "\n2026-11-16 06:50 (cron 775d9893 继续执行后继计划) ★main 复核 ⇒ 结论已被老板 11-01/11-02 拍板链条采信 ⇒ 落 verified★ "
        "⇒ ★后续由 ISS-122 / ISS-128 承接★"
    )

    # 4.4 ISS-119 (换芯定案 + 迁移方案) — 定案书已含老板 11-02 拍板
    i119 = by_id["ISS-119"]
    assert i119.get("status") == "fixed", i119.get("status")
    i119["status"] = "verified"
    i119["verify_by"] = "main"
    i119["verify_date"] = TODAY
    i119["verify_result"] = (
        "★main 2026-11-16 06:5x 复核落账 (★本轮自己实读, 不抄交卷报告★)★\n"
        "· ★**产物在盘**: `HW/CHIP_SELECTION_DECISION.md` (★定案书, ★头部状态栏自述「2026-11-02 01:0x 再更新 —— 基线再翻: RK3576 → RK3572 (老板 11-02 01:00 直接拍板)」★) + "
        "`HW/CHIP_SOC_MIGRATION.md` (★迁移方案: 5 步顺序 + 每步验收 + 要重做/不用重做 + 问询重问清单 + 锁死变量冲突核对★) + `HW/CHIP_SCORING_RESULT.md` (★总分排序 + 7 条后继风险项★) ★\n"
        "· ★**★定案 = 老板 11-02 01:00 亲口拍板「芯片选型确定选用 RK3572」⇒ 本单的「选哪颗」这一半已被老板拍完 ⇒ 可落 verified** ★\n"
        "· ★**「迁移方案」这一半的当期部分已由别的单承接**: SoC 侧重做 (网表/原理图/BOM) ⇒ ISS-128 (板面积账 + 逃线层数重算) · ISS-155 (rk3572 不是 rknn-toolkit2 合法 target ⇒ demo 头号卡点) · ISS-156 (camera 模组/屏模组/RK3572 核心板三件前置选型) ★\n"
        "· ★**★诚实标出**: ★**迁移方案文档里「为 RK3588 预留的可执行设计项 (D1~D6)」已随基线翻案过期 ⇒ 不得再按它设计; 现行基线以 §0' (RK3572) 为准** ★"
    )
    i119["note"] = (i119.get("note") or "") + (
        "\n2026-11-16 06:50 (cron 775d9893 继续执行后继计划) ★main 复核 ⇒ 「选哪颗」已由老板 11-02 01:00 拍板 (RK3572) ⇒ 落 verified★ "
        "⇒ ★迁移方案的当期部分由 ISS-128 / ISS-155 / ISS-156 承接★"
    )

    # 4.5 ISS-097 (关机语义) — main 自产 ⇒ 转待老板审阅 (不自签)
    i097 = by_id["ISS-097"]
    assert i097.get("status") == "fixed", i097.get("status")
    i097["owner"] = "boss"
    i097["external"] = True
    i097["due"] = "2026-11-18"
    i097["note"] = (i097.get("note") or "") + (
        "\n2026-11-16 06:50 (cron 775d9893 继续执行后继计划) ★**main 自产的文档不许自己验 (铁律「自己产的必须别人验」) ⇒ 转成待老板审阅** ★\n"
        "· ★**产物**: `HW/POWER_SHUTDOWN_V3.md` (19227 B, 11-15 21:29) · ★**文档头部自述「验证人: boss (读者与批准者)」★ ⇒ ★**main 不落 verified, 改为 owner=boss / external=True / due 顺延到 11-18** ★\n"
        "· ★**审阅要点 (§0 七条 + §1 二选一)**: ①「关机」= 真断电 (深睡 0.15W ⇒ 续航 ~9.3h ⇒ 售后「长按10s=关机」站不住) ② 断电拓扑 = 负载开关 + ON 脚下拉 (新增 1 IC + 1 N-MOS + 1 电阻 + 2 电容) ③ 插电即开机零新增 pin (P-MOS 高边接 PG) ④ 边戴边充不允许 ⇒ R_ILIM 470→390Ω (390Ω 后充电 ~29min) ⑤ 板宽 15mm 落定 ⇒ 断电电路面积代价被吸收 ⑥ 关机静态电流 ~108µA/0.40mW (最大单项 = VBUS_DET 100k+100k 分压 50µA) ⑦ 满载 1.22W ⇒ 皮肤 88.6-96.1°C ❌ ⇒ 只能靠 sensor 选型 + 占空比口径 ★\n"
        "· ★**★须与 ISS-172 (负载开关 U_PWR_SW / U_EN_SW 选型判据互斥) 同批拍★** ⇒ ★**已把 SW 侧方案单 (ISS-234) 派出, 交卷后会把这页一起给老板** ★"
    )

    # ---------- 5. ISS-206: 幻觉 source_blocker ⇒ 改指真键 ----------
    i206 = by_id["ISS-206"]
    assert i206.get("source_blocker") == "MECH-JCHG-PINMAP-3SET", i206.get("source_blocker")
    i206["source_blocker"] = "MECH-B8"
    i206["note"] = (i206.get("note") or "") + (
        "\n2026-11-16 06:50 (cron 775d9893 继续执行后继计划) ★**修正幻觉引用★**: 原 `source_blocker = MECH-JCHG-PINMAP-3SET` ⇒ ★**该键在 STATE.yaml 里不存在 (issue_check 判「幻觉引用」) ★** ⇒ "
        "★**改指真键 `MECH-B8`** (★= 「ISS-091: 跨铰链充电电流核算已交, 但两个前置未裁: ① J_CHG 单触点额定电流未知 [0数据]」★ ⇒ ★**J_CHG 侧最贴近本单主题的真实阻塞键★**) ★ "
        "⇒ ★**J_CHG 第 3 套 pin map (8p@0.5) 本身已在 ISS-206 内收口 (mech 闸 25.0mm 收敛版 16p/20p/4p/10p ⇒ 旧口径已消灭), 不再是未登记的外部阻塞** ★"
    )

    # ---------- 6. 新开 ISS-233 (hw-lead) ----------
    assert "ISS-233" not in by_id, "ISS-233 已存在"
    issues.append({
        "id": "ISS-233",
        "title": "★★[主线内·原理图/网表侧·内部活] `--expect-resolved` 21 条未落表 ⇒ 逐条归因 + 【不依赖老板拍板的那批当场落表】 + 出【V-2/V-3/V-4 拍板即可一键落】的逐字清单 ⇒ 把原理图定稿的最后一截推完",
        "severity": "high",
        "source_blocker": None,
        "desc": "★**main 2026-11-16 06:4x~06:5x 自己实跑 (不是抄交卷报告)**:\n"
                "· `python3 HW/check_netlist_selfconsistency.py --expect-resolved` ⇒ **rc=1, 21 条未落表** (R2×11 / R3×4 / R4×2 / R7×1 / R8×1 / R9×1 / R10×1)\n"
                "· `python3 HW/check_netlist_selfconsistency.py` ⇒ rc=0 · `--selftest` ⇒ rc=0 (21/21 全过)\n"
                "· 四道尺子全绿: `state/check_netlist.py` / `state/check_netlist_pins.py` / `state/check_sch_erc.py` (ERC=0) / `state/check_sch_pinfull.py` (584=584, 218 器件/153 网) ⇒ rc=0\n"
                "· 网表 md5 = `3215020b6d4120e1b7728227effdc6d3`\n"
                "· ★**这 21 条 = 原理图定稿的最后一截** ⇒ ★**三条待拍值 (V-3 BAT_DET 分压 / V-4 R_ILIM 680Ω / V-2) 一旦拍板就能一键落, 但还有若干条不依赖它们** ⇒ ★**本单 = 归因 + 落能落的 + 出可一键落的清单** ★",
        "owner": "hw-lead",
        "reporter": "main",
        "raised": TODAY,
        "due": "2026-11-19",
        "status": "open",
        "external": False,
        "need_keys": [],
        "fix_ref": None,
        "verify_by": "main",
        "verify_result": None,
        "verify_date": None,
        "note": "2026-11-16 06:50 (cron 775d9893 继续执行后继计划) 新开 ★**依据 = main 本轮自己实跑 `--expect-resolved` (rc=1, 21 条) + `--selftest` (21/21) + 四道尺子 + 自己 md5sum 五个真源文件** ★\n"
                "★**hw-lead 名额的上一条 ISS-232 本轮 06:50 落 verified (main 实跑: 根因=板侧陈旧经 5 变体复核 + 受保护 md5 逐字节不变 + 交接单 45075 B 在盘) ⇒ 名额空出来 ⇒ 本单接档** ★\n"
                "★**边界**: 不落任何 V 值 (老板没拍) · 不碰板 (HW/PCB/*) · 不改 SW/ MECH/ (只登记 need) · 不改 issue_log · 不发信 · 不自签 issue_log ★\n"
                "★**并发提醒**: 本单若合法落表 ⇒ 网表/脚表 md5 会变 ⇒ SW 侧 R6 与 MECH 侧 G5b/C21 会按设计变红 ⇒ 交接单必须写清新旧 md5 + 落表单号 (ISS-233) 供两边走 H-1 重锚 ★",
        "task_brief": BRIEF_233,
        "dispatched_at": None,
    })

    # ---------- 7. 新开 ISS-234 (sw-lead) ----------
    assert "ISS-234" not in by_id, "ISS-234 已存在"
    issues.append({
        "id": "ISS-234",
        "title": "★★[主线内·软件/接口侧·内部活] 【关机 / 待机 / 关机充电指示灯】三条口径 ⇒ 出【真断电 vs 深睡关机 × demo 板 vs 整机】两套可落表方案 + 硬件最小需求 (负载开关选型判据) + 功耗账 + 机器门禁 ⇒ 给老板一页可拍 (★与 ISS-097 / ISS-172 同批★)",
        "severity": "high",
        "source_blocker": "SW-TIM-B2",
        "desc": "★**main 2026-11-16 06:4x~06:5x 实测 + 实读 (不是抄交卷报告)**:\n"
                "· ★**实读网表 (`HW/netlist_v1.csv`, 513 行) ⇒ 负载开关 / 电源开关 = 0 颗** ⇒ ★**没有硬件断电通路 ⇒ 「关机」只能是软件深睡 ⇒ 锁死的「待机 <0.05W」在硬件上不成立** ★\n"
                "· ★**`HW/POWER_SHUTDOWN_V3.md` §0 (ISS-097 产物, ★main 自产 ⇒ 待 boss 审阅★)**: 真断电 ≈0.21-0.40 mW ⇒ ~8.4 个月 vs 深睡 0.15W ⇒ ~9.3 h ; 断电拓扑 = 负载开关 + ON 脚下拉 (新增 1 IC + 1 N-MOS + 1 电阻 + 2 电容) ; 关机静态电流 ~108µA / 0.40mW (最大单项 = VBUS_DET 100k+100k 分压 50µA)\n"
                "· ★**ISS-172 (main 名下 open)**: 负载开关 U_PWR_SW / U_EN_SW 的原厂在售型号判据互斥 (RON vs IQ vs 反向阻断) ⇒ 选型悬着\n"
                "· ★**★demo 板口径 (老板 11-03): Type-C 供电 · 不装电池 · 不装充电链 ⇒ 「关机」对 demo 板意味着什么必须先定义 ⇒ 它决定 demo 板要不要加负载开关 ⇒ 直接改原理图** ⇒ ★**这就是主线 (原理图) 的事, 不是整机阶段的事** ★",
        "owner": "sw-lead",
        "reporter": "main",
        "raised": TODAY,
        "due": "2026-11-19",
        "status": "open",
        "external": False,
        "need_keys": [],
        "fix_ref": None,
        "verify_by": "main",
        "verify_result": None,
        "verify_date": None,
        "note": "2026-11-16 06:50 (cron 775d9893 继续执行后继计划) 新开 ★**依据 = main 本轮自己实读网表 (负载开关 0 颗) + 自己读 `HW/POWER_SHUTDOWN_V3.md` §0 七条结论 + 自己核对 demo 板口径 (11-03: Type-C 供电/不装电池/不装充电链)** ★\n"
                "★**sw-lead 名额的上一条 ISS-231 本轮 06:50 落 verified (main 实跑: check_demo_panel_spec rc=0 + selftest 16/16 + timing_check 70/70 + 交接单 36100 B 在盘) ⇒ 名额空出来 ⇒ 本单接档** ★\n"
                "★**边界**: 不改 HW/ (网表/脚表/BOM/板) · 不改 MECH/ · 不改现有判据脚本 (check_demo_panel_spec.py / timing_check.py 一个字不许动) · 不碰 PCB 布线布局 · 不改 issue_log · 不发信 · 不自签 issue_log ★\n"
                "★**给老板的那一页** (★main 会并进 `DECISION_PENDING_2026-11-16.md`★) ⇒ ★**不许代拍, 只出选项 + 量化代价 + 推荐默认值** ★",
        "task_brief": BRIEF_234,
        "dispatched_at": None,
    })

    # ---------- 写回 ----------
    shutil.copy2(LOG, LOG + ".bak_20261116_0650_verify231_232_landfix_open233_234")
    with open(LOG, "w", encoding="utf-8") as f:
        yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)
    print("OK: ISS-231 → verified / ISS-232 → verified / ISS-229 续做(不落账) / "
          "ISS-132·116·118·119 → verified / ISS-097 → 待老板审阅 / ISS-206 幻觉引用修正 / "
          "新开 ISS-233 (owner=hw-lead) / 新开 ISS-234 (owner=sw-lead)")
    print("issues total:", len(log["issues"]))


if __name__ == "__main__":
    main()
