# HW/CORE_MODULE_SELECTION.md —— demo 主板 核心模块选型表

> **日期**: 2026-11-04 01:0x · **状态**: demo 板（= 本项目的"整机主板"，老板 11-03 09:54 定：没有整机、没有镜脚，demo/主板用 Type-C 供电）
> **依据**: 原厂 datasheet / 官方手册 / 原厂 3D 模型（逐条带出处，见各行"依据"列 + `HW/PCB/PINOUT_FOOTPRINT_SPEC.md`）

## 1. 主链路（已定）

| # | 类别 | 型号 | 关键参数 | 接口 / 封装 | 状态 | 依据 |
|---|---|---|---|---|---|---|
| 1 | **主控模块 SoM** | **Forlinx FET3572-C** (RK3572) | 8 核 A72+A53 · 4 TOPS NPU · 68×50mm · 1.6mm 10 层沉金 · VCC_DCIN **5~13V** · 自带 PMIC / 晶振 / eMMC | **4×100pin / 0.4mm BTB**（P1~P4） | ✅ **已定** | Forlinx OK3572-C 手册 §2.3~2.7 + 产品页 |
| 2 | **载板 BTB 座** ×4 | **HIROSE DF40C-100DS-0.4V(51)** | 0.4mm pitch · 100 位 · 焊盘 **0.2×0.7mm** · **排中心距 3.08mm** · 背夹 + 上下双面触点 | UQFN 封装外形的 BTB 母座 | ✅ **已定**（几何两路互证） | 原厂 2D 产品图 + 原厂 3D STEP 解析（互证一致） |
| 3 | **相机模组** | **Radxa Camera 4K** (SONY IMX415) | 8.3MP 1/2.8" · 滚珠快门 · FOV 88.2°/75°/59° · 37MHz MCLK · **4-lane MIPI CSI** · RAW10/12 | **31p / 0.3mm FPC**（座 FH35C-31S-0.3SHW(50)）· 模组级 3.3V+5V · SCCB = **I2C5（1.8V 域）** | ✅ **已定** | Radxa 官方文档 + Rockchip BSP `imx415.c` |
| 4 | **相机座** | **HIROSE FH35C-31S-0.3SHW(50)** | 0.3mm / 31 位 · 背夹 · 上下双面触点 · 0.9mm 高 | 与 #3 配套 | ✅ **已定** | Hirose 原厂页 + 载板侧针位表（Rock 4D 官方） |
| 5 | **USB-C 座** | **GCT USB4105** (16p) | SMT 贴片母座 · 8.64×6.40mm 焊盘区 | VBUS(A4/A9/B4/B9) · D+(A6/B6) · D−(A7/B7) · CC1(A5) · CC2(B5) · GND(A1/A12/B1/B12)+shell | ✅ **已定**（本板唯一 5V 入口，受电端 UFP，CC 5.1k×2） | GCT 原厂页 + LCSC |
| 6 | **3.3V / 1.8V LDO** ×3 必装 | **TPS7A2033DQNR** / **TPS7A2018DQNR** | 1×1mm **X2SON (DQN0004A)** · **1=OUT · 2=GND · 3=EN · 4=IN · 5=散热焊盘→GND** | 3 颗必装（L33 / IO33 / IO18）· 4 颗 DNP（sensor 三轨 / LIGHT_1V8） | ✅ **已定**（脚号按原厂 datasheet） | TI TPS7A20 datasheet |
| 7 | **底板主电源门控** | **TPS22991RAA** | UQFN-4 RAA 0.85×0.75mm · RON 25mΩ · **无反向阻断 (RCB)** | IN=5V / ON=CARRIER_BOARD_EN / OUT=RAIL_BOARD_5V | ⏳ **待你点头**（ISS-172） | TI datasheet + Forlinx §3.5 门控要求 |
| 8 | **关机开关** | **TPS22991RAA** | 同上 | ON ← SoM 的 PWRON_L (P3_88) | ⏳ 同 ISS-172 | 同上 |

## 2. 显示链路（★待你拍板，老板 11-03 19:4x 要求 ≤3 寸）

