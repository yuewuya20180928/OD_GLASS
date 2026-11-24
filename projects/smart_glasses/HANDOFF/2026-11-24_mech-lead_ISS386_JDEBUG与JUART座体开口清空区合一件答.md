# ISS-386 · mech-lead · 交卷页 · `J_DEBUG` + `J_UART` 座体 / 开口 / 必须清空区 【合一件答】

★**交卷人**: 结构总工 (mech-lead) · ★**派活**: 项目总工 (main) · ★**单号**: ISS-386 · ★**日期**: 2026-11-24 ★
★**本页性质**: ★**纯分析 + 新建机器闸 + 沙盒预演 · 零写板 · 零落表 · 零改已签收件 / 既有页面正文 · 零改既有闸 · 零挂链 · 零外发 · 不代拍 · 不自签 `state/issue_log.yaml`** ★ ⇒ 合「板只改一次」纪律 ① (先派不动板的) ★

★**三件交付物**: ★① `MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md` (真相页) · ★② `MECH/check_debug_seat_3d_fit.py` (新闸 · K0~K10 · `--selftest` 18 条反向用例 · ★**零挂链**★) · ★③ 本页 (交卷页) ★
★**留证**: ★`logs/iss386/gate_run.txt` · ★`logs/iss386/gate_selftest.txt` · ★`logs/iss386/boundary_selfcheck.txt` · ★沙盒 `tmp/iss386_sbx/` ★

---

## ★B1 结论摘要 ★

★**一句话**: ★**`J_DEBUG` 与 `J_UART` 换官方 P1.27 THT land 后, 两颗件的 3D 净距判决【方向相同】(两件罩住轴都红) ⇒ 同批改的板两个答案【不互相矛盾】; `J_DEBUG` 的清空区 X 宽三个竞争值 (`1.7750`/`4.0850`/`4.8100`) 各算一遍 ⇒ 【红绿方向完全相同】(全红) ⇒ `OI-5` 选哪个【只改返工幅度】不改方向 ⇒ 那一趟 `J_DEBUG` 的结构件无论如何都要动; `J_UART` 三个候选落点逐个给 3D 判决 ⇒ 【全部罩住红 / 全部开口绿】⇒ 落点裁决【不被结构侧阻塞】, 但结构件的清空区【中心】依赖落点 ⇒ 出件必须等落点定死** ★

★**同源主表的四行 (★两件同表·同判据·同 `TOL`/`CRIT` 取法★)**:

| 位号 | 档位 | 铜箔包络 X/Y | 座体必须清空区 X/Y | 开口 X/Y | 开口余量 X/Y | 罩住余量 X/Y | 最坏余量 (开口 / 罩住) | CRIT | 判决 |
|---|---|---|---|---|---|---|---|---|---|
| `J_DEBUG` | `status_quo` | `1.7750`/`0.9000` | `1.7750`/`2.5400` | `10.2000`/`4.6000` | `4.2125`/`1.0300` | `0.0000`/`0.8200` | `3.9125`/`0.7300` ; `-0.3000`/`0.5200` | `0.60` | 罩住红 (X 同义反复 / Y `0.5200`) |
| `J_DEBUG` | `official_tht` | `4.8100`/`1.0000` | `1.7750`/`2.5400` | `10.2000`/`4.6000` | `2.6950`/`1.0300` | `-1.5175`/`0.7700` | `2.3950`/`0.7300` ; `-1.8175`/`0.4700` | `0.60` | 罩住红 (X `-1.8175` / Y `-0.4700`) ; 开口绿 |
| `J_UART` | `status_quo` | `0.7750`/`0.9000` | `2.5400`/`2.5400` | `10.2000`/`4.6000` | `3.8300`/`1.0300` | `0.8825`/`0.8200` | `3.5300`/`0.7300` ; `0.5825`/`0.5200` | `0.60` | 罩住红 (X `0.5825` / Y `0.5200`) |
| `J_UART` | `official_tht` | `2.2700`/`1.0000` | `2.5400`/`2.5400` | `10.2000`/`4.6000` | `3.8300`/`1.0300` | `0.1350`/`0.7700` | `3.5300`/`0.7300` ; `-0.1650`/`0.4700` | `0.60` | 罩住红 (X `-0.1650` / Y `-0.4700`) ; 开口绿 |

★**`J_UART` 三候选的 3D 判定 (★逐候选·全部给★)**:

| 候选 | 朝向 / pad1 | copper bbox X/Y | 罩住最坏 | 罩住判决 | 开口最坏 | 开口判决 | 总判决 |
|---|---|---|---|---|---|---|---|
| `C1` | rot 270 / `(18.6000, 68.6000)` | X `16.8300..19.1000` × Y `68.1000..69.1000` | `-1.0900` | ★红 (向左伸出 `0.7900`) ★ | `+0.7300` | ★绿 ★ | ★罩住红 / 开口绿 ⇒ 不过阈 ★ |
| `C2` | rot 90 / `(18.4000, 68.4000)` | X `17.9000..20.1700` × Y `67.9000..68.9000` | `-0.3100` | ★红 (向右伸出 `0.0100`) ★ | `+0.7300` | ★绿 ★ | ★罩住红 / 开口绿 ⇒ 不过阈 ★ |
| `C3` | rot 90 / `(18.3000, 68.6000)` | X `17.8000..20.0700` × Y `68.1000..69.1000` | `-0.2100` | ★红 (四边在区内但最窄边 `0.0900`) ★ | `+0.7300` | ★绿 ★ | ★罩住红 / 开口绿 ⇒ 不过阈 ★ |

★**`J_DEBUG` 清空区 X 宽三值各算一遍 (★只摆代价, 不代拍★)**:

| 清空区 X 宽 | 罩住余量 | 最坏余量 | 每边超出 | 判决 | 结构件要不要返工 |
|---|---|---|---|---|---|
| `1.7750` | `-1.5175` | `-1.8175` | `1.5175` | ★红 ★ | ★要 (当场干涉) ; 要过判据需 `6.6100` (`+4.8350`) ★ |
| `4.0850` | `-0.3625` | `-0.6625` | `0.3625` | ★红 ★ | ★要 ; 要过判据需 `6.6100` (`+2.5250`) ★ |
| `4.8100` | `0.0000` | `-0.3000` | `0.0000` (齐平) | ★红 (最坏 `-0.3000` < `CRIT`) ★ | ★判据上要 ; 要过判据需 `6.6100` (`+1.8000`) ★ |

★**三条给「板那一趟」的结构侧硬结论**:
1. ★**`J_DEBUG` 结构件无论如何都要动** (三个竞争值全红) ⇒ 不存在「先只改 `J_UART`」的省事方案 ★
2. ★**要过罩住判据的清空区 X 宽需求**: `J_DEBUG` ≥ `6.6100` · `J_UART` ≥ `4.0700` ⇒ ★**`6.6100` 比官方 land 自己的 `F.CrtYd` `6.0900` 还大 `0.5200` ⇒ ⑤ 判据对 THT 排针偏紧 (OI-12, 归 main + boss)** ★
3. ★**Y 向零制造余量**: 两件罩住 Y 余量都 `0.7700` (最坏 `0.4700` 红) ⇒ 要过阈需清空区 Y ≥ `2.8000`; ★**而罩开口 Y `4.6000` 恰好只容 `2.8000` ⇒ 只放大清空区会把开口顶死 ⇒ 要留余量必须同时放大开口 Y (OI-13)** ★

