# RK3572 GPIO0 → VCCIO 供电组 · 官方映射自查结论 (ISS-228)

> ★**owner**: sw-lead (软件/工具链侧总工) · ★**单号**: ISS-228 · ★**日期**: 2026-11-16
> ★**上游**: ★**`state/fragments/hw.yaml` 里挂着的一条跨域 need `iss148_rk3572_gpio0_vccio_domain_check`** (to=sw-lead, since 2026-11-02, due 2026-11-03 ⇒ ★**逾期 13 天**★) ⇒ ★**本单就是去接掉它** ★
> ★**证据等级定义 (★全单统一, 一个词都不许混用★)**: ★**`[官网]`** = 官方文档原文 (Rockchip datasheet / Rockchip 官方内核 / Forlinx 官方手册) · ★**`[实测]`** = ★**本机脚本 / 本机文件实读** (★板与屏不在本机 ⇒ 板端实测 = 0 条★) · ★**`[推算]`** = 由已核事实做的推导 (★方法写明★) · ★**`[0数据]`** = 查不到 ★
> ★**边界**: ★**本单没改** `HW/` 下任何文件 · ★**没改** `MECH/` 下任何文件 · ★**没改** `state/issue_log.yaml` / `PROJECT_TRACKER.md` §0 / `DECISION_PENDING_2026-11-16.md` / `state/outbox/` / 别人的分片 · ★**没碰** PCB 布线/布局/板框 · ★**零外发** · ★**没自签 issue_log** ★

---

## ★0 一句话结论 (★先看这条★)

★★**I2C_A 上拉最终必须是 1.8V (2.2kΩ) —— 这个结论现在有 `[官网]` 级依据了, 不再是拍脑袋; 而且 ★★它不是"退而求其次", 是唯一正确答案★★** ★

★**但本单查出的真正价值不在"确认 1.8V", 而在于 ★★把这条 need 的 ★前提错误★ 当场揪出来★★**:

| # | ★**原 need 的前提 (★转述自 `state/fragments/hw.yaml` L1124-L1133 与 `HW/AR0234CS_OPEN_SOURCE_FACTS.md` L241 / L474★)** | ★**本单核查结论** | ★**等级** |
|---|---|---|---|
| ① | ★**"I2C0_SCL = GPIO0_B0 (球 1K21) / I2C0_SDA = GPIO0_B1 (球 U32) ⇒ 这两根脚挂哪个 VCCIO 组 ⇒ ★I2C_A 上拉最终是 1.8V / 2.8V / 3.3V"** ★ | ★**前提错**: ★**本板 I2C_A 根本不接在 I2C0 / GPIO0_B0 / GPIO0_B1 上!** ★★本板 I2C_A 走 SoM **P2_31 / P2_33** ⇒ 官方 Forlinx 手册 §2.6.2 = **I2C5_SCL_M3 / I2C5_SDA_M3 = GPIO3_C4 (球 AH33) / GPIO3_C1 (球 AL33)**, ★**不是 I2C0**★ ⇒ ★**"I2C0 挂哪组" 这个问题对 I2C_A ★【无因果关系】★ ⇒ 原 need 的 "3.3V/2.8V 会超 SoC 侧 abs-max ⇒ 整条 I2C_A 要重新设计" 这条推论链 ★**从根上就不成立**★** ★ | ★**`[官网]`** (★Forlinx OK3572-C 官方手册 §2.6.2 Table 4 逐格转录 + 本机实读 `HW/PCB/FET3572C_PIN_TABLE.csv` L132/L134★) |
| ② | ★**"GPIO0 组紧跟 VCCIO1_VCC ⇒ 若 VCCIO1_VCC 属 1.8V only ⇒ SoC 侧 GPIO0 只允许 1.98V"** ★ | ★**推论链断在第 2 环**: ★**VCCIO1_VCC ≠ GPIO0 的供电网** ★ ⇒ ★**GPIO0_A0…B3 属 PMUIO0_VCC1V8, GPIO0_B4…D5 属 PMUIO1_VCC** ★ ⇒ ★**GPIO0 这一个 bank ★被两个不同的 VCCIO 组劈开了★** ⇒ ★**"GPIO0 → 某一个 VCCIO 组" 这个提问方式本身 ★就是错的★ ★ | ★**`[官网]`** (★Rockchip RK3572 Datasheet Rev 1.1 §2.6 引脚表 + §3.1/§3.2 电源域表★) |
| ③ | ★**"datasheet 没有 GPIO bank → VCCIO 组的对应表 ⇒ 只能靠引脚表顺序推断 ⇒ 不能当结论"** ★ | ★**这句 ★【对】但 ★【结论过头了】★**: ★**datasheet 确实没有一张"bank→VCCIO"表, 但 §2.6 引脚表本身 ★就是按供电域分组排的★** ⇒ ★**顺序不是"乱序猜测", 是 ★官方排版语义★** ⇒ ★**本单把这条 ★从"不能当结论" 升级成 "[官网] + 三重交叉验证"★** ★ | ★**`[官网]`** + ★**`[实测]`** (★本机解析 109 个可比球位, 108/109 与 SoM 官方 VOL 列一致★) |
| ④ | ★**"⇒ 这条不核, U2 (AR0234CS) 的最终改法不能定稿"** ★ | ★**可以定稿了**: ★**I2C_A 上拉 = 1.8V / 2.2kΩ (已落表, 见 §4) ⇒ AR0234CS 若上, VDD_IO 必须走 1.8V (Note 19.2 允许 VDD_IO 与 VDDIO_PHY 并轨 when 1.8V) ⇒ ★**顺带解掉 "VDDIO_PHY 缺轨" 那条硬伤**★ ⇒ ★**U2 的最终改法 ★可以定稿★** ★ | ★**`[官网]`** (★onsemi AR0234CS datasheet Note 10 / Note 19.2 / Table 13, 已在 `HW/AR0234CS_OPEN_SOURCE_FACTS.md` 内★) |

---

## ★1 检索面清单 (★查了哪些官方源, 一个不漏★)

