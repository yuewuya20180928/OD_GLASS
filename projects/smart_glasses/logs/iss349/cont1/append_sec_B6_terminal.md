
---

# ★★B6-终检 · cont1 追加小节 (★2026-11-23 03:5x · 上一轮 abort 掐在最后一步·本节补齐★) ★

> ★**本节是追加式 · §B0~§B7 老字一字未删** ★
> ★**权威任务书**: `state/dispatch_briefs/ISS-349_hw_preflight_b33生成器回归_cont1.md` ★
> ★**上一轮 (01:4x 派) 的会话在【最后一步】被 abort 掐死 ⇒ 产物其实已落盘, 只差「分片登记 + 终检」两件 ⇒ 本节就是那两件 ★**

## B6-终检-0 · 本续单做了什么 (★三件·逐条自评★)

| # | ★任务书要求 ★ | ★本轮实际做了什么 ★ | ★判定 ★ |
|---|---|---|---|
| 1 | ★**分片登记** ★ | ★**9 条** (2 个 artifact + 1 个 answer + 5 个 interface_claim + 1 个 logs artifact + 1 条 status·另 附项 1 走 `--set-json`) ★ —— ★**全部只走 `python3 state/frag_write.py --agent hw-lead`·零 `open(p,"w")`★** ★ | ✔ **通过** |
| 2 | ★**终检补跑** (★上一轮就死在这★) ★ | ★**新闸主模式 rc=0** ★ + ★**`--selftest` 末行 `ALL TESTS PASS` rc=0** ★ + ★**页内引用路径 MISS = 0** ★ ⇒ ★**原样输出全贴在本节** ★ | ✔ **通过** |
| 3 | ★**交 main 的 3 条 (§B5/B7-4 已写·复核一遍即可) + 附项 1** ★ | ★**§B5 三条复核完毕 (见 B6-终检-6)·§B7-4 口径一字不改 (见 B6-终检-5)** ★ + ★**附项 1 已改: `q3_storage_and_audio` 的 `item` 措辞「外挂 SPI-NOR 16-64MB」→「外挂 SPI-NOR ≥128 MiB (1 Gbit) 起」·只改这一句·`to`/`due`/`since`/`waiting_on` 与其余 240 条 `needs_from` 逐字未动** ★ | ✔ **通过** |

## B6-终检-1 · ★新闸主模式 (★原样输出★)★

```
$ cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
$ export TMPDIR=/home/yuewuya/.openclaw/workspace/projects/smart_glasses/tmp/iss349/tmpdir
$ python3 HW/check_preflight_regen_idempotent.py
==================================================================================================
  ISS-349 · 「板侧项全集」页【重跑不蒸发】闸 (★C1 表/JSON 同源 · C2 重跑幂等 · C3 来源在册 · C4 必需项★)
==================================================================================================
  PROJ      = /home/yuewuya/.openclaw/workspace/projects/smart_glasses
  CHECKLIST = /home/yuewuya/.openclaw/workspace/projects/smart_glasses/HW/PCB/BOARD_ONEPASS_PREFLIGHT.md
  GEN_PROJ  = /home/yuewuya/.openclaw/workspace/projects/smart_glasses
  SANDBOX   = /home/yuewuya/.openclaw/workspace/projects/smart_glasses/tmp/iss349/regen_gate
--------------------------------------------------------------------------------------------------
  OK    C1 表/JSON 同源 (★id 集合逐个相等★)
         §2 表 33 行 (唯一 id 33) · §7 JSON 33 条 (唯一 id 33) · 集合逐一相等: ✔
  OK    C2 重跑幂等 (★真页 == 沙盒重跑输出★)
         真页 md5 = 581f116a6e41c6c7d6b9290874ade4c5 · 沙盒重跑输出 md5 = 581f116a6e41c6c7d6b9290874ade4c5 · 零行差异: ✔
  OK    C3 来源在册 (★source_iss ∈ 覆盖度闸 SOURCES★)
         33 条 item 的 source_iss 全在 SOURCES (11 个来源单) 里: ✔
  OK    C4 必需项在场 (★加严块★)
         必需项 1 个: ✔
         ✔ 必需板侧项在场: B33_PIN_LAND_1P27 (§2 表 + §7 JSON)
--------------------------------------------------------------------------------------------------
  ✅ rc=0: ★★页与生成器同源 · 重跑零差异 · 来源全在册 · 必需项在场 ★★
--- rc=0 ---
```
★**日志**: `logs/iss349/cont1/01_gate_main.log` ★

