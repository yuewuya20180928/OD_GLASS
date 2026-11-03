# FPC 针位表 (按真实在售模组)

## camera: Radxa Camera 4K (IMX415) —— 31p / 0.3mm, 座 HIROSE FH35C-31S-0.3SHW(50)

| 针 | 定义 | 针 | 定义 |
|---|---|---|---|
| 1 | GND | 2 | MDN4 |
| 3 | MDP4 | 4 | GND |
| 5 | MDN3 | 6 | MDP3 |
| 7 | GND | 8 | NC |
| 9 | NC | 10 | GND |
| 11 | MDN2 | 12 | MDP2 |
| 13 | GND | 14 | MDN1 |
| 15 | MDP1 | 16 | GND |
| 17 | MCN | 18 | MCP |
| 19 | GND | 20 | MCLK |
| 21 | GND | 22 | NC |
| 23 | NC | 24 | SCL |
| 25 | SDA | 26 | NC |
| 27 | RESET | 28 | VCC3.3V |
| 29 | VCC3.3V | 30 | VCC5V |

## display: **Radxa Display 8HD** —— ★**板侧 39p / 0.3mm** (屏侧原生 40p / 0.5mm)

> ★★**2026-11-03 19:3x 换口径**: 板上画的是**板侧 39p/0.3mm 座** (HIROSE **FH35C-39S-0.3SHW(50)**, 背夹 + 上下双面触点, ★**与相机侧 FH35C-31S-0.3SHW(50) 同系列**);
> 原厂转接线 AC013 一头插屏 (40p/0.5mm) 一头插我们的座 ⇒ **我们不用自制排线**;
> ★**换算式: 屏侧脚号 = 板侧脚号 + 1** (屏侧 pin1=NC 被原厂线省掉, 其余 39 脚 1:1 直通, 无交叉);
> ★老板 19:29 拍板 **demo 不需要触控** ⇒ 板侧 23~27 (TP-RESET/VCC/INT/SDA/SCL) 我们**不接**;
> ★背光 = **1 串 2 颗并联** (阴极 34/35 同网, 阳极 38/39 同网) ⇒ 板侧要自带 BOOST+恒流+PWM (ISS-173);
> 屏侧 40p 原文表见 `HW/STEP1_PARTS_SPEC.md` §3.1; 39p 表的三个原厂出处见 `HW/PCB/DISPLAY_39P_PINOUT.md`。

| 板侧脚 | 信号 | 屏侧脚 | 说明 |
|---|---|---|---|
| 1 | VDD3V3 | 2 | Panel main logic 3.3V supply (Q6A net VCC_3V3_LCD). Panel-si |
| 2 | IOVCC1V8-3V3 | 3 | Panel IO supply, 1.8V or 3.3V selectable (Q6A: VCC_1V8 via R |
| 3 | SENSOR-INT | 4 | Panel-side pin 4 = 'NC' with description 'INT 1' (gravity se |
| 4 | RESET | 5 | Panel global reset (panel-side pin 5 Reset). Q6A: DISP0_RESE |
| 5 | NC | 6 | Panel-side pin 6 = 'NC' with description 'INT 2' (gravity se |
| 6 | GND1 | 7 | Ground. Panel-side pin 7 (GND) |
| 7 | MIPI-0N | 8 | MIPI DSI lane 0 differential negative (Q6A net DSI0_B0_LN0_M |
| 8 | MIPI-0P | 9 | MIPI DSI lane 0 differential positive (DSI0_A0_LN0_P). Panel |
| 9 | GND2 | 10 | Ground. Panel-side pin 10 (GND) |
| 10 | MIPI-1N | 11 | MIPI DSI lane 1 differential negative (DSI0_A1_LN1_M). Panel |
| 11 | MIPI-1P | 12 | MIPI DSI lane 1 differential positive (DSI0_C0_LN1_P). Panel |
| 12 | GND3 | 13 | Ground. Panel-side pin 13 (GND) |
| 13 | MIPI-CKN | 14 | MIPI DSI differential clock negative (DSI0_C1_CLK_M). Panel- |
| 14 | MIPI-CKP | 15 | MIPI DSI differential clock positive (DSI0_B1_CLK_P). Panel- |
| 15 | GND4 | 16 | Ground. Panel-side pin 16 (GND) |
| 16 | MIPI-2N | 17 | MIPI DSI lane 2 differential negative (DSI0_B2_LN2_M). Panel |
| 17 | MIPI-2P | 18 | MIPI DSI lane 2 differential positive (DSI0_A2_LN2_P). Panel |
| 18 | GND5 | 19 | Ground. Panel-side pin 19 (GND) |
| 19 | MIPI-3N | 20 | MIPI DSI lane 3 differential negative (DSI0_NC_LN3_M). Panel |
| 20 | MIPI-3P | 21 | MIPI DSI lane 3 differential positive (DSI0_C2_LN3_P). Panel |
| 21 | GND6 | 22 | Ground. Panel-side pin 22 (GND) |
| 22 | GND7 | 23 | Ground. Panel-side pin 23 (GND) |
| 23 | TP-RESET | 24 | Touch panel reset (Q6A net TP_RST). Panel-side pin 24 (TP_RE |
| 24 | TP-VCC | 25 | Touch panel 3.3V supply (Q6A net VCC_3V3) - the touch contro |
| 25 | TP-INT | 26 | Touch interrupt (Q6A net TP_INT). Panel-side pin 26 (TP_INT) |
| 26 | TP-SDA | 27 | Touch I2C data (Q6A net TP_SDA, level-shifted by U8 UM3204H) |
| 27 | TP-SCL | 28 | Touch I2C clock (Q6A net TP_SCL). Panel-side pin 28 (TP_SCL) |
| 28 | GND8 | 29 | Ground. Panel-side pin 29 (GND) |
| 29 | GND9 | 30 | Ground. Panel-side pin 30 (GND) |
| 30 | VCC3V31 | 31 | Panel 3.3V supply, 2nd pin (Q6A net VCC_3V3_LCD). Panel-side |
| 31 | VCC3V32 | 32 | Panel 3.3V supply, 3rd pin. Panel-side pin 32 (VDD 3.3V) |
| 32 | GND11 | 33 | Ground (official numbering skips GND10). Panel-side pin 33 ( |
| 33 | GND12 | 34 | Ground. Panel-side pin 34 (GND) |
| 34 | LED-1 | 35 | BACKLIGHT CATHODE, 1st of 2. Panel-side pin 35 (LED-). Tie w |
| 35 | LED- | 36 | BACKLIGHT CATHODE, 2nd of 2. Panel-side pin 36 (LED-). Never |
| 36 | NC | 37 | No connect (stays unconnected on the 39p side too). Panel-si |
| 37 | NC | 38 | No connect (stays unconnected on the 39p side too). Panel-si |
| 38 | LED+1 | 39 | BACKLIGHT ANODE, 1st of 2. Panel-side pin 39 (LED+). Tie wit |
| 39 | LED+ | 40 | BACKLIGHT ANODE, 2nd of 2. Panel-side pin 40 (LED+) |
