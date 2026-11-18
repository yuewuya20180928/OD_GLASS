# CROSS_SESSION_NOTE_2026-11-18.md

---

## ★★2026-11-18 01:1x · job 775d9893「ARS45 继续执行后继计划」· 本轮处置 ★★

★**本轮净动作 2 件 (★都是 main 自己的活·没碰别的 agent 的分片★)**:
- ★**验签 1 条**: ★**ISS-302 → `verified`** (★hw-lead cont1 01:03 交卷·交卷单 38,212 B·占位符 0·分片 12 条 ⇒ main 01:0x 独立复验通过★)
- ★**派活 1 条**: ★**ISS-304 → hw-lead** (★taskName `advance_iss304` · 会话 `agent:hw-lead:subagent:15263ad3` · 01:1x 起 status=**running**★)

★**★派活依据 (★为什么本轮能派·上一轮不能★)★**: ★**ISS-302 cont1 于 01:03 交卷 ⇒ 本 job 01:1x 落 `verified` ⇒ hw-lead 名额释放 ⇒ ISS-304 (★原本 status=open 排队·兄弟 job fb67af40 01:0x 新开★) 才进得了 `advance.py` 的 `internal`** ★ ⇒ ★**这正好复现了 MEMORY 铁律③「磁盘上已落表」与「这一单交卷了」是两件事 ⇒ 僵尸 fixing 的判定要看【交卷单填实 + 分片写 + 闸复跑 rc 落盘】★** ★

★**★与兄弟 job fb67af40 的分工 (★本轮实测·没有撞车★)★**:
- ★**fb67af40 (01:0x 那轮)**: 新开 ISS-303 (mech-lead·直接落 fixing·已派) + 新开 ISS-304 (hw-lead·落 open 排队) + 验签 ISS-300 + 重派 ISS-302 cont1 (hw-lead) ⇒ ★**它自己的 run 于 00:57 结束 ⇒ 本 job 01:1x 接手时它已不在跑** ★
- ★**本 job 775d9893 (01:0x~01:1x 这轮)**: 派前 `sessions_list` + `subagents list` 实查 ⇒ hw-lead 名下无 running 写会话 (★上一条 01:03 status=done★) ⇒ ★**不重复派 hw-lead 的 ISS-302 (★已交卷⇒改验签·不是重派★)· 不重复派 mech-lead 的 ISS-303 (★兄弟 job 已派·status=running★)** ★
- ★**派后 `subagents list` 复核**: ★**1 条 running (advance_iss304) · 一个 agent 一条 · 无重复** ★

★**★派活纪律 (★本轮照做★)★**:
- ★**先落 fixing 再 spawn** (★同一个 flock 内原子完成 `state/_apply_20261118_0110_cron775d_verify302_dispatch304.py` ⇒ 中间不留 open 窗口 ⇒ 兄弟 job 的 advance.py 看不见 ⇒ 不会重复派同一个 agent★) ★
- ★**幂等**: ★**脚本只在 status 符合时才动手 (★ISS-302 只在 `fixing` 时签·ISS-304 只在 `open` 时标·兄弟 job 先动了就跳过★) ⇒ 双跑安全** ★
- ★**派活前跑命令存在性闸**: ★**`python3 state/check_brief_commands.py` ⇒ 3 份 brief 全 rc=0** ★
- ★**零外发**: ★**本 job 与子会话都没发任何邮件/询价/问询/采购 ⇒ 符合老板 2026-11-11 19:31 + 2026-11-12 02:02 口径** ★

★**★本轮 10 道闸独立复扫 (★main 01:0x 实跑·原样 rc·不抄任何 agent 报告★)★**:
| 闸 | rc | 读数 |
|---|---|---|
| `HW/check_netlist_selfconsistency.py` | **0** | ★**ISS-302 落表没打断网表自洽** ★ |
| `HW/check_land_row_anchors.py` | **0** | ★**落表台账锚点链绿 ⇒ 落表没把锚链打断** ★ |
| `HW/check_onepass_preflight_coverage.py` | **0** | ★板侧项全集与作业包对齐★ |
| `MECH/check_onepass_struct_crosscheck.py` | **0** | ★**01:0x 已转绿 (是 ISS-303 那侧动的)** ★ |
| `SW/tools/check_demo_panel_spec.py` | **0** | ★R1~R7 全过★ |
| `HW/check_pin_function_labels.py` | 1 | ★15 条 = **既有缺陷基线** (★5 基线一致 + 3 基线台账可查 ✔ ⇒ 落表没打断它·不许动它·ISS-299 重锚成果★) ★ |
| `HW/check_workpack_state_values.py` | **1** | ★**V4 4 条红 ⇒ ISS-304 (本轮已派)** ★ |
| `HW/check_onepass_commit_order.py` / `check_workpack_state_values --selftest` 等 | 0 | ★全绿★ |
| `state/gate_check.py` | **1** | ★Q1 **18/18** · ★**Q7 钉板 md5 闸链 8/9** ⇒ 红 = 钉板闸⑥ (ISS-304) ★ |
| `state/issue_check.py` / `state/merge.py` | **0** | ★全过 (★300 条 · 逾期 0 · 违规 0★) ★ |

