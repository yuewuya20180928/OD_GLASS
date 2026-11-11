# 原理图脚数 vs 真实器件脚数 —— 逐器件对账 (PIN_REALITY_GAP)

> ★**生成器**: `state/gen_pin_reality_gap.py` (★重跑即刷新★)  
> ★**生成时间**: 2026-11-11  · ★**对应原理图**: `HW/PCB/demo_mainboard*.kicad_sch` (★按表全量画, 584 脚★)

## 0. 口径 (★凡给出统计数必带口径★)

| 口径项 | 值 | 含义 |
|---|---|---|
| ★**表侧脚数**★ | 584 | `HW/netlist_v1_pins.csv` 行数 (★每行=一脚, **含 DNP 行**★) |
| ★**表侧器件数**★ | 218 | 同表不同 ref 的个数 |
| ★**真实器件脚数**★ | 189 有 / 29 无 | 只在**本机可查到的权威源**查到才填; ★**查不到写 `[0数据]`, 不猜**★ |
| ★**脚数一致**★ | 183 | 表侧脚数 == 真实器件脚数 |
| ★**真实多脚**★ | 6 | 真实器件脚数 > 表侧脚数 (★表里只画用到的脚★) |
| ★**表里多脚**★ | 0 | ★**表侧脚数 > 真实器件脚数 ⇒ 物理上不该存在的脚, 需核**★ |
| ★**DNP 脚数**★ | 117 | 表侧 `dnp=DNP` 的行数 (★口径: 含 DNP★) |

★★**数据源 (★全部本机可复核; 不联网 / 不问供应商 / 不猜★)**★★

1. ★**KiCad 10.0.8 官方符号库**★ `/home/yuewuya/kicad/squashfs-root/usr/share/kicad/symbols/`
2. ★**项目自有真值表**★ `state/check_netlist_pins.py` 的 `SPEC_PINS` / `PARTIAL_PINS`
3. ★**RK3572 SOM 球位表**★ `HW/PCB/FET3572C_PIN_TABLE.csv` (★P1=100/P2=99/P3=100/P4=100 球位/座★)
4. ★**BOM 型号**★ `HW/BOM_v1.csv` 的 `opn` / `footprint` 列 (★型号已定型 ⇒ 可回查官方库★)

---

## 1. ★**表里脚数 > 真实器件脚数 (★物理上不该存在的脚 —— 本轮唯一需核的一类★)**

★无 (表侧脚数没有超过真实器件脚数的情形)★

---

## 2. ★**真实器件脚数 > 表里脚数 (★表里只画了用到的脚 —— 正常, 不是漏画★)**

| 器件 | 表里脚数 | 真实脚数 | 差 | DNP脚 | 型号/依据 | 说明 |
|---|---|---|---|---|---|---|
| `J_SOM_P1` | 10 | 100 | +90 | 0 | state/check_netlist_pins.py:PARTIAL_PINS (项目自有真值表) + HW/PCB/FET3572C_PIN_TABLE.csv (RK3572 SOM 100 球位/座) | 真实器件比表多 90 脚 ⇒ **表里只画了"用到的脚"**, 余下是空脚/NC/散热焊盘 |
| `J_SOM_P2` | 9 | 100 | +91 | 0 | state/check_netlist_pins.py:PARTIAL_PINS (项目自有真值表) + HW/PCB/FET3572C_PIN_TABLE.csv (RK3572 SOM 100 球位/座) | 真实器件比表多 91 脚 ⇒ **表里只画了"用到的脚"**, 余下是空脚/NC/散热焊盘 |
| `J_SOM_P3` | 19 | 100 | +81 | 0 | state/check_netlist_pins.py:PARTIAL_PINS (项目自有真值表) + HW/PCB/FET3572C_PIN_TABLE.csv (RK3572 SOM 100 球位/座) | 真实器件比表多 81 脚 ⇒ **表里只画了"用到的脚"**, 余下是空脚/NC/散热焊盘 |
| `J_SOM_P4` | 14 | 100 | +86 | 0 | state/check_netlist_pins.py:PARTIAL_PINS (项目自有真值表) + HW/PCB/FET3572C_PIN_TABLE.csv (RK3572 SOM 100 球位/座) | 真实器件比表多 86 脚 ⇒ **表里只画了"用到的脚"**, 余下是空脚/NC/散热焊盘 |
| `U_DCDC_VCORE` | 3 | 17 | +14 | 0 | BOM opn=TPS62130ARGTR ⇒ KiCad 官方库 Regulator_Switching:TPS62130 (16 脚 + 散热焊盘) | 真实器件比表多 14 脚 ⇒ **表里只画了"用到的脚"**, 余下是空脚/NC/散热焊盘 |
| `U_DCDC_VIO` | 3 | 17 | +14 | 0 | BOM opn=TPS62130ARGTR ⇒ KiCad 官方库 Regulator_Switching:TPS62130 (16 脚 + 散热焊盘) | 真实器件比表多 14 脚 ⇒ **表里只画了"用到的脚"**, 余下是空脚/NC/散热焊盘 |