## B6-终检-2 · ★新闸自测 (★原样输出·末行 ALL TESTS PASS★)★

```
$ python3 HW/check_preflight_regen_idempotent.py --selftest
==================================================================================================
  ISS-349 · 「板侧项全集」页【重跑不蒸发】闸 (★C1 表/JSON 同源 · C2 重跑幂等 · C3 来源在册 · C4 必需项★)
==================================================================================================
  ★反向用例沙盒: /home/yuewuya/.openclaw/workspace/projects/smart_glasses/tmp/iss349/regen_gate
--------------------------------------------------------------------------------------------------
  ★反向用例 (★端到端跑真生成器★):
  PASS  正例 · 沙盒重跑 == 真页 (★零行差异·零蒸发★)
      ★生成器 rc=0 · 沙盒页 md5=581f116a6e41c6c7d6b9290874ade4c5 · 真页 md5=581f116a6e41c6c7d6b9290874ade4c5
  PASS  R1 · 生成器里删掉 B33 ⇒ 重跑 ⇒ 页回到 32 条 ⇒ 闸红并点名「B33 缺失」
      ★闸 rc 判红=True · 点名到 B33=True★
           ❌ 必需板侧项缺失: B33_PIN_LAND_1P27 (★表里没有·JSON 里也没有★) ⇒ ★**生成器里那条被删掉 / 页里那条被手改掉 ⇒ 命中这里** ★
  PASS  R2 · 真页 JSON 里 B33 的 pitch 改成假值 9.99 ⇒ 闸红 (★真页 != 重跑输出★)
      ★闸 rc 判红=True · C2 判红=True · 贴了 diff=True★
           ❌ 真页 != 沙盒重跑输出 ⇒ ★**页与生成器不同源 (重跑会改页)★** ⇒ md5 06a730fed9d7283b03d4d7db0170d055 vs 581f116a6e41c6c7d6b9290874ade4c5
  PASS  R3 · 真页 JSON 里 B33 的 source_iss 改成 ISS-999 (不在 SOURCES) ⇒ 闸红并点名
      ★闸 rc 判红=True · C3 判红=True · 点名到 B33+ISS-999=True★
           ❌ 真页 != 沙盒重跑输出 ⇒ ★**页与生成器不同源 (重跑会改页)★** ⇒ md5 170fca80ea6c3cfd516f0b0c8dbe95b6 vs 581f116a6e41c6c7d6b9290874ade4c5 / ❌ ❌ id=B33_PIN_LAND_1P27 的 source_iss='ISS-999' 不在覆盖度闸的 SOURCES 里 ⇒ 来源不明
  PASS  R4 · 沙盒里把板读结果改成 1.27 ⇒ 重跑 ⇒ 页里的现状值【自己】变成 1.27 (★不是死值★)
      ★改板 rc=0 · 生成器 rc=0 · 板读 1.27 ⇒ 页里跟上了=True★
           [实测] 板读 (bash state/pcbnew_py.sh): `J_DEBUG` = pitch 1.27 / 4 脚 / 铜箔 X 142.0625..146.1475 × Y 56.1500..57.0500 (4.0850 × 0.9000); `J_UART` = pitch 1.27 / 2 脚 / 铜箔 X 18.5025..20.0475 × Y 68.1500..69.0500 (1.5450 × 0.9000); BOM/网表写 1.27mm (`HW/BOM_v1.csv:71` = `
  PASS  恢复原件后 · 再跑一次 ⇒ 闸绿 (★不是永远红的闸★)
      ★生成器 rc=0 · 闸全绿=True★
--------------------------------------------------------------------------------------------------
  ALL TESTS PASS