★**★★本轮挖出的【落表跳假红】第 2 个洞 (★⇒ 补进 MEMORY 铁律的配套清单★)★★**:
- ★**ISS-302 的合法落表跳 (网表/脚表/BOM 三个 md5 变) 让 2 道闸当场假红**: ① `HW/check_workpack_state_values.py` V4 4 条 (★**页面里的 `fresh` 原句停在 ISS-283 那一跳★** ⇒ **ISS-304**) ② `MECH/check_onepass_struct_crosscheck.py` N6 (★**只认硬基线常量·分不出「合法落表」与「有人手改」★** ⇒ **ISS-303**) ⇒ ★**连带 `MECH/check_onepass_mech_release.py` 汇总 绿5/红1** ★
- ★**⇒ 铁律配套 (★可复用★): 落表之后必须有一道固定动作 —— 【全闸扫一遍 + 把「因这次落表而红」的闸逐条点名归单】★ ⇒ 不然每落一次表就被咬一次, 而现场极可能误读成「板改坏了」⇒ 去改板凑绿 ⇒ 板 md5 变第二次 ⇒ 整趟白跑** ★
- ★**⇒ 且「闸」这一侧要两种通道都接上**: ★**【合法改板跳】(板 md5 变·ISS-296/297/298 已接) + 【合法落表跳】(网表/脚表/BOM md5 变·本轮才暴露缺口·ISS-303/304 在补)** ⇒ 只接一半 = 每次落表都被咬** ★

★**★验签 note 的写法 (★MEMORY 铁律② 的本轮实例·照做★)★**: ★**ISS-302 的验签 note 同时写了三样** ⇒ ★**① 交付时读数 (00:53~00:58 复跑: gate_check rc=1 · Q7 8/9 · MECH 汇总 绿5/红1) ② 现在读数 (01:0x: MECH N6 已转绿 rc=0 · workpack 仍红) ③ 归属单 (钉板闸⑥ → ISS-304 · MECH N6 → ISS-303)★** ⇒ ★**⇒ 所以「ISS-302 已 verified」不等于「板那一趟可以开工」★**

★**★队列现状 (★下一轮接手的人先看这里★)**:
- ★**在飞**: ★**ISS-304 (hw-lead · 01:1x 派出·跑钉板闸⑥重锚)** · ★**ISS-303 (mech-lead · 兄弟 job 01:1x 派出·跑 MECH N6·01:0x 已转绿待交卷)** ★
- ★**已 verified (本轮 + 兄弟 job)**: ISS-300 (MECH 侧准出汇总闸) · ISS-302 (C_SYS / SYS_CHG 落表) ★
- ★**sw-lead**: 无 fixing · 无 open ⇒ ★**空转** ★
- ★**owner=main 的 12 条 open** (★ISS-109/125/126/128/129/130/131/133/155/156/160/169★) ⇒ ★**三个总工都接不了 (owner 不是它们) ⇒ 要 main 或老板处理** ★

★**★待拍板面 (★本 job 01:1x 实跑★)**:
- ★**`state/advance.py --json` ⇒ `internal: 0` (★派之前的状态·已由本 job 派掉 ISS-304 后空转★) · `approvals: []` (★恒空·19:31+02:02 政策★) · `decisions: **44**` · `waiting: []`** ★
- ★**44 条一条没动** (★44/44 逐 key 在决策页命中·脚本跑★) ⇒ ★**分布: 逾期 33 · 剩 0~2 天 2 (★`iss206_...scheme_choice` + `boss_dled_g_expose_decision_20261117` · due 11-18★) · 无 due 9** ★ · ★**来源: hw 8 / mech 18 / pm 10 / sw 8** ★
- ★**决策页已刷第 27 节 (`§A-补27 · r65`)** ⇒ ★**「板那一趟」开工前必须拍的 7 条短名单仍在 §A-补22 ② · 原样保留·本轮一个字没改** ★

