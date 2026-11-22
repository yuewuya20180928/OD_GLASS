# HW/IMX415_DEMO_SENSOR_FACTS.md —— demo sensor 改 IMX415 的四问 (硬件数据)

| 项 | 内容 |
|---|---|
| 作者 | **hw-lead (硬件总工)** |
| 日期 | **2026-11-02 19:40** |
| 触发 | 老板 **2026-11-02 19:29** 指示: "当前demo不考虑功耗, sensor你只要考虑sensor能够输出1920*1080@60fps的规格就行…**sensor选型你考虑的太多了, 只考虑规格和数据(硬件数据、软件配置数据)来源是否充足就行**" ⇒ demo sensor 定 **IMX415** (AR0234CS 保留给整机方案) |
| 本单范围 | **只出事实, 不改网表** (改网表是 ISS-150 的活) · **全部公开来源, 不联系厂家 / 不发问询函 / 不发帖** |
| 证据等级 | `[官方]` = 厂商公开 datasheet / flyer · `[实测]` = 本次实际下载解析的文件 · `[推算]` = 由 datasheet 数值算得 · `[待核]` = 公开来源未覆盖 |
| 硬约束 | 不发邮件 / 不联系代理 / 不在社区发帖问厂家 · 只写本文 + `HW/AR0234CS_OPEN_SOURCE_FACTS.md` + `state/fragments/hw.yaml` |

---

## 0. 一句话结论 (4 条, 先看这个)

| # | 结论 | 等级 |
|---|---|---|
| **①** | ★★**IMX415 只要 3 条轨, 和网表现有的 3 条 sensor 轨一一对应 —— 但电压全要改**: `dvdd` **1.1V**(网表现 1.2V) · `dovdd` **1.8V**(网表现 2.8V ★**2.8V 会直接烧 sensor**) · `avdd` **2.9V**(网表现 2.8V)。**轨数不变 ⇒ 只改电压设定值, 不加不减 LDO** ⇒ "换料不换板" 成立 | `[官方]+[推算]` |
| **②** | ★★**1080p60 走 sensor 侧 2/2 行 binning (不是 crop) ⇒ 不影响 FOV, 不违反老板 10-25「禁止 ROI/crop」**。**Rockchip BSP `imx415.c` 已经带这个模式** (`1944×1097`, 寄存器 `0x3020=0x01`), 但**出厂配的是 30fps** ⇒ **60fps 只需改 VMAX 一个数 (0x0C5D→0x062E)**, 是"改一行"不是"移植驱动" | `[实测]+[推算]` |
| **③** | ★★**现成 IQ 不能直接用在 1080p60**: IQ 文件里 `sensor_calib.resolution` 明写 **3840×2160**, 且 rkaiq 仓库里 IMX415 的 **mesh (LSC 网格) 文件名也锁死 3840×2160** ⇒ 1080p 档缺 mesh。⇒ **demo 唯一要做的 tuning = 补一套 1920×1080 的 mesh + AE 曝光表换算**, 工作量 **1~2 人日 (需暗室/灰卡)**, **不是 1~2 人周** (AR0234CS 那条才是人周级) | `[实测]` |
| **④** | ★★**模组采购硬判据 (见 §4)**: **必须 4-lane** (★RK BSP 驱动**只在 4-lane 表里**有 binning 模式, 2-lane 表里没有 ⇒ 只接 2 lane 驱动根本不给你 1080p 模式) · **必须带镜头+IR-cut** · **必须确认 AC 耦合电容在不在模组上** · **I2C 7-bit 地址 0x1a** | `[实测]+[官方]` |

---

## 1. ① 电源域 (公开 datasheet) ⇒ 直接决定网表那三条轨怎么改

### 1.1 三条轨的电压/电流 (官方)

| 轨 (RK BSP 驱动里的 regulator 名) | datasheet 名 | Min | **Typ** | Max | 电流 Typ | 电流 Max | 绝对最大额定值 |
|---|---|---|---|---|---|---|---|
| `dvdd` (Digital core) | **DVDD1** | 1.00 V | **1.10 V** | 1.20 V | IDVDD **187 mA** | **250 mA** | **-0.3 ~ 2.0 V** |
| `dovdd` (Digital I/O) | **OVDD** | 1.70 V | **1.80 V** | 1.90 V | IOVDD **3 mA** | **3 mA** | **-0.3 ~ 3.3 V** |
| `avdd` (Analog) | **AVDD1** | 2.80 V | **2.90 V** | 3.00 V | IAVDD **128 mA** | **156 mA** | **-0.3 ~ 3.3 V** |

