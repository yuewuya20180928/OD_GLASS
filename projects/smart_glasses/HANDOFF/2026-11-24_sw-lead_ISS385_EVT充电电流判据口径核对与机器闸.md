# 2026-11-24 · sw-lead · ISS-385 · EVT 充电电流判据口径核对与机器闸

> ★**单号**: ISS-385 (sw-lead) · **日期**: 2026-11-24 · **交接对象**: main (项目总工) / 老板
> ★**性质**: ★**纯分析 + 新建机器闸 + 沙盒预演** ⇒ ★**零写板 · 零落表 · 零改既有页面正文 · 零改既有闸 · 零挂链 · 零外发 · 不代拍** ★
> ★**一句话**: ★**`PWR-05` 的「充电电流 ≥ 1.5A」在现行 680Ω 档下【两个口径都达不到】(输入侧 0.5735A / 电池侧 0.6974A, 差 2.62× / 2.15×); 且该不兼容【在旧 0.822 系数下就已存在】⇒ 属【既存判据缺陷】; 且 `U_CHG`/`R_ILIM` 的 board 域【全是 `CHG_BOARD`】⇒ demo 主 PCB 上【没有这条充电链】; 另查出【同一行的第二个坑】: 「寄存器回读」不可达 (充电 IC 的 I2C 不过铰链)。三个改法候选 (甲/乙/丙) 已逐条摆清代价, **不代拍**。** ★

---

## B1 · 结论摘要

### B1.1 三问逐条答 (★每条都有机器判据支撑, 不许写「建议改成 X」了事★)

| 问 | 答 | 关键数字 (★本机实跑/实读 ★) | 判据在哪 |
|---|---|---|---|
| ★**Q1**: `PWR-05` 的「充电电流」量哪个量? ★ | ★**按【电池侧充电电流 `ICHG`】读** (证据 E1/E2/E3), ★**但结论对两个口径都成立 ⇒ 不必先赌对读法** ★ | ★**输入侧 `IINMAX` max = 0.5735294 A ⇒ 1.5A 差 2.6154×** · ★**电池侧 `ICHG` max = 0.6974118 A ⇒ 1.5A 差 2.1508×** ★ | ★真相页 §1 (证据表 E1~E5) + 闸 K3 (按语义对账) ★ |
| ★**Q2**: 判据怎么改? ★ | ★**三个候选全摆出来, 一个都不默认选**: ★**甲** = 单侧降阈 (≥0.60A, ★**丢失「R_ILIM 缺失」鉴别力★**) · ★**乙** = 双侧窗口 (0.54~0.75A, ★**保留鉴别力但现场易误判★**) · ★**丙** = 注明 demo 板不适用 + 移整机阶段 (★**改动面最大, 但单独用会留下错数★**) ★ | ★**谁定 = main / 老板 (U1)** ★ | ★真相页 §2 (含 §2.4 对照表) + §4 判据口径表 (C1~C6) ★ |
| ★**Q3**: 是不是这次才坏掉的? ★ | ★**不是。既存判据缺陷。** ★ | ★**旧 0.822 系数 + 390Ω 档: `ICHG` max = 0.822A ⇒ 1.5A 差 1.83× ⇒ 那时就永远判不过** ★ | ★真相页 §3 (时间线 + 事实分账 F1~F5) ★ |

### B1.2 ★★本单额外查出的【第二个坑】(★与 1.5A 无关, 同一行 L131 里★)★★

★**`charging_state=1` 的读回方式「寄存器回读」在硬件上【不可达】**: 充电 IC 的 `I2C_CHG_SCL`/`I2C_CHG_SDA` 全部在 `CHG_BOARD` (网表 L483/L485), ★**`MAIN_PCB` 上 `I2C_CHG_*` 行数 = 0** ⇒ SoC 读不到 `BQ25896` 的任何寄存器 ⇒ ★**项目自己在 `SW/SW_TIMING_REVIEW.md` L441 早就这么判过** ⇒ **可用替代 = `CHG_STAT` GPIO + `VBUS_DET` ADC 双通路 (`HW/CHARGE_STATUS_READBACK.md` B1, fail-safe)** ★
★**⇒ 任何改法都必须同时修「阈值」和「读回方式」两处, 只修阈值不够** ★

### B1.3 ★★本单登记的机器事实 (★全部本机实读, 可复现★)★★

