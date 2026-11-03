# HW/STEP1_LANDING_LIST.md —— demo 落地清单（**板子全部自己画**版）

| 项 | 内容 |
|---|---|
| 作者 | 项目总工 (main) · 2026-11-02 22:3x |
| ★**前提变更** | ★**老板 2026-11-02 22:30 拍板: 「不行, 板子必须全部自己画」** ⇒ ★**推翻 20:4x 的"Step1 用公开 SBC 当载体"建议** ⇒ ★**demo 用自研主板**, 不再用现成 SBC 承载 |
| 形态 | ★**一块自研主板** (RK3572 核心板 SOM + 两个 FPC 座 + 电源树 + 调试) + ★**外购 sensor 模组** + ★**外购屏幕模组** + 两根 **FPC 软排** ⇒ 与老板 19:25 定的形态一致 |
| 依据 | `HW/DEMO_BOARD_HW_DECISION.md`（硬件方案定案）· `HW/PART_ALTERNATIVES_REGISTRY.md`（33 候选/53 链接）· `SW/DEMO_OD_PIPELINE_SPEC.md` · `SW/RKNN_BUILD_ENV_RECOVERY.md` · `HW/IMX415_DEMO_SENSOR_FACTS.md` / `HW/AR0234CS_OPEN_SOURCE_FACTS.md` |

---

## 0. ★★★ 自研板带来的最大连带：**选型顺序倒置**

既然**模组是外购、板子是我们画**，⇒ ★**主板的 FPC 座规格不是我们定的，是模组定的**：

> ★★ **正确顺序：先选模组 → 拿到它的 FPC 针数/间距/针位表 → 主板照抄画座**

⇒ ★**推翻了 19:4x 的"自研目标规格 0.5mm/24p"**（那个规格在公开现货里根本不存在 ⇒ 画出来也没模组能插）⇒ **主板 FPC 座 = 被模组倒逼出来的**。
⇒ ★**主板唯一的"自选"部分** = **RK3572 核心板 (SOM) 的焊接方式 + 电源树 + 调试口 + 板尺寸/层数**。

---

## 1. ★ 选型顺序（严格按这个顺序做，每步都有交付物）

| 步 | 选什么 | 交付物 | 为什么它卡着下一步 | 单号 |
|---|---|---|---|---|
| **P1** | ★**camera 模组**（公开在售 IMX415） | ★**FPC 针数/间距/针位表 + 供电清单 + 1080p60 寄存器序列** | ⇒ **主板 camera FPC 座按它画** | ★**ISS-158** |
| **P2** | ★**屏幕模组**（公开在售 8HD/10FHD DSI 一体屏） | ★**FPC 针位表 + init code / DSI timing / DDC 地址 + 驱动 IC 型号** | ⇒ **主板 display FPC 座按它画**; ★**驱动 IC 必须在内核白名单里**（ST7701/ST7703/ILI9881C/NV3052C…；★**EK79007/EK73217/NV3049 内核没有**） | ★**ISS-158** |
| **P3** | ★**RK3572 核心板 (SOM)** | ★**引脚定义表 + 尺寸 + 焊接/连接方式 + 供电要求 + CSI/DSI 通道分配 + 公开原理图** | ⇒ **主板围绕它画**; ★**它也是绕开 TBD-01（SoC 球位图未公开）的关键** | ★**ISS-158** |
| **P4** | ★**主板本体** | ★**网表（已改到位）+ 板级约束 + 选型清单** | ⇒ 可下单打样 | **ISS-149/150**（已 fixed）· ★**ISS-158** 收口 |

★**P1~P3 全部是"公开在售 + 公开资料可查"** ⇒ ★**不触发 L4（不咨询厂家）**；★**若某件公开渠道拿不到 ⇒ 换第二家（L2）**，不回头找厂家。

---

## 2. ★ 主板规格草案（自研，四问已定案）

| 项 | 决定 | 依据 |
|---|---|---|
| **主控** | ★**RK3572 核心板 (SOM) 焊在主板上**（★**不焊裸芯片**） | ★**SoC 球位图官方未到 (TBD-01)** ⇒ 用 SOM 则主板完全不碰球号；★**SOM 引脚定义公开可查** ⇒ 不触发 L4 |
| **camera 连接** | ★**板内 FPC 座（针数/间距照 P1 模组）**，2-lane CSI + MCLK + SCCB + RESET + 三轨电源 + GND | 1080p60 RAW10 = 1.244Gbps ⇒ 2-lane 够；★**I2C 上拉电压 ≤ sensor VI abs max**（IMX415 = 3.3V 合法；★换 AR0234CS 须 ≤3.1V ⇒ 改 2.8V） |
| **display 连接** | ★**板内 FPC 座（针数/间距照 P2 模组）**，4-lane DSI + DDC + 3.3V + EN + GND | 1920×1080@60 RGB888 ≈ 373Mbps ⇒ 4-lane 绰绰有余，**不需 DSC** |
| **电源** | ★USB-C 5V 输入 → 3.3V (SOM) + 三路 sensor 轨 (1.2/1.8/2.8V, 照 IMX415) + 3.3V (屏模组) + **(DNP) 充电位** | ★**demo 不装电池、不上充电链**（充电链属整机阶段的镜框充电板） |
| **EN** | ★**9 路电源 IC 的 EN 已全部补进网表**（除 AVDD 外直连 RAIL_SYS；AVDD 走 RC 延时 ⇒ AVDD 最后上电） | ★★**P0：TPS7A20 的 EN 内部 500k 下拉 ⇒ 悬空=关断 ⇒ 投板后整板不上电** ⇒ 已修 |
| **尺寸/层数** | ★**先不锁**（老板 19:25 不考虑结构）⇒ ★**但层数必须先定**：MIPI 差分对 ⇒ ★**≥6 层**（RK357x 载板公开设计通则），并按 100Ω 差分阻抗设计 | ★层数定不下来 ⇒ 阻抗/逃线无从谈起 ⇒ ★**这是 P4 之前必须定的第一件事** |
| **调试** | USB-UART + JTAG + BOOT/RESET 按键 + 状态 LED + 电源/各轨测试点 | 常规 |

