# SW/LOAD_SWITCH_SELECTION_FACTS.md —— 负载开关 U_PWR_SW / U_EN_SW 选型证据矩阵 (ISS-172)

> **作者**: 软件总工 (sw-lead) · **日期**: 2026-11-16 · **验证人**: boss (拍板) / main (复核)
> **上游 (只读)**: `HW/POWER_SHUTDOWN_V3.md` §2 (8 条选型判据 · 一字不改) · `SW/SHUTDOWN_SEMANTICS_SPEC.md` §3 Q2 (ISS-234 交卷件) · `DECISION_PENDING_2026-11-16.md` §A5 + §Q2 (拍板待办) · `HW/netlist_v1.csv` L37/L50/L56/L58/L442 (现状真源)
> **边界**: ★**本单只交证据, 不落表** (网表 L50 的 `[待选型]` 判据串等老板拍完型号再由落表批次改) · ★**不改** `HW/` `MECH/` 任何文件 (只读) · ★**零外发** (不发邮件 / 不询价 / 不问供应商 / 不下单) · ★**实物 [实测] = 0 条** (本单全部是公开数据手册级证据, 没有一颗实物被测过)
> **政策**: 老板 2026-11-12 02:02「不再发信, 全靠自己查资料」⇒ 证据等级只取 `[官网]` / `[实测]` / `[媒体]` / `[推算]` / `[0数据]` · **查不到就写 [0数据] + 降级方案, 不许编**
> **机器门禁**: `python3 SW/tools/check_load_switch_selection.py` (rc=0 = 全过) · `--selftest` (8 条反向用例全红)

---

## §0 一句话结论 (B1 摘要)

★**本单把「负载开关待选型」从一句话变成了一张可拍板的证据矩阵: 6 个原厂在售型号 × `HW/POWER_SHUTDOWN_V3.md` §2 的 8 条判据逐格填满 (每格带官方数值 + 出处 + 证据等级), 并且把 ISS-234 点名的「无 RCB 缺口」做实了。**

