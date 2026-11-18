# SW/DEMO_PANEL_WAVESHARE_2P8_SPEC.md —— demo 显示侧真源规格 (Waveshare 2.8inch DSI LCD, SKU 22028)

> **交卷人**: 软件总工 (sw-lead, 拿延迟说话) 💻 · **日期**: 2026-11-15 · **单号**: ISS-212 (闭环 `demo_od_p0_4_panel_init_code`)
> **依据**: 老板 **2026-11-04 01:19 拍板 demo 屏 = Waveshare 2.8inch DSI LCD (SKU 22028)** ⇒ 本文件把 demo 显示侧口径从「**整机屏 视涯 0.49" 1920×1080 (整机路线·暂缓)**」**重锚到 demo 屏真实那一块**。
> **本单性质**: ★**只出规格 + 逐处定性 + 机器门禁** —— **不改网表 / 不改板 / 不改 `HW/` 任何文件**。
> **写入边界**: 本单只写 `SW/DEMO_PANEL_WAVESHARE_2P8_SPEC.md` (本文件) · `SW/DEMO_PANEL_SPEC_TRIAGE.md` (新建) · `SW/DEMO_OD_PIPELINE_SPEC.md` (★**只改定性表判成 demo 活动口径的那几处**) · `SW/tools/check_demo_panel_spec.py` (新建) · `HANDOFF/2026-11-15_sw-lead_ISS212_*.md` · 自己分片 `state/fragments/sw.yaml` (走 `state/frag_write.py`)。
> **未改**: `HW/` 下任何文件 (含 `HW/PCB/WAVESHARE_2P8_INIT_AND_BACKLIGHT.md` / `HW/DISPLAY_SMALL_SCREEN_OPTIONS.md` —— **只引用, 一个字未改**) · `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/PCB/demo_mainboard.kicad_pcb` / `demo_mainboard.kicad_pro` · `state/gen_*.py` · `state/issue_log.yaml` · `PROJECT_TRACKER.md` §0 · `state/outbox/` · 别人的分片 · `SW/DEMO_OD_TIMING_SPEC.md` / `SW/SW_TIMING_REVIEW.md` / `SW/RKNN_BENCH.md` / `SW/DEMO_BOARD_60MS_VERDICT_PLAN.md` (ISS-205/207/210 已验证件, 碰了就是回退)。
> **零外发**: 本单**未发任何邮件 / 询价 / 问询 / 采购** (老板 2026-11-11 19:31 + 2026-11-12 02:02) ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案。
> **证据等级**: `[官网]` ≡ `[官方]` (厂商官网 / 官方内核源码 / 官方 wiki) · `[实测]` (本机脚本级或 grep 级真值; **本单无任何实物测量**) · `[媒体]` · `[推算]` (由官方事实推导, 非官方原文) · `[0数据]` (查不到)。

---

## 0 一页纸结论

| # | 结论 | 关键数字 | 证据 |
|---|---|---|---|
| **Q-1** | ★★**demo 屏 = Waveshare 2.8inch DSI LCD (SKU 22028)**: **480×640 / MIPI-DSI 2-lane / 15p 1.0mm FPC / 3V3 (pin14+15) / 模组内供背光** | 刷新率 **60.85 Hz** (50 MHz ÷ (830×990)) | `[官网]` (Waveshare 官方 wiki 逐针表 + 商品页 + 树莓派官方内核 `ws_panel_2_8_mode`) |
| **Q-2** | ★★**这块屏不需要任何 DCS init 序列** —— 树莓派官方内核 `panel-waveshare-dsi.c` **一条 DSI 指令都不发**; 面板与背光全走 **I2C (模组内 MCU)**: probe `0xC0/0xC2/0xAC` · enable `0xAD=0x01` · disable `0xAD=0x00` · 背光 `0xAB`+`0xAA` | ⇒ **demo 阶段 1 直接上真面板**, 「等 init 序列」这道闸**对 demo 屏不成立** | `[官网]` (官方驱动源码, 本单 2026-11-15 23:4x 亲自拉取复核) |
| **Q-3** | ★**软件侧 DSI 必须配 2-lane** —— 板侧座引出 4 lane + CK, 但**屏侧物理只有 2 对差分** (15p: DN0/DP0 + DN1/DP1 + CK) ⇒ 板上的 lane2/lane3 是给**将来整机屏**留的 | payload **448.6 Mbps** @60.85 Hz RGB888 ⇒ **224.3 Mbps/lane** (RK3572 驱动上限 1.8 Gbps/lane ⇒ 余量 8.0×) | `[官网]` (屏侧逐针表 + 官方驱动 `lanes = 2`) + `[推算]` (带宽) |
| **Q-4** | ★★**I2C_B 是面板控制总线, 且速率上限已被物理卡死: ≤100 kHz** —— I2C_B = 4.7k 上拉 @ `RAIL_VDD_3V3_IO` (3.3V) ⇒ **t_r@300pF = 1194.7 ns > 1000 ns** ⇒ 标准模式不通过 | 屏 MCU **0x45** · 触摸 GT911 **0x14** (demo 不接) · TMP117 **0x48** 同总线不冲突 | `[实测]` (本机 `python3 SW/tools/timing_check.py --only F3_i2c_rise`, 2026-11-15 23:5x) |
| **Q-5** | ★**显示侧不再是 60ms 账本的瓶颈** —— 合成段像素数从 2.07 Mpx 降到 **0.307 Mpx (÷6.75)** ⇒ `t_compose` [推算] **3.0 ms → ~0.44 ms**; TX 物理下限从 7.776 ms 降到 **2.304 ms** (同 `HW/e2e_budget_rk3572.py` §⑥ 口径) ⇒ 显示输出侧合计 **10.09 ms → ~2.75 ms** | 余量从「合成段只剩 2.32 ms」放宽到 **7.79 ms** | `[推算]` (按像素数线性缩放 + 官方带宽口径) |
| **Q-6** | ★**整机视涯 0.49" 在 RK3572 上不可用 (整机路线·暂缓)** —— RK3572 **没有 DSC 编码器** (DSI TX 内核全文无 `dsc`; VOP2 只有 RK3588 有 `.nr_dscs = 2`) ⇒ 视涯 0.49" 的 **VESA DSC 3:1** 模式在 RK3572 上出不来 ⇒ 整机屏路线要么换 SoC, 要么要求面板支持**非 DSC** 模式 | 非 DSC 模式 payload = 1920×1080×24×60 = **2986 Mbps** ⇒ 4-lane 够 | `[官网]` (Rockchip 官方内核) + `[推算]` |
| **Q-7** | ★**留了机器门禁**: `SW/tools/check_demo_panel_spec.py` (rc=0 = 全过; 失败点名哪一条; 带 `--selftest` 反向用例) | 4 组判据 + 5 个反向用例 | `[实测]` (脚本级) |

