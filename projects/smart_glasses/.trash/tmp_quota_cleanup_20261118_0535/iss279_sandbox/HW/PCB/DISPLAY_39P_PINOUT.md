# Radxa Display 8 HD —— ★主板侧 39-pin / 0.3mm FPC 座 针位表

> ★★ 本文件只回答一件事: **我们主板上那个 39p / 0.3mm 的座, 第 1 脚到第 39 脚分别是什么**。
> ★ 屏侧 40p / 0.5mm 的针位表已在 `HW/STEP1_PARTS_SPEC.md` §3.1 闭环 (Radxa 官方 Pinout 原文), 本文件**不重复抄屏侧表**, 只在 §3 给 40→39 的对应/合并关系。
> ★ 纪律: 全部结论只认 **Radxa 原厂资料** (官方文档站 / 官方 GitHub / 原厂原理图 PDF / 官方产品页); 查不到的写「未查到」并附试过的 URL (§8); **任何脚位都不猜**。

---

## 0. 结论速览 (TL;DR)

| # | 问题 | 结论 | 证据 |
|---|---|---|---|
| 1 | 39p 侧的逐脚表 | ★**已拿到**, 39 针逐针, 见 §2 | [S1] ROCK 5C 官方逐脚表 + [S4] Q6A 原厂原理图 J10, **两处逐针完全一致** |
| 2 | 座型号 | ★**HIROSE FH35C-39S-0.3SHW(50)** (39 位 / 0.3mm / 镀金) | [S1] ROCK 5C 官方接口页原文 |
| 3 | 座型 / 触点方向 | ★**翻盖锁扣 (flip-lock) + 下接触 (bottom contact)**; FH35C 系列本体 = **背夹式 (back flip) + 上下双面触点** ⇒ **与我们已有的 camera 座 FH35C-31S-0.3SHW(50) 同系列同机构, 改针数即可** | [S2] ROCK 5A 官方接口页 + 项目 `PINOUT_FOOTPRINT_SPEC.md` §10 (HIROSE FH35C 系列规格书) |
| 4 | 40→39 到底省了哪个脚 | ★**省的是屏侧第 1 脚 (NC)**, 其余 39 脚 **1:1 直通、零合并** ⇒ ★**屏侧脚号 = 主板侧脚号 + 1 (从第 2 脚起)** | §3; [S1][S4][S5][S11] 四方交叉 |
| 5 | 主板侧有没有触控 I2C | ★**有**: 23 TP-RESET / 24 TP-VCC / 25 TP-INT / 26 TP-SDA / 27 TP-SCL | [S1][S4] |
| 6 | 主板侧有没有背光 | ★**有**: 34 LED-1 / 35 LED- (双阴极) / 38 LED+1 / 39 LED+ (双阳极) | [S1][S4][S5] |
| 7 | 15p/1.0mm 那版带什么 | ★**带 DSI + 触控 I2C, 但背光 PWM / 触控 RST / 触控 INT / 重力传感器 INT 都甩到外接 7 针排针上** ⇒ 15p 版**装不下「4-lane DSI + 触控 + 背光」** ⇒ ★**我们必须走 39p 版** | [S7][S8][S9][S10] |
| 8 | 8HD 自己的背光电压/电流/串数 | ★**未查到** (官方只写 "Backlight: White LED" / 300 cd/m²) ⇒ 只有**结构性结论**: ★**1 串, 2 颗并联** (2 阴极 + 2 阳极, 板上并成一路) | §4; 未查到清单见 §8 |
| 9 | Radxa 有没有公开 39p 转接线本身的图纸 | ★**没有** (只有 15p 版 AC012 的分线定义图; 39p 版 AC013 的针位图 URL 404) ⇒ 本表的 39p 映射是**从原厂板级针位表反推**, 但**由 4 个独立原厂来源互证** | §8 |

---

## 1. 连接器 (header)

| 项 | 值 | 出处 |
|---|---|---|
| **型号** | ★**HIROSE FH35C-39S-0.3SHW(50)** | [S1] ROCK 5C: "Utilizes a 39-pin, 0.3 mm pitch, gold-plated connector, model FH35C-39S-0.3SHW(50)" |
| **厂商** | HIROSE | [S1] |
| **针数 / 间距** | ★**39 位置 / 0.3 mm pitch** | [S1][S2][S3] |
| **镀金** | gold-plated | [S1] |
| **形态** | SMD right-angle FPC 连接器 (贴片, 直角出线) | [S2] ROCK 5A: "39-pin, 0.3 mm pitch, SMD right-angle FPC connector" |
| **连接方式 / 触点** | ★**flip-lock (翻盖锁扣), bottom contact (下接触)** | [S2] ROCK 5A: "Connection: flip-lock, bottom contact" |
| **★FH35C 系列本体机构** | ★**背夹式 (back flip) + 上下双面触点 (Top & Bottom contact) + 座体高 0.9mm + 兼容 0.2mm 厚 FPC** ⇒ **与本项目 camera 座 FH35C-31S-0.3SHW(50) 同系列同机构** (奇偶脚分上/下排) | 项目 `HW/PCB/PINOUT_FOOTPRINT_SPEC.md` §10 (HIROSE FH35C 系列规格书原文) — ⇒ **footprint 可在已自绘的 FH35C-31S 基础上改针数 (31→39)**, 但**必须回 HIROSE 拿 FH35C-39S 的原厂 land pattern / 尺寸表逐项核对** (本单未取 FH35C-39S 原厂图纸) |
| **板端还是屏端** | ★**板端 (Motherboard side)** —— 39p/0.3mm 这一头插我们主板; 屏端是 40p/0.5mm | [S7] Radxa 官方产品页: "39-pin 0.3mm pitch (Motherboard side) to 40-pin 0.5mm pitch (Display side)" |
| **配套原厂排线** | ★**FPC AC013 / AC013N** ("39P 0.3mm to 40P 0.5mm, Opposite Side FPC Cable", Plug-and-Play, For Radxa Display 8 HD and Display 10 FHD) | [S13][S14] |
| **Dragon Q6A 是否同型号** | ★Q6A 官方页只写 "39-Pin / 0.3mm pitch FPC 接口" 未写型号; 但 Q6A 原理图 J10 符号的**针名与 [S1] 的 ROCK 5C 官方 39 针表逐针一致** (含 `GND1..GND9/GND11/GND12` 缺 `GND10` 这种怪癖) ⇒ ★**Q6A 用的就是同一颗 FH35C-39S-0.3SHW(50)** — **[推断, 高置信]**, 若要 100% 落死需 Radxa 出 Q6A BOM | [S3][S4] |

