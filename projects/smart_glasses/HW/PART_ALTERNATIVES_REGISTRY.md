# HW/PART_ALTERNATIVES_REGISTRY.md —— 替代料候选清单 (L1/L2 阶段的凭证)

| 项 | 内容 |
|---|---|
| 作者 | **硬件总工 (hw-lead)** |
| 日期 | 2026-11-02 20:16 (GMT+8) · **2026-11-02 23:10 补 ISS-158 选型闭环** (三类"针位表/引脚定义/尺寸"列已补 + 新增 C6/C7) |
| 触发 | 老板 2026-11-02 19:45 定**四级阶梯**: ①先上网找 → ②换替代料 → ③**所有元件都试过了还找不到** → ④才走采购方案咨询厂家; ★**demo 阶段量很小 ⇒ 不走批量定制采购, 物料走「公开现货 / 样品渠道」** |
| 本单目的 | ★**把"都试过了"从形容词变成可核查的清单** —— 每个物料类别给出**公开可点的候选**, 并标注**已试 / 未试** |
| 纪律 | ①每条链接**实测可点** (标注实测 HTTP 状态; 403 = 本站对 curl 的 Cloudflare 拦截, 浏览器可开, 已注明) ②查不到的写 **未查**, **不猜价格 / 库存 / 针数** ③**本单不含任何"联系厂家"动作** (L4 未触发) ④**已试/未试栏真的动** |
| 数据来源 | 公开资料实测 + `HW/open_source_rank.py` (D1~D5, 已跑过, 未重测) + Rockchip BSP 内核实测 |

★**判读方式 (给 boss)**:
- **"未试"不等于"没查"** —— 本单绝大多数候选的"已查"程度是 **公开页面/规格书/内核源码实测**, "已试"指**上手跑通/实物验证**, 目前项目里 **零采购记录** (grep `已购|已下单|已到手` 全库无命中) ⇒ **L3 的门槛还没到, 现在正是 L1/L2 阶段**。
- ★**最值钱的一条结论在第 3 类 (屏幕)**: 内核里**确实**有 ST7701 / ST7703 / ILI9881C / NV3052C 的现成 panel 驱动 + 完整 init code 范例 ⇒ **面板 init code 大概率不必问厂家**; ★**但老板假设里的 EK79007+EK73217 与 NV3049, 内核里其实【没有】** (见 §3.3, 实测文件清单) ⇒ **这两颗不能当"白送"算**。

---

## 1. 主控载体 (SOM / SBC) —— demo 链路第 1 环

★**demo 需求**: RK3572/RK3576 一颗 SoC + **≥1 路 MIPI-CSI (2-lane 起)** + **≥1 路 MIPI-DSI (4-lane)**; ★**引脚定义是否公开 = 画主板的硬前提** (画不出来 = 投板后返工 2-4 周)。

| 类别 | 候选名 | 公开在售渠道 (可点链接) | 关键规格 | ①能否满足 demo 硬指标 | ②数据来源是否充足 (D1~D5) | **已试/未试** | 备注 |
|---|---|---|---|---|---|---|---|
| 主控载体 | **Forlinx OK3572-C** (RK3572 SBC) + ★**FET3572-C SoM** | 规格页 <https://www.forlinx.net/single-board-computer/rk3572-dev-kit-ok3572-c-180.html> (实测 200) · SoM 页 <https://www.forlinx.net/product/rk3572-som-fet3572-c-179.html> (实测 200) · **产品简介 PDF** <https://www.forlinx.net/download/FET3572-C-SoM-OK3572-C-SBC-Product-Brief.pdf> (实测 200 ★**需浏览器 UA 否则 403**) · 下载中心 <https://www.forlinx.net/resources/download-center.html> (实测 200, 逐针表需注册登录) | SoM: RK3572 8 核 A72+A53 · **MIPI-CSI 2 路 × 4-lane D-PHY v1.2 (2.5Gbps/lane), 每路可拆 2×2-lane, 最多 4×2-lane 相机** · **MIPI-DSI 1 路 4-lane (DSI 1.2, 4lane×2.5Gbps)** · HDMI 2.1 (4K@60) · eDP · DVP 1 路 | ✔ CSI 4-lane 够 IMX415 1080p60 RAW10 (1.244Gbps) · DSI 4-lane 够 1920×1080 RGB888 (373Mbps) | ★**高**: 产品简介 PDF 公开 (含接口表 + 驱动支持清单: MIPI-DSI 7" LCD070CM+1024600AB21) | **未试** (仅公开资料核查) | ★**首选**: 与 `HW/DEMO_BOARD_HW_DECISION.md` Step1 选型一致 (同一款) ⇒ 零换型成本 |
| ★★ **SOM 规格 (ISS-158 实测, P3 定案)** | ★**Forlinx FET3572-C (RK3572 SOM)** | ★**产品简介 PDF 原文 (实测 200, 需浏览器 UA)** | ★**外形 68mm × 50mm** · ★**连接方式 = 板对板连接器 4 × 100Pin, 针间距 0.4mm, 配合高度 1.5mm** (⇒ 主板要画 4 个 0.4mm 100pin BTB = 400 焊盘) · ★**供电 DC 5V–13V** · 温度 0~+80℃ (J 工业级 −40~+85℃) · **CSI 2×4-lane / DSI 1×4-lane** · 2×GMAC · ≤4 CAN-FD · ≤12 UART · ≤9 I2C(+1 I3C) · ≤5 SPI · ≤16 PWM · 3×Combo SerDes · 1×DSMC | ✔ | ★**规格骨架全齐 (实测)**; ★**逐针引脚定义表 = 未查** (在下载中心, 需注册登录 ★**属公开下载, 非 L4**) · ★**机械尺寸图/连接器 footprint = 未查** · ★**PDF 明写 "Compatible with the pin design of the FET3576-C SoM" ⇒ 拿到 FET3576-C 的引脚表即等于拿到 FET3572-C 的** · 同厂同类件 FET3588-C SoM PDF 在 DigiKey 公开镜像 (实测 200) 可作结构参照 | **未试** | ★**主板画板前必办: 从 Forlinx 下载中心取 3 个文件 = 引脚定义表 + 原理图 + 机械尺寸图**; ★**在此之前 400 针的焊盘坐标与电气含义都不能定 ⇒ 不得开跑线** |
| 主控载体 | **ArmSoM CM5** (RK3576 核心板, **CM4 兼容**) + CM5-IO | 文档站 <https://docs.armsom.org/armsom-cm5> (实测 200) · RK3576 SBC 总览 <https://www.armsom.org/post/rk3576-sbc-introduction> · Sige5 SBC 文档 <https://docs.armsom.org/armsom-sige5> | RK3576 · CM5 55×40×4.9mm, 4.5~5.5V 输入 · **MIPI-CSI 2 路 4-lane (2.5Gbps/lane)** · **MIPI-DSI 1 路 4-lane** · HDMI 2.1 + DP1.4 · 40-pin 排针 | ✔ 同上 | ★**高**: 文档站公开 (规格 + 40-pin 定义 + 相机/显示用法章节 <https://docs.armsom.org/interface-usage/camera>) | **未试** | ★**CM4 兼容 = 引脚生态现成** (RPi 15p/22p CSI 座可直插) ⇒ 适合"公开模组 + 公开相机模组"零改造组合 |
| 主控载体 | **DFRobot RK3576 核心板 + 评估板 (DFR1218)** | Wiki <https://wiki.dfrobot.com/dfr1218> (实测 200) · 载板接口指南 <https://wiki.dfrobot.com/dfr1218/docs/23725> · 套件页 <https://www.dfrobot.com/product-3143.html> (RK3576+RK1828 套件, **含 IMX415 相机模组**) | RK3576 6TOPS NPU · **载板引出 3 路 MIPI-CSI, 每路 4-lane** · SoC 侧共 5 个 CSI-2 (Port0 支持 4-lane 或 3×C-PHY) · **MIPI DSI-2 V1.1, 4-lane, ≤2560×1600@60, 10-bit RGB** · DP1.4 + HDMI2.1 | ✔ CSI 通道数最多 (4-lane×3) | ★**高**: Wiki 公开 **Pinout & Specs 表** + 载板接口逐项说明 | **未试** | ★**套件自带 IMX415 相机模组** ⇒ demo 链路"主控+相机"一次到位, 但 **价格未查** |
| 主控载体 | **Banana Pi BPI-CM5 Pro** (RK3576 核心板) | 文档 <https://docs.banana-pi.org/en/BPI-CM5_Pro/BananaPi_BPI-CM5_Pro> (实测 200) | RK3576 · **MIPI-CSI 1 路 4-lane + 1 路 2-lane** · **MIPI-DSI 1 路 4-lane (≤2K@60)** · HDMI 2.1 + DP1.4 · 40-pin | ✔ | ★**中高**: 文档公开接口表 | **未试** | CSI 4-lane 只有 1 路 ⇒ 若日后要双摄不够 |
| 主控载体 | Luckfox Core3576 (RK3576, 260-pin SO-DIMM 核心板) | 评测公开页 <https://openelab.io/blogs/learn/luckfox-core3576-review-rk3576-edge-ai-board-with-6-tops-npu-the-efficient-mid-range-contender> | RK3576 SoM 69.6×45mm, 260-pin SO-DIMM · 载板 2× MIPI CSI · **MIPI DSI 4-lane ≤2K@60 (默认 1280×800 面板)** | ✔ | ★**中**: 仅公开评测页; **官方规格页未查** | **未试** | 二手渠道, 优先级最低; **官方页未查** 已如实标注 |

