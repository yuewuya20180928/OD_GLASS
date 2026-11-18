# ISS-299 · hw-lead · cont1 续做说明 (★2026-11-17 22:2x · cron `fb67af40` 重派僵尸 fixing★)

★**权威任务书全文** = `state/issue_log.yaml` 里 `ISS-299` 的 `task_brief` 字段 (★= `state/dispatch_briefs/ISS-299_hw_h1_reanchor_hop2.md` 全文★)
★**本文件 = cont1 续做说明全文★**
★**★从盘上继续, 不要从零重做★** (★主体已做完, 只差最后一格★)

# ★★⑱ · ISS-299 cont1 续做说明 (★2026-11-17 22:2x 由 main (moli) · cron `fb67af40` 本轮追加★)

> ★**上一趟子会话**: `agent:hw-lead:subagent:008bc381` (sessionId `5b01e341`) · **21:46:41 → 21:59:41** · runtime 776s · **status=timeout / abortedLastRun=true** ⇒ ★**死在「交卷单 B0~B6 已填、⑰-1/⑰-3/⑰-4/⑰-5 已填、只差 §⑰-2 那张回归读数表」那一刻** ★
> ★**★死因 = 【父死子死】型连带 (★不是你自己跑不动★)**: ★**两个子会话 (hw-lead `5b01e341` 与 mech-lead `1765a992`) 的 `endedAt` 相差 81 毫秒 (21:59:41 / 21:59:40) ⇒ 是【父 run `aea23265` 整个被掐 ⇒ 两个子被连带杀掉】⇒ ★**⇒ 这一趟的命门 = 【先落盘再展开】: 交卷单先填完落盘, 再做别的★** ★
> ★**★⇒ 本 job (cron `fb67af40`) = 僵尸 fixing 的唯一重派方 ⇒ 本轮重派 = cont1 续做 (★不是从零重做★)★**

## ★★⑱-1 · 盘面实况 (★main 22:1x~22:2x 本机实跑 + 实读, 不抄任何 agent 报告★)

★**★好消息: 主体【全做完了】⇒ 你这趟【只剩 1 件 paperwork】★**

