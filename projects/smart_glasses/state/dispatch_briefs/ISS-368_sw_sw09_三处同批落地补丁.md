★**任务书全文**: `state/dispatch_briefs/ISS-368_sw_sw09_三处同批落地补丁.md` ★
★**题**: ★**把「板那一趟」SW 侧清单第 9 条 (SW09_FP_TRUTH_READ) 的【三处同批落地】做成【幂等补丁脚本 + 副本 dry-run 证明 + 回滚说明】** ★★
★**类别**: ★**纯作业包 + 沙盒 dry-run + 新建闸 · 零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 · 零外发 · 不代老板拍板** ★★
★**派活依据 (★main 2026-11-23 16:58 裁决 + 17:5x 本机实读·不抄任何 agent 报告★)**:
★**① ISS-362 (sw-lead) 交卷页 §B5 第 1 问, main 已裁 (★原文在 `state/fragments/pm.yaml` 的 answer
`iss363_b5_1_checklist_ninth_item_verdict_20261123`★)**: ★**「加第 9 条」= 加** ★ ⇒ ★**但必须三处同批落地**:
　① `SW/BOARD_ONEPASS_SW_SYNC.md` 的 §2 表 + §2.1 分布表 + §6 JSON 块 加 `SW09_FP_TRUTH_READ`
　② `SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md` 的 H4-REG 三数字 **8→9 / 0→1 / 4→新值**
　③ 本单新闸 `SW/tools/check_fp_truth_read.py` (★ISS-363 已交·裸跑 rc=0·`--selftest` 8/8★)
★**② main 已裁 (★同族第 2 问★)**: ★**「加闸」= 加** ⇒ ★**交新脚本 `SW/tools/check_fp_truth_read.py` · 挂不挂链 = main 的机制地界** ★
★**③ main 已裁 (★第 3 问★)**: ★**9 条过期 need 的正文【不改】** ⇒ 改用机器闸 F3 判「仍 open 的 to=sw-lead need 引着的 md5 == 落表台账链头」★
★**④ main 已裁 (★第 4 问★)**: ★**锚点副本跟到 ISS-302 链头 · 但必须走合法换源通道 (落 decision + 留痕)· 不许手改 md5** ⇒ ★**ISS-363 零改那个文件**
★**⇒ 「三处同批落地」的【真件落地】= main 的一键动作 (★落表批次地界★) ⇒ ★**本单只交【可执行的幂等补丁 + 副本 dry-run 证明 + 回滚说明】· 真件零改** ★★

★**★为什么要现在做 (★main 17:5x 本机实读★)**: ★**「板只改一次」那一趟 (S1~S13) 会【合法地】把三份真源的 md5 一起换掉** ⇒
★**SW 侧的 10 道准出闸 + 清单页 + ISS-362 页三数字全部盯着这件事** ⇒ ★**若三处不同批落地 ⇒ 清单页说 9 条、ISS-362 页说 8 条、
闸按 8 条判 ⇒ 那一趟当天必然出现「清单与闸互相打脸」⇒ 红了没人解释 ⇒ 最坏是有人为让闸绿去改锚点/改判据 (★正是 ISS-273/275/284 花大力气堵掉的漏洞★)** ★
★**⇒ 本单 = 把那三处变成【一次可执行、幂等、可回滚、且有沙盒证明的动作】** ★★

★**本单交付物 (★3 件·不许扩项★)**:
★**① 一页** ★**新建** `SW/BOARD_ONEPASS_SW09_LANDING_PATCH.md` ★★
  · §0 口径与读数 (★每个数字写清「哪个脚本产出·怎么复跑」★)
  · §1 三处落点逐字规格: ★**每处的【定位串】(★唯一锚点·不许靠行号★) + 【原文】+ 【新文】+ 【改完怎么自证】** ★
  · §2 幂等性: ★**同一补丁跑第二次 ⇒ 零变更 (★逐字节 diff = 0★)· 跑第三次同样零变更** ★
  · §3 dry-run 证明 (★副本上跑★): ★**改完三处后 10 道 SW 闸全绿 + 新闸 F1~F7 全绿 + 反证「只改一处 ⇒ H4 红 + F4 红」** ★
  · §4 回滚: ★**逐字节反向补丁 + 回滚命令 + 回滚后 10 道闸复跑读数** ★
  · §5 未决项 (★只登记·不代拍★): ★**新闸挂不挂 `state/gate_check.py` 的 EXTRA_GATES = main 的机制地界 (★本单零挂链★)** ★
★**② 幂等补丁脚本 + 一条机器闸** ★**新建** ★
  · ★**新建** `SW/tools/apply_sw09_three_place_patch.py` (★★**默认干跑 (dry-run)·只有显式 `--apply` 才写盘·★且只允许写到 ★副本目录★⇒ 真件写不进去★) ★★
  · ★**新建** `SW/tools/check_sw09_patch_dryrun.py` (★判据: ★**① 三处是否同批到位 (★页内三处 + JSON 块计数 == 9★) ② ISS-362 页 H4-REG 三数字是否 == (9/1/新值) ③ 干跑两次的 diff 是否为 0 ④ 10 道 SW 闸是否全绿 ⑤ 证据等级五级白名单 ⑥ 正文零挂起措辞 ⑦ 沙盒在项目盘 `tmp/`★) ★★
    · ★**`--selftest` 反向用例 ≥ 6 条·每条自证「红的是目标那一条, 其余仍绿」** ★
