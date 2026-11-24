# MECH · 「已签收件追加登记台账」设计 + 三处陈旧 pin 逐条裁定 (ISS-399)

> ★**单号**: ISS-399 · ★**owner**: mech-lead · ★**verify_by**: main · ★**零外发** ★
> ★**性质**: ★**纯分析 + 新建真相页 + 新建机器闸 + 出逐字补丁(不应用)** ★· ★零写板 · 零落表 · 零改既有闸 · 零改既有页正文 · 零挂链 · 不代拍 ★
> ★**派活**: 项目总工 (main) · cron `775d9893` · 2026-11-24 21:44 派 / cont2 (2026-11-24 22:0x) 续做 ★
> ★**配套闸**: `MECH/check_mech_signed_append_ledger.py` (★本单新建·M1~M7 判据 + `--selftest` 12 条反向用例·★零挂链★) ★
> ★**配套交卷页**: `HANDOFF/2026-11-24_mech-lead_ISS399_MECH域已签收件追加台账设计与自守闸.md` ★

---

## ★§0 · 口径与边界自证 ★

### ★0.1 · 本页要回答的问题 (一句话) ★

★**MECH 域每一道闸都把「别的文件」的 md5 写死成常量 ⇒ 每次合法的口径订正都会让那个常量永久陈旧 ⇒ 红是真的、但原因是对的 ⇒ 现场极可能误读成「MECH 改坏了」⇒ 板白改第二遍。** ★
★**本页给出: ① 盘面【全量】清账 (逐处一行) ② 三处已陈旧 pin 的【逐条裁定】(是不是合法动作 / 为什么没人更新基线) ③ MECH 域【追加登记台账】的设计 ④ 三条【逐字补丁】(不应用) ⑤ 挂链建议 (不应用)。** ★

### ★0.2 · 「合法变更」在本页的口径 (★本单自定·★**不代拍 M-D**★) ★

| 词 | 本页的用法 | 判据出处 |
|---|---|---|
| ★**合法变更** ★ | ★**该变更 (a) 由某个单号明确提出并留下交卷记录 (b) 变更的【新值】与【旧值】都还能在文档里查到 (c) 变更没有藏起来 (交卷页里有逐字 md5 台账行) ⇒ 三个条件齐 ⇒ 合法** ★ | §2 逐条裁定 · ★**这三条由本单提出·M-D 待 main 拍**★ |
| ★**悄悄换基线** ★ | ★**改了闸里的写死常量、但没留下上述 (a)(b)(c) 任一条 ⇒ 无论文件本身改得对不对 ⇒ 都判红** ★ | §4 补丁 ① · 闸 M4 ★
| ★**追加式订正** ★ | ★**house 现有规矩的说法: 追加式订正 = 老字一字未删, 只在尾部追加** ★ | ★**★★ 本页实测发现: 三处陈旧 pin 里【没有一处】是纯追加 (见 §2.4) ⇒ 这条规矩在这三处【全部不成立】★★★ ★ |

### ★0.3 · 边界自证 (★逐条·★全部为【实测】★) ★

| # | 边界 | 本页的自证方式 | 结果 |
|---|---|---|---|
| 1 | ★**零写板** ★ | 板 md5 / mtime(ns) / size 三项与基线逐字比 | ★**板 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · size `4940213` 全等** ★ `[实测]` |
| 2 | ★**零落表** ★ | 网表 / 脚表 / BOM 三张表 md5 与基线逐字比 | ★**`6aee500e…` / `9174309d…` / `5b999399…` 全等** ★ `[实测]` |
| 3 | ★**零改既有闸** ★ | ★**那 11 道 MECH 域闸 (含任务书点名的 9 道) 开工前后 md5 逐字相同** ★ | ★**全等 (基线存 `logs/iss399/baseline_9gates_md5.txt`)** ★ `[实测]` |
| 4 | ★**零改既有页面正文** ★ | ★**只【新建】本页 + 交卷页; 已有的 MECH 页面一个字没改** ★ | ★**成立** ★ `[实测]` |
| 5 | ★**零挂链** ★ | `grep -c check_mech_signed_append_ledger state/gate_check.py` | ★**0** ★ `[实测]` |
| 6 | ★**零外发** ★ | 全程只读本机文件 + 跑本机脚本 | ★**零次外发请求** ★ `[实测]` |
| 7 | ★**不代拍** ★ | ★**M-A / M-B / M-C / M-D 四条全交 main (交卷页 B5), 每条带代价** ★ | ★**一条都没自己定** ★ `[实测]` |
| 8 | ★**不自签 issue_log** ★ | `state/issue_log.yaml` 一个字节没动 | ★**成立** ★ `[实测]` |
| 9 | ★**只写自己分片** ★ | 只走 `python3 state/frag_write.py --agent mech-lead` | ★**成立** ★ `[实测]` |
| 10 | ★**沙盒只落项目盘** ★ | 临时产物只写 `tmp/iss399/` · 留证只写 `logs/iss399/` | ★**未写系统 `/tmp`** ★ `[实测]` |

### ★0.4 · 证据分级口径 ★

★**白名单五级: `[官网]` / `[实测]` / `[媒体]` / `[推算]` / `[0数据]`** ★
★**本页所有关键结论都带等级; 盘上实读的写 `[实测]`; 由实读推出但没独立复算的写 `[推算]`; 本机没有的写 `[0数据]`。** ★
★**零挂起措辞: 本页不写「缺口等外部回话」这类话; 查不到的一律自己查 + 标等级 + 给降级方案。** ★

---

## ★§1 · MECH 域「钉别人 md5」全量清账表 ★

### ★1.1 · 枚举口径 (★代码级·★不手抄任何人的表★) ★

★**枚举器 = `MECH/check_mech_signed_append_ledger.py` 里的 `enumerate_pins()`**: ★**用 Python `ast` 逐个解析 `MECH/*.py` 与 `MECH/tools/*.py` 的源码 AST** ★ ⇒
★**凡是把「一个 32 位十六进制字符串」当字典值、而字典键解析得出一个【盘上真实存在的文件路径】的, 就登记为一处 pin; 位于函数体内的 (★自测夹具★) 不算 pin。** ★ `[实测]`
★**⇒ 枚举结果: 盘上共 ★**49 处 pin** ★, 分布在 ★**11 道 MECH 域闸** ★ 里, 分三类: ★

| 类别 | 含义 | 处数 | 本页口径 |
|---|---|---|---|
| ★**P1 硬钉** ★ | ★**把别人的 md5 写死成常量, 且该闸【没有】任何台账/合法变更通道** ★ | ★**42** ★ | ★**本单清账 + 在册的主体 (M1 要求逐处在册)** ★ |
| ★**P2 板族钉** ★ | 钉的是板族文件 (`.kicad_pcb` / `.kicad_pro`) | 4 | 不在本台账口径内 (板是板侧地界) |
| ★**P3 台账通道钉** ★ | ★**钉的是落表台账管的三个文件, 且该闸【已经】有「硬基线 ∪ 落表台账登记值」的通道** ★ | 3 | ★**已有先例 (ISS-296 / ISS-303) ⇒ 本单不改, 只登记** ★ |

### ★1.2 · ★P1 硬钉 42 处 · 逐处一行 (★这是全量·不是抽样★)★

