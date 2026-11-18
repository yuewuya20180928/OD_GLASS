# 2026-11-12 mech-lead · ISS-200 · J_CHG 接口契约收敛到网表真源

> **交卷人**: 结构总工 (mech-lead, 带散热) 🔩 · **日期**: 2026-11-12 01:5x
> **触发**: 项目总工派活 (队列自动推进 · 闭环 ISS-200)
> **本单性质**: 把**结构侧**的 J_CHG pin map 旧口径收敛到**网表真源** ⇒ **结构侧的接口契约不许和网表对着干**
> **边界**: ★**只写 3 个文件**: `state/fragments/mech.yaml` (★**只动 `interface_claims.j_chg_pin_map` 这一条** + 新增 2 artifact + 3 need★) · `MECH/USB_HINGE_STRUCTURE.md` (★**只动 §5.2 的 `J_CHG` 块**★) · `MECH/_frag_update_iss200.py` (新建) + 本交接单
> ★**没碰**: `HW/` 任何文件 (★**那是 ISS-199 的地界**★) · `state/p10_rows.json` · `state/issue_log.yaml` · `state/gen_*.py` · `PROJECT_TRACKER.md` §0 · 别人的分片 · ★**MECH 侧其它任何结构几何数字** (pitch / 座体尺寸 / 板宽 / 铰链尺寸 一律不动)
> ★**没联系任何供应商/原厂** (外发一律经项目总工)

---

## 1. 结论摘要

1. ★**改完了 —— 结构侧不再有第二口径** —— `state/fragments/mech.yaml` 的 `interface_claims.j_chg_pin_map` 与 `MECH/USB_HINGE_STRUCTURE.md` §5.2 的 `J_CHG` 块**已全部改到网表逐脚口径**, `TS_RTN` 这个网在结构侧只剩**历史沿革说明**里的提及, **当前口径断言里一个都没有**。

2. ★**我自己复算过, 没有照抄题单** —— [实测] 从 `HW/netlist_v1.csv` 逐行扫 `J_CHG pinN` 节点反查 net 名, 复算结果与题单给的真源**逐脚一致**:

   | pin | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
   |---|---|---|---|---|---|---|---|---|---|---|
   | net (复算) | BAT_CHG | BAT_CHG | GND | GND | CHG_STAT | PWR_GOOD | **NC** | **TS_BAT** | **HINGE_RSV** | **HINGE_RSV** |
   | 复算依据 (网表行号) | 15/16/76/497 | 16/17 | 22 | 22/23 | 189/482 | 61/192/481 | **433** | 42/478 | **20** | **21** |

   ⇒ 与 `HW/CHARGE_BOARD_SPEC.md` §5.2 (ISS-136 已定版) **逐脚一致** ⇒ **真源 = 网表, 文档是它的镜像**。

