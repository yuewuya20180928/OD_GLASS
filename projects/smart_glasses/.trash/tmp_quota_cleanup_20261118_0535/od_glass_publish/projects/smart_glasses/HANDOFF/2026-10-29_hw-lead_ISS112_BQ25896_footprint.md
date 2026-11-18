# [hw-lead→PM] ISS-112 · BQ25896 封装落库 (WQFN RTW 24pin 4×4mm) + 充电板面积重算 (+7mm²) + 24 脚 pinout 复核

- **发起方**: hw-lead (硬件总工)
- **日期**: 2026-10-29
- **结论**: 封装已按 TI 官方定死并落进 BOM (`BQ25896RTWR` / WQFN RTW 24pin 4×4mm 16mm²), 24 脚 pinout 表本身经 datasheet 逐脚复核 **24/24 无错位**; ★但面积重算查出**充电板本来就装不下 (超 13.32mm²)**, 且同批复查查出 **4 个 U_CHG 脚在网表里同时挂在两个网上** + **`J_CHG` 铰链 pin map 三方口径不一致** —— 后两条**不在本单授权范围, 要你裁决**。
- **依据**: `HW/CHG_BOARD_AREA_RECHECK.md` · `HW/calc_chg_board_area.py` · `HW/check_bq25896_pinout.py` ·
  `HW/CHARGE_BOARD_SPEC.md` §2.1/§2.2/§5.2 · `HW/RELIABILITY_DESIGN.md` §3.0(4)/§B7 ·
  官方 ti.com/product/BQ25896 + ti.com/lit/gpn/BQ25896 + datasheet SLUSC76C §7

---

## B1 结论摘要

1. **封装已定死并落库**: BQ25896 只有 **WQFN (RTW) 24pin · 4×4mm = 16 mm² · P0.5 · h≤0.8mm** 一种封装,
   **OPN = BQ25896RTWR** (Active Production, 3000/盘, -40~85°C) `[官方]`。
   `HW/CHARGE_BOARD_SPEC.md` §2.1/§2.2/P10 行、`HW/RELIABILITY_DESIGN.md` §3.0(4)/§B7 已改;
   **`HW/BOM_v1.csv` 第 9 行 `U_CHG` 的封装列已落 OPN** (走生成器, 没手改 CSV)。

2. ★**BOM 封装列的机制已打通**: `state/gen_netlist.py` 加 **PARTS 寄存器** (位号→封装/OPN, 器件级唯一真源)
   → netlist 新增 `footprint`/`opn` 两列 → `state/gen_bom.py` 搬到 BOM。
   ⇒ **C-9 (BOM 封装全部回填) 仍 FAIL: 332 个位号里现在只有 1 个回填** (U_CHG), 但机制留给后续单逐颗填。

3. ★**充电板面积: 余量不够, 且不够是 ISS-112 之前就有的**。
   - **按 C-13 现有模型**: 111.17 → **118.17 mm²** (占"扣 Type-C 后可用 184.14mm²" 60.4% → **64.2%**) ⇒ **仍 PASS**;
   - ★**按修正模型** (逐颗给封装 + 把 **J_CHG 框侧座体 58.24mm²** 算进来 —— C-13 没算它, 但它物理上焊在充电板上):
     器件占位 **139.22 mm²** vs 可用 **125.90 mm²** ⇒ **超装 13.32 mm² (110.6%)** ⇒ **充电板现状判 FAIL**。
   - ⇒ **缺口 13.32 mm²**, 已给 **3 条腾挪方案**: **T-1 扩板 25×10→25×12** (零板费增量, 79.1%) /
     **T-2 双面贴+删DNP** (腾 12.62mm², **差 0.70mm² 仍不够**) / **T-3 纯删件** (腾 15.74mm², 98.1% ✅);
     **T-2+T-3 合并 = 90.4%** ⇒ **推荐 T-2+T-3 组合**。

