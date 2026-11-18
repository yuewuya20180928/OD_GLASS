# Waveshare 2.8inch DSI LCD (SKU 22028) —— init 序列 / 背光电流 / RK3572 DSI 能力

> **任务**: 2026-11-04 01:19 boss 拍板 demo 屏换 Waveshare 2.8inch DSI LCD (SKU 22028) ⇒ 本文件只回答三件事:
> ① init 序列 (树莓派官方 → Rockchip 格式) · ② 背光/3V3 电流 · ③ RK3572 DSI 能不能 2-lane / 支不支持 VESA DSC
>
> **本文件不改任何其它交付物** (网表 / 板文件 / issue_log / tracker / STATE.yaml 一律未动) —— 凡是"要改别处"的结论, 一律以 **⚠️ 待办 (只提示, 不执行)** 列出。
>
> **证据等级约定**:
> `[官方]` = 树莓派官方 firmware / Rockchip 官方内核源码 / 厂商 datasheet / 厂商官方 wiki 与商品页
> `[实测]` = 本地对官方二进制/源码直接解出来的实测结果 (如 dtbo 解包)
> `[推断]` = 由官方事实推导, **不是** 官方原文
> `[未查到]` = 查过但官方渠道确实没有, 并列出试过的 URL

---

## 0. TL;DR (三条结论先给)

| # | 问题 | 结论 | 证据等级 |
|---|---|---|---|
| ① | init 序列 | ★★**这块屏不需要任何 DCS init 序列** —— 树莓派官方内核驱动 `panel-waveshare-dsi.c` 对 `waveshare,2.8inch-panel` **一条 DSI 指令都不发**, 全部控制走 **I2C (模组内 MCU)**: probe 写 `0xC0/0xC2/0xAC`、enable 写 `0xAD=0x01`、disable 写 `0xAD=0x00`、背光写 `0xAB`+`0xAA` | `[官方]` |
| ② | 背光电流 | ★**官方未公布 (未查到)** —— 官方商品页规格表只有 10 个字段, **没有电流/功耗字段**; 15 针表无背光脚 ⇒ 背光在模组内从 3V3 取电。**推断 ≤150mA@3.3V (含背光)** ⇒ **LIGHT_3V3 预算 150mA → 建议改 200mA**, **不触发** TPS7A2033 换料/并联 (额定 300mA, 降额上限 240mA) | `[未查到]` + `[推断]` |
| ③ | DSI 2-lane / DSC | **2-lane: 支持** (RK3572 `max_data_lanes = 4`, lane 数由 DT `dsi,lanes` 决定, 1/2/4 都跑得动); ★★**DSC: 不支持 —— RK3572 没有 DSC 编码器** (DSI TX 内核全文无 dsc; VOP2 只有 RK3588 有 `.nr_dscs = 2`; Rockchip 自己的 DSI2 驱动里 `.dsc = true` 也**只有 RK3588**) ⇒ **视涯 0.49" (VESA DSC 3:1) 在 RK3572 上不能用** | `[官方]` |

> ★**这三条把 `HW/DISPLAY_SMALL_SCREEN_OPTIONS.md` §3.1 的一条前提推翻了**: 该文写 "init sequence 公开可得 ⇒ 把树莓派的 init 翻译成 Rockchip 格式"。**事实是树莓派官方根本没有这段 init 序列** —— 所以本任务不是"翻译", 而是"**确认不需要**"。这反而是好事: 不存在"抄错一条寄存器把屏烧了"的风险。

---

## 1. init 序列: 树莓派官方到底有没有?

### 1.1 ★原始出处 (逐条给到文件路径 + commit + 分支)

