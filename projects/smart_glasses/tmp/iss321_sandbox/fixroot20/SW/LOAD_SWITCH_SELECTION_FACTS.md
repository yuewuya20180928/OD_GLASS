# SW/LOAD_SWITCH_SELECTION_FACTS.md —— 负载开关 U_PWR_SW_1 / U_EN_SW_1 选型证据矩阵 (ISS-172)

> **作者**: 软件总工 (sw-lead) · **日期**: 2026-11-16 · **验证人**: boss (拍板) / main (复核)
> **上游 (只读)**: `HW/POWER_SHUTDOWN_V3.md` §2 (8 条选型判据 · 一字不改) · `SW/SHUTDOWN_SEMANTICS_SPEC.md` §3 Q2 (ISS-234 交卷件) · `DECISION_PENDING_2026-11-16.md` §A5 + §Q2 (拍板待办) · `HW/netlist_v1.csv` L37/L50/L56/L58/L442 (现状真源)
> **边界**: ★**本单只交证据, 不落表** (★**第 2 轮 2026-11-17: 网表 L50 的 `[待选型]` 串已由 ISS-257 落表批次落成型号串 ⇒ 派单前提过期 ⇒ 本单第 2 轮只做「快照重锚 + C9 落表后回归门禁」, 仍然一个字都不落表**) · ★**不改** `HW/` `MECH/` 任何文件 (只读) · ★**零外发** (不发邮件 / 不询价 / 不问供应商 / 不下单) · ★**实物 [实测] = 0 条** (本单全部是公开数据手册级证据, 没有一颗实物被测过)
> **政策**: 老板 2026-11-12 02:02「不再发信, 全靠自己查资料」⇒ 证据等级只取 `[官网]` / `[实测]` / `[媒体]` / `[推算]` / `[0数据]` · **查不到就写 [0数据] + 降级方案, 不许编**
> **机器门禁**: `python3 SW/tools/check_load_switch_selection.py` (rc=0 = 全过) · `--selftest` (★**第 2 轮起 12 条**反向用例全红 ★)

---

## §0 一句话结论 (B1 摘要)

★**本单把「负载开关待选型」从一句话变成了一张可拍板的证据矩阵: 6 个原厂在售型号 × `HW/POWER_SHUTDOWN_V3.md` §2 的 8 条判据逐格填满 (每格带官方数值 + 出处 + 证据等级), 并且把 ISS-234 点名的「无 RCB 缺口」做实了。**

