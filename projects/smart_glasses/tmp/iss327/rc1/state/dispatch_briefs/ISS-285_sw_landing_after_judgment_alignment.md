★**ISS-285 · sw-lead 任务书 —— ★★【落表之后: SW 侧三道判据过期】★★ (★纯分析 + 判据口径收口类 · 零写板 · 零落表★)**

> ★**派活人**: 项目总工 (main / moli) · ★**派活时刻**: ★**2026-11-17 11:0x** ★ · ★**job**: cron `775d9893` (ARS45 继续执行后继计划) ★
> ★**owner**: sw-lead · ★**verify_by**: main · ★**单号**: ISS-285 · ★**零外发** ★
> ★**本单性质**: ★**内部活 · 门禁/判据口径侧** ★ ⇒ ★**零写板 · 零落表 · 零改网表/脚表/BOM · 不替老板拍板** ★

---

## ★① 病灶 (★main 2026-11-17 10:5x 本机实跑, 原样 rc, 不抄任何交卷报告★)

★**背景**: ★**老板 09:49 拍板「按照你的建议执行」⇒ A1 (V-3=E) + A2 (V-4=680) 已于 09:58:16 授权落表 (rc=0)** ⇒ ★**网表 / 脚表 / BOM 三件的 md5 当场变了** ★

★**main 实跑 (★2026-11-17 10:5x★)**:
```
$ python3 SW/tools/check_demo_panel_spec.py            ⇒ rc=0    (★R1~R7 全过 ★)
$ python3 SW/tools/check_demo_panel_spec.py --selftest ⇒ rc=0    (★SELFTEST 22/22 ★)
$ python3 SW/tools/timing_check.py                     ⇒ rc=1    (★SELFTEST 68/71 ⇒ 3 条红 ★)
$ python3 HW/check_step1_parts_spec.py                 ⇒ rc=0    (8/8)
$ python3 HW/check_onepass_preflight_coverage.py       ⇒ rc=1    (★P6 三个基线 md5 过期 ★ ⇒ ★**归 hw-lead 的 ISS-283, 不是本单★**)
```

★**★本单只管 `SW/tools/timing_check.py` 那 3 条红★ (★`check_onepass_preflight_coverage.py` 的红已在 ISS-283 (hw-lead) 的任务书里 ★**不许你去改 hw-lead 的文件**★)**:

| # | 红的判据 (★原文★) | 为什么红 (★main 实查★) |
|---|---|---|
| ★1★ | ★`网表锚点: 现行网表 md5 ∈ 落表台账登记的状态 (落表前 / 落表后)` ★ | ★`SW/SW_MD5_BASELINE_LEDGER.md` §1 锚点块里 `source_ledger.entries[]` 的网表那一条, `md5` 还停在 **ISS-257 那跳 `e06c1dd6…`** ⇒ ★而盘上已是落表后 `2f17650c…` ⇒ 不在允许集里 ⇒ 红★ |
| ★2★ | ★`网表锚点: 锚点 ↔ 落表台账 ↔ 盘上真源 三方对账成立 (不许悄悄换真源)` ★ | ★同上 (★`timing_check.py` L244~L247: `盘上真源 md5 ≠ 锚点登记 md5` ⇒ 判 BAD★) ⇒ **★看起来像「真源被换了」, 实际是「授权落表后锚点没前移」★** |
| ★3★ | ★`F4' 实读: ADC 装机链是 VBUS_DET_D; BAT_DET 三颗全 DNP` ★ | ★落表后 BAT_DET 三颗**已改成必装** (★网表 L182 `R_BAT_DET_1` = 100k ±1% 必装 · L183 `R_BAT_DET_2` = 60k ±1% 必装 · L184 `C_DET_BAT` = 100nF ±10% 必装★) ⇒ ★**这条期望值过期了** (★它还在要求「三颗全 DNP」★) |

---

## ★② ★★根因一句话: 【判据源不一致】★★

★**同一个事实 (「网表当前合法 md5 是多少」), 现在有两个判决源, 结果一个绿一个红**:

| 判据 | 判决源 | 落表后读数 |
|---|---|---|
| ★**`SW/tools/check_demo_panel_spec.py` R6** ★ | ★**落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` 里该文件的最新落表记录 (链头)** ★ (★ISS-275 口径★) | ★**绿** ✅ (★链头自动前移到 09:58 那跳★) |
| ★**`SW/tools/timing_check.py` 网表锚点** ★ | ★**SW 台账 §1 锚点块 `source_ledger.entries[]` 里那一跳的 `md5` 字段 (冻结值)** ★ | ★**红** ❌ (★锚点没前移★) |

★**⇒ 这不是「有人偷换真源」, 是【授权落表后, 第二个判据源没跟上】★ ⇒ ★**修法必须落在「让两个判据源同源」上, 不许靠放宽判据来消红** ★

---

## ★③ ★★开工前置 (★硬约束, 先看这条★)★★

★**★ISS-283 (hw-lead · 在飞) 的三件落表 (★A3 = V-2=1 + W-4 `Q_PG` pad1↔pad3 + G-5 亮度档★) 一落, 网表 / 脚表 / BOM 的 md5 会【再变一次】★★** ⇒ ★**⇒ 你现在把锚点前移到 09:58 那跳, 等 ISS-283 落完又会被打红一次 ⇒ ⇒ 白干★**

★**⇒ 本单分两段, 你自己判断当前处在哪一段 (★开工前先查 `state/issue_log.yaml` 里 ISS-283 的 status★)**:

| 情形 | 本单动作 |
|---|---|
| ★**ISS-283 还没落 verified** ★ | ★**只做【只读分析 + 方案页 + 自测设计 + 交叉引用】** ★ ⇒ ★**不许改 `SW/SW_MD5_BASELINE_LEDGER.md` 的锚点 · 不许改 `timing_check.py` 的任何判据 · 不许改期望值** ★ ⇒ ★**交付一份「等 ISS-283 落表后一次性套用」的补丁方案 + 反向用例设计** ★ ⇒ ★**登记 need 给 main (★说清「等哪个单号落完再套」★)** ★ |
| ★**ISS-283 已落 verified** ★ | ★**做全套 (B1 + B2 + B3) ★** ⇒ ★**锚点前移到 ISS-283 落表后的最新一跳 (★台账链头★) ⇒ `timing_check.py` 回 rc=0 ⇒ 落交卷单** ★ |

---

## ★④ 要交的三件 (★每件都能独立验收★)

### ★B1 · 判据源同源化 (★网表锚点 ×2 ⇒ 绿★)

★**目标**: ★**`timing_check.py` 的网表锚点判据与 `check_demo_panel_spec.py` R6 读【同一个判决源】** ★ ⇒ ★**判据方向不许变 (★「盘上 ≠ 合法状态 ⇒ 红」必须保留★)** ★

★**两条做法 (★你定细节, 下面四条不许破★)**:
1. ★**判据方向不许变**: ★**盘上 md5 不在【台账登记的合法状态集合】⇒ 仍必须红** ★
2. ★**不许把「取不准」放宽成「取最近一条」** ⇒ ★**fail-closed 那条 (链头不唯一 / 链断 / 链头无单号 ⇒ 红) 一条都不许动** ★
3. ★**不许把落表台账当「锚点可写集合」** ⇒ ★**落表台账 append-only + 链完整性的防线不许松** ★
4. ★**不许弱化 ISS-275 已跑通的那条链头逻辑** ⇒ ★**改完 `check_demo_panel_spec.py` 算出的【链头 / 链 / 产出单号】必须与改前逐字相同** ★

### ★B2 · F4' 期望随落表更新 (★第 3 条红 ⇒ 绿★)

★**现状**: 期望 = 「★**BAT_DET 三颗全 DNP**★」 ⇒ ★**落表后已改成必装 ⇒ 期望过期★**
★**要求**: ★**期望改成「BAT_DET 三颗必装 (V-3=E 落表后)」** ★ ⇒ ★**★但判据强度不许比原来弱★** ⇒ ★**反向用例必须能抓住相反情形 (★把三颗改回 DNP ⇒ 这条必须变红★)** ★ ⇒ ★**证据出处 = `HW/netlist_v1.csv` L182/L183/L184 + 落表台账 §16 (老板凭据)★**

### ★B3 · 反向用例 (★至少 4 条, 每条贴原样 rc + 期望红组 vs 实际红组★)

| # | 构造 | 期望 |
|---|---|---|
| ① | ★**盘上网表 md5 落在台账登记的任何状态之外 (伪造一个 md5)** ★ | ★**红** ★ |
| ② | ★**落表台账里那一行四项不齐 (单号 / 文件名 / 前后 md5)** ★ | ★**红** ★ |
| ③ | ★**链头不唯一 (台账里有两条指向同一文件)** ★ | ★**红** (★fail-closed 不许动★) ★ |
| ④ | ★**把 BAT_DET 三颗改回 DNP (期望值被改坏)** ★ | ★**红** ★ |
| ⑤ | ★**正向对照: 一切如常 ⇒ rc=0** ★ | ★**绿** (★证明闸不是恒红★) ★ |

### ★B4 · 回归 (★别的闸一条不许红★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 SW/tools/check_demo_panel_spec.py; echo "rc=$?"           # 期望 rc=0 (R1~R7 全过)
python3 SW/tools/check_demo_panel_spec.py --selftest; echo "rc=$?"  # 期望 rc=0 (★条数只许增不许减 ★)
python3 SW/tools/timing_check.py; echo "rc=$?"                   # 期望 rc=0 (71/71)
python3 HW/check_step1_parts_spec.py; echo "rc=$?"               # 期望 rc=0
python3 state/merge.py && python3 state/gate_check.py; echo "rc=$?"  # 期望 rc=0 / rc=0
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro \
       HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
# ★★板 611b869e… / .kicad_pro 3e504d2b… 必须逐字节不变★★
```