| 闸 | 行号 | 被钉文件 | 闸里写死的基线 | 盘上现值 | 状态 | 陈旧原因 + 证据出处 |
|---|---|---|---|---|---|---|
| `MECH/cavity_recalc_check.py` | L93 | `MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md` | `96239070dc7c0ec00edb1b758a698769` | `96239070dc7c0ec00edb1b758a698769` | 绿 | — (基线 == 盘上现值) |
| `MECH/cavity_recalc_check.py` | L101 | `MECH/display_biosafety_v2_check.py` | `29c77fc3fc823048b1d96c9500d28dd7` | `29c77fc3fc823048b1d96c9500d28dd7` | 绿 | — (基线 == 盘上现值) |
| `MECH/cavity_recalc_check.py` | L94 | `MECH/hinge_usb_check.py` | `3425bc141508de8a35f34c7cf7b803e8` | `3425bc141508de8a35f34c7cf7b803e8` | 绿 | — (基线 == 盘上现值) |
| `MECH/cavity_recalc_check.py` | L100 | `MECH/hw_cross_review_check.py` | `e521387b87b0fcdf9f22d56f14199967` | `e521387b87b0fcdf9f22d56f14199967` | 绿 | — (基线 == 盘上现值) |
| `MECH/cavity_recalc_check.py` | L99 | `MECH/service_port_check.py` | `db58ff6a2afc28b8bf517e3c57c56bc1` | `db58ff6a2afc28b8bf517e3c57c56bc1` | 绿 | — (基线 == 盘上现值) |
| `MECH/check_connector_clearance_caliber.py` | L83 | `MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` | `da7b02c013fa49c65b70ed3bea97b787` | `da7b02c013fa49c65b70ed3bea97b787` | 绿 | — (基线 == 盘上现值) |
| `MECH/check_connector_clearance_caliber.py` | L84 | `MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md` | `ffc099397dc573df207f265bff57dffb` | `f1ce54c981dd1f64071a177a374df85d` | ★**已陈旧**★ | ★合法·已披露★ ⇒ ISS-374 cont2 (2026-11-24 04:12:52) 订正「座体本体外框」口径 ⇒ 见 §2.1 |
| `MECH/check_connector_clearance_caliber.py` | L87 | `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` | `b254fa98c09bc7adb058e1d03eb13980` | `b254fa98c09bc7adb058e1d03eb13980` | 绿 | — (基线 == 盘上现值) |
| `MECH/check_connector_clearance_caliber.py` | L85 | `MECH/check_jdebug_1p27_clearance.py` | `a9914b2c3e9f8f92f1fbb60d1d8bdd86` | `a9914b2c3e9f8f92f1fbb60d1d8bdd86` | 绿 | — (基线 == 盘上现值) |
| `MECH/check_connector_clearance_caliber.py` | L86 | `MECH/check_juart_1p27_clearance.py` | `ea89e0dd3b2f77828b69f06bbe76969d` | `daf8fa367d89e22f6d3af3d5049bdfb6` | ★**已陈旧**★ | ★合法·已披露★ ⇒ ISS-374 cont2 (2026-11-24 04:13:02) 同步闸内 selftest 夹具字段名 ⇒ 见 §2.2 |
| `MECH/check_debug_seat_3d_fit.py` | L94 | `HW/BOM_v1.csv` | `5b9993992405904a60ac96a020b375d8` | `5b9993992405904a60ac96a020b375d8` | 绿 | — (基线 == 盘上现值) |
| `MECH/check_debug_seat_3d_fit.py` | L92 | `HW/netlist_v1.csv` | `6aee500e60ba0732f83a9cf557ba90ab` | `6aee500e60ba0732f83a9cf557ba90ab` | 绿 | — (基线 == 盘上现值) |
| `MECH/check_debug_seat_3d_fit.py` | L93 | `HW/netlist_v1_pins.csv` | `9174309df1ec9411ac8e8d9e80ee386a` | `9174309df1ec9411ac8e8d9e80ee386a` | 绿 | — (基线 == 盘上现值) |
| `MECH/check_debug_seat_rework_spec.py` | L97 | `HW/BOM_v1.csv` | `5b9993992405904a60ac96a020b375d8` | `5b9993992405904a60ac96a020b375d8` | 绿 | — (基线 == 盘上现值) |
| `MECH/check_debug_seat_rework_spec.py` | L95 | `HW/netlist_v1.csv` | `6aee500e60ba0732f83a9cf557ba90ab` | `6aee500e60ba0732f83a9cf557ba90ab` | 绿 | — (基线 == 盘上现值) |
| `MECH/check_debug_seat_rework_spec.py` | L96 | `HW/netlist_v1_pins.csv` | `9174309df1ec9411ac8e8d9e80ee386a` | `9174309df1ec9411ac8e8d9e80ee386a` | 绿 | — (基线 == 盘上现值) |
| `MECH/check_demo_struct_truth.py` | L92 | `MECH/display_biosafety_v2_check.py` | `29c77fc3fc823048b1d96c9500d28dd7` | `29c77fc3fc823048b1d96c9500d28dd7` | 绿 | — (基线 == 盘上现值) |
| `MECH/check_demo_struct_truth.py` | L83 | `MECH/hinge_usb_check.py` | `3425bc141508de8a35f34c7cf7b803e8` | `3425bc141508de8a35f34c7cf7b803e8` | 绿 | — (基线 == 盘上现值) |
| `MECH/check_demo_struct_truth.py` | L91 | `MECH/hw_cross_review_check.py` | `e521387b87b0fcdf9f22d56f14199967` | `e521387b87b0fcdf9f22d56f14199967` | 绿 | — (基线 == 盘上现值) |
| `MECH/check_demo_struct_truth.py` | L90 | `MECH/service_port_check.py` | `db58ff6a2afc28b8bf517e3c57c56bc1` | `db58ff6a2afc28b8bf517e3c57c56bc1` | 绿 | — (基线 == 盘上现值) |
| `MECH/check_fts_seat_body_geometry.py` | L94 | `HW/BOM_v1.csv` | `5b9993992405904a60ac96a020b375d8` | `5b9993992405904a60ac96a020b375d8` | 绿 | — (基线 == 盘上现值) |
| `MECH/check_fts_seat_body_geometry.py` | L92 | `HW/netlist_v1.csv` | `6aee500e60ba0732f83a9cf557ba90ab` | `6aee500e60ba0732f83a9cf557ba90ab` | 绿 | — (基线 == 盘上现值) |
| `MECH/check_fts_seat_body_geometry.py` | L93 | `HW/netlist_v1_pins.csv` | `9174309df1ec9411ac8e8d9e80ee386a` | `9174309df1ec9411ac8e8d9e80ee386a` | 绿 | — (基线 == 盘上现值) |
| `MECH/check_fts_seat_sample_plan.py` | L62 | `HW/BOM_v1.csv` | `5b9993992405904a60ac96a020b375d8` | `5b9993992405904a60ac96a020b375d8` | 绿 | — (基线 == 盘上现值) |
| `MECH/check_fts_seat_sample_plan.py` | L60 | `HW/netlist_v1.csv` | `6aee500e60ba0732f83a9cf557ba90ab` | `6aee500e60ba0732f83a9cf557ba90ab` | 绿 | — (基线 == 盘上现值) |
| `MECH/check_fts_seat_sample_plan.py` | L61 | `HW/netlist_v1_pins.csv` | `9174309df1ec9411ac8e8d9e80ee386a` | `9174309df1ec9411ac8e8d9e80ee386a` | 绿 | — (基线 == 盘上现值) |
| `MECH/check_fts_seat_sample_plan.py` | L70 | `MECH/BOARD_ONEPASS_FTS_SEAT_BODY_GEOMETRY.md` | `15697668d10368e971710069c9b73994` | `15697668d10368e971710069c9b73994` | 绿 | — (基线 == 盘上现值) |
| `MECH/check_fts_seat_sample_plan.py` | L71 | `MECH/BOARD_ONEPASS_FTS_VS_GENERIC_COURTYARD_DELTA.md` | `0cb3ff2de940522b467ca3b01feda11c` | `0cb3ff2de940522b467ca3b01feda11c` | 绿 | — (基线 == 盘上现值) |
| `MECH/check_fts_seat_sample_plan.py` | L66 | `MECH/check_fts_seat_body_geometry.py` | `1cdc6e9838419647e018c9a4c41319a2` | `1cdc6e9838419647e018c9a4c41319a2` | 绿 | — (基线 == 盘上现值) |
| `MECH/check_fts_seat_sample_plan.py` | L67 | `MECH/check_fts_vs_generic_courtyard_delta.py` | `8f8424a5e632fa3d223271850109c6d0` | `8f8424a5e632fa3d223271850109c6d0` | 绿 | — (基线 == 盘上现值) |
| `MECH/check_fts_seat_sample_plan.py` | L68 | `MECH/check_onepass_mech_release.py` | `bd90741d38c6cd362d83e1f205cc21c5` | `bd90741d38c6cd362d83e1f205cc21c5` | 绿 | — (基线 == 盘上现值) |
| `MECH/check_fts_seat_sample_plan.py` | L69 | `MECH/check_onepass_mech_sync.py` | `5247486a6739d9b0cd5cf9a886c771e8` | `5247486a6739d9b0cd5cf9a886c771e8` | 绿 | — (基线 == 盘上现值) |
| `MECH/check_fts_vs_generic_courtyard_delta.py` | L36 | `HW/BOM_v1.csv` | `5b9993992405904a60ac96a020b375d8` | `5b9993992405904a60ac96a020b375d8` | 绿 | — (基线 == 盘上现值) |
| `MECH/check_fts_vs_generic_courtyard_delta.py` | L34 | `HW/netlist_v1.csv` | `6aee500e60ba0732f83a9cf557ba90ab` | `6aee500e60ba0732f83a9cf557ba90ab` | 绿 | — (基线 == 盘上现值) |
| `MECH/check_fts_vs_generic_courtyard_delta.py` | L35 | `HW/netlist_v1_pins.csv` | `9174309df1ec9411ac8e8d9e80ee386a` | `9174309df1ec9411ac8e8d9e80ee386a` | 绿 | — (基线 == 盘上现值) |
| `MECH/check_mech_dual_caliber_gate.py` | L76 | `MECH/hw_cross_review_check.py` | `e521387b87b0fcdf9f22d56f14199967` | `e521387b87b0fcdf9f22d56f14199967` | 绿 | — (基线 == 盘上现值) |
| `MECH/check_zoujuan_marker_consistency.py` | L61 | `MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md` | `96239070dc7c0ec00edb1b758a698769` | `96239070dc7c0ec00edb1b758a698769` | 绿 | — (基线 == 盘上现值) |
| `MECH/check_zoujuan_marker_consistency.py` | L62 | `MECH/JBD_ROLE_NARROWING.md` | `bda4a29464336bc1452c913602ce3f46` | `bda4a29464336bc1452c913602ce3f46` | 绿 | — (基线 == 盘上现值) |
| `MECH/check_zoujuan_marker_consistency.py` | L63 | `MECH/check_demo_struct_truth.py` | `fa9b59e593a13408ad9505d986276f63` | `483d018a66d17d2ead25d1558a1f8ffe` | ★**已陈旧**★ | ★合法·已披露★ ⇒ ISS-296 (2026-11-17 20:25:32) G5b 合法改板通道改造 ⇒ 见 §2.3 |
| `MECH/check_zoujuan_marker_consistency.py` | L60 | `MECH/display_biosafety_v2_check.py` | `29c77fc3fc823048b1d96c9500d28dd7` | `29c77fc3fc823048b1d96c9500d28dd7` | 绿 | — (基线 == 盘上现值) |
| `MECH/display_biosafety_v2_check.py` | L55 | `MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md` | `96239070dc7c0ec00edb1b758a698769` | `96239070dc7c0ec00edb1b758a698769` | 绿 | — (基线 == 盘上现值) |
| `MECH/display_biosafety_v2_check.py` | L56 | `MECH/JBD_ROLE_NARROWING.md` | `bda4a29464336bc1452c913602ce3f46` | `bda4a29464336bc1452c913602ce3f46` | 绿 | — (基线 == 盘上现值) |

★**逐闸计数 (与盘面枚举一致)**: `cavity_recalc_check.py` 5 · `check_connector_clearance_caliber.py` 5 · `check_debug_seat_3d_fit.py` 3 · `check_debug_seat_rework_spec.py` 3 · `check_demo_struct_truth.py` 4 · `check_fts_seat_body_geometry.py` 3 · `check_fts_seat_sample_plan.py` 9 · `check_fts_vs_generic_courtyard_delta.py` 3 · `check_mech_dual_caliber_gate.py` 1 · `check_zoujuan_marker_consistency.py` 4 · `display_biosafety_v2_check.py` 2 ⇒ ★**合计 42** ★ `[实测]`

### ★1.3 · P2 / P3 附录 (★7 处·★不纳入 §1 机器块★) ★

| 闸 | 行号 | 被钉文件 | 闸里写死的基线 | 盘上现值 | 类别 | 状态 |
|---|---|---|---|---|---|---|
| `MECH/check_board_frame_coords.py` | L110 | `HW/PCB/demo_mainboard.kicad_pcb` | `611b869e13518c3c023fb178f91a0075` | `611b869e13518c3c023fb178f91a0075` | P2 板族钉 | 绿 |
| `MECH/check_board_frame_coords.py` | L111 | `HW/PCB/demo_mainboard.kicad_pro` | `3e504d2be83152e337949723e909be1b` | `3e504d2be83152e337949723e909be1b` | P2 板族钉 | 绿 |
| `MECH/check_demo_struct_truth.py` | L81 | `HW/PCB/demo_mainboard.kicad_pcb` | `611b869e13518c3c023fb178f91a0075` | `611b869e13518c3c023fb178f91a0075` | P2 板族钉 | 绿 |
| `MECH/check_demo_struct_truth.py` | L82 | `HW/PCB/demo_mainboard.kicad_pro` | `3e504d2be83152e337949723e909be1b` | `3e504d2be83152e337949723e909be1b` | P2 板族钉 | 绿 |
| `MECH/check_onepass_struct_crosscheck.py` | L74 | `HW/BOM_v1.csv` | `5d02bece9477ffce5fbe0193c7d5cce4` | `5b9993992405904a60ac96a020b375d8` | P3 台账通道钉 | ★**已陈旧 (但有通道·不归本台账口径)**★ |
| `MECH/check_onepass_struct_crosscheck.py` | L72 | `HW/netlist_v1.csv` | `37f62ac3f0b81d92ca7d48fdea717f07` | `6aee500e60ba0732f83a9cf557ba90ab` | P3 台账通道钉 | ★**已陈旧 (但有通道·不归本台账口径)**★ |
| `MECH/check_onepass_struct_crosscheck.py` | L73 | `HW/netlist_v1_pins.csv` | `a4270120454aedf7a23c92cd8985c8a6` | `9174309df1ec9411ac8e8d9e80ee386a` | P3 台账通道钉 | ★**已陈旧 (但有通道·不归本台账口径)**★ |

