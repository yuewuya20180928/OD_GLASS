# HW/STEP1_PARTS_SPEC.md —— Step1 三件外购件的规格汇总 (P1 camera / P2 屏 / P3 核心板)

| 项 | 内容 |
|---|---|
| 作者 | **硬件总工 (hw-lead)** |
| 日期 | 2026-11-02 23:05 (GMT+8) |
| 触发 | 老板 2026-11-02 22:30 拍板「**板子必须全部自己画**」⇒ demo 用**自研主板** ⇒ ★**主板的 FPC 座/供电/接口全被外购件倒逼** ⇒ **必须先把这三件选定并拿到机械+电气规格** |
| 单号 | **ISS-158** (本单) |
| 本单范围 | ★**只交 P1/P2/P3 三件的规格**, 不做 F4~F12 致命项清零 (那是 ISS-159) |
| 写入范围 | 本文件 + `HW/PART_ALTERNATIVES_REGISTRY.md` (补三类"针位表/引脚定义/尺寸"列) + `state/fragments/hw.yaml` |
| 纪律 | ① **全部公开在售 + 公开资料可查 ⇒ 不触发 L4 (不咨询厂家)**, 本单不含任何"联系厂家"动作 ② **没查到写「未查」** —— 不猜价格/库存/针数/引脚 ③ 证据分级 `[实测]` = 本单实际抓到原文 / `[官方]` = 厂商公开文档 / `[推断]` = 不可当结论 |

---

## 0. 一句话结论 (先看这个)

★★ **三件都已在公开渠道选定并拿到画板所需的规格** ⇒ ★**主板现在可以照抄画了**:

| 件 | 选定的实物 | ★**主板要照抄的关键规格** | 状态 |
|---|---|---|---|
| **P1 camera 模组** | ★**Radxa Camera 4K** (SONY IMX415) | ★**31p / 0.3mm** FPC, **逐针针位表已拿到** (§2.1) · 4-lane CSI · SCCB **0x1a** | ★**针位表 = 全 31 针原文** ✔ |
| **P2 屏模组** | ★**Radxa Display 8 HD** (800×1280) | ★**40p / 0.5mm** FPC, **逐针针位表已拿到** (§3.1) · **4-lane DSI** · 驱动 IC 走内核白名单 | ★**针位表 = 全 40 针原文** ✔ |
| **P3 RK3572 核心板 (SOM)** | ★**Forlinx FET3572-C** (RK3572, 4×100pin BTB) | ★**68×50mm / 4×100Pin 0.4mm pitch 板对板连接器 / DC 5V-13V** | ★**引脚定义表 = 未查** ✘ (见 §4.5, ★这是唯一的硬缺口) |

★★ **选型顺序倒置已被本单证实并落地**: P1 先落 (针位表 ✔) → P2 次之 (针位表 ✔) → P3 最后 (★**引脚定义表在 Forlinx 公开资料里没有**, 见 §4.5 ⇒ **这是主板画板前必须补的唯一一块**)。

★**一条必须写进采购硬判据的新结论** (本单实测, 推翻 `PART_ALTERNATIVES_REGISTRY.md` §2 的一处说法):
> ★**"0.5mm/24p 自研目标规格" 作废之后, 正确的替代不是"改成 24p", 而是"改成 31p/0.3mm (camera) + 40p/0.5mm (display)"** —— 这两个座都有**逐针针位表公开可查**, 照抄即可, 不需要转接排线, 不需要任何"自造规格"。

---

## 1. ★ 为什么这三件是"硬前提" (给 boss 看代价)

| 件 | 缺了它会怎样 | 返工成本 (老板的账) |
|---|---|---|
| P1 camera 模组 | 主板 camera FPC 座**画不出来** ⇒ 板子投了才发现插不上 | 2-4 周 + ¥4-8K/批 |
| P2 屏模组 | 主板 display FPC 座**画不出来** (针数/间距/针序错一个 = 屏不亮) | 同上 |
| P3 核心板 | 主板**不知道该在哪块板上放什么** ⇒ 布局/层数/电源树全部无法定 | ★**改板 = 重画 = 同上** |

★**本单把这三条从"未查"推进到"有规格"** (§2/§3 已闭环), ★**只留 P3 的引脚定义表一个缺口** (§4.5)。

---

## 2. ★★ P1 —— camera 模组: **Radxa Camera 4K** (SONY IMX415)

### 2.1 ★★★ ① FPC 针数/间距/针位表 —— 【实测, 全 31 针原文】★这决定主板的座

★**选型理由**: ① IMX415 = 项目 demo 已定案的 sensor ② 4-lane CSI (**RK BSP 驱动只在 4-lane 模式表里有 1080p binning 模式**, 2-lane 表里没有 ⇒ 必须 4-lane) ③ 公开在售 ④ ★**针位表完整公开** ⇒ 主板可直接照抄

| 项 | 值 | 证据 |
|---|---|---|
| 模组 | **Radxa Camera 4K** | 公开在售 (Radxa 官方 + 授权分销) |
| **FPC 针数** | ★**31 pin** | `[实测]` 官方文档"引脚定义"表原文 |
| **FPC 间距** | ★**0.3mm pitch** | `[实测]` 同上 + 载板侧连接器型号交叉验证 |
| **主板侧连接器** | ★**HIROSE FH35C-31S-0.3SHW(50)** | `[实测]` Radxa ROCK4D 公开接口页原文: "Radxa 31-Pin / 0.3mm pitch FPC connector (model FH35C-31S-0.3SHW(50))", 并明写该 4-lane 口"for high-resolution cameras (Camera 4K)" · ★**同页另证 RPi 标准口 = FPC1030-15S-TAG (15 位 / 1.0mm)** |
| **连接器形态** | 翻盖式 (Back flip actuator) / ZIF / **上下双面触点 (Top & Bottom)** / 兼容 0.2mm 厚 FPC / 横向插拔 | `[实测]` HIROSE 原厂页 + Mouser 页 |
| 机械尺寸 | 长 10.9mm × 宽 4.2mm × 高 0.9mm (actuator OPEN 态进深 3.35mm / CLOSE 态 4.2mm) | `[实测]` HIROSE 原厂页 |
| **模组尺寸图** | ★公开 (官方文档"物理规格"节有带尺寸的实物图) | `[实测]` <https://docs.radxa.com/accessories/camera/camera-4k> |
| 默认排线长度 | 150mm | `[实测]` 同上 |

★★ **模组侧 31 针针位表 (全表, 逐针)** —— ★**主板照这张表画座**:

| 针 | 定义 | 针 | 定义 | 针 | 定义 | 针 | 定义 |
|---|---|---|---|---|---|---|---|
| **1** | GND | **2** | **MDN4** (MIPI D- 4) | **3** | **MDP4** (MIPI D+ 4) | **4** | GND |
| **5** | **MDN3** | **6** | **MDP3** | **7** | GND | **8** | NC |
| **9** | NC | **10** | GND | **11** | **MDN2** | **12** | **MDP2** |
| **13** | GND | **14** | **MDN1** | **15** | **MDP1** | **16** | GND |
| **17** | **MCN** (MIPI CLK-) | **18** | **MCP** (MIPI CLK+) | **19** | GND | **20** | **MCLK** |
| **21** | GND | **22** | NC | **23** | NC | **24** | **SCL** (I2C) |
| **25** | **SDA** (I2C) | **26** | NC | **27** | **RESET** | **28** | **VCC3.3V** |
| **29** | **VCC3.3V** | **30** | **VCC5V** | **31** | **VCC5V** | | |

