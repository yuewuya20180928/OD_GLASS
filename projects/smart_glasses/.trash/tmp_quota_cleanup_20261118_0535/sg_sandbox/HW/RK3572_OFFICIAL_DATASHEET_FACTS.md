# RK3572 官方 datasheet 事实卡 (Rev 1.1)

> 交付: ISS-181 周更新 · hw-lead · 2026-11-06
> ★**本卡解决一个 main 的高危阻塞**: STATE 里那条 `RK3572 无官方 Brief Datasheet (本项目全部证据等级 = [媒体]/[模组厂口径])` —— **官方 datasheet 就在项目库里** (`HW/RK3572_PIN_TABLE/RK3572_datasheet_V1.1.pdf`), 47 页 / 2,414,580 B / md5 `c0e3763036e2f6a3e8a2f68f2254851d` / PDF 元数据 Author=Rockchip, CreationDate=2026-04-14 11:32:39 CST。
> ★**下载来源** (2026-11-02 当时走的开源渠道, 未发邮件/未联系代理): `https://rockchip.fr/RK3572%20datasheet%20V1.1.pdf`
> ★**证据等级 = [官方]** (Rockchip 原厂书面), 不是 [媒体]/[模组厂口径]。
>
> **自证**: `python3 HW/rk3572_official_facts_check.py` (rc=0, 逐条断言本页数字都能在 PDF 文本层 grep 到)

---

## 1. 封装 (§1.2 Package Type / §2 Package Information)

| 项 | 官方值 | 出处 | 等级 |
|---|---|---|---|
| 封装代号 | **FCCSP550L** | 文本层 L827 / L855 (Table 2-1 Order Information) | [官方] |
| 本体尺寸 | **14.3 mm × 15.5 mm** | L827 | [官方] |
| 球尺寸 | **0.25 mm** | L827-828 | [官方] |
| 球间距 | **0.42 mm & 0.52 mm & 0.65 mm 混合** | L828 | [官方] |
| 球数 | **550** (FCCSP550L, 命名即球数) | L827 / §2.6 引脚表 550 项 | [官方] |
| MSL | 3 | §2.4 | [官方] |
| 球材料 | SnAgCu | §2.5 | [官方] |
| 包装 | 98 PCS / Tray | Table 2-1 | [官方] |
| 球阵列图 | Fig 2-2 Top View / Fig 2-3 Bottom View / Fig 2-4 Side View / Fig 2-5 Dimension (p.19-21) | 目录 L72-76 | [官方] |

★**这块直接改写项目里两个旧结论**:
1. `HW/CHIP_SELECTION_DECISION.md` L43 与 `HW/CHIP_SCORING_RESULT.md` L175 把 FCCSP550L 14.3×15.5mm 标成 **[媒体]** ⇒ ★**现在升到 [官方]**。
2. ★**球间距是 0.42/0.52/0.65 混合, 不是单一 pitch** ⇒ 项目此前"pitch 未知 ⇒ 逃线层数只能 [推算]" (ISS-128 的原话) **这条前提作废**: ★**最小 pitch = 0.42 mm** ⇒ 对照项目自己定的判据 (`≥0.4mm 可行 / 0.35mm 极限 / ≤0.3mm 须 HDI`): **RK3572 落在 0.42 ⇒ 可行区间, 不需要 HDI** ⇒ ★**ISS-128 那个"逃线 9 层破 4-6 层锁死"的前提需要按 0.42mm 重算, 不能继续按 pitch 未知的保守值算**。

★**注意**: 本项目 **demo 主板用的是 SoM 模组 (FET3572-C) 的 BTB (0.4mm pitch), 不是裸 SoC 的 FCCSP** ⇒ 上面 0.42mm **不适用于当前布线板的出脚约束** (那个约束实测就是 0.4mm pitch, 见 `HW/PCB/ROUTING_REPORT.md`)。两条 pitch 不要混。

## 2. 内存 (§1.2.4)

