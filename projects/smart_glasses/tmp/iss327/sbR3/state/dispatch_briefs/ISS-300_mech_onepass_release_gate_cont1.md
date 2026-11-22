# ISS-300 · mech-lead · cont1 续做说明 (★2026-11-17 22:2x · cron `fb67af40` 重派僵尸 fixing★)

★**权威任务书全文** = `state/issue_log.yaml` 里 `ISS-300` 的 `task_brief` 字段 (★= `state/dispatch_briefs/ISS-300_mech_onepass_release_gate.md` 全文★)
★**上一趟交卷单**: `HANDOFF/2026-11-17_mech-lead_ISS300_结构侧准出汇总闸.md`
★**本文件 = cont1 续做说明全文★**
★**★从盘上继续, 不要从零重做★** (★闸本体已做完, 只差 paperwork★)

# ★★⑱ · ISS-300 cont1 续做说明 (★2026-11-17 22:2x 由 main (moli) · cron `fb67af40` 本轮追加★)

> ★**上一趟子会话**: `agent:mech-lead:subagent:e2720689` (sessionId `1765a992`) · **21:46:40 → 21:59:40** · runtime 776s · **status=timeout / abortedLastRun=true** ⇒ ★**死在「新闸已写好并跑绿、只差交卷单 B1~B6 还是 1,828 B 骨架」那一刻** ★
> ★**★死因 = 【父死子死】型连带 (★不是你自己跑不动★)**: ★**两个子会话 (hw-lead `5b01e341` 与 mech-lead `1765a992`) 的 `endedAt` 相差 81 毫秒 (21:59:41 / 21:59:40) ⇒ 是【父 run `aea23265` 整个被掐 ⇒ 两个子被连带杀掉】⇒ ★**⇒ 这一趟的命门 = 【先落盘再展开】: 交卷单先填完落盘, 再做别的★** ★
> ★**★⇒ 本 job (cron `fb67af40`) = 僵尸 fixing 的唯一重派方 ⇒ 本轮重派 = cont1 续做 (★不是从零重做★)★**

## ★★⑱-1 · 盘面实况 (★main 22:1x~22:2x 本机实跑 + 实读, 不抄任何 agent 报告★)

★**★好消息: 闸本体【已做完且已跑绿】⇒ 你这趟【只剩 paperwork】★**

