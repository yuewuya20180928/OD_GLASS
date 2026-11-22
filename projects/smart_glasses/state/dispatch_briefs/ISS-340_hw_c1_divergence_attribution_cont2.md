★★★★【main 2026-11-22 23:5x 追加 · 第三轮派活 · ★上一轮 cont2 (会话 `75cf0660`) 于 23:37:52 被【连带 abort】·它一个字都没写★ ⇒ 本单从头做★★★】★★★★
★**父会话 = 本 main 会话 (★它会用 `sessions_yield` 等你 ⇒ 不会像 23:30 那趟那样被连带 abort★)** ★
★**★先落盘, 后填内容 (★铁律·上一轮就这么死的·★被中断也不许零产出★)**: ① **第一件事** = 用 write 把交卷页 `HANDOFF/2026-11-22_hw-lead_ISS340_板网表C1差异归属判定.md` 的 **B1~B6 六个标题骨架先落盘** (★每块只写一行标题 + 一行说明·即可★) ⇒ ★**这样中途被打断, 盘上也有半页, 不会被判「一个字都没写」★** ② 再逐块把 cont1 已在盘的读数填进去 (★**不许重跑 cont1 的活·不许重跑任何臂·不许重跑长链★**) ③ 最后写 `logs/iss340/07_cont2_required_checks.log` + 分片补登记 (★只走 `python3 state/frag_write.py --agent hw-lead`★) ★
★**★引用零假引用 (★上一轮 ISS-337 就是栽在这·★交卷页自称引了盘上不存在的文件 ⇒ 签不了★)**: 交卷页里引用的每个 `logs/iss340/*` / `HW/*` / `state/*` 文件必须**逐个在盘** ⇒ 交卷前跑一次「引用逐个查存在」自检, 把输出贴进 §B6 ★
★**本单只要 3 件 (★cont1 的 4 件交付物已在盘·只许引用不许改★)**: ① 交卷页 B0~B7 (★`state/gate_check.py` 的 Q1 判据 = B1 结论摘要 / B2 验收标准自评 / B3 证据分级 / B4 接口取值声明 / B5 未决项与卡点 / B6 自证复现命令★) ② `logs/iss340/07_cont2_required_checks.log` ③ `state/fragments/hw.yaml` 补 2~3 条 (★零重复 key★) ★
★**回复 ≤ 400 字 + 4 行读数 (`SELFTEST_RC` / `GATE_RC` / `FRAG_ISS340_HITS` / `BOARD_MD5`)★**

【ISS-340 · hw-lead · ★★PCB 线 · cont2 · 零写板 ★★】
★**板↔网表 C1 红根因归属判定 —— cont2 = 只补【交卷页 B0~B7】+【分片补登记】, 不许重做 cont1 的任何交付物★**

★**派活方 = 项目总工 (main) · 2026-11-22 23:3x · cron fb67af40 (队列自动派活)★★**
★**兄弟 job (cron 775d9893) 22:36 明确把本单 cont2 留给本 job 认领 ⇒ 本 job 派出 cont2 ⇒ 兄弟 job 不会再重复派 hw-lead★**
★**工作目录 (★所有命令都在这里跑★)**: `cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses`

---

## §0 现状 (★main 本机实读, 不抄任何 agent 报告★)

★**cont1 (会话 `agent:hw-lead:subagent:a493c424`, 22:24 交卷) 已把 4 件交付物全部落盘** ⇒ ★**cont2 不许重做、不许改写它们★**:

| ★cont1 已在盘 (main 本机 stat 实读) ★ | 字节 / mtime | ★cont2 动作 ★ |
|---|---|---|
| `HW/check_board_netlist_divergence_gate.py` (判别闸本体 · 只读) | 45,073 B @ 2026-11-22 22:21 | ★**只许跑, 不许改** ★ |
| `HW/PCB/BOARD_TRIP_NETLIST_DIVERGENCE.md` (一页权威口径) | 12,796 B @ 2026-11-22 22:24 | ★**只许引用, 不许改** ★ |
| `logs/iss340/` (7 件: 01_c1_verdict_table.md · 01_selftest_out.txt · 02_gate_current_board_netlist.txt · 03_check_pcb_nets_c1.txt · 04_board_fingerprint.txt · 05_merge.txt · 06_gate_check.txt) | 目录 @ 22:23 | ★**只许追加新文件, 不许改旧件** ★ |
| `state/fragments/hw.yaml` (`grep -c iss340` = **7**) | 22:23 | ★**cont2 再补 2~3 条 (见 §3)★** ★**不许重写整份分片★** ★ |

★**板双证 (main 本机实读)**: `HW/PCB/demo_mainboard.kicad_pcb` md5 = `611b869e13518c3c023fb178f91a0075` · mtime = `2026-11-06 07:07:17.362193413` · 4,940,213 B
★**网表 md5 = `6aee500e60ba…` (2026-11-18 00:21)** ⇒ ★**板是 11-06 的板, 网表/原理图/BOM 是 11-18 的★★