- 电流测试条件 `[官方]`: MIPI CSI-2 / **4 Lane, 2079 Mbps, 12 bit, 60 frame/s, All-pixel mode**。
- 电源轨**上电顺序** `[官方]`: **DVDD(1.1V) → OVDD(1.8V) → AVDD(2.9V)**, 三条轨必须在 **200 ms 内**全部上升到位。
- `Topr` -30 ~ +85 °C, `Tspec` -10 ~ +60 °C。
- **输入电压绝对最大: `VI` = -0.3 ~ (OVDD + 0.3) V, 且不超过 3.3 V** ⇒ ★**I2C 上拉 3.3V 合法 (VIH max = 1.9V < 3.0V < 3.3V)** —— 这一点跟 AR0234CS 相反, 见 §1.4。

### 1.2 ★ 对照现网表 (三条轨全要改电压, 轨数不变)

| 网表轨 (`HW/netlist_v1.csv` L89~L109) | 现在 (按 AR0234CS 写的) | ★**IMX415 应改为** | 差 | 后果 |
|---|---|---|---|---|
| `SENSOR_CORE` (U_LDO_S12, TPS7A20-12) | **1.2 V / 50 mA** | **1.1 V / 250 mA** | 电压 1.2→1.1 ✔ 在 DVDD1 范围内 | ✔ 改档即可 (TPS7A20 家族固定档覆盖 0.8~5.5V) |
| `SENSOR_VDD_IO` (U_LDO_S28B, TPS7A20-28) | **2.8 V / 30 mA** | **1.8 V / 3 mA** | ★★**2.8 V ≫ OVDD Max 1.90 V** | ★★★**不改 = 直接烧 sensor**(绝对最大也只有 3.3V, 长期 2.8V 工作直接超规格) ⇒ **必须改 1.8V** |
| `SENSOR_AVDD` (U_LDO_S28, TPS7A20-28) | **2.8 V / 30 mA** | **2.9 V / 156 mA** | 2.8V 在 AVDD1 Min(2.80) 边界上, Typ 是 2.9 | 电压改 2.9V; ★**电流额定 30mA ≪ 156mA ⇒ 规格文字要改** (TPS7A20 本体 300mA 够用, 只是 `netlist_v1.csv` 里写的"最大电流"数字是按 AR0234CS 的 30mA 填的) |

★**结论**: **轨数 3 条不变、LDO 型号 (TPS7A20) 不变、封装不变** ⇒ ★**改三颗 LDO 的输出电压设定 + 改三处规格文字的电流值** ⇒ **不用改板、不用加 LDO、不用删 LDO**。这是"换料不换板"的经典情形。
★ **[待核]**: TPS7A20 的**固定档位表**里是否有 **1.1V / 1.8V / 2.9V** 这三个点 (家族覆盖 0.8~5.5V 共 30 档, 需逐档核; 若 2.9V 缺档, 换 TPS7A20 家族同封装的邻近档或改用可调版)。**核不过 = 换料, 但因封装全档共用 X2SON ⇒ 仍不换板**。

### 1.3 ★ 上电顺序约束 (新增, 现网表没管)

- datasheet 要求 **DVDD(1.1V) 先, 再 OVDD(1.8V), 最后 AVDD(2.9V)**, 200 ms 内完成。
- ★**现网表三条 LDO 全部同时接 `RAIL_SYS`、无使能脚** ⇒ **上电顺序不确定** ⇒ 三条轨一起爬升时, 若 AVDD 先到 2.9V 而 DVDD 还是 0V, 违反 datasheet 顺序。
- ★**最低成本对策 (二选一, 都只动网表)**: ①给 AVDD 那颗 LDO 加 **EN 脚 + RC 延时** (或换成带 EN 的档), 让 AVDD 最后上电; ②在驱动侧用 `regulator_bulk_enable` 之外的顺序 + 延时 (驱动已经要求 "power raising → XCLR ≥500 ns"、"XCLR → clk ≥1 µs"、"XCLR → I2C ≥20 µs", 但**这管不到三条轨之间的顺序**)。
- **[待核]** onsemi/Sony 对"三轨乱序"的实际耐受度 (datasheet 只给了推荐顺序, 没给乱序惩罚) ⇒ **保守按"必须顺序上电"设计**。

### 1.4 ★ I2C 上拉电平 (本条与 AR0234CS 相反, 别照抄)

