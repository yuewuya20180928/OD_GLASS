# ISS-262 · hw-lead 任务书 (第 2 趟·续做) —— 落表行号漂移的机器兜底 + V-3/V-4 同批落表清单

> ★**派活人**: 项目总工 (main / moli) · ★**派活时刻**: 2026-11-17 03:2x · ★**job**: cron `fb67af40` (ARS45 队列自动派活 · 第 3 趟)
> ★**权威任务书 = `state/dispatch_briefs/ISS-262_hw_land_row_anchor_guard.md` (★逐字读完再动手★)** ⇒ ★**本文件只加"第 2 趟的执行纪律 + 已完成/未完成盘点", 不改任务书内容★**
> ★**本单 = 内部活 · 原理图/网表侧 · 不是 PCB 布线/布局类 · 不是老板级拍板★**
> ★**零外发 · 零采购 · 不联系任何供应商 · 不下单 · V-2/V-3/V-4 一个值都不许落 (★老板还没拍★)**

---

## ① ★为什么有第 2 趟 (★main 本机实跑, 不是抄交卷报告★)

★**第 1 趟的会话被 harness 掐死了 (★不是你自己写崩★)**:

| 项 | 实测值 |
|---|---|
| 会话 | `agent:hw-lead:subagent:7922c2a0` (taskName `queue_iss262`) |
| 起止 | 02:33:32 → 02:57:05 (★runtimeMs 1410578 ≈ 23.5 分钟★) |
| 终止原因 | `openclaw:prompt-error` = **"This operation was aborted"** (★父 cron 跑完被收摊, 子会话一起被 abort★) |
| 盘上产物 | ★**只有一个交卷单骨架 (1034 B), B1~B6 全是 `_(施工中)_` / 零脚本 / 零日志 / 分片 0 条 (grep iss262 = 0)★** |

★**⇒ 第 2 趟的唯一目标: ★把东西落到盘上★, 别再攒到最后一次性写★**

★**第 1 趟已经想清楚、可以直接用的结论 (★原样抄自它的 transcript, 省你重想★)**:
- ★**锚点清单是"混合"的**: `state/gen_netlist.py` **L381 / L393** (★F1 那对★) · **L40 / L184** (★在 L344 之前 ⇒ 不漂★) · `HW/netlist_v1.csv` **L8 / L12** (★F1 两行, 说的是**网表行号**不是脚本行号★) · `HW/check_pin_function_labels.py` 的 `PROTECTED_MD5` (★L127★) + `KNOWN_DEFECTS` (★L143★) ★
- ★**判定"某处 `L<n>` 指向哪个文件"的办法 = 用 snippet 反查**: snippet 带 `add(` 前缀的 ⇒ 只可能在 `state/gen_netlist.py`; 只含 `VBUS_5V_F1` + `C_VBUS_OUT` 两个词的 ⇒ 只可能在 `HW/netlist_v1.csv` ⇒ ★**这样清单才能机器枚举, 不许手抄★**
- ★**"V-3 会删 3 行 DEMO_DNP ⇒ 行号整体 -3" ⇒ 只有 L381/L393 这种"指向 344 行之后"的才真的漂★** ⇒ ★**闸必须能区分「漂了」和「没漂」**

---

## ② ★本趟时间预算 (★硬纪律★ ⇒ 违反即交卷无效★)

★**总预算 25 分钟, 分 5 段, ★每段结束立刻把结果 append 进交卷单文件★ (不许攒到最后)★**:

| 段 | 时长 | 做什么 | 落盘物 |
|---|---|---|---|
| P0 | ≤3 min | 读权威任务书 + 读 `state/land_v_values.py` 现状 (2158 行, ★**只读不许重写**★) | 交卷单 B1 填"结论一句话" |
| P1 | ≤12 min | ★**写闸 + `--selftest` ≥4 条反向用例 + 实跑★** | 新闸脚本 (★名字自己定, 但 `--selftest` 必须能独立跑★) + 原始日志 |
| P2 | ≤4 min | 追加 `HW/SCHEMATIC_LANDING_NEXT_BATCH_V1.md` 的同批落表清单 (★老字不许删★) | 文档追加段 |
| P3 | ≤3 min | 分片 (★只走 `python3 state/frag_write.py --agent hw-lead`★) | `state/fragments/hw.yaml` |
| P4 | ≤3 min | 交卷单 B1~B6 填满 + 验收 rc 原样贴 | 交卷单 (★≥6 KB★) |

