# ISS-302 · hw-lead 交卷单 —— C_SYS / SYS_CHG 必装落表 + note 追加式订正 + BOM 加 20 µF

| 项 | 值 |
|---|---|
| 单号 | ISS-302 |
| owner | hw-lead (subagent) |
| 派活人 | 项目总工 (main / moli) · job cron `fb67af40` (ARS45 队列自动派活) |
| verify_by | main |
| 派活时刻 | 2026-11-18 00:5x (Asia/Shanghai) · ★brief 文件 mtime 00:51★ · cron fb67af40 重派僵尸 fixing |
| 性质 | 内部活 · 落表链侧 · **零写板** · 零改既有判据阈值 |
| 外发 | **零外发** |
| 本轮性质 | ★**cont1 续做 = 收尾 paperwork 单** (★落表主体已由上一趟做完并落盘★) |
| 实物实测 | ★**0 条** (★本机无板、无量具、无实物 ⇒ 全部结论只到纸面/官网级★) |

> 骨架 2026-11-18 00:1x 建；本轮 (cont1) 2026-11-18 00:5x~00:58 (本机 `date` 实读) 逐节填实。
> ★**本单是收尾单, 不是落表单** ⇒ 网表 / 脚表 / BOM / 落表台账 / `state/p10_rows.json` **一个字节不许再动**, 本轮只做 3 件 paperwork (交卷单填实 / 分片 / 闸复跑落盘)。★

---

## B1 依据

### ★B1-① 判决据 (TI 官网逐字)★

> ★**TI BQ25896 datasheet, 文献号 SLUSC76C (JULY 2015 – REVISED MAY 2018), §7 Pin Functions 表, SYS 脚 (pin 15,16) 原文逐字** ★:
>
> **"System connection point. The internal BATFET is connected between BAT and SYS. When the battery falls below the minimum system voltage, switch-mode converter keeps SYS above the minimum system voltage. Connect a 20uF closely to the SYS pin."**

★**证据等级 = [官网]** ★ · ★**本轮 hw-lead 两条独立途径各查一遍, 互相印证** ★:

| 途径 | 来源 | 读到的位置 | 结果 |
|---|---|---|---|
| ★**A · 本机留存的 TI 官方 PDF 转文本** ★ | `state/.cache_iss243/bq25896.pdf` (md5 `5f2c3958901c8841c7b698b71a16b927`, 2026-11-16 15:17 落盘) · `pdftotext` 输出 `state/.cache_iss243/bq25896.txt` | ★**L319~L327** ★ (SYS 行) | ★**逐字命中**: `SYS  15,16  P` → `...Connect a 20uF closely to the` / `SYS pin.` ★ |
| ★**B · 本轮联网自查 (2026-11-18 00:5x, 本机实跑)** ★ | ★**TI 官方文档页 `https://www.ti.com/lit/gpn/BQ25896`** ★ | Pin Functions 描述块 | ★**逐字命中**: `SYS 15,16 P System connection point. The internal BATFET is connected between BAT and SYS. ... Connect a 20uF closely to the SYS pin.` ★ |

⇒ ★**结论: `SYS_CHG` / `C_SYS` 必须必装, 且 SYS 脚必须挂 20 µF 到地 (紧靠 SYS pin)★** ★

### ★B1-② 由判决据推出的落表内容 (逐条标证据等级)★

| # | 结论 | 等级 | 推理依据 |
|---|---|---|---|
| 1 | ★`SYS_CHG` / `C_SYS` **DNP → 必装** ★ | ★**[官网]** ★ | ★TI §7 明令『Connect a 20uF closely to the SYS pin.』⇒ SYS 脚不许悬空★ |
| 2 | ★20 µF 挂 **充电板本地 PGND**, 紧靠 `U_CHG` pin15/16 ★ | ★**[官网]+[推算]** ★ | ★官网只说『closely to the SYS pin』; 『挂 PGND』= TI 同表 PGND 行原文『connect directly to the ground connection of input and output capacitors of the charger』★ |
| 3 | ★**不跨铰链引镜脚系统轨** ★ | ★**[推算]** ★ | ★充电板本地就有 PGND 地平面 ⇒ 20 µF 本地回路 ⇒ 无需把镜脚 RAIL_SYS 经 J_CHG 引过来★ |
| 4 | ★**不需要跨铰链多引 2 根电源 pin** ★ | ★**[推算]** ★ | ★由第 3 条直接推出 ⇒ ★**原 PM 裁决担心的那个代价不成立**★ |
| 5 | ★**充电路径不变** = IN · 内部 BATFET · BAT · 跨铰链 · 电芯 (反向阻断仍由 BATFET 提供) ★ | ★**[官网]+[推算]** ★ | ★datasheet SYS 行『The internal BATFET is connected between BAT and SYS.』★ |
| 6 | ★板面占用 **≈8 mm² (0805/1206)**, 不是 25×10mm ★ | ★**[推算]** ★ | ★0805 本体 2.0×1.25 = 2.50 mm² · 1206 本体 3.2×1.6 = 5.12 mm² · ★含焊盘与贴装工艺边 ≈8 mm²★ ⇒ 充电板 25×10mm 板面装得下, 不构成板面风险★ |
| 7 | ★**网名维持 `SYS_CHG`** (不并到镜脚 `RAIL_SYS`) ★ | ★**[推算]** ★ | ★充电板 SYS 与镜脚 RAIL_SYS 是两个网; 合并 = 把充电板 SYS 并到镜脚系统轨 = 电气冲突★ |
| 8 | ★`DNP 时不占板面` **这句是错的** ⇒ 删 ★ | ★**[推算]** ★ | ★DNP 也照样占 land pattern (位置 / 焊盘 / 阻焊 / 丝印都已在板上)★ |
| 9 | ★**一颗两脚电容不许一脚必装一脚 DNP** ⇒ L499 / L500 同步必装 ★ | ★**[推算]** ★ | ★一颗 2 脚电容只装一脚 = 电容悬空脚, 等于没装★ |
| 10 | ★封装 / OPN **仍 [待定]**, 不编造 ★ | ★**[0数据]** ★ | ★20 µF / 6.3 V / X7R 或 X5R 是 TI §10.2.2.3 的料号条件; 具体封装与厂商料号项目内无 ⇒ BOM 留『待定』★ |

### ★B1-③ 落表台账里的位置 (本单的痕迹在哪)★

