# PINOUT_FOOTPRINT_SPEC —— demo 主板器件封装与脚号落定规格表

> **作者**: 子 agent (ic-footprint-pinout-spec) · **日期**: 2026-11-03
> **任务**: 把 demo 主板上脚号还没落定的器件, 用**原厂 datasheet / 原厂 ECAD** 定下来: 封装 (footprint) + 引脚号 ↔ 引脚名对应关系
> **★本文只出规格表, 不改网表** —— 网表改动由项目总工执行 (历史教训: 让子 agent 直接改网表, 三次 0 产出)
> **机器版**: `HW/PCB/pinout_footprint.json` (同目录) —— `pins` 的键是**真实引脚号 (字符串)**, 值是引脚名, 可直接拿去生成 KiCad 封装与改网表节点

---

## 0. 判据与本次执行摘要 (★照抄铁律)

- ★**没查过官方 datasheet 的器件不许填** —— 每个封装/脚号必须带**原厂来源 URL** + **页码/图号**
- **授权分销商镜像** (Mouser / DigiKey / LCSC / Arrow) 的**原厂 PDF** 可以当证据; **第三方博客 / 知乎 / AI 生成的封装不许当证据**
- 查不到的写 **"未查到"**, **不许猜**
- ★**封装命名**统一给: 原厂封装代号 + 尺寸 + pitch + 厂商 land pattern 文件名 (若有)

### 0.1 ★KiCad 官方库 footprint 对照表 (已在本机 KiCad footprint 库里核对过存在性)

> 本机库路径: `/home/yuewuya/kicad/AppDir/share/kicad/footprints/`
> ★**焊盘编号顺序一定要复核** —— 库内通用封装的编号方向与 TI 原厂脚号不一定一致 (尤其 TPS7A20 的 1=OUT/4=IN 与 TPS62130A 的 13=EN/4=PG 这类交叉编号)

| 器件 | 原厂 land pattern | KiCad 官方库 footprint | 状态 |
|---|---|---|---|
| U_LDO_* (7 颗 TPS7A20) | `DQN0004A` | `Package_DFN_QFN:UDFN-4-1EP_1x1mm_P0.65mm_EP0.48x0.48mm` | ✅ **尺寸/pitch 全对** (1×1mm, 0.65mm pitch, pad1-4 + pad5 中心散热焊盘) ⇒ ★核对编号顺序 + pin5 接 GND |
| U_SUPV (SOT-23 变体) | `DBV0006A` | `Package_TO_SOT_SMD:SOT-23-6` | ✅ 存在; ★核对编号方向 |
| U_SUPV (WSON 变体) | `DRV0006D` | — | ★需自绘 (2.0×2.0mm, 0.65mm pitch) |
| U_PWR_SW / U_EN_SW (TPS22991) | `RAA0004A` | — | ★需自绘 (0.85×0.75mm UQFN-4, 库内无) |
| U_BATPROT (BQ2970) | `DSE0006A` | — | ★需自绘 (1.5×1.5mm DFN-6, 库内无) |
| Q1 / Q2 (CSD16406Q3) | `Q3` | — | ★需自绘 (3.3×3.3mm SON-8, 库内无) |
| U_DCDC_VCORE / VIO (TPS62130A) | `RGT0016C` | `Package_DFN_QFN:VQFN-16-1EP_3x3mm_P0.5mm_EP1.68x1.68mm` | ✅ **散热焊盘 1.68mm 与原厂完全对上**; ★核对编号方向 |
| J_TYPE_C (GCT USB4105) | 原厂 Recommended PCB Layout | `Connector_USB.pretty:USB_C_Receptacle_*` (Amphenol / CNCTech / G-Switch) 可作几何参考 | ★**GCT USB4105 无现成封装 ⇒ 需自绘** |
| CONN_CAM (FH35C-31S) | HIROSE Recommended Land Dimensions | — | ★需自绘 (库内无 HIROSE FH 系列) |
| CONN_LIGHT (FH12-22S) | ★**官方封装已拿到** (RPi 官方 CM5IO .kicad_mod, 几何已抄录) | `Hirose_FH12-22S-0.5SH_1x22-1MP_P0.50mm_Horizontal` | ★**2026-11-04 定案** ⇒ 不用自绘 |

| 器件 | 状态 | 封装 | 脚号来源 |
|---|---|---|---|
| U_LDO_L33 / IO33 / IO18 / L18 / S12 / S18B / S28 (7 颗 TPS7A20) | ✅ **已查实** | X2SON DQN (4 pin + 散热焊盘) | TPS7A20 SBVS338H p.4 Fig 4-3 + Table 4-1 |
| U_SUPV (TPS3808G01) | ✅ **已查实** | SOT-23-6 DBV / WSON-6 DRV (二选一) | TPS3808 SBVS050N p.4 Fig 5-1/5-2 + Table 5-1 |
| U_PWR_SW (负载开关) | ✅ **已查实** ★**推荐 TPS22991** | UQFN-4 RAA (0.85×0.75mm) | TPS22991 SLVSFK0B p.4 Fig 5-1 + Table 5-1 |
| U_EN_SW (F13 底板主电源门控) | ✅ **已查实** ★**推荐 TPS22991** | UQFN-4 RAA (0.85×0.75mm) | 同上 (脚号表完全一致) |
| U_BATPROT (BQ2970) | ✅ **已查实** | WSON-6 DSE (1.5×1.5mm) | BQ2970 SLUSBU9I p.3 Fig 5-1 + Table 5-1 |
| Q1 (保护 MOS) | ✅ **已查实** ★**推荐 CSD16406Q3** (BQ2970 原厂点名) | SON-8 Q3 (3.3×3.3mm) | BQ2970 SLUSBU9I p.20 (原厂点名用此 FET) + CSD16406Q3 SLPS202B |
| BT_432243 (电池) | ⚠️ **部分未查到** (见 §7) | 软包 LiPo 2 焊盘 (尺寸已有库内官方值) | — |
| J_TYPE_C (USB-C 16p) | ✅ **已查实** ★**推荐 GCT USB4105** | SMT 贴片 USB-C 母座 | GCT USB4105 图纸 Rev B3 (DigiKey 镜像原厂 PDF) |
| U_DCDC_VCORE / VIO (TPS62130A) | ✅ **已查实 · 标 DNP** | VQFN-16 RGT (3×3mm) | TPS62130A SLVSAG7F p.3 Fig 6-1 + Table 6-1 |
| CONN_CAM (FH35C-31S-0.3SHW(50)) | ✅ **已查实** | 0.3mm 背夹式双面触点 FPC 座, 31p | HIROSE 原厂 2D 图 + 系列规格书 |
| CONN_LIGHT (FH12-22S-0.5SH(55)) | ✅ **已查实 · 已定案** (见 §11) | **22p / 0.5mm** 右角(水平) / 底接触 FPC 座 | ★**Raspberry Pi 官方 CM4IO/CM5IO KiCad 器件属性 + 官方封装 .kicad_mod**; 针序照 **Pi5 官方原理图 J4** |

★**本次最重要的 3 条纠正** (与任务书里的假设不同, 已按原厂 datasheet 落定):
1. **TPS7A20 的 X2SON 是 "4 脚 + 散热焊盘" 不是 "5 脚"** —— 脚号是 **1=OUT, 2=GND, 3=EN, 4=IN, 5=散热焊盘(接 GND)**; 任务书模板里的 `{"1":"IN","2":"GND","3":"EN","4":"OUT","5":"NC"}` **是错的** (那是 SOT-23 版的 pin 4=N/C, 不是 X2SON)。
2. **BQ2970 没有单一 "GATE" 脚** —— 原厂是 **COUT (pin2, 充放电管) / DOUT (pin3, 放电容) 两个独立栅驱动**。网表里 "U_BATPROT.GATE 一根线接 Q1+Q2 共栅" 的画法**与原厂不符** ⇒ 必须改成 Q1 接 DOUT / Q2 接 COUT (或按实际拓扑分配), 且两管**不能共栅**。
3. **TPS3808 的采样脚叫 SENSE 不是 IN** —— 网表里的 `U_SUPV IN` 对应原厂 **pin 5 = SENSE**; 且原厂还有 **MR (pin3, 手动复位)** 和 **GND (pin2)** 两脚网表里没有。

---

## 1. U_LDO_L33 / U_LDO_IO33 / U_LDO_IO18 / U_LDO_L18 / U_LDO_S12 / U_LDO_S18B / U_LDO_S28 —— TPS7A20 系列 (7 颗)

### 1.1 器件与封装

