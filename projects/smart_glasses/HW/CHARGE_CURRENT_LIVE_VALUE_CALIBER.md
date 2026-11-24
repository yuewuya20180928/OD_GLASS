# CHARGE_CURRENT_LIVE_VALUE_CALIBER.md — 充电电流活值口径 (ISS-384 · hw-lead · 2026-11-24)

> ★★★**一句话**: ★**三份 HW 活文档的充电电流活值仍停在 `0.822` 旧系数档; 网表侧 2026-11-16 已落 680Ω + 1.216 系数; 本单把文档追平, 网表一个字没动** ★★★
> ★★**本单 = 纯文档口径单** ⇒ ★**零写板 / 零落表 / 零改既有闸 / 零外发 / 不代拍** ★★
> ★**唯一权威源 (只读 · 已签收)**: `MECH/HINGE_POWER_CALC.md` §0-A / §0-A.1 对照表 (ISS-229 · mech-lead · 已 verified) + `MECH/hinge_power_calc.json` 的 `rilim_table` ⇒ 复现 `python3 MECH/hinge_power_calc.py --json` (rc=0) ★

---

## §0 一句话结论 (先看这条)

| 项 | 结论 |
|---|---|
| **文档侧现状 (开工前)** | `HW/PCB_OUTLINE_60x15.md` / `HW/J_CHG_SELECTION.md` / `HW/POWER_BUDGET_V3.md` 三份活文档里, 充电电流活值仍写着 **`0.822` 旧系数** 派生的 `ICHG 0.82A` / `单 pin 0.411A` / `余量 1.22×` / `充电 ~29min` / `充电 ~51min` 等 ⇒ 共 **34 处活值** (逐处见 §1) ★ |
| **网表侧现状 (开工前)** | `HW/netlist_v1.csv` L47/L48 的 `R_ILIM` **早在 2026-11-16 就落成 `680Ω`** (V-4 裁定), note 里写的是 `1.216 / 1.071` ⇒ ★**网表侧早就对了** ★ |
| **本单动作** | ★**把三份文档追平到已落表的真值** ⇒ 不是「改一个数」, 是「消除文档与网表的口径分叉」 ★ |
| **本单边界** | ★**网表 / 脚表 / BOM / 板文件一个字节都没动** ⇒ 板要对着一个不再变的网表继续画 (合「板只改一次」纪律 ①) ★ |
| **现行档位 (已落表事实)** | `R_ILIM` = **680Ω** ⇒ **ICHG 0.697A / 单 pin 0.349A / 触点余量 1.43×** ⇒ 当前系数 **1.216 @3.70V** / **1.071 @4.20V** ★ |
| **不代拍** | `R_ILIM` 最终取哪一档是【老板 / PM 域】(V-4 已裁 680Ω 是已落表事实) ⇒ ★**本单只报「文档与已落表真值不一致」, 不提新档位建议** ★ |

---

## §1 逐处订正表 (★每一行 = 文件:行号 → 旧值逐字 → 新值逐字 → 权威出处 → 证据等级★)

> ★**口径纪律**: 表内「旧值逐字」= 原页原文, **一个字没删** (追加式订正块 · 老字保留); ★**标「历史留痕」的格 (PCB_OUTLINE L151 / L193) 不进本表, 见 §2** ★

### `HW/PCB_OUTLINE_60x15.md` (14 处)

