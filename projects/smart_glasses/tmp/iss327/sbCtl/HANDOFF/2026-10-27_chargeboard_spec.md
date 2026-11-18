# [hw-lead→PM] 充电板 (镜框) 器件级连接规格 —— ISS-093 支撑产出

- 发起方: hw-lead (硬件总工)
- 日期: 2026-10-27
- 产出: **`HW/CHARGE_BOARD_SPEC.md`** (充电板整页器件级连接规格, 11 节) + 本交接单
- **本单没有改任何生成物**: `state/gen_netlist.py` / `HW/netlist_v1.csv` / `HW/SCHEMATIC_V1.md` / `HW/BOM_v1.csv` **一字未动**; `state/` 下无写入; `state/fragments/` 无写入; `MECH/` `SW/` `PROJECT_TRACKER.md` `DECISIONS.md` 无触碰; **未联系任何供应商/原厂**。
- 依据: `HW/SCHEMATIC_V1.md` P1/P6/P9 · `HW/INTERFACE_TABLE.md` §4.2 + 电源轨表 · `HW/POWER_IC_SELECTION.md` §3.1/§3.5 · `HW/BOM_v1.csv` · `MECH/USB_HINGE_STRUCTURE.md` · `MECH/MECH_BUDGET.md` · **TI BQ25896 datasheet (ti.com) · TI TPS25730 datasheet (ti.com) · USB Type-C Spec R2.0 (usb.org, 已下载全文)**

---

## B1 结论摘要

1. **★交付物**: `HW/CHARGE_BOARD_SPEC.md` —— 充电板器件级连接规格, 含 **80 行可落网表的连接清单** (列与 `HW/netlist_v1.csv` 完全一致: `page/net/node1/node2/ref/value/type/dnp/evidence/tbd/note/conn_id/board`), PM 直接照它改生成器即可。
2. **★Type-C 16p 母座 16 脚全部落到物理 A/B 位** (USB-IF Spec R2.0 **Table 3-5** 原文核对, 不是自拟): 14 脚接线 + 2 脚 NC (SBU1 A8 / SBU2 B8), 另 8 个 A/B 位置 (A2/A3/A10/A11/B2/B3/B10/B11) 在 16p 母座上**物理不存在**, PCB 不得放焊盘。
3. **★★查出 3 处现行网表的硬伤 (都不是"缺件", 是"接错/漏接")**:
   - **① Type-C 的 GND 只接了 A1+A12, 漏了 B1+B12** —— USB-IF Table 3-5 规定 16p 母座 GND 是 **A1/A12/B1/B12 四个脚**, 现行网表漏两个 ⇒ **Type-C 回流路径少一半**。本规格已补齐到 16 == 16。
   - **② TS 线没进跨铰链 pin map** —— V1.2 已裁决"NTC 贴电芯 → 在镜脚 → BQ25896 的 TS 脚在镜框 ⇒ **TS 必须跨铰链**", 但现行 `J_CHG` pin map (pin5=CHG_STAT/pin6=PG/pin7=VBUS_DET/pin8-10 预留) **没有 TS 这一根**, 且网表里 `R_NTC_BAT` 还被标成 `CHG_BOARD` 并接到 `BAT_PROT` —— **网表与裁决直接矛盾**。
   - **③ TS 分压阻值与 datasheet 不符** —— datasheet Equation 2 原文给的是 **RT1=5.24k (REGN→TS) + RT2=30.31k (TS→GND) + 103AT NTC 并在 RT2 上**; 现行网表是 "10k NTC + 10k 下拉" ⇒ 阈值全错, 电池过温保护会误动作/不动作。本规格给出 datasheet 原文值并**独立复算验证** (0°C→73.26% ≈ V(T1)=73.25%; 60°C→34.40% ≈ V(T5)=34.375%)。
4. **★BQ25896 逐脚规格 (24 脚全覆盖)**, 关键项全部照 datasheet 原文:
   - 输入去耦: **1µF @ VBUS (pin1) + 其余 @ PMID (pin23)** (原文 "put 1µF on VBUS to PGND, and the rest capacitance on PMID to PGND") —— 现行网表把 100µF 堆在 VBUS 脚、**PMID 没电容**, 要改。
   - `C_REGN` 4.7µF/10V (pin22) · `C_BST` 47nF (pin19/20↔pin21) · `C_BAT` 10µF (pin13/14) · 开关电感 **2.2µH** (纹波 0.29A = 29%, 落在 datasheet 20-40% 指引内; 1µH 会到 64%)。
   - **PSEL 拉低 / CE 拉低 / OTG 拉低 / QON 悬空 (内部上拉)** —— "CE pin must be pulled High or Low" ⇒ CE **不得悬空**。