- IMX415 的 I2C (SCL/SDA) 挂在 **OVDD (1.8V) 域**。
- **[官方] DC 特性**: `VIH` min = 0.7 × OVDD = **1.26 V**, `VIH` **max = 1.9 V**; `VIL` max = 0.3 × OVDD = **0.54 V**; `IOL` 3 mA。
- ⇒ ★★**I2C_A 上拉可以保持 3.3V** (VIH max 1.9V < 3.0V < 绝对最大 3.3V) —— **TBD-05 对 IMX415 这一侧不成立为"必须改 2.8V"**, 但因为 OVDD 变成 1.8V, 上拉电阻两端电压升高 (3.3V 上拉, 高电平 3.3V, 低电平灌 3.3V-IOL, 而 IOL 只允许 3 mA) ⇒ ★**上拉阻值要重算** (3.3V 上拉时, 低电平电流 = (3.3 - VOL)/R, VOL max 0.4V(1.8V 域) ⇒ R ≥ (3.3-0.4)/3mA = **967 Ω** ⇒ 取 **1.0 kΩ~2.2 kΩ**)。
- ⇒ ★**建议: I2C_A 上拉改 1.8V 而不是 3.3V** —— 理由: ①同总线其它从设备 (TMP117 1.7~5.5V ✔ / 充电 IC / 光机) 的电平容差要一起核; ②1.8V 上拉时低电平灌流只有 1.4mA, 对 sensor 更温和; ③**统一成 1.8V 可以让"整条 I2C_A 是 1.8V 域"这件事在网表上一眼可见, 避免下次换 sensor 再踩坑**。
- **[待核]** I2C_A 上现有从设备清单与各自电平域 (TMP117 / 充电 IC / 光机 / 屏) —— **这是 ISS-150 改网表前的前置项**。

### 1.5 ★ 与 AR0234CS 的对照表 (两者绝对不能混用同一套轨)

| 项 | **IMX415** (demo) | **AR0234CS** (整机) |
|---|---|---|
| 轨数 | **3 条** (dvdd/dovdd/avdd) | **6+ 条** (见 `HW/AR0234CS_OPEN_SOURCE_FACTS.md` U4) |
| 核心电压 | 1.1 V | 1.2 V (VDD/VDD_PHY/VDD_DATA) |
| IO 电压 | **1.8 V** | **2.8 V** (VDD_IO) + **1.8 V** (VDDIO_PHY) |
| 模拟电压 | **2.9 V** | 2.8 V (VAA/VAA_PIX/VAA_PHY) |
| I2C 上拉 | 1.8 V (或 3.3V, 见 §1.4) | **2.8 V** (U2 结论) |
| ★**同一个 `SENSOR_VDD_IO` 轨** | **1.8 V** | **2.8 V** | ★★**两条路的 VDD_IO 差 1.0V ⇒ 换 sensor 时这条轨一定要跟着改, 且不能"两版板子共用一颗 LDO 输出"** |

---

## 2. ② 1080p60 怎么出 —— sensor 侧 binning, 不是 ISP 侧 crop

### 2.1 ★ 为什么 ISP 侧 crop 不行 (老板 10-25 那条禁令在这里长什么样)

| 路径 | ISP 进线数据量 | 判定 |
|---|---|---|
| 全分辨率 3840×2160 @60 | **497.7 MP/s** | ✘ 超本项目 ISP 250 MP/s 口径 (`HW/R_GEO_Q03_ISP_THROUGHPUT_ADJUDICATION.md` / `HW/e2e_budget_rk3572.py`) |
| 全分辨率 3840×2160 @30 | 248.9 MP/s | ✘ 帧率只有 30, 不满足 60fps 硬指标 |
| **ISP 侧 crop 3840×2160 → 1920×1080 @60** | **仍是 497.7 MP/s** | ✘✘ **crop 发生在 ISP 之后, 不减 ISP 进线带宽 ⇒ 这条路物理上不成立** |
| ★**sensor 侧 2/2 行 binning → 1920×1080 @60** | **124.4 MP/s** | ✔ **成立, 且余量 50%** |

⇒ ★★**结论: 必须让 sensor 自己少吐像素, 且只能是 binning (全阵列读出), 不能是 crop (只读中间一块)。**

### 2.2 ★ 官方口径: IMX415 本身就有 2/2 行 binning 模式, 而且是 1920×1080

`[官方]` Sony IMX415-AAQR Flyer:
- "Readout mode: **All-pixel scan mode** / **Horizontal/Vertical 2/2-line binning mode** / Window cropping mode"
- "Maximum frame rate: All pixel 3840(H)×2160(V) **90.9 fps (10 bit)** / **Horizontal/Vertical 2/2-line binning 1920(H)×1080(V) approx 2.07M pixels, 90.9 fps**, CSI-2 10bit"
- 有效像素 3864×2192, 推荐录像像素 3840×2160, 单元 1.45 µm × 1.45 µm。

⇒ ★**sensor 出 1920×1080 是官方一等公民模式, 不是 hack。** 且 **binning 读的是整个阵列 ⇒ 视场角不变** ⇒ **不触犯老板 10-25「禁止 ROI/crop 裁画面取景」**。

### 2.3 ★★ Rockchip BSP `imx415.c` 已经带这个模式 (实测, 零移植)