---

## 1 屏本体规格 (demo 活动口径)

| 项 | 值 | 证据 |
|---|---|---|
| 型号 / 料号 | **Waveshare 2.8inch DSI LCD**, Part No. "2.8inch DSI LCD", **SKU 22028** | `[官网]` 商品页 + `HW/DISPLAY_SMALL_SCREEN_OPTIONS.md` §3.1 |
| 分辨率 | **480 × 640** (硬件分辨率) | `[官网]` 官方 wiki Features "hardware resolution of 480×640" + 官方驱动 `hdisplay=480 / vdisplay=640` |
| 面板类型 | **IPS**, 光学贴合 (optical bonding), 5 点电容触摸, 钢化玻璃 (硬度 6H) | `[官网]` 官方 wiki Features |
| 视角 | **160°** | `[官网]` 官方商品页规格表 |
| 显示接口 | **MIPI-DSI (D-PHY)**, **2-lane** + CK | `[官网]` 15p 逐针表 + 官方驱动 `lanes = 2` |
| 触摸接口 | **I2C** (5 点电容) | `[官网]` 官方 wiki |
| 屏侧连接器 | **15 位 / 1.0mm FPC** | `[官网]` 官方商品页 Package Content "15PIN 1.0 pitch" |
| 供电 | **3V3** (pin14 = 3V3, pin15 = 3V3) | `[官网]` 官方 wiki 逐针表 |
| 背光 | ★**无独立背光脚** ⇒ 模组内从 3V3 取电, **由模组内 MCU 经 I2C 调光** | `[官网]` 逐针表 (15 脚里无背光脚) + 官方驱动 commit 正文 "all using a common MCU to control the panel and backlight" |
| RESET 脚 | ★**没有** ⇒ 屏不回初始化时只能重新上电 | `[官网]` 逐针表 (15 脚里无 RESET) |
| TE 脚 | ★**没有** ⇒ **不能做 TE 同步**, 撕裂只能靠刷新率错开 | `[官网]` 逐针表 |
| 物理显示区 | ★**官方未公布** ⇒ 按 2.8" 对角 71.1 mm + 3:4 推算 ≈ **42.7 × 56.9 mm** (dts 写 `width-mm=43 / height-mm=57`) | `[推算]` (官方未给, 几何推算) |
| ★**官方驱动里 `width_mm=154 / height_mm=86` 是该驱动的通用常量, 不是 2.8" 的真实尺寸** ⇒ 不许照抄 | — | `[官网]` (驱动 `ws_panel_get_modes()` 硬编码) |

### 1.1 时序 (逐字抄官方驱动, 没有任何"按经验改")

| 项 | 值 | 来源 |
|---|---|---|
| pixel clock | **50000 kHz** | `[官网]` `ws_panel_2_8_mode.clock = 50000` |
| hdisplay / hsync_start / hsync_end / htotal | **480 / 630 / 680 / 830** | `[官网]` 同上 (`480+150` / `480+150+50` / `480+150+50+150`) |
| vdisplay / vsync_start / vsync_end / vtotal | **640 / 790 / 840 / 990** | `[官网]` 同上 (`640+150` / `640+150+50` / `640+150+50+150`) |
| **刷新率** | **50e6 ÷ (830×990) = 60.849 Hz** | `[推算]` (由官方时序算得) |
| DSI 格式 | **RGB888** (`MIPI_DSI_FMT_RGB888`), bpc 8 | `[官网]` 驱动 `ts->dsi->format = MIPI_DSI_FMT_RGB888` |
| DSI 模式标志 | `MIPI_DSI_MODE_VIDEO_HSE \| MIPI_DSI_MODE_VIDEO \| MIPI_DSI_CLOCK_NON_CONTINUOUS` | `[官网]` 驱动 `ws_panel_2_8_data.mode_flags` |
| lane 数 | **2** | `[官网]` 驱动 `ws_panel_2_8_data.lanes = 2` |

---

## 2 帧率与 lane 口径 (板侧 4 lane vs 屏侧 2 lane ⇒ 软件配几 lane)