--- rc=0 ---
```
★**日志**: `logs/iss349/cont1/02_gate_selftest.log` ★

## B6-终检-3 · ★页内引用路径 MISS 自检 (★任务书 §5⑤·最近三轮全栽在这条上★)★

```
$ python3 logs/iss349/cont1/path_miss_check.py --page HANDOFF/2026-11-23_hw-lead_ISS349_板侧项全集生成器回归修复.md --out logs/iss349/cont1/04_path_miss_final.txt
★ISS-349 cont1 · 交卷页引用路径 MISS 自检 (★任务书 §5⑤·最近三轮全栽在这条上★)
  被检页 = HANDOFF/2026-11-23_hw-lead_ISS349_板侧项全集生成器回归修复.md
  被检路径数 = 41
  OK   HANDOFF/2026-11-23_hw-lead_ISS349_板侧项全集生成器回归修复.md
  OK   HW/BOM_v1.csv
  OK   HW/PCB/BOARD_ONEPASS_PREFLIGHT.md
  OK   HW/PCB/BOARD_ONEPASS_WORKPACKET.md
  OK   HW/PCB/demo_mainboard.kicad_pcb
  OK   HW/SCHEMATIC_LANDING_V1_LANDED.md
  OK   HW/check_netlist_contradiction_r3.py
  OK   HW/check_onepass_preflight_coverage.py
  OK   HW/check_pin_function_labels.py
  OK   HW/check_preflight_regen_idempotent.py
  OK   HW/check_workpack_state_values.py
  OK   HW/netlist_v1.csv
  OK   HW/netlist_v1_pins.csv
  OK   logs/iss349/evidence/evaporation_repro.txt
  OK   logs/iss349/evidence/mksandbox.sh
  OK   logs/iss349/evidence/page_BEFORE_ISS343_handedit.md
  OK   logs/iss349/run_iss349.sh
  OK   logs/iss349/run_iss349_full.log
  OK   state/_iss277_build_preflight.py
  OK   state/_iss277_preflight_appendix.md
  OK   state/_iss304_ledger_fresh.py
  OK   state/_iss304_sync_state_baseline_md5.py
  OK   state/dispatch_briefs/ISS-292_hw_preflight_generator_realign_cont1.md
  OK   state/dispatch_briefs/ISS-304_hw_workpack_state_values_reanchor.md
  OK   state/dispatch_briefs/ISS-349_hw_preflight_b33生成器回归_修复.md
  OK   state/frag_write.py
  OK   state/fragments/hw.yaml
  OK   state/fragments/mech.yaml
  OK   state/fragments/pm.yaml
  OK   state/fragments/sw.yaml
  OK   state/gate_check.py
  OK   state/issue_log.yaml
  OK   state/merge.py
  OK   state/pcbnew_py.sh
  ★MISS 行数 = 0
  --- rc=0 ---
```

★**日志**: `logs/iss349/cont1/04_path_miss_final.txt` · ★**自检脚本**: `logs/iss349/cont1/path_miss_check.py` (★从交卷页正文里抽路径 token·逐个 stat 在盘★) ★

## B6-终检-4 · ★交卷前必跑 (★merge / gate_check / 既有闸 / 板指纹★)★

```
$ python3 state/merge.py
✅ STATE.yaml 已刷新 (2026-11-23T03:51:19+08:00)
   产出 746 | 阻塞 43 (高危 33) | 未闭合需求 344 | 冲突 0 | 健康度 red
--- rc=0 ---

$ python3 state/gate_check.py
==========================================================================
项目总工质量门 · 3 个子模块总工交付看板
==========================================================================

【Q1 交付齐备率】 17/18 个必填验收块齐全
   hw-lead    6/6  缺: 无   交接单: 2026-11-23_hw-lead_ISS349_板侧项全集生成器回归修复.md
   sw-lead    5/6  缺: ['B2']   交接单: 2026-11-23_sw-lead_ISS350_Q3分档口径写回SW侧.md
   mech-lead  6/6  缺: 无   交接单: 2026-11-23_mech-lead_ISS345_8脚本迁双口径.md

【Q2 证据分级率】 3/3 个总工的交付做了证据分级
   hw-lead    标签: ['实测', '推算', '0数据']

【Q3 接口声明率】 全员 interface_claims 共 1032 条 (目标 ≥3 条/总工 → 冲突才能自动检出)
   hw-lead    396 条