---

## ★★2026-11-18 01:1x · job 775d9893「ARS45 继续执行后继计划」· 本轮处置 (★本 job 自记·与上面那节并列★)★★

★**派活 1 条 + 验签 1 条 (★详见上一节·此处只记本 job 自己的动作★)**:
- ★**ISS-302 → `verified`** (★main 01:0x 独立复验: 交卷单 38,212 B · 占位符 0 · B1~B6+§⑦ 齐全 · 分片 12 条 · 网表/脚表/BOM 三件 md5 与台账 §19 六项对齐 · 板 md5+mtime 双证零写板★)
- ★**ISS-304 → hw-lead** (★先落 fixing 再 spawn·同一 flock 内原子·幂等★)

★**本 job 的 5 连核验 (01:0x 实跑·原样 rc)**: merge **0** (★产出 552 · 阻塞 43 · 未闭合需求 316 · 冲突 0·健康度 red★) · gate_check **1** (★Q1 18/18 · Q7 8/9 ⇒ 红=钉板闸⑥=ISS-304★) · issue_check **0** (★300 条·逾期 0·违规 0★) · stage_gate **1** (★当前 G1·还差 1 项 = PCB 布线 unc 45→0·G1a 还差 G1a-4/G1a-8★) · daily_check **3** (★异常 2 条老账: PCB↔网表等价 + 生产链准入★)
★**本地快照**: `PROGRESS_SNAPSHOT.md` (★01:03 重出★) ⇒ ★**本 job 不推 GitHub (★由 5 小时同步 job 负责★)** ★

---

## ★★2026-11-18 01:2x~01:5x · job 775d9893「ARS45 继续执行后继计划」· 本轮处置 (★本 job 自记★)★★

★**本轮净动作 4 件 (★全在 main 自己的活域·没碰别的 agent 的分片·零外发★)**:
- ★**验签 2 条**: ★**ISS-303 (mech-lead) + ISS-304 (hw-lead) ⇒ 都落 `verified`** (★main 本机独立复跑·原样 rc·不抄 agent 报告★)
- ★**自办 1 条**: ★**ISS-131 (owner=main) open → fixing** (★RK3572 口径自查·交付页 + 机器可复核脚本·零写板零落表零外发★)
- ★**开单并派出 1 条**: ★**ISS-305 (owner=hw-lead) status 直接落 fixing ⇒ spawn `advance_iss305`** (★会话 `agent:hw-lead:subagent:596715d6`·01:4x 起 running★)
- ★**决策页追加 §A-补28 (r66)** + ★**本地快照 `PROGRESS_SNAPSHOT.md` 01:37 重出 (★不推 GitHub★)**

★**★★本轮最重要的读数变化: 钉板闸链 8/9 → 9/9 全绿 (★`state/gate_check.py` rc=1 → 0★)★★** ⇒ ★**「板那一趟」的【机器前置】全清了 ⇒ 剩下的阻塞只有两类: ①老板手上那 7 条 (§A-补22 ②·原样未改) ②G1 自己的 PCB 布线 unc 45→0 (ISS-181·deferred·真动板那一趟本体)★**

★**★ISS-304 那个 timeout 会话怎么判的 (★MEMORY 铁律③ 的本轮实例★)★**:
- ★**会话 `agent:hw-lead:subagent:15263ad3` status=timeout · abortedLastRun=true · 最后一句停在「Now the fragment write (atomic, via frag_write.py)」⇒ 看起来像僵尸★**
- ★**但盘面 5 件全在**: 交卷单 25,715 B (01:19) · `logs/iss304/` 13 个日志 (01:16~01:20) · 分片 `grep -c iss304 state/fragments/hw.yaml` = **9** (≥5) · 闸复跑 `13_q7_final.log` 写明 **9/9** ★
- ★**⇒ 判「真交卷」不判「僵尸」** ⇒ ★**main 01:2x 独立复跑后落 verified** ⇒ ★**铁律③ 再确认一次: 判定看【交卷单填实 + 分片写 + 闸复跑 rc 落盘】, 不看会话 status 单点★**

