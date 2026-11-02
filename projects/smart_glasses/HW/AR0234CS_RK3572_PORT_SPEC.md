# HW/AR0234CS_RK3572_PORT_SPEC.md —— AR0234CS → RK3572 驱动移植规格 (ISS-144)

| 项 | 内容 |
|---|---|
| 作者 | **hw-lead (硬件总工)** —— 本单第一次真正交付 (前两次派 hw-lead = 0 产出: 第一次 11 分钟烧 442k tokens 文件 mtime 没变; 第二次 16 分钟后 failed) |
| 日期 | 2026-11-02 |
| 触发 | 老板 2026-11-02 19:07 定的 **预研 demo 板方案** (RK3572 + AR0234CS + 视涯 0.49") ⇒ 采集链第一步 = **AR0234CS 在 RK3572 上出 RAW** |
| 上游依据 | `HW/OPEN_SOURCE_AVAILABILITY.md` §2 (五数据源实测) · `HW/SENSOR_SELECTION.md` §B4 · `HW/DISPLAY_SENSOR_CHAIN.md` §2.5 · `SW/DEMO_OD_PIPELINE_SPEC.md` (软件侧路径判断) |
| 本单范围 | ★**只出规格, 不写代码** (大任务拆两步: 先规格后实现) · 证据等级: `[实测]`=本单亲自抓取验证 / `[官方]` / `[推算]` / `[待核]` |
| ★**本单改了什么** | ★**上一版 (19:20, 项目总工自写) 有 3 处硬伤, 本版逐条订正并在 §0 列出** —— 见 §0.2 |

---

## 0. 结论与本版订正

### 0.1 一句话结论

★**AR0234CS 在 Rockchip 侧没有任何现成驱动** (本单实测: 上游主线无 · Rockchip BSP kernel `develop-6.1` 363 个 sensor 驱动里无 · `develop-6.12` 里也无 · rkaiq 公开 iqfiles 里无 IQ 文件) ⇒ **demo 采集链的第一块骨牌是一次真实的驱动移植**。
⇒ ★**好消息: 移植起点是公开的、完整的、GPL-2.0 的** (RPi 版 42KB 驱动 + DT overlay + dkms) ⇒ **这是"移植"不是"从零写"**。
⇒ ★**但更省事的做法在 §6**: demo 板**先用有现成 BSP 驱动 + 现成 ISP3 IQ 的 sensor (IMX415 / OV02B10) 把链路打通**, AR0234CS 后补 ⇒ **可把 demo 关键路径从这条最长路径上挪开**。

### 0.2 ★★ 上一版规格的 3 处硬伤 (本版已订正, 每条都有实测依据)

| # | 上一版写的 | ★**实测真相** | 影响 |
|---|---|---|---|
| **E1** | ★**`opensource206/UC788_AR0234_SENSOR_TO_RK3588` = "RK3588 同族 bringup, 平台差异最小, 优先看它"** | ★**该仓库是空的** —— 本单实拉 GitHub API: 整仓只有 `LICENSE` (GPL-3.0, 35149 B) + `README.md` (**82 B**, 内容仅一句 "Bringup of AR0234 image sensor on RK3588 platform") + **1 star / 0 fork / 总大小 14 KB**。**没有任何驱动代码、没有 DT、没有 IQ** | ★**这是"1 分★★★ + 名字像"的最强伪装"** ⇒ ★**"同族 bringup 可抄"这条判断不成立** ⇒ 移植起点**只剩 S2/S3 两个** ⇒ §2 工作量与 §6 路径判断都要按"无同族参考"重算 |
| **E2** | ★**DT 里 `reg = <0x36>`, 注释"与 TMP117 0x48 不冲突"** | ★**AR0234CS 的 I2C 地址是 `0x10`, 不是 `0x36`** —— 本单实拉三个独立来源交叉验证: ①`Kurokesu/ar0234-rpi-driver` 的 `ar0234-overlay.dts`: `ar0234@10 { compatible = "onnn,ar0234cs"; reg = <0x10>; }` ②`Kurokesu/ar0234-jetson-driver` 的 `tegra234-p3767-camera-p3768-ar0234-A.dts`: `rbpcv3_ar0234_a@10 { compatible = "onnn,ar0234"; reg = <0x10>; }` ③RPi 驱动的 DTS overlay 用同一地址。**`0x36` 是上一代 OV04C10 的地址** (网表 row 153 的 "sensor 0x36" 注释也还是 OV 时代的) | ★**照 0x36 写 ⇒ 板子焊出来 sensor 永远不应答 ⇒ 白投一轮板**。⇒ 本版 §3 改 `0x10`, 并**新增卡点 R7**: ★**网表 I2C 地址冲突注释要同步改 (本单不改网表, 走 need)** |
| **E3** | ★**"RK3572 用 rkisp3 (不是 rkisp1)"** —— 方向对, 但**"BSP kernel 分支 = develop-6.1"** | ★**方向完全正确** (本单实测 RK3572 的 ISP 节点是 `rockchip,rkisp-vir` + `rockchip,rkcif-mipi-lvds` + `rockchip,rkisp-sditf` ⇒ 确属 ISP3 代) ★**但分支号要改**: 本单实拉 → **`arch/arm64/boot/dts/rockchip/rk3572.dtsi` 在 `develop-6.1` 和 `develop-6.6` 上都是 404, 只在 `develop-6.12` 上存在 (159719 B)** ⇒ ★**RK3572 的主线内核基线是 6.12, 不是 6.1** ⇒ ★**移植要落到 6.12 的 `drivers/media/i2c/`** ⇒ 上一版 C1 写的 "BSP kernel 分支 develop-6.1" **会导致改错分支** |

★**另补两条上一版没有、但会直接决定成败的正向实测**: 

★**(a) ISP3 支持 GRBG Bayer 顺序** —— 本单实拉 `drivers/media/platform/rockchip/isp/common.h`, 里面有 `enum { RAW_RGGB=0, RAW_GRBG, RAW_GBRG, RAW_BGGR }`, 且 `isp_params_v3x.c` 的 BLS 通道映射四路全实现 (含 `case RAW_GRBG:`) ⇒ ★**AR0234CS 的 GRBG 输出 (RPi 驱动用的就是 `MEDIA_BUS_FMT_SGRBG10_1X10`) 在 rkisp3 上原生可走** ⇒ **这一条不是风险, 是"已排除的风险"** —— 写进去是为了避免下一个人再去核一遍。

★**(b) ★★ 手上的 Radxa A7S 板 (RK3576) 就是 rkisp3 同一代 ⇒ 驱动移植不必等 RK3572 板** —— 本单实拉对比两个 SoC 的 DTS:
- **RK3572** (目标): `rockchip,rk3572-csi2-dphy` → `rockchip,rkcif-mipi-lvds` → `rockchip,rkisp-vir` → `rockchip,rkisp-sditf`
- **RK3576** (A7S 板, 本单实拉 `rk3576.dtsi`): ★**拓扑逐节点完全同构** —— `rockchip,rk3576-csi2-dphy` → `rockchip,rkcif-mipi-lvds` → `rockchip,rkisp-vir` → `rockchip,rkisp-sditf` ⇒ ★**只有 dphy 的 compatible 字符串带 SoC 名不同, 其余全部一样**
⇒ ★**⇒ C1/C2/C3/C6 (驱动本体 + 寄存器 + 曝光增益 + rkaiq 注册) 全部可以在 A7S 板上先做先验**, 只差 C4/C5 的 SoC 专属 DT 节点名 ⇒ ★**"等 RK3572 板"不构成 C1~C3/C6 的前置** (见 §5 R12)。
⇒ ★**并且 A7S 的内核基线比 RK3572 老**: 实测 `rk3576.dtsi` 在 `develop-6.1` **存在 (200)**, 而 `rk3572.dtsi` 在 `develop-6.1` **不存在 (404)** ⇒ ★**⇒ 驱动代码在 6.1 与 6.12 之间只需要小改 (ISP3 API 6.1 已有 `isp_params_v3x.c`/`common.h`), 两块板可共用同一份 `ar0234.c`** ⇒ ★**这是"先在 A7S 上验证、再迁到 RK3572"这条路可行的硬依据**。

---

## 1. 移植起点 (公开可抄的仓库 —— 逐个实拉验证)

★**本节每一行都是本单亲自拉过仓库/文件后写的**, 不是转述。

| # | 仓库 (本单实拉) | 许可证 | ★**能直接取什么** | ★**要改哪几处 / 能不能直接用** |
|---|---|---|---|---|
| **S1** | `opensource206/UC788_AR0234_SENSOR_TO_RK3588` | GPL-3.0 | ★** NOTHING —— 仓库是空的** | ★**不能用作起点** (E1: 只有 LICENSE + 82 B README) ⇒ ★**它唯一的价值是: 证明"有人试图做 RK3588 同族 bringup 但没做成/没公开" ⇒ 说明这条路没有现成车可抄, 得自己开** |
| **S2** ★★ | `Kurokesu/ar0234-rpi-driver` | ★**GPL-2.0** (API 实测 `spdx_id: GPL-2.0`) | ★**最完整的一份, 本单实测文件清单**: `ar0234.c` (**42761 B** · 完整 V4L2 subdev) + `ar0234-overlay.dts` (2921 B) + `dkms.conf` (368 B) + `dkms.postinst` + `setup.sh` (2841 B) + `Makefile` + `LICENSE` + `docs/`。★**25 stars, 最后 push 2026-10-20** (还在更新) | ★**能直接用, 但框架层要换**: ①它用 **Raspberry Pi 的 `media/v4l2-cci.h` (CCI)** —— `cci_read/cci_write` 全篇用了 **24 处**, Rockchip 内核**没有 CCI** ⇒ ★**这 24 处要改写成 Rockchip 的 `regmap` 写法** (对标 `ov02b10.c` 的 `i2c_smbus`/`regmap`) ②`compatible = "onnn,ar0234cs"` (★**注意是 onnn 不是 onsemi —— 上游自己的拼写**) ③它是 **RPi 单 sensor overlay**, 要改成 RK3572 的 `csi2_dphy` + `rkcif` + `rkisp-vir` 三段链路 ④它**没有 rkmodule ioctl** (`RKMODULE_GET_MODULE_INFO` 等) ⇒ ★**rkaiq 对接要另加 (见 C6)** |
| **S3** ★ | `Kurokesu/ar0234-jetson-driver` | ★**GPL-2.0** (API 实测) | ★**本单实测文件清单**: `nv_ar0234.c` (21150 B, **NVIDIA tegracam 框架**) + ★**`ar0234_mode_tbls.h` (5915 B) —— 这个头文件是本单找到的 ★"最干净的一块可复用资产": 它把 PLL/模式/帧率表按 `camera_common_frmfmt` 结构拆开了, **不含任何框架依赖** ⇒ ★**寄存器时序直接抄它** + `tegra234-*.dts` × 4 (Jetson DT 参考) + `tuning/` 目录 (★**注意: 是 NVIDIA nvcam 的 tuning, 不是 rkaiq IQ ⇒ 不可直接用, 只证明"AR0234 是需要 per-lens tuning 的"**) | ★**框架层完全不能用** (tegracam 是 NVIDIA 私有框架) ⇒ **只取 `ar0234_mode_tbls.h` 的寄存器表 + `tuning/` 的存在性证据** |
| **S4** | `LPXingxing/LI-AR0234CS-STEREO-GMSL2` | ★**无 LICENSE 文件** (API 实测 `license: None`) | Xavier 平台 GMSL2 立体双目驱动 (总大小 50 MB, `Xavier_Driver/` + `34.1.1`/`35.1`/`35.2_GA`/`35.3.1` 四个 L4T 版本) | ★**不能抄 (无许可证 = 无授权)** ⇒ ★**只能当"这块料被多方移植过"的旁证** (与 S5 一起构成 D4=2 分的依据) |
| **S5** | openipc `cameras/sensors/ar0234` | 公开库 (MIT core) | ★**条目真实存在** (本单实拉 HTTP 200, 标题 "onsemi AR0234 image sensor: specifications"; 快照 `HW/_os_snapshots/openipc_sensors.json` 的 896 项清单里确有 `ar0234`) | ★**规格参考** (公开参数 + 各平台驱动索引) |
| **S6** | ★**Rockchip BSP kernel `develop-6.12`** (本单实拉) | GPL-2.0 | ★**这是"骨架"的真正来源, 上一版漏了**: `drivers/media/i2c/ov02b10.c` (35448 B) —— ★**Rockchip sensor 驱动的标准骨架** (见 §2 C1)。★实测 `drivers/media/i2c/ar0234.c` **在 6.12 上是 404 ⇒ 确认无驱动** | ★**直接抄骨架, 只换 sensor 私有部分** |

★**GitHub 命中 20 个仓库 vs OV04C10 的 0 个** (实测, `HW/_os_snapshots/github_repo_counts.json`) ⇒ ★**这是 11-02 09:23「开源数据优先」判据的落点**。

★**本节的真正结论**: ★**能抄的只有 "寄存器时序" (S3 头文件) + "曝光/增益/帧长算法" (S2 驱动) 两块; "Rockchip 框架骨架" 要从 S6 抄; ★**"同族 SoC 的现成 AR0234 移植" = 不存在 (E1)** ⇒ ⇒ **这比上一版说的更接近"从零写一遍", 但不是"从零查寄存器"** —— 差别在于**寄存器时序是现成的**。

---

## 2. 改动清单 (逐项: 改什么 / 依据 / 工作量)

★**工作量口径**: 人日 = 一个熟悉 V4L2 subdev + Rockchip camera 框架的人做完并自测通过。★**不含**"在 RK3572 板子上调通到出图"的时间 (那是 bringup 风险, 归 §5)。

| # | 改动项 | ★**改什么 (具体到文件/函数)** | 依据 | 工作量 |
|---|---|---|---|---|
| **C1** | **V4L2 subdev 驱动骨架** | 新增 `drivers/media/i2c/ar0234.c` (★**落 `develop-6.12`** —— 见 E3)。★**骨架从 `ov02b10.c` 抄**: `struct ar0234` + `v4l2_i2c_subdev_init` + `media_entity_pads_init` (`MEDIA_PAD_FL_SOURCE`) + `media_entity.function = MEDIA_ENT_F_CAM_SENSOR` + `v4l2_async_register_subdev_sensor` + `device_initcall_sync(sensor_mod_init)` (BSP 用 `i2c_add_driver` 而非 `module_i2c_driver`) + `pm_runtime` 三件套 | S6 骨架 + S2 的 `ar0234.c` 私有部分 | ★**2 人日** (比上一版 1.5 涨 0.5: 因为 **S2 的 CCI 层要重写 24 处**, 不是"抄") |
| **C2** | ★**寄存器时序 + 模式表** | ★**直接抄 S3 的 `ar0234_mode_tbls.h`** (`ar0234_pll_config_24_450_10bit[]` / `ar0234_pixclk_45mhz_mfr_settings[]` / `ar0234_mode_1920x1200[]` / `ar0234_mode_960x600[]`) ⇒ 改成 Rockchip 的 `struct regval` 列表 + `supported_modes[]` 格式 (★**对标 `ov02b10.c` 的 `ov02b10_linear10bit_1600x1200_regs`**)。★**必抄的寄存器**: `0x3000` CHIP_ID (`0x0A56` 彩色 / `0x1A56` 单色 —— 校验用) · `0x300A` FRAME_LENGTH_LINES · `0x3012` EXPOSURE_COARSE · `0x305E` DIGITAL_GAIN · `0x3060` ANALOG_GAIN · `0x30BA` MFR (增益档位选择, 写法 `0x7620 | val`) · `0x3022` GROUPED_PARAMETER_HOLD (改 0x30BA 时必须成组) · `0x3354` MIPI_CNTRL · `0x31AC` DATA_FORMAT_BITS (8/10 bit) · `0x0200\|n_lanes` SERIAL_FORMAT (lane 数) | S3 头文件 (GPL-2.0, 可抄) + S2 驱动里的同名寄存器 | ★**1 人日** |
| **C3** | ★**曝光 / 增益 / 帧长控制** | ★**这是 OD 的命门**: 曝光与增益必须可控, 否则自动曝光会把 80 类检测搞崩。★**要落 3 个 V4L2 ctrl**: `V4L2_CID_EXPOSURE` → `0x3012` (★**注意 S2 只写了 coarse, 我们的 `0x3012` 写的是行数 coarse ⇒ 60fps 下 16.7ms/行, 曝光粒度粗 ⇒ 短曝光必须靠 gain 补 —— 要核 onsemi 的 fine exposure 寄存器是否存在 [待核]**) · `V4L2_CID_ANALOGUE_GAIN` → ★**必须抄 S2 的 `ar0234_set_analog_gain()` 那套"按 pixclk 分档"逻辑** (45MHz 档: <0x36 用 gain_bits(6) 否则 (0); 90MHz 档: <0x20→(2) / <0x3A→(1) / else (0) —— ★**因为 0x30BA 增益档位是跟像素时钟绑定的, 换 lane 数就得换档, 直接抄错 ⇒ 画面全灰/全白**) · `V4L2_CID_DIGITAL_GAIN` → `0x305E`。★**帧长**: `V4L2_CID_VBLANK` → `0x300A` (写 `mode->height + vblank - 5`, `AR0234_FLL_OVERHEAD=5`) | S2 `ar0234.c` 的 `set_ctrl` + `ar0234_set_analog_gain()` | ★**1 人日** (上一版 0.5 **严重低估**: 增益的 pixclk 分档逻辑是隐藏坑, 且 fine exposure 要核) |
| **C4** | **DT overlay** | ★**不是"overlay"而是改主 DTS** (RK3572 用 `dtsi`/`evb.dtsi`, 无 RPi 那种 plugin overlay 机制) ⇒ 在 `arch/arm64/boot/dts/rockchip/rk3572-evb.dtsi` 加 sensor 节点 (内容见 §3)。★**★ 可拆成两半做**: ★**先在 A7S (RK3576) 的 DTS 上做一遍** (★**两 SoC 拓扑逐节点同构, 只差 dphy compatible 的 SoC 名** ⇒ 见 §0.2 (b)) ⇒ ★**这样 C4 不必等 RK3572 板, 也不必等 RK3572 的 6.12 DTS 全部核完** | S6 的 RK3572 DTS 拓扑 (本单实拉 `rk3572.dtsi` + `rk3572-evb.dtsi`) + ★**本单实拉 `rk3576.dtsi` 对比** | ★**0.5 人日** |
| **C5** | ★**rkisp3 的 format / 帧率协商** | ★**这是上一版漏得最狠的一项**。★**本单实拉 RK3572 的 ISP 拓扑 (6.12)**: 链路是 **`csi2_dphy` (`rockchip,rk3572-csi2-dphy`) → `rkcif_mipi_lvds` (`rockchip,rkcif-mipi-lvds`) → `rkisp_vir` (`rockchip,rkisp-vir`) → `rkisp_vir*_sditf` (`rockchip,rkisp-sditf`)** ⇒ ★**要改 4 处**: ①sensor 的 `bus_fmt` 必须填 `MEDIA_BUS_FMT_SGRBG10_1X10` (★**AR0234 是 GRBG**, 对标 `ov02b10.c` 的 `MEDIA_BUS_FMT_SBGGR10_1X10` —— **别照抄 ov02b10 的 BGGR**) ②`link_freq` 菜单要给 **450 MHz** (S2 的 10bit 档; ★**ov02b10 用的是 `MIPI_FREQ_360M`, 那是 8bit 档, 照抄就掉速**) ③`max_fps` / `hts_def` / `vts_def` / `exp_def` 四项要按 1920×1200@60 重算 (对标 `ov02b10.c` 的 `exp_def=0x02ea, hts_def=0x06ac, vts_def=0x04c4` 那组写法) ④★**ISP 输入宽高对齐**: `ov02b10.c` 注释明确写 "input width of the isp needs to be 16 aligned, height 8 aligned" ⇒ 1920×1200 天然满足 (1920%16=0, 1200%8=0) ✔ | ★**本单实拉 `rk3572.dtsi` (6.12) + `isp_params_v3x.c` + `common.h`** + S2 的 `ar0234_modes[]` (width/height/crop/reg_sequence) | ★**1.5 人日** (上一版 1 人日 ⇒ 涨 0.5: 4 处改动 + 4 项要算, 且 lane/位深联动) |
| **C6** | ★**rkaiq 侧注册** | ★**要做 3 件独立的事**: ①★**驱动侧补 rkmodule ioctl** (`RKMODULE_GET_MODULE_INFO` 等 —— ★**S2 没有这套**, 对标 `ov02b10.c` 的 `ov02b10_ioctl()`) —— ★**`GET_MODULE_INFO` 里的 `inf->base.sensor` 字段就是 rkaiq 认 sensor 的钥匙** (`ov02b10.c` 填 `"ov02b10"` ⇒ 我们填 `"ar0234cs"`) ②★**DT 里补 `rockchip,camera-module-*` 四件套** (`rockchip,camera-module-index` / `-name` / `-facing` / `rockchip,camera-lens-name` —— `ov02b10.c` probe 里逐个 `of_property_read_*`) ③★**IQ 文件名要对上**: ★**本单实测 rkaiq 公开 iqfiles 的命名规则 = `<sensor名>_<module名>_<lens名>.json`** (实证: `ov02b10_default_default.json` · `imx415_CMK-OT2022-PX1_IR0147-50IRC-8M-F20.json` · `gc8034_default_default.json`) ⇒ ★**我们最终要产出 `ar0234cs_<module>_<lens>.json`** ⇒ ★**名字对不上 ⇒ rkaiq 起不来 (A4 挂)** | ★**本单实拉 `ov02b10.c` 的 probe + ioctl 段 + rkaiq iqfiles 快照 (`HW/_os_snapshots/rkaiq_iqfiles.json`, 166 项)** | ★**1 人日** |
| **C7** | **ISP tuning (IQ 文件本体)** | ★**不在本单** ⇒ **ISS-139** | ★**rkaiq 公开 iqfiles 里没有 AR0234** (本单复核 166 项清单, 确认无 ar0234 项) | ★**1~2 人周 + 暗室/灰卡 + ★必须等镜头模组定版** |

★**合计 (C1~C6) ≈ 7 人日** —— ★**比上一版的 5.5 人日多 1.5 天, 三个涨点各有实测依据**: ①**CCI → regmap 重写 24 处** (C1 +0.5) ②**增益的 pixclk 分档 + fine exposure 要核** (C3 +0.5) ③**rkisp3 format/帧率要改 4 处、算 4 项** (C5 +0.5)。
★**但这仍是"能出 RAW"的部分**, 不含调色/tuning/整机联调。

★**★ 一句话给老板**: ★**7 人日 ≈ 1.5 周 (1 人) 或 4 天 (2 人) 出 RAW** ⇒ ★**"驱动移植"这一段**本身**不是 2-3 周的大头** —— ★**大头是 C7 tuning (1~2 人周 + 硬件窗口) 和面板 init code (ISS-142 未发)**。

---

## 3. 设备树要点 (要哪些节点与属性)

★**本节所有 Rockchip 侧节点名/属性名都是本单实拉 `rockchip-linux/kernel@develop-6.12` 验证的**, 不是套模板。

### 3.1 sensor 节点 (加在 `rk3572-evb.dtsi`, 挂在 `&i2c2` 下)

```
    ar0234cs: ar0234cs@10 {
        compatible = "onsemi,ar0234cs";   /* ★注意: 上游 S2/S3 都写 "onnn,ar0234cs" (拼写错误),
                                           * 我们自己写规范 vendor 前缀 "onsemi" ⇒ 
                                           * 但 C6 ①里 inf->base.sensor 必须填 "ar0234cs" (rkaiq 认这个) */
        reg = <0x10>;                      /* ★★★ 本单实测 3 个来源一致 = 0x10 (E2) */
        status = "okay";

        /* --- 时钟 --- */
        clocks = <&cru CLK_MIPICSI_OUT>;   /* ★待核: 6.12 的 RK3572 DTS 里 CSI_MCLK 的具体 clock id
                                           * (本单未定位到确切宏名) ⇒ 见 §5 R8 */
        clock-names = "xclk";              /* ★ov02b10.c 用 "xvclk"; 名字必须与驱动一致, 否则 devm_clk_get 失败 */

        /* --- 供电 (★按 11-02 网表新值写: SENSOR_VDD_IO 已 1.8V→2.8V) --- */
        vana-supply = <&vcc_2v8_sensor>;  /* SENSOR_AVDD  2.8V ★[待原厂] (有无独立模拟轨待 onsemi, ISS-142) */
        vdig-supply = <&vcc_2v8_sensor>;  /* SENSOR_VDD_IO 2.8V ★(U_LDO_S28B, TPS7A20-28, ≤30mA) */
        vddl-supply = <&vcc_1v2_sensor>;  /* SENSOR_CORE  1.2V (VDD/VDD_PHY/VDD_DATA) */
        /* ★ regulator 的 phandle 名待定: RK3572 的 2.8V/1.2V rail 在 6.12 DTS 里的节点名本单未定位 ⇒ §5 R8 */

        /* --- 复位 / 省电 --- */
        reset-gpios = <&gpio3 RK_PB0 GPIO_ACTIVE_LOW>;
        pwdn-gpios = <&gpio3 RK_PB1 GPIO_ACTIVE_HIGH>;   /* ★若模组有 PWDN 脚才加; 否则省略 */

        /* --- rkisp3 / rkaiq 对接 (★C6 ②, 四个属性一个都不能少) --- */
        rockchip,camera-module-index = <0>;
        rockchip,camera-module-facing = "front";
        rockchip,camera-module-name = "ar0234cs";   /* ★与 IQ 文件名第二段对应 */
        rockchip,camera-lens-name = "default";       /* ★与 IQ 文件名第三段对应 */

        /* --- 模式 --- */
        hvmode = <0>;   /* 若要跑 HDR (本单不做, AR0234CS 单次曝光 ⇒ 可省) */

        ports {
            port@0 {
                ar0234cs_out: endpoint {
                    remote-endpoint = <&csi2_in1>;   /* ★见 §3.2: 连的是 rkcif 侧的 csi2, 不是 rkisp */
                    clock-lanes = <0>;
                    clock-noncontinuous;
                    link-frequencies = /bits/ 64 <450000000>;  /* ★10bit 档 = 450MHz (S2 实测);
                                                                * ov02b10 的 MIPI_FREQ_360M 是 8bit 档, 别抄 */
                    data-lanes = <1 2>;   /* ★本板实测: 网表 P5 只有 D0+D1 两对必装, D2/D3 是 DNP (见 §5 R9) */
                };
            };
        };
    };
```

### 3.2 ★★ RK3572 的 ISP 链路节点 (★上一版没写, 但不写就接不通)

★**本单实拉 `rk3572.dtsi` (6.12) 的实测拓扑** (不是模板):

```
    csi2_dphy0: csi2-dphy0 {          compatible = "rockchip,rk3572-csi2-dphy";   /* PHY */
    rkcif_mipi_lvds: rkcif-mipi-lvds { compatible = "rockchip,rkcif-mipi-lvds";   /* CSI2 RX */
    rkisp_vir0: rkisp-vir0 {           compatible = "rockchip,rkisp-vir";           /* ★ISP3 核 */
    rkisp_vir0_sditf: rkisp-vir0-sditf { compatible = "rockchip,rkisp-sditf";       /* 输出 */
```

★**三个必做**:
1. ★**`rkcif_mipi_lvds` 必须 `status = "okay"`** (RK3572 出厂默认 `disabled` —— 本单实拉 `rk3572.dtsi`, 全部 `rkcif_mipi_lvds*` / `rkisp_vir*` 都是 `status = "disabled"` ⇒ ★**不开就是没链路**)
2. ★**`rkisp_vir0` + `rkisp_vir0_sditf` 必须一起开** (sditf 是把 ISP 接到显示/VIC 的桥)
3. ★**endpoint 的 `remote-endpoint` 要连 `rkcif` 侧的 `csi2` input 节点** (`&csi2_in1` 这类), ★**不是连 `rkisp`** ⇒ ★**这正是上一版说的"不要套 rkisp1 老模板"的具体落点** (rkisp1 是 sensor 直连 rkisp; rkisp3 是 sensor → csi2_dphy → rkcif → rkisp-vir 三段)

★**RK3572 有 4 组 `mipi0_csi2..3` + 6 个 `csi2_dphy0..5` + 5 个 `rkisp_vir0..4`** (本单实拉) ⇒ ★**两路相机时, 第二路要另占一组 `csi2_dphy` + `rkcif_mipi_lvds1` + `rkisp_vir1`** ⇒ ★**"两路相机共用, 一次投入两处受益" 这句话在 6.12 上成立** (硬件资源确实够)。

---

## 4. 验收判据 (5 条, 可执行, 按顺序过)

| # | 判据 | ★**怎么验 (具体命令)** | 过不了说明什么 |
|---|---|---|---|
| **A1** | **驱动能 enumerate 到 subdev** | `v4l2-ctl --list-devices` 出现 `ar0234cs`; ★**且** `media-ctl -p` 里能看到 sensor 实体 ★**名字形如 `m00_f_ar0234cs 2-0010`** (★**`ov02b10.c` 的 `snprintf(sd->name, "m%02d_%s_%s %s", module_index, facing, SENSOR_NAME, dev_name)` 决定的 ⇒ 驱动里 SENSOR_NAME 填错 ⇒ 名字就不对**) | DT 的 `compatible`/`reg` 不匹配 (★**最常见就是 reg 写成 0x36 ⇒ 永远不应答** — E2) · 驱动没编进去 |
| **A2** | **media-ctl 链路通** | `media-ctl -d /dev/media0 --set-v4l2 '"m00_f_ar0234cs 2-0010":0[fmt:SRGGB10_1X10/1920x1200]'` ★**成功返回 0** ⇒ ★**必须显式写 `SRGGB10_1X10` (GRBG!)** —— 写错成 `SBGGR10_1X10` 会 format 不匹配 | ★**rkisp3 的 format 没协商上 (C5 没做对)** ★或 ★**`rkcif_mipi_lvds` / `rkisp_vir0` 没 `status="okay"`** (§3.2) |
| **A3** | ★**能拿到 1920×1200@60 RAW10** | `v4l2-ctl -d /dev/video0 --set-fmt-video=width=1920,height=1200,pixelformat=BA10 --stream-mmap --stream-count=60 --stream-to=/tmp/a.raw` ⇒ ★**文件大小 = 60 × 1920×1200×2 B (BA10 打包) = 276,480,000 B**; ★**再核帧率**: `v4l2-ctl -d /dev/video0 --stream-mmap --stream-count=300 --print-fps` ⇒ **≥55 fps** | ★**lane 数 / 位深 / link freq 三者联动错** (最典型: link freq 抄了 360MHz 的 8bit 档 ⇒ 带宽减半 ⇒ 掉到 30fps) ★或 ★**增益的 0x30BA 档位抄错 (跟 pixclk 绑) ⇒ 画面全灰** |
| **A4** | ★**rkaiq 能起** | ★**`rk_aiq_uapi2_sysctl_start` 不报错** (返回 0 且日志无 "sensor not found" / "iq file not found") ⇒ ★**再核 `rk_aiq_uapi2_sysctl_getExpSwAttr` 能读回曝光值** | ★**C6 三件事任一没做对**: ①`inf->base.sensor` 名字不对 ②`rockchip,camera-module-*` 属性缺失 ③★**IQ 文件名不符合 `<sensor>_<module>_<lens>.json` 规则** ⇒ ★**注意: 这一条在 C7 完成前【必然过不了】** ⇒ 见 §4.1 |
| **A5** | ★**抽帧亮度 / 行数 / 时间戳正确** | ★**行数**: 用 `v4l2-ctl --stream-mmap --stream-count=1 --stream-to=/tmp/f.raw` 抓一帧, 检查行字节数 = 1920×2 = 3840 B/行 × 1200 行 = 4,608,000 B/帧 ★**亮度**: 解一帧算直方图 ⇒ ★**必须非全黑、非单峰** (全黑 = 曝光没接上; 单峰/全白 = 增益档位错) ★**时间戳**: `v4l2-ctl --stream-mmap --stream-count=300 --verbose` 打印的 `timestamp` 必须单调递增且间隔 ≈16.67 ms | ★**曝光控制没接上 (C3)** ★或 ★**增益分档错 (C3)** |

### 4.1 ★★ 验收顺序的硬约束 (老板/项目总工必须知道)

★**A1~A3 可以在 C1~C5 做完后独立过** (不需要 ISP tuning) ⇒ ★**这是"最小可验证集"**。
★**A4 / A5 依赖 C6, 而 C6 的第 ③件 (IQ 文件) 属于 C7 (ISS-139)** ⇒ ★**结论: ★"能出 RAW" 与 "rkaiq 能起" 是两个不同的里程碑, 中间隔着 tuning**。
⇒ ★**因此 §4 的 5 条判据里, 真正卡 demo 的只有 A1~A3** —— ★**A4/A5 是"量产前"判据, 不是"demo 出画面"判据**。★**不要把 A4 当成 demo 的门槛, 否则会误判成"驱动没搞定"**。

★**★★ 实跑前置 (19:18 主控补充)**: ★**A1~A5 全部要真板子跑** —— ★**当前 Radxa A7S 板连不上** (宿主机 192.168.71.x ↔ 板子 192.168.2.x, mDNS 不解析; R12) ⇒ ★**⇒ 下面 5 条判据现在全部标「待板子恢复后执行」, 但【判据本身已经定死, 不许改松】**。★**★ 两条并行手段**: ①**A7S 网络恢复后直接在 A7S 上跑 A1~A5** (A7S = RK3576, 与 RK3572 的 ISP 拓扑逐节点同构 ⇒ ★**驱动 + IQ + 采集链都能先验**, 见 §0.2 (b) / R13) ②**RK3572 的 C4/C5 DT 静态核对** (查 6.12 DTS, 不需要板子 —— R8)。★**★ 详见 §6.2 的执行顺序表**。

---

## 5. 卡点与风险 (★每条写"卡在谁手里 / 多久")

| # | 卡点 | ★**卡在谁手里** | ★**多久** | ★**能不能并行绕开** |
|---|---|---|---|---|
| **R1** | ★**AR0234CS 在 Rockchip 侧零驱动, 且零同族参考** (E1: 那个 RK3588 仓库是空的) | **我们自己** | ★**7 人日 (C1~C6)** | ✅ **能** ⇒ 见 §6 路径B |
| **R2** | ★**ISP tuning (IQ) 没有现成** | 我们自己 + onsemi | ★**1~2 人周 + 暗室/灰卡** | ⚠️ 部分 ⇒ ★**要 onsemi 回信 (ISS-142) 问"有没有现成 IQ 给 Rockchip ISP3"**; ★**且必须等镜头/模组定版** |
| **R3** | ★**CRA / 畸变 / MTF** | onsemi (AND9658-D) + 模组厂 | 随问询 | ★**demo 阶段容忍畸变** (老板 10-25 原则) ⇒ **不阻塞** |
| **R4** | ★**VDD_IO abs max (决定 I2C 上拉 2.8V / 3.3V)** | onsemi | 随问询 | ✅ **能** ⇒ ★**保守设计: 上拉改 2.8V, 查不到就按保守走** ★**但改上拉 = 改电路 ⇒ 要核同总线从设备 (TMP117 1.7-5.5V ✔ / 充电 IC / 光机)** |
| **R5** | **RK3572 官方 Brief Datasheet 未到** (球位号/电源域/CSI 参数) | 瑞芯微 / 模组厂 | ★**卡 SoC 侧, 与本单并行** | ⚠️ 部分 ⇒ ★**但本单已用主线 6.12 DTS 顶替了大部分 (节点名/拓扑都拿到了)** ⇒ ★**剩余缺口见 R8** |
| **R6** | **镜头 / 模组未定版** | 模组厂 | ★**卡 tuning, 不卡驱动** | ✅ **能** |
| **R7** ★**新** | ★**网表里 I2C 地址注释还是 OV 时代的 "sensor 0x36"** (E2: AR0234CS 实际是 **0x10**) | ★**我们 (main)** | ★**0.5 天** (改注释 + 复核 `0x10` 与 TMP117 `0x48` / 桥接 `0x50` / 充电 IC `0x12` / 光机 `0x72` **不冲突** ⇒ ★**地址本身不冲突, 只是注释错**) | ✅ **能** ⇒ ★**本单不越界改网表, 已登记 need** |
| **R8** ★**新** | ★**RK3572 DTS 里的具体 symbol 名没定位到**: ①CSI_MCLK 的 clock id (`CLK_MIPICSI_OUT`? 6.12 的 RK3572 未必沿用这个名字) ②2.8V / 1.2V regulator 的 phandle 节点名 ③`csi2_inN` input 节点的准确名字与编号 | **我们自己** (查 6.12 DTS 即可, 不等外部) | ★**0.5 天** | ✅ **能** ⇒ ★**这是"抄节点名"的活, 不是外部依赖** ⇒ ★**本单把它显式列出来, 是为了不让它在 C4 阶段变成"等回复"的假阻塞** |
| **R9** ★**新** | ★**网表 P5 只有 CSI D0+D1 两对 lane 必装, D2/D3 是 DNP** (100Ω 对地端接位) ⇒ ★**实际是 2-lane 板** | **我们自己 / 机械** | ★**0.5 天核** | ⚠️ ★**不阻塞, 但要写死**: ★**2-lane @450MHz = 900 Mbps/lane × 2 = 1.8 Gbps ≥ 1.382 Gbps payload (1920×1200×10bit×60) ⇒ 带宽够** ★**(对标 `HW/DISPLAY_SENSOR_CHAIN.md` 的算式) ⇒ ★**但 DT 里 `data-lanes` 必须写 `<1 2>`, 驱动 lane 数分支也要走 2-lane** ⇒ ★**别按 4-lane 写** |
| **R10** ★**新** | ★**AR0234CS fine exposure 寄存器是否存在未知** (S2 驱动只写了 coarse `0x3012`) | onsemi (datasheet) | 随问询 | ⚠️ ★**不阻塞出 RAW, 但影响 C3 的曝光粒度设计** ⇒ ★**要写进 ISS-142 问询单** |
| **R11** ★**新** | ★**onsemi 问询函 (ISS-142) 一封未发** ⇒ R2/R3/R4/R10 全卡在这 | ★**boss (放行) + onsemi (回信)** | ★**问询 1 天 + 回信 1~3 周 (不可控)** | ★**★ 这是本单最长的外部依赖** ⇒ ★**建议: 放行后优先问 ①lane 速率/位深档位 ②IQ 文件 ③fine exposure ④abs max ⑤pinout/电源域 —— 这 5 条直接对应 C2/C3/C6/R4/R10** |
| **R12** ★**新 (19:18 主控补充)** | ★**Radxa A7S 板当前连不上** (宿主机换网段到 192.168.71.x, 板子在 192.168.2.x, mDNS 也不解析) ⇒ ★**跑不了 bringup 验证** | ★**网络 / 基础设施 (主控另开 ISS-147 处理)** | ★**半天 (改 IP 或走串口/静态路由)** | ★**不阻塞写码** ⇒ ★**★ 但它阻塞 §4 的 A1~A5 实跑** ⇒ ★**⇒ A1~A5 全部标"待板子恢复后执行"**; ★**另: 别指望从板上捞 ONNX/.rknn 资产 (ISS-147)** |
| **R13** ★**新 (19:18 主控补充)** | ★**手上没有 RK3572 板** ⇒ 原本"等 RK3572 板回来再验证"的默认路径不成立 | ★**我们** | ★**0** | ✅ ★**能绕开** ⇒ ★**★ 用 A7S (RK3576) 当先行验证平台**: 实测两 SoC 的 ISP 拓扑**逐节点同构** (见 §0.2 (b)) ⇒ ★**C1/C2/C3/C6 在 A7S 上做完, 只差 C4/C5 的 SoC 专属节点名** ⇒ ★**⇒ 「等 RK3572 板」不构成 C1~C3/C6 的前置** |
| **R14** ★**新 (19:18 主控补充)** | ★**面板 init code (视涯问询函) 未发** ⇒ ★**demo 出画面在面板侧就被卡住, 与 sensor 选谁无关** | ★**boss (放行) + 视涯/模组厂 (回信)** | ★**问询 1 天 + 回信 1~3 周** | ★**★ 这是整个 demo 的真瓶颈** (sw-lead 与本单判断一致) ⇒ ★**⇒ §6 的执行顺序必须是「面板先解锁 + 路径B 先打通」** |

---

## 6. ★ 两条路径对比 (老板 19:07 指示后加)

| | **路径 A: AR0234CS 单线** | ★**路径 B: 先用现成 sensor 打通, AR0234CS 后补** |
|---|---|---|
| 做法 | 直接做 §2 的 C1~C6 + §3 的 DT | ★**先用 IMX415 / OV02B10** (★**两者 Rockchip BSP 都有驱动: `imx415.c` (86805 B) / `ov02b10.c` (35448 B) —— 本单实拉 `develop-6.12` 的 `drivers/media/i2c/` 两个都存在且非空**) ★**且 rkaiq `iqfiles/isp3x/` 里都有现成 IQ** (★**本单实拉 rkaiq 仓 `git/trees` 递归清单: `isp3x/ov02b10_default_default.json` + `isp3x/imx415_CMK-OT2022-PX1_IR0147-50IRC-8M-F20.json` —— ★**isp3x 目录一共只有 10 个 .json, 这两个都在里面**) ⇒ 把 demo 链路跑通; 之后 AR0234CS 只换 **sensor + 一份 tuning** |
| 硬件代价 | 无 | ★**多一颗 sensor 的备料成本** (demo 阶段可接受) ★**+ 一个"接线/供电/镜头对不上"的问题** (IMX415 是 1/1.8" 8.4MP **滚动快门** · OV02B10 是 1/5" 1600×1200@30 —— ★**两者都不满足 AR0234CS 的 120°FOV/全局快门/1920×1200@60** ⇒ 路径B **只用来跑通链路, 不代表产品指标达标**) |
| 周期代价 | ★**+2~3 周** (R1+R2 串在关键路径上) | ★**省 10~14 人天** (sw-lead 工时口径) ★**本单复核: ★省的是 C1~C6 的 7 人日 + C7 的 1~2 人周 ⇒ ★合计 15~21 人天** |
| 出画面时间 | 晚 | ★**早** |
| 风险 | ★**整条 demo 链被最长的那条路径卡住** | ★**多一次换料 + 一次重调 tuning** |

### 6.1 ★★ hw-lead 的判断 (要回答老板的那个问题: **路径B 能不能把 demo 关键路径从 AR0234CS 身上挪开? 挪开的话 demo 最早什么时候能出画面?**)

**答: 能挪开, 但要分清"挪开什么"。**

★**能挪开的**: ★**demo 板"跑出画面"这件事** —— 因为 demo 链路上 **90% 与 sensor 无关** (SW 侧 75% 与 sensor 无关, sw-lead 已算过) ⇒ ★**采集链只需要证明 "sensor → RK → ISP → OD 推理 → 画框 → 屏" 这条管子通** ⇒ ★**换一颗有现成驱动 + 现成 IQ 的 sensor, 这条管子就通了**。

★**挪不开的**: ★**产品化的那一步** —— AR0234CS 的 120°FOV / 全局快门 / 1920×1200@60 这三个指标, ★**IMX415 和 OV02B10 一个都满足不了** ⇒ ★**路径B 跑通 ≠ 方案达标** ⇒ ★**路径B 买到的是"时间", 不是"结论"**。

★**demo 最早什么时候能出画面 —— 按今天的实测重排 (相对天, 不给绝对日期, 因为板子什么时候到不由我定)**:

| 里程碑 | 路径 B | 路径 A |
|---|---|---|
| **T0** = demo 板 + 模组到手 | ★**T0** | ★**T0** |
| 采集链通 (A1~A3 过) | ★**T0 + 1~2 天** (驱动现成 + DT 改 + IQ 现成 ⇒ ★**主要成本是"模组接线/供电对不对", 不是软件**) | ★**T0 + 7 人日 (1 人) / T0 + 4 天 (2 人)** |
| 面板亮 + OD 出框 | ★**T0 + 1~2 天 + 面板 init code 到货** | ★同左 (不因 sensor 而异) |
| ★**★ 真瓶颈** | ★**★★ 面板 init code (ISS-142 一封未发) —— 不是 sensor** | ★**同左** |
| ISP tuning 完 (色彩达标) | ★**T0 + 1~2 人周 (换 sensor 后要重调)** | ★**T0 + 1~2 人周 (C7)** |

⇒ ★**结论 (一句话)**: ★**路径B 让 demo 出画面的时间提前 ≈ 5~10 天 (省 C1~C6 的 7 人日), 但 ★不改变"面板 init code 是真瓶颈"这个事实** ⇒ ★**最该做的一件事仍然是: ★把 onsemi 问询函 + 面板问询函都放行 (两封一起, 不要分批)**。
⇒ ★**建议 A/B 并行 (不是二选一)**: ①**立刻**按路径 B 把软件链路跑通 (SW 侧 75% 与 sensor 无关) ②同时做路径 A 的 C1~C6 (不占 SW 人力, 7 人日) ③**面板问询立刻外发**。
⇒ ★**两条路径共用的部分**: 板子 / RK3572 模组 / 供电 / DSI 显示 / RKNN 推理 / 画框 / 后处理 ⇒ ★**约 90% 的工作不因换 sensor 重做**。

### 6.2 ★★ 执行顺序: ★**面板先解锁 + 路径B 先打通** (主控 19:18 指示, 本单认同并落成约束)

★**主控 19:18 给的同步结论**: 软件侧 **75% 与 sensor 无关**; ★**真瓶颈是面板 init code** (视涯问询函未发)。★**本单完全认同**, 并把它落成下面这张表 —— ★**因为 A/B 怎么排都不会绕开面板这一环, 所以排序必须按"先解锁最长的外部依赖"来排**:

| 优先级 | 动作 | ★**为什么排这个位置** | 卡在谁 |
|---|---|---|---|
| **P0** | ★**面板 (视涯) 问询函放行 + 外发** | ★**这是 demo 出画面的唯一真瓶颈** (R14) ⇒ ★**它每晚一天, A/B 两条路径都晚一天** ⇒ ★**必须第一个动** | ★**boss 放行** |
| **P0** | ★**onsemi 问询函放行 + 外发** (按本单 §5 R11 补 5 项) | ★**这是 AR0234CS 侧最长的外部依赖** (R2/R3/R4/R10 全卡它) ⇒ ★**它与面板问询并行, 互不占用对方资源** ⇒ ★**两封一起放行, 不要分批** | ★**boss 放行** |
| **P1** | ★**路径B 先打通** (IMX415/OV02B10, 驱动+IQ 现成) | ★**只换 sensor 就能证明 "sensor→RK→ISP→OD→画框→屏" 整条管子** ⇒ ★**且这 75% 的软件工作与 sensor 无关, 现在就能干** ⇒ ★**它把"链路是否通"这个不确定性尽早消掉** | **sw-lead + hw-lead** |
| **P1** | ★**路径A 的 C1/C2/C3/C6 并行做** (7 人日) | ★**不占 SW 人力**; ★**且 ★C1/C2/C3/C6 可以先在 A7S (RK3576) 上做** (R13: 两 SoC 的 ISP 拓扑逐节点同构) ⇒ ★**不等 RK3572 板** | ★**hw-lead** |
| **P2** | ★**A7S 板网络恢复** (宿主机 192.168.71.x ↔ 板子 192.168.2.x) | ★**它阻塞 §4 的 A1~A5 实跑** (R12) ⇒ ★**但它是网络活, 半天能好, 不该压在上面** ⇒ ★**别把"板子连不上"当"规格没写完"** | **主控 / ISS-147** |
| **P2** | ★**ISP tuning (C7)** | ★**它必须等镜头模组定版, 早动也没用** ⇒ ★**排最后不是它不重要, 是它客观上被 R6 卡住** | **mod-lead + 模组厂** |

★**★ 一句话给主控**: ★**"面板先解锁 + 路径B 先打通" 这条我照办了, 并且要补一句**: ★**路径B 的"先打通"现在有一个更省事的载体 —— A7S 板** (R13) ⇒ ★**不用等 demo 板, 用手上一块同代板就能验驱动 + 验 IQ + 验整条采集链** ⇒ ★**⇒ 建议把 A7S 网络恢复 (P2, 半天) 提到 P1**: ★**它是"用上现成板"的开关, 而不只是一张采资单**。

★**★ 但仍要如实说清一句 (hw-lead 的保留意见)**: ★**A7S 是 RK3576, RK3572 板还没有** ⇒ ★**A1~A5 在 A7S 上过 ≠ 在 RK3572 上过** ⇒ ★**A5 的验收判据 (时间戳/行数/亮度) 可以先在 A7S 上跑, 但 ★"RK3572 上 C4/C5 的 DT 节点名对不对"这条只能等 RK3572 板或 RK3572 的 6.12 DTS 静态核对** ⇒ ★**别把 A7S 的绿灯当成 RK3572 的验收**。

★**★ 路径B 的一个隐藏前提 (本单实测, 上一版没写)**: ★**路径B 能不能走, 取决于 demo 板的 sensor 是不是"外接模组"**。网表 P5 显示 sensor 是走 `CONN_CAM` (18p 跨铰链连接器) 外接的 ⇒ ★**换 sensor 只需换模组, 不动主板** ⇒ ★**路径B 在硬件上是通的** ★**但这条依赖 ISS-146 (demo 板形态: 模组+转接板 vs 自制整板) —— 若是"自制整板", 换 sensor 就要改板, 路径B 的成本会跳上去** ⇒ ★**★ 这条直接推给 ISS-146: ★demo 板选 "模组+转接板" 才让路径B 成立**。

---

## 7. 复算与复现

```bash
cd projects/smart_glasses
python3 HW/open_source_rank.py --selftest        # 开源数据快照与排序 (D1~D5)
python3 SW/tools/fov_scale_check.py               # 1920×1200@60 的视场/吞吐/letterbox 账
python3 HW/e2e_budget_rk3572.py --selftest        # 端到端预算 (ISP 吞吐余量 44.7%)
python3 state/frag_write.py --agent hw-lead --show # 本单分片内容
```

**证据快照**: `HW/_os_snapshots/` (linux_mainline_i2c 201 项 · rockchip_bsp_i2c 363 项 · rkaiq_iqfiles 166 项 · github_repo_counts · openipc_sensors 896 项), 抓取时间 2026-11-02 09:29~09:30。

★**本单 (11-02 19:09~) 亲自抓取的证据 (可复现)**:

| 证据 | 抓取方式 | 结论 |
|---|---|---|
| `opensource206/UC788_AR0234_SENSOR_TO_RK3588` 仓库内容 | GitHub API `repos/{r}/contents/` | ★**空仓** (LICENSE + 82 B README, 1 star, 14 KB) ⇒ **E1** |
| `Kurokesu/ar0234-rpi-driver` 文件清单 + LICENSE | GitHub API | GPL-2.0 · `ar0234.c` **42761 B** · `ar0234-overlay.dts` 2921 B · dkms.conf · setup.sh · 25 stars · push 2026-10-20 |
| `Kurokesu/ar0234-jetson-driver` 文件清单 | GitHub API | GPL-2.0 · `nv_ar0234.c` 21150 B · ★**`ar0234_mode_tbls.h` 5915 B (最干净的复用资产)** · `tuning/` (nvcam 格式, 非 rkaiq) |
| `LPXingxing/LI-AR0234CS-STEREO-GMSL2` | GitHub API | ★**无 LICENSE** (license: None) ⇒ **不可抄** · 50 MB · 四个 L4T 版本 |
| openipc `cameras/sensors/ar0234` | HTTP GET | 200 · "onsemi AR0234 image sensor: specifications" |
| ★**AR0234CS I2C 地址 = 0x10** | 三个独立来源交叉: RPi `ar0234-overlay.dts` (`ar0234@10` / `reg = <0x10>`) + Jetson `tegra234-...-ar0234-A.dts` (`rbpcv3_ar0234_a@10` / `reg = <0x10>`) + 同源驱动 DTS | ★**不是 0x36** ⇒ **E2** |
| ★**AR0234CS 寄存器与增益逻辑** | 读 `ar0234.c` (42761 B) 全文 | CHIP_ID `0x3000`=`0x0A56`/`0x1A56` · FRAME_LENGTH `0x300A` · EXPOSURE_COARSE `0x3012` · DIGITAL_GAIN `0x305E` · ANALOG_GAIN `0x3060` · MFR `0x30BA` (`0x7620\|val`, **按 pixclk 分档**) · GROUPED_HOLD `0x3022` · PLL/时序表 4 套 · 4 个模式 (1920×1200 / 1920×1080 / 1280×720 / 960×600) |
| ★**RK3572 无 ar0234 驱动** | raw `develop-6.12/drivers/media/i2c/ar0234.c` → **404**; 同目录 `imx415.c` 86805 B ✓ `ov02b10.c` 35448 B ✓ | ★**6.12 也没有 ⇒ 结论在 6.1/6.12 两个分支都成立** |
| ★**RK3572 DTS 只在 develop-6.12** | raw `rk3572.dtsi`: 6.1 → 404, 6.6 → 404, **6.12 → 200 (159719 B)** | ★**内核基线是 6.12** ⇒ **E3** |
| ★**RK3572 ISP 拓扑** | 读 `rk3572.dtsi` (6.12) 全文 | `csi2-dphy0..5` (`rockchip,rk3572-csi2-dphy`) · `rkcif-mipi-lvds{,1,2,3}` (`rockchip,rkcif-mipi-lvds`) · `rkisp-vir0..4` (`rockchip,rkisp-vir`) · `rkisp-vir*_sditf` (`rockchip,rkisp-sditf`) · ★**全部默认 `status="disabled"`** · `mipi0-csi2..3` (`rockchip,rk3572-mipi-csi2`) |
| ★**Rockchip sensor 驱动骨架** | 读 `ov02b10.c` (6.12) 全文 | `RKMODULE_GET_MODULE_INFO` 等 ioctl · `inf->base.sensor/module/lens` · `rockchip,camera-module-index/-name/-facing` + `rockchip,camera-lens-name` 四个 DT 属性 · `rockchip,camera-hdr-mode` · `rockchip,camera_default`/`camera_sleep` pinctrl · `clock-names="xvclk"` · `snprintf(sd->name,"m%02d_%s_%s %s",...)` · `device_initcall_sync` · ISP 输入 **宽 16 对齐 / 高 8 对齐** |
| ★**rkisp3 支持 GRBG** | 读 `isp/common.h` (`enum { RAW_RGGB=0, RAW_GRBG, RAW_GBRG, RAW_BGGR }`) + `isp_params_v3x.c` (`case RAW_GRBG:` 两条 BLS 映射全实现) | ★**AR0234 的 GRBG 原生可走** ⇒ **已排除的风险** |
| ★**rkaiq IQ 命名规则** | 读 `HW/_os_snapshots/rkaiq_iqfiles.json` (166 项) + ★**实拉 rkaiq 仓 `git/trees/HEAD?recursive=1` (2551 项, 未截断)** | ★**`<sensor>_<module>_<lens>.json`** (实证 3 例) ⇒ C6 ③ 的判据; ★**`iqfiles/` 下有 6 个 ISP 代目录: `isp20` / `isp21` / `isp32` / `isp32_lite` / `isp3x` + 4 个 mesh 目录** ⇒ ★**RK3572 (ISP3) 用 `isp3x/`**; ★**`isp3x/` 一共只有 10 个 .json, 其中 `ov02b10_default_default.json` + `imx415_CMK-OT2022-PX1_IR0147-50IRC-8M-F20.json` 都在 ⇒ 路径B 的 IQ 齐备; ★**`ar0234` / `ov04c10` 命中数 = 0** (全树扫) |
| ★**★ A7S (RK3576) 与 RK3572 的 ISP 拓扑同构** | ★**实拉对比 `rk3576.dtsi` 与 `rk3572.dtsi` (6.12)** | RK3576: `rockchip,rk3576-csi2-dphy` → `rockchip,rkcif-mipi-lvds` → `rockchip,rkisp-vir` → `rockchip,rkisp-sditf`; ★**RK3572 逐节点同构, 只差 dphy compatible 的 SoC 名** ⇒ ★**C1/C2/C3/C6 可先在 A7S 上验 (R13)**; ★**且 `rk3576.dtsi` 在 `develop-6.1` 存在 (200), 而 `rk3572.dtsi` 在 6.1 是 404 ⇒ 两块板可共用同一份 `ar0234.c`** |
| ★**★ 板子连不上 (19:18 主控)** | 口头/书面转述 | ★**宿主机 192.168.71.x ↔ 板子 192.168.2.x, mDNS 不解析** ⇒ ★**A1~A5 暂不可实跑 (R12)**, ★**且别指望从板上捞 ONNX/.rknn (ISS-147)** |
| ★**网表 (11-02 19:09 新值)** | 读 `HW/netlist_v1.csv` P1/P2/P5 段 | ★`SENSOR_VDD_IO` **2.8V** via **U_LDO_S28B** (TPS7A20-28, ≤30mA) · `SENSOR_AVDD` 2.8V [待原厂] · `SENSOR_CORE` 1.2V · ★**I2C_A 上拉 4.7k→3.3V, 带 [TBD-05]** (VDD_IO abs max 待 onsemi) · ★**P5 只有 D0+D1 必装, D2/D3 = DNP** ⇒ **实际 2-lane** · `CONN_CAM` 18p: pin1/2=CK, 3-10=D0..D3, 11=MCLK, 12=RESET, 13/14=I2C_A, 15/16/17=三条电源, 18=GND |

**证据等级**: 驱动存在与否 / 仓库内容与许可证 / I2C 地址 / 寄存器表 / RK3572 DTS 拓扑 / ISP Bayer 支持 / IQ 命名 / 网表电源轨 = ★**`[实测]` (本单亲自抓取, 抓取方式见上表)** · AR0234CS 电气与模式 = `[官方]` (datasheet 口径, 见 `HW/SENSOR_SELECTION.md` §B4) · 工作量估算 = `[推算]` · CRA / IQ 本体 / abs max / fine exposure / RK3572 具体 symbol 名 = ★**`[待核]` (清单见 §5 R3/R4/R8/R10)**。
