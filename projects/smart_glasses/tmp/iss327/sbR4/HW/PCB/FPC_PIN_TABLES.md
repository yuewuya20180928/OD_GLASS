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

## display: **Waveshare 2.8inch DSI LCD (SKU 22028)** —— ★**板侧 22p / 0.5mm** (Pi5 DISPLAY 座口径)

> ★★**2026-11-04 定稿**: demo 屏换成 **Waveshare 2.8inch DSI LCD** (2.8", 480×640, 2-lane, 屏侧原生 **15p/1.0mm**),
> 官方线 = **22p(0.5mm, Pi5 侧) ↔ 15p(1.0mm, 屏侧)** ⇒ **我们板上的座必须是 RPi mini-FPC 22p**,
> 座型 = **HIROSE FH12-22S-0.5SH(55)** (RPi 官方 CM4IO/CM5IO 封装)。
>
> ★★**针序必须照 Raspberry Pi 5 官方 DISPLAY 座 (J4) 抄** —— 与 **CM5IO 的 22p 针序不同** (CM5IO: 2/3=D0 · 5/6=D1 · 8/9=CLK · 20/21=I2C;
> Pi5 DISPLAY: 2/3=D1 · 5/6=CLK · 8/9=D0 · 11/12=I2C) ⇒ 抄错 ⇒ 屏必不亮。
> ★**16..22 在 Pi5 上是 NC** ⇒ 线缆里也是 NC ⇒ 本板自用 (承载 lane2/lane3 ⇒ 主板→屏段 4-lane)。
> 依据链与逐条出处: **`HW/PCB/PI5_DSI_22P_PINOUT.md`** (机器可读: `HW/PCB/pi5_dsi_22p.json`)。

| 座脚 | Pi5 J4 (官方) | 屏侧 15p | 板上的网 | 说明 |
|---|---|---|---|---|
| 1 | GND | GND | GND | 回流地 |
| 2 | DSI1_DN1 | DSI1_DN1 | `DSI_D0_D1_N` | DSI lane1 差分− |
| 3 | DSI1_DP1 | DSI1_DP1 | `DSI_D0_D1_P` | DSI lane1 差分+ |
| 4 | GND | GND | GND | 回流地 |
| 5 | DSI1_CN | DSI1_CN | `DSI_D0_CK_N` | DSI 时钟差分− |
| 6 | DSI1_CP | DSI1_CP | `DSI_D0_CK_P` | DSI 时钟差分+ |
| 7 | GND | GND | GND | 回流地 |
| 8 | DSI1_DN0 | DSI1_DN0 | `DSI_D0_D0_N` | DSI lane0 差分− |
| 9 | DSI1_DP0 | DSI1_DP0 | `DSI_D0_D0_P` | DSI lane0 差分+ |
| 10 | GND | GND | GND | 回流地 |
| 11 | SCL0 | SCL0 | `I2C_B_SCL` | **屏控制 I2C** (屏内 MCU @0x45) —— 不是触控线 |
| 12 | SDA0 | SDA0 | `I2C_B_SDA` | 屏控制 I2C |
| 13 | GND | GND | GND | 回流地 |
| 14 | 3V3 | 3V3 | `LIGHT_3V3` | 面板 3.3V |
| 15 | 3V3 | 3V3 | `LIGHT_3V3` | 面板 3.3V |
| 16 | NC | — | `DSI_D0_D2_N` | ★自用: lane2 差分− (4-lane 预留) |
| 17 | NC | — | `DSI_D0_D2_P` | ★自用: lane2 差分+ |
| 18 | NC | — | `DSI_D0_D3_N` | ★自用: lane3 差分− |
| 19 | NC | — | `DSI_D0_D3_P` | ★自用: lane3 差分+ |
| 20 | NC | — | GND | ★自用: 预留地 |
| 21 | NC | — | GND | ★自用: 预留地 |
| 22 | NC | — | GND | ★自用: 预留地 |

★demo 屏只跑 **lane0 + lane1 + 时钟** (2-lane), lane2/lane3 从 SoM DSI TX 一路引到座上、屏端不接。
★`I2C_B` 上拉在 `VDD_3V3_IO` (3.3V) ⇒ 与屏内 MCU 的 3.3V I2C **同域, 无需电平转换**; 同总线上还挂 TMP117 (0x48), 与屏 MCU (0x45) **地址不冲突**。
★背光: Waveshare 屏**没有独立背光脚** ⇒ 板上不做 BOOST/恒流/PWM 链 (原先按 Radxa 8HD 做的背光链已删)。

> ★**已作废**: 2026-11-03 之前这里是「Radxa Display 8HD 板侧 39p/0.3mm」表 —— demo 屏已换 Waveshare 2.8inch ⇒ 整表作废。
> 该屏的**屏侧 40p 官方原文**仍在 `HW/STEP1_PARTS_SPEC.md` §3.1 (留档用, 不再用于本板)。