---

## 2. ★ 主板侧 39 针逐脚表 (我们画座就照这张)

> ★ 信号名取 [S1] (ROCK 5C 官方 39 针表) 原文; [S4] (Dragon Q6A 原厂原理图 V1.21 sheet 31/37, PDF 第 29 页, 连接器 **J10 / LCD_39P**) 的针名与网络**逐针一致**, 两处互证。
> ★ 电平一列取 [S1] 的 "Voltage &" 栏。

| 脚 | 信号名 | 电平 | 说明 | 屏侧 40p 对应 | 出处 |
|---|---|---|---|---|---|
| **1** | `VDD3V3` | 3.3V | 屏主逻辑 3.3V 供电 (Q6A 网名 `VCC_3V3_LCD`) | 2 VDD | [S1][S4] p.29 |
| **2** | `IOVCC1V8-3V3` | 1.8V | 屏 IO 供电, 1.8V 或 3.3V 可选 (Q6A: `VCC_1V8` 经 R312 0R 串入) | 3 VCCIO | [S1][S4] p.29 |
| **3** | `NULL` (Q6A 符号名 `SENSOR-INT`) | — | ★ 面板侧第 4 脚 = **INT 1** (重力传感器中断 1)。ROCK 5C 同位空置; **Q6A 已把它命名成 `SENSOR-INT` 但板上并未接任何网络** ⇒ 我们**可以用**这一脚接面板的重力传感器中断 (可选功能) | 4 NC / INT 1 | [S1][S5][S4] p.29 |
| **4** | `RESET` | 3.3V | 屏全局复位 (面板侧 5 Reset) — Q6A: `DISP0_RESET_N` 经 R313 0R 串入 | 5 Reset | [S1][S4] p.29 |
| **5** | `NULL` (Q6A 符号名未标注, 原图显示为 "6") | — | ★ 面板侧第 6 脚 = **INT 2** (重力传感器中断 2)。ROCK 5C 空置, Q6A 板上未接 | 6 NC / INT 2 | [S1][S5][S4] p.29 |
| **6** | `GND1` | — | 地 | 7 GND | [S1][S4] p.29 |
| **7** | `MIPI-0N` | — | MIPI DSI lane0 差分负 (Q6A 网名 `DSI0_B0_LN0_M`) | 8 MIPI_0N | [S1][S4] p.29 |
| **8** | `MIPI-0P` | — | MIPI DSI lane0 差分正 (`DSI0_A0_LN0_P`) | 9 MIPI_0P | [S1][S4] p.29 |
| **9** | `GND2` | — | 地 | 10 GND | [S1][S4] p.29 |
| **10** | `MIPI-1N` | — | MIPI DSI lane1 差分负 (`DSI0_A1_LN1_M`) | 11 MIPI_1N | [S1][S4] p.29 |
| **11** | `MIPI-1P` | — | MIPI DSI lane1 差分正 (`DSI0_C0_LN1_P`) | 12 MIPI_1P | [S1][S4] p.29 |
| **12** | `GND3` | — | 地 | 13 GND | [S1][S4] p.29 |
| **13** | `MIPI-CKN` | — | MIPI DSI 差分时钟负 (`DSI0_C1_CLK_M`) | 14 MIPI_CKN | [S1][S4] p.29 |
| **14** | `MIPI-CKP` | — | MIPI DSI 差分时钟正 (`DSI0_B1_CLK_P`) | 15 MIPI_CKP | [S1][S4] p.29 |
| **15** | `GND4` | — | 地 | 16 GND | [S1][S4] p.29 |
| **16** | `MIPI-2N` | — | MIPI DSI lane2 差分负 (`DSI0_B2_LN2_M`) | 17 MIPI_2N | [S1][S4] p.29 |
| **17** | `MIPI-2P` | — | MIPI DSI lane2 差分正 (`DSI0_A2_LN2_P`) | 18 MIPI_2P | [S1][S4] p.29 |
| **18** | `GND5` | — | 地 | 19 GND | [S1][S4] p.29 |
| **19** | `MIPI-3N` | — | MIPI DSI lane3 差分负 (`DSI0_NC_LN3_M`) | 20 MIPI_3N | [S1][S4] p.29 |
| **20** | `MIPI-3P` | — | MIPI DSI lane3 差分正 (`DSI0_C2_LN3_P`) | 21 MIPI_3P | [S1][S4] p.29 |
| **21** | `GND6` | — | 地 | 22 GND | [S1][S4] p.29 |
| **22** | `GND7` | — | 地 | 23 GND | [S1][S4] p.29 |
| **23** | `TP-RESET` | 3.3V | ★**触控复位** (Q6A 网名 `TP_RST`) | 24 TP_RESET | [S1][S4] p.29 |
| **24** | `TP-VCC` | 3.3V | ★**触控电源** 3.3V (Q6A 网名 `VCC_3V3`) | 25 TP_VCC | [S1][S4] p.29 |
| **25** | `TP-INT` | 3.3V | ★**触控中断** (Q6A 网名 `TP_INT`) | 26 TP_INT | [S1][S4] p.29 |
| **26** | `TP-SDA` | 3.3V | ★**触控 I2C 数据** (Q6A 网名 `TP_SDA`, 经 U8 `UM3204H` 电平转换) | 27 TP_SDA | [S1][S4] p.29 |
| **27** | `TP-SCL` | 3.3V | ★**触控 I2C 时钟** (Q6A 网名 `TP_SCL`) | 28 TP_SCL | [S1][S4] p.29 |
| **28** | `GND8` | — | 地 | 29 GND | [S1][S4] p.29 |
| **29** | `GND9` | — | 地 | 30 GND | [S1][S4] p.29 |
| **30** | `VCC3V31` | 3.3V | ★ 屏 3.3V 供电 (第 2 路, Q6A 网名 `VCC_3V3_LCD`) | 31 VDD 3.3V | [S1][S4] p.29 |
| **31** | `VCC3V32` | 3.3V | ★ 屏 3.3V 供电 (第 3 路) | 32 VDD 3.3V | [S1][S4] p.29 |
| **32** | `GND11` | — | 地 (★注意官方编号**跳过 GND10**) | 33 GND | [S1][S4] p.29 |
| **33** | `GND12` | — | 地 | 34 GND | [S1][S4] p.29 |
| **34** | `LED-1` | — | ★★**背光阴极 (第 1 只)** — 面板侧 35 LED- | 35 LED- | [S1][S4] p.29 |
| **35** | `LED-` | — | ★★**背光阴极 (第 2 只)** — 面板侧 36 LED- | 36 LED- | [S1][S4][S5] |
| **36** | `NULL` | — | ★ 空脚 | 37 NC | [S1][S4] p.29 |
| **37** | `NULL` | — | ★ 空脚 | 38 NC | [S1][S4] p.29 |
| **38** | `LED+1` | — | ★★**背光阳极 (第 1 只)** — 面板侧 39 LED+ | 39 LED+ | [S1][S4] p.29 |
| **39** | `LED+` | — | ★★**背光阳极 (第 2 只)** — 面板侧 40 LED+ | 40 LED+ | [S1][S4][S5] |