4. ★★**(d) 24 脚 pinout 复核结果 = 两句话**: **表没错, 网表有错**。
   - ✅ **§2.2 的 24 脚表经 datasheet SLUSC76C §7 逐脚核对 24/24 全对, 无错位**;
   - ❌ **但网表里 4 个 U_CHG 脚同时挂在两个网上**:
     **pin17/pin18 (PGND)** ↔ `TS_RTN` · **pin22 (REGN)** ↔ `TS_BAT` · **pin4 (STAT)** ↔ `CHG_STAT_L`。
     ★**导出后 `HW/netlist_v1.net` 的 PGND 网里查无 U_CHG** ⇒ BQ25896 的功率地脚被挤到 `TS_RTN` 细线上,
     充电回流 (~0.82A) 只能经 `J_CHG pin10` (0.5mm ZIF / 0.5A 额定) 回镜脚 ⇒ **超触点额定 + 双 pin 并联回流设计被绕过 + `R_STAR_PGND` 单点星接失效**。

5. ★★**顺手查出 `J_CHG` 铰链 pin map 三方口径不一致** (规格 §5.2 提案 / 网表实际 / 结构侧 `interface_claims` 各不相同,
   **pin5-pin10 六个脚全对不上**) ⇒ **FPC 加工图与座体在锁定前不许下单**。

---

## B2 验收标准自评

| 验收标准 (ISS-112 任务书) | 自评 | 依据 |
|---|---|---|
| (a) `HW/CHARGE_BOARD_SPEC.md:486` 与 `HW/RELIABILITY_DESIGN.md:103,506` 的封装改掉 + 附 ti.com 链接 + 标 [官方] | ✅ **通过** | `CHARGE_BOARD_SPEC.md` §2.1 (含"旧写法已废"行)、§2.2 PowerPAD 备注、P10 行 (现 :524)、`RELIABILITY_DESIGN.md` §3.0(4) 标题 + §B7 证据行; 均带 ti.com/product/BQ25896 + ti.com/lit/gpn/BQ25896 链接 |
| (a′) 顺带清掉库内其它同一处错误 | ✅ **通过** | `HW/PCB_FORM_FACTOR_RECHECK.md` §5.3 面积表 ("U_CHG VQFN-16 4×4=16" → "U_CHG **WQFN-24** 4×4=16"; 面积本来就写的 16, 只是标签错); `HW/RELIABILITY_ABSMAX_DERATING_V2.md` R-F6 加"已处置"块 |
| (b) `BOM_v1.csv` 封装列落 OPN, **走生成器不手改 CSV** | ✅ **通过** | `state/gen_netlist.py` 加 `PARTS` 寄存器 + netlist 新增 `footprint`/`opn` 列; `state/gen_bom.py` 搬运 + BOM 新增 `opn` 列; 重生成后 `HW/BOM_v1.csv` 第 9 行 `U_CHG` = `WQFN-24 4x4mm P0.5 (...)` + `BQ25896RTWR`; **生成器幂等已验证** (重跑 diff 无漂移) |
| (b′) KiCad 导出别再落 `TBD:IC_PLACEHOLDER` | ✅ **通过** | `state/gen_kicad_net.py` 加 `REF_FOOTPRINT` 覆盖; `HW/netlist_v1.net` 里 `U_CHG` → `TI_RTW0024H (WQFN-24 4x4mm P0.5, TI 封装图 4224801/A)` (用 TI 自己的 land pattern 代号, **不编 KiCad 库名**) |
| (c) 重算充电板面积, 给出还剩多少余量 | ✅ **通过** | `HW/calc_chg_board_area.py` + `HW/CHG_BOARD_AREA_RECHECK.md` §3: C-13 口径 64.2% / 修正物理口径 **110.6%**, 缺口 **13.32 mm²** |
| (c′) 若不够, 给 3 条腾挪方案 | ✅ **通过** | `CHG_BOARD_AREA_RECHECK.md` §4: T-1 扩板 / T-2 双面贴+删DNP / T-3 纯删件, 每条列"动哪些件 + 省多少 mm² + 代价 + 谁拍板" |
| (d) 复核 24 脚 pinout 表与网表引用有无错位 | ✅ **通过 (复核做完, 且查出真错位)** | `HW/check_bq25896_pinout.py` 7 项检查: ①/①b/①c/②/③/④ 全 PASS (表 24/24 对); **⑤ 4 个脚 pin conflict FAIL**、**⑥ 导出后 pin17/18 不在 PGND FAIL**、**⑦ J_CHG pin map 三方分歧 FAIL** |
| 证据分级 [实测]/[官方]/[推算]/[0数据] 全标 | ✅ **通过** | 本单 B3 + `CHG_BOARD_AREA_RECHECK.md` §B3 (逐条标) |
| 交卷前跑 `merge.py` (rc=0) + `gate_check.py` (Q1 18/18) | ✅ **通过** | 见 B6 末尾贴的输出 |
| **充电板现状按修正口径是否合格** | ❌ **不通过** | 器件占位 139.22 mm² > 可用 125.90 mm² (超 13.32 mm²) ⇒ 需按 §4 处置 (T-1 或 T-2+T-3) 才算通过 |
| **网表语义 (4 个 pin conflict) 是否已修** | ❌ **不通过** | **本单不授权改网表语义** (充电 TS 环 / 充电灯链, 牵涉 ISS-091) ⇒ 已升级为待裁决项 (见 B5 E-1) |
| 只改 HW/ + 生成器 + HANDOFF, 不碰别人文件 | ✅ **通过** | 见"边界声明"; **未改 `state/fragments/` 下任何文件** (ISS-112 任务书明令), **未改 MECH/、SW/、PROJECT_TRACKER.md、DECISIONS.md、state/issue_log.yaml** |
| 未联系供应商/原厂 | ✅ **通过** | 只读了 TI **公开**产品页/订购页/datasheet (公开页面, 不构成询价); 未发任何邮件/询价单 |