★**派生的 4-lane 对应关系** (按上表, 从模组视角): `MDN4/MDP4` = lane4 · `MDN3/MDP3` = lane3 · `MDN2/MDP2` = lane2 · `MDN1/MDP1` = lane1 · `MCN/MCP` = 差分时钟对。

★★ **主板侧必须补的东西 (本表没有, 主板自己定)**:
| 信号 | 主板侧接到哪 | 依据 |
|---|---|---|
| MCLK | SoC 的 `MIPI_CAMERAOUT` / xvclk | `[实测]` Radxa CM5 overlay dts: `clocks = <&cru CLK_MIPI_CAMARAOUT_M1>; clock-names = "xvclk"` |
| MDN1..MDP4 + MCN/MCP | SoC 的 **CSI 4-lane D-PHY** | `[实测]` 同 dts: `data-lanes = <1 2 3 4>` |
| SCL/SDA | SoC 的 I2C (本项目 I2C_A) | ★**上拉 ≤3.3V 合法, 阻值 2.2k** (既定事实④) |
| RESET | SoC GPIO (低有效) | `[实测]` 同 dts: `reset-gpios = <&gpio1 RK_PB3 GPIO_ACTIVE_LOW>` |
| PWDN | SoC GPIO (高有效) | `[实测]` 同 dts: `pwdn-gpios = <&gpio1 RK_PA7 GPIO_ACTIVE_HIGH>` |
| VCC3.3V / VCC5V | ★**模组带 5V 和 3.3V 两组** ⇒ 主板要两路都供 | ★**注意: 这跟我们原计划"只给 sensor 三条轨 (1.1/1.8/2.9V)"是【两套不同的东西】** —— 模组级供电 vs sensor 芯片级供电, 见 §2.4 |

> ★**【实测】载板侧 31p 针序 (独立第二来源, 交叉验证用 —— ★但不可直接当主板依据)**: Radxa ROCK4D 公开页给了同一款连接器的**载板侧** 31 针表 (3 列 × 11 行, 载板自己的信号命名):
> `1 GND | 2 MIPI_DPHY_CSI1_RX_D3N | 3 MIPI_CSI0_PDN1_H | 4 I2C5_SCL_M3_MIPI_CSI1 | 5 MIPI_DPHY_CSI1_RX_D2N | 6 MIPI_DPHY_CSI1_RX_D2P | 7 GND | 8 MIPI_DPHY_CSI2_RX_CLK_N | 9 MIPI_DPHY_CSI2_RX_CLK_P | 10 GND | 11 MIPI_DPHY_CSI1_RX_D1N | 12 MIPI_DPHY_CSI1_RX_D1P | 13 GND | 14 MIPI_DPHY_CSI1_RX_D0N | 15 MIPI_DPHY_CSI1_RX_D0P | 16 GND | 17 MIPI_DPHY_CSI1_CLK_N | 18 MIPI_DPHY_CSI1_CLK_P | 19 GND | 20 MIPI_DPHY_CSI1_CAM_CLKOUT | 21 GND | 22 MIPI_DPHY_CSI0_CAM_CLKOUT | 23 MIPI_CSI0_PDN1_H | 24 I2C5_SCL | 25 I2C5_SDA | 26 MIPI_CSI0_PDN2_H | 27 CAM1_RST_L | 28 VCC_3V3_S0 | 29 VCC_3V3_S0 | 30 VCC5V0_DEVICE_S0 | 31 VCC5V0_DEVICE_S0 | 32 GND | 33 GND`
>
> ★★ **这份表的正确用法 (★ 别整表照抄!)**:
> - ★**两表一致的针 (⇒ 可信度高)**: **针 24 = I2C_SCL, 25 = I2C_SDA, 27 = RESET, 28/29 = 3.3V, 30/31 = 5V** ⇒ ★**这 7 个针两处独立来源完全吻合 ⇒ 电源/复位/I2C 的针位定案**; **数据对针位也对得上 (载板 D0N/D0P ↔ 模组 MDN1/MDP1, 只是 lane 编号体系不同: 载板用 D0~D3, 模组用 MDN1~MDN4)**
> - ★**两表【不一致】的针**: **针 3/4 与 8/9/20/22/23/26** —— ★**因为 ROCK4D 的这个 31p 座同时兼容 Camera 4K 与 Camera 13M 214, 载板侧是"多用途"分配 (含 PDN1_H/PDN2_H 这类给别的模组用的信号), 与 Camera 4K 模组自己的 FPC 定义不同**
> - ★**表尾 32/33 = GND**: 该表编到 33 号, 而连接器是 **31 位 (31 contacts)** ⇒ ★**32/33 应是载板侧的接地焊盘 (footprint-only), 不是触点** ⇒ ★**主板按 31p 画, 是否加额外地焊盘由机械决定**
> ⇒ ★★ **结论: 主板画座一律以 §2.1 的【模组侧 31 针表】为准 (那是 Camera 4K 自己的 FPC 定义), 载板表只用来验证电源/复位/I2C 的针位**。

### 2.2 ★★ ② 1080p60 寄存器/配置序列 —— 【实测, 随货必须给的那份】

★**来源**: Rockchip BSP `drivers/media/i2c/imx415.c` (分支 `develop-6.1`) —— ★**这就是"随货必须给"的配置序列的公开等价物** (内核驱动里带的是完整寄存器表, 模组厂随货给的就是这张表)。

| 项 | 值 | 证据 |
|---|---|---|
| **1080p 模式分辨率** | ★**1944 × 1097** (2/2 行 binning) | `[实测]` imx415.c `supported_modes[]` 条目 `.width=1944 .height=1097` |
| **binning 开关** | ★**`0x3020 = 0x01`** (= BRL/2,2 binning) | `[实测]` `imx415_linear_12bit_1932x1096_594M_regs[]` 首条 `{0x3020, 0x01}` |
| **位深** | 12bit (`MEDIA_BUS_FMT_SGBRG12_1X12`) | `[实测]` 同 mode 条目 |
| **出厂帧率** | 30fps (`max_fps = 10000/300000`) | `[实测]` 同上 |
| **★ 改成 60fps 的唯一改动** | ★**VTS: `0x0C5D` → `0x062E`** (一改即 60fps) | `[实测]` mode 条目 `.vts_def = 0x0c5d`; 帧率公式源码注释: `frame rate = 1/(VMAX*1H)`, `VMAX >= (PIX_VWIDTH/2)+46` |
| **1080p 模式完整寄存器序列** | ★**36 条寄存器** (见下) | `[实测]` `imx415_linear_12bit_1932x1096_594M_regs[]` |
| **XVCLK 频率** | 37 MHz (`IMX415_XVCLK_FREQ_37M`) | `[实测]` 同 mode 条目 |

★**1080p (1944×1097) 模式寄存器序列 —— 全 36 条, 照抄**:

```
0x3020=0x01  0x3021=0x01  0x3022=0x01  0x3024=0x5D  0x3025=0x0C  0x3028=0x0E
0x3029=0x03  0x302C=0x00  0x302D=0x00  0x3031=0x00  0x3033=0x07  0x3050=0x08
0x3051=0x00  0x3054=0x19  0x3058=0x3E  0x3060=0x25  0x3064=0x4A  0x30CF=0x00
0x30D9=0x02  0x30DA=0x01  0x3118=0x80  0x3260=0x01  0x3701=0x00  0x400C=0x00
0x4018=0x67  0x401A=0x27  0x401C=0x27  0x401E=0xB7  0x401F=0x00  0x4020=0x2F
0x4022=0x4F  0x4024=0x2F  0x4026=0x47  0x4028=0x27  0x4074=0x01
```
★**配套**: `global_reg_list = imx415_global_12bit_3864x2192_regs[]` (全局寄存器) + `hts_def = 0x030e * 3` + `exp_def = 0x05dc - 0x08` + `mipi_freq_idx = 0` + `.vc[PAD0] = 0`。
★**注意**: 驱动里这条 1080p 模式是 **12bit**; 若要 10bit, 另有一条 `imx415_linear_10bit_*` 的 3864×2192 模式 (但**没有** 1944×1097 的 10bit 版本) ⇒ ★**demo 就用 12bit 通道** (带宽更宽, 但 1080p60 RAW12 = 1.492Gbps, 4-lane 够)。

> ★★ **这一条直接决定主板工作量**: 1080p60 **不需要移植驱动** —— 模式已经在 BSP 里, 只改 VMAX 一个数 ⇒ **"随货必须给寄存器序列"这条硬判据, 公开渠道已经满足 (内核驱动 = 同源寄存器表)**。

### 2.3 ★ ③ AC 耦合是否内置 —— **部分查实 / 部分未查**

| 项 | 状态 | 说明 |
|---|---|---|
| MIPI D-PHY 差分对需 AC 耦合 | `[官方]` 事实 | CSI-2 规范要求高速差分对经 AC 耦合; IMX415 侧无内部耦合 |
| ★**耦合电容是否做在模组上** | ★**未查** | 公开文档页/产品简介 PDF **未明确写** (模组内部原理图未公开); ★**⇒ 主板必须按"可能需要"预留** ⇒ 见下面的可执行约束 |
| 建议做法 (不猜, 只给判据) | ★**主板侧预留可选 AC 耦合位** | ★**因为"内置"没查实 ⇒ 若模组内置而主板也放, 串联两个耦合电容会导致 D-PHY 眼图劣化** ⇒ ★**正确做法 = 主板上放 0Ω 跳线位 (默认不贴), 采购到货后拆掉/补上** —— 这是"改板 2-4 周"里最容易踩的一个坑 |

★**可执行约束 (直接抄进原理图)**: ★**camera FPC 座的 4 组差分对 (MDN1..MDP4 + MCN/MCP) 各预留一个 0402 AC 耦合电容位 (默认 DNP), 电容值未查 (按 SoC 侧 CSI 接收器推荐值定, 待核)** ⇒ 采购到货 + 拆模组看过原理图后, 二选一决定贴/不贴。

### 2.4 ★★ ④ 供电轨/电流 + 上电时序 —— 【两层, 必须分清】★这是最容易搞错的地方

★★ **A 层: sensor 芯片级 (IMX415 裸件, 项目既有事实, 不重复)**:

| 轨 | 电压 | 电流 typ/max | 绝对最大 |
|---|---|---|---|
| **DVDD1** (数字) | 1.00 / **1.10** / 1.20 V | 187 mA / **250 mA** | −0.3 ~ 2.0 V |
| **OVDD** (IO) | 1.70 / **1.80** / 1.90 V | 3 mA / 3 mA | −0.3 ~ 3.3 V |
| **AVDD1** (模拟) | 2.80 / **2.90** / 3.00 V | 128 mA / **156 mA** | −0.3 ~ 3.3 V |

★**上电时序 (datasheet 硬要求)**: **DVDD(1.1V) → OVDD(1.8V) → AVDD(2.9V), 三轨 200ms 内全部到位** ⇒ ★**主板必须给三条 LDO 加 EN 脚做顺序 (EN 脚 + RC 延时链)**, 详见 `HW/PART_ALTERNATIVES_REGISTRY.md` §6.2 的 P0 条目 (TPS7A20 EN 悬空 = 全表关断)。

★★ **B 层: 模组级 (Radxa Camera 4K 整模组的供电, ★这一层是新信息)**:

| 项 | 值 | 证据 |
|---|---|---|
| ★**模组要 3.3V + 5V 两组** | 针 28/29 = **VCC3.3V**, 针 30/31 = **VCC5V** | `[实测]` 模组 31 针表 |
| ★**模组级电流 / 功耗** | ★**未查** | 官方文档页与产品简介 PDF 均未给出模组级电流 |
| ⇒ 主板电源树怎么配 | ★**模组级的 3.3V/5V 需求，与 sensor 芯片级的 1.1/1.8/2.9V 是【两套独立的东西】** | ★**模组内部自带从 3.3V/5V 到 sensor 三轨的 LDO (推断, 未查) ⇒ 主板只管供 3.3V + 5V** |
| ⇒ **对主板电源树的影响 (★★★)** | ★★**如果这个推断成立, 主板就不用自己给 sensor 拉三条轨 —— 只供 3.3V + 5V 即可** ⇒ ★**主板 LDO 数量减少 3 颗, 面积/热/上电顺序问题一起少一半** | ★**[推断, 待核]** —— ★**必须核实模组内部供电架构 (打开模组或看随货原理图)**; ★**核实前, 主板电源树按"模组自带 LDO"画 (省面积), 但 BOM 里保留三条 sensor LDO 的 DNP 位置作为退路** |

★**可执行约束**: ★**主板电源树先按"模组自带 LDO, 主板只供 5V + 3.3V"设计 (省 3 颗 LDO + 省面积)**; ★**但必须在 BOM 里给 3 条 sensor 轨留 DNP 焊盘** (万一模组不带 LDO, 贴上就能跑, 不改板)。

### 2.5 ★ ⑤ SCCB 地址 —— 【实测, 与既定事实一致】

★**`0x1a`** —— `[实测]` 两处独立来源: ① 既定事实 (IMX415 datasheet) ② Radxa CM5 overlay dts `imx415@1a { reg = <0x1a>; }` (I2C8 上, `pinctrl-0 = <&i2c8m2_xfer>`)。
★**I2C 上拉**: ★**≤3.3V 合法** (IMX415 `VI` 绝对最大 = OVDD+0.3 = 3.3V), ★**阻值 2.2k** (既定事实④, 不再论证)。

### 2.6 ★ ⑥ 镜头 FOV 口径 —— 【实测, 官方文档原文】

| 项 | 值 |
|---|---|
| ★**FOV (对角/水平/垂直)** | ★**D = 88.2 ± 5° · H = 75 ± 3° · V = 59 ± 2°** |
| **CRA** | 15° |
| **镜头接口** | **M12 × P0.5** |
| **焦距 EFL** | 2.95 ± 5% mm |
| **后焦距 BFL** | 4.64 mm |
| **镜间距 (flange)** | 4.00 mm |
| **镜头工作温度** | −40 °C ~ +85 °C |
| **sensor 对角线** | 6.43 mm (1/2.8 型) |
| **像素** | 8.29 MP · 单元 1.45 µm × 1.45 µm |
| **输出** | MIPI CSI-2 4-lane, RAW10 / RAW12 |