★**P3 那 3 处 (★`check_onepass_struct_crosscheck.py` L72/L73/L74★) 的写死基线【也是陈旧的】★ (★`37f62ac3…` / `a4270120…` / `5d02bece…` ≠ 盘上 `6aee500e…` / `9174309d…` / `5b999399…`★) ⇒ ★**但那正是 ISS-296/ISS-303 先例要治的病 (硬基线 ∪ 落表台账登记值 ⇒ 台账里那 3 个值是合法的) ⇒ 本单【不改】它, 只在这里登记一笔, 免得下一趟误以为盘面有第四批陈旧 pin。** ★ `[实测]`

### ★1.4 · ★★本页清账数与任务书 §一 那张表【不一致】(★差在哪·★为什么以本页为准★★) ★

| 项 | 任务书 §一 (main 手数) | 本页 (代码级枚举) | 差在哪 |
|---|---|---|---|
| 闸数 | ★**9 道** ★ | ★**11 道** ★ | ★**多出 2 道: `MECH/cavity_recalc_check.py` (5 处) + `MECH/display_biosafety_v2_check.py` (2 处)** ★ |
| pin 总数 | ★**35 处** ★ | ★**49 处 (P1 42 + P2 4 + P3 3)** ★ | ★**35 = 那 9 道闸里的数 (P1 口径下就是 35); 少的 7 处全在那 2 道漏数的闸里** ★ |

★**⇒ 结论: 任务书那张 35 处的表【少算了 7 处】, 但【那 3 处已陈旧 pin 的认定完全正确】(三处都在那 9 道闸里) ⇒ 本单的结论不受影响; 受影响的是「MECH 域到底有多少处硬钉」这个数。** ★ `[实测]`
★**⇒ 对新闸 M1 的直接影响: §1 在册清单必须登记 ★**42** ★ 处 (★不是 35★) ⇒ 少登记 7 处 ⇒ M1 立刻判红。** ★

### ★1.5 · ★机器块 (★新闸 M1/M4 读它·★人也能读★) ★

<!-- MECH-SIGNED-APPEND-LEDGER-INVENTORY-BEGIN -->
```json
{
  "pins": [
    {
      "gate": "MECH/cavity_recalc_check.py",
      "target": "MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md",
      "baseline": "96239070dc7c0ec00edb1b758a698769",
      "line": 93
    },
    {
      "gate": "MECH/cavity_recalc_check.py",
      "target": "MECH/display_biosafety_v2_check.py",
      "baseline": "29c77fc3fc823048b1d96c9500d28dd7",
      "line": 101
    },
    {
      "gate": "MECH/cavity_recalc_check.py",
      "target": "MECH/hinge_usb_check.py",
      "baseline": "3425bc141508de8a35f34c7cf7b803e8",
      "line": 94
    },
    {
      "gate": "MECH/cavity_recalc_check.py",
      "target": "MECH/hw_cross_review_check.py",
      "baseline": "e521387b87b0fcdf9f22d56f14199967",
      "line": 100
    },
    {
      "gate": "MECH/cavity_recalc_check.py",
      "target": "MECH/service_port_check.py",
      "baseline": "db58ff6a2afc28b8bf517e3c57c56bc1",
      "line": 99
    },
    {
      "gate": "MECH/check_connector_clearance_caliber.py",
      "target": "MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md",
      "baseline": "da7b02c013fa49c65b70ed3bea97b787",
      "line": 83
    },
    {
      "gate": "MECH/check_connector_clearance_caliber.py",
      "target": "MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md",
      "baseline": "ffc099397dc573df207f265bff57dffb",
      "line": 84
    },
    {
      "gate": "MECH/check_connector_clearance_caliber.py",
      "target": "MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md",
      "baseline": "b254fa98c09bc7adb058e1d03eb13980",
      "line": 87
    },
    {
      "gate": "MECH/check_connector_clearance_caliber.py",
      "target": "MECH/check_jdebug_1p27_clearance.py",
      "baseline": "a9914b2c3e9f8f92f1fbb60d1d8bdd86",
      "line": 85
    },
    {
      "gate": "MECH/check_connector_clearance_caliber.py",
      "target": "MECH/check_juart_1p27_clearance.py",
      "baseline": "ea89e0dd3b2f77828b69f06bbe76969d",
      "line": 86
    },
    {
      "gate": "MECH/check_debug_seat_3d_fit.py",
      "target": "HW/BOM_v1.csv",
      "baseline": "5b9993992405904a60ac96a020b375d8",
      "line": 94
    },
    {
      "gate": "MECH/check_debug_seat_3d_fit.py",
      "target": "HW/netlist_v1.csv",
      "baseline": "6aee500e60ba0732f83a9cf557ba90ab",
      "line": 92
    },
    {
      "gate": "MECH/check_debug_seat_3d_fit.py",
      "target": "HW/netlist_v1_pins.csv",
      "baseline": "9174309df1ec9411ac8e8d9e80ee386a",
      "line": 93
    },
    {
      "gate": "MECH/check_debug_seat_rework_spec.py",
      "target": "HW/BOM_v1.csv",
      "baseline": "5b9993992405904a60ac96a020b375d8",
      "line": 97
    },
    {
      "gate": "MECH/check_debug_seat_rework_spec.py",
      "target": "HW/netlist_v1.csv",
      "baseline": "6aee500e60ba0732f83a9cf557ba90ab",
      "line": 95
    },
    {
      "gate": "MECH/check_debug_seat_rework_spec.py",
      "target": "HW/netlist_v1_pins.csv",
      "baseline": "9174309df1ec9411ac8e8d9e80ee386a",
      "line": 96
    },
    {
      "gate": "MECH/check_demo_struct_truth.py",
      "target": "MECH/display_biosafety_v2_check.py",
      "baseline": "29c77fc3fc823048b1d96c9500d28dd7",
      "line": 92
    },
    {
      "gate": "MECH/check_demo_struct_truth.py",
      "target": "MECH/hinge_usb_check.py",
      "baseline": "3425bc141508de8a35f34c7cf7b803e8",
      "line": 83
    },
    {
      "gate": "MECH/check_demo_struct_truth.py",
      "target": "MECH/hw_cross_review_check.py",
      "baseline": "e521387b87b0fcdf9f22d56f14199967",
      "line": 91
    },
    {
      "gate": "MECH/check_demo_struct_truth.py",
      "target": "MECH/service_port_check.py",
      "baseline": "db58ff6a2afc28b8bf517e3c57c56bc1",
      "line": 90
    },
    {
      "gate": "MECH/check_fts_seat_body_geometry.py",
      "target": "HW/BOM_v1.csv",
      "baseline": "5b9993992405904a60ac96a020b375d8",
      "line": 94
    },
    {
      "gate": "MECH/check_fts_seat_body_geometry.py",
      "target": "HW/netlist_v1.csv",
      "baseline": "6aee500e60ba0732f83a9cf557ba90ab",
      "line": 92
    },
    {
      "gate": "MECH/check_fts_seat_body_geometry.py",
      "target": "HW/netlist_v1_pins.csv",
      "baseline": "9174309df1ec9411ac8e8d9e80ee386a",
      "line": 93
    },
    {
      "gate": "MECH/check_fts_seat_sample_plan.py",
      "target": "HW/BOM_v1.csv",
      "baseline": "5b9993992405904a60ac96a020b375d8",
      "line": 62
    },
    {
      "gate": "MECH/check_fts_seat_sample_plan.py",
      "target": "HW/netlist_v1.csv",
      "baseline": "6aee500e60ba0732f83a9cf557ba90ab",
      "line": 60
    },
    {
      "gate": "MECH/check_fts_seat_sample_plan.py",
      "target": "HW/netlist_v1_pins.csv",
      "baseline": "9174309df1ec9411ac8e8d9e80ee386a",
      "line": 61
    },
    {
      "gate": "MECH/check_fts_seat_sample_plan.py",
      "target": "MECH/BOARD_ONEPASS_FTS_SEAT_BODY_GEOMETRY.md",
      "baseline": "15697668d10368e971710069c9b73994",
      "line": 70
    },
    {
      "gate": "MECH/check_fts_seat_sample_plan.py",
      "target": "MECH/BOARD_ONEPASS_FTS_VS_GENERIC_COURTYARD_DELTA.md",
      "baseline": "0cb3ff2de940522b467ca3b01feda11c",
      "line": 71
    },
    {
      "gate": "MECH/check_fts_seat_sample_plan.py",
      "target": "MECH/check_fts_seat_body_geometry.py",
      "baseline": "1cdc6e9838419647e018c9a4c41319a2",
      "line": 66
    },
    {
      "gate": "MECH/check_fts_seat_sample_plan.py",
      "target": "MECH/check_fts_vs_generic_courtyard_delta.py",
      "baseline": "8f8424a5e632fa3d223271850109c6d0",
      "line": 67
    },
    {
      "gate": "MECH/check_fts_seat_sample_plan.py",
      "target": "MECH/check_onepass_mech_release.py",
      "baseline": "bd90741d38c6cd362d83e1f205cc21c5",
      "line": 68
    },
    {
      "gate": "MECH/check_fts_seat_sample_plan.py",
      "target": "MECH/check_onepass_mech_sync.py",
      "baseline": "5247486a6739d9b0cd5cf9a886c771e8",
      "line": 69
    },
    {
      "gate": "MECH/check_fts_vs_generic_courtyard_delta.py",
      "target": "HW/BOM_v1.csv",
      "baseline": "5b9993992405904a60ac96a020b375d8",
      "line": 36
    },
    {
      "gate": "MECH/check_fts_vs_generic_courtyard_delta.py",
      "target": "HW/netlist_v1.csv",
      "baseline": "6aee500e60ba0732f83a9cf557ba90ab",
      "line": 34
    },
    {
      "gate": "MECH/check_fts_vs_generic_courtyard_delta.py",
      "target": "HW/netlist_v1_pins.csv",
      "baseline": "9174309df1ec9411ac8e8d9e80ee386a",
      "line": 35
    },
    {
      "gate": "MECH/check_mech_dual_caliber_gate.py",
      "target": "MECH/hw_cross_review_check.py",
      "baseline": "e521387b87b0fcdf9f22d56f14199967",
      "line": 76
    },
    {
      "gate": "MECH/check_zoujuan_marker_consistency.py",
      "target": "MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md",
      "baseline": "96239070dc7c0ec00edb1b758a698769",
      "line": 61
    },
    {
      "gate": "MECH/check_zoujuan_marker_consistency.py",
      "target": "MECH/JBD_ROLE_NARROWING.md",
      "baseline": "bda4a29464336bc1452c913602ce3f46",
      "line": 62
    },
    {
      "gate": "MECH/check_zoujuan_marker_consistency.py",
      "target": "MECH/check_demo_struct_truth.py",
      "baseline": "fa9b59e593a13408ad9505d986276f63",
      "line": 63
    },
    {
      "gate": "MECH/check_zoujuan_marker_consistency.py",
      "target": "MECH/display_biosafety_v2_check.py",
      "baseline": "29c77fc3fc823048b1d96c9500d28dd7",
      "line": 60
    },
    {
      "gate": "MECH/display_biosafety_v2_check.py",
      "target": "MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md",
      "baseline": "96239070dc7c0ec00edb1b758a698769",
      "line": 55
    },
    {
      "gate": "MECH/display_biosafety_v2_check.py",
      "target": "MECH/JBD_ROLE_NARROWING.md",
      "baseline": "bda4a29464336bc1452c913602ce3f46",
      "line": 56
    }
  ]
}
```
<!-- MECH-SIGNED-APPEND-LEDGER-INVENTORY-END -->

