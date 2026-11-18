# SOM (Forlinx FET3572-C) 逐针表 · 验证报告

> 生成: `state/_iss165_som_pins_rebuild.py` · 数据源: **fx3572_manual.html** (OK3572-C 官方手册 V1.0, §2.6.2 引脚表 + §2.7 功能表) · 交叉源: **fx3576_manual.html**

## 1. 表结构 (每张引脚表 = 一个连接器的一半脚)

| 引脚表 | 归属连接器 | 行数 | 脚号范围 | 奇/偶 | 功能表反查命中 | 冲突票 |
|---|---|---|---|---|---|---|
| 0 | P1 | 50 | 1~99 | odd | 6 | 无 |
| 1 | P1 | 50 | 2~100 | even | 13 | 无 |
| 2 | P2 | 50 | 1~99 | odd | 6 | 无 |
| 3 | P2 | 49 | 2~100 | even | 3 | 无 |
| 4 | P3 | 50 | 1~99 | odd | 5 | 无 |
| 5 | P3 | 50 | 2~100 | even | 11 | 无 |
| 6 | P4 | 50 | 1~99 | odd | 3 | 无 |
| 7 | P4 | 50 | 2~100 | even | 12 | 无 |

> ★**表序 → 连接器** 是结构事实 (4 连接器 × 奇脚表/偶脚表), **功能表反查** 独立复核一致 ⇒ 两条链互证.

## 2. 覆盖度 (每个连接器 1~100 脚)

- **P1**: 有定义 100 脚 · 手册未列 0 脚 
- **P2**: 有定义 99 脚 · 手册未列 1 脚 → 40
- **P3**: 有定义 100 脚 · 手册未列 0 脚 
- **P4**: 有定义 100 脚 · 手册未列 0 脚 

## 3. 双手册交叉验证 (OK3572-C vs OK3576-C)

- 比对键数: 400 · **差异 168 处**

| 脚 | OK3572-C | OK3576-C |
|---|---|---|
| P1_100 | USB_DRD1_VBUSDET | USB2_OTG1_VBUSDET |
| P1_11 | SDMMC0_D3 | SDMMC_D3 |
| P1_13 | SDMMC0_D2 | SDMMC_D2 |
| P1_27 | GND | None |
| P1_3 | SDMMC0_D1 | SDMMC_D1 |
| P1_40 | SARADC_VIN6_DDR | SARADC_VIN6 |
| P1_42 | SARADC_VIN7 | SARADC_VIN7_LCD_ID |
| P1_46 | GPIO0_C1_d | HDMI_TX_ON_H |
| P1_48 | —— | TYPEC_DPTX_AUX_PUPDCTL2 |
| P1_5 | SDMMC0_D0 | SDMMC_D0 |
| P1_50 | GPIO2_B0_d | GPIO2_B5_d |
| P1_54 | GPIO2_B5_d | CAN1_RX_M3 |
| P1_56 | GPIO2_B6_d | I2C8_SCL_M2 |
| P1_58 | HDMI_TX_SDA_M0 | HDMI_TX_SDA |
| P1_60 | GPIO2_B7_d | I2C8_SDA_M2 |
| P1_64 | GPIO0_D3_d | PCIE0_PERSTn |
| P1_66 | —— | CAN1_TX_M3 |
| P1_68 | HDMI_TX_SCL_M0 | HDMI_TX_SCL |
| P1_7 | SDMMC0_CLK | SDMMC_CLK |
| P1_70 | GPIO2_B2_d | I2C7_SCL_M1 |
| P1_72 | GPIO2_B4_d | I2C7_SDA_M1 |
| P1_74 | PCIE1_WAKEn | PCIE0_WAKEn_M0 |
| P1_76 | PWM1_CH1_M0 | GPIO2_B3_d |
| P1_78 | PCIE1_CLKREQN_M3 | PCIE0_CLKREQn_M0 |
| P1_80 | GPIO0_C2_d | GPIO2_B1_d |
| P1_82 | —— | TYPEC_DPTX_AUX_PUPDCTL1 |
| P1_9 | SDMMC0_CMD | SDMMC_CMD |
| P1_92 | USB_DRD1_DP | USB2_HOST1_DP |
| P1_94 | USB_DRD1_DM | USB2_HOST1_DM |
| P1_98 | USB_DRD1_ID | USB2_OTG1_ID |

## 4. 与上一版表 (FET3576C_PIN_TABLE.csv) 的差异

- 旧表 399 行 / 可用 (conn,num) 键 281 个 · **conn 为空的行 16**
- **与新表信号不符的键: 302 处**
  - `P1_100`: 旧=`GND` → 新=`USB_DRD1_VBUSDET`
  - `P1_11`: 旧=`None` → 新=`SDMMC0_D3`
  - `P1_12`: 旧=`GND` → 新=`——`
  - `P1_13`: 旧=`GND` → 新=`SDMMC0_D2`
  - `P1_17`: 旧=`——` → 新=`HDMI_TX_SBDN`
  - `P1_19`: 旧=`GND` → 新=`HDMI_TX_SBDP`
  - `P1_22`: 旧=`GND` → 新=`——`
  - `P1_23`: 旧=`——` → 新=`HDMI_TX_D3N`
  - `P1_25`: 旧=`GND` → 新=`HDMI_TX_D3P`
  - `P1_28`: 旧=`——` → 新=`SARADC_VIN0_BOOT`
  - `P1_29`: 旧=`None` → 新=`HDMI_TX_D0N`
  - `P1_3`: 旧=`None` → 新=`SDMMC0_D1`

> ★**旧表不可用于画板** (GND 串组 ⇒ P1 有 196 行/102 个重复 num; 另有 conn 空行) ⇒ **以 `FET3572C_PIN_TABLE.csv` 为准**.

## 5. 我们实际用到的脚 (供画板核对)

| 信号 | 出现的脚 |
|---|---|
| CARRIER_BOARD_EN | P3_87 |
| PWRON_L | P3_88 |
| VCC_DCIN | P3_91, P3_93, P3_95, P3_97, P3_99, P3_98, P3_100 |
| RESET_L | P2_100 |
| SARADC_VIN0_BOOT | P1_28 |
| SARADC_VIN2_HW_ID | P1_32 |
| USB2_OTG1_VBUSDET | ★手册未列 |
| USB2_HOST1_DP | ★手册未列 |
| USB2_HOST1_DM | ★手册未列 |
| UART0_TX_M0_DEBUG | P2_7 |
| UART0_RX_M0_DEBUG | P2_9 |
| I2C8_SCL_M2 | ★手册未列 |
| I2C8_SDA_M2 | ★手册未列 |
| I2C7_SCL_M1 | ★手册未列 |
| I2C7_SDA_M1 | ★手册未列 |
| GPIO2_B5_d | P1_54 |
| GPIO2_B3_d | ★手册未列 |
| GPIO2_B1_d | ★手册未列 |
| GPIO3_D4_d | P2_19 |

> ★**结论**: (conn,num) 全部有手册出处, 无冲突票 ⇒ **可作为画板唯一依据**.

