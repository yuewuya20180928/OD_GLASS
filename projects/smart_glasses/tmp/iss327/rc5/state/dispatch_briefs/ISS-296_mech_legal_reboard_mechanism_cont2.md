# ISS-296 · mech-lead · cont2 续做说明 (★2026-11-17 20:5x · cron `fb67af40` 重派僵尸 fixing★)

★**权威任务书全文** = `state/issue_log.yaml` 里 `ISS-296` 的 `task_brief` 字段 (★含原任务书 + ⑬ 节 + ⑭ 节 + 本 ⑮ 节★)
★**上一趟续做任务书** = `state/dispatch_briefs/ISS-296_mech_legal_reboard_mechanism.md` (★24,767 B · 20:11★)
★**本文件 = ⑮ 节 (本轮重派说明) 全文★**

# ★★⑮ · ISS-296 cont2 续做说明 (★2026-11-17 20:5x 由 main (moli) · cron `fb67af40` 本轮追加★)

> ★**上一趟子会话**: `agent:mech-lead:subagent:e8cb142c` (sessionId `5e731ce9`) · **20:12:22 → 20:31:38** · runtime 1155s · **status=timeout / abortedLastRun=true** ⇒ ★**死在【闸本体已改好、交卷单还是骨架、分片一个字没写】那一刻** ★
> ★**★死因不是它自己跑不动, 是【本 job (cron fb67af40) 的上一轮 run 整个被中断 ⇒ 两个子会话同一秒一起死 (20:31:38 · 相差 102 毫秒) ⇒ 父被杀 ⇒ 子被连带】★** ⇒ ★**所以你这一趟: ① 干活顺序 = 【先把活干完落盘】(★每件交付物落盘就追加 rc★) ② 写盘要勤 (★每 10 分钟至少一次★) ⇒ ★**这样再被打断, 活也不会丢** ★
> ★**⇒ 本 job (cron `fb67af40`) = 僵尸 fixing 的唯一重派方 ⇒ 本轮已重派 = cont2 续做 (★不是从零重做★)★**

## ★★⑮-1 · 盘面实况 (★main 20:4x~20:5x 本机实跑, 不抄任何交卷报告★)

★**★好消息: 闸本体 + 收工清单 + 同源探针【三件都已经做完了】⇒ 你这趟【只剩 paperwork】★**

| 件 | 现状 (★main 20:5x 本机实读★) |
|---|---|
| ★**闸 1** ★ | ★**`MECH/check_board_frame_coords.py` (mtime 20:20) 已接上「落表台账链头 + 合法改板通道」(C4) ⇒ `python3 MECH/check_board_frame_coords.py` = **rc=0** · `--selftest` = **rc=0** (★末行「【自检结论】✅ 一致」· ⑯a 链头不唯一⇒红 / ⑯b 链断⇒红 / ⑰ 正向对照⇒绿 三条全抓到了★)** ★ |
| ★**闸 2** ★ | ★**`MECH/check_demo_struct_truth.py` (mtime 20:25) 已接上通道 (G5b) ⇒ `python3 MECH/check_demo_struct_truth.py` = **rc=0** · `--selftest` = **rc=0** (★末行「反向用例: **28/28** 抓到了」· 含 R10 同组覆盖⇒红 / R11a 链头不唯一⇒红 / R11b 链断⇒红 / R12 正向对照⇒绿★)** ★ |
| ★**MECH 收工清单** ★ | ★**`MECH/BOARD_ONEPASS_MECH_SYNC.md` 已追加 `## ★★§ISS-296-收工清单` 一节 (mtime 20:27:45) ⇒ 含 M0 (为什么要先做) / M1 (★落表台账那一行长什么样 = 给 main 的接口格式★) / M2 (收工后同一次重锚清单 M2-1~M2-6 强制项) / M3 (★收工那天【全仓 9 道钉板 md5 的闸】都要绿★) ⇒ ★**追加式已完成, 老字一字没删 (改前副本留证 `logs/iss296/msync_before_iss296.md` 87,062 B · 20:27★)** ★ ⇒ ★**这一节不许再追加一遍, 也不许改写★** ★ |
| ★**同源探针** ★ | ★**`logs/iss296/probe_ledger_reading_same_source.py` (7,407 B · 20:27) 已在 ⇒ ★**main 20:5x 实跑 = rc=0 · 末行 `IDENTICAL: True`** ★ ⇒ ★**B1 第 ⑤ 条「同源机器证明」已达标, 不许重写★** ★ |
| ★**回归** ★ | ★**`python3 MECH/check_onepass_mech_sync.py` = rc=0 (· `--selftest` rc=0) · `python3 MECH/check_onepass_struct_crosscheck.py` = rc=0 (· `--selftest` rc=0) · `python3 state/merge.py` = rc=0 · `python3 state/gate_check.py` = rc=0 · `python3 state/issue_check.py` = rc=0** ★ ⇒ ★**B4 回归已全绿, 不许重跑出新的红★** ★ |
| ★**交卷单** ★ | ★**★还是骨架★ `HANDOFF/2026-11-17_mech-lead_ISS296_合法改板机制与收工重锚.md` = **1,197 B** (mtime 20:12:48) ⇒ 正文写着「⏳ 进行中」+「（正文待填）」⇒ ★**这是你这趟最重的一件** ★ |
| ★**分片** ★ | ★**★`grep -c iss296 state/fragments/mech.yaml` = 0 ⇒ 一条都没写★** (mtime 仍是 19:37 的 ISS-295 那趟) ⇒ ★**这趟必须写★** ★ |
| ★**受保护 5 件** ★ | ★**板 `611b869e13518c3c023fb178f91a0075` (mtime 仍 `2026-11-06 07:07:17.362193413`) · `.kicad_pro` `3e504d2be83152e337949723e909be1b` · 网表 `37f62ac3f0b8` · 脚表 `a4270120454a` · BOM `5d02bece9477`** ★ ⇒ ★**必须逐字节不变 (★本单零写板 · 零落表★)★** ★ |