| # | ★**官方源** ★ | ★**URL / 路径** ★ | ★**本机取得的什么** ★ | ★**等级** ★ |
|---|---|---|---|---|
| S1 | ★**Rockchip RK3572 Datasheet Rev 1.1** (★项目库内官方 PDF, ★不是网上下载的★) ★ | `HW/RK3572_PIN_TABLE/RK3572_datasheet_V1.1.pdf` (★2,414,580 B★) | ★**§2.6 引脚表 (p.22-p.29, Table 2-1 "Pin Number Order Information")** ★ + ★**§3.1 Table 3-1 Absolute Ratings + §3.2 Table 3-2 Recommended operating conditions (p.39)** ★ + ★**§3.3 Table 3-3 DC Characteristics (p.41)** ★ | ★**`[官网]`** ★ |
| S2 | ★**Rockchip 官方内核 `develop-6.12`** ★ `rk3572-pinctrl.dtsi` ★ | `raw.githubusercontent.com/rockchip-linux/kernel/develop-6.12/arch/arm64/boot/dts/rockchip/rk3572-pinctrl.dtsi` (★111,730 B★) | ★**545 条 `rockchip,pins` 复用组, 但 ★【全文 0 处】出现 VCCIO/PMUIO 网名 ⇒ 本路 [0数据]★** ⇒ ★**它只给 "bank 号 + pad 号 + 复用功能", 不含 IO 域电压★** | ★**`[0数据]`** (★本路无果★) |
| S3 | ★**Rockchip 官方内核 `develop-6.12`** ★ `rk3572.dtsi` + `rk3572-evb.dtsi` + `rk3572-evb1-v10.dtsi` + `rk3572-linux.dtsi` + `rk3572s.dtsi` ★ | 同上仓库同分支 | ★**★5 个 dtsi 全查完: ★【0 个】含 `io-domains` 节点 / ★【0 个】含 `domain-supply` / ★【0 个】含 `vccio` 网名★ ⇒ ★**RK3572 在官方 BSP 里 ★【没有可用的 io-domain 节点】★ ⇒ ★**本路 [0数据]★** | ★**`[0数据]`** (★本路无果★) |
| S4 | ★**上游 Linux `torvalds/linux`** `rk3572.dtsi` / `rk3572-pinctrl.dtsi` ★ | `raw.githubusercontent.com/torvalds/linux/master/arch/arm64/boot/dts/rockchip/` | ★**★404 —— 上游 mainline ★【还没有】RK3572 的 dtsi★ (★只有 RK3576 的★) ⇒ 本路 [0数据]★** | ★**`[0数据]`** (★本路无果★) |
| S5 | ★**Rockchip 官方 IO-domain 驱动** `drivers/soc/rockchip/io-domain.c` (★`develop-6.12`★) ★ | 同上仓库 | ★**★该驱动只 support `rockchip,rk3568-pmu-io-voltage-domain`; ★【没有】RK3572 条目 ⇒ 本路 [0数据]★** ⇒ ★**⇒ RK3572 的 IO 域电压 ★【不是软件可配的】★ ⇒ ★**它由 ★【硬件供电轨】★ 决定 ⇒ ★【必须查 SoM / 载板手册】★ —— 这 ★★反过来证明 S6/S7 才是正解★** | ★**`[0数据]`** (★本路无果★) |
| S6 | ★**Forlinx OK3572-C 开发板官方手册** (★FET3572-C SoM + 载板, ★V1.0 / 2026-06-15★) ★ | `docs.forlinx.net/rockchip/ok3572-c/OK3572-C_User_Hardware_Manual.html` (★351,453 B 全文抓取★) | ★**§2.6.2 Table 1-8 = SoM 399 个连接器脚 (NUM/BALL/Signal Name/GPIO/★VOL★/Pin Description/Default Function) —— ★含 ★每脚的官方电平 VOL 列★** ★ + ★**§3.5.4 / §3.5.5.1 = ★官方明文写 "JTAG_TCK_M0/JTAG_TMS_M0 is located in the ★VCCIO1★ domain" 与 "JTAG_TCK_M1/JTAG_TMS_M1 is located in the ★PMUIO1★ domain"★ ⇒ ★★这是本单最硬的 ★【官方 bank→VCCIO 归属声明】★★ ★** | ★**`[官网]`** ★ |
| S7 | ★**Forlinx FET3572-C 载板 (OK3572-C) 电源与信号表** (★同上手册 §2.7 / §3.5 / 载板侧 GPIO 电压列★) ★ | 同上 | ★**载板侧逐脚电平 (★例: P2_71 = 球 1AE21 = HDMI_TX_HPDIN_M0 / GPIO4_B1_d / ★1.8V★) ⇒ 与 §2.6.2 的 VOL 列一致 ★** ⇒ ★**SoM 侧与载板侧电平 ★【自洽】★** | ★**`[官网]`** ★ |
| S8 | ★**Rockchip RK3576 Brief Datasheet + Forlinx OK3576-C 手册** (★同代兄弟芯片, 作旁证★) ★ | `rock-chips.com/uploads/pdf/2024.3.18/192/RK3576%20Brief%20Datasheet%20V1.2-20240311.pdf` · `docs.forlinx.net/rockchip/ok3576-c/...` | ★**RK3576 手册同款写法: "SDMMC0_DET_L … Determines whether the ★VCCIO1★ power domain I/O is configured for SDMMC0 or JTAG" ⇒ ★**证明 "某某脚在 VCCIO 几域" 是 ★Rockchip/Forlinx 官方文档的 ★标准表述法★ ⇒ ★**本单用同法读 RK3572 是合规的★** ★ | ★**`[官网]`** (★旁证★) |
| S9 | ★**项目内已有官方转录**: `HW/PCB/FET3572C_PIN_TABLE.csv` (★399 行 = S6 §2.6.2 的 8 张表 ★逐格转录★) ★ | 项目库内 | ★**★本单用本机脚本把它与 S1 的引脚表逐球对账 ⇒ 109 个可比 GPIO 球位里 108 个与 datasheet 解析一一对上 ⇒ ★**这份项目内转录是 S6 官方表的忠实副本, 可直接当 `[官网]` 用★** ★** | ★**`[官网]`** (★经 `HW/PCB/RK3572_SOM_BALLTABLE_CROSSCHECK.md` §1 官方逐格零差异核对背书★) |

★★**★本单 ★零外发★ (★不发邮件 / 不询价 / 不问询 / 不采购★) ⇒ 全部缺口都是"自己网上查" + 标证据等级 + 查不到写降级方案 ⇒ ★**S2/S3/S4/S5 四路全 [0数据] 是"自己查完确实没有", 不是"等原厂回信"★** ★★

---

## ★2 逐源结论 (★每源写清: 查了什么 ⇒ 得到什么 ⇒ 等级★)

### ★2.1 S1 (Rockchip RK3572 Datasheet Rev 1.1) ⇒ ★**引脚表按供电域分组, 这是官方排版语义★** ★

★★**★关键发现: §2.6 "Pin Number List / Table 2-1 Pin Number Order Information" 这张表 ★不是乱序的 —— 它是 ★【按 IO 供电域分组】★排的, 每组的末尾紧跟该组的供电网名那一行 (Abbr 列 = `-`)★** ★

★**本机用 `pdftotext -layout` 抽出带列对齐的表 (★所以能拿到 Ball 列 + Abbr 列, 而不是扁平串★), 逐行扫描, 规则 = "**某个 GPIO 行的归属 = 它之后遇到的 ★第一条供电网行 (PMUIOx_VCC / VCCIOx_VCC)★**" ⇒ 得到完整映射: ★

