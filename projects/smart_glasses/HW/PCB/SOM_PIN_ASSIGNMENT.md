# SOM 引脚分配表 (RK3572 核心板 Forlinx FET3572-C)

> ★脚标识 = 手册权威形式 `P<x>_<num>` (4 个连接器各 100 脚) ⇒ **主板上是 4 个独立 100 脚 BTB 座 (J_SOM_P1..P4)**
> 来源: Forlinx 官方手册 (OK3576-C_User_Hardware_Manual) §2.6.2 引脚表 + §2.7 功能表; 全量映射 `HW/PCB/som_pin_full_map.json`

| 我们的信号 | SOM 脚名 | 连接器 | 组内脚 | 座 | 网络名 |
|---|---|---|---|---|---|
| BOOT_N | SARADC_VIN0_BOOT | P1 | 28 | J_SOM_P1 | J_SOM_P1_pin28 |
| GPIO_CAM_RESET | GPIO2_B5_d | P1 | 50 | J_SOM_P1 | J_SOM_P1_pin50 |
| GPIO_DSI_RESET | GPIO2_B3_d | P1 | 76 | J_SOM_P1 | J_SOM_P1_pin76 |
| I2C_A_SCL | I2C8_SCL_M2 | P1 | 56 | J_SOM_P1 | J_SOM_P1_pin56 |
| I2C_A_SDA | I2C8_SDA_M2 | P1 | 60 | J_SOM_P1 | J_SOM_P1_pin60 |
| I2C_B_SCL | I2C7_SCL_M1 | P1 | 70 | J_SOM_P1 | J_SOM_P1_pin70 |
| I2C_B_SDA | I2C7_SDA_M1 | P1 | 72 | J_SOM_P1 | J_SOM_P1_pin72 |
| ID_DETECT_0 | SARADC_VIN2_HW_ID | P1 | 32 | J_SOM_P1 | J_SOM_P1_pin32 |
| LED_0 | GPIO2_B1_d | P1 | 80 | J_SOM_P1 | J_SOM_P1_pin80 |
| LED_1 | GPIO3_D4_d | P2 | 19 | J_SOM_P2 | J_SOM_P2_pin19 |
| PWR_CTRL | PWRON_L | P3 | 88 | J_SOM_P3 | J_SOM_P3_pin88 |
| RESET_N | RESET_L | P2 | 100 | J_SOM_P2 | J_SOM_P2_pin100 |
| UART_RX | UART0_RX_M0_DEBUG | P2 | 9 | J_SOM_P2 | J_SOM_P2_pin9 |
| UART_TX | UART0_TX_M0_DEBUG | P2 | 7 | J_SOM_P2 | J_SOM_P2_pin7 |
| USB_D_N | USB2_HOST1_DM | P1 | 94 | J_SOM_P1 | J_SOM_P1_pin94 |
| USB_D_P | USB2_HOST1_DP | P1 | 92 | J_SOM_P1 | J_SOM_P1_pin92 |
| USB_VBUS_DET | USB2_OTG1_VBUSDET | P1 | 100 | J_SOM_P1 | J_SOM_P1_pin100 |

## 未分配 (★主板自己提供 / DNP)

- **CSI_RESET_N** ★**SOM 未引出 camera 的 RESET/MCLK ⇒ 主板必须自己产生 (★架构级结论, 要补 MCLK 源)**
- **CSI_MCLK** ★**SOM 未引出 camera 的 RESET/MCLK ⇒ 主板必须自己产生 (★架构级结论, 要补 MCLK 源)**
- **ID_DETECT_1**
- **FSIN** ★SOM 上无对应脚 ⇒ 主板不接
- **XTAL_0** ★**晶振在核心板上 ⇒ 主板不接**
- **XTAL_1** ★**晶振在核心板上 ⇒ 主板不接**

## 固定脚

| 功能 | 脚标识 |
|---|---|
| VCC_DCIN (5-13V 输入) | P3_91 / P3_93 / P3_95 / P3_97 / P3_99 / P3_98 / P3_100 |
| CARRIER_BOARD_EN (底板使能, ★致命项 F13) | P3_87 |
| PWRON_L (开机) | P3_88 |