3. ★**逐处 "改前 → 改后"**:

   | # | 位置 | 改前 | 改后 |
   |---|---|---|---|
   | ① | `state/fragments/mech.yaml` `interface_claims.j_chg_pin_map` **value** | `1x10p:1/2=BAT_CHG,3/4=GND,5=CHG_STAT,6=PWR_GOOD,7=VBUS_DET,8=TS,9=RSV,10=TS_RTN` | `1x10p:1/2=BAT_CHG,3/4=GND,5=CHG_STAT,6=PWR_GOOD,7=NC,8=TS_BAT,9/10=HINGE_RSV` |
   | ② | 同条 **note** | `…; pin10 = TS 专用回流 (偏差 0.44-0.99°C → <0.01°C)` | ★**该断言删掉** (TS_RTN 网在网表里 0 次出现 ⇒ 现行 map 里没有跨铰链 TS 专用回流 ⇒ 那条偏差数字是按已不存在的通路算的); 换成逐脚现行说明 (pin7=NC 的来由 / pin8=TS_BAT / pin9-10=HINGE_RSV); **TS_RTN 只以【历史沿革 (旧口径已作废)】** 形式保留** |
   | ③ | 同条 **ref** | `HW/netlist_v1.csv` | `HW/netlist_v1.csv + HW/CHARGE_BOARD_SPEC.md#5.2` |
   | ④ | `MECH/USB_HINGE_STRUCTURE.md` §5.2 标题行 | `#### J_CHG (1×6 1.27 mm 排线座, …)` | `#### J_CHG (1×10p @0.5 mm 排线座, …) —— ★**旧 "1×6 1.27 mm" 口径已作废 (ISS-085 已改 1×10p@0.5mm)**★` (★**老字符串原样留在作废声明里, 没静默删数字★) |
   | ⑤ | §5.2 第 1 条 (pin 排布与 pitch) | `网表 pin1=SYS / 2=VBUS_DET / 3=BAT_DET / 4=CHG_STAT / 5=PWR_GOOD / 6=GND … 但 1.27 mm pitch 不适合做跨铰链供电` | 现行 10p 逐脚 map + `0.5 mm pitch 用于跨铰链供电` (引 §5.3 C-1: 铰链 R=3.0 mm ⇒ 1.27 mm FFC 弯折半径达不到寿命要求) |
   | ⑥ | §5.2 第 2 条 (键位/防呆) | `反插 (180° 翻转) 时 pin1(SYS) ↔ pin6(GND) 直接短接 → 充电板 MOS 直通烧毁` | ★**该论证作废** (现行 map 无 SYS 脚); 180° 翻转 = pin i ↔ pin 11-i ⇒ **BAT_CHG(pin1/pin2) ↔ HINGE_RSV(pin10/pin9) = 落在预留脚 ⇒ 充电电流断路, 不与 GND 直短**; 现存风险 = **GND(pin3) ↔ TS_BAT(pin8) 短** + **CHG_STAT(pin5) ↔ PWR_GOOD(pin6) 短** ⇒ **机械防呆仍必需, 理由换了** |
   | ⑦ | §5.2 第 3 条 (载流) | `RAIL_SYS 标称最大 0.55 A … 建议 SYS 占 2 脚` | ★**跨铰链载流不是 SYS** (网表 J_CHG 无 SYS 脚 ⇒ SYS 不跨铰链); 跨铰链的是 **BAT_CHG 1.0-1.5 A 走 pin1/pin2 双 pin 并联**, 390Ω 档 ICHG 0.82 A ⇒ **单 pin 0.411 A ≤ 0.5 A 触点额定 (余量 1.22×)**; ★**"要占 2 脚" 的结论仍成立, 对象从 SYS 换成 BAT_CHG** |
   | ⑧ | §5.2 第 4 条 (电池路径) | `⚠️ J_CHG 没有电池脚` | ✅ **有电池脚** —— pin1/pin2 = `BAT_CHG` ⇒ 1.0-1.5 A 充电电流**有跨铰链通路** (BAT_CHG → BQ2970 → 电芯) |
   | ⑨ | §5.2 第 5 条 (检测线) | `VBUS_DET / BAT_DET 是 1M+1M 分压 (源阻抗 500 kΩ) 跨铰链 → 必须被 GND 夹持 … 与 USB 差分对 ≥3 mm 间距` | ★跨铰链高阻检测线**只剩 TS_BAT (pin8)** (源阻抗 3-4 kΩ); ★**`VBUS_DET` 2026-11-04 起改主板本地分压** (`R_VBUS_DET_D1`/`_D2` → `J_SOM_P1` pin100 ⇒ 不跨铰链, 对应 **pin7 = NC**); ★`BAT_DET` 电池在镜脚本地检测, 不跨铰链 ⇒ **老口径 500 kΩ 夹持/≥3 mm 约束失去适用对象**; ★**`VBUS_DET` 这个网本身没删** (网表里仍有 9 处, 仍是主板本地检测网) |