| 文件:行号 | 旧值 (逐字) | 新值 (逐字) | 权威出处 | 证据等级 |
|---|---|---|---|---|
| `HW/PCB_OUTLINE_60x15.md` L20 | 充电电流档位 = R_ILIM 390Ω (IINMAX ≈1.00A / ICHG ≈0.82A / 单 pin 0.411A / 充电 ~29min); 300Ω 档正式判死 (单 pin 0.534A) | 充电电流档位 = R_ILIM 680Ω (V-4 已落表 2026-11-16) (IINMAX ≈0.57A / ICHG ≈0.697A / 单 pin 0.349A / 充电 ~34min); 390Ω 档正式判死 (单 pin 0.608A 超 0.5A 触点上限 21.6%); 300Ω 档正式判死 (单 pin 0.790A) | MECH/HINGE_POWER_CALC.md §0-A.1 对照表 + rilim_table (680Ω max 行) | [实测] |
| `HW/PCB_OUTLINE_60x15.md` L23 | 电芯内阻发热 (0.10Ω · 114mW @1.07A / ~45mW @0.82A) 贴皮肤侧 | 电芯内阻发热 (0.10Ω · 48.6mW @0.697A) 贴皮肤侧 (680Ω 档 max) | MECH/HINGE_POWER_CALC.md §0-A.1 对照表 (680Ω 档 max 行: 电芯发热 48.6 mW) | [实测] |
| `HW/PCB_OUTLINE_60x15.md` L132 | 0.411A/触点 余量 1.22× | 0.349A/触点 余量 1.43× (680Ω 档真值; 390Ω 档 0.608A 超 0.5A 上限 21.6% ⇒ 判死) | MECH/HINGE_POWER_CALC.md §0-A.1 + rilim_table (680Ω max 行) | [实测] |
| `HW/PCB_OUTLINE_60x15.md` L143 | 1.07 A · 0.534A · ❌ 正式判死 (单 pin > 0.5A 天花板) | ICHG 1.581 A · 单 pin 0.790 A · ❌ 正式判死 (超 0.5A 天花板 58%) | MECH/HINGE_POWER_CALC.json rilim_table (300Ω max 行) | [实测] |
| `HW/PCB_OUTLINE_60x15.md` L144 | 0.82 / 0.91 / 1.00 A · 0.82A · 0.411A · ✅ 余量 1.22× (对 0.5A 触点) | 0.82 / 0.91 / 1.00 A (IINMAX 不变) · ICHG 1.216 A · 单 pin 0.608 A · ❌ 余量 0.82× (超 0.5A 触点上限 21.6%) ⇒ 390Ω 档判死 | MECH/HINGE_POWER_CALC.md §0-A.1 + rilim_table (390Ω max 行) | [实测] |
| `HW/PCB_OUTLINE_60x15.md` L146 | 0.47 / 0.52 / 0.57 A · 0.47 A · 0.236A · ✅ 余量最大, 充电 ~51min | 0.47 / 0.52 / 0.57 A (IINMAX 不变) · ICHG 0.697 A · 单 pin 0.349A · ✅ 余量 1.43× · 充电 ~34min | MECH/HINGE_POWER_CALC.json rilim_table (680Ω max 行) | [实测] |
| `HW/PCB_OUTLINE_60x15.md` L149 | 390Ω max 档充电 ~29.20min / 典型 32.08min | 680Ω max 档充电 ~34.41min / 典型 37.81min (390Ω 档 max 19.74min / 典型 21.68min, 但该档已判死) | MECH/HINGE_POWER_CALC.json rilim_table t_charge_min (400mAh 口径) | [实测] |
| `HW/PCB_OUTLINE_60x15.md` L154 | 电流可以从 470Ω 提到 390Ω (充电 ~29min) | 该提速叙事作废 (390Ω 档已判死 · 单 pin 0.608A); 现行档位 = 680Ω (充电 ~34min) | MECH/HINGE_POWER_CALC.md §0-A.1 + rilim_table | [实测] |
| `HW/PCB_OUTLINE_60x15.md` L178 | TS 参考地被 1A 回流抬高 14-32mV = 0.44-0.99°C 停充门限偏差 | TS 参考地被 0.697A 回流抬高 20.9mV = 0.65°C 停充门限偏差 (680Ω 档 max) | MECH/HINGE_POWER_CALC.md §M-4 表 (680Ω 行) | [实测] |
| `HW/PCB_OUTLINE_60x15.md` L234 | iin = (320/r, 355/r, 390/r); ichg = tuple(v*0.822 for v in iin) | iin = (320/r, 355/r, 390/r); ichg = tuple(v*1.216 for v in iin)   # ISS-384 订正: 旧系数 0.822 是 1.216 的倒数 (方向反了) ⇒ 作废; 1.216@3.70V / 1.071@4.20V | MECH/HINGE_POWER_CALC.md §0-A + HW/CHARGE_BOARD_SPEC.md §2.4 | [实测] |
| `HW/PCB_OUTLINE_60x15.md` L276 | R_ILIM 390Ω → IINMAX 0.82/0.91/1.00A, ICHG 0.82A, 单 pin 0.411A · [推算] (×0.822 换算) | R_ILIM 680Ω → IINMAX 0.47/0.52/0.57A, ICHG 0.697A, 单 pin 0.349A · [实测] (×1.216 换算) | MECH/HINGE_POWER_CALC.md §0-A.1 + rilim_table | [实测] |
| `HW/PCB_OUTLINE_60x15.md` L277 | 300Ω 档判死 (单 pin 0.534A > 0.5A) | 300Ω 档判死 (单 pin 0.790A > 0.5A · 超 58%) | MECH/HINGE_POWER_CALC.json rilim_table (300Ω max 行) | [实测] |
| `HW/PCB_OUTLINE_60x15.md` L280 | 390Ω 档的 ICHG 触点余量 1.22× · 0.5A ÷ 0.411A | 680Ω 档的 ICHG 触点余量 1.43× · 0.5A ÷ 0.349A | MECH/HINGE_POWER_CALC.json rilim_table (680Ω max 行) | [实测] |
| `HW/PCB_OUTLINE_60x15.md` L283 | 电芯内阻 0.10Ω / 发热 45mW@0.82A | 电芯内阻 0.10Ω / 发热 48.6mW@0.697A | MECH/HINGE_POWER_CALC.md §0-A.1 (680Ω 档 max 行) | [实测] |

