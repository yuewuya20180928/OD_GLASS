# MECH · 「板那一趟」MECH 判决链 【前提依赖图 + 作废传播矩阵】—— 真相页 (ISS-407 · mech-lead)

> ★**生成**: 2026-11-25 02:2x~03:0x (mech-lead · 本机实跑) · ★**形态**: ★**纯查证 + 纯分析 · 零写板 · 零落表 · 零改既有闸 · 零改既有页正文 · 零挂链 · 零外发 · 不代拍 · 不自签** ★
> ★**纪律归位**: 「板只改一次」纪律 ① (★先派纯分析类·不动板★) · ★**本单是【开工前的依赖图】, 不是【已经出事】** ★
> ★**证据等级**: `[官网]` = 厂商官网/能力表逐字 · `[实测]` = 本机实读/实跑读数 · `[媒体]` = 第三方报道 · `[推算]` = 本机按公式算 · `[0数据]` = 查不到 ★
> ★**承接**: ISS-393 (courtyard 前提错误扩散面) · ISS-397 (座体三量实测档 `[0数据]`) · ISS-399 (9 道闸 35 处 md5 pin) · ISS-400 (115 条机器块指针可达性) · ISS-403 (焊盘 1.000→1.110 ⇒ 7 个数全作废 + 5 道盲闸) · ISS-405 (29 道闸只挂 4 道) ★★**本单不重复它们, 是把它们【接成一条依赖链】** ★
> ★**本页所有数值均由 `MECH/check_verdict_premise_dependency.py` 现读/实扫后渲染 (★不许手抄★)** ★

==============================================================================
## ★§0 · 一句话结论 (★本机实跑得出·不抄任何 agent 报告★) ★

★★ **MECH 判决链的「前提 → 数 → 闸 → 已签收结论」这条链, 今天【没有任何一张表把它写下来】—— 6 张清账页 (ISS-393/397/399/400/403/405) 各自查清了【一格】, 但没有一张说清「我改了哪一个前提量 (焊盘尺寸 / 钻孔 / 座体外形 / 清空区), 到底会让哪几个数、哪几道闸、哪几条已签收结论同时作废, 谁负责重算」⇒ 于是「板那一趟」开工前, 没有人能回答「焊盘从 `1.000` 改成 `1.110`, 我要重算几个数、重跑哪几道闸」★ ★★

★**判据句 (方向)**: ★**MECH 侧必须把「前提量清单 (当前值 + 证据等级 + 真值读取点) → 依赖图 → 作废传播矩阵」三者【机器可判】地落下来, 并在「板那一趟」开工前【逐项过一遍前提值】⇒ 否则任何一个前提量改一格, 就会静默地让一批数、几道闸、几条已签收结论同时过期, 而【没有任何机器闸会响】** ★
★**事实句 (现状)**: ★**本机实跑 (★AST 实扫 9 道判决链闸 + 逐条读点复现★): ① 前提量清单 17 格里有 【4 格没有真值读取点】(★座体外形 X/Y/Z 三量 + 板厚 ⇒ 全是 `[0数据]`★) ⇒ 【前提改了没人知道】; ② 9 道判决链闸里有 【4 道把几何量写死在源码里】(★`official.J_DEBUG.copper.x = 4.81` 这类字面量, 实扫 26 个写死常量点★) ⇒ 【闸判的是「常数对不对」, 不是「板现在是什么」】⇒ 前提一改, 闸照样判绿 (★ISS-403 已 A/B 实测: 两臂 stdout md5 逐字相同★); ③ 另有 【5 道闸一个几何字面量都没有】⇒ 它们的「盲」是另一个根因 (【没有通向 KiCad 库的读入口】族); ④ 本单新闸 `MECH/check_verdict_premise_dependency.py` 【裸跑 rc=1】—— ★**红的是现状, 不是闸故障** ★** ★★
★**两句同时成立, 不许混成一句「OK / 合格」** ★

==============================================================================
## ★§1 · 表 (a) · 前提量清单 (★当前值 + 证据等级 + 真值读取点★) ★

★**读法**: ★**「真值读取点」这一栏 = 机器能重新读出来的地方 (★文件 + 行/正则★) ⇒ 判据 D1 要求脚本能【现读现对拍】, 不许手抄数值★** ★

| ID | ★前提量★ | ★当前值★ | 单位 | ★证据等级★ | ★真值读取点 (★机器可复现★)★ | ★状态★ |
|---|---|---|---|---|---|---|
| `PQ01` | 排针焊盘 X 尺寸 | `1.0000` | mm | `[实测]` | KiCad 官方库 `PinHeader_1x04_P1.27mm_Vertical.kicad_mod` · 读取器 `kicad_mod_pad_x` | ★**有真源** ★ |
| `PQ02` | 排针焊盘 Y 尺寸 | `1.0000` | mm | `[实测]` | KiCad 官方库 `PinHeader_1x04_P1.27mm_Vertical.kicad_mod` · 读取器 `kicad_mod_pad_y` | ★**有真源** ★ |
| `PQ03` | 库件默认钻孔 | `0.6500` | mm | `[实测]` | KiCad 官方库 `PinHeader_1x04_P1.27mm_Vertical.kicad_mod` · 读取器 `kicad_mod_drill` | ★**有真源** ★ |
| `PQ04` | 「板那一趟」规划钻孔 | `0.7100` | mm | `[官网]` | `HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md` · 正则 `0\.71` | ★**有真源** ★ |
| `PQ05` | J_DEBUG 焊盘跨距 (Y 向) | `3.8100` | mm | `[实测]` | KiCad 官方库 `PinHeader_1x04_P1.27mm_Vertical.kicad_mod` · 读取器 `kicad_mod_span_y` | ★**有真源** ★ |
| `PQ06` | J_UART 焊盘跨距 (Y 向) | `1.2700` | mm | `[实测]` | KiCad 官方库 `PinHeader_1x02_P1.27mm_Vertical.kicad_mod` · 读取器 `kicad_mod_span_y` | ★**有真源** ★ |
| `PQ07` | TOL["fdm_part"] (FDM 零件公差) | `0.3000` | mm | `[实测]` | `MECH/service_port_check.py` · `TOL['fdm_part']` | ★**有真源** ★ |
| `PQ08` | CRIT (判决阈 = 2 × TOL["fdm_part"]) | `0.6000` | mm | `[推算]` | `MECH/service_port_check.py` · `CRIT = 2 * TOL["fdm_part"]` ⇒ 按源码表达式实算 | ★**有真源** ★ |
| `PQ09` | 检修口 必须清空区 X 宽 | `2.5400` | mm | `[实测]` | `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` · 行正则 `检修口\s*·\s*必须清空区` + 区间正则 `X\s+([0-9.]+)\.\.([0-9.]+)` ⇒ 宽 = 差 | ★**有真源** ★ |
| `PQ10` | 检修口 必须清空区 Y 宽 | `2.5400` | mm | `[实测]` | `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` · 行正则 `检修口\s*·\s*必须清空区` + 区间正则 `Y\s+([0-9.]+)\.\.([0-9.]+)` ⇒ 宽 = 差 | ★**有真源** ★ |
| `PQ11` | 调试口 必须清空区 Y 宽 | `2.5400` | mm | `[实测]` | `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` · 行正则 `调试口\s*·\s*必须清空区` + 区间正则 `Y\s+([0-9.]+)\.\.([0-9.]+)` ⇒ 宽 = 差 | ★**有真源** ★ |
| `PQ12` | 调试口 开口 X 宽 | `10.2000` | mm | `[实测]` | `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` · 行正则 `调试口\s*·\s*开口` + 区间正则 `X\s+([0-9.]+)\.\.([0-9.]+)` ⇒ 宽 = 差 | ★**有真源** ★ |
| `PQ13` | 座体外形宽 X (绝缘体) | `[0数据]` | mm | `[0数据]` | ★**无真值读取点** (★ISS-397 已登记: 三量实测档收样中 ⇒ 至今无真值来源★) | ★**★无真源 ⇒ 前提改了没人知道★** ★ |
| `PQ14` | 座体外形宽 Y (绝缘体) | `[0数据]` | mm | `[0数据]` | ★**无真值读取点** (★ISS-397 同上★) | ★**★无真源 ⇒ 前提改了没人知道★** ★ |
| `PQ15` | 座体外形高 Z (绝缘体) | `[0数据]` | mm | `[0数据]` | ★**无真值读取点** (★ISS-397 同上★) | ★**★无真源 ⇒ 前提改了没人知道★** ★ |
| `PQ16` | 板厚 | `[0数据]` | mm | `[0数据]` | ★**无真值读取点** (★本单未找到可复现的成品板厚真值读取点★) | ★**★无真源 ⇒ 前提改了没人知道★** ★ |
| `PQ17` | 板厂 PTH 环宽绝对下限 (多层 1oz) | `0.1500` | mm | `[官网]` | `MECH/BOARD_ONEPASS_PAD_SIZE_COUPLING.md` 机器块 · `fab_capability → absolute_min_mm` | ★**有真源** ★ |

★**★【D1 的现状病 · 本机实读】★**: ★**17 个前提量里, 4 格 (`PQ13` / `PQ14` / `PQ15` / `PQ16`)【读不出来】⇒ 判据 D1 直接判红 ⇒ 这不是闸故障, 这就是现状** ★
★**★【读点纪律】★**: ★**「当前值」这一列【不许手抄】⇒ 新闸每次跑都按「真值读取点」现读, 与本页登记值逐格对拍 ⇒ 对不上即判红 (★这就是 D1「读不出来 ⇒ 判红」的机器实现★)** ★

★**★【7 个数 · 由前提量推导 (★不是抄的, 是按 §3 的推导式现算的★)】★**

