# HW/CHARGE_BOARD_SPEC.md —— 充电板 (镜框) 器件级连接规格

> **文档性质**: 规格 (**只描述连接关系 / 取值 / 证据**), **不含网表改动**。
> **本单不碰**: `state/gen_netlist.py` · `HW/netlist_v1.csv` · `HW/SCHEMATIC_V1.md` · `HW/BOM_v1.csv` (生成物, 唯一真源是生成器, 由项目总工改)。
> **本单不碰**: `state/` 下任何文件 · `state/fragments/` · `MECH/` · `SW/` · `PROJECT_TRACKER.md` · `DECISIONS.md`。
> **起草**: hw-lead (器件级规格) · 2026-10-27 · **待项目总工审校 → 落 P10 页**。

---

## 0. 板级定位与边界

| 项 | 结论 | 证据 |
|---|---|---|
| 充电板位置 | **镜框** (ISS-014 决策 5 + V1.2 裁决) | `HW/SCHEMATIC_V1.md` P1 §V1.2 |
| 充电板尺寸 | **25 × 10 × 0.8 mm** | [推算] `MECH/MECH_BUDGET.md` §1.3 M3 |
| 充电板固定 | 1×M1.2 螺钉 + 铝屏蔽罩贴合 Type-C | [推算] 同上 |
| **本板装的件** | Type-C 16p 母座 · ESD 阵列 · π 滤波 (磁珠+10µF+100µF) · BQ25896 + 全部外围 · CC Rd ×2 · VBUS_DET 分压 · 跨铰链连接器 (`J_CHG`) 一侧 | 本规格 §1-§5 |
| **不在本板的件 (明确排除)** | 电池 · 电池保护 IC **BQ2970** · 2× 外置 N-MOS · 电池 NTC + TS 下臂 · SoC · 全部 DC-DC / LDO · 电池保护与 MOS 走线 | `HW/SCHEMATIC_V1.md` P1 §V1.2 (电池 + 保护在镜脚) |
| 充电板上的逻辑电源 | **无 3.3V 轨** —— 只有 VBUS (5V) 和 BQ25896 内部 REGN (5V)。任何需要 3.3V 的器件 (如 TPS25730 的 VIN_3V3) 必须额外造 3.3V | [官方] BQ25896 datasheet §8.5 (REGN = 5V) |

> ★**本规格的一条硬前提**: 充电板**没有 3.3V 逻辑电源**。所有跨铰链开漏信号 (CHG_STAT / PWR_GOOD) 的上拉电阻**必须放主板侧** (3.3V), 充电板侧只输出开漏。

---

## 1. Type-C 16p 母座 —— 完整物理脚位

### 1.1 选型口径

| 项 | 取值 | 证据 |
|---|---|---|
| 类型 | 16P 母座, 沉板 (through-hole barrel), 4 脚插板 | [官方·厂商页] `HW/POWER_IC_SELECTION.md` §3.5 (航宏 hhswitch.com/type16p) |
| 本体尺寸 | 8.94 × 6.5 × 3.16 mm | [官方·厂商页] 同上 |
| 沉板深度 | 0.8 / 1.0 / 1.6 / 2.10 mm 四种 → **由结构总工按镜框端件壁厚选** | [官方·厂商页] 同上 |
| 面板开孔 | **9.5 × 3.6 mm** | [官方·结构] `MECH/USB_HINGE_STRUCTURE.md` §5.2 F-5 + `MECH_BUDGET.md` §5.1 |
| 寿命 | 10000 次 | [官方·厂商页] |
| **具体型号 / 焊盘图** | **待选型** —— 厂商页无型号级数据, 需询价 (**外发一律经项目总工**) | [0数据] |

### 1.2 ★完整物理脚位表 (USB-IF A/B 编号, 24 个位置全列)

> 依据: **USB Type-C Cable and Connector Specification, Release 2.0 (2019-08)** §Table 3-5 "USB Type-C Receptacle Interface Pin Assignments for USB 2.0-only Support" —— **usb.org 官方 PDF, 已下载核过**。
> ★**本板用物理 A/B 脚位, 不用网表自拟的逻辑编号** (MECH §5.3 C-2 明确要求: "PCB 焊盘必须按器件数据手册的物理 A/B 脚位画")。

| # | 物理脚位 | 名称 | 16p 母座是否有此触点 | **本板去向** | 值 / 要求 | 证据 | 备注 |
|---|---|---|---|---|---|---|---|
| 1 | **A1** | GND | ✅ | `GND` (数字地/回流) | 4 脚 GND 并联 | [官方] Table 3-5 | |
| 2 | A2 | TX1+ | ❌ 16p 无此触点 | **NC (无焊盘)** | — | [官方] Table 3-5 | 24p 才有 |
| 3 | A3 | TX1− | ❌ 16p 无此触点 | **NC (无焊盘)** | — | [官方] Table 3-5 | 24p 才有 |
| 4 | **A4** | VBUS | ✅ | `USB_VBUS_RAW` | 5V | [官方] Table 3-5 | 4 个 VBUS 脚 (A4/A9/B4/B9) 座内并联 |
| 5 | **A5** | CC1 | ✅ | `USB_CC1` → `R_CC1` 5.1k → GND | Rd = 5.1kΩ ±20% | [官方] Table 3-5 + §4.x | |
| 6 | **A6** | D+ (Dp1) | ✅ | `USB_D_P_CHG` (与 B6 并联) | 90Ω 差分; 并联走线 **≤3.5mm** | [官方] Table 3-5 Note 2 | |
| 7 | **A7** | D− (Dn1) | ✅ | `USB_D_N_CHG` (与 B7 并联) | 90Ω 差分; 并联走线 **≤3.5mm** | [官方] Table 3-5 Note 2 | |
| 8 | **A8** | SBU1 | ✅ | **不接 (NC)** | "shall be not connected unless required" | [官方] Table 3-5 Note 3 | 本机不做 Alt Mode |
| 9 | **A9** | VBUS | ✅ | `USB_VBUS_RAW` | 5V | [官方] Table 3-5 | |
| 10 | A10 | RX2− | ❌ 16p 无此触点 | **NC (无焊盘)** | — | [官方] Table 3-5 | 24p 才有 |
| 11 | A11 | RX2+ | ❌ 16p 无此触点 | **NC (无焊盘)** | — | [官方] Table 3-5 | 24p 才有 |
| 12 | **A12** | GND | ✅ | `GND` | — | [官方] Table 3-5 | |
| 13 | **B1** | GND | ✅ | `GND` | — | [官方] Table 3-5 | ★**当前网表漏了 B1/B12** |
| 14 | B2 | TX2+ | ❌ 16p 无此触点 | **NC (无焊盘)** | — | [官方] Table 3-5 | 24p 才有 |
| 15 | B3 | TX2− | ❌ 16p 无此触点 | **NC (无焊盘)** | — | [官方] Table 3-5 | 24p 才有 |
| 16 | **B4** | VBUS | ✅ | `USB_VBUS_RAW` | 5V | [官方] Table 3-5 | |
| 17 | **B5** | CC2 | ✅ | `USB_CC2` → `R_CC2` 5.1k → GND | Rd = 5.1kΩ ±20% | [官方] Table 3-5 | |
| 18 | **B6** | D+ (Dp2) | ✅ | `USB_D_P_CHG` (与 A6 并联) | ≤3.5mm | [官方] Table 3-5 Note 2 | ★双份并联, 否则插头翻面不通 |
| 19 | **B7** | D− (Dn2) | ✅ | `USB_D_N_CHG` (与 A7 并联) | ≤3.5mm | [官方] Table 3-5 Note 2 | ★双份并联 |
| 20 | **B8** | SBU2 | ✅ | **不接 (NC)** | — | [官方] Table 3-5 Note 3 | |
| 21 | **B9** | VBUS | ✅ | `USB_VBUS_RAW` | 5V | [官方] Table 3-5 | |
| 22 | B10 | RX2− | ❌ 16p 无此触点 | **NC (无焊盘)** | — | [官方] Table 3-5 | 24p 才有 |
| 23 | B11 | RX2+ | ❌ 16p 无此触点 | **NC (无焊盘)** | — | [官方] Table 3-5 | 24p 才有 |
| 24 | **B12** | GND | ✅ | `GND` | — | [官方] Table 3-5 | ★**当前网表漏了 B1/B12** |
| — | **屏蔽壳 (shell)** | — | ✅ | `GND` **单点接** | 与机壳地的接法待结构定 (ISS-065) | [官方] + [推算] | 不用细线连壳, 用短粗铜皮 |

**脚位计数对账 (门禁用)**:
- 16p 母座实际触点 = **16** (A1/A4/A5/A6/A7/A8/A9/A12/B1/B4/B5/B6/B7/B8/B9/B12)
- 其中**接了** = 14 (VBUS×4 + GND×4 + CC×2 + D+×2 + D−×2)
- 其中**不接** = 2 (SBU1 A8 / SBU2 B8)
- 另有 8 个 A/B 位置在 16p 母座上**物理不存在** (A2/A3/A10/A11/B2/B3/B10/B11) → PCB 焊盘图**不得**在这些位置放盘
- ★**当前网表引用数 = 12** (只有 A4+A9+B4+B9 / A1+A12 / A5 / B5 / A6+B6 / A7+B7), **比声明的 16 少 4** (漏 B1、B12 两个 GND + A8、B8 两个 SBU 未列) → **P10 落网表时必须补齐到 16**

### 1.3 Type-C 侧硬规则

| 规则 | 值 | 证据 |
|---|---|---|
| D+/D− 双份并联走线长度 | **≤3.5 mm** (A6↔B6, A7↔B7) | [官方] USB-IF Spec R2.0 Table 3-5 Note 2: "The maximum shorting trace length should not exceed 3.5 mm" |
| VBUS 4 脚 | A4/A9/B4/B9 **全部并联**, 不得只接 2 个 | [官方] 同上 Table 3-5 |
| GND 4 脚 | A1/A12/B1/B12 **全部并联** | [官方] 同上 Table 3-5 |
| 未用触点 | "shall be electrically isolated from power, ground or signaling (i.e., not connected)" | [官方] Table 3-5 Note 1 |
| SBU | A8/B8 **不接** | [官方] Table 3-5 Note 3 |
| 座→ESD 走线 | **≤3.0 mm**, ESD 装**充电板**侧 (不上 FPC) | [推算] `MECH/USB_HINGE_STRUCTURE.md` §5.2 E-1 + §8 规则 ④ |
| USB 2.0 差分阻抗 | **90Ω ±10%** (不是 100Ω) | [官方] 规格 B-21/B-22 (沿用 P6 口径) |

---

## 2. BQ25896 全电路

### 2.1 器件与总览

| 项 | 取值 | 证据 |
|---|---|---|
| 型号 | **TI BQ25896** | [官方] ti.com/lit/ds/symlink/bq25896.pdf (已下载核过) |
| 拓扑 | 开关型 buck, 1S 锂电 | [官方] |
| 封装 | VQFN-16 (RGT) **3×3 mm**, 带散热焊盘 | [官方] §7 Pin Configuration |
| 充电电流 | 最高 3.008A (可编程); **我们用硬件封顶 ≤1.30A 输入 / ~1.0A 充电** | [官方] REG04 |
| 内部 BATFET | 11 mΩ | [官方] |
| I2C 从机地址 | **0x6B** (1101011B) | [官方] §9.2.16.5 + "I2C Address 6BH" |
| 开关频率 | 1.5 MHz (typ) | [官方] |
| REGN | 内部 LDO **5.0V** (4.8-5.5V), 限流 50mA | [官方] §8.5 |
| 单价 / 交期 | **[0数据]** → 询价走项目总工 | — |

### 2.2 ★BQ25896 24 脚逐脚连接规格