4. ★**写法纪律守住了** —— `state/frag_write.py --add-claim` 是【追加】不是【改写】, 用它会把 `j_chg_pin_map` 变成两条 ⇒ ★**我没用它**, 照 `MECH/_frag_update_iss092.py` 的范式新建 `MECH/_frag_update_iss200.py`: `from frag_write import update_fragment` → 在 `interface_claims` 里**按 key 定位后替换那一条** (脚本内置断言: 命中数必须恰好 1, 否则 SystemExit) → 原子写回 (tmp + fsync + os.replace) ⇒ ★**`j_chg_pin_map` 交卷后仍然只有 1 条** (★**没出现 key 重复**★)。

5. ★**5 处越界残留我只报、没改** (详见 §5) —— 结构侧 4 处 (同文件 §5.1 表 / §5.3 C-4 / §5.3 C-1 尾巴 / F-5·F-6) + HW 侧 4 处, 全部登记成 needs 给项目总工 ⇒ **一条都没顺手改**。

---

## 2. 验收标准自评 (逐条 通过/不通过/未验)

| # | 验收项 | 自评 | 依据 |
|---|---|---|---|
| 1 | `interface_claims.j_chg_pin_map` 的 **value / note / ref 三件都改** | ✅ **通过** | value → `…7=NC,8=TS_BAT,9/10=HINGE_RSV`; note 里 "pin10 = TS 专用回流 (偏差 0.44-0.99°C → <0.01°C)" **已删** (只在【历史沿革 (旧口径已作废)】里留一句说明为什么作废); ref → `HW/netlist_v1.csv + HW/CHARGE_BOARD_SPEC.md#5.2` |
| 2 | ★**`j_chg_pin_map` 交卷后仍然只有 1 条** (不许 key 重复) | ✅ **通过** | `grep -c "^- key: j_chg_pin_map" state/fragments/mech.yaml` ⇒ **1**; 脚本内置断言 (命中数 ≠ 1 直接 SystemExit, 不写盘) |
| 3 | ★**必须用 `state/frag_write.py` 的原子写, 禁 `open(p,"w")`** | ✅ **通过** | `MECH/_frag_update_iss200.py` 只 `from frag_write import update_fragment` ⇒ 写盘走 `frag_write.atomic_write_yaml` (tmp + fsync + os.replace); ★**脚本里没有一处 `open(..., "w")`** |
| 4 | ★**不许用 `--add-claim` (追加语义)** | ✅ **通过** | 脚本用的是 `update_fragment()` + **按 key 定位替换**; ★**没跑过 `--add-claim`** |
| 5 | §5.2 `J_CHG` 块的 pin map 行改成现行 10p 逐脚口径 | ✅ **通过** | §5.2 第 1 条 + 标题行 + 块首说明段, 三处一致 |
| 6 | ★**凡结论是从老 6 脚 map 推出来的 ⇒ 一律改成现行口径或明确标作废, 不许一半新一半旧** | ✅ **通过** | 5 条结论 (pitch / 防呆 / 载流 / 电池脚 / 检测线) **全部重推**, 每条都点明"老口径哪一句作废"; 标题行带 ★**旧 "1×6 1.27 mm" 口径已作废**★ 标记 |
| 7 | ★**不许改任何结构几何数字** (pitch / 座体尺寸 / 板宽 / 铰链尺寸 一律不动) | ✅ **通过** | §5.2 块内**没有删改任何既有几何数字**; 老字符串 "1×6 1.27 mm" **原样保留在作废声明里**; 新写的数字 (0.5 mm pitch / R=3.0 mm / 0.411 A / 0.5 A / 3-4 kΩ) 全部是**引用既有文档的既有结论** (C-1 / `HW/J_CHG_SELECTION.md` §0-2 §3.2 / `HW/CHARGE_BOARD_SPEC.md` §5.2), **不是新定的几何值**; §5.1 表 / §5.3 / 其余章节 **一字未动** |
| 8 | ★**别把 `VBUS_DET` 这个网整个删掉** | ✅ **通过** | §5.2 第 5 条 + claim note 都明写 "**过期的是『VBUS_DET 跨铰链走 J_CHG pin7/pin8』这句话, 不是 VBUS_DET 这个网** —— 该网在网表里仍有 9 处, 仍是主板本地检测网" |
| 9 | ★**结构侧别的文档残留旧 pin map ⇒ 只报, 不许顺手改** | ✅ **通过** | 检出 8 处残留 (MECH 4 + HW 4), **一条没改**, 全部写进 §5 并登记成 3 条 needs 给项目总工 |
| 10 | ★**不许碰 HW/ 与 `state/p10_rows.json` 与 `state/issue_log.yaml` 与别人的分片** | ✅ **通过** | `md5sum` 三件一字未变 (§6); 只写过 `state/fragments/mech.yaml` (mech-lead 自己的分片) + `MECH/USB_HINGE_STRUCTURE.md` §5.2 + 新建 `MECH/_frag_update_iss200.py` + 本交接单 |
| 11 | `python3 state/merge.py` rc=0 且 **冲突 0** | ✅ **通过** | 见 §6 (`冲突 0`, rc=0) |
| 12 | `python3 state/gate_check.py` rc=0 且 **【Q1】18/18** | ✅ **通过** | 见 §6 (`【Q1 交付齐备率】 18/18`, rc=0) |
| 13 | ★**`grep -n "TS_RTN"` 只许剩历史沿革说明, 不许有当前口径断言** | ✅ **通过** | 见 §6 —— `state/fragments/mech.yaml` 命中 1 行, 该行是【历史沿革 (旧口径已作废, 勿再当活口径用)】里的说明; `MECH/USB_HINGE_STRUCTURE.md` 命中 0 行 |
| 14 | ★**issue 状态不许我改** (改 issue 状态是 main 的活) | ✅ **通过** | `state/issue_log.yaml` **未写入**; ISS-200 的状态留给项目总工 |
| 15 | ★**不联系供应商/原厂** | ✅ **通过** | 全程零外发; 引用 `HW/J_CHG_SELECTION.md` 里的 Hirose / Amphenol 信息**全是项目内已有文档**, 没询价、没联系 |
| 16 | ★**BQ25896 在 TS 短接时的具体保护动作** | ❌ **未验 (0 数据)** | 我只从结构侧推出 "TS 检测通路被旁路" 这个**结构后果**; 芯片侧判过冷/过热的具体动作**需查 TI datasheet** ⇒ 文档里标 [0数据], **不编** |