---

## B3 证据分级

| 结论 | 等级 | 来源 / 算式 |
|---|---|---|
| BQ25896 只有 **WQFN (RTW) 24pin · 4×4mm · 16mm²** 一种封装 | **[官方]** | ti.com/product/BQ25896: "WQFN (RTW) / 24 / 16 mm² (4 mm × 4 mm)" |
| 封装细节: **P0.5 · h≤0.8mm · 封装图 4224801/A** | **[官方]** | ti.com/lit/gpn/BQ25896 封装附录: "WQFN - 0.8 mm max height / RTW 24 PLASTIC QUAD FLATPACK - NO LEAD / 4 x 4, 0.5 mm pitch" |
| **OPN BQ25896RTWR** Active Production / 3000 盘 / -40~85°C / marking "BQ 25896" | **[官方]** | ti.com/lit/gpn/BQ25896 订购页 (同族 RTWT / RTWR.A / RTWR.B) |
| **24 脚 pinout 与官方一致 (24/24)** | **[官方]** + [实测] | datasheet SLUSC76C §7 Pin Functions + 第 5 页 Top View 引脚图 (已 `pdftotext` 抽出逐条核对); 机械复核 `HW/check_bq25896_pinout.py` 检查项 ① PASS |
| 旧写法 "VQFN-16 3×3mm (RGT)" **该封装不存在** | **[官方]** | 同上 (TI 只有 RTW 一种封装) |
| Δ 占板面积 = **+7.00 mm²** | **[推算]** | 16 − 9 = 7 (封装尺寸差, 非估算) |
| C-13 口径面积 111.17 → 118.17 mm² (60.4% → 64.2%) | **[实测]** | `python3 HW/calc_chg_board_area.py` (逐字复刻 `MECH/cross_review_check.py` 的 `CHG_FOOTPRINT` 表) |
| 修正口径面积 **139.22 mm²** (34 个 CHG_BOARD 位号逐颗算) | **[实测]** | 同上脚本; 器件清单来源 = `HW/netlist_v1.csv` (`board==CHG_BOARD`, 投板真源) |
| **缺口 13.32 mm²** (物理口径) / 10.32 mm² (C-13 判据口径) | **[推算]** | 139.22 − 125.90 / 139.22 − 128.90 |
| J_CHG 框侧座体 **58.24 mm²** | **[推算]** | `HW/J_CHG_SELECTION.md` §3.2 (FH12-10S 座体宽≈9.1 × 进深≈6.4; **10p 具体尺寸表 [0数据]**, 由 28p 实测反推) |
| 充电板外形 25×10×0.8mm (250 mm²) | **[推算]** | MECH/MECH_BUDGET.md §1.3 M3 (⚠️ 见 B5 D-2: 部位仍写 [脚], ISS-014 已挪镜框) |
| Type-C 座体 8.9×7.4 = 65.86 mm² | **[推算]** | MECH_BUDGET §1.3 M4 |
| **pin17/18 不在导出网表的 PGND 里** | **[实测]** | `HW/netlist_v1.net` net `PGND` 节点表 = C_VBUS_IC.2 / C_PMID.2 / R_PSEL.2 / R_OTG.2 / R_CE.2 / C_BAT.2 / C_SYS.2 / R_STAR_PGND.1 —— **查无 U_CHG**; 而 net `TS_RTN` 里有 U_CHG pin17 + pin18 |
| 4 个脚同时挂两个网 (pin4 / pin17 / pin18 / pin22) | **[实测]** | `HW/check_bq25896_pinout.py` 检查项 ⑤; 原始行号: pin4 → CSV 行 483/515/516; pin17,18 → 行 22/469/471/481/491/493/497/501/502/503; pin22 → 行 40/41/43/477/485/487/489/517 |
| J_CHG 触点额定 0.5A | **[官方]** | `HW/J_CHG_SELECTION.md` §3.2 (FH12 规格书); 本项目工况 0.411A/触点 是**电池充电电流**路径, 与 J_CHG **pin10 回流**路径不是同一件事 |
| 走线/间距/平面不可用区 | **[0数据]** | 未建模 ⇒ 本文所有占位率**不含**这部分 ⇒ 真实紧张度比数字更差 |
| 充电板在镜框内的可用宽×高余量 / 单面还是双面贴 | **[0数据]** | 待结构总工 (B5 D-3 / D-7) |
| 充电板现状装不装得下 (物理口径) | **[推算]** | 139.22 mm² 器件 > 125.90 mm² 可用 ⇒ **超装 13.32 mm²** (土地面积层面, 未含走线) |