> 引脚图 (Top View) 已按 datasheet 第 5 页图片逐字核对: 1 VBUS / 2 PSEL / 3 PG / 4 STAT / 5 SCL / 6 SDA / 7 INT / 8 OTG / 9 CE / 10 ILIM / 11 TS / 12 QON / 13-14 BAT / 15-16 SYS / 17-18 PGND / 19-20 SW / 21 BTST / 22 REGN / 23 PMID / 24 NC。

| pin | 名称 | 类型 | **本板连接** | 值 / 取法 | 证据 | 备注 |
|---|---|---|---|---|---|---|
| **1** | VBUS | P | `VBUS_5V_CHG` (π 滤波后级) + `C_VBUS_IC` 1µF → PGND | 3.9-14V 输入 | [官方] "Place a 1-µF ceramic capacitor from VBUS to PGND and place it as close as possible to IC" | 内部带 RBFET 反灌保护 |
| **2** | PSEL | DI | `R_PSEL` 10k → PGND (**拉低 = 适配器/DCP**) | 低 | [官方] "High indicates a USB host source and Low indicates an adapter source" | 本机无 USB PHY 主机 → **必须拉低**; 输入源检测后 IINLIM 自动切 3.25A, 实际由 ILIM 电阻封顶 |
| **3** | PG | DO | → `J_CHG pin7` → 主板侧 `R_PU_PG` 10k → 3.3V | 开漏 | [官方] "Connect to the pull up rail via 10-kΩ resistor. LOW indicates a good input source" | **上拉在主板侧** (充电板无 3.3V) |
| **4** | STAT | DO | → `J_CHG pin6` → 主板侧 `R_PU_CHG_STAT` 10k → 3.3V | 开漏 | [官方] "LOW indicates charge in progress. HIGH indicates charge complete or charge disabled. When any fault condition occurs, STAT pin blinks in 1 Hz" | **上拉在主板侧** |
| **5** | SCL | DIO | `J_CHG pin9` (预留, DNP) | 400kHz | [官方] "Connect SCL to the logic rail through a 10-kΩ resistor" | 上拉**只**放主板侧 4.7k→3.3V; 见 §2.8 |
| **6** | SDA | DIO | `J_CHG pin10` (预留, DNP) | 400kHz | [官方] 同上 | 同上 |
| **7** | INT | DO | **不跨铰链**; 本板留 `R_PU_INT` 位 (DNP) | 开漏 256µs 脉冲 | [官方] "The INT pin sends active low, 256-µs pulse to host" | J_CHG 无余量; 状态靠 STAT+PG |
| **8** | OTG | DI | `R_OTG` 10k → PGND (**拉低 = 关 boost**) | 低 | [官方] "The boost mode is activated when OTG_CONFIG = 1, OTG pin is high..." | 本机不做 OTG |
| **9** | CE | DI | `R_CE` 10k → PGND (**拉低 = 允许充电**) | 低 | [官方] "CE pin must be pulled High or Low" | **不能悬空**; 拉低的好处 = SoC 死机也能充电 |
| **10** | ILIM | AI | `R_ILIM` → PGND | **390Ω ±1% (0402)** | [官方] "IINMAX = KILIM/RILIM", KILIM = 320/355/390 AΩ | 见 §2.4; ILIM 脚被稳在 **0.8V**, 电阻功耗 = 0.8²/R ≈ 2.1mW |
| **11** | TS | AI | `R_TS1` 5.24k ← REGN_5V; TS 网**跨铰链** → 镜脚 `R_TS2` 30.31k ∥ `R_NTC_BAT` 10k(103AT) → GND | 见 §2.5 | [官方] + [推算-可复算] | 硬件级电池过温/欠温停充 (不依赖 SoC) |
| **12** | QON | DI | **NC** (内部上拉) | — | [官方] "The pin contains an internal pull-up to maintain default high logic" | SYS 在镜脚, 按键功能放镜脚侧; 本板留焊盘不装 |
| **13,14** | BAT | P | `BAT_CHG` → `C_BAT` 10µF → PGND → `J_CHG pin1/pin2` (双 pin 并联) → 镜脚 BQ2970 → 电池 | 充电 1.0-1.5A | [官方] "Connect a 10uF closely to the BAT pin" | **跨铰链载流路径起点**; 见 §5 |
| **15,16** | SYS | P | **本板不用** (SYS 在镜脚由 BQ2970 产生); 留 `C_SYS` 20µF 位 (DNP) | — | [官方] "Connect a 20uF closely to the SYS pin" | ★见 §2.6 的说明与风险 |
| **17,18** | PGND | P | 功率地平面 (开关节点地), 散热焊盘过孔星接 | — | [官方] "connect directly to the PGND ... A single point connection is recommended between power PGND and the analog GND near the IC PGND pin" | 高电流回流 |
| **19,20** | SW | P | `L_CHG` 2.2µH 另一端 (开关节点) | — | [官方] "Connect the 0.047µF bootstrap capacitor from SW to BTST" | 铜箔面积最小化 |
| **21** | BTST | P | `C_BST` 47nF → SW | 0.047µF | [官方] 同上 | 自举 |
| **22** | REGN | P | `C_REGN` 4.7µF 10V → GND; 同时是 TS 分压基准 | 5.0V | [官方] "Connect a 4.7 µF (10 V rating) ceramic capacitor from REGN to analog GND" | |
| **23** | PMID | DO | `L_CHG` 2.2µH 一端 + `C_PMID` 10µF → PGND | — | [官方] "put 1µF on VBUS to PGND, and the rest capacitance on PMID to PGND" | |
| **24** | NC | — | **NC** | — | [官方] "No Connect" | |
| — | **PowerPAD** | P | 焊到 PGND 平面, ≥6 个过孔 | — | [官方] "Always solder PowerPAD Pad to the board, and have vias on the PowerPAD plane star-connecting to PGND" | 散热焊盘是 3×3mm 器件在 25×10mm 小板上的唯一散热路径 |

### 2.3 输入去耦与电感 (照 datasheet 原话)

| 位号 | 值 | 连接 | 证据 |
|---|---|---|---|
| `C_VBUS_IC` | 1µF X7R 25V | pin1 (VBUS) → PGND, **紧贴 IC** | [官方] pin1 说明 |
| `C_PMID` | 10µF X7R 25V | pin23 (PMID) → PGND | [官方] "the rest capacitance on PMID to PGND"; 8.2µF 建议值对应 3-5A 充电电流, 本设计 ~1.0A 取 10µF |
| `L_CHG` | 2.2µH, Isat ≥1.5A, DCR ≤50mΩ | PMID ↔ SW | [官方] "To get good loop stability, 1-µH and minimum of 20-µF output capacitor is recommended" + 纹波算式 |
| `C_BST` | 47nF 25V | SW ↔ BTST | [官方] |
| `C_REGN` | 4.7µF 10V | REGN → GND | [官方] |
| `C_BAT` | 10µF X7R 6.3V | BAT → PGND | [官方] pin13/14 说明 |

**纹波复算** (可复现):
```
IRIPPLE = VBUS × D × (1-D) / (fs × L)
  VBUS = 5V, VBAT = 3.7V → D = 0.74, fs = 1.5MHz, L = 2.2µH
  IRIPPLE = 5 × 0.74 × 0.26 / (1.5e6 × 2.2e-6) = 0.962 / 3.30 = 0.29 A
  → 29% of ICHG=1.0A  ⇒ 落在 datasheet 建议的 20-40% 区间 ✔
  (若取 1µH: IRIPPLE = 0.962/1.5 = 0.64A = 64% ⇒ 偏大, 不取)
IBAT_peak = ICHG + IRIPPLE/2 = 1.0 + 0.145 = 1.15A ⇒ Isat 选 ≥1.5A
```

### 2.4 ★输入电流硬上限: `R_ILIM` (本单最重要的一颗电阻)

**BQ25896 的 ILIM 脚不是串在功率路径上** —— 它是一个被稳在 **0.8V** 的电压节点, 电阻从 ILIM 到地, 设定输入电流上限:

```
IINMAX = KILIM / RILIM          (KILIM = 320 / 355 / 390 AΩ, min/typ/max)
实际输入电流上限 = min(ILIM 脚设定, IINLIM 寄存器设定)   ← datasheet 原文
```

| `R_ILIM` | IINMAX (min/typ/max) | CC 段电池电流上限 (×Vbat/Vbus/η ≈ 0.822) | 铰链段实际载流 | 用途 |
|---|---|---|---|---|
| **390Ω ±1%** | 0.82 / 0.91 / **1.00 A** | 0.67 / 0.75 / **0.82 A** | **~0.75 A** | ★★**本规格推荐值** (V1.9, 老板 10-28 拍板『边戴边充不允许』⇒ 皮肤温度不再是充电时硬约束 ⇒ 充电电流可提速; 单 pin 0.411A ≤ 0.5A 触点天花板, 余量 1.22×) |
| 300Ω ±1% | 1.07 / 1.18 / 1.30 A | 0.88 / 0.97 / 1.07 A | ~1.0 A | ❌ **300Ω 档正式判死** (V1.9): 单 pin 0.534A > 任何 0.5mm pitch FPC ZIF 的 0.5A 触点天花板 (只能靠 1.0mm pitch, 而铰链区装不下) ⇒ **不可选** |
| 260Ω ±1% | 1.23 / 1.37 / 1.50 A | 1.01 / 1.13 / 1.23 A | ~1.1 A | datasheet 官方示例值 (KILIM=390 max 时 1.5A) |

> ★**电阻功耗不是问题**: ILIM 脚被稳在 0.8V → P = 0.8²/390 = **1.64 mW** → 0402 足够 (不需要大功率电阻)。
> ⚠️ **[待原厂]**: datasheet 的 KILIM 规格只在 "IINMAX = 1.5A" 工况点给出 (min/typ/max 320/355/390 AΩ)。**低电流档 (本设计 1.0A) 的 KILIM trim 是否同值, datasheet 原文未给** → 需 TI 确认 (见 §8 待决项 3)。若 KILIM 在低电流档偏大, 实际 IINMAX 会高于上表 → 仍被 1.3A 内的最坏值封住。

### 2.5 ★电池 NTC / TS 分压 (datasheet 原文算法复算)

**BQ25896 的 TS 门限 (占 REGN 的百分比)** [官方 §8.5]:

| 阈值 | 值 (%V(REGN)) | REGN=5V 时 | 对应温度 (103AT) |
|---|---|---|---|
| V(T1) | 73.25% (typ) | 3.663 V | 0°C (冷 → 降流) |
| V(T2) | 68.25% (typ) | 3.413 V | 10°C |
| V(T3) | 44.75% (typ) | 2.238 V | 45°C (暖 → 降压) |
| V(T5) | 34.375% (typ) | 1.719 V | 60°C (过温 → 停充) |

**datasheet Equation 2 的解** (0-60°C 窗口, 103AT):
```
RT1 (REGN→TS)  = 5.24 kΩ     ← datasheet 原文
RT2 (TS→GND)   = 30.31 kΩ    ← datasheet 原文
RTH  = 10 k NTC (103AT = 10k B=3435), 与 RT2 并联
```
**独立复算验证** (本单自算, 可复现):
```
V_TS = VREGN × (RTH ∥ RT2) / (RT1 + (RTH ∥ RT2))
  0°C  : RTH = 27.28k → RTH∥RT2 = 14.358k → V_TS = 5 × 14.358/19.598 = 3.663V = 73.26% ✔ (= V(T1))
  60°C : RTH =  3.02k → RTH∥RT2 =  2.747k → V_TS = 5 ×  2.747/7.987 = 1.720V = 34.40% ✔ (= V(T5))
```