---

## 3. 证据分级

| 标记 | 含义 | 本页用法 |
|---|---|---|
| **[实测]** | 从项目内真源**跑出来/扫出来**的真值 | ★**网表逐脚 net 名复算** (`HW/netlist_v1.csv` 逐行扫 `J_CHG pinN` 反查 net) · ★**`TS_RTN` 命中数 0** · ★**`VBUS_DET` 命中 9 行** · ★**网表行号定位** (pin7=NC 在第 433 行 等) · ★**`j_chg_pin_map` 条数 = 1** · ★**三个 md5 一字未变** · ★**merge rc=0 冲突 0** · ★**gate Q1 18/18** |
| **[官方]** | 项目内已锁死的口径 / 厂商规格书原文 | `HW/CHARGE_BOARD_SPEC.md` §5.2 (ISS-136 定版) · `HW/J_CHG_SELECTION.md` §0-5 / §2.1「机械防呆」行 / §5 J-1 (FH12 只有 polarizing mark indicator) · `HW/J_CHG_SELECTION.md` §0-2 / §3.2 (0.5A 触点额定 / 70% 降额条款 / 0.411A / 余量 1.22×) · BQ25896 TS 源阻抗 3-4 kΩ (datasheet 口径) · ISS-085 (J_CHG 改 1×10p@0.5mm) |
| **[推算]** | 由前两者推导 (推导过程写在文档里) | ★**反插逐脚对映 (pin i ↔ pin 11-i) 推出的新防呆理由** (BAT_CHG 落在预留脚 ⇒ 断路不短接 / GND↔TS_BAT 短 / CHG_STAT↔PWR_GOOD 短) · ★**"SYS 不跨铰链 ⇒ 载流对象换成 BAT_CHG"** · ★**"老 500 kΩ 夹持/≥3 mm 约束失去适用对象"** |
| **[0数据]** | 拿不到 | ★**BQ25896 在 TS 被短接/旁路时的具体保护动作** (需 TI datasheet) · ★**实物反插试验** (0 台样机) · ★**本单无任何物理实测** |