★ **符号里另有 2 个机械焊盘, 不是 FPC 触点**: Q6A 原理图 J10 符号除 1..39 外还有 `PAD1` (符号脚 41, 顶边) 与 `PAD2` (符号脚 40, 底边) —— 机械固定焊盘, **不占 39 针里的任何一位, 画座时不要多画针**。出处: [S4] p.29 符号图 (J10 `LCD_39P`)。

---

## 3. ★ 屏侧 40p → 主板侧 39p 对应 / 合并表

★ **核心结论 (一句话)**: ★★**39p 侧 = 屏侧 40p 表「原样搬过来, 只把屏侧第 1 脚 (NC) 去掉」; 没有任何信号被合并 (没有把两个脚并成一个脚), 也没有丢任何功能信号。**
⇒ ★**换算公式: 主板侧脚号 = 屏侧脚号 − 1 (对屏侧第 2~40 脚); 屏侧第 1 脚在 39p 侧不存在。**

| 屏侧 40p 脚 | 屏侧信号 | 主板侧 39p 位置 | 状态 |
|---|---|---|---|
| **1** | NC | ★**(无)** | ★**确定: 就是这个 NC 被省掉** —— 见下方"三条独立证据" |
| 2 | VDD 3.3V | **1** | 确定 (1:1) |
| 3 | VCCIO (1.8–3.3V) | **2** | 确定 (1:1) |
| 4 | NC (面板描述 INT 1) | **3** | 确定 (1:1) — 官方表写 NC, 实际是重力传感器中断 1 |
| 5 | Reset | **4** | 确定 (1:1) |
| 6 | NC (面板描述 INT 2) | **5** | 确定 (1:1) — 同上, 重力传感器中断 2 |
| 7 | GND | **6** | 确定 (1:1) |
| 8 | MIPI_0N | **7** | 确定 (1:1) |
| 9 | MIPI_0P | **8** | 确定 (1:1) |
| 10 | GND | **9** | 确定 (1:1) |
| 11 | MIPI_1N | **10** | 确定 (1:1) |
| 12 | MIPI_1P | **11** | 确定 (1:1) |
| 13 | GND | **12** | 确定 (1:1) |
| 14 | MIPI_CKN | **13** | 确定 (1:1) |
| 15 | MIPI_CKP | **14** | 确定 (1:1) |
| 16 | GND | **15** | 确定 (1:1) |
| 17 | MIPI_2N | **16** | 确定 (1:1) |
| 18 | MIPI_2P | **17** | 确定 (1:1) |
| 19 | GND | **18** | 确定 (1:1) |
| 20 | MIPI_3N | **19** | 确定 (1:1) |
| 21 | MIPI_3P | **20** | 确定 (1:1) |
| 22 | GND | **21** | 确定 (1:1) |
| 23 | GND | **22** | 确定 (1:1) |
| 24 | TP_RESET | **23** | 确定 (1:1) |
| 25 | TP_VCC | **24** | 确定 (1:1) |
| 26 | TP_INT | **25** | 确定 (1:1) |
| 27 | TP_SDA | **26** | 确定 (1:1) |
| 28 | TP_SCL | **27** | 确定 (1:1) |
| 29 | GND | **28** | 确定 (1:1) |
| 30 | GND | **29** | 确定 (1:1) |
| 31 | VDD 3.3V | **30** | 确定 (1:1) |
| 32 | VDD 3.3V | **31** | 确定 (1:1) |
| 33 | GND | **32** | 确定 (1:1) |
| 34 | GND | **33** | 确定 (1:1) |
| 35 | LED- (阴极) | **34** | 确定 (1:1) |
| 36 | LED- (阴极) | **35** | 确定 (1:1) — ★**两根阴极, 不合并, 板上自己并** |
| 37 | NC | **36** | 确定 (1:1, 仍是空脚) |
| 38 | NC | **37** | 确定 (1:1, 仍是空脚) |
| 39 | LED+ (阳极) | **38** | 确定 (1:1) |
| 40 | LED+ (阳极) | **39** | 确定 (1:1) — ★**两根阳极, 不合并, 板上自己并** |

