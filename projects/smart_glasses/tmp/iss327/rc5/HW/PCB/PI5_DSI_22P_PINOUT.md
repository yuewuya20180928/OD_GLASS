# Pi5 DSI 22p 座针位表 —— demo 主板 CONN_LIGHT 板内 FPC 座

> 结论一句话: **板上的显示 FPC 座 = Hirose FH12-22S-0.5SH(55) (22p/0.5mm/右角)**, 针序**必须照 Pi 5 官方原理图 J4 (DISPLAY 座) 抄**, 不能照 CM5IO 的 22p 抄 —— 这两套 22p 针序**不一样**。
>
> 写于 2026-11-04 · 总工 · 机器可读版: `HW/PCB/pi5_dsi_22p.json`

---

## 1. 为什么这件事必须先查清 (背景)

demo 屏换成 **Waveshare 2.8inch DSI LCD (SKU 22028)** 后, 屏侧原生接口是 **15p / 1.0mm**, 而官方线缆是 **22p(0.5mm, Pi5 侧) ↔ 15p(1.0mm, 屏侧)**。
⇒ 板上的座不是"随便一个 22p", 它必须**与 Pi 5 板上的 DISPLAY 座逐针一致**, Waveshare 那根线才插得上、信号才通。

---

## 2. 三条独立证据 (互相印证)

| # | 来源 | 拿到什么 |
|---|---|---|
| **P1** | **Raspberry Pi Ltd 官方 Pi 5 原理图** `RP-008350-DS-raspberry-pi-5-mechanical.pdf` (1 页 A1, J4 = DISPLAY 座) | J4 逐脚网名: 2=DSI1_DN1 / 3=DSI1_DP1 / 5=DSI1_CN / 6=DSI1_CP / 8=DSI1_DN0 / 9=DSI1_DP0 / 11=SCL0 / 12=SDA0 / 15=3V3; **1,4,7,10,13,14 = GND**; **16..30 标红叉 (NC)** |
| **P2** | **Raspberry Pi 官方 CM4IO / CM5IO KiCad 设计文件** (`CM5IO.pretty/Hirose_FH12-22S-0.5SH_1x22-1MP_P0.50mm_Horizontal.kicad_mod` + `CM5IO.kicad_sch` 属性) | 座型号 = **Hirose FH12-22S-0.5SH(55)**, 22p/0.5mm/右角/1 固定柱; 官方封装几何 (焊盘 0.3×1.3mm, pitch 0.5, pad1 在 +x 端, 本体 -1.2~+3.4, courtyard ±8.55×-3~+4.9) |
| **P3/P4** | **Waveshare 官方 wiki「2.8inch DSI LCD」** Interface Definition 表 + 接线说明 | 屏侧 **15p** 脚名脚号: 1 GND / 2 DSI1_DN1 / 3 DSI1_DP1 / 4 GND / 5 DSI1_CN / 6 DSI1_CP / 7 GND / 8 DSI1_DN0 / 9 DSI1_DP0 / 10 GND / 11 SCL0 / 12 SDA0 / 13 GND / 14 3V3 / 15 3V3; 接线说明明写 "22PIN DSI1 interface … DSI Cable-12cm" |

**交叉验证结果**:
- P1 (Pi5 J4, 官方) 的 1..15 脚名与 P3 (Waveshare 屏侧 15p) 的 1..15 脚名 **逐脚完全一致** ⇒ 两侧针序同构 ✔
- P2 的封装 (Hirose FH12) 与 P5 (Adafruit: "Pi 5 的 22p 与 CM DK 同一 mini-FPC 格式") 一致 ⇒ 官方封装可直接用 ✔

---

## 3. ★★关键推论: 那根线是 1:1 直通, 所以 16..22 是我们的

线缆是**被动**的。屏侧只有 15 脚, 且 15 脚的信号已经由 Pi5 J4 的 1..15 脚**全部**提供 ⇒ 线缆只能把 **22p 的 1..15 一一对应到 15p 的 1..15**。
⇒ **22p 的 16..22 在 Pi 5 上是 NC ⇒ 在线缆里也是 NC ⇒ 板子可以自由使用这 7 个脚** (本项目拿来放 lane2/lane3 差分, 满足老板"主板→屏段 4-lane"的要求)。

---

## 4. ★★最容易踩的坑: CM5IO 的 22p 针序 ≠ Pi5 DISPLAY 座的针序

从 **CM5IO 官方 PCB 焊盘网表** (P6) 读出来的 22p (J5, MIPI0):

```
1 GND | 2 D0_N | 3 D0_P | 4 GND | 5 D1_N | 6 D1_P | 7 GND | 8 C_N | 9 C_P | 10 GND
| 11 D2_N | 12 D2_P | 13 GND | 14 D3_N | 15 D3_P | 16 GND | 17 GPIO0 | 18 GPIO1 | 19 GND | 20 SCL | 21 SDA | 22 3V3
```

对比 Pi5 的 **DISPLAY** 座 (P1): 2/3 = **D1** (不是 D0), 5/6 = **时钟** (不是 D1), 8/9 = **D0** (不是时钟), 11/12 = **SCL/SDA** (不是 D2)。