5. **★★最重要的一条: `R_ILIM` 是本板唯一的安全兜底件**。
   - BQ25896 的 **REG04 复位默认 ICHG = 2048 mA** [官方] ⇒ **不编程 I2C 时, 充电电流默认就是 2.05A**。
   - ILIM 脚是稳在 0.8V 的电压节点, `IINMAX = KILIM/RILIM` (KILIM 320/355/390 AΩ) ⇒ **一颗 300Ω 电阻就把输入电流硬件封在 1.07-1.30A (CC 段电池电流 ~0.88-1.07A)**, 与软件无关。
   - ⇒ **`R_ILIM` 不装 = 铰链段过 2.05A (超 1.5A 设计点 1.37 倍)**。建议门禁加一条"必须有 ILIM 电阻"判据。
   - ISS-091 若判定铰链只能过 1.0A ⇒ **换 390Ω (→ 0.82-1.00A), 换料不换板**。
6. **★CC/PD 取舍: 我的推荐 = 第一版不上 TPS25730, 只留 Rd 5.1k ×2**。依据: (a) 我们只要 5V, PD 的高压能力对 1S 锂电整机**一点用没有**; (b) **充电板没有 3.3V 轨**, 而 TPS25730 的 VIN_3V3 要 3.0-3.6V (绝对最大 4V) ⇒ 要么额外加一颗 LDO, 要么走 datasheet 没给示例的 "VBUS LDO" 路径 (**待 TI 确认**); (c) 25×10mm 小板放不下 QFN-38 + 10 颗外围; (d) **真正的安全上限由 `R_ILIM` 给, PD 一个都给不了**。
7. **★★"PD 5V/2A 会不会把铰链电流抬到 2A" 的量化回答 (本单核心分析)**: **不会 —— 铰链过的是电池充电电流 ICHG, 不是输入电流 IIN**, 而 `ICHG ≈ 0.822 × IIN` (VBAT=3.7V / VBUS=5V / η=90%)。
   - Rd-only + 常见 Rp=56k 充电器 → 源只给 500mA → **铰链只过 ~0.41A** (余量 3.7×);
   - 加 PD 5V/2A + `R_ILIM`=300Ω → **铰链 ~0.88-1.07A** (余量 1.4-1.7×);
   - **最坏 = 不编程 ICHG 且不装 `R_ILIM`** → 铰链 **2.048A** ❌。
   - ⇒ **铰链 1.5A 规格不用改; 要盯的是 `R_ILIM` 取值, 不是 PD。**
8. **★BQ25896 的 I2C 地址现行记载是错的**: `HW/INTERFACE_TABLE.md` §4.2/§4.4 写 **0x12 [推算] — 需查 datasheet**, datasheet 原文是 **0x6B (1101011B)** [官方]。0x6B 与总线 A 现有地址 (0x36/0x48/0x50/0x54/0x72/0x62) **不冲突** ⇒ 无论走不走 I2C, 这条都要改。
9. **★`J_CHG` pin map 提案 (10p @0.5mm)**: 1/2=BAT_CHG(并联) · 3/4=GND(并联) · **5=TS(新增)** · 6=CHG_STAT · 7=PWR_GOOD · 8=VBUS_DET · **9/10=充电 IC 的 I2C(新增, 预留 DNP)**。
   - 现行 pin map 是 5=CHG_STAT/6=PG/7=VBUS_DET/8-10=预留 ⇒ 本提案把 3 根信号各后移 1 位, **pin map 要改**。
   - 与结构侧 `MECH/USB_HINGE_STRUCTURE.md` §5.3 **C-4 建议 8p** 有出入 —— 但**铰链高度预算够**: P9 已算 (10+4+18+21)×0.5 = **26.5mm** vs 镜脚根部净高 **37.0mm** ⇒ 余 **10.5mm** ✅。**建议请结构总工按 10p 复核一次**。
   - ★**"电池挪回镜框"的可回退分支与基线 pin map 不兼容** (脚数 9 且映射不同) ⇒ **电池位置必须在打样前锁死**。