| 位号 | 值 | 装在哪块板 | 连接 | 证据 |
|---|---|---|---|---|
| `R_TS1` | **5.24k ±1%** | **充电板 (镜框)** | REGN_5V → TS_BAT | [官方] Equation 2 |
| `R_TS2` | **30.31k ±1%** | **镜脚主 PCB** | TS_BAT → GND | [官方] Equation 2 |
| `R_NTC_BAT` | **10k NTC B=3435 (103AT)** | **镜脚主 PCB, 贴电芯** | TS_BAT → GND (与 R_TS2 并联) | [官方] "Recommend 103AT-2 thermistor" |

> ★**与当前网表的冲突 (必须改)**: 现行 `HW/netlist_v1.csv` 里 `R_NTC_BAT` 在 **CHG_BOARD** 且接到 `BAT_PROT` (电池保护节点), `R_TS_PULL` 10k → GND。→ **应改为: NTC + 30.31k 下臂在镜脚侧贴电芯; 充电板侧只有 5.24k 上臂 (REGN→TS); TS 网跨铰链**。
> ⚠️ NTC 下臂到底接 GND 还是接电芯负极 (BAT−): datasheet 原文是 "to GND"。本项目 GND 是单点汇流 (`CHG_GND_STAR`), 电芯负极在镜脚与数字地同参考 → **两者等价**; 本规格按 datasheet 取 **GND**, 并把此条列入 §8 待确认项。
> ★**安全性副产品**: 若 TS 跨铰链断开, 充电板侧只有 `R_TS1` → TS 电平 = REGN = 5V = 100% > V(T1) → 芯片判"过冷" → **硬件自动停充** ✔ (符合"电池断开时不充电"的期望)。

### 2.6 ★SYS 脚在本板不用的说明与风险

- 现行架构: **电池 + BQ2970 + 2×MOS 在镜脚**, SYS 在镜脚本地产生 → **BQ25896 的 SYS 脚 (pin15/16) 对外无负载**。
- datasheet 对 SYS 脚的要求是 "Connect a 20uF closely to the SYS pin" —— 该 20µF 是**系统端**体电容 (SYS 是内部 BATFET 的输出端)。
- **本规格处理**: SYS 脚保留 `C_SYS` (20µF) **焊盘位, 默认 DNP**。
  - 理由 1: SYS 节点不接任何负载时, 加 20µF 只是让节点有定义, 不产生功能收益, 却占充电板 (25×10mm) 的面积。
  - 理由 2: **留位不装 = 将来若改回"电池在镜框 + 充电板在镜脚"架构, 只要接 2 根线 + 贴这颗电容即可, 不用改板** (与 ISS-014 可回退分支对齐)。
- ⚠️ **[待原厂]**: "SYS 脚悬空 (不接 20µF) 是否影响 BQ25896 的 BATFET 通路与充电环路" —— datasheet 未明确说明 → 需 TI 确认 (见 §8 待决项 2)。

### 2.7 其它控制脚取值汇总

| 脚 | 接法 | 值 | 理由 | 证据 |
|---|---|---|---|---|
| PSEL (2) | 10k → PGND | 拉低 = 适配器 | 本机无 USB PHY 主机; 拉高会锁 500mA | [官方] |
| CE (9) | 10k → PGND | 拉低 = 允许充电 | "must be pulled High or Low"; 拉低 → SoC 死机仍能充 | [官方] |
| OTG (8) | 10k → PGND | 拉低 = 关 boost | 不做 OTG | [官方] |
| QON (12) | NC | 内部上拉 | 按键功能放镜脚侧 | [官方] |
| PG (3) / STAT (4) | 跨铰链, 主板侧 10k 上拉 3.3V | 开漏 | 充电板无 3.3V | [官方] |
| INT (7) | 不跨铰链, 留位 DNP | 开漏 256µs | J_CHG 无余量; 状态走 STAT+PG | [官方] |
| SCL (5) / SDA (6) | 跨铰链 (预留 pin9/pin10), 主板侧 4.7k 上拉 3.3V | 400kHz | 见 §2.8 | [官方] |

### 2.8 ★★风险 R-1: 复位默认充电电流 = 2048 mA (若不编程 I2C)

| 项 | 值 | 证据 |
|---|---|---|
| REG04 (Fast Charge Current) **复位默认值** | **2048 mA** (0100000), 可编程范围 0-3008 mA | [官方] REG04 Table 10 |
| REG00 (IINLIM) 复位默认值 | 500 mA; 输入源检测后按 PSEL 自动改写 (PSEL=Low → 3.25A) | [官方] REG00 Table 6 |
| **实际输入电流上限** | = min(ILIM 脚设定, IINLIM 寄存器设定) | [官方] §9.2.3.3 |
| **本规格的封顶链** | ILIM 脚 `R_ILIM` = 390Ω → **0.82-1.00A 硬件上限**, 与寄存器无关 | [官方] |

> ⇒ **只要 `R_ILIM` 装上, 就算 SoC 死机、就算 I2C 不跨铰链、就算 ICHG 寄存器停在 2048mA, 充电电流也被硬件压在 ~1.0A** —— 铰链段安全。
> ⇒ **如果 `R_ILIM` 不装 (或被误装成大阻值) 而 ICHG 又停在 2048mA, 铰链会过 2.05A → 超设计点 1.5A 的 1.37 倍** —— 这是本板**唯一一处"一颗电阻兜住一条安全链"**的地方, 门禁里应加"必须有 ILIM 电阻"判据。
> ⇒ **所以 `R_ILIM` 是本规格的第一优先件, `I2C` 是"锦上添花"不是"必须"。**

### 2.9 ★风险 R-2: 与 `INTERFACE_TABLE.md` §4.2 的 I2C 地址冲突

| 项 | 现行记载 | datasheet 实际 | 结论 |
|---|---|---|---|
| BQ25896 的 7-bit I2C 地址 | **0x12** (标注 "[推算] — 需查 datasheet I2C 地址") | **0x6B** (1101011B) | ★**必须改** |
| 与总线 A 现有地址 (0x36 / 0x48 / 0x50 / 0x54 / 0x72 / 0x62) 冲突? | — | 0x6B 不在其中 | ✅ 无冲突 |
| 0x60-0x6F 段 | 0x62 标"预留 (第二个温度计/电量计)" | 0x6B 落在该段内 | ⚠️ 需与 0x62 的预留一起说明 (不冲突, 但同段) |

> ⇒ `HW/INTERFACE_TABLE.md` §4.2 第 (5) 行与 §4.4 地址表要改成 **0x6B (7-bit) / 0xD6 (10-bit)**。**这一条与"要不要跨铰链走 I2C"无关, 无论走不走都要改。**

---

## 3. ★CC / PD 控制器取舍 (本单要项目总工拍板的第 1 项)

### 3.1 事实基础

| 事实 | 值 | 证据 |
|---|---|---|
| Type-C 源端电流由 **Rp** 决定, 与 Rd 无关 | Default 56kΩ → 500mA (USB2) / 900mA ( 1,500mA USB3.2); 22kΩ → 1.5A; 10kΩ → 3.0A | [官方] USB-IF Spec R2.0 **Table 4-24** |
| Sink 侧 Rd | **5.1 kΩ ±20%** (CC1/CC2 各一颗到 GND) | [官方] USB-IF Spec R2.0 §4.x / §5.x |
| 只挂 Rd 时能拿到多少电流 | **完全取决于充电器的 Rp** (常见 56kΩ → 500mA) | [官方] 同上 + `HW/POWER_IC_SELECTION.md` §3.2 |
| TPS25730 是 PD3.1 sink-only UFP, 无需固件, 引脚可配置 | — | [官方] ti.com/lit/ds/symlink/tps25730.pdf §8.3.6/8.3.11-13 |
| TPS25730 集成 dead-battery Rd | RSNK = 4.1-6.1 kΩ | [官方] §6.2 |
| TPS25730 的 **VIN_3V3 (pin38) 需要 3.0-3.6V** (绝对最大 4V) | 工作范围 3.0-3.6V, 绝对最大 4.0V | [官方] §6.1/§6.2 |
| TPS25730 封装 | QFN-38 **4×4mm**, θJA = 57.4 °C/W | [官方] §5/§6.5 |
| TPS25730 外围量 | 4×ADCIN 分压电阻 + 2×CC 电容 (200-480pF) + 3~4 体电容 + (D 版还带内部功率通路 FET) | [官方] §9.2.2 例图 / §6.4 |

### 3.2 方案对比

| 维度 | **方案 A: 只留 Rd 5.1k ×2 (本规格推荐)** | 方案 B: 加 TPS25730 (PD 显式请求 5V/2A) |
|---|---|---|
| 充电电流可控性 | **不可控** (0.5A ~ 1.5A 随充电器 Rp 而变) | **可控** (显式请求, 源必须应答) |
| 源侧合规性 | 可能超过源广告值 (我们拉 1.0A 而源只广告 500mA → 源端过流保护动作, 端口掉电重枚举) | 天然合规 (PD 协商后按契约取流) |
| 额外器件 | **0** | +1 IC (4×4 QFN-38) + ~10 颗无源件 |
| **3.3V 需求** | **无** | ★**需要 VIN_3V3 = 3.0-3.6V, 而充电板没有 3.3V 轨** → 额外加一颗 3.3V LDO, 或按 datasheet 的 "VBUS LDO" 路径接 (**datasheet 无该接法示例 → 待 TI 确认**) |
| 面积 (25×10mm 板) | ~2 颗 0402 | 16mm² 焊盘 + 散热过孔 + 外围 ≈ 占板 8-10% |
| 我们用得上的 PD 能力 | — | 只用 5V; 9/12/15/20V **完全用不上** (整机是 1S 锂电, 最高 4.2V) |
| 失效模式 | 源只给 500mA → 充电慢 (575mAh 电池 ≈ 1.65h) | 3.3V 未起来 → PD 控制器不工作 → 退化成"无 Rd" → **CC 悬空 = 源认为没接设备** |

### 3.3 ★推荐: **方案 A (只留 Rd 5.1k ×2)**, 但加两条补丁

**推荐依据 (按权重排序)**:
1. **我们要的电压只有 5V** —— PD 的核心价值 (更高电压/更高功率) 对 1S 锂电整机**一点用没有**。
2. **充电板没有 3.3V 轨** —— 上 TPS25730 要么加 LDO (多一颗料 + 静态电流 + 启动时序), 要么走 datasheet 没给示例的 "VBUS LDO" 路径 (**待 TI 确认**)。
3. **25×10mm 面积紧张** —— 充电板同时要装 Type-C + ESD + π 滤波 + BQ25896 + 全部外围 + J_CHG 一侧。
4. **真正的安全上限由 `R_ILIM` 保证, 与 PD 无关** (见 §2.8) —— PD 控制器不提供任何本项目当前缺的安全能力。
5. **成本/交期**: 单价与交期均为 [0数据], 询价走项目总工; 多一颗 QFN-38 在 25×10mm 小板上贴装与返修的代价高于收益。

**补丁 1 —— 把"源只给 500mA"这件事变成可观测的, 而不是不可控的**:
- SoC 侧可对已跨铰链的 USB D+/D− 做 **BC1.2 检测** (SoC 是 UFP, 有 USB PHY) → 知道源的真实能力。
- 若要据此调充电电流, 就需要 **BQ25896 的 I2C 跨铰链** (J_CHG pin9/pin10, 见 §5.3)。
- **所以 I2C 跨铰链不是"为了 PD", 而是为了"源侧合规 + 充电电流可编程"** —— 这两件事 Rd 方案都做不了。

**补丁 2 —— 把 ILIM 电阻选成"保守但够用", 留出软件调整空间**:
- `R_ILIM` = 390Ω (→ 输入 0.82-1.00A, CC 段电池电流 ~0.67-0.82A)。
- 若源只支持 500mA (Rp=56k), 我们拉 0.5A 就停 —— **源不会过流** ✔; 若源支持 1.5A/2A, 我们最多拉 1.0A (ILIM 封顶), **仍可能略超源的 500mA 广告值** → 这正是补丁 1 (I2C + BC1.2) 要解决的。
- ⇒ **`R_ILIM` = 390Ω 是"无软件依赖"的基线; 有软件时 SoC 按 BC1.2 结果写 REG00 (IINLIM) 来精确贴合源能力。**

