# TP_INT 改脚规格 —— ISS-174 闭环件 (原理图变更规格 + SoM 侧候选脚清单)

| 项 | 值 |
|---|---|
| 文件 | `HW/PCB/TP_INT_REMAP_SPEC.md` |
| 日期 | 2026-11-15 |
| 作者 | hw-lead (硬件总工) |
| 对应 issue | ISS-174 (「demo 触控收不到中断」) |
| 门禁 | `python3 HW/check_tp_int_gap.py` (rc=0 = 现状与本规格一致) · `--selftest` 5/5 |
| ★**本单性质** | ★**只出规格与证据** ⇒ **不改网表 / 不改板 / 不改原理图文件** (落笔留给 main 在原理图定稿那一轮一次性改) |
| ★**零外发** | 本单**没有**任何邮件 / 询价 / 采购 / 原厂问询 ⇒ 缺口一律自己查 + 标证据等级 + 写降级方案 |

---

## 0. 结论先行 (一句话)

★**ISS-174 的前提已经过期** —— 现行屏座 `CONN_LIGHT` (22p) **根本没有触控中断脚**, `NET_TP_INT` 在网表里**根本不存在** ⇒ **本板不需要接 TP_INT**; **但 SoM 侧必须现在就把"将来接"的那只脚定下来** ⇒ **主选 `J_SOM_P4 pin62` (GPIO2_D7_z, ball B7)** ⇒ **代价 0** (焊盘已在板上 · BOM 不变 · 本板一行网表都不改)。

---

## 1. 判真伪 —— 判定 **(c) 部分成立**

### 1.0 判定表

| 分项 | 判定 | 依据 |
|---|---|---|
| **① `NET_TP_INT` 存不存在** | ★**不存在** (不是"没接 SoM", 是"这条线压根没画") | `grep -n "TP_INT" HW/netlist_v1.csv` ⇒ **0 命中**; `HW/netlist_v1_pins.csv` ⇒ **0 命中**; 全库大小写不敏感搜 `tp_int` ⇒ **0 命中** |
| **② 触控归谁管** | ★**归屏内 MCU / 屏内触控控制器, 走 I2C_B ⇒ SoM 侧不需要 TP_INT** | `HW/netlist_v1.csv:248/249` (I2C_B_SCL/SDA → CONN_LIGHT pin11/12, 屏内 MCU @0x45); `HW/PCB/WAVESHARE_2P8_INIT_AND_BACKLIGHT.md:262` (官方规格 **Touch Port I2C**)、`:414`、`:430` (Pi5 官方 overlay `vc4-kms-dsi-waveshare-panel.dtbo` 内 `panel_disp1@45` + 触摸 GT911 @0x14) |
| **③ `TP_RESET` 现行是什么** | ★**是「测试点位号」, 挂在 `RESET_N` (SoM 自身复位链) 上 —— 与屏完全无关** | `HW/netlist_v1.csv:366` (`P7,RESET_N,TP_RESET,R_PU_RESET_N,TP_RESET,测试点,...`) · `HW/netlist_v1_pins.csv:489` (`TP_RESET.1,RESET_N,...`) |
| **总判定** | ★**(c) 部分成立** —— issue 的**主体断言 (三条) 全部不成立**; **只有前瞻残项 R1 成立** (见 §1.4/§1.5) |

### 1.1 判定① —— `NET_TP_INT` 到底存不存在

```
$ grep -n "TP_INT" HW/netlist_v1.csv
(rc=1, 0 命中)
$ grep -n -i "tp_int" HW/netlist_v1.csv HW/netlist_v1_pins.csv
(rc=1, 0 命中)
$ grep -n "TP_INT\|TP_RESET" HW/PCB/demo_mainboard.kicad_pcb
11964:		(property "Reference" "TP_RESET"      ← ★这是「测试点封装位号」, 不是网名
```

⇒ **不是"改了名", 是这条线在现行网表里从头到尾就没画过。**
`netlist_v1.csv` 全表 514 行 / `netlist_v1_pins.csv` 全表 585 行, `TP_INT` / `NET_TP_INT` 零命中。
★唯一的 `INT_` 网名是 `INT_CHG` (`HW/netlist_v1.csv:487`) —— 充电板 BQ25896 的开漏中断, **与触控无关**。

### 1.2 判定② —— 触控功能在现行架构里归谁管

**结论: 归屏内 MCU / 屏内触控控制器, 走 I2C_B; SoM 侧不需要 TP_INT。**

| 证据 | 出处 | 等级 |
|---|---|---|
| 屏座 pin11/12 = `SCL0`/`SDA0` ⇒ **屏控制 I2C** (屏内 MCU @0x45), **不是触控中断线** | `HW/netlist_v1.csv:248-249` (`[CONN_LIGHT] Pi5 DISPLAY 座 pin11 = SCL0 ⇒ 屏控制 I2C`); `HW/netlist_v1_pins.csv:38-39` | [官网] |
| ★屏模组内 MCU I2C 地址 **0x45**, 出处 = **Raspberry Pi 官方 firmware overlay `vc4-kms-dsi-waveshare-panel.dtbo` 内 `panel_disp1@45`** | `HW/netlist_v1.csv:248` note; `HW/I2C_ADDR_TABLE.md:56` + 证据表 `[S5]`/`[R2]` | [官网] |
| ★屏的**触控端口就是 I2C** (官方规格: *Touch Type Capacitive / Touch Points 5-Points / **Touch Port I2C***) ⇒ 触控数据不走出座 | `HW/PCB/WAVESHARE_2P8_INIT_AND_BACKLIGHT.md:262` (Waveshare 官方 wiki「2.8inch DSI LCD」Interface Definition) | [官网] |
| 触摸 GT911 @0x14 **在同一根 I2C 上**, demo 不接 | `HW/PCB/WAVESHARE_2P8_INIT_AND_BACKLIGHT.md:414`、`:430`; `HW/I2C_ADDR_TABLE.md:56` note | [官网] |
| 网表注释**明写 "I2C_B 不是触控线"** | `HW/netlist_v1.csv:231-236` / `HW/netlist_v1_pins.csv` 对应 note | [推算] (项目自记) |
| ★**屏座 22 脚里没有任何触控/复位脚** (全表见 §2) | `HW/netlist_v1_pins.csv:36-57` | [实测] (本机 grep) |

⇒ **触控中断由屏内 MCU 处理, SoM 侧根本不需要 TP_INT** ⇒ 本板 **无缺口**。

### 1.3 判定③ —— `TP_RESET` 现行到底是什么

★**它是一个「测试点位号」, 不是网名; 它挂在 `RESET_N` (SoM 自身复位链) 上, 和屏没有任何关系。**

| 项 | 现行事实 | 行号 |
|---|---|---|
| 网名 | `RESET_N` (**不是** `TP_RESET` / `NET_TP_RESET`) | `HW/netlist_v1.csv:366` · `HW/netlist_v1_pins.csv:489` |
| 位号 | `TP_RESET` (P7 测试点, Value = 测试点) | `HW/netlist_v1.csv:366` · `HW/netlist_v1_pins.csv:489` |
| 属于哪条链 | **SoM 复位链**: `R_PU_RESET_N` 10k 上拉 (到 `RAIL_VDD_1V8_IO`) + `R_SER_RESET_N` 1k + `C_RST` 100nF + `SW_RST` 按键 + `Q_AND` 硬件 AND (DNP) + `U_SUPV` 监督器 (DNP) ⇒ 末级经 `R_SER_RESET_N` 到 `J_SOM_P2 pin100` (= SoM `RESET_L`) | `HW/netlist_v1.csv:65/66/377/378/379/380/382/409` |
| ★结论 | ★**"TP_RESET 是屏复位线"这个前提不成立** ⇒ **不是"接了屏没接 SoM", 是"这条线现在压根不是屏复位线"** | — |

### 1.4 把 issue 原描述逐条拆开

ISS-174 (raised 2026-11-03 19:1x) 原描述有 4 条断言:

| # | 原断言 | 现行判定 | 行号级证据 |
|---|---|---|---|
| A | "当前网表里 `NET_TP_INT` **只连到屏模组一个节点**, 没接任何 SoM 脚" | ★**不成立** —— 该网**不存在** | `grep -n "TP_INT" HW/netlist_v1.csv` ⇒ 0 命中 (§1.1) |
| B | "**pin26 = TP_INT** 是触控的中断输出 (低有效)" | ★**对**已作废的 **Radxa Display 8HD 板侧 39p/0.3mm FPC** 成立; ★**对现行 22p 座不成立** (22 座无此脚) | 8HD 侧: `HW/PCB/DISPLAY_39P_PINOUT.md:71/73/123/125` (39p pin24=TP_RESET / pin26=TP_INT) · ★**该表已整表作废**: `HW/PCB/FPC_PIN_TABLES.md` 末段「★**已作废**: 2026-11-03 之前这里是「Radxa Display 8HD 板侧 39p/0.3mm」表 —— demo 屏已换 Waveshare 2.8inch ⇒ **整表作废**」; 现行 22 座全表见 §2 |
| C | "处置: 从 SoM 的 GPIO 池里再分一个脚给它" | ★**本板无信号可接** ⇒ 降级为**「前瞻预选 + 占位」** | §2 (22 脚全占用) + §3 (候选表) |
| D | note: "`NET_TP_RESET` (pin24) 也只连到屏模组一侧 ⇒ 触控复位没人拉" | ★**不成立** —— `TP_RESET` 是 SoM 复位链的测试点位号, `NET_TP_RESET` 不存在 | §1.3 |

⇒ **根因**: issue 是在 **2026-11-03 换屏之前** (屏 = Radxa 8HD 39p) 提的; **2026-11-04 demo 屏换成 Waveshare 2.8inch 22p 后整表作废**, 但 **issue 没跟着清** ⇒ **这正是「老 issue 描述漂移」的典型样本** (本单的机械防线 = `HW/check_tp_int_gap.py`)。

### 1.5 ★仍然成立的前瞻残项 R1 (本单真正要关的东西)

**R1: SoM 侧目前**没有**为"带独立触控中断脚的屏"预留任何 GPIO。**

- 光机 (屏模组) 选型 **ISS-156 仍 open**; **ISS-158** 已把 P2 屏模组定为 **Radxa Display 8HD/10FHD 40p/0.5mm** (`state/issue_log.yaml` ISS-158 note: "P2 = **Radxa Display 8HD/10FHD 40p/0.5mm, 逐针表 40/40**") ⇒ ★**那块屏的 pin26 确实是 TP_INT、pin24 确实是 TP_RESET** (`HW/PCB/DISPLAY_39P_PINOUT.md:71/73`) ⇒ **换屏时这个需求会真的回来**。
- ⇒ **正确的动作不是"改脚", 而是"现在就把 SoM 侧那只脚钉死"** —— 因为 SoM 球位座 (`J_SOM_P1..P4`) 已在板上, **占一个空焊盘代价 = 0**; 等屏选型定了再动, 就要连带改 SoM 球位/网表/板/整链重出。
- ⇒ **本单 §3 的候选表 + §4 的规格, 就是 R1 的关闭件。**

### 1.6 ★这条 issue 应当改成什么 (建议 main 落账用的措辞)

> **ISS-174 建议改写为**: 「**SoM 侧预留给『带独立触控中断脚的屏』的 GPIO** (前置选型占位) —— 当前 demo 屏 = **Waveshare 2.8inch 22p** (`CONN_LIGHT`), 官方规格 **Touch Port = I2C**, 触控由屏内 MCU @0x45 处理 ⇒ **本板无触控中断缺口, 不接 TP_INT**。但 ISS-156/ISS-158 的 P2 屏模组候选 (Radxa 8HD/10FHD 40p) 带 **pin26=TP_INT / pin24=TP_RESET** ⇒ 需**现在**预选一个 SoM 侧 3.3V GPIO 并占位 ⇒ **主选 `J_SOM_P4 pin62` (GPIO2_D7_z, ball B7, 官方默认 ETH0_RXCLK)**, 备选 P4_60/58/56/54/52 ⇒ **BOM 不变 / 本板网表 0 改动 / 焊盘已在板上**。」

---

## 2. `CONN_LIGHT` 22 脚在网表里的落点全表 (★唯一答案: 触控不在这个座上)

来源: `HW/netlist_v1_pins.csv` 第 36..57 行 (每脚一行) · `HW/netlist_v1.csv` 对应行 · Pi5 官方 J4 脚名来自 `HW/PCB/PI5_DSI_22P_PINOUT.md` §2 (证据 P1 = Raspberry Pi 官方 Pi 5 原理图)。

| pin | Pi5 官方 J4 脚名 | 屏侧 15p | 网表网名 | `netlist_v1_pins.csv` 行号 | `netlist_v1.csv` 行号 | 说明 |
|---|---|---|---|---|---|---|
| 1 | `GND` | `GND` | `GND` | 36 | 238 | 回地 |
| 2 | `DSI1_DN1` | `DSI1_DN1` | `DSI_D0_D1_N` | 47 | 222, 345 | DSI 差分 |
| 3 | `DSI1_DP1` | `DSI1_DP1` | `DSI_D0_D1_P` | 51 | 220, 344 | DSI 差分 |
| 4 | `GND` | `GND` | `GND` | 52 | 239 | 回地 |
| 5 | `DSI1_CN` | `DSI1_CN` | `DSI_D0_CK_N` | 53 | 214, 341 | DSI 差分 |
| 6 | `DSI1_CP` | `DSI1_CP` | `DSI_D0_CK_P` | 54 | 212, 340 | DSI 差分 |
| 7 | `GND` | `GND` | `GND` | 55 | 240 | 回地 |
| 8 | `DSI1_DN0` | `DSI1_DN0` | `DSI_D0_D0_N` | 56 | 218, 343 | DSI 差分 |
| 9 | `DSI1_DP0` | `DSI1_DP0` | `DSI_D0_D0_P` | 57 | 216, 342 | DSI 差分 |
| 10 | `GND` | `GND` | `GND` | 37 | 241 | 回地 |
| 11 | `SCL0` | `SCL0` | `I2C_B_SCL` | 38 | 248, 350 | ★屏控制 I2C (屏内 MCU @0x45) |
| 12 | `SDA0` | `SDA0` | `I2C_B_SDA` | 39 | 249, 351 | ★屏控制 I2C (屏内 MCU @0x45) |
| 13 | `GND` | `GND` | `GND` | 40 | 242 | 回地 |
| 14 | `3V3` | `3V3` | `LIGHT_3V3` | 41 | 246, 334 | 屏 3.3V |
| 15 | `3V3` | `3V3` | `LIGHT_3V3` | 42 | 247 | 屏 3.3V |
| 16 | `NC` | — | `DSI_D0_D2_N` | 43 | 226, 347 | ★自用: 4-lane 预留 (Pi5 侧 NC) |
| 17 | `NC` | — | `DSI_D0_D2_P` | 44 | 224, 346 | ★自用: 4-lane 预留 (Pi5 侧 NC) |
| 18 | `NC` | — | `DSI_D0_D3_N` | 45 | 230, 349 | ★自用: 4-lane 预留 (Pi5 侧 NC) |
| 19 | `NC` | — | `DSI_D0_D3_P` | 46 | 228, 348 | ★自用: 4-lane 预留 (Pi5 侧 NC) |
| 20 | `NC` | — | `GND` | 48 | 243 | 回地 |
| 21 | `NC` | — | `GND` | 49 | 244 | 回地 |
| 22 | `NC` | — | `GND` | 50 | 245 | 回地 |

★**结论**: 22 脚 **全部有主** (8 个 GND + 2 个 3V3 + 2 个 I2C_B + 10 个 DSI 差分) ⇒ ★**这个座上既没有触控中断脚, 也没有屏复位脚, 也没有空脚可占**。
★**唯一"空"的是 pin16..22** —— 但那 7 个脚在 **Pi5 官方 J4 上是 NC** (`HW/PCB/PI5_DSI_22P_PINOUT.md` §2 证据 P1: "**16..30 标红叉 (NC)**"), 在 Waveshare 官方 22p↔15p 线缆里**也是 NC** ⇒ ★**它们在线缆那头根本没有导体 ⇒ 接不了屏侧的 TP_INT**。

---

## 3. SoM 侧 GPIO 池候选脚表

### 3.1 池子怎么算出来的 (算法可复核)