| 项 | 结论 | 证据 |
|---|---|---|
| **SoC 能力** | RK3572 **原生 4-lane** MIPI-DSI 1.2 (`max_data_lanes = 4`, 驱动上限 1.8 Gbps/lane) ⇒ 2-lane 是**少用**不是不支持 | `[官网]` Rockchip 官方内核 `dw-mipi-dsi-rockchip.c` (`rk3572_chip_data`) |
| **屏侧物理** | ★**只有 2 对差分** (15p: `DSI1_DN0/DP0` @8/9 · `DSI1_DN1/DP1` @2/3 · `DSI1_CN/CP` @5/6) ⇒ **4-lane 对这块屏不是"软件选择", 是物理不存在** | `[官网]` 官方逐针表 |
| **⇒ 软件口径** | ★**`dsi,lanes = <2>`**; 板上的 `DSI_D0_D2/D3` (CONN_LIGHT_1 pin16~19) 是**给将来整机屏留的**, demo 阶段闲置 | `[推算]` + `HW/PCB/PI5_DSI_22P_PINOUT.md` |
| **带宽** | payload = 480×640×24×60.849 = **448.6 Mbps** ⇒ 2 lane 时 **224.3 Mbps/lane** ⇒ 相对 1.8 Gbps/lane **余量 8.0×** | `[推算]` |
| **TX 物理下限** | 口径 A (同 `HW/e2e_budget_rk3572.py` §⑥: 2 lane × 2.0 Gbps × 80% 效率 = 3200 Mbps 有效) ⇒ **2.304 ms/帧**; 口径 B (驱动上限 1.8 Gbps/lane × 2 lane, 100%) ⇒ **2.048 ms/帧** | `[推算]` (对照: ★**整机屏 1080p** 同口径 = 7.776 ms · 整机路线·暂缓) |
| **帧率对齐** | 面板 **60.85 Hz**, 源 60 fps ⇒ **无 TE 脚** ⇒ 只能靠"源帧率与面板刷新率错开"或"每帧整帧提交"避撕裂; demo 阶段**不做 TE 同步** | `[官网]` (无 TE 脚) + `[推算]` |
| **接线** | ★**板不改**: 屏接板用 **Waveshare 官方 `DSI-Cable-12cm`** (Type A/B = **15pin↔22pin**, Type C = dual-plug 22pin) ⇒ 板上的 22p 座 (Pi5 DISPLAY 针序) 直接插官方线 | `[官网]` 官方排线页 + `HW/DISPLAY_SMALL_SCREEN_OPTIONS.md` [S3] |

---

## 3 ★★「无 DCS init 序列」这条结论 (附官方驱动出处)

**结论**: ★★**这块屏不需要任何 DCS init 序列** ⇒ `panel-init-sequence` **故意不写** ⇒ 不存在"抄错一条寄存器把屏烧了"的风险, 也不存在"等 init 序列"这道闸。

### 3.1 官方驱动做了什么 (逐条照抄, 一条不漏)

| 阶段 | 官方驱动动作 | 出处 |
|---|---|---|
| **probe** | `ws_panel_i2c_write(ts, 0xc0, 0x01);` / `0xc2, 0x01` / `0xac, 0x01` | `[官网]` `ws_panel_probe()` |
| **enable** | `ws_panel_i2c_write(ts, 0xad, 0x01);` (★仅 13.3" 2-lane 档位用 `0x02`; 2.8" 走 `0x01`) | `[官网]` `ws_panel_enable()` |
| **disable** | `ws_panel_i2c_write(ts, 0xad, 0x00);` | `[官网]` `ws_panel_disable()` |
| **背光** | `ws_panel_i2c_write(ts, 0xab, 0xff - backlight_get_brightness(bl));` 然后 `ws_panel_i2c_write(ts, 0xaa, 0x01);` | `[官网]` `ws_panel_bl_update_status()` |
| **DSI 侧** | `ts->dsi->mode_flags = ...; ts->dsi->format = MIPI_DSI_FMT_RGB888; ts->dsi->lanes = 2;` | `[官网]` `ws_panel_probe()` |
| **DSI 写操作** | ★**全文件零次** `mipi_dsi_dcs_write*` / `mipi_dsi_generic_write` ⇒ **官方从未给这块屏发过任何 DCS 指令** | `[官网]` (本单 2026-11-15 23:4x 亲自拉取源码全文复核) |

### 3.2 官方出处 (可复查)

| 编号 | 出处 |
|---|---|
| **[R1]** | 树莓派官方内核 `raspberrypi/linux` 分支 `rpi-6.12.y` · `drivers/gpu/drm/panel/panel-waveshare-dsi.c` · 首次提交 commit **`d8e5eb49991de6b8fa9231532a11036e24aa84de`** (2023-04-14, Dave Stevenson) · <https://github.com/raspberrypi/linux/blob/rpi-6.12.y/drivers/gpu/drm/panel/panel-waveshare-dsi.c> · ★**本单亲自拉取原文逐条复核** (`web_fetch` raw, 2026-11-15 23:4x) |
| **[R2]** | 树莓派官方 firmware `boot/overlays/vc4-kms-dsi-waveshare-panel.dtbo` (master) ⇒ 面板 I2C **0x45** / 触摸 GT911 **0x14** · <https://github.com/raspberrypi/firmware/blob/master/boot/overlays/vc4-kms-dsi-waveshare-panel.dtbo> (本项目已实测解 DTB 留档, 见 `HW/PCB/WAVESHARE_2P8_INIT_AND_BACKLIGHT.md` [R2]) |
| **[R3]** | Waveshare 官方 wiki「2.8inch DSI LCD」· <https://www.waveshare.com/wiki/2.8inch_DSI_LCD> ⇒ 15 针表 / "Supports software control of backlight brightness" / 官方接线说明 (Pi5 走 **DSI Cable-12cm**) · ★**本单亲自拉取复核** |
| **[R4]** | Waveshare 官方商品页 (SKU 22028) · <https://www.waveshare.com/product/2.8inch-dsi-lcd.htm> ⇒ 480×640 / DSI / IPS / 160° / 电容触摸 / 5 点 / I2C 触摸口 · ★**本单亲自拉取复核** (官方 DSI 对照表内 "2.8inch DSI LCD — 480×640 — DSI — IPS — 160° — Capacitive — I2C") |
| **[R5]** | Waveshare 官方排线页 · <https://www.waveshare.com/product/dsi-cable-12cm.htm> ⇒ DSI-Cable-12cm-A/B = **15pin↔22pin**, -C = dual-plug 22pin · ★**本单亲自拉取复核** |

