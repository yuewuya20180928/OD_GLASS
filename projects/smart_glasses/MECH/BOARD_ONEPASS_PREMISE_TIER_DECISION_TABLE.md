# MECH · 「板那一趟」排针焊盘【前提量选档 ⇒ 下游作废传播】机器可判决策表 (ISS-410 · mech-lead)

> ★**生成**: 2026-11-25 02:5x~04:0x (mech-lead · 本机实跑) · ★**形态**: ★**纯查证 + 纯分析 · 零写板 · 零落表 · 零改既有闸 · 零改既有页正文 · 零挂链 · 零外发 · 不代拍 · 不自签** ★
> ★**纪律归位**: 「板只改一次」纪律 ① (★先派纯分析/作业包类·不动板★) · ★**本单是【开工前的选档决策表】, 不是【已经出事】** ★
> ★**证据等级**: `[官网]` = 厂商官网/能力表逐字 · `[实测]` = 本机实读/实跑读数 · `[媒体]` = 第三方报道 · `[推算]` = 本机按公式算 · `[0数据]` = 查不到 ★
> ★**承接**: ISS-403 (焊盘 1.000→1.110 ⇒ 7 个数全作废 + 5 道盲闸·出【矩阵】不出【闸】) · ISS-407 (判决链前提依赖图 + 作废传播矩阵·出【依赖图 + 一道盯依赖图的闸】·但依赖图没接上「四档选哪一档」这个入口) · ISS-405 (29 道闸只挂 4 道) ★★**本单不重复它们, 是把它们【接成一张可执行的选择表 + 一道盯这张表的闸】** ★
> ★**本页所有数值均由 `MECH/check_premise_tier_decision.py` 现读/实算后渲染 (★不许手抄★)** ★

==============================================================================
## ★§0 · 一句话结论 (★本机实跑得出·不抄任何 agent 报告★) ★

★★ **「板那一趟」的排针焊盘前提量今天【连「现在盘上是哪一档」都答不出来】—— 板面实读: `J_DEBUG`/`J_UART` 是【自绘 SMD 占位 land】(焊盘 `0.2750×0.9000` · pitch `0.50` · 【无钻孔】) ⇒ 【板面压根没有 THT 排针焊盘】⇒ 四档 (`1.000`/`1.010`/`1.110`/`1.218`) 全部是【未来板面】的候选值, 不是现状值; 而四个记着这一格的来源里【只有 1 个真记着】(真相页机器块记 P1000) · 【BOM 没这一格】 · 【作业包没这一格】 · 【板面这一格是空的】⇒ ⇒ 「板只改一次」那一趟开工前, 没有任何机器闸能回答「现在到底是哪一档 / 换档要重算什么 / 换档了有没有人重算」** ★★

★**判据句 (方向)**: ★**MECH 侧必须把「前提量的【四档候选】+【四来源各自记没记】+【换档的重算/重跑/重签清单】+【当前档位能不能从板面机器判】」四件事【同时】落成机器可判, 并在「板那一趟」开工前【逐来源对齐 + 逐档照单重算】⇒ 否则前提量在那一趟被顺手改动, MECH 七个数当场作废, 而 5 道闸对它【完全盲】⇒ 结构件按旧数出件 ⇒ 装配干涉 ⇒ 板改第二次** ★
★**事实句 (现状)**: ★**本机实跑: ① 板面 `J_DEBUG`/`J_UART` = SMD 占位 (`0.2750×0.9000` · pitch `0.50` · 无钻孔) ⇒ 【四档哪一档都不是】; ② 四来源逐条实读 ⇒ BOM 【没这一格】 · 作业包 【没这一格】 · 真相页机器块 【记 P1000】 · 板面 【没这一格】 ⇒ 【四来源不一致 ⇒ 现状红】; ③ 本单新闸 `MECH/check_premise_tier_decision.py` 【裸跑 rc=1】—— ★**红的是现状, 不是闸故障** ★** ★★
★**两句同时成立, 不许混成一句「OK / 合格」** ★

★**★⇒ 本单对 ISS-403 的一处【口径订正】(★本机实读·必须写死, 否则下一个人会照抄错口径★) ★**:
★**ISS-403 §7 机器块 `current_pad` 记的是 KiCad 官方库 `.kicad_mod` 的 `(size 1 1)` —— 那是【板那一趟】要落的 THT 封装, 不是【现在板面上的东西】★**
★**⇒ 本单把「板面实读」单列为四来源之一 ⇒ 四来源的「板面 footprint」这一格实读结果是【SMD 占位】⇒ 这就是本单 T2 判红的根因 (★不是闸坏了, 是这一格真的空着★)** ★ `[实测]`

==============================================================================
## ★§1 · 表 (a-1) · 四档 × 七个数 · 完整矩阵 (★28 格·本机按公式实算 + 与 ISS-403 登记值逐格对拍★) ★

### ★§1.1 · 七个数是谁 + 各自的推导式 (★公式单一事实源 = 本页机器块 `seven_number_defs`★) ★

| # | ★数名★ | ★推导式★ | ★常量取值 + 出处★ |
|---|---|---|---|
| ① | `j_debug_copper_x` | `跨距 3.8100 + pad` | 跨距 `3.8100` = KiCad 官方库 `PinHeader_1x04_P1.27mm_Vertical.kicad_mod` 实读 `[实测]` |
| ② | `j_uart_copper_x` | `跨距 1.2700 + pad` | 跨距 `1.2700` = 同族 `PinHeader_1x02_P1.27mm_Vertical.kicad_mod` 实读 `[实测]` |
| ③ | `j_debug_required_clear_x` | `① + 2 × (CRIT + TOL)` = `① + 1.8000` | `CRIT 0.6000` / `TOL 0.3000` = `MECH/service_port_check.py` L126-L127 `[实测]` |
| ④ | `j_uart_required_clear_x` | `② + 2 × (CRIT + TOL)` = `② + 1.8000` | 同上 `[实测]` |
| ⑤ | `j_uart_cover_margin_x` | `(座体必须清空区 X 宽 2.5400 − ②) / 2` | `2.5400` = `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` L346 `[实测]` |
| ⑥ | `j_debug_opening_margin_x` | `(开口 X 宽 10.2000 − ①) / 2` | `10.2000` = 同页 L352 `[实测]` |
| ⑦ | `j_debug_cover_margin_y` | `(座体必须清空区 Y 宽 2.5400 − pad) / 2` | `2.5400` = 同页 L351 `[实测]` (★`copper_y = pad`★) |

### ★§1.2 · 全矩阵 (★4 档 × 7 数 = 28 格★) ★

★**读法**: ★`铜箔X` = ①/② · `清空需求` = ③/④ · `罩住X` = ⑤ · `开口X` = ⑥ · `罩住Y` = ⑦ ★

| 档位 | pad | 环宽(Ø0.71) | ① `J_DEBUG` 铜箔X | ② `J_UART` 铜箔X | ③ `J_DEBUG` 清空需求 | ④ `J_UART` 清空需求 | ⑤ `J_UART` 罩住X | ⑥ `J_DEBUG` 开口X | ⑦ `J_DEBUG` 罩住Y |
|---|---|---|---|---|---|---|---|---|---|
| ★`P1000`★ | `1.000` | `0.1450` | ★`4.8100`★ | ★`2.2700`★ | ★`6.6100`★ | ★`4.0700`★ | ★`0.1350`★ | ★`2.6950`★ | ★`0.7700`★ |
| `P1010` | `1.010` | `0.1500` | `4.8200` | `2.2800` | `6.6200` | `4.0800` | `0.1300` | `2.6900` | `0.7650` |
| ★`P1110`★ | `1.110` | `0.2000` | ★`4.9200`★ | ★`2.3800`★ | ★`6.7200`★ | ★`4.1800`★ | ★`0.0800`★ | ★`2.6400`★ | ★`0.7150`★ |
| `P1218` | `1.218` | `0.2540` | `5.0280` | `2.4880` | `6.8280` | `4.2880` | `0.0260` | `2.5860` | `0.6610` |

★**★【抄录对拍 · 28/28 逐格一致】★**: ★**本机按 §1.1 的公式实算 28 格 ⇒ 与 ISS-403 交卷页 `MECH/BOARD_ONEPASS_PAD_SIZE_COUPLING.md` §7 机器块 `seven_numbers_matrix` 的 28 格【逐格逐字相同】(★差 > 1e-9 即判红★) ⇒ 抄对** ★ (`[实测]` + `[推算]`)

★**★【逐档过阈结论 (★`最坏 = 余量 − TOL 0.30` ⇒ 过阈要 `余量 ≥ CRIT 0.60`★)】★**:

| 档位 | ⑤ `J_UART` 罩住X | 最坏 | 判决 | ⑦ `J_DEBUG` 罩住Y | 最坏 | 判决 | ⑥ `J_DEBUG` 开口X | 最坏 | 判决 |
|---|---|---|---|---|---|---|---|---|---|
| `P1000` | `0.1350` | `-0.1650` | ★**红** ★ | `0.7700` | `0.4700` | ★**红** ★ | `2.6950` | `2.3950` | 绿 |
| `P1010` | `0.1300` | `-0.1700` | ★**红** ★ | `0.7650` | `0.4650` | ★**红** ★ | `2.6900` | `2.3900` | 绿 |
| `P1110` | `0.0800` | `-0.2200` | ★**红 (更狠)** ★ | `0.7150` | `0.4150` | ★**红 (更狠)** ★ | `2.6400` | `2.3400` | 绿 |
| `P1218` | `0.0260` | `-0.2740` | ★**红 (最狠)** ★ | `0.6610` | `0.3610` | ★**红 (最狠)** ★ | `2.5860` | `2.2860` | 绿 |

★**★⇒ 三条硬事实 (★本机实算★) ★**:
★**① 7 个数【无一例外全部要重算】**: ①/② 直接吃 pad; ③/④ 由 ①/② 派生; ⑤ 由 ② 派生; ⑥ 由 ① 派生; ⑦ 由 pad 直接派生 ⇒ ★**一个都不例外** ★ `[推算]`
★**② 焊盘越大越红**: ⑤ `0.1350 → 0.1300 → 0.0800 → 0.0260` (最坏 `-0.1650 → -0.1700 → -0.2200 → -0.2740`) · ⑦ `0.7700 → 0.7650 → 0.7150 → 0.6610` (最坏 `0.4700 → 0.4650 → 0.4150 → 0.3610`) ⇒ ★**两个本来就红的项, 档位每往上走一格就红得更狠** ★ `[推算]`
★**③ 环宽这一格决定哪一档【在物理上成立】**: `(pad − 0.71)/2` ⇒ `0.1450` / `0.1500` / `0.2000` / `0.2540` ⇒ 详见 §3 ★ `[推算]`

==============================================================================
## ★§2 · 表 (a-2) · 四来源「这一格记没记 / 记的是哪一档」· 逐来源判定 (★本机逐源实读★) ★

★**★【四来源是谁】★**: ★**① `SRC_BOM` = `HW/BOM_v1.csv` · ② `SRC_WORKPACKET` = `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` · ③ `SRC_TRUTH_PAGE` = `MECH/BOARD_ONEPASS_FTS_VS_GENERIC_COURTYARD_DELTA.md` (机器块) · ④ `SRC_BOARD_FACE` = `HW/PCB/demo_mainboard.kicad_pcb` (J_DEBUG/J_UART 的 footprint 实读)** ★

| 来源 | ★机器读法 (★不许手抄★)★ | ★「记没记这一格」★ | ★记的是哪一档★ | ★本机实读证据 (★逐字★)★ |
|---|---|---|---|---|
| ★`SRC_BOM` ★ | ★`csv.DictReader` ⇒ 取 `ref ∈ {J_DEBUG, J_UART}` 两行 ⇒ 全行文本搜「≥3 位小数 且 值 ∈ 四档」的 token ★ | ★**✗ 没记** ★ | —— | ★`HW/BOM_v1.csv:71` `J_DEBUG,1,1×4 1.27mm 排针 (JTAG),CONN,必装,镜脚主 PCB,P8,[推算],,待定,,待定,待定,连接器,型号/间距/引脚编号待结构与装配复核 (★本版 pin 编号自拟)` · ★`:77` `J_UART,1,1×2 1.27mm 排针 (UART),…` ⇒ **`footprint`/`opn`/`tolerance`/`alt_part` 四列全空或「待定」· `memo` 只写「型号/间距/引脚编号待结构与装配复核」⇒ 【压根没有 pad 尺寸这一格】** ★ ⇒ ★**记的是【间距 1.27】(那是 `PQ05`/`PQ06`), 不是【焊盘边长】(本单前提量)** ★ |
| ★`SRC_WORKPACKET` ★ | ★全文搜「≥3 位小数 且 值 ∈ 四档」的 token ★ | ★**✗ 没记** ★ | —— | ★**本机实跑: 全文命中 `1.010` / `1.110` / `1.218` / `1.000` 的 token 数 = 0** ★ ⇒ ★**L243 调试口开口段写的是「`OPEN_X` 常量 `10.200`」+ 罩住清空区 X `142.0625..143.8375` + 单边净距 X `4.2125` / Y `1.0300` ⇒ 这些数是按现状算出来的, 但那一段【没写死 pad 档】⇒ 前提量改了, 这段数【不会自己报警】** ★ |
| ★`SRC_TRUTH_PAGE` ★ | ★取该页最后一个 JSON 机器块 ⇒ `json.dumps` 全文 ⇒ 同款 token 搜 ★ | ★**✓ 记了 (在 note 字段里)** ★ | ★**`P1000`** ★ | ★**机器块 `dimensions.copper_env_x_4pos.note` 逐字「铜箔包络只由焊盘 `1.000x1.000` @1.27 跨距 `3.81` 决定; 钻孔 `0.65->0.71` 不进铜箔包络; …」· `copper_env_x_2pos.note` 逐字「同上 (`1.27 + 1.000`)」· `copper_env_y.value` = `1.0000` (note 逐字「同上 (焊盘宽 `1.000`)」) · `required_clearance_y_copper.note` 逐字「只吃铜箔 `1.0000 + 2 x 0.9000`」** ★ ⇒ ★**真相页把 `1.000` 写进了【现状值型判据】⇒ 这一格记的是 P1000** ★ |
| ★`SRC_BOARD_FACE` ★ | ★只读解析 footprint (括号配平) ⇒ `J_DEBUG`/`J_UART` 的 pad `size` / `type` / `drill` / `pitch` / 铜箔包络 ★ | ★**✗ 没记 (这一格是空的)** ★ | —— | ★**本机实读: `J_DEBUG` = 4 焊盘 · 全部 `smd rect` · size `0.2750×0.9000` · pitch `0.50` · 【无钻孔】· 铜箔 X `1.7750` / Y `0.9000`; `J_UART` = 2 焊盘 · 同样 `smd rect` · `0.2750×0.9000` · pitch `0.50` · 【无钻孔】· 铜箔 X `0.7750` / Y `0.9000`; 两者的 `(footprint "")` = 【库名空】⇒ 自绘占位** ★ ⇒ ★**板面【今天根本没有 THT 排针焊盘】⇒ 四档哪一档都不是 ⇒ 这一格不是「记错」, 是「没记」** ★ |