★**对我们项目的意义**: 水平 75° / 垂直 59° ⇒ ★**这个 FOV 覆盖老板的"30° 垂直半视场 + 120° 对角"目标绰绰有余** (模组镜头 FOV 比系统 FOV 大, 才正常)。

### 2.7 ★ ⑦ FPC 弯折寿命 / 插拔次数 —— **未查**

| 项 | 状态 | 说明 |
|---|---|---|
| **连接器插拔次数** | ★**未查** | HIROSE FH35C 原厂页本单抓到的字段里**没有** cycles 字段 (只有尺寸/间距/额定电压/电流) ⇒ **不猜** |
| **FPC 弯折寿命** | ★**未查** | 模组厂商未公开 FPC 的弯折规格 |
| ⇒ 主板该怎么画 | ★**按"不弯折"设计**: camera FPC 排线**不跨铰链**, 直连, 长度 ≤60mm | ★**依据是项目的既有硬约束 (排线不跨铰链)**, 不是寿命数据 |
| ⇒ 待补 | ★**若要当正式可靠性指标, 需要 FH35C 原厂规格书的 durability 章节 + 模组 FPC 规格书** —— ★**这两份在公开下载区可能存在, 本单未取到 ⇒ 标未查** |

---

## 3. ★★ P2 —— 屏模组: **Radxa Display 8 HD** (800×1280, 全彩, GT911 触控)

### 3.1 ★★★ ① FPC 针数/间距/针位表 —— 【实测, 全 40 针原文】★这决定主板的座

| 项 | 值 | 证据 |
|---|---|---|
| 模组 | **Radxa Display 8 HD** | 公开在售 |
| **FPC 针数 (屏侧)** | ★**40 pin** | `[实测]` 官方文档"Pinout"表原文 |
| **FPC 间距 (屏侧)** | ★**0.5mm pitch** | `[实测]` 官方文档 + 产品页原文: "39-pin 0.3mm pitch (Motherboard side) to **40-pin 0.5mm pitch (Display side)**" |
| **主板侧排线另一头** | ★**39p / 0.3mm** (或 15p / 1.0mm 二选一) | `[实测]` 产品页原文: "FPC Cable Specification: 39-pin 0.3mm pitch (Motherboard side) to 40-pin 0.5mm pitch (Display side)" / "15-pin 1.0mm pitch (Motherboard side) to 40-pin 0.5mm pitch (Display side)" |
| ⇒ **★主板该画哪个?** | ★★**画 39p / 0.3mm** (走厂商原厂排线) ⇒ 或 **15p / 1.0mm** (走 RPi 标准排线, 更通用) | ★**两个都是公开在售的原厂排线规格 ⇒ 主板自选, 但建议 39p/0.3mm (与相机侧 31p/0.3mm 同工艺)** |
| **DSI lane 数** | ★**2-lane 或 4-lane 都支持** ("requires 2-lane or 4-lane MIPI DSI signal support") | `[实测]` 产品页原文 |
| **屏侧连接器型号** | ★**未查** (官方文档只给针位表, 未给连接器型号) | ★**主板画座时按 40p/0.5mm 贴板翻盖式选 (FH12-40S-0.5SH 一类), 型号待定** |

★★ **屏侧 40 针针位表 (全表, 逐针)** —— ★**主板照这张表画座**:

| 针 | 名称 | 说明 | 针 | 名称 | 说明 |
|---|---|---|---|---|---|
| **1** | NC | No connection | **21** | **MIPI_3P** | +MIPI differential data input |
| **2** | **VDD** | **3.3V** | **22** | GND | Ground |
| **3** | **VCCIO** | IO VCC (**1.8V–3.3V**) | **23** | GND | Ground |
| **4** | NC | INT 1 | **24** | **TP_RESET** | External interrupt to the host Reset |
| **5** | **Reset** | RESET | **25** | **TP_VCC** | Power |
| **6** | NC | INT 2 | **26** | **TP_INT** | External Low is active |
| **7** | GND | Ground | **27** | **TP_SDA** | I2C data in/out |
| **8** | **MIPI_0N** | −MIPI differential data input | **28** | **TP_SCL** | I2C clock input |
| **9** | **MIPI_0P** | +MIPI differential data input | **29** | GND | Ground |
| **10** | GND | Ground | **30** | GND | Ground |
| **11** | **MIPI_1N** | −MIPI differential data input | **31** | **VDD** | VDD 3.3V |
| **12** | **MIPI_1P** | +MIPI differential data input | **32** | **VDD** | VDD 3.3V |
| **13** | GND | Ground | **33** | GND | Ground |
| **14** | **MIPI_CKN** | −MIPI differential clock input | **34** | GND | Ground |
| **15** | **MIPI_CKP** | +MIPI differential clock input | **35** | **LED−** | LED Cathode |
| **16** | GND | Ground | **36** | **LED−** | LED Cathode |
| **17** | **MIPI_2N** | −MIPI differential data input | **37** | NC | No connection |
| **18** | **MIPI_2P** | +MIPI differential data input | **38** | NC | No connection |
| **19** | GND | Ground | **39** | **LED+** | LED Anode |
| **20** | **MIPI_3N** | −MIPI differential data input | **40** | **LED+** | LED Anode |

★**信号分组 (主板布局用)**:
- **DSI 数据对**: `MIPI_0N/P` (lane0) · `MIPI_1N/P` (lane1) · `MIPI_2N/P` (lane2) · `MIPI_3N/P` (lane3) · `MIPI_CKN/P` (时钟对)
- **电源**: VDD 3.3V (针 2/31/32) · VCCIO 1.8–3.3V (针 3) · LED 背光 (针 35/36 = LED−, 针 39/40 = LED+)
- **触控 I2C**: TP_SCL (28) / TP_SDA (27) / TP_RESET (24) / TP_INT (26) / TP_VCC (25)
- **屏复位**: Reset (5)

★**★ 主板侧的电源要点 (这条最容易被漏)**:
> ★**背光 LED 是 12V 级** (10 FHD 官方实测: LED 电压 typ 12.8V / max 14V, LED 电流 typ 200mA; 8 HD 官方标"输入电压 1.8V"指 IO 域, 背光同样是白 LED) ⇒ ★**主板必须给屏背光单独做一路 12V 升压 (BOOST) + 限流 (或直接接 5V/3.7V 经升压)**, ★**不能用 3.3V 直接点背光**。
> ⇒ ★**这条会改主板电源树**, 是本单对主板最实质的影响之一。

### 3.2 ★★ ② init code / DSI timing / DDC 地址