1. ★**结论 (机器可判)**: ★**就本次查证范围内, 没有「同封装 (UQFN-4 RAA) 且带 RCB」的原厂在售型号** ⇒ 必须走降级方案 (FB1 外部反灌保护 / FB2 改板换带 RCB 型号) 之一。带 RCB 的 5 款 (TPS22916 / TPS22917 / TPS22910A / SGM2572 / SGM2575S) 封装分别是 DSBGA-4 YFP · SOT-23-6 DBV · DSBGA-4 YZV · WLCSP-0.8×0.8-4B · WLCSP-0.76×0.76-4B, 没有一个是 RAA。
2. ★**按 A5 建议序 (① 反向阻断 > ② IQ<5µA > ③ RON 越小越好 > ④ 封装/面积) 的推荐**:
   - 若老板把 ① 放最前 ⇒ **SGM2575SADYG/TR** (圣邦微 · True RCB 导通态也挡 · ★**30 mΩ typ / 63 mΩ max**· 2A · 0.578 mm²) 是本次查证范围内**唯一同时满足 RCB 与 RON ≤ 40 mΩ (typ 口径)** 的在售型号 ⇒ 代价 = 改板 + ★**引脚编号体系整体换 (A1=VOUT/A2=VIN/B1=GND/B2=ON, 与现网表 1/2/3/4 无一兼容)**;
   - 若老板把 ④ (封装/面积/**不改板**) 放最前 ⇒ **TPS22991RAA** (唯一与现网表 footprint 逐字一致的 UQFN-4 RAA ⇒ 换料不换板) ⇒ RCB 缺口用 **FB1** 兜;
   - 若 ② (关机续航) 放最前 ⇒ **TPS22916BYFPR / TPS22917xDBVR** 的关断漏电最好 (10 nA typ), 但 RON 60 / 80 mΩ 超判据 3。
3. ★**ISS-234 点名的 `TPS22991RAA` 仍留在册 (不许悄悄删)** —— 但本轮补上了一条它此前没写的事实: ★**它的关断漏电 ISD max = 20 µA @ -40~85 °C > 判据 4 的 5 µA 门槛** (typ 14 nA 远低于门槛) ⇒ 按 max 口径它是**唯一硬超判据**的一条, 在关机账 108 µA 里占 18.5%。
4. ★**2026-11-17 04:5x 补证轮 (★把上一轮剩下的缺口填平★)**: ★**圣邦微两颗候选的官方数据手册 PDF 已从官方服务器直取成功** ⇒ ① SGM2575S / SGM2572 的证据等级全部从 [媒体] → **[官网]**, 全文已无 [媒体] 依赖; ② ★**两个 [0数据] 关闭**: 绝对最大额定 (VIN −0.3~6 V ⇒ 判据 1 满足) 与 **4-ball 引脚原表** (SGM2575S: A1 OUT / A2 IN / B1 GND / B2 ON; SGM2572: A1 VOUT / A2 VIN / B1 GND / B2 ON) ⇒ ★**原来那条「改板返工代价最高的一项」已不再是未知**; ③ ★**查出一条对推荐有实质影响的新事实**: SGM2575S 的 **RON max = 63 mΩ** (SGM2572 = 60 mΩ) ⇒ ★**「唯一 RCB + RON 双满足」只在 typ 口径成立; max 口径下没有任何一颗带 RCB 的在售型号能过判据 3** ⇒ 建议老板拍优先级序时★**一并拍「RON 按 typ 还是按 max 判」+「SYS 电流按 0.55 A 还是 2 A 算」** (§4 第 3 条落点 / §3.4 事实 B)。
5. ★**两条顺带查出来的落表阻塞**: ①现网表 OPN `TPS22991RAA` **只锁了封装没锁变体字母** (TI 有 B/BN/C/CN 四个变体, 上电上升时间 141 µs vs 662 µs, QOD 有无也不同); ②★**【2026-11-17 已解除】** SGM2575S / SGM2572 的 4-ball 引脚定义不再是 [0数据] ⇒ ★**但取到后反而多了一条硬事实: 三颗 RCB 候选 (TPS22916 / SGM2572 / SGM2575S) 的球编号全是 A1=VOUT / A2=VIN / B1=GND / B2=ON, 与现网表 1=VIN/2=ON/3=VOUT/4=GND 无一兼容 ⇒ 改板不是「换个料号」, 是「换引脚编号体系」⇒ 板那一趟必须逐线重核** (§3.4 事实 A)。
6. ★**本单不代拍**: 优先级序与型号的最终拍板 = 老板 (`DECISION_PENDING_2026-11-16.md` §A5 / §Q2)。


## §0.1 ★第 2 轮补记 (2026-11-17): 落表已经发生 ⇒ 派单前提 `[待选型]` 已过期

★**本节是 2026-11-17 第 2 轮实测补的; 第 1 轮 (2026-11-16 12:58 交卷) 的 8 条判据逐格评定、RCB 专项结论与 §4 推荐一字未改。**

1. ★**派单书的前提已不成立 (不是本单做错了, 是世界变了)**: 派单 (main 2026-11-16 10:4x 实读) 的前提是「网表 L50 value 栏至今是 `[待选型] 负载开关 (≥2A, R_on ≤40mΩ@3.7V, IQ ≤5µA, 带反向阻断)`」★**该前提在 2026-11-16 21:2x~22:25 之间失效** ⇒ 落表批次 **ISS-257 (hw-lead · G1a-7 选型落表)** 把 L50 的 value 栏改成 ★**`TPS22991RAA (负载开关 1=VIN/2=ON/3=VOUT/4=GND, UQFN-4 RAA · ≥2A · R_on 25mΩ@5V · 无 RCB ⇒ 选型口径待 A5 追认)`** ⇒ **[实测]** 2026-11-17 实读 `HW/netlist_v1.csv` L50 (md5 `e06c1dd633566aa44732762c2ff99d1c`)。
2. ★**落表用的就是本单的矩阵**: ISS-257 落的型号 = `TPS22991RAA` = 本矩阵里**唯一与现网表 footprint 逐字一致** (UQFN-4 RAA 0.85×0.75 mm 0.4 mm pitch) 的候选 ⇒ ★**「换料不换板」这条结论已被落表批次采纳**; 并且落表串里★**明写了「无 RCB ⇒ 选型口径待 A5 追认」** ⇒ ★**RCB 缺口没有被落表掩盖, 而是被写进了网表** ⇒ 与本单 §3.3 的结论 (无同封装带 RCB 的在售型号) 一致。
3. ★**但落表把两条判据从网表 value 栏里拿掉了 (必须登记, 不能装作没发生)**: 旧串写「IQ ≤5µA」与「带反向阻断」, 新串只剩「≥2A」「R_on 25mΩ@5V」, 并把「带反向阻断」改写成「无 RCB」⇒ ★**判据 4 (IQ) 与判据 5 (反向阻断) 在网表侧不再以「要求」的形式出现** ⇒ ★**判据真源仍是 `HW/POWER_SHUTDOWN_V3.md` §2 (8 条, 一个字没改, 门禁 C7 逐条比)** ⇒ 本矩阵的逐格评定继续按 8 条判据走, 网表侧的失声登记在基准块 `netlist_drift.dropped_requirements`。
4. ★**落表后残留 3 条缺口 (本单只登记, 不落表)**: 见 §9.2 ⇒ 归属 = 落表批次 / main。
5. ★**第 2 轮只做两件事**: ① 把基准块的网表快照**重锚**到现行 value, 并把 drift 登记成机器可读块; ② **给门禁加一条 C9 (落表后回归)**, 让「矩阵与网表各说各话」这件事在落表之后**仍然抓得住** ⇒ ★**第 1 轮的 C6 只对落表前的快照有效, 落表后是个洞 (本轮实测发现)**。

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
| C3 | **SGM2572ADYG/TR** | 圣邦微 (国产) | WLCSP-0.8×0.8-4B · 0.64 mm² | **有** (仅禁用态) | ★**封装不同 ⇒ 必须改板**; ★**引脚 A1=VOUT / A2=VIN / B1=GND / B2=ON** (官方 PDF 原表) | [官网] |
| C4 | TPS22917xDBVR | TI | SOT-23-6 (DBV) 2.9×2.8mm · 8.12 mm² | **有** (Always-ON true) | ★**6 脚 + 超判据 6 面积 ⇒ 必须改板**; 引脚 1=VIN/2=GND/3=ON/4=CT/5=QOD/6=VOUT | [官网] |
| C5 | TPS22910AYZVR | TI | DSBGA-4 (YZV) WCSP 0.9×0.9 · 1.5625 mm² | **有** (Full-Time, ON+OFF) | ★**封装不同 ⇒ 必须改板**; ON 极性需按具体 OPN 核对 | [官网] |
| C6 | **SGM2575SADYG/TR** | 圣邦微 (国产) | WLCSP-0.76×0.76-4B · 0.578 mm² | **有** (True RCB, 导通态也挡) | ★**封装不同 ⇒ 必须改板**; ★**引脚 A1=OUT / A2=IN / B1=GND / B2=ON** (官方 PDF 原表) | [官网] |

> ★**候选册说明 (机器基准块口径)**: 门禁 C1 的反向用例是「**把候选砍到 2 个 ⇒ 红**」⇒ 机器基准块的 `candidates` 册**正好取 3 个** (C1 / C2 / C3) 才能自证「砍一个就红」; C4 / C5 / C6 以基准块的 `alternates` 数组**同字段并列**, 正文 §2 矩阵 **6 行全部逐格填满**, 没有一个是「大概/应该」。
> ★**全部为原厂在售**: TI 官网产品页均标 ACTIVE / Catalog; 圣邦微官网订购信息栏标「量产」。

### 2.2 判据 × 候选 总表 (机器基准块的正文镜像)

| # | 判据 | C1 TPS22991RAA | C2 TPS22916BYFPR | C3 SGM2572ADYG/TR | C4 TPS22917xDBVR | C5 TPS22910AYZVR | C6 SGM2575SADYG/TR |
|---|---|---|---|---|---|---|---|
| 1 | VIN 绝对额定 ≥ 5V | 绝对最大 VIN −0.3~**6 V**; 工作 1.0–5.5 V ✔ | 绝对最大 VIN −0.3~**6 V**; 工作 1.0–5.5 V ✔ | ★绝对最大 VIN −0.3~**6 V**; 工作 1–5.5 V ✔ | 工作 1–5.5 V ✔; 绝对最大 [0数据] | 工作 1.4–5.5 V ✔; 绝对最大 [0数据] | ★绝对最大 VIN −0.3~**6 V**; 工作 1.2–5.5 V ✔ |
| 2 | Iout ≥ 2A | **3 A** ✔ | **2 A** (脉冲 2.5 A) ⚠卡门槛 | **2 A** (脉冲 2.5 A) ⚠卡门槛 | **2 A** ⚠卡门槛 | **2 A** ⚠卡门槛 | **2 A** ⚠卡门槛 |
| 3 | R_on ≤ 40mΩ @3.7V | **25 mΩ typ @5V** (3.7V 内插 ~27–28) ✔ 目标≤30 | 60 mΩ typ @5V (max 100@85°C) ✘ | ★**34 mΩ typ / 60 mΩ max** ⇒ typ ✔ / ★max ✘ | 80 mΩ typ @5V ✘ | 61 mΩ @3.3V ✘ | ★**30 mΩ typ / ★63 mΩ max** ⇒ typ ✔ / ★max ✘ |
| 4 | 关机漏电 IQ ≤ 5µA | ISD **14 nA typ** / ★**20 µA max @-40~85°C** ✘ (max 口径) | ISD 10 nA typ / 100 nA max ✔ | ★ISD **90 nA typ / 440 nA max** ✔ | ISD 10 nA typ ✔ (max 未取得) | ISD 1.2 µA typ ✔ | ★ISD **0.15 µA typ / 0.5 µA max** ✔ |
| 5 | 必须有反向阻断 | ★**无** ✘ (缺口) | **有** Always-ON true ✔ | **有** (仅禁用态) ✔ | **有** Always-ON true ✔ | **有** Full-Time ✔ | **有** True RCB ✔ |
| 6 | 面积 ≤ 2×2mm | 0.6375 mm² ✔ | 1 mm² ✔ | 0.64 mm² ✔ | 8.12 mm² ✘ | 1.5625 mm² ✔ | 0.578 mm² ✔ |
| 7 | −40 ~ +85 °C | −55~+125 °C ✔ | −40~+85 °C ✔ | −40~+85 °C ✔ | −45~+125 °C ✔ | −40~+85 °C ✔ | ★**−40~+125 °C** ✔ (原表已取) |
| 8 | ON 兼容 3.3V GPIO + 确定默认态 | ON=pin2 高有效 ✔ (内部下拉 [0数据], 外部 10k 兜底) | 高有效 ✔ + 智能下拉 750 kΩ typ ✔ | ★VIH **1.1 V** / VIL 0~0.4 V ✔ (3.3V GPIO 可驱动) | ON=pin3 高有效 ✔ + 750 kΩ typ ✔ | 高/低两版 ★**须按 OPN 核对** | ★VIH **0.71 V** / VIL 0~0.3 V ✔ + 智能下拉 1 MΩ ✔ |

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
- **判据 8**: ON = pin2, 原文「Active high switch control input」⇒ **高有效, 与网表 (SoC GPIO 拉高 = 开机) 一致**; 芯片内部 ON 下拉阻值本轮未取得 ([0数据]), 但本设计不依赖它 (网表 L56 `R_PD_ON_1` 10k 下拉已在) ⇒ 默认态确定; 无 power-off latch 型号 `[官网]`。
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
★**★2026-11-17 04:5x 本轮补证 (★官方 PDF 直取成功 ⇒ 证据等级从 [官网] 官网产品页 + [媒体] 第三方镜像 升级为 [官网] 官方数据手册★)**

- **封装**: WLCSP-0.8 × 0.8-4B (4 ball, 绿色封装) ⇒ **不是 RAA ⇒ 必须改板**; 官网订购信息栏三个 OPN (A/B/C = 上升 85 / 1600 / 2200 µs), 状态「量产」`[官网]`。
- **★引脚定义 (★本轮从官方 PDF 原表取到 ⇒ 原 [0数据] 已关闭★)**: 官方手册 PIN CONFIGURATION (TOP VIEW) = **A1 VOUT / A2 VIN / B1 GND / B2 ON**; PIN DESCRIPTION 原文「A2 VIN — Switch Input. It is recommended to use a bypass capacitor (ceramic) to ground.」「B2 ON — Switch Control Input. Active high enables the device. **Do not float this pin.**」⇒ ★**与网表 1=VIN / 2=ON / 3=VOUT / 4=GND 完全不兼容 ⇒ 改板必须重画 footprint** `[官网]`。
- **判据 1**: 工作 1–5.5 V; ★**绝对最大额定 (官方 PDF ABSOLUTE MAXIMUM RATINGS 表): Input Voltage Range VIN = −0.3 V to 6 V / Output Voltage Range VOUT = −0.3 V to 6 V / ON Pin Voltage Range VON = −0.3 V to 6 V** ⇒ **满足** (6 V > 5 V) `[官网]`。
- **判据 2**: Maximum Continuous Switch Current, **IMAX = 2 A**; 脉冲 IPLS = 2.5 A (pulse < 300 µs, 2% duty) ⇒ **卡门槛** `[官网]`。
- **判据 3**: RON **34 mΩ typ / ★60 mΩ max** @ VIN=5 V 与 @ VIN=3.3 V ⇒ 3.7 V 档 typ ≈ 34 mΩ ⇒ **按 typ 满足** (目标 ≤30 mΩ 差一点); ★**按 max 口径不满足 (60 mΩ > 40 mΩ, 超 50%)**; 压降 @1A = 34 mV typ / 60 mV max `[官网]`。
- **判据 4**: Shutdown Current ISD **90 nA typ / 440 nA max** (VIN=5.5 V, VON=0 V); Quiescent Current IQ **220 nA typ / 400 nA max** (VIN=3.3 V) / 320 nA typ / 560 nA max (VIN=5 V) / 140 nA typ / 300 nA max (VIN=1 V); Supply Leakage Current in Shutdown Mode ILEAKAGE 450 nA max; ON Pin Leakage Current ION 420 nA max ⇒ **typ 与 max 双双满足** (关机账 108 µA 的 0.4%) `[官网]`。
- **判据 5**: ★**有, 但只在禁用态** —— ★**官方手册 APPLICATION INFORMATION 原文: "If the ON pin is pulled low, the device is disabled, while VIN > 1V or VOUT > 1V is met, the reverse current protection function is activated. This function prevents the current flowing from VOUT to VIN…"** ⇒ ★**全手册无 "True Reverse Current Blocking" 字样、无 VT_RCB 行 ⇒ 官方坐实「仅禁用态」** ⇒ 对本板「关机插 USB (开关禁用)」场景是覆盖的; ★**导通态不挡** ⇒ 缺口说明必须写清这一条 `[官网]`。
- **判据 6**: 0.64 mm² (WLCSP-0.8×0.8-4B) ⇒ **满足** (与现 RAA 同面积, 但不是同一封装, 不能直接换料); 官方手册热阻 θJA = 279 ℃/W `[官网]`。
- **判据 7**: 官方 PACKAGE/ORDERING INFORMATION 表 SPECIFIED TEMPERATURE RANGE = **−40 ℃ to +85 ℃** ⇒ **满足** `[官网]`。
- **判据 8**: ★**官方 RECOMMENDED OPERATING CONDITIONS: ON Pin Input High Voltage VIH = 1.1 V to 5.5 V (min 1.1 V) / ON Pin Input Low Voltage VIL = 0 V to 0.4 V** ⇒ 3.3 V GPIO 可直接驱动 ⇒ **满足**; 官网特性栏另有「低阈值 1.8V GPIO 控制输入」; 官方手册未列内部下拉阻值 ⇒ 靠外部 10k 下拉兜底; 无 power-off latch `[官网]`。

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

★**★2026-11-17 04:5x 本轮补证 (★官方 PDF 直取成功 ⇒ 全部 [媒体] → [官网]★)**

- **封装**: WLCSP-0.76 × 0.76-4B = 0.578 mm² ⇒ **面积最小的候选**, 但封装不同 ⇒ **必须改板**; 数据手册标题即「5.5V, 2A, 30 mΩ RDSON Load Switch with Reverse Current Protection」`[官网]`。
- **★引脚定义 (★本轮从官方 PDF 原表取到 ⇒ 原 [0数据] 已关闭★)**: 官方手册 PIN CONFIGURATION (TOP VIEW) = **A1 OUT / A2 IN / B1 GND / B2 ON**; PIN DESCRIPTION 原文「A1 OUT — Switch Output.」「A2 IN — Switch Input. It is recommended to use a bypass capacitor (ceramic) to ground.」「B1 GND — Ground.」「B2 ON — Switch Control Input. Setting the ON pin to a high logic level enables the device, and setting it to a low logic level disables the device.」⇒ ★**与网表 1=VIN / 2=ON / 3=VOUT / 4=GND 完全不兼容 ⇒ 改板必须重画 footprint** `[官网]`。
- **判据 1**: ★**绝对最大额定 (官方 PDF ABSOLUTE MAXIMUM RATINGS 表): Input Voltage Range VIN = −0.3 V to 6 V / Output Voltage Range VOUT = −0.3 V to 6 V / ON Pin Voltage Range VON = −0.3 V to 6 V**; RECOMMENDED OPERATING CONDITIONS: Input Voltage Range VIN = 1.2 V to 5.5 V ⇒ **满足** (6 V > 5 V) `[官网]`。
- **判据 2**: Maximum Continuous Switch Current, **IMAX = 2 A** ⇒ **卡门槛** `[官网]`。
- **判据 3**: ★**官方 EC 表 On-Resistance RDSON: VIN = 5.5 V → typ 30 mΩ / ★max 63 mΩ; VIN = 3.3 V → typ 30 mΩ / ★max 63 mΩ; VIN = 1.2 V → typ 48 mΩ** (IOUT = −200 mA, VON = 1.2 V) ⇒ 3.7 V 档 typ ≈ 30 mΩ ⇒ ★**按 typ 满足 (30 mΩ ≤ 40 mΩ, 也压住目标 ≤30 mΩ)**; ★**按 max 口径不满足 (63 mΩ > 40 mΩ, 超 57%)** —— ★**这是本轮新查出来的口径差异, 见 §4 末条** `[官网]`。
- **判据 4**: ★**官方 EC 表: Shutdown Current ISD (VIN=5.5 V, VON=0 V) TJ=−40~85 °C → typ 0.15 µA / ★max 0.5 µA; TJ=−40~125 °C → typ 0.15 µA / max 1.2 µA; Supply Leakage Current in Shutdown Mode ILEAKAGE 同档; Quiescent Current IQ (VIN=3.3 V) typ 0.37 µA / max 1.1 µA; (VIN=5.5 V) typ 0.57 µA / max 1.5 µA; ON Pin Leakage Current ION 10 nA typ / 900 nA max; Reverse Current When Disabled IRC 10 nA typ / 900 nA max** ⇒ **typ 与 max 双双满足 ≤5 µA** (官方 FEATURES 栏: Low Shutdown Current 0.15 µA TYP · Low Quiescent Current 0.23 µA TYP) `[官网]`。
- **判据 5**: ★**有, True RCB** —— ★**官方 EC 表原文: "True Reverse Current Blocking / RCB Protection Trip Point VT_RCB (VOUT − VIN): typ 6 mV, min 24 mV, max 50 mV / RCB Hysteresis VRCB_HYS: 30 mV"**; ★**官方 APPLICATION INFORMATION 原文: "The reverse current protection function is activated when VOUT is higher than VIN by VT_RCB. The reverse current protection is enabled whether the ON pin is high or low. This function prevents the current flowing from OUT to IN…"** ⇒ **导通态也挡**, 比 SGM2572 的「仅禁用态」更强 `[官网]`。
  - ★**⚠️ 官方手册内部措辞不一致 (本轮如实记录, 不替厂家圆场)**: 同一份手册的 FEATURES 栏写的是「**Reverse Current Protection When Disabled**」(与 SGM2572 同措辞), 而 EC 表写「**True Reverse Current Blocking**」、APPLICATION INFORMATION 写「enabled whether the ON pin is high or low」、FUNCTIONAL BLOCK DIAGRAM 里也画了 Reverse Current Blocking 模块 ⇒ ★**以 EC 表 + 应用说明 + 功能框图三处一致为准 = True RCB (导通态也挡); FEATURES 那一行按厂家的简写看待, 不作反向证据** `[官网]`。
- **判据 6**: 0.578 mm² (WLCSP-0.76×0.76-4B) ⇒ 满足, 6 个候选里最小; 官方热阻 θJA = 221 ℃/W / θJB = 82.6 ℃/W / θJC = 92.9 ℃/W `[官网]`。
- **判据 7**: ★**官方 PACKAGE/ORDERING INFORMATION 表 SPECIFIED TEMPERATURE RANGE = −40 ℃ to +125 ℃** (两个 OPN 皆是) ⇒ **满足**, 上限余量 40 °C `[官网]`。
- **判据 8**: ★**官方 RECOMMENDED OPERATING CONDITIONS: ON Pin Input High Voltage VIH = 0.71 V to 5.5 V / ON Pin Input Low Voltage VIL = 0 V to 0.3 V** ⇒ 3.3 V GPIO 可直接驱动 ⇒ **满足**; 官方 FEATURES「Low Threshold 1.2V GPIO Control Input」+「Smart ON」(上电期间智能下拉电阻避免 ON 引脚悬空, ON > VIH 后断开 ⇒ 默认态确定) + EC 表 Smart Pull-Down Resistance RPD_ON = 1 MΩ (Disabled) · Output Pull-Down Resistance RPD = 230 Ω typ / 300 Ω max (仅 SGM2575SAD 有 QOD) ⇒ **默认态有内部下拉兜底 (外部 10k 下拉仍保留)**; 另有 UVLO: VUVLO_R 0.94 V typ / 1.26 V max (TJ=−40~125 °C), 迟滞 100 mV ⇒ SYS 下限 3.5 V 场景不受影响 `[官网]`。
- **★订购信息 (官方 PACKAGE/ORDERING INFORMATION 表)**: SGM2575SAYG/TR (marking 01) 与 ★**SGM2575SADYG/TR (marking 00)**, 均为 WLCSP-0.76×0.76-4B · −40 ℃ to +125 ℃ · Tape and Reel 4000 `[官网]`。

---

## §3 RCB (反向电流阻断) 专项 —— 把 ISS-234 的缺口做实

### 3.1 逐候选判定 (官方原文摘录, 不是转述)

| 型号 | 判定 | 官方原文摘录 | 出处 | 等级 |
|---|---|---|---|---|
| **TPS22991RAA** | ★**无** | 「Features: Inrush current control, Quick output discharge, Thermal shutdown」—— 无 Reverse current protection 条目; Description 只提 N 沟道 MOSFET 与 150 Ω QOD | TI 官网产品页 + 数据手册 SLVSFK0B §1/§3 | [官网] |
| **TPS22916BYFPR** | **有** | 「Always-ON true Reverse Current Blocking (RCB): Activation current (IRCB): −500 mA (typ.) / Reverse leakage (IIN,RCB): −300 nA (max.)」 | TI 官网产品页 Features | [官网] |
| **TPS22917xDBVR** | **有** | 「Always-ON true Reverse Current Blocking (RCB): Activation current (IRCB): −500 mA (typical) / Reverse leakage (IIN,RCB): −1 µA (maximum)」 | TI 官网产品页 Features | [官网] |
| **TPS22910AYZVR** | **有** | 「The TPS22910A, TPS22912C, and TPS22913B/C devices provide reverse current protection in ON and OFF states. An internal reverse voltage comparator disables the power-switch when the output voltage (VOUT) is driven higher than the input voltage (VIN), by VRCP, to quickly (10 µs typ) stop the flow of current towards the input side of the switch. Reverse current protection is always active, even when the power-switch is disabled.」 | TI 官网产品页 描述栏 | [官网] |
| **SGM2572ADYG/TR** | **有** (仅禁用态) | ★**官方数据手册 APPLICATION INFORMATION 原文: "If the ON pin is pulled low, the device is disabled, while VIN > 1V or VOUT > 1V is met, the reverse current protection function is activated. This function prevents the current flowing from VOUT to VIN…"** (★**全手册无 "True Reverse Current Blocking" 字样、无 VT_RCB 行 ⇒ 官方坐实「仅禁用态」★) | 圣邦微官方数据手册 SGM2572.pdf (MAY 2022, SG Micro Corp) §APPLICATION INFORMATION + FEATURES 栏 | [官网] |
| **SGM2575SADYG/TR** | **有** (True, 导通态也挡) | ★**官方数据手册 APPLICATION INFORMATION 原文: "The reverse current protection function is activated when VOUT is higher than VIN by VT_RCB. The reverse current protection is enabled whether the ON pin is high or low. This function prevents the current flowing from OUT to IN…"** + ★**EC 表原文: "True Reverse Current Blocking / RCB Protection Trip Point VT_RCB (VOUT − VIN): typ 6 mV, min 24 mV, max 50 mV / RCB Hysteresis VRCB_HYS: 30 mV"** | 圣邦微官方数据手册 SGM2575S.PDF (JULY 2025 – REV.A.1, SG Micro Corp) §APPLICATION INFORMATION + §ELECTRICAL CHARACTERISTICS | [官网] |
| TPS22918DBVR (★查过 = 无) | **无** | 官网 Features 只有「Inrush current control, Quick output discharge」 | TI 官网产品页 | [官网] |
| TPS22919DCKR (★查过 = 无) | **无** | 官网 Features 只有「Inrush current control, Quick output discharge, Short circuit protection, Thermal shutdown」 | TI 官网产品页 | [官网] |

> ★**brief 点名的「TPS22918 / TPS22919 一类是不是带 RCB」已按官方数据手册/官网 Features 逐个核过**: ★**这两款都【不带】RCB** —— 它们是「可调上升时间 + 可调 QOD」型 (TPS22918 SOT-23-6, RON 52 mΩ @5V / 53 mΩ @3.3V, IQ 8.3 µA, 2A, −40~+105 °C; TPS22919 SC70-6, RON 89/90/105 mΩ, IQ 8 µA, ISD 2 nA, 1.5A, 带短路保护, −40~+125 °C) ⇒ **不要把它们当 RCB 备选** `[官网]`。
> ★**2026-11-17 04:5x 本轮独立复核 (TI 官网产品页实抓)**: TPS22991 Features 栏 = 「Inrush current control, Quick output discharge, Thermal shutdown」(★无 RCB 条目★) · TPS22916 Features 栏 = 「Always-ON true Reverse Current Blocking (RCB) / Activation current (IRCB): −500 mA (typ.) / Reverse leakage (IIN,RCB): −300 nA (max.)」 · TPS22917 Features 栏 = 同型 (反向漏 −1 µA max) · TPS22910A Features 栏 = 「Full-Time Reverse Current Protection」+ 描述栏「Reverse current protection is always active, even when the power-switch is disabled.」 · TPS22918 Features 栏 = 「Inrush current control, Quick output discharge」(★无 RCB★) · TPS22919 Features 栏 = 「Inrush current control, Quick output discharge, Short circuit protection, Thermal shutdown」(★无 RCB★) ⇒ ★**六款 TI 候选的 RCB 判定逐条被官网原文坐实, 零推断** `[官网]`。
> ★**⚠️ 官方手册内部措辞不一致 (如实记录, 不替厂家圆场)**: SGM2575S 手册 FEATURES 栏写「Reverse Current Protection When Disabled」(与 SGM2572 同措辞), 但 EC 表写「True Reverse Current Blocking」、APPLICATION INFORMATION 写「enabled whether the ON pin is high or low」、功能框图也画了 Reverse Current Blocking 模块 ⇒ ★**以三处一致为准 = True RCB (导通态也挡); FEATURES 那一行按厂家简写看待, 不作反向证据** `[官网]`。

### 3.2 为什么 RCB 对本板是**硬需求**而不是形式条款

- 关机插 USB 时: 充电板 PG 拉低 ⇒ **Q_PG_1 (P-MOS 高边, `HW/POWER_SHUTDOWN_V3.md` §3 V1.9 P0 修正)** 把负载开关 ON 脚拉到 BAT_SW ⇒ **负载开关被强制导通**。
- 此时 USB 的 5V 经 SoC 的 IO 脚灌到 SYS (= 负载开关 VOUT) ⇒ 因为开关处于**导通**态, 电流经 MOSFET 通道回到 VIN (BAT_SW) ⇒ **N 沟道体二极管只挡 VIN→VOUT 方向, 挡不住导通态的通道反灌** ⇒ 没有 RCB 就真的把电池反灌了 ⇒ 判据 5 的原文「关机插 USB 时 5V 会经 SoC 的 IO 脚反向灌进电池」在本板拓扑下**成立** `[推算]` (拓扑依据 HW §3; 方向依据 §2 判据 5 原文)。
- ★**U_EN_SW_1 不需要 RCB** (与 ISS-234 §3 N-1 的裁一致): 它的 EN 由 SoM 的 P3_87 驱动, 底板 5V 全部挂 RAIL_BOARD_5V (本身就在 U_EN_SW_1 之后) ⇒ 关断时底板无电, 不存在外部 5V 反灌回它的路径 `[推算]` (依据 `HW/netlist_v1.csv` L440-L444 + ISS-234 §3)。

### 3.3 结论 (机器可判): **没有「同封装 + 带 RCB」的在售型号**

- 就本次查证范围 (TI TPS229xx 单路族 91/16/17/18/19/10A + 圣邦微 SGM2572 / SGM2575S): 带 RCB 的 5 款封装分别是 DSBGA-4 YFP · SOT-23-6 DBV · DSBGA-4 YZV · WLCSP-0.8×0.8-4B · WLCSP-0.76×0.76-4B ⇒ **没有一款是现网表 footprint 的 UQFN-4 RAA (0.85 × 0.75, 0.4 mm pitch)** ⇒ ★**必须走降级方案**。
- ★**残留缺口 [0数据]**: TI 官网参数筛选器里「4 脚 UQFN-HR (RAA) 全系 + 带 RCB」的型号本轮**未逐项穷举** ⇒ 若老板要 100% 穷举, 需按官网 Load Switch 参数筛选器 (Package = UQFN-HR 4 / Reverse Current Protection = Yes) 过滤后逐个核数据手册 ⇒ **这是一条人工动作, 本单不做, 也不能靠推断代替**。

### 3.4 ★★2026-11-17 补证后的两条新事实 (★都在本轮实抓的官方手册里★)

- ★**事实 A — 三颗带 RCB 的候选共用同一套球编号, 且都不是网表的 1/2/3/4**:

  | 型号 | 官方手册 PIN CONFIGURATION (TOP VIEW) | 与网表 1=VIN/2=ON/3=VOUT/4=GND |
  |---|---|---|
  | TPS22916BYFPR (DSBGA-4 YFP) | A1 VOUT / A2 VIN / B1 GND / B2 ON | ★**不兼容** |
  | SGM2572ADYG/TR (WLCSP-0.8×0.8-4B) | A1 VOUT / A2 VIN / B1 GND / B2 ON | ★**不兼容** |
  | SGM2575SADYG/TR (WLCSP-0.76×0.76-4B) | A1 OUT / A2 IN / B1 GND / B2 ON | ★**不兼容** |

  ⇒ ★**改板价值**: ① 三颗 RCB 候选的**逻辑引脚排布完全一致** ⇒ 原理图符号可共用, 改板只需画一套「VOUT 在 A1 / VIN 在 A2」的 footprint 家族 (物理封装不同: BGA-4 bump / WLCSP-0.8 / WLCSP-0.76); ② ★**反过来看, 现网表的 UQFN-4 RAA (1=VIN/2=ON/3=VOUT/4=GND) 与三颗 RCB 候选没有任何一颗引脚对得上** ⇒ ★**改板不是「换个料」, 是「换引脚编号体系」⇒ 板那一趟必须重核每一根线** `[官网]` + `[推算]`。
- ★**事实 B — ★「唯一 RCB + RON ≤ 40 mΩ 双满足」只在 typ 口径成立, max 口径下没有任何一颗 RCB 候选过判据 3★**:

  | 型号 | RON typ | RON max | 对判据 3 (≤40 mΩ @3.7V) |
  |---|---|---|---|
  | TPS22991RAA (无 RCB) | 25 mΩ @5V | 本轮未取得 | typ ✔ |
  | TPS22916BYFPR (RCB) | 60 mΩ @5V | **100 mΩ @85 °C** | typ ✘ / max ✘ |
  | TPS22917xDBVR (RCB) | 80 mΩ @5V | 本轮未取得 | typ ✘ |
  | TPS22910AYZVR (RCB) | 60 mΩ @5V / 61 mΩ @3.3V | 本轮未取得 | typ ✘ |
  | SGM2572ADYG/TR (RCB 仅禁用态) | 34 mΩ | **60 mΩ** | typ ✔ / max ✘ |
  | **SGM2575SADYG/TR (True RCB)** | **30 mΩ** | **63 mΩ** | ★**typ ✔ / max ✘** |

  ⇒ ★**SGM2575S 仍是「唯一 typ 口径同时带 True RCB 且 RON ≤ 40 mΩ」的在售型号**, 但 ★**max 口径下 63 mΩ 超判据 3 门槛 57%** ⇒ **[推算] 压降**: 按网表 L37 的 SYS 最大 0.55 A 算, 63 mΩ ⇒ **34.7 mV**; 按 1 A 算 ⇒ **63 mV**; 按 2 A 算 ⇒ **126 mV** (SYS 下限 3.5 V, SoC UVLO 3.5 V) ⇒ ★**按本板真实工况 (0.55 A) 压降可接受; 按 2 A 满载口径不可接受** ⇒ 判据 2 与网表 L37 的口径冲突 (§1 末) 在这里变成了**可量化的分歧点**, 请老板与 main 一并裁。

---

## §4 建议 (按 A5 建议序打分 · ★不代拍★)

> 依据: `DECISION_PENDING_2026-11-16.md` §A5 给的建议序 = **① 反向阻断 > ② IQ<5µA > ③ RON 越小越好 > ④ 封装/面积**。★**本单只按这个序出推荐, 优先级序本身与型号的拍板 = 老板**。

| 候选 | ① RCB | ② IQ/关机漏电 | ③ RON (≤40mΩ@3.7V) | ④ 封装/面积 | 按 A5 序的推荐 |
|---|---|---|---|---|---|
| C1 TPS22991RAA | ✘ 无 | △ typ 14 nA ✔ / ★max 20 µA ✘ | ✔ 25 mΩ (最优) | ✔ 0.6375 mm² **+ 同封装 = 不改板** | **若 ④ 优先 ⇒ 推荐 (唯一不改板)**, RCB 缺口走 FB1 |
| C2 TPS22916BYFPR | ✔ Always-ON true | ✔ 10 nA typ / 100 nA max | ✘ 60 mΩ | ✔ 1 mm² (改板) | 若 ①+② 优先 ⇒ 推荐; 压降代价最大的一档 |
| C3 SGM2572ADYG/TR | ✔ (仅禁用态) | ✔ 90 nA typ / 440 nA max | ✔ 34 mΩ typ / ✘ 60 mΩ max | ✔ 0.64 mm² (改板) | 中庸档; ★禁用态阻断正好覆盖关机场景, 导通态不挡 |
| C4 TPS22917xDBVR | ✔ Always-ON true | ✔ 10 nA typ | ✘ 80 mΩ | ✘ 8.12 mm² (超判据 6) | 不推荐 (面积 + 压降双输) |
| C5 TPS22910AYZVR | ✔ Full-Time | ✔ 1.2 µA typ | ✘ 61 mΩ | ✔ 1.5625 mm² (改板) | 次选 (RCB 语义最强, 导通态也挡) |
| C6 SGM2575SADYG/TR | ✔ True RCB | ✔ 0.15 µA typ / 0.5 µA max | ✔ **30 mΩ typ (带 RCB 里最优)** / ✘ 63 mΩ max | ✔ **0.578 mm² (最小)** (改板) | **若 ① 排最前 ⇒ 推荐这个** (唯一 typ 口径 RCB + RON 双满足) |

★**四条给老板的落点**:
1. ★**A5 说的「判据互斥」在本次查证范围内不成立**: `TPS22916/17` 确实是「有 RCB 但 RON 60~80 mΩ」, 但 ★**国产 `SGM2575S` 把互斥打破了** (True RCB + 30 mΩ typ + 2A + 0.578 mm²) ⇒ 老板的优先级序可以变成「① 优先且不改 RON」⇒ 代价从「改板」+「压降变大」变成只有「改板 + 须核 4-ball 引脚定义」。
2. ★**唯一不用改板的是 TPS22991RAA, 但它有两处硬伤**: ① 无 RCB (关机插 USB 会反灌, §3.2 已证); ② 关断漏电 max 20 µA 超判据 4 (关机账 108 µA 的 18.5%)。
3. ★**2026-11-17 补证新增的第 3 条落点 — ★「唯一 RCB + RON 双满足」只在 typ 口径成立★**: SGM2575S 的官方 EC 表给出 **RDSON max = 63 mΩ** (SGM2572 是 60 mΩ) ⇒ ★**max 口径下没有任何一颗带 RCB 的在售型号能过判据 3 的 40 mΩ 门槛** ⇒ 请老板在拍优先级序时★**一并拍「RON 按 typ 还是按 max 判」** ⇒ [推算] 按本板真实工况 (网表 L37: SYS 最大 0.55 A) 算, 63 mΩ 的压降只有 **34.7 mV**; 按 1 A 算 63 mV; 按 2 A 算 126 mV ⇒ ★**「0.55 A 还是 2 A」这个口径分歧, 直接决定 RCB 候选能不能上**。
4. ★**本单不代拍优先级序, 也不代拍型号** ⇒ 请老板在 §A5 上给一句「① 优先 / ④ 优先 / ② 优先」, 本单的矩阵立刻能收敛成一个型号 + 一条降级路线。

---

## §5 降级方案 (2 条主方案 · 覆盖 brief 列出的四种情形)

> ★**机器基准块为什么只有 2 条**: 门禁 C5 的反向用例是「把降级方案砍到 1 条 ⇒ 红」⇒ 基准块取 **2 条** 才能自证; 每条内部含变体, 覆盖 brief 的 ①换封装 ②外部反灌保护 ③接受无 RCB 改拓扑/记缺口 ④换 SoM/电池方案。

### FB1 —— 不改板路线: 保留 TPS22991RAA + 外部反灌保护 / 改拓扑 / 记缺口

- **改了什么**
  - 变体 A: 在 **U_PWR_SW_1 的 VOUT(SYS) 与 SoC IO 之间**串 1 颗反向阻断元件 (肖特基 D 或 P-FET 理想二极管), 把 USB 5V 的反灌从 SoC IO 旁路掉 (注意: **不能**串在 SYS 主路上, 见代价栏)。
  - 变体 B (改拓扑): 取消 Q_PG_1 对 ON 脚「插电即开机」的强制拉高 ⇒ 关机插 USB 时负载开关保持禁用 ⇒ N 沟道体二极管天然阻断 VOUT→VIN ⇒ 代价是失去「插电即开机」。
  - 变体 C (接受无 RCB): 把缺口正式登记进 `HW/POWER_SHUTDOWN_V3.md` §2 与决策页 §A5, 并要求 hw-lead 在板级核实 SoC IO 脚的反灌是否被 SoC 内部保护钳位。
- **代价**: 面积 变体 A +1~3 mm² (镜脚板缺 300 mm² 的余量里可吸收), B/C = 0 · 压降 变体 A 肖特基 @0.55A 约 0.20~0.30 V ⇒ **若串在 SYS 主路上会吃掉 SYS 下限 3.5V 与 SoC UVLO 3.5V 的全部余量 ⇒ 只能串在 SoC IO 支路**; P-FET 理想二极管约 20~50 mV (Rds×I) · 静态功耗 变体 A 肖特基反向漏 1~10 µA (关机账 108 µA 的 +1~9%), 理想二极管控制器 5~20 µA (+5~19%) · 工艺 变体 A 加 1~2 颗件 + 改网表 (footprint 不动 ⇒ 不改板), 变体 B 动关机状态机与 Q_PG_1 选型 · 延期 变体 A/C = 0 板次, 变体 B 需重跑 `SW/tools/check_shutdown_semantics.py`。
- **适用条件**: 老板把 A5 的 ④ (封装/面积/**不改板**) 放在 ① (反向阻断) 之上, 或明确接受「关机插电期间电池被反灌」这条风险被登记并接受 ⇒ **这是「没有同封装且带 RCB 的在售型号」这一最坏情形的首选路线**。
- **依据**: `[推算]` 压降/漏电基于网表 L37 的 SYS 最大 0.55A 与 SYS 下限 3.5V / SoC UVLO 3.5V; `[推算]` 肖特基 Vf 与反向漏电取常见档位 (本轮未取具体料号数据手册 ⇒ 选型后必须按其数据手册复核); 拓扑依据 `HW/POWER_SHUTDOWN_V3.md` §3 (Q_PG_1 P-MOS 高边 + ON 脚 10k 下拉) 与 §2 判据 5; 缺口登记依据 ISS-234 交卷件 §3 Q2。

### FB2 —— 改板路线: 换成带 RCB 的在售型号

- **改了什么**: 换 U_PWR_SW_1 的封装与型号 ⇒ 首选 **SGM2575SADYG/TR** (True RCB · 30 mΩ typ / 63 mΩ max · 2A · 0.578 mm²), 次选 **TPS22910AYZVR** (Full-Time RCB · 61 mΩ @3.3V), 再次 **TPS22916BYFPR** (Always-ON true RCB · 60 mΩ @5V) 或 **TPS22917xDBVR** (RCB · 80 mΩ @5V · 但面积超判据 6) · 变体 D: 若 RCB 缺口被判为「由充电板/结构侧保证」(USB 5V 永不与 SYS 相连), 则整条改板路线可免, 直接落 TPS22991RAA · 变体 E: 极端方案 —— 换带理想二极管/电源路径管理的 SoM 或换电池供电方案 (把反灌问题挪到 SoM 侧解决)。
- **代价**: 面积 SGM2575S 0.578 mm² (比现 RAA 的 0.6375 mm² 还小一点) / TPS22910A 1.5625 mm² / TPS22916 1 mm² / TPS22917 8.12 mm² (超判据 6) · 工艺 ★**改板 = 改原理图 + 改 PCB footprint + 重跑 DRC/ERC + 重跑网表/脚表门禁 ⇒ 板那一趟必须排进计划** (ISS-172 落表后才能启动) · 延期 ★板改版 + 重新投板 + 重测, 按本项目节奏至少 1~2 个排期窗口; ★**2026-11-17 补证: SGM2575S / SGM2572 / TPS22916 三颗候选的官方引脚原表已全部取到 (见 §3.4 事实 A) ⇒ 原来那条「引脚定义 [0数据] ⇒ 改板前必须先核原表」的前置阻塞【已关闭】; 但新固化成一条必做动作: 三颗候选的球编号都是 A1=VOUT/A2=VIN/B1=GND/B2=ON, 与现网表 1=VIN/2=ON/3=VOUT/4=GND 【无一兼容】⇒ 板那一趟必须逐线重核, 不是换个料号了事** · 变体 E 代价最大 (SoM/电池方案重选 + 全部下游电源树重画), 不在本单范围。
- **适用条件**: 老板把 ① (反向阻断) 排在最前且接受改板 ⇒ 这是「把反灌硬约束做实」的唯一无缺口路线; 若同时要求 RON ≤ 40 mΩ, 则本次查证范围内只有 **SGM2575S** 同时满足。
- **依据**: `[官网]` / `[媒体]` 各型号的封装 / RCB / RON / IQ 数值见 §6 出处表; ★**2026-11-17: 圣邦微两颗候选已从 [媒体] (搜索引擎文本化 / 第三方镜像) 升级为 [官网] (官方 PDF 直取) ⇒ 全文已无 [媒体] 依赖** `[实测]` 现网表 footprint 与引脚定义来自 `HW/netlist_v1.csv` L50/L58; `[推算]` 排期代价按本项目板改版既有节奏估计 (本轮未取项目管理排期表), 具体天数由项目总工核。

---

## §6 出处表 (取数时间 ★第 1 轮 2026-11-16 11:47~11:52 GMT+8 + 第 3 轮补证 2026-11-17 04:52~04:57 GMT+8★ · 全部公开数据手册/官网)

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
| S11 | ★**圣邦微官方数据手册 (2026-11-17 直取, 非搜索引文) `https://www.sg-micro.com/rect/assets/a8959667-d386-4c95-a64d-205e9b7b4446/SGM2575S.PDF`** (PDF 779390 B · 7 页 · JULY 2025 – REV.A.1, SG Micro Corp; 标题 5.5V/2A/30 mΩ RDSON + Reverse Current Protection; ★**ABSOLUTE MAXIMUM RATINGS: VIN/VOUT/VON −0.3 V to 6 V · IMAX 2 A**; ★**PIN CONFIGURATION (TOP VIEW): A1 OUT / A2 IN / B1 GND / B2 ON**; ★**EC 表: RDSON 30 mΩ typ / ★63 mΩ max @5.5 V 与 @3.3 V, 48 mΩ @1.2 V; ISD 0.15 µA typ / 0.5 µA max (-40~85 °C) / 1.2 µA max (-40~125 °C); IQ 0.37 µA typ / 1.1 µA max @3.3 V; IRC 10 nA typ / 900 nA max; ION 10 nA typ / 900 nA max; RPD 230/300 Ω; RPD_ON 1 MΩ; ★**True Reverse Current Blocking VT_RCB typ 6 mV / min 24 / max 50 mV, 迟滞 30 mV**; VIH 0.71 V / VIL 0~0.3 V; UVLO 0.94/1.26 V; WLCSP-0.76×0.76-4B; θJA 221 ℃/W; 订购表 SGM2575SAYG/TR + SGM2575SADYG/TR, −40℃ to +125℃**) | 原厂官方数据手册 (★官方服务器直取 PDF + 本机 pdftotext 提取, 非搜索引擎引文★) | C6 全部 8 格 + 引脚定义 + RCB 判定 | [官网] |
| S12 | ★**圣邦微官方数据手册 (2026-11-17 直取) `https://www.sg-micro.com/rect/assets/2cfc9d3d-567e-4a1a-b62e-e71150753502/SGM2572.pdf`** (PDF 28 页 · MAY 2022, SG Micro Corp; ★**ABSOLUTE MAXIMUM RATINGS: VIN/VOUT/VON −0.3 V to 6 V · IMAX 2 A · IPLS 2.5 A (pulse <300 µs, 2% duty) · θJA 279 ℃/W**; ★**PIN CONFIGURATION (TOP VIEW): A1 VOUT / A2 VIN / B1 GND / B2 ON**, PIN DESCRIPTION 原文「B2 ON — Switch Control Input. Active high enables the device. Do not float this pin.」; ★**EC 表: RON 34 mΩ typ / ★60 mΩ max @5 V 与 @3.3 V; ISD 90 nA typ / 440 nA max; IQ 220 nA typ / 400 nA max @3.3 V; ILEAKAGE 450 nA max; ION 420 nA max; IRC 1 µA max; RPD 280/370 Ω; VIH 1.1 V / VIL 0~0.4 V**; ★**APPLICATION INFORMATION 原文「If the ON pin is pulled low, the device is disabled, while VIN > 1V or VOUT > 1V is met, the reverse current protection function is activated…」且全手册无 "True Reverse Current Blocking" / VT_RCB**; WLCSP-0.8×0.8-4B; 订购表 SGM2572AD/BD/CDYG/TR, −40℃ to +85℃**) | 原厂官方数据手册 (★官方服务器直取 PDF + 本机 pdftotext 提取★) | C3 全部 8 格 + 引脚定义 + RCB 判定 | [官网] |
| S13 | `HW/POWER_SHUTDOWN_V3.md` §2 (8 条判据原文 · 只读) + §3 (Q_PG_1 P-MOS 高边 / ON 脚 10k 下拉 / 真关机拓扑) + §6 (关机功耗预算 ~108 µA) | 项目内部文档 (只读) | §1 判据 · §3.2 拓扑依据 · §4 关机账占比 | [实测] (项目内部口径) |
| S14 | `HW/netlist_v1.csv` L37 (SYS 3.0–4.2V / 最大 0.55A / SYS 下限 3.5V / SoC UVLO 3.5V) · L50 (U_PWR_SW_1 本体行, value 栏 = `[待选型] 负载开关 (≥2A, R_on ≤40mΩ@3.7V, IQ ≤5µA, 带反向阻断)`, footprint = UQFN-4 RAA 0.85 x 0.75 mm 0.4 mm pitch, OPN = TPS22991RAA) · L56 (`R_PD_ON_1` 10k) · L58 (ON 节点) · L440–L444 (U_EN_SW_1 引脚与 CARRIER_BOARD_EN) | 网表 (只读) | §1 判据串对照 · §2 引脚一致性 · §3.2 · §5 代价推算 | [实测] |
| S15 | `SW/SHUTDOWN_SEMANTICS_SPEC.md` §3 (ISS-234 交卷: Q2 推荐 TPS22991RAA + 要求登记「无 RCB」缺口 + N-1「整机负载开关选型必须同时看 RON/IQ/RCB 三条」) + `DECISION_PENDING_2026-11-16.md` §A5 / §Q2 (拍板待办 + 建议优先级序) | 项目内部文档 (只读) | §0 摘要 · §3 缺口承接 · §4 打分依据 | [实测] (项目内部口径) |

> ★**证据等级统计 (2026-11-17 补证后)**: `[官网]` 占绝对主体 (TI 官网产品页 ×5 + TI 数据手册 ×3 + 圣邦微官网产品页 ×2 + ★**圣邦微官方数据手册 PDF 直取 ×2★) · ★**全文已无 [媒体] 依赖** (上一轮的 [媒体] 来自「搜索引擎文本化引文」与「原厂选型指南的第三方镜像」, 本轮全部换成官方服务器直取 PDF) · `[推算]` 只用于压降/漏电/关机账占比/排期代价的推导 · `[0数据]` 只剩两处 (TI 官网筛选器未穷举 UQFN-HR+RCB 全系 · TPS22917/TPS22910A 的 RON max 档未取得) · ★**实物 [实测] = 0 条**。

---

## §7 落表影响 (★本单不落表★)

| # | 落表时必须一起改的项 | 现状 | 归属 |
|---|---|---|---|
| L1 | `HW/netlist_v1.csv` L50 的 value 栏 `[待选型] 负载开关 (≥2A, R_on ≤40mΩ@3.7V, IQ ≤5µA, 带反向阻断)` ⇒ 换成老板拍定的型号 + 判据串 | ★**2026-11-16 22:25 已由 hw-lead 的 ISS-257 落表批次落成 `TPS22991RAA (负载开关 1=VIN/2=ON/3=VOUT/4=GND, UQFN-4 RAA · ≥2A · R_on 25mΩ@5V · 无 RCB ⇒ 选型口径待 A5 追认)` ⇒ 本单不需改, 但 ★**它落的是「不改板」分支, 「无 RCB」缺口仍在 ⇒ 仍等 §A5 追认** | 已落 (ISS-257) · 追认等老板 |
| L2 | 同行的 OPN 栏 `TPS22991RAA` ⇒ 补全变体字母 (B/BN/C/CN 之一, 影响 QOD 有无与上电斜率) | 本单只报 | 落表批次 |
| L3 | L442 `U_EN_SW_1` 的 value 栏 `TPS22991RAA (负载开关: 1=VIN/2=ON/3=VOUT/4=GND, UQFN-4 RAA 0.85 x 0.75 mm)` ⇒ 若整机型号改封装, 这颗也要一起改 | 本单只报 | 落表批次 |
| L4 | 若选带 RCB 的改板型号 ⇒ 原理图 + PCB footprint 一起改 (DSBGA-4 / WLCSP-4 ball 的焊盘编号与现 RAA 不同) | 本单只报 | hw-lead (板那一趟) |
| L5 | 判据 2 与网表 L37 的口径冲突 (2A vs 0.55A) ★**2026-11-17 补证后升级为量化分歧点**: max 口径下 RCB 候选全部不过判据 3 (SGM2575S 63 mΩ / SGM2572 60 mΩ), 而按 0.55 A 实工况压降只有 34.7 mV ⇒ ★**这一句直接决定 RCB 候选能不能上** | 本单只报 | 老板 / main 裁 |


> ★**§7 表下补记 (2026-11-17 第 2 轮)**: ★**L1 已由 ISS-257 (hw-lead) 落表** (value 栏 = `TPS22991RAA (负载开关 1=VIN/2=ON/3=VOUT/4=GND, UQFN-4 RAA · ≥2A · R_on 25mΩ@5V · 无 RCB ⇒ 选型口径待 A5 追认)`) ⇒ ★**不是本单落的, 本单一个字都没改网表**; ★**L2 (OPN 补变体字母) 仍开着** (落表串用的就是 `TPS22991RAA` 无变体后缀, 而 TI 有 B/BN/C/CN 四个变体: 上电上升时间 141 µs vs 662 µs, QOD 有无也不同 ⇒ 上电斜率与 QOD 行为仍**未锁**) ⇒ ★**L3 (L442 跟着改) 未触发** (本轮不改封装) ⇒ ★**L5 (判据 2 与 L37 的 2A vs 0.55A 口径冲突) 仍开着** ⇒ ★**落表后残留 3 条缺口 (G-1 / G-2 / G-3), 见 §9.2**。

---

## §8 自证复现命令

```bash
cd projects/smart_glasses
python3 SW/tools/check_load_switch_selection.py             # rc=0 = 证据矩阵门禁全过
python3 SW/tools/check_load_switch_selection.py --selftest   # rc=0 = 12/12 反向用例全红 (M1~M8 第1轮 + M9~M12 第2轮)
python3 SW/tools/check_load_switch_selection.py --sandbox    # rc=0 = 4/4 ★真改网表★的反向自证 (C9 抓的是网表那一侧)
python3 SW/tools/check_shutdown_semantics.py                 # rc=0 (ISS-234 的闸, 本单不许打红)
python3 state/merge.py && python3 state/gate_check.py         # rc=0, Q1 18/18
```


## §9 第 2 轮 (2026-11-17) 落表后回归 —— 快照重锚 + C9 门禁

### 9.1 落表后网表现状 (2026-11-17 实读 · [实测])

| 位置 | 落表前 (第 1 轮快照) | 落表后 (现行真值) | 归属 |
|---|---|---|---|
| `HW/netlist_v1.csv` L50 value 栏 | `[待选型] 负载开关 (≥2A, R_on ≤40mΩ@3.7V, IQ ≤5µA, 带反向阻断)` | `TPS22991RAA (负载开关 1=VIN/2=ON/3=VOUT/4=GND, UQFN-4 RAA · ≥2A · R_on 25mΩ@5V · 无 RCB ⇒ 选型口径待 A5 追认)` | ISS-257 (hw-lead) |
| 同行证据等级栏 | `[推算]` | `[官方]` | ISS-257 (hw-lead) |
| 同行 OPN 栏 | `TPS22991RAA` | `TPS22991RAA` (**一字未改**) | 本来就在 |
| 同行 footprint 栏 | `UQFN-4 RAA, 0.85 x 0.75 mm, 0.4 mm pitch` | **一字未改** | 本来就在 |
| L442 (`U_EN_SW_1`) value 栏 | `TPS22991RAA (负载开关: 1=VIN/2=ON/3=VOUT/4=GND, UQFN-4 RAA 0.85 x 0.75 mm)` | **一字未改** | —— |
| 现行网表 md5 | `34132f7e…` (第 1 轮交卷时) | `e06c1dd633566aa44732762c2ff99d1c` | ISS-249 / 257 / 262 / 268 (hw-lead) |

> ★**md5 漂移归属**: 网表 / 脚表 / BOM 三个 md5 自第 1 轮交卷后变了 ⇒ ★**全部是 hw-lead 的落表批次 (ISS-249 / ISS-257 / ISS-262 / ISS-268) 干的, 不是本单** ⇒ 本单对 `HW/` 的写入量 = **0 字节** (只读)。板 md5 `611b869e…` 自始至终一字未改。

### 9.2 落表后残留缺口 (3 条 · 本单只登记, 不落表)

| # | 缺口 | 为什么算缺口 | 归属 |
|---|---|---|---|
| G-1 | L50 note 栏仍写「型号待选型, 询价经项目总工」 | ★**同一行的 value 栏已经落成型号串了** ⇒ 一个说"还没选", 一个说"选好了" ⇒ 同一个器件本体行自相矛盾 | 落表批次 |
| G-2 | L50 note 栏仍写「**反向阻断必查** (关机插 USB 时防 5V 经 SoC IO 反灌电池)」 | ★**同一行的 value 栏写着「无 RCB」** ⇒ 「必查」与「无」并存 ⇒ 这颗器件到底带不带反向阻断, 网表自相矛盾 ⇒ ★**这正是本单 §3 要做实的那个缺口, 现在它被写进网表自己身上了** | 落表批次 |
| G-3 | L442 (`U_EN_SW_1`) note 栏仍写「ISS-172 待老板点头」 | ISS-172 已交卷 ⇒ 实际只剩「A5 优先级序」这一句 ⇒ 状态词过期 | main / 落表批次 |

★**这 3 条本单一条都不改** ⇒ ★**理由 = 本单边界是「不落表」**; ★**改法归属已登记在基准块顶层 `residual_gaps` (机器可读) + §9.2 (人读) ⇒ ★**门禁 C9(f) 强制这份登记不许为空** ⇒ ★**落表批次可以把网表改了, 但不许把「残留缺口登记」删掉**。

### 9.3 门禁第 2 轮加的 C9 (落表后回归)

★**第 1 轮的洞 (实测)**: C6 只校验「基准块里的**快照**」与矩阵判据对不对得上 ⇒ ★**网表被落表批次改了以后, 快照并不会自己跟着变** ⇒ C6 拿着一份已经过期的快照照样绿 ⇒ ★**「不许矩阵与判据串各说各话」在落表之后就失效了**。

★**C9 的 6 条子判据 (全部机械可判)**:

| # | 子判据 | 红了意味着 |
|---|---|---|
| a | 基准块 `netlist_value_snapshot` 必须**等于现行网表** U_PWR_SW_1 本体行的 value 栏 (归一化比较) | 网表又变了 / 快照没重锚 ⇒ 矩阵对网表的陈述已过期 |
| b | `netlist_drift` 必须存在且 `landed_by` / `landed_at` / `reason` / `pre_drift_snapshot` / `post_drift_snapshot` 五个字段非空 | 落表漂移没登记来源 ⇒ 无法追责 |
| c | `netlist_drift.pre_drift_snapshot` 必须等于顶层 `netlist_value_pre_drift`; `post_drift_snapshot` 必须等于 `netlist_value_snapshot` | drift 记录与快照自相矛盾 |
| d | 落表前后串**不一样**时 ⇒ `netlist_drift.dropped_requirements` 必须非空 | 落表悄悄丢了判据却没人登记 |
| e | 现行网表 value **提到 RCB** 时 ⇒ 落地型号必须在候选册里 + 它的 RCB 判定必须与网表口径一致 (网表说「无 RCB」⇒ 矩阵必须判「无」) + 矩阵判据必须覆盖「反向阻断」 | ★**网表说无, 矩阵说有 ⇒ 各说各话 (本轮要堵的就是这个)** |
| f | 顶层 `residual_gaps` 必须非空 | 落表后的残留缺口没登记 |

★**为什么 C9 不违反「不挂 md5」那条铁律**: C9 锚的是**内容** (value 栏字符串), 不是 md5 ⇒ ★**网表落别的批次 (改别的行) 不影响 C9; 只有 U_PWR_SW_1 本体行的 value 栏再变一次, C9 才会红** ⇒ ★**红了就是"该重锚了", 不是"网表动了"** ⇒ ★**重锚成本 = 改基准块 1 处 + 登记 drift 1 条**。

### 9.4 第 2 轮新增的反向用例 (M9~M12)

| 用例 | 变异 | 期望红 |
|---|---|---|
| M9 | 把基准块 `netlist_value_snapshot` 改回落表前的旧串 (模拟"落表了没重锚") | C9 |
| M10 | 把落地型号 `TPS22991RAA` 的 RCB 判定从「无」改成「有」 (模拟"网表说无, 矩阵说有") | C9 |
| M11 | 删掉整个 `netlist_drift` 块 (模拟"漂移不登记") | C9 |
| M12 | 清空 `residual_gaps` (模拟"残留缺口不登记") | C9 |

★**每条都自证「它真的改到了目标」**: 变异函数改不动就报「变异函数没有改到任何东西」⇒ 算失败; 变异后必须**指定的那一条**红 ⇒ 否则算失败; ★**且要落盘回读再跑一遍** (ISS-227 同款教训)。

★**但 M1~M12 只改【文档副本】⇒ 它们证明不了「网表真的变了门禁会红」—— 而 C9 的全部意义就在网表变的那一侧** ⇒ ★**第 2 轮另加 `--sandbox` 模式: 在 /tmp 临时树上真的改网表, 再跑真脚本** (★真盘 0 字节写入★):

| 用例 | 真改网表的哪一处 | 期望 |
|---|---|---|
| ① | `U_PWR_SW_1` 本体行的 value 栏 (落表批次再落一次) | 红 (C9 + C6) |
| ② | 同行的「无 RCB」翻成「带 RCB」 | 红 (C9) |
| ③ | 同行换成候选册里没有的型号 | 红 (C9 + C6) |
| ④ | ★**网表别的行** (落别的批次, 与本单无关) | ★**必须绿 (不许误伤)** |

★**④ 是关键**: 它证明 C9 锚的是**内容**不是 md5 ⇒ 别人落别的批次不会把我的门禁打红; ★**而①~③ 证明 C9 抓的确实是网表那一侧** ⇒ ★**两条合起来 = 「谁动 U_PWR_SW_1 的 value 栏谁必须来重锚」**。


<!-- BEGIN 选型证据基准块 -->
```json
{
  "meta": {
    "issue": "ISS-172",
    "doc": "SW/LOAD_SWITCH_SELECTION_FACTS.md",
    "author": "sw-lead",
    "date": "2026-11-16",
    "evidence_policy": "老板 2026-11-12 02:02 不再发信 · 全靠自己查资料 · 证据等级只取 [官网]/[实测]/[媒体]/[推算]/[0数据]",
    "boundary": "只交证据 · 不落表 · ★第 2 轮 (2026-11-17): 落表已由 ISS-257 发生 (不是本单落的), 本单仍不落表, 只重锚快照 + 加 C9 落表后回归门禁",
    "scope_note": "机器基准块 candidates 册取 3 个 (门禁 C1 的反向用例设计为「把候选砍到 2 个 ⇒ 红」⇒ 基准册必须正好 3 个才能自证); 其余 3 个同族/国产候选以 alternates 数组并列 (同样 8 条判据逐格填满), 正文 §2 矩阵共 6 个型号全部逐格填满",
    "round2_date": "2026-11-17",
    "round2_note": "★第 2 轮 = 落表后回归: ISS-257 已把网表 L50 的 [待选型] 串落成型号串 ⇒ 派单前提过期 ⇒ 本轮只做 [基准块快照重锚 + drift 登记 + 门禁加 C9], ★8 条判据的逐格评定与 §4 推荐一字未改",
    "round3_date": "2026-11-17",
    "round3_note": "★第 3 轮 = 补证轮 (2026-11-17 04:5x): 圣邦微两颗候选 (SGM2572 / SGM2575S) 的官方数据手册 PDF 已从官方服务器直取 ⇒ 证据等级全部从 [媒体] 升级为 [官网] (全文已无 [媒体] 依赖) + 关闭两个 [0数据] 格 (绝对最大额定 VIN -0.3~6V => 判据 1 满足; 4-ball 引脚原表) + 新查出 SGM2575S RON max = 63 mΩ (SGM2572 = 60 mΩ) ⇒ 『唯一 RCB + RON 双满足』只在 typ 口径成立 ⇒ ★本轮只改这些格子的证据与文字, ★8 条判据的逐格评定结论 / RCB 专项结论 / §4 推荐 / 2 条降级方案的结构 一字未改; ★机器基准块本轮同步订正了 FB2.cost / FB2.condition / FB2.basis / conclusion.recommendation_by_a5_order 四处仍写着『引脚定义 [0数据] 须核原表』的过期文字 (正文 §5 已在第 3 轮改正, 基准块本轮跟上) ⇒ ★矩阵与基准块不再各说各话"
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
      "change": "不改板路线: 保留 TPS22991RAA (UQFN-4 RAA · 同封装换料不换板) + 在反灌通路上补外部阻断 —— 变体 A: 在 U_PWR_SW_1 的 VOUT(SYS) 与 SoC IO 之间串 1 颗反向阻断元件 (肖特基 D 或 P-FET 理想二极管), 把 5V 反灌从 SoC IO 旁路掉; 变体 B: 改拓扑 —— 取消 Q_PG_1 (P-MOS 高边) 对负载开关 ON 脚的『插电即开机』强制拉高, 使关机插 USB 时开关始终保持禁用 (N-MOS 体二极管天然阻断 VOUT->VIN), 代价是失去『插电即开机』; 变体 C: 接受无 RCB, 把缺口登记进 HW/POWER_SHUTDOWN_V3.md §2 与决策页 §A5, 并要求 hw-lead 在板级核实 SoC IO 脚反灌电流是否被 SoC 内部保护钳位",
      "cost": "面积: 变体 A 加 1 颗二极管/MOS + 1~2 颗电阻 (估 1~3 mm², 镜脚板缺 300 mm² 的余量里可吸收); 变体 B/C 面积 0。压降: 变体 A 肖特基 @0.55A 约 0.20~0.30V (Vf typ 0.35~0.55V @0.55A) —— 若串在 SYS 主路上会直接吃掉 SYS 下限 3.5V 与 SoC UVLO 3.5V 的全部余量 ⇒ 只能串在 SoC IO 支路 (不承载 SYS 主电流); P-FET 理想二极管方案压降约 20~50mV (Rds x I)。静态功耗: 肖特基反向漏 1~10 µA (加到关机账 108 µA 上 ⇒ +1~9%); 理想二极管控制器静态 5~20 µA (+5~19%)。工艺: 变体 A 需加 1~2 颗件 + 改原理图与网表 (仍不改板 footprint); 变体 B 要动关机状态机与 Q_PG_1 选型。延期: 变体 A/C 0 板次; 变体 B 需重跑关机语义门禁 (SW/tools/check_shutdown_semantics.py)",
      "condition": "适用条件: 老板把 A5 建议序的第 ④ 条 (封装/面积/不改板) 放在第 ① 条 (反向阻断) 之上, 或明确接受『关机插电期间电池不被反灌』这条风险被文档登记并接受 ⇒ 这是『没有同封装且带 RCB 的在售型号』这一最坏情形下的首选路线",
      "basis": "[推算] 压降/漏电基于网表 L37 的 SYS 最大 0.55A (330 mA x 1.5 + 瞬态) 与 SYS 下限 3.5V / SoC UVLO 3.5V (同 L37 note, R-F1 裁决); [推算] 肖特基 Vf 与反向漏电取常见档位, 本轮未取具体料号数据手册 ⇒ 选具体器件后必须按其数据手册复核; 拓扑依据 HW/POWER_SHUTDOWN_V3.md §3 (Q_PG_1 P-MOS 高边 · 插电即开机路径 · ON 脚 10k 下拉默认关) 与 §2 判据 5 (关机插 USB 时 5V 经 SoC IO 反灌电池); 缺口登记依据 ISS-234 交卷件 SW/SHUTDOWN_SEMANTICS_SPEC.md §3 Q2 (Q2 推荐 TPS22991RAA + 要求登记无 RCB 缺口)"
    },
    {
      "id": "FB2",
      "change": "改板路线: 换掉 U_PWR_SW_1 的封装与型号, 选原厂在售且带反向阻断的型号 —— 首选 SGM2575S (圣邦微 WLCSP-0.76x0.76-4B · True RCB · 30 mΩ · 2A), 次选 TPS22910AYZVR (TI DSBGA-4 YZV 0.9x0.9 WCSP · Full-Time RCB · 61 mΩ @3.3V), 再次 TPS22916BYFPR (TI DSBGA-4 YFP 1 mm² · Always-ON true RCB · 60 mΩ @5V) 或 TPS22917xDBVR (TI SOT-23-6 · RCB · 80 mΩ @5V); 变体 D: 若 RCB 缺口在本项目被判为『由结构/充电板侧保证』(例如 USB 5V 永不与 SYS 相连), 则整条改板路线可免, 直接落 TPS22991RAA; 变体 E: 极端方案 —— 改用带理想二极管/电源路径管理的 SoM 或换电池供电方案 (把反灌问题挪到 SoM 侧解决)",
      "cost": "面积: SGM2575S 0.76x0.76 = 0.578 mm² (比现 UQFN-4 RAA 的 0.6375 mm² 略小); TPS22910A 1.5625 mm²; TPS22916 1 mm²; TPS22917 SOT-23-6 8.12 mm² (超判据 6 的 2x2 mm²)。工艺: 改板 = 改原理图 + 改 PCB footprint + 重跑 DRC/ERC + 重跑网表/脚表门禁 ⇒ 板那一趟必须排进计划 (ISS-172 落表后才能启动)。延期: 板改版 + 重新投板 + 重测, 按本项目节奏至少 1~2 个排期窗口; ★2026-11-17 补证: SGM2575S / SGM2572 / TPS22916 三颗候选的官方引脚原表已全部取到 (SGM2575S: A1 OUT / A2 IN / B1 GND / B2 ON; SGM2572 与 TPS22916: A1 VOUT / A2 VIN / B1 GND / B2 ON) ⇒ ★原来那条『引脚定义 [0数据] ⇒ 改板前必须先核原表』的前置阻塞【已关闭】; ★但新固化成一条必做动作: 三颗候选的球编号与现网表 1=VIN/2=ON/3=VOUT/4=GND 无一兼容 ⇒ 板那一趟必须逐线重核, 不是换个料号了事; ★另: SGM2575S 的 RON max = 63 mΩ (SGM2572 = 60 mΩ) ⇒ max 口径下没有任何一颗带 RCB 的在售型号能过判据 3 的 40 mΩ 门槛 ⇒ 选型前必须先拍『RON 按 typ 还是 max 判』。变体 E 代价最大: SoM/电池方案重选 + 全部下游电源树重画, 不在本单范围",
      "condition": "适用条件: 老板把 A5 建议序的第 ① 条 (反向阻断) 排在最前, 且接受改板一次 ⇒ 这是『把反灌硬约束做实』的唯一无缺口路线; 若同时要求 RON <= 40 mΩ, 则只有 SGM2575S (30 mΩ typ / ★63 mΩ max) 在本次查证范围内同时满足 RCB 与 RON —— ★但这只在 typ 口径成立; 按 max 口径 (63 mΩ > 40 mΩ) 没有任何一颗带 RCB 的在售型号能过判据 3 ⇒ 选型前必须先拍『RON 按 typ 还是 max 判』+『SYS 电流按 0.55 A 还是 2 A 算』",
      "basis": "[官网] 封装/RCB/RON/IQ 数值来自各原厂官网产品页与数据手册 (见 §6 出处表); [实测] 现网表 footprint 与引脚定义来自 HW/netlist_v1.csv L50/L58 (UQFN-4 RAA, 0.85 x 0.75 mm, 0.4 mm pitch · 1=VIN/2=ON/3=VOUT/4=GND); [推算] 排期代价按本项目板改版既有节奏估计 (本轮未取项目管理排期表), 具体天数由项目总工核; ★[官网] 2026-11-17 补证 (圣邦微官方数据手册 PDF 直取, 见 §6 出处表 S11/S12): SGM2575S EC 表 RDSON 30 mΩ typ / ★63 mΩ max @5.5 V 与 @3.3 V + True Reverse Current Blocking (VT_RCB typ 6 mV / min 24 / max 50 mV) + PIN CONFIGURATION A1 OUT / A2 IN / B1 GND / B2 ON + ABSOLUTE MAXIMUM VIN/VOUT/VON −0.3~6 V / IMAX 2 A; SGM2572 EC 表 RON 34 mΩ typ / 60 mΩ max + 禁用态反向电流保护 (全手册无 True RCB / VT_RCB) + PIN CONFIGURATION A1 VOUT / A2 VIN / B1 GND / B2 ON"
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
          "value": "ON = pin2, 数据手册引脚功能表原文 Active high switch control input => 高有效, 与网表 (SoC GPIO 拉高 = 开机, R_PD_ON_1 10k 下拉 = 默认关) 一致; 芯片内部 ON 脚智能下拉阻值本轮未在官网文本中取得 => 内部下拉按 [0数据] 记, 但本设计不依赖它 (外部 10k 下拉已在网表), 故默认态确定; 无 power-off latch / OFF-after-delay 型号 => 关断状态靠外部下拉保持",
          "source": "TI 数据手册 SLVSFK0B §5 Pin Functions 表 5-1 (VIN 1 / ON 2 Active high / VOUT 3 / GND 4) + 网表 HW/netlist_v1.csv L56 (R_PD_ON_1 10k) 与 L58",
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
      "package": "WLCSP-0.8 x 0.8-4B (4 ball, 绿色封装) —— 不是 UQFN-4 RAA => 换封装 => 必须改板; 官网订购信息栏标『量产』, 三个 OPN: SGM2572ADYG/TR (上升 85 us) / SGM2572BDYG/TR (1600 us) / SGM2572CDYG/TR (2200 us); ★官方手册 PIN CONFIGURATION (TOP VIEW) = A1 VOUT / A2 VIN / B1 GND / B2 ON => 与网表 1=VIN/2=ON/3=VOUT/4=GND 不兼容",
      "cells": {
        "1": {
          "value": "★绝对最大额定 (官方数据手册 ABSOLUTE MAXIMUM RATINGS 表): Input Voltage Range VIN = -0.3 V to 6 V / Output Voltage Range VOUT = -0.3 V to 6 V / ON Pin Voltage Range VON = -0.3 V to 6 V; RECOMMENDED OPERATING CONDITIONS: Input Voltage Range VIN = 1 V to 5.5 V => 判据 1 (VIN 绝对额定 >= 5V) 满足 (6 V > 5 V)",
          "source": "圣邦微官方数据手册 https://www.sg-micro.com/rect/assets/2cfc9d3d-567e-4a1a-b62e-e71150753502/SGM2572.pdf (MAY 2022, SG Micro Corp) §ABSOLUTE MAXIMUM RATINGS + §RECOMMENDED OPERATING CONDITIONS —— ★2026-11-17 由官方服务器直取 PDF (非搜索引擎引文)",
          "evidence": "[官网]"
        },
        "2": {
          "value": "Maximum Continuous Switch Current, IMAX = 2 A (ABSOLUTE MAXIMUM RATINGS 表); Maximum Pulsed Switch Current IPLS = 2.5 A (pulse < 300 us, 2% duty cycle) => 判据 2 (Iout >= 2A) 正好卡在门槛, 无余量",
          "source": "圣邦微官方数据手册 SGM2572.pdf (MAY 2022) §ABSOLUTE MAXIMUM RATINGS (Maximum Continuous Switch Current IMAX / Maximum Pulsed Switch Current IPLS 行) + §ELECTRICAL CHARACTERISTICS 表头 (Full = -40℃ to +85℃)",
          "evidence": "[官网]"
        },
        "3": {
          "value": "RON = 34 mΩ typ / ★60 mΩ max (VIN = 5V, VON = 1.2V, IOUT = -200mA); RON = 34 mΩ typ / 60 mΩ max (VIN = 3.3V); ★官方 EC 表只有 5V 与 3.3V 两档 => 3.7 V 档按 typ 约 34 mΩ => ★判据 3 (<= 40 mΩ @3.7V, 目标 <= 30 mΩ) 按 typ 满足, ★按 max 不满足 (60 mΩ > 40 mΩ, 超 50%); 压降 @1A = 34 mV typ / 60 mV max",
          "source": "圣邦微官方数据手册 SGM2572.pdf (MAY 2022) §ELECTRICAL CHARACTERISTICS 表 On-Resistance (RON) 两行 (VIN = 5V 与 VIN = 3.3V, VON = 1.2V, IOUT = -200mA, MIN/TYP/MAX 列)",
          "evidence": "[官网]"
        },
        "4": {
          "value": "★官方 EC 表: Shutdown Current ISD = 90 nA typ / 440 nA max (VIN = 5.5V, VON = 0V); Quiescent Current IQ = 220 nA typ / 400 nA max (VIN = 3.3V) / 320 nA typ / 560 nA max (VIN = 5V) / 140 nA typ / 300 nA max (VIN = 1V); Supply Leakage Current in Shutdown Mode ILEAKAGE = 450 nA max; ON Pin Leakage Current ION = 420 nA max => 判据 4 (关机漏电 IQ <= 5 uA) typ 与 max 双双满足 (440 nA = 关机账 108 uA 的 0.4%)",
          "source": "圣邦微官方数据手册 SGM2572.pdf (MAY 2022) §ELECTRICAL CHARACTERISTICS 表 (Quiescent Current IQ / Shutdown Current ISD / Supply Leakage Current in Shutdown Mode ILEAKAGE / ON Pin Leakage Current ION 行) + §FEATURES 栏 (低关断电流 90nA 典型值)",
          "evidence": "[官网]"
        },
        "5": {
          "value": "有 RCB —— ★官方数据手册 APPLICATION INFORMATION 原文: \"If the ON pin is pulled low, the device is disabled, while VIN > 1V or VOUT > 1V is met, the reverse current protection function is activated. This function prevents the current flowing from VOUT to VIN…\" ★且全手册无 \"True Reverse Current Blocking\" 字样、无 VT_RCB 行 => 官方坐实『仅禁用态』; 对本板『关机插 USB』(开关处于禁用态) 场景是覆盖的, ★但开关导通时的反灌仍会通过通道发生, 缺口说明必须写清这一点",
          "source": "圣邦微官方数据手册 https://www.sg-micro.com/rect/assets/2cfc9d3d-567e-4a1a-b62e-e71150753502/SGM2572.pdf §APPLICATION INFORMATION (Reverse Current Protection 段) + §ELECTRICAL CHARACTERISTICS 表 (Reverse Current When Disabled IRC 行) + §FEATURES 栏 (Reverse Current Protection When Disabled)",
          "evidence": "[官网]"
        },
        "6": {
          "value": "封装 WLCSP-0.8 x 0.8 mm = 0.64 mm² (官网特性栏与订购信息栏; 官方手册 PACKAGE/ORDERING INFORMATION 表同) => 判据 6 (面积 <= 2 x 2 mm) 满足, 与现 UQFN-4 RAA 的 0.6375 mm² 基本同面积 (但不是同一个封装, 不能直接换料); 官方热阻 WLCSP-0.8×0.8-4B θJA = 279 ℃/W",
          "source": "圣邦微官网产品页 https://www.sg-micro.com/cn/product/SGM2572 (特性栏 + 订购信息栏 Package 列) + 圣邦微官方数据手册 SGM2572.pdf §ABSOLUTE MAXIMUM RATINGS (Package Thermal Resistance 行)",
          "evidence": "[官网]"
        },
        "7": {
          "value": "★官方 PACKAGE/ORDERING INFORMATION 表 SPECIFIED TEMPERATURE RANGE = -40℃ to +85℃ (三个 OPN 同) => 判据 7 (-40 ~ +85 °C) 满足",
          "source": "圣邦微官方数据手册 SGM2572.pdf (MAY 2022) §PACKAGE/ORDERING INFORMATION 表 (MODEL / PACKAGE DESCRIPTION / SPECIFIED TEMPERATURE RANGE 列) + 官网订购信息栏 Operating Temperature Range",
          "evidence": "[官网]"
        },
        "8": {
          "value": "★官方 RECOMMENDED OPERATING CONDITIONS: ON Pin Input High Voltage VIH = 1.1V to 5.5V (min 1.1V) / ON Pin Input Low Voltage VIL = 0V to 0.4V; EC 表 VIH 1.1V / VIL 0.4V => 3.3V GPIO 可直接驱动 => 判据 8 满足; 官网特性栏另有『低阈值 1.8V GPIO 控制输入』; ★官方手册 PIN DESCRIPTION 原文『B2 ON — Switch Control Input. Active high enables the device. Do not float this pin.』=> 默认态需外部 10k 下拉保证 (网表 L56 R_PD_ON_1 已在); 无 power-off latch",
          "source": "圣邦微官方数据手册 SGM2572.pdf (MAY 2022) §RECOMMENDED OPERATING CONDITIONS (ON Pin Input High Voltage / ON Pin Input Low Voltage 行) + §ELECTRICAL CHARACTERISTICS 表 + §PIN DESCRIPTION 表 + 官网产品页特性栏 (低阈值 1.8V GPIO 控制输入) + 网表 HW/netlist_v1.csv L56 (R_PD_ON_1 10k)",
          "evidence": "[官网]"
        }
      },
      "rcb": {
        "verdict": "有",
        "quote": "If the ON pin is pulled low, the device is disabled, while VIN > 1V or VOUT > 1V is met, the reverse current protection function is activated. This function prevents the current flowing from VOUT to VIN, and is very useful when SGM2572 is disabled and the output needs to be driven by another voltage source. (官方数据手册 APPLICATION INFORMATION 原文照抄; ★全手册无 \"True Reverse Current Blocking\" / VT_RCB => 官方坐实『仅禁用态』, 不是 always-ON)",
        "source": "圣邦微官方数据手册 https://www.sg-micro.com/rect/assets/2cfc9d3d-567e-4a1a-b62e-e71150753502/SGM2572.pdf (MAY 2022, SG Micro Corp) §APPLICATION INFORMATION (Reverse Current Protection 段) + §ELECTRICAL CHARACTERISTICS 表 (Reverse Current When Disabled IRC 行)",
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
      "package": "WLCSP-0.76 x 0.76-4B (4 ball, 绿色封装) => 0.578 mm², 比现 UQFN-4 RAA 的 0.6375 mm² 还小一点, 但封装不同 => 必须改板; 数据手册标题即 5.5V, 2A, 30 mΩ RDSON Load Switch with Reverse Current Protection; ★官方手册 PIN CONFIGURATION (TOP VIEW) = A1 OUT / A2 IN / B1 GND / B2 ON => 与网表 1=VIN/2=ON/3=VOUT/4=GND 不兼容",
      "cells": {
        "1": {
          "value": "★绝对最大额定 (官方数据手册 ABSOLUTE MAXIMUM RATINGS 表): Input Voltage Range VIN = -0.3 V to 6 V / Output Voltage Range VOUT = -0.3 V to 6 V / ON Pin Voltage Range VON = -0.3 V to 6 V; RECOMMENDED OPERATING CONDITIONS: Input Voltage Range VIN = 1.2V to 5.5V => 判据 1 (VIN 绝对额定 >= 5V) 满足 (6 V > 5 V)",
          "source": "圣邦微官方数据手册 https://www.sg-micro.com/rect/assets/a8959667-d386-4c95-a64d-205e9b7b4446/SGM2575S.PDF (JULY 2025 - REV.A.1, SG Micro Corp) §ABSOLUTE MAXIMUM RATINGS + §RECOMMENDED OPERATING CONDITIONS —— ★2026-11-17 由官方服务器直取 PDF (非搜索引擎引文)",
          "evidence": "[官网]"
        },
        "2": {
          "value": "Maximum Continuous Switch Current, IMAX = 2 A (ABSOLUTE MAXIMUM RATINGS 表); FEATURES 栏 Maximum Continuous Current: 2A => 判据 2 (Iout >= 2A) 卡在门槛",
          "source": "圣邦微官方数据手册 SGM2575S.PDF (JULY 2025 - REV.A.1) §ABSOLUTE MAXIMUM RATINGS (Maximum Continuous Switch Current IMAX 行) + §FEATURES 栏",
          "evidence": "[官网]"
        },
        "3": {
          "value": "★官方 EC 表 On-Resistance RDSON: VIN = 5.5V, VON = 1.2V, IOUT = -200mA => typ 30 mΩ / ★max 63 mΩ; VIN = 3.3V 同 => typ 30 mΩ / max 63 mΩ; VIN = 1.2V => typ 48 mΩ => 3.7 V 档 typ 约 30 mΩ => ★判据 3 (<= 40 mΩ @3.7V, 目标 <= 30 mΩ) 按 typ 满足 (★查证范围内唯一 typ 口径同时带 True RCB 且 RON <= 40 mΩ 的在售型号), ★但按 max 不满足 (63 mΩ > 40 mΩ, 超 57%); [推算] 压降 @0.55A (网表 L37 SYS 最大) = 34.7 mV / @1A = 63 mV / @2A = 126 mV",
          "source": "圣邦微官方数据手册 SGM2575S.PDF (JULY 2025 - REV.A.1) §ELECTRICAL CHARACTERISTICS 表 On-Resistance (RDSON) 三行 (VIN = 5.5V / 3.3V / 1.2V, VON = 1.2V, IOUT = -200mA, MIN/TYP/MAX 列)",
          "evidence": "[官网]"
        },
        "4": {
          "value": "★官方 EC 表: Shutdown Current ISD (VIN = 5.5V, VON = 0V) TJ = -40℃ to +85℃ => typ 0.15 µA / ★max 0.5 µA; TJ = -40℃ to +125℃ => typ 0.15 µA / max 1.2 µA; Supply Leakage Current in Shutdown Mode ILEAKAGE 同档; Quiescent Current IQ (VIN = 3.3V) => typ 0.37 µA / max 1.1 µA, (VIN = 5.5V) => typ 0.57 µA / max 1.5 µA; ON Pin Leakage Current ION = 10 nA typ / 900 nA max; Reverse Current When Disabled IRC = 10 nA typ / 900 nA max => 判据 4 (关机漏电 IQ <= 5 uA) typ 与 max 双双满足 (0.5 µA max)",
          "source": "圣邦微官方数据手册 SGM2575S.PDF (JULY 2025 - REV.A.1) §ELECTRICAL CHARACTERISTICS 表 (Shutdown Current ISD / Supply Leakage Current in Shutdown Mode ILEAKAGE / Quiescent Current IQ / ON Pin Leakage Current ION / Reverse Current When Disabled IRC 行) + §FEATURES 栏 (Low Shutdown Current 0.15μA TYP · Low Quiescent Current 0.23μA TYP)",
          "evidence": "[官网]"
        },
        "5": {
          "value": "有 RCB 且是 True RCB —— ★官方 EC 表原文: \"True Reverse Current Blocking / RCB Protection Trip Point VT_RCB (VOUT - VIN): typ 6 mV, min 24 mV, max 50 mV / RCB Hysteresis VRCB_HYS: 30 mV\"; ★官方 APPLICATION INFORMATION 原文: \"The reverse current protection function is activated when VOUT is higher than VIN by VT_RCB. The reverse current protection is enabled whether the ON pin is high or low. This function prevents the current flowing from OUT to IN…\" => ★判据 5 满足, 且比 SGM2572 的『仅禁用态』更强 (导通态也挡); ★⚠️ 同一份手册的 FEATURES 栏写的是『Reverse Current Protection When Disabled』(厂家简写), 与 EC 表 + 应用说明 + 功能框图三处一致口径相左 => 以三处一致为准 = True RCB, FEATURES 那行不作反向证据",
          "source": "圣邦微官方数据手册 https://www.sg-micro.com/rect/assets/a8959667-d386-4c95-a64d-205e9b7b4446/SGM2575S.PDF (JULY 2025 - REV.A.1, SG Micro Corp) §ELECTRICAL CHARACTERISTICS 表 (True Reverse Current Blocking / RCB Protection Trip Point VT_RCB / RCB Hysteresis 行) + §APPLICATION INFORMATION (Reverse Current Protection 段) + §FEATURES 栏 + §FUNCTIONAL BLOCK DIAGRAM",
          "evidence": "[官网]"
        },
        "6": {
          "value": "WLCSP-0.76 x 0.76 mm = 0.578 mm² (官方 FEATURES 栏 Available in a Green WLCSP-0.76×0.76-4B Package) => 判据 6 (面积 <= 2 x 2 mm) 满足, 是 6 个候选里面积最小的; 官方热阻 WLCSP-0.76×0.76-4B θJA = 221 ℃/W / θJB = 82.6 ℃/W / θJC = 92.9 ℃/W",
          "source": "圣邦微官方数据手册 SGM2575S.PDF (JULY 2025 - REV.A.1) §FEATURES 栏 (Available in a Green WLCSP-0.76×0.76-4B Package) + §ABSOLUTE MAXIMUM RATINGS (Package Thermal Resistance 行) + §PACKAGE/ORDERING INFORMATION 表",
          "evidence": "[官网]"
        },
        "7": {
          "value": "★官方 PACKAGE/ORDERING INFORMATION 表 SPECIFIED TEMPERATURE RANGE = -40℃ to +125℃ (SGM2575SAYG/TR 与 SGM2575SADYG/TR 两个 OPN 同) => 判据 7 (-40 ~ +85 °C) 满足, 上限余量 40 ℃",
          "source": "圣邦微官方数据手册 SGM2575S.PDF (JULY 2025 - REV.A.1) §PACKAGE/ORDERING INFORMATION 表 (MODEL / PACKAGE DESCRIPTION / SPECIFIED TEMPERATURE RANGE / ORDERING NUMBER 列)",
          "evidence": "[官网]"
        },
        "8": {
          "value": "★官方 RECOMMENDED OPERATING CONDITIONS: ON Pin Input High Voltage VIH = 0.71V to 5.5V / ON Pin Input Low Voltage VIL = 0V to 0.3V; EC 表 VIH 0.71 V / VIL 0.3 V => 3.3 V GPIO 可直接驱动 => 判据 8 满足; 官方 FEATURES 栏『Low Threshold 1.2V GPIO Control Input』+『Smart ON』(上电期间智能下拉电阻避免 ON 引脚悬空, ON > VIH 后断开 => 默认态确定); EC 表 Smart Pull-Down Resistance RPD_ON = 1 MΩ (Disabled), Output Pull-Down Resistance RPD = 230 Ω typ / 300 Ω max (仅 SGM2575SAD 有 QOD); 另有 UVLO: VUVLO_R typ 0.94 V / max 1.26 V (TJ = -40℃ to +125℃), 迟滞 100 mV => SYS 下限 3.5 V 场景不受影响",
          "source": "圣邦微官方数据手册 SGM2575S.PDF (JULY 2025 - REV.A.1) §RECOMMENDED OPERATING CONDITIONS (ON Pin Input High Voltage / ON Pin Input Low Voltage 行) + §ELECTRICAL CHARACTERISTICS 表 (ON Pin Leakage Current / Smart Pull-Down Resistance / Output Pull-Down Resistance / UVLO Threshold, Rising / UVLO Hysteresis 行) + §FEATURES 栏 (Low Threshold 1.2V GPIO Control Input / Smart ON) + §APPLICATION INFORMATION (Smart ON 表 1)",
          "evidence": "[官网]"
        }
      },
      "rcb": {
        "verdict": "有",
        "quote": "The reverse current protection function is activated when VOUT is higher than VIN by VT_RCB. The reverse current protection is enabled whether the ON pin is high or low. This function prevents the current flowing from OUT to IN, and is very useful when SGM2575S is disabled and the output needs to be driven by another voltage source. (官方数据手册 APPLICATION INFORMATION 原文照抄) + True Reverse Current Blocking / RCB Protection Trip Point VT_RCB: VOUT - VIN, typ 6 mV, min 24 mV, max 50 mV; RCB Hysteresis VRCB_HYS 30 mV (官方 EC 表原文照抄)",
        "source": "圣邦微官方数据手册 https://www.sg-micro.com/rect/assets/a8959667-d386-4c95-a64d-205e9b7b4446/SGM2575S.PDF (JULY 2025 - REV.A.1, SG Micro Corp) §APPLICATION INFORMATION (Reverse Current Protection 段) + §ELECTRICAL CHARACTERISTICS 表 (True Reverse Current Blocking / VT_RCB / VRCB_HYS 行)",
        "evidence": "[官网]"
      }
    }
  ],
  "conclusion": {
    "same_package_with_rcb_available": false,
    "same_package_check_scope": "本次查证范围 = TI TPS229xx 单路负载开关族 (91/16/17/18/19/10A) + 圣邦微 SGM2572/SGM2575S。范围内带 RCB 的 4 款 (TPS22916 / TPS22917 / TPS22910A / SGM2572 / SGM2575S) 封装分别是 DSBGA-4 YFP / SOT-23-6 DBV / DSBGA-4 YZV / WLCSP-0.8x0.8-4B / WLCSP-0.76x0.76-4B —— 没有一款是现网表 footprint 的 UQFN-4 RAA (0.85 x 0.75, 0.4 mm pitch)。★残留缺口 [0数据]: TI 官网参数筛选器里 4 脚 UQFN-HR (RAA) 全系带 RCB 的型号本轮未逐项穷举 ⇒ 若老板要求 100% 穷举, 需按 TI 官网 Load Switch 参数筛选器 (Package = UQFN-HR 4 / VIN <= 5.5 / Reverse Current Protection = Yes) 过滤后逐个核数据手册, 这是一条人工动作 (本单不做, 也不能靠推断代替)。★2026-11-17 补证: 三颗带 RCB 候选的官方引脚原表已取到 (TPS22916 A1=VOUT/A2=VIN/B1=GND/B2=ON · SGM2572 A1=VOUT/A2=VIN/B1=GND/B2=ON · SGM2575S A1=OUT/A2=IN/B1=GND/B2=ON) => 三者球编号一致但与现网表 1=VIN/2=ON/3=VOUT/4=GND 无一兼容 ⇒ 改板必须重画 footprint 并逐线重核",
    "recommendation_order_source": "DECISION_PENDING_2026-11-16.md §A5 (老板待拍优先级序: 1 反向阻断 > 2 IQ < 5uA > 3 RON 越小越好 > 4 封装/面积)",
    "recommendation_by_a5_order": "按 A5 建议序: (1) 反向阻断优先 => 唯一同时满足 RCB + RON <= 40 mΩ 的在售型号是 SGM2575SADYG/TR (True RCB, 30 mΩ, 2A, 0.578 mm²), 代价 = 改板 + ★引脚原表已取到 (2026-11-17 补证) ⇒ 三颗 RCB 候选的球编号 A1=VOUT/A2=VIN/B1=GND/B2=ON 与现网表 1/2/3/4 无一兼容 ⇒ 板那一趟必须逐线重核; ★另注: SGM2575S RON 30 mΩ typ / 63 mΩ max ⇒ 『唯一 RCB + RON 双满足』只在 typ 口径成立, max 口径下没有 RCB 候选能过判据 3; (2) 若 IQ/关机续航优先 => TPS22916BYFPR (ISD 10 nA typ / 100 nA max) 与 TPS22917xDBVR (10 nA typ) 最好, 但 RON 60/80 mΩ 超判据 3; (3) 若 RON 优先 => TPS22991RAA 25 mΩ 最优但无 RCB, 且关断漏电 max 20 uA 超判据 4; (4) 若 封装/面积/不改板优先 => 只有 TPS22991RAA (同封装 UQFN-4 RAA, 换料不换板) 满足, RCB 缺口用 FB1 兜",
    "recommendation_disclaimer": "★本单只交证据 + 按 A5 建议序的推荐, 不代拍优先级序, 不代拍型号 ⇒ 最终拍板 = 老板 (DECISION_PENDING_2026-11-16.md §A5 / §Q2)",
    "key_findings": [
      "TPS22991RAA (ISS-234 点名推荐) 唯一硬超判据的是判据 4 的 max 口径: 关断漏电 ISD max 20 uA @ -40~85 °C > 5 uA (typ 14 nA 远低于门槛) => 关机账 108 uA 里这一项按 max 占 18.5%",
      "现网表 OPN 'TPS22991RAA' 只锁了封装 (RAA), 没有变体字母: TI 数据手册 Device Comparison Table 列 TPS22991B/BN (快上电) 与 TPS22991C/CN (慢上电) 四个变体, 上电上升时间 141 us (B/BN) vs 662 us (C/CN) @3.3V, 且 QOD 有无随变体不同 => 落表批次必须补全 OPN 变体字母",
      "RCB 缺口在本板是硬需求而不是形式条款: 关机插 USB 时充电板 PG 拉低 => Q_PG_1 (P-MOS 高边, HW/POWER_SHUTDOWN_V3.md §3) 把 ON 拉到 BAT_SW => 负载开关被强制导通 => 5V 经 SoC IO 到 SYS 再经开关通道反灌回 BAT_SW; N 沟道体二极管只挡 VIN->VOUT 方向, 挡不住导通态的通道反灌 => 没有 RCB 就真的会把电池反灌",
      "判据口径冲突 (本单只报不改): HW/POWER_SHUTDOWN_V3.md §2 判据 2 写 Iout >= 2A (持续 1A 上下), 而 HW/netlist_v1.csv L37 写 SYS 最大电流 0.55A (330 mA x 1.5 + 瞬态) => 两处口径不一致, 压降与发热推算按 0.55A / 1A / 2A 三档都给, 由老板与 main 裁",
      "2026-11-17 补证: 圣邦微两颗候选 (SGM2572 / SGM2575S) 的官方数据手册 PDF 已从官方服务器直取 => 证据等级全部从 [媒体] 升级为 [官网], 全文已无 [媒体] 依赖; 同时关闭了两个 [0数据] 格 (绝对最大额定 VIN -0.3~6V => 判据 1 满足; 4-ball 引脚原表)",
      "2026-11-17 补证查出的实质影响: SGM2575S 官方 EC 表给出 RDSON max = 63 mΩ (SGM2572 = 60 mΩ) => 『唯一 RCB + RON <= 40 mΩ 双满足』只在 typ 口径成立; max 口径下没有任何一颗带 RCB 的在售型号能过判据 3 => 建议老板拍优先级序时一并拍『RON 按 typ 还是按 max 判』+『SYS 电流按 0.55A 还是 2A 算』",
      "2026-11-17 补证查出的引脚硬事实: TPS22916BYFPR / SGM2572ADYG/TR / SGM2575SADYG/TR 三颗带 RCB 的候选, 官方手册 PIN CONFIGURATION 全是 A1=VOUT / A2=VIN / B1=GND / B2=ON, 与现网表 1=VIN/2=ON/3=VOUT/4=GND 无一兼容 => 改板不是『换个料号』而是『换引脚编号体系』, 板那一趟必须逐线重核"
    ]
  },
  "netlist_value_snapshot": "TPS22991RAA (负载开关 1=VIN/2=ON/3=VOUT/4=GND, UQFN-4 RAA · ≥2A · R_on 25mΩ@5V · 无 RCB ⇒ 选型口径待 A5 追认)",
  "netlist_value_pre_drift": "[待选型] 负载开关 (≥2A, R_on ≤40mΩ@3.7V, IQ ≤5µA, 带反向阻断)",
  "netlist_drift": {
    "landed_by": "ISS-257 (hw-lead · G1a-7 选型落表 · main 2026-11-16 verified)",
    "landed_at": "2026-11-16 21:2x 决定 / 2026-11-16 22:25:14 写盘 (HW/netlist_v1.csv mtime)",
    "landed_ref": "state/_apply_iss257_g1a7_selection.py (一次性落表器) + state/gen_netlist.py (真源)",
    "reason": "G1a-7 要求把 14 件「必装 ∩ value 含 [待选型]」回填成真实可采购型号; U_PWR_SW_1 落的是本矩阵里唯一与现 footprint 逐字一致的 TPS22991RAA, 并把 RCB 缺口写进 value 栏 ⇒ 落表批次明知缺 RCB 也要落, 口径留给 A5 追认",
    "pre_drift_snapshot": "[待选型] 负载开关 (≥2A, R_on ≤40mΩ@3.7V, IQ ≤5µA, 带反向阻断)",
    "post_drift_snapshot": "TPS22991RAA (负载开关 1=VIN/2=ON/3=VOUT/4=GND, UQFN-4 RAA · ≥2A · R_on 25mΩ@5V · 无 RCB ⇒ 选型口径待 A5 追认)",
    "dropped_requirements": [
      "网表 value 栏不再写 IQ ≤5µA ⇒ 判据 4 (关机漏电) 在网表侧失声 (判据真源 HW/POWER_SHUTDOWN_V3.md §2 一字未改, 本矩阵仍按判据 4 逐格评)",
      "网表 value 栏不再写 带反向阻断 ⇒ 改成 无 RCB ⇒ 判据 5 (反向阻断) 在网表侧从「必须」变成「已知缺口」"
    ],
    "residual_gaps_ref": "顶层 residual_gaps (三条)",
    "verify": "main 2026-11-16 13:2x~13:3x 实跑复验 ISS-172 (rc=0 · selftest 8/8); ★本次 drift 由 sw-lead 2026-11-17 第 2 轮实测发现并重锚"
  },
  "residual_gaps": [
    "L50 note 栏仍写「选型判据 8 条见 HW/POWER_SHUTDOWN_V3.md §2 (型号待选型, 询价经项目总工)」⇒ 与同一行的 value 栏 (已落型号 TPS22991RAA) 自相矛盾 ⇒ 残留缺口 ⇒ 归落表批次",
    "L50 note 栏仍写「反向阻断必查 (关机插 USB 时防 5V 经 SoC IO 反灌电池)」⇒ 与同一行 value 栏的「无 RCB」并存 ⇒ 同一器件本体行里「必查」与「无」互相矛盾 ⇒ 残留缺口 ⇒ 归落表批次",
    "L442 (U_EN_SW_1) note 栏仍写「选型 = TPS22991RAA (项目总工 11-03 已裁, ISS-172 待老板点头)」⇒ ISS-172 已交卷 ⇒ 实际只剩「A5 优先级序」这一句 ⇒ 残留缺口 ⇒ 归 main / 落表批次"
  ],
  "netlist_update_note": "★2026-11-16 22:25 由 hw-lead 的 ISS-257 落表批次把网表 L50 的 value 栏从 『[待选型] 负载开关 (≥2A, R_on ≤40mΩ@3.7V, IQ ≤5µA, 带反向阻断)』改成上面这行 => 本快照已跟到落表后的真值 (★本单只交证据, 不落表, 不改网表★); 落表落的是『不改板』分支 (TPS22991RAA 同封装), 『无 RCB』缺口仍在, 等 §A5 追认"
}
```
<!-- END 选型证据基准块 -->

> ★**上面这段是机器可读基准块** (只由 `SW/tools/check_load_switch_selection.py` 校验; 人读的那份是 §2 的矩阵与 §3 的 RCB 专项)。★**不要手改**: 改完必须重跑门禁 `python3 SW/tools/check_load_switch_selection.py` (rc=0) 与 `--selftest` (8/8)。