★ **"省掉的就是屏侧第 1 脚" —— 三条独立证据**:
1. **位差唯一解**: 屏侧 2~40 与主板侧 1~39 **逐针信号全对得上** (VDD↔VDD3V3, VCCIO↔IOVCC1V8-3V3, Reset↔RESET, 4 对 MIPI 差分对, 5 个触控脚, LED−×2, LED+×2 全部一一对上), 且**整体偏移恒为 −1**; 若省的是别的 NC, 必然在某处错位, 但 40 针里 5 个 NC (1/4/6/37/38) 无论去掉哪个都会破坏对齐 ⇒ **唯一解 = 去掉第 1 脚**。来源: [S1][S5] 对齐, [S4] 原理图实物核对。
2. **原厂板级针位表**: ROCK 5C 官方 39 针表 [S1] 与 ROCK 4D 官方 SBC 侧表 [S11] (第 1~39 位) **同样从 VDD3V3/LCD_3V3 起排**, 与面板表的前 39 脚 (即面板 2~40) 一一对齐 —— 两块不同的 Radxa 板 + 一块 Dragon 板, **三个原厂来源同构**。
3. **★背光脚数自洽**: 面板侧 LED− 有 **2 只** (35/36)、LED+ 有 **2 只** (39/40); 主板侧也各有 **2 只** (34/35 与 38/39) ⇒ **没有发生"并脚"**; 面板侧 2 个 NC (37/38) 在主板侧原样保留为 2 个空脚 (36/37) ⇒ **40→39 的 −1 只能来自头部第 1 脚**。

★ **顺便裁定一个历史矛盾 (35/36/39/40)**: ★**屏侧 35 = LED−, 36 = LED−, 39 = LED+, 40 = LED+ (官方 Pinout 原文)** —— 与 [S5] 屏侧官方表、[S1] 主板侧 39 针表 (34/35 = 阴极, 38/39 = 阳极)、[S4] Q6A 原理图 (VCC_LEDK 同时接 34+35, VCC_LEDA 同时接 38+39) **三处一致**。⇒ ★**背光是 1 串、该串 2 颗并联**; ★**LED− 与 LED+ 是两套独立回路, 严禁互短** (本项目 `HW/STEP1_PARTS_SPEC.md` 已按此订正)。

---

## 4. ★ 背光 (8HD 自己的背光规格)

| 项 | 值 | 状态 / 出处 |
|---|---|---|
| 背光类型 | **白色 LED** | [S5] 官方 LCD 特征表: "Backlight: White LED" |
| 亮度 | 300 (typ) cd/m² | [S5] "Luminance (cd/㎡): 300 type" |
| **背光 LED 电压 (typ/max)** | ★**未查到** | 8HD 官方文档页只给 "Backlight: White LED" / 亮度, **无电压/电流/串数**; 试过的 URL 见 §8 |
| **背光 LED 电流 (typ/max)** | ★**未查到** | 同上 |
| **串数 (几串 / 每串几颗)** | ★**结构性可定: 1 串, 每串 2 颗并联** (面板侧 2 阴极 + 2 阳极; 主板侧同构) | [S5] 屏侧 35/36 = LED−, 39/40 = LED+; [S1] 主板侧 34/35, 38/39; [S4] Q6A 原理图 p.29: 34+35 同接 `VCC_LEDK`, 38+39 同接 `VCC_LEDA` ⇒ **2 颗并联成一串** |
| ★**参考: 同族 10FHD 的背光电参数 (可作量级参考, 不是 8HD 的值)** | LED 电流 180 (typ) / 200 (max) mA; LED 电压 12 (min) / **12.8 (typ)** / **14 (max)** V @ I=180mA; 亮度 300 (typ) / 350 (max) cd/m² | [S12] Radxa Display 10 FHD 官方"背光物理参数"表 —— ★**注意: 这是 10 寸 FHD 的值, 不能当成 8HD 的值用** |
| ★**Radxa 怎么驱动这块背光的 (可抄的参考设计)** | ★**Dragon Q6A 用 U43 = SY7203DBC (BOOST LED 驱动)**: 输入 `VCC_5V_PERI` → L48 4.7µH/2A → 输出 `VCC_LEDA` (阳极) / `VCC_LEDK` (阴极, 经 R315 = 1.1Ω 采样限流); EN = `EDP_BLPWM` (SoC PWM 调光); FB 分压 R314 = 100K 1% | [S4] p.29 原理图 (LCD_MIPI_EDP 页) — ⇒ **说明 8HD 的 LED 轨压必然高于 5V (必须 BOOST), 且背光调光走 PWM (不是 I2C)** |