### `HW/J_CHG_SELECTION.md` (16 处)

| 文件:行号 | 旧值 (逐字) | 新值 (逐字) | 权威出处 | 证据等级 |
|---|---|---|---|---|
| `HW/J_CHG_SELECTION.md` L15 | 只有 pin1/pin2 载流 (0.411A) · 0.5A 可用, 余量 1.22× | 只有 pin1/pin2 载流 (0.349A) · 0.5A 可用, 余量 1.43× (680Ω 档真值) | MECH/HINGE_POWER_CALC.md §0-A.1 + rilim_table (680Ω max 行) | [实测] |
| `HW/J_CHG_SELECTION.md` L16 | 390Ω 档的单 pin 0.411A 就不合格, 会被迫退到 680Ω (充电 51min) · 0.411A > 0.35A | 680Ω 档的单 pin 0.349A 合格 (充电 ~34min) · 0.349A < 0.35A (680Ω 档单 pin 0.349A vs 0.5A) | MECH/HINGE_POWER_CALC.md §0-A.1 + rilim_table (680Ω max 行) | [实测] |
| `HW/J_CHG_SELECTION.md` L17 | 单 pin 0.534A 超过任何 0.5mm pitch FPC ZIF 的 0.5A 额定上限 | 单 pin 0.790A 超过任何 0.5mm pitch FPC ZIF 的 0.5A 额定上限 | MECH/HINGE_POWER_CALC.json rilim_table (300Ω max 行) | [实测] |
| `HW/J_CHG_SELECTION.md` L32 | R_ILIM = 390Ω → ICHG 0.822A (max) → 单 pin 0.411A | R_ILIM = 680Ω (V-4 裁定 2026-11-16) → ICHG 0.697A (max) → 单 pin 0.349A | 网表 R_ILIM 行 (V1.9) + MECH/HINGE_POWER_CALC.md §0-A.1 | [实测] |
| `HW/J_CHG_SELECTION.md` L89 | ICHG = IINMAX × 0.822 → 0.822 A | ICHG = IINMAX × 1.216 (η·Vbus/Vbat @VBAT=3.70V) → 0.697 A | MECH/HINGE_POWER_CALC.md §0-A + HW/CHARGE_BOARD_SPEC.md §2.4 | [实测] |
| `HW/J_CHG_SELECTION.md` L90 | 单 pin (pin1 / pin2 并联) → 0.411 A | 单 pin (pin1 / pin2 并联) → 0.349 A | MECH/HINGE_POWER_CALC.json rilim_table (680Ω max 行) | [实测] |
| `HW/J_CHG_SELECTION.md` L91 | 双 pin 合计 → 0.822 A | 双 pin 合计 → 0.697 A | MECH/HINGE_POWER_CALC.json rilim_table (680Ω max 行) | [实测] |
| `HW/J_CHG_SELECTION.md` L99 | 390Ω 档 (0.411A) \| 300Ω 档 (0.534A) | 680Ω 档 (0.349A) | 390Ω 档 (0.608A) | MECH/HINGE_POWER_CALC.md §0-A.1 对照表 | [实测] |
| `HW/J_CHG_SELECTION.md` L101 | ❌ 0.411 > 0.35 不合格 | ✅ 0.349 < 0.35 合格 | MECH/HINGE_POWER_CALC.json rilim_table (680Ω max 行) | [实测] |
| `HW/J_CHG_SELECTION.md` L102 | 只有 pin1/pin2 载流 0.411A, pin3/4 回流 0.411A ... ✅ 0.411 < 0.5, 余量 1.22× · ❌ 0.534 > 0.5 | 只有 pin1/pin2 载流 0.349A, pin3/4 回流 0.349A ... ✅ 0.349 < 0.5, 余量 1.43× · ❌ 0.790 > 0.5 | MECH/HINGE_POWER_CALC.md §0-A.1 + rilim_table (680Ω max 行) | [实测] |
| `HW/J_CHG_SELECTION.md` L103 | R_ILIM 300Ω → ICHG 1.069A → 单 pin 0.534A | R_ILIM 300Ω → ICHG 1.581A → 单 pin 0.790A | MECH/HINGE_POWER_CALC.json rilim_table (300Ω max 行) | [实测] |
| `HW/J_CHG_SELECTION.md` L108 | 390Ω 档就自动不合格 → 会被迫退到 680Ω (充电 51min, 而 390Ω 是 29min) | 680Ω 档单 pin 0.349A 合格 (充电 ~34min) ⇒ 两种读法都过, 没有解释空间 | MECH/HINGE_POWER_CALC.md §0-A.1 + rilim_table | [实测] |
| `HW/J_CHG_SELECTION.md` L110 | 单 pin 0.534A 超过 0.5mm pitch FPC ZIF 的 0.5A 额定上限 | 单 pin 0.790A 超过 0.5mm pitch FPC ZIF 的 0.5A 额定上限 | MECH/HINGE_POWER_CALC.json rilim_table (300Ω max 行) | [实测] |
| `HW/J_CHG_SELECTION.md` L161 | 0.5A → 70% → 0.35A, 而我们的单 pin 是 0.411A —— 恰好夹在中间 | 0.5A → 70% → 0.35A, 而我们的单 pin 是 0.349A —— 在 0.35A 之上, 不夹中间 | MECH/HINGE_POWER_CALC.json rilim_table (680Ω max 行) | [实测] |
| `HW/J_CHG_SELECTION.md` L168 | 300Ω 档 (单 pin 0.534A) 在 0.5mm pitch 下无解 | 300Ω 档 (单 pin 0.790A) 在 0.5mm pitch 下无解 | MECH/HINGE_POWER_CALC.json rilim_table (300Ω max 行) | [实测] |
| `HW/J_CHG_SELECTION.md` L197 | R_ILIM = 390Ω → ICHG 0.822A → 单 pin 0.411A | R_ILIM = 680Ω → ICHG 0.697A → 单 pin 0.349A | 网表 R_ILIM 行 (V1.9) + MECH/HINGE_POWER_CALC.md §0-A.1 | [实测] |