---

## B4 接口取值声明 (interface_claims)

> ★**按 ISS-112 任务书, 本单不写 `state/fragments/` 下任何文件** (明令) ⇒ 下面 9 条**没有登记进分片**。
> **B5 "待办" 里给了项目总工一条可直接执行的 `frag_write.py` 命令**, 跑一次即可全部登记 (零转写风险)。

| key | value (短规范值) | note |
|---|---|---|
| `bq25896_package` | `WQFN(RTW)24 4x4mm P0.5 16mm2` | `[官方]` ti.com/lit/gpn/BQ25896; 封装图 4224801/A; h≤0.8mm |
| `bq25896_opn` | `BQ25896RTWR` | `[官方]` 同上订购页; 询价经项目总工 |
| `bq25896_pins` | `24` | `[官方]` datasheet §7 —— 24 脚表本身正确, 错的只是封装名 |
| `bq25896_footprint_area` | `16.0mm2` | `[官方]` 4×4; 旧值 9mm2 作废 |
| `chg_board_outline` | `25x10x0.8mm` | `[推算]` MECH_BUDGET §1.3 M3; ⚠️ 待结构总工按 ISS-014 重出 (B5 D-2) |
| `chg_board_area_used` | `139.22mm2` | `[推算]` `HW/calc_chg_board_area.py` (修正口径, 34 个 CHG_BOARD 位号) |
| `chg_board_area_gap` | `13.32mm2` | `[推算]` 物理口径缺口 (扣 J_CHG 座体后可用 125.90mm2) |
| `chg_board_j_chg_seat_area` | `58.24mm2` | `[推算]` J_CHG_SELECTION §3.2; **C-13 未计入** |
| `chg_board_area_limit` | `0.70` | `[推算]` C-13 判据 (占扣-Type-C后可用面积的比例) |

---

## B5 未决项与卡点

### E. ★★必须项目总工裁决 (超出本单授权 —— 本单只做封装 + 复核)