| 项 | 值 |
|---|---|
| 原厂器件 | **Texas Instruments TPS7A20** (300mA 超低噪声低 IQ LDO) |
| 原厂封装代号 | **DQN** = X2SON, **1mm × 1mm**, 高 0.4mm max, **无引脚 (no lead)** |
| 厂商 land pattern / 封装图代号 | **`DQN0004A`** (原厂 datasheet 机械尺寸节 "PACKAGE OUTLINE DQN0004A — X2SON - 0.4 mm max height PLASTIC SMALL OUTLINE - NO LEAD"; 焊盘 0.48+0.12/−0.1mm 方形, 2X 0.65mm pitch, PIN 1 INDEX AREA) |
| KiCad 官方库 footprint | `Package_DFN_QFN:UDFN-4-1EP_1x1mm_P0.65mm_EP0.48x0.48mm` (尺寸/pitch 全对; ★核对编号顺序, pad5 = 散热焊盘接 GND) |
| 可选封装 (同系列同脚号表) | `DBV` = SOT-23-5 2.9×2.8mm / `YCJ`+`YCK` = DSBGA-4 0.61mm 见 §1.4 |
| 脚数 | **4 个信号脚 + 1 个散热焊盘 (Thermal Pad) = 5 个焊盘** |
| Pitch | 0.65mm (2×2 焊盘, 见 §1.5) |

### 1.2 脚号 ↔ 引脚名 (X2SON DQN, 顶视图 — ★这是最关键的一张表)

| 脚号 | 引脚名 | I/O | 原厂说明 (摘要) |
|---|---|---|---|
| **1** | **OUT** | O | 稳压输出。必须接低 ESR 电容到地; 关断 (VEN < VEN(LOW)) 时内部 150Ω 下拉把 VOUT 拉到地 |
| **2** | **GND** | — | 公共地 |
| **3** | **EN** | I | 使能输入。低于 VEN(LOW) 关断并把输出放电到地; 高于 VEN(HI) 使能。**内部有 500kΩ 下拉** ⇒ 悬空 = 关断 |
| **4** | **IN** | I | 输入电源。需就近接 ≥1µF 陶瓷电容到地 |
| **5** | **Thermal Pad** | — | **散热焊盘: 接 GND 或悬空; 严禁接除 GND 以外任何电位**; 接大面积地平面改善散热 |

> ★**对照任务书模板的纠正**: 任务书给的 `{"1":"IN","2":"GND","3":"EN","4":"OUT","5":"NC"}` **不成立**。
> 原厂 X2SON 是 **1=OUT / 2=GND / 3=EN / 4=IN / 5=Thermal Pad**; 且 X2SON **没有 NC 脚** (NC 脚是 SOT-23 版的 pin 4)。

### 1.3 7 颗的电压档与网表对应 (原厂可订型号)

| ref | 网表值 | 原厂可订型号 | DNP? | 备注 |
|---|---|---|---|---|
| U_LDO_L33 | TPS7A20-33 | **TPS7A2033DQNR** (X2SON DQN) | 必装 | 3.3V / 150mA |
| U_LDO_IO33 | TPS7A20-33 | **TPS7A2033DQNR** | 必装 | 3.3V / 200mA |
| U_LDO_IO18 | TPS7A20-18 | **TPS7A2018DQNR** | 必装 | 1.8V / 100mA |
| U_LDO_L18 | TPS7A20-18 | **TPS7A2018DQNR** | DNP | 1.8V / 50mA |
| U_LDO_S12 | TPS7A20-12 | **TPS7A2012DQNR** | DNP | 1.2V / 250mA |
| U_LDO_S18B | TPS7A20-18 | **TPS7A2018DQNR** | DNP | 1.8V / 3mA |
| U_LDO_S28 | TPS7A20-28 | **TPS7A2028DQNR** | DNP | 2.8V / 156mA |

★**"换料不换板"成立**: 30 档固定电压 (0.8–5.5V, 25mV 步进) **全部共用 X2SON (DQN) 封装与同一脚号表** ⇒ 电压档变动不用改板。

### 1.4 三个封装变体 (脚号表不同, 别混用)

| 封装 | 代号 | 尺寸 | pin1 | pin2 | pin3 | pin4 | pin5 | pin6/pad |
|---|---|---|---|---|---|---|---|---|
| **X2SON (本项目用)** | **DQN** | 1.0×1.0mm | OUT | GND | EN | IN | Thermal Pad | — |
| SOT-23-5 | DBV | 2.9×2.8mm | IN | GND | EN | **N/C** | OUT | — |
| DSBGA-4 | YCJ / YCK | 0.612 / 0.616mm | A1=IN · A2=OUT · B1=EN · B2=GND | | | | | — |

### 1.5 关键电气与布局参数 (★画板要看)

| 参数 | 值 | 出处 |
|---|---|---|
| EN 门限 | VEN(LOW) ≤ 0.3V 关断 / VEN(HI) ≥ 0.9V 使能 | SBVS338H §6.5 |
| EN 内部下拉 | **500kΩ** (悬空 = 关断 ⇒ **必须画 EN 线**) | Table 4-1 (p.4) |
| 输入电压范围 | 1.6 – 6.0V | §6.3 |
| 输出电流 | 300mA (DQN/YCJ/YCK: IOUT 1mA–300mA) | §5.4 / §6.5 |
| 压差 (DQN) | VOUT ≥ 1.85V 时 145mV max @300mA | §6.5 |
| 关断输出放电 | 内部 150Ω 下拉 | Table 4-1 |
| RθJA | DQN(X2SON) **166.1 °C/W**; DBV(SOT-23) 187.1 °C/W | §5.4 p.6 |
| **推荐布局** | **Figure 7-8 "DQN Package (X2SON) Typical Layout"** (p.32): CIN 在 IN(4) 与 GND(2) 之间, COUT 在 OUT(1) 与 GND(2) 之间 | p.32 |

### 1.6 证据 URL

- **主证据 (原厂 datasheet)**: <https://www.ti.com/lit/ds/symlink/tps7a20.pdf> — SBVS338H, MARCH 2020 – REVISED JULY 2024
  - **PDF p.4** = Figure 4-3 "DQN Package, 4-Pin X2SON (Top View)" + Figure 4-4 + **Table 4-1 "Pin Functions: X2SON, SOT-23"** ★脚号表出处
  - PDF p.3 = Figure 4-1/4-2 (YCJ/YCK DSBGA) + Table "Pin Functions: DSBGA"
  - PDF p.6 = §5.4 Thermal Information (RθJA)
  - PDF p.32 = Figure 7-8 "DQN Package (X2SON) Typical Layout" ★布局照抄
  - PDF p.34+ = Package Outline **DQN0004A** / **DBV0005A** + Orderable Addendum (TPS7A2012/18/28/33 DQNR 全部在册)

---

## 2. U_SUPV —— 上电监督器 + 复位 (TPS3808G01 类)

### 2.1 器件与封装

| 项 | 值 |
|---|---|
| 原厂器件 | **TI TPS3808** (Low-IQ 可编程延时电压监督器) |
| 型号变体 | **TPS3808G01** = **可调阈值版** (VIT = 0.405V 典型, 用 R1/R2 分压设定); 固定档: G09/G12/G125/G15/G18/G19/G25/G30/G33/G50 |
| 封装 (推荐) | **DBV = SOT-23-6** (2.9×2.8mm 级), 厂商 land pattern 代号 **`DBV0006A`**; KiCad: `Package_TO_SOT_SMD:SOT-23-6` (★核对编号方向) |
| 封装 (备选, 更小) | **DRV = WSON-6 (2.00×2.00mm) 带散热焊盘**, 代号 **`DRV0006A`** / `DRV0006D` (★库内无 ⇒ 需自绘) |
| 脚数 | 6 (SOT-23) / 6 + 散热焊盘 (WSON) |

### 2.2 脚号 ↔ 引脚名 (★两套装法, 别混)

| 引脚名 | **SOT-23 (DBV) 脚号** | **WSON (DRV) 脚号** | I/O | 原厂说明 (摘要) |
|---|---|---|---|---|
| **CT** | **4** | **3** | I | 复位延时编程脚。接 40k–200kΩ 到 VDD = 固定延时; **接地参考电容 ≥100pF = 用户可编程延时** |
| **GND** | **2** | **5** | — | 地 |
| **MR** | **3** | **4** | I | 手动复位脚。**内部 90kΩ 上拉到 VDD** ⇒ 拉低则复位置位 |
| **RESET** | **1** | **6** | O | **开漏输出**。SENSE 低于阈值 或 MR 拉低 ⇒ 拉低; 恢复后保持低电平直到延时到。**需 10kΩ–1MΩ 外部上拉**, 允许上拉到高于 VDD 的电位 |
| **SENSE** | **5** | **2** | I | 电压采样脚。接被监控电压; 低于 VIT 则复位置位 |
| **VDD** | **6** | **1** | I | 供电。就近接 0.1µF 陶瓷电容 |
| Thermal Pad | — | Pad | — | 接地平面 |