### 3.3 对 SW 的直接后果

1. **demo 阶段 1 就能上真面板** —— 不需要任何"先拿 init 序列"的等待期。
2. **不做 DCS 背光** —— ★**不许**用 `panel-simple` 的 DCS 0x51 调光 (本屏不认) ⇒ 走 I2C `0xAB`+`0xAA`。
3. **`panel-init-sequence` / `panel-exit-sequence` 故意省略** —— Rockchip 的 `panel_simple_of_get_desc_data()` 在属性不存在时**一条都不发且不报错** ⇒ 漏写不会黑屏。
4. **不需要写 `backlight = <&backlight>`** —— 不写时内核会自己注册一个 DCS 背光设备, 写 0x51 会被本屏忽略, 无害; **本屏亮度必须由 SW 走 I2C 控**。

---

## 4 I2C 面板控制序列 (地址 / 速率 / 背光 / 触摸)

### 4.1 地址

| 设备 | 7-bit 地址 | 状态 | 证据 |
|---|---|---|---|
| **Waveshare 2.8" 模组内 MCU (面板 + 背光)** | **0x45** | **本板在挂** (I2C_B) | `[官网]` [R2] (`panel_disp1@45`) |
| **触摸 GT911 (Goodix)** | **0x14** | ★**demo 不接** (可选) | `[官网]` [R2] (`goodix@14`) |
| TMP117 温度计 | 0x48 | 同在 I2C_B ⇒ **不冲突** (0x48 ≠ 0x45) | `[实测]` `HW/I2C_ADDR_TABLE.md` + 网表 |

### 4.2 ★★ 硬上限: I2C_B ≤ 100 kHz (面板 bring-up 的速率天花板)

| 项 | 值 | 证据 |
|---|---|---|
| I2C_B 上拉 | **4.7 kΩ** → `RAIL_VDD_3V3_IO` (**3.3 V**) | `[实测]` 网表 `R_PU_I2CB_SCL_1/SDA` (L235/L236) |
| 走线 | 走 **CONN_LIGHT_1 22p FPC** ⇒ **有线容** (按 300pF 判) | `[实测]` 网表 + `SW/SW_TIMING_REVIEW.md` §6 |
| t_r @100pF | **398.2 ns** | `[实测]` 本机 `python3 SW/tools/timing_check.py --only F3_i2c_rise` (2026-11-15 23:5x) |
| **t_r @300pF** | **1194.7 ns > 1000 ns** ⇒ **标准模式 (100 kHz) 不通过** | ★同上 |
| ⇒ **速率上限** | ★**I2C_B 必须 ≤ 100 kHz** (面板控制总线 = I2C_B ⇒ 这条直接卡住面板 bring-up 的 I2C 速率) | ★同上 |
| 对照: I2C_A | 2.2 kΩ / 1.8 V ⇒ 559 ns@300pF ⇒ 标准模式过, 但快模式 400 kHz 仍不行 (559 > 300) ⇒ **所有 I2C 总线统一 ≤ 100 kHz** | ★同上 |
| **怎么落到软件** | ① 设备树 i2c 节点 `clock-frequency = <100000>;` ② 用户态 `i2cset`/`i2cdetect` 跑在适配器速率上 (不高于 100 kHz) | `[推算]` + Rockchip 官方内核 `i2c-core` 绑定 |

### 4.3 面板控制序列 (demo 阶段直接可用的最小集)

```bash
# ① 探测 (屏在不在)
i2cdetect -y <bus>            # 期望: 0x45 (与 TMP117 0x48 同一条总线)

# ② probe 三写 (官方驱动 ws_panel_probe 顺序)
i2cset -y <bus> 0x45 0xc0 0x01
i2cset -y <bus> 0x45 0xc2 0x01
i2cset -y <bus> 0x45 0xac 0x01

# ③ 点亮 (面板使能)
i2cset -y <bus> 0x45 0xad 0x01

# ④ 背光 (★官方极性: 0xAB = 0xFF - 亮度 ⇒ 0xAB=0x00 最亮, 0xAB=0xFF 最暗)
i2cset -y <bus> 0x45 0xab 0x00     # 最亮
i2cset -y <bus> 0x45 0xaa 0x01     # 背光生效

# ⑤ 熄屏
i2cset -y <bus> 0x45 0xad 0x00
```

> ★**`<bus>` = I2C_B 在 Linux 里的 bus 号** —— 取决于板级 dts 的 `aliases` / 控制器顺序, **本单 [0数据]** ⇒ 用 §8 的 "扫全部 i2c 控制器"办法定位 (找同时能看到 0x45 与 0x48 的那条)。
> ★**生产实现建议**: 写一个 ~20 行内核小驱动 (`i2c_driver` + 自定义 compatible) 把 `0xAD=0x01` + `0xAB/0xAA` 做掉并注册 `BACKLIGHT_RAW` 背光设备 (官方口径); demo 阶段用上面的 `i2cset` 脚本即可, **两者都要求 I2C ≤ 100 kHz**。