【Q6 硬件真源闸】 HW pinout 真源闸: ✅ 通过 (rc=0)
   全部检查项通过

【Q7 钉板 md5 闸链】 9/9 道绿 (★9 道全部 fail-closed 挂在门禁链里★)
   ✅ 钉板闸① FSIN 根因闸: rc=0
   ✅ 钉板闸② G1a-7 选型落表闸: rc=0
   ✅ 钉板闸③ 改板提交顺序闸: rc=0
   ✅ 钉板闸④ 作业包覆盖度闸: rc=0
   ✅ 钉板闸⑤ 脚表功能标签闸: rc=0
   ✅ 钉板闸⑥ 作业包现状值闸: rc=0
   ✅ 钉板闸⑦ 板框坐标闸: rc=0
   ✅ 钉板闸⑧ 结构真值闸: rc=0
   ✅ 钉板闸⑨ SW 侧合法改板通道闸: rc=0

【缺口清单】(可直接转成下一轮派活项) —— 4 条
   · hw-lead: 179 条需求确实还没人答 (等另一个总工)
   · sw-lead: 交接单缺 [B2] 验收标准自评 (逐条 通过/不通过/未验)
   · sw-lead: 92 条需求确实还没人答 (等另一个总工)
   · mech-lead: 70 条需求确实还没人答 (等另一个总工)

==========================================================================
--- rc=0 ---
```

### ★★Q1 = 17/18 (★不是 18/18·但★**缺的不是本单**★)★★

★**缺的那 1 格 = `sw-lead` 的 `B2` ⇒ 与本单零关系** ★

| 项 | ★本机实读事实 ★ |
|---|---|
| ★**谁缺** ★ | `sw-lead` 5/6 (缺 `B2` = 「验收标准自评 (逐条 通过/不通过/未验)」) · ★**hw-lead 6/6 · 缺: 无** ★ |
| ★**缺在哪个文件** ★ | `HANDOFF/2026-11-23_sw-lead_ISS350_Q3分档口径写回SW侧.md` (★**1,203 B · mtime 2026-11-23 03:47**★) ⇒ ★**那是 main 在 03:47 预落的骨架** (★文件首行自述: 「★**骨架已由 main 预落·防中途死掉·内容由 sw-lead 填★」★) ★ |
| ★**为什么判缺** ★ | `state/gate_check.py:49` 的 B2 关键词表 = `["验收标准自评", "自评", "验收标准"]` ⇒ ★该骨架的 B2 标题写的是「## B2 改后措辞 (★3 条逐条对照 + 依据★)」·**三个关键词一个都不含** ⇒ 判缺 ★ |
| ★**为什么不回退** ★ | `state/gate_check.py:87` `pick_handoff()` 的规则 ③ (★2026-11-18 main 加的★): ★**自称 B 块结构 ⇒ 缺块就是【倒退】⇒ 不许回退到 7 天内齐备的老单来顶住齐备率** ★ ⇒ ★**这是闸的设计意图·不是 bug** ★ |
| ★**本单为什么不修** ★ | ★**`HANDOFF/` 下 sw-lead 的交接页不是本单的地界** ★ (★任务书 §2 边界: 「只写本单允许的文件·不碰别人的」★) ⇒ ★**本单一个字都没碰 sw-lead 的页** ★ ⇒ ★**这一格要 sw-lead 自己把 B2 填出来** ★ |

★**给 main 的一句话**: ★**Q1 从 18/18 掉到 17/18 的时刻 = 03:47 (main 预落 sw-lead ISS-350 骨架那一分钟)·不是本单造成的 (本单只写 hw.yaml + 本页 + logs/iss349/)·hw-lead 那一格 6/6 缺: 无 ⇒ 等 sw-lead 把 ISS-350 的 B2 填了就会回 18/18** ★

★**日志**: `logs/iss349/cont1/07_merge_gate_check.log` ★

### ★既有闸不许被本单弄红 (★本单一个字未改它们★)★

```
$ python3 HW/check_onepass_preflight_coverage.py
  OK   P1 / P2 / P3 / P4 / P5 / P6
     ✔ 作业包 §0.2 ③ 的 ③ ⇒ 命中 ['B33_PIN_LAND_1P27'] (覆盖令牌 4 个全在)
     ✔ 受保护 5 件 md5 逐字节不变: ✔
  ✅ rc=0: ★★板侧项全集与作业包对齐, 现状值与盘面一致 ★★