```
池成员 = FET3572C_PIN_TABLE.csv 里 (conn ∈ {P1,P2,P3,P4})
       ∧ gpio 列能解析出真实 GPIO (GPIO[0-3]_[A-D][0-7], 后缀 _d/_u/_z)
       ∧ vol 列含 "3.3V"
       ∧ desc 不含官方 "not available"      ← Forlinx 手册原文
       ∧ (conn,num) ∉ som_pin_assign.json 的 assign ∪ fixed
       ∧ (conn,num) 在 netlist_v1.csv 里 0 命中
⇒ 结果: **36 只** (P4=22 / P1=13 / P2=1 / **P3=0**)
```

★**为什么 P3 = 0**: RK3572 的 P3 (DSI/CSI + 供电) 座上所有 GPIO-capable 脚**全是 1.8V 域** (`HW/PCB/FET3572C_PIN_TABLE.csv` P3 各行 vol 列) ⇒ 3.3V 候选只能在 P1/P2/P4 —— 这也解释了 brief 为什么点名 P1/P2/P4。

### 3.2 候选脚表 (★每个候选都有官方功能名 + 官方 IOMUX + 占用证据, 没有一个靠"看起来空着")

| # | SoM 脚 | ball | 官方 GPIO | 电平 | 官方出厂默认功能 (Rockchip datasheet 原文抄录) | 出处 | 官方内核 IOMUX ⇒ 能否复用成 GPIO 输入 | 本板占用 (行号级) | 几何 (只报风险, 不布线) |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **J_SOM_P4 pin62** **★主选★** | `B7` | `GPIO2_D7_z` | 3.3V | `CAN1_RX_M3/PWM2_CH3_M2/I2C4_SDA_M2/SPI3_CSN0_M0/UART3_RTSN_M0/VI_CIF_ ⏎ B7      GPIO2_D7 ⏎ CLKI/SPDIF_TX0_M2/FSPI1_RST/FSPI1_CSN1_M1/ETH0_RXCLK/GPIO2_D7_z` | datasheet V1.1 **p.27** | bank2 `RK_PD7` · F1:`eth0_rxclk` · F2:`fspi1m1_csn1` · F3:`fspi1_rst` · F5:`spdif_tx0_m2` · F6:`vi_cif_clki` · …共10条 ⇒ **FUNC0 未列 = GPIO 复位功能 ⇒ 可作输入** | 网表 **0 命中** (`grep -c "J_SOM_P4 pin62" HW/netlist_v1.csv` = 0) | 到 CONN_LIGHT 最近 **6.41 mm** · 走廊既有铜箔 83 段 |
| 2 | **J_SOM_P4 pin60** 备选 | `A10` | `GPIO2_C7_d` | 3.3V | `ISP_PRELIGHT_TRIG_M0/UART11_RX_M2/I2C9_SCL_M2/SPI1_CSN1_M1/UART10_RTSN_ ⏎ M1/VI_CIF_D4/PDM_CLK1_M3/SAI0_MCLK_M0/SDMMC0_D3_M1/FSPI1_D4_M1/ETH0_RX     A10     GPIO2_C7 ⏎ CTL/GPIO2_C7_d` | datasheet V1.1 **p.27** | bank2 `RK_PC7` · F1:`eth0_rxctl` · F2:`fspi1_d4_m1` · F3:`sdmmc0_d3_m1` · F4:`sai0_mclk_m0` · F5:`pdm_clk1_m3` · …共11条 | 网表 **0 命中** | 到 CONN_LIGHT 最近 **6.3 mm** · 走廊既有铜箔 106 段 |
| 3 | **J_SOM_P4 pin58** 备选 | `1D6` | `GPIO2_D2_d` | 3.3V | `SATA30_PORT0_ACTLED_M0/PWM1_CH3_M2/I2C6_SCL_M2/SPI1_CSN0_M1/UART1_TX_ ⏎ M1/VI_CIF_D1/SAI0_SDO0_M0/SDMMC0_PWREN_M1/FSPI1_D1_M1/ETH0_RXD0/GPIO2_    1D6      GPIO2_D2 ⏎ D2_d` | datasheet V1.1 **p.27** | bank2 `RK_PD2` · F1:`eth0_rxd0` · F2:`fspi1_d1_m1` · F3:`sdmmc0m1_pwren` · F4:`sai0_sdo0_m0` · F6:`vi_cif_d1` · …共10条 | 网表 **0 命中** | 到 CONN_LIGHT 最近 **6.22 mm** · 走廊既有铜箔 133 段 |
| 4 | **J_SOM_P4 pin56** 备选 | `A7` | `GPIO2_D1_d` | 3.3V | `PCIE1_CLKREQN_M0/SATA30_PORT1_ACTLED_M0/PWM0_CH0_M2/I2C7_SDA_M1/SPI1_ ⏎ MISO_M1/UART1_RTSN_M1/VI_CIF_D2/PDM_SDI3_M3/SAI0_LRCK_M0/SDMMC0_CLK_M      A7      GPIO2_D1 ⏎ 1/FSPI1_D2_M1/ETH0_RXD1/GPIO2_D1_d` | datasheet V1.1 **p.27** | bank2 `RK_PD1` · F1:`eth0_rxd1` · F2:`fspi1_d2_m1` · F3:`sdmmc0_clk_m1` · F4:`sai0_lrck_m0` · F5:`pdm_sdi3_m3` · …共12条 | 网表 **0 命中** | 到 CONN_LIGHT 最近 **6.16 mm** · 走廊既有铜箔 162 段 |
| 5 | **J_SOM_P4 pin54** 备选 | `1B4` | `GPIO2_C1_d` | 3.3V | `PWM2_CH7_M0/SPI3_CSN1_M2/SPI4_CSN0_M2/UART5_CTSN_M1/PDM_SDI0_M1/SAI0_ ⏎ 1B4      GPIO2_C1 ⏎ SDO0_M2/SAI1_SDI0_M0/VI_CIF_D8/ETH0_RXD2/GPIO2_C1_d` | datasheet V1.1 **p.26** | bank2 `RK_PC1` · F1:`eth0_rxd2` · F2:`vi_cif_d8` · F4:`sai1_sdi0_m0` · F5:`sai0_sdo0_m2` · F6:`pdm_sdi0_m1` · …共9条 | 网表 **0 命中** | 到 CONN_LIGHT 最近 **6.12 mm** · 走廊既有铜箔 193 段 |
| 6 | **J_SOM_P4 pin52** 备选 | `1C4` | `GPIO2_C0_d` | 3.3V | `SPI4_MISO_M2/UART5_RTSN_M1/PDM_SDI1_M1/SAI1_SDI1_M0/SAI1_SDO3_M0/VI_CIF ⏎ 1C4      GPIO2_C0 ⏎ _D9/ETH0_RXD3/GPIO2_C0_d` | datasheet V1.1 **p.26** | bank2 `RK_PC0` · F1:`eth0_rxd3` · F2:`vi_cif_d9` · F4:`sai1_sdo3_m0` · F5:`sai1_sdi1_m0` · F6:`pdm_sdi1_m1` · …共7条 | 网表 **0 命中** | 到 CONN_LIGHT 最近 **6.11 mm** · 走廊既有铜箔 202 段 |
| 7 | **J_SOM_P4 pin39** 备选 | `1T22` | `GPIO0_C6_d` | 3.3V | `I2C3_SCL_M1/UART8_RTSN_M1/SAI0_SCLK_M1/SPI0_CSN0_M0/GPIO0_C6_d           1T22    GPIO0_C6` | datasheet V1.1 **p.25** | bank0 `RK_PC6` · F4:`sai0_sclk_m1` · F9:`uart8m1_rtsn` · F10:`spi0m0_csn0` · F11:`i2c3_scl_m1` | 网表 **0 命中** | 到 CONN_LIGHT 最近 **9.19 mm** · 走廊既有铜箔 351 段 |
| 8 | **J_SOM_P4 pin29** 备选 | `1A2` | `GPIO2_B1_d` | 3.3V | `CAN0_TX_M2/PWM2_CH4_M1/I2C2_SCL_M2/SPI3_CSN0_M2/UART6_TX_M0/SAI0_SDI1_ ⏎ 1A2      GPIO2_B1 ⏎ M2/SAI1_SCLK_M0/GPIO2_B1_d` | datasheet V1.1 **p.26** | bank2 `RK_PB1` · F4:`sai1_sclk_m0` · F5:`sai0_sdi1_m2` · F9:`uart6_tx_m0` · F10:`spi3m2_csn0` · F11:`i2c2_scl_m2` · …共7条 | 网表 **0 命中** | 到 CONN_LIGHT 最近 **9.19 mm** · 走廊既有铜箔 532 段 |
| 9 | **J_SOM_P4 pin31** 备选 | `1D2` | `GPIO2_B3_d` | 3.3V | `CAN0_RX_M2/PCIE1_CLKREQN_M2/I2C2_SDA_M2/SPI4_CSN1_M2/UART9_RX_M2/SAI0_ ⏎ 1D2      GPIO2_B3 ⏎ SDI2_M2/SAI1_LRCK_M0/VI_CIF_D14/UART6_CTSN_M0/GPIO2_B3_d` | datasheet V1.1 **p.26** | bank2 `RK_PB3` · F2:`vi_cif_d14` · F4:`sai1_lrck_m0` · F5:`sai0_sdi2_m2` · F9:`uart9_rx_m2` · F10:`spi4m2_csn1` · …共9条 | 网表 **0 命中** | 到 CONN_LIGHT 最近 **9.19 mm** · 走廊既有铜箔 474 段 |
| 10 | **J_SOM_P4 pin5** 备选 | `B10` | `GPIO2_C5_d` | 3.3V | `PWM2_CH5_M2/I2C8_SDA_M2/UART10_RX_M1/VI_CIF_D6/PDM_CLK0_M3/SAI0_SDI1_M ⏎ B10     GPIO2_C5 ⏎ 0/SDMMC0_D1_M1/FSPI1_D6_M1/ETH0_MDIO/GPIO2_C5_d` | datasheet V1.1 **p.27** | bank2 `RK_PC5` · F1:`eth0_mdio` · F2:`fspi1_d6_m1` · F3:`sdmmc0_d1_m1` · F4:`sai0_sdi1_m0` · F5:`pdm_clk0_m3` · …共9条 | 网表 **0 命中** | 到 CONN_LIGHT 最近 **9.19 mm** · 走廊既有铜箔 432 段 |
| 11 | **J_SOM_P4 pin7** 备选 | `B9` | `GPIO2_C6_d` | 3.3V | `UART11_TX_M2/I2C9_SDA_M2/SPI3_CSN1_M0/UART10_CTSN_M1/VI_CIF_D5/PDM_SDI ⏎ B9      GPIO2_C6 ⏎ 1_M3/SAI0_SDO1_M0/SDMMC0_D2_M1/FSPI1_D5_M1/ETH0_MDC/GPIO2_C6_d` | datasheet V1.1 **p.27** | bank2 `RK_PC6` · F1:`eth0_mdc` · F2:`fspi1_d2_m1` · F3:`sdmmc0_d2_m1` · F4:`sai0_sdo1_m0` · F5:`pdm_sdi1_m3` · …共10条 | 网表 **0 命中** | 到 CONN_LIGHT 最近 **9.19 mm** · 走廊既有铜箔 417 段 |
| 12 | **J_SOM_P1 pin56** 备选 | `1D3` | `GPIO2_B6_d` | 3.3V | `UART2_RTSN_M1/SPI4_CLK_M2/UART11_TX_M1/PDM_SDI3_M1/SAI1_SDI3_M0/SAI1_S ⏎ 1D3      GPIO2_B6 ⏎ DO1_M0/VI_CIF_D11/ETH0_PPSCLK/GPIO2_B6_d` | datasheet V1.1 **p.26** | bank2 `RK_PB6` · F1:`eth0_ppsclk` · F2:`vi_cif_d11` · F4:`sai1_sdo1_m0` · F5:`sai1_sdi3_m0` · F6:`pdm_sdi3_m1` · …共8条 | 网表 **0 命中** | 到 CONN_LIGHT 最近 **54.12 mm** · 走廊既有铜箔 104 段 |
| 13 | **J_SOM_P1 pin60** 备选 | `A4` | `GPIO2_B7_d` | 3.3V | `UART2_CTSN_M1/SPI4_MOSI_M2/UART11_RX_M1/PDM_SDI2_M1/SAI1_SDI2_M0/SAI1_ ⏎ A4      GPIO2_B7 ⏎ SDO2_M0/VI_CIF_D10/ETH0_PPSTRIG/GPIO2_B7_d` | datasheet V1.1 **p.26** | bank2 `RK_PB7` · F1:`eth0_ppstrig` · F2:`vi_cif_d10` · F4:`sai1_sdo2_m0` · F5:`sai1_sdi2_m0` · F6:`pdm_sdi2_m1` · …共9条 | 网表 **0 命中** | 到 CONN_LIGHT 最近 **53.79 mm** · 走廊既有铜箔 101 段 |

