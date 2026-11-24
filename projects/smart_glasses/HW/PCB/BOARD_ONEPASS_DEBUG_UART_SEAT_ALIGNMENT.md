# BOARD_ONEPASS_DEBUG_UART_SEAT_ALIGNMENT · `J_DEBUG` / `J_UART` 座体选型【四方对齐作业包】

> **交卷人**: 硬件总工 (hw-lead) · **单号**: ISS-383 · **日期**: 2026-11-24 · **类型**: ★纯分析 + 新建机器闸 + 库清单核对 ⇒ **零写板 · 零落表 · 零改既有闸 · 零改已签收件 · 零外发 · 不代拍** ★
> **来源单**: ISS-380 (hw-lead, 2026-11-24 06:07 交卷) 交回的两条缺口 —— ★**(a)** §2 候选表 D-1 / U-1 的「单排 1×4 / 1×2 排布」只到家族页, 官网单品页二次确认标 `[推算]` ⇒ **真实排布与 pin 方径未坐实** · ★**(b)** §5-④ 自查出的三方三口径不自洽 (板面两个封装都是 0.5 mm 排距 SMD 占位盘 / BOM 写「1.27 mm 直插排针」/ 结构侧算「Cortex-10 2×5」) ★
> **板指纹 (本单开工前 / 交卷后逐字一致)**: md5 `611b869e13518c3c023fb178f91a0075` / size `4940213` / mtime `2026-11-06 07:07:17.362193413` · `[实测]`
> **本单新建**: 本页 + `HW/check_debug_uart_seat_alignment.py` (闸 K0~K4) · ★**既有页面正文一个字未动** · `[实测]`
> **不重复谁**: 落位几何 = ISS-376 / ISS-379 已 verified (只引用) · 针序契约 = ISS-375 已交卷 (只引用) · 料号清单本体 = ISS-380 (只读) · MECH 侧排布标签 = ISS-382 (在飞, 一个字节都不碰) · `[实测]`

---

## §0 一句话结论

★★**四个口径现在【一个都还对不上】: BOM 描述栏说「1.27 mm 单排直插」, 板面实际封装是「0.5 mm 排距 SMD 占位盘」, 结构侧模型是「Cortex-10 2×5 直插」, E-1 板决策只说了「land pitch 0.50 → 1.27」; ★而且本单把 ISS-380 标 `[推算]` 的那一格坐实之后, 冲突比原先登记的更深一层 —— ISS-380 登记的两个【首选候选件】`FTSH-104-01-F-DV` (D-1) 与 `FTSH-102-01-F-DV` (U-1) 在 Samtec 官网单品页上是「**2 Row 双排 + SMT 贴片**」, 排布与型态两格都不满足板侧口径; ⇒ ★「板那一趟」要一次改对, 必须先裁三件事: (1) 【排布/脚数】单排 1×4 还是双排 2×5 · (2) 【型态】直插 THT 还是贴片 SMT · (3) 【库封装】官方通用件还是自建 —— 三件都在 §3 的对齐表里逐格显式登记, 裁决归 main + mech-lead, 本单不代拍**★ · `[实测]` (板侧/库侧) + `[官网]`/`[媒体]` (厂商侧) + `[推算]` (家族规律)

 ★**三条关键结论拆解 (结论必须落到这三条上)**: · `[实测]`

| # | 结论 | 证据等级 |
|---|---|---|
| 0-1 | ★**「排布」那一格坐实了, 而且坐实的是【冲突】不是【一致】**: `FTSH-104-01-F-DV` = Samtec 官网单品页标题「.050in/1.27mm Micro Header Strip, **8 Pin, 2 Row, SMT**, Gold Flash/Tin, .120in Post」+ DigiKey 参数表「Connector Header **Surface Mount** 8 position / Number of Positions 8 / Number of Rows **2**」⇒ **8 脚双排贴片**, 与板侧真值「1×4 单排直插」在【脚数 / 排布 / 型态】三格上都不一致 | `[官网]` (samtec.com 单品页标题) + `[媒体]` (DigiKey 参数表) |
| 0-2 | ★**「1.27 mm 单排直插」这一档, 本单在 Samtec 与 Würth 两家都查不到对应件**: ★**Samtec FTSH 1.27 mm 族核到的 8 个官网单品页 / DigiKey 参数表, 「Number of Rows」全部 = 2** (8/10/20/6/4/28/40/…) ⇒ 该族只有双排 (垂直 SMT `-DV` / 垂直直插 `-D` / 水平 SMT `-DH` / 混装 `-MT`) ⇒ **单排没有**; ★**Würth WR-PHD 1.27 mm 族在册件全部是 2 排** (`62202021121` 20 触点 2 排 / `62202821121` 28 触点 2 排 / `62130421021` 2×4 SMT), 而 WR-PHD 的 1 排件全在 2.54 mm 档 (`61300411121` / `61300211121`) ⇒ **两家的 1.27 mm 都没有单排** | `[官网]` + `[媒体]` + `[推算]` (家族编码规律) |
| 0-3 | ★**库侧那格反而是对得上板侧的, 但只对得上【单排直插】这一档**: 本地 `Connector_PinHeader_1.27mm.pretty` 里 `PinHeader_1x04_P1.27mm_Vertical` (md5 `7a5f470c1f70d4b832be258501945385`) 与 `PinHeader_1x02_P1.27mm_Vertical` (md5 `47bcbf6d0f267d543e50d4b2a8dfabf5`) **都是单排 THT / 排距 1.27 / 焊盘 1.000×1.000 / 钻孔 0.65**, 与 BOM 描述栏同型 ⇒ **若主口径裁定为「1×4 / 1×2 单排直插」, 板侧 land 与库封装两边都现成, 缺的只是厂商料号**; ★**但库里那两个 `_SMD_Pin1Left/Right` 变体是「2 列交错」, 与 Samtec 双排 SMT 的「2 排 1.27 mm 排中心距」不同型 ⇒ 若裁定走双排 SMT, 库封装必须自建** | `[实测]` (本单自己解析 `.kicad_mod`) |

---

## §1 候选件真实规格表 (★只深挖 D-1 / U-1 两个首选件; 其余 6 个各一行状态★)

 ★**硬要求**: 逐格标证据等级 (`[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]`) · ★**查不到的每一格必须标 `[0数据]` + 写降级方案 (降级方案是必须项, 见 §1.5)** ★
 ★**本节只填 ISS-380 §2 标 `[推算]` 的那一格 (真实排布) 与 pin 方径, 不重做 ISS-380 的选型结论。** · `[实测]`

### §1.1 D-1 = Samtec `FTSH-104-01-F-DV` (ISS-380 登记的 `J_DEBUG` 首选候选)