| ★**供电网 (datasheet 网名)** ★ | ★**覆盖的 GPIO 组 (本机解析)** ★ | ★**datasheet §3.1/§3.2 电压档 (★p.39 渲染图口径, `HW/RK3572_OFFICIAL_DATASHEET_FACTS.md` §5 已定★)** ★ | ★**abs-max** ★ |
|---|---|---|---|
| ★**PMUIO0_VCC1V8** ★ | ★**GPIO0_A0 … GPIO0_B3** ★ (★含 ★**GPIO0_B0 (球 1K21) = I2C0_SCL_M0**★ 与 ★**GPIO0_B1 (球 U32) = I2C0_SDA_M0**★) ★ | ★**1.8V only** ★ | ★**max 1.98 V** ★ |
| ★**PMUIO1_VCC** ★ | ★**GPIO0_B4 … GPIO0_D5** ★ | ★**1.8V/3.3V** ★ | ★**max 3.63 V** ★ |
| ★**VCCIO0_VCC1V8** ★ | ★**GPIO1_A0 … GPIO1_B3** ★ | ★**1.8V only** ★ | ★**max 1.98 V** ★ |
| ★**VCCIO1_VCC** ★ | ★**GPIO2_A0 … GPIO2_A5** ★ (★= SDMMC0 那 6 脚★) ★ | ★**1.8V/3.3V** ★ | ★**max 3.63 V** ★ |
| ★**VCCIO2_VCC** ★ | ★**GPIO2_B0 … GPIO2_C3** ★ | ★**1.8V/3.3V** ★ | ★**max 3.63 V** |
| ★**VCCIO3_VCC** ★ | ★**GPIO1_B4 … GPIO1_D6** ★ | ★**1.8V/3.3V** ★ | ★**max 3.63 V** |
| ★**VCCIO4_VCC** ★ | ★**GPIO2_C4 … GPIO2_D7** ★ | ★**1.8V/3.3V** ★ | ★**max 3.63 V** |
| ★**VCCIO5_VCC_0 (+ VCCIO5_VCC_1 同组双球)** ★ | ★**GPIO3_A4 … GPIO4_A1** ★ (★含 ★**GPIO3_C4 (球 AH33) = I2C5_SCL_M3**★ 与 ★**GPIO3_C1 (球 AL33) = I2C5_SDA_M3**★ ⇒ ★★这才是本板 I2C_A 真正所在的那一组★★) ★ | ★**1.8V/3.3V** ★ | ★**max 3.63 V** ★ |
| ★**VCCIO6_VCC** ★ | ★**GPIO4_B0 … GPIO4_B7** ★ | ★**1.8V/3.3V** ★ | ★**max 3.63 V** ★ |
| ★**VCCIO7_VCC** ★ | ★**(本板 SoM 未引出对应脚)** ★ | ★**1.2V/1.8V** ★ | ★**max 1.98 V** ★ |

★**⇒ ★★核心结论 (★这就是原 need 问的那个问题, ★现在有答案了★)★★**:

★★**① RK3572 的 "GPIO bank → VCCIO 供电组" ★不是 1:1 的 —— ★【一个 bank 会被劈成多个供电组】★★ ★★
★★**② 具体到 GPIO0: ★【GPIO0_A0…GPIO0_B3 → PMUIO0_VCC1V8 (1.8V only, abs-max 1.98V)】★ + ★【GPIO0_B4…GPIO0_D5 → PMUIO1_VCC (1.8V/3.3V, abs-max 3.63V)】★ ★★
★★**③ ⇒ GPIO0_B0 (球 1K21, = I2C0_SCL_M0) 与 GPIO0_B1 (球 U32, = I2C0_SDA_M0) ★【落在 PMUIO0_VCC1V8 这一组 ⇒ 1.8V only ⇒ abs-max 1.98 V】★★ ★★
★★**④ ★★⇒ 原 need 里 "GPIO0 只允许 1.98V" 这句话, ★【对 GPIO0_B0/B1 这两根脚本身 ★【恰好成立】★★ —— ★【但它成立的原因是 PMUIO0_VCC1V8, 不是 VCCIO1_VCC】★ ★★
★★**⑤ ★★⇒ 而 §3.1/§3.2 那一栏 "1.8V only = PMUIO0_VCC1V8 + VCCIO0_VCC1V8" 里面 ★【并没有】 VCCIO1_VCC ⇒ ★★原 need 与 `HW/AR0234CS_OPEN_SOURCE_FACTS.md` L241/L474 说的 "VCCIO1_VCC 属 1.8V only" ★★【是错的】★★ ⇒ ★★"VCCIO1_VCC 能上 3.3V (max 3.63V)" 这条 ★【才是对的】★★ ★★

★**⇒ ★【本单把原 need 从 "全部推论作废" 修正为 "结论对了一半, 但理由和网名都错了, 且这个结论对 I2C_A 没有因果关系"】★** ★

★★**等级: ★`[官网]` (★datasheet §2.6 引脚表排版 + §3.1/§3.2 电源域表★) + ★`[实测]` (★本机脚本解析, 见 §2.4★)★★**

---

### ★2.2 S6 (Forlinx OK3572-C 官方手册) ⇒ ★★**官方明文给了两组 bank→VCCIO 归属, 用来验证 §2.1 的读法★★** ★

★★**Forlinx 官方手册 §3.5.5.1 原文 (★本机实抓★)**:

> "The RK3572 has two JTAG multiplexes: **JTAG_TCK_M0/JTAG_TMS_M0 is located in the ★VCCIO1★ domain** and is multiplexed with SDMMC0 via the IOMUX; **JTAG_TCK_M1/JTAG_TMS_M1 is located in the ★PMUIO1★ domain** and is multiplexed with UART_Debug—UART0_M0."

★★**本单用它验 §2.1 的解析 (★注意: 这两组脚 ★恰好分别落在 ★【两个不同的 bank】★ 上 ⇒ 检验力最强★)****

| ★**官方声明** ★ | ★**对应的 SoC 脚 (datasheet §2.6)** ★ | ★**§2.1 本机解析结果** ★ | ★**对上了吗** ★ |
|---|---|---|---|
| ★**JTAG_TCK_M0 / JTAG_TMS_M0 ∈ VCCIO1** ★ | ★**GPIO2_A2 (球 B11) / GPIO2_A3 (球 1A8)** ★ | ★**VCCIO1_VCC** ★ | ★**✅ 对上** ★ |
| ★**JTAG_TCK_M1 / JTAG_TMS_M1 ∈ PMUIO1** ★ | ★**GPIO0_D4 (球 U33) / GPIO0_D5 (球 V32)** ★ | ★**PMUIO1_VCC** ★ | ★**✅ 对上** ★ |

★★**⇒ ★★两组官方声明 ★【全部对上】★★ ⇒ §2.1 的 "供电网行 = 组尾标记" 读法 ★【被官方文档独立验证】★★ ★

★★**★Forlinx 手册 §3.5.4 另有第三条官方声明 (★与本板直接相关★)**: "SDMMC0_DET_L (PIN: P3_90) … Determines whether the ★VCCIO1★ power domain I/O is configured for SDMMC0 or JTAG functionality." ⇒ ★**SDMMC0 那 6 脚 (GPIO2_A0…A5) 在 VCCIO1** ★ ⇒ ★**与 §2.1 解析一致 (VCCIO1_VCC = GPIO2_A0…A5) ⇒ ★★第三条交叉验证通过★★ ★**

★**⇒ ★`[官网]` (★Forlinx 官方手册 §3.5.4 / §3.5.5.1 原文, 本机实抓 351 KB 全文★)****

---

### ★2.3 S6 的 SoM 逐脚 VOL 列 ⇒ ★★**SoM 官方电平表 ★直接给出 "这根脚在 1.8V 还是 3.3V"★★** ★

★**Forlinx §2.6.2 表头原文**: "NUM ——SoM connector pin no. / Ball —— CPU pin ball no. / GPIO ——CPU pin general I/O port serial number / ★**Vol —— Pin signal electrical level**★ / Signal Name——SoM connector network name …"

★★**★这是本单 ★最直接可用的一张表: ★【SoM 官方逐脚电平】★ ⇒ 它不需要任何推断, ★【官方直接写明】★★★

★**本板 I2C_A 两根脚的官方逐字 (★本机实抓 Forlinx 官方手册§★)**:

```
|31| |AH33| |I2C5_SCL_M3| |GPIO3_C4_d| |1.8V| |I2C5 clock| |I2C5_SCL_M3|
|33| |AL33| |I2C5_SDA_M3| |GPIO3_C1_d| |1.8V| |I2C5 Data| |I2C5_SDA_M3|
```