### 3.4 ★★对"跨铰链充电电流 1.0-1.5A"的影响 (量化)

> **关键概念**: 铰链段流过的是**电池充电电流 ICHG**, 不是输入电流 IIN。
> `ICHG ≈ IIN × (VBAT / VBUS) / η`, 取 VBAT=3.7V, VBUS=5V, η=90% → **ICHG ≈ 0.822 × IIN**。

| 场景 | 源侧能力 | `R_ILIM` | IIN 上限 | **铰链段 ICHG** | 相对 1.5A 设计点的余量 |
|---|---|---|---|---|---|
| ① Rd-only + 常见 Rp=56k 充电器 | 500 mA | 390Ω | 0.5A (源封顶) | **~0.41 A** | **3.7×** |
| ② Rd-only + Rp=22k 充电器 | 1.5 A | 390Ω | 0.82-1.00A | **~0.67-0.82 A** | **1.8-2.2×** |
| ③ 加 PD 5V/2A + `R_ILIM`=390Ω | 2 A | 390Ω | 0.82-1.00A | **~0.67-0.82 A** | **1.8-2.2×** |
| ④ 加 PD 5V/2A + `R_ILIM`=260Ω (更激进) | 2 A | 260Ω | 1.23-1.50A | **~1.01-1.23 A** | **1.2-1.5×** |
| ⑤ 加 PD 5V/2A + `R_ILIM`=300Ω ❌ | 2 A | 300Ω | 1.07-1.30A | **~0.88-1.07 A** | ❌ **判死**: 单 pin 0.534A > 0.5A 触点天花板 |
| ⑥ ★**最坏** ★: 不编程 ICHG + `R_ILIM` 不装 + 源支持 2A | 2 A | 无 | 寄存器 REG00 3.25A | **2.048 A (REG04 复位默认)** | ❌ **超 1.37×** |

**结论 (三条)**:
1. **铰链段载流规格 (1.5A) 不需要因为"上 PD"而改** —— 场景 ① 到 ⑤ 全部 ≤1.23A, 都在 1.5A 内。
2. **PD 5V/2A 真正改变的是"我们敢拉多少"**: 从 0.41A (场景 ①) 提到 1.0-1.2A (场景 ③/⑤)。**铰链段余量从 3.7× 缩到 1.4×** —— 这才是 ISS-091 核算时该盯的数, 而不是"PD 能不能拉到 2A"。
3. ★**真正的风险不是 PD, 是场景 ⑥**: BQ25896 的 **REG04 复位默认 ICHG = 2048 mA** [官方]。只要 `R_ILIM` 装上, 场景 ⑥ 被硬件压回 ~1.0A (390Ω 档 max 1.00A); **`R_ILIM` 不装 = 铰链过 2.05A**。⇒ **`R_ILIM` 是必装件, 不是选配件。**

**⇒ 提交项目总工拍板的问题**: 是否接受"第一版只留 Rd 5.1k ×2 (充电电流 0.4-1.1A 随充电器而变)"?
- 若**接受** → 按本规格出 P10, `R_ILIM`=390Ω, J_CHG pin9/pin10 留空给未来的 I2C。
- 若**不接受** (要求"必须 5V/2A 可控") → 上 TPS25730, 但**必须同时解决 VIN_3V3 的 3.3V 来源** (加 LDO 还是走 VBUS LDO 路径 → **需 TI 确认, 见 §8 待决项 1**), 且充电板面积 +8-10%, J_CHG 仍建议保留 pin9/pin10 (PD 控制器在充电板, 但充电 IC 的 I2C 仍在镜脚 → 仍要跨铰链)。

---

## 4. 保护与滤波

### 4.1 Type-C 入口 ESD 阵列

| 项 | 取值 | 证据 |
|---|---|---|
| **保护对象** | **5 个网**: VBUS / D+ / D− / CC1 / CC2 (SBU 不接 → 不需要) | [官方] Table 3-5 Note 3 + 本规格 §1.2 |
| 通道数 | **5-6 通道阵列** (一条通道对一个网) | [推算] |
| 位置 | 充电板侧, 距 Type-C 座 **≤3.0 mm** | [推算] `MECH/USB_HINGE_STRUCTURE.md` §5.2 E-1 (结构硬要求) |
| D+/D− 对地容值 | **≤1 pF** (保护 90Ω 差分眼图) | [推算] `HW/POWER_IC_SELECTION.md` §3.5 (EMC R-03) |
| CC / VBUS 对地容值 | **≤3 pF** | [推算] 同上 |
| VRWM | ≥24V (若将来上 PD); **只做 5V 时 ≥5-6V 也可** (钳位更低更好) | [推算] 同上 —— ⚠️ 两档取舍见 §8 待决项 4 |
| 型号 | **待选型 / 待询价** (外发经项目总工) | [0数据] |
| 地端 | ESD 阵列地脚 → 座侧 GND (与 Type-C GND 4 脚同网) | [推算] |

### 4.2 π 滤波 (磁珠 + 10µF + 100µF)

| 位号 | 值 | 连接 | 说明 | 证据 |
|---|---|---|---|---|
| `FB_VBUS` | 磁珠, 额定 **≥2A**, DCR ≤50mΩ, Z@100MHz 100-600Ω | USB_VBUS_RAW → VBUS_5V_F1 | 放在 ESD **之后** | [推算] EMC R-03 + [官方] 充电电流需求 |
| `C_VBUS_IN` | 10µF X7R 25V | VBUS_5V_ESD → GND | 磁珠前级 | [推算] |
| `C_VBUS_BULK` | 100µF X7R 10V | VBUS_5V_F1 → GND | 磁珠后级体电容 | [推算] (BQ25896 输入体电容) |

> ★**顺序不可换**: **Type-C → ESD → 磁珠 → 体电容 → BQ25896 VBUS 脚**。ESD 必须在磁珠**之前** (ESD 要直接泄放到地, 走线越短钳位越准)。
> ⚠️ **BQ25896 的输入去耦按 datasheet 原话**: "put **1µF on VBUS to PGND**, and the **rest capacitance on PMID to PGND**" → **100µF 体电容不能全部堆在 VBUS 脚** (PMID 也必须有电容), 否则开关节点环路不稳。本规格: VBUS 脚 1µF + PMID 脚 10µF, 100µF 体电容放在磁珠后级 (上游)。
> ⚠️ **100µF 与 BQ25896 的输入过冲**: 100µF 挂在 VBUS 脚上游, 上电浪涌由内部 RBFET 限制 —— 官方推荐只放 1µF 在 VBUS 脚, 故本规格的 100µF **放在 π 滤波后级、BQ25896 VBUS 脚之前** (两者之间是同一条粗铜), 浪涌由 RBFET 承受。**[待原厂]** 若 TI 建议把体电容全部放 PMID, 请按 TI 意见调整 (只动 2 行网表)。

### 4.3 输入 OVP / 浪涌

| 机制 | 归属 | 说明 | 证据 |
|---|---|---|---|
| VBUS 绝对最大 22V | BQ25896 内建 | 芯片级耐压足够 | [官方] §8.1 |
| 输入电压门限 VINDPM (最小 3.9V) + VINDPM_OS | BQ25896 寄存器 | VBUS=5V 不触发 DPM; 寄存器默认值即可 | [官方] REG00 |
| **VBUS 瞬态浪涌 (线缆插入尖峰)** | **外部 TVS**: `D_TVS_VBUS` 5V 级单向 TVS, **DNP / 待选型** | VRWM ≥5.0V, 钳位电压 < 芯片绝对最大 22V (留足余量); 位置紧靠 Type-C 座 | [推算] (datasheet 绝对最大 22V + 线缆尖峰常识) |
| ESD | §4.1 | 人手接触路径 (本项目 EMC 第一风险 R-07) | [推算] `HW/EMC_PRECHECK.md` §R-07 |

### 4.4 ★电池保护 (BQ2970 + 2×MOS) —— **不在充电板**

| 件 | 装在哪 | 依据 |
|---|---|---|
| 电池 432243 (3.7V ≥420mAh) | **镜脚主 PCB** | `HW/SCHEMATIC_V1.md` P1 §V1.2 (MECH-B7 裁决) |
| **BQ2970** (1S 保护 IC, OVP 4.275V 档) | **镜脚主 PCB** | 同上 + `HW/POWER_IC_SELECTION.md` §3.3 |
| **2× 外置 N-MOS** (BQ2970 驱动) | **镜脚主 PCB** | 同上 |
| 充电板这边 | **不需要任何电芯级保护件** | 充电板只负责 VBUS → 电池的充电通路 |

> ⇒ **充电板 BOM 不含 BQ2970 / MOS / 电池** —— 这条要在备料单上写死, 否则会重复采购。

---

## 5. 跨铰链界面 (充电板侧)

### 5.1 过铰链的线 (逐类: 要求 + 取值)

| # | 线 | 方向 | 充电板侧 (镜框) | 镜脚侧 | 取值 / 要求 | 证据 |
|---|---|---|---|---|---|---|
| 1 | **充电电流 (双 pin)** | 镜框 → 镜脚 | `U_CHG` pin13/14 (BAT) → `BAT_CHG` → `J_CHG` pin1 **+** pin2 | `J_CHG` → BQ2970 → 电池 | **1.0-1.5A**, 双 pin 并联 (每 pin ≤0.75A); 1.27mm→0.5mm 改后每 pin 载流下降 → 用并联解决 | [推算] `MECH/USB_HINGE_STRUCTURE.md` §5.3 C-1 + P1 §V1.2 |
| 2 | **回流 (双 pin)** | 镜框 → 镜脚 | `J_CHG` pin3 **+** pin4 → 充电板 GND | 镜脚数字地 | 与电源 pin **相邻** → 环路面积最小 | [推算] P9 |
| 3 | **VBUS_DET (高阻分压)** | 镜框 → 镜脚 | `R_VDET_TOP` 1M ← VBUS; `R_VDET_BOT` 1M → GND; 中点 → `J_CHG` pin8 | SoC ADC | 源阻抗 **500 kΩ** → **必须被 GND 夹持** (每根至少一侧相邻 GND) 且与 USB 差分对 **≥3mm** | [推算] `MECH/USB_HINGE_STRUCTURE.md` §5.2 第 5 条 |
| 4 | **CHG_STAT (开漏)** | 镜框 → 镜脚 | `U_CHG` pin4 → `J_CHG` pin6 | SoC GPIO, **主板侧** 10k 上拉 → 3.3V | LOW=充电中 / HIGH=完成或禁用 / **1Hz 闪烁=故障** | [官方] datasheet + STAT 状态表 |
| 5 | **PWR_GOOD (开漏)** | 镜框 → 镜脚 | `U_CHG` pin3 → `J_CHG` pin7 | SoC GPIO, **主板侧** 10k 上拉 → 3.3V | LOW = 输入源良好 (VBUS 在 VVBUS_OP 内 & IBATSRC>30mA) | [官方] datasheet |
| 6 | **USB D+/D−** | 镜脚 → 镜框 | `CONN_USB` pin1/2 → 板内走线 → `J_TYPE_C` A6+B6 / A7+B7 | SoC → 22Ω 串阻 (主板侧) → `CONN_USB` | **90Ω ±10% 差分**; D+/D− 双份并联 **≤3.5mm**; **不装共模扼流圈**; 两端各一组 ESD | [官方] USB-IF Table 3-5 Note 2 + [推算] P9 两条硬规则 |
| 7 | **USB 回流** | | `CONN_USB` pin3 (独立回流地) | 镜脚 GND | 独立 pin, 不与电源共 pin | [推算] P9 |
| 8 | **TS (电池 NTC)** | 镜脚 → 镜框 | `U_CHG` pin11 (TS) → `J_CHG` pin5 | NTC 10k ∥ 30.31k → GND | 源阻抗 3-4 kΩ → 跨铰链 OK; **充电板侧只有 5.24k 上臂 (REGN→TS)** | [官方] Equation 2 + [推算] |
| 9 | **BQ25896 I2C** | 镜脚 → 镜框 | `U_CHG` pin5/6 → `J_CHG` pin9/pin10 | SoC, **主板侧** 4.7k 上拉 → 3.3V | 400kHz; **跨铰链跑 400kHz I2C 是新增的 EMI/边沿风险** | [待裁决] §5.3 |