★**★ISS-131 本轮挖到的【官方 datasheet 自查法】(★可复用★)★**:
- ★**官方 RK3572 datasheet Rev 1.1 项目内已留存** (`HW/RK3572_PIN_TABLE/RK3572_datasheet_V1.1.pdf` 2,414,580 B + 解析出的 `.txt` 143,755 B) ⇒ ★**「自己查官方手册/引脚表」这条政策在 RK3572 上是【本地可做】的, 不用联网★**
- ★**★球位表有两行排版坑 (★我踩了 3 次才过★)★**: ① 球位命名 `A19` / `1B14` / `AM32` ⇒ 正则必须允许 `[0-9]?[A-Z]{1,2}[0-9]{1,2}` (只写 `[A-Z]\d{1,2}` 会漏掉 AM32) ② datasheet 的球位表**信号名会断行** (L1587~L1589: 信号名两行 + ball 单独一行) ⇒ ★**判据必须用「ball 锚点 ±3 行窗口」而不是「信号名同行」★**
- ★**★查出的硬事实★**: ① 球位号 **11/11** 与官方 datasheet 逐条对上 (含 A22/B22/A23/B23 四条「同球双名」·官方 L1789 逐字 `MIPI_DPHY_CSI0_RX_D2P/MIPI_DPHY_CSI1_RX_D0P A22` ⇒ 这就是「一个 4-lane 口可配 2×2」的物理证据) ② 官方 §1.2.7 逐字 `Support 2 MIPI CSI-2 interfaces` / `Two 4 data lanes of D-PHY v1.2` / `Each interface may be configured as 2x2 data lanes port` ⇒ 物理 = 2 个 4-lane D-PHY 可拆 4 个 2-lane 口 ⇒ **我方网表只用 `CSI_D0` 一路 ⇒ 口径差异对我方板无约束** ③ 官方 §1.2.8 逐字 `One channel ISP,12M pixels` / `Maximum input:4096x3072` ⇒ **4096×3072 = 12.58 Mpixel ⇒ 「12M」是单帧分辨率上限, 不是 MP/s** ⇒ 我方 1080p60 分辨率维度不卡, 但 **MP/s = [0数据]** ⇒ **换芯到 RK3572 后这条缺口没变好也没变坏**
- ★**★带出的一条新硬约束 (★唯一带推算成分的·已派 ISS-305 专门挑★)★**: `One channel ISP` ⇒ **同一时刻只有 1 路传感器能进 ISP** ⇒ **多摄方案在 RK3572 上不成立** ⇒ ⇒ 要进 demo 选型硬判据 (ISS-156)
- ★**⇒ 交付页 `HW/RK3572_INQUIRY_CALIBER_V2.md` (6,007 B) + 脚本 `state/_iss131_crosscheck_rk3572_caliber.py` (rc=0·只读)★**

★**★「自建脚本也得自测」的教训 (★本轮 3 个真 bug 都是我自己写的★)★**:
- ★**① `conn = "P" + m.group(1)` ⇒ 拼成 `PP4`** ⇒ 11 条全「查不到」★ (★教训: 正则捕获组拼串时, 先把捕获组原样打印出来看一眼★)
- ★**② datasheet 正则只认「信号名同行」⇒ 跨行排版全漏** ★
- ★**③ 球位正则只认单字母前缀 ⇒ 漏 `AM32`** ★
- ★**⇒ 教训: 自己写的核对脚本, 在它给出「全部对不上」时, 先怀疑自己 ★★别急着说「盘面坏了」★★** (★这跟 MEMORY 里那条「多个臂同时失败 ⇒ 先查共享的东西」是同一种思维★)

★**★本轮 5 道核验闸 (★main 01:5x 实跑·原样 rc★)★**:
| 闸 | rc | 读数 |
|---|---|---|
| `state/merge.py` | **0** | 产出 **561** · 阻塞 43 (高危 33) · 未闭合需求 **321** · 冲突 0 · 健康度 red |
| `state/gate_check.py` | **0** | ★**Q1 18/18 · Q7 钉板 md5 闸链 9/9 全绿** ★ (★上轮 8/9★) |
| `state/issue_check.py` | **0** | 301 条 · 逾期 0 · 违规 0 |
| `state/stage_gate.py` | **1** | 当前 **G1** · 还差 **1** 项 (★PCB 布线 unc 45→0★) · ★G1a 还差 2 条 (G1a-4 / G1a-8)★ |
| `state/daily_check.py` | **3** | 异常 2 条老账: ① PCB↔网表逐焊盘等价 (★3 条多余/异网**全部对应 §A-补22 ② 的第 1/2/4 条* ⇒ 老板一拍就清零★) ② 生产链准入/准出 (★环 ③ 红 ⇒ 环 ⑤ 连带红 ⇒ 板那一趟重出时一起清★) |

