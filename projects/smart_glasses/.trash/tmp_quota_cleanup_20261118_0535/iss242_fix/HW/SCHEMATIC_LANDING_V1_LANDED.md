# ★★原理图侧落表记录 v1 (★ISS-220 · 2026-11-16 · 硬件总工 (hw-lead) 执行★)★★

> ★**性质**: ★**这是【执行记录】** ⇒ ★**网表 / 脚表 / BOM / 原理图 (.kicad_sch) / SPEC.json / CHARGE_BOARD_SPEC.md / 生成器 都真改了** ⇒ ★**与之配套的作业包 `HW/SCHEMATIC_LANDING_WORKPACKET_V1.md` (★"要改成什么"★) 与本文件 (★"改没改、改成什么、跑出来什么"★) 必须成对读** ★
> ★**单号**: ★**ISS-220** · ★**owner**: hw-lead · ★**verify_by**: main · ★**上游**: ★**ISS-217 交卷的作业包 `HW/SCHEMATIC_LANDING_WORKPACKET_V1.md`** (28 条作业条目 × 8 栏齐) · ★**规格页**: `HW/NETLIST_SELF_CONSISTENCY_SPEC.md` (★新增 §5.3 落表状态★)
> ★**边界 (★本单逐条自查过★)★**: ★**没碰** `HW/PCB/demo_mainboard.kicad_pcb` / `HW/PCB/demo_mainboard.kicad_pro` (★md5 逐字节不变★) · ★**没碰 PCB 布线 / 布局 / 板框** (★一行板都没重出★) · ★**没改** `MECH/` / `SW/` / `state/issue_log.yaml` / `PROJECT_TRACKER.md` §0 / `state/outbox/` / 别人的分片 (★`state/fragments/{pm,sw,mech}.yaml` 一个字节没碰★) · ★**没代拍** V-1~V-6 里任何一条** ★
> ★**零外发**: ★**本单未发任何邮件 / 询价 / 问询 / 采购 / 原厂问询** ⇒ ★**本单实物 [实测] = 0 条** (★板与屏不在本机★) ⇒ ★**凡是标 [实测] 的, 一律是"本机脚本 / 本机文件实读"★ ⇒ ★**凡是 [官网] 的, 一律是引用项目库内已存的一手件 (TI / ON Semi / 官方 datasheet 抽取文本), 本单没有新建任何外发动作★** ★

---

## 0. ★★一句话结论 + 前后对比★★