| 项 | 位置 |
|---|---|
| ★**落表台账** ★ | ★`HW/SCHEMATIC_LANDING_V1_LANDED.md` ★**§19 (L1437 起)** ★ |
| ★**§19.1 一句话结论** ★ | L1439~L1441 |
| ★**§16.2 新旧 md5 前后对照** ★ | L1443~L1450 |
| ★**§19.3 逐条登记** ★ | ★**`<!--ISS302_ROWS-->` L1451~L1455** ★ (5 行 = 网表 / 脚表 / BOM / 板 / .kicad_pro) |
| ★**落表脚本** ★ | `state/_apply_iss302_csys_landing.py` (11,811 B · mtime 2026-11-18 00:21:02) |
| ★**落表真源** ★ | `state/p10_rows.json` (36,362 B · mtime 00:21:04) ★P10 充电板页器件级行数据 = `state/gen_netlist.py` 的唯一输入★ |

---

## B2 改动清单

### ★B2-① 网表三行 (★`HW/netlist_v1.csv` L498 / L499 / L500★)★

★**改法 = 走落表链 (改真源 → 重生成), 不是手改产物** ★:
`state/p10_rows.json` → `state/_apply_iss302_csys_landing.py` (改真源) → `gen_netlist` → `gen_kicad_net` → `gen_netlist_pins` → `gen_bom` → `gen_schematic_pages` → `gen_kicad_sch` ⇒ ★**三件产物 mtime 全 = 2026-11-18 00:21:08** ★

| 网表行 | 位号 / 脚 | dnp 改动 | note 追加式订正 (★老字逐字留痕, 一字不许删★) |
|---|---|---|---|
| ★**L498** ★ | `SYS_CHG` = `U_CHG pin15` → `U_CHG pin16` (★SYS 脚内部连线★) | ★**DNP → 必装** ★ | ★① PM 老裁决『电池与负载都在镜脚 ⇒ 充电板没有系统侧负载 · **VSYS 脚不接 (NC)**』★**标已作废**★ (被 [官网] TI §7 推翻) ② 『⚠️ [待原厂] SYS 悬空是否影响 BATFET 通路与充电环路 (TI 确认)』★**标已结**★ (TI §7 明令接 20 µF ⇒ SYS 不再悬空) ③ 『⚠️ 待裁决: 网名用 SYS_CHG 而不是 SYS』★**维持 SYS_CHG**★ ④ 追加『★SYS 必接 20 µF (TI §7); 不跨铰链引系统轨★』★ |
| ★**L499** ★ | `SYS_CHG` = `U_CHG pin16` → `C_SYS` | ★**DNP → 必装** ★ | ★① 『C_SYS 留位不装 = 保留 "电池挪镜框" 可回退分支』★**标已作废**★ ② 『本板 SYS 无负载, 装 20µF 只占 25×10mm 板面』★**标已作废**★ ⇒ 换成 ★**『≈8 mm² (0805/1206)』**★ ③ PM 裁决『VSYS 脚不接 (NC)』★**标已作废**★ ④ 追加规格行『★20 µF / 6.3 V · X7R 或 X5R (TI §10.2.2.3)★ · 封装/OPN 仍待选型 ⇒ BOM 留"待定", 不编造』★ |
| ★**L500** ★ | `PGND` = `C_SYS` → `U_CHG pin17+pin18` (★C_SYS 另一脚接地★) | ★**DNP → 必装** ★ | ★① 『DNP 时不占板面』★**标已作废**★ (★错: DNP 也照样占 land pattern★) ② 追加『★C_SYS 改为必装 ⇒ **本行 (C_SYS 另一脚) 同步改必装** (★一颗两脚电容不许一脚必装一脚 DNP★)』★ ③ 追加『★≈8 mm² (0805/1206)』★ |

★**老字留痕自证**: 三行原 note 全文 (含『VSYS 脚不接 (NC)』/『C_SYS 留位不装』/『25×10mm 板面』/『DNP 时不占板面』) **仍在网表里**, 只在其后追加 ★`★★订正 (ISS-302 · 2026-11-18 · hw-lead · 追加式 · 老字留痕)★`★ 标记的作废/维持/替换句 ⇒ ★**没有任何一个字被删掉**★ ★

### ★B2-② BOM 一行 (★`HW/BOM_v1.csv` L48★)★

```csv
C_SYS,1,20µF X7R 6.3V,C,必装,镜框充电板,P10,[官方],,待定,,待定,待定,已定型-无源件,"阻容感: 值/容差可定, **封装待板宽/贴装工艺定**"
```

| 列 | 值 |
|---|---|
| 位号 | `C_SYS` |
| 数量 | 1 |
| 规格 | **20 µF X7R 6.3 V** |
| dnp | ★**必装** ★ (落表前 = `DNP`) |
| 板 | 镜框充电板 (CHG_BOARD) |
| 页 | P10 |
| 证据 | **[官方]** (TI §7) |
| 封装/厂商料号 | ★`待定` (★不编造★) |

### ★B2-③ 落表前后 md5 对照表 (★本单唯一被允许变的三件 + 两件必须不变的★)★

| 文件 | 落表前 md5 | 落表后 md5 (★现值★) | 变了? | mtime |
|---|---|---|---|---|
| ★`HW/netlist_v1.csv` ★ | `37f62ac3f0b81d92ca7d48fdea717f07` | ★**`6aee500e60ba0732f83a9cf557ba90ab`** ★ | ★**是 (本单该有的)** ★ | 2026-11-18 00:21:08 |
| ★`HW/netlist_v1_pins.csv` ★ | `a4270120454aedf7a23c92cd8985c8a6` | ★**`9174309df1ec9411ac8e8d9e80ee386a`** ★ | ★**是 (本单该有的)** ★ | 2026-11-18 00:21:08 |
| ★`HW/BOM_v1.csv` ★ | `5d02bece9477ffce5fbe0193c7d5cce4` | ★**`5b9993992405904a60ac96a020b375d8`** ★ | ★**是 (本单该有的)** ★ | 2026-11-18 00:21:08 |
| ★`HW/PCB/demo_mainboard.kicad_pcb` ★ | `611b869e13518c3c023fb178f91a0075` | ★`611b869e13518c3c023fb178f91a0075` ★ | ★否 (零写板) ★ | 2026-11-06 07:07:17 |
| ★`HW/PCB/demo_mainboard.kicad_pro` ★ | `3e504d2be83152e337949723e909be1b` | ★`3e504d2be83152e337949723e909be1b` ★ | ★否 (零写板) ★ | 2026-11-04 23:47:30 |
| ★`HW/SCHEMATIC_LANDING_V1_LANDED.md` ★ | — | ★`d1a7765bb151cc69bb794dc6b6158264` ★ | ★台账本单该写 (§19 + ISS302_ROWS) ★ | 2026-11-18 00:22:44 |
| ★`state/p10_rows.json` ★ | — | ★`2836846d8ff503f98cc6d258a832664d` ★ | ★真源本单该改 ★ | 2026-11-18 00:21:04 |