★**★⇒ 本表的三条结论 (★本机实跑★) ★**:
★**① 四来源【不一致】⇒ T1 判红 (★红的是现状★)**: ★**四个来源里只有 1 个 (真相页) 真记着这一格, 且它记的是 P1000 (★物理上已死的档: 环宽 0.1450 < 0.15★) ⇒ 三个来源没记 + 一个记着死档 ⇒ 「现在到底是哪一档」今天无人能答** ★
★**② 板面这一格【不是四档中任一档】⇒ T2 判红 (★红的是现状★)**: ★**板面实读 = SMD 占位 ⇒ 【不是任何一档】⇒ 前提量在板面上【还没有载体】⇒ 这正是「板只改一次」纪律 ① (先派分析, 别在那一趟顺手改) 的物理理由** ★
★**③ 【记的是哪一档】这件事【四来源没有一个能答】⇒ 「前提量的当前档位」至今无机器可判的读数** ★

==============================================================================
## ★§3 · 表 (c) · 「板厂工艺能力」这一格的【自己查】结果 (★不外发·不挂成外部依赖★) ★

★**★【本单自己查 · 证据等级 `[官网]`】★**

| 项 | 内容 | 证据等级 |
|---|---|---|
| ★**主源 (官网) ★** | ★**JLCPCB 官方 PCB 能力页** `https://jlcpcb.com/capabilities/pcb-capabilities` · ★**本单本机 curl 现取** ⇒ 落盘 `tmp/iss410/jlcpcb_pcb_capabilities_live.html` (md5 `351f5f897ea1236c30d4ad2409e84311` · 140276 B) ★ | `[官网]` |
| ★**逐字引用 (环宽四行) ★** | ★`PTH annular ring ≧0.20mm 2-layer: 1 oz: Recommended 0.25 mm or above; absolute minimum 0.18 mm 2 oz: 0.254 mm or above Multilayer: 1 oz: Recommended 0.20 mm or above; absolute minimum 0.15 mm 2 oz: 0.254 mm or above` ★ | `[官网]` |
| ★**复核 (与 ISS-403 留存件对拍) ★** | ★**ISS-403 留存的 `tmp/cron775d_r90/jlcpcb_pcb_capabilities_20261124_2043.html` (md5 `24dd86f068aa85728b74706f2fd80b3e`) ⇒ 本单现取件与它【环宽四行逐字相同】⇒ 能力表口径没漂** ★ | `[实测]` |
| ★**副源 (官网·第二家) ★** | ★**PCB.cn 官方能力页** `https://pcbcn.com/capabilities` ⇒ 逐字 `Min Width of Annular Ring | 0.15mm / 6mil` ⇒ ★**独立第二家也把环宽下限放在 0.15 这一量级 ⇒ 不是 JLCPCB 一家的口径** ★ | `[官网]` |
| ★**本板适用行 ★** | ★**`Multilayer: 1 oz`** ⇒ 绝对下限 `0.15` · 推荐值 `0.20` ★ —— 依据: 本板 = ★**8 层**★ (板文件 `(layers …)` 段 `F.Cu` + `In1..In6.Cu` + `B.Cu` 共 8 个 `*.Cu` signal 层, `[实测]`) · 外层铜 ★**1 oz**★ (`HW/PCB/FAB_ORDER_NOTES.md` §叠层表, `[实测]`) ★ | `[实测]` + `[推算]` |
| ★**条件句 (若板厂按 2 层做) ★** | ★2 层 1 oz 绝对下限 `0.18` ⇒ `P1010` 【不满足】⇒ 需 `pad ≥ 1.070` ★ | `[推算]` |

★**★【四档 × 四行能力口径 · 逐档过阈矩阵 (★本机实算★)】★**:

| 档位 | 环宽 | 多层 1oz 绝对下限 `0.15` | 多层 1oz 推荐 `0.20` | 2 层 1oz 绝对下限 `0.18` | 2 层 1oz 推荐 `0.25` |
|---|---|---|---|---|---|
| `P1000` | `0.1450` | ✗ | ✗ | ✗ | ✗ |
| `P1010` | `0.1500` | ✓ 恰达 | ✗ | ✗ | ✗ |
| `P1110` | `0.2000` | ✓ | ✓ 恰达 | ✓ | ✗ |
| `P1218` | `0.2540` | ✓ | ✓ | ✓ | ✓ |

★**★【降级方案 · 必须项 (★不许把「板厂是谁」继续挂成外部依赖★)】★**:
★**① 适用行【由本板自己的叠层规格决定, 不由板厂名字决定】** ⇒ 叠层 `8 层` + 外层 `1 oz` 是★**我们的规格**★ ⇒ 适用行恒为 `Multilayer: 1 oz` ⇒ ★**板厂名字【不参与】选档** ★ ⇒ ★**「板厂是谁」这一格【不再是选档的前置条件】** ★ `[推算]`
★**② 若仍要在【板厂完全未知】的前提下取一个【不必等任何回信就能确定可制造】的档** ⇒ ★**`P1218`** ★ (环宽 `0.2540` 同时 ≥ `0.15` / `0.18` / `0.20` / `0.25` 四行 ⇒ 四行全过) ⇒ ★**代价 = MECH 侧重算量最大 + `J_UART` 罩住余量 `0.0260` (最坏 `-0.2740`) 红得最狠** ★ `[推算]`
★**③ 若按推荐值 `0.20` 走 (最常见口径)** ⇒ ★**`P1110`** ★ (环宽 `0.2000` 恰达) ⇒ ★**MECH 侧代价居中** ★ `[推算]`
★**④ 本单【不外发任何邮件 / 询价 / 问询 / 采购】** (★老板 2026-11-11 19:31 + 2026-11-12 02:02「不再发信, 全靠自己查资料」★) ⇒ ★**四档全列 + 每档达成口径 + 每档 MECH 侧后果 + 每档结构件代价 全部算好 ⇒ main 拍档时直接选一档即可, 不必回本单再算一遍, 也不必等板厂回信** ★ `[实测]`

==============================================================================
## ★§4 · 表 (b) · 每档的「必须重算 / 必须重跑 / 必须重签」清单 (★从 ISS-407 依赖图现算导出★) ★

★**★【导出规则 (★单一事实源★)】★**: ★**ISS-407 依赖图 `MECH/BOARD_ONEPASS_VERDICT_PREMISE_DEPENDENCY.md` §8 机器块 `dependency_graph` 里, `premises ∩ {PQ01, PQ02} ≠ ∅` 的边 = `E01`~`E09` ⇒ 这 9 条边的 `numbers` / `gates` / `conclusions` 三个并集 = 本页每档的三张清单 (★机器现算, 不许手抄★)** ★

★**【清单内容 (★四档完全相同 —— 因为【前提量一动, 依赖图上挂着的就全都过期】, 与动多少无关★)】★**:

| 清单 | 条目 | 条数 |
|---|---|---|
| ★**必须重算的数** ★ | ★`j_debug_copper_x` · `j_uart_copper_x` · `j_debug_required_clear_x` · `j_uart_required_clear_x` · `j_uart_cover_margin_x` · `j_debug_opening_margin_x` · `j_debug_cover_margin_y` (★判决链 7 个数, 一条都不例外★) ★+ `annular_ring` · `seven_numbers_matrix` · `pad_tier` (★档位自身的三格★) ★ | ★**10** ★ |
| ★**必须重跑的闸** ★ | ★`MECH/check_debug_seat_3d_fit.py` · `MECH/check_debug_seat_rework_spec.py` · `MECH/check_fts_seat_body_geometry.py` · `MECH/check_fts_vs_generic_courtyard_delta.py` · `MECH/check_fts_seat_sample_plan.py` · `MECH/check_jdebug_1p27_clearance.py` · `MECH/check_juart_1p27_clearance.py` · `MECH/check_connector_clearance_caliber.py` · `MECH/check_pad_size_coupling_closed.py` ★ | ★**9** ★ |
| ★**必须重签的结论/页** ★ | ★`MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md` · `MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` · `MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md` · `MECH/BOARD_ONEPASS_FTS_VS_GENERIC_COURTYARD_DELTA.md` · `MECH/BOARD_ONEPASS_FTS_SEAT_SAMPLE_MEASURE_PLAN.md` · `MECH/BOARD_ONEPASS_PAD_SIZE_COUPLING.md` · `HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md` ★ | ★**7** ★ |

★**★【四档逐档的「触发理由 + 本档新增的额外后果」★**:

| 档位 | pad | 环宽 | ★触发理由 (为什么必须离开现状档)★ | ★本档的 MECH 侧后果 (7 个数)★ | ★结构件侧代价 (量级·不代估金额)★ |
|---|---|---|---|---|---|
| ★`P1000`★ | `1.000` | `0.1450` | ★**现状口径档·前提已死** ★ (环宽 `0.1450` < 多层 1oz 绝对下限 `0.15` ⇒ 物理上不成立 ⇒ 【必须离开】) ★ | 7 个数全部要重算 (换到任何一档都变) | ★**这一档【不可能是最终答案】⇒ 「不改」这个选项本身就不存在** ★ |
| `P1010` | `1.010` | `0.1500` | 恰达多层 1oz 绝对下限 `0.15` | 铜箔X ±`0.0100` · 罩住X `0.1350→0.1300` · 罩住Y `0.7700→0.7650` ⇒ 改动最小 | 最小 (结构件重算量最小) ★⚠ 若板厂按 2 层做 ⇒ 本档不成立 ⇒ 需 `pad ≥ 1.070` ★ |
| `P1110` | `1.110` | `0.2000` | 达多层 1oz 推荐值 `0.20` | 铜箔X `4.8100→4.9200` / `2.2700→2.3800` · 清空需求 `6.6100→6.7200` / `4.0700→4.1800` · `J_UART` 罩住X `0.1350→0.0800` (最坏 `-0.1650→-0.2200`) · `J_DEBUG` 罩住Y `0.7700→0.7150` (最坏 `0.4700→0.4150`) | 中 (结构件 + 镜脚侧整体重算一次·2-4 周 + ¥4-8K 级·沿用 ISS-387/391 已登记量级) ★ |
| `P1218` | `1.218` | `0.2540` | 达 2 oz 口径 `0.254` | 铜箔X `4.8100→5.0280` / `2.2700→2.4880` · 清空需求 `6.6100→6.8280` / `4.0700→4.2880` · `J_UART` 罩住X `0.1350→0.0260` (最坏 `-0.1650→-0.2740`) · `J_DEBUG` 罩住Y `0.7700→0.6610` (最坏 `0.4700→0.3610`) | 最大 (清空区 X 要多让 ~1.02/边·镜脚侧重算量最大·`J_UART` 罩住余量几乎归零 ⇒ 红得最狠) ★ |

★**★【★不代拍★】**: ★**本单【不选档】。机器块 `decision_taken_here` = `"not_decided_here"` (★闸 T6 会查★) ⇒ 选哪一档 = main 的地界 (★ISS-397 已写死「排期交 main 拍, 一条都不代拍」★)** ★

==============================================================================
## ★§5 · 盲闸登记 + 漂移检测 (★T4 的载体★) ★

★**★【登记来源 (★引用, 不重做 A/B 实测当新发现★)】★**: ★**ISS-403 交卷页 `MECH/BOARD_ONEPASS_PAD_SIZE_COUPLING.md` §4.2 的 A/B 实测表 (★A 臂 pad `1.110` vs B 臂 pad `1.000`·红项集合差集 = 空★) ⇒ 5 道盲 + 2 道敏感** ★
★**★【本单的复核 (★复核 + 留证, 不是重做 A/B★)】★**: ★**本机现跑这 7 道闸, 取 stdout+stderr 的 md5, 与 ISS-403 登记的 `baseline_stdout_md5` 逐道对拍 ⇒ 5 道盲闸【逐字相同】⇒ ISS-403 的盲/敏感分类至今成立** ★