| 格 | 实测值 | 出处 / 复现 | 证据等级 |
|---|---|---|---|
| 排距 | `1.27 mm` (`.050"`) | Samtec 官网单品页标题「.050in/1.27mm Micro Header Strip, 8 Pin, 2 Row, SMT, Gold Flash/Tin, .120in Post」https://www.samtec.com/products/ftsh-104-01-f-dv · DigiKey「Pitch - Mating 0.050" (1.27mm)」 | `[官网]` + `[媒体]` |
| ★**脚数** ★ | ★**`8 Pin`** (不是 1×4 的 4 脚) ★ | Samtec 官网单品页标题「**8 Pin, 2 Row**」· DigiKey「Number of Positions **8**」https://www.digikey.com/en/products/detail/samtec-inc/FTSH-104-01-F-DV/6678165 | `[官网]` + `[媒体]` |
| ★**排布** ★ | ★**双排 (2 Row)** —— 每排 4 位 · 排中心距 `1.27 mm` ★ | Samtec 官网单品页标题「**2 Row**」· DigiKey「Number of Rows **2**」「Row Spacing - Mating 0.050" (1.27mm)」· ★**同族旁证**: 第三方库存表记「**FTS-105-01-F-DV** — CONNECTOR, HEADER, 1.27MM, **SMT, 10WAY**, SAMTEC」⇒ 105 = 每排 5 位 × 2 排 = 10 位 ⇒ **规律成立: `-DV` = 每排 N 位 × 2 排** | `[官网]` + `[媒体]` + `[推算]` (家族编码规律) |
| ★**型态** ★ | ★**SMT 贴片 (Surface Mount)** —— ★**不是直插 THT** ★ | Samtec 官网单品页标题「**SMT**」· DigiKey「Connector Header **Surface Mount** 8 position」· ★**旁证**: 同族 `FTSH-105-01-S-D-K` 官网标题写的是「10 Pin, 2 Row, **Through Hole**, 30µin Gold/Tin」⇒ ★**`-D-` = 双排直插 / `-DV` = 双排垂直贴片, 两者在 Samtec 官网标题里是分开写的** | `[官网]` + `[媒体]` |
| ★**pin 方径** ★ | ★**方针 `0.016 in` = `0.41 mm`** ★ | Samtec 官网家族页的 mated-views 表逐字: 「FTSH - .050" (1,27mm), **.016" (.41mm) Square Post** Terminal Strip, Vertical Surface Mount」· Samtec 原厂 PDF 规格段: 「Terminal Material: Phosphor Bronze」 | `[官网]` |
| ★**座体高 (post)** ★ | ★**post 高 `0.120 in` = `3.05 mm`** (="-01-" lead style A) ★ | Samtec 官网单品页标题尾部「**.120in Post**」· ★**Samtec 原厂 PDF 规格段**: 「LEAD STYLE A –01 (3.05) .120 –02 (1.91) .075 –03 (1.65) .065 –04 (3.81) .150 –05 (4.32) .170」⇒ ★**⇒ 座体/针柱高出板面 `3.05 mm` 这一格, ISS-380 标 `[0数据]` 的项, 本单坐实到 `3.05 mm`** | `[官网]` |
| 镀层 | `-F-` = **Gold Flash/Tin** (闪光金) | Samtec 官网单品页标题「**Gold Flash/Tin**」; 对照同族 `-L-` = 10µin Gold/Tin、`-S-` = 30µin Gold/Tin | `[官网]` |
| ★**铜箔 X 宽** ★ | ★**`[0数据]`** —— ★**SMT 版的原厂推荐 land pattern (IPC-1752) 本单未拿到** ⇒ ⇒ ★**不能拿板侧已算的 `4.8100` 顶替 (那是 1×4 THT 单排的数, 与 2×4 SMT 双排不是同一档)** ⇒ 降级见 §1.5-④ | Samtec 官网单品页只给「Download Product Specs」入口, 本单未取到该 land 图; Mouser 镜像的 Samtec PDF 是 **SURFACE MOUNT MICRO HEADER** 目录页, 未含逐件 land 图 | `[0数据]` |
| ★**与板侧真值逐格对比 (1×4 / 1.27 / 单排 / 直插)** ★ | ★**排距 ✓ · 脚数 ✗ (8≠4) · 排布 ✗ (双排≠单排) · 型态 ✗ (SMT≠直插)** ⇒ ★**四格里错三格 ⇒ D-1 不能作为「板侧 1×4 直插」的落表件** | 本表 + `HW/FP_TRUTH_BASELINE.md:125` (板侧目标封装) + `HW/BOM_v1.csv:71` | `[实测]` + `[官网]` |
| ★**与结构侧 Cortex-10 口径逐格对比 (2×5 / 1.27 / 双排 / 直插)** ★ | ★**排距 ✓ · 排布 ✓ (双排) · 型态 ✗ (SMT≠直插) · 脚数 ✗ (2×4=8 ≠ 2×5=10)** ⇒ ★**只差【脚数】与【型态】两格** ⇒ ★**D-1 属于「结构侧那一档」, 但不是那一档里的直插版** | 本表 + `MECH/service_port_check.py:70` (`jd_cols=5` / `jd_rows=2`) | `[实测]` + `[官网]` |

### §1.2 U-1 = Samtec `FTSH-102-01-F-DV` (ISS-380 登记的 `J_UART` 首选候选)

| 格 | 实测值 | 出处 / 复现 | 证据等级 |
|---|---|---|---|
| 排距 | `1.27 mm` (`.050"`) | Samtec 官网单品页标题「.050in/1.27mm Micro Header Strip, 4 Pin, 2 Row, SMT, Gold Flash/Tin, .120in Post」https://www.samtec.com/products/ftsh-102-01-f-dv · DigiKey 同族页「Pitch - Mating 0.050" (1.27mm)」 | `[官网]` + `[媒体]` |
| ★**脚数** ★ | ★**`4 Pin`** (不是 1×2 的 2 脚) ★ | Samtec 官网单品页标题「**4 Pin, 2 Row**」 | `[官网]` |
| ★**排布** ★ | ★**双排 (2 Row)** —— 每排 2 位 ⇒ 物理上是 2×2 方阵 ★ | Samtec 官网单品页标题「**2 Row**」· DigiKey「Number of Rows 2」「Number of Positions 4」 | `[官网]` + `[媒体]` |
| ★**型态** ★ | ★**SMT 贴片 (Surface Mount)** —— ★**不是直插 THT** ★ | Samtec 官网单品页标题「**SMT**」· DigiKey「Connector Header Surface Mount」 | `[官网]` + `[媒体]` |
| ★**pin 方径** ★ | ★**方针 `0.016 in` = `0.41 mm`** (同族) ★ | Samtec 官网家族页 mated-views 表「.016" (.41mm) Square Post」 | `[官网]` |
| ★**座体高 (post)** ★ | ★**post 高 `0.120 in` = `3.05 mm`** (同族 "-01-") ★ | Samtec 官网单品页标题「**.120in Post**」· Samtec 原厂 PDF「LEAD STYLE A –01 (3.05) .120」 | `[官网]` |
| 镀层 | `-F-` = **Gold Flash/Tin** | Samtec 官网单品页标题 | `[官网]` |
| ★**铜箔 X 宽** ★ | ★**`[0数据]`** (SMT 双排 2×2 的原厂 land 未取到) ⇒ 降级见 §1.5-④ | 同 §1.1 | `[0数据]` |
| ★**与板侧真值逐格对比 (1×2 / 1.27 / 单排 / 直插)** ★ | ★**排距 ✓ · 脚数 ✗ (4≠2) · 排布 ✗ (双排≠单排) · 型态 ✗ (SMT≠直插)** ⇒ ★**四格里错三格 ⇒ U-1 不能作为「板侧 1×2 直插」的落表件** | 本表 + `HW/BOM_v1.csv:77` | `[实测]` + `[官网]` |
| ★**结构侧状态** ★ | ★**`J_UART` 座体在结构侧已定 DNP (只留焊盘)** ⇒ ★**⇒ `J_UART` 的选型在【结构开口】上没有硬约束, 但在【板面 land + 脚表】上仍有硬约束 (脚表 `J_UART.pin1/pin2` = `UART_TX`/`UART_RX` 已在 `HW/netlist_v1_pins.csv:275`~`276` 具名)** | `MECH/service_port_check.py:217` 判据 2.6 逐字: 「J_UART 座体若装 (DNP) 需开口 Y 放大到 5.24 —— 本文取 4.60 ⇒ J_UART 座体一律 DNP」 | `[实测]` (MECH 侧) + `[实测]` (板侧) |

### §1.3 ★其余 6 个候选: 各一行状态 (★只写「排距 / 脚数是否满足板侧真值」, 不再深挖★)

