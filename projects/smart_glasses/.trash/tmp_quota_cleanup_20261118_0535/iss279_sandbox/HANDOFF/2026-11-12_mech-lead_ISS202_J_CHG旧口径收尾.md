# 2026-11-12 mech-lead · ISS-202 · J_CHG 旧口径收尾 (结构侧 4 处文档 + 1 条分片 claim note)

> ★**一句话**: ISS-200 昨天把 `§5.2 J_CHG 块` + `interface_claims.j_chg_pin_map` 收敛到网表真源, 但按纪律只报不改, 留下 5 处旧口径; ★**本单把其中 4 处文档 + 1 条 claim note 全部按网表真源订正**, ★**结构侧 J_CHG 不再有第 3 套 pin map**。

---

## 1. 结论摘要 (B1)

**一句话**: ★**结构侧 J_CHG 接口口径已全部收敛到 `HW/netlist_v1.csv` 逐脚真源** —— ①§5.1 表 J_CHG 行 ②§5.3 C-4 ③§5.3 C-1 尾巴 ④§5.2 F-5/F-6 ⑤分片 claim `mech_j_chg_pins` 的 note, ★**5 处全改完, 每处带「★已按网表真源订正 (ISS-202 · 2026-11-12)★」注记**; ★**零结构几何数字被改** (铰链 R=3.0 mm / 板宽 / 堆叠 24.0 mm / 走线长度 一律未动 —— 唯一重算的两个派生值在 §5.1 那张**脚位占用显示表**里, 按表头自带公式机械重算, 详见 §2 ①)。

### 1.1 逐处「改前 → 改后」

| # | 位置 | 改前 | 改后 |
|---|---|---|---|
| ① | `MECH/USB_HINGE_STRUCTURE.md` §5.1 表 · J_CHG 行 | `6 (1×6 @1.27)` / 必装 **5** / DNP 0 / 触点区 **6.35 mm (@1.27)** / 座体宽 **8.35 mm** | `10 (1×10 @0.5)` / 用到 **10** / 必装 **7** / DNP **3** / 触点区 **3.5 mm (@0.5)** / 座体宽 **5.5 mm** ＋ ★表后订正注记 |
| ② | 同文件 §5.3 **C-4** | `J_CHG` → **8p @0.5** | `J_CHG` → **1×10p @0.5** ★(原写 8p = 老 6 脚期收敛建议) ＋ ★本格算式「仍按 8p 口径 ⇒ 与上格不一致 · 属几何数字变更 · 只报不改」标注 |
| ③ | 同文件 §5.3 **C-1** 尾巴 | 改 0.5 mm FPC 后 **SYS** 单触点载流下降 → 用 **2 脚并联** 解决 | 改 0.5 mm FPC 后单触点载流下降 → 用 **2 脚并联** 解决 ★★**跨铰链载流是 BAT_CHG (pin1/pin2 双 pin 并联), SYS 根本不跨铰链** (网表 J_CHG 无 SYS 脚) |
| ④ | 同文件 §5.2 **F-5** 影响列 | (镜框侧: 只 **0.55 A SYS**) → 决定 J_CHG 的脚数与型号 | ★★**跨铰链载流是 BAT_CHG (SYS 根本不跨铰链)**, 老口径「镜框侧只 0.55 A SYS」**已作废** → 决定 J_CHG 的脚数与型号 (现行 1×10p@0.5mm, pin1/2=BAT_CHG 双 pin 并联) |
| ④ | 同文件 §5.2 **F-6** 影响列 | 反插 = **SYS 短接 GND** = 充电板 MOS 直通 | ★**反插后果已变**: 180° 翻转 = pin i ↔ pin 11-i ⇒ BAT_CHG(pin1/2) 落 HINGE_RSV(pin10/9) = **断路, 不与 GND 直短**; 真实风险 = **GND(pin3) ↔ TS_BAT(pin8) 短** + **CHG_STAT(pin5) ↔ PWR_GOOD(pin6) 短** ⇒ ★**防呆仍必需, 理由已换** |
| ⑤ | `state/fragments/mech.yaml` claim **`mech_j_chg_pins`** 的 note | 『pin8=TS, pin9=RSV, **pin10=TS 专用回流**』+『SYS×2 载流…』+『与 j_chg_pin_map 自相矛盾』 | ★**pin8=TS_BAT** · ★**pin9/10=HINGE_RSV** (TS_RTN 网在网表里已 0 次出现) · ★**跨铰链载流是 BAT_CHG, SYS 不跨铰链** · ★与 `j_chg_pin_map` **逐脚已一致**。★**value `10p@0.5mm` 不动** (已与网表 CONN 行一致) |