★**★一处订正 (★新页登记·★不回头改老页★)★**: ★**ISS-377 §3.2 `DP-1` 给 `J_UART` 清空区 `3.4700` (= `2.2700 + 2 × CRIT`) 是【名义余量】口径; 按全链 (最坏 = 余量 − `TOL` ≥ `CRIT`) 需要 `4.0700` ⇒ 差 `0.6000` ⇒ 按 `3.4700` 出件仍不过阈 ⇒ 本单只登记 (`OI-14`), 由 main 决定要不要往老页落** ★

---

## ★B2 验收标准自评 (★逐条 通过 / 不通过 / 未验★)★

| # | 验收项 | 结论 | 证据 (逐条) |
|---|---|---|---|
| 1 | ★**两连接器是否在同一张同源表里 (逐行列, 不许写「已合并」这种空话) ★** | ★**通过** ★ | ★真相页 §1 一张表 · 表头 13 列 · 数据行 4 行: ① `J_DEBUG`/`status_quo` ② `J_DEBUG`/`official_tht` ③ `J_UART`/`status_quo` ④ `J_UART`/`official_tht` ; ★**闸 K1.1 (同表存在) + K1.2 (行字段数 == 表头) + K1.3 (四个 ref×tier 组合齐全) + K1.4 (行数 == 4) + K1.5 (每行 8 个余量数与机器块逐字相等) 全绿** ★ |
| 2 | ★**`J_UART` 三个候选是否全部有判决 (逐个列) ★** | ★**通过** ★ | ★`C1` rot 270 `(18.6000,68.6000)` ⇒ 罩住最坏 `-1.0900` 红 / 开口最坏 `+0.7300` 绿 ; ★`C2` rot 90 `(18.4000,68.4000)` ⇒ `-0.3100` 红 / `+0.7300` 绿 ; ★`C3` rot 90 `(18.3000,68.6000)` ⇒ `-0.2100` 红 / `+0.7300` 绿 ; ★**闸 K2.1 (候选数 == 3) + K2.2 (三个坐标逐字对 ISS-379) + K3.4/K3.5/K3.6 (逐候选重算对拍) 全绿** ★ |
| 3 | ★**`J_DEBUG` 三个清空区候选值是否各算了一遍 ★** | ★**通过** ★ | ★`1.7750` → 罩住 `-1.5175` / 最坏 `-1.8175` ; ★`4.0850` → `-0.3625` / `-0.6625` ; ★`4.8100` → `0.0000` / `-0.3000` ; ★**每行都给「结构件要不要返工 + 返工代价」; 闸 K1b.1 (三值齐全) + K1b.3 (页内正文三个数都在) + K3.7/K3.8 (逐值重算对拍) 全绿** ★ |
| 4 | ★**§4 一致性核对是否有结论 ★** | ★**通过** ★ | ★真相页 §4 九条逐条给结论 (①同判据链 ②同一份 `CRIT`/`TOL` ③`J_DEBUG` 隐含要求 `J_UART` 同改 ④`J_UART` 隐含要求 `J_DEBUG` 同改 ⑤判决方向不矛盾 ⑥发现 ISS-377 `DP-1` 的 `0.6000` 缺口 ⑦Y 向耦合 ⑧没偷偷落点 ⑨没偷偷答 `OI-5`) + 一张「那一趟」清单表 (两件各自: 现状清空区 / 几何不干涉所需 / 过判据所需 / 中心 / 开口要不要动) ★ |
| 5 | ★**`J_UART` 落点【有没有被你偷偷挑掉一个】 (★这一条不许糊过去·门禁不查这个, 只有人查★) ★** | ★**通过 (未挑) ★** | ★真相页 §2 三个候选【并列给出, 不排序、不建议、不标「推荐」】 ; ★机器块 `landing_point_decision = "not_decided_here"` , 三个候选 `chosen` 全为 `false` ; ★§4 ⑧ 明写「没有偷偷替 main 落点」 ; ★**闸 K10.1 (必须 == not_decided_here) + K10.2 (任一候选 chosen=true 即红) + 反向用例 09 (把候选标 chosen ⇒ rc=1 点名 K10) 全绿** ★ |
| 6 | ★**网表 / 脚表 / BOM md5 前后逐字相同 (零落表) ★** | ★**通过** ★ | ★`HW/netlist_v1.csv` = `6aee500e60ba0732f83a9cf557ba90ab` · ★`HW/netlist_v1_pins.csv` = `9174309df1ec9411ac8e8d9e80ee386a` · ★`HW/BOM_v1.csv` = `5b9993992405904a60ac96a020b375d8` (★开工前 = 交卷后, 逐字相同★) ; ★**闸 K9.3 现场比对基线 + 反向用例 15 (沙盒网表被追加 ⇒ rc=1 点名 K9) 全绿** ★ |
| 7 | ★**板三项指纹逐字相同 (零写板) ★** | ★**通过** ★ | ★md5 `611b869e13518c3c023fb178f91a0075` · ★mtime `2026-11-06 07:07:17.362193413` · ★size `4940213` (★三项 == 基线★) ; ★**闸 K9.1/K9.2 + 反向用例 13 (沙盒板被追加一字节 ⇒ rc=1 点名 K9) 全绿** ★ |
| 8 | ★**既有闸 md5 未变 ★** | ★**通过** ★ | ★9 个既有闸/常量文件 md5 开工前 == 交卷后: ★`check_onepass_struct_crosscheck.py` `4eddd08fa4c1e9894a63b8cba0dee500` · ★`check_onepass_mech_sync.py` `5247486a6739d9b0cd5cf9a886c771e8` · ★`check_jdebug_arrangement_truth.py` `67741a510cc3d1709d1894c2da2eeff0` · ★`check_jdebug_1p27_clearance.py` `a9914b2c3e9f8f92f1fbb60d1d8bdd86` · ★`check_juart_1p27_clearance.py` `daf8fa367d89e22f6d3af3d5049bdfb6` · ★`check_board_frame_coords.py` `d4bd30c241718a8c0baf3084f78e2eb7` · ★`check_mech_verdict_freshness.py` `ce4c772d7f54b712c8907646804283c5` · ★`service_port_check.py` `db58ff6a2afc28b8bf517e3c57c56bc1` · ★`check_connector_clearance_caliber.py` `fc8d97d48cacafb43a1be4e1fe3a6524` (★`CRIT`/`TOL` 只读未改★) ★ |
| 9 | ★**既有页正文未变 (★六份已签收页 + 板侧两页★) ★** | ★**通过** ★ | ★`BOARD_ONEPASS_CONNECTOR_CLEARANCE_CALIBER.md` `73e3ec1db370c5667a9d8c5ec964c17e` · ★`BOARD_ONEPASS_JUART_1P27_CLEARANCE.md` `f1ce54c981dd1f64071a177a374df85d` · ★`BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` `da7b02c013fa49c65b70ed3bea97b787` · ★`BOARD_ONEPASS_JDEBUG_ARRANGEMENT_TRUTH.md` `5ffaab52c1582425aa210d68ab3b1618` · ★`BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` `b254fa98c09bc7adb058e1d03eb13980` · ★`BOARD_ONEPASS_MECH_CLAIMS.md` `e91a594adebabeccddfff20fe787255a` · ★`BOARD_ONEPASS_MECH_SYNC.md` `ddd931ea7fe60277e03bc50b9092a6bc` · ★`HW/PCB/BOARD_ONEPASS_JUART_LAND_FIT.md` `8962321c2b94630a221b60fdbff4a5b1` ★**开工前 == 交卷后, 逐字相同** ★ ⇒ ★**本单只新建 `MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md` 一个 `MECH/BOARD_ONEPASS_*` 文件 + 一个新闸 + 本页** ★ |
| 10 | ★**新闸裸跑 rc=0 ★** | ★**通过** ★ | ★`python3 MECH/check_debug_seat_3d_fit.py` ⇒ ★**判据 201 条 · 失败 0 条 · PASS · rc=0** ★ (留证 `logs/iss386/gate_run.txt`) ★ |
| 11 | ★**新闸 `--selftest` 末行 ALL TESTS PASS ★** | ★**通过** ★ | ★`python3 MECH/check_debug_seat_3d_fit.py --selftest` ⇒ ★**反向用例 18 条, 通过 18 条 · 末行 `ALL TESTS PASS` · rc=0** ★ (留证 `logs/iss386/gate_selftest.txt`) ★ |
| 12 | ★**`grep -c check_debug_seat_3d_fit state/gate_check.py` = 0 (零挂链) ★** | ★**通过** ★ | ★实测输出 `0` ; ★**闸 KCHAIN 现场自查 + 反向用例 16 (把本闸挂进 `state/gate_check.py` ⇒ rc=1 点名 KCHAIN) 全绿** ★ |
| 13 | ★**既有闸回归前后读数逐字相同 ★** | ★**通过** ★ | ★`check_onepass_struct_crosscheck` rc=0 · ★`check_onepass_mech_sync` rc=0 · ★`check_jdebug_arrangement_truth` rc=0 · ★`check_jdebug_1p27_clearance` rc=0 · ★`check_juart_1p27_clearance` rc=0 · ★`check_mech_verdict_freshness` rc=0 · ★`check_board_frame_coords --compute` rc=0 ; ★**基线项 `check_connector_clearance_caliber` rc=1 (★那是已知基线红·非本单引入·前后逐字相同★)** ★ |
| 14 | ★**零外发 (★不发任何对外消息·★缺口一律自己查 + 标证据等级 + 查不到写降级方案★) ★** | ★**通过** ★ | ★本单零对外沟通 ; ★所有 `[0数据]` 处均给降级方案 (真相页 §5.1 `DP-1`~`DP-5`) ; ★**闸 K8.1 (页内零挂起措辞) + K8.4 (页内零外发措辞) + 反向用例 12 (注入挂起措辞 ⇒ rc=1 点名 K8) 全绿** ★ |
| 15 | ★**不代拍 (★`OI-5` 不代答·★`J_UART` 落点不重开·★座体高 `h` 不猜★) ★** | ★**通过** ★ | ★`OI-5` 只摆三行事实与代价, 页内无「应采用 X」式裁决语 ; ★`J_UART` 落点只登记依赖 (OI-3, 注明已被 ISS-379 挂起) ; ★`h` 按 Z 向保守上界 `4.70` 参数化且明写「X 向判决与 `h` 无关」 ; ★**闸 K10.1/K10.4 全绿** ★ |
| 16 | ★**未验项 (★诚实登记·不糊过去★) ★** | ★**未验** ★ | ★**① 板侧三个候选落点本身没在本单复核 (ISS-379 已签收·只读引用·本单不重算板侧铜)** · ★**② `J_DEBUG` / `J_UART` 座体真实型号与真实高 `h` = `[0数据]` (本机无厂商图纸 ⇒ 已给降级方案)** · ★**③ 装配实测未做 (样件兜底 = `DP-5`)** ★ |

