# ISS-325 · hw-lead · ★★「板只改一次」那一趟的 S8 前置: 「左上布局」21 器件钉位沙盒预演 (★把 ISS-322 的处方第一次真正单变量实跑一遍★)★★

> ★**派活人**: 项目总工 (main / moli) · ★**owner**: hw-lead · ★**verify_by**: main · ★**单号**: ISS-325
> ★**job**: cron `fb67af40` (ARS45 队列自动派活) · ★**派活时刻**: ★**2026-11-18 12:1x** ★
> ★**性质**: 内部活 · ★**PCB 线 · 纯沙盒预演 / 作业包 / 判据设计类 (HW 侧)** ★ · ★**零写板 · 零落表 · 零改闸 · 零改生成器代码 · 零改网表/脚表/BOM/原理图真源** ★ · ★**沙盒只写 `tmp/` + `logs/iss325/`** ★ · 零外发 · 不替老板拍板 · 不自签 issue_log
> ★**上游**: `ISS-322` (S8 布线归零作业包 · ★**verified 12:1x·本单的上游**) · `ISS-317` (S1 五侧改名清单 · verified) · `ISS-265` (S8 死因 5 条 · ★**方向已被 ISS-322 实测推翻·只当反面教材★**) · `ISS-308` (S8 可达性判决书 · verified)

---

## ★0 · 主线口径 (★老板 2026-11-17 00:43: 「接下来的目标是绘制 PCB 图」★)

★**当前主线 = 绘制 PCB 图** ⇒ ★**布线 / 布局类 ISS 现在【可派】** ★
★**但「板只改一次」铁律仍在**: 真动板那一趟必须一次做完 (位号改名 + 板侧同步 B-1~B-8 + ★**布局修正** + 布线 45→0 + Gerber/投产包重出 · 同一趟 · 背靠背) ★
★**本单是那趟的【前置预演】, 不是那趟本身** ⇒ ★**本单只在沙盒里跑, 官方板一个字节都不许动** ★
★**为什么它现在必须做**: ISS-322 已把 S8 的死因登记完 (45/45) 并判了「(a) 几何可布」, 但它同时留下一句 ★**「归零【从未被证明】—— 盘上 11 份 DRC JSON 最低 = 23, 无一份 = 0」** ★ ⇒ ★**S8 能不能真的归零, 现在是纯推算** ★ ⇒ ★**本单就是去把它变成实测** ★

---

## ★1 · main 12:1x 本机实读的事实 (★你的活从这些数开始, 不许自己重测当基线★)

