#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main 新开三单 (2026-11-15 23:5x · 队列自动派活 job fb67af40)
=================================================================
★背景: ★**`advance.py --json` 的 A 段 (internal) = 0 条** ⇒ 不是没活, 是
  ★**20 条 open 全在 boss(5) / main(15) 名下, 三个总工名下 open = 0** ⇒
  ★**兄弟 job (ARS45 继续执行后继计划) 上一轮明确交接**:
  ★「下一轮开单来源 = 各总工交卷里的 needs_from + **独立的『队列自动派活』job**;
  ★  **本 job 不自己开单, 避免撞车**」⇒ ★**开单是本 job 的活** ★
  ★本轮三单全部来自各总工交卷里**未答**的 needs_from (self.yaml / hw.yaml / mech.yaml) ★

★三单全部【原理图主线内】(老板 2026-11-11 10:07 口径):
  ★① ISS-211 → hw-lead  : 网表自身一致性 4 处 (原理图/网表/选型)
  ★② ISS-212 → sw-lead  : demo 显示侧口径重锚到 Waveshare 2.8" (软件/显示)
  ★③ ISS-213 → mech-lead: 结构真源 54 项逐条定性 + demo 板真缺陷收口 (结构)
  ★**三单都不许改网表 / 板 / 脚表 / .kicad_pro** ⇒ 受保护 md5 一个字节不许变
  ★**三单都不许外发** (老板 2026-11-11 19:31 + 2026-11-12 02:02)

★铁律: 干活的人不许自签 ⇒ verify_by=main (main 独立复核后落账)
★不碰: PROJECT_TRACKER.md §0 / 任何分片 (含 mech.yaml 的 U-3 订正 ⇒ 交 mech-lead 自己在 ISS-213 里改)
       / 任何真源文件 (板/网表/脚表/原理图) / outbox / issue_log 的既有条目状态
"""
import os
import shutil
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")

# ==================================================================
# ① ISS-211 → hw-lead
# ==================================================================
BRIEF_211 = """★**目标 (★内部活·不是 PCB 布线/布局类·不是老板级拍板★)**: 把 ★**现行网表自身 4 处"自己跟自己打架"的地方一次性收口**★ ⇒ 出 ★**一份逐条落表规格 + 一个能自动复核的机器门禁**★ ⇒ ★**本单不许改网表 / 不许改板 / 不许改生成器**★ ⇒ ★**零外发** ★

★★**为什么是现在 (★main 2026-11-15 23:2x~23:4x 实测, 不是推测★)** ★★
· ★**这 4 条不是"文档没跟上"这种软问题, 是同一张网表里两行字直接互相否定**★ ⇒ ★**下一个读网表的人 (评审人 / 板厂 / 另一个总工) 会拿到错的那一行**★ ⇒ ★**其中第 (2) 条会让 SoC 的 ADC 输入脚悬空, 第 (3) 条会让一颗 4 脚 IC 在 BOM 里被登记成 NET 行**★ ⇒ ★**投板前必须收口** ★
· ★**但现在不能改网表**: ★**整链重出 第 1 步 (`state/RECHAIN_STEP1_LANDING_SPEC.md`) 要把 C/E/D 三项一次合并落表 ⇒ 板只改一次** ★ ⇒ ★**先落表 = 留证链/Gerber/投产包/盖印 白跑两遍** ★ ⇒ ★**所以本单 = 出规格 + 出门禁, 让这 4 条跟着那一趟一起落** ★ (★这是 ISS-191 / ISS-174 已验证过的路子★)

★★**★① 四条缺陷 (★main 逐条实跑读原文, 行号就是现在的, 你要自己复核一遍再动手★)** ★★
★**第 (1) 条: I2C_A 上拉 —— 网线行说 4.7k/3.3V, 器件行说 2.2k/1.8V** ★
· ★**网表 `HW/netlist_v1.csv` L167** = `P2,I2C_A_SCL,J_SOM_P2 pin31,R_PU_I2CA_SCL,NET_I2C_A_SCL,"上拉 4.7k 到 3.3V (灌 702µA, t_r=2.38µs@100pF)",NET,必装,...` ★
· ★**网表 L169** = `P2,VDD_1V8_IO,R_PU_I2CA_SCL,RAIL_VDD_1V8_IO,R_PU_I2CA_SCL,2.2k ±1%,R,必装,...` ⇒ ★**同一个 ref `R_PU_I2CA_SCL`, 前一行说 4.7k 上拉到 3.3V, 后一行说 2.2k 上拉到 1.8V** ★ (★L168/L170 = SDA 同款★)
· ★**L169 自己的 note 已经把 3.3V 那句判成作废**: ★「★★11-04 ISS-153 订正: **实际 net = RAIL_VDD_1V8_IO (1.8V 域)**; ★**旧注释写的『[VDD_3V3_IO] / 3.3V 上拉』与网表相反, 已作废**」★ ⇒ ★**L167/L168 还在逐字复述那句"已作废"的话** ★
· ★**另有一处算术错**: ★**L167 的 `t_r=2.38µs@100pF` 与它自己写的 4.7k 对不上** ⇒ ★`SW/SW_TIMING_REVIEW.md` §6 已经把这句翻掉了: 「★**旧结论翻转** … ★**2.2k 的实算是 186ns, 注记 2380ns 差 12.8 倍**」★ ⇒ ★**L167/L168 那三个数 (4.7k / 3.3V / 2.38µs) 是同一处过期, 一次改掉** ★
· ★**根因不在网表, 在规格源头**: ★**`HW/SCHEMATIC_V1_SPEC.json` 的 B-01 / B-02 仍写 `level: "3.3V"` + `imp: "上拉 4.7k 到 3.3V (灌 702µA, t_r=2.38µs@100pF)"`** ★ ⇒ ★**`state/gen_netlist.py:770` 的 `conn_row()` 文档自己写着「★**value 默认取规格 imp (A 组阻抗必须与规格逐字一致 · check_netlist 判据 5)**」** ★ ⇒ ★**⇒ 真修法 = 改 SPEC.json 的 B-01/B-02 (level + imp), 不是手改网表** ★ (★手改 CSV 会被下次重跑生成器覆盖 ⇒ 那就是"改在产物上", 老毛病★)

★★**第 (2) 条: BAT_DET 整条分压链全 DNP, 但 SoC 的 ADC 输入脚是必装** ★
· ★**L181** = `P2,BAT_DET,RAIL_BAT,R_BAT_DET_1,NET_BAT_DET,1M+1M 分压 + 100nF,NET,必装,...` ★
· ★**L186** = `P2,BAT_DET,J_SOM_P1 pin38,NET_BAT_DET,NET_BAT_DET,1M+1M 分压 + 100nF,NET,必装,...` ★ ★**note: 「[BAT_DET] SoC ADC 输入节点 (跨板那一侧)」** ★
· ★**而 L182 / L183 / L184 / L185 (R_BAT_DET_1 / R_BAT_DET_2 / C_DET_BAT) 四行全部 `dnp=DNP`** ★ ⇒ ★**⇒ SoM 的 ADC 输入脚接在一个"一颗件都不装"的分压器上 = 悬空输入** ★
· ★**L182 的 note 是 `★DNP: 同上` —— "同上"指什么, 网表里没写** ⇒ ★**这本身也是一处"读者自己猜"的口径洞** ★