★ **对项目电源树的直接影响 (ISS-173 关联)**: 我们自己的面板若同样要 ~12.8V/200mA, ★**Q6A 的做法可直接抄**: BOOST (SY7203DBC 类) + 采样电阻限流 + PWM 调光; ★**但 8HD 自己的 LED 轨压/电流官方未公布 ⇒ 本条标 [推断, 待核]**, 落板前须实测屏背光 (量 LED+ 与 LED- 之间的电压与电流), 或向 Radxa 索取 8HD 背光规格。

---

## 5. ★ 15p / 1.0mm 那一版到底带什么 (结论)

| 项 | 结论 | 出处 |
|---|---|---|
| 线材形态 | ★**15-pin 1.0mm pitch (Motherboard side) to 40-pin 0.5mm pitch (Display side)** —— 板端是 15p/1.0mm, 与 RPi 生态 (RPi 4B 的 15 位 DSI 座) 同制式 | [S7] Radxa 官方产品页原文 |
| 适用板 | ROCK **3A / 3C / 4SE** + **Raspberry Pi 4B** (走 39p 线的是 4C+ / 5A / 5B) | [S8] 官方使用教程表; [S9] 官方 GitHub 仓库 README |
| ★**带哪些信号** | ★**DSI + 触控 I2C 在 15p FPC 上; 但背光 PWM、触控 RST、触控 INT、重力传感器 INT 全部甩到"额外 7 针排针"上** | [S8] "15 pin 转 40 pin 的 FPC 排线有需要额外连接的 7 pin 排针"; [S10] AC012 官方分线图 (40 端分出: `GSENSOR-INT` / `LCD-RESET` / `TP-INT` / `TP-RST` / `BL-PWM` / `GND` / `VCC 5V`) |
| 7 针排针的官方接线 | ROCK 3A/3C/4SE: `VCC_5V`←+5V, `GND`←GND, `PWM`←PWM(GPIO), `TP-RST`←GPIO, `YP-INT`←GPIO, `LCD-RST`←+3.3V, `GINT`←不接; RPi 4B: `VCC-5V`←PIN2, `GND`←PIN6, `BL-PWM`←PIN1(3V3, ★即常亮), `TP-RST`←GPIO17, `TP-INT`←GPIO4, `LCD-RESET`←PIN17(3V3), 第 7 脚未用 | [S8][S9] |
| ★**背光结论** | ★**15p 版拿不到背光 PWM/背光供电控制** —— RPi 官方文档自己写着 "The backlight brightness of the current version is not adjustable" (亮度不可调) | [S9] 官方 README "Known Issues" |
| ★**DSI lane 数** | 8HD 官方产品页: **"requires 2-lane or 4-lane MIPI DSI signal support"**; RPi 4B 本身只有 2-lane ⇒ 15p 方案实际跑 **2-lane** | [S7][S9] |
| ★**15p 侧逐脚表** | ★**未查到** (Radxa 未公开 AC012 的 15 端针位图; 官方图只画 40 端分线) | §8 |
| ★**结论 (回答老板的推论)** | ★**boss 的算术成立**: 15 个位置塞不下「4-lane DSI(10) + 触控 I2C(2) + TP_RST(1) + TP_INT(1) + 电源/地」再留背光 ⇒ ★**15p 版 = 精简版 (背光 + 触控 RST/INT 外置)** ⇒ ★**我们要 4-lane DSI + 触控 + 背光一体化 ⇒ 必须走 39p 版 (或自己排线), 15p 版不可用** |

---

## 6. ★ 两种板端方案对比