---

## 3. ★★ 画板前必须清零的"致命项"清单（★照 EN 的教训来：这类项一旦漏到投板后，代价是 2~4 周）

★**本版口径（2026-11-03 09:4x · ISS-159 闭卷）**：状态列 = **已清零 / 待清 / 不适用 / 未查**；★**每项依据在 §3.1 依据区**（文件:行号 或 URL，可复核）；★**查不到就写「未查」，不猜**；★**本单撞出的冲突/依赖在 §3.2**（交项目总工裁决 ⇒ **本单只读、不自己改**）。

| # | 致命项 | 怎么查（**全部公开渠道**） | 状态 |
|---|---|---|---|
| **F1** | ★**电源 IC 的 EN** | TI datasheet 实读 | ✅ **已清零**（9 路使能全有网；AVDD 走 RC 延时） |
| **F2** | ★**sensor 三条轨电压/电流** | 公开 datasheet | ✅ **已清零**（★结论已被 **F14** 推翻 ⇒ 三轨全 DNP） |
| **F3** | ★**I2C 上拉电压与阻值** | sensor 的 VI abs max + IOL | ⚠️ **已清零（口径要改）**：阻值 **2.2k 不变**；★**上拉轨 3.3V → 1.8V** |
| **F4** | ★**主板 FPC 座针数/间距** | ★**照 P1/P2 模组的针位表** | 🔄 **待清**：camera ✔ / ★**display ✖ 两个互斥选项** |
| **F5** | ★**RK3572 SOM 的引脚定义/尺寸/焊接方式** | 模组厂公开规格 + 原理图 | 🔄 **待清**（★依赖 ISS-165/167/168/169 在飞） |
| **F6** | ★**层数与阻抗** | ★**Forlinx OK3572-C 手册 §3.5.16 / §3.5.17.1** | ✅ **已清零**（6 层 + 100Ω/50Ω + skew 判据） |
| **F7** | ★**MCLK 走线/端接/AC 耦合位置** | 公开 sensor 模组参考设计 + Rockchip camera module 通则 | 🔄 **待清**（★位已留，**值未锁**） |
| **F8** | ★**面板 init code / timing 适配** | ★**抄 `rk3576-evb.dtsi` 现成 panel-init-sequence** | ✅ **已清零**（模板已落：**261 条 init + 2 条 exit**） |
| **F9** | ★**ISP tuning（1080p 档缺 mesh）** | 公开 IQ + 自制 mesh | 🔄 **待清**（1~2 人日 + 暗室；★卡出图不卡板） |
| **F10** | ★**ESD/TVS/过压** | ★**Forlinx 手册 §3.5 各接口章 + §2.4.5** | 🔄 **待清**（判据已定；★**display 口无 ESD 位**） |
| **F11** | ★**FPC 弯折寿命/插拔次数/补强** | 连接器厂公开规格 | ❓ **未查**（★公开渠道无 durability 字段） |
| **F12** | ★**散热** | ★**demo 不考虑功耗 ⇒ 先不管**（整机阶段再说） | ⏸ **不适用**（老板明确暂缓） |
| **F13** | ★**底板主电源使能（CARRIER_BOARD_EN pin87）** | ★**Forlinx OK3572-C 手册 §4 Power-on Sequence** | 🔴 **待清 · 阻塞投板**（★网表只落了一半） |
| **F14** | ★**camera 模组级供电（主板要不要供那三条轨）** | ★**先看模组接口表，再看芯片 datasheet** | ✅ **已清零**（三轨 + 3 颗 TPS7A20 + 6 个去耦位全 DNP） |
| ★**F15** | ★**〔本单新撞出〕display 背光/触控 4 脚并网 + 主板无 12V BOOST** | 模组原厂针位表 vs 主板网表逐脚比对 | 🔴 **待清 · 阻塞投板**（★**建议立项**） |

### 3.1 依据区（★逐条可核：文件:行号 或 URL）

★**行号口径**：`HW/netlist_v1.csv` 与 `HW/PCB/*` 正被 **ISS-165 / ISS-167** 在飞改动 ⇒ 下列网表行号 = **2026-11-03 09:35 版快照**（`HW/netlist_v1.csv` mtime 09:35:35；`HW/PCB/STACKUP.md` / `LAYOUT_RULES.md` mtime 09:36:52）⇒ ★**引用前按位号/网名复核**。
★**公开手册快照**：Forlinx **OK3572-C User Hardware Manual V1.0** = <https://forlinxembedded.github.io/rockchip/ok3572-c/OK3572-C_User_Hardware_Manual.html>（本地快照 `state/_os_snapshots/fx3572_manual.html`；下方 §3.1 的"剥标签行"= 该 HTML 去标签后的行号）。

**F1（EN）— 已清零**
- `HW/netlist_v1.csv:53`（U_PWR_SW 的 ON ← J_SOM_P3 pin88，10k 下拉默认关 `:51`）· `:65`（U_DCDC_VCORE EN）· `:69`（U_DCDC_VIO EN）· `:96,104,112,120,128,136`（6 颗 TPS7A20 的 EN）⇒ ★**9 路使能全部有网**。
- `U_LDO_S28`（SENSOR_AVDD）**没有 EN 行 = 正确**（该轨已因 **F14** DNP）。