| 项 | 官方值 | 出处 | 等级 |
|---|---|---|---|
| 类型 | LPDDR4 / LPDDR4X / LPDDR5 / LPDDR5X | L171-172 | [官方] |
| 速率档 | **LPDDR4(X)-4266 / LPDDR5(X)-5500** (JEDEC) | L216 | [官方] |
| 位宽 | **单通道 32 bits** | L217 | [官方] |
| 容量 | 最大 16GB | L219 | [官方] |

★**订正一处旧口径**: `HW/CHIP_SHORTLIST_EVIDENCE.md` L88 里 RK3576 写"官方框图标 216bit = 2×16bit" —— ★**那是 RK3576, 不是 RK3572**; **RK3572 官方就是单通道 32bit** ⇒ ★**DDR 带宽账要按 32bit 重算, 不能沿用 216bit 的数**。

## 3. ISP (§1.2.10 Image Signal Processor V3.5)

| 项 | 官方值 | 出处 | 等级 |
|---|---|---|---|
| 通路 | **单通道 ISP** | L488 | [官方] |
| 像素能力 | **12M pixels** | L488 | [官方] |
| 最大输入 | **4096 × 3072** | L490 | [官方] |
| 最小输入 | 264 × 264 | L491 | [官方] |
| VICAP 格式 | raw8/raw10/raw12/raw14/raw16 | L486 | [官方] |

★**这直接钉死 ISS-062 R-GEO 问03 (ISP 吞吐余量) 的官方天花板**: 12 MPix/frame ⇒ ★**1080p60 = 1920×1080×60 = 124.4 MPix/s, 对 12 MPix 单帧能力 ⇒ 余量 = 12M/2.0736M ≈ 5.8× (余量 82.7%)**。⇒ ★**"余量 1.9%" (250 vs 497.7 MP/s 那套) 是按 RK3576 的 16M/其他口径算的, 对 RK3572 不成立** ⇒ ★**Q03 的两个矛盾口径 (1.9% vs 50.7%) 都不适用于 RK3572, 这是第三个值 82.7%**。

## 4. 显示输出 (★Q16 决定性证据)

| 接口 | 官方值 | 出处 | 等级 |
|---|---|---|---|
| HDMI/eDP TX | **One HDMI/eDP TX combo PHY** | L626 | [官方] |
| HDMI | v2.1, 4K@60, RGB/YUV444/422/420 8/10bit, HDCP 2.3/1.4, CEC/ARC | L627-635 | [官方] |
| eDP | v1.3, **compliant with DisplayPort v1.2**, 主链路 4 lane, RBR 1.62 / HBR 2.7 / **HBR2 5.4 Gbps/lane**, 4K@60, PSR, EDID | L637-648 | [官方] |
| MIPI DSI TX | **DSI-1.2, 4 data lane, ≤2.5 Gbps/lane** | L652-654 | [官方] |
| 并行输出 | RGB / BT.656 / BT.1120, ≤1920×1080@60, ≤8bit | L657-661 | [官方] |
| EBC | E-Ink EPD, ≤1872×1404, 16bit, 32 级灰, Direct/LUT/3-window | L664-671 | [官方] |
| VO 复用 | "Each Video Port may connect to any of HDMI/eDP/DSI/PARA interface" | L581 | [官方] |

★★**这回答了 Q16 (显示 TX 接口 DSI TX / DP TX / 两者) —— 对 RK3572 是"两者都有"**:
- **DSI TX**: DSI-1.2 4-lane @2.5Gbps (光机走这条)
- **DP TX**: eDP v1.3 (声明 compliant with DP v1.2), 4 lane HBR2 5.4Gbps/lane ⇒ **标准 DP 协议存在**
- ★**但 eDP 是 DP 的"嵌入式"封装形态** (主链路 + AUX + HPD, 无独立 DP 连接器) ⇒ **能直连标准 DP 口的物理器件仍在 [0数据]**, 不能凭 "compliant with DisplayPort v1.2" 就断言"能插 DP 显示器"。
⇒ ★**结论写法**: "SoC 侧 **DSI TX 与 DP 协议 (eDP) 都有**; 但**能否直插标准 DP 连接器 = [0数据]**, 要看 FET3572-C 模组把哪几根 TX 引出来了 ⇒ **须查 SoM 模组引脚图, 不看 SoC datasheet**"。

