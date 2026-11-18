# [hw-lead→PM] ISS-199 · HW 侧 J_CHG pin map 第二口径全部收敛到网表真源 (4 处)

> 日期: 2026-11-15 21:2x · 承接: ISS-199 (owner main → hw-lead)
> ★**本单把 ISS-136 遗留的 4 处"第二口径"收干净, 让 `J_CHG` 这个接口只剩一套 pin map。**

---

## B1 结论摘要

**结论: 4 处全部订正完毕, 门禁全绿, 真源三件套一字未变。**

★**先说一条方法论**: 题单把真源直接给了 (pin1/2=BAT_CHG … pin9/10=HINGE_RSV), 但我**没有照抄** ——
自己把 `HW/netlist_v1.csv` 全表扫了一遍 (`node1` + `node2` 两列都扫, 不漏), 逐脚统计 distinct net, 得出的结论与题单一致。
**"题单对了"这件事本身不是证据, "我复算了一遍"才是。**

### ① 逐脚复算 (我自己的口径, [实测] `HW/netlist_v1.csv`)

| pin | 网表实际 net | dnp | 网表行号 |
|---|---|---|---|
| 1 / 2 | `BAT_CHG` | 必装 | P1 15/16 · P10 497 · P9 416 |
| 3 / 4 | `GND` | 必装 | P1 22/23 |
| 5 | `CHG_STAT` | 必装 | P2 189 · P10 482 |
| 6 | `PWR_GOOD` | 必装 | P2 192 · P10 481 · P1 61 |
| **7** | **`NC`** | **DNP** | **P9 433** (note: 2026-11-04 起 VBUS_DET 改主板本地分压 ⇒ 预留不接) |
| **8** | **`TS_BAT`** | 必装 | P1 42 · P10 478 |
| **9 / 10** | **`HINGE_RSV`** | **DNP** | P1 20/21 ([INVENTORY] 占位) |

★**三个交叉验证** (不是单点实测):
- `state/p10_rows.json` (P10 页真上游, md5 `c2dc73fe…`) 独立给出同口径: `TS_BAT→J_CHG pin8` · `PWR_GOOD→pin6` · `CHG_STAT→pin5` · I2C 不跨铰链 ⇒ `pin9/10` 留空不接 ⇒ **与网表逐脚一致**;
- `HW/check_bq25896_pinout.py` 检查项 ⑦ (ISS-136 已改成"**实读**规格 §5.2 表逐脚对拍网表") ⇒ 本单改动前后恒为 PASS;
- `HW/netlist_v1_pins.csv` (生成物) 逐脚: pin7=NC · pin8=TS_BAT ⇒ 同口径。

### ② 逐处 "改前 → 改后" (4 处)

**【第 1 处】`HW/CHARGE_BOARD_SPEC.md` §5.1 过铰链线表 (第 399/402/403/406/407 行) + 其后第 400 行那条订正注记**

| 行 | 改前 | 改后 | 错在哪一脚 |
|---|---|---|---|
| 399 (行 3 VBUS_DET) | `中点 → J_CHG pin8` · 方向 `镜框 → 镜脚` · 镜脚侧 `SoC ADC` | 方向 `主板本地 (不跨铰链)` · 充电板侧 `R_VBUS_DET_D1/D2` + `C_DET_VBUS_D` 中点 `VBUS_DET_D` · 镜脚侧 `J_SOM_P1 pin100` · 并写明 `J_CHG pin7=NC` / `pin8=TS_BAT` | ★**pin8 错** (pin8 现归 `TS_BAT`); 且 `VBUS_DET` 2026-11-04 起已**不跨铰链** (网表 P1 434-439 全在 MAIN_PCB) |
| 400 (订正注记) | "网表实际是 pin7=VBUS_DET / **pin10=TS 专用回流** …… 本表待更新" | 整条重写为 **2026-11-12 订正 (ISS-199)**: 逐脚列全现行口径 + 注明 `TS_RTN` 网在现行网表 0 处 | ★**注记本身在传播旧口径** (pin7=VBUS_DET / pin10=TS 专用回流) |
| 402 (行 4 CHG_STAT) | `U_CHG pin4 → J_CHG pin6` | `→ J_CHG pin**5**` | ★**pin6 错** |
| 403 (行 5 PWR_GOOD) | `U_CHG pin3 → J_CHG pin7` | `→ J_CHG pin**6**` | ★**pin7 错** (且 pin7 已被 pin 占用给 `NC`) |
| 406 (行 8 TS) | `U_CHG pin11 (TS) → J_CHG pin5` | `→ J_CHG pin**8**` | ★**pin5 错** (pin5 现归 `CHG_STAT`) |
| 407 (行 9 BQ25896 I2C) | `U_CHG pin5/6 → J_CHG pin9/pin10` · 方向 `镜脚 → 镜框` | 方向 `不跨铰链 (充电板本地自闭环)` · `U_CHG pin5/6 → 本地 R_PU_SCL/SDA 10k → REGN 5V` · `J_CHG pin9/10 = HINGE_RSV 预留不接` | ★**pin9/10 错** (两脚都是 `HINGE_RSV` DNP; I2C 自闭环是 PM 裁决) |

