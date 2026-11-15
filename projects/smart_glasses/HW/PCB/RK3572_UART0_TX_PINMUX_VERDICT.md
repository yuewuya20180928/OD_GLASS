# ★★[官网×3 交叉] `J_SOM_P2.pin7` 当 `UART_TX` 用 —— 引脚复用合法性判定 (ISS-204 闭环)★★

> ★**日期**: 2026-11-15 21:4x · ★**执行**: 硬件总工 (hw-lead) · ★**单号**: ISS-204
> ★**依据**: ★**老板 2026-11-12 02:02 指令「不再发信，全靠自己查资料」★★ (本单**未发任何邮件 / 未联系任何原厂·供应商·采购**)
> ★**证据等级**: ★**[官网]** (Rockchip datasheet + Rockchip 官方内核仓库 + Forlinx 官方手册) · ★**[实测]** (本机脚本/grep 实读) · ★**[推算]** (由已核事实推出) · ★**[0数据]** (查不到)
> ★**本单性质**: ★**只出文档，一个字节都不许改设计** ⇒ 板 / 网表 / 原理图 / 生成器全部未动 (见 §6 md5 实测)

---

## 0. ★★结论先行 (三条判据一起给)★★

| # | 结论 | 证据等级 |
|---|---|---|
| ★**①** | ★**`J_SOM_P2.pin7` 可以当 `UART_TX` 用 —— 而且【根本不需要引脚复用】, 它出厂默认功能就是 `UART0_TX_M0_DEBUG`** ⇒ ★**本板设计正确, 零改动, 零改板代价** | ★**[官网] ×3 独立源交叉** |
| ★**②** | ★**★★本单的【前提本身是错的】★★★**: 官方 `PWM0_CH1_M0 / GPIO0_C3_d` 是 ★**P2_3 (ball W33)**★, ★**不是 P2_7**★; ★**P2_7 = ball U33 = `UART0_TX_M0_DEBUG` / GPIO0_D4_u**★ | ★**[官网]** (Forlinx Table 3 + Rockchip datasheet p.30/p.31 双向印证) |
| ★**③** | ★**BOOT 链与 UART0 零交集 ⇒ 不受影响** (`SARADC_VIN0_BOOT` = P1_28 / `PMIC_VDC` = P3_10, ★**两者官方 GPIO 列都是「——」⇒ 专用脚, 无任何 GPIO 复用功能**★) | ★**[官网]** + ★**[实测]** (本板实际用脚核对) |

★★**⇒ 一句话给项目总工**: ★**ISS-204 不是缺陷, 是【前提误读】⇒ 板和网表一个字都不用改 ⇒ 但 [顺带查出 1 条真缺陷 (UART 缺 100Ω 串阻 + TVS) + 1 条可关闭的外部依赖 (TBD-01)] 落在 §5, 要另开 issue 走网表流程。★★

---

## 1. ★★先把前提摆正: `PWM0_CH1_M0` 到底是哪个脚? (★错位在哪★)★★

### 1.1 ★★官方模组表 (Forlinx) —— `P2_7` 在【奇数表 Table 3】, 不在偶数表 Table 4★★

> ★**出处**: `https://docs.forlinx.net/rockchip/ok3572-c/OK3572-C_User_Hardware_Manual.html`
> ★**章节**: §2.6.2 "FET3572-C SoM Pin Function Description" ⇒ ★**Table 3 "P2 Connector Interface (Odd) Pin Definition"**
> ★**表头**: `NUM | BALL | Signal Name | GPIO | VOL | Pin Description | Default Function`

★**原文抄录 (三行逐字)**:

```
7 | U33 | UART0_TX_M0_DEBUG | GPIO0_D4_u | 3.3V | UART0 send (Debug Serial Port) | UART0_TX_M0_DEBUG
9 | V32 | UART0_RX_M0_DEBUG | GPIO0_D5_u | 3.3V | UART0 receive (Debug Serial Port) | UART0_RX_M0_DEBUG
3 | W33 | PWM0_CH1_M0       | GPIO0_C3_d | 3.3V | PWM0_CH1_M0                   | M.2_PWR_EN_3V3
```