**F2（三条轨参数）— 已清零，但结论被 F14 推翻**
- 原结论 1.2V/1.8V/2.8V + 250/3/156mA 来自 IMX415 芯片级 datasheet（`HW/IMX415_DEMO_SENSOR_FACTS.md`）；★**这是芯片级参数，不是模组级接口** ⇒ 见 **F14**，三条轨最终 **DNP**（`HW/netlist_v1.csv:87,89,94,97,102,105` 三颗 TPS7A20 全 DNP）。

**F3（I2C 上拉）— 已清零，口径要改**
- ★**实际接法**：`HW/netlist_v1.csv:152,153` = `R_PU_I2CA_SCL/SDA` = **2.2k ±1% 拉到 `RAIL_VDD_1V8_IO`（1.8V 域）**。
- ★**为什么改 1.8V**：camera 模组 FPC 上就标 **I2C5** ⇒ RK3572 的 I2C5 是 **1.8V 域** ⇒ `HW/PCB/FET3572C_PIN_TABLE.csv:132,134`（P2_31 `I2C5_SCL_M3` / P2_33 `I2C5_SDA_M3`，电平列 = **1.8V**）+ `HW/PCB/SOM_PIN_ASSIGNMENT.md:35,80`。
- ★**遗留**：网表 `:150,151` note 仍写"上拉 4.7k 到 3.3V"、`:154,155` note 写"上拉 2.2k 到 3.3V" ⇒ ★**三个值打架**（实际 2.2k/1.8V）⇒ 交项目总工改注释（见 §3.2-C4）。

**F4（主板 FPC 座）— 待清（camera ✔ / display ✖）**
- ★**camera 已清零**：Radxa Camera 4K = **31p / 0.3mm**，主板侧座 **HIROSE FH35C-31S-0.3SHW(50)**（翻盖式 / 上下双面触点 / 兼容 0.2mm 厚 FPC / 横向插拔）⇒ `HW/STEP1_PARTS_SPEC.md:54,55,56`（Radxa ROCK4D 公开接口页原文）+ 逐针表 `HW/PCB/FPC_PIN_TABLES.md:3-21`（31/31）；网表声明行 `HW/netlist_v1.csv:287`。
- ★**display 有两个互斥选项（必须拍板）**：屏侧 **40p/0.5mm**，但★**原厂排线的另一头（主板侧）是 39p/0.3mm（或 15p/1.0mm）** ⇒ `HW/STEP1_PARTS_SPEC.md:198,199`（原文 "39-pin 0.3mm pitch (Motherboard side) to 40-pin 0.5mm pitch (Display side)"）。
  - 选项 A：**39p/0.3mm**（走原厂排线）⇒ ★**主板侧 39 针针位表我们没有（未查）**。
  - 选项 B：**40p/0.5mm 直插**（现网表走的就是这条，声明行 `HW/netlist_v1.csv:218`）⇒ ★**屏侧座型号仍是"一类"未定**（`HW/STEP1_PARTS_SPEC.md:202` 标**未查**）。
  - ★**同一份文档自相矛盾**：`:200` 说"主板该画 39p/0.3mm"，而里程碑 M2（`:397`）说"display FPC 座 = 40p/0.5mm" ⇒ ★**现网表按 B 画 ⇒ 若最后选 A，整张 40 针表作废、座要换** ⇒ **投板前必须定**。

**F5（SOM 引脚/尺寸/焊接）— 待清（依赖在飞改动）**
- ★**数据已落地**（本单**只引用，一个字没改**）：`HW/PCB/FET3572C_PIN_TABLE.csv`（399 行，由 OK3572-C 手册 §2.6.2/§2.7 重建）+ `HW/PCB/SOM_PIN_ASSIGNMENT.md`（46 个信号）+ `HW/PCB/som_pin_assign.json` + `HW/PCB/som_btb_params.json`。
- ★**抽样核过**：`FET3572C_PIN_TABLE.csv:29`（P1_28 `SARADC_VIN0_BOOT` 1.8V）· `:132,134`（I2C5 1.8V 域）· `:145`（P2_45 `CAM_CLK0_OUT_M0` 1.8V）· `:200`（P2_100 `RESET_L`）· `:287`（P3_87 `CARRIER_BOARD_EN`）· `:288`（P3_88 `PWRON_L`）· `:291-300`（P3_91/93/95/97/98/99/100 = `VCC_DCIN`）。
- ★**依赖在飞**：**ISS-165**（A2 段 · fixing）正在改这些文件 + 生成器 · **ISS-167**（焊盘编号假绿 · fixing）· **ISS-168**（RK3572≠RK3576 电气功能，已 fixed ⇒ 现表已换口径）· **ISS-169**（★4×100pin BTB 座机械位置/pin1 方向**未与原厂 DXF 核对** ⇒ 板子**不能下单**）⇒ ★**本项不单独下结论，跟在飞改动走**。

**F6（层数与阻抗）— 已清零**
- ★**层数 = 6 层**（项目总工定案，本单**不自己拍**）：`HW/PCB/STACKUP.md:8,9`（L1 信号 / L2 GND 完整 / L3 信号+局部电源 / L4 电源平面 / L5 信号 / L6 GND 完整）+ `HW/PCB_DRAWING_PLAN.md:42,44-51`。
- ★**阻抗判据的公开依据（Forlinx OK3572-C 手册）**：
  - §3.5.16 Video Input Interface（剥标签行 **4987-4992**）："Routing impedance required differential **100ohm±10%**"；"single end **50ohm ± 10%**"；"**Inter-Pair Skew maximum ＜3mil**"；"**Equivalent length between clock and data < 6 mil**"；"Differential pair space better ＞4 times MIPI line space, and at least **3 times MIPI line width**"。
  - §3.5.17.1 MIPI_DSI（剥标签行 **5010-5020**）：同样 "differential **100ohm ± 10%**" / skew ＜3mil / clock-data 等长 <6mil。
  - ★**互证**：`HW/PCB/LAYOUT_RULES.md:5`（MIPI 100Ω + 对间距 ≥3× 线宽 + L2/L6 完整 GND + 长度差 **≤0.13mm**）⇒ 0.13mm = **5.12mil < 6mil** ✔ 合规。