★**这个块是「判据面」: 新闸 M1 要求盘上扫到的每一处 P1 pin 都在册 (少一处 ⇒ 新闸能从缝里溜过去 ⇒ 判红); M4 用它当【登记基线】, 闸里常量一旦与它不同 ⇒ 就是「悄悄换基线」⇒ 判红。** ★
★**⇒ 所以本页与新闸必须同源: 本页的 §1.5 由 `tmp/iss399/gen_truth_page.py` 从新闸自己的枚举器生成 ⇒ 两者不可能各写各的。** ★ `[实测]`

---

## ★§2 · 三处已陈旧 pin 的逐条裁定 ★

### ★2.0 · 裁定用到的【证据链】清单 (★全是本机实读·★不是抄报告★) ★

| 证据 | 出处 | 能证明什么 |
|---|---|---|
| ★**E1** ★ | `state/.verify/sign_iss374_selftest.txt` (★mtime `2026-11-24 02:26:45`★) 里的护栏行: 「`MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md` 逐字节未变 (md5 `ffc09939…`)」 | ★**2026-11-24 02:26:45 那一刻, 该页的 md5 = `ffc09939…`** ★ `[实测]` |
| ★**E2** ★ | `tmp/iss377/selftest/M1/MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md` (★md5 `ffc09939…`·mtime `2026-11-24 01:23:23`★) 与 `tmp/iss377/selftest/M1/MECH/check_juart_1p27_clearance.py` (★md5 `ea89e0dd…`·mtime `2026-11-24 01:24:52`★) | ★**两份【改动前】的逐字节副本还在盘上 ⇒ 可以直接 diff ⇒ 这是本单能给出【逐字级】结论的唯一原因** ★ `[实测]` |
| ★**E3** ★ | `HANDOFF/2026-11-23_mech-lead_ISS374_JUART排针1.27净距真相.md` ⑬ 交付物 md5 台账 (★mtime `2026-11-24 04:17:43`★): `f1ce54c9…` / `daf8fa36…` | ★**ISS-374 cont2 交卷时, 这两个文件已经是新 md5 ⇒ 变更【已披露】** ★ `[实测]` |
| ★**E4** ★ | 同页 §B6.2 事故与回滚记录末条: 「交卷时的最终状态: 板 / 页 / CRIT 真身 三者逐字节回到基线 (`md5 611b869e…` / `md5 ffc09939…` / `md5 db58ff6a…`)」 | ★**ISS-374 在 01:2x 那次沙盒穿透事故后, 曾把该页【逐字节回滚】到 `ffc09939…`** ★ `[实测]` |
| ★**E5** ★ | `HANDOFF/2026-11-24_mech-lead_ISS382_JDEBUG排针排布标签订正与G5盲区.md` 验收第 11 条: 「`K7` 基线红 2 条是开工前就有的 (ISS-374 cont2 追加已签收页所致)」 | ★**上游 agent 已经把这两条红归因过一次, 但【归因没有落进任何台账】⇒ 所以红一直挂着** ★ `[实测]` |
| ★**E6** ★ | `MECH/check_connector_clearance_caliber.py` 自身 mtime `2026-11-24 03:31:08` + 它的 `SIGNED_BASELINE` 字典 (★L82-L88★) 注释「★已签收件的逐字节基线 (★ISS-371 / ISS-374 已由 main 签收 verified·★K7 专防「改已签收件」★)★」 | ★**钉基线的那道闸, 是在 03:31:08 写的; 那一刻该页还是 `ffc09939…` ⇒ 它当时【钉对了】** ★ `[实测]` |
| ★**E7** ★ | `HANDOFF/2026-11-17_mech-lead_ISS296_合法改板机制与收工重锚.md` 第 16 行 / 第 34 行: 「`MECH/check_demo_struct_truth.py` (改: 合法改板路径) ✅ 已完成 (20:25:32)」+ 「72,428 B · 2026-11-17 20:25:32 · G5b 通道」 | ★**第三处陈旧 pin 的作者 = ISS-296, 改动内容 = 把 G5b 接到落表台账通道** ★ `[实测]` |
| ★**E8** ★ | `HANDOFF/2026-11-17_mech-lead_ISS295_结构输入认领与防漂闸.md` §B7.5 表格: `check_demo_struct_truth.py` · `2026-11-17 20:25:32` · `483d018a…` · 谁改的 = ★**别的单** ★ | ★**ISS-295 自己把它记成「别的单」⇒ 当时就没人去回头更新钉它的基线** ★ `[实测]` |
| ★**E9** ★ | `MECH/check_zoujuan_marker_consistency.py` 自身 mtime `2026-11-16 10:59:26` | ★**第三处陈旧 pin 的钉基线闸写在 2026-11-16 10:59 ⇒ 早于 11-17 20:25 的那次改动 9.4 小时 ⇒ 它【当时钉对了】** ★ `[实测]` |

---

### ★2.1 · pin #1 — `MECH/check_connector_clearance_caliber.py` L84 钉 `MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md` ★

★**闸里写死**: `ffc099397dc573df207f265bff57dffb` · ★**盘上现值**: `f1ce54c981dd1f64071a177a374df85d` ★ `[实测]`

#### ★2.1.1 · 它是不是合法动作? ★

★**是合法动作, 但★**不是【纯追加】★** —— 这是本单最要紧的一条发现。** ★

★**用 E2 的改动前副本直接 diff (★本机实跑, ★不是推算★):** ★
```
$ diff tmp/iss377/selftest/M1/MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md \
       MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md
  ⇒ 新增 51 行 / 删掉 9 行  (★改前 361 行 30,549 B ⇒ 改后 403 行 37,640 B★)
```
★**那 9 行【被删掉的】老字是** (★逐字★):
1. L96 一行: `| fab 外框 (含笔画) | X 18.0198..23.4602 (5.4404) × Y 67.4500..72.5500 (5.1000) [实测] | 同左 [实测] |` ⇒ 被替换成【两行】: 「座体本体外框 (F.Fab 轮廓线·不含文字) X 19.4200..22.0600 (2.6400)」+「(留档) F.Fab 层全框 (含 Reference 文字) X 18.0198..23.4602 (5.4405)」
2. L109 一行表头: `| 档 | 铜箔 X 宽 | … | fab 外框 (X × Y) | ≥ CRIT 0.60 ? |` ⇒ 改成 `| ★座体本体外框 (X × Y)★ |`
3. L112 / L113 / L114 三行数据行: 外框列的 `5.4404 × 2.2000` / `5.4404 × 5.1000` / `5.4404 × 5.1000` ⇒ 改成 `2.6400 × 2.2000` / `2.6400 × 5.1000` / `2.6400 × 5.1000`

★**⇒ 老字【不是】逐字保留的: 有 5 行被【就地替换】了 (值从 `5.4404` 改成 `2.6400`)。** ★ `[实测]`
★**⇒ 但【旧值仍然查得到】**: 新页 §7 明确写着「文字全框只作留档, 不进结构判断: S1/S2 = `5.4405` × (`2.2000` / `5.1000`)」⇒ ★**值留档了, 只是行被替换了。** ★ `[实测]`
★**⇒ 且【结论数一个字没动】**: 余量 `0.1350` / `-0.1650` / `0.3100` / `0.0100` 与三条判决 (THT 不过 / SMD 不过 / SMD 不过) 在改前改后逐字相同 ⇒ ★**这次订正改的是「座体本体外框」的口径, 不是结论。** ★ `[实测]`

★**谁干的**: ★**ISS-374 cont2** (★真件 mtime `2026-11-24 04:12:52`★) ⇒ 该单的交卷页 ⑬ 逐字记录了交卷时的 md5 `f1ce54c9…` (E3) ⇒ ★**已披露。** ★
★**为什么是它**: ★**时间线闭合** —— 02:26:45 签收快照 = `ffc09939…` (E1) → 03:31:08 钉基线的闸写下去, 那一刻还是 `ffc09939…` (E6) → 04:12:52 页被订正成 `f1ce54c9…` (E3) ⇒ ★**闸是在【改动之前】写的, 改动落在【闸写完之后】⇒ 基线从此永久陈旧。** ★ `[实测]`

#### ★2.1.2 · 如果合法, 为什么没人更新基线? ★

★**因为 MECH 域【没有一本账】。** ★
★**具体是三件事叠在一起: ①** 这次变更的记录只落在【交卷页】里 (E3), 交卷页不是【判决源】, 闸不会去读它; ★**②** 钉基线的那道闸 (`check_connector_clearance_caliber.py`) 是 ★**零挂链** 的 (★`grep -c check_connector_clearance_caliber state/gate_check.py` = 0★) ⇒ 它的红【零通知】; ★**③** 下一个跑这道闸的 agent (ISS-382) 只能在自己的交卷页里写一句「这红不是我造成的」 (E5) ⇒ ★**归因写在了【又一张交卷页】里, 还是不是判决源 ⇒ 下一个 agent 还得再猜一遍。** ★ `[实测]`
★**⇒ 病根不是「忘了更新基线」, 是「没有【能落表的地方」⇒ 每次都要靠人肉考古。** ★

#### ★2.1.3 · 裁定 ★