★★**⇒ 错位点**: ★**`PWM0_CH1_M0 / GPIO0_C3_d` 的 NUM 是 3 (ball W33), 官方默认功能栏还写着 `M.2_PWR_EN_3V3`** ⇒ ★**它跟 `UART_TX` 没有任何关系**; ★**`P2_7` 是 `UART0_TX_M0_DEBUG`, `P2_9` 是 `UART0_RX_M0_DEBUG` ⇒ TX/RX 本来就是同一组 UART0, 是【官方默认】, 不是【需要我们去做引脚复用】★★

### 1.2 ★★官方模组表【按功能】分表 —— 直接把 P2_7 钉死在 UART0_TX 上 (★★最硬的一条★★)★★

> ★**出处**: 同上手册 · ★**章节**: ★**§2.7.9 "UART Interface Control Pins"** (SoM 按功能归类的表)
> ★**表头**: `Default Function | Signal Name | I/O | Default Function | Pin Number`

★**原文抄录**:

```
UART0 | UART0_TX_M0_DEBUG | O | UART0 data sending     | P2_7
      | UART0_RX_M0_DEBUG | I | UART0 data receiving    | P2_9
UART11| UART11_TX_M1      | O | UART11 data sending    | P1_56
      | UART11_RX_M1      | I | UART11 data receiving   | P1_60
UART9 | UART9_TX_M0       | O | UART9 data sending     | P4_21
      | UART9_RX_M0       | I | UART9 data receiving    | P4_23
UART8 | UART8_TX_M0       | O | UART8 data sending     | P2_73
      | UART8_RX_M0       | I | UART8 data receiving    | P2_69
```

★★**⇒ 官方自己写的: `UART0_TX_M0_DEBUG` 的 Pin Number 就是 `P2_7`** ⇒ ★**我们网表 `J_SOM_P2.pin7 → UART_TX` 与官方口径【逐字一致】** ★

### 1.3 ★★官方模组表【载板调试电路】—— 一句话把 IOMUX 关系说透★★

> ★**出处**: 同上手册 · ★**章节**: ★**§3.5.5 "JTAG and UART Debug Circuits"**

★**原文抄录 (两段关键话)**:

```
The RK3572 has two JTAG multiplexes: JTAG_TCK_M0/JTAG_TMS_M0 is located in the VCCIO1 domain and is
multiplexed with SDMMC0 via the IOMUX; JTAG_TCK_M1/JTAG_TMS_M1 is located in the PMUIO1 domain and is
multiplexed with UART_Debug—UART0_M0. The IOMUX multiplexing configuration is shown in the figure below.

The UART Debug is set by default to UART0_TX_M0_DEBUG (P2_7)/UART0_RX_M0_DEBUG (P2_9). UART Debug signal
needs to be connected with 100ohm resistor in series, if plug-in is used, and TVS tube needs to be added
near the plug-in position.
```

★★**⇒ 官方口径**: ★**UART0_TX (GPIO0_D4) 与 JTAG_TCK_M1 是同一颗 pad 上的两个 IOMUX 功能 (互斥), 而 UART Debug 的【出厂默认】就是 UART0_TX_M0 (P2_7)** ⇒ ★**我们不占用 JTAG_TCK_M1 ⇒ 冲突不存在, 且连 pinmux 都不用配 (它就是默认)** ★

---

## 2. ★★★本单要的"唯一证据": 官方 IOMUX 那一行原文 (★Rockchip 侧·SoC 级真源★★)

### 2.1 ★★Rockchip 官方 datasheet —— 球位/功能对照表★★