### 2.3 ★网表纠正点 (改网表时务必看)

| 网表现状 | 问题 | 原厂对应 |
|---|---|---|
| `U_SUPV IN` (SUPV_SENSE) | 引脚名错 | 原厂叫 **SENSE** (DBV pin 5 / DRV pin 2) |
| `U_SUPV CT` | ✔ 名字对 | DBV pin **4** / DRV pin **3** |
| `U_SUPV RESET (开漏)` | ✔ 名字对 | DBV pin **1** / DRV pin **6**, **开漏, 必须外接上拉** |
| `U_SUPV VDD` | ✔ 名字对 | DBV pin **6** / DRV pin **1** |
| **网表缺失** | ★**GND (pin2/5) 没画** | 必须接 GND |
| **网表缺失** | ★**MR (pin3/4) 没画** | 内部 90kΩ 上拉 ⇒ 悬空=不复位, 但**建议显式接 VDD** 或留测试点 |

### 2.4 电气参数

| 参数 | 值 | 出处 |
|---|---|---|
| VDD 输入范围 | 1.7 – 6.5V | §6.3 (p.5) |
| VIT (G01 可调) | 0.405V 典型, R1+R2 = 4MΩ | §7.2 |
| RESET 漏电流 | 300nA max (V_RESET = 6.5V, 未置位) | §6.5 |
| MR 内部上拉 | 90kΩ | Table 5-1 |
| RESET 电流 | −5mA … +5mA | §6.1 |
| RθJA | DBV 180.9 / DRV 178.1 °C/W | §6.4 (p.5) |

### 2.5 证据 URL

- **主证据**: <https://www.ti.com/lit/ds/symlink/tps3808.pdf> — SBVS050N, MAY 2004 – REVISED AUGUST 2026
  - **PDF p.4** = **Figure 5-1 "DBV Package 6-Pin SOT-23 Top View"** + **Figure 5-2 "DRV Package 6-Pin (2.00mm × 2.00mm) WSON With Thermal Pad Top View"** + **Table 5-1 "Pin Functions"** ★脚号表出处
  - PDF p.5 = §6.3/6.4 (Recommended Operating Conditions, Thermal Information)
  - PDF p.6 = §6.5 (DC 电气)
  - PDF p.18+ = Mechanical (DBV0006A / DRV0006A) + Orderable Addendum

---

## 3. U_PWR_SW —— 关机负载开关 (SYS 主轨门控)

### 3.1 选型判据 vs 候选 (全部按原厂 datasheet 核过)

项目判据来源: `HW/POWER_SHUTDOWN_V3.md` §2 (8 条硬判据) —— ★**本表不替项目总工做最终裁决, 只给原厂数据供裁决**。

| 候选 | 封装 | Iout max | RON @5V / @3.6V | IQ | 反向阻断 | 状态 |
|---|---|---|---|---|---|---|
| **TPS22991** ★推荐 | **UQFN-4 RAA 0.85×0.75mm** (原厂 land pattern `RAA0004A`) | **3A** | **25mΩ / 25mΩ** | 6µA typ @3.3V (12µA max −40~85°C) | ✗ (但有 QOD 150Ω) | ✅ 4 脚最简, RON 达标, 封装最小 |
| TPS22916 | WCSP-4 YFP 0.78×0.78mm | 2A | 60mΩ / 70mΩ | **0.5µA typ** | ✅ **Always-ON true RCB** (反向漏 −300nA max) | 判据 3 (RON ≤40mΩ) **不达标** |
| TPS22917 | SOT-23-6 DBV | 2A | 80mΩ / 90mΩ | 0.5µA typ | ✅ Always-ON true RCB (−1µA max) | RON 不达标, 6 脚 |
| TPS22914B/C | DSBGA-4 YFP 0.74×0.74mm | 2A | 37mΩ / — | 7.7µA typ | ✗ | RON 最好但 IQ 超 5µA 判据, 且 WCSP 难焊 |
| TPS22918 | SOT-23-6 DBV | 2A | 52mΩ / — | — | ✗ (QOD 可配) | RON 不达标 |
| TPS22910A | WCSP-4 YZV 0.9×0.9mm | 2A | 60mΩ / 61mΩ | 2µA typ | ✅ Full-Time Reverse Current Protection | **ON 是 Active Low** ⇒ 与本设计 "ON 拉高=开机" 相反 |

★**推荐 TPS22991 的理由** (请项目总工裁决):
- 判据 2 (Iout ≥ 2A): **3A** ✔ 有余量
- 判据 3 (RON ≤ 40mΩ @3.7V): **25mΩ** ✔ 是候选里唯一大幅超标的
- 判据 4 (IQ ≤ 5µA): 6µA typ (3.3V) — ⚠️ **略超 5µA 判据**, 需裁决是否放宽; (若必须 ≤5µA 则只有 TPS22916/17 系列, 但 RON 不达标 ⇒ 判据 3 与 4 互斥, **必须二选一放宽**)
- 判据 5 (反向阻断): ✗ TPS22991 无 RCB ⇒ ★**风险: 关机插 USB 时 5V 仍可能经 SoC IO 反灌** ⇒ **必须补外围阻断措施** (或在 SYS 后加串联肖特基/或改用 TPS22916 并接受 RON 代价)。**这一条是本表最重要的一条待裁决项**。
- 判据 6 (面积 ≤ 2×2mm): **0.85×0.75mm** ✔ 全候选最小
- 判据 7 (−40~+85°C): ✔ (−55~+125°C)
- 判据 8 (ON 兼容 3.3V GPIO + 确定默认态): **Active High, 内部 500kΩ Smart Pulldown** ⇒ 悬空/高阻 = 关 ✔ **天然满足 "ON 脚下拉 = 默认关"**

### 3.2 脚号 ↔ 引脚名 (TPS22991 RAA, UQFN-4)

| 脚号 | 引脚名 | I/O | 原厂说明 (摘要) |
|---|---|---|---|
| **1** | **VIN** | I | 开关输入 |
| **2** | **ON** | I | **高有效** 开关使能。VIH(ON) = 0.8V, VIL(ON) = 0.35V, 迟滞 0.07V; **内部 500kΩ Smart Pulldown** (禁用时) |
| **3** | **VOUT** | O | 开关输出 |
| **4** | **GND** | — | 器件地 |

### 3.3 电气参数 (TPS22991)

| 参数 | 值 | 出处 |
|---|---|---|
| VIN 范围 | 1.0 – 5.5V | §1 |
| IMAX | **3A** | §6.5 |
| RON | 25mΩ typ @5V & @3.3V (25°C); 35mΩ max @−40~85°C | §6.5 p.6 |
| IQ (VIN) | 6µA typ @3.3V (25°C); 12µA max @−40~85°C | §6.5 p.6 |
| ISD (VIN) | 14nA typ @3.3V | §6.5 p.6 |
| QOD | 150Ω (关断时输出经此下拉到地) | §1 / §6.5 |
| ON 阈值 / 下拉 | VIH 0.8V / VIL 0.35V / RPD 500kΩ | §6.5 |
| 版本 | B/BN: tR = 141µs @3.3V; C/CN: tR = 662µs @3.3V (慢速版更防浪涌) | §1 |
| 封装 | RAA UQFN-4, **0.85 × 0.75mm, 0.4mm pitch** | §1 / Table 5-1 |

### 3.4 证据 URL

- **主证据**: <https://www.ti.com/lit/ds/symlink/tps22991.pdf> — SLVSFK0B, MAY 2024 – REVISED FEBRUARY 2025
  - **PDF p.4** = **Figure 5-1 "TPS22991 RAA Package, 4-Pin UQFN (Top View)"** + **Table 5-1 "Pin Functions"** ★脚号表出处
  - PDF p.6 = §6.5 Electrical Characteristics (RON / IQ / ISD / ON 阈值)