★**"取值/要求" 列的判据数值 (500 kΩ / ≥3mm / 0.75A / 400kHz / 4.7k / 10k) 一律未动**, 只改"走哪一脚 / 是否跨铰链"。

**【第 2 处】`HW/CHARGE_BOARD_SPEC.md` §7 的 P10 csv 镜像块 (J_CHG 跨铰链相关行)**

| 行 | 改前 | 改后 |
|---|---|---|
| 552 | note 内嵌旧 pin map "5=TS, 6=CHG_STAT, 7=PG, 8=VBUS_DET, 9/10=I2C 预留" | 换成网表真源口径 + 标"原注记 (…) 是旧口径" |
| 559 | `TS_BAT,R_TS1,J_CHG pin5` | `TS_BAT,R_TS1,**J_CHG pin8**` |
| 564 | `CHG_STAT,U_CHG pin4,J_CHG pin6` | `…,**J_CHG pin5**` |
| 565 | `PWR_GOOD,U_CHG pin3,J_CHG pin7` | `…,**J_CHG pin6**` |
| 566 | `I2C_CHG_SCL,U_CHG pin5,J_CHG pin9,…,DNP,[待裁决]` | `**HINGE_RSV,J_CHG pin9,J_CHG pin9,J_CHG,预留 (不装),NET,DNP,[实测]**` (逐字镜像网表 P1 第 20 行) |
| 567 | `I2C_CHG_SDA,U_CHG pin6,J_CHG pin10,…` | `**HINGE_RSV,J_CHG pin10,J_CHG pin10,J_CHG,预留 (不装),NET,DNP,[实测]**` (镜像网表 P1 第 21 行) |
| 581 | note "**跨铰链**必须被 GND 夹持" | "**主板本地**走线必须被 GND 夹持" + 注明 2026-11-04 起不跨铰链 |
| 584 | `VBUS_DET,R_VDET_TOP,**J_CHG pin8**,…,必装,[推算]` | `**NC,J_CHG pin7,NC,NC,预留 (NC),NET,DNP,[实测]**` (镜像网表 P9 第 433 行) + note 写明 pin8 现归 `TS_BAT`、`VBUS_DET` 本地分压仍在 (网未废) |

★**行数 80 不变、板别分布 65/11/4 不变** ⇒ §7.1 计数对账表与 §10 复现命令**继续成立**。
★**`board` 列一个没动** (改 board 会连带 §7.1 计数表, 那是本单地界外)。

**【第 3 处】`HW/J_CHG_SELECTION.md` 第 30 行 (C-2 行) 与第 196 行 (证据分级汇总行)**

- 30 行改前: `pin5=CHG_STAT · pin6=PWR_GOOD · **pin7=VBUS_DET** · **pin8=TS** · pin9=预留 · **pin10=TS 专用回流**` ⇒
  改后: `pin5=CHG_STAT · pin6=PWR_GOOD · **pin7=NC** · **pin8=TS_BAT** · **pin9/10=HINGE_RSV**`, 来源列改为"逐脚实读 + §5.2 定版", 并标注原行是旧口径。
- 196 行改前: `(… pin7 VBUS_DET, pin8 TS, pin9 预留, **pin10 TS_RTN**)` ⇒ 改后: `(… pin7 NC, pin8 TS_BAT, pin9/10 HINGE_RSV)`, 依据列从"网表第 35 行 + 第 21 行"改成**逐脚行号清单** (P1 15/16/20/21/22/23 · P2 189/192 · P9 433 · P10 478/481/482)。

**【第 4 处】`HW/POWER_SHUTDOWN_V3.md` 第 129 行 (V1.8 网表改动清单)**

