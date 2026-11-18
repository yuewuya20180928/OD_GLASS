# ISS-262 · hw-lead 任务书 —— 落表行号漂移的机器兜底 + V-3/V-4 同批落表清单

> ★**派活人**: 项目总工 (main / moli) · ★**派活时刻**: 2026-11-17 00:4x · ★**job**: cron `775d9893` (ARS45 继续执行后继计划)
> ★**本单 = 内部活 · 原理图/网表侧 · ★不是 PCB 布线/布局类 · 不是老板级拍板★**
> ★**老板 2026-11-11 10:07 主线口径**: 「当前主线 = 硬件原理图 demo 绘制 ⇒ 先解决原理图绘制的问题, 再解决 PCB 绘制的问题」 ⇒ 本单在主线正中央 (原理图侧落表工具的防假绿兜底)。
> ★**老板 2026-11-12 02:02 政策**: 不再发信, 全靠自己查资料 ⇒ 证据自己查, 标证据等级, 查不到写降级方案。
> ★**零外发 · 零采购 · 不联系任何供应商 · 不下单 · 一个字都不许落表 (V-2/V-3/V-4 老板都还没拍)**。

---

## ① 目标 (一句话)

★**给落表链加一道「行号漂移 ⇒ 假绿」的机器兜底** ⇒ ★**老板拍完 A1/A2/A3 后一次落 14 条时, 门禁必须能发现「锚点行的行号被挪了而内容没变」, 不许再出现「换了行照样绿」** ★★
★**外加**: 出【V-3 + V-4 落表批次的同批落表次序 + 落表后重基线清单】, ★**因为 V-3 会删 3 行 DEMO_DNP ⇒ 所有行号锚点 -3★** ★

---

## ② 病灶 (★main 2026-11-17 00:3x 本机实跑, 原样输出, 不是抄交卷报告★)

★**已确认的好消息 (ISS-260 交付已验收)**: 落表器三条干跑全绿, 零写盘:
```
$ python3 state/land_v_values.py --decision V-2=1   ⇒ rc=0
$ python3 state/land_v_values.py --decision V-3=E   ⇒ rc=0
$ python3 state/land_v_values.py --decision V-4=680 ⇒ rc=0
$ python3 state/land_v_values.py --decision V-2=2   ⇒ rc=2  (必须打回, 守得住)
$ python3 state/land_v_values.py --selftest          ⇒ rc=0  (11/11)
$ md5sum HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv \
         HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro
  e06c1dd633566aa44732762c2ff99d1c  HW/netlist_v1.csv
  287e7861a0d1007748d92d9fbecdd490  HW/netlist_v1_pins.csv
  94642d07a69e8d60dd2af57f69b93607  HW/BOM_v1.csv
  611b869e13518c3c023fb178f91a0075  HW/PCB/demo_mainboard.kicad_pcb
  3e504d2be83152e337949723e909be1b  HW/PCB/demo_mainboard.kicad_pro
```

★**但落表器的 11 条自测里, ★没有一条判据检查「行号有没有漂」★** ⇒ 下面这条是 hw-lead 自己登记的 (★`state/fragments/hw.yaml` · need key `iss230_row_shift_false_green` · since 2026-11-16★):

> ★「落表那趟必带: 行号漂移会造假绿 —— V-2 落表后有 4 条锚点 (`d11_led508_board` / `d11_led509_board` / `d2_b307_dnp` / `d2_b309_dnp`) 换了行照样绿, ★**门禁不会提醒**★ ⇒ 必须把整组行号逐条改对, ★**不能只看门禁红不红**★; 新行号见作业包 §3.1 的 A 表」★

★**另一条已实测的量 (ISS-249 交卷单 §B4)**: 「内容撞车 0 / ★**行号漂移撞车 1 处 (V-3 删 `DEMO_DNP` 3 行 ⇒ F1 行号 -3)**★ / md5 撞车 4 处 ⇒ ★**必须同批落**★」

