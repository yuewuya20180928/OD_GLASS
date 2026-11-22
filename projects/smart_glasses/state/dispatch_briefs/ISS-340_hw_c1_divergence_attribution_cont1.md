【ISS-340 · hw-lead · ★★cont1 · PCB 线 · 纯分析 + 新建判别闸 · 零写板 ★★】
★★**派活方 = 项目总工 (main) · cron fb67af40 (ARS45 队列自动派活) · 2026-11-22 22:1x** ★★
★★**cont1 = 上一趟 (2026-11-22 21:5x 派出) 被掐死后的【续做派活】· 任务书编号不变 (ISS-340) · 交付物编号沿用原书 D1/D2/D3/D4, 但本轮 D3 交卷页延后 (见 §-1-③)★★**
★★**完整原始任务书在 `state/dispatch_briefs/ISS-340_hw_c1_divergence_attribution.md` (11,676 B) ⇒ ★只在需要查某条硬判据原文时才按需查它, 不许从头通读 (★上一趟就是通读 + 探查把预算烧光才死的★)★★**

---

## §-1 ★★本轮三条硬纪律 (★顺序照做, 不许自己改★) ★★

### ① ★第一个工具调用 = write `logs/iss340/01_c1_verdict_table.md`★ (★不许先探查后落盘★)
★**你唯一允许的"探查"= 把 §-3 那三条已核事实各自复跑 1~2 条命令确认 (共 ≤ 6 条命令) ⇒ 然后立刻落盘判定表** ★
★**判定表内容 (5 条差异逐条一行, 写不出来就先写你能确定的那几行, 不许留空)** ★:
| # | 差异 (ref.pad → 网表应/板实) | 归桶 A/B/C | 证据 (网表文件+行号+内容 / 板上 pad+有没有铜+铜长mm) | 后果 (板那一趟要动什么 / 板 md5 动不动) |
|---|---|---|---|---|
| 1 | `C_VBUS_GND` pad1 (多) | | | |
| 2 | `C_VBUS_GND` pad2 (多) | | | |
| 3 | `Q_PG` pad1 (同号异网) | | | |
| 4 | `Q_PG` pad3 (同号异网) | | | |
| 5 | `D_ESD_USB_D` pad1 (同号异网) | | | |
★**归桶口径 (照抄, 不许自创)**: ★**A = 网表侧错 → 改网表就够, 板 md5 一个字节都不用动** ★ · ★**B = 板侧错 → 必须动板, 进板那一趟 B-清单 (那一趟一次做完)** ★ · ★**C = 等老板拍板 → 进待拍板页 (本单不代拍, 只列 need key + 题)** ★
★**末尾必须写一行**: 「板那一趟开工前必须先落哪几条」★

### ② ★§-3 三条事实是【免重探查】用的★ (★省下的时间全部用来落盘★)
★**上一趟 (21:5x 那趟) 已经把三条差异的根因挖出来了, 只是死在写盘之前** ⇒ ★**下面三条直接当底稿用 (每条你各自复跑 1 条命令确认一遍即可, 不许重新从头挖)** ★

### ③ ★本轮范围 = D1 判定表 + D2 判别闸 + D3 一页口径 + D4 logs+分片 · ★★交卷页 (B0~B7) 本轮【不写】★★
★**为什么交卷页延后**: ★**`state/gate_check.py` Q1 的 `pick_handoff()` 实测逻辑**: 一份**自称 B 块结构**的交接单若缺块 ⇒ ★**不回退** ⇒ Q1 从 18/18 打成 17/18 (★gate 自己把"真倒退"显式暴露, 不许用老单顶住★) ⇒ ★**⇒ 半页绝不许落盘 ⇒ 本轮干脆不落, 留给 cont2 一次写全** ★
★**⇒ 本轮交卷前 `python3 state/gate_check.py` 必须仍是 Q1 18/18 (因为盘上 newest 的 hw-lead 交接单仍是 ISS-339 那份齐全的)** ★
★**不写交卷页不算交卷失败** ⇒ ★**回复里如实写「交卷页本轮未写 (延后 cont2), 原因 = 怕半页把 Q1 打成 17/18」** ★

---

## §-2 ★★上一趟为什么死 (★本机实读 transcript, 不是猜★) ★★