| # | 事实 (★main 本机实跑·2026-11-18 12:1x★) | 怎么复现 |
|---|---|---|
| ① | ★**现役板 `HW/PCB/demo_mainboard.kicad_pcb` md5 = `611b869e13518c3c023fb178f91a0075` · mtime = `2026-11-06 07:07:17.362193413`** ⇒ **零写板双证的基线值** | `md5sum HW/PCB/demo_mainboard.kicad_pcb` · `stat -c "%y" HW/PCB/demo_mainboard.kicad_pcb` |
| ② | ★**现役板 DRC violations = 0 · unconnected items = 45** | `python3 state/check_pcb_drc.py HW/PCB/demo_mainboard.kicad_pcb` |
| ③ | ★**ISS-322 已 verified, 它的判决书在 `HW/PCB/BOARD_ONEPASS_S8_ROUTING_WORKPACKET.md`** (544 行 · §0~§7) ⇒ ★**你的处方不许推翻它, 只许实测它** | 读该文件 §3-5 / §3-6 / §3-8 |
| ④ | ★★**ISS-322 §3-8 的处方 (逐字)**: 「★**布局: 21 个器件 (`10×R_SEL_*` + `10×TP_DSI_*` + `R_SEL_D3_P` 换位) 挪到左上 x 5.50..38.35** ★」· 目标「★**段内 P/N 翻转 17 → 0** ★」· 「★**必须与 S1/S2/S3/S4/S6/S7 在【同一趟】里做完 —— 这样板 md5 仍然只变一次** ★」 | 同 ③ |
| ⑤ | ★★**本单存在的理由 (★main 查遍 53 个臂脚本得到的★)**: ★**盘上 53 个臂脚本 (★`state/` 目录下名字以 `.sh` 结尾的那批·★v31~v77 全系列★) 没有任何一个把 `TP_DSI_*` 钉到左上** ★ —— 只有 `state/v58_arms.sh` 与 `state/v69_arms.sh` 钉过 `TP_DSI_*`, 但那是在 **y=8.80** 的另一组坐标 (⇒ 跟左上无关) ★ ⇒ ★**⇒ ISS-322 的「21 器件」处方, 在本项目历史上【从未被单变量实跑过】** ★ ⇒ ★**⇒ 你跑的这趟就是【第一次】** ★ | `grep -rn "TP_DSI" state/ --include="*.sh"` (★main 实跑: 只有 v58 / v69 两个文件命中★) |
| ⑥ | ★**左上那 7 块同代板的 unc (ISS-322 §3-6 表)**: `35 / 35 / 28 / 29 / 29 / 26 / 23` ⇒ ★**现役板 (lane 序反) = 45 = 全盘最差** ★ ⇒ ★**unc 与 lane 序单调相关** ★ | 读 `logs/iss322/22_lane_order_vs_unc.txt` |
| ⑦ | ★★**⚠ 一处必须订正的读数 (★main 本机 fresh DRC 实跑发现的★)**: ★**那张表的 unc 列不是全部 fresh 测的** —— `logs/iss322/scripts/probe_lane_order_vs_unc.py` 把 unc **硬编码**在脚本里 (★`BOARDS` 列表★) ⇒ ★**main 对同一块板 (md5 `5a5197152157a70b19fbe1365283915c` = `state/.lastgood/baseline_v76mx0_chain.kicad_pcb` = `/tmp/chain_v76mx0/final_chain.kicad_pcb`) fresh 跑 DRC 得 ★**unc = 29 (不是表里的 26)**** ★ ⇒ ★**⇒ 那张表的 unc 列是【历史记录】不是【本单可复现的 fresh 读数】** ★ ⇒ ★**★本单必须把每个数都 fresh 测一遍, 不许抄那张表★** ★ | `bash state/kicad.sh pcb drc --output /tmp/_mx0.json --severity-error --severity-warning --format json state/.lastgood/baseline_v76mx0_chain.kicad_pcb` ⇒ 数 `unconnected_items` |
| ⑧ | ★**main 本机 fresh DRC 逐块复测 (四条链产物, ★可当你的对照先验·但仍要自己 fresh 测★)**: `chain_v76mz` = viol 4 / unc 30 · `chain_v76mg1` = viol 6 / unc 25 · `chain_v76mx0` = viol 0 / unc 29 · `chain_v76mw0` = viol 0 / unc 29 · ★**盘上最好板 `state/.lastgood/best_unc23_clrfix.kicad_pcb` 自带 DRC JSON = viol 0 / unc 23** ★ | 同 ⑦ 的命令, 换板路径 |
| ⑨ | ★★**左上目标坐标 (★main 从 `state/.lastgood/best_unc23_clrfix.kicad_pcb` 实读出来的封装原点·20 个器件★)**: `R_SEL_D3_P:5.50,3.00` `R_SEL_D3_N:7.95,3.00` `R_SEL_D2_P:13.10,3.00` `R_SEL_D2_N:15.55,3.00` `R_SEL_CK_P:20.70,3.00` `R_SEL_CK_N:23.15,3.00` `R_SEL_D1_P:28.30,3.00` `R_SEL_D1_N:30.75,3.00` `R_SEL_D0_P:35.90,3.00` `R_SEL_D0_N:38.35,3.00` ★ + ★`TP_DSI_D3_P:5.50,6.20` `TP_DSI_D3_N:7.95,6.20` `TP_DSI_D2_P:13.10,6.20` `TP_DSI_D2_N:15.55,6.20` `TP_DSI_CK_P:20.70,6.20` `TP_DSI_CK_N:23.15,6.20` `TP_DSI_D1_P:28.30,6.20` `TP_DSI_D1_N:30.75,6.20` `TP_DSI_D0_P:35.90,6.20` ★ + ★**`TP_DSI_D0_N:41.55,3.00`** (★唯一 y=3.00 那个·不许自己改成 6.20★)★ | ★**自己机器读一遍 (不许手抄上表)**: 读那个板的 `(footprint … (property "Reference" "R_SEL_*"` / `"TP_DSI_*"` 块里的 `(at x y` ⇒ ★**产出一张 TSV 进 `logs/iss325/`**★ |
| ⑩ | ★**现役板的 `TP_DSI_*` 落位 (★main 实读★)**: 9 个在 **y=79.70** (右侧竖排) · `TP_DSI_D0_N` 在 (75.70,5.50) · `TP_DSI_D3_P` 在 (75.70,9.50) ⇒ ★**⇒ 现在 lane 序是反的 (与 SoM 端序相反), 正是 unc=45 的成因** ★ | 同 ⑨ 的机器读法, 读现役板 |
| ⑪ | ★★**配方 (★照抄 `state/v76mz_arms.sh` 的 env, 逐字节不变★)**: `PCB_LAYERS=8 PCB_ABUDGET_MULT=6 PCB_HALO_MARGIN=0.0625 PCB_BOARD_W=160 PCB_BOARD_H=100 PCB_AREA_BOT=5,58,70,97 PCB_AREA_TOP=78,5,120,36 PCB_AREA_RES=78,38,157,97 PCB_PIN_CONN_CAM=1 PCB_SKIP_PAD_CELLS=1 PCB_PAIR_ESCAPE_EXEMPT=1 PCB_PAIR_EXEMPT_R=0.0 PCB_GND_FIRST=1 PCB_VIA_HALO_MARGIN=0.0 PCB_CONN_GND_ESCAPE=CONN_CAM:4.0 PCB_KEEPOUT=24.0,56.1,35.6,59.6` + `PCB_PAIR_BEFORE_PWR=1` + `PCB_PRIORITY_NETS="FSIN_OUT;LIGHT_5V;LIGHT_3V3;I2C_A_SCL;I2C_A_SDA;I2C_B_SCL;I2C_B_SDA;LED_G;LED_G_D;KEY_CAM;JTAG_TDI;SPI_SCLK_BOOT;SPI_MOSI_BOOT;SPI_MISO_BOOT;UART_RX;USB_CC2;BAT_DET;ID_DETECT_0;ID_DETECT_1;JTAG_TDO;JTAG_TMS;UART_TX;LED_B_D"` + `PCB_W_MIN=0.15` + `PCB_VIA_HALO_CENTER=1 PCB_MERGE_FIX=1 PCB_ESC_ROWNORM=2` + `PCB_PRIO_SPAN_SORT=1 PCB_MEANDER_EDGE=1 PCB_GRID=0.125` + ★**`PCB_ROUTE_RESERVE=<复用 state/.lastgood/v76mg_reserve.txt 的整串>`** ★ | ★**`state/v76mz_arms.sh` L40~L60 逐字读★ · ★**预留串文件 md5 = `1950683f8f2981eb6e1141c3559c02a6` (只读复用·不许覆盖它)★** ★ |
| ⑫ | ★**唯一变量**: ★**`PCB_PART_POS` 从 10 个 `R_SEL_*` 扩到 20 个 (加 10 个 `TP_DSI_*`)** ★ ⇒ ★**其余 env 一个字节都不许动** ★ | 同 ⑪ |
| ⑬ | ★★**三个写盘陷阱 (★main 实读源码确认·踩中就污染官方盘面★)**: ★**(a)** `state/gen_pcb_netlist_board.py` 的 `REPORT` 默认写 ★**`HW/PCB/PCB_NETLIST_FILL.txt`** ★ ⇒ ★**必须设 `PCB_REPORT=/tmp/<你的路径>`** ★ (★盘上 53 个臂脚本**没有一个**设过它·所以历史臂都覆盖过那个文件★) ★**(b)** ★**绝不许设 `PCB_ALLOW_OFFICIAL=1`** ★ (★设了就能覆盖官方板·生成器 L75~L82 有守卫★) ★**(c)** ★**`PCB_OUT` 必须以 `.kicad_pcb` 结尾** ★ (★否则生成器 L56~L70 直接 `sys.exit(3)` 秒退·v69 那轮白跑 6 小时的前车之鉴★) ★ | ★**`state/gen_pcb_netlist_board.py` L55~L90 + L75~L82★** ★ |
| ⑭ | ★★**`.layout_done.json` 不会被污染 (★已确认★)**: ★**生成器只在 `PCB_OUT` == 官方板路径时才写 `HW/PCB/.layout_done.json`** (★L520~L526 显式守卫: 非官方板 ⇒ 打印「不写 .layout_done.json」并 return★) ⇒ ★**你用 `PCB_OUT=/tmp/...` ⇒ 阶段门读的 `HW/PCB/.layout_done.json` (unconnected=45) 一个字节都不会动** ★ | `sed -n '510,530p' state/gen_pcb_netlist_board.py` |
| ⑮ | ★★**⚠ 生成器代码比参照板新 ⇒ 你的读数是【新数据点】, 不许宣称「复现了 unc 23」★**: ★`state/gen_pcb_netlist_board.py` mtime = **2026-11-17 05:16** · `state/gen_pcb_routing.py` mtime = 2026-11-11 04:33 · 而 `best_unc23_clrfix.kicad_pcb` 是 **2026-11-11 04:43** ⇒ ★**⇒ 官方生成器在参照板之后被改过 ⇒ 你这趟的结果【无论好坏】都是新事实, 不是复现** ★ ⇒ ★**⇒ 交卷页必须写清这一点, 不许把「和我以为的一样」当结论** ★ | `ls -la --time-style=+%F_%H:%M state/gen_pcb_netlist_board.py state/gen_pcb_routing.py state/.lastgood/best_unc23_clrfix.kicad_pcb` |
| ⑯ | ★**对照锚点**: ★**现役板 (unc 45 · lane 序反)** ★ vs ★**左上臂 (你跑出来的)** ★ vs ★**`state/.lastgood/best_unc23_clrfix.kicad_pcb` (unc 23 · 左上限序 · 2026-11-11)** ★ ⇒ ★**三方对照 (unc 条数 + 网名集合差集 + DRC)** ★ | ★**`state/cmp_unc_sets.py` (网名集合三层口径) + `state/compare_arm_official.py` (名单制闸)★** ★ |
| ⑰ | ★**闸链现状 (main 12:1x 实跑)**: `python3 state/gate_check.py` ⇒ ★**rc=0** ★ · ★**Q1 18/18** ★ · ★**Q7 钉板 md5 闸链 9/9 全绿** ★ ⇒ ★**你交卷时 rc 必须是 0; 若红 ⇒ 逐字归因到某一件, 不许「环境问题」四个字糊过去** ★ | `python3 state/gate_check.py` |
| ⑱ | ★**磁盘**: `/tmp` 剩 **5.2G / 7.5G** (tmpfs) · 工作区 `tmp/` 725M · 根分区剩 **388G** ⇒ ★**沙盒产物放 `tmp/iss325/` 或 `/tmp/iss325_*` 都行, 但链产物 `state/replay_patch_chain.sh` 会写死 `/tmp/chain_<TAG>` ⇒ 你的 TAG 要带 `iss325` 前缀以免撞历史链** ★ | `df -h /tmp .` |
| ⑲ | ★**时间盒**: ★**一条臂 ≈ 路由器 10~12 min + 套链 6~12 min (★main 实测历史臂的 mtime 差★) ⇒ ★**整单预算 ≤ 75 分钟**, 超时就把已完成的部分如实交上来 (★**不许为了凑齐而删掉真实读数★**) ★ | ★**历史臂 mtime: `/tmp/v76mz_R.log` 09:30 → `/tmp/chain_v76mz/final_chain.kicad_pcb` 09:36★** ★ |
| ⑳ | ★**★不许把「归零」当本单的交付结论★**: ★**盘上从来没有一块板到过 unc = 0** ⇒ ★**你跑出 0 是意外之喜, 跑不出 0 也是有价值的实测 (它会把「归零」从推算变成「已知做不到 / 已知能做到但差多少」)** ★ ⇒ ★**★两种结果都要如实交, 不许只报好看的★** ★ | 同 ⑮ 的读数 |