---

## B3 落表台账痕迹 + 锚点重锚记录

### ★B3-① 台账痕迹 (逐条, 带行号)★

| 台账位置 | 内容 |
|---|---|
| ★`HW/SCHEMATIC_LANDING_V1_LANDED.md` L1437 ★ | ★**§19 · ISS-302 落表链 标题行** ★ (含 TI SLUSC76C §7 逐字引用 + 单号 + owner + 日期) |
| ★L1439~L1441 (§19.1) ★ | ★一句话结论: `SYS_CHG` / `C_SYS` DNP→必装 + note 追加式订正 + BOM 加 1 颗 20 µF 6.3 V X7R/X5R★ · 真源 = `state/p10_rows.json` · 落表脚本 = `state/_apply_iss302_csys_landing.py` · 产物一律重生成 (6 个生成器) |
| ★L1443~L1450 (§16.2) ★ | ★新旧 md5 前后对照表 (网表 / 脚表 / BOM / 板 / .kicad_pro 五行) + ★**受保护的两个必须逐字节不变**★ + ★**零写板自证 (md5 + mtime 双重)**★ |
| ★**L1451~L1455 (§19.3 `<!--ISS302_ROWS-->`)** ★ | ★**逐条登记 5 行**: L1451 网表 / L1452 脚表 / L1453 BOM / L1454 板 / L1455 .kicad_pro · 每行 = 台账行号 + 文件名 + 旧 md5 + 新 md5 + 落表时刻 (2026-11-18 00:3x) + 单号 (ISS-302)★ |

### ★B3-② ★**台账为准的新口径已被别的闸独立验过 (不是自说自话)**★

★`HW/check_workpack_state_values.py` 的 V6「受保护 5 件 md5 逐字节不变」段, ★**实跑原样输出** ★:

```
  OK   V6
     受保护 5 件 md5 逐字节不变: ✔
     ✔ ★HW/PCB/demo_mainboard.kicad_pcb: 盘上 md5 611b869e1351 == 保护基线 (★落表台账里没有变更行 ⇒ 纯 md5 硬保护·逐字节未变★) ⇒ 放行★
     ✔ ★HW/PCB/demo_mainboard.kicad_pro: 盘上 md5 3e504d2be831 == 保护基线 (★落表台账里没有变更行 ⇒ 纯 md5 硬保护·逐字节未变★) ⇒ 放行★
     ✔ HW/netlist_v1.csv md5 == 落表台账登记 6aee500e60ba0732f83a9cf557ba90ab (★落表单号 ISS-302·台账 L1437·§16.2★) ⇒ 未被绕过改动
     ✔ HW/netlist_v1_pins.csv md5 == 落表台账登记 9174309df1ec9411ac8e8d9e80ee386a (★落表单号 ISS-302·台账 L1437·§16.2★) ⇒ 未被绕过改动
     ✔ HW/BOM_v1.csv md5 == 落表台账登记 5b9993992405904a60ac96a020b375d8 (★落表单号 ISS-302·台账 L1437·§16.2★) ⇒ 未被绕过改动
```

⇒ ★**含义: 本单的落表是【走台账的正路】完成的, 不是手改产物绕过台账 (闸自己认出来了)★** ★

### ★B3-③ ★**谁需要重锚** (★按闸归属分家, 本单不越界★)★

| 闸 | 红了几条 | 红的具体条目 | ★归属 (谁去重锚)★ | ★本单做没做★ |
|---|---|---|---|---|
| ★`HW/check_workpack_state_values.py` ★ | ★**4 条** ★ | ★`W10_MD5_NETLIST` / `W10B_MD5_PINS` / `W10C_MD5_BOM` / `C07_B26_MD5_LEDGER` ⇒ 作业包/清单页里的现值没跟上盘面 ★ | ★**ISS-304** (不是本单) ★ | ★**没做** ★ (★本单不许改判据/不许改基线常量⇒ 只有 main 去更作业包与清单页的现值★) |
| ★`MECH/check_onepass_struct_crosscheck.py` ★ | ★**N6 3 条** ★ | ★网表 `37f62ac3…`→`6aee500e…` / 脚表 `a4270120…`→`9174309d…` / BOM `5d02bece…`→`5b999399…` ⇒ ★**这台闸只认硬基线, 不认【合法落表跳】**★ | ★**ISS-303** (不是本单) ★ | ★**没做** ★ |
| ★`HW/check_pin_function_labels.py` ★ | ★**15 条** ★ | ★**既有缺陷基线** (ISS-239 · 脚表功能串号) · ★**注意这不是本单落表造成的**★ | ★**既有基线** (★下一批落表里修★) | ★**没做** ★ (★ISS-299 的重锚成果: 『5 个基线全部一致 + 3 个基线在落表台账里可查 ✔』⇒ **不许再重锚**★) |

★**★注 (main 00:5x 读数 vs 本轮实跑, 以实跑为准)★**: main 00:5x 的表里 `HW/check_workpack_state_values.py` 写的是 **3 条** (`W10B` / `W10C` / `C07`); ★**hw-lead 本轮实跑是 4 条** (多了 `W10_MD5_NETLIST`) ★ ⇒ ★**以实跑为准, 4 条全归 ISS-304** ★

---

## B4 闸复跑现场 rc

★**复跑时间**: 2026-11-18 00:53~00:58 (Asia/Shanghai · 本机 `date` 实读) · ★**本机实跑, 非抄任何 agent 报告** ★
★**复跑日志**: ★**`logs/iss302/gates_rerun.log`** ★ (每道闸带 `### CMD` / `### output begin-end` / `### RC` / `### VERDICT`) · ★**runner 脚本 `logs/iss302/run_gates.sh`** ★ · ★**stdout `logs/iss302/run_gates.out`** ★

### ★B4-① 21 道闸复跑 rc 汇总 (★原样★)★