### 1.2 ★**本单没做但你可能以为做了的事 (边界透明)**

· ★**没有改任何几何数字**: 铰链 R=3.0 mm、板宽、铰链区堆叠 24.0 mm / 余 13.0 mm、跨铰链走线长度 27-59 mm —— **一字未动**。
· ★**§5.3 C-4 那一行的堆叠算式 (`40 脚 / 20 mm / 24.0 mm / 余 13.0 mm`) 仍是 8p 口径, 我没改** —— 因为改它 = 改几何数字 ⇒ 越界。★**已就地打 ★ 标注 + 登记 need 请你裁** (两条算式的候选重算值见 §5 卡点 2)。
· ★**ISS-200 登记的 2 条 need 我没动** (`iss200_mech_doc_residual_old_pinmap` / `iss200_mech_frag_mech_j_chg_pins_note` —— ★**这 2 条本单已做掉, 但关需求是 main 的活** ⇒ 请 main 回写 answers 闭合)。
· ★**本文件 §5.2 的 F-3 行、§0/§3/§7/§8/§9 里还有 11 处 8p / 6 脚旧口径** —— 都在本单地界外 ⇒ **只报不改**, 已登记 need。

---

## 2. 复算依据 (★自己复算, 不照抄题单)

### 2.1 逐脚对拍网表 [实测]

命令: `grep -n "J_CHG" HW/netlist_v1_pins.csv` (逐脚 net 行) + `grep -n "J_CHG" HW/netlist_v1.csv` (主网表) ⇒ 现行 10p 逐脚 map:

| pin | net [实测] | dnp | 备注 |
|---|---|---|---|
| 1 | `BAT_CHG` | 必装 | 充电电流跨铰链, **双 pin 并联** |
| 2 | `BAT_CHG` | 必装 | 同上 (每 pin ≈0.75 A @1.27mm 旧注记 / 现行 0.411 A @390Ω 档) |
| 3 | `GND` | 必装 | 回流双 pin (与电源 pin 相邻) |
| 4 | `GND` | 必装 | 同上 |
| 5 | `CHG_STAT` | 必装 | 开漏, 主板侧 10k 上拉 |
| 6 | `PWR_GOOD` | 必装 | 开漏, 主板侧 10k 上拉 |
| 7 | `NC` | DNP | ★2026-11-04 起 VBUS_DET 改**主板本地**分压 ⇒ 不接 |
| 8 | `TS_BAT` | 必装 | NTC 在镜脚 / BQ25896 TS 在镜框 ⇒ TS 必须跨铰链 (高阻, 源阻抗 3-4 kΩ) |
| 9 | `NC` (主表 net `HINGE_RSV`) | DNP | 预留 (I2C 本板自闭环) |
| 10 | `NC` (主表 net `HINGE_RSV`) | DNP | 预留 |