- 备选证据 (反向阻断型):
  - TPS22916: <https://www.ti.com/lit/ds/symlink/tps22916.pdf> — SLVSDO5F, **PDF p.3 Fig 5-1/5-2 + Table 5-1** (A1=VOUT, A2=VIN, B1=GND, B2=ON); p.5 §6.5 RCB 参数
  - TPS22917: <https://www.ti.com/lit/ds/symlink/tps22917.pdf> — SLVSDW8B, **PDF p.4 Fig 6-1 + Table 6-1** (1=VIN,2=GND,3=ON,4=CT,5=QOD,6=VOUT); p.6 §7.5
  - TPS22910A: <https://www.ti.com/lit/ds/symlink/tps22910a.pdf> — SLVSB49F, **PDF p.3 Table 1 Pin Assignments** (B=ON, B=GND, A=VIN, A=VOUT)
  - TPS22914B/C: <https://www.ti.com/lit/ds/symlink/tps22914.pdf> — SLVSCO0F, **PDF p.3 Fig 5-1 + Table 5-1**
  - TPS22918: <https://www.ti.com/lit/ds/symlink/tps22918.pdf> — **PDF p.3 Fig 5-1 + Table 5-1** (1=VIN,2=GND,3=ON,4=CT,5=QOD,6=VOUT), 封装代号 `DBV0006A`

---

## 4. U_EN_SW —— F13 底板主电源门控 (型号还没选)

### 4.1 定位 (★先讲清楚这块是干什么的)

| 项 | 值 | 来源 |
|---|---|---|
| 作用 | ★**底板主电源使能**: `CARRIER_BOARD_EN` (SOM P3_87) → `U_EN_SW.EN`; `U_EN_SW.IN` ← `RAIL_DEMO_5V` (demo 板 USB-C 5V); `U_EN_SW.OUT` → **`RAIL_BOARD_5V`** → 9 条 LDO/DC-DC 的 VIN + 6 条 EN | `HW/STEP1_LANDING_LIST.md` L152 |
| 电流需求 | RAIL_BOARD_5V 喂 7 颗 LDO (300mA max each) + 2 颗 DC-DC (3A max each) ⇒ **理论峰值远大于 2A**, 但其中多数 DNP | `HW/netlist_v1.csv` |
| 上电时序理由 | Forlinx 手册: 底板早于核心板上电会 "通电瞬间电流过大, 设备无法启动, 甚至对处理器造成不可逆转的损坏" | `HW/NETLIST_REV2_SPEC.md` §0③ |

### 4.2 ★推荐: TPS22991 (与 U_PWR_SW 同型, 脚号表一致)

**脚号 ↔ 引脚名 与 §3.2 完全相同**:

| 脚号 | 引脚名 |
|---|---|
| 1 | VIN |
| 2 | ON |
| 3 | VOUT |
| 4 | GND |

> ★**网表引脚名对应**: 网表 `U_EN_SW EN / IN / OUT / GND` ⇒ **EN = pin 2, IN = pin 1, OUT = pin 3, GND = pin 4**。

★**选它的理由**:
- `CARRIER_BOARD_EN` 是 3.3V 信号 ⇒ ON 阈值 VIH = 0.8V, VIL = 0.35V ⇒ 3.3V 直驱 OK, 且 1kΩ 上拉 (手册给的) 也在规格内
- **内部 500kΩ Smart Pulldown** ⇒ SOM 未上电 / 高阻时开关自动关 ⇒ 天然满足 Forlinx 要的 "严格控制上电时序"
- **VIN 最高 5.5V** ⇒ 吃 demo 板 USB-C 5V OK
- **3A / 25mΩ / 0.85×0.75mm** ⇒ 5V 轨总电流 (含 DNP 满额) 有余量, 面积最小
- **-55~+125°C** ⇒ 镜脚贴皮肤工况 OK
- ⚠️ **待裁决**: 若 5V 轨满额电流 > 3A (9 颗 LDO 全装 + 2 颗 DC-DC) ⇒ 需改用 TPS22990 (10A, 3.9mΩ, DML 10-pin WSON) 或并联

### 4.3 备选 (若必须带反向阻断)

| 型号 | 脚号 | 出处 |
|---|---|---|
| TPS22916 (YFP WCSP-4) | A1=VOUT, A2=VIN, B1=GND, B2=ON | SLVSDO5F p.3 Table 5-1 |
| TPS22990 (DML WSON-10) | CT=1, NC=2, VIN=3, thermal pad=4, VOUT=8,9,10, … | SLVSDK1C p.3 Fig 6-1 + Table 6-1 (10A / 3.9mΩ) |

### 4.4 证据 URL

- **主证据**: <https://www.ti.com/lit/ds/symlink/tps22991.pdf> — SLVSFK0B, **PDF p.4 Fig 5-1 + Table 5-1**, p.6 §6.5
- 备选: <https://www.ti.com/lit/ds/symlink/tps22916.pdf> (SLVSDO5F p.3) · <https://www.ti.com/lit/ds/symlink/tps22990.pdf> (SLVSDK1C p.3)

---

## 5. U_BATPROT —— 电池保护 IC (BQ2970)

### 5.1 器件与封装

| 项 | 值 |
|---|---|
| 原厂器件 | **TI BQ2970 / BQ2971 / BQ2972 / BQ2973** (1S 锂电保护, 过充/过放/过流/短路) |
| 封装 | **DSE = WSON-6 (1.50 × 1.50 × 0.75mm)**, 厂商 land pattern 代号 **`DSE0006A`** (原厂 PACKAGE OUTLINE p.32: 4X 0.5mm pitch, 焊盘 0.3mm 长, 中心散热焊盘); ★**KiCad 官方库无此尺寸 ⇒ 需自绘** |
| 脚数 | 6 (含 1 个 NC) |
| 规格阈值 | BQ2970: OVP 4.275V / UVP 2.800V / OCC −100mV / OCD 100mV / SCD 500mV; 检测延时 OVP 1.25s · UVP 144ms · OCD 8ms · OCC 8ms · SCD 250µs |
| 静态电流 | NORMAL 4µA typ / 5.5µA max; Shutdown 0.1µA |

### 5.2 脚号 ↔ 引脚名 (DSE WSON-6, 顶视图)

| 脚号 | 引脚名 | I/O | 原厂说明 (摘要) |
|---|---|---|---|
| **1** | **NC** | NC | **无连接 (电气开路)** |
| **2** | **COUT** | O | **充电 FET 栅驱动输出**。故障时由高变低 ⇒ 要求充电 FET 关断。**5MΩ 高阻电阻接 VSS** 用于栅电容放电 |
| **3** | **DOUT** | O | **放电 FET 栅驱动输出**。故障时由高变低 ⇒ 要求放电 FET 关断。**5MΩ 高阻电阻接 VSS** |
| **4** | **VSS** | P | **电芯负端 / 地**。所有内部测量以此为参考 |
| **5** | **BAT** | P | 器件供电输入 = 电池正端 (PACK+)。就近 0.1µF 去耦 |
| **6** | **V−** | I/O | **电压采样脚 (PACK−)**。与 VSS 构成差分测量。**应用电路: 2.2kΩ 电阻从 V− 连到系统 PACK−**; 内部有到 VBAT 的上拉 (100–550kΩ) |

### 5.3 ★★网表纠正点 (本条最关键 — 会导致保护完全失效)

| 网表现状 | 问题 | 原厂正解 |
|---|---|---|
| `U_BATPROT GATE` 一根网 → `Q1 GATE` + `Q2 GATE` (BAT_GATE) | ★★**原厂没有单一 GATE 脚**; 且**两管共栅 = 充放两个方向的 FET 同时被同一个信号控制 ⇒ 无法分别断开充/放 ⇒ 保护逻辑失效** | **Q1 (放电管) 栅 → DOUT (pin 3); Q2 (充电管) 栅 → COUT (pin 2)**; 两管**必须分开** |
| `U_BATPROT B+` | 名字非原厂名 | → **BAT (pin 5)** |
| `U_BATPROT B-` | 名字非原厂名 | → **VSS (pin 4)** |
| **网表缺失** | ★**V− (pin 6) 没画** | 必须补: V− ↔ 2.2kΩ ↔ 系统 PACK− (电芯负极节点) |
| **网表缺失** | ★**NC (pin 1) 没画** | 画成 NC / 悬空焊盘 |
| **网表缺失** | ★**两管栅源 5MΩ 没画** | 每管栅-源之间 5MΩ (原厂建议, 泄放栅电容) |
| **网表缺失** | BAT 脚的 330Ω + 0.1µF RC 滤波没画 | 原厂建议: BAT 串 330Ω (限反接电流) + 0.1µF 到地 |

### 5.4 ★Q1/Q2 的 MOS 选型 (★原厂直接点名了)