- 改前: `| TS 专用回流 (J_CHG pin10 + R_TS_PULL/R_NTC_BAT 下端改接 TS_RTN) | 4 | P1 |` ——
  ★**它挂在"已落进 `state/gen_netlist.py`, V1.8" 的表里 = 一条当前口径断言, 而该改动 2026-11-03 已撤除**。
- 改后: 标为 `★TS 专用回流 —— 已撤除 (2026-11-03)`, 写明 `TS_RTN` 现行网表 **0 处**、pin10 现为 `HINGE_RSV`、NTC 与 30.31k 下臂回 `PGND`/`GND`、**功率回流仍走 `J_CHG` pin3/pin4 双 pin 并联 (不经 TS 细线)**。

### ③ 每处都加了订正注记

4 处全部带 `★**已按网表真源订正 (ISS-199 · 2026-11-12)**★` ⇒ 读的人不会再以为那是当前口径。

---

## B2 验收标准自评

| # | 验收标准 | 自评 | 依据 |
|---|---|---|---|
| ① | 先自己复算真源 (不照抄题单) | ✅ 通过 | 独立扫 `HW/netlist_v1.csv` 全表 (node1+node2 两列), 逐脚 distinct net; 与 `state/p10_rows.json` + `HW/netlist_v1_pins.csv` 三方互证 |
| ② | 4 处全部按网表真源订正 | ✅ 通过 | 见 B1 ② 逐处对照表 |
| ③ | §5.1 那条 2026-11-02 订正注记本身也改 | ✅ 通过 | 第 400 行整条重写 (它原本在传播 pin7=VBUS_DET / pin10=TS 专用回流) |
| ④ | 每处加"已按网表真源订正 (ISS-199)"注记 | ✅ 通过 | 4 处齐全 |
| ⑤ | 只改 pin map / 跨铰链归属, 不动判据阈值/几何数字 | ✅ 通过 | 500 kΩ / ≥3mm / 0.75A / 400kHz / 4.7k / 10k / V(T1)=73.25% / V(T5)=34.375% 全部原样 |
| ⑥ | `check_bq25896_pinout.py` rc=0 (不许变红) | ✅ 通过 | rc=0, **11/11 PASS, 0 FAIL** |
| ⑦ | `gate_check.py` rc=0 且 Q1 = 18/18 | ✅ 通过 | rc=0, Q1 18/18, 【Q6 硬件真源闸】✅ 通过 (rc=0) |
| ⑧ | `merge.py` rc=0 | ✅ 通过 | rc=0, 产出 194 / 冲突 **0** |
| ⑨ | 三个 md5 一字未变 | ✅ 通过 | 网表 `c78f9912…` · 板 `611b869e…` · `state/p10_rows.json` `c2dc73fe…` |
| ⑩ | `grep TS_RTN` 逐行可分类 (无当前口径断言) | ✅ 通过 | 见 B5 逐行分类 |
| ⑪ | 不越界 | ✅ 通过 | 改动清单见文末; §5.2 / ISS-112 对照表 / §2.2 第 144 行 / `state/p10_rows.json` / 网表 / PCB / `check_bq25896_pinout.py` / `state/gen_*.py` / `MECH/` / `PROJECT_TRACKER.md` §0 / 别人的分片 **全部一字未动** |

★**"没做"的 (不是"通过", 是"没做")**: ISS-199 的 issue 状态我没动 (`state/issue_log.yaml` 是 main 的活); 结构侧 `interface_claims` 的 4 脚旧值我没代改 (别人的分片); **HW 侧第 5 处旧口径我没动 (不在本单地界)** —— 见 B5。

---

## B3 证据分级