10. **★跨铰链 9 类线逐类给了取值**: 充电电流双 pin (1.0-1.5A, 每 pin ≤0.75A, **不装 π 滤波**) · 回流双 pin · VBUS_DET (1M+1M, 源阻抗 500kΩ, 必须 GND 夹持 + 距 USB 差分 ≥3mm) · CHG_STAT / PWR_GOOD (开漏, **上拉只能放主板侧**, 充电板无 3.3V) · USB D+/D− (90Ω, 双份并联 ≤3.5mm, 不装共模扼流圈) · TS (新) · 充电 IC I2C (新, 预留) · USB 回流独立 pin。
11. **机械/装配约束 15 条全部引自 MECH 已有结论, 一条没自创**: 开孔 **9.5×3.6mm** · 末端壁厚 **≥1.5mm** · **Type-C 座正下方 ≥2 个承力柱 + 一个沿拔出方向的限位台阶** (ISS-085 F-4/F-5) · 拔线力不得经由 FPC 传递 · 充电板 25×10×0.8mm + M1.2 + 铝屏蔽罩 · Type-C 与充电 IC 热隔离 ≥5mm · ESD ≤3.0mm 且不上 FPC · `J_CHG` 机械防呆。
12. **★电池保护 IC 不在充电板**: BQ2970 + 2×MOS + 电芯全在**镜脚主 PCB** ⇒ **充电板 BOM 明确不含这三样** (备料口径要写死, 否则重复采购)。

---

## B2 验收标准自评

| 验收标准 (PM 给的 4 条) | 自评 | 依据 |
|---|---|---|
| **① 每个连接器声明的 pin 都要能数出来 (Type-C 16p 必须列全 16 脚去向, 哪怕写"不接")** | ✅ **通过** | `HW/CHARGE_BOARD_SPEC.md` §1.2 把 **24 个 A/B 位置全列**: 16 个真实触点 (14 接 + SBU×2 写"不接") + 8 个 16p 不存在的位置 (写"无此触点/无焊盘"); §7.1 给出计数对账表。脚本自检: `J_TYPE_C pads: 16 (+shield)` / `U_CHG pins: 24` / `J_CHG pins: 10` —— **声明 == 清单引用** ✅ |
| **② 每个器件给证据等级; 拿不到的写"待选型/待原厂", 不许编型号** | ✅ **通过** | 清单里 80 行的 `evidence` 列: **[官方] 55 行 / [推算] 23 行 / [待裁决] 2 行**; §9 给出 24 条结论的分级表; §8 列出 **4 条待原厂 + 5 条待选型 + 1 条待复算 + 3 条待改** —— **没有一个型号是编的** (Type-C 座 / ESD 阵列 / 磁珠 / 电感 / TVS 一律"待选型", 询价走 PM) |
| **③ 末尾给"可落网表"的连接清单, 列与 `HW/netlist_v1.csv` 一致** | ✅ **通过** | §7 CSV 块, 13 列 × **80 行**, 用 `csv.DictReader` 解析 **0 个残行**; 列名逐字对齐 `page,net,node1,node2,ref,value,type,dnp,evidence,tbd,note,conn_id,board`; 每行 13 列写脚本断言过 |
| **④ 交不出证据的项: 写清"缺什么 / 谁能给 / 什么时候"** | ✅ **通过** | §8 表格 18 行, 每行 4 列 (缺什么 / 谁能给 / 什么时候 / 影响哪一条) —— **无空口** |
| **覆盖项 1: Type-C 16p 完整物理脚位** | ✅ 通过 | §1.2 (24 位全列) + §1.3 (≤3.5mm / 4 脚并联 / SBU 不接 / 屏蔽壳单点) |
| **覆盖项 2: BQ25896 全电路** | ✅ 通过 | §2.2 逐脚 24 行 (引脚/类型/连接/值/证据/备注) + §2.3 去耦电感 + §2.4 ILIM + §2.5 TS + §2.7 控制脚 + §2.8/§2.9 两条风险 |
| **覆盖项 3: CC/PD 取舍 + 推荐 + 依据 + 对跨铰链电流的影响** | ✅ 通过 | §3.1 事实基础 (全部官方) + §3.2 两方案对比 + §3.3 **推荐方案 A + 5 条依据 + 2 条补丁** + §3.4 **6 场景量化表** |
| **覆盖项 4: 保护与滤波 (ESD / π / OVP 浪涌 / 电池保护不在本板)** | ✅ 通过 | §4.1 ESD (5 网 / ≤1pF / ≤3pF / ≤3.0mm) + §4.2 π (含"PMID 也必须有电容"的 datasheet 原文) + §4.3 OVP/TVS + §4.4 **电池保护不在本板** |
| **覆盖项 5: 跨铰链 4 类线 (+2 类新增) 的要求与取值** | ✅ 通过 | §5.1 9 类线逐类表 + §5.2 pin map 提案 + §5.3 5 条待裁决 |
| **覆盖项 6: 机械/装配约束 (引自 MECH)** | ✅ 通过 | §6 共 15 条, 每条标 MECH 出处; **未自创任何数** |
| **硬规则: 球位号仍全 TBD-01, 不许编造** | ✅ 通过 | 本单**零个** SoC 球位号; 涉及 SoC 的地方只写 "SoC 侧球位号 TBD-01" 占位 |
| **硬规则: 不许改 state/ / 不写 state/fragments/ / 不碰 MECH SW PROJECT_TRACKER DECISIONS** | ✅ 通过 | 本单只写了 2 个新文件: `HW/CHARGE_BOARD_SPEC.md` + 本交接单 |
| **硬规则: 球位号/网表由 PM 落生成器** | ✅ 通过 | §11 给了"PM 落 P10 时要动的清单" (5 个文件), **生成物一律没手改** |
| **可落网表清单行数** | ⚠️ **未验 (需 PM 落进生成器后由 `state/check_netlist.py` 判)** | 本单只保证 **CSV 格式与列数**自洽; ERC/DRC (如 "PGND 单点接地"、"每条轨都有来源") 需 PM 落页后跑 |
| **与现行网表的一致性** | ❌ **不通过 (已列 3 处硬伤 + 1 处待改)** | B1 第 3 条 + B5 待改 1/2/3 —— **须 PM 在生成器里修**, 本单无权改 |