★**证据等级**: 官方默认功能 = **[官网]** (Rockchip 官方 datasheet V1.1 §2.6 Pin Number List, p.25/26/27) · IOMUX = **[官网]** (Rockchip 官方内核 `rk3572-pinctrl.dtsi`, `develop-6.12`) · 占用 = **[实测]** (本机 grep, 行号可复核) · 几何 = **[推算]** (脚本从板文件反读, ★**只报距离与走廊铜箔密度, 不做任何布线**) · ★**实物 [实测] = 0 条** (无实板)。

### 3.3 判据② 明令排除的脚 (官方默认功能落在 BOOT / 电源域 / 复位 / 调试链上)

| 被排除的脚 | 官方默认功能 | 排除理由 |
|---|---|---|
| `J_SOM_P4 pin4` (1P21, `GPIO0_D1_d`, 3.3V) | `TYPEC0_PWREN` | **电源使能** ⇒ 判据② 不通过 |
| `J_SOM_P4 pin9` (1P20, `GPIO0_D0_d`, 3.3V) | `MIPI_DSI1_RESET` | **复位** ⇒ 判据② 不通过 |
| `J_SOM_P4 pin33` (AB33, `GPIO0_B6_d`, 3.3V) | `TF_PWR_EN_3V3` | **电源使能** ⇒ 判据② 不通过 |
| `J_SOM_P4 pin35` (A11, `GPIO2_C4_d`, 3.3V) | `4G/5G_MOD_PWREN_3V3` | **电源使能** ⇒ 判据② 不通过 |
| `J_SOM_P4 pin37` (A8, `GPIO2_D0_d`, 3.3V) | `M.2_PCIE0_CLKREQN_M0_3V3` | **PCIe 时钟** ⇒ 判据② 不通过 |
| `J_SOM_P1 pin74` (1P22, `GPIO0_D2_d`, 3.3V) | `PCIE0_WAKEn_M0` | **PCIe 唤醒** ⇒ 判据② 不通过 |
| `J_SOM_P1 pin76` (AB32, `GPIO0_B5_d`, 3.3V) | `M.2_PCIE0_WAKEn_3V3` | **PCIe 唤醒** ⇒ 判据② 不通过 |
| `J_SOM_P1 pin3` (1A10, `GPIO2_A1_d`, 1.8V/3.3V) | `SDMMC0_D1` | **BOOT 链** (SoM 启动存储总线) ⇒ 判据② 不通过 |
| `J_SOM_P1 pin5` (1D8, `GPIO2_A0_d`, 1.8V/3.3V) | `SDMMC0_D0` | **BOOT 链** ⇒ 判据② 不通过 |
| `J_SOM_P1 pin7` (1C8, `GPIO2_A5_d`, 1.8V/3.3V) | `SDMMC0_CLK` | **BOOT 链** ⇒ 判据② 不通过 |
| `J_SOM_P1 pin9` (1B8, `GPIO2_A4_z`, 1.8V/3.3V) | `SDMMC0_CMD` | **BOOT 链** ⇒ 判据② 不通过 |
| `J_SOM_P1 pin11` (1A8, `GPIO2_A3_d`, 1.8V/3.3V) | `SDMMC0_D3` | **BOOT 链** ⇒ 判据② 不通过 |
| `J_SOM_P1 pin13` (B11, `GPIO2_A2_d`, 1.8V/3.3V) | `SDMMC0_D2` | **BOOT 链** ⇒ 判据② 不通过 |
| `J_SOM_P2 pin3` (W33, `GPIO0_C3_d`, 3.3V) | `M.2_PWR_EN_3V3` | **电源使能** ⇒ 判据② 不通过 |
| `J_SOM_P2 pin5` (AC33, `GPIO0_B4_d`, 3.3V) | `x` | ★**Forlinx 官方手册原文 "Occupied by the SoM and not available."** ⇒ 不可用 |
| `J_SOM_P2 pin19` (AL32, `GPIO3_D4_d`, **1.8V**) | `GMAC1_INT` | 1.8V 域 + INT ⇒ 判据①② 双不通过 |
| `J_SOM_P2 pin21` (1D10, `GPIO3_D5_d`, **1.8V**) | `GMAC1_RESET` | 1.8V 域 + RESET ⇒ 判据①② 双不通过 |
| `J_SOM_P2 pin79` (1AB22, `GPIO3_D0_d`, **1.8V**) | `MIPI_DSI1_EN_1V8` | 1.8V 域 + DSI 使能 ⇒ 判据①② 双不通过 |
| `J_SOM_P2 pin75` (1M20, `GPIO0_A5_z`, **1.8V**) | `TYPEC0_INT` | 1.8V 域 + Type-C INT ⇒ 判据①② 双不通过 |