| # | 厂商 + 完整料号 | 排距 / 脚数 / 排布 / 型态 | 对【板侧真值 1×4 单排直插 1.27】是否满足 | 证据等级 |
|---|---|---|---|---|
| D-2 | **Samtec** `FTSH-105-01-L-DV-K` | `1.27 mm` · `10 Pin` · 双排 2×5 · SMT | ★**排距 ✓ · 脚数 ✗ (2×5=10 ≠ 1×4)** ⇒ 属【结构侧 Cortex-10 口径】那一档 | `[媒体]` (DigiKey: "10 POSITION, 2ROW, 1.27MM, Surface Mount Gold") + `[官网]` (家族页) |
| D-3 | **Würth Elektronik** `61300411121` | `2.54 mm` · `4 Contact` · 1 Row · THT | ★**排距 ✗ (2.54≠1.27) · 脚数 ✓ · 单排 ✓ · 直插 ✓** ⇒ ★**只有排距一格不合 ⇒ 结构侧必须清空区 X 从 `7.62` 改到 ≥ `8.62` ⇒ 必然改结构件** | `[官网]` (Würth 家族页) + `[媒体]` (RS: "2.54mm Pitch / 4 Contacts / 1 Row / Through Hole") |
| D-4 | **Würth Elektronik** `62130421021` | `1.27 mm` · 双排 4 位 (2×2) · SMT | ★**排距 ✓ · 脚数 ✗ (双排 2×2 ≠ 单排 1×4)** | `[媒体]` (alldatasheet 收录 WÜRTH 原厂 PDF: "WR-PHD 1.27mm SMT Straight Dual Pin Header") |
| U-2 | **Würth Elektronik** `61300211121` | `2.54 mm` · `2 Contact` · 1 Row · THT | ★**排距 ✗ (2.54≠1.27) · 脚数 ✓** ⇒ 铜箔 X 宽 `3.5400` 放不进 `J_UART` 现有 `2.5400` 清空区 ⇒ 结构红灯加剧 | `[官网]` + `[媒体]` (同族 4 脚件在 RS 实测 "Through Hole Straight / Pitch 2.54 / Tail 3mm / Mating 6mm"; ★**本条 2 位单排这一格标 `[推算]`, 系同族外推**) |
| U-3 | **Würth Elektronik** `62201021121` | `1.27 mm` · `20 Contact` · 2 Row · THT | ★**排距 ✓ · 脚数 ✗ (2×10)** ⇒ 属【Cortex 口径的直插版本】参照 | `[媒体]` (RS: "WR-PHD / Pitch 1.27mm / 20 Contacts / 2 Rows / Through Hole / 1.0A") |
| U-4 | **GCT** `USB4105-GF-A` (板面现写简称 `USB4105-16P`) | USB Type-C 母座 · 16 脚 · SMT + 直插固定脚 | ★**不是 `J_UART` 候选** ⇒ 列在此处的唯一目的 = ★**给 BOM 写法一个正例: 厂商型号要写「可下单完整料号 + 官网链接」, 而不是板面现在这种 `USB4105-16P` 简称** (见 §4) | `[官网]` (gct.co 产品页) + `[媒体]` (TME/DigiKey 参数表) |

### §1.4 ★★本单新查实的一条【家族级】事实 (★这一条决定了 §4 能不能写出可采购料号★)

| # | 事实 | 证据 | 证据等级 |
|---|---|---|---|
| 1-4-1 | ★**Samtec FTSH 1.27 mm 族 = 双排族**: 本单核到的 Samtec 官网单品页 + DigiKey/RS 参数表共 8 个 FTSH 件 (`104/102/105/103/107/108/110/120` 系列), ★**「Number of Rows」全部 = 2** ⇒ ★**该族可查到的型态只有: 双排垂直 SMT (`-DV`) / 双排垂直直插 (`-D`) / 双排水平 SMT (`-DH`) / 混装 (`-MT`)** ⇒ ★**⇒ 「1.27 mm 单排」在 Samtec FTSH 族内未查到对应件** | DigiKey「FTSH-104-01-F-DV」Number of Rows 2 · 「FTSH-104-01-F-D」Number of Rows 2 · 「FTSH-104-01-F-DV-TR」2 · 「FTSH-104-01-F-DV-A-P-TR」2 · 「FTSH-104-01-F-DV-005」2 (Positions 8 / Loaded 7) · Samtec「FTSH-104-01-L-DV」标题 8 Pin 2 Row · Samtec「FTSH-105-01-S-D-K」标题 10 Pin 2 Row Through Hole · 第三方库存表「FTS-105-01-F-DV — 1.27MM, SMT, 10WAY」 | `[官网]` + `[媒体]` + `[推算]` |
| 1-4-2 | ★**Würth WR-PHD 1.27 mm 族 = 双排族**: 在册 1.27 mm 件 `62202021121` (20 触点 / 2 Row / THT)、`62202821121` (28 触点 / 2 Row / THT)、`62130421021` (双排 SMT) 全部 2 Row; ★**而 WR-PHD 的 1 Row 件全在 2.54 mm 档** (`61300411121` 4 触点 1 Row / `61300211121` 2 触点 1 Row) ⇒ ★**⇒ Würth 侧「1.27 mm 单排直插」也未查到对应件** | RS 参数表逐字: "62202021121 — 1.27mm Pitch, 20 Contacts, **2 Rows**, Through Hole" · "62202821121 — 1.27 mm Pitch, 28 Contacts, **2 Row**, Through Hole" · "61300411121 — 2.54 mm Pitch, 4 Contacts, **1 Row**, Through Hole" · "61300211121 — 2.54 mm Pitch, 2 Contacts, **1 Row**, Through Hole" | `[媒体]` + `[官网]` |
| 1-4-3 | ★**⇒ 本单给 main 的第一个硬事实**: ★**「1×4 / 1×2 单排直插 1.27 mm」这一档, 在 Samtec 与 Würth 两家主流厂都查不到对应件** ⇒ ★**⇒ 这不是「再查查就能查到」, 而是要么 (甲) 另找厂 (通用 1.27 mm 单排排针 / JLC 通用件), 要么 (乙) 接受双排档并改脚表 + 结构清空区** ⇒ ★**⇒ 「板那一趟」照 BOM 描述栏 (单排直插) 画之前, 这件事必须先有结论** | 本页 §1.4-1 + §1.4-2 + §2 (库里有单排 THT 通用封装, 说明【封装】这一侧不缺, 缺的是【厂商单料号】) | `[推算]` (结论基于 §1.4-1/2 两条实测) |

### §1.5 ★降级方案 (★查不到 / 不满足时的必填项, 逐条可执行★)

| # | 降级方案 | 内容 | 证据等级 |
|---|---|---|---|
| 1-5-① | ★**改选同族但改档的型号 (两档各自的后果)** | ★**(甲) 走「双排」档**: `J_DEBUG` ⇒ `FTSH-105-01-L-DV-K` (D-2, 2×5 SMT, 与结构侧 Cortex-10 脚数排布完全同型) ⇒ ★**代价**: 板侧 land 从 1×4 改成 2×5 (改板) + 库封装须自建 (库里的 `_SMD_Pin1Left` 是 2 列交错, 与 2×5 不同型) + 脚表要加到 10 脚; ★**(乙) 走「单排」档**: 板侧与库封装都现成 (§2), ★**代价**: 厂商单料号在 Samtec / Würth 都查不到 ⇒ 须另找厂 / 按规格书下单 | `[官网]` + `[媒体]` + `[推算]` |
| 1-5-② | ★**单排直插 1.27 mm 查不到 ⇒ 降级为「按封装规格书采购」**: ★**采购技术条件已可从库里取到** —— 排距 `1.27` / 单排 / 脚数 `4`(J_DEBUG) 与 `2`(J_UART) / 直插 THT / 方针 `0.5 mm` 推定 (库封装钻孔 `0.65` ⇒ 方针 0.5 + 0.15 间隙) / 焊盘 `1.000 × 1.000` / post 高 `3.05 mm` ⇒ ★**⇒ 「厂商 + 完整料号 + 官网链接」这一栏在甲档未落定前, 只能写规格 + 库封装名, 不能写假料号** | `HW/PCB/BOARD_ONEPASS_DEBUG_UART_SEAT_ALIGNMENT.md` §2 库封装实读 (钻孔 `0.65` / 焊盘 `1.000×1.000` / 排距 `1.27`) + Samtec 官网 post 高 `3.05 mm` | `[实测]` + `[官网]` |
| 1-5-③ | ★**座体高不再是 `[0数据]` ⇒ 按 `3.05 mm` 出件, 但仍留余量**: ★**FTSH 族 post 高 `3.05 mm` 已坐实** ⇒ ★**结构侧可用上界从「座体高完全未知」收紧到「post 高 3.05 mm」** ⇒ ★**但 Z 向可用空间只有 `4.70 mm` (镜脚内腔厚 `7.30` − PCB 元件面 `2.60`, `MECH/service_port_check.py` `BASE` 实读推得) ⇒ ★**⇒ 若最终选 1.27 mm 直插排针且 post 高 ≥ `3.05 mm`, 必须在结构开口 Z 向按「座体凸出镜脚外表面」建模 (与 `J_USB_C` 同类做法)** ⇒ ★**⇒ 本单不给「选直插还是贴片」的裁决, 只把这条余量账摆出来** | Samtec 官网「.120in Post」+ `MECH/service_port_check.py` `BASE` 块 (`cav_h` / `h_pcb_face`) | `[官网]` + `[推算]` |
| 1-5-④ | ★**双排 SMT 的铜箔 X 宽查不到 ⇒ 降级为「按 §2.4 清单自建封装时从原厂 land 图补」**: ★**不许拿 `4.8100` (1×4 THT 单排) 顶替 2×4 SMT 的数** ⇒ ★**自建封装所需的关键尺寸清单见 §2.4, 缺的项只有「原厂推荐 SMT land (pad 尺寸 / 间距 / 阻焊开窗)」一项, 其余 (钻孔 / 焊盘尺寸 / 排距) 在单排档已由库封装给出** | 本页 §2.3 / §2.4 | `[0数据]` + `[实测]` |
| 1-5-⑤ | ★**高度查不到时不得反向污染「铜箔 X 宽」**: ★**铜箔 X 宽由【排距 × 脚数 × 排布】唯一确定, 与座体高无关** ⇒ ★**⇒ §1 的 `[0数据]` 只影响「自建 SMT 封装的 land 尺寸」, 不影响「选型本身可不可采购」** | 本页 §1 与 §3 逐格表 | `[实测]` |