★**合法性: ★合法但【不是纯追加】★ (★见 §2.4 的汇总★)。** ★
★**K7 判据评价: ★**该判据此刻的红是【正确】的 —— 文件确实被改了 ⇒ 「逐字节 md5 不变」这句话描述的事实成立。★ ★**但它作为【判决源】是坏的**: 它把「合法的口径订正」和「有人偷改已签收件」判成了同一件事 ⇒ ★**⇒ 处置方向不是「把基线改成新值」, 是「把判决源从写死常量换成台账链头」 (见 §3.4 + §4 补丁 ②)。** ★

---

### ★2.2 · pin #2 — `MECH/check_connector_clearance_caliber.py` L86 钉 `MECH/check_juart_1p27_clearance.py` ★

★**闸里写死**: `ea89e0dd3b2f77828b69f06bbe76969d` · ★**盘上现值**: `daf8fa367d89e22f6d3af3d5049bdfb6` ★ `[实测]`

#### ★2.2.1 · 它是不是合法动作? ★

★**合法, 且【改动面比 #1 还小】。** ★
★**用 E2 的改动前副本直接 diff (★本机实跑★):** ★
```
$ diff tmp/iss377/selftest/M1/MECH/check_juart_1p27_clearance.py \
       MECH/check_juart_1p27_clearance.py
1030,1031c1030,1031
<  mutate=lambda d: _mut_page(d, '"pass_nominal": false, "pass_worst": false,\n     "fab_x": 5.4404',
<                               '"pass_nominal": true, "pass_worst": false,\n     "fab_x": 5.4404'))
---
>  mutate=lambda d: _mut_page(d, '"pass_nominal": false, "pass_worst": false,\n     "fab_body_x": 2.6400',
>                               '"pass_nominal": true, "pass_worst": false,\n     "fab_body_x": 2.6400'))
  ⇒ 行数【一模一样】(1,098 行) · size 51,899 B → 51,909 B (★只 +10 B★) ⇒ 只改了 1 处、2 行
```
★**⇒ 改的只有【`--selftest` 里那条变异夹具的字段名与取值】(`fab_x` / `5.4404` → `fab_body_x` / `2.6400`); ★★九条判据 J0~J9 的【判据逻辑、阈值、判决顺序】一个字没动。** ★ `[实测]`
★**⇒ 但严格说: 它也不是【逐字节未动】的已签收闸 —— 是一道【被就地改过 2 行】的已签收闸。** ★ `[实测]`

#### ★2.2.2 · 如果合法, 为什么没人更新基线? ★

★**与 §2.1.2 完全同因** (★同一个闸、同一个 `SIGNED_BASELINE` 字典、同一段时间窗、同一批单★) ⇒ **不多述。** ★

#### ★2.2.3 · 裁定 ★

★**合法性: ★合法·改动面 2 行·只动自测夹具·判据逻辑零改动·已披露。** ★
★**★但它证明了另一件事: 闸的【自测夹具】跟着真相页的字段名走 ⇒ ★**真相页字段一改名, 闸就必须跟着改 ⇒ 「已签收闸逐字节不许动」这条规矩【本身就和「真相页可以订正」互斥】。** ★ ★**⇒ 这不是执行问题, 是【口径互斥】问题 ⇒ 必须改判据 (M-D)。** ★

---

### ★2.3 · pin #3 — `MECH/check_zoujuan_marker_consistency.py` L63 钉 `MECH/check_demo_struct_truth.py` ★

★**闸里写死**: `fa9b59e593a13408ad9505d986276f63` · ★**盘上现值**: `483d018a66d17d2ead25d1558a1f8ffe` ★ `[实测]`

#### ★2.3.1 · 它是不是合法动作? ★

★**合法, 而且它是【本仓已经治过一次的同型病】的另一个面。** ★

★**谁干的**: ★**ISS-296** (★`HANDOFF/2026-11-17_mech-lead_ISS296_合法改板机制与收工重锚.md` 第 16 行 + 第 34 行, E7★) ⇒ ★**改动内容 = 把 `check_demo_struct_truth.py` 的 G5b / C21 接到【落表台账通道】(★「合法改板路径」★) ⇒ 该单自报「主跑 rc=0 · `--selftest` rc=0 · 末行反向用例 28/28 抓到了」⇒ ★**已披露、已自证。** ★ `[实测]`
★**ISS-295 的交卷页把它记成「别的单」并留下「现在 mtime / 现在 md5 / 谁改的」三列 (E8) ⇒ ★**归因意识有, 落表没有。** ★ `[实测]`

★**时间线闭合**: ★**2026-11-16 03:55:42 该闸 md5 = `fa9b59e5…` (ISS-245 交卷页逐字记录) → 2026-11-16 10:59:26 `check_zoujuan_marker_consistency.py` 写下并钉住 `fa9b59e5…` (E9) ⇒ ★**钉的时候是对的 → 2026-11-17 20:25:32 ISS-296 改造该闸 ⇒ 基线从那一刻起永久陈旧。** ★ `[实测]`

★**★为什么这次特别值得记: ISS-296 干的事【恰恰就是】给 `check_demo_struct_truth.py` 接「硬基线 ∪ 落表台账登记值」通道 ⇒ ★**也就是说: 「用台账替代写死常量」这个解法【早就已经在 MECH 域自己身上被实现过一次了】★ ⇒ 本单 §3 的设计不是新发明, 是【把 ISS-296 的做法搬进 MECH 域自己的台账】。** ★ `[实测]`

#### ★2.3.2 · 如果合法, 为什么没人更新基线? ★

★**与 §2.1.2 同因。** ★
★**★但这一处多一层讽刺: 改造 `check_demo_struct_truth.py` 的那件事本身就是为了【消灭写死常量】, 而它自己被另一道闸写死着 ⇒ ★**病治好了病, 病又长在了治病的刀上。** ★ ★**⇒ 这正是本单 §3 要给 MECH 域自己开一本账的理由: 闸之间互相钉 ⇒ 必须有一本【谁钉了谁】的账, 否则【每治好一处就多一处新的陈旧】。** ★ `[实测]`

#### ★2.3.3 · 裁定 ★

★**合法性: ★合法·已披露·已自证·而且是「治同型病」的那个动作本身。** ★
★**K5 判据评价: 同 §2.1.3 ⇒ ★**红是【正确】的 (文件确实被改了), 但判决源【坏了】(把合法改造与偷改判成同一件事)。** ★

---

### ★2.4 · ★★三条裁定的汇总表 + 一个必须写下来的核心结论 ★★

| # | pin | 写死基线 → 现值 | 是不是合法动作 | 变更性质 | 已披露? | 裁定 |
|---|---|---|---|---|---|---|
| ★**1** ★ | `check_connector_clearance_caliber.py` L84 → `BOARD_ONEPASS_JUART_1P27_CLEARANCE.md` | `ffc09939…` → `f1ce54c9…` | ★**是** (ISS-374 cont2) ★ | ★**局部替换 (5 行就地改写) + 尾部追加 §7** ★ | ★**是** (交卷页 ⑬) ★ | ★**红正确 · 判决源该换** ★ |
| ★**2** ★ | `check_connector_clearance_caliber.py` L86 → `check_juart_1p27_clearance.py` | `ea89e0dd…` → `daf8fa36…` | ★**是** (ISS-374 cont2) ★ | ★**局部替换 (2 行·只动 selftest 夹具)** ★ | ★**是** (交卷页 ⑬) ★ | ★**红正确 · 判决源该换** ★ |
| ★**3** ★ | `check_zoujuan_marker_consistency.py` L63 → `check_demo_struct_truth.py` | `fa9b59e5…` → `483d018a…` | ★**是** (ISS-296) ★ | ★**判决源改造 (接落表台账通道)** ★ | ★**是** (ISS-296 交卷页) ★ | ★**红正确 · 判决源该换** ★ |

★**★★ 核心结论 (★本单最值钱的一条·★写给 main 看★★): ★★

★**① 这 3 处【没有一处】是「纯字节追加」—— 任务书 §一③ 说的「ISS-374 cont2 做的是【追加式订正】(★house 规矩: 追加式订正·老字一字未删★)」这个描述, 在本机逐字节 diff 下【不成立】: #1 有 5 行老字被就地替换, #2 有 2 行被就地替换, #3 是判决源改造。** ★ `[实测]`
★**⇒ ⇒ 这条 house 规矩本身需要被重新定义**: ★**「追加式订正」在 MECH 域的合法形态至少有三种 (纯追加 / 局部替换 / 判决源改造), 而「老字一字未删」只是其中最窄的一种。** ★
★**⇒ ⇒ ★★**台账的字段设计因此不能只记 `prev_md5 → md5` + 「老字逐字未删」的自证 —— 那三条自证【一条都过不了】(★过不了 = 永远判红 = 这道闸还是没治好病★)。台账必须改记: 「改动性质」+「旧值是否留档」+「是否已在交卷页披露 (给 md5 台账行号)」+「判定结论数有没有变」。** ★ ★**这四条才是能对得上现实的自证。** ★
★**② 这 3 处的红【全部正确】(文件确实被改了) ⇒ ★**绝不能靠「把基线常量直接改成现值」来消红** —— 那正是新闸 M4 要打的那一枪 (★§4 补丁 ① + 闸 `--selftest` 的 c06 用例★)。** ★
★**③ 三处的【共同病根】不是「忘了更新基线」, 是 ★**MECH 域没有一本【谁钉了谁】的账**★ ⇒ 三处红至今没人归因 ⇒ ★**⇒ 本单 §3 的台账是唯一的结构性解法。** ★

---

## ★§3 · MECH 域【已签收件追加登记台账】设计 ★

### ★3.1 · 台账长什么样 (★原子记录字段·★字段设计理由逐条给★) ★

★**载体 = 一个 Markdown 文件, 一张 append-only 表 (★追加只许往后加行·不许改老行·不许删行★)。** ★
★**表头 (★必须一字不差·★闸按这个表头解析★):** ★
```
| 单号 | 文件 | prev_md5 | md5 | 追加类型 | 追加位置 | 自证 |
```
★**逐字段的设计理由 (★★其中两个字段是本单对任务书建议的【修正】★★):** ★