---

## B3 证据分级

| 关键结论 | 等级 | 说明 |
|---|---|---|
| Type-C 16p 物理脚位 (24 个 A/B 位置, 16 个真实触点) | **[官方]** | **USB Type-C Cable and Connector Specification R2.0 (usb.org, 2019-08) Table 3-5** —— 官方 PDF 全文已下载 (373 页), 表格原文逐字核对 |
| D+/D− 双份并联走线 **≤3.5 mm** | **[官方]** | 同上 Table 3-5 Note 2 原文 |
| SBU (A8/B8) **不接** | **[官方]** | 同上 Table 3-5 Note 3 原文 |
| 未用触点须电气隔离 | **[官方]** | 同上 Table 3-5 Note 1 原文 |
| Rd = **5.1 kΩ ±20%** | **[官方]** | 同上 §4.x / §5.x 原文 |
| 源端 Rp: 56kΩ→500mA / 22kΩ→1.5A / 10kΩ→3.0A | **[官方]** | 同上 **Table 4-24** 原文 |
| BQ25896 引脚表 (1-24) | **[官方]** | TI BQ25896 datasheet §7 + **第 5 页 Pin Configuration 图 (已渲染成 PNG 用视觉模型逐字核对, 不是靠猜)** |
| BQ25896 **I2C 地址 0x6B** | **[官方]** | 同上 §9.2.16.5 + 特性表 "I2C Address 6BH" |
| BQ25896 **REG04 复位默认 ICHG = 2048 mA** (可编程 0-3008mA) | **[官方]** | 同上 REG04 Table 10 |
| BQ25896 REG00 复位默认 IINLIM = 500 mA (PSEL=Low 时自动切 3.25A) | **[官方]** | 同上 REG00 Table 6 |
| ILIM: `IINMAX = KILIM/RILIM`, ILIM 脚稳在 0.8V, KILIM=320/355/390 AΩ | **[官方]** | 同上 Pin Functions (pin10) + §8.5 |
| 输入去耦 "1µF on VBUS to PGND, 其余 on PMID" · BAT 10µF · REGN 4.7µF/10V · BTST 0.047µF | **[官方]** | 同上 pin1 / pin23 / pin13-14 / pin22 / pin19-21 说明原文 |
| 环路稳定 "1-µH + ≥20µF 输出电容" · 输入体电容 8.2µF (3-5A) | **[官方]** | 同上 §10.2.2.2 / §10.2.2.3 |
| TS 门限 V(T1)=73.25% / V(T2)=68.25% / V(T3)=44.75% / V(T5)=34.375% of REGN | **[官方]** | 同上 §8.5 |
| TS 分压 RT1=5.24k / RT2=30.31k / 103AT | **[官方]** | 同上 **Equation 2** (原文直接给了这组解) |
| **TS 分压独立复算验证** (0°C→3.663V=73.26%; 60°C→1.720V=34.40%) | **[推算·可复算]** | 本单自算, B6 命令 10 一条命令复现, 与 datasheet 阈值吻合到 0.01% |
| TPS25730: VIN_3V3 **3.0-3.6V** (绝对最大 4V) · QFN-38 4×4mm · θJA 57.4°C/W · 内置 dead-battery Rd (RSNK 4.1-6.1k) · ADCIN 配 5V/2A (Operating 2A/Max 3A) | **[官方]** | TI TPS25730 datasheet §6.1/§6.5/§5/§8.3.11-13 |
| Type-C 座外形 8.94×6.5×3.16mm / 沉板 4 档 / 10000 次 / 面板开孔 9.5×3.6 | **[官方·厂商页]** | `HW/POWER_IC_SELECTION.md` §3.5 (航宏 hhswitch.com) —— **本单只转引**; 厂商页抓下来是 JS 页面, **无型号级数据** → 型号 [0数据] |
| 承力柱 ≥2 + 限位台阶 · 壁厚 ≥1.5mm · 开孔 9.5×3.6 · 热隔离 ≥5mm · ESD ≤3.0mm | **[官方·结构]** | `MECH/USB_HINGE_STRUCTURE.md` §5.2 F-4/F-5/E-1 + §7 —— **本单只转引, 一个数没自创** |
| 充电板 25×10×0.8mm · M1.2 + 铝屏蔽罩 | **[推算]** | `MECH/MECH_BUDGET.md` §1.3 M3 —— 转引 |
| ESD 阵列 5 网 / ≤1pF / ≤3pF / VRWM 档 | **[推算]** | `HW/POWER_IC_SELECTION.md` §3.5 (EMC R-03) —— 转引 |
| `R_ILIM`=300Ω → IIN 1.07-1.30A → ICHG ~0.88-1.07A | **[推算·可复算]** | 公式 `IINMAX=KILIM/RILIM` + `ICHG≈IIN×VBAT/VBUS/η`, B6 命令 10 可复现 |
| 电感纹波 0.29A @2.2µH (29%) / 0.64A @1µH (64%) | **[推算·可复算]** | datasheet §10.2.2.1 公式, B6 命令 10 可复现 |
| 铰链载流 6 场景表 (0.41A ~ 2.048A) | **[推算]** | §3.4; 假设 VBAT=3.7V / η=90%, 已标注 |
| 铰链区高度 26.5mm vs 37.0mm (余 10.5mm) | **[官方·项目内]** | `HW/SCHEMATIC_V1.md` P9 (转引) |
| Type-C 座 / ESD 阵列 / 磁珠 / 电感 / TVS **具体型号** | **[0数据]** | 厂商询价走 PM —— **本单未联系任何供应商/原厂** |
| BQ25896 / TPS25730 单价与交期 | **[0数据]** | 同上 |
| TPS25730 "只用 VBUS LDO 路径" 接法是否可行 | **[0数据]** | datasheet 只给外部 3.3V 供 VIN_3V3 的示例, 未给该路径示例 → **待 TI 确认** |