| 方案 | 板端连接器 | 排线 | 触控 | 背光 | 4-lane DSI | 我们的代价 |
|---|---|---|---|---|---|---|
| **A 走原厂 39p 线** | ★**39p / 0.3mm, HIROSE FH35C-39S-0.3SHW(50)**, SMD 直角, flip-lock + bottom contact (FH35C 系列本体 = 背夹式 + 上下双面触点) — [S1][S2] | ★**原厂随屏线 FPC AC013 / AC013N** (39P 0.3mm ↔ 40P 0.5mm, Opposite Side, Plug-and-Play) — [S13][S14] | ★**有** (23 TP-RESET / 24 TP-VCC / 25 TP-INT / 26 TP-SDA / 27 TP-SCL) — [S1][S4] | ★**有** (34 LED-1 / 35 LED- / 38 LED+1 / 39 LED+; 板上 34+35 并一路阴极, 38+39 并一路阳极) — [S1][S4] | ★**能** (4-lane: 7/8, 10/11, 16/17, 19/20 + 时钟 13/14) — [S1][S4] | ★**选型即抄**: 座型号已由原厂公布 ⇒ footprint 在项目已有的 FH35C-31S 基础上改针数 (31→39) 即可, 但**须回 HIROSE 取 FH35C-39S 原厂尺寸表逐项核对** (本单未取); ★**须自备 BOOST 背光驱动** (8HD 轨压 > 5V, 官方未公布确切值 ⇒ 标待核) |
| **B 走 15p RPi 线** | ★**15p / 1.0mm (板端)** — [S7] | 原厂/市面 **15P↔40P** 线 (AC012), ★**必须再外接 7 针排针** (GSENSOR-INT / LCD-RESET / TP-INT / TP-RST / BL-PWM / GND / VCC 5V) — [S8][S9][S10] | ★**部分**: I2C (SDA/SCL) 在 15p 上, 但 **TP-RST / TP-INT 要外接排针** — [S8][S10] | ★**不带 (背光 PWM 与 VCC5V 走外接 7 针)**; 官方文档自述亮度不可调 — [S9][S10] | ★**不能 (15 位塞不下 4-lane + 触控 + 背光)**; RPi 4B 实测只跑 **2-lane** — [S7][S9] | ★**最差**: 要额外排线/飞线接 7 针 (TP_RST/TP_INT/BL_PWM/LCD_RST/VCC5V/GND/GINT), 背光还要另做驱动, DSI 只能 2-lane ⇒ ★**不建议** |

★ **推荐: 方案 A**。理由: 座型号/针序全部有原厂依据 (§2), 一根线同时带齐 4-lane DSI + 触控 + 背光, 且**不需要任何自制转接板**。

---

## 7. ★ 怎么用 (给画板/画座的人)

1. ★**我们主板要画的座 = 39 位 / 0.3mm FPC 座**, 型号 **HIROSE FH35C-39S-0.3SHW(50)** [S1]; 形态 SMD 直角、flip-lock、下接触 [S2]; FH35C 系列本体为背夹式 + 上下双面触点 ⇒ **footprint 可由项目已有的 `CONN_CAM` (FH35C-31S-0.3SHW(50)) footprint 改针数得到, 但必须回 HIROSE 取 FH35C-39S 原厂 land pattern 复核** (项目 `HW/PCB/PINOUT_FOOTPRINT_SPEC.md` §10 记录了 31 位版的原厂依据)。
2. ★**针序照抄 §2 表**; ⚠️ **最易踩的坑: 不要拿屏侧 40p 表的脚号直接画座** —— 屏侧第 1 脚 (NC) 在 39p 侧不存在, **屏侧脚号 = 主板侧脚号 + 1**。
3. ★**电气分组** (可直接抄进原理图):
   - **4-lane DSI 差分对**: (7,8) (10,11) (16,17) (19,20) + 差分时钟 (13,14) ⇒ SoC DSI TX, 4 lane 可用。
   - **触控 I2C**: 26 = TP-SDA, 27 = TP-SCL (3.3V 域, 上拉 ≤3.3V 合法) + 23 = TP-RESET (低有效 GPIO) + 25 = TP-INT (GPIO 输入) + 24 = TP-VCC (3.3V 供电, ★**触控要单独给 3.3V**)。
   - **屏供电**: 1 = 3.3V, 30 = 3.3V, 31 = 3.3V (三处 3.3V, 面板侧是 VDD×3) + 2 = IO 供电 (1.8V 或 3.3V, 按面板 VCCIO 要求定) + 29/33 等 GND。
   - **背光**: 34+35 = 阴极 (板上并成一路) / 38+39 = 阳极 (板上并成一路) ⇒ ★**BOOST 输出两条轨** (阳极轨接 38+39, 阴极回流经采样电阻接 34+35), PWM 调光 (照 Q6A: `EDP_BLPWM` → BOOST EN) [S4]。
   - **重力传感器 (可选)**: 3 = INT1, 5 = INT2 —— 面板侧确实有这两个脚 [S5], 8HD 内置重力传感器可用于自动旋转; ★**ROCK 5C 未引出, Q6A 引出但未接** ⇒ 我们可自行接 GPIO (是否需要取决于是否做自动旋转功能)。
4. ★**背光电气参数留口**: 8HD 官方未公布 LED 电压/电流 (§4) ⇒ ★**主板先把 BOOST + 采样电阻按最坏情况 (12.8V/200mA, 参考 10FHD 同族量级) 留位, 并在丝印/测试点留 LED+ / LED− 实测点**, 屏到货后实测再定采样阻值 (标 [推断, 待核])。
5. ★**排线**: 买原厂 **FPC AC013 或 AC013N** (39P 0.3mm ↔ 40P 0.5mm) 直接插我们新做的 39p 座; ★**不要买 15p 线** (见 §5/§6)。
6. ★**原始资料留存**: 原厂 39p 逐脚表原文在 [S1] (ROCK 5C 接口页), 原厂板级原理图在 [S4] (Dragon Q6A 原理图 V1.21 PDF 第 29 页 / sheet 31 of 37)。

---

## 8. ★「未查到」清单 + 试过的 URL / 失败原因

