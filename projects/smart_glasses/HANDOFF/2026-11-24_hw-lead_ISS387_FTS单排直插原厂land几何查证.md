# ISS-387 · hw-lead · FTS 单排直插原厂 land 几何查证 (cont1 交卷)

★**本单 = ISS-387 cont1 (续做趟)** ★ · ★**零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 · 零挂链 · 零外发 · 不代拍** ★
★**日期**: 2026-11-24 11:04~11:40 (GMT+8) · ★**agent**: hw-lead (硬件总工) · ★**issue**: ISS-387 ★
★**上一趟** (2026-11-24 09:45:20~10:10:23) 被 spawn 的 `runTimeoutSeconds=1500` 掐死 (墙钟 25.05 分钟) ⇒ ★**真相页已在盘, 闸/交卷页/分片全缺** ⇒ 本趟只补这三件, ★**真相页正文一个字不许删改** ★

---

## B1 · 结论摘要 (★一句话★)

★**`FTS-104-01-F-S` / `FTS-102-01-F-S` 是真实存在的 Samtec 单排直插件 (4 位 / 2 位 · 1 排 · 1.27 mm 排距) `[官网]`; Samtec 官方直插推荐 PCB 图【只给孔位图, 不给铜箔焊盘直径】⇒ 「原厂 land 的铜箔 X 宽」在官方那一层根本不存在官方数 `[官网]`+`[实测]`; MECH 全链吃的 `4.8100` / `2.2700` 是【盘上通用 KiCad 库件的焊盘 `1.000` 算出来的】, 不是厂件数 `[实测]`+`[推算]`; ★**盘上通用库钻孔 `0.65` 比官方 `Ø0.71` 小 `0.06` ⇒ 落 FTS 必须改孔, 但只要焊盘仍是 `1.000×1.000`, 铜箔包络不变 ⇒ MECH 全链余量数一个都不用重算 ⇒ 结构件不必为这一趟再返工一次** `[官网]`+`[实测]`+`[推算]`; ★**本单零写板零落表, 只交「真相页 + 新闸 + 交卷页 + 分片」, 料号落地与 BOM 落表一律不代拍 (`landing_part_decision = not_decided_here`)** ★

### B1-① 三条硬结论 (★上一趟查到的, 本趟只补证据不推翻★)
| # | 结论 | 证据等级 | 本趟补的证据 |
|---|---|---|---|
| H-1 | ★`FTS-104-01-F-S` / `FTS-102-01-F-S` 真实存在 · 4 位/2 位 · ★**1 排**★ · 直插 · 排距 `1.27 mm` ⇒ ★**ISS-383 §0-2「两家都没有单排」被官网单品页逐字推翻** ★ | ★`[官网]` ★ | ★§7.1-7-3 `pdftotext` 文字层复跑逐字含 `(NO OF POS x .050[1.27]) - .050[1.27]` / `.050 1.27 (TYP)` / `.028 0.71 (TYP)` ★ |
| H-2 | ★Samtec 官方直插 land ★**只给孔位图, 不给铜箔焊盘直径** ⇒ ★「原厂 land 的铜箔 X 宽」★**在官方那一层根本不存在官方数** ⇒ ★`4.8100` / `2.2700` 是通用库件焊盘 `1.000` 算的 ★ | ★`[官网]`+`[实测]` ★ | ★7-3 复跑: 官方推荐 PCB 图文字层全文**无任何铜箔焊盘直径数字**; 7-1 复跑: 通用件铜箔包络 = 跨距 + 焊盘 `1.000` ⇒ 与 §4 逐字一致 ★ |
| H-3 | ★盘上通用库钻孔 `0.65` < 官方 `Ø0.71` (差 `0.06`) ⇒ ★**落 FTS 必须改孔**; ★**但只要焊盘仍是 `1.000×1.000`, 铜箔包络不变 ⇒ MECH 全链余量数不用重算 ⇒ 结构件不必为这一趟再返工一次** ★ | ★`[官网]`+`[实测]`+`[推算]` ★ | ★7-1 复跑 (通用件 `0.65`) + 7-3 复跑 (官方 `.028 0.71 (TYP)`) + 7-6 复跑 (MECH L491/L683-L686/L746 仍写死 `4.81`/`2.27`) ★ |

### B1-② ★族别辨析 (本单命门·第 4 条硬结论) ★
★**`FTSH-104-01-F-DV` 是双排贴片, 与 `FTS-104-01-F-S` 是不同族、不同件 ⇒ 它的任何数 (铜箔宽 / 孔径 / 座体高) 都不许顶替 FTS 的数** ★ `[官网]`
★⇒ 本单新闸 **K4 专打这一条**: 机器块里 FTS 料号字段出现 `FTSH` / 多出 FTSH 料号条目 ⇒ 判红 ★

