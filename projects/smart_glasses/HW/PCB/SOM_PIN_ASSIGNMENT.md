# SOM 引脚分配表 (RK3572 核心板 Forlinx FET3572-C) ★RK3572 口径

> ★脚标识 = 手册权威形式 `P<x>_<num>` (4 个连接器各 100 脚) ⇒ 主板上是 **4 个独立 100 脚 BTB 座 (J_SOM_P1..P4)**
> 真值: `HW/PCB/FET3572C_PIN_TABLE.csv` (399 行, 由 OK3572-C 官方手册重建) · 机器可读: `HW/PCB/som_pin_assign.json`
> ★**本表已从 OK3576-C 口径全面换掉**: 实测 RK3572 与 RK3576 引脚功能不同 (226/398 脚球号不同)

| 我们的信号 | RK3572 信号 | 连接器 | 组内脚 | 球号 | 电平 | 座 | 依据 |
|---|---|---|---|---|---|---|---|
| BAT_DET | SARADC_VIN5 | P1 | 38 | 1AE17 | 1.8V | J_SOM_P1 | 电池电压检测 (1M+1M 分压进 ADC) |
| BOOT_N | SARADC_VIN0_BOOT | P1 | 28 | 1AF21 | 1.8V | J_SOM_P1 | BOOT 模式选择 (SARADC 分压) |
| CSI_D0_CK_N | MIPI_DPHY_CSI0_RX_CLKN | P4 | 77 | B20 | —— | J_SOM_P4 | CSI lane0 时钟 - |
| CSI_D0_CK_P | MIPI_DPHY_CSI0_RX_CLKP | P4 | 79 | A20 | —— | J_SOM_P4 | CSI lane0 时钟 + |
| CSI_D0_D0_N | MIPI_DPHY_CSI0_RX_D0N | P4 | 65 | B19 | —— | J_SOM_P4 | CSI lane1 - |
| CSI_D0_D0_P | MIPI_DPHY_CSI0_RX_D0P | P4 | 67 | A19 | —— | J_SOM_P4 | CSI lane1 + |
| CSI_D0_D1_N | MIPI_DPHY_CSI0_RX_D1N | P4 | 71 | 1C14 | —— | J_SOM_P4 | CSI lane2 - |
| CSI_D0_D1_P | MIPI_DPHY_CSI0_RX_D1P | P4 | 73 | 1B14 | —— | J_SOM_P4 | CSI lane2 + |
| CSI_D0_D2_N | MIPI_DPHY_CSI1_RX_D0N | P4 | 83 | B22 | —— | J_SOM_P4 | ★CSI lane3 - |
| CSI_D0_D2_P | MIPI_DPHY_CSI1_RX_D0P | P4 | 85 | A22 | —— | J_SOM_P4 | ★CSI lane3 + (4lane = CSI0+CSI1 拼) |
| CSI_D0_D3_N | MIPI_DPHY_CSI1_RX_D1N | P4 | 89 | B23 | —— | J_SOM_P4 | ★CSI lane4 - |
| CSI_D0_D3_P | MIPI_DPHY_CSI1_RX_D1P | P4 | 91 | A23 | —— | J_SOM_P4 | ★CSI lane4 + |
| CSI_MCLK | CAM_CLK0_OUT_M0 | P2 | 45 | AM32 | 1.8V | J_SOM_P2 | ★SoM 自带 CAM_CLK 输出 ⇒ 不用主板自己产 (1.8V) |
| CSI_RESET_N | GPIO0_C1_d | P1 | 46 | Y33 | 3.3V | J_SOM_P1 | ★(旧 CSI_RESET_N 已并入 CAM_RESET_N; 此条备用) |
| DSI_TX_CK_N | MIPI_DPHY_DSI_TX_CLKN | P3 | 69 | AR27 | —— | J_SOM_P3 | DSI 时钟 - |
| DSI_TX_CK_P | MIPI_DPHY_DSI_TX_CLKP | P3 | 71 | AT27 | —— | J_SOM_P3 | DSI 时钟 + |
| DSI_TX_D0_N | MIPI_DPHY_DSI_TX_D0N | P3 | 57 | 1AD15 | —— | J_SOM_P3 | DSI lane0 - |
| DSI_TX_D0_P | MIPI_DPHY_DSI_TX_D0P | P3 | 59 | 1AE15 | —— | J_SOM_P3 | DSI lane0 + |
| DSI_TX_D1_N | MIPI_DPHY_DSI_TX_D1N | P3 | 63 | AR26 | —— | J_SOM_P3 | DSI lane1 - |
| DSI_TX_D1_P | MIPI_DPHY_DSI_TX_D1P | P3 | 65 | AT26 | —— | J_SOM_P3 | DSI lane1 + |
| DSI_TX_D2_N | MIPI_DPHY_DSI_TX_D2N | P3 | 75 | AR29 | —— | J_SOM_P3 | DSI lane2 - |
| DSI_TX_D2_P | MIPI_DPHY_DSI_TX_D2P | P3 | 77 | AT29 | —— | J_SOM_P3 | DSI lane2 + |
| DSI_TX_D3_N | MIPI_DPHY_DSI_TX_D3N | P3 | 81 | AR30 | —— | J_SOM_P3 | DSI lane3 - |
| DSI_TX_D3_P | MIPI_DPHY_DSI_TX_D3P | P3 | 83 | AT30 | —— | J_SOM_P3 | DSI lane3 + |
| GPIO_CAM_RESET | GPIO2_B5_d | P1 | 54 | B4 | 3.3V | J_SOM_P1 | camera RESET (低有效, 3.3V) |
| GPIO_DSI_RESET | GPIO2_B6_d | P1 | 56 | 1D3 | 3.3V | J_SOM_P1 | DSI RESET (3.3V) |
| I2C_A_SCL | I2C5_SCL_M3 | P2 | 31 | AH33 | 1.8V | J_SOM_P2 | ★相机 SCCB (模组 FPC 标注 I2C5; RK3572 的 I2C5 = 1.8V 域 ⇒ 上拉改 1.8V) |
| I2C_A_SDA | I2C5_SDA_M3 | P2 | 33 | AL33 | 1.8V | J_SOM_P2 | ★同上 |
| I2C_B_SCL | I2C2_SCL_M0 | P2 | 11 | AA32 | 3.3V | J_SOM_P2 | 触控 I2C + TMP117 (3.3V 域; TMP117 VIH=0.7×V+ ⇒ 不能上 1.8V) |
| I2C_B_SDA | I2C2_SDA_M0 | P2 | 1 | Y32 | 3.3V | J_SOM_P2 | ★同上 |
| ID0 | SARADC_VIN2_HW_ID | P1 | 32 | 1AE19 | 1.8V | J_SOM_P1 | 硬件版本 ID (SARADC2) |
| ID1 | SARADC_VIN4 | P1 | 36 | 1AD17 | 1.8V | J_SOM_P1 | 第二路 SARADC (通用 ADC) |
| KEY_CAM | GPIO0_C7_d | P4 | 3 | 1T23 | 3.3V | J_SOM_P4 | 拍照键 (3.3V) |
| KEY_PWR | GPIO0_D3_d | P1 | 64 | 1P23 | 3.3V | J_SOM_P1 | 电源键 (3.3V) |
| KEY_VOL_M | GPIO0_C5_d | P4 | 1 | 1T21 | 3.3V | J_SOM_P4 | 音量- (3.3V) |
| KEY_VOL_P | GPIO0_C4_d | P2 | 13 | 1T20 | 3.3V | J_SOM_P2 | 音量+ (3.3V) |
| LED_B | GPIO4_B4_d | P4 | 21 | AR33 | 3.3V | J_SOM_P4 | 蓝 (3.3V) |
| LED_G | GPIO4_B7_d | P4 | 19 | AN32 | 3.3V | J_SOM_P4 | 绿 (3.3V) |
| LED_R | GPIO0_C2_d | P1 | 80 | W32 | 3.3V | J_SOM_P1 | 红 (3.3V) |
| PWR_CTRL | PWRON_L | P3 | 88 | —— | —— | J_SOM_P3 | 开机/关机 (SoM 输出) |
| RESET_N | RESET_L | P2 | 100 | —— | —— | J_SOM_P2 | SoM 复位 (低有效) |
| UART_RX | UART0_RX_M0_DEBUG | P2 | 9 | V32 | 3.3V | J_SOM_P2 | 调试串口 RX (3.3V) |
| UART_TX | UART0_TX_M0_DEBUG | P2 | 7 | U33 | 3.3V | J_SOM_P2 | 调试串口 TX (3.3V) |
| USB_D_N | USB_DRD1_DM | P1 | 94 | A26 | —— | J_SOM_P1 | USB 2.0 D- (OTG1) |
| USB_D_P | USB_DRD1_DP | P1 | 92 | B26 | —— | J_SOM_P1 | USB 2.0 D+ (OTG1) |
| USB_VBUS_DET | USB_DRD1_VBUSDET | P1 | 100 | B28 | —— | J_SOM_P1 | USB VBUS 插入检测 |