| 件 | 现状 (★main 22:1x~22:2x 本机实读 + 实跑★) |
|---|---|
| ★**闸本体** ★ | ★**`HW/check_pin_function_labels.py` = 55,420 B (mtime 21:51:18) ⇒ 已改好**: `PROTECTED_MD5` 三个基线**已重锚**到 ISS-283 落表后真盘实测值 (`HW/netlist_v1.csv` = `37f62ac3f0b81d92ca7d48fdea717f07` · `HW/netlist_v1_pins.csv` = `a4270120454aedf7a23c92cd8985c8a6` · `HW/BOM_v1.csv` = `5d02bece9477ffce5fbe0193c7d5cce4`) · `MD5_ANCHOR_CHAIN` **逐跳补齐** (网表追加 `ISS-236` + `ISS-283` ×2 三跳 · BOM 追加 `ISS-236` + `ISS-283` 两跳 · ★每跳「旧 md5」== 上一跳「新 md5」⇒ 链无断★) ⇒ `KNOWN_DEFECTS` 15 条 + `KNOWN_SNAPSHOT_SHA256` = `4b48cfee483dfd8a…` **一字未动** ★ |
| ★**闸读数** ★ | ★**`python3 HW/check_pin_function_labels.py --expect-known` ⇒ rc=0** (快照 15 / 实算 15 逐条一致) · ★**`--selftest` ⇒ rc=0** (「13 条既有 + 10 条通道反向用例, 每条均自证改到了目标」) · ★**默认模式 ⇒ rc=1 且恰好 15 条缺陷 = 【既有缺陷基线·不是失败】★** ★ ⇒ ★**任务书目标读数「缺陷 18→15 · `--expect-known` rc=0 · `--selftest` rc=0」【全部达成】★** ★ |
| ★**交卷单** ★ | ★**`HANDOFF/2026-11-17_hw-lead_ISS299_H1重锚第2跳_基线常量.md` = 20,689 B** ⇒ ★**B0~B6 六块齐全且都非空** (B0 1,426 B · B1 1,099 · B2 2,485 · B3 1,257 · B4 2,013 · B5 776 · B6 1,809) · ★**⑰-1 反向用例 6/6 表已填** · ★**⑰-3 边界自证 E1~E8 已填** · ★**⑰-4 / ⑰-5 已填** ★ ⇒ ★**不要重建, 只填最后一格★** |
| ★**★唯一没填的** ★ | ★**§⑰-2「全套回归读数 (★现场 rc★)」那一行还是占位符**: ★**L189 = `★(回归跑完后现场填入)★`** ★ (★另 L166 的指路句 `★(见文末 §⑰-2 追加块 —— 回归跑完后现场填入)★` 在 §⑰-2 有内容后就自然成立★) ⇒ ★**★这就是你这趟唯一的活★** ★ |
| ★**ISS-297 附带小修** ★ | ★**已完成**: `HANDOFF/2026-11-17_hw-lead_ISS297_合法改板通道.md` 末尾**追加**了 3 行标准标题行 (B2 / B3 / B4 · mtime 21:52 · ★B0~B6 老字未动★) ⇒ ★**任务书那条款已完成, 你不用再做★** ★ |
| ★**分片** ★ | ★**`state/fragments/hw.yaml`: `grep -c iss299` = 10** ⇒ `interface_claims` 5 条 (`iss299_hw_gate5_h1_reanchor_hop2_done` / `iss299_hw_gate5_baseline_constants_reanchored` / `iss299_hw_anchor_chain_gapless_appended` / `iss299_hw_zero_board_write_zero_landing` / `iss299_hw_iss297_handoff_b2b3b4_appended`) · `needs_from` 2 条 · `artifacts` 3 条 · ★**`status` = {phase: delivered, progress_pct: 100, health: 绿, summary 已是 ISS-299}** ⇒ ★**分片【已齐】, 本单【不用再写分片】★** ★ |
| ★**日志** ★ | ★**在盘**: `logs/iss299/selftest_after.log` (4,718 B) · `logs/iss299/regression.log` (42,579 B) · `logs/iss299/gate_check.log` (2,928 B) · `logs/iss299/reverse_cases.log` (775 B) ⇒ ★**§⑰-2 的真实读数从这里抄, 一个字不许编★** ★ |
| ★**受保护 5 件** ★ | ★**板 `611b869e13518c3c023fb178f91a0075` (mtime 仍 `2026-11-06 07:07:17.362193413`) · `.kicad_pro` `3e504d2be83152e337949723e909be1b` · 网表 `37f62ac3f0b81d92ca7d48fdea717f07` · 脚表 `a4270120454aedf7a23c92cd8985c8a6` · BOM `5d02bece9477ffce5fbe0193c7d5cce4`** ★ ⇒ ★**必须逐字节不变 (★本单零写板 · 零落表★)★** ★ |

## ★★⑱-2 · 本趟只做 1 件 (★闸本体一个字都不许再动★)

★**★目标: 把交卷单 §⑰-2 那行占位符换成【真实回归读数表】★**

### ★① 填 §⑰-2「全套回归读数 (★现场 rc★)」

★**做法 (★素材盘上都有, 照抄真实 rc, 不许编★)**:
- ★**逐条列本单自跑过的命令 + 现场 rc + 一句话结论**, 覆盖: ★**`python3 HW/check_pin_function_labels.py` (默认 ⇒ rc=1 · 恰好 15 条缺陷 = 既有缺陷基线)** · ★**`--expect-known` ⇒ rc=0 (15/15 一致)** · ★**`--selftest` ⇒ rc=0 (13 + 10)** · ★**反向用例 R1~R6 (6/6, 引用 ⑰-1 已填的那张表即可)** · ★**`python3 state/merge.py` ⇒ rc=0** · ★**`python3 state/gate_check.py` ⇒ rc=0 (Q1 18/18)** · ★**`python3 state/issue_check.py` ⇒ rc=0** ★
- ★**末尾再追加一行受保护 5 件 md5 + 板 mtime 的终检读数 (★用 `md5sum` + `ls -la --time-style=full-iso` 现跑, 别抄旧的★)** ★
- ★**★替换的是那行占位符 (★`★(回归跑完后现场填入)★`·★它本来就是给你留的空位·不是「老字」★)⇒ ★**允许改这一行** ★ ⇒ ★**但 §⑰-1 / ⑰-3 / ⑰-4 / ⑰-5 与 B0~B6 的【老字一个字不许删、不许改】★** ★

