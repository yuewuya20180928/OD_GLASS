# HW/DISPLAY_SMALL_SCREEN_OPTIONS.md —— demo 主板换 ≤3.0 寸显示模组: 候选清单与定案建议

> **触发**: 老板 2026-11-03 19:4x —— "**屏幕太大了, 换小屏幕的, 屏幕不要超过 3 寸大小**"
> **原选件**: Radxa Display 8 HD = 8.0 寸 / 800×1280 竖屏 / 背光 12.8V 级 (见 `HW/STEP1_PARTS_SPEC.md` §3、`HW/PCB/DISPLAY_39P_PINOUT.md`)
> **硬约束**: 屏 ≤ 3.0 寸 · MIPI DSI · 驱动可用 (内核白名单 or init sequence 公开可得) · FPC 针位表与连接器型号公开 · 不需要触控 · 背光 ≤5V (OLED 无背光最好)
> **本文件 = 显示侧的候选真源 (人读)** · 机器读版: `HW/display_small_options.json` (同目录)
> ★**纪律**: 全部结论只认 **原厂/官方资料** (厂家官网 / 厂家官方 GitHub / 内核源码 / 上市公司招股书); 查不到的写「未查到」并附试过的 URL (§7)。第三方转述(淘宝/知乎/媒体)不作证据。

---

## 0. ★ 一句话结论