> ★**出处 URL**: ★**`https://rockchip.fr/RK3572%20datasheet%20V1.0.pdf`** (★文件头 `RK3572 Datasheet Rev 1.0`, ★**Copyright © 2026 Rockchip Electronics Co., Ltd.**, ★**共 51 页**★)
> ★**章节**: ★**§2.6 "Pin Number List"** ⇒ ★**Table 2-1 "Pin Number Order Information"**
> ★**页码**: ★**UART0_TX / UART0_RX 两行在 p.31** (页脚 `Copyright © 2026 Rockchip Electronics Co., Ltd. 31`) · ★**GPIO0_C3 (PWM0_CH1_M0) 那行在 p.30**

★**原文抄录 (p.31, 表头 `Pin Name | Pin | Abbr`)**:

```
JTAG_TCK_M1/UART0_TX_M0/GPIO0_D4_u                         U33    GPIO0_D4
JTAG_TMS_M1/UART0_RX_M0/GPIO0_D5_u                         V32    GPIO0_D5
```

★**原文抄录 (p.30, 同一张表)**:

```
PWM0_CH1_M0/PDM_CLK1_M0/HDMI_TX_CEC_M1/SPI0_CSN1_M0/
GPIO0_C3_d                                                W33    GPIO0_C3
```

★★**⇒ 证据链闭合**: ★**Forlinx 说 P2_7 = ball U33** ⇒ ★**Rockchip 说 ball U33 = GPIO0_D4 = `JTAG_TCK_M1 / UART0_TX_M0`** ⇒ ★**两边独立官方源在【球位】这一级完全对上 ⇒ `J_SOM_P2.pin7` 就是 UART0_TX_M0 的原生脚, 【不是复用】★★

### 2.2 ★★Rockchip 官方内核仓库 —— IOMUX 的可编程侧 (★FUNC 编号的权威来源★)★★

> ★**出处 URL**: ★**`https://raw.githubusercontent.com/rockchip-linux/kernel/develop-6.12/arch/arm64/boot/dts/rockchip/rk3572-pinctrl.dtsi`**
> ★**仓库**: ★**`rockchip-linux/kernel` (Rockchip 官方内核仓库)** · ★**分支 `develop-6.12`**
> ★**文件头**: `Copyright (c) 2025 Rockchip Electronics Co., Ltd.` + ★**"This file is auto generated by pin2dts tool"** ⇒ ★**即 Rockchip 自己从 IOMUX 表生成的 pinmux 权威表**

★**原文抄录 (`uart0` 节点)**:

```dts
	uart0 {
		/omit-if-no-ref/
		uart0m0_xfer_pins: uart0m0-xfer-pins {
			rockchip,pins =
				/* uart0_rx_m0 */
				<0 RK_PD5 9 &pcfg_pull_up>,
				/* uart0_tx_m0 */
				<0 RK_PD4 9 &pcfg_pull_up>;
		};

		/omit-if-no-ref/
		uart0m1_xfer_pins: uart0m1-xfer-pins {
			rockchip,pins =
				/* uart0_rx_m1 */
				<2 RK_PA0 9 &pcfg_pull_up>,
				/* uart0_tx_m1 */
				<2 RK_PA1 9 &pcfg_pull_up>;
		};
	};
```

★**读法**: `<bank> RK_PX# <FUNC>` ⇒ ★**`GPIO0_D4` (RK_PD4) 的 FUNC 9 = `uart0_tx_m0`; `GPIO0_D5` (RK_PD5) 的 FUNC 9 = `uart0_rx_m0`** ⇒ ★**TX/RX 成对, 同 FUNC 值 ⇒ 同一组 UART0 复用方案, 合法** ★

★**本机脚本把 `rk3572-pinctrl.dtsi` 全量解析出的【这两颗 pad 的完整 IOMUX 列表】(★[实测]·脚本自跑★)**:

```
=== GPIO0_D4 (P2_7 / UART0_TX_M0 ball) full IOMUX list ===
  FUNC  9: ['uart0_tx_m0']
  FUNC 10: ['jtag_tck_m1']

=== GPIO0_D5 (P2_9 / UART0_RX_M0 ball) full IOMUX list ===
  FUNC  9: ['uart0_rx_m0']
  FUNC 10: ['jtag_tms_m1']
```