---

## ★B3 证据分级 ★

| 断言 | 等级 | 出处 / 复跑 |
|---|---|---|
| 罩开口 `O` / 座体必须清空区 `H` 的坐标与宽度 (两件) | ★`[实测]` ★ | `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` §3.4 / §3.5 + L72 机器块 · 闸 K3.3 现场回读比对 |
| `CRIT = 0.60` · `TOL["fdm_part"] = 0.30` | ★`[实测]` ★ | `MECH/service_port_check.py` **L126-L127** (★闸现场读源码·不写死·反向用例 03 证明改源码闸读数跟着变★) |
| 现状铜箔包络 (`1.7750×0.9000` / `0.7750×0.9000`) | ★`[实测]` ★ | `logs/iss377/board_connectors.json` (ISS-377 已签收) + ISS-371 §0.3 |
| 官方 THT 铜箔包络 (`4.8100×1.0000` / `2.2700×1.0000`) | ★`[实测]` ★ | ISS-371 §0.1 / ISS-374 §1.2 (★解析本机 KiCad 官方 `.kicad_mod` 实算★) |
| 官方 THT land 局部铜箔包络 (rot 90 / rot 270) | ★`[实测]` ★ | `HW/PCB/BOARD_ONEPASS_JUART_LAND_FIT.md` §9 `CU` 机器块 (ISS-379 已签收) |
| 三个候选落点 (朝向 / pad1 / 板侧余量 / 位移) | ★`[实测]` ★ | `HW/PCB/BOARD_ONEPASS_JUART_LAND_FIT.md` §2.3 (ISS-379 已签收) |
| 全部余量 (开口 / 罩住 / 最坏 / 三候选实口径 / 三清空区竞争值) | ★`[推算]` ★ | 真相页 §1~§3 + 闸现场重算 (K3 逐项对拍) |
| 达标所需每边名义余量 `0.9000` · 清空区 X 需求 `4.0700`/`6.6100` · Y 向零余量 | ★`[推算]` ★ | 真相页 §0 / §2.1 / §4 |
| 官方 land 的 `F.Fab` `5.0800` X / `F.CrtYd` `6.0900` X | ★`[实测]` ★ | ISS-371 §0.1 |
| 座体真实高 `h` / 厂商料号 / keepout 图纸 | ★`[0数据]` ★ | ISS-267 F-8 / ISS-380 §3.3 ⇒ 降级方案 §5.1 `DP-1`~`DP-5` |
| `J_UART` 落点选哪个 / `J_DEBUG` 清空区 X 宽取哪个 | ★`[0数据]` (★待 main 裁决★) ★ | ★**本单不选 · 不答** ⇒ 三候选全给判决 · 三值全给代价 ★ |

