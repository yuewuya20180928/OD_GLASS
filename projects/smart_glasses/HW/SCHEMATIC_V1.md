# HW/SCHEMATIC_V1.md —— ARS45 硬件原理图 V1 (8 页图页)
> **生成方式**: 器件表由 `state/gen_schematic_pages.py` 从 `HW/netlist_v1.csv` **机械生成** (不会与 netlist 漂移); 每页叙述是**项目总工的判断** (写在生成脚本的 NARRATIVE 里)。
> **本版不是投板文件** —— SoC 侧球位图未回 (原厂, 第 5 天), 全部写成 `SoC[TBD-01].<信号>` 占位; 原厂回信后**只填球号 + 改 TBD 项**即可进 PCB。
> **门禁**: `python3 state/check_netlist.py` (12 条机械判据, 项目总工的验收器) + 本文件的 8 页完整性由
> `grep -o '^## P[0-9]' HW/SCHEMATIC_V1.md | sort -u` 机械核对。
> **相关**: 图纸规格 `HW/SCHEMATIC_V1_SPEC.json` · netlist `HW/netlist_v1.csv` · KiCad 可导入 `HW/netlist_v1.net` ·
> 顶层接口 `HW/SCHEMATIC_L1.md` · 连接表 `HW/INTERFACE_TABLE.md` · 查证结果 `HW/ONLINE_FINDINGS_2026-10-26.md`
---

## P1 电源树
> 13 电源域 + Type-C 充电链 + 3 路 LDO + 2 路 DC-DC

### 功能块与判断
**这张页是整个方案的电源账, 也是散热账的起点。**

- 电源链: Type-C 5V → ESD + π 滤波 → `VBUS_5V` (2.0A) → 电池充放 (BQ25896 + BQ2970 + 2×MOS) → `BAT` → `SYS` (3.0-4.2V, 0.55A 上限) → 2 路 DC-DC (TPS62130A) + 6 路 LDO (TPS7A20 系列) 分出 13 条轨。
- ★**R-F1 硬伤已裁决**: `SYS` 下限 3.0V 与 3.3V 轨的 dropout (110mV typ [官方]) 冲突 → 放电末段 12-15% 电量时 3.3V 轨失效 = **用��快没电突然黑屏**。**基线方案: UVP 抬到 3.5V + 3.3V 改由 TPS62130A 供** (代价 12-15% 容量不可用 → 电池容量与续航口径要重算)。第三条路 (更低 dropout 的 LDO / IO 轨直吃 SYS / 加 buck-boost) 正在评估 (ISS-067)。
- ★**V_CORE 上界按 1.0V** (网上查证: 工作电压范围 0.65-1V, DVFS [媒体·百科]) → DC-DC 输出范围与压差核算要覆盖 1.0V, 不是我们原假设的 0.9V。
- **散热账**: 满载镜腿内发热量 0.90W → 皮肤侧 **80.1°C** (镜腿内主口径) / 96.1°C (整机上界), vs ISO 13732-1 的 43°C 红线 → **贴皮肤镜腿只能承受 0.15-0.2W**。⇒ 这页的每个电流数字都要跟"按需触发"口径一起看, 不然整机方案会被温度否掉。
- **[待原厂]**: 各电源域的**标称电压 / 典型电流 / 最大电流 / 上电时序 / 是否需外部 LDO** (TBD-02)。`V_CORE` 与 `V_SOC_IO` 的电压现在都还是待定 → DC-DC 只是"IC 可画, 电压待定"。

### 器件表 (28 行 netlist 记录)
| net | 节点1 | 节点2 | 位号 | 值 | 类型 | DNP | 证据 | TBD | 说明 |
|---|---|---|---|---|---|---|---|---|---|
| VBUS_5V | J_TYPE_C pin1 | D_ESD_TC | RAIL_VBUS_5V | 5.0V ±5% | RAIL | 必装 | [推算] |  | 电源域: 目标 5.0V ±5% / 最大电流 2.0A (PD 5V/2A); SoC 侧球位号 TBD-01 |
| VBUS_5V | FB_VBUS | TP_VBUS | FB_VBUS | π 滤波磁珠 [待选型] | L | 必装 | [推算] |  | [VBUS_5V] VBUS 入口 π 滤波位 (值随充电 IC 稳定性定) |
| VBUS_5V_F1 | FB_VBUS | C_VBUS_IN | C_VBUS_IN | [待选型] 10µF | C | DNP | [推算] |  | [VBUS_5V_F1] π 滤波输入电容位 (值待充电 IC 定) |
| VBUS_5V_CHG | C_VBUS_IN | C_VBUS_OUT | C_VBUS_OUT | [待选型] 100µF | C | DNP | [推算] |  | [VBUS_5V_CHG] π 滤波电容 (后级)位 (BQ25896 建议 ≥100µF) |
| VBUS_5V_CHG | U_CHG | NET_VBUS_5V_CHG | U_CHG | BQ25896 | IC | 必装 | [官方] |  | [VBUS_5V_CHG] 1A 单节锂电充电 IC (TI) |
| GND | C_VBUS_OUT | GND | C_VBUS_OUT | [待选型] 100µF | C | DNP | [推算] |  | π 滤波电容 (后级) 地端 |
| BAT | RAIL_BAT | U_BATPROT | RAIL_BAT | 4.2V 满 / 3.0V 截止 | RAIL | 必装 | [官方] |  | 电源域: 目标 4.2V 满 / 3.0V 截止 / 最大电流 1.0-1.5A 充电; SoC 侧球位号 TBD-01 |
| BAT | TP_BAT | BAT_432243 | TP_BAT | 测试点 | TP | 必装 | [推算] |  | [BAT] 电池电压 (BQ25896 BAT 脚) |
| SYS | RAIL_SYS | U_BATPROT | RAIL_SYS | 3.0-4.2V | RAIL | 必装 | [推算] |  | 电源域: 目标 3.0-4.2V / 最大电流 0.55A (330mA×1.5 + 瞬态); SoC 侧球位号 TBD-01 |
| SYS | TP_SYS | J_CHG pin1 | TP_SYS | 测试点 | TP | 必装 | [推算] |  | [SYS] 系统 3.7V 主轨 |
| V_CORE | RAIL_V_CORE | U_DCDC_VCORE | RAIL_V_CORE | [待原厂] (典型 0.8-0.9V) | RAIL | 必装 | [待原厂] | TBD-02 | 电源域: 目标 [待原厂] (典型 0.8-0.9V) / 最大电流 ≥2.0A; SoC 侧球位号 TBD-01 |
| V_CORE | TP_VCORE | SoC[TBD-01].V_CORE | TP_VCORE | 测试点 + 引线可及 | TP | 必装 | [推算] |  | [V_CORE] SoC 核心轨 |
| V_SOC_IO | RAIL_V_SOC_IO | U_DCDC_VIO | RAIL_V_SOC_IO | [待原厂] (3.3/1.8/1.2V) | RAIL | 必装 | [待原厂] | TBD-02 | 电源域: 目标 [待原厂] (3.3/1.8/1.2V) / 最大电流 ≥1.0A; SoC 侧球位号 TBD-01 |
| V_SOC_IO | TP_VIO | SoC[TBD-01].V_SOC_IO | TP_VIO | 测试点 | TP | 必装 | [推算] |  | [V_SOC_IO] SoC IO 轨 |
| SENSOR_AVDD | RAIL_SENSOR_AVDD | U_LDO_S28 | RAIL_SENSOR_AVDD | 2.8V | RAIL | 必装 | [官方] |  | 电源域: 目标 2.8V / 最大电流 30mA; SoC 侧球位号 TBD-01 |
| SENSOR_AVDD | TP_SENSOR_2V8 | CONN_CAM pin15 | TP_SENSOR_2V8 | 测试点 | TP | 必装 | [推算] |  | [SENSOR_AVDD] sensor AVDD 2.8V (规格名 3V3/1V8/2V8 中的 2.8V) |
| SENSOR_VDD_IO | RAIL_SENSOR_VDD_IO | U_LDO_S18 | RAIL_SENSOR_VDD_IO | 1.8V | RAIL | 必装 | [官方] |  | 电源域: 目标 1.8V / 最大电流 30mA; SoC 侧球位号 TBD-01 |
| SENSOR_VDD_IO | TP_SENSOR_1V8 | CONN_CAM pin16 | TP_SENSOR_1V8 | 测试点 | TP | 必装 | [推算] |  | [SENSOR_VDD_IO] sensor VDD_IO 1.8V |
| SENSOR_CORE | RAIL_SENSOR_CORE | U_LDO_S12 | RAIL_SENSOR_CORE | 1.2V | RAIL | 必装 | [官方] |  | 电源域: 目标 1.2V / 最大电流 50mA; SoC 侧球位号 TBD-01 |
| SENSOR_CORE | TP_SENSOR_1V2 | CONN_CAM pin17 | TP_SENSOR_1V2 | 测试点 | TP | 必装 | [推算] |  | [SENSOR_CORE] sensor CORE 1.2V |
| LIGHT_3V3 | RAIL_LIGHT_3V3 | U_LDO_L33 | RAIL_LIGHT_3V3 | 3.3V | RAIL | 必装 | [推算] | TBD-02 | 电源域: 目标 3.3V / 最大电流 150mA; SoC 侧球位号 TBD-01 |
| LIGHT_3V3 | TP_LIGHT_3V3 | CONN_LIGHT pin27 | TP_LIGHT_3V3 | 测试点 | TP | 必装 | [推算] |  | [LIGHT_3V3] 光机 3.3V 轨 |
| LIGHT_1V8 | RAIL_LIGHT_1V8 | U_LDO_L18 | RAIL_LIGHT_1V8 | 1.8V | RAIL | DNP | [推算] | TBD-02 | 电源域: 目标 [待 JBD] / 最大电流 50mA; SoC 侧球位号 TBD-01 |
| LIGHT_1V8 | TP_LIGHT_1V8 | CONN_LIGHT pin28 | TP_LIGHT_1V8 | 测试点 | TP | DNP | [推算] |  | [LIGHT_1V8] 光机 1.8V 轨, 待 JBD |
| LIGHT_5V | RAIL_LIGHT_5V | CONN_LIGHT pin29 | RAIL_LIGHT_5V | 5.0V | RAIL | DNP | [推算] | TBD-02 | 电源域: 目标 [待 JBD] / 最大电流 50mA; SoC 侧球位号 TBD-01 |
| VDD_3V3_IO | RAIL_VDD_3V3_IO | U_LDO_IO33 | RAIL_VDD_3V3_IO | 3.3V | RAIL | 必装 | [推算] |  |  |
| VDD_1V8_IO | RAIL_VDD_1V8_IO | U_LDO_IO18 | RAIL_VDD_1V8_IO | 1.8V | RAIL | 必装 | [推算] |  |  |
| GND | RAIL_GND | GND | RAIL_GND | 机壳地 / 数字地 (单点汇流) | RAIL | 必装 | [推算] |  | 电源域: 目标 — / 最大电流 —; SoC 侧球位号 TBD-01 |

## P2 SoC 主控
> 低速控制 / ADC 检测 / I2C / FSIN — SoC 侧全部 TBD-01 占位

### 功能块与判断
**SoC 侧的脚全是 TBD 占位 —— 这页是"原厂回信后只填球号就能投板"的关键。**

- SoC 侧节点统一写成 `SoC[TBD-01].<信号名>`: **原厂引脚表/球位图未回 (第 5 天)**, 所以本页**不写一个球号**。
- 本页信号: I2C_A (总线 A, 接 sensor / NTC / 桥接 / 充电 IC) · 充电状态回读 (`CHG_STAT` / `PWR_GOOD` / `VBUS_DET` / `BAT_DET`) · `FSIN` 帧同步 (引到测试点, 若 SoC 无此脚则 DNP) · `ID_DETECT` (焊盘跳线)。
- ★**充电状态读回有兜底**: 即使 SoC 读不到充电 IC 状态, 也有 `TP_CHG_STAT` + `TP_VBUS` → "充电时禁 OD" 门禁不会瞎 (M-CHRG 判未验, 但不至于误判)。
- ★**USB PHY 基本确认存在** (官网智能可穿戴页列 USB 3.0) → `USB_D+/D-` 走 Type-C 这条路**有依据了**; 但版本 (2.0/3.0) 与 PHY 数量仍要问 (影响引脚预算)。
- **[待原厂]**: 引脚表与球位图 (TBD-01) · USB PHY 版本与引脚数 (TBD-10) · 帧同步能否引出/能否输入 (TBD-07 / TBD-13) · I2C 从设备地址是否可配 (TBD-09)。