★★**⇒ `GPIO0_D4` 全pad 只有 2 个功能: `uart0_tx_m0` (FUNC9) 与 `jtag_tck_m1` (FUNC10) ⇒ 官方默认是 UART0_TX, 且我们不占 JTAG ⇒ 无冲突、无需 pinmux 配置★★

### 2.3 ★★反向补一条: 假如当初真的把 UART_TX 接到 P2_3 (GPIO0_C3), 会怎样? (★"不能复用"的那条路, 也一起交掉★)★★

★**`GPIO0_C3` (ball W33 = P2_3) 的完整 IOMUX (Rockchip 官方 dtsi, ★[实测]·全量解析★)**:

```
=== GPIO0_C3 (P2_3 / PWM0_CH1_M0 ball) full IOMUX list ===
  FUNC  6: ['pdm_clk1_m0']
  FUNC  9: ['hdmi_tx_cec_m1']
  FUNC 10: ['spi0m0_csn1']
  FUNC 12: ['pwm0m0_ch1']
```

★★**⇒ `GPIO0_C3` 的 4 个功能里【没有任何 UART】⇒ 若 (假如) 真把 UART_TX 接到 P2_3, 那是【真缺陷且不可复用】。但我们的板接的是 P2_7 ⇒ 此路不成立。★★

---

## 3. ★★BOOT 阶段副作用核对 (★brief 指定的第二问★★)

| BOOT 相关信号 | 官方座脚 | 官方 GPIO 列 | 物理性质 | 我们板用没用 | 对 UART0 有无影响 |
|---|---|---|---|---|---|
| `SARADC_VIN0_BOOT` | ★**P1_28** (ball 1AF21, 1.8V) | ★**—— (空)** | ★**专用 SAR-ADC 脚, 无 GPIO 复用功能** | ★**用了** (`J_SOM_P1.pin28 = BOOT_N`, 10k 上拉 VDD_1V8_IO + BOOT 键到 GND) | ★**无** —— 物理上不可能复用成 UART0_TX/RX |
| `PMIC_VDC` | ★**P3_10** | ★**—— (空)** | ★**专用脚, "SoM startup mode switching" (启动模式切换, 在 SoM 内部决定)** | ★**没用** (本板 J_SOM_P3 只用 57/59/63/65/69/71/75/77/81/83/87/88/91/93/95/97/98/99/100) | ★**无** —— 整条在 SoM 内部 |

★**证据**: Forlinx 手册 §2.6.2 ★**Table 2 (P1 Even) NUM=28** 与 ★**Table 6 (P3 Even) NUM=10** 两行 ★**[官网]**; 本板用脚清单 ★**[实测]** (`HW/netlist_v1_pins.csv` grep)

★★**⇒ 结论**: ★**UART0_TX/RX (GPIO0_D4/D5) 与 BOOT 链物理上零交集 ⇒ 不管是"复用"还是"直接用默认功能", 都不影响启动。brief 里"PMIC_VDC / SARADC_VIN0_BOOT 走 SARADC/ADC 脚, 不在这条 UART 链上"这句话 —— ★**[官网] 核实成立**★★

---

## 4. ★★替代脚候选 + 改板代价 (★brief 指定的第三问·虽本单不需要, 但预案交齐★)★★

★**候选全集 = Rockchip 官方 `rk3572-pinctrl.dtsi` 全量 `uart*_tx_*` (★[实测]·本机脚本扫出★)**, ★**只列 SoM 座脚上真实存在、且本板有选择空间的★★