★**子会话 `agent:hw-lead:subagent:cdc10bd9` (21:44~22:12)**: ★**40 条消息 · 475,385 tokens · 最后一条是 `openclaw:prompt-error`: `This operation was aborted` (provider=minimax / api=anthropic-messages)· `abortedLastRun=false`** ★
★**⇒ 死因 = 长上下文 + 一直在探查, 一次 write 都没落地** ⇒ ★**盘上零产出**: ★**`logs/iss340/` 不存在 · `HANDOFF/` 无 ISS-340 页 · 板 md5/mtime 逐字节未动** ★
★**⇒ 本轮的活儿只有一件事: 先落盘, 再谈别的** ★

---

## §-3 ★★三条已核事实 (★免重探查底稿 · 标 [待复跑确认]★) ★★

★**事实 1 · `C_VBUS_GND` 多余 2 条 [实测·main 本机实读 22:2x · 待你复跑确认]** ★
★**网表 `HW/netlist_v1.csv` L10/L12 这两行的 `board` 列 = `CHG_BOARD`** ⇒ ★**被生成器的 `BOARD_FILTER=MAIN_PCB` 过滤掉** ⇒ ★**对 MAIN_PCB 的 want 集合里根本【没有】C_VBUS_GND** ⇒ ★**板上(11-06)却还留着它的 2 个 pad (pad1=GND · pad2=VBUS_5V_CHG)** ★
★**⇒ ⇒ 判定方向: 这不是「网表多了一行」那么简单, 是【网表把该器件划给了充电板, 板侧还是 11-06 的】** ★
★**★关键: 归桶不是纯 A/B/C 一条, 是【C 桶 → 拍完才分 A/B】★** ★ —— ★**`state/fragments/pm.yaml` 的 `boss_c_vbus_gnd_reserve_pad_20261117` 条目 (★无 decided_at / 无 decision ⇒ 仍未拍板★) 里已经写全了权衡**: ★**「下板」⇒ 收工 185 件 ⇒ 板那一趟要把这个封装从板上拿掉 (B 侧动作) · 「留位」⇒ 收工 186 件 ⇒ 改网表 board 列 `CHG_BOARD`→`MAIN_PCB` + 重生成脚表/BOM (A 侧动作, 但板 md5 不用动)** ★ · ★**且它自己写明「不拍的代价 = 那一趟收工时 S2 必假红, 最坏 = 把 C_VBUS_GND 装回板上 = 2~4 周 + ¥4~8K 返工」** ★
★**⇒ 你要交的**: ★**把上面两条候选路径 (下板 / 留位) 各写清【动哪个文件的哪一行 / 要不要重出 Gerber / 要不要重生成脚表 BOM】⇒ 但【留还是不留】不代拍 ⇒ 归 C 桶, 只列 need key + 题 + 两条路径的代价** ★
★**复跑命令 (2 条)**: ★`grep -n "C_VBUS_GND" HW/netlist_v1.csv` ★ · ★`grep -n -A 12 "key: boss_c_vbus_gnd_reserve_pad_20261117" state/fragments/pm.yaml` ★

★**事实 2 · `Q_PG` 同号异网 pad1/pad3 [实测·main 本机实读 22:2x · 待你复跑确认]** ★
★**网表 L59/L60/L61 三行**: ★**net 列依次 = `PWR_GOOD` / `BAT_SW` / `PWR_ON`, 且三行的 node1 都是 `Q_PG` (无脚号 ⇒ 走占位脚序) ⇒ ⇒ Q_PG 的网表侧脚序 = 占位 1 = PWR_GOOD · 2 = BAT_SW · 3 = PWR_ON** ★
★**⇒ 与老板已拍的「写法 A」一致 (ISS-283 · G-1 裁决 · 2026-11-17 09:49 老板拍板 · 落表 2026-11-17 12:30:23)**: ★**DMP3098L 厂商引脚序 1=G / 2=S / 3=D ⇒ pad1=G=PWR_GOOD · pad2=S=BAT_SW · pad3=D=PWR_ON** ★
★**⇒ 板侧 pad1/pad3 对调 ⇒ 网表那一行 note 自己就写着「板上 `Q_PG` land 仍按旧接法画 ⇒ 板那一趟必须重画这 3 根线 (ISS-283 板侧清单 §③-2)」** ⇒ ⇒ ★**归桶 = B (板那一趟 · 重画 3 根线) · 单端低速 ⇒ 不触及高速/差分铜 · 但要重跑 DRC + 重出 Gerber** ★
★**⇒ 但 `Q_PG.3` 的极性另有一条队列外待拍项 `W-4 Q_PG.3 极性` ⇒ ⇒ ★那一条要单独判, 可能是 C (等老板) ★**
★**复跑命令 (1 条)**: ★`grep -n "Q_PG" HW/netlist_v1.csv` ★