### 器件表 (24 行 netlist 记录)
| net | 节点1 | 节点2 | 位号 | 值 | 类型 | DNP | 证据 | TBD | 说明 |
|---|---|---|---|---|---|---|---|---|---|
| I2C_A_SCL | SoC[TBD-01].I2C_A_SCL | R_PU_I2CA_SCL | NET_I2C_A_SCL | 上拉 4.7k 到 3.3V (灌 702µA, t_r=2.38µs@100pF) | NET | 必装 | [推算] |  | 方向 双向 (主机); 电平 3.3V; 阻抗 上拉 4.7k 到 3.3V (灌 702µA, t_r=2.38µs@100pF); 连接 SoC [待原厂] + sensor/ |
| I2C_A_SCL | CONN_CAM pin13 | TP_I2CA_SCL | TP_I2CA_SCL | 测试点 | TP | 必装 | [推算] |  | [I2C_A_SCL] I2C_A 时钟 |
| I2C_A_SDA | SoC[TBD-01].I2C_A_SDA | R_PU_I2CA_SDA | NET_I2C_A_SDA | 上拉 4.7k 到 3.3V | NET | 必装 | [推算] |  | 方向 双向 (主机); 电平 3.3V; 阻抗 上拉 4.7k 到 3.3V; 连接 同上; 测试点 TP_I2CA_SDA |
| I2C_A_SDA | CONN_CAM pin14 | TP_I2CA_SDA | TP_I2CA_SDA | 测试点 | TP | 必装 | [推算] |  | [I2C_A_SDA] I2C_A 数据 |
| VDD_3V3_IO | R_PU_I2CA_SCL | RAIL_VDD_3V3_IO | R_PU_I2CA_SCL | 4.7k ±1% | R | 必装 | [推算] |  | [VDD_3V3_IO] I2C_A 上拉 (规格: 4.7k 到 3.3V) |
| VDD_3V3_IO | R_PU_I2CA_SDA | RAIL_VDD_3V3_IO | R_PU_I2CA_SDA | 4.7k ±1% | R | 必装 | [推算] |  | [VDD_3V3_IO] I2C_A 上拉 |
| VBUS_DET_RAW | RAIL_VBUS_5V | R_VBUS_DET_1 | R_VBUS_DET_1 | 1M ±1% | R | 必装 | [推算] |  | [VBUS_DET_RAW] VBUS 分压上臂 |
| VBUS_DET | R_VBUS_DET_1 | R_VBUS_DET_2 | NET_VBUS_DET | 1M+1M 分压 + 100nF | NET | 必装 | [推算] |  | 方向 充电板→SoC; 电平 0-3.3V (分压); 阻抗 1M+1M 分压 + 100nF; 连接 Type-C VBUS → ADC; 测试点 TP_VBUS |
| VBUS_DET | C_DET_VBUS | J_CHG pin2 | C_DET_VBUS | 100nF ±10% | C | 必装 | [推算] |  | [VBUS_DET] ADC 滤波 |
| VBUS_DET | SoC[TBD-01].VBUS_DET | NET_VBUS_DET | NET_VBUS_DET | 1M+1M 分压 + 100nF | NET | 必装 | [推算] |  | [VBUS_DET] 附加节点 (同 net) |
| GND | R_VBUS_DET_2 | GND | R_VBUS_DET_2 | 1M ±1% | R | 必装 | [推算] |  | 分压下臂 地端 |
| GND | C_DET_VBUS | GND | C_DET_VBUS | 100nF ±10% | C | 必装 | [推算] |  | ADC 滤波电容 地端 |
| BAT_DET_RAW | RAIL_BAT | R_BAT_DET_1 | R_BAT_DET_1 | 1M ±1% | R | 必装 | [推算] |  | [BAT_DET_RAW] BAT 分压上臂 |
| BAT_DET | R_BAT_DET_1 | R_BAT_DET_2 | NET_BAT_DET | 1M+1M 分压 + 100nF | NET | 必装 | [推算] |  | 方向 充电板→SoC; 电平 0-3.3V (分压); 阻抗 1M+1M 分压 + 100nF; 连接 电池 BAT → ADC; 测试点 TP_BAT |
| BAT_DET | C_DET_BAT | J_CHG pin3 | C_DET_BAT | 100nF ±10% | C | 必装 | [推算] |  | [BAT_DET] ADC 滤波 |
| BAT_DET | SoC[TBD-01].BAT_DET | NET_BAT_DET | NET_BAT_DET | 1M+1M 分压 + 100nF | NET | 必装 | [推算] |  | [BAT_DET] 附加节点 (同 net) |
| GND | R_BAT_DET_2 | GND | R_BAT_DET_2 | 1M ±1% | R | 必装 | [推算] |  | 分压下臂 地端 |
| GND | C_DET_BAT | GND | C_DET_BAT | 100nF ±10% | C | 必装 | [推算] |  | ADC 滤波电容 地端 |
| CHG_STAT | U_CHG | R_PU_CHG_STAT | NET_CHG_STAT | 单端 | NET | 必装 | [推算] |  | 方向 充电IC→SoC; 电平 3.3V (开漏); 阻抗 单端; 连接 BQ25896 STAT 脚 → SoC GPIO; 测试点 TP_CHG_STAT |
| CHG_STAT | J_CHG pin4 | SoC[TBD-01].CHG_STAT | NET_CHG_STAT | 单端 | NET | 必装 | [推算] |  | [CHG_STAT] 附加节点 (同 net) |
| PWR_GOOD | U_CHG | R_PU_PG | NET_PWR_GOOD | 单端 | NET | 必装 | [推算] |  | 方向 充电IC→SoC; 电平 3.3V (开漏); 阻抗 单端; 连接 BQ25896 PG 脚 → SoC GPIO; 测试点 TP_PG |
| PWR_GOOD | J_CHG pin5 | SoC[TBD-01].PWR_GOOD | NET_PWR_GOOD | 单端 | NET | 必装 | [推算] |  | [PWR_GOOD] 附加节点 (同 net) |
| VDD_3V3_IO | R_PU_CHG_STAT | RAIL_VDD_3V3_IO | R_PU_CHG_STAT | 10k ±1% | R | 必装 | [推算] |  | [VDD_3V3_IO] BQ25896 STAT 开漏上拉 |
| VDD_3V3_IO | R_PU_PG | RAIL_VDD_3V3_IO | R_PU_PG | 10k ±1% | R | 必装 | [推算] |  | [VDD_3V3_IO] BQ25896 PG 开漏上拉 |

## P3 启动存储
> ★ 只留焊盘位 + 串阻位, 不画存储芯片 (内置 DRAM 已确认, 启动介质必然外挂)

### 功能块与判断
**这一页故意"空着" —— 但它是有依据的空, 不是漏画。**

- ★**官网已确认 ARS45 内置 512MB DRAM 且已量产** (另有 ARS48 1GB 已送样 / ARS41 128MB Q3 送样) → **启动介质必然外挂**。所以本页只画 **4 条 SPI 信号 + 串阻位 + 焊盘位**, **不画存储芯片**。
- 两种外挂形态的代价差别很大: **SPI-NOR** (小, 省板宽, 兆易创新是酷芯微第二大股东 → 生态顺) vs **eMMC** (容量大但吃板面积 → 我们评估板宽 12→15mm) ⇒ **这个选择直接顶到板宽**, 而板宽又被官网"宽度≤8mm"卡着 (见 §(1.25))。
- 串阻位 (0Ω) 的作用: 让 SoC 的启动介质可以换 NOR/eMMC 而**不改板** —— 两种都留位, 装配时决定。
- **[待原厂]**: 外挂是 SPI-NOR 还是 eMMC (TBD-06) · 挂在哪个接口 (SPI 控制器? eMMC/NAND 控制器?) (TBD-11) · 上电时序要求 (TBD-12)。

