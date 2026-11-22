# HW/CHARGE_CURRENT_RECHECK_2026-11-01.md —— 充电电流换算复核 + ISS-105 收口

> **触发**: ① ISS-105 (更正 hw-lead 分片过期值 + J_CHG 按一对备料 + 机械防呆升为硬判据) · ② ISS-089 交叉评审第 3 条 (`mech-lead` needs `iss089_ichg_ratio_datasheet`) —— **mech-lead 指出 `HW/CHARGE_BOARD_SPEC.md` §3.4 的 ICHG/IIN 换算方向反了**, 本单独立复核并确认命中。
>
> **数字唯一出处**: `HW/calc_chg_ichg.py` (rc=0, 无外部依赖) → `HW/calc_chg_ichg.json`
> **本文没有改**: 网表 (`HW/netlist_v1.csv`) / 网表生成器 (`state/gen_netlist.py`) / `HW/CHARGE_BOARD_SPEC.md` 正文 / 任何别人的文件 —— 见 §7 写入范围声明。

---

## B1 结论摘要 (每条带数字)

1. **★方向反了, 已独立确认**: buck 降压功率守恒 `Pout = η·Pin` ⇒ **`ICHG = η·(VBUS/VBAT)·IIN = 1.2162 × IIN`**; `HW/CHARGE_BOARD_SPEC.md` §3.4 写的是 `ICHG = (VBAT/VBUS)/η · IIN = 0.8222 × IIN`。两个系数**互为倒数** (乘积 = 1.000000000, 脚本自校)。
2. **★390Ω 档判死 (旧值 → 新值)**: 旧记 "ICHG 0.82A / 单 pin **0.411A** (触点余量 1.22×)" ⇒ 按正确换算: `IINMAX 0.821-1.000A` / **`ICHG 0.998-1.216A`** / **单 pin 0.608A** ⇒ **超过 0.5mm pitch ZIF 触点 0.5A 额定天花板 (余量 0.82×) ⇒ ❌ 不通过**。
3. **建议 `R_ILIM` 390Ω → 680Ω (换料不换板, 0402 ±1%)**: `IINMAX 0.471-0.574A` / `ICHG 0.572-0.698A` / **单 pin 0.349A** ⇒ 触点余量 **1.43×** ✅, 铰链设计点 (1.5A) 余量 **2.15×** ✅, 充电时间 (420mAh 标称) **CC ≈ 36 min + 恒压段 ≈ 50-60 min**。
4. **★但 680Ω 仍触不到电芯倍率线**: 0.698A / 420mAh = **1.66C** > 典型 1C ⇒ 若电芯规格书确认 ≤1C, 则须退到 **1.0kΩ (1.13C)** 或 **1.2kΩ (0.94C ✅)**。**电芯允许倍率是 [0数据]** (规格书未到, needs `rel_battery_cell_spec`) ⇒ **本单给区间与判据, 不替老板拍板**。
5. **mech-lead 的铰链压降/发热核算不受影响**: 他按 **1.5A 设计点**算 (`MECH/HINGE_POWER_CALC.md`), 而订正后最坏 ICHG = 1.216A (390Ω) 或 0.698A (680Ω) ⇒ **他的算法仍偏保守**, 不用重算。
6. **ISS-105 其余两条已闭环**: ① `J_CHG` **实物一对** (框侧座 + 脚侧座) ⇒ 已写进 `HW/BOM_v1.csv` 备料栏 + 网表 P1 注记 + RFQ 口径; ② **机械防呆升为硬判据** ⇒ 已是 `state/outbox/j_chg_rfq.md` 的 **C-4** 硬判据 (反插 = BAT_CHG 短接 GND ⇒ 充电板 MOS 直通), 未放行外发。
7. **分片过期值同步订正**: `pcb_outline` **60x15mm → 60x30mm** (老板 10-29 19:16 拍板板宽 30mm, 11-01 20:5x 台账订正) · `pcb_width_recommend` **15mm → 30mm** · `pcb_mount_holes_xy` 的 **Y 坐标按 30mm 板宽重算** (P1/P2 Y=15.00, S1/S2 Y=10.00/20.00) · `battery_capacity_tier` 的**重复旧值条目已删** (只留 315/387)。