| 想查的东西 | 状态 | 试过的 URL / 失败原因 |
|---|---|---|
| **8HD 自己的背光 LED 电压 (typ/max)、电流 (typ/max)、串数** | ★**未查到** (官方只有 "Backlight: White LED" + 300 cd/m²; **串数是结构性推出来的, 不是官方数值**) | ① `https://docs.radxa.com/en/accessories/display/lcd-8-hd/lcd-8-hd-product` → LCD 特征表无背光电参数 (只有 Backlight: White LED / Luminance 300 cd/m²) ② `https://docs.radxa.com/zh-cn/accessories/display/lcd-8-hd/lcd-8-hd-product` → 同上 ③ `https://www.radxa.com/products/accessories/display-8hd` → 静态 HTML 里无 Tech Spec 表 (Docusaurus 客户端渲染, 未取到表格内容) ④ `https://docs.radxa.com/img/accessories/display/display-8hd-spec.webp` → **404** ⑤ `https://radxa.com/img/accessories/display/display-8hd-spec.webp` → **404** ⑥ `https://dl.radxa.com/dragon/q6a/hw/datasheets/` → 目录里只有 `80-23889-1_REV_AW_QCS6490_and_QCS5430_Data_Sheet.pdf` (SoC), 无背光/屏料号 ⑦ `https://docs.radxa.com/en/accessories/display/lcd-10-fhd/lcd-10-fhd-product` → 10FHD **有**背光物理参数表, 8HD **没有** (对比确认不是我漏抄) |
| **Radxa 是否公开 39p/0.3mm 转接线 (AC013) 本身的图纸/针位表** | ★**未公开** | ① `https://docs.radxa.com/img/accessories/display/ac013-pin-definition.webp` → **404** (对照: 15p 版的 `.../ac012-pin-definition.webp` → **200, 存在**) ⇒ ★**Radxa 只公开了 15p 版的分线定义图, 39p 版没有** ② `https://www.radxa.com/products/accessories/fpc-adapter-cable-ac013` → 页面无针位表, 无可下载图纸链接 (Docusaurus 静态页里 Downloads 区块无 PDF/zip 链接) ③ `https://dl.radxa.com/dragon/q6a/hw/datasheets/` → 无连接器/线缆资料 |
| **Q6A 原理图里 J10 的连接器料号** | ★**未查到** (原理图只写位号 `J10` + 符号名 `LCD_39P`, 无器件型号) | ① `https://dl.radxa.com/dragon/q6a/hw/radxa_dragon_q6a_schematic_v1.21.pdf` → grep 仅 `J10` / `LCD_39P` ② `https://dl.radxa.com/dragon/q6a/hw/radxa_dragon_q6a_components_placement_map_v1.21.pdf` → 只是贴装位置图, 无型号表 ③ `https://dl.radxa.com/dragon/q6a/hw/radxa_dragon_q6a_3d_stp_v1.21.zip` → ★**多次下载被截断 (本地只拿到 2.5/4.3MB), 未能取出 3D 实体名** ⇒ 型号改由 [S1] ROCK 5C 页 + 针名逐针一致性给出 (标 [推断, 高置信]) |
| **15p 侧 (板端) 逐脚表** | ★**未查到** | ① `https://docs.radxa.com/img/accessories/display/ac012-pin-definition.webp` → 图上**只画 40 端分出的 7 根线**, 无 15 端针位 ② `https://docs.radxa.com/en/accessories/display/lcd-8-hd/lcd-8-hd-usage` → 只给 7 针排针接线表, 无 15 端针位 ③ `https://github.com/radxa/radxa-displays-on-raspberry-pi` (官方仓库) → README 只有接线表 |
| **FH35C-39S-0.3SHW(50) 的原厂 land pattern / 尺寸图** | ★**本单未取** (本文件只给型号与形态; footprint 数值须回 HIROSE 取) | `https://www.hirose.com/en/product/series/FH35C/documents` (系列页) —— 项目已在 `HW/PCB/PINOUT_FOOTPRINT_SPEC.md` §10 留了 FH35C-31S 的取法, 39 位版照此办理 |

---

## 9. ★ 出处索引 (全部为 Radxa 原厂资料)