| 件 | 现状 (★main 22:1x~22:2x 本机实读 + 实跑★) |
|---|---|
| ★**新闸本体** ★ | ★**`MECH/check_onepass_mech_release.py` = 21,227 B (mtime 21:53) ⇒ 已写好**: 清单里 6 道闸齐 (`MECH/check_board_frame_coords.py` · `MECH/check_demo_struct_truth.py` · `MECH/check_onepass_mech_sync.py` · `MECH/check_onepass_struct_crosscheck.py` · `MECH/board_port_opening_s6_check.py` · `MECH/check_mech_verdict_freshness.py`) · ★**fail-closed 语义照 `state/gate_check.py` 的 `run_external_gate` 写 (脚本不存在 / 跑不起来 / 超时 ⇒ 一律算红)** ★ · ★**红闸点名 + `--json` + `--selftest` 三样都有** ★ |
| ★**闸读数 (main 现跑)** ★ | ★**`python3 MECH/check_onepass_mech_release.py` ⇒ rc=0** (末段: 「6 道闸: 绿 6 / 红 0」+「★汇总 rc = 0 ⇒ ★MECH 侧结构可以出 Gerber★」+ ★自带一句诚实边界「只代表结构侧 6 道闸全绿·不等于整条板链全绿·HW/SW 侧的闸另算」★) · ★**`--selftest` ⇒ rc=0** (末行「【自检结论】✅ 一致 (反向用例全抓到 · 真盘一个字节不许动)」; ★反向用例 ⑥ 真沙盒真篡改: 改 1 个开口坐标常量 ⇒ 汇总红 1 道并【点名到】`MECH/check_board_frame_coords.py` · 其余 5 道仍绿 · 恢复 ⇒ 回绿 · 真件 md5 不变 = True★) · ★**`--json` ⇒ `ok=True n_total=6 n_green=6 n_red=0` 且 cwd 无关 (root 由 `__file__` 推导)** ★ ⇒ ★**任务书的三条验收读数【全部达成】★** ★ |
| ★**交卷单 (★唯一没做的★)** ★ | ★**`HANDOFF/2026-11-17_mech-lead_ISS300_结构侧准出汇总闸.md` = 1,828 B ⇒ 还是骨架**: ★**★`grep -cE "🔄|待填"` = 10 处占位符★** ⇒ ★**B1 结论摘要 / B2 验收标准自评 / B3 证据分级 / B4 接口取值声明 / B5 未决项与卡点 / B6 自证复现命令 —— 六块全是「🔄 待填」** ★ ⇒ ★**★这就是你这趟唯一的活★** ★ |
| ★**分片** ★ | ★**`state/fragments/mech.yaml`: `grep -c iss300` = 12** ⇒ ★**`interface_claims` 5 条** (`iss300_mech_release_gate_path` / `iss300_mech_release_gate_command` / `iss300_mech_release_manifest` / `iss300_mech_release_failclosed_semantics` / `iss300_mech_release_zero_write_board`) · ★**`needs_from` 2 条** (`iss300_release_gate_hook_into_gate_chain` / `iss300_release_gate_hook_staging_vs_legal_reboard`) · `artifacts` 3 条 · ★**`status` = {phase: delivered, progress_pct: 100, health: 绿, summary 已是 ISS-300}** ⇒ ★**分片【已齐】, 本单【不用再写分片】★** ★ |
| ★**日志** ★ | ★**在盘**: `logs/iss300/` 下 17 个文件 —— `baseline_6gates.log` · `boundary_before.txt` (4,255 B) · `boundary_after.txt` (4,317 B) · `main_run.log` · `merge.log` · `regression.log` (8,163 B) · `regression_iss300.sh` · `reverse_case.log` (9,017 B) · `reverse_case_iss300.py` · `selftest.log` · `selftest_rerun.log` · `gate_check_board_frame_coords.log` · `gate_check_demo_struct_truth.log` · `gate_check_mech_verdict_freshness.log` · `gate_check_onepass_mech_sync.log` · `gate_check_onepass_struct_crosscheck.log` · `gate_check_board_port_opening_s6_check.log` ⇒ ★**交卷单的素材全在这里, 一个字不许编★** ★ |
| ★**受保护 6 件** ★ | ★**板 `611b869e13518c3c023fb178f91a0075` (mtime 仍 `2026-11-06 07:07:17.362193413`) · `.kicad_pro` `3e504d2be83152e337949723e909be1b` · 网表 `37f62ac3f0b81d92ca7d48fdea717f07` · 脚表 `a4270120454aedf7a23c92cd8985c8a6` · BOM `5d02bece9477ffce5fbe0193c7d5cce4`** ★ ⇒ ★**必须逐字节不变 (★本单零写板 · 零落表★)★** ★ |

## ★★⑱-2 · 本趟只做 1 件 (★闸本体一个字都不许再动★)

★**★目标: 把交卷单的 10 处占位符全部换成真实内容★**

### ★① 填满 B0 + B1~B6 (★素材盘上都有, 照抄真实 rc, 不许编★)

★**做法 (★逐块给要点, 内容你从 `logs/iss300/` 抄真实读数★)**:

- ★**B0 交付物清单**: ★**4 行全部改成「✅ 已完成」并给现场自证** (① 本交卷单 ⇒ 填完后给新字节数 + mtime · ② `MECH/check_onepass_mech_release.py` ⇒ **21,227 B · mtime 21:53** + 主跑 rc=0 + `--selftest` rc=0 · ③ `state/fragments/mech.yaml` ⇒ **`grep -c iss300` = 12** (interface_claims 5 / needs_from 2 / artifacts 3 / status=delivered·100·绿) · ④ `logs/iss300/` ⇒ **17 个文件** (边界基线 + 回归日志 + 反向用例日志)) ★
- ★**B1 结论摘要 (一句话)**: ★**「MECH 侧『板只改一次』准出汇总闸已落地: 一条命令 `python3 MECH/check_onepass_mech_release.py` ⇒ rc=0 ⇒ 结构侧 6 道闸全绿 ⇒ 可以出 Gerber; 任一道红 ⇒ 汇总红并点名是哪一道」+ ★**附一句诚实边界: 「只代表结构侧 6 道闸全绿·不等于整条板链全绿·HW/SW 侧的闸另算」★** ★
- ★**B2 验收标准自评 (★逐条 通过/不通过/未验★)**: ★**照任务书「验收读数」那一条一条列, 每条给现场 rc + 结论**: ★**① 新闸主跑 rc=0 且逐条列 6 道各自的 rc** (★从 `logs/iss300/gate_check_*.log` 抄★) · ★**② `--selftest` rc=0** · ★**③ 6 道闸本体各自读数不许变 (今天全 rc=0)** · ★**④ `state/merge.py` rc=0 · `state/gate_check.py` rc=0 (Q1 18/18) · `state/issue_check.py` rc=0** · ★**⑤ 分片 (`frag_write.py` 原子写 · claims ≥3 · needs ≥1 · status 三项)** · ★**⑥ 交卷单 B1~B6 六块齐全 + 反向用例原样 rc + 边界自证** · ★**⑦ fail-closed 三条 (脚本不存在 / 跑不起来 / 超时 ⇒ 一律算红)** · ★**⑧ 清单缺一道 ⇒ 汇总直接红** ★ ⇒ ★**每条标「通过」/「不通过」/「未验」, 不许含糊★** ★
- ★**B3 证据分级**: ★**固定五级 `[官网]` / `[实测]` / `[媒体]` / `[推算]` / `[0数据]`** ⇒ ★**本单全是 `[实测]` (本机实跑读数)** · ★**★并如实写一句: 实物 `[实测]` = 0 条 (★本机无板、无量具 ⇒ 本页一切「实测」= 文件实读 + 脚本实跑★)** ★
- ★**B4 接口取值声明 (interface_claims)**: ★**照 `state/fragments/mech.yaml` 里那 5 条 `iss300_*` 的口径写进交卷单 (★key 逐字抄, 别自己另起名字★)** ★
- ★**B5 未决项与卡点**: ★**照分片里那 2 条 `needs_from` 写 (★只列事实与代价, 不替 main / 老板拍板★)**: ★**① `iss300_release_gate_hook_into_gate_chain` = 「把新闸挂进 `state/gate_check.py` 的门禁链」⇒ ★**挂闸是 main 的活 (★你只登记, 不许自己改 `state/gate_check.py`★)★** · ★**② `iss300_release_gate_hook_staging_vs_legal_reboard` = 「板那一趟当天, 汇总闸里那 2 道钉板 md5 闸必然从绿转红, 只有走合法改板通道才走得绿 ⇒ 当天读数怎么解释」** ★ ⇒ ★**★不许替 main 拍板★** ★
- ★**B6 自证复现命令**: ★**把下面这组命令逐条写进去 (★都能本机跑★)** ★

### ★② 交卷前自检 (★两条★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
grep -cE "🔄|待填" HANDOFF/2026-11-17_mech-lead_ISS300_结构侧准出汇总闸.md ; echo "★上面必须是 0★"
python3 state/check_report_placeholders.py < HANDOFF/2026-11-17_mech-lead_ISS300_结构侧准出汇总闸.md ; echo "rc=$?"
```
★**★注意 (★main 22:2x 实测出来的坑★)**: ★**`check_report_placeholders.py` 只抓 `%(name)s` / `PLACEHOLDER` / 裸 `TODO`·它【抓不到】`🔄 待填` ⇒ ⇒ ★**别拿它当「已填」的证据 ⇒ ★**上面那条 `grep` 才是真判据 (必须 0)★** ★

### ★③ 交卷前必跑 (★全部本机实跑, 贴现场 rc★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 MECH/check_onepass_mech_release.py ;            echo "rc=$?"
python3 MECH/check_onepass_mech_release.py --json ;     echo "rc=$?"
python3 MECH/check_onepass_mech_release.py --selftest ; echo "rc=$?"
python3 MECH/check_board_frame_coords.py ;               echo "rc=$?"
python3 MECH/check_demo_struct_truth.py ;               echo "rc=$?"
python3 MECH/check_onepass_mech_sync.py ;               echo "rc=$?"
python3 MECH/check_onepass_struct_crosscheck.py ;       echo "rc=$?"
python3 MECH/board_port_opening_s6_check.py ;           echo "rc=$?"
python3 MECH/check_mech_verdict_freshness.py ;          echo "rc=$?"
python3 state/merge.py ;                                echo "rc=$?"
python3 state/gate_check.py ;                           echo "rc=$?"
python3 state/issue_check.py ;                          echo "rc=$?"
grep -c iss300 state/fragments/mech.yaml ;              echo "count=$?"
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro \
       HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
ls -la --time-style=full-iso HW/PCB/demo_mainboard.kicad_pcb
```