| 项 | 值 | 出处 |
|---|---|---|
| 原厂指定 FET | ★**"Use the CSD16406Q3 FET for the application."** | **BQ2970 SLUSBU9I PDF p.20** §9.2.2 |
| 原厂选型判据 | Vdss = 25V; 每管 Rds(on) = **7.5mΩ @ Tj=25°C, Vgs=3.5V**; Imax > 50A (短路 350µs 工况) | 同上 p.20 |
| CSD16406Q3 参数 | Vds = 25V; Vgs(th) = 1.4/1.8/2.2 V (min/typ/max); Rds(on) = 5.9mΩ typ @Vgs=4.5V (7.4mΩ max), 4.2mΩ @Vgs=10V; Qg = 5.8nC; Qgd = 1.5nC; Ciss = 840pF | CSD16406Q3 SLPS202B PDF p.3 §5.1 |
| 封装 | **Q3 = SON 3.3 × 3.3mm** (8 pin + 散热焊盘), 尺寸表 §7.1, PCB pattern §7.2, 钢网 §7.3 (散热焊盘 1.75×2.45mm); ★**KiCad 官方库无此尺寸 ⇒ 需自绘** | SLPS202B p.8–9 |

★**CSD16406Q3 脚号 (Q3 封装, 底视)**:
| 脚号 | 引脚名 |
|---|---|
| 1, 2 | **GATE** |
| 3, 4 | **SOURCE** (common source) |
| 5, 6, 7, 8 | **DRAIN** |

> 证据: 原厂 PDF p.4 图 M0161-01 / M0161-02 顶视/底视 (GATE / Source / DRAIN 三块标注) + 同封装 TI CSD87503Q3E 官方 gpn 页 "Table 1. Pin Configuration" 明确 "Pin 1 Gate 1 / Pin 2 Common Source / Pin 3 Gate 2 / Pin 4 Common Source / Pins 5, 6 Drain 2 / Pins 7, 8 Drain 1" 的排布方式。★**注意**: CSD16406Q3 本身 datasheet 里没有文字 pin table (只有图), 画 KiCad 封装时**建议以 TI 官方 CAD/land pattern 或 KiCad 官方库 `Package_SON:SON-3.3x3.3mm_8P` 为准并实测复核**。

### 5.5 电气/耐压

| 参数 | 值 | 出处 |
|---|---|---|
| BAT 绝对最大 | −0.3 … 12V | §6.1 |
| V− 绝对最大 | BAT−28 … BAT+0.3 V | §6.1 |
| 推荐工作 BAT | −0.3 … 8V | §6.3 |
| RθJA (DSE) | 190.5 °C/W | §6.4 p.5 |
| 过流保护采样 | Vds 感应法 (外部 2.2kΩ 到 PACK−) | §5.1.3 / Fig 9-1 p.19 |

### 5.6 证据 URL

- **主证据**: <https://www.ti.com/lit/ds/symlink/bq2970.pdf> — SLUSBU9I, MARCH 2014 – REVISED AUGUST 2024
  - **PDF p.3** = **Figure 5-1 "DSE Package 6-PIN WSON Top View"** + **Table 5-1 "Pin Functions"** ★脚号表出处 (BAT=5, COUT=2, DOUT=3, NC=1, VSS=4, V−=6)
  - PDF p.4 = §5.1 Pin Descriptions (逐脚说明)
  - PDF p.5 = §6.3/6.4 (Recommended Operating Conditions, Thermal)
  - **PDF p.19** = Figure 9-1 "Typical Application Schematic, BQ2970" (含 2.2kΩ / 330Ω / 0.1µF / 5MΩ)
  - **PDF p.20** = §9.2.2 ★**"Use the CSD16406Q3 FET for the application"** + FET 选型判据 (Vdss 25V, 7.5mΩ @3.5V, Imax>50A)
  - PDF p.23+ = Mechanical (DSE0006A) + Orderable Addendum
- **Q1/QQ2 FET 证据**: <https://www.ti.com/lit/ds/symlink/csd16406q3.pdf> — SLPS202B, **PDF p.3 §5.1 电气表**, **p.4 图 M0161-01/02 (GATE/Source/DRAIN)**, **p.8 §7.1 Q3 Package Dimensions**, **p.9 §7.2 Recommended PCB Pattern / §7.3 Recommended Stencil Opening**

---

## 6. Q1 —— 电池保护高边 N-MOS (型号待定 → 本表给原厂点名型号)

见 §5.4。摘要:

| 项 | 值 |
|---|---|
| ★推荐型号 | **CSD16406Q3** (TI NexFET) —— **BQ2970 原厂 datasheet p.20 直接点名** |
| 封装 | **Q3 = SON 3.3 × 3.3mm, 8 pin** (1,2=GATE · 3,4=SOURCE · 5–8=DRAIN) |
| 关键参数 | Vds 25V / Vgs(th) 1.4–2.2V / Rds(on) 5.9mΩ typ @4.5V / Qg 5.8nC |
| 证据 | BQ2970 SLUSBU9I p.20 + CSD16406Q3 SLPS202B p.3, p.4, p.8, p.9 |
| ⚠️ 风险 | ★**Vgs(th) max 2.2V**: BQ2970 的 COUT/DOUT 高电平仅 3.4–3.7V (BAT 供电) ⇒ **必须核对 3.4V 栅压下的实际 Rds(on)**, 原厂判据写的是 "7.5mΩ @ Vgs=3.5V" ⇒ **与 CSD16406Q3 官方表的 4.5V 条件不同**, 需按原厂判据实测/选更匹配的 FET。**这是选型硬判据, 请项目总工裁决。** |

---

## 7. BT_432243 —— 1S 锂聚合物电池 3.7V ≥420mAh

### 7.1 已查实 (库内官方值, 来自项目规格文件)

| 项 | 值 | 出处 |
|---|---|---|
| 型号 | **丰江 432243** | `HW/POWER_TOPOLOGY_RF1_3V3V_UVP.md` L227 / `HW/EMC_PRECHECK.md` L84 |
| 尺寸 | **4.3 × 22.0 × 43.5mm** (厚 × 宽 × 长) | `HW/POWER_TOPOLOGY_RF1_3V3V_UVP.md` L227 (标 `[官方]` 库内网表 `BT_432243`) |
| 电压/容量 | 3.7V 标称 / ≥420mAh / 4.2V 满充 | `HW/EMC_PRECHECK.md` L84 / `HW/POWER_BUDGET_V3.md` L260 |
| 装夹处 | 镜腿主 PCB (镜脚) | `HW/CHARGE_BOARD_SPEC.md` L382 |
| 厚度预算 | 4.3mm 电芯 ⇒ 镜腿 7.3mm (名义 7.0) | `HW/POWER_BUDGET_V3.md` L260–261 |

### 7.2 封装 / 焊盘 —— ★未查到 (不许猜)

| 项 | 状态 |
|---|---|
| 电池两极的物理引出形式 (焊片 / 引线 / JST-PH2.0 座) | ★**未查到** —— 丰江 (Fengjiang) 官网未检索到 432243 的原厂规格书 PDF, 搜索命中的均为第三方零售页 (aliyun/hackstore 等) 与尺寸不符的型号 (如 552535 / 602040 / 502030) ⇒ **按铁律不采信** |
| B+ / B− 焊盘间距与尺寸 | ★**未查到** |
| 建议动作 | ★**走采购硬判据**: 向供应商索取 432243 原厂规格书 (含尺寸图 + 极性标识 + 引出形式), 拿到后再定 footprint。**本项在网表里标 [待采购], 不要先画焊盘**。 |

### 7.3 网表引脚名

| 网表名 | 建议原厂名 | 脚号 |
|---|---|---|
| `BT_432243 B+` | 电芯正极 | 1 (待原厂规格书确认) |
| `BT_432243 B-` | 电芯负极 | 2 (待原厂规格书确认) |

---

## 8. J_TYPE_C —— USB Type-C 16p 母座 (demo 板 5V 供电 + USB 数据入口)

### 8.1 器件与封装

| 项 | 值 |
|---|---|
| 原厂器件 | **GCT (Global Connector Technology) USB4105** — "USB Type C Receptacle for USB 2.0 SMT Type, PCB Top Mount" |
| 可订型号 | `USB4105-XXX-XXX` (镀层/卷带选项), 壳体 stake 长度: 空 = 0.95mm / `060` = 0.60mm / `120` = 1.20mm |
| 触点 | **16 脚** (USB 2.0 Type-C 母座 = A1/A4/A5/A6/A7/A8/A9/A12 + B1/B4/B5/B6/B7/B8/B9/B12) |
| 封装 | **SMT 贴片 (PCB Top Mount), 带 2 个 Ø0.50mm 定位孔 + 2 个 Ø0.65mm 壳体固定孔**; 外形 8.64 × 6.40mm (焊盘区), 主体高 3.50mm |
| 焊盘 | **16 × 0.20mm 宽**, 间距 0.50mm (pitch), 焊盘长度 0.45mm (4×) / 0.25mm (2×) / 0.75mm (2×) 等 (见原厂图纸 "Recommended PCB Layout") |
| KiCad footprint | ★**GCT USB4105 无现成 KiCad 封装 ⇒ 需自绘**; `Connector_USB.pretty:USB_C_Receptacle_*` (Amphenol / CNCTech / G-Switch) 可作几何参考 |
| 载流 | VBUS 脚合计 **5.00A**; GND 脚合计 **6.25A**; **A5/B5 (CC) 1.25A**; 其余每脚 **0.25A** |
| 耐压 | 48V DC; 绝缘 100MΩ min; 接触电阻 40mΩ max (初始) |
| 耐久 | 20,000 次插拔 |
| 工作温度 | −40 ~ +85°C |