---

## 3. ★**逐器件全表 (218 个器件)**★

| 器件 | 类型 | 表里脚数 | 真实脚数 | 差 | DNP脚 | 型号 / 数据来源 |
|---|---|---|---|---|---|---|
| `BT_432243` | CONN | 2 | [0数据] | [0数据] | 2 | [0数据] |
| `CHG_GND_STAR` | CONN | 1 | [0数据] | [0数据] | 0 | [0数据] |
| `CONN_CAM` | NET | 31 | 31 | +0 | 0 | state/check_netlist_pins.py:SPEC_PINS (项目自有真值表) |
| `CONN_LIGHT` | CONN | 22 | 22 | +0 | 0 | FH12-22S-0.5SH(55) · state/check_netlist_pins.py:SPEC_PINS (项目自有真值表) |
| `C_AC_CSI_D0_CK_N` | C | 2 | 2 | +0 | 0 | KiCad 官方库 Device:C |
| `C_AC_CSI_D0_CK_P` | C | 2 | 2 | +0 | 0 | KiCad 官方库 Device:C |
| `C_AC_CSI_D0_D0_N` | C | 2 | 2 | +0 | 0 | KiCad 官方库 Device:C |
| `C_AC_CSI_D0_D0_P` | C | 2 | 2 | +0 | 0 | KiCad 官方库 Device:C |
| `C_AC_CSI_D0_D1_N` | C | 2 | 2 | +0 | 0 | KiCad 官方库 Device:C |
| `C_AC_CSI_D0_D1_P` | C | 2 | 2 | +0 | 0 | KiCad 官方库 Device:C |
| `C_AC_CSI_D0_D2_N` | C | 2 | 2 | +0 | 0 | KiCad 官方库 Device:C |
| `C_AC_CSI_D0_D2_P` | C | 2 | 2 | +0 | 0 | KiCad 官方库 Device:C |
| `C_AC_CSI_D0_D3_N` | C | 2 | 2 | +0 | 0 | KiCad 官方库 Device:C |
| `C_AC_CSI_D0_D3_P` | C | 2 | 2 | +0 | 0 | KiCad 官方库 Device:C |
| `C_BAT` | C | 2 | 2 | +0 | 0 | KiCad 官方库 Device:C |
| `C_BST` | C | 2 | 2 | +0 | 0 | KiCad 官方库 Device:C |
| `C_BULK_LIGHT_1V8` | C | 2 | 2 | +0 | 2 | KiCad 官方库 Device:C |
| `C_BULK_LIGHT_3V3` | C | 2 | 2 | +0 | 0 | KiCad 官方库 Device:C |
| `C_BULK_SENSOR_AVDD` | C | 2 | 2 | +0 | 2 | KiCad 官方库 Device:C |
| `C_BULK_SENSOR_CORE` | C | 2 | 2 | +0 | 2 | KiCad 官方库 Device:C |
| `C_BULK_SENSOR_VDD_IO` | C | 2 | 2 | +0 | 2 | KiCad 官方库 Device:C |
| `C_BULK_VDD_1V8_IO` | C | 2 | 2 | +0 | 0 | KiCad 官方库 Device:C |
| `C_BULK_VDD_3V3_IO` | C | 2 | 2 | +0 | 0 | KiCad 官方库 Device:C |
| `C_BULK_V_CORE` | C | 2 | 2 | +0 | 2 | KiCad 官方库 Device:C |
| `C_BULK_V_SOC_IO` | C | 2 | 2 | +0 | 2 | KiCad 官方库 Device:C |
| `C_DET_BAT` | C | 2 | 2 | +0 | 2 | KiCad 官方库 Device:C |
| `C_DET_VBUS_D` | C | 2 | 2 | +0 | 0 | KiCad 官方库 Device:C |
| `C_HF_LIGHT_1V8` | C | 2 | 2 | +0 | 2 | KiCad 官方库 Device:C |
| `C_HF_LIGHT_3V3` | C | 2 | 2 | +0 | 0 | KiCad 官方库 Device:C |
| `C_HF_SENSOR_AVDD` | C | 2 | 2 | +0 | 2 | KiCad 官方库 Device:C |
| `C_HF_SENSOR_CORE` | C | 2 | 2 | +0 | 2 | KiCad 官方库 Device:C |
| `C_HF_SENSOR_VDD_IO` | C | 2 | 2 | +0 | 2 | KiCad 官方库 Device:C |
| `C_HF_VDD_1V8_IO` | C | 2 | 2 | +0 | 0 | KiCad 官方库 Device:C |
| `C_HF_VDD_3V3_IO` | C | 2 | 2 | +0 | 0 | KiCad 官方库 Device:C |
| `C_HF_V_CORE` | C | 2 | 2 | +0 | 2 | KiCad 官方库 Device:C |
| `C_HF_V_SOC_IO` | C | 2 | 2 | +0 | 2 | KiCad 官方库 Device:C |
| `C_KEY_CAM` | C | 2 | 2 | +0 | 2 | KiCad 官方库 Device:C |
| `C_KEY_PWR` | C | 2 | 2 | +0 | 0 | KiCad 官方库 Device:C |
| `C_KEY_VM` | C | 2 | 2 | +0 | 0 | KiCad 官方库 Device:C |
| `C_KEY_VP` | C | 2 | 2 | +0 | 0 | KiCad 官方库 Device:C |
| `C_PMID` | C | 2 | 2 | +0 | 0 | KiCad 官方库 Device:C |
| `C_REGN` | C | 2 | 2 | +0 | 0 | KiCad 官方库 Device:C |
| `C_RST` | C | 2 | 2 | +0 | 0 | KiCad 官方库 Device:C |
| `C_SUPV` | C | 2 | 2 | +0 | 2 | KiCad 官方库 Device:C |
| `C_SW_IN` | C | 2 | 2 | +0 | 0 | KiCad 官方库 Device:C |
| `C_SW_OUT` | C | 2 | 2 | +0 | 0 | KiCad 官方库 Device:C |
| `C_SYS` | C | 2 | 2 | +0 | 2 | KiCad 官方库 Device:C |
| `C_TEMP` | C | 2 | 2 | +0 | 0 | KiCad 官方库 Device:C |
| `C_VBUS_DEMO` | C | 2 | 2 | +0 | 0 | KiCad 官方库 Device:C |
| `C_VBUS_GND` | C | 2 | 2 | +0 | 2 | KiCad 官方库 Device:C |
| `C_VBUS_IC` | C | 2 | 2 | +0 | 0 | KiCad 官方库 Device:C |
| `C_VBUS_IN` | C | 2 | 2 | +0 | 2 | KiCad 官方库 Device:C |
| `C_VBUS_OUT` | C | 2 | 2 | +0 | 2 | KiCad 官方库 Device:C |
| `C_XTAL_IN` | C | 2 | 2 | +0 | 2 | KiCad 官方库 Device:C |
| `C_XTAL_OUT` | C | 2 | 2 | +0 | 2 | KiCad 官方库 Device:C |
| `D_CHG_LED` | LED | 2 | 2 | +0 | 0 | KiCad 官方库 Device:LED |
| `D_ESD_CAM` | D | 2 | [0数据] | [0数据] | 0 | [0数据] |
| `D_ESD_DEMO` | D | 2 | [0数据] | [0数据] | 0 | [0数据] |
| `D_ESD_LIGHT` | D | 2 | [0数据] | [0数据] | 2 | [0数据] |
| `D_ESD_TC` | D | 4 | [0数据] | [0数据] | 0 | [0数据] |
| `D_ESD_USB_D` | D | 2 | [0数据] | [0数据] | 0 | [0数据] |
| `D_LED_B` | LED | 2 | 2 | +0 | 2 | KiCad 官方库 Device:LED |
| `D_LED_G` | LED | 2 | 2 | +0 | 0 | KiCad 官方库 Device:LED |
| `D_LED_R` | LED | 2 | 2 | +0 | 0 | KiCad 官方库 Device:LED |
| `D_TVS_VBUS` | D | 2 | [0数据] | [0数据] | 0 | [0数据] |
| `FB_DEMO` | L | 2 | [0数据] | [0数据] | 0 | [0数据] |
| `FB_VBUS` | L | 2 | [0数据] | [0数据] | 0 | [0数据] |
| `J_BOOT1` | CONN | 6 | 6 | +0 | 6 | state/check_netlist_pins.py:SPEC_PINS (项目自有真值表) |
| `J_CHG` | NET | 10 | 10 | +0 | 3 | state/check_netlist_pins.py:SPEC_PINS (项目自有真值表) |
| `J_DEBUG` | CONN | 4 | 4 | +0 | 0 | state/check_netlist_pins.py:SPEC_PINS (项目自有真值表) |
| `J_SOM_P1` | NET | 10 | 100 | +90 | 0 | state/check_netlist_pins.py:PARTIAL_PINS (项目自有真值表) + HW/PCB/FET3572C_PIN_TABLE.csv (RK3572 SOM 100 球位/座) |
| `J_SOM_P2` | - | 9 | 100 | +91 | 0 | state/check_netlist_pins.py:PARTIAL_PINS (项目自有真值表) + HW/PCB/FET3572C_PIN_TABLE.csv (RK3572 SOM 100 球位/座) |
| `J_SOM_P3` | NET | 19 | 100 | +81 | 0 | state/check_netlist_pins.py:PARTIAL_PINS (项目自有真值表) + HW/PCB/FET3572C_PIN_TABLE.csv (RK3572 SOM 100 球位/座) |
| `J_SOM_P4` | - | 14 | 100 | +86 | 0 | state/check_netlist_pins.py:PARTIAL_PINS (项目自有真值表) + HW/PCB/FET3572C_PIN_TABLE.csv (RK3572 SOM 100 球位/座) |
| `J_TYPE_C` | CONN | 17 | 17 | +0 | 2 | GCT USB4105 (USB Type C Receptacle for USB 2.0, SMT Type, PCB Top Mount) · BOM opn=GCT USB4105 (USB2.0 16P) ⇒ KiCad 官方库 Connector:USB_C_Receptacle_USB2.0_16P (16 脚 + shield) |
| `J_UART` | CONN | 2 | 2 | +0 | 0 | state/check_netlist_pins.py:SPEC_PINS (项目自有真值表) |
| `J_USB_C` | CONN | 14 | [0数据] | [0数据] | 0 | GCT USB4105-16P (USB Type-C 母座 16P, SMT 顶装) —— ★**焊盘宽度按原厂 0.30mm** (登记曾误写 0.20mm) · [0数据] |
| `L_CHG` | L | 2 | 2 | +0 | 0 | KiCad 官方库 Device:L |
| `Q1` | SW | 1 | [0数据] | [0数据] | 1 | [0数据] |
| `Q2` | SW | 1 | [0数据] | [0数据] | 1 | CSD16406Q3 (同 Q1) · [0数据] |
| `Q_AND` | SW | 3 | [0数据] | [0数据] | 0 | [0数据] |
| `Q_CHG_LED` | SW | 3 | [0数据] | [0数据] | 0 | [0数据] |
| `Q_ENVC` | SW | 3 | [0数据] | [0数据] | 1 | [0数据] |
| `Q_PG` | SW | 3 | [0数据] | [0数据] | 0 | [0数据] |
| `R_BAT_DET_1` | R | 2 | 2 | +0 | 2 | KiCad 官方库 Device:R |
| `R_BAT_DET_2` | R | 2 | 2 | +0 | 2 | KiCad 官方库 Device:R |
| `R_CC1` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `R_CC1_D` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `R_CC2` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `R_CC2_D` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `R_CE` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `R_CHG_LED` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `R_EN_VCORE` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `R_ID_JMP0` | R | 2 | 2 | +0 | 2 | KiCad 官方库 Device:R |
| `R_ID_JMP1` | R | 2 | 2 | +0 | 2 | KiCad 官方库 Device:R |
| `R_ILIM` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `R_JTAG_TCK` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `R_JTAG_TDI` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `R_JTAG_TDO` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `R_JTAG_TMS` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `R_KEY_CAM` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `R_KEY_PWR` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `R_KEY_VM` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `R_KEY_VP` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `R_LED_B` | R | 2 | 2 | +0 | 2 | KiCad 官方库 Device:R |
| `R_LED_G` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `R_LED_R` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `R_NTC_BAT` | R | 2 | 2 | +0 | 2 | KiCad 官方库 Device:R |
| `R_OTG` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `R_PD_ON` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `R_PG_PULL` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `R_PSEL` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `R_PU_BOOT_N` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `R_PU_CHG_STAT` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `R_PU_I2CA_SCL` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `R_PU_I2CA_SDA` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `R_PU_I2CB_SCL` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `R_PU_I2CB_SDA` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `R_PU_ID0` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `R_PU_ID1` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `R_PU_INT` | R | 2 | 2 | +0 | 2 | KiCad 官方库 Device:R |
| `R_PU_PG` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `R_PU_RESET_N` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `R_PU_SCL` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `R_PU_SDA` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `R_SEL_CK_N` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `R_SEL_CK_P` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `R_SEL_D0_N` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `R_SEL_D0_P` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `R_SEL_D1_N` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `R_SEL_D1_P` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `R_SEL_D2_N` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `R_SEL_D2_P` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `R_SEL_D3_N` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `R_SEL_D3_P` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `R_SER_CSI_MCLK` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `R_SER_FSIN` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `R_SER_RESET_N` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `R_SER_SPI_CSn` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `R_SER_SPI_MISO` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `R_SER_SPI_MOSI` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `R_SER_SPI_SCLK` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `R_SER_USB_D_N` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `R_SER_USB_D_P` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `R_STAR_PGND` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `R_SUPV_DIV1` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `R_SUPV_DIV2` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `R_TS_PULL` | R | 2 | 2 | +0 | 2 | KiCad 官方库 Device:R |
| `R_TS_TOP` | R | 2 | 2 | +0 | 2 | KiCad 官方库 Device:R |
| `R_VBUS_DET_D1` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `R_VBUS_DET_D2` | R | 2 | 2 | +0 | 0 | KiCad 官方库 Device:R |
| `SW_BOOT` | SW | 2 | [0数据] | [0数据] | 0 | [0数据] |
| `SW_KEY_CAM` | SW | 2 | [0数据] | [0数据] | 2 | [0数据] |
| `SW_KEY_PWR` | SW | 2 | [0数据] | [0数据] | 0 | [0数据] |
| `SW_KEY_VM` | SW | 2 | [0数据] | [0数据] | 0 | [0数据] |
| `SW_KEY_VP` | SW | 2 | [0数据] | [0数据] | 0 | [0数据] |
| `SW_RST` | SW | 2 | [0数据] | [0数据] | 0 | [0数据] |
| `TP_BAT` | TP | 1 | 1 | +0 | 1 | KiCad 官方库 Connector:TestPoint (单脚测试点) |
| `TP_BAT_CHG` | TP | 1 | 1 | +0 | 0 | KiCad 官方库 Connector:TestPoint (单脚测试点) |
| `TP_BOOT` | TP | 1 | 1 | +0 | 0 | KiCad 官方库 Connector:TestPoint (单脚测试点) |
| `TP_CHG_STAT` | TP | 1 | 1 | +0 | 0 | KiCad 官方库 Connector:TestPoint (单脚测试点) |
| `TP_CSI_CK_N` | TP | 1 | 1 | +0 | 0 | KiCad 官方库 Connector:TestPoint (单脚测试点) |
| `TP_CSI_CK_P` | TP | 1 | 1 | +0 | 0 | KiCad 官方库 Connector:TestPoint (单脚测试点) |
| `TP_CSI_D0_N` | TP | 1 | 1 | +0 | 0 | KiCad 官方库 Connector:TestPoint (单脚测试点) |
| `TP_CSI_D0_P` | TP | 1 | 1 | +0 | 0 | KiCad 官方库 Connector:TestPoint (单脚测试点) |
| `TP_DSI_CK_N` | TP | 1 | 1 | +0 | 0 | KiCad 官方库 Connector:TestPoint (单脚测试点) |
| `TP_DSI_CK_P` | TP | 1 | 1 | +0 | 0 | KiCad 官方库 Connector:TestPoint (单脚测试点) |
| `TP_DSI_D0_N` | TP | 1 | 1 | +0 | 0 | KiCad 官方库 Connector:TestPoint (单脚测试点) |
| `TP_DSI_D0_P` | TP | 1 | 1 | +0 | 0 | KiCad 官方库 Connector:TestPoint (单脚测试点) |
| `TP_DSI_D1_N` | TP | 1 | 1 | +0 | 0 | KiCad 官方库 Connector:TestPoint (单脚测试点) |
| `TP_DSI_D1_P` | TP | 1 | 1 | +0 | 0 | KiCad 官方库 Connector:TestPoint (单脚测试点) |
| `TP_DSI_D2_N` | TP | 1 | 1 | +0 | 0 | KiCad 官方库 Connector:TestPoint (单脚测试点) |
| `TP_DSI_D2_P` | TP | 1 | 1 | +0 | 0 | KiCad 官方库 Connector:TestPoint (单脚测试点) |
| `TP_DSI_D3_N` | TP | 1 | 1 | +0 | 0 | KiCad 官方库 Connector:TestPoint (单脚测试点) |
| `TP_DSI_D3_P` | TP | 1 | 1 | +0 | 0 | KiCad 官方库 Connector:TestPoint (单脚测试点) |
| `TP_FSIN` | TP | 1 | 1 | +0 | 0 | KiCad 官方库 Connector:TestPoint (单脚测试点) |
| `TP_I2CA_SCL` | TP | 1 | 1 | +0 | 0 | KiCad 官方库 Connector:TestPoint (单脚测试点) |
| `TP_I2CA_SDA` | TP | 1 | 1 | +0 | 0 | KiCad 官方库 Connector:TestPoint (单脚测试点) |
| `TP_I2CB_SCL` | TP | 1 | 1 | +0 | 0 | KiCad 官方库 Connector:TestPoint (单脚测试点) |
| `TP_I2CB_SDA` | TP | 1 | 1 | +0 | 0 | KiCad 官方库 Connector:TestPoint (单脚测试点) |
| `TP_ID` | TP | 1 | 1 | +0 | 0 | KiCad 官方库 Connector:TestPoint (单脚测试点) |
| `TP_JTAG` | TP | 1 | 1 | +0 | 0 | KiCad 官方库 Connector:TestPoint (单脚测试点) |
| `TP_KEY_PWR` | TP | 1 | 1 | +0 | 0 | KiCad 官方库 Connector:TestPoint (单脚测试点) |
| `TP_KEY_VM` | TP | 1 | 1 | +0 | 0 | KiCad 官方库 Connector:TestPoint (单脚测试点) |
| `TP_KEY_VP` | TP | 1 | 1 | +0 | 0 | KiCad 官方库 Connector:TestPoint (单脚测试点) |
| `TP_LED_B` | TP | 1 | 1 | +0 | 1 | KiCad 官方库 Connector:TestPoint (单脚测试点) |
| `TP_LED_G` | TP | 1 | 1 | +0 | 0 | KiCad 官方库 Connector:TestPoint (单脚测试点) |
| `TP_LED_R` | TP | 1 | 1 | +0 | 0 | KiCad 官方库 Connector:TestPoint (单脚测试点) |
| `TP_LIGHT_3V3` | TP | 1 | 1 | +0 | 0 | KiCad 官方库 Connector:TestPoint (单脚测试点) |
| `TP_MCLK` | TP | 1 | 1 | +0 | 0 | KiCad 官方库 Connector:TestPoint (单脚测试点) |
| `TP_PG` | TP | 1 | 1 | +0 | 0 | KiCad 官方库 Connector:TestPoint (单脚测试点) |
| `TP_PG_VCORE` | TP | 1 | 1 | +0 | 0 | KiCad 官方库 Connector:TestPoint (单脚测试点) |
| `TP_PG_VIO` | TP | 1 | 1 | +0 | 0 | KiCad 官方库 Connector:TestPoint (单脚测试点) |
| `TP_RESET` | TP | 1 | 1 | +0 | 0 | KiCad 官方库 Connector:TestPoint (单脚测试点) |
| `TP_SYS` | TP | 1 | 1 | +0 | 0 | KiCad 官方库 Connector:TestPoint (单脚测试点) |
| `TP_TS` | TP | 1 | 1 | +0 | 0 | KiCad 官方库 Connector:TestPoint (单脚测试点) |
| `TP_UART` | TP | 1 | 1 | +0 | 0 | KiCad 官方库 Connector:TestPoint (单脚测试点) |
| `TP_USB_D_N` | TP | 1 | 1 | +0 | 0 | KiCad 官方库 Connector:TestPoint (单脚测试点) |
| `TP_USB_D_P` | TP | 1 | 1 | +0 | 0 | KiCad 官方库 Connector:TestPoint (单脚测试点) |
| `TP_VBUS` | TP | 1 | 1 | +0 | 0 | KiCad 官方库 Connector:TestPoint (单脚测试点) |
| `TP_VCORE` | TP | 1 | 1 | +0 | 0 | KiCad 官方库 Connector:TestPoint (单脚测试点) |
| `TP_VIO` | TP | 1 | 1 | +0 | 0 | KiCad 官方库 Connector:TestPoint (单脚测试点) |
| `U_BATPROT` | IC | 3 | [0数据] | [0数据] | 3 | [0数据] |
| `U_CHG` | IC | 24 | 24 | +0 | 4 | BQ25896RTWR · state/check_netlist_pins.py:SPEC_PINS (项目自有真值表) |
| `U_DCDC_VCORE` | NET | 3 | 17 | +14 | 0 | TPS62130ARGTR · BOM opn=TPS62130ARGTR ⇒ KiCad 官方库 Regulator_Switching:TPS62130 (16 脚 + 散热焊盘) |
| `U_DCDC_VIO` | NET | 3 | 17 | +14 | 0 | TPS62130ARGTR · BOM opn=TPS62130ARGTR ⇒ KiCad 官方库 Regulator_Switching:TPS62130 (16 脚 + 散热焊盘) |
| `U_EN_SW` | NET | 4 | [0数据] | [0数据] | 0 | TPS22991RAA · [0数据] |
| `U_LDO_IO18` | NET | 5 | 5 | +0 | 0 | TPS7A2018DQNR · BOM opn=TPS7A2018DQNR ⇒ KiCad 官方库 Regulator_Linear:TPS7A20xxxDQN |
| `U_LDO_IO33` | NET | 5 | 5 | +0 | 0 | TPS7A2033DQNR · BOM opn=TPS7A2033DQNR ⇒ KiCad 官方库 Regulator_Linear:TPS7A20xxxDQN |
| `U_LDO_L18` | NET | 5 | 5 | +0 | 5 | TPS7A2018DQNR · BOM opn=TPS7A2018DQNR ⇒ KiCad 官方库 Regulator_Linear:TPS7A20xxxDQN |
| `U_LDO_L33` | NET | 5 | 5 | +0 | 0 | TPS7A2033DQNR · BOM opn=TPS7A2033DQNR ⇒ KiCad 官方库 Regulator_Linear:TPS7A20xxxDQN |
| `U_LDO_S12` | NET | 5 | 5 | +0 | 5 | TPS7A2012DQNR · BOM opn=TPS7A2012DQNR ⇒ KiCad 官方库 Regulator_Linear:TPS7A20xxxDQN |
| `U_LDO_S18B` | NET | 5 | 5 | +0 | 5 | TPS7A2018DQNR · BOM opn=TPS7A2018DQNR ⇒ KiCad 官方库 Regulator_Linear:TPS7A20xxxDQN |
| `U_LDO_S28` | NET | 4 | [0数据] | [0数据] | 4 | [0数据] |
| `U_PWR_SW` | NET | 4 | [0数据] | [0数据] | 0 | TPS22991RAA · [0数据] |
| `U_SUPV` | NET | 4 | [0数据] | [0数据] | 4 | [0数据] |
| `U_TEMP` | IC | 6 | 6 | +0 | 0 | TI TMP117 (DRV0006B, I2C 温度计 ±0.1°C, 地址 0x48) · state/check_netlist_pins.py:SPEC_PINS (项目自有真值表) |
| `X1` | CONN | 3 | [0数据] | [0数据] | 3 | [0数据] |