| # | 需要谁回答什么 | 期望时限 | 走谁 | 我的假设 (若不回应) |
|---|---|---|---|---|
| **E-1** | ★★**网表里 4 个 U_CHG 脚同时挂两个网, 怎么改?** (a) `pin17/pin18` PGND ↔ `TS_RTN` —— 现状导出后 **BQ25896 的功率地脚不在 PGND 网上**, 充电回流被迫走 `TS_RTN` 细线 + `J_CHG pin10` 单触点 (0.5A 额定 vs 实际 ~0.82A); (b) `pin22` REGN ↔ `TS_BAT` —— 翻错则内部 5V LDO 短进 NTC 分压, **停充安全门限失效**; (c) `pin4` STAT ↔ `CHG_STAT_L` —— 翻错则 STAT 被拉到 5V, SW 侧"状态未知→禁 OD"会锁死显示。<br>**我的建议**: 把 `TS_RTN` 在充电板侧**并进 PGND 单一网名** (TS 专用回流的电气意图不变, 只是网表里不能再有两个网名共用一个脚), 即改 `state/p10_rows.json` 的 TS_RTN 行 + P1 的 `TS_BAT,R_TS_TOP,U_CHG pin22` 行的网名 —— **但这牵涉 ISS-091 的跨铰链压降/发热核算, 不在本单授权** | **投板前 (硬阻塞)** | 项目总工裁决 (必要时组织 mech-lead 三方) | 维持现状 (导出后 pin17/18 在 TS_RTN) ⇒ **网表不许拿去投板** |
| **E-2** | ★★**`J_CHG` 铰链 pin map 三方分歧, 以哪一方为准?** 规格 §5.2 提案 (pin5=TS / 6=STAT / 7=PG / 8=VBUS_DET / 9-10=I2C) vs 网表实际 (pin5=STAT / 6=PG / 8=TS / 9=RSV / 10=TS_RTN) vs 结构侧 `interface_claims` (pin5=STAT / 6=PG / 7=VBUS_DET / 8=TS / 9=RSV / 10=TS_RTN) —— **pin5-pin10 六个脚全对不上**。**建议以网表为准** (它是投板真源, 且结构侧已按它回执), 把规格 §5.2 的"提案"改成"已锁定"; 但 pin9/pin10 的 I2C 预留就没了 (J-3 裁决前提归零) | **投板前 (FPC 加工图不许下单)** | 项目总工裁决 | 按**网表实际**口径记账 |
| **E-3** | ★**充电板按哪条撑挪方案落地?** T-1 扩板 (25×10→25×12, 零板费增量, 79.1%) / T-2 双面贴+删DNP (腾 12.62, **差 0.70mm² 仍不够**) / T-3 纯删件 (腾 15.74, 98.1%) / **T-2+T-3 合并 (腾 25.36, 90.4%)**。**我推荐 T-2+T-3** (零板费增量、零结构改版、顺手接上结构总工的 `iss089_chg_led_board_column`) | 投板前 | 项目总工裁决 | 按 **T-2+T-3 组合**记账 |
| **E-4** | ★**充电灯链要不要留在充电板?** T-3 里"移到镜脚侧"这一条省 4.78mm², 但**SoC 死机时充电灯不亮** | 投板前 | 项目总工 (与结构总工 `iss089_chg_led_board_column` 一起) | 保留在充电板 (T-3 少省 4.78mm²) |

### D. 需结构总工回答 (经项目总工转达 —— 我不直接联系)

| # | 需要谁回答什么 | 期望时限 | 走谁 | 我的假设 |
|---|---|---|---|---|
| **D-1** | ★**`MECH/cross_review_check.py` 的 `CHG_FOOTPRINT["U_CHG"]`: `3.0*3.0` → `4.0*4.0`**, 并建议 C-13 增列"扣 J_CHG 座体"口径 (否则缺口永远看不见)。**这是结构总工的脚本, 本单未越界改** | 投板前 | 结构总工 | 按"已改成 16mm²"记账 |
| **D-2** | ★**充电板外形 25×10mm 还是最新口径?** MECH_BUDGET §1.3 M3 仍写 25×10×0.8 **且部位标 [脚]**, 而 ISS-014 已把充电板挪到**镜框** | 投板前 | 结构总工 | 按 25×10 (保守) |
| **D-3** | ★**充电板在镜框内的可用宽 × 高 × 周边让位余量** (T-1 扩板 / T-2 双面贴都要用) | 投板前 | 结构总工 | 不假设有余量 |
| **D-4** | ★**J_CHG 框侧座体焊在哪块板上?** 58.24mm² 直接决定缺口是 13.32 还是 3.08 mm² (若不在充电板上, T-3 一条就够) | 投板前 | 结构总工 | 按"焊在充电板上" (保守) |
| **D-7** | **充电板单面贴还是双面贴?** (决定利用率判据与 T-2 可行性) | 投板前 | 结构总工 | 按单面 (保守) |

### 待办: 需要项目总工做什么