★★**⇒ ★【官方逐字: 本板 I2C_A 两根脚 = I2C5_SCL_M3 / I2C5_SDA_M3 = GPIO3_C4 (AH33) / GPIO3_C1 (AL33), 电平 = 1.8V】★★ ★
★★**⇒ ★【原 need 说 "I2C0 = GPIO0_B0/B1 (球 1K21/U32)" ⇒ ★【与官方手册逐字矛盾】★ —— ★★那两根球位 ★【本板 SoM 根本没引出】★★ (★本机实读: `FET3572C_PIN_TABLE.csv` 中球 1K21 / U32 ★【0 条】★)★★ ★

★★**⇒ 等级: ★`[官网]` (★Forlinx 官方手册 §2.6.2 Table 4 逐格转录★) + ★`[实测]` (★本机实读项目内转录表★)****

---

### ★2.4 ★★**[实测] 本机验证: §2.1 的映射规则 ★【108/109 可比球位与 SoM 官方 VOL 列一致】★★** ★

★★**这是本单最硬的一条机器证据 (★也是判据串敢给的前提★)****

★**方法 (★`[实测]`, 全部本机跑, 可复现★)**:
1. 从 ★**项目库内官方 PDF**★ `HW/RK3572_PIN_TABLE/RK3572_datasheet_V1.1.pdf` 用 `pdftotext -layout` 抽出带列对齐的 §2.6 引脚表 (★得 Ball 列 + Abbr 列★)
2. 逐行扫描, 规则 = "GPIO 行归属 = 其后第一条供电网行" ⇒ 得 129 个 GPIO 脚 → 供电网 的映射
3. 把映射与 ★**S9 项目内转录表 `HW/PCB/FET3572C_PIN_TABLE.csv` 的官方 VOL 列**★ 逐球对账

★**结果 (★反证法: 若规则错, 一个供电组内就会出现两个不同电平★)**:

```
=== FALSIFICATION TEST: 一个供电网 => 只能有一个 SoM 官方电平 ===
  PMUIO0_VCC1V8      n=  6 {'1.8V': 6}              OK
  PMUIO1_VCC         n= 18 {'3.3V': 18}             OK
  VCCIO0_VCC1V8      n=  0 (本板 SoM 未引出)         OK
  VCCIO1_VCC         n=  6 {'1.8V/3.3V': 6}         OK   ← 6 个 SDMMC0 脚
  VCCIO2_VCC         n= 12 {'3.3V': 12}             OK
  VCCIO3_VCC         n= 19 {'1.8V': 19}             OK
  VCCIO4_VCC         n= 12 {'3.3V': 12}             OK
  VCCIO5_VCC_0       n= 28 {'1.8V': 28}             OK
  VCCIO6_VCC         n=  8 {'3.3V': 7, '1.8V': 1}   <<< 1 例外
  ⇒ 可比球位 109 个, 一致 108 个 (唯一例外 = 球 1AE21, 官方标了 _1V8) ⇒ 108/109
```

★**样本量说明 (★不许夸大★)**: ★**SoM 官方表 399 行里, 190 个有真实球位号, 其中 110 行的 GPIO 列是 GPIO 脚 (★其余 80 行是电源/地/模拟脚, 没有 GPIO 归属可对账★) ⇒ ★**真正可比的是 109 个球位** (★另有 1 个球位 1D10 因 ★【官方手册与 datasheet 的球位号对不上】★ 见 §2.7 被排除★) ⇒ ★**本单 ★【没有】拿 399 或 190 当分母★****

★★**★那 1 个例外 ★【不是本单规则的错, 是官方 SoM 自己的脚级例外】★★** ★
★**例外: 球 1AE21 = GPIO4_B1 ⇒ VCCIO6_VCC 组内, 但官方 VOL = 1.8V (★组内其余 7 脚 = 3.3V★)****
★**⇒ 本机实抓 Forlinx 官方手册 §2.7 载板侧, 该脚逐字 = "★71 | 1AE21 | HDMI_TX_HPDIN_M0 | GPIO4_B1_d | 1.8V | HDMI send link detection | HDMI_TX_HPDIN_M0_1V8★" ⇒ ★★官方自己在网名尾巴上标了 "_1V8" ⇒ ★【SoM 侧该脚被特殊处理成 1.8V】★★ ⇒ ★★与 RK3576 手册同类描述 ("level shifters … make them 3.3v when they otherwise would have been 1.8v") ★【是 SoM 板级电平搬移, 不是 SoC 域归属错】★★**
★**⇒ ★★该例外的存在 ★【反而强化】★★了本单的规则 (★若规则是错的, 例外不会 ★【恰好落在一个官方标了 "_1V8" 特殊网名的脚上】★★) ★**

★★**★第二重机器证据: GPIO0 组内的电压翻转点 ★【与官方供电网行位置 ★逐行对齐】★★****
```
PMUIO0_VCC1V8 组 (GPIO0_A0..GPIO0_B3) 的 SoM 官方 VOL:  全部 1.8V  (5 个在板脚 + 6 个不在板)
PMUIO1_VCC    组 (GPIO0_B4..GPIO0_D5) 的 SoM 官方 VOL:  全部 3.3V  (18/18)
  ★ 翻转点恰好落在 datasheet §2.6 表里 "GPIO0_B3 (1M23, 1.8V)" 之后、"PMUIO0_VCC1V8 (2G11)" 那一行、"GPIO0_B4 (AC33, 3.3V)" 之前
  ★ ⇒ 23/23 逐球吻合, 零例外
```

★**⇒ ★`[实测]` (★本机脚本, 108/109 + 23/23, 可复现; ★门禁 `SW/tools/check_rk3572_vccio_domain.py` 每次重跑★)****

---

### ★2.5 S3/S5 (BSP + io-domain 驱动) ⇒ ★★**为什么"必须查 SoM/载板手册"而不是查 BSP★★** ★

★★**本单查完 S2/S3/S4/S5 四路官方内核源, 结论是: ★【RK3572 的 IO 域电压 ★【根本不是软件可配的】★ ⇒ ★【只能从硬件供电轨 / SoM 官方表读】★ ⇒ ★★这 ★反过来把 S6 提升为唯一正解★★**

★**证据**: Rockchip 官方 `drivers/soc/rockchip/io-domain.c` (`develop-6.12`, 本机实抓 20,342 B) 的 `rockchip_iodomain_ids[]` 里 ★**只有 `rockchip,rk3568-pmu-io-voltage-domain`, 没有 RK3572 条目**; ★**RK3572 的 5 个 dtsi 里 0 个含 `io-domains` / `domain-supply` / `vccio` 网名** ★
★**⇒ 等级: ★`[0数据]` (★BSP 侧确无此信息, 已穷尽官方内核源★)****

---

### ★2.6 ★★**[0数据] 清单 (★查完确实没有的, 不是没查★)** ★