---

## 4. ★**怎么读这张表 (★评审口径★)**

- ★**本轮原理图按 `HW/netlist_v1_pins.csv` 全量画 (584 脚, 含 DNP 行)** ⇒ 图上脚数 = 表侧脚数 = 584, 逐器件相等 (★`state/check_sch_pinfull.py` 实测 K=0★)。
- ★**『表里脚数』是【这个设计实际用到的脚】, 不是【器件出厂总脚数】**★
  ⇒ 第 2 节那些『真实多脚』是正常的 (★空脚/NC/散热焊盘本来就不接★), ★**不是漏画**★
- ★**第 1 节那些『表里多脚』才是真问题** ★ ⇒ 逐个核: 是表里脚号写错了, 还是选型/脚数口径不一致
- ★**`[0数据]` = 本机查不到真实脚数** ★ ⇒ ★**型号回信后重跑 `state/gen_pin_reality_gap.py` 即可自动补齐** ★
- ★**没有改任何表** ★: `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` 一个字节都没动 (★md5 不变, 见交卷实测★)

---

## 5. ★**本轮未做/待下一轮 (★不硬凑★)**

- ★**表里多脚的那几项** ★: 需要**原厂型号回信**才能定论 ⇒ ★**本轮不猜、不改表** ★
- ★**`[0数据]` 的 29 个器件** ★: BOM 里 `opn` / `footprint` 还是『待定』 ⇒ 无权威源可查 ⇒ ★**本轮标 `[0数据]`** ★