| # | 闸 | ★rc (原样)★ | 读数 |
|---|---|---|---|
| 1 | `HW/check_pin_function_labels.py` | ★**1** ★ | ★15 条缺陷 = **既有缺陷基线** (ISS-239) · 『5 个基线全部一致 + 3 个基线在落表台账里可查 ✔』⇒ **本单落表没打断它** |
| 2 | `HW/check_pin_function_labels.py --selftest` | 0 | — |
| 3 | `HW/check_step1_parts_spec.py` | 0 | 8/8 |
| 4 | `HW/check_onepass_preflight_coverage.py` | 0 | — |
| 5 | `HW/check_g1a7_selection_landed.py` | 0 | — |
| 6 | `HW/check_onepass_commit_order.py` | 0 | — |
| 7 | `HW/check_workpack_state_values.py` | ★**1** ★ | ★**4 条**: `W10_MD5_NETLIST` / `W10B_MD5_PINS` / `W10C_MD5_BOM` / `C07_B26_MD5_LEDGER` ⇒ **ISS-304** |
| 8 | `HW/check_fsin_rootcause.py` | 0 | — |
| 9 | `HW/check_netlist_selfconsistency.py` | 0 | — |
| 10 | `HW/check_netlist_selfconsistency.py --expect-resolved` | ★**1** ★ | ★4 条未落表 = **R3 / R4 / R9** (板封装 U_EN_SW 的 Value 还是脚级功能串 / D− 网上仍无 ESD 位号 / D_ESD_USB_D 仍只有 2 焊盘 / D_ESD_USB_D→J_USB_C 距离 47.99mm > 3.0mm) ⇒ ★**这是『整链重出 第 1 步』那一批的活, 不是本单**★ · 闸自己的话: 『现在缺陷仍在 ⇒ 本口径应当是红的; 等它们随『整链重出 第 1 步』落表后本口径才转绿』★ |
| 11 | `HW/check_land_row_anchors.py` | 0 | ★**落表台账锚点链绿** ⇒ 本单落表没把锚链打断★ |
| 12 | `SW/tools/check_demo_panel_spec.py` | 0 | — |
| 13 | `SW/tools/timing_check.py` | 0 | — |
| 14 | `SW/tools/check_onepass_sw_sync.py` | 0 | — |
| 15 | `MECH/check_onepass_mech_release.py` | ★**1** ★ | ★汇总 6 道闸 = **绿 5 / 红 1** ⇒ 红的那道 = `MECH/check_onepass_struct_crosscheck.py` ⇒ **ISS-303** |
| 16 | `MECH/check_mech_verdict_freshness.py` | 0 | — |
| 17 | `MECH/check_onepass_mech_sync.py` | 0 | — |
| 18 | `MECH/check_onepass_struct_crosscheck.py` | ★**1** ★ | ★N1~N5 全绿 (帧标签 / SoM 承载区零冲突 / 三条开口 / 必清空区净距 / 座体三方对照) · ★**N6 受保护 5 件 md5 红 3 条** ⇒ **ISS-303** |
| 19 | `MECH/check_demo_struct_truth.py` | 0 | — |
| 20 | `MECH/check_board_frame_coords.py` | 0 | — |
| 21 | `MECH/board_port_opening_s6_check.py` (被 15 号汇总调用) | 0 | — |

### ★B4-② 三道红闸的现场输出原样 (★只摘判据行, 一字不改★)★

**★`HW/check_workpack_state_values.py` ⇒ rc=1 (V4 段)★**:
```
  FAIL  V4
     现状值 == 盘面实测 (★实跑探针★): ❌
     ...
     ❌ id=W10_MD5_NETLIST: 实测值 '6aee500e60ba0732f83a9cf557ba90ab' 不在 fresh 原句里 ⇒ 订正句里的现值没跟上盘面
     ❌ id=W10B_MD5_PINS: 实测值 '9174309df1ec9411ac8e8d9e80ee386a' 不在 fresh 原句里 ⇒ 订正句里的现值没跟上盘面
     ❌ id=W10C_MD5_BOM: 实测值 '5b9993992405904a60ac96a020b375d8' 不在 fresh 原句里 ⇒ 订正句里的现值没跟上盘面
     ❌ id=C07_B26_MD5_LEDGER: 实测值 '6aee500e60ba0732f83a9cf557ba90ab' 不在 fresh 原句里 ⇒ 订正句里的现值没跟上盘面
```

**★`MECH/check_onepass_struct_crosscheck.py` ⇒ rc=1 (N6 段)★**:
```
  N6 受保护 5 件 md5 ..... ❌ 红
      · HW/PCB/demo_mainboard.kicad_pcb              611b869e13518c3c023fb178f91a0075 == 611b869e13518c3c023fb178f91a0075
      · HW/PCB/demo_mainboard.kicad_pro              3e504d2be83152e337949723e909be1b == 3e504d2be83152e337949723e909be1b
      · HW/netlist_v1.csv                            6aee500e60ba0732f83a9cf557ba90ab != 37f62ac3f0b81d92ca7d48fdea717f07
      · HW/netlist_v1_pins.csv                       9174309df1ec9411ac8e8d9e80ee386a != a4270120454aedf7a23c92cd8985c8a6
      · HW/BOM_v1.csv                                5b9993992405904a60ac96a020b375d8 != 5d02bece9477ffce5fbe0193c7d5cce4
...
【红】3 条
  ✗ N6 受保护件被改: HW/netlist_v1.csv 基线 37f62ac3f0b81d92ca7d48fdea717f07 ⇒ 现值 6aee500e60ba0732f83a9cf557ba90ab
  ✗ N6 受保护件被改: HW/netlist_v1_pins.csv 基线 a4270120454aedf7a23c92cd8985c8a6 ⇒ 现值 9174309df1ec9411ac8e8d9e80ee386a
  ✗ N6 受保护件被改: HW/BOM_v1.csv 基线 5d02bece9477ffce5fbe0193c7d5cce4 ⇒ 现值 5b9993992405904a60ac96a020b375d8
```
★**注意: N6 里板的两个 md5 是 `==` (没变)**, ★红的 3 条**全是纸面产物** (网表/脚表/BOM)★ ⇒ ★**零写板这一条, MECH 那道闸自己也认** ★

**★`HW/check_pin_function_labels.py` ⇒ rc=1 (基线段)★**:
```
  ── 【④/④b 受保护文件 md5 + 基线可追溯性】 5 个基线全部一致 + 3 个基线在落表台账里可查 ✔

  判定: ❌ 不过 (15 条缺陷) ⇒ ★当前是已知缺陷基线, 落表批次里修★
```