### 5.2 ★`J_CHG` pin map 提案 (10p @0.5mm)

> **本规格只提提案, 不改 `INTERFACES.md` / 网表** —— pin map 是接口表的地盘, 由项目总工拍板。

| pin | 提案 (基线: 电池在镜脚) | 说明 |
|---|---|---|
| pin1 | `BAT_CHG+` | 充电电流 (与 pin2 并联) |
| pin2 | `BAT_CHG+` | 充电电流 (与 pin1 并联) |
| pin3 | `GND_CHG` | 回流 (与 pin4 并联) |
| pin4 | `GND_CHG` | 回流 (与 pin3 并联) |
| **pin5** | **`TS_BAT`** | ★**新增** —— NTC 在镜脚, TS 必须跨铰链 (现行 pin map 缺这一根) |
| pin6 | `CHG_STAT` | 开漏, 主板侧上拉 |
| pin7 | `PWR_GOOD` | 开漏, 主板侧上拉 |
| pin8 | `VBUS_DET` | 1M+1M 分压输出 |
| **pin9** | **`I2C_CHG_SCL`** (预留/DNP) | ★**新增** —— 给 SoC 编程 ICHG/IINLIM + 读 VBUS/IBAT |
| **pin10** | **`I2C_CHG_SDA`** (预留/DNP) | ★**新增** |

**与现行 pin map 的差异**: 现行 (P9) 是 pin5=CHG_STAT / pin6=PWR_GOOD / pin7=VBUS_DET / pin8-10=预留。本提案把 CHG_STAT/PG/VBUS_DET **各后移 1 位**, 把 pin5 让给 TS, 把 pin9/10 留给 I2C。

**★与结构侧建议的冲突 (需项目总工转达结构总工复核)**:
- 结构侧 `MECH/USB_HINGE_STRUCTURE.md` §5.3 **C-4** 建议 `J_CHG` → **8p @0.5mm** (8+20+4+8 = 40 脚 = 20mm 触点区)。
- 本提案是 **10p** (基线实需 8 根 + I2C 预留 2 根)。
- **但铰链高度预算够**: P9 已算 (10+4+18+21)×0.5 = **26.5mm** vs 镜脚根部净高 **37.0mm** → **余 10.5mm** ✔。结构侧 C-4 的 8p 建议是在**没算 TS 和 I2C** 的前提下给出的 (按当时口径数脚)。⇒ **请结构总工按 10p 复核一次铰链区堆叠 (结论预期: 仍通过, 余量 10.5mm)**。

**★"电池装镜框"可回退分支的 pin map 不兼容 (必须提前知道)**:
- 若将来把电池挪回镜框 (V1.2 的可回退分支), 跨铰链的大电流换成 **SYS 0.55A**, 但 **TS 不再需要跨铰链** (NTC 与充电器同板), 而 **BQ25896 的 I2C 仍然要跨铰链** (SoC 仍在镜脚) → 脚数 = SYS×2 + GND×2 + CHG_STAT + PG + VBUS_DET + I2C×2 = **9 根**, 且**与基线 pin map 不兼容**。
- ⇒ **结论: `J_CHG` 的 pin map 必须在打样前锁死电池位置; 两种形态不能共用同一张 pin map**。这是 §5.3 待裁决项。

### 5.3 ★待项目总工裁决 (跨铰链接口)

| # | 问题 | 我的建议 | 影响 |
|---|---|---|---|
| **J-1** | `J_CHG` pin map 采纳本提案 (10p, 含 TS + I2C 预留)? | **采纳** | 决定 P10 全部跨铰链行 |
| **J-2** | `J_CHG` 做 8p 还是 10p? | **10p** (余量 10.5mm), 请结构总工复核 | 铰链区堆叠 |
| **J-3** | BQ25896 的 I2C **跨不跨铰链**? | **跨 (pin9/pin10), 但默认 DNP** —— 跨了才能按 BC1.2 结果写 REG00/REG04; 不跨也能工作 (靠 `R_ILIM` 兜底) | 2 个铰链脚 + 400kHz 跨铰链 EMI |
| **J-4** | 电池位置 (镜脚 vs 镜框) 打样前锁死? | **锁镜脚** (基线), 同时接受 pin map 不可两态通用 | 连接器封装/PCB 一旦定型不可逆 |
| **J-5** | `VBUS_DET` 是否保留 (与 PG 功能重叠)? | **保留** (pin8), 但可 DNP | 省 1 个铰链脚 |

---

## 6. 机械 / 装配约束 (全部引自 MECH 已有结论, 本单不自创)

| # | 约束 | 值 | 来源 |
|---|---|---|---|
| M-1 | Type-C 面板开孔 | **9.5 × 3.6 mm** | `MECH/USB_HINGE_STRUCTURE.md` §5.2 F-5 / `MECH_BUDGET.md` §5.1 / `MECH/print/GEOM_SPEC_REVA.md` #44 |
| M-2 | 末端壁厚 (承力材料) | **≥1.5 mm** | 同上 |
| M-3 | 开口边 | 加**铝框防刮** | 同上 |
| M-4 | **承力路径** | Type-C 座正下方 **≥2 个承力柱** + **一个沿拔出方向的限位台阶** (让拔出时先顶限位面, 而不是拉焊点) | ISS-085 **F-4** (`MECH/USB_HINGE_STRUCTURE.md` §5.2 第 4 条) |
| M-5 | 拔线力路径 | **不得经由跨铰链 FPC 传递** | 同上 |
| M-6 | 插拔力 | USB-C 插拔力典型 **15-30 N** [推算] (规范原文未核) | 同上 |
| M-7 | 沉板深度 | 0.8 / 1.0 / 1.6 / 2.10 mm 四种 → 由结构总工按镜框端件壁厚选 | `HW/POWER_IC_SELECTION.md` §3.5 |
| M-8 | 充电板外形 | 25 × 10 × 0.8 mm | `MECH/MECH_BUDGET.md` §1.3 M3 |
| M-9 | 充电板固定 | 1×M1.2 螺钉 + 铝屏蔽罩贴合 Type-C | 同上 |
| M-10 | **散热隔离** | Type-C 座与充电 IC 的**热隔离 ≥5 mm** (或加隔热槽); 充电 IC 耗散落在镜框端件 | `MECH/USB_HINGE_STRUCTURE.md` §7 装配 |
| M-11 | 位置 | Type-C 座必须放**镜框端件靠铰链处** (框内段 ≤20mm) | `MECH/USB_HINGE_STRUCTURE.md` §5.2 第 6 条 |
| M-12 | ESD 距离 | 距连接器 **≤3.0 mm**, 一律放 PCB 端, **不许上 FPC** | 同上 §5.2 E-1 + ISS-085 规则 ④ |
| M-13 | 固定夹滑移 | ≤0.1 mm; 应力释放直线段 ≥5.0 mm; 弯折半径 ≥3.0 mm | ISS-085 规则 ③ |
| M-14 | 防呆 | `J_CHG` 必须有机械防呆 (无防呆 → 反插 = 短接) | ISS-085 F-6 |
| M-15 | 印刷公差 | 面板开孔宽公差 ±0.1 (9.4~9.6) | `MECH/print/MEASURE_CHECKLIST.md` H9 |

> ★**M-4 是本单最容易被漏掉的一条**: 网表和 BOM 都看不出"Type-C 座底下要有 2 根承力柱 + 1 个限位台阶" —— 这是**结构件**, 但**没有它, 插拔力会直接作用在焊点上**。备料/结构清单里必须显式列出。

---

## 7. ★可落网表的连接清单

> **格式与 `HW/netlist_v1.csv` 完全一致**: `page,net,node1,node2,ref,value,type,dnp,evidence,tbd,note,conn_id,board`
> **页号统一用 `P10`** (新页: 充电板器件级)。`board` 列三档: `CHG_BOARD` / `MAIN_PCB` / `HINGE`。
> **可直接贴进 `state/gen_netlist.py`**; 项目总工落页时再决定 P10 的标题与叙述。
> ⚠️ **本清单不含任何 SoC 球位号** —— 全部 TBD-01 占位由 PM 处理, 本单不碰。

