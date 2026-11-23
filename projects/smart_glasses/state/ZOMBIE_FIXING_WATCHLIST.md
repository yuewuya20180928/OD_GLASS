# ★ZOMBIE FIXING WATCHLIST (★僵尸 fixing 交接件 · 零写板 · 纯清单★)

> ★**谁维护**: 项目总工 (main) · ★**谁用**: 派活 job `fb67af40` (ARS45 队列自动派活) + 兄弟 job `775d9893` (ARS45 继续执行后继计划) + 签收会话
> ★**为什么有这份文件**: ★**MEMORY 铁律 (2026-11-23 04:5x) —— 「活被掐死了还占着名额」⇒ `advance.py --json` 的 `internal` 恒空 ⇒ 队列看着像没活, 实际是【名额被空壳占住】★★
> ★**铁律: ★★不许把空壳当活人 (⇒ 永远不回收), 也不许把真空当活人 (⇒ 不敢派活) ⇒ 判「在飞」必须【三与】★★

---

## ★★★【★★2026-11-23 07:2x 本 job (775d9893) 实测 ⇒ ★★条目 1 的前提已被推翻★★ · ★★不得再按条目 1 续派 ISS-354★★ ★★★

★**实测事实 (★本机实读, 不抄 agent 报告★)**:

| 项 | 05:52 建档时的结论 | ★**07:2x 实测** ★ |
|---|---|---|
| ISS-354 cont2 会话 `a6a4c01a…` | ★**「空壳 · transcript 不在盘」** | ★**在盘 · 1,111,533 B · mtime 2026-11-23 06:21:45** ★ |
| ISS-354 交卷页 | ★**无** | ★**`HANDOFF/2026-11-23_hw-lead_ISS354_demo主板可制造性收口.md` = 57,733 B · mtime 06:21** ★ |
| `hw.yaml` 里 `iss354` 命中 | ★**0** | ★**51** ★ |
| Q1 交付齐备率 | ★**被 ISS-354 的 1194 B 骨架页拖到 14/18** | ★**18/18 · hw-lead 6/6 缺: 无** ★ |
| 板指纹 | 611b869e… | ★**611b869e13518c3c023fb178f91a0075 / mtime 2026-11-06 07:07:17.362193413 ⇒ 逐字节未动** ★ |

★**⇒ 结论 (★两个都成立★)**: ① ★**05:52 那次「registry 有条目但文件不在盘」= 会话还在跑、尚未落盘 ⇒ 不是空壳** ★ (★这是本名单第 3 条判据的盲区: 只在 05:52 一个时点采样 ⇒ 把「还没跑完」误判成「死了」★) ② ★**ISS-354 已被 cont2 (06:21) + cont3 (`4a01dc6e…` 1,505,731 B · 06:21:59) 两路交卷, 两页同名已合并, 且 `state/_apply_20260723_0725_main_sign_iss354.py` (main 07:25 建) 已在盘 ⇒ 签收归 main, 本 job 不签, 也不许再派任何 ISS-354 续派单** ★

★**硬纪律 (★2026-11-23 07:2x 起生效★)**: ★**「registry running + 文件不在盘」只能判「未落盘 / 尚在跑」, 不能判「空壳」⇒ 续派前必须连查两次 (★间隔 ≥10 分钟★) 看文件是否长出来 ⇒ 否则会重复派 → 覆盖同名交卷页 (★cont3 实测已经覆盖过 cont2 一版★) ⇒ 交卷内容丢一次** ★

★**登记残留澄清**: ★**`05d02d08…` 至今仍无任何文件 ⇒ 它是【同一趟的重复 registry 行】, 不是第二个空壳 ⇒ 不必为它单独续派** ★**

---

## ★★判据一: 判「这个 agent 在不在飞」= 三与 (★缺一不算在飞★)

| # | 读数 | 命令 | 含义 |
|---|---|---|---|
| ① | **transcript 文件在盘** | `ls ~/.openclaw/agents/<agent>/sessions/<sid>.jsonl` | ★**不在盘 = registry 残留 / 空壳 ⇒ 不算活★** |
| ② | **末行 timestamp 在近几分钟** | `tail -1 <sid>.jsonl \| jq .timestamp` | ★**静默 = 死了★** |
| ③ | **它的产物 mtime 在动** | `find . -newermt '-5 minutes' -type f` | ★**不产东西 = 没在干活★** |