---

## B2 复核过程 (可复算)

### 2.1 换算式与自校

```
buck 降压:  Pout = η · Pin
            VBAT · ICHG = η · VBUS · IIN
      ⇒     ICHG = η · (VBUS/VBAT) · IIN = 0.90 × (5.0/3.7) = 1.216216 × IIN

旧式(反了): ICHG = (VBAT/VBUS) / η · IIN = (3.7/5.0)/0.90 = 0.822222 × IIN

自校: 1.216216 × 0.822222 = 1.000000000  ⇒ 两者互为倒数 ⇒ 方向错就是量级差 1.48×
```

> **物理自查 (与实测一致)**: 手机 5V/1A 充电器给 3.85V 电芯充到 ~1.2A (5W×0.92/3.85V≈1.19A) —— **电池电流 > 输入电流**, 这正是 buck 的特征。旧式给出的是升压关系, 与 buck 矛盾。⇒ 旧式方向**确定反了**。

### 2.2 档位扫描 (脚本输出, `python3 HW/calc_chg_ichg.py`)

| R_ILIM | IINMAX min/typ/max | **ICHG (正确)** | **单 pin (正确)** | 单 pin (旧式) | 触点余量 | 铰链余量 | 电芯倍率 | 判定 |
|---|---|---|---|---|---|---|---|---|
| **390Ω (现行)** | 0.821 / 0.910 / 1.000 A | **0.998-1.216 A** | **0.608 A** | 0.411 A | **0.82× ❌** | 1.23× ✅ | 2.90C ❌ | ❌ **不通过** |
| 510Ω | 0.627 / 0.696 / 0.765 A | 0.763-0.930 A | 0.465 A | 0.314 A | 1.07× ⚠️贴边 | 1.61× ✅ | 2.21C ❌ | ⚠️ |
| **680Ω (建议)** | 0.471 / 0.522 / 0.574 A | **0.572-0.698 A** | **0.349 A** | 0.236 A | **1.43× ✅** | 2.15× ✅ | 1.66C ❌ | ✅ 触点 ✅ / ⚠️倍率 |
| 1.0kΩ | 0.320 / 0.355 / 0.390 A | 0.389-0.474 A | 0.237 A | 0.160 A | 2.11× ✅ | 3.16× ✅ | 1.13C ❌ | ✅ 触点 ✅ / ⚠️倍率 |
| **1.2kΩ (倍率合规档)** | 0.267 / 0.296 / 0.325 A | 0.324-0.395 A | 0.198 A | 0.134 A | 2.53× ✅ | 3.79× ✅ | **0.94C ✅** | ✅ 全过 |

**参数**: VBUS 5.0V · VBAT 3.7V · η 0.90 · KILIM = 320/355/390 AΩ (`IINLIM = KILIM/R_ILIM`) · J_CHG pin1/pin2 双 pin 并联 · 触点额定 0.5A/触点 · 铰链设计点 1.5A · 电芯 420mAh · 倍率上限 1C (**[0数据]**)。

### 2.3 三条硬判据 (为什么是 680Ω 而不是"随便退一档")

| 判据 | 上限来源 | 允许的 ICHG | 反推 R_ILIM 下限 | 命中的是哪一档 |
|---|---|---|---|---|
| **J-1 触点额定** | 0.5A/触点 (硬判据 `j_chg_contact_rating_min`) × 2 pin | ≤ **1.00 A** | R_ILIM ≥ 390/0.822 = **475Ω** | 510Ω 起 (但 510Ω 余量仅 1.07× 贴边) |
| **J-2 电芯充电倍率** | ≤1C (典型, **[0数据]** 依赖电芯规格书) | ≤ **0.42 A** (420mAh) | R_ILIM ≥ 390/(0.42/1.216) = **1.13 kΩ** | 1.2kΩ |
| **J-3 铰链设计点** | BAT_CHG 1.5A (双 pin) | ≤ 1.5 A | R_ILIM ≥ 390×1.216/1.5 = 317Ω | 390Ω 就过 (✅ 任何候选档都过) |