### ★B4-③ ★**收尾三道 (★分片写完后跑, 00:59:28~01:00:04★)****

★**日志**: ★**`logs/iss302/final_gates.log`** ★ (★runner `logs/iss302/run_final.sh`★) ★

| 闸 | ★rc (原样)★ | 读数 |
|---|---|---|
| ★`state/merge.py` ★ | ★**0** ★ | ★分片已合进 STATE.yaml (rc=0 ⇒ 合并成功)★ |
| ★`state/gate_check.py` ★ | ★**1** ★ | ★**Q1 = 18/18 ✔** · ★**Q7 钉板 md5 闸链 = 8/9 绿** ⇒ ★红的是「**钉板闸⑥ 作业包现状值闸**」⇒ ★**板那一趟不许开工** ★ |
| ★`state/issue_check.py` ★ | ★**0** ★ | — |

★**gate_check.py 现场原样 (★Q1 / Q7 段★)★**:
```
【Q1 交付齐备率】 18/18 个必填验收块齐全
...
【Q7 钉板 md5 闸链】 8/9 道绿 (★9 道全部 fail-closed 挂在门禁链里★)
   ✅ 钉板闸① FSIN 根因闸: rc=0
   ✅ 钉板闸② G1a-7 选型落表闸: rc=0
   ✅ 钉板闸③ 改板提交顺序闸: rc=0
   ✅ 钉板闸④ 作业包覆盖度闸: rc=0
   ✅ 钉板闸⑤ 脚表功能标签闸: rc=0
   ❌ 钉板闸⑥ 作业包现状值闸: rc=1
   ✅ 钉板闸⑦ 板框坐标闸: rc=0
   ✅ 钉板闸⑧ 结构真值闸: rc=0
   ✅ 钉板闸⑨ SW 侧合法改板通道闸: rc=0
   ★⇒ 板 md5 / 落表链 / 结构真值 出现漂移 ⇒ 板那一趟不许开工
...
  ❌ rc=1: ★★文档里的现状值漂了 / 订正没到位 / 判据不齐 ⇒ 那一趟会照着过期数字验收 ★★
```

★**★不掩饰声明★**: ★`state/gate_check.py` 的 rc=1 **不是本单的红**, ★**红的是钉板闸⑥ = 作业包现状值闸 = `HW/check_workpack_state_values.py` 的 V4 那 4 条** ★ ⇒ ★**归 ISS-304** ★ · ★**本单没有改任何判据 / 任何基线常量去消这个红** ★

### ★B4-④ ★**01:0x 并发复读 (★本单收尾时, 并发 agent 已经动手了★)★★

★**事实**: ★`MECH/check_onepass_struct_crosscheck.py` 的 mtime = **2026-11-18 00:59:25** ★ ⇒ ★**在 hw-lead 复跑 (00:53~00:58) 之后, 有人改了这道闸** ★ (★**不是 hw-lead 改的** ★ · ★该改动属 **ISS-303** 的活 · 同目录另见 `HANDOFF/2026-11-18_mech-lead_ISS303_N6合法落表跳.md` 与 `logs/iss303/`★) ★
★**日志**: ★`logs/iss302/gates_rerun_0103_concurrent.log` ★

| 闸 | ★00:5x 复跑 (本单那份)★ | ★01:01 再读 (并发后)★ | 说明 |
|---|---|---|---|
| `MECH/check_onepass_struct_crosscheck.py` | ★**rc=1** (N6 3 条) ★ | ★**rc=0** (『N1~N6 全过』) ★ | ★**ISS-303 已把「合法落表跳」的口径做进闸里** ⇒ ★**分家分对了** ★ |
| `MECH/check_onepass_mech_release.py` | ★**rc=1** (绿 5 / 红 1) ★ | ★**rc=0** (『6 道闸: 绿 6 / 红 0』) ★ | ★同上, 汇总里那道红已绿★ |
| `HW/check_workpack_state_values.py` | ★**rc=1** (V4 4 条) ★ | ★**rc=1** (仍红) ★ | ★**ISS-304 还没做** ⇒ ★**板那一趟仍不许开工** ★ |
| `state/gate_check.py` | ★**rc=1** (Q1 18/18 · Q7 8/9) ★ | ★**rc=1** (Q1 18/18 · Q7 8/9, 红 = 钉板闸⑥) ★ | ★**读数未变** ★ |

★**★这条并发复读的价值 (★给 main 的判据依据★)★**: ★**B3-③ 的分家是对的** —— ★**ISS-303 那边一动手, N6 当场转绿 (01:01) ⇒ 证明那 3 条确实不是本单该修的**; ★**ISS-304 那边未动 ⇒ 作业包现状值闸仍红 ⇒ 『板那一趟不许开工』的结论仍成立** ★

---

## B5 板零变化自证

★**双证 = md5 + mtime (★两者都要没变, 缺一个都不算自证★)★**

| 文件 | ★md5 (现值)★ | ★mtime (现值)★ | 判定 |
|---|---|---|---|
| ★`HW/PCB/demo_mainboard.kicad_pcb` ★ | ★`611b869e13518c3c023fb178f91a0075` ★ | ★`2026-11-06 07:07:17.362193413 +0800` ★ | ★**逐字节未变 (自 11-06 07:07 起未动) ⇒ 零写板** ★ |
| ★`HW/PCB/demo_mainboard.kicad_pro` ★ | ★`3e504d2be83152e337949723e909be1b` ★ | ★`2026-11-04 23:47:30.279742515 +0800` ★ | ★**逐字节未变 ⇒ 零写板** ★ |

★**原件核对**: ★**落表前 md5 = 落表后 md5 = 现值** ★ (台账 §16.2 与 §19.3 两处登记值与盘面现值三者一致, 见 B2-③) ★

★**★为什么这一单可以零写板 (依据, 不靠嘴说)★**:
- ★`C_SYS` / `SYS_CHG` 落的是 **CHG_BOARD (镜框充电板)** ★
- ★**CHG_BOARD 根本没有 PCB 文件** ★ ⇒ 装不装都在同一次布局里落 ⇒ ★**不构成「板改第二次」** ★
- ★主板 `demo_mainboard.kicad_pcb` 本单**一行都没碰** ★

### ★B5-② 三件落表产物的 md5 (★变了是【本单该有的】, 说清楚★)★