| 项 | 值 |
|---|---|
| 文件 | `drivers/gpu/drm/panel/panel-waveshare-dsi.c` |
| 仓库 | 树莓派官方内核 `raspberrypi/linux` |
| 分支 | `rpi-6.12.y` (本次取证) · `rpi-6.18.y` (逐行 diff, 2.8" 条目**完全一致**) |
| 首次提交 | commit **`d8e5eb49991de6b8fa9231532a11036e24aa84de`** · 2023-04-14 · Dave Stevenson \<dave.stevenson@raspberrypi.com\> · "drm/panel: Add panel driver for Waveshare DSI touchscreens" |
| 后续提交 | `5be45105efe5` (2024-12-05, +13.3") · `ce9e4c59477b` (2025-04-01, +7.0"H) —— **都没动 2.8" 条目** |
| URL | <https://github.com/raspberrypi/linux/blob/rpi-6.12.y/drivers/gpu/drm/panel/panel-waveshare-dsi.c> |

★**该 commit 的正文本身就是架构说明** (原文照抄):

> "Waveshare sell a range of DSI panels of varying sizes, **all using a common MCU to control the panel and backlight**."

⇒ 官方口径: **Waveshare DSI 屏 = DSI 只跑像素流, 面板与背光由模组内 MCU (I2C) 控制**。

### 1.2 ★树莓派官方对这块屏做的**全部**动作 (逐条照抄, 一条不漏)

驱动是 **i2c_driver** (`i2c_driver(&ws_panel_driver)`), `of_device_id` 表里 `waveshare,2.8inch-panel` ⇒ **面板本身就是一个 I2C 设备**。

**(a) probe 时 (3 条 I2C 写)** —— `ws_panel_probe()`:

```c
	ws_panel_i2c_write(ts, 0xc0, 0x01);
	ws_panel_i2c_write(ts, 0xc2, 0x01);
	ws_panel_i2c_write(ts, 0xac, 0x01);
```

**(b) 点亮 / 熄灭 (面板使能, 走 I2C 不是 DCS)**:

```c
static int ws_panel_enable(struct drm_panel *panel)
{
	ws_panel_i2c_write(ts, 0xad, 0x01);   /* enable  */
}
static int ws_panel_disable(struct drm_panel *panel)
{
	ws_panel_i2c_write(ts, 0xad, 0x00);   /* disable */
}
```

**(c) 背光亮度 (I2C, BACKLIGHT_RAW 类型)**:

```c
static int ws_panel_bl_update_status(struct backlight_device *bl)
{
	ws_panel_i2c_write(ts, 0xab, 0xff - backlight_get_brightness(bl));
	ws_panel_i2c_write(ts, 0xaa, 0x01);
}
```

**(d) DSI 侧参数 (2.8" 条目, 逐字照抄)**:

```c
static const struct drm_display_mode ws_panel_2_8_mode = {
	.clock = 50000,
	.hdisplay = 480,
	.hsync_start = 480 + 150,
	.hsync_end = 480 + 150 + 50,
	.htotal = 480 + 150 + 50 + 150,
	.vdisplay = 640,
	.vsync_start = 640 + 150,
	.vsync_end = 640 + 150 + 50,
	.vtotal = 640 + 150 + 50 + 150,
};

static const struct ws_panel_data ws_panel_2_8_data = {
	.mode = &ws_panel_2_8_mode,
	.lanes = 2,
	.mode_flags = MIPI_DSI_MODE_VIDEO_HSE | MIPI_DSI_MODE_VIDEO | MIPI_DSI_CLOCK_NON_CONTINUOUS,
};
```

且在 probe 末尾:

```c
	ts->dsi->mode_flags = _ws_panel_data->mode_flags;
	ts->dsi->format = MIPI_DSI_FMT_RGB888;
	ts->dsi->lanes = _ws_panel_data->lanes;
```

**(e) ★全文件里 DSI 侧的写操作为零** —— 整个 `panel-waveshare-dsi.c` **没有一次 `mipi_dsi_dcs_write*` / `mipi_dsi_generic_write`**; 也就是说 ★**官方没有给这块屏发过任何 DCS init 序列**。

### 1.3 ★I2C 侧的两个地址 (官方 firmware overlay 实测解包)

来源: 树莓派官方 firmware 仓库 `boot/overlays/vc4-kms-dsi-waveshare-panel.dtbo` (master)
<https://github.com/raspberrypi/firmware/blob/master/boot/overlays/vc4-kms-dsi-waveshare-panel.dtbo> `[实测]` (本地解 DTB 得出)

| 节点 | reg | compatible | 说明 |
|---|---|---|---|
| `panel_disp1@45` | **0x45** | 默认 `waveshare,10.1inch-panel`; 被 override 改成 `waveshare,2.8inch-panel` | ★**这块屏的 MCU 在 I2C 7-bit 地址 0x45** (`2_8_inch` override 只改 compatible / touchscreen-size, **不改 reg** ⇒ 2.8" 与其它 Waveshare 屏同址) |
| `goodix@14` | **0x14** | `goodix,gt911` | 5 点电容触摸 (GT911) —— 我们 demo 阶段可不接 |
| `ilitek@41` | 0x41 | `ilitek,ili2517` | `status = "disabled"` (未用) |

★官方 wiki 也确认用法: `dtoverlay=vc4-kms-dsi-waveshare-panel,2_8_inch` (Bookworm/Trixie) —— 走的就是上面这个内核驱动。

### 1.4 Rockchip 侧 `panel-init-sequence` 的格式 (★别被任务书里的说法带偏)

任务书写 "`<延迟us> 0x<reg> 0x<参数>`" —— ★**实际不是这样**。Rockchip develop-6.12 `drivers/gpu/drm/panel/panel-simple.c`:

```c
struct panel_cmd_header {
	u8 data_type;
	u8 delay;
	u8 payload_length;
} __packed;                                   /* ← 3 字节头, 不是 4 */
```

⇒ **`panel-init-sequence` 每条 = `<data_type> <delay(ms)> <payload_len> <payload...>`**, 且 ★**delay 是"发完这条之后"的延时** (`panel_simple_xfer_dsi_cmd_seq()`: 先写后 `panel_simple_msleep(cmd->header.delay)`)。

对照我们本地模板 `HW/PCB/panel_simple_dsi_template.dtsi` (取自 `rk3576-evb.dtsi:261`) 的 `23 00 02 FE 21`:
`data_type=0x23` = `MIPI_DSI_GENERIC_SHORT_WRITE_2_PARAM`, `delay=0x00`, `len=2`, payload=`FE 21`。
(枚举值出处: `include/drm/drm_mipi_dsi.h` — `MIPI_DSI_MODE_VIDEO=BIT(0)`, `MIPI_DSI_MODE_VIDEO_HSE=BIT(4)`, `MIPI_DSI_CLOCK_NON_CONTINUOUS=BIT(10)`, `MIPI_DSI_FMT_RGB888`) `[官方]`

★★**init 序列属性是"可选"的** —— `panel_simple_of_get_desc_data()`:

```c
	data = of_get_property(np, "panel-init-sequence", &len);
	if (data) { ...解析... }        /* 属性不存在 ⇒ 一条都不发, 不报错 */
```

⇒ **我们要么不写 `panel-init-sequence`, 要么写空 —— 绝不会"漏写导致黑屏"。**

### 1.5 ★★可直接粘贴的 dts 片段 (2-lane / 480×640)

> 时序 100% 抄自 §1.2(d) 的 `ws_panel_2_8_mode`; **没有任何"按经验改"**。
> ★ 时序节点用 **Rockchip 自家的 `display_timing` 绑定** (`drivers/video/of_display_timing.c`: `clock-frequency` / `hactive` / `hfront-porch` / `hback-porch` / `hsync-len` / `vactive` / `vfront-porch` / `vback-porch` / `vsync-len`), **不是** 上游 `clock/hdisplay/...` 那套 —— 写错属性名内核会 `could not find property` 直接拒绝。
> ★ `clock-frequency` 单位 **Hz** (`drm_display_mode_from_videomode()`: `dmode->clock = vm->pixelclock / 1000` ⇒ Hz 进、kHz 出)。

```dts
/*
 * Waveshare 2.8inch DSI LCD  (Part No. "2.8inch DSI LCD", SKU 22028)
 * 480x640 / MIPI DSI 2-lane / 15pin 1.0mm FPC / 3V3 (pin14+pin15) / 模组内供背光
 *
 * 时序/格式/模式标志: 逐字抄自树莓派官方内核
 *   drivers/gpu/drm/panel/panel-waveshare-dsi.c  (compatible "waveshare,2.8inch-panel")
 *   commit d8e5eb49991de6b8fa9231532a11036e24aa84de (2023-04-14, Dave Stevenson)
 *
 * ★ 本屏 **不需要 DCS init 序列** (官方驱动零 DSI 写) ⇒ 不写 panel-init-sequence。
 */
&dsi {
	status = "okay";
	//rockchip,lane-rate = <1000>;      /* 可选: 每 lane 目标速率 (Mbps), 驱动也会按 mode 自动算 */

	dsi_panel: panel@0 {
		status = "okay";
		compatible = "simple-panel-dsi";
		reg = <0>;

		/*
		 * ★ 背光: 本屏没有独立背光脚, 背光/点亮由模组内 MCU 经 I2C (地址 0x45) 控制
		 *   ⇒ 故意 **不写** backlight = <&backlight> (那会走 DCS 0x51 调光, 本屏不认)
		 *   ⇒ 不写时内核会自己注册一个 DCS 背光设备, 亮度写 0x51 会被本屏忽略, 无害
		 */
		reset-delay-ms   = <10>;
		enable-delay-ms  = <10>;
		prepare-delay-ms = <10>;
		init-delay-ms    = <10>;
		unprepare-delay-ms = <10>;
		disable-delay-ms = <60>;

		width-mm  = <43>;    /* [推断] 2.8" 对角 71.1mm, 3:4 ⇒ 42.7 x 56.9mm; 官方未公布 */
		height-mm = <57>;    /* [推断] 同上 */

		dsi,flags  = <(MIPI_DSI_MODE_VIDEO | MIPI_DSI_MODE_VIDEO_HSE |
				MIPI_DSI_CLOCK_NON_CONTINUOUS)>;
		dsi,format = <MIPI_DSI_FMT_RGB888>;
		dsi,lanes  = <2>;

		/* 时序: 抄自树莓派 ws_panel_2_8_mode
		 *   clock=50000kHz / hdisplay=480 / hsync_start=630 / hsync_end=680 / htotal=830
		 *   vdisplay=640 / vsync_start=790 / vsync_end=840 / vtotal=990
		 *   ⇒ 刷新率 = 50e6 / (830 x 990) = 60.85 Hz
		 */
		panel-timing {
			clock-frequency = <50000000>;
			hactive    = <480>;
			hfront-porch = <150>;   /* hsync_start 630 - hdisplay 480 */
			hsync-len   = <50>;    /* hsync_end 680 - hsync_start 630 */
			hback-porch = <150>;   /* htotal 830 - hsync_end 680 */
			vactive    = <640>;
			vfront-porch = <150>;   /* vsync_start 790 - vdisplay 640 */
			vsync-len   = <50>;    /* vsync_end 840 - vsync_start 790 */
			vback-porch = <150>;   /* vtotal 990 - vsync_end 840 */
		};

		/* ★ panel-init-sequence: 故意省略 (官方驱动零 DCS 写, 见 §1.2(e)) */
		/* ★ panel-exit-sequence: 故意省略 (官方驱动无退出序列) */
	};
};
```

★**屏侧 I2C 另需接** (否则屏可能点不亮 + 无法调光) —— 见 §4 的 P0 待办。

### 1.6 "4-lane 版本的差异说明"

| 维度 | 2-lane (本屏, 实际) | 4-lane (假想) |
|---|---|---|
| **屏侧物理** | ★**物理上只有 2 对差分**: 15 针表 = `DSI1_DN0/DP0` + `DSI1_DN1/DP1` + `DSI1_CN/CP` ⇒ **4-lane 对这块屏不是"软件选择", 是物理不存在** | 需要屏侧有 DN2/DP2/DN3/DP3 ⇒ **必须换屏/换模组** |
| **dts** | `dsi,lanes = <2>` | `dsi,lanes = <4>` (其余全同) |
| **内核支持** | ✔ `max_data_lanes = 4` ⇒ 1/2/4 都能跑 | ✔ 同左 |
| **SoM 侧** | FET3572-C 的 DSI 4 对差分 (P3: CK±/D0±/D1±/D2±/D3±) **针位固定, 一个字都不用改** | 同左 |
| **主板→屏这一段** | ★**我们 demo 屏座只有 15 位 (2 对差分) ⇒ 物理上只能走 2-lane**; 要留 4-lane 能力只能按 `DISPLAY_SMALL_SCREEN_OPTIONS.md` §4.3 方案 A 在同位置**再放一个 24 位/0.5mm 4-lane 座 (DNP 或 0Ω 选择)** | 同左 |
| **带宽** | 50MHz × 24bpp = **1.2Gbps payload ⇒ 600Mbps/lane** (RK3572 驱动上限 1.8Gbps/lane, 余量 3×) | 300Mbps/lane (用不上) |

★所以 **`DISPLAY_SMALL_SCREEN_OPTIONS.md` §4.1 "主板→屏仍按 4-lane 画, 将来不用改板" 这条建议, 对 demo 屏 (15 针座) 在物理上不成立** —— 15 针座放不下 4 对差分。要么接受 demo 阶段 2-lane 且将来换座, 要么现在就上 24 位双座方案。

### 1.7 兜底方案 (★仅当实测发现面板确实需要 DCS init 时)

Rockchip 内核里有 **同分辨率 (480×640)、同 lane 数 (2-lane) 的现成 GIP 序列**: `drivers/gpu/drm/panel/panel-sitronix-st7701.c` 的 `densitron,dmt028vghmcmi-1a` (完整 GIP 写在 .c 里, `panel_sleep_delay = 5`) `[官方]`。

★**但它不是这块屏的序列** —— 两者时序明显不同:

| | Waveshare 2.8" (RPi 官方) | Densitron DMT028VGHMCMI-1A (Rockchip 内核) |
|---|---|---|
| clock | 50000 kHz | 22325 kHz |
| htotal / vtotal | 830 / 990 | 544 / 698 |
| 刷新率 | 60.85 Hz | ≈58.8 Hz |

⇒ **不要混用**。只有在实测确认这块屏的驱动 IC 确实是 ST7701 且兼容时, 才考虑改用 Rockchip 内核那个档位 (那样连 dts 时序都要换成它的)。

---

## 2. 背光 / 3V3 电流

### 2.1 ★官方数据: **未查到**

★ 官方商品页规格表 (把页面里全部 `igKey/igValue` 字段抠出来, 共 10 项) —— **没有任何电流/功耗/背光字段**:

```
Size 2.8″ / Resolution 480×640 / Display Port DSI / Display Panel IPS /
Viewing Angle 160° / Touch Type Capacitive / Touch Points 5-Points /
Touch Port I2C / Touch Panel Tech Optical Bonding / Touch Panel Toughened Glass
```

★ 官方 wiki (中/英) 也只有 "**Supports software control of backlight brightness**" 一句, **无背光电压/电流/PWM 能力参数**。

**试过的 URL (全部无电流数据)**:
1. <https://www.waveshare.com/product/2.8inch-dsi-lcd.htm> (规格表字段清单如上)
2. <https://www.waveshare.com/wiki/2.8inch_DSI_LCD> (英)
3. <https://www.waveshare.net/w/index.php?title=2.8inch_DSI_LCD&action=raw> (中, raw)
4. <https://www.waveshare.com/product/4inch-dsi-lcd.htm> / `3.4inch-dsi-lcd-c.htm` (同族对比, 无)
5. <https://www.waveshare.com/product/5inch-dsi-lcd.htm> —— ★唯一带功耗字段的同族页面, 但只写 **"Power Consumption: Low Power"**, **无数值**
6. <https://files.waveshare.com/upload/b/b3/2.8inch_DSI_LCD.zip> (3D 图; 无电气参数)

### 2.2 可用的官方锚点

| 锚点 | 值 | 等级 |
|---|---|---|
| 15 针表 | pin14 = 3V3, pin15 = 3V3, **无背光脚、无 RESET 脚** | `[官方]` |
| 官方内核 commit 正文 | "all using a common MCU to control the panel and backlight" ⇒ 背光由模组内 MCU 控 | `[官方]` |
| Rockchip 内核 `panel-sitronix-st7701.c` 同分辨率裸面板 (480×640/2-lane) 电源域 | 面板逻辑本身的 3.3V 域电流为**十几 mA 量级** (ST7701 裸面板档位的 vdd3p3 负载 ~13mA 量级) —— ⚠️ 这是**裸面板**值, 不是模组值 | `[官方]`(内核) + `[推断]` |

### 2.3 ★推断值与 LIGHT_3V3 预算修正

**[推断, 中置信]** 这块模组从 3.3V 取的电流 = 背光 + 面板逻辑 + 触摸 + MCU + 内部稳压损耗:

| 分项 | 估计 | 依据 |
|---|---|---|
| 背光 (模组内 3~4 颗 LED 并联 @~3.0V, 单颗 ~15~20mA) | **45~80 mA** | `[推断]` 2.8" IPS 背光常规做法 (官方未公布, 无法引证) |
| 面板驱动 IC + MCU + 触摸 | **15~30 mA** | `[推断]` 以同分辨率 ST7701 裸面板 3.3V 域 ~13mA 量级为锚 |
| 内部转换/压降损耗 | **5~15 mA** | `[推断]` |
| **合计 @3.3V** | **≈ 70~125 mA** | `[推断]` |
| **设计上限 (含余量)** | **150 mA** | `[推断]` |

⇒ **结论: 屏这块吃不到 300mA, TPS7A2033 (300mA 额定 / 240mA 建议上限) 不用换、不用并联。**

### 2.4 ★我们 LIGHT_3V3 轨的电流预算修正值

| 项 | 现在 (网表) | 建议修正 | 理由 |
|---|---|---|---|
| `LIGHT_3V3` 预算 | **150 mA** (`netlist_v1.csv` P1 / `RELIABILITY_DESIGN.md` §3 (3) 表) | **200 mA** | 150mA 原本是给"8HD 的 12.8V 背光链 + 其它"估的; 现在屏换成 2.8" 内部供电模组 (估 ~100mA), 但**未知数全在背光上** ⇒ 把余量从 50mA 抬到 100mA, 占 TPS7A2033 额定 300mA 的 67%, 仍在建议上限 240mA 之内 |
| `U_LDO_L33` 器件 | TPS7A2033DQNR (300mA) | **保持不变** | 200mA < 240mA 降额上限 ⇒ 不触发换料/并联 |
| 备注 | — | ⚠️ **R-F1 仍是真风险** | `TPS7A20` 压差 110mV typ ⇒ `LIGHT_3V3` 轨在 **SYS < 3.41V 时失效** (1S 锂电放电末段 ~12~15% 电量)。**换屏不解决这个** —— 屏换小反而让这条更值得优先处理 |

⚠️ **待办 (只提示, 本文件不改网表)**: `HW/netlist_v1.csv` 里 `RAIL_LIGHT_3V3` 的 150mA 与 `HW/RELIABILITY_DESIGN.md` §3 (3) 的 150mA, 建议由裁决人改为 **200mA**, 并把注释补成 "含 Waveshare 2.8" 模组 (~100mA 推断) + 其它 50mA + 余量"。

---

## 3. RK3572 的 DSI: 2-lane 支持 + VESA DSC 支持

### 3.1 2-lane: ✔ **支持**

**证据链 (全部 Rockchip 官方内核 develop-6.12)**:

1. **SoC 侧能力**: `drivers/gpu/drm/rockchip/dw-mipi-dsi-rockchip.c` 的 `rk3572_chip_data`:
   ```c
   .reg = 0x276d0000,
   .max_data_lanes = 4,
   .max_bit_rate_per_lane = 1800000000UL,   /* 1.8 Gbps/lane */
   .soc_type = RK3572,
   ```
   `compatible = "rockchip,rk3572-mipi-dsi"` ⇒ ★**硬件支持到 4 lane**, 用 2 lane 是"少用"而不是"不支持"。
   ⚠️ 注意: datasheet 写 "up to 4lane*2.5Gbps", 但**驱动把上限设在 1.8Gbps/lane** ⇒ 实际按 1.8Gbps 设计。

2. **lane 数由 DT 决定**: `drivers/gpu/drm/panel/panel-simple.c:5844` (`of_property_read_u32(np, "dsi,lanes", &val)`) → `dsi->lanes = desc->lanes` (同文件 `:5904` 附近 `panel_simple_dsi_probe()`)。

3. **lane 数的换算与 DPHY 编程**: `drivers/gpu/drm/bridge/synopsys/dw-mipi-dsi.c`:
   ```c
   339:  dsi->lanes = (device->lanes > max_data_lanes) ? device->lanes / 2 : device->lanes;
   923:  ... N_LANES(dsi->lanes) ...
   ```
   ⇒ `dsi,lanes = 2` ⇒ `dsi->lanes = 2` ⇒ DPHY 编 2 条数据 lane。**1/2/4 全部合法。**

4. **datasheet 佐证**: RK3572 Datasheet V1.1 (本地 `HW/RK3572_PIN_TABLE/rk3572_datasheet_V1.1.txt`):
   - L575: "One MIPI DSI1.2 interface，up to **4lane**\*2.5Gbps"
   - L647-649: "MIPI DSI-1.2 TX interface / One MIPI DSI V1.2 interface with D-PHY / Supports **4 data lanes** on D-PHY with up to 2.5Gbps per lane"
   - ⇒ ★**RK3572 只有 1 个 DSI 控制器** (`rk3572.dtsi:3260` `dsi@276d0000`), 与 "One MIPI DSI" 一致。

5. **非连续时钟也支持** (树莓派驱动用到 `MIPI_DSI_CLOCK_NON_CONTINUOUS`): `dw-mipi-dsi.c:1108`
   ```c
   if (dsi->mode_flags & MIPI_DSI_CLOCK_NON_CONTINUOUS)
           val |= AUTO_CLKLANE_CTRL;
   ```

**带宽校核** `[推算]`: 50 MHz × 24 bpp (RGB888) = **1.2 Gbps payload** ⇒ 2 lane 时 **600 Mbps/lane**, 相对 1.8 Gbps/lane 上限有 3× 余量 ✔。

### 3.2 ★★VESA DSC: ✘ **RK3572 不支持 (查死了)**

**结论**: ★**RK3572 没有任何 DSC 编码器 ⇒ 它不能输出 DSC 压缩的 DSI 流 ⇒ 视涯 0.49" (datasheet 原文 "MIPI D-PHY 1 PORT, **VESA DSC 3:1**") 在 RK3572 上不可用。** (`HW/DISPLAY_SMALL_SCREEN_OPTIONS.md` 里的 ISS-125/D3 "未查" 到此关闭)

**三条独立证据链** (全部 Rockchip 官方内核 develop-6.12):

**证据链 A —— DSI TX 内核里根本没有 DSC**:
`drivers/gpu/drm/bridge/synopsys/dw-mipi-dsi.c` (RK3572 用的就是它) —— ★**全文 grep "dsc" = 0 命中**。⇒ DSI 控制器不会压缩, 只搬运。

**证据链 B —— VOP2 里只有 RK3588 有 DSC 编码器**:
`drivers/gpu/drm/rockchip/rockchip_vop2_reg.c`:
```c
static const struct vop2_data rk3572_vop = {
	.version = VOP_VERSION_RK3572,
	.nr_vps = 2, ...          /* ★ 没有 .nr_dscs ⇒ nr_dscs = 0 */
};
...
static const struct vop2_data rk3588_vop = {
	.version = VOP_VERSION_RK3588,
	.nr_dscs = 2,             /* ★ 只有 RK3588 配了 DSC 模块 */
	.dsc = &rk3588_vop_dsc_data,
};
```
且 `drivers/gpu/drm/rockchip/rockchip_drm_vop2.c` 里所有 DSC 开关函数都叫 `rk3588_vop2_dsc_*` / 走 `vop2->dscs[]` (`nr_dscs` 个) ⇒ **RK3572 无路可走**。

**证据链 C —— Rockchip 自己在 DSI2 驱动里用 per-SoC 标志声明 DSC 能力**:
`drivers/gpu/drm/rockchip/dw-mipi-dsi2-rockchip.c`:
```c
static const struct dw_mipi_dsi2_plat_data rk3576_mipi_dsi2_plat_data = {
	.dsc = false,             /* ★ RK3576: 无 DSC */
	...
};
static const struct dw_mipi_dsi2_plat_data rk3588_mipi_dsi2_plat_data = {
	.dsc = true,              /* ★ 只有 RK3588: 有 DSC */
	...
};
```
⇒ ★**整个 Rockchip 内核里 DSC 能力只出现在 RK3588 上**。

**为什么"驱动里有 DSC 代码"不等于"SoC 支持"** (★这是本题最容易踩的坑, 必须写清楚):
`dw-mipi-dsi-rockchip.c` 里确实有 DSC 代码 (`dw_mipi_dsi_get_dsc_info_from_sink()`: 从面板 DT 读 `compressed-data` + 从 `panel-init-sequence` 里扒 `MIPI_DSI_PICTURE_PARAMETER_SET` 的 PPS, 然后 `s->dsc_enable = 1` 传给 CRTC)。但那只是**把"面板支持 DSC"这个信息上报给 DRM/VOP**; ★**真正的压缩器在 VOP 里**, 而 RK3572 的 VOP 没有这个模块 ⇒ 在 RK3572 上设 `compressed-data` 只会得到**未压缩的数据 + 错误的元信息 = 花屏**。

**datasheet 侧佐证**: RK3572 Datasheet V1.1 全文 **grep "DSC" = 0 命中**; 视频输出的数据格式只列 `RGBA8888/RGB888/RGB565/RGB1010102` / `YUV444/422/420/400` / `Tile 4x4` / **`AFBCD`** (Rockchip 自家的 AFBC 压缩, ≠ VESA DSC) —— ★**datasheet 只字未提 DSC**。

### 3.3 对"整机目标 = 视涯 0.49" (DSC 3:1)"的影响 (★硬判据)

| 方案 | 可行性 |
|---|---|
| RK3572 + 视涯 0.49" (必须 DSC 3:1) | ✘ **不可行** (SoC 侧无 DSC 编码器) |
| RK3588 + 视崖 0.49" | ✔ 理论可行 (`.dsc = true` + `nr_dscs = 2`), 但 SoM 要换 |
| RK3572 + 视崖屏 **不用 DSC** | 需面板厂提供非压缩模式 (1920×1080@60 RGB888 ≈ 2986 Mbps payload ⇒ 4-lane 完全够, 见 `HW/DISPLAY_SENSOR_CHAIN.md` §) ⇒ ★**要去 B2B 问面板厂能不能跑非 DSC 模式** · ★**依据 (ISS-186 订正)**: payload = 1920×1080×24×60 = 2985.98 Mbps ⇒ ①4-lane@2.5Gbps raw 10 Gbps ⇒ 占 **29.9%** ②脚本口径 4-lane@2.0Gbps × 80% = 6400 Mbps ⇒ 占 **46.7%** ⇒ ★**两种口径都远低于 100% ⇒「4-lane 完全够」的结论方向不变**; ★**TX 物理下限 7.776ms (`HW/e2e_budget_rk3572.py` `tx_min_ms()`) = 2986 Mbps ÷ 60fps ÷ 6400 Mbps ⇒ 就是按这个 payload 算的 ⇒ 文档与脚本口径一致** |

⇒ ★**采购硬判据新增一条**: "SY049WDM01 必须支持 **非 DSC** 的 1920×1080@60 RGB888 DSI 模式", 否则 RK3572 方案直接作废。

### 3.4 SoM 侧 (FET3572-C) 怎么配合

- SoM 的 DSI 是 **4-lane + CK** (P3: `DSI_TX_CK_P/N`, `D0_P/N`, `D1_P/N`, `D2_P/N`, `D3_P/N`) ⇒ ★**SoM 侧 pin 分配一个字都不用改** (2-lane 只是少用 2 对)。
- ★**主板→屏这一段**: demo 15 针座物理上只有 2 对差分 ⇒ demo 阶段主板也只能 2-lane (见 §1.6)。
- 主板侧省下来的: **2 对差分走线 + 2 个连接器脚位** (若最终只走 2-lane)。

---

## 4. ⚠️ 待办 (只提示, 本文件不改任何别的交付物)

| 优先级 | 事项 | 依据 | 建议落点 (不改) |
|---|---|---|---|
| **P0** | ★**屏的 I2C 必须接上**: 不接 I2C ⇒ 屏大概率**点不亮** (官方驱动靠 I2C `0xAD=0x01` 使能) + **无法调光** (`0xAB`/`0xAA`)。⇒ 与 `DISPLAY_SMALL_SCREEN_OPTIONS.md` §3.1 "触控一律不接" 的旧结论冲突 (那是在不知道 MCU 角色时的判断) ⇒ **建议把 15 针的 SCL0/SDA0 接到 RK3572 的 I2C 上** (I2C 设备地址 0x45, 触摸 GT911 在 0x14 可选) | §1.2 / §1.3 | `HW/DISPLAY_SMALL_SCREEN_OPTIONS.md` §3.1 "触控/背光" 行 |
| **P0** | demo 阶段点亮屏的办法: ① 写一个 20 行的小内核驱动 (i2c_driver, compatible 自定义) 把 `0xAD=0x01` + `0xAB/0xAA` 做掉; 或 ② 启动脚本 `i2cset -y 1 0x45 0xad 0x01` + 背光 0xab/0xaa。★**不要用 panel-simple 的 DCS 背光 (0x51)** | §1.2 / §1.4 | 新增 SW 任务 |
| **P1** | `LIGHT_3V3` 预算 150mA → **200mA** (见 §2.4) | §2.3/§2.4 | `HW/netlist_v1.csv` + `HW/RELIABILITY_DESIGN.md` §3 (3) |
| **P1** | **R-F1 (LDO dropout) 仍是真风险**: SYS<3.41V 时 LIGHT_3V3/VDD_3V3_IO 失效 ⇒ "用到快没电突然黑屏"; 换小屏**不解决**这个问题 | `HW/RELIABILITY_DESIGN.md` §3 (3) | 已有裁决入口 |
| **P1** | 屏座: demo 15 位/1.0mm; 若要保留 4-lane 能力 ⇒ 按 §4.3 方案 A 加 24 位/0.5mm 4-lane 座 | §1.6 | `HW/DISPLAY_SMALL_SCREEN_OPTIONS.md` §4.3 |
| **P1** | 采购硬判据: 视崖 0.49" 必须支持**非 DSC** 模式 | §3.3 | `HW/STEP1_PARTS_SPEC.md` / RFQ |
| **P2** | 屏的 **RESET 脚没有** ⇒ 屏不回初始化只能重新上电 | 15 针表 | 已知风险, 记台账 |
| **P2** | 屏的**驱动 IC 型号** 仍未查到 ⇒ 不能确定能否用 Rockchip 内核的 `densitron,dmt028vghmcmi-1a` 兜底 (§1.7) | §1.7 | 实测清单 |

---

## 5. 证据清单

| 编号 | 来源 | 用途 | 类型 |
|---|---|---|---|
| [R1] | 树莓派官方内核 `drivers/gpu/drm/panel/panel-waveshare-dsi.c` @ `raspberrypi/linux` 分支 `rpi-6.12.y` (并 diff 了 `rpi-6.18.y`) · commit `d8e5eb49991de6b8fa9231532a11036e24aa84de` (2023-04-14, Dave Stevenson) · <https://github.com/raspberrypi/linux/blob/rpi-6.12.y/drivers/gpu/drm/panel/panel-waveshare-dsi.c> | 2.8" 时序/lane/format/flags + I2C 控制序列 + "无 DCS init" 结论 | `[官方]` |
| [R2] | 树莓派官方 firmware `boot/overlays/vc4-kms-dsi-waveshare-panel.dtbo` @ `raspberrypi/firmware` master · <https://github.com/raspberrypi/firmware/blob/master/boot/overlays/vc4-kms-dsi-waveshare-panel.dtbo> | 面板 I2C 地址 0x45 / 触摸 0x14 / `waveshare,2.8inch-panel` compatible | `[官方]` + `[实测]`(解 DTB) |
| [R3] | Waveshare 官方 wiki「2.8inch DSI LCD」中/英 · <https://www.waveshare.com/wiki/2.8inch_DSI_LCD> · <https://www.waveshare.net/w/index.php?title=2.8inch_DSI_LCD&action=raw> | 15 针表 / "支持软件控制背光亮度" / `dtoverlay=vc4-kms-dsi-waveshare-panel,2_8_inch` | `[官方]` |
| [R4] | Waveshare 官方商品页 (SKU 22028) · <https://www.waveshare.com/product/2.8inch-dsi-lcd.htm> | 规格表字段 (确认**无**电流/功耗字段) | `[官方]` |
| [R5] | Rockchip 官方内核 `develop-6.12` `drivers/gpu/drm/rockchip/dw-mipi-dsi-rockchip.c` (`rk3572_chip_data`: max_data_lanes=4 / 1.8Gbps / compatible `rockchip,rk3572-mipi-dsi`; DSC 读取路径) | 2-lane 可行 + DSC 只是"上报"不是"编码" | `[官方]` |
| [R6] | Rockchip 官方内核 `develop-6.12` `drivers/gpu/drm/bridge/synopsys/dw-mipi-dsi.c` (:339 lane 换算 / :923 N_LANES / :1108 非连续时钟 / **全文无 dsc**) | lane 数机制 + **DSI TX 无 DSC** | `[官方]` |
| [R7] | Rockchip 官方内核 `develop-6.12` `drivers/gpu/drm/rockchip/rockchip_vop2_reg.c` (`rk3572_vop` 无 `.nr_dscs` vs `rk3588_vop` `.nr_dscs = 2`) + `rockchip_drm_vop2.c` (`rk3588_vop2_dsc_*`) | **RK3572 无 DSC 编码器** | `[官方]` |
| [R8] | Rockchip 官方内核 `develop-6.12` `drivers/gpu/drm/rockchip/dw-mipi-dsi2-rockchip.c` (`:2261 rk3576 {.dsc=false}` / `:2271 rk3588 {.dsc=true}`) | Rockchip 官方 per-SoC DSC 能力标志 | `[官方]` |
| [R9] | Rockchip 官方内核 `develop-6.12` `drivers/gpu/drm/panel/panel-simple.c` (`struct panel_cmd_header` @:56 / `panel_simple_of_get_desc_data` @:5450, init/exit 序列可选 + `panel-timing`/`display-timings` / `dsi,lanes` @:5844 / `"simple-panel-dsi"` .data=NULL @:5796 / `panel_simple_dsi_probe`) | Rockchip init 序列格式 + 属性可选性 + dts 写法 | `[官方]` |
| [R10] | Rockchip 官方内核 `develop-6.12` `drivers/video/of_display_timing.c` (`clock-frequency`/`hactive`/`hfront-porch`… 绑定) + `drivers/gpu/drm/drm_modes.c` (`drm_display_mode_from_videomode`: `clock/1000`) | `panel-timing` 节点的属性名与单位 | `[官方]` |
| [R11] | Rockchip 官方内核 `develop-6.12` `arch/arm64/boot/dts/rockchip/rk3576-evb.dtsi:261` (`dsi_panel` 节点) | 我们本地 `HW/PCB/panel_simple_dsi_template.dtsi` 的出处 | `[官方]` |
| [R12] | Rockchip 官方内核 `develop-6.12` `arch/arm64/boot/dts/rockchip/rk3572.dtsi:3260` (`dsi@276d0000`, compatible `rockchip,rk3572-mipi-dsi`) | RK3572 只有一个 DSI 控制器 | `[官方]` |
| [R13] | Rockchip 官方内核 `develop-6.12` `drivers/gpu/drm/panel/panel-sitronix-st7701.c` (`densitron,dmt028vghmcmi-1a`: 480×640/2-lane + 完整 GIP + 电源域) | §1.7 兜底 + §2.2 电流锚点 | `[官方]` |
| [R14] | RK3572 Datasheet V1.1 (本地 `HW/RK3572_PIN_TABLE/RK3572_datasheet_V1.1.pdf` + 文本 `rk3572_datasheet_V1.1.txt` L575 / L647-649) | "One MIPI DSI1.2, up to 4lane*2.5Gbps" / "4 data lanes" / 全文无 DSC | `[官方]` |
| [R15] | `include/drm/drm_mipi_dsi.h` (Rockchip develop-6.12): `MIPI_DSI_MODE_VIDEO=BIT(0)` / `MIPI_DSI_MODE_VIDEO_HSE=BIT(4)` / `MIPI_DSI_CLOCK_NON_CONTINUOUS=BIT(10)` / `MIPI_DSI_FMT_RGB888` | dts 标志位与格式枚举 | `[官方]` |

---

## 6. 未查到清单 (★查不到就是查不到, 不编)

| 未查到的项 | 试过的 URL / 途径 | 结论 |
|---|---|---|
| ★**这块屏的 DCS init 序列** | 树莓派官方内核 (全 109 个 panel 文件里只有 `panel-waveshare-dsi.c` / `-v2.c` 命中 "waveshare"; `rpi-6.12.y` 与 `rpi-6.18.y` 均已逐行读过) | **不是"查不到", 是"确认不存在"** —— 官方驱动零 DSI 写, 面板靠模组内 MCU 自初始化 |
| ★**背光电压/电流/功耗** | [R3] wiki 中/英 · [R4] 商品页 · 同族 4inch/3.4inch/5inch 商品页 · 3D 图 zip | **官方未公布** ⇒ §2.3 标 `[推断]` |
| 屏的**驱动 IC 型号** | 商品页 / wiki / 3D STEP (PRODUCT 名只有 `2_8INCH-480X640-LCD` / `2_8INCH-DSI-LCD-PCBA`) | 未查到 ⇒ 不能断定能不能用 ST7701 兜底 |
| 屏侧 FPC **连接器料号** | wiki / 商品页 / 3D zip | 未查到 (沿用 `DISPLAY_SMALL_SCREEN_OPTIONS.md` 的结论) |
| **屏的物理显示区尺寸 (mm)** | 商品页 / wiki | 官方未给 ⇒ §1.5 的 `width-mm/height-mm` 标 `[推断]` (几何推算) |
| 触摸 **I2C 地址是否可用 DIP 开关改** | wiki 只在旧版 `.ko` 安装步骤里提 "I2C拨码开关" (`WS_xinchDSI_MAIN.sh 28 I2C0`), 没给说明 | 未查到 |

---

> **本文件到此结束。** 只写了 `HW/PCB/WAVESHARE_2P8_INIT_AND_BACKLIGHT.md` 一个文件; 网表 / 板文件 / issue_log / tracker / STATE.yaml / 其它交付物 **全部未改**。§4 的待办需要裁决人另行拍板。