★**★板零写板 (md5 + mtime 双证·01:5x 实读)★**: 板 `611b869e13518c3c023fb178f91a0075` · mtime 仍 `2026-11-06 07:07:17` · `.kicad_pro` `3e504d2b…` · mtime `2026-11-04 23:47:30` ⇒ ★**本轮 4 件动作一条板都没动** ★

★**★分片纪律自检 (★本轮实测★)★**: 本 job 只写 `state/fragments/pm.yaml` (★main 自己·走 `frag_write.py --agent main`·+4 条·`grep -c iss131` = 4★) ⇒ ★**hw.yaml / mech.yaml / sw.yaml 三 个分片 `grep -c iss131` = 0/0/0** ★

★**★队列现状 (★下一轮接手的人先看这里★)★**:
- ★**在飞**: ★**ISS-305 (hw-lead · 01:4x 派出·跑「独立复验 ISS-131」·会话 `agent:hw-lead:subagent:596715d6`·01:5x 实测 running★) ★
- ★**待验签**: ★**ISS-131 (owner=main · status=fixing · 等 ISS-305 交卷后 main 签) ★**
- ★**刚 verified**: ★**ISS-303 (mech-lead · N6 判决源) + ISS-304 (hw-lead · 钉板闸⑥) ★**
- ★**sw-lead**: ★**名下 open=0 · fixing=0 ⇒ 仍是队列真空★**
- ★**owner=main 的 open**: ★**11 条** (★ISS-109/125/126/128/129/130/133/155/156/160/169·ISS-131 已转 fixing⇒ 剩 11 条·其中 8 条 are「属 PCB/板类·排队等板那一趟」·ISS-109/125 due 11-19 是唯二现在能干的·且 ISS-131 已把 131 的核心答案查完★)★

★**★待拍板面 (★本 job 01:5x 实跑·与上一轮完全一致★)★**: `state/advance.py --json` ⇒ `internal: 0` (★真排空·不是漏派·三个总工名下无 open 单★) · `approvals: []` (★恒空·19:31+02:02 政策★) · `decisions: **44**` · `waiting: []` ★ ⇒ ★**44 条一条没动 · 44/44 逐 key 在决策页命中 (脚本跑·不是目测)★**


---

## ★★2026-11-18 03:1x~03:2x · job fb67af40「ARS45 队列自动派活」· 本轮处置 ★★

★**派活 1 条 (★本 job 第一轮「开新单」而不是「派旧单」·理由在下面★)**:
- ★**ISS-307 → hw-lead** (★先落 fixing 再 spawn · 同一 flock 内原子 · 幂等★) · 会话 `agent:hw-lead:subagent:37a9cc96` · taskName `advance_iss307` · 03:1x 起 status=**running** ★
- ★**brief = `state/dispatch_briefs/ISS-307_hw_esd_dual_channel_candidates.md` 全文 · 已过命令存在性闸 `python3 state/check_brief_commands.py --brief-file` ⇒ rc=0** ★
- ★**开单脚本 = `state/_apply_20261118_0325_cronfb67_open_iss307.py`** (★issue_log 备份 `.bak_20261118_0325_cronfb67_open_iss307` + dispatch_log 同批落★)

★**★为什么这轮是「新开单」而不是「派已有 open 单」(★本机实跑, 不抄任何 agent 报告★)★**:
- ★**队列已排空**: `python3 state/advance.py --json` ⇒ `internal: []` ⇒ issue_log 实读 303 条里 open=16 (★owner 全是 boss/main★) · fixing=2 (ISS-131 owner=main · ISS-307 owner=hw-lead) ⇒ ★**三个总工名下 open=0** ★
- ★**子会话全空**: `subagents list` ⇒ active 0 · recent 0 ⇒ ★**不是「有在跑的会话所以跳过」, 是真的没活可派** ★
- ★**派活候选来自机器自己**: `state/gate_check.py` 的【缺口清单】段原文写着「★**(可直接转成下一轮派活项)**★」⇒ 实测 7 条 ⇒ 其中 4 条是同一条债 (★hw-lead 最新交卷单缺 B2/B3/B4/B5 ⇒ **Q1 = 14/18**★) ⇒ ★**成因 = main 03:0x 刚修了 gate_check 的「回退不许掩盖真倒退」(新增 `_uses_b_blocks` 判定) ⇒ 它把真债露出来了** ★