★**第 1 类小结 (给 boss 的判断)**:
1. ★**"引脚定义公开"这一栏只有 DFRobot(RK3576 Wiki pinout 表) 与 ArmSoM(docs 站) 我实测到了公开定义**; Forlinx 只有**产品简介 PDF** 公开, **引脚表/原理图下载页未查** ⇒ ★**画板前必须先解决的就是这条**, 但 **不用问厂家** —— 走各家的**公开下载区/文档站**即可 (L1 路径)。
2. ★**RK3572 与 RK3576 都可选** ⇒ **主控这颗不必再当风险项**; 但 ★**换 SoC 家族会同时废掉摄像头与显示的两条驱动基线** (D2/RK BSP 驱动都是 RK3572 基线实测) ⇒ **换板型时优先换模组, 不换 SoC**。

---

## 2. camera 模组 (MIPI-CSI, 带 FPC 出线) —— demo 链路第 2 环

★**demo 需求**: IMX415 模组, **1080p60 可出图**, **FPC 出线**; ★**关键约束: 主板端我们画的是 0.5mm 24p** ⇒ 模组端 FPC 必须是**同规格**或者**中间要转接排线**。

| 类别 | 候选名 | 公开在售渠道 (可点链接) | 关键规格 | ①能否满足 demo 硬指标 | ②数据来源是否充足 (D1~D5) | **已试/未试** | 备注 |
|---|---|---|---|---|---|---|---|
| camera 模组 | ★★**Radxa Camera 4K** (IMX415) ★**P1 定案** | 产品页 <https://www.radxa.com/products/accessories/camera4k> (实测 200) · ★**模组官方文档 (含引脚定义表 + 物理规格图)** <https://docs.radxa.com/accessories/camera/camera-4k> (实测 200) · ★**连接器规格页 (含载板侧 31p 针序)** <https://docs.radxa.com/en/rock4/rock4d/hardware-use/mipi-csi> (实测 200) · IMX415 datasheet <https://dl.radxa.com/accessories/camera-4k/IMX415-AAQR-C_Datasheet_E19504.pdf> | IMX415 8.29MP · **4-lane CSI, FPC 座 31-pin / 0.3mm / 型号 FH35C-31S-0.3SHW(50)** · ★**逐针表实测拿到 (31/31)**: 1 GND/2 MDN4/3 MDP4/4 GND/5 MDN3/6 MDP3/7 GND/8 NC/9 NC/10 GND/11 MDN2/12 MDP2/13 GND/14 MDN1/15 MDP1/16 GND/17 MCN/18 MCP/19 GND/20 MCLK/21 GND/22 NC/23 NC/24 SCL/25 SDA/26 NC/27 RESET/28-29 VCC3.3V/30-31 VCC5V · ★**FOV D88.2±5° H75±3° V59±2°, CRA 15°, M12×P0.5, EFL 2.95±5%mm, BFL 4.64mm, 镜间距 4.00mm** · SCCB **0x1a** · 排线 AC006 (31P0.3↔31P0.3) / AC008 (31P0.3↔15P1.0) | ✔ 8.29MP 1080p60 绰绰有余 (项目已定 IMX415) | ★**高 (sensor 侧)**: D1 主线 imx415.c ✔ · D2 RK BSP imx415.c ✔ · D3 rkaiq ISP3x IQ json ✔ · D4 51 仓库 · D5 openipc ✔ ⇒ **10/10** (脚本实测) | **未试** (未上手) | ★★★ **P1 定案 (ISS-158 实测)**: ★**"0.5mm/24p 自研目标规格"作废 → 主板 camera 座 = 31p/0.3mm 照抄上表, 不用转接排线** · ★**1080p60 = 1944×1097 / 12bit / `0x3020=0x01` (2/2 binning) / VTS `0x0C5D`→`0x062E`** (BSP imx415.c 实测, 只改 VMAX 一处) · ★**模组级只要 3.3V + 5V (针 28-31), sensor 三条轨 (1.1/1.8/2.9V) 疑在模组内部 ⇒ 主板 LDO 可省 3 颗 [推断, 待核]** · ★**AC 耦合是否内置 = 未查 ⇒ 主板 4 组差分对各留 0402 耦合位默认 DNP** |
| camera 模组 | **Radxa Camera 8M 219** (IMX219) | 产品页 <https://www.radxa.com/products/accessories/camera-8m-219> (实测 200) · 文档 <https://docs.radxa.com/en/dragon/q6a/accessories/camera-8m-219> (实测 200) | IMX219 8MP · **15-pin / 1.0mm / 贴板翻盖式 (Flip type, bottom contact)** · 排线 AC004 (15P1.0↔15P1.0) | ⚠️ IMX219 1080p60 **帧率不达标** (公开口径 1080p30 级) ⇒ 只做**链路冒烟**用, 不做最终相机 | ★**高**: IMX219 主线+BSP 驱动都有, 但**不在本项目 D1~D5 表** (本项目 sensor 池是 IMX415/AR0521/OV9281/OV02B10/OV02C10/AR0234CS/OV04C10) ⇒ 本栏 **未评级** | **未试** | ★**它的价值是"15p/1.0mm = RPi 标准"** ⇒ **引脚定义现成**: RPi 15p 完整针位表公开 (见第 5 类) ⇒ 做 0.5mm 24p 主板时可照抄信号分配 |
| camera 模组 | **Arducam IMX415 (SKU B0569)** | 文档 <https://docs.arducam.com/Raspberry-Pi-Camera/Native-camera/8.3MP-IMX415> (★**403 = Cloudflare 拦 curl, 浏览器可开**) · 针位总表 <https://docs.arducam.com/Raspberry-Pi-Camera/raspberry-pi-camera-pinout> (403 同上) · 针位表镜像 <https://www.arducam.com/blog/raspberry-pi-camera-pinout> (403 同上) | IMX415 8.3MP Starvis · 3840×2160 · MIPI CSI-2 · 固定焦 3m∞ · FOV 104°(D)×88°(H) · **15-pin / 22-pin RPi 标准派生连接器** | ✔ 8.3MP (但公开口径 3864×2192@15.75fps 满帧 ⇒ **1080p60 需靠 sensor 窗口化, 项目已确认 BSP 带该模式**) | ★**高**: sensor 侧 10/10 (同 IMX415) · **模组侧公开参数有** (SKU/分辨率/接口/FOV/对焦) | **未试** | ★**Arducam 的 15p/22p 针位表在公网公开** (含 22p 逐针表) ⇒ ★**这是本项目 FPC 针位表最省事的公开参照** |
| camera 模组 | **Arducam OV9281 (SKU B0452, 22/TOP)** | 文档 <https://docs.arducam.com/Raspberry-Pi-Camera/Native-camera/Global-Shutter/1MP-OV9281-OV9282> (403 = 拦 curl) | OV9281 1MP **全局快门** 1280×800, 1/4" 3µm, 22-pin TOP | ✘ **分辨率/帧率不达标** (1280×800 vs 要 1080p60) | ★**中**: D2 BSP 驱动 ✔ / D3 IQ ✘ / D4 38 / D5 ✔ ⇒ 6/10 (脚本实测) | **未试** | 列为**已排除的备胎**: 若后期要换全局快门, 它是公开现货里的首选 |
| camera 模组 | **Waveshare IMX219 (Pi5-IMX219-77-120)** | 公开在售页 (Amazon 官方店铺) <https://www.amazon.com/waveshare-Compatible-Raspberry-Interface-Resolution/dp/B0CPLZR5JJ> | IMX219 8MP 3280×2464 · MIPI-CSI · 120° FOV · **RPi 15p 标准** | ⚠️ 同 8M 219, 只做链路冒烟 | **未评级** (不在本项目 sensor 池) | **未试** | ★**唯一公开可点的 IMX219 在售链接** (waveshare.com 自家相机页 URL 未查) |
| camera 模组 | **DFRobot RK3576+RK1828 套件自带 IMX415 相机模组** | <https://www.dfrobot.com/product-3143.html> | IMX415 + FPC 出线 (随套件) | ✔ | ★**sensor 侧 10/10**; **模组 FPC 针数/间距: 未查** | **未试** | ★**"主控+相机一次到位"的最省事路线**; 规格页未抓细节 ⇒ 针数未查 |

★**第 2 类小结**:
1. ★**FPC 规格真相**: 公开在售的 IMX415 模组**几乎都是 31p/0.3mm (Radxa) 或 RPi 15p/1.0mm / 22p/0.5mm 派生 (Arducam)**, **几乎没有"0.5mm 24p"现货** ⇒ ★**我们主板端画的 0.5mm 24p 是个自造规格, 落地前要么改成 RPi 标准 (15p/22p, 针位表公开), 要么接受一条转接排线**。★**这条必须进采购硬判据, 且**是**本单最可能踩坑的地方。
2. ★**针位表公开性**: Arducam 公网公开 RPi 15p/22p 逐针表 + 15↔22 转换原理图 ⇒ ★**我们要 24p 的信号分配, 照 RPi 15p 表改是最省的** (CSI 差分 + CLK + I2C + RESET + 电源 + 地, RPi 表已全覆盖)。