- ★**必须纠正任务书里的一句**：任务书写"**≥6 层**，依据＝公开 RK357x 载板设计通则" ⇒ ★**这句没有公开依据**：唯一公开可查的 RK3572 载板（Forlinx OK3572-C）本身是 **4 层**（剥标签行 **4494**："Plate making process: 1.6mm thickness, **4-layer PCB**"；SoM 板是 10 层，行 **360**）⇒ ★**6 层是本板的设计决定（向上留余量：同板要跑 1×CSI 4-lane + 1×DSI 4-lane + 电源 + USB + 调试），不是照抄公开值**；★**真正硬的公开依据是上面那几条阻抗/偏斜/间距判据**。
- ⇒ ★**层数已定 ⇒ 「层数不定 ⇒ 阻抗/逃线无从谈起 ⇒ 阻塞投板」这条阻塞已解除**。

**F7（MCLK 走线/端接/AC 耦合）— 待清（位已留，值未锁）**
- ★**MCLK 由 SoM 出，不用主板自己产**：`HW/PCB/SOM_PIN_ASSIGNMENT.md:21`（`CSI_MCLK` = `CAM_CLK0_OUT_M0`，P2_45，**1.8V**）+ `HW/PCB/FET3572C_PIN_TABLE.csv:145`；网表 `HW/netlist_v1.csv:267`（源端 → `R_SER_CSI_MCLK`，单端需包地）· `:268`（串阻位 **必装**，值 `[待原厂]`/TBD-03）· `:339`（`TP_MCLK` 测试点）。
- ★**AC 耦合位置**：10 个 100nF 耦合位全在网表（CK_P/N + D0~D3 P/N，`HW/netlist_v1.csv:247-266`），note 明确"**原厂是否内置 AC 耦合未回（TBD-03）；内置则本位改 DNP，未内置必须装**" ⇒ ★**位已留 ⇒ 内置与否只改 BOM、不改板 ⇒ 不属投板后致命**；★**主板侧若装 ⇒ 规则：紧贴 FPC 座 ≤5mm、不放 SOM 侧**（`HW/PCB/LAYOUT_RULES.md:14` 第 3 条硬规则）。
- ★**走线规则**：MCLK 与 CSI/DSI 时钟对分开走、间距 ≥3× 线宽、中间夹 GND（`HW/PCB/LAYOUT_RULES.md:12` 第 1 条 + `HW/PCB_DRAWING_PLAN.md:58`）；阻抗/偏斜判据同 **F6**。
- ★**还差两项**：①模组是否内置 AC 耦合（TBD-03）②MCLK 电平/速率 ⇒ 串阻值写不死；★**另：1.8V MCLK 是否被模组接受 = 未查**（模组规格未公开该脚的最大输入电压）。

**F8（面板 init code / timing）— 已清零（★有一个前提条件）**
- ★**公开开源来源**：Rockchip BSP kernel `develop-6.12` 的 `rk3576-evb.dtsi` 里 `dsi_panel: panel@0`（`compatible = "simple-panel-dsi"`、4-lane、`MIPI_DSI_FMT_RGB888`、`VIDEO|VIDEO_BURST|LPM|NO_EOT_PACKET`）⇒ 已落 `HW/PCB/panel_simple_dsi_template.dtsi`（`:17` compatible、`:25-29` flags/format/lanes、`:32-293` panel-init-sequence **261 条**、`:296-298` panel-exit-sequence **2 条**、`:300-317` display-timings 132MHz/1080×1920）。
- ★**前提条件**：这条路只对**内核白名单驱动 IC + simple-panel-dsi** 的屏成立 ⇒ ★**demo 屏必须选 10FHD 路线**；若选 Radxa Display 8 HD（`compatible = "radxa,display-8hd"`，驱动在 Radxa 私有内核）⇒ ★**8HD 的 init code 未公开 ⇒ 本项退回待清**（`HW/STEP1_PARTS_SPEC.md:196-202,238-240`）。
- ★**口径小订正**：任务书/issue_log 说"263 条 panel-init-sequence" ⇒ 实测 = **261 条 init + 2 条 exit = 263 条总量**（`HW/STEP1_PARTS_SPEC.md:239` 写"263 条寄存器写 + panel-exit-sequence 2 条"）⇒ **文件本身没问题，是口径把 init+exit 合算了**。

**F9（ISP tuning 1080p 档缺 mesh）— 待清（卡出图，不卡板）**
- ★**依据**：`HW/IMX415_DEMO_SENSOR_FACTS.md:20`（现成 IQ 的 `sensor_calib.resolution` 明写 **3840×2160**，且 rkaiq 仓库里 IMX415 的 mesh 文件名锁死 3840×2160 ⇒ **1080p 档缺 mesh**；工作量 **1~2 人日（需暗室/灰卡）**）· `:155`（`FEC_mesh_3840_2160_imx415_3.6mm/` 10 个 .bin）· `:173,174`（要重调的两处：补 1920×1080 mesh + AE 曝光表换算，VMAX 3165→1582）· `:234`（公开来源 URL：<https://github.com/TinkerBoard/rockchip-linux-external-camera_engine_rkaiq>，实拉 `git/trees/HEAD?recursive=1`）。
- ⇒ **不卡投板**（mesh 是标定物，不是板子），卡出图；退路见 §6。