**demo 屏选 「Waveshare 2.8inch DSI LCD」(2.8" / 480×640 / MIPI DSI 2-lane / 15 位 1.0mm FPC / $43.39)**, 理由三条:
1. **它是全网唯一一款"≤3.0 寸 + MIPI DSI + 官方公开逐针 FPC 表 + 在售可买 + 官方 driver 生态"四项全中的模组** ( Waveshare 官方产品页自己的 DSI 对照表里, DSI 最小档就是 2.8 寸 —— 再往下就没有了);
2. ★**它的 15 针里没有背光引脚** ⇒ 背光由模组内部从 3V3 取电 ⇒ 主板**整条「12V BOOST + 采样限流 + PWM 调光」链可以砍掉** (8HD 那 2.6W 直接消失);
3. ★**init sequence 公开可得**: 树莓派官方 firmware 里有 `waveshare,2.8inch-panel`; Rockchip 内核 `panel-sitronix-st7701.c` 里同时有**同分辨率同 lane 数**的 2.8 寸档位 (`densitron,dmt028vghmcmi-1a`, 480×640 / 2-lane / RGB888 + 完整 GIP 序列在 .c 里) ⇒ **两条路都通, 不必等厂家**。

★**顺带两条硬结论 (比选屏本身更值钱)**:
- ★**ISS-132 已经有答案了**: 视涯官网 0.49" 页面同时列 **全彩版 与 单色绿 (Mono-G) 版** ⇒ 不是"单色 or 全彩"二选一, 而是**产品线里两个规格并存** (见 §5)。
- ★**视涯 0.49" 官方 datasheet 拿到了** (2021年01月版 PDF): 型号 **SY049WDM01**, 接口原文 **"MIPI D-PHY 1 PORT, VESA DSC 3:1"**, **刷新率 60–90Hz**, **功耗 468mW @ 90Hz / 100% duty** ⇒ ★**面板侧就有 DSC, 且 468mW 比 8HD 背光单项 (2.6W) 还低 5.5 倍** ⇒ 换小屏同时解决尺寸、功耗、DSC 三件事。

---

## 1. 换屏的连带影响 (先算清楚再选)

| 维度 | 现状 (8HD) | 换成 ≤3" 后 | 结论 |
|---|---|---|---|
| **DSI lane 数** | 4-lane (屏支持 2/4) | ★**demo 屏 2-lane** (Waveshare 15 针只有 DSI1_DN0/DP0 + DSI1_DN1/DP1 两对数据) | ★**SoM 侧不用改** —— Forlinx FET3572-C 的 DSI 本来就是 4-lane, BTB 座针位固定; 变的只有"主板 → 屏座"这一段 |
| **主板→屏 那一段的布线** | 按 4-lane 画 | ★**建议维持 4-lane 布线不变**, 屏座保留 lane2/lane3 针位 | 理由: 整机屏 (视涯 0.49") 针位表还没拿到, 可能是 4-lane; 现在把 4-lane 留好, 以后换屏不改板 |
| **软件侧 lane 配置** | dts `dsi,lanes` | 切 2-lane | ★内核里就有先例: `panel-sitronix-st7701.c` 的 2.8" 档位 `.lanes = 2` ⇒ 纯 DT 配置, 不动硬件 |
| **背光** | 12.8V typ / 200mA (10FHD 官方值) ⇒ 2.56W | ★**15 针无背光引脚** ⇒ 模组内部从 3V3 取电 | ★**BOOST + 限流 + PWM 三件套可砍**; 背光电流官方未公布 ⇒ 需实测 |
| **USB-C 900mA 预算** | 4.6W vs 4.5W ⇒ 超 | 去掉 8HD 背光 2.6W ⇒ **≈2.0–2.3W** (背光电流待实测) | ★**超预算问题缓解** |
| **屏座** | 屏侧 40p/0.5mm, 板侧 39p/0.3mm (FH35C-39S-0.3SHW(50)) | ★**15 位 / 1.0mm** (Waveshare 官方包内 FPC "15PIN 1.0 pitch") | ★**屏座要改** ⇒ 见 §4.3 两条方案 |
| **触控** | GT911 (I2C) | 2.8" 模组自带 5 点电容 (I2C SCL0/SDA0) | ★**我们一律不接**: 屏侧 I2C 与 DDC 走同一对线, 我们把 DDC 留给屏的 DDC, 触控当没有; 代价 = 少接 4 根线, 无电气负担 |

---

## 2. 候选总表 (4 个, 全部满足 ≤3.0" + MIPI DSI)

| # | 候选 | 尺寸 | 分辨率 | DSI | FPC 针数/间距 | 驱动 | 背光 | 公开针位表 | 价格 | 判定 |
|---|---|---|---|---|---|---|---|---|---|---|
| **1** ★ | **Waveshare 2.8inch DSI LCD** (SKU 22028) | **2.8"** | 480×640 IPS 光学贴合 | **2-lane** + CK | **15 位 / 1.0mm** (官方包内 FPC 实测口径) | RPi 官方 firmware 有 `waveshare,2.8inch-panel`; Rockchip 内核有同档 ST7701 | ★**无独立背光引脚** (模组内供) | ★**有** (官方 wiki 逐针表) | **$43.39** (1~9) | ★★**首选** |
| **2** | **Densitron DMT028VGHMCMI-1A** (敦泰面板) | **2.8"** | 480×640 | **2-lane** RGB888 | 未查到 (裸面板) | ★★**Rockchip 内核白名单已有** (`panel-sitronix-st7701.c`, GIP 序列在 .c) | 未查到 | 未查到 | 未查到 | ★**驱动最干净, 但针位表要问原厂** |
| **3** | **Samsung S6E63J0X03** (圆形 OLED) | **1.61"** (29×29mm) | 320×320 | **1-lane** | 未查到 | ★★**Rockchip 内核白名单已有** (`panel-samsung-s6e63j0x03.c`, init 在 .c) | ★★**无背光 (OLED)** | 未查到 | 未查到 | ★**形态/功耗最像产品目标, 但缺模组** |
| **4** | **视涯 0.49" SY049WDM01** | **0.49"** | 1920×1080 | MIPI D-PHY 1 port, **DSC 3:1** | 未查到 (侧出脚, 底部 pin 区 19.03mm) | 视涯面板在 Rockchip 内核有先例 (`panel-visionox-rm69299.c`) | ★**无背光 (OLED)** | **未查到** (datasheet 无针位表) | 未查到 (走 B2B) | **产品目标, 不是 demo 采购件** |

★**为什么只有这 4 个**: 见 §6 —— Rockchip 内核 79 个 panel 文件我逐个扫过 (含物理尺寸/分辨率/lane), **≤3.2" 且真·DSI 的只有 1.61" 的 S6E63J0X03 一个**; 公开在售的 ≤3 寸 MIPI DSI **模组** (带逐针表) 只有 Waveshare 2.8" 一款。

---

## 3. 逐候选证据

### 3.1 ★ 候选 1: Waveshare 2.8inch DSI LCD —— 首选

| 项 | 值 | 证据 |
|---|---|---|
| 厂商 / 型号 | Waveshare, **Part No. "2.8inch DSI LCD"**, **SKU 22028** | [官方] 商品页 `SKU: 22028 / Part No.: 2.8inch DSI LCD` |
| 尺寸 / 分辨率 | **2.8" / 480×640**, IPS, 光学贴合, 160° 视角, 硬玻璃 6H | [官方] 商品页 Details 表 |
| 接口 | ★**MIPI DSI 2-lane** (由 15 针表里只有 DSI1_DN0/DP0 + DSI1_DN1/DP1 两对数据 + DSI1_CN/CP 一对时钟得出) | [实测] 官方 wiki 逐针表 |
| ★**FPC 针数 / 间距** | ★**15 位 / 1.0mm pitch** | [官方] 商品页 Package Content: "**FPC 15PIN 1.0 pitch 50mm (opposite sides) x1**" + "FPC 15PIN 1.0 pitch 160mm (opposite sides) x1" |
| ★**逐针针位表 (屏侧, 全部 15 针)** | 1 GND · 2 DSI1_DN1 · 3 DSI1_DP1 · 4 GND · 5 DSI1_CN · 6 DSI1_CP · 7 GND · 8 DSI1_DN0 · 9 DSI1_DP0 · 10 GND · 11 SCL0 · 12 SDA0 · 13 GND · 14 3V3 · 15 3V3 | [实测] 官方 wiki "Interface Definition" 表 (中英文页一致) |
| 连接器型号 | ★**未查到** —— Waveshare 只公开针位表与线材规格, 没公开板上那颗 FPC 座料号 ⇒ 主板按 **RPi 标准 15 位 / 1.0mm 翻盖式 FPC 座** 选型 (型号待定, 走 JLC 常规件) | — |
| 背光 | ★★**15 针里没有独立背光引脚 (也没有 RESET 引脚)** ⇒ 背光与复位都在模组内部 (推断: 模组自带 LED 驱动与复位 RC) ⇒ **主板只供 3.3V, 不需要 BOOST/限流/PWM**; ★**背光的电压/电流/是否 PWM 可调 = 未查到** (官方规格页无背光物理参数表) | [实测] 针位表 + [官方] 商品页无背光章节 |
| 触控 | 5 点电容, **I2C** (SCL0/SDA0), 硬玻璃 + 光学贴合 | [官方] wiki Features + 商品页 Details |
| ★**init sequence 可得性** | **(a)** 树莓派官方 firmware 仓库 `boot/overlays/vc4-kms-dsi-waveshare-panel.dtbo` 里有 **`compatible=waveshare,2.8inch-panel`** + `touchscreen-size-x=480 / touchscreen-size-y=640` ⇒ 树莓派生态里这块屏是**官方登记过的面板**; **(b)** Waveshare 官方 GitHub `Waveshare-DSI-LCD` 提供 Pi4/Pi5 两条路线的 `WS_xinchDSI_Screen.ko` + `.dtbo` (init 在 .ko 内) ⇒ **公开可得, 不必问厂家** | [实测] 官方仓库二进制 (dtbo 已解出 compatible) |
| Rockchip 侧怎么接 | ★**走 `simple-panel-dsi` 路线** (只要 dts + init sequence, 不带任何私有 driver) —— 判据同 `HW/STEP1_PARTS_SPEC.md` §3.6 | — |
| ★**内核里的同档先例** | `drivers/gpu/drm/panel/panel-sitronix-st7701.c` (Rockchip develop-6.1) 里已有 **`densitron,dmt028vghmcmi-1a` = 2.8" / 480×640 / 2-lane / RGB888**, 完整 **GIP 序列写在 .c 里**, timing: clock 22325kHz, htotal 544, vtotal 698 (≈58.8Hz), hsync 4, vsync 40, **NHSYNC+NVSYNC** | [实测] 内核源码 |
| 价格 | **$43.39** (1~9 档) / 10~49 $43.09 / 50~99 $42.97 / 100+ $42.97 | [官方] 商品页价格表 (2026-11-03 抓) |
| 交期 / 供货 | ★**未查到** (商品页无交期字段) | — |
| ★★**缺点 (必须写进台账)** | ① 15 针无 RESET ⇒ **我们不接复位**, 若屏偶发不回初始化只能靠重新上电 (推断, 需实测); ② 背光电流未知 ⇒ 3V3 轨要留余量; ③ 480×640 只有 0.3M 像素, 画 OD 框够用但不是"显示效果 demo"; ④ 2.8" 玻璃面板硬且大, 结构上仍要占镜框位置 | — |

### 3.2 候选 2: Densitron DMT028VGHMCMI-1A (2.8" / 480×640 / ST7701 / 2-lane) —— 驱动最干净

| 项 | 值 | 证据 |
|---|---|---|
| 厂商 | Densitron (敦泰) 面板 | [实测] 内核 compatible `densitron,dmt028vghmcmi-1a` |
| 内核支持 | ★★**Rockchip develop-6.1 `panel-sitronix-st7701.c` 已收录**: mode 480×640 @ clock 22325kHz, `.lanes = 2`, `MIPI_DSI_FMT_RGB888`, 尺寸 56×78mm, `panel_sleep_delay = 5`, **GIP 序列 (`dmt028vghmcmi_1a_gip_sequence`) 完整写在 .c 里** ⇒ **BSP 零移植** | [实测] 内核源码 |
| ★为什么值得留着 | ★**它是"驱动可用性"这一维的最优解**: 不用写任何代码, 不用问厂家要 init code, 只差一个针位表 | — |
| ★缺口 | ★**FPC 针位表 / 连接器型号 / 背光电参数 = 未查到** (裸面板不是模组, 公开渠道没有这套资料) ⇒ 要向敦泰或其模组厂索取 | — |
| 与候选 1 的关系 | ★**两者极可能是同一块面板规格 (480×640 / ST7701 / 2-lane)** ⇒ 若实测 Waveshare 2.8" 的驱动 IC 确为 ST7701 且 init 兼容, 可直接改用 `densitron,dmt028vghmcmi-1a` 档位, **驱动彻底落到 Rockchip 内核里** ⇒ **强烈建议落板前用一次 dev 板实测把这条确认掉** | [推断, 高置信] |

### 3.3 候选 3: Samsung S6E63J0X03 (1.61" / 320×320 / 1-lane / 圆 OLED) —— 形态最像产品目标

| 项 | 值 | 证据 |
|---|---|---|
| 尺寸 / 分辨率 | 29×29mm (**1.61"**), 320×320, clock 4649kHz | [实测] 内核 `panel-samsung-s6e63j0x03.c` |
| 接口 | **MIPI DSI 1-lane** | [实测] 同上 |
| 内核支持 | ★★**Rockchip develop-6.1 白名单内**: `panel-samsung-s6e63j0x03.c`, 含完整 init 序列与 gamma 表 | [实测] 内核源码 |
| ★背光 | ★★**无背光 (OLED 自发光)** ⇒ 整条背光链消失 | — |
| ★缺口 | ★**公开在售模组与 FPC 针位表 = 未查到** (这颗料是手机/穿戴用的裸屏, 不是模组) ⇒ 采购与针位表都要问原厂 | — |
| 价值 | ★**它是"我们要的最终形态"的现成答案**: 1.6 寸圆屏 + OLED 无背光 + 内核已有驱动 + 1-lane ⇒ 若将来做小样机, 这条路比 2.8" LCD 更接近产品形态 | — |
| ★内树位置 | ★Rockchip 内核 79 个 panel 文件里, 真·MIPI-DSI 且 ≤3.0 寸的**只有 2 个**: 本项 (1.61") 与 `densitron,dmt028vghmcmi-1a` (2.8"), 次小就是 3.63" (`elida,kd35t133`) ⇒ ★"≤3 寸 + 内核白名单 + 公开针位表"三条同时满足的只有 Waveshare 2.8" | [实测] 全树扫描 |

### 3.4 候选 4: 视涯 0.49" SY049WDM01 (产品目标, 非 demo 采购件) —— 详见 §5

---

## 4. ★ 三个必须现在拍板的连带决定

### 4.1 DSI 是 2-lane 还是 4-lane? ⇒ **屏侧 2-lane, 主板→屏这一段保持 4-lane 布线**

- **SoM 侧 (Forlinx FET3572-C / RK3572)**: DSI 本来就是 **1×4-lane** (BTB 座 400 针, 针位固定) ⇒ ★**SoM 侧 pin 分配一个字都不用改**;
- **demo 屏侧**: Waveshare 2.8" 只有 **2-lane** ⇒ 板子上 lane2/lane3 这对差分**在 demo 阶段闲置**;
- ★**建议**: 主板→屏座的连线**仍按 4-lane 画** (lane0~lane3 + CK 全部引出到座上), 屏侧用一条转接线只接 lane0/lane1 + CK ⇒ **这样将来换整机屏 (视涯 0.49", 可能是 4-lane + DSC) 时不用改板, 只换屏 + 换线**;
- **软件**: dts 里 `dsi,lanes` 切 2 (内核里 `dmt028vghmcmi-1a` 就是 `.lanes = 2` 的现成先例) ⇒ **不动硬件**;
- **带宽校核** [推算]: 480×640@60 RGB888 ≈ **442 Mbps** payload ⇒ 2-lane 需 ≥221 Mbps/lane, 常规 DSI 2-lane @500Mbps 有 2 倍余量 ⇒ 够。

### 4.2 背光链要不要留?

★**建议: 主板上背光 BOOST + 限流 + PWM 三件套按"保留但 DNP"处理**, 理由:
- ① demo 屏 (Waveshare 2.8") **不需要** (模组内部供);
- ② 但**整机屏与"万一换成别的 2.8~3 寸 LCD 模组"可能要** (这类小 LCD 的背光常见 3.0~3.4V / 40~80mA, 也有做成 5V 以上的) ⇒ 留位成本远小于二次改板;
- ③ ★**8HD 那套 12.8V BOOST 现在可以彻底从电源树里划掉** (原电源树按 12V BOOST + 恒流 + PWM ≈2.6W 算的) ⇒ ★**USB-C 900mA 预算从 4.6W 降到 ≈2.0–2.3W** (背光电流实测后定稿)。

### 4.3 ★ 屏座 (display FPC seat) 怎么画?

现状: 屏座是给 8HD 的 **39 位 / 0.3mm (FH35C-39S-0.3SHW(50))** ⇒ ★**换 ≤3 寸屏 = 屏座必改**。

| 方案 | 做法 | 优点 | 缺点 |
|---|---|---|---|
| **A (推荐)** | 屏座按 **15 位 / 1.0mm (RPi 标准)** 画, 直接插 Waveshare 2.8"; ★**另外在同位置预留一个 24 位 / 0.5mm 的 4-lane 座 (DNP 或用 0Ω 选择)** 供将来整机屏 | demo 零转接、零焊接; 量产路线也不堵 | 多一个座的位置与走线 |
| **B** | 屏座直接按 **24 位 / 0.5mm (4-lane + CK + DDC + RST + 3V3×2 + GND×4 + 背光预留)** 画, demo 用一条 **15位/1.0mm → 24位/0.5mm 自制转接线** | 一座两用, 将来接整机屏不用改板 | demo 要额外做/买一条转接线 (JLC 常规件可做, 成本个位数到几十元) |
| C | 只画 15 位/1.0mm | 最省 | ★**整机屏若是 4-lane / 针位不同 ⇒ 二次改板** ⇒ **不推荐** |

★**我的建议: 选 B (24 位/0.5mm 为主座)**, 理由: 整机屏 (视涯 0.49") 的**针位表至今未查到** (ISS-133/ISS-132 一线), 现在按 demo 屏把座定死 (方案 C) 等于把产品的不确定性写进板子; 按 4-lane 预留 + 转接线接 demo 屏, **板子只改一次**。

---

## 5. ★ 视涯 0.49" 1920×1080 SiOLED —— 公开资料查到了什么 (含 ISS-132 的答案)

### 5.1 ★★ ISS-132 (单色还是全彩?) —— **已有答案: 两个规格并存**

视涯官网 0.49" 产品页 (https://www.seeya-tech.com/html/products/3971.html) 同时列 **三个 0.49" 规格** [官方, 实测]:

| 官方型号名 | 分辨率 | 亮度 | 对比度 | **色彩** | 接口 |
|---|---|---|---|---|---|
| **0.49" OLEDoS 高亮版** | 1920×1080 | **3000 nits** | 50,000:1 | **Full RGB (全彩)** | **MIPI** |
| **0.49" OLEDoS** | 1920×1080 | **1800 nits** | 50,000:1 | **Full RGB (全彩)** | **MIPI** |
| **0.49" OLEDoS Mono-G** | 1920×1080 | **20000 nits** | 50,000:1 | **Green (单色绿)** | **MIPI** |

⇒ ★**不是"单色 or 全彩"的二选一**: 全彩有 1800/3000 nits 两档, 另有单色绿 20000 nits 档。
⇒ ★**对项目的直接含义**:
  ① **单色绿 (20000 nits) 是 OD 检测框的天然形态** —— 检测框本来就是"目标框 + 类别文字", 绿色单色反而更干净、功耗更低 (自发光面积小) ⇒ ★**若最终选 Mono-G, "彩色显示"卖点要改, 但 OD 场景不受影响**;
  ② **全彩版 1800 nits 也够做 AR 观感**, 但 BOM 成本明显高于 Mono-G ⇒ **选型时把"要全彩还是 Mono-G"作为一道独立决策题提给老板**, 不要让它默认挂在"0.49" 1920×1080"底下。

### 5.2 ★★ 官方 datasheet 拿到了 (2021年01月版 PDF)

来源 [官方]: 产品页的"下载"按钮直链 → `https://www.seeya-tech.com/uploads/2021/01/010917/SeeYA Technology - 049 OLEDoS.pdf` (另有 `... - 049 Mono-G OLEDoS.pdf`), 已下载并解析 (PDF 为图片版, 逐页渲染后读出):

| 项 | 值 | 说明 |
|---|---|---|
| **型号** | **SY049WDM01** (全彩) | ★datasheet 首页型号 |
| 分辨率 / 像素 | **1920×1080**, 像素 **5.6 μm**, **4496 PPI** | |
| AA (有效显示区) | **10.783 × 6.065 mm** | |
| 对比度 / 色域 | **50,000:1**, **DCI-P3 >90%** | |
| 亮度 | 1800 nits (高亮版 3000 / Mono-G 20000) | |
| ★**功耗** | ★**468 mW @ 90Hz, 100% duty** | ★★这是面板整机功耗, **比 8HD 背光单项 (2.56W) 还低 5.5 倍** ⇒ 直接支撑"换小屏" |
| ★**接口** | ★**"MIPI D-PHY 1 PORT, VESA DSC 3:1"** (datasheet 原文) | ★**面板侧就支持 DSC**; ★"1 PORT" 未写 lane 数 ⇒ 2 或 4 lane 待问 |
| 刷新率 | **60 – 90 Hz** | |
| 机械 | 玻璃 9.09±0.35 × 15.68±0.25 mm, **模组厚 1.48±0.1 mm**, **FPC 侧边出 Pin** (侧出脚), 底部 pin 区 19.03 mm, pin 区公差 0.4±0.1 mm | ★**侧出脚** ⇒ 结构上是"横向引出", 对 FPC 弯折半径有要求 |
| 工艺 | 12 英寸硅晶圆, 80nm | |
| 联系方式 | sales@seeya-tech.com; 上海浦东 / 合肥 | |

### 5.3 ★ 对 ISS-132 / ISS-133 / D3 的影响 (只提, 不改别的文件)

- **ISS-132 (单色/全彩)**: ★**结论可更新为"全彩与单色绿并存, 需老板选型"** (证据 = 官网 0.49" 页三个规格 + 两份官方 PDF);
- **D3 (RK3572 DSI 不支持 DSC 的风险)**: ★**面板侧确认支持 VESA DSC 3:1** ⇒ 风险范围缩到 "**RK3572 的 DSI 控制器能否解 DSC**" 这一个点 (SoC 侧), 不再是双向未知;
- **D1 (无全彩版本 ⇒ 老板不接受单色)**: ★**该条作废** —— 全彩版本确实存在 (1800/3000 nits);
- ★**新信息**: "MIPI D-PHY 1 PORT" ⇒ 若整机屏实际只要 1 个 port, 则 §4.1 的"4-lane 预留"策略对整机屏可能过度, 但**对 demo 屏无所谓** ⇒ 维持 4-lane 预留 (成本 = 一对差分线) 仍是划算的。

---

## 6. ★ 内核白名单实测: ≤3 寸的 DSI 面板到底有没有?

**方法**: 从 `rockchip-linux/kernel` 分支 `develop-6.1` 拉取 `drivers/gpu/drm/panel/` 下**全部 79 个 .c** (与 `HW/STEP1_PARTS_SPEC.md` §3.5 记的 "79 个 panel 文件" 一致), 逐个解析 compatible / 物理尺寸 / 分辨率 / lane 数 / 是否有 init 序列。

**结果 (DSI 类, 按物理对角线排序)**:

| 排名 | 驱动文件 | 尺寸 | 对角 | 分辨率 | lane | init 在哪 |
|---|---|---|---|---|---|---|
| **1** | ★`panel-samsung-s6e63j0x03.c` | 29×29mm | **1.61"** | 320×320 | **1** | **.c 里** |
| **2** | ★**`panel-sitronix-st7701.c` 的 `densitron,dmt028vghmcmi-1a` 档位** (与 `techstar,ts8550b` 同文件) | 56×78mm | **2.8" 档** | **480×640** | **2** | **.c 里 (完整 GIP 序列)** |
| 3 | `panel-elida-kd35t133.c` | 42×82mm | 3.63" | 320×480 | 1 | .c 里 |
| 4 | `panel-samsung-s6d16d0.c` | 84×48mm | 3.81" | 864×480 | 2 | .c 里 |
| 5 | `panel-novatek-nt35560.c` | 48×84mm | 3.81" | 480×854/864 | 2 | .c 里 |
| 6 | `panel-orisetech-otm8009a.c` | 52×86mm | 3.96" | 480×800 | 2 | .c 里 |
| … | … | … | … | … | … | … |
| (中段) | `panel-visionox-rm69299.c` | 74×131mm | 5.92" | 1080×2248 | 4 | .c 里 (5 条 DCS 写) |

★**三条硬结论**:
1. ★**Rockchip 内核白名单里, 真·MIPI-DSI 且 ≤3.0 寸的面板, 全树只有 2 个: Samsung S6E63J0X03 (1.61") 与 Densitron DMT028VGHMCMI-1A (2.8")** —— 但★**这两个都只到"面板/驱动"层, 都没有公开在售的带针位表的模组** ⇒ 所以"≤3 寸 + 内核白名单 + 公开针位表"三条同时满足的, **全网只有 Waveshare 2.8" 一款模组**;
2. ★**`panel-simple.c` 里唯二 ≤3.2 寸的条目都不是 DSI**: `sharp,ls020b1dd01d` (42×28mm, 240×160, **RGB565 + SHARP_SIGNALS, 并行口**) 与 `giantplus,gpm940b0` (60×45mm, **RGB888 3X8 并行口**) ⇒ **别被"内核里有小屏"误导, 那两条是并口屏**;
3. ★**`panel-visionox-rm69299.c` (compatible `visionox,rm69299-1080p-display`) 是视涯面板在 Rockchip 内核里的现成先例** —— 1080×2248 / 4-lane / RGB888 / VIDEO+LPM / 只用 5 条 DCS 写 (0xFE/0xC2/0x35/0x51 + sleep out + display on), 供电 `vdda` + `vdd3p3` (负载 32mA / 13.2mA) ⇒ ★**"视涯 SiOLED 走 Rockchip DSI"这条路内核里已有先例可循**, 不用从零猜。

---

## 7. ★ 未查到项 (含试过的 URL) —— 纪律留痕

| 未查到的 | 试过的 URL / 方法 |
|---|---|
| Waveshare 2.8" 的**驱动 IC 型号** | ① `https://www.waveshare.com/wiki/2.8inch_DSI_LCD` (规格表无) ② `https://www.waveshare.net/w/index.php?title=2.8inch_DSI_LCD&action=raw` (无) ③ 商品页 `https://www.waveshare.com/product/2.8inch-dsi-lcd.htm` (无) ⇒ **[推断]** ST7701 系列 (依据: Rockchip `st7701` 驱动里就有 480×640/2-lane 的 2.8" 档位) |
| Waveshare 2.8" 的**屏侧 FPC 连接器型号** | ① wiki 接口定义节 (只有针位表) ② 商品页 Package Content (只有线材规格) ③ 官方 3D 图 `https://files.waveshare.com/upload/b/b3/2.8inch_DSI_LCD.zip` (内含 `2_8inch-dsi-lcd_asm.stp`, PRODUCT 名只有 `2_8INCH-480X640-LCD` / `2_8INCH-DSI-LCD-PCBA` 等, **无连接器料号**) ⇒ **未查到** |
| Waveshare 2.8" 的**背光电压/电流/PWM 能力** | ① 商品页 Details (无背光章节) ② wiki Features 只写 "Supports software control of backlight brightness", 但 15 针表里无背光引脚 ⇒ **背光电参数未查到**, 需实测或问原厂 |
| Densitron DMT028VGHMCMI-1A 的**针位表 / 连接器 / 背光 / 模组形态 / 采购渠道** | ① Rockchip 内核源码 (只有 compatible + mode + GIP, 无机械/电气) ② 公开搜索未找到原厂 datasheet ⇒ **未查到** |
| Samsung S6E63J0X03 的**针位表 / 在售模组 / 采购渠道** | ① 内核源码 (只有 compatible + mode + init) ② 公开搜索未找到原厂 datasheet ⇒ **未查到** |
| 视涯 0.49" 的 **FPC 针位表 / lane 数 (2 还是 4) / 供电脚定义** | ① 官方 datasheet PDF (只有机械尺寸与 "MIPI D-PHY 1 PORT, VESA DSC 3:1", **无针位表**) ② 官网 0.49" 页 (无) ⇒ **未查到**, 需走 B2B 问询 (sales@seeya-tech.com) |
| 视涯 0.49" 的**零售采购渠道 / 单价 / 交期** | 官网无商城, 只有"联系我们/发送表单" ⇒ **未查到** |
| RK3572 DSI 控制器的 **DSC 解码能力** | 本单未查 (超出本单范围, 属 ISS-125/D3) ⇒ **未查** |
| Waveshare 2.8" 的**交期** | 商品页无交期字段 ⇒ **未查到** |

---

## 8. 出处索引 (全部为原厂/官方资料)

| # | 来源 | 用在哪 |
|---|---|---|
| **[S1]** | Waveshare 官方 wiki「2.8inch DSI LCD」接口定义 + 特性: <https://www.waveshare.com/wiki/2.8inch_DSI_LCD> (中文同源 <https://www.waveshare.net/w/index.php?title=2.8inch_DSI_LCD&action=raw>) | §3.1 逐针表 / 特性 / 接线 |
| **[S2]** | Waveshare 官方商品页 (SKU 22028, 价格, Details 表, Package Content, DSI 型号对照表): <https://www.waveshare.com/product/2.8inch-dsi-lcd.htm> | §3.1 规格 / 价格 / **FPC 15PIN 1.0 pitch** |
| **[S3]** | Waveshare 官方 DSI 排线页 (15pin→22pin / dual-plug 22pin): <https://www.waveshare.com/product/dsi-cable-12cm.htm> | §3.1 Pi5 转接 |
| **[S4]** | Waveshare 官方 GitHub「Waveshare-DSI-LCD」(Pi4/Pi5 dtbo + WS_xinchDSI_Screen.ko + Backlight): <https://github.com/waveshare/Waveshare-DSI-LCD> | §3.1 init/driver 公开可得性 |
| **[S5]** | Raspberry Pi 官方 firmware 仓库 `boot/overlays/vc4-kms-dsi-waveshare-panel.dtbo` (已解出 `compatible=waveshare,2.8inch-panel`): <https://github.com/raspberrypi/firmware> | §3.1 init 官方来源 |
| **[S6]** | Rockchip 内核 `drivers/gpu/drm/panel/panel-sitronix-st7701.c` (`densitron,dmt028vghmcmi-1a` 2.8"/480×640/2-lane + GIP): <https://github.com/rockchip-linux/kernel> 分支 `develop-6.1` | §3.1 / §3.2 / §6 |
| **[S7]** | Rockchip 内核 `panel-samsung-s6e63j0x03.c` (1.61"/320×320/1-lane): 同上 | §3.3 / §6 |
| **[S8]** | Rockchip 内核 `panel-visionox-rm69299.c` (`visionox,rm69299-1080p-display`): 同上 | §5.3 / §6 |
| **[S9]** | Rockchip 内核 `panel-simple.c` 全部 79 个 panel 文件扫描 (含 `sharp,ls020b1dd01d` / `giantplus,gpm940b0` 两条 ≤3.2" **并口**条目): 同上 | §6 结论 2 |
| **[S10]** | 视涯科技官网 0.49" 产品页 (三个规格 + 下载直链): <https://www.seeya-tech.com/html/products/3971.html> | §5.1 / §5.2 |
| **[S11]** | 视涯科技官方 datasheet PDF (全彩): <https://www.seeya-tech.com/uploads/2021/01/010917/SeeYA%20Technology%20-%20049%20OLEDoS.pdf>; 单色绿: `.../SeeYA Technology - 049 Mono-G OLEDoS.pdf` | §5.2 全部参数 |
| **[S12]** | 视涯科技招股说明书 (上交所公开 PDF, 竞品对比表含 0.49"/1920×1080/对比度 50,000:1): <https://static.sse.com.cn/stock/disclosure/announcement/c/202506/002094_20250626_8Q5Z.pdf> | §5.1 交叉核对 |
| **[S13]** | Waveshare 官方 3D 图 zip (STEP 内 PRODUCT 名, 无连接器料号): <https://files.waveshare.com/upload/b/b3/2.8inch_DSI_LCD.zip> | §3.1 / §7 |

---

## 9. ★ 建议动作 (给项目总工, 本单**不执行**)

1. **屏选型拍板**: 建议 **Waveshare 2.8inch DSI LCD** (候选 1) 作为 demo 屏 (唯一"≤3.0 寸 + DSI + 公开逐针表 + 在售 + 官方 driver 生态"全中的件);
2. **屏座方案拍板**: 建议 §4.3 的 **方案 B (24 位/0.5mm 主座 + 15→24 转接线接 demo 屏)**, 别按 demo 屏把座定死;
3. **电源树**: 8HD 的 **12V BOOST + 限流 + PWM 整链划掉**, 背光链留位 DNP; USB-C 预算重算 (4.6W → ≈2.0–2.3W);
4. **DSI**: SoM 侧不动; 板→屏维持 4-lane 布线, demo 屏走 2-lane (dts `dsi,lanes=2`);
5. **★ISS-132 可以更新了**: 视涯 0.49" **全彩 (1800/3000 nits) 与单色绿 (20000 nits) 并存** ⇒ 请老板在 "全彩 / Mono-G" 之间选型 (影响 BOM 与"彩色显示"卖点);
6. **★ISS-133/D3 缩范围**: 面板侧 **DSC 3:1 已确认**, 剩下只查 "RK3572 DSI 能否解 DSC" 与 "视涯屏 lane 数 (2/4)" 两个点;
7. **实测清单 (落板前)**: Waveshare 2.8" 的驱动 IC / 背光电流 / 是否需外部复位 ⇒ 一次 dev 板实测同时把 §3.2 的 "同面板 ST7701 假设" 一起确认掉。

---

## 10. 自证

```bash
cd projects/smart_glasses
python3 state/merge.py && python3 state/issue_check.py && python3 state/gate_check.py
```
★**本单只写了 `HW/DISPLAY_SMALL_SCREEN_OPTIONS.md` 与 `HW/display_small_options.json` 两个文件**, 未改网表 / 板文件 / issue_log / tracker / STATE.yaml。