---

## B2 · 验收标准自评 (逐条 通过 / 不通过 / 未验)

| # | 验收标准 | 判定 | 自评依据 (★本机实跑读数★) |
|---|---|---|---|
| A-1 | ★真相页在盘且正文定稿 (★只许追加, 不许删改★) | ★**通过** ★ | ★`HW/PCB/BOARD_ONEPASS_FTS_SINGLE_ROW_LAND_TRUTH.md` 44,122 B @10:10:03, md5 `3e019b04f469bce196529300bf374979` ⇒ 与 brief 基线逐字同; 本趟只在页尾追加 §8 一块, ★**追加后前 44,122 B 的 md5 仍 = `3e019b04…` ⇒ §0~§7 逐字节未动** ★ |
| A-2 | ★§7.2 机器块 `json.loads` 可解析 | ★**通过** ★ | ★闸 K0 实跑绿 (闸自己解析本页机器块, 解析失败即红) ★ |
| A-3 | ★§7.1 的复跑命令逐条能跑且读数对得上 | ★**通过** ★ | ★7-1~7-11 全部实跑, 输出见 B6; ★**只有 7-9 一条的「预期命中数」过期** (原写「1 命中」, 实跑 11) ⇒ 已在真相页 §8-② 追加块**订正**, 未动 §7.1 正文 ★ |
| A-4 | ★**新闸 `HW/check_fts_single_row_land_truth.py` 在盘, 零挂链** | ★**通过** ★ | ★文件在盘 (31,159 B); ★`grep -c check_fts_single_row_land_truth state/gate_check.py` = **0** ⇒ 零挂链 (★挂链是 main 的地界★) ★ |
| A-5 | ★**新闸 fail-closed, 每条判据有反向用例** | ★**通过** ★ | ★K0~K6 七条; ★`--selftest` **17/17 PASS · ALL TESTS PASS · rc=0** (★≥8 条反向用例, 其中 2 条专打命门★) ★ |
| A-6 | ★**新闸从机器块读数, 不写死任何数** | ★**通过** ★ | ★通用件铜箔宽取 `generic_part_measured`; 偏离登记取 `deviation_vs_generic_part` ⇒ ★**改页即红 (设计, 不是 bug)** ★; 自测用例 ②/⑥/⑦ 已实证改页即红 ★ |
| A-7 | ★**新闸与环境无关 (沙盒落项目盘)** | ★**通过** ★ | ★沙盒 = `tmp/iss387_sbx/` (★从本闸自己的 `PROJ` 推, 不依赖系统 `/tmp` 深度★); `TMPDIR=$PWD/tmp` 下 17/17 PASS ★ |
| A-8 | ★零写板 · 零落表 | ★**通过** ★ | ★见 B2-② 指纹表 ★ |
| A-9 | ★零改既有闸 / 既有页面正文 | ★**通过** ★ | ★见 B2-② 指纹表 ★ |
| A-10 | ★零外发 | ★**通过** ★ | ★全程只读本机 + 自己网上查资料; ★**未调用任何发信 / 询价 / 问询 / 采购工具**; `state/outbox/` 一个字节未动 ★ |
| A-11 | ★不代拍 | ★**通过** ★ | ★机器块 `landing_part_decision = not_decided_here` (★闸 K5 守住★); ★BOM 型号栏只给草案, 未落表 ★ |
| A-12 | ★不自签台账 | ★**通过** ★ | ★`state/issue_log.yaml` 一个字节未动 ★ |
| A-13 | ★交卷页 B1~B6 六段齐全 | ★**通过** ★ | ★本页 B1~B6 齐全; ★`state/gate_check.py` 的 `REQUIRED_BLOCKS` 六个关键词 (结论 / 验收标准自评 / 证据分级 / 接口取值 / 未决 / 复现) 全部命中 ★ |
| A-14 | ★**原厂直插档座体外形 (宽/深) 官方尺寸** | ★**未验** (★= `[0数据]`★) | ★官网直插档外形尺寸查不到官方数 ⇒ ★**已走 §6-④ 降级** (官网 3D/CAD 下载 或 实测样件卡尺复现) ★; ★**不许写成挂起** ⇒ 闸 K5 的零挂起判据盯着这一段 ★ |
| A-15 | ★**单排 (-S) 版官方打印件直链** | ★**未验** (★= `[0数据]`★) | ★已走 §6-① 降级 (用已取得的直插孔位图 + 「单排只取一行」明示推算) ★ |