| # | ★数名★ | ★现值★ | ★推导式 (★本页机器块 `seven_number_defs`★)★ |
|---|---|---|---|
| 1 | `j_debug_copper_x` | `4.8100` | `PQ05(跨距) + PQ01(pad)` |
| 2 | `j_uart_copper_x` | `2.2700` | `PQ06(跨距) + PQ01(pad)` |
| 3 | `j_debug_required_clear_x` | `6.6100` | `j_debug_copper_x + 2*(PQ08+PQ07)` |
| 4 | `j_uart_required_clear_x` | `4.0700` | `j_uart_copper_x + 2*(PQ08+PQ07)` |
| 5 | `j_uart_cover_margin_x` | `0.1350` | `(PQ09 - j_uart_copper_x)/2` |
| 6 | `j_debug_opening_margin_x` | `2.6950` | `(PQ12 - j_debug_copper_x)/2` |
| 7 | `j_debug_cover_margin_y` | `0.7700` | `(PQ11 - PQ01)/2` |

==============================================================================
## ★§2 · 写死常量点 · AST 实扫清单 (★判据 D3 的载体★) ★

★**扫描规则 `HC-SCAN-v2` (★可复现·不许手抄·单一事实源★)**: ★**见 `MECH/check_verdict_premise_dependency.py` 的 `scan_gate_constants()` ★**(★真相页与新闸共用同一份实现★) ★

★**R1 (具名)**: 赋值右值, 且目标名匹配几何词表 `GEOM_TOKEN` · ★**R2 (几何路径叶)**: dict/list 字面量的叶, 且点分路径含几何词表匹配 (★例 `official.J_DEBUG.copper.x`★) · ★**R3 / R3' / R4 (几何值比较)**: 出现在 `ast.Compare` / 比较型调用 (`near(...)`) / `dict.get` 默认值里, 且数值落在本仓已登记的几何真值集合 `GEOMETRY_VALUE_SET` 内 ★
★**为什么剔掉别的**: ★**`round(x, 6)` 的进位位 / 切片上限 / 分隔线宽度 / 正则组号 / 90° 旋转角 / 时区小时数 / 数值比对容差 (`TOL = 1e-6`) 【不是几何量】⇒ 不收, 免得淹没真信号** ★ `[推算]`

★**★实扫结果 (★共 26 个写死常量点 · 分布在 4 道判决链闸里★)** ★

| ★HC ID★ | ★闸★ | ★行号★ | ★值 (mm)★ | ★命中规则★ | ★源码上下文 (★逐字★)★ | ★落在依赖图哪条边★ |
|---|---|---|---|---|---|---|
| `HC-001` | `MECH/check_debug_seat_3d_fit.py` | L108 | `1.775000` | `R2` | `DEBUG_CLEAR_X = (1.7750, 4.0850, 4.8100)` | `E01` |
| `HC-002` | `MECH/check_debug_seat_3d_fit.py` | L108 | `4.085000` | `R2` | `DEBUG_CLEAR_X = (1.7750, 4.0850, 4.8100)` | `E01` |
| `HC-003` | `MECH/check_debug_seat_3d_fit.py` | L108 | `4.810000` | `R2` | `DEBUG_CLEAR_X = (1.7750, 4.0850, 4.8100)` | `E01` |
| `HC-004` | `MECH/check_debug_seat_3d_fit.py` | L675 | `0.900000` | `R2` | `"J_DEBUG": {"copper": {"x": 1.775, "y": 0.9},` | `E01` |
| `HC-005` | `MECH/check_debug_seat_3d_fit.py` | L675 | `1.775000` | `R2` | `"J_DEBUG": {"copper": {"x": 1.775, "y": 0.9},` | `E01` |
| `HC-006` | `MECH/check_debug_seat_3d_fit.py` | L678 | `0.775000` | `R2` | `"J_UART": {"copper": {"x": 0.775, "y": 0.9},` | `E01` |
| `HC-007` | `MECH/check_debug_seat_3d_fit.py` | L678 | `0.900000` | `R2` | `"J_UART": {"copper": {"x": 0.775, "y": 0.9},` | `E01` |
| `HC-008` | `MECH/check_debug_seat_3d_fit.py` | L683 | `1.000000` | `R2` | `"J_DEBUG": {"copper": {"x": 4.81, "y": 1.0},` | `E01` |
| `HC-009` | `MECH/check_debug_seat_3d_fit.py` | L683 | `4.810000` | `R2` | `"J_DEBUG": {"copper": {"x": 4.81, "y": 1.0},` | `E01` |
| `HC-010` | `MECH/check_debug_seat_3d_fit.py` | L686 | `1.000000` | `R2` | `"J_UART": {"copper": {"x": 2.27, "y": 1.0},` | `E01` |
| `HC-011` | `MECH/check_debug_seat_3d_fit.py` | L686 | `2.270000` | `R2` | `"J_UART": {"copper": {"x": 2.27, "y": 1.0},` | `E01` |
| `HC-012` | `MECH/check_debug_seat_3d_fit.py` | L731 | `1.775000` | `R2` | `1.7750: "MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L351 (真相页·座体宽 = 板读铜箔宽)",` | `E01` |
| `HC-013` | `MECH/check_debug_seat_3d_fit.py` | L732 | `4.085000` | `R2` | `4.0850: "MECH/BOARD_ONEPASS_MECH_SYNC.md L561 / MECH/BOARD_ONEPASS_MECH_CLAIMS.md L50 / "` | `E01` |
| `HC-014` | `MECH/check_debug_seat_3d_fit.py` | L734 | `4.810000` | `R2` | `4.8100: "MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md §0.1 (官方 THT 真 land·3.81 + 1.00)",` | `E01` |
| `HC-015` | `MECH/check_debug_seat_3d_fit.py` | L737 | `1.775000` | `R2` | `1.7750: "结构件按此数出件 ⇒ 换官方 THT 后铜箔每边超出清空区 1.5175 ⇒ 几何上当场干涉 ⇒ "` | `E01` |
| `HC-016` | `MECH/check_debug_seat_3d_fit.py` | L739 | `4.085000` | `R2` | `4.0850: "结构件按此数出件 ⇒ 换官方 THT 后铜箔每边超出清空区 0.3625 ⇒ 仍干涉 ⇒ "` | `E01` |
| `HC-017` | `MECH/check_debug_seat_3d_fit.py` | L741 | `4.810000` | `R2` | `4.8100: "结构件按此数出件 ⇒ 换官方 THT 后铜箔与清空区齐平 (每边超出 0.0000) ⇒ 几何上不干涉, "` | `E01` |
| `HC-018` | `MECH/check_debug_seat_rework_spec.py` | L118 | `6.610000` | `R1` | `REQUIRED_CLEAR_X = 6.6100` | `E02` |
| `HC-019` | `MECH/check_debug_seat_rework_spec.py` | L120 | `4.810000` | `R1` | `OFFICIAL_DEBUG_COPPER_X = 4.8100` | `E02` |
| `HC-020` | `MECH/check_debug_seat_rework_spec.py` | L122 | `1.000000` | `R1` | `OFFICIAL_COPPER_Y = 1.0000` | `E02` |
| `HC-021` | `MECH/check_jdebug_1p27_clearance.py` | L397 | `1.270000` | `R3'` | `if not near(geo["pitch"], 1.27):` | `E06` |
| `HC-022` | `MECH/check_jdebug_1p27_clearance.py` | L399 | `3.810000` | `R3'` | `if not near(geo["span"], 3.81):` | `E06` |
| `HC-023` | `MECH/check_jdebug_1p27_clearance.py` | L404 | `0.650000` | `R3'` | `if geo["drill"] is None or not near(geo["drill"], 0.65):` | `E06` |
| `HC-024` | `MECH/check_juart_1p27_clearance.py` | L417 | `1.270000` | `R3'` | `if not near(pitch, 1.27):` | `E07` |
| `HC-025` | `MECH/check_juart_1p27_clearance.py` | L837 | `0.600000` | `R4` | `ctx["crit"] = crit.get("crit", 0.60)` | `E07` |
| `HC-026` | `MECH/check_juart_1p27_clearance.py` | L838 | `0.300000` | `R4` | `ctx["fdm_part"] = crit.get("fdm_part", 0.30)` | `E07` |

★**★【9 道闸里有 5 道实扫结果 = 0 ⇒ 它们的「盲」不是同一个根因★】★**: ★**`check_fts_seat_body_geometry.py` / `check_fts_vs_generic_courtyard_delta.py` / `check_fts_seat_sample_plan.py` / `check_connector_clearance_caliber.py` / `check_pad_size_coupling_closed.py` 里【一个几何字面量都没有】⇒ 它们的几何量是从【页/机器块】读的, 不是从【源码常量】读的 ⇒ ★**「盲」的机制是「压根没有通向 KiCad 库的读入口」(★ISS-403 §4.3 已实测: `kicad_mod`/`LIBROOT` 命中数 = 0★) ⇒ ⇒ 【盲闸有两族: 写死族 (E01/E02/E06/E07 · 4 道) 与 无读入口族 (E03/E04/E05/E08/E09 · 5 道)】★ ★ ★

★**★⇒ 判据句**: ★**凡出现在上表里的常量, 都是【闸里写死的板面几何量】⇒ 板面一改, 闸【看不见】⇒ 这就是 ISS-403 那 5 道盲闸的【机械根因】** ★ (`[实测]`)

==============================================================================
## ★§3 · 表 (b) · 依赖图 (★前提量 → 受影响的数 → 受影响的闸 → 受影响的结论 → 谁能重算★) ★

★**读法**: ★**一行 = 一条边 (★前提量组 → 某个闸★) ⇒ 前提量变一格 ⇒ 这一行整体过期 ⇒ 「谁能重算」那列是归属 (★本单不代拍·只摆代价★)** ★
★**粒度说明**: ★**行 = (前提量组 × 判决链闸) ⇒ 因为「写死常量点」是挂在【闸】上的, 一行一闸才能做到「每个写死常量点逐条出现在依赖图里」(★判据 D3★)** ★