---

## B4 接口取值声明

| 接口 | 本版取值 (短规范值) | 说明 |
|---|---|---|
| 新页号 | **P10** | 充电板器件级页 (P1/P6/P9 已有充电链子集, P10 补完整页) |
| 连接清单规模 | **80 行 × 13 列** | CHG_BOARD 65 / MAIN_PCB 4 / HINGE 11; 必装 68 / DNP 12 |
| `J_TYPE_C` | **16p 母座, 16 触点全列** | 物理 A/B 位; 14 接 + SBU×2 NC; 屏蔽壳单点接 GND |
| `U_CHG` | **BQ25896 VQFN-16 3×3mm, 24 脚全覆盖** | 1-24 逐脚给连接 |
| `J_CHG` | **1×10p @0.5mm (本单提案 pin map)** | 1/2=BAT_CHG · 3/4=GND · 5=TS · 6=CHG_STAT · 7=PG · 8=VBUS_DET · 9/10=I2C(预留) —— **待 PM 裁决** |
| 充电电流 | **1.0 A 典型 / 1.5 A 上限** | ILIM 硬件封顶; 对齐 `POWER_IC_SELECTION` §3.1.3 "推荐 1.0A" |
| 输入电流硬件上限 | **1.07-1.30 A** (`R_ILIM`=300Ω) | 换 390Ω → 0.82-1.00A (换料不换板) |
| Type-C 输入 | 5.0V ±5%, USB 2.0 | CC 走 **Rd 5.1k ×2 (不上 PD 控制器)** |
| 铰链大电流 | **1.0-1.5A 双 pin 并联, 每 pin ≤0.75A** | **不装 π 滤波**; 载流核算见 ISS-091 |
| TS 分压 | **RT1 5.24k (REGN→TS) / RT2 30.31k (TS→GND) / NTC 103AT 并在 RT2** | datasheet Equation 2 原文值 |
| 开漏跨铰链信号 | CHG_STAT / PWR_GOOD / INT, **上拉一律主板侧 3.3V** | 充电板无 3.3V 轨 |
| ESD 阵列 | **5 网 / ≥5 通道 / D±≤1pF / CC·VBUS≤3pF / 距座 ≤3.0mm** | VRWM 档待 PM 拍板 |
| π 滤波 | 磁珠 (≥2A) + 10µF + 100µF, **ESD 在前、磁珠在后** | 另加 1µF@VBUS + 10µF@PMID (BQ25896 自己的) |
| 电池保护 | **不在充电板** | BQ2970 + 2×MOS + 电芯全在镜脚 |
| 球位号 | **零新增** | SoC 侧一律 TBD-01 占位 |