---

## 5 dts 片段怎么用 (Rockchip 侧)

> ★**时序/格式/模式标志逐字抄官方驱动**; ★**属性名用 Rockchip 自家绑定** (`drivers/video/of_display_timing.c`: `clock-frequency` / `hactive` / `hfront-porch` / `hback-porch` / `hsync-len` / `vactive` / `vfront-porch` / `vback-porch` / `vsync-len`) —— ★**不是**上游 `clock/hdisplay/...` 那套, 写错属性名内核直接拒绝。
> ★`clock-frequency` 单位 **Hz** (内核 `drm_display_mode_from_videomode()`: `dmode->clock = vm->pixelclock / 1000` ⇒ Hz 进, kHz 出)。

```dts
/*
 * Waveshare 2.8inch DSI LCD  (Part No. "2.8inch DSI LCD", SKU 22028)
 * 480x640 / MIPI DSI 2-lane / 15pin 1.0mm FPC / 3V3 (pin14+pin15) / 模组内供背光
 *
 * 时序/格式/模式标志: 逐字抄树莓派官方内核
 *   drivers/gpu/drm/panel/panel-waveshare-dsi.c  (compatible "waveshare,2.8inch-panel")
 *   commit d8e5eb49991de6b8fa9231532a11036e24aa84de (2023-04-14, Dave Stevenson)
 *
 * ★ 本屏 **不需要 DCS init 序列** (官方驱动零 DSI 写) ⇒ 不写 panel-init-sequence。
 */
&dsi {
	status = "okay";

	dsi_panel: panel@0 {
		status = "okay";
		compatible = "simple-panel-dsi";
		reg = <0>;

		reset-delay-ms     = <10>;
		enable-delay-ms    = <10>;
		prepare-delay-ms   = <10>;
		init-delay-ms      = <10>;
		unprepare-delay-ms = <10>;
		disable-delay-ms   = <60>;

		width-mm  = <43>;    /* [推算] 2.8" 对角 71.1mm, 3:4 ⇒ 42.7 x 56.9mm; 官方未公布 */
		height-mm = <57>;    /* [推算] 同上 */

		dsi,flags  = <(MIPI_DSI_MODE_VIDEO | MIPI_DSI_MODE_VIDEO_HSE |
				MIPI_DSI_CLOCK_NON_CONTINUOUS)>;
		dsi,format = <MIPI_DSI_FMT_RGB888>;
		dsi,lanes  = <2>;    /* ★屏侧物理只有 2 对差分 ⇒ 必须 2 */

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

		/* ★ panel-init-sequence: 故意省略 (官方驱动零 DCS 写, 见 §3.1) */
		/* ★ panel-exit-sequence: 故意省略 (官方驱动无退出序列) */
	};
};

/* ★ 屏控制 I2C (I2C_B): 速率必须 <= 100 kHz (t_r@300pF = 1194.7ns > 1000ns) */
&i2c_B {
	clock-frequency = <100000>;    /* ★硬上限, 不许改 */
	status = "okay";
};
```

★**用法三条**:
1. **不写 `panel-init-sequence`** —— 官方驱动零 DCS 写, 属性不存在时内核一条都不发且不报错 ⇒ 漏写不会黑屏。
2. **不写 `backlight = <&backlight>`** —— 写了会走 DCS 0x51 调光, **本屏不认** ⇒ 亮度由 SW 走 I2C `0xAB`+`0xAA` 控 (§4.3)。
3. **lane 数写 2** —— 板侧 lane2/lane3 (`CONN_LIGHT_1` pin16~19) 在 demo 阶段闲置, 留给将来整机屏。

---

## 6 Rockchip ST7701 GIP 可参照件 (兜底, 不可直接套)

| 项 | 值 | 证据 |
|---|---|---|
| 可参照件 | `drivers/gpu/drm/panel/panel-sitronix-st7701.c` 的 **`densitron,dmt028vghmcmi-1a`** —— **同分辨率 480×640 + 同 lane 数 2-lane**, 完整 GIP 序列写在 .c 里 | `[官网]` Rockchip 官方内核 |
| ★**但它不是这块屏的序列** | 时序明显不同: Waveshare (RPi 官方) clock 50000 kHz / htotal 830 / vtotal 990 / 60.85 Hz **vs** Densitron clock 22325 kHz / htotal 544 / vtotal 698 / ≈58.8 Hz | `[官网]` + `[推算]` |
| ⇒ 结论 | ★**不要混用**; 只有当实测确认这块屏的驱动 IC 确为 ST7701 且兼容时, 才考虑改用该档位 (**那样连 dts 时序都要换成它的**) | `[推算]` |
| 屏的驱动 IC 型号 | ★**[0数据]** —— 官方商品页 / wiki / 3D 图都没有 ⇒ 兜底路线成立与否**板端实测才知道** | `[0数据]` (试过的 URL 见 `HW/DISPLAY_SMALL_SCREEN_OPTIONS.md` §7) |

---

## 7 显示几何 (letterbox / 框宽 / 显存) —— demo 活动口径

### 7.1 letterbox 账 (面板是 **3:4 竖屏**, 源是 **16:10 横屏** ⇒ 黑边方向翻转)

