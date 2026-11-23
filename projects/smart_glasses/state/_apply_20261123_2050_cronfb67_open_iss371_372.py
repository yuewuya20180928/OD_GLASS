#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
★**cron fb67af40 (ARS45 队列自动派活) · 2026-11-23 20:5x · 新开 ISS-371 / ISS-372 并落 `fixing`** ★

★**为什么开单 (★本机实读·不是猜★)★**:
  ① `python3 state/advance.py --json` ⇒ ★**internal: []** (三个总工名下零 `open` 可派)
  ② ★**但三个槽位不是都被占满★**: hw-lead = ★**ISS-369 真在飞** (★会话 `245328df` transcript 20:46:05 仍在写·`tmp/iss369/tools/` 20:44 仍在落盘★)
     ⇒ ★**sw-lead / mech-lead 两个槽位【真空】= 一个在跑会话都没有 + 名下零 open 项** ★
     ⇒ ★**⇒ 队列对这两条线是真断的 (不是被占满, 是没活)** ★
  ③ ★**两件活都有本机实测出来的真依据 (★不是编的·不是抄任何 agent 报告★)★**:
     · ★**ISS-371 (mech-lead)**: `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` §C-SEAT-1 与 MECH 三页 + 机器块写的
       「改 land 到 1.27 ⇒ 铜箔 X 宽 4.0850 / 单边间隙 3.0575 / 最坏 2.7575」★**四处同源推导** ★
       ⇒ ★**main 本机实算: 官方真 land `Connector_PinHeader_1.27mm:PinHeader_1x04_P1.27mm_Vertical.kicad_mod`
         的 pad 是 1.0×1.0 (实测), 不是现页沿用的 0.275 ⇒ 铜箔 X 宽 = 3.81+1.0 = 4.8100 ⇒ Δ +0.7250**
       ⇒ ★**⇒ 现页的每个数都偏乐观 0.3625mm; 且清空区仍按 4.0850 留 ⇒ 最外侧焊盘每边越界 0.3625 ⇒ 铜箔直接进清空区**
       ⇒ ★**⇒ 「板只改一次」那一趟开工前不算清, 要么改结构件返工, 要么板 md5 变第二次 ⇒ 整趟白跑** ★
       ⇒ ★**且这条正是 `hw.yaml` 里挂了没人答的 need `iss356_jdebug_mech_clearance_recheck` (to=mech-lead·since=2026-11-23)** ★
     · ★**ISS-372 (sw-lead)**: SW 域 17 个活文件 / 57 处硬写旧板 md5, 其中 3 处判据脚本 ★
       ⇒ ★**`SW/tools/check_fp_truth_read.py` (ISS-363 今天 17:27 造) 与 `SW/tools/check_onepass_legb_sw_impact.py` (ISS-370 今天 19:50 造)
         都没有合法改板通道, 也不在那张「钉板 md5 的闸清单」里 (那张是 11-17 生成的·main 实读)** ★
       ⇒ ★**⇒ 改板当天它们必红 (F5 / G8 判据本机实读确认), 而红的真含义是「板被换了」⇒ 现场极可能误读⇒ 改板凑绿⇒ 板 md5 变第二次** ★
       ⇒ ★**⇒ 且没有任何闸在守那张清单的新鲜度 ⇒ 下一个新闸再硬钉板 md5 时没人拦** ★
  ④ ★**两条都是 PCB 线的【纯分析 + 作业包 + 新建闸 + 沙盒预演】⇒ 零写板 · 零落表 ⇒ 符合「板只改一次」纪律 ① (先派纯分析/作业包类)★**

★**★防撞车 (★铁律⑩-i: 先落 `fixing` 再 spawn★)★**:
  ★**status 直接落 `fixing` ⇒ 兄弟 job 775d9893 读的是同一个字段 ⇒ 它看到 fixing 就不会再派 ⇒ 零撞车窗口** ★
  ★**issue_log 写回用【文本追加】(★不是全文件 yaml 重排·★全文件重排实测会把 ISS-370 那条 verify_result 折行·属 churn★)⇒ 前 365 条逐条逐字节不变** ★
  ★**dispatch_log 同样文本追加 ⇒ 前 376 条逐条逐字节不变** ★