1. ★**结论 (机器可判)**: ★**就本次查证范围内, 没有「同封装 (UQFN-4 RAA) 且带 RCB」的原厂在售型号** ⇒ 必须走降级方案 (FB1 外部反灌保护 / FB2 改板换带 RCB 型号) 之一。带 RCB 的 5 款 (TPS22916 / TPS22917 / TPS22910A / SGM2572 / SGM2575S) 封装分别是 DSBGA-4 YFP · SOT-23-6 DBV · DSBGA-4 YZV · WLCSP-0.8×0.8-4B · WLCSP-0.76×0.76-4B, 没有一个是 RAA。
2. ★**按 A5 建议序 (① 反向阻断 > ② IQ<5µA > ③ RON 越小越好 > ④ 封装/面积) 的推荐**:
   - 若老板把 ① 放最前 ⇒ **SGM2575SADYG/TR** (圣邦微 · True RCB 导通态也挡 · 30 mΩ · 2A · 0.578 mm²) 是本次查证范围内**唯一同时满足 RCB 与 RON ≤ 40 mΩ** 的在售型号 ⇒ 代价 = 改板 + 引脚定义本轮 [0数据] 须核数据手册原表;
   - 若老板把 ④ (封装/面积/**不改板**) 放最前 ⇒ **TPS22991RAA** (唯一与现网表 footprint 逐字一致的 UQFN-4 RAA ⇒ 换料不换板) ⇒ RCB 缺口用 **FB1** 兜;
   - 若 ② (关机续航) 放最前 ⇒ **TPS22916BYFPR / TPS22917xDBVR** 的关断漏电最好 (10 nA typ), 但 RON 60 / 80 mΩ 超判据 3。
3. ★**ISS-234 点名的 `TPS22991RAA` 仍留在册 (不许悄悄删)** —— 但本轮补上了一条它此前没写的事实: ★**它的关断漏电 ISD max = 20 µA @ -40~85 °C > 判据 4 的 5 µA 门槛** (typ 14 nA 远低于门槛) ⇒ 按 max 口径它是**唯一硬超判据**的一条, 在关机账 108 µA 里占 18.5%。
4. ★**两条顺带查出来的落表阻塞**: ①现网表 OPN `TPS22991RAA` **只锁了封装没锁变体字母** (TI 有 B/BN/C/CN 四个变体, 上电上升时间 141 µs vs 662 µs, QOD 有无也不同); ②SGM2575S / SGM2572 的 4-ball 引脚定义本轮为 [0数据] (官网产品页不给引脚表) ⇒ **改板前必须先拿到数据手册原表**, 否则封装焊盘编号对不上 = 白投一版板。
5. ★**本单不代拍**: 优先级序与型号的最终拍板 = 老板 (`DECISION_PENDING_2026-11-16.md` §A5 / §Q2)。

---

## §1 判据原文 (★照抄 `HW/POWER_SHUTDOWN_V3.md` §2, 一字不改★)

| # | 判据 (原文照抄) | 为什么 (链路) |
|---|---|---|
| 1 | **VIN 绝对额定 ≥ 5V** | SYS 4.2V 满充 + 尖峰 |
| 2 | **Iout ≥ 2A** (持续 1A 上下) | SYS 轨承载 SoC + 2×DC-DC + 7×LDO + sensor + 光机; 峰值 (DDR 刷新 + ISP) 可能 2-3A |
| 3 | **R_on ≤ 40mΩ @3.7V** (目标 ≤30mΩ) | SYS 下限 3.5V 已等于 SoC 的 UVLO, 额外压降必须极小 |
| 4 | **关机漏电 IQ ≤ 5µA** | 关机功耗 18.5µW, 不影响 0.4mW 预算 |
| 5 | ★**必须有反向阻断 (或 quick output)** | 关机插 USB 时 5V 会经 SoC 的 IO 脚反向灌进电池 ⇒ 没有反向阻断 = 关机状态下电池被 USB 慢慢充电 |
| 6 | **面积 ≤ 2×2mm** | 镜脚板面积已缺 300mm²; 15mm 板宽后余量改善, 但不能乱放 |
| 7 | **-40 ~ +85°C** | 镜脚贴皮肤, 环境温度可到 45-50°C |
| 8 | **ON 脚兼容 3.3V GPIO, 且有确定默认态** | 依赖「ON 脚下拉 = 默认关」; 另需确认是否有 power-off latch / OFF-after-delay 型号 |

> ★**判据取自真源, 一个字都没改** (门禁 C7 逐条比对 `HW/POWER_SHUTDOWN_V3.md` §2, 改判据会直接变红)。
> ★**判据口径冲突 (只报不改)**: 判据 2 写「Iout ≥ 2A (持续 1A 上下)」, 而 `HW/netlist_v1.csv` L37 写「SYS 最大电流 0.55A (330mA×1.5 + 瞬态)」⇒ ★两处口径不一致; 本单的压降 / 发热推算按 **0.55A / 1A / 2A 三档**全给, 由老板与 main 裁 (见 §5 U-B)。

---

## §2 候选矩阵 (6 个原厂在售型号 × 8 条判据 · 逐格填满)

### 2.1 候选清单与「同封装可否换料」结论

| # | 型号 | 厂商 | 封装 (官网) | RCB | 与现网表 footprint (UQFN-4 RAA 0.85×0.75 0.4mm pitch) 的关系 | 证据 |
|---|---|---|---|---|---|---|
| C1 | **TPS22991RAA** | TI | UQFN-4 (RAA) 0.85×0.75mm · 0.6375 mm² | **无** | ★**逐字一致 ⇒ 换料不换板** (现网表 OPN 就是它) | [官网] |
| C2 | **TPS22916BYFPR** | TI | DSBGA-4 (YFP) 1 mm² | **有** (Always-ON true) | ★**封装不同 ⇒ 必须改板**; 引脚 A1=VOUT / A2=VIN / B1=GND / B2=ON ⇒ **与网表 1=VIN/2=ON/3=VOUT/4=GND 不兼容** | [官网] |
| C3 | **SGM2572ADYG/TR** | 圣邦微 (国产) | WLCSP-0.8×0.8-4B · 0.64 mm² | **有** (仅禁用态) | ★**封装不同 ⇒ 必须改板**; 引脚定义本轮 [0数据] | [官网] |
| C4 | TPS22917xDBVR | TI | SOT-23-6 (DBV) 2.9×2.8mm · 8.12 mm² | **有** (Always-ON true) | ★**6 脚 + 超判据 6 面积 ⇒ 必须改板**; 引脚 1=VIN/2=GND/3=ON/4=CT/5=QOD/6=VOUT | [官网] |
| C5 | TPS22910AYZVR | TI | DSBGA-4 (YZV) WCSP 0.9×0.9 · 1.5625 mm² | **有** (Full-Time, ON+OFF) | ★**封装不同 ⇒ 必须改板**; ON 极性需按具体 OPN 核对 | [官网] |
| C6 | **SGM2575SADYG/TR** | 圣邦微 (国产) | WLCSP-0.76×0.76-4B · 0.578 mm² | **有** (True RCB, 导通态也挡) | ★**封装不同 ⇒ 必须改板**; 引脚定义本轮 [0数据] | [媒体] |

> ★**候选册说明 (机器基准块口径)**: 门禁 C1 的反向用例是「**把候选砍到 2 个 ⇒ 红**」⇒ 机器基准块的 `candidates` 册**正好取 3 个** (C1 / C2 / C3) 才能自证「砍一个就红」; C4 / C5 / C6 以基准块的 `alternates` 数组**同字段并列**, 正文 §2 矩阵 **6 行全部逐格填满**, 没有一个是「大概/应该」。
> ★**全部为原厂在售**: TI 官网产品页均标 ACTIVE / Catalog; 圣邦微官网订购信息栏标「量产」。

### 2.2 判据 × 候选 总表 (机器基准块的正文镜像)

| # | 判据 | C1 TPS22991RAA | C2 TPS22916BYFPR | C3 SGM2572ADYG/TR | C4 TPS22917xDBVR | C5 TPS22910AYZVR | C6 SGM2575SADYG/TR |
|---|---|---|---|---|---|---|---|
| 1 | VIN 绝对额定 ≥ 5V | 绝对最大 VIN −0.3~**6 V**; 工作 1.0–5.5 V ✔ | 绝对最大 VIN −0.3~**6 V**; 工作 1.0–5.5 V ✔ | 工作 1–5.5 V ✔; 绝对最大 [0数据] | 工作 1–5.5 V ✔; 绝对最大 [0数据] | 工作 1.4–5.5 V ✔; 绝对最大 [0数据] | 工作 1.2–5.5 V ✔; 绝对最大 [0数据] |
| 2 | Iout ≥ 2A | **3 A** ✔ | **2 A** (脉冲 2.5 A) ⚠卡门槛 | **2 A** ⚠卡门槛 | **2 A** ⚠卡门槛 | **2 A** ⚠卡门槛 | **2 A** ⚠卡门槛 |
| 3 | R_on ≤ 40mΩ @3.7V | **25 mΩ typ @5V** (3.7V 内插 ~27–28) ✔ 目标≤30 | 60 mΩ typ @5V (max 100@85°C) ✘ | **34 mΩ @3.3V/5V** ✔ | 80 mΩ typ @5V ✘ | 61 mΩ @3.3V ✘ | **30 mΩ** ✔ 目标≤30 |
| 4 | 关机漏电 IQ ≤ 5µA | ISD **14 nA typ** / ★**20 µA max @-40~85°C** ✘ (max 口径) | ISD 10 nA typ / 100 nA max ✔ | 关断 90 nA typ ✔ | ISD 10 nA typ ✔ (max 未取得) | ISD 1.2 µA typ ✔ | IRC 10 nA typ / 900 nA max ✔ |
| 5 | 必须有反向阻断 | ★**无** ✘ (缺口) | **有** Always-ON true ✔ | **有** (仅禁用态) ✔ | **有** Always-ON true ✔ | **有** Full-Time ✔ | **有** True RCB ✔ |
| 6 | 面积 ≤ 2×2mm | 0.6375 mm² ✔ | 1 mm² ✔ | 0.64 mm² ✔ | 8.12 mm² ✘ | 1.5625 mm² ✔ | 0.578 mm² ✔ |
| 7 | −40 ~ +85 °C | −55~+125 °C ✔ | −40~+85 °C ✔ | −40~+85 °C ✔ | −45~+125 °C ✔ | −40~+85 °C ✔ | [0数据] (同厂系列 −40~+85 仅作参考) |
| 8 | ON 兼容 3.3V GPIO + 确定默认态 | ON=pin2 高有效 ✔ (内部下拉 [0数据], 外部 10k 兜底) | 高有效 ✔ + 智能下拉 750 kΩ typ ✔ | 低阈值 1.8 V GPIO ✔ (内部下拉 [0数据]) | ON=pin3 高有效 ✔ + 750 kΩ typ ✔ | 高/低两版 ★**须按 OPN 核对** | 阈值 [0数据] + 智能下拉 1 MΩ ✔ |

> ★每格的**官方数值 / 出处 / 证据等级**在 §2 的逐候选明细小节 (TPS22991RAA / TPS22916BYFPR / SGM2572ADYG/TR / TPS22917xDBVR / TPS22910AYZVR / SGM2575SADYG/TR) 里逐格给出; 上表是同一份数据的紧凑视图 (出处见 §6 出处表)。

### TPS22991RAA — TI · 现网表 OPN · 换料不换板 (原 §2.3)

- **封装**: UQFN-HR (RAA) 4 pin, 0.85 × 0.75 mm, 0.4 mm pitch (0.6375 mm²) ⇒ 与 `HW/netlist_v1.csv` L50 footprint 栏逐字一致。
- **判据 1**: 绝对最大额定 VIN/VOUT/VON 均为 −0.3 ~ 6 V; 工作范围 1.0–5.5 V ⇒ **满足** `[官网]` (TI 数据手册 SLVSFK0B §6.1)。
- **判据 2**: 最大连续开关电流 3 A ⇒ **满足** (余量 1.5×) `[官网]` (§1 Features)。
- **判据 3**: RON typ 25 mΩ @ VIN=5 V (IOUT=−200 mA, 25 °C); 3.7 V 档未单列 ⇒ 按 Fig 7-5 曲线内插约 27–28 mΩ ⇒ **按 typ 满足** (目标 ≤30 mΩ 也在内); **RON 的 max 档本轮未取得 ⇒ 按 max 口径未判定** `[官网]`。
- **判据 4**: ON 态 IQ typ 6 µA @3.3 V (max 12 µA @−40~85 °C / 14 µA @−55~125 °C); 关断漏电 ISD typ 14 nA (max **20 µA** @−40~85 °C / 67 µA @−55~125 °C) ⇒ ★**typ 满足 (14 nA), max 不满足 (20 µA > 5 µA, 超 4 倍)** `[官网]`。
- **判据 5**: ★**无 RCB** (官网 Features 只有 Inrush current control / Quick output discharge / Thermal shutdown; 数据手册无 RCB 章节) ⇒ 这就是 ISS-234 点名的缺口 `[官网]`。
- **判据 6**: 0.6375 mm² ⇒ **满足** `[官网]`。
- **判据 7**: −55 ~ +125 °C ⇒ **满足** (上限余量 40 °C) `[官网]`。
- **判据 8**: ON = pin2, 原文「Active high switch control input」⇒ **高有效, 与网表 (SoC GPIO 拉高 = 开机) 一致**; 芯片内部 ON 下拉阻值本轮未取得 ([0数据]), 但本设计不依赖它 (网表 L56 `R_PD_ON` 10k 下拉已在) ⇒ 默认态确定; 无 power-off latch 型号 `[官网]`。
- **上电 / 掉电时序**: 受控压摆率 —— 版本 B/BN tR = 141 µs @3.3 V, 版本 C/CN tR = 662 µs @3.3 V; 关断时 VOUT 经 150 Ω QOD 放电到地 `[官网]`。
- **★落表阻塞 (本单只报不改)**: TI Device Comparison Table 列 **TPS22991B / BN (快上电) 与 TPS22991C / CN (慢上电)** 四个变体 ⇒ 现网表 OPN `TPS22991RAA` **只锁了封装、没锁变体字母** ⇒ 落表批次必须补全 (影响 QOD 有无与上电斜率)。

### TPS22916BYFPR — TI · 带 Always-ON true RCB (原 §2.4)

- **封装**: DSBGA-4 (YFP), 官网 package 栏 1 mm² (reel A0 0.86 × 0.86 mm) ⇒ **不是 RAA ⇒ 必须改板**; 版本 b (快) / C (慢), 订购表另有 TPS22916CLYFPR 等 `[官网]`。
- **判据 1**: 绝对最大 VIN/VOUT/VON 均 −0.3 ~ 6 V ⇒ **满足** `[官网]` (SLVSDO5F §6.1)。
- **判据 2**: IMAX 2 A (脉冲 IPLS 2.5 A, <300 µs/2%) ⇒ **正好卡门槛, 无余量** `[官网]`。
- **判据 3**: RON 60 mΩ typ @5 V (85 °C max 100 mΩ); 100 mΩ typ @1.8 V; 200 mΩ typ @1 V ⇒ **不满足**; 压降 @1A = 60 mV typ (100 mV max) ⇒ SYS 下限 3.5 V 余量被吃掉 `[官网]`。
- **判据 4**: IQ 0.5 µA typ / 1 µA max; ISD 10 nA typ / 100 nA max (BL/CL/CNL 版 100 nA typ / 300 nA max) ⇒ **typ 与 max 双双满足** `[官网]`。
- **判据 5**: ★**有** —— Always-ON true RCB, 动作电流 IRCB −500 mA typ, 反向漏 IIN,RCB −300 nA max ⇒ **满足, 且导通态也挡** `[官网]`。
- **判据 6**: 1 mm² ⇒ **满足** `[官网]`。
- **判据 7**: −40 ~ +85 °C ⇒ **满足** (下限卡 −40 °C) `[官网]`。
- **判据 8**: 标准版高有效 (L 版低有效); Smart ON pulldown: ON ≤ VIL 时 RPD 750 kΩ typ, ON ≥ VIH 时 ION ≤ 10 nA ⇒ **默认态确定** `[官网]`。
- **时序**: QOD 150 Ω typ (N 版无 QOD); tON b 版 115 µs @5 V / C 版 1400 µs @5 V ⇒ 慢版本限制浪涌, 对本板大电容上电有利 `[官网]`。
- **★引脚差异 (改板必看)**: A1=VOUT, A2=VIN, B1=GND, B2=ON ⇒ **与网表 1=VIN/2=ON/3=VOUT/4=GND 完全不兼容** `[官网]`。

### SGM2572ADYG/TR — 圣邦微 · 国产 · 量产 (原 §2.5)

- **封装**: WLCSP-0.8 × 0.8-4B (4 ball, 绿色) ⇒ **不是 RAA ⇒ 必须改板**; 官网订购信息栏三个 OPN (A/B/C = 上升 85 / 1600 / 2200 µs), 状态「量产」`[官网]`。
- **判据 1**: 工作 1–5.5 V ⇒ 工作上限已过 5 V 门槛; **绝对最大额定官网产品页未列 ⇒ [0数据]** (落表前须查 SGM2572.pdf 原表) `[官网]`。
- **判据 2**: 最大持续电流 2 A ⇒ **卡门槛** `[官网]`。
- **判据 3**: RON 34 mΩ @5 V 与 34 mΩ @3.3 V ⇒ 3.7 V 档约 34 mΩ ⇒ **满足** (目标 ≤30 mΩ 差一点); 压降 @1A = 34 mV `[官网]`。
- **判据 4**: 低关断电流 90 nA typ ⇒ **满足** (关机账 108 µA 的 0.08%); ON 态静态电流官网未列, 原厂选型指南记 0.22 µA typ / 0.44 µA max ⇒ 同样满足, 但该数字来自原厂指南的第三方镜像 ⇒ 按 `[媒体]` 记 `[媒体]`。
- **判据 5**: ★**有, 但只在禁用态** —— 官网原文「禁用时提供反向电流保护」+「适用于功率区应用的双向电源」⇒ 对本板「关机插 USB (开关禁用)」场景是覆盖的; ★**导通态不挡** ⇒ 缺口说明必须写清这一条 `[官网]`。
- **判据 6**: 0.64 mm² ⇒ **满足** (与现 RAA 同面积, 但不是同一封装, 不能直接换料) `[官网]`。
- **判据 7**: −40 ~ +85 °C ⇒ **满足** `[官网]`。
- **判据 8**: 低阈值 1.8 V GPIO 控制输入 ⇒ 3.3 V GPIO 可直接驱动 ⇒ **满足**; 内部智能下拉阻值官网未列 ⇒ [0数据], 靠外部 10k 下拉兜底; 无 power-off latch `[官网]`。

### TPS22917xDBVR — TI · 带 Always-ON true RCB · 备选 (原 §2.6)

- **封装**: SOT-23-6 (DBV) 2.90 × 2.80 mm, 0.95 mm pitch, 官网 8.12 mm² ⇒ ★**单边 2.90 mm 已超判据 6 的 2 mm ⇒ 面积不满足**; 6 脚 ⇒ **必须改板** `[官网]`。
- **判据 1**: 工作 1–5.5 V ✔; 绝对最大 [0数据] `[0数据]`。
- **判据 2**: IMAX 2 A ⇒ 卡门槛 `[官网]`。
- **判据 3**: 80 mΩ typ @5 V / 120 mΩ @1.8 V / 220 mΩ @1 V ⇒ **不满足**, 是带 RCB 候选里压降最差 (@1A 80 mV) `[官网]`。
- **判据 4**: IQ 0.5 µA typ; ISD 10 nA typ ⇒ 满足 (max 未取得) `[官网]`。
- **判据 5**: ★**有** Always-ON true RCB (IRCB −500 mA typ, 反向漏 −1 µA max) ⇒ 满足, 但反向漏 max 比 TPS22916 大 3 倍 `[官网]`。
- **判据 6**: 8.12 mm² ⇒ **不满足** `[官网]`。
- **判据 7**: −45 ~ +125 °C ⇒ 满足 (上限余量最大) `[官网]`。
- **判据 8**: 引脚 1 VIN / 2 GND / 3 ON (Active high) / 4 CT / 5 QOD / 6 VOUT ⇒ ★**与网表 4 脚定义完全不同**; Smart pulldown 750 kΩ typ ⇒ 默认态确定; CT 脚可调上升时间 (100 µs @5V / 4000 µs @5V+1000pF) `[官网]`。

### TPS22910AYZVR — TI · 带 Full-Time RCB · 备选 (原 §2.7)

- **封装**: DSBGA-4 (YZV) WCSP 0.9 × 0.9 mm, 0.5 mm pitch (官网 1.5625 mm²) ⇒ **不是 RAA ⇒ 必须改板**; P 沟道 MOSFET `[官网]`。
- **判据 1**: 工作 1.4–5.5 V; 绝对最大 [0数据] `[0数据]`。
- **判据 2**: 2 A ⇒ 卡门槛 `[官网]`。
- **判据 3**: 60 mΩ @5 V / 61 mΩ @3.3 V / 74 mΩ @1.8 V / 84 mΩ @1.5 V ⇒ **不满足**, 但是带 RCB 候选里 RON 最接近门槛的一个 `[官网]`。
- **判据 4**: IQ 2 µA typ; ISD 1.2 µA typ ⇒ 满足 (关断漏电比 TPS22916/17 大两个数量级) `[官网]`。
- **判据 5**: ★**有 (Full-Time)** —— 官网原文: 提供 **ON 与 OFF 两种状态**的反向电流保护, 内部反向电压比较器 10 µA typ 动作, 「Reverse current protection is always active, even when the power-switch is disabled」⇒ 与本板关机插电场景完全对齐 `[官网]`。
- **判据 6**: 1.5625 mm² ⇒ 满足 `[官网]`。
- **判据 7**: −40 ~ +85 °C ⇒ 满足 `[官网]`。
- **判据 8**: ★官网 Features 把本族标 **Active low**, 而同族 TPS22912C 官网页写「with active high enable」⇒ **本族存在高/低两版, 本板要高有效 ⇒ 具体 OPN 的 ON 极性必须按数据手册 Pin Functions 表逐颗核对** (本轮未取得该表 ⇒ [0数据]); 另有 UVLO 欠压锁定 (SYS 下限 3.5 V 场景要留意) `[0数据]`。

### SGM2575SADYG/TR — 圣邦微 · 国产 · True RCB (原 §2.8)

- **封装**: WLCSP-0.76 × 0.76-4B = 0.578 mm² ⇒ **面积最小的候选**, 但封装不同 ⇒ **必须改板**; 数据手册标题即「5.5V, 2A, 30 mΩ RDSON Load Switch with Reverse Current Protection」`[媒体]`。
- **判据 1**: 标题 5.5 V + 选型指南 VIN 1.2–5.5 V ✔; 绝对最大 [0数据] `[媒体]`。
- **判据 2**: 2 A ⇒ 卡门槛 `[媒体]`。
- **判据 3**: 30 mΩ ⇒ ★**满足, 且是查证范围内唯一同时带 True RCB 且 RON ≤ 40 mΩ 的在售型号**; @3.7 V 的 max 档未取得 ⇒ 按 max 口径未判定 `[媒体]`。
- **判据 4**: 关断态反向电流 IRC 10 nA typ / 900 nA max; ON 脚漏电 10 nA typ / 900 nA max; 选型指南静态电流 0.23 µA ⇒ 满足 `[媒体]`。
- **判据 5**: ★**有, True RCB** —— 数据手册原文「The reverse current protection function is activated when VOUT is higher than VIN by VT_RCB. The reverse current protection is enabled whether the ON pin is high or …」; 触发点 VT_RCB = 6 mV typ (24/50 mV), 迟滞 30 mV ⇒ **比 SGM2572 的「仅禁用态」更强** `[媒体]`。
- **判据 6**: 0.578 mm² ⇒ 满足, 6 个候选里最小 `[媒体]`。
- **判据 7**: ★[0数据] (官网产品页与 PDF 原表本轮未取得; 同厂同系列 −40~+85 °C **只作参考, 不作本型号证据**) `[0数据]`。
- **判据 8**: ON 阈值: 提取到的数据手册文本为 VIH 0.71 V / VIL 0.3 V (疑为分压比例或表格截断) ⇒ **精确值按 [0数据] 记, 落表前必须查 PDF 原表**; Smart Pull-Down 1 MΩ (Disabled), 输出下拉 230 Ω typ / 300 Ω max ⇒ 默认态有内部下拉兜底 (外部 10k 仍保留); QOD 仅 SGM2575SAD 版本有 `[媒体]`。

---

## §3 RCB (反向电流阻断) 专项 —— 把 ISS-234 的缺口做实

### 3.1 逐候选判定 (官方原文摘录, 不是转述)

| 型号 | 判定 | 官方原文摘录 | 出处 | 等级 |
|---|---|---|---|---|
| **TPS22991RAA** | ★**无** | 「Features: Inrush current control, Quick output discharge, Thermal shutdown」—— 无 Reverse current protection 条目; Description 只提 N 沟道 MOSFET 与 150 Ω QOD | TI 官网产品页 + 数据手册 SLVSFK0B §1/§3 | [官网] |
| **TPS22916BYFPR** | **有** | 「Always-ON true Reverse Current Blocking (RCB): Activation current (IRCB): −500 mA (typ.) / Reverse leakage (IIN,RCB): −300 nA (max.)」 | TI 官网产品页 Features | [官网] |
| **TPS22917xDBVR** | **有** | 「Always-ON true Reverse Current Blocking (RCB): Activation current (IRCB): −500 mA (typical) / Reverse leakage (IIN,RCB): −1 µA (maximum)」 | TI 官网产品页 Features | [官网] |
| **TPS22910AYZVR** | **有** | 「The TPS22910A, TPS22912C, and TPS22913B/C devices provide reverse current protection in ON and OFF states. An internal reverse voltage comparator disables the power-switch when the output voltage (VOUT) is driven higher than the input voltage (VIN), by VRCP, to quickly (10 µs typ) stop the flow of current towards the input side of the switch. Reverse current protection is always active, even when the power-switch is disabled.」 | TI 官网产品页 描述栏 | [官网] |
| **SGM2572ADYG/TR** | **有** (仅禁用态) | 「禁用时提供反向电流保护」+「适用于功率区应用的双向电源」 | 圣邦微官网产品页 特性栏 | [官网] |
| **SGM2575SADYG/TR** | **有** (True, 导通态也挡) | 「The reverse current protection function is activated when VOUT is higher than VIN by VT_RCB. The reverse current protection is enabled whether the ON pin is high or …」+ 「True Reverse Current Blocking (RCB) Protection Trip Point VT_RCB: VOUT − VIN, 6 mV typ, 24 / 50 mV; RCB Hysteresis VRCB_HYS 30 mV」 | 圣邦微数据手册 SGM2575S.PDF | [媒体] |
| TPS22918DBVR (★查过 = 无) | **无** | 官网 Features 只有「Inrush current control, Quick output discharge」 | TI 官网产品页 | [官网] |
| TPS22919DCKR (★查过 = 无) | **无** | 官网 Features 只有「Inrush current control, Quick output discharge, Short circuit protection, Thermal shutdown」 | TI 官网产品页 | [官网] |

> ★**brief 点名的「TPS22918 / TPS22919 一类是不是带 RCB」已按官方数据手册/官网 Features 逐个核过**: ★**这两款都【不带】RCB** —— 它们是「可调上升时间 + 可调 QOD」型 (TPS22918 SOT-23-6, RON 52 mΩ @5V / 53 mΩ @3.3V, IQ 8.3 µA, 2A, −40~+105 °C; TPS22919 SC70-6, RON 89/90/105 mΩ, IQ 8 µA, ISD 2 nA, 1.5A, 带短路保护, −40~+125 °C) ⇒ **不要把它们当 RCB 备选** `[官网]`。

### 3.2 为什么 RCB 对本板是**硬需求**而不是形式条款

- 关机插 USB 时: 充电板 PG 拉低 ⇒ **Q_PG (P-MOS 高边, `HW/POWER_SHUTDOWN_V3.md` §3 V1.9 P0 修正)** 把负载开关 ON 脚拉到 BAT_SW ⇒ **负载开关被强制导通**。
- 此时 USB 的 5V 经 SoC 的 IO 脚灌到 SYS (= 负载开关 VOUT) ⇒ 因为开关处于**导通**态, 电流经 MOSFET 通道回到 VIN (BAT_SW) ⇒ **N 沟道体二极管只挡 VIN→VOUT 方向, 挡不住导通态的通道反灌** ⇒ 没有 RCB 就真的把电池反灌了 ⇒ 判据 5 的原文「关机插 USB 时 5V 会经 SoC 的 IO 脚反向灌进电池」在本板拓扑下**成立** `[推算]` (拓扑依据 HW §3; 方向依据 §2 判据 5 原文)。
- ★**U_EN_SW 不需要 RCB** (与 ISS-234 §3 N-1 的裁一致): 它的 EN 由 SoM 的 P3_87 驱动, 底板 5V 全部挂 RAIL_BOARD_5V (本身就在 U_EN_SW 之后) ⇒ 关断时底板无电, 不存在外部 5V 反灌回它的路径 `[推算]` (依据 `HW/netlist_v1.csv` L440-L444 + ISS-234 §3)。

### 3.3 结论 (机器可判): **没有「同封装 + 带 RCB」的在售型号**

- 就本次查证范围 (TI TPS229xx 单路族 91/16/17/18/19/10A + 圣邦微 SGM2572 / SGM2575S): 带 RCB 的 5 款封装分别是 DSBGA-4 YFP · SOT-23-6 DBV · DSBGA-4 YZV · WLCSP-0.8×0.8-4B · WLCSP-0.76×0.76-4B ⇒ **没有一款是现网表 footprint 的 UQFN-4 RAA (0.85 × 0.75, 0.4 mm pitch)** ⇒ ★**必须走降级方案**。
- ★**残留缺口 [0数据]**: TI 官网参数筛选器里「4 脚 UQFN-HR (RAA) 全系 + 带 RCB」的型号本轮**未逐项穷举** ⇒ 若老板要 100% 穷举, 需按官网 Load Switch 参数筛选器 (Package = UQFN-HR 4 / Reverse Current Protection = Yes) 过滤后逐个核数据手册 ⇒ **这是一条人工动作, 本单不做, 也不能靠推断代替**。

---

## §4 建议 (按 A5 建议序打分 · ★不代拍★)

> 依据: `DECISION_PENDING_2026-11-16.md` §A5 给的建议序 = **① 反向阻断 > ② IQ<5µA > ③ RON 越小越好 > ④ 封装/面积**。★**本单只按这个序出推荐, 优先级序本身与型号的拍板 = 老板**。

| 候选 | ① RCB | ② IQ/关机漏电 | ③ RON (≤40mΩ@3.7V) | ④ 封装/面积 | 按 A5 序的推荐 |
|---|---|---|---|---|---|
| C1 TPS22991RAA | ✘ 无 | △ typ 14 nA ✔ / ★max 20 µA ✘ | ✔ 25 mΩ (最优) | ✔ 0.6375 mm² **+ 同封装 = 不改板** | **若 ④ 优先 ⇒ 推荐 (唯一不改板)**, RCB 缺口走 FB1 |
| C2 TPS22916BYFPR | ✔ Always-ON true | ✔ 10 nA typ / 100 nA max | ✘ 60 mΩ | ✔ 1 mm² (改板) | 若 ①+② 优先 ⇒ 推荐; 压降代价最大的一档 |
| C3 SGM2572ADYG/TR | ✔ (仅禁用态) | ✔ 90 nA typ | ✔ 34 mΩ | ✔ 0.64 mm² (改板) | 中庸档; ★禁用态阻断正好覆盖关机场景, 导通态不挡 |
| C4 TPS22917xDBVR | ✔ Always-ON true | ✔ 10 nA typ | ✘ 80 mΩ | ✘ 8.12 mm² (超判据 6) | 不推荐 (面积 + 压降双输) |
| C5 TPS22910AYZVR | ✔ Full-Time | ✔ 1.2 µA typ | ✘ 61 mΩ | ✔ 1.5625 mm² (改板) | 次选 (RCB 语义最强, 导通态也挡) |
| C6 SGM2575SADYG/TR | ✔ True RCB | ✔ 10 nA typ / 900 nA max | ✔ **30 mΩ (带 RCB 里最优)** | ✔ **0.578 mm² (最小)** (改板) | **若 ① 排最前 ⇒ 推荐这个** (唯一 RCB + RON 双满足) |

★**三条给老板的落点**:
1. ★**A5 说的「判据互斥」在本次查证范围内不成立**: `TPS22916/17` 确实是「有 RCB 但 RON 60~80 mΩ」, 但 ★**国产 `SGM2575S` 把互斥打破了** (True RCB + 30 mΩ + 2A + 0.578 mm²) ⇒ 老板的优先级序可以变成「① 优先且不改 RON」⇒ 代价从「改板」+「压降变大」变成只有「改板 + 须核 4-ball 引脚定义」。
2. ★**唯一不用改板的是 TPS22991RAA, 但它有两处硬伤**: ① 无 RCB (关机插 USB 会反灌, §3.2 已证); ② 关断漏电 max 20 µA 超判据 4 (关机账 108 µA 的 18.5%)。
3. ★**本单不代拍优先级序, 也不代拍型号** ⇒ 请老板在 §A5 上给一句「① 优先 / ④ 优先 / ② 优先」, 本单的矩阵立刻能收敛成一个型号 + 一条降级路线。

---

## §5 降级方案 (2 条主方案 · 覆盖 brief 列出的四种情形)

> ★**机器基准块为什么只有 2 条**: 门禁 C5 的反向用例是「把降级方案砍到 1 条 ⇒ 红」⇒ 基准块取 **2 条** 才能自证; 每条内部含变体, 覆盖 brief 的 ①换封装 ②外部反灌保护 ③接受无 RCB 改拓扑/记缺口 ④换 SoM/电池方案。

### FB1 —— 不改板路线: 保留 TPS22991RAA + 外部反灌保护 / 改拓扑 / 记缺口

- **改了什么**
  - 变体 A: 在 **U_PWR_SW 的 VOUT(SYS) 与 SoC IO 之间**串 1 颗反向阻断元件 (肖特基 D 或 P-FET 理想二极管), 把 USB 5V 的反灌从 SoC IO 旁路掉 (注意: **不能**串在 SYS 主路上, 见代价栏)。
  - 变体 B (改拓扑): 取消 Q_PG 对 ON 脚「插电即开机」的强制拉高 ⇒ 关机插 USB 时负载开关保持禁用 ⇒ N 沟道体二极管天然阻断 VOUT→VIN ⇒ 代价是失去「插电即开机」。
  - 变体 C (接受无 RCB): 把缺口正式登记进 `HW/POWER_SHUTDOWN_V3.md` §2 与决策页 §A5, 并要求 hw-lead 在板级核实 SoC IO 脚的反灌是否被 SoC 内部保护钳位。
- **代价**: 面积 变体 A +1~3 mm² (镜脚板缺 300 mm² 的余量里可吸收), B/C = 0 · 压降 变体 A 肖特基 @0.55A 约 0.20~0.30 V ⇒ **若串在 SYS 主路上会吃掉 SYS 下限 3.5V 与 SoC UVLO 3.5V 的全部余量 ⇒ 只能串在 SoC IO 支路**; P-FET 理想二极管约 20~50 mV (Rds×I) · 静态功耗 变体 A 肖特基反向漏 1~10 µA (关机账 108 µA 的 +1~9%), 理想二极管控制器 5~20 µA (+5~19%) · 工艺 变体 A 加 1~2 颗件 + 改网表 (footprint 不动 ⇒ 不改板), 变体 B 动关机状态机与 Q_PG 选型 · 延期 变体 A/C = 0 板次, 变体 B 需重跑 `SW/tools/check_shutdown_semantics.py`。
- **适用条件**: 老板把 A5 的 ④ (封装/面积/**不改板**) 放在 ① (反向阻断) 之上, 或明确接受「关机插电期间电池被反灌」这条风险被登记并接受 ⇒ **这是「没有同封装且带 RCB 的在售型号」这一最坏情形的首选路线**。
- **依据**: `[推算]` 压降/漏电基于网表 L37 的 SYS 最大 0.55A 与 SYS 下限 3.5V / SoC UVLO 3.5V; `[推算]` 肖特基 Vf 与反向漏电取常见档位 (本轮未取具体料号数据手册 ⇒ 选型后必须按其数据手册复核); 拓扑依据 `HW/POWER_SHUTDOWN_V3.md` §3 (Q_PG P-MOS 高边 + ON 脚 10k 下拉) 与 §2 判据 5; 缺口登记依据 ISS-234 交卷件 §3 Q2。

### FB2 —— 改板路线: 换成带 RCB 的在售型号

- **改了什么**: 换 U_PWR_SW 的封装与型号 ⇒ 首选 **SGM2575SADYG/TR** (True RCB · 30 mΩ · 2A · 0.578 mm²), 次选 **TPS22910AYZVR** (Full-Time RCB · 61 mΩ @3.3V), 再次 **TPS22916BYFPR** (Always-ON true RCB · 60 mΩ @5V) 或 **TPS22917xDBVR** (RCB · 80 mΩ @5V · 但面积超判据 6) · 变体 D: 若 RCB 缺口被判为「由充电板/结构侧保证」(USB 5V 永不与 SYS 相连), 则整条改板路线可免, 直接落 TPS22991RAA · 变体 E: 极端方案 —— 换带理想二极管/电源路径管理的 SoM 或换电池供电方案 (把反灌问题挪到 SoM 侧解决)。
- **代价**: 面积 SGM2575S 0.578 mm² (比现 RAA 的 0.6375 mm² 还小一点) / TPS22910A 1.5625 mm² / TPS22916 1 mm² / TPS22917 8.12 mm² (超判据 6) · 工艺 ★**改板 = 改原理图 + 改 PCB footprint + 重跑 DRC/ERC + 重跑网表/脚表门禁 ⇒ 板那一趟必须排进计划** (ISS-172 落表后才能启动) · 延期 ★板改版 + 重新投板 + 重测, 按本项目节奏至少 1~2 个排期窗口; ★**SGM2575S / SGM2572 的 4-ball 引脚定义本轮为 [0数据] ⇒ 改板前必须先拿到数据手册原表核对 4 个 ball 的 VIN/ON/VOUT/GND 编号 (这是改板返工代价最高的一项)** · 变体 E 代价最大 (SoM/电池方案重选 + 全部下游电源树重画), 不在本单范围。
- **适用条件**: 老板把 ① (反向阻断) 排在最前且接受改板 ⇒ 这是「把反灌硬约束做实」的唯一无缺口路线; 若同时要求 RON ≤ 40 mΩ, 则本次查证范围内只有 **SGM2575S** 同时满足。
- **依据**: `[官网]` / `[媒体]` 各型号的封装 / RCB / RON / IQ 数值见 §6 出处表; `[实测]` 现网表 footprint 与引脚定义来自 `HW/netlist_v1.csv` L50/L58; `[推算]` 排期代价按本项目板改版既有节奏估计 (本轮未取项目管理排期表), 具体天数由项目总工核。

---

## §6 出处表 (取数时间 2026-11-16 11:47~11:52 GMT+8 · 全部公开数据手册/官网)

| # | 来源 | 类型 | 用于 | 等级 |
|---|---|---|---|---|
| S1 | TI 官网产品页 `https://www.ti.com/product/TPS22991` (Features / 规格栏 / package 栏 / Description) | 官网 | C1 全部 8 格 + RCB 判定 | [官网] |
| S2 | TI 数据手册 SLVSFK0B (Rev.B, 2025-02-13) `https://www.ti.com/lit/gpn/TPS22991` — §5 Pin Functions 表 5-1 (VIN 1 / ON 2 / VOUT 3 / GND 4) · §6.1 Absolute Maximum Ratings (VIN/VOUT/VON −0.3~6 V) · §6.5 Electrical Characteristics (RON 25 mΩ @5V; IQ 6 µA typ; ISD 14 nA typ / 20 µA max) · Device Comparison Table (B/BN/C/CN 变体) | 官网 | C1 判据 1/3/4/8 + 时序 + 变体缺口 | [官网] |
| S3 | TI 官网产品页 `https://www.ti.com/product/TPS22916` (Features: RON 60/100/200 mΩ · IQ 0.5 µA typ / 1 µA max · ISD 10 nA typ / 100 nA max · Always-ON true RCB · Smart ON pulldown · QOD 150 Ω · tON 115/1400 µs) | 官网 | C2 全部 8 格 + RCB 判定 | [官网] |
| S4 | TI 数据手册 SLVSDO5F (2021-12) `https://www.ti.com/lit/gpn/TPS22916` — §5 Pin Functions 表 5-1 (A1 VOUT / A2 VIN / B1 GND / B2 ON) · §6.1 Absolute Maximum Ratings (VIN/VOUT/VON −0.3~6 V, IMAX 2 A, IPLS 2.5 A, TJ 125 °C, TSTG −65~150 °C) · 订购表 (TPS22916BYFPR, DSBGA YFP 4) | 官网 | C2 判据 1/2/6 + 引脚差异 | [官网] |
| S5 | TI 官网产品页 `https://www.ti.com/product/TPS22917` (Features: RON 80/120/220 mΩ · IQ 0.5 µA typ · ISD 10 nA typ · Always-ON true RCB (IRCB −500 mA typ, 漏 −1 µA max) · SOT-23-6 8.12 mm² · −45~+125 °C) | 官网 | C4 全部 8 格 + RCB 判定 | [官网] |
| S6 | TI 数据手册 ZHCSHL1B (2021-12) `https://www.ti.com/lit/gpn/TPS22917` — §6 Pin Functions 表 6-1 + 图 6-1 (1 VIN / 2 GND / 3 ON / 4 CT / 5 QOD / 6 VOUT) · Device Comparison Table (TPS22917 高有效 / TPS22917L 低有效) | 官网 | C4 判据 8 引脚差异 | [官网] |
| S7 | TI 官网产品页 `https://www.ti.com/product/TPS22910A` (Description 原文: ON 与 OFF 两态反向电流保护 + 内部反向电压比较器 10 µs typ + always active · Features: RON 60/61/74/84 mΩ · IQ 2 µA typ · ISD 1.2 µA typ · WCSP 0.9×0.9 4 pin · −40~85 °C) | 官网 | C5 全部 8 格 + RCB 判定 | [官网] |
| S8 | TI 官网产品页 `https://www.ti.com/product/TPS22918` (Features 只有 Inrush current control / Quick output discharge ⇒ **无 RCB**; RON 52 mΩ @5V / 53 mΩ @3.3V; IQ 8.3 µA; 2A; SOT-23-6; −40~+105 °C) | 官网 | §3.1 「查过 = 无」 | [官网] |
| S9 | TI 官网产品页 `https://www.ti.com/product/TPS22919` (Features 无 Reverse current protection ⇒ **无 RCB**; RON 89/90/105 mΩ; IQ 8 µA; ISD 2 nA; 1.5A; SC70-6; −40~+125 °C) | 官网 | §3.1 「查过 = 无」 | [官网] |
| S10 | 圣邦微官网产品页 `https://www.sg-micro.com/cn/product/SGM2572` (特性栏: 1V~5.5V / 2A / RON 34 mΩ @5V 与 @3.3V / 关断电流 90 nA typ / 禁用时反向电流保护 / 低阈值 1.8V GPIO / 双向电源 / 上升时间 A 85µs B 1600µs C 2200µs / 快速输出放电 / WLCSP-0.8×0.8-4B; 订购信息栏: 量产 · −40℃~+85℃ · 3 个 OPN) | 官网 | C3 全部 8 格 + RCB 判定 | [官网] |
| S11 | 圣邦微数据手册 `https://www.sg-micro.com/rect/assets/a8959667-d386-4c95-a64d-205e9b7b4446/SGM2575S.PDF` (2 JULY 2025, SG Micro Corp; 标题 5.5V/2A/30 mΩ RDSON + Reverse Current Protection; True RCB 触发点 6 mV typ / 24 / 50 mV, 迟滞 30 mV; IRC 10 nA typ / 900 nA max; ION 10 nA typ / 900 nA max; RPD 230/300 Ω; 智能下拉 1 MΩ; WLCSP-0.76×0.76-4B) | 原厂数据手册 (本轮经搜索引擎文本化抓取, PDF 直取为二进制) | C6 全部 8 格 + RCB 判定 | [媒体] |
| S12 | SGMICRO 官方选型指南 2025 Q3 (Avnet 镜像) `https://my.avnet.com/wcm/connect/04f1699a-86ea-4f07-b19d-0aa9aab2b58a/SGMICRO+Product+Selection+Guide+(2025+Q3).pdf` (行 SGM2572: 静态 0.22 µA / 关断 <0.44 µA; 行 SGM2575S: 静态 0.23 µA / VIN 1.2–5.5 V / 2A) | 原厂文档的第三方镜像 | C3 判据 4 · C6 判据 1/2/4 | [媒体] |
| S13 | `HW/POWER_SHUTDOWN_V3.md` §2 (8 条判据原文 · 只读) + §3 (Q_PG P-MOS 高边 / ON 脚 10k 下拉 / 真关机拓扑) + §6 (关机功耗预算 ~108 µA) | 项目内部文档 (只读) | §1 判据 · §3.2 拓扑依据 · §4 关机账占比 | [实测] (项目内部口径) |
| S14 | `HW/netlist_v1.csv` L37 (SYS 3.0–4.2V / 最大 0.55A / SYS 下限 3.5V / SoC UVLO 3.5V) · L50 (U_PWR_SW 本体行, value 栏 = `[待选型] 负载开关 (≥2A, R_on ≤40mΩ@3.7V, IQ ≤5µA, 带反向阻断)`, footprint = UQFN-4 RAA 0.85 x 0.75 mm 0.4 mm pitch, OPN = TPS22991RAA) · L56 (`R_PD_ON` 10k) · L58 (ON 节点) · L440–L444 (U_EN_SW 引脚与 CARRIER_BOARD_EN) | 网表 (只读) | §1 判据串对照 · §2 引脚一致性 · §3.2 · §5 代价推算 | [实测] |
| S15 | `SW/SHUTDOWN_SEMANTICS_SPEC.md` §3 (ISS-234 交卷: Q2 推荐 TPS22991RAA + 要求登记「无 RCB」缺口 + N-1「整机负载开关选型必须同时看 RON/IQ/RCB 三条」) + `DECISION_PENDING_2026-11-16.md` §A5 / §Q2 (拍板待办 + 建议优先级序) | 项目内部文档 (只读) | §0 摘要 · §3 缺口承接 · §4 打分依据 | [实测] (项目内部口径) |

> ★**证据等级统计**: `[官网]` 为主 (TI 官网产品页 + 数据手册 + 圣邦微官网产品页) · `[媒体]` 仅用于「原厂数据手册经搜索引擎文本化抓取」与「原厂选型指南的第三方镜像」 · `[推算]` 只用于压降/漏电/关机账占比/排期代价的推导 · `[0数据]` 明确标出本轮没查到的格子 · ★**实物 [实测] = 0 条**。

---

## §7 落表影响 (★本单不落表★)

| # | 落表时必须一起改的项 | 现状 | 归属 |
|---|---|---|---|
| L1 | `HW/netlist_v1.csv` L50 的 value 栏 `[待选型] 负载开关 (≥2A, R_on ≤40mΩ@3.7V, IQ ≤5µA, 带反向阻断)` ⇒ 换成老板拍定的型号 + 判据串 | ★**本单不改** (等老板拍板) | 落表批次 |
| L2 | 同行的 OPN 栏 `TPS22991RAA` ⇒ 补全变体字母 (B/BN/C/CN 之一, 影响 QOD 有无与上电斜率) | 本单只报 | 落表批次 |
| L3 | L442 `U_EN_SW` 的 value 栏 `TPS22991RAA (负载开关: 1=VIN/2=ON/3=VOUT/4=GND, UQFN-4 RAA 0.85 x 0.75 mm)` ⇒ 若整机型号改封装, 这颗也要一起改 | 本单只报 | 落表批次 |
| L4 | 若选带 RCB 的改板型号 ⇒ 原理图 + PCB footprint 一起改 (DSBGA-4 / WLCSP-4 ball 的焊盘编号与现 RAA 不同) | 本单只报 | hw-lead (板那一趟) |
| L5 | 判据 2 与网表 L37 的口径冲突 (2A vs 0.55A) | 本单只报 | 老板 / main 裁 |

---

## §8 自证复现命令

```bash
cd projects/smart_glasses
python3 SW/tools/check_load_switch_selection.py             # rc=0 = 证据矩阵门禁全过
python3 SW/tools/check_load_switch_selection.py --selftest   # rc=0 = 8/8 反向用例全红
python3 SW/tools/check_shutdown_semantics.py                 # rc=0 (ISS-234 的闸, 本单不许打红)
python3 state/merge.py && python3 state/gate_check.py         # rc=0, Q1 18/18
```

<!-- BEGIN 选型证据基准块 -->
```json
{
  "meta": {
    "issue": "ISS-172",
    "doc": "SW/LOAD_SWITCH_SELECTION_FACTS.md",
    "author": "sw-lead",
    "date": "2026-11-16",
    "evidence_policy": "老板 2026-11-12 02:02 不再发信 · 全靠自己查资料 · 证据等级只取 [官网]/[实测]/[媒体]/[推算]/[0数据]",
    "boundary": "只交证据 · 不落表 · 网表 L50 的 [待选型] 判据串等老板拍完型号再由落表批次改",
    "scope_note": "机器基准块 candidates 册取 3 个 (门禁 C1 的反向用例设计为「把候选砍到 2 个 ⇒ 红」⇒ 基准册必须正好 3 个才能自证); 其余 3 个同族/国产候选以 alternates 数组并列 (同样 8 条判据逐格填满), 正文 §2 矩阵共 6 个型号全部逐格填满"
  },
  "criteria": [
    {
      "id": 1,
      "text": "**VIN 绝对额定 ≥ 5V**"
    },
    {
      "id": 2,
      "text": "**Iout ≥ 2A** (持续 1A 上下)"
    },
    {
      "id": 3,
      "text": "**R_on ≤ 40mΩ @3.7V** (目标 ≤30mΩ)"
    },
    {
      "id": 4,
      "text": "**关机漏电 IQ ≤ 5µA**"
    },
    {
      "id": 5,
      "text": "★**必须有反向阻断 (或 quick output)**"
    },
    {
      "id": 6,
      "text": "**面积 ≤ 2×2mm**"
    },
    {
      "id": 7,
      "text": "**-40 ~ +85°C**"
    },
    {
      "id": 8,
      "text": "**ON 脚兼容 3.3V GPIO, 且有确定默认态**"
    }
  ],
  "fallbacks": [
    {
      "id": "FB1",
      "change": "不改板路线: 保留 TPS22991RAA (UQFN-4 RAA · 同封装换料不换板) + 在反灌通路上补外部阻断 —— 变体 A: 在 U_PWR_SW 的 VOUT(SYS) 与 SoC IO 之间串 1 颗反向阻断元件 (肖特基 D 或 P-FET 理想二极管), 把 5V 反灌从 SoC IO 旁路掉; 变体 B: 改拓扑 —— 取消 Q_PG (P-MOS 高边) 对负载开关 ON 脚的『插电即开机』强制拉高, 使关机插 USB 时开关始终保持禁用 (N-MOS 体二极管天然阻断 VOUT->VIN), 代价是失去『插电即开机』; 变体 C: 接受无 RCB, 把缺口登记进 HW/POWER_SHUTDOWN_V3.md §2 与决策页 §A5, 并要求 hw-lead 在板级核实 SoC IO 脚反灌电流是否被 SoC 内部保护钳位",
      "cost": "面积: 变体 A 加 1 颗二极管/MOS + 1~2 颗电阻 (估 1~3 mm², 镜脚板缺 300 mm² 的余量里可吸收); 变体 B/C 面积 0。压降: 变体 A 肖特基 @0.55A 约 0.20~0.30V (Vf typ 0.35~0.55V @0.55A) —— 若串在 SYS 主路上会直接吃掉 SYS 下限 3.5V 与 SoC UVLO 3.5V 的全部余量 ⇒ 只能串在 SoC IO 支路 (不承载 SYS 主电流); P-FET 理想二极管方案压降约 20~50mV (Rds x I)。静态功耗: 肖特基反向漏 1~10 µA (加到关机账 108 µA 上 ⇒ +1~9%); 理想二极管控制器静态 5~20 µA (+5~19%)。工艺: 变体 A 需加 1~2 颗件 + 改原理图与网表 (仍不改板 footprint); 变体 B 要动关机状态机与 Q_PG 选型。延期: 变体 A/C 0 板次; 变体 B 需重跑关机语义门禁 (SW/tools/check_shutdown_semantics.py)",
      "condition": "适用条件: 老板把 A5 建议序的第 ④ 条 (封装/面积/不改板) 放在第 ① 条 (反向阻断) 之上, 或明确接受『关机插电期间电池不被反灌』这条风险被文档登记并接受 ⇒ 这是『没有同封装且带 RCB 的在售型号』这一最坏情形下的首选路线",
      "basis": "[推算] 压降/漏电基于网表 L37 的 SYS 最大 0.55A (330 mA x 1.5 + 瞬态) 与 SYS 下限 3.5V / SoC UVLO 3.5V (同 L37 note, R-F1 裁决); [推算] 肖特基 Vf 与反向漏电取常见档位, 本轮未取具体料号数据手册 ⇒ 选具体器件后必须按其数据手册复核; 拓扑依据 HW/POWER_SHUTDOWN_V3.md §3 (Q_PG P-MOS 高边 · 插电即开机路径 · ON 脚 10k 下拉默认关) 与 §2 判据 5 (关机插 USB 时 5V 经 SoC IO 反灌电池); 缺口登记依据 ISS-234 交卷件 SW/SHUTDOWN_SEMANTICS_SPEC.md §3 Q2 (Q2 推荐 TPS22991RAA + 要求登记无 RCB 缺口)"
    },
    {
      "id": "FB2",
      "change": "改板路线: 换掉 U_PWR_SW 的封装与型号, 选原厂在售且带反向阻断的型号 —— 首选 SGM2575S (圣邦微 WLCSP-0.76x0.76-4B · True RCB · 30 mΩ · 2A), 次选 TPS22910AYZVR (TI DSBGA-4 YZV 0.9x0.9 WCSP · Full-Time RCB · 61 mΩ @3.3V), 再次 TPS22916BYFPR (TI DSBGA-4 YFP 1 mm² · Always-ON true RCB · 60 mΩ @5V) 或 TPS22917xDBVR (TI SOT-23-6 · RCB · 80 mΩ @5V); 变体 D: 若 RCB 缺口在本项目被判为『由结构/充电板侧保证』(例如 USB 5V 永不与 SYS 相连), 则整条改板路线可免, 直接落 TPS22991RAA; 变体 E: 极端方案 —— 改用带理想二极管/电源路径管理的 SoM 或换电池供电方案 (把反灌问题挪到 SoM 侧解决)",
      "cost": "面积: SGM2575S 0.76x0.76 = 0.578 mm² (比现 UQFN-4 RAA 的 0.6375 mm² 略小); TPS22910A 1.5625 mm²; TPS22916 1 mm²; TPS22917 SOT-23-6 8.12 mm² (超判据 6 的 2x2 mm²)。工艺: 改板 = 改原理图 + 改 PCB footprint + 重跑 DRC/ERC + 重跑网表/脚表门禁 ⇒ 板那一趟必须排进计划 (ISS-172 落表后才能启动)。延期: 板改版 + 重新投板 + 重测, 按本项目节奏至少 1~2 个排期窗口; SGM2575S 的引脚定义本轮为 [0数据] ⇒ 改板前必须先拿到 SGM2575S.pdf 原表核对 4 个 ball 的 VIN/ON/VOUT/GND 编号 (改板返工代价最高的一项)。变体 E 代价最大: SoM/电池方案重选 + 全部下游电源树重画, 不在本单范围",
      "condition": "适用条件: 老板把 A5 建议序的第 ① 条 (反向阻断) 排在最前, 且接受改板一次 ⇒ 这是『把反灌硬约束做实』的唯一无缺口路线; 若同时要求 RON <= 40 mΩ, 则只有 SGM2575S (30 mΩ) 在本次查证范围内同时满足 RCB 与 RON",
      "basis": "[官网] 封装/RCB/RON/IQ 数值来自各原厂官网产品页与数据手册 (见 §6 出处表); [实测] 现网表 footprint 与引脚定义来自 HW/netlist_v1.csv L50/L58 (UQFN-4 RAA, 0.85 x 0.75 mm, 0.4 mm pitch · 1=VIN/2=ON/3=VOUT/4=GND); [推算] 排期代价按本项目板改版既有节奏估计 (本轮未取项目管理排期表), 具体天数由项目总工核"
    }
  ],
  "candidates": [
    {
      "id": "TPS22991RAA",
      "vendor": "Texas Instruments",
      "package": "UQFN-4 (RAA), 0.85 x 0.75 mm, 0.4 mm pitch, 0.6375 mm² —— 与 HW/netlist_v1.csv L50 的 footprint 栏逐字一致 => 换料不换板",
      "cells": {
        "1": {
          "value": "绝对最大额定 VIN -0.3 ~ 6 V (VOUT/VON 同 -0.3 ~ 6 V); 工作范围 1.0 ~ 5.5 V => 判据 1 (VIN 绝对额定 >= 5V) 满足 (6 V > 5 V)",
          "source": "TI 数据手册 SLVSFK0B (Rev.B, 2025-02-13) §6.1 Absolute Maximum Ratings (VIN/VOUT/VON 行) + §1 Features (Input voltage range: 1V to 5.5V) + 官网产品页 https://www.ti.com/product/TPS22991",
          "evidence": "[官网]"
        },
        "2": {
          "value": "最大连续开关电流 3 A (Imax 3 A) => 判据 2 (Iout >= 2A, 持续 1A 上下) 满足, 余量 1.5 倍; 绝对最大表另列 IMAX 3 A",
          "source": "TI 数据手册 SLVSFK0B §1 Features (3A maximum continuous switch current) + 官网产品页规格栏 Imax (A) = 3",
          "evidence": "[官网]"
        },
        "3": {
          "value": "RON typ 25 mΩ @ VIN = 5 V (IOUT = -200 mA, 25 °C); 3.7 V 档数据手册未单列 => 按 RON-vs-VIN 曲线 (Fig 7-5) 内插约 27~28 mΩ => 判据 3 (<= 40 mΩ @3.7V, 目标 <= 30 mΩ) 按 typ 满足; RON 的 max 档本轮未取得 => 按 max 口径未判定",
          "source": "TI 数据手册 SLVSFK0B §6.5 Electrical Characteristics 表 ON-RESISTANCE (RON) 行 (VIN = 5V, 25 °C, 25 mΩ) + 图 7-5 RON vs Input Voltage",
          "evidence": "[官网]"
        },
        "4": {
          "value": "ON 态静态电流 IQ typ 6 uA @ VIN = 3.3 V (max 12 uA @ -40~85 °C, 14 uA @ -55~125 °C); 关机漏电 ISD typ 14 nA @ 3.3 V (max 20 uA @ -40~85 °C, 67 uA @ -55~125 °C) => 判据 4 (关机漏电 IQ <= 5 uA): 按 typ (14 nA) 满足, ★按 max (20 uA) 不满足 (超 4 倍) —— 这是本型号唯一硬超判据的一条",
          "source": "TI 数据手册 SLVSFK0B §6.5 表 IQ, VIN / ISD, VIN 两行 (25 °C / -40~85 °C / -55~125 °C 三档) + §1 Features (Low shutdown current: ISD at 3.3V VIN = 14nA typ)",
          "evidence": "[官网]"
        },
        "5": {
          "value": "无 RCB —— 官网 Features 栏只有 Inrush current control / Quick output discharge / Thermal shutdown, 无 Reverse current protection 条目; 数据手册 SLVSFK0B 目录 (Pin Configuration / Absolute Maximum / Electrical Characteristics) 无 Reverse Current Blocking 章节; 官网 Description 只说含 N 沟道 MOSFET 与 150 Ω QOD => 判据 5 (必须有反向阻断) 不满足 => 这就是 ISS-234 点名的『无 RCB』缺口",
          "source": "TI 官网产品页 Features 栏 https://www.ti.com/product/TPS22991 + 数据手册 SLVSFK0B §1 Features / §3 Description / §5-§6 目录",
          "evidence": "[官网]"
        },
        "6": {
          "value": "封装 0.85 x 0.75 mm = 0.6375 mm² (官网 package 栏 UQFN-HR (RAA) 4 pins, 0.6375 mm²) => 判据 6 (面积 <= 2 x 2 mm) 满足, 是候选里最小的之一",
          "source": "TI 官网产品页 package 栏 (UQFN-HR (RAA) · 4 · 0.6375 mm² (0.75 mm x 0.85 mm)) + 数据手册 SLVSFK0B Package Information",
          "evidence": "[官网]"
        },
        "7": {
          "value": "工作温度 -55 ~ +125 °C (自由空气) => 判据 7 (-40 ~ +85 °C) 满足, 余量 40 °C",
          "source": "TI 官网产品页 Operating temperature range (°C) = -55 to 125 + 数据手册 SLVSFK0B §1 Features (characterized for -55 °C to +125 °C)",
          "evidence": "[官网]"
        },
        "8": {
          "value": "ON = pin2, 数据手册引脚功能表原文 Active high switch control input => 高有效, 与网表 (SoC GPIO 拉高 = 开机, R_PD_ON 10k 下拉 = 默认关) 一致; 芯片内部 ON 脚智能下拉阻值本轮未在官网文本中取得 => 内部下拉按 [0数据] 记, 但本设计不依赖它 (外部 10k 下拉已在网表), 故默认态确定; 无 power-off latch / OFF-after-delay 型号 => 关断状态靠外部下拉保持",
          "source": "TI 数据手册 SLVSFK0B §5 Pin Functions 表 5-1 (VIN 1 / ON 2 Active high / VOUT 3 / GND 4) + 网表 HW/netlist_v1.csv L56 (R_PD_ON 10k) 与 L58",
          "evidence": "[官网]"
        }
      },
      "rcb": {
        "verdict": "无",
        "quote": "Features: Inrush current control, Quick output discharge, Thermal shutdown (原文照抄, 无 Reverse current protection 条目); Description: The TPS22991 is a small, low RON, single channel load switch with controlled slew rate. The device contains an N-channel MOSFET ... The TPS22991 further reduces the total solution size by integrating a 150Ω pulldown resistor for quick output discharge (QOD) when the switch is turned off.",
        "source": "TI 官网产品页 https://www.ti.com/product/TPS22991 (Features 与 Description 栏) + 数据手册 SLVSFK0B §1 Features / §3 Description",
        "evidence": "[官网]"
      }
    },
    {
      "id": "TPS22916BYFPR",
      "vendor": "Texas Instruments",
      "package": "DSBGA-4 (YFP), 4 bump, 官网 package 栏标 1 mm² (reel A0 0.86 x 0.86 mm) —— 不是 UQFN-4 RAA => 换封装 => 必须改板; 器件版本 b/C (快/慢上电斜率), 订购表另有 TPS22916CLYFPR 等",
      "cells": {
        "1": {
          "value": "绝对最大额定 VIN -0.3 ~ 6 V, VOUT -0.3 ~ 6 V, VON -0.3 ~ 6 V; 工作范围 1 ~ 5.5 V => 判据 1 满足 (6 V > 5 V)",
          "source": "TI 数据手册 SLVSDO5F (2021-12) §6.1 Absolute Maximum Ratings (VIN / VOUT / VON 行) + 官网产品页 https://www.ti.com/product/TPS22916 (Input operating voltage range 1V-5.5V)",
          "evidence": "[官网]"
        },
        "2": {
          "value": "最大连续开关电流 IMAX 2 A; 脉冲 IPLS 2.5 A (pulse < 300 us, 2% duty) => 判据 2 (Iout >= 2A) 正好卡在门槛, 无余量",
          "source": "TI 数据手册 SLVSDO5F §6.1 Absolute Maximum Ratings (IMAX 2 A / IPLS 2.5 A 行) + 官网 Features (Maximum continuous current (IMAX): 2 A)",
          "evidence": "[官网]"
        },
        "3": {
          "value": "RON 60 mΩ typ @ VIN = 5 V (85 °C max 100 mΩ); 100 mΩ typ @ 1.8 V (150 mΩ max @85 °C); 200 mΩ typ @ 1 V (325 mΩ max @85 °C) => 3.7 V 档不低于 60 mΩ => ★判据 3 (<= 40 mΩ @3.7V) 不满足; 压降 @1A = 60 mV typ (100 mV max @85 °C) => SYS 下限 3.5V 余量被吃掉",
          "source": "TI 官网产品页 https://www.ti.com/product/TPS22916 Features (ON-resistance (RON): 5VIN = 60 mΩ typ, 100 mΩ 85°C max / 1.8VIN = 100 mΩ typ / 1VIN = 200 mΩ typ)",
          "evidence": "[官网]"
        },
        "4": {
          "value": "ON 态 IQ typ 0.5 uA / max 1 uA; OFF 态 ISD typ 10 nA / max 100 nA (TPS22916BL/CL/CNL 版本 ISD 100 nA typ / 300 nA max) => 判据 4 (<= 5 uA) typ 与 max 双双满足, 是候选里关机漏电余量最好的之一",
          "source": "TI 官网产品页 https://www.ti.com/product/TPS22916 Features (ON state (IQ): 0.5 uA typ, 1 uA max; OFF state (ISD): 10 nA typ, 100 nA max; TPS22916BL/CL/CNL (ISD): 100 nA typ, 300 nA max)",
          "evidence": "[官网]"
        },
        "5": {
          "value": "有 RCB —— Always-ON true Reverse Current Blocking (RCB): Activation current (IRCB): -500 mA typ; Reverse leakage (IIN,RCB): -300 nA max => ★判据 5 满足, 且是 always-ON (开关导通时也挡反灌), 比『仅禁用态阻断』的型号更强",
          "source": "TI 官网产品页 https://www.ti.com/product/TPS22916 Features (Always-ON true Reverse Current Blocking (RCB) 两条) + 数据手册 SLVSDO5F",
          "evidence": "[官网]"
        },
        "6": {
          "value": "封装 4 bump DSBGA (YFP), 官网 package 栏标 1 mm² (0.86 x 0.86 mm) => 判据 6 (面积 <= 2 x 2 mm) 满足",
          "source": "TI 官网产品页 package 栏 (DSBGA (YFP) · 4 · 1 mm²) + 数据手册 SLVSDO5F 订购表 (TPS22916BYFPR, DSBGA YFP 4, K0 0.59 mm, A0 0.86 mm)",
          "evidence": "[官网]"
        },
        "7": {
          "value": "工作温度 -40 ~ +85 °C => 判据 7 满足, 但下限正好卡在 -40 °C (镜脚贴皮肤, 环境 45~50 °C 上限仍有余量)",
          "source": "TI 官网产品页 Operating temperature range (°C) = -40 to 85",
          "evidence": "[官网]"
        },
        "8": {
          "value": "ON 高有效 (标准版; L 版本为低有效, 官网写 Active low enable option (L versions)); Smart ON pin pulldown: ON >= VIH 时 ION max 10 nA, ON <= VIL 时 RPD 750 kΩ typ => 默认态确定 (内部智能下拉 + 网表外部 10k 双保险) => 判据 8 满足; 无 power-off latch 型号",
          "source": "TI 官网产品页 https://www.ti.com/product/TPS22916 Features (Smart ON pin pulldown (RPD) 两条 + Active low enable option (L versions))",
          "evidence": "[官网]"
        }
      },
      "rcb": {
        "verdict": "有",
        "quote": "Always-ON true Reverse Current Blocking (RCB): Activation current (IRCB): -500 mA (typ.) / Reverse leakage (IIN,RCB): -300 nA (max.) (原文照抄)",
        "source": "TI 官网产品页 https://www.ti.com/product/TPS22916 Features 栏 (与数据手册 SLVSDO5F 的 Reverse Current Blocking 小节一致)",
        "evidence": "[官网]"
      }
    },
    {
      "id": "SGM2572ADYG/TR",
      "vendor": "圣邦微 SGMICRO (国产)",
      "package": "WLCSP-0.8 x 0.8-4B (4 ball, 绿色封装) —— 不是 UQFN-4 RAA => 换封装 => 必须改板; 官网订购信息栏标『量产』, 三个 OPN: SGM2572ADYG/TR (上升 85 us) / SGM2572BDYG/TR (1600 us) / SGM2572CDYG/TR (2200 us)",
      "cells": {
        "1": {
          "value": "工作输入电压范围 1 V ~ 5.5 V (官网特性栏) => 判据 1 (VIN 绝对额定 >= 5V): 工作上限 5.5 V 已 > 5 V, 但官网产品页未列绝对最大额定表 => 绝对最大额定按 [0数据] 记, 落表前必须查 SGM2572.pdf 原表确认 VIN/VOUT 的绝对最大值",
          "source": "圣邦微官网产品页 https://www.sg-micro.com/cn/product/SGM2572 (特性栏 输入电压范围 1V 至 5.5V) —— 绝对最大额定表本轮未在官网页面呈现",
          "evidence": "[官网]"
        },
        "2": {
          "value": "最大持续电流 2 A (官网特性栏) => 判据 2 (Iout >= 2A) 正好卡在门槛, 无余量",
          "source": "圣邦微官网产品页 https://www.sg-micro.com/cn/product/SGM2572 (特性栏 最大持续电流 2A)",
          "evidence": "[官网]"
        },
        "3": {
          "value": "RON = 34 mΩ @ VIN = 5 V; RON = 34 mΩ @ VIN = 3.3 V (官网特性栏两行) => 3.7 V 档按 3.3/5 V 两点内插约 34 mΩ => ★判据 3 (<= 40 mΩ @3.7V, 目标 <= 30 mΩ) 满足; 压降 @1A = 34 mV (比 TPS22916 的 60 mV 少 26 mV), 比现 OPN TPS22991RAA 的 25 mΩ 多 9 mV",
          "source": "圣邦微官网产品页 https://www.sg-micro.com/cn/product/SGM2572 (特性栏 低导通电阻 RON = 34mΩ (VIN = 5V) / RON = 34mΩ (VIN = 3.3V))",
          "evidence": "[官网]"
        },
        "4": {
          "value": "低关断电流 90 nA (typ) (官网特性栏) => 判据 4 (关机漏电 IQ <= 5 uA) 满足 (90 nA = 关机账 108 uA 的 0.08%); ON 态静态电流官网产品页未列, SGMICRO 官方选型指南 (2025 Q3, Avnet 镜像) 记 0.22 uA typ / 0.44 uA max => 同样满足 <= 5 uA, 但这一条数字来自原厂指南的第三方镜像, 按 [媒体] 记",
          "source": "圣邦微官网产品页 https://www.sg-micro.com/cn/product/SGM2572 (低关断电流 90nA 典型值) + SGMICRO 官方选型指南 2025 Q3 (Avnet 镜像) https://my.avnet.com/wcm/connect/04f1699a-86ea-4f07-b19d-0aa9aab2b58a/SGMICRO+Product+Selection+Guide+%282025+Q3%29.pdf",
          "evidence": "[媒体]"
        },
        "5": {
          "value": "有 RCB —— 官网特性栏原文『禁用时提供反向电流保护』, 另有『适用于功率区应用的双向电源』; ★关键限定: 官网写的是禁用时 (off-state) 阻断, 不是导通也挡的 always-ON true RCB ⇒ 对本板『关机插 USB』场景 (开关处于禁用态) 是覆盖的, 但开关导通时的反灌仍会通过通道发生, 缺口说明必须写清这一点",
          "source": "圣邦微官网产品页 https://www.sg-micro.com/cn/product/SGM2572 (特性栏 禁用时提供反向电流保护 / 适用于功率区应用的双向电源)",
          "evidence": "[官网]"
        },
        "6": {
          "value": "封装 WLCSP-0.8 x 0.8 mm = 0.64 mm² (官网特性栏与订购信息栏) => 判据 6 (面积 <= 2 x 2 mm) 满足, 与现 UQFN-4 RAA 的 0.6375 mm² 基本同面积 (但不是同一个封装, 不能直接换料)",
          "source": "圣邦微官网产品页 https://www.sg-micro.com/cn/product/SGM2572 (采用绿色 WLCSP-0.8 x 0.8-4B 封装 / 订购信息栏 Package 列)",
          "evidence": "[官网]"
        },
        "7": {
          "value": "工作温度 -40 °C ~ +85 °C (官网订购信息栏 Operating Temperature Range 列) => 判据 7 满足",
          "source": "圣邦微官网产品页 https://www.sg-micro.com/cn/product/SGM2572 (订购信息栏 Operating Temperature Range = -40℃ to +85℃, MSL1)",
          "evidence": "[官网]"
        },
        "8": {
          "value": "低阈值 1.8 V GPIO 控制输入 (官网特性栏) => 3.3 V GPIO 可直接驱动 => 判据 8 满足; ★ON 脚内部智能下拉阻值官网产品页未列 => 按 [0数据] 记, 本设计靠网表外部 10k 下拉保证默认关, 不依赖芯片内部下拉; 官网描述『由导通引脚控制』未提 power-off latch",
          "source": "圣邦微官网产品页 https://www.sg-micro.com/cn/product/SGM2572 (特性栏 低阈值 1.8V GPIO 控制输入 + 描述栏 由导通引脚控制)",
          "evidence": "[官网]"
        }
      },
      "rcb": {
        "verdict": "有",
        "quote": "禁用时提供反向电流保护 / 适用于功率区应用的双向电源 (官网特性栏原文照抄; ★官网措辞限定在『禁用时』, 不是 always-ON true RCB)",
        "source": "圣邦微官网产品页 https://www.sg-micro.com/cn/product/SGM2572 (特性栏 与 描述栏)",
        "evidence": "[官网]"
      }
    }
  ],
  "alternates": [
    {
      "part": "TPS22917xDBVR",
      "vendor": "Texas Instruments",
      "package": "SOT-23-6 (DBV), 2.90 x 2.80 mm, 0.95 mm pitch, 官网 package 栏 8.12 mm² —— 6 脚且面积超判据 6 => 必须改板; 版本 TPS22917 高有效 / TPS22917L 低有效",
      "cells": {
        "1": {
          "value": "工作输入 1 ~ 5.5 V; 绝对最大额定表本轮未取得 => 按 [0数据] 记; 工作上限 5.5 V 已满足判据 1 的门槛",
          "source": "TI 官网产品页 https://www.ti.com/product/TPS22917 (Input operating voltage range 1V-5.5V) —— §6.1 绝对最大额定本轮未取得",
          "evidence": "[0数据]"
        },
        "2": {
          "value": "最大连续开关电流 IMAX 2 A => 判据 2 卡在门槛, 无余量",
          "source": "TI 官网产品页 https://www.ti.com/product/TPS22917 (Maximum continuous current (IMAX): 2 A)",
          "evidence": "[官网]"
        },
        "3": {
          "value": "RON 80 mΩ typ @ 5 V; 120 mΩ typ @ 1.8 V; 220 mΩ typ @ 1 V => 3.7 V 档 >= 80 mΩ => ★判据 3 (<= 40 mΩ @3.7V) 不满足, 是带 RCB 候选里压降最差的一个 (@1A 压降 80 mV)",
          "source": "TI 官网产品页 https://www.ti.com/product/TPS22917 (On-resistance (RON): 5VIN = 80 mΩ typical / 1.8VIN = 120 mΩ / 1VIN = 220 mΩ)",
          "evidence": "[官网]"
        },
        "4": {
          "value": "ON 态 IQ typ 0.5 uA; OFF 态 ISD typ 10 nA => 判据 4 满足 (typ 口径); max 值本轮未取得 => 按 max 口径未判定",
          "source": "TI 官网产品页 https://www.ti.com/product/TPS22917 (Ultra-low power consumption: ON state (IQ) 0.5 uA typical; OFF state (ISD) 10 nA typical)",
          "evidence": "[官网]"
        },
        "5": {
          "value": "有 RCB —— Always-ON true Reverse Current Blocking (RCB): IRCB -500 mA typ; 反向漏 IIN,RCB -1 uA max => ★判据 5 满足 (always-ON), 但反向漏 max 比 TPS22916 的 300 nA 大 3 倍",
          "source": "TI 官网产品页 https://www.ti.com/product/TPS22917 Features (Always-ON true Reverse Current Blocking (RCB) 两条)",
          "evidence": "[官网]"
        },
        "6": {
          "value": "SOT-23-6 (DBV) 2.90 x 2.80 mm = 8.12 mm² => ★判据 6 (面积 <= 2 x 2 mm) 不满足 (单边 2.90 mm 已超 2 mm), 镜脚板面积最紧的候选",
          "source": "TI 官网产品页 package 栏 (SOT-23 (DBV) · 6 · 8.12 mm² (2.9 mm x 2.8 mm))",
          "evidence": "[官网]"
        },
        "7": {
          "value": "工作温度 -45 ~ +125 °C => 判据 7 满足, 上限余量最大",
          "source": "TI 官网产品页 Operating temperature range (°C) = -45 to 125",
          "evidence": "[官网]"
        },
        "8": {
          "value": "引脚功能 (DBV 6 脚 SOT-23): 1 VIN / 2 GND / 3 ON (Active high switch control input. Do not leave floating.) / 4 CT / 5 QOD / 6 VOUT => ★与网表 1=VIN / 2=ON / 3=VOUT / 4=GND 完全不同 (6 脚, 且 ON 在 pin3, 多出 CT/QOD 两脚) => 换这个型号必须改板 + 重新定义引脚; Smart ON pin pulldown 750 kΩ typ => 默认态确定; CT 脚可调上升时间 (100 us @5V CT 断开 / 4000 us @5V CT=1000 pF)",
          "source": "TI 数据手册 ZHCSHL1B (2021-12) §6 Pin Functions 表 6-1 + 图 6-1 DBV Package 6-Pin SOT-23 Top View + Device Comparison Table (TPS22917 Active High / TPS22917L Active Low) + 官网产品页 Smart ON pin pulldown / turn ON timing",
          "evidence": "[官网]"
        }
      },
      "rcb": {
        "verdict": "有",
        "quote": "Always-ON true Reverse Current Blocking (RCB): Activation current (IRCB): -500 mA (typical) / Reverse leakage (IIN,RCB): -1 uA (maximum) (原文照抄)",
        "source": "TI 官网产品页 https://www.ti.com/product/TPS22917 Features 栏 + 数据手册 ZHCSHL1B",
        "evidence": "[官网]"
      }
    },
    {
      "part": "TPS22910AYZVR",
      "vendor": "Texas Instruments",
      "package": "DSBGA-4 (YZV), 4 pin WCSP 0.9 x 0.9 mm, 0.5 mm pitch, 官网 package 栏 1.5625 mm² —— 4 脚但不是 UQFN-4 RAA => 必须改板; P 沟道 MOSFET",
      "cells": {
        "1": {
          "value": "工作输入 1.4 ~ 5.5 V; 绝对最大额定表本轮未取得 => 按 [0数据] 记; 官网 VIN 标称上限 5.5 V",
          "source": "TI 官网产品页 https://www.ti.com/product/TPS22910A (Input Voltage Range: 1.4 V to 5.5 V / Vin (max) 5.5 V)",
          "evidence": "[0数据]"
        },
        "2": {
          "value": "最大连续开关电流 2 A => 判据 2 卡在门槛",
          "source": "TI 官网产品页 https://www.ti.com/product/TPS22910A (2-A Maximum Continuous Switch Current)",
          "evidence": "[官网]"
        },
        "3": {
          "value": "RON 60 mΩ @ 5 V; 61 mΩ @ 3.3 V; 74 mΩ @ 1.8 V; 84 mΩ @ 1.5 V => 3.7 V 档 >= 61 mΩ => ★判据 3 (<= 40 mΩ @3.7V) 不满足; 但它是带 RCB 候选里 RON 最接近门槛的一个 (61 mΩ vs 40 mΩ)",
          "source": "TI 官网产品页 https://www.ti.com/product/TPS22910A (Low ON-Resistance RON = 60 mΩ at VIN = 5 V / 61 mΩ at 3.3 V / 74 mΩ at 1.8 V / 84 mΩ at 1.5 V)",
          "evidence": "[官网]"
        },
        "4": {
          "value": "ON 态 IQ typ 2 uA; OFF 态 ISD typ 1.2 uA => 判据 4 满足 (typ 口径), 但关断漏电比 TPS22916/17 的 10 nA 大两个数量级 (1.2 uA = 关机账 108 uA 的 1.1%)",
          "source": "TI 官网产品页 https://www.ti.com/product/TPS22910A 规格栏 (Quiescent current (Iq) (typ) 2 uA / Shutdown current (ISD) (typ) 1.2 uA)",
          "evidence": "[官网]"
        },
        "5": {
          "value": "有 RCB (Full-Time) —— 官网原文: The TPS22910A, TPS22912C, and TPS22913B/C devices provide reverse current protection in ON and OFF states ... Reverse current protection is always active, even when the power-switch is disabled. => ★判据 5 满足, 且是『ON 与 OFF 两种状态都挡』的 Full-Time 反向保护 (与本板关机插电场景完全对齐)",
          "source": "TI 官网产品页 https://www.ti.com/product/TPS22910A 描述栏原文 + Features 栏 (Full-Time Reverse Current Protection)",
          "evidence": "[官网]"
        },
        "6": {
          "value": "封装 0.9 x 0.9 mm WCSP 4 pin, 官网 package 栏 1.5625 mm² => 判据 6 (面积 <= 2 x 2 mm) 满足 (比 2 x 2 = 4 mm² 小)",
          "source": "TI 官网产品页 package 栏 (DSBGA (YZV) · 4 · 1.5625 mm²) + Features (Four Pin Wafer-Chip-Scale Package (Nom) 0.9 mm x 0.9 mm, 0.5-mm Pitch)",
          "evidence": "[官网]"
        },
        "7": {
          "value": "工作温度 -40 ~ +85 °C => 判据 7 满足 (下限卡 -40 °C)",
          "source": "TI 官网产品页 Operating temperature range (°C) = -40 to 85",
          "evidence": "[官网]"
        },
        "8": {
          "value": "ON 为数字输入, 官网 Features 栏把本族标为 Active low, 而官网把同族的 TPS22912C 描述为 5.5-V, 2-A, 60-mΩ load switch with active high enable ⇒ ★本族存在高/低两版, 本板要求高有效 ⇒ 具体 OPN 的 ON 极性必须按数据手册 Pin Functions 表逐颗核对 (本轮未取得该表 => 按 [0数据] 记); 无 power-off latch; 另有 UVLO 欠压锁定 (本板 SYS 下限 3.5V 场景需注意)",
          "source": "TI 官网产品页 https://www.ti.com/product/TPS22910A (Features 栏 Active low / Under voltage lock out + 同族 TPS22912C 页描述 with active high enable) —— Pin Functions 表本轮未取得",
          "evidence": "[0数据]"
        }
      },
      "rcb": {
        "verdict": "有",
        "quote": "The TPS22910A, TPS22912C, and TPS22913B/C devices provide reverse current protection in ON and OFF states. An internal reverse voltage comparator disables the power-switch when the output voltage (VOUT) is driven higher than the input voltage (VIN), by VRCP, to quickly (10 us typ) stop the flow of current towards the input side of the switch. Reverse current protection is always active, even when the power-switch is disabled. (原文照抄)",
        "source": "TI 官网产品页 https://www.ti.com/product/TPS22910A 描述栏 + Features 栏 (Full-Time Reverse Current Protection)",
        "evidence": "[官网]"
      }
    },
    {
      "part": "SGM2575SADYG/TR",
      "vendor": "圣邦微 SGMICRO (国产)",
      "package": "WLCSP-0.76 x 0.76-4B (4 ball, 绿色封装) => 0.578 mm², 比现 UQFN-4 RAA 的 0.6375 mm² 还小一点, 但封装不同 => 必须改板; 数据手册标题即 5.5V, 2A, 30 mΩ RDSON Load Switch with Reverse Current Protection",
      "cells": {
        "1": {
          "value": "数据手册标题 5.5V; 官方选型指南记 VIN 1.2 ~ 5.5 V => 工作上限 5.5 V; 绝对最大额定表本轮未取得 (PDF 抓取为二进制) => 按 [0数据] 记",
          "source": "圣邦微数据手册 https://www.sg-micro.com/rect/assets/a8959667-d386-4c95-a64d-205e9b7b4446/SGM2575S.PDF (标题行) + SGMICRO 官方选型指南 2025 Q3 (Avnet 镜像) 行 SGM2575S (VIN 1.2-5.5 V)",
          "evidence": "[媒体]"
        },
        "2": {
          "value": "2 A 连续电流 (数据手册标题 5.5V, 2A; 选型指南 Output Current 2000 mA) => 判据 2 卡在门槛",
          "source": "圣邦微数据手册 SGM2575S.PDF 标题行 + SGMICRO 官方选型指南 2025 Q3 (Avnet 镜像) 行 SGM2575S",
          "evidence": "[媒体]"
        },
        "3": {
          "value": "RDSON 30 mΩ (数据手册标题 5.5V, 2A, 30 mΩ RDSON) => 3.7 V 档按 30 mΩ 量级 => ★判据 3 (<= 40 mΩ @3.7V, 目标 <= 30 mΩ) 满足, 且是本次查证范围内唯一同时带 True RCB 且 RON <= 40 mΩ 的在售型号; 具体 @3.7 V 的 max 档本轮未取得 => 按 max 口径未判定",
          "source": "圣邦微数据手册 https://www.sg-micro.com/rect/assets/a8959667-d386-4c95-a64d-205e9b7b4446/SGM2575S.PDF 标题行 (30 mΩ RDSON)",
          "evidence": "[媒体]"
        },
        "4": {
          "value": "关断态反向电流 IRC typ 10 nA / max 900 nA (数据手册表: Reverse Current When Disabled, VIN = VON = 0V, VOUT = 5V); ON 脚漏电 ION typ 10 nA / max 900 nA (VON = 3.3V); 官方选型指南记静态电流 0.23 uA => 判据 4 (<= 5 uA) 满足",
          "source": "圣邦微数据手册 SGM2575S.PDF 电气特性表 (Reverse Current When Disabled / ON Pin Leakage Current / Smart Pull-Down Resistance 行) + SGMICRO 官方选型指南 2025 Q3 (Avnet 镜像)",
          "evidence": "[媒体]"
        },
        "5": {
          "value": "有 RCB 且是 True RCB —— 数据手册原文: The reverse current protection function is activated when VOUT is higher than VIN by VT_RCB. The reverse current protection is enabled whether the ON pin is high or ... ; 触发点 VT_RCB = VOUT - VIN: 6 mV typ (24 / 50 mV 上下限), 迟滞 VRCB_HYS 30 mV => ★判据 5 满足, 且比 SGM2572 的『仅禁用态』更强 (导通态也挡)",
          "source": "圣邦微数据手册 https://www.sg-micro.com/rect/assets/a8959667-d386-4c95-a64d-205e9b7b4446/SGM2575S.PDF (Reverse Current Protection 应用说明段 + True Reverse Current Blocking (RCB) Protection Trip Point / RCB Hysteresis 行)",
          "evidence": "[媒体]"
        },
        "6": {
          "value": "WLCSP-0.76 x 0.76-4B = 0.578 mm² => 判据 6 (面积 <= 2 x 2 mm) 满足, 是 6 个候选里面积最小的",
          "source": "圣邦微数据手册 SGM2575S.PDF (Available in a Green WLCSP-0.76 x 0.76-4B Package) + SGMICRO 官方选型指南 2025 Q3 行 SGM2575S",
          "evidence": "[媒体]"
        },
        "7": {
          "value": "工作温度本轮未取得 (官网产品页未抓取到 SGM2575S 页面, PDF 为二进制) => 按 [0数据] 记; 同厂同系列 SGM2572/SGM2575 官网标 -40 ~ +85 °C, 只能作为参考, 不能当本型号的官方值",
          "source": "圣邦微数据手册 SGM2575S.PDF 订购信息表 —— 本轮未取得; 参考同厂 SGM2572 官网 -40℃ to +85℃ (仅作系列参考, 不作本型号证据)",
          "evidence": "[0数据]"
        },
        "8": {
          "value": "ON 脚输入高低阈值: 数据手册电气表提取到的文本为 VIH 0.71 V / VIL 0.3 V (疑为分压比例或表格截断) => 精确值按 [0数据] 记, 落表前必须查 PDF 原表; Smart Pull-Down Resistance 1 MΩ (Disabled), 输出下拉 RPD 230 Ω typ / 300 Ω max => 默认态有内部下拉兜底, 外部 10k 下拉仍保留; 上升时间/QOD 选项: QOD 仅 SGM2575SAD 有 (数据手册 Quick Output Discharge (SGM2575SAD Only))",
          "source": "圣邦微数据手册 SGM2575S.PDF 电气特性表 (ON Pin Input High Voltage / ON Pin Input Low Voltage / Smart Pull-Down Resistance / Output Pull-Down Resistance 行) + Features (Quick Output Discharge (SGM2575SAD Only))",
          "evidence": "[媒体]"
        }
      },
      "rcb": {
        "verdict": "有",
        "quote": "The reverse current protection function is activated when VOUT is higher than VIN by VT_RCB. The reverse current protection is enabled whether the ON pin is high or ... (原文照抄, 后半句在 PDF 提取中被截断); True Reverse Current Blocking (RCB) Protection Trip Point VT_RCB: VOUT - VIN, 6 mV typ, 24 / 50 mV; RCB Hysteresis VRCB_HYS 30 mV",
        "source": "圣邦微数据手册 https://www.sg-micro.com/rect/assets/a8959667-d386-4c95-a64d-205e9b7b4446/SGM2575S.PDF (Reverse Current Protection 段 + 电气特性表 RCB 行)",
        "evidence": "[媒体]"
      }
    }
  ],
  "conclusion": {
    "same_package_with_rcb_available": false,
    "same_package_check_scope": "本次查证范围 = TI TPS229xx 单路负载开关族 (91/16/17/18/19/10A) + 圣邦微 SGM2572/SGM2575S。范围内带 RCB 的 4 款 (TPS22916 / TPS22917 / TPS22910A / SGM2572 / SGM2575S) 封装分别是 DSBGA-4 YFP / SOT-23-6 DBV / DSBGA-4 YZV / WLCSP-0.8x0.8-4B / WLCSP-0.76x0.76-4B —— 没有一款是现网表 footprint 的 UQFN-4 RAA (0.85 x 0.75, 0.4 mm pitch)。★残留缺口 [0数据]: TI 官网参数筛选器里 4 脚 UQFN-HR (RAA) 全系带 RCB 的型号本轮未逐项穷举 ⇒ 若老板要求 100% 穷举, 需按 TI 官网 Load Switch 参数筛选器 (Package = UQFN-HR 4 / VIN <= 5.5 / Reverse Current Protection = Yes) 过滤后逐个核数据手册, 这是一条人工动作 (本单不做, 也不能靠推断代替)",
    "recommendation_order_source": "DECISION_PENDING_2026-11-16.md §A5 (老板待拍优先级序: 1 反向阻断 > 2 IQ < 5uA > 3 RON 越小越好 > 4 封装/面积)",
    "recommendation_by_a5_order": "按 A5 建议序: (1) 反向阻断优先 => 唯一同时满足 RCB + RON <= 40 mΩ 的在售型号是 SGM2575SADYG/TR (True RCB, 30 mΩ, 2A, 0.578 mm²), 代价 = 改板 + 引脚定义本轮 [0数据] 须核 PDF 原表; (2) 若 IQ/关机续航优先 => TPS22916BYFPR (ISD 10 nA typ / 100 nA max) 与 TPS22917xDBVR (10 nA typ) 最好, 但 RON 60/80 mΩ 超判据 3; (3) 若 RON 优先 => TPS22991RAA 25 mΩ 最优但无 RCB, 且关断漏电 max 20 uA 超判据 4; (4) 若 封装/面积/不改板优先 => 只有 TPS22991RAA (同封装 UQFN-4 RAA, 换料不换板) 满足, RCB 缺口用 FB1 兜",
    "recommendation_disclaimer": "★本单只交证据 + 按 A5 建议序的推荐, 不代拍优先级序, 不代拍型号 ⇒ 最终拍板 = 老板 (DECISION_PENDING_2026-11-16.md §A5 / §Q2)",
    "key_findings": [
      "TPS22991RAA (ISS-234 点名推荐) 唯一硬超判据的是判据 4 的 max 口径: 关断漏电 ISD max 20 uA @ -40~85 °C > 5 uA (typ 14 nA 远低于门槛) => 关机账 108 uA 里这一项按 max 占 18.5%",
      "现网表 OPN 'TPS22991RAA' 只锁了封装 (RAA), 没有变体字母: TI 数据手册 Device Comparison Table 列 TPS22991B/BN (快上电) 与 TPS22991C/CN (慢上电) 四个变体, 上电上升时间 141 us (B/BN) vs 662 us (C/CN) @3.3V, 且 QOD 有无随变体不同 => 落表批次必须补全 OPN 变体字母",
      "RCB 缺口在本板是硬需求而不是形式条款: 关机插 USB 时充电板 PG 拉低 => Q_PG (P-MOS 高边, HW/POWER_SHUTDOWN_V3.md §3) 把 ON 拉到 BAT_SW => 负载开关被强制导通 => 5V 经 SoC IO 到 SYS 再经开关通道反灌回 BAT_SW; N 沟道体二极管只挡 VIN->VOUT 方向, 挡不住导通态的通道反灌 => 没有 RCB 就真的会把电池反灌",
      "判据口径冲突 (本单只报不改): HW/POWER_SHUTDOWN_V3.md §2 判据 2 写 Iout >= 2A (持续 1A 上下), 而 HW/netlist_v1.csv L37 写 SYS 最大电流 0.55A (330 mA x 1.5 + 瞬态) => 两处口径不一致, 压降与发热推算按 0.55A / 1A / 2A 三档都给, 由老板与 main 裁"
    ]
  },
  "netlist_value_snapshot": "[待选型] 负载开关 (≥2A, R_on ≤40mΩ@3.7V, IQ ≤5µA, 带反向阻断)"
}
```
<!-- END 选型证据基准块 -->

> ★**上面这段是机器可读基准块** (只由 `SW/tools/check_load_switch_selection.py` 校验; 人读的那份是 §2 的矩阵与 §3 的 RCB 专项)。★**不要手改**: 改完必须重跑门禁 `python3 SW/tools/check_load_switch_selection.py` (rc=0) 与 `--selftest` (8/8)。