--- rc=0 ---

$ python3 HW/check_workpack_state_values.py
  ✅ rc=0: ★★两份文档里的现状值 == 盘面实测, 且七类判据齐 ★★
--- rc=0 ---
```

### ★板指纹 + 受保护 5 件 (★零写板 · 零落表 ★)★

```
$ md5sum HW/PCB/demo_mainboard.kicad_pcb ; stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb
611b869e13518c3c023fb178f91a0075  HW/PCB/demo_mainboard.kicad_pcb
2026-11-06 07:07:17.362193413 +0800 4940213

$ md5sum HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv HW/PCB/demo_mainboard.kicad_pcb
6aee500e60ba0732f83a9cf557ba90ab  HW/netlist_v1.csv
9174309df1ec9411ac8e8d9e80ee386a  HW/netlist_v1_pins.csv
5b9993992405904a60ac96a020b375d8  HW/BOM_v1.csv
611b869e13518c3c023fb178f91a0075  HW/PCB/demo_mainboard.kicad_pcb
```
★**板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` ⇒ 与 2026-11-23 01:4x 那一轮开工前逐字节相同 ⇒ 零写板** ★
★**日志**: `logs/iss349/cont1/09_existing_gates_and_md5.log` ★

## B6-终检-5 · ★§B7-4 交接口径复核 (★一字不改·原样转述给 main★)★

★**§B7-4 原文 (★本轮只复核·一字未改★)**:

> ★**板那一趟开工之后, 生成器 (`state/_iss277_build_preflight.py`) / 新闸 (`HW/check_preflight_regen_idempotent.py`) / 清单页 (`HW/PCB/BOARD_ONEPASS_PREFLIGHT.md`) 这三件在本单之后不许再改** ★
> ⇒ ★**板那一趟期间它们给出的读数才有效** ★ ⇒ ★**板改完之后: 跑一次生成器 (让现状值自己变成 1.27) + 跑一次新闸 (C2 应当仍绿) + 跑一次覆盖度闸 (P4 应当仍绿·见 §B5-1★)** ★

★**本轮复核结论**: ★**该口径本轮一字未改·且本轮已经把它写进 `state/fragments/hw.yaml` 的 interface_claim `iss349_preflight_regen_idempotent` 的 `note` 里 ⇒ merge 之后 main / SW / MECH 三侧都能在 STATE.yaml 里读到这条「判据冻结」口径 (★上一轮它只存在于本页正文·merge 读不到·这正是本续单存在的理由★)** ★

## B6-终检-6 · ★§B5 三条复核 (★给 main 的提示·不是本单的未完成项★)★

| # | §B5 原文要点 | ★本轮复核 (★本机实读★) ★ | ★本轮处置 ★ |
|---|---|---|---|
| 1 | ★**覆盖度闸 P4 的覆盖令牌 `0.50`** 是前向风险 ⇒ 已做成「从 main 裁决原文现读」⇒ 令牌不会消失 ★ | ★**本轮实跑覆盖度闸 P4: `✔ 作业包 §0.2 ③ 的 ③ ⇒ 命中 ['B33_PIN_LAND_1P27'] (覆盖令牌 4 个全在)` ⇒ 令牌现值仍在** ★ | ★**不用动** ★ · ★板那一趟跑完、重跑生成器之后 main 亲自核一眼 P4 仍绿 (★`python3 -B HW/check_onepass_preflight_coverage.py`★) ★ |
| 2 | ★**新闸 C4 的 `REQUIRED_ITEMS` 是写死的** ⇒ 以后再加板侧项必须同一单里往里加一行 + 跑 `--selftest` ★ | ★**本轮实读 `HW/check_preflight_regen_idempotent.py:65` ⇒ `REQUIRED_ITEMS = ("B33_PIN_LAND_1P27",)` (★1 项·与 §B7-4 的冻结口径一致·本轮未改★)** ★ | ★**走加严流程** ★ |
| 3 | ★**生成器多了一条对 `state/fragments/pm.yaml` 的读** (★fail-soft·读不到就降级并打 ⚠·不让生成器拒写页★) ★ | ★**本轮实跑生成器 rc=0 + 新闸 C3 `33 条 item 的 source_iss 全在 SOURCES (11 个来源单) 里: ✔` ⇒ 降级路径当前【未被触发】** ★ | ★**若 main 以后改了 pm.yaml 那一句 ⇒ 生成器降级 ⇒ 覆盖度闸 P4 的 `0.50` 令牌就靠不住了 ⇒ 那时 main 要同步改覆盖度闸的令牌口径 (★那是覆盖度闸的地界·本单不许动★)** ★ |