### B2-② ★边界自证 (指纹对照, ★开工前 11:04:42 / 交卷时 11:3x 两次实测同值★)★
| 文件 | md5 | 判定 |
|---|---|---|
| `HW/PCB/demo_mainboard.kicad_pcb` | `611b869e13518c3c023fb178f91a0075` (size `4940213` · mtime `2026-11-06 07:07:17.362193413`) | ★**零写板** ⇒ ★板已 18 天逐字节未动 ⇒ **G1 仍开, 不许投板** ★ |
| `HW/netlist_v1.csv` | `6aee500e60ba0732f83a9cf557ba90ab` | ★**零落表** ★ |
| `HW/netlist_v1_pins.csv` | `9174309df1ec9411ac8e8d9e80ee386a` | ★**零落表** ★ |
| `HW/BOM_v1.csv` | `5b9993992405904a60ac96a020b375d8` | ★**零落表** ★ |
| `state/gate_check.py` | `5f370bb8cf828473e70ccc5d6412da98` | ★**零改既有闸** ★ |
| `MECH/check_debug_seat_3d_fit.py` | `667e6006280cc8c0533d8ce8fa39f8be` | ★**零改既有闸** ★ |
| `MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md` | `3d0c8e7de86e0f853450dcb7404d9f44` | ★**零改既有页面正文** ★ |
| `HW/check_debug_uart_seat_alignment.py` | `52e067ed99edaaced50fd565bed90042` | ★**零改既有闸** ★ |
| `HW/check_debug_uart_seat_truth.py` | `274f759101ca4bc131f25633dc209b0c` | ★**零改既有闸** ★ |
| `state/issue_log.yaml` | ★一个字节未动 ★ | ★**不自签台账** ★ |

---

## B3 · 证据分级 (★每条结论挂五级之一★)

### B3-① 词表 (★与真相页 §1.1 一致★)
★`[官网]` = 原厂/分销官网原文或官方 PDF 文字层 · ★`[实测]` = 本机自己跑出来的读数 · ★`[媒体]` = 第三方媒体/分销页 · ★`[推算]` = 由前两者推导 (含明示假设) · ★`[0数据]` = ★**查不到官方数 (不许用经验值冒充实测)** ★