`[实测]` `https://raw.githubusercontent.com/rockchip-linux/kernel/develop-6.1/drivers/media/i2c/imx415.c`

| 位置 | 内容 | 意义 |
|---|---|---|
| L1085 `supported_modes[]` | 第 8 项: `.width=1944, .height=1097`, `.max_fps = {10000, 300000}` = **30 fps**, `.vts_def = 0x0c5d`, `.hts_def = 0x030e*3`, `.bpp=12`, `.mipi_freq_idx=0`, `.reg_list = imx415_linear_12bit_1932x1096_594M_regs` | ★**模式已在** |
| L690 `imx415_linear_12bit_1932x1096_594M_regs[]` | **`{0x3020,0x01}, {0x3021,0x01}, {0x3022,0x01}`** | ★★**对比全分辨率模式 L(12bit 3864x2192_891M) 是 `{0x3020,0x00},{0x3021,0x00},{0x3022,0x00}`** ⇒ **这就是 binning 寄存器 (0x3020=BINNING_MODE), 不是 crop** |
| 同上 | `0x3024/0x3025` = 0x5D/0x0C ⇒ **VMAX = 0x0C5D = 3165**; `0x3028/0x3029` = 0x0E/0x03 ⇒ **HMAX = 0x030E = 782** | ★**帧长/行长寄存器** |
| L2800 `imx415_get_selection()` | `CROP_START(SRC,DST) = ((SRC-DST)/2/4*4)`; 当 `cur_mode->width==1944` ⇒ `left=12, width=1920, top=8, height=1080` | ★**驱动自己把 1944×1097 裁到 1920×1080 (边沿对齐修正, 不是取中心 ⇒ FOV 不变)** |
| L1516 / L3089 | `vblank_def = mode->vts_def - mode->height`; `vblank_min = (mode->height + 46) - mode->height` | ★**帧长是 runtime 可控的 vblank 控件, 改帧率有正规入口** |
| L179-183 | `imx415_supply_names[] = {"dvdd","dovdd","avdd"}` | ★**驱动只认 3 条轨 ⇒ 与 §1.1 的 datasheet 三条轨一一对应** |
| L3218 | `if (num_data_lanes == IMX415_4LANES) supported_modes = supported_modes; else supported_modes = supported_modes_2lane;` | ★★**2-lane 表里只有 3864×2192@15fps 和 1284×720@90fps, 没有 binning 模式 ⇒ 只接 2 lane 拿不到 1080p** |

### 2.4 ★★ 60fps 只需要改一个数 (帧长 VMAX), 实测算式

`[推算]` 1H 周期 = HMAX / 74.25 MHz (驱动 L1104 注释 "1H period = (1100 clock) = (1100 * 1 / 74.25MHz)"; 该模式 HMAX = 782 ⇒ 1H = 782/74.25e6 = **10.5386 µs**)

| | 当前 (30 fps) | 改为 60 fps |
|---|---|---|
| HMAX | 782 (0x030E) | 782 (不变) |
| **VMAX** | **3165 (0x0C5D)** | **1582 (0x062E)** |
| 帧时间 | 3165 × 10.5386 µs = **33.354 ms ⇒ 29.98 fps** | 1582 × 10.5386 µs = **16.672 ms ⇒ 59.98 fps** ✔ |
| sensor 上限校核 | binning 模式官方上限 **90.9 fps** ⇒ 60fps 需 VMAX ≥ 3165×29.98/90.9 = 1044 | **1582 ≫ 1044 ✔ 合法** |

⇒ ★★★**结论: 1080p60 = "切到驱动已有的 binning 模式 (1944×1097) + 把 VMAX 从 0x0C5D 改成 0x062E", 是一处寄存器/一行 `.vts_def` 的改动, 不是驱动移植。**
⇒ ★改动量估算: 驱动 **0.5 人日** (加一个 mode 项或改 vts_def + exp_def + vblank_min), DT **0.2 人日** (改 `imx415_get_selection` 已有的 1920×1080 裁剪 + mode 索引), rkaiq 注册 **0.2 人日** ⇒ **合计 ≈ 1 人日**, 对比 AR0234CS 路径的 **5.5 人日**。

### 2.5 ★ MIPI 带宽校核 (4-lane / 2-lane 都算一遍)