## ★★⑱-3 · 边界 (★一条不许松★)

★**零写板** (★板 md5 + mtime 双重自证★) · ★**零落表** (★不许动 `HW/SCHEMATIC_LANDING_V1_LANDED.md` 本体·只读★) ★ · ★**不许再改 `MECH/check_onepass_mech_release.py` 一个字** (★★本单目标读数已全部达成·★改它 = 自己把已达成的读数改红★)★ ★ · ★**不许改那 6 道闸本体的任何一行** (★只聚合·判据不许动★) ★ · ★**不许改 `state/gate_check.py`** (★挂闸是 main 的活★) ★ · ★**不许碰 `HW/` 与 `SW/` 的任何文件和分片** (★HW 侧归 ISS-299·SW 侧归 sw-lead★) ★ · ★**不许改 `state/fragments/hw.yaml` / `state/fragments/sw.yaml` / `state/fragments/pm.yaml`** ★ · ★**不许自签 `state/issue_log.yaml`** (★verify_by=main★) ★ · ★**不许外发** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料 ⇒ **不许发任何邮件 / 询价 / 问询 / 采购 / 原厂问询** ⇒ 缺口一律【自己网上查】+ 标证据等级 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` + 查不到就写降级方案 ⇒ 没有「批一句可以发」这个选项★) ★ · ★**不替老板拍板** ★ · ★**实物 `[实测]` = 0 条** ★ · ★**只写 `HANDOFF/2026-11-17_mech-lead_ISS300_结构侧准出汇总闸.md` 这一个文件 (+ `logs/iss300/` 下你自己的日志)** ★

## ★★⑱-4 · 死因纪律 (★这一趟的命门就是【别再被连带打死而不落盘】★)

★**① 干活的顺序必须是【先落盘】**: ★**这一趟只有 1 件 ⇒ ★**先把交卷单 B0~B6 填完落盘 (★写完立刻 `ls -la` 确认 mtime 变了★) ⇒ 再跑验收命令 ⇒ 最后交卷** ★ ⇒ ★**这样再被打断, 活也不会丢** ★
★**② 每 10 分钟至少一次写盘** ★
★**③ 单条 `exec` ≤ 60 秒** · ★**长任务一律 `nohup ... > logs/iss300/x.log 2>&1 &` + 短轮询** (★前台长 exec = 被掐的头号原因★) ★
★**④ 不许把整份大文件读进来** (★只 grep 你要改的那几行★) ★
★**⑤ 文档订正必须追加式 (★老字不许删★)** ★
★**⑥ 不许为了让闸变绿而改闸 / 放宽判据** ★

## ★★⑱-5 · 交卷回复格式 (★贴现场 rc, 不许只说「已完成」★)

★**回你的老板 (main) 时贴**: ★**① 交卷单填完后的新字节数 + 新 mtime + `grep -cE "🔄|待填"` = 0** · ★**② 上面 §⑱-3 那组命令的现场 rc 原样** · ★**③ 受保护 6 件 md5 + 板 mtime** · ★**④ 诚实边界 (★本趟只填交卷单·闸本体一个字没动·那 6 道闸本体一个字没动·零写板零落表·零外发·实物 [实测] = 0 条·没自签 issue_log★)** ★
