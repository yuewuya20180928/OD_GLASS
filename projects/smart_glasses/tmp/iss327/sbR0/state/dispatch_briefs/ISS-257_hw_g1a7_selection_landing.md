# ISS-257 · hw-lead 任务书 —— G1a-7「选型已落表」: 14 件必装 `[待选型]` 落成真型号 + 重生成链

> ★**派活人**: 项目总工 (main / moli) · ★**派活时刻**: 2026-11-16 20:3x · ★**job**: cron `775d9893` (ARS45 继续执行后继计划)
> ★**本单 = 内部活 · 原理图主线内 · 不是 PCB 布线/布局类 · 不是老板级拍板**
> ★**老板 2026-11-11 10:07 主线口径**: 「先解决原理图绘制的问题, 再解决 PCB 绘制的问题」 ⇒ 本单正是主线正中央的一步。
> ★**老板 2026-11-12 02:02 政策**: 不再发信, 全靠自己查资料 ⇒ 证据自己查, 标证据等级, 查不到就写降级方案, **不许去凑「等一句可以发」**。
> ★**零外发 · 零采购 · 不联系任何供应商 · 不下单**。

---

## ① 目标 (一句话)

★**把 BOM 里「必装 ∩ value 含 `[待选型]`」的 14 件, 落成真型号 (value + opn) ⇒ `state/check_stage_g1a.py` 的 **G1a-7 转绿** ⇒ 同时把生成链 (网表 → 脚表 → BOM → 原理图) 按硬顺序重生成, 不留半新半旧。**

**目标状态 (全部可机器判定)**:
1. `HW/BOM_v1.csv` 里「必装 ∩ value 含 `[待选型]`」= **0 件** (或 = 剩下的每件都在交卷单里写明"等老板哪一条", 且 value 已是**真实可采购型号**而不是占位词)
2. `python3 state/check_stage_g1a.py` ⇒ **G1a-7 ✅**, 且 **G1a-1/2/3/5/6 仍然 ✅** (不许把别的判据弄红)
3. 生成链 6 件全部是**本轮落表之后**重生成的
4. 落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` 有本单**新段** (§18), 四字段齐全 (单号 / 文件名 / 新旧 md5 同一行)
5. 一个新门禁 + `--selftest` 反向用例 (证明判据真在被读)
6. 交卷单 + 分片

---

## ② 病灶 (★main 2026-11-16 20:2x 本机实跑, 原样输出, 不是抄交卷报告★)

```
$ python3 state/check_stage_g1a.py
  ✅ G1a-1  ERC = 0 (KiCad 自己跑 ERC)
  ✅ G1a-2  图上脚数 == 表里脚数 (K=0)
  ✅ G1a-3  KiCad 真能打开/导出 (loadable)
  ❌ G1a-4  落表已清零 (翻面口径)          ← ★不是本单的活 (见 §⑦)
  ✅ G1a-5  网表尺子 (含表↔网表双向一致)
  ✅ G1a-6  网表脚表尺子 (针脚归属唯一)
  ❌ G1a-7  选型已落表 (必装件无「[待选型]」)
         必装且仍写「[待选型]」= 14 件 ⇒ D_ESD_CAM(…) D_ESD_DEMO(…) D_ESD_TC(…) D_ESD_USB_D(…)
         D_TVS_VBUS(…) FB_DEMO(…) FB_VBUS(…) Q_AND(…) Q_CHG_LED(…) Q_ENVC(…) Q_PG(…)
         R_SUPV_DIV1(…) R_SUPV_DIV2(…) U_PWR_SW(…)
  ❌ G1a-8  关机语义 + 负载开关选型已决      ← ★等老板审阅 (见 §⑦)