| 路径 | 源帧 | k | 内容区 | 黑边 |
|---|---|---|---|---|
| **P1** (AR0234CS 全幅) | 1920×1200 (16:10) | **0.25** (min(480/1920, 640/1200)) | **480×300** | ★**上下各 170 px, 左右 0** |
| **P2** (复用锁定 ISP 链) | 640×480 (4:3) | **0.75** | **480×360** | ★**上下各 140 px, 左右 0** |
| **P3 (可选, 旋转 90°)** | 1200×1920 | 0.3333 | **400×640** | 左右各 40 px |

★**为什么黑边从"左右"变成"上下"**: 面板 480×640 是 **竖屏 3:4 (0.75)**, 源 16:10 是横屏 (1.6) ⇒ 按**宽度**缩 ⇒ 高度富余 ⇒ 黑边在**上下**。
★**P3 (旋转) 是可选项, 默认不旋转** —— 旋转能把黑边从 340 px 压到 80 px, 但会引入一次 90° 旋转 (多一次全帧搬运) ⇒ **配置项 `display.rotate` (默认 0)**, 板端实测再定; ★**本单不替老板拍**。

### 7.2 框宽 (屏变小 ⇒ 框宽必须重算, 否则"框几乎不可见")

| 路径 | k | 屏上目标 ≥2 px | ⇒ 帧坐标系框宽 | 旧口径 (1080p, k=0.9) |
|---|---|---|---|---|
| **P1** | 0.25 | ≥ 2 px | **8 px** (8×0.25 = 2.0) | 3 px → 2.7 px |
| **P2** | 0.75 | ≥ 2 px | **3 px** (3×0.75 = 2.25) | 1 px → 2.25 px |

★**旧口径 (P1 3px / P2 1px) 在 480×640 上会变成 0.75 px / 0.75 px ⇒ 几乎不可见** ⇒ **框宽必须配置化, 且 demo 默认值改为 P1=8 / P2=3**。

### 7.3 显存与合成开销 (显示侧不再是瓶颈)

| 项 | 旧 (整机屏口径·整机路线·暂缓) | 新 (Waveshare 480×640) | 比值 |
|---|---|---|---|
| 画布像素 | 2.0736 Mpx | **0.3072 Mpx** | **÷6.75** |
| NV12 画布内存 | 3.11 MB | **0.44 MB** | ÷7.1 |
| `t_compose` (按像素线性) | 3.0 ms (模型占位) | **~0.44 ms** [推算] | ÷6.75 |
| TX 物理下限 (同口径) | 7.776 ms | **2.304 ms** | ÷3.38 |
| **显示输出侧合计** | **10.09 ms** | **~2.75 ms** | ⇒ ★**60ms 账本里显示侧余量从 2.32 ms 放宽到 7.79 ms** |

> ★**推算口径声明**: `t_compose` 按**像素数线性缩放**推 (每像素成本不变) —— 这是假设不是实测; **板端实测为准** (`SW/DEMO_BOARD_60MS_VERDICT_PLAN.md` 第 7/8 段打点, ISS-210 已备好)。
> ★**本单板端 [实测] = 0 条** (板不在本机)。

---

## 8 ★ 板端到货后 30 分钟验证清单 (每步: 命令 → 期望 → 判据)

> 前提: 屏已用 **Waveshare 官方 `DSI-Cable-12cm` (15pin↔22pin)** 接到板上的 `CONN_LIGHT_1` 22p 座; 板已刷 RK3572 BSP; dts 已按 §5 配好 (`dsi,lanes=2` + `panel-timing` + `clock-frequency=100000`)。
> ★**贯穿全程的判据原则**: 每一步都写"期望看到什么"和"什么算失败" —— 不许"看着像对的"就算过。