★**调试链口径**: 本板调试串口 = `UART0_TX_M0_DEBUG` / `UART0_RX_M0_DEBUG` = `J_SOM_P2 pin7` / `pin9` (`HW/PCB/som_pin_assign.json` `assign.UART_TX/UART_RX`) ⇒ **候选池里没有任何一只脚落在 UART0/JTAG 上**; `UART11` (P1_56/P1_60) 与 `UART8`/`UART9` **不是**本板调试链。

### 3.3.1 ★★最强反驳的正面回答: 「OK3572-C 载板把 ETH0 用了, 这些脚还能当 GPIO 吗?」★★

★这是评审时最可能被问的一条, 正面回答如下 (全部 [官网]):

| 问 | 答 | 出处 |
|---|---|---|
| P1/P2/P3/P4 是**谁**的 100 脚? | ★**FET3572-C SoM 自己的**球位座定义 —— 手册**第 2 章 = "FET3572-C SoM Description"**, §2.6 = **"FET3572-C SoM Pin Definition"**, §2.7 = "SoM Interfaces" ⇒ **不是载板的脚** | Forlinx 官方手册目录 (本机快照 `state/_os_snapshots/fx3572_manual.html`) |
| 那 P4_38..P4_62 的 ETH0 是谁在用? | ★**SoM 把这 14 个球位"指定"为以太网接口控制脚 (§2.7.11 "Ethernet Interface Control Pins"), 但【PHY + 双 RJ45 是在 OK3572-C 载板上】(第 3 章 §3.5.10 "Ethernet Circuit": "The carrier board supports **dual** 1000/100/10M Ethernet interfaces, which are led out via RJ45") ⇒ **我们用自研主板替掉载板 ⇒ 这 14 个球位在主板上就是空脚** | 手册 §2.7.11 + §3.5.10 |
| §2.7.11 的官方原文 (逐脚) | `GMAC0_MDC_M0 → P4_7` · `GMAC0_MDIO_M0 → P4_5` · `GMAC0_TXD3/TXD2/TXD1/TXD0 → P4_38/P4_40/P4_42/P4_44` · `GMAC0_TXCTL/TXCLK → P4_46/P4_48` · `GMAC0_RXD3/RXD2/RXD1/RXD0 → P4_52/P4_54/P4_56/P4_58` · `GMAC0_RXCTL → P4_60` · ★**`GMAC0_RXCLK_M0 → P4_62`** | 手册 §2.7.11 原文 (本机快照) |
| 空脚能不能留? | ★**手册原文: "Unused signal pins on the core board can be left floating, but all GND connections must be properly established."** ⇒ ★**官方明确允许把 SoM 未用信号脚留空/另作他用** | 手册 §2.8.1 "SoM Circuit Design Guidelines" |
| 那 SoM 会不会自己驱动这颗球? | 不会 —— **SOM 自带能力清单里没有以太网 PHY** (`HW/PCB/SOM_BUILTIN_CAPABILITY.md` A1..A8: PMIC / 晶振 / 板载存储 / USB2.0 OTG / MCLK / 复位链 / 4×100pin BTB / MIPI ⇒ **无 PHY**) ⇒ ball B7 (`GPIO2_D7`) 在 SOM 上是**未驱动**的 | `HW/PCB/SOM_BUILTIN_CAPABILITY.md` + 手册 §2.4 性能参数 |

⇒ **结论: `P4_62` 是合法的、SoM 侧未被驱动的 3.3V 空脚。** ⇒ 用它做 TP_INT 的 SoM 侧输入, **电气上成立**。

### 3.4 选脚结论 + 三条判据逐条对照

**★主选: `J_SOM_P4 pin62` (ball `B7`, `GPIO2_D7_z`, 官方默认 `ETH0_RXCLK`, 3.3V)**
**★备选 (按序): `P4_60` → `P4_58` → `P4_56` → `P4_54` → `P4_52` → `P4_39` → `P4_29/31` → `P1_56/60`**

| 判据 | 逐条对照 | 结论 |
|---|---|---|
| **① 必须是 SoM 上已有的 3.3V GPIO 输入脚** (不许引外部器件, 不许改板层数/层序) | · 3.3V ✔ (`FET3572C_PIN_TABLE.csv` P4_62 vol 列 = 3.3V) · 是 SoM 座上**已经引出来**的球位 ✔ (`J_SOM_P4` = 100 脚 0.4mm BTB, 焊盘已在板上) · 官方 IOMUX 里 **FUNC0 未列 = GPIO 复位功能** ⇒ 天然可作输入, **零 pinmux 配置** ✔ · 不引外部器件 ✔ (只占一个已有的空焊盘) · 不改板层数/层序 ✔ (现板 **8 铜层**, `HW/PCB/STACKUP.md` 从板文件反读) | ★**通过** |
| **② 不能是 BOOT / 电源域 / 复位 / 调试链路相关的脚** | · `P4_62` 官方默认 `ETH0_RXCLK` = 以太网参考时钟, **既非 BOOT、也非电源域/复位、也非调试链** ✔ · Forlinx 手册对该脚无上拉/特殊说明 (只有启动配置类脚才有内部上下拉, §3.5.4.1) ✔ · 全部被排除的 BOOT/电源/复位脚已在 §3.3 逐条列名 ✔ | ★**通过** |
| **③ 离现有走线/机械干涉最小** (只报几何风险, 不做布线) | · `J_SOM_P4` 座中心 (25.0, 52.5); `CONN_LIGHT` 座中心 (30.0, 62.0) ⇒ 主选脚焊盘 (22.80, 54.04), **到 CONN_LIGHT 最近焊盘 6.41 mm** ★(**J_SOM_P4 是四个 SoM 座里离屏座最近的**) · 走廊既有铜箔 **83 段** = 全 36 只候选里**最低** (对比 P1_56 = 104 段但距离 54.12 mm) · **机械干涉**: `J_SOM_P4` 与 `CONN_LIGHT` 是板上两个独立封装, 中间无第三器件 (板 160×100 mm) ⇒ 无机械干涉 | ★**通过** |

★**为什么选 `P4_62` 而不是 `P1_56`**:
`P1_56` 虽被我们自己的 `som_pin_assign.json` `released` 段明确释放 ("★2026-11-04: Waveshare 2.8\" 屏侧无 RESET 脚 ⇒ SoM 的 P1_56 (GPIO2_B6_d) 释放"), ★**但 ISS-204 的 F3 结论正是「`P1_56`/`P1_60` 是零 pinmux 成本的第二路 UART」⇒ 把它留给 TP_INT 会打断那个规划**; 且它离屏座 **54.12 mm** (几何最差)。⇒ **`P1_56`/`P1_60` 留在池里但只作第 12/13 顺位**。

★**机会成本声明**: 烧掉 `ETH0_RXCLK` ⇒ **以太网参考时钟没了**。本项目 (眼镜) 无以太网 PHY 需求 ⇒ 代价 ≈ 0; 若将来要以太网, 换备选 `P4_52/54/56/58/60` 任一只即可 (同组同域)。