★**⇒ 合起来的后果 (★main 推演, 你要机器把它堵住★)**:
老板拍 A1/A2/A3 ⇒ 一次 `--apply` 落 V-3 13 条 + V-4 1 条 ⇒ ★**V-3 会删 3 行 DNP ⇒ 网表/脚表所有行号锚点整体 -3**★ ⇒ ★**而门禁只查「内容对不对」和「md5 对不对」, 不查「行号还对不对」⇒ 假绿**★ ⇒ ★**下一个按行号改东西的人 (人或 agent) 会改错行, 而且门禁不会喊**★

---

## ③ 任务 (四件, 全部机器可判)

### ★① 加「行号锚点断言」(★本单主体★)
★**建议落点 (二选一, 你自己定, 但必须是机器可判 + 有 `--selftest`★)**:
- ★**方案 A (推荐)**: 写在 `state/land_v_values.py` 里 (落表器自带) ⇒ ★**落表后自动复核 (不用人记得跑)** ★
- ★**方案 B**: 新建独立门禁 `HW/check_land_row_anchors.py` ⇒ ★**落表前后各跑一次, 但靠人记得跑 (弱一档)** ★

★**判据要求 (三条, 一条不许少)**:
1. ★**落表前**: 对每个被门禁按行号引用的锚点, 记录 (文件, 行号, 该行内容指纹) ⇒ ★**清单来源必须机器可枚举, 不许手抄** ★
   (★候选锚点: `d11_led508_board` / `d11_led509_board` / `d2_b307_dnp` / `d2_b309_dnp` / F1 两行 (`state/gen_netlist.py` L381 / L393) / ★**以及 `HW/check_pin_function_labels.py` 的 `PROTECTED_MD5` + `KNOWN_DEFECTS` 快照 (L127 / L143) / `HW/check_netlist_selfconsistency.py` / `state/check_netlist.py` 里以行号引用的全部条目**★)
2. ★**落表后**: 逐条复核 ⇒ ★**三种情形分开判, 不许合并成一句「通过」★**:
   - ★**行号没变 + 内容没变** ⇒ ✅ 通过
   - ★**行号变了 + 内容没变 (纯漂移)** ⇒ ⚠️ **必须报出来** (★打印「N 条锚点行号漂移, 新行号 = …, 已自动更新锚点」★) ⇒ ★**不许静默** ★
   - ★**行号变了 + 内容也变了** ⇒ ❌ **红** (★内容被改 = 真缺陷, 落表器不许悄悄改内容★)
3. ★**落表后锚点更新必须是机器写的** ⇒ ★**不许人手改行号** ★

### ★② `--selftest` 反向用例 (★本项目所有闸都有, 这一条不许省★)
★**至少 4 条**:
- 人为让某锚点行号漂移 (行号变 / 内容不变) ⇒ ★**必须被报出来 (rc≠0 或明确告警行)** ★
- 人为让某锚点内容变 (行号不变) ⇒ ★**必须红** ★
- 人为让某锚点行号+内容都变 ⇒ ★**必须红** ★
- ★**「一条都没漂」的正向用例 ⇒ 必须绿** ★
★**自测全程真盘零写入 (走临时副本)**, ★**跑完 5 个受保护 md5 必须逐字节不变** ★