★**★§B5 三条本轮全部复核完毕 · 本单无阻塞项 · 不依赖老板拍板 · 零外发 ★★**

## B6-终检-7 · ★分片登记明细 (★9 条 + 附项 1★)★

★**写入通道**: ★**只有 `python3 state/frag_write.py --agent hw-lead` (★零 `open(p,"w")` 手写 YAML★)** ★

| # | 类别 | ★key / path ★ | ★落点 ★ |
|---|---|---|---|
| 1 | artifact | `HANDOFF/2026-11-23_hw-lead_ISS349_板侧项全集生成器回归修复.md` (kind=handoff · v1.0) | `state/fragments/hw.yaml` → `artifacts` |
| 2 | artifact | `HW/check_preflight_regen_idempotent.py` (kind=gate · v1.0) | `state/fragments/hw.yaml` → `artifacts` |
| 3 | artifact | `logs/iss349/` (kind=log · v1.0) | `state/fragments/hw.yaml` → `artifacts` |
| 4 | answer | `iss349_preflight_b33_generator_fixed` → `to=main` | `state/fragments/hw.yaml` → `answers` |
| 5 | claim | `iss349_preflight_regen_idempotent` (★判据冻结口径★) | `state/fragments/hw.yaml` → `interface_claims` |
| 6 | claim | `preflight_regen_gate_rc` = `0 = 全过 · 1 = 闸红 · 2 = 用法错 · 3 = 闸崩` | `state/fragments/hw.yaml` → `interface_claims` |
| 7 | claim | `preflight_item_b33_pin_land_pitch` (板读 0.50 ⇒ BOM/网表 1.27 ⇒ Δ 0.77) | `state/fragments/hw.yaml` → `interface_claims` |
| 8 | claim | `preflight_item_b33_source_iss` = `ISS-290` | `state/fragments/hw.yaml` → `interface_claims` |
| 9 | claim | `preflight_regen_gate_env` (4 个 env) | `state/fragments/hw.yaml` → `interface_claims` |
| + | status | `phase=iss349-delivered` · `progress_pct=100` · `health=green` | `state/fragments/hw.yaml` → `status` |

★**★零重复 key 自证 (★本轮实跑★)★**: ★`iss349` 在改前命中 = 0 ★ ⇒ ★**6 个 key 各命中恰好 1 次** ★ (★`iss349_preflight_b33_generator_fixed`=1 · `iss349_preflight_regen_idempotent`=1 · `preflight_regen_gate_rc`=1 · `preflight_item_b33_pin_land_pitch`=1 · `preflight_item_b33_source_iss`=1 · `preflight_regen_gate_env`=1★) ★ ⇒ ★**没有新建第二条** ★

★**日志**: `logs/iss349/cont1/03_frag_write.log` · ★**登记脚本 (★可复现★)**: `logs/iss349/cont1/frag_write_iss349.sh` ★

## B6-终检-8 · ★附项 1 · `q3_storage_and_audio` 容量口径订正 (★同一分片·零写板★)★

### ★改了什么 (★只改这一句措辞★)★

| 项 | ★改前 ★ | ★改后 ★ |
|---|---|---|
| `item` | `Q3 模型/rootfs 怎么存(只ADB push是否接受外挂 SPI-NOR 16-64MB, 板宽12->15mm) + 音频到底做不做(tracker全文无音频条目, 我不擅自加也不擅自排除)` | `Q3 模型/rootfs 怎么存(只ADB push是否接受外挂 SPI-NOR ≥128 MiB (1 Gbit) 起, 板宽12->15mm) + 音频到底做不做(tracker全文无音频条目, 我不擅自加也不擅自排除)` |