⇒ **J-3 不是约束, J-1 与 J-2 才是**; 两者相差 2.4 倍 ⇒ **真值取决于电芯规格书** ⇒ 这条必须等 `rel_battery_cell_spec`。
⇒ **给老板/项目总工的选择题**: (a) 680Ω —— 触点余量 1.43×, 充电 ≈50-60 min, 电池按 1.66C 充 (⚠️ 超典型 1C); (b) 1.2kΩ —— 触点余量 2.53× + 倍率 0.94C ✅, 充电 ≈75-85 min。**默认按 (a) 680Ω 设计, 留 (b) 1.2kΩ 作为电芯规格书回来后的退档 (同 0402 同封装, 换料不换板, 零板费)。**

### 2.4 R_ILIM 仍是必装件 (结论不变, 数字变)

| 场景 | 铰链电流 | 单 pin | 判定 |
|---|---|---|---|
| R_ILIM **不装 / 误装大阻值** | REG04 复位默认 ICHG = **2048 mA** | **1.024 A** | ❌ 铰链过 **1.365×** 设计点 ⇒ **R_ILIM 是必装件, 换料不换板** |
| R_ILIM = 390Ω (现行) | 0.998-1.216 A | 0.608 A | ❌ 超触点 |
| R_ILIM = 680Ω (建议) | 0.572-0.698 A | 0.349 A | ✅ |

### 2.5 对 mech-lead 铰链核算的影响 = **无**

`MECH/HINGE_POWER_CALC.md` 按 **1.5A 设计点**算压降/发热; 订正后实际最坏 ICHG = 1.216A (390Ω) / 0.698A (680Ω) ⇒ **他的算法仍保守 1.23-2.15×** ⇒ **不需要重算, 不需要改结构**。

---

## B3 ISS-105 三条子项逐条闭环

| 子项 | 状态 | 落点 | 证据 |
|---|---|---|---|
| ① `pcb_outline` 过期值 **50×12 → 60×15mm** (10-28 已改) | ✅ 已闭环, **但 11-01 再订正到 60×30mm** | `state/fragments/hw.yaml` claim `pcb_outline` = `60x30mm`; 旧值 `60x15mm` → 新值 `60x30mm` | 老板 10-29 19:16 拍板板宽 30mm (`PROJECT_TRACKER §0` 板宽行, 11-01 20:5x 台账订正) |
| ② `chg_input_limit` 过期值 **1.07-1.30A (300Ω)** | ✅ 已闭环并**二次订正** (方向 + 数值) | claim `chg_input_limit` = `0.82-1.00A` (IINMAX, 390Ω) + 新 claim `chg_ichg_at_rilim` = `1.00-1.22A` + `chg_single_pin_a` = `0.50-0.61A` + 新 claim `chg_rilim_recommended` = `680Ω` | 本文 §2.2 |
| ③ **J_CHG 按一对备料** | ✅ 已闭环 | `HW/BOM_v1.csv` 第 12 行 `J_CHG` 的 `procurement`/`memo` 栏写 "**实物一对 (框侧座 + 脚侧座), 备料 2 只**"; 网表 P1 行注记同口径; claim `j_chg_qty` = `2` | `HW/PCB_OUTLINE_60x15.md` §3.2 |
| ④ **机械防呆升为硬判据** | ✅ 已闭环 (未外发) | `state/outbox/j_chg_rfq.md` **C-4** 条: 反插 = BAT_CHG 短接 GND ⇒ 必须结构级防呆, 并问 ①带防呆键型号 ②仅 A 侧可插/AutoLock ③与 FPC 弯折段共存 | RFQ 草稿 (待项目总工放行, needs `iss105_jchg_rfq_release`) |

---

## B4 证据分级