---

## B5 未决项与卡点

### 接口请求 (给 PM, 不直接联系其他总工)

1. **★CC/PD 拍板 (最高优先, 卡 P10 落页)** — 对方: **PM**; 需不需要同步 TI → 走 PM。
   - 我的**推荐: 不上 TPS25730, 只留 Rd 5.1k ×2** (依据见 B1 第 6 条)。
   - 若 PM 拍板"必须 5V/2A 可控", 则**必须同时解决 VIN_3V3 的 3.3V 来源** —— 要么加一颗 3.3V LDO, 要么走 datasheet 没给示例的 "VBUS LDO" 路径 (**待 TI 确认**), 且充电板面积 +8-10%。
   - **两个选项都不影响本单已交付的规格**: 选 A 直接落 P10; 选 B 只需在 P10 上加一颗 IC + ~10 颗无源件, 连接清单其余部分不变。

2. **★`J_CHG` pin map 拍板 (卡 PCB 开孔, 不可逆)** — 对方: **PM** (+ 结构总工复核 10p)。
   - 采纳本提案 (10p, 含 TS + I2C 预留)? 还是退回 8p (则必须放弃充电 IC 的 I2C 跨铰链, 充电电流只能靠 `R_ILIM` 兜底)?
   - **同时请转达结构总工**: §5.3 **C-4 建议的 8p** 是在没算 TS / I2C 的前提下数的脚; 按 P9 的堆叠预算, **10p 仍余 10.5mm** ⇒ 请复核一次 10p。

3. **★电池位置锁死 (镜脚 vs 镜框)** — 对方: **PM**。
   - 本单发现: "电池挪回镜框"的可回退分支**与基线 pin map 不兼容** (脚数 9 且映射不同) ⇒ **打样前必须锁死**, 否则连接器焊盘要重画。

4. **★BQ25896 的 I2C 跨不跨铰链** — 对方: **PM**。建议**跨 (pin9/pin10, 默认 DNP)**; 不跨也能工作 (靠 `R_ILIM` 兜底), 但 SoC 就无法按 BC1.2 结果调 IINLIM, 也不能读 VBUS/IBAT。

5. **`VBUS_DET` 是否保留** — 对方: **PM**。与 PG 功能重叠, 保留但可 DNP; 保留则占用 pin8, 去掉则 pin8 空出。

6. **ESD 阵列 VRWM 档** — 对方: **PM**。≥24V (为将来上 PD 留后路) vs 5-6V (当前 5V 足够、钳位更低)。**若按 B5-1 选"不上 PD", 建议直接用 5-6V 档**。

### 待原厂 / 待选型 (缺什么 / 谁能给 / 什么时候)

| # | 缺什么 | 谁能给 | 什么时候 |
|---|---|---|---|
| 待原厂-1 | KILIM 在 **低电流档 (1.0A)** 的 trim 值 (datasheet 只在 1.5A 工况点给 320/355/390 AΩ) | TI 技术支持 | 投板前 |
| 待原厂-2 | SYS 脚悬空 (不接 20µF) 是否影响 BATFET 通路 / 充电环路 | TI 技术支持 | 投板前 |
| 待原厂-3 | 100µF 体电容放 VBUS 上游 vs 全部放 PMID | TI 技术支持 | 投板前 |
| 待原厂-4 | TS 下臂接 GND 还是接电芯负极 BAT− | TI 技术支持 | 投板前 |
| 待原厂-5 | (若上 PD) TPS25730 "只用 VBUS LDO" 路径接法 | TI 技术支持 | 拍板后立即 |
| 待选型-1 | Type-C 16p 母座型号 + PCB 焊盘图 | 厂商询价 (经 PM) | 备料前 |
| 待选型-2 | ESD 阵列型号 (5-6 通道, D±≤1pF) | 厂商询价 (经 PM) | 备料前 |
| 待选型-3 | 磁珠 (≥2A, DCR≤50mΩ) + 5V 级 TVS | 厂商询价 (经 PM) | 备料前 |
| 待选型-4 | 2.2µH 电感 (Isat≥1.5A) | 厂商询价 (经 PM) | 备料前 |
| 待复算-1 | ISS-091 铰链段 1.5A 载流/压降/发热 | 结构总工 | 投板前 (定 `R_ILIM` 300Ω 还是 390Ω) |
| 待改-1 | `INTERFACE_TABLE.md` §4.2/§4.4: BQ25896 地址 **0x12 → 0x6B** | PM | 下轮 |
| 待改-2 | 网表 `R_NTC_BAT` / `R_TS_PULL` 的板别与接法 | PM (落 P10) | 落 P10 时 |
| 待改-3 | 网表 P1 里 22 行 SYS/DC-DC/LDO 的 `board` 列 (CHG_BOARD → MAIN_PCB) | PM (生成器) | 落 P10 时 |