### B3-② 逐条登记
| # | 断言 | 等级 | 来源 / 复跑 |
|---|---|---|---|
| E-01 | ★`FTS-104-01-F-S` = 4 位 · ★**1 排**★ · 直插 · 排距 `1.27` · 孔 `Ø0.71 (TYP)` · 座体高 `0.86` ★ | ★`[官网]` ★ | ★Samtec 官网单品页 `https://www.samtec.com/products/fts-104-01-f-s` (真相页 §2 逐字抄录 + `prose_anchors`) ★ |
| E-02 | ★`FTS-102-01-F-S` = 2 位 · ★**1 排**★ · 直插 · 排距 `1.27` · 孔 `Ø0.71 (TYP)` ★ | ★`[官网]` ★ | ★Samtec 官网单品页 `https://www.samtec.com/products/fts-102-01-f-s` (真相页 §3) ★ |
| E-03 | ★官方直插推荐 PCB 图文字层逐字含 `(NO OF POS x .050[1.27]) - .050[1.27]` / `.050 1.27 (TYP)` / `.028 0.71 (TYP)` ★ | ★`[官网]` + ★`[实测]` ★ | ★`tmp/iss387/fts-1xx-xx-xx-dx-xx-footprint.pdf` (md5 `1cbe4a2bfa456d8fd030c8b76bdf8dd5`) · `pdftotext -layout` ⇒ B6-③ ★ |
| E-04 | ★**该官方图全文无铜箔焊盘直径** ⇒ ★**「原厂 land 的铜箔 X 宽」无官方数** ★ | ★`[官网]` + ★`[推算]` ★ | ★同上, 文字层逐行核过 ⇒ ★**这条是 MECH 全链余量数的根问题** ★ |
| E-05 | ★盘上通用件 `J_DEBUG` = 焊盘 `1.0x1.0` · 钻孔 `0.65` · 1 排 · 排距 `[1.27,1.27,1.27]` · 铜箔包络 `4.81 x 1.0` ★ | ★`[实测]` ★ | ★`python3 tmp/iss387/measure_generic_part.py` ⇒ B6-② ★ |
| E-06 | ★盘上通用件 `J_UART` = 焊盘 `1.0x1.0` · 钻孔 `0.65` · 1 排 · 排距 `[1.27]` · 铜箔包络 `2.27 x 1.0` ★ | ★`[实测]` ★ | ★同上 ★ |
| E-07 | ★两个通用库件 md5 = `7a5f470c…` / `47bcbf6d…` ★ | ★`[实测]` ★ | ★B6-② md5sum ★ |
| E-08 | ★`MECH/check_debug_seat_3d_fit.py` L491 / L683-L686 / L746 写死 `4.81` / `2.27` ⇒ ★MECH 全链吃的是这个数 ★ | ★`[实测]` ★ | ★B6-④ ★ |
| E-09 | ★`MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md` 吃 `6.6100` / `4.0700` / `0.1350` / `2.6950` / `0.7700` + OI-5 / OI-12 ★ | ★`[实测]` ★ | ★真相页 §5-① (已登记) ★ |
| E-10 | ★`HW/BOM_v1.csv` 第 71/77 行 `opn` / `footprint` 仍 `待定` ⇒ ★**本单零落表, 只给草案** ★ | ★`[实测]` ★ | ★B6-④ ★ |
| E-11 | ★★原厂直插档座体外形 (宽/深) 官方尺寸★ | ★`[0数据]` ★ | ★**已走 §6-④ 降级** (官网 3D/CAD 下载 / 实测样件卡尺) ★ |
| E-12 | ★★单排 (-S) 版官方打印件直链★ | ★`[0数据]` ★ | ★**已走 §6-① 降级** ★ |
| E-13 | ★**FTSH 是另一个族 (双排贴片), 任何数不许顶替 FTS** ★ | ★`[官网]` ★ | ★Samtec 官网 `FTSH` 族页 (真相页 §3.2 / §5-④) ★ |
| E-14 | ★**落 FTS 必须改孔 `0.65 → 0.71`**; ★**焊盘不变 ⇒ 铜箔包络不变 ⇒ MECH 余量数不用重算** ★ | ★`[推算]` ★ | ★由 E-03/E-05/E-06 推导 (假设: 铜箔包络只看焊盘, 不看钻孔 —— 与 MECH 现有口径一致) ★ |

★**零挂起自证**: 全页无「等原厂回信 / 待外部确认 / 等回复 / pending reply / 待确认」等语境 (★闸 K5 的零挂起判据实跑绿; 唯一出现的「等原厂回信 / 待外部确认」在 §6-④ 里是【禁止令原文】, 带否定语境, 不算挂起★) ★

---

## B4 · 接口取值声明 (interface_claims)

★**本单是 PCB 主线的【纯查证层】⇒ 以下 5 条是本单对外的接口取值; ★其中前 3 条是【事实登记】, 后 2 条是【留白/条件】, ★**本单不代裁**★**

| # | 接口 | 取值 | 谁在吃 | 等级 |
|---|---|---|---|---|
| IC-1 | ★`J_DEBUG` 板侧 land 封装族★ | ★**继续用盘上通用 KiCad 库件** `Connector_PinHeader_1.27mm:PinHeader_1x04_P1.27mm_Vertical` (md5 `7a5f470c…`) ★**+ 落 FTS 时把孔径改 `0.71`** ★ (★焊盘仍 `1.000×1.000` ⇒ 铜箔包络 `4.8100` 不变★) | ★MECH 全链 (`4.8100`) · BOM 型号栏草案 ★ | ★`[实测]`+`[推算]` ★ |
| IC-2 | ★`J_UART` 板侧 land 封装族★ | ★**继续用盘上通用 KiCad 库件** `PinHeader_1x02_P1.27mm_Vertical` (md5 `47bcbf6d…`) ★**+ 落 FTS 时把孔径改 `0.71`** ★ (★焊盘仍 `1.000×1.000` ⇒ 铜箔包络 `2.2700` 不变★) | ★MECH 全链 (`2.2700`) · BOM 型号栏草案 ★ | ★`[实测]`+`[推算]` ★ |
| IC-3 | ★**MECH 全链余量数的成立条件**★ | ★**只要板上焊盘保持 `1.000×1.000`, MECH 的 `4.8100` / `2.2700` / `6.6100` / `4.0700` / `0.1350` / `2.6950` / `0.7700` 一个数都不用改 ⇒ 结构件不必为这一趟再返工一次** ★ | ★MECH/check_debug_seat_3d_fit.py · MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md ★ | ★`[推算]` ★⇒ ★**已由新闸 K3 守着 (改了这个数而不登记 ⇒ 红)** ★ |
| IC-4 | ★BOM 型号栏 (★本单零落表, 只给草案★)★ | ★`J_DEBUG` → `FTS-104-01-F-S` (Samtec · 4 位 1 排直插 · 1.27) + land = `PinHeader_1x04_P1.27mm_Vertical` + **孔径 `0.71`** + 偏离 D-1/D-2/D-3 登记 ★ · ★`J_UART` → `FTS-102-01-F-S` + land = `PinHeader_1x02_P1.27mm_Vertical` + **孔径 `0.71`** + 偏离 D-1/D-2/D-3 登记 ★ | ★`HW/BOM_v1.csv` 第 71/77 行 (★**落表时机 = 与 land 改动同一次工序, 即「板只改一次」那一趟★**) ★ | ★`[官网]`(料号) + ★`[实测]`(land/孔径) ★ |
| IC-5 | ★**料号落地裁决权**★ | ★**`not_decided_here`** ⇒ ★**本单不代拍: A2 (Samtec 厂件 land) 与 A4 (KiCad 通用件 land) 指向不同封装来源, 落板那一刻必须合成一个, 裁决归 main / boss** ★ | ★main (板只改一次那一趟) ★ | ★`[推算]` ★ |