| # | 步骤 | 命令 | 期望看到什么 | 判据 (通过 / 失败) |
|---|---|---|---|---|
| **V0** | 供电与地 | 示波器/万用表量 `CONN_LIGHT_1` pin14/15 | **3.3 V** (且 pin1/4/7/10/13 都是 GND) | ✅ 3.3 V ±5% · ❌ 无 3.3 V ⇒ 先查 `LIGHT_3V3` (R-F1 LDO dropout 风险, 见 `HW/RELIABILITY_DESIGN.md`) |
| **V1** | 屏在 I2C 上 | `for b in 0 1 2 3 4 5; do echo "== i2c-$b"; i2cdetect -y $b; done` | ★**有一条总线上同时出现 `0x45` (屏 MCU) 与 `0x48` (TMP117)** | ✅ 找到 `0x45` ⇒ 记下 bus 号 `<bus>` · ❌ 没有 0x45 ⇒ 查转接线方向 (Type A/B 上下反插) / 查 FPC 座 pin11/12 是否真接到 `I2C_B` |
| **V2** | I2C 速率生效 | `dmesg \| grep -i "i2c"` + dts 复查 `clock-frequency = <100000>` | i2c 适配器速率 **100 kHz** | ✅ 速率 ≤ 100 kHz · ❌ 400 kHz ⇒ ★**违反 I2C_B 硬上限 (t_r@300pF=1194.7ns)**, 立刻降速 (面板可能不稳) |
| **V3** | probe 三写 | `i2cset -y <bus> 0x45 0xc0 0x01` (再 `0xc2 0x01`, `0xac 0x01`) | 三条都**无 `-E` / 无 NAK** | ✅ rc=0 · ❌ NAK ⇒ 回到 V1 (地址/接线/供电) |
| **V4** | 点亮 + 背光 | `i2cset -y <bus> 0x45 0xad 0x01` 然后 `0xab 0x00` + `0xaa 0x01` | ★**屏亮起 (背光白)**; 此时**还没有画面**是正常的 (还没送像素) | ✅ 屏亮 ⇒ 模组内 MCU 通路通 · ❌ 不亮 ⇒ 查 `0xAD` 写值 / 背光极性 (`0xAB` = 0xFF − 亮度) / 3V3 |
| **V5** | DRM 侧 mode | `modetest -M rockchip` (或 `cat /sys/kernel/debug/dri/0/state`) | ★**有 480×640 的 mode (60.85 Hz)**; DSI connector 已连上 (`connected`) | ✅ 出现 480×640 · ❌ 只有别的分辨率 ⇒ dts 的 `panel-timing` 没被吃进去 (`dmesg \| grep -i "could not find property"`) |
| **V6** | DSI TX 真的在出 | `modetest -M rockchip -s Rockchip:480x640` (plane 彩条) + `dmesg \| grep -i dsi` | ★**屏上出现彩条**; dmesg 无 DSI 报错 | ✅ 彩条出来 ⇒ **屏上已有画面** (demo 阶段 1 直接成功) · ❌ 屏亮但无画面 ⇒ 查 lane 数 (必须 2) / 格式 (RGB888) / `MIPI_DSI_MODE_VIDEO_HSE` |
| **V7** | 帧率与撕裂 | 静止彩条跑 300 帧, 拍照/录像 | 静止画面**无撕裂、无行错位**; 记录 `fps_display` | ✅ 60.85 Hz 附近稳定 · ❌ 撕裂 ⇒ ★**屏无 TE 脚** ⇒ 只能靠"每帧整帧提交"或降源帧率错开 |
| **V8** | 端到端管线 | demo 程序跑 **≥300 帧** (`SW/DEMO_BOARD_60MS_VERDICT_PLAN.md` 第 7/8 段打点) | ★**框画在物体上**; 黑边**上下各 170 px (P1) / 140 px (P2)**; 9 个打点全有值 | ✅ 框对 + 黑边位置精确 + 打点齐全 · ❌ 黑边位置错 ⇒ letterbox 参数 (`scale/pad_y`) 写错 |
| **V9** | 亮度可调 | `i2cset -y <bus> 0x45 0xab 0x40` + `0xaa 0x01`, 再 `0xab 0xff` | 亮度**明显变暗 → 变亮** | ✅ 亮度随 `0xAB` 变化 ⇒ 背光通路通 · ❌ 无变化 ⇒ 背光不受控 (MCU 固件差异) |

★**30 分钟怎么排**: V0~V4 = **8 分钟** (供电 + I2C + 点亮) ⇒ V5~V6 = **7 分钟** (DRM/DSI) ⇒ V7~V9 = **15 分钟** (帧率 + 管线 + 亮度)。
★**V6 通过 = demo 显示侧验收通过** —— 不需要任何"init 序列"、不需要任何外发。

---

## 9 整机路线占位 (整机路线·暂缓)

<!-- BEGIN 整机路线占位区 (本区允许出现 视涯 / 1920×1080 / init code 等整机口径) -->
> ★**整机路线·暂缓** —— 本区是**整机屏路线**的占位, **不是 demo 活动口径**; demo 活动口径见 §1~§8。

| 项 | 整机路线现状 | 证据等级 |
|---|---|---|
| ★**整机屏** | **视涯 (SeeYA) 0.49" 1920×1080 SiOLED** —— 仍是**整机屏**的既定选型 (老板 11-02 01:12 决定) | `[官网]` (历史决策) · ★**整机路线·暂缓** |
| ★**整机侧关键约束** | 视涯 0.49" datasheet 写 "VESA DSC 3:1" ⇒ ★**RK3572 没有 DSC 编码器** ⇒ **这个屏在 RK3572 上出不来** ⇒ 整机路线要么换 SoC (RK3588 有 `.nr_dscs = 2` / `.dsc = true`), 要么要求面板支持**非 DSC** 模式 (1920×1080@60 RGB888 = 2986 Mbps, 4-lane 够) | `[官网]` (Rockchip 官方内核: DSI TX 内核全文无 `dsc`; VOP2 只有 RK3588 配 `nr_dscs`) + `[推算]` |
| ★**整机侧 init code / 时序** | ★**[0数据]** —— 视涯侧的 DCS init 序列 / 时序 / 单色全彩 / 逐帧延迟, **全部未拿到**; ★**本单不外发** (老板 11-11 19:31 + 11-12 02:02) ⇒ **不许再写"等原厂回信", 更不许写"等放行外发"** | ★**整机路线·暂缓** + `[0数据]` |
| ★**整机侧降级方案 (不许留成外部依赖)** | ① **demo 阶段不依赖视涯**: 显示侧全部按 Waveshare 2.8" 走 (§1~§8) ⇒ 整机选型未决**不阻塞 demo**; ② 整机屏若仍是视涯 ⇒ 采购硬判据加一条「**必须支持非 DSC 的 1920×1080@60 RGB888 DSI 模式**」, 否则 RK3572 方案作废; ③ 若面板厂坚持只给 DSC 模式 ⇒ 整机路线**换 SoC 到 RK3588**; ④ 逐帧延迟 (S10 占位 5.0 ms) ⇒ 整机阶段实测, 不用猜 | ★**整机路线·暂缓** + `[0数据]` / `[推算]` |
| ★**谁拍板** | 整机屏路线 (视涯 vs Waveshare 各走哪条) / 屏的最终选型 / FOV = ★**老板拍板**; ★**本单只做 demo 屏这一半** | — |
<!-- END 整机路线占位区 -->

---

## 10 证据分级汇总