```csv
page,net,node1,node2,ref,value,type,dnp,evidence,tbd,note,conn_id,board
P10,VBUS_5V,J_TYPE_C A4+A9+B4+B9,D_ESD_TC,RAIL_VBUS_5V,5.0V ±5%,RAIL,必装,[推算],,电源域: 5.0V ±5% / 输入电流硬件上限 0.82-1.00A (R_ILIM=390Ω) / 充电链整条在充电板(镜框); SoC 侧球位号 TBD-01,C-01,CHG_BOARD
P10,USB_VBUS_RAW,J_TYPE_C A4+A9+B4+B9,D_ESD_TC,J_TYPE_C,Type-C 16p 母座 (沉板 4脚插板),CONN,必装,[官方],,USB-IF Type-C Spec R2.0 Table 3-5: A4/A9/B4/B9=VBUS (座内并联); 座→ESD 走线 ≤3.0mm (MECH E-1); 型号待选型,C-01,CHG_BOARD
P10,USB_VBUS_RAW,D_ESD_TC,USB_VBUS_RAW,D_ESD_TC,ESD 阵列 5~6 通道 [待选型],D,必装,[推算],,"Type-C 入口 ESD: 保护 VBUS/D+/D-/CC1/CC2 共 5 网; D+/D- 容值 ≤1pF, CC/VBUS ≤3pF; 距座 ≤3.0mm; 型号待选型/询价走项目总工",C-01,CHG_BOARD
P10,GND,D_ESD_TC,GND,D_ESD_TC,ESD 阵列 5~6 通道 [待选型],D,必装,[推算],,ESD 阵列地端 (Type-C 座侧地),C-01,CHG_BOARD
P10,VBUS_5V_ESD,D_ESD_TC,FB_VBUS,FB_VBUS,"π 滤波磁珠 [待选型] (≥2A, DCR≤50mΩ)",L,必装,[推算],,π 滤波前级磁珠: 必须排在 ESD 之后; 型号待选型,C-01,CHG_BOARD
P10,VBUS_5V_ESD,VBUS_5V_ESD,C_VBUS_IN,C_VBUS_IN,10µF X7R 25V,C,必装,[推算],,π 滤波输入电容 (磁珠前级),C-01,CHG_BOARD
P10,GND,C_VBUS_IN,GND,C_VBUS_IN,10µF X7R 25V,C,必装,[推算],,π 滤波输入电容 地端,C-01,CHG_BOARD
P10,VBUS_5V_F1,FB_VBUS,FB_VBUS,FB_VBUS,"π 滤波磁珠 [待选型] (≥2A, DCR≤50mΩ)",L,必装,[推算],,π 滤波后级 (同一颗磁珠输出端),C-01,CHG_BOARD
P10,VBUS_5V_F1,VBUS_5V_F1,C_VBUS_BULK,C_VBUS_BULK,100µF X7R 10V,C,必装,[推算],,π 滤波后级体电容 (BQ25896 输入体电容),C-01,CHG_BOARD
P10,GND,C_VBUS_BULK,GND,C_VBUS_BULK,100µF X7R 10V,C,必装,[推算],,π 滤波后级电容 地端,C-01,CHG_BOARD
P10,VBUS_5V_CHG,FB_VBUS,U_CHG pin1,FB_VBUS,"π 滤波磁珠 [待选型] (≥2A, DCR≤50mΩ)",L,必装,[推算],,磁珠后级 → BQ25896 VBUS 脚 (pin1),C-01,CHG_BOARD
P10,VBUS_5V_CHG,C_VBUS_BULK,U_CHG pin1,C_VBUS_BULK,100µF X7R 10V,C,必装,[推算],,体电容 → BQ25896 VBUS 脚 (pin1),C-01,CHG_BOARD
P10,VBUS_5V_CHG,U_CHG pin1,C_VBUS_IC,C_VBUS_IC,1µF X7R 25V,C,必装,[官方],,★BQ25896 pin1 VBUS: 'Place a 1-µF ceramic capacitor from VBUS to PGND and place it as close as possible to IC',C-01,CHG_BOARD
P10,PGND,C_VBUS_IC,PGND,C_VBUS_IC,1µF X7R 25V,C,必装,[官方],,BQ25896 VBUS 去耦 地端 (PGND),C-01,CHG_BOARD
P10,PMID,U_CHG pin23,L_CHG,L_CHG,2.2µH Isat≥1.5A DCR≤50mΩ,L,必装,[官方],,开关电感 PMID↔SW; IRIPPLE=VBUS·D·(1-D)/(fs·L)=0.29A @5V/3.7V/1.5MHz/2.2µH (datasheet 指引 20-40%),C-01,CHG_BOARD
P10,SW,L_CHG,U_CHG pin19+pin20,L_CHG,2.2µH Isat≥1.5A DCR≤50mΩ,L,必装,[官方],,电感另一端 → SW 开关节点 (铜箔面积最小),C-01,CHG_BOARD
P10,PMID,U_CHG pin23,C_PMID,C_PMID,10µF X7R 25V,C,必装,[官方],,"★'put 1µF on VBUS to PGND, and the rest capacitance on PMID to PGND'; PMID 电容不可省",C-01,CHG_BOARD
P10,PGND,C_PMID,PGND,C_PMID,10µF X7R 25V,C,必装,[官方],,PMID 电容 地端,C-01,CHG_BOARD
P10,SW,U_CHG pin19+pin20,C_BST,C_BST,47nF 25V,C,必装,[官方],,★自举电容 0.047µF from SW to BTST,C-01,CHG_BOARD
P10,BTST,U_CHG pin21,C_BST,C_BST,47nF 25V,C,必装,[官方],,BTST ↔ SW 自举电容 另一端,C-01,CHG_BOARD
P10,REGN_5V,U_CHG pin22,C_REGN,C_REGN,4.7µF 10V,C,必装,[官方],,★'Connect a 4.7 µF (10 V rating) ceramic capacitor from REGN to analog GND',C-01,CHG_BOARD
P10,GND,C_REGN,GND,C_REGN,4.7µF 10V,C,必装,[官方],,REGN 去耦 地端 (模拟地),C-01,CHG_BOARD
P10,VBUS_5V_CHG,U_CHG pin1,U_CHG,U_CHG,BQ25896,IC,必装,[官方],,TI BQ25896 VQFN-16 3×3mm (RGT); 充电 IC 装镜框充电板; 单价/交期 [0数据] 询价走项目总工,C-01,CHG_BOARD
P10,SW,U_CHG pin19+pin20,U_CHG,U_CHG,BQ25896,IC,必装,[官方],,pin19/20 SW 开关节点,C-01,CHG_BOARD
P10,BTST,U_CHG pin21,U_CHG,U_CHG,BQ25896,IC,必装,[官方],,pin21 BTST,C-01,CHG_BOARD
P10,REGN_5V,U_CHG pin22,U_CHG,U_CHG,BQ25896,IC,必装,[官方],,"pin22 REGN (内部 LDO 5.0V, 4.8-5.5V, 限流 50mA) = TS 分压基准",C-01,CHG_BOARD
P10,PMID,U_CHG pin23,U_CHG,U_CHG,BQ25896,IC,必装,[官方],,pin23 PMID (RBFET 漏极 + HSFET 漏极),C-01,CHG_BOARD
P10,PGND,U_CHG pin17+pin18,PGND,U_CHG,BQ25896,IC,必装,[官方],,pin17/18 PGND 功率地 (开关节点地); 'A single point connection is recommended between power PGND and the analog GND near the IC PGND pin'; PowerPAD 同接 PGND + ≥6 过孔,C-01,CHG_BOARD
P10,ILIM,U_CHG pin10,R_ILIM,R_ILIM,390Ω ±1% (0402),R,必装,[官方],,"★输入电流硬件上限: IINMAX=KILIM/RILIM (KILIM 320/355/390 AΩ) → 0.82-1.00A; CC 段电池电流 ~0.67-0.82A; ILIM 脚稳在 0.8V, 功耗 0.8²/390=1.64mW; **必装件** (不装 → REG04 复位默认 ICHG=2048mA 会让铰链过 2.05A); ★★V1.9 (老板 10-28): 定 390Ω (单 pin 0.411A, 触点 ≥0.5A 余量 1.22×); 300Ω 档判死 (单 pin 0.534A > 0.5A 天花板)",C-01,CHG_BOARD
P10,PGND,R_ILIM,PGND,R_ILIM,390Ω ±1% (0402),R,必装,[官方],,ILIM 电阻 地端,C-01,CHG_BOARD
P10,PSEL,U_CHG pin2,R_PSEL,R_PSEL,10k ±1%,R,必装,[官方],,"PSEL 拉低 = 适配器/DCP → 源检测后 IINLIM 自动切 3.25A, 实际由 ILIM 电阻封顶; 拉高会锁 500mA",C-01,CHG_BOARD
P10,PGND,R_PSEL,PGND,R_PSEL,10k ±1%,R,必装,[官方],,PSEL 下拉 地端,C-01,CHG_BOARD
P10,CE_SET,U_CHG pin9,R_CE,R_CE,10k ±1%,R,必装,[官方],,CE 拉低 = 允许充电 (CHG_CONFIG 复位默认 1); 'CE pin must be pulled High or Low' → 不得悬空; 拉低的好处: SoC 死机也能充电,C-01,CHG_BOARD
P10,PGND,R_CE,PGND,R_CE,10k ±1%,R,必装,[官方],,CE 下拉 地端,C-01,CHG_BOARD
P10,OTG_SET,U_CHG pin8,R_OTG,R_OTG,10k ±1%,R,必装,[官方],,OTG 拉低 = 关 boost 模式 (本机不做 OTG),C-01,CHG_BOARD
P10,PGND,R_OTG,PGND,R_OTG,10k ±1%,R,必装,[官方],,OTG 下拉 地端,C-01,CHG_BOARD
P10,QON,U_CHG pin12,NC,NC,QON 不接 (内部上拉),NET,DNP,[官方],,QON 按键功能放镜脚侧 (SYS 在镜脚); 本板留焊盘不装,C-01,CHG_BOARD
P10,SYS,U_CHG pin15+pin16,C_SYS,C_SYS,20µF 6.3V,C,DNP,[官方],,"★SYS 在镜脚由 BQ2970 产生, 本板 SYS 不对外供电; 留位不装 = 保留'电池挪镜框'可回退分支; 悬空是否影响 BATFET 通路待 TI 确认",C-02,CHG_BOARD
P10,PGND,C_SYS,PGND,C_SYS,20µF 6.3V,C,DNP,[官方],,SYS 电容 地端,C-02,CHG_BOARD
P10,BAT_CHG,U_CHG pin13+pin14,C_BAT,C_BAT,10µF X7R 6.3V,C,必装,[官方],,★'Connect a 10uF closely to the BAT pin' (pin13/14),C-03,CHG_BOARD
P10,PGND,C_BAT,PGND,C_BAT,10µF X7R 6.3V,C,必装,[官方],,BAT 去耦 地端,C-03,CHG_BOARD
P10,BAT_CHG,U_CHG pin13+pin14,U_CHG,U_CHG,BQ25896,IC,必装,[官方],,pin13/14 BAT (内部 11mΩ BATFET); 充电电流路径 BAT→J_CHG→镜脚电池,C-03,CHG_BOARD
P10,NC_UCHG,U_CHG pin24,NC_UCHG,NC,NC (datasheet: No Connect),NET,DNP,[官方],,pin24 NC: 不接 (16p 母座同类的 pin 名对照: VBUS1/PSEL2/PG3/STAT4/SCL5/SDA6/INT7/OTG8/CE9/ILIM10/TS11/QON12/BAT13-14/SYS15-16/PGND17-18/SW19-20/BTST21/REGN22/PMID23/NC24),C-01,CHG_BOARD
P10,BAT_CHG,BAT_CHG,J_CHG pin1,BAT_CHG,跨铰链 1.0-1.5A (双 pin 并联),NET,必装,[推算],,"充电电流跨铰链 (J_CHG pin1/pin2 并联, 每 pin ≤0.75A); 铰链段**不装 π 滤波** (会破坏 BQ25896 环路稳定性); 载流/压降/发热核算见 ISS-091",C-03,HINGE
P10,BAT_CHG,J_CHG pin1,J_CHG pin2,J_CHG,"1×10p@0.5mm 排线座 (充电板↔主 PCB, 跨铰链载流)",CONN,必装,[推算],,"双 pin 并联; ★本单提案 pin map: 1/2=BAT_CHG, 3/4=GND, 5=TS, 6=CHG_STAT, 7=PG, 8=VBUS_DET, 9/10=I2C 预留 —— 待 PM 裁决 (见 §5.2)",C-03,HINGE
P10,BAT_CHG,J_CHG pin2,U_BATPROT,BAT_CHG,跨铰链 1.0-1.5A (双 pin 并联),NET,必装,[推算],,"镜脚侧: 进 BQ2970 + 2×MOS (保护 IC 与电池同板, **不在充电板**)",C-03,HINGE
P10,GND_CHG,J_CHG pin3,J_CHG pin4,J_CHG,回流 (双 pin),NET,必装,[推算],,充电电流回流双 pin (与电源 pin 相邻 → 环路面积最小),C-03,HINGE
P10,GND_CHG,J_CHG pin4,GND,J_CHG,回流 (双 pin),NET,必装,[推算],,回流进镜脚侧数字地,C-03,HINGE
P10,TS_BAT,R_TS1,U_CHG pin11,R_TS1,5.24k ±1%,R,必装,[官方],,★TS 分压上臂 REGN→TS (datasheet Equation 2: RT1=5.24k); TS 网跨铰链到镜脚电池侧 NTC,C-03,CHG_BOARD
P10,REGN_5V,R_TS1,REGN_5V,R_TS1,5.24k ±1%,R,必装,[官方],,TS 上臂 取自 REGN (5.0V),C-03,CHG_BOARD
P10,TS_BAT,U_CHG pin11,U_CHG,U_CHG,BQ25896,IC,必装,[官方],,pin11 TS: 硬件级电池过温/欠温停充 (不依赖 SoC); 阈值 V(T1)=73.25% / V(T5)=34.375% of REGN,C-03,CHG_BOARD
P10,TS_BAT,R_TS1,J_CHG pin5,TS_BAT,高阻检测线 (源阻抗 3-4kΩ),NET,必装,[推算],,TS 跨铰链 (NTC 在镜脚电池侧); 源阻抗仅 3-4kΩ → 跨铰链 OK,C-03,HINGE
P10,TS_BAT,R_TS2,TS_BAT,R_TS2,30.31k ±1%,R,必装,[官方],,"★TS 分压下臂 (**镜脚侧**, 与 NTC 并联): datasheet Equation 2 → RT2=30.31k; 装在电池旁 (NTC 旁边), 引线尽量短",C-03,MAIN_PCB
P10,GND,R_TS2,GND,R_TS2,30.31k ±1%,R,必装,[官方],,TS 下臂 地端,C-03,MAIN_PCB
P10,TS_BAT,R_NTC_BAT,TS_BAT,R_NTC_BAT,10k NTC B=3435 (103AT) 贴电芯,R,必装,[官方],,★电池 NTC (**镜脚侧**): 与 R_TS2 并联; 'Recommend 103AT-2 thermistor'; 贴电芯表面; ★现行网表把它放在 CHG_BOARD 且接 BAT_PROT → 必须改,C-03,MAIN_PCB
P10,GND,R_NTC_BAT,GND,R_NTC_BAT,10k NTC B=3435 (103AT),R,必装,[官方],,NTC 地端 (贴电芯负极侧),C-03,MAIN_PCB
P10,CHG_STAT,U_CHG pin4,J_CHG pin6,CHG_STAT,开漏 (主板侧 10k 上拉 3.3V),NET,必装,[官方],,★STAT: LOW=充电中 / HIGH=完成或禁用 / 1Hz 闪烁=故障; **上拉只能在主板侧** (充电板无 3.3V),B-05,HINGE
P10,PWR_GOOD,U_CHG pin3,J_CHG pin7,PWR_GOOD,开漏 (主板侧 10k 上拉 3.3V),NET,必装,[官方],,★PG: LOW=输入源良好 (VBUS 在 VVBUS_OP 内 & IBATSRC>30mA); 上拉在主板侧,B-06,HINGE
P10,I2C_CHG_SCL,U_CHG pin5,J_CHG pin9,I2C_CHG_SCL,400kHz (上拉在主板侧 4.7k→3.3V),NET,DNP,[待裁决],,"★BQ25896 I2C 跨铰链 (预留): 用于 SoC 编程 REG04(ICHG)/REG00(IINLIM) 与读 VBUS/IBAT; 上拉只放主板侧, 本板不留上拉; 待 PM 裁决 (J-3)",B-08,HINGE
P10,I2C_CHG_SDA,U_CHG pin6,J_CHG pin10,I2C_CHG_SDA,400kHz (上拉在主板侧 4.7k→3.3V),NET,DNP,[待裁决],,同 SCL; 待 PM 裁决 (J-3),B-08,HINGE
P10,I2C_CHG_SCL,U_CHG pin5,R_PU_SCL,R_PU_SCL,10k ±1%,R,DNP,[官方],,BQ25896 SCL 上拉位 (留位): **跨铰链版本不装** (上拉在主板侧); 不跨版本也不装,B-08,CHG_BOARD
P10,I2C_CHG_SDA,U_CHG pin6,R_PU_SDA,R_PU_SDA,10k ±1%,R,DNP,[官方],,BQ25896 SDA 上拉位 (留位): 同上,B-08,CHG_BOARD
P10,INT_CHG,U_CHG pin7,R_PU_INT,R_PU_INT,10k ±1%,R,DNP,[官方],,"INT 开漏 256µs 脉冲; **本版不跨铰链** (J_CHG 无余量), 留位不装; 若将来要跨, 上拉必须移到主板侧 3.3V 并顶掉 J_CHG pin9/pin10",B-07,CHG_BOARD
P10,USB_CC1,J_TYPE_C A5,R_CC1,USB_CC1,5.1k ±1% (Rd 到 GND),NET,必装,[官方],,★Type-C Rd: 'Pin A5 (CC) ... shall be connected to GND through a resistor Rd (5.1 kΩ ± 20%)' (USB-IF Spec R2.0); 本板只做 Rd 不上 PD 控制器 (见 §3),B-23,CHG_BOARD
P10,GND,R_CC1,GND,R_CC1,5.1k ±1%,R,必装,[官方],,CC1 Rd 地端,B-23,CHG_BOARD
P10,USB_CC2,J_TYPE_C B5,R_CC2,USB_CC2,5.1k ±1% (Rd 到 GND),NET,必装,[官方],,CC2 Rd (USB-IF: 5.1kΩ ±20%),B-23,CHG_BOARD
P10,GND,R_CC2,GND,R_CC2,5.1k ±1%,R,必装,[官方],,CC2 Rd 地端,B-23,CHG_BOARD
P10,USB_D_P_CHG,CONN_USB pin1,J_TYPE_C A6+B6,USB_D_P_CHG,板内走线 90Ω 差分,NET,必装,[官方],,★充电板侧 USB D+ 从跨铰链连接器到 Type-C (A6+B6 双份并联); 规范: 'The maximum shorting trace length should not exceed 3.5 mm',B-23,CHG_BOARD
P10,USB_D_N_CHG,CONN_USB pin2,J_TYPE_C A7+B7,USB_D_N_CHG,板内走线 90Ω 差分,NET,必装,[官方],,"同 D- (A7+B7 双份并联, ≤3.5mm); ★不装共模扼流圈",B-23,CHG_BOARD
P10,GND,J_TYPE_C A1+A12+B1+B12,GND,J_TYPE_C,Type-C 16p 母座 (物理 A/B 脚位),CONN,必装,[官方],,"★USB-IF Table 3-5: GND = A1/A12/B1/B12 (4 脚全并联); ★现行网表只写了 A1+A12 → B1/B12 悬空 (回流减半), 必须补",C-01,CHG_BOARD
P10,GND,J_TYPE_C shield,GND,J_TYPE_C,Type-C 16p 母座 (物理 A/B 脚位),CONN,必装,[官方],,"屏蔽壳 → GND **单点接** (短粗铜皮, 不用细线); 与机壳地的接法待结构定 (ISS-065)",C-01,CHG_BOARD
P10,NC_SBU1,J_TYPE_C A8,NC_SBU1,NC,SBU1 不接 (规范要求),NET,DNP,[官方],,"★USB-IF Table 3-5 Note 3: 'Contacts A8 and B8 (SBU1 and SBU2) shall be not connected unless required for a specified purpose'; 本机不做 Alt Mode → 悬空 (焊盘可留, 不接)",B-23,CHG_BOARD
P10,NC_SBU2,J_TYPE_C B8,NC_SBU2,NC,SBU2 不接 (规范要求),NET,DNP,[官方],,SBU2 同上,B-23,CHG_BOARD
P10,VBUS_DET,USB_VBUS_RAW,R_VDET_TOP,R_VDET_TOP,1M ±1%,R,必装,[推算],,VBUS 检测分压 上臂 (充电板侧): 1M+1M → 源阻抗 500kΩ; 跨铰链必须被 GND 夹持 (每根至少一侧相邻 GND) 且与 USB 差分对 ≥3mm (MECH §5.2 第5条),B-09,CHG_BOARD
P10,VBUS_DET,R_VDET_BOT,VBUS_DET,R_VDET_BOT,1M ±1%,R,必装,[推算],,VBUS 检测分压 下臂 (充电板侧); 中点 = VBUS_DET 网 (2.5V @ VBUS 5V),B-09,CHG_BOARD
P10,GND,R_VDET_BOT,GND,R_VDET_BOT,1M ±1%,R,必装,[推算],,VBUS 检测分压 下臂 地端,B-09,CHG_BOARD
P10,VBUS_DET,R_VDET_TOP,J_CHG pin8,VBUS_DET,1M+1M 分压输出 (2.5V @5V),NET,必装,[推算],,"跨铰链高阻检测线 (500kΩ 源阻抗 → 易受干扰, 必须 GND 夹持 + 远离 USB 差分)",B-09,HINGE
P10,GND,PGND,GND,R_STAR_PGND,0Ω (可选: 单点星接),R,DNP,[官方],,"★BQ25896: 'A single point connection is recommended between power PGND and the analog GND near the IC PGND pin'; 若项目管理上只用单地, 删掉此位并把 PGND 全并到 GND (只改网表 1 行)",C-01,CHG_BOARD
P10,VBUS_5V,TP_VBUS,VBUS_5V,TP_VBUS,测试点,TP,必装,[推算],,充电板侧 VBUS 测点 (π 滤波后级),C-01,CHG_BOARD
P10,TS_BAT,TP_TS,TS_BAT,TP_TS,测试点,TP,必装,[推算],,TS 电压测点 (调 TS 分压 / 验证 NTC 跨铰链通断),C-03,CHG_BOARD
```