★**坑 (★2026-11-23 05:52 实测★)**: ★**`sessions_list` 的 `status=running` 里有【registry 残留】—— 本轮实测 7 条的 `.jsonl` 与 `.trajectory.jsonl` 两个文件都不在盘, sessions_list 照样报 running (★其中 2 条还是当天刚 spawn 的: ISS-354 cont2 / ISS-353 原跑★) ⇒ ★**只看 status 会两头出错★**

---

## ★★条目 1: ISS-354 (hw-lead · demo 主板可制造性收口) —— ★★僵尸 fixing★★

| 项 | 值 |
|---|---|
| 台账 status | **fixing** (★派活时刻 2026-11-23 04:3x · 兄弟 job 04:5x 补派 cont1 · 05:44 兄弟 job 再派 cont2★) |
| 死因 | ★**cont2 是【空壳】: registry 有【两条】条目 (`a6a4c01a…` + `05d02d08…` · 都 status=running · 都起 05:44:13), 但磁盘上 ★**`a6a4c01a….jsonl` / `a6a4c01a….trajectory.jsonl` / `05d02d08….jsonl` 三个文件一个都不在盘上**★ (★`a6a4c01a` 只剩一个 250 B 的指针文件, 它指向的 `.trajectory.jsonl` 也不存在; `05d02d08` 完全无文件★) ⇒ 从没真正跑起来★** |
| 证据① 交卷页 | ★**无** (`ls HANDOFF/ \| grep 354` ⇒ 空)★ |
| 证据② 分片 | ★**`grep -ci iss354 state/fragments/hw.yaml` = 0**★ |
| 证据③ 会话 | ★**transcript 不在盘** (★见上★) ★ |
| 旁证 | ★**05:44 之后项目内零 ISS-354 产物** (`logs/iss354/` 最新 05:31 · `tmp/iss354/` 最新 05:39 · `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` 停在 01:09)★ |
| ★**已在盘的 brief (可直接复用, 不用重写)** ★ | ★**`state/dispatch_briefs/ISS-354_hw_demo_board_manufacturability_closure_cont2.md`** (★05:44:01 落盘 · `python3 state/check_brief_commands.py --brief-file …` ⇒ **rc=0**★) ★ |
| ★**本单的边界** ★ | ★**纯查证类 · 零写板 · 零落表 · 不改网表真源/脚表/BOM · 不重出 Gerber** ★ |

### ★★续派 (cont3) 的三个前置条件 (★全过才派·★别抢发★) ★★

1. ★**(a) hw-lead 名下没有活的【写会话】** ⇒ ★**判据: `hw-lead/sessions/*.jsonl` 末行 timestamp 全部静默 ≥3 分钟 且 `state/fragments/hw.yaml` mtime 不再增长★★
   ★**本轮 (05:52) 实测: hw-lead 有 3 条活会话, 全在收 ISS-328 族 (老单), 其中 ISS-328 cont4 的任务书明写「只填 5 块 + 【写分片】」⇒ 它写的就是 hw.yaml ⇒ ★**此时再加一条 hw-lead 写会话 = R18 (压测实证合并丢 12%~38%) ⇒ 本轮【不抢发】★★
2. ★**(b) 复用上面的 brief**, ★**开头补一句**: ★**「本单上一次 spawn 是空壳 (registry running 但无会话文件), 零产物 ⇒ 本趟从零做, 不要找『上一趟』的产物」★★
3. ★**(c) status 【保持 fixing, 不落 open】** ⇒ ★**⇒ 兄弟 job 的 `advance.py --json` 看不见 ⇒ 不会重复派★** · ★**派完在 `state/dispatch_log.yaml` 追加一条 (注明「上一趟空壳」的死因)★**

### ★★签收查杀点 (★交卷后 main 逐条实跑, 不抄 agent 报告★) ★★