### 3.1 ★**"过期的是哪一句" 的边界 (最容易被误伤的一条)**

★**`VBUS_DET` 这个网没有作废, 只是不再跨铰链** —— [实测] 网表里 `VBUS_DET` 命中 **9 行**, 其中真正的 `VBUS_DET` 网是**主板本地**分压链 (`R_VBUS_DET_D1` → `R_VBUS_DET_D2` → GND → `J_SOM_P1` pin100), **不接 J_CHG**; ★**过期的是"VBUS_DET 跨铰链走 J_CHG pin7/pin8"这句话** ⇒ 对应的 J_CHG **pin7 = NC** (网表第 433 行, DNP)。

---

## 4. 接口取值声明 (interface_claims)

★**本单只动了 1 条 claim**, 值取自网表真源:

| key | 值 (改后) | 出处 |
|---|---|---|
| `j_chg_pin_map` | `1x10p:1/2=BAT_CHG,3/4=GND,5=CHG_STAT,6=PWR_GOOD,7=NC,8=TS_BAT,9/10=HINGE_RSV` | ★[实测] `HW/netlist_v1.csv` 逐脚复算 + `HW/CHARGE_BOARD_SPEC.md` §5.2 (ISS-136 定版) |

★**同域另一条 claim `mech_j_chg_pins` 我没动** (本单地界只许动 `j_chg_pin_map` 一条) —— ★**但它的 note 里 "pin10=TS 专用回流" 现在是错的** ⇒ 已登记 need 给项目总工 (§5.3) ⇒ ★**合并器检不出这种同域不一致 (只有跨域同 key 才判冲突), 只能人工收口**。

---

## 5. 未决项与卡点 (需要谁回答什么)

★**本单没有需要 main 拍板的"要不要做"—— 活已经干完了。** 下面 5 条全是**只报不改的越界残留**, 我按纪律**一条都没动**, 需要项目总工裁决"要不要授权下一轮一并订正 / 转给谁":

| # | 位置 | 残留内容 | 为什么我没改 | 登记在 |
|---|---|---|---|---|
| 1 | ★**MECH** `MECH/USB_HINGE_STRUCTURE.md` §5.1 表 (J_CHG 行) | 仍写 `6 (1×6 @1.27)` / 触点区宽 `6.35 mm` / 座体宽 `8.35 mm` = 老 6 脚口径 | ★**本单只许动 §5.2 的 `J_CHG` 块** ⇒ §5.1 表不在地界内 | need `iss200_mech_doc_residual_old_pinmap` |
| 2 | ★**MECH** 同文件 §5.3 C-4 | 仍写 `J_CHG → 8p @0.5` (现行是 1×10p@0.5mm) | 同上 (§5.3 不在地界内) | 同上 |
| 3 | ★**MECH** 同文件 §5.3 C-1 尾巴 + F-5 / F-6 | 仍写 "SYS 单触点载流下降 → 2 脚并联" / "反插 = SYS 短接 GND = 充电板 MOS 直通" | 同上; ★**F-6 的论证按现行 10p map 复算不成立** (已在 §5.2 第 2 条写清新结论) | 同上 |
| 4 | ★**HW** `HW/netlist_v1.csv` 第 38 行 / 第 412 行 **note 列** | 仍留 V1.5 期旧文字 "pin7=VBUS_DET / pin8=TS / pin9-10=预留" / "SYS 经 J_CHG 回主 PCB"; ★**但同表逐脚 net 行是对的** | ★**HW/ 是 ISS-199 的地界, 我不许代改** ⇒ 只报 | need `iss200_hw_residual_old_pinmap` |
| 5 | ★**HW** `HW/POWER_SHUTDOWN_V3.md` 第 129 行 / `HW/J_CHG_SELECTION.md` §0-5·C-8 | "TS 专用回流 (J_CHG pin10 … TS_RTN)" / "反插 = BAT_CHG 短接 GND" | 同上 | 同上 |
| 6 | ★**MECH** `state/fragments/mech.yaml` 同域 claim `mech_j_chg_pins` 的 note | 仍断言 "pin8=TS, pin9=RSV, **pin10=TS 专用回流**" ⇒ 与改后的 `j_chg_pin_map` 自相矛盾 | ★**本单只许动 `j_chg_pin_map` 这一条** ⇒ 只报 | need `iss200_mech_frag_mech_j_chg_pins_note` |