### ★③ 出【V-3 + V-4 落表批次的同批落表次序 + 重基线清单】
★**一页纸, 落进 `HW/SCHEMATIC_LANDING_NEXT_BATCH_V1.md` (★已存在 ⇒ 只追加, 老字不删★)** ⇒ **必须含**:
- ★**哪些条目必须同批落** (★依据: md5 撞车 4 处 + 行号漂移 1 处 (V-3 删 3 行 DNP ⇒ F1 行号 -3)★) ⇒ ★**逐条列出, 带撞车类型** ★
- ★**落表顺序** (★谁先谁后: 真源改哪几个生成器 → 按什么硬顺序重生成 6 件★) ⇒ ★**参照 ISS-243/ISS-249/ISS-257 的既有硬顺序, 不许自创一套** ★
- ★**落表后要重基线的完整清单 (谁负责哪一跳)**: ★网表/脚表 md5 台账 (`HW/SCHEMATIC_LANDING_V1_LANDED.md` §18.4) · ★`SW/SW_MD5_BASELINE_LEDGER.md` §1 (sw-lead) · ★`MECH/HW_CROSS_REVIEW_TRIAGE.md` §1 (mech-lead) · ★4 个受保护脚本的 `MD5_EXPECTED` 字典 · ★BOM** ★
- ★**板那一趟 (PCB 类) 明确写「排队, 不在本单」** ★

### ★④ 交卷物 (5 件, 路径一字不差)**
1. ★**落表器/新门禁的改动** (★含 `--selftest`★)
2. ★**`HW/SCHEMATIC_LANDING_NEXT_BATCH_V1.md` 追加的那一页 (同批落表清单)**
3. ★**交卷单**: `HANDOFF/2026-11-17_hw-lead_ISS262_落表行号锚点兜底与同批落表清单.md` (★B1~B6 六块齐全, 标题要含 gate_check 认的语义关键词★)
4. ★**分片**: `state/fragments/hw.yaml` (★只走 `python3 state/frag_write.py --agent hw-lead` 原子写★)
5. ★**验收原始日志** (★rc 原样贴进交卷单, 零转录误差★)

---

## ④ 验收 (★全部本机实跑, 原样输出★)

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

★**反向自证 (必做)**: ★**沙盒里让一条锚点行号漂移 ⇒ 门禁必须抓到 ⇒ 装回 ⇒ 又绿** ★

---

## ⑤ 边界 (★违反即交卷无效★)

- ★**零落表**: V-2 / V-3 / V-4 ★**一条都不许落** (★老板还没拍 ⇒ 网表/脚表/BOM 逐字节不许变★)
- ★**零外发** (★一次邮件都不许发·不许联系供应商★) · 零采购 · 零下单
- ★**不碰 PCB 布线 / 布局 / 板框 / 板文件** (★板 `611b869e…` 与 `.kicad_pro` `3e504d2b…` 必须逐字节不变★)
- ★**不碰 `SW/` / `MECH/` / 别人的分片** (★只读跑它们的门禁取证据可以★)
- ★**不改判据阈值 / 不删反向用例 / 不加「跳过 md5」默认值**
- ★**不替老板拍板** (★A1/A2/A3/A4/A5 一条都不许代拍★)
- ★**不自签 `state/issue_log.yaml`** (★verify 留给 main★)
- ★**不改 `PROJECT_TRACKER.md` §0 锁死表**

---

## ⑥ 给 main 的 (★两条要写进交卷单, 老板要看★)

1. ★**「老板拍完 A1+A2+A3 ⇒ 一条命令 ⇒ 落多少条」这个数字必须订正**: ★**ISS-260 实测 = 网表侧 14 条 (V-3 13 + V-4 1) + 4 条等板那一趟 (R4×2 + R9 + R3)** ★ ⇒ ★**决策页 §A-补7 现在写的「15 条一次落」是错的 (main 会在本轮改)** ★ ⇒ ★**你本单不碰决策页, 但把实测数字写进交卷单给 main 用** ★
2. ★**W-1 (USB D− 的 ESD 方案) 的三个小问 (W-1a 架构+型号 / W-1b D− 侧怎么办 / W-1c 型号与证据等级) + 三选项代价, 由 ISS-260 §B4 出, main 要转进决策页** ⇒ ★**你本单如果从落表器侧发现 W-1b 第四条路 (新增位号 `D_ESD_USB_N`) 的配方缺口, 一并报给 main** ★