---

## 3. 屏幕模组 (MIPI-DSI, 带驱动板 + FPC) —— demo 链路第 3 环 ★★本单核心

★**老板的假设**: 公开在售的 MIPI-DSI 屏模组驱动 IC 是公开的 (ST7701 / EK79007+EK73217 / NV3049 等) ⇒ **Rockchip 内核里就有这些 panel 的驱动与时序** ⇒ **面板 init code 大概率不必问厂家** ⇒ ★**请在公开资料里找到该 panel 驱动/时序在哪 (内核路径/文件名)**。

### 3.1 ★★ 内核实测: Rockchip BSP develop-6.1 `drivers/gpu/drm/panel/` 全部 79 个文件里, 与 DSI 相关的驱动 (实测 GitHub API 列目录)

| 面板驱动 IC | **内核路径 (实测)** | 状态 | 备注 |
|---|---|---|---|
| **ST7701** (Sitronix) | ★★`drivers/gpu/drm/panel/panel-sitronix-st7701.c` | ★**BSP develop-6.1 ✔ + 上游主线 ✔** | 实测源码 of_match: `densitron,dmt028vghmcmi-1a` (**480×640, 2-lane MIPI DSI, 内置 ST7701**) 与 `techstar,ts8550b` (**480×854, 2-lane, 内置 ST7701**) ⇒ ★**这块屏就是"公开面板 + 内核驱动"的现成组合** |
| **ST7703** | `drivers/gpu/drm/panel/panel-sitronix-st7703.c` | BSP develop-6.1 ✔ + 主线 ✔ | |
| **ST7789V** | `drivers/gpu/drm/panel/panel-sitronix-st7789v.c` | BSP develop-6.1 ✔ + 主线 ✔ | |
| **ILI9881C** | `drivers/gpu/drm/panel/panel-ilitek-ili9881c.c` | BSP develop-6.1 ✔ + 主线 ✔ | |
| **NV3052C** (NewVision) | `drivers/gpu/drm/panel/panel-newvision-nv3052c.c` | BSP develop-6.1 ✔ + 主线 ✔ | ★**注意是 NV3052C** |
| **NV3051D** (NewVision) | `drivers/gpu/drm/panel/panel-newvision-nv3051d.c` | ★**上游主线 ✔ / BSP develop-6.1 ✘** | BSP 侧没有 |
| **OTM8009A** (Orisetech) | `drivers/gpu/drm/panel/panel-orisetech-otm8009a.c` | BSP develop-6.1 ✔ + 主线 ✔ | |
| **HX8394** (Himax) | `drivers/gpu/drm/panel/panel-himax-hx8394.c` | ★**上游主线 ✔ / BSP develop-6.1 ✘** | 上游 6.0 以后加入 |
| **RPi 7" 触控屏 (TC358762)** | `drivers/gpu/drm/panel/panel-raspberrypi-touchscreen.c` | BSP develop-6.1 ✔ + 主线 ✔ | ★**配合 radxa-overlays 的 `rock-5b-raspi-7inch-touchscreen.dts` (compatible = `raspits,tc358762`, lane-rate 605, 完整 display-timings) ⇒ 800×480 这条路是"内核驱动 + 公开 dts"双公开** |

### 3.2 ★★ init code 在哪 —— 三个可直接抄的公开范例 (全部实测抓到原文)

| # | 公开范例 | **init code / 时序在哪 (实测路径)** | 抄什么 |
|---|---|---|---|
| ① | **Rockchip 自己 RK3576 EVB 的 DSI 面板** | ★★`arch/arm64/boot/dts/rockchip/rk3576-evb.dtsi` → `&dsi { dsi_panel: panel@0 { compatible = "simple-panel-dsi"; dsi,lanes = <4>; dsi,format = <MIPI_DSI_FMT_RGB888>; panel-init-sequence = [ …~30 条 Command2/BK0/BK1 寄存器写… ]; panel-exit-sequence = […]; display-timings { clock-frequency = <132000000>; hactive = <1080>; vactive = <1920>; … } } }` | ★**最贴我们**: **1080×1920 / 4-lane / RGB888** —— 我们目标屏是 **1920×1080 (横置)**, 物理上就是这块屏转 90° ⇒ ★**init code 直接可抄, 只要加一条 orientation 翻转** |
| ② | **Radxa Display 10 FHD (1200×1920)** | `radxa-pkg/radxa-overlays` → `arch/arm64/boot/dts/rockchip/overlays/radxa-cm5-io-radxa-display-10fhd.dts` → `compatible = "simple-panel-dsi"` + `panel-init-sequence = [05 78 01 11 / 05 00 01 29]` + `display-timings { clock-frequency = <160000000>; hactive = <1200>; vactive = <1920>; … }` | ★**"simple-panel-dsi + dts 里塞 init code"的完整模板** (含 EOT_PACKET 标志) |
| ③ | **RPi 7" 800×480 (TC358762)** | `radxa-overlays` → `arch/arm64/boot/dts/rockchip/overlays/rock-5b-raspi-7inch-touchscreen.dts` → `compatible = "raspits,tc358762"` + `rockchip,lane-rate = <605>` + `display-timings { clock-frequency = <26000000>; hactive = <800>; vactive = <480>; … }` | ★**800×480 这条路的 dts 现成** |

★⇒ **结论 (硬)**: ★**面板 init code 不必问厂家** —— 路径是 **Rockchip BSP 内核自带 panel 驱动 + 公开 dts 范例**, 不是问人。

### 3.3 ★★ 反例 (必须说清, 否则老板会拿错假设去采购): **EK79007 / EK73217 / NV3049 在内核里没有**

★**实测方法**: 用 GitHub API **逐个列出** `rockchip-linux/kernel` (分支 `develop-6.1`) 与 `torvalds/linux` (分支 `master`) 的 `drivers/gpu/drm/panel/` **全部文件名**, 再按 `ek7 / ek73 / nv30 / nv3049` 过滤。
★**实测结论**:
- **BSP develop-6.1 (79 个文件)**: **无 `panel-ek79007.c`、无 `panel-ek73217.c`、无任何 `nv3049` 文件** ⇒ ★**EK79007/EK73217/NV3049 这三个 IC 在 Rockchip BSP 6.1 基线上【没有现成 panel 驱动】**。
- **上游主线 (master)**: 同样**无 ek79007 / ek73217 / nv3049**; 主线有的是 `nv3051d` / `nv3052c` / `hx8394` / `jd9365da-h3` / `ili9806e-dsi` / `raspberrypi-touchscreen` 等。
- ★**那 init code 从哪来?** —— Rockchip 生态里 EK79007 这类屏**通常走 `compatible = "simple-panel-dsi"` + dts 里手写 `panel-init-sequence`** (就像 §3.2 的 ①②) ⇒ ★**不是"内核白送", 是"我们自己抄一个 dts"**, 而**抄谁的 dts = 找用同一块屏的公开板子** (这才是 L1 的活)。

### 3.4 公开在售屏模组候选 (带驱动板 + FPC)