| # | ★前提量★ | ★受影响的数 (★名字★)★ | ★受影响的闸 (★判决链闸★)★ | ★写死常量点 (★HC ID★)★ | ★受影响的已签收结论/页★ | ★谁能重算★ |
|---|---|---|---|---|---|---|
| ★**E01**★ | `PQ01`, `PQ02`, `PQ07`, `PQ08`, `PQ09`, `PQ10`, `PQ11`, `PQ12`, `PQ13`, `PQ14`, `PQ15`, `PQ16` | `j_debug_copper_x`<br>`j_uart_copper_x`<br>`j_debug_cover_margin_y` | `MECH/check_debug_seat_3d_fit.py` | `HC-001`<br>`HC-002`<br>`HC-003`<br>`HC-004`<br>`HC-005`<br>`HC-006`<br>`HC-007`<br>`HC-008`<br>`HC-009`<br>`HC-010`<br>`HC-011`<br>`HC-012`<br>`HC-013`<br>`HC-014`<br>`HC-015`<br>`HC-016`<br>`HC-017` | `MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md`<br>`MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` | ★mech-lead (重算) + main (落表)★ |
| ★**E02**★ | `PQ01`, `PQ02`, `PQ07`, `PQ08`, `PQ09`, `PQ11`, `PQ13`, `PQ14`, `PQ15` | `j_debug_required_clear_x`<br>`j_uart_required_clear_x` | `MECH/check_debug_seat_rework_spec.py` | `HC-018`<br>`HC-019`<br>`HC-020` | `MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md`<br>`MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md` | ★mech-lead (重算) + main (落表)★ |
| ★**E03**★ | `PQ01`, `PQ02`, `PQ09`, `PQ11`, `PQ13`, `PQ14`, `PQ15` | `seat_clearance_x`<br>`seat_interference` | `MECH/check_fts_seat_body_geometry.py` | — | `MECH/BOARD_ONEPASS_FTS_SEAT_SAMPLE_MEASURE_PLAN.md` | ★hw-lead (收样实测) + mech-lead (重算)★ |
| ★**E04**★ | `PQ01`, `PQ02`, `PQ13`, `PQ14`, `PQ15` | `courtyard_delta_18` | `MECH/check_fts_vs_generic_courtyard_delta.py` | — | `MECH/BOARD_ONEPASS_FTS_VS_GENERIC_COURTYARD_DELTA.md` | ★mech-lead (重算) + main (落表)★ |
| ★**E05**★ | `PQ01`, `PQ02`, `PQ13`, `PQ14`, `PQ15` | `seat_3q_sample` | `MECH/check_fts_seat_sample_plan.py` | — | `MECH/BOARD_ONEPASS_FTS_SEAT_SAMPLE_MEASURE_PLAN.md` | ★hw-lead (收样实测) + mech-lead (重算)★ |
| ★**E06**★ | `PQ01`, `PQ02`, `PQ03`, `PQ04`, `PQ05`, `PQ07`, `PQ08`, `PQ11`, `PQ12` | `copper_w_along`<br>`per_edge_mm`<br>`annular_ring_mm` | `MECH/check_jdebug_1p27_clearance.py` | `HC-021`<br>`HC-022`<br>`HC-023` | `MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` | ★mech-lead (重算) + main (落表)★ |
| ★**E07**★ | `PQ01`, `PQ02`, `PQ03`, `PQ04`, `PQ06`, `PQ07`, `PQ08`, `PQ09` | `j_uart_cover_margin_x`<br>`j_debug_opening_margin_x`<br>`j_uart_required_clear_x` | `MECH/check_juart_1p27_clearance.py` | `HC-024`<br>`HC-025`<br>`HC-026` | `MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md` | ★mech-lead (重算) + main (落表)★ |
| ★**E08**★ | `PQ01`, `PQ02`, `PQ07`, `PQ08`, `PQ09`, `PQ10`, `PQ11`, `PQ12` | `connector_clearance_caliber` | `MECH/check_connector_clearance_caliber.py` | — | `MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md` | ★mech-lead (重算) + main (落表)★ |
| ★**E09**★ | `PQ01`, `PQ02`, `PQ03`, `PQ04`, `PQ05`, `PQ06`, `PQ07`, `PQ08`, `PQ17` | `seven_numbers_matrix`<br>`pad_tier`<br>`annular_ring` | `MECH/check_pad_size_coupling_closed.py` | — | `MECH/BOARD_ONEPASS_PAD_SIZE_COUPLING.md`<br>`HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md` | ★hw-lead (板侧) + mech-lead (重算) + main (拍档)★ |
| ★**E10**★ | `PQ03` | `annular_ring_lib` | — (无闸直接消费) | — | `HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md` | ★hw-lead (板侧) + main (拍)★ |
| ★**E11**★ | `PQ05`, `PQ06` | `j_debug_copper_x`<br>`j_uart_copper_x` | — (无闸直接消费) | — | `MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` | ★mech-lead (重算)★ |
| ★**E12**★ | `PQ09`, `PQ10`, `PQ11`, `PQ12` | `j_uart_cover_margin_x`<br>`j_debug_opening_margin_x`<br>`j_debug_cover_margin_y` | — (无闸直接消费) | — | `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` | ★mech-lead (重算) + main (落表)★ |
| ★**E13**★ | `PQ16` | `seat_z_fit` | — (无闸直接消费) | — | `MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md` | ★mech-lead (重算) + main (拍板厚)★ |
| ★**E14**★ | `PQ17` | `fab_annular_min` | — (无闸直接消费) | — | `MECH/BOARD_ONEPASS_PAD_SIZE_COUPLING.md` | ★main (定板厂/拍档) + hw-lead (落板)★ |
| ★**E15**★ | `PQ13`, `PQ14`, `PQ15` | `seat_clearance_x`<br>`seat_3q_sample`<br>`courtyard_delta_18` | — (无闸直接消费) | — | `MECH/BOARD_ONEPASS_FTS_SEAT_SAMPLE_MEASURE_PLAN.md` | ★hw-lead (收样) + mech-lead (重算) + main (落档)★ |

★**★【D2 的现状病】★**: ★**17 个前提量里, 4 个 (`PQ13` / `PQ14` / `PQ15` / `PQ16`) 在本图里只能挂到「三量收样」这一层, 挂不到具体数字 ⇒ 它们【登记了但没人用得上】⇒ 这本身就是「座体三量至今 `[0数据]`」在依赖图上的样子** ★ `[实测]`

==============================================================================
## ★§4 · 表 (c) · 作废传播矩阵 (★前提变一格 ⇒ 哪些格子从绿变红★) ★

★**记法**: ★**行 = 前提量变的那一格; `▲` = 该格从绿变红 (值过期, 必须重算); `●` = 该格【本就已经红】(变一格只是红得更红, 不构成新信息); `—` = 不受影响** ★

| ★前提变化 (★一行 = 一次改动作★) | ★受影响的数 (★旧 → 新·★实算★)★ | ★受影响的闸 (★变盲/变红★)★ | ★受影响的已签收结论★ |
|---|---|---|---|
| ★**焊盘 PQ01/PQ02  1.000 → 1.110**★ | ▲`j_debug_copper_x` `4.8100` → `4.9200`<br>▲`j_uart_copper_x` `2.2700` → `2.3800`<br>▲`j_debug_required_clear_x` `6.6100` → `6.7200`<br>▲`j_uart_required_clear_x` `4.0700` → `4.1800`<br>▲`j_uart_cover_margin_x` `0.1350` → `0.0800`<br>▲`j_debug_opening_margin_x` `2.6950` → `2.6400`<br>▲`j_debug_cover_margin_y` `0.7700` → `0.7150` | `MECH/check_debug_seat_3d_fit.py`<br>`MECH/check_debug_seat_rework_spec.py`<br>`MECH/check_fts_seat_body_geometry.py`<br>`MECH/check_fts_vs_generic_courtyard_delta.py`<br>`MECH/check_fts_seat_sample_plan.py`<br>`MECH/check_jdebug_1p27_clearance.py`<br>`MECH/check_juart_1p27_clearance.py`<br>`MECH/check_connector_clearance_caliber.py` | `MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md`<br>`MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md`<br>`MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md`<br>`MECH/BOARD_ONEPASS_PAD_SIZE_COUPLING.md` |
| ★**规划钻孔 PQ04  0.71 → 0.65**★ | ▲`annular_ring`<br>▲`seven_numbers_matrix` | `MECH/check_pad_size_coupling_closed.py`<br>`MECH/check_jdebug_1p27_clearance.py`<br>`MECH/check_juart_1p27_clearance.py` | `MECH/BOARD_ONEPASS_PAD_SIZE_COUPLING.md`<br>`HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md` |
| ★**座体三量 PQ13/PQ14/PQ15 (实测档到手)**★ | ▲`seat_clearance_x`<br>▲`seat_3q_sample`<br>▲`courtyard_delta_18` | `MECH/check_fts_seat_body_geometry.py`<br>`MECH/check_fts_seat_sample_plan.py`<br>`MECH/check_fts_vs_generic_courtyard_delta.py` | `MECH/BOARD_ONEPASS_FTS_SEAT_SAMPLE_MEASURE_PLAN.md` |
| ★**清空区/开口 PQ09~PQ12 改一格**★ | ▲`j_uart_cover_margin_x` `0.1350`<br>▲`j_debug_opening_margin_x` `2.6950`<br>▲`j_debug_cover_margin_y` `0.7700` | `MECH/check_debug_seat_3d_fit.py`<br>`MECH/check_debug_seat_rework_spec.py`<br>`MECH/check_jdebug_1p27_clearance.py`<br>`MECH/check_juart_1p27_clearance.py`<br>`MECH/check_connector_clearance_caliber.py` | `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md`<br>`MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md`<br>`MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md` |
| ★**判决阈 PQ07/PQ08 改一格**★ | ▲`j_debug_required_clear_x` `6.6100`<br>▲`j_uart_required_clear_x` `4.0700`<br>▲`j_uart_cover_margin_x` `0.1350`<br>▲`j_debug_opening_margin_x` `2.6950`<br>▲`j_debug_cover_margin_y` `0.7700` | `MECH/check_debug_seat_3d_fit.py`<br>`MECH/check_debug_seat_rework_spec.py`<br>`MECH/check_jdebug_1p27_clearance.py`<br>`MECH/check_juart_1p27_clearance.py`<br>`MECH/check_connector_clearance_caliber.py` | `MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md`<br>`MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md`<br>`MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md` |
| ★**板厚 PQ16 定档**★ | ▲`seat_z_fit` | `MECH/check_debug_seat_3d_fit.py` | `MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md` |
| ★**板厂能力 PQ17 改一格 (或换板厂)**★ | ▲`fab_annular_min` | `MECH/check_pad_size_coupling_closed.py` | `MECH/BOARD_ONEPASS_PAD_SIZE_COUPLING.md` |