| # | 闸 | ★敏感性★ | ★本机现跑 rc★ | ★本机现跑 stdout md5★ | ★与 ISS-403 登记基线★ | ★静态机制签名 (AST 实扫)★ |
|---|---|---|---|---|---|---|
| 1 | `MECH/check_debug_seat_3d_fit.py` | ★**盲** ★ | `0` | `a64fd53091c16f9538348ffa23a99a37` | ★**逐字相同** ★ | `BLIND(hardcoded-pad-value)` · lib-read 入口 `0` · P1000 字面量 `9` 处 |
| 2 | `MECH/check_debug_seat_rework_spec.py` | ★**盲** ★ | `0` | `b86c561098d8d52f9a873780e00a3ce3` | ★**逐字相同** ★ | `BLIND(hardcoded-pad-value)` · lib-read 入口 `0` · P1000 字面量 `4` 处 |
| 3 | `MECH/check_fts_seat_body_geometry.py` | ★**盲** ★ | `0` | `5d17b5e23afa509561cdcee7c527526b` | ★**逐字相同** ★ | `BLIND(no-lib-read)` · lib-read 入口 `0` · P1000 字面量 `0` 处 |
| 4 | `MECH/check_connector_clearance_caliber.py` | ★**盲** ★ | `1` (★既有 `K7` md5 漂移·与本单无关★) | `7ade27949541ba0d694088e812c8b6b5` | ★**逐字相同** ★ | `BLIND(hardcoded-pad-value)` · lib-read 入口 `0` · P1000 字面量 `1` 处 |
| 5 | `MECH/check_fts_vs_generic_courtyard_delta.py` | ★**盲** ★ | `0` | `7839434d7e69608953507a51946bb165` | ★**逐字相同** ★ | `BLIND(no-lib-read)` · lib-read 入口 `0` · P1000 字面量 `0` 处 |
| 6 | `MECH/check_jdebug_1p27_clearance.py` | ★**敏感** ★ | `0` | `3bbd512a94a61d89cf766fbb0375f313` | ★**ISS-403 未登记 stdout md5 ⇒ 本单首次登记** ★ | `SENSITIVE(lib-read)` · `.kicad_mod` 运行期引用 `12` · `LIBROOT` 引用 `7` |
| 7 | `MECH/check_juart_1p27_clearance.py` | ★**敏感** ★ | `0` | `bf3a434cd122c91bf4bcc9c98c964a20` | ★**ISS-403 未登记 stdout md5 ⇒ 本单首次登记** ★ | `SENSITIVE(lib-read)` · `.kicad_mod` 运行期引用 `14` · `LIBROOT` 引用 `15` |

★**★【漂移检测 (★T4 的机器实现·两条腿★)】★**:
★**① 行为腿**: ★**每次跑本闸都现跑这 7 道闸 ⇒ stdout md5 与登记基线对拍 ⇒ 任一道变了 ⇒ 【它对 pad 的敏感性可能已变】⇒ 判红 (★逼人重做 A/B★)** ★
★**② 静态腿**: ★**AST 实扫这 7 道闸的 `.kicad_mod` 运行期引用 + `LIBROOT` 引用 + P1000 档字面量 ⇒ 重算「盲 / 敏感」分类 ⇒ 与登记分类不符 ⇒ 【从盲变成不盲 或 从不盲变成盲】⇒ 判红** ★