| 配置 | ISP 进线 | MIPI payload | 驱动给的 link freq | 判定 |
|---|---|---|---|---|
| ★**4-lane, binning 1920×1080@60, 12 bit** | 124.4 MP/s | 124.4 × 12 = **1.49 Gbps** | `mipi_freq_idx=0` ⇒ `MIPI_FREQ_297M` (= 594 Mbps/lane 数据率, 与 reg list 名 "**594M**" 吻合); 驱动 `pixel_rate = link_freq/bpp*2*lanes = 297e6/12*2*4 = 198 MP/s` | ✔ **198 > 124.4, 余量 59%** |
| 4-lane, 10 bit | 124.4 MP/s | 1.24 Gbps | 同上 → 237.6 MP/s | ✔ 余量 91% |
| 2-lane (若强行走) | 124.4 MP/s | 1.24~1.49 Gbps | 2 lane × 594 Mbps = **1188 Mbps** | ★**10bit 勉强够 / 12bit 不够**, 且 ★**驱动 2-lane 表根本没有 binning 模式** ⇒ **必须 4-lane** |
| (参考) 全分辨率 4-lane 3864×2192@30, 10 bit | 254 MP/s | 2.54 Gbps | `mipi_freq_idx=1` ⇒ 446M → 356.8 MP/s | ✔ 但帧率只有 30 |

⇒ ★★**采购硬判据 (因此): 模组必须出 4-lane MIPI CSI-2。** (本项目 `HW/AR0234CS_RK3572_PORT_SPEC.md` 里的 AR0234CS 方案是 2-lane 900 Mbps/lane ⇒ **换 IMX415 后 CSI 走线/连接器必须改 4-lane**, 这条要进 ISS-150 的网表改动单。)

---

## 3. ③ 现成 IQ 文件适用哪个分辨率 —— 明确结论 + 工作量

### 3.1 ★ 仓库实测: RK3572 (isp3x) 能用的 IMX415 IQ 只有 **1 个**

`[实测]` `https://github.com/TinkerBoard/rockchip-linux-external-camera_engine_rkaiq` (整树 `git/trees/HEAD?recursive=1`, 2551 项, 已实测):

| 文件 | 目录 | 格式 | RK3572 (isp3x) 能用? |
|---|---|---|---|
| `imx415_CMK-OT2022-PX1_IR0147-50IRC-8M-F20.json` | `rkaiq/iqfiles/isp3x/` | JSON (isp3x) | ✔ **唯一可用** |
| `imx415_YT-RK415-V1_IR0147-60IRC-8M-F20.xml` | `rkaiq/iqfiles/**isp20**/` | XML | ✘ isp2.0 代, 格式/目录都不对 |
| `imx415_YT10092_IR0147-28IRC-8M-F20.xml` (+`-hdr3`) | `rkaiq/iqfiles/**isp20**/` | XML | ✘ 同上 |
| `imx415_YT10092_IR0147-36IRC-8M-F20.xml` (+`-hdr3`) | `rkaiq/iqfiles/**isp20**/` | XML | ✘ 同上 |
| `imx415_YT10092_IR0147-60IRC-8M-F20.xml` (+`-hdr3`) | `rkaiq/iqfiles/**isp20**/` | XML | ✘ 同上 |
| `FEC_mesh_3840_2160_imx415_3.6mm/` (10 个 .bin) | `rkaiq/iqfiles/` | 二进制网格 | ⚠ **文件名锁死 3840_2160** ⇒ 1080p 用不了 |
| `LDCH_mesh_3840_2160_imx415_3.6mm/` (5 个 .bin) | `rkaiq/iqfiles/` | 二进制网格 | ⚠ 同上 |

### 3.2 ★ IQ 文件里分辨率是**写死的**

`[实测]` IQ JSON 头部:
```json
"sensor_calib": {
    "resolution": { "width": 3840, "height": 2160 },
    ...
}
```
⇒ ★**IQ 自己声明的标定分辨率是 3840×2160。**

### 3.3 ★★ 明确结论 + 工作量

| 子项 | 结论 | 等级 |
|---|---|---|
| **能不能"裁到 1080p60 后直接用"** | ✘ **不能直接用**。至少两处硬伤: ① IQ 的 `sensor_calib.resolution` = 3840×2160, 与 ISP 实际进线 1920×1080 不符; ② **LSC(mesh) 网格文件按 3840×2160 标定, 仓库里没有 1920×1080 的版本** ⇒ 四角/边缘的色彩与亮度校正会偏 | `[实测]` |
| **要不要重调** | ✔ **要**, 但范围可控: **① 补一套 1920×1080 的 FEC/LDCH mesh (网格标定); ② AE 曝光表按新帧长换算** (VMAX 3165→1582 ⇒ 最大曝光时间减半, `exposure_index` 表要按新行时间/帧长重算) | `[推算]` |
| **工作量** | ★**1~2 人日** (含灰卡/暗室一次标定 + AE 换算), **不是 AR0234CS 那条路的 1~2 人周**。⇒ **demo 阶段这是唯一、也是最小的 tuning 工作** | `[推算]` |
| **对老板判据的意义** | ★**"数据来源充足"仍然成立**: 数据 (IQ JSON + 网格 + 驱动 + 官方 datasheet) 全部公开可得、下载即用; 需要补的只是"换分辨率的网格标定"这一步, 而这一步**有现成工具链** (rkaiq iqtool) | `[实测]+[推算]` |
| **[待核]** rkaiq 在 `sensor_calib.resolution` 与实际进线分辨率不一致时的**具体行为** (是硬报错拒绝加载, 还是打 warning 后继续) —— 本次公开来源没查到实现细节。★**保守假设: 报错或明显色彩偏差 ⇒ 必须补 1920×1080 网格** | `[待核]` |