1. ★**登记 9 条 interface_claims** (ISS-112 任务书禁止我碰 `state/fragments/`)。**一条命令搞定**:
   ```bash
   cd projects/smart_glasses && python3 state/frag_write.py --agent hw-lead \
     --add-claim 'key=bq25896_package value="WQFN(RTW)24 4x4mm P0.5 16mm2" note="[官方] ti.com/lit/gpn/BQ25896 封装图4224801/A h<=0.8mm"' \
     --add-claim 'key=bq25896_opn value="BQ25896RTWR" note="[官方] ti.com/lit/gpn/BQ25896 订购页; 询价经项目总工"' \
     --add-claim 'key=bq25896_pins value="24" note="[官方] datasheet SLUSC76C §7; 24脚表本身正确, 错的只是封装名"' \
     --add-claim 'key=bq25896_footprint_area value="16.0mm2" note="[官方] 4x4; 旧值 9mm2 作废 (ISS-112)"' \
     --add-claim 'key=chg_board_outline value="25x10x0.8mm" note="[推算] MECH_BUDGET M3; 待结构总工按 ISS-014 重出"' \
     --add-claim 'key=chg_board_area_used value="139.22mm2" note="[推算] HW/calc_chg_board_area.py 修正口径"' \
     --add-claim 'key=chg_board_area_gap value="13.32mm2" note="[推算] 物理口径缺口; 扣 J_CHG 座体后可用 125.90mm2"' \
     --add-claim 'key=chg_board_j_chg_seat_area value="58.24mm2" note="[推算] J_CHG_SELECTION 3.2; C-13 未计入"' \
     --add-claim 'key=chg_board_area_limit value="0.70" note="[推算] C-13 判据"'
   ```
   > ★**值含空格 ⇒ 必须用双引号包起来** (`frag_write.py` 内部走 `shlex.split`, 不加引号会被拆成多个 token 直接报错)。
   > **本命令我已用 `shlex` 离线验过解析结果, 但故意没有执行** —— ISS-112 任务书禁止本单碰 `state/fragments/`。
2. ★**裁决 E-1 / E-2 / E-3 / E-4** (E-1 是投板硬阻塞)。
3. **转达 D-1~D-4、D-7 给结构总工** (D-1 是"缺口永远看不见"的根因)。
4. **ISS-112 的 `fix_ref` 建议填**: `HW/CHG_BOARD_AREA_RECHECK.md` + `HW/calc_chg_board_area.py` + `HW/check_bq25896_pinout.py`
   (封装部分 ✅ 完成; **面积与网表语义部分因 E-1/E-3 未裁决 ⇒ 建议 ISS-112 保持 `fixing` 直到 E-1/E-3 落)**。
5. **ISS-113 是 sw-lead 的, 与本单无关**; 但注意 `_verify_20261029_batch.py` 里 ISS-112 的 `task_brief`
   与本单执行口径一致, 无需改。

### 阻塞: 缺什么信息 (需要老板/原厂回答 X)

| # | 缺什么 | 走谁 | 影响 |
|---|---|---|---|
| **X-1** | **BQ25896 单价 / 交期** (OPN 已定, 可以开始询价了) | 项目总工 (外发一律经你) | BOM 询价单; 不影响本单结论 |
| **X-2** | **BQ25896 的 TI 原厂书面答复**: ① "VSYS 脚悬空 (不接 20µF) 是否影响 BATFET 通路与充电环路" (CHARGE_BOARD_SPEC §8 待决项 2, 本单未动); ② "BQ25896RTWR 的 RTW0024H land pattern 能否拿到官方 STEP/IBIS" | 项目总工 | 不阻塞本单; 阻塞 PCB 正式落封装 |
| **X-3** | **充电板的外形与位置最终口径** (镜框? 25×10 还是别的?) | 老板/结构总工 | 直接决定 T-1 是否零代价 |

---

## B6 自证复现命令