| # | 事实 | 值 | 出处 |
|---|---|---|---|
| F1 | `U_CHG` board 域 | ★**10 行全 `CHG_BOARD`** (8 必装 + 2 DNP: pin12/pin24 = NC) ★ | `HW/netlist_v1.csv` |
| F2 | `R_ILIM` board 域 | ★**2 行全 `CHG_BOARD`** (必装) ★ | `HW/netlist_v1.csv` L47/L48 |
| F3 | **有 `board=MAIN_PCB` 的充电链行吗** | ★**0 行** (全表分布: `MAIN_PCB` 404 / `CHG_BOARD` 94 / `HINGE` 15) ★ | 同上 |
| F4 | `J_TYPE_C` (判据里的「插 Type-C」那个座) | ★**18 行全 `CHG_BOARD`** ★ | `HW/netlist_v1.csv` + `HW/BOM_v1.csv` L76 |
| F5 | demo 主 PCB 板文件里有充电链吗 | ★**没有**: `U_CHG` 0 次 / `R_ILIM` 0 次 (只有 `BAT_CHG` 21 次 / `TP_BAT_CHG` 1 次) ★ | `HW/PCB/demo_mainboard.kicad_pcb` |
| F6 | 电池座在 demo 板上装不装 | ★`BT_432243` **DNP** · `U_BATPROT` **DNP** ★ | `HW/BOM_v1.csv` L2 / L204 |
| F7 | demo 装机态有无充电板 | ★**无** (主板↔充电板唯一通路 `J_CHG` **DNP**) ★ | `SW/SHUTDOWN_SEMANTICS_SPEC.md` §0 L96 |
| F8 | 680Ω 档真值 (min/typ/max) | ★`IINMAX` 0.4706/0.5221/**0.5735** A · `ICHG` 0.5722/0.6348/**0.6974** A · 单 pin **0.3487** A ★ | `MECH/hinge_power_calc.json` `rilim_table` (本机实跑) |
| F9 | `PWR-05` 是不是唯一一处提充电电流 | ★**是** (全文 grep 只有 L131 一处) ★ | `SW/EVT_TEMPLATE.md` |
| F10 | 唯一够得着 1.5A 的档 | ★300Ω (`ICHG` 1.5808A) —— ★**但 300Ω 已因单 pin 0.7904A > 0.50A 触点上限判死** ★ | `HW/CHARGE_BOARD_SPEC.md` §2.4 L185 |

---

## B2 · 验收标准自评 (★逐条 通过 / 不通过 / 未验 ★)

| # | 验收项 | 判定 | 依据 (★本机实测读数 ★) |
|---|---|---|---|
| ★1 ★ | ★**Q1 答了 (量哪个量 + 证据行号 + 两口径真值)** ★ | ★**通过** ★ | ★真相页 §1: 读法 = `ICHG`, 证据 E1 (`SW/EVT_TEMPLATE.md` L131) / E2 (`HW/CHARGE_BOARD_SPEC.md` §2.4 L182~L186 + §3.4 L320) / E3 (`HW/CHARGE_CURRENT_RECHECK_2026-11-01.md` L56 + `HW/INTERFACE_TABLE.md` L106) / E4 (权威表实跑) / E5 (两口径都达不到 ⇒ 结论与读法无关) ★ |
| ★2 ★ | ★**Q2 答了 (三个候选 + 逐条代价 + 谁来定)** ★ | ★**通过** ★ | ★真相页 §2.1 甲 / §2.2 乙 / §2.3 丙, 每条含「判据具体写法 + 代价 4 条 + 谁来定」; §2.4 机器可读对照表; ★**§2.4 明写「本单不代拍」** ★ |
| ★3 ★ | ★**Q3 答了 (既存判据的事实分账)** ★ | ★**通过** ★ | ★真相页 §3: 时间线 (390Ω 旧系数 0.822A ⇒ 差 1.83×) + 分账 F1~F5 ⇒ ★**「不是 ISS-229 造成的」逐字写明** ★ |
| ★4 ★ | ★**Q2-丙 的 board 域结论【自己实读】过 (不许抄任务书)** ★ | ★**通过** ★ | ★**本机实跑** `csv.DictReader` 扫 `HW/netlist_v1.csv`: `U_CHG` 10 行 board 全 `CHG_BOARD` · `R_ILIM` 2 行 board 全 `CHG_BOARD` · **`MAIN_PCB` 0 行** ⇒ 另加 F4~F7 四条交叉证据 (板文件 grep / BOM / `SHUTDOWN_SEMANTICS_SPEC`) ★ |
| ★5 ★ | ★**网表/脚表/BOM md5 前后逐字相同 (零落表)** ★ | ★**通过** ★ | ★`HW/netlist_v1.csv` `6aee500e…` · `HW/netlist_v1_pins.csv` `9174309d…` · `HW/BOM_v1.csv` `5b999399…` ★**开工前后逐字相同** (见 B6) ★ |
| ★6 ★ | ★**板三项指纹逐字相同 (零写板)** ★ | ★**通过** ★ | ★md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · size `4940213` ★**三项开工前后逐字相同** (见 B6) ★ |
| ★7 ★ | ★**`SW/EVT_TEMPLATE.md` 正文 md5 前后逐字相同 (不许改它)** ★ | ★**通过** ★ | ★`773dcaf7432b66397a1fa3240c32c3ad` ★**开工前后逐字相同** ⇒ ★**正文一个字都没改** (★闸 K8 运行前后 md5 也自证一次★) ★ |
| ★8 ★ | ★**零改既有闸 (`s2_board_judge.py` / `s2_board_selftest.py` md5 逐字不变)** ★ | ★**通过** ★ | ★`38bf8a62fc4183e8a64fadd7f208631b` / `9fb6c7a097e11f4d206f4aa7f69db8c6` ★**开工前后逐字相同** ★ |
| ★9 ★ | ★**新闸裸跑 rc=0** ★ | ★**通过** ★ | ★`python3 SW/check_evt_charge_current_criterion.py` ⇒ ★**rc=0** ★ (pre 相; ★且 4 条既存缺陷被逐条点名, 不是静默绿★) ★ |
| ★10 ★ | ★**新闸 `--selftest` 末行 ALL TESTS PASS** ★ | ★**通过** ★ | ★`python3 SW/check_evt_charge_current_criterion.py --selftest` ⇒ ★**反向用例 20/20 通过, 末行 `ALL TESTS PASS`, rc=0** ★ |
| ★11 ★ | ★**`grep -c check_evt_charge_current_criterion state/gate_check.py` = 0 (零挂链)** ★ | ★**通过** ★ | ★**实测 = 0** ★ ⇒ ★**本闸零挂链, 挂不挂是 main 的地界 (U4)** ★ |
| ★12 ★ | ★**判据按【语义】判, 不按【子串】判 (本单命门)** ★ | ★**通过** ★ | ★闸 K2 用【比较符 + 数值 + 量纲】双向解析 + 浮点容差: ★**「≥1.5A」改「≤1.5A」/ 改「≥0.01A」/ 改「≥1.6A」/ 改窗口写法 ⇒ 全部判红并点名 (反向 1/2/3/14)** ★; ★**「1.50 A」「1500mA」同义改写 ⇒ 不误伤 (不误伤 1/2)** ★; ★**「@5V/2A 适配器」的 2A 不被当阈值 (不误伤 3)** ★ |
| ★13 ★ | ★**闸不许误伤: 不许改 EVT 模板正文来让自己绿** ★ | ★**通过** ★ | ★闸 K8 运行前后 `SW/EVT_TEMPLATE.md` md5 自证; ★**闸只读该文件, 无任何写路径**; ★**反证: 反向 5/6/7/13 把口径页机器块改坏 ⇒ 闸立刻红 ⇒ 证明它不是「无脑判绿」** ★ |
| ★14 ★ | ★**证据等级齐全 (五级固定口径: `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]`)** ★ | ★**通过** ★ | ★真相页 §5 证据分级表 ★**5 行, 五级齐全, 每行都带等级** ★ ⇒ ★**闸 K6 逐行校验 (缺等级或有一行没标等级 ⇒ 红; 反向 9 实测判红)** ★ |
| ★15 ★ | ★**零外发 (不许发任何邮件/询价/问询/采购)** ★ | ★**通过** ★ | ★**本单未发出任何对外消息**; ★**没有一条未决项是「等原厂回信」** (§6 六条全是 main 内部裁决 / 板到手自测) ★; ★**查不到的 = `[0数据]` + 降级方案** (`KILIM` 低电流档 trim 值 = 0 条 ⇒ 降级方案 = 按档位表 min/typ/max 三档取, 不依赖单一 trim 值) ★ |
| ★16 ★ | ★**不代拍** ★ | ★**通过** ★ | ★真相页 §2.4 + §6 U1 明写「选哪个 = main/老板的地界」; ★**本页与交卷页均未写死最终判据数值** (只给候选 + 代价) ★ |
| ★17 ★ | ★**只写本任务允许的文件** ★ | ★**通过** ★ | ★**新建 3 件** (`SW/EVT_CHARGE_CURRENT_CRITERION_CALIBER.md` · `SW/check_evt_charge_current_criterion.py` · 本交卷页) + ★**分片只写 `state/fragments/sw.yaml`** (走 `state/frag_write.py --agent sw-lead` ⇒ 工具内部按 `FILE_OF` 强制映射到 `sw.yaml`, 物理上无法写别人分片) ⇒ ★**`hw.yaml`/`mech.yaml`/`pm.yaml` 本单【一次都没写过】** (★注: 交卷期间 `hw.yaml`/`mech.yaml` 的 md5 由【别的总工并发写】而变 (hw-lead 08:55:52 / mech-lead 08:39:18, 两份 `updated_by` 均为本人) ⇒ ★**不是本单写的**, 不据此自证★) ★ |
| ★18 ★ | ★**不自签 `state/issue_log.yaml`** ★ | ★**通过** ★ | ★**签收归 main** ⇒ ★**本单未写 `state/issue_log.yaml`** (mtime `2026-11-24 08:27:30` 早于本单任何写入) ★ |
| ★19 ★ | ★**沙盒只落 `tmp/iss385_sbx/` + `logs/iss385/`, 未用 `cp -al`** ★ | ★**通过** ★ | ★闸的 `--selftest` 用 `shutil.copy2` 逐件复制到 `tmp/iss385_sbx/selftest/case_*/`; ★**未用硬链接** (★本项目吃过硬链接的亏★) ★; ★**证据落 `logs/iss385/boundary_proof.txt`** ★ |
| ★20 ★ | ★**证据分级表里的 `[0数据]` 项都配了降级方案** ★ | ★**通过** ★ | ★真相页 §5 `[0数据]` 行: ① 板端实测 0 条 ② `ICHG` 波形/抬压 0 条 ⇒ C4 判读法改为「记 V0, 不预设」 ③ `KILIM` 低电流档 trim 0 条 ⇒ 降级 = 按 min/typ/max 三档取 ★ |
| ★21 ★ | ★**板端实测值** ★ | ★**未验** ★ | ★**板未投板** ⇒ ★**一切板端结论都不是 `[实测]`** ⇒ ★**闸能判的是【判据文本 vs 硬件真值】的相容性, 不是板端通没通过** ★ |
| ★22 ★ | ★**最终判据改成哪一条** ★ | ★**未验 (★不代拍★)** ★ | ★**U1 待 main / 老板拍** ⇒ ★**本单只交候选 + 代价 + 闸** ★ |

---

## B3 · 证据分级

★**本单主体 = `[实测]` (本机实读文件 + 实跑 `MECH/hinge_power_calc.py` + 实读网表 board 域)** ★

| 等级 | 本单用它标什么 | 条目 |
|---|---|---|
| ★`[实测]` ★ | ★本机实跑/实读 (可复现) ★ | ★① `MECH/hinge_power_calc.py --json` rc=0 ⇒ `rilim_table` 680Ω 档 min/typ/max (`ICHG` 0.5722/0.6348/0.6974 A · `IINMAX` 0.4706/0.5221/0.5735 A · 单 pin 0.3487 A) ② 网表 board 域 (`U_CHG` 10 行 + `R_ILIM` 2 行全 `CHG_BOARD`, `MAIN_PCB` 0 行) ③ 板文件 `U_CHG`/`R_ILIM` 0 次 ④ BOM `BT_432243`/`U_BATPROT` DNP · `J_TYPE_C` `CHG_BOARD` ⑤ `SW/EVT_TEMPLATE.md` 全文只有 L131 提充电电流 ⑥ `grep -c check_evt_charge_current_criterion state/gate_check.py` = 0 ⑦ 板三项指纹 + 网表三件 + EVT 模板 + 既有闸两份 md5 前后逐字相同 ⑧ 新闸裸跑 rc=0 / `--selftest` 20/20 ALL TESTS PASS ⑨ 闸 `--phase post` rc=1 且逐条点名 ⑩ `--strict` rc=1 且逐条点名 ★ |
| ★`[官方]` ★ | ★厂商官网 / 官方 datasheet ★ | ★① `BQ25896` REG04 复位默认 `ICHG` = 2048 mA (`HW/CHARGE_BOARD_SPEC.md` §2.8 引 TI datasheet) ⇒ ★**用于算「R_ILIM 缺失」故障电流 2.048A** ★ ② `BQ25896` REG0B `CHRG_STAT` 位域 + STAT 输出极性 (低=充电中/高=完成或禁用/1Hz闪=故障) (`ti.com/lit/gpn/BQ25896`) ③ `IINMAX = KILIM/R_ILIM`, `KILIM` 320/355/390 AΩ ④ `R_ILIM` = 680Ω ±1% 必装 (网表 L47/L48 `evidence` 列 = `[官方]`) ★ |
| ★`[推算]` ★ | ★由上面两类推出 (写清过程) ★ | ★① 判据候选 0.60A = typ `ICHG` 0.6348 × 0.95; 备选 0.54A = min 0.5722 × 0.95 ② 窗口上限 0.75A = max 0.6974 × 1.08 ③ 不可达倍数 2.6154× (输入侧) / 2.1508× (电池侧) / 1.825× (旧 0.822 系数 390Ω) ④ C4 的「0.6A × 10min = 0.10Ah = 420mAh 的 24% ⇒ 10min 抬 0.1V 是否够须实测」 ⑤ 旧 390Ω 档 `ICHG` 0.822A (由旧网表 `value` 串逐字引, 非现算) ★ |
| ★`[媒体]` ★ | ★第三方报道 ★ | ★**本单零条** ⇒ 充电电流真值全部可从官方 datasheet + 权威表自算 ⇒ ★**不拿媒体报道当判据来源** ★ |
| ★`[0数据]` ★ | ★查不到 / 板端还测不了 ★ | ★① 板端实测电流 = **0 条** (板未投板) ② `ICHG` 实际波形 + 电池 10min 抬压 = **0 条** ⇒ C4 须实测 ③ `BQ25896` 低电流档 `KILIM` trim 值 = **0 条** (datasheet 只在 1.5A 工况点给 320/355/390) ⇒ **降级方案 = 按档位表 min/typ/max 三档取, 不依赖单一 trim 值 ⇒ 本单不需要发信给原厂** ★ |

---

## B4 · 接口取值声明 (interface_claims)

★**本单落 6 条 (★全部 to=main / 全项目可见, 供跨模块冲突检测★)★**

| key | value (★机器可读 ★) | 出处行号 | 等级 |
|---|---|---|---|
| ★`iss385_pwr05_measured_quantity` ★ | ★**`PWR-05` 的「充电电流」按【电池侧充电电流 `ICHG`】读** (输入侧 `IIN` 是另一读法, 但两者都达不到 1.5A ⇒ 结论与读法无关) ★ | ★`SW/EVT_TEMPLATE.md` L131 (同句并列三项全是电池侧可观测量) + `HW/CHARGE_BOARD_SPEC.md` §2.4 L182~L186 + §3.4 L320 (项目口径 `ICHG = IIN×η·Vbus/Vbat`) + `HW/CHARGE_CURRENT_RECHECK_2026-11-01.md` L56 (1.5A 出处 = 铰链设计点 `BAT_CHG`) + `HW/INTERFACE_TABLE.md` L106 ★ | ★`[实测]`+`[推算]` ★ |
| ★`iss385_pwr05_hardware_truth_680` ★ | ★**`R_ILIM`=680Ω 档真值: `IINMAX` min/typ/max = 0.4706/0.5221/**0.5735294** A · `ICHG` min/typ/max = 0.5722/0.6348/**0.6974118** A · 单 pin max = **0.3487059** A** ★ | ★`MECH/hinge_power_calc.json` `rilim_table` (`R_ILIM`=680, `tag`=min/typ/max) ⇒ **本机实跑 `python3 MECH/hinge_power_calc.py --json` rc=0 复算** ★ | ★`[实测]` ★ |
| ★`iss385_pwr05_unreachable_ratio` ★ | ★**判据要求 ≥1.5A ⇒ 输入侧差 1.5/0.5735294 = 2.6154×, 电池侧差 1.5/0.6974118 = 2.1508× ⇒ 【两个口径都永远判不过】** ★ | ★同上真值 (本单实算) ★ | ★`[推算]` ★ |
| ★`iss385_pwr05_applicability_demo_main_pcb` ★ | ★**`applicable_on_demo_main_pcb` = `false`** ⇒ ★**`U_CHG` 10 行 + `R_ILIM` 2 行 board 全 = `CHG_BOARD`, `MAIN_PCB` 上 0 行; `J_TYPE_C` 18 行全 `CHG_BOARD`; 板文件 `U_CHG`/`R_ILIM` 各 0 次; `BT_432243`/`U_BATPROT` 均 DNP; demo 装机态 `J_CHG` DNP** ★ | ★`HW/netlist_v1.csv` (全表扫) + `HW/BOM_v1.csv` L2/L76/L204 + `HW/PCB/demo_mainboard.kicad_pcb` + `SW/SHUTDOWN_SEMANTICS_SPEC.md` §0 L96 ★ | ★`[实测]` ★ |
| ★`iss385_pwr05_charger_register_unreachable` ★ | ★**充电 IC 的 `I2C_CHG_SCL`/`I2C_CHG_SDA` 全在 `CHG_BOARD`, `MAIN_PCB` 上 0 行 ⇒ SoC 读不到 `BQ25896` 寄存器 ⇒ `PWR-05` 的「寄存器回读」不可达 ⇒ 读回须用 `CHG_STAT` GPIO + `VBUS_DET` ADC 双通路** ★ | ★`HW/netlist_v1.csv` L483/L485 + `SW/SW_TIMING_REVIEW.md` L441 (`chg_state_source` = `CHG_STAT-主,PG-备,ADC-辅`) + `HW/CHARGE_STATUS_READBACK.md` B1 ★ | ★`[实测]`+`[官方]` ★ |
| ★`iss385_pwr05_defect_is_preexisting` ★ | ★**该不兼容属【既存判据缺陷】, 不是 ISS-229 造成**: 旧 0.822 系数 + 390Ω 档 `ICHG` max = 0.822A ⇒ 1.5A 差 1.825× ⇒ 判据写下那天起就永远判不过 ⇒ **ISS-229 只把差距从 1.83× 拉到 2.15×, 没有把它弄坏** ★ | ★`HW/SCHEMATIC_LANDING_WORKPACKET_V1.md` L227 (逐字引旧网表 L47/L48 `value` = 「390Ω ±1% (IINMAX ≈1.00A · ICHG ≈0.82A)」) + `MECH/hinge_power_calc.py` L16~L22 (系数方向修正说明) + `HW/netlist_v1.csv` L47 `note` ★ | ★`[实测]`+`[推算]` ★ |

---

## B5 · 未决项与卡点 (★需要谁回答什么 · ★全部可自行闭环, 没有一条是「等外部回复」★)

| # | 卡点 | 要谁答 | 答什么 | 阻塞等级 | 降级方案 (★不许挂着★) |
|---|---|---|---|---|---|
| ★U1 ★ | ★**`PWR-05` 最终采用甲/乙/丙哪个 (或组合)** ★ | ★**main / 老板** ★ | ★**从真相页 §2.4 对照表里选一行** ⇒ ★**本单只摆代价, 不代拍** ★ | ★**高** ★ | ★**main 不裁 ⇒ 闸 post 相一直红, 但不影响本单交卷 (闸零挂链, 不进项目门禁链)** ★ |
| ★U2 ★ | ★**判据落进 `SW/EVT_TEMPLATE.md` 的时机** ★ | ★**main** ★ | ★**必须与「改板那一趟」同批** (★模板版本 v1.0 + §0.4 判据来源表 + 七段判定矩阵 L79~L119 三处联动★) ⇒ **提前单独改 = 中间态 = churn** ★ | ★**高** ★ | ★**维持现状 (不动) = 本单默认状态; 闸 pre 相登记基线照样绿** ★ |
| ★U3 ★ | ★**落地时机器块登记值要同批更新** ★ | ★**main (执行时)** ★ | ★**main 改完 EVT 页后, 必须同批更新 `SW/EVT_CHARGE_CURRENT_CRITERION_CALIBER.md` 机器块的 `evt_current_criterion_a` / `evt_current_criterion_max_a`** ⇒ ★**否则本闸立刻报「口径被换掉」** (★这正是闸的设计意图: 盯口径漂移★) ★ | ★**中** ★ | ★**闸给出精确报错文本 (含现值与登记值), 照着改即可** ★ |
| ★U4 ★ | ★**本闸是否挂进 `state/gate_check.py`** ★ | ★**main** ★ | ★**本单【零挂链】(实测命中 0)** ⇒ 挂不挂是 main 的地界 (★先例: ISS-381 同款零挂链★) ★ | ★**中** ★ | ★**不挂 = 项目门禁链不受影响, 本闸仍可人工单跑** ★ |
| ★U5 ★ | ★**C4 的 10min 抬压 0.1V 在 `ICHG` 降到 0.6A 后是否仍可达** ★ | ★**sw-lead (板到手后自测)** ★ | ★**板通电后实测: 插 Type-C 前记 V0, 10min 后记 V1, 记 `V1-V0`** ⇒ ★**降级方案已写进 C4 判读法 (记 V0, 不预设门槛)** ⇒ **不依赖任何外部回复** ★ | ★**低** (板端事) ★ | ★**板不可达是物理事实, 不是等外部回复** ★ |
| ★U6 ★ | ★**充电链 board 域 = `CHG_BOARD` ⇒ demo 板无充电链, 这条架构事实要不要另开一单推动充电板** ★ | ★**main** ★ | ★**本单只登记 (F1~F7)**: **要不要另开「充电板落地」单 = main 的地界** ★ | ★**中** ★ | ★**本单不动任何架构, 只登记事实** ★ |

★**★零外发自证**: ★**上面 6 条里, 没有一条是「等原厂回信 / 等外部回复」** ⇒ ★**U1/U2/U3/U4/U6 = main 内部裁决 (自己就能闭环) · U5 = 板到手后自己测** ⇒ ★**全部可自行闭环, 不许把外部依赖挂着当阻塞项** ★

---

## B6 · 自证复现命令 (★逐条可复跑 ★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses

# ── §1 权威表复算 (★本单结论的数值来源★)
python3 MECH/hinge_power_calc.py --json
#   ⇒ rc=0 ; MECH/hinge_power_calc.json 的 md5 = b7c3256f39804f748aea779971944e63
#     (★与 ISS-229 交卷单 L322 记录的 md5 逐字相同 ⇒ 复算幂等, 未改口径★)

# ── §2 board 域实读 (★Q2-丙 的机器依据★)
python3 - <<'PY'
import csv
r=list(csv.DictReader(open('HW/netlist_v1.csv')))
for x in r:
    if x.get('ref') in ('U_CHG','R_ILIM'):
        print(x.get('ref'),'| board=',x.get('board'),'| dnp=',x.get('dnp'))
PY
#   ⇒ U_CHG / R_ILIM 的 board 全是 CHG_BOARD (共 12 行) ; MAIN_PCB 0 行

# ── §3 本单新闸 (★新建·零挂链★)
python3 SW/check_evt_charge_current_criterion.py
#   ⇒ rc=0 (pre 相) + 逐条点名 4 条既存缺陷 (K3/K4/K5b/K9)
python3 SW/check_evt_charge_current_criterion.py --phase post
#   ⇒ rc=1 (改判据那一趟的验收相, 今天必红) + 点名「永远判不过」
python3 SW/check_evt_charge_current_criterion.py --strict
#   ⇒ rc=1 (既存缺陷也当红)
python3 SW/check_evt_charge_current_criterion.py --selftest
#   ⇒ rc=0 ; 反向用例 20/20 通过 ; 末行 ALL TESTS PASS

# ── §4 零挂链 + 边界自证
grep -c check_evt_charge_current_criterion state/gate_check.py     # ⇒ 0
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv \
       HW/BOM_v1.csv SW/EVT_TEMPLATE.md SW/tools/s2_board_judge.py SW/tools/s2_board_selftest.py
stat -c '%n %s %y' HW/PCB/demo_mainboard.kicad_pcb
#   ⇒ 板 611b869e13518c3c023fb178f91a0075 / 4940213 / 2026-11-06 07:07:17.362193413 (三项前后逐字相同)
#   ⇒ 网表 6aee500e… / 脚表 9174309d… / BOM 5b999399… / EVT 773dcaf7… (前后逐字相同)
#   ⇒ 既有闸 38bf8a62… / 9fb6c7a0… (前后逐字相同)

# ── §5 既有闸基线 (★判据基线用 --selftest 那条; 不带 --selftest 跑它 rc=3 是它自己要参数, 不是本单的锅★)
python3 SW/tools/s2_board_judge.py --selftest    # ⇒ rc=0 (基线, 前后逐字相同)
python3 SW/tools/s2_board_selftest.py           # ⇒ rc=2 (基线, 前后逐字相同)

# ── §6 项目门禁 (★交卷前必跑★)
python3 state/merge.py                          # ⇒ rc=0
python3 state/gate_check.py                     # ⇒ rc=0 (Q1 18/18)
python3 state/check_brief_commands.py --brief-file state/dispatch_briefs/ISS-385_sw_evt_charge_current_criterion.md   # ⇒ rc=0
```

