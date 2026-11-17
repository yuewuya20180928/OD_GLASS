# ISS-297 · hw-lead · cont2 续做说明 (★2026-11-17 20:1x · cron `fb67af40` 重派僵尸 fixing★)

★**权威任务书全文** = `state/issue_log.yaml` 里 `ISS-297` 的 `task_brief` 字段 (★含原任务书 + ⑭ 节 + ⑮ 节★)
★**上一趟续做任务书** = `state/dispatch_briefs/ISS-297_hw_legal_reboard_channel_cont1.md`
★**本文件 = ⑯ 节 (本轮重派说明) + ⑮ 节 (main 20:0x 写的现状交接) 全文★**

# ★★⑯ · ISS-297 cont2 续做说明 (★2026-11-17 20:1x 由 main (moli) · cron `fb67af40` 本轮追加★)

> ★**本段 = 本轮 (cron `fb67af40` · 队列自动派活) 接手 ⑮ 节里说的「僵尸 fixing 重派」** ★
> ★**上一趟 cont1 会话**: `agent:hw-lead:subagent:76f08dd2` (sessionId `66d81b9f`) · 19:28:57 → **19:37:08** · runtime 485s · **status=timeout / abortedLastRun=true** ⇒ ★**死在「改第 2 道闸」中途** ★
> ★**⇒ 本 job (cron `fb67af40`) = ⑮ 节里说的【僵尸 fixing 的唯一重派方】⇒ 本轮已重派 = cont2 续做 (★不是从零重做★)★**

## ★★⑯-1 · 盘面实况 (★main 20:1x 本机实跑, 不抄任何交卷报告★)

| 件 | 现状 (★本机实读★) |
|---|---|
| ★**交卷单** ★ | ★**`HANDOFF/2026-11-17_hw-lead_ISS297_合法改板通道.md` = 骨架 1,147 B (mtime 19:29)** ★ ⇒ ★**直接往里填 B0~B6, 别重建** ★ |
| ★**共用判决库** ★ | ★**`HW/board_reboard.py` = 35,661 B (mtime 18:42)** ★ ⇒ ★**已在盘, 6 道闸接通道时直接用它 (★别自己再写一份 reboard 逻辑★)★ |
| ★**第 1 道闸** ★ | ★**`HW/check_fsin_rootcause.py` mtime 19:31:46 · md5 `a8fcc75faf…`** ★ ⇒ ★**cont1 改过它 (★自己实跑 `python3 HW/check_fsin_rootcause.py; echo rc=$?` 确认现状, 别照抄假设★)★ |
| ★**第 2 道闸** ★ | ★**`HW/check_g1a7_selection_landed.py` mtime 19:33:12 · md5 `1791d1d970…`** ★ ⇒ ★**★cont1 改到一半就死了 ⇒ 这是本趟最可能「改了一半」的一处 ⇒ 先实跑 + 看 diff, 续着改, 别从头重写★** ★ |
| ★**第 3~6 道闸** ★ | ★**`HW/check_onepass_commit_order.py` (12:46) · `HW/check_onepass_preflight_coverage.py` (13:20) · `HW/check_pin_function_labels.py` (04:56) · `HW/check_workpack_state_values.py` (15:02)** ★ ⇒ ★**mtime 全在 cont1 之前 ⇒ 还没被碰过** ★ |
| ★**分片** ★ | ★**`grep -c iss297 state/fragments/hw.yaml` = 0** ★ ⇒ ★**本趟必须写 (★走 `state/frag_write.py --agent hw-lead` 原子写★)★ |
| ★**受保护 5 件** ★ | ★**板 `611b869e13518c3c023fb178f91a0075` (mtime 仍 `2026-11-06 07:07:17.362193413`) · `.kicad_pro` `3e504d2be83152e337949723e909be1b` · 网表 `37f62ac3f0b81d92ca7d48fdea717f07` · 脚表 `a4270120454aedf7a23c92cd8985c8a6` · BOM `5d02bece9477ffce5fbe0193c7d5cce4`** ★ ⇒ ★**必须逐字节不变 (★本单零写板·零落表★)★** |

## ★★⑯-2 · 本趟只做 4 件 (★与 ⑭-2 节完全一致, 不许换顺序★)

1. ★**修那 2 条过期 fixture** (`HW/check_fsin_rootcause.py --selftest` ⇒ 23/25 ⇒ 目标 25/25) ⇒ ★**不许删用例来凑绿** ★
2. ★**把 5 道闸接到通道上** (★第 2 道闸可能改了一半 ⇒ 先查后改★) ⇒ ★**判据方向不许变 + fail-closed 三条一条不许动 + `reboard: null` 仍按纯 md5 硬保护判** ★
3. ★**每道闸 ≥4 条反向用例 (★沙盒跑, 真盘零写★)** ⇒ ★**照 `HW/board_reboard.py` 里 `CASES` 那 10 条的形状★** ★
4. ★**交卷单 (★往 1,147 B 骨架里填 B0~B6★) + 分片 (★`grep -c iss297` ≥ 4★)** ★

## ★★⑯-3 · 必跑 (★全部本机实跑, 贴现场 rc★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 HW/check_fsin_rootcause.py ; echo "rc=$?"
python3 HW/check_g1a7_selection_landed.py ; echo "rc=$?"
python3 HW/check_onepass_commit_order.py ; echo "rc=$?"
python3 HW/check_onepass_preflight_coverage.py ; echo "rc=$?"
python3 HW/check_pin_function_labels.py ; echo "rc=$?"
python3 HW/check_workpack_state_values.py ; echo "rc=$?"
python3 state/merge.py ; echo "rc=$?"
python3 state/gate_check.py ; echo "rc=$?"
python3 state/issue_check.py ; echo "rc=$?"
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro \
       HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