### 7.1 本清单的计数对账 (供门禁直接用)

| 计数项 | 声明 | 清单里实际 | 对账 |
|---|---|---|---|
| `J_TYPE_C` 触点 | **16** (14 接 + 2 NC) | 16 (A1/A4/A5/A6/A7/A8/A9/A12/B1/B4/B5/B6/B7/B8/B9/B12) | ✅ 16 == 16 |
| └ 现行网表引用 | 16 | **12** | ❌ **差 4 (漏 B1/B12/A8/B8) → 必须补** |
| `J_TYPE_C` 16p 不存在的 A/B 位置 | 8 (A2/A3/A10/A11/B2/B3/B10/B11) | 0 (PCB 无焊盘) | ✅ |
| `U_CHG` 引脚 | **24** (含 NC) | 24 (1-24 全覆盖, 含 pin24 NC) | ✅ 24 == 24 |
| └ 实际接线脚 | 22 (除 pin24 NC) | 22 | ✅ |
| `J_CHG` 引脚 (本单提案) | 10 | 10 (1,2,3,4,5,6,7,8,9,10) | ✅ 10 == 10 |
| 本清单总行数 | — | **80** | CHG_BOARD 65 / MAIN_PCB 4 / HINGE 11 |

---

## 8. 未决项与待决清单

| # | 缺什么 | 谁能给 | 什么时候 | 影响哪一条 |
|---|---|---|---|---|
| **待决-1** | **要不要上 TPS25730 (PD)?** —— 上就必须解决 VIN_3V3 的 3.3V 来源 (加 LDO 还是走 datasheet 的 "VBUS LDO" 路径, **datasheet 无该接法示例**) | **项目总工拍板** + (若走 VBUS LDO 路径) **TI 技术支持** | 本单出规格前 (已给推荐: **不上**) | §3 全部 |
| **待决-2** | `J_CHG` pin map (10p 提案) + 电池位置锁死 | **项目总工** (+ 结构总工复核 10p 堆叠) | **打样前 (不可逆)** | §5.2 / §7 全部跨铰链行 |
| **待决-3** | BQ25896 的 I2C 跨不跨铰链 | **项目总工** | 落 P10 前 | §2.8 / §3.3 |
| **待原厂-1** | **KILIM 在低电流档 (1.0A) 的 trim 值** —— datasheet 只在 "IINMAX=1.5A" 工况点给 320/355/390 AΩ, 低电流档是否同值未给 | **TI 技术支持** (BQ25896) | 投板前 | §2.4 (`R_ILIM` 取值精度) |
| **待原厂-2** | **SYS 脚悬空 (不接 20µF) 是否影响 BATFET 通路 / 充电环路** | **TI 技术支持** | 投板前 | §2.6 (`C_SYS` DNP 决策) |
| **待原厂-3** | 100µF 体电容放在 VBUS 脚上游 vs 全部放 PMID, TI 是否认可 (datasheet 只说 1µF@VBUS + 其余@PMID) | **TI 技术支持** | 投板前 | §4.2 |
| **待原厂-4** | TS 下臂接 **GND** 还是接**电芯负极 (BAT−)** —— datasheet 原文是 GND, 但很多设计接 BAT− | **TI 技术支持** | 投板前 | §2.5 |
| **待选型-1** | Type-C 16p 母座**具体型号 + PCB 焊盘图** (4 脚插板孔位) | **厂商询价 (经项目总工)** | 备料前 | §1.1 |
| **待选型-2** | ESD 阵列型号 (5-6 通道, D+/D− ≤1pF, CC/VBUS ≤3pF) | **厂商询价 (经项目总工)** | 备料前 | §4.1 |
| **待选型-3** | π 滤波磁珠 (≥2A, DCR ≤50mΩ) + `D_TVS_VBUS` (5V 级 TVS) | **厂商询价 (经项目总工)** | 备料前 | §4.2 / §4.3 |
| **待选型-4** | 电感 2.2µH (Isat ≥1.5A, DCR ≤50mΩ) | **厂商询价 (经项目总工)** | 备料前 | §2.3 |
| **待选型-5** | ESD 阵列 VRWM 档: ≥24V (为将来上 PD 留后路) vs 5-6V (钳位更低, 当前 5V 足够) | **项目总工拍板** | 投板前 | §4.1 |
| ~~待复算-1~~ ✅ | **ISS-091** 已闭环 (10-28): 铰链段载流/压降/发热核算完成 → **定 390Ω**, 300Ω 判死 | **结构总工** | 已闭环 | §2.4 (`R_ILIM` = 390Ω) |
| **待改-1** | `HW/INTERFACE_TABLE.md` §4.2 / §4.4: BQ25896 的 I2C 地址 **0x12 → 0x6B** (datasheet 原文) | 项目总工 (本单只提规格, 不改文件) | 下轮 | §2.9 |
| **待改-2** | 现行网表 `R_NTC_BAT` / `R_TS_PULL` 的**板别与接法** (见 §2.5 注) | 项目总工 (落 P10 时改) | 落 P10 时 | §2.5 |
| **待改-3** | 现行网表 P1 里 **SYS / SYS_PCB / DC-DC / LDO 共 22 行被标成 `board=CHG_BOARD`**, 但按 V1.2 它们全在**镜脚主 PCB** | 项目总工 (生成器 board 列) | 落 P10 时 | 备料/装配口径 |