★**★边界自证 (★证据等级: 本段 = `[实测]` · ★开工前后两次 md5 对照, 结果逐条贴出 ★)★★**

| 边界 | 自证方式 | 结果 |
|---|---|---|
| ★零写板★ | 板 md5 / mtime / size 三项, 开工前后各打一次 (`logs/iss385/boundary_proof.txt`) | ★**逐字相同** (`611b869e…` / `2026-11-06 07:07:17.362193413` / `4940213`) ★ |
| ★零落表★ | 网表 / 脚表 / BOM 三件 md5 前后对照 | ★**逐字相同** (`6aee500e…` / `9174309d…` / `5b999399…`) ★ |
| ★零改既有页面正文★ | `SW/EVT_TEMPLATE.md` md5 前后对照 (★+ 闸 K8 运行前后自证★) | ★**逐字相同** (`773dcaf7432b66397a1fa3240c32c3ad`) ⇒ ★**正文一个字都没改** ★ |
| ★零改既有闸★ | `s2_board_judge.py` / `s2_board_selftest.py` md5 前后对照 | ★**逐字相同** (`38bf8a62…` / `9fb6c7a0…`) ★ |
| ★零写 MECH/HW 地界★ | `MECH/hinge_power_calc.json` md5 对照 (★**只被 §6 第一条命令【按任务书指定的复算命令】重新生成过, 内容 md5 与 ISS-229 基线逐字相同 ⇒ 幂等; `HW/netlist_v1.csv` 只读** ★) | ★**内容逐字相同** (`b7c3256f…` = ISS-229 交卷单 L322 记录值) ★ |
| ★零挂链★ | `grep -c check_evt_charge_current_criterion state/gate_check.py` | ★**0** ★ |
| ★零外发★ | 本单**未发出任何邮件 / 询价 / 问询 / 采购**; 厂商资料一律自己查 + 标证据等级 | ★**零外发** ★ |
| ★不自签 issue_log / 不写别人的分片★ | `state/issue_log.yaml` mtime `2026-11-24 08:27:30` (★早于本单任何写入★) · 分片只写 `state/fragments/sw.yaml` (走 `state/frag_write.py --agent sw-lead` ⇒ 工具按 `FILE_OF` 强制映射, 物理上写不到别人分片) · ★**`hw.yaml`/`mech.yaml` 交卷期间 md5 有变 = 别的总工并发写 (hw-lead `updated_by: hw-lead` / mech-lead), 不是本单写的** ★ | ★**合规** ★ |
| ★沙盒只落 tmp/iss385_sbx/ + logs/iss385/★ | 未写系统 `/tmp`; 未用 `cp -al` 造副本 (★L-24 硬规矩★) | ★**合规** ★ |

---

> ★**证据等级约定**: `[实测]` = 本机实跑读数 · `[官网]`/`[官方]` = 厂商官网 / 官方 datasheet · `[推算]` = 由实测/官方推导 · `[媒体]` = 第三方报道 (本单零条) · `[0数据]` = 查不到 / 板端还测不了
> ★**本页不含任何未标等级的断言**
> ★**★本单不代拍: 「PWR-05 最终改成哪一条」是 main/老板的地界; 本单只交【真相页 + 机器闸 + 三个候选及代价】★**