| 文件 | md5 | 变化 | 为什么该变 |
|---|---|---|---|
| `HW/netlist_v1.csv` | `6aee500e60ba0732f83a9cf557ba90ab` | ★**变** ★ (前 `37f62ac3…`) ★ | ★本单就是改它 (L498/L499/L500 dnp + note) ⇒ **该变** ★ |
| `HW/netlist_v1_pins.csv` | `9174309df1ec9411ac8e8d9e80ee386a` | ★**变** ★ (前 `a4270120…`) ★ | ★脚表随网表重生成 ⇒ **该变** ★ |
| `HW/BOM_v1.csv` | `5b9993992405904a60ac96a020b375d8` | ★**变** ★ (前 `5d02bece…`) ★ | ★本单加 L48 一行 (C_SYS 必装 20 µF) ⇒ **该变** ★ |

★**★本轮 (cont1) 自己一个字节都没再动这三件** ★: ★**本轮只写了 3 件 paperwork (交卷单 / 分片 / 日志) ⇒ 产物 md5 与 mtime 相对 00:21:08 那一趟完全一致 (mtime 仍 00:21:08)★** ★

---

## B6 分片 + 边界自证

### ★B6-① 分片 (★走 `python3 state/frag_write.py --agent hw-lead` 原子写, 没碰别人的分片★)★

| 项 | 值 |
|---|---|
| ★**分片文件** ★ | ★`state/fragments/hw.yaml` (★只有这一份★ · `mech.yaml` / `sw.yaml` / `pm.yaml` 一个字节没碰★) ★ |
| ★**写法** ★ | ★`python3 state/frag_write.py --agent hw-lead --add-claim ... --add-answer ... --add-artifact ... --status ...` ★ (★**原子写 tmp + os.replace**, 不是 `open(p,"w")`★) ★ |
| ★**校验** ★ | ★**`grep -c iss302 state/fragments/hw.yaml` = 12** ★ (★目标 ≥ 5 ✔★) |
| ★**写了什么 (6 处)** ★ | ★① claim (落表本体) ② claim (零写板自证) ③ answer (给 main: 两道闸变红分别归谁) ④ answer (01:01 并发复读: 分家分对了) ⑤ artifact (交卷单) ⑥ status (phase=delivered · progress_pct=100 · health=绿)★ |

★**★分片 5 条内容摘要 (★详情见 `state/fragments/hw.yaml`★)★**:

| # | 类型 | key | 内容要点 |
|---|---|---|---|
| ① | ★claim★ | `iss302_csys_landing` | ★`C_SYS` / `SYS_CHG` DNP→必装 + note 追加式订正 (老字留痕) + BOM L48 加 1 颗 20 µF 6.3V X7R 必装 · 依据 = TI bq25896 SLUSC76C §7 逐字『Connect a 20uF closely to the SYS pin.』[官网] · 落表真源 = `state/p10_rows.json` · 落表脚本 = `state/_apply_iss302_csys_landing.py` · 台账 §19 + ISS302_ROWS L1451~L1455★ |
| ② | ★claim★ | `iss302_zero_board_change` | ★零写板双证: 板 md5 `611b869e13518c3c023fb178f91a0075` + mtime 2026-11-06 07:07:17.362193413 未变 · .kicad_pro md5 `3e504d2be83152e337949723e909be1b` + mtime 2026-11-04 23:47:30.279742515 未变 · 本轮 cont1 三件产物 md5/mtime 也一字未再动 (仍 00:21:08) · CHG_BOARD 无 PCB 文件 ⇒ 不构成板改第二次★ |
| ③ | ★answer★ | `iss302_red_gates_ownership` | ★`HW/check_workpack_state_values.py` V4 4 条 (W10_MD5_NETLIST / W10B_MD5_PINS / W10C_MD5_BOM / C07_B26_MD5_LEDGER) ⇒ **归 ISS-304**; `MECH/check_onepass_struct_crosscheck.py` N6 3 条 (网表/脚表/BOM md5) ⇒ **归 ISS-303**; `HW/check_pin_function_labels.py` 15 条 = 既有缺陷基线 ISS-239 ⇒ 不许重锚★ |
| ④ | ★artifact★ | `HANDOFF/2026-11-18_hw-lead_ISS302_CSYS落表.md` | ★交卷单 · B1~B6 + §⑦ 七块填实 (★占位符扫描命中数 = 0 ★ · 原样命令与输出落 `logs/iss302/placeholders_check.log`★) · 零写板零外发不自签 issue_log★ |
| ⑤ | ★status★ | — | ★phase=delivered · progress_pct=100 · health=绿 · summary 写明『ISS-302 落表链闭环: 落表主体 00:21 已完成, cont1 收尾 paperwork 三件齐 (交卷单填实 / 分片 5 处 / 闸复跑 21 道 + 收尾 3 道原样 rc 落盘) · 零写板零落表零外发 · 红闸 4 道已分家 ISS-303/ISS-304』★ |

### ★B6-② 边界逐条自证 (★违反就是不合格★)★

| # | 边界 | ★本单实况★ | 自证方式 |
|---|---|---|---|
| 1 | ★**零写板** ★ | ★**✔ 板 + .kicad_pro 的 md5 与 mtime 双双未变** ★ | B5 两行 md5 + mtime |
| 2 | ★**零落表** (网表/脚表/BOM/台账/`state/p10_rows.json` 一个字节不许再动) ★ | ★**✔ 本轮未改这 5 件任何一件** (mtime 仍 00:21:08 / 00:22:44 / 00:21:04) ★ | `stat` mtime + md5 与台账登记三者一致 |
| 3 | ★**不许动别人的闸** ★ | ★**✔ `HW/check_pin_function_labels.py` / `HW/check_workpack_state_values.py` / `MECH/*` / `HW/check_netlist_selfconsistency.py` 一个字节没改** ★ | 本轮写盘清单只有 3 件 paperwork + `logs/iss302/` |
| 4 | ★**不许放宽判据 / 不许改基线常量** ★ | ★**✔ 没改任何基线常量, 没改任何判据阈值** (红闸一律如实记录) ★ | B4-② 现场原样输出 |
| 5 | ★**零外发** ★ | ★**✔ 没发任何邮件 / 询价 / 问询 / 采购** ★ | 本轮只有本机 exec + 一次 TI 官网只读抓取 (查资料, 不是外发) |
| 6 | ★**不替老板拍板** ★ | ★**✔ 封装 / OPN 仍留『待定』, 没有替老板定料号或定选型档位** ★ | B1-② 第 10 条 + BOM L48 `待定` |
| 7 | ★**不自签 `state/issue_log.yaml`** ★ | ★**✔ 一个字节没改** (签字是 main 的活) ★ | 本轮写盘清单 |
| 8 | ★**只写自己那一份分片** ★ | ★**✔ 只写 `state/fragments/hw.yaml`** ★ | B6-① + `mech.yaml`/`sw.yaml`/`pm.yaml` 未改 |
| 9 | ★**不许把整份大文件读进来** (只 grep 要改的那几行) ★ | ★**✔ 只 grep 了网表 L495~L502 / BOM L44~L52 / 台账 L1425~L1470 / issue_log ISS-302 段** ★ | 命令记录 |
| 10 | ★**实物 [实测] = 0 条** ★ | ★**✔ 本机无板、无量具、无实物 ⇒ 全文零条冒充实测** ★ | B1 / B2 / B5 全部标 [官网] / [推算] / [0数据] |
| 11 | ★**不许替 main 签 issue_log / 不许把 issue 判为 verified** ★ | ★**✔ ISS-302 的 status 仍由 main 处置** ★ | 本轮未写 issue_log |