```

## ★★⑯-4 · 边界 (★与 ⑭-4 节完全一致, 一条不许松★)

★**零写板** · ★**零落表** · ★**不许改 `HW/SCHEMATIC_LANDING_V1_LANDED.md` 台账本体 (★只读★)** ★ · ★**不许动 `SW/` 与 `MECH/` 的任何文件和分片** (★SW 侧那道闸归 ISS-298·MECH 侧两道闸归 ISS-296★) ★ · ★**不许放宽 fail-closed 三条** · ★**不许为了让闸变绿去改台账里那两个 `md5:` 基线** (★那是「挖坑」, 正是 ISS-284/273 堵死的洞★) ★ · ★**不许把 `HW/check_pin_function_labels.py` 那 18 条既有缺陷顺手修掉** ★ · ★零外发 · ★**不替老板拍板** · ★**不自签 issue_log** · ★**只写自己的分片** · ★**实物 `[实测]` = 0 条** ★

## ★★⑯-5 · 死因纪律 (★cont1 就是栽在这里★)

★**每条 `exec` ≤ 60 秒** · ★**长任务一律 `nohup ... > logs/iss297/x.log 2>&1 &` + 短轮询** (★前台长 exec = 被掐的头号原因★) · ★**每 10 分钟至少一次写盘** · ★**每落一件交付物就把 rc 追加进交卷单** · ★**交卷单第一件事就是 `write` 补骨架 (★已有 1,147 B 骨架, 直接填★)** · ★**分片写完 `grep` 校验** · ★**不许把整份大文件读进来** (★只 grep 你要改的那几行★)

────────────────────────────────────────

★★⑮ 续做说明 (★2026-11-17 20:0x main 实跑查盘·★上一趟 19:37:08 timeout 死掉★★)

★**★派活权归兄弟队列 job (★cron `fb67af40` ★★它是【僵尸 fixing 的唯一重派方】★★) ⇒ ★**本 job 不抢派, 只把【盘上现状】交给它★★**

★**★上一趟 (cont1) 死于模型侧 timeout ⇒ 交卷单只有骨架 ⇒ ★**但活的产物可能已在盘上, 请先查盘再决定要不要重做★★**
★**★main 20:0x 实查盘 (★自己跑的, 不抄任何交卷报告★)★**:
| 项 | 状态 |
|---|---|
| ★**交卷单** ★ | ★**骨架 (★1,147 B·★待 main 20:0x 查盘时确认)★** ⇒ ★**直接往里填 B1~B6, 别重建** ★ |
| ★**该域 6 道闸的通道改动** ★ | ★**★请自己查: `HW/check_fsin_rootcause.py` · `HW/check_g1a7_selection_landed.py` · `HW/check_onepass_commit_order.py` · `HW/check_onepass_preflight_coverage.py` · `HW/check_pin_function_labels.py` · `HW/check_workpack_state_values.py`★** ⇒ ★**★凡是已经改到一半的, ★★续着改, 不要从头重写★ ★ |
| ★**通道形状 (★不许自创★)** ★ | ★**ISS-284 的 `reboard` 原子映射 {by, file, prev_md5, md5}** ⇒ ★**四项缺一 ⇒ 整条记录无效 ⇒ 红** ★ ⇒ ★**判据方向不许变 (盘上 ≠ 链头 ⇒ 红) + fail-closed 三条 (链头不唯一 / 链断 / 链头无单号 ⇒ 红) 一条不许动** ★ |
| ★**全仓清单 (★机器生成, 可复核★)** ★ | ★**`state/board_md5_pinned_gates.md`** ★ (+ JSON · 生成脚本 `state/_gen_board_md5_pinned_gates.py`) ⇒ ★**★本单是这 9 道里的 6 道 (HW 侧)★** ★ |
| ★**★已跑通的先例 (★不是猜的★)** ★ | ★**`SW/tools/check_demo_panel_spec.py` 在 ISS-284 转成台账口径后不再硬钉板 md5 ⇒ 全仓清单里根本找不到它** ★ ⇒ ★**⇒ 「不硬钉」不是靠删断言, 是靠判决源换成【落表台账 + 合法改板记录】** ★ |

★**★必跑 (★全部本机实跑, 贴现场 rc★)**:
```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 HW/check_fsin_rootcause.py ; echo "rc=$?"
python3 HW/check_g1a7_selection_landed.py ; echo "rc=$?"
python3 HW/check_onepass_commit_order.py ; echo "rc=$?"
python3 HW/check_onepass_preflight_coverage.py ; echo "rc=$?"
python3 HW/check_pin_function_labels.py ; echo "rc=$?"
python3 HW/check_workpack_state_values.py ; echo "rc=$?"
python3 state/gate_check.py ; echo "rc=$?"     # ★Q1 18/18 + ★**新挂的两个闸也要绿★**
python3 state/issue_check.py ; echo "rc=$?"
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro
# ★★板 611b869e… / .kicad_pro 3e504d2b… 一个字节不许变 (本单零写板)★★
```
★**★死因纪律 (★19:37:08 timeout★)**: ★**每条 `exec` ≤ 60 秒** · ★**长任务 `nohup` 后台 + 短轮询** · ★**每 10 分钟至少一次写盘** · ★**交卷单先建骨架再干活** ★