---

## ★2 · 本单要交的东西 (★5 件 · 缺一不算交卷★)

### ★★交付物 (2 件) · ★★这两份是本单新建的文件 (★交卷时才有 ⇒ 交卷前必然不存在★)★★

1. ★**新建 `HW/PCB/ONETRIP_S8_LEFTUPPER_REHEARSAL.md`** ★ (★主交付物·§0~§9★)
2. ★**新建 `HANDOFF/2026-11-18_hw-lead_ISS325_左上布局沙盒预演.md`** ★ (★交卷页·B0~B6★)

### ★① 【主交付物】「左上布局」沙盒预演作业包 (★新建文档★)

- ★**落点**: ★**`HW/PCB/ONETRIP_S8_LEFTUPPER_REHEARSAL.md`** ★ (★**新建**; ★**`HW/PCB/BOARD_ONEPASS_S8_ROUTING_WORKPACKET.md` 是 ISS-322 的, 只读·不许改★**)
- ★**章节 (每一节都要填实, 不许写「同上」/「见前」)**:
  | § | 内容 | ★**硬要求** ★ |
  |---|---|---|
  | §0 | 口径与边界自证 | ★**写清本单是什么 / 不是什么 (沙盒预演·零写板·零落表·零改闸·零改生成器代码)★** ★ |
  | §1 | ★**处方复述 + 目标坐标机器读取表** ★ | ★**从 `state/.lastgood/best_unc23_clrfix.kicad_pcb` 机器读出 20 个器件的封装原点 ⇒ 出 TSV ⇒ 逐字给最终 `PCB_PART_POS` 串★** ★**不许手抄 (★main 表里的数只当交叉核对用·§1-⑨★)★** ★ |
  | §2 | ★**臂配置 (env 逐字 + 唯一变量说明)** ★ | ★**env 逐字列出来 + 标出「唯一变量 = `PCB_PART_POS` 多 10 个 `TP_DSI_*`」+ 预留串 md5 (只读复用)★** ★ |
  | §3 | ★**跑批读数 (三方对照表) ★** | ★**现役板 45 (fresh 实测) vs 你的左上臂 vs `best_unc23_clrfix` 23 ⇒ 每格都要 fresh DRC 出来的数 + 各自的板 md5 (⇒ 别人能对得上是哪块板)★** ★ |
  | §4 | ★**网名集合对照 (不是只比条数!) ★** | ★**用 `state/cmp_unc_sets.py` 出【网名集合 / 端点归属集合 / 精确端点坐标】三层口径的差集 (★三层的强弱差别照它自己的 docstring 抄★)⇒ ★**并逐条回答: 左上臂比现役板【少了哪些网】/【多了哪些网】/【哪些网两边都没通 (硬骨头)】** ★ |
  | §5 | ★**名单制闸判定 (★照 ISS-322 §4-3-③ 的写法★) ★** | ★**`python3 state/compare_arm_official.py <你的候选板> HW/PCB/demo_mainboard.kicad_pcb` ⇒ ★**退铜名单必须为空 · 差分死腿必须为空 · 逐网孤岛不许变多** ★ ⇒ ★**★把这三条逐条抄出来, 不许只写「通过/不通过」★** ★ |
  | §6 | ★**段内 P/N 顺序翻转复算 (★ISS-322 §3-5 的 17/47 那个指标★) ★** | ★**用归档脚本 `logs/iss322/scripts/probe_pn_order.py` 对你的候选板跑 ⇒ ★**目标: 翻转 17 → 0** ★ ⇒ ★**并给出「CSI 侧那 5 族 (Δx=0.50mm) 的翻转有没有单独解决」** ★ |
  | §7 | ★**结论: 「归零」到底可达不可达 (★本单最值钱的一段★) ★** | ★**跑出 0 ⇒ 给出「零可达」的第一个实测证据 + 它怎么来的★** ★**跑不出 0 ⇒ 逐条列出「离 0 还差几条 + 每条卡在什么上 (照 ISS-322 §2-6 的机制级读数: 板上零铜 vs 长了一半)」★** ★**两种都必须给「不跑这趟会怎样 / 跑完这趟改变了什么」★** ★ |
  | §8 | ★**给「板那一趟」的作业包增补 (★逐字改法, 零改真文件★) ★** | ★**给 `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` §3-S8 与 `HW/PCB/LAYOUT_FIX_SPEC.md` §0 的逐字改法 + 行号 (★照 ISS-322 §5-6 的写法★)★** ★**★其中必须包含一条: 「『官方板 18092』= 现役板本身 ⇒ 它是【自证】不是【旁证】」这条订正·不许被改回去★** ★ |
  | §9 | ★**证据分级 + 零写板双证 + 文件清单 ★** | ★**`[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` 逐条标 + 板 md5/mtime 交卷前后 + 占位符扫描 0** ★ |