★**本单实际用到的等级**: ★`[实测]` / ★`[推算]` / ★`[0数据]` (★白名单五级·未越界·闸 K7.1 现场校验★) ★

---

## ★B4 接口取值声明 (★我认领了什么 / 我没认领什么★)★

★**我认领 (★mech-lead 的结构侧口径★)**:

| 接口 | 取值 | 证据等级 | 出处 |
|---|---|---|---|
| `iss386_same_table_rows` | ★`J_DEBUG`/`status_quo` + `J_DEBUG`/`official_tht` + `J_UART`/`status_quo` + `J_UART`/`official_tht` 四行同表 (13 列) ★ | `[实测]`+`[推算]` | 真相页 §1 + 机器块 `rows` |
| `iss386_debug_official_tht` | ★铜箔 `4.8100×1.0000` · 开口余量 X `2.6950` (最坏 `2.3950`) · 罩住余量 X `-1.5175` (最坏 `-1.8175`) · 罩住 Y `0.7700` (最坏 `0.4700`) ⇒ **罩住红 / 开口绿** ★ | `[实测]`+`[推算]` | 真相页 §1 + 机器块 |
| `iss386_uart_official_tht` | ★铜箔 `2.2700×1.0000` · 开口余量 X `3.8300` (最坏 `3.5300`) · 罩住余量 X `0.1350` (最坏 `-0.1650`) · 罩住 Y `0.7700` (最坏 `0.4700`) ⇒ **罩住红 / 开口绿** ★ | `[实测]`+`[推算]` | 真相页 §1 + 机器块 |
| `iss386_juart_cand_c1` | ★rot 270 `(18.6000,68.6000)` · copper X `16.8300..19.1000` × Y `68.1000..69.1000` · 罩住最坏 `-1.0900` (红) · 开口最坏 `+0.7300` (绿) ★ | `[实测]`+`[推算]` | 真相页 §2 + 机器块 `j_uart_candidates[0]` |
| `iss386_juart_cand_c2` | ★rot 90 `(18.4000,68.4000)` · copper X `17.9000..20.1700` × Y `67.9000..68.9000` · 罩住最坏 `-0.3100` (红) · 开口最坏 `+0.7300` (绿) ★ | `[实测]`+`[推算]` | 同上 `[1]` |
| `iss386_juart_cand_c3` | ★rot 90 `(18.3000,68.6000)` · copper X `17.8000..20.0700` × Y `68.1000..69.1000` · 罩住最坏 `-0.2100` (红) · 开口最坏 `+0.7300` (绿) ★ | `[实测]`+`[推算]` | 同上 `[2]` |
| `iss386_debug_clear_x_candidates` | ★`1.7750` → 罩住 `-1.5175`/最坏 `-1.8175`/每边超 `1.5175` ; ★`4.0850` → `-0.3625`/`-0.6625`/`0.3625` ; ★`4.8100` → `0.0000`/`-0.3000`/`0.0000` ⇒ **三者全红** ★ | `[实测]`+`[推算]` | 真相页 §3 + 机器块 `j_debug_clearance_x_candidates` |
| `iss386_frame_dependency` | ★帧 id = `B160x100` ; ★**三个候选的绝对坐标挂在该帧上 ⇒ 若上位问题落乙, 三个坐标【全部作废】** ; ★**但 FW-1~FW-5 五条结论全是【宽度/余量/相对位置】结论 ⇒ 与帧无关 ⇒ 坐标作废不影响判决** ★ | `[推算]` | 真相页 §2.1 + 机器块 `frame_independent` |
| `iss386_required_margin` | ★达标所需每边名义余量 = `CRIT + TOL["fdm_part"]` = `0.9000` ; ⇒ `J_DEBUG` 清空区 X 需 ≥ `6.6100` ; `J_UART` 清空区 X 需 ≥ `4.0700` (中心随落点: `17.9650`/`19.0350`/`18.9350`) ; 两件清空区 Y 需 ≥ `2.8000` 而开口 Y 只容 `2.8000` ⇒ **Y 向零余量** ★ | `[推算]` | 真相页 §0 / §2.1 / §4 |
| `iss386_criterion_source` | ★判据链 = ISS-377 §0.1 ; ★`CRIT`/`TOL` = `MECH/service_port_check.py` L126-L127 现场读 (不写死) ★ | `[实测]` | 机器块 `criterion` + 闸 K5 |

★**我【不】认领 (★裁决权不在结构侧★)**: ★**`OI-5` (`J_DEBUG` 清空区 X 宽取哪个) ⇒ main** · ★**`J_UART` 落点三选一 ⇒ main (已被 ISS-379 挂起, 本单不重开)** · ★**`B33` 换 land 范围 ⇒ main (OI-2)** · ★**座体真实高 `h` 定版 ⇒ boss (OI-11)** · ★**⑤ 罩住判据是否过严 ⇒ main + boss (OI-12)** · ★**Y 向零余量是否接受 ⇒ main + boss (OI-13)** ★

---

## ★B5 未决项与卡点 (★需要谁回答什么★)★