### 3.5 改了它要付的代价 (主选 `P4_62`)

| 维度 | 代价 |
|---|---|
| 改网表行数 | **本板 = 0 行** (判据: 现行屏座无 TP_INT 脚 ⇒ 无信号可接 ⇒ **本轮不动网表**) |
| 改原理图页 | **本板 = 0 页** (前瞻轮才动: P4 显示页 + P1 电源页, 见 §4.4) |
| 板要不要动 | **本板 = 不动** (焊盘已在板上; ★**换屏到 Radxa 8HD 40p 时才要动** —— 换 FPC 座 + 走线, 见 §4.5) |
| BOM 变不变 | **不变** (0 个新器件; 上拉用 SoM pad 内部弱上拉, 见 §4.7) |
| 整链要不要重出 | **本板 = 不要** (网表没改 ⇒ 网表/引脚表/板/PDF 全不变) |
| 占用成本 | 烧掉 `ETH0_RXCLK` (见 §3.4) |

---

## 4. 原理图变更规格 (★本单唯一的产出形态★)

### 4.1 A 段 —— 本板 (现行 Waveshare 2.8" 22p): **不改什么**

| 项 | 结论 | 理由 (行号级) |
|---|---|---|
| 要改哪个网 | ★**一个都不改** | `NET_TP_INT` 不存在 (§1.1); 屏侧无触控中断脚 (§2) |
| 要接哪个脚 | ★**不接** | 同上 |
| 网表 CSV | ★**0 行增 / 0 行删** | — |
| 原理图 | ★**0 页改动** (`demo_mainboard_p1..p10.kicad_sch` 全部不动) | — |
| 板 | ★**不动** | `demo_mainboard.kicad_pcb` md5 `611b869e13518c3c023fb178f91a0075` 交卷前后相同 |
| BOM | ★**不变** | — |
| 唯一要做的 | ★**在 `state/fragments/hw.yaml` 登记「`J_SOM_P4 pin62` = 预留给屏侧触控中断 (R1)」** ⇒ 防止下一轮有人把它拿去干别的 (门禁 `HW/check_tp_int_gap.py` 会抓) | §5.4 |

### 4.2 B 段 —— 前瞻 (光机换到带 TP_INT 的屏时): **改什么**

★**触发条件**: ISS-156/ISS-158 的 P2 屏模组最终选定为 **Radxa Display 8HD/10FHD 40p/0.5mm** (其 pin26 = TP_INT, pin24 = TP_RESET, 见 `HW/PCB/DISPLAY_39P_PINOUT.md:71/73/123/125`)。

| 项 | 规格 |
|---|---|
| 要改/不改哪个网 | ★**新增 1 个网** `TP_INT` (SoM 侧用 `TP_INT` 不用 `NET_TP_INT` —— 现行网表里 `NET_*` 前缀是**轨/伪件名**的约定, 纯信号网不带 `NET_` 前缀, 例: `I2C_B_SCL` / `CAM_RESET_N` / `DSI_D0_CK_P`); ★**不改任何现有网** (现有 22p 座 pin16..19 仍给 lane2/lane3) |
| 要接到哪个脚 | ★**SoM 侧: `J_SOM_P4 pin62`** = ball `B7` = `GPIO2_D7_z` (3.3V) · 官方默认 `ETH0_RXCLK` · ★**屏侧: 新 40p 座的 pin26** (`TP-INT`) |
| 屏侧脚位 | ★**待 ISS-156 落定** (39p↔40p 合并关系见 `HW/PCB/display_39p_pinout.json` 的 `merge_40_to_39`) ⇒ **本轮只钉 SoM 侧, 屏侧位号留 TBD** |

### 4.3 网表 CSV 该加/删哪几行 (★给模板, 本单**不改 CSV★★)

★**表列顺序** (`HW/netlist_v1.csv` 表头): `page,net,node1,node2,ref,value,type,dnp,evidence,tbd,note,conn_id,board,footprint,opn`

**行 1 —— SoM 侧** (落在 **P4 显示页**):

```
P4,TP_INT,J_SOM_P4 pin62,NET_TP_INT,NET_TP_INT,TP_INT,NET,必装,[官网],,"[TP_INT] ★触控中断 (低有效) ⇒ 屏 = Radxa Display 8HD/10FHD 40p FPC pin26 (TP-INT); SoM 侧 J_SOM_P4 pin62 = GPIO2_D7_z (ball B7, 官方默认 ETH0_RXCLK, 3.3V) ⇒ **FUNC0 = GPIO 输入, 零 pinmux**; ★上拉用 SoM pad 内部弱上拉 (Rockchip RRPU 10~100kΩ @3.3V + pcfg_pull_up) ⇒ **BOM 不变**; ★本轮只在光机换屏时落, 现行 Waveshare 22p 屏无此脚",A-23,MAIN_PCB,,
```

**行 2 —— 屏侧** (落在 **P4 显示页**; ★**座位号待 ISS-156 落定**, 模板里用占位):

```
P4,TP_INT,<新屏座 ref> pin26,NET_TP_INT,NET_TP_INT,TP_INT,NET,必装,[官网],,"[TP_INT] ★屏侧触控中断 (低有效) ⇒ 新 39/40p 座 pin26 = TP-INT; ★座 ref 待 ISS-156 屏模组选型落定 (现行为 CONN_LIGHT 22p, 无此脚)",A-23,MAIN_PCB,,
```

★**要删的行: 0 行。**
★**conn_id 说明**: 现行 `A-01..A-22` (显示/相机高速段) + `A-24` 已占, `B-01..B-24` 已占 ⇒ **`A-23` 是显示段里唯一空号** (`conn_id` 分配实测见 `HW/netlist_v1.csv` 第 12 列)。
★**若将来要加 `TP_RESET`** (新 40p 座 pin24): 同法再加一行, SoM 侧另选一只 3.3V GPIO (本单**未预选** —— 规格里只点名 `TP_INT` 一只, 避免过度占脚; ⇒ 见 §6 的 [0数据] 项)。

### 4.4 原理图哪一页要加哪根线 (★给页码 + 位号, 本单**不改 .kicad_sch★★)

| 页 | 页名 | 要加什么 | 位号 |
|---|---|---|---|
| **P4** | 显示双出口 (`HW/PCB/demo_mainboard_p4.kicad_sch`) | 屏侧那根线的**引出线 + `global_label "TP_INT"`** (照抄 `I2C_B_SCL` 的跨页画法) | 新屏座 ref (待定) 的 pin26 |
| **P1** | 电源树 (`HW/PCB/demo_mainboard_p1.kicad_sch`) | SoM 侧那根线的**引出线 + `global_label "TP_INT"`** | `J_SOM_P4` 的 pin62 |

★**跨页机制依据 (实测)**:
- `J_SOM_P1/P2/P3/P4` 四个座**全部画在 P1 页** (本机实测: 四个页文件里只有 `demo_mainboard_p1.kicad_sch` 含 `J_SOM_P*` 符号) ⇒ 规则见 `state/gen_kicad_sch.py:145-190` (`build_devices` 的 page 归属: ★**`J_SOM_P2`/`J_SOM_P4` 在网表里只出现在节点串、页为空 ⇒ 一律兜底落 P1**)。
- `CONN_LIGHT` 画在 **P4 页** (实测: `demo_mainboard_p4.kicad_sch` 含 `CONN_LIGHT` 符号)。
- ★**跨页网用 `global_label` 连接**, 现成样板 = `I2C_B_SCL`: `demo_mainboard_p1.kicad_sch:3369` 有 `global_label "I2C_B_SCL"`, `demo_mainboard_p4.kicad_sch:567` 与 `:643` 各有一个同名 `global_label "I2C_B_SCL"` ⇒ **TP_INT 照这个画法一字不改地套**。
- ⇒ **网表行的 `page` 列必须写 `P4`** (照 `I2C_B_SCL` 两行的写法, `HW/netlist_v1.csv:231` / `:248` 都是 `P4`)。

### 4.5 板侧要不要跟着动 (★结论 + 理由)