| ID | 来源 | 链接 | 取用位置 |
|---|---|---|---|
| **S1** | ★**ROCK 5C 官方硬件接口页 —— 39p 逐脚表 + 连接器型号** | <https://docs.radxa.com/en/rock5/rock5c/hardware-design/hardware-interface> | §MIPI DSI: "MIPI screen support. Utilizes a 39-pin, 0.3 mm pitch, gold-plated connector, model FH35C-39S-0.3SHW(50)" + 39 行 Pin/Name/Voltage 表 |
| **S2** | ROCK 5A 官方硬件接口页 —— 连接器形态/触点 | <https://docs.radxa.com/en/rock5/rock5a/hardware-design/hardware-interface> | §MIPI DSI: "Connector type: 39-pin, 0.3 mm pitch, SMD right-angle FPC connector" / "Connection: flip-lock, bottom contact" |
| **S3** | ★Dragon Q6A 官方 MIPI DSI 页 | <https://docs.radxa.com/en/dragon/q6a/hardware-use/mipi-dsi> | "39-Pin / 0.3mm pitch FPC 接口"; "接口引脚定义 → 参考资源汇总下载页的硬件原理图" |
| **S4** | ★**Dragon Q6A 原厂硬件原理图 PDF V1.21 (35 页)** | <https://dl.radxa.com/dragon/q6a/hw/radxa_dragon_q6a_schematic_v1.21.pdf> | **PDF 第 29 页 = 图纸 sheet 31 of 37 (LCD_MIPI_EDP)**: 连接器 **J10 / LCD_39P** 的 39 针符号 + 网络名 (R312 0R→IOVCC, R313 0R→DISP0_RESET_N, `VCC_LEDK`→34/35, `VCC_LEDA`→38/39, `EDP_BLPWM`→U43 SY7203DBC 背光 BOOST, L48 4.7µH, R315 1.1Ω, R314 100K) |
| **S5** | ★**Radxa Display 8 HD 官方产品页 (文档站)** —— 屏侧 40p 表 | <https://docs.radxa.com/en/accessories/display/lcd-8-hd/lcd-8-hd-product> (中文版 <https://docs.radxa.com/zh-cn/accessories/display/lcd-8-hd/lcd-8-hd-product>) | §Pinout 表 1~40 (含 4 = "NC / INT 1", 6 = "NC / INT 2", 35/36 = LED-, 39/40 = LED+); §LCD 特征表 (Backlight: White LED) |
| **S6** | Radxa Display 8 HD 官方文档站 —— 使用教程 | <https://docs.radxa.com/en/accessories/display/lcd-8-hd/lcd-8-hd-usage> | §适配产品/线材种类表 (39p→40p / 15p→40p); §7 针排针接线表 (3A/3C/4SE/RPi) |
| **S7** | ★**Radxa Display 8 HD 官方产品页 (radxa.com)** —— FPC 规格 | <https://www.radxa.com/products/accessories/display-8hd> | "FPC Cable Specification: 39-pin 0.3mm pitch (Motherboard side) to 40-pin 0.5mm pitch (Display side)"; "15-pin 1.0mm pitch (Motherboard side) to 40-pin 0.5mm pitch (Display side)"; "requires 2-lane or 4-lane MIPI DSI signal support"; "One Cable for Power, Touch, Rotation Detection and Display" |
| **S8** | Radxa 官方文档站 —— 8HD 使用教程 (中/英) | <https://docs.radxa.com/en/accessories/display/lcd-8-hd/lcd-8-hd-usage> | §"15 pin 转 40 pin 的 FPC 排线有需要额外连接的 7 pin 排针" + 各 SBC / RPi 接线表 |
| **S9** | ★Radxa 官方 GitHub 仓库 (radxa-displays-on-raspberry-pi) | <https://github.com/radxa/radxa-displays-on-raspberry-pi> | README: 15→40 排线 + 7 针排针接线表 (VCC-5V/GND/BL-PWM/TP-RST/TP-INT/LCD-RESET); "The backlight brightness of the current version is not adjustable" |
| **S10** | ★Radxa 官方 AC012 分线定义图 (图) | <https://docs.radxa.com/img/accessories/display/ac012-pin-definition.webp> | 图上 40 端分出 7 根: `GSENSOR-INT` / `LCD-RESET` / `TP-INT` / `TP-RST` / `BL-PWM` / `GND` / `VCC 5V` (标注 "RSPI_TO_MIPI_V1.1") |
| **S11** | ROCK 4D 官方 MIPI DSI 页 —— SBC 侧针位表 (交叉验证) | <https://docs.radxa.com/en/rock4/rock4d/hardware-use/mipi-dsi> | §Interface Specifications: 第 1~39 位与 [S1] 逐针同构 (1 LCD_3V3 / 2 LCD_3V3/VCC_1V8_S0 / 3 NC / 4 LCD_RESET_1 / 5 NC / 6 GND / 7 D0N … 34-35 VCC_LEDK2 / 36-37 NC / 38-39 VCC_LEDA2) + "39-pin 0.3mm SBC to 40-pin 0.5mm Display" 线材说明 |
| **S12** | Radxa Display 10 FHD 官方产品页 —— 背光物理参数表 (仅作同族量级参考) | <https://docs.radxa.com/en/accessories/display/lcd-10-fhd/lcd-10-fhd-product> | §背光物理参数表: LED 电流 180/200 mA, LED 电压 12/12.8/14 V @180mA; §信号定义表 (4 = INT1, 6 = INT2) |
| **S13** | Radxa 官方 FPC AC013 产品页 | <https://www.radxa.com/products/accessories/fpc-adapter-cable-ac013> | "39P 0.3mm to 40P 0.5mm, Opposite Side FPC Cable"; "Plug-and-Play"; "For Radxa Display 8 HD and Display 10 FHD" |
| **S14** | Radxa 官方 FPC AC013N 产品页 | <https://www.radxa.com/products/accessories/fpc-adapter-cable-ac013n> | 同 AC013 规格 (另一版本号) |
| **S15** | Radxa 官方资源下载页 (Q6A 原理图出处) | <https://docs.radxa.com/en/dragon/q6a/download> | 列出 `radxa_dragon_q6a_schematic_v1.21.pdf` 等硬件资源 (S4 的官方出处) |

★ **本文件所有脚位均无推测成分**: 39 针逐针表由 **[S1] 原厂公开针位表** 与 **[S4] 原厂原理图符号/网络** 双向锁定, 并由 **[S5] 屏侧 40p 表** 与 **[S11] 另一块板的 SBC 侧表** 交叉验证; 唯二属推断的条目已就地标注为 **[推断, 待核] / [推断, 高置信]** (背光电参数 [待核]; Q6A 连接器型号 [高置信])。

---

## 10. 变更记录

| 日期 | 内容 |
|---|---|
| 2026-11-03 | 首版: 39p/0.3mm 主板侧针位表闭环 (原厂三方互证) + 40→39 对应表 (省掉屏侧第 1 脚) + 连接器型号 (FH35C-39S-0.3SHW(50)) + 背光结构性结论 + 15p 版结论 + 两方案对比 |
