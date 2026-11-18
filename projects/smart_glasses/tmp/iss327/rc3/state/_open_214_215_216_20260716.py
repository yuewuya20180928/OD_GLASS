#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main 新开三单 (2026-11-16 00:5x · 队列自动派活 job fb67af40)
=================================================================
★**为什么这次要开单**: ★**`advance.py --json` 的 A 段 (internal) = 0 条** ⇒
  ★**不是没活, 是 20 条 open 全在 boss(5)/main(15) 名下, 三个总工名下 open = 0** ⇒
  ★**上一轮三条单 (ISS-211/212/213) 交卷后 status 停在 `fixing` ⇒ 本轮先清僵尸 (已落 verified)
  ⇒ 现在三个总工名额空出来了 ⇒ ★**本 job 的活 = 从各总工交卷里的 needs_from 开下一批单** ★

★**上一轮 (ISS-211/212/213) 兄弟 job 交接的口径**: 「下一轮开单来源 = 各总工交卷里的 needs_from
  + 独立的队列自动派活 job; 本 job 不自己开单」⇒ ★**开单是本 job 的活** ★

★三单全部【原理图主线内】(老板 2026-11-11 10:07 口径: PCB 布线/布局类一律不派):
  ★① ISS-214 → hw-lead  : 网表/规格自身矛盾第 2 轮 + ISS-211 三条待裁条目自己查证
  ★② ISS-215 → sw-lead  : demo 60ms 判据链的显示侧口径重锚 (ISS-212 已定的 480×640)
  ★③ ISS-216 → mech-lead: MECH_BUDGET 充电耗散 0.8W 线性口径 → buck 口径 (ISS-213 门禁已钉死)
★**三单都不许改网表 / 脚表 / 板 / .kicad_pro / 任何生成器** ⇒ 受保护 md5 一个字节不许变
★**三单都不许外发** (老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料)
★**★凡要查资料的 ⇒ 自己网上查 + 标证据等级 + 查不到必须写降级方案★** (不得把外部依赖挂着当阻塞项)

★铁律: 干活的人不许自签 ⇒ verify_by=main (main 独立复核后落账)
★不碰: PROJECT_TRACKER.md §0 / 任何分片 / 任何真源文件 (板/网表/脚表/原理图) / outbox
"""
import os
import shutil
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
BAK = LOG + ".bak_20260716_0055_open_214_215_216"

# ==================================================================
# ① ISS-214 → hw-lead
# ==================================================================
BRIEF_214 = """★**目标 (★内部活·不是 PCB 布线/布局类·不是老板级拍板★)**: 把 ★**"网表/规格自己跟自己打架"从 ISS-211 的 4 条扩到第 2 轮共 8 条**★ ⇒ 出 ★**一份落表规格 v2 + 把 ISS-211 的机器门禁扩到覆盖全部 8 条**★ ⇒ ★**本单不许改网表 / 脚表 / 板 / .kicad_pro / 任何生成器 / SPEC.json**★ ⇒ ★**零外发** ★