| # | ★**没查到的东西** ★ | ★**已穷尽的官方源** ★ | ★**对本单结论有影响吗** ★ |
|---|---|---|---|
| ① ★**ZD-1** ★ | ★**RK3572 datasheet 里有没有一张显式的 "GPIO bank → VCCIO 供电组" 对应表** ★ | ★S1 (★全文 2,920 行 `pdftotext -layout` 抽取, 逐行扫过★) ★ | ★**没有 ⇒ 这就是原 need 说 "查不到" 的原因, 它是对的★ ⇒ ★【但 §2.6 引脚表本身的分组排版就是那张表的等价物★, ★【加上官方 VTAG 归属声明 + SoM 逐脚 VOL 列, 已足以定案】★** |
| ② ★**ZD-2** ★ | ★**RK3572 datasheet §3.1/§3.2 里 "VCCIOx ↔ 具体 GPIO 脚" 的显式交叉引用** ★ | ★S1 ★ | ★**没有 ⇒ ★【§2.6 的分组 + S6 官方声明 联合给出】★** |
| ③ ★**ZD-3** ★ | ★**BSP 侧的 IO 域配置 (`io-domains` / `domain-supply`)** ★ | ★S2/S3/S4/S5 四路官方内核源 ★ | ★**无 ⇒ ★【因为 RK3572 本就不是软件可配 IO 域】★ ⇒ 不影响** |
| ④ ★**ZD-4** ★ | ★**"GPIO0_B0/B1 是否可能另有 3.3V 档"** ★ | ★S1 + S6 ★ | ★**没有 ⇒ PMUIO0_VCC1V8 是 1.8V only, abs-max 1.98 V (datasheet p.39 渲染图已定) ⇒ ★【这两根脚本身永远上不了 3.3V】★** |
| ⑤ ★**ZD-5** ★ | ★**SoM 侧 VCCIO 供电轨的 ★网名★ (★如 "VCCIO5_1V8" 这种载板上的 rail 名★)** ★ | ★S6/S7 (★Forlinx 手册全文 351 KB 扫过, 只出现 2 处 "VCCIO1", ★【无】VCCIO 供电网名表★) ★ | ★**无 ⇒ 不影响本单结论 (★我们要的是 ★脚→域→电压★, 不是域→网名★) ⇒ ★【但若将来要画原理图上的 VCCIO rail 名, 这一项仍是 [0数据] ⇒ 见 §4 降级方案 D-3】★** |

---

### ★2.7 ★★[推算] 顺带查出的一处 ★官方-vs-官方 球位号不一致★ (★与本单结论无关, 但必须报, 不许瞒★) ★

★**球 1D10: Forlinx 官方手册 (载板侧 §2.7 与 SoM §2.6.2 两处) 都写 = GPIO3_D5_d; 而 Rockchip RK3572 Datasheet Rev 1.1 §2.6 写 = AVSS_17 (模拟地), 且 datasheet 里 GPIO3_D5 是球 1AB20****
★**⇒ 本单把该球位 ★【排除出对账样本】★ (★不是规则错, 是两份官方文档在这一个球位上不一致★) ⇒ 可比球位 = 109 而非 110 ★**
★**⇒ ★【本板不用这根脚】★ (★I2C_A 走 AH33/AL33, 与此无关★) ⇒ 对本单结论零影响 ★**
★**等级: ★`[推算]` (★两份官方文档逐字对读★) + ★`[0数据]` (★谁是笔误无从判定★) ★**

---

## ★3 ★★结论一句话 (★任务书 (c) 项的正面回答★)★★

★★**"I2C0 (GPIO0_B0/B1) 的 IO 域电压能不能上 3.3V / 2.8V / 1.8V" ⇒ ★★【不能上 3.3V, 不能上 2.8V, 只能 1.8V】★★ (★GPIO0_B0/B1 属 PMUIO0_VCC1V8, 1.8V only, abs-max 1.98 V —— `[官网]` datasheet p.39 + §2.6 引脚表分组★) ★★

★★**"那 I2C_A 上拉最终该是多少?" ⇒ ★★1.8V, 2.2kΩ★★ (★但 ★【理由是】★ ★**本板 I2C_A 走 I2C5 (GPIO3_C4/C1, 球 AH33/AL33), Forlinx 官方 SoM 逐脚表逐字写 "1.8V" ⇒ ★【官方直接给的值, 不需要任何推断】★ —— ★★跟 "GPIO0_B0/B1 属 PMUIO0" 这件事 ★【没有因果关系】★★) ★★

★★**★⇒ ★【原 need 的 §7-② 遗留 ("这条不核, U2 的最终改法不能定稿") ⇒ ★【可以定稿了】★ ⇒ ★【ISS-211 d1 的取值依据 ★【从 "待核" 变成 "[官网] 1.8V"】★ ⇒ ★【任务书说的 "落表定稿前不核, d1 只能悬着" ⇒ ★【本单把它解掉了】★★★ ★

---

## ★4 ★★给 hw-lead 的可落表判据串 (★任务书 (②) 项; ★可直接粘进 `HW/SCHEMATIC_LANDING_WORKPACKET_V1.md`★)★★

★**★边界声明: ★【本单只出文字判据, 不改任何网表】★ ⇒ ★【落表由 hw-lead 做】★ ⇒ ★【`HW/` 下本单一个字节没动】★**

★★**★判据串 (★建议贴进 `HW/SCHEMATIC_LANDING_WORKPACKET_V1.md` §2.1 (d1) 的 ⑤ 改法栏 之后, 作为新增一栏 "⑧ 官方依据 (ISS-228 补)"; ★【不替换 §2.1 现有任何一栏, 不改现有 8 栏结构】★)★★:

```
⑧ 官方依据 (ISS-228 · sw-lead · 2026-11-16 · 零外发 · 板端[实测]=0 条):

★结论★: B-01 / B-02 的最终取值为 ★imp = 上拉 2.2k 到 1.8V (RAIL_VDD_1V8_IO) / level = 1.8V★
  ⇒ ★【此取值 ★不是 "保守默认", 是 ★【官方唯一正解】★】★

★官方出处 (★按强度排序, ★每条都能自己复现★)★:
  [官网-1] Forlinx OK3572-C 官方手册 §2.6.2 Table 4 (P2 Even) 逐字:
            P2_31 = 球 AH33 = I2C5_SCL_M3 / GPIO3_C4_d / VOL 1.8V
            P2_33 = 球 AL33 = I2C5_SDA_M3 / GPIO3_C1_d / VOL 1.8V
            ⇒ ★【官方逐字: 本板 I2C_A 两根脚就是 1.8V 域】★
  [官网-2] Rockchip RK3572 Datasheet Rev 1.1 §3.1 Table 3-1 + §3.2 Table 3-2 (p.39):
            GPIO3_C4 / GPIO3_C1 所在供电组 VCCIO5_VCC 属 "1.8V/3.3V" 档, abs-max 3.63 V
            ⇒ SoC 侧不吃紧; ★【真正把电压钉死在 1.8V 的是 SoM 侧的 1.8V 供电 (见[官网-1])】★
  [官网-3] ★【勘误, ★务必连带改】★: 原 need (state/fragments/hw.yaml L1124-L1133) 与
            HW/AR0234CS_OPEN_SOURCE_FACTS.md L241 / L474 写的
            "I2C0_SCL = GPIO0_B0 (球 1K21) / I2C0_SDA = GPIO0_B1 (球 U32)" ⇒ ★【与官方手册矛盾】★
            ★【本板 I2C_A 走 I2C5 (GPIO3_C4/C1, 球 AH33/AL33); 球 1K21 / U32 本板 SoM 根本没引出】★
            ⇒ ★【该 need 的 "3.3V/2.8V 超 SoC 侧 abs-max ⇒ 整条 I2C_A 要重新设计" 这条推论 ★【不成立】★,
               ★【因为 I2C_A 根本不接在 I2C0 上】★
  [官网-4] ★【勘误 2】★: "VCCIO1_VCC 属 1.8V only (max 1.98V)" ⇒ ★【错】★
            ⇒ VCCIO1_VCC 与 PMUIO1_VCC + VCCIO1~6_VCC 同属 "1.8V/3.3V" 档 (max 3.63 V);
               "1.8V only" 那一档 ★【只有 PMUIO0_VCC1V8 + VCCIO0_VCC1V8】
               ★【而 GPIO0_B0/B1 确实落在 PMUIO0_VCC1V8 ⇒ 这两根脚本身 1.98V abs-max 是真的】★
               ⇒ ★【但对 I2C_A 无因果关系 (见[官网-3])】★

★阻值 2.2k 的算式 (★不变, ★本单只补官方依据, ★不改数★)★:
  VOL(max)=0.4V, IOL(max)=3mA ⇒ R >= (1.8-0.4)/3mA = 467Ω ⇒ 取 2.2k
  灌流 (1.8-0.4)/2.2k = 0.64mA <= 3mA ✔ ; t_r = 2.2k x 100pF x 0.847 ≈ 186ns ✔
  ★来源: RK3572 datasheet §3.3 Table 3-3 (Digital 3.3V/1.8V GPIO @1.8V: VOL max 0.25*DVDD, VIH min 0.7*DVDD) + onsemi AR0234CS Table 6 (RSD 1.5k~4.7k)★

★落表时必须连带改的 ★【勘误 2 处, ★别漏】★:
  ① HW/AR0234CS_OPEN_SOURCE_FACTS.md L241 / L474 的 "RK3572 侧 (I2C0/I2C1, GPIO0_B0/B1)" 段
     ⇒ ★【改为 "RK3572 侧 = I2C5_M3 (GPIO3_C4/C1, 球 AH33/AL33), Forlinx 官方 SoM 逐脚 VOL = 1.8V"】★
  ★【★本单 ★【没有】改这两处 —— HW/ 是 hw-lead 地界, ★【本单只报, 不动】★】★

★若 ★【整板换 AR0234CS】(★整机阶段, 不是 demo 板★) ⇒ ★【本单给的是方向, 不是定稿】★:
  AR0234CS 若 VDD_IO = 2.8V ⇒ VIH = 0.7 x 2.8 = 1.96V > 1.8V 上拉 ⇒ ★【从设备认不出高电平】★
  ⇒ 正确解法是 ★【VDD_IO 改 1.8V】★ (onsemi Note 19.2: "VDD_IO and VDDIO_PHY if 1.8 VDC each" ⇒ ★【还能顺带解掉
    "VDDIO_PHY 缺一条 1.8V 轨" 那条硬伤 — 两条轨并成一条 1.8V, 正好填掉 CONN_CAM_1 的空脚需求】★)
  ⇒ ★【★零新增器件, ★且不增加 BOM 行】★  ★★依据: onsemi AR0234CS datasheet Note 10 / Note 19.2 / Table 13 (已在 HW/AR0234CS_OPEN_SOURCE_FACTS.md 内)★★
```

★★**★若结论是 [0数据] ⇒ 保守默认 + 后续解锁条件 (★任务书 (②) 第 3 项; ★本单结论 ★【不是】[0数据]★, 但 ★【仍把这条写出来, 供 §2.6 ①/②/⑤ 三项残留缺口用】★)★★**:

| ★**保守默认 (★在没查到之前, 网表一律这么填★)** ★ | ★**后续解锁条件 (★满足哪条才能改★)** ★ |
|---|---|
| ★**默认 1: I2C_A 上拉 `imp` = "上拉 2.2k 到 1.8V (RAIL_VDD_1V8_IO, 灌 0.64mA @VOL=0.4V, t_r=186ns@100pF / 559ns@300pF)" / `level` = "1.8V"** ★ (★填到 `HW/SCHEMATIC_V1_SPEC.json` `connections[20]`/`[21]` 的 `level` 与 `imp` 两键★) ★ | ★**解锁 = ★【S6 官方逐脚 VOL 列 = 1.8V】★ ⇒ ★【★本单已满足★ ⇒ ★【默认已升级为定稿】★】★** ★ |
| ★**默认 2: 凡是"某某脚在哪个 VCCIO 域"类断言, 一律写 `★[0数据]★` + 注明 "须查 SoM 官方逐脚 VOL 列", ★【不许】写一个具体电压★** ★ (★填到任何文档的证据等级栏 / `note` 字段★) ★ | ★**解锁 = ★【S6 §2.6.2 的 VOL 列 或 S1 §2.6 引脚表分组 + 官方 JTAG 归属声明 交叉验证通过】★ ⇒ ★【★本单已满足 ⇒ 此条默认也已解锁★】★** ★ |
| ★**默认 3: 凡是要落到原理图上的 "VCCIO rail 网名" (★如 VCCIO5 的载板 rail 名★), 一律写 `★[0数据]★`, ★【不许】自己编一个 `VCCIO5_3V3` 之类的网名★** ★ (★填到 `HW/SCHEMATIC_V1_SPEC.json` 相应 `note` / 原理图页电源标注★) ★ | ★**解锁 = ★【拿到 Forlinx 载板原理图 / 官方 rail 命名表】★ ⇒ ★【★★至今 [0数据]★★ ⇒ ★【本条默认 ★【继续生效】★ ⇒ ★【hw-lead 落表时 ★【不许】在网表/原理图里写 VCCIO rail 名】★】★** ★ |

---

## ★5 ★★证据分级总表 (★任务书 (b) 项的正面回答 + 边界自查★)★★