## ★★⑮-2 · 本趟只做 3 件 (★闸本体不许再动★)

### ★① 填满交卷单 (★B1~B4 四块齐全 + 反向用例原样 rc + 同源探针 `IDENTICAL: True` 读数★)

★**交卷单文件路径 = `HANDOFF/2026-11-17_mech-lead_ISS296_合法改板机制与收工重锚.md`** ★
★**★原任务书 §④ 里把它写成了 `..._ISS295_...`(★那是 17:6x 改号时的笔误★) ⇒ 盘上真身是 **ISS296** 这个名字 ⇒ ★**你只填现在这个文件, 绝对不许另建一个 ISS295 名字的文件 (那会变成两份交卷单)★** ★

★**要写进去的四块 (★每一块的内容盘上都已经有了, 你【抄实测值】, 不要新编★)**:

| 块 | 该写什么 | ★**素材在哪儿 (★main 20:5x 实跑, 你复跑一遍贴现场 rc★)** ★ |
|---|---|---|
| ★**B1** ★ | ★MECH 两道闸怎么接的「合法改板」通道 (★照 SW 侧 ISS-284 那四条: ① 保护基线自证 ② 台账无变更行⇒纯 md5 硬保护 ③ 有变更行⇒链头唯一/链不断/链头有单号 + 四项原子记录逐字对上 + 基线留链尾 + 盘上==链头 ④ 同组成对覆盖★) ★ | ★`MECH/check_board_frame_coords.py` 的 `PROTECTED_LEDGER` / `check_hard_protected_legal_reboard` 一段 (★L74~L110 附近★) · `MECH/check_demo_struct_truth.py` 的 G5b 一段 (★L97~L110 附近 + 落表台账判决源 L328 起★) ★ |
| ★**B1-⑤** ★ | ★**同源机器证明** ★ | ★★`python3 logs/iss296/probe_ledger_reading_same_source.py` ⇒ rc=0 · 末行 `IDENTICAL: True` ⇒ ★**MECH 侧解析器与 SW 侧解析器对同一份台账读出的【链头 / 链 / 链头单号 / 取不准原因 / 链上出现过的 md5 / 记录集】逐字相同★** ★ |
| ★**B2** ★ | ★MECH 侧「收工后同一次重锚」强制项清单 ★ | ★**`MECH/BOARD_ONEPASS_MECH_SYNC.md` 的 `## ★★§ISS-296-收工清单` 一节 (M0/M1/M2-1~M2-6/M3) ⇒ ★**交卷单里引它 + 摘 M2 六条 + M3 那张 9 道闸表 (★M3 表里 HW 6 道那一列现在写的是「待建」⇒ ★**那 6 道在 ISS-297 已经建好了 ⇒ 你可以照盘面实况改成「已建 (ISS-297)」, 但只许改 M3 表里那 6 个单元格的文字, 不许动别的行★)★** ★ |
| ★**B3** ★ | ★**反向用例 ≥4 条** (★每条贴原样 rc + 期望红组 vs 实际红组★) ★ | ★**闸 1 `--selftest` 里的 ⑯a / ⑯b / ⑰** (★链头不唯一⇒红 / 链断⇒红 / 正向对照⇒绿★) + ★**闸 2 `--selftest` 里的 R10 / R11a / R11b / R12** (★同组覆盖⇒红 / 链头不唯一⇒红 / 链断⇒红 / 正向对照⇒绿★) ⇒ ★**原样日志在 `logs/iss296/frame_selftest.log` · `logs/iss296/struct_truth_selftest.log` (★都在盘上★)** ★ |
| ★**B4** ★ | ★**回归 + 边界自证 (★受保护 5 件 md5 + mtime 双重自证·板 mtime 仍须是 2026-11-06 07:07:17★)** ★ | ★★`python3 MECH/check_onepass_mech_sync.py` · `python3 MECH/check_onepass_struct_crosscheck.py` · `python3 state/merge.py` · `python3 state/gate_check.py` · `python3 state/issue_check.py` ⇒ 全 rc=0 · ★**加 `md5sum` 那 5 件 + `stat` 板 mtime★** ★ |