### ★没改什么 (★本机实跑自证·逐字对照★)★

★**`needs_from` 241 条 ⇒ 改前 241 / 改后 241 (不增不减) · 逐条 diff = 只有 index 5 (`q3_storage_and_audio`) 的 `item` 一个字段变了** ★

```
[OK] needs_from 条目数 = 241 (改前 241 · 不增不减)
[OK] 目标条目 index = 5 · key = q3_storage_and_audio
[OK] 改动字段 = ['item'] (只有 item)
[OK] item 改前 = Q3 模型/rootfs 怎么存(只ADB push是否接受外挂 SPI-NOR 16-64MB, 板宽12->15mm) + 音频到底做不做(tracker全文无音频条目, 我不擅自加也不擅自排除)
[OK] item 改后 = Q3 模型/rootfs 怎么存(只ADB push是否接受外挂 SPI-NOR ≥128 MiB (1 Gbit) 起, 板宽12->15mm) + 音频到底做不做(tracker全文无音频条目, 我不擅自加也不擅自排除)
[OK] 字段 key         = 'q3_storage_and_audio' (逐字未动)
[OK] 字段 to          = 'boss' (逐字未动)
[OK] 字段 due         = '2026-10-27' (逐字未动)
[OK] 字段 since       = '2026-10-25' (逐字未动)
[OK] 字段 waiting_on  = 'boss' (逐字未动)
```

★**写入通道**: ★**`python3 state/frag_write.py --agent hw-lead --set-json logs/iss349/cont1/needs_from_after.json --set-field needs_from`** (★原子替换整段 `needs_from`·中间件由 `logs/iss349/cont1/q3_item_fix_prep.py` 生成并自检过「只有 item 变」★) ★
★**改前快照 (★可回滚★)**: `logs/iss349/cont1/hw.yaml.before_setjson` (★md5 `8ed849e3f7ee165f4db5ae64231d1917`★) ★
★**日志**: `logs/iss349/cont1/05_q3_item_fix_prep.log` · `logs/iss349/cont1/06_q3_item_fix_setjson.log` ★

### ★依据 (★证据分级标齐★)★

| ★依据 ★ | ★证据等级 ★ | ★出处 (★本机实读★) ★ |
|---|---|---|
| ★**flash ≥128MB 是 SW 总工在 ISS-080 锁死的硬约束** (★`rootfs ≤30MB` ⇒ 64MB SPI-NOR 装不下★) ★ | `[实测]` (★仓内既有台账逐字★) ★ | `HW/SCHEMATIC_V1.md:282` · `HW/SCHEMATIC_V1_1_CHANGELOG.md` C10 · `HW/SOC_PIN_BUDGET.md:71` (★「若外挂 → sw-lead §4.1 分区表要 ≥128MB SPI-NOR (64MB 实测 FAIL)」★) ★ |
| ★**Winbond 料号里的数字是 Mbit 不是 MB** ⇒ `W25Q64` = 64 Mbit = **8 MB** · `W25Q256` = 256 Mbit = **32 MB** ⇒ 老板拍板页现写的「16~64 MB」在【容量维度】和【料号维度】两层都错 ★ | `[官网]` (★料号密度线 8Mb~2Gb·W25Q256JV = 256 Mbit / 32 MB·V 2.7~3.6 V·与 `VDD_3V3_IO` 匹配★) ★ | `HANDOFF/2026-11-23_sw-lead_ISS346_存储容量矩阵与板侧时点.md:165`~`:166` ★ |
| ★**ISS-346 机器判决: 5×4 容量矩阵 20/20 格跑通** ⇒ 64MB NOR 整列作废 (★rootfs 20/30/40/64 MB 四档全 FAIL★) ⇒ ≥128 MiB 起 | `[实测]` (★`flash_layout_check.py` 原始输出★) ★ | `HANDOFF/2026-11-23_sw-lead_ISS346_存储容量矩阵与板侧时点.md` §B2-1/§B2-2 (★矩阵脚本 `SW/tools/gen_storage_capacity_matrix.py`★) ★ |
| ★**ISS-346 原文就点名要订正这一行** ⇒ 「★**顺带订正同一行的容量口径** ⇒ 现写「外挂 SPI-NOR 16~64 MB」⇒ 建议改为「**≥128 MiB (1 Gbit) 起的 SPI-NOR**」」 ★ | `[实测]` (★逐字★) ★ | `HANDOFF/2026-11-23_sw-lead_ISS346_存储容量矩阵与板侧时点.md:340` ★ |