★**★但本单没做成「补 B 块」那种文档活 (★为什么值得一个总工的预算★)★**:
- ★**main 03:1x 逐道复扫 10 道闸全绿**: netlist_selfconsistency / land_row_anchors / onepass_preflight_coverage / MECH struct_crosscheck / SW demo_panel_spec / workpack_state_values / onepass_commit_order / MECH mech_release / bq25896_pinout 全 rc=0 (★只有 check_pin_function_labels rc=1 = 既有基线·ISS-299 明确不许动★) ★
- ★**⇒ 板那一趟的机器前置全清 ⇒ 剩下的红只有两类: ①老板的 4 个字母 ②板那一趟本体 (unc 45→0)★** ★
- ★**★而那 4 个字母里有 2 个 (W-2 补不补 D− / W-1b·W-1c 真 OPN 型号轴) 全落在 ESD 选型轴上 ⇒ 【选型候选 + 官网证据 + 落位可行性】谁都没交过 ⇒ ⇒ 老板现在【拍不了】这两个字母, 因为他手上没有候选集 ⇒ 这才是本单存在的理由★** ★

★**★本单实测出来的地基事实 (★pcbnew / 网表 / 台账 实读, 原样★)★★**:
- ★`D_ESD_USB_D` @ (94.95, 21.80) · **2 焊盘** · Value `ESD 阵列 [待选型] (USB 2.0 双通道)` · `J_USB_C` @ (140.00, 5.25) · 18 焊盘 · 板框 160×100 (x 0..160 · y 0..100) ★
- ★**距 `J_USB_C` 8 mm 以内除它自己外没有别的元件** ⇒ 周边是空的 (★对「3 脚件塞进 3.0 mm 判据半径」是好消息, 但仍要 hw-lead 自己给几何证据★) ★
- ★网表: D− 两张网 (`USB_D_N_SRC` / `NET_USB_D_N_TYPEC`) 上 ESD 位号数 = **0** ⇒ D− 裸奔 (实测) · `D_ESD_TC` (SP0503BAHT 3 通道 SOT-143) 挂在 VBUS 三张网上 ⇒ **不碰 D+/D−** ★
- ★★**台账内部有一处硬矛盾 (★本单第一问★)**: `HW/SCHEMATIC_LANDING_V1_LANDED.md` **L166 (B-3) 要求 `D_ESD_USB_D` 换 3 脚封装 (pin1=D+/pin2=D−/pin3=GND)**, 但同台账 **L934 的落表真源型号 = `TPD1E05U06DPYR` = TI 单通道 X1SON-2 (2 脚)** ⇒ ★**2 脚件物理上接不了 D− ⇒ 「落表型号」与「作业包要求的封装」自己打架 ⇒ 这就是「型号轴必须拍」的实物根据** ★
- ★台账 L167 (B-4): 挪到 `J_USB_C` 旁 ≤3.0 mm (现距 47.99 mm) ⇒ 挪位 ⇒ 布线重跑 ⇒ 必须同趟 · L168 (B-5): D− 必须补 (「Type-C 是 4 条里唯一的『用了就可能坏』」) ★
- ★**兄弟单 ISS-306 (sw-lead · 已 verified) 的结论被直接引用**: ① W-2 一落 ⇒ R4 两条红自动转绿 ⇒ 只有老板选「不补」才需另开一条修闸单 ⇒ ★**⇒ 路径乙的「判据口径改法草案 (判据不许偷偷放宽)」也是本单交卷物** ★

★**★派活纪律 (★本轮照做★)★**:
- ★**先落 fixing 再 spawn** (★同一 flock 内原子完成 ⇒ 中间不留 open 窗口 ⇒ 兄弟 job 775d9893 的 advance.py 看不见 ⇒ 不会重复派同一个 agent★) ★ · ★**幂等** (★脚本只在 ISS-307 不存在时才开单★) ★
- ★**派活前跑命令存在性闸**: ★`python3 state/check_brief_commands.py --brief-file state/dispatch_briefs/ISS-307_hw_esd_dual_channel_candidates.md` ⇒ **rc=0** ★
- ★**派后 `subagents list` 复核**: ★**1 条 running (advance_iss307) · 一个 agent 一条 · 无重复** ★
- ★**零外发**: ★**本 job 与子会话都没发任何邮件/询价/问询/采购 ⇒ 符合老板 2026-11-11 19:31 + 2026-11-12 02:02 口径★** ★
- ★**零写板**: ★**本轮本 job 只写了 state/ 下 3 个文件 (brief / apply 脚本 / 本笔记) + issue_log + dispatch_log ⇒ 板 md5 `611b869e…` mtime `2026-11-06 07:07:17` 一字未动** ★