**F10（ESD/TVS/过压）— 待清（★判据已定，但网表有缺口）**
- ★**公开判据（Forlinx OK3572-C 手册）**：
  - §3.5.15 SATA3.0 章（剥标签行 **6440**）："All signals of an eSATA connector must have ESD protection **placed close to the connector**. The ESD parasitic capacitance must **not exceed 0.4 pF**."
  - §3.5.15 USB2.0 章（行 **6426**）："**ESD protection is mandatory on all signals.** For USB 2.0 signals, ESD parasitic capacitance must **not exceed 3 pF**." + DP/DM 串 2.2Ω。
  - §3.5.17.2 HDMI_TX 章（行 **6639-6640**）：HDMI2.1 ≤**0.2pF**；其他信号建议 ≤**1pF**。
  - §2.4.5 ESD Features（行 **526-538**）：SoM 导出信号 **ESD HBM ±2000V / CDM ±250V**，且"all the signals exported from SoM are electrostatic sensitive signals, **the interfaces should be well protected from static electricity in the carrier board design**" ⇒ ★**我们的 camera/display FPC 口同样要**。
- ★**现状核对**：`HW/PCB/LAYOUT_RULES.md:7` 只写了"ESD 器件紧贴座"（USB 行），★**没有寄生电容上限，也没有 MIPI FPC 口的 ESD 行** ⇒ ★**本单不写 `HW/PCB/`（禁写区）⇒ 规则正文留在本表** ★**待落 `LAYOUT_RULES.md`，依赖 ISS-165/ISS-167 收工后由项目总工统一应用**。
- ★**网表缺口**：ESD 位只有 4 个 —— `D_ESD_TC`（Type-C VBUS 入口，`:4`）· `D_ESD_USB`（USB DP/DM，`:408,409`）· `D_ESD_CAM`（紧贴 CONN_CAM，`:413`）· `D_ESD_LIGHT`（光机 5V 口，`:142`，**DNP**）⇒ ★**display FPC 座（CONN_LIGHT）的 4-lane DSI 10 根差分线完全没有 ESD 位** ⇒ 违反 Forlinx"mandatory on all signals" ⇒ **投板后要改板加器件 ⇒ 阻塞投板**；★**且四颗 ESD 器件全部"ESD 阵列 [待选型]" ⇒ 寄生电容无法核**。

**F11（FPC 弯折寿命/插拔次数/补强）— 未查**
- ★**为什么查不到**：`HW/STEP1_PARTS_SPEC.md:179-187`（§2.7 标题即"**未查**"）—— ①**HIROSE FH35C 原厂页本轮抓到的字段里没有 cycles/durability 字段**（只有尺寸/间距/额定电压/电流）⇒ `:183`；②**模组厂商未公开 FPC 的弯折规格** ⇒ `:184`；③要当正式可靠性指标需要 **FH35C 原厂规格书 durability 章节 + 模组 FPC 规格书**，★**这两份在公开下载区可能存在，本单未取到 ⇒ 标未查**（`:186,187`）；★**补强片（stiffener）厚度规则同样未取到 ⇒ 未查**。
- ★**兜底（不是寿命数据，是规避）**：按"**不弯折**"设计 —— camera FPC 排线**不跨铰链**、直连、长度 ≤60mm（`HW/STEP1_PARTS_SPEC.md:185`，依据是项目既有硬约束"排线不跨铰链"）+ 板级自检项"FPC 插拔 20 次不虚接"（本文件 §5 V9 ④）。

**F12（散热）— 不适用**
- ★**依据**：老板明确"demo 不考虑功耗"⇒ 本文件 §2 尺寸/层数行 + 任务书 ISS-159 desc（"F12 散热 ⇒ ★demo 不考虑功耗 ⇒ 老板明确暂缓"）；`HW/DEMO_BOARD_HW_DECISION.md:50`（demo 阶段 SOM 散热面朝下贴导热垫/铜箔，用外壳导热即可，不做结构）⇒ ★**本轮不查散热；但机械上仍要留 SOM 散热面朝下的位置**。

**F13（CARRIER_BOARD_EN 底板使能）— 待清 · 阻塞投板（★建议升为独立 P0）**
- ★**公开依据（Forlinx OK3572-C 手册）**：
  - §4 Hardware Design Guide → "Power-on Sequence"（剥标签行 **5090-5093**）："When designing the carrier board, it is strongly recommended to reference the development board design by using the **CARRIER_BOARD_EN signal output from the core board as the enable for the carrier board's power-on sequence**. Strictly control the power-on timing; failure to do so may result in: · **Excessive inrush current during power-on.** · **Device failure to boot.** · **In the worst-case scenario, irreversible damage to the processor.**"
  - §3.5.1 Carrier Board Power（行 **4621**）："After the SoM starts up normally … it outputs a high level via the **CARRIER_BOARD_EN** pin to enable U3, thereby outputting VCC_5V to power certain peripherals …（3.3V, 1kΩ pull-up）"；★**同章 Note（行 4625）**："When designing independently, please **strictly adhere to the power-up sequencing**"。
  - §2.4.2 Power Parameter：SoM 供电 **5-13V**（⇒ demo 走 USB-C 5V 在范围内 ✔）。
  - 逐针：`HW/PCB/FET3572C_PIN_TABLE.csv:287`（P3_87 `CARRIER_BOARD_EN`，3.3V，1K pull-up，**不接 GPIO**）· `:291-300`（P3_91/93/95/97/98/99/100 = `VCC_DCIN`）。