| 场景 | 板侧 | 理由 |
|---|---|---|
| **本板 (现行屏)** | ★**不动** | 屏座无 TP_INT 脚; SoM 侧焊盘已在板上; 网表 0 改动 ⇒ 板文件 md5 必须保持 `611b869e13518c3c023fb178f91a0075` |
| **前瞻 (换 Radxa 8HD/10FHD 40p 屏)** | ★**要动, 但只动「屏侧那一块」** | ① **FPC 座换型**: 22p/0.5mm (HIROSE FH12-22S) ⇒ 39p/0.3mm (HIROSE FH35C-39S-0.3SHW(50)) ⇒ **新封装 + 新 pitch** ⇒ **必然改板**; ② **SoM 侧不用动** ⇒ ★**这正是本单要先把 `J_SOM_P4 pin62` 钉死的原因** (SoM 侧零改动 ⇒ 换屏只动屏侧那一块); ③ **层数/层序不动** (现板 8 铜层, `HW/PCB/STACKUP.md`) ⇒ 换座是同面内局部改, 不触发叠层重做 |
| ★**几何风险提示 (只报, 不布线)** | 新 40p 座 (0.3mm pitch, 39 脚) 若放在现 `CONN_LIGHT` (30.0, 62.0) 位置, 39 脚 @0.3mm ≈ 11.7 mm 长 ⇒ 与 `J_SOM_P4` (25.0, 52.5) 的间距仍 ≥ 6 mm 量级 ⇒ **机械上可行**; ⇒ **但具体落位要等屏模组机械图** ⇒ [0数据] |

### 4.6 BOM 变不变 (★结论)

★**不变 (0 个新器件)。**
- 不加电阻 (上拉走 SoM pad 内部弱上拉, §4.7);
- 不加连接器 (SoM 侧只占已有焊盘);
- 换屏那轮才动 BOM (新 FPC 座 + 线缆), **不在本单**。

### 4.7 ★TP_INT 要不要上拉 (低有效中断)

★**结论: 用 SoM pad 的内部弱上拉 ⇒ 不用加外部电阻 ⇒ BOM 不变。** (官方依据如下, 三源交叉)

| 出处 | 原文 / 数值 | 等级 |
|---|---|---|
| **Rockchip 官方 datasheet V1.1 p.14 (GPIO 特性)** | "All of GPIOs can be used to generate interrupt" · "Supports configurable pull direction (a **weak pull-up** and a weak pull-down)" | [官网] |
| **Rockchip 官方 datasheet V1.1 p.41 (3.3V/1.8V GPIO @3.3V 电气)** | `Pullup Resistor  RRPU  Min 10 / NA / **Max 100** Kohm`; `Pulldown Resistor RRPD 10~100 Kohm`; `Input pullup resistor current IRPU @3.3V: -20 / NA / **-180** uA (VPAD=0V)`; `Input leakage current IPAD: -10 / NA / **10** uA` | [官网] |
| **Rockchip 官方内核 `rockchip-pinconf.dtsi`** | `pcfg_pull_up: pcfg-pull-up { bias-pull-up; };` ⇒ **pad 内部上拉可配** (在 `rk3572-pinctrl.dtsi` 里被引用 108 次) | [官网] |
| **Forlinx 官方 OK3572-C/FET3572-C User's Hardware Manual** | "All GPIOs can be used to generate interrupts; Supports configuration of pull-up/pull-down (**weak pull-up and weak pull-down**)" | [官网] |

★**裕量核算 (3.3V 域) [推算]**: VIH(min) = 2.1 V (datasheet p.41)。内部上拉最坏 100 kΩ 时, 漏电 10 µA ⇒ 压降 1.0 V ⇒ 静态高电平 ≈ 2.3 V > 2.1 V ✔ (裕量仅 0.2 V); 上拉最坏 10 kΩ 时 ⇒ 压降 0.1 V ⇒ 3.2 V ✔ 裕量充足。
⇒ ★**结论: 内部弱上拉在本拓扑 (开漏 INT, 静态) 下够用**, 但**裕量在 100 kΩ 端只有 0.2 V** ⇒ 见 §6 降级方案。

---

## 5. 整链重出清单 (★真实脚本名, 不许编★)

### 5.1 本板 (本单不改任何东西 ⇒ **本轮不需要重出**)

★**不改网表 ⇒ 网表/引脚表/原理图/板/PDF/BOM 全部不变 ⇒ 不跑生成链。**
**只跑门禁**:
```
python3 HW/check_tp_int_gap.py             # rc=0
python3 HW/check_tp_int_gap.py --selftest  # rc=0
python3 state/check_netlist.py             # rc=0
python3 state/check_netlist_pins.py        # rc=0
python3 state/merge.py                     # rc=0
python3 state/gate_check.py                # rc=0, 【Q1】18/18
```

### 5.2 前瞻轮 (真正落 TP_INT 那一步, 一次性按序跑)

★**顺序不能乱** (★改了网表没跑导出链 ⇒ PCB 工程师手上还是旧版脚级表, 2026-11-04 ISS-153 踩过这个坑):
```
# ① 改网表源 (★在 state/gen_netlist.py 里加那两行, 不是手改 CSV★)
# ② 重新生成网表
python3 state/gen_netlist.py               # → HW/netlist_v1.csv
python3 state/gen_netlist_pins.py          # → HW/netlist_v1_pins.csv
# ③ 重新生成 KiCad 原理图 (★页归属由 page 列决定 ⇒ 那两行 page 必须写 P4★)
python3 state/gen_kicad_sch.py             # → HW/PCB/demo_mainboard_p1..p10.kicad_sch + demo_mainboard.kicad_sch
# ④ 重新生成 KiCad 网表 (导出链, ★缺这一步脚级表会缺脚★)
python3 state/gen_kicad_net.py             # → HW/netlist_v1.net
# ⑤ 板侧换座 + 走线 (★换屏那一轮才做; 本单不做★)
python3 state/gen_pcb_netlist_board.py     # → 板网表
python3 state/gen_pcb_routing.py           # → 板布线
# ⑥ BOM
python3 state/gen_bom.py                   # → HW/BOM_v1.csv
# ⑦ 门禁 (★全部必须 rc=0★)
python3 state/check_netlist.py             # rc=0
python3 state/check_netlist_pins.py        # rc=0
python3 state/check_kicad_net.py            # rc=0
python3 state/check_sch_pinfull.py         # rc=0
python3 state/check_pcb_nets.py            # rc=0
python3 HW/check_tp_int_gap.py              # rc=0   ★本单新门禁
python3 state/merge.py                     # rc=0
python3 state/gate_check.py                # rc=0, 【Q1】18/18
```
★**脚本存在性** (交卷前实测): `state/gen_netlist.py` ✔ · `state/gen_netlist_pins.py` ✔ · `state/gen_kicad_sch.py` ✔ · `state/gen_kicad_net.py` ✔ · `state/gen_pcb_netlist_board.py` ✔ · `state/gen_pcb_routing.py` ✔ · `state/gen_bom.py` ✔ · `state/check_netlist.py` ✔ · `state/check_netlist_pins.py` ✔ · `state/check_kicad_net.py` ✔ · `state/check_sch_pinfull.py` ✔ · `state/check_pcb_nets.py` ✔ · `state/merge.py` ✔ · `state/gate_check.py` ✔

### 5.3 并发提示
`state/merge.py` 若报 **rc=2** (并发写 `STATE.yaml` 冲突) ⇒ **等 30 秒重跑一次**; 重跑仍红就如实报, 不死磕。

### 5.4 ★登记 (本单唯一动 `state/` 的动作)
`state/fragments/hw.yaml` **只许新增条目** (走 `state/frag_write.py`, 禁 `open(p,"w")`):
> artifact: `HW/PCB/TP_INT_REMAP_SPEC.md` · `HW/check_tp_int_gap.py` · `HANDOFF/2026-11-15_hw-lead_ISS174_TPINT改脚规格.md`
> claim: `J_SOM_P4 pin62` (GPIO2_D7_z, ball B7) = **预留给屏侧触控中断 TP_INT 的 SoM 侧脚 (R1)** ⇒ 现行 Waveshare 22p 屏不接, 换 Radxa 8HD/10FHD 40p 屏时才落 ⇒ ★**该脚不得他用**。

---

## 6. [0数据] 项与降级方案 (★查不到就写降级, 不许猜, 没有「等原厂回信」这个选项★)