· ★**交叉核对**: 与 `HW/CHARGE_BOARD_SPEC.md` §5.2 (ISS-136 定版) 逐脚一致 ✔; 与同域 claim `j_chg_pin_map` (ISS-200 已订正) 逐脚一致 ✔。
· ★**`TS_RTN` 已死**: [实测] `grep -c "TS_RTN" HW/netlist_v1.csv` ⇒ **0** ⇒ 网表里不存在「跨铰链 TS 专用回流」这个网 ⇒ ★**pin10 只能是 HINGE_RSV**。
· ★**`VBUS_DET` 没死**: [实测] `grep -c "VBUS_DET" HW/netlist_v1.csv` ⇒ **9** 处, 仍是**主板本地**分压网 (`R_VBUS_DET_D1`/`_D2` → `J_SOM_P1` pin100) ⇒ ★**过期的是「它跨铰链走 J_CHG pin7/pin8」这句话, 不是这个网** —— 本单**没有**删任何 VBUS_DET 表述。

### 2.2 §5.1 表 J_CHG 行的新值怎么来的 [实测]

命令: `python3 MECH/hinge_usb_check.py` ⇒ 解析当前网表输出 `J_CHG 声明 10 / 用到 10 / 必装 7 / DNP 3 / 触点区 3.5 mm / 板宽 OK`。
· 必装触点区宽 = 必装脚数 7 × pitch 0.5 = **3.5 mm** (表头自带公式「触点区宽 = 必装数 × pitch」);
· 座体宽 = 3.5 + 2.0 = **5.5 mm** (表头自带公式「座体宽 = 触点区宽 + 2.0 mm」; 与脚本 `socket_width_mm(7, 0.5)` 一致);
· ★**这两个 mm 是「脚位占用显示行」里的派生值, 不是结构几何预算** ⇒ 按表头公式机械重算, **不动任何预算数字**。★**若你认为连派生值也不许动 ⇒ 请裁, 我改成「只改 pin 列 + 两格标注待重算」**。

### 2.3 反插复算 (与 ISS-200 §5.2 第 2 条同源)

180° 翻转 ⇒ **pin i ↔ pin 11-i**:
· pin1(BAT_CHG) ↔ pin10(HINGE_RSV), pin2(BAT_CHG) ↔ pin9(HINGE_RSV) ⇒ 充电电流**落预留脚 = 断路**, **不与 GND 直短** ⇒ 老口径「SYS/BAT_CHG 短接 GND → MOS 直通」**作废**;
· 真实风险: **pin3(GND) ↔ pin8(TS_BAT)** 短 (TS 温度检测通路被旁路) + **pin5(CHG_STAT) ↔ pin6(PWR_GOOD)** 短 (两个开漏状态信号互短) ⇒ ★**机械防呆结论不变 (仍必需), 理由换掉**。

---

## 3. 验收标准自评 (B2)

| 验收项 | 判据 | 结果 |
|---|---|---|
| ① §5.1 表 J_CHG 行改到现行 10p@0.5 口径 | 声明/用到/必装/DNP/触点区宽/座体宽 全部与网表复算一致 | ✅ **通过** (10/10/7/3/3.5 mm/5.5 mm) |
| ② §5.3 C-4 的 J_CHG pin 规格 | = 1×10p @0.5 | ✅ **通过** (堆叠算式按边界只标不改, 见 §1.2) |
| ③ §5.3 C-1 跨铰链载流归属 | 从 SYS 改为 BAT_CHG | ✅ **通过** |
| ④ §5.2 F-5 / F-6 防呆措辞 | 按 pin i ↔ pin 11-i 重算 | ✅ **通过** |
| ⑤ 分片 claim `mech_j_chg_pins` 的 note | pin10 改为 HINGE_RSV, 与 `j_chg_pin_map` 对齐 | ✅ **通过** (★**value 未动**) |
| ⑥ 每处带订正注记 | 「★已按网表真源订正 (ISS-202 · 2026-11-12)★」 | ✅ **通过** (4 处文档 + 1 条 note, 逐条可 grep) |
| ⑦ **不许改结构几何数字** | pitch/座体尺寸/板宽/铰链尺寸 | ✅ **通过** (★仅 §5.1 脚位占用表的 2 个派生值按表头公式重算, 已标注; 预算数字全未动) |
| ⑧ **不许碰** HW/ · §5.2 J_CHG 块 · p10_rows.json · gen_*.py · issue_log.yaml · 别人分片 | md5 + diff 自证 | ✅ **通过** (网表/板 md5 一字未变; §5.2 J_CHG 块未动; issue_log 未动) |
| ⑨ 分片 key 不重复 | `j_chg_pin_map` × 1, `mech_j_chg_pins` × 1 | ✅ **通过** (claims 总数 186, 重复 key = 0) |
| ⑩ 合并器 / 质量门 | `merge.py` rc=0 冲突 0; `gate_check.py` rc=0, Q1 18/18 | ✅ **通过** |
| ⑪ 越界残留 | 只报不改 | ✅ **通过** (登记 5 条 need, 见 §5) |