### `HW/POWER_BUDGET_V3.md` (5 处)

| 文件:行号 | 旧值 (逐字) | 新值 (逐字) | 权威出处 | 证据等级 |
|---|---|---|---|---|
| `HW/POWER_BUDGET_V3.md` L360 | CC 段电池电流 (×Vbat/Vbus/η ≈ 0.822) | CC 段电池电流 (×η·Vbus/Vbat = 1.216 @3.70V / 1.071 @4.20V) | MECH/HINGE_POWER_CALC.md §0-A + HW/CHARGE_BOARD_SPEC.md §2.4 | [实测] |
| `HW/POWER_BUDGET_V3.md` L362 | 1.07 / 1.18 / 1.30 A · 0.88 / 0.97 / 1.07 A | CC 段电池电流 1.298 / 1.437 / 1.581 A (300Ω 档 ❌ 判死 · 单 pin 0.790A) | MECH/HINGE_POWER_CALC.json rilim_table (300Ω 行) | [实测] |
| `HW/POWER_BUDGET_V3.md` L363 | 0.82 / 0.91 / 1.00 A · 0.67 / 0.75 / 0.82 A | CC 段电池电流 0.997 / 1.107 / 1.216 A (390Ω 档 ❌ 判死 · 单 pin 0.608A 超 21.6%) | MECH/HINGE_POWER_CALC.json rilim_table (390Ω 行) | [实测] |
| `HW/POWER_BUDGET_V3.md` L477 | R_ILIM 300Ω / 390Ω → IINMAX 1.07/1.18/1.30 A / 0.82/0.91/1.00 A | 不变 (IINMAX = KILIM/R_ILIM 是官方输入电流上限, 与 ICHG 口径无关); 补: 现行档位 = 680Ω → IINMAX 0.47/0.52/0.57 A | BQ25896 datasheet KILIM 320/355/390 AΩ [官方] | [实测] |
| `HW/POWER_BUDGET_V3.md` L524 | R_ILIM=300R->IINMAX 1.07/1.18/1.30A, CC 0.88-1.07A; 390R->0.82/0.91/1.00A, CC 0.67-0.82A | R_ILIM=300R->IINMAX 1.07/1.18/1.30A, CC 1.30-1.58A; 680R->0.47/0.52/0.57A, CC 0.57-0.70A | MECH/HINGE_POWER_CALC.json rilim_table | [实测] |