---

## §2 ★库封装可得性表 (★自己解析 `.kicad_mod`, 不许只抄库名★)

 ★**库路径**: `/home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty/` · ★**解析命令见 §6 命令 2 / 3** · `[实测]`

### §2.1 与 `J_DEBUG` (1×4) / `J_UART` (1×2) 相关的 `.kicad_mod` 逐个解析

| # | `.kicad_mod` | md5 | 类型 (`attr`) | 焊盘数 | 排布 | 排距 | 焊盘尺寸 | 钻孔 | 铜箔包络 (rot0) | 证据等级 |
|---|---|---|---|---|---|---|---|---|---|---|
| 2-1-1 | `PinHeader_1x04_P1.27mm_Vertical` | `7a5f470c1f70d4b832be258501945385` | `through_hole` | **4** | ★**单排 1×4** (pad1 `(0,0)` / pad2 `(0,1.27)` / pad3 `(0,2.54)` / pad4 `(0,3.81)`, 沿局部 **Y** 一列) | `1.27` | `1.000 × 1.000` (pad1 `rect`, pad2~4 `circle`) | `0.65` | X `1.0000` × Y `4.8100` | `[实测]` |
| 2-1-2 | `PinHeader_1x02_P1.27mm_Vertical` | `47bcbf6d0f267d543e50d4b2a8dfabf5` | `through_hole` | **2** | ★**单排 1×2** (pad1 `(0,0)` / pad2 `(0,1.27)`) | `1.27` | `1.000 × 1.000` (pad1 `rect`, pad2 `circle`) | `0.65` | X `1.0000` × Y `2.2700` | `[实测]` |
| 2-1-3 | `PinHeader_1x04_P1.27mm_Vertical_SMD_Pin1Left` | `9d6b0e63e99e6484d2cd3fa0bb28c4a5` | SMD | **4** | ★**2 列 × 4 行交错** (`(-1.5,-1.905)` / `(1.5,-0.635)` / `(-1.5,0.635)` / `(1.5,1.905)`) | `1.27` (Y 向) | `3.000 × 0.650` | 无 | X `6.0000` × Y `4.4600` | `[实测]` |
| 2-1-4 | `PinHeader_1x02_P1.27mm_Vertical_SMD_Pin1Left` | `7f15e4a1a32059c2b8eea027edfdbd84` | SMD | **2** | ★**2 列交错** (`(-1.5,-0.635)` / `(1.5,0.635)`) | `1.27` (Y 向) | `3.000 × 0.650` | 无 | X `6.0000` × Y `1.9200` | `[实测]` |
| 2-1-5 | `PinHeader_2x04_P1.27mm_Vertical` | `248a1fdbe052733752598d6f8ede637d` | `through_hole` | **8** | ★**双排 2×4** (pad1 `(0,0)` / pad2 `(1.27,0)` / pad3 `(0,1.27)` / pad4 `(1.27,1.27)` …, 行中心距 `1.27`) | `1.27` | `1.000 × 1.000` | `0.65` | 行距 `1.27` ⇒ 铜箔行向宽 `2.2700` | `[实测]` |
| 2-1-6 | `PinHeader_2x02_P1.27mm_Vertical` | `d6463821d4973e4a7236f5ff9a7cb607` | `through_hole` | **4** | ★**双排 2×2** (pad1 `(0,0)` / pad2 `(1.27,0)` / pad3 `(0,1.27)` / pad4 `(1.27,1.27)`) | `1.27` | `1.000 × 1.000` | `0.65` | 行距 `1.27` ⇒ 铜箔行向宽 `2.2700` | `[实测]` |
| 2-1-7 | `..._Vertical_SMD_Pin1Right` 变体 | (见 §6 命令 2 的 md5 清单) | SMD | 4 / 2 | ★**2 列交错 (pin1 在右列)** ⇒ ★**与 `_Pin1Left` 同型, 只是镜像** | `1.27` | `3.000 × 0.650` | 无 | 同 `_Pin1Left` | `[实测]` |

 ★**库目录全量清单 (供 main 复核「库侧到底有什么」)**: `PinHeader_1x01..1x40_P1.27mm_{Vertical,Horizontal}.kicad_mod` + `PinHeader_1x02..1x40_P1.27mm_Vertical_SMD_Pin1Left/Right.kicad_mod` + `PinHeader_2x01..2x40_P1.27mm_{Vertical,Horizontal}.kicad_mod` + `PinHeader_2x01..2x40_P1.27mm_Vertical_SMD.kicad_mod` ⇒ ★**1.27 mm 的 1×2 / 1×4 直插封装【在盘】** (与任务书一致) · `[实测]`

### §2.2 「排布是否同型」逐件判定 (★不许拿「排距一样」当「封装可用」★)

| 库件 | 与【板侧真值 1×4 单排直插】同型? | 与【D-1 `FTSH-104-01-F-DV` 双排 2×4 SMT】同型? | 与【U-1 `FTSH-102-01-F-DV` 双排 2×2 SMT】同型? | 证据等级 |
|---|---|---|---|---|
| `PinHeader_1x04_P1.27mm_Vertical` | ★**✓ 同型** (单排 4 位 THT 1.27) | ✗ (单排 ≠ 双排; THT ≠ SMT) | ✗ | `[实测]` |
| `PinHeader_1x02_P1.27mm_Vertical` | ★**✓ 同型** (单排 2 位 THT 1.27) | ✗ | ✗ | `[实测]` |
| `PinHeader_1x04_P1.27mm_Vertical_SMD_Pin1Left/Right` | ✗ (双列交错 ≠ 单排) | ★**✗ 排布不同型** ★(库件 = **2 列 × 4 行**, 列中心距 `3.00`; FTSH D-1 = **2 排 × 4 位**, 排中心距 `1.27`) ⇒ ★**连排布口径都对不上, 更不用说 THT/SMT** | ✗ | `[实测]` + `[官网]` |
| `PinHeader_2x04_P1.27mm_Vertical` | ✗ (双排) | ★**✗ 排布同型但型态不同型** (库件 THT + 钻孔 `0.65`; D-1 = **SMT 无钻孔**) ⇒ ★**⇒ 若选 D-1, 这个件不能直接用, 只能拿它当「2×4 排布几何」的参照** | ✗ | `[实测]` + `[官网]` |
| `PinHeader_2x02_P1.27mm_Vertical` | ✗ | ✗ | ★**✗ 排布同型但型态不同型** (THT vs SMT) ⇒ 同上 | `[实测]` + `[官网]` |

 ★**⇒ §2 的三条结论**: · `[实测]`
 ★**(1)** **板侧口径 (单排直插) ⇒ 库封装现成, 不用自建** —— `J_DEBUG` → `Connector_PinHeader_1.27mm:PinHeader_1x04_P1.27mm_Vertical` (★**这一条已经由 ISS-356 锁死**: `HW/FP_TRUTH_BASELINE.md:125`「候选真库封装 `lib:name` = `Connector_PinHeader_1.27mm:PinHeader_1x04_P1.27mm_Vertical`」+ 同页 `:126` 库文件 md5 `7a5f470c1f70d4b832be258501945385` ★与本单实读逐字一致) · `[实测]`
 ★**(2)** **`J_UART` 在 `HW/FP_TRUTH_BASELINE.md` 里 `grep -c` = `0` ⇒ 它的目标 `lib:name` 还没登记** ⇒ 对应件应同为 `Connector_PinHeader_1.27mm:PinHeader_1x02_P1.27mm_Vertical` (md5 `47bcbf6d0f267d543e50d4b2a8dfabf5`) ⇒ **这是「板那一趟」要补的一条登记** (本单零落表, 只登记) · `[实测]`
 ★**(3)** **双排 SMT 档 (D-1 / U-1) ⇒ 库里【没有同型件】, 必须自建** ⇒ 关键尺寸清单见 §2.4 · `[实测]`