### 器件表 (10 行 netlist 记录)
| net | 节点1 | 节点2 | 位号 | 值 | 类型 | DNP | 证据 | TBD | 说明 |
|---|---|---|---|---|---|---|---|---|---|
| SPI_SCLK | SoC[TBD-01].SPI_SCLK | R_SER_SPI_SCLK | NET_SPI_SCLK | 0Ω (串阻位) | NET | 必装 | [待原厂] | TBD-06 | 启动存储: 只留焊盘位 + 串阻位, 不画存储芯片 (内置 boot storage 还是外挂 SPI-NOR/eMMC 未确认; 外挂 eMMC 方案 PCB 面积 +25% 且 |
| SPI_SCLK_BOOT | R_SER_SPI_SCLK | J_BOOT1 pin1 | R_SER_SPI_SCLK | 0Ω (串阻位) | R | 必装 | [待原厂] | TBD-06 | [SPI_SCLK_BOOT] SPI SCLK 串阻位 (0Ω 调试用) |
| SPI_CSn | SoC[TBD-01].SPI_CSn | R_SER_SPI_CSn | NET_SPI_CSn | 0Ω (串阻位) | NET | 必装 | [待原厂] | TBD-06 | 启动存储: 只留焊盘位 + 串阻位, 不画存储芯片 (内置 boot storage 还是外挂 SPI-NOR/eMMC 未确认; 外挂 eMMC 方案 PCB 面积 +25% 且 |
| SPI_CSn_BOOT | R_SER_SPI_CSn | J_BOOT1 pin2 | R_SER_SPI_CSn | 0Ω (串阻位) | R | 必装 | [待原厂] | TBD-06 | [SPI_CSn_BOOT] SPI CS 串阻位 |
| SPI_MOSI | SoC[TBD-01].SPI_MOSI | R_SER_SPI_MOSI | NET_SPI_MOSI | 0Ω (串阻位) | NET | 必装 | [待原厂] | TBD-11 | 启动存储: 只留焊盘位 + 串阻位, 不画存储芯片 (内置 boot storage 还是外挂 SPI-NOR/eMMC 未确认; 外挂 eMMC 方案 PCB 面积 +25% 且 |
| SPI_MOSI_BOOT | R_SER_SPI_MOSI | J_BOOT1 pin3 | R_SER_SPI_MOSI | 0Ω (串阻位) | R | 必装 | [待原厂] | TBD-11 | [SPI_MOSI_BOOT] SPI MOSI 串阻位 |
| SPI_MISO | SoC[TBD-01].SPI_MISO | R_SER_SPI_MISO | NET_SPI_MISO | 0Ω (串阻位) | NET | 必装 | [待原厂] | TBD-11 | 启动存储: 只留焊盘位 + 串阻位, 不画存储芯片 (内置 boot storage 还是外挂 SPI-NOR/eMMC 未确认; 外挂 eMMC 方案 PCB 面积 +25% 且 |
| SPI_MISO_BOOT | R_SER_SPI_MISO | J_BOOT1 pin4 | R_SER_SPI_MISO | 0Ω (串阻位) | R | 必装 | [待原厂] | TBD-11 | [SPI_MISO_BOOT] SPI MISO 串阻位 |
| VDD_3V3_IO | J_BOOT1 pin5 | RAIL_VDD_3V3_IO | J_BOOT1 | 启动存储焊盘位 (4p 信号 + 2p 电源/GND 预留) | CONN | 必装 | [待原厂] | TBD-06 | [VDD_3V3_IO] ★内置 boot storage 还是外挂 SPI-NOR/eMMC 未确认 (Q19) -> 只留焊盘位; pin5/pin6 预留外挂 SPI-NOR |
| GND | J_BOOT1 pin6 | GND | J_BOOT1 | 启动存储焊盘位 (4p 信号 + 2p 电源/GND 预留) | CONN | 必装 | [待原厂] | TBD-06 | 焊盘位 GND 预留 (外挂 SPI-NOR 用) |

## P4 显示双出口
> DSI 原生 / 桥接 互斥 8 个 0Ω 位; 走鹃Ⅱ 原生 800×600 (上采样 ×1.25)

### 功能块与判断
**这一页决定要不要多一颗桥接芯片 (100-300mW + 4-8 周采购 + PCB 面积)。**

- 走鹃Ⅱ 是 **800×600 原生** (官网+LEDinside+EET 三源一致) → 我们的链路是 **ISP 640×480 → OD letterbox → 640×640 → 显示上采样 ×1.25 → 800×600**, 正好对上; 老板锁的显示分辨率 800×600 与光引擎原生一致 ✅。
- ★**30° 是对角 FOV** (自洽校验: 对角 1000px ÷ 30° = 33.3 PPD) → 显示端原生角分辨率 0.030°/px 对角。显示端映射 (采集 120° → 显示 30°) 是 **Q23** 待老板拍板: (a) 全幅压进 30° (看得广但糊) (b) 30° 中心窗口 (看得清但窄, 但显示侧要 crop)。
- ★**8 个 0Ω 位 = 两条互斥路**: `R_SEL_*` (SoC 原生 DSI TX 直连光机) 与 `BR_*` (经桥接芯片) **不得同时装** (否则两个驱动源打架) → BOM 分两组列, 由装配决定。`R_SEL_D2/D3` 与 `R_TERM_*` 永远 DNP (2 lane 不够时再装; 端接 100Ω 对地, 0402 手工可补)。
- ★**显示 TX 的新证据**: 官网原文 "支持端到端 **3-4ms** 超低延迟显示链路" + "多屏异显" → **芯片内部确有显示输出通路**; 官网另有 "集成 Display Port 1.4" (但**没写方向**, 而媒体写 DP1.4 RX) ⇒ **推断: 极可能有显示 TX, 具体接口待定** → 所以**双出口必须都留**。
- **[待原厂]**: 有无 MIPI-DSI TX / DP1.4 是否有 TX / 能否同时工作 / lane 数与速率 (TBD-04) · DSI DDC I2C 是否独立于 SoC 通用 I2C (TBD-09)。

### 器件表 (46 行 netlist 记录)
| net | 节点1 | 节点2 | 位号 | 值 | 类型 | DNP | 证据 | TBD | 说明 |
|---|---|---|---|---|---|---|---|---|---|
| DSI_D0_CK_P_SRC | SoC[TBD-01].DSI_TX_CK_P | R_SEL_CK_P | NET_DSI_D0_CK_P_SRC | 100Ω ±10% | NET | 必装 | [推算] | TBD-04 | 方向 SoC(或桥接)→光机; 电平 1.2V CML; 阻抗 100Ω ±10%; 连接 CONN_LIGHT pin3 + R_SEL_CK 0Ω; 测试点 TP_DSI_CK |
| DSI_D0_CK_P | R_SEL_CK_P | CONN_LIGHT pin3 | R_SEL_CK_P | 0Ω | R | 必装 | [官方] | TBD-04 | [DSI_D0_CK_P] 显示双出口选择位 (方案A 装 0Ω / 方案B DNP) — ★规格位 R_SEL_* 必须拆 P/N 两颗, 单颗 0Ω 会把差分对短接 |
| DSI_BR_CK_P_SRC | U_BRIDGE pin1 | BR_CK_P | BR_CK_P | 0Ω | R | DNP | [官方] | TBD-04 | [DSI_BR_CK_P_SRC] 方案B 桥接位 (方案A DNP / 方案B 装 0Ω) — ★与 R_SEL_* 互斥, 不得同装 |
| DSI_BR_CK_P | BR_CK_P | CONN_LIGHT pin21 | BR_CK_P | 0Ω | R | DNP | [官方] | TBD-04 | [DSI_BR_CK_P] 方案B 桥接位 (方案A DNP / 方案B 装 0Ω) — ★与 R_SEL_* 互斥, 不得同装 |
| DSI_D0_CK_N_SRC | SoC[TBD-01].DSI_TX_CK_N | R_SEL_CK_N | NET_DSI_D0_CK_N_SRC | 100Ω ±10% | NET | 必装 | [推算] | TBD-04 | 方向 SoC(或桥接)→光机; 电平 1.2V CML; 阻抗 100Ω ±10%; 连接 CONN_LIGHT pin4 + R_SEL_CK 0Ω; 测试点 TP_DSI_CK |
| DSI_D0_CK_N | R_SEL_CK_N | CONN_LIGHT pin4 | R_SEL_CK_N | 0Ω | R | 必装 | [官方] | TBD-04 | [DSI_D0_CK_N] 显示双出口选择位 (方案A 装 0Ω / 方案B DNP) — ★规格位 R_SEL_* 必须拆 P/N 两颗, 单颗 0Ω 会把差分对短接 |
| DSI_BR_CK_N_SRC | U_BRIDGE pin2 | BR_CK_N | BR_CK_N | 0Ω | R | DNP | [官方] | TBD-04 | [DSI_BR_CK_N_SRC] 方案B 桥接位 (方案A DNP / 方案B 装 0Ω) — ★与 R_SEL_* 互斥, 不得同装 |
| DSI_BR_CK_N | BR_CK_N | CONN_LIGHT pin22 | BR_CK_N | 0Ω | R | DNP | [官方] | TBD-04 | [DSI_BR_CK_N] 方案B 桥接位 (方案A DNP / 方案B 装 0Ω) — ★与 R_SEL_* 互斥, 不得同装 |
| DSI_D0_D0_P_SRC | SoC[TBD-01].DSI_TX_D0_P | R_SEL_D0_P | NET_DSI_D0_D0_P_SRC | 100Ω ±10% | NET | 必装 | [推算] | TBD-04 | 方向 SoC(或桥接)→光机; 电平 1.2V CML; 阻抗 100Ω ±10%; 连接 CONN_LIGHT pin5 + R_SEL_D0; 测试点 TP_DSI_D0_P |
| DSI_D0_D0_P | R_SEL_D0_P | CONN_LIGHT pin5 | R_SEL_D0_P | 0Ω | R | 必装 | [官方] | TBD-04 | [DSI_D0_D0_P] 显示双出口选择位 (方案A 装 0Ω / 方案B DNP) — ★规格位 R_SEL_* 必须拆 P/N 两颗, 单颗 0Ω 会把差分对短接 |
| DSI_BR_D0_P_SRC | U_BRIDGE pin3 | BR_D0_P | BR_D0_P | 0Ω | R | DNP | [官方] | TBD-04 | [DSI_BR_D0_P_SRC] 方案B 桥接位 (方案A DNP / 方案B 装 0Ω) — ★与 R_SEL_* 互斥, 不得同装 |
| DSI_BR_D0_P | BR_D0_P | CONN_LIGHT pin23 | BR_D0_P | 0Ω | R | DNP | [官方] | TBD-04 | [DSI_BR_D0_P] 方案B 桥接位 (方案A DNP / 方案B 装 0Ω) — ★与 R_SEL_* 互斥, 不得同装 |
| DSI_D0_D0_N_SRC | SoC[TBD-01].DSI_TX_D0_N | R_SEL_D0_N | NET_DSI_D0_D0_N_SRC | 100Ω ±10% | NET | 必装 | [推算] | TBD-04 | 方向 SoC(或桥接)→光机; 电平 1.2V CML; 阻抗 100Ω ±10%; 连接 CONN_LIGHT pin6 + R_SEL_D0; 测试点 TP_DSI_D0_N |
| DSI_D0_D0_N | R_SEL_D0_N | CONN_LIGHT pin6 | R_SEL_D0_N | 0Ω | R | 必装 | [官方] | TBD-04 | [DSI_D0_D0_N] 显示双出口选择位 (方案A 装 0Ω / 方案B DNP) — ★规格位 R_SEL_* 必须拆 P/N 两颗, 单颗 0Ω 会把差分对短接 |
| DSI_BR_D0_N_SRC | U_BRIDGE pin4 | BR_D0_N | BR_D0_N | 0Ω | R | DNP | [官方] | TBD-04 | [DSI_BR_D0_N_SRC] 方案B 桥接位 (方案A DNP / 方案B 装 0Ω) — ★与 R_SEL_* 互斥, 不得同装 |
| DSI_BR_D0_N | BR_D0_N | CONN_LIGHT pin24 | BR_D0_N | 0Ω | R | DNP | [官方] | TBD-04 | [DSI_BR_D0_N] 方案B 桥接位 (方案A DNP / 方案B 装 0Ω) — ★与 R_SEL_* 互斥, 不得同装 |
| DSI_D0_D1_P_SRC | SoC[TBD-01].DSI_TX_D1_P | R_SEL_D1_P | NET_DSI_D0_D1_P_SRC | 100Ω ±10% | NET | 必装 | [推算] | TBD-04 | 方向 SoC(或桥接)→光机; 电平 1.2V CML; 阻抗 100Ω ±10%; 连接 CONN_LIGHT pin7 + R_SEL_D1; 测试点 — |
| DSI_D0_D1_P | R_SEL_D1_P | CONN_LIGHT pin7 | R_SEL_D1_P | 0Ω | R | 必装 | [官方] | TBD-04 | [DSI_D0_D1_P] 显示双出口选择位 (方案A 装 0Ω / 方案B DNP) — ★规格位 R_SEL_* 必须拆 P/N 两颗, 单颗 0Ω 会把差分对短接 |
| DSI_BR_D1_P_SRC | U_BRIDGE pin5 | BR_D1_P | BR_D1_P | 0Ω | R | DNP | [官方] | TBD-04 | [DSI_BR_D1_P_SRC] 方案B 桥接位 (方案A DNP / 方案B 装 0Ω) — ★与 R_SEL_* 互斥, 不得同装 |
| DSI_BR_D1_P | BR_D1_P | CONN_LIGHT pin25 | BR_D1_P | 0Ω | R | DNP | [官方] | TBD-04 | [DSI_BR_D1_P] 方案B 桥接位 (方案A DNP / 方案B 装 0Ω) — ★与 R_SEL_* 互斥, 不得同装 |
| DSI_D0_D1_N_SRC | SoC[TBD-01].DSI_TX_D1_N | R_SEL_D1_N | NET_DSI_D0_D1_N_SRC | 100Ω ±10% | NET | 必装 | [推算] | TBD-04 | 方向 SoC(或桥接)→光机; 电平 1.2V CML; 阻抗 100Ω ±10%; 连接 CONN_LIGHT pin8 + R_SEL_D1; 测试点 — |
| DSI_D0_D1_N | R_SEL_D1_N | CONN_LIGHT pin8 | R_SEL_D1_N | 0Ω | R | 必装 | [官方] | TBD-04 | [DSI_D0_D1_N] 显示双出口选择位 (方案A 装 0Ω / 方案B DNP) — ★规格位 R_SEL_* 必须拆 P/N 两颗, 单颗 0Ω 会把差分对短接 |
| DSI_BR_D1_N_SRC | U_BRIDGE pin6 | BR_D1_N | BR_D1_N | 0Ω | R | DNP | [官方] | TBD-04 | [DSI_BR_D1_N_SRC] 方案B 桥接位 (方案A DNP / 方案B 装 0Ω) — ★与 R_SEL_* 互斥, 不得同装 |
| DSI_BR_D1_N | BR_D1_N | CONN_LIGHT pin26 | BR_D1_N | 0Ω | R | DNP | [官方] | TBD-04 | [DSI_BR_D1_N] 方案B 桥接位 (方案A DNP / 方案B 装 0Ω) — ★与 R_SEL_* 互斥, 不得同装 |
| DSI_D0_D2_P_SRC | SoC[TBD-01].DSI_TX_D2_P | R_SEL_D2_P | NET_DSI_D0_D2_P_SRC | 100Ω ±10% | NET | DNP | [推算] | TBD-04 | 方向 SoC→光机; 电平 1.2V CML; 阻抗 100Ω ±10%; 连接 CONN_LIGHT pin9 + R_SEL_D2 + 100Ω 对地端接; 测试点 — |
| DSI_D0_D2_P_SRC | R_TERM_DSI_D0_D2_P | NET_DSI_D0_D2_P_SRC | R_TERM_DSI_D0_D2_P | 100Ω ±1% | R | DNP | [推算] |  | [DSI_D0_D2_P_SRC] 未用差分对 100Ω 对地端接 (0402, 手工可补装) |
| DSI_D0_D2_P | R_SEL_D2_P | CONN_LIGHT pin9 | R_SEL_D2_P | 0Ω | R | DNP | [官方] | TBD-04 | [DSI_D0_D2_P] 4-lane 预留位 (2-lane 不够时再装) |
| GND | R_TERM_DSI_D0_D2_P | GND | R_TERM_DSI_D0_D2_P | 100Ω ±1% | R | DNP | [推算] |  | 未用差分对 100Ω 对地端接 (未用 lane 才装) |
| DSI_D0_D2_N_SRC | SoC[TBD-01].DSI_TX_D2_N | R_SEL_D2_N | NET_DSI_D0_D2_N_SRC | 100Ω ±10% | NET | DNP | [推算] | TBD-04 | 方向 SoC→光机; 电平 1.2V CML; 阻抗 100Ω ±10%; 连接 CONN_LIGHT pin10/11/12 + 100Ω 对地端接; 测试点 — |
| DSI_D0_D2_N_SRC | R_TERM_DSI_D0_D2_N | NET_DSI_D0_D2_N_SRC | R_TERM_DSI_D0_D2_N | 100Ω ±1% | R | DNP | [推算] |  | [DSI_D0_D2_N_SRC] 未用差分对 100Ω 对地端接 (0402, 手工可补装) |
| DSI_D0_D2_N | R_SEL_D2_N | CONN_LIGHT pin10 | R_SEL_D2_N | 0Ω | R | DNP | [官方] | TBD-04 | [DSI_D0_D2_N] 4-lane 预留位 (2-lane 不够时再装) |
| GND | R_TERM_DSI_D0_D2_N | GND | R_TERM_DSI_D0_D2_N | 100Ω ±1% | R | DNP | [推算] |  | 未用差分对 100Ω 对地端接 (未用 lane 才装) |
| DSI_D0_D3_P_SRC | SoC[TBD-01].DSI_TX_D3_P | R_SEL_D3_P | NET_DSI_D0_D3_P_SRC | 100Ω ±10% | NET | DNP | [推算] | TBD-04 | 方向 SoC→光机; 电平 1.2V CML; 阻抗 100Ω ±10%; 连接 CONN_LIGHT pin10/11/12 + 100Ω 对地端接; 测试点 — |
| DSI_D0_D3_P_SRC | R_TERM_DSI_D0_D3_P | NET_DSI_D0_D3_P_SRC | R_TERM_DSI_D0_D3_P | 100Ω ±1% | R | DNP | [推算] |  | [DSI_D0_D3_P_SRC] 未用差分对 100Ω 对地端接 (0402, 手工可补装) |
| DSI_D0_D3_P | R_SEL_D3_P | CONN_LIGHT pin11 | R_SEL_D3_P | 0Ω | R | DNP | [官方] | TBD-04 | [DSI_D0_D3_P] 4-lane 预留位 (2-lane 不够时再装) |
| GND | R_TERM_DSI_D0_D3_P | GND | R_TERM_DSI_D0_D3_P | 100Ω ±1% | R | DNP | [推算] |  | 未用差分对 100Ω 对地端接 (未用 lane 才装) |
| DSI_D0_D3_N_SRC | SoC[TBD-01].DSI_TX_D3_N | R_SEL_D3_N | NET_DSI_D0_D3_N_SRC | 100Ω ±10% | NET | DNP | [推算] | TBD-04 | 方向 SoC→光机; 电平 1.2V CML; 阻抗 100Ω ±10%; 连接 CONN_LIGHT pin10/11/12 + 100Ω 对地端接; 测试点 — |
| DSI_D0_D3_N_SRC | R_TERM_DSI_D0_D3_N | NET_DSI_D0_D3_N_SRC | R_TERM_DSI_D0_D3_N | 100Ω ±1% | R | DNP | [推算] |  | [DSI_D0_D3_N_SRC] 未用差分对 100Ω 对地端接 (0402, 手工可补装) |
| DSI_D0_D3_N | R_SEL_D3_N | CONN_LIGHT pin12 | R_SEL_D3_N | 0Ω | R | DNP | [官方] | TBD-04 | [DSI_D0_D3_N] 4-lane 预留位 (2-lane 不够时再装) |
| GND | R_TERM_DSI_D0_D3_N | GND | R_TERM_DSI_D0_D3_N | 100Ω ±1% | R | DNP | [推算] |  | 未用差分对 100Ω 对地端接 (未用 lane 才装) |
| I2C_B_SCL | SoC[TBD-01].I2C_B_SCL | R_PU_I2CB_SCL | NET_I2C_B_SCL | 上拉 4.7k, 放主板侧 | NET | 必装 | [推算] | TBD-04 | 方向 双向; 电平 3.3V; 阻抗 上拉 4.7k, 放主板侧; 连接 CONN_LIGHT pin13 → 光机; 测试点 TP_I2CB_SCL |
| I2C_B_SCL | CONN_LIGHT pin13 | NET_I2C_B_SCL | NET_I2C_B_SCL | 上拉 4.7k, 放主板侧 | NET | 必装 | [推算] | TBD-04 | [I2C_B_SCL] 附加节点 (同 net) |
| I2C_B_SDA | SoC[TBD-01].I2C_B_SDA | R_PU_I2CB_SDA | NET_I2C_B_SDA | 上拉 4.7k, 放主板侧 | NET | 必装 | [推算] | TBD-04 | 方向 双向; 电平 3.3V; 阻抗 上拉 4.7k, 放主板侧; 连接 CONN_LIGHT pin14 → 光机; 测试点 TP_I2CB_SDA |
| I2C_B_SDA | CONN_LIGHT pin14 | NET_I2C_B_SDA | NET_I2C_B_SDA | 上拉 4.7k, 放主板侧 | NET | 必装 | [推算] | TBD-04 | [I2C_B_SDA] 附加节点 (同 net) |
| VDD_3V3_IO | R_PU_I2CB_SCL | RAIL_VDD_3V3_IO | R_PU_I2CB_SCL | 4.7k ±1% | R | 必装 | [推算] |  | [VDD_3V3_IO] DSI DDC 上拉 (放主板侧) |
| VDD_3V3_IO | R_PU_I2CB_SDA | RAIL_VDD_3V3_IO | R_PU_I2CB_SDA | 4.7k ±1% | R | 必装 | [推算] |  | [VDD_3V3_IO] DSI DDC 上拉 |

## P5 MIPI-CSI 传感器
> CONN_CAM 40p 跨铰链; 4-lane 预留; AC 耦合 + 对地端接

### 功能块与判断
**传感器侧: 跨铰链的差分对, 全部 100Ω 差分 + AC 耦合位 + 对地端接位。**

- 4-lane CSI: `A-01..A-10` (CK + D0..D3), 其中 **D2/D3 是 DNP (预留 4-lane)** —— 我们只用 1080p60 单路, 2-lane 就够, 但**预留 4-lane 是为了让"以后换高分辨率 sensor"不用改板**。
- 跨铰链是这里最脆的一环: `CONN_CAM` 40p 走铰链 → 阻抗连续性、AC 耦合电容位置、对地端接位置都要跟结构侧的铰链行程对齐 (ISS-065 的结构建议里提了这一条)。
- 传感器电源 3 条轨 (`SENSOR_AVDD` 2.8V / `SENSOR_VDD_IO` 1.8V / `SENSOR_CORE` 1.2V) 由 3 路 TPS7A20 LDO 供, **都在镜框侧** (不进镜腿皮肤路径) → 这也是散热账里"镜腿内发热量 0.90W"能成立的原因。
- ★**传感器选型还锁着 3 件事** (Q16 宽高比 / Q24 准入线 / sensor 必须支持**全幅**输出模式): 裸 1080p 对 OV04C10 就是 ROI 模式 (对角 FOV 120°→85.61°), 违反我们"禁 ROI"的硬约束 → **只有 1080p ROI 模式的 sensor 一票否决**。
- **[待原厂]**: CSI lane 数 / 每 lane 速率 / 电压域 / AC 耦合是否内置 / MCLK 电压 (TBD-03)。

### 器件表 (33 行 netlist 记录)
| net | 节点1 | 节点2 | 位号 | 值 | 类型 | DNP | 证据 | TBD | 说明 |
|---|---|---|---|---|---|---|---|---|---|
| CSI_D0_CK_P_SRC | SoC[TBD-01].CSI_D0_CK_P | C_AC_CSI_D0_CK_P | NET_CSI_D0_CK_P_SRC | 100Ω ±10% | NET | 必装 | [待原厂] | TBD-03 | 方向 SoC→sensor; 电平 1.2V CML [待原厂]; 阻抗 100Ω ±10%; 连接 CONN_CAM 40p (跨铰链) + AC 耦合电容位; 测试点 TP_C |
| CSI_D0_CK_P | C_AC_CSI_D0_CK_P | CONN_CAM pin1 | C_AC_CSI_D0_CK_P | 100nF ±10% | C | 必装 | [推算] | TBD-03 | [CSI_D0_CK_P] AC 耦合电容位 (MIPI 标准 100nF) — 原厂是否内置 AC 耦合未回 (TBD-03); 内置则本位可改 DNP, 未内置必须装 |
| CSI_D0_CK_N_SRC | SoC[TBD-01].CSI_D0_CK_N | C_AC_CSI_D0_CK_N | NET_CSI_D0_CK_N_SRC | 100Ω ±10% | NET | 必装 | [待原厂] | TBD-03 | 方向 SoC→sensor; 电平 1.2V CML [待原厂]; 阻抗 100Ω ±10%; 连接 同上; 测试点 TP_CSI_CK_N |
| CSI_D0_CK_N | C_AC_CSI_D0_CK_N | CONN_CAM pin2 | C_AC_CSI_D0_CK_N | 100nF ±10% | C | 必装 | [推算] | TBD-03 | [CSI_D0_CK_N] AC 耦合电容位 (MIPI 标准 100nF) — 原厂是否内置 AC 耦合未回 (TBD-03); 内置则本位可改 DNP, 未内置必须装 |
| CSI_D0_D0_P_SRC | SoC[TBD-01].CSI_D0_D0_P | C_AC_CSI_D0_D0_P | NET_CSI_D0_D0_P_SRC | 100Ω ±10% | NET | 必装 | [待原厂] | TBD-03 | 方向 SoC→sensor; 电平 1.2V CML [待原厂]; 阻抗 100Ω ±10%; 连接 同上; 测试点 TP_CSI_D0_P |
| CSI_D0_D0_P | C_AC_CSI_D0_D0_P | CONN_CAM pin3 | C_AC_CSI_D0_D0_P | 100nF ±10% | C | 必装 | [推算] | TBD-03 | [CSI_D0_D0_P] AC 耦合电容位 (MIPI 标准 100nF) — 原厂是否内置 AC 耦合未回 (TBD-03); 内置则本位可改 DNP, 未内置必须装 |
| CSI_D0_D0_N_SRC | SoC[TBD-01].CSI_D0_D0_N | C_AC_CSI_D0_D0_N | NET_CSI_D0_D0_N_SRC | 100Ω ±10% | NET | 必装 | [待原厂] | TBD-03 | 方向 SoC→sensor; 电平 1.2V CML [待原厂]; 阻抗 100Ω ±10%; 连接 同上; 测试点 TP_CSI_D0_N |
| CSI_D0_D0_N | C_AC_CSI_D0_D0_N | CONN_CAM pin4 | C_AC_CSI_D0_D0_N | 100nF ±10% | C | 必装 | [推算] | TBD-03 | [CSI_D0_D0_N] AC 耦合电容位 (MIPI 标准 100nF) — 原厂是否内置 AC 耦合未回 (TBD-03); 内置则本位可改 DNP, 未内置必须装 |
| CSI_D0_D1_P_SRC | SoC[TBD-01].CSI_D0_D1_P | C_AC_CSI_D0_D1_P | NET_CSI_D0_D1_P_SRC | 100Ω ±10% | NET | 必装 | [待原厂] | TBD-03 | 方向 SoC→sensor; 电平 1.2V CML [待原厂]; 阻抗 100Ω ±10%; 连接 同上; 测试点 — |
| CSI_D0_D1_P | C_AC_CSI_D0_D1_P | CONN_CAM pin5 | C_AC_CSI_D0_D1_P | 100nF ±10% | C | 必装 | [推算] | TBD-03 | [CSI_D0_D1_P] AC 耦合电容位 (MIPI 标准 100nF) — 原厂是否内置 AC 耦合未回 (TBD-03); 内置则本位可改 DNP, 未内置必须装 |
| CSI_D0_D1_N_SRC | SoC[TBD-01].CSI_D0_D1_N | C_AC_CSI_D0_D1_N | NET_CSI_D0_D1_N_SRC | 100Ω ±10% | NET | 必装 | [待原厂] | TBD-03 | 方向 SoC→sensor; 电平 1.2V CML [待原厂]; 阻抗 100Ω ±10%; 连接 同上; 测试点 — |
| CSI_D0_D1_N | C_AC_CSI_D0_D1_N | CONN_CAM pin6 | C_AC_CSI_D0_D1_N | 100nF ±10% | C | 必装 | [推算] | TBD-03 | [CSI_D0_D1_N] AC 耦合电容位 (MIPI 标准 100nF) — 原厂是否内置 AC 耦合未回 (TBD-03); 内置则本位可改 DNP, 未内置必须装 |
| CSI_D0_D2_P_SRC | SoC[TBD-01].CSI_D0_D2_P | C_AC_CSI_D0_D2_P | NET_CSI_D0_D2_P_SRC | 100Ω ±10% | NET | DNP | [待原厂] | TBD-03 | 方向 SoC→sensor; 电平 1.2V CML [待原厂]; 阻抗 100Ω ±10%; 连接 同上 + 100Ω 对地端接; 测试点 — |
| CSI_D0_D2_P_SRC | R_TERM_CSI_D0_D2_P | NET_CSI_D0_D2_P_SRC | R_TERM_CSI_D0_D2_P | 100Ω ±1% | R | DNP | [推算] |  | [CSI_D0_D2_P_SRC] 未用差分对 100Ω 对地端接 (0402, 手工可补装) |
| CSI_D0_D2_P | C_AC_CSI_D0_D2_P | CONN_CAM pin7 | C_AC_CSI_D0_D2_P | 100nF ±10% | C | DNP | [推算] | TBD-03 | [CSI_D0_D2_P] 4-lane 预留 AC 耦合位 (对应 lane DNP) |
| GND | R_TERM_CSI_D0_D2_P | GND | R_TERM_CSI_D0_D2_P | 100Ω ±1% | R | DNP | [推算] |  | 未用差分对 100Ω 对地端接 (未用 lane 才装) |
| CSI_D0_D2_N_SRC | SoC[TBD-01].CSI_D0_D2_N | C_AC_CSI_D0_D2_N | NET_CSI_D0_D2_N_SRC | 100Ω ±10% | NET | DNP | [待原厂] | TBD-03 | 方向 SoC→sensor; 电平 1.2V CML [待原厂]; 阻抗 100Ω ±10%; 连接 同上 + 100Ω 对地端接; 测试点 — |
| CSI_D0_D2_N_SRC | R_TERM_CSI_D0_D2_N | NET_CSI_D0_D2_N_SRC | R_TERM_CSI_D0_D2_N | 100Ω ±1% | R | DNP | [推算] |  | [CSI_D0_D2_N_SRC] 未用差分对 100Ω 对地端接 (0402, 手工可补装) |
| CSI_D0_D2_N | C_AC_CSI_D0_D2_N | CONN_CAM pin8 | C_AC_CSI_D0_D2_N | 100nF ±10% | C | DNP | [推算] | TBD-03 | [CSI_D0_D2_N] 4-lane 预留 AC 耦合位 (对应 lane DNP) |
| GND | R_TERM_CSI_D0_D2_N | GND | R_TERM_CSI_D0_D2_N | 100Ω ±1% | R | DNP | [推算] |  | 未用差分对 100Ω 对地端接 (未用 lane 才装) |
| CSI_D0_D3_P_SRC | SoC[TBD-01].CSI_D0_D3_P | C_AC_CSI_D0_D3_P | NET_CSI_D0_D3_P_SRC | 100Ω ±10% | NET | DNP | [待原厂] | TBD-03 | 方向 SoC→sensor; 电平 1.2V CML [待原厂]; 阻抗 100Ω ±10%; 连接 同上 + 100Ω 对地端接; 测试点 — |
| CSI_D0_D3_P_SRC | R_TERM_CSI_D0_D3_P | NET_CSI_D0_D3_P_SRC | R_TERM_CSI_D0_D3_P | 100Ω ±1% | R | DNP | [推算] |  | [CSI_D0_D3_P_SRC] 未用差分对 100Ω 对地端接 (0402, 手工可补装) |
| CSI_D0_D3_P | C_AC_CSI_D0_D3_P | CONN_CAM pin9 | C_AC_CSI_D0_D3_P | 100nF ±10% | C | DNP | [推算] | TBD-03 | [CSI_D0_D3_P] 4-lane 预留 AC 耦合位 (对应 lane DNP) |
| GND | R_TERM_CSI_D0_D3_P | GND | R_TERM_CSI_D0_D3_P | 100Ω ±1% | R | DNP | [推算] |  | 未用差分对 100Ω 对地端接 (未用 lane 才装) |
| CSI_D0_D3_N_SRC | SoC[TBD-01].CSI_D0_D3_N | C_AC_CSI_D0_D3_N | NET_CSI_D0_D3_N_SRC | 100Ω ±10% | NET | DNP | [待原厂] | TBD-03 | 方向 SoC→sensor; 电平 1.2V CML [待原厂]; 阻抗 100Ω ±10%; 连接 同上 + 100Ω 对地端接; 测试点 — |
| CSI_D0_D3_N_SRC | R_TERM_CSI_D0_D3_N | NET_CSI_D0_D3_N_SRC | R_TERM_CSI_D0_D3_N | 100Ω ±1% | R | DNP | [推算] |  | [CSI_D0_D3_N_SRC] 未用差分对 100Ω 对地端接 (0402, 手工可补装) |
| CSI_D0_D3_N | C_AC_CSI_D0_D3_N | CONN_CAM pin10 | C_AC_CSI_D0_D3_N | 100nF ±10% | C | DNP | [推算] | TBD-03 | [CSI_D0_D3_N] 4-lane 预留 AC 耦合位 (对应 lane DNP) |
| GND | R_TERM_CSI_D0_D3_N | GND | R_TERM_CSI_D0_D3_N | 100Ω ±1% | R | DNP | [推算] |  | 未用差分对 100Ω 对地端接 (未用 lane 才装) |
| CSI_MCLK_SRC | SoC[TBD-01].CSI_MCLK | R_SER_CSI_MCLK | NET_CSI_MCLK_SRC | 单端, 需包地 | NET | 必装 | [待原厂] | TBD-03 | 方向 SoC→sensor; 电平 [待原厂]; 阻抗 单端, 需包地; 连接 CONN_CAM; 单独包地, 与电源并行 ≤5mm, 间距 ≥3mm; 测试点 TP_MCLK |
| CSI_MCLK | R_SER_CSI_MCLK | CONN_CAM pin11 | R_SER_CSI_MCLK | [待原厂] | R | DNP | [待原厂] | TBD-03 | [CSI_MCLK] MCLK 串阻位 (值随 TBD-03 的 MCLK 电平定; 33Ω 为经验值, 不写死) |
| CSI_RESET_N | SoC[TBD-01].CSI_RESET_N | R_PU_CSI_RST | NET_CSI_RESET_N | 单端, 10k 上拉 | NET | 必装 | [待原厂] | TBD-03 | 方向 SoC→sensor; 电平 1.8V [待原厂]; 阻抗 单端, 10k 上拉; 连接 CONN_CAM; 测试点 TP_CSI_RST |
| CSI_RESET_N | CONN_CAM pin12 | NET_CSI_RESET_N | NET_CSI_RESET_N | 单端, 10k 上拉 | NET | 必装 | [待原厂] | TBD-03 | [CSI_RESET_N] 附加节点 (同 net) |
| VDD_1V8_IO | R_PU_CSI_RST | RAIL_VDD_1V8_IO | R_PU_CSI_RST | 10k ±1% | R | 必装 | [推算] |  | [VDD_1V8_IO] CSI_RESET_N 上拉 (1.8V 域) |

## P6 高速差分与连接器
> DP_TX 4 lane / USB 2.0 / Type-C CC

### 功能块与判断
**高速差分与连接器: 板宽与 pitch 的风险都集中在这几页。**

- `A-21` DP_TX 4 lane: 主 PCB 内部走线 + redriver 位 (0402 串阻 ×4 + 对地电容位) —— 走线是 8×10mm 芯片**逃线**的主要出口, 也是"宽度≤8mm 硬约束"最吃紧的地方。
- `USB_D+/D-` (Type-C → 主 PCB, 跨铰链则经 `CONN_USB`) + `USB_CC1/CC2` (Type-C 方向检测) —— 我们**第一版不上无线**, USB 只做调试/烧录通道。
- ★**本轮网上查证标红的一条**: 官网说"封装尺寸须压缩至**宽度≤8mm**" + 8×10mm FCCSP **集成 DRAM** 的球间距通常 0.4-0.5mm [推算] → **我们 12mm 板宽 + 4-6 层叠层假设可能过于乐观** ⇒ **ISS-078 (blocker) 要按 pitch 0.3/0.4/0.5mm 三档重算**。这页的走线密度在 pitch 变大时会先崩。
- **[待原厂]**: FCCSP pitch + 完整球位图 + 逃线参考布局 (TBD-05) + AR9481 同 Die 代理资料。

### 器件表 (33 行 netlist 记录)
| net | 节点1 | 节点2 | 位号 | 值 | 类型 | DNP | 证据 | TBD | 说明 |
|---|---|---|---|---|---|---|---|---|---|
| DP_TX_A0_P_SRC | SoC[TBD-01].DP_TX_A0_P | R_SER_DP_A0_P | NET_DP_TX_A0_P_SRC | 100Ω ±10% (DP 1.4) | NET | 必装 | [待原厂] |  | 方向 SoC→桥接芯片; 电平 差分 [待原厂]; 阻抗 100Ω ±10% (DP 1.4); 连接 主 PCB 内部走线 + redriver 位 (0402 串阻 ×4 +  |
| DP_TX_A0_P | R_SER_DP_A0_P | U_BRIDGE pin21 | R_SER_DP_A0_P | 100Ω ±10% | R | 必装 | [待原厂] |  | [DP_TX_A0_P] DP TX 串阻位 (规格: 0402 串阻 ×4; 4 lane × P/N -> 实物 8 颗, 装配按实际 lane 数裁剪) |
| DP_TX_A0_N_SRC | SoC[TBD-01].DP_TX_A0_N | R_SER_DP_A0_N | NET_DP_TX_A0_N_SRC | 100Ω ±10% (DP 1.4) | NET | 必装 | [待原厂] |  | 方向 SoC→桥接芯片; 电平 差分 [待原厂]; 阻抗 100Ω ±10% (DP 1.4); 连接 主 PCB 内部走线 + redriver 位 (0402 串阻 ×4 +  |
| DP_TX_A0_N | R_SER_DP_A0_N | U_BRIDGE pin22 | R_SER_DP_A0_N | 100Ω ±10% | R | 必装 | [待原厂] |  | [DP_TX_A0_N] DP TX 串阻位 (规格: 0402 串阻 ×4; 4 lane × P/N -> 实物 8 颗, 装配按实际 lane 数裁剪) |
| DP_TX_A0_P_SRC | C_AC_DP_A0 | SoC[TBD-01].DP_TX_A0_P | C_AC_DP_A0 | [待原厂] | C | DNP | [待原厂] | TBD-04 | [DP_TX_A0_P_SRC] DP TX 对地电容位 (AC 耦合到地; 值随桥接芯片而定) |
| GND | C_AC_DP_A0 | GND | C_AC_DP_A0 | [待原厂] | C | DNP | [待原厂] | TBD-04 | DP TX 对地电容位 地端 |
| DP_TX_A1_P_SRC | SoC[TBD-01].DP_TX_A1_P | R_SER_DP_A1_P | NET_DP_TX_A1_P_SRC | 100Ω ±10% (DP 1.4) | NET | 必装 | [待原厂] |  | 方向 SoC→桥接芯片; 电平 差分 [待原厂]; 阻抗 100Ω ±10% (DP 1.4); 连接 主 PCB 内部走线 + redriver 位 (0402 串阻 ×4 +  |
| DP_TX_A1_P | R_SER_DP_A1_P | U_BRIDGE pin23 | R_SER_DP_A1_P | 100Ω ±10% | R | 必装 | [待原厂] |  | [DP_TX_A1_P] DP TX 串阻位 (规格: 0402 串阻 ×4; 4 lane × P/N -> 实物 8 颗, 装配按实际 lane 数裁剪) |
| DP_TX_A1_N_SRC | SoC[TBD-01].DP_TX_A1_N | R_SER_DP_A1_N | NET_DP_TX_A1_N_SRC | 100Ω ±10% (DP 1.4) | NET | 必装 | [待原厂] |  | 方向 SoC→桥接芯片; 电平 差分 [待原厂]; 阻抗 100Ω ±10% (DP 1.4); 连接 主 PCB 内部走线 + redriver 位 (0402 串阻 ×4 +  |
| DP_TX_A1_N | R_SER_DP_A1_N | U_BRIDGE pin24 | R_SER_DP_A1_N | 100Ω ±10% | R | 必装 | [待原厂] |  | [DP_TX_A1_N] DP TX 串阻位 (规格: 0402 串阻 ×4; 4 lane × P/N -> 实物 8 颗, 装配按实际 lane 数裁剪) |
| DP_TX_A1_P_SRC | C_AC_DP_A1 | SoC[TBD-01].DP_TX_A1_P | C_AC_DP_A1 | [待原厂] | C | DNP | [待原厂] | TBD-04 | [DP_TX_A1_P_SRC] DP TX 对地电容位 (AC 耦合到地; 值随桥接芯片而定) |
| GND | C_AC_DP_A1 | GND | C_AC_DP_A1 | [待原厂] | C | DNP | [待原厂] | TBD-04 | DP TX 对地电容位 地端 |
| DP_TX_A2_P_SRC | SoC[TBD-01].DP_TX_A2_P | R_SER_DP_A2_P | NET_DP_TX_A2_P_SRC | 100Ω ±10% (DP 1.4) | NET | 必装 | [待原厂] |  | 方向 SoC→桥接芯片; 电平 差分 [待原厂]; 阻抗 100Ω ±10% (DP 1.4); 连接 主 PCB 内部走线 + redriver 位 (0402 串阻 ×4 +  |
| DP_TX_A2_P | R_SER_DP_A2_P | U_BRIDGE pin25 | R_SER_DP_A2_P | 100Ω ±10% | R | 必装 | [待原厂] |  | [DP_TX_A2_P] DP TX 串阻位 (规格: 0402 串阻 ×4; 4 lane × P/N -> 实物 8 颗, 装配按实际 lane 数裁剪) |
| DP_TX_A2_N_SRC | SoC[TBD-01].DP_TX_A2_N | R_SER_DP_A2_N | NET_DP_TX_A2_N_SRC | 100Ω ±10% (DP 1.4) | NET | 必装 | [待原厂] |  | 方向 SoC→桥接芯片; 电平 差分 [待原厂]; 阻抗 100Ω ±10% (DP 1.4); 连接 主 PCB 内部走线 + redriver 位 (0402 串阻 ×4 +  |
| DP_TX_A2_N | R_SER_DP_A2_N | U_BRIDGE pin26 | R_SER_DP_A2_N | 100Ω ±10% | R | 必装 | [待原厂] |  | [DP_TX_A2_N] DP TX 串阻位 (规格: 0402 串阻 ×4; 4 lane × P/N -> 实物 8 颗, 装配按实际 lane 数裁剪) |
| DP_TX_A2_P_SRC | C_AC_DP_A2 | SoC[TBD-01].DP_TX_A2_P | C_AC_DP_A2 | [待原厂] | C | DNP | [待原厂] | TBD-04 | [DP_TX_A2_P_SRC] DP TX 对地电容位 (AC 耦合到地; 值随桥接芯片而定) |
| GND | C_AC_DP_A2 | GND | C_AC_DP_A2 | [待原厂] | C | DNP | [待原厂] | TBD-04 | DP TX 对地电容位 地端 |
| DP_TX_A3_P_SRC | SoC[TBD-01].DP_TX_A3_P | R_SER_DP_A3_P | NET_DP_TX_A3_P_SRC | 100Ω ±10% (DP 1.4) | NET | 必装 | [待原厂] |  | 方向 SoC→桥接芯片; 电平 差分 [待原厂]; 阻抗 100Ω ±10% (DP 1.4); 连接 主 PCB 内部走线 + redriver 位 (0402 串阻 ×4 +  |
| DP_TX_A3_P | R_SER_DP_A3_P | U_BRIDGE pin27 | R_SER_DP_A3_P | 100Ω ±10% | R | 必装 | [待原厂] |  | [DP_TX_A3_P] DP TX 串阻位 (规格: 0402 串阻 ×4; 4 lane × P/N -> 实物 8 颗, 装配按实际 lane 数裁剪) |
| DP_TX_A3_N_SRC | SoC[TBD-01].DP_TX_A3_N | R_SER_DP_A3_N | NET_DP_TX_A3_N_SRC | 100Ω ±10% (DP 1.4) | NET | 必装 | [待原厂] |  | 方向 SoC→桥接芯片; 电平 差分 [待原厂]; 阻抗 100Ω ±10% (DP 1.4); 连接 主 PCB 内部走线 + redriver 位 (0402 串阻 ×4 +  |
| DP_TX_A3_N | R_SER_DP_A3_N | U_BRIDGE pin28 | R_SER_DP_A3_N | 100Ω ±10% | R | 必装 | [待原厂] |  | [DP_TX_A3_N] DP TX 串阻位 (规格: 0402 串阻 ×4; 4 lane × P/N -> 实物 8 颗, 装配按实际 lane 数裁剪) |
| DP_TX_A3_P_SRC | C_AC_DP_A3 | SoC[TBD-01].DP_TX_A3_P | C_AC_DP_A3 | [待原厂] | C | DNP | [待原厂] | TBD-04 | [DP_TX_A3_P_SRC] DP TX 对地电容位 (AC 耦合到地; 值随桥接芯片而定) |
| GND | C_AC_DP_A3 | GND | C_AC_DP_A3 | [待原厂] | C | DNP | [待原厂] | TBD-04 | DP TX 对地电容位 地端 |
| USB_D_P_SRC | SoC[TBD-01].USB_D_P | R_SER_USB_D_P | NET_USB_D_P_SRC | 90Ω ±10% (与 MIPI 不同模板!) | NET | 必装 | [待原厂] | TBD-10 | 方向 SoC↔Type-C; 电平 3.3V [待原厂]; 阻抗 90Ω ±10% (与 MIPI 不同模板!); 连接 Type-C → 主 PCB (跨铰链则经 CONN_US |
| USB_D_P | R_SER_USB_D_P | J_TYPE_C pin4 | R_SER_USB_D_P | 22Ω ±1% | R | 必装 | [推算] | TBD-10 | [USB_D_P] USB 2.0 源端串阻 (D+); SoC 有无 USB PHY 未回 (TBD-10) |
| USB_D_N_SRC | SoC[TBD-01].USB_D_N | R_SER_USB_D_N | NET_USB_D_N_SRC | 90Ω ±10% | NET | 必装 | [待原厂] | TBD-10 | 方向 SoC↔Type-C; 电平 3.3V [待原厂]; 阻抗 90Ω ±10%; 连接 同上; 测试点 TP_USB_D- |
| USB_D_N | R_SER_USB_D_N | J_TYPE_C pin5 | R_SER_USB_D_N | 22Ω ±1% | R | 必装 | [推算] | TBD-10 | [USB_D_N] USB 2.0 源端串阻 (D-) |
| USB_CC1 | J_TYPE_C pin2 | R_CC1 | NET_USB_CC1 | Rd 5.1k 到 GND ×2 (PD sink 时由 TPS25730 接管) | NET | 必装 | [推算] |  | 方向 Type-C→PD控制器; 电平 —; 阻抗 Rd 5.1k 到 GND ×2 (PD sink 时由 TPS25730 接管); 连接 Type-C; 测试点 — |
| USB_CC2 | J_TYPE_C pin3 | R_CC2 | R_CC2 | 5.1k ±1% | R | 必装 | [推算] |  | [USB_CC2] Type-C Rd (非 PD 时下拉) |
| GND | R_CC1 | GND | R_CC1 | 5.1k ±1% | R | 必装 | [推算] |  | Type-C Rd 下拉端 |
| GND | R_CC2 | GND | R_CC2 | 5.1k ±1% | R | 必装 | [推算] |  | Type-C Rd 下拉端 |
| GND | J_TYPE_C pin6 | GND | J_TYPE_C | Type-C 16p 座 | CONN | 必装 | [官方] |  | Type-C GND 脚 |

## P7 板级接口与测试点
> 13 个测试点 + 3 按键 + 3 LED + ID 跳线

### 功能块与判断
**测试点是这台样机的"仪器接口" —— 13 个点决定了我们能不能在 G3 测出真数。**

- 13 个 TP 覆盖: 5 条电源 (VBUS / SYS / BAT / VCORE / VIO) + 3 条传感器轨 + 3 条光机轨 + 光机 DDC 相关的 2 条 (TBD-09 未确认前按"若 DDC 独立"预留)。**每个 TP 都在 §位置 写明"量哪个脚、离多远"**。
- 3 个按键 (PWR / VOL+ / VOL-) + 3 个 LED (R/G/B; **B 是 DNP —— 第一版不上无线**) + `ID_DETECT` 焊盘跳线 (主板/副板识别)。
- ★**这一页决定了三个硬指标能不能从"推算"变成"实测"**: 端到端 (`TP_FSIN` + 串口打点) · 皮肤温度 (热电偶) · 充电态温度 (`TP_CHG_STAT` + `TP_VBUS`)。**没这些点, EVT 只能写"未验"**。
- 全部测点走 **测试点 + π 滤波后** 的形式 → 第一台样机不贴这些点会返工 (后续加板要重来), 所以清单里明确标"第一台样机没有这些, 后期加板要重来"。
- **[待原厂]**: 帧同步能否引出 (TBD-07) · 充电状态能否读回 (TBD-08, 已有 TP 兜底, 不卡项目)。

### 器件表 (73 行 netlist 记录)
| net | 节点1 | 节点2 | 位号 | 值 | 类型 | DNP | 证据 | TBD | 说明 |
|---|---|---|---|---|---|---|---|---|---|
| LED_R | SoC[TBD-01].LED_R | R_LED_R | NET_LED_R | 1k 串阻 -> LED -> GND | NET | 必装 | [推算] |  | 方向 SoC→LED; 电平 3.3V; 阻抗 1k 串阻 → LED → GND; 连接 主 PCB; 测试点 TP_LED_R |
| LED_R_D | R_LED_R | D_LED_R | R_LED_R | 1k ±1% | R | 必装 | [推算] |  | [LED_R_D] LED_R 串阻 |
| GND | D_LED_R | GND | D_LED_R | LED (待选型) | LED | 必装 | [推算] |  | LED 阴极 -> GND |
| LED_G | SoC[TBD-01].LED_G | R_LED_G | NET_LED_G | 1k 串阻 -> LED -> GND | NET | 必装 | [推算] |  | 方向 SoC→LED; 电平 3.3V; 阻抗 1k 串阻 → LED → GND; 连接 主 PCB; 测试点 TP_LED_G |
| LED_G_D | R_LED_G | D_LED_G | R_LED_G | 1k ±1% | R | 必装 | [推算] |  | [LED_G_D] LED_G 串阻 |
| GND | D_LED_G | GND | D_LED_G | LED (待选型) | LED | 必装 | [推算] |  | LED 阴极 -> GND |
| LED_B | SoC[TBD-01].LED_B | R_LED_B | NET_LED_B | 1k 串阻 -> LED -> GND | NET | DNP | [推算] |  | 方向 SoC→LED; 电平 3.3V; 阻抗 1k 串阻 → LED → GND; 连接 主 PCB; 测试点 TP_LED_B |
| LED_B_D | R_LED_B | D_LED_B | R_LED_B | 1k ±1% | R | 必装 | [推算] |  | [LED_B_D] LED_B 串阻 |
| GND | D_LED_B | GND | D_LED_B | LED (待选型) | LED | DNP | [推算] |  | LED 阴极 -> GND |
| KEY_PWR | SoC[TBD-01].KEY_PWR | R_KEY_PWR | NET_KEY_PWR | 上拉 10k, 按下到 GND, 支持长按 | NET | 必装 | [推算] |  | 方向 按键→SoC; 电平 0/3.3V; 阻抗 上拉 10k, 按下到 GND, 支持长按; 连接 主 PCB; 测试点 TP_KEY_PWR |
| KEY_PWR | SW_KEY_PWR | NET_KEY_PWR | SW_KEY_PWR | 按键 (待选型) | SW | 必装 | [推算] |  | [KEY_PWR] KEY_PWR 按键 (CAM 键: 焊盘必留, 不装) |
| VDD_3V3_IO | R_KEY_PWR | RAIL_VDD_3V3_IO | R_KEY_PWR | 10k ±1% | R | 必装 | [推算] |  | [VDD_3V3_IO] KEY_PWR 上拉 (按下到 GND, 支持长按) |
| GND | SW_KEY_PWR | GND | SW_KEY_PWR | 按键 (待选型) | SW | 必装 | [推算] |  | 按键另一端 -> GND |
| KEY_VOL+ | SoC[TBD-01].KEY_VOL+ | R_KEY_VP | NET_KEY_VOL | 上拉 10k, 按下到 GND, 支持长按 | NET | 必装 | [推算] |  | 方向 按键→SoC; 电平 0/3.3V; 阻抗 同上; 连接 主 PCB; 测试点 TP_KEY_VP |
| KEY_VOL+ | SW_KEY_VP | NET_KEY_VOL | SW_KEY_VP | 按键 (待选型) | SW | 必装 | [推算] |  | [KEY_VOL+] KEY_VOL+ 按键 (CAM 键: 焊盘必留, 不装) |
| VDD_3V3_IO | R_KEY_VP | RAIL_VDD_3V3_IO | R_KEY_VP | 10k ±1% | R | 必装 | [推算] |  | [VDD_3V3_IO] KEY_VOL+ 上拉 (按下到 GND, 支持长按) |
| GND | SW_KEY_VP | GND | SW_KEY_VP | 按键 (待选型) | SW | 必装 | [推算] |  | 按键另一端 -> GND |
| KEY_VOL- | SoC[TBD-01].KEY_VOL- | R_KEY_VM | NET_KEY_VOL | 上拉 10k, 按下到 GND, 支持长按 | NET | 必装 | [推算] |  | 方向 按键→SoC; 电平 0/3.3V; 阻抗 同上; 连接 主 PCB; 测试点 TP_KEY_VM |
| KEY_VOL- | SW_KEY_VM | NET_KEY_VOL | SW_KEY_VM | 按键 (待选型) | SW | 必装 | [推算] |  | [KEY_VOL-] KEY_VOL- 按键 (CAM 键: 焊盘必留, 不装) |
| VDD_3V3_IO | R_KEY_VM | RAIL_VDD_3V3_IO | R_KEY_VM | 10k ±1% | R | 必装 | [推算] |  | [VDD_3V3_IO] KEY_VOL- 上拉 (按下到 GND, 支持长按) |
| GND | SW_KEY_VM | GND | SW_KEY_VM | 按键 (待选型) | SW | 必装 | [推算] |  | 按键另一端 -> GND |
| KEY_CAM | SoC[TBD-01].KEY_CAM | R_KEY_CAM | NET_KEY_CAM | 上拉 10k, 按下到 GND, 支持长按 | NET | DNP | [推算] |  | 方向 按键→SoC; 电平 0/3.3V; 阻抗 同上; 连接 主 PCB (焊盘留, 不装); 测试点 — |
| KEY_CAM | SW_KEY_CAM | NET_KEY_CAM | SW_KEY_CAM | 按键 (待选型) | SW | DNP | [推算] |  | [KEY_CAM] KEY_CAM 按键 (CAM 键: 焊盘必留, 不装) |
| VDD_3V3_IO | R_KEY_CAM | RAIL_VDD_3V3_IO | R_KEY_CAM | 10k ±1% | R | 必装 | [推算] |  | [VDD_3V3_IO] KEY_CAM 上拉 (按下到 GND, 支持长按) |
| GND | SW_KEY_CAM | GND | SW_KEY_CAM | 按键 (待选型) | SW | DNP | [推算] |  | 按键另一端 -> GND |
| ID_DETECT_0 | SoC[TBD-01].ID0 | R_PU_ID0 | NET_ID_DETECT_0 | GPIO 编码 (2 位) | NET | 必装 | [推算] |  | 方向 板级→SoC; 电平 3.3V; 阻抗 GPIO 编码 (2 位); 连接 主 PCB (焊盘跳线); 测试点 TP_ID |
| ID_DETECT_0 | R_ID_JMP0 | NET_ID_DETECT_0 | R_ID_JMP0 | 0Ω (跳线位) | R | DNP | [推算] |  | [ID_DETECT_0] 板级 ID 位 0 跳线位 (焊盘跳线编码 2 位) |
| VDD_3V3_IO | R_PU_ID0 | RAIL_VDD_3V3_IO | R_PU_ID0 | 10k ±1% | R | 必装 | [推算] |  | [VDD_3V3_IO] 板级 ID 位 {0} 上拉 |
| GND | R_ID_JMP0 | GND | R_ID_JMP0 | 0Ω (跳线位) | R | DNP | [推算] |  | ID 跳线位 -> GND (装上 = 该位 0) |
| ID_DETECT_1 | SoC[TBD-01].ID1 | R_PU_ID1 | NET_ID_DETECT_1 | GPIO 编码 (2 位) | NET | 必装 | [推算] |  | 方向 板级→SoC; 电平 3.3V; 阻抗 GPIO 编码 (2 位); 连接 主 PCB (焊盘跳线); 测试点 TP_ID |
| ID_DETECT_1 | R_ID_JMP1 | NET_ID_DETECT_1 | R_ID_JMP1 | 0Ω (跳线位) | R | DNP | [推算] |  | [ID_DETECT_1] 板级 ID 位 1 跳线位 (焊盘跳线编码 2 位) |
| VDD_3V3_IO | R_PU_ID1 | RAIL_VDD_3V3_IO | R_PU_ID1 | 10k ±1% | R | 必装 | [推算] |  | [VDD_3V3_IO] 板级 ID 位 {0} 上拉 |
| GND | R_ID_JMP1 | GND | R_ID_JMP1 | 0Ω (跳线位) | R | DNP | [推算] |  | ID 跳线位 -> GND (装上 = 该位 0) |
| VBUS_5V | TP_VBUS | J_TYPE_C pin1 | TP_VBUS | 测试点 | TP | 必装 | [推算] |  | 测什么: Type-C 入口 5V; 位置: Type-C 出口侧 ≤3mm |
| SYS | TP_SYS | J_CHG pin1 | TP_SYS | 测试点 | TP | 必装 | [推算] |  | 测什么: 系统 3.7V 主轨; 位置: 电池保护后 |
| BAT | TP_BAT | U_BATPROT | TP_BAT | 测试点 | TP | 必装 | [推算] |  | 测什么: 电池电压; 位置: BQ25896 BAT 脚 |
| V_CORE | TP_VCORE | U_DCDC_VCORE | TP_VCORE | 测试点 | TP | 必装 | [推算] |  | 测什么: SoC 核心轨; 位置: DC-DC 输出 |
| V_SOC_IO | TP_VIO | U_DCDC_VIO | TP_VIO | 测试点 | TP | 必装 | [推算] |  | 测什么: SoC IO 轨; 位置: DC-DC/LDO 输出 |
| SENSOR_AVDD | TP_SENSOR_2V8 | U_LDO_S28 | TP_SENSOR_2V8 | 测试点 | TP | 必装 | [推算] |  | 测什么: sensor 三条轨; 位置: LDO 输出 (规格合并名 TP_SENSOR_3V3/1V8/2V8) |
| SENSOR_VDD_IO | TP_SENSOR_1V8 | U_LDO_S18 | TP_SENSOR_1V8 | 测试点 | TP | 必装 | [推算] |  | 测什么: sensor 三条轨; 位置: LDO 输出 (规格合并名 TP_SENSOR_3V3/1V8/2V8) |
| SENSOR_CORE | TP_SENSOR_1V2 | U_LDO_S12 | TP_SENSOR_1V2 | 测试点 | TP | 必装 | [推算] |  | 测什么: sensor 三条轨; 位置: LDO 输出 (规格合并名 TP_SENSOR_3V3/1V8/2V8) |
| LIGHT_3V3 | TP_LIGHT_3V3 | U_LDO_L33 | TP_LIGHT_3V3 | 测试点 | TP | 必装 | [推算] |  | 测什么: 光机轨; 位置: LDO 输出 |
| LIGHT_1V8 | TP_LIGHT_1V8 | U_LDO_L18 | TP_LIGHT_1V8 | 测试点 | TP | DNP | [推算] |  | 测什么: 光机 1.8V 轨 (待 JBD) |
| CSI_D0_CK_P | TP_CSI_CK_P | CONN_CAM pin1 | TP_CSI_CK_P | 测试点 | TP | 必装 | [推算] |  | 测什么: CSI 时钟差分 (示波器测眼图/摆幅); 位置: 连接器出口 (规格合并名 TP_CSI_D0_CK_P / _N) |
| CSI_D0_CK_N | TP_CSI_CK_N | CONN_CAM pin2 | TP_CSI_CK_N | 测试点 | TP | 必装 | [推算] |  | 测什么: CSI 时钟差分 (规格合并名 TP_CSI_D0_CK_P / _N) |
| CSI_D0_D0_P | TP_CSI_D0_P | CONN_CAM pin3 | TP_CSI_D0_P | 测试点 | TP | 必装 | [推算] |  | 测什么: CSI D0 数据差分; 位置: 连接器出口 |
| CSI_D0_D0_N | TP_CSI_D0_N | CONN_CAM pin4 | TP_CSI_D0_N | 测试点 | TP | 必装 | [推算] |  | 测什么: CSI D0 数据差分; 位置: 连接器出口 |
| CSI_RESET_N | TP_CSI_RST | CONN_CAM pin12 | TP_CSI_RST | 测试点 | TP | 必装 | [推算] |  | 测什么: CSI 复位 (10k 上拉点) |
| CSI_MCLK | TP_MCLK | CONN_CAM pin11 | TP_MCLK | 测试点 | TP | 必装 | [推算] |  | 测什么: MCLK (包地走线) |
| DSI_D0_CK_P | TP_DSI_CK_P | CONN_LIGHT pin3 | TP_DSI_CK_P | 测试点 | TP | 必装 | [推算] |  | 测什么: DSI 时钟差分; 位置: 连接器出口 (规格合并名 TP_DSI_D0_CK_P / _N) |
| DSI_D0_CK_N | TP_DSI_CK_N | CONN_LIGHT pin4 | TP_DSI_CK_N | 测试点 | TP | 必装 | [推算] |  | 测什么: DSI 时钟差分 (规格合并名 TP_DSI_D0_CK_P / _N) |
| DSI_D0_D0_P | TP_DSI_D0_P | CONN_LIGHT pin5 | TP_DSI_D0_P | 测试点 | TP | 必装 | [推算] |  | 测什么: DSI D0 数据差分 |
| DSI_D0_D0_N | TP_DSI_D0_N | CONN_LIGHT pin6 | TP_DSI_D0_N | 测试点 | TP | 必装 | [推算] |  | 测什么: DSI D0 数据差分 |
| I2C_A_SCL | TP_I2CA_SCL | CONN_CAM pin13 | TP_I2CA_SCL | 测试点 | TP | 必装 | [推算] |  | 测什么: I2C_A 时钟 |
| I2C_A_SDA | TP_I2CA_SDA | CONN_CAM pin14 | TP_I2CA_SDA | 测试点 | TP | 必装 | [推算] |  | 测什么: I2C_A 数据 |
| I2C_B_SCL | TP_I2CB_SCL | CONN_LIGHT pin13 | TP_I2CB_SCL | 测试点 | TP | 必装 | [推算] |  | 测什么: DDC 时钟 (I2C_B) |
| I2C_B_SDA | TP_I2CB_SDA | CONN_LIGHT pin14 | TP_I2CB_SDA | 测试点 | TP | 必装 | [推算] |  | 测什么: DDC 数据 (I2C_B) |
| USB_D_P | TP_USB_D_P | J_TYPE_C pin4 | TP_USB_D_P | 测试点 | TP | 必装 | [推算] |  | 测什么: USB 2.0 差分; 位置: Type-C 出口 (规格合并名 TP_USB_D+ / D-) |
| USB_D_N | TP_USB_D_N | J_TYPE_C pin5 | TP_USB_D_N | 测试点 | TP | 必装 | [推算] |  | 测什么: USB 2.0 差分 (规格合并名 TP_USB_D+ / D-) |
| FSIN_OUT | TP_FSIN | R_SER_FSIN | TP_FSIN | 测试点 | TP | 必装 | [推算] |  | 测什么: 帧同步 (FSIN/VSYNC) 引出; 位置: SoC 侧 -> 回答原厂问询 Q4b.3 |
| CHG_STAT | TP_CHG_STAT | R_PU_CHG_STAT | TP_CHG_STAT | 测试点 | TP | 必装 | [推算] |  | 测什么: 充电状态; 位置: BQ25896 STAT 脚 -> 回答 Q4b.4 |
| PWR_GOOD | TP_PG | R_PU_PG | TP_PG | 测试点 | TP | 必装 | [推算] |  | 测什么: 电源好 (BQ25896 PG 脚) |
| ID_DETECT_0 | TP_ID | R_PU_ID0 | TP_ID | 测试点 | TP | 必装 | [推算] |  | 测什么: 板级版本识别 (I2C EEPROM 或 GPIO 编码); 位置: 主 PCB |
| LED_R | TP_LED_R | R_LED_R | TP_LED_R | 测试点 | TP | 必装 | [推算] |  | 测什么: LED 红 |
| LED_G | TP_LED_G | R_LED_G | TP_LED_G | 测试点 | TP | 必装 | [推算] |  | 测什么: LED 绿 |
| LED_B | TP_LED_B | R_LED_B | TP_LED_B | 测试点 | TP | DNP | [推算] |  | 测什么: LED 蓝 (无无线 -> DNP) |
| KEY_PWR | TP_KEY_PWR | R_KEY_PWR | TP_KEY_PWR | 测试点 | TP | 必装 | [推算] |  | 测什么: 电源键 |
| KEY_VOL+ | TP_KEY_VP | R_KEY_VP | TP_KEY_VP | 测试点 | TP | 必装 | [推算] |  | 测什么: 音量+ 键 |
| KEY_VOL- | TP_KEY_VM | R_KEY_VM | TP_KEY_VM | 测试点 | TP | 必装 | [推算] |  | 测什么: 音量- 键 |
| RESET_N | TP_RESET | R_PU_RESET_N | TP_RESET | 测试点 | TP | 必装 | [推算] |  | 测什么: 复位网 |
| BOOT_N | TP_BOOT | R_PU_BOOT_N | TP_BOOT | 测试点 | TP | 必装 | [推算] |  | 测什么: BOOT 网 |
| JTAG_TCK | TP_JTAG | J_DEBUG pin1 | TP_JTAG | 测试点 | TP | 必装 | [推算] |  | 测什么: JTAG 时钟 |
| UART_TX | TP_UART | J_UART pin1 | TP_UART | 测试点 | TP | 可选 | [推算] |  | 测什么: UART TX (与 USB 二选一) |

## P8 时钟 · 复位 · 调试
> XTAL 两套方案 (内部RC不装 / 外部晶振焊盘位不装) + RESET/BOOT + JTAG/UART

### 功能块与判断
**时钟 / 复位 / 调试 —— 看着不起眼, 但这里有两个"必须双份"的决定。**

- ★**XTAL 双方案**: 参考版**同时**给 "内部 RC (不装)" 与 "外部晶振 (焊盘位 + 2×12pF, **不装**)" 两套 —— 因为**原厂一句话就能定生死** (ARS45 到底要不要外部晶振, 同 Die 的 AR9481 也不能确定)。焊盘位先留, 装配时按原厂确认选。
- `RESET_N` / `BOOT_N` 走按键到 GND (软上电/进下载模式), **释放时序**待原厂 (TBD-12) → 这决定我们按键电容与上电电阻怎么配。
- `JTAG` 4 线 + `UART` 2 线 复用 1×4 1.27mm 排针 (**不装贴片**, 手工可焊) —— 调试/烧录通道, 与 USB 二选一。
- **[待原厂]**: 上下电/复位时序要求 (TBD-12, 含 RESET 释放时机与内部 DCDC 同步机制) · 是否有 USB PHY 及其版本 (TBD-10) · 启动介质与挂载接口 (TBD-06/11)。

### 器件表 (29 行 netlist 记录)
| net | 节点1 | 节点2 | 位号 | 值 | 类型 | DNP | 证据 | TBD | 说明 |
|---|---|---|---|---|---|---|---|---|---|
| XTAL_IN | SoC[TBD-01].XTAL_IN | X1 | NET_XTAL_IN | 12pF | NET | DNP | [同Die参考-待官方确认] | TBD-12 | 时钟: 外部晶振位 (XTAL_IN) |
| XTAL_IN | C_XTAL_IN | NET_XTAL_IN | C_XTAL_IN | 12pF ±10% | C | DNP | [同Die参考-待官方确认] | TBD-12 | [XTAL_IN] 晶振负载电容 (XTAL_IN 侧) |
| XTAL_OUT | SoC[TBD-01].XTAL_OUT | X1 | NET_XTAL_OUT | 12pF | NET | DNP | [同Die参考-待官方确认] | TBD-12 | 时钟: 外部晶振位 (XTAL_OUT) |
| XTAL_OUT | C_XTAL_OUT | NET_XTAL_OUT | C_XTAL_OUT | 12pF ±10% | C | DNP | [同Die参考-待官方确认] | TBD-12 | [XTAL_OUT] 晶振负载电容 (XTAL_OUT 侧) |
| GND | C_XTAL_IN | GND | C_XTAL_IN | 12pF ±10% | C | DNP | [同Die参考-待官方确认] | TBD-12 | 晶振负载电容 地端 |
| GND | C_XTAL_OUT | GND | C_XTAL_OUT | 12pF ±10% | C | DNP | [同Die参考-待官方确认] | TBD-12 | 晶振负载电容 地端 |
| RESET_N | R_PU_RESET_N | R_SER_RESET_N | NET_RESET_N | 上拉 10k + RC(1k/100nF) | NET | 必装 | [待原厂] | TBD-12 | 方向 双向; 电平 1.8V [待原厂]; 阻抗 上拉 10k + RC(1k/100nF); 连接 SoC RESET_N + 按键到 GND; 测试点 TP_RESET |
| RESET_N | SW_RST | NET_RESET_N | SW_RST | 复位按键 (待选型) | SW | 必装 | [推算] |  | [RESET_N] 复位键 -> GND |
| RESET_N_SOC | R_SER_RESET_N | SoC[TBD-01].RESET_N | R_SER_RESET_N | 1k ±1% | R | 必装 | [推算] |  | [RESET_N_SOC] RESET_N RC 串联 (与 C_RST 构成 RC 复位) |
| RESET_N_SOC | C_RST | NET_RESET_N_SOC | C_RST | 100nF ±10% | C | 必装 | [推算] |  | [RESET_N_SOC] RESET_N 对地 RC 电容 |
| VDD_1V8_IO | R_PU_RESET_N | RAIL_VDD_1V8_IO | R_PU_RESET_N | 10k ±1% | R | 必装 | [推算] |  | [VDD_1V8_IO] RESET_N 上拉 (1.8V 域) |
| GND | C_RST | GND | C_RST | 100nF ±10% | C | 必装 | [推算] |  | RESET RC 电容 地端 |
| GND | SW_RST | GND | SW_RST | 复位按键 (待选型) | SW | 必装 | [推算] |  | 复位键 -> GND |
| BOOT_N | SoC[TBD-01].BOOT_N | R_PU_BOOT_N | NET_BOOT_N | 上拉 10k | NET | 必装 | [待原厂] | TBD-12 | 方向 双向; 电平 1.8V [待原厂]; 阻抗 上拉 10k; 连接 SoC BOOT 脚 + 按键到 GND; 测试点 TP_BOOT |
| BOOT_N | SW_BOOT | NET_BOOT_N | SW_BOOT | BOOT 按键 (待选型) | SW | 必装 | [推算] |  | [BOOT_N] BOOT 键 -> GND |
| VDD_1V8_IO | R_PU_BOOT_N | RAIL_VDD_1V8_IO | R_PU_BOOT_N | 10k ±1% | R | 必装 | [推算] |  | [VDD_1V8_IO] BOOT_N 上拉 (1.8V 域) |
| GND | SW_BOOT | GND | SW_BOOT | BOOT 按键 (待选型) | SW | 必装 | [推算] |  | BOOT 键 -> GND |
| JTAG_TCK_SOC | SoC[TBD-01].JTAG_TCK | R_JTAG_TCK | NET_JTAG_TCK_SOC | 单端, 100Ω 串阻 | NET | 必装 | [待原厂] |  | 方向 双向; 电平 [待原厂]; 阻抗 单端, 100Ω 串阻; 连接 1×4 1.27mm 排针 (调试用, 不装贴片); 测试点 TP_JTAG |
| JTAG_TCK | R_JTAG_TCK | J_DEBUG pin1 | R_JTAG_TCK | 100Ω ±1% | R | 必装 | [推算] |  | [JTAG_TCK] JTAG TCK 串阻 |
| JTAG_TMS_SOC | SoC[TBD-01].JTAG_TMS | R_JTAG_TMS | NET_JTAG_TMS_SOC | 单端, 100Ω 串阻 | NET | 必装 | [待原厂] |  | 方向 双向; 电平 [待原厂]; 阻抗 单端, 100Ω 串阻; 连接 1×4 1.27mm 排针 (调试用, 不装贴片); 测试点 TP_JTAG |
| JTAG_TMS | R_JTAG_TMS | J_DEBUG pin2 | R_JTAG_TMS | 100Ω ±1% | R | 必装 | [推算] |  | [JTAG_TMS] JTAG TMS 串阻 |
| JTAG_TDI_SOC | SoC[TBD-01].JTAG_TDI | R_JTAG_TDI | NET_JTAG_TDI_SOC | 单端, 100Ω 串阻 | NET | 必装 | [待原厂] |  | 方向 双向; 电平 [待原厂]; 阻抗 单端, 100Ω 串阻; 连接 1×4 1.27mm 排针 (调试用, 不装贴片); 测试点 TP_JTAG |
| JTAG_TDI | R_JTAG_TDI | J_DEBUG pin3 | R_JTAG_TDI | 100Ω ±1% | R | 必装 | [推算] |  | [JTAG_TDI] JTAG TDI 串阻 |
| JTAG_TDO_SOC | SoC[TBD-01].JTAG_TDO | R_JTAG_TDO | NET_JTAG_TDO_SOC | 单端, 100Ω 串阻 | NET | 必装 | [待原厂] |  | 方向 双向; 电平 [待原厂]; 阻抗 单端, 100Ω 串阻; 连接 1×4 1.27mm 排针 (调试用, 不装贴片); 测试点 TP_JTAG |
| JTAG_TDO | R_JTAG_TDO | J_DEBUG pin4 | R_JTAG_TDO | 100Ω ±1% | R | 必装 | [推算] |  | [JTAG_TDO] JTAG TDO 串阻 |
| UART_TX | SoC[TBD-01].UART_TX | J_UART pin1 | NET_UART_TX | 单端 | NET | 可选 | [待原厂] |  | 方向 双向; 电平 3.3V [待原厂]; 阻抗 单端; 连接 同 B-19 排针 (复用脚); 测试点 TP_UART |
| UART_RX | SoC[TBD-01].UART_RX | J_UART pin2 | J_UART | 1×2 1.27mm 排针 (UART) | CONN | 可选 | [推算] |  | [UART_RX] 规格: UART 与 JTAG 复用同一排针 -> 本版拆成 1×2 独立排针 (原厂要求复用则再合并) |
| FSIN | SoC[TBD-01].FSIN | R_SER_FSIN | NET_FSIN | 单端, 50Ω 串阻 | NET | 必装 | [待原厂] | TBD-13 | 方向 SoC→外部; 电平 [待原厂]; 阻抗 单端, 50Ω 串阻; 连接 SoC FSIN/VSYNC 脚 → 测试点; 测试点 TP_FSIN |
| FSIN_OUT | R_SER_FSIN | TP_FSIN | R_SER_FSIN | 50Ω ±1% | R | 必装 | [推算] | TBD-13 | [FSIN_OUT] FSIN 引出串阻 |

---

## 附: 本版与投板版还差什么 (缺口清单)
| # | 缺什么 | 卡住谁 | 怎么解 |
|---|---|---|---|
| 1 | SoC 引脚表 / 球位图 / FCCSP pitch | 原理图定版 + PCB 逃线 + 板宽 (blocker) | 原厂 (TBD-01/05) —— **网上确认拿不到** (官网无下载区) |
| 2 | 各电源域标称电压/最大电流/上电时序 | P1 电源页定版 + DC-DC 选型 | 原厂 (TBD-02) |
| 3 | MIPI-CSI lane 数/速率/AC 耦合是否内置 | P5 传感器页 (AC 耦合位/端接位) | 原厂 (TBD-03) |
| 4 | 显示 TX 接口类型 (DSI / DP / 两者) | P4 显示页 + 要不要桥接芯片 | 原厂 (TBD-04) + **JBD 开发套件接口定义** (可能更快) |
| 5 | 启动存储形态 (SPI-NOR vs eMMC) 与挂载口 | P3 启动存储页 + 板宽 | 原厂 (TBD-06/11) |
| 6 | 球位号 (全部 SoC 侧节点) | 8 页全部 | 原厂 (TBD-01) |

> ★**并行风险**: 官网「宽度≤8mm」+ FCCSP 集成 DRAM 的 pitch 通常 0.4-0.5mm [推算] → **12mm 板宽与 4-6 层假设可能被推翻** (ISS-078, blocker)。