★**③ 交卷页 + 分片 + 留证** ★
  · ★**交卷页** ★**新建** `HANDOFF/2026-11-23_sw-lead_ISS368_SW09三处同批落地补丁.md` (★B1~B6 六段齐全 + 验收线逐条判定 + 落盘清单 + 沙盒留证路径★)
  · ★**分片** `state/fragments/sw.yaml` ★**只走 `state/frag_write.py`** ★ ⇒ 写前后各记一次 md5 基线 · ★期间被别人改过 ⇒ 停下并在交卷页 B5 写清「已停止」·不许静默覆盖★
  · ★**留证** `logs/iss368/` (★基线 md5 / 干跑两次的 diff / selftest 全量输出 / 闸复跑输出★)

★**边界 (★逐条·不许越★)**:
★**零写板** (★板 md5 必须仍 `611b869e13518c3c023fb178f91a0075` · mtime 必须仍 `2026-11-06 07:07:17.362193413`★) ★
★**零落表** (★`HW/netlist_v1.csv` · `HW/netlist_v1_pins.csv` · `HW/BOM_v1.csv` · `SW/SW_MD5_BASELINE_LEDGER.md` · `state/issue_log.yaml` 一字不改★) ★
★**★真件三处零改 (★本单只交补丁·真件落地是 main 在那一趟的一键动作★)**: ★**`SW/BOARD_ONEPASS_SW_SYNC.md` · `SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md` ·
`SW/tools/check_fp_truth_read.py` 一字不许改** ★ ⇒ ★**dry-run 一律在项目盘 `tmp/` 的副本上做** ★
★**零改既有闸**: ★**`SW/tools/check_onepass_sw_sync.py` · `SW/tools/check_sw_fp_truth_impact.py` · `SW/tools/check_onepass_sw_release.py` ·
`state/gate_check.py` · `state/merge.py` · `state/frag_write.py` 一字不改** ★ ⇒ ★**零挂链 (本单的新闸也不挂)** ★
★**零外发 / 零采购 / 零联系供应商** ★ **不替老板拍板** ★ **不写别人的分片** (★只写 `state/fragments/sw.yaml`★) ★ **不改 `PROJECT_TRACKER.md` §0** ★
★**证据分级必标** (★`[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]`★) ★
★**单条 `exec` ≤ ~120 秒 · 不许 `yaml.safe_load` 3 MB 的 `STATE.yaml`** ★

★**必跑命令 (★全部真实存在·main 2026-11-23 17:5x 本机实测过★)**:
```
python3 SW/tools/check_fp_truth_read.py                   # ★ISS-363 的闸·只读用★
python3 SW/tools/check_fp_truth_read.py --selftest
python3 SW/tools/check_sw_fp_truth_impact.py              # ★ISS-362 的闸·只读用★
python3 SW/tools/check_onepass_sw_sync.py                 # ★既有闸·读完须仍 rc=0★
python3 SW/tools/check_onepass_sw_release.py              # ★既有汇总闸·读完须仍 rc=0★
python3 SW/tools/apply_sw09_three_place_patch.py --dry-run
python3 SW/tools/check_sw09_patch_dryrun.py              # ★本单新建★
python3 SW/tools/check_sw09_patch_dryrun.py --selftest
python3 state/merge.py
python3 state/gate_check.py
python3 state/frag_write.py --agent sw-lead --show
md5sum HW/PCB/demo_mainboard.kicad_pcb SW/BOARD_ONEPASS_SW_SYNC.md SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md SW/SW_MD5_BASELINE_LEDGER.md
```
★**验收线 (★20 条·main 会自己复跑·不采信你的自述★)**:
① 页存在且非空 ② 三处落点各给「定位串 + 原文 + 新文 + 自证」 ③ 补丁脚本默认干跑 · 写不进真件 ④ 干跑两次 diff = 0 ⑤ 副本上三处同批落地后 10 道 SW 闸全绿 ⑥ 新闸 F1~F7 全绿 ⑦ 反证「只改一处 ⇒ H4 红 + F4 红」成立 ⑧ 新闸 rc=0 ⑨ `--selftest` ≥6/6 且每条自证「只红目标那条」 ⑩ 沙盒在项目盘 `tmp/` ⑪ 真件三处逐字节未变 (★md5 前后一致★) ⑫ 板 md5/mtime 逐字节未变 ⑬ 网表/脚表/BOM/锚点台账 md5 逐字节未变 ⑭ 既有闸脚本一个字节未改 ⑮ `merge.py` rc=0 且 `gate_check.py` rc=0 (★Q1 = 18/18★) ⑯ 证据等级全在五级白名单 ⑰ 正文零挂起措辞 ⑱ 分片写入只走 `state/frag_write.py` ⑲ 交卷页 B1~B6 齐全 + `logs/iss368/` 留证在盘 (≥ 10 件) ⑳ 回滚说明 + 反向补丁在盘 (★逐字原文 + 回滚命令 + 回滚后闸读数★)
★**收工后按老规矩回卷**: ★**交卷摘要 + 必跑命令的 rc + 三件交付物路径 + 边界自证 + 要 main 裁的事 (逐条写清「要谁回答什么」)★ ★