★**登记的偏离 (D-1 / D-2 / D-3, ★必须跟着 land 改动一起进 BOM 备注★)**: ★**D-1** 焊盘 `1.000` 是第三方库件/IPC 口径, 不是厂件数 · ★**D-2** 钻孔 `0.65 ≠ 0.71` ⇒ 落 FTS 必须改孔 · ★**D-3** `F.CrtYd`/`F.Fab` 是通用排针的 courtyard, 不是 FTS 厂件 keepout ⇒ ★**OI-12 的对照物要重算** ★

---

## B5 · 未决项与卡点 (需要谁回答什么 + 代价)

★**真相页机器块登记的 4 条 `open_items` 就是本单 needs 的底稿; ★OI-387-4 本属 mech-lead, 按派活要求登记进本单 needs 但 `to=main` 并注明「mech-lead 侧执行」★**

| # | 未决 | 要谁回答 | 回答什么 | 代价 (不回答会怎样) |
|---|---|---|---|---|
| OI-387-1 | ★落 FTS 时板上焊盘是否仍取 `1.000×1.000`★ | ★**main** ★ | ★**拍**: 焊盘保持 `1.000×1.000`? ★**代价**: 这是「MECH 全链余量数一个都不用改」★**唯一的成立条件**★ ⇒ ★**不拍 ⇒ MECH 的 `4.8100`/`2.2700`/`6.6100`/`4.0700`/`0.1350`/`2.6950`/`0.7700` 七个数全部要重算 ⇒ 结构件 + 镜脚侧返工一次 (★2-4 周 + ¥4-8K 级★)★ ★ |
| OI-387-2 | ★板上钻孔 `0.65 → 0.71` 的改板动作是否与「板只改一次」那一趟同批★ | ★**main** ★ | ★**拍**: 改孔动作并进那一趟? ★**代价**: ★**不同批 ⇒ 多投一次板 (2-4 周 + ¥4-8K); 同批 ⇒ 零额外成本 (钻孔不进铜箔包络 ⇒ 不动 MECH)** ★ ★ |
| OI-387-3 | ★§㊳ A2 (Samtec 厂件 land) 与 A4 (KiCad 通用件 land) 指向不同封装来源, 落板时须合成一个★ | ★**main** ★ | ★**拍**: 落板时用 Samtec 官方 land, 还是 KiCad 通用件 land + BOM 型号栏写「等价替代」? ★**代价**: ★**不拍 ⇒ 落板那一刻会出现「封装来源与 BOM 型号栏不同源」⇒ 同源纪律破 ⇒ 焊盘/孔径/座体三者对不上 (投板后才发现 ⇒ 2-4 周返工)** ★ ★ |
| OI-387-4 | ★FTS 直插档座体外形 (宽/深) 官方尺寸 = `[0数据]`★ | ★**main (mech-lead 侧执行)** ★ | ★**走 §6-④ 降级**: ①官网 3D/CAD 下载量外形 (宽 X / 深 Y / 高 Z) → 回填 `keepout_dwg`; ②落 FTS 时先打一块单板样, 卡尺量【座体宽 X / 深 Y / 绝缘体高 Z】三个量 ★**代价**: ★**不填 ⇒ OI-12 (「判据要求的清空区 `6.6100` 比 courtyard 还大 `0.5200`」这个结论) 的对照物仍是通用排针的 courtyard ⇒ 这条结论作废 ⇒ 结构侧清空区余量算错 ⇒ 装配干涉** ★ ★ |