| # | 字段 | 含义 | 为什么必须有它 | ★**与任务书建议的差别** ★ |
|---|---|---|---|---|
| 1 | ★**单号** ★ | 谁干的 (`ISS-nnn`) | ★**没有单号的追加 = 「来源不明的漂移」⇒ 判红** ★ | 同 |
| 2 | ★**文件** ★ | 被追加/被改的文件的仓内相对路径 | 台账按文件索引链 | 同 |
| 3 | ★**prev_md5** ★ | 改之前的 md5 | 链的上一环 | 同 |
| 4 | ★**md5** ★ | 改之后的 md5 | 链的当前环 | 同 |
| 5 | ★**追加类型** ★ | ★**枚举: `纯字节追加` / `局部订正`** ★ | ★**它把「这次变更是什么性质」写进账里 ⇒ 闸可以用它区分【纯追加】与【就地替换】** ★ | ★**任务书原文是「追加位置」一栏+「老字逐字未删」的自证方式; 本单把它拆成 5+7 两栏 (★理由见下条★)** ★ |
| 6 | ★**追加位置** ★ | 追加/改动落在文件的哪一段 (★如「§7 追加块」/「§2 表格 5 行就地替换」/「L1030-L1031 selftest 夹具」★) | ★**让下一个 agent 一眼看出这次动的是哪块** ★ | ★**同上** ★ |
| 7 | ★**自证** ★ | ★**一条可机器判的句子, 必须含: ①旧值是否留档 (含旧值所在位置) ②是否已在交卷页披露 (给交卷页 + md5 台账行号) ③判定结论数有没有变 (有/无 + 变了几处)** ★ | ★**这才是【对得上现实】的自证** ★ | ★**★任务书原文写的是「「老字逐字未删」的自证方式」★ ⇒ ★**本单建议改掉: 三处陈旧 pin 里【没有一处】是纯追加 ⇒ 这条自证【永远过不了】⇒ 台账会永远判红 ⇒ 等于没设计** ★** ⇒ 换成上面三条 (★逐条都有盘上证据可查★)** ★ |

★**★附: 台账本体还要有一条【自述块】 (★闸只读那张表·自述块是给人看的★):** ★
★**- 这本账由谁写 (★待 M-A 拍★) · 每一次追加必须同一次提交通过分片登记 (★`state/frag_write.py`★) · 谁有权改老行: 【没有人】。** ★

### ★3.2 · 台账放哪 / 叫什么 / 谁写 (★★本单只提方案·★不替 main 拍★★) ★

| 候选 | 优点 | 缺点 | 本单的倾向 |
|---|---|---|---|
| ★**A. 新建 `MECH/SIGNED_APPEND_LEDGER.md`** ★ | ★**MECH 域自己的账 ⇒ 跟 MECH 域的判决源放在一起 ⇒ 闸读它是【同域】读盘** ★ | 要新建一个文件 | ★**★建议默认值** ★ |
| B. 复用 `HW/SCHEMATIC_LANDING_V1_LANDED.md` 的 MECH 段 | 不新建文件 | ★**那本是【板侧落表台账】; MECH 页的追加式订正【不是落表】⇒ 塞进去会污染板那条链 ⇒ 而且板侧那条链有它自己的 fail-closed 口径** ★ | 不建议 |
| C. 放 `state/` 下 | 跟门禁机制同域 | ★**MECH 域的判据源应该在 MECH 域; 放 state 会让「闸读自己域的账」变成跨域读** ★ | 不建议 |

★**⇒ 新闸 `check_mech_signed_append_ledger.py` 已按建议默认值 A 实现 (`LEDGER_REL = "MECH/SIGNED_APPEND_LEDGER.md"`) ⇒ ★**main 拍别的路径, 改这一个常量即可 (★不改任何判据★)。** ★
★**★M-A 待 main 拍: 放哪 / 叫什么 / 谁写。★★**

### ★3.3 · fail-closed 口径 (★判红的四种情形·★与 SW 侧 `SW_MD5_BASELINE_LEDGER.md` 同形★) ★

| # | 情形 | 判决 |
|---|---|---|
| 1 | ★**台账读不到** (文件不存在 / 记录块标记缺失 / 表头不是规定表头) | ★**判红** (★fail-closed: 没有账 = 没有归因 = 一切陈旧 pin 都判红★) ★ |
| 2 | ★**链断了** (上一行 `md5` ≠ 下一行 `prev_md5`) | ★**判红** |
| 3 | ★**链头不唯一 / 链头无单号** (某行 `单号` 不合 `ISS-[0-9]+`) | ★**判红** |
| 4 | ★**链头 ≠ 盘上现值** (台账说文件现在是 X, 盘上是 Y) | ★**判红** (★真源被换了 / 台账没跟上★) |

★**⇒ 这四条已经逐条实现在新闸 M3 里 (★`load_ledger()` / `chain_state()` / `ledger_match()`★) ⇒ 闸自带 `--selftest` 的 c03/c04/c05/c10 四条反向用例逐条打它们。** ★ `[实测]`

### ★3.4 · ★判决源怎么从「写死常量」换成「硬基线 ∪ 台账链头」★

★**判据的形状 (★照 ISS-303 `N6` 的先例·★照 ISS-372 `H4/H5` 的形状★):** ★
```
改前 (写死常量):     判决 = (md5_of(被钉文件) == 写死常量)
改后 (硬基线 ∪ 链头): 判决 = (md5_of(被钉文件) == 写死硬基线)
                       OR (md5_of(被钉文件) == 台账链头)
                       AND (台账链完整 AND 链头有单号)
```
★**★为什么要「∪」而不是「换」: 写死常量是【签收锚点】(★它证明「这块内容自签收以来没人动过」★) ⇒ ★**它不能被删掉; 要加的是「除非台账里有一次已登记的合法追加」这一条出路。** ★
★**★M4 那道护栏管的是【另一半】: ★**即使有人把写死常量直接改成现值 (★这样 md5 恒等 ⇒ 判据永远绿★), 只要台账里没有对应的一行 (★`prev` = 登记基线、`md5` = 新常量★), 本闸照样判红。** ★ ★**⇒ 「悄悄换基线」这条路被堵死。** ★

---

## ★§4 · 逐字补丁 (★三条·★**不应用**·★本单【不许】动那 11 道闸的任何一行★) ★

> ★**适用**: 补丁 ②③ 各自需要补丁 ① 的 helper。★**落法**: ★**先落 ① (新建一个只读 helper), 再落 ②③ (各改 1 处判决函数 + 1 处常量)。** ★
> ★**★落这些补丁的前提是 M-A / M-B 拍完 (★台账得先有地方落·★链头得先有值★) ⇒ 本单【不落】。** ★

### ★★补丁 ① · 新建 `MECH/mech_signed_append_ledger_reader.py` (★只读 helper·★只落一份·★两处判决共用★★) ★

★**新建文件 (★零改既有闸·★只加只读工具★)。** ★
★**改前: 【无此文件】★ ⇒ ★**改后 (★全文·★新建★):** ★
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''MECH/mech_signed_append_ledger_reader.py —— 【已签收件追加登记台账】只读读取器