### 3.4 ★ 命名解码 (给采购用)

`imx415_CMK-OT2022-PX1_IR0147-50IRC-8M-F20.json`:
- `CMK-OT2022-PX1` = **模组型号** (摄像头模组 / 型号 / 变体)
- `IR0147` = **镜头代号** (与 mesh 目录名 `imx415_3.6mm` 呼应 ⇒ 该镜头 **EFL ≈ 3.6 mm**)
- `50IRC` = **IR-cut 规格** (同族还有 28IRC / 36IRC / 60IRC)
- `8M` = **8 兆像素标定档** (对应 3840×2160)
- `F20` = **光圈 F2.0**
⇒ ★★**采购必须买到"同镜头代号 + 同 IRC 规格"的模组, 否则现成 IQ 的颜色/亮度基线对不上, 整套 IQ 等于作废。**

---

## 4. ④ 模组采购硬判据 (写死, 不发问询函)

> 全部公开可得 / 全部可自证。**只要有一条不满足就不买。**

| # | 硬判据 | 验收方法 | 依据 |
|---|---|---|---|
| **P1** | ★**Sensor 必须是 Sony IMX415 (AAQR 彩色版)**, 1/2.8" 8.46MP | 模组丝印/料号 + 芯片 ID **0x311A 读回 = 0xE0** | 驱动 `CHIP_ID 0xE0` / `IMX415_REG_CHIP_ID 0x311A` (L81-82) |
| **P2** | ★**必须 4-lane MIPI CSI-2** (4 条 data lane 全部引出) | FPC 引脚表里有 DMO1/DMO2/DMO3/DMO4 四组差分 + DCK | ★驱动 2-lane 表无 binning 模式 ⇒ 2 lane 拿不到 1080p (§2.3 L3218) |
| **P3** | ★**I2C 7-bit 地址 = 0x1A** | 模组原理图/引脚表 | 与本板 TMP117 (0x48) / 充电 IC / 光机**不冲突** ✔ |
| **P4** | ★**供电必须 3 轨直出裸 sensor** (1.1V / 1.8V / 2.9V), **不能是模组自带 LDO 只收一路 3.3V** —— 或反过来: **必须自带 LDO 且只收一路**, 二者择一但**必须在采购单上写死** | 模组框图 | ★驱动要 3 个 regulator (`dvdd`/`dovdd`/`avdd`, L179-183); 自带 LDO 的模组则由模组内部生成 ⇒ **本板 LDO 数量随之变** (ISS-150 要按此画网表) |
| **P5** | ★**AC 耦合电容**: MIPI D-PHY 的 DMO/DCK 差分对**必须**有 AC 耦合电容。**要求"模组板载"**, 不接受由主板代焊 | 模组 BOM / 照片 | 若主板代焊 ⇒ 本板要多加 8 只 100nF (4 lane × 2) ⇒ **影响 BOM 与板面积**, 必须提前定 |
| **P6** | ★**必须自带镜头 + IR-cut 滤光片**, 且镜头代号须匹配 **`IR0147`** (EFL ≈ 3.6 mm), IR-cut 规格须与所选 IQ 一致 (选 `50IRC` ⇒ 必须买 `50IRC` 那一档) | 模组料号 + IQ 文件名对应 | §3.4; ★**买错镜头/IR-cut ⇒ 现成 IQ 直接作废** |
| **P7** | ★**必须带 `XCLR` (复位) 和 `INCK` (主时钟) 引脚**; `SLAMODE0/1` 引出或固定地址 0x1A | 引脚表 | 驱动需要 XCLR + xclk; 时序要求: 电源→XCLR ≥500 ns, XCLR→clk ≥1 µs, XCLR→I2C ≥20 µs (驱动 L2618/2624/2650 注释) |
| **P8** | ★**FPC 规格**: 引脚数、间距 (0.5 mm pitch)、**弯折方向与最小弯折半径**、连接器型号须与主板 CAM 连接器匹配 | 模组机械图 | ★**这条不写死 = 装机时才发现装不上 ⇒ 返工 2~4 周** (老板关注的返工成本) |
| **P9** | ★**主时钟频率**: 4-lane 用 **37.125 MHz** (驱动 `IMX415_XVCLK_FREQ_37M`), 2-lane 用 27 MHz | 模组要求 | ★**主板 CAM 连接器要引 xclk, 频率与驱动一致** |
| **P10** | ★**电流能力**: AVDD 轨必须能供 **≥156 mA**, DVDD 轨 **≥250 mA** (datasheet max) ⇒ 主板 LDO 选型满足 | 复算 | §1.1 |
| **P11** | ★**工作温度**: 模组 `-30 ~ +60 °C` (环境) 可接受; 镜腿内靠近皮肤一侧按整机热设计核 | 规格书 | demo 阶段容忍 |
| **P12** | ★**随货必须提供**: ①**引脚定义表** ②**模组尺寸图 + FPC 图** ③**镜头/IR-cut 规格** ④**AC 耦合电容是否板载的明确说明** ⑤**INCK 频率要求** ⑥**模组功耗/电流表** | 收货清单 | ★**缺项 = 不下单** (不靠问询函补, 按合同附件写死) |

