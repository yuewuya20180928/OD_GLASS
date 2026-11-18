# A2 段: 我们要挂到 SOM 座的 58 个 SoC 节点 —— 逐条对针号

★**方法**: 在 `HW/PCB/FET3576C_PIN_TABLE.csv` 里找同义信号 (我们 `CSI_D0_D3_P` ↔ 他们 `MIPI_DPHY_CSI_RX_D3P`; 我们 `DSI_TX_D3_P` ↔ 他们 `MIPI_DPHY_DSI_TX_D3P`; 其余按功能对应)。
★**判定**: 找到 ⇒ 改网表挂该针号; 找不到 ⇒ ①换同功能的其它针 ②或该功能在 FET3572-C 上没有 ⇒ 删功能/换板。

| 我们的 SoC 节点 | SOM 针号 | 对方信号名 | 结论 |
|---|---|---|---|
| `BAT_DET` | | | |
| `BOOT_N` | | | |
| `CSI_D0_CK_N` | | | |
| `CSI_D0_CK_P` | | | |
| `CSI_D0_D0_N` | | | |
| `CSI_D0_D0_P` | | | |
| `CSI_D0_D1_N` | | | |
| `CSI_D0_D1_P` | | | |
| `CSI_D0_D2_N` | | | |
| `CSI_D0_D2_P` | | | |
| `CSI_D0_D3_N` | | | |
| `CSI_D0_D3_P` | | | |
| `CSI_MCLK` | | | |
| `CSI_RESET_N` | | | |
| `DSI_TX_CK_N` | | | |
| `DSI_TX_CK_P` | | | |
| `DSI_TX_D0_N` | | | |
| `DSI_TX_D0_P` | | | |
| `DSI_TX_D1_N` | | | |
| `DSI_TX_D1_P` | | | |
| `DSI_TX_D2_N` | | | |
| `DSI_TX_D2_P` | | | |
| `DSI_TX_D3_N` | | | |
| `DSI_TX_D3_P` | | | |
| `FSIN` | | | |
| `GPIO_CAM_RESET` | | | |
| `GPIO_DSI_RESET` | | | |
| `I2C_A_SCL` | | | |
| `I2C_A_SDA` | | | |
| `I2C_B_SCL` | | | |
| `I2C_B_SDA` | | | |
| `ID0` | | | |
| `ID1` | | | |
| `JTAG_TCK` | | | |
| `JTAG_TDI` | | | |
| `JTAG_TDO` | | | |
| `JTAG_TMS` | | | |
| `KEY_CAM` | | | |
| `KEY_PWR` | | | |
| `KEY_VOL_M` | | | |
| `KEY_VOL_P` | | | |
| `LED_B` | | | |
| `LED_G` | | | |
| `LED_R` | | | |
| `PWR_CTRL` | | | |
| `RESET_N` | | | |
| `SPI_CSn` | | | |
| `SPI_MISO` | | | |
| `SPI_MOSI` | | | |
| `SPI_SCLK` | | | |
| `UART_RX` | | | |
| `UART_TX` | | | |
| `USB_D_N` | | | |
| `USB_D_P` | | | |
| `USB_VBUS_DET` | | | |
| `VBUS_DET` | | | |
| `XTAL_IN` | | | |
| `XTAL_OUT` | | | |