---

## §⑦ 本单让哪些闸变红 / 哪些被前移 / 哪些纹丝不动

### ★§⑦-1 变红 (★**全部由本单【合法落表】造成**, 已分家另开单跟★)★

| 闸 | rc | ★变红原因 (★本单合法落表造成的副作用★)★ | ★已归谁跟★ |
|---|---|---|---|
| ★`HW/check_workpack_state_values.py` ★ | ★**1** ★ | ★V4 实跑探针: 作业包 / 清单页里的**现值** (网表/脚表/BOM/台账 md5) 没跟上盘面新值 ⇒ **4 条** (`W10_MD5_NETLIST` / `W10B_MD5_PINS` / `W10C_MD5_BOM` / `C07_B26_MD5_LEDGER`) ★ | ★**ISS-304** ★ |
| ★`MECH/check_onepass_struct_crosscheck.py` ★ | ★**1** ★ | ★N6 受保护 5 件 md5 里的**纸面 3 件** (网表/脚表/BOM) 与硬基线不等 ⇒ ★**这台闸只认硬基线, 不认【合法落表跳】**★ ⇒ 3 条 ★ | ★**ISS-303** ★ (★**01:01 并发复读已转绿 rc=0 ⇒ 分家分对了, 见 B4-④★**) ★ |
| ★`MECH/check_onepass_mech_release.py` ★ | ★**1** ★ | ★汇总 6 道闸 = **绿 5 / 红 1** ⇒ ★红的那一道**就是上面那道** struct_crosscheck ⇒ **不是 MECH 自己的新问题** ★ | ★**ISS-303** ★ (★**01:01 并发复读已转绿 rc=0★**) ★ |
| ★`state/gate_check.py` ★ | ★**1** ★ | ★Q1 18/18 ✔ · ★**Q7 钉板 md5 闸链 = 8/9 绿** ⇒ ★红的是「**钉板闸⑥ 作业包现状值闸**」= 上面那道 workpack_state_values ⇒ ★**板那一趟不许开工** ★ | ★**ISS-304** ★ |

★**★关键纪律声明 (★本单做得对的地方★)★**: ★这 4 道红闸, 本单**没有**靠"改判据"或"改基线常量"去消红 ⇒ ★**一个字都没改别人的闸** ⇒ ★**本单只如实记录「本单合法落表 ⇒ 这几道闸转红, 已另开 ISS-303 / ISS-304 跟」★** ★

### ★§⑦-2 被前移 (★本单不推进的活被挡住的★)★

| 活 | 被谁挡 | 结论 |
|---|---|---|
| ★**「板只改一次」那一趟 (钉板)** ★ | ★`state/gate_check.py` Q7 钉板 md5 闸链 8/9 (红 = 钉板闸⑥ 作业包现状值闸) ★ | ★**板那一趟不许开工** ⇒ 必须先由 ISS-304 把作业包现值跟上盘面 ★ |
| ★**MECH 侧结构交叉核对 (N6) 转绿** ★ | ★`MECH/check_onepass_struct_crosscheck.py` N6 3 条 ★ | ★须由 ISS-303 处理 (★这台闸只认硬基线, 不认合法落表跳 ⇒ 归 MECH/PM 定口径, 不归 hw-lead★) ⇒ ★**01:01 已由 ISS-303 那边的并发改动转绿 (rc=0), 见 B4-④** ★ |
| ★**脚表功能串号 15 条缺陷** ★ | ★`HW/check_pin_function_labels.py` 15 条 (既有基线 ISS-239) ★ | ★**不是本单造成的**, 下一批落表里修; ★**本单不许重锚**★ ★ |

### ★§⑦-3 纹丝不动 (★21 道里 rc 全 0 的 17 道 + 1 道基线不变的红闸★)★

★**rc = 0 (17 道)**: `HW/check_pin_function_labels.py --selftest` (0) · `HW/check_step1_parts_spec.py` (0 · 8/8) · `HW/check_onepass_preflight_coverage.py` (0) · `HW/check_g1a7_selection_landed.py` (0) · `HW/check_onepass_commit_order.py` (0) · `HW/check_fsin_rootcause.py` (0) · `HW/check_netlist_selfconsistency.py` (0) · `HW/check_land_row_anchors.py` (0) ★**⇒ 落表台账锚点链没被打断, 这是本单落表链正确性的独立旁证**★ · `SW/tools/check_demo_panel_spec.py` (0) · `SW/tools/timing_check.py` (0) · `SW/tools/check_onepass_sw_sync.py` (0) · `MECH/check_mech_verdict_freshness.py` (0) · `MECH/check_onepass_mech_sync.py` (0) · `MECH/check_demo_struct_truth.py` (0) · `MECH/check_board_frame_coords.py` (0) · `MECH/board_port_opening_s6_check.py` (0) · `state/issue_check.py` (0)

★**rc = 1 但读数与落表前完全一致 (既有基线, 不是本单造成)★**: `HW/check_pin_function_labels.py` ⇒ ★15 条缺陷 (ISS-239 既有基线) + 『5 个基线全部一致 + 3 个基线在落表台账里可查 ✔』★ ⇒ ★**本单落表没打断它**★

★**rc = 1 且是另一批的活 (本单既没造成也不归本单修)★**: `HW/check_netlist_selfconsistency.py --expect-resolved` ⇒ ★R3 / R4 / R9 未落表 ⇒ 闸自己写明『等它们随「整链重出 第 1 步」落表后本口径才转绿』★

### ★§⑦-4 本单交付清单 (★3 件 paperwork, 各能独立验收★)★