★★**为什么是现在 (★main 2026-11-16 00:1x~00:4x 实测, 不是推测★)** ★★
· ★**ISS-211 (11-15 23:5x 交卷, 已 verified) 把 4 条网表自相矛盾定性完了, 但它自己留了 4 条 need 给 main** ★
  (U-1 ESD 方案 / U-2 SARADC_VIN5 参数 / U-4 BAT_DET 漏电预算 / 附带发现 #1 USB 串阻双值) ⇒ ★**这些 need 里没有一条是老板级拍板, 全是"自己去查资料就能定"的活** ★
  ⇒ ★**按老板 2026-11-12 02:02「不再发信, 全靠自己查资料」的口径, 它们本来就该变成"自己查 + 标证据等级 + 查不到写降级方案", 而不是继续挂在 needs_from 上** ★
· ★**ISS-213 (11-15 23:5x 交卷, 已 verified) 又转来 5 条跨域条目, 其中 3 条落在 hw-lead 地界** ⇒ ★**同型缺陷还在往外冒** ★
· ★**但现在不能改网表**: ★**整链重出 第 1 步 (`state/RECHAIN_STEP1_LANDING_SPEC.md`) 要把 C/E/D 三项一次合并落表 ⇒ 板只改一次** ★ ⇒ ★**先落表 = 留证链/Gerber/投产包/盖印 白跑两遍** ★ ⇒ ★**所以本单 = 出规格 + 扩门禁, 让这 8 条跟着那一趟一起落** ★ (★这正是 ISS-211 已跑通的路子★)

★★**★① 八条 (★main 逐条实跑读原文, 行号就是现在的, 你要自己复核一遍再动手★)** ★★
★**第 (1) 条【ISS-211 附带发现 #1·同型】USB 串阻: 同一颗器件两个阻值** ★
· ★**网表 `HW/netlist_v1.csv` L291** = `P6,USB_D_P_SRC,J_SOM_P1 pin92,R_SER_USB_D_P,NET_USB_D_P_SRC,90Ω ±10% (与 MIPI 不同模板!),NET,必装,...`
· ★**网表 L431** = `P1,NET_USB_D_P_TYPEC,R_SER_USB_D_P,J_USB_C A6+B6,R_SER_USB_D_P,22Ω ±1%,R,必装,...`
· ★**L292 / L432 同款 (D−)** ⇒ ★**同一个 ref `R_SER_USB_D_P` / `R_SER_USB_D_N`, 前一行 90Ω, 后一行 22Ω** ★ ⇒ ★**而这两行在电气上是【串联在同一条 USB D+ 通道上】(USB_D_P_SRC → R_SER_USB_D_P → NET_USB_D_P_TYPEC → J_USB_C A6+B6)** ★
· ★**根因不在网表, 在规格源头**: ★**`HW/SCHEMATIC_V1_SPEC.json` 的 connections[40] (`signal: "USB_D+"`) 的 `imp` = `"90Ω ±10% (与 MIPI 不同模板!)"`, connections[41] (`signal: "USB_D-"`) 的 `imp` = `"90Ω ±10%"`** ★
  ⇒ ★**`state/gen_netlist.py` 第 772-774 行自己写着「value 默认取规格 imp (A 组阻抗必须与规格逐字一致 · check_netlist 判据 5)」** ★
  ⇒ ★**⇒ 真修法 = 改 SPEC.json 的 connections[40]/[41], 不是手改网表** ★ (★手改 CSV 会被下次重跑生成器覆盖 ⇒ 那就是"改在产物上", 老毛病★)
· ★**"90Ω" 本身就可疑**: ★**L291 自己的 note 就写着「与 MIPI 不同模板!」⇒ 像是 MIPI 模板串过来的** ★ ⇒ ★**但 USB 2.0 源码串阻到底该用 22Ω 还是别的值, ★【你自己查官网/官方手册原文确认, 标证据等级】★ ⇒ 别照抄我这句话** ★

★**第 (2) 条【ISS-213 转来的 PIN-MISMATCH / STK-P9】P9 页正文 21p vs 网表 22p** ★
· ★**main 实测**: ★**`HW/netlist_v1_pins.csv` 里 `CONN_LIGHT` 脚行 = 22 条 (pin1..pin22)** ★ · ★**`HW/netlist_v1.csv` 的 CONN_LIGHT 器件行 value = `★22p@0.5mm (HIROSE FH12-22S-0.5SH(55), ...)`** ★
· ★**但 `state/gen_schematic_pages.py` 第 147 行 P9 页正文写**: ★**`CONN_LIGHT` (**1×21p@0.5mm**) — ... 21 = 5V 预留 (待 JBD)** ★
· ★**⇒ 堆叠账两口径互斥**: ★**P9 页自算 (10+4+18+21)×0.5 = 26.50mm, 而同页器件表/网表的 22p 触点区口径 = 27.00mm** ★
  ⇒ ★**你要出: 22p 是真值吗 (还是该改脚表?)、堆叠账唯一口径取哪个、P9 页正文该怎么改 (改生成器 vs 改网表两条路各自代价)** ★
  ⇒ ★**注意: ★**改 `state/gen_schematic_pages.py` 就等于改原理图产物 (P9 页 svg 也在投产包里) ⇒ ★**两条路都要说清代价, 本单只出规格不许动手** ★

★**第 (3) 条【ISS-211 U-2】SARADC_VIN5 满量程 —— main 已把官方口径找出来了** ★
· ★**main 实测 (不用等原厂, 项目库里就有官方 datasheet)**: ★**`HW/RK3572_PIN_TABLE/RK3572_datasheet_V1.1.pdf` 第 3.10 节 Table 3-16 (p.45) 写: Resolution = 12 Bit, Analog Input Range AIN = AVSS18 ~ AVDD18 (即 0 ~ 1.8V)** ★
  ⇒ ★**`HW/PCB/FET3572C_PIN_TABLE.csv` 第 39 行 = `P1,38,1AE17,SARADC_VIN5,——,1.8V,General ADC5,SARADC_VIN5` ⇒ 这脚是 1.8V 域** ★
· ★**⇒ 所以 ISS-211 第 (2) 条那个"1:1 分压会烧脚"的判断成立**: ★**现网表 `HW/netlist_v1.csv` L181-L186 的 BAT_DET 链是 `1M+1M 分压 + 100nF` (L182/L183 上臂下臂 1M ±1%) ⇒ @4.2V 中点 = 2.10V ⇒ 灌进 1.8V 域 ADC ⇒ 超 AVDD18** ★
  ⇒ ★**你要出: ① 把上面这条 [官网] 口径逐字抄进规格 (附 datasheet 页码/表号) ② 给分压比候选 + 判据 (含满量程余量 / 源阻抗 / 采样时间, 查不到就写降级方案) ③ 明确现值为什么必须改** ★

★**第 (4) 条【ISS-211 U-4】BAT_DET 分压链漏电预算** ★
· ★**现状 1M+1M ⇒ 待机漏电 ~1.65µA@5V; 若改到 100k 量级 ⇒ 漏电抬约 10 倍** ★
· ★**你要出: 漏电 vs 待机功耗/续航 (老板关注 ≥1h) 的量化 + 折中判据 + 降级方案 (含"不改会怎样")** ★

★**第 (5) 条【ISS-211 U-1】USB D− 的 ESD 方案 + 型号判据** ★
· ★**现状 (main 实测)**: ★**网表里 USB 侧只有一颗 `D_ESD_USB_D` (L417/L418) = 2 焊盘, note 自称「ESD 阵列 [待选型] (USB 2.0 双通道)」, 但物理上只跨 `USB_D_P_SRC` 与 `GND`** ★
  ⇒ ★**D− 侧 (USB_D_N_SRC, L292) 0 颗 ESD** ★ ⇒ ★**"双通道"这句自称与实际不符** ★
· ★**你要出: ① D− 到底需不需要单独的 ESD (自己查 USB 2.0 / ESD 选型官方资料, 标证据等级) ② 方案二选一 (3 脚双通道阵列封装 vs 现有 2 脚件 + 另加一只 D− 件) + 型号判据 (结电容 / 钳位 / IEC 61000-4-2 等级) ③ 查不到就写降级方案** ★

★**第 (6) 条【ISS-211 已定的 4 条】I2C_A 上拉 / BAT_DET 全 DNP 但 ADC 脚必装 / U_EN_SW 无器件本体行 / USB D− 无 ESD** ★
· ★**这 4 条 ISS-211 已出规格页 + 门禁 (`HW/NETLIST_SELF_CONSISTENCY_SPEC.md` + `HW/check_netlist_selfconsistency.py`, 现状守卫 rc=0 / selftest 9/9 / 翻面口径 `--expect-resolved` rc=1)** ★
· ★**你要做的是把新 5 条并进同一套"三方对齐 (规格页 ⇄ 脚本 ⇄ 现行文件)"锚点体系**, ★**不是重写 ISS-211 的规格页** ★

★**第 (7) 条【ISS-213 转来的 THM-RATIO】`HW/CHARGE_BOARD_SPEC.md` §3.4 的 ICHG/IIN 系数方向反了** ★
· ★**main 实测**: ★**该文件第 182 行表头写「CC 段电池电流上限 (×Vbat/Vbus/η ≈ 0.822)」** ★
· ★**而 ISS-213 的机器门禁 `MECH/check_demo_struct_truth.py` G2.8 已按物理真值判: ICHG/IIN = η·Vbus/Vbat = 1.216 (3.70V) / 1.071 (4.20V), 并注明"规格书的 0.822/0.933 是倒数"** ★
  ⇒ ★**⇒ 同一件事两个文件是反的 ⇒ 而这直接决定 390Ω 档单 pin 载流 (现值说 0.50-0.61A) ⇒ 决定 R_ILIM 档位能不能定** ★
· ★**你要出: ① 用 BQ25896 datasheet 原文把系数方向定死 (★自己查官网, 不许发信, 标证据等级★) ② 连带 390Ω 档的单 pin 载流与 0.5A 触点额定天花板的关系重算 ③ 明确 §3.4 表要改成什么 (只出规格, 本单不许改那个文件)** ★

★**第 (8) 条【ISS-213 转来的 NET-LED board 列】★★main 实测与转述不一致, 以你实跑为准★★** ★
· ★**mech-lead 的 need 原话是「网表 board 列标错 —— R_CHG_LED 两端分别标 CHG_BOARD 与 MAIN_PCB」** ★
· ★**★main 自己实跑的结果: `HW/netlist_v1.csv` L508/L509 两行 `R_CHG_LED` 的 board 列 (第 13 列) 都是 `CHG_BOARD` —— 与该行 note「装在充电板 (镜框) 靠近 Type-C 座」一致 ⇒ 转述里"一端标 MAIN_PCB"这半句不成立** ★
· ★**★但同一张网上确实有一处真矛盾 (main 实跑)**: ★**net `VBUS_5V_CHG` 上, L11 `C_VBUS_OUT` 的 board = `CHG_BOARD`, 而 L12 `C_VBUS_GND` 的 board = `MAIN_PCB` ⇒ 同一颗 VBUS 电容的两端分属两块板** ★
· ★**⇒ 你要按自己的实跑重新定性 (★main 已把实跑结果给你, 是让你核对, 不是让你照抄★), 并把"转述 vs 实测不一致"这件事本身也写进规格的证据栏 (★这正是本项目反复吃过亏的地方: 别人的转述不能当事实用★)** ★

★★**★★① 你要交付什么 (★四件, 缺一件不算交卷★)** ★★
· ★**① 落表规格 v2**: ★**把 8 条并进 `HW/NETLIST_SELF_CONSISTENCY_SPEC.md` (★扩写, 不是另起炉灶★) 或另开一份 v2 并注明与 ISS-211 那份的关系** ★
  ⇒ ★**每条必须 8 栏齐全: 项号 / 现状 (逐字原文 + 行号) / 问题 / 根因 (★追到源头: SPEC.json / 生成器 / 真源网表, 不许停在网表★) / 目标取值或判据 / 该改哪张表的哪一行 / 验收判据 / 证据等级 (★[官网]/[实测]/[推算]/[0数据]★)** ★
· ★**② 机器门禁扩展**: ★**扩 `HW/check_netlist_selfconsistency.py`** ⇒ ★**新增 5 条 (本单 8 条里 ISS-211 未覆盖的) 的锚点三方对齐检查** ★
  ⇒ ★**`--selftest` 必须给每条新锚点至少 1 个反向用例 (★改坏 ⇒ 必须变红★), 并保持 9/9 原有用例一条不许删** ★ ⇒ ★**`--expect-resolved` 翻面口径现在应当是红的 (缺陷尚未落表), 你交付时也要是红的** ★
· ★**③ 交卷报告**: ★**★新建★ `HANDOFF/2026-11-16_hw-lead_ISS214_网表一致性第2轮与3条待裁自查.md`** ★ ⇒ ★**B1 结论摘要 / B2 验收标准自评 (逐条 通过/不通过/未验) / B3 证据分级 / B4 接口取值声明 / B5 未决项与卡点 (需要谁回答什么) / B6 自证复现命令 —— 六块齐全** ★
· ★**④ 分片**: ★**走 `state/frag_write.py` 原子写** ★ ⇒ ★**登记你的 artifact / claim / need (★need 一律 `to: main`★) ⇒ ★**不许用 `open(p,"w")` 直写分片** ★

★★**★★② 证据与外发的硬规矩 (★老板 2026-11-11 19:31 + 2026-11-12 02:02★)** ★★
· ★**不许外发任何邮件 / 询价 / 问询 / 采购 / 原厂问询** ⇒ ★**`state/outbox/` 里的草稿一律不发, 只作资料留档** ⇒ ★**没有"老板批一句可以发"这个选项** ★
· ★**凡要查资料 (datasheet / 选型 / 官方口径) ⇒ 自己网上查**: ★**证据等级用 [官网] (厂商官网/官方 datasheet) / [实测] (本机可复现) / [媒体] / [推算] / [0数据] (查不到)** ★
· ★**查不到时降级方案是【必须项】** (★实测样件 / 选官网参数直接满足的替代型号 / 改设计路径绕开它★) ⇒ ★**不许把外部依赖挂着当阻塞项** ★
· ★**第 (3) 条的 datasheet 已在项目库里 (`HW/RK3572_PIN_TABLE/RK3572_datasheet_V1.1.pdf`) ⇒ 那条不许写"等原厂", 你直接读** ★

★★**★★③ 边界 (★一条不许越★)** ★★
★**不许改**: ★`HW/netlist_v1.csv` · `HW/netlist_v1_pins.csv` · `HW/PCB/demo_mainboard.kicad_pcb` · `HW/PCB/demo_mainboard.kicad_pro` ·
`HW/SCHEMATIC_V1_SPEC.json` · `state/gen_netlist.py` · `state/gen_schematic_pages.py` · `HW/CHARGE_BOARD_SPEC.md` ·
`state/issue_log.yaml` · `PROJECT_TRACKER.md` §0 · `state/outbox/` · ★**任何别的总工的分片** ★
★**不许碰**: ★**PCB 布线 / 布局 / 板框** (★老板 2026-11-11 10:07: PCB 类一律不派, 排队等原理图定稿★) ★
★**受保护 md5 交卷时必须逐字节不变**: ★`HW/netlist_v1.csv` = `c78f991283cc82d56c8e3dd31657c785` ·
`HW/netlist_v1_pins.csv` = `4814617e22b567d76164e56bc5e39dc8` · `HW/PCB/demo_mainboard.kicad_pcb` = `611b869e13518c3c023fb178f91a0075` ·
`HW/PCB/demo_mainboard.kicad_pro` = `3e504d2be83152e337949723e909be1b` ★
★**§5 边界**: ★**本单 0 次外发 · 本单实物 [实测] = 0 条 (板与屏不在本机) ⇒ 凡是"实测"字样都必须说明是本机脚本实测还是纸上推算** ★

★★**★★④ 交卷前跑这三条 (rc 必须 0 / 必须贴输出)★★** ★★
★**`python3 HW/check_netlist_selfconsistency.py`** ⇒ rc=0 (现状守卫)
★**`python3 HW/check_netlist_selfconsistency.py --selftest`** ⇒ rc=0 (★原 9/9 + 你新增的反向用例全过★)
★**`python3 state/merge.py`** ⇒ rc=0 ★**且** ★**`python3 state/gate_check.py`** ⇒ rc=0 (Q1 必须 18/18)
★**★把这三条的输出原样贴进你的回复★** ★
"""

# ==================================================================
# ② ISS-215 → sw-lead
# ==================================================================
BRIEF_215 = """★**目标 (★内部活·不是 PCB 布线/布局类·不是老板级拍板★)**: 把 ★**demo 板 60ms 生死判定链的"显示侧"从退役的整机 1920×1080 口径, 重锚到 demo 屏现行 480×640 口径**★ ⇒ 出 ★**逐处定性 + 改写 + 一个能自动复核的机器门禁**★ ⇒ ★**本单不许改网表 / 脚表 / 板 / HW/ 下任何文件**★ ⇒ ★**零外发** ★

★★**为什么是现在 (★main 2026-11-16 00:2x~00:4x 实测, 不是推测★)** ★★
· ★**ISS-212 (11-15 23:5x 交卷, 已 verified) 已经把 demo 显示侧口径定版成 Waveshare 2.8" 480×640 (2-lane · 无 DCS init · I2C_B ≤100kHz)**, 并算出 demo 口径的显示侧账: ★**TX 物理下限 2.304ms (口径 A) / 2.048ms (口径 B) · t_compose ~0.44ms · 显示输出侧合计 ~2.75ms · 合成段余量 7.79ms** ★
· ★**★但 ISS-212 自己声明它没碰 4 个下游文件 ⇒ 那 4 个文件至今还是旧的 1080p 口径 (main 逐个 grep 实测) ★** ★
  ★**`SW/DEMO_OD_TIMING_SPEC.md`** ⇒ ★**`7.776` 出现 4 处 / `1920` 出现 6 处 / `10.09` 出现 4 处 / `2.32` 出现 3 处 / `4.32` 出现 4 处** ★ (行 83 / 116 / 200-204 / 225-253)
  ★**`SW/DEMO_BOARD_60MS_VERDICT_PLAN.md`** ⇒ ★**`7.776` 出现 2 处 / `10.09` 出现 3 处 / `2.32` 出现 2 处** ★ (行 66-67 / 178 / 196)
  ★**`SW/tools/rknn_bench.py` 第 258 行** ⇒ ★**`S9 = 3.0  # ms  显示输出侧 (... ★TX 物理下限 @1080p = 7.776ms★ ...)`** ★
  ★**`SW/tools/demo_timing_check.py` 第 162 / 164-166 / 236 行** ⇒ ★**断言 `t_compose` 标注 `4.32`** ★
· ★**⇒ 后果 (★这是本单的价值★)**: ★**demo 板的 60ms 生死判定现在扣的是【整机屏】的 TX 下限 7.776ms, 而 demo 屏实际只要 2.304ms ⇒ 合成段上限被算成 2.32ms, 实际是 7.79ms ⇒ ★★判据被算严了约 3.4 倍★★ ⇒ 可能把本该过的判死, 也可能掩盖真实瓶颈** ★
· ★**为什么这不是"文档没跟上"这种软问题**: ★**ISS-210 (60ms 判据链, 11-15 22:4x verified) 的生死线、ISS-137 (合成段判据) 的 10.09ms/2.32ms、ISS-212 的屏口径 —— 三块已交卷件互相打架 ⇒ 而 60ms 是老板锁死的硬指标** ★
  ⇒ ★**所以本单 = 把这三块接上, 出逐处定性 + 机器门禁, 让"demo 活动口径"和"整机路线占位"两栏彻底分开** ★

★★**★① 你要处理什么 (★两条线, 不许只做一条★)** ★★
★**线 A —— 60ms 判据链的显示侧数字 (demo 活动口径)** ★
· ★**`SW/DEMO_OD_TIMING_SPEC.md`**: ★**§2 段表第 7 段"显示帧 (1920×1080) 就绪"、§3.3.1 的 TX 7.776ms / 输出侧 10.09ms / 合成段 2.32ms / 800×600→1920×1080 ×4.32 缩放律** ★ ⇒ ★**全部要按 demo 屏 480×640 重算 (ISS-212 已给: TX 2.304ms · t_compose ~0.44ms · 输出侧合计 ~2.75ms · 合成段余量 7.79ms) ★
· ★**`SW/DEMO_BOARD_60MS_VERDICT_PLAN.md`**: ★**§段表第 7/8 段 (10.09ms / 7.776ms) + 判据第 3 条 (合计 ≤10.09ms ⇒ 合成段 ≤2.32ms) + §"② 合成/上屏侧判据"** ★ ⇒ ★**同样按 demo 屏重算** ★
· ★**`SW/tools/rknn_bench.py` 第 258 行 S9 的注记**: ★**注记里那句「TX 物理下限 @1080p = 7.776ms」是整机口径, 要改成 demo 口径 (或显式标成整机占位)** ★
  ⇒ ★**★但 S9 = 3.0 这个数值本身不许动** ★ ⇒ ★**它是 S9 模型占位, 动了会连带影响 `SW/RKNN_BENCH.md` §4.1 的 S9 标签与那边已发布的 21/21 + 9/9 锚点 ⇒ ★**你要自己确认改注记的连带影响并写清, 别自作主张改数值** ★
· ★**`SW/tools/demo_timing_check.py` 第 162/164-166/236 行的 `4.32` 断言**: ★**那是"缩放律 ×4.32"的机器锚点 ⇒ demo 屏口径下缩放律变成 ÷6.75 (2.07 Mpx → 0.307 Mpx) ⇒ 断言要跟着改, 且要有反向用例** ★

★**线 B —— "整机路线占位"那几处不许删, 要显式标住** ★
· ★**ISS-212 的定性表已经把这类处理立成规矩了 (见 `SW/DEMO_PANEL_SPEC_TRIAGE.md` L-08 / L-16: 同一行里既写 demo 活动口径, 又把整机 1080p 那套数作为"整机路线·暂缓"在同一行注明)** ★
· ★**⇒ 你在 60ms 判据链上也照这个规矩办: ★**整机 1080p 的那些数 (7.776 / 10.09 / 2.32 / 4.32) 不是"错", 它们属于整机路线 (整机屏 0.49" 视涯) ⇒ 正确处置是分栏 + 显式标注, 不是删掉、也不是留着冒充 demo 口径** ★
· ★**★特别提醒: `HW/e2e_budget_rk3572.py` 是整机 1080p 口径的权威源头 (它自测里钉死「TX_MIN_1080 = 7.776 不许被悄悄改小」) ⇒ ★**那是 HW 地界, 本单不许动它; demo 口径的新账要另立锚点, 不许去改整机那个源头** ★**

★★**★★② 你要交付什么 (★四件, 缺一件不算交卷★)** ★★
· ★**① 逐处定性表**: ★**一份 md, 把线 A 那 4 个文件里【凡是 1080p 口径的显示侧数字】逐处列出来 (文件 + 行号 + 原文 + 判定: demo 活动口径 / 整机路线占位 / 历史留档 / 说明文字)** ★
  ⇒ ★**判定只有这四档, 不许有"待定"** ★ ⇒ ★**数量必须与 grep 命中数对得上 (你自己给命令)** ★
· ★**② 改写**: ★**改 `SW/DEMO_OD_TIMING_SPEC.md` · `SW/DEMO_BOARD_60MS_VERDICT_PLAN.md` · `SW/tools/rknn_bench.py` (只许改注记, 不许改 S9 数值) · `SW/tools/demo_timing_check.py`** ★
  ⇒ ★**每一处改动都要能指回 ISS-212 的哪一个数 (TX 2.304 / 2.048 · t_compose 0.44 · 输出侧 2.75 · 余量 7.79)** ★
· ★**③ 机器门禁**: ★**扩 `SW/tools/demo_timing_check.py`** ⇒ ★**新增断言: ★**demo 活动口径的位置不许再出现 `7.776` / `10.09` / `2.32` / `4.32` (整机占位的位置必须带显式标注, 且不在 demo 活动栏)★; ★**每条新断言配 ≥1 个反向用例 (改坏 ⇒ 必须变红)** ★
· ★**④ 交卷报告 + 分片**: ★**★新建★ `HANDOFF/2026-11-16_sw-lead_ISS215_demo60ms判据链显示侧重锚.md` (B1~B6 六块齐全)** ★ + ★**分片走 `state/frag_write.py` 原子写 (artifact / claim / need, need 一律 `to: main`)** ★

★★**★★③ 口径纪律 (★一条不许松★)** ★★
· ★**60ms 硬指标本身不许动** ★ · ★**ISP 判据 15.10 / 17.33ms (ISS-124 发布值) 不许调松** ★ · ★**S9 = 3.0 数值不许动** ★
· ★**板端一切 = [0数据]** ⇒ ★**不许编造板端时延数字; 板端实测 = 待执行, 不是已验证** ★
· ★**新出现的数必须标证据等级**: ★**[推算] (按像素数线性缩放 + 官方带宽口径) / [官网] (面板官方规格) / [实测] (本机脚本跑出来) / [0数据] (板端)** ★
· ★**每改一处都要留"这个数从哪来"** ⇒ ★**不许出现"按比例估一下"这种没有出处的数** ★

★★**★★④ 边界 (★一条不许越★)** ★★
★**不许改**: ★`HW/` 下任何文件 (★含 `HW/e2e_budget_rk3572.py` —— 那是整机 1080p 口径的权威源头★) · `HW/netlist_v1.csv` · `HW/PCB/demo_mainboard.kicad_pcb` ·
`HW/PCB/demo_mainboard.kicad_pro` · `state/issue_log.yaml` · `PROJECT_TRACKER.md` §0 · `state/outbox/` · ★**任何别的总工的分片** ★
★**不许改 ISS-212 已交付的产物**: ★`SW/DEMO_PANEL_WAVESHARE_2P8_SPEC.md` · `SW/DEMO_PANEL_SPEC_TRIAGE.md` · `SW/tools/check_demo_panel_spec.py` (★只引用, 不许改★)
★**不许碰**: ★**PCB 布线 / 布局** ★
★**受保护 md5 交卷时必须逐字节不变**: ★`HW/netlist_v1.csv` = `c78f991283cc82d56c8e3dd31657c785` ·
`HW/PCB/demo_mainboard.kicad_pcb` = `611b869e13518c3c023fb178f91a0075` · `HW/PCB/demo_mainboard.kicad_pro` = `3e504d2be83152e337949723e909be1b` ·
★**`HW/e2e_budget_rk3572.py` 的 md5 也要贴出来 (它是整机口径源头, 本单不许动它)** ★
★**§5 边界**: ★**本单 0 次外发 · 本单实物 [实测] = 0 条** ★

★★**★★⑤ 交卷前跑这三条 (rc 必须 0 / 必须贴输出)★★** ★★
★**`python3 SW/tools/demo_timing_check.py`** ⇒ rc=0 (含你新增的断言与反向用例)
★**`python3 SW/tools/check_demo_panel_spec.py`** ⇒ rc=0 (★ISS-212 的门禁不许被你改红★)
★**`python3 state/merge.py`** ⇒ rc=0 ★**且** ★**`python3 state/gate_check.py`** ⇒ rc=0 (Q1 必须 18/18)
★**★把这三条的输出原样贴进你的回复★** ★
"""

# ==================================================================
# ③ ISS-216 → mech-lead
# ==================================================================
BRIEF_216 = """★**目标 (★内部活·不是 PCB 布线/布局类·不是老板级拍板★)**: 把 ★**结构侧"充电耗散"这条热学口径从"线性充电 IC 0.8W"改成"buck 0.45-0.57W"**, 让 ★**文档 / 计算脚本 / 机器门禁三处一致**★ ⇒ ★**本单不许改 HW/ 下任何文件 / 不许碰 PCB 布线布局**★ ⇒ ★**零外发** ★

★★**为什么是现在 (★main 2026-11-16 00:3x 实测, 不是推测★)** ★★
· ★**ISS-213 (11-15 23:5x 交卷, 已 verified) 的机器门禁 `MECH/check_demo_struct_truth.py` 的 G2.5 / G2.6 / G2.8 已经按 buck 口径判了**: ★**端件温升 ΔT = 83.33K ⇒ 表面 108.33°C · 60°C 判据 ⇒ P_max = 0.210W (现耗散 0.50W ⇒ 超 2.38× ⇒ 必须金属热路) · ICHG/IIN = η·Vbus/Vbat = 1.216 (3.70V) / 1.071 (4.20V), 并注明"规格书的 0.822/0.933 是倒数"** ★
· ★**★但同一批数字在另外两个文件里还是反的 (main 逐行实跑) ★** ★
  ★**`MECH/MECH_BUDGET.md` 第 497 行**: ★**`| **B. 峰值: 充电** | Type-C 输入 (5V) + 线性充电 IC | **0.8 W @ 1A** (IC 自身耗散 = (5−4.2)V × 1A) | [推算]; 充电 IC 拓扑参考 MPS MP26029/MP2710/MP2721 资料 [官网] |`** ★
  → ★**① 拓扑引错了**: ★**我们板上 P10 充电板是开关型 buck (BQ25896), 不是 MPS 那几颗线性料** ★
  → ★**② 公式是线性 IC 的 (5−4.2)×1A, buck 不是这么算的** ★
  ★**`MECH/MECH_BUDGET.md` 第 501 行 / 第 596 行**: ★**结构硬结论两处都写「充电 IC 的 0.8W 耗散必须落在不接触皮肤的位置」** ★
  ★**`MECH/verify_budget.py` 第 45 行**: ★**`P_CHARGE = 0.8  # W [推算] 线性充电 IC 耗散 (5V-4.2V) × 1A`** ★ → ★**第 232-234 行 §2 充电峰值场景用它算皮肤温度** ★
· ★**⇒ 同一个物理量, 门禁按 buck 判, 文档按线性算 ⇒ 而 §2.1/§2.3.1/§3 三处结构结论都挂在它上面 (充电板必须挪出贴皮肤处 / 端件必超温 / 必须金属热路)** ★
· ★**⇒ 本单价值 = 把这条口径一次收干净, 让"文档 / 脚本 / 门禁"三处说同一句话** ★

★★**★① 你要交付什么 (★四件, 缺一件不算交卷★)** ★★
· ★**① 口径统一 (文档侧)**: ★**改 `MECH/MECH_BUDGET.md`**: ★**① §2.1 峰值充电行的耗散值与算法改成 buck (Pin − Pout + DCR), 拓扑引用改成板上真实器件 (BQ25896, 走官网口径, 标证据等级) ② 第 501 / 596 行的结构硬结论跟着改 (0.8W → 新值, 并把结论按新值重述) ③ §2.3.1 充电峰值场景 + §3 重量表里受影响的数字连带改** ★
  ⇒ ★**ISS-213 的原话是「§2.1 写 0.8 W @ 1A (IC 自身耗散 = (5−4.2)V × 1A) = 线性充电 IC 公式, 而 P10 充电板是开关型 buck ⇒ 耗散应按 Pin − Pout + DCR = 0.45–0.57W ⇒ 端件外表面温升 83K ⇒ 108°C (0.8W 口径是 133K ⇒ 158°C) ⇒ 60°C 判据 ⇒ P_max = 0.21W ⇒ 必须金属热路」—— ★**这一段是 ISS-213 给你的输入, 你要自己复核后再落** ★
· ★**② 计算脚本对齐**: ★**改 `MECH/verify_budget.py` 的 `P_CHARGE` 常量 (第 45 行) + §2 充电峰值场景的输出** ★
  ⇒ ★**★★关键: 该脚本自带"文档 vs 脚本"逐项对拍 (当前 39/39 项与文档一致) ⇒ ★**你改了常量, 39/39 里凡是依赖它的项必须同时改文档, 否则脚本会红 ★★⇒ ★**这就是你这单真正的机器门禁: 改完之后它必须仍然 39/39 (或新的 N/N) 全绿** ★
· ★**③ 新增一条"口径自检" + 反向用例**: ★**让 `MECH/verify_budget.py` 能自检"充电耗散口径 = buck 而不是线性"** ⇒ ★**例如断言 `P_CHARGE` 落在 buck 区间 (0.45-0.57) 且注释/文档里带 buck 口径标识; 并加 `--selftest` 反向用例 (把常量改回 0.8 ⇒ 必须变红)** ★
  ⇒ ★**该脚本现在没有 `--selftest` ⇒ 你要新建这个模式 (★照 `MECH/check_demo_struct_truth.py --selftest` 的写法★)** ★
· ★**④ 交卷报告 + 分片**: ★**★新建★ `HANDOFF/2026-11-16_mech-lead_ISS216_充电耗散口径统一.md` (B1~B6 六块齐全)** ★ + ★**分片走 `state/frag_write.py` 原子写** ★
  ⇒ ★**ISS-213 已把两条 claim 落过分片了 (`mech_endpoint_surface_temp_caliber` / `mech_mech_budget_linear_0p8w_dead`) ⇒ ★**你改完把这两条的取值对齐 (走 frag_write, 不许手改分片)** ★

★★**★★② 一条不许顺带松的判据 (★本单最容易被顺手改坏的地方★)** ★★
· ★**判据阈值一个不许顺带松**: ★**cavity_req 4.50 · CRIT 0.60 · cav_v 38.00 · duct_v 6.00** ★
· ★**板框四数不许动**: ★**60.00 / 30.00 / 1.00 / 3.33g** ★
· ★**★★"把 0.8W 改成 0.5W" 本身就是一次判据变动 —— 所以你的交卷必须写清: 这不是放宽阈值, 是把公式换成板上真实拓扑的公式; 且改完之后所有受影响的结论要一条条重列 (哪些结论方向不变 / 哪些变 / 哪些需要 main 重新裁决)★** ★
· ★**例如 (你自己复核后写)**: ★**端件表面 108°C vs 60°C 判据 ⇒ 仍超 ⇒ "必须金属热路"这条结论方向不变; 但 P_max 从 (60−25)/166.67 推出的数、以及 §3 重量表的连带值要重算** ★
· ★**`MECH/HW_CROSS_REVIEW_TRIAGE.md` 里 ISS-213 已定的 17 条 FAIL 仍然是 FAIL (排队等原理图定稿) —— ★**本单不许把它们改成 PASS** ★

★★**★★③ 边界 (★一条不许越★)** ★★
★**不许改**: ★`HW/` 下任何文件 (★网表 / 脚表 / 板 / .kicad_pro★) · `MECH/hw_cross_review_check.py` · `MECH/hinge_usb_check.py` ·
`MECH/service_port_check.py` · `MECH/display_biosafety_v2_check.py` · `MECH/check_demo_struct_truth.py` (★ISS-213 的门禁, 含它的 md5 锚点★) ·
`MECH/HW_CROSS_REVIEW_TRIAGE.md` (★只引用★) · `state/issue_log.yaml` · `PROJECT_TRACKER.md` §0 · `state/outbox/` · ★**任何别的总工的分片** ★
★**不许碰**: ★**PCB 布线 / 布局 / 板框** ★ · ★**打印包基线 (`MECH/print/`) —— ★**ISS-213 说的"打印包第三档试样"是【另一件事】(要动 Rev B 打印包 93/93 + 38/38 基线), ★**本单不许顺手做, 不许动打印包任何文件** ★
★**受保护 md5 交卷时必须逐字节不变**: ★`MECH/hinge_usb_check.py` = `3425bc141508de8a35f34c7cf7b803e8` ·
`MECH/service_port_check.py` = `9b24bf985764880f0105aee677fba6a8` · `MECH/hw_cross_review_check.py` = `e521387b87b0fcdf9f22d56f14199967` ·
`MECH/display_biosafety_v2_check.py` = `29c77fc3fc823048b1d96c9500d28dd7` ·
`HW/netlist_v1.csv` = `c78f991283cc82d56c8e3dd31657c785` · `HW/PCB/demo_mainboard.kicad_pcb` = `611b869e13518c3c023fb178f91a0075` ·
`HW/PCB/demo_mainboard.kicad_pro` = `3e504d2be83152e337949723e909be1b`
★**§5 边界**: ★**本单 0 次外发 · 本单实物 [实测] = 0 条 (板不在本机) ⇒ 端件 108°C 之类全是 [推算]** ★

★★**★★④ 交卷前跑这四条 (rc 必须 0 / 必须贴输出)★★** ★★
★**`python3 MECH/verify_budget.py`** ⇒ rc=0 (★文档 vs 脚本 逐项对拍全绿★)
★**`python3 MECH/verify_budget.py --selftest`** ⇒ rc=0 (★你新建的自检 + 反向用例★)
★**`python3 MECH/check_demo_struct_truth.py`** ⇒ rc=0 (★20/20 全过, 且它的 17 条 FAIL 仍然是 FAIL★)
★**`python3 state/merge.py`** ⇒ rc=0 ★**且** ★**`python3 state/gate_check.py`** ⇒ rc=0 (Q1 必须 18/18)
★**★把这几条的输出原样贴进你的回复★** ★
"""

NEW = [
    {
        "id": "ISS-214",
        "title": ("★★[主线内·原理图/网表侧·内部活] 网表/规格自身矛盾第 2 轮 (USB 串阻双值 / P9 页 21p vs 22p / SARADC 满量程 / BAT_DET 漏电 / USB D− 无 ESD / ICHG 系数方向反 / NET-LED board 列) "
                  "⇒ 出落表规格 v2 + 扩机器门禁 (不改网表·不改板·不改生成器·零外发)"),
        "severity": "high",
        "source_blocker": "HW-B3",
        "desc": ("★**ISS-211 (11-15 23:5x 交卷, 已 verified) 把 4 条网表自相矛盾定性完, 但自己留了 4 条 need 给 main (U-1 ESD 方案 / U-2 SARADC_VIN5 参数 / U-4 BAT_DET 漏电预算 / 附带发现 #1 USB 串阻双值) ⇒ "
                  "这些没有一条是老板级拍板, 全是【自己查资料就能定】的活 ⇒ 按老板 2026-11-12 02:02「不再发信, 全靠自己查资料」的口径, 它们本来就该变成「自己查 + 标证据等级 + 查不到写降级方案」, 而不是继续挂在 needs_from 上** ★ "
                  "★**ISS-213 (同轮交卷, 已 verified) 又转来 5 条跨域条目, 其中 3 条落在 hw-lead 地界 ⇒ 同型缺陷还在往外冒** ★ "
                  "★**main 2026-11-16 00:1x~00:4x 逐条实跑复核后确认 8 条全部成立, 且其中 3 条是 main 自己新挖出来的**: ★**① USB 串阻双值的根因 = `HW/SCHEMATIC_V1_SPEC.json` connections[40]/[41] 的 imp 写 '90Ω ±10%', 而网表 L431/L432 器件行写 '22Ω ±1%', 且 `state/gen_netlist.py:772-774` 明确「value 默认取规格 imp」⇒ 手改 CSV 会被生成器覆盖** ★ "
                  "★**② P9 页正文 21p vs 网表/脚表 22p (脚表实测 CONN_LIGHT = pin1..pin22) ⇒ 堆叠账 26.50 vs 27.00 两口径互斥** ★ "
                  "★**③ SARADC_VIN5 满量程 main 已从项目库内官方 datasheet (`HW/RK3572_PIN_TABLE/RK3572_datasheet_V1.1.pdf` §3.10 Table 3-16, p.45: Resolution 12 Bit, AIN = AVSS18~AVDD18) 查到 ⇒ 1.8V 域, 现有 1M+1M 分压 @4.2V 中点 2.10V 确实超 AVDD18 ⇒ 不需要等原厂** ★ "
                  "★**④ CHARGE_BOARD_SPEC.md:182 的 ICHG/IIN 系数方向反了 (写 ×Vbat/Vbus/η ≈ 0.822, 物理真值 η·Vbus/Vbat = 1.216/1.071) ⇒ 直接决定 390Ω 档单 pin 载流与 R_ILIM 档位** ★ "
                  "★**⑤ NET-LED 那条: mech-lead 的转述说 'R_CHG_LED 两端分别标 CHG_BOARD 与 MAIN_PCB', 但 main 实跑 L508/L509 两行 board 列都是 CHG_BOARD ⇒ 转述那半句不成立; 真矛盾在同网 L11 C_VBUS_OUT=CHG_BOARD vs L12 C_VBUS_GND=MAIN_PCB (同一颗电容两端分属两块板) ⇒ 本单要求以实跑为准重新定性** ★ "
                  "★**现在不能改网表**: 整链重出第 1 步 (`state/RECHAIN_STEP1_LANDING_SPEC.md`) 要把 C/E/D 三项一次合并落表 ⇒ 板只改一次 ⇒ 本单 = 出规格 + 扩门禁, 让 8 条跟着那一趟一起落 (ISS-211 已跑通的路子)** ★"),
        "owner": "hw-lead",
        "reporter": "main",
        "raised": "2026-11-16",
        "due": "2026-11-19",
        "status": "open",
        "external": "False",
        "need_keys": "[]",
        "fix_ref": None,
        "verify_by": "main",
        "verify_result": None,
        "verify_date": None,
        "note": ("2026-11-16 00:5x 队列自动派活 job (fb67af40) 新开 ★**依据 = ISS-211/ISS-213 交卷里的 needs_from + main 2026-11-16 00:1x~00:4x 实跑复核 (8 条全部成立, 其中 3 条 main 新挖)** ★ "
                 "★**上一轮 (ISS-211/212/213) 的僵尸 fixing 已于本轮 00:3x 清掉并落 verified ⇒ 三个总工名额空出来 ⇒ 本单是第 2 轮** ★"),
        "task_brief": BRIEF_214,
    },
    {
        "id": "ISS-215",
        "title": ("★★★[demo 头号路径·自己查版·软件/时序侧] demo 板 60ms 生死判定链的显示侧口径重锚: 从退役的整机 1920×1080 (TX 7.776ms / 输出侧 10.09ms / 合成段 2.32ms) 改到 demo 屏现行 480×640 (TX 2.304ms / 输出侧 ~2.75ms / 余量 7.79ms) ⇒ 判据被算严了 3.4 倍 ⇒ 逐处定性 + 改写 + 机器门禁"),
        "severity": "high",
        "source_blocker": "PM-B5",
        "desc": ("★**ISS-212 (11-15 23:5x 交卷, 已 verified) 已把 demo 显示侧口径定版成 Waveshare 2.8\" 480×640 (2-lane · 无 DCS init · I2C_B ≤100kHz), 并算出 demo 口径的显示侧账 (TX 物理下限 2.304ms 口径 A / 2.048ms 口径 B · t_compose ~0.44ms · 显示输出侧合计 ~2.75ms · 合成段余量 7.79ms)** ★ "
                  "★**★但 ISS-212 自己声明没碰的 4 个下游文件, 至今仍是旧的 1080p 口径 (main 2026-11-16 00:2x 逐个 grep 实测)**: ★**`SW/DEMO_OD_TIMING_SPEC.md` (7.776×4 / 1920×6 / 10.09×4 / 2.32×3 / 4.32×4)** ★ · "
                  "★**`SW/DEMO_BOARD_60MS_VERDICT_PLAN.md` (7.776×2 / 10.09×3 / 2.32×2)** ★ · ★**`SW/tools/rknn_bench.py:258` (S9 注记里写「TX 物理下限 @1080p = 7.776ms」)** ★ · ★**`SW/tools/demo_timing_check.py:162/164-166/236` (断言 t_compose 标注 4.32)** ★ "
                  "★**⇒ 后果: demo 板的 60ms 生死判定现在扣的是【整机屏】的 TX 下限, 合成段上限被算成 2.32ms, 实际 7.79ms ⇒ 判据被算严了约 3.4 倍 ⇒ 可能把本该过的判死, 也可能掩盖真实瓶颈** ★ "
                  "★**这已不是「文档没跟上」这种软问题: ISS-210 (60ms 判据链, 已 verified) 的生死线 / ISS-137 (合成段判据) 的 10.09ms+2.32ms / ISS-212 的屏口径 —— 三块已交卷件互相打架, 而 60ms 是老板锁死的硬指标** ★ "
                  "★**处理规矩: 整机 1080p 那些数不是「错」, 它们属于整机路线 (整机屏 0.49\" 视涯) ⇒ 正确处置是分栏 + 显式标注「整机路线·暂缓」, 不是删掉, 也不是留着冒充 demo 口径 (沿用 ISS-212 定性表 L-08/L-16 的成例)** ★ "
                  "★**`HW/e2e_budget_rk3572.py` 是整机 1080p 口径的权威源头 (自测钉死 TX_MIN_1080 = 7.776 不许被悄悄改小) ⇒ HW 地界, 本单不许动它; demo 口径另立锚点** ★"),
        "owner": "sw-lead",
        "reporter": "main",
        "raised": "2026-11-16",
        "due": "2026-11-19",
        "status": "open",
        "external": "False",
        "need_keys": "[]",
        "fix_ref": None,
        "verify_by": "main",
        "verify_result": None,
        "verify_date": None,
        "note": ("2026-11-16 00:5x 队列自动派活 job (fb67af40) 新开 ★**依据 = ISS-210 / ISS-137 / ISS-212 三块已交卷件之间的口径断点 + main 2026-11-16 00:2x 逐文件 grep 实测 (命中数已逐个记在 desc 里)** ★ "
                 "★**sw-lead 名额的上一条 (ISS-212) 已于本轮 00:3x 落 verified ⇒ 名额空出来 ⇒ 本单是第 2 轮** ★"),
        "task_brief": BRIEF_215,
    },
    {
        "id": "ISS-216",
        "title": ("★★[主线内·结构侧·内部活] MECH_BUDGET 充电耗散口径统一: 线性充电 IC 0.8W → 板上真实 buck (BQ25896) 0.45-0.57W ⇒ 文档 §2.1/§2.3.1/§3 + verify_budget.py 常量 + 门禁锚点对齐 + 新增 --selftest 口径自检 (端件 108°C / P_max 0.21W / 必须金属热路)"),
        "severity": "high",
        "source_blocker": "MECH-B2",
        "desc": ("★**ISS-213 (11-15 23:5x 交卷, 已 verified) 的机器门禁 `MECH/check_demo_struct_truth.py` G2.5/G2.6/G2.8 已按 buck 口径判 (端件 ΔT 83.33K ⇒ 108.33°C · 60°C 判据 ⇒ P_max 0.210W, 现耗散 0.50W ⇒ 超 2.38× ⇒ 必须金属热路 · ICHG/IIN = 1.216/1.071, 注明规格书的 0.822/0.933 是倒数)** ★ "
                  "★**★但同一批数字在另外两个文件里还是反的 (main 2026-11-16 00:3x 逐行实跑)**: ★**`MECH/MECH_BUDGET.md:497` 写「0.8 W @ 1A (IC 自身耗散 = (5−4.2)V × 1A)」且拓扑引用 MPS MP26029/MP2710/MP2721 (线性料), 而我们板上 P10 是 BQ25896 开关型 buck** ★ · "
                  "★**`MECH/MECH_BUDGET.md:501` 与 `:596` 两处结构硬结论都挂在这个 0.8W 上** ★ · ★**`MECH/verify_budget.py:45` 的 `P_CHARGE = 0.8` (注释「线性充电 IC 耗散」) 喂给第 232-234 行 §2 充电峰值场景算皮肤温度** ★ "
                  "★**⇒ 同一个物理量, 门禁按 buck 判 / 文档按线性算 ⇒ §2.1 / §2.3.1 / §3 三处结构结论都挂在它上面 ⇒ 本单价值 = 一次收干净, 让文档 / 脚本 / 门禁三处说同一句话** ★ "
                  "★**注: 该脚本自带「文档 vs 脚本」逐项对拍 (当前 39/39 全绿) ⇒ 改常量后文档必须同步, 否则脚本变红 ⇒ 这就是本单真正的机器门禁** ★ "
                  "★**ISS-213 同时把两条 claim 落过分片 (`mech_endpoint_surface_temp_caliber` / `mech_mech_budget_linear_0p8w_dead`) ⇒ 本单改完要把取值对齐 (走 frag_write)** ★"),
        "owner": "mech-lead",
        "reporter": "main",
        "raised": "2026-11-16",
        "due": "2026-11-19",
        "status": "open",
        "external": "False",
        "need_keys": "[]",
        "fix_ref": None,
        "verify_by": "main",
        "verify_result": None,
        "verify_date": None,
        "note": ("2026-11-16 00:5x 队列自动派活 job (fb67af40) 新开 ★**依据 = ISS-213 交卷时登记给 main 的 need `iss213_mech_mech_budget_charge_caliber_text` + main 2026-11-16 00:3x 逐行实跑复核 (文档 / 脚本 / 门禁三处口径不一致全部成立)** ★ "
                 "★**mech-lead 名额的上一条 (ISS-213) 已于本轮 00:3x 落 verified ⇒ 名额空出来 ⇒ 本单是第 2 轮** ★"),
        "task_brief": BRIEF_216,
    },
]


def atomic_write(path: str, data: str) -> None:
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".issue_log.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
        dfd = os.open(d, os.O_RDONLY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def main() -> int:
    import fcntl
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        with open(LOG, encoding="utf-8") as f:
            raw = f.read()
        log = yaml.safe_load(raw)

        rt = yaml.safe_dump(log, allow_unicode=True, sort_keys=False, width=200)
        if rt != raw:
            print("❌ yaml 往返不一致 ⇒ 拒绝落盘")
            return 2
        print("✅ yaml 往返逐字节一致 (自证通过)")

        issues = log.get("issues") or []
        by_id = {i.get("id"): i for i in issues}
        for n in NEW:
            iid = n["id"]
            assert iid not in by_id, "%s 已存在 ⇒ 中止" % iid
            assert n["owner"] in ("hw-lead", "sw-lead", "mech-lead"), "%s owner 非法" % iid
            assert n["verify_by"] == "main", "%s verify_by 必须 main" % iid
            assert n["severity"] in ("blocker", "high", "medium", "low"), "%s severity 非法" % iid
            issues.append(n)
            print(" - 新开 %s → %s (%s)" % (iid, n["owner"], n["title"][:40]))

        log["issues"] = issues
        shutil.copy2(LOG, BAK)
        atomic_write(LOG, yaml.safe_dump(log, allow_unicode=True, sort_keys=False, width=200))
        print("备份:", BAK)
        print("issues 总数:", len(issues))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