★★**落表结果**: ★**28 条作业条目里, 6 组真源改动真落进了盘上 (d1 / d6 / d10 方向修正部分 / d11+#5 / #1+补差A 的字段基建 / #7 核验 + #8 并入 d10), 其余 22 条全部【BLOCKED】并写明卡在谁 / 卡在哪一条 V** ⇒ ★**没有一条写"待定"** ★

| 指标 | 落表前 | 落表后 | 怎么量的 |
|---|---|---|---|
| ★**`--expect-resolved` 的「未落表条数」** ★ | ★**50** ★ | ★**29** ★ | ★**`python3 HW/check_netlist_selfconsistency.py --expect-resolved`** ★ |
| ★**翻面判据 R1 / R6 / R11** ★ | ★**全红** ★ | ★**全绿** ★ | 同上 (逐条看输出) ★ |
| ★**翻面判据 R10** ★ | ★**4 条红** ★ | ★**1 条红** ★ (★档位那条仍 BLOCKED 于 V-4★) ★ | 同上 ★ |
| ★**翻面判据 R2 / R3 / R4 / R5 / R7 / R8 / R9** ★ | ★**红** ★ | ★**红 (未动)** ★ | ★**全部 BLOCKED, 原因见 §3** ★ |
| ★**现状守卫 `EXPECT` 锚点条数** ★ | ★**154** ★ | ★**160** ★ (★+6 条正向锚点, ★**一条未减**★) ★ | `python3 HW/check_netlist_selfconsistency.py --emit-anchors \| wc -l` ★ |
| ★**网表行数 / 脚表行数 / BOM 行数** ★ | ★**513 / 584 / 218** ★ | ★**513 / 584 / 218** ★ (★零增零删 ⇒ 门禁锚点的行号全部不变★) ★ | `wc -l` ★ |

★★**★"落表不许靠删条目 / 改判据达成"的自证★**: ★**R1~R11 十一条翻面判据的代码一个字没改** (`HW/check_netlist_selfconsistency.py` 的 `check_resolved()` 与落表前逐字相同, ★只改了 `EXPECT` 里的【现状断言】与 `--selftest` 的【突变方向】★) ⇒ ★**"未落表条数 50 → 29" 是缺陷真的被修掉 21 条, 不是判据被放松★** ★

---

## 1. ★★已落表条目 · 逐条 (★改了哪个真源的哪一行 · 改前/改后字面值 · 落表后跑的命令与输出行 · 证据等级★)★★

### ★★1.1 · d1 · I2C_A 上拉 (★R1 转绿★)★★

| 项 | 内容 |
|---|---|
| ★**真源文件 · 行号** ★ | ★**`HW/SCHEMATIC_V1_SPEC.json`** · `connections[]` 里 ★**`id == "B-01"` (idx 20)** 与 ★**`id == "B-02"` (idx 21)** 的 ★**`level` 键与 `imp` 键** (★**不碰网表** — 网表是产物★) ★ |
| ★**改前 (字面)** ★ | `B-01`: `level="3.3V"` · `imp="上拉 4.7k 到 3.3V (灌 702µA, t_r=2.38µs@100pF)"`<br>`B-02`: `level="3.3V"` · `imp="上拉 4.7k 到 3.3V"` |
| ★**改后 (字面)** ★ | `B-01`: `level="1.8V"` · `imp="上拉 2.2k 到 1.8V (RAIL_VDD_1V8_IO, 灌 0.64mA @VOL=0.4V, t_r=186ns@100pF / 559ns@300pF)"`<br>`B-02`: `level="1.8V"` · `imp="上拉 2.2k 到 1.8V"` |
| ★**落表后产物 (逐字)** ★ | 表A ★**L167** `value` = `上拉 2.2k 到 1.8V (RAIL_VDD_1V8_IO, 灌 0.64mA @VOL=0.4V, t_r=186ns@100pF / 559ns@300pF)` (★行号未变★)<br>表A ★**L168** `value` = `上拉 2.2k 到 1.8V` (★行号未变★)<br>表A L167/L168 的 `note` 同步从 `电平 3.3V; 阻抗 上拉 4.7k 到 3.3V…` 变成 `电平 1.8V; 阻抗 上拉 2.2k 到 1.8V…` ★ |
| ★**跑的命令 + 输出行** ★ | `python3 state/gen_netlist.py` (rc=0) ⇒ ★**表A 只有 L167/L168 两行的 value+note 变, 其余 511 行逐字节不变** ★<br>`python3 HW/check_netlist_selfconsistency.py --expect-resolved` ⇒ ★**R1 的 10 条红全部消失** (★落表前 10 条: 「仍有 2 行写着『4.7k 到 3.3V / 2.38µs』」+ B-01/B-02 的 level/imp 4 条 + 表A L167/L168 2 条 = 10 条; 落表后 R1 段一条不剩★) ★ |
| ★**证据等级** ★ | ★**[实测]** ★SPEC.json 与表A 的逐字 (★2026-11-16 02:3x 本机实读 + 生成器实跑★) · ★**[实测]** `HW/PCB/FET3572C_PIN_TABLE.csv` 的 P2_31/P2_33 电压域 = `1.8V` (★SoM 厂 IO 域表★) · ★**[推算]** 灌流 (1.8−0.4)/2.2k = 0.64mA · t_r = 2.2k×100pF×0.847 ≈ 186ns · ★**[0数据]** SoM I2C 脚 abs-max (★不阻塞: SoC 域已由厂表锁死 1.8V★) ★ |

### ★★1.2 · 补差A / #1 · `imp` 一个字段混着用 ⇒ 字段拆分 (★字段基建已落 · 值迁移仍卡 V-1★)★★

| 项 | 内容 |
|---|---|
| ★**真源文件 · 行号** ★ | ① ★**`HW/SCHEMATIC_V1_SPEC.json`** · ★**26 条 `connections` 新增 `z_diff` 键** (★A 组 20 条 + `A-11`/`A-12` + `B-01`/`B-02`/`B-09`/`B-19` + `B-21`/`B-22`★)<br>② ★**`state/gen_netlist.py`** · ★**`conn_row()` 的 ★**L784 (取值优先级) 与 ★**L787 (note 阻抗栏) ★**+ 其 docstring (L770-L782) ★ |
| ★**改前 (字面)** ★ | ① `connections[*]` **没有** `z_diff` 键; ② `v = value if value is not None else (c.get("imp") or c.get("level") or "")` · `note = (f"方向 …; 阻抗 {c.get('imp','')}; "…)` |
| ★**改后 (字面)** ★ | ① `z_diff` 取值: ★**A 组 20 条 (`A-01`~`A-10`/`A-13`~`A-22`) = `"100Ω ±10%"` ★ (★与原 `imp` 逐字相同, 迁移时删 `imp` 即可★) · `A-11`/`A-12` (单端) = `""` · `B-01`/`B-02`/`B-09`/`B-19` = `""` · ★**`B-21`/`B-22` = `"90Ω ±15% 受控阻抗"`** ★ (★`[官网]` ON Semi AND8074/D: USB 双绞线特性阻抗 90Ω ±15%★) · ② `v = value if value is not None else (c.get("imp") or c.get("z_diff") or c.get("level") or "")` · `note = (f"方向 …; 阻抗 {c.get('imp') or c.get('z_diff','')}; "…)` |
| ★**跑的命令 + 输出行** ★ | `python3 state/gen_netlist.py` (rc=0) ⇒ ★**网表产物逐字节不变** (★A 组 20 条 NET 行 value 仍 `100Ω ±10%`; B 组 4 条仍原值; C 组 11 条 `imp` 键本来就不存在 ⇒ 仍落到 `level`; ⇒ 表A 的 8 行差异与本条无关, 全是 d10/d11/d1 的改动★) ★<br>`python3 state/check_netlist.py` ⇒ ★**`✅ 全过 — 原理图 V1.1 可进交叉评审`** (★判据 5「A 组阻抗逐条对照规格」仍然逐条在跑, ★因为 A 组的 `imp` 一个都没清★) ★ |
| ★**★为什么 A 组 20 条的 `imp` 这次不清★** ★ | ★**作业包 补差A ⑤ 说「A 组 20 条 `imp` → 清空」, 但清空之后 `state/check_netlist.py` 判据 5 的 `want = spec_imp.get(cid, "")` 会变成空串 ⇒ 那 20 条**永远被 skip** ⇒ ★**判据覆盖从 20 行掉到 0 行 = 判据被静默放松** ★**而 `state/check_netlist.py` 不在本单的允许改动清单里** (★作业包 ④ 栏没点它★) ⇒ ★**⇒ 本单只落【字段基建 + 数据】, 清空 `imp` 必须与 `check_netlist.py` 判据 5 的同步改判据同趟做 (作业包 补差A ⑦ 自己写的就是这句)★★** ★ |
| ★**证据等级** ★ | ★**[实测]** 57 条 `connections` 全表枚举 (★本机脚本实读★) · ★**[实测]** `state/gen_netlist.py` L770-L787 逐字 · ★**[官网]** ON Semi AND8074/D 的 90Ω ±15% · ★**[推算]** 「改动面 = 2 行 / 1 个文件 + 26 个 JSON 键, 且 A 组产物逐字节不变」的推导 ★ |

### ★★1.3 · d6 · CONN_LIGHT 21p vs 22p + P9 页的通道数 / 堆叠账 (★R6 转绿★)★★

| 项 | 内容 |
|---|---|
| ★**真源文件 · 行号** ★ | ★**`state/gen_schematic_pages.py`** ★**`PAGES["P9"]` 的 NARRATIVE 手写字符串 (★L143-L149 那一段★)** + `PAGES["P9"]` 副标题 (L41) + `PAGES["P5"]` 副标题 (L37) + P5 正文 (L100) + P6 正文 (L109) ★**★后面这 3 处是【同源残留】(作业包 d6 ⑤ 没点名, 但与 P9 同属【页正文 vs 网表】矛盾族), 一并收口并在 §3.4 登记★** ★ |
| ★**改前 (字面)** ★ | ① `⇒ **4 组跨铰链通道**:` ② `  2. \`CONN_USB\` (**4p@0.5mm**) — USB 2.0 差分 (**烧录/调试口唯一通路**) + 独立回流地 + 1 预留` ③ `  3. \`CONN_CAM\` (**18p@0.5mm**) — pin1/2 = CSI CK · … · **pin18 = 独立回流地**` ④ `  4. \`CONN_LIGHT\` (**1×21p@0.5mm**) — pin1/2 = DSI CK · … · 21 = 5V 预留 (待 JBD)` ⑤ 堆叠账 `堆叠 (10+4+18+21)×0.5 = **26.5mm** vs 镜脚根部净高 **37.0mm** → **余 10.5mm**` |
| ★**改后 (字面)** ★ | ① `⇒ ★**1 组跨铰链 (J_CHG) + 3 条板内 FPC**★:` ② `  2. ~~\`CONN_USB\`~~ — ★**已删** (跨铰链 USB 座于 **2026-11-04 取消**; USB 2.0 差分不再跨铰链, 改走主板自带 Type-C + 板内走线; ★网表里 \`count(ref==CONN_USB) == 0\`★)` ③ `  3. \`CONN_CAM\` (**31p@0.3mm · 板内 FPC 座**, Radxa Camera 4K, 座 HIROSE FH35C-31S-0.3SHW(50); ★**它不是跨铰链链路**★) — pin1 = GND · 2/3 = CSI D0_D3 N/P · … · 30/31 = LIGHT_5V` (★**pin map 按脚表 31 行逐条抄, 不是照抄旧的 18p map★) ④ `  4. \`CONN_LIGHT\` (**1×22p@0.5mm**, 座 HIROSE FH12-22S-0.5SH(55), ★板内 FPC 座★) — pin1 = GND · 2/3 = DSI D0_D1 N/P · … · 20/21/22 = GND (回流; ★**pin21/pin22 是地脚, 不是『5V 预留』**★)` ⑤ 堆叠账 `★**铰链区高度预算 (★口径 = 结构侧现行值, 本页不自带第二个堆叠数★)**: 跨铰链只剩 **1 组** (\`J_CHG\` 10p), 触点区 **0.5mm pitch** → ★**FPC 带宽口径见 \`MECH/HW_CROSS_REVIEW_TRIAGE.md\` 第 08 项 STK-P9** … vs 镜脚根部净高 **38.00mm** (★\`MECH/cross_review_check.py\` 锁死值; ★**37.0 是已作废的叠放模型算式 (22+12+3), 不许再用**★) ⇒ ★**余量按结构侧现行口径核算 (★数值归 MECH + 项目总工, 待 V-5 裁决; ★本页不自带第二个数★)**★ ✅` |
| ★**跑的命令 + 输出行** ★ | `python3 state/gen_schematic_pages.py` (rc=0) ⇒ ★**`HW/SCHEMATIC_V1.md` 重出 (P9 页 8 行器件表 + 新正文)★**<br>`python3 HW/check_netlist_selfconsistency.py --expect-resolved` ⇒ ★**R6 的 3 条红 (「P9 页正文里还有『CONN_LIGHT 1×21p@0.5mm』」/「没有『1×22p@0.5mm』」/「堆叠算式还在用 CONN_LIGHT=21p」) 全部消失** ★<br>`python3 state/check_netlist_pins.py` ⇒ ★**`✅ 全过 —— 每个针脚归属唯一` (★脚表 CONN_LIGHT 仍 22 行 / CONN_CAM 仍 31 行, ★行数没动★)** ★ |
| ★**★为什么堆叠【数值】没落★** ★ | ★**V-5 的硬要求**: 「★**本页不许再自带一个堆叠数**, 改成【引用】结构侧口径 + 写清『净高 38.00』⇒ ★**宁可不写数, 也不写第二个错数**★」 ⇒ ★**本单照办: 只写 38.00mm 这个 MECH 锁死分母 + 引用口径来源, 余量数值留给 V-5 (MECH + 项目总工)★** ★ |
| ★**证据等级** ★ | ★**[实测]** `state/gen_schematic_pages.py` 改前改后逐字 · 脚表 `count(ref==CONN_LIGHT)==22` / `count(ref==CONN_CAM)==31` (★本机实跑★) · 表A L237/L290 的 value 逐字 · ★**[实测]** `MECH/cross_review_check.py:64` 逐字「37.0 是已作废的叠放模型算式 … 现行是锁死的腔体净高 38.00」 · ★**[官网]** 官方 RPi CM5IO / Pi5 DISPLAY 座封装 = Hirose FH12-22S-0.5SH(55) ⇒ **22p 是真值** · ★**[推算]** 「跨铰链只剩 1 组 ⇒ 堆叠算式 (10+4+18+21)×0.5 的四个输入里三个已作废」 ★ |

### ★★1.4 · d10 · CHARGE_BOARD_SPEC 的 ICHG/IIN 系数方向 (★★R10: 4 条红 → 1 条红 · 档位本身仍卡 V-4★)★★

| 项 | 内容 |
|---|---|
| ★**真源文件 · 行号** ★ | ① ★**`HW/CHARGE_BOARD_SPEC.md`** · ★**L182 (表头) / L184 (390Ω 行) / L185 (300Ω 行) / L186 (260Ω 行) / L320 (§3.4 公式) / L325-L329 (§3.4 场景①~⑤) / L397 (充电电流接口表) / L536 (§7 清单的 R_ILIM 行) / L551 (§7 清单的 J_CHG 行) / L711-L712 (§7 末尾的自检脚本)** ★<br>② ★**`state/gen_netlist.py`** · ★**L514-L516 (R_ILIM 的 `add()` 源注释块) / L520 (R_ILIM 的 value) / L522-L528 (R_ILIM 的 note) / L530 (R_ILIM 第 2 行的 value) / L399 (BAT_CHG 铰链载流行 note)** ★<br>③ ★**`state/p10_rows.json`** · ★**row 45 (P10 整页的 J_CHG 行 note)** ★★**★注意: 作业包 d10 ④ 栏把这一行记成「`state/gen_netlist.py` 的 J_CHG 那条 `add()`」, 但★**P10 整页的行数据真源其实是 `state/p10_rows.json`**★ (★`state/gen_netlist.py:1348-1359` 的 `build_p10_json()` 只做加载 + 门禁★) ⇒ ★**本单改的是 p10_rows.json (★改源, 不是改产物★)★★** ★ |
| ★**改前 (字面)** ★ | ① L182 `CC 段电池电流上限 (×Vbat/Vbus/η ≈ 0.822)` · L184 `0.67 / 0.75 / **0.82 A**` + `**~0.75 A**` + `单 pin 0.411A ≤ 0.5A 触点天花板, 余量 1.22×` + 用途 `★★**本规格推荐值**` · L185 `0.88 / 0.97 / 1.07 A` + `单 pin 0.534A` · L186 `1.01 / 1.13 / 1.23 A` · L320 `ICHG ≈ IIN × (VBAT / VBUS) / η … **ICHG ≈ 0.822 × IIN**` · L711 `lo*0.822` · 场景① `**~0.41 A** / **3.7×**` · 场景②③ `**~0.67-0.82 A** / **1.8-2.2×**` · 场景④ `**~1.01-1.23 A** / **1.2-1.5×**` · 场景⑤ `**~0.88-1.07 A**` + `单 pin 0.534A`<br>② `390Ω ±1% (IINMAX ≈1.00A · ICHG ≈0.82A · 单 pin 0.411A)` ×2 · note 里 `★★V1.7 按 ISS-091 结构核算定 **470Ω**` + `0.411A/触点 余量 1.22×` + `定为 390Ω (ICHG 0.82A / 单 pin 0.411A / 充电 ~29min)` + `单 pin 0.534A` + `皮肤侧仍 42.14°C … ⇒ 不能再抬电流`<br>③ `充电电流跨铰链: J_CHG pin1/pin2 双 pin 并联 (每 pin ≤0.75A); …` |
| ★**改后 (字面)** ★ | ① L182 `CC 段电池电流上限 (ICHG/IIN = η·Vbus/Vbat = **1.216 @3.70V** / **1.071 @4.20V**)` · L184 `0.997 / 1.107 / **1.216 A**` + `**~1.1 A**` + `单 pin **0.608A** (pin1/pin2 双 pin 并联) > **0.50A 触点工作上限 21.6%** ⇒ **本档不成立**; 候选档位见 \`DECISION_PENDING_2026-11-16.md\` §3 (老板待拍项, ★**本单不代拍**★)` · L185 `1.298 / 1.437 / **1.581 A**` + `~1.4 A` + `单 pin **0.791A**` · L186 `1.496 / 1.657 / **1.824 A**` + `~1.7 A` + `单 pin **0.912A**` · L320 `buck 功率守恒 \`VBUS·IIN·η = VBAT·ICHG\` ⇒ \`ICHG ≈ IIN × η × (VBUS / VBAT)\` … **ICHG ≈ 1.216 × IIN** (VBAT=3.70V) / **1.071 × IIN** (VBAT=4.20V)` · L711 `lo*1.216` (+ 新增 `@4.20V ~{lo*1.071:…}` 与 `单 pin(2 并联)@3.70V max {hi*1.216/2:.3f} A`) · 场景① `**~0.61 A** / **2.5×**` · 场景②③ `**~1.00-1.22 A** / **1.2-1.5×**` · 场景④ `**~1.50-1.82 A** / ❌ **0.8-1.0× (已到/超 1.5A 设计点)**` · 场景⑤ `**~1.30-1.58 A**` + `单 pin **0.791A**`<br>② `390Ω ±1% (IINMAX ≈1.00A · ICHG ≈1.22A · 单 pin 0.608A ⇒ 超 0.50A 工作上限 21.6% · 档位待 V-4 裁决)` ×2 · note 改成 `★★★**方向修正 (ISS-214 d10 · ISS-220 落表 2026-11-16)** … ★**旧口径写的 (VBAT/VBUS)/η = 0.822 是它的倒数** ⇒ …『ICHG 0.82A / 单 pin 0.411A / 余量 1.22×』**全部作废**★` + `★★**V1.7 (470Ω) 已作废** (V1.8 起改 390Ω; ★**V1.9 终值待 V-4 裁决**)★` + `★★**390Ω 档真值** … **单 pin 0.608A > 0.50A 触点工作上限 21.6%** ⇒ **390Ω 档不成立, 档位待 V-4 裁决**` + `300Ω 档单 pin **0.791A** / 260Ω 档单 pin **0.912A** ⇒ 均判死` + `★**皮肤侧『42.14°C / 不能再抬电流』那条结论是在 0.822 系数下算的** ⇒ 按 1.216 系数, 电芯内阻发热从 114mW 升到 148mW (0.10Ω × 1.216²) ⇒ **该温度数不可信, 必须由结构总工用 MECH/HINGE_POWER_CALC.md 重算 (ISS-091 地界)**★`<br>③ `充电电流跨铰链: J_CHG pin1/pin2 双 pin 并联 (★每 pin **额定 0.75A / 工作上限 0.50A** (ISS-099: FH12-10S-0.5SH(55) 单触点额定 ≥0.5A; 70% 降额条款只针对全部触点同时导通, 本工况不适用)★); ★**按 ICHG/IIN = 1.216 真值, 390Ω 档单 pin = 0.608A > 0.50A 工作上限 21.6% ⇒ 档位待 V-4 裁决**★; …` |
| ★**跑的命令 + 输出行** ★ | `python3 state/gen_netlist.py` (rc=0) ⇒ ★**表A L47/L48 的 value + L47 的 note 变, L16 的 BAT_CHG note 变, L497 的 J_CHG note 变 (★共 4 行, 行号未变★)** ★<br>`python3 state/gen_bom.py` ⇒ ★**BOM L97 的 value 同步 (★行号未变★)** ★<br>`python3 HW/check_netlist_selfconsistency.py --expect-resolved` ⇒ ★**R10 从 4 条红降到 1 条红** ★<br>★**落表前 4 条**: `CHARGE_BOARD_SPEC 里还有 0.822` / `没有 1.216 / 1.071 这两个真值` / `表A 行 47 的 R_ILIM value 还写着单 pin 0.411A` / `表A 行 48 的 …` + `390Ω 档单 pin 载流上限 = 0.608 A > 0.5 A 触点额定 ⇒ R_ILIM 档位没重新定`<br>★**落表后剩 1 条**: ★**`390Ω 档单 pin 载流上限 = 0.608 A > 0.5 A 触点额定 ⇒ R_ILIM 档位没重新定`** ★(★这条只能靠 V-4 裁档位才能转绿, ★本单不许代拍★) ★ |
| ★**证据等级** ★ | ★**[官网]** TI **BQ25896** datasheet **SLUSC76C** (★ILIM 脚原话「IINMAX = KILIM/RILIM」· KILIM 320/355/390 AΩ · 效率 92.5%@2A / 90.5%@3A ⇒ η 取 0.90 保守值★) · ★**[实测]** CHARGE_BOARD_SPEC 改前改后逐字 + 表A L47/L48/L497 + BOM L97 + `MECH/check_demo_struct_truth.py` G2.8 (★它按物理真值判 1.216/1.071, 与本单一致★) · ★**[推算]** 功率守恒全表 (★1.2162@3.70V / 1.0714@4.20V; 390Ω ⇒ 单 pin 0.608A / 300Ω ⇒ 0.791A / 260Ω ⇒ 0.912A; 电芯内阻发热 114mW → 148mW★) · ★**[0数据]** 铰链段实际接触电阻 / 温升 / 载流实测 (★无样件★) · ★**[0数据]** 皮肤侧 42.14°C 这个数 (★它是按错系数算的, 本单**没有**重算, 只标了不可信并派给 mech-lead★) ★ |

### ★★1.5 · d11 / #5 · π 滤波对地电容 `C_VBUS_GND` 的 board 归属 (★R11 转绿★)★★

| 项 | 内容 |
|---|---|
| ★**真源文件 · 行号** ★ | ★**`state/gen_netlist.py`** · ★**`CHG_BOARD_REFS` 白名单 (★L121-L133★)** ★**加一行 `"C_VBUS_GND",`** (★与 `"C_VBUS_OUT"` 同列★) ★ |
| ★**改前 (字面)** ★ | `CHG_BOARD_REFS = { "D_CHG_LED", "Q_CHG_LED", "R_CHG_LED", "C_REGN", "R_ILIM", "J_TYPE_C", "D_ESD_TC", "FB_VBUS", "C_VBUS_IN", "C_VBUS_OUT", "U_CHG", … }` ⇒ ★**`C_VBUS_GND` 不在白名单 ⇒ 落进 `board_for()` 的默认分支 ⇒ `MAIN_PCB`** ★ |
| ★**改后 (字面)** ★ | `CHG_BOARD_REFS = { …, "C_VBUS_IN", "C_VBUS_OUT", ★"C_VBUS_GND",★ "U_CHG", … }` (★带注释: π 滤波后级【对地】电容, 物理上必须在充电板 (与 C_VBUS_OUT 同板)★) ★ |
| ★**落表后产物 (逐字)** ★ | 表A ★**L10** board `MAIN_PCB` → ★**`CHG_BOARD`** ★ (行号未变)<br>表A ★**L12** board `MAIN_PCB` → ★**`CHG_BOARD`** ★ (行号未变)<br>脚表 ★**L148/L149** (`C_VBUS_GND.1/.2`) board `MAIN_PCB` → ★**`CHG_BOARD`** ★ (行号未变)<br>BOM ★**L51** 的板列 `镜脚主 PCB` → ★**`镜框充电板`** ★ (行号未变) ★ |
| ★**跑的命令 + 输出行** ★ | `python3 state/gen_netlist.py` → `python3 state/gen_netlist_pins.py` → `python3 state/gen_bom.py` (全 rc=0)<br>`python3 HW/check_netlist_selfconsistency.py --expect-resolved` ⇒ ★**R11 的 3 条红全部消失** (★落表前: 「网 VBUS_5V_CHG 上还有 1 行的 board 列不是 CHG_BOARD (行/board = [(12, 'MAIN_PCB')])」+「C_VBUS_GND 的 board 列仍是 'MAIN_PCB' (表A 行 10)」+「(表A 行 12)」; 落表后 R11 段一条不剩★) ★ |
| ★**★白名单双向对账 (★#5 ⑤ 第 ② 步★) 实跑结果: ★不通过, 已登记★** ★ | ★**方向A (网表 board=CHG_BOARD 但 §7 清单里没有) = 15 个 ref**: `C_VBUS_GND` · `C_VBUS_OUT` · `D_CHG_LED` · `D_TVS_VBUS` · `Q_CHG_LED` · `R_CHG_LED` · `R_PU_CHG_STAT` · `R_TS_TOP` · `TP_CHG_STAT` + 6 个网名型 (`NET_BAT_PROT` / `NET_CHG_STAT` / `NET_PWR_GOOD` / `NET_TS_BAT` / `NET_USB_CC1` / `NET_USB_CC2`)<br>★**方向B (§7 清单里有、但网表里 board 不是 CHG_BOARD 或根本没有这个 ref) = 16 个**: `J_CHG` (HINGE) · `R_NTC_BAT` (MAIN_PCB) + 14 个网表里**根本不存在的位号** (`R_VDET_TOP` / `R_VDET_BOT` / `USB_D_P_CHG` / `USB_D_N_CHG` / `R_TS1` / `R_TS2` / `C_VBUS_BULK` / `BAT_CHG` / `CHG_STAT` / `PWR_GOOD` / `TS_BAT` / `NC` / `USB_CC1` / `USB_CC2`)<br>★**⇒ 结论: ★**`HW/CHARGE_BOARD_SPEC.md` §7 的清单与现行网表是两个版本**(★§7 是 P10 整页的手抄快照, 没跟着网表走★) ⇒ ★**⇒ 作业包 #5 ⑤ 的「双向对账」这一步在现状下【不可能通过】, 必须连同 #6/补差C 的 π 滤波真值拓扑一起重做 §7 (★归充电板整机阶段那一趟, 本单不代做★)** ⇒ ★**本单只把【白名单这个结构性根因】修掉 (漏一颗就默认落 MAIN_PCB 的坑), 对账结论登记给 main** ★ |
| ★**证据等级** ★ | ★**[实测]** 表A L9-L13 / 脚表 L148/L149/L154/L155 / BOM L51 改前改后逐字 · `state/gen_netlist.py` 的 `CHG_BOARD_REFS` 与 `board_for()` 源码与注释逐字 · ★**[实测]** 双向对账脚本实跑 (★网表 CHG_BOARD 94 行 / 40 个 ref; §7 清单 80 行 / 41 个 ref; §7 里 board 列不是 CHG_BOARD 的 16 行★) · ★**[官方]** BQ25896「Place a 1-µF ceramic capacitor from VBUS to PGND and place it as close as possible to IC」 · ★**[推算]** 「白名单驱动 ⇒ 同型缺陷会持续往外冒 (R_VBUS_DET_1/2 已修过一次)」 ★ |

### ★★1.6 · #7 · `R_CHG_LED` 的转述与实跑不一致 (★已核验, 一个字没改★)★★

| 项 | 内容 |
|---|---|
| ★**真源文件** ★ | ★**无 (本条不落表)** ★ |
| ★**核验命令 + 输出行** ★ | `python3 -c "import csv;rows=list(csv.reader(open('HW/netlist_v1.csv',encoding='utf-8')));print([(r[0],r[4],r[12]) for r in rows[1:] if r[4] in ('R_CHG_LED','D_CHG_LED','Q_CHG_LED')])"` ⇒ ★**落表前与落表后两次实跑, 输出完全相同**: `[('', 'R_CHG_LED', 'CHG_BOARD'), ('', 'R_CHG_LED', 'CHG_BOARD'), ('', 'D_CHG_LED', 'CHG_BOARD'), ('', 'Q_CHG_LED', 'CHG_BOARD')]` ⇒ ★**整条充电灯链全在 CHG_BOARD, 转述的「R_CHG_LED 两端分属两块板」被证伪 ⇒ ★**本条一个字都没改 (★照转述改会把没坏的件改坏★)** ★ |
| ★**证据等级** ★ | ★**[实测]** 表A L508-L511 逐字 (board 列逐条实读) ★ |

### ★★1.7 · #8 · `R_ILIM` note 里的 V1.7 残留 "470Ω" (★已落表, 并入 d10★)★★

| 项 | 内容 |
|---|---|
| ★**真源文件 · 行号** ★ | ★**`state/gen_netlist.py`** · ★**L522-L528 (R_ILIM 那条 `add()` 的 note 字符串)** ★ |
| ★**改前 (字面)** ★ | `★★V1.7 按 ISS-091 结构核算定 **470Ω**: BQ25896 的 IINLIM 复位默认 **2048mA** [官方] (不装 = 铰链吃 ~1.68A); 结构总工核算 … **300Ω · ICHG 1.07A · 充电时皮肤侧 47.1°C 超 ISO 13732-1 的 43°C 红线** …; 470Ω · 0.68A · 39.9°C (充电 ~35min); 680Ω · 0.47A · 37.3°C. ★★★**V1.8 改 …**` ★**⇒ 同一条 note 里两个档位 (470Ω 与 390Ω) 并排★** ★ |
| ★**改后 (字面)** ★ | `★★**V1.7 (470Ω) 已作废** (V1.8 起改 390Ω; ★**V1.9 终值待 V-4 裁决**)★` ★**⇒ note 里不再有两个档位并排 (★历史推导过程保留, 但明确标作废★)** ★ |
| ★**跑的命令 + 输出行** ★ | `python3 state/gen_netlist.py` (rc=0) ⇒ ★**表A L47 的 note 变 (★与 d10 同一次改动★)** ★ |
| ★**证据等级** ★ | ★**[实测]** 表A L47 note 改前改后逐字 · ★**[推算]** 「两个档位并排 ⇒ 读者无法判断终值」的后果 · ★**[0数据]** V1.7 的 470Ω 当时是不是真做过 (★note 里保留了推导过程, 但推导本身有 470/680/300 三个候选 ⇒ 真值只有 V1.9 的 390Ω, 而 390Ω 现在又待 V-4 裁决★) ★ |

---

## 2. ★★落表后逐字重生成清单 (★不许手工编辑产物★)★★

| 序 | 命令 | rc | 产物 | md5 前 → 后 |
|---|---|---|---|---|
| ① | `python3 state/gen_netlist.py` | 0 | `HW/netlist_v1.csv` (★513 行, 零增零删★) | `c78f991283cc` → `13f59a43dbd3` |
| ② | `python3 state/gen_kicad_net.py` | 0 | `HW/netlist_v1.net` (★218 器件 / 153 网★) | `bbcd2e9aee84` → `978ab59e297e` |
| ③ | `python3 state/gen_netlist_pins.py` | 0 | `HW/netlist_v1_pins.csv` (★584 行, 零增零删★) | `4814617e22b5` → `a600afae493f` |
| ④ | `python3 state/gen_bom.py` | 0 | `HW/BOM_v1.csv` (★218 行, 零增零删★) | `c0b335e1601c` → `92b51580867d` |
| ⑤ | `python3 state/gen_schematic_pages.py` | 0 | `HW/SCHEMATIC_V1.md` (★9 页正文 + 器件表★) | `444daca54e21` → ★**见下**★ |
| ⑥ | `python3 state/gen_kicad_sch.py` | 0 | `HW/PCB/demo_mainboard*.kicad_sch` (★11 个文件 + `demo_mainboard_sch.net`★) | ★**★内容只变了 R_ILIM 的 Value/MPN 属性 (去 uuid 后逐行 diff 只有那 2 行), 其余是生成器每次重铸 uuid 的既有行为★** ★ |
| ⑦ | ★**没跑** ★ | — | ★**`HW/PCB/demo_mainboard.kicad_pcb` / `.kicad_pro` (★本单不许碰板★)** ★ | ★**`611b869e13518c3c023fb178f91a0075` / `3e504d2be83152e337949723e909be1b` ⇒ 逐字节不变** ★ |

★**★生成链幂等性先验 (★开工前实测, 保证"改产物"与"改源"分得清★)★**: ★**在动任何源之前, 先把 ①②③④⑤ 全跑一遍 ⇒ 5 个产物的 md5 一个字节都没变** ⇒ ★**⇒ 重跑生成器只可能反映真源改动, 不可能夹带生成器漂移★** ★

★**★改产物前的逐行对照 (★8 行, 行号零位移★)★**:
| 行 | 变化 | 属哪条 |
|---|---|---|
| 表A **L10** | board `MAIN_PCB` → `CHG_BOARD` | d11 |
| 表A **L12** | board `MAIN_PCB` → `CHG_BOARD` | d11 |
| 表A **L16** | note: `每 pin ≈0.75A, 1.27mm 排线` → 额定/工作上限 + 0.608A + 待 V-4 | d10 |
| 表A **L47** | value + note | d10 + #8 |
| 表A **L48** | value | d10 |
| 表A **L167** | value + note | d1 |
| 表A **L168** | value + note | d1 |
| 表A **L497** | note | d10 (J_CHG 行, 真源 = `state/p10_rows.json`) |
| 脚表 **L148/L149** | board | d11 |
| 脚表 **L192/L194/L197/L198** | note | d10 (BAT_CHG) |
| 脚表 **L329/L330** | value + note | d10 |
| BOM **L51** | 板列 `镜脚主 PCB` → `镜框充电板` | d11 |
| BOM **L97** | value | d10 |
★**⇒ 表A 8 行 + 脚表 8 行 + BOM 2 行 = 18 行, ★**其余 500+ 行逐字节不变**★** ★

---

## 3. ★★未落表条目 · 逐条 BLOCKED 于谁 (★不许留"待定"★)★★

| 项号 | 状态 | ★**BLOCKED 于** ★ | 需要谁拍 / 要做什么 | 为什么不能本单做 |
|---|---|---|---|---|
| ★**d2** ★ | ★**BLOCKED** ★ | ★**V-3** ★ (★+ 落表机制修正, 见下★) ★ | **项目总工 / 老板**裁 BAT_DET 分压比 (2.0M+1.2M 还是 2.0M+1.0M) | ★**d2 ③ 自己写明: 「把 DNP 翻成必装」若不定分压比, 照 1M+1M 贴上去就是 2.100V 过压 ⇒ **只翻 DNP 比现在更坏**★ ⇒ 裁 V-3 之前翻 DNP = 把过压件装上板 ★ |
| ★**d2 的改法修正 (★落表时发现的真源事实★)** ★ | ★**需写进下一批作业包** ★ | — | ★**落表那趟的 ⑤ 栏要改成: `state/gen_netlist.py` 的 `DEMO_DNP` 字典 (★现 L306-L327★) 里把 `R_BAT_DET_1` / `R_BAT_DET_2` / `C_DET_BAT` 三条摘掉, ★**不是**改 BAT_DET 段那些 `add()` 的 `dnp=` 参数 (★那个参数被 `add()` 里的 `if ref in DEMO_DNP: dnp = "DNP"` 覆盖, ★改了没用★)★** ★ | ★**作业包 d2 ⑤ 写的是「改那 4 条 `add()` 的 `dnp`」—— ★**本单实读源码: 那 4 条 `add()` 的 dnp 参数写的就是 `"必装"`, 真正把它们按成 DNP 的是 `DEMO_DNP` 白名单 (★网表 note 里的 `★DNP: 同上 (电池电压分压上臂)` 就是 `add()` 自动加的前缀★) ⇒ ★**作业包的改法落不了地, 必须改 DEMO_DNP★★** ★ |
| ★**d7** ★ | ★**BLOCKED** ★ | ★**V-3** ★ | 同上 | 分压比是 V-3 的内容; R2/R7 都靠它转绿 |
| ★**d8** ★ | ★**BLOCKED** ★ | ★**V-3** ★ | 同上 | note 里的漏电流数 (1.31µA @4.2V vs 1.40µA) 取决于下臂 1.2M 还是 1.0M |
| ★**#2** ★ | ★**BLOCKED** (并入 d8) ★ | ★**V-3** ★ | 同上 | 与 d8 同一处字符串, 不许改两遍 |
| ★**d3** ★ | ★**BLOCKED** ★ | ★**板只改一次的纪律** (★⇒ 与 d4 同批, 而 d4 卡 V-2★) ★ | **main** 派「板只改一次」那一趟, ★**同趟**: 网表加 `type=IC` 本体行 + 脚表 + BOM type + ★**板封装 `U_EN_SW` 的 `Value` 属性 (由 `state/gen_pcb_components.py:156` 取该 ref 的第一行自动刷)★** | ★**R3 的判据含「板封装 `U_EN_SW` 的 Value 不再是脚级功能串」⇒ 只改网表 ⇒ R3 转不了绿 ⇒ 且 ★**本体行必须排在 4 条 NET 行之前, 否则板的 Value 还是错的那句★**; 落表还会让 ★**表A 行号从 441 起全体 +1** (★门禁锚点要跟着改行号★) ⇒ ★**必须与板那一趟同批, 不能单独落★** ★ |
| ★**d4** ★ | ★**BLOCKED** ★ | ★**V-2** ★ (★ESD 方案二选一 + 型号 = 老板级选型★) ★ | **老板**裁 ESD 方案与型号 | ★**型号 = 选型 = 老板级; 且换 3 脚封装 + 挪位置 ⇒ 布线必须重跑 ⇒ 归「板只改一次」那一趟★** ★ |
| ★**d9** ★ | ★**BLOCKED** ★ | ★**V-2** ★ (★+ 板侧≤3.0mm★) ★ | 同上 | 与 d4 同一趟 (ESD 器件 + 位置) |
| ★**d5** ★ | ★**BLOCKED** ★ | ★**V-1** ★ (★USB 串阻: 22Ω 外部串阻 还是 0Ω 靠 SoM PHY 内部匹配★) ★ | **项目总工 / 老板**裁 V-1 | ★**R5 的判据是「NET 行 value 含 22Ω」⇒ 取 0Ω 就得改门禁 EXPECT ⇒ ★**这属于代拍, 本单不做★**; ★**但 90Ω 那个错值两种裁法都必须清掉, 已在补差A 里把字段拆好, V-1 一落就是两行改动★** ★ |
| ★**#1 / 补差A 的值迁移** ★ | ★**部分落表** ★ | ★**V-1** ★ | 同 d5 | ★**字段与数据已备好, 只差 B-21/B-22 的 `imp` 取 22Ω 还是 0Ω★** ★ |
| ★**#4 / 补差C 的 `J_CHG` 位号消歧** ★ | ★**BLOCKED** ★ | ★**ISS-199 (铰链结构) / ISS-202 (J_CHG pinmap)** ★ | **mech-lead + main** 排期 | ★**网表侧改 `J_CHG` → `J_CHG_FPC` 会牵动表A/表B/BOM/板四处位号 + P9 页 pin map + 结构开孔; 且 P9 页的 J_CHG pin map 与网表对不上 (★网表: 7=NC / 8=TS_BAT, 没有 5/6 的行; P9 页写 5=CHG_STAT / 6=PWR_GOOD / 7=VBUS_DET★) ⇒ ★**归那两个 issue 的地界★** ★ |
| ★**#6 / 补差C 的 π 滤波真值拓扑** ★ | ★**BLOCKED** ★ | ★**充电板整机阶段单 (V-7, main 派单)** ★ | **main** 派充电板那一趟 | ★**网表侧要把 `C_VBUS_OUT` 的【串联 100µF】去掉并统一成对地的 `C_VBUS_BULK`, 而 `C_VBUS_BULK` 这个位号现在**网表里根本没有** ⇒ 是一次拓扑级改动 + §7 清单重写 + §7.1 计数重算 ⇒ ★**作业包 ⑥ 栏自己写明「本条不在本单落表范围 (充电板整机阶段, 不进 demo 板)」★** ★ |
| ★**#3 / 补差B / V-6** ★ | ★**已落定** (★ISS-217 已落, 本单只需知会★) ★ | — | ★**无需签字** | ★**门禁 R9 阈值已是 3.0mm + 反向用例 `m_esd_threshold_5mm` 在跑 (★自检 19/19 里的一条★)★** ★ |

---

## 4. ★★落表后需要【板侧】同步的清单 (★只报告, 不许改板★)★★

★★**本单一个字节都没碰板** ★(`HW/PCB/demo_mainboard.kicad_pcb` md5 `611b869e13518c3c023fb178f91a0075` 与 `.kicad_pro` md5 `3e504d2be83152e337949723e909be1b` ★**逐字节不变**★; ★**板生成器一个都没跑**★) ⇒ ★**下列 6 项必须并进 main 派的「板只改一次」那一趟, ★否则网表与板会长期对不上★** ★

| # | 条目号 | 需要改板上的什么 | 定位 | 为什么必须改 |
|---|---|---|---|---|
| ★**B-1** ★ | ★**d11 / #5** ★ | ★**把 `C_VBUS_GND` 的封装从 demo 主 PCB 上拿掉** (★它现在还在板上, pad1→GND / pad2→VBUS_5V_CHG, 原点 (107.7, 42.5)★) | `HW/PCB/demo_mainboard.kicad_pcb` · 封装 `C_VBUS_GND` · ★**板生成器按 board 列过滤 ⇒ 重跑 `state/gen_pcb_netlist_board.py` 即自动消失** ★ | ★**网表/BOM 已改成 CHG_BOARD, 板还是 MAIN_PCB ⇒ 同一颗电容在两块板各有一份 ⇒ 装配会多贴一颗, 且主板那半边是死头支路★** ★ |
| ★**B-2** ★ | ★**d3** ★ | ★**板封装 `U_EN_SW` 的 `Value` 属性** 从 `EN 输入 (高=放行底板)` 改成器件身份描述 | 板文件 `U_EN_SW` 封装 (★4 焊盘, 原点 (135.3, 58.0) 附近★) · ★**`state/gen_pcb_components.py:156` 取该 ref 在网表里的第一行 ⇒ 网表加了本体行后重跑自动刷** ★ | ★**R3 的判据就是这条; 不改 ⇒ 投产包/盖印上板厂看到的是一句脚功能串★** ★ |
| ★**B-3** ★ | ★**d4 / d9** ★ | ★**`D_ESD_USB_D` 从 2 脚换 3 脚封装 (pin1=D+ / pin2=D− / pin3=GND)** ★ | 板文件 `D_ESD_USB_D` (★现 pads=2, pad1→`USB_D_P_SRC` / pad2→GND, 原点 (94.95, 21.80)★) · `state/gen_pcb_components.py` 封装表 | ★**R4 判据: 板上挂 D− 两张网的 ESD 位号数 ≥1 且 `D_ESD_USB_D` 焊盘数 = 3★** ★ |
| ★**B-4** ★ | ★**d4 / d9** ★ | ★**把 `D_ESD_USB_D` 挪到 `J_USB_C` 旁 ≤ 3.0 mm** (★现距 **47.99 mm**★) | 板文件 `D_ESD_USB_D` 原点 (94.95, 21.80) vs `J_USB_C` 原点 (140.00, 5.25) · `state/gen_pcb_routing.py` / `state/gen_pcb_netlist_board.py` | ★**R9 判据 (阈值 3.0mm, 按 ISS-085 规矩)★; ★**挪位置 ⇒ 布线必须重跑 ⇒ 必须与 B-3 同趟★** ★ |
| ★**B-5** ★ | ★**d4 / d9** ★ | ★**USB D− 那条路上补 ESD** (★现在板上挂 `USB_D_N_SRC` / `NET_USB_D_N_TYPEC` 的 ESD 位号数 = **0**★) | 板文件 · 4 个 ESD 位号 (`D_ESD_CAM` / `D_ESD_DEMO` / `D_ESD_LIGHT` / `D_ESD_USB_D`) 逐个查网 | ★**R4 判据: D− 侧必须有 ESD★ ⇒ **Type-C 是日常插拔口, 这是 4 条里唯一的"用了就可能坏"** ★ |
| ★**B-6** ★ | ★**#6 / 补差C** ★ | ★**充电板 π 滤波的位号与拓扑** (★`C_VBUS_BULK` 对地 / 去掉 `C_VBUS_OUT` 的串联 100µF★) | 充电板 (★本单不碰; 充电板不进 demo 板★) | ★**100µF 串在 BQ25896 的 DC 输入路径上 ⇒ 稳态充不了电 (整机阶段 P0)★ ⇒ 归充电板整机阶段单 (V-7)★** ★ |

---

## 5. ★★落表过程中的【发现】(★作业包本身有 3 处与真源对不上, 已登记★)★★

| # | 发现 | 影响 | 处置 |
|---|---|---|---|
| ★**F-1** ★ | ★**作业包 d2 ⑤ 说「改 BAT_DET 段那 4 条 `add()` 的 `dnp`」—— 改不动** ★ (★那 4 条的 dnp 参数本来就是 `"必装"`, 真正把 DNP 按下去的是 `state/gen_netlist.py` 的 `DEMO_DNP` 字典, ★`add()` 里 `if ref in DEMO_DNP: dnp = "DNP"` 会覆盖参数★) ★ | ★**照作业包做 = 白做, 而且会以为已经修好了★** | ★**本单不改作业包 (留给下一批落表时同步改), 已在本文件 §3 写明正确改法★; 已登记给 main ★** |
| ★**F-2** ★ | ★**作业包 d10 ④ 把「J_CHG 那条 `add()` 的 note」记成 `state/gen_netlist.py`, 但 P10 整页的行数据真源是 `state/p10_rows.json`** ★ (★`gen_netlist.py:1348-1359` 的 `build_p10_json()` 只做加载 + 门禁★) | ★**照作业包改 `gen_netlist.py` = 改不到那一行★** | ★**本单改的是 `state/p10_rows.json` (★改源, 不是改产物★), 并在此登记; ★**该文件不在作业包 ④ 栏点名的清单里, 是作业包的文件归属写错了★** ★ |
| ★**F-3** ★ | ★**补差A ⑤ 说「A 组 20 条 `imp` 清空」与 `state/check_netlist.py` 判据 5 冲突** ★ (★清空 ⇒ 判据 5 的 `want` 变空 ⇒ 那 20 条被 skip ⇒ 判据覆盖 20 行 → 0 行★) | ★**清空会让 `check_netlist.py` 的判据被静默放松 (而那文件不在本单允许改动清单里)★** | ★**本单只落字段基建 + 数据, 不清 `imp`; 已在 §1.2 写明"清空必须与判据 5 的同步改判据同趟做"★ ** |
| ★**F-4** ★ | ★**d10 的方向修正连带把「皮肤侧 42.14°C / 不能再抬电流」这条结论作废了** ★ (★它是按 0.822 系数算的; 按 1.216 系数, 电芯内阻发热 114mW → 148mW★) | ★**充电时皮肤温度这条安全结论现在没有可信数字★** (★ISO 13732-1 的 43°C 红线仍有效★) | ★**本单不在网表里写新温度数 (★没有 MECH 的模型就不许编★), 已在 note 里标"该温度数不可信, 必须由结构总工用 MECH/HINGE_POWER_CALC.md 重算"★; ★**已登记成 need 给 main/mech-lead (见交接单 B5)★** ★ |
| ★**F-5** ★ | ★**作业包 #5 ⑤ 的「白名单 ↔ §7 清单双向对账」在现状下不可能通过** ★ (★§7 是手抄快照, 与网表是两个版本: 16 个位号网表里没有, 15 个 CHG_BOARD 位号不在 §7 里★) | ★**#5 的最后一步闭不了★** | ★**已在本文件 §1.5 写明实测结果 + 归到 #6/补差C 的充电板整页那一趟; 登记给 main ★** ★ |

---

## 6. ★★受保护 md5 前后对照 (★交卷时逐条实测★)★★

| 文件 | 落表前 md5 | 落表后 md5 | 说明 |
|---|---|---|---|
| ★**`HW/PCB/demo_mainboard.kicad_pcb`** ★ | ★**`611b869e13518c3c023fb178f91a0075`** ★ | ★**`611b869e13518c3c023fb178f91a0075`** ★ | ★**逐字节不变 (★本单不许碰板★)★** ★ |
| ★**`HW/PCB/demo_mainboard.kicad_pro`** ★ | ★**`3e504d2be83152e337949723e909be1b`** ★ | ★**`3e504d2be83152e337949723e909be1b`** ★ | ★**逐字节不变** ★ |

★★**真源与产物的 md5 前后对照 (★每个要改的真源都留了 `.bak_iss220` 副本, 在 `state/.bak_iss220/`★)★★

| 文件 | 落表前 md5 | 落表后 md5 | 类别 |
|---|---|---|---|
| `HW/SCHEMATIC_V1_SPEC.json` | `33e841fafd5a863eafd3aaf6b38a3287` | `1e29b4cb48f9…` | ★**真源** (d1 + 补差A) ★ |
| `state/gen_netlist.py` | `fb596cc42a61f82d0aa3f0a679658fab` | `c69dff8723c3375fd089fee075d8f31c` | ★**真源** (补差A 2 行 + d10 + d11 + #8) ★ |
| `state/p10_rows.json` | `c2dc73fe1e9fbd8edec68828dec81c36` (★按"仅还原那一条 note"重建★) | `056c52699278fb3fbdcb39e5df6681f1` | ★**真源** (d10 的 J_CHG 行; ★作业包把文件归属写错了, 见 F-2★) ★ |
| `state/gen_schematic_pages.py` | `7a64c76169941ba93335105e9eee55da` | `fc63b5559ab0…` | ★**真源** (d6) ★ |
| `HW/CHARGE_BOARD_SPEC.md` | `b063dce0639166580009053220346802` | `9e2f21651b07…` | ★**真源** (d10) ★ |
| `HW/check_netlist_selfconsistency.py` | `7c6487a10683073fcc5f6a8584976a0c` | `5e387936738f…` | ★**门禁** (★只改 EXPECT 现状断言 + selftest 突变方向 + 追加 6 条正向锚点; ★R1~R11 判据与阈值一字未动★) ★ |
| `HW/NETLIST_SELF_CONSISTENCY_SPEC.md` | `2ef4677fe54d6cdf0ea29184e100bf47` | `8e0ac3f7e0ed…` | ★**规格页** (★锚点表重生成 + 已落表条目的现状逐字 + 新增 §5.3 落表状态★) ★ |
| `HW/SCHEMATIC_LANDING_WORKPACKET_V1.md` | `5e9daa2e1a696de77c9bf3609cb143de` | `0970113b9443…` | ★**作业包** (★已落表条目的 ② 栏加落表注记 + 新增 §8 落表状态★) ★ |
| `HW/netlist_v1.csv` | `c78f991283cc82d56c8e3dd31657c785` | `13f59a43dbd3…` | ★**产物** (★重跑生成器★) ★ |
| `HW/netlist_v1.net` | `bbcd2e9aee841a59324a74cc0ed9f450` | `978ab59e297e…` | ★**产物** ★ |
| `HW/netlist_v1_pins.csv` | `4814617e22b567d76164e56bc5e39dc8` | `a600afae493f…` | ★**产物** ★ |
| `HW/BOM_v1.csv` | `c0b335e1601c3e1ac1df41b8e6e7f033` | `92b51580867d…` | ★**产物** ★ |
| `HW/SCHEMATIC_V1.md` | `444daca54e2116aaf97f2e6501a74a0c` | ★**见 `md5sum HW/SCHEMATIC_V1.md`** ★ | ★**产物** ★ |
| `HW/PCB/demo_mainboard*.kicad_sch` (11 个) | ★**见 `state/.bak_iss220/*.kicad_sch.bak_iss220`** ★ | ★**见 `md5sum HW/PCB/*.kicad_sch`** ★ | ★**产物** (★内容只变 R_ILIM 的 Value/MPN, 其余是 uuid 重铸★) ★ |

★**★`.bak_iss220` 副本清单 (★回滚用★)★**: ★**`state/.bak_iss220/`** (★13 个真源/门禁/规格页/作业包 + 4 个产物 + 11 个 .kicad_sch + `p10_rows.json` + `SCHEMATIC_V1.md`★) ★

---

## 7. ★★落表后机器门禁实测 (★命令 + 原始输出行★)★★

★**7 条命令的 rc 全部符合预期, ★**没有任何一条门禁因为落表而变红★** ★

| # | 命令 | 期望 rc | 实测 rc | 关键输出行 |
|---|---|---|---|---|
| 1 | `python3 HW/check_netlist_selfconsistency.py` | 0 | ★**0** ★ | `✅ rc=0: ★现状与 HW/NETLIST_SELF_CONSISTENCY_SPEC.md 一致★` |
| 2 | `python3 HW/check_netlist_selfconsistency.py --selftest` | 0 | ★**0** ★ | `自检结果: 19/19 通过` · `翻面口径 (--expect-resolved) 现状 rc=1 (期望 1 = 缺陷尚未落表) ✔` |
| 3 | `python3 HW/check_netlist_selfconsistency.py --expect-resolved` | 1 | ★**1** ★ | `★★ rc=1: 翻面口径未通过 (29 条未落表) ★★` (★落表前是 **50** 条★) |
| 4 | `python3 state/check_netlist.py` | 0 | ★**0** ★ | `✅ 全过 — 原理图 V1.1 可进交叉评审` |
| 5 | `python3 state/check_netlist_pins.py` | 0 | ★**0** ★ | `✅ 全过 —— 每个针脚归属唯一, 连接器针数与针号齐, SoC 节点全部落到真实引脚` |
| 6 | `python3 state/check_sch_erc.py` | 0 | ★**0** ★ | `ERC 违规数 = 0 (★报告自称 0★) · 分类 {}` · `判定: ✅ 过 (ERC=0)` |
| 7 | `python3 state/merge.py && python3 state/gate_check.py` | 0 / 0 | ★**0 / 0** ★ | `✅ STATE.yaml 已刷新` · `【Q1 交付齐备率】 18/18 个必填验收块齐全` · `【Q6 硬件真源闸】 HW pinout 真源闸: ✅ 通过 (rc=0)` |

★**★另外 3 条我没改但跑过的门禁 (★也全绿, 防止落表把别处带红★)★**: ★**`python3 state/check_kicad_net.py`** (rc=0, `✅ 全过 — .net 与 netlist 一致 (可给 PCB 工程师)`) · ★**`python3 state/check_sch_loadable.py`** (rc=0, `✅ 全过 —— 原理图是 KiCad 真能打开、能导出 PDF/网表/BOM 的图纸`) · ★**`python3 state/check_sch_pinfull.py`** (rc=0, `判定: ✅ 过 (逐器件脚数全相等)`; ★图上 584 脚 / 表里 584 脚★) ★

★**★"--expect-resolved" 落表前 → 落表后 逐条对照 (★逐条实测, 差额 21 条 = R1 11 + R6 3 + R10 4 + R11 3, ★一条不多一条不少★)★★**

| R# | 落表前条数 | 落表后条数 | 差 | 说明 |
|---|---|---|---|---|
| ★**R1** ★ | ★**11** ★ | ★**0** ★ | ★**−11** ★ | ★**d1 落表转绿** ★ |
| ★**R2** ★ | 11 | 11 | 0 | d2/d7 卡 V-3 (★`R_BAT_DET_*`/`C_DET_BAT` 的 DNP 9 条 + 分压后 2.100V 过压 1 条 + 器件行分压比判据 1 条★) |
| ★**R3** ★ | 4 | 4 | 0 | d3 卡「板只改一次」 |
| ★**R4** ★ | 2 | 2 | 0 | d4/d9 卡 V-2 + 板 |
| ★**R5** ★ | 8 | 8 | 0 | d5 卡 V-1 |
| ★**R6** ★ | ★**3** ★ | ★**0** ★ | ★**−3** ★ | ★**d6 落表转绿** ★ |
| ★**R7** ★ | 1 | 1 | 0 | d7 卡 V-3 |
| ★**R8** ★ | 1 | 1 | 0 | d8 卡 V-3 |
| ★**R9** ★ | 1 | 1 | 0 | d4/d9 卡 V-2 + 板 (★ESD 距 J_USB_C = 47.99mm > 3.0mm★) |
| ★**R10** ★ | ★**5** ★ | ★**1** ★ | ★**−4** ★ | ★**d10 方向修正落表 ⇒ 剩「390Ω 档单 pin 载流上限 = 0.608 A > 0.5 A ⇒ R_ILIM 档位没重新定」1 条, ★卡 V-4★** ★ |
| ★**R11** ★ | ★**3** ★ | ★**0** ★ | ★**−3** ★ | ★**d11 落表转绿** ★ |
| ★**合计** ★ | ★**50** ★ | ★**29** ★ | ★**−21** ★ | ★**⇒ 差额恰好 = 落表真修掉的 21 条, ★没有一条是靠改判据消掉的★** ★ |

★**★R1 为什么是 11 条 (★落表前逐条数过, 不是估的★)★**: ★**「仍有 2 行写着『4.7k 到 3.3V / 2.38µs』」(1) + B-01 的 level/imp 三条 (3) + B-02 的 level/imp 三条 (3) + 表A L167/L168 两条 (2) = 11** ★

---

## 8. ★★复现命令 (★B6 自证★)★★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses

# ★落表链路 (改源 → 重生成) ★
python3 state/gen_netlist.py                 # rc=0 · 写 HW/netlist_v1.csv
python3 state/gen_kicad_net.py                # rc=0 · 写 HW/netlist_v1.net
python3 state/gen_netlist_pins.py             # rc=0 · 写 HW/netlist_v1_pins.csv (584 行)
python3 state/gen_bom.py                      # rc=0 · 写 HW/BOM_v1.csv (218 行)
python3 state/gen_schematic_pages.py          # rc=0 · 写 HW/SCHEMATIC_V1.md
python3 state/gen_kicad_sch.py                # rc=0 · 重出 11 个 .kicad_sch (★板不碰★)

# ★门禁 (7 条 + 3 条旁证) ★
python3 HW/check_netlist_selfconsistency.py            # rc=0
python3 HW/check_netlist_selfconsistency.py --selftest # rc=0 · 19/19
python3 HW/check_netlist_selfconsistency.py --expect-resolved   # rc=1 · ★29 条未落表 (★落表前 50★)
python3 state/check_netlist.py                         # rc=0
python3 state/check_netlist_pins.py                    # rc=0
python3 state/check_sch_erc.py                         # rc=0 · ERC=0
python3 state/merge.py && python3 state/gate_check.py  # rc=0 · Q1 18/18
python3 state/check_kicad_net.py                       # rc=0 (旁证)
python3 state/check_sch_loadable.py                    # rc=0 (旁证)
python3 state/check_sch_pinfull.py                     # rc=0 (旁证)

# ★受保护 md5 (必须逐字节不变) ★
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro
# 611b869e13518c3c023fb178f91a0075  demo_mainboard.kicad_pcb
# 3e504d2be83152e337949723e909be1b  demo_mainboard.kicad_pro

# ★锚点表 (规格页 ⇄ 脚本 逐字一致) ★
python3 HW/check_netlist_selfconsistency.py --emit-anchors | wc -l    # 162 (★= 表头2 + 160 条锚点★)
```

★**★回滚办法★**: ★**`state/.bak_iss220/` 里有每个真源/产物/原理图的改前副本 ⇒ 直接拷回去即可 (★本单所有改动都是"改源 + 重生成", 没有手改产物, 所以回滚 = 还原真源 + 重跑生成链★)** ★

---

## 9. ★★交卷自查 (★逐条★)★

| 检查项 | 结果 |
|---|---|
| 改真源前是否留 `.bak_iss220` 副本 | ★**是 (真源 6 + 门禁 1 + 规格页 1 + 作业包 1 + 产物 4 + 原理图 11 + `p10_rows.json` + `SCHEMATIC_V1.md`)★** |
| 产物是否全部由生成器重出 (★没手改 CSV★) | ★**是 (链 ①②③④⑤⑥ 全跑, rc=0)★** |
| 板 / `.kicad_pro` 是否碰过 | ★**没有 (md5 逐字节不变; 板生成器一个没跑)★** |
| PCB 布线 / 布局 / 板框是否碰过 | ★**没有** ★ |
| `MECH/` / `SW/` / `issue_log.yaml` / `PROJECT_TRACKER.md` §0 / `state/outbox/` / 别人的分片是否碰过 | ★**没有 (★`state/fragments/{pm,sw,mech}.yaml` 未改★)★** |
| 有没有代拍 V-1~V-6 | ★**没有 (★d5/d10 的档位我按"真值写清 + 明确标待裁"处理, 一个裁都没裁★)★** |
| 门禁判据 / 阈值有没有为了让门禁变绿而放松 | ★**没有 (★R1~R11 的代码一字未改; EXPECT 现状断言改成【新现状】; 追加 6 条正向锚点, 一条未减★)★** |
| 门禁有没有变红 | ★**没有 (★7 条要求命令 rc 全符合预期; 另 3 条旁证门禁也全绿★)★** |
| 未落的条目有没有写明卡在谁 / 卡在哪条 V | ★**全部写明 (§3, ★无"待定"字样★)★** |
| 零外发 | ★**是 (未发邮件 / 询价 / 问询 / 采购 / 原厂问询)★** |
| 实物 [实测] 条数 | ★**0 条 (板与屏不在本机; 所有 [实测] 均为本机脚本/本机文件实读)★** |
| 有没有自签 issue_log | ★**没有 (★status 留给 main 落 verified★)★** |

---

# ★★★第 2 批 (★ISS-223 · 2026-11-16 · 硬件总工 hw-lead 执行★) ★★★

> ★**一句话**: ★**V-1 已由 main 裁 = 22Ω ⇒ 落表第 2 批 = d5 (USB 串阻) + 补差A 的值迁移 (A 组 20 条 `imp` 清空 / 差分阻抗搬进 `z_diff`) ⇒ 门禁 `--expect-resolved` 的「未落表条数」★**25 → 21**★ (★ISS-220 交卷基线是 29; 本单起跑实测 25, 因为 04:15 那一版 SPEC.json 已把 B-21/B-22 的 `imp` 改掉, R5 的 4 条 spec 侧条件先转了绿★) ⇒ ★**R5 全组 8 条清零**★ · ★**同时把 ISS-220 查出的作业包 5 处病 (F-1~F-5) 就地修完 + 新增 §9 修订记录**★ · ★**并把 V-3 从「拍不了」变成「可拍」(★给出误差算式 + 推荐值 + 降级方案, 但不代拍★)**★**
> ★**零外发** (★未发邮件 / 询价 / 问询 / 采购 / 原厂问询★) · ★**本单实物 [实测] = 0 条** (★板与屏不在本机; 所有 [实测] 均为本机脚本 / 本机文件实读★) · ★**没有自签 issue_log** (★status 留给 main 落 verified★)

## ★★10 · 第 2 批落表条目 · 逐条 (★改了哪个真源的哪一行 · 改前/改后字面值 · 落表后跑的命令与输出行 · 证据等级★) ★★

### ★★10.1 · d5 · USB 串阻: 同一颗器件两个阻值 (90Ω vs 22Ω) (★★R5 全绿★★) ★★

| 栏 | 内容 |
|---|---|
| ★**真源文件 · 行号** ★ | ① ★**`HW/SCHEMATIC_V1_SPEC.json`** · `connections` 里 `id == "B-21"` / `id == "B-22"` 的 `imp` ★ (★**这两行是 ISS-223 前一个会话 04:15 落的, 本单沿用·未再改★**) · ② ★**`HW/check_netlist_selfconsistency.py`** · `EXPECT` 的 4 个单元格 (`d5_a291_value` / `d5_a292_value` / `d5_spec_b21_imp` / `d5_spec_b22_imp`) ★ + ③ ★**`HW/NETLIST_SELF_CONSISTENCY_SPEC.md`** · §2 锚点表同 4 个单元格 (★用 `--emit-anchors` 整块重生成覆盖, 不是手打★) |
| ★**改前 (字面)** ★ | `d5_a291_value` = `value == 90Ω ±10% (与 MIPI 不同模板!)` · `d5_a292_value` = `value == 90Ω ±10%` · `d5_spec_b21_imp` = `spec.connections[id=B-21].imp == 90Ω ±10% (与 MIPI 不同模板!)` · `d5_spec_b22_imp` = `spec.connections[id=B-22].imp == 90Ω ±10%` |
| ★**改后 (字面)** ★ | `d5_a291_value` = `value == 22Ω ±1%` · `d5_a292_value` = `value == 22Ω ±1%` · `d5_spec_b21_imp` = `spec.connections[id=B-21].imp == 22Ω ±1%` · `d5_spec_b22_imp` = `spec.connections[id=B-22].imp == 22Ω ±1%` |
| ★**★为什么这 4 个单元格必须同趟改 (★不是「改判据凑绿」★)** ★ | ★**这 4 条断言的【本体】(表A L291/L292 的 NET 行 value 必须 == SPEC.json B-21/B-22 的 `imp`) 一个字没改, 改的只是【断言的现状值】** ★ ⇒ ★**锚点条数一条没减 (d5 组仍 16 条 · 全表仍 160 条)**★ ⇒ ★**判据阈值与 `check_resolved()` 的 R1~R11 代码逐字未动**★ ⇒ ★**自检 19/19 仍全绿 ⇒ 判据没被放松成「怎么改都不红」**★ ★ |
| ★**--selftest 用例 9 的突变方向同步翻转** ★ | ★**落表后现状已是 22Ω ⇒ 原用例「改坏 B-21.imp (90Ω→22Ω)」改成了【同值改坏 ⇒ 永远抓不到红】⇒ 必须翻** ★ ⇒ ★**改成「退回 90Ω 的旧缺陷」** (★与 ISS-220 落表时 d1 (`m_net_value`) / d6 (`m_pages_21p_to_22p`) 同型处理★) ★ ⇒ ★**用例名也跟着改**: `用例9 [d5] 改坏 SPEC.json B-21.imp (22Ω→90Ω 退回旧缺陷) ⇒ 必须红` ★ |
| ★**落表后重生成 (★不许手工编辑产物★)** ★ | `python3 state/gen_netlist.py` → 表A **L291/L292 两行** value 由 `90Ω ±10% (与 MIPI 不同模板!)` / `90Ω ±10%` 变成 `22Ω ±1%`, 且 note 多了 `; 差分阻抗 90Ω ±15% 受控阻抗` (★`conn_row()` 的 `imp_extra` 逻辑★) ⇒ ★**全网表只有这 2 行变了 (diff = 6 行 = 2 改 + 4 分隔符), 其余 511 行逐字节不变** ★ |
| ★**命令与输出行** ★ | `python3 HW/check_netlist_selfconsistency.py` ⇒ `✅ rc=0: ★现状与 HW/NETLIST_SELF_CONSISTENCY_SPEC.md 一致★` · `python3 HW/check_netlist_selfconsistency.py --selftest` ⇒ `自检结果: 19/19 通过` · `python3 HW/check_netlist_selfconsistency.py --expect-resolved` ⇒ `★★ rc=1: 翻面口径未通过 (21 条未落表) ★★` (★R5 段一条红都没有了★) |
| ★**证据等级** ★ | ★**[官网]** ON Semi **AND8074/D** (USB 1.1 规范串阻 28~44Ω · 工业主流 22Ω/30Ω · 双绞线特性阻抗 Zo = 90Ω ±15%) · onsemi **STF202-22T1G** (内置 RS 20/22/24Ω) · ★**[实测]** `HW/SCHEMATIC_V1_SPEC.json` `B-21`/`B-22` 全文 (本机实读) + 表A L291/L292/L431/L432 逐字 + 板 `R_SER_USB_D_P/N = 22Ω±1%` (★本机文件实读·不是板实物量测★) + ★**[推算]** 「90Ω 串在 90Ω 线上 ⇒ 源端看到 180Ω ⇒ 摆幅减半 ⇒ 眼图不合规」 · ★**[0数据]** SoM (Forlinx) USB PHY 的驱动阻抗 / 外部串阻是否必需 (★V-1 的唯一外部依赖⇒ 降级: 已按 22Ω 落, 手册到手只核对驱动阻抗一条★) |

### ★★10.2 · 补差A / #1 · 值迁移 (★A 组 20 条 `imp` 清空 · 差分阻抗搬进 `z_diff`★) ★★

| 栏 | 内容 |
|---|---|
| ★**真源文件 · 行号** ★ | ① ★**`HW/SCHEMATIC_V1_SPEC.json`** · `connections` 里 A 组 20 条 (`A-01`~`A-10` / `A-13`~`A-22`) 的 `imp` → `""` + `z_diff` → `"100Ω ±10%"` (★**04:15 那版会话落的, 本单沿用·未再改★**) · ② ★**`state/gen_netlist.py`** · `conn_row()` 的取值优先级 (`imp` → `z_diff` → `level`) + note 的『差分阻抗』栏 (★**04:21 落的·本单沿用★**) · ③ ★**`state/check_netlist.py`** · 判据 5 的比对源 (`imp` 或 `z_diff`) (★**04:24 落的·本单沿用★**) |
| ★**★F-3 的同趟约束 (★本单实测确认★)** ★ | ★**只清空 A 组 `imp` 不改 `state/check_netlist.py` 判据 5 ⇒ `want` 变空 ⇒ 那 20 行被 `continue` 跳过 ⇒ 判据覆盖从 20 行【静默掉到 0 行】, 而门禁仍然是绿的 (判据被悄悄废掉)** ★ ⇒ ★**本单实测: 判据 5 的比对源已是 `(c.get("imp") or c.get("z_diff") or "")` ⇒ `python3 state/check_netlist.py` 的判据 5 输出仍是「A 组阻抗逐条对照规格 (20 条 net)」⇒ 覆盖 20 行, 一条没少** ★ |
| ★**落表后重生成** ★ | ★**A 组 20 条 NET 行的 value 逐字节不变** (★`imp` 清空前是 `100Ω ±10%`, 迁移后由 `z_diff` 顶上仍是 `100Ω ±10%`★) ⇒ ★**这正是「拆字段不改变任何产物」的设计意图, 本批实测确认** ★ |
| ★**证据等级** ★ | ★**[实测]** `HW/SCHEMATIC_V1_SPEC.json` 57 条 connections 全表枚举 (本机实读) + `state/gen_netlist.py` `conn_row()` 逐字 (L772-L800) + `state/check_netlist.py` 判据 5 逐字 (L93-L113) + 表A 20 条 A 组行逐行实读 · ★**[推算]** 「改动面 = 2 行 / 1 个文件, 且 A 组 20 条产物逐字节不变」 |

### ★★10.3 · 作业包 F-1 ~ F-5 就地修完 (★ISS-220 查出的 5 处病★) ★★

★**落表位置**: ★**`HW/SCHEMATIC_LANDING_WORKPACKET_V1.md`** (★作业包是 hw-lead 自己的产物, 本单可改★) ★**本单新增 §9「F-1 ~ F-5 修订记录」, 并就地改了 4 处** ★

| # | 病 | ★**就地改在哪** ★ | ★**本单实测依据** ★ |
|---|---|---|---|
| ★**F-1** ★ | d2 的 `dnp` 改法落不了地 | ★**§2.2 ④⑤** | `state/gen_netlist.py` 的 `DEMO_DNP` (L315-L322) 里 `R_BAT_DET_1` / `R_BAT_DET_2` / `C_DET_BAT` 三个 ref 【确在】⇒ `add()` 末尾会无条件覆盖 `dnp="DNP"` ⇒ 原改法无效 ⇒ 改法改成【删白名单条目 + 改 value/note】; 脚表的 `dnp` 是从网表 CSV 派生的 (`state/gen_netlist_pins.py` L230) ⇒ 不用单独改 |
| ★**F-2** ★ | d10 的 `J_CHG` 行真源写错文件 | ★**§2.10 ④⑤ + §4.C ④** | `state/gen_netlist.py` L1366-L1370 逐字「充电板整页的行数据由 `state/p10_rows.json` 提供」⇒ `J_CHG` 那条 NET 行 (表A L497, `net=BAT_CHG`) 的真源是 `state/p10_rows.json`, 改 `gen_netlist.py` 无效 ⇒ 且该 note 的目标值已过期 (ISS-220 已落成 1.216 真值口径) |
| ★**F-3** ★ | 清空 A 组 `imp` 会静默放松判据 5 | ★**§4.A ⑤ 改法表新增第 9 行 + 结果表 + ⑦** | `state/check_netlist.py` 判据 5 的 `want` 变空 ⇒ 20 行被 `continue` ⇒ 覆盖 20→0 行且门禁仍绿 ⇒ 改法表第 9 行写明「必须同趟改」; 结果表的「为什么」列原文「判据仍成立」已订正为「必须同趟改比对源」 |
| ★**F-4** ★ | d10 的方向修正连带作废「皮肤侧 42.14°C / 不能再抬电流」 | ★**§2.10 ⑤ 新增一行** | 42.14°C 是按错的 0.822 系数算的 ⇒ 按 1.216 系数电芯内阻发热 114mW → 148mW ⇒ 该温度数现在「无有效数字」; 目标文件写明 = `HW/PCB_OUTLINE_60x15.md` L149/L190 + `MECH/hinge_power_calc.json` 的 `rilim_table` ⇒ **本单没改那两行** (★不在本单可改清单★) ⇒ 归 MECH 重算那一趟 |
| ★**F-5** ★ | #5 的「白名单 ↔ §7 双向对账」在现状下不可能过 | ★**§3.5 ⑤ ②** | ★**本单实测复算三方对拍**: §7 的 CSV 块共 80 行, `board` 分布 = CHG_BOARD 64 / HINGE 11 / MAIN_PCB 4 / **1 行解析错位** (★`U_CHG` 那行 note 里逗号未加引号 ⇒ board 列被解析成 `" 0.8mm max height"` ⇒ §7 本身不是合法 CSV★) ⇒ §7 里有网表没有 = **16 个位号** (9 个 §7 侧 CHG_BOARD + 7 个 §7 侧 HINGE/MAIN_PCB/错位) · 网表有 §7 没有 = **15 个 CHG_BOARD 位号** ⇒ ⇒ 对账归 #6/补差C 的【充电板整页】那一趟, 本批不做 |

### ★★10.4 · ISS-220 的 3 条分片声明补落盘 (★交付物 ①★) ★★

| 栏 | 内容 |
|---|---|
| ★**落点** ★ | ★**`state/fragments/hw.yaml`** 的 `interface_claims` · 走 ★**`python3 state/frag_write.py --agent hw-lead --add-claim ...`** (★内部走 `update_fragment()` → `atomic_write_yaml()`: tmp + fsync + `os.replace`★) ⇒ ★**没有用 `open(p,"w")`** ★ |
| ★**3 个 key** ★ | ★**`iss220_chgboard_white_list_scope`** (★充电板归属 = `CHG_BOARD_REFS` 白名单驱动 ⇒ 漏一颗就默认落 MAIN_PCB★) · ★**`iss220_i2ca_pullup_domain_1v8`** (★I2C_A 上拉 = 2.2k 到 `RAIL_VDD_1V8_IO`★) · ★**`iss220_ichg_ratio_true_value`** (★`ICHG/IIN = η·Vbus/Vbat` = 1.216@3.70V / 1.071@4.20V★) |
| ★**mtime 前 / 后** ★ | ★**前**: `2026-11-16 01:59:34` (md5 `7eeea9ebc73556d525b9b816fc77667f`) ⇒ ★**后**: `2026-11-16 05:13:58` (md5 `88d0f2f92479a21980bca9cfb4427638`) ★ |
| ★**命中行** ★ | `state/fragments/hw.yaml` L2858 / L2863 / L2868 (★`grep -n` 实测★) |

---

## ★★11 · V-3 可判化 (★RK3572 SARADC_VIN5 官方参数自查 + 误差算式 + 推荐值 + 降级方案★; ★不许代拍★) ★★

★**结论一句话**: ★**V-3 现在的选项集 (A: 2.0M+1.2M vs D: 2.0M+1.0M) 是个【伪选择】—— 两者的 R_top 都是 2.0M, 而两个主导误差项 (电阻比容差 / 漏电经 R_top) 【完全相同】; 真正的决策是【分压链的阻抗等级】, 而这一条被 V-3 的选项集漏掉了 ⇒ 本单给出可拍依据 + 推荐值 (新方案 E = 100k+60k+100nF) + 降级方案, 但【不代拍】** ★

### ★★11.1 · 官方参数自查 (★自己查·零外发·用项目库内的一手件★) ★★

| 参数 | 查到的值 | 证据等级 | 逐字出处 (本机实读) |
|---|---|---|---|
| ★**分辨率** ★ | ★**12 bit** ★ | ★**[官网]** | `HW/RK3572_PIN_TABLE/rk3572_datasheet_V1.1.txt` (RK3572 Datasheet Rev 1.1, ★**Copyright © 2026 Rockchip Electronics Co., Ltd.**★) §3.10 **Table 3-16** → `Resolution  NA  12  NA  Bit`; §1.2 特性也写「Successive approximation ADC(SARADC) / Supports 12-bit resolution / Supports up to 1MS/s sampling rate / Supports 8 single-ended input channels」 |
| ★**满量程 / 模拟输入范围** ★ | ★**AIN = `AVSS18` ~ `AVDD18`**; `SARADC_AVDD1V8` = ★**1.62 / 1.8 / 1.98 V** (min/typ/max) ★ | ★**[官网]** | 同上 Table 3-16 → `Anglog Input Range  AIN  AVSS18  NA  AVDD18  V`; 电气总表 → `SARADC Analog Power(1.8V)  SARADC_AVDD1V8  1.62  1.8  1.98  V` ⇒ ★**1 LSB = 1.8/4096 = 439.5 µV (typ) / 1.98/4096 = 483.4 µV (max)** ★ |
| ★**线性度 / 偏移** ★ | ★**DNL ±1.0 typ / ±3.0 max LSB (PD=Low) · INL ±2.0 typ / ±6.0 max LSB (Fs=1MS/s, FCLK=20MHz) · 顶部/底部 offset 误差 ±10 typ / ±20 max LSB** ★ | ★**[官网]** | 同上 Table 3-16 ⇒ ★**合计 worst = (20+6+3) = 29 LSB** ★ |
| ★**★输入漏电流** ★ | ★**[0数据] ★查不到**★ ⇒ datasheet Table 3-16 【没有】漏电流行 | ★**[0数据]** | ★**逐字核对过的坑**: datasheet 全文里那几条 `Input leakage current  IPAD  -10  NA  10  uA` 属于 ★**Table 3-4「Electrical Characteristics for General IO」= 数字 GPIO**★ (★行归属已逐字核对: 那一段每个参数的分组写的是 `Digital 3.3V/1.8V GPIO` / `Digital 1.8V only and Digital 1.8V/1.2V GPIO` / `VCCIO0 IO`★), ★**不是 SARADC**★ ⇒ ★**不能拿 GPIO 的 10µA 当 SARADC 的值, 也不能拿它当 SARADC 的值来论证「漏电无所谓」** ★ |
| ★**★输入电容 / 采样保持时间 / 内部采样电容 C_in** ★ | ★**[0数据] ★查不到**★ | ★**[0数据]** | ★**datasheet 全文 grep「input capacitance / Capacitance / acquisition / Input Resistance / source impedance / Sample」⇒ 零命中** ★ ⇒ 这些参数在 ★**Rockchip TRM**★ 里, ★**TRM 不公开** ★ ⇒ 公开的 Linux 主线 `drivers/iio/adc/rockchip_saradc.c` ★**也没有 rk3572 的条目**★ (★表里只有 saradc / rk3066-tsadc / rk3399 / rk3528 / rk3562 / rk3568 / rk3588 / rv1106★) ⇒ ★**RK3572 走 BSP 驱动 ⇒ 拿不到** ★ ⇒ ★**顺带一条有用的 [官网]**: 该驱动的 `IIO_CHAN_INFO_SCALE` 是 `uv_vref / 1000` 除以 `scan_type.realbits` ⇒ ★**VFS 由 vref regulator 定, 且 raw 读数不做硬件 offset 校准** (`last_val &= GENMASK(realbits-1, 0)`) ⇒ ★**offset ±20 LSB 是【软件】要自己标的** ★ |

### ★★11.2 · 误差算式 (★口径 = 项目自己的 `SW/tools/timing_check.py` F4, 不是本单另起一套★) ★★

```
k          = R_bot / (R_top + R_bot)                       # 分压比
V_node     = V_BAT · k
R_th       = R_top || R_bot                               # 源阻抗 (THEVENIN)
τ          = R_th · C_filter
LSB_node   = V_FS / 2^12                                  # V_FS = 1.8V typ (★不是 3.3V★)
t_settle   = ln(1 / (0.5·LSB/ V_FS)) · τ = ln(2^12) · τ = 9.0109 · τ
ΔV_leak    = I_leak · R_th                                ⇒ ★折算到电池侧 = I_leak · **R_top**★
ΔV_ratio   = ( R_top/(R_top+R_bot)·ε_bot + R_bot/(R_top+R_bot)·ε_top ) · V_node   (worst-case, 两颗反向取极值)
ΔV_ADC     = (offset_max + INL_max + DNL_max) · LSB = 29 · LSB
```

★**★决定性的恒等式 (本单实算)★**: ★**`R_th / k = R_top`** ⇒ ★**漏电引起的【电池侧】误差只跟【上臂】R_top 有关, 与下臂无关** ★ ⇒ ★**A (2.0M+1.2M) 与 D (2.0M+1.0M) 的 R_top 都是 2.0M ⇒ 漏电误差项【完全相同】** ★ ⇒ ★**而电阻比容差项 A 与 D 也同为 ±1.00%** ★ ⇒ ★**⇒ A 与 D 的差别只剩【利用率 / 分辨率 / 分压电流】三项 (A 全面占优), 而【决定成败】的两项 (漏电 + 建立时间) 两边一样差** ★

### ★★11.3 · 三档实测对比 (★`state/calc_v3_batdet.py` 的本机实跑输出·可复现★) ★★

| 方案 | k | R_th | τ | t_settle(½LSB) | V_node@4.2V | 利用率@1.8V | ★**过压?** ★ | 比容差(worst) | ADC 自身(max) | 漏电@1µA | 占 FS |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ★**现行 1M+1M** (DNP 未装) ★ | 0.50000 | 500.0 kΩ | 50.00 ms | 450.5 ms | **2.1000** | 116.7% | ★**是** ★ | ±1.00% | 28.0 mV | 500.0 mV | 27.8% |
| ★**V-3 方案 A 2.0M+1.2M** ★ | 0.37500 | 750.0 kΩ | 75.00 ms | 675.8 ms | 1.5750 | 87.5% | 否 | ±1.00% | 37.4 mV | 750.0 mV | 41.7% |
| ★**V-3 方案 D 2.0M+1.0M** ★ | 0.33333 | 666.7 kΩ | 66.67 ms | 600.7 ms | 1.4000 | 77.8% | 否 | ±1.00% | 42.1 mV | 666.7 mV | 37.0% |
| ★**★新方案 E 100k+60k + 100nF** ★ | 0.37500 | **37.5 kΩ** | **3.75 ms** | **33.8 ms** | 1.5750 | 87.5% | 否 | ±1.00% | 37.4 mV | **37.5 mV** | **2.1%** |
| ★**新方案 E′ 100k+60k + 1µF** ★ | 0.37500 | 37.5 kΩ | 37.50 ms | 337.9 ms | 1.5750 | 87.5% | 否 | ±1.00% | 37.4 mV | 37.5 mV | 2.1% |

★**★静态功耗 (方案 E 的唯一代价)★**: ★**26.25 µA / 110.25 µW / 0.630 mAh·日⁻¹** (★现行 1M+1M 只要 2.10 µA / 8.82 µW / 0.050 mAh·日⁻¹★) ⇒ ★**这是「待机功耗 vs 精度」的唯一取舍, 归老板拍** ★

★**★建立时间敏感度 (C_in 是 [0数据], 只做扫描★)★**: ★**`t_acq = 9.0109 × R_th × C_in`** ★ ⇒ 方案 E 在 C_in = 10/20/30 pF 下分别 = ★**3.4 / 6.8 / 10.1 µs**★ (★方案 A 是 67.6 / 135.2 / 202.7 µs★) ⇒ ★**方案 E 的采样窗口小到可以忽略; 方案 A 的窗口虽然也不大, 但要跟 1MS/s 的转换周期比, 就不确定了** ★

### ★★11.4 · 可拍依据 + 推荐值 + 降级方案 (★供 main/老板拍·本单不代拍★) ★★

| 栏 | 内容 |
|---|---|
| ★**可拍依据 (①)** ★ | ★**现行 1M+1M 在【任何】分压比下都过压** (4.2V × 0.5 = **2.100V > AVDD18 max 1.98V**) ⇒ ★**d2/d7/d8 的现状是确定的缺陷, 不是"待定"** ★ |
| ★**可拍依据 (②)** ★ | ★**V-3 现有两个候选 (A / D) 的差别只有 R_th 的 12.5%, 而两者都差 3 个数量级** (★SAR ADC 要的是 kΩ 级源阻抗, 不是 750kΩ★) ⇒ ★**⇒ V-3 现在的选项集是【伪选择】; 必须把【阻抗等级】摆到台面上** ★ |
| ★**可拍依据 (③)** ★ | ★**漏电误差项只跟 R_top 有关 (恒等式 `R_th/k = R_top`)** ⇒ ★**要压漏电误差只有一条路: 把 R_top 从 2.0M 降到 100k (↓20 倍)**, 而不是在下臂 1.2M/1.0M 之间选 ★ |
| ★**可拍依据 (④)** ★ | ★**BAT_DET 的用途定位把它从"精度需求"降级成"阈值判断"**: ★**`SW/SW_REQUIREMENTS.md` M7-R6 只要求「软件侧确认电量读取正常」, 不是电量百分比精度** ⇒ ★**⇒ 用途的精度需求 (低电量告警粗判, ±100mV 级) ≪ 残差误差 ⇒ V-3 变成【可判】** ★ |
| ★**★推荐值 (供拍, 本单不代拍)★** ★ | ★**方案 E = 上臂 100k ±1% + 下臂 60k ±1% + 滤波 100nF ±10%** ★ ⇒ ★**k = 0.375 (与 A 同 ⇒ 利用率 87.5% / 电池侧分辨率 1.172 mV 都不打折)** · ★**R_th = 37.5 kΩ ⇒ τ = 3.75 ms ⇒ t_settle(½LSB) = 34 ms ⇒ 软件侧等 ≥50 ms 就到 ½LSB** · ★**漏电 @1µA (最坏占位值) = 37.5 mV = 2.1% FS ⇒ 可软件标定 (常数项)** · ★**总误差 (含 ADC 自身 29 LSB) < 2.9% FS** · ★**唯一代价 = 26.25 µA / 110 µW 常开** ★ |
| ★**降级方案 (①)** ★ | ★**若不能接受 110 µW 常开** ⇒ ★**把分压链改成"按需使能" (用一个 P-MOS 把上臂接到 BAT, 采样时才开)**: 采样窗口 34 ms × 采样周期 ⇒ ★**均摊功耗可降到 µW 级** ⇒ ★**但这是【板级拓扑】改动 ⇒ 归「板只改一次」那一趟★** ★ |
| ★**降级方案 (②)** ★ | ★**若 SoM 手册 / SoC TRM 拿不到 (I_leak / C_in / t_acq 三个数)**: ★**按方案 E 落表, 并把 BAT_DET 的用途口径写死为【低电量告警粗判 (±100mV 级)】, 不作【电量百分比显示】的精度基准** ⇒ ★**依据 = M7-R6 的措辞 (只要求"读取正常")** ★ ⇒ ★**即便 I_leak = 1µA 这个最坏占位值, E 的总误差仍 < 2.9% FS ⇒ 够用** ★ |
| ★**降级方案 (③)** ★ | ★**若连方案 E 的 110 µW 都不能接受** ⇒ ★**兜底口径: BAT_DET 链【保持不装 (DNP)】, 电量改由【BQ25896 的 I2C 状态寄存器】读 (★BQ25896 有 VBUS/VSYS/IBAT 遥测★) ⇒ ★**但这是【换架构】, 归 V-7 充电板整机阶段单★** ★ |
| ★**降级方案 (④)** ★ | ★**★本单【不落表 V-3 的值】★**: ★**网表仍是 1M+1M + DNP (★诚实的现状★) ⇒ ★**d2 / d7 / d8 仍然 BLOCKED 于 V-3, 门禁 R2/R7/R8 仍然红 (★21 条里的 13 条★) ⇒ ★**这不是本单的失败, 这是"没拍就不落"的纪律** ★ |
| ★**★顺带查出的一处 SW 侧口径错 (★只报不改·SW 地界★)★** ★ | ★**`SW/tools/timing_check.py` 的 `DEVICE["V_DET_FS"] = 3.3`** ★ ⇒ ★**`BAT_DET` 走 `J_SOM_P1 pin38 = SARADC_VIN5` = 1.8V 域 (FET3572C_PIN_TABLE.csv P1_38) ⇒ V_DET_FS 对这条链应该是 1.8V, 不是 3.3V** ★ ⇒ ★**⇒ SW 算出来的「漏电偏移 %满量程」对 BAT_DET 链【偏小 1.83 倍】(1.8/3.3)** ★ ⇒ ★**⇒ 本单把这条登记成 need 给 sw-lead (见交接单 B5 第 11 条), 本单不动 `SW/`** ★ |
| ★**证据等级** ★ | ★**[官网]** RK3572 Datasheet Rev 1.1 §3.10 Table 3-16 + 电气总表 + §1.2 特性 (★项目库内 `HW/RK3572_PIN_TABLE/rk3572_datasheet_V1.1.txt`★) · ★**[官网]** Linux 主线 `drivers/iio/adc/rockchip_saradc.c` (★VFS 由 vref regulator 定 / raw 无硬件 offset 校准 / 无 rk3572 条目★) · ★**[实测]** `state/calc_v3_batdet.py` 的本机实跑输出 (★`state/calc_v3_batdet_output.txt`·可复现★) + `SW/tools/timing_check.py` L1028-L1070 逐字 (★公式口径★) + `HW/PCB/FET3572C_PIN_TABLE.csv` P1_38 逐字 · ★**[推算]** `R_th/k = R_top` 恒等式与全部误差项的传播 · ★**[0数据]** SARADC_VIN5 的输入漏电流 / 输入电容 / t_acq / C_in (★datasheet 无 · TRM 不公开 · BSP 驱动拿不到★) |

---

## ★★12 · 板侧同步清单 (★第 2 批更新·★只更新状态, 不许动板★) ★★

| 项 | 落表项 | ★**因本批落表而变化的** ★ | ★**仍等 V-2 与「板只改一次」那一趟的** ★ |
|---|---|---|---|
| ★**B-1** ★ | ★**d11 / #5** ★ | ★**无变化** (★ISS-220 已把 `C_VBUS_GND` 判成 CHG_BOARD, 板还是 MAIN_PCB ⇒ 已知不一致照旧★) | ★**照旧**: 把 `C_VBUS_GND` 的封装从 demo 主 PCB 上拿掉 (★板生成器按 board 列过滤 ⇒ 重跑 `state/gen_pcb_netlist_board.py` 即自动消失★) ★ |
| ★**B-2** ★ | ★**d3** ★ | ★**无变化** | ★**照旧**: 板封装 `U_EN_SW` 的 `Value` 属性从 `EN 输入 (高=放行底板)` 改成器件身份描述 (★R3 判据就是这条★) ★ |
| ★**B-3** ★ | ★**d4 / d9** ★ | ★**无变化** | ★**照旧**: `D_ESD_USB_D` 从 2 脚换 3 脚封装 (pin1=D+ / pin2=D− / pin3=GND) ★ |
| ★**B-4** ★ | ★**d4 / d9** ★ | ★**无变化** | ★**照旧**: 把 `D_ESD_USB_D` 挪到 `J_USB_C` 旁 ≤ 3.0 mm (★现距 47.99 mm★) ⇒ 布线必须重跑 ⇒ 必须与 B-3 同趟 ★ |
| ★**B-5** ★ | ★**d4 / d9** ★ | ★**无变化** | ★**照旧**: USB D− 那条路上补 ESD (★现在板上挂 D− 两张网的 ESD 位号数 = 0★) ★ |
| ★**B-6** ★ | ★**#6 / 补差C** ★ | ★**无变化** | ★**照旧**: 充电板 π 滤波的位号与拓扑 (★归充电板整机阶段单 V-7★) ★ |
| ★**★B-7 (★本批新增★)** ★ | ★**d5 / 补差A** ★ | ★**★网表侧已改: `R_SER_USB_D_P` / `R_SER_USB_D_N` 的 NET 行 value 由 90Ω 改成 22Ω ±1% ⇒ ★**板上的器件值本来就是 22Ω, 板侧【无需改动】★ (★本批实测: 板 `R_SER_USB_D_P/N` = 22Ω±1%★)** ⇒ ★**⇒ d5 这一条【不进板侧同步清单】(★它是"网表追平板", 不是"板要改"★)** ★ | — (★无★) |
| ★**★B-8 (★本批新增★)** ★ | ★**V-3 (待拍)** ★ | ★**无 (★V-3 没拍, 没落表★)** | ★**★若 main/老板拍【方案 E (100k+60k)】⇒ 板侧 `R_BAT_DET_1` / `R_BAT_DET_2` 的封装/阻值要改 (★1M → 100k / 60k★) ⇒ ★**这条必须并进「板只改一次」那一趟**, 否则又要重出一次板 ★** ⇒ ★**⇒ ★**这是 V-3 必须在派板前拍完的原因** ★ ★ |

---

## ★★13 · 受保护 md5 前后对照 (★第 2 批·本单起跑基线 ⇒ 交卷实测★) ★★

| 文件 | 前 (本单起跑) | 后 (交卷) | 变了? |
|---|---|---|---|
| ★**`HW/SCHEMATIC_V1_SPEC.json`** ★ | `7584f8b479194710621d175fa3168c1f` | `7584f8b479194710621d175fa3168c1f` | ★**否** (★04:15 那版会话已落 B-21/B-22 的 `imp` + A 组清空·本单沿用未再改★) |
| ★**`state/gen_netlist.py`** ★ | `3c765729de34db50ee1b0ddd60c360a2` | `3c765729de34db50ee1b0ddd60c360a2` | ★**否** (★04:21 那版会话已落 `conn_row()` 取值优先级★) |
| ★**`state/check_netlist.py`** ★ | `d13381f42f41f2f1a89dbfbf98484535` | `d13381f42f41f2f1a89dbfbf98484535` | ★**否** (★04:24 那版会话已落判据 5 的 `imp or z_diff`★) |
| ★**`HW/check_netlist_selfconsistency.py`** ★ | `5e387936738f399ebbe4cbebd5479bb0` | `6767202963eb96c4050125379b125b7c` | ★**是** (★EXPECT 4 个单元格 + selftest 用例 9 的突变方向 + 用例名★) |
| ★**`HW/NETLIST_SELF_CONSISTENCY_SPEC.md`** ★ | `8e0ac3f7e0edc31847ca158e5ee0456a` | `118bfabbf726b9fa9a59e6361a5f412c` | ★**是** (★锚点表 4 个单元格·用 `--emit-anchors` 整块重生成★) |
| ★**`HW/SCHEMATIC_LANDING_WORKPACKET_V1.md`** ★ | `0970113b9443157d2f3c2d3c2e72f510` | `bae9da8c15ff0d08bf6c3c900a84b0a7` | ★**是** (★F-1~F-5 就地修 + §9 修订记录 + §8 状态表更新★) |
| ★**`HW/SCHEMATIC_LANDING_V1_LANDED.md`** ★ | `5fd6e08ca9d9138c5cbf84a86be77908` | ★**★本文件自身 (★md5 会随本节的写入而变 ⇒ 以交卷时 `md5sum` 实测为准★)** ★ | ★**是** (★本 §10~§14★) |
| ★**`HW/netlist_v1.csv`** ★ | `13f59a43dbd35dc6cb16e897c8c891ab` | `3215020b6d4120e1b7728227effdc6d3` | ★**是** (★**只 L291/L292 两行**★) |
| ★**`HW/netlist_v1_pins.csv`** ★ | `a600afae493f5a7a6c55f46ad35ac89c` | `a600afae493f5a7a6c55f46ad35ac89c` | ★**否** (★脚表不含 NET 行的 value★) |
| ★**`HW/BOM_v1.csv`** ★ | `92b51580867deca9f8b04af88d925d96` | `92b51580867deca9f8b04af88d925d96` | ★**否** ★ |
| ★**`HW/BOM_pseudo_refs_v1.csv`** ★ | `984dd73dd8d1ed492b5b1fb38519034c` | `47e1659a42d8d3f6728ea653df1eb530` | ★**是** (★L54/L55 两行跟着网表走★) |
| ★**`HW/netlist_v1.net`** ★ | `978ab59e297e6bb89f873b763569eccb` | `978ab59e297e6bb89f873b763569eccb` | ★**否** ★ |
| ★**`HW/SCHEMATIC_V1.md`** ★ | `a349ccbeee4a65830cbde21d0e409825` | `b06298db21de27112def71d28ce2997b` | ★**是** (★生成物·跟着网表走★) |
| ★**`HW/PCB/demo_mainboard.kicad_pcb`** ★ | ★**`611b869e13518c3c023fb178f91a0075`** ★ | ★**`611b869e13518c3c023fb178f91a0075`** ★ | ★**否 (受保护·逐字节不变)★** |
| ★**`HW/PCB/demo_mainboard.kicad_pro`** ★ | ★**`3e504d2be83152e337949723e909be1b`** ★ | ★**`3e504d2be83152e337949723e909be1b`** ★ | ★**否 (受保护·逐字节不变)★** |
| ★**`state/fragments/hw.yaml`** ★ | `7eeea9ebc73556d525b9b816fc77667f` | ★**`88d0f2f92479a21980bca9cfb4427638`** (★补落 3 条后·05:13★) → ★**`714c070a04e67613d437519768e7ec95`** (★再加 3 条 `interface_claims` + 4 条 `needs_from` + 3 条 `artifacts` + `status`·05:29★) ★ | ★**是** (★**全部走 `frag_write.py` 原子写·没有 `open(p,"w")`**★) ★ |

★**★★同窗口内【别人】动过的 `HW/PCB/` 文件 (★★诚实标出, 不是我干的★)★★**: ★**`HW/PCB/_frame_reference.kicad_pcb` / `STACKUP.md` / `LAYOUT_RULES.md` / `GEN_SELF_CHECK.txt` 在 05:22:35 被重生成过** ★ (★写入者是 `state/gen_kicad_project.py` (★骨架生成器·它只【反读】板文件写叠层/规则文档, 不写板★) ⇒ 调用链 = `state/chain_gate.py` → `state/check_pcb_drc.py` 的 C5 生成器自检 ⇒ ★**不是本单跑的命令**★ (★本单只跑了 `gen_netlist.py` / `gen_netlist_pins.py` / `gen_bom.py` / `gen_kicad_net.py` / `gen_schematic_pages.py` / `gen_kicad_sch.py`★) ⇒ ★**受保护的 `HW/PCB/demo_mainboard.kicad_pcb` 与 `.kicad_pro` 的 mtime 仍是 2026-11-06 07:07:17 / 2026-11-16 (未变), md5 逐字节不变** ★

★**★回滚副本★**: ★**`state/.bak_iss223_r2/`** (★12 个本单起跑基线副本★) + ★**`state/.bak_iss223/`** (★上一会话 04:06 留的 13 个 ISS-223 前基线★) ★

---

## ★★14 · 第 2 批复现命令 (★B6 自证★) ★★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses

# ★★7 条必跑门禁 ★★
python3 HW/check_netlist_selfconsistency.py                    # rc=0 (现状守卫 + 作业包完整性 + 三方对齐)
python3 HW/check_netlist_selfconsistency.py --selftest          # rc=0 (反向用例全抓到, 19/19)
python3 HW/check_netlist_selfconsistency.py --expect-resolved   # rc=1 (★预期: 还有 21 条未落表★)
python3 state/check_netlist.py                                  # rc=0 (全过)
python3 state/check_netlist_pins.py                             # rc=0 (每个针脚归属唯一)
python3 state/check_sch_erc.py                                  # rc=0 (ERC 违规数 = 0)
python3 state/check_sch_pinfull.py                              # rc=0 (图上脚数 = 表里脚数)
python3 state/merge.py && python3 state/gate_check.py           # rc=0 且 【Q1 交付齐备率】 18/18

# ★★落表链路 (改源 → 重生成; ★板不碰★) ★★
python3 state/gen_netlist.py && python3 state/gen_netlist_pins.py && \
python3 state/gen_bom.py && python3 state/gen_kicad_net.py && \
python3 state/gen_schematic_pages.py && python3 state/gen_kicad_sch.py

# ★★V-3 误差预算 (★可复现★) ★★
python3 state/calc_v3_batdet.py          # 输出已存 state/calc_v3_batdet_output.txt

# ★★受保护 md5 (必须逐字节不变) ★★
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro
# 611b869e13518c3c023fb178f91a0075 / 3e504d2be83152e337949723e909be1b

# ★★锚点表 (规格页 ⇄ 脚本 逐字一致) ★★
python3 HW/check_netlist_selfconsistency.py --emit-anchors | wc -l    # 162
```

---

## ★★15 · 第 3 批落表条目 (★ISS-233 · 2026-11-16 · 硬件总工 (hw-lead) 执行 · ★d3 网表侧·A 类自主落★) ★★

> ★**单号**: ★**ISS-233** · ★**owner**: hw-lead · ★**verify_by**: main · ★**上游**: ★**ISS-230 交卷的作业包 `HW/SCHEMATIC_LANDING_BATCH3_WORKPACKET_V2.md` (★21 条未落表的逐条归因★)**
> ★**性质**: ★**A 类自主落 (★不依赖老板拍任何 V 值★)** ⇒ ★**本批【没有落任何 V 值】(V-2 / V-3 / V-4 老板都没拍) ⇒ 一条都没落★** · ★**没碰板 (受保护 md5 逐字节不变)★ · ★**没碰 `SW/` / `MECH/` / `state/issue_log.yaml` / `PROJECT_TRACKER.md` §0 / 别人的分片★** · ★**零外发 ⇒ 本批实物 [实测] = 0 条★**
> ★**交卷单**: ★**`HANDOFF/2026-11-16_hw-lead_ISS233_21条未落表归因与拍板即落清单.md`** (★21 条逐条归因 + V-2/V-3/V-4 拍板即落逐字清单 + 新旧 md5 登记位★)**

### ★★15.1 · 一句话结论 + 前后对比 ★★

★★**落表结果**: ★**21 条未落表里, 【A 类】3 条当场落 (★R3 的网表侧 3 条: 表A 本体行 / 表B 本体行 / BOM type+value★) ⇒ ★**`--expect-resolved` 21 → 18** ★; ★**其余 18 条按【V-3 = 13 条 / V-2+板 = 3 条 / V-4 = 1 条 / 板侧 R3 = 1 条】逐条归因并写进交卷单★** ⇒ ★**没有一条写"待定"★**

| 指标 | 落表前 | 落表后 | 怎么量的 |
|---|---|---|---|
| ★**`--expect-resolved` 未落表条数** ★ | ★**21** ★ | ★**18** ★ | ★**`python3 HW/check_netlist_selfconsistency.py --expect-resolved`** ★ |
| ★**R3 四条判据** ★ | ★**全红 (4 条)** ★ | ★**3 条绿 + 1 条红 (★板侧★)** ★ | 同上 (逐条看输出) ★ |
| ★**R2 / R7 / R8 / R4 / R9 / R10** ★ | ★**红** ★ | ★**红 (未动, 一个字没碰)** ★ | ★**全部 BLOCKED 于 V 值 / 板那一趟, 原因见交卷单 §1★** ★ |
| ★**现状守卫 `EXPECT` 锚点条数** ★ | ★**160** ★ | ★**160** ★ (★**一条未减**★) ★ | `python3 HW/check_netlist_selfconsistency.py --emit-anchors \| wc -l` ★ |
| ★**网表行数 / 脚表行数 / BOM 行数** ★ | ★**513 / 584 / 218** ★ | ★**513 / 584 / 218** ★ (★零增零删 ⇒ 门禁锚点的行号全部不变★) ★ | `wc -l` ★ |
| ★**`--selftest` 反向用例** ★ | ★**21/21** ★ | ★**21/21** ★ (★用例4 的突变方向按新现状翻转★) ★ | `python3 HW/check_netlist_selfconsistency.py --selftest` ★ |

★★**★"落表不许靠删条目 / 改判据达成"的自证 (★两条反向自证都实跑过★)★★**:
· ★**(b1) 旧脚本 + 旧数据** ⇒ ★**三张表 md5 逐字节回到基线 (`3215020b…` / `a600afae…` / `92b51580…`) + `--expect-resolved` 回到 ★**21 条**★ + 现状守卫 rc=0 (★旧状态自洽, 说明回退是faithful 的★)** ★
· ★**(b2) 新脚本 + 旧数据 (只把 A 类落的三行改回旧值)** ⇒ ★**现状守卫 ★**rc=1 (红 5 条: `d3_a442_type` / `d3_a_body` / `d3_b_body` / `d3_bom208_type` / `d3_bom208_value`)★ + `--expect-resolved` 回到 ★**21 条**★** ★
· ⇒ ★**⇒ 判据没被「调没」, 是缺陷真的被修掉 3 条★**

### ★★15.2 · 落表条目 · 逐条 (★改了哪个真源的哪一行 · 改前/改后字面值 · 跑的命令与输出行 · 证据等级★) ★★

#### ★★15.2.1 · d3 · `U_EN_SW` 缺器件本体行 ⇒ BOM 把它登记成 NET 行 (★R3 网表侧 3/4 转绿★) ★★

| 项 | 内容 |
|---|---|
| ★**真源文件 · 行号** ★ | ★**`state/gen_netlist.py`** · ★**`build_p1()` 里 U_EN_SW 那 4 条 `add()` 的第 2 条 (★`add("P1", "RAIL_DEMO_5V", "U_EN_SW VIN", "RAIL_DEMO_5V", "U_EN_SW", …)★ ⇒ 盘上是 ★**L1496-L1497**★)** ★**一处真源, 改一行 (★`type` + `value` + `note` 三个字段★)** ★ |
| ★**改前 (字面)** ★ | `value` = `5V 输入` · `type` = `NET` · `note` = `[U_EN_SW] IN = 5V (Type-C 直供)` ★ |
| ★**改后 (字面)** ★ | `value` = ★`TPS22991RAA (负载开关: 1=VIN/2=ON/3=VOUT/4=GND, UQFN-4 RAA 0.85 x 0.75 mm)`★ · `type` = ★`IC`★ · `note` = ★`[U_EN_SW] ★★器件本体行 (type=IC · 挂在 pin1/VIN 上 · 同族正确写法 = U_PWR_SW 本体行挂 pin3/VOUT)★★ ★pin1 脚级功能: IN = 5V 输入 (Type-C 直供 5V)★ \| pin2 = EN 输入 (高=放行底板) \| pin3 = 5V 输出 (受 CARRIER_BOARD_EN 门控) \| pin4 = GND \| ★★F13 落法: 底板所有 3.3V/5V 支路都挂 RAIL_BOARD_5V (不是 SYS) ⇒ 主板各路只在 SoM 就绪后上电 ⇒ 防底板早于核心板上电损坏处理器★★ \| ★选型 = TPS22991RAA (项目总工 11-03 已裁, ISS-172 待老板点头; 同 UQFN-4 封装 ⇒ 若改 TPS22916/17 = 换料不换板)★`★ ★ |
| ★**为什么本体行挂 pin1 (而不是照抄 U_PWR_SW 的 pin3)** ★ | ★**pin1 = 表B 里 U_EN_SW 的第一行 ⇒ 原理图符号的 `Value` 属性会跟着变成器件身份描述 (★落表前符号上写的是 "5V 输入" 这句脚功能串★) ⇒ ★**★原理图 (当前主线交付物) 上看得到料号★** ★ ⇒ ★**板侧的封装 `Value` 属性仍是脚功能串, 但那一侧反正要手工改 (★`gen_pcb_components.py` 对已在板上的封装走 `if ref in have: continue` ⇒ 不会自动重写 Value★) ⇒ 挂哪个脚对板侧没差别★** ★ |
| ★**落表后产物 (逐字, 只列变的那几行)** ★ | 表A ★**L442**: `P1,RAIL_DEMO_5V,U_EN_SW pin1,RAIL_DEMO_5V,U_EN_SW,"TPS22991RAA (负载开关: 1=VIN/2=ON/3=VOUT/4=GND, UQFN-4 RAA 0.85 x 0.75 mm)",IC,必装,[官方],,"[U_EN_SW] ★★器件本体行 …",A-24,MAIN_PCB,"UQFN-4 RAA, 0.85 x 0.75 mm, 0.4 mm pitch",TPS22991RAA` (★行号未变★)<br>表B ★**L531**: `U_EN_SW.pin1,RAIL_DEMO_5V,U_EN_SW,pin1,P1,"TPS22991RAA (负载开关: …)",IC,必装,MAIN_PCB,A-24,…` (★行号未变★)<br>BOM ★**L208**: `U_EN_SW,1,"TPS22991RAA (负载开关: …)",IC,必装,镜脚主 PCB,P1,[官方],,"UQFN-4 RAA, 0.85 x 0.75 mm, 0.4 mm pitch",TPS22991RAA,待定,待定,已定型-IC,型号已定 (官网/官方数据手册), 封装与替代料待采购确认` (★行号未变★) ★ |
| ★**跑的命令 + 输出行** ★ | `python3 state/gen_netlist.py` (rc=0) ⇒ ★**表A 只有 L442 一行变, 其余 512 行逐字节不变★**<br>`python3 state/gen_kicad_net.py` (rc=0) ⇒ ★**`HW/netlist_v1.net` 逐字节不变 (`978ab59e…`)★**<br>`python3 state/gen_netlist_pins.py` (rc=0) ⇒ ★**脚表 584 行不变, 只有 L531 一行变★**<br>`python3 state/gen_bom.py` (rc=0) ⇒ ★**BOM 218 行不变, 只有 L208 一行变 (★`procurement` 从 `待分类` 变 `已定型-IC`★)** ★<br>`python3 HW/check_netlist_selfconsistency.py --expect-resolved` ⇒ ★**21 条 → 18 条 (R3 的 3 条网表侧红消失, 板侧那 1 条仍在)★** ★<br>`python3 HW/check_netlist_selfconsistency.py` ⇒ ★**rc=0 (现状守卫)★** · `--selftest` ⇒ ★**rc=0, 21/21★** ★ |
| ★**门禁锚点同步 (★只改【现状断言值】, 判据本体与阈值一个字没动, 锚点条数 160 → 160★)** ★ | `d3_a442_type`: `type == NET` → ★`type == IC`★ · `d3_a_body`: `count(ref==U_EN_SW&type!=NET) == 0` → ★`== 1`★ · `d3_b_body`: 同型 → ★`== 1`★ · `d3_bom208_type`: `type == NET` → ★`type == IC`★ · `d3_bom208_value`: `value == EN 输入 (高=放行底板)` → ★`value == TPS22991RAA (负载开关: 1=VIN/2=ON/3=VOUT/4=GND, UQFN-4 RAA 0.85 x 0.75 mm)`★ · ★**`d3_board_value` 一个字没动 (★板没动★)** ★ · ★**`--selftest` 用例4 (`m_bom_type`) 的突变方向翻转: `BOM L208 type` 由 `IC` 改成 `NET` (退回旧缺陷) ⇒ 仍必须红★** ★ |
| ★**证据等级** ★ | ★**[实测]** 三张表逐行 diff (★本机实跑 + 实读★) · ★**[实测]** `--expect-resolved` 21 → 18 (★本机实跑★) · ★**[实测]** `--selftest` 21/21 (★本机实跑★) · ★**[实测]** 受保护 md5 逐字节不变 (★本机 md5sum★) · ★**[官网]** 器件身份 = ★**TI TPS22991RAA** (★项目库内已登记: `HW/CORE_MODULE_SELECTION.md` L16 / `HW/POWER_RAIL_SPEC.md` L44 / 网表 `opn` 列 [官方] / 板封装 `UQFN-4 RAA`★) · ★**[推算]** 「本体行挂在 pin1 ⇒ 原理图符号 Value 变成料号」 (★由 `state/gen_kicad_sch.py` 的 `build_devices()` 取首行 value 实测确认★) · ★**[0数据]** TPS22991 的 RON / IQ 实测值 (★本单没查 ⇒ ★**没写进网表 value 串★; `HW/CORE_MODULE_SELECTION.md` 里的 RON 25mΩ 是项目库内既有登记, 本单未复核★) ★ |

### ★★15.3 · 本批【没落】的东西 (★逐条 + 卡在谁★) ★★

| 条目 | 归因 | 卡在谁 | 交卷单位置 |
|---|---|---|---|
| ★**R2 ×11 + R7 + R8 (13 条)** ★ | ★**B 类** ★ | ★**V-3** (★老板 / 项目总工★) ⇒ ★**降级④ (改读 BQ25896 遥测) 的话这一批【永远不落】 ⇒ 所以 DNP 的翻法也归 V-3, 本单不许先翻★** ★ | 交卷单 §2.1 + §3 |
| ★**R4 ×2 + R9 ×1 (3 条)** ★ | ★**C 类 (板侧那一趟)** ★ | ★**V-2 选型 (老板) + 板侧换封装/挪位置/重跑布线 ⇒ 网表侧落表一条都转不绿 (★ISS-230 实测 7→7★)** ★ | 交卷单 §2.2 + §3 |
| ★**R10 ×1** ★ | ★**B 类** ★ | ★**V-4** (★老板; 建议 680Ω★) ★ | 交卷单 §2.3 + §3 |
| ★**R3 的板侧 1 条 (板封装 `U_EN_SW` 的 `Value` 属性)** ★ | ★**C 类 (板侧那一趟)** ★ | ★**板侧同步清单 B-2 ⇒ 手工改 (★生成器不会自动改已在板上的封装★)** ★ | 交卷单 §2.4 + §3 |

### ★★15.4 · 受保护 md5 前后对照 (★第 3 批·本单起跑基线 ⇒ 交卷实测★) ★★

| 文件 | 前 (本单起跑) | 后 (交卷) | 变了? |
|---|---|---|---|
| ★**`HW/PCB/demo_mainboard.kicad_pcb`** ★ | ★**`611b869e13518c3c023fb178f91a0075`** ★ | ★**`611b869e13518c3c023fb178f91a0075`** ★ | ★**否 (受保护·逐字节不变)★** |
| ★**`HW/PCB/demo_mainboard.kicad_pro`** ★ | ★**`3e504d2be83152e337949723e909be1b`** ★ | ★**`3e504d2be83152e337949723e909be1b`** ★ | ★**否 (受保护·逐字节不变)★** |
| ★**`HW/netlist_v1.csv`** ★ | `3215020b6d4120e1b7728227effdc6d3` | `34132f7e40a241e1fae1476be0eafbd5` | ★**是 (★只有 L442 一行★)** ★ |
| ★**`HW/netlist_v1_pins.csv`** ★ | `a600afae493f5a7a6c55f46ad35ac89c` | `b21b743a7702d30729f0d653c15392df` | ★**是 (★只有 L531 一行★)** ★ |
| ★**`HW/BOM_v1.csv`** ★ | `92b51580867deca9f8b04af88d925d96` | `c195a117ff17490d4d1e1a5b8f1995a7` | ★**是 (★只有 L208 一行★)** ★ |
| ★**`HW/BOM_pseudo_refs_v1.csv`** ★ | `47e1659a42d8d3f6728ea653df1eb530` | `47e1659a42d8d3f6728ea653df1eb530` | ★**否** ★ |
| ★**`HW/netlist_v1.net`** ★ | `978ab59e297e6bb89f873b763569eccb` | `978ab59e297e6bb89f873b763569eccb` | ★**否** ★ |
| ★**`HW/SCHEMATIC_V1.md`** ★ | `b06298db21de27112def71d28ce2997b` | `b1fa5a0c17726037ff3407b31ecbb631` | ★**是 (★生成物·跟着网表走★)** ★ |
| ★**`HW/PCB/demo_mainboard*.kicad_sch` (11 个)** ★ | ★**各自不同 (★生成物含随机 UUID★)** ★ | ★**各自不同 (★`demo_mainboard_p1.kicad_sch` = `4e9691a0018511473886b7bd4f6f8587`★)** ★ | ★**是 (★生成物; ★**其中 U_EN_SW 符号的 `Value` 属性从 "5V 输入" 变成器件身份描述★)** ★ |
| ★**`state/gen_netlist.py`** ★ | `3c765729de34db50ee1b0ddd60c360a2` | `9dfb6771c9beb110021bba182f128c64` | ★**是 (★真源·一行★)** ★ |
| ★**`HW/check_netlist_selfconsistency.py`** ★ | `3b4d5b2061ec9f7011a1c9718e296d1a` | `19743c14bd50cd917551db0a6d642a39` | ★**是 (★EXPECT 5 个单元格 + selftest 用例4 的突变方向 + 用例名★)** ★ |
| ★**`HW/NETLIST_SELF_CONSISTENCY_SPEC.md`** ★ | `118bfabbf726b9fa9a59e6361a5f412c` | `d633265b4532a007643904d6a73140cf` | ★**是 (★锚点表整块重生成 + §1 ① / §2 表 / §5.3 / 新增 §5.4★)** ★ |
| ★**`HW/SCHEMATIC_LANDING_V1_LANDED.md`** ★ | `83c2deee2850956b1591acbe9173e480` | ★**本文件自身 (★md5 会随本节的写入而变 ⇒ 以交卷时 `md5sum` 实测为准★)** ★ | ★**是 (★本 §15★)** ★ |

★**★回滚副本★**: ★**`state/.bak_iss233/`** (★本单起跑基线: 13 个文件 + 11 个 `.kicad_sch` + `state/fragments/hw.yaml`★) ★

### ★★15.5 · 第 3 批复现命令 (★B6 自证★) ★★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses

# ★★7 条必跑门禁 (★ISS-233 落表后的实测口径★) ★★
python3 HW/check_netlist_selfconsistency.py                    # rc=0 (现状守卫; 锚点 160 条)
python3 HW/check_netlist_selfconsistency.py --selftest          # rc=0 (反向用例 21/21)
python3 HW/check_netlist_selfconsistency.py --expect-resolved   # rc=1 (★预期: 还有 18 条未落表★)
python3 state/check_netlist.py                                  # rc=0 (全过)
python3 state/check_netlist_pins.py                             # rc=0 (每个针脚归属唯一)
python3 state/check_sch_erc.py                                  # rc=0 (ERC=0)
python3 state/check_sch_pinfull.py                              # rc=0 (图上 584 脚 = 表里 584 脚)
python3 state/merge.py && python3 state/gate_check.py           # rc=0 (Q1 交付齐备率 18/18)

# ★★落表链路 (改源 → 重生成; ★板不碰★) ★★
python3 state/gen_netlist.py && python3 state/gen_kicad_net.py && \
python3 state/gen_netlist_pins.py && python3 state/gen_bom.py && \
python3 state/gen_schematic_pages.py && python3 state/gen_kicad_sch.py

# ★★受保护 md5 (必须逐字节不变) ★★
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro
# 611b869e13518c3c023fb178f91a0075 / 3e504d2be83152e337949723e909be1b

# ★★锚点表 (规格页 ⇄ 脚本 逐字一致) ★★
python3 HW/check_netlist_selfconsistency.py --emit-anchors | wc -l    # 162
```