| # | 交付物 | 验收判据 | ★本轮实况★ |
|---|---|---|---|
| ① | ★**交卷单** `HANDOFF/2026-11-18_hw-lead_ISS302_CSYS落表.md` ★ | ★**占位符扫描命中数 = 0** (★两类占位符: 转圈箭头符 / 「待」紧接「填」的两字词 ★原样命令与输出落 `logs/iss302/placeholders_check.log`★) | ★**0** ✔ |
| ② | ★**分片** `state/fragments/hw.yaml` ★ | ★**`grep -c iss302` ≥ 5** ★ | ★**12** ✔ |
| ③ | ★**闸复跑日志** ★ | ★**`logs/iss302/gates_rerun.log` + `logs/iss302/final_gates.log` 存在且含原样 rc** ★ | ★**已落盘** ✔ |

---

## 交卷前必跑 (★rc 原样★)

★**日志**: ★**`logs/iss302/final_verify.log`** ★ (★= 同内容副本 `logs/iss302/placeholders_check.log`★ · ★runner `logs/iss302/run_verify.sh`★) ★
★**跑完时刻**: 2026-11-18 01:03~01:04 (本机 `date` 实读) ★

```text
### [1] python3 state/merge.py
rc=0

### [2] python3 state/gate_check.py   (★Q1 必须 18/18; ★Q7 现在 8/9 ⇒ 原样贴, 不许掩饰★)
【Q1 交付齐备率】 18/18 个必填验收块齐全
【Q7 钉板 md5 闸链】 8/9 道绿 (★9 道全部 fail-closed 挂在门禁链里★)
   ✅ 钉板闸① FSIN 根因闸: rc=0
   ✅ 钉板闸② G1a-7 选型落表闸: rc=0
   ✅ 钉板闸③ 改板提交顺序闸: rc=0
   ✅ 钉板闸④ 作业包覆盖度闸: rc=0
   ✅ 钉板闸⑤ 脚表功能标签闸: rc=0
   ❌ 钉板闸⑥ 作业包现状值闸: rc=1
   ✅ 钉板闸⑦ 板框坐标闸: rc=0
   ✅ 钉板闸⑧ 结构真值闸: rc=0
   ✅ 钉板闸⑨ SW 侧合法改板通道闸: rc=0
   ★⇒ 板 md5 / 落表链 / 结构真值 出现漂移 ⇒ 板那一趟不许开工
rc=1

### [3] python3 state/issue_check.py
rc=0

### [4] 交卷单占位符扫描 (★两类占位符: 转圈箭头符 / 「待」紧接「填」的两字词★) ⇒ 必须 0
0
rc=1

### [5] 分片命中数 (★必须 >= 5★)
12
rc=0

### [6] 板 + .kicad_pro 零写板双证 (md5 + mtime)
611b869e13518c3c023fb178f91a0075  HW/PCB/demo_mainboard.kicad_pcb
3e504d2be83152e337949723e909be1b  HW/PCB/demo_mainboard.kicad_pro
rc=0
HW/PCB/demo_mainboard.kicad_pcb  mtime=2026-11-06 07:07:17.362193413 +0800
HW/PCB/demo_mainboard.kicad_pro  mtime=2026-11-04 23:47:30.279742515 +0800
rc=0

### [7] 三件落表产物 (★本单 cont1 一个字节没再动★)
6aee500e60ba0732f83a9cf557ba90ab  HW/netlist_v1.csv
9174309df1ec9411ac8e8d9e80ee386a  HW/netlist_v1_pins.csv
5b9993992405904a60ac96a020b375d8  HW/BOM_v1.csv
rc=0
HW/netlist_v1.csv  mtime=2026-11-18 00:21:08.701116490 +0800
HW/netlist_v1_pins.csv  mtime=2026-11-18 00:21:08.806117786 +0800
HW/BOM_v1.csv  mtime=2026-11-18 00:21:08.953119601 +0800
rc=0
```

★**读数解释 (★防误读★)★**:
- ★**[2] `state/gate_check.py` rc=1** ⇒ ★Q1 18/18 ✔ · Q7 8/9 (★红 = 钉板闸⑥ 作业包现状值闸 = ISS-304★) ⇒ ★**不是本单的红, 原样贴, 没掩饰** ★
- ★**[4] rc=1 是 grep 的「无匹配」返回码** ⇒ ★**命中数 = 0 = 通过** (★有命中时 grep 才返回 0 并打印命中数★) ⇒ ★**本单交卷单 0 个占位符** ★
- ★**[6] 板与 .kicad_pro 的 md5 与 mtime 双双与 11-06 / 11-04 基线一致** ⇒ ★**零写板** ★
- ★**[7] 三件产物的 mtime 仍 00:21:08** ⇒ ★**本轮 cont1 一个字节没再动** ★

---

## ★给 main 的 2 条 answer (★分片里也写了同一份★)★

| # | 问题 | 答 |
|---|---|---|
| ① | ★**`HW/check_workpack_state_values.py` 红的那几条归谁? ★** | ★**归 ISS-304** (★本单实跑 = **4 条**: `W10_MD5_NETLIST` / `W10B_MD5_PINS` / `W10C_MD5_BOM` / `C07_B26_MD5_LEDGER` · ★main 00:5x 读数写 3 条, 以实跑 4 条为准★) ⇒ 需把**作业包 + 清单页**里的现值 (网表/脚表/BOM/台账 md5) 跟上盘面新值 ★**hw-lead 不去改这两个文档的现值** (★那不是本单的活★)★ |
| ② | ★**`MECH/check_onepass_struct_crosscheck.py` N6 红的那几条归谁? ★** | ★**归 ISS-303** (★3 条 = 网表 / 脚表 / BOM 的 md5 与硬基线不等 ★板与 .kicad_pro 两条是 `==` 没变 ⇒ **零写板成立**★) ⇒ ★**这台闸只认硬基线, 不认【合法落表跳】** ⇒ 要 MECH/PM 定"合法落表跳"的口径 (★不是让 hw-lead 把基线常量改回旧值★)★ |

★**★第三条 hw-lead 自提 (★任务书没点名, 我自己发现★)★**: ★`HW/check_netlist_selfconsistency.py --expect-resolved` 也在红 (4 条 R3/R4/R9 未落表) ⇒ ★**这是「整链重出 第 1 步」那一批的活, 建议 main 在 ISS-304 里一并点名, 别让它以后被当成新问题重复提★** ★