| 候选 | RK3572 pad | SoM 座脚 | 官方默认功能 (Forlinx) | 电平 | 本板现状 | ★**改板代价** |
|---|---|---|---|---|---|---|
| ★**`uart0_tx_m0`** | ★**GPIO0_D4 (U33)** | ★**P2_7** | ★**UART0_TX_M0_DEBUG (出厂默认)** | 3.3V | ★**本板已用 = `UART_TX`** | ★**0 —— 不动** ★ |
| `uart0_tx_m1` | GPIO2_A1 (1A10) | P1_3 | SDMMC0_D1 | 1.8/3.3V | 本板未用 P1_3 | ★**高** —— 改网表+板+BOM+整链重出, 且★**牺牲 SD 卡数据线** (且 TX/RX 需成对搬到 P1_3 + GPIO2_A0) |
| ★**`uart11_tx_m1`** | ★**GPIO2_B6 (1D3)** | ★**P1_56** | ★**UART11_TX_M1_3V3 (★出厂默认本来就是 UART★)** | 3.3V | ★**本板未用 P1_56 / P1_60** | ★**低** —— 只加 2 条网络 + 1 个排针 + 100Ω×2 + TVS, ★**不用换脚、不用改 SoM 侧** ★ |
| `uart8_tx_m0` | GPIO3_C6 (AJ33) | P2_73 | UART8_TX_M0_1V8 | ★1.8V | 本板未用 P2_69/P2_73 | ★**中** —— 1.8V 域 ⇒ 需加电平转换 |
| `uart9_tx_m0` | GPIO4_B4 (AR33) | P4_21 | UART9_TX_M0_3V3 | 3.3V | 本板未用 | 中 |
| `uart10_tx_m2` | GPIO0_C4 (1T20) | P2_13 | PWM0_CH0_M0 (MIPI 背光 PWM) | 3.3V | ★**本板已用 = `KEY_VOL_P`** | ★**高** —— 要牺牲按键输入 |

★**改板代价分档 (★按 USER.md 老板关注点★)**:
- ★**本板情形 (P2_7) = 0** ⇒ ★**零改板、零返工、零板费** ⇒ ★**投板一次成功概率不受影响** ★
- ★**低档 (P1_56/P1_60 加一路 UART11)** ⇒ 只动载板一小块 + BOM 加 4 个料 (2 电阻 + TVS + 排针) ⇒ ★**不需要整链重出** ⇒ ★**★这是"将来要调试口 + 应用口两路"时的首选候选★★
- ★**高档 (换 SoM 既有脚) = 改网表 + 改板 + 改 BOM + 整链重出** ⇒ ★**2-4 周 + ¥4-8K (老板口径)** ⇒ ★**本单不走这条路★★

---

## 5. ★★顺带查出来的 3 条真发现 (★只报告, 不改设计★)

### ★★F1 [官网→实测缺口] ★★官方要求 UART Debug 串 100Ω + 插口旁加 TVS —— 我们板两条都没有 ⇒ 这是本单唯一的【真缺陷级】发现★★

- ★**[官网]** Forlinx 手册 §3.5.5 原文: ★**"UART Debug signal needs to be connected with 100ohm resistor in series, if plug-in is used, and TVS tube needs to be added near the plug-in position."** ★
- ★**[官网]** 同节 Note 原文: ★**"It is recommended to keep Q1 and Q2, which can effectively prevent the U6 current from flowing back to the CPU through UART0_TX/RX when the core board is not powered-up, affecting the startup and even causing damage."** ★
  ⇒ ★**即: 插 USB-TTL 时若 SoM 未上电, 外部驱动器的电流会经 UART0_TX 反灌进 SoM ⇒ 官方原话是"影响启动, 甚至造成损坏"** ★
- ★**[实测]** `HW/netlist_v1.csv` 里 UART 两条网络**只有**:
  - `UART_TX`: `J_SOM_P2 pin7 → J_UART pin1` + `TP_UART` 测试点
  - `UART_RX`: `J_SOM_P2 pin9 → J_UART pin2` + `TP_UART` 测试点
  - ★**全网表 grep 无任何 UART 网络上的串联电阻, 无 UART 网络上的 TVS/ESD 阵列** ★