★**本单没有「等原厂回信」这种挂起项**: ★**每条缺口都给了降级路径 (§6-① ~ §6-⑤) ⇒ 闸 K5 的零挂起判据盯着这一段** ★

---

## B6 · 自证复现命令 (★原样输出 + rc★)

★**前置**: `cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses` · `export TMPDIR=$PWD/tmp` ★

### B6-① 本单新闸 (★主交付物★)
```
$ python3 HW/check_fts_single_row_land_truth.py
── ISS-387 FTS 单排直插 land 真相页闸
  [K0] ✔ GREEN  真相页 + 机器块在盘 / 可解析 / 无空字段
  [K1] ✔ GREEN  positions_rows 必须 1 排 (族别辨析命门)
  [K2] ✔ GREEN  铜箔宽: 等于通用件 或 [0数据]+降级
  [K3] ✔ GREEN  偏离必须登记 + 影响面点名 MECH
  [K4] ✔ GREEN  不许拿 FTSH 顶替 FTS
  [K5] ✔ GREEN  证据分级 / 零挂起 / 判据与事实分开
  [K6] ✔ GREEN  零写板 / 零落表 / 零挂链
── ISS-387 FTS 单排直插 land 真相页闸: 7/7 条绿
✅ 全绿
rc=0
```

```
$ python3 HW/check_fts_single_row_land_truth.py --selftest
  [PASS] 正向对照 (原页面)                     全绿 (期望) · 实际红: 无
  [PASS] ① 把 FTS-104 的 positions_rows 从 1 排改成 2 排 ⇒ K1 红
  [PASS] ② copper_x_width 改成 9.9900 且影响面抹掉 MECH 那几行 ⇒ K3 红
  [PASS] ③ deviation_vs_generic_part.status 从 registered 改掉 ⇒ K3 红
  [PASS] ④ 把 FTSH-104-01-F-DV 塞进 FTS 料号字段 ⇒ K4 红
  [PASS] ⑤ 机器块里多出 FTSH-104-01-F-DV 条目 ⇒ K4 红
  [PASS] ⑥ copper_y_width 写成 2.0000 (第三种情形) ⇒ K2 红
  [PASS] ⑦ copper_x_width 仍是 [0数据] 但 degrade_refs 里删掉降级条目 ⇒ K2 红
  [PASS] ⑧ evidence 写成「官网(无括号)」不在白名单 ⇒ K5 红
  [PASS] ⑨ §6 里塞一句「等原厂回信」⇒ K5 红
  [PASS] ⑩ 判据句混进 §2 事实抄录节 ⇒ K5 红
  [PASS] ⑪ 机器块 json 被改坏 ⇒ K0 红
  [PASS] ⑫ 机器块里出现空字符串字段 ⇒ K0 红
  [PASS] ⑬ 机器块 board_write 改成 yes ⇒ K6 红
  [PASS] ⑭ 板 md5 被动过 ⇒ K6 红
  [PASS] ⑮ landing_part_decision 改成 decided_fts ⇒ K5 红
  [PASS] ⑯ 官网原句锚点被从正文删掉 ⇒ K5 红
── selftest: 17/17 PASS
ALL TESTS PASS
rc=0
```

### B6-② 盘上通用件自解析 + 库件 md5 (★§7.1-7-1 / 7-2★)
```
$ python3 tmp/iss387/measure_generic_part.py
=== J_DEBUG ===
  文件      : PinHeader_1x04_P1.27mm_Vertical.kicad_mod
  md5       : 7a5f470c1f70d4b832be258501945385
  焊盘数    : 4   (类型: thru_hole)
  pad 尺寸  : 1.0 x 1.0 mm
  钻孔      : 0.65 mm  (全部焊盘一致: True)
  排数      : 1  (焊盘中心 X 唯一值 [0.0])
  排距      : [1.27, 1.27, 1.27] mm
  铜箔包络  : 沿脚排 4.81 mm x 垂直脚排 1.0 mm
  MECH 口径 : copper.x(沿脚排) = 4.81   copper.y(垂直脚排) = 1.0
=== J_UART ===
  文件      : PinHeader_1x02_P1.27mm_Vertical.kicad_mod
  md5       : 47bcbf6d0f267d543e50d4b2a8dfabf5
  焊盘数    : 2   (类型: thru_hole)
  pad 尺寸  : 1.0 x 1.0 mm
  钻孔      : 0.65 mm  (全部焊盘一致: True)
  排数      : 1  (焊盘中心 X 唯一值 [0.0])
  排距      : [1.27] mm
  铜箔包络  : 沿脚排 2.27 mm x 垂直脚排 1.0 mm
  MECH 口径 : copper.x(沿脚排) = 2.27   copper.y(垂直脚排) = 1.0
rc=0

$ md5sum /home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty/PinHeader_1x0{4,2}_P1.27mm_Vertical.kicad_mod
7a5f470c1f70d4b832be258501945385  .../PinHeader_1x04_P1.27mm_Vertical.kicad_mod
47bcbf6d0f267d543e50d4b2a8dfabf5   .../PinHeader_1x02_P1.27mm_Vertical.kicad_mod
rc=0
```