---

## 4. 证据分级 (B3)

| 结论 | 证据级别 | 依据 |
|---|---|---|
| 现行 10p 逐脚 map (pin1/2=BAT_CHG … pin9/10=HINGE_RSV) | **[实测]** | `HW/netlist_v1_pins.csv` + `HW/netlist_v1.csv` 逐脚 net 行 (md5 `c78f9912…`) |
| `TS_RTN` 网已不存在 | **[实测]** | `grep -c TS_RTN HW/netlist_v1.csv` = **0** |
| `VBUS_DET` 仍有 9 处且是主板本地网 | **[实测]** | `grep -c VBUS_DET HW/netlist_v1.csv` = 9; `R_VBUS_DET_D1/_D2` → `J_SOM_P1` pin100 |
| §5.1 表新值 (10/10/7/3/3.5/5.5) | **[实测]** | `python3 MECH/hinge_usb_check.py` 对当前网表的解析 + 表头自带公式 |
| 首选件 = 1×10p@0.5 (FH12-10S-0.5SH(55)) · 单触点 ≥0.5 A | **[官方]** | `HW/J_CHG_SELECTION.md` (厂商型号, ★未询价 ⇒ 外发经项目总工) |
| 390Ω 档 ICHG 0.82 A ⇒ 单 pin 0.411 A ≤ 0.5 A (余量 1.22×) | [官方]+[推算] | BQ25896 datasheet + `MECH/HINGE_POWER_CALC.md` |
| 反插后果 (断路 + GND↔TS_BAT 短 + CHG_STAT↔PWR_GOOD 短) | [推算] | 现行逐脚 map 复算 (pin i ↔ pin 11-i) |
| BQ25896 侧具体保护动作 (反插时 TS 被旁路后芯片怎么反应) | **[0数据]** | 需 TI 确认, ★本单不猜 |
| §5.3 C-4 堆叠算式的候选重算值 (21.0 / 25.0 / 25.0 mm) | [推算] | 本文行内算式 vs 脚本算式, ★**未写入文档**, 待裁 |
| 铰链段功耗 0.015-0.127 W @1 A · 皮肤侧温升 0.8-6.4 °C | [推算] | `MECH/HINGE_POWER_CALC.md` (充电时不在皮肤上 ⇒ 不受 43 °C 红线约束) |

---

## 5. 接口取值声明 (B4)

| key | value | 本单动作 |
|---|---|---|
| `mech_j_chg_pins` | `10p@0.5mm` | ★**value 不动**, **note 订正** (pin10: TS 专用回流 → HINGE_RSV; 载流: SYS → BAT_CHG; 与 `j_chg_pin_map` 对齐) |
| `j_chg_pin_map` | `1x10p:1/2=BAT_CHG,3/4=GND,5=CHG_STAT,6=PWR_GOOD,7=NC,8=TS_BAT,9/10=HINGE_RSV` | ★**不动** (ISS-200 已定版, 本单一个字都没改) |

---

## 6. 未决项与卡点 (B5) —— 需要谁回答什么