★**cont1 的结论 (main 已实读 `logs/iss340/01_selftest_out.txt` 与 `logs/iss340/02_gate_current_board_netlist.txt` 核对过) ★**:
- ★**C1 差异 = 5 条**: 缺失 0 · 多余 2 (`C_VBUS_GND` pad1=GND · pad2=VBUS_5V_CHG) · 同号异网 3 (`Q_PG` pad1 应 PWR_GOOD 实 PWR_ON · `Q_PG` pad3 应 PWR_ON 实 PWR_GOOD · `D_ESD_USB_D` pad1 应 NET_USB_D_P_TYPEC 实 USB_D_P_SRC) ★
- ★**归桶 = A 0 / B 3 / C 2 (无未解释)★** ⇒ ★**没有一条是"只改网表就够" ⇒ 板 md5 这一趟躲不掉 (C 桶 2 条拍成"留位"时才可能只改网表)★★**
- ★**cont1 对"3 条差异 ↔ 3 条待拍板项"的对应关系 = 1 证实 + 2 推翻** ⇒ ★**老板真待拍只剩 C 桶的 `C_VBUS_GND` 留/下板 1 个 (另加 `W-4` 的 `.3` 极性一项)★**

★**cont1 明确没做的一件事 (★就是 cont2 的全部范围★)**: ★**交卷页 (B0~B7) 没写** ⇒ ★**理由 = 怕写半页把 `state/gate_check.py` 的 Q1 从 18/18 打成 17/18 ⇒ 盘上 newest 仍是 ISS-339 那份齐全的★★**

---

## §1 本单范围 (★只有 3 件, 不许扩★)

★**交卷物 (3 件)** ★

1. ★**新建★ `HANDOFF/2026-11-22_hw-lead_ISS340_板网表C1差异归属判定.md` (★**交卷页 B0~B7 七块齐全★**)★ — 详见 §2
2. ★**新建★ `logs/iss340/07_cont2_required_checks.log` (★必跑项原样输出贴进去★)★ — 详见 §4
3. ★**改★ `state/fragments/hw.yaml` (★**只许走 `state/frag_write.py` 原子写, 禁止 `open(p,"w")`★**)★ — 详见 §3

★**不许碰的东西 (★越界 = 交卷不算数★)★**: ★**板 `HW/PCB/demo_mainboard.kicad_pcb` (零写板) · 网表 `HW/netlist_v1.csv` (零落表) · `HW/check_board_netlist_divergence_gate.py` (零改闸) · `HW/PCB/BOARD_TRIP_NETLIST_DIVERGENCE.md` (零改规格页) · `logs/iss340/` 里 cont1 的 7 件旧件 (零改旧件) · `state/fragments/pm.yaml` / `mech.yaml` / `sw.yaml` (零写别人的分片) · `state/issue_log.yaml` (★那是 main 的派单记录, 不许自己改★) ★**

---

## §2 D1 · 交卷页硬要求 (★`state/gate_check.py` 的 Q1 会逐块打分★)

★**页路径**: `HANDOFF/2026-11-22_hw-lead_ISS340_板网表C1差异归属判定.md`
★**必须逐块给出, 且每个块首行标题里必须带上【方括号里的关键词】(★gate_check 按关键词打分, 关键词缺一个就掉到 17/18★)**:

| 块 | ★标题必须含关键词★ | 内容硬要求 |
|---|---|---|
| **B0** | `一页摘要` | ★**一句话结论**给 main: 「C1 5 条差异 = A0/B3/C2 ⇒ 板 md5 这一趟躲不掉; 板那一趟开工前必须先落 C 桶 2 条」 ★ |
| **B1** | `结论摘要` | ★**5 条差异逐条一行**: 差异 / 网表侧 / 板侧 / 归桶 (A/B/C) / 证据 / 后果 ★ + ★**A 桶 = 0 条**(★"只改网表就够"这一栏必须显式写 0, 不许留空★) ★ + ★**B 桶 3 条逐条写死【板那一趟要动什么 · 触及不触及高速/差分铜 · 要不要重出 Gerber】★ ★**`D_ESD_USB_D` 那条必须写明 = 90Ω 受控阻抗差分对成员 ⇒ DRC 必须带差分对规则, 且不许破坏 D+/D− 匹配, 且必须与 S4 的 B-3/B-4/B-5 合并成一次原子操作 (不是"挪一根 stub")★★** ★ + ★**C 桶 2 条逐条写 need key + 一句话题 (只列, 不代拍)★★** |
| **B2** | `验收标准自评` | ★**逐条 对 / 不对 + 机器读数** (★把 §4 四个命令的实跑输出贴在这里★) ★ + ★**cont1 交回的"3 条对应 = 1 证实 + 2 推翻"逐条写清哪条被推翻★** |
| **B3** | `证据分级` | ★**本单每一个数标 [实测]/[官方]/[推算]/[0数据]★** (★板 md5/mtime = [实测] · C1 五条 = [实测] · 归桶理由 = [推算]★) |
| **B4** | `接口取值声明` | ★**`HW/check_board_netlist_divergence_gate.py` 的 rc 语义 (0=无未解释差异 / 2=有未解释差异 / 1=运行错误) + 入参 (`--netlist` / `--registry` / `--selftest`) + 输出格式 + 跟既有闸的关系 (与 `state/check_pcb_nets.py` 的关系: 前者归桶, 后者只判等价)★** ★ + ★**分片登记声明 (走的全是 `state/frag_write.py --agent hw-lead`, 只写自己分片)★★** |
| **B5** | `未决项与卡点` | ★**卡点表 (谁 / 答什么 / 不答的后果) ★** 至少写清: ★**① C 桶 2 条 (`C_VBUS_GND` pad1/pad2 留位还是下板 ⇒ need key `boss_c_vbus_gnd_reserve_pad_20261117`) ★** ★**② `Q_PG` pad1/pad3 的 PWR_GOOD/PWR_ON 归属 (与 `W-4` 的 `.3` 极性一项合看) ★** ★**③ `D_ESD_USB_D` pad1 随 ESD 架构轴 (A3 / W-2) 走, 不许本单代拍 ★** ★**④ cont1 推迟交卷页这件事本身 (如实登记, 不许写成"已完成")★** ★ + ★**写明"本单不代拍"★** |
| **B6** | `自证复现命令` | ★**四条命令逐条 + 逐条原样输出 (从 `logs/iss340/07_cont2_required_checks.log` 抄)★** ★**必须含板 md5/mtime 前后对比 (开工前 = 交卷后)★★** |
| **B7** | `边界自证` | ★**做了 / 没做逐条列★** ★**零写板 · 零改闸 · 零落表 · 零改 cont1 旧件 · 零写别人分片 · 零外发 · 未代拍 · 板 md5 与 mtime 逐字节未变 (把 `stat` 输出贴上)★** |