| 结论 | 分级 | 依据 |
|---|---|---|
| J_CHG 10 脚逐脚 net (BAT_CHG/GND/CHG_STAT/PWR_GOOD/NC/TS_BAT/HINGE_RSV) | **[实测]** | 直接解析 `HW/netlist_v1.csv` 全表, `node1`+`node2` 两列都扫, 逐脚统计 distinct net + dnp + 行号 |
| `TS_RTN` 在现行网表 0 处 | **[实测]** | `grep -c "TS_RTN" HW/netlist_v1.csv` ⇒ **0**; 字段级 `net/node1/node2/note` 合计亦为 0 |
| `VBUS_DET` 这个网**没废** (只是不跨铰链) | **[实测]** | 网表 `VBUS_DET` 字样 21 处; 其中 net 列为 `VBUS_DET` 1 行 (P1 439) + `VBUS_DET_D` 2 行 (P1 435/438) + `R_VBUS_DET_D1/D2` 2 行 (P1 434/436), **board 全是 MAIN_PCB** |
| `J_CHG pin7 = NC` 的成因 (2026-11-04 起 VBUS_DET 改本地分压) | **[实测]** | 网表 P9 第 433 行 note 原文 |
| `J_CHG pin9/10 = HINGE_RSV` 且为 DNP | **[实测]** | 网表 P1 第 20/21 行 ([INVENTORY] 占位行) |
| I2C 不跨铰链 (PM 裁决) | **[实测]** | 网表 P10 第 483/485 行 note + `state/p10_rows.json` 同源 note |
| `state/p10_rows.json` = P10 页真上游 | **[实测]** | `state/gen_netlist.py` 第 1347-1356 行 `build_p10_json()` 直接 load 它; 本单 md5 未变 |
| §7 csv 块结构未变 | **[实测]** | `awk` 复现命令: 行数 **80** / 板别 **CHG_BOARD 65 · HINGE 11 · MAIN_PCB 4** (与基线副本逐字相同) |
| `TS_RTN` 撤除后功率回流路径 | **[推算]** | 网表 pin3/4 = GND 双 pin + `R_STAR_PGND` 单点星接 ⇒ 回流不经 TS; 但"结构侧实际载流/温升"仍要结构总工核 (ISS-091 口径) |
| 结构侧 `interface_claims` 现值 | **[0数据]** | 我**没有**读 mech 分片以外的权威件, 不在本单地界, 未改 |

---

## B4 接口取值声明

- **`j_chg_pin_map` (J_CHG 跨铰链 10p pin map)** — 我方 (hw-lead) 取值 (与 ISS-136 已登记值一致, 本单**未改取值**, 只把**散在 4 处的镜像文字**收敛到它):
  `1x10p: 1/2=BAT_CHG, 3/4=GND, 5=CHG_STAT, 6=PWR_GOOD, 7=NC, 8=TS_BAT, 9/10=HINGE_RSV`
  - 依据: `HW/netlist_v1.csv` 投板真源, 逐脚实读 **[实测]**; 交叉验证 `state/p10_rows.json` + `HW/netlist_v1_pins.csv` **[实测]**
  - ★**结构侧 `interface_claims` (`mech.yaml`) 仍是 `7=VBUS_DET / 8=TS / 9=RSV / 10=TS_RTN`** ⇒ **仍不一致, 仍需结构侧同步** (ISS-136 已登记, 本单再次点名; 改别人的分片不在我地界)
- **本单未新增任何硬件接口取值** (pin map 是**订正已有取值**的镜像, 不是新提一个)。

---

## B5 未决项与卡点

### ① `grep TS_RTN` 逐行分类 (题单要求: 说不清哪行属于哪类 = 没做完)

| 文件:行 | 分类 | 说明 |
|---|---|---|
| `HW/CHARGE_BOARD_SPEC.md:144` | **历史沿革 (ISS-112 告警快照)** | ★**本单地界外, 只报不改** —— 它是 ISS-112 当年的"pin17/18 挂两个网"告警原文 |
| `HW/CHARGE_BOARD_SPEC.md:400` | **已订正注记 (本单新增)** | 明确写"`TS_RTN` 网现行网表 0 处 ⇒ 旧口径" |
| `HW/CHARGE_BOARD_SPEC.md:424` | **已定版表内的说明文字 (§5.2, ISS-136 已定版, 本单不许动)** | 内容是"2026-11-03 起跨铰链 `TS_RTN` 残留撤除" —— 是**撤除说明**, 不是当前口径断言 |
| `HW/CHARGE_BOARD_SPEC.md:426` | **已订正注记 (ISS-136)** | 同上, 讲的是"pin10 `TS_RTN`→`HINGE_RSV` 的订正动作" |
| `HW/CHARGE_BOARD_SPEC.md:441` | **历史快照 (ISS-112 三方对照表, 已加注记, 不许再动)** | 该表第 10 行是 2026-10-29 当时的"网表实际"列 |
| `HW/CHARGE_BOARD_SPEC.md:567` | **已订正注记 (本单新增, §7 行)** | 明确写"2026-11-03 撤除, 现行网表 0 处" |
| `HW/J_CHG_SELECTION.md:30` | **已订正注记 (本单改)** | 明确写"跨铰链 `TS_RTN` 这个网现行网表 0 处, 2026-11-03 撤除" |
| `HW/J_CHG_SELECTION.md:196` | **已订正注记 (本单改)** | 同上 |
| `HW/POWER_SHUTDOWN_V3.md:129` | **历史沿革 + 已订正注记 (本单改)** | 整行标为"已撤除 (2026-11-03)" + 写明 0 处 |