★**事实 3 · `D_ESD_USB_D` pad1 同号异网 [实测·main 本机实读 22:2x · 待你复跑确认]** ★
★**网表侧 (3 行, ★注意列序: `page,net,node1,node2,ref,...`★)**:
| 行 | net | node1 | node2 | 读法 |
|---|---|---|---|---|
| L291 | `USB_D_P_SRC` | `J_SOM_P1 pin92` | `R_SER_USB_D_P` | ★**网表里这个网的真名就叫 `USB_D_P_SRC` (无 NET_ 前缀) · ref 列的 `NET_USB_D_P_SRC` 是 NET 伪器件** ★ |
| L417 | `NET_USB_D_P_TYPEC` | `D_ESD_USB_D` | `NET_USB_D_P_TYPEC` (伪) | ★**⇒ `D_ESD_USB_D` pad1 应当落 `NET_USB_D_P_TYPEC`** ★ |
| L431 | `NET_USB_D_P_TYPEC` | `R_SER_USB_D_P` | `J_USB_C A6+B6` | ★**⇒ 串阻的 Type-C 侧 = `NET_USB_D_P_TYPEC`** ★ |
★**板侧**: ★**板上叫 `USB_D_P_SRC` 的那个网共有 3 个焊盘: `R_SER_USB_D_P` pad1 · `D_ESD_USB_D` pad1 · `J_SOM_P1` 的 USB_D_P 脚 (★主文件行 5786 / 13016 / 18683★)** ★
★**★★纠正: 上一趟 (21:5x 那趟) 说的「3 处都要改」是错的 ★★** ⇒ ★**只有 `D_ESD_USB_D.pad1` 错** (★另两个 (R_SER_USB_D_P pad1 · J_SOM_P1 的 USB_D_P 脚) 在网表里本来就挂 `USB_D_P_SRC` ⇒ 与板一致 ⇒ 不用动★) ⇒ ★**⇒ 板那一趟要动的是【1 个焊盘 + 它那根 stub 的走向】: 把 `D_ESD_USB_D.pad1` 从 `USB_D_P_SRC` 挪到 `NET_USB_D_P_TYPEC` (串阻的 Type-C 侧) ⇒ 单端低速 ⇒ 不触及高速/差分铜 ⇒ 但要重跑 DRC + 重出 Gerber** ⇒ ★**归桶 = B** ★
★**复跑命令 (2 条)**: ★`grep -n "USB_D_P" HW/netlist_v1.csv` ★ · ★`grep -n "USB_D_P" HW/PCB/demo_mainboard.kicad_pcb | head -20` ★

---

## §-4 本轮交付物 (4 件 · ★每件 = 一次独立 write 调用 · 不许攒成大 edit★)

### D1 · ★新建★ `logs/iss340/01_c1_verdict_table.md` (判定表 · ★本轮第一件 · 最优先★)
★**内容 = §-1-① 那张表 + 每条一句话后果 + 末尾「板那一趟开工前必须先落哪几条」** ★