- ★**落法（已定的部分）**：`HW/PCB/SOM_PIN_ASSIGNMENT.md:61`（固定脚表：`P3_87`）· `:84`（**F13 落法**：SoM 的 CARRIER_BOARD_EN → 主板负载开关 **U_EN_SW** 的 EN ⇒ 主板各路挂 **RAIL_BOARD_5V**；★**SoM 自己的 VCC_DCIN 直供 5V，不受门控**）+ `HW/PCB/som_pin_assign.json:398`（`"CARRIER_BOARD_EN": "P3_87"`）。
- ★**网表只落了一半（实测 `HW/netlist_v1.csv`，09:35 版）**：
  - ✅ 9 条 LDO/DC-DC 的 **VIN** 已改挂 `RAIL_BOARD_5V`（`:75,82,89,96,104,112,120,128,136`），6 条 **EN** 也挂 `RAIL_BOARD_5V`（`:96,104,112,120,128,136`），note 里写着"F13: 由 CARRIER_BOARD_EN 门控"。
  - ❌ **网表里没有 `U_EN_SW` 这个器件**（`grep -c U_EN_SW` = **0**）；❌ **`CARRIER_BOARD_EN` 没有作为网名出现过**（`grep -c "^P[0-9]*,CARRIER_BOARD_EN"` = **0**，9 次出现全在 note 正文里）；❌ **`RAIL_BOARD_5V` 没有任何驱动源** —— 全网 15 条命中**全是别的器件的 VIN/EN 输入脚** ⇒ ★**这条轨是悬空的**。
  - ⇒ ★**照现网表投板 = 底板与核心板同时上电 + 各路无源 ⇒ 与 F1 同级（板子起不来 / 伤处理器）**。
  - ★**现有门禁抓不到**：`state/check_netlist.py` 判据 8 只查"轨名在图上"、判据 11 只查"同网多驱动" ⇒ ★**"电源轨没有驱动源"这条判据不存在**（`state/check_netlist_pins.py` 2026-11-03 新增的 5 条判据也不含它）。
  - ⇒ ★**建议**：①立独立 P0 单；②给网表门禁补一条"每条 RAIL_* 必须有 ≥1 个输出驱动"。

**F14（camera 模组级供电）— 已清零**
- ★**依据**：Radxa Camera 4K 31 针表 **pin28/29 = VCC3.3V、pin30/31 = VCC5V** ⇒ `HW/PCB/FPC_PIN_TABLES.md:20,21` + `HW/STEP1_PARTS_SPEC.md:146`（"B 层: 模组级 (Radxa Camera 4K 整模组的供电)"）⇒ ★**模组内部自己稳压 ⇒ 主板不需要 sensor 芯片级三条轨**。
- ★**落地（三处一致）**：①`HW/netlist_v1.csv:87,89,94,97,102,105`（`U_LDO_S28`/`U_LDO_S18B`/`U_LDO_S12` 三颗 TPS7A20 全 **DNP**）+ `:90-93,98-101,106-109`（★**六个去耦位全 DNP**）②`HW/SCHEMATIC_V1_SPEC.json` 的 `power_rails` 三条 status = "❌ 不画 (DNP)" ✔ ③任务书/issue_log F14 条目。
- ★**教训（已入册）**：★**芯片级电源参数 ≠ 模组级接口 ⇒ 选型必须先看"模组接口表"再看芯片 datasheet**。

★**F15（本次新撞出）— 待清 · 阻塞投板（★建议立项）**
- ★**display 的背光/触控 4 脚被并在同一个网上**：`HW/netlist_v1.csv:243,244,245,246` = `NET_DSI_AUX` ← `CONN_LIGHT` **pin24 / pin26 / pin35 / pin40**。
- ★**逐脚比对公开针位表 ⇒ 这 4 个脚不是一类信号**：`HW/STEP1_PARTS_SPEC.md:208-227`（屏侧 40 针全表）—— pin24 = **TP_RESET**（主机→触控 复位，**输出**）· pin26 = **TP_INT**（触控→主机 中断，**输入**）· **pin35 = LED−（LED 阴极）** · **pin40 = LED+（LED 阳极）**。
- ★**后果**：①**LED+ 与 LED− 短接** ⇒ 屏背光 LED 直接短路；②另两个脚也被接地（`HW/netlist_v1.csv:230` pin36 → GND、`:231` pin39 → GND）—— ★**而 pin36 = LED−、pin39 = LED+** ⇒ **背光两端都接地**；③pin24/pin26 输出输入互短。
- ★**网表 note 的理由与公开规格矛盾**：note 写"demo 阶段不驱动（触控与背光由模组内部处理），无功能影响"，但 `HW/STEP1_PARTS_SPEC.md:234-238` 明确写"★**背光 LED 是 12V 级**（10FHD 官方实测：typ 12.8V / max 14V，电流 typ 200mA）⇒ ★**主板必须给屏背光单独做一路 12V 升压 (BOOST) + 限流**，★**不能用 3.3V 直接点背光** ⇒ ★**这条会改主板电源树**"。
- ★**主板电源树里确实没有背光电源**：`HW/SCHEMATIC_V1_SPEC.json` 的 13 条 `power_rails` 里**没有 12V/BOOST 轨**；`HW/netlist_v1.csv` 全文 grep `BOOST|backlight` **零命中**（唯一一条 boost 是充电板 OTG，见 `:456`）。
- ⇒ ★**投板后插屏 = 背光短路（烧屏/烧板）+ 屏不亮 ⇒ 2~4 周返工级** ⇒ ★**建议立项为 F15，并由项目总工裁决 F4 的 display 座选项（A/B）**。

### 3.2 ★ 本单撞出的冲突 / 依赖清单（★交项目总工裁决 ⇒ 本单**只读不改**）