---

## 9. 证据分级汇总

| 关键结论 | 等级 | 依据 |
|---|---|---|
| Type-C 16p 物理脚位 (A/B 24 位置 + 16 触点) | **[官方]** | USB Type-C Spec R2.0 (usb.org, 2019-08) Table 3-5 |
| D+/D− 双份并联走线 **≤3.5mm** | **[官方]** | 同上 Table 3-5 Note 2 |
| SBU (A8/B8) **不接** | **[官方]** | 同上 Table 3-5 Note 3 |
| Rd = **5.1kΩ ±20%** | **[官方]** | 同上 §4.x / §5.x |
| 源端 Rp 56k/22k/10k → 500mA/1.5A/3.0A | **[官方]** | 同上 Table 4-24 |
| BQ25896 引脚表 (1-24) | **[官方]** | TI BQ25896 datasheet §7 + 第 5 页 Pin Configuration 图 (已渲染图片逐字核对) |
| BQ25896 I2C 地址 **0x6B** | **[官方]** | 同上 §9.2.16.5 |
| BQ25896 **REG04 复位默认 ICHG = 2048mA** | **[官方]** | 同上 REG04 Table 10 |
| BQ25896 REG00 复位默认 IINLIM = 500mA | **[官方]** | 同上 REG00 Table 6 |
| ILIM: IINMAX = KILIM/RILIM, ILIM 脚稳在 0.8V | **[官方]** | 同上 Pin Functions (pin10) |
| 输入去耦: 1µF@VBUS, 其余@PMID | **[官方]** | 同上 pin1/pin23 说明 |
| 输出电容 ≥20µF + 1µH 起步 (环路稳定) | **[官方]** | 同上 §10.2.2.3 |
| REGN = 5.0V (4.8-5.5V), 4.7µF 去耦 | **[官方]** | 同上 §8.5 / pin22 说明 |
| TS 分压 RT1=5.24k / RT2=30.31k / 103AT | **[官方]** | 同上 Equation 2 (原文给的解) |
| TS 阈值 V(T1)=73.25% / V(T5)=34.375% of REGN | **[官方]** | 同上 §8.5 |
| TS 分压复算验证 (0°C→73.26%, 60°C→34.40%) | **[推算·可复算]** | 本单自算 (公式见 §2.5), B6 可复现 |
| TPS25730: VIN_3V3 3.0-3.6V (绝对最大 4V), QFN-38 4×4mm, 内部 dead-battery Rd, ADCIN 配 5V/2A | **[官方]** | TI TPS25730 datasheet §6.1/§6.5/§5/§8.3.11-13 |
| Type-C 座外形 / 开孔 / 沉板深度 / 寿命 | **[官方·厂商页]** | `HW/POWER_IC_SELECTION.md` §3.5 (航宏) —— 本单只转引 |
| 承力柱 ≥2 + 限位台阶 / 壁厚 ≥1.5mm / 开孔 9.5×3.6 / 热隔离 ≥5mm | **[官方·结构]** | `MECH/USB_HINGE_STRUCTURE.md` §5.2 F-4/F-5, §7 —— 本单只转引 |
| `R_ILIM` = 390Ω → IIN 0.82-1.00A → ICHG ~0.67-0.82A | **[推算·可复算]** | 公式见 §2.4 / §3.4, B6 可复现 |
| 电感纹波 IRIPPLE = 0.29A @ 2.2µH | **[推算·可复算]** | datasheet §10.2.2.1 公式, B6 可复现 |
| 铰链载流余量 (场景 ①-⑥) | **[推算]** | §3.4 表, 假设 VBAT=3.7V / η=90% |
| 充电板 25×10×0.8mm / M1.2 固定 + 铝屏蔽罩 | **[推算]** | `MECH/MECH_BUDGET.md` §1.3 M3 —— 转引 |
| ESD 阵列通道数 / 容值 / VRWM | **[推算]** | `HW/POWER_IC_SELECTION.md` §3.5 (EMC R-03) —— 转引 |
| Type-C 座具体型号 / ESD 阵列型号 / 磁珠 / 电感 / TVS 型号 | **[0数据]** | 厂商询价走项目总工 (未联系任何供应商) |
| 单价 / 交期 (BQ25896, TPS25730) | **[0数据]** | 同上 |

---

## 10. 自证复现命令 (B6)

```bash
cd projects/smart_glasses

# (1) 官方原件: 三份 datasheet / 规范 (全部 ti.com + usb.org)
mkdir -p /tmp/chg && cd /tmp/chg
curl -sSL -o bq25896.pdf   https://www.ti.com/lit/ds/symlink/bq25896.pdf
curl -sSL -o tps25730.pdf  https://www.ti.com/lit/ds/symlink/tps25730.pdf
curl -sSL -o usbc_spec.pdf "https://www.usb.org/sites/default/files/USB%20Type-C%20Spec%20R2.0%20-%20August%202019.pdf"
for f in bq25896 tps25730 usbc_spec; do pdftotext -layout $f.pdf $f.txt; done
file bq25896.pdf tps25730.pdf usbc_spec.pdf   # 校验: 三份都是 PDF (不是 404 页)

# (2) USB-IF Type-C 16p 脚位表 + 三条 Note (官方原文)
grep -n -A 40 "Table 3-5 USB Type-C Receptacle Interface Pin Assignments" /tmp/chg/usbc_spec.txt | head -60
grep -n "maximum shorting trace length should not exceed 3.5 mm" /tmp/chg/usbc_spec.txt
grep -n "shall be not connected unless required" /tmp/chg/usbc_spec.txt

# (3) USB-IF 源端电流表 (Rp 56k/22k/10k)
grep -n -A 12 "Table 4-24 Source CC Termination" /tmp/chg/usbc_spec.txt

# (4) BQ25896 引脚功能表 (1-24)
grep -n -A 120 "Pin Functions" /tmp/chg/bq25896.txt | head -130

# (5) BQ25896 关键寄存器默认值 (ICHG 复位 2048mA / IINLIM 复位 500mA)
grep -n -A 20 "Table 10. REG04" /tmp/chg/bq25896.txt
grep -n -A 20 "Table 6. REG00"  /tmp/chg/bq25896.txt

# (6) BQ25896 I2C 地址 0x6B
grep -n "I2C Address\|Slave Address" /tmp/chg/bq25896.txt | head

# (7) ILIM 公式与 KILIM 公差
grep -n "KILIM" /tmp/chg/bq25896.txt | head

# (8) TS 分压 (Equation 2) 与阈值
grep -n -B2 -A 20 "RT2 =" /tmp/chg/bq25896.txt | head -40
grep -n "V(T1)\|V(T5)" /tmp/chg/bq25896.txt | head

# (9) TPS25730: VIN_3V3 电压窗 / 封装 / ADCIN 电流配置表
grep -n "VIN_3V3" /tmp/chg/tps25730.txt | head
grep -n -A 20 "Table 8-6. ADCIN3 & ADCIN4 Sink Current Configuration" /tmp/chg/tps25730.txt | head -30

# (10) 本单的关键复算 (TS 分压 + ILIM + 纹波) —— 一条命令跑完
python3 - <<'PY'
VREGN=5.0; RT1=5240.0; RT2=30310.0
def vts(rth):
    par=1/(1/rth+1/RT2); return VREGN*par/(RT1+par)
print("TS @0C  =", round(vts(27280),4), "V =", round(vts(27280)/VREGN*100,2), "%  (datasheet V(T1)=73.25%)")
print("TS @60C =", round(vts(3020),4),  "V =", round(vts(3020)/VREGN*100,2),  "%  (datasheet V(T5)=34.375%)")
for r in (390,300,260):
    lo,ty,hi = 320/r, 355/r, 390/r
    print(f"R_ILIM={r} -> IINMAX {lo:.2f}/{ty:.2f}/{hi:.2f} A -> ICHG~{lo*0.822:.2f}/{ty*0.822:.2f}/{hi*0.822:.2f} A")
VBUS,VBAT,fs,L = 5.0,3.7,1.5e6,2.2e-6; D=VBAT/VBUS
print("IRIPPLE =", round(VBUS*D*(1-D)/(fs*L),3), "A @2.2uH ;", round(VBUS*D*(1-D)/(fs*1e-6),3), "A @1.0uH")
PY

# (11) 本规格 §7 连接清单的行数与板别分布
awk '/^```csv/{f=1;next} /^```$/{if(f){f=0}} f' HW/CHARGE_BOARD_SPEC.md | grep -c '^P10,'
awk '/^```csv/{f=1;next} /^```$/{if(f){f=0}} f' HW/CHARGE_BOARD_SPEC.md | grep '^P10,' | awk -F, '{print $NF}' | sort | uniq -c
```

---

## 11. 变更影响面 (本单**没有**改任何生成物, 以下是 PM 落 P10 时要动的清单)

| 生成物 | 要动什么 |
|---|---|
| `state/gen_netlist.py` | 新增 **P10 页** (§7 的 80 行); 修 `J_TYPE_C` GND 脚 (A1+A12 → A1+A12+B1+B12) + 补 SBU 两行; 修 `R_NTC_BAT`/`R_TS_PULL` 的板别与接法; 修 P1 里 22 行 SYS/DC-DC/LDO 的 `board` 列 (CHG_BOARD → MAIN_PCB) |
| `state/gen_schematic_pages.py` | 新增 P10 页叙述 (本页 §0-§6 的判断可直接搬) |
| `HW/netlist_v1.csv` / `HW/SCHEMATIC_V1.md` / `HW/BOM_v1.csv` | **由生成器产出, 不手改** |
| `HW/INTERFACE_TABLE.md` | §4.2 / §4.4 的 BQ25896 地址 0x12 → **0x6B**; `J_CHG` pin map 段 |
| `HW/BOM_v1.csv` | 充电板 BOM 必须明确 **不含** BQ2970 / MOS / 电池 (§4.4) |

---

*文档结束。生成于 2026-10-27, 起草 hw-lead (器件级规格), 待项目总工审校。*