## 固定脚 (电源 / 使能)

| 功能 | 脚标识 | 说明 |
|---|---|---|
| VCC_DCIN (5-13V 输入) | P3_91, P3_93, P3_95, P3_97, P3_98, P3_99, P3_100 | ★SoM 自己的供电 ⇒ **不经过 U_EN_SW 门控** (否则 SoM 永远起不来) |
| CARRIER_BOARD_EN (底板使能) | P3_87 | ★Forlinx 原文: 底板早于核心板上电 ⇒ 电流过大/无法启动/**可能损坏处理器** ⇒ 主板各路必须由它放行 |
| PWRON_L (开机) | P3_88 | 与 PWR_CTRL 同一脚 |

## 未引出 (DNP, ★不编造)

- **SPI_SCLK** — FET3572-C 未引出 SPI (SoM 板载 eMMC/SD ⇒ 主板不挂 SPI-NOR)
- **SPI_CSn** — 同上
- **SPI_MOSI** — 同上
- **SPI_MISO** — 同上
- **JTAG_TCK** — FET3572-C 未引出 JTAG (调试走 UART0)
- **JTAG_TMS** — 同上
- **JTAG_TDI** — 同上
- **JTAG_TDO** — 同上
- **XTAL_IN** — 晶振在 SoM 板上 ⇒ 主板不接
- **XTAL_OUT** — 同上
- **FSIN** — FET3572-C 无 FSIN 脚

## 关键结论 (与上一版分配的差异)

1. ★**I2C 换了组**: 相机 SCCB = **I2C5 (1.8V 域)** (模组 FPC 上就写着 I2C5) ⇒ **上拉必须改 1.8V**; 触控 I2C + TMP117 = **I2C2 (3.3V 域)** (TMP117 的 VIH=0.7×V+ ⇒ 1.8V 总线不满足)
2. ★**4-lane CSI 在 RK3572 上必须拆**: 模组 lane1/2 → CSI0 D0/D1, lane3/4 → CSI1 D0/D1 (Forlinx 载板原理图同款接法; RK3572 每端口只有 2 lane)
3. ★**camera MCLK 由 SoM 出** (CAM_CLK0_OUT_M0) ⇒ 上一版"主板自己产 MCLK"的结论作废
4. ★**SPI/JTAG/XTAL/FSIN 未引出** ⇒ 对应行标 DNP
5. ★**F13 落法**: SoM 的 CARRIER_BOARD_EN → 主板负载开关 U_EN_SW 的 EN ⇒ 主板各路挂 **RAIL_BOARD_5V** (不是 SYS); SoM 自己的 VCC_DCIN 直供 5V (不受门控)