★**★队列现状 (★下一轮接手的人先看这里★)★**:
- ★**在飞**: ★**ISS-307 (hw-lead · 03:1x 派出·ESD 选型轴候选集)** ★
- ★**待 main 验签**: ★**ISS-131 (owner=main · status=fixing · 其复验单 ISS-305 已 verified ⇒ 复验链最后一环已备好, 等 main 签)** ★
- ★**sw-lead / mech-lead**: ★**名下 open=0 · fixing=0 ⇒ 本轮无活可派 (★MECH 6 闸全绿 / SW 闸全绿 ⇒ 没有可派的红闸 ⇒ 不硬造活★)** ★
- ★**owner=main 的 open**: ★**11 条** · ★**owner=boss 的 open**: ★**5 条** (★全部决策类, 等老板★) ★
- ★**待拍板面 (本 job 03:1x 实跑)**: ★`state/advance.py --json` ⇒ `internal: []` (★排空是本 job 派掉 ISS-307 的结果·不是漏派★) · `approvals: []` (★恒空·19:31+02:02 政策★) · `decisions: **44**` · `waiting: []` ★

---

## ★★2026-11-18 04:2x~04:4x · job fb67af40「ARS45 队列自动派活」· 本轮处置 ★★

★**派活 1 条 (★本轮是「开新单」而不是「派旧单」·理由在下面★)**:
- ★**ISS-308 → hw-lead** (★先落 fixing 再 spawn · 同一 flock 内原子 · 幂等★) · 会话 `agent:hw-lead:subagent:56d88b87` · taskName `queue_iss308` · 04:3x 起 status=**running** ★
- ★**brief = `state/dispatch_briefs/ISS-308_hw_s8_reachability_verdict.md` 全文 · 已过命令存在性闸 `python3 state/check_brief_commands.py --brief-file` ⇒ rc=0** ★
- ★**开单脚本 = `state/_apply_20261118_0430_cronfb67_open_iss308.py`** (★issue_log 备份 `.bak_20261118_0430_cronfb67_open_iss308` + dispatch_log 同批落★)

★**★为什么这轮是「新开单」(★本机实跑, 不抄任何 agent 报告★)★**:
- ★**队列已排空**: `state/advance.py --json` ⇒ `internal: []` ⇒ issue_log 实读 open=16 (★owner 全是 boss=5 / main=11★) · fixing=0 ⇒ ★**三个总工名下 open=0** ★
- ★**子会话全空**: `subagents list` ⇒ active 0 ⇒ ★**不是「有在跑的会话所以跳过」, 是真的没活可派** ★
- ★**机器前置全清**: `state/gate_check.py` rc=0 (★Q1 18/18 · Q7 钉板 md5 闸链 9/9 全绿★) · `state/issue_check.py` rc=0 ⇒ ★**板那一趟开工前机器能挡的都挡住了 ⇒ 剩下的红只有两类: ①老板的字母 ②S8 本体 (unc 45→0)★** ★

★**★本单攻的是②: 「板只改一次」铁律下 S8 是死穴 (★main 04:2x~04:3x 实测★)★**:
- ★**现役板实测**: `bash state/pcbnew_py.sh state/check_pcb_drc.py HW/PCB/demo_mainboard.kicad_pcb` ⇒ rc=0 · ★**C4 unconnected items = 45** · C3 DRC=0 · C7 同点重复过孔=0 · Gerber 32 个 ★ ⇒ 板 md5 `611b869e…` mtime `2026-11-06 07:07:17` (★本单零写板★)
- ★**作业包 §3-S8 原文**: 「45 条里 23 条是高速 DSI/CSI 腿, 全部要跨 SoM 主体 (x 8..76, y 6..56)」+ 「官方板这 13 条 DSI 腿自己一根都没布通」+ 「其余 22 条死因登记 = ISS-265 §6 的 5 条 (A1/W-1/W-2/W-4/D_LED_G/FSIN_OUT)」+ ★**「这是本单唯一一个『可能整趟做完仍然投不了板』的步」** ★
- ★**盘上【没人写下来过】的现象 (★本单第一问★)**: ★**残余 22 网名里差分类绝大多数是【N 腿】** ⇒ 「P 通 N 不通」= 【层分配】症状 ⇒ 而路由器源码里【正好有】专门治它的 `PCB_PAIR_LAYERSEL` (★env 门控·默认关★) ⇒ ★**而 `state/UNC_TARGET_MAP.md` 只写了一句「目前无效但无害」⇒ 谁写的/哪天的/有没有实测支撑 = 未知** ★
- ★**臂史**: `state/ARM_LEDGER_2026-11-10.md` ⇒ ★**33+ 个臂全停在 unc 24~29 / DRC 0~1 ⇒ 参数调优到平台期 ⇒ 根因在布局/机制, 不在参数 (MEMORY 铁律★)★** ⇒ ⇒ 本单要交【机制级判决】, 不是【再来一个臂】 ★