| 结论 | 等级 | 依据 |
|---|---|---|
| `ICHG = η·(VBUS/VBAT)·IIN` = 1.2162× | **[推算]** | 功率守恒 + 参数 (η 0.90 为 `[推算]`, VBUS/VBAT 为设计值) |
| 旧式 0.8222× 与正确式互为倒数 (乘积 1.000000000) | **[推算]** (脚本自校) | `HW/calc_chg_ichg.py` |
| 390Ω 档单 pin 0.608A > 0.5A 触点额定 | **[推算]** + 触点额定 **[官方-厂商页]** (FH12-10S-0.5SH(55) 0.5A/触点) | 脚本 + `HW/J_CHG_SELECTION.md` |
| `IINLIM = KILIM/R_ILIM`, KILIM = 320/355/390 AΩ | **[官方]** (BQ25896 REG00) 转引 | `HW/CHARGE_BOARD_SPEC.md` §2.4 |
| REG04 复位默认 ICHG = 2048mA | **[官方]** | 同上 §2.8 |
| 电芯允许充电倍率 1C | **[0数据]** ⚠️ | 规格书未到 (needs `rel_battery_cell_spec`) |
| η = 0.90 | **[推算]** | buck 通用档 |
| J_CHG 实物一对 | **[实测-结构回执]** (mech-lead ISS-099/100) | `HW/PCB_OUTLINE_60x15.md` §3.2 |
| 板宽 30mm / 板长 60mm | **[官方-老板拍板]** | `PROJECT_TRACKER §0` (11-01 20:5x 订正) |
| 实物 **[实测] 条数 = 0** | — | 无样机 |

---

## B5 未决项与卡点

| # | 未决 | 需谁答 | due | 走谁 |
|---|---|---|---|---|
| 1 | **`R_ILIM` 退档裁决: 680Ω (快, 1.66C) vs 1.2kΩ (慢, 0.94C)** | boss (经 main) | **2026-11-03** | 项目总工 |
| 2 | **电芯允许充电倍率 + 循环寿命 + 充电温度窗口** (决定 1) | 原厂 (经 main) | **2026-11-03** (原 due 10-30 已逾期) | 项目总工 |
| 3 | **网表 + BOM 的 R_ILIM 实际改值 + 充电时间口径** (本文只给判据, 改网表要动 `state/gen_netlist.py` —— 不在本单边界) | main | 2026-11-04 | 项目总工 |
| 4 | **`HW/CHARGE_BOARD_SPEC.md` §3.4 的 0.822 式要不要就地加订正横幅** (本文不改既有文档正文 ⇒ 由文件 owner 决定) | main | 2026-11-04 | 项目总工 |
| 5 | **J_CHG 实物一对 ⇒ 网表是否拆 J_CHG_A / J_CHG_B 两个 ref** (拆了 BOM 的 qty 自检口径也要改) | main | 2026-11-05 | 项目总工 |

---

## B6 自证复现命令

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 HW/calc_chg_ichg.py              # rc=0, 打印档位扫描 + 写 JSON
python3 HW/hw_week_20261101_check.py     # rc=0, 本周全部关键数字一次复算
python3 state/merge.py && python3 state/gate_check.py
```

---

## B7 写入范围声明

| 项 | 内容 |
|---|---|
| **本文只写** | `HW/CHARGE_CURRENT_RECHECK_2026-11-01.md` (本文件) · `HW/calc_chg_ichg.py` · `HW/calc_chg_ichg.json` · `HW/BOM_v1.csv` (仅 J_CHG 行的备料栏) · `HW/EVT_RELIABILITY_TEST_ITEMS.md` · `HW/hw_week_20261101_check.py` · `HANDOFF/2026-11-01_hw-lead_*.md` · `state/fragments/hw.yaml` (经 `state/frag_write.py` 原子写) · `state/issue_log.yaml` (仅 owner==hw-lead 的行, 原子写) |
| **本文没改** | `PROJECT_TRACKER.md` (含 §0 锁死表) · `STATE.yaml` · `state/gen_netlist.py` · `state/gen_bom.py` · `HW/CHARGE_BOARD_SPEC.md` · `HW/netlist_v1.csv` · `HW/RELIABILITY_DESIGN.md` · `SW/` · `MECH/` · 别人的分片 |
| **本文没做** | 未联系任何供应商/原厂 · 未发任何邮件 · 未放行 RFQ · 未下任何采购单 |