★★**第 (3) 条: U_EN_SW 没有器件本体行 ⇒ BOM 里这颗 IC 被登记成 NET 行** ★
· ★**网表里 `ref == U_EN_SW` 的行只有 4 行, `type` 全是 `NET`** (★L441 EN 输入 / L442 5V 输入 / L443 5V 输出 / L444 GND★) ★**表B (`HW/netlist_v1_pins.csv`) 里 `U_EN_SW.pin1..pin4` 四行 `type` 也全是 `NET`** ★
· ★**对比: 同为负载开关的 U_PWR_SW 有本体行** (★L50, `type=IC`, value `[待选型] 负载开关 (≥2A, R_on ≤40mΩ@3.7V, IQ ≤5µA, 带反向阻断)`★) ⇒ ★**同一块板上两颗同类器件, 一颗有本体行一颗没有** ★
· ★**后果已经在 BOM 上显形**: ★**`HW/BOM_v1.csv` 第 208 行 = `U_EN_SW,1,EN 输入 (高=放行底板),NET,必装,...`** ★ ⇒ ★**一颗 4 脚 IC 的 value 栏里躺着一句脚功能串, type 栏是 NET** ★ ⇒ ★**根因 (main 实读 `state/gen_bom.py:143` 的 `_pick_value` 注释自己写着)**: ★「★**器件本体行 (type 不是 'NET') 的 value = 器件身份描述**; ★**网节点行 (type='NET') 的 value = 脚级功能串**」★ ⇒ ★**⇒ 没有本体行 ⇒ BOM 取到的必然是脚级功能串** ★ ⇒ ★**`state/gen_netlist.py:1471-1483` 用 `add(...)` 逐脚建 NET 行, 缺一条 `type=IC` 的器件本体行** ★

★★**第 (4) 条: USB D− 全程没有 ESD, 而那颗器件自称"双通道"** ★
· ★**L417 / L418**: ★`D_ESD_USB_D` 只有两脚 = `USB_D_P_SRC` + `GND` ★ ⇒ ★**板文件封装也只有 2 焊盘** (★`HW/BOM_v1.csv` 第 62 行: 「★板文件封装: 2 焊盘 …」★) ★
· ★**而它的 value 写的是「ESD 阵列 [待选型] (USB 2.0 **双通道**)」** ⇒ ★**名不副实: 只有 D+ 一路进了 ESD, GND 是回流不是第二路数据** ★
· ★**D− 那条路 (`NET_USB_D_N_TYPEC` → `R_SER_USB_D_N` → `J_USB_C A7+B7`, L432 / L435) 全程无 ESD** ★ ⇒ ★**Type-C 入口只护了差分的一边** ★
· ★**讽刺的是 L417 自己的 note 就引了规矩**: ★「★**Forlinx 载板指引要求 ESD 紧贴接口**」★ ⇒ ★**⇒ 引用了规矩, 自己没照做 (护了一半)** ★

★★**② 你要交的东西 (★三件 + 一份登记★)** ★★
· ★**① 落表规格页** ⇒ ★**新建 `HW/NETLIST_SELF_CONSISTENCY_SPEC.md`** ★ ⇒ ★**4 条 × 6 栏**: ★**① 现象 (网表原文逐字 + 行号) ② 为什么它是缺陷 (可判定依据, 引得到别处) ③ 修法 (精确到【改哪个文件的哪个字段】★例: 第 (1) 条 = 改 `HW/SCHEMATIC_V1_SPEC.json` 的 B-01/B-02 的 `level` + `imp` ★**不许写"改一下网表"这种话**) ④ 影响面 (BOM 备料 / 装配 / 板 / 评审 / 投板, 逐项写有没有) ⑤ 落表时机 (★归整链重出第 1 步那一趟, 不许单独改 md5★) ⑥ 证据等级** ★
· ★**② 机器门禁** ⇒ ★**新建 `HW/check_netlist_selfconsistency.py`** ★ ⇒ ★**它不是"检查网表对不对", 是"检查【规格页】跟【现行网表】还对不对得上"** ★ ⇒ ★**判据 (★每条都要能被反向用例抓到★)**: ★**a) 4 条缺陷的现状 (行号 + 关键字段) 与规格页逐字对得上 —— 对不上 = 网表被静默改过 = 红** ★**b) `HW/BOM_v1.csv` 里 `U_EN_SW` 行的 `type` 仍是 `NET` (现状断言, 让它别被悄悄"修好"而规格页不跟) ★**c) 4 条各自的"不该改错"锚点仍在 (★例: L169 的 note 里那句"已作废"还在 ★ / L182 的 `dnp=DNP` 还在 ★)** ★ · ★**带 `--selftest` (★反向用例: 把任一锚点改坏 ⇒ 自测必须变红★)** ★ · ★**rc=0 的口径要写清楚: 现在 4 条缺陷仍在 ⇒ 门禁是"现状守卫"不是"合格证"; 等它们随整链重出落表后, 门禁要能翻成"缺陷已消失" ⇒ 你把翻面条件写进规格页 §⑤** ★
· ★**③ 交卷件** ⇒ ★**新建 `HANDOFF/2026-11-15_hw-lead_ISS211_网表自身一致性4处.md`** (★≤25 行, B1~B6 结构齐全★) ★
· ★**④ 分片登记** ⇒ ★**走 `state/frag_write.py` 原子写 `state/fragments/hw.yaml`** (★只写自己那一份, 不许手改 yaml★)