❌ G1a 还差 3 条
```

★**14 件的现值 (main 自己从 `HW/netlist_v1.csv` 逐行读出来的, 不是推测)**:

| # | 位号 | 现 value (含 `[待选型]`) | 板 | 板侧焊盘 | 备注 (从网表 note 摘) |
|---|---|---|---|---|---|
| 1 | `D_ESD_CAM` | ESD 阵列 [待选型] (多通道 CSI) | MAIN_PCB | 2 焊盘 | 跨铰链 CSI 主板侧 ESD 位 |
| 2 | `D_ESD_DEMO` | ESD 阵列 [待选型] (USB 2.0) | MAIN_PCB | 2 焊盘 | USB-C VBUS 入口 ESD |
| 3 | `D_ESD_TC` | ESD 阵列 [待选型] | CHG_BOARD | 待定 | Type-C VBUS 入口 ESD |
| 4 | `D_ESD_USB_D` | ESD 阵列 [待选型] (USB 2.0 双通道) | MAIN_PCB | 2 焊盘 | 紧贴 J_USB_C |
| 5 | `D_TVS_VBUS` | 5V 级单向 TVS [待选型] | CHG_BOARD | 待定 | VRWM 5-6V · 脉冲 ≥3A |
| 6 | `FB_DEMO` | π 滤波磁珠 [待选型] | MAIN_PCB | 2 焊盘 | VBUS π 滤波 (磁珠+体电容) |
| 7 | `FB_VBUS` | π 滤波磁珠 [待选型] | CHG_BOARD | 待定 | 充电 IC 环路稳定性 |
| 8 | `Q_AND` | [待选型] N-MOS (硬件 AND) | MAIN_PCB | 3 焊盘 | 复位链 |
| 9 | `Q_CHG_LED` | [待选型] N-MOS | CHG_BOARD | 待定 | 充电灯本地开关管 |
| 10 | `Q_ENVC` | [待选型] N-MOS (反相) | MAIN_PCB | 3 焊盘 | 顺序链 |
| 11 | `Q_PG` | [待选型] **P-MOS 高边开关** (低漏, Vgs(th) 明确) | MAIN_PCB | 3 焊盘 | ★P0 修正件 (源极接 ON / 漏极接 BAT_SW) |
| 12 | `R_SUPV_DIV1` | [待选型] 分压上臂 (0Ω 跳线位) | MAIN_PCB | 待定 | ★**最终阻值 = 老板 A1 (V-3)** |
| 13 | `R_SUPV_DIV2` | [待选型] 分压下臂 (0Ω 跳线位) | MAIN_PCB | 待定 | ★**最终阻值 = 老板 A1 (V-3)** |
| 14 | `U_PWR_SW` | [待选型] 负载开关 (≥2A, R_on ≤40mΩ@3.7V, IQ ≤5µA, 带反向阻断) | MAIN_PCB | UQFN-4 RAA 0.85×0.75mm 0.4mm pitch | ★**opn 列现值已写 `TPS22991RAA`** |

★**14 件的网表 `footprint` 列与 `opn` 列现在全是空的 (只有 `U_PWR_SW` 有 opn = `TPS22991RAA`)** ⇒ ★**落表只碰 value / opn / evidence 三列文字, 封装列一个字不许动**。

★**当前受保护 md5 (main 20:2x 实测, 你交卷后必须逐条对账)**:
网表 `16ac89f77c25a3f61834cc7ebcd78a7f` · 脚表 `ef436a37…` · BOM `2a7305741134788dfee9f13f34c656b4` · 板 `611b869e…` · `.kicad_pro` `3e504d2b…`
★**板 + `.kicad_pro` 必须逐字节不变** (板侧 = PCB 类, 按老板 11-11 10:07 口径**排队不派**)。

---

## ③ 证据已经在盘上了 (★**不许从零重查**★)

★**选型不是这单的难点, 难点是"落表不许改脚数/封装"。选型矩阵已经有人做完了:**

| 已有件 | 内容 | 出处 |
|---|---|---|
| ★**`HW/PART_SELECTION_MATRIX_2026-11-16.md`** | ★**22/22 覆盖** (ISS-241 交卷) · 每件 ≥2 候选 + 官方参数 + 封装兼容性 + 降级方案 | sw-lead 11-16 14:3x, main 已独立复验 (`HW/check_part_selection_matrix.py` rc=0 8/8 · `--selftest` 9/9) |
| `HW/check_part_selection_matrix.py` | 矩阵机器门禁 (8/8) | 同上 |
| `HANDOFF/2026-11-16_sw-lead_ISS244_选型缺口自查补全与OPN回填清单.md` | ISS-244 的 P1~P6 (含 OPN 回填清单) | sw-lead 11-16 15:5x |
| `SW/LOAD_SWITCH_SELECTION_FACTS.md` + `HANDOFF/2026-11-16_sw-lead_ISS172_负载开关选型证据矩阵.md` | 负载开关 ≥3 候选 × 8 条判据 + RCB 缺口 | sw-lead ISS-172 (verified) |
| `HW/POWER_SHUTDOWN_V3.md §2` | 负载开关选型 8 条判据 | 主规格 |
| `HW/STEP1_PARTS_SPEC.md` | demo 板器件规格 (含 RULING=A 块) | hw-lead |

★**你的动作 = 把矩阵里的推荐/候选落成真型号, 而不是重新做一遍选型。**
★**矩阵里没有的 (或矩阵只给了候选没给结论的) ⇒ 才允许自己查**, 且必须标证据等级 `[官网]` / `[实测]` / `[媒体]` / `[推算]` / `[0数据]`; ★**查不到 ⇒ 写降级方案 + 标 [0数据] ⇒ 绝不许编型号**。

---

## ④ 落表口径 (★**硬约束, 违反就是本单失败**★)

1. ★**只许改 `value` / `opn` / `evidence` 三列文字** ⇒ ★**不许改**: 脚数 (基准 `HW/netlist_v1_pins.csv` 现 **584 脚 / 218 器件** · `state/check_sch_pinfull.py` 现 584=584 · K=0) · `footprint` 列 · `dnp` 列 (DNP 口径是 R11 等判据的基准) · 任何 `net` / `node1` / `node2` (★**改连接 = 改网表 = 另一件事, 本单不碰**★) · `tbd` 列 · `note` 列 (除非是补本单落表来源, 那就在落表台账写, 别塞进 note)。
2. ★**不许改脚数去迁就真器件**: 真实的多通道 ESD 阵列是 3~6 脚, 而网表现在把 4 件 ESD 建成 **2 脚模型 (信号 + GND)** ⇒ ★**落 2 脚能实现真实现的型号 (单线 ESD/TVS 二极管), 并把"另一条数据线目前无保护"登记成 need** ⇒ ★**不许把网表改成 3 脚/6 脚** (那要板侧重生成 = PCB 类, 不派)。
3. ★**`U_PWR_SW`**: value 必须落成 **网表 `opn` 列现写的 `TPS22991RAA`** (★**不许自选型号·不许换封装·不许换 RON/IQ 档位**★) ⇒ 理由: opn 列已经是项目总工 11-16 07:0x 的推荐 (决策页 §A5 / §Q2 的建议默认 = A), ★**同封装 ⇒ 后改是"换料不换板", 零成本** ⇒ ★**交卷单里必须明写「这是决策页默认, 待老板一句追认」**, 并在分片里登记一条 need 给 main (让 main 把这一条放进老板待追认清单, ★不许自己把这条单子从老板清单里划掉★)。
4. ★**`R_SUPV_DIV1` / `R_SUPV_DIV2`**: ★**最终阻值 = 老板 A1 (V-3), 还没拍** ⇒ ★**不许编一个具体阻值** ⇒ 落 **真型号的 0Ω 跳线 (0Ω ±1% 电阻, 封装不许写死)** + value 尾巴明写「V-3 分压最终阻值待 A1 拍板」⇒ ★**这是真值 (设计现状就是 0Ω 跳线位), 不是占位词 ⇒ 门禁能过, 真相也写着** ⇒ ★**"0Ω 两颗同时短接会把 V_SOC_IO 直通 SUPV_SENSE"这个设计缺口必须登记成 need 交 main (依赖 A1)**, 不许自己拍阻值。
5. ★**不许用"待定/待选型/TBD/待拍"这类占位词去糊弄 G1a-7** ⇒ value 里必须出现**真实可采购的型号或规格** (例: `PESD5V0S1BA` / `0Ω ±1%` / `BSS138` / 具体 P-MOS 型号) ⇒ ★**占位词糊弄 = 假绿, 铁律不许**。
6. ★**不许落 V-2 / V-3 / V-4 三条老板级落表** (决策页 A1/A2/A3) ⇒ ★**尤其 V-3 (R_SUPV_DIV1/2 的最终阻值) 与 V-4 (R_ILIM 档位) 不许碰** ⇒ V-4 相关的 `R_ILIM` 那一行本单一个字不许动。

---

## ⑤ 交付物 (★缺一件不算交卷★)

| # | 交付物 | 位置 / 说明 |
|---|---|---|
| 1 | ★**真源落表** | ★**`state/gen_netlist.py` 里对应行的 value/opn/evidence 文字** (★**不许手改 `HW/netlist_v1.csv`** ★ — CSV 是生成物, 手改会被下次生成覆盖) |
| 2 | ★**生成链重生成 (硬顺序)** | `python3 state/gen_netlist.py && python3 state/gen_kicad_net.py && python3 state/gen_netlist_pins.py && python3 state/gen_bom.py && python3 state/gen_schematic_pages.py && python3 state/gen_kicad_sch.py` (★6 条全 rc=0★ · ★**板那条不许跑** ★: `bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py` = 板侧 = PCB 类 = 不派★) |
| 3 | ★**落表台账新段** | `HW/SCHEMATIC_LANDING_V1_LANDED.md` **§18** (★沿用 §17 的格式: 改了哪一行(行号+改前/改后) · 跑了哪条命令 + 输出行 · **每个产物的新旧 md5 同一行** · 反向用例清单 · 没落的那几条 + 为什么★) |
| 4 | ★**新门禁** | ★**`HW/check_g1a7_selection_landed.py`** (+ `--selftest`) ⇒ 判据: ① 必装 ∩ `[待选型]` = 0 ② 14 个位号逐个点名: value 非空 / 不含占位词 / opn 非空 ③ 脚数仍是 584 / 器件 218 / K=0 ④ 板 + `.kicad_pro` md5 逐字节不变 ⇒ ★**反向用例 ≥6 条** (把某个 value 改回 `[待选型]` ⇒ 必须红; 删一个位号 ⇒ 必须红; 改脚数 ⇒ 必须红 …) |
| 5 | ★**交卷单** | `HANDOFF/2026-11-16_hw-lead_ISS257_G1a7选型落表.md` (★B1~B6 齐全: B1 病灶 / B2 改了什么 / B3 落表台账 / B4 反向自证 / B5 门禁原样输出 / B6 边界自审★) |
| 6 | ★**分片** | `state/fragments/hw.yaml` (★**只走 `state/frag_write.py --agent hw-lead` 原子写★** · ★只加自己的 key★ · ★不许碰 sw.yaml / mech.yaml / pm.yaml★) |

---

## ⑥ 验收 (★main 会照这 15 条独立复跑, 原样贴 rc★)

```
python3 state/check_stage_g1a.py                 # rc=1 但 ★G1a-7 ✅★ · G1a-1/2/3/5/6 必须仍 ✅
python3 state/check_stage_g1a.py --selftest      # rc=0 (★不许少用例★)
python3 HW/check_g1a7_selection_landed.py        # rc=0  (★本单新门禁★)
python3 HW/check_g1a7_selection_landed.py --selftest   # rc=0 (★反向用例全抓到★)
python3 state/check_netlist.py                  # rc=0
python3 state/check_netlist_pins.py             # rc=0
python3 state/check_sch_erc.py                  # rc=0 (ERC=0)
python3 state/check_sch_pinfull.py              # rc=0 (图上 584 脚 = 表里 584 脚 · K=0)
python3 HW/check_netlist_selfconsistency.py      # rc=0 (现状守卫)
python3 HW/check_netlist_selfconsistency.py --expect-resolved   # rc=1 (★仍 18 条, ★一条不许上升★)
python3 HW/check_netlist_contradiction_r3.py     # rc=1 (★FINDINGS 仍 = 2 (F2+F3) ★)
python3 HW/check_netlist_contradiction_r3.py --selftest          # rc=0 (★12/12 不许少★)
python3 state/merge.py && python3 state/gate_check.py           # rc=0 (★Q1 18/18★)
md5sum HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro
# ★前三个会变 (落表所致) ★后两个必须逐字节不变: 611b869e… / 3e504d2b… ★
```

★**反向自证 (必做, 配方照抄 §17.8 的三步沙盒法)**: 把改动的几行改回旧值 ⇒ 重生成 ⇒ ★**新门禁必须 rc=1** ⇒ 装回 ⇒ rc=0 ⇒ ★**证明判据真在被读, 不是把红灯调没**。

★**H-1 重锚预告 (写交卷单, 别自己动别人的域)**: 落表 ⇒ 网表/脚表/BOM 三个 md5 变 ⇒ ★**SW 侧 `SW/tools/check_demo_panel_spec.py` 的 R6 锚点与 MECH 侧 `MECH/check_demo_struct_truth.py` 的 G5b/C21 锚点会过期变红** ⇒ ★**这是"上游合法落表 ⇒ 下游锚点过期", 不是你的锅** ⇒ 你只负责: ① 落表台账里把**新 md5 四字段齐全**写全 ② 在分片里给 sw-lead / mech-lead 各登记一条 need (单号 + 新旧 md5 + 文件名) ⇒ ★**重锚由 main 另派, 你不许碰 SW/ MECH/ 的台账**。

---

## ⑦ 明确不归本单 (★省得你越界★)

- ★**G1a-4** (落表已清零 18 条) = V-2/V-3/V-4 三条老板级落表 ⇒ ★**等老板 A1/A2/A3 ⇒ 本单不许碰**。
- ★**G1a-8** (关机语义) = `ISS-097` 是**老板审阅件** (★铁律: main 自产的文档不许自己验★) ⇒ ★**不许把 ISS-097 落 verified** ⇒ 本单不许碰。
- ★**板侧 / 布线 / 布局 / 板框 / 焊盘号 / 封装号 (ISS-169 的 15 件封装脚号)** = PCB 类 ⇒ ★**不派, 排队** ⇒ 板 md5 必须逐字节不变。
- ★**采购**: 不下单、不询价、不联系供应商 ⇒ 选型只到"型号 + 官方参数 + 证据等级"为止。
- ★**老板级拍板项** (§A5 负载开关优先级序 / A1 V-3 / A2 V-4 / A6 屏版本 / A7 SoM 形态 / A8 板长): ★**一律不许代拍** ⇒ 只登记 need。

---

## ⑧ 边界 (★违反即本单作废★)

★**零外发** (不连任何供应商 · 不发邮件 · 不下单 · 不发 GET 以外的下载) · ★**零 clone / 零 pip install / 零大文件下载** (★本机下载 ≈6 KB/s ⇒ 98 MB 要 4.6 小时 ⇒ 一律不许下★) · ★**零实物** ([实测] 条数 = 0) · ★**不碰板 / 布线 / 布局 / 板框** · ★**不碰 `SW/` `MECH/` 的文件与分片** · ★**不改 `state/issue_log.yaml`** (status 留给 main 落 verified) · ★**不改 `PROJECT_TRACKER.md`** (尤其 §0 锁死表) · ★**不碰 `DECISION_PENDING_2026-11-16.md`** (那是老板的页面) · ★**不改判据阈值** · ★**不改 `state/check_sch_erc.py` / `check_sch_pinfull.py`** (★它们内部会调 `gen_kicad_sch.py` 重铸 uuid ⇒ 跑一次就改 mtime ★ **本单不改它们**) · ★**不自签 verified**。

---

## ⑨ 时间纪律 (★本项目 11-16 实测出来的铁律★)

★**子会话默认 600s 会被掐死 (本项目已掐死 6 次)。你这次有 90 分钟, 但**别把成果攒在内存里**★:
· ★**第 1 步就把"改哪几行 + 型号是什么"写进 `HW/SCHEMATIC_LANDING_V1_LANDED.md` §18 草稿并落盘**;
· ★**每落一个文件就刷一次盘**, 交卷单写一半也算交卷 (宁可交半份带 rc 的, 不要交一份没落盘的);
· ★**沙盒反向自证放在最后** (它最费时间, 但它是"判据不是摆设"的唯一证据);
· ★**若时间不够 ⇒ 交"已落表 + 已重生成 + 已跑门禁 + 交卷单草稿"**, 并在交卷单里写明还差什么 ⇒ ★**不许硬撑到超时被掐, 那样一个字都不留**。

★**遇到任何"必须老板拍"的岔路 ⇒ 不要停: 选那个**不代拍**的分支继续做, 并把它登记成 need 交 main。**