⇒ ★**结论: 剩余 9 处 `TS_RTN` 全部属于【历史沿革】或【已订正注记】, 【当前口径断言】0 处。**

### ② ★★**HW 侧还有第 5 处旧口径 —— 本单地界外, 报 main (重要)**

`HW/CHARGE_STATUS_READBACK.md`:
- 第 19 行: `NET_VBUS_DET → J_CHG pin7 → SoC USB_VBUS_DET ADC` (跨铰链断言, 现已不跨)
- 第 43 行: `J_CHG pin map: pin1/2=BAT_CHG, pin3/4=GND, pin5=CHG_STAT, pin6=PWR_GOOD, **pin7=VBUS_DET, pin8=TS, pin9/10=预留**` ← **完整的一套旧 pin map, 且是"当前口径"表 (不是历史快照)**

⇒ 已登记 `needs_from` key=`iss199_jchg_pinmap_residual_5th_vocab` 转 main。

### ③ 其它**报告不改**的残留 (地界外 / 生成物 / 历史件)

| 位置 | 问题 | 为什么本单不改 |
|---|---|---|
| `HW/CHARGE_BOARD_SPEC.md` **§2.2** 第 117/118/119/120 行 | PG 写 `→ J_CHG pin7` (应 pin6) · STAT 写 `→ J_CHG pin6` (应 pin5) · SCL/SDA 写 `J_CHG pin9/pin10` | §2.2 不在本单可改清单 (题单只许动 §5.1 表 + §5.1 注记 + §7 镜像块) ⇒ 报 |
| `HW/POWER_SHUTDOWN_V3.md` 第 114/116 行 | "VBUS_DET 分压在充电板 → 经 **J_CHG pin7** 跨铰链" / "TS 参考地接**专用回流 (J_CHG pin10)**" | 本单对该文件只许动第 129 行 ⇒ 报 |
| `HW/SCHEMATIC_V1.md` 第 61/62/63/64/618 行 | TS 专用回流 + 旧 pin map 摘要 (`pin7 = VBUS_DET · pin8-10 = 预留`) | ★**它是生成物** (`state/gen_schematic_pages.py` 从 `HW/netlist_v1.csv` 生成) ⇒ **手改会被下次 gen 覆盖**; 根因在生成器硬编码 (第 144 行) ⇒ 改生成器不在本单地界 ⇒ 报 main |
| `HW/CHARGE_BOARD_SPEC.md` §7 csv 第 581/582/583 行 | `R_VDET_TOP/R_VDET_BOT` 仍写"充电板侧" + board=CHG_BOARD; 现行网表是 **MAIN_PCB** 的 `R_VBUS_DET_D1/D2` | ★改 board 列会连带 §7.1 计数对账表 (= 本单地界外) ⇒ 板别口径整条报 main |
| `HW/CHARGE_BOARD_SPEC.md` §7 csv 第 568/569 行 | I2C 上拉写 DNP "不装"; 真上游 `state/p10_rows.json` 是**必装 10k 挂 `REGN` 5V** (PM 已裁决) | 是**装配取值**不是 pin map, 且本单不许改判据 ⇒ 报 |
| `HW/CHARGE_BOARD_SPEC.md` §7 csv 第 24 行 (r24) | CSV 列数 16 (note 内有裸逗号), **基线副本同样 16** ⇒ 存量缺陷 | 与本单无关, 且不是我引入 ⇒ 报 |
| `HW/SCHEMATIC_V1_2_REVIEW.md` 第 50 行 | 旧 pin map, 但该文是 **V1.2 复核快照** (带日期与 [实测] 标签) | 历史沿革类, 可留 (建议加一行"已过期"注) |

### ④ 其它未决

1. **结构侧 `interface_claims` 的 4 脚旧值** (`mech.yaml`: `7=VBUS_DET / 8=TS / 9=RSV / 10=TS_RTN`) 仍与网表不一致 ⇒ **ISS-136 已登记, 本单再点名**; 改别人的分片不在我地界。
2. **ISS-199 issue 状态未动** (改 issue 状态是 main 的活)。
3. **无阻塞项**: 4 处验收全过, 无"必须等裁决才能交付"的内容。