| ★**结论** ★ | ★**等级** ★ | ★**怎么量的** ★ |
|---|---|---|
| ★**GPIO0_B0 (球 1K21) / GPIO0_B1 (球 U32) → PMUIO0_VCC1V8, 1.8V only, abs-max 1.98 V** ★ | ★**`[官网]`** | ★**Rockchip RK3572 Datasheet Rev 1.1 §2.6 引脚表分组 (本机 `pdftotext -layout` 实解析) + §3.1/§3.2 p.39 (渲染图口径, `HW/RK3572_OFFICIAL_DATASHEET_FACTS.md` §5 已定) ★** |
| ★**GPIO0_B4…GPIO0_D5 → PMUIO1_VCC, 1.8V/3.3V, abs-max 3.63 V** ★ | ★**`[官网]`** | ★**同上** ★ |
| ★**★本板 I2C_A = I2C5_SCL_M3 / I2C5_SDA_M3 = GPIO3_C4 (AH33) / GPIO3_C1 (AL33), 官方 VOL = 1.8V** ★ | ★**`[官网]`** | ★**Forlinx OK3572-C 官方手册 §2.6.2 Table 4 逐字 (本机实抓 351,453 B 全文) + 项目内转录表 `HW/PCB/FET3572C_PIN_TABLE.csv` L132/L134 逐格核对 ★** |
| ★**★球 1K21 / U32 本板 SoM 未引出 ⇒ 原 need 的 I2C0 前提对本板不成立** ★ | ★**`[官网]` + `[实测]`** ★ | ★**`[官网]`: Forlinx §2.6.2 全表无该两球 · ★`[实测]`: 本机 grep `FET3572C_PIN_TABLE.csv` 命中 0 条 ★** |
| ★**"JTAG_TCK_M0/TMS_M0 ∈ VCCIO1" 与 "JTAG_TCK_M1/TMS_M1 ∈ PMUIO1"** ★ | ★**`[官网]`** | ★**Forlinx 官方手册 §3.5.5.1 原文 (本机实抓) ★** |
| ★**"SDMMC0 6 脚在 VCCIO1"** ★ | ★**`[官网]`** | ★**Forlinx 官方手册 §3.5.4 原文 ★** |
| ★**§2.6 引脚表供电网分组解析 ⇒ 109 个可比球位中 108 个与 SoM 官方 VOL 列一致** ★ | ★**`[实测]`** ★ | ★**本机脚本 (★门禁 `SW/tools/check_rk3572_vccio_domain.py` 每次重跑★) ★** |
| ★**GPIO0 组内电压翻转点 (B3|B4) 逐球吻合 23/23** ★ | ★**`[实测]`** | ★**本机脚本 ★** |
| ★**1 例外 (球 1AE21 / GPIO4_B1 = 1.8V, 组内其余 3.3V)** ★ | ★**`[官网]` + `[推算]`** ★ | ★**`[官网]`: Forlinx 手册载板侧逐字 "HDMI_TX_HPDIN_M0_1V8" (★官方自己标了 1V8 后缀★) · ★`[推算]`: 判定为 SoM 板级电平搬移 ★** |
| ★**RK3572 无软件可配 IO 域 (BSP/driver 皆无)** ★ | ★**`[0数据]`** | ★**5 个官方 dtsi + 官方 io-domain.c 全查, 无 RK3572 条目 ★** |
| ★**SoM 侧 VCCIO 供电轨网名** ★ | ★**`[0数据]`** | ★**Forlinx 手册全文仅 2 处 "VCCIO1" (且是 JTAG/SDMMC 语境, 非 rail 名) ★** |
| ★**RK3572 datasheet 是否有显式 bank→VCCIO 表** ★ | ★**`[0数据]`** (★★**但 §2.6 分组排版 + S6 官方声明 已给出等价答案★**★) | ★**全文逐行扫过 ★** |
| ★**B-01/B-02 最终取值 = 2.2k / 1.8V** ★ | ★**`[官网]`** | ★**见 §4 判据串 ★** |
| ★**2.2k 阻值算式 (VOL 0.4V / IOL 3mA / t_r 186ns)** ★ | ★**`[推算]`** (★输入全 `[官网]`★) | ★**RK3572 §3.3 Table 3-3 + onsemi Table 6; ★算术可复核 ★** |
| ★**AR0234CS 若上 ⇒ VDD_IO 走 1.8V (而非 2.8V)** ★ | ★**`[官网]`** | ★**onsemi AR0234CS Note 10 / Note 19.2 / Table 13 (转录在 `HW/AR0234CS_OPEN_SOURCE_FACTS.md`) ★** |
| ★**★板端 [实测] = 0 条** ★ | ★**★板与屏不在本机 ⇒ 所有 [实测] 都是 "本机脚本 / 本机文件实读"★** | ★**★零外发 ⇒ 无任何外部问询★** ★ |

---

## ★6 机器可读锚点 (★供门禁脚本锁死★)