- ★**⇒ 建议**: ★**新开一条 issue: UART_TX/UART_RX 各加 100Ω 串联 + 插口旁加 ESD/TVS 阵列 (对齐官方拓扑) ⇒ 属网表改动, 要走正常流程, ★**本单不许改网表 ⇒ 只登记, 交项目总工裁决** ★**

### ★★F2 [官网] 网表 UART 两条网络挂的 `[待原厂] TBD-01` 可以【不问任何人】直接关掉★★

- `HW/netlist_v1.csv` P8 两行标的是 `evidence=[待原厂]`, `tbd=TBD-01`, note 写 "方向 双向; 电平 3.3V [待原厂]; 阻抗 单端" ⇒ ★**方向写的是"双向"是错的** ★
- ★**[官网]** Forlinx §2.7.9 表明确: `UART0_TX_M0_DEBUG` **I/O = O (输出)**, `UART0_RX_M0_DEBUG` **I/O = I (输入)**; ★**VOL = 3.3V** (Table 3) ⇒ ★**方向应为 TX=O / RX=I, 电平 3.3V, 单端** ★
- ★**⇒ TBD-01 这条外部依赖 【不需要发信问原厂】, 用公开官网数据即可闭合** ⇒ ★**本单不改网表 (只登记)** ★

### ★★F3 [官网] 将来若要"调试口 + 应用口"两路, `P1_56 / P1_60` 是零 pinmux 成本的第二路 UART★★

- ★**[官网]** Forlinx Table 2 (P1 Even) NUM=56/60 ⇒ 官方默认功能就是 `UART11_TX_M1_3V3` / `UART11_RX_M1_3V3` ⇒ ★**连 pinmux 都不用配, 出厂默认就是 UART** ★
- ★**[实测]** 本板 J_SOM_P1 只用 28/32/36/38/54/64/80/92/94/100 ⇒ ★**P1_56 / P1_60 空着** ★
- ★**⇒ 代价 = 载板加 2 条网络 + 1 个排针 + 100Ω×2 + TVS ⇒ 不动 SoM 侧, 不换脚, 不整链重出** ★

---

## 6. ★★本单零改动自证 (md5 实测)★★

★**[实测]** 本单开工前 / 交卷时各测一次:

```
$ md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv
611b869e13518c3c023fb178f91a0075  HW/PCB/demo_mainboard.kicad_pcb
c78f991283cc82d56c8e3dd31657c785  HW/netlist_v1.csv
```

★**⇒ 板 md5 = `611b869e13518c3c023fb178f91a0075` ✔ (与 brief 要求一致) · 网表 md5 = `c78f991283cc82d56c8e3dd31657c785` ✔** ⇒ ★**本单只出文档, 设计侧零字节改动** ★

★**本单实际写入的文件 (★全部在允许边界内★)**:
1. ★**`HW/PCB/RK3572_UART0_TX_PINMUX_VERDICT.md`** (★本文件·新增★)
2. ★**`HANDOFF/2026-11-15_hw-lead_ISS204_UART0_TX_pinmux核.md`** (★交卷报告·新增★)
3. ★**`state/fragments/hw.yaml`** (★走 `state/frag_write.py` 原子写, ★**只新增本单相关条目**★)

★**本单【没碰】的文件 (★逐个点名, 供复核★)**: `HW/netlist_v1.csv` · `HW/netlist_v1_pins.csv` · `HW/PCB/demo_mainboard.kicad_pcb` · `HW/PCB/demo_mainboard*.kicad_sch` · `state/gen_kicad_sch.py` · `HW/PCB/FET3572C_PIN_TABLE.csv` · `HW/PCB/PIN_REALITY_GAP.md` · `state/issue_log.yaml` · `PROJECT_TRACKER.md` · `sw.yaml` / `mech.yaml` / `pm.yaml` ⇒ ★**全部未动** ★

---

