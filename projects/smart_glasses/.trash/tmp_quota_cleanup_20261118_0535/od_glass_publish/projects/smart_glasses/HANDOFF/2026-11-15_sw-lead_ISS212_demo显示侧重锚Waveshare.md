# [sw-lead→PM] ISS-212 · demo 显示侧重锚 Waveshare 2.8" (480×640) + 逐处定性表 + 机器门禁
- 发起方: sw-lead · 日期: 2026-11-15 · 单号 ISS-212 (闭环 need `demo_od_p0_4_panel_init_code`) · 零外发 (不发邮件/询价/问询/采购) · 板端 [实测] = **0 条** (板与屏都不在本机)
## B1 结论摘要
① **demo 屏侧真源规格已出** ⇒ `SW/DEMO_PANEL_WAVESHARE_2P8_SPEC.md`: ★**480×640 / 2-lane / 无 DCS / I2C_B ≤100kHz** 四条 + I2C 面板控制序列 (probe 0xC0/0xC2/0xAC · enable 0xAD=0x01 · disable 0xAD=0x00 · 背光 0xAB+0xAA) + 屏 MCU **0x45** / 触摸 GT911 **0x14** + dts 片段 (不写 panel-init-sequence) + ST7701 兜底件 + **板端 30 分钟验证清单 V0~V9 (每步 命令/期望/判据)** ⇒ ★**"等 init code"这道闸对 demo 屏根本不成立** (官方驱动零 DSI 写); 屏物理显示区 [推算] **42.7×56.9 mm** (dts 写 43×57), 背光功耗 [0数据] (官方未公布, HW 侧推断 ~70~125 mA@3.3V ≈ 0.23~0.41 W)。
② **逐处定性表已出** ⇒ `SW/DEMO_PANEL_SPEC_TRIAGE.md`: ★**38 处** (22 处 grep 命中 `1920×1080|视涯|SeeYA` + 16 处关联活动口径) ⇒ 改写 33 / 整机占位标注 4 / 原样保留 1 (OV02B10 sensor 分辨率); ★**字母框全重算** (面板是 3:4 竖屏 ⇒ 黑边方向翻转): P1 k=0.25 内容 480×300 **上下各 170px** · P2 k=0.75 **上下各 140px** · 框宽 P1 **8px** / P2 **3px** (旧 2px 在屏上只剩 0.5px ⇒ 必须改)。
③ **pipeline spec 已按表重锚** ⇒ `SW/DEMO_OD_PIPELINE_SPEC.md` 只改被判 demo 活动口径的 33 处 (其余一字未动) ⇒ ★**显示侧不再是 60ms 账本的瓶颈**: 画布 2.07→**0.307 Mpx (÷6.75)** ⇒ `t_compose` [推算] 3.0→**~0.44 ms** · TX 物理下限 7.776→**2.304 ms** ⇒ 显示输出侧 10.09→**~2.75 ms** (合成段余量 2.32→**7.79 ms**)。
④ **need `demo_od_p0_4_panel_init_code` 已结** ⇒ demo 半 = 自己查完 (**[官网]**: RPi 官方内核 commit `d8e5eb49991de6b8fa9231532a11036e24aa84de` 本单亲自拉取复核) · 整机视涯半 = **[0数据] + 降级方案** (①demo 不依赖视涯 ②采购硬判据加「必须支持**非 DSC** 的 1920×1080@60 RGB888」, 因 RK3572 **没有 DSC 编码器** ⇒ VESA DSC 3:1 出不来 ③面板厂坚持只给 DSC ⇒ 整机换 SoC RK3588 ④逐帧延迟 S10=5.0ms 整机实测) ⇒ ★**不许再写"等原厂回信" / "放行外发"**。
⑤ **机器门禁已留** ⇒ `SW/tools/check_demo_panel_spec.py`: **rc=0** + `--selftest` **8/8** (反向: 把 demo 口径塞回去必须变红) + R6 受保护 md5 校验。
## B2 验收标准自评
- ✅ 门禁 rc=0 / selftest 8/8 · ✅ 22+16=38 处定性表齐 · ✅ 三件交付物 + 交卷件在位 · ✅ **板/网表/脚表/.kicad_pro md5 逐字节未变** (611b869e… / c78f9912… / 4814617e… / 3e504d2b…) · ✅ **HW/ 一个字未改** (`WAVESHARE_2P8_INIT_AND_BACKLIGHT.md` / `DISPLAY_SMALL_SCREEN_OPTIONS.md` 只引用) · ✅ 未碰 `DEMO_OD_TIMING_SPEC.md`/`SW_TIMING_REVIEW.md`/`RKNN_BENCH.md`/`DEMO_BOARD_60MS_VERDICT_PLAN.md` · ✅ 未改 `state/issue_log.yaml`/`PROJECT_TRACKER.md` §0/`state/outbox/`/别人的分片 · ✅ 零外发
- ★**本单 [实测] = 脚本级/grep 级, 0 条实物测量** ⇒ **板端 30 分钟清单是"待执行"不是"已验证"**; ★**60ms 与显示侧全部未实测**
## B3 证据分级
[官网] RPi 官方 `panel-waveshare-dsi.c` (★**零 DCS 写** + 时序/lane/format + I2C 序列) · 官方 wiki 15 针表 (3V3@14/15 · 无背光脚 · 无 RESET · 无 TE) · 官方商品页 (480×640/IPS/全彩) · 官方排线页 (15pin↔22pin) · 官方 dtbo (0x45/0x14) · Rockchip 官方内核 (2-lane 支持 / **RK3572 无 DSC** / ST7701 参照) — **本单亲自拉取复核** · [实测] 仅脚本级 (`timing_check.py --only F3_i2c_rise` 实跑: I2C_B 4.7k/3.3V ⇒ 398.2 ns@100pF / **1194.7 ns@300pF > 1000ns** ⇒ ≤100kHz; 22 行/30 处 grep 计数; 门禁 rc/selftest; md5) · [推算] 60.85 Hz · 448.6 Mbps · 224.3 Mbps/lane · 2.304/2.048 ms · k=0.25/0.75 · 170/140/40 px · 8/3 px · ~0.44 ms · 压扁 2.13× · 42.7×56.9 mm · [0数据] 整机视涯侧 init 序列/时序/单色全彩/逐帧延迟 · 屏驱动 IC · 背光电参数 · I2C_B 的 Linux bus 号 · 板端一切 · [媒体] **0 条**
## B4 接口取值声明 (interface_claims)
key `demo_panel_resolution`=`480x640` · `demo_panel_dsi_lanes`=`2` · `demo_panel_mode`=`480x640@60.85` · `demo_panel_refresh_hz`=`60.85` · `demo_panel_dcs_init`=`none` · `demo_panel_i2c_addr`=`0x45` · `demo_panel_touch_i2c_addr`=`0x14` · `demo_panel_i2c_max_rate`=`100kHz` · `demo_panel_backlight_ctrl`=`0xAB+0xAA` · `demo_panel_payload`=`448.6Mbps` · `demo_panel_tx_floor_ms`=`2.304` · `demo_panel_letterbox_p1`=`k=0.25;pad_y=170` · `demo_panel_letterbox_p2`=`k=0.75;pad_y=140` · `demo_panel_box_line_px`=`P1=8;P2=3` ⇒ 老共享键 `display_resolution`/`panel_init_sequence_source` **只加口径注记、值未改** ⇒ **不制造跨分片冲突** (merge 冲突仍 0)
## B5 未决项与卡点
① **整机屏路线 / 最终选型 / FOV = 老板拍板** (我只做 demo 屏这一半) · ② 整机视涯若坚持 DSC 3:1 ⇒ RK3572 方案作废 (换面板要求非 DSC, 或换 SoC RK3588) · ③ demo 屏是否旋转 90° (黑边 340→80 px) ⇒ sw-lead 建议默认不旋转 (`display.rotate`=0), 板端实测再定 · ④ 屏驱动 IC [0数据] ⇒ ST7701 兜底是否成立 = 板端实测 · ⑤ 背光功耗/电流 [0数据] ⇒ `LIGHT_3V3` 150mA 是否抬到 200mA = **hw-lead 裁决** (本单不改网表) · ⑥ I2C_B 的 Linux bus 号 [0数据] ⇒ 板端按"扫全部控制器, 找同时有 0x45 与 0x48 的那条"定位 · ⑦ **板未到 ⇒ 60ms 与显示侧全部未实测**
## B6 自证复现命令 (输出原样)
```bash
$ python3 SW/tools/check_demo_panel_spec.py            → ✅ 全过 (R1~R6) rc=0
$ python3 SW/tools/check_demo_panel_spec.py --selftest  → SELFTEST 8/8 通过 (8 条反向用例全红)
$ grep -c "整机路线·暂缓" SW/DEMO_OD_PIPELINE_SPEC.md   → 19 (整机占位标注); grep -c "左右各 96px\|左右各 240px\|面板 1920×1080\|问询函外发比选" → 0 (旧 demo 口径零残留)
$ python3 state/merge.py && python3 state/gate_check.py → ✅ STATE.yaml 已刷新 · 【Q1 交付齐备率】18/18 · gate rc=0
$ md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/PCB/demo_mainboard.kicad_pro → 611b869e13518c3c023fb178f91a0075 / c78f991283cc82d56c8e3dd31657c785 / 4814617e22b567d76164e56bc5e39dc8 / 3e504d2be83152e337949723e909be1b
```