```bash
cd projects/smart_glasses

# ── ① 充电板面积重算 (本单主脚本) ─────────────────────────────
python3 HW/calc_chg_board_area.py
#    ⇒ 期望: 新 139.22mm² / 占可用 75.6% (旧 132.22 / 71.8%) / Δ +7.00
#    ⇒ 期望: C-13 口径 111.17→118.17 (60.4%→64.2%) PASS
#    ⇒ 期望: 含 J_CHG 座体 197.46mm² = 107.2% FAIL
#    ⇒ 期望: T-1 50.00 / T-2 12.62 (❌差0.70) / T-3 15.74 (✅) / T-2+T-3 25.36 (✅90.4%)

# ── ② 24 脚 pinout 机械复核 ─────────────────────────────────
python3 HW/check_bq25896_pinout.py
#    ⇒ 期望: ①①b①c②③④ 全 PASS; ⑤ FAIL (pin4/17/18/22 双挂); ⑥ FAIL (pin17/18 不在 PGND); ⑦ FAIL (J_CHG 三方分歧)
#    ⇒ 退出码 1 (有 FAIL) —— 这是**预期的**, 报告的就是这些 FAIL

# ── ③ BOM 封装列已落 OPN ────────────────────────────────────
grep "^U_CHG," HW/BOM_v1.csv
#    ⇒ 期望第 10 列 = WQFN-24 4x4mm P0.5 (RTW 24, 16mm², h<=0.8mm, TI 封装图 4224801/A), 第 11 列 = BQ25896RTWR

# ── ④ 生成器幂等 (重跑不漂移) ───────────────────────────────
cp HW/netlist_v1.csv /tmp/n && cp HW/BOM_v1.csv /tmp/b
python3 state/gen_netlist.py >/dev/null && python3 state/gen_bom.py >/dev/null && python3 state/gen_kicad_net.py >/dev/null
diff -q /tmp/n HW/netlist_v1.csv && diff -q /tmp/b HW/BOM_v1.csv && echo "✅ 幂等"

# ── ⑤ 网表自检 + 结构侧交叉复核 ─────────────────────────────
python3 state/check_netlist.py 2>&1 | tail -3
python3 MECH/cross_review_check.py 2>&1 | grep -A2 "C-13"   # ⚠️ 现状 U_CHG 仍按 9mm² 算, 等 D-1

# ── ⑥ 门禁 (交卷前必跑) ────────────────────────────────────
python3 state/merge.py; echo "merge rc=$?"
python3 state/gate_check.py 2>&1 | grep -A1 "Q1"
```

### 本单交卷输出 (merge + gate) —— ★实跑, 原样贴

```
$ python3 state/merge.py ; echo "merge rc=$?"
✅ STATE.yaml 已刷新 (2026-10-29T09:34:37+08:00)
   产出 81 | 阻塞 33 (高危 26) | 未闭合需求 52 | 冲突 0 | 健康度 red
merge rc=0

$ python3 state/gate_check.py ; echo "gate rc=$?"
==========================================================================
项目总工质量门 · 3 个子模块总工交付看板
==========================================================================

【Q1 交付齐备率】 18/18 个必填验收块齐全
   hw-lead    6/6  缺: 无   交接单: 2026-10-29_hw-lead_ISS112_BQ25896_footprint.md
   sw-lead    6/6  缺: 无   交接单: 2026-10-29_sw-lead_RKNN转换链实测.md
   mech-lead  6/6  缺: 无   交接单: 2026-10-29_mech-lead_原型制作计划_ISS027.md

【Q2 证据分级率】 3/3 个总工的交付做了证据分级
gate rc=0
```

> ★**merge rc=0 ✅ · gate rc=0 ✅ · Q1 = 18/18 ✅** (本单交接单 B1-B6 六块齐全)。
> ★**注**: `python3 HW/check_bq25896_pinout.py` 的退出码是 **1** —— 这是**预期的**:
> 该脚本报的就是本单查出的 3 个 FAIL (⑤ pin 双挂 / ⑥ pin17-18 不在 PGND / ⑦ J_CHG 三方分歧),
> **不是脚本坏了**。

---

## 接口请求 (需要跟别的模块对齐时写这里, 不要自己联系)

### 致 结构总工 (mech-lead) —— 经项目总工转达

- **对方**: mech-lead
- **我的需求**: ① `MECH/cross_review_check.py` 的 `CHG_FOOTPRINT["U_CHG"]` 由 `3.0*3.0` 改成 `4.0*4.0` (D-1);
  ② 充电板外形 (25×10?) 与部位 (M3 还写 [脚], ISS-014 已挪镜框) 重出 (D-2);
  ③ 充电板在镜框内的可用宽×高×让位余量 (D-3); ④ J_CHG 框侧座体焊在哪块板上 (D-4);
  ⑤ 充电板单面贴还是双面贴 (D-7)。
- **我的假设 (如果对方不回应, 我会按这个做)**: 充电板按 25×10×0.8mm (镜框内) 记账; J_CHG 框侧座体按**焊在充电板上**记账 (58.24mm² 计入板面); 单面贴记账; C-13 的 `CHG_FOOTPRINT["U_CHG"]` 按**已改成 4.0×4.0** 记账。
- **配套**: 我这边出 `HW/CHG_BOARD_AREA_RECHECK.md` 的 T-1/T-2/T-3 三条撑挪方案, 需要的正是你的 ②③④⑤。