> ★**合计**: 订正行 **35 行** = ★**活值 34 处** + 1 处「数值不变·说明行」 (`HW/POWER_BUDGET_V3.md` L477 — IINMAX = KILIM/R_ILIM 是官方输入电流上限, 与 ICHG 口径无关 ⇒ 不变) ★
> ★**「现行档位真值」补记 (680Ω · 三份文档的订正块里都已带上)**: IINMAX 0.47 / 0.52 / **0.57 A** · **ICHG 0.697 A** · **单 pin 0.349 A** · **触点余量 1.43×** (对 0.50 A 触点工作上限) · 充电 ~34min (max 档) · 皮肤侧 40.1°C (MECH §0-A.1 对照表) ★

---

## §2 「历史留痕 vs 活值」分账表 (★本单的核心: 证明我不是在做无脑全局替换★)

| 分类 | 处数 | 具体位置 | 本单处置 |
|---|---|---|---|
| **① 活值 (旧系数派生, 已订正)** | 34 | 见 §1 逐处订正表 | ★**追加式订正块** (三份文档末尾各一个) ⇒ 旧字保留 + 新值追平 ★ |
| **② 历史留痕 (ISS-230 作废标记)** | 2 | `HW/PCB_OUTLINE_60x15.md` **L151** 与 **L193** (两行语境均含「作废」二字, 原文用「倒方向的 0.822 系数」解释作废原因) | ★**一个字不许删** ⇒ ★**不进 §1 订正表** ⇒ 新闸按【语境】豁免, **不红** ★ |
| **③ 网表里的合法历史说明 (落表真源)** | 2 | `HW/netlist_v1.csv` **L47 / L48** (`R_ILIM` 行 note 字段, 原文「旧口径写的 (VBAT/VBUS)/η = 0.822 是它的倒数」) | ★**一个字不许动** (动它 = 违「板只改一次」· 本单是文档口径单不是落表单) ⇒ ★**新闸的扫描范围不许包含网表/脚表/BOM** ⇒ 不红 ★ |
| **④ 订正块自身的旧值留痕** | 35 | 三份文档的 ISS-384 订正块「旧值 (逐字)」列 | ★**刻意留痕** (给读者看「原来写的是什么」) ⇒ 闸按【订正表行】豁免 ★ |

> ★★**分账小结**: ★**全库 `0.822` 共 4 类去向** — 「① 活值 34 处 ⇒ 追平」 / 「② ISS-230 作废标记 2 处 ⇒ 保留」 / 「③ 网表合法说明 2 处 ⇒ 保留」 / 「④ 订正块留痕 ⇒ 保留」 ⇒ ★**没有一处被无脑替换掉** ★★
> ★★**为什么必须分账**: ★**若全局替换 `0.822` → `1.216`, 就会把 ISS-230 的作废标记和网表的合法说明一起改掉** ⇒ ★**作废标记被抹掉 = 证据链断** ⇒ ★**网表被改 = 板要重画 (2-4 周 + ¥4-8K)** ⇒ ★**本单用「语境判 + 锚点登记」把这两条红线焊死** ★★

---

## §3 根因: 为什么这些数会被改错 (★用 MECH/HINGE_POWER_CALC.md §0-A 的原话口径★)

> ★★★**根因 (MECH §0-A 原话)**: ★★**buck 降压的功率守恒是 `Pout = eta·Pin` ⇒ `ICHG/IIN = eta·Vbus/Vbat`, 而不是它的倒数 `(Vbat/Vbus)/eta`** ★★ ⇒ ★**改正后 `Vbat=3.70V ⇒ 1.216` (本文主口径 = 取最坏: Vbat 最低 ⇒ 系数最大 ⇒ 温度最高) · `Vbat=4.20V ⇒ 1.071` (CV 段末端) · 旧值 `0.822` = `(Vbat/Vbus)/eta` = 1.216 的倒数 ⇒ 方向反了 ⇒ 已作废** ★★★