| # | 查不到/未定的项 | 状态 | 降级方案 |
|---|---|---|---|
| 1 | **TP_RESET (新 40p 座 pin24) 的 SoM 侧脚** | **[0数据]** —— 本单**只预选 1 只脚** (TP_INT), 不预选第 2 只 | 换屏那一轮按 §3.2 表再挑一只 (同 P4 组同域, 零代价); 或按 Radxa Q6A 官方做法 **靠屏模组内部上拉** (`HW/PCB/DISPLAY_39P_PINOUT.md` §note 待核项) ⇒ 落板前用示波器实测 TP_RESET 静态电平再决定 |
| 2 | **新 40p 屏座的机械落位 / 干涉** | **[0数据]** —— 等 ISS-156 屏模组机械图 | §4.5 已给几何量级判断 (与 `J_SOM_P4` 间距 ≥6 mm 量级, 可行); 落位由结构总工在屏模组选定后定, **本单不做布局** |
| 3 | **RK3572 pad 内部上拉的 typ 值** | **[0数据]** —— datasheet 只给区间 10~100 kΩ, 无 typ | 已按最坏 100 kΩ 核算 (§4.7): 高电平 ≈2.3 V > VIH 2.1 V ✔; ⇒ **若实测发现上升沿慢/误触发** ⇒ 改走外部上拉 (10k 到 `RAIL_VDD_3V3_IO`), ★**但本单不加这个电阻进 BOM** (须另开变更单) |
| 4 | **GT911 @0x14 的 INT 静态电平 / 漏电流** | **[0数据]** —— Waveshare 官方只给 "Touch Port I2C", 未给 GT911 INT 电气 | 本板不接该 INT ⇒ 不影响; 将来若改为「SoM 直连 GT911」而非走屏内 MCU ⇒ 按 §4.7 同法核算, **并须补查 GT911 datasheet 的 INT 驱动能力** |
| 5 | **FET3572-C 载板层面 (不是 SoC 层面) 有没有给这些脚加外部上下拉** | **[0数据]** —— Forlinx 手册只对**启动配置类脚** (SDMMC0_DET_L / BOOT 分压) 明写内部上下拉; 其余 GPIO 脚**未逐脚列** | 已在 §3.4 判据② 里声明: 若将来发现载板对该脚有外部上拉 ⇒ 与 pad 内部上拉并联 ⇒ 电平仍为高, **不冲突**; 但阻值变小 ⇒ 重新核算 IRPU |
| 6 | **换屏后的 40p 座与 39p 原厂表的针序合并关系** | **[0数据]** —— `HW/PCB/display_39p_pinout.json` 有 `merge_40_to_39` 字段但未核 | 换屏那一轮必须逐针核 (39p↔40p 差一个脚), **本单不预判** |

---

## 7. 边界 (★本单没做什么 —— 写清楚, 免得被当成"设计已改"★)

- ★**没改网表** (`HW/netlist_v1.csv` md5 `c78f991283cc82d56c8e3dd31657c785`, 交卷前后相同)
- ★**没改引脚表** (`HW/netlist_v1_pins.csv` md5 `4814617e22b567d76164e56bc5e39dc8`, 交卷前后相同)
- ★**没改板** (`HW/PCB/demo_mainboard.kicad_pcb` md5 `611b869e13518c3c023fb178f91a0075`, 交卷前后相同)
- ★**没改 SoM 引脚分配表** (`HW/PCB/som_pin_assign.json` md5 `800d08d4451fee46c180815d8badc21c`, 交卷前后相同)
- ★**没改任何 `.kicad_sch`** / 任何 `state/gen_*.py` / 任何既有的 `state/check_*.py`
- ★**没碰** `HW/PCB/RK3572_UART0_TX_PINMUX_VERDICT.md` (ISS-204 交卷件) / `HW/POWER_BUDGET_V3.md` / `HW/` 下其它既有文档 / `SW/` / `MECH/` / `state/issue_log.yaml` / `PROJECT_TRACKER.md` §0 / `state/outbox/`
- ★**没做任何布线 / 布局 / 叠层 / 层序** (几何只报距离与走廊铜箔密度)
- ★**没外发任何邮件 / 询价 / 问询 / 采购 / 原厂问询**
- ★**没改 issue 状态** (改 issue 状态是 main 的活)
- ★**实物 [实测] = 0 条** (无实板) ⇒ 板端一律 [0数据]

---

## 8. 本单用到的源 (★全部公开可复核★)

| # | 源 | 等级 | 用途 |
|---|---|---|---|
| S1 | `HW/netlist_v1.csv` (514 行) · `HW/netlist_v1_pins.csv` (585 行) | [实测] (本机 grep) | 判真伪 ①②③ · 22 脚全表 · 占用证据 |
| S2 | `HW/PCB/FET3572C_PIN_TABLE.csv` (399 行, 由 Forlinx 官方手册重建) | [官网] | 官方 GPIO / 电压域 / 出厂默认功能 |
| S3 | `HW/PCB/som_pin_assign.json` | [官网] (派生自 Forlinx 手册) | 已分配/已释放/固定脚 |
| S4 | `HW/PCB/PI5_DSI_22P_PINOUT.md` (+ `pi5_dsi_22p.json`) | [官网] | Pi5 官方 J4 针序 · **16..22 = NC** |
| S5 | `HW/PCB/FPC_PIN_TABLES.md` | [官网] | ★**「Radxa 8HD 39p 表整表作废」**的书面依据 |
| S6 | `HW/PCB/DISPLAY_39P_PINOUT.md` (39p pin24=TP_RESET / pin26=TP_INT) · `display_39p_pinout.json` | [官网] | ISS-174 原描述的出处 + 前瞻场景 |
| S7 | `HW/PCB/WAVESHARE_2P8_INIT_AND_BACKLIGHT.md` (:262 官方 Touch Port I2C · :414 · :430 Pi5 官方 overlay) | [官网] | 触控归谁管 |
| S8 | `HW/I2C_ADDR_TABLE.md` (:56 屏内 MCU 0x45 · 触摸 GT911 0x14) | [官网] | I2C 归属 |
| S9 | **Rockchip 官方 RK3572 Datasheet V1.1** §2.6 Pin Number List (p.22 起; 候选行在 p.25/26/27) · GPIO 特性 p.14 · 电气 p.41 —— 本机副本 `HW/RK3572_PIN_TABLE/RK3572_datasheet_V1.1.pdf` + `.txt` (解析产物 `rk3572_pins.json`) | [官网] | 官方出厂默认功能原文 + 内部上拉参数 |
| S10 | **Rockchip 官方内核** `rk3572-pinctrl.dtsi` (`rockchip-linux/kernel` `develop-6.12`) + `rockchip-pinconf.dtsi` —— 本次从官方仓库只读拉取 (★**不是外发, 是公开源读取**) | [官网] | IOMUX 条目 + `pcfg_pull_up` |
| S11 | **Forlinx 官方 OK3572-C / FET3572-C User's Hardware Manual** (本机快照 `state/_os_snapshots/fx3572_manual.html`) | [官网] | 球位↔座脚映射 · "All GPIOs can be used to generate interrupts" · 启动脚内部上下拉 · ★**§2.6 "FET3572-C SoM Pin Definition" (P1..P4 是 SoM 自己的座)** · ★**§2.7.11 "Ethernet Interface Control Pins" (`GMAC0_RXCLK_M0 → P4_62` 等 14 脚逐脚原文)** · ★**§2.8.1 "Unused signal pins on the core board can be left floating"** · ★**§3.5.10 "Ethernet Circuit" (PHY + 双 RJ45 在**载板**上 ⇒ 主板替掉载板 ⇒ 这些脚是空脚)** |
| S12 | `HW/PCB/demo_mainboard.kicad_pcb` (板文件反读, 160×100 mm / 8 铜层) · `HW/PCB/STACKUP.md` | [实测] (本机解析) | 几何风险 |
| S13 | `state/gen_kicad_sch.py:145-190` (页归属规则) · `demo_mainboard_p1/p4.kicad_sch` | [实测] | 原理图页与跨页画法 |

★**本单的"官方"口径与 ISS-204 同源同法**: Rockchip datasheet (球位/功能) + Rockchip 官方内核 pinctrl (复用) + Forlinx 官方手册 (载板侧) 三源交叉。
