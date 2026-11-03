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

## display: Radxa Display 8HD/10FHD —— 40p / 0.5mm

| 针 | 定义 | 针 | 定义 |
|---|---|---|---|
| 1 | NC | 2 | VDD_3V3 |
| 3 | VCCIO | 4 | NC |
| 5 | RESET | 6 | NC |
| 7 | GND | 8 | MIPI_0N |
| 9 | MIPI_0P | 10 | GND |
| 11 | MIPI_1N | 12 | MIPI_1P |
| 13 | GND | 14 | MIPI_CKN |
| 15 | MIPI_CKP | 16 | GND |
| 17 | MIPI_2N | 18 | MIPI_2P |
| 19 | GND | 20 | MIPI_3N |
| 21 | MIPI_3P | 22 | GND |
| 23 | GND | 24 | TP_RESET |
| 25 | TP_VCC | 26 | TP_INT |
| 27 | TP_SDA | 28 | TP_SCL |
| 29 | GND | 30 | GND |
| 31 | VDD_3V3 | 32 | VDD_3V3 |
| 33 | GND | 34 | GND |
| 35 | LED_N | 36 | GND |
| 37 | NC | 38 | NC |
| 39 | GND | 40 | LED_P |

> ★★**2026-11-03 19:0x 更正与推算 (ISS-170)**
>
> **① 这张 40 针表是"屏侧"接口, 不是我们主板要画的座** —— Radxa Display 8HD 的官方 FPC 规格原文:
> "**39-pin 0.3mm pitch (Motherboard side) to 40-pin 0.5mm pitch (Display side)**"
> (另一版 15-pin 1.0mm 主板侧) ⇒ **我们主板要对插的是转接线的板端 = 39p/0.3mm** ⇒ ★**本表的针号不能直接用在主板侧**
> ⇒ ⇒ 主板侧针位表正在取: `HW/PCB/DISPLAY_39P_PINOUT.md` (专项进行中, 任务书 `state/TASK_display_39p_pinout.md`)
>
> **② "40→39" 的算术结论 (按位数的)**: **屏侧 5 个 NC 脚去掉 1 个 ⇒ 恰好 39 个位置**;
> 两种 LED± 标注下都成立 ⇒ **39 不是靠并脚省出来的, 是转接线省掉了一个 NC 位**
> ⇒ ★**被省的是哪一个 NC (1/4/6/37/38 中的哪个) 必须定死** —— 少一位 ⇒ 后面所有信号编号整体错一位
>
> **③ ★本地两份文档对 35/36/39/40 四个脚互相矛盾 (待官方裁定)**:
> | 脚 | `HW/STEP1_PARTS_SPEC.md` | **本表** |
> |---|---|---|
> | 35 | LED− | LED_N |
> | 36 | LED− | GND |
> | 39 | LED+ | GND |
> | 40 | LED+ | LED_P |
> ⇒ ★★**这不是小事**: LED± 各一根还是各两根 ⇒ **背光是 1 串还是 2 串** ⇒ 直接决定 ISS-173 的 12V BOOST 驱动拓扑
> ⇒ ★**以 Radxa 官方针位表为准**, 专项正在裁定 ⇒ ★**在裁定之前, 本表的这 4 个脚按"待官方确认"对待**