### ★② 交卷前自检 (★两条★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 state/check_report_placeholders.py < HANDOFF/2026-11-17_hw-lead_ISS299_H1重锚第2跳_基线常量.md ; echo "rc=$?"
grep -nE "🔄|待填|★\(回归跑完后现场填入\)★" HANDOFF/2026-11-17_hw-lead_ISS299_H1重锚第2跳_基线常量.md ; echo "★上面必须 0 行命中★"
```
★**★注意 (★main 22:2x 实测出来的坑★)**: ★**`check_report_placeholders.py` 只抓 `%(name)s` / `PLACEHOLDER` / 裸 `TODO`·它【抓不到】`🔄 待填` 和 `★(…填入…)★` 这种形态 ⇒ ⇒ 别拿它当「已填」的证据 ⇒ ★**上面那条 `grep` 才是真判据 (必须 0 行命中)★** ★

### ★③ 交卷前必跑 (★全部本机实跑, 贴现场 rc★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 HW/check_pin_function_labels.py ;                echo "rc=$?"   # ★既有缺陷基线·期望 1★
python3 HW/check_pin_function_labels.py --expect-known ; echo "rc=$?"   # ★期望 0★
python3 HW/check_pin_function_labels.py --selftest ;     echo "rc=$?"   # ★期望 0★
python3 state/merge.py ;                                  echo "rc=$?"
python3 state/gate_check.py ;                             echo "rc=$?"
python3 state/issue_check.py ;                            echo "rc=$?"
grep -c iss299 state/fragments/hw.yaml ;                  echo "count=$?"
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro \
       HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
ls -la --time-style=full-iso HW/PCB/demo_mainboard.kicad_pcb
```

## ★★⑱-3 · 边界 (★一条不许松★)

★**零写板** (★板 md5 + mtime 双重自证★) · ★**零落表** (★不许动 `HW/SCHEMATIC_LANDING_V1_LANDED.md` 本体·只读★) ★ · ★**不许再改 `HW/check_pin_function_labels.py` 一个字** (★★本单目标读数已全部达成·★改它 = 自己把已达成的读数改红★)★ ★ · ★**不许改 `state/board_reboard.py`** (★共用判决库·只读★) ★ · ★**不许改 `state/gate_check.py`** (★挂闸是 main 的活★) ★ · ★**不许动 `MECH/` 与 `SW/` 任何文件和分片** (★MECH 侧归 ISS-300★) ★ · ★**不许改 `state/fragments/mech.yaml` / `state/fragments/sw.yaml` / `state/fragments/pm.yaml`** ★ · ★**不许自签 `state/issue_log.yaml`** (★verify_by=main★) ★ · ★**不许外发** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料 ⇒ **不许发任何邮件 / 询价 / 问询 / 采购 / 原厂问询** ⇒ 缺口一律【自己网上查】+ 标证据等级 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` + 查不到就写降级方案 ⇒ 没有「批一句可以发」这个选项★) ★ · ★**不替老板拍板** ★ · ★**实物 `[实测]` = 0 条** ★ · ★**只写 `HANDOFF/2026-11-17_hw-lead_ISS299_H1重锚第2跳_基线常量.md` 这一个文件 (+ `logs/iss299/` 下你自己的日志)** ★

## ★★⑱-4 · 死因纪律 (★这一趟的命门就是【别再被连带打死而不落盘】★)

★**① 干活的顺序必须是【先落盘】**: ★**这一趟只有 1 件 ⇒ ★**先把 §⑰-2 填完落盘 (★写完立刻 `ls -la` 确认 mtime 变了★) ⇒ 再跑验收命令 ⇒ 最后交卷** ★ ⇒ ★**这样再被打断, 活也不会丢** ★
★**② 每 10 分钟至少一次写盘** ★
★**③ 单条 `exec` ≤ 60 秒** · ★**长任务一律 `nohup ... > logs/iss299/x.log 2>&1 &` + 短轮询** (★前台长 exec = 被掐的头号原因★) ★
★**④ 不许把整份大文件读进来** (★只 grep 你要改的那几行★) ★
★**⑤ 文档订正必须追加式 (★老字不许删★)** ★
★**⑥ 不许为了让闸变绿而改闸 / 放宽判据** ★

## ★★⑱-5 · 交卷回复格式 (★贴现场 rc, 不许只说「已完成」★)

★**回你的老板 (main) 时贴**: ★**① §⑰-2 填进去之后交卷单的新字节数 + 新 mtime** · ★**② 上面 §⑱-3 那组命令的现场 rc 原样** · ★**③ 受保护 5 件 md5 + 板 mtime** · ★**④ `grep -nE "🔄|待填|★\(回归跑完后现场填入\)★" <交卷单>` ⇒ 0 行命中** · ★**⑤ 诚实边界 (★本趟只填了 §⑰-2·闸本体一个字没动·零写板零落表·零外发·实物 [实测] = 0 条·没自签 issue_log★)** ★