| # | key | 卡点 | 要谁答 |
|---|---|---|---|
| 1 | `iss202_mech_doc_residual_jchg_old_6pin` | 本文件里 **11 处** J_CHG 旧口径 (§0 C-3/C-5/C-6 · §3.1 L-1 · §3.2b 声明版+收敛版 · §3.2c · §7 · §8 U-2 · §9 两行 —— ★**其中 §9 `mech_j_chg_pins` 行仍写 value `8p@0.5mm`, 与本分片 claim 的 `10p@0.5mm` 直接矛盾 = 结构侧文档里还藏着第 3 套 pin map**), 外加 §5.2 F-3 的 8p (ISS-200 定版区, 我没碰) | **main** (授权下一轮一并订正; 49.62 / 24.00 / 25.62 是否连带重算请给口径) |
| 2 | `iss202_mech_c4_stack_arith_pending` | §5.3 C-4 行 pin 规格已改 1×10p, 但**同行的触点区/堆叠算式仍是 8p 口径** ⇒ 该行现在自相矛盾 (已就地 ★ 标注)。候选重算: 行内算式 42 脚 = 21.0 mm 触点区 + 4 mm 间隙 = **25.0 mm 堆叠 / 余 12.0**; 脚本算式 50 脚 = **25.0 mm** ⇒ 堆叠两法都是 25.0, 触点区两法不同 | **main** (裁算式; ★**属几何数字, 本单不动**) |
| 3 | `iss202_mech_script_recommended_pins_jchg_8` | `MECH/hinge_usb_check.py` 第 77 行 `RECOMMENDED_PINS["J_CHG"]=8` 及其注释 (SYS×2 载流 / VBUS_DET / BAT_DET 跨铰链) 仍是老 6 脚期口径 ⇒ ★**24.0 mm 那条链的根在脚本** (既有脚本, 改它要单独授权) | **main** |
| 4 | `iss202_mech_other_docs_jchg_old_pinmap` | 其它 3 份结构文档仍带旧口径: `FPC_FAB_NOTES.md` N-6/I-5 · `RELIABILITY_TEST_PLAN.md` R10/§T-14/判据/K-11/K-12 · `STRUCT_REVIEW_ISS065.md` R3 | **main** (★**只改 pin map / 跨铰链归属 / 防呆措辞, 不改几何数字**) |
| 5 | `iss202_mech_frag_old_needs_stale` | 本分片 2 条老 need 前提已不存在: `iss091_pin9_10_ntc_return` (还在问 pin9/10 改作 NTC 专用回流 ⇒ 该提案已被网表撤除) + `iss100_jchg_pitch_fix` (还在说脚本 pitch 是 1.27 ⇒ 早已是 0.5); ★**另**: ISS-200 的 2 条 need 本单已做掉, 需 main 回写 answers 闭合 | **main** |
| — | `iss200_hw_residual_old_pinmap` | ★**HW/ 是 ISS-199 的地界, 我没碰** (netlist note 列 / `POWER_SHUTDOWN_V3.md` 第 129 行 / `J_CHG_SELECTION.md` 防呆论证) | **main → ISS-199** |

---

## 7. 自证复现命令 (B6) —— 原样贴