★**`M1`**: ★**ISS-403 已 A/B 实测 7 道闸: 5 道对焊盘尺寸【完全盲】(两臂 stdout md5 逐字相同) + 2 道会转红 (jdebug G1~G4 / juart J0/J1/J5/J7); 本单依赖图覆盖 9 道 (多出的 check_fts_seat_sample_plan.py 与 check_pad_size_coupling_closed.py 未做过 A/B)** ★
★**`M2`**: ★**环宽口径翻转: (1.000−0.71)/2=0.1450 → (1.000−0.65)/2=0.1750 ⇒ 环宽这一格由红转绿** ★
★**`M3`**: ★**这三道闸【第一次有真值可判】⇒ 前提从 `[0数据]` 变有源, 是【新增判据】不是【作废】** ★
★**`M4`**: ★**清空区宽是【座体支配】, 与焊盘无关 ⇒ 改焊盘不会改它, 改座体才会** ★
★**`M5`**: ★**阈值一改 ⇒ 所有「最坏 = 余量 − TOL」的过阈结论同时重判** ★
★**`M6`**: ★**Z 向基准 ⇒ 只影响 3D 装配那一道闸** ★
★**`M7`**: ★**这是【门限】不是【被测值】⇒ 板厂换人 ⇒ 全部 pad 档位结论重排** ★

★**★⇒ 本表与 ISS-403 的关系 (★不重复·是它的通用版★) ★**:
★**ISS-403 只查了【焊盘尺寸】这一个前提 (`M1`) ⇒ 本表把它扩成 7 行 (7 个前提量各一行) ⇒ ★**任何一行都能按同一套机器判据验: 矩阵里每一格都必须能在 §3 依赖图里找到对应边 (★判据 D4★)** ★

==============================================================================
## ★§5 · 新闸怎么把上面三张表变成「机器可判」 (★判据 D1~D6 的机器实现★) ★

