# HW/POWER_RAIL_SPEC.md —— demo 主板 电源轨需求表（★H3-04 必选槽位）

> ★**为什么现在建这张表**: 2026-11-03 一天里, 三次"电源算错了"的问题都是这张表该管的
> (① 背光 2.6W 撑爆 USB-C 900mA 预算 ② 相机模组自带稳压 ⇒ 主板白砍 3 颗 LDO
> ③ SoM 自带 PMIC ⇒ 主板白砍 2 颗 DC-DC + 5 个时序件) ⇒ ★**槽位缺一项, 就会重复犯**。
> 判据来源: `~/.openclaw/workspace/skills/smart-hardware-reference/references/structure-requirements.md`
> **H3-04 电源设计方案** 的必选组件: 电源输入规格 / 各轨电压电流需求 / LDO·DC-DC 选型 / 纹波噪声指标 / 启动时序 / 掉电保护。
> ★**状态**: v0.1（2026-11-03）· 输入侧与 SoM 侧已定量, 背光侧待实测, 整机阶段另立版本。

## 1. 电源输入规格（槽位: 电源输入规格）

| 项 | 值 | 依据 |
|---|---|---|
| 入口 | **USB-C (Type-C 受电端 UFP)**, `J_USB_C` | 老板 2026-11-03 09:54: "没有整机, 没有镜脚, demo/主板用 type-c 供电" |
| 输入电压 | **5.0 V ±5%** (USB VBUS) | USB 2.0/3.0 Type-C |
| ★**默认电流上限** | **900 mA** (CC1/CC2 各 5.1k 下拉 ⇒ 默认档) | USB Type-C 规范: Rd 5.1k ⇒ 900 mA/1.5 A/3.0 A 由源端 advertise 决定, 我们作为 UFP 只给 Rd |
| ⇒ **可用总功率** | **5 V × 0.9 A = 4.5 W** | ★**这是硬天花板** (见 §5 预算) |
| 反灌保护 | ★**U_EN_SW (TPS22991RAA) 无反向阻断 (RCB)** ⇒ 主板 5V 轨在关机/掉电时可能被反灌 | ISS-172 待裁: 若要 RCB 改 TPS22916/17 (RON 60~90mΩ) |
| 电池 | ★**demo 不装电池** (电池 + 保护 IC + MOS 全 DNP) | 老板 09:54; ISS-169 |
| 充电链 | ★**demo 不上充电链** (U_CHG 那套在 CHG_BOARD ⇒ 不进这块板) | 老板 09:54 |

## 2. 各轨电压/电流需求（槽位: 各轨电压电流需求）★核心表

| 轨 | 电压 | 电流需求 (估) | 负载 | 来源 | 状态 |
|---|---|---|---|---|---|
| `RAIL_USB_5V` | 5.0 V | **见 §5 预算** | Type-C VBUS → ESD → π 滤波 | USB-C | 已定 |
| `RAIL_BOARD_5V` | 5.0 V | ≈ 0.6 A | 底板各路（经 `U_EN_SW` 门控） | `U_EN_SW` (TPS22991RAA) | ★由 **SoM 的 CARRIER_BOARD_EN (P3_87)** 放行 |
| `RAIL_SOM_DCIN` | 5.0 V | SoM 自身 (原厂口径 670 mW ⇒ ≈0.14 A) | FET3572-C 的 VCC_DCIN **7 脚并联** (P3_91/93/95/97/98/99/100) | `RAIL_USB_5V` **直供** | ★**不受 U_EN_SW 门控**（否则 SoM 起不来） |
| `VDD_3V3_IO` | 3.3 V | ≈ 0.2 A | I2C 上拉 / 相机模组 VCC3.3V / 屏 VDD | `U_LDO_IO33` (TPS7A20-33, X2SON) | 必装 |
| `VDD_1V8_IO` | 1.8 V | ≈ 0.1 A | 屏 VCCIO / 相机 SCCB 上拉 | `U_LDO_IO18` (TPS7A20-18, X2SON) | 必装 |
| `LIGHT_3V3` | 3.3 V | **0.2 A** (预算上调) | 屏模组 VDD (含屏内背光电流) | `U_LDO_L33` (TPS7A20-33) | 必装 |
| `LIGHT_1V8` | 1.8 V | — | 屏模组 I/O 域（8HD 的 VCCIO 可 1.8~3.3V） | `U_LDO_L18` | ★**DNP**（demo 取 3.3V） |
| `SENSOR_AVDD / VDD_IO / CORE` | 2.8/1.8/1.2 V | — | ~~传感器芯片级轨~~ | ~~3 颗 TPS7A20~~ | ★**DNP —— 相机模组自带稳压**（见 `HW/PCB/SOM_BUILTIN_CAPABILITY.md` B1） |
| `V_CORE / V_SOC_IO` | — | — | ~~SoC 核心/IO 轨~~ | ~~2 颗 TPS62130A~~ | ★**DNP —— SoM 自带 PMIC**（A1） |
| ~~背光 BOOST~~ | — | — | ~~屏背光~~ | — | ★**已取消 (2026-11-04)**: demo 屏改 **Waveshare 2.8"** (15 针表里**无独立背光脚** ⇒ 背光由模组内从 3.3V 取) ⇒ **12V BOOST + 恒流 + PWM 整链不需要** |