★★**③ 边界 (★不许越线★)** ★★
· ★**不许改**: ★`HW/netlist_v1.csv` · ★`HW/netlist_v1_pins.csv` · ★`HW/PCB/demo_mainboard.kicad_pcb` · ★`HW/PCB/demo_mainboard.kicad_pro` · ★`HW/SCHEMATIC_V1_SPEC.json` · ★`state/gen_netlist.py` · ★`state/gen_netlist_pins.py` · ★`state/gen_bom.py` · ★`state/check_netlist.py` · ★`state/check_netlist_pins.py` · ★`state/issue_log.yaml` 的任何状态 · ★`PROJECT_TRACKER.md` §0 · ★`state/outbox/` · ★别人的分片 ★
· ★**受保护 md5 交卷前后必须逐字节不变**: ★**板 `611b869e13518c3c023fb178f91a0075` · 网表 `c78f991283cc82d56c8e3dd31657c785` · 脚表 `4814617e22b567d76164e56bc5e39dc8` · `.kicad_pro` `3e504d2be83152e337949723e909be1b`** ★
· ★**(3)(4) 两条的修法可能牵到板侧 (封装 / 器件行数 / 座体) ⇒ 只出规格 + 标注"需不需要改板 / 归哪一趟落表", 不许自己动板** ★
· ★**不许替老板拍**: ★**(4) 条的 ESD 选型 / (3) 条的 U_EN_SW 具体型号 (ISS-172 还是 open, 老板级) ⇒ 你只出"缺什么 / 需要什么判据", 不定型号** ★
· ★**零外发**: ★**不许发任何邮件 / 询价 / 问询 / 采购** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★) ⇒ ★**缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ⇒ 没有"批一句可以发"这个选项** ★
· ★**交卷前跑 `python3 state/merge.py` (rc 必须 0) && `python3 state/gate_check.py` (★Q1 必须 18/18★) 并把输出贴进回复** ★
"""

# ==================================================================
# ② ISS-212 → sw-lead
# ==================================================================
BRIEF_212 = """★**目标 (★内部活·不是 PCB 布线/布局类·不是老板级拍板★)**: 把 ★**demo 显示侧的口径从"视涯 0.49\\" 1920×1080"重锚到"demo 屏真实那块 Waveshare 2.8\\""**★ ⇒ 出 ★**一份 demo 屏侧真源规格 + 一份逐处定性表 + 一个机器门禁**★ ⇒ ★**本单不许改网表 / 不许改板 / 不许改 HW/**★ ⇒ ★**零外发** ★

★★**为什么是现在 (★main 2026-11-15 23:2x~23:4x 实测, 不是推测★)** ★★
· ★**老板 2026-11-04 01:19 已拍板 demo 屏换 Waveshare 2.8inch DSI LCD (SKU 22028)**, ★**而 SW 侧至今零提及**: ★**`grep -rn "Waveshare|2.8inch|22028" SW/` = 0 命中** ★ ⇒ ★**SW 唯一那份 demo 管线规格 `SW/DEMO_OD_PIPELINE_SPEC.md` (ISS-145, 11-02 19:xx 写的) 全篇还在按视涯 0.49\\" 写** ★
· ★**实测命中数**: ★**`SW/DEMO_OD_PIPELINE_SPEC.md` 里 `1920×1080|1920x1080|视涯|SeeYA` 命中 22 处** ★ ⇒ ★**含 §5 的 letterbox 算式 (AR0234CS 1920×1200 → 面板 1920×1080, k=0.9, 内容 1728×1080, 左右各 96px 黑边) + §5 面板行「面板 init code / 时序 ★**未拿到**」+ §4.3 的两阶段验证法 + §7.5「真正卡住'屏上有画'的是面板 init code ⇒ **问询函外发比选 sensor 路径更紧急**」** ★
· ★**★而对 demo 屏来说, §4.3 的"两阶段"整个是假阻塞★**: ★**`HW/PCB/WAVESHARE_2P8_INIT_AND_BACKLIGHT.md` (460 行) 已把官方口径查完**: ★**这块屏不需要任何 DCS init 序列** —— 树莓派官方内核 `drivers/gpu/drm/panel/panel-waveshare-dsi.c` 对 `waveshare,2.8inch-panel` ★**一条 DSI 指令都不发**, 全部控制走 **I2C (模组内 MCU)**: probe 写 `0xC0/0xC2/0xAC` · enable 写 `0xAD=0x01` · disable 写 `0xAD=0x00` · 背光写 `0xAB`+`0xAA` ★ ⇒ ★**⇒ demo 阶段 1 就能上真面板, "等 init code" 这道闸对 demo 屏根本不成立** ★
· ★**★而 SW 之前登记的 need `demo_od_p0_4_panel_init_code` 写的是「请项目总工/老板放行外发问询函」★** ⇒ ★**按老板 2026-11-12 02:02 新口径 (不再发信, 全靠自己查资料), 这条不许再当"外发前置"挂着** ★ ⇒ ★**demo 屏这一半已经自己查完 (官方 RPi 内核 + Rockchip 内核 + Waveshare 官方 wiki, 见上) ⇒ 整机视涯那一半才是 [0数据] ⇒ 本单要给它一个降级结论, 不许留成外部依赖** ★

★★**★① 已经查到的 (★main 实测, 你不用重查, 但要在你的规格里复核一遍并标证据等级★)** ★★
· ★**屏本体**: ★**480×640 / MIPI DSI 2-lane / 15pin 1.0mm FPC / 3V3 (pin14+pin15) / 模组内供背光 (无独立背光脚、无 RESET 脚)** ★`[官网]` (Waveshare 官方商品页 + 官方逐针表, 出处见该文档 §7)
· ★**init**: ★**不需要 DCS** —— 面板与背光由模组内 MCU 控 (RPi 官方驱动实测行为, commit `d8e5eb49991de6b8fa9231532a11036e24aa84de`, 分支 `rpi-6.12.y` / `rpi-6.18.y` 逐行 diff 一致) ★`[官网]`
· ★**屏侧 I2C**: ★**地址 0x45** (面板控制) · 触摸 **GT911 在 0x14 可选** ★`[官网]`
· ★**SoC 侧 (RK3572)**: ★**2-lane 跑得动** (`max_data_lanes = 4`, 1/2/4 都行) · ★**★没有 DSC 编码器** ★ (★DSI TX 内核全文无 `dsc`; VOP2 只有 RK3588 有 `.nr_dscs = 2`; Rockchip 自己的 DSI2 驱动里 `.dsc = true` 也**只有 RK3588**)★`[官网]` ⇒ ★**⇒ 整机视涯 0.49\\" (VESA DSC 3:1) 在 RK3572 上不能用** ★
· ★**现成可抄的官方件**: ★**Rockchip 内核有同分辨率 (480×640) 同 lane 数 (2-lane) 的现成 GIP 序列** (`drivers/gpu/drm/panel/panel-sitronix-st7701.c` 的 `densitron,dmt028vghmcmi-1a`) ★`[官网]` · ★**官方 dts 片段已备好** (★`HW/PCB/WAVESHARE_2P8_INIT_AND_BACKLIGHT.md` §1.5: `hdisplay=480 / hsync_start=630 / hsync_end=680 / htotal=830 / vdisplay=640 / vsync_start=790 / vsync_end=840 / vtotal=990 / clock=50000kHz`★)
· ★**★板侧约束 (★main 实跑网表读出来的, 这几条决定软件该怎么配★)** ★★
  · ★**板侧座是 22p@0.5mm** (`HIROSE FH12-22S-0.5SH(55)`, 右角/底接触/1 固定柱, 针序照 **Raspberry Pi 5 官方 DISPLAY 座 (J4)**, 网表 `HW/netlist_v1.csv` L237) ⇒ ★**板侧引出的是 4 lane + CK (DSI_D0_CK + D0/D1/D2/D3 各一对, 中间串 0Ω `R_SEL_*` 直通位) + I2C_B (pin11/pin12) + GND/3V3** ★
  · ★**★但屏侧物理只有 2 对差分** ⇒ ★**⇒ 软件侧 DSI 必须按 2-lane 配, 板上的 lane2/lane3 是给将来整机屏留的** ★ (`HW/PCB/WAVESHARE_2P8_INIT_AND_BACKLIGHT.md` §1.6 / §4.1 / §5)
  · ★**屏接板靠官方转接线**: ★**Waveshare 官方 DSI 排线页有 15pin→22pin / dual-plug 22pin** ⇒ ★**板不改, 屏侧用官方线** ★`[官网]` (出处 `HW/DISPLAY_SMALL_SCREEN_OPTIONS.md` [S3])
  · ★**★I2C_B 的速率上限已经算死了, 而且它就是面板控制总线**: ★**`SW/SW_TIMING_REVIEW.md` §6 已翻转** ⇒ ★**I2C_A (2.2k/1.8V) 通过; ★**I2C_B (4.7k/3.3V, 走 CONN_LIGHT 22p FPC ⇒ 有线容) 300pF 时 t_r = 1194.7ns > 1000ns ⇒ I2C_B 必须 ≤100kHz** ★ ⇒ ★**⇒ 面板 bring-up 的 I2C 速率上限就被这条卡着, 必须写进 demo 屏规格** ★

★★**② 你要交的东西 (★三件 + 一份登记★)** ★★
· ★**① demo 屏侧真源规格** ⇒ ★**新建 `SW/DEMO_PANEL_WAVESHARE_2P8_SPEC.md`** ★ ⇒ ★**必含**: ★**分辨率 / 帧率口径 (板侧 4 lane vs 屏侧 2 lane ⇒ 软件配几 lane) / "无 DCS" 这条结论 (附官方驱动出处) / I2C 面板控制序列 (probe 0xC0/0xC2/0xAC · enable 0xAD=0x01 · disable 0xAD=0x00 · 背光 0xAB+0xAA) / 屏 I2C 0x45 + 触摸 GT911 0x14 / I2C_B ≤100kHz 这条硬上限及其来源 / dts 片段怎么用 / Rockchip ST7701 GIP 可参照件 / 板端到货后 30 分钟验证清单 (每步: 命令 + 期望看到什么 + 判据)** ★ ⇒ ★**每条标 [官网]/[实测]/[媒体]/[推算]/[0数据]** ★
· ★**② 逐处定性表** ⇒ ★**新建 `SW/DEMO_PANEL_SPEC_TRIAGE.md`** ★ ⇒ ★**对 `SW/DEMO_OD_PIPELINE_SPEC.md` 那 22 处 1920×1080/视涯/SeeYA 命中逐处定性**: ★**① demo 活动口径 (必须改成 Waveshare 480×640) ② 整机路线占位 (视涯 0.49\\" 仍是整机屏, **保留但必须标明"整机路线·暂缓"**, **不许一把删掉**) ③ 历史沿革 (原样保留 + 一句话注记)** ★ ⇒ ★**这张表的写法照 `MECH/DISPLAY_LEGACY_V2_CLOSEOUT.md` 的成例 (33 处逐处定性表) — 那是 mech-lead 已交卷已验收的样板** ★ ⇒ ★**然后只改"demo 活动口径"那几处, 其余一字不许动** ★
· ★**③ 机器门禁** ⇒ ★**新建 `SW/tools/check_demo_panel_spec.py`** ★ ⇒ ★**判据**: ★**a) demo 屏规格里 480×640 / 2-lane / 无 DCS / I2C_B ≤100kHz 四条在位 ★**b) demo 屏规格里**不许**把"视涯 / 1920×1080 / init code 未拿到"当成 **demo 活动口径** (出现在整机路线/历史段落里是允许的) ★**c) `SW/DEMO_OD_PIPELINE_SPEC.md` 里被定性表判成 demo 活动口径的那几处, 确实已经改掉 ★**d) 带 `--selftest` (反向用例: 把某处 demo 口径塞回去 ⇒ 自测必须变红)** ★
· ★**④ 顺带把 need `demo_od_p0_4_panel_init_code` 结掉**: ★**demo 半 = 自己查完的结论 (上面的官方证据) + 证据等级**; ★**整机视涯半 = [0数据] + 降级方案 (★不许再写"等原厂回信" / 不许再提"放行外发"★)** ⇒ ★**并把它登记进你的分片 (★`state/frag_write.py` 原子写 `state/fragments/sw.yaml`★)** ★
· ★**⑤ 交卷件** ⇒ ★**新建 `HANDOFF/2026-11-15_sw-lead_ISS212_demo显示侧重锚Waveshare.md`** (★≤25 行, B1~B6 结构齐全★) ★

★★**③ 边界 (★不许越线★)** ★★
· ★**不许改**: ★`HW/` 下任何文件 (★`HW/PCB/WAVESHARE_2P8_INIT_AND_BACKLIGHT.md` / `HW/DISPLAY_SMALL_SCREEN_OPTIONS.md` 你只引用, 一个字不许改★) · ★`HW/netlist_v1.csv` / ★`HW/netlist_v1_pins.csv` / ★`HW/PCB/demo_mainboard.kicad_pcb` / ★`HW/PCB/demo_mainboard.kicad_pro` · ★`state/gen_*.py` · ★`state/issue_log.yaml` 的任何状态 · ★`PROJECT_TRACKER.md` §0 · ★`state/outbox/` · ★别人的分片 ★
· ★**SW 侧只许动这 4 个文件**: ★**`SW/DEMO_OD_PIPELINE_SPEC.md` (只改定性表判成 demo 活动口径的那几处) + `SW/DEMO_PANEL_WAVESHARE_2P8_SPEC.md` (新建) + `SW/DEMO_PANEL_SPEC_TRIAGE.md` (新建) + `SW/tools/check_demo_panel_spec.py` (新建)** ★ ⇒ ★**不许动 `SW/DEMO_OD_TIMING_SPEC.md` / `SW/SW_TIMING_REVIEW.md` / `SW/RKNN_BENCH.md` / `SW/DEMO_BOARD_60MS_VERDICT_PLAN.md` (★那几份是 ISS-205 / ISS-207 / ISS-210 已验证件, 碰了就是回退★)** ★
· ★**受保护 md5 交卷前后必须逐字节不变**: ★**板 `611b869e13518c3c023fb178f91a0075` · 网表 `c78f991283cc82d56c8e3dd31657c785` · 脚表 `4814617e22b567d76164e56bc5e39dc8` · `.kicad_pro` `3e504d2be83152e337949723e909be1b`** ★
· ★**不许替老板拍**: ★**整机屏路线 (视涯 vs Waveshare 各走哪条) / 屏的最终选型 / FOV** —— 你只做 **demo 屏**这一半, 整机那半只给降级结论 + 标 [0数据] ★
· ★**零外发**: ★**不许发任何邮件 / 询价 / 问询 / 采购** (★老板 2026-11-11 19:31 + 2026-11-12 02:02★) ⇒ ★**缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ⇒ 没有"批一句可以发"这个选项** ★
· ★**交卷前跑 `python3 state/merge.py` (rc 必须 0) && `python3 state/gate_check.py` (★Q1 必须 18/18★) 并把输出贴进回复** ★
"""

# ==================================================================
# ③ ISS-213 → mech-lead
# ==================================================================
BRIEF_213 = """★**目标 (★内部活·不是 PCB 布线/布局类·不是老板级拍板★)**: 把 ★**结构侧那份 54 项交叉复核表逐条定性 + demo 板上"现在做出来就会出问题"的那几条真缺陷收掉**★ ⇒ 出 ★**一份逐条定性表 + 一个能自动复核的机器门禁**★ ⇒ ★**本单不许改网表 / 不许改板 / 不许碰 PCB 布线布局**★ ⇒ ★**零外发** ★

★★**为什么是现在 (★main 2026-11-15 23:2x~23:4x 实测, 不是推测★)** ★★
· ★**`MECH/hw_cross_review_check.py` 现在报: PASS 14 / FAIL 17 / 条件通过 8 / 说明 15 (共 54 项), 而它的 rc = 0** ★ ⇒ ★**它自己写的那句「★**FAIL 项不是'做不出来', 是'按现在的图纸/口径做出来会出问题'**」** ★ ⇒ ★**★17 条"做出来会出问题"挂着, 却一个红灯都不点** ★
· ★**★而且它根本不在巡检链上★**: ★**main 实测 `state/daily_check.py` 里 grep 不到 `hw_cross_review` / `service_port` / `hinge_usb` / `display_biosafety` / `cavity_recalc` 任何一个** ★ ⇒ ★**⇒ 这 17 条在每日巡检里完全隐形** ★ ⇒ ★**★这已经是本项目同类问题的第三次复发**: ★**① 原理图 ERC 从未跑过 (46 条 label_dangling 全盲) ② 图=表 尺子 (584 脚) 建之前一直是假绿 ③ 现在结构侧 17 条 FAIL 也不在链上** ★ ⇒ ★**⇒ 本单的真正价值不在"修 17 条", 在【让这 17 条从隐形变成有账】** ★
· ★**17 条 FAIL 名单 (★main 自己实跑读出来的, 以你实跑为准★)**: ★**PIN-MISMATCH P9 正文声明 vs 网表实际 pin 数 / STK-FANOUT 4 条 FPC 的 V 带合计 vs 主 PCB 板宽 (Y) / PCB-X-GAP 铰链端 X 向缺口 / MRG-54P 全合并成 1 个连接器 (63p@0.5mm · 网表实读) / MRG-X-4 铰链端 X 占位 (4 座分开) / MRG-X-3 铰链端 X 占位 (3 座 J_CHG+USB 合并) / MRG-X-3 铰链端 X 占位 (3 座 · 深度上界 7.5) / TOPO-3 P9 页的堆叠账缺 2 项 (自己发现) / FRM-SUM 框侧 4 条 FPC 的 V 向带宽合计 / CHG-OPEN Type-C 面板开孔单边间隙 / CHG-PRINT-TOL CHARGE_BOARD_SPEC 的印刷公差要求 vs FDM 能力 / THM-RATIO-3.70 buck 功率守恒 ICHG/IIN @Vbat=3.70V / THM-RATIO-4.20 同上 @Vbat=4.20V / THM-SURF-buck 端件外表面温升 (buck 正确口径 Pin-Pout+DCR) / THM-SURF-MECH 端件外表面温升 (MECH_BUDGET 线性口径) / THM-PATH 端件散热路径 (自己发现) / NET-LED 充电灯电路 (D_CHG_LED/Q_CHG_LED/R_CHG_LED) 的 board 列** ★
· ★**其中 NET-LED 那条 main 已读到结论**: ★**网表 board = `['CHG_BOARD']`, 但同页注记写"装在充电板 (镜框) 靠近 Type-C 座" ⇒ `R_CHG_LED` 两端分别标 `CHG_BOARD` (net `VBUS_5V_CHG`) 与 `MAIN_PCB`, 而 `VBUS_5V_CHG` 只存在于充电板 ⇒ LED 链条物理上只能在镜框 ⇒ board 列标错 ⇒ BOM 备料 / 装配 / ISS-103 导光孔位置会跟着做错** ★ (★但这条的网表 board 列是 HW 地界 ⇒ **你不许自己改, 只登记 need 给 main**★)

★★**★★必须按【原理图主线】分流 (★老板 2026-11-11 10:07 口径: PCB 布线/布局类一律【不派】·排队等原理图定稿★)★★** ★★
· ★**属于 PCB 布线 / 布局 / 板框改动的一律【不许修】**: ★**MRG-X-3 / MRG-X-4 / MRG-54P / STK-FANOUT / FRM-SUM / PCB-X-GAP** 这六条 (★铰链端 X 向占位 / 座体合并 / FPC 带宽 vs 板宽 / 板框缺口★) ⇒ ★**你只做定性 + 写清"排队等原理图定稿, 恢复条件是什么", 不许动** ★ ⇒ ★**★这六条不许改, 也不许为了"让它变绿"去调判据阈值** ★
· ★**demo 板当前成立、且在 MECH 地界内 (印刷公差 / 开孔间隙 / 腔体 / 热路径 / 端件温升口径 / 功率守恒算式) ⇒ 你可以修** ★
· ★**跨域的 (★例: NET-LED 的网表 board 列 = HW 地界★) ⇒ 只登记 need 给 main, 由 main 派给对应总工** ★ ⇒ ★**不许你直接指派别人, 也不许你自己去改 HW/** ★ ⇒ ★**(★防撞车: 已经有在飞单, 你别往同一个 agent 名额上塞活★) ★
· ★**你手里还有一条 ISS-206 留下的自家账要一起收**: ★**分片 `state/fragments/mech.yaml` 的 claim `mech_hinge_stack_fixed_mm` 仍写 24.00, 而文档 (ISS-206 裁 2 定的 16p/20p/4p/10p) 已是 25.00** ★ ⇒ ★**走 `state/frag_write.py` 把它改成 25.00, 不许手改 yaml, 不许动别的 key** ★

★★**★① 结构真源的现行口径 (★main 实测, 只引用不许改★)** ★★
· ★**`MECH/BOARD_GEOM_30MM.md` §1 现行板框**: ★**板长 X = 60.00mm (X=0 = 铰链端) · 板宽 Y = 30.00mm · 板厚 = 1.00mm (6 层) · 板重 3.33g · 角工艺边 0.50 / 器件边距带 0.80mm** ★ ⇒ ★**该文件 §0/§1 明写「★凡与上述口径不同 (如 12mm / 15mm / 板长 76 / 板长 50 / RK3588 8×10 封装) 的数, **都是死值**」** ★ ⇒ ★**PIN-SET-2 用套 A (Y 按中心线平移, S 孔 ±5.00 不变) · 打印包口径 = Rev B** ★
· ★**`MECH/service_port_check.py` 的现行基准**: ★**`pcb_thk` = 1.00 (★注释: 6 层现行; 4 层 0.80 已作废★) · 硬要求 `cavity_req` = 4.50 (ISS-085 §6.1 盖板内腔 ≥4.5)** ★
· ★**★顺带给你一条 main 实测出来的结论 (交 main 裁, 你不许自己改 issue_log)★**: ★**`state/issue_log.yaml` 的 ISS-126 (open / owner=main / due 2026-11-05) 至今还按"板厚 0.41 / 0.80 / 1.00 / 1.22 四档都有可能, 只有 0.80 及以下才安全, 1.22 档净空 4.48 破 4.50"在写, 并把解锁条件挂在"等 PCB 厂 DFM 报告 (ISS-122)"上** ★ ⇒ ★**但结构真源现在的板厚是 1.00mm (6 层), 而 `MECH/service_port_check.py` 的现行基准 `pcb_thk` 也是 1.00 ⇒ 净空 4.70 ≥ 4.50** ★ ⇒ ★**⇒ ISS-126 的前提已被现口径超越 (且"6 层 = 0.41mm"那个假设本身与现口径对不上)** ★ ⇒ ★**你在定性表里给出 ISS-126 的**真实状态**结论 (含现行口径下的净空数 + 判据出处), 交 main 裁 ⇒ 你不许改 issue_log** ★

★★**② 你要交的东西 (★三件 + 一份登记★)** ★★
· ★**① 逐条定性表** ⇒ ★**新建 `MECH/HW_CROSS_REVIEW_TRIAGE.md`** ★ ⇒ ★**54 项全覆盖, 每项一行**: ★**项号 / 现状判定 (PASS·FAIL·条件通过·说明) / 与 demo 板的相关性 (demo 板当前成立 · 整机阶段 · 打印包阶段) / 是否在 MECH 地界内 (是 / 否·归谁) / 处置 (★修掉·出规格·登记 need 给 main·**排队等原理图定稿**★) / 排队的恢复条件 / 证据等级** ★ ⇒ ★**★"处置"这一栏就是本单的核心交付: 17 条 FAIL 每一条都要有一个明确去处, 不许留空不许写"待定"** ★ ⇒ ★**成例照 `MECH/DISPLAY_LEGACY_V2_CLOSEOUT.md` 的 33 处逐处定性表** ★
· ★**② 机器门禁** ⇒ ★**新建 `MECH/check_demo_struct_truth.py`** ★ ⇒ ★**它守的是"demo 板当前成立的条目", 不是"54 项全绿"** ★ ⇒ ★**判据**: ★**a) demo 板当前成立的那些项 (你在 ① 里判定的) 全部通过 —— 有红的就红 ★**b) 属 PCB/布局类的那六条, 断言它们"已被登记排队"而不是被静默 (★不许为了让它变绿去动它★) ★**c) `MECH/BOARD_GEOM_30MM.md` §1 的 60.00 / 30.00 / 1.00 / 3.33g 四个数一个没被改 ★**d) 判据阈值一个没被松 (★`cavity_req` 4.50 / `judge/CRIT` 0.60 / `cav_v` 38.00 / `duct_v` 6.00 这几个不许动★) ★ · ★**e) 带 `--selftest` (反向用例: 把任一锚点改坏 ⇒ 自测必须变红)** ★ · ★**f) 这个新闸的挂巡检与否交 main 裁 ⇒ 你不许自己改 `state/daily_check.py`** ★
· ★**③ 交卷件** ⇒ ★**新建 `HANDOFF/2026-11-15_mech-lead_ISS213_结构54项定性表与demo真缺陷收口.md`** (★≤25 行, B1~B6 结构齐全★) ★
· ★**④ 分片登记** ⇒ ★**走 `state/frag_write.py` 原子写 `state/fragments/mech.yaml`**: ★**新增 artifact / claim / need (给 main 的那几条) + 顺手把 `mech_hinge_stack_fixed_mm` 改成 25.00** ★ (★只写自己那一份, 不许手改 yaml, 不许动别的 key★) ★

★★**③ 边界 (★不许越线★)** ★★
· ★**不许改**: ★`HW/` 下任何文件 · ★`HW/netlist_v1.csv` / ★`HW/netlist_v1_pins.csv` · ★`HW/PCB/demo_mainboard.kicad_pcb` / ★`HW/PCB/demo_mainboard.kicad_pro` · ★`state/gen_*.py` · ★`state/daily_check.py` · ★`state/issue_log.yaml` 的任何状态 (★包括 ISS-126★) · ★`PROJECT_TRACKER.md` §0 · ★`state/outbox/` · ★别人的分片 ★
· ★**不许改 `MECH/BOARD_GEOM_30MM.md` §1 的板框真源数** (★60.00 / 30.00 / 1.00 / 3.33g 一个字不许动★) · ★**不许改判据阈值** (★`cavity_req` 4.50 / `CRIT` 0.60 / `cav_v` 38.00 / `duct_v` 6.00★) · ★**不许改 `MECH/service_port_check.py` / `MECH/hinge_usb_check.py` / `MECH/hw_cross_review_check.py` 的判据语义** (★只许改文档与产出, 改判据就等于"把红灯调没"★)
· ★**不许碰 PCB 布线 / 布局 / 板框** (★那六条只定性 + 排队★)
· ★**受保护 md5 交卷前后必须逐字节不变**: ★**板 `611b869e13518c3c023fb178f91a0075` · 网表 `c78f991283cc82d56c8e3dd31657c785` · 脚表 `4814617e22b567d76164e56bc5e39dc8` · `.kicad_pro` `3e504d2be83152e337949723e909be1b`** ★
· ★**不许替老板拍**: ★**整机屏路线 / 波导归属 / FOV / 板长方案取舍 (裁 6) / 充电板是否留** —— 你只把数摆出来 + 给判据 + 给建议, 拍板留给老板 ★
· ★**零外发**: ★**不许发任何邮件 / 询价 / 问询 / 采购** (★老板 2026-11-11 19:31 + 2026-11-12 02:02★) ⇒ ★**缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ⇒ 没有"批一句可以发"这个选项** ★
· ★**交卷前跑 `python3 state/merge.py` (rc 必须 0) && `python3 state/gate_check.py` (★Q1 必须 18/18★) 并把输出贴进回复** ★
"""

NEW = {
    "ISS-211": {
        "id": "ISS-211",
        "title": "★★[主线内·原理图/网表侧·内部活] 现行网表自身 4 处自相矛盾 (I2C_A 上拉行 vs 器件行 / BAT_DET 分压链全 DNP 但 SoC ADC 脚必装 / U_EN_SW 无器件本体行 ⇒ BOM 登记成 NET / USB D− 无 ESD 而器件自称双通道) ⇒ 出落表规格 + 机器门禁 (不改网表·不改板)",
        "severity": "high",
        "source_blocker": "ISS-190",
        "desc": "★**ISS-190 (sw-lead 时序复评) 交卷时登记的 7 条 needs_from 里, 4 条指向 hw-lead 且至今未答** ⇒ ★**main 2026-11-15 23:2x~23:4x 逐条实跑网表复核, 4 条全部成立** ⇒ ① `HW/netlist_v1.csv` L167/L168 仍逐字复述 L169 自己判为『已作废』的 4.7k/3.3V (实为 2.2k/1.8V 域, 根因在 `HW/SCHEMATIC_V1_SPEC.json` 的 B-01/B-02) ② L181/L186 (BAT_DET 网 + SoM ADC 脚 J_SOM_P1 pin38) 必装而 L182~L185 (R_BAT_DET_1/2 + C_DET_BAT) 全 DNP ⇒ ADC 输入悬空 ③ `ref==U_EN_SW` 在表A/表B 都是 type=NET、无 type=IC 器件本体行 (对比 U_PWR_SW L50 有) ⇒ `HW/BOM_v1.csv` 第 208 行把这颗 4 脚 IC 登记成 `value=EN 输入 (高=放行底板), type=NET` ④ `D_ESD_USB_D` 只有 USB_D_P_SRC + GND 两脚 (板封装 2 焊盘) 而 value 自称『USB 2.0 双通道』, D− (NET_USB_D_N_TYPEC → R_SER_USB_D_N → J_USB_C A7+B7) 全程无 ESD ⇒ **这四条不是软问题, 是同一张网表里两行字互相否定, 投板前必须收口** ⇒ ★**但现在不许改网表**: 整链重出第 1 步 (`state/RECHAIN_STEP1_LANDING_SPEC.md`) 要把 C/E/D 三项一次合并落表 ⇒ 板只改一次 ⇒ 先落表 = 留证链/Gerber/投产包/盖印 白跑两遍 ⇒ **本单 = 出规格 + 出门禁, 让这 4 条跟着那一趟一起落** (★同 ISS-191 / ISS-174 已验证的路子★)",
        "owner": "hw-lead",
        "reporter": "main",
        "raised": "2026-11-15",
        "due": "2026-11-18",
        "status": "open",
        "external": False,
        "need_keys": ["iss190_netlist_i2ca_note_contradiction",
                       "iss190_netlist_bat_det_all_dnp",
                       "iss190_netlist_u_en_sw_no_device_row",
                       "iss190_netlist_usb_dminus_no_esd"],
        "fix_ref": None,
        "verify_by": "main",
        "verify_result": None,
        "verify_date": None,
        "note": "2026-11-15 23:5x main 新开 (★A 段 internal=0 ⇒ 20 条 open 全在 boss(5)/main(15) 名下、三个总工名下 open=0 ⇒ 兄弟 job 上一轮明确交接『下一轮开单来源 = 各总工交卷里的 needs_from + 独立的队列自动派活 job; 本 job 不自己开单』⇒ 开单是本 job 的活★) ⇒ ★**依据 = sw-lead ISS-190 交卷里 4 条至今未答的 needs_from + main 本轮逐行实测复核** ⇒ ★**本单不改网表/板/脚表/生成器, 受保护 md5 一个字节不许变** ★",
        "dispatched_at": None,
        "task_brief": BRIEF_211,
    },
    "ISS-212": {
        "id": "ISS-212",
        "title": "★★★[demo 头号路径·自己查版·软件/显示侧] demo 显示侧口径重锚到 Waveshare 2.8\" (480×640 · 2-lane · 无需 DCS init · I2C_B ≤100kHz) + 逐处定性表 + 机器门禁 (SW 侧对 demo 屏至今零提及)",
        "severity": "high",
        "source_blocker": "ISS-145",
        "desc": "★**老板 2026-11-04 01:19 已拍板 demo 屏换 Waveshare 2.8inch DSI LCD (SKU 22028)**, 而 ★**SW 侧至今零提及** (main 实测 `grep -rn \"Waveshare|2.8inch|22028\" SW/` = 0 命中) ⇒ ★**SW 唯一那份 demo 管线规格 `SW/DEMO_OD_PIPELINE_SPEC.md` (ISS-145, 11-02 写的) 全篇还按视涯 0.49\" 写: `1920×1080|视涯|SeeYA` 命中 22 处** (含 §5 letterbox 算式 k=0.9/1728×1080/96px 黑边 + §5「面板 init code / 时序 未拿到」+ §4.3 两阶段验证法 + §7.5「问询函外发比选 sensor 路径更紧急」) ⇒ ★**★而对 demo 屏来说 §4.3 的两阶段整个是假阻塞**: `HW/PCB/WAVESHARE_2P8_INIT_AND_BACKLIGHT.md` (460 行) 已查完官方口径 = ★**这块屏不需要任何 DCS init 序列** (树莓派官方内核 panel-waveshare-dsi.c 一条 DSI 指令都不发, 面板与背光全走 I2C 模组内 MCU: probe 0xC0/0xC2/0xAC · enable 0xAD=0x01 · 背光 0xAB+0xAA) ⇒ ★**demo 阶段 1 就能上真面板** ★ ⇒ ★**板侧是 22p@0.5mm RPi5-J4 座引出 4 lane + CK, 但屏侧物理只有 2 对差分 ⇒ 软件侧 DSI 必须按 2-lane 配; 屏接板用 Waveshare 官方 15pin→22pin 线, 板不改** ⇒ ★**且 `SW/SW_TIMING_REVIEW.md` §6 已判死 I2C_B (4.7k/3.3V, 300pF 时 t_r=1194.7ns>1000ns) ⇒ I2C_B 必须 ≤100kHz —— 而 I2C_B 正是面板控制总线** ⇒ ★**顺带把 sw-lead 之前登记的 need `demo_od_p0_4_panel_init_code` (写着『请项目总工/老板放行外发问询函』) 结掉: demo 半 = 自己查完的结论, 整机视涯半 = [0数据] + 降级方案, 不许再留成外部依赖** ★",
        "owner": "sw-lead",
        "reporter": "main",
        "raised": "2026-11-15",
        "due": "2026-11-18",
        "status": "open",
        "external": False,
        "need_keys": ["demo_od_p0_4_panel_init_code"],
        "fix_ref": None,
        "verify_by": "main",
        "verify_result": None,
        "verify_date": None,
        "note": "2026-11-15 23:5x main 新开 (★A 段 internal=0 ⇒ 20 条 open 全在 boss(5)/main(15) 名下、三个总工名下 open=0 ⇒ 兄弟 job 上一轮明确交接『下一轮开单来源 = 各总工交卷里的 needs_from + 独立的队列自动派活 job』⇒ 开单是本 job 的活★) ⇒ ★**依据 = 老板 11-04 01:19 demo 屏改型 + main 本轮实测 SW 侧零提及 + HW 侧 460 行官方取证已在盘** ⇒ ★**本单零外发: demo 半的官方口径自己查完, 整机半给降级结论, 不许再提外发放行** ★",
        "dispatched_at": None,
        "task_brief": BRIEF_212,
    },
    "ISS-213": {
        "id": "ISS-213",
        "title": "★★[主线内·结构侧·内部活] 结构侧 54 项交叉复核逐条定性 (17 条 FAIL 挂在 rc=0 且不在每日巡检链上 ⇒ 隐形) + demo 板当前成立的真缺陷收口 + 机器门禁 (PCB 布线/布局 6 条只定性排队不许修)",
        "severity": "high",
        "source_blocker": "ISS-203",
        "desc": "★**`MECH/hw_cross_review_check.py` 现在报 PASS 14 / FAIL 17 / 条件通过 8 / 说明 15 (共 54 项) 而 rc=0**, 它自己写着「★**FAIL 项不是'做不出来', 是'按现在的图纸/口径做出来会出问题'**」⇒ ★**17 条做出来会出问题挂着, 一个红灯都不点** ⇒ ★**★而且 main 实测 `state/daily_check.py` 里 grep 不到 hw_cross_review / service_port / hinge_usb / display_biosafety / cavity_recalc 任何一个 ⇒ 这 17 条在每日巡检里完全隐形** ⇒ ★**★同类问题第三次复发** (① 原理图 ERC 从未跑过 46 条 label_dangling 全盲 ② 图=表 尺子建之前一直假绿 ③ 现在结构侧 17 条 FAIL 也不在链上) ⇒ ★**本单的价值不在修 17 条, 在让这 17 条从隐形变成有账**: 54 项逐条定性 (每项给: 现状判定 / 与 demo 板相关性 / 是否在 MECH 地界内 / 处置 / 排队的恢复条件 / 证据等级) ⇒ ★**★按老板 11-11 10:07 原理图主线口径分流: MRG-X-3 / MRG-X-4 / MRG-54P / STK-FANOUT / FRM-SUM / PCB-X-GAP 这 6 条属 PCB 布线/布局/板框改动 ⇒ 一律【不许修】只定性 + 排队等原理图定稿; 其余 demo 板当前成立且在 MECH 地界内的 (印刷公差/开孔间隙/腔体/热路径/端件温升口径/功率守恒算式) 可以修; 跨域的 (NET-LED 网表 board 列 = HW 地界) 只登记 need 给 main** ⇒ ★**顺带收两条自家账: ① 分片 claim `mech_hinge_stack_fixed_mm` 仍 24.00 而文档 (ISS-206 裁 2 的 16p/20p/4p/10p) 已是 25.00 ⇒ 走 frag_write.py 改 ② 交 main 裁一条结论: ISS-126 (open/main/逾期) 仍按『板厚 0.41/0.80/1.00/1.22 四档, 只有 0.80 及以下才安全, 1.22 档净空 4.48 破 4.50』在写并把解锁挂在『等 PCB 厂 DFM 报告 (ISS-122)』上, 但结构真源 `MECH/BOARD_GEOM_30MM.md` §1 现行板厚 = 1.00mm (6 层)、`MECH/service_port_check.py` 现行基准 `pcb_thk` = 1.00 ⇒ 净空 4.70 ≥ 4.50 ⇒ 其前提已被现口径超越 (且『6 层 = 0.41mm』与现口径对不上) ⇒ main 给了这半边, 另半边交 main 裁** ★",
        "owner": "mech-lead",
        "reporter": "main",
        "raised": "2026-11-15",
        "due": "2026-11-19",
        "status": "open",
        "external": False,
        "need_keys": ["iss208_mech_recompute_optical_thermal_468mw"],
        "fix_ref": None,
        "verify_by": "main",
        "verify_result": None,
        "verify_date": None,
        "note": "2026-11-15 23:5x main 新开 (★A 段 internal=0 ⇒ 20 条 open 全在 boss(5)/main(15) 名下、三个总工名下 open=0 ⇒ 兄弟 job 上一轮明确交接『下一轮开单来源 = 各总工交卷里的 needs_from + 独立的队列自动派活 job』⇒ 开单是本 job 的活★) ⇒ ★**依据 = main 本轮实测 `hw_cross_review_check.py` 的 17 条 FAIL + `daily_check.py` 里 grep 不到它** ⇒ ★**本单不许改网表/板/脚表/PCB 布线布局/判据阈值** ★",
        "dispatched_at": None,
        "task_brief": BRIEF_213,
    },
}


def main():
    import fcntl
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        with open(LOG, encoding="utf-8") as f:
            log = yaml.safe_load(f)
        issues = log.get("issues") or []
        by_id = {i.get("id"): i for i in issues}

        # ★自证: 现有条目一个都不许被本脚本改 (只允许追加)
        before_ids = set(by_id)
        before_status = {k: v.get("status") for k, v in by_id.items()}

        out = []
        for iid, rec in NEW.items():
            if iid in by_id:
                raise SystemExit("%s 已存在, 拒绝重复开单" % iid)
            issues.append(rec)
            out.append("%s → %s 新开 (status=open, due %s)"
                       % (iid, rec["owner"], rec["due"]))

        log["issues"] = issues

        # ★yaml 往返自证 (确保写出去还能原样读回来)
        txt = yaml.safe_dump(log, allow_unicode=True, sort_keys=False, width=200)
        back = yaml.safe_load(txt)
        assert len(back["issues"]) == len(issues), "yaml 往返行数不一致"
        assert set(i.get("id") for i in back["issues"]) == (before_ids | set(NEW)), "yaml 往返 id 集合不一致"

        d = os.path.dirname(LOG)
        bak = LOG + ".bak_20261115_2355_open_211_212_213"
        shutil.copy2(LOG, bak)
        fd, tmp = tempfile.mkstemp(dir=d, prefix=".issue_log.", suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(txt)
            os.replace(tmp, LOG)
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)

        # ★写后复核: 既有条目的 status 一个都没变
        with open(LOG, encoding="utf-8") as f:
            log2 = yaml.safe_load(f)
        for i in log2["issues"]:
            iid = i.get("id")
            if iid in before_ids:
                assert i.get("status") == before_status[iid], \
                    "%s 的 status 被改了 (%s → %s)" % (iid, before_status[iid], i.get("status"))

        print("备份:", bak)
        for line in out:
            print(" -", line)
        print("自证: 既有 %d 条 status 全部未变 · yaml 往返一致 · 原子写完成" % len(before_ids))


if __name__ == "__main__":
    main()