★**边界**: ★**只写 `state/issue_log.yaml` + `state/dispatch_log.yaml` 两个文件** ★ (★不动分片 · 不动板 · 不动网表/脚表/BOM · 不动既有闸 · 不动既有页面 · 不推 GitHub · 零外发·不替老板拍板★)
"""
from __future__ import annotations

import fcntl
import os
import shutil
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
DLOG = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
STAMP = "20261123_2050_cronfb67_open_iss371_372"

BRIEF371 = "ISS-371_mech_jdebug_127_land_clearance_truth.md"
BRIEF372 = "ISS-372_sw_board_md5_rebase_readiness.md"

B371 = open(os.path.join(HERE, "dispatch_briefs", BRIEF371), encoding="utf-8").read()
B372 = open(os.path.join(HERE, "dispatch_briefs", BRIEF372), encoding="utf-8").read()

TITLE371 = (
    "★★[★新主线·PCB 线·结构侧·「板那一趟」`J_DEBUG` 排针 land 改 1.27mm 后的净距真相·纯分析+文档订正(追加式)+新建闸+沙盒预演·零写板] ★★"
    "【★main 2026-11-23 20:4x~20:5x 本机实算★: 现有四处 (HW 作业包 §C-SEAT-1 + MECH 三页 + 机器块) 同源推导写的"
    "「改 land 到 1.27 ⇒ 铜箔 X 宽 4.0850 / 单边间隙 3.0575 / 最坏 2.7575」, 而本机实读官方真 land "
    "`Connector_PinHeader_1.27mm:PinHeader_1x04_P1.27mm_Vertical.kicad_mod` 的 pad 是 1.0×1.0 (不是现页沿用的 0.275) "
    "⇒ 铜箔 X 宽 = 3.81+1.0 = 4.8100 ⇒ Δ +0.7250 ⇒ ★★现页每个数都偏乐观 0.3625mm; 且清空区若仍按 4.0850 留, "
    "最外侧焊盘每边越界 0.3625 ⇒ 铜箔直接进清空区⇒ 板只改一次那一趟开工前不算清 ⇒ 要么改结构件返工, 要么板 md5 变第二次⇒ 整趟白跑★★ "
    "⇒ ★★本单 = ① 一页逐条量差表 (三档口径 × 每一项·每格带复跑命令) ② 一条【官方 land 实读 + 清空区不许越界 + 单边间隙对称且 ≥CRIT】的机器闸 "
    "③ 追加式订正块 (老字一字不删·机器块只加字段不改旧字段值) + 降级方案 (SMD 2×2 交错变体) 整段重算 + 换型 (SMD占位→THT) 的环宽 [0数据] "
    "④ 答掉 `hw.yaml` 里挂了没人答的 need `iss356_jdebug_mech_clearance_recheck` (to=mech-lead·since=2026-11-23)** "
    "★【纯分析 + 文档订正 + 新建闸类 · 零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 · 零挂链 · 零外发 · 不代老板拍板】★★"
)

DESC371 = (
    "★**main 2026-11-23 20:4x~20:5x 本机实读 (★不抄任何 agent 报告·全部可复跑★)★** ⇒ "
    "★**① 官方真 land 实测 (读盘上 .kicad_mod, 不抄文档)★**: `Connector_PinHeader_1.27mm.pretty/PinHeader_1x04_P1.27mm_Vertical.kicad_mod` "
    "⇒ pad1~pad4 全是 `thru_hole size=1 1 drill=0.65`, at x=0/1.27/2.54/3.81, fp_rect -1.55 -1.14 .. 1.55 4.95 "
    "⇒ ★**铜箔 X 宽 = 3×1.27 (跨距 3.81) + 1.0 (pad 宽) = 4.8100** ★ ⇒ 环宽 = (1.0−0.65)/2 = 0.1750mm (★本仓无任何环宽判据 ⇒ [0数据]★) "
    "★**② 降级方案 SMD 变体实测**: `PinHeader_1x04_P1.27mm_Vertical_SMD_Pin1Left.kicad_mod` ⇒ pad 全是 `smd size=3 0.65` "
    "at (-1.5,-1.905)(1.5,-0.635)(-1.5,0.635)(1.5,1.905), fp_rect -3.5 -3.04 .. 3.5 3.04 ⇒ ★**2×2 交错·铜箔 X 跨距 6.00·fab 7.00×6.08 "
    "⇒ 与现页口径完全不可比, 必须整段重算** ★ "
    "★**③ 板面现状实测 (读板文件本体)★**: `J_DEBUG` = `(footprint \"\"` (★lib_id 空·自绘占位★) at (144.3 58), "
    "4 个 `smd rect (size 0.275 0.9)` @ pitch 0.50, F.Fab -3 -2 .. 3 2 (6.00×4.00), net JTAG_TCK/TMS/TDI/TDO "
    "⇒ ★**板面是【SMD 占位 (pad 宽 0.275) + pitch 0.50】, 而官方 1.27 land 是【THT (pad 1.0×1.0) + pitch 1.27】 "
    "⇒ 改 land 同时是【换型 SMD→THT】+【换封装真值】+【换 pitch】三件事捆在一起** ★ "
    "★**④ 现页口径的来历本机可反推★**: 4.0850 = 3.81 (跨距) + 0.275 (★沿用了板面占位 SMD pad 的宽度★) "
    "⇒ ★★它算的是「把 SMD 占位的 0.275 宽 pad 搬到 1.27 pitch 上」, 不是「官方 THT land 的 1.0 宽 pad」★★ "
    "★**⑤ 现存四处同源推导 (★main 本机实读行号·四处是同一个数的四个副本⇒ 一处错⇒ 四处一起错★)★**: "
    "`HW/PCB/BOARD_ONEPASS_WORKPACKET.md` L326 (§C-SEAT-1) · `MECH/BOARD_ONEPASS_MECH_SYNC.md` L561-L565/L572 (含机器块) · "
    "`MECH/BOARD_ONEPASS_MECH_CLAIMS.md` L50/L58/L133 (§C-OPEN-1) · `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` L175/L205/L211/L216/L241-L242 "
    "+ 机器块 L1917-L1927 (clearance_x 3.0575 / worst_clearance_x 2.7575 / placeable_width 3.0575 / delta_clearance_x -1.155) "
    "★**⑥ ★★按官方 THT 真值重算 (★居中解·板面位置不动·只换 land·main 本机实算★)★★**: 铜箔 X 中心 142.9500 · 开口 X 137.850..148.050 "
    "(PORT_OPEN_DEBUG) · `CRIT` = 0.60 (= `MECH/service_port_check.py` L126-L127 的 `2 × TOL[\"fdm_part\"]`, `TOL[\"fdm_part\"]`=0.30) "
    "⇒ 现状 (1.7750) 单边间隙 4.2125/4.2125 最坏 3.9125 · 现页口径 (4.0850) 单边间隙 3.0575/3.0575 最坏 2.7575 · "
    "★★官方 THT 真值 (4.8100) ⇒ 铜箔 X 140.5450..145.3550 ⇒ 单边间隙 2.6950/2.6950 最坏 2.3950 ⇒ 仍 ≥ CRIT 0.60 (余量 3.99×) ⇒ "
    "★**结论方向不变, 但每一个数都偏乐观 0.3625mm** ★★ ★**且清空区宽若仍按 4.0850 留 ⇒ 最外侧焊盘每边超出清空区 0.3625 ⇒ 铜箔直接进清空区** ★ "
    "★**⇒ 「板只改一次」那一趟 (S6 排针 land 改动, 板侧项 B33_PIN_LAND_1P27) 开工前必须把这个数算准, 否则要么改结构件返工, 要么板 md5 变第二次⇒ 整趟白跑** ★ "
    "★**⑦ 这条正是 `state/fragments/hw.yaml` 里挂了至今没人答的 need★**: key `iss356_jdebug_mech_clearance_recheck` · `to: mech-lead` · "
    "`since: 2026-11-23` · 原文要点 = 「只给封装真值 Connector_PinHeader_1.27mm:PinHeader_1x04_P1.27mm_Vertical (4 通孔 @1.27, pad 1.0×1.0, 实测在盘) "
    "⇒ 但量差要核: 作业包 §C-SEAT-1 的清空区是按 1.27 pitch + 0.275mm 宽 pad 算的 (X 宽 4.0850mm), 而官方 THT 排针 pad 宽 1.0mm ⇒ 铜箔净宽 4.81mm ⇒ 差 0.725mm "
    "⇒ 请按官方 land 核清空区/开口/座体净距是否还过 (单边间隙与 CRIT 0.60 的关系) ⇒ 若改用 SMD 变体则 land 变 2×2 交错而非 1×4 直排 ⇒ 结构尺寸要重算」★ "
    "★**⇒ 本单就是去把这条 need 做掉 (★答掉它, 别让它永远挂着)** ★ "
    "★**⑧ 判据常量真身**: `CRIT` 0.60 来自 `MECH/service_port_check.py` L126-L127 (★不许写死·你的闸要自己取★) · "
    "开口 Y 口径 `OPEN_Y_eff(h) = max(4.60, h + 1.80)` · h = `[0数据]` ⇒ 不许把 2.54 当事实写死 "
    "★**⑨ MECH 域既有闸 7 道, 你追加块之后必须仍全 rc=0** ★: `MECH/check_onepass_mech_sync.py` · `MECH/check_onepass_struct_crosscheck.py` · "
    "`MECH/check_demo_struct_truth.py` · `MECH/check_board_frame_coords.py` · `MECH/check_mech_dual_caliber_gate.py` · "
    "`MECH/check_onepass_s10_led_spec_sync.py` · `MECH/check_onepass_s10_fp_swap_impact.py` "
    "★**⑩ 板面双证**: md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · size 4940213 (★开工前 + 交卷后各一次★) "
    "★**⇒ 本单只出【纯分析 + 追加式文档订正 + 一条新闸 + 沙盒预演】, 一个字节都不许写板** ★"
)

TITLE372 = (
    "★★[★新主线·PCB 线·SW 侧·「板那一趟」S9 换基线 · SW 侧板 md5 引用面清账 + 一条「钉板 md5 闸清单」自守闸·纯分析+作业包+新建闸+沙盒预演·零写板] ★★"
    "【★main 2026-11-23 20:4x~20:5x 本机实读★: SW 域 17 个活文件 / 57 处硬写旧板 md5 `611b869e…` (3 个判据脚本 + 14 个 .md); "
    "而那张「钉板 md5 的闸清单」是 2026-11-17 20:49 生成的, 今天新造的 2 道 SW 闸 (ISS-363 17:27 / ISS-370 19:50) "
    "★**既没进那张表、也没有合法改板通道**★ ⇒ 改板当天它们必红 (F5 判板 md5≠基线 ⇒ 红; G8 判板 md5≠受保护基线 ⇒ 红), "
    "而红的真含义是「板被换了」不是「板改坏了」⇒ 现场极可能误读⇒ 去改板凑绿⇒ 板 md5 变第二次⇒ 整趟白跑 "
    "★**⇒ 且那张表没有任何闸在守它新鲜 (本机实读: `state/gate_check.py` 零命中) ⇒ 下一道新闸再硬钉板 md5 时没人拦** ★★ "
    "⇒ ★★另: 57 处不是同一种东西 —— 判据锚 (必须随板改) / 规格页引用 (那一趟随板改·平时不许动) / 历史留证 (★永远不许改★) "
    "三类处置方式【完全相反】⇒ 「改板那天全仓 sed 替换一遍」是错的 (会把历史留证改成假记录) ⇒ 必须逐处分类 ★★ "
    "⇒ ★★本单 = ① SW 域 57 处逐处清账 (哪处随板改 / 哪处永远不许改 / 哪处交 main) ② 一条【清单新鲜度 + 缺口登记】自守闸 "
    "(★「登记过的缺口」不红, 「没人知道的缺口」才红 ⇒ 下一个新闸当场被抓住★) ③ 一条「判据锚不许伪装成历史留证」的反向判据 "
    "④ 答掉挂了两周的过期 need `iss249_kicad_sch_md5_not_anchor_sw` (★main 实测: 那两条门禁跑完 .kicad_sch md5 一字未变·且 SW 域对它的命中 = 0 ⇒ 两个前提一个不成立一个没落地★)** "
    "★【纯分析 + 作业包 + 新建闸类 · 零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 · 零挂链 · 零外发 · 不代老板拍板】★★"
)

DESC372 = (
    "★**main 2026-11-23 20:4x~20:5x 本机实读 (★不抄任何 agent 报告·全部可复跑★)★** ⇒ "
    "★**① SW 域硬写旧板 md5 的活文件实扫 (★排除 `.bak` / `__pycache__`★)★**: ★**17 个活文件 · 57 处命中** ★ —— "
    "判据脚本 3 个 (`SW/tools/check_fp_truth_read.py` 1 处 · `SW/tools/check_onepass_sw_sync.py` 5 处 · "
    "`SW/tools/check_onepass_legb_sw_impact.py` 1 处) · "
    "规格页/台账 14 个 .md (`SW/SW_MD5_BASELINE_LEDGER.md` 13 处 ★= R6/R7 的判决源★ · `SW/ONETRIP_SW_SAMEBATCH_RENAME_LIST.md` 3 · "
    "`SW/BOARD_ONEPASS_SW_SYNC.md` 3 · `SW/BOARD_ONEPASS_LEGB_SW_IMPACT.md` 4 · `SW/ONETRIP_SW_POSTRENAME_GATE_SOP.md` 4 · "
    "`SW/SW_NEEDS_TRIAGE.md` 3 · `SW/BOARD_ONEPASS_SW09_LANDING_PATCH.md` 2 · `SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md` 2 · "
    "`SW/BOARD_ONEPASS_FP_TRUTH_READ_ENTRY.md` 1 · `SW/ONETRIP_SW_RENAME_SAFETY.md` 1 · `SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md` 1 · "
    "`SW/DEMO_BOARD_60MS_VERDICT_PLAN.md` 1 · `SW/LOAD_SWITCH_SELECTION_FACTS.md` 1) · "
    "★**历史留证 1 个 (`SW/research/ISS250_r6_复核记录.md` 1 处)** ★ "
    "★**⇒ 这 57 处分三类, 处置方式【完全相反】: ①判据锚 (必须随板改·否则闸假红) ②规格页引用 (改板那一趟随板改·平时不许动) "
    "③历史留证 (★永远不许改★ ⇒ 改了就是伪造当时读数, 比留着旧数更坏★) ⇒ ★★「改板那天把 611b869e 全仓 sed 替换一遍」是【错的】★★** ★ "
    "★**② 那张「钉板 md5 的闸清单」已经过期 (★本机硬事实★)★**: `state/board_md5_pinned_gates.json` + `.md` "
    "(★由 `state/_gen_board_md5_pinned_gates.py` 一次性生成★) 生成时刻 = ★**2026-11-17 20:49** ★ · 它自己页首写的目的 (逐字) = "
    "「板只改一次那一趟 (S1~S13) 合法改板当天, 下面这 9 道闸会同时红 ⇒ 而这些红的真实含义是『板被换了』, 不是『板改坏了』 ⇒ "
    "现场极可能误读成后者 ⇒ 去改板凑绿 ⇒ 板 md5 变第二次 ⇒ 整趟白跑 ⇒ 所以板那一趟开工前, 每道钉板 md5 的闸都必须先有【合法改板】通道」★ "
    "★**本机实读那张 json = 9 条 (HW 6 / MECH 2 / SW 1·`SW/tools/check_onepass_sw_sync.py`)· 9 条全部标「已有 reboard 通道」** ★ "
    "★**★全仓实扫【真钉板 md5 的活判据脚本】⇒ 找到 3 道【今天新造 + 没有 reboard 通道 + 不在清单里】的闸★**: "
    "`SW/tools/check_fp_truth_read.py` (★ISS-363 今天 17:27 交付·L87 `BOARD_BASELINE_MD5`★) · "
    "`SW/tools/check_onepass_legb_sw_impact.py` (★ISS-370 今天 19:50 交付·L70 `PROTECTED_MD5`★) · "
    "`HW/check_iss354_manufacturability.py` (★L40 `EXPECT_PCB_MD5·hw-lead 的域★) ⇒ ★★清单是 11-17 的, 闸是 11-23 造的, 谁都没提醒谁★★** ★ "
    "★**③ 判据逻辑本机实读确认 (★所以「改板当天必红」不是猜测★)★**: "
    "`check_fp_truth_read.py` 的 F5 (L405 起) 判 `b[\"md5\"] != BOARD_BASELINE_MD5` ⇒ 追加「板 md5=%s ≠ 基线 %s ⇒ 判红 (板被换过 ⇒ 零写板自证失败)」; "
    "`check_onepass_legb_sw_impact.py` 的 G8 (L397 起) 逐个比 `PROTECTED_MD5` 的 4 个键 ⇒ 板 md5 不等就红 ⇒ ★**盘上板 md5 一变, 这两道闸立刻红** ★ "
    "★**④ 那张清单【没有任何闸在守它新鲜】★**: 本机实跑 `grep -rn board_md5_pinned_gates --include=*.py` ⇒ 只命中一次性脚本 "
    "`state/_apply_20261117_1845_main_open296_297_298.py` + 一份决策页 ⇒ `state/gate_check.py` 零命中 ⇒ ★★这张清单自生自灭★ ★ "
    "★**⑤ 挂了两周的过期 need + main 的实测反证★**: `sw.yaml` → `needs_from` → key `iss249_kicad_sch_md5_not_anchor_sw` · `to: sw-lead` · "
    "`since: 2026-11-16` · 至今未闭合 · 原文 = 「`HW/PCB/demo_mainboard*.kicad_sch` (11 个) 的 md5 真的不能当锚点 …… "
    "跑这两条门禁就会重铸随机 UUID ⇒ 任何门禁跑完 md5 都变」★ ⇒ ★**main 本机实测 (20:4x·前后各打一次 md5)★**: "
    "`check_sch_erc.py` rc=0 后 `.kicad_sch` md5 = `e433793b4a3ec321cc69f466d7e15de7` (★一字未变★) · `check_sch_pinfull.py` rc=0 后同样一字未变 "
    "⇒ ★**前提①「跑这两条门禁就会重铸随机 UUID」实测不成立** (★`check_sch_pinfull.py` 虽 `import gen_kicad_sch`, 但只用它的 `kicad_ref()` 纯函数·不重生成原理图★)★ "
    "⇒ ★**前提②「风险已落地」实测没落地** (★`grep -rn e433793b SW/` ⇒ 零命中 ⇒ SW 侧从未拿 .kicad_sch 的 md5 当过锚★) ★ "
    "⇒ ★**但必须由你自己查到底「谁会改它」: `state/gen_kicad_sch.py` L119 就是 `str(uuid.uuid4())` + L345/358/378/398/426/448 处处 `uid()` ⇒ 它本身是随机源 "
    "⇒ 请在沙盒副本上实跑一次看 md5 是否变 (★绝不许在真件上跑·那会重铸真原理图★)⇒ 结论才完整** ★ "
    "★**⑥ 权威口径与现成范本 (★照抄·不许自创★)★**: 合法改板机制的**唯一真源** = `SW/tools/check_demo_panel_spec.py` 的 **R6** (★ISS-284 已跑通★); "
    "SW 侧**已跑通**的通道样板 = `SW/tools/check_onepass_sw_sync.py` (20 处 `reboard`·交卷页 `HANDOFF/2026-11-17_sw-lead_ISS298_合法改板通道.md` 37,070 B); "
    "`reboard` **四项原子映射** = `by`/`file`/`prev_md5`/`md5` (★缺一 ⇒ 红·四项必须与落表台账链头逐字对上★); "
    "**fail-closed 三条** = 链头不唯一 / 链断 / 链头无单号 ⇒ 红 (★一条不许放宽★); "
    "`reboard: null` = 还没发生过合法改板 ⇒ **纯 md5 硬保护** (★不许为了「将来会改」就把基线放松★); "
    "已跑通的反向用例 5 条 = ⑪台账查不到那行⇒红 ⑫链头不唯一⇒红 ⑬链断⇒红 ⑭只改板不动 .kicad_pro⇒红 ⑮四项齐全⇒绿 "
    "⇒ ★**⇒ 你要交付的闸不许自己造第二套合法改板判据 ⇒ 照「只读调用权威闸」那形状** ★ "
    "★**⑦ 板面双证**: md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · size 4940213 "
    "★**⇒ 本单只出【纯分析 + 作业包 + 一条新闸 + 沙盒预演】, 一个字节都不许写板; 那 3 道闸的通道【补丁规格】交出来, 落不落交 main 排期** ★"
)

NEW = [
    {
        "id": "ISS-371",
        "title": TITLE371,
        "severity": "high",
        "source_blocker": "ISS-343",
        "source_agent": "main",
        "desc": DESC371,
        "owner": "mech-lead",
        "reporter": "main",
        "raised": "2026-11-23",
        "due": "2026-11-26",
        "status": "fixing",
        "external": False,
        "need_keys": ["iss356_jdebug_mech_clearance_recheck"],
        "task_brief": B371,
        "note": (
            "★2026-11-23 20:5x cron fb67af40 新开并【直接落 fixing】(★铁律⑩-i: 先落 fixing 再 spawn ⇒ 兄弟 job 775d9893 读同一字段 ⇒ 零撞车窗口★)★ "
            "★**开单依据**: ① `state/advance.py --json` ⇒ internal=[] (三个总工名下零 open 可派) "
            "② ★**但两个槽位是真空 (不是被占满)**: hw-lead = ISS-369 真在飞 (会话 `245328df` transcript 20:46:05 仍在写·`tmp/iss369/tools/` 20:44 仍在落盘) "
            "⇒ ★**sw-lead / mech-lead 两个槽位一个在跑会话都没有 + 名下零 open 项 ⇒ 队列对这两条线是真断的** ★ "
            "③ ★**本单是 main 本机实算出来的真缺陷 (★不是抄任何 agent 报告★)★**: 现页四处同源推导写「铜箔 X 宽 4.0850 / 单边间隙 3.0575」, "
            "而官方真 land 的 pad 是 1.0×1.0 (实测) ⇒ 铜箔 X 宽 4.8100 ⇒ Δ +0.7250 ⇒ ★★现页每个数偏乐观 0.3625mm; "
            "且清空区若仍按 4.0850 留 ⇒ 最外侧焊盘每边越界 0.3625 ⇒ 铜箔直接进清空区 ⇒ 板只改一次那一趟开工前不算清 ⇒ 板 md5 要么变第二次要么结构件返工★ ★ "
            "④ ★**它就是 `hw.yaml` 里挂了没人答的 need `iss356_jdebug_mech_clearance_recheck` (to=mech-lead·since=2026-11-23) ⇒ 本单顺手把它答掉** ★ "
            "⑤ ★**PCB 类 = 纯分析 + 追加式文档订正 + 新建闸 + 沙盒预演 ⇒ 零写板 · 零落表 ⇒ 符合「板只改一次」纪律 ①** ★ "
            "★**任务书全文**: `state/dispatch_briefs/%s`★ "
            "★**边界**: 零写板 (md5 必须仍 611b869e13518c3c023fb178f91a0075 · mtime 必须仍 2026-11-06 07:07:17.362193413 · size 仍 4940213) · "
            "零落表 (网表/脚表/BOM/落表台账/原理图/issue_log 一字不改) · 零改既有闸 (MECH 域 7 道 + check_pcb_nets/gate_check/merge/frag_write 一字不改) · "
            "零改既有页面正文 (MECH 两页只许文件末尾追加块·机器块只许加字段不许改旧字段值) · "
            "HW/PCB/BOARD_ONEPASS_WORKPACKET.md 与 MECH/BOARD_ONEPASS_MECH_CLAIMS.md 一个字都不许动 (别人的域) · 零挂链 · "
            "只写自己的分片 state/fragments/mech.yaml (只走 frag_write.py) · 沙盒只落 tmp/iss371_sbx/ + logs/iss371/ · "
            "不代老板拍板 · 零外发 (老板 2026-11-11 19:31 + 2026-11-12 02:02) · 不自签 issue_log★"
        ) % BRIEF371,
        "dispatched_at": "2026-11-23",
    },
    {
        "id": "ISS-372",
        "title": TITLE372,
        "severity": "high",
        "source_blocker": "ISS-297",
        "source_agent": "main",
        "desc": DESC372,
        "owner": "sw-lead",
        "reporter": "main",
        "raised": "2026-11-23",
        "due": "2026-11-26",
        "status": "fixing",
        "external": False,
        "need_keys": ["iss249_kicad_sch_md5_not_anchor_sw"],
        "task_brief": B372,
        "note": (
            "★2026-11-23 20:5x cron fb67af40 新开并【直接落 fixing】(★铁律⑩-i: 先落 fixing 再 spawn ⇒ 兄弟 job 775d9893 读同一字段 ⇒ 零撞车窗口★)★ "
            "★**开单依据**: ① `state/advance.py --json` ⇒ internal=[] (三个总工名下零 open 可派) "
            "② ★**但两个槽位是真空 (不是被占满)**: hw-lead = ISS-369 真在飞 ⇒ ★**sw-lead / mech-lead 一个在跑会话都没有 + 名下零 open 项** ★ "
            "③ ★**本单是 main 本机实读出来的真隐患 (★不是抄任何 agent 报告★)★**: SW 域 17 个活文件 / 57 处硬写旧板 md5, 其中 3 处是判据脚本; "
            "★**那张「钉板 md5 的闸清单」是 2026-11-17 生成的, 今天新造的 2 道 SW 闸 (ISS-363 / ISS-370) 既没进清单、也没有合法改板通道** ★ "
            "⇒ 改板当天它们必红 (F5 / G8 判据本机实读确认), 而红的真含义是「板被换了」⇒ 现场极可能误读⇒ 改板凑绿⇒ 板 md5 变第二次⇒ 整趟白跑 ⇒ "
            "★**且没有任何闸在守那张清单的新鲜度 ⇒ 下一个新闸再硬钉板 md5 时没人拦** ★ "
            "④ ★**且 57 处分三类处置方式完全相反 (判据锚 / 规格页引用 / 历史留证) ⇒ 「全仓 sed 替换一遍」是错的** ★ "
            "⑤ ★**PCB 类 = 纯分析 + 作业包 + 新建闸 + 沙盒预演 ⇒ 零写板 · 零落表 ⇒ 符合「板只改一次」纪律 ①** ★ "
            "★**任务书全文**: `state/dispatch_briefs/%s`★ "
            "★**边界**: 零写板 (md5 必须仍 611b869e13518c3c023fb178f91a0075 · mtime 必须仍 2026-11-06 07:07:17.362193413 · size 仍 4940213) · "
            "零落表 (网表/脚表/BOM/落表台账/原理图 11 个/issue_log 一字不改) · "
            "零改既有闸 (那 3 道 SW 闸 + check_demo_panel_spec/timing_check/check_shutdown_semantics + check_pcb_nets/gate_check/merge/frag_write/check_sch_erc/check_sch_pinfull 一字不改 ★只交补丁规格不落★) · "
            "零改既有页面正文 (SW_MD5_BASELINE_LEDGER 那 13 处是 R6/R7 判决源·一个字都不许动; 其余 .md 与历史留证同样不许动) · "
            "零改 state/ 下的 board_md5_pinned_gates.json/.md (main 的域·只给「刷新后应有的内容」并登记 need) · 零挂链 · "
            "只写自己的分片 state/fragments/sw.yaml (只走 frag_write.py) · 沙盒只落 tmp/iss372_sbx/ + logs/iss372/ · "
            "不代老板拍板 · 零外发 (老板 2026-11-11 19:31 + 2026-11-12 02:02) · 不自签 issue_log★"
        ) % BRIEF372,
        "dispatched_at": "2026-11-23",
    },
]


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
    applied = []
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)

        shutil.copy2(LOG, LOG + ".bak_" + STAMP)
        shutil.copy2(DLOG, DLOG + ".bak_" + STAMP)
        applied.append("备份: issue_log.yaml + dispatch_log.yaml")

        # ---------- issue_log: 文本追加 (★不全文件 yaml 重排·避免 churn★) ----------
        orig_log = open(LOG, encoding="utf-8").read()
        log = yaml.safe_load(orig_log) or {}
        issues = log.get("issues") or []
        idx = {i.get("id"): i for i in issues}
        before_ids = list(idx.keys())

        blocks = []
        for new in NEW:
            iid = new["id"]
            if iid in idx:
                it = idx[iid]
                it["status"] = new["status"]
                it["task_brief"] = new["task_brief"]
                it["note"] = new["note"]
                it["dispatched_at"] = new["dispatched_at"]
                applied.append("%s 已存在 ⇒ status→fixing + brief/note 刷新 (幂等)" % iid)
                # 幂等: 已存在则不重复追加文本
                continue
            blk = yaml.safe_dump([new], allow_unicode=True, sort_keys=False,
                                 width=100, default_flow_style=False)
            assert blk.startswith("- id:"), blk[:80]
            blocks.append(blk)
            applied.append("新开 %s (%s) · status 落 fixing (★先落 fixing 再 spawn⇒零撞车窗口★)"
                           % (iid, new["owner"]))

        if blocks:
            out = orig_log.rstrip("\n") + "\n" + "".join(blocks)
            atomic_write(LOG, out)
        else:
            out = orig_log

        # ---------- 写回自检: 前 N 条逐条完全不变 ----------
        back = yaml.safe_load(open(LOG, encoding="utf-8")) or {}
        after = back.get("issues") or []
        if len(after) != len(issues) + len(blocks):
            sys_err = ("issue_log 写回条数不对: 期望 %d, 实际 %d"
                       % (len(issues) + len(blocks), len(after)))
            raise SystemExit("★" + sys_err)
        if not all(a == b for a, b in zip(issues, after[:len(issues)])):
            raise SystemExit("★issue_log 写回自检失败: 前 %d 条有变动" % len(issues))
        applied.append("issue_log 自检: 前 %d 条逐条不变 + 新增 %d 条 ⇒ OK"
                       % (len(issues), len(blocks)))

        # ---------- dispatch_log: 文本追加 ----------
        orig_dl = open(DLOG, encoding="utf-8").read()
        dlog = yaml.safe_load(orig_dl) or []
        dl_is_dict = isinstance(dlog, dict)
        entries = dlog.get("dispatches") or [] if dl_is_dict else dlog

        dl_blocks = []
        for new in NEW:
            iid = new["id"]
            if any(e.get("issue") == iid for e in entries):
                applied.append("dispatch_log.yaml: %s 已有记录 ⇒ 不重复追加" % iid)
                continue
            entry = {
                "issue": iid,
                "agent": new["owner"],
                "at": "2026-11-23 20:5x",
                "job": ("cron fb67af40 (ARS45 队列自动派活) · ★本 job 步骤 2 的动作: "
                        "★**开单 + 直接落 fixing + spawn** (★铁律⑩-i 先落 fixing 再 spawn⇒兄弟 job 读同一字段⇒零撞车窗口★)★"),
                "brief": new["note"],
            }
            blk = yaml.safe_dump([entry], allow_unicode=True, sort_keys=False,
                                 width=100, default_flow_style=False)
            assert blk.startswith("- issue:"), blk[:80]
            dl_blocks.append(blk)
            applied.append("dispatch_log.yaml += %s %s 1 条" % (iid, new["owner"]))

        if dl_blocks:
            out_dl = orig_dl.rstrip("\n") + "\n" + "".join(dl_blocks)
            atomic_write(DLOG, out_dl)
        else:
            out_dl = orig_dl

        back_dl = yaml.safe_load(open(DLOG, encoding="utf-8")) or []
        e2 = back_dl.get("dispatches") or [] if dl_is_dict else back_dl
        if len(e2) != len(entries) + len(dl_blocks):
            raise SystemExit("★dispatch_log 写回条数不对")
        if not all(a == b for a, b in zip(entries, e2[:len(entries)])):
            raise SystemExit("★dispatch_log 写回自检失败: 前 %d 条有变动" % len(entries))
        applied.append("dispatch_log 自检: 前 %d 条逐条不变 + 新增 %d 条 ⇒ OK"
                       % (len(entries), len(dl_blocks)))

    for a in applied:
        print("·", a)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