### 2.1 ★ 选型登记（H3-04 槽位: LDO/DC-DC 选型）

| 轨 | 器件 | 封装 | 脚号（★已按原厂 datasheet 落定） | OPN |
|---|---|---|---|---|
| `VDD_3V3_IO` | TPS7A2033DQNR | X2SON / DQN0004A | **1=OUT · 2=GND · 3=EN · 4=IN · 5=散热焊盘(→GND)** | TPS7A2033DQNR |
| `VDD_1V8_IO` | TPS7A2018DQNR | X2SON / DQN0004A | 同上 | TPS7A2018DQNR |
| `LIGHT_3V3` | TPS7A2033DQNR | X2SON / DQN0004A | 同上 | TPS7A2033DQNR |
| `RAIL_BOARD_5V` | **TPS22991RAA** (负载开关) | UQFN-4 RAA 0.85×0.75 mm | **1=VIN · 2=ON · 3=VOUT · 4=GND** | TPS22991RAA |
| ★`RAIL_SOM_DCIN` | 直连 5V（7 脚并联） | — | — | — |
| ~~背光 BOOST~~ | **不需要**（demo 屏 Waveshare 2.8" 无独立背光脚 ⇒ 背光由模组内 MCU 从 3.3V 取；原参考 Dragon Q6A 的 SY7203DBC 方案作废） | — | — | ★**已取消** |

> ★**X2SON 的散热焊盘 (pin5) 必须接 GND** —— 这是原厂要求（既是散热通路也是 GND 回路）；
> ★**我们 12:5x 才发现网表里把 LDO 的 GND 脚整个漏了** ⇒ 现在已补（pin2 + pin5 都接 GND）。

## 3. 启动时序（槽位: 启动时序）★H3-04 必选，今天之前我们**没有这张表**