| ★判据★ | ★机器实现 (★新闸 `MECH/check_verdict_premise_dependency.py`★)★ |
|---|---|
| ★**D1**★ 前提量清单可机器重建 | ★新闸按 §1「真值读取点」**现读**每个前提量 (★kicad_mod 正则 / md 行区间 / py 常量 / 机器块转引★) ⇒ 与本页登记值逐格对拍 ⇒ ★**读不出来 ⇒ 判红** (★现状: 4 格红★) ★ |
| ★**D2**★ 依赖图自洽 | ★每个前提 ID 必须在 §3 依赖图里至少挂到 1 条边 ⇒ ★**孤立前提量 ⇒ 判红** ★ |
| ★**D3**★ 写死常量点必须进依赖图 | ★新闸按规则 `HC-SCAN-v2` 对 9 道判决链闸 **AST 实扫** ⇒ 每个字面量出现点 (★gate+行+值★) 必须在本页机器块 `hardcoded_constants` 里登记 **且** 被 §3 依赖图某行的「写死常量点」栏引用 ⇒ ★**漏一条 ⇒ 判红** ★ |
| ★**D4**★ 矩阵与依赖图一致 | ★§4 每行的每个格子, 必须能在 §3 依赖图里找到对应边 (★该边的目标含它, 且与该行至少共享一个前提量★) ⇒ ★**矩阵多一格/少一格 ⇒ 判红** ★ |
| ★**D5**★ 板三证不动 | ★板 / 网表 / 脚表 / BOM 的 md5 与基线逐字相同 (★板 md5 = `611b869e13518c3c023fb178f91a0075`★) ⇒ ★**任何一个动了 ⇒ 判红** ★ |
| ★**D6**★ 零挂链 + 零外发 + 证据分级 | ★`grep -c check_verdict_premise_dependency state/gate_check.py` = 0 ⇒ ★`state/outbox/` 树摘要与基线逐字相同 ⇒ ★每条结论带 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` 五级之一 ⇒ ★**任一不满足 ⇒ 判红** ★ |

★**★【本闸的两种跑法】★**: ★**① 裸跑 `python3 MECH/check_verdict_premise_dependency.py` ⇒ ★**rc=1** (★红的是现状: 4 格前提无真源★) · ★**② `--selftest` ⇒ rc=0 · 末行逐字 `ALL TESTS PASS` (★正向 2 + 反向 12★)** ★

==============================================================================
## ★§6 · 边界自证 (★逐条·★本机实跑★) ★

| 边界 | 自证方式 | 读数 |
|---|---|---|
| ★**零写板** ★ | `md5sum` + `stat` 三项 | ★`611b869e13518c3c023fb178f91a0075` / `2026-11-06 07:07:17.362193413` / `4940213` ⇒ 与基线**逐字节相同** ★ |
| ★**零落表** ★ | 网表/脚表/BOM md5 | ★`6aee500e60ba0732f83a9cf557ba90ab` / `9174309df1ec9411ac8e8d9e80ee386a` / `5b9993992405904a60ac96a020b375d8` ⇒ 与基线逐字相同; ★`mech.yaml` 由本单单写 (★走 `state/frag_write.py`★) ★ |
| ★**零改既有闸判据/阈值** ★ | 9 道判决链闸 + ISS-393/397/399/400/403/405 交卷的 6 道闸源码 md5 对拍 | ★开工前/收工后**逐字相同** (★见交卷页 B6/B7★) ★ |
| ★**零改既有页正文** ★ | 6 张既有页 md5 对拍 | ★**逐字相同** (★见交卷页 B7★) ★ |
| ★**零挂链** ★ | `grep -c check_verdict_premise_dependency state/gate_check.py` | ★**0** ★ |
| ★**零外发** ★ | `state/outbox/` 全树摘要 | ★22 个文件 · 树摘要 `7c5f45e922447340349a224cf05a9807` ⇒ 与基线**逐字节相同** ⇒ ★**本单没发任何邮件/询价/问询/采购** ★ |
| ★**不代拍** ★ | 机器块 `decision_taken_here` | ★`"not_decided_here"` ★ |
| ★**不自签** ★ | `state/issue_log.yaml` | ★**一行没写** (★ISS-407 的签收归 main★) ★ |
| ★**沙盒只落项目盘** ★ | 沙盒路径 | ★`tmp/iss407/` (★未向系统 `/tmp` 写任何字节★) ★ |

==============================================================================
## ★§7 · 未决项 (★一条都不代拍·★全部 to=main★) ★

| ID | 未决项 | 归属 |
|---|---|---|
| `OI-407-1` | 「板那一趟」开工前要不要按依赖图逐项过一遍前提值 | main |
| `OI-407-2` | 焊盘档拍下后必须同批重算的几个数是谁的活 | main |
| `OI-407-3` | 写死常量点要不要改成「现读板面」(判据口径变更) | main |
| `OI-407-4` | 作废传播矩阵要不要挂成投板前的硬清单 | main |
| `OI-407-5` | 本闸自己挂不挂链 (自指悖论) | main |

★**★【自指悖论 · 本单【不自己解决】★】★**: ★**`MECH/check_verdict_premise_dependency.py` 自己也不在链上 (★D6 自证 `grep -c` = 0★) ⇒ 它同样需要被登记 (★在 `state/gate_check.py` 链上 或 人工签核台账里★) ⇒ ★**而那一步在 main 地界 (★改 `state/gate_check.py` = 改已签收件★) ⇒ 本单【不挂链】⇒ 台账里「本闸自身」这一行写 `待 main 挂链` ⇒ 交 main 裁决** ★

==============================================================================
## ★§8 · 机器块 (★可被 `MECH/check_verdict_premise_dependency.py` 解析★) ★

```json
{
  "doc": "ISS-407 · MECH 判决链前提依赖图 + 作废传播矩阵 · 机读块",
  "generated_by": "mech-lead · 2026-11-25 · 本机实读/实扫 (零写板/零落表/零挂链/零外发)",
  "evidence_levels": [
    "官网",
    "实测",
    "媒体",
    "推算",
    "0数据"
  ],
  "hc_scan_rule": "HC-SCAN-v2",
  "hc_scan_gates": [
    "MECH/check_debug_seat_3d_fit.py",
    "MECH/check_debug_seat_rework_spec.py",
    "MECH/check_fts_seat_body_geometry.py",
    "MECH/check_fts_vs_generic_courtyard_delta.py",
    "MECH/check_fts_seat_sample_plan.py",
    "MECH/check_jdebug_1p27_clearance.py",
    "MECH/check_juart_1p27_clearance.py",
    "MECH/check_connector_clearance_caliber.py",
    "MECH/check_pad_size_coupling_closed.py"
  ],
  "premise_quantities": [
    {
      "id": "PQ01",
      "name": "排针焊盘 X 尺寸",
      "unit": "mm",
      "evidence": "实测",
      "read_point": {
        "kind": "kicad_mod_pad_x",
        "path": "/home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty/PinHeader_1x04_P1.27mm_Vertical.kicad_mod"
      },
      "note": "官方 KiCad 库 THT 排针封装",
      "current_value": 1.0,
      "read_status": "有真源",
      "read_error": ""
    },
    {
      "id": "PQ02",
      "name": "排针焊盘 Y 尺寸",
      "unit": "mm",
      "evidence": "实测",
      "read_point": {
        "kind": "kicad_mod_pad_y",
        "path": "/home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty/PinHeader_1x04_P1.27mm_Vertical.kicad_mod"
      },
      "note": "同上",
      "current_value": 1.0,
      "read_status": "有真源",
      "read_error": ""
    },
    {
      "id": "PQ03",
      "name": "库件默认钻孔",
      "unit": "mm",
      "evidence": "实测",
      "read_point": {
        "kind": "kicad_mod_drill",
        "path": "/home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty/PinHeader_1x04_P1.27mm_Vertical.kicad_mod"
      },
      "note": "第三方库件默认值, 不是厂件规格",
      "current_value": 0.65,
      "read_status": "有真源",
      "read_error": ""
    },
    {
      "id": "PQ04",
      "name": "「板那一趟」规划钻孔",
      "unit": "mm",
      "evidence": "官网",
      "read_point": {
        "kind": "md_first_number",
        "path": "HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md",
        "pattern": "0\\.71"
      },
      "note": "Samtec 官方推荐 PCB 图 `.028 0.71 (TYP)` 逐字",
      "current_value": 0.71,
      "read_status": "有真源",
      "read_error": ""
    },
    {
      "id": "PQ05",
      "name": "J_DEBUG 焊盘跨距 (Y 向)",
      "unit": "mm",
      "evidence": "实测",
      "read_point": {
        "kind": "kicad_mod_span_y",
        "path": "/home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty/PinHeader_1x04_P1.27mm_Vertical.kicad_mod"
      },
      "note": "1x04 封装 4 个 pad 的 Y 向跨距",
      "current_value": 3.81,
      "read_status": "有真源",
      "read_error": ""
    },
    {
      "id": "PQ06",
      "name": "J_UART 焊盘跨距 (Y 向)",
      "unit": "mm",
      "evidence": "实测",
      "read_point": {
        "kind": "kicad_mod_span_y",
        "path": "/home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty/PinHeader_1x02_P1.27mm_Vertical.kicad_mod"
      },
      "note": "1x02 封装 2 个 pad 的 Y 向跨距",
      "current_value": 1.27,
      "read_status": "有真源",
      "read_error": ""
    },
    {
      "id": "PQ07",
      "name": "TOL[\"fdm_part\"] (FDM 零件公差)",
      "unit": "mm",
      "evidence": "实测",
      "read_point": {
        "kind": "py_dict_value",
        "path": "MECH/service_port_check.py",
        "var": "TOL",
        "key": "fdm_part"
      },
      "note": "MECH 口径真值表",
      "current_value": 0.3,
      "read_status": "有真源",
      "read_error": ""
    },
    {
      "id": "PQ08",
      "name": "CRIT (判决阈 = 2 × TOL[\"fdm_part\"])",
      "unit": "mm",
      "evidence": "推算",
      "read_point": {
        "kind": "py_crit",
        "path": "MECH/service_port_check.py"
      },
      "note": "按源码表达式实算, 不抄常量",
      "current_value": 0.6,
      "read_status": "有真源",
      "read_error": ""
    },
    {
      "id": "PQ09",
      "name": "检修口 必须清空区 X 宽",
      "unit": "mm",
      "evidence": "实测",
      "read_point": {
        "kind": "md_range_width",
        "path": "MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md",
        "line_pattern": "检修口\\s*·\\s*必须清空区",
        "range_pattern": "X\\s+([0-9.]+)\\.\\.([0-9.]+)"
      },
      "note": "座体支配, 固定值, 不随铜箔走",
      "current_value": 2.54,
      "read_status": "有真源",
      "read_error": ""
    },
    {
      "id": "PQ10",
      "name": "检修口 必须清空区 Y 宽",
      "unit": "mm",
      "evidence": "实测",
      "read_point": {
        "kind": "md_range_width",
        "path": "MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md",
        "line_pattern": "检修口\\s*·\\s*必须清空区",
        "range_pattern": "Y\\s+([0-9.]+)\\.\\.([0-9.]+)"
      },
      "note": "同上",
      "current_value": 2.54,
      "read_status": "有真源",
      "read_error": ""
    },
    {
      "id": "PQ11",
      "name": "调试口 必须清空区 Y 宽",
      "unit": "mm",
      "evidence": "实测",
      "read_point": {
        "kind": "md_range_width",
        "path": "MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md",
        "line_pattern": "调试口\\s*·\\s*必须清空区",
        "range_pattern": "Y\\s+([0-9.]+)\\.\\.([0-9.]+)"
      },
      "note": "同上",
      "current_value": 2.54,
      "read_status": "有真源",
      "read_error": ""
    },
    {
      "id": "PQ12",
      "name": "调试口 开口 X 宽",
      "unit": "mm",
      "evidence": "实测",
      "read_point": {
        "kind": "md_range_width",
        "path": "MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md",
        "line_pattern": "调试口\\s*·\\s*开口",
        "range_pattern": "X\\s+([0-9.]+)\\.\\.([0-9.]+)"
      },
      "note": "开口 (居中解)",
      "current_value": 10.2,
      "read_status": "有真源",
      "read_error": ""
    },
    {
      "id": "PQ13",
      "name": "座体外形宽 X (绝缘体)",
      "unit": "mm",
      "evidence": "0数据",
      "read_point": {
        "kind": "missing"
      },
      "note": "ISS-397 已登记: 三量实测档收样中 ⇒ 至今无真值来源",
      "current_value": "[0数据]",
      "read_status": "无真源",
      "read_error": "无真值读取点 (kind=missing)"
    },
    {
      "id": "PQ14",
      "name": "座体外形宽 Y (绝缘体)",
      "unit": "mm",
      "evidence": "0数据",
      "read_point": {
        "kind": "missing"
      },
      "note": "ISS-397 同上",
      "current_value": "[0数据]",
      "read_status": "无真源",
      "read_error": "无真值读取点 (kind=missing)"
    },
    {
      "id": "PQ15",
      "name": "座体外形高 Z (绝缘体)",
      "unit": "mm",
      "evidence": "0数据",
      "read_point": {
        "kind": "missing"
      },
      "note": "ISS-397 同上",
      "current_value": "[0数据]",
      "read_status": "无真源",
      "read_error": "无真值读取点 (kind=missing)"
    },
    {
      "id": "PQ16",
      "name": "板厚",
      "unit": "mm",
      "evidence": "0数据",
      "read_point": {
        "kind": "missing"
      },
      "note": "本单未找到可复现的成品板厚真值读取点",
      "current_value": "[0数据]",
      "read_status": "无真源",
      "read_error": "无真值读取点 (kind=missing)"
    },
    {
      "id": "PQ17",
      "name": "板厂 PTH 环宽绝对下限 (多层 1oz)",
      "unit": "mm",
      "evidence": "官网",
      "read_point": {
        "kind": "json_block_value",
        "path": "MECH/BOARD_ONEPASS_PAD_SIZE_COUPLING.md",
        "pointer": [
          "fab_capability",
          "absolute_min_mm"
        ]
      },
      "note": "JLCPCB 官方能力表逐字 · 经 ISS-403 已签收机器块转引",
      "current_value": 0.15,
      "read_status": "有真源",
      "read_error": ""
    }
  ],
  "seven_number_defs": {
    "j_debug_copper_x": "PQ05(跨距) + PQ01(pad)",
    "j_uart_copper_x": "PQ06(跨距) + PQ01(pad)",
    "j_debug_required_clear_x": "j_debug_copper_x + 2*(PQ08+PQ07)",
    "j_uart_required_clear_x": "j_uart_copper_x + 2*(PQ08+PQ07)",
    "j_uart_cover_margin_x": "(PQ09 - j_uart_copper_x)/2",
    "j_debug_opening_margin_x": "(PQ12 - j_debug_copper_x)/2",
    "j_debug_cover_margin_y": "(PQ11 - PQ01)/2"
  },
  "seven_numbers_current": {
    "j_debug_copper_x": 4.81,
    "j_uart_copper_x": 2.27,
    "j_debug_required_clear_x": 6.61,
    "j_uart_required_clear_x": 4.07,
    "j_uart_cover_margin_x": 0.135,
    "j_debug_opening_margin_x": 2.695,
    "j_debug_cover_margin_y": 0.77
  },
  "dependency_graph": [
    {
      "id": "E01",
      "premises": [
        "PQ01",
        "PQ02",
        "PQ07",
        "PQ08",
        "PQ09",
        "PQ10",
        "PQ11",
        "PQ12",
        "PQ13",
        "PQ14",
        "PQ15",
        "PQ16"
      ],
      "numbers": [
        "j_debug_copper_x",
        "j_uart_copper_x",
        "j_debug_cover_margin_y"
      ],
      "gates": [
        "MECH/check_debug_seat_3d_fit.py"
      ],
      "conclusions": [
        "MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md",
        "MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md"
      ],
      "owner": "mech-lead (重算) + main (落表)",
      "hardcoded_constant_ids": [
        "HC-001",
        "HC-002",
        "HC-003",
        "HC-004",
        "HC-005",
        "HC-006",
        "HC-007",
        "HC-008",
        "HC-009",
        "HC-010",
        "HC-011",
        "HC-012",
        "HC-013",
        "HC-014",
        "HC-015",
        "HC-016",
        "HC-017"
      ]
    },
    {
      "id": "E02",
      "premises": [
        "PQ01",
        "PQ02",
        "PQ07",
        "PQ08",
        "PQ09",
        "PQ11",
        "PQ13",
        "PQ14",
        "PQ15"
      ],
      "numbers": [
        "j_debug_required_clear_x",
        "j_uart_required_clear_x"
      ],
      "gates": [
        "MECH/check_debug_seat_rework_spec.py"
      ],
      "conclusions": [
        "MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md",
        "MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md"
      ],
      "owner": "mech-lead (重算) + main (落表)",
      "hardcoded_constant_ids": [
        "HC-018",
        "HC-019",
        "HC-020"
      ]
    },
    {
      "id": "E03",
      "premises": [
        "PQ01",
        "PQ02",
        "PQ09",
        "PQ11",
        "PQ13",
        "PQ14",
        "PQ15"
      ],
      "numbers": [
        "seat_clearance_x",
        "seat_interference"
      ],
      "gates": [
        "MECH/check_fts_seat_body_geometry.py"
      ],
      "conclusions": [
        "MECH/BOARD_ONEPASS_FTS_SEAT_SAMPLE_MEASURE_PLAN.md"
      ],
      "owner": "hw-lead (收样实测) + mech-lead (重算)"
    },
    {
      "id": "E04",
      "premises": [
        "PQ01",
        "PQ02",
        "PQ13",
        "PQ14",
        "PQ15"
      ],
      "numbers": [
        "courtyard_delta_18"
      ],
      "gates": [
        "MECH/check_fts_vs_generic_courtyard_delta.py"
      ],
      "conclusions": [
        "MECH/BOARD_ONEPASS_FTS_VS_GENERIC_COURTYARD_DELTA.md"
      ],
      "owner": "mech-lead (重算) + main (落表)"
    },
    {
      "id": "E05",
      "premises": [
        "PQ01",
        "PQ02",
        "PQ13",
        "PQ14",
        "PQ15"
      ],
      "numbers": [
        "seat_3q_sample"
      ],
      "gates": [
        "MECH/check_fts_seat_sample_plan.py"
      ],
      "conclusions": [
        "MECH/BOARD_ONEPASS_FTS_SEAT_SAMPLE_MEASURE_PLAN.md"
      ],
      "owner": "hw-lead (收样实测) + mech-lead (重算)"
    },
    {
      "id": "E06",
      "premises": [
        "PQ01",
        "PQ02",
        "PQ03",
        "PQ04",
        "PQ05",
        "PQ07",
        "PQ08",
        "PQ11",
        "PQ12"
      ],
      "numbers": [
        "copper_w_along",
        "per_edge_mm",
        "annular_ring_mm"
      ],
      "gates": [
        "MECH/check_jdebug_1p27_clearance.py"
      ],
      "conclusions": [
        "MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md"
      ],
      "owner": "mech-lead (重算) + main (落表)",
      "hardcoded_constant_ids": [
        "HC-021",
        "HC-022",
        "HC-023"
      ]
    },
    {
      "id": "E07",
      "premises": [
        "PQ01",
        "PQ02",
        "PQ03",
        "PQ04",
        "PQ06",
        "PQ07",
        "PQ08",
        "PQ09"
      ],
      "numbers": [
        "j_uart_cover_margin_x",
        "j_debug_opening_margin_x",
        "j_uart_required_clear_x"
      ],
      "gates": [
        "MECH/check_juart_1p27_clearance.py"
      ],
      "conclusions": [
        "MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md"
      ],
      "owner": "mech-lead (重算) + main (落表)",
      "hardcoded_constant_ids": [
        "HC-024",
        "HC-025",
        "HC-026"
      ]
    },
    {
      "id": "E08",
      "premises": [
        "PQ01",
        "PQ02",
        "PQ07",
        "PQ08",
        "PQ09",
        "PQ10",
        "PQ11",
        "PQ12"
      ],
      "numbers": [
        "connector_clearance_caliber"
      ],
      "gates": [
        "MECH/check_connector_clearance_caliber.py"
      ],
      "conclusions": [
        "MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md"
      ],
      "owner": "mech-lead (重算) + main (落表)"
    },
    {
      "id": "E09",
      "premises": [
        "PQ01",
        "PQ02",
        "PQ03",
        "PQ04",
        "PQ05",
        "PQ06",
        "PQ07",
        "PQ08",
        "PQ17"
      ],
      "numbers": [
        "seven_numbers_matrix",
        "pad_tier",
        "annular_ring"
      ],
      "gates": [
        "MECH/check_pad_size_coupling_closed.py"
      ],
      "conclusions": [
        "MECH/BOARD_ONEPASS_PAD_SIZE_COUPLING.md",
        "HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md"
      ],
      "owner": "hw-lead (板侧) + mech-lead (重算) + main (拍档)"
    },
    {
      "id": "E10",
      "premises": [
        "PQ03"
      ],
      "numbers": [
        "annular_ring_lib"
      ],
      "gates": [],
      "conclusions": [
        "HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md"
      ],
      "owner": "hw-lead (板侧) + main (拍)"
    },
    {
      "id": "E11",
      "premises": [
        "PQ05",
        "PQ06"
      ],
      "numbers": [
        "j_debug_copper_x",
        "j_uart_copper_x"
      ],
      "gates": [],
      "conclusions": [
        "MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md"
      ],
      "owner": "mech-lead (重算)"
    },
    {
      "id": "E12",
      "premises": [
        "PQ09",
        "PQ10",
        "PQ11",
        "PQ12"
      ],
      "numbers": [
        "j_uart_cover_margin_x",
        "j_debug_opening_margin_x",
        "j_debug_cover_margin_y"
      ],
      "gates": [],
      "conclusions": [
        "MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md"
      ],
      "owner": "mech-lead (重算) + main (落表)"
    },
    {
      "id": "E13",
      "premises": [
        "PQ16"
      ],
      "numbers": [
        "seat_z_fit"
      ],
      "gates": [],
      "conclusions": [
        "MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md"
      ],
      "owner": "mech-lead (重算) + main (拍板厚)"
    },
    {
      "id": "E14",
      "premises": [
        "PQ17"
      ],
      "numbers": [
        "fab_annular_min"
      ],
      "gates": [],
      "conclusions": [
        "MECH/BOARD_ONEPASS_PAD_SIZE_COUPLING.md"
      ],
      "owner": "main (定板厂/拍档) + hw-lead (落板)"
    },
    {
      "id": "E15",
      "premises": [
        "PQ13",
        "PQ14",
        "PQ15"
      ],
      "numbers": [
        "seat_clearance_x",
        "seat_3q_sample",
        "courtyard_delta_18"
      ],
      "gates": [],
      "conclusions": [
        "MECH/BOARD_ONEPASS_FTS_SEAT_SAMPLE_MEASURE_PLAN.md"
      ],
      "owner": "hw-lead (收样) + mech-lead (重算) + main (落档)"
    }
  ],
  "hardcoded_constants": [
    {
      "id": "HC-001",
      "gate": "MECH/check_debug_seat_3d_fit.py",
      "line": 108,
      "value": 1.775,
      "rules": [
        "R2"
      ],
      "ctx": "DEBUG_CLEAR_X[0]",
      "text": "DEBUG_CLEAR_X = (1.7750, 4.0850, 4.8100)",
      "edge": "E01"
    },
    {
      "id": "HC-002",
      "gate": "MECH/check_debug_seat_3d_fit.py",
      "line": 108,
      "value": 4.085,
      "rules": [
        "R2"
      ],
      "ctx": "DEBUG_CLEAR_X[1]",
      "text": "DEBUG_CLEAR_X = (1.7750, 4.0850, 4.8100)",
      "edge": "E01"
    },
    {
      "id": "HC-003",
      "gate": "MECH/check_debug_seat_3d_fit.py",
      "line": 108,
      "value": 4.81,
      "rules": [
        "R2"
      ],
      "ctx": "DEBUG_CLEAR_X[2]",
      "text": "DEBUG_CLEAR_X = (1.7750, 4.0850, 4.8100)",
      "edge": "E01"
    },
    {
      "id": "HC-004",
      "gate": "MECH/check_debug_seat_3d_fit.py",
      "line": 675,
      "value": 0.9,
      "rules": [
        "R2"
      ],
      "ctx": "status.J_DEBUG.copper.y",
      "text": "\"J_DEBUG\": {\"copper\": {\"x\": 1.775, \"y\": 0.9},",
      "edge": "E01"
    },
    {
      "id": "HC-005",
      "gate": "MECH/check_debug_seat_3d_fit.py",
      "line": 675,
      "value": 1.775,
      "rules": [
        "R2"
      ],
      "ctx": "status.J_DEBUG.copper.x",
      "text": "\"J_DEBUG\": {\"copper\": {\"x\": 1.775, \"y\": 0.9},",
      "edge": "E01"
    },
    {
      "id": "HC-006",
      "gate": "MECH/check_debug_seat_3d_fit.py",
      "line": 678,
      "value": 0.775,
      "rules": [
        "R2"
      ],
      "ctx": "status.J_UART.copper.x",
      "text": "\"J_UART\": {\"copper\": {\"x\": 0.775, \"y\": 0.9},",
      "edge": "E01"
    },
    {
      "id": "HC-007",
      "gate": "MECH/check_debug_seat_3d_fit.py",
      "line": 678,
      "value": 0.9,
      "rules": [
        "R2"
      ],
      "ctx": "status.J_UART.copper.y",
      "text": "\"J_UART\": {\"copper\": {\"x\": 0.775, \"y\": 0.9},",
      "edge": "E01"
    },
    {
      "id": "HC-008",
      "gate": "MECH/check_debug_seat_3d_fit.py",
      "line": 683,
      "value": 1.0,
      "rules": [
        "R2"
      ],
      "ctx": "official.J_DEBUG.copper.y",
      "text": "\"J_DEBUG\": {\"copper\": {\"x\": 4.81, \"y\": 1.0},",
      "edge": "E01"
    },
    {
      "id": "HC-009",
      "gate": "MECH/check_debug_seat_3d_fit.py",
      "line": 683,
      "value": 4.81,
      "rules": [
        "R2"
      ],
      "ctx": "official.J_DEBUG.copper.x",
      "text": "\"J_DEBUG\": {\"copper\": {\"x\": 4.81, \"y\": 1.0},",
      "edge": "E01"
    },
    {
      "id": "HC-010",
      "gate": "MECH/check_debug_seat_3d_fit.py",
      "line": 686,
      "value": 1.0,
      "rules": [
        "R2"
      ],
      "ctx": "official.J_UART.copper.y",
      "text": "\"J_UART\": {\"copper\": {\"x\": 2.27, \"y\": 1.0},",
      "edge": "E01"
    },
    {
      "id": "HC-011",
      "gate": "MECH/check_debug_seat_3d_fit.py",
      "line": 686,
      "value": 2.27,
      "rules": [
        "R2"
      ],
      "ctx": "official.J_UART.copper.x",
      "text": "\"J_UART\": {\"copper\": {\"x\": 2.27, \"y\": 1.0},",
      "edge": "E01"
    },
    {
      "id": "HC-012",
      "gate": "MECH/check_debug_seat_3d_fit.py",
      "line": 731,
      "value": 1.775,
      "rules": [
        "R2"
      ],
      "ctx": "clear_src.1.775",
      "text": "1.7750: \"MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L351 (真相页·座体宽 = 板读铜箔宽)\",",
      "edge": "E01"
    },
    {
      "id": "HC-013",
      "gate": "MECH/check_debug_seat_3d_fit.py",
      "line": 732,
      "value": 4.085,
      "rules": [
        "R2"
      ],
      "ctx": "clear_src.4.085",
      "text": "4.0850: \"MECH/BOARD_ONEPASS_MECH_SYNC.md L561 / MECH/BOARD_ONEPASS_MECH_CLAIMS.md L50 / \"",
      "edge": "E01"
    },
    {
      "id": "HC-014",
      "gate": "MECH/check_debug_seat_3d_fit.py",
      "line": 734,
      "value": 4.81,
      "rules": [
        "R2"
      ],
      "ctx": "clear_src.4.81",
      "text": "4.8100: \"MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md §0.1 (官方 THT 真 land·3.81 + 1.00)\",",
      "edge": "E01"
    },
    {
      "id": "HC-015",
      "gate": "MECH/check_debug_seat_3d_fit.py",
      "line": 737,
      "value": 1.775,
      "rules": [
        "R2"
      ],
      "ctx": "clear_costs.1.775",
      "text": "1.7750: \"结构件按此数出件 ⇒ 换官方 THT 后铜箔每边超出清空区 1.5175 ⇒ 几何上当场干涉 ⇒ \"",
      "edge": "E01"
    },
    {
      "id": "HC-016",
      "gate": "MECH/check_debug_seat_3d_fit.py",
      "line": 739,
      "value": 4.085,
      "rules": [
        "R2"
      ],
      "ctx": "clear_costs.4.085",
      "text": "4.0850: \"结构件按此数出件 ⇒ 换官方 THT 后铜箔每边超出清空区 0.3625 ⇒ 仍干涉 ⇒ \"",
      "edge": "E01"
    },
    {
      "id": "HC-017",
      "gate": "MECH/check_debug_seat_3d_fit.py",
      "line": 741,
      "value": 4.81,
      "rules": [
        "R2"
      ],
      "ctx": "clear_costs.4.81",
      "text": "4.8100: \"结构件按此数出件 ⇒ 换官方 THT 后铜箔与清空区齐平 (每边超出 0.0000) ⇒ 几何上不干涉, \"",
      "edge": "E01"
    },
    {
      "id": "HC-018",
      "gate": "MECH/check_debug_seat_rework_spec.py",
      "line": 118,
      "value": 6.61,
      "rules": [
        "R1"
      ],
      "ctx": "REQUIRED_CLEAR_X",
      "text": "REQUIRED_CLEAR_X = 6.6100",
      "edge": "E02"
    },
    {
      "id": "HC-019",
      "gate": "MECH/check_debug_seat_rework_spec.py",
      "line": 120,
      "value": 4.81,
      "rules": [
        "R1"
      ],
      "ctx": "OFFICIAL_DEBUG_COPPER_X",
      "text": "OFFICIAL_DEBUG_COPPER_X = 4.8100",
      "edge": "E02"
    },
    {
      "id": "HC-020",
      "gate": "MECH/check_debug_seat_rework_spec.py",
      "line": 122,
      "value": 1.0,
      "rules": [
        "R1"
      ],
      "ctx": "OFFICIAL_COPPER_Y",
      "text": "OFFICIAL_COPPER_Y = 1.0000",
      "edge": "E02"
    },
    {
      "id": "HC-021",
      "gate": "MECH/check_jdebug_1p27_clearance.py",
      "line": 397,
      "value": 1.27,
      "rules": [
        "R3'"
      ],
      "ctx": "near(...)",
      "text": "if not near(geo[\"pitch\"], 1.27):",
      "edge": "E06"
    },
    {
      "id": "HC-022",
      "gate": "MECH/check_jdebug_1p27_clearance.py",
      "line": 399,
      "value": 3.81,
      "rules": [
        "R3'"
      ],
      "ctx": "near(...)",
      "text": "if not near(geo[\"span\"], 3.81):",
      "edge": "E06"
    },
    {
      "id": "HC-023",
      "gate": "MECH/check_jdebug_1p27_clearance.py",
      "line": 404,
      "value": 0.65,
      "rules": [
        "R3'"
      ],
      "ctx": "near(...)",
      "text": "if geo[\"drill\"] is None or not near(geo[\"drill\"], 0.65):",
      "edge": "E06"
    },
    {
      "id": "HC-024",
      "gate": "MECH/check_juart_1p27_clearance.py",
      "line": 417,
      "value": 1.27,
      "rules": [
        "R3'"
      ],
      "ctx": "near(...)",
      "text": "if not near(pitch, 1.27):",
      "edge": "E07"
    },
    {
      "id": "HC-025",
      "gate": "MECH/check_juart_1p27_clearance.py",
      "line": 837,
      "value": 0.6,
      "rules": [
        "R4"
      ],
      "ctx": "get-default",
      "text": "ctx[\"crit\"] = crit.get(\"crit\", 0.60)",
      "edge": "E07"
    },
    {
      "id": "HC-026",
      "gate": "MECH/check_juart_1p27_clearance.py",
      "line": 838,
      "value": 0.3,
      "rules": [
        "R4"
      ],
      "ctx": "get-default",
      "text": "ctx[\"fdm_part\"] = crit.get(\"fdm_part\", 0.30)",
      "edge": "E07"
    }
  ],
  "invalidation_matrix": [
    {
      "id": "M1",
      "label": "焊盘 PQ01/PQ02  1.000 → 1.110",
      "premise_change": {
        "premises": [
          "PQ01",
          "PQ02"
        ],
        "from": 1.0,
        "to": 1.11
      },
      "cells": [
        {
          "kind": "number",
          "target": "j_debug_copper_x",
          "status": "invalid",
          "old_value": 4.81,
          "new_value": 4.92
        },
        {
          "kind": "number",
          "target": "j_uart_copper_x",
          "status": "invalid",
          "old_value": 2.27,
          "new_value": 2.38
        },
        {
          "kind": "number",
          "target": "j_debug_required_clear_x",
          "status": "invalid",
          "old_value": 6.61,
          "new_value": 6.72
        },
        {
          "kind": "number",
          "target": "j_uart_required_clear_x",
          "status": "invalid",
          "old_value": 4.07,
          "new_value": 4.18
        },
        {
          "kind": "number",
          "target": "j_uart_cover_margin_x",
          "status": "invalid",
          "old_value": 0.135,
          "new_value": 0.08
        },
        {
          "kind": "number",
          "target": "j_debug_opening_margin_x",
          "status": "invalid",
          "old_value": 2.695,
          "new_value": 2.64
        },
        {
          "kind": "number",
          "target": "j_debug_cover_margin_y",
          "status": "invalid",
          "old_value": 0.77,
          "new_value": 0.715
        },
        {
          "kind": "gate",
          "target": "MECH/check_debug_seat_3d_fit.py",
          "status": "invalid"
        },
        {
          "kind": "gate",
          "target": "MECH/check_debug_seat_rework_spec.py",
          "status": "invalid"
        },
        {
          "kind": "gate",
          "target": "MECH/check_fts_seat_body_geometry.py",
          "status": "invalid"
        },
        {
          "kind": "gate",
          "target": "MECH/check_fts_vs_generic_courtyard_delta.py",
          "status": "invalid"
        },
        {
          "kind": "gate",
          "target": "MECH/check_fts_seat_sample_plan.py",
          "status": "invalid"
        },
        {
          "kind": "gate",
          "target": "MECH/check_jdebug_1p27_clearance.py",
          "status": "invalid"
        },
        {
          "kind": "gate",
          "target": "MECH/check_juart_1p27_clearance.py",
          "status": "invalid"
        },
        {
          "kind": "gate",
          "target": "MECH/check_connector_clearance_caliber.py",
          "status": "invalid"
        },
        {
          "kind": "conclusion",
          "target": "MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md",
          "status": "invalid"
        },
        {
          "kind": "conclusion",
          "target": "MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md",
          "status": "invalid"
        },
        {
          "kind": "conclusion",
          "target": "MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md",
          "status": "invalid"
        },
        {
          "kind": "conclusion",
          "target": "MECH/BOARD_ONEPASS_PAD_SIZE_COUPLING.md",
          "status": "invalid"
        }
      ],
      "note": "ISS-403 已 A/B 实测 7 道闸: 5 道对焊盘尺寸【完全盲】(两臂 stdout md5 逐字相同) + 2 道会转红 (jdebug G1~G4 / juart J0/J1/J5/J7); 本单依赖图覆盖 9 道 (多出的 check_fts_seat_sample_plan.py 与 check_pad_size_coupling_closed.py 未做过 A/B)"
    },
    {
      "id": "M2",
      "label": "规划钻孔 PQ04  0.71 → 0.65",
      "premise_change": {
        "premises": [
          "PQ04"
        ],
        "from": 0.71,
        "to": 0.65
      },
      "cells": [
        {
          "kind": "number",
          "target": "annular_ring",
          "status": "invalid",
          "new_value": 0.175
        },
        {
          "kind": "number",
          "target": "seven_numbers_matrix",
          "status": "invalid"
        },
        {
          "kind": "gate",
          "target": "MECH/check_pad_size_coupling_closed.py",
          "status": "invalid"
        },
        {
          "kind": "gate",
          "target": "MECH/check_jdebug_1p27_clearance.py",
          "status": "invalid"
        },
        {
          "kind": "gate",
          "target": "MECH/check_juart_1p27_clearance.py",
          "status": "invalid"
        },
        {
          "kind": "conclusion",
          "target": "MECH/BOARD_ONEPASS_PAD_SIZE_COUPLING.md",
          "status": "invalid"
        },
        {
          "kind": "conclusion",
          "target": "HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md",
          "status": "invalid"
        }
      ],
      "note": "环宽口径翻转: (1.000−0.71)/2=0.1450 → (1.000−0.65)/2=0.1750 ⇒ 环宽这一格由红转绿"
    },
    {
      "id": "M3",
      "label": "座体三量 PQ13/PQ14/PQ15 (实测档到手)",
      "premise_change": {
        "premises": [
          "PQ13",
          "PQ14",
          "PQ15"
        ],
        "from": null,
        "to": null
      },
      "cells": [
        {
          "kind": "number",
          "target": "seat_clearance_x",
          "status": "invalid"
        },
        {
          "kind": "number",
          "target": "seat_3q_sample",
          "status": "invalid"
        },
        {
          "kind": "number",
          "target": "courtyard_delta_18",
          "status": "invalid"
        },
        {
          "kind": "gate",
          "target": "MECH/check_fts_seat_body_geometry.py",
          "status": "invalid"
        },
        {
          "kind": "gate",
          "target": "MECH/check_fts_seat_sample_plan.py",
          "status": "invalid"
        },
        {
          "kind": "gate",
          "target": "MECH/check_fts_vs_generic_courtyard_delta.py",
          "status": "invalid"
        },
        {
          "kind": "conclusion",
          "target": "MECH/BOARD_ONEPASS_FTS_SEAT_SAMPLE_MEASURE_PLAN.md",
          "status": "invalid"
        }
      ],
      "note": "这三道闸【第一次有真值可判】⇒ 前提从 `[0数据]` 变有源, 是【新增判据】不是【作废】"
    },
    {
      "id": "M4",
      "label": "清空区/开口 PQ09~PQ12 改一格",
      "premise_change": {
        "premises": [
          "PQ09",
          "PQ10",
          "PQ11",
          "PQ12"
        ],
        "from": null,
        "to": null
      },
      "cells": [
        {
          "kind": "number",
          "target": "j_uart_cover_margin_x",
          "status": "invalid",
          "old_value": 0.135
        },
        {
          "kind": "number",
          "target": "j_debug_opening_margin_x",
          "status": "invalid",
          "old_value": 2.695
        },
        {
          "kind": "number",
          "target": "j_debug_cover_margin_y",
          "status": "invalid",
          "old_value": 0.77
        },
        {
          "kind": "gate",
          "target": "MECH/check_debug_seat_3d_fit.py",
          "status": "invalid"
        },
        {
          "kind": "gate",
          "target": "MECH/check_debug_seat_rework_spec.py",
          "status": "invalid"
        },
        {
          "kind": "gate",
          "target": "MECH/check_jdebug_1p27_clearance.py",
          "status": "invalid"
        },
        {
          "kind": "gate",
          "target": "MECH/check_juart_1p27_clearance.py",
          "status": "invalid"
        },
        {
          "kind": "gate",
          "target": "MECH/check_connector_clearance_caliber.py",
          "status": "invalid"
        },
        {
          "kind": "conclusion",
          "target": "MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md",
          "status": "invalid"
        },
        {
          "kind": "conclusion",
          "target": "MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md",
          "status": "invalid"
        },
        {
          "kind": "conclusion",
          "target": "MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md",
          "status": "invalid"
        }
      ],
      "note": "清空区宽是【座体支配】, 与焊盘无关 ⇒ 改焊盘不会改它, 改座体才会"
    },
    {
      "id": "M5",
      "label": "判决阈 PQ07/PQ08 改一格",
      "premise_change": {
        "premises": [
          "PQ07",
          "PQ08"
        ],
        "from": null,
        "to": null
      },
      "cells": [
        {
          "kind": "number",
          "target": "j_debug_required_clear_x",
          "status": "invalid",
          "old_value": 6.61
        },
        {
          "kind": "number",
          "target": "j_uart_required_clear_x",
          "status": "invalid",
          "old_value": 4.07
        },
        {
          "kind": "number",
          "target": "j_uart_cover_margin_x",
          "status": "invalid",
          "old_value": 0.135
        },
        {
          "kind": "number",
          "target": "j_debug_opening_margin_x",
          "status": "invalid",
          "old_value": 2.695
        },
        {
          "kind": "number",
          "target": "j_debug_cover_margin_y",
          "status": "invalid",
          "old_value": 0.77
        },
        {
          "kind": "gate",
          "target": "MECH/check_debug_seat_3d_fit.py",
          "status": "invalid"
        },
        {
          "kind": "gate",
          "target": "MECH/check_debug_seat_rework_spec.py",
          "status": "invalid"
        },
        {
          "kind": "gate",
          "target": "MECH/check_jdebug_1p27_clearance.py",
          "status": "invalid"
        },
        {
          "kind": "gate",
          "target": "MECH/check_juart_1p27_clearance.py",
          "status": "invalid"
        },
        {
          "kind": "gate",
          "target": "MECH/check_connector_clearance_caliber.py",
          "status": "invalid"
        },
        {
          "kind": "conclusion",
          "target": "MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md",
          "status": "invalid"
        },
        {
          "kind": "conclusion",
          "target": "MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md",
          "status": "invalid"
        },
        {
          "kind": "conclusion",
          "target": "MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md",
          "status": "invalid"
        }
      ],
      "note": "阈值一改 ⇒ 所有「最坏 = 余量 − TOL」的过阈结论同时重判"
    },
    {
      "id": "M6",
      "label": "板厚 PQ16 定档",
      "premise_change": {
        "premises": [
          "PQ16"
        ],
        "from": null,
        "to": null
      },
      "cells": [
        {
          "kind": "number",
          "target": "seat_z_fit",
          "status": "invalid"
        },
        {
          "kind": "gate",
          "target": "MECH/check_debug_seat_3d_fit.py",
          "status": "invalid"
        },
        {
          "kind": "conclusion",
          "target": "MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md",
          "status": "invalid"
        }
      ],
      "note": "Z 向基准 ⇒ 只影响 3D 装配那一道闸"
    },
    {
      "id": "M7",
      "label": "板厂能力 PQ17 改一格 (或换板厂)",
      "premise_change": {
        "premises": [
          "PQ17"
        ],
        "from": null,
        "to": null
      },
      "cells": [
        {
          "kind": "number",
          "target": "fab_annular_min",
          "status": "invalid"
        },
        {
          "kind": "gate",
          "target": "MECH/check_pad_size_coupling_closed.py",
          "status": "invalid"
        },
        {
          "kind": "conclusion",
          "target": "MECH/BOARD_ONEPASS_PAD_SIZE_COUPLING.md",
          "status": "invalid"
        }
      ],
      "note": "这是【门限】不是【被测值】⇒ 板厂换人 ⇒ 全部 pad 档位结论重排"
    }
  ],
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
  "outbox_baseline": {
    "tree_md5": "7c5f45e922447340349a224cf05a9807",
    "files": 22
  },
  "board_baseline": {
    "path": "HW/PCB/demo_mainboard.kicad_pcb",
    "md5": "611b869e13518c3c023fb178f91a0075",
    "size": 4940213,
    "mtime": "2026-11-06 07:07:17.362193413"
  },
  "gate_criteria": {
    "D1": "每个前提量的「当前值 + 真值读取点」必须能被脚本重新读出来 ⇒ 读不出来 ⇒ 判红",
    "D2": "每个前提量至少挂到 1 条依赖边 ⇒ 孤立前提量 ⇒ 判红",
    "D3": "AST 实扫到的写死常量点必须逐条登记且被依赖图引用 ⇒ 漏一条 ⇒ 判红",
    "D4": "矩阵每一格必须能在依赖图里找到对应边 ⇒ 多/少一格 ⇒ 判红",
    "D5": "板 / 网表 / 脚表 / BOM md5 与基线逐字相同",
    "D6": "零挂链 (grep=0) + 零外发 (outbox 树摘要) + 证据分级五级白名单"
  },
  "open_items": {
    "OI-407-1": "「板那一趟」开工前要不要按依赖图逐项过一遍前提值 ⇒ to=main",
    "OI-407-2": "焊盘档拍下后必须同批重算的几个数是谁的活 ⇒ to=main",
    "OI-407-3": "写死常量点要不要改成「现读板面」(判据口径变更) ⇒ to=main",
    "OI-407-4": "作废传播矩阵要不要挂成投板前的硬清单 ⇒ to=main",
    "OI-407-5": "本闸自己挂不挂链 (自指悖论) ⇒ to=main"
  },
  "self_reference_paradox": "本闸自身不在链上 (D6 自证 grep=0) ⇒ 需 main 登记 (链上 或 人工签核台账) ⇒ 本单不代拍",
  "decision_taken_here": "not_decided_here"
}
```

==============================================================================
★**页尾**: ★**本页 = 真相页 + 机器块; 判据载体 = `MECH/check_verdict_premise_dependency.py` (★裸跑 rc=1 = 现状自洽描述的是病; `--selftest` rc=0 末行逐字 `ALL TESTS PASS`★) · 交卷页 = `HANDOFF/2026-11-25_mech-lead_ISS407_判决链前提依赖与作废传播.md`** ★
★**★本单零写板 · 零落表 (除自有分片) · 零改既有闸 · 零改既有页正文 · 零挂链 · 零外发 · 不代拍 · 不自签** ★