| 环节 | 旧口径 (错) | 新口径 (真) | 后果 |
|---|---|---|---|
| 系数方向 | `ICHG = IIN × (VBAT/VBUS)/η` = **0.822** | `ICHG = IIN × η·(VBUS/VBAT)` = **1.216 / 1.071** | ★**偏小 1.48 倍** ⇒ 电流被低估 ⇒ 触点天花板判据失效 ★ |
| 390Ω 档 ICHG | 0.822 A | **1.216 A** | ×1.479 |
| 390Ω 档 单 pin | 0.411 A ✅ | **0.608 A ❌ (超 0.50 A 触点上限 21.6%)** | ★**「余量 1.22×」变成「余量 0.82×」** ⇒ 该档判死 ★ |
| 470Ω 档 单 pin | 0.341 A ✅ | **0.505 A ❌ (超 1.0%)** | ★**「有 0.16A 余量」是假的** ⇒ 该档判死 ★ |
| 680Ω 档 单 pin | 0.236 A ✅ | **0.349 A ✅ (余量 1.43×)** | ★**唯一成立的档** ⇒ V-4 落表 680Ω ★ |
| 充电时间 | 300:22 / 390:29 / 470:35 / 680:51 min | **300:15 / 390:20 / 470:24 / 680:34 min** | 电流↑ ⇒ 时间↓ ⇒ ★**旧时间按旧系数 ⇒ 也全错** ★ |
| TS 参考地偏移 | 1A ⇒ 14-32 mV ⇒ 0.44-0.99 °C | **680Ω 档 0.697A ⇒ 20.9 mV ⇒ 0.65 °C** | ★**O-4 行的停充门限偏差数错** ★ |

> ★★**为什么这个错特别危险**: ★**它让 390Ω 档看起来「余量 1.22×, 安全」** ⇒ ★**若按旧余量放行 390Ω, 单 pin 0.608A 打在 0.5A 触点上限上 ⇒ 过热/退镀/接触电阻漂移** ⇒ ★**这类错不会在评审时被发现, 只会在客户端表现为「充不进电/发烫/掉线」** ⇒ ★**这就是必须建闸的理由: 让「旧系数」在文档里无法再以【活值】形态存活** ★★
> ★★**闸的判定面盲区 (本单最有价值的发现)**: ★**既有闸 `HW/check_netlist_selfconsistency.py` 的 R10 判据只扫一个文件 `chgspec` = `HW/CHARGE_BOARD_SPEC.md`** ⇒ ★**那份文件今天 `grep -c "0.822"` = 0 (已清干净) ⇒ R10 现在是绿的, 但它【压根没看】下面这三份文件** ⇒ ★★**同样的旧系数活值, R10 看不见 ⇒ 这就是「闸的判定面有洞」的机器事实** ⇒ ★**本单在【新闸】里另写一份 (不改既有闸的判据表) ★★

---

## §4 证据分级表

| 结论 / 数据 | 证据等级 | 依据 |
|---|---|---|
| 本页 §1 的**旧值逐字** (原页原文) | **[实测]** | 本机 `grep -nE` + 逐行实读三份 HW 文档 (行号见 §1) |
| 本页 §1 的**新值逐字** (ICHG / 单 pin / 余量 / 充电时间) | **[实测]** | 本机实跑 `python3 MECH/hinge_power_calc.py --json` (rc=0) ⇒ `MECH/hinge_power_calc.json` 的 `rilim_table` (ISS-229 · mech-lead · 已 verified) |
| 当前系数 **1.216 @3.70V / 1.071 @4.20V** | **[实测]**(复现) + **[推算]**(来源) | 同上脚本的 `ichg_factor` 字段; 系数源 = `HW/CHARGE_BOARD_SPEC.md` §2.4 (ISS-220 第 1 批已改正) |
| `ICHG = IIN × η·(Vbus/Vbat)` 的**物理式** | **[推算]** | buck 功率守恒 `Vbus·IIN·η = Vbat·ICHG` (MECH §0-A 同口径) |
| `IINMAX = KILIM/R_ILIM` (KILIM 320/355/390 AΩ) | **[官方]** | BQ25896 datasheet (经 `HW/CHARGE_BOARD_SPEC.md` §2.4 引) |
| 680Ω 档**皮肤侧 40.1 °C** / 电芯发热 48.6 mW | **[推算]** (MECH 实算) | `MECH/HINGE_POWER_CALC.md` §0-A.1 对照表 (680Ω 档 max 行) ⇒ ★**本单只引用, 不另算一套** ★ |
| TS 参考地偏移 20.9 mV / 0.65 °C | **[推算]** (MECH 实算) | `MECH/HINGE_POWER_CALC.md` §M-4 表 (680Ω 行) |
| 旧系数 `0.822` 的**作废判定** | **[实测]** (ISS-230 留痕) | `HW/PCB_OUTLINE_60x15.md` L151 / L193 两处作废标记 (保留不动) |
| `R_ILIM` = **680Ω** 是**已落表**事实 | **[实测]** | `HW/netlist_v1.csv` L47/L48 + `HW/netlist_v1_pins.csv` + `HW/BOM_v1.csv` (V-4 裁定 2026-11-16) |
| 网表 L47/L48 的 2 处 `0.822` 属**合法历史说明** | **[实测]** | 本机实读网表 note 字段 (原文「旧口径写的 (VBAT/VBUS)/η = 0.822 是它的倒数」) |
| 板件指纹 (零写板) | **[实测]** | `md5sum HW/PCB/demo_mainboard.kicad_pcb` 开工前后逐字相同 |
| **本单未查到的外部数据** | **[0数据]** | 见 §5 (本单 0 条硬阻塞) |