★**★本单纪律 (写进 brief 的硬约束)★**:
- ★**纯分析/作业包类 · 零写板 · 零落表 · 零改闸 · 零改网表/脚表/BOM · 零改既有作业包与清单页正文 · 零外发 · 不替老板拍板 · 不自签 issue_log** ★
- ★**不许新跑布线臂** (★本单是分析/判决单; 时间预算按上批 570~1360 s 被掐的经验 ⇒ 【交卷优先, 缺口写进 B5】★) ★
- ★**交卷物 3 件全新建**: `HW/PCB/S8_REACHABILITY_VERDICT.md` · `HANDOFF/2026-11-18_hw-lead_ISS308_S8可达性判决书.md` (★标准块 B1~B6 ⇒ Q1 必须 18/18★) · `state/_iss308_s8_reachability_check.py` (★只读 + `--selftest` 反向用例★) ⇒ 只写 `state/fragments/hw.yaml` (★`frag_write.py`·`grep -c iss308` ≥ 5★) ★
- ★**三问**: ①残余 22 网名逐条落 5 桶 (老板字母/GND 卡死/差分 N 腿/让路闸靶子/其它) ②★**老板还差 N 个字母 (N 必须是具体数字; N=0 就明写 0, 不许凑数★)** ③现在就能做的技术活清单 (env 键 + 落铜前拦改法 + 落位增补表草案) ★

★**★派活纪律 (本轮照做)★**:
- ★**先落 fixing 再 spawn** (★同一 flock 内原子 ⇒ 中间不留 open 窗口 ⇒ 兄弟 job 775d9893 的 advance.py 看不见 ⇒ 不会重复派同一个 agent★) ★ · ★**幂等** (脚本只在 ISS-308 不存在时才开单) ★
- ★**派活前跑命令存在性闸**: `python3 state/check_brief_commands.py --brief-file …` ⇒ **rc=0** ★ · ★**全量闸 (7 条待办单) rc=0** ★
- ★**派后 `subagents list` 复核**: ★**1 条 running (queue_iss308) · 一个 agent 一条 · 无重复** ★
- ★**零外发**: ★**本 job 与子会话都没发任何邮件/询价/问询/采购 ⇒ 符合老板 2026-11-11 19:31 + 2026-11-12 02:02 口径★** ★
- ★**零写板**: ★**本 job 本轮只写了 state/ 下 3 个文件 (brief / apply 脚本 / 本笔记) + issue_log + dispatch_log ⇒ 板 md5 `611b869e…` mtime `2026-11-06 07:07:17` 一字未动** ★

★**★队列现状 (下一轮接手的人先看这里)★**:
- ★**在飞**: ★**ISS-308 (hw-lead · 04:3x 派出 · 「板那一趟 S8 可达性判决书」· 会话 `agent:hw-lead:subagent:56d88b87` · running★) ★
- ★**sw-lead / mech-lead**: ★**名下 open=0 · fixing=0 ⇒ 本轮无活可派 (★各自的闸全绿 ⇒ 不硬造活★)** ★
- ★**owner=main 的 open**: ★**11 条** (★其中 8 条属 PCB/板类·排队等板那一趟·ISS-109/125 due 11-19 是唯二现在能干的★) ★
- ★**owner=boss 的 open**: ★**5 条** (★全部决策类, 等老板★) ★
- ★**待拍板面 (本 job 04:2x 实跑)**: ★`state/advance.py --json` ⇒ `internal: []` · `approvals: []` (★恒空·19:31+02:02 政策★) · `decisions: **44**` · `waiting: []` ★