- ★**占位符扫描必须 0** (★扫 `🔄` / `待填` / `PLACEHOLDER` / `施工中★)

### ★② 交卷页 (★标准验收块 B0~B6 齐全★)

- ★**落点**: ★**`HANDOFF/2026-11-18_hw-lead_ISS325_左上布局沙盒预演.md`** ★
- ★**B0** 一句话 + 交付物清单 · ★**B1** 结论摘要 (★**第一条必须是「左上布局跑出来 unc = ? · 归零可达 = ?」**★) · ★**B2** 验收标准自评 (★逐条 通过/不通过/未验★) · ★**B3** 证据分级 · ★**B4** 接口取值声明 (★**别人要照抄的东西逐字给: 最终 `PCB_PART_POS` 串 + 臂 env + 三方对照表 + 名单制闸三条判定★**) · ★**B5** 未决项与卡点 (★need key + 一句话问法 + 不拍的后果★) · ★**B6** 自证复现命令 (★逐条可跑·输出已落盘★)
- ★**占位符扫描 0**

### ★③ 原始输出目录

- ★**落点**: ★**`logs/iss325/`** (★新建·只写自己这一份★)
- ★**内容**: ① 目标坐标机器读取 TSV + 读取脚本 ② 臂 env 快照 + 臂运行日志 (★**逐字拷贝 `PCB_PART_POS` 串·不许手抄进文档★**) ③ fresh DRC JSON (每块板一份) ④ 三方对照表 ⑤ `cmp_unc_sets` 输出 ⑥ 名单制闸输出 ⑦ `probe_pn_order` 输出 ⑧ 零写板双证 ⑨ 交卷前门禁链输出
- ★**★沙盒纪律★**: ★**沙盒只写 `tmp/iss325/` + `logs/iss325/`** ★ ⇒ ★**`state/.lastgood/**` 只读·`HW/PCB/**` 只读·`SW/**` / `MECH/**` 一律不碰** ★

### ★④ hw 分片

- ★**落点**: ★**`state/fragments/hw.yaml`** · ★**必须走 `python3 state/frag_write.py --agent hw-lead` 原子写** ★ (★禁止 `open(p,"w")`★)
- ★**内容**: artifacts (≥1 · 指向 ①②) · needs_from (★**一条新的 need: `iss325_s8_zero_reachability` (key 自拟但必须唯一 + 写在交付页里)★ · 问法 = 「★**S8 归零到底可达不可达? 左上布局跑完 unc = ? 离 0 还差几条 / 差在哪**★」· 不拍的后果 = 「★**S8 归零仍是推算 ⇒ 那一趟可能白做 (板 md5 变第一次但归不了零 ⇒ 还得再改一次 ⇒ 2-4 周 + ¥4-8K)**★」· 谁答 = ★**main + 老板 (★依 G7 `iss322_s8_rsel_lane_order` 的落板★)★**) · interface_claims (≥1 · 给别人照抄的 `PCB_PART_POS` 串 + 三方对照表) · status

### ★⑤ 交卷前必跑 (★逐字可粘贴·输出原样贴进交卷页★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses

# ① 零写板双证 (★交卷前后各跑一次·两次都要贴★)
md5sum HW/PCB/demo_mainboard.kicad_pcb        # 必须 = 611b869e13518c3c023fb178f91a0075
stat -c "%y" HW/PCB/demo_mainboard.kicad_pcb  # 必须 = 2026-11-06 07:07:17.362193413

# ② 名单制闸 (★ISS-322 §4-3-③ 的写法·退铜/差分死腿/逐网孤岛 三条都要抄出来★)
python3 state/compare_arm_official.py --self-test                     # 必须 rc=0 · ALL TESTS PASS
python3 state/compare_arm_official.py <你的候选板> HW/PCB/demo_mainboard.kicad_pcb

# ③ 网名集合对照 (三层口径)
python3 state/cmp_unc_sets.py <你的候选板>.drc.json <现役板>.drc.json

# ④ 图纸门禁 (★你的候选板必须 viol=0 / unc 读数报出来★)
python3 state/check_pcb_drc.py <你的候选板>

# ⑤ 门禁链 (★rc 必须 0 · Q1 必须 18/18 · Q7 必须 9/9★)
python3 state/merge.py && python3 state/gate_check.py && python3 state/issue_check.py

# ⑥ 占位符 (★两份交付文档都必须 0★)
grep -cE "🔄|待填|PLACEHOLDER|施工中" HW/PCB/ONETRIP_S8_LEFTUPPER_REHEARSAL.md
grep -cE "🔄|待填|PLACEHOLDER|施工中" "HANDOFF/2026-11-18_hw-lead_ISS325_左上布局沙盒预演.md"

# ⑦ 分片已写 (★必须 ≥1★)
grep -c "iss325" state/fragments/hw.yaml
```

---

## ★3 · 边界 (★一条都不许越★)

| # | 边界 | 自证方式 |
|---|---|---|
| 1 | ★**零写板** ★ | ★**官方板 md5 + mtime 交卷前后逐字节相同 (★且 `.layout_done.json` 也不许动·★它是阶段门 G1 的判据来源★)★** |
| 2 | ★**零落表** ★ | ★网表 / 脚表 / BOM / 原理图源 md5 全部未变 ★ |
| 3 | ★**零改闸 + 零改生成器代码** ★ | ★**`state/*.py` / `state/*.sh` / `MECH/*.py` / `SW/tools/*.py` 全部 md5 未变 (★你只新建臂脚本, 名字带 `iss325`, 放在 `state/` 下★)★** |
| 4 | ★**零改既有文档正文** ★ | ★**`HW/PCB/**` / `MECH/**` / `SW/**` 既有文件 md5 全未变 (★§8 只给「逐字改法 + 行号」, 不动原文★)★** |
| 5 | ★**不写别人的分片** ★ | ★**只写 `state/fragments/hw.yaml`** ★ (★`sw.yaml` / `mech.yaml` / `pm.yaml` 一个字节都不许碰★) ★ |
| 6 | ★**零外发** ★ | ★**不许发任何邮件 / 询价 / 问询 / 采购 (老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料) ⇒ 需要外部资料一律自己网上查 + 标证据等级 + 查不到写降级方案 ⇒ 没有「批一句可以发」这个选项** ★ |
| 7 | ★**不替老板拍板** ★ | ★**G7 (`iss322_s8_rsel_lane_order`) 的落板归 main + 老板** ★ ⇒ ★**你只给实测读数 + 选项 + 代价 + 建议默认值 + 不拍的后果, 不给「决定」** ★ |
| 8 | ★**不自签 issue_log** ★ | ★**`state/issue_log.yaml` 一个字节不许动 (★签字是 main 的活★)** ★ |
| 9 | ★**不许覆盖历史链 / 预留串** ★ | ★**`/tmp/chain_*` 与 `state/.lastgood/v76mg_reserve.txt` 只读·你的 TAG 必须带 `iss325` 前缀★** ★ |

---

## ★4 · 时间盒与「交半成品」纪律 (★本项目的老教训·这轮特意写进来★)

★**整单 ≤ 75 分钟** ⇒ ★**超时就把已完成的部分如实交上来** ★
★**具体做法 (★照 ISS-317 cont2 的成功做法★)**:
1. ★**§1 的坐标表 + §2 的 env 快照先落盘** (★这两件不依赖跑批·几分钟就完★) ⇒ ★**万一超时, 作业包也有骨架 + 可复现配方★**
2. ★**臂跑起来之后, 每产出一个读数就往 `logs/iss325/` 落一份** (★不要攒到最后一起写★) ⇒ ★**被中断也不丢读数★**
3. ★**★不许为了「看起来完整」而把没跑的部分写成实测★** ⇒ ★**没跑的格写「未跑 (原因)」·不许填数★**

---

## ★5 · 给 main 的 need (★本单不代拍·逐条登记到分片的 needs 里★)

★**need key 建议前缀**: `iss325_s8_*` · ★**每条必须带: 一句话问法 + 谁答 + 不答的后果 (★量化: 板 md5 变几次 / 投不投得了板★) + 建议默认值 + 建议排期** ★

---