### 8.2 ★脚号 ↔ 引脚名 (★USB-IF 物理脚位, 16 脚)

★**这是任务书要的核心**: 网表里的 `J_TYPE_C` 用的正是 **USB-IF 物理脚 A1..B12 + shield**。原厂图纸 "Recommended PCB Layout" 明确标出了焊盘顺序:

| 焊盘序 (原厂图纸, 从左到右) | USB-IF 脚 | 信号 | 匹配顺序 |
|---|---|---|---|
| 1 | **A1** | GND | First |
| 2 | **B12** | GND | First |
| 3 | **A4** | VBUS | First |
| 4 | **B9** | VBUS | First |
| 5 | **B8** | SBU2 | Second |
| 6 | **A5** | CC1 | Second |
| 7 | **B7** | Dn2 (D−) | Second |
| 8 | **A6** | Dp1 (D+) | Second |
| 9 | **A7** | Dn1 (D−) | Second |
| 10 | **B6** | Dp2 (D+) | Second |
| 11 | **A8** | SBU1 | Second |
| 12 | **B5** | CC2 | Second |
| 13 | **B4** | VBUS | First |
| 14 | **A9** | VBUS | First |
| 15 | **B1** | GND | First |
| 16 | **A12** | GND | First |
| — | **SHELL** | GND (屏蔽壳) | — |

★**图上原样文字 (照抄, 画 KiCad 封装时按这个顺序)**:
`A1 B12 A4 B9 B8 A5 B7 A6 A7 B6 A8 B5 B4 A9 B1 A12`

### 8.3 网表对应

| 网表现状 | 对应原厂脚 | 状态 |
|---|---|---|
| `J_TYPE_C A4+A9+B4+B9` → VBUS_5V | A4 / A9 / B4 / B9 | ✔ 四脚全并 (原厂 VBUS 合计 5.00A) |
| `J_TYPE_C` → USB_CC1 | **A5** (CC1) | ✔ |
| `J_TYPE_C` → USB_CC2 | **B5** (CC2) | ✔ |
| `J_TYPE_C` → USB_D_P | **A6** (Dp1) **+ B6** (Dp2) | ★网表只写了一处 ⇒ 建议 A6+B6 并联 |
| `J_TYPE_C` → USB_D_N | **A7** (Dn1) **+ B7** (Dn2) | ★同上 |
| `J_TYPE_C` → GND | A1 / B12 / A12 / B1 (4 脚 GND, 合计 6.25A) | ★**网表只挂 1 个 GND 节点 ⇒ 4 脚全接** |
| `J_TYPE_C` → NC | **A8 / B8** (SBU1 / SBU2) | ✔ |
| 屏蔽壳 | SHELL | ★**必须接 GND** (原厂: "The receptacle shell shall be connected to the PCB ground plane" — USB-IF 规范 §) |

### 8.4 证据 URL

- **主证据 (原厂图纸, 授权分销商 DigiKey 镜像的原厂 PDF)**: <https://media.digikey.com/pdf/Data%20Sheets/GCT%20PDFs/USB4105.pdf>
  - 标题栏: **USB4105 / USB Type C Receptacle for USB 2.0 SMT Type, PCB Top Mount / Drawing Date 4th October 2019 / By CC / Revision B PCN, B3 24/02/23**
  - **Sheet 1/2** = 外形图 + **"Recommended PCB Layout"** (焊盘顺序 `A1 B12 A4 B9 B8 A5 B7 A6 A7 B6 A8 B5 B4 A9 B1 A12`, 16×0.20mm 焊盘宽, 8.94mm 板边距离, 2×Ø0.50 定位孔) + **Pin/Signal 表** (A1/B12/A4/B9/A5/B8/A6/B7/A7/B6/A8/B5/A9/B4/A12/B1 + SHELL GND)
  - Sheet 2/2 = 卷带包装图
- **USB-IF 规范 (物理脚位定义权威源)**: <https://www.usb.org/sites/default/files/USB%20Type-C%20Spec%20R2.0%20-%20August%202019.pdf>
  - **Table 3-5 "USB Type-C Receptacle Interface Pin Assignments for USB 2.0-only Support"** (p.41 附近) —— A/B 12 脚功能与匹配顺序
  - p.41 = "11. The receptacle shell shall be connected to the PCB ground plane. 12. All VBUS pins shall be connected together… 13. All Ground return pins shall be connected together…"
- **16 脚定义 (为什么 16p 而不是 24p)**: <https://www.usb.org/sites/default/files/USB%20Type-C_Compliance%20Document_Rev_2_1b_June_2021.pdf> — "USB 2.0 Type-C receptacle: **16 contacts: A1, A4, A5, A6, A7, A8, A9, A12, B1, B4, B5, B6, B7, B8, B9, and B12**" ✔ 与 GCT USB4105 完全一致

---

## 9. U_DCDC_VCORE / U_DCDC_VIO —— TPS62130A (★已 DNP)

### 9.1 器件与封装

| 项 | 值 |
|---|---|
| 原厂器件 | **TI TPS62130A** (3A 17V 降压转换器, **可调输出版本**) |
| ★关键区别 | **TPS62130A 的 PG 极性 = EN 为低时 PG 输出低** (固定版 TPS62130 = 高阻) —— 网表注释里"PG 极性待原厂核"这条, **原厂已答: A 版 PG 是低有效** |
| 封装 | **RGT = VQFN-16 (3.00 × 3.00mm) 带散热焊盘**, 厂商 land pattern 代号 **`RGT0016C`** (原厂 PACKAGE OUTLINE p.40: 中心散热焊盘 **1.68mm** 方形, 12X 0.5mm pitch); KiCad: `Package_DFN_QFN:VQFN-16-1EP_3x3mm_P0.5mm_EP1.68x1.68mm` (★核对编号方向) |
| 脚数 | 16 + 散热焊盘 |
| DNP 原因 | ★**SoM 自带 PMIC ⇒ 主板不产 SoC 核心/IO 轨** ⇒ 首版不贴 (网表 DNP 标记保留) |

### 9.2 脚号 ↔ 引脚名 (RGT VQFN-16, 顶视图)

| 脚号 | 引脚名 | I/O | 原厂说明 (摘要) |
|---|---|---|---|
| **1, 2, 3** | **SW** | O | 开关节点。SW 与 COUT 之间接电感 |
| **4** | **PG** | O | 输出 Power Good (**High = VOUT 就绪, Low = VOUT 低于标称**); **开漏, 需上拉电阻**。★A 版: EN 低时 PG 为低 |
| **5** | **FB** | I | 可调版反馈输入。接分压电阻; **固定输出版建议接 AGND** 改善热性能 |
| **6** | **AGND** | — | 模拟地。**必须直接连散热焊盘与公共地平面** |
| **7** | **FSW** | I | 开关频率选择 (低 ≈ 2.5MHz, 高 ≈ 1.25MHz) |
| **8** | **DEF** | I | 输出电压比例选择 (低 = 标称, 高 = 标称 +5%) |
| **9** | **SS/TR** | I | 软启动/跟踪。接外部电容设定上升时间 |
| **10** | **AVIN** | I | 控制电路供电。接与 PVIN 同源 |
| **11, 12** | **PVIN** | I | 功率级供电。接与 AVIN 同源 |
| **13** | **EN** | I | 使能 (高 = 开, 低 = 关) |
| **14** | **VOS** | I | 输出电压采样脚 |
| **15, 16** | **PGND** | — | 功率地。**必须直接连散热焊盘与公共地平面** |
| **EP (焊盘)** | **Exposed Thermal Pad** | — | 必须连 AGND (pin 6) + PGND (pin 15,16) + 公共地平面; 必须焊接以散热 |