| # | 冲突 / 依赖 | 涉及文件（本单**未改**） | 建议 |
|---|---|---|---|
| **C1** | ★**F13 只落了一半**：`RAIL_BOARD_5V` 无驱动源、`U_EN_SW` 不在网表、`CARRIER_BOARD_EN` 没当网名 | `HW/netlist_v1.csv`（ISS-165 在飞） | ★**立独立 P0**；网表补 `U_EN_SW` + `CARRIER_BOARD_EN`→EN 连接；★**门禁加"每条 RAIL_* 必须有输出驱动"** |
| **C2** | ★**F15：display 背光/触控 4 脚并网（LED+ 与 LED− 短接）+ 主板无 12V BOOST 背光轨** | `HW/netlist_v1.csv:230,231,243-246` | ★**立独立 P0**；补 12V BOOST + 限流；4 脚拆开（背光/触控各走各的，或明确 DNP 且**不能同网**） |
| **C3** | ★**F4：display 座两个互斥选项**（39p/0.3mm 走原厂排线 vs 40p/0.5mm 直插）；★同文档 `:200` 与 `:397` 自相矛盾；屏侧座型号 **未查** | `HW/STEP1_PARTS_SPEC.md` · `HW/PCB/FPC_PIN_TABLES.md`（屏侧 40 针表） | ★**项目总工拍板 A/B**；选 A ⇒ 需补 39 针主板侧针位表 + 整张 40 针表作废 |
| **C4** | ★**F3 口径**：网表 note 写"4.7k/3.3V"、`:154,155` 写"2.2k/3.3V"，实际是 **2.2k 拉到 1.8V**（I2C5 域） | `HW/netlist_v1.csv:150,151,154,155` | 改注释；★**F3 的"已清零"表述也要改成"上拉轨 1.8V"** |
| **C5** | ★**F13 没同步进规格文件**：`HW/SCHEMATIC_V1_SPEC.json` 里 grep 不到 `U_EN_SW` / `CARRIER_BOARD_EN` / `RAIL_BOARD_5V`（网表已改） | `HW/SCHEMATIC_V1_SPEC.json`（禁写区） | 规格补 F13；★**并改 `meta.en_policy`**（仍写"除 SENSOR_AVDD 外直连 RAIL_SYS / SENSOR_AVDD 走 RC 延时" ⇒ 与 F14/F13 都不符） |
| **C6** | ★**F10：display FPC 口没有 ESD 位**（Forlinx: mandatory on all signals）；4 颗 ESD 器件全是"[待选型]" ⇒ 寄生电容无法核 | `HW/netlist_v1.csv` · ★`HW/PCB/LAYOUT_RULES.md`（禁写区） | 补 `D_ESD_LIGHT`（紧贴 CONN_LIGHT，选 ≤0.4pF 的件）；★**ESD 硬规则（紧贴接口 + 寄生电容上限）待落 `LAYOUT_RULES.md`，依赖 ISS-165/ISS-167 收工后由项目总工统一应用** |
| **C7** | ★**F5 依赖在飞**：ISS-165（A2 段）· ISS-167（焊盘编号假绿）· ISS-169（BTB 座机械位置未核 ⇒ 板子不能下单） | `HW/PCB/FET3572C_PIN_TABLE.csv` · `SOM_PIN_ASSIGNMENT.md` · `som_pin_assign.json` · `som_btb_params.json` · `HW/PCB/STACKUP.md` · `HW/PCB/LAYOUT_RULES.md` | ★**本单只引用不修改**；跟 A2 段收工后再复核 F5 |
| **C8** | ★**F6 口径**："≥6 层"在公开渠道无依据（唯一公开 RK3572 载板是 **4 层**）⇒ 6 层是本板设计决定 | `HW/PCB/STACKUP.md` · `HW/PCB_DRAWING_PLAN.md` | 口径照 §3.1 F6 改写（**不改文件**，交项目总工） |

### 3.3 ★ 未查清单（★为什么查不到 ⇒ 不猜）

| 项 | 为什么查不到 | 兜底 |
|---|---|---|
| **F11** 连接器插拔次数 / FPC 弯折寿命 / 补强片规则 | HIROSE FH35C 原厂页本轮抓到的字段**无 cycles/durability**；模组厂**未公开** FPC 弯折规格；所需两份原厂规格书本轮**未取到**（`HW/STEP1_PARTS_SPEC.md:179-187`） | 按"**不弯折**"设计（排线不跨铰链、≤60mm）+ V9 插拔 20 次自检 |
| **F4** display 屏侧连接器型号 | 官方文档只给针位表，**未给座型号**（`HW/STEP1_PARTS_SPEC.md:202`） | 先按 40p/0.5mm 贴板翻盖式（FH12-40S-0.5SH 一类）预留，等 C3 拍板 |
| **F4** display **主板侧 39 针**针位表 | 官方只公开屏侧 40 针；主板侧 39p/0.3mm 那张表**未取到** | 选 A 前必须补 |
| **F7** 模组是否内置 AC 耦合（TBD-03）/ MCLK 串阻值 / MCLK 1.8V 是否被模组接受 | 模组侧公开资料未给（网表注"原厂是否内置 AC 耦合未回"） | 耦合位与串阻位**都留在板上** ⇒ 只改 BOM 不改板 |
| **F10** ESD 器件型号与寄生电容 | 四颗 ESD 全是"**[待选型]**"，无型号 ⇒ 寄生电容无从核 | 选型时按 Forlinx 上限（高速差分 ≤0.4pF / USB ≤3pF / 其他 ≤1pF）挑 |
| **F15** display 背光 12V BOOST 的具体器件/电感 | 本单**只做致命项清零**，不做背光电源设计 | 立单后由电源树那一轮做 |