| 级别 | 本单用在哪 | 条数 |
|---|---|---|
| `[官网]` | ★**官方驱动逐条复核** (probe/enable/disable/背光/时序/lane/format/模式标志 + ★**零 DCS 写**) · 官方 wiki 15 针表 (3V3 @14/15 · 无背光脚 · 无 RESET · 无 TE) · 官方商品页 (480×640/DSI/IPS/160°/电容 5 点/I2C 触摸) · 官方排线页 (15pin↔22pin) · 官方 dtbo (0x45 / 0x14) · Rockchip 官方内核 (2-lane 支持 / **RK3572 无 DSC** / ST7701 参照件) | 12 项 |
| `[实测]` | ★**仅脚本级/grep 级** (本机 `timing_check.py --only F3_i2c_rise` 实跑: I2C_B 4.7k/3.3V ⇒ 398.2 ns@100pF / **1194.7 ns@300pF** ⇒ std_mode ❌ ⇒ 速率上限 100 kHz; 网表行级读; 门禁 rc 与自测; md5 逐字节) —— ★**本单无任何实物测量** (板与屏都不在本机) | 6 项 |
| `[推算]` | 刷新率 60.85 Hz · payload 448.6 Mbps / 224.3 Mbps per lane · TX 下限 2.304 / 2.048 ms · letterbox k=0.25 / 0.75 与黑边 170 / 140 px · 框宽 8 / 3 px · `t_compose` ~0.44 ms · 物理显示区 42.7×56.9 mm | 9 项 |
| `[0数据]` | ★**整机屏侧 (整机路线·暂缓)**: DCS init 序列 / 时序 / 单色全彩 / 逐帧延迟 · 屏的驱动 IC 型号 · 屏侧背光电压电流 · I2C_B 在 Linux 里的 bus 号 · 板端一切实测 | 5 项 |
| `[媒体]` | **0 条** (本单零引用媒体源) | 0 |

---

## 11 未查到清单 (★查不到就是查不到, 不编)

| 未查到 | 试过的途径 | 降级方案 |
|---|---|---|
| 屏的**驱动 IC 型号** | 官方商品页 / wiki / 3D 图 (PRODUCT 名只有 `2_8INCH-480X640-LCD` / `2_8INCH-DSI-LCD-PCBA`) | ⇒ 用官方 RPi 驱动口径 (§5 dts 片段) 走, 不依赖驱动 IC; ST7701 兜底**只在实测确认后**才启用 (§6) |
| 屏的**背光电压/电流/功耗** | 官方商品页规格表 (10 个字段, 无电流) / wiki / 同族 4"/3.4"/5" 商品页 / 3D 图 zip | ⇒ 板侧按 `LIGHT_3V3` 轨预算走 (见 `HW/PCB/WAVESHARE_2P8_INIT_AND_BACKLIGHT.md` §2.3 的 [推断] ~70~125 mA); **本单不改网表** |
| 屏的**物理显示区尺寸 (mm)** | 官方商品页 / wiki | ⇒ 用 [推算] 42.7×56.9 mm (dts `width-mm=43 / height-mm=57`) |
| 触摸 **I2C 地址是否可用拨码改** | 官方 wiki 只在旧版 `.ko` 安装步骤提 "I2C 拨码开关" | ⇒ demo 不接触摸, 不影响 |
| **I2C_B 在 Linux 里的 bus 号** | 取决于板级 dts 控制器顺序 (本机无板级 dts) | ⇒ §8 V1 用"扫全部 i2c 控制器, 找同时有 0x45 与 0x48 的那条"定位 |
| ★**整机屏侧全部 init 序列 / 时序 / 单色全彩 / 逐帧延迟** | 见 §9 | ⇒ **降级方案写死** (§9 降级方案 ①②③④) ⇒ **demo 不受影响, 整机路线暂缓** |

---

## 12 与其它单号的接口 (本单改了谁 / 没改谁)

| 文件 | 本单动作 |
|---|---|
| `SW/DEMO_OD_PIPELINE_SPEC.md` | ★**只改定性表判成 demo 活动口径的那几处** (显示分辨率 / letterbox 账 / 框宽 / DRM mode / 面板行 / 两阶段验证法 / 附录 A 的面板 init 序列行) ⇒ 其余一字未动 ⇒ 详见 `SW/DEMO_PANEL_SPEC_TRIAGE.md` |
| `SW/DEMO_PANEL_SPEC_TRIAGE.md` | ★**新建**: 22 处 grep 命中 + 12 处关联活动口径的逐处定性表 |
| `SW/tools/check_demo_panel_spec.py` | ★**新建**: 机器门禁 (4 组判据 + `--selftest` 反向用例) |
| `HW/` | ★**一个字未改** (只引用 `HW/PCB/WAVESHARE_2P8_INIT_AND_BACKLIGHT.md` / `HW/DISPLAY_SMALL_SCREEN_OPTIONS.md` / `HW/PCB/PI5_DSI_22P_PINOUT.md` / `HW/netlist_v1.csv` / `HW/I2C_ADDR_TABLE.md`) |
| `state/fragments/sw.yaml` | ★**只写自己分片** (走 `state/frag_write.py` 原子写): 结掉 need `demo_od_p0_4_panel_init_code` + 登记 artifacts / interface_claims |

> ★**本单纪律声明**: 本单**未修改** `PROJECT_TRACKER.md` / `state/issue_log.yaml` / `state/outbox/` / `HW/` 下任何文件 / `SW/` 下其它已验证件; **未写任何可执行代码** (只写了一个**门禁检查脚本**); **未发任何邮件 / 询价 / 问询 / 采购**; 所有未核项已列入 §11 并标 `[0数据]` + 降级方案, **没有用推断冒充事实**。