★**网表引脚名对应**:
| 网表名 | 原厂脚号 |
|---|---|
| `U_DCDC_VCORE EN` / `U_DCDC_VIO EN` | **13** |
| `U_DCDC_VCORE PG` / `U_DCDC_VIO PG` | **4** (开漏, 需上拉) |
| `U_DCDC_VCORE VIN` / `U_DCDC_VIO VIN` | **10 (AVIN) + 11/12 (PVIN)** |
| `U_DCDC_VCORE SW` | **1, 2, 3** |

### 9.3 电气参数

| 参数 | 值 | 出处 |
|---|---|---|
| 输入范围 | 3 – 17V | §6.3 / §1 |
| 输出电流 | 3A | §1 |
| 开关频率 | 2.5MHz (FSW 低) / 1.25MHz (FSW 高) | Table 6-1 |
| 开关节点电压范围 | 见 datasheet | §6.3 |
| EN 阈值 | 高 = 使能 | Table 6-1 |
| RθJA | RGT 16 pins 见 §5.4 | — |

### 9.4 证据 URL

- **主证据**: <https://www.ti.com/lit/ds/symlink/tps62130a.pdf> — SLVSAG7F, NOVEMBER 2011 – REVISED NOVEMBER 2021
  - **PDF p.3** = **Figure 6-1 "16-Pin VQFN With Exposed Thermal Pad (RGT) Top View"** + **Table 6-1 "Pin Functions"** ★脚号表出处
  - PDF p.3 = Device Comparison Table (★TPS62130A vs TPS62130 的 PG 极性差别)
  - PDF p.18+ = Mechanical (RGT0016C) + Orderable Addendum (TPS62130ARGTR 等)

---

## 10. CONN_CAM —— HIROSE FH35C-31S-0.3SHW(50) (31p / 0.3mm 背夹式双面触点)

### 10.1 器件与封装 (★型号已定, 只缺脚号方向 → 本节把它补齐)

| 项 | 值 |
|---|---|
| 原厂器件 | **HIROSE FH35C-31S-0.3SHW(50)** |
| 原厂 Code Number | **CL580-2923-7-50** (HIROSE 内部物料号) |
| 系列 | **FH35C = 0.3mm pitch, 0.9mm height, back flip type dual-sided FPC connector** (原厂系列规格书首页原文) |
| 触点方向 | **Top & Bottom (上下双面触点)** — 原厂产品页 "Contact Orientation: Top & Bottom" |
| FPC 厚度 | **0.2mm** (原厂 "FFC/FPC Thickness 0.2mm"; 兼容 0.2±0.03mm) |
| 插拔方向 | 横向 (Horizontal); 锁扣在背面 (Back flip) |
| 尺寸 (31p) | **A = 10.9mm** (长), B = 8.4mm, C = 9.0mm, D = 9.63mm, E = 10.33mm, F = 9.6mm (原厂 DIMENSION TABLE) |
| 额定 | 30V AC/DC; **0.2A/触点**; 接触电阻 100mΩ max (含 FPC 12mm 体阻) |
| 温度 | 工作 −55 ~ +105°C; 存储 −10 ~ +50°C (打包态) |
| 保持力 | 0.2N × 触点数 min (初始) |
| 寿命 | 10 次插拔 (原厂规格书 MECHANICAL OPERATION) |

### 10.2 ★脚号 ↔ 引脚名 (★31 脚, 双排交错)

**原厂 Recommended PCB Mounting Pattern (底视, "Connector image: underside") 的焊盘排布**:

| 排 | 脚号 | 数量 | 说明 |
|---|---|---|---|
| **上排 (Top contact)** | **偶数脚: 2, 4, 6, …, 30** | **(n−1)/2 = 15** | 上排焊盘 (底部触点, 长度 0.65±0.03mm) |
| **下排 (Bottom contact)** | **奇数脚: 1, 3, 5, …, 31** | **(n+1)/2 = 16** | 下排焊盘 (长度 0.8±0.03mm) |
| 合计 | 1 – 31 | **31** | 交错 (staggered) 排列, 同排 pitch **0.3mm**, 两排错开半 pitch |

★**pin 1 位置**: 原厂图纸明确标注 **"Contact No. 1" 指向下排最右侧焊盘**, **"Contact No. 2" 指向上排最右侧焊盘**; 编号沿排**自右向左**递增 (与 "Recommended FPC" 图的左→右标注互为镜像, 因为一个是底视一个是 FPC 正视)。

★**尺寸公式 (原厂图纸框内原文, n = 触点数)**:
- 上排跨度 = **((n−1)/2) × 0.3 ± 0.02**
- 下排跨度 = **((n+1)/2) × 0.3 ± 0.02**
- 位置度公差: ⊕ 0.02 | X (PCB 视图) / ⊕ 0.02 | Y (钢网视图)

### 10.3 Land pattern / 钢网 (★直接拿去画 KiCad footprint)

| 参数 | 值 | 出处 |
|---|---|---|
| 焊盘宽 (沿 pitch 方向) | **0.3 ± 0.02mm** | Recommended Land Dimensions |
| 上排焊盘长 | **0.65 ± 0.03mm** | 同上 |
| 下排焊盘长 | **0.8 ± 0.03mm** | 同上 |
| 上排内缘到参考线 | 0.35 (参考) | 同上 |
| 两排内缘间距 | **2.15 ± 0.03mm** | 同上 |
| 垂直总跨 | (3.6) (参考) | 同上 |
| 端部固定焊盘 | 0.4 ± 0.03 / 0.5 ± 0.03 / 0.2 ± 0.03mm | 同上 |
| 钢网厚度 | t = 0.1mm | Recommended Land and Metal Mask Dimensions |
| 钢网上排开口 | 0.55 ± 0.02mm; 下排开口 0.65 ± 0.02mm; 开口宽 **0.23 ± 0.02mm** | 同上 |
| 视图方向 | ★**"Connector image: underside"** (即从板底看焊盘图) | 同上 |
| FPC 侧焊盘 | 宽 0.1±0.02mm; 同侧间距 0.6mm; 交错半间距 0.3mm; 触点长 0.75/0.85mm; 加固板厚 0.2±0.03mm | Recommended FPC Dimensions |

### 10.4 证据 URL

- **主证据 1 (原厂 2D 图, PDF)**: <https://www.hirose.com/en/product/p/CL0580-2923-7-50/documents?path=%2Fapi%2Fv1%2Fproducts%2FCL0580-2923-7-50%2Fdocuments%2Fdrawing_2d%2Fcontent%3Flang%3DEN>
  - 图号 **EDC3-338903-01** (7 sheets, Nov.1.2026)
  - **Sheet 1** = 外形 + **"RECOMMENDED PCB MOUNTING PATTERN"** (含 Contact No.1 / No.2 标注, 公式 ((n±1)/2)×0.3) + **"RECOMMENDED STENCIL PATTERN"**
  - Sheet 2 = RECOMMENDED FPC (左→右 Contact No.1 标注, 0.3mm 交错)
  - Sheet 4 = DIMENSION TABLE (31p: A=10.9, B=8.4, C=9.0, D=9.63, E=10.33, F=9.6)
- **主证据 2 (原厂系列规格书 PDF)**: <https://www.hirose.com/en/product/series/FH35C/documents?path=%2Fapi%2Fv1%2Fseries%2FFH35C%2Fdocuments%2Fproduct_series_catalog%2Fcontent%3Flang%3DEN>
  - 首页 = "0.3 mm pitch, 0.9 mm height, back flip type dual-sided FPC connector"
  - **p.3 "Recommended Land Dimensions"** = §10.3 全部 land/钢网尺寸
  - p.4 "Recommended Land and Metal Mask Dimensions" = 钢网尺寸
  - p.5 "Recommended FPC Dimensions" = FPC 侧焊盘
- **主证据 3 (原厂规格书)**: <https://www.hirose.com/en/product/p/CL0580-2923-7-50/documents?path=%2Fapi%2Fv1%2Fproducts%2FCL0580-2923-7-50%2Fdocuments%2Fspec_sheet%2Fcontent%3Flang%3DEN> — 30V/0.2A/接触电阻/保持力/温度
- **原厂产品页**: <https://www.hirose.com/en/product/p/CL0580-2923-7-50> (31 positions · 0.3mm pitch · 0.2mm FPC · Top & Bottom contact · Back actuator)

---

## 11. CONN_LIGHT —— ★**已定案 2026-11-04: HIROSE FH12-22S-0.5SH(55) (22p / 0.5mm, Pi5 同规)**

> ★**本节整段重写**: 原 §11 是"40p/0.5mm 座 · 型号未定 · 给 4 个候选" (那是 **Radxa Display 8HD** 时代的结论) ⇒
> demo 屏已换 **Waveshare 2.8inch DSI LCD (SKU 22028)**, 原厂线 = **22p(0.5mm) ↔ 15p(1.0mm)** ⇒ **板侧座定为 22p/0.5mm**。

