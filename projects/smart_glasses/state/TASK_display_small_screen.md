【ARS45 · demo 主板 · 换 ≤3 寸显示模组 (老板 2026-11-03 19:4x 拍板)】

## 老板原话
"**屏幕太大了，换小屏幕的，屏幕不要超过 3 寸大小**"
(背景: 现在选的是 **Radxa Display 8HD = 8.0 寸 / 800×1280 竖屏**, 老板嫌大)
⇒ ★**硬约束: 屏 ≤ 3.0 寸**

## 背景 (为什么要换, 别只看尺寸)
· 整机目标是 **视涯 0.49" 1920×1080 SiOLED** ⇒ **0.49" 远小于 3"** ⇒ 换小屏是**朝产品目标靠**, 不是单纯省钱
· 8HD 的背光要 **12.8V 级** ⇒ 主板得加 **12V BOOST + 恒流 + PWM** (≈2.6W) ⇒ ★**小屏若能 3.3V/5V 直接供背光, 就能省掉 BOOST + 限流 + 那 2.6W 的 USB-C 预算**
· 老板已定: **demo 不需要触控** ⇒ 候选屏**不必带触控**
· demo 屏的职责: **验 DSI 通路 + 跑算法**, 不需要 1080p ⇒ 分辨率可以让位给"好买好接"

## 交付物 (★只写这 2 个文件, 不许碰别的)
1. `projects/smart_glasses/HW/DISPLAY_SMALL_SCREEN_OPTIONS.md`
2. `projects/smart_glasses/HW/display_small_options.json`
   格式: `{"candidates":[{"name":"...","vendor":"...","size_inch":2.8,"resolution":"...","interface":"MIPI DSI 2-lane/4-lane",
   "fpc_connector":"<型号>","fpc_positions":24,"fpc_pitch_mm":0.5,"driver_ic":"...","kernel_support":"simple-panel-dsi / 内核白名单 / 需自驱",
   "backlight":"3.3V/5V/12V/无背光(OLED)","backlight_current_ma":null,"public_pinout_url":"...","price_hint_usd":null,"notes":"..."}],
   "product_target":{"panel":"视涯 0.49in 1920x1080 SiOLED","status":"...","public_interface":"...","source":"..."}}`

## 硬约束 (候选必须满足)
① **尺寸 ≤ 3.0 寸**
② **MIPI DSI** (与我们 SoM 的 DSI 一致; 2-lane 或 4-lane 都要, 请标明)
③ ★**驱动要"可用"**: 优先 (a) 内核白名单里的 IC (ST7701/ST7789V/ILI9881C/TP9950/或 `simple-panel-dsi` 兼容) 或 (b) **init sequence 能公开拿到** (厂商 dts / 公开 kernel 分支 / 开源驱动)
④ ★**FPC 针位表与连接器型号要公开** (我们要照着画座 + 改网表) —— 针数/间距/型号都要
⑤ 不用触控 (但若屏自带触控, 说明它会不会拖累我们 —— 触控线我们一律不接)
⑥ 背光电压尽量 ≤5V; 若是 OLED 无背光 ⇒ ★**请明确写出来** (那最省事)

## 查找路径
· Radxa / Waveshare / 其它公开在售的 1.5"/2.0"/2.4"/2.8"/3.0" MIPI DSI 模组
· ★**顺带查 视涯 0.49" 1920×1080 SiOLED 有没有公开的接口/针位/资料** (ISS-132 单色还是全彩 / ISS-133 显示架构)
· Rockchip 内核 `panel-simple.c` / `panel-*.c` 里有没有小屏的 init sequence 可抄
· ★顺带确认: 换成 ≤3 寸后, **我们的 DSI 是 2-lane 还是 4-lane** ⇒ 影响 SoM 侧 pin 分配 (现在按 4-lane 画)

## 纪律
· ★**只认原厂/官方资料**; 第三方转述不许当证据; 查不到写"未查到" + 试过的 URL
· ★**只写上面这 2 个文件**; 不许改 网表 / 板文件 / issue_log / tracker / STATE.yaml
· 临时下载放 /tmp; 不发邮件 / 不联系厂家 / 不下单

## 汇报 (8~12 行)
候选几个 / 各候选关键参数 (尺寸/分辨率/lane/连接器/背光) / **你建议选哪个 + 理由** / 视涯 0.49" 的公开资料查到什么 / 两个文件路径