★**★到点就交卷★**: ★**若 P1 还没做完, 就把 P1 做完为止, 然后如实写"交付物② 未交, 下一趟补", 不许超时硬撑, 不许交空卷★**
★**★每条命令不许超过 120 秒★** ⇒ ★**长命令一律 `nohup ... &` 后台跑 + 轮询日志★** (★`state/land_v_values.py --selftest` 与 `check_netlist_selfconsistency.py --selftest` 都不慢, 但 `--expect-resolved` 那条别在前台跑满★)

---

## ③ ★本趟的交付范围 (★比第 1 趟收窄, 保证能落盘★)

★**必交 (本趟)**:
1. ★**交付物①: 行号锚点断言闸 + `--selftest` (★≥4 条反向用例: ①纯漂移(行号变/内容不变)必须被报出来 ②内容变(行号不变)必须红 ③行号+内容都变必须红 ④一条都没漂的正向必须绿★)**
   - ★**判据三条一条不许少** (★抄权威任务书 §③① 的 1/2/3★): 落表前记录 (文件, 行号, 内容指纹) ⇒ 清单**机器可枚举** · 落表后三种情形分开判 (**"纯漂移"必须报出来不许静默**) · 锚点更新必须**机器写**
   - ★**落点二选一你自己定**: 方案 A = 写进 `state/land_v_values.py` (落表后自动复核, ★**推荐★**) · 方案 B = 新建独立门禁 `HW/check_land_row_anchors.py` (★**若选 B, 必须在交卷单写明"落表后要人记得跑"这个弱点★**)
   - ★**自测全程真盘零写入 (走临时副本)**, 跑完 5 个受保护 md5 必须逐字节不变
2. ★**交付物⑤: 验收原始日志** (★rc 原样贴进交卷单, 零转录误差★)
3. ★**交卷单**: `HANDOFF/2026-11-17_hw-lead_ISS262_落表行号锚点兜底与同批落表清单.md` ★**B1~B6 六块齐全, 标题要含 gate_check 认的语义关键词** (★B1 含"结论" · B2 含"验收标准自评" · B3 含"证据分级" · B4 含"接口取值" · B5 含"未决/卡点" · B6 含"复现命令"★)
4. ★**分片**: `state/fragments/hw.yaml` (★只走 `python3 state/frag_write.py --agent hw-lead` 原子写★)

