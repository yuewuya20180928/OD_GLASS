# ★★⑭ · ISS-295 cont1 续做说明 (★2026-11-17 18:1x 由 main (moli) 追加★)

> ★**为什么有这一段**: 上一趟子会话 `agent:mech-lead:subagent:885e9633` (sessionId f80ec41b) 17:48:57 → 18:04:18 · runtime 462s · **status=timeout / abortedLastRun=true** ⇒ ★**死在「写闸文件」的那一刻** (transcript 最后两行: assistant「Now the gate itself:」→ toolResult「Aborted」)★ ⇒ ★**交付物 4 件里 3 件是 0 字节 / 骨架** ⇒ ★**本趟是【续做】, 不是从零重做** ★

## ★盘面实况 (★main 18:0x~18:1x 本机实测, 不抄任何 agent 报告★)

| 交付物 | 实测状态 |
|---|---|
| ① ★**新建** `MECH/BOARD_ONEPASS_MECH_CLAIMS.md` | ★**不存在** ★ (`ls` ⇒ No such file or directory) |
| ② ★**新建** `MECH/check_mech_verdict_freshness.py` | ★**不存在** ★ (`ls` ⇒ No such file or directory) |
| ③ 本交卷单 `HANDOFF/2026-11-17_mech-lead_ISS295_结构输入认领与防漂闸.md` | ★**967 B 骨架** ★ ⇒ B0~B6 七节全是「(占位 → 交卷时补全)」 |
| ④ 分片 `state/fragments/mech.yaml` | ★**0 条** ★ ⇒ `grep -c iss295` = 0 |

★**唯一在盘的产物**: `logs/iss295/gen_coverage_windows.py` (2473 B) = 抽「逐字覆盖窗口」的辅助脚本 (★上一趟刚写完就跑出漂移行清单, 接着就断了★) ⇒ ★**它是本趟的现成工具, 不用重写** ★

## ★上一趟已经查出来的 7 行漂移 (★直接当闸的监控对象, 不用重查★)

| 文件 | 行 (★会漂!)★ | 命中词 (★闸按这个短语命中★) |
|---|---|---|
| `MECH/BOARD_ONEPASS_MECH_SYNC.md` | L579 | 「没有这条边开口」 |
| `MECH/BOARD_ONEPASS_MECH_SYNC.md` | L610 | 「缺一条结构边开口规格」 |
| `MECH/BOARD_ONEPASS_MECH_SYNC.md` | L670 | 「缺一条边开口规格」 |
| `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` | L68 | 「登记为缺口」 |
| `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` | L175 | 「缺一条边开口规格」 |
| `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` | L188 | 「缺一条边开口规格」 |
| `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` | L294 | 「缺一条结构边开口规格」 |

★**⚠ 行号会漂** ⇒ ★**闸不许把行号写死** ⇒ ★**闸必须按【逐字短语】命中, 不许按行号命中** ⇒ ★★(★这是 ISS-273/ISS-286 那类「一落表就假红」的老坑★)★★
★**⚠ 反过来**: 闸也不许因为「这两页里现在还留着旧字」就判红 ⇒ ★**这两页的旧字是【历史留痕】(ISS-290 的机器块不许动) ⇒ 闸要判的是【新写的那段结论不许再漂】, 不是【旧字必须消失】** ★

## ★本趟只做 4 件 (★顺序不许换★)

1. ★**先把交卷单骨架补成「有内容的骨架」**: `write` 一次, 把 B0~B6 七块标题 + 每块要写什么的清单先写下去 ⇒ ★**不许再留「(占位 → 交卷时补全)」这种字样** ★
2. ★**B1**: 写 `MECH/BOARD_ONEPASS_MECH_CLAIMS.md` (★新建 · 结构侧输入认领句全表 · 可直接抄进作业包 §3-S6 · 含「还没主的输入」一节★)
3. ★**B2**: 写 `MECH/check_mech_verdict_freshness.py` (★新建 · 过期结论防漂闸 + `--selftest` 反向用例 ≥4 条 ★**按短语命中, 不许按行号**★)
4. ★**B3**: 交卷单填满 + 分片 `state/fragments/mech.yaml` (★走 `python3 state/frag_write.py --agent mech-lead` 原子写 · 写完 `grep -c iss295` ≥ 4★)

## ★验收 (★原样 rc 贴进交卷单★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 MECH/check_mech_verdict_freshness.py;             echo "rc=$?"
python3 MECH/check_mech_verdict_freshness.py --selftest;  echo "rc=$?"
python3 MECH/check_onepass_mech_sync.py;                  echo "rc=$?"
python3 MECH/check_onepass_struct_crosscheck.py;          echo "rc=$?"
python3 state/merge.py;                                   echo "rc=$?"
python3 state/gate_check.py;                              echo "rc=$?"
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro \
       HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
# ★★板 611b869e… / .kicad_pro 3e504d2b… 必须逐字节不变★★
```

★**受保护 5 件基线 (★main 18:1x 本机实测, 直接当你的验收基线★)**:
板 `611b869e13518c3c023fb178f91a0075` (mtime 仍 `2026-11-06 07:07:17.362193413`) · `.kicad_pro` `3e504d2be83152e337949723e909be1b` · 网表 `37f62ac3f0b81d92ca7d48fdea717f07` · 脚表 `a4270120454aedf7a23c92cd8985c8a6` · BOM `5d02bece9477ffce5fbe0193c7d5cce4`

## ★纪律 (★上一趟就是这么栽的★)

★**交卷单第一件事就是 `write` 建骨架** ★ · ★**长任务一律 `nohup ... > logs/iss295/x.log 2>&1 &` + 短轮询** (★前台长 exec = 被掐的头号原因 · 上一趟就是 462s 死在写闸那一刻★) ★ · ★**单条 exec ≤ ~120 秒** ★ · ★**每 10 分钟至少一次写盘** ★ · ★**每落一件交付物就把 rc 追加进交卷单** ★ · ★**分片写完 `grep` 校验** ★ · ★**零写板 · 零落表 · 零改网表/脚表/BOM · 零外发 · 不替老板拍板 · 不自签 issue_log (★签字是 main 的活★)** ★
★**不许把整份大文件读进来** (★只 grep 你要改的那几行★)