★**★写页纪律 (★cont1 就是死在这一步的兄弟案例, 别重蹈★)★**:
- ★**整页 = 一次 write 调用** ⇒ 不许分 8 次写 8 个块 (★分多次写 = 中途被掐 = 留下半页 = Q1 掉到 17/18★) ★
- ★**先写 B0~B7 全部小节标题 + 每节 ≥3 行实质内容 ⇒ 一次 write ⇒ 再补细节 (★补细节是第二次 write, 但骨架必须完整★)★**
- ★**页里不许出现空指针 / `TODO` / `待补` / `XXX` ⇒ 写不出来的那一项写 `[0数据]` + 一句话原因★**
- ★**页里引用的每个文件路径必须真实存在 ⇒ 写完自查一遍 `grep -o '`[^`]*`' 页名 | while read p; do [ -e "$p" ] || echo "MISS $p"; done` ⇒ 必须 0 行 MISS★**

---

## §3 D3 · 分片补登记 (★只走 `state/frag_write.py`★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 state/frag_write.py --agent hw-lead --add-artifact path="HANDOFF/2026-11-22_hw-lead_ISS340_板网表C1差异归属判定.md" summary="ISS-340 cont2 交卷页 B0~B7 (C1 5 条差异归桶 A0/B3/C2)"
python3 state/frag_write.py --agent hw-lead --add-answer key=iss340_c1_attribution_verdict to=main value="C1 5 条差异归桶 A0/B3/C2; A 桶=0 (板 md5 躲不掉); 3 条对应关系 1 证实 2 推翻; 老板真待拍只剩 C_VBUS_GND 留/下板 + W-4 的 .3 极性" ref="HANDOFF/2026-11-22_hw-lead_ISS340_板网表C1差异归属判定.md"
python3 state/frag_write.py --agent hw-lead --add-need key=iss340_c_bucket_boss_decisions to=boss item="C 桶 2 条待拍: (1) C_VBUS_GND pad1/pad2 = 留位还是下板 (留位⇒ 只改网表 board 列 CHG_BOARD→MAIN_PCB, 板 md5 不动; 下板⇒ 进板那一趟); (2) Q_PG pad1/pad3 的 PWR_GOOD/PWR_ON 归属 (与 W-4 的 .3 极性合看)。★D_ESD_USB_D pad1 随 ESD 架构轴 A3/W-2 走, 另拍。"
```
★**验收信号**: `grep -c iss340 state/fragments/hw.yaml` ≥ **10** (现在是 7) ★**且 `python3 state/merge.py` rc=0 后 STATE.yaml 能读到这 3 条★**

---

## §4 D2 · 必跑项 (★每个只跑一次, 原样输出存进 `logs/iss340/07_cont2_required_checks.log`★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 HW/check_board_netlist_divergence_gate.py --selftest
python3 HW/check_board_netlist_divergence_gate.py HW/PCB/demo_mainboard.kicad_pcb --netlist HW/netlist_v1.csv
md5sum HW/PCB/demo_mainboard.kicad_pcb && stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb
python3 state/merge.py
python3 state/gate_check.py
```
★**期望读数 (★main 本机实读过 cont1 的日志, 对不上就如实写进 §B2 自评, 不许改闸也不许改网表去凑绿★)★**:
- selftest ⇒ **rc=0 且末行 `ALL TESTS PASS`** (★T1 正向 5 条全复现且归桶 5 · T2 反向消一条 ⇒ 总数 4 · T5 合成"网表多一行"⇒ 归 A★)
- 闸跑当前板+网表 ⇒ **rc=0** 且 C1 差异 = 缺失 0 / 多余 2 / 同号异网 3 · 归桶 A0/B3/C2
- 板 md5 = `611b869e13518c3c023fb178f91a0075` · mtime = `2026-11-06 07:07:17.362193413` ★**跑前跑后各贴一次, 必须逐字节相同★★**
- `state/merge.py` ⇒ **rc=0**
- ★**`state/gate_check.py` ⇒ rc=0 且 Q1 = 18/18 ⇒ ★★这一条必须在【交卷页写完之后】再跑一次 (★它是唯一允许的第二次: 因为它必须读新页★)★★** ★**若 Q1 掉到 17/18 ⇒ 立刻按 §2 的关键词表补齐缺的那一块 ⇒ 再跑一次 ⇒ 仍掉就把缺块写进 §B5 交 main★**

---

## §5 边界自证 (★交卷回复里逐条给结论, 不许只说"都做了"★)

| 项 | 要求 |
|---|---|
| 板 | ★**零写板** ⇒ md5 + mtime 前后逐字节相同 ★ |
| 网表 / 脚表 / BOM / 原理图 | ★**零改** ⇒ md5 不变 ★ |
| `HW/check_board_netlist_divergence_gate.py` | ★**零改** ⇒ md5 不变 (cont1 的证据链靠它成立) ★ |
| `HW/PCB/BOARD_TRIP_NETLIST_DIVERGENCE.md` | ★**零改** ⇒ md5 不变 ★ |
| `logs/iss340/` 旧 7 件 | ★**零改** ⇒ 只新增 `07_cont2_required_checks.log` ★ |
| 分片 | ★**只写 `state/fragments/hw.yaml`** ⇒ `pm.yaml` / `mech.yaml` / `sw.yaml` 的 md5 不变 ★ |
| `state/issue_log.yaml` | ★**零改** (★main 才改得了★) ★ |
| 外发 | ★**零外发** ⇒ 不发任何邮件/询价/问询/采购 (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★) ★**本单也没有任何需要外查的缺口 (C1 五条全在本机盘面上) ⇒ 一条都不用查★** |
| 拍板 | ★**不代拍** ⇒ C 桶只列 need key + 题面 ★ |

---

## §6 防死纪律 (★main 21:16 实测教训, 上一单 cont1 的兄弟案例死在这上面★)

1. ★**每个交付物 = 一次 write 调用 · 不许写第一件之前跑任何探查 · 必跑项只许跑一次 · 先落 [交卷页骨架] 再补 [细节]** ★
2. ★**若只剩一次落盘机会 ⇒ 先落交卷页 (机器可判的完整结构比文档细节值钱) ⇒ 再落分片 ★**
3. ★**别开长任务**: 本单只有 3 件交付物, 不要顺手去改闸、改网表、改规格页、写别的页 ★
4. ★**token / runtime 纪律**: 本单目标 ≤ 25 分钟; 若感觉要超时 ⇒ ★**先把交卷页写出来 (哪怕细节不齐) ⇒ 再补** ★

---

## §7 交卷回复格式 (★回给 main, 不许直接进老板拍板页★)

1. ★**一句话**: C1 归桶结论 + 板 md5 是否被动过 ★
2. ★**交卷页路径 + 字节 + mtime** ★
3. ★**必跑项 5 条的 rc (★gate_check 那条必须写 Q1 = ?/18★)** ★
4. ★**分片**: `grep -c iss340` 的前后数 ★
5. ★**交 main 裁的 3 条** (★C 桶 2 条进老板拍板页的措辞建议 + `D_ESD_USB_D` 是否必须与 S4 合并成一次原子操作★) ★
6. ★**本单【没做、也不该由本单做】的事 (★诚实登记★)**: 归桶不重判 / 闸不改 / 网表不落表 / 板不动 / 不代拍 ★