---

## 5. ★ [待核] 清单 (公开来源未覆盖, 不联系厂家的前提下怎么闭)

| # | 待核项 | 闭法 | 阻塞谁 |
|---|---|---|---|
| **T1** | ★**TPS7A20 固定档位表**里有没有 1.1V / 1.8V / 2.9V 三个点 | 查 TI 官网档位表 (公开, 不需联系厂家) | ISS-150 改网表 (选料) |
| **T2** | ★**rkaiq 对 `sensor_calib.resolution` 不匹配的实际行为** (拒绝加载 / 仅告警) | 读 rkaiq 源码 `sensor_hw_info` / `iq_parser` 路径 (公开仓库, 本次没读完) | §3.3 的 tuning 工作量定性 |
| **T3** | ★**IMX415 I2C_A 同总线从设备的电平域** (TMP117 / 充电 IC / 光机 / 屏) | 查本项目网表 + 各器件 datasheet | §1.4 上拉电平定案 |
| **T4** | ★**binning 模式的 INCK / 最小 HMAX** (我算 1H 用的是 74.25 MHz 口径, 与驱动 xclk 37.125 MHz 的关系是"传感器内部 ×2") | 读 datasheet 的 AC 特性 (INCK 章节) + 驱动注释 | §2.4 帧率算式的严谨性 |
| **T5** | ★**驱动报的 1944×1097 与传感器实际 binning 输出 1932×1096 的 12px/1row 差** 从哪来 | 读 datasheet 窗口/binning 章节 | ISP 对齐 (不影响 1920×1080 裁剪结果) |
| **T6** | ★**模组引脚数 / 连接器型号** (P8) | 只能从供应商规格书拿 —— ★**但这条写进采购单当"必须随货提供"的附件**, 不发问询函 | 装机 |
| **T7** | ★**AE 曝光表换算的具体幅度** (VMAX 3165→1582 ⇒ 曝光区间减半) | 拿到 rkaiq iqtool 后实测一次 | §3.3 工作量 1~2 人日是否够 |

---

## 6. 证据清单 (URL + 定位)

| # | 来源 | URL | 定位 | 等级 |
|---|---|---|---|---|
| E1 | **Sony IMX415-AAQR Flyer** | https://www.sony-semicon.com/files/62/flyer_security/IMX415-AAQR_Flyer.pdf | "analog 2.9 V, digital 1.1 V, interface 1.8 V triple power supply"; "Readout mode: All-pixel scan mode / **Horizontal/Vertical 2/2-line binning mode** / Window cropping mode"; "All pixel 3840×2160 90.9 fps / **2/2-line binning 1920×1080 90.9 fps**"; "Package 114 pin LGA" | `[官方]` |
| E2 | **IMX415-AAQR-C Datasheet** (Radxa 公开镜像) | https://dl.radxa.com/accessories/camera-4k/IMX415-AAQR-C_Datasheet_E19504.pdf | p.3 绝对最大额定值 (AVDD/OVDD/DVDD/VI); p.3 应用条件 (AVDD1/OVDD/DVDD1); p.14 DC 特性 (VIH/VIL/IOH/IOL); p.15 电流消耗 (IAVDD/IOVDD/IDVDD); §"Power Up" 上电顺序 DVDD→OVDD→AVDD / 200 ms | `[官方]` |
| E3 | **Rockchip BSP `imx415.c`** (develop-6.1) | https://raw.githubusercontent.com/rockchip-linux/kernel/develop-6.1/drivers/media/i2c/imx415.c | L179-183 轨名; L690-725 binning 寄存器表 (0x3020=0x01); L1255-1276 1944×1097@30fps 模式项; L2800-2840 `get_selection` 裁到 1920×1080; L1516-1522 vblank; L3218 2lane/4lane 分表 | `[实测]` |
| E4 | **Linux mainline `imx415.c`** | https://raw.githubusercontent.com/torvalds/linux/master/drivers/media/i2c/imx415.c | 上游同源模式表 (交叉验证) | `[实测]` |
| E5 | **rkaiq IQ 仓库整树** | https://github.com/TinkerBoard/rockchip-linux-external-camera_engine_rkaiq (`git/trees/HEAD?recursive=1`) | `rkaiq/iqfiles/isp3x/imx415_CMK-OT2022-PX1_IR0147-50IRC-8M-F20.json` (唯一 isp3x); 其余 7 个在 `isp20/` 且是 xml; mesh 目录名锁 3840_2160 | `[实测]` |
| E6 | **IQ JSON 本体** | 同 E5 raw 路径 | `sensor_calib.resolution = {3840, 2160}`; `Gain2Reg`/`CISGainSet`/`CISTimeSet` (帧长相关项) | `[实测]` |
| E7 | **本项目开源快照** | `HW/_os_snapshots/rkaiq_iqfiles.json` / `rockchip_bsp_i2c.json` / `linux_mainline_i2c.json` / `github_repo_counts.json` | IMX415: isp3x IQ 1 个 + isp20 IQ 7 个; BSP 驱动有 `imx415.c` ✔; mainline 有 `imx415.c` ✔; GitHub 命中 **51** 个仓库 | `[实测]` |
| E8 | **ISP 吞吐口径** | 本项目 `HW/R_GEO_Q03_ISP_THROUGHPUT_ADJUDICATION.md`, `HW/e2e_budget_rk3572.py` | ISP 250 MP/s 口径 / 余量 44.7% | `[实测]` |
| E9 | **AR0234CS 对照** | `HW/AR0234CS_OPEN_SOURCE_FACTS.md` (本文同时产出) | U2 / U4 | `[官方]` |