| 项 | 值 | 来源 |
|---|---|---|
| 型号 | **HIROSE FH12-22S-0.5SH(55)** | RPi 官方 CM4IO/CM5IO KiCad 器件属性 (Field5/Field6) |
| 规格 | 22 位置 / **0.5mm pitch** / 右角(水平) / 表面贴装 / **Bottom Contact** / 1 个固定柱 | 官方封装名与描述 |
| 官方 land pattern | **有** —— `Hirose_FH12-22S-0.5SH_1x22-1MP_P0.50mm_Horizontal.kicad_mod` (RPi 官方 CM5IO.pretty) ⇒ **几何已抄进 `HW/PCB/display_fpc_params.json`** | 同上 |
| 焊盘 | 22 个, **0.3 × 1.3mm** 矩形, pitch 0.5, 焊盘行 y = -1.85, **pad1 在 +x 端 (x=+5.25)** | 官方 .kicad_mod 逐值抄录 |
| 本体 / Courtyard | F.Fab x -7.05..+7.05, y -1.2..+3.4 · Courtyard ±8.55 × -3.0..+4.9 | 同上 |
| ★★**针序** | ★**照 Raspberry Pi 5 官方 DISPLAY 座 (J4)**: 1=GND 2=DSI1_DN1 3=DSI1_DP1 4=GND 5=DSI1_CN 6=DSI1_CP 7=GND 8=DSI1_DN0 9=DSI1_DP0 10=GND 11=SCL0 12=SDA0 13=GND 14=3V3 15=3V3 | Pi5 官方原理图 RP-008350 (J4) |
| ★16..22 | 在 Pi5 上是 **NC** ⇒ 被动线的 22p 端也必然 NC ⇒ **本板自用**: lane2=16/17 · lane3=18/19 · 20/21/22 预留地 ⇒ **4-lane 能力保留, 不必上第二颗座** | Pi5 原理图红叉 + 线缆直通推论 |
| ★★**不可混抄** | ★**CM5IO 的 22p 针序 ≠ Pi5 DISPLAY 座** (CM5IO: 2/3=D0 · 5/6=D1 · 8/9=CLK · 20/21=I2C) ⇒ 照 CM5IO 抄 ⇒ 屏必不亮 | CM5IO 官方 PCB 焊盘网表 |
| 屏侧 | **15p / 1.0mm** (Waveshare 屏原生) ⇒ 靠官方 "DSI Cable-12cm" 22p↔15p 线连接 | Waveshare 官方 wiki |
| 配套线 | Waveshare 『DSI Cable-12cm』 (或 RPi 官方 22-way↔15-way FFC) | 同上 |

★**逐针表**: `HW/PCB/PI5_DSI_22P_PINOUT.md` (含三条独立证据) · 机器可读 `HW/PCB/pi5_dsi_22p.json`
★**板级复核**: `state/verify_display_fpc.py` (针号→网络 / 焊盘几何 / 与其它器件外框不打架) ⇒ 22/22 全过
★**未决 (须实物核对)**: 买线后万用表核 22p 端针序 (1 脚方向 / 3V3 位置) + 确认线缆 22p 端触点朝向 (底接触?)

---

## 11.5 U_TEMP —— TI TMP117 数字温度计 (★**2026-11-04 04:0x 补, 并订正脚号**)

| 项 | 值 | 出处 |
|---|---|---|
| 型号 / 封装 | **TMP117**, **WSON (6) = DRV0006B**, 2.00 × 2.00 mm, 0.8mm max height | TI SNOSD82D §1 器件表 ("WSON (6) — 2.00 mm × 2.00 mm") |
| ★★**脚位 (官方 6 脚)** | **1 = SCL · 2 = GND · 3 = ALERT · 4 = ADD0 · 5 = V+ · 6 = SDA** | TI SNOSD82D §5 **Table 5-1 "Pin Functions"** + Figure 5-1 (DRV 顶视: 1=左上 SCL, 2=左中 GND, 3=左下 ALERT, 4=右下 ADD0, 5=右中 V+, 6=右上 SDA) |
| ★**之前的错** | ★**2026-11-04 之前我们把它写成 4 脚 (1=SDA 2=SCL 3=VDD 4=GND) ⇒ 与原厂脚号完全对不上** ⇒ 照通用 IC 封装焊上去必然不工作 | (本次自查) |
| 脚距 / 焊盘 | **0.65mm** 脚距 ("4X (0.65)") · 每脚 **0.45 × 0.30mm** ("6X (0.45)" / "6X (0.3)") · **两列焊盘中心距 1.95mm** ("(1.95)") | TI 原厂 **EXAMPLE BOARD LAYOUT**, 图纸号 **4223922/A 09/2017** |
| ★**散热焊盘 (EP)** | ★**不画、不焊** —— 原厂明确: "The package thermal pad is **not connected to the device ground** and **should be left unsoldered for best measurement accuracy**"; 若要焊, 必须接地或悬空 | TI SNOSD82D §10 Application Information / §10.1 Layout Guidelines |
| 地址 | **ADD0 (pin4) 接 GND ⇒ I2C 地址 0x48** (原厂: ADD0 可接 GND / V+ / SDA / SCL) | TI Table 5-1 |
| ALERT (pin3) | 开漏输出 (过温/数据就绪告警), **需上拉** ⇒ demo 悬空 (原厂允许); 若要告警上报需另占一个 SoM GPIO | TI Table 5-1 |
| 板上实现 | `state/tmp117_footprint.py` 自绘官方 land pattern (库内无 WSON-6 2×2) · 焊盘 0.45×0.30 / 脚距 0.65 / 列距 1.95 / 无 EP | 本项目 |

## 12. ★仍未查到 / 需采购硬判据的清单

| # | 器件 | 缺什么 | 建议动作 |
|---|---|---|---|
| 1 | **BT_432243** | ★**电池两极引出形式 + 焊盘尺寸全部未查到** (丰江 432243 原厂规格书未检索到; 第三方零售页型号/尺寸不符, 按铁律不采信) | 走采购硬判据: 向供应商索取 432243 原厂规格书 (尺寸图 + 极性 + 引出形式); **在此之前网表标 [待采购], 不要先画焊盘** |
| 2 | ~~**CONN_LIGHT**~~ | ★**2026-11-04 已定案** (HIROSE FH12-22S-0.5SH(55), 22p/0.5mm, 官方封装已抄录, 见 §11) ⇒ ★**仅剩实物核对**: 线缆 22p 端针序 + 触点朝向 | 买线后万用表核针序 (与 SoM DF40C pin1 行问题同级) |
| 3 | **Q1 / Q2** | ★**Vgs 3.4V 下的实际 Rds(on) 未查到** (原厂判据写 7.5mΩ @3.5V, 但 CSD16406Q3 官方表只有 4.5V/10V 条件) | 按 BQ2970 §9.2.2 判据 (Vdss=25V, 7.5mΩ@3.5V, Imax>50A) 选 FET; 或选 Vgs(th) 更低的型号 |
| 4 | **U_PWR_SW / U_EN_SW** | ★**反向阻断 (判据 5) 与 IQ ≤5µA (判据 4) 与 RON ≤40mΩ (判据 3) 三者在原厂在售型号里互斥** —— TPS22991 只满足 RON; TPS22916/17 满足 IQ+RCB 但 RON 60–90mΩ | ★**请项目总工裁决放宽哪一条**; 本文只给原厂数据, 不替裁 |
| 5 | **U_SUPV** | ★**该器件在最新网表里已标 DNP** (SoM 内部 PMIC 已做上电复位) ⇒ 封装/脚号虽已查实, 但**首版不贴** | 保留 footprint 占位 + DNP 标记 |
| 6 | **候选 B/C/D 的原厂封装图** | 未取得可引用的原厂 Product Brief PDF | 向原厂/授权分销商索取 |

---

## 13. 纪律自检

- ★**只写了 2 个文件**: `HW/PCB/PINOUT_FOOTPRINT_SPEC.md` (本文) + `HW/PCB/pinout_footprint.json`
- ★**未改**: 网表 / 规格 JSON / 板文件 / 脚本 / issue_log / tracker —— 全部只读
- 临时下载: 全部在 `/tmp/parts/` (未塞进项目目录); 图像分析用的临时 PNG 在 `~/.openclaw/workspace/.tmp_parts/` (★工作区临时目录, **交付后应删**)
- 未发邮件 / 未联系厂家 / 未下单 / 未询价
- 每条脚号都有原厂 URL + 页码/图号; 查不到的明确标 "未查到"