## 7. ★★要项目总工落账的 3 件订正 (★本单不许改, 列出来★★)

| # | 文件 | 位置 | 现状 (错) | 应为 |
|---|---|---|---|---|
| ★**①** | `HW/PCB/RK3572_SOM_BALLTABLE_CROSSCHECK.md` | §3 发现 A | "★**官方**: `P2_7` = `PWM0_CH1_M0` / GPIO0_C3_d / 3.3V" | ★**`P2_7` = `UART0_TX_M0_DEBUG` / GPIO0_D4_u / U33; `PWM0_CH1_M0` 是 `P2_3` (W33)** ★ |
| ★**②** | `HW/PCB/PIN_REALITY_GAP.md` §5.1 | 那句 "待核: `P2_7` 官方默认功能是 `PWM0_CH1_M0`, 我们拿它当 `UART_TX` 用 ⇒ 这是【引脚复用】, 需用官方 pinmux 表交叉核" | 同上错 | ★**该文件是 `state/gen_kicad_sch.py --pin-gap` 的产物 ⇒ 要改必须在【生成器】里改, 不能手改产物 ⇒ ★**本单不许动生成器 / 也不许重跑 ⇒ 留给项目总工** ★ |
| ★**③** | 同上 | ISS-204 的 need 条目 | "待 hw-lead 用官方 pinmux 表交叉核" | ★**已核完: 不用复用, P2_7 出厂默认就是 UART0_TX_M0_DEBUG ⇒ need 可关** ★ |

★**自查**: 我们自己的表本来是对的 ⇒ ★**`HW/PCB/FET3572C_PIN_TABLE.csv` 行 `P2,7,U33,UART0_TX_M0_DEBUG,GPIO0_D4_u,3.3V,UART0 send (Debug Serial Port),UART0_TX_M0_DEBUG` ✔** · ★**`HW/PCB/SOM_PIN_VERIFY.md:96` 已写 `UART0_TX_M0_DEBUG | P2_7` ✔** ⇒ ★**错位只在 `RK3572_SOM_BALLTABLE_CROSSCHECK.md` 这一处人写的文档里, 不在数据里** ★

---

## 8. ★★查不到的项 + 降级方案 (★按纪律: 查不到就写 [0数据], 不许猜★★)

| 查不到的项 | 等级 | 已知缺口 | 降级方案 |
|---|---|---|---|
| ★**Forlinx "FET3572-C SoM Pin Multiplexing Comparison Table"** | ★**[0数据]** | 官方手册 Overview 明写 "For information on pin function multiplexing and hardware design guidelines, please refer to Forlinx's 'FET3572-C Pin Multiplexing Comparison Table'" ⇒ ★**该文件在 Forlinx 下载区需登录/注册后获取, 公开直链取不到** | ★**已用两份更强的一手源替代**: ★**① Rockchip 官方 datasheet §2.6 Table 2-1 (SoC 级真源, 含全 pad 功能串) ② Rockchip 官方内核 `rk3572-pinctrl.dtsi` (IOMUX FUNC 编号权威)** ⇒ ★**结论等价且更强 (Forlinx 那份是模组级裁剪视图) ⇒ 不影响本单结论**; ★**若将来真要全量 pinmux 表, 拿到这份可补, 但本项目不需要** ★ |
| ★**本板 UART0_TX/RX 的实际波形 / 反灌实测** | ★**[0数据]** | ★**本单无实板, 不测, 不猜** | ★**按 F1 用官方拓扑规避 (100Ω 串阻 + TVS + SoM 未上电时不让外部驱动) ⇒ 官方给的就是规避手段, 不是要实测** ★ |
| ★**`GPIO0_D4_u` 后缀 `_u` 的准确定义** | ★**[推算]** | ★**两份官方件互证**: Forlinx §3.5.5 "JTAG_TCK_M1/JTAG_TMS_M1 is located in the **PMUIO1 domain**" + datasheet p.31 `GPIO0_D4_u = JTAG_TCK_M1 / UART0_TX_M0` ⇒ ★**⇒ `_u` ≈ PMUIO1 域 (3.3V), `_d` ≈ VCCIO 域, `_z` ≈ ?** | ★**不影响结论** (电平已由 Forlinx Table 3 的 VOL 列直接给 3.3V) ⇒ ★**标 [推算] 即可, 不下断言** ★ |