---

## §5 未决项

| # | 事项 | 状态 | 处置 / 降级方案 |
|---|---|---|---|
| 1 | 本单是否有硬阻塞 | ★**0 条** | — |
| 2 | J_CHG 座体单触点额定是否 ≥0.5A (官方规格页) | ★**已闭合 [官网]** | ★**main 2026-11-24 09:3x 裁决 ⇒ 已把规格页逐字条款 + 官方参数钉进 `HW/J_CHG_SELECTION.md` §7 追加块**: 70% 降额条款逐字原文 "Note 1 : When passing the current through all of the contacts, use 70% of the current rating." (Hirose [FH12] Series Catalog · Nov.1.2026 · Adaptive FPC/FFC contact specifications 表 Note 1) + FH12-10S-0.5SH(55) Rated Current **0.5A** + 10p 尺寸 A=4.5/B=8.1/C=9.1/D=5.57 (官网) ⇒ ★**页码 = [0数据]** (本机直连官网/Farnell PDF 被拦: 21 字节 stub / rc=124) ⇒ 降级方案 = 条款原文 + 文档名 + 版本日期 + 小节名 + URL 四锚点已齐, 判定结论不受页码影响 ★ |
| 3 | KILIM 在低电流档的 trim 是否同 320/355/390 AΩ | **[0数据]** | ★**降级方案**: 按 datasheet 值取最坏 (max 390 AΩ) ⇒ 若实际偏大, IINMAX 上升 ⇒ ★**但 680Ω 档仍远低于 390Ω 档, 结论方向不变** (MECH §7-N7 同口径) |
| 4 | 板端实测 (ICHG / 触点温升) | **[0数据]** (板端 0 条实测) | ★**降级方案**: EVT 阶段按 `HW/EVT_RELIABILITY_TEST_ITEMS.md` 实测复核; ★**在此之前所有 ICHG 数一律标 [推算]/[实测](脚本) 而非 [实测](板端)** ★ |
| 5 | 电流探针/治具 | **[0数据]** | ★**降级方案**: 选型见 ISS-257 (已 verified) 的治具口径; ★**本单不外发任何询价** (老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料) ★ |

> ★★**外发纪律声明**: ★**本单没有发出任何邮件 / 询价 / 问询 / 采购** ⇒ ★**所有缺口一律【自己网上查 + 标证据等级 + 查不到就写降级方案】** ⇒ ★**没有「等原厂回信 / 等外部确认」这类挂着当阻塞项的东西** ★★

---

## §6 已收裁决 (★main 2026-11-24 09:3x 回覆我方 5 条 need★)

| need | main 裁决要点 | 本单怎么落 |
|---|---|---|
| `iss384_rilim_档位确认` | ★**维持 680Ω** (V-4 已裁且已落表 2026-11-16) · main 从权威 JSON 重算: 680Ω 档 max = IINMAX 0.573529 / ICHG 0.697412 / 单 pin 0.348706 (< 0.35A 保守降额线 ✓) / 余量 1.43× / 充电 34.41min · 390Ω 单 pin 0.6080 (超 21.6% 判死) · 300Ω 单 pin 0.7904 判死 · ★**档位是老板域, main 只登记「只有 680Ω 同时活」这个机器事实** | ★**本单全部文档活值已追平到 680Ω** ⇒ ★**不代拍, 不提新档位建议** ✓ |
| `iss384_jchg_触点额定` | 判定标准用「单触点额定 ≥0.5A」, 书面确认走 RFQ (零外发) · ★**补一件事: 把规格页的逐字条款 + 页码钉进 `HW/J_CHG_SELECTION.md` §7** | ★**已做**: §7 追加块钉入 70% 条款逐字原文 + 0.5A 额定 + 10p 官方尺寸; ★**页码 = [0数据] + 降级方案** (四锚点已齐) ✓ |
| `iss384_evt_板端实测` | EVT 阶段实测, **不阻塞本趟** · 权威源 `evidence.board_measured` = 0 条 ⇒ 一切 ICHG 数标 [推算]/[实测](脚本) 不冒充实测 · ★**知悉型, 不是等外部回复** | ★**§5 第 4 条照此登记 [0数据] + EVT 降级方案** ✓ |
| `iss384_gate_hook_decision` | ★**与「板只改一次」那一趟同批挂** (先例 ISS-300/309/312/315 + ISS-372 U7 + ISS-379 Q8 + ISS-381 B4 + ISS-382 C4) · ★**闸与它要防的那批事同批生效才是真防线** · ★**挂链动作由 main 统一做, 不许 agent 自挂** | ★**本闸零挂链** (`grep -c` = 0) ⇒ ★**与 main 裁决一致** ✓ |
| `iss384_netlist_note_390ohm_residual` | ★**另开「网表 note 订正」单, 只订 note 文本, 不动元件值 / 不改板 / 不改 680Ω 裁定** · ★**该动作属「落表」⇒ 进「板只改一次」那一趟同批做, 不许另起一趟碰网表** | ★**本单零落表 ⇒ 网表 L483/L493 与脚表 L502 三处 390Ω 活值本单一个字没动** ⇒ ★**已登记为「板只改一次」那一趟的待办, 不是本单的活** ✓ |