---

## ★⑤ 交卷物 (★4 件★)

1. ★**交卷单** `HANDOFF/2026-11-17_sw-lead_ISS285_落表后SW判据口径收口.md` (★B1~B6 六块齐全 + 反向用例原样 rc★) ★
2. ★**方案/补丁页** (★§③ 情形一 ⇒ 交【方案页 + 待套用补丁说明】; §③ 情形二 ⇒ 交【已套用 + rc 证据】★) ★
3. ★**落表台账锚点 / `timing_check.py` 判据改动** (★**只在 §③ 情形二才动**★ ⇒ ★**情形一不许碰这两个文件★) ★
4. ★**分片** `state/fragments/sw.yaml` (★走 `python3 state/frag_write.py --agent sw-lead` 原子写★ ⇒ ★**写完 `grep` 校验 `iss285` 在不在★★)

---

## ★⑥ 边界 (★违反就是不合格★)

★**零写板** · ★**零落表** (★网表/脚表/BOM 一个字节不许动★) · ★**不许动 ISS-275 那条已跑通的链头逻辑** · ★**不许放宽 fail-closed 三条** · ★**不许改 `HW/` / `MECH/` 的文件与分片** (★`HW/check_onepass_preflight_coverage.py` 的红**归 ISS-283 (hw-lead)** ⇒ ★**你不要碰它**★) · ★**零外发** · ★**不替老板拍板** · ★**不自签 issue_log** (★签字是 main 的活★) · ★**不许把整份大文件读进来** (★只 grep 你要改的那几行★)

---

## ★⑦ 纪律 (★这项目的老教训★)

★**交卷单第一件事就是 `write` 建骨架 (★哪怕只写 3 行标题 + 交付物清单★)** ★ · ★**长任务一律 `nohup ... > logs/iss285/x.log 2>&1 &` + 短轮询 (★前台长 exec = 被掐的头号原因★)** ★ · ★**单条 `exec` ≤ ~120 秒** ★ · ★**每 10 分钟至少一次写盘** ★ · ★**每落一件交付物就把 rc 追加进交卷单** ★ · ★**分片写完 `grep` 校验** ★