⇒ **同一个 22p 物理格式, 两种针序**。抄错 ⇒ DSI 差分对全错、I2C 接错、时钟接到数据上 ⇒ **屏绝对不亮**。
⇒ 我们的座**只能照 P1 (Pi5 DISPLAY) 抄**。

---

## 5. 板侧针位表 (落地口径)

| 座脚 | Pi5 J4 (官方) | 屏侧 15p | 我们板上的网 | 用途 | 装 |
|---|---|---|---|---|---|
| 1 | GND | GND | GND | 回流地 | 必装 |
| 2 | DSI1_DN1 | DSI1_DN1 | `DSI_D0_D1_N` | lane1 差分− | 必装 |
| 3 | DSI1_DP1 | DSI1_DP1 | `DSI_D0_D1_P` | lane1 差分+ | 必装 |
| 4 | GND | GND | GND | 回流地 | 必装 |
| 5 | DSI1_CN | DSI1_CN | `DSI_D0_CK_N` | DSI 时钟− | 必装 |
| 6 | DSI1_CP | DSI1_CP | `DSI_D0_CK_P` | DSI 时钟+ | 必装 |
| 7 | GND | GND | GND | 回流地 | 必装 |
| 8 | DSI1_DN0 | DSI1_DN0 | `DSI_D0_D0_N` | lane0 差分− | 必装 |
| 9 | DSI1_DP0 | DSI1_DP0 | `DSI_D0_D0_P` | lane0 差分+ | 必装 |
| 10 | GND | GND | GND | 回流地 | 必装 |
| 11 | SCL0 | SCL0 | `I2C_B_SCL` | **屏控制 I2C** (屏内 MCU @0x45) | 必装 |
| 12 | SDA0 | SDA0 | `I2C_B_SDA` | 屏控制 I2C | 必装 |
| 13 | GND | GND | GND | 回流地 | 必装 |
| 14 | 3V3 | 3V3 | `LIGHT_3V3` | 面板 3.3V | 必装 |
| 15 | 3V3 | 3V3 | `LIGHT_3V3` | 面板 3.3V | 必装 |
| 16 | NC | — | `DSI_D0_D2_N` | ★自用: lane2 差分− | 必装 |
| 17 | NC | — | `DSI_D0_D2_P` | ★自用: lane2 差分+ | 必装 |
| 18 | NC | — | `DSI_D0_D3_N` | ★自用: lane3 差分− | 必装 |
| 19 | NC | — | `DSI_D0_D3_P` | ★自用: lane3 差分+ | 必装 |
| 20 | NC | — | GND | 预留 | 必装 |
| 21 | NC | — | GND | 预留 | 必装 |
| 22 | NC | — | GND | 预留 | 必装 |

**demo 实际用到的差分**: 只有 lane0 + lane1 + CK (屏是 2-lane)。lane2/lane3 从 SoM DSI TX 一路引到座上, **demo 屏端不接** ⇒ 满足"主板→屏段 4-lane、屏端 2-lane"。

**I2C 电平**: `I2C_B` 上拉已在 `VDD_3V3_IO` (3.3V) ✔ —— 与屏内 MCU 的 3.3V I2C 同域, **不需要电平转换**。
★注意: `I2C_B` 上还挂着 **TMP117 (0x48)**, 屏内 MCU 是 **0x45** ⇒ 地址不冲突 ✔。

---

## 6. 连接器 / 封装 (可直接用官方件)

- **型号**: `Hirose FH12-22S-0.5SH(55)` —— 22 脚 / 0.5mm / 右角(水平) / 表面贴装 / **底接触** / 1 个固定柱
- **官方封装**: `Hirose_FH12-22S-0.5SH_1x22-1MP_P0.50mm_Horizontal.kicad_mod` (Raspberry Pi 官方 CM4IO/CM5IO 设计文件内, 已抄进本项目 `HW/PCB/`)
- **焊盘**: 22 个, 0.3×1.3mm, pitch 0.5mm, y = -1.85 (相对本体中心), **pad1 在 +x 端** ⇒ 脚的 x 坐标 = +5.25 → -5.25
- **本体**: F.Fab -7.05..+7.05 × -1.2..+3.4; Courtyard ±8.55 × -3.0..+4.9

---

## 7. 未决 / 必须实物核对 (下单前)

1. ★**买线后用万用表核 22p 端针序** (1 脚方向、3V3 与 GND 位置) —— 与 SoM DF40C 的 pin1 行问题**同级**: 错了整条 DSI 反接、屏必不亮。
2. ★**确认线缆 22p 端触点朝向** (FFC 触点朝下=底接触座可用; 若为顶接触则要翻线或换座型)。
3. 整机阶段换 **视崖 0.49" SiOLED** 时, 本座的 16..19 自用脚位作废, 改按面板原厂接口定义。

---

## 8. 变更影响

- 板上 **CONN_LIGHT 从 39p/0.3mm (FH35C-39S) 改为 22p/0.5mm (FH12-22S)** ⇒ 板宽方向少 17 个焊盘, 机械上更宽松。
- 之前按 Radxa 40p 表写的屏侧 pin 行 (GND 11 个 / NC 4 个 / 3V3 …) **全部作废**, 改按本表。
- `state/check_netlist_pins.py` 的 `SPEC_PINS['CONN_LIGHT']` 由 39 → **22**, 并删掉过渡期的"缺脚豁免"。