---

## 7. ★ 给 ISS-150 (改网表) 的落账清单 (本单不改网表)

| # | 要改什么 | 从 | 到 | 依据 |
|---|---|---|---|---|
| **N1** | `SENSOR_CORE` 轨电压 | 1.2 V | **1.1 V** | §1.2 / E2 |
| **N2** | `SENSOR_VDD_IO` 轨电压 | 2.8 V | **1.8 V** | ★★§1.2 —— **不改会烧 sensor** |
| **N3** | `SENSOR_AVDD` 轨电压 | 2.8 V | **2.9 V** | §1.2 / E2 |
| **N4** | 三条轨的电流规格文字 | 50 / 30 / 30 mA | **250 / 3 / 156 mA** (max) | §1.1 / E2 |
| **N5** | I2C_A 上拉电平 | 3.3 V | **1.8 V (建议) / 3.3V (可接受, 但阻值要重算 ≥1.0kΩ)** | §1.4, ★前置 T3 |
| **N6** | CAM 连接器 / CSI 走线 | **2-lane** | **4-lane** | ★§2.5 (驱动只在 4-lane 表有 binning) |
| **N7** | 上电顺序 | 三轨同时 | **DVDD→OVDD→AVDD** | §1.3 / E2 |
| **N8** | 新增 1080p60 模式 | — | VMAX 0x0C5D→0x062E + mode 项 | §2.4 |
| **N9** | IQ | 8M 3840×2160 | **补 1920×1080 mesh + AE 曝光表换算** | §3.3 |

---

## 8. 复现命令

```bash
# 取 Rockchip BSP 驱动
curl -sSL https://raw.githubusercontent.com/rockchip-linux/kernel/develop-6.1/drivers/media/i2c/imx415.c -o rk_imx415.c
grep -n "1944\|1097\|0x3020\|imx415_supply_names" rk_imx415.c

# 取 IMX415 datasheet 并转文本 (Radxa 公开镜像)
curl -sSL https://dl.radxa.com/accessories/camera-4k/IMX415-AAQR-C_Datasheet_E19504.pdf -o imx415_ds.pdf
pdftotext -layout imx415_ds.pdf imx415_ds.txt
grep -n -A25 "Absolute Maximum Ratings" imx415_ds.txt

# 取 rkaiq 整树, 确认 IMX415 的 IQ 分布
curl -sSL "https://api.github.com/repos/TinkerBoard/rockchip-linux-external-camera_engine_rkaiq/git/trees/HEAD?recursive=1" \
  | python3 -c "import json,sys; [print(t['path']) for t in json.load(sys.stdin)['tree'] if 'imx415' in t['path']]"

# 取 IQ JSON, 看声明的分辨率
curl -sSL https://raw.githubusercontent.com/TinkerBoard/rockchip-linux-external-camera_engine_rkaiq/HEAD/rkaiq/iqfiles/isp3x/imx415_CMK-OT2022-PX1_IR0147-50IRC-8M-F20.json \
  | grep -A4 '"resolution"'
```