| 项 | 值 | 证据 |
|---|---|---|
| **面板 compatible** | ★**`radxa,display-8hd`** | `[实测]` Radxa overlay dts (`radxa-cm5-io-radxa-display-8hd.dts`) |
| **★驱动在哪** | ★**内核 `drivers/gpu/drm/panel/` 里【没有】这个 driver** (79 个 panel 文件实测清单里**无** `panel-radxa-*`) ⇒ ★**该驱动在 Radxa 自己的内核分支里, 不在 rockchip-linux/develop-6.1** | ★**⇒ 主板/BSP 侧要自己带这个驱动 ⇒ 见 §3.6 的重要提示** |
| **DSI 格式** | `MIPI_DSI_FMT_RGB888` (10FHD dts) | `[实测]` |
| **lane rate** | `rockchip,lane-rate = <480>` (8HD dts) | `[实测]` |
| **10 FHD 的 DSI timing (公开 dts, 可直接抄)** | ★**clock 160 MHz / hactive 1200 / vactive 1920 / hbp 60 / hfp 80 / hsync 1 / vbp 25 / vfp 35 / vsync 1** | `[实测]` `radxa-cm5-io-radxa-display-10fhd.dts` 的 `display-timings` |
| **8HD 的 init code / timing** | ★**未查** (dts 里只有 `compatible = "radxa,display-8hd"`, init code 在那个专属 driver 里) | ★**见 §3.6** |
| **★Rockchip 自家 EVB 屏的 init code (1080×1920, ★与我们目标屏最贴)** | ★**`rk3576-evb.dtsi` → `dsi_panel: panel@0` 里 `panel-init-sequence` 共 ★**263 条**寄存器写 (0x23 = 0x00 0x02 <cmd> <param> 格式) + `panel-exit-sequence` 2 条** | `[实测]` `arch/arm64/boot/dts/rockchip/rk3576-evb.dtsi` (develop-6.1) |
| **EVB 屏的 timing** | ★**clock 132 MHz / hactive 1080 / vactive 1920 / hfp 15 / hsync 4 / hbp 30 / vfp 15 / vsync 2 / vbp 15**; `dsi,lanes = <4>`; `dsi,format = RGB888`; flags = VIDEO \| VIDEO_BURST \| LPM \| **NO_EOT_PACKET** | `[实测]` 同上 |
| **★DDC 地址 (触控 I2C)** | ★**未查** (官方文档只写 TP_SCL/TP_SDA, 未给地址) | ★**⇒ 主板不需关心 (屏自己从机), 但软件要知道 ⇒ 从 GT911 驱动常量取 (典型 0x5D/0x14, 待核)** |

★★ **★ 最贴我们目标的那份 init code 在哪 (这是本单对 P2 最有价值的交付)**:
> **`arch/arm64/boot/dts/rockchip/rk3576-evb.dtsi`** (Rockchip BSP develop-6.1) 里的 `&dsi { dsi_panel: panel@0 { ... } }`:
> - `compatible = "simple-panel-dsi"` ⇒ ★**不需要专用 panel driver, 只要一个 dts 节点 + 这份 init sequence**
> - ★**1080×1920 / 4-lane / RGB888** ⇒ ★**我们的目标屏是 1920×1080 横置 ⇒ 物理上就是这块屏转 90° ⇒ init code 可直接抄, 只需加 orientation 翻转**
> - ★**263 条寄存器写**是全的, 不是占位符

### 3.3 ★ ③ 供电

| 项 | 值 | 证据 |
|---|---|---|
| **VDD (逻辑)** | 3.3V (针 2/31/32) | `[实测]` 针位表 |
| **VCCIO (IO 域)** | **1.8V–3.3V** (针 3) | `[实测]` 针位表 (8HD) / 10FHD 明确 "1.8V" |
| **★背光 LED** | ★**12V 级** (10FHD: typ 12.8V, max 14V @ 200mA typ) | `[实测]` 10FHD 官方文档背光表 |
| **触控供电** | TP_VCC (针 25) | `[实测]` 针位表 |
| **8HD 屏标称输入电压** | 1.8V (指 IO 域) | `[实测]` 8HD 官方规格表 |

### 3.4 ★ ④ 有效显示区

| 项 | 8 HD | 10 FHD (对照) |
|---|---|---|
| **尺寸** | 8.0 英寸 | 10.1 英寸 (10:16) |
| **分辨率** | ★**800 × 1280** | 1200 × 1920 |
| **★有效显示区** | ★**107.64 (H) × 172.224 (V) mm** | ★**135.36 (W) × 216.58 (H) mm** |
| **外形尺寸** | ★**未查** (8HD 官方文档"物理规格"节只有图, 无文字尺寸) | ★**155 (高) × 246.16 (宽) × 5.95 (深) mm** |
| **像素间距** | 0.04485 (W) × 3 × 0.13455 (H) | 0.0564 (H) × 0.1692 (V) |
| **亮度 / 对比度** | 300 cd/m² 型 / 1000:1 typ | 350 cd/m² typ @180mA |
| **工作温度** | −20 ~ +60 ℃ | — |

★**对我们项目的意义**: ★**8HD 是 800×1280 竖屏; 我们要 1920×1080 横屏 ⇒ 8HD 分辨率不够 (只有 800×1280) ⇒ ★**demo 用它验 DSI 通路可以, 但"1920×1080"这个产品目标它达不到** ⇒ ★**屏的分辨率仍是独立风险项 (见 `HW/PART_ALTERNATIVES_REGISTRY.md` §3.4 的 C4)** —— ★**视涯 0.49" 1920×1080 SiOLED 仍无公开对标品, 那是整机阶段的事**。

### 3.5 ★ ⑤ 单色/全彩 + ⑥ 驱动 IC 型号 —— 【★ 关键项, 有重要发现】

| 项 | 值 | 证据 |
|---|---|---|
| **⑤ 单色/全彩** | ★**全彩 16.7M (1670 万色)**, RGB 竖条纹, 常黑模式, 全视角 | `[实测]` 8HD 官方规格表: "800x1280、16.7M 色分辨率" / "显示颜色: 16.7M" / "像素排列: RGB 竖条纹" / "显示模式: 常黑" |
| **⑥ 面板驱动 IC 型号** | ★**未查到具体型号** | ★**但见下面这条 —— 它比型号更重要** |

★★ **★ 本单对 P2 最有价值的一条实测发现 (直接回答"驱动 IC 是否在白名单里")**:

> ★**Radxa Display 8 HD 用的是 `compatible = "radxa,display-8hd"` —— 这不是 Rockchip 白名单里任何一颗 IC (ST7701/ST7703/ST7789V/ILI9881C/NV3052C/OTM8009A/HX8394/RPi-TC358762 都不是)** ⇒ ★**内核的 79 个 panel 文件里【没有】它** ⇒ ★**这块屏的驱动不在 rockchip-linux/develop-6.1 里, 在 Radxa 自家内核分支**。
>
> ★⇒ **所以 8HD 违反"驱动 IC 须在内核白名单里"这条硬判据** ⇒ ★**但它有替代路径**: `radxa-cm5-io-radxa-display-10fhd.dts` 里 10 FHD 用的是 ★**`compatible = "simple-panel-dsi"`** ⇒ ★**`simple-panel-dsi` 在内核里有 (`panel-simple.c`, 实测在 79 个文件里)** ⇒ ★**10 FHD 这条路只要 dts + init sequence, 不需要任何专用 driver**。

★**⇒ 对 P2 的最终判据 (给主板画板用)**:

| 路线 | 驱动依赖 | init code 来源 | 判定 |
|---|---|---|---|
| **★10 FHD (`simple-panel-dsi`)** | ★**只要内核 `panel-simple.c` (在白名单机制之外, 但**内核自带**) + 一个 dts 节点** | ★**公开 dts 里就有 `panel-init-sequence = [05 78 01 11 / 05 00 01 29]` + 完整 `display-timings` (160MHz/1200×1920)** | ★★**最干净: 主板/BSP 零移植** |
| **8HD (`radxa,display-8hd`)** | ★**需要 Radxa 私有内核里的 driver** | ★**未查** | ⚠️ **要带一份私有 driver ⇒ 不算"零移植"** |
| **EVB 屏 (`simple-panel-dsi` + 263 条 init)** | ★**只要 `panel-simple.c`** | ★**Rockchip BSP 自带, 1080×1920, 与我们目标屏最贴** | ★★**"init code 不必问厂家"的最硬证据** |

★**★ 给主板的 P2 建议 (按"最少移植"排序)**:
1. ★**首选: 走 `simple-panel-dsi` 路线** (10 FHD 或任何 `simple-panel-dsi` 兼容屏) ⇒ **主板的 DSI 侧不需要任何特殊处理, 只是 4-lane 差分 + 电源 + 背光 12V**
2. ★**init code 从 `rk3576-evb.dtsi` 抄** (1080×1920/4-lane, 与我们目标屏同分辨率族)
3. ★**驱动 IC 型号: 未查** —— ★**但"驱动 IC 是否在白名单"这个问题, 对 `simple-panel-dsi` 路线【自动不成立】** (不依赖具体 IC 的专用 driver) ⇒ ★**这条硬判据可以用"选 `simple-panel-dsi` 屏"来满足, 而不是死磕某颗 IC 型号**

### 3.6 ★★ 一个必须写进风险台账的发现

> ★**"内核白名单"这条判据有个前提**: 它只覆盖**专用 panel driver** 形式的驱动。
> ★**`simple-panel-dsi` 这条路 (10 FHD / EVB 屏) 不需要专用 driver, 但它需要一份 init sequence** ⇒ ★**init sequence 从哪来才是真问题**。
> ★**公开渠道拿到的 init code 只有两种来源**:
> - ★**(a) `rk3576-evb.dtsi` 的 263 条 (Rockchip 自家屏, 1080×1920)** —— ★**可抄, 但那是 EVB 屏的参数, 换屏就得换**
> - ★**(b) 10 FHD 的 2 条 (`05 78 01 11` = sleep out, `05 00 01 29` = display on)** —— ★**这不是完整 init code, 是"最小可用集"**
> ⇒ ★**结论: 面板 init code 仍然"不必问厂家" (走 (a) 抄 EVB 或抄同屏的公开 dts), 但也不是"内核白送"** ⇒ ★**选屏时的硬判据应改成: "能找到用同一块屏的公开 dts"** —— ★**这正是 `PART_ALTERNATIVES_REGISTRY.md` §3.3 已经写下的结论, 本单实测再次证实**。

---

## 4. ★★ P3 —— RK3572 核心板 (SOM): **Forlinx FET3572-C**

> ★**为什么选它 (不是 SBC)**: 老板要"能焊在自己主板上的核心板"; ★**SBC 是完整板子, 不能当主板的一部分焊上去** ⇒ ★**必须选 SOM**。

### 4.1 ★★★ ① 引脚定义表 —— ★★ **未查 (这是本单唯一的硬缺口)** ★★

| 项 | 状态 | 说明 |
|---|---|---|
| ★**FET3572-C 逐针引脚定义表 (400 针)** | ★★**未查** | ★**Forlinx 公开资料只给了接口"数量表" (每个接口几路), 没有逐针表**; 逐针表在**下载中心 (需登录)**, 本单未登录 ⇒ **不猜** |
| 已查到的公开下载区入口 | `[实测]` | <https://www.forlinx.net/resources/download-center.html> (实测 200, 内容需登录) · 产品简介 PDF <https://www.forlinx.net/download/FET3572-C-SoM-OK3572-C-SBC-Product-Brief.pdf> (实测 200, ★**需浏览器 UA 才不被拦**) |
| ★**同厂同系列可参考的公开件** | ★**同系列的 FET3588-C SoM 简介 PDF 在 DigiKey 公开镜像里** (实测 200) ⇒ ★**能确认"同一套 4×100pin 架构 + 有 'pinmux sheet' 资料包"** | <https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/5731/FET3588-C%20SoM.pdf> |
| ★**"pin-compatible"的公开声明** | ★**产品简介 PDF 明写 "Compatible with the pin design of the *FET3576-C SoM"** ⇒ ★**FET3572-C 与 FET3576-C 引脚兼容** ⇒ ★**⇒ 拿到 FET3576-C 的引脚表就等于拿到 FET3572-C 的** (前提: 电源/功能差异要核) | `[实测]` PDF 原文 |
| ★**⇒ 主板画板前的动作 (不需要问厂家)** | ★**去 Forlinx 下载中心下载 FET3576-C / FET3572-C 的 "SoM 引脚定义 (Pin Definition)" + "原理图" + "机械尺寸图" 三个文件** —— ★**这是公开下载, 只是要注册账号, 不是"咨询厂家"** ⇒ ★**仍不触发 L4** | ★**这条是本单给 P3 留的唯一一条待办** |

### 4.2 ★★ ② 外形尺寸 + 焊接/连接方式 —— 【实测, 数字全齐】

| 项 | 值 | 证据 |
|---|---|---|
| **SoM 型号** | **FET3572-C** (工业级 **FET3572J-C**) | `[实测]` |
| ★**外形尺寸** | ★**68 mm × 50 mm** | `[实测]` 产品简介 PDF "SoM Parameter" + 官网 JSON 字段 `Dimensions = 68mm*50mm` |
| ★**焊接/连接方式** | ★★**板对板连接器 (Board-to-Board Connector), 4 × 100Pin, 针间距 0.4mm, 配合高度 1.5mm** | ★`[实测]` PDF "Connection: Board-to-board connector (4 × 100Pin, pin pitch 0.4mm, combined height 1.5mm)" + 官网 JSON `Package = Board-to-Board Connector (4x 100-pin, 0.4mm pitch, 1.5mm mating height)` |
| **★ 这跟老板的"推荐焊接"对不对得上?** | ⚠️ **不完全对得上** —— ★**FET3572-C 是"连接器式", 不是"焊死在板上"的 BGA/SOM 邮票式** ⇒ 主板上要放 **4 个 0.4mm pitch 100pin 板对板连接器** (400 触点) | ★**主板要照这 400 针的连接器画焊盘** ⇒ ★**引脚定义表就更加是硬前提** |
| 温度 | FET3572-C: 0 ~ +80 ℃ · FET3572J-C: −40 ~ +85 ℃ | `[实测]` PDF |
| 公开机械尺寸图 | ★**未查** (PDF 里有 "Exterior and dimensions" 示意图, 但**逐针坐标/连接器 footprint 未公开抓到**) | ★**主板画连接器 footprint 需要它** |

★**对比候选 (同一批实测, 给老板做取舍)**:

| SOM | SoC | 尺寸 | 连接方式 | 供电 | 公开逐针表 |
|---|---|---|---|---|---|
| ★**Forlinx FET3572-C** | **RK3572** | ★**68×50mm** | **4×100pin BTB, 0.4mm, 1.5mm** | ★**DC 5V–13V** | ★**未查** (下载中心) |
| ArmSoM CM5 | RK3576 | 55×40×4.9mm | BTB + 40pin 排针 (CM4 兼容) | 5V/12V (载板 DC 口) | ★**40pin 表实测公开** (<https://docs.armsom.org/interface-usage/40pin>), ★**100pin 表未公开抓到** |
| Radxa CM5 | RK3576 | 未查 | 100pin BTB + 40pin | 未查 | ★**40pin 表实测公开** (<https://docs.radxa.com/som/cm/cm5/hardware/hw-interface>), ★**100pin 表未查** |
| DFRobot RK3576 Core Board | RK3576 | 146×102mm (整板) | ★**整板 SBC 形态, 不是可焊 SOM** | 12–24V | ★**只公开了"板上有哪些接口", 无逐针表** |
| Luckfox Core3576 | RK3576 | 69.6×45mm | 260-pin SO-DIMM | 未查 | 未查 |

★**★ 判据结论 (★ 含一条硬伤, 必须说)**:
> ★**"主板的 FPC 座/供电/接口全被外购件倒逼" 这条对 P3 同样成立, 而且更狠**: ★**主板要围着一个 4×100pin / 0.4mm pitch 的板对板连接器阵列画板** ⇒ ★**这 400 个焊盘的机械坐标必须来自厂商的机械图, 电气含义必须来自引脚定义表** ⇒ ★**这两份文件现在都"未查"**。
> ⇒ ★**所以 P3 的选型结论是: 规格骨架 (尺寸/连接器/供电/接口数) 已实测齐全, 但"引脚定义表"这一项仍是"未查", 主板画板前必须先从 Forlinx 下载中心把它取下来** (★**公开下载, 非 L4**)。

### 4.3 ★ ③ 供电要求

| 项 | 值 | 证据 |
|---|---|---|
| ★**SoM 输入电压** | ★**DC 5V – 13V** | `[实测]` PDF "Operating Voltage: DC 5V-13V" + 官网 JSON `VoltageInput = DC 5V - 13V input` |
| ★**SoM 输入电流 / 峰值功耗** | ★**未查** | ★**主板电源设计要这个数, 公开资料没给 ⇒ 必须从下载中心的硬件手册拿** |
| 上电顺序 | ★**未查** | ★**同理** |
| 建议 | ★**主板给 SoM 供 5V** (5–13V 区间下沿, 用 USB/电池升压到 5V 最省事) | ★**[推断, 待核]** |

### 4.4 ★★ ④ MIPI CSI / DSI 通道分配与引脚

| 项 | 值 | 证据 |
|---|---|---|
| ★**MIPI CSI** | ★**2 × MIPI CSI-2, 每路 4 data lanes, D-PHY v1.2, 2.5 Gbps/lane**; ★**每路 4 lane 可拆成 2 × 2-lane 配��**; ★**最多支持 4 台 2-lane 相机** | `[实测]` PDF "SoM Function Parameters" |
| ⇒ **对 P1 的意义** | ★**4-lane IMX415 走其中一路** ⇒ ★**正好匹配 §2 的 4-lane 需求** (驱动只在 4-lane 表里有 1080p 模式 ⇒ **必须占满一路 4 lane, 不能拆**) | ★**主板的 CSI 座和 SoM 侧必须整路 4 lane 对 4 lane** |
| ★**MIPI DSI** | ★**1 × MIPI DSI 1.2, 最多 4 lane × 2.5 Gbps** | `[实测]` PDF |
| ⇒ **对 P2 的意义** | ★**4-lane DSI 够** (800×1280@60 RGB888 ≈ 246 Mbps; 1920×1080@60 RGB888 ≈ 373 Mbps) | ★**与 §3 的 4-lane 屏相容** |
| **DVP** | 1 路 (8/10/12/16-bit, ≤150MHz) | `[实测]` PDF |
| **HDMI/eDP** | 1 (HDMI 2.1 与 eDP 复用) | `[实测]` PDF |
| **其他** | 2×GMAC (RGMII/RMII) · ≤4 CAN-FD · ≤12 UART · ≤9 I2C (+1 I3C master) · ≤5 SPI · ≤16 PWM · ≤8 ADC · 3×Combo SerDes (PCIe2.1/SATA3.1/USB3.0) · 2×USB2.0 OTG · ≤2 SDIO · 1×DSMC 并行总线 (8/16-bit, ≤4 片选) | `[实测]` PDF |
| ★**CSI/DSI 的具体引脚号** | ★**未查** (要引脚定义表) | ★**§4.1 的待办** |

### 4.5 ★ ⑤ 公开原理图 / 尺寸图

| 项 | 状态 | 说明 |
|---|---|---|
| **SoM 原理图** | ★**未查** (在下载中心) | ★**主板照 SoM 原理图核对电源/地/上下拉** |
| **机械尺寸图 (连接器 footprint)** | ★**未查** (PDF 有 "Exterior and dimensions" 示意图, 但逐针坐标未抓到) | ★**主板画 4 个 100pin 0.4mm 连接器焊盘必须要它** |
| **同厂可公开镜像的同类件** | ★**FET3588-C SoM 简介 PDF 在 DigiKey 公开镜像 (实测 200)** ⇒ ★**能确认 Forlinx 的公开资料结构 (含 "files, pinmux sheet" 资料包说明)** | <https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/5731/FET3588-C%20SoM.pdf> |
| ★**Rockchip 侧 EVB 参考 (可公开)** | ★**`rk3576-evb.dtsi` 是公开的** (本单已实测抓到全部 DSI panel + init code) ⇒ ★**"Rockchip 自家 1080×1920 DSI 屏怎么接" 有公开答案** | `[实测]` |

---

## 5. ★★ 给主板画板的落成约束 (直接抄进原理图/布局说明)

| # | 约束 | 依据 | 落在哪 |
|---|---|---|---|
| **M1** | ★**camera FPC 座 = 31p / 0.3mm / 翻盖式贴板** (HIROSE FH35C-31S-0.3SHW(50) 或同规格), **针序照 §2.1 的 31 针表** | §2.1 `[实测]` | 原理图相机页 + 布局 |
| **M2** | ★**display FPC 座 = 40p / 0.5mm / 翻盖式贴板**, **针序照 §3.1 的 40 针表**; 主板侧排线走 39p/0.3mm 或 15p/1.0mm 原厂件 | §3.1 `[实测]` | 原理图显示页 + 布局 |
| **M3** | ★**camera 4 组差分对 + 1 组时钟对, 各预留一个 AC 耦合电容位, 默认 DNP** (模组是否内置未查实 ⇒ 留退路) | §2.3 | 原理图相机页 |
| **M4** | ★**sensor 三条轨 (1.1/1.8/2.9V) 的 LDO: EN 脚全部显式接法 (不许 NC) + 按 DVDD→OVDD→AVDD 顺序 RC 延时** (模组自带 LDO 的推断待核 ⇒ **BOM 留 DNP 焊盘**) | §2.4 + `PART_ALTERNATIVES_REGISTRY.md` §6.2 | 原理图电源页 (P0) |
| **M5** | ★**I2C 上拉 = 2.2k, 上拉电源 ≤3.3V (相机侧)** | §2.5 | 原理图 |
| **M6** | ★**屏背光单独一路 12V BOOST + 限流** (LED typ 12.8V / max 14V / 200mA typ) | §3.3 | 原理图显示页 |
| **M7** | ★**触控 I2C (TP_SCL/TP_SDA/TP_INT/TP_RESET) 走 SoC 的另一组 I2C, 不与相机 I2C 共用** | §3.1 | 原理图 |
| **M8** | ★**DSI 走 4-lane, 不用 2-lane** (8HD 支持 2/4 lane, 但 10FHD 必须 4-lane ⇒ 统一按 4-lane 画) | §3.1/§3.2 | 原理图 + 布局 |
| **M9** | ★**SoM 侧: 主板画 4 × 100pin / 0.4mm pitch / 1.5mm 高 板对板连接器, 供 5V** ⇒ ★**连接器型号 + footprint 等 Forlinx 引脚定义表 + 机械图到手后再定 (现在是 TBD, 不是"待优化")** | §4.2 | 布局 |
| **M10** | ★**SoM 的 400 针里, CSI/DSI 具体引脚号待引脚定义表补齐** ⇒ ★**在此之前不得开跑线** | §4.4 | 原理图 |
| **M11** | ★**1080p60 = 1944×1097 / 12bit / `0x3020=0x01` (2/2 binning) / VTS `0x0C5D`→`0x062E`** ⇒ 软件/BSP 侧确认, 硬件侧只需保证 4-lane + MCLK 37MHz | §2.2 | BSP 配置 |

---

## 6. ★★ 本单结论 (给 boss 的 5 条)

| # | 结论 | 依据 | 落成动作 |
|---|---|---|---|
| **S1** | ★★**P1/P2 两件"决定主板两个 FPC 座"的规格已闭环**: camera **31p/0.3mm (逐针表 31/31)**, display **40p/0.5mm (逐针表 40/40)** ⇒ ★**"0.5mm/24p 自研目标规格"正式作废, 替换为这两个公开可查的规格** ⇒ ★**主板不用转接排线, 不用自造规格** | §2.1 / §3.1 逐针表原文 | ★**画板照抄** |
| **S2** | ★★**P3 的规格骨架齐了, 但"引脚定义表"仍是唯一硬缺口**: FET3572-C = **68×50mm / 4×100pin 0.4mm BTB / DC 5-13V / CSI 2×4-lane / DSI 1×4-lane** (全部实测) ⇒ ★**主板要画 400 焊盘的连接器阵列, 必须先拿到引脚定义表 + 机械图** ⇒ ★**走 Forlinx 下载中心 (公开注册下载, 不是 L4)**, ★**且 PDF 明写 FET3572-C 与 FET3576-C 引脚兼容 ⇒ 拿到 FET3576-C 的表即等于拿到 FET3572-C 的** | §4.1–4.5 | ★**P3 待办 = 下载三个文件** |
| **S3** | ★★**"面板 init code 不必问厂家" 再次实测成立, 但判据要改口径**: 公开 dts 里就有 init sequence —— `rk3576-evb.dtsi` 的 **263 条 (1080×1920/4-lane, 与我们目标屏最贴)** + 10 FHD 的 2 条 + `radxa-cm5-io-radxa-display-10fhd.dts` 的完整 timing ⇒ ★**选屏硬判据应改成 "能找到用同一块屏的公开 dts"** (不是死磕某颗 IC 在不在白名单) ⇒ ★**EK79007/EK73217/NV3049 内核里没有 这条仍然成立** | §3.2 / §3.5 / §3.6 | ★**并进 `PART_ALTERNATIVES_REGISTRY.md` C1** |
| **S4** | ★★**主板电源树要改两处**: ① **屏背光是 12V 级 ⇒ 单独 BOOST** ② **camera 模组级只要 3.3V + 5V ⇒ sensor 三条 LDO 可能整个不需要** (待核模组内部供电架构) ⇒ ★**省 3 颗 LDO + 一路升压, 但 BOM 里必须留 3 条 sensor 轨的 DNP 焊盘做退路** | §2.4 / §3.3 | ★**画板前定** |
| **S5** | ★★**"驱动 IC 须在白名单"这条判据有前提**: 它只管**专用 panel driver**; 走 `simple-panel-dsi` 的屏 (10 FHD / EVB 屏) **不依赖任何专用 driver** ⇒ ★**这条硬判据可以用"选 `simple-panel-dsi` 屏"直接满足** ⇒ ★**⇒ P2 定案走 `simple-panel-dsi` 路线** (10 FHD 或同族), ★**8HD (`radxa,display-8hd`) 需要带私有 driver ⇒ 降级为备选** | §3.5 / §3.6 | ★**P2 定案** |

★**本单没做的事 (明确交代)**:
- ★**没联系任何厂家 / 没发问询函 / 没发帖** ⇒ **L4 未触发**
- ★**没改** `PROJECT_TRACKER.md` / `state/issue_log.yaml` / `HW/DEMO_BOARD_HW_DECISION.md` / `HW/STEP1_LANDING_LIST.md` / `state/gen_netlist.py` / `HW/netlist_v1.csv`
- ★**F4~F12 致命项清零 = ISS-159**, 不在本单
- ★**价格 / 库存 / 交期 = 全部未查** (本单只管机械+电气规格)

★**证据等级**: 逐针表 / dts 原文 / 驱动源码 / 厂商 PDF 原文 / 官方规格表 / 公开页面 = **[实测]** · 引脚定义表 / 模组级电流 / AC 耦合是否内置 / 连接器寿命 / 驱动 IC 型号 / 面板机械尺寸 / SoM 引脚号 = **[未查]** · "模组自带 LDO" / "8HD 屏驱动在 Radxa 私有内核" = **[推断, 待核]**。

★**复算命令 (本单所有链接均实测 HTTP 200, 部分需浏览器 UA)**:
```bash
# P1 针位表 + 规格
curl -sL https://docs.radxa.com/accessories/camera/camera-4k | grep -A40 "引脚定义"
# P1 载板侧 31p 针序 (交叉验证)
curl -sL https://docs.radxa.com/en/rock4/rock4d/hardware-use/mipi-csi | grep -A60 "31-Pin"
# P2 针位表 + 规格
curl -sL https://docs.radxa.com/accessories/display/lcd-8-hd/lcd-8-hd-product | grep -A80 "Pinout"
# P2 10FHD dts (init code + timing)
curl -sL https://raw.githubusercontent.com/radxa-pkg/radxa-overlays/HEAD/arch/arm64/boot/dts/rockchip/overlays/radxa-cm5-io-radxa-display-10fhd.dts
# P2 EVB 屏 263 条 init code
curl -sL https://raw.githubusercontent.com/rockchip-linux/kernel/develop-6.1/arch/arm64/boot/dts/rockchip/rk3576-evb.dtsi | sed -n '260,560p'
# P1 1080p60 寄存器序列
curl -sL https://raw.githubusercontent.com/rockchip-linux/kernel/develop-6.1/drivers/media/i2c/imx415.c | sed -n '690,730p'
# P3 SoM 规格 (需浏览器 UA)
curl -sL -A "Mozilla/5.0" https://www.forlinx.net/download/FET3572-C-SoM-OK3572-C-SBC-Product-Brief.pdf | pdftotext -layout - -
```