### 致 项目总工 (main)

- **对方**: main
- **我的需求**: 裁决 E-1 (网表 4 个 pin 双挂 —— 投板硬阻塞) / E-2 (`J_CHG` pin map 三方分歧) /
  E-3 (三条撑挪方案选哪条) / E-4 (充电灯链留不留充电板); 并代为登记 B4 的 9 条 interface_claims。
- **我的假设 (如果对方不回应, 我会按这个做)**: E-1 按"网表语义本单不动, `netlist_v1.net` 不许拿去投板"记账;
  E-2 按**网表实际**口径记账 (pin5=STAT / pin6=PG / pin8=TS / pin9=RSV / pin10=TS_RTN);
  E-3 按 **T-2+T-3 组合**记账; E-4 按**充电灯保留在充电板**记账。

---

## 边界声明

**本单改动的文件** (全部可 git diff 核对):

| 文件 | 改了什么 |
|---|---|
| `HW/CHARGE_BOARD_SPEC.md` | §2.1 封装行 (新写法 + "旧写法已废"行) · §2.2 PowerPAD 备注 · §2.2 后新增 **pin 双挂告警** · §5.2 后新增 **J_CHG pin map 三方分歧告警** · P10 行 (现 :524) 封装 note |
| `HW/RELIABILITY_DESIGN.md` | §3.0(4) 标题 · §B7 证据行 · §3.0(4) 后新增 "R-F6 已处置"块 |
| `HW/RELIABILITY_ABSMAX_DERATING_V2.md` | R-F6 段新增 "已处置"块 (面积重算结论 + 指向新文档) |
| `HW/PCB_FORM_FACTOR_RECHECK.md` | §5.3 面积表 `U_CHG VQFN-16 4×4=16` → `U_CHG **WQFN-24** 4×4=16` (面积本就 16, 只修标签) |
| `HW/CHG_BOARD_AREA_RECHECK.md` | ★新建 · 面积重算 + 3 条撑挪方案 |
| `HW/calc_chg_board_area.py` | ★新建 · 面积重算脚本 (可复现) |
| `HW/check_bq25896_pinout.py` | ★新建 · 24 脚 pinout + pin 双挂 + J_CHG 分歧 机械复核脚本 |
| `HW/netlist_v1.csv` / `HW/BOM_v1.csv` / `HW/netlist_v1.net` | **生成物** (由生成器重生成) |
| `state/gen_netlist.py` | 加 `PARTS` 寄存器 (位号→封装/OPN) + netlist 新增 `footprint`/`opn` 列 |
| `state/gen_bom.py` | 消费 `footprint`/`opn` → BOM 新增 `opn` 列 + 落地率统计 |
| `state/gen_kicad_net.py` | 加 `REF_FOOTPRINT` 位号级封装覆盖 (U_CHG 不再落 `TBD:IC_PLACEHOLDER`) |
| `HANDOFF/2026-10-29_hw-lead_ISS112_BQ25896_footprint.md` | ★本单 |

**本单明确没有做**:

- ❌ **没写 `state/fragments/` 下任何文件** (ISS-112 任务书明令"不许碰 state/fragments/ 下任何文件") ⇒
  **B4 的 9 条 interface_claims 未登记进分片**, 已给出项目总工一条可直接执行的 `frag_write.py` 命令 (见"待办"第 1 条)。
  ⇒ ★**这是本单唯一的"登记缺口"**, 请项目总工代跑一次命令, 否则 `bq25896_package` / `bq25896_opn`
  这类值不会进冲突检测, 别人写错封装不会被告警。
- ❌ 没改 `MECH/` 下任何文件 (含 `cross_review_check.py` 的 `CHG_FOOTPRINT` —— 见 D-1)。
- ❌ 没改 `SW/` / `PROJECT_TRACKER.md` / `DECISIONS.md` / `state/issue_log.yaml` / `state/merge.py` / `state/gate_check.py`。
- ❌ **没改网表的电气语义** (充电 TS 环 / 充电灯链 / `J_CHG` pin map) —— 见 E-1 / E-2。
- ❌ 没联系任何供应商/原厂 (只读了 TI 公开产品页/订购页/datasheet; 询价走项目总工)。
- ❌ 没直接联系其他总工 (接口请求全部写在本单, 经项目总工转达)。