★**这同时打掉了 `HW/CHIP_SELECTION_DECISION.md` L12 "无 DP" 那个 [媒体] 口径** ⇒ RK3572 **有** DP TX 能力 (eDP) + HDMI 2.1 ⇒ **"无 DP 所以要加桥接芯片" 这条推理链要重写**。

## 5. 电源域 (§3.1 Absolute Maximum / §3.2 Recommended Operating)

| 电源组 | 绝对最大 | 推荐工作 | 出处 | 等级 |
|---|---|---|---|---|
| PMUIO0_VCC1V8 / VCCIO0_VCC1V8 | **1.8V only, -0.5 ~ 1.98 V** | 1.65/1.8/1.95 V | p.39 Table 3-1 + Table 3-2 | [官方] |
| PMUIO1_VCC, VCCIO1~6_VCC | **1.8V/3.3V, -0.5 ~ 3.63 V** | 2.7/3.3/3.6 V | 同上 | [官方] |
| VCCIO7_VCC | **1.2V/1.8V, -0.5 ~ 1.98 V** | 1.08/1.2/1.32 V | 同上 | [官方] |
| CPU_BIG_DVDD / CPU_LIT_DVDD | — | 0.675/0.75/**1.0** V | Table 3-2 | [官方] |
| GPU_DVDD / NPU_DVDD | — | 0.675/0.75/0.918 V | Table 3-2 | [官方] |
| LOGIC_DVDD | — | 0.675/0.75/0.825 V | Table 3-2 | [官方] |
| PMU_LOGIC_DVDD0V75 | — | 0.675/0.75/0.825 V | Table 3-2 | [官方] |
| DDRPHY_DVDD / DDRPHY_PLL_DVDD | — | 0.675/0.75/0.9 / 0.8925 V | Table 3-2 | [官方] |
| DDRPHY_VDDQ / VDDQH | -0.3 ~ 0.95 / 1.25 V | 0.675/0.75/0.825 / 1.05 V | Table 3-1 / 3-2 | [官方] |
| 独立电源域 | **PMU 支持 23 个可分别上下电的电源域** (软件控制) | — | L259 | [官方] |
| Tj 绝对最大 | 125 ℃ (Storage -40~125 ℃) | — | Table 3-1 / 4.1 | [官方] |

★**★这直接结掉 sw-lead 的 `iss148_rk3572_gpio0_vccio_domain_check` 这条 need**:
- 之前的说法: "本地 txt 把 VCCIO1_VCC 归在 1.8V only 一栏 ⇒ SoC 侧 GPIO0 只允许 1.98V ⇒ 整条 I2C_A 电平域要重新设计" —— ★**这个推断是错的**。
- ★**实测(p.39 高分辨率渲染图, 不是扁平文本猜)**: `1.8V/3.3V GPIO supply voltage` 那一行的 net 名是 **PMUIO1_VCC + VCCIO1_VCC + VCCIO2_VCC + VCCIO3_VCC + VCCIO4_VCC + VCCIO5_VCC + VCCIO6_VCC** (max **3.63 V**); `1.8V only` 那行只有 **PMUIO0_VCC1V8 + VCCIO0_VCC1V8** (max 1.98 V); `1.2V/1.8V` 那行只有 **VCCIO7_VCC**。
- ★**扁平文本 (pdftotext) 把这一段的多行单元格错位了** ⇒ 之前那句"VCCIO1_VCC 属 1.8V only"是**排版假象**, 不是官方口径。★**渲染图为准**: `HW/RK3572_PIN_TABLE/figs/p39_gpio_crop2.png`。
- ★**⇒ 结论**: **VCCIO1_VCC 能上 3.3V (max 3.63V)** ⇒ **I2C_A 走 3.3V 上拉在 SoC 侧不违规** ⇒ ★**原 need 里"整条 I2C_A 降 1.8V / 加电平转换"那条结论作废** ⇒ 只剩 AR0234CS 侧自己的约束 (VIN ≤ VDD_IO+0.3 = 3.1V ⇒ 上拉必须 ≤3.1V ⇒ 2.8V 成立, 3.3V 不成立) ⇒ ★**最终 I2C_A 上拉 = 2.8V, 但理由只剩 sensor 侧 abs-max 一条, 不再有 SoC 侧那条**。

★**但是 (必须说清)**: ★**datasheet 没有 GPIO bank → VCCIO 组的对应表**。它只给"VCCIO1_VCC 这个网名属于哪一档电压"。I2C0_SCL/SDA = **GPIO0_B0 (球 1K21) / GPIO0_B1 (球 U32)** (§2.6 引脚表 L1258-1260), ★**GPIO0_B0/B1 具体挂哪个 VCCIO 供电组 = [0数据]** ⇒ ★**严格结论: "VCCIO1_VCC 可上 3.3V" 是官方事实; "I2C0 这两根脚能不能上 3.3V" 仍需 SoM 模组 (FET3572-C) 的 IO 域文档或 BSP dtsi 佐证** ⇒ **本卡不推翻 sw-lead 那条 need, 只把它从"数据全无"降级为"只剩 SoM 侧 bank→VCCIO 映射这一个问题"**。

## 6. 散热 (§4 Thermal Management)

| 项 | 官方值 | 等级 |
|---|---|---|
| ψJT / θJA / θJB / θJC | **全部 TBD** (Table 4-1 四行全是 TBD) | [官方] = 官方自己没给 |
| 绝对最大结温 Tj | 125 ℃ | [官方] |

★**⇒ SoC 域功耗/热阻官方口径 = 官方文档本身是 TBD** ⇒ ★**ISS-077 / ISS-130 那个"皮肤 43℃ 红线"结论仍不能用官方 datasheet 支撑, 证据等级维持 [推算]** ⇒ ★**别把"找到了官方 datasheet"误当成"功耗账有官方依据了"**。

---

## 7. 这张卡**没有**回答的 (留给下周 / 留给他人)

1. ★**电源域电流上限** (每个 VCCIO/AVDD 允许多少 mA) —— Table 3-1 只给电压上限, 不给电流 ⇒ **[0数据]**
2. ★**GPIO0_B0/B1 → VCCIO 组的映射** —— datasheet 没有 bank 表 ⇒ 需 SoM 引脚图 / BSP dtsi
3. ★**每个电源域的功耗数字** —— 官方 TBD
4. ★**SoM (FET3572-C) 把哪些 TX/IO 引出来了** —— Q16 的最后一环, 查 SoM 文档, 不查 SoC

---

## 8. 自证 (一条命令复现本页每个数字)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 HW/rk3572_official_facts_check.py     # rc=0 ⇒ 每个断言都能在 PDF 文本层 grep 到
```

脚本逐条断言: FCCSP550L / 14.3mmx15.5mm / ball 0.25mm / pitch 0.42&0.52&0.65 / 32bits / 4266 / 5500 / 12M pixels / 4096x3072 / 264x264 / HDMI v2.1 / eDP v1.3 / DisplayPort v1.2 / 5.4Gbps / DSI-1.2 / 2.5Gbps / BT.656 / BT.1120 / 23 separate power domains / 1.98V / 3.63V / 1.08V / CPU_BIG_DVDD 1.0V / NPU_DVDD 0.918V / Tj 125℃ —— **每条都带 PDF 文本层行号**, 任何一条 grep 不到就 rc≠0。