### §2.3 「不许拿排距一样当封装可用」的三条对照 (★本单的核心方法论, 写在这里防下一个人再踩★)

| # | 对照 | 事实 | 证据等级 |
|---|---|---|---|
| 2-3-1 | ★**排距一样 ≠ 排布一样** | 库件 `..._SMD_Pin1Left` 与 FTSH D-1 **排距都是 `1.27`**, 但排布是 **2 列 × 4 行 (列距 `3.00`)** vs **2 排 × 4 位 (排距 `1.27`)** ⇒ ★**⇒ 换 land 后 pin 对位全变 (脚序方向 / pin1 所在排), ISS-375 已交卷的针序契约判据 D0~D8 必须在新 land 上重跑** | `[实测]` + `[官网]` |
| 2-3-2 | ★**排布一样 ≠ 型态一样** | 库件 `PinHeader_2x04_P1.27mm_Vertical` 与 D-1 **排布一样 (2×4)** ⇒ 但库件是 **THT 带钻孔 `0.65`**, D-1 是 **SMT 无钻孔** ⇒ ★**⇒ 用错型态的后果 = 板上多 8 个不该有的钻孔 + 焊盘形状完全不同** | `[实测]` + `[官网]` |
| 2-3-3 | ★**型态一样 ≠ 方针一样** | 库件钻孔 `0.65` ⇒ 适配方针约 `0.5 mm`; ★**而 Samtec FTSH 方针 `0.41 mm`** ⇒ ★**⇒ 若真选 Samtec 双排 SMT, 焊盘与钻孔的尺寸口径全部要按原厂 land 走, 不能沿用库里通用件** | `[实测]` + `[官网]` |

### §2.4 ★自建封装所需的关键尺寸清单 (★仅当主口径裁定走「双排 SMT」时才需要★)

| # | 关键尺寸 | 现值 | 来源 | 证据等级 |
|---|---|---|---|---|
| 2-4-1 | 排距 | `1.27` | Samtec 官网 (D-1 / U-1 单品页标题) | `[官网]` |
| 2-4-2 | 排布 / 排数 / 每排位数 | D-1 = `2 排 × 4 位`; U-1 = `2 排 × 2 位`; 排中心距 `1.27` | Samtec 官网单品页 + DigiKey「Number of Rows / Row Spacing - Mating」 | `[官网]` + `[媒体]` |
| 2-4-3 | 焊盘 (pad) 尺寸 / 焊盘间距 | ★**`[0数据]`** —— 原厂推荐 SMT land (IPC-1752) 未取到 | — | `[0数据]` ⇒ 降级 §1.5-④ |
| 2-4-4 | 钻孔 | ★**SMT 无钻孔 (不适用)** ★ | Samtec 官网「SMT」 | `[官网]` |
| 2-4-5 | pin 方径 (方针) | `0.41 mm` (`0.016"`) | Samtec 官网家族页 mated-views 表 | `[官网]` |
| 2-4-6 | post 高 (座体高出板面) | `3.05 mm` (`0.120"`) | Samtec 官网单品页标题 + 原厂 PDF lead style A | `[官网]` |
| 2-4-7 | 阻焊开窗 / 丝印边界 | ★**`[0数据]`** —— 须按原厂 land 图取 | — | `[0数据]` ⇒ 降级 §1.5-④ |
| 2-4-8 | 板面焊盘排布的 pin1 定位 (哪一排 / 脚序方向) | ★**`[0数据]`** ⇒ ★**须查原厂 land 图 + 用 ISS-375 针序契约判据 D0~D8 复验** | — | `[0数据]` |

---

