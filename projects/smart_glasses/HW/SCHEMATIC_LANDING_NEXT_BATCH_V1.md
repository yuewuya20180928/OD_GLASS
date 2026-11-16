# HW/SCHEMATIC_LANDING_NEXT_BATCH_V1.md —— ISS-247 · 下一批落表清单 v1 (F1 + V-2/V-3/V-4)

> ★★★**【ISS-249 · 2026-11-16 19:4x 已更新为「F1 已落」版】** ★★★
> ★**F1 已于 ISS-249 真落表** (★台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` §17★) ⇒ ★**下一批 = V-2 + V-3 + V-4 三条** ★
> ★**本版改了什么**: ★**① §2.2 行号漂移表: 漂移对象从 F1 换成 V-2 / V-4** (★F1 已定稿, 不再漂★) ★**② §2.3 md5 撞车: 4 处 → 3 处, 「只落 F1」的 md5 已实测 = `16ac89f7…`** ★**③ §3.1 / §3.2 的两个坑已在本批 (ISS-249) 同批改完** ⇒ **下一批不用再改** ★**④ §5 `.kicad_sch` 口径升级** (★新发现: 门禁自己会重铸 UUID★) ★**⑤ §6 门禁清单更新** (★F1 门禁 11 条 / R3 门禁 12 条★) ★**⑥ §7 的「F1 落真盘」行已销账** ★

> ★**硬件总工 (hw-lead) · 2026-11-16 18:0x~18:4x · 单号 ISS-247 · verify_by = main (项目总工)** ★
> ★**配套**: `HW/SCHEMATIC_LANDING_F1_WORKPACKET_V1.md` (F1 落表作业包 v1) · `HW/check_iss247_f1_landed.py` (机器门禁) ★
> ★**本单只出清单, ★不改真源 / 不落盘 / 不替老板拍板** ★ · ★**零外发** ★ · ★**实物 [实测] = 0 条** ★

---

## ★0 一句话

★★**下一批 = 一次落 3 件 (★V-2 + V-3 + V-4★) ⇒ 因为 ★它们全都改 `state/gen_netlist.py` ⇒ 全都改网表 md5 ⇒ 分批落 = SW/MECH 白锚一次 + 门禁链当场过期★ ⇒ 必须同批一次落, 落完把新 md5 一次性广播给 SW (ISS-245) / MECH (ISS-246)** ★★
★★**★F1 已落 (ISS-249, 2026-11-16 19:2x)★ ⇒ 下一批只剩三条; ★并且 F1 落表带来的两个【陈旧锚点】(R3 的 T7/T8 + F1 门禁的 T0/T4/T5) 已在 ISS-249 同批修好 ⇒ 下一批不用再管这两个坑** ★★

---

## 1 · 四条的落表要素 (★谁改哪一行 · 前置条件★)

| 项 | ★**F1** ★ | ★**V-2** ★ | ★**V-3** ★ | ★**V-4** ★ |
|---|---|---|---|---|
| ★**一句话** ★ | ★**两颗 2 脚电容的端子标签撞车 (node2 槽借了对方的裸位号)** ★ | ★**USB ESD 方案 / 型号 (D_ESD_USB_D 从 SoM 侧挪到 Type-C 侧 + 3 脚双通道)** ★ | ★**电池分压链 R_BAT_DET_1/2 + C_DET_BAT 从 DEMO_DNP 拿出来 + 上/下臂阻值** ★ | ★**R_ILIM 输入限流档位 (390Ω 判死 → 选 680 / 470 / 390)** ★ |
| ★**真源文件** ★ | ★`state/gen_netlist.py` ★ | ★`state/gen_netlist.py` + `HW/SCHEMATIC_V1_SPEC.json` ★ | ★`state/gen_netlist.py` + `HW/SCHEMATIC_V1_SPEC.json` + `HW/check_netlist_selfconsistency.py` + `HW/NETLIST_SELF_CONSISTENCY_SPEC.md` ★ | ★`state/gen_netlist.py` + `state/p10_rows.json` + `HW/CHARGE_BOARD_SPEC.md` ★ |
| ★**改的行 (★本机 `grep -n` 现值★)** ★ | ★**L381** (FB_VBUS 后级行) + ★**L393** (C_VBUS_GND 信号端行) 的 `add()` 第 4 参数 ★ | ★**L1420~L1424** (ESD 段 5 行 → 7 行) ★ | ★**L331/L332/L333** (删 `DEMO_DNP` 三行) + P2 段上/下臂 `value` 行 ★ | ★**L537 / L547** (R_ILIM 的 `value` + `note`, 原地替换) ★ |
| ★**取值白名单** ★ | ★无 (布尔: 改 / 不改)★ | ★`V-2 ∈ {1, 2}` (★`2` = 只落网表侧 ⇒ ★**ISS-230 实测: 一条都转不绿 = 假绿, 必须打回★**)★ | ★`V-3 ∈ {E, A, D, DEG4}` ★ | ★`V-4 ∈ {680, 470, 390}` (★`390` = 已判死档, 落它 ⇒ R10 仍红★)★ |
| ★**前置条件 (★谁先拍★)** ★ | ★**无需拍板** (★F1 是【自相矛盾】不是【选型分歧】⇒ 自主落, ★但本轮 main 已定: 不落表, 出作业包等下一批★)★ | ★**老板拍 A1** (★ESD 方案 / 型号★) ★ | ★**老板拍 A2** (★分压档位 / 阻值组合★) ★ | ★**老板拍 A3** (★R_ILIM 档位★) ★ |
| ★**落表器** ★ | ★**目前不在 `state/land_v_values.py` 里** ⇒ 见 §4 的两条路 ★ | `python3 state/land_v_values.py --decision V-2=1` | `python3 state/land_v_values.py --decision V-3=E` | `python3 state/land_v_values.py --decision V-4=680` |
| ★**落表后网表 md5 变?** ★ | ★**变** (`611c3ba3…` → `16ac89f7…` 若只落 F1) ★ | ★**变** ★ | ★**变** ★ | ★**变** ★ |
| ★**落表后脚表 md5 变?** ★ | ★**不变** (★实测★) ★ | ★**变** (★行号 +1 ⇒ ANCHORS 要跟着改★) ★ | ★**变** (★DNP→必装 ⇒ 脚表 `dnp` 列变★) ★ | ★**变** (★`value` 列变★) ★ |
| ★**落表后 BOM 变?** ★ | ★**不变** (★实测★) ★ | ★**变** ★ | ★**变** (★DNP→必装★) ★ | ★**变** ★ |
| ★**落表后 `.net` 变?** ★ | ★**不变** (★实测★) ★ | ★**变** (★ESD 挪网★) ★ | ★**变** ★ | ★**变** ★ |
| ★**落表后板 / `.kicad_pro` 变?** ★ | ★**不变** ★ | ★**不变** ★ | ★**不变** ★ | ★**不变** ★ |

---

## 2 · ★**落表顺序 + 互斥 / 撞车分析 (★本机实测行号推出来的★)★**

### 2.1 ★**内容撞车: ★零★**

| 改动 | 行区间 (`state/gen_netlist.py` 现值) | 与 F1 的 L381 / L393 重叠? |
|---|---|---|
| **F1** | **L381**, **L393** | — |
| **V-3** | **L331~L333** (删 3 行) + P2 段阻值行 (L3xx 之后, 需现场 `grep`) | ★**否** ★ |
| **V-4** | **L537**, **L547** | ★**否** ★ |
| **V-2** | **L1420~L1424** | ★**否** ★ |

⇒ ★**四条改的是四个互不重叠的行块 ⇒ 内容上零撞车 ⇒ 可以同批落** ★

### 2.2 ★**行号漂移撞车: ★F1 已落 ⇒ 漂移对象换成 V-2 / V-4 (★下一批最容易被坑到的地方★★)** ★★

★★**【ISS-249 更新】F1 已于 2026-11-16 19:2x 真落表** ⇒ ★**F1 的落点 (L381 / L393) 已定稿, 不会再漂** ★
★★**⇒ 漂移现在只影响 V-2 与 V-4**: ★**V-3 落表会删掉 `state/gen_netlist.py` 的 L331/L332/L333 三行 (`DEMO_DNP` 里的 `R_BAT_DET_1` / `R_BAT_DET_2` / `C_DET_BAT`) ⇒ ★**该行之后的所有行号一律 -3** ★ ⇒ ★**V-4 与 V-2 的落点会漂** ★

| 条目 | ★**现值 (F1 已落后的盘上真值, 2026-11-16 19:4x `grep -n` 实测)** ★ | ★**V-3 落表后** ★ | 备注 |
|---|---|---|---|
| ★**F1 改法 1 (FB_VBUS 后级行)** ★ | ★**L381** ★ (★已落·已定稿★) | ★**L378** ★ (★但已经落过了, 不用再动★) | ★**已落** ★ |
| ★**F1 改法 2 (C_VBUS_GND 信号端行)** ★ | ★**L393** ★ (★已落·已定稿★) | ★**L390** ★ (★同上★) | ★**已落** ★ |
| ★**V-4 改法 1 (`R_ILIM` 的 `value`)** ★ | ★**L537** ★ | ★**L534** ★ | ★**★下一批的漂移点 1★** ★ |
| ★**V-4 改法 2 (`R_ILIM` 的 `note`)** ★ | ★**L547** ★ | ★**L544** ★ | ★**★下一批的漂移点 2★** ★ |
| ★**V-2 (ESD 段 5 行 → 7 行)** ★ | ★**L1420 ~ L1424** ★ | ★**L1417 ~ L1421** ★ | ★**★下一批的漂移点 3★** ★ |
| ★**V-3 自身 (`DEMO_DNP` 三行)** ★ | ★**L331 / L332 / L333** ★ | ★**删掉本身** ★ | ★**删行 ⇒ 后续全 -3** ★ |

⇒ ★**⇒ 落表顺序 (★F1 已落 ⇒ 方案甲/乙 合并成一条★):** ★

| 方案 | 顺序 | 优点 | 风险 |
|---|---|---|---|
| ★**甲 (★现在是唯一可行·★推荐★)** ★ | ★**V-3 先落 (删 3 行) → 再按漂移后的行号落 V-4 (L534/L544) 与 V-2 (L1417~L1421)** ★ | ★**一次落完, 只广播一次 md5** ★ | ★**裸行号定位 = 易错** ⇒ ★**必须配合下面的「唯一字符串 + assert count==1」** ★ |
| ★**乙 (★推荐·★与 ISS-243/ISS-249 的做法一致★)** ★ | ★**V-2 / V-3 / V-4 都走 `state/land_v_values.py` 的 Patch 机制 (★`old` 字符串唯一命中 + `ctx` 锚点, ★不依赖行号★)** ★ | ★**自带 dry-run / 白名单 / 老板凭据门禁 / 自动回滚 / 落表后自动跑门禁并打印新 md5** ★ | ★**要把三条都做成落表器的分支 (★见 §4 路乙★)** ★ |

★★**⇒ 硬规矩: ★**下一批落表一律不许用裸行号定位 ⇒ 一律用「唯一字符串 + 上下文锚点」定位** ★★
★★**⇒ 复现命令里必须带 `assert t.count(old) == 1` (★命中数不是 1 就停★) —— `HW/SCHEMATIC_LANDING_F1_WORKPACKET_V1.md` §5 的复现脚本已经这么写了** ★★

### 2.3 ★**md5 撞车: ★有 4 处 (⇒ 必须同批落)★**

★**F1 / V-2 / V-3 / V-4 四条全都改 `state/gen_netlist.py` ⇒ 全都触发整链重生成 ⇒ 网表 md5 全都变** ★

| 落表批次 | 网表 md5 | SW (ISS-245) / MECH (ISS-246) 的锚点 |
|---|---|---|
| ★**ISS-247 出清单时的盘上真值** ★ | `611c3ba3db3dc7de7213063375b96d01` | ★**两边当时锚的就是这个** ★ |
| ★**现在 (★ISS-249 落完 F1·★2026-11-16 19:2x 实测★)** ★ | ★**`16ac89f77c25a3f61834cc7ebcd78a7f`** ★ | ★**★两边锚的已经过期 ⇒ SW/MECH 各须重锚 1 次 (ISS-249 已登记 need)★** ★ |
| ★**F1 + V-2 + V-3 + V-4 同批** ★ | ★**落完现算** ★ | ★**两边只需再重锚 1 次** ★ |

★★**⇒ md5 撞车由 4 处降为 3 处** (★F1 那处已发生并已广播给 SW/MECH; 剩 V-2 / V-3 / V-4 三处 ⇒ ★**仍必须同批落, 否则 SW/MECH 还要锚第三次**★) ★★
★★**★F1 的 md5 变化是「纯 node2 写法」引起的 (脚表 / BOM / `.net` / 板 / `.kicad_pro` 逐字节不变) ⇒ 对下游只影响网表那一个锚点★** ★

⇒ ★**⇒ 这就是本单【只出作业包不落真盘】的硬理由: ★落 F1 会把正在跑的 ISS-245 / ISS-246 的锚点当场打穿 ⇒ 等 A1/A2/A3 拍完, 下一批一次落, 落完广播一次新 md5** ★★

### 2.4 ★**门禁撞车: ★1 处 (★T7 / T8★) ⇒ 见 §3★**

---

## 3 · ★★**★下一批必须同批做的配套改动 (★T7 / T8 那条坑 + 其余 4 项★)★★** ★★

### 3.1 ★★**★坑 1 (★已于 ISS-249 同批改完·★下一批不用再改★): `HW/check_netlist_contradiction_r3.py --selftest` 的 T7 / T8 必红** ★★

> ★★★**【ISS-249 更新 · 2026-11-16 19:3x】这个坑已经落地了, 而且比本清单原先预计的还多一条** ★★★
> ★**① 已改**: ★**T7 ⇒ 「恰 2 条 且 ids == [F2, F3]」· T8 ⇒ 「A1/A2 绿 且 A3/A4 红」· 主模式条数期望 `== 3` ⇒ `== 2 且 ids == [F2,F3]` + 文案** ★
> ★**② 已新增反向用例 T11** (★main 19:3x 口径: 反向用例不许删 + 必须新增「改回 F1 ⇒ 必须回到 3 条」★) ⇒ ★**「把 F1 改回旧值 ⇒ findings 必须回到 3 条 (F1+F2+F3)」** ⇒ ★**证明条数期望的改动没把判据调没** ★
> ★**③ rc 语义一个字没动** (`1 if findings else 0`) ⇒ ★**F2/F3 还在 ⇒ 主模式仍 rc=1 (预期)** ⇒ ★**「恰 2 条」那行结论现在是 ✅, 但 rc 仍是 1** ★
> ★**④ 另外新增一个本清单原先没算到的坑**: ★**`HW/check_iss247_f1_landed.py --selftest` 的 T0 / T4 / T5 也是「现状断言」⇒ F1 一落表这三条必红** ⇒ ★**已按 main 19:3x 口径改成「fixture 显式回退成落表前」⇒ 与活文件状态无关 ⇒ 落表前跑 / 落表后跑 = 同一套断言 (11/11)** ★
> ★**详见**: `HW/SCHEMATIC_LANDING_V1_LANDED.md` §17.4 (逐行改前改后 + 反向用例清单) ★

★★**★以下是 ISS-247 出清单时的原始处方 (★已由 ISS-249 执行, 留档★)★** ★★

★**F1 一落表 ⇒ `findings` 从 3 条变 2 条 (F1 消失, 剩 F2 + F3) ⇒ `R3-A1` / `R3-A2` 从红变绿 ⇒ T7 / T8 这两条断言【断言的是落表前现状】⇒ 必红** ★★

★**本机沙盒实跑 (`sb1` = 已按本作业包改过并重生成) ⇒ 原样输出:** ★

```
  ❌ T7 现状 (真文件) 必须恰 3 条 findings
       findings=2 ids=['F2', 'F3']
  ❌ T8 现状必须 A1/A2/A3/A4 四条规则全红
       {'R3-A1': 0, 'R3-A2': 0, 'R3-A3': 1, 'R3-A4': 43}
------------------------------------------------------------------------------
  反向用例 11 条 · 失败 2 条
  ❌ 有用例没抓到
```

★**下一批要改的 (★只改【现状断言值】, ★判据逻辑一个字不许动★):** ★

| 位置 | 改前 | 改后 |
|---|---|---|
| ★`--selftest` T7 ★ | `ok = (len(r7["findings"]) == 3)` ★ | ★`ok = (len(r7["findings"]) == 2 and [f["id"] for f in r7["findings"]] == ["F2", "F3"])` ★ |
| ★`--selftest` T8 ★ | `ok = all(not r7["rules"][r]["ok"] for r in ("R3-A1","R3-A2","R3-A3","R3-A4"))` ★ | ★`ok = (r7["rules"]["R3-A1"]["ok"] and r7["rules"]["R3-A2"]["ok"] and not r7["rules"]["R3-A3"]["ok"] and not r7["rules"]["R3-A4"]["ok"])` ★ |
| ★主模式摘要 ★ | `ok = (len(res["findings"]) == 3)` + 文案「主线要求 = 恰 3 条」 ★ | ★`ok = (len(res["findings"]) == 2)` + 文案「主线要求 = 恰 2 条 (F2 + F3)」 ★ |

★**★一条反向用例都不许删★**: ★T1 / T2 / T3 三条 (★注入错误 ⇒ 必须抓到红★) 在 `sb1` 里实测仍是 ✅ ⇒ 落表后仍必须保留 ⇒ ★**下一批只准改 T7 / T8 的【现状断言值】, 不准碰 T1~T6 / T9 / T10** ★★

★**★并且: ★`HW/check_netlist_contradiction_r3.py` 的主模式 rc 落表后仍是 1 (★因为 F2 / F3 还在★) ⇒ 这是【预期的】, 不是新红灯 ⇒ 不许为了让它变绿去动 F2 / F3** ★★

### 3.2 ★**坑 2: 新门禁 `HW/check_iss247_f1_landed.py` 的口径翻转** ★

| 命令 | 现在 (F1 未落) | 落表后 (F1 已落) | 下一批怎么办 |
|---|---|---|---|
| `python3 HW/check_iss247_f1_landed.py` (默认 = 判定) | ★**rc=1** (F1 未落) ★ | ★**rc=0** (F1 已落) ★ | ★**不用改** ★ |
| `python3 HW/check_iss247_f1_landed.py --expect-not-landed` (现状守卫) | ★**rc=0** ★ | ★**rc=1** ★ (★ISS-249 实测确认★) | ★**★已停用·★常跑命令一律用默认模式 (判定) 或 `--expect-landed`★** ★ |
| `python3 HW/check_iss247_f1_landed.py --selftest` | ★**rc=0** (11/11) ★ | ★**rc=0** (11/11)** ★ (★ISS-249 实测: fixture 改成状态无关后仍是 11/11, T0/T4/T5 从「必红」变「回退态必红」★) | ★**不用改** ★ |

### 3.3 ★**坑 3: 落表台账 §17 必须追加 (★SW 侧 R6 判据要读它★)** ★

★**`HW/SCHEMATIC_LANDING_V1_LANDED.md` §16 是「第 4 批」的段 ⇒ 下一批要开 ★**§17** ★ ⇒ ★**必须逐字含: 单号 + 文件名 + 新 md5 + 旧 md5 四项齐全且在同一行** ★ (★SW 侧 `check_demo_panel_spec.py` 的 R6 判据 ②③④⑤ 就是查这三样★) ★

★**追加内容 (★F1 那部分★):** ★

| 文件 | 旧 md5 | 新 md5 | 变了吗 |
|---|---|---|---|
| `HW/netlist_v1.csv` | `611c3ba3db3dc7de7213063375b96d01` | ★**落完现算** ★ | ★**是 (★只有表A L8 / L12 两行★)** ★ |
| `HW/netlist_v1_pins.csv` | `ef436a37412ac9b6eac3c9f41f1edca4` | ★**落完现算** ★ | ★**F1 部分不变; V-2/V-3/V-4 部分会变** ★ |
| `HW/BOM_v1.csv` | `2a7305741134788dfee9f13f34c656b4` | ★**落完现算** ★ | ★**同上** ★ |
| `HW/PCB/demo_mainboard.kicad_pcb` | `611b869e13518c3c023fb178f91a0075` | ★**同左** ★ | ★**否** ★ |
| `HW/PCB/demo_mainboard.kicad_pro` | `3e504d2be83152e337949723e909be1b` | ★**同左** ★ | ★**否** ★ |
| `state/gen_netlist.py` (★真源★) | ★**落完现算** ★ | ★**落完现算** ★ | ★**是** ★ |
| ★`HW/PCB/demo_mainboard*.kicad_sch` (11 个)★ | 各自不同 | 各自不同 | ★**是 (★生成物含随机 UUID★ ⇒ 见 §5★)** ★ |

### 3.4 ★**坑 4: SW / MECH 两侧的 H-1 重锚 (★不是本单的活★)** ★

★**落表后网表 md5 变 ⇒ ★ISS-245 (sw-lead) 与 ISS-246 (mech-lead) 锚的是【落表前】的 md5 ⇒ 必须让两边各重锚 1 次 (§1 那张表的「落表后网表 md5」那一格) ★★

### 3.5 ★**坑 5: `--expect-resolved` 的条数会随 V-3 变 (★F1 不影响★)** ★

| 口径 | 现在 | 只落 F1 | ★**F1 + V-2 + V-3 + V-4** ★ |
|---|---|---|---|
| `HW/check_netlist_selfconsistency.py` (现状守卫) | rc=0 | ★**rc=0** ★ | ★**rc=0** ★ (`land_v_values.py` 自带 ExpectPatch 处理) |
| `HW/check_netlist_selfconsistency.py --expect-resolved` | rc=1 · ★**18 条** ★ | ★**rc=1 · 仍 18 条** ★ (★本机 `sb1` 实测★) | ★**条数会减少** (★V-3 会把 R2 那批转绿★) ⇒ ★**`EXPECT` 锚点要跟着改 (落表器自带处理)★** |

---

## 4 · ★**F1 怎么进下一批: 两条路 (★推荐第 2 条★)★**

| 路 | 做法 | 优点 | 缺点 |
|---|---|---|---|
| **甲** | ★**手工改 `state/gen_netlist.py` 两行 + 手工跑整链 + 手工补台账 + 手工改 T7/T8** ★ | 不动落表器 | ★**没有 dry-run / 没有自动回滚 / 没有「不许替老板拍板」的机器化保证 / 行号易错** ★ |
| ★**乙 (★推荐★)** ★ | ★**把 F1 做成 `state/land_v_values.py` 的一个新分支 (★例: `--decision F1=land★` / `--decision F1=skip★`) ⇒ 复用它已有的: ① 默认 dry-run 零写盘 ② `old` 字符串唯一命中 + `ctx` 锚点 (⇒ 不依赖行号, ★**§2.2 的漂移坑自动消失**★) ③ `--apply` 必须带 `--boss-decision` 凭据 ④ 落表前自动打 `.bak_land_v_values_*` 回滚副本 ⑤ 落表后自动跑门禁 + 打印新 md5** ★ | ★**一次落四条, 顺序无关, 自带回滚, 自带门禁实跑, 自带 md5 广播** ★ | ★**要动一下落表器 (★新增一个分支, ★不改既有 V-2/V-3/V-4 分支的逻辑★)** ★ |

★**⇒ 给 main 的建议: ★**下一批按「路乙」走, F1 挂进 `state/land_v_values.py` ⇒ 一条命令一次落四条 (★F1 + V-2 + V-3 + V-4★) ⇒ 落完把 stdout 的新 md5 直接广播给 SW / MECH** ★★

★**若走「路甲」, 最低要求: ★**① 改法用唯一字符串 + `assert count == 1` ② 落表前先 `cp` 一份 `.bak` ③ 落表后跑 §5 的整串门禁 ④ 台账 §17 四项齐全 ⑤ T7 / T8 同步改** ★★

---

## 5 · ★**`.kicad_sch` 的 UUID 抖动 (★下一批必须提前定口径, 不然台账会脏★)★**

★**本机实测: ★`state/gen_kicad_sch.py` 每次跑都重铸随机 UUID ⇒ 11 个 `.kicad_sch` 的 md5 每次都变; `HW/PCB/STACKUP.md` / `LAYOUT_RULES.md` / `GEN_SELF_CHECK.txt` 每次都重写时间戳 ⇒ 这 4 个派生物也会跟着变** ★
★**⇒ ★**归一化 UUID + 时间戳后, `sb_base` 与 `sb1` 的 11 个 `.kicad_sch` 逐字节相同** ★ ⇒ ★**F1 对原理图图形零影响** ★

| 口径 | 做法 | 代价 |
|---|---|---|
| **甲** | ★**落表后把 11 个 `.kicad_sch` + 4 个派生物 restore 回落表前** ★ | ★**干净: 台账里只有「真变了」的件** ★ |
| **乙** | ★**接受抖动, 台账里逐条写明「生成物含随机 UUID ⇒ md5 每次都变, 不可当锚点」** ★ | 台账脏一点, 但与既有 §16 的既有口径一致 |

★**⇒ 推荐甲 (★restore★) ⇒ 但要注意: ★**`.kicad_sch` 里若含 F1 的图形变化就要留新的** —— 本次实测 **F1 对图形零影响** ⇒ ★**可以放心 restore** ★★

★★**★★【ISS-249 · 2026-11-16 19:3x 新发现 · 比上面严重得多】★★** ★
★★**`state/check_sch_pinfull.py` 与 `state/check_sch_erc.py` 内部会 `subprocess` 调 `state/gen_kicad_sch.py`** ⇒ ★**跑这两条门禁 = 重铸 11 个 `.kicad_sch` 的随机 UUID** ⇒ ★**⇒ 口径甲 (restore) 只能维持到「下一次跑这两条门禁」为止 ⇒ 任何门禁跑完, `.kicad_sch` 的 md5 都会变** ★
★★**⇒ 口径结论 (下一批照此办)**: ★**① `.kicad_sch` 的 md5 【永久不可当锚点】, SW/MECH 的重锚名单里不许出现它** ★ ★**② 台账里只写「归一化 UUID+时间戳后与落表前逐字节相同 ⇒ 图形零影响」, 不写 md5** ★ ★**③ 若坚持要台账干净 ⇒ restore 必须放在【跑完全部门禁之后】的最后一步 (★ISS-249 就是这么做的★), 但别指望它稳定** ★
★★**实测依据 (ISS-249)**: ★**11 个 `.kicad_sch` 归一化后 11/11 逐字节相同 ⇒ F1 对原理图图形零影响** ★ ★`[实测]` ★

---

## 6 · ★**下一批落表后的必跑门禁清单 (★整串, ★逐条要 rc★)★**

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses

# ── 落表链路 (★顺序硬: 脚表脚号来自 .net★)
python3 state/gen_netlist.py && python3 state/gen_kicad_net.py && \
python3 state/gen_netlist_pins.py && python3 state/gen_bom.py && \
python3 state/gen_schematic_pages.py && python3 state/gen_kicad_sch.py

# ── 必跑门禁
python3 HW/check_netlist_selfconsistency.py                    # rc=0 (现状守卫)
python3 HW/check_netlist_selfconsistency.py --selftest          # rc=0
python3 HW/check_netlist_selfconsistency.py --expect-resolved   # rc=1 (★V-3 落完后条数会变, 落表器会改 EXPECT★)
python3 HW/check_netlist_contradiction_r3.py                    # rc=1 (★恰 2 条 = F2 + F3★ ★**T7/T8 已于 ISS-249 改完★)
python3 HW/check_netlist_contradiction_r3.py --selftest         # rc=0 (★12/12 · ★含 T11「改回 F1 ⇒ 必须 3 条」★)
python3 HW/check_iss247_f1_landed.py                            # rc=0 (★F1 已落★)
python3 HW/check_iss247_f1_landed.py --selftest                 # rc=0 (★11/11 · ★T0/T4/T5 的 fixture 已改成状态无关★)
python3 state/check_netlist.py && python3 state/check_netlist_pins.py   # rc=0
python3 state/check_sch_erc.py && python3 state/check_sch_pinfull.py   # rc=0 (★ERC=0★)
python3 HW/check_part_selection_matrix.py                       # rc=0 (8/8)
python3 state/merge.py && python3 state/gate_check.py           # rc=0 (Q1 18/18)

# ── 受保护 md5 (★5 件必须逐字节不变★)
md5sum HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv \
       HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro
```

---

## 7 · ★**本单【没做】的东西 (★逐条 + 卡在谁★)★**

| 没做的事 | 为什么 | 卡在谁 |
|---|---|---|
| ★**F1 落真盘** ★ | ★★★**【ISS-249 已销账】★ F1 已于 2026-11-16 19:2x 真落表** (★真源 `state/gen_netlist.py` L381 / L393 的 node2 槽改成各自自己的网名 · 网表 md5 `611c3ba3…` → `16ac89f7…` · 门禁 `HW/check_iss247_f1_landed.py` rc=1 → rc=0 · 台账 §17★) ⇒ ★**下一批只剩 V-2 / V-3 / V-4** ★ | ★**已闭合 (ISS-249)** ★ |
| ★**V-2 / V-3 / V-4 的取值** ★ | ★**不替老板拍板** ★ | ★老板 (★A1 / A2 / A3★)★ |
| ★**F2 (J_CHG 位号消歧)** ★ | ★**本单只登记, 不做** (★要牵板那一趟★) ★ | ★板那一趟 (★老板 2026-11-11 10:07 口径排队★)★ |
| ★**F3 (板侧 DNP 标记)** ★ | ★**本单只登记, 不做** (★要改板文件★) ★ | ★板那一趟 ★ |
| ★**SW / MECH 分片与台账** ★ | ★**ISS-245 / ISS-246 的活** ★ | ★sw-lead / mech-lead ★ |
| ★**`state/issue_log.yaml` 自改** ★ | ★**verify 留给 main** ★ | ★main ★ |
| ★**`PROJECT_TRACKER.md` §0 锁死表** ★ | ★**不许碰** ★ | ★—★ |

---

## 8 · ★**【ISS-249 · 2026-11-16 19:4x】F1 已落后的交卷摘要 (★下一批照 §6 + §8 走★)★★

| 项 | 值 | 出处 |
|---|---|---|
| ★**F1 状态** ★ | ★**已落表** (★真源 L381 / L393 的 node2 改成 `VBUS_5V_F1` / `VBUS_5V_CHG`★) ★ | ★**台账 §17** ★ |
| ★**网表 md5 (现值)** ★ | ★**`16ac89f77c25a3f61834cc7ebcd78a7f`** ★ | ★**台账 §17.5** ★ |
| ★**未变四件** ★ | ★**脚表 `ef436a37…` · BOM `2a730574…` · 板 `611b869e…` · `.kicad_pro` `3e504d2b…`** ★ | ★**台账 §17.5** ★ |
| ★**已同批改完的配套** ★ | ★**R3 的 T7/T8 + 主模式条数期望 + 新增 T11 · F1 门禁的 T0/T4/T5 fixture + T6 两种起点** ★ ⇒ ★**下一批不用再改这两个门禁** ★ | ★**台账 §17.4** ★ |
| ★**下一批还剩什么** ★ | ★**V-2 (ESD 方案) + V-3 (电池分压链出 DNP) + V-4 (R_ILIM 档位) 三条, 仍必须同批落** ★ | ★**§1 / §2.1** ★ |
| ★**下一批的行号** ★ | ★**V-4: L537/L547 ⇒ V-3 落表后 L534/L544 · V-2: L1420~L1424 ⇒ L1417~L1421 · 仍用「唯一字符串 + assert count==1」定位** ★ | ★**§2.2** ★ |
| ★**下一批的 md5 撞车** ★ | ★**3 处 (V-2/V-3/V-4) ⇒ 同批落 ⇒ SW/MECH 只再重锚 1 次** ★ | ★**§2.3** ★ |
| ★**`.kicad_sch` 口径** ★ | ★**md5 永久不可当锚点 (★门禁自己会重铸 UUID★) ⇒ 台账只写「归一化后逐字节相同」** ★ | ★**§5** ★ |

---

> ★**本清单只登记与排期, ★不落盘、不拍板、不碰板、不碰别人的分片★ ⇒ ★**下一批请照 §6 的整串门禁 + §3 的 5 项配套一起做** ★ ★

---

## 9 · ★★【ISS-262 · 2026-11-17 03:4x · hw-lead】V-3 + V-4 同批落表清单 (★追加段 · 老字一句没删★)★★

> ★**本段作者**: hw-lead · ★**单号**: ISS-262 · ★**性质**: ★**只登记与排期, ★零落表 · 零拍板 · 零写盘真源★ ★
> ★**依据**: 任务书 `state/dispatch_briefs/ISS-262_hw_land_row_anchor_guard.md` §③③ · ★**数字全部来自本机实跑 (★日志 `HW/ISS262_acceptance_rc.log`★)** ★

### 9.1 · ★**哪些条目必须同批落 (★逐条 + 撞车类型★)** ★

| # | ★**条目** ★ | ★**撞车类型** ★ | ★**撞车详情 (★实测★)** ★ | ★**同批落的理由** ★ |
|---|---|---|---|---|
| 1 | ★**`HW/netlist_v1.csv` (表A)** ★ | ★**md5 撞车** ★ | ★**V-3=E 改 L181-L186 六行 · V-4=680 改 L47/L48/L497 三行 · V-2=1 改 L417/L418 网名 ⇒ 三条都改这同一个文件** ★ | ★**三处改动落进同一个 md5 ⇒ 必须一次落完, 落完只重锚 1 次 (★SW/MECH 侧省一轮★)** ★ |
| 2 | ★**`HW/netlist_v1_pins.csv` (表B)** ★ | ★**md5 撞车** ★ | ★**V-3=E 改 6 行 (脚表 L100/L307/L309 一带) · V-4=680 改 L329/L330 ⇒ 同一个文件** ★ | ★**同上** ★ |
| 3 | ★**`HW/BOM_v1.csv`** ★ | ★**md5 撞车** ★ | ★**V-3=E 改 3 行 (L86/L87 一带) · V-4=680 改 L97 ⇒ 同一个文件** ★ | ★**同上** ★ |
| 4 | ★**`state/gen_netlist.py` (真源)** ★ | ★**md5 撞车 + ★**行号漂移撞车** ★ | ★**V-3=E 删 `DEMO_DNP` 3 个条目 (L348 一带) ⇒ ★**L348 之后所有行号整体 -3** ★ · V-4=680 改 L557/L560/L562 一带 · V-2=1 改 L1454 ⇒ 三条都改这同一个文件** ★ | ★**★这一条是本批【唯一的行号漂移源】★ ★ (★见 9.2 的订正★)** ★ |
| 5 | ★**`HW/check_netlist_selfconsistency.py` 的 `EXPECT` 现状断言** ★ | ★**内容撞车 (★断言值随落表走★)** ★ | ★**V-3=E 要改 21 条断言 · V-4=680 要改 6 条 · V-2=1 要改 1 条 (`d4_a417_net`) ⇒ 同一个列表** ★ | ★**★同一批落 ⇒ 断言一次改齐; 分批落 ⇒ 中间态红, 且【改一半的断言】就是【假绿】的前身★ ★** ★ |
| 6 | ★**`HW/NETLIST_SELF_CONSISTENCY_SPEC.md` 的 `<!-- ANCHORS -->` 块** ★ | ★**内容撞车 (★整块重生成★)** ★ | ★**三条都要整块重生成 (★`state/land_v_values.py` 的 `regen_spec_anchors(root)`★)** ★ | ★**一次重生成 ⇒ 规格页与源码逐字一致 (★不一致 ⇒ 新闸 `HW/check_land_row_anchors.py` 直接红★)** ★ |
| 7 | ★**`state/p10_rows.json`** ★ | ★**md5 撞车** ★ | ★**V-4=680 改 J_CHG / BAT_CHG 行的 note (L688 一带)** ★ | ★**同批落** ★ |
| 8 | ★**`HW/CHARGE_BOARD_SPEC.md`** ★ | ★**md5 撞车** ★ | ★**V-4=680 改 §2.2 / §2.4 / §3.4 / §7 CSV / §8 / §9 / §10 共 15 处** ★ | ★**同批落** ★ |
| 9 | ★**`HW/SCHEMATIC_V1_SPEC.json`** ★ | ★**md5 撞车** ★ | ★**V-3=E 改 B-08 的 `level` / `imp` (L426/L427)** ★ | ★**同批落** ★ |

★**★口径订正 (★必须写进下一批的作业包★)★** ★:
> ★**「V-3 删 3 行 ⇒ 所有行号锚点 -3」这句话, 对【网表 / 脚表 / BOM 的行号】不成立** ★
> ★**★[实测]★ 表A 513 行不变 (只有 L181-L186 六行变) · 脚表 584 行不变 (6 行变) · BOM 218 行不变 (3 行变) ⇒ ★**CSV 的行号一条都不漂** ★ ★
> ★**★[实测]★ V-3=E 删的是 `state/gen_netlist.py:348` 那个 Python 字典的 3 个条目 ⇒ ★**真正 -3 的是【生成器源码行号】** ★ ★
> ★⇒ ★**下一批的作业包: 【表行锚点】不用改行号; 【生成器源码行锚点】必须改 (★F1 那对现在在 `state/gen_netlist.py` L400 / L413 —— ISS-249 落表后已与旧文里的 L381 / L393 不同了★)★ ★

### 9.2 · ★**落表顺序 (★参照 ISS-243 / ISS-249 / ISS-257 的既有硬顺序, ★不许自创★)** ★

★**★硬顺序 = `state/land_v_values.py` 的 `GEN_ORDER` (★既有常量, ★本单一个字没改★)★** ★:

```
① 改真源 (★state/gen_netlist.py / state/p10_rows.json / HW/SCHEMATIC_V1_SPEC.json / HW/CHARGE_BOARD_SPEC.md★)
      ↓
② 重生成 6 件 (★GEN_ORDER, ★顺序是硬的, ★不许换★)
   1. state/gen_netlist.py       ⇒ HW/netlist_v1.csv        (网表 表A)
   2. state/gen_kicad_net.py     ⇒ HW/netlist_v1.net
   3. state/gen_netlist_pins.py  ⇒ HW/netlist_v1_pins.csv   (脚表 表B)
   4. state/gen_bom.py           ⇒ HW/BOM_v1.csv
   5. state/gen_schematic_pages.py⇒ HW/SCHEMATIC_V1.md
   6. state/gen_kicad_sch.py     ⇒ HW/PCB/demo_mainboard*.kicad_sch
      ↓
③ 改门禁现状断言 (★HW/check_netlist_selfconsistency.py 的 EXPECT, ★落表器自带的 apply_expect_patch★)
      ↓
④ 规格页 ANCHORS 块整块重生成 (★regen_spec_anchors(root)★)
      ↓
⑤ 规格页 §5.5 + 落表台账 §16 / §18.4 (★带真实 md5★)
      ↓
⑥ ★**ISS-262 新增这一步: 行号锚点守卫 ★**
   python3 HW/check_land_row_anchors.py --reanchor
   ⇒ ★**打印「N 条锚点行号漂移, 新行号 = …」⇒ 机器改 EXPECT 行号 + 规格页 ANCHORS 行号 + 台账★ ★
   ⇒ ★**这一条已自动挂进 `state/land_v_values.py` 的落表后门禁链 (★不用人记得跑★)★ ★
      ↓
⑦ 落表后门禁实跑 (★顺序同上 + 新闸, ★任一条红 ⇒ 自动回滚★)
      ↓
⑧ 受保护 md5 核对 (★板 611b869e… / .kicad_pro 3e504d2b… 必须逐字节不变★)
```

★**★为什么第 ⑥ 步必须放在 ⑦ 之前 (★顺序是硬的, ★不许自创★)** ★:
> ★**门禁 `HW/check_netlist_selfconsistency.py` 是按【行号】找行的 ⇒ 行号没重锚 ⇒ 它查的根本不是那颗器件 ⇒ ★**「假绿」就是这么来的** ★ ⇒ ★**先重锚, 再跑门禁, 顺序反了就等于没跑★ ★**

### 9.3 · ★**落表后要重基线的完整清单 (★谁负责哪一跳★)** ★

| # | ★**要重基线的东西** ★ | ★**谁** ★ | ★**在哪改** ★ | ★**填什么** ★ |
|---|---|---|---|---|
| 1 | ★**网表 / 脚表 md5 台账** ★ | ★**hw-lead** ★ | ★**`HW/SCHEMATIC_LANDING_V1_LANDED.md` §18.4 (md5 台账表)** ★ | ★**单号 + 文件名 + 新 md5 + 旧 md5 四项同行齐全 (★四项缺一项 ⇒ SW/MECH 没法重锚★)** ★ |
| 2 | ★**SW 侧 md5 台账** ★ | ★**sw-lead** ★ | ★**`SW/SW_MD5_BASELINE_LEDGER.md` §1 `entries`** ★ | ★**`HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / (★BOM 若在表里★) 三条 ★** ★ |
| 3 | ★**MECH 侧 md5 台账** ★ | ★**mech-lead** ★ | ★**`MECH/HW_CROSS_REVIEW_TRIAGE.md` §1 `source_ledger.entries` + §3.1 留痕新增一行** ★ | ★**同上三项** ★ |
| 4 | ★**受保护脚本的 md5 字典 (4 处)** ★ | ★**hw-lead (HW 侧 2 处) + mech-lead (MECH 侧 2 处)** ★ | ★**① `HW/check_pin_function_labels.py` 的 `PROTECTED_MD5` (网表/脚表/BOM/板/`.kicad_pro` 5 条基线) ★② `HW/check_g1a7_selection_landed.py` 的板 md5 + 14 件三方位号核对 ★③ `MECH/cavity_recalc_check.py` 的 `MD5_EXPECTED` ★④ `MECH/check_demo_struct_truth.py` 的 `MD5_EXPECTED`** ★ | ★**★改 md5 基线 = 【承认新基线】, 必须在交卷单里说明为什么改 (★不许为了凑绿改★)★ ★** ★ |
| 5 | ★**BOM** ★ | ★**hw-lead** ★ | ★**`HW/BOM_v1.csv` + §18.4 台账 + `HW/check_pin_function_labels.py` 的 `PROTECTED_MD5`** ★ | ★**BOM 的 md5 与 218 行内容要跟网表同批变, 不许分批** ★ |
| 6 | ★**规格页 ANCHORS 块** ★ | ★**hw-lead (★落表器自动★)** ★ | ★**`HW/NETLIST_SELF_CONSISTENCY_SPEC.md` 的 `<!-- ANCHORS:BEGIN/END -->`** ★ | ★**★必须与 `HW/check_netlist_selfconsistency.py` 的 `EXPECT` 逐字一致 ⇒ 不一致 ⇒ 新闸直接红 (★已实跑验证: T7 用例★)★ ★** ★ |
| 7 | ★**★ISS-262 新闸的行号锚点台账★** ★ | ★**hw-lead (★落表器自动★)** ★ | ★**`HW/land_row_anchors_registry.json` + `HW/check_land_row_anchors.py` 里的 `REGISTRY_SHA256` 常量** ★ | ★**★机器写 (★`--reanchor` 自动同步★) ⇒ 不许人手改行号★ ★** ★ |

### 9.4 · ★**板那一趟 (★PCB 类★) ⇒ ★**排队, 不在本单**★ ★

| ★**板侧项** ★ | ★**为什么排板那一趟** ★ | ★**排队给谁** ★ |
|---|---|---|
| ★**V-2 的 B-3 (换封装) / B-4 (挪到 J_USB_C 旁 ≤3.0mm) / B-5 (D− 补 ESD)** ★ | ★**★落表器【不做】板那一趟 (★板 `611b869e…` 与 `.kicad_pro` `3e504d2b…` 必须逐字节不变★) ⇒ 干跑日志原样: 「V-2=1 的板那一趟本工具【不做】… 继续排队」** ★ | ★**板那一趟 (★老板 2026-11-11 10:07「先原理图后 PCB」口径★)** ★ |
| ★**R4×2 (ESD 双通道 / D− 侧) + R9 (ESD 距接口 ≤3.0mm)** ★ | ★**★D− 侧要新增位号 `D_ESD_USB_N` ⇒ 落表器侧【零配方】(`grep -c` = 0) ⇒ 网表/脚表/BOM 三处要加行 ⇒ 又是一次行号位移 (★本闸会自动报漂移并机器重锚★)** ★ | ★**板那一趟 + 落表器配方缺口 (★要 main 排下一趟给 hw-lead★)** ★ |
| ★**R3 (U_EN_SW 板封装 Value 属性)** ★ | ★**★板文件是受保护件 ⇒ 落表那趟不碰; ★**落表那趟的板侧清单是 4 条, 但落表器自己的 `board_delta` 字段只数到 3 条 ⇒ 差的就是 R3 这条, 落表那趟的作业包必须点名它** ★** ★ | ★**板那一趟** ★ |

---

> ★**★本段只登记与排期, ★零落表 · 零拍板 · 零写盘真源 · 板一个字节没碰★ ⇒ ★**下一批请照 §9.2 的硬顺序 + §9.3 的 7 项重基线一起做** ★ ★

---

## 10 · ★★【ISS-247 复验 · 2026-11-17 05:0x · hw-lead】下一批三条配方 dry-run 实测 + ★**真源行号漂移硬规矩**★★ (★追加段 · 老字一句没删★)★★

> ★**本段作者**: hw-lead · ★**单号**: ISS-247 (★复验轮★) · ★**性质**: ★**只登记与实测, 零落表 · 零拍板 · 零写真源** ★
> ★**依据**: ★**本机实跑 (★验收日志 `HW/ISS247_reverify_acceptance_rc.log` + 交卷单 `HANDOFF/2026-11-17_hw-lead_ISS247_复验与下一批落表路径实测.md`★)** ★
> ★**触发**: ★**网关 reload 后 ISS-247 任务书被重投 ⇒ 第一动作 = 查台账 (ISS-247 已 verified · F1 已由 ISS-249 真落) ⇒ 不重做已验证的交付物, 改成【复验 + 现状订正】★** ★

### 10.1 · ★**复验结论 (★ISS-247 五件交付物仍在盘且仍成立★)** ★

| ★**项** ★ | ★**2026-11-17 05:0x 实测** ★ |
|---|---|
| ★**F1 落表状态** ★ | ★**已落** (★`HW/check_iss247_f1_landed.py` rc=0 · S1~S6 全绿 · `--selftest` rc=0 11/11★) ★ |
| ★**R3 矛盾判据** ★ | ★**恰 2 条 (F2 + F3) · rc=1** (★F1 已消失★) ★ |
| ★**V-2/V-3/V-4 是否被代拍** ★ | ★**没有** (★`--expect-resolved` 仍 18 条★) ★ |
| ★**真盘 5 个受保护 md5** ★ | ★网表 `e06c1dd6…` · 脚表 `287e7861…` · BOM `94642d07…` · 板 `611b869e…` · `.kicad_pro` `3e504d2b…` (★跑前跑后逐字节不变★) ★ |
| ★**md5 现状注记** ★ | ★**§2.3 表里那三个值 (`611c3ba3…` / `16ac89f7…`) 已作废** ⇒ ★**现行 = ISS-249 (11-16 19:22) + ISS-257 (11-16 21:22) 两次合法落表后的 `e06c1dd6…` / `287e7861…` / `94642d07…`★** ★ |

### 10.2 · ★**下一批三条配方的沙盒 dry-run 实测 (★★每条都 rc=0 ⇒ 一次落的路径仍然通★★)** ★

★**沙盒**: `/home/yuewuya/.openclaw/tmpwork/iss247_dryrun` (★`rsync` 整树拷贝 107 MB ★ 真盘只读 ★ 跑完已 `rm -rf`★) ★

| ★**命令 (★沙盒内★)** ★ | ★**rc** ★ | ★**配方命中的现行真源位置 (★2026-11-17 05:0x 快照★)** ★ |
|---|---|---|
| ★`python3 state/land_v_values.py --decision V-3=E` ★ | ★**0** ★ | ★`state/gen_netlist.py:348` (删 `DEMO_DNP` 三行) + `:912` / `:914` (上下臂 value+note) + `HW/SCHEMATIC_V1_SPEC.json:426/427` (B-08 level/imp) + 门禁 EXPECT/selftest 9 处 ★ |
| ★`python3 state/land_v_values.py --decision V-4=680` ★ | ★**0** ★ | ★`state/gen_netlist.py:557` (2 处) + `:560` + `:562` + `state/p10_rows.json:688` + `HW/CHARGE_BOARD_SPEC.md` 12 处 ★ |
| ★`python3 state/land_v_values.py --decision V-2=1` ★ | ★**0** ★ | ★`state/gen_netlist.py:1454` (D_ESD_USB_D 挪 Type-C 侧) + 门禁断言 `d4_a417_net` ★ |

★**★每条配方都打印「(匹配 1 处)」⇒ 旧串在现行真源里唯一命中 ⇒ ISS-260 修过的 V-2 路径没被后续落表打穿 ⇒ 下一批不用先补配方, 直接落** ★
★**沙盒零写盘自证**: ★`md5sum -c` ⇒ `HW/netlist_v1.csv: OK` / `HW/netlist_v1_pins.csv: OK` / `HW/BOM_v1.csv: OK` ★

### 10.3 · ★★**【硬规矩 · 下一批落表前必读】真源行号是一次性快照, 落表那一刻就再漂**★★ ★

★★**F1 那对行号的历史 (★本轮实测, ★与 §9.1 的订正逐字一致★)** ★★

| ★**条目** ★ | ★**ISS-247 交卷时写的** ★ | ★**ISS-249 落表时写的** ★ | ★**2026-11-17 05:0x 实测** ★ | ★**漂了** ★ |
|---|---|---|---|---|
| ★**F1 改法 1 (FB_VBUS 后级行)** ★ | ★L381 ★ | ★L381 ★ | ★**L400** ★ | ★**+19** ★ |
| ★**F1 改法 2 (C_VBUS_GND 信号端行)** ★ | ★L393 ★ | ★L393 ★ | ★**L413** ★ | ★**+20** ★ |

⇒ ★**§2.2 表里那两行「现值」已经过期 (★它们是 ISS-249 当时的快照★)** ⇒ ★**下一批任何人照抄 §2.2 的 L537 / L547 / L1420~L1424 都会打偏** ★
⇒ ★**★行号 = 【一次性快照】, 只在落表那一刻有效★** ⇒ ★**下一批落表前必须重跑一次 dry-run 取当时的行号; 落表脚本一律用「唯一字符串 + 上下文锚点 + `assert count == 1`」定位, 不许裸行号 (★ISS-243 / ISS-249 / ISS-257 三个已落表单都是这么做的★)** ★
⇒ ★**同一条纪律对 SW/MECH 侧的 md5 锚点一样成立 (★md5 也是一次性快照★) ⇒ 下一批一次落完只广播一次新 md5, 两边各重锚 1 次** ★

### 10.4 · ★**本段对下一批作业包的要求 (★逐条, 落表人照抄即可★)** ★

1. ★**落表前**: ★**先在沙盒里 `python3 state/land_v_values.py --decision V-3=E --decision V-4=680 --decision V-2=1` (★dry-run·零写盘★) ⇒ 打印出当时的命中行号与 diff, 把它当【唯一权威行号】** ★
2. ★**落表中**: ★**用落表器自己的 Patch 机制 (★`old` 唯一命中 + `ctx` 锚点★) ⇒ 不依赖行号** ★
3. ★**落表后**: ★**必须按 ISS-262 §9.2 的硬顺序走 (★① 改真源 → ② 重生成 6 件 → ③ 改门禁 EXPECT → ④ 重生成规格页 ANCHORS → ⑤ 台账 → ⑥ `HW/check_land_row_anchors.py --reanchor` → ⑦ 落表后门禁实跑 → ⑧ 受保护 md5 核对★) ⇒ ★**⑥ 必须在 ⑦ 之前, 顺序反了就等于没跑门禁** ★
4. ★**落表后必跑**: ★**`HW/check_iss247_f1_landed.py` (rc=0) · `HW/check_netlist_contradiction_r3.py` (★仍恰 2 条 F2+F3 · rc=1★) · `HW/check_netlist_selfconsistency.py --expect-resolved` (★条数按落表器 stdout 的预期值, ★不许回退到 18★) · `HW/check_land_row_anchors.py` (rc=0) · 四道尺子 + `state/merge.py` + `state/gate_check.py`** ★
5. ★**落表后**: ★**广播一次新 md5 给 sw-lead / mech-lead (★四项齐全: 落表单号 + 文件名 + 新 md5 + 旧 md5★) ⇒ 链上是 H-1 重锚的第 7 跳** ★