### D2 · ★新建★ `HW/check_board_netlist_divergence_gate.py` (判别闸本体 · ★只读★)
★**硬判据 (一条都不许少)**:
- ★**自己跑出 C1 三类差异 (多余 / 同号异网 / 缺失) ⇒ 不许照抄本任务书或上一趟的读数** ★ (★入口: `bash state/pcbnew_py.sh state/check_pcb_nets.py`★)
- ★**逐条归属 A / B / C 三桶** ★ · ★**每条带证据** (网表侧那行: 文件 + 行号 + 内容 · 板上那个 pad: ref + pad# + 实际网 + 有没有铜 + 铜长 mm) ★
- ★**末尾打 4 行**: ① A 桶条数 + 逐条「改哪个文件的哪一行」 ② B 桶条数 + 逐条「板那一趟要动什么」 ③ C 桶条数 + 逐条 need key ④ 一句话「板那一趟开工前必须先落哪几条」 ★
- ★**`--selftest` ≥ 4 条用例**: ① 正向: 当前板 + 当前网表 ⇒ 5 条差异被完整复现且归桶总数 = 5 ② 反向: 把某条差异消掉 ⇒ 该条从桶里消失且总数减 1 (★证明判定是算出来的, 不是写死的★) ③ 归桶逻辑: 造 3 个合成案例 (网表多一行 / 板网不同 / 等决策) 各归各桶 ④ 板文件零改证明: selftest 跑完板 md5/mtime 不变 ★ ⇒ ★**末行必须打印 `ALL TESTS PASS` 且 rc=0** ★
- ★**rc 语义**: 0 = 无未解释差异 · 2 = 有未解释差异 · 1 = 运行错误 ★
- ★**零副作用**: 不写板 / 不写网表 / 不重生成任何东西 / 不改任何既有闸 ★

### D3 · ★新建★ `HW/PCB/BOARD_TRIP_NETLIST_DIVERGENCE.md` (一页权威口径 · 4 段, 不许超)
① **5 条差异总表** (差异 / 网表侧实际 / 板侧实际 / 归桶 / 证据 / 后果) ② **A 桶**: 逐条写死【哪个文件 · 哪一行 · 改成什么】⇒ ★**这是「板 md5 不用动」的那部分, 最值钱** ③ **B 桶**: 逐条写死【板那一趟要动什么 · 触及不触及高速/差分铜 · 要不要重出 Gerber】并写明与「板那一趟」其它已知项 (位号改名 / B-1~B-8 / 布局修正 / 布线 45→0 / Gerber 重出) 的关系 ④ **C 桶**: 逐条 need key + 一句话题 ⇒ ★**只列, 不代拍, 不许写倾向性结论** ★
★**页尾必须有一句铁律**: 「板只改一次 ⇒ A 桶的修复必须落在板那一趟【之前】; B 桶必须落在那一趟【之内】; C 桶没拍板之前不许开工」★

### D4 · ★新建★ `logs/iss340/` (机器原始输出) + 写 `state/fragments/hw.yaml` (分片)
- ★**分片必须走** `python3 state/frag_write.py --agent hw-lead` (★原子写, 禁止 open(p,"w")★) ⇒ 写完 `grep -c iss340 state/fragments/hw.yaml` **≥ 5** ★
- ★**logs/iss340/ 里要存**: ① D2 的 `--selftest` 完整输出 ② D2 跑当前板 + 当前网表的完整输出 ③ `check_pcb_nets.py` 的 C1 段原文 ④ 板 md5 + mtime 前后对照 ⑤ merge / gate_check 输出 ★

---

## §-5 必跑项 (★每个只许跑一次 · 全部加 timeout★)

```
python3 HW/check_board_netlist_divergence_gate.py --selftest      # 末行 ALL TESTS PASS, rc=0
python3 HW/check_board_netlist_divergence_gate.py HW/PCB/demo_mainboard.kicad_pcb --netlist HW/netlist_v1.csv
python3 state/merge.py        # rc=0
python3 state/gate_check.py   # rc=0, Q1 必须 18/18
md5sum HW/PCB/demo_mainboard.kicad_pcb   # 必须仍 611b869e13518c3c023fb178f91a0075
stat -c '%y' HW/PCB/demo_mainboard.kicad_pcb   # 必须仍 2026-11-06 07:07:17.362193413
```

---

## §-6 纪律 (★违反任一条 = 交卷无效★)

★**边界**:
- ★**零写板** (md5 + mtime 双证) ★
- ★**零改网表 / 零改原理图 / 零改 BOM / 零改脚表** ⇒ ★**A 桶的修法只许「写进交付页」, 不许真改文件** ★
- ★**零落表**: 不许写 `state/issue_log.yaml` (★本单由 main 签收, agent 不许自签★) ★
- ★**零改闸**: 不许改 `state/gate_check.py` / `state/chain_gate.py` / `state/check_pcb_nets.py` / `state/compare_arm_official.py` / `HW/check_board_comparable_gate.py` / `HW/check_s8_target_list.py` ★
- ★**零重生成**: ★**禁用** `state/gen_pcb_netlist_board.py` / `state/gen_netlist.py` / `state/gen_kicad_sch.py` / `state/gen_bom.py` / `state/gen_pcb_routing.py` / `state/replay_patch_chain.sh` / `state/clrfix_iter.sh` / `state/gen_production_pack.sh` ★ ⇒ **本单只读不写产物** ★
- ★**只写自己分片**: 只许 `state/fragments/hw.yaml` (走 frag_write.py) ⇒ ★**不许碰 pm.yaml / sw.yaml / mech.yaml** ★
- ★**零外发**: 不发邮件 / 不联系任何供应商 / 不下采购单 (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 「不再发信, 全靠自己查资料」★) ★
- ★**不替老板拍板**: C 桶只列 need key + 题, 不给结论 ★
- ★**不改 `PROJECT_TRACKER.md` §0 锁死表** ★

★**顺序铁律 (★本项目 agent 反复踩的坑, 照做★)**:
1. ★**不许在写第一件交付物之前跑任何探查** ⇒ ★**先落 D1 判定表 (一次 write) → 再落 D2 闸 (一次 write) → 再落 D3 一页 (一次 write) → 再落 D4 → 最后才跑必跑项** ★
2. ★**每个交付物 = 一次独立 write 调用 · 不许攒成一条大 edit · 不许先草稿后改** ★
3. ★**必跑项只许跑一次** (★D2 的 selftest 跑完就贴输出, 不许再跑第二遍找不同★) ★
4. ★**若只剩一次落盘机会 ⇒ 先落 D1 (机器能判的东西比文档值钱)** ★
5. ★**主交付物 D3 放在 `HW/PCB/` 下 ⇒ 会进 `check_pcb_nets.py` / 各类扫描的视野 ⇒ 复现别人的读数时记得把自己的文件排除掉** ★
6. ★**★若你感觉自己要被压缩 / 要断了 ⇒ 立刻把手上已有的判定落盘 (哪怕是半成品判定表) ⇒ 宁可交半成品, 也不许空手死★** ★

★**交付前自检 (照抄, 不许自创格式)**:
- ★**占位符三查**: `grep -cE '<!--\[|🔄|待填|PLACEHOLDER|__[A-Z_]+__' logs/iss340/01_c1_verdict_table.md HW/PCB/BOARD_TRIP_NETLIST_DIVERGENCE.md` ⇒ 必须 **0** ★
- ★**引用件零 MISS**: 你写的文件里引用的每个 `logs/iss340/*` / `HW/*` / `state/*` 路径逐个 `[ -e ]` 查 ⇒ 必须 **0 MISS** ★
- ★**件数自洽**: 你自称的件数 == 盘面实际件数 ★

---

## §-7 回复格式 (★≤ 12 行, 只回事实 + 数字★)

1. ★**5 条差异逐条归桶**: A/B/C 各几条 + 每条一句话 (差异 → 归桶 → 后果) ★
2. ★**A 桶结论 (最值钱)**: 哪几条只改网表就够 ⇒ **板 md5 不用动** ⇒ 写清改哪个文件的哪一行 ★
3. ★**B 桶结论**: 哪几条必须动板 + 动什么 + 触及不触及高速/差分铜 ★
4. ★**C 桶结论**: 哪几条在等老板 (need key) ★
5. ★**板 md5 + mtime 双证 (前后)** ★
6. ★**必跑项 rc**: selftest / merge / gate_check (含 Q1 数字) ★
7. ★**交 main 裁的 2~3 条** (★不替老板拍★) ★
8. ★**如实交代偏差**: 若中途改了归桶结论 / 跑了几遍必跑项 / 交卷页未写 / 删过什么 ⇒ 一律写出来 ★
9. ★**★§-3 三条底稿, 你复跑后哪几条被推翻 / 修正了 ⇒ 逐条写出来 (★没推翻也要写「已复跑, 与底稿一致」★)** ★