| 序 | 事件 | 条件 | 谁保证 |
|---|---|---|---|
| ① | USB-C 5 V 上电（VBUS 检测进 SoM 的 `USB_DRD1_VBUSDET`） | — | Type-C |
| ② | SoM 自身 VCC_DCIN (5V) 上电 ⇒ SoM 内部 PMIC 启动 ⇒ SoM 起来 | ① | **直供，不受门控** |
| ③ | SoM 拉高 `CARRIER_BOARD_EN` (P3_87) ⇒ 放行底板 | ② | ★Forlinx 原文: 底板早于核心板上电 ⇒ 电流过大/无法启动/**可能损坏处理器** ⇒ 门控**必需** |
| ④ | `RAIL_BOARD_5V` → 3 LDO 起来 → `VDD_3V3_IO` / `VDD_1V8_IO` / `LIGHT_3V3` | ③ | LDO 的 EN 直连 `RAIL_BOARD_5V`（datasheet 门限 VEN(LOW)≤0.3 V 关断 / VEN(HIGH)≥0.9 V 使能 ⇒ 5 V 安全） |
| ⑤ | 相机模组 3.3V/5V、屏模组 3.3V/1.8V 到位 | ④ | 相机模组自带稳压 ⇒ 内部顺序由模组保证 |
| ⑥ | ~~背光 BOOST~~ | — | ★**已取消** (demo 屏无背光脚 ⇒ 背光由模组内 MCU 管 ⇒ 我们只需给 3.3V) |
| ⑦ | SoM 复位释放 (`RESET_L` P2_100) | ② 之后 | 现在 = 10k 上拉 + 1k/100nF RC + 按键（**U_SUPV 已 DNP**：SoM 自带 PMIC 复位 ⇒ 官方载板也没有监督器） |

> ★**我们曾经缺这张表的代价**（今天都踩到了）: ① LDO 的 EN 悬空 ⇒ 整板不上电（EN 内部 500 kΩ 下拉）② 相机三轨上电顺序（DVDD→OVDD→AVDD）没管 ③ 背光与 SoM 的先后没定。

## 4. 掉电/异常保护（槽位: 掉电保护）

| 项 | 现状 | 风险 / 待办 |
|---|---|---|
| SoM 侧 | `CARRIER_BOARD_EN` 由 SoM 拉低 ⇒ 底板断电 | OK |
| 反向阻断 | ★**U_EN_SW 无 RCB** | ★关机/掉电时 5V 轨可能被反灌 ⇒ ISS-172 待裁 |
| 相机模组 | 自带稳压 + 模组级 3.3V/5V | OK |
| ~~背光 BOOST~~ | — | ★**已取消** (屏无独立背光脚) |
| 过流/短路 | ★**无** | 3.3V/5V 支路未加保险丝/限流 ⇒ 待评估 |

## 5. ★功率预算（USB-C 900 mA 硬上限 vs 实际需求）

| 负载 | 估功率 | 备注 |
|---|---|---|
| SoM (FET3572-C) | **0.67 W** (原厂 670 mW @5V ⇒ 0.134 A) | RK3572 原厂口径 |
| **3 颗 LDO 输出** (3.3V/1.8V/3.3V) | ≈ 0.6 W | 相机 3.3V+5V / 屏 3.3V+1.8V / I2C 上拉 |
| 相机模组 5V | ≈ 0.75 W | 模组级电流**未查** (保守估) |
| **屏 (Waveshare 2.8") 3.3V** | **≈ 0.35 W** | 推断 70~125mA@3.3V (含背光, 官方未公布) |
| 杂项 (I2C 上拉 / LED / 按键 / ESD) | ≈ 0.1 W | |
| **合计** | **≈ 2.5 W** | ★**远低于 5 V×0.9 A = 4.5 W 的天花板** ⇒ ★**USB-C 预算宽裕, 不用换 3A advertise 方案** |

⇒ ★**结论 (2026-11-04 更新)**: ★**demo 屏换 Waveshare 2.8" 之后, 预算从 4.6W 降到 ≈2.5W ⇒ USB-C 900mA 完全够用** ⇒
① 原先"12V BOOST + 3A advertise"的两个大动作**都不需要了** ⇒ 板子省一颗 BOOST + 4.7µH + 采样电阻 + 面积 ⇒
② ★**整机更没有这个问题**: 整机屏是视崖 0.49" **SiOLED 自发光 ⇒ 整机本来就没有背光** ⇒ 这条只是 demo 阶段的中间账。

## 6. 纹波/噪声（槽位: 纹波噪声指标）★当前只有定性结论

| 轨 | 指标 | 来源 |
|---|---|---|
| `VDD_1V8_IO` | 走 I2C + 屏 I/O 域 | ★**TPS7A20 有 7 µVrms / PSRR 60 dB 规格** ⇒ 相机模组自带稳压时用不到 |
| 相机 SCCB 上拉 | ★**必须上拉到 1.8 V**（RK3572 的 I2C5 是 1.8 V 域；模组 FPC 上就标 I2C5） | ★**旧网表拉到 3.3V ⇒ 会把 SoM 的 1.8 V 脚灌 3.3V ⇒ 已改** |
| 屏触控 I2C | 1.8 V 域 vs 触控 3.3 V | ★**触控不要了 ⇒ 不用管**（老板 09:29） |
| `LIGHT_3V3` / `VDD_3V3_IO` | 纹波未量化 | 待板测 |

## 7. 关联

- 能力清单（模块内置 ⇒ 不重复做）: `HW/PCB/SOM_BUILTIN_CAPABILITY.md`
- 器件封装/脚号: `HW/PCB/PINOUT_FOOTPRINT_SPEC.md` + `HW/PCB/pinout_footprint.json`
- 电源门控 (F13): `HW/PCB/SOM_PIN_ASSIGNMENT.md`
- 未闭环: ISS-169 / ISS-170 / ISS-172 / ISS-173