⇒ ★**纪律（沿用 + 收紧）**：★**F1~F10/F13~F15 全部有明确"公开渠道"查法 ⇒ 不用问厂家** ⇒ ★**F11 查不到就写未查，不猜** ⇒ ★**F12 是老板明确说的不考虑 ⇒ 不适用** ⇒ ★**本单只改本文件 §3 + `state/fragments/hw.yaml`，其它文件一个字没动**。

---

## 4. ★ 软件步骤（板子回来之前就能做完的部分标 ✅）

| # | 步骤 | 状态 |
|---|---|---|
| **S1** | ★**target 兼容性验证**（`rk3572` 非合法 target ⇒ 用 `rk3576` 转） | 🔴 **卡板子** ⇒ ★**主板回来后第一件事**（ISS-155） |
| **S2** | 导出 ONNX（yolov5n@640） | ✅ 工具链已恢复，四步跑通 |
| **S3** | 转 RKNN（`target_platform='rk3576'`） | ✅ 跑通 |
| **S4** | 板端推理 + 精度（yolov5n F1 0.2927） | ✅ 跑通（★**待 ISS-157 修缓存后重测确认**） |
| **S5** | 相机出 RAW（IMX415 2/2 行 binning，**不是 crop**） | 🔴 卡板子 |
| **S6** | ISP（rkaiq；★**1080p 档需补 mesh**） | ⚠️ 卡 tuning（1~2 人日） |
| **S7** | OD 后处理 + 画框（**Y 平面不碰 U/V**；**画框在缩放之前**） | ✅ 规格已定 |
| **S8** | 显示（DRM/KMS + 4-lane DSI + panel 节点抄内核 dts） | 🔴 卡板子 + init code |
| **S9** | 9 个打点（**纯 NPU 与 SDK 总耗时分开报**） | ✅ 规格已定 |
| **S10** | 收敛判据（V1~V9） | 见 §5 |

---

## 5. ★ 验收判据（V1~V9，板级新增 V9）

| # | 判据 | 怎么测 |
|---|---|---|
| V1 | camera 模组被枚举 | `v4l2-ctl --list-devices` 出 imx415；`media-ctl -p` 链路通 |
| V2 | ★出 1920×1080@60 RAW | 抓 60 帧、行数 1080、时间戳 ≈16.67ms、fps ≥55 |
| V3 | ISP 出图 | 亮度分布正常（★Step1 允许先无 IQ） |
| V4 | OD 出框 | 框 ID ∈ [0,79]；离线/在线框 IoU > 0.95 |
| V5 | 框不错位 | IoU ≥ 0.5；往返误差 ≤2px；letterbox 黑边精确 |
| V6 | 屏上有画面 | 无色偏/撕裂/错位；单色屏用双色描边 |
| V7 | 9 个打点全有值 | 每段 min/avg/max/p50/p95 + 帧数 ≥300 |
| V8 | ★target 兼容性结论 | RK3572 的 `librknnrt.so` 能否加载 rk3576 target（ISS-155） |
| ★**V9** | ★**板级**: ①**9 路电源全部有使能**（各轨测试点有电压）②**无复位/掉电**（连续启停 20 次正常）③**MIPI 差分阻抗符合设计**（回厂测阻抗）④**FPC 插拔 20 次不虚接** ⑤**各测试点电压在规格内** | ★**板子回来后的自检清单** |

---

## 6. ★ 风险与退路（每条都有退路）

| 风险 | 触发 | 退路 |
|---|---|---|
| ★**打样周期成为最长路径** | 板子回来要等 | ★**软件侧 S2/S3/S4/S7/S9 先做完**；★**F1~F3 已修** ⇒ 板子回来只差 S1/S5/S8 + tuning ⇒ ★**回来后 1~2 天就能出画面**（前提是板子一次做对 ⇒ ★**这正是 F1~F11 清单的意义**） |
| ★**SOM 买不到 / 停产** | P3 失败 | 换第二家 SOM（L2）⇒ ★**不换主控**（换主控会推翻 ISP3/NPU/DSI 全部） |
| ★**camera 模组无公开现货 / FPC 对不上** | P1 失败 | 换第二家模组 ⇒ 主板 FPC 座跟着改（★**所以 F4 必须在 P1 之后才冻**） |
| ★**屏模组驱动 IC 不在内核白名单** | P2 失败 | 换白名单型号（重买，不自己抄 dts） |
| ★**rk3576 target 在 RK3572 上加载失败** | S1 失败 | ★**改用 RK3576 板做 demo**（★但**主板仍是 RK3572** ⇒ ★**主板要留"换芯"余量**: 电源树按 3.3V/5V 通用输入设计） |
| ★**tuning 缺 mesh** | S6 | 先无 IQ 跑通链路；mesh 1~2 人日补 |
| Radxa 板不可达 | — | 不影响自研主线（A7S 线单独排网络恢复） |

---

## 7. ★ 现在需要老板拍板的两件事

1. ★**P1/P2/P3 的选型授权**：camera 模组（公开在售 IMX415）、屏模组（公开在售 8HD/10FHD，驱动 IC 在白名单内）、RK3572 核心板（公开在售）⇒ ★**默认按"先选这三件、拿到针位表再画主板"推进**
2. ★**视崖 0.49" 屏在 demo 阶段用公开屏替代**（原屏无公开对标品）⇒ ★**默认如此，视崖留整机阶段**

---

**证据等级**: 模组/核心板规格与在售状态 = `[公开]`（★**具体链接以 `HW/PART_ALTERNATIVES_REGISTRY.md` 为准**）· 器件电源/模式/target 合法性/精度 = `[实测]`（facts 与 ISS-147）· 板级接法与阻抗通则 = `[推算]` · 层数/尺寸 = `[待定]`。