---

## 机器块 (★格式同 `MECH/HINGE_POWER_CALC.md` 的机器块写法★)

```yaml
charge_current_live_value:
  source: MECH/HINGE_POWER_CALC.md §0-A + §0-A.1 (ISS-229) + MECH/hinge_power_calc.json rilim_table
  repro: python3 MECH/hinge_power_calc.py --json   # rc=0
  landed_r_ohm: 680
  coef_main: 1.216        # ICHG/IIN = eta*Vbus/Vbat @ VBAT=3.70V (最坏档)
  coef_cv: 1.071          # @ VBAT=4.20V (CV 段末端)
  coef_legacy_void: 0.822 # 旧倒数方向系数 (已作废 · 仅留痕 · 不得当当前口径)
  contact_limit_a: 0.50   # J_CHG 单触点工作上限
  rilim:
    - r_ohm: 300
      ichg_max: 1.581
      per_pin_max: 0.790
      margin_to_0p5A: 0.63
      verdict: DEAD
    - r_ohm: 390
      ichg_max: 1.216
      per_pin_max: 0.608
      margin_to_0p5A: 0.82
      verdict: DEAD
    - r_ohm: 470
      ichg_max: 1.009
      per_pin_max: 0.505
      margin_to_0p5A: 0.99
      verdict: DEAD
    - r_ohm: 680
      ichg_max: 0.697
      per_pin_max: 0.349
      margin_to_0p5A: 1.43
      verdict: PASS
```

---

## 闸 (★本单新建 · 零挂链★)

| 项 | 值 |
|---|---|
| 新闸文件 | `HW/check_charge_current_live_value.py` (★**新建**·★**未改任何既有闸**★) |
| 裸跑 | `python3 HW/check_charge_current_live_value.py` ⇒ rc=0 |
| 自测 | `python3 HW/check_charge_current_live_value.py --selftest` ⇒ rc=0 · 末行 `ALL TESTS PASS` |
| 扫描范围 | `HW/PCB_OUTLINE_60x15.md` · `HW/J_CHG_SELECTION.md` · `HW/POWER_BUDGET_V3.md` (★**不含**网表/脚表/BOM/板文件★) |
| 判定方式 | ★**按语境判, 不按子串判**: 作废标记行 (含「作废」) ⇒ 不红; 订正块「锚点」列登记过的行 ⇒ 不红; 其余出现旧值 token ⇒ 红并点名 文件:行号 ★ |
| ★**零挂链** | ★**本闸【没有】挂进 `state/gate_check.py`** (挂链是 main 的地界) ⇒ 实测 `grep -c check_charge_current_live_value state/gate_check.py` = **0** ★ |
| 既有闸 | `HW/check_netlist_selfconsistency.py` md5 `5281b65dbcc9af7bccc6c79a9066812d` 开工前后逐字相同 ⇒ ★**R10 的判定面只在【新闸】里另写一份, 它的判据表一个字没改** ★ |

---

## 关联

- 权威源: `MECH/HINGE_POWER_CALC.md` (ISS-229 · mech-lead) · `MECH/hinge_power_calc.json`
- 网表真源: `HW/netlist_v1.csv` L47/L48 (`R_ILIM` = 680Ω · V-4 裁定 2026-11-16)
- 已改正的同源文档: `HW/CHARGE_BOARD_SPEC.md` §2.4 / §3.4 (★**既有闸 R10 只扫它**★)
- 上游留痕: `HW/PCB_OUTLINE_60x15.md` L151 / L193 (ISS-230 作废标记 · 保留不动)
- 交卷页: `HANDOFF/2026-11-24_hw-lead_ISS384_充电电流活值口径收口与R10判定面盲区.md`