| # | 未决项 | 要谁回答什么 | 为什么不本单答 | 代价 / 期限 |
|---|---|---|---|---|
| ★**OI-5** ★ | ★`J_DEBUG` 的「必须清空区 X 宽」以哪个数为准 (`1.7750` / `4.0850` / `4.8100`) ★ | ★**main**: 「`J_DEBUG` 的『必须清空区 X 宽』取哪一个?」 ★ | ★三个数在仓里并存 (ISS-377 §2-C3) ; ★**本单只摆三行事实与代价, 不代拍** ★ | ★**三者红绿方向相同 (全红) ⇒ 只改返工幅度 (每边 `1.5175`/`0.3625`/`0.0000`) ; 但结构件【无论如何都要动】 ⇒ 开工前必须定** ★ |
| ★**OI-3** ★ | ★`J_UART` 落点三选一 (rot 270 / rot 90 / rot 90) ★ | ★**main** (★已被 ISS-379 裁决挂起, 本单【不重开】, 只登记依赖★) ★ | ★落点裁决权在 main ★ | ★**三候选的 3D 判决本单已全部给出且同向 ⇒ 落点裁决【不被结构侧阻塞】 ; 但结构件【中心】依赖落点 ⇒ 出件必须等落点定死** ★ |
| ★**OI-2** ★ | ★`B33_PIN_LAND_1P27` 的范围是否含 `J_UART` ★ | ★**main** (ISS-377 已登记, 本单沿用) ★ | ★板那一趟的范围裁决权在 main ★ | ★含 ⇒ 两件结构件同批返工 ; 不含 ⇒ `J_UART` 结构件零返工 ★ |
| ★**OI-11** ★ | ★`J_DEBUG` 座体真实高 `h` = `[0数据]` ★ | ★**boss**: 「`h` 走三档参数化, 还是定版一个值锁死?」 ★ | ★无实物依据 ; 本单按 Z 向保守上界 `4.70` 参数化 (ISS-380 §3.3-② 同源) ★ | ★**X 向判决与 `h` 无关 ⇒ 不阻塞 `OI-5`** ; Y 向判决随 `h` 变 (真相页 §3.1) ★ |
| ★**OI-12** ★ | ★⑤ 罩住判据对 THT 排针是否过严 (★判据要求 `6.6100` > 官方 land `F.CrtYd` `6.0900`★) ★ | ★**main + boss** ★ | ★口径裁决权不在结构侧 ; 本单只摆事实 ★ | ★口径一改, §1~§3 全部余量要重算 ⇒ 越早定越省返工 ★ |
| ★**OI-13** ★ | ★Y 向零余量 (开口 Y `4.6000` 只容清空区 Y `2.8000`) 是否接受 ★ | ★**main + boss** ★ | ★口径 + 成本取舍 ★ | ★接受 ⇒ 装配无容错 ; 放大 ⇒ 罩开口 Y 重做 (≥ `5.6000`) ⇒ 两件同批 ★ |
| ★**OI-14** ★ | ★ISS-377 §3.2 `DP-1` 的 `J_UART` 清空区 `3.4700` (名义余量口径) 是否订正为 `4.0700` (全链口径) ★ | ★**main** (★订正块只写在本单新页, 不回头改老页★) ★ | ★老页是已签收件, 本单零改 ★ | ★差 `0.6000` ⇒ 按 `3.4700` 出件仍不过阈 ★ |
| ★**OI-15** ★ | ★`J_UART` 三候选里 pad1 位移 `0.2441` 的归属 (★任务书记在 `(18.4000,68.4000)` 名下, ISS-379 §2.3 实为 `(18.5000,68.4000)` 的值) ★ | ★**main / hw-lead** 核对即可 ★ | ★本单只登记订正, 不改 ISS-379 页 ★ | ★不影响任何余量/判决, 只影响「挪多远」的账 ★ |

★**★本单没有需要外部回复才能推进的项 (★零外发·★零挂链★)**: ★**所有 `[0数据]` 处都给了降级方案 (真相页 §5.1 `DP-1`~`DP-5`) ⇒ 没有任何一条卡在外部依赖上** ★

---

## ★B6 自证复现命令 (★逐条可跑·★rc 已实测★)★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses

# ★★本单新建闸 (★只读·零挂链·★判据 201 条)★★
python3 MECH/check_debug_seat_3d_fit.py             # rc=0 · 末行 PASS · 判据 201 条失败 0 条
python3 MECH/check_debug_seat_3d_fit.py --selftest  # rc=0 · 末行 ALL TESTS PASS · 反向用例 18/18
python3 MECH/check_debug_seat_3d_fit.py --emit      # 机器块 JSON (页内 §9 就是它)

# ★★既有闸回归 (★只跑不改·★前后逐字相同)★★
python3 MECH/check_onepass_struct_crosscheck.py;      echo rc=$?   # rc=0
python3 MECH/check_onepass_mech_sync.py;               echo rc=$?   # rc=0
python3 MECH/check_jdebug_arrangement_truth.py;        echo rc=$?   # rc=0
python3 MECH/check_jdebug_1p27_clearance.py;           echo rc=$?   # rc=0
python3 MECH/check_juart_1p27_clearance.py;            echo rc=$?   # rc=0
python3 MECH/check_mech_verdict_freshness.py;          echo rc=$?   # rc=0
python3 MECH/check_board_frame_coords.py --compute;    echo rc=$?   # rc=0
python3 MECH/check_connector_clearance_caliber.py;     echo rc=$?   # rc=1 ★**基线红·非本单引入·前后逐字相同**★

# ★★零写板 / 零落表 / 零改既有件 / 零挂链 自证★★
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
stat -c '%n %y %s' HW/PCB/demo_mainboard.kicad_pcb
md5sum MECH/check_onepass_struct_crosscheck.py MECH/check_onepass_mech_sync.py \
       MECH/check_jdebug_arrangement_truth.py MECH/check_jdebug_1p27_clearance.py \
       MECH/check_juart_1p27_clearance.py MECH/check_board_frame_coords.py \
       MECH/check_mech_verdict_freshness.py MECH/service_port_check.py \
       MECH/check_connector_clearance_caliber.py
md5sum MECH/BOARD_ONEPASS_CONNECTOR_CLEARANCE_CALIBER.md MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md \
       MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md MECH/BOARD_ONEPASS_JDEBUG_ARRANGEMENT_TRUTH.md \
       MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md MECH/BOARD_ONEPASS_MECH_CLAIMS.md \
       MECH/BOARD_ONEPASS_MECH_SYNC.md HW/PCB/BOARD_ONEPASS_JUART_LAND_FIT.md
grep -c check_debug_seat_3d_fit state/gate_check.py     # 必须 0