### 做不到 / 交不出的项 (探测记录 + 为什么不物理可行 + 可执行替代)

| 项 | 探测记录 | 为什么不物理可行 | 可执行替代 | 有环境就能立刻出结果 |
|---|---|---|---|---|
| Type-C 16p 母座**具体型号 + 焊盘图** | `curl https://www.hhswitch.com/type16p/` → HTTP 200, 但页面是 JS 渲染, 可读文本里**只有公司名, 无任何型号/尺寸参数** | 厂商未在页面暴露型号级数据; 更深层目录未公开 | 用**同类 16p 沉板座的通用焊盘 (4 脚插板)** 先画, 型号定了只改焊盘不改原理图 | 有浏览器/厂商 PDF 目录即可立刻出结果 |
| TPS25730 "只用 VBUS LDO" 接法 | datasheet 全文 grep: LDO_3V3 描述为 "Output of supply switched from VIN_3V3 or **VBUS LDO**", 但 **§9.2.2 例图用的是外部 3.3V 供 VIN_3V3**, **没有**只走 VBUS LDO 的示例 | datasheet 未给该接法示例, 照猜接线有烧机风险 | **推荐不上 TPS25730** (B5-1); 若要上, 走"加一颗 3.3V LDO"这条有例图的路径 | 有 TI EVM/参考设计原理图即可立刻确认 |
| 铰链段每 pin 载流 / 压降 / 发热 | 不在本单职责内, 且需要 FPC 厂商规格书 (0.5mm pitch FPC 单触点载流) | 属 ISS-091 结构侧核算 | 本单已把**铰链实际电流的 6 个场景**算清楚, 直接给 ISS-091 当输入 | 结构总工有 FPC 厂商规格书即可立刻出结果 |
| BQ25896 单价 / 交期 | 未联系任何供应商 (外发一律经 PM) | 外发需 PM 授权 | 标 [0数据], 走 PM 询价 | PM 授权询价即可 |
| `VBUS_DET` 跨铰链的**读数误差** (500kΩ 源阻抗) | 已按 MECH §5.2 第 5 条写明"必须 GND 夹持 + 距 USB 差分 ≥3mm", 但**量化误差需要实测** (主板侧输入阻抗未知) | 主板侧分压/ADC 采样电路还没定 | 规格里保留 1M+1M (MECH 已定口径), 误差等主板侧 ADC 电路定稿后再算 | 主板侧 ADC 电路定稿即可立刻算 |

---

## B6 自证复现命令

```bash
cd projects/smart_glasses

# (0) 本单产出 (2 个文件)
ls -l HW/CHARGE_BOARD_SPEC.md HANDOFF/2026-10-27_chargeboard_spec.md

# (1) ★列表格式自检: 13 列 / 80 行 / 引脚覆盖 == 声明 (一条命令跑完)
python3 - <<'PY'
import csv, io, collections
s = open('HW/CHARGE_BOARD_SPEC.md', encoding='utf-8').read()
i = s.index('```csv\n') + len('```csv\n'); j = s.index('\n```', i)
rows = list(csv.DictReader(io.StringIO(s[i:j])))
print('rows:', len(rows), '| 全部 13 列:', all(len(r)==13 and None not in r.values() for r in rows))
print('cols:', list(rows[0].keys()))
print('board:', dict(collections.Counter(r['board'] for r in rows)))
print('evidence:', dict(collections.Counter(r['evidence'] for r in rows)))
def pins(ref):
    out=set()
    for r in rows:
        for k in ('node1','node2'):
            v=r[k]
            if v.startswith(ref+' '):
                out.update(v[len(ref)+1:].split('+'))
    return out
tc, uchg, jchg = pins('J_TYPE_C'), pins('U_CHG'), pins('J_CHG')
EXP16 = {'A1','A4','A5','A6','A7','A8','A9','A12','B1','B4','B5','B6','B7','B8','B9','B12'}
print('J_TYPE_C 声明 16 == 引用', len(tc-{'shield'}), '->', (tc-{'shield'})==EXP16)
print('U_CHG 声明 24 == 引用', len(uchg), '->', {'pin%d'%i for i in range(1,25)} <= uchg)
print('J_CHG 声明 10 == 引用', len(jchg), '->', {'pin%d'%i for i in range(1,11)} <= jchg)
PY