★**可延到下一趟 (★若真没时间, 交卷单必须如实写"未交"★)**:
5. ★**交付物②: `HW/SCHEMATIC_LANDING_NEXT_BATCH_V1.md` 追加同批落表清单** (★文件已在盘, 261 行 / 24.6 KB, ★**只追加, 老字不许删**★)
   - ★**要写的点任务书 §③③ 已经全给了 (★不用再设计, 直接抄成清单★)**: 哪些条目必须同批落 (★依据 = md5 撞车 4 处 + 行号漂移 1 处 (V-3 删 3 行 DNP ⇒ F1 行号 -3)★, 逐条列 + 撞车类型) · 落表顺序 (★参照 ISS-243/ISS-249/ISS-257 的既有硬顺序, 不许自创★) · 落表后重基线完整清单 (★网表/脚表 md5 台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` §18.4 · `SW/SW_MD5_BASELINE_LEDGER.md` §1 (sw-lead) · `MECH/HW_CROSS_REVIEW_TRIAGE.md` §1 (mech-lead) · 4 个受保护脚本的 `MD5_EXPECTED` 字典 · BOM★) · ★**板那一趟 (PCB 类) 明确写"排队, 不在本单"★**

---

## ④ ★验收 (★本机实跑, 原样输出, 全部不许省★)

```
python3 state/land_v_values.py --decision V-2=1      ⇒ rc=0  (干跑, 零写盘)
python3 state/land_v_values.py --decision V-3=E      ⇒ rc=0
python3 state/land_v_values.py --decision V-4=680    ⇒ rc=0
python3 state/land_v_values.py --selftest            ⇒ rc=0  (★条数 ≥ 11 + 你新加的 4 条, 一条不许删★)
python3 state/check_netlist.py                       ⇒ rc=0
python3 state/check_netlist_pins.py                  ⇒ rc=0
python3 state/check_sch_erc.py                       ⇒ rc=0  (ERC=0)
python3 state/check_sch_pinfull.py                   ⇒ rc=0  (584=584 · K=0)
python3 HW/check_netlist_selfconsistency.py           ⇒ rc=0
python3 HW/check_netlist_selfconsistency.py --expect-resolved ⇒ rc=1 (★仍 18 条, 一条不许上升★)
python3 HW/check_g1a7_selection_landed.py             ⇒ rc=0
python3 state/check_stage_g1a.py                     ⇒ rc=1 (★只差 G1a-4 + G1a-8, 别的不许红★)
python3 state/merge.py && python3 state/gate_check.py ⇒ rc=0 (★Q1 18/18★)
md5sum (5 件受保护)                                  ⇒ 逐字节不变 (★跑前跑后对照★)
```

★**受保护 5 件的现值 (★main 03:1x 实测, 你跑完要逐字节对上★)**:
`HW/netlist_v1.csv` = `e06c1dd633566aa44732762c2ff99d1c` · `HW/netlist_v1_pins.csv` = `287e7861a0d1007748d92d9fbecdd490` · `HW/BOM_v1.csv` = `94642d07a69e8d60dd2af57f69b93607` · `HW/PCB/demo_mainboard.kicad_pcb` = `611b869e13518c3c023fb178f91a0075` · `HW/PCB/demo_mainboard.kicad_pro` = `3e504d2be83152e337949723e909be1b`

★**反向自证 (必做)**: ★**沙盒里让一条锚点行号漂移 ⇒ 闸必须抓到 ⇒ 装回 ⇒ 又绿★** (★沙盒用临时副本, 真盘零写入★)

---

## ⑤ 边界 (★违反即交卷无效★)

- ★**零落表**: V-2 / V-3 / V-4 ★**一条都不许落** (★老板还没拍 ⇒ 网表/脚表/BOM 逐字节不许变★)
- ★**零外发** (★一次邮件都不许发·不许联系供应商★) · 零采购 · 零下单
- ★**不许重写 `state/land_v_values.py` 的既有 2158 行** (★ISS-260 交付已验收: 干跑三条全 rc=0 · `--selftest` 11/11 · 5 个 md5 逐字节不变★) ⇒ ★**只许加新闸 / 新断言, 不许动既有配方与既有用例★**
- ★**不碰 PCB 布线 / 布局 / 板框 / 板文件** (★板 `611b869e…` 与 `.kicad_pro` `3e504d2b…` 必须逐字节不变★)
- ★**不碰 `SW/` / `MECH/` / 别人的分片** (★只读跑它们的门禁取证据可以★)
- ★**不改判据阈值 / 不删反向用例 / 不加「跳过 md5」默认值**
- ★**不替老板拍板** (★A1/A2/A3/A4/A5 一条都不许代拍★)
- ★**不自签 `state/issue_log.yaml`** (★verify 留给 main★)
- ★**不改 `PROJECT_TRACKER.md` §0 锁死表**

## ⑥ ★给 main 的 (★两条, 写进交卷单§B5/§B6★)

1. ★**「老板拍完 A1+A2+A3 ⇒ 一条命令 ⇒ 落多少条」这个数字必须订正**: ★**ISS-260 实测 = 网表侧 14 条 (V-3 13 + V-4 1) + 4 条等板那一趟 (R4×2 + R9 + R3)★** ⇒ ★**决策页 §A-补7 现在写的「15 条一次落」是错的 (★main 会在本轮改★)** ⇒ ★**你本单不碰决策页, 但把实测数字写进交卷单给 main 用★**
2. ★**W-1 (USB D− 的 ESD 方案) 三个小问 (W-1a 架构+型号 / W-1b D− 侧怎么办 / W-1c 型号与证据等级) + 三选项代价 = ISS-260 §B4 已出, main 要转进决策页** ⇒ ★**若你从落表器侧发现 W-1b 第四条路 (新增位号 `D_ESD_USB_N`) 的配方缺口, 一并报给 main★**

★**额外纪律 (★通用, 三条都要守★)**:
① ★**写分片必须用 `python3 state/frag_write.py --agent hw-lead` (禁止 `open(p,"w")`)★**
② ★**只写本任务允许的文件, 不碰别人的★**
③ ★**证据分级 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` 必须标★**
④ ★**不许外发任何邮件/询价/问询/采购 (老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料) ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ⇒ 没有"批一句可以发"这个选项★**
⑤ ★**交卷前跑 `python3 state/merge.py` (rc 必须 0) && `python3 state/gate_check.py` (Q1 必须 18/18) 并把输出贴进回复★**