---

## 9. ★★本次用到的源 (★全部公开可复核★★)

| 源 | 用途 | 等级 |
|---|---|---|
| ★**`https://rockchip.fr/RK3572%20datasheet%20V1.0.pdf`** (RK3572 Datasheet Rev 1.0, ★51 页, © 2026 Rockchip) | ★**§2.6 Pin Number List / Table 2-1: ★p.31 `JTAG_TCK_M1/UART0_TX_M0/GPIO0_D4_u  U33  GPIO0_D4` + `JTAG_TMS_M1/UART0_RX_M0/GPIO0_D5_u  V32  GPIO0_D5`; ★p.30 `PWM0_CH1_M0/.../GPIO0_C3_d  W33  GPIO0_C3`** | ★**[官网]** |
| ★**`https://raw.githubusercontent.com/rockchip-linux/kernel/develop-6.12/arch/arm64/boot/dts/rockchip/rk3572-pinctrl.dtsi`** (Rockchip 官方内核仓库) | ★**`uart0` 节点: `uart0_tx_m0 = <0 RK_PD4 9>` / `uart0_rx_m0 = <0 RK_PD5 9>`; ★GPIO0_C3/D4/D5 全量 IOMUX 扫描** | ★**[官网]** |
| ★**`https://docs.forlinx.net/rockchip/ok3572-c/OK3572-C_User_Hardware_Manual.html`** (User's Hardware Manual V1.0, 15/06/2026) | ★**§2.6.2 Table 3 (P2 Odd) NUM=7/9/3 三行原文; §2.7.9 UART 按功能表 (P2_7); §3.5.5 JTAG+UART Debug 电路原文 (含 100Ω / TVS / 反灌告警); §2.6.2 Table 2 (P1 Even) NUM=28 SARADC_VIN0_BOOT; Table 6 (P3 Even) NUM=10 PMIC_VDC** | ★**[官网]** |
| ★**`https://www.forlinx.net/download/FET3572-C-SoM-OK3572-C-SBC-Product-Brief.pdf`** | ★**交叉印证 "Hardware Documentation 清单含 Pin Multiplexing Comparison Table"** | ★**[官网]** |
| ★**本机实测**: `HW/netlist_v1.csv` · `HW/netlist_v1_pins.csv` · `HW/PCB/FET3572C_PIN_TABLE.csv` · `md5sum` · ★**自写解析脚本扫 `rk3572-pinctrl.dtsi` 全量 IOMUX** | ★**用脚清单 / UART 网络连接关系 / 缺 100Ω+TVS 缺口 / md5 未变 / IOMUX 全表** | ★**[实测]** |

★**本地留档 (★外部下载物, 按项目惯例【不进仓】★)**: `/tmp/rk3572_ds.pdf` (2,443,541 B) · `/tmp/rk3572_ds.txt` (pdftotext -layout 提取) · `/tmp/rk3572-pinctrl.dtsi` (111,730 B) · `/tmp/ok3572_manual.html` (351,453 B) ⇒ ★**仓里只留本文件这个结论 + 源 URL + 页码** ★

---

> ★**页脚**: ★**ISS-204 交卷 · 硬件总工 (hw-lead) · 2026-11-15** · ★**板 md5 `611b869e13518c3c023fb178f91a0075` / 网表 md5 `c78f991283cc82d56c8e3dd31657c785` 未变** · ★**未发任何邮件 · 未联系任何原厂/供应商 · 未下任何采购单** · ★**issue 状态由项目总工落账, 本单未碰 `state/issue_log.yaml`** ★