# (2) ★官方原件 (全部 ti.com + usb.org, 无二手媒体)
mkdir -p /tmp/chg && cd /tmp/chg
curl -sSL -o bq25896.pdf   https://www.ti.com/lit/ds/symlink/bq25896.pdf
curl -sSL -o tps25730.pdf  https://www.ti.com/lit/ds/symlink/tps25730.pdf
curl -sSL -o usbc_spec.pdf "https://www.usb.org/sites/default/files/USB%20Type-C%20Spec%20R2.0%20-%20August%202019.pdf"
for f in bq25896 tps25730 usbc_spec; do pdftotext -layout $f.pdf $f.txt; done
file bq25896.pdf tps25730.pdf usbc_spec.pdf     # 三份都要是 PDF (不是 404 HTML)

# (3) USB-IF Table 3-5 (16p 脚位 + 三条 Note)
grep -n -A 40 "Table 3-5 USB Type-C Receptacle Interface Pin Assignments" /tmp/chg/usbc_spec.txt | head -60
grep -n "maximum shorting trace length should not exceed 3.5 mm" /tmp/chg/usbc_spec.txt
grep -n "shall be not connected unless required" /tmp/chg/usbc_spec.txt

# (4) USB-IF Table 4-24 (Rp 56k/22k/10k → 电流)
grep -n -A 12 "Table 4-24 Source CC Termination" /tmp/chg/usbc_spec.txt

# (5) BQ25896 引脚功能表 (1-24)
grep -n -A 120 "Pin Functions" /tmp/chg/bq25896.txt | head -130

# (6) BQ25896 寄存器默认值 (ICHG 复位 2048mA / IINLIM 复位 500mA) + I2C 地址 0x6B
grep -n -A 20 "Table 10. REG04" /tmp/chg/bq25896.txt
grep -n -A 20 "Table 6. REG00"  /tmp/chg/bq25896.txt
grep -n "I2C Address\|Slave Address" /tmp/chg/bq25896.txt | head

# (7) ILIM 公式 / KILIM 公差
grep -n "KILIM" /tmp/chg/bq25896.txt | head

# (8) TS 分压 Equation 2 + 阈值
grep -n -B2 -A 20 "RT2 =" /tmp/chg/bq25896.txt | head -40
grep -n "V(T1)\|V(T5)" /tmp/chg/bq25896.txt | head

# (9) TPS25730: VIN_3V3 电压窗 + 封装 + ADCIN 电流配置
grep -n "VIN_3V3" /tmp/chg/tps25730.txt | head
grep -n -A 20 "Table 8-6. ADCIN3 & ADCIN4 Sink Current Configuration" /tmp/chg/tps25730.txt | head -30

# (10) ★关键复算 (TS 分压 + ILIM + 纹波) —— 决定 "铰链到底过多少电流"
python3 - <<'PY'
VREGN=5.0; RT1=5240.0; RT2=30310.0
def vts(rth):
    par=1/(1/rth+1/RT2); return VREGN*par/(RT1+par)
print("TS @0C  =", round(vts(27280),4), "V =", round(vts(27280)/VREGN*100,2), "%  (datasheet V(T1)=73.25%)")
print("TS @60C =", round(vts(3020),4),  "V =", round(vts(3020)/VREGN*100,2),  "%  (datasheet V(T5)=34.375%)")
for r in (390,300,260):
    lo,ty,hi = 320/r, 355/r, 390/r
    print(f"R_ILIM={r} -> IINMAX {lo:.2f}/{ty:.2f}/{hi:.2f} A -> ICHG~{lo*0.822:.2f}/{ty*0.822:.2f}/{hi*0.822:.2f} A")
print("REG04 复位默认 ICHG = 2048 mA  → 不装 R_ILIM 时铰链会过 2.05A (超 1.5A 设计点 1.37x)")
VBUS,VBAT,fs,L = 5.0,3.7,1.5e6,2.2e-6; D=VBAT/VBUS
print("IRIPPLE =", round(VBUS*D*(1-D)/(fs*L),3), "A @2.2uH ;", round(VBUS*D*(1-D)/(fs*1e-6),3), "A @1.0uH")
PY

# (11) 本单**没有**改任何生成物的证明 (与 git 无关, 直接比对内容指纹)
grep -c "P10" HW/netlist_v1.csv        # 应为 0 (网表里还没有 P10 页, 本单没落)
ls HW/ | grep -E "netlist_v1.csv|SCHEMATIC_V1.md|BOM_v1.csv"   # 这 3 个文件本单没动
git -C . status --porcelain 2>/dev/null | head   # 若有 git: 只应看到 2 个新增文件
```

---

*交接单结束。起草 hw-lead 2026-10-27。规格正文见 `HW/CHARGE_BOARD_SPEC.md`。*