---

## B6 自证复现命令

```bash
cd projects/smart_glasses

# ① 硬件闸 (★必须 rc=0)
python3 HW/check_bq25896_pinout.py ; echo "rc=$?"

# ② 门禁链 (★必须 rc=0 且 Q1 18/18)
python3 state/gate_check.py 2>&1 | grep -E "Q1 |Q6" ; echo "rc=${PIPESTATUS[0]}"

# ③ 状态源 (★必须 rc=0)
python3 state/merge.py ; echo "rc=$?"

# ④ md5 对拍 (★三个必须一字未变)
md5sum HW/netlist_v1.csv HW/PCB/demo_mainboard.kicad_pcb state/p10_rows.json

# ⑤ TS_RTN 残留 (★逐行分类, 见 B5 ①)
grep -n "TS_RTN" HW/CHARGE_BOARD_SPEC.md HW/J_CHG_SELECTION.md HW/POWER_SHUTDOWN_V3.md

# ⑥ §7 csv 镜像块结构 (★行数 80 / 板别 65-11-4 不变)
awk '/^```csv/{f=1;next} /^```$/{if(f){f=0}} f' HW/CHARGE_BOARD_SPEC.md | grep -c '^P10,'
awk '/^```csv/{f=1;next} /^```$/{if(f){f=0}} f' HW/CHARGE_BOARD_SPEC.md | grep '^P10,' | awk -F, '{print $NF}' | sort | uniq -c

# ⑦ 逐脚复算 (独立于题单, 自己算真源)
python3 - <<'EOF'
import csv,re
rows=list(csv.DictReader(open('HW/netlist_v1.csv',encoding='utf-8')))
m={}
for i,r in enumerate(rows,start=2):
    for s in ('node1','node2'):
        mm=re.search(r'J_CHG\s+pin\s*(\d+)', r.get(s) or '', re.I)
        if mm: m.setdefault(int(mm.group(1)),set()).add(r['net'])
for p in sorted(m): print(f"  J_CHG pin{p:<3} -> {sorted(m[p])}")
EOF

# ⑧ TS_RTN 网在网表里 0 处 / VBUS_DET 网没废
grep -c "TS_RTN" HW/netlist_v1.csv ; grep -c "VBUS_DET" HW/netlist_v1.csv
```

★**并发说明**: 本单 `merge.py` 一次跑过 (rc=0, 冲突 0), 未遇 rc=2 并发冲突。

---

## 附: 改动清单 (可逐条对拍)

| 文件 | 改了什么 | 行数 |
|---|---|---|
| `HW/CHARGE_BOARD_SPEC.md` | **仅** §5.1 表第 399/402/403/406/407 行 + 第 400 行订正注记 (整条重写) + §7 csv 镜像块第 552/559/564/565/566/567/581/584 行 | 5 + 1 + 8 |
| `HW/J_CHG_SELECTION.md` | **仅** 第 30 行 (C-2 行) 与第 196 行 (证据分级汇总行) | 2 |
| `HW/POWER_SHUTDOWN_V3.md` | **仅** 第 129 行 | 1 |
| `HANDOFF/2026-11-15_hw-lead_ISS199_J_CHG_pinmap_第2口径收敛.md` | 本文件 | 新增 |
| `state/fragments/hw.yaml` | 经 `state/frag_write.py` 新增 1 条 `needs_from` + 1 条 `answer` (闭合 ISS-136 那条) + 2 条 `artifact` (只增不删, 未动别人 key) | — |

★**未动 (地界外)**: `HW/CHARGE_BOARD_SPEC.md` **§5.2 (第 409-426 行)** · **§5.2 下方 ISS-112 历史快照对照表 (第 430-446 行)** · **第 144 行 §2.2 的 PGND/TS_RTN 记述** · §2.2 表本体 (第 113-121 行) · §7.1 计数对账表 ·
`HW/netlist_v1.csv` · `HW/netlist_v1_pins.csv` · `HW/PCB/demo_mainboard.kicad_pcb` · `HW/PCB/demo_mainboard*.kicad_sch` · `HW/check_bq25896_pinout.py` ·
`state/p10_rows.json` · 任何 `state/gen_*.py` · `MECH/` 下任何文件 · `PROJECT_TRACKER.md` §0 · `state/issue_log.yaml` · 别人的分片。

★**外部无联系**: 本单未联系任何供应商/原厂, 未发任何邮件/询价/问询/采购 (外发一律经项目总工)。