★**★这一句是【老板拍板页 §① 第 6 行】的口径来源 ⇒ 不改 ⇒ 老板看到的题面是错的 ⇒ 本单必须改** ★
★**★本单不替老板拍板**: ★**只把「容量下限」从错值订正成 ISS-080 已锁死的值 (★128MB 那道门槛早就有 SW 总工签过字★)·§B5 那条 `> 64 MiB ⇒ 必须 eMMC` 的口径冲突带 (★ISS-346 §B2-2 点名的「需总工/老板裁决」★) ★**本单一个字都没碰、也没替老板裁** ★** ★

## B6-终检-9 · ★本轮零写板 / 零落表 / 零改闸 / 零外发 自证 (★cont1 增量部分★)★

| ★不许做 ★ | ★自证 (★cont1 增量★) ★ |
|---|---|
| ★**写板 / 改板 / 重跑布线** ★ | ★**板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` ⇒ 与 01:4x 开工前逐字节相同** ★ (★本轮只在 `tmp/iss349/regen_gate/` 沙盒里跑过 R4 的改板★) ★ |
| ★**改网表 / 脚表 / BOM / 原理图 / `.kicad_pro`** ★ | ★**受保护 5 件 md5 逐字节不变 (★覆盖度闸 P6 + 现状值闸 V6 两道闸实跑确认✔★)** ★ |
| ★**手改 `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md`** ★ | ★**本轮对它的写 = 0 次** ★ (★只有新闸在沙盒里生成副本·真页 md5 `581f116a6e41c6c7d6b9290874ade4c5` 全程未变★) ★ |
| ★**改既有闸的判定逻辑** ★ | ★**`HW/check_onepass_preflight_coverage.py` / `HW/check_workpack_state_values.py` / `state/gate_check.py` 一个字节未改** ★ |
| ★**写别人的分片** ★ | ★**只写 `state/fragments/hw.yaml`** ★ (★`pm.yaml` / `mech.yaml` / `sw.yaml` / `issue_log.yaml` 只读未写★) ★ |
| ★**改 `state/issue_log.yaml`** ★ | ★**未改** ★ (★签收是 main 的活★) ★ |
| ★**外发任何邮件 / 询价 / 问询 / 采购** ★ | ★**本轮零外部动作·零外发** ★ ⇒ ★缺口全部【自己网上查/仓内实读】+ 标证据等级 (★附项 1 的三条依据全部是仓内逐字台账 + sw-lead 交卷页 + 官网料号口径·没有一条靠印象★) ★ |
| ★**替老板拍板** ★ | ★**本轮新增老板拍板项 = 0** ★ (★附项 1 只是把已锁死的容量下限写对·不是新决策★) ★ |
| ★**不许替 main 签字 (`status` 改 `verified`)** ★ | ★**本轮只把 `status.phase` 写成 `iss349-delivered`·`verified` 没碰** ★ |
| ★**沙盒 / 日志落 `/tmp`** ★ | ★**全程 `TMPDIR=$PROJ/tmp/iss349/tmpdir`·沙盒在 `tmp/iss349/`·日志在 `logs/iss349/`·零字节落 `/tmp`** ★ |

---

★**★交卷人 = 硬件总工 (hw-lead) · 2026-11-23 03:5x · ISS-349 cont1 (续单收尾) · 本单零写板 · 零落表 · 零改既有闸判定逻辑 · 零外发 · 不代拍 ★★**
★**★上一轮 (01:4x) 的交卷页内容一字未删; 本节是追加式补齐「分片登记 + 终检」两件 ★★**
