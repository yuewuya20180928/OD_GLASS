# ★★ISS-174 交卷报告 —— demo 触控中断 (TP_INT) 改脚规格 (★判定: (c) 部分成立·本板不接·但预留脚现在就得钉死★)★★

> ★**日期**: 2026-11-15 · ★**执行**: 硬件总工 (hw-lead) · ★**单号**: ISS-174 · ★**owner**: hw-lead · ★**verify_by**: main
> ★**详情文档**: ★**`HW/PCB/TP_INT_REMAP_SPEC.md`** (证据原文全文在那份) · ★**门禁**: ★**`HW/check_tp_int_gap.py`** (rc=0 / `--selftest` 5/5)

---

## ★B1. 结论 (★一句话★★)★★
★★**ISS-174 的前提已过期: 现行屏座 `CONN_LIGHT` (22p, Waveshare 2.8") 官方规格 "Touch Port = I2C" ⇒ 触控由屏内 MCU @0x45 处理, 座上既无触控中断脚也无屏复位脚 ⇒ `NET_TP_INT` 在网表里 0 命中 (不是"没接 SoM", 是"这条线压根没画") ⇒ 判定 (c) 部分成立: issue 主体三条断言全不成立, 只有前瞻残项 R1 成立 (SoM 侧无预留脚) ⇒ 本板 0 网表改动 / 0 原理图改动 / 不改板 / BOM 不变, 但★**现在就把 SoM 侧预留脚钉死 = `J_SOM_P4 pin62` (GPIO2_D7_z, ball B7)****★★

| ★**判定项** | ★**结论 + 行号级证据** |
|---|---|
| ① `NET_TP_INT` 存不存在 | ★**不存在** — `grep -n "TP_INT" HW/netlist_v1.csv` (514 行) ⇒ 0 命中; `netlist_v1_pins.csv` (585 行) ⇒ 0 命中; 板文件里只有 `property "Reference" "TP_RESET"` (测试点封装位号, `demo_mainboard.kicad_pcb:11964`) |
| ② 触控归谁管 | ★**归屏内 MCU, 走 I2C_B** — `netlist_v1.csv:248/249` (pin11/12 = 屏控制 I2C, 屏内 MCU @0x45); Waveshare 官方规格 **Touch Port I2C** (`WAVESHARE_2P8_INIT_AND_BACKLIGHT.md:262`); Pi5 官方 overlay `vc4-kms-dsi-waveshare-panel.dtbo` 内 `panel_disp1@45` + 触摸 GT911 @0x14 (`:430`) ⇒ **SoM 侧不需要 TP_INT** |
| ③ `TP_RESET` 现行是什么 | ★**是测试点位号, 挂在 `RESET_N` (SoM 自身复位链) 上, 与屏无关** — `netlist_v1.csv:366` + `netlist_v1_pins.csv:489`; 链: `R_PU_RESET_N` 10k + `R_SER_RESET_N` 1k + `C_RST` 100nF + `SW_RST` + `Q_AND` ⇒ 末级到 `J_SOM_P2 pin100` |
| 根因 | issue 提于 **2026-11-03 换屏之前** (屏 = Radxa 8HD 39p, 其 pin26=TP_INT / pin24=TP_RESET — `DISPLAY_39P_PINOUT.md:71/73/123/125`); **2026-11-04 换成 Waveshare 2.8" 22p 后整表作废** (`FPC_PIN_TABLES.md` 末段) ⇒ ★**老 issue 描述漂移, 没跟着清** |

## ★B2. `CONN_LIGHT` 22 脚落点全表 (★触控不在这个座上·全 22 脚都有主★★) ★
`netlist_v1_pins.csv:36..57` ⇒ **8×GND + 2×LIGHT_3V3 + 2×I2C_B(SCL/SDA) + 10×DSI 差分** (D0_CK/D0/D1/D2/D3 各 P/N) ⇒ ★**无触控脚 / 无复位脚 / 无空脚**; pin16..22 虽是 Pi5 侧 **NC** (`PI5_DSI_22P_PINOUT.md` §2 证据 P1: "16..30 标红叉 NC"), 但**官方线缆里也是 NC ⇒ 线缆那头没导体 ⇒ 接不了屏侧 TP_INT**。

## ★B3. SoM GPIO 候选脚表 (★每个都有官方功能名 + 官方 IOMUX + 占用证据, 无一只靠"看起来空着"★) ★
**池算法**: `FET3572C_PIN_TABLE.csv` ∧ gpio 真实 ∧ vol 含 3.3V ∧ desc 无 "not available" ∧ 未在 `som_pin_assign.json` assign/fixed ∧ 网表 0 命中 ⇒ **36 只 (P4=22 / P1=13 / P2=1 / P3=0, P3 全 1.8V 域)**。

| ★**#** | ★**SoM 脚** | ★**ball** | ★**官方 GPIO** | ★**官方出厂默认功能 (datasheet 原文)** | ★**出处** | ★**IOMUX (官方内核) ⇒ 可否 GPIO 输入** | ★**占用** | ★**几何** |
|---|---|---|---|---|---|---|---|---|
| 1 | ★**J_SOM_P4 pin62 ★主选★** | `B7` | `GPIO2_D7_z` | `ETH0_RXCLK/GPIO2_D7_z` | ds **p.27** | bank2 `RK_PD7` F1:`eth0_rxclk` F2:`fspi1m1_csn1` F3:`fspi1_rst` …共10条 ⇒ **FUNC0 未列=GPIO 复位 ⇒ 零 pinmux 输入** | 网表 **0 命中** | 到屏座 **6.41 mm** · 走廊铜箔 **83 段 (最低)** |
| 2 | J_SOM_P4 pin60 | `A10` | `GPIO2_C7_d` | `ETH0_RXCTL/GPIO2_C7_d` | ds p.27 | bank2 `RK_PC7` F1:`eth0_rxctl` …共11条 | 0 命中 | 6.3 mm / 106 段 |
| 3 | J_SOM_P4 pin58 | `1D6` | `GPIO2_D2_d` | `ETH0_RXD0/GPIO2_D2_d` | ds p.27 | bank2 `RK_PD2` F1:`eth0_rxd0` …共10条 | 0 命中 | 6.22 mm / 133 段 |
| 4 | J_SOM_P4 pin56 | `A7` | `GPIO2_D1_d` | `ETH0_RXD1/GPIO2_D1_d` | ds p.27 | bank2 `RK_PD1` F1:`eth0_rxd1` …共12条 | 0 命中 | 6.16 mm / 162 段 |
| 5 | J_SOM_P4 pin54 | `1B4` | `GPIO2_C1_d` | `ETH0_RXD2/GPIO2_C1_d` | ds p.26 | bank2 `RK_PC1` F1:`eth0_rxd2` …共9条 | 0 命中 | 6.12 mm / 193 段 |
| 6 | J_SOM_P4 pin52 | `1C4` | `GPIO2_C0_d` | `ETH0_RXD3/GPIO2_C0_d` | ds p.26 | bank2 `RK_PC0` F1:`eth0_rxd3` …共7条 | 0 命中 | 6.11 mm / 202 段 |
| 7 | J_SOM_P4 pin39 | `1T22` | `GPIO0_C6_d` | `I2C3_SCL_M1_3V3/GPIO0_C6_d` | ds p.25 | bank0 `RK_PC6` F11:`i2c3_scl_m1` | 0 命中 | 9.19 mm / 351 段 |
| 8-9 | P4 pin29 / pin31 | `1A2`/`1D2` | `GPIO2_B1_d`/`GPIO2_B3_d` | `CAN0_TX_M2`/`CAN0_RX_M2` | ds p.26 | bank2 `RK_PB1`/`RK_PB3` | 0 命中 | 9.19 mm / 532·474 段 |
| 10-11 | P4 pin5 / pin7 | `B10`/`B9` | `GPIO2_C5_d`/`GPIO2_C6_d` | `ETH0_MDIO`/`ETH0_MDC` | ds p.27 | bank2 `RK_PC5`/`RK_PC6` | 0 命中 | 9.19 mm / 432·417 段 |
| 12-13 | P1 pin56 / pin60 | `1D3`/`A4` | `GPIO2_B6_d`/`GPIO2_B7_d` | `UART11_TX_M1`/`UART11_RX_M1` | ds p.26 | bank2 `RK_PB6`/`RK_PB7` | 0 命中 | ★**54.1 mm (几何最差)** · ISS-204 的 F3「零 pinmux 第二路 UART」⇒ 留给它 |

★**判据②明令排除**: `P4_4`(TYPEC0_PWREN)/`P4_9`(MIPI_DSI1_RESET)/`P4_33`+`P4_35`(PWR_EN)/`P4_37`(PCIE CLKREQN)/`P1_74`+`P1_76`(PCIE WAKEn)/`P1_3/5/7/9/11/13`(SDMMC0 = **BOOT 链**)/`P2_3`(M.2_PWR_EN)/`P2_5`(Forlinx 官方 **"Occupied by the SoM and not available."**)/`P2_19`+`P2_21`+`P2_79`+`P2_75`(**1.8V 域** + INT/RESET/DSI-EN/TYPEC-INT) ⇒ 全 20 只逐条列名在 `TP_INT_REMAP_SPEC.md` §3.3。

★**最强反驳的正面回答 (评审必问)**: 「OK3572-C **载板**把 ETH0 用了, P4_38..P4_62 还能当 GPIO 吗?」⇒ ★**能**: ① 手册**第 2 章 = FET3572-C SoM 章**, §2.6 "FET3572-C **SoM** Pin Definition" ⇒ **P1..P4 是 SoM 自己的 100 脚座**, 不是载板的脚; ② 手册 §2.7.11 "Ethernet Interface Control Pins" 逐脚原文 `GMAC0_RXCLK_M0 → **P4_62**` / `GMAC0_RXD3/RXD2/RXD1/RXD0 → P4_52/54/56/58` / `GMAC0_TX* → P4_38..48` / `GMAC0_MDC/MDIO → P4_7/P4_5`; ③ ★**PHY + 双 RJ45 在 OK3572-C 载板上** (手册 §3.5.10 "The **carrier board** supports dual 1000/100/10M Ethernet interfaces, which are led out via RJ45") ⇒ ★**我们用自研主板替掉载板 ⇒ 这 14 个球位在主板上就是空脚**; ④ 手册 §2.8.1 原文 "**Unused signal pins on the core board can be left floating**, but all GND connections must be properly established" ⇒ 官方明确允许留空另作他用; ⑤ SOM 自带能力清单 (`SOM_BUILTIN_CAPABILITY.md` A1..A8) **无以太网 PHY** ⇒ ball B7 在 SOM 上未被驱动 ⇒ ★**电气上成立**。

## ★B4. 规格摘要 (★照着做就能改; 本单一个字节都没改★) ★
★**本板 (现在)**: 改网 **0 行** / 改原理图 **0 页** / 板 **不动** / BOM **不变** ⇒ **不需要跑整链重出**, 只跑门禁。
★**前瞻 (光机换到带 TP_INT 的屏, ISS-156 落定 Radxa 8HD/10FHD 40p 时)**: ① 新增 1 个网 **`TP_INT`** (★不带 `NET_` 前缀 — 现行 `NET_*` 是轨/伪件名约定, 纯信号网例: `I2C_B_SCL`/`CAM_RESET_N`); ② SoM 侧 → **`J_SOM_P4 pin62`**; 屏侧 → 新 40p 座 **pin26** (★座 ref 待 ISS-156); ③ 网表 CSV **加 2 行** (`page` 列必须写 **`P4`**), 模板见 `TP_INT_REMAP_SPEC.md` §4.3 (`conn_id` 用显示段唯一空号 **`A-23`**); ④ 原理图 **P4 显示页** (屏侧引出线 + `global_label "TP_INT"`) + **P1 电源页** (J_SOM_P4 侧, ★J_SOM_P1..P4 四座全画在 P1, 规则见 `gen_kicad_sch.py:145-190`) ⇒ ★**跨页用 `global_label`, 样板照抄 `I2C_B_SCL`** (实测 `p1.kicad_sch:3369` + `p4.kicad_sch:567/643`); ⑤ 板侧: **只动屏侧那一块** (换 22p/0.5mm → 39p/0.3mm 座) ⇒ ★**SoM 侧零改动 = 本单先钉死 pin62 的全部理由**; ⑥ **BOM 不变**; ⑦ **上拉**: 用 SoM pad 内部弱上拉 (Rockchip ds p.41 `RRPU` 10~100 kΩ @3.3V + `IRPU` ≤180 µA; 官方内核 `pcfg_pull_up { bias-pull-up; }`; Forlinx 手册 "All GPIOs can be used to generate interrupts") ⇒ 最坏 100 kΩ 时高电平 ≈2.3 V > VIH 2.1 V ✔ ⇒ **不加电阻进 BOM**; 降级 = 若实测上升沿慢 ⇒ 改外部 10k 上拉 (须另开变更单)。

## ★B5. 复现命令 + 输出 (★交卷前实跑★★) ★
```
$ python3 HW/check_tp_int_gap.py             # ✅ rc=0  现状与规格一致
$ python3 HW/check_tp_int_gap.py --selftest  # ✅ rc=0  自检 5/5 (假占用/假TP_INT网/pin22改网/备选脚被占 全被抓)
$ python3 state/check_netlist.py             # rc=0 (未变红)
$ python3 state/check_netlist_pins.py        # rc=0 (未变红)
$ python3 state/merge.py                     # rc=0
$ python3 state/gate_check.py                # rc=0, 【Q1】18/18
$ md5sum HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/PCB/demo_mainboard.kicad_pcb HW/PCB/som_pin_assign.json
c78f991283cc82d56c8e3dd31657c785  HW/netlist_v1.csv      ★与期望一致 (开工前=交卷后)
4814617e22b567d76164e56bc5e39dc8  HW/netlist_v1_pins.csv ★与开工前一致
611b869e13518c3c023fb178f91a0075  HW/PCB/demo_mainboard.kicad_pcb ★与期望一致 (开工前=交卷后)
800d08d4451fee46c180815d8badc21c  HW/PCB/som_pin_assign.json ★与开工前一致
```
★**零外发** (无邮件/询价/采购/原厂问询) · ★**实物 [实测] = 0 条** (无实板) · ★**[0数据] 6 项 + 降级方案** 见 `TP_INT_REMAP_SPEC.md` §6 (TP_RESET 的 SoM 脚未预选 / 新座机械落位 / pad 内部上拉 typ 值 / GT911 INT 电气 / 载板层外部上下拉 / 39p↔40p 针序合并) · ★**未碰**: 网表/引脚表/板/原理图/som_pin_assign.json/任何 gen_*.py/任何既有 check_*.py/issue_log.yaml/SW/MECH/outbox · ★**只新增 3 个文件** + `state/fragments/hw.yaml` 一条登记 (走 `frag_write.py`)。
★**建议 main 落账**: ISS-174 按 §1.6 措辞改写为「**SoM 侧预留给屏侧触控中断的 GPIO (前置选型占位)**」; 状态改动是 main 的活, 本单未碰 `state/issue_log.yaml`。