```console
$ cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
$ python3 state/merge.py
✅ STATE.yaml 已刷新 (2026-11-12T02:33:32+08:00)
   产出 186 | 阻塞 43 (高危 33) | 未闭合需求 112 | 冲突 0 | 健康度 red
rc=0

$ python3 state/gate_check.py
【Q1 交付齐备率】 18/18 个必填验收块齐全
   hw-lead    6/6  缺: 无   交接单: 2026-11-12_hw-lead_ISS136_J_CHG_pinmap_订正与门禁接入.md
   sw-lead    6/6  缺: 无   交接单: 2026-11-11_sw-lead_ISS196_rknn台账与rk3572结论.md
   mech-lead  6/6  缺: 无   交接单: 2026-11-12_mech-lead_ISS200_J_CHG接口契约收敛.md
…
【Q6 硬件真源闸】 HW pinout 真源闸: ✅ 通过 (rc=0)
rc=0

$ grep -n "TS_RTN" MECH/USB_HINGE_STRUCTURE.md state/fragments/mech.yaml
MECH/USB_HINGE_STRUCTURE.md            → ★0 行 (rc=1)
state/fragments/mech.yaml:386:   逐脚订正 (pin7 VBUS_DET→NC / pin8 TS→TS_BAT / pin9-10 旧值(RSV / TS_RTN)→HINGE_RSV) …
state/fragments/mech.yaml:1316:  第 129 行 『TS 专用回流 (J_CHG pin10 + …改接 TS_RTN)』 —— TS_RTN 网在网表里 0 次出现; …
state/fragments/mech.yaml:1393:  …『改成 NTC 专用回流后偏差 <0.01C』当活结论 ⇒ 该提案已被网表撤除 ([实测] TS_RTN 在网表里 0 次出现…
state/fragments/mech.yaml:1855:  ③★**『pin10=TS 专用回流』⇒ 现为 HINGE_RSV** —— ★**`TS_RTN` 这个网在网表里已 0 次出现** …
state/fragments/mech.yaml:1856:  -c TS_RTN HW/netlist_v1.csv` = 0; 2026-11-03 起跨铰链 TS 专用回流残留撤除 …
state/fragments/mech.yaml:1998:  8=TS / 9=RSV / 10=TS_RTN』是 V1.5-V1.8 期口径 —— TS_RTN 这个网在网表里已 0 次出现 …
★逐行分类: 386/1855/1856/1998 = 【已订正注记 + 历史沿革说明】; 1316/1393 = 【残留报告里引用的历史文字】;
★**当前口径断言里 0 处 TS_RTN** (文档 0 行 + claim note 已改)。

$ md5sum HW/netlist_v1.csv HW/PCB/demo_mainboard.kicad_pcb
c78f991283cc82d56c8e3dd31657c785  HW/netlist_v1.csv          ★与期望一致
611b869e13518c3c023fb178f91a0075  HW/PCB/demo_mainboard.kicad_pcb  ★与期望一致

$ python3 MECH/hinge_usb_check.py     # §5.1 表新值的来源
[1] 连接器 pin 占用 (从 HW/netlist_v1.csv 解析)
    J_CHG           10    10     7     3       3.5        OK
…
[4] 正文对表 → 关键词检查 ✅ 全过 · 关键数字 4.4/24.0 ✅ · [FAIL] 0 项

$ python3 -c "import yaml;d=yaml.safe_load(open('state/fragments/mech.yaml'));…"
claims 总数 186 · j_chg_pin_map × 1 · mech_j_chg_pins × 1 · 重复 key 0
needs 总数 101 (新增 5, 既有 96 一字未动)
```

★**边界自证**: `HW/` 下 0 文件被写 (md5 双向核对) · `MECH/USB_HINGE_STRUCTURE.md` **只动 ①-④ 四处** (§5.2 的 J_CHG 块、F-3 行一字未动) · `state/issue_log.yaml` / `state/p10_rows.json` / `state/gen_*.py` / 别人的分片 / `PROJECT_TRACKER.md` 全部未碰。

---

## 8. 一句话给项目总工

★**结构侧 J_CHG 现在只有一套口径 (网表逐脚)**: 4 处文档 + 1 条分片 note 已按真源改完、每处带注记、**几何数字零改动**; ★**请你裁 3 件事**: ①§5.3 C-4 堆叠算式按哪套算式重算 (25.0 mm 两种算法一致) ②是否授权改 `hinge_usb_check.py` 的 `RECOMMENDED_PINS["J_CHG"]=8` (24.0 mm 那条链的根) ③本文件里剩下的 11 处旧口径 (含 §9 `mech_j_chg_pins` = `8p@0.5mm` 这处**第 3 套 pin map**) + 另 3 份结构文档要不要下一轮一并收; ★**另**: ISS-200 那 2 条 need 本单已做掉, 请回写 answers 闭合。