### ★② 写分片 (★走 `state/frag_write.py` 原子写, ★★禁止 `open(p,"w")`★★)

★**`grep -c iss296 state/fragments/mech.yaml` 现在 = 0 ⇒ 本趟必须写到 ≥ 4** ★

★**按 ISS-298 (★已 verified 的同批·★`state/fragments/sw.yaml` 里 `grep -c iss298` = 4★) 的形状写** ⇒ ★**`interface_claims` 至少 3 条 (★照 sw.yaml 里那三条的写法★) + 至少 1 条 `artifacts` (★交卷单 + 两个闸 + 收工清单页 + 同源探针★) + 至少 1 条 `needs_from` 给 main** ★

★**必写的 `interface_claims` 三条 (★key 请自拟但必须带 `iss296` 前缀, 便于 grep★)**:
1. ★**MECH 两道闸已接「合法改板」通道** (★判决源 = 落表台账链头 + reboard 四项原子映射 · 判据方向没变 · fail-closed 三条没动★)
2. ★**反向用例全抓到** (★闸 1 ⑯a/⑯b/⑰ + 闸 2 R10/R11a/R11b/R12 · 沙盒跑 · 真盘零写·闸 2 合计 28/28★)
3. ★**零写板 · 零落表** (★受保护 5 件 md5 逐字节不变 + 板 mtime 仍 2026-11-06 07:07:17 + 同源探针 `IDENTICAL: True`★)

★**必写的 `needs_from` (★给 main 的, ★只列事实与代价, 不替 main / 老板拍板★)**:
- ★**M3 那张 9 道闸表里 HW 6 道的状态** (★ISS-297 已建, 但【收工那天 9 道要同一次全绿】这件事要 main 写进「板只改一次」那一趟的作业包★)
- ★**M2-6 帧标 id 统一** (★`B160x100` vs `160x100-bench` vs `60x30-setA` vs `F30` ⇒ ★**本单只登记, 不代裁** ⇒ ★**这是 main → 老板 (U-274-6)★**)
- ★**M1 那两行落表台账的接口格式** (★这是给 main 在「出板那一趟」落表用的格式 ⇒ ★**台账本体不许你写★**)

★**★顺手做一件小事 (★原任务书 §④ 尾巴提的那件★)**: ★**`iss282_mech_sync_m5_baseline_after_landing` 这条 need —— ★**main 20:5x 实查: `grep -c iss282_mech_sync_m5_baseline_after_landing state/fragments/mech.yaml` = 0 ⇒ ★**它已经不在盘上了 (★被后来的单子合并/清掉了★) ⇒ ★**不要去找它、不要凭空造它★** ★ ⇒ ★**`iss294_usbc_edge_opening_size_and_z_window` 这条还在 (★`state/fragments/mech.yaml` L2729★) ⇒ ★**你只需要在分片里把它的现状写清 (★它 = 结构开口最终尺寸 = main→老板拍板项 ⇒ **不许你自己定尺寸**★)★** ★

★**★也要把 `status` 块更新成你这一单的 (★用 `--status` 参数★)★**: ★`phase=delivered progress_pct=100 health=绿 summary="★ISS-296 cont2 交卷 …"`★