<!-- BEGIN RK3572_VCCIO_DOMAIN_ANCHORS
```yaml
iss228:
  ball_gpio_domain:
    # ★datasheet §2.6 引脚表分组 (本机解析) ⇒ 供电网 ⇒ 电压档 ⇒ abs-max
    # ★★本表只放 ★【本板 I2C_A 真正涉及的那几组】+ 【原 need 点名的那几组】★★
    PMUIO0_VCC1V8:
      gpio_groups: ["GPIO0_A0..GPIO0_B3"]
      covers: ["GPIO0_B0", "GPIO0_B1"]     # ★原 need 点名的两根 (I2C0_SCL_M0 / I2C0_SDA_M0)
      volt_class: "1.8V only"
      abs_max_v: 1.98
      so_m_volt: "1.8V"
    PMUIO1_VCC:
      gpio_groups: ["GPIO0_B4..GPIO0_D5"]
      volt_class: "1.8V/3.3V"
      abs_max_v: 3.63
      so_m_volt: "3.3V"
    VCCIO0_VCC1V8:
      gpio_groups: ["GPIO1_A0..GPIO1_B3"]
      volt_class: "1.8V only"
      abs_max_v: 1.98
      so_m_volt: "1.8V"
    VCCIO1_VCC:
      gpio_groups: ["GPIO2_A0..GPIO2_A5"]
      volt_class: "1.8V/3.3V"
      abs_max_v: 3.63
      so_m_volt: "1.8V/3.3V"
    VCCIO5_VCC_0:
      gpio_groups: ["GPIO3_A4..GPIO4_A1"]
      covers: ["GPIO3_C4", "GPIO3_C1"]      # ★★本板 I2C_A 真正所在的那一组★★
      volt_class: "1.8V/3.3V"
      abs_max_v: 3.63
      so_m_volt: "1.8V"
  board_i2c_a:
    net_name_scl: "I2C_A_SCL"
    net_name_sda: "I2C_A_SDA"
    som_connector: "FET3572-C"
    som_pins: ["P2_31", "P2_33"]
    soc_balls: ["AH33", "AL33"]
    soc_signal: ["I2C5_SCL_M3", "I2C5_SDA_M3"]
    soc_gpio: ["GPIO3_C4", "GPIO3_C1"]
    so_m_official_vol: "1.8V"
    supply_net: "VCCIO5_VCC_0"
    level: "1.8V"
    imp: "上拉 2.2k 到 1.8V (RAIL_VDD_1V8_IO, 灌 0.64mA @VOL=0.4V, t_r=186ns@100pF / 559ns@300pF)"
    imp_b02: "上拉 2.2k 到 1.8V"
    spec_json_field: "connections[20](B-01) / connections[21](B-02) 的 level 与 imp"
  wrong_premises_to_reject:
    - id: "premise_i2c0_on_gpio0_b0_b1"
      wrong: "本板 I2C_A 接在 I2C0 / GPIO0_B0 (球 1K21) / GPIO0_B1 (球 U32) 上"
      right: "本板 I2C_A 接在 I2C5_M3 / GPIO3_C4 (球 AH33) / GPIO3_C1 (球 AL33) 上; 球 1K21 与 U32 本板 SoM 根本没引出"
      must_not_say: ["I2C_A = GPIO0_B0", "I2C_A = GPIO0_B1", "I2C_A 走 I2C0"]
    - id: "premise_vccio1_is_1v8_only"
      wrong: "VCCIO1_VCC 属 1.8V only GPIO supply voltage (max 1.98 V)"
      right: "VCCIO1_VCC 与 PMUIO1_VCC + VCCIO1~6_VCC 同属 1.8V/3.3V 档 (max 3.63 V); 1.8V only 档只有 PMUIO0_VCC1V8 + VCCIO0_VCC1V8"
      must_not_say: ["VCCIO1_VCC 属 1.8V only", "VCCIO1_VCC max 1.98"]
    - id: "premise_gpio0_is_one_domain"
      wrong: "GPIO0 整组属同一个 VCCIO 供电组"
      right: "GPIO0 被劈成两组: GPIO0_A0..GPIO0_B3 -> PMUIO0_VCC1V8; GPIO0_B4..GPIO0_D5 -> PMUIO1_VCC"
      must_not_say: ["GPIO0 属 VCCIO1", "GPIO0 整组只有 1.98V"]
  degrade_plan:
    - id: "D-1"
      default: "B-01/B-02 的 level=1.8V, imp=上拉 2.2k 到 1.8V"
      unlock: "Forlinx 官方 SoM 逐脚 VOL 列 = 1.8V"
      unlocked: true
    - id: "D-2"
      default: "bank->VCCIO 类断言一律写 [0数据] + 注明须查 SoM 官方逐脚 VOL 列"
      unlock: "SoM 官方逐脚 VOL 列 或 datasheet §2.6 分组 + 官方 JTAG 归属声明 交叉验证"
      unlocked: true
    - id: "D-3"
      default: "VCCIO rail 网名一律写 [0数据], 不许自己编网名"
      unlock: "拿到 Forlinx 载板原理图 / 官方 rail 命名表"
      unlocked: false
  zero_data_items:
    - id: "ZD-1"
      what: "RK3572 datasheet 里有没有一张显式的 GPIO bank → VCCIO 供电组对应表"
      status: "[0数据]"
    - id: "ZD-2"
      what: "RK3572 datasheet §3.1/§3.2 里 VCCIOx ↔ 具体 GPIO 脚 的显式交叉引用"
      status: "[0数据]"
    - id: "ZD-3"
      what: "BSP 侧的 IO 域配置 (io-domains / domain-supply)"
      status: "[0数据]"
    - id: "ZD-4"
      what: "GPIO0_B0/B1 是否可能另有 3.3V 档"
      status: "[0数据]"
    - id: "ZD-5"
      what: "SoM 侧 VCCIO 供电轨的网名 (载板上的 rail 名)"
      status: "[0数据]"
  official_citations:
    - id: "[官网-1]"
      source: "Forlinx OK3572-C 官方手册 §2.6.2 Table 4 (P2 Even) 逐字"
      quote: "P2_31 = 球 AH33 = I2C5_SCL_M3 / GPIO3_C4_d / VOL 1.8V"
    - id: "[官网-2]"
      source: "Rockchip RK3572 Datasheet Rev 1.1 §3.1 Table 3-1 + §3.2 Table 3-2 (p.39)"
      quote: "GPIO3_C4 / GPIO3_C1 所在供电组 VCCIO5_VCC 属 1.8V/3.3V 档, abs-max 3.63 V"
    - id: "[官网-3]"
      source: "Forlinx OK3572-C 官方手册 §2.6.2 (勘误: 本板 I2C_A 走 I2C5, 不是 I2C0)"
      quote: "球 1K21 / U32 本板 SoM 根本没引出"
    - id: "[官网-4]"
      source: "Rockchip RK3572 Datasheet Rev 1.1 p.39 (勘误 2: VCCIO1_VCC 不属 1.8V only)"
      quote: "1.8V only 那一档 只有 PMUIO0_VCC1V8 + VCCIO0_VCC1V8"
  official_crosschecks:
    - claim: "JTAG_TCK_M0/JTAG_TMS_M0 位于 VCCIO1 域"
      soc_gpio: ["GPIO2_A2", "GPIO2_A3"]
      parsed_domain: "VCCIO1_VCC"
      pass: true
    - claim: "JTAG_TCK_M1/JTAG_TMS_M1 位于 PMUIO1 域"
      soc_gpio: ["GPIO0_D4", "GPIO0_D5"]
      parsed_domain: "PMUIO1_VCC"
      pass: true
    - claim: "SDMMC0_DET_L 决定 VCCIO1 域配置为 SDMMC0 或 JTAG"
      soc_gpio: ["GPIO2_A0", "GPIO2_A1", "GPIO2_A2", "GPIO2_A3", "GPIO2_A4", "GPIO2_A5"]
      parsed_domain: "VCCIO1_VCC"
      pass: true
  falsification:
    so_m_gpio_balls_available: 110
    so_m_balls_checked: 109
    so_m_balls_matched: 108
    gpio0_block_boundary_match: "23/23"
    known_exception:
      ball: "1AE21"
      gpio: "GPIO4_B1"
      domain: "VCCIO6_VCC"
      so_m_volt: "1.8V"
      reason: "官方载板侧网名带 _1V8 后缀 (HDMI_TX_HPDIN_M0_1V8) ⇒ SoM 板级电平搬移, 非 SoC 域归属错"
  board_measured_count: 0
  external_contact_count: 0
```
<!-- END RK3572_VCCIO_DOMAIN_ANCHORS -->

---

## ★7 边界自查 (★本单动了什么 / 没动什么★)

| ★**项** ★ | ★**状态** ★ |
|---|---|
| ★**`HW/` 下任何文件** ★ | ★**零写入** (★网表 / 脚表 / 板 / `.kicad_pro` / 原理图 / BOM / `SCHEMATIC_V1_SPEC.json` / `FET3572C_PIN_TABLE.csv` 一个字节没动★) ⇒ ★**判据串只出文字, 落表由 hw-lead 做** ★ |
| ★**`MECH/` 下任何文件** ★ | ★**零写入** ★ |
| ★**`state/issue_log.yaml`** ★ | ★**零写入** (★status 留给 main 落 verified★) ★ |
| ★**`PROJECT_TRACKER.md` §0 / `DECISION_PENDING_2026-11-16.md` / `state/outbox/`** ★ | ★**零写入** ★ |
| ★**别人的分片 (`state/fragments/{pm,hw,mech}.yaml`)** ★ | ★**零写入** ★ |
| ★**PCB 布线 / 布局 / 板框** ★ | ★**零触碰** ★ |
| ★**板端 [实测]** ★ | ★**0 条** (★板与屏不在本机★) ⇒ ★**所有 [实测] 都是 "本机脚本 / 本机文件实读"** ★ |
| ★**外发动作** ★ | ★**零** (★不发邮件 / 不询价 / 不问询 / 不采购★) ⇒ ★**S2/S3/S4/S5 四路 [0数据] 是 "自己查完确实没有", 不是 "等原厂回信"** ★ |
| ★**自签 issue** ★ | ★**没有** ★ |
| ★**本单新建的文件** ★ | ★**3 个**: `SW/RK3572_GPIO0_VCCIO_DOMAIN_FACTS.md` (本文件) · `SW/tools/check_rk3572_vccio_domain.py` (机器门禁) · `HANDOFF/2026-11-16_sw-lead_ISS228_RK3572_GPIO0_VCCIO官方映射自查.md` (交接单) ★ + ★**`state/fragments/sw.yaml` 原子写** ★ |

---

## ★8 自证 (★一条命令复现本页每个数★)

```bash
cd projects/smart_glasses
python3 SW/tools/check_rk3572_vccio_domain.py             # rc=0 ⇒ C1~C8 全过
python3 SW/tools/check_rk3572_vccio_domain.py --selftest   # rc=0 ⇒ 反向用例 N/N 全抓到
```

★**门禁每次会重跑**: ★**(a) 从项目库内官方 PDF 重新 `pdftotext -layout` 解析 §2.6 引脚表 ⇒ 重算 129 脚→供电网 映射 ★**(b) 用 ★**Forlinx 官方手册的官方转录表**★ `HW/PCB/FET3572C_PIN_TABLE.csv` 重跑 108/109 反证测试 ★**(c) 重跑三条官方交叉验证 ★**(d) 重核 B-01/B-02 的 `level`/`imp` 取值 ★**

★**⇒ 任一条被改坏 ⇒ 立刻红 (★不是 "写完就交"★)**