# ★★台账侧 (★签收归 main·本单不自签★)★★
python3 state/merge.py                                   # rc=0
python3 state/gate_check.py                              # rc=0 · Q1 18/18
python3 state/check_brief_commands.py                    # rc=0
```

★**留证文件**: ★`logs/iss386/gate_run.txt` (裸跑全文) · ★`logs/iss386/gate_selftest.txt` (18 条反向用例全文) · ★`logs/iss386/boundary_selfcheck.txt` (边界自证全文) · ★`tmp/iss386_sbx/block.json` (机器块留证) ★

★**★交卷人自审一句话★**: ★**本单只交【分析 + 新闸 + 沙盒预演】, 没动板、没落表、没改任何已签收件、没挂链、没外发、没替 main 落点、没替 main 答 `OI-5`、没猜座体高度 ; 唯一新增的事实是【三条结构侧硬结论】(① `J_DEBUG` 结构件那一趟无论如何都要动 ② 要过罩住判据的清空区 X 宽需求 `4.0700`/`6.6100` ③ Y 向零余量) 与【一处订正】(ISS-377 `DP-1` 的 `3.4700` 缺 `0.6000`)★**

---

## ★B7 本趟 (cont1) 独立复核段 (★2026-11-24 08:53~08:58 · mech-lead · 收尾趟★)★

★**本段是【追加】, `B1~B6` 一字未改** ★(★追加前整页 md5 = `99d724ed3bc043857403674ec4977487` / 24,733 B ⇒ 追加前逐字校验通过★) ★

### ★B7.1 本趟定位与做法 ★

★**上一趟 (08:28:50~08:45:36 · 16.6 min · `status=timeout`) 死因 = 墙掐在最后一次 `state/merge.py` / `state/gate_check.py` 复跑上 ⇒ 三件交付物全部已在盘, 但【交卷消息】没发出来 ⇒ 零交卷** ★
★**⇒ 本趟 = 【收尾趟】: 独立复核 + 补缺 + 交卷消息 ⇒ ★★一件交付物都没重做★★** ★

★**本趟实际动作 (逐条自报)** ★:
1. ★**独立复核**: §四 必跑命令**全部自己实跑一遍** (★不抄 main 的读数, 不抄上一趟留证★) ⇒ 原样输出落 `logs/iss386/cont1_verify.log` (★584 行★) ★
2. ★**补缺 1 条**: 分片 `needs_from` 里**没有 `OI-15`** (★B5 表里有、真相页 §2 有、但 `needs_from` 没登记★) ⇒ 走 `state/frag_write.py --agent mech-lead --add-need` 补登 ⇒ `needs_from` 173 → 174 (★key 不重复, 实测 dup=0★)
3. ★**交卷消息**: 本段 + 本次回复正文

### ★B7.2 §四 必跑命令 · 本趟原样输出 + rc (★一条不省★)★

```
$ python3 MECH/check_debug_seat_3d_fit.py
★CRIT/TOL 现场从 MECH/service_port_check.py 源码读: CRIT = 0.6 · TOL['fdm_part'] = 0.3
★要求每边余量 >= CRIT + TOL = 0.9
[ok]   K9.1       ✓
[ok]   K9.2       ✓
[ok]   K9.3       ✓
[ok]   K9.3       ✓
[ok]   K9.3       ✓
[ok]   K10.1      ✓
[ok]   K10.2      ✓
[ok]   K10.2      ✓
[ok]   K10.2      ✓
[ok]   K10.3      ✓
[ok]   K10.4      ✓
[ok]   KCHAIN     ✓
判据 201 条 · 失败 0 条
PASS
rc=0
```

```
$ python3 MECH/check_debug_seat_3d_fit.py --selftest
[ok]   c01_drop_candidate     rc=1 且点名 K2 ✓  (★`J_UART` 三个候选落点必须全部有判决: 实有 2 个 (期望 3))
[ok]   c02_frame_id           rc=1 且点名 K6 ✓  (★机器块 frame_id 'F30A' ≠ 'B160x100' (帧 id 写错/被改))
[ok]   c03_tol_changed        rc=1 且点名 K3 ✓  (页内声明的 CRIT 0.6 ≠ 源码实读 0.8 (阈值改了必须跟着改声明))
[ok]   c04_wrong_margin       rc=1 且点名 K3 ✓  (同源表行 ('J_UART', 'official_tht') 的余量数与机器块不一致: 缺 ['0.5350'])
[ok]   c05_flip_verdict       rc=1 且点名 K4 ✓  (J_UART official_tht 轴 x 判决: 页内 True ≠ 实算 False)
[ok]   c06_crit_hardcoded     rc=1 且点名 K5 ✓  (机器块缺 CRIT/TOL 取法声明 (必须指向 MECH/service_port_check.py 源码): '0.60 (写死)')
[ok]   c07_split_tables       rc=1 且点名 K1 ✓  (同源表缺行: 缺 [('J_UART', 'status_quo')] (实有 [('J_DEBUG', 'official_tht'), ('J_DEBUG', 'status_quo'), ('J_UART', 'o)
[ok]   c08_drop_clear_x       rc=1 且点名 K1b ✓  (★`J_DEBUG` 清空区 X 宽三个竞争值必须齐全: 实有 [1.775, 4.085], 期望 [1.775, 4.085, 4.81])
[ok]   c09_pick_landing       rc=1 且点名 K10 ✓  (★本页不许替 main 落点: landing_point_decision = 'rot270' (必须是 not_decided_here))
[ok]   c10_drop_void_stmt     rc=1 且点名 K6 ✓  (页内缺『若上位问题落乙 ⇒ 三个候选坐标全部作废』的声明)
[ok]   c11_drop_evidence      rc=1 且点名 K7 ✓  (J_DEBUG status_quo 行缺证据等级)
[ok]   c12_pending_wording    rc=1 且点名 K8 ✓  (页内出现挂起措辞: '等原厂回信' (禁止把外部依赖挂着当阻塞项))
[ok]   c13_board_changed      rc=1 且点名 K9 ✓  (板 md5 a1e4cd56809969686c938266909512e2 ≠ 基线 611b869e13518c3c023fb178f91a0075 (零写板被破坏))
[ok]   c14_drop_degrade       rc=1 且点名 K8 ✓  (降级方案少于 3 条 (查不到处必须给降级方案): 2)
[ok]   c15_netlist_changed    rc=1 且点名 K9 ✓  (HW/netlist_v1.csv md5 b53de80c17f4271c7a14fd495fa19c09 ≠ 基线 6aee500e60ba0732f83a9cf557ba90ab (零落表被破坏))
[ok]   c16_chained            rc=1 且点名 KCHAIN ✓  (★本闸被挂进了 state/gate_check.py (本单零挂链·挂不挂归 main))
[ok]   c17_drop_oi5           rc=1 且点名 K10 ✓  (页内未登记 OI-5 (`J_DEBUG` 清空区 X 宽以哪个数为准 ⇒ to=main))
[ok]   c18_drop_frame_indep   rc=1 且点名 K6 ✓  (机器块缺帧无关结论 (frame_independent.statements))
反向用例 18 条, 通过 18 条
ALL TESTS PASS
rc=0
```

★**★selftest 本趟是【自己跑的】(★不是引用上一趟留证★)**: ★**08:53:48 起跑, 18/18 全过, 末行 `ALL TESTS PASS`, rc=0** ★
★★**且与上一趟留证 `logs/iss386/gate_selftest.txt` 逐字相同 (★`diff` 实测零差异, 只差本趟自己加的 `RC=0` 行★) ⇒ 反向用例集没有被偷改** ★★

```
$ python3 MECH/check_onepass_struct_crosscheck.py     ⇒ rc=0   (末行【绿】N1~N6 全过)
$ python3 MECH/check_onepass_mech_sync.py             ⇒ rc=0   (末行 口径提醒: 一切「实测」= 文件实读 + 脚本实跑; 实物 [实测] = 0 条)
$ python3 MECH/check_jdebug_arrangement_truth.py      ⇒ rc=0   (末行 合计: 6/6 条判据通过)
$ python3 MECH/check_jdebug_1p27_clearance.py         ⇒ rc=0   (末行 合计: 7/7 条判据通过)
$ python3 MECH/check_juart_1p27_clearance.py          ⇒ rc=0   (末行 RESULT: PASS (9/9 判据通过))
$ python3 MECH/check_mech_verdict_freshness.py        ⇒ rc=0   (末行 ⇒ 全绿 (F1~F6) rc=0)
$ python3 MECH/check_board_frame_coords.py --compute   ⇒ rc=0   (末行 clr 0.50 ⇒ 可落位带 2075 条 · 整高 2 条 · 最近原点 (8.420, 64.200) · LED_G_D = 0.965 mm)
```

★**★六个既有闸: merge 前 / merge 后各跑一遍, 输出【逐字相同】(★`diff` 实测, 6/6 = True★)** ★:
```
  check_onepass_struct_crosscheck      pre_rc=0 post_rc=0  逐字相同=True
  check_onepass_mech_sync              pre_rc=0 post_rc=0  逐字相同=True
  check_jdebug_arrangement_truth       pre_rc=0 post_rc=0  逐字相同=True
  check_jdebug_1p27_clearance          pre_rc=0 post_rc=0  逐字相同=True
  check_juart_1p27_clearance           pre_rc=0 post_rc=0  逐字相同=True
  check_mech_verdict_freshness         pre_rc=0 post_rc=0  逐字相同=True
```

```
$ python3 state/merge.py
✅ STATE.yaml 已刷新 (2026-11-24T08:54:04+08:00)
   产出 839 | 阻塞 43 (高危 33) | 未闭合需求 365 | 冲突 0 | 健康度 red
rc=0

$ python3 state/gate_check.py
【Q1 交付齐备率】 18/18 个必填验收块齐全
   hw-lead    6/6  缺: 无
   sw-lead    6/6  缺: 无
   mech-lead  6/6  缺: 无   交接单: 2026-11-24_mech-lead_ISS386_JDEBUG与JUART座体开口清空区合一件答.md
【Q2 证据分级率】 3/3 个总工的交付做了证据分级
【Q3 接口声明率】 全员 interface_claims 共 1198 条 (mech-lead 383 条)
【Q4 需求闭环率】 问方视角 136/553 · 答方视角 243 条 (mech-lead 我答 85 条 (有效 21) · 被答 50/173)
【Q5 硬指标覆盖】 1/3 个总工报出了 ≥3 类硬指标数字
【Q6 硬件真源闸】 HW pinout 真源闸: ✅ 通过 (rc=0)
【Q7 钉板 md5 闸链】 10/10 道绿
rc=0

$ python3 state/check_brief_commands.py
── 查了 9 条待办单的 task_brief, 有问题的 0 条
rc=0
```

★**★基线闸 (★red 是基线, 不是本单引入★)**: ★`python3 MECH/check_connector_clearance_caliber.py` ⇒ **rc=1** (★`RESULT: FAIL (1 条不通过)` · K7 FAIL: `MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md` md5 `f1ce54c9…` ≠ 已签收基线 `ffc09939…` + `MECH/check_juart_1p27_clearance.py` md5 `daf8fa36…` ≠ 已签收基线 `ea89e0dd…`★) ★
★★**本趟连跑两次, 两次输出逐字相同 ⇒ 这条红是【本单之前就红】, 与本单零写板零落表零改已签收件无关 (★本单没碰这两个文件, md5 与上一趟留证 `logs/iss386/boundary_selfcheck.txt` 完全一致★)★★ ★

★**★零挂链**: ★`grep -c check_debug_seat_3d_fit state/gate_check.py` ⇒ **0** (★开工前 0 / 收工 0, 两个读数一致★) ★

### ★B7.3 板 / 网表 / 脚表 / BOM 四项指纹 · 前后对比 (★零写板 · 零落表 · 纳秒级★)★

| ★项★ | ★开工前 (08:53:43)★ | ★收工前 (08:57)★ | ★结论★ |
|---|---|---|---|
| ★`HW/PCB/demo_mainboard.kicad_pcb` md5★ | `611b869e13518c3c023fb178f91a0075` | `611b869e13518c3c023fb178f91a0075` | ★**逐字相同 ⇒ 零写板** ★ |
| ★同上 mtime★ | `2026-11-06 07:07:17.362193413` | `2026-11-06 07:07:17.362193413` | ★**纳秒级未动** ★ |
| ★同上 size★ | `4940213` | `4940213` | ★**未动** ★ |
| ★`HW/netlist_v1.csv` md5★ | `6aee500e60ba0732f83a9cf557ba90ab` | `6aee500e60ba0732f83a9cf557ba90ab` | ★**逐字相同 ⇒ 零落表** ★ |
| ★`HW/netlist_v1_pins.csv` md5★ | `9174309df1ec9411ac8e8d9e80ee386a` | `9174309df1ec9411ac8e8d9e80ee386a` | ★**逐字相同 ⇒ 零落脚表** ★ |
| ★`HW/BOM_v1.csv` md5★ | `5b9993992405904a60ac96a020b375d8` | `5b9993992405904a60ac96a020b375d8` | ★**逐字相同 ⇒ 零落 BOM** ★ |
| ★`MECH/service_port_check.py` md5★ | `db58ff6a2afc28b8bf517e3c57c56bc1` | `db58ff6a2afc28b8bf517e3c57c56bc1` | ★**判据源头未动 (★CRIT/TOL 现场读的就是它★)** ★ |
| ★`MECH/check_onepass_struct_crosscheck.py` md5★ | `4eddd08fa4c1e9894a63b8cba0dee500` | `4eddd08fa4c1e9894a63b8cba0dee500` | ★**既有闸未动** ★ |

★**八个已签收件 md5 (★本趟全程未写★)★**: ★`73e3ec1db370c5667a9d8c5ec964c17e` / `f1ce54c981dd1f64071a177a374df85d` / `da7b02c013fa49c65b70ed3bea97b787` / `5ffaab52c1582425aa210d68ab3b1618` / `b254fa98c09bc7adb058e1d03eb13980` / `e91a594adebabeccddfff20fe787255a` / `ddd931ea7fe60277e03bc50b9092a6bc` / `8962321c2b94630a221b60fdbff4a5b1` ★
★★**⇒ 与上一趟留证 `logs/iss386/boundary_selfcheck.txt` 的「已签收页 md5 (交卷后)」一栏【逐字相同】⇒ 本趟一个字节都没动已签收件**★★

### ★B7.4 7 条 needs 复述 (★逐条「要谁回答什么」· 只登记不代拍★)★

| # | key | 要谁 | ★要谁回答什么★ | 不本单答的理由 |
|---|---|---|---|---|
| 1 | `iss386_oi5_jdebug_clearance_x_pick_one` | ★**main** ★ | ★「`J_DEBUG` 的『必须清空区 X 宽』取 `1.7750` / `4.0850` / `4.8100` 哪一个?」 ★ | ★三个值在仓里并存 (ISS-377 §2-C3) ; ★**本单只摆三行事实与代价, 不代拍** ★ |
| 2 | `iss386_oi3_juart_landing_dependency` | ★**main** ★ | ★「`J_UART` 落点三选一 (rot 270 / rot 90 / rot 90) 定哪个? (★已被 ISS-379 裁决挂起, 本单【不重开】, 只登记依赖★)」 ★ | ★落点裁决权在 main ★ |
| 3 | `iss386_oi2_b33_land_scope` | ★**main** ★ | ★「`B33_PIN_LAND_1P27` 的范围含不含 `J_UART`?」 ★ | ★板那一趟的范围裁决权在 main ★ |
| 4 | `iss386_oi11_seat_height_h` | ★**boss** ★ | ★「`J_DEBUG` / `J_UART` 座体真实高 `h` 走三档参数化, 还是定版一个值锁死?」 ★ | ★实物 `[0数据]` ; 本单按 Z 向保守上界 `4.70` 参数化 (ISS-380 §3.3-② 同源) ★ |
| 5 | `iss386_oi12_cover_criterion_too_strict` | ★**main** ★ | ★「⑤ 罩住判据 (座体清空区必须罩住铜箔、每边 ≥ `CRIT`) 对 THT 排针是不是过严?」 ★ | ★口径裁决权不在结构侧 ; ★事实: 要过判据 `J_DEBUG` 清空区 X 需 `6.6100`, 而官方 land 自己的 `F.CrtYd` 只有 `6.0900` X ⇒ ★判据比 courtyard 还大 `0.5200`★ ★ |
| 6 | `iss386_oi13_y_zero_margin` | ★**main** ★ | ★「Y 向零制造余量接受吗? 还是要开口 Y 一起放大 (≥ `5.6000`) ?」 ★ | ★口径 + 成本取舍 ★ |
| 7 | `iss386_oi14_iss377_dp1_gap` | ★**main** ★ | ★「ISS-377 §3.2 `DP-1` 给的 `J_UART` 清空区 `3.4700` (名义余量口径) 订正为 `4.0700` (全链口径) —— 差 `0.6000`, 要不要往老页落?」 ★ | ★老页是已签收件, 本单零改 ⇒ ★订正块只写在本单新页★ ★ |
| ★8 (★本趟补登★)★ | ★`iss386_oi15_pad1_displacement_attribution` ★ | ★**main** ★ | ★「任务书记的 `0.2441` 是在 `(18.4000,68.4000)` 名下, ISS-379 §2.3 实为 `(18.5000,68.4000)` 的值 —— 哪一处是笔误?」 ★ | ★★**本趟复核发现的缺口**: ★B5 表里有 `OI-15`, 真相页 §2 也有这处订正, 但 `needs_from` 【没有登记】⇒ ★**本趟已补登** (走 `state/frag_write.py`, key 不重复, 实测 dup=0)★ ★ |

### ★B7.5 本趟发现的缺口 (★不糊过去★)★

★**缺口 1 (★已补·★唯一一处写入★)**: ★`OI-15` **漏登记** —— ★交卷页 `B5` 表列了 `OI-15`、真相页 §2 写了这处订正, 但分片 `needs_from` 里【没有对应条目】(★复核时 `grep -c 'iss386_oi15' state/fragments/mech.yaml` = 0★) ⇒ ★**本趟用 `state/frag_write.py --agent mech-lead --add-need` 补登** ⇒ `needs_from` 173 → 174 (★8 条 iss386 needs 全部无重复★) ★
★**缺口 2 (★已查清·★不是本单引入·★不改·★只报告★)**: ★`MECH/check_connector_clearance_caliber.py` 基线 rc=1 (K7 FAIL), 失败原因 = `MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md` 与 `MECH/check_juart_1p27_clearance.py` 两个文件的 md5 与「已签收基线」对不上 (★`f1ce54c9…` vs `ffc09939…` / `daf8fa36…` vs `ea89e0dd…`★) ⇒ ★**本趟连跑两次输出逐字相同, 且与上一趟留证一致 ⇒ 这条红在本单开工前就存在, 与本单无关; 本单不碰这两个文件 (★它们在「八个已签收件 + 既有闸」清单里, 一个字节不许动★) ⇒ ★**留待 main 裁 (★是它自己签收基线更新, 还是别的总工动过, 不归我判★)** ★
★**缺口 3 (★如实报·★不改口径★)**: ★`state/gate_check.py` 的 Q4 里 main 自己打了一行 ★`❌ 与 merge.py 不一致 (merge: 外部 46 / 总工 365 vs gate: 外部 46 / 总工 367)`★ ⇒ ★**本趟 `state/merge.py` → `state/gate_check.py` 是严格顺序跑的 (08:54:04 刷新 → 紧接着跑 gate) ⇒ 这个差值来自【别的总工在本趟跑闸期间又写了自己的分片】(★`state/fragments/hw.yaml` mtime `08:55:52` / `sw.yaml` mtime `08:54:11` —— 都晚于我的 merge 刷新时刻★) ⇒ ★**不是本单引入, 也不是本单能修 (★那两片不是我的地界★) ⇒ 只报告, 不代修** ★

### ★B7.6 本趟边界自证 (★七条逐条自签★)★

| ★项★ | ★自证★ |
|---|---|
| ★零写板★ | ★板 md5 `611b869e…` / mtime `2026-11-06 07:07:17.362193413` / size `4940213` 三项开工前后【逐字相同】★ |
| ★零落表★ | ★网表 `6aee500e…` / 脚表 `9174309d…` / BOM `5b999399…` 三项开工前后【逐字相同】★ |
| ★零改已签收件★ | ★八个已签收页 md5 与上一趟留证【逐字相同】; 本趟对它们只有 `md5sum` 读操作★ |
| ★零挂链★ | ★`grep -c check_debug_seat_3d_fit state/gate_check.py` = **0** (★开工前 0 / 收工 0★) ★ |
| ★零外发★ | ★本趟无任何邮件 / 询价 / 问询 / 采购动作; 无「批一句可以发」★ |
| ★不代拍★ | ★`OI-5` 只摆 `1.7750`/`4.0850`/`4.8100` 三值各自的后果与代价, ★**没写「应该用 4.8100」**; 落点 `landing_point_decision` 保持 `not_decided_here` (★闸 K10 + 反向用例 c09 都在判这一条★) ★ |
| ★未自签台账★ | ★`state/issue_log.yaml` mtime 仍为 `2026-11-24 08:27:30.614014326` / size `4788705` ⇒ ★**本趟未动 (★签收归 main★)** ★ |
| ★没写别人的分片★ | ★本趟只写 `state/fragments/mech.yaml` (★走 `state/frag_write.py`★); `hw.yaml` / `sw.yaml` / `pm.yaml` 未动 (★它们 mtime 的变化是别的总工自己写的, 不是我★) ★ |

★**★本趟写过的文件 (★穷举·★共 4 个★)★**: ★`logs/iss386/cont1_verify.log` (★新·留证★) · ★`logs/iss386/cont1_selftest_tmp.txt` (★新·selftest 留证★) · ★`HANDOFF/2026-11-24_mech-lead_ISS386_JDEBUG与JUART座体开口清空区合一件答.md` (★追加 B7★) · ★`state/fragments/mech.yaml` (★走 `frag_write.py` 补登 1 条 need★) ★

★**★本趟的自我判断 (★一句话★)★**: ★**上一趟的三件交付物经本趟独立复核【全部成立】—— 新闸裸跑 201 条判据 0 失败、selftest 18/18 全过且与上一趟留证逐字相同、六个既有闸 merge 前后逐字相同、板/网表/脚表/BOM 四项指纹逐字未动; 本趟只补了 1 处真缺口 (`OI-15` 漏登记) 并把交卷消息发出来 ⇒ ★★ISS-386 cont1 至此才算真正交卷★★** ★