## §3 ★四方口径对齐表 (★逐格标「一致 / 冲突 / 待定」+ 冲突格的后果★)

 ★**四个口径**: ① BOM 描述栏 (`HW/BOM_v1.csv:71` / `:77`) · ② 板面实际封装 (板面实读) · ③ 结构侧模型 (`MECH/service_port_check.py`, 只读) · ④ E-1 板决策 (`HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 判据 `B33_PIN_LAND_1P27` + `HW/PCB/BOARD_ONEPASS_S10_SWAP_SET_TRUTH.md` §2.1 腿③) · `[实测]`

### §3.1 逐格 × 逐口径 对齐矩阵

| 格 | ① BOM 描述栏 | ② 板面实际封装 | ③ 结构侧模型 | ④ E-1 板决策 | 判定 | 后果 (不迁就, 只摆代价) | 证据等级 |
|---|---|---|---|---|---|---|---|
| ★**排距** ★ | `1.27 mm` (`HW/BOM_v1.csv:71` / `:77` 描述栏「1×4 1.27mm 排针」/「1×2 1.27mm 排针」) | ★**`0.50 mm`** (4 个 SMD pad 中心距全 `0.500`; 2 个 SMD pad 中心距 `0.500`) | `1.27 mm` (`jd_pitch = 1.27`) | `1.27` (判据栏「`J_DEBUG`/`J_UART` 排针 land pitch 0.50→1.27mm」) | ★**①③④ 一致 · ② 冲突** | ★**后果**: 1.27 mm 实物排针落不进现役 0.5 mm 占位 land ⇒ **板那一趟必须把 land 换成选定型号的官方 land**, 否则座体装不上 (与 ISS-380 §5-④ 同源) | `[实测]` (①②③④ 四处逐条实读) |
| ★**脚数** ★ | `J_DEBUG` = 4 · `J_UART` = 2 (描述栏「1×4」/「1×2」; 脚表 `HW/netlist_v1_pins.csv:202`~`205` / `:275`~`276` 逐条具名) | `J_DEBUG` = 4 个 pad · `J_UART` = 2 个 pad | ★**`10` (Cortex-10 2×5)** (`jd_cols = 5` / `jd_rows = 2`) | ★**待定** (E-1 只说了 pitch, 没说脚数) | ★**①② 一致 · ③ 冲突 · ④ 待定** | ★**后果**: 脚表脚数与结构侧「必须清空区 X `7.62`」/「开口 X `10.20`」不同源 ⇒ 结构侧 5-① 那三个数要按选定档重算; 若走双排 2×5 ⇒ **脚表要加到 10 脚 + 脚位重新对位** | `[实测]` |
| ★**排布** ★ | ★**单排** (描述栏「1×4」/「1×2」) | ★**单排** (`J_DEBUG` 4 pad 一列 @0.5; `J_UART` 2 pad 一列 @0.5) | ★**双排 2×5** (`jd_rows = 2`) | ★**待定** (E-1 未指定) | ★**①② 一致 · ③ 冲突 · ④ 待定** | ★**后果**: ★**排布不同 ⇒ 换 land 后 pin 对位全变** (pin1 落在哪一排 / 脚序方向是否翻转) ⇒ **ISS-375 已交卷的针序契约判据 D0~D8 必须在新 land 上重跑**; 且 **库封装必须换成同排布件** (§2.2) | `[实测]` |
| ★**型态** ★ | ★**直插 (THT)** (「排针」; 板面 value 栏也写「排针」) | ★**SMD 贴片占位盘** (pad 属性 = SMD, `0.275 × 0.900`, **无钻孔**) | ★**直插 (Cortex-10 座体, 有实体座体要清空)** (`jd_body_w = 5.08` / `jd_body_h = 2.54`) | ★**待定** (E-1 未指定) | ★**①③ 一致 · ② 冲突 · ④ 待定** | ★**后果**: ★**现役板上两个封装都是 0.5 mm 排距 SMD 占位盘** ⇒ 若按 BOM 口径换直插 land ⇒ **要新增 8+2 个钻孔** + 铜箔 X 宽从 `1.7750` / `0.7750` 变 `4.8100` / `2.2700` ⇒ 结构清空区重算; 若按 D-1/U-1 (双排 SMT) ⇒ **库封装必须自建** (§2.4) | `[实测]` |

★**机器可读口径块 (★闸 K2 逐格点名用; 与 §3.1 表格逐字对应★)**: · `[实测]`

```
<!-- MACHINELINE
GRID|排距|BOM=1.27|PCB=0.50|MECH=1.27|E1=1.27
GRID|脚数|BOM=4|PCB=4|MECH=10|E1=unset
GRID|排布|BOM=单排|PCB=单排|MECH=双排2x5|E1=unset
GRID|型态|BOM=直插THT|PCB=SMD占位|MECH=直插|E1=unset
-->
```

### §3.2 ★★冲突登记 (★本单只登记, 不改任何一个口径; 裁决归 main + mech-lead★)

 ★**登记格式**: `CONFLICT|<格>|<口径对照>|<后果>` · ★**下列每一条都是机器可检的 (闸 K2 逐条点名, 缺一条即红)** · `[实测]`

```
CONFLICT|排距|① BOM描述栏 1.27mm vs ② 板面实际封装 0.50mm|后果: 1.27mm 实物排针落不进现役 0.5mm 排距 SMD 占位 land ⇒ 板那一趟必须把两个座体的 land 换成选定型号的官方 land (B33_PIN_LAND_1P27 已登记) ⇒ 铜箔 X 宽与结构清空区同步重算
CONFLICT|脚数|① BOM描述栏 4脚/2脚 vs ③ 结构侧 Cortex-10 10脚(2x5)|后果: 脚表 HW/netlist_v1_pins.csv 的脚数与结构侧必须清空区 X 7.62 / 开口 X 10.20 不同源 ⇒ 结构侧 5-1 三个数要按选定档重算 ⇒ 走双排 2x5 则脚表要加到 10 脚且脚位重新对位 ⇒ ISS-375 针序契约 D0~D8 需重跑
CONFLICT|排布|① BOM描述栏 单排 vs ③ 结构侧 双排2x5|后果: 排布不同则换 land 后 pin 对位全变 (pin1 所在排 / 脚序方向) ⇒ 库封装必须换成同排布件 (库的 _SMD_Pin1Left 是 2 列交错 与 Samtec 双排 1.27mm 排中心距 不同型) ⇒ 自建封装则须补原厂 land 图
CONFLICT|型态|① BOM描述栏 直插THT vs ② 板面实际封装 SMD贴片占位盘|后果: 现役板两个封装都是 0.5mm 排距 SMD 占位盘 (pad 0.275x0.900 无钻孔) ⇒ 按直插口径换 land 要新增 10 个钻孔且铜箔 X 宽 1.7750/0.7750 -> 4.8100/2.2700 ⇒ 结构清空区重算 ⇒ 按双排SMT口径则库封装必须自建
```

 ★**★再加一条【厂商件与板侧口径】的冲突登记 (本单新查实, 不在原四格里, 但同样是冲突, 必须显形)**: · `[实测]`

```
CONFLICT|厂商件排布|① 板侧真值 1x4单排直插 vs D-1 FTSH-104-01-F-DV 实测 8Pin/2Row/SMT|后果: D-1 四格里错三格 (脚数8vs4/排布双排vs单排/型态SMTvs直插) ⇒ 不能作为板侧 1x4 直插的落表件 ⇒ 若按 D-1 落表则等于把板侧口径改成双排SMT ⇒ 脚表/结构清空区/库封装三处同时要改
CONFLICT|厂商件排布|① 板侧真值 1x2单排直插 vs U-1 FTSH-102-01-F-DV 实测 4Pin/2Row/SMT|后果: U-1 四格里错三格 (脚数4vs2/排布双排vs单排/型态SMTvs直插) ⇒ 不能作为板侧 1x2 直插的落表件 ⇒ 同上三处连带
CONFLICT|厂商件可得性|① 板侧真值 1.27mm单排 vs Samtec/Wurth 两族均无双排以外的单排件|后果: 板侧口径那一档在 Samtec 与 Wurth 都查不到可下单料号 (库封装却现成) ⇒ 型号栏要么另找厂按规格书下单 (§1.5-2) 要么改走双排档 ⇒ 这一格不落定 BOM 型号栏就填不出可采购料号
```

### §3.3 ★判据与事实的分账 (★闸 K4 要求的「判据 / 事实分开」★)

 ★**判据 (别人定的规则, 本单只引用不修改)**: · `[实测]`
- ★**判据 1**: `J_DEBUG` / `J_UART` 的 land pitch **`0.50 → 1.27`** 要在【同一趟】做完 ⇒ 出处 `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 判据栏 `B33_PIN_LAND_1P27` (行 `63`) + JSON 块 (行 `544`~`549`) + `HW/PCB/BOARD_ONEPASS_S10_SWAP_SET_TRUTH.md` §2.1 腿③ (行见 §6 命令 4) ⇒ ★**E-1 由 main 2026-11-17 18:45 拍死, 本单不改**
- ★**判据 2**: `J_DEBUG` 的目标库封装 = `Connector_PinHeader_1.27mm:PinHeader_1x04_P1.27mm_Vertical` ⇒ 出处 `HW/FP_TRUTH_BASELINE.md:125` + `:126` (库文件 md5 `7a5f470c1f70d4b832be258501945385`) ⇒ ★**本单实读 md5 与之逐字一致 ⇒ 该判据未被本单推翻**
- ★**判据 3**: 结构侧「必须清空区 = 座体, 不是焊盘」+ `CRIT = 0.60` ⇒ 出处 `MECH/service_port_check.py` 判据 2.4 / `TOL["fdm_part"]` ⇒ ★**本单只引用**
- ★**判据 4**: 零写板 / 零落表 / 零改既有闸 / 零改已签收件 / 零外发 / 不代拍 ⇒ 出处 任务书 ISS-383 §五

 ★**事实 (本单自己跑出来的, 每条给复现命令)**: · `[实测]`
- ★**事实 1**: 板面 `J_DEBUG` = 4 个 SMD pad, 排距 `0.500`, pad `0.275 × 0.900`, 铜箔 X `142.0625..143.8375` × Y `56.1500..57.0500` ⇒ §6 命令 1
- ★**事实 2**: 板面 `J_UART` = 2 个 SMD pad, 排距 `0.500`, pad1 `(18.6400, 68.6000)` = `UART_TX`, pad2 `(19.1400, 68.6000)` = `UART_RX`, 铜箔 X `18.5025..19.2775` × Y `68.1500..69.0500` ⇒ §6 命令 1
- ★**事实 3**: 库件 `PinHeader_1x04_P1.27mm_Vertical` = 单排 4 位 THT / 排距 `1.27` / 焊盘 `1.000 × 1.000` / 钻孔 `0.65` ⇒ §6 命令 2
- ★**事实 4**: 库件 `_SMD_Pin1Left` = 2 列交错 / 焊盘 `3.000 × 0.650` / 无钻孔 ⇒ §6 命令 2
- ★**事实 5**: `FTSH-104-01-F-DV` = `8 Pin / 2 Row / SMT` (Samtec 官网标题 + DigiKey 参数表) ⇒ §6 命令 5
- ★**事实 6**: `FTSH-102-01-F-DV` = `4 Pin / 2 Row / SMT` (Samtec 官网标题) ⇒ §6 命令 5
- ★**事实 7**: FTSH 方针 `0.41 mm` / post 高 `3.05 mm` ⇒ §6 命令 5
- ★**事实 8**: `J_UART` 在 `HW/FP_TRUTH_BASELINE.md` 里 `grep -c` = `0` ⇒ §6 命令 4
- ★**事实 9**: 板三项指纹 md5 `611b869e13518c3c023fb178f91a0075` / size `4940213` / mtime `2026-11-06 07:07:17.362193413` ⇒ §6 命令 1

---

## §4 ★BOM 型号栏草案 (★只给草案 · ★不落表 · ★不改 `HW/BOM_v1.csv` 一个字节★)

 ★**先例**: `J_USB_C` 现在写的是 `USB4105-16P` **简称** ⇒ ★**可下单完整料号 = `USB4105-GF-A`** ⇒ ★**「板那一趟」的 BOM 要写完整料号 + 官网链接, 不写简称** (ISS-380 §6 未决项 6-5 已登记, 本单沿用) · `[官网]` + `[媒体]`
 ★**★下面的两行是【草案】, 一行都没落进 `HW/BOM_v1.csv` (闸 K3 会验这一点)★** · `[实测]`

### §4.1 `J_DEBUG` 行型号栏草案 (★三档并存, 由 main 选一档, 本单不选★)

| 档 | 厂商 + 完整料号 + 官网链接 (草案写法) | 对齐到哪一格 | 填上以后**还剩哪几格没对齐** |
|---|---|---|---|
| ★**甲 (板侧口径 · 1×4 单排直插)** ★ | ★**厂商: 待指定 (Samtec / Würth 两家均无 1.27 mm 单排件, 见 §1.4) · 完整料号: 待落定 · 官网链接: 待落定** ⇒ ★**降级写法 (规格书版, 合法可采购描述)**: 「1.27 mm 4 位单排直插排针 (方针 0.5 mm 推定, post 高 3.05 mm) — 库封装 `Connector_PinHeader_1.27mm:PinHeader_1x04_P1.27mm_Vertical` (钻孔 0.65, 焊盘 1.000×1.000)」⇒ ★**对应库封装 md5 `7a5f470c1f70d4b832be258501945385` (已由 ISS-356 锁定)** | 排距 ✓ · 脚数 ✓ · 排布 ✓ · 型态 ✓ ⇒ **四个格全对齐** · `[实测]` (库封装实读) + `[推算]` (方针 0.5 推定) | ★**还剩**: ① **厂商 + 完整料号 + 官网链接**三样都没落定 (§1.4-3: 两家都查不到) · ② **板面 land 仍是 0.5 mm SMD 占位盘**, 板那一趟要换 (§3.1 排距格) · ③ **结构侧按 Cortex-10 2×5 算的三个数** (`7.62` / `10.20` / `5.08`) 要按 1×4 重算 · ④ **pin1 所在排 / 脚序方向**在新 land 上要复验 (ISS-375 D0~D8) · `[实测]` |
| ★**乙 (结构侧 Cortex-10 口径 · 2×5 双排)** ★ | **Samtec** · `FTSH-105-01-L-DV-K` · https://www.samtec.com/products/ftsh · (分销页 https://www.digikey.com/en/products/detail/samtec-inc/FTSH-105-01-L-DV-K-TR/2649981) | 排距 ✓ · 脚数 ✓ (2×5=10) · 排布 ✓ (双排) · 型态 ✓ 垂直 ⇒ ★**与结构侧同型; 与板侧 1×4 口径三格不合** · `[官网]` + `[媒体]` | ★**还剩**: ① **板侧 land 要从 1×4 改成 2×5 (改板)** + 脚表要加到 10 脚 + 库封装要自建 (§2.4, 缺原厂 SMT land) · ② **型态是 SMT 而结构侧假设的是「有实体的直插 Cortex-10 座体」** (`jd_body_h = 2.54` 是那个座体的高, 与 SMT 排针的 post 高 `3.05` 不是一回事) ⇒ **开口 Y 宽 `4.60` 要按真座体重算** · ③ **pin1 所在排**要复验 · `[实测]` + `[官网]` |
| ★**丙 (ISS-380 原首选 · 本单已证伪其排布/型态)** ★ | **Samtec** · `FTSH-104-01-F-DV` · https://www.samtec.com/products/ftsh-104-01-f-dv | ★**排距 ✓ · 排布 ✓ 双排 · 脚数 ✗ (2×4=8 ≠ 10) · 型态 ✓ 垂直 SMT** ⇒ ★**属「双排 SMT」档, 既不是板侧 1×4 档, 也不是结构侧 2×5 档** | ★**还剩**: ★**四格里错三格** (§1.1) ⇒ **本单不建议把它当落表件**, 只作为「双排 SMT 这一档到底长什么样」的证据留档 |

### §4.2 `J_UART` 行型号栏草案 (★三档并存, 本单不选★)

| 档 | 厂商 + 完整料号 + 官网链接 (草案写法) | 对齐到哪一格 | 填上以后**还剩哪几格没对齐** |
|---|---|---|---|
| ★**甲 (板侧口径 · 1×2 单排直插)** ★ | ★**厂商: 待指定 (同 §1.4, 无 1.27 mm 单排件) · 完整料号: 待落定 · 官网链接: 待落定** ⇒ ★**降级写法 (规格书版)**: 「1.27 mm 2 位单排直插排针 (方针 0.5 mm 推定) — 库封装 `Connector_PinHeader_1.27mm:PinHeader_1x02_P1.27mm_Vertical` (钻孔 0.65, 焊盘 1.000×1.000)」⇒ ★**对应库封装 md5 `47bcbf6d0f267d543e50d4b2a8dfabf5` (★**这一条本单新增: `J_UART` 在 `HW/FP_TRUTH_BASELINE.md` 里还没有 target_lib 登记, 见 §2.2-②**)** | 排距 ✓ · 脚数 ✓ · 排布 ✓ · 型态 ✓ ⇒ **四个格全对齐** · `[实测]` (库封装实读) + `[推算]` (方针 0.5 推定) | ★**还剩**: ① 厂商 + 完整料号 + 官网链接 未落定 · ② **板面 land 仍是 0.5 mm SMD 占位盘** · ③ **结构侧 `J_UART` 座体已定 DNP** ⇒ 座体选了也只留焊盘, 但 **铜箔 X 宽换直插后 `0.7750 → 2.2700`, 每边余量 `0.1350 < CRIT 0.60` = 结构红灯** (既有页已算过, 本单不重拍) · ④ **`J_UART` 的 target_lib 还没在 `FP_TRUTH_BASELINE` 登记** · `[实测]` |
| ★**乙 (结构侧口径)** ★ | ★**结构侧 `J_UART` 座体一律 DNP ⇒ 本档无候选件 (板面只留焊盘)** | — · `[实测]` (MECH 侧判据 2.6) | ★**还剩**: 无 (本档不存在) · `[实测]` |
| ★**丙 (ISS-380 原首选 · 本单已证伪其排布/型态)** ★ | **Samtec** · `FTSH-102-01-F-DV` · https://www.samtec.com/products/ftsh-102-01-f-dv | ★**排距 ✓ · 排布 ✓ 双排 · 脚数 ✗ (4≠2) · 型态 ✓ 垂直 SMT** | ★**还剩**: ★**四格里错三格** (§1.2) ⇒ 同 §4.1-丙, 只留档 |

### §4.3 ★BOM 写法正例 (★给「板那一趟」照抄的格式, 不落表★)

 ★**格式**: `厂商 · 完整料号 (可下单, 不写简称) · 官网链接 · 关键参数 (排距 / 脚数 / 排布 / 型态 / 方针 / post 高)` · `[官网]`
 ★**正例 (在册可查)**: `Global Connector Technology (GCT) · USB4105-GF-A · https://gct.co/connector/usb4105 · USB Type-C 母座 16P · SMT 顶装 + 直插固定脚` ⇒ ★**对照**: `J_USB_C` 板面现在写的是 `USB4105-16P` **简称** ⇒ 「板那一趟」要改成上面这行完整写法 · `[官网]` + `[媒体]`

---

## §5 未决项 (★要谁回答什么 + 本单给了什么事实 + 证据等级 · ★不代拍★)

| # | 要谁回答 | 要回答什么 | 本单给了什么事实 | 证据等级 |
|---|---|---|---|---|
| 5-1 | ★**main** ★ | ★**「1×4 直插」这个口径以谁为准** (BOM 描述栏 / 板面现状 / 结构侧 Cortex-10 2×5 三者对不上) ⇒ ★**它决定「板那一趟」要改的是 land、脚表, 还是结构件** | ★**四个口径逐格对齐 (§3.1) + 冲突登记 (§3.2, 6 条) + ★**厂商件实测 (D-1 = 8Pin/2Row/SMT, U-1 = 4Pin/2Row/SMT)** ⇒ ★**⇒ 主口径落定前, BOM 型号栏填不出可采购料号** | `[实测]` + `[官网]` |
| 5-2 | ★**main** ★ | ★**「1.27 mm 单排直插」这一档的厂商料号怎么办**: ★**(甲)** 另找厂 (通用 1.27 mm 单排排针) 按 §1.5-② 的规格书下单 · ★**(乙)** 改走双排档 (D-2 / 结构侧 Cortex-10 同型) | ★**Samtec 与 Würth 两家的 1.27 mm 族【全部是双排】, 本单核到 8+4 个官网/分销件逐条为证 (§1.4)**; ★**而库封装侧单排直插是现成的 (§2.1)** ⇒ ★**⇒ 缺的是「厂商单料号」, 不是「封装」** | `[官网]` + `[媒体]` + `[推算]` |
| 5-3 | ★**mech-lead** ★ | ★**结构侧那三条不自洽点要不要跟着换料号一起重算** (ISS-380 §5-① 脚数 / 5-② 相对位置 / 5-③ 座体高度) | ★**只登记, 不改 MECH 一个字节**: 5-① 脚数 ⇒ 脚表 4/2 脚 vs 结构侧 10 脚 (§3.1) · 5-③ 高度 ⇒ ★**post 高已从 `[0数据]` 收紧到 `3.05 mm`** (FTSH 族), 而 Z 向可用空间只有 `4.70 mm` ⇒ 开口 Z 向要按「座体凸出镜脚外表面」建模 (§1.5-③) · ★**`J_UART` 座体 DNP 这一条结构侧已定, 本单沿用** | `[实测]` + `[官网]` |
| 5-4 | ★**main** ★ | ★**BOM 型号栏什么时候落** (落表 = 改网表真源 ⇒ 须在「板只改一次」那一趟里一次做完) | ★**本单零落表**: `HW/BOM_v1.csv` / `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` 三个 md5 开工前后逐字相同 (§6 命令 6) · ★**§4 只给草案** ⇒ ★**闸 K3 会验「BOM 型号栏此刻仍是待定」** | `[实测]` |
| 5-5 | ★**main** ★ | ★**新闸挂不挂 `state/gate_check.py`** ⇒ ★**本单零挂链** (挂链是 main 的地界; 先例: 提前单独挂 ⇒ 中间态红 ⇒ 现场误读成「板坏了」) | ★**闸脚本已写好并自测通过: `HW/check_debug_uart_seat_alignment.py` (K0~K4) ⇒ ★**挂链与否、挂点在哪, 由 main 拍** | `[实测]` |
| 5-6 | ★**main** ★ | ★**库封装用官方通用件还是自建 Samtec 专用封装** ⇒ ★**本单只给两者的代价, 不代裁** | ★**(甲) 官方通用件**: 板侧 1×4 / 1×2 单排直插档 ⇒ `PinHeader_1x04_P1.27mm_Vertical` (md5 `7a5f470c1f70d4b832be258501945385`, ISS-356 已锁) + `PinHeader_1x02_P1.27mm_Vertical` (md5 `47bcbf6d0f267d543e50d4b2a8dfabf5`) ⇒ ★**代价 = 找一家做单排 1.27 mm 直插的厂, 料号待落定**; ★**(乙) 自建 Samtec 专用封装**: ⇒ ★**代价 = §2.4 清单里 `pad 尺寸 / 焊盘间距 / 阻焊开窗 / 丝印边界 / pin1 定位` 五格全是 `[0数据]`, 要先取原厂 land 图** | `[实测]` + `[0数据]` |
| 5-7 | ★**main** ★ | ★**`J_UART` 的 target_lib 要不要补进 `HW/FP_TRUTH_BASELINE.md`** (★**本单零落表, 只登记**) | ★**`J_UART` 在 `FP_TRUTH_BASELINE.md` 里 `grep -c` = `0`** (§6 命令 4) ⇒ ★**建议对应件 `Connector_PinHeader_1.27mm:PinHeader_1x02_P1.27mm_Vertical` (md5 `47bcbf6d0f267d543e50d4b2a8dfabf5`)** | `[实测]` |

---

## §6 复跑命令 (★每个数都能自己跑出来★)

 ★**前置**: `cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses` · ★**全部只读, 不写板 / 不落表 / 不改既有闸** · `[实测]`

| # | 命令 | 出什么 |
|---|---|---|
| 6-1 | ★`bash state/pcbnew_py.sh -c "import pcbnew; b=pcbnew.LoadBoard('HW/PCB/demo_mainboard.kicad_pcb'); [print(r, 'origin=', round(pcbnew.ToMM(f.GetPosition().x),4), round(pcbnew.ToMM(f.GetPosition().y),4), 'pads=', [(p.GetNumber(), p.GetNetname(), round(pcbnew.ToMM(p.GetPosition().x),4), round(pcbnew.ToMM(p.GetPosition().y),4), round(pcbnew.ToMM(p.GetSize().x),4), round(pcbnew.ToMM(p.GetSize().y),4)) for p in f.Pads()]) for r in ('J_DEBUG','J_UART') for f in [x for x in b.GetFootprints() if x.GetReference()==r]]"` ★ | §3.1 的 ①② 两行 (封装原点 / pad 净名 / 坐标 / 尺寸) + 排距 (相邻 pad 差) |
| 6-2 | ★`md5sum HW/PCB/demo_mainboard.kicad_pcb && stat -c '%s %y' HW/PCB/demo_mainboard.kicad_pcb` ★ | §3.3 事实 9 (板指纹三件套) |
| 6-3 | ★`for f in PinHeader_1x04_P1.27mm_Vertical PinHeader_1x02_P1.27mm_Vertical PinHeader_1x04_P1.27mm_Vertical_SMD_Pin1Left PinHeader_1x02_P1.27mm_Vertical_SMD_Pin1Left PinHeader_2x04_P1.27mm_Vertical PinHeader_2x02_P1.27mm_Vertical; do p=/home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty/$f.kicad_mod; echo "== $f md5=$(md5sum $p | cut -d' ' -f1)"; grep -E '\(pad |\(at |\(size |\(drill |attr' $p; done` ★ | §2.1 全表 (类型 / 焊盘数 / 排布 / 排距 / 焊盘尺寸 / 钻孔) |
| 6-4 | ★`grep -n "B33_PIN_LAND_1P27" HW/PCB/BOARD_ONEPASS_PREFLIGHT.md | head -3 && grep -n "jd_cols\|jd_rows\|jd_pitch\|jd_body_w\|jd_body_h\|ju_body_h\|OPEN_X\|OPEN_Y" MECH/service_port_check.py | head -20 && grep -c "J_UART" HW/FP_TRUTH_BASELINE.md && grep -n "PinHeader_1x04_P1.27mm_Vertical" HW/FP_TRUTH_BASELINE.md | head -3` ★ | §3.1 的 ③④ (E-1 判据 + 结构侧当前用的数) + §3.3 事实 2 / 8 |
| 6-5 | ★**厂商侧 (本单全部靠自己上网查, 未发任何邮件/询价/采购)**: ★`web_fetch https://www.samtec.com/products/ftsh-104-01-f-dv` (标题含「8 Pin, 2 Row, SMT, Gold Flash/Tin, .120in Post」) + `web_fetch https://www.samtec.com/products/ftsh-102-01-f-dv` (标题含「4 Pin, 2 Row, SMT, Gold Flash/Tin, .120in Post」) + `web_fetch https://www.digikey.com/en/products/detail/samtec-inc/FTSH-104-01-F-DV/6678165` (Number of Positions 8 / Number of Rows 2 / Surface Mount) + `web_fetch https://www.samtec.com/products/ftsh` (家族页 mated-views 表: 「.016" (.41mm) Square Post」) + Samtec 原厂 PDF「LEAD STYLE A –01 (3.05) .120」 ★ | §1.1 / §1.2 / §1.4 全部厂商格 |
| 6-6 | ★`md5sum HW/BOM_v1.csv HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/PCB/BOARD_ONEPASS_DEBUG_UART_SEAT_PART_TRUTH.md HW/check_debug_uart_seat_truth.py HW/PCB/BOARD_ONEPASS_JUART_LAND_FIT.md HW/PCB/BOARD_ONEPASS_JDEBUG_LAND_FIT.md` ★ | §0 边界自证 (零落表 / 零改已签收件) |
| 6-7 | ★`sed -n '71p;77p' HW/BOM_v1.csv && sed -n '202,205p;275,276p' HW/netlist_v1_pins.csv` ★ | §3.1 的 ① (BOM 描述栏 + 脚表具名脚) |
| 6-8 | ★`python3 HW/check_debug_uart_seat_alignment.py` / ★`python3 HW/check_debug_uart_seat_alignment.py --selftest` ★ | ★**本单新建闸 K0~K4 (正向 rc=0 / 自测末行 `ALL TESTS PASS`)** |

---

> **本单边界自证**: ★**零写板** (板 md5 仍 `611b869e13518c3c023fb178f91a0075` / size `4940213` / mtime `2026-11-06 07:07:17.362193413`) · ★**零落表** (`HW/BOM_v1.csv` / `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` 一个字节未动) · ★**零改既有闸** (`HW/check_debug_uart_seat_truth.py` / `HW/check_juart_land_fit.py` / `HW/check_board_comparable_gate.py` / `HW/check_s8_target_list.py` / `state/compare_arm_official.py` 五个 md5 逐字未动) · ★**零改已签收页** (`..._PART_TRUTH.md` / `..._JUART_LAND_FIT.md` / `..._JDEBUG_LAND_FIT.md` 三页 md5 逐字未动) · ★**零碰 MECH** (`MECH/**` 一个字节未写) · ★**零挂链** (`state/gate_check.py` 未碰) · ★**零外发** (未发任何邮件 / 询价 / 问询 / 采购) · ★**不代拍** · ★**不写别人的分片** (`sw.yaml` / `mech.yaml` / `pm.yaml` 一个字未写) · ★**沙盒只落 `tmp/iss383_sbx/` + `logs/iss383/`** · `[实测]`