★性质★: 只读 · 零写板 · 零落表 · 零改任何既有闸 · 不代拍
★用途★: 给 MECH 域各道闸提供【台账链头】, 让「写死常量」判据长出【已登记的合法追加】这一条出路
★台账路径★: MECH/SIGNED_APPEND_LEDGER.md   (★路径是常量·★M-A 待 main 拍·★改这一行即可★)
'''
import hashlib
import os
import re

LEDGER_REL = "MECH/SIGNED_APPEND_LEDGER.md"
REC_BEGIN = "<!-- MECH-SIGNED-APPEND-LEDGER-RECORDS-BEGIN -->"
REC_END = "<!-- MECH-SIGNED-APPEND-LEDGER-RECORDS-END -->"
REC_HEADER = ("单号", "文件", "prev_md5", "md5", "追加类型", "追加位置", "自证")
APPEND_KINDS = ("纯字节追加", "局部订正")
MD5RE = re.compile(r"^[0-9a-f]{32}$")


def md5_of(path):
    h = hashlib.md5()
    try:
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                h.update(chunk)
    except OSError:
        return None
    return h.hexdigest()


def load_records(root):
    '''读台账记录块。返回 (ok, why, records)'''
    path = os.path.join(root, LEDGER_REL)
    if not os.path.exists(path):
        return False, "台账 %s 不存在" % LEDGER_REL, []
    with open(path, encoding="utf-8", errors="replace") as fh:
        txt = fh.read()
    i, j = txt.find(REC_BEGIN), txt.find(REC_END)
    if i < 0 or j < 0 or j < i:
        return False, "台账 %s 缺记录块标记" % LEDGER_REL, []
    rows, header_seen = [], False
    for ln in txt[i + len(REC_BEGIN):j].splitlines():
        s = ln.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if not header_seen:
            header_seen = tuple(cells[:7]) == REC_HEADER
            continue
        if set("".join(cells)) <= set("-: ") or len(cells) < 7:
            continue
        rows.append({"iss": cells[0], "file": cells[1].replace("\\", "/"),
                     "prev": cells[2].lower(), "md5": cells[3].lower(),
                     "kind": cells[4], "where": cells[5], "proof": cells[6]})
    if not header_seen:
        return False, "台账 %s 的表头不是规定表头" % LEDGER_REL, []
    return True, "", rows


def chain_head(root, target):
    '''返回 (ok, why, head_md5)。★fail-closed: 链断 / 链头无单号 / 类型不在枚举 ⇒ 判红★'''
    ok, why, rows = load_records(root)
    if not ok:
        return False, why, None
    recs = [r for r in rows if r["file"] == target]
    if not recs:
        return False, "台账里没有 %s 的记录" % target, None
    for r in recs:
        if not re.match(r"^ISS-[0-9]+", r["iss"]):
            return False, "台账 %s 有一行缺单号" % target, None
        if r["kind"] not in APPEND_KINDS:
            return False, "台账 %s 有一行的追加类型不在枚举内" % target, None
    for a, b in zip(recs, recs[1:]):
        if a["md5"] != b["prev"]:
            return False, "台账 %s 的链断了" % target, None
    return True, "", recs[-1]["md5"]


def baseline_ok(root, target, hard_baseline):
    '''★判决式: 硬基线 ∪ 台账链头。★任一条成立即算【未被偷改】★'''
    got = md5_of(os.path.join(root, target))
    if got is None:
        return False, "%s 读不到" % target
    if got == hard_baseline:
        return True, "命中硬基线 %s" % hard_baseline[:8]
    ok, why, head = chain_head(root, target)
    if ok and head == got:
        return True, "命中台账链头 %s" % head[:8]
    if not ok:
        return False, "台账判决失败: %s" % why
    return False, "md5 %s 既不等于硬基线 %s, 也不等于台账链头 %s" % (got[:8], hard_baseline[:8], head[:8])
```

### ★★补丁 ② · `MECH/check_connector_clearance_caliber.py` (★覆盖 §2.1 / §2.2 两处陈旧 pin★) ★

★**改前 (★L81-L88 逐字★):** ★
```python
# ★已签收件的逐字节基线 (★ISS-371 / ISS-374 已由 main 签收 verified·★K7 专防「改已签收件」★)★
SIGNED_BASELINE = {
    JDEBUG_REL: "da7b02c013fa49c65b70ed3bea97b787",
    JUART_REL: "ffc099397dc573df207f265bff57dffb",
    GATE_JDEBUG_REL: "a9914b2c3e9f8f92f1fbb60d1d8bdd86",
    GATE_JUART_REL: "ea89e0dd3b2f77828b69f06bbe76969d",
    CALIBER_REL: "b254fa98c09bc7adb058e1d03eb13980",
}
```
★**改后 (★同一位置·★硬基线一个都不删·★只加注释标明它是【签收锚点】而不再是唯一出路★):** ★
```python
# ★已签收件的逐字节基线 (★ISS-371 / ISS-374 已由 main 签收 verified·★K7 专防「改已签收件」★)
# ★★ISS-399 口径订正 (★不删任何常量·★只把 K7 的判决源从【写死常量】换成【硬基线 ∪ 台账链头】★★)
#   ★ISS-374 cont2 (2026-11-24 04:12/04:13) 对该页与该闸做过一次【已披露的】口径订正 ⇒
#   ★本字典是 03:31:08 写下来的签收锚点 ⇒ 与盘上现值不同【不是】有人偷改 ⇒
#   ★⇒ 判据改成: 命中硬基线【或】命中台账链头 ⇒ 合法追加不再永久红·偷改照样红★
SIGNED_BASELINE = {
    JDEBUG_REL: "da7b02c013fa49c65b70ed3bea97b787",
    JUART_REL: "ffc099397dc573df207f265bff57dffb",
    GATE_JDEBUG_REL: "a9914b2c3e9f8f92f1fbb60d1d8bdd86",
    GATE_JUART_REL: "ea89e0dd3b2f77828b69f06bbe76969d",
    CALIBER_REL: "b254fa98c09bc7adb058e1d03eb13980",
}
```
★**改前 (★L642-L653 逐字★):** ★
```python
    # ---------------- K7 ----------------
    def k7(self):
        bad = []
        for rel, want in SIGNED_BASELINE.items():
            path = p(self.root, rel)
            if not os.path.exists(path):
                bad.append("%s 不存在" % rel)
                continue
            got = md5_of(path)
            if got != want:
                bad.append("%s md5 %s != 已签收基线 %s" % (rel, got, want))
        return self.chk("K7", not bad, "; ".join(bad) if bad else "已签收页/闸逐字节未变")
```
★**改后 (★★判据句从「不许改」改成「不许【悄悄】改」★★):** ★
```python
    # ---------------- K7 ----------------
    def k7(self):
        bad = []
        for rel, want in SIGNED_BASELINE.items():
            path = p(self.root, rel)
            if not os.path.exists(path):
                bad.append("%s 不存在" % rel)
                continue
            got = md5_of(path)
            if got == want:
                continue
            # ★ISS-399 口径订正: 硬基线 ∪ 台账链头 (★合法追加不再永久红★)
            ok, why = ledger_reader.baseline_ok(self.root, rel, want)
            if not ok:
                bad.append("%s md5 %s != 已签收基线 %s (%s)" % (rel, got, want, why))
        return self.chk("K7", not bad, "; ".join(bad) if bad else "已签收页/闸逐字节未变 (或已在台账登记的合法追加)")
```
★**还要加两行 import (★L1x 区·★在 `import` 段里★):** ★
```python
import mech_signed_append_ledger_reader as ledger_reader
```
★**★判定线没有动: 「偷改一个字节 ⇒ 必须红」这条【没松】—— 补丁 ① 的 `baseline_ok()` 在台账判决失败时返回 False ⇒ 判红。** ★
★**★但要注意一个代价 (★交 main 裁决·★本单不代拍★): ★**台账一旦存在, 台账【链头】就成了新的合法基线 ⇒ 台账本身被改坏 = 全域判红 ⇒ ★**台账的写权限必须比闸还紧 (★这是 M-A「谁写」那一问的真正代价)。** ★

### ★★补丁 ③ · `MECH/check_zoujuan_marker_consistency.py` (★覆盖 §2.3 那处陈旧 pin★) ★

★**改前 (★L59-L64 逐字★):** ★
```python
# 受保护文件 md5 (交卷前逐字节不变)
GUARDED = {
    "MECH/display_biosafety_v2_check.py": "29c77fc3fc823048b1d96c9500d28dd7",
    "MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md": "96239070dc7c0ec00edb1b758a698769",
    "MECH/JBD_ROLE_NARROWING.md": "bda4a29464336bc1452c913602ce3f46",
    "MECH/check_demo_struct_truth.py": "fa9b59e593a13408ad9505d986276f63",
}
```
★**改后 (★硬基线一个都不删·★只加注释★):** ★
```python
# 受保护文件 md5 (交卷前逐字节不变)
# ★★ISS-399 口径订正 (★不删任何常量·★K5 的判决源改成【硬基线 ∪ 台账链头】★★)
#   ★MECH/check_demo_struct_truth.py 于 2026-11-17 20:25:32 被 ISS-296 改造为
#   ★【G5b 落表台账通道】(★已披露·★该单自报 rc=0 + 反向用例 28/28★)
#   ★⇒ 本条基线是 2026-11-16 10:59:26 写下来的签收锚点 ⇒ 与现值不同【不是】有人偷改★
GUARDED = {
    "MECH/display_biosafety_v2_check.py": "29c77fc3fc823048b1d96c9500d28dd7",
    "MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md": "96239070dc7c0ec00edb1b758a698769",
    "MECH/JBD_ROLE_NARROWING.md": "bda4a29464336bc1452c913602ce3f46",
    "MECH/check_demo_struct_truth.py": "fa9b59e593a13408ad9505d986276f63",
}
```
★**改前 (★L259-L273 逐字★):** ★
```python
# ---------------------------------------------------------------- [K5] 受保护文件 md5 未变
def check_k5(root: str):
    bad = []
    for rel, want in sorted(GUARDED.items()):
        p = os.path.join(root, rel)
        if not os.path.exists(p):
            bad.append("%s 缺失" % rel)
            continue
        got = _md5(p)
        if got != want:
            bad.append("%s md5 %s≠%s" % (rel, got, want))
    ok = not bad
    detail = ("受保护文件 md5 逐字节未变 (%d 个): %s"
              % (len(GUARDED), ", ".join("%s=%s…" % (r.split("/")[-1], v[:8]) for r, v in sorted(GUARDED.items())))
              if ok else "受保护文件被改: " + " ; ".join(bad))
    return ok, detail
```
★**改后 (★★判据句从「不许改」改成「不许【悄悄】改」★★):** ★
```python
# ---------------------------------------------------------------- [K5] 受保护文件 md5 未变
def check_k5(root: str):
    bad = []
    for rel, want in sorted(GUARDED.items()):
        p = os.path.join(root, rel)
        if not os.path.exists(p):
            bad.append("%s 缺失" % rel)
            continue
        got = _md5(p)
        if got == want:
            continue
        # ★ISS-399 口径订正: 硬基线 ∪ 台账链头 (★合法追加不再永久红★)
        ok, why = ledger_reader.baseline_ok(root, rel, want)
        if not ok:
            bad.append("%s md5 %s≠%s (%s)" % (rel, got, want, why))
    ok = not bad
    detail = ("受保护文件 md5 逐字节未变 (或已在台账登记的合法追加) (%d 个): %s"
              % (len(GUARDED), ", ".join("%s=%s…" % (r.split("/")[-1], v[:8]) for r, v in sorted(GUARDED.items())))
              if ok else "受保护文件被改: " + " ; ".join(bad))
    return ok, detail
```
★**要加的 import (★在 `import` 段里·★与补丁 ② 同一行★):** ★
```python
import mech_signed_append_ledger_reader as ledger_reader
```

---

## ★§5 · 挂链建议 (★给 `state/gate_check.py` 的逐字建议·★**本单零挂链**·★挂不挂是 main 的地界★) ★

★**本单的建议: ★**挂**★ (★与 SW 侧 `SW/tools/check_sw_board_md5_rebase_readiness.py` 同等待遇★)。** ★
★**理由 (★三条·★每条都有盘上依据★):** ★
★**① 这 9 道 (★现为 11 道★) MECH 闸里只有 1 道在官方链上 (`check_demo_struct_truth.py`) ⇒ 其余的红【零通知】⇒ 三个月来 3 处陈旧 pin 一直没人归因 (★§2.4 的核心结论就是这个★)。** ★ `[实测]`
★**② SW 侧 ISS-372 已经用 `check_sw_board_md5_rebase_readiness.py` 抓同类缝 (H4: 每道真钉板 md5 的判据脚本必须在 §2 有账) ⇒ ★**MECH 域至今没有这一道 ⇒ MECH 侧是对偶的缺口。** ★ `[实测]`
★**③ 新闸本身【零挂链】是本单的边界 (★`grep -c check_mech_signed_append_ledger state/gate_check.py` = 0★) ⇒ ★**但挂不挂要在【main 拍 M-C】之后才能做。** ★

★**★逐字建议 (★M-C 拍「挂」之后才落·★本单【不落】★):** ★
```python
# ★在 state/gate_check.py 的 EXTRA_GATES 名单里加一行 (★位置按该文件现有排序习惯★):
"MECH/check_mech_signed_append_ledger.py",
```
★**★挂上之后它会红 (★红的是现状: 3 处陈旧 pin 归因不到 + 台账还没建★) ⇒ ★**main 落链之前必须先把 M-A (台账落位) 与 M-B (追平方式) 拍完, 否则等于往官方链上挂一道永久红的闸 ⇒ 那比不挂更糟 (★会让人开始习惯性地忽略官方链的红★)。** ★
★**★⇒ ★**建议顺序: M-A → M-B (→ M-D) → 落台账 + 落补丁 ①②③ → 再挂链。** ★ ★**本单一条都不代拍。** ★

---

## ★§6 · 边界自证 + 机器块 ★

### ★6.1 · 边界自证 (★与 §0.3 同表·★这里给盘面读数★) ★

★**板三证 (★零写板★):** ★
```
611b869e13518c3c023fb178f91a0075  HW/PCB/demo_mainboard.kicad_pcb
  mtime = 2026-11-06 07:07:17.362193413  (ns = 1793920037362193413)
  size  = 4940213
```
★**落表三张表 (★零落表★):** ★
```
6aee500e60ba0732f83a9cf557ba90ab  HW/netlist_v1.csv
9174309df1ec9411ac8e8d9e80ee386a  HW/netlist_v1_pins.csv
5b9993992405904a60ac96a020b375d8  HW/BOM_v1.csv
```
★**那 11 道 MECH 域闸的 md5 (★开工前后逐字相同·★基线存 `logs/iss399/baseline_9gates_md5.txt`★):** ★
```
fc8d97d48cacafb43a1be4e1fe3a6524  MECH/check_connector_clearance_caliber.py
667e6006280cc8c0533d8ce8fa39f8be  MECH/check_debug_seat_3d_fit.py
babadd6b073d691374051ea7409a6a1f  MECH/check_debug_seat_rework_spec.py
483d018a66d17d2ead25d1558a1f8ffe  MECH/check_demo_struct_truth.py
1cdc6e9838419647e018c9a4c41319a2  MECH/check_fts_seat_body_geometry.py
7b6ae98c04d32dea87e90f9a683bcac7  MECH/check_fts_seat_sample_plan.py
8f8424a5e632fa3d223271850109c6d0  MECH/check_fts_vs_generic_courtyard_delta.py
c898273018eabba466a04b88402d286c  MECH/check_mech_dual_caliber_gate.py
bcc165d7461ba8906c03b101a72f962d  MECH/check_zoujuan_marker_consistency.py
```
★**零挂链:** `grep -c check_mech_signed_append_ledger state/gate_check.py` ⇒ `0` ★
★**零外发:** 本单全程零次外发请求 (只读本机文件 + 跑本机脚本) ★
★**不自签 issue_log:** `state/issue_log.yaml` 一个字节没动 ★
★**只写自己分片:** 只走 `python3 state/frag_write.py --agent mech-lead` ★

### ★6.2 · ★★本单对新闸做的 4 处实现缺陷修正 (★如实报·★不留暗伤★★) ★

★**★这 3 处改的是【本单自己新建的新闸】 `MECH/check_mech_signed_append_ledger.py` (★上一趟 21:48:41 落盘的那一份★) ⇒ 【不属于】任务书 §五「零改既有闸」里点名的 9 道闸 (★那 9 道的 md5 一个字节没动·见 §6.1★) ⇒ 但仍然如实登记在这里。** ★
★**★三处修正的共同性质: 修的是【假红】(★闸说自己坏·其实自己没坏★) ⇒ 修完之后【闸整体仍然是红的】(★M2 / M3 红 = 现状·★不是闸故障★) ⇒ 没有一条是「为了让它绿而放宽判据」。** ★

| # | 位置 | 原实现的问题 | 修法 | 修前读数 | 修后读数 | ★**判据/阈值有没有动** ★ |
|---|---|---|---|---|---|---|
| ★**1** ★ | 闸 M5 (板三证) | ★**拿 `datetime.fromtimestamp(st.st_mtime)` (★只到 6 位微秒★) 去比 9 位纳秒基线 `2026-11-06 07:07:17.362193413` ⇒ 微秒截断成 `…362193` ⇒ ★**永远 != 基线 ⇒ M5 永远红** ⇒ 且红的时候打印「板被写过」⇒ ★**对真没被写过的板做假指控** ★ | ★**改用 `st.st_mtime_ns` 的纳秒位按 9 位拼 ⇒ 与基线同精度同量纲** ★ | ★**M5 红: 「板 mtime=…362193 ≠ 基线 …362193413 (★板被写过★)」** ★ | ★**M5 绿 (板 md5/size/纳秒 mtime 三项全等基线)** ★ | ★**没有★ (★`BOARD_MD5` / `BOARD_MTIME` / `BOARD_SIZE` 三个阈值常量一字未改·★只把【比较精度】从 6 位微秒对齐到 9 位纳秒·★反而更严★) ★ |
| ★**2** ★ | 闸 M6 (证据分级) | ★**闸源码里【就有】`FORBIDDEN_PENDING` 这个词表常量 ⇒ 扫本闸源码全文必然自命中 ⇒ M6 永远红 ⇒ 红的原因是【闸自己的词表】⇒ 假红** ★ | ★**扫本闸源码时先把【词表常量定义块】剔掉再扫 (★词表本身一字不改·★真相页/台账两处的扫描一个字没动★)** ★ | ★**M6 红: 「本闸源码里出现零挂起措辞 …」 (★12 条错误全是词表自命中★)** ★ | ★**M6 绿 (★真相页 + 台账的扫描照旧·★c11 反向用例仍能抓到真件里的挂起措辞★)** ★ | ★**没有★ (★词表一个词没删·★扫描范围只排除了【本闸自己的定义块】★) ★ |
| ★**3** ★ | 闸 `--selftest` c01 + 沙盒构建 | ★**① c01 期望「M2 也绿」—— 但 M2 是【现状判据】⇒ 3 处陈旧 pin 在盘 ⇒ M2 必红 ⇒ 用例永远不可能通过; ② 沙盒只复制了 `MECH/*.py` + 几个固定文件 ⇒ 【被钉的 .md 真相页】不在沙盒里 ⇒ 该 pin 在沙盒里根本没被枚举 ⇒ c03/c04/c05/c10 改的那一行在沙盒里【不存在】⇒ 4 条用例「应红却绿」⇒ 假通过** ★ | ★**① 期望值改成逐判据给 (★M3/M4 绿 + M2 红·★红的是现状★); ② 沙盒额外复制盘上每一处 pin 的【被钉文件本身】(★只读副本·真件零碰★)** ★ | ★**SELFTEST FAILED (3/12)** ★ | ★**见 §6.3 的实跑读数** ★ | ★**没有★ (★改的是【自测用例的期望写法】与【沙盒的文件清单】·★判据 M1~M7 一条没动★) ★ |
| ★**4** ★ | 闸 `--selftest` c11 夹具 | ★**c11 的用例标题与夹具里【把零挂起词表里的词又写了一遍】⇒ 闸源码里又含那个词 ⇒ M6 扫本闸源码时又自命中 ⇒ 假红** ★ | ★**夹具改成从词表里【取】那个词 (`FORBIDDEN_PENDING[0]`) 而不是再写一遍; 用例标题改成不含该词的描述** ★ | ★**M6 红: 「本闸源码里出现零挂起措辞 …」** ★ | ★**M6 绿 (★c11 仍能在沙盒真相页里抓到真件的挂起措辞·★反向用例照样抓到★)** ★ | ★**没有★ (★词表一个词没删·★判据扫描范围没动·★c11 反而从【假通过】变成【真通过】★) ★ |

★**★⇒ ★**四处的修前/修后读数 (★本页落地前的裸跑 ⇒ 本页落地后的裸跑★):** ★
★**修前 (2026-11-24 22:0x, ★真相页还不存在时★): M1 红 (★在册清单读不到·fail-closed★) / M2 红 (★3 处陈旧 pin = 现状★) / M3 红 (★台账还没建·fail-closed★) / M4 红 (★fail-closed★) / M5 红 (★假红★) / M6 红 (★假红★) / M7 绿 ⇒ ★**共 6 条红** ★**
★**修后 (★本页落地 + 4 处修正后★): M1 绿 / M2 红 (★现状★) / M3 红 (★现状·等 M-A·M-B★) / M4 绿 / M5 绿 / M6 绿 / M7 绿 ⇒ ★**共 2 条红, 且这 2 条全是【现状】** ★**
★**⇒ ★**红得更诚实, 不是更绿: 修掉的 4 条红里有 2 条是【闸自己的缺陷】(假红), 1 条是【本页还没落】(已落), 1 条是【fail-closed 的正常红】(M4 有清单就不红); ★**剩下的 2 条是本单要治的病, 它们【必须一直红着】, 一直到 M-A / M-B 拍完、台账落地。** ★**
★**★⇒ `--selftest` 修前 `SELFTEST FAILED (3/12)` ⇒ 修后 ★**`ALL TESTS PASS` (12/12)** ★ · ★**反向用例 12 条 ≥ 任务书要求的 8 条, 且 c06 是专打 M4「悄悄改常量 ⇒ 必红」的那一条。** ★

### ★6.3 · ★★闸与页必须同源 (★任务书第 ④ 条·★本单逐条自证★) ★

| 项 | 闸里 | 本页里 | 一致? |
|---|---|---|---|
| 台账路径 | `LEDGER_REL = "MECH/SIGNED_APPEND_LEDGER.md"` | §3.2 建议默认值 A (★同一路径★) | ★**一致** ★ |
| 在册清单 | `enumerate_pins()` 的 AST 枚举 | §1.5 机器块 (★由同一个枚举器生成★) | ★**同源·不可能各写各的** ★ |
| 记录表头 | `REC_HEADER = ("单号","文件","prev_md5","md5","追加类型","追加位置","自证")` | §3.1 表头 (★逐字相同★) | ★**一致** ★ |
| 追加类型枚举 | `APPEND_KINDS = ("纯字节追加","局部订正")` | §3.1 第 5 栏枚举 (★逐字相同★) | ★**一致** ★ |
| 台账记录块标记 | `REC_BEGIN` / `REC_END` | §3.1 (★同名★) | ★**一致** ★ |
| 板三证基线 | `BOARD_MD5` / `BOARD_MTIME` / `BOARD_SIZE` | §6.1 (★逐字相同★) | ★**一致** ★ |

★**⇒ 本页的 §1.5 机器块由 `tmp/iss399/gen_truth_page.py` 生成, 该脚本 import 的就是新闸自己 ⇒ ★**改闸的枚举器就自动改本页, 反之亦然 ⇒ 「同源」是结构保证, 不是口头承诺。** ★ `[实测]`

### ★6.4 · ★★本页的一个已知残留缺口 (★如实报·★下一趟再补★) ★

★**新闸 M4 的护栏有一个残留缺口: ★**如果有人【同时】把闸里的写死常量【和】本页 §1.5 机器块里的登记基线一起改成现值 (★两边同步改★), M4 比对的两边就仍然相等 ⇒ ★**M4 不会红。** ★
★**⇒ 这条缺口在自测 c06 里【抓不到】(★c06 只改闸里的常量·不动 §1★) ⇒ ★**c06 是「单边偷改」的反向用例, 不是「双边同步偷改」的反向用例。** ★
★**⇒ 建议的收紧方向 (★本单【不落】·★交 main 裁决★): ★**M4 的锚点应该从「§1 登记基线」换成「台账链头」—— 也就是: 闸里的常量必须等于【台账里那个文件的链头】, 而 §1 机器块退化成【清单 + 交叉核对】。** ★ ★**代价: 台账一坏 ⇒ 全域判红 ⇒ 台账的写权限必须比闸更紧 (★这就是 M-A「谁写」那一问的真正代价★)。** ★
★**⇒ 本单【不落】这条收紧: ★**它是判据口径的改动, 归 M-B / M-D 拍板, 本单一条都不代拍。** ★

---

★**★★ 本页终 ★★**
★**证据等级: 本页所有数字与行号均为【实测】(★本机实跑 md5sum / stat / diff / ast 枚举 / 实跑闸★) ⇒ 推导句标 `[推算]` ⇒ 本机没有的标 `[0数据]`。** ★
★**边界: 零写板 · 零落表 · 零改既有闸 · 零改既有页正文 · 零挂链 · 零外发 · 不代拍 · 不自签 issue_log · 只写自己分片。** ★