★**另**: `HW/CHARGE_BOARD_SPEC.md` §5.1 表 + §7 的 P10 镜像块仍是旧口径 —— ★**ISS-136 已登记 needs_from 转项目总工, 我不重复登记**。

★**诚实边界**: 实物 [实测] **0 条** (0 台样机 / 0 次反插试验 / 0 个温度实测) ⇒ ★**本单全部结论 = 设计态网表复算 + 文档对拍**, 没有任何物理验证。

---

## 6. 自证复现命令 (逐条, 原样贴)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses

python3 state/merge.py          # rc 必须 0, 冲突必须 0
python3 state/gate_check.py     # rc=0, 【Q1】必须 18/18
grep -n "TS_RTN" MECH/USB_HINGE_STRUCTURE.md state/fragments/mech.yaml
md5sum HW/netlist_v1.csv HW/PCB/demo_mainboard.kicad_pcb state/p10_rows.json
```

★**期望**: 网表 `c78f991283cc82d56c8e3dd31657c785` · 板 `611b869e13518c3c023fb178f91a0075` · `state/p10_rows.json` `c2dc73fe1e9fbd8edec68828dec81c36` ⇒ ★**三者必须一字未变**。

★**自查 (key 不重复)**:
```bash
grep -c "^- key: j_chg_pin_map" state/fragments/mech.yaml   # 必须 = 1
```

★**逐脚复算 (本单依据)**:
```bash
python3 - <<'EOF'
import csv, re, collections
rows=list(csv.DictReader(open('HW/netlist_v1.csv',encoding='utf-8')))
hits=collections.defaultdict(set)
for r in rows:
    for node in (r.get('node1',''), r.get('node2','')):
        for m in re.finditer(r'J_CHG pin(\d+)', node):
            hits[int(m.group(1))].add(r.get('net'))
for p in range(1,11): print(f"pin{p:<2} -> {sorted(hits.get(p,[]))}")
EOF
```

★**分片写法纪律自查**:
```bash
grep -n 'open(' MECH/_frag_update_iss200.py        # 不得出现 open(...,"w")
grep -n 'add-claim' MECH/_frag_update_iss200.py    # 不得出现 (追加语义)
```

---

## 7. 一句话给项目总工

★**结构侧 J_CHG 接口契约已收敛到网表真源, 改完了** —— `interface_claims.j_chg_pin_map` (value/note/ref 三件) 与 `MECH/USB_HINGE_STRUCTURE.md` §5.2 `J_CHG` 块 (5 条结论全部按现行 10p map 重推) 都已改到 `pin1/2=BAT_CHG · pin3/4=GND · pin5=CHG_STAT · pin6=PWR_GOOD · pin7=NC · pin8=TS_BAT · pin9/10=HINGE_RSV`; ★**顺手纠正了 3 条由老 6 脚 map 推出来的结论** (电池脚 / 反插后果 / 跨铰链载流对象) ⇒ ★**要你裁的只有一件事: §5 里 6 条越界残留要不要授权下一轮一并订正** (结构侧 4 处 + HW 侧 4 处 + 同域另一条 claim 的 note)。