### B6-③ 原厂件文字层 (★§7.1-7-3 / 7-4 / 7-5 ★· ★两份 PDF 已在盘, 本单未重下★)★
```
$ md5sum tmp/iss387/fts_catalog.pdf tmp/iss387/fts-1xx-xx-xx-dx-xx-footprint.pdf
fa249db9454f92c77d7e0a5ef62a0ba6  tmp/iss387/fts_catalog.pdf
1cbe4a2bfa456d8fd030c8b76bdf8dd5  tmp/iss387/fts-1xx-xx-xx-dx-xx-footprint.pdf

$ pdftotext -layout tmp/iss387/fts-1xx-xx-xx-dx-xx-footprint.pdf - | head -40
REVISION N               RECOMMENDED PCB LAYOUT FOR FTS-1XX-XX-XX-DX-XX
                                         (NO OF POS x .050[1.27]) - .050[1.27]
                                   .050 1.27 (TYP)
                                                                                     .028 0.71 (TYP)
             .050 1.27
                                                    FIG 1
                                      N    FTS-1XX-XX-XX-D SHOWN
                             ALL DIMENSIONS ARE SYMMETRIC ABOUT THE CENTERLINE
rc=0
⇒ ★逐行核过: 该文字层【无任何铜箔焊盘直径数字】⇒ 「官方直插图不给铜箔焊盘直径」坐实 ★

$ pdftotext -layout tmp/iss387/fts_catalog.pdf - | head -40
FTS
Board Mates: CLP, FLE
Cable Mates: FFSD
NO. PINS PER ROW : 02 thru 50 (except –S & –SA option = 05 thru 46)
LEAD STYLE : –01 = .120" Post (3.05 mm) (Mates with FFSD)
ROW OPTION : –S = Single Through-hole (05 thru 46 positions. Style -02 & -03 only)
⇒ ★与真相页 §3.2-① / §3.2-② 逐字一致 ⇒ 「–S 只供 05~46 位」这条歧义仍成立 (本单不代裁) ★
rc=0
```

### B6-④ MECH 那几行 + BOM 两行 (★§7.1-7-6 / 7-7 / 7-8 ★· ★只读, 不许改★)★
```
$ sed -n '98,101p;491p;683p;686p;746p' MECH/check_debug_seat_3d_fit.py
KICAD_LIB = "/home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty"
FOOTPRINT_FILE = {
    "J_DEBUG": "PinHeader_1x04_P1.27mm_Vertical.kicad_mod",
    "J_UART": "PinHeader_1x02_P1.27mm_Vertical.kicad_mod",
            want_cover = r4((float(c["value"]) - 4.81) / 2.0)
        "J_DEBUG": {"copper": {"x": 4.81, "y": 1.0},
        "J_UART": {"copper": {"x": 2.27, "y": 1.0},
        mc = r4((v - 4.81) / 2.0)
rc=0

$ sed -n '71p;77p' HW/BOM_v1.csv
J_DEBUG,1,1×4 1.27mm 排针 (JTAG),CONN,必装,镜脚主 PCB,P8,[推算],,待定,,待定,待定,连接器,型号/间距/引脚编号待结构与装配复核 (★本版 pin 编号自拟)
J_UART,1,1×2 1.27mm 排针 (UART),CONN,可选,镜脚主 PCB,P8,[推算],,待定,,待定,待定,连接器,型号/间距/引脚编号待结构与装配复核 (★本版 pin 编号自拟)
rc=0
```

### B6-⑤ 通用封装几何闸 (★★真命令 = 带 pcbnew 包装器, 裸 `python3` 会炸 `ModuleNotFoundError`★★)
```
$ bash state/pcbnew_py.sh state/check_footprint_geom.py
… (末行)
✅ 几何全对
rc=0
```