★**★【★一条必须写死的口径★】★**: ★**ISS-403 的 A/B 实测【只覆盖 7 道】, 而 ISS-407 依赖图覆盖 9 道 (多出 `check_fts_seat_sample_plan.py` 与 `check_pad_size_coupling_closed.py` ⇒ 这 2 道【没做过 A/B】⇒ 它们的敏感性【至今未实测】⇒ 本单只登记「它们在依赖图上挂着 PQ01/PQ02」, 不谎称它们盲或不盲** ★ ★ `[实测]`

==============================================================================
## ★§6 · 判据 T1~T7 · 机器实现 (★载体 = `MECH/check_premise_tier_decision.py`★) ★

| ★判据★ | ★机器实现★ |
|---|---|
| ★**T1**★ 四来源一致性 | ★**实读** BOM (`csv.DictReader`) · 作业包 (全文) · 真相页机器块 (`json`) · 板面 footprint (只读解析) ⇒ 逐来源判「记没记 / 记的是哪一档」⇒ ★**四来源档位不一致, 或任何一来源没记 ⇒ 判红** ★ ⇒ 现状: BOM 没这一格 ⇒ 现状必红 ★ |
| ★**T2**★ 当前档位机器可判 | ★**从板面 footprint 实读 `J_DEBUG`/`J_UART` 的 THT 焊盘边长 ⇒ 判定落在四档哪一档 ⇒ 不在任何一档 ⇒ 判红** ★ ⇒ ★**不许从文档抄** ★ ⇒ 现状: 板面是 SMD 占位 ⇒ 判红 ★ |
| ★**T3**★ 换档清单完整 | ★**四档每一档的「重算的数 / 重跑的闸 / 重签的结论」三张清单 ⇒ 条数 ≥ N (10 / 9 / 7) 且每条都能在 ISS-407 依赖图的 `numbers` / `gates` / `conclusions` 并集里找到对应节点 ⇒ 少一条 ⇒ 判红** ★ ⇒ ★**不许只判「清单非空」** ★ |
| ★**T4**★ 盲闸登记 + 漂移 | ★**7 道判决链闸的 pad 敏感性登记在册 ⇒ 现跑 stdout md5 对拍 + AST 静态签名重算分类 ⇒ 任一处漂移 ⇒ 判红** ★ |
| ★**T5**★ fail-closed | ★**依赖图页 / 本页 / BOM 任一读不到 ⇒ 判红, 不许判绿** ★ |
| ★**T6**★ 零挂链 + 零外发 | ★**`grep -c check_premise_tier_decision state/gate_check.py` = 0 ⇒ `state/outbox/` 树摘要与基线逐字相同 ⇒ `decision_taken_here` = `not_decided_here`** ★ |
| ★**T7**★ 板指纹自证 | ★**跑完板 md5 / mtime / size 与基线 (`611b869e13518c3c023fb178f91a0075` / `2026-11-06 07:07:17.362193413` / `4940213`) 逐字相同 ⇒ 且本闸跑前跑后两次现读一致 ⇒ 判红** ★ |

★**★【两种跑法】★**: ★**① 裸跑 `python3 MECH/check_premise_tier_decision.py` ⇒ rc=1** (★红的是现状: T1 四来源不一致 + T2 板面无 THT 焊盘 + T6 板面档位未定★) · ★**② `--selftest` ⇒ rc=0 · 末行逐字 `ALL TESTS PASS`** (★正向 ≥1 + 反向 ≥8★) ★

==============================================================================
## ★§7 · 边界自证 (★逐条·★本机实跑★) ★

| 边界 | 自证方式 | 读数 |
|---|---|---|
| ★**零写板** ★ | `md5sum` + `stat` 三项 | ★`611b869e13518c3c023fb178f91a0075` / `2026-11-06 07:07:17.362193413` / `4940213` ⇒ 与基线**逐字节相同** ★ |
| ★**零落表** ★ | 网表 / 脚表 / BOM md5 | ★`6aee500e60ba0732f83a9cf557ba90ab` / `9174309df1ec9411ac8e8d9e80ee386a` / `5b9993992405904a60ac96a020b375d8` ⇒ 与基线逐字相同; ★`mech.yaml` 由本单单写 (★走 `state/frag_write.py`★) ★ |
| ★**零改既有闸判据** ★ | 4 道既有闸源码 md5 对拍 | ★`check_verdict_premise_dependency.py` / `check_mech_gate_hook_coverage.py` / `check_pad_size_coupling_closed.py` / `check_onepass_mech_release.py` ⇒ 开工前/收工后**逐字相同** ★ |
| ★**零改既有页正文** ★ | 4 张既有页 md5 对拍 | ★`BOARD_ONEPASS_PAD_SIZE_COUPLING.md` / `BOARD_ONEPASS_FTS_VS_GENERIC_COURTYARD_DELTA.md` / `BOARD_ONEPASS_VERDICT_PREMISE_DEPENDENCY.md` / `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` ⇒ **逐字相同** ★ |
| ★**零挂链** ★ | `grep -c check_premise_tier_decision state/gate_check.py` | ★**0** ★ |
| ★**零外发** ★ | `state/outbox/` 全树摘要 | ★22 个文件 · 树摘要 `7c5f45e922447340349a224cf05a9807` ⇒ 与基线**逐字节相同** ⇒ ★**本单没发任何邮件/询价/问询/采购** ★ |
| ★**不代拍** ★ | 机器块 `decision_taken_here` | ★`"not_decided_here"` ★ |
| ★**不自签** ★ | `state/issue_log.yaml` | ★**一行没写** (★ISS-410 的签收归 main★) ★ |
| ★**沙盒只落项目盘** ★ | 沙盒路径 | ★`tmp/iss410/` (★未向系统 `/tmp` 写任何字节★) ★ |

==============================================================================
## ★§8 · 未决项 (★一条都不代拍·★全部 to=main / HW 域交 hw-lead★) ★

| ID | 未决项 | 归属 |
|---|---|---|
| ★**OI-410-1**★ | ★焊盘前提量最终取哪一档 (`P1010` / `P1110` / `P1218`) ⇒ ★**本单不代拍** ★ | main |
| ★**OI-410-2**★ | ★BOM 的 `J_DEBUG`/`J_UART` 行要不要补「焊盘边长」这一格 (★HW 域⇒hw-lead·拍板归 main★) ★ | hw-lead + main |
| ★**OI-410-3**★ | ★作业包 L243 调试口开口段的认领句要不要把 pad 档写死进去 (★否则前提量一变那段数不会自己报警★) ★ | hw-lead + main |
| ★**OI-410-4**★ | ★现状真相页 (`FTS_VS_GENERIC`) 的【现状值型判据】要不要随拍档同批更新 (★它现在把 `1.000` 写死了★) ★ | main (落表) + mech-lead (重算) |
| ★**OI-410-5**★ | ★7 道 MECH 闸挂不挂 `state/gate_check.py` (★ISS-403 `OI-403-4` / ISS-405 同源★) ⇒ ★**不挂 ⇒ 「前提量改了会响」这件事永远没人看得见** ★ | main |
| ★**OI-410-6**★ | ★`check_fts_seat_sample_plan.py` 与 `check_pad_size_coupling_closed.py` 这 2 道 (★依赖图挂 PQ01/PQ02 但【没做过 A/B】★) 要不要补 A/B 实测 ★ | main |

==============================================================================
## ★§9 · 机器块 (★可被 `MECH/check_premise_tier_decision.py` 解析★) ★

```json
{
  "doc": "ISS-410 · 「板那一趟」排针焊盘前提量【四档选档 ⇒ 下游作废传播】决策表 · 机读块",
  "generated_by": "mech-lead · 2026-11-25 · 本机实读/实算 (零写板/零落表/零挂链/零外发)",
  "evidence_levels": [
    "官网",
    "实测",
    "媒体",
    "推算",
    "0数据"
  ],
  "premise_quantity": {
    "name": "排针焊盘边长 (THT 焊盘 X/Y 边长)",
    "unit": "mm",
    "is_future_state": true,
    "why": "★本单实读结论★: 现状板面上 J_DEBUG/J_UART 是自绘 SMD 占位 land (0.2750×0.9000 · pitch 0.50 · 无钻孔) ⇒ ★板面【今天根本没有】THT 排针焊盘 ⇒ 四档全部是【未来板面 (板那一趟)】的候选值, 不是【现状值】★",
    "tiers": [
      {
        "id": "P1000",
        "pad_mm": 1.0,
        "annular_ring_mm": 0.145,
        "meets": "none",
        "note": "现状口径档 (ISS-387/391 当时口径) · 环宽 0.1450 < 多层1oz绝对下限 0.15 ⇒ 前提已死"
      },
      {
        "id": "P1010",
        "pad_mm": 1.01,
        "annular_ring_mm": 0.15,
        "meets": "abs_min",
        "note": "恰达多层 1oz 绝对下限 0.15 · 未达推荐值 0.20"
      },
      {
        "id": "P1110",
        "pad_mm": 1.11,
        "annular_ring_mm": 0.2,
        "meets": "recommended",
        "note": "达多层 1oz 推荐值 0.20"
      },
      {
        "id": "P1218",
        "pad_mm": 1.218,
        "annular_ring_mm": 0.254,
        "meets": "2oz_min",
        "note": "达 2 oz 口径的 0.254"
      }
    ]
  },
  "formula_constants": {
    "span_debug_mm": 3.81,
    "span_uart_mm": 1.27,
    "crit_mm": 0.6,
    "tol_fdm_part_mm": 0.3,
    "clear_uart_x_mm": 2.54,
    "open_debug_x_mm": 10.2,
    "clear_debug_y_mm": 2.54,
    "planned_drill_mm": 0.71,
    "source": "★PQ05/PQ06 (KiCad 官方 .kicad_mod 实读) · PQ07/PQ08 (MECH/service_port_check.py L126-L127) · PQ09/PQ11/PQ12 (MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L346/L351/L352) · PQ04 (HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md §1.1 Samtec Ø0.71 TYP) ★"
  },
  "seven_number_defs": {
    "j_debug_copper_x": "span_debug_mm(3.8100) + pad",
    "j_uart_copper_x": "span_uart_mm(1.2700) + pad",
    "j_debug_required_clear_x": "j_debug_copper_x + 2*(CRIT+TOL) = j_debug_copper_x + 1.8000",
    "j_uart_required_clear_x": "j_uart_copper_x + 2*(CRIT+TOL) = j_uart_copper_x + 1.8000",
    "j_uart_cover_margin_x": "(clear_uart_x_mm(2.5400) - j_uart_copper_x)/2",
    "j_debug_opening_margin_x": "(open_debug_x_mm(10.2000) - j_debug_copper_x)/2",
    "j_debug_cover_margin_y": "(clear_debug_y_mm(2.5400) - pad)/2"
  },
  "seven_numbers_matrix": {
    "P1000": {
      "j_debug_copper_x": 4.81,
      "j_uart_copper_x": 2.27,
      "j_debug_required_clear_x": 6.61,
      "j_uart_required_clear_x": 4.07,
      "j_uart_cover_margin_x": 0.135,
      "j_debug_opening_margin_x": 2.695,
      "j_debug_cover_margin_y": 0.77,
      "annular_ring_mm": 0.145
    },
    "P1010": {
      "j_debug_copper_x": 4.82,
      "j_uart_copper_x": 2.28,
      "j_debug_required_clear_x": 6.62,
      "j_uart_required_clear_x": 4.08,
      "j_uart_cover_margin_x": 0.13,
      "j_debug_opening_margin_x": 2.69,
      "j_debug_cover_margin_y": 0.765,
      "annular_ring_mm": 0.15
    },
    "P1110": {
      "j_debug_copper_x": 4.92,
      "j_uart_copper_x": 2.38,
      "j_debug_required_clear_x": 6.72,
      "j_uart_required_clear_x": 4.18,
      "j_uart_cover_margin_x": 0.08,
      "j_debug_opening_margin_x": 2.64,
      "j_debug_cover_margin_y": 0.715,
      "annular_ring_mm": 0.2
    },
    "P1218": {
      "j_debug_copper_x": 5.028,
      "j_uart_copper_x": 2.488,
      "j_debug_required_clear_x": 6.828,
      "j_uart_required_clear_x": 4.288,
      "j_uart_cover_margin_x": 0.026,
      "j_debug_opening_margin_x": 2.586,
      "j_debug_cover_margin_y": 0.661,
      "annular_ring_mm": 0.254
    }
  },
  "iss403_matrix_crosscheck": {
    "source": "MECH/BOARD_ONEPASS_PAD_SIZE_COUPLING.md §7 机器块 seven_numbers_matrix (ISS-403 登记值)",
    "recompute_rule": "★按本块 seven_number_defs 的公式【本机实算】⇒ 与 ISS-403 登记值逐格对拍 ⇒ 28 格全同才算抄对 ★",
    "cells": {
      "P1000": {
        "j_debug_copper_x": {
          "recomputed": 4.81,
          "iss403_registered": 4.81,
          "match": true
        },
        "j_uart_copper_x": {
          "recomputed": 2.27,
          "iss403_registered": 2.27,
          "match": true
        },
        "j_debug_required_clear_x": {
          "recomputed": 6.61,
          "iss403_registered": 6.61,
          "match": true
        },
        "j_uart_required_clear_x": {
          "recomputed": 4.07,
          "iss403_registered": 4.07,
          "match": true
        },
        "j_uart_cover_margin_x": {
          "recomputed": 0.135,
          "iss403_registered": 0.135,
          "match": true
        },
        "j_debug_opening_margin_x": {
          "recomputed": 2.695,
          "iss403_registered": 2.695,
          "match": true
        },
        "j_debug_cover_margin_y": {
          "recomputed": 0.77,
          "iss403_registered": 0.77,
          "match": true
        }
      },
      "P1010": {
        "j_debug_copper_x": {
          "recomputed": 4.82,
          "iss403_registered": 4.82,
          "match": true
        },
        "j_uart_copper_x": {
          "recomputed": 2.28,
          "iss403_registered": 2.28,
          "match": true
        },
        "j_debug_required_clear_x": {
          "recomputed": 6.62,
          "iss403_registered": 6.62,
          "match": true
        },
        "j_uart_required_clear_x": {
          "recomputed": 4.08,
          "iss403_registered": 4.08,
          "match": true
        },
        "j_uart_cover_margin_x": {
          "recomputed": 0.13,
          "iss403_registered": 0.13,
          "match": true
        },
        "j_debug_opening_margin_x": {
          "recomputed": 2.69,
          "iss403_registered": 2.69,
          "match": true
        },
        "j_debug_cover_margin_y": {
          "recomputed": 0.765,
          "iss403_registered": 0.765,
          "match": true
        }
      },
      "P1110": {
        "j_debug_copper_x": {
          "recomputed": 4.92,
          "iss403_registered": 4.92,
          "match": true
        },
        "j_uart_copper_x": {
          "recomputed": 2.38,
          "iss403_registered": 2.38,
          "match": true
        },
        "j_debug_required_clear_x": {
          "recomputed": 6.72,
          "iss403_registered": 6.72,
          "match": true
        },
        "j_uart_required_clear_x": {
          "recomputed": 4.18,
          "iss403_registered": 4.18,
          "match": true
        },
        "j_uart_cover_margin_x": {
          "recomputed": 0.08,
          "iss403_registered": 0.08,
          "match": true
        },
        "j_debug_opening_margin_x": {
          "recomputed": 2.64,
          "iss403_registered": 2.64,
          "match": true
        },
        "j_debug_cover_margin_y": {
          "recomputed": 0.715,
          "iss403_registered": 0.715,
          "match": true
        }
      },
      "P1218": {
        "j_debug_copper_x": {
          "recomputed": 5.028,
          "iss403_registered": 5.028,
          "match": true
        },
        "j_uart_copper_x": {
          "recomputed": 2.488,
          "iss403_registered": 2.488,
          "match": true
        },
        "j_debug_required_clear_x": {
          "recomputed": 6.828,
          "iss403_registered": 6.828,
          "match": true
        },
        "j_uart_required_clear_x": {
          "recomputed": 4.288,
          "iss403_registered": 4.288,
          "match": true
        },
        "j_uart_cover_margin_x": {
          "recomputed": 0.026,
          "iss403_registered": 0.026,
          "match": true
        },
        "j_debug_opening_margin_x": {
          "recomputed": 2.586,
          "iss403_registered": 2.586,
          "match": true
        },
        "j_debug_cover_margin_y": {
          "recomputed": 0.661,
          "iss403_registered": 0.661,
          "match": true
        }
      }
    },
    "all_28_match": true
  },
  "verdict_per_tier": {
    "P1000": {
      "j_uart_cover_margin_x": 0.135,
      "j_uart_cover_margin_x_worst": -0.165,
      "j_uart_cover_margin_x_verdict": "红",
      "j_debug_cover_margin_y": 0.77,
      "j_debug_cover_margin_y_worst": 0.47,
      "j_debug_cover_margin_y_verdict": "红",
      "j_debug_opening_margin_x": 2.695,
      "j_debug_opening_margin_x_worst": 2.395,
      "j_debug_opening_margin_x_verdict": "绿"
    },
    "P1010": {
      "j_uart_cover_margin_x": 0.13,
      "j_uart_cover_margin_x_worst": -0.17,
      "j_uart_cover_margin_x_verdict": "红",
      "j_debug_cover_margin_y": 0.765,
      "j_debug_cover_margin_y_worst": 0.465,
      "j_debug_cover_margin_y_verdict": "红",
      "j_debug_opening_margin_x": 2.69,
      "j_debug_opening_margin_x_worst": 2.39,
      "j_debug_opening_margin_x_verdict": "绿"
    },
    "P1110": {
      "j_uart_cover_margin_x": 0.08,
      "j_uart_cover_margin_x_worst": -0.22,
      "j_uart_cover_margin_x_verdict": "红",
      "j_debug_cover_margin_y": 0.715,
      "j_debug_cover_margin_y_worst": 0.415,
      "j_debug_cover_margin_y_verdict": "红",
      "j_debug_opening_margin_x": 2.64,
      "j_debug_opening_margin_x_worst": 2.34,
      "j_debug_opening_margin_x_verdict": "绿"
    },
    "P1218": {
      "j_uart_cover_margin_x": 0.026,
      "j_uart_cover_margin_x_worst": -0.274,
      "j_uart_cover_margin_x_verdict": "红",
      "j_debug_cover_margin_y": 0.661,
      "j_debug_cover_margin_y_worst": 0.361,
      "j_debug_cover_margin_y_verdict": "红",
      "j_debug_opening_margin_x": 2.586,
      "j_debug_opening_margin_x_worst": 2.286,
      "j_debug_opening_margin_x_verdict": "绿"
    }
  },
  "board_face_reference": {
    "path": "HW/PCB/demo_mainboard.kicad_pcb",
    "read_method": "★只读解析 (逐 footprint 括号配平) ⇒ 取 J_DEBUG/J_UART 的 pad size / type / drill / pitch / 铜箔包络 ★",
    "land": {
      "J_DEBUG": {
        "pad_count": 4,
        "pad_types": [
          "smd"
        ],
        "pad_size_mm": [
          0.275,
          0.9
        ],
        "has_drill": false,
        "tht_pad_count": 0,
        "pitch_x_mm": 0.5,
        "copper_x_mm": 1.775,
        "copper_y_mm": 0.9,
        "lib_id_empty": true
      },
      "J_UART": {
        "pad_count": 2,
        "pad_types": [
          "smd"
        ],
        "pad_size_mm": [
          0.275,
          0.9
        ],
        "has_drill": false,
        "tht_pad_count": 0,
        "pitch_x_mm": 0.5,
        "copper_x_mm": 0.775,
        "copper_y_mm": 0.9,
        "lib_id_empty": true
      }
    },
    "tht_pad_tier": null,
    "finding": "板面 J_DEBUG 现在是自绘 SMD 占位 land (焊盘 0.2750×0.9000, pitch 0.50, 无钻孔) ⇒ 板面【没有】THT 排针焊盘 ⇒ 四档哪一档都不是",
    "note": "★与 ISS-403 的口径差异★: ISS-403 §7 机器块 `current_pad` 记的是 KiCad 官方库 `.kicad_mod` 的 (size 1 1) (★那是【板那一趟】要落的 THT 封装★) ⇒ ★板面实读 (SMD 占位) 与 库件实读 (THT 1.000) 是两个不同的东西 ⇒ 本单把【板面实读】单列为四来源之一 ★"
  },
  "sources": [
    {
      "id": "SRC_BOM",
      "path": "HW/BOM_v1.csv",
      "machine_read": "★csv.DictReader ⇒ 取 ref ∈ {J_DEBUG,J_UART} 两行 ⇒ 全行文本里搜「≥3 位小数且值 ∈ 四档」的 token ★",
      "records_pad_tier": false,
      "recorded_tier": null,
      "hits": {},
      "finding": "★BOM 这一格【压根没有 pad 尺寸】★ (ref=J_DEBUG value='1×4 1.27mm 排针 (JTAG)' · footprint/opn/tolerance/alt_part 全空或『待定』) ⇒ 记的是【间距 1.27】不是【焊盘边长】",
      "evidence": "实测"
    },
    {
      "id": "SRC_WORKPACKET",
      "path": "HW/PCB/BOARD_ONEPASS_WORKPACKET.md",
      "machine_read": "★全文搜「≥3 位小数且值 ∈ 四档」的 token ★",
      "records_pad_tier": false,
      "recorded_tier": null,
      "hits": {},
      "finding": "★作业包【没有写死 pad 档】★ (L243 调试口开口段的 OPEN_X 10.200 / 罩住清空区 X 142.0625..143.8375 / 单边净距 X 4.2125 都是按现状算出来的, 但那一段没写 pad 档) ⇒ 前提量一变, 那段数【不会自己报警】",
      "evidence": "实测"
    },
    {
      "id": "SRC_TRUTH_PAGE",
      "path": "MECH/BOARD_ONEPASS_FTS_VS_GENERIC_COURTYARD_DELTA.md",
      "machine_read": "★取该页最后一个 JSON 机器块 ⇒ json.dumps 全文 ⇒ 搜「≥3 位小数且值 ∈ 四档」的 token ★",
      "records_pad_tier": true,
      "recorded_tier": "P1000",
      "hits": {
        "P1000": [
          "1.000",
          "1.000",
          "1.000",
          "1.000"
        ]
      },
      "finding": "★真相页把 1.000 写进了【现状值型判据】★ (machine block dimensions.copper_env_x_4pos.note 逐字『焊盘 1.000x1.000 @1.27 跨距 3.81』· copper_env_y=1.0000 · required_clearance_y_copper note 逐字『只吃铜箔 1.0000 + 2 x 0.9000』) ⇒ 记的是 P1000",
      "evidence": "实测"
    },
    {
      "id": "SRC_BOARD_FACE",
      "path": "HW/PCB/demo_mainboard.kicad_pcb",
      "machine_read": "★只读解析 footprint ⇒ J_DEBUG/J_UART 的 THT pad size ⇒ 落在四档哪一档 ★",
      "records_pad_tier": false,
      "recorded_tier": null,
      "hits": {},
      "finding": "板面 J_DEBUG 现在是自绘 SMD 占位 land (焊盘 0.2750×0.9000, pitch 0.50, 无钻孔) ⇒ 板面【没有】THT 排针焊盘 ⇒ 四档哪一档都不是",
      "evidence": "实测"
    }
  ],
  "tier_recompute_matrix": [
    {
      "tier": "P1000",
      "pad_mm": 1.0,
      "annular_ring_mm": 0.145,
      "recompute_numbers": [
        "j_debug_copper_x",
        "j_uart_copper_x",
        "j_debug_required_clear_x",
        "j_uart_required_clear_x",
        "j_uart_cover_margin_x",
        "j_debug_opening_margin_x",
        "j_debug_cover_margin_y",
        "annular_ring",
        "seven_numbers_matrix",
        "pad_tier"
      ],
      "rerun_gates": [
        "MECH/check_connector_clearance_caliber.py",
        "MECH/check_debug_seat_3d_fit.py",
        "MECH/check_debug_seat_rework_spec.py",
        "MECH/check_fts_seat_body_geometry.py",
        "MECH/check_fts_seat_sample_plan.py",
        "MECH/check_fts_vs_generic_courtyard_delta.py",
        "MECH/check_jdebug_1p27_clearance.py",
        "MECH/check_juart_1p27_clearance.py",
        "MECH/check_pad_size_coupling_closed.py"
      ],
      "resign_conclusions": [
        "HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md",
        "MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md",
        "MECH/BOARD_ONEPASS_FTS_SEAT_SAMPLE_MEASURE_PLAN.md",
        "MECH/BOARD_ONEPASS_FTS_VS_GENERIC_COURTYARD_DELTA.md",
        "MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md",
        "MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md",
        "MECH/BOARD_ONEPASS_PAD_SIZE_COUPLING.md"
      ],
      "driver": "★现状档·前提已死★ (环宽 0.1450 < 多层 1oz 绝对下限 0.15 ⇒ 必须离开这一档 ⇒ 7 个数全部要重算)",
      "dependency_edges": [
        "E01",
        "E02",
        "E03",
        "E04",
        "E05",
        "E06",
        "E07",
        "E08",
        "E09"
      ],
      "note": "★本清单的三个集合【全部由 ISS-407 依赖图里 premises ∩ {PQ01,PQ02} ≠ ∅ 的边 (E01~E09) 现算导出★ ⇒ 少一条 ⇒ 判红"
    },
    {
      "tier": "P1010",
      "pad_mm": 1.01,
      "annular_ring_mm": 0.15,
      "recompute_numbers": [
        "j_debug_copper_x",
        "j_uart_copper_x",
        "j_debug_required_clear_x",
        "j_uart_required_clear_x",
        "j_uart_cover_margin_x",
        "j_debug_opening_margin_x",
        "j_debug_cover_margin_y",
        "annular_ring",
        "seven_numbers_matrix",
        "pad_tier"
      ],
      "rerun_gates": [
        "MECH/check_connector_clearance_caliber.py",
        "MECH/check_debug_seat_3d_fit.py",
        "MECH/check_debug_seat_rework_spec.py",
        "MECH/check_fts_seat_body_geometry.py",
        "MECH/check_fts_seat_sample_plan.py",
        "MECH/check_fts_vs_generic_courtyard_delta.py",
        "MECH/check_jdebug_1p27_clearance.py",
        "MECH/check_juart_1p27_clearance.py",
        "MECH/check_pad_size_coupling_closed.py"
      ],
      "resign_conclusions": [
        "HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md",
        "MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md",
        "MECH/BOARD_ONEPASS_FTS_SEAT_SAMPLE_MEASURE_PLAN.md",
        "MECH/BOARD_ONEPASS_FTS_VS_GENERIC_COURTYARD_DELTA.md",
        "MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md",
        "MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md",
        "MECH/BOARD_ONEPASS_PAD_SIZE_COUPLING.md"
      ],
      "driver": "★最小改动档★ (7 个数变动最小: 铜箔X ±0.0100 · 罩住X/Y ±0.0050)",
      "dependency_edges": [
        "E01",
        "E02",
        "E03",
        "E04",
        "E05",
        "E06",
        "E07",
        "E08",
        "E09"
      ],
      "note": "★本清单的三个集合【全部由 ISS-407 依赖图里 premises ∩ {PQ01,PQ02} ≠ ∅ 的边 (E01~E09) 现算导出★ ⇒ 少一条 ⇒ 判红"
    },
    {
      "tier": "P1110",
      "pad_mm": 1.11,
      "annular_ring_mm": 0.2,
      "recompute_numbers": [
        "j_debug_copper_x",
        "j_uart_copper_x",
        "j_debug_required_clear_x",
        "j_uart_required_clear_x",
        "j_uart_cover_margin_x",
        "j_debug_opening_margin_x",
        "j_debug_cover_margin_y",
        "annular_ring",
        "seven_numbers_matrix",
        "pad_tier"
      ],
      "rerun_gates": [
        "MECH/check_connector_clearance_caliber.py",
        "MECH/check_debug_seat_3d_fit.py",
        "MECH/check_debug_seat_rework_spec.py",
        "MECH/check_fts_seat_body_geometry.py",
        "MECH/check_fts_seat_sample_plan.py",
        "MECH/check_fts_vs_generic_courtyard_delta.py",
        "MECH/check_jdebug_1p27_clearance.py",
        "MECH/check_juart_1p27_clearance.py",
        "MECH/check_pad_size_coupling_closed.py"
      ],
      "resign_conclusions": [
        "HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md",
        "MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md",
        "MECH/BOARD_ONEPASS_FTS_SEAT_SAMPLE_MEASURE_PLAN.md",
        "MECH/BOARD_ONEPASS_FTS_VS_GENERIC_COURTYARD_DELTA.md",
        "MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md",
        "MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md",
        "MECH/BOARD_ONEPASS_PAD_SIZE_COUPLING.md"
      ],
      "driver": "★推荐值档★ (达多层 1oz 推荐 0.20 ⇒ 板厂退单风险最低)",
      "dependency_edges": [
        "E01",
        "E02",
        "E03",
        "E04",
        "E05",
        "E06",
        "E07",
        "E08",
        "E09"
      ],
      "note": "★本清单的三个集合【全部由 ISS-407 依赖图里 premises ∩ {PQ01,PQ02} ≠ ∅ 的边 (E01~E09) 现算导出★ ⇒ 少一条 ⇒ 判红"
    },
    {
      "tier": "P1218",
      "pad_mm": 1.218,
      "annular_ring_mm": 0.254,
      "recompute_numbers": [
        "j_debug_copper_x",
        "j_uart_copper_x",
        "j_debug_required_clear_x",
        "j_uart_required_clear_x",
        "j_uart_cover_margin_x",
        "j_debug_opening_margin_x",
        "j_debug_cover_margin_y",
        "annular_ring",
        "seven_numbers_matrix",
        "pad_tier"
      ],
      "rerun_gates": [
        "MECH/check_connector_clearance_caliber.py",
        "MECH/check_debug_seat_3d_fit.py",
        "MECH/check_debug_seat_rework_spec.py",
        "MECH/check_fts_seat_body_geometry.py",
        "MECH/check_fts_seat_sample_plan.py",
        "MECH/check_fts_vs_generic_courtyard_delta.py",
        "MECH/check_jdebug_1p27_clearance.py",
        "MECH/check_juart_1p27_clearance.py",
        "MECH/check_pad_size_coupling_closed.py"
      ],
      "resign_conclusions": [
        "HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md",
        "MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md",
        "MECH/BOARD_ONEPASS_FTS_SEAT_SAMPLE_MEASURE_PLAN.md",
        "MECH/BOARD_ONEPASS_FTS_VS_GENERIC_COURTYARD_DELTA.md",
        "MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md",
        "MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md",
        "MECH/BOARD_ONEPASS_PAD_SIZE_COUPLING.md"
      ],
      "driver": "★2oz 口径档★ (达 0.254 ⇒ 罩住余量几乎归零 ⇒ 红得最狠 · 结构件重算量最大)",
      "dependency_edges": [
        "E01",
        "E02",
        "E03",
        "E04",
        "E05",
        "E06",
        "E07",
        "E08",
        "E09"
      ],
      "note": "★本清单的三个集合【全部由 ISS-407 依赖图里 premises ∩ {PQ01,PQ02} ≠ ∅ 的边 (E01~E09) 现算导出★ ⇒ 少一条 ⇒ 判红"
    }
  ],
  "dependency_graph_ref": {
    "page": "MECH/BOARD_ONEPASS_VERDICT_PREMISE_DEPENDENCY.md",
    "edges_for_pad": [
      "E01",
      "E02",
      "E03",
      "E04",
      "E05",
      "E06",
      "E07",
      "E08",
      "E09"
    ],
    "numbers_union": [
      "annular_ring",
      "annular_ring_mm",
      "connector_clearance_caliber",
      "copper_w_along",
      "courtyard_delta_18",
      "j_debug_copper_x",
      "j_debug_cover_margin_y",
      "j_debug_opening_margin_x",
      "j_debug_required_clear_x",
      "j_uart_copper_x",
      "j_uart_cover_margin_x",
      "j_uart_required_clear_x",
      "pad_tier",
      "per_edge_mm",
      "seat_3q_sample",
      "seat_clearance_x",
      "seat_interference",
      "seven_numbers_matrix"
    ],
    "gates_union": [
      "MECH/check_connector_clearance_caliber.py",
      "MECH/check_debug_seat_3d_fit.py",
      "MECH/check_debug_seat_rework_spec.py",
      "MECH/check_fts_seat_body_geometry.py",
      "MECH/check_fts_seat_sample_plan.py",
      "MECH/check_fts_vs_generic_courtyard_delta.py",
      "MECH/check_jdebug_1p27_clearance.py",
      "MECH/check_juart_1p27_clearance.py",
      "MECH/check_pad_size_coupling_closed.py"
    ],
    "conclusions_union": [
      "HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md",
      "MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md",
      "MECH/BOARD_ONEPASS_FTS_SEAT_SAMPLE_MEASURE_PLAN.md",
      "MECH/BOARD_ONEPASS_FTS_VS_GENERIC_COURTYARD_DELTA.md",
      "MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md",
      "MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md",
      "MECH/BOARD_ONEPASS_PAD_SIZE_COUPLING.md"
    ],
    "core_seven_numbers": [
      "j_debug_copper_x",
      "j_uart_copper_x",
      "j_debug_required_clear_x",
      "j_uart_required_clear_x",
      "j_uart_cover_margin_x",
      "j_debug_opening_margin_x",
      "j_debug_cover_margin_y"
    ]
  },
  "blind_gate_registry": [
    {
      "gate": "MECH/check_debug_seat_3d_fit.py",
      "sensitivity": "BLIND",
      "iss403_baseline_rc": 0,
      "iss403_baseline_stdout_md5": "a64fd53091c16f9538348ffa23a99a37",
      "rerun_rc": 0,
      "rerun_stdout_md5": "a64fd53091c16f9538348ffa23a99a37",
      "stdout_md5_matches_iss403": true,
      "lib_signature": {
        "kicad_mod_runtime_refs": 2,
        "libroot_refs": 0,
        "p1000_literal_refs": 9,
        "class": "BLIND(hardcoded-pad-value)"
      },
      "blind_mechanism": "official 表把铜箔宽写死成 pad=1.000 的产物",
      "iss403_blind_lines": [
        "L683",
        "L686",
        "L491",
        "L746",
        "L753"
      ]
    },
    {
      "gate": "MECH/check_debug_seat_rework_spec.py",
      "sensitivity": "BLIND",
      "iss403_baseline_rc": 0,
      "iss403_baseline_stdout_md5": "b86c561098d8d52f9a873780e00a3ce3",
      "rerun_rc": 0,
      "rerun_stdout_md5": "b86c561098d8d52f9a873780e00a3ce3",
      "stdout_md5_matches_iss403": true,
      "lib_signature": {
        "kicad_mod_runtime_refs": 0,
        "libroot_refs": 0,
        "p1000_literal_refs": 4,
        "class": "BLIND(hardcoded-pad-value)"
      },
      "blind_mechanism": "OFFICIAL_DEBUG_COPPER_X / OFFICIAL_COPPER_Y 模块级常量写死",
      "iss403_blind_lines": [
        "L120",
        "L122",
        "L579"
      ]
    },
    {
      "gate": "MECH/check_fts_seat_body_geometry.py",
      "sensitivity": "BLIND",
      "iss403_baseline_rc": 0,
      "iss403_baseline_stdout_md5": "5d17b5e23afa509561cdcee7c527526b",
      "rerun_rc": 0,
      "rerun_stdout_md5": "5d17b5e23afa509561cdcee7c527526b",
      "stdout_md5_matches_iss403": true,
      "lib_signature": {
        "kicad_mod_runtime_refs": 0,
        "libroot_refs": 0,
        "p1000_literal_refs": 0,
        "class": "BLIND(no-lib-read)"
      },
      "blind_mechanism": "全文件无任何 .kicad_mod / LIBROOT 读入口",
      "iss403_blind_lines": []
    },
    {
      "gate": "MECH/check_connector_clearance_caliber.py",
      "sensitivity": "BLIND",
      "iss403_baseline_rc": 1,
      "iss403_baseline_stdout_md5": "7ade27949541ba0d694088e812c8b6b5",
      "rerun_rc": 1,
      "rerun_stdout_md5": "7ade27949541ba0d694088e812c8b6b5",
      "stdout_md5_matches_iss403": true,
      "lib_signature": {
        "kicad_mod_runtime_refs": 0,
        "libroot_refs": 0,
        "p1000_literal_refs": 1,
        "class": "BLIND(hardcoded-pad-value)"
      },
      "blind_mechanism": "全文件无任何 .kicad_mod / LIBROOT 读入口",
      "iss403_blind_lines": []
    },
    {
      "gate": "MECH/check_fts_vs_generic_courtyard_delta.py",
      "sensitivity": "BLIND",
      "iss403_baseline_rc": 0,
      "iss403_baseline_stdout_md5": "7839434d7e69608953507a51946bb165",
      "rerun_rc": 0,
      "rerun_stdout_md5": "7839434d7e69608953507a51946bb165",
      "stdout_md5_matches_iss403": true,
      "lib_signature": {
        "kicad_mod_runtime_refs": 0,
        "libroot_refs": 0,
        "p1000_literal_refs": 0,
        "class": "BLIND(no-lib-read)"
      },
      "blind_mechanism": "全文件无任何 .kicad_mod / LIBROOT 读入口",
      "iss403_blind_lines": []
    },
    {
      "gate": "MECH/check_jdebug_1p27_clearance.py",
      "sensitivity": "SENSITIVE",
      "iss403_baseline_rc": 0,
      "iss403_baseline_stdout_md5": "",
      "rerun_rc": 0,
      "rerun_stdout_md5": "3bbd512a94a61d89cf766fbb0375f313",
      "stdout_md5_matches_iss403": null,
      "lib_signature": {
        "kicad_mod_runtime_refs": 12,
        "libroot_refs": 7,
        "p1000_literal_refs": 0,
        "class": "SENSITIVE(lib-read)"
      },
      "sensitive_mechanism": "LIBROOT 现读 .kicad_mod ⇒ copper_w_along = span + pad_along",
      "pad_1p110_red": [
        "G1",
        "G2",
        "G3",
        "G4"
      ]
    },
    {
      "gate": "MECH/check_juart_1p27_clearance.py",
      "sensitivity": "SENSITIVE",
      "iss403_baseline_rc": 0,
      "iss403_baseline_stdout_md5": "",
      "rerun_rc": 0,
      "rerun_stdout_md5": "bf3a434cd122c91bf4bcc9c98c964a20",
      "stdout_md5_matches_iss403": null,
      "lib_signature": {
        "kicad_mod_runtime_refs": 14,
        "libroot_refs": 15,
        "p1000_literal_refs": 0,
        "class": "SENSITIVE(lib-read)"
      },
      "sensitive_mechanism": "LIBROOT / --libroot 现读 .kicad_mod",
      "pad_1p110_red": [
        "J0",
        "J1",
        "J5",
        "J7"
      ]
    }
  ],
  "fab_capability": {
    "question": "★本单自己查的结果 (不外发 · 不挂成外部依赖)★",
    "primary_source": "JLCPCB 官方 PCB 能力页 https://jlcpcb.com/capabilities/pcb-capabilities",
    "primary_evidence": "官网",
    "primary_quote_verbatim": "PTH annular ring ≧0.20mm 2-layer: 1 oz: Recommended 0.25 mm or above; absolute minimum 0.18 mm 2 oz: 0.254 mm or above Multilayer: 1 oz: Recommended 0.20 mm or above; absolute minimum 0.15 mm 2 oz: 0.254 mm or above",
    "primary_live_fetch": {
      "url": "https://jlcpcb.com/capabilities/pcb-capabilities",
      "saved_to": "tmp/iss410/jlcpcb_pcb_capabilities_live.html",
      "md5": "351f5f897ea1236c30d4ad2409e84311",
      "bytes": 140276,
      "note": "★本单本机 curl 现取 · 与 ISS-403 留存的 tmp/cron775d_r90/jlcpcb_pcb_capabilities_20261124_2043.html (md5 24dd86f068aa85728b74706f2fd80b3e) 逐字对照 ⇒ 环宽四行一致 ★"
    },
    "secondary_source": "PCB.cn 官方能力页 https://pcbcn.com/capabilities",
    "secondary_evidence": "官网",
    "secondary_quote_verbatim": "Min Width of Annular Ring | 0.15mm / 6mil",
    "applicable_row": "Multilayer: 1 oz",
    "applicable_row_reason": "★本板 = 8 层 (板文件 layers 段 F.Cu + In1..In6.Cu + B.Cu 共 8 个 *.Cu signal 层) · 外层铜 1 oz (HW/PCB/FAB_ORDER_NOTES.md §叠层表)★",
    "recommended_mm": 0.2,
    "absolute_min_mm": 0.15,
    "two_layer_1oz_absolute_min_mm": 0.18,
    "board_layer_count": 8,
    "board_outer_copper_oz": 1,
    "tier_meets_matrix": {
      "P1000": {
        "annular_ring_mm": 0.145,
        "multilayer_1oz_abs_min_0p15": false,
        "multilayer_1oz_rec_0p20": false,
        "two_layer_1oz_abs_min_0p18": false,
        "two_layer_1oz_rec_0p25": false
      },
      "P1010": {
        "annular_ring_mm": 0.15,
        "multilayer_1oz_abs_min_0p15": true,
        "multilayer_1oz_rec_0p20": false,
        "two_layer_1oz_abs_min_0p18": false,
        "two_layer_1oz_rec_0p25": false
      },
      "P1110": {
        "annular_ring_mm": 0.2,
        "multilayer_1oz_abs_min_0p15": true,
        "multilayer_1oz_rec_0p20": true,
        "two_layer_1oz_abs_min_0p18": true,
        "two_layer_1oz_rec_0p25": false
      },
      "P1218": {
        "annular_ring_mm": 0.254,
        "multilayer_1oz_abs_min_0p15": true,
        "multilayer_1oz_rec_0p20": true,
        "two_layer_1oz_abs_min_0p18": true,
        "two_layer_1oz_rec_0p25": true
      }
    },
    "degradation_plan": {
      "problem": "★「板厂是谁」这一格至今 [0数据] (HW/PCB/FAB_ORDER_NOTES.md 全文只写『板厂』从未指名)★",
      "rule": "★降级口径 = 【适用行由本板自己的叠层规格决定, 不由板厂名字决定】★ ⇒ 叠层 8 层 + 外层 1 oz 是【我们的规格】⇒ 适用行 = Multilayer: 1 oz ⇒ 下限 0.15 / 推荐 0.20 ⇒ 板厂名字【不参与】选档 ✓",
      "safest_tier_without_external_confirm": "P1218",
      "safest_tier_reason": "★P1218 的环宽 0.2540 同时 ≥ 0.15 (多层绝对下限) / ≥ 0.18 (2 层绝对下限) / ≥ 0.20 (多层推荐) / ≥ 0.25 (2 层推荐) ⇒ 四行全过 ⇒ 【不需要任何板厂回复就能确定可制造】★ ⇒ 代价 = MECH 侧重算量最大 + J_UART 罩住余量 0.0260 (最坏 -0.2740) 红得最狠",
      "no_external_dependency": "★本单【不外发任何询价/问询/采购】(老板 2026-11-11 19:31 + 2026-11-12 02:02) ⇒ 四档全列 + 每档达成口径 + 每档 MECH 侧后果 + 每档结构件代价 全部算好 ⇒ main 拍档时直接选一档, 不必回本单再算一遍, 也不必等板厂回信 ★"
    }
  },
  "baseline_files": {
    "board": "HW/PCB/demo_mainboard.kicad_pcb",
    "netlist": "HW/netlist_v1.csv",
    "pinlist": "HW/netlist_v1_pins.csv",
    "bom": "HW/BOM_v1.csv"
  },
  "table_baselines": {
    "board": "611b869e13518c3c023fb178f91a0075",
    "netlist": "6aee500e60ba0732f83a9cf557ba90ab",
    "pinlist": "9174309df1ec9411ac8e8d9e80ee386a",
    "bom": "5b9993992405904a60ac96a020b375d8"
  },
  "board_baseline": {
    "path": "HW/PCB/demo_mainboard.kicad_pcb",
    "md5": "611b869e13518c3c023fb178f91a0075",
    "size": 4940213,
    "mtime": "2026-11-06 07:07:17.362193413"
  },
  "outbox_baseline": {
    "tree_md5": "7c5f45e922447340349a224cf05a9807",
    "files": 22
  },
  "gate_criteria": {
    "T1": "四来源一致性 —— BOM / 作业包 / 真相页机器块 / 板面 footprint 逐来源实读 ⇒ 判「记没记这一格 + 记的是哪一档」⇒ 四来源档位不一致 或 任何一来源没记 ⇒ 判红",
    "T2": "当前档位机器可判 —— 从板面 footprint 实读 J_DEBUG/J_UART 的 THT 焊盘边长 ⇒ 落在四档哪一档; 不在任何一档 ⇒ 判红 (不许从文档抄)",
    "T3": "换档重算清单完整 —— 四档每一档的『必须重算的数 / 必须重跑的闸 / 必须重签的结论』三张清单 ⇒ 条数 ≥ N 且每条都能在 ISS-407 依赖图里找到对应节点 ⇒ 少一条判红",
    "T4": "盲闸登记 + 漂移检测 —— 7 道判决链闸的 pad 敏感性登记在册; 每跑一次现读 stdout md5 与登记基线对拍 + 静态 lib-read 签名复核 ⇒ 状态从『盲』变『不盲』或反过来 ⇒ 判红",
    "T5": "fail-closed —— 依赖图页 / 真相页 / BOM 任一读不到 ⇒ 判红, 不许判绿",
    "T6": "零挂链 + 零外发自证 —— grep -c 本闸名 state/gate_check.py = 0 且 state/outbox/ 树摘要与基线逐字相同",
    "T7": "板指纹自证 —— 跑完板 md5 / mtime / size 与基线逐字相同"
  },
  "open_items": {
    "OI-410-1": "焊盘前提量最终取哪一档 (P1010 / P1110 / P1218) ⇒ to=main (★本单不代拍★)",
    "OI-410-2": "BOM 的 J_DEBUG/J_UART 行要不要补『焊盘边长』这一格 (HW 域 ⇒ to=hw-lead, 拍板归 main) ★",
    "OI-410-3": "作业包 L243 调试口开口段要不要把 pad 档写死进认领句 ★",
    "OI-410-4": "现状真相页 (FTS_VS_GENERIC) 的现状值型判据要不要随拍档同批更新 ★",
    "OI-410-5": "7 道 MECH 闸挂不挂 state/gate_check.py ⇒ to=main (ISS-403 OI-403-4 / ISS-405 同源)"
  },
  "decision_taken_here": "not_decided_here"
}
```json 机器块 ⇒ json.dumps 全文 ⇒ 搜「≥3 位小数且值 ∈ 四档」的 token ★",
      "records_pad_tier": true,
      "recorded_tier": "P1000",
      "hits": {
        "P1000": [
          "1.000",
          "1.000",
          "1.000",
          "1.000"
        ]
      },
      "finding": "★真相页把 1.000 写进了【现状值型判据】★ (machine block dimensions.copper_env_x_4pos.note 逐字『焊盘 1.000x1.000 @1.27 跨距 3.81』· copper_env_y=1.0000 · required_clearance_y_copper note 逐字『只吃铜箔 1.0000 + 2 x 0.9000』) ⇒ 记的是 P1000",
      "evidence": "实测"
    },
    {
      "id": "SRC_BOARD_FACE",
      "path": "HW/PCB/demo_mainboard.kicad_pcb",
      "machine_read": "★只读解析 footprint ⇒ J_DEBUG/J_UART 的 THT pad size ⇒ 落在四档哪一档 ★",
      "records_pad_tier": false,
      "recorded_tier": null,
      "hits": {},
      "finding": "板面 J_DEBUG 现在是自绘 SMD 占位 land (焊盘 0.2750×0.9000, pitch 0.50, 无钻孔) ⇒ 板面【没有】THT 排针焊盘 ⇒ 四档哪一档都不是",
      "evidence": "实测"
    }
  ],
  "tier_recompute_matrix": [
    {
      "tier": "P1000",
      "pad_mm": 1.0,
      "annular_ring_mm": 0.145,
      "recompute_numbers": [
        "j_debug_copper_x",
        "j_uart_copper_x",
        "j_debug_required_clear_x",
        "j_uart_required_clear_x",
        "j_uart_cover_margin_x",
        "j_debug_opening_margin_x",
        "j_debug_cover_margin_y",
        "annular_ring",
        "seven_numbers_matrix",
        "pad_tier"
      ],
      "rerun_gates": [
        "MECH/check_connector_clearance_caliber.py",
        "MECH/check_debug_seat_3d_fit.py",
        "MECH/check_debug_seat_rework_spec.py",
        "MECH/check_fts_seat_body_geometry.py",
        "MECH/check_fts_seat_sample_plan.py",
        "MECH/check_fts_vs_generic_courtyard_delta.py",
        "MECH/check_jdebug_1p27_clearance.py",
        "MECH/check_juart_1p27_clearance.py",
        "MECH/check_pad_size_coupling_closed.py"
      ],
      "resign_conclusions": [
        "HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md",
        "MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md",
        "MECH/BOARD_ONEPASS_FTS_SEAT_SAMPLE_MEASURE_PLAN.md",
        "MECH/BOARD_ONEPASS_FTS_VS_GENERIC_COURTYARD_DELTA.md",
        "MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md",
        "MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md",
        "MECH/BOARD_ONEPASS_PAD_SIZE_COUPLING.md"
      ],
      "driver": "★现状档·前提已死★ (环宽 0.1450 < 多层 1oz 绝对下限 0.15 ⇒ 必须离开这一档 ⇒ 7 个数全部要重算)",
      "dependency_edges": [
        "E01",
        "E02",
        "E03",
        "E04",
        "E05",
        "E06",
        "E07",
        "E08",
        "E09"
      ],
      "note": "★本清单的三个集合【全部由 ISS-407 依赖图里 premises ∩ {PQ01,PQ02} ≠ ∅ 的边 (E01~E09) 现算导出★ ⇒ 少一条 ⇒ 判红"
    },
    {
      "tier": "P1010",
      "pad_mm": 1.01,
      "annular_ring_mm": 0.15,
      "recompute_numbers": [
        "j_debug_copper_x",
        "j_uart_copper_x",
        "j_debug_required_clear_x",
        "j_uart_required_clear_x",
        "j_uart_cover_margin_x",
        "j_debug_opening_margin_x",
        "j_debug_cover_margin_y",
        "annular_ring",
        "seven_numbers_matrix",
        "pad_tier"
      ],
      "rerun_gates": [
        "MECH/check_connector_clearance_caliber.py",
        "MECH/check_debug_seat_3d_fit.py",
        "MECH/check_debug_seat_rework_spec.py",
        "MECH/check_fts_seat_body_geometry.py",
        "MECH/check_fts_seat_sample_plan.py",
        "MECH/check_fts_vs_generic_courtyard_delta.py",
        "MECH/check_jdebug_1p27_clearance.py",
        "MECH/check_juart_1p27_clearance.py",
        "MECH/check_pad_size_coupling_closed.py"
      ],
      "resign_conclusions": [
        "HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md",
        "MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md",
        "MECH/BOARD_ONEPASS_FTS_SEAT_SAMPLE_MEASURE_PLAN.md",
        "MECH/BOARD_ONEPASS_FTS_VS_GENERIC_COURTYARD_DELTA.md",
        "MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md",
        "MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md",
        "MECH/BOARD_ONEPASS_PAD_SIZE_COUPLING.md"
      ],
      "driver": "★最小改动档★ (7 个数变动最小: 铜箔X ±0.0100 · 罩住X/Y ±0.0050)",
      "dependency_edges": [
        "E01",
        "E02",
        "E03",
        "E04",
        "E05",
        "E06",
        "E07",
        "E08",
        "E09"
      ],
      "note": "★本清单的三个集合【全部由 ISS-407 依赖图里 premises ∩ {PQ01,PQ02} ≠ ∅ 的边 (E01~E09) 现算导出★ ⇒ 少一条 ⇒ 判红"
    },
    {
      "tier": "P1110",
      "pad_mm": 1.11,
      "annular_ring_mm": 0.2,
      "recompute_numbers": [
        "j_debug_copper_x",
        "j_uart_copper_x",
        "j_debug_required_clear_x",
        "j_uart_required_clear_x",
        "j_uart_cover_margin_x",
        "j_debug_opening_margin_x",
        "j_debug_cover_margin_y",
        "annular_ring",
        "seven_numbers_matrix",
        "pad_tier"
      ],
      "rerun_gates": [
        "MECH/check_connector_clearance_caliber.py",
        "MECH/check_debug_seat_3d_fit.py",
        "MECH/check_debug_seat_rework_spec.py",
        "MECH/check_fts_seat_body_geometry.py",
        "MECH/check_fts_seat_sample_plan.py",
        "MECH/check_fts_vs_generic_courtyard_delta.py",
        "MECH/check_jdebug_1p27_clearance.py",
        "MECH/check_juart_1p27_clearance.py",
        "MECH/check_pad_size_coupling_closed.py"
      ],
      "resign_conclusions": [
        "HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md",
        "MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md",
        "MECH/BOARD_ONEPASS_FTS_SEAT_SAMPLE_MEASURE_PLAN.md",
        "MECH/BOARD_ONEPASS_FTS_VS_GENERIC_COURTYARD_DELTA.md",
        "MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md",
        "MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md",
        "MECH/BOARD_ONEPASS_PAD_SIZE_COUPLING.md"
      ],
      "driver": "★推荐值档★ (达多层 1oz 推荐 0.20 ⇒ 板厂退单风险最低)",
      "dependency_edges": [
        "E01",
        "E02",
        "E03",
        "E04",
        "E05",
        "E06",
        "E07",
        "E08",
        "E09"
      ],
      "note": "★本清单的三个集合【全部由 ISS-407 依赖图里 premises ∩ {PQ01,PQ02} ≠ ∅ 的边 (E01~E09) 现算导出★ ⇒ 少一条 ⇒ 判红"
    },
    {
      "tier": "P1218",
      "pad_mm": 1.218,
      "annular_ring_mm": 0.254,
      "recompute_numbers": [
        "j_debug_copper_x",
        "j_uart_copper_x",
        "j_debug_required_clear_x",
        "j_uart_required_clear_x",
        "j_uart_cover_margin_x",
        "j_debug_opening_margin_x",
        "j_debug_cover_margin_y",
        "annular_ring",
        "seven_numbers_matrix",
        "pad_tier"
      ],
      "rerun_gates": [
        "MECH/check_connector_clearance_caliber.py",
        "MECH/check_debug_seat_3d_fit.py",
        "MECH/check_debug_seat_rework_spec.py",
        "MECH/check_fts_seat_body_geometry.py",
        "MECH/check_fts_seat_sample_plan.py",
        "MECH/check_fts_vs_generic_courtyard_delta.py",
        "MECH/check_jdebug_1p27_clearance.py",
        "MECH/check_juart_1p27_clearance.py",
        "MECH/check_pad_size_coupling_closed.py"
      ],
      "resign_conclusions": [
        "HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md",
        "MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md",
        "MECH/BOARD_ONEPASS_FTS_SEAT_SAMPLE_MEASURE_PLAN.md",
        "MECH/BOARD_ONEPASS_FTS_VS_GENERIC_COURTYARD_DELTA.md",
        "MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md",
        "MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md",
        "MECH/BOARD_ONEPASS_PAD_SIZE_COUPLING.md"
      ],
      "driver": "★2oz 口径档★ (达 0.254 ⇒ 罩住余量几乎归零 ⇒ 红得最狠 · 结构件重算量最大)",
      "dependency_edges": [
        "E01",
        "E02",
        "E03",
        "E04",
        "E05",
        "E06",
        "E07",
        "E08",
        "E09"
      ],
      "note": "★本清单的三个集合【全部由 ISS-407 依赖图里 premises ∩ {PQ01,PQ02} ≠ ∅ 的边 (E01~E09) 现算导出★ ⇒ 少一条 ⇒ 判红"
    }
  ],
  "dependency_graph_ref": {
    "page": "MECH/BOARD_ONEPASS_VERDICT_PREMISE_DEPENDENCY.md",
    "edges_for_pad": [
      "E01",
      "E02",
      "E03",
      "E04",
      "E05",
      "E06",
      "E07",
      "E08",
      "E09"
    ],
    "numbers_union": [
      "annular_ring",
      "annular_ring_mm",
      "connector_clearance_caliber",
      "copper_w_along",
      "courtyard_delta_18",
      "j_debug_copper_x",
      "j_debug_cover_margin_y",
      "j_debug_opening_margin_x",
      "j_debug_required_clear_x",
      "j_uart_copper_x",
      "j_uart_cover_margin_x",
      "j_uart_required_clear_x",
      "pad_tier",
      "per_edge_mm",
      "seat_3q_sample",
      "seat_clearance_x",
      "seat_interference",
      "seven_numbers_matrix"
    ],
    "gates_union": [
      "MECH/check_connector_clearance_caliber.py",
      "MECH/check_debug_seat_3d_fit.py",
      "MECH/check_debug_seat_rework_spec.py",
      "MECH/check_fts_seat_body_geometry.py",
      "MECH/check_fts_seat_sample_plan.py",
      "MECH/check_fts_vs_generic_courtyard_delta.py",
      "MECH/check_jdebug_1p27_clearance.py",
      "MECH/check_juart_1p27_clearance.py",
      "MECH/check_pad_size_coupling_closed.py"
    ],
    "conclusions_union": [
      "HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md",
      "MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md",
      "MECH/BOARD_ONEPASS_FTS_SEAT_SAMPLE_MEASURE_PLAN.md",
      "MECH/BOARD_ONEPASS_FTS_VS_GENERIC_COURTYARD_DELTA.md",
      "MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md",
      "MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md",
      "MECH/BOARD_ONEPASS_PAD_SIZE_COUPLING.md"
    ],
    "core_seven_numbers": [
      "j_debug_copper_x",
      "j_uart_copper_x",
      "j_debug_required_clear_x",
      "j_uart_required_clear_x",
      "j_uart_cover_margin_x",
      "j_debug_opening_margin_x",
      "j_debug_cover_margin_y"
    ]
  },
  "blind_gate_registry": [
    {
      "gate": "MECH/check_debug_seat_3d_fit.py",
      "sensitivity": "BLIND",
      "iss403_baseline_rc": 0,
      "iss403_baseline_stdout_md5": "a64fd53091c16f9538348ffa23a99a37",
      "rerun_rc": 0,
      "rerun_stdout_md5": "a64fd53091c16f9538348ffa23a99a37",
      "stdout_md5_matches_iss403": true,
      "lib_signature": {
        "kicad_mod_runtime_refs": 2,
        "libroot_refs": 0,
        "p1000_literal_refs": 9,
        "class": "BLIND(hardcoded-pad-value)"
      },
      "blind_mechanism": "official 表把铜箔宽写死成 pad=1.000 的产物",
      "iss403_blind_lines": [
        "L683",
        "L686",
        "L491",
        "L746",
        "L753"
      ]
    },
    {
      "gate": "MECH/check_debug_seat_rework_spec.py",
      "sensitivity": "BLIND",
      "iss403_baseline_rc": 0,
      "iss403_baseline_stdout_md5": "b86c561098d8d52f9a873780e00a3ce3",
      "rerun_rc": 0,
      "rerun_stdout_md5": "b86c561098d8d52f9a873780e00a3ce3",
      "stdout_md5_matches_iss403": true,
      "lib_signature": {
        "kicad_mod_runtime_refs": 0,
        "libroot_refs": 0,
        "p1000_literal_refs": 4,
        "class": "BLIND(hardcoded-pad-value)"
      },
      "blind_mechanism": "OFFICIAL_DEBUG_COPPER_X / OFFICIAL_COPPER_Y 模块级常量写死",
      "iss403_blind_lines": [
        "L120",
        "L122",
        "L579"
      ]
    },
    {
      "gate": "MECH/check_fts_seat_body_geometry.py",
      "sensitivity": "BLIND",
      "iss403_baseline_rc": 0,
      "iss403_baseline_stdout_md5": "5d17b5e23afa509561cdcee7c527526b",
      "rerun_rc": 0,
      "rerun_stdout_md5": "5d17b5e23afa509561cdcee7c527526b",
      "stdout_md5_matches_iss403": true,
      "lib_signature": {
        "kicad_mod_runtime_refs": 0,
        "libroot_refs": 0,
        "p1000_literal_refs": 0,
        "class": "BLIND(no-lib-read)"
      },
      "blind_mechanism": "全文件无任何 .kicad_mod / LIBROOT 读入口",
      "iss403_blind_lines": []
    },
    {
      "gate": "MECH/check_connector_clearance_caliber.py",
      "sensitivity": "BLIND",
      "iss403_baseline_rc": 1,
      "iss403_baseline_stdout_md5": "7ade27949541ba0d694088e812c8b6b5",
      "rerun_rc": 1,
      "rerun_stdout_md5": "7ade27949541ba0d694088e812c8b6b5",
      "stdout_md5_matches_iss403": true,
      "lib_signature": {
        "kicad_mod_runtime_refs": 0,
        "libroot_refs": 0,
        "p1000_literal_refs": 1,
        "class": "BLIND(hardcoded-pad-value)"
      },
      "blind_mechanism": "全文件无任何 .kicad_mod / LIBROOT 读入口",
      "iss403_blind_lines": []
    },
    {
      "gate": "MECH/check_fts_vs_generic_courtyard_delta.py",
      "sensitivity": "BLIND",
      "iss403_baseline_rc": 0,
      "iss403_baseline_stdout_md5": "7839434d7e69608953507a51946bb165",
      "rerun_rc": 0,
      "rerun_stdout_md5": "7839434d7e69608953507a51946bb165",
      "stdout_md5_matches_iss403": true,
      "lib_signature": {
        "kicad_mod_runtime_refs": 0,
        "libroot_refs": 0,
        "p1000_literal_refs": 0,
        "class": "BLIND(no-lib-read)"
      },
      "blind_mechanism": "全文件无任何 .kicad_mod / LIBROOT 读入口",
      "iss403_blind_lines": []
    },
    {
      "gate": "MECH/check_jdebug_1p27_clearance.py",
      "sensitivity": "SENSITIVE",
      "iss403_baseline_rc": 0,
      "iss403_baseline_stdout_md5": "",
      "rerun_rc": 0,
      "rerun_stdout_md5": "3bbd512a94a61d89cf766fbb0375f313",
      "stdout_md5_matches_iss403": null,
      "lib_signature": {
        "kicad_mod_runtime_refs": 12,
        "libroot_refs": 7,
        "p1000_literal_refs": 0,
        "class": "SENSITIVE(lib-read)"
      },
      "sensitive_mechanism": "LIBROOT 现读 .kicad_mod ⇒ copper_w_along = span + pad_along",
      "pad_1p110_red": [
        "G1",
        "G2",
        "G3",
        "G4"
      ]
    },
    {
      "gate": "MECH/check_juart_1p27_clearance.py",
      "sensitivity": "SENSITIVE",
      "iss403_baseline_rc": 0,
      "iss403_baseline_stdout_md5": "",
      "rerun_rc": 0,
      "rerun_stdout_md5": "bf3a434cd122c91bf4bcc9c98c964a20",
      "stdout_md5_matches_iss403": null,
      "lib_signature": {
        "kicad_mod_runtime_refs": 14,
        "libroot_refs": 15,
        "p1000_literal_refs": 0,
        "class": "SENSITIVE(lib-read)"
      },
      "sensitive_mechanism": "LIBROOT / --libroot 现读 .kicad_mod",
      "pad_1p110_red": [
        "J0",
        "J1",
        "J5",
        "J7"
      ]
    }
  ],
  "fab_capability": {
    "question": "★本单自己查的结果 (不外发 · 不挂成外部依赖)★",
    "primary_source": "JLCPCB 官方 PCB 能力页 https://jlcpcb.com/capabilities/pcb-capabilities",
    "primary_evidence": "官网",
    "primary_quote_verbatim": "PTH annular ring ≧0.20mm 2-layer: 1 oz: Recommended 0.25 mm or above; absolute minimum 0.18 mm 2 oz: 0.254 mm or above Multilayer: 1 oz: Recommended 0.20 mm or above; absolute minimum 0.15 mm 2 oz: 0.254 mm or above",
    "primary_live_fetch": {
      "url": "https://jlcpcb.com/capabilities/pcb-capabilities",
      "saved_to": "tmp/iss410/jlcpcb_pcb_capabilities_live.html",
      "md5": "351f5f897ea1236c30d4ad2409e84311",
      "bytes": 140276,
      "note": "★本单本机 curl 现取 · 与 ISS-403 留存的 tmp/cron775d_r90/jlcpcb_pcb_capabilities_20261124_2043.html (md5 24dd86f068aa85728b74706f2fd80b3e) 逐字对照 ⇒ 环宽四行一致 ★"
    },
    "secondary_source": "PCB.cn 官方能力页 https://pcbcn.com/capabilities",
    "secondary_evidence": "官网",
    "secondary_quote_verbatim": "Min Width of Annular Ring | 0.15mm / 6mil",
    "applicable_row": "Multilayer: 1 oz",
    "applicable_row_reason": "★本板 = 8 层 (板文件 layers 段 F.Cu + In1..In6.Cu + B.Cu 共 8 个 *.Cu signal 层) · 外层铜 1 oz (HW/PCB/FAB_ORDER_NOTES.md §叠层表)★",
    "recommended_mm": 0.2,
    "absolute_min_mm": 0.15,
    "two_layer_1oz_absolute_min_mm": 0.18,
    "board_layer_count": 8,
    "board_outer_copper_oz": 1,
    "tier_meets_matrix": {
      "P1000": {
        "annular_ring_mm": 0.145,
        "multilayer_1oz_abs_min_0p15": false,
        "multilayer_1oz_rec_0p20": false,
        "two_layer_1oz_abs_min_0p18": false,
        "two_layer_1oz_rec_0p25": false
      },
      "P1010": {
        "annular_ring_mm": 0.15,
        "multilayer_1oz_abs_min_0p15": true,
        "multilayer_1oz_rec_0p20": false,
        "two_layer_1oz_abs_min_0p18": false,
        "two_layer_1oz_rec_0p25": false
      },
      "P1110": {
        "annular_ring_mm": 0.2,
        "multilayer_1oz_abs_min_0p15": true,
        "multilayer_1oz_rec_0p20": true,
        "two_layer_1oz_abs_min_0p18": true,
        "two_layer_1oz_rec_0p25": false
      },
      "P1218": {
        "annular_ring_mm": 0.254,
        "multilayer_1oz_abs_min_0p15": true,
        "multilayer_1oz_rec_0p20": true,
        "two_layer_1oz_abs_min_0p18": true,
        "two_layer_1oz_rec_0p25": true
      }
    },
    "degradation_plan": {
      "problem": "★「板厂是谁」这一格至今 [0数据] (HW/PCB/FAB_ORDER_NOTES.md 全文只写『板厂』从未指名)★",
      "rule": "★降级口径 = 【适用行由本板自己的叠层规格决定, 不由板厂名字决定】★ ⇒ 叠层 8 层 + 外层 1 oz 是【我们的规格】⇒ 适用行 = Multilayer: 1 oz ⇒ 下限 0.15 / 推荐 0.20 ⇒ 板厂名字【不参与】选档 ✓",
      "safest_tier_without_external_confirm": "P1218",
      "safest_tier_reason": "★P1218 的环宽 0.2540 同时 ≥ 0.15 (多层绝对下限) / ≥ 0.18 (2 层绝对下限) / ≥ 0.20 (多层推荐) / ≥ 0.25 (2 层推荐) ⇒ 四行全过 ⇒ 【不需要任何板厂回复就能确定可制造】★ ⇒ 代价 = MECH 侧重算量最大 + J_UART 罩住余量 0.0260 (最坏 -0.2740) 红得最狠",
      "no_external_dependency": "★本单【不外发任何询价/问询/采购】(老板 2026-11-11 19:31 + 2026-11-12 02:02) ⇒ 四档全列 + 每档达成口径 + 每档 MECH 侧后果 + 每档结构件代价 全部算好 ⇒ main 拍档时直接选一档, 不必回本单再算一遍, 也不必等板厂回信 ★"
    }
  },
  "baseline_files": {
    "board": "HW/PCB/demo_mainboard.kicad_pcb",
    "netlist": "HW/netlist_v1.csv",
    "pinlist": "HW/netlist_v1_pins.csv",
    "bom": "HW/BOM_v1.csv"
  },
  "table_baselines": {
    "board": "611b869e13518c3c023fb178f91a0075",
    "netlist": "6aee500e60ba0732f83a9cf557ba90ab",
    "pinlist": "9174309df1ec9411ac8e8d9e80ee386a",
    "bom": "5b9993992405904a60ac96a020b375d8"
  },
  "board_baseline": {
    "path": "HW/PCB/demo_mainboard.kicad_pcb",
    "md5": "611b869e13518c3c023fb178f91a0075",
    "size": 4940213,
    "mtime": "2026-11-06 07:07:17.362193413"
  },
  "outbox_baseline": {
    "tree_md5": "7c5f45e922447340349a224cf05a9807",
    "files": 22
  },
  "gate_criteria": {
    "T1": "四来源一致性 —— BOM / 作业包 / 真相页机器块 / 板面 footprint 逐来源实读 ⇒ 判「记没记这一格 + 记的是哪一档」⇒ 四来源档位不一致 或 任何一来源没记 ⇒ 判红",
    "T2": "当前档位机器可判 —— 从板面 footprint 实读 J_DEBUG/J_UART 的 THT 焊盘边长 ⇒ 落在四档哪一档; 不在任何一档 ⇒ 判红 (不许从文档抄)",
    "T3": "换档重算清单完整 —— 四档每一档的『必须重算的数 / 必须重跑的闸 / 必须重签的结论』三张清单 ⇒ 条数 ≥ N 且每条都能在 ISS-407 依赖图里找到对应节点 ⇒ 少一条判红",
    "T4": "盲闸登记 + 漂移检测 —— 7 道判决链闸的 pad 敏感性登记在册; 每跑一次现读 stdout md5 与登记基线对拍 + 静态 lib-read 签名复核 ⇒ 状态从『盲』变『不盲』或反过来 ⇒ 判红",
    "T5": "fail-closed —— 依赖图页 / 真相页 / BOM 任一读不到 ⇒ 判红, 不许判绿",
    "T6": "零挂链 + 零外发自证 —— grep -c 本闸名 state/gate_check.py = 0 且 state/outbox/ 树摘要与基线逐字相同",
    "T7": "板指纹自证 —— 跑完板 md5 / mtime / size 与基线逐字相同"
  },
  "open_items": {
    "OI-410-1": "焊盘前提量最终取哪一档 (P1010 / P1110 / P1218) ⇒ to=main (★本单不代拍★)",
    "OI-410-2": "BOM 的 J_DEBUG/J_UART 行要不要补『焊盘边长』这一格 (HW 域 ⇒ to=hw-lead, 拍板归 main) ★",
    "OI-410-3": "作业包 L243 调试口开口段要不要把 pad 档写死进认领句 ★",
    "OI-410-4": "现状真相页 (FTS_VS_GENERIC) 的现状值型判据要不要随拍档同批更新 ★",
    "OI-410-5": "7 道 MECH 闸挂不挂 state/gate_check.py ⇒ to=main (ISS-403 OI-403-4 / ISS-405 同源)"
  },
  "decision_taken_here": "not_decided_here"
}
```

★**页尾**: ★**本页 = 真相页 + 机器块; 判据载体在 `MECH/check_premise_tier_decision.py` (★裸跑 rc=1 = 现状红; `--selftest` rc=0 末行逐字 `ALL TESTS PASS`★) · 交卷页 = `HANDOFF/2026-11-25_mech-lead_ISS410_前提量选档决策表与闸.md`** ★
★**★本单零写板 · 零落表 (除自有分片) · 零改既有闸 · 零改既有页正文 · 零挂链 · 零外发 · 不代拍 · 不自签** ★


==============================================================================
## ★§10 · 【追加式】补 · cont1 趟 (★2026-11-25 03:1x~03:2x · mech-lead★) ★

★**本段是【追加】, 不是重写**: ★**§0~§9 的正文与机器块逐字未动** ★
★**补之前** 本页 = `84024` B / md5 `185b5f689b87ce13bb4b164e341aacc5` ★
★**补之后** 的字节数 + md5 ⇒ 记在交卷页 `HANDOFF/2026-11-25_mech-lead_ISS410_前提量选档决策表与闸.md` §B7.9 (★★那两组数字两处都写·不许只写一处★★) ★
★**★方法论纪律 (★本段特意不含「json 围栏」★)**: ★`MECH/check_premise_tier_decision.py` 的 `load_page_machine_block()` 用正则取的是【**最后一个** json 围栏】⇒ ★本页若在 §9 之后再加一个 json 围栏, 闸就会去解析新块 ⇒ 必炸★ ⇒ ★**本段一律不写任何 json 围栏 ⇒ 闸的解析目标仍是 §9 机器块★ ★`[实测]`
★**★踩过的坑 (★本趟实测, 已回滚重做★)**: ★本段第一版在正文里写了「三个反引号 + json」这个字面量 ⇒ 闸的正则把它当成【一个新 json 围栏的开头】⇒ ★**机器块解析当场失败, 闸多出 5 条假红 (T5/T6 全炸)★** ⇒ ★**处置: 把本页截回 84024 B (md5 `185b5f689b87ce13bb4b164e341aacc5`, 逐字复原) 再重写本段, 且正文里再不许出现那个字面量★ ★`[实测]`

### ★§10.1 · 【本趟实测到的一条新事实】★ 挂链覆盖率闸: 9/10 ⇒ **8/10** (★因本闸在盘★)

| 项 | 读数 |
|---|---|
| ★**本单新闸在盘上** ★ | `MECH/check_premise_tier_decision.py` ⇒ ★**它成了 ISS-405 那道闸 M1「盘上未登记的闸」的第二条红项** ★ |
| ★**本机实跑** ★ | `python3 MECH/check_mech_gate_hook_coverage.py` ⇒ ★**rc=1 · 合计 8/10** ★ (★ISS-410 brief §三 写的是「9/10」—— 那是【本闸还没落盘时】的读数★) ★ |
| ★**M1 红项逐字** ★ | ★`★盘上未登记的闸 2 道: MECH/check_premise_tier_decision.py, MECH/check_verdict_premise_dependency.py` ★ |
| ★**M2 红项** ★ | ★10 道必挂闸既不在门禁链、也不在人工签核台账 (★与本单无关, 是现状★) ★ |
| ★**不许去擦** ★ | ★roster (`MECH/BOARD_ONEPASS_GATE_HOOK_COVERAGE.md`) 是 ISS-405 已签收页 ⇒ ★**本单无权代改** ⇒ 这条已作为 §8 `OI-410-5` 交 main ★`[实测]` ★ |

### ★§10.2 · 【诚实登记】机器块 `open_items` 少登记了 `OI-410-6`

★**本页 §8 的未决项表列了 6 条 (`OI-410-1`~`OI-410-6`), 但 §9 机器块的 `open_items` 只登记了 5 条 (`OI-410-1`~`OI-410-5`) ⇒ ★**漏了 `OI-410-6` (`check_fts_seat_sample_plan.py` 与 `check_pad_size_coupling_closed.py` 这 2 道要不要补 A/B 实测)★ ★
★**处置**: ★**不原地改机器块** (★那会破坏「§0~§9 逐字不动」这条追加式纪律★) ⇒ ★**在这里补登记**, 并同时补进 `state/fragments/mech.yaml` 的 `needs_from` (`iss410_q6_ab_test_two_more_gates`) 与 `needs_open_ledger` (`iss410_ledger_oq6_ab_test_two_more_gates`)★ ⇒ ★**三处口径一致 (表格 / 机器块补登记 / 分片)★★ ★`[实测]`
★**`OI-410-6` 逐字**: ★`check_fts_seat_sample_plan.py` 与 `check_pad_size_coupling_closed.py` 这 2 道 (★依赖图挂 PQ01/PQ02 但【没做过 A/B】★) 要不要补 A/B 实测 ⇒ ★**归属 main** ★

### ★§10.3 · 本趟 (cont1) 的自检读数 (★逐字·★全文落 `logs/iss410/`★) ★

| 命令 | rc | 末行 / 关键读数 |
|---|---|---|
| `python3 MECH/check_premise_tier_decision.py --selftest` | ★0★ | ★`ALL TESTS PASS` · ★正向 1 条 · 反向 19 条★ ★`[实测]` ★ |
| `python3 MECH/check_premise_tier_decision.py` (裸跑) | ★1★ | ★`RESULT: FAIL (5 条判据不通过)` ⇒ T1 ×4 (BOM/作业包/板面 没记 + 只有 1/4 记着) + T2 ×1 (板面 SMD 占位 ⇒ 判定不出档位) ⇒ ★**红的是现状** ★`[实测]` ★ |
| `python3 MECH/check_verdict_premise_dependency.py --selftest` (ISS-407 闸·复核用) | ★0★ | ★`ALL TESTS PASS` · 正向 2 + 反向 12 ⇒ ★**本单未改它一字** ★`[实测]` ★ |
| `python3 MECH/check_mech_gate_hook_coverage.py` (ISS-405 闸·复核用) | ★1★ | ★合计 8/10 ⇒ 见 §10.1 ★`[实测]` ★ |
| `python3 state/check_brief_commands.py --brief-file state/dispatch_briefs/ISS-410_mech_premise_tier_decision_table.md` | ★0★ | ★brief 自检命令全过 ★`[实测]` ★ |
| 分片收口四项自检 | — | ★丢 key = 0 · 多的 key = 17 (全是新增) · **老条目内容有变 = 0** ★`[实测]` ★ |

### ★§10.4 · 本趟【没有】改变的任何口径 (★点名·免得被误读★) ★

★**① 四档的档位定义没变** (★`P1000`/`P1010`/`P1110`/`P1218` = `1.000`/`1.010`/`1.110`/`1.218` mm★) ★
★**② 七个数的定义式没变** (★§1.1 的 7 条公式逐字不动★) ★
★**③ 28 格矩阵没变** (★本趟只【复核】未重算; 闸 T3b 每次跑都现算 28 格并与 ISS-403 登记值对拍 ⇒ 差 > 1e-9 即红★ ⇒ ★**矩阵本身在机器上被持续担保**★) ★
★**④ 板厂能力四行没变** (★`[官网]` 双源现取件 md5 `351f5f897ea1236c30d4ad2409e84311` + PCB.cn 副源★) ★
★**⑤ 盲闸登记 5 盲 + 2 敏感没变** (★本趟【复核】stdout md5 对拍, 未重做 A/B★) ★
★**⑥ `decision_taken_here` 仍是 `not_decided_here`** ⇒ ★**选档一条都没代拍** ★`[实测]` ★

★**★本段是【追加】: §0~§9 与机器块逐字未动 · 本页补前 `84024` B / md5 `185b5f689b87ce13bb4b164e341aacc5` · 补后数字见交卷页 §B7.9 ★**