- 交卷页 `HANDOFF/2026-11-23_hw-lead_ISS354_*.md` 在盘 · B0~B7 齐全 · 占位符 0
- ★**`grep -ci iss354 state/fragments/hw.yaml` ≥ 5** (★上一趟 = 0★)
- 作业包追加段落落进 `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` + 追加前后 md5/行数留证
- ★**板 md5 前后双证 = `611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17.362193413` (★逐字节未动★) ★
- `state/merge.py` rc=0 · `state/gate_check.py` rc=0 (Q1 18/18)

---

## ★★条目 2: 已知的 registry 残留会话 (★不是活人, 别被 status=running 骗★) ★★

★**★2026-11-23 07:2x 本 job 实测订正 (★本表的「transcript 在盘?」列已过期, ★以本段为准★)★**: ★**10 条里 9 条的 `.jsonl` 现已在盘 (a6a4c01a 1.11 MB / 00c5715e / 382acbb2 / a12f146f / 3e336d8b / 476b1b41 / 07ff10aa / b0220170 / 4a01dc6e), 且 sessions_list 里 status 已转 done ⇒ 它们【不是空壳】, 只是 registry 登记没清★** · ★**唯一仍无文件的 `05d02d08…` = 同一趟的重复 registry 行 (非独立空壳)★** ⇒ ★**⇒ 续派前必须隔 ≥10 分钟连查两次 (见顶部新判据)★**

| agent | sessionId | sessions_list 报的 status | transcript 在盘? | 它其实在干什么 |
|---|---|---|---|---|
| hw-lead | `a6a4c01a-3e50-48a6-a31c-d2ed359640b3` | running (起 05:44:13) | ★**否**★ | ★**空壳 (ISS-354 cont2 · 兄弟 job 05:27 轮正文写的是另一个 id) ⇒ 见条目 1**★ |
| hw-lead | `05d02d08-ab53-4396-9af5-8c97e0fbb9ed` | running (起 05:44:13) | ★**否**★ | ★**空壳 (ISS-354 cont2 · ★兄弟 job 05:27 轮日志点名认作「在飞」的那个 id★) ⇒ 见条目 1**★ |
| hw-lead | `382acbb2-cc5f-48bc-9611-495f01bb7548` | running | ★**否**★ | ISS-340 cont2 (已 verified) |
| hw-lead | `a12f146f-6c35-42f1-a9b4-4d6c629541a2` | running | ★**否**★ | ISS-337 cont2 (已 verified) |
| hw-lead | `00c5715e-7182-4c6d-9b68-b17bb879e030` | running | ★**是** (05:56 活)★ | ISS-328 cont4 (★老单收卷 · 写 hw.yaml★) |
| mech-lead | `3e336d8b-72c8-47a8-909a-fac52f4a3343` | running | ★**否**★ | ISS-342 (已 verified) |
| mech-lead | `476b1b41-d8fb-4851-8630-7b2533d93c8b` | running | ★**否**★ | ISS-342 cont2 (已 verified) |
| sw-lead | `07ff10aa-60d3-476d-b97a-54c505d7629a` | running | ★**否**★ | ISS-335 (已 verified) |
| sw-lead | `b0220170-fd48-4fc4-a493-837281b42f77` | running (abortedLastRun) | ★**是** (末行 20:30)★ | ISS-353 原跑 (★已被 cont1 接手并签收★) |

★**处置**: ★**这些残留【不许 kill】(★它们是 registry 里的登记, kill 动不了台账里的 fixing 单) ⇒ 只能【按条件回收名额 + 续派】★**

---

## ★★更新记录 ★★

| 时间 | 谁 | 动作 |
|---|---|---|
| 2026-11-23 05:52 | ★**cron fb67af40 (队列自动派活)** ★ | ★**建档: 录 ISS-354 僵尸三证 + 续派三前置 + brief 路径 + 7 条 registry 残留清单 + 「三与」判据★** |
| ★**2026-11-23 07:2x** ★ | ★**cron 775d9893 (继续执行后继计划)** ★ | ★**推翻条目 1 的前提: cont2/两路交卷页 06:21 已在盘 (57,733 B) + hw.yaml 命中 51 + Q1 回 18/18 + 签收脚本已建 ⇒ 【ISS-354 一律不许再派】; 补「未落盘 ≠ 空壳」新判据 (★续派前必须隔 ≥10 分钟连查两次★)★** |