### B6-⑥ 板 / 三表 / 既有闸 指纹 (★开工前 / 交卷时两次同值★)
```
$ md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
611b869e13518c3c023fb178f91a0075  HW/PCB/demo_mainboard.kicad_pcb
6aee500e60ba0732f83a9cf557ba90ab  HW/netlist_v1.csv
9174309df1ec9411ac8e8d9e80ee386a  HW/netlist_v1_pins.csv
5b9993992405904a60ac96a020b375d8  HW/BOM_v1.csv
$ stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb
2026-11-06 07:07:17.362193413 4940213
$ grep -c check_fts_single_row_land_truth state/gate_check.py
0
rc=0
```

### B6-⑦ 收尾 (★rc 必须 0 · Q1 必须 18/18★)
```
$ python3 state/frag_write.py --agent hw-lead --show     # rc=0
$ python3 state/merge.py
✅ STATE.yaml 已刷新 (2026-11-24T11:10:06+08:00)
   产出 843 | 阻塞 43 (高危 33) | 未闭合需求 355 | 冲突 0 | 健康度 red
rc=0
★注: 「产出 843」= 本单分片已并入 (开工前基线 839 + 本单 4 条产出物);
★「健康度 red / 阻塞 43」是项目全局历史欠账 (★与本单无关, 本单未新增阻塞★), 本单只负责 rc=0 且冲突=0 ★

$ python3 state/gate_check.py
【Q1 交付齐备率】 18/18 个必填验收块齐全
【Q7 钉板 md5 闸链】 10/10 道绿
… (Q4/Q5/Q6 全绿, 缺口清单 3 条 = 本单无关的历史欠账)
rc=0
```
★**完整原样输出见 `logs/iss387/cont1_verify.log`** ★

### B6-⑧ ★闸的迭代记录 (★诚实交代, 不藏★)★
★**新闸第一次裸跑是红的 (rc=1)**: K5 的零挂起判据把真相页 §6-③ / §7.1-7-8 里引用的 **BOM 型号栏现状字段「待定」** 误判成挂起措辞 ⇒ ★**已修**: 「待定」退出挂起词表 (本项目里「待定」是 `HW/BOM_v1.csv` 第 71/77 行的**现状字段值**, 是事实不是挂起), 并加了「现状描述行」豁免 ⇒ ★**修判据, 不放松判据** (K1/K3/K4 命门判据一次也没动过) ★ ⇒ ★**第二次起 7/7 绿** ★
★**另两处已修的漏检/误检**: ① K4 的 `FTSH` 匹配改成不分大小写 (URL 里的小写 `ftsh-` 也是族别混用) ② K5 的「官网原句锚点」改成**只在正文里找** (不许只在机器块里自说自话 ⇒ 否则原句判据会退化成回声) ★ ⇒ ★**两条都是自测用例 ④ / ⑯ 逼出来的** ★

---

## ★本单交卷清单 (★3 件交付物 + 追加块 + 分片★)★
| # | 交付物 | 路径 | 状态 |
|---|---|---|---|
| 1 | ★真相页 (★已在盘; 本趟只追加 §8 一块, §0~§7 正文逐字节未动★)★ | `HW/PCB/BOARD_ONEPASS_FTS_SINGLE_ROW_LAND_TRUTH.md` | ★在盘 ✓ (44,122 B 正文 + §8 追加块) ★ |
| 2 | ★**新闸 (★本单主交付物·零挂链★)** ★ | `HW/check_fts_single_row_land_truth.py` | ★在盘 ✓ · 裸跑 7/7 绿 rc=0 · `--selftest` 17/17 rc=0 ★ |
| 3 | ★**交卷页 (本文件 · B1~B6 齐全)** ★ | `HANDOFF/2026-11-24_hw-lead_ISS387_FTS单排直插原厂land几何查证.md` | ★在盘 ✓ ★ |

★**给 main 的三条动作请求 (★不在本单地界, 本单不代拍★)★**:
① ★**挂链**: 把 `HW/check_fts_single_row_land_truth.py` 挂进 `state/gate_check.py` (★挂链是 main 的地界, 本单 `grep` 命中数 = 0★)
② ★**回 4 条 needs**: OI-387-1 / -2 / -3 拍板 (代价见 B5), OI-387-4 转 mech-lead 走 §6-④ 降级
③ ★**板只改一次那一趟**: 改孔 `0.65 → 0.71` 与 BOM 型号栏落表 (IC-4) ★**并进同一批** ★ ⇒ **G1 仍开, 不许投板**