### ★③ 交卷前必跑 (★全部本机实跑, 贴现场 rc★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 MECH/check_board_frame_coords.py ;            echo "rc=$?"
python3 MECH/check_board_frame_coords.py --selftest ;  echo "rc=$?"
python3 MECH/check_demo_struct_truth.py ;              echo "rc=$?"
python3 MECH/check_demo_struct_truth.py --selftest ;   echo "rc=$?"
python3 MECH/check_onepass_mech_sync.py ;              echo "rc=$?"
python3 MECH/check_onepass_struct_crosscheck.py ;      echo "rc=$?"
python3 logs/iss296/probe_ledger_reading_same_source.py ; echo "rc=$?"
python3 state/merge.py ;                               echo "rc=$?"
python3 state/gate_check.py ;                          echo "rc=$?"
python3 state/issue_check.py ;                         echo "rc=$?"
grep -c iss296 state/fragments/mech.yaml ;             echo "count=$?"
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro \
       HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
ls -la --time-style=full-iso HW/PCB/demo_mainboard.kicad_pcb
```

## ★★⑮-3 · 边界 (★一条不许松★)

★**零写板** (★板 md5 + mtime 双重自证★) · ★**零落表** · ★**不许写落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` 本体 (★只读★)** ★ · ★**不许改 `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` / `HW/PCB/demo_mainboard.kicad_pcb` / `HW/PCB/demo_mainboard.kicad_pro` / `state/gen_netlist.py` / `state/land_v_values.py`** ★ · ★**不许改 `SW/tools/check_demo_panel_spec.py` 的 R6 逻辑** (★那是 ISS-284 的定版闸·MECH 侧只【读它的形状】+ 【在自己的探针里读它的解析器】★) ★ · ★**不许改 `MECH/check_onepass_mech_sync.py` / `MECH/check_onepass_struct_crosscheck.py`** (★ISS-294 的交卷物·只跑它们做回归·不许改★) ★ · ★**不许改 `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md`** (★ISS-290 的交卷物★) ★ · ★**不许改任何阈值** (★CRIT 0.60 / cavity_req 4.50 / cav_v 38.00 / duct_v 6.00 一个都不许动★) ★ · ★**不许碰 `HW/` 与 `SW/` 的文件与分片** ★ · ★**不许改 `state/gate_check.py` / `state/issue_log.yaml`** (★签字是 main 的活★) ★ · ★**零外发** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料 ⇒ **不许发任何邮件 / 询价 / 问询 / 采购 / 原厂问询** ⇒ 缺口一律【自己网上查】+ 标证据等级 [官网]/[实测]/[媒体]/[推算]/[0数据] + 查不到就写降级方案 ⇒ 没有「批一句可以发」这个选项★) ★ · ★**不替老板拍板** ★ · ★**不自签 issue_log** (★verify_by=main★) ★ · ★**只写自己的分片 `state/fragments/mech.yaml`** (★`hw.yaml` / `sw.yaml` / `pm.yaml` 一个字节都不许碰★) ★ · ★**实物 `[实测]` = 0 条** (★本机无板无量具★) ★

## ★★⑮-4 · 死因纪律 (★这一趟的命门就是【别再被连带打死而不落盘】★)

★**① 干活的顺序必须是【先落盘】**: ★**交卷单先 `write` 补成完整骨架 (★哪怕每块只写一句占位★) ⇒ 再逐块填** ★ (★本趟只剩 paperwork, 快得很★)
★**② 每 10 分钟至少一次写盘** · ★**每落一件交付物就把 rc 追加进交卷单** (★这样再被打断, 已完成的部分都在★)
★**③ 单条 `exec` ≤ 60 秒** · ★**长任务一律 `nohup ... > logs/iss296/x.log 2>&1 &` + 短轮询** (★前台长 exec = 被掐的头号原因★)
★**④ 分片写完 `grep -c iss296 state/fragments/mech.yaml` 校验** ★
★**⑤ 不许把整份大文件读进来** (★只 grep 你要改的那几行★)
★**⑥ 写分片必须用 `state/frag_write.py` 原子写 (★禁止 `open(p,"w")`★)** ★
★**⑦ 文档订正必须追加式 (★老字不许删★) ⇒ ★**改数必须留痕 (★谁改的 / 哪个单号 / 新旧值 / 依据★)★** ★
★**⑧ 不许为了让闸绿而改闸 / 放宽判据** ★
★**⑨ 沙盒副本上做反向用例, 真件一个字节不许碰** ★