| 类别 | 候选名 | 公开在售渠道 (可点链接) | 关键规格 | ①能否满足 demo 硬指标 | ②数据来源是否充足 | **已试/未试** | 备注 |
|---|---|---|---|---|---|---|---|
| 屏幕模组 | ★**Waveshare 4.3inch DSI LCD** (800×480, 电容触控) | 产品页 <https://www.waveshare.com/4.3inch-dsi-lcd.htm> (实测 200) · ★**Wiki 含完整 Pin Definition 表** <https://www.waveshare.com/wiki/4.3inch_DSI_LCD> (实测 200) | 800×480 IPS · DSI 2-lane (DSI_DN0/DP0 + DN1/DP1) · **FPC 15PIN / 1.0mm / 50mm 与 160mm 两根排线随附** · 触控 I2C · **公开 wiki 的 Pin Definition: 1 GND / 2 DSI1_DN1 / 3 DSI1_DP1 / 4 GND / 5 DSI1_CN / 6 DSI1_CP / 7 GND / 8 DSI1_DN0 / 9 DSI1_DP0 / 10 GND / 11 SCL0 / 12 SDA0 / 13 GND / 14 3V3 / 15 3V3** | ✔ DSI 2-lane 带宽: 800×480@60 RGB888 ≈ 74Mbps ≪ 2×1.2Gbps ⇒ **带宽够**; ⚠️ **分辨率只有 800×480, 不到 1920×1080** ⇒ 只能做**链路冒烟**, 不能当最终显示 | ★**高**: **驱动板 + FPC 针位表 + 接线图全公开**; ★**面板 IC: 未查** (wiki 只说 "Daspberry Pi 上直接驱动", 未写 IC) ⇒ **IC 与内核驱动的对应关系: 未查** | **未试** | ★**"针位表公开"这一栏它是满分** ⇒ **做主板 FPC 座针位分配的现成模板** |
| 屏幕模组 | **Waveshare 2.8inch DSI LCD** (480×640, 电容触控, 光学贴合) | 产品页 <https://www.waveshare.com/2.8inch-dsi-lcd.htm> (实测 200) · Wiki <https://www.waveshare.com/wiki/2.8inch_DSI_LCD> (实测 200) | 480×640 IPS 光学贴合 · DSI · **15PIN / 1.0mm** · Pin Definition 同 4.3" 格式 (实测已抓, 15 针全表公开) | ✔ 带宽足够; ⚠️ 分辨率 480×640 ⇒ 只做冒烟 | ★**高**: 针位表公开; **面板 IC: 未查** | **未试** | ★**480×640 与内核 `densitron,dmt028vghmcmi-1a` (480×640, 内置 ST7701) 分辨率一致 ⇒ ★**"这块屏很可能就是 ST7701 那颗"** —— 但这是**推断, IC 未查**, 不可当结论 |
| 屏幕模组 | ★★**Radxa Display 8 HD / 10 FHD** (MIPI-DSI 一体屏模组) ★**P2 定案** | Display 8 HD 产品页 <https://www.radxa.com/products/accessories/display-8hd> (实测 200) · ★**8 HD 官方文档 (含全 40 针 Pinout 表 + 规格)** <https://docs.radxa.com/accessories/display/lcd-8-hd/lcd-8-hd-product> (实测 200) · ★**10 FHD 官方文档 (含全 40 针信号定义表 + 背光参数)** <https://docs.radxa.com/accessories/display/lcd-10-fhd/lcd-10-fhd-product> (实测 200) · Display 10 FHD 产品页 <https://www.radxa.com/products/accessories/display-10fhd> (实测 200) | ★**FPC = 屏侧 40p / 0.5mm** (主板侧 39P 0.3mm 或 15P 1.0mm) · ★**8 HD 逐针表实测拿到 (40/40)**: 1 NC/2 VDD 3V3/3 VCCIO 1.8-3.3V/4 NC(INT1)/5 Reset/6 NC(INT2)/7 GND/8-9 MIPI_0N-P/10 GND/11-12 MIPI_1N-P/13 GND/14-15 MIPI_CKN-P/16 GND/17-18 MIPI_2N-P/19 GND/20 MIPI_3N/21 MIPI_3P/22-23 GND/24 TP_RESET/25 TP_VCC/26 TP_INT/27 TP_SDA/28 TP_SCL/29-30 GND/31-32 VDD 3V3/33-34 GND/35-36 LED−/37-38 NC/39-40 LED+ · 8 HD: 800×1280 **16.7M 全彩**, 有效显示区 **107.64×172.224mm**, 300cd/m², GT911 5点触控, 2/4-lane 皆可 · 10 FHD: 1200×1920 有效区 135.36×216.58mm, 外形 155×246.16×5.95mm, ★**背光 LED 12.8V typ / 14V max @200mA typ** | ✔ 10 FHD 带宽: 1200×1920@60 RGB888 ≈ 415Mbps, 4-lane 绰绰有余 | ★**高**: **radxa-overlays 里有对应 Rockchip dts** (实测 `radxa-cm5-io-radxa-display-10fhd.dts` 含 `simple-panel-dsi` + **完整 init sequence + display-timings 160MHz/1200×1920**) ⇒ ★**屏 + dts 都在公开仓库里** | **未试** | ★★★ **P2 定案 (ISS-158 实测)**: ★**主板 display 座 = 40p/0.5mm 照抄上表** · ★**判据口径改了: "驱动 IC 在内核白名单"只管**专用 panel driver**; 走 `simple-panel-dsi` 的屏 (10 FHD) **不依赖任何专用驱动** ⇒ ★**P2 首选 `simple-panel-dsi` 路线 (10 FHD), 8 HD (`radxa,display-8hd`) 需带 Radxa 私有 driver ⇒ 降级备选** · ★**init code 公开可抄: `rk3576-evb.dtsi` 里 263 条 (1080×1920/4-lane, 与我们目标屏最贴)** · ★**主板电源树要加一路 12V BOOST 供背光** · ★**屏侧连接器型号 = 未查** |
| 屏幕模组 | **Forlinx 7-inch MIPI 屏 LCD070CM+1024600AB21** | 公开在售 (Forlinx) —— **产品页未查**; ★**该屏型号出现在 OK3572-C 公开产品简介 PDF 的驱动支持清单里** (<https://www.forlinx.net/download/FET3572-C-SoM-OK3572-C-SBC-Product-Brief.pdf> 实测 200) | 1024×600 @30fps | ⚠️ 30fps ⇒ **不满足 1080p60 观感目标**, 且**不是我们的目标屏** | ★**中**: 型号与兼容性公开, **规格页/针位表: 未查** | **未试** | ★**价值是"公开在售 + RK3572 SBC 原厂支持清单里点名"** ⇒ 零驱动风险, 但分辨率/刷新率只适合冒烟 |
| 屏幕模组 | **RPi 7" DSI 触控屏 (TC358762, 800×480)** | ★**Rockchip 侧 dts 公开**: <https://github.com/radxa-pkg/radxa-overlays/blob/HEAD/arch/arm64/boot/dts/rockchip/overlays/rock-5b-raspi-7inch-touchscreen.dts> (实测 200) · 内核驱动 `panel-raspberrypi-touchscreen.c` | 800×480 · DSI 2-lane · 内核驱动 + dt binding 公开 | ⚠️ 分辨率只到 800×480 | ★**高 (驱动侧)**: 内核驱动 + 公开 dts + 公开 binding | **未试** | ★**"内核驱动 + 公开 dts"匹配最干净的一块** |

★**第 3 类小结 (★这是本单最值钱的结论★)**:
1. ★★**"面板 init code 不必问厂家" = 成立** ⇒ 三条现成路径: **(a)** 选内核已有驱动的 IC (ST7701 / ST7703 / ST7789V / ILI9881C / NV3052C / OTM8009A) ⇒ **加一个 dts 节点即可**; **(b)** 选 `simple-panel-dsi` + **抄 `rk3576-evb.dtsi` 的 init sequence** (1080×1920/4-lane, 与我们屏最贴); **(c)** 走 `radxa-overlays` 里对应屏的公开 dts (10 FHD / RPi 7")。
2. ★★**但老板假设里的 EK79007+EK73217 与 NV3049, 内核里【没有】** ⇒ **不能拿"内核有驱动"当采购理由去选这三颗 IC 的屏** ⇒ **选屏时按"内核驱动清单"反推: ST7701/ST7703/ST7789V/ILI9881C/NV3052C/OTM8009A/HX8394/RPi-touchscreen 这 8 颗才是零移植的**。
3. ★**屏的分辨率是 demo 的真瓶颈**: 公开现货 MIPI-DSI 一体屏里, 最高只有 **1200×1920 (Radxa 10 FHD) / 800×1280 (8 HD)**, 800×480/480×640 一大堆; ★**"1920×1080 视涯 SiOLED"这块屏本身在公开现货里【没有可点到的对标品】** ⇒ **视涯这块屏的采购仍是独立风险项 (走 L1 公开渠道找, 找不到再谈 L2)** —— ★**但它不影响 demo 跑链路**: demo 用 8 HD 或 10 FHD 就能验完 DSI 通路。

---

## 4. sensor 裸件 —— ★**直接复用 `HW/open_source_rank.py` 实测结果 (未重测)**

★**跑法**: `cd projects/smart_glasses && python3 HW/open_source_rank.py` ⇒ 实测输出 (IMX415 10/10 … OV04C10 0/10)。

| 类别 | 候选名 | 公开在售渠道 (可点链接) | 关键规格 | ①能否满足 demo 硬指标 | ②数据来源是否充足 (D1~D5, **脚本实测**) | **已试/未试** | ★**换这颗时网表要跟着改什么** |
|---|---|---|---|---|---|---|---|
| sensor 裸件 | **IMX415** ★**demo 定案** | Sony 公开 flyer <https://www.sony-semicon.com/files/62/flyer_security/IMX415-AAQR_Flyer.pdf> · ★**datasheet (Radxa 公开镜像)** <https://dl.radxa.com/accessories/camera-4k/IMX415-AAQR-C_Datasheet_E19504.pdf> | 3840×2160 (8.3MP) 1/1.8" 1.45µm, **滚动快门** · 上电序 **DVDD(1.1V) → OVDD(1.8V) → AVDD(2.9V)**, 三轨 200ms 内到位 | ✔ **满足 1080p60** (3840×2160@60 可裁/窗口化 1080p60) | ★**10/10** — D1 主线 `imx415.c` ✔ · D2 RK BSP `imx415.c` ✔ · D3 rkaiq ISP3x `imx415_CMK-OT2022-PX1_IR0147-50IRC-8M-F20.json` ✔ · D4 51 仓库 · D5 openipc ✔ | **已试** (公开 datasheet + 内核 + IQ 三方实测, `HW/IMX415_DEMO_SENSOR_FACTS.md`) | ★**三条轨全改**: `SENSOR_CORE` 1.2V→**1.1V** (TPS7A20-12→**TPS7A20-11**, 电流 50mA→**250mA**) · `SENSOR_VDD_IO` 2.8V→**1.8V** (★**不改直接烧 sensor**, OVDD 上限 1.90V) · `SENSOR_AVDD` 2.8V→**2.9V** (typ; 电流 30mA→**156mA**) · ★**I2C_A 上拉**: 建议改 **1.8V**, 阻值 **1.0k~2.2k** (3.3V 上拉时 IOL 3mA 只允许 R≥967Ω) · ★**上电顺序**: 现网表三轨同起、无顺序 ⇒ **demo 可先跑, 量产必须给 AVDD 加 EN/延时** (ISS-152) |
| sensor 裸件 | **AR0234CS** (onsemi) ★**整机方案候选** | 公开 datasheet <https://www.sunnywale.com/uploadfile/2022/0222/AR0234CS-D-Awin.PDF> | 1920×1200@60, **全局快门**, 1/2.6" 3.0µm · **VDD 1.2V / VDD_IO 2.8V** · VAA/VAA_PIX/VAA_PHY 可并 2.8V · VDD/VDD_PHY/VDD_DATA 可并 1.2V · **VDDIO_PHY 1.8V 独立** | ✔ 帧率/快门更好, ⚠️ **16:10 不是 16:9** (立体角只丢 9.70%) | ★**3/10** — D1 ✘ · D2 ✘ · D3 ✘ · D4 20 仓库 (含 `opensource206/UC788_AR0234_SENSOR_TO_RK3588` RK3588 同族 bringup) · D5 ✔ | **已试** (公开 datasheet 实测, `HW/AR0234CS_OPEN_SOURCE_FACTS.md` / `AR0234CS_RK3572_PORT_SPEC.md`) | ★★**同一条 `SENSOR_VDD_IO` 轨与 IMX415 差 1.0V (2.8 vs 1.8) ⇒ 换料必改轨**; 另: ★**I2C_A 上拉必须 2.8V** (VIN 绝对最大 = VDD_IO+0.3 = 3.1V ⇒ 3.3V 超规格 0.2V) ⇒ **两条路的 I2C 上拉不能共用一颗 LDO 输出, 建议做成 1.8V/2.8V 两档 (jumper)**; ★**要加第 4 条轨** (VDDIO_PHY 1.8V 无处可接) ⇒ **这是"换料不换板"破功点**; 驱动/IQ 要**移植** (非白送) |
| sensor 裸件 | **AR0521** (onsemi) | 公开 datasheet (onsemi 官网, **具体页 URL 未查**) | 2592×1944@60, 1/2.5", **滚动快门** (electronic rolling shutter + global reset, 非全局) | ⚠️ 滚动快门 ⇒ 不适合当 AR0234CS 替代 | ★**8/10** — D1 ✔ · D2 ✔ · D3 ✘ · D4 7 · D5 ✔ | **部分已试** (只有 open_source_rank 打分, **未做电源域/网表影响核算**) | ★**未查** (电源轨/上电顺序/IO 域未核) ⇒ **本栏空白 = 真实状态** |
| sensor 裸件 | **OV04C10** (豪威) | 公开 datasheet (**具体页 URL 未查**) | 1920×1080@60 路线 | ⚠️ 规格过线, 但生态为零 | ★**0/10** — D1~D5 **全 ✘** (GitHub 搜 `ov04c10` = **0 个仓库**) | **部分已试** (只有打分, 网表影响未核) | ★**未查**; ★**已知风险: 从零写驱动 + 寄存器表要外部给 ⇒ 卡在不可控周期** ⇒ ★**L3 判据上它排在最后** |

★**第 4 类小结**: ★**"换料"这个词在本类里 = "改三条轨 + 改 I2C 上拉 + 可能加一条轨 + 可能重写驱动"**, 不是换个料号就完事。★**因此 §2 的结论 (公开现货模组的 FPC 规格与我们的 24p 不一致) 和 §4 的结论 (电源轨差 1.0V) 合起来说明: ★**demo 阶段的正确做法是"选一条路彻底走通" (RK3572 + IMX415 模组 + 公开 DSI 屏), 而不是"每类都留三五个候选混着试"**。

---

## 5. FPC 连接器与排线

★**demo 需求**: 主板端 2 个座 —— camera 侧 **0.5mm 24p** / display 侧 **0.5mm 20p** (翻盖式, 贴板), 排线 ≤60mm 不跨铰链。

| 类别 | 候选名 | 公开在售渠道 (可点链接) | 关键规格 | ①能否满足 demo 硬指标 | ②数据来源是否充足 | **已试/未试** | 备注 |
|---|---|---|---|---|---|---|---|
| FPC 连接器 | ★**HIROSE FH35C-31S-0.3SHW(50)** | ★**原厂页** <https://www.hirose.com/en/product/p/CL0580-2923-7-50> (实测 200) · 系列页 <https://www.hirose.com/en/product/series/FH35C> (403 = 拦 curl, 浏览器可开) · Mouser <https://www.mouser.com/ProductDetail/Hirose-Connector/FH35C-31S-0.3SHW50> (实测 200) · DigiKey <https://www.digikey.com/en/products/detail/hirose-electric-co-ltd/FH35C-31S-0-3SHW-10/5132543> (403 = 拦 curl) | ★**31 位 / 0.3mm pitch / 0.9mm 高 / 翻盖式 (Back flip actuator) / 上下双面触点 (Top & Bottom) / ZIF / 兼容 0.2mm 厚 FPC / 横向插拔** · 长 10.9mm · 宽 4.2mm | ✔ 4-lane CSI 用 (Radxa Camera 4K 用的就是它) | ★**高**: 原厂页实测抓到规格字段 | **未试** | ★**额定电流 / 弯折寿命: 未查** (原厂页有该字段, 本单未抓) ⇒ **不猜** |
| FPC 连接器 | ★**RPi 标准 15p / 1.0mm (FPC1030-15S-TAG)** | ★**Radxa ROCK4D 公开接口页** <https://docs.radxa.com/en/rock4/rock4d/hardware-use/mipi-csi> (实测 200) (★该页明写型号 + 针数 + 间距 + "pin-compatible with the official Raspberry Pi 15P CSI camera standard") | **15 位 / 1.0mm pitch / 贴板翻盖式** · 型号 FPC1030-15S-TAG | ✔ 2-lane CSI 够 (1080p60 RAW10 = 1.244Gbps, 2 lane × 700Mbps) | ★**高 (针位表)**: ★**RPi 15p 逐针表在公网公开** —— <https://www.arducam.com/blog/raspberry-pi-camera-pinout> (403 = 拦 curl, 浏览器可开) 与 <https://docs.arducam.com/Raspberry-Pi-Camera/raspberry-pi-camera-pinout> (403 同上) | **未试** | ★★**这是本类里"针位表公开"最硬的一条**: 逐针信号名 (1 GND / 2 CAM_D0_N / 3 CAM_D0_P / 4 GND / 5 CAM_D1_N / 6 CAM_D1_P / 7 GND / 8 CAM_CK_N / 9 CAM_CK_P / 10 GND / 11 CAM_IO0 / 12 CAM_IO1 / 13 CAM_SCL …) ⇒ ★**我们 24p 的针位分配照它改, 等于"公开标准"** |
| FPC 连接器 | ★**HIROSE FH12-24S-0.5SH(55)** (0.5mm 24p) | 原厂系列 PDF (RS 在线) <https://docs.rs-online.com/a372/0900766b80fd1ead.pdf> (403 = 拦 curl, 浏览器可开) · 对比规格页 <https://www.jinftry.com/product-compare/FH12-24S-0-5SH-55-vs-XF2J-162412A> (403 = 拦 curl) | ★**0.5mm pitch / 24 位 / 翻盖锁 (Flip Lock) / 贴板 / 底部触点 / 高度 2.00mm / 适配 0.30mm 厚 FPC / 额定电压 50V** | ✔ 正好是我们 camera 侧要画的 24p 0.5mm | ★**中高**: 公开选型表 (FH12 系列 6~53 位全覆盖, 含 **FH12-20S-0.5SH** = display 侧 20p) + 规格对比页 | **未试** | ★**额定电流 / 弯折寿命: 未查** |
| FPC 连接器 | **HIROSE FH12-20S-0.5SH** (0.5mm 20p) | 同上 (RS 在线 FH12 系列 PDF 里实测有 `FH12-20S-0.5SH`) | 0.5mm / 20 位 / 翻盖式 | ✔ display 侧 20p | ★**中高** (同上) | **未试** | |
| FPC 排线 | **Radxa AC004 / AC005 / AC006 / AC008 / AC012 / AC013** | 公开产品/配件页 <https://www.radxa.com/products> (实测 200) (实测页面文字: AC004 15P 0.3mm↔15P 1.0mm 同面 / AC005 39P0.3↔15P1.0 / AC006 31P0.3↔31P0.3 反面 / AC008 31P0.3↔15P1.0 同面 / AC012 15P1.0↔40P0.5 反面 / AC013 39P0.3↔40P0.5 反面 / AC013N) | ★**FPC 型号 + 针数 + 间距 + 同面/反面 全公开** | ✔ 我们要的转接组合都在里面 (31P0.3↔15P1.0 = AC008; 15P1.0↔40P0.5 = AC012) | ★**高** (公开页面已列规格) | **未试** | ★**长度规格: 未查** (demo 要求 ≤60mm ⇒ 选型时必须确认长度) |

---

## 6. 电源

★**demo 需求**: 充电 IC / 保护 IC (整机阶段, demo 先 DNP) + **三条 sensor LDO 轨** + ★**ISS-152 要的"带 EN 的低噪声 LDO"**。

| 类别 | 候选名 | 公开在售渠道 (可点链接) | 关键规格 | ①能否满足 demo 硬指标 | ②数据来源是否充足 | **已试/未试** | 备注 |
|---|---|---|---|---|---|---|---|
| 电源 | **TI BQ25896** (充电) | 产品页 <https://www.ti.com/product/BQ25896> (实测 200) · datasheet <https://www.ti.com/lit/ds/symlink/bq25896.pdf> (实测 200) | 1-cell Li-ion 充电 + 电源路径管理 + NTC | ✔ (demo 先 DNP 占位) | ★**高**: 原厂产品页 + 数据手册公开 | **未试** | ★**demo 阶段不阻塞** |
| 电源 | **TI BQ2970** (电池保护) | 产品页 <https://www.ti.com/product/BQ2970> (实测 200) · datasheet <https://www.ti.com/lit/ds/symlink/bq2970.pdf> (实测 200) | 1-cell 保护 (过充/过放/短路) | ✔ | ★**高** | **未试** | |
| 电源 | ★★**TI TPS7A20 系列 (固定输出低噪声 LDO)** | 产品页 <https://www.ti.com/product/TPS7A20> (实测 200) · ★**datasheet** <https://www.ti.com/lit/ds/symlink/tps7a20.pdf> (实测 200, 本单已抓全文) | 300mA · 超低噪声 · 低 IQ · 高 PSRR · ★**实测确认有 EN 脚** (DSBGA/X2SON/SOT-23 都有; **EN 高有效, 内部 500kΩ 下拉, 默认关断**) · 档位实测: **TPS7A2012 (1.2V) / -18 / -28 / -30 / -33 / -29 / -09 / -50 …** | ✔ sensor 三条轨用得到 (1.1/1.8/2.9V 档) | ★**高**: 原厂 datasheet 实读 | **已试** (datasheet 实读, 但**未上手**) | ★★★**重大修正 —— 推翻项目里的一条说法**: 项目内 (ISS-152 描述 + `HW/IMX415_DEMO_SENSOR_FACTS.md` §1.3) 写 **"TPS7A20 是固定输出无 EN"** ⇒ ★**实测 datasheet: TPS7A20 有 EN 脚** (Pin Functions 表: DSBGA B1 = EN; X2SON/SOT-23 第 3 脚 = EN; 另有 500kΩ 内部下拉 + VEN(LO/HI) 阈值) ⇒ ★**ISS-152 的对策①"给 AVDD 那颗加 EN + RC 延时"** 用**同一颗 TPS7A20 就能做, 不必换 LDO 家族** ⇒ **换料不换板保住**。⚠️ **但**: **2.9V 档只有 TPS7A2029 (X2SON DQN / DSBGA YCK 封装), SOT-23-5 (DBV) 没有 2.9V 档** (实测 orderable addendum: DBV 只有 -12/-18/-28/-30/-33) ⇒ ★**AVDD 若要 2.9V typ ⇒ 封装要从 DBV 换成 DQN/YCK ⇒ 焊盘会改** ⇒ ★**2.9V 这条不是"换料不换板"**, 要么留在 2.8V (落 AVDD1 Min 边界), 要么改封装 |
| 电源 | ★**TI TPS7A54** (可调 + PG) | 产品页 <https://www.ti.com/product/TPS7A54> (实测 200) · datasheet <https://www.ti.com/lit/ds/symlink/tps7a54.pdf> (实测 200) | 0.8~5.15V 可调 / 4A / **PG (上电顺序指示)** / SOT-23-6 | ✔ AVDD 想拿 2.9V typ ⇒ 用可调版**一次解决** | ★**高** | **未试** | ★**项目里已作为"备选未画入 BOM"记过** (`HW/SCHEMATIC_V1_1_CHANGELOG.md` C6) ⇒ ★**它同时解 ISS-152 的顺序问题 (PG) 和 2.9V 档问题**, ★**代价: 封装不同 + 4A 对 demo 过剩, 但 BOM 里本来就是 DNP/选型阶段** |

### 6.1 ★★ 补充实测: TPS7A20 各电压档的**封装可得性** (这决定"换档会不会改焊盘")

★**实测方法**: 读 TI datasheet (SBVS338H) 的 orderable addendum 表, 逐档看有哪些封装。

| 需要的电压 | TPS7A20 档位 | **实测可得封装** | ★**焊盘会不会改** |
|---|---|---|---|
| 3.3V (LOGIC) | TPS7A2033 | **DBV (SOT-23-5) ✔** / DQN (X2SON) / YCJ / YCK | 不改 (只要现 BOM 用 DBV) |
| 2.8V (AVDD 现状) | TPS7A2028 | **DBV ✔** / DQN / YCJ / YCK | 不改 |
| ★**2.9V (AVDD typ)** | TPS7A2029 | ★**只有 DQN (X2SON-4) 与 YCK (DSBGA-4) —— 没有 DBV (SOT-23-5)** | ★★**改 (SOT-23-5 → X2SON/DSBGA, 焊盘完全不同)** ⇒ **不是"换料不换板"** |
| 1.8V (OVDD / IO) | TPS7A2018 | **DBV ✔** / DQN / YCJ / YCK | 不改 |
| 1.2V (DVDD 现状) | TPS7A2012 | **DBV ✔** / DQN / YCJ / YCK | 不改 |
| ★**1.1V (DVDD typ)** | TPS7A2011 | ★**只有 DQN (X2SON-4) 与 YCK (DSBGA-4) —— 没有 DBV** | ★★**改焊盘** |

★★**由此得到一条比"改电压"更省事的结论 (直接改 `HW/IMX415_DEMO_SENSOR_FACTS.md` §1.2)**:
- ★**DVDD (数字轨): 不必改到 1.1V** —— IMX415 的 DVDD1 适用范围是 **1.00~1.20 V**, ★**现状 TPS7A20-12 的 1.2 V 就落在范围内 (上限)** ⇒ ★**保持 1.2V / TPS7A20-12 即可, 焊盘不动, 只有"最大电流 50mA → 250mA"这行规格文字要改 (TPS7A20 本体 300mA 够用)** ⇒ ★**省掉一次换档 + 换封装**。★**只有当 1.2V 顶到上限带来裕量不足时**, 才需要 1.1V ⇒ ★**但 1.1V 档没有 SOT-23-5 ⇒ 那时必须换封装 (SOT-23-5 → X2SON-4) ⇒ 这是"改板"级动作, 要单独立项**。
- ★**AVDD (模拟轨): 2.9V typ 同样没有 DBV** ⇒ ★**要 2.9V 就必须换封装 (或改用 TPS7A54 可调 + PG, 顺带解 ISS-152 的顺序问题)** ⇒ ★**建议: demo 阶段保留 2.8V (落在 AVDD1 Min 边界 2.80V), 整机阶段再评 2.9V / TPS7A54**。
- ★**当前 BOM 封装列全是"待定"** (`HW/BOM_v1.csv` footprint/opn 两列 = 待定) ⇒ ★**所以现在定封装还来得及, 一旦画板焊盘定型, 上面两条"改档"就都变成"改板"** ⇒ ★**建议在 BOM 里把 TPS7A20 的封装明确写成 DBV (SOT-23-5)**, 以便日后需要 EN/RC 延时或换可调 LDO 时还有余地 (注: ★**EN 脚在所有封装上都有**, 见 §6 TPS7A20 行)。

### 6.2 ★★★ 实测查到的**投板后才会炸**的一类问题: TPS7A20 的 EN 脚悬空 ⇒ **LDO 直接关断**

★**这是本单查电源时顺带挖出来的 P0, 必读** (与「已试/未试」无关, 是**画板硬约束**):

| 项 | 实测内容 | 出处 |
|---|---|---|
| 事实 1 | TPS7A20 **有 EN 脚**, 高有效; **EN 内部有 500kΩ 下拉**, datasheet 原文: **"keeps the LDO disabled even when the EN pin is left floating"** ⇒ ★**EN 悬空 = LDO 关断 (输出 0V)** | TI SBVS338H (2024-07 版) §6.3 / §7 应用信息, 实读全文 |
| 事实 2 | 阈值实测: **VEN(LOW) ≤ 0.3 V ⇒ 关断; VEN(HI) ≥ 0.9 V ⇒ 使能** (VIN = 1.6~6.0V 条件下) | 同上, 电气特性表 |
| 事实 3 | ★**EN 在所有封装上都是真脚**: DSBGA-4 = B1 · X2SON-4 (DQN) = 第 3 脚 · **SOT-23-5 (DBV) = 第 3 脚 (第 4 脚 N/C)** | 同上, Pin Functions 表 + 引脚图 |
| ★**事实 4 (本项目现状)** | ★**`HW/SCHEMATIC_V1_SPEC.json` 与 `HW/SCHEMATIC_V1.md` 的 7 路 LDO 连接行里, 没有任何 EN 网络** —— 只有 `RAIL_SYS → IN` 与 `OUT → rail` 两端 ⇒ ★**EN 脚的接法在网表里【未定义】** | 实查 SPEC json (`connections[]` C-06~C-10 等) 与 SCHEMATIC_V1.md 电源页连接表 |

★★**为什么这是 P0 (而不是「建议优化」)**:
- ★**投板后板子直接不启动** —— 7 路 LDO 全部输出 0V ⇒ SoC 无电 / sensor 无电 / 光机无电 ⇒ **开机就没反应**, 而这种故障在 **EVT 上要重新投板** (老板的账: 2-4 周 + ¥4-8K/批)。
- ★**它比「上电顺序」严重一个量级**: ISS-152 讨论的是「顺序不保证」(demo 能跑, 量产要闭环); 而 EN 悬空是 **「顺序都谈不上, 压根不输出」** ⇒ ★**ISS-152 的对策①"给 AVDD 那颗加 EN + RC 延时"如果只加在 AVDD 一颗上, 其余 6 颗仍全部关断** ⇒ ★**EN 的处理必须是全表 7 颗一起定, 不能只补一颗**。
- ★**"现在改网表成本 ≈ 0"**: BOM 的 footprint / opn 两列现在全是"待定" ⇒ **现在定封装 + 现在写 EN 接法, 焊盘一次到位**; 一旦焊盘定型, 后面想补 EN 就要加走线/改板。

★★**可执行约束 (直接抄进原理图, 不许放行前不填)**:

| LDO | EN 接法 | 目的 |
|---|---|---|
| `U_LDO_S28` (SENSOR_AVDD 2.8V) | **EN = RAIL_SYS (直连 IN) + RC 延时到 AVDD** (R+C 从 SYS 下来) ⇒ ★**最后上电** | 满足 IMX415 上电序 **DVDD → OVDD → AVDD** (200ms 内) |
| `U_LDO_S18B` (SENSOR_VDD_IO 1.8V) | **EN = RAIL_SYS + RC 延时 (第二级)** | 上电序第 2 级 |
| `U_LDO_S12` (SENSOR_CORE 1.2V) | **EN = RAIL_SYS (直连 IN, 无延时)** | 上电序第 1 级 |
| 其余 4 颗 (`U_LDO_L33` / `U_LDO_L18` DNP / `U_LDO_IO33` / `U_LDO_IO18`) | ★**EN 必须显式接到 IN 或经 10k 上拉** (不可 NC) | **防“悬空 = 关断”** |

★**RC 延时取值**: EN 阈值 0.9V (VEN(HI)) ⇒ R×C 定 RC 充电到 0.9V 的时间; ★**具体 R/C 值本单未算** ⇒ **标 [待核], 需按 datasheet 6.3 的使能时序 + IMX415 200ms 总窗口反推**。

★**同时纠正项目内一处错误说法 (必须改)**: 项目内 (ISS-152 描述 + `HW/IMX415_DEMO_SENSOR_FACTS.md` §1.3) 写 **"TPS7A20 是固定输出无 EN"** ⇒ ★**实测: TPS7A20 有 EN 脚 (高有效 + 500kΩ 内部下拉)** ⇒ ★**结论反转: 不用换 LDO 家族就能拿到 EN ⇒ ISS-152 的对策①成本从「换料」降到「改网表」**。

---

## 7. 调试与接口

| 类别 | 候选名 | 公开在售渠道 (可点链接) | 关键规格 | ①能否满足 demo 硬指标 | ②数据来源是否充足 | **已试/未试** | 备注 |
|---|---|---|---|---|---|---|---|
| 调试/接口 | **USB-UART: Adafruit USB to TTL 串口线 (PL2303/CP2102 版)** | <https://www.adafruit.com/product/954> (实测 200) | USB-A 转 4 线 (TX/RX/GND/VCC) · 3.3V/5.0V 档 | ✔ RK3572 调试口 | ★**高**: 公开产品页 + 页内附 PL2303HX.D / PL2303TA / CP210X 资料链接 | **未试** | |
| 调试/接口 | **CH340 USB-UART 模块** | ★**CH340 官方 datasheet (SparkFun 镜像)** <https://cdn.sparkfun.com/datasheets/Dev/Arduino/Other/CH340DS1.PDF> (实测 200) · 模块在售页 (Amazon Maikrt) <https://www.amazon.com/Adapter-Module-Converter-Development-Projects%EF%BC%88Golden%EF%BC%89/dp/B07DYS8HKS> | CH340G/C · 6 脚 (VCC/3V3/TXD/RXD/GND) · 内置晶振与否 | ✔ | ★**高** (官方 datasheet) | **未试** | ★**若自焊到主板, 选 CH340 方案要额外处理 3.3V/5V 跳线** |
| 调试/接口 | **JTAG: SEGGER J-Link** | <https://www.segger.com/products/debug-probes/j-link/> (实测 200) | ARM Cortex-A 调试/仿真 · ★**对 RK3572 的支持情况: 未查** | ⚠️ **未查** | ★**中**: 产品线公开, **RK3572 支持表: 未查** | **未试** | |
| 调试/接口 | **Raspberry Pi Debug Probe** (CMSIS-DAP + USB-UART 二合一) | <https://www.raspberrypi.com/products/debug-probe/> (403 = 拦 curl, 浏览器可开) · 文档 <https://www.raspberrypi.com/documentation/microcontrollers/debug-probe.html> (403 同上) · ★**Adafruit 同款在售** <https://www.adafruit.com/product/4755> (实测 200) | CMSIS-DAP (SWD) + USB 串口 · ★**一把顶两把 (调试 + console)** | ✔ (SWD 走 Cortex-A 调试口) | ★**中高** | **未试** | ★**demo 阶段最省事**: 一根线同时给 SWD 与 UART console ⇒ **建议做成"调试与接口"类的首选** |

---

## 8. ★ "已试 / 未试" 汇总 (L3 凭证的核心)

★**判定口径 (写清楚, 免得歧义)**:
- **已试** = 该候选的关键结论**已在本项目落账并可复算** (公开 datasheet / 内核源码 / 脚本打分实测)
- **部分已试** = 只有一部分结论落账 (其余 = 未查)
- **未试** = 本单首次进清单, **仅公开页面/源码核查, 未上手、未采购**

| 类别 | 已试 | 部分已试 | 未试 |
|---|---|---|---|
| 1 主控载体 | — | — | OK3572-C / FET3572-C · ArmSoM CM5 · DFRobot DFR1218 · BPI-CM5 Pro · Luckfox Core3576 (共 5 个) |
| 2 camera 模组 | — | — | Radxa Camera 4K · Radxa Camera 8M 219 · Arducam IMX415 B0569 · Arducam OV9281 B0452 · Waveshare IMX219 · DFRobot 套件 IMX415 (共 6 个) |
| 3 屏幕模组 | — | — | Waveshare 4.3" DSI · Waveshare 2.8" DSI · Radxa Display 5/8HD/10FHD · Forlinx 7" MIPI · RPi 7" TC358762 (共 5 个) |
| 4 sensor 裸件 | ★**IMX415 (10/10)** ★**AR0234CS (3/10)** | AR0521 (8/10, 只打分) · OV04C10 (0/10, 只打分) | — |
| 5 FPC 连接器/排线 | — | — | FH35C-31S-0.3SHW(50) · FPC1030-15S-TAG · FH12-24S-0.5SH · FH12-20S-0.5SH · Radxa AC004/005/006/008/012/013 (共 5 组) |
| 6 电源 | ★**TPS7A20 系列 (datasheet 实读, 且推翻项目内两条说法: ①"无 EN" ②"要换 LDO 家族")** · ★**P0: EN 悬空=全表关断** | — | BQ25896 · BQ2970 · TPS7A54 (共 3 个) |
| 7 调试与接口 | — | — | Adafruit USB-TTL · CH340 模块 · SEGGER J-Link · RPi Debug Probe (共 4 个) |

★**★ L3 判据自评 (老板要的可核查性)**: **全库零采购记录** (`grep -rnE "已购|已下单|已到手" --include=*.md .` 无命中) ⇒ ★**"所有元件都试过了" 这个条件目前【不成立】, 连物料都还没开始上手** ⇒ ★**L4 (走采购方案咨询厂家) 现在不该触发; 本单只是把 L1/L2 的成果固化成可核查清单**。

---

## 9. ★★ 本单给 boss 的 5 条可执行结论 (可落成约束)

| # | 结论 | 依据 (实测) | 落成动作 |
|---|---|---|---|
| **C1** | ★★**面板 init code 不必问厂家** —— 路径是"Rockchip BSP 内核自带 panel 驱动 + 公开 dts 范例", 不是"问人" | `drivers/gpu/drm/panel/panel-sitronix-st7701.c` (BSP+主线) 等 8 颗 IC 驱动实测; `rk3576-evb.dtsi` 内含 1080×1920/4-lane 的完整 init sequence | ★**选屏判据改成"内核驱动清单优先"**: ST7701 / ST7703 / ST7789V / ILI9881C / NV3052C / OTM8009A / HX8394 / RPi-touchscreen; ★**EK79007+EK73217+NV3049 从"白送"降级为"要自己抄 dts"** |
| **C2** | ★★**TPS7A20 有 EN 脚** ⇒ ISS-152 的上电顺序对策**不必换 LDO 家族**, 同型号加 EN+RC 延时即可; ★**且 2.9V / 1.1V 档没有 SOT-23-5 封装** ⇒ 想要 2.9V 就得改焊盘 ⇒ **DVDD 建议保持 1.2V 不动** | TI datasheet 实读: (a) Pin Functions 表 (DSBGA B1 / X2SON+SOT23 第 3 脚 = EN, 高有效, 内部 500kΩ 下拉) ⇒ 项目内 "TPS7A20 无 EN" 的说法**是错的**; (b) orderable addendum: **TPS7A2029 / TPS7A2011 只有 DQN (X2SON-4) 与 YCK (DSBGA-4), 没有 DBV (SOT-23-5)** | ★**ISS-152 描述与 `HW/IMX415_DEMO_SENSOR_FACTS.md` §1.3 需改** (三轨同起 ⇒ 加 EN 脚 + RC 延时即可保顺序); ★**§1.2 的 "DVDD 改 1.1V" 建议撤回** (1.2V 就在 DVDD1 1.00~1.20V 范围内 ⇒ 不动焊盘, 只改电流规格文字); ★**BOM footprint/opn 列现全是"待定" ⇒ 现在定封装 (建议 DBV) 还来得及, 画板焊盘定型后换档=改板** |
| **C3** | ★**公开现货 camera 模组的 FPC 规格与我们自画的 0.5mm 24p 对不上** (现货是 31p/0.3mm 或 RPi 15p/1.0mm / 22p/0.5mm) | Radxa ROCK4D 接口页 + Arducam 针位页 实测 | ★**主板 FPC 座二选一**: (a) **改成 RPi 15p/22p 标准** (针位表公网公开, 照抄最省) (b) 保留 24p 但**采购硬判据里写死"模组 FPC 规格 + 是否配转接排线"** ⇒ **这条必须在画板前定, 否则投板后是 2-4 周返工** |
| ★★**C3-bis (ISS-158 实测闭环)** | ★★**C3 已闭环: 主板两个 FPC 座规格定死 = camera 31p/0.3mm + display 40p/0.5mm, 逐针表全部拿到, 不用转接排线, 不用自造 24p** | ★**实测**: Radxa 官方文档 camera-4k 页 (31 针引脚定义表) + lcd-8-hd 页 (40 针 Pinout 表) + ROCK4D 页 (载板侧 31p 针序交叉验证) | ★**主板照 `HW/STEP1_PARTS_SPEC.md` §2.1 / §3.1 的两张表画座** ⇒ ★**C3 从"二选一待定"变成"已定"** |
| **C4** | ★**屏的分辨率是 demo 真瓶颈, 但不妨碍跑链路** —— 公开现货 MIPI-DSI 一体屏最高只到 1200×1920 (Radxa 10 FHD) / 800×1280 (8 HD), **"1920×1080 视涯 SiOLED"在公开现货里无对标品** | Radxa / Waveshare 产品页实测 | ★**demo 用 8 HD 或 10 FHD 验完 DSI 通路** (两者 dts 都在 radxa-overlays 公开仓库); ★**视涯那块屏单列为独立风险项**, 走 L1 公开渠道找, 找不到才谈 L2 |

| **C5** | ★★★**P0: TPS7A20 的 EN 脚悬空 ⇒ 7 路 LDO 全部关断 ⇒ 投板后板子不启动** | TI SBVS338H 实读: "keeps the LDO disabled even when the EN pin is left floating" + 内部 500kΩ 下拉 + VEN(LOW)≤0.3V / VEN(HI)≥0.9V; ★**本项目 7 路 LDO 的网表行里没有任何 EN 网络** (实查 `SCHEMATIC_V1_SPEC.json` connections C-06~C-10 与 `SCHEMATIC_V1.md` 电源页) | ★**画板前必须落**: 7 颗 EN **全部**显式接法 (S28 = IN + RC 延时 / S18B = IN + RC 延时 / S12 = IN 直连 / 其余 4 颗 = IN 直连或 10k 上拉, **不许 NC**) ⇒ ★**顺带解掉 ISS-152 的上电顺序** (DVDD→OVDD→AVDD 靠 EN 的 RC 延时链) ⇒ ★**现在 BOM footprint/opn 全是"待定" ⇒ 改网表成本 ≈ 0, 焊盘定型后就变成改板** |
| ★★**C6 (ISS-158 实测新增)** | ★★**"驱动 IC 须在 Rockchip 内核白名单" 这条判据有前提 —— 它只管【专用 panel driver】; 走 `simple-panel-dsi` 的屏不依赖任何专用驱动, 这条判据自动不成立** ⇒ ★**P2 首选 `simple-panel-dsi` 路线 (Radxa 10 FHD), 而非死磕某颗 IC 型号** | ★**实测**: `radxa-cm5-io-radxa-display-10fhd.dts` 用 `compatible = "simple-panel-dsi"` + init sequence + 完整 display-timings; ★**内核 79 个 panel 文件实测清单里有 `panel-simple.c` 但没有 `panel-radxa-*`** ⇒ 8HD (`radxa,display-8hd`) 的驱动在 Radxa 私有内核 ⇒ **8HD 降级为备选** | ★**选屏硬判据改成两条**: ① 走 `simple-panel-dsi` (不依赖专用驱动) ② ★**"能找到用同一块屏的公开 dts"** (init code 来源) |
| ★★**C7 (ISS-158 实测新增)** | ★★**主板电源树要改两处: ① 屏背光是 12V 级 ⇒ 须单独 BOOST (typ 12.8V / max 14V / 200mA typ) ② camera 模组级只要 3.3V + 5V ⇒ sensor 三条 LDO (1.1/1.8/2.9V) 可能整个不需要** | ★**实测**: Radxa Display 10 FHD 官方文档背光表; ★**Radxa Camera 4K 官方文档 31 针表 (针 28-29 = VCC3.3V, 针 30-31 = VCC5V)** | ★**画板前定**: 按"模组自带 LDO"画电源树 (省 3 颗 LDO + 面积) ★**但 BOM 必留 3 条 sensor 轨的 DNP 焊盘做退路** (模组内部供电架构 = 未查实, 属[推断, 待核]) |


---

## 10. ★★ ISS-158 补充 (2026-11-02 23:10) —— 三件外购件的"针位表/引脚定义/尺寸"已补

★**本节只补三类料的关键规格列** (针位表 / 引脚定义 / 尺寸) ⇒ ★**完整规格汇总在 `HW/STEP1_PARTS_SPEC.md`** (主板照它画) ⇒ ★**本节与那份文件不重复, 只做索引**。

| 类 | 件 | ★**针位表/引脚定义 (实测)** | ★**尺寸/机械 (实测)** | ★**主板要画的** |
|---|---|---|---|---|
| **P1 camera 模组** | **Radxa Camera 4K** (IMX415) | ★**模组侧 31 针表 (31/31 全拿到)** <https://docs.radxa.com/accessories/camera/camera-4k> (实测 200) + ★**载板侧 31 针针序 (第二来源交叉验证)** <https://docs.radxa.com/en/rock4/rock4d/hardware-use/mipi-csi> (实测 200) ⇒ ★**两表针 24/25=I2C, 27=RESET, 28-29=3V3, 30-31=5V 逐针一致** | ★**连接器 FH35C-31S-0.3SHW(50): 10.9×4.2×0.9mm** (HIROSE 原厂页实测 200) · 模组尺寸图公开 (官方文档"物理规格"节) · 排线默认 150mm | ★**31p / 0.3mm 翻盖式贴板座**, 针序照 `STEP1_PARTS_SPEC.md` §2.1 |
| **P2 屏模组** | **Radxa Display 8 HD** / **10 FHD** | ★**屏侧 40 针表 (40/40 全拿到)** <https://docs.radxa.com/accessories/display/lcd-8-hd/lcd-8-hd-product> (实测 200) + <https://docs.radxa.com/accessories/display/lcd-10-fhd/lcd-10-fhd-product> (实测 200) | ★**8 HD 有效区 107.64×172.224mm** (外形尺寸 = 未查, 官方只给图) · ★**10 FHD 有效区 135.36×216.58mm / 外形 155×246.16×5.95mm** | ★**40p / 0.5mm 翻盖式贴板座**, 针序照 `STEP1_PARTS_SPEC.md` §3.1; ★**主板侧排线走 39P0.3mm 或 15P1.0mm 原厂件** |
| **P3 RK3572 核心板 (SOM)** | **Forlinx FET3572-C** | ★**逐针引脚定义表 = 未查** (下载中心需注册登录, ★**属公开下载非 L4**) · ★**PDF 明写与 FET3576-C 引脚兼容 ⇒ 拿 FET3576-C 的表即可** | ★**68 × 50 mm** · ★**4 × 100Pin / 0.4mm pitch / 1.5mm 配合高度 板对板连接器** ⇒ ★**主板要画 4 个 BTB = 400 焊盘** · ★**机械尺寸图 (连接器 footprint) = 未查** | ★**等引脚定义表 + 机械图到手再定 footprint; 在此之前不得开跑线** |

★**P3 的一个必须记住的落差**: ★**老板说的"推荐焊接 (省连接器、成本低、可靠)" 对 FET3572-C 不成立** —— ★**它是 4×100pin 板对板连接器式 SOM, 不是焊死式** ⇒ ★**主板要承担 400 个触点的连接器焊盘** ⇒ ★**这恰恰让"引脚定义表"从"nice to have"变成"画板硬前提"**。

★**证据等级**: 内核源码路径 / 目录清单 / dts 原文 / TI datasheet 字段 / 公开产品页规格 = **[实测]** · 公开在售但本单未抓细节 (针数、长度、价格、库存) = **[未查]**, 已在表内逐格标注 · 推断 (如 2.8" 屏可能是 ST7701) = **[推断, 不可当结论]**。

★**复算命令**:
```bash
cd projects/smart_glasses
python3 HW/open_source_rank.py          # 第 4 类 D1~D5 (本单未重测, 直接复用)
# 本单所有链接的 HTTP 状态均已实测, 403 = 站点对 curl 的 Cloudflare 拦截 (浏览器可开)
```