| # | 候选 | 尺寸 / 分辨率 | DSI | FPC | 背光 | 驱动 / init | 备注 |
|---|---|---|---|---|---|---|---|
| ★**①** | **Waveshare 2.8inch DSI LCD (SKU 22028)** | 2.8" / 480×640 IPS 光学贴合 160° 硬玻璃 | **2-lane** | **15 位 / 1.0mm**（官方 Package Content 原文）· 官方 wiki 逐针表 15 针全公开 | ★**无独立背光脚**（模组内从 3V3 取）⇒ **12V BOOST 整链可砍** | init 公开可得（树莓派官方 firmware `waveshare,2.8inch-panel`）· Rockchip 内核有同档 480×640/2-lane ST7701 先例 | ★**建议选它**（唯一「≤3寸+DSI+官方公开逐针表+在售+官方 driver 生态」四项全中）· $43.39 |
| ② | Densitron DMT028VGHMCMI-1A（敦泰 2.8" 裸面板） | 2.8" / 480×640（内核记 56×78mm） | 2-lane | 未查到 | 未查到 | ★**内核 `panel-sitronix-st7701.c` 已收录，GIP/init 在 .c 里 ⇒ BSP 零移植** | 但针位表/采购渠道未查到 |
| ③ | Samsung S6E63J0X03（1.61" 圆形 AMOLED 面板） | 1.61" / 320×320（内核记 29×29mm） | 1-lane | 未查到 | ★**OLED 无背光** | 内核 `panel-samsung-s6e63j0x03.c` 已收录 | 公开模组未查到 |
| ④ | **视涯 SY049WDM01 0.49" OLEDoS**（产品目标，非 demo 采购件） | 0.49" / 1920×1080 · 5.6μm · 4496PPI · AA 10.783×6.065mm | **MIPI D-PHY 1 PORT + VESA DSC 3:1**（官方 datasheet） | ★**无公开 FPC 针位表**（仅机械：底部 pin 区 19.03mm、模组厚 1.48mm、侧出脚） | ★**OLED 无背光** | ★**面板 init 序列未公开**（需厂家） | 三个规格并存：3000nits Full RGB / 1800nits Full RGB / **20000nits Mono-G 单色绿** ⇒ **ISS-132「单色还是全彩」不成立**（是选规格）⇒ **D3 风险只剩「RK3572 能否解 DSC」** |

★**显示座选型建议（关键）**：**SoM 侧 4-lane 一个字都不用改** ⇒ "主板→屏座"那段**维持 4-lane 布线、座按 24 位 / 0.5mm 预留**，demo 用 **15→24 转接线** ⇒ ★**别按 demo 屏把座定死**（整机屏针位表至今未查到）。

## 3. 已砍掉 / 不上这块板（★"模块已内置就不重复做"）

| 项 | 器件 | 为什么砍 | 依据 |
|---|---|---|---|
| SoC 核心/IO 轨 DC-DC | TPS62130ARGTR ×2 | ★**SoM 自带 PMIC**（P3_10 = PMIC_VDC）⇒ 主板不产 SoC 核心/IO 轨 | SoM 引脚表 |
| 传感器三轨 LDO | TPS7A2028/2018/2012 ×3 | ★**相机模组自带稳压**（模组只吃 3.3V + 5V） | Radxa 模组针位表 |
| 上电监督器 | TPS3808G01DBVR | ★**SoM 内部 PMIC 已做复位**；Forlinx 官方载板复位电路也只有"按键 + RC + ESD"，**没有监督器** | Forlinx 载板原理图 |
| 晶振 | X1 + 2×12pF | 晶振在 SoM 板上 | SoM 引脚表 |
| 启动存储焊盘位 | J_BOOT1（6p） | SoM 板载 eMMC/SD ⇒ 主板不挂 SPI-NOR | SoM 引脚表 |
| 电池 + 保护链 | 丰江 432243 + BQ2970DSE + CSD16406Q3 ×2 | ★**demo 主板用 Type-C 供电 ⇒ 不装电池** | 老板 11-03 09:54 |
| 充电链 | BQ25896RTWR + 周边 | demo 不上充电链（整机阶段另议） | 同上 |

## 4. 还没落定的（投板前必须清零）

| 项 | 缺什么 | 状态 |
|---|---|---|
| **显示模组 + 显示座** | 见 §2 ⇒ **待你拍板** | ⏳ |
| **TMP117 板载温度计** | ★**封装/脚号未落定**（不在 `pinout_footprint.json` 里） | ⏳ |
| **4 个按键 + RGB LED** | 型号未选（[待选型]） | ⏳ |
| **背光 BOOST** | 若最终选带背光脚的屏才需要（①无背光脚 ⇒ **可砍**） | ⏳（ISS-173） |
| **载板 BTB 座 pin1 排向** | ★**Hirose 公开资料无脚号** ⇒ 由 Forlinx 侧两处交叉定（4 座一致：奇数脚 = y 小排）⇒ ★**投板前必须万用表实测一次**（买 1 片 SoM） | ⏳（ISS-169） |
| **Q1/Q2 的 Rds(on)@Vgs=3.5V** | BQ2970 判据要 7.5mΩ@3.5V，CSD16406Q3 官方表只有 4.5/10V 条件（demo DNP，优先级低） | ⏳（ISS-171） |
| **布线** | ★**0 根走线**（unconnected 358）⇒ 按老板指示**放最后** | ⏳ |
