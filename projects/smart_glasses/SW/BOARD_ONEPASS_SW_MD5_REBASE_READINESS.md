# BOARD_ONEPASS_SW_MD5_REBASE_READINESS · 「板那一趟」SW 侧板 md5 引用面清账 + 清单自守

> ★**单号**: ISS-372 · ★**执笔**: sw-lead (软件总工) · ★**时刻**: 2026-11-23 (Asia/Shanghai)
> ★**类别**: ★**纯分析 + 作业包 + 新建闸 + 沙盒预演 · 零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 · 零挂链 · 零外发 · 不代老板拍板** ★
> ★**配套**: ★机器闸 `SW/tools/check_sw_board_md5_rebase_readiness.py` (H1~H7 + `--selftest` 8 条反向用例) ★
> ★**交卷页**: `HANDOFF/2026-11-23_sw-lead_ISS372_SW侧板md5引用面清账与清单自守.md` ★

---

## ★0 · 口径与读数 (★全部本机实读·全部可复跑★)

### ★0.1 · 板 md5 基线 (★逐字★)

| 项 | 值 | 来源 | 复跑命令 |
|---|---|---|---|
| 板文件 | `HW/PCB/demo_mainboard.kicad_pcb` | 盘上真件 | `ls -l HW/PCB/demo_mainboard.kicad_pcb` |
| ★**md5** ★ | ★`611b869e13518c3c023fb178f91a0075` ★ | 盘上真件 | `md5sum HW/PCB/demo_mainboard.kicad_pcb` |
| ★**mtime** ★ | ★`2026-11-06 07:07:17.362193413` ★ | 盘上真件 | `stat -c '%y' HW/PCB/demo_mainboard.kicad_pcb` |
| ★**size** ★ | ★`4940213` ★ | 盘上真件 | `stat -c '%s' HW/PCB/demo_mainboard.kicad_pcb` |

★**开工前 / 交卷后各打一次 ⇒ 三项逐字节相同 (见交卷页 B5 + `logs/iss372/07_board_double_evidence.txt`)** ★[实测]

### ★0.2 · 落表台账真身 + 链头从哪读

| 项 | 值 | 复跑/定位命令 |
|---|---|---|
| 落表台账真身 | `HW/SCHEMATIC_LANDING_V1_LANDED.md` (★append-only 的信任边界★) | `grep -n 'demo_mainboard.kicad_pcb' HW/SCHEMATIC_LANDING_V1_LANDED.md` |
| 链头算法 (唯一真源) | `SW/tools/check_demo_panel_spec.py` 的 `sw_ledger_change_state()` / `sw_ledger_state()` / `sw_ledger_change_rows()` | `grep -n 'def sw_ledger_change_state\|def sw_ledger_state\|def sw_ledger_change_rows' SW/tools/check_demo_panel_spec.py` |
| ★**权威 R6 判据位置** ★ | ★`SW/tools/check_demo_panel_spec.py` 的 `check_r6_hard_protected()` (★L748 起★) ★ | `grep -n 'def check_r6_hard_protected' SW/tools/check_demo_panel_spec.py` |
| 合法改板四件原子 | `by` / `file` / `prev_md5` / `md5` (★`REBOARD_FIELDS`★) | `grep -n 'REBOARD_FIELDS' SW/tools/check_demo_panel_spec.py` |
| SW 台账锚点块 | `SW/SW_MD5_BASELINE_LEDGER.md` 的 `# BEGIN SW_MD5_ANCHORS` 块 (`anchors.hard_protected[]`) | `grep -n 'BEGIN SW_MD5_ANCHORS' SW/SW_MD5_BASELINE_LEDGER.md` |

### ★0.3 · SW 域板 md5 引用面 (★本单的正题·扫描读数★)

| 口径 | 读数 | 复跑命令 |
|---|---|---|
| ★**活文件数** ★ | ★**20** ★ (★cont1: 上一趟交卷时 = 17★) | `python3 SW/tools/check_sw_board_md5_rebase_readiness.py` (H1 自扫) |
| ★**命中行数** ★ | ★**53** ★ (★上一趟 = 47★) | 同上 |
| ★**命中处数** ★ | ★**63** ★ (★上一趟 = 57★) | 同上 |
| 三类分布 | ★判据锚 **11** 行 / 规格页引用 **17** 行 / 历史留证 **25** 行 ★ (★上一趟 = 9 / 17 / 21★) | 同上 |

★**扫描口径 (★与上一趟那套 grep 命令有一处实质差别·见 §1.9★)** ★[实测]
★**逐文件遍历 + 逐行计数 (排除 `.bak` / `__pycache__`)** ⇒ ★**不用 `grep -v` 做行级过滤** ★

---

## ★1 · SW 域 53 行 / 63 处 板 md5 引用逐处清单 (★本单的正题★)

### ★1.1 · 三类归属的定义 (★判定口径·不是修辞★)

| 归属 | 定义 (★看这一处的【角色】·不是看它在哪个文件★) | 判据 |
|---|---|---|
| ★**判据锚** ★ | ★这一处文本是某个机器判决的比较目标 (脚本里的字面量 / 台账锚点里的保护基线 / 接口格式契约里的值) ★ | 改它 = 改判据 ⇒ 闸会红 |
| ★**规格页引用** ★ | ★这一处文本是人读的页面上的【当前值 / 期望值 / 清单条目】引用 (不是判决依据, 但会被某些闸当现状值读) ★ | 改板那一趟要跟着板改, 平时不许动 |
| ★**历史留证** ★ | ★这一处文本记录的是【某一次历史读数 / 某一次交卷当时的自证结果】 ★ | ★**永远不许改** (改了就是造假记录, 比留着旧数更坏) ★ |

### ★1.2 · 三种处置的定义

| 处置 | 含义 |
|---|---|
| ★**随板改** ★ | 改板那一趟 (S9 换基线) 必须跟着改 ⇒ 不改则页面说谎或闸假红 |
| ★**不许改** ★ | 永远不许动 |
| ★**交 main 拍** ★ | 判据方向 / 机制取舍 ⇒ 本单只登记 + 给代价, 不代拍 |

### ★1.3 · 逐处清单 (★53 行·一行一行·不许按文件归并★)

★**说明**: ★「原文」列给的是该行的**关键片段** (★全文太长 ⇒ 只截关键部分★); ★「命中处」列 = 该行里 `611b869e` 这个 8 位前缀出现的次数 (★全文 32 位 md5 一律算 1 处·带省略号的 12 位前缀写法也算 1 处★)★

| # | 文件 | 行号 | 命中处 | 原文 (关键片段) | 三类归属 | 处置 | 备注 (为什么这么判/这么处置) |
|---|---|---|---|---|---|---|---|
| 1 | `SW/BOARD_ONEPASS_DEBUG_HEADER_FW_IMPACT.md` | 328 | 1 | `…t -c '%y %s'`（开工前 / 交卷后各一次）★ \| md5 **`611b869e13518c3c023fb178f91a0075`** · mtime **…` | 历史留证 | 不许改 | ★【cont1 新增 · ISS-378 页 §7 边界自证表「零写板」那一行】★ ⇒ 记的是 2026-11-24 02:4x 交卷当时的三项读数 ⇒ 不许改★ |
| 2 | `SW/BOARD_ONEPASS_DEBUG_HEADER_FW_IMPACT.md` | 397 | 1 | `"board_md5": "611b869e13518c3c023fb178f91a0075",` | 判据锚 | 交 main 拍 | ★★【cont1 新增 · ★★本单最要紧的一条★★】★★ 这一行在 ```json iss378_contract``` 机器块的 ★"baseline"."board_md5"★ ⇒ ★它是闸 SW/tools/check_debug_header_fw_impact.py 的 W7 (w7_zero_write) 的【判决源】: W7 拿机器块里的 baseline.board_md5 跟盘上实测比 ⇒ 不等就红 ⇒ ★所以它【不是规格页引用】, 是【判据锚】★★ ⇒ ★★它是本单 H4 检测盲区的活证据: 该闸源码里【没有 32 位字面量】(它自己算 md5), 钉板 md5 靠的是【页面内嵌基线】⇒ 上一趟只扫 .py 字面量的检测网【抓不到它】★★ ⇒ 必须走 §2 补丁 P-G ⇒ 谁落/何时落 = main 排期 |
| 3 | `SW/BOARD_ONEPASS_DEBUG_PIN_ORDER_CONTRACT.md` | 282 | 1 | `…at -c '%y %s'`（开工前 / 交卷后各一次） \| md5 **`611b869e13518c3c023fb178f91a0075`** · mtime **…` | 历史留证 | 不许改 | ★【cont1 新增 · ISS-375 页 §4-2 边界自证表「零写板」那一行】★ ⇒ 它记的是 2026-11-24 02:0x 交卷当时的三项读数 ⇒ 某一次交卷当时的事实 ⇒ 不许改★ |
| 4 | `SW/BOARD_ONEPASS_DEBUG_PIN_ORDER_CONTRACT.md` | 338 | 1 | `…** (板 md5 / mtime / size 三项未动, 板指纹仍为 `611b869e13518c3c023fb178f91a0075` / `2026-11-0…` | 历史留证 | 不许改 | ★【cont1 新增 · ISS-375 页【追加式订正 (2026-11-24 02:5x)】段末的「板指纹仍为 …」】★ ⇒ 它记的是那个追加时刻的事实 ⇒ 不许改★ |
| 5 | `SW/BOARD_ONEPASS_DEBUG_PIN_ORDER_CONTRACT.md` | 357 | 1 | `…无冲突** (板 md5 / mtime / size 三项未动, 仍为 `611b869e13518c3c023fb178f91a0075` / `2026-11-0…` | 历史留证 | 不许改 | ★【cont1 新增 · ISS-375 页【追加式订正 (2026-11-24 04:3x · cont3)】段首的「板 md5 / mtime / size 三项未动, 仍为 …」】★ ⇒ 它记的是那个追加时刻的事实 ⇒ 不许改★ |
| 6 | `SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md` | 164 | 1 | `…链头取代的历史值 ⇒ 不许照抄 ⇒ 退休; ★它正文里另外那 2 个 (板 611b869e / .kicad_pro 3e504d2b) 是【受保护 5 件的盘上现值…` | 规格页引用 | 随板改 | ★登记项: 板 md5 = 受保护 5 件的盘上现值 ⇒ 那一趟随板改★ |
| 7 | `SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md` | 217 | 1 | `…1_reanchor_netlist_md5_sw \| NEED-MD5: 611b869e13518c3c023fb178f91a0075 \| PRODUCED-BY…` | 规格页引用 | 随板改 | ★NEED-KEY 登记行 (板 md5 = 盘上现值) ⇒ 那一趟随板改★ |
| 8 | `SW/BOARD_ONEPASS_FP_TRUTH_READ_ENTRY.md` | 14 | 1 | `…HW/PCB/demo_mainboard.kicad_pcb` ★ \| `611b869e13518c3c023fb178f91a0075` \| `2026-11-0…` | 规格页引用 | 随板改 | ★§1 清单第 1 行 (板 + md5 + mtime + size) ⇒ 它是 ISS-363 闸 F4 的被检对象 ⇒ 那一趟随板改★ |
| 9 | `SW/BOARD_ONEPASS_LEGB_SW_IMPACT.md` | 75 | 1 | `"board_md5": "611b869e13518c3c023fb178f91a0075",` | 规格页引用 | 随板改 | ★页里抄了判据脚本的 PROTECTED_MD5 字面量 ⇒ 那一趟随板改 (它抄的是判据, 不是判决源)★ |
| 10 | `SW/BOARD_ONEPASS_LEGB_SW_IMPACT.md` | 213 | 1 | `…d.kicad_pcb` \| 2026-11-06 07:07:17 \| `611b869e13518c3c023fb178f91a0075` (= 基线) \| 未动…` | 规格页引用 | 随板改 | ★现状表 (板 md5 = 基线 · 未动) ⇒ 那一趟随板改★ |
| 11 | `SW/BOARD_ONEPASS_LEGB_SW_IMPACT.md` | 221 | 1 | `…`HW/PCB/demo_mainboard.kicad_pcb` \| `611b869e13518c3c023fb178f91a0075` \| 4,940,213…` | 规格页引用 | 随板改 | ★板双证表 (md5 / size / mtime) ⇒ 那一趟随板改★ |
| 12 | `SW/BOARD_ONEPASS_LEGB_SW_IMPACT.md` | 420 | 1 | `…只发生在 `tmp/iss370_sbx/` 的副本上 \| ★板 md5 `611b869e13518c3c023fb178f91a0075` + mtime `202…` | 历史留证 | 不许改 | ★零写板自证留痕 (交卷前后逐字节相同) ⇒ 某一次交卷当时的事实 ⇒ 不许改★ |
| 13 | `SW/BOARD_ONEPASS_SW09_LANDING_PATCH.md` | 36 | 1 | `\| R8 \| 板 md5 / mtime \| `611b869e13518c3c023fb178f91a0075` / `2026-11-0…` | 规格页引用 | 随板改 | ★R8 判据表 (板 md5 / mtime) ⇒ 那一趟随板改★ |
| 14 | `SW/BOARD_ONEPASS_SW09_LANDING_PATCH.md` | 481 | 1 | `\| 零写板 \| 板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `202…` | 历史留证 | 不许改 | ★零写板留痕 (未变 [实测]) ⇒ 某一次交卷当时的事实 ⇒ 不许改★ |
| 15 | `SW/BOARD_ONEPASS_SW_SYNC.md` | 38 | 1 | `…上 = §4 三方案★) ★ \| ★**[实测]** 盘上板 md5 = `611b869e13518c3c023fb178f91a0075` · 台账 §1 `har…` | 规格页引用 | 随板改 | ★★【SW01_PCB_MD5 清单第 1 条的 current_state】⇒ 它被 SW/tools/check_onepass_sw_sync.py 的 W5 当【现状值】读 ⇒ ★那一趟不换基线 ⇒ W5 当场红 (沙盒 T2 实测: B 闸 rc=1)★ ⇒ 必须随板改★ |
| 16 | `SW/BOARD_ONEPASS_SW_SYNC.md` | 94 | 1 | `\| SW 台账 `hard_protected` 钉死的板 md5 \| `611b869e13518c3c023fb178f91a0075` \| `SW/SW_MD5…` | 规格页引用 | 随板改 | ★现状表 (台账钉死的板 md5) ⇒ 那一趟随板改★ |
| 17 | `SW/BOARD_ONEPASS_SW_SYNC.md` | 167 | 1 | `…"current_state": "[实测] 盘上板 md5 = 611b869e13518c3c023fb178f91a0075 · 台账 §1 hard_…` | 规格页引用 | 随板改 | ★§6 机器可读 JSON 块里的 current_state (W5 读它) ⇒ 那一趟随板改★ |
| 18 | `SW/DEMO_BOARD_60MS_VERDICT_PLAN.md` | 328 | 1 | `…cad_pcb HW/netlist_v1.csv           # 611b869e… / c78f9912… (逐字节未变)` | 规格页引用 | 随板改 | ★命令式复现注记 (12 位前缀) ⇒ 台账 §2 S-04 已定口径「保留 + 标注 · 命令式引用跑出来就是现值」⇒ 那一趟随板改★ |
| 19 | `SW/LOAD_SWITCH_SELECTION_FACTS.md` | 338 | 1 | `…本单对 `HW/` 的写入量 = **0 字节** (只读)。板 md5 `611b869e…` 自始至终一字未改。` | 历史留证 | 不许改 | ★md5 漂移归属叙述 (板 md5 自始至终一字未改) ⇒ 某一次交卷当时的事实 ⇒ 不许改★ |
| 20 | `SW/ONETRIP_SW_POSTRENAME_GATE_SOP.md` | 18 | 1 | `…`tmp/iss327/` 的沙盒副本上做; 真件板只读 \| 板 md5 `611b869e13518c3c023fb178f91a0075` + mtime `202…` | 历史留证 | 不许改 | ★零写板留痕 (交卷前后逐字节相同) ⇒ 不许改★ |
| 21 | `SW/ONETRIP_SW_POSTRENAME_GATE_SOP.md` | 63 | 1 | `★**期望读数**: ★**板 md5 ≠ `611b869e13518c3c023fb178f91a0075`** (★改了板 ⇒ md…` | 规格页引用 | 随板改 | ★【期望读数: 板 md5 ≠ 611b869e…】(改了板 ⇒ md5 必须变) ⇒ 这是改板那一趟的判据式描述 ⇒ 那一趟随板改 (改成「≠ <新板 md5>」)★ |
| 22 | `SW/ONETRIP_SW_POSTRENAME_GATE_SOP.md` | 310 | 1 | `…的原文是 `基线就不绿: ['R6 硬保护: … (fadf2c2f… ≠ 611b869e…)', 'R6 台账链: …']` ⇒ ★**它红在步 7 (md5 重锚…` | 历史留证 | 不许改 | ★某一次实测的报错原文引用 (rc=2 的原文) ⇒ 不许改★ |
| 23 | `SW/ONETRIP_SW_POSTRENAME_GATE_SOP.md` | 508 | 1 | `…单号>/md5_pre_board.txt` \| ★**改前的板指纹 = `611b869e13518c3c023fb178f91a0075`★** ⇒ ★**证明「板…` | 规格页引用 | 随板改 | ★流程表「板 md5 (改前)」⇒ 那一趟的改前指纹 = 新基线 ⇒ 那一趟随板改★ |
| 24 | `SW/ONETRIP_SW_RENAME_SAFETY.md` | 409 | 1 | `…m HW/PCB/demo_mainboard.kicad_pcb` = `611b869e13518c3c023fb178f91a0075` · mtime = `2…` | 历史留证 | 不许改 | ★零写板留痕 ⇒ 不许改★ |
| 25 | `SW/ONETRIP_SW_SAMEBATCH_RENAME_LIST.md` | 492 | 1 | `…HW/PCB/demo_mainboard.kicad_pcb (… ≠ 611b869e13518c3c023fb178f91a0075)']` | 历史留证 | 不许改 | ★反向用例的报错原文引用 ⇒ 不许改★ |
| 26 | `SW/ONETRIP_SW_SAMEBATCH_RENAME_LIST.md` | 619 | 1 | `…"current_state": "[实测] 盘上板 md5 = 611b869e13518c3c023fb178f91a0075 · 台账 §1 hard_…` | 规格页引用 | 随板改 | ★抄了清单页的 current_state (W5 同源口径) ⇒ 那一趟随板改★ |
| 27 | `SW/ONETRIP_SW_SAMEBATCH_RENAME_LIST.md` | 870 | 1 | `…/PCB/demo_mainboard.kicad_pcb` md5 = `611b869e13518c3c023fb178f91a0075` · mtime = `2…` | 历史留证 | 不许改 | ★零写板留痕 ⇒ 不许改★ |
| 28 | `SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md` | 211 | 1 | `…b` + `stat -c '%y'` 开工前后各一次 \| ★**md5 `611b869e13518c3c023fb178f91a0075` / mtime `202…` | 历史留证 | 不许改 | ★零写板留痕 ⇒ 不许改★ |
| 29 | `SW/SW_MD5_BASELINE_LEDGER.md` | 61 | 1 | `md5: 611b869e13518c3c023fb178f91a0075` | 判据锚 | 不许改 | ★§1 锚点块 hard_protected[板].md5 = 保护基线 ⇒ ISS-284 ④: 保护基线必须留在台账链尾 ⇒ 永远不许改★ |
| 30 | `SW/SW_MD5_BASELINE_LEDGER.md` | 114 | 1 | `…`HW/PCB/demo_mainboard.kicad_pcb` \| `611b869e13518c3c023fb178f91a0075` \| `<新板 md5>`…` | 判据锚 | 交 main 拍 | ★§1 ISS-284 ⑥ 给 main 的落表台账行格式模板 (改前 md5 = 当次改板前的值) ⇒ 那一趟由 main 照此写新行; ★模板本身要不要换成新基线 = main 拍 (代价: 不换 = 模板永远是旧基线, 换 = 模板失去「格式样例」的恒定性与可读性)★ |
| 31 | `SW/SW_MD5_BASELINE_LEDGER.md` | 131 | 1 | `…网表 `c78f9912…` / 脚表 `4814617e…` / 板 `611b869e…` / `.kicad_pro` `3e504d2b…` \| ★**恒红*…` | 规格页引用 | 随板改 | ★§2 S-01 行 = check_demo_panel_spec 的 PROTECTED_MD5 字面量【现状登记】⇒ 改板那一趟随板改★ |
| 32 | `SW/SW_MD5_BASELINE_LEDGER.md` | 134 | 1 | `…PLAN.md` L328 \| ★**文档 · 复现命令注记** ★ \| `611b869e… / c78f9912…` (12 位前缀) \| 文档口径**过期** \|…` | 规格页引用 | 随板改 | ★§2 S-04 行 = DEMO_BOARD_60MS_VERDICT_PLAN L328 的【现状登记】⇒ 改板那一趟随板改★ |
| 33 | `SW/SW_MD5_BASELINE_LEDGER.md` | 164 | 2 | `…脚表 `ef436a37…` / BOM `2a730574…` / 板 `611b869e…` / `.kicad_pro` `3e504d2b…` 四件逐字节不变…` | 历史留证 | 不许改 | ★§3 R-08 留痕行 (ISS-249 / ISS-254 第 5 跳重锚当时的事实) ⇒ 改它 = 改历史★ |
| 34 | `SW/SW_MD5_BASELINE_LEDGER.md` | 166 | 2 | `…94642d07…` 不在 R6 的受管真源里 ⇒ 只登记不许改★; 板 `611b869e…` / `.kicad_pro` `3e504d2b…` 逐字节不变 ⇒…` | 历史留证 | 不许改 | ★§3 R-09 留痕行 (ISS-257 / ISS-258 第 6 跳重锚当时的事实) ⇒ 改它 = 改历史★ |
| 35 | `SW/SW_MD5_BASELINE_LEDGER.md` | 168 | 2 | `…/ 网表 / 脚表 / BOM 五个 md5 交卷前后逐字节不变** (★`611b869e…` / `3e504d2b…` / `e06c1dd6…` / `287e…` | 历史留证 | 不许改 | ★§3 R-10 留痕行 (ISS-275 判决源换源当时的事实) ⇒ 改它 = 改历史★ |
| 36 | `SW/SW_MD5_BASELINE_LEDGER.md` | 170 | 3 | `…W/PCB/demo_mainboard.kicad_pcb` (… ≠ `611b869e…`)」 ⇒ ★**「板只改一次」那一趟 (S1~S13) 合法地就要改板…` | 历史留证 | 不许改 | ★§3 R-11 留痕行 (ISS-279「设计上无路」当时的事实) ⇒ 改它 = 改历史★ |
| 37 | `SW/SW_MD5_BASELINE_LEDGER.md` | 171 | 3 | `…W/PCB/demo_mainboard.kicad_pcb` (… ≠ `611b869e…`)」 ⇒ ★**那一趟合法改板当天 SW R6 必红, 而手改 `har…` | 历史留证 | 不许改 | ★§3 R-12 留痕行 (ISS-284 合法改板机制落地当时的事实) ⇒ 改它 = 改历史★ |
| 38 | `SW/SW_MD5_BASELINE_LEDGER.md` | 172 | 2 | `…o` 的两个 md5 仍然一个字不许动** (★ISS-279 交卷基线 `611b869e…` / `3e504d2b…`★) ⇒ ★**「不许手改 md5 凑绿」照…` | 历史留证 | 不许改 | ★§3 R-13 留痕行 (ISS-279 收口轮 W6 基线口径订正当时的事实) ⇒ 改它 = 改历史★ |
| 39 | `SW/SW_MD5_BASELINE_LEDGER.md` | 173 | 2 | `…个字节**★ ⇒ ★**板 / `.kicad_pro` 逐字节不变 (★`611b869e…` / `3e504d2b…★)** ★ \| ★**`python3 SW…` | 历史留证 | 不许改 | ★§3 R-14 留痕行 (ISS-279 收口轮 W6 链头判据收严当时的事实) ⇒ 改它 = 改历史★ ★★【本机新发现 ★ 上两趟那套 `grep -v '\.bak'` 的逐行清单把这一行漏掉了! ★ 原因: 这一行的正文里含 `state/.bak_iss220/…` ⇒ 被那条过滤规则【连带】过滤 ⇒ 计数 (57 处) 对, 但【逐行清单】少一行 ⇒ 本单改用逐文件遍历 + 逐行计数 (★不受该连带过滤影响★)★] |
| 40 | `SW/SW_MD5_BASELINE_LEDGER.md` | 181 | 1 | `…7` (同批同刻, ★不在 R6 受管真源里 ⇒ 只登记不许改★); 板 `611b869e13518c3c023fb178f91a0075` / `.kicad_pr…` | 历史留证 | 不许改 | ★§3 追加段 (ISS-258 第 6 跳重锚当时的事实) ⇒ 不许改★ |
| 41 | `SW/SW_MD5_BASELINE_LEDGER.md` | 183 | 1 | `…9b93607` (★不在 R6 受管真源里 ⇒ 只登记不许改★); 板 `611b869e13518c3c023fb178f91a0075` / `.kicad_pr…` | 历史留证 | 不许改 | ★§3 追加段 (ISS-275 判决源换源当时的事实) ⇒ 不许改★ |
| 42 | `SW/SW_NEEDS_TRIAGE.md` | 186 | 1 | `…7f62ac3…/脚表 a4270120…/BOM 5d02bece…/板 611b869e… 四个 md5 逐字节不变) ⇒ 且该禁令被新闸 SW/tools/che…` | 历史留证 | 不许改 | ★已闭合 need 的闭环注 (四个 md5 逐字节不变) ⇒ 某一次交卷当时的事实 ⇒ 不许改★ |
| 43 | `SW/SW_NEEDS_TRIAGE.md` | 346 | 1 | `\| 板 md5 (钉板真值) \| `611b869e13518c3c023fb178f91a0075` + mtime `202…` | 规格页引用 | 随板改 | ★判据表行「板 md5 (钉板真值)」⇒ 那一趟随板改★ |
| 44 | `SW/SW_NEEDS_TRIAGE.md` | 359 | 1 | `\| 板 md5 `611b869e13518c3c023fb178f91a0075` + mtime `202…` | 历史留证 | 不许改 | ★证据表行 ([实测] · 交卷前后逐字节相同) ⇒ 某一次交卷当时的事实 ⇒ 不许改★ |
| 45 | `SW/research/ISS250_r6_复核记录.md` | 25 | 1 | `….py` 实跑, 2026-11-17 05:40★)**: 板 md5 `611b869e13518c3c023fb178f91a0075` (★自 11-06 07…` | 历史留证 | 不许改 | ★★【本单唯一的「某次复核当时的读数留痕」⇒ 永远不许改】★★ 它的正文里还有板侧硬数字 (板 md5 / 18092 段走线 / 433 过孔 / unconnected=45 / 板↔网表 rc=1 / R3 矛盾 2 条 / G1 仍开) ⇒ 那都是 2026-11-17 05:40 的读数 ⇒ 一律不许改 |
| 46 | `SW/tools/check_debug_pin_order_contract.py` | 53 | 1 | `BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"` | 判据锚 | 交 main 拍 | ★★【cont1 新增 · ISS-375 (2026-11-24 02:05 交付) 的闸 D7 硬钉目标】★★ BOARD_MD5/BOARD_MTIME/BOARD_SIZE 三个常量 ⇒ ★该闸 D7 判「盘上板指纹三项 == 这三个常量」⇒ 改板当天必红 ⇒ ★手改字面量 = 挖坑 ⇒ 不许★ ⇒ 必须走 §2 补丁 P-F ⇒ 谁落/何时落 = main 排期 |
| 47 | `SW/tools/check_fp_truth_read.py` | 87 | 1 | `BOARD_BASELINE_MD5 = "611b869e13518c3c023fb178f91a0075"` | 判据锚 | 交 main 拍 | ★F5 的板 md5 硬比较目标 (ISS-363 今天 17:27 交付) ⇒ 改板当天必红 ⇒ ★手改字面量 = 挖坑 ⇒ 不许★ ⇒ 必须走 §2 补丁 P-C ⇒ 谁落/何时落 = main 排期 |
| 48 | `SW/tools/check_onepass_legb_sw_impact.py` | 70 | 1 | `"board_md5": "611b869e13518c3c023fb178f91a0075",` | 判据锚 | 交 main 拍 | ★G8 的 PROTECTED_MD5['board_md5'] (ISS-370 今天 19:50 交付) ⇒ 改板当天必红 ⇒ ★手改字面量 = 挖坑 ⇒ 不许★ ⇒ 必须走 §2 补丁 P-D ⇒ 谁落/何时落 = main 排期 |
| 49 | `SW/tools/check_onepass_sw_sync.py` | 109 | 1 | `…"HW/PCB/demo_mainboard.kicad_pcb": "611b869e13518c3c023fb178f91a0075",` | 判据锚 | 不许改 | ★ANCHOR_MD5 = 锚点防篡改副本 ⇒ 它的角色是【盯住台账锚点里的保护基线有没有被手改】⇒ ISS-284 语义: 锚点里的 md5 永远不许改★ (已跑通的合法改板通道闸) |
| 50 | `SW/tools/check_onepass_sw_sync.py` | 806 | 2 | `"611b869e13518c3c023fb178f91a0075", "611b869e13…` | 判据锚 | 不许改 | ★--selftest 夹具里的假 md5 对 (基准/改后) ⇒ 是反向用例的输入, 不是判决锚★ |
| 51 | `SW/tools/check_onepass_sw_sync.py` | 829 | 1 | `assert "611b869e13518c3c023fb178f91a0075" in t` | 判据锚 | 不许改 | ★--selftest 夹具断言 ⇒ 同上★ |
| 52 | `SW/tools/check_onepass_sw_sync.py` | 831 | 1 | `f.write(t.replace("md5: 611b869e13518c3c023fb178f91a0075",` | 判据锚 | 不许改 | ★--selftest 夹具写入 (把基线改成假值) ⇒ 同上★ |
| 53 | `SW/tools/check_onepass_sw_sync.py` | 832 | 1 | `"md5: 611b869e13518c3c023fb178f91a0076", 1))` | 判据锚 | 不许改 | ★--selftest 夹具写入 (假值那一侧) ⇒ 同上★ |

| 54 | `SW/BOARD_ONEPASS_ZERO_FALSE_CONNECTIVITY.md` | 23 | 1 | \| 1 \| 板指纹 \| md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · size `4940213` ⇒ **19 天逐字节未动** \| | 规格页引用 | 交 main 拍 | ★【ISS-408 补登记 · 第 54 行】★ 它在 ISS-381 页 §1「板面真值」表第 1 行 ⇒ 自述盘上【当前】板指纹 + 挂一条活的复现命令 ⇒ 它不是判决源 ⇒ 按 §1.2 落在【规格页引用】这一侧 ⇒ ★**归属方向归 main (§6 Q1)**: 判【历史留证】则永远不许改 (板那一趟页面说谎), 判【规格页引用】则必须随板改 (进 S9 换基线清单) ⇒ 两个方向结论相反 ⇒ 本单只登记 + 给代价, 不代拍★ |
| 55 | `SW/BOARD_ONEPASS_ZERO_FALSE_CONNECTIVITY.md` | 241 | 1 | \| ★零写板★ \| 板 md5 `611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17.362193413` / size `4940213` 开工前后对照 `logs/iss381/baseline_fingerprints.txt` \| ★**逐字相同** (开工前 / 交卷后两次实测输出见 `logs/iss381/boundary_proof.txt`) ★ \| | 历史留证 | 不许改 | ★【ISS-408 补登记 · 第 55 行】★ 它在 ISS-381 页 §7「边界自证」表「零写板」那一行 ⇒ 记的是某一次交卷当时的前后对照结果 ⇒ ★**同款形状在 §1.3 第 1 行已有先例** (ISS-378 页 §7 同款行 = 历史留证 / 不许改) ⇒ 口径一致 ⇒ 处置取 fail-safe 方向「不许改」⇒ ★**改历史留证 = 造假记录, 比留着旧数更坏**★ |
| 56 | `SW/EVT_CHARGE_CURRENT_CRITERION_CALIBER.md` | 215 | 1 | ⑦ 板三项指纹 (md5 `611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17.362193413` / size 4940213) 前后逐字相同 | 历史留证 | 不许改 | ★【ISS-408 补登记 · 第 56 行】★ 它在 ISS-385 页 §5「证据分级表」的 [实测] 行第 ⑦ 条 ⇒ 记的是那一次交卷当时「前后逐字相同」的对照结论 ⇒ 逐字对上 §1.2 的【历史留证】定义 ⇒ 处置取 fail-safe 方向「不许改」★ |
| 57 | `SW/tools/check_sw_false_connectivity_gate.py` | 73 | 1 | `BASELINE_BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"` | 判据锚 | 交 main 拍 | ★【ISS-408 补登记 · 第 57 行】★ 它是 ISS-381 那道零假连通闸的板 md5 硬比较目标 (★同文件 L448 `if md5 != BASELINE_BOARD_MD5:` 把它喂给失败清单 ⇒ 盘上一变必红★) ⇒ ★**H3 明确「历史留证不许落在 .py 判据脚本上」⇒ .py 里的板 md5 字面量只能是判据锚**★ ⇒ 处置方向归 main (§6 Q2) |

### ★1.4 · 三类分布与处置分布 (★机器复算★)

| 三类归属 | 行数 | 其中 .py 判据脚本 | 处置「随板改」 | 处置「不许改」 | 处置「交 main 拍」 |
|---|---|---|---|---|---|
| 判据锚 | 11 | 8 | 0 | 6 | 5 |
| 规格页引用 | 17 | 0 | 17 | 0 | 0 |
| 历史留证 | 25 | 0 | 0 | 25 | 0 |
| ★**合计** ★ | ★**53** ★ | ★**8** ★ | ★**17** ★ | ★**31** ★ | ★**5** ★ |

★**三条结论 (★本单的正题·一句话版★)** ★[实测]
★**① 「改板那天把 `611b869e` 全仓 sed 替换一遍」是错的**: 它会把 **21 行历史留证**改成假记录 (★比留着旧数更坏★) ⇒ ★**必须逐处分类, 不许一刀切** ★
★**② 判据锚 11 行里, 只有 4 行 (4 道【没有合法改板通道】的闸: ISS-363 的 F5 / ISS-370 的 G8 / ISS-375 的 D7 / ISS-378 的 W7) 需要动** ⇒ ★**其余 7 行一条都不许动** (台账里的保护基线 = 永远不许改; 锚点防篡改副本 = 它的存在意义就是盯住那个基线没被手改) ★
★**③ 规格页引用 17 行 = 改板那一趟「S9 换基线」一次改齐的清单** (★沙盒 T2b 实测: 这 17 行不改 ⇒ 已有通道的闸 W5 当场红·见 §2.4★) ★

### ★1.5 · 「随板改」那一类在改板那一趟的具体改法 (★照沙盒 T2b 实跑出来的★)

★**改板那一趟 (S9) 的动作 = 把【规格页引用】那一类一次改齐** ★[实测]
★**沙盒实测**: ★只把 17 处「规格页引用」里的 12 个页面 (★`SW/BOARD_ONEPASS_SW_SYNC.md` / `SW/BOARD_ONEPASS_LEGB_SW_IMPACT.md` / `SW/BOARD_ONEPASS_FP_TRUTH_*` / `SW/ONETRIP_*` / `SW/SW_NEEDS_TRIAGE.md` / `SW/DEMO_BOARD_60MS_VERDICT_PLAN.md` / `SW/LOAD_SWITCH_SELECTION_FACTS.md` / `SW/BOARD_ONEPASS_SW09_LANDING_PATCH.md`★) 里的旧 md5 换成新 md5 ⇒ ★**已有通道的闸 B 从 rc=1 变 rc=0** ★
★**★台账 (`SW/SW_MD5_BASELINE_LEDGER.md`) 与历史留证 (`SW/research/ISS250_r6_复核记录.md`) 不在其中 ⇒ 一行都不许动★** ★[实测]

### ★1.6 · 「不许改」那一类为什么一个字都不许动 (★三条理由·逐条可查★)

| 那一处 | 为什么不许动 | 证据等级 |
|---|---|---|
| ★台账锚点块 `hard_protected[板].md5` (`SW/SW_MD5_BASELINE_LEDGER.md` L61) ★ | ★ISS-284 ④: 保护基线必须留在台账链的链尾 ⇒ 改了就是「基线被偷偷前移」⇒ 闸当场红★ | [实测] |
| ★`SW/tools/check_onepass_sw_sync.py` L109 的 `ANCHOR_MD5` ★ | ★它的角色是【盯住台账锚点里的保护基线有没有被手改】⇒ 它自己一动, 盯防就失效了★ | [实测] |
| ★`SW/research/ISS250_r6_复核记录.md` L25 ★ | ★它是某次复核当时的读数留痕 (板 md5 / 18092 段走线 / 433 过孔 / unconnected=45 / 板↔网表 rc=1 / R3 矛盾 2 条 / G1 仍开) ⇒ 改它 = 改历史★ | [实测] |

### ★1.7 · 「判据锚」那一类的三类处置细分 (★11 行逐行★)

| 行 | 是什么 | 处置 | 为什么 |
|---|---|---|---|
| `SW/tools/check_fp_truth_read.py:87` | F5 的板 md5 硬比较目标 | ★**交 main 拍** ★ | ★改板当天必红; ★**但手改字面量 = 挖坑** ⇒ 只能走 §2 的通道补丁 P-C ⇒ 谁落/何时落 = main 排期★ |
| `SW/tools/check_onepass_legb_sw_impact.py:70` | G8 的 `PROTECTED_MD5["board_md5"]` | ★**交 main 拍** ★ | 同上 ⇒ 走 P-D |
| `SW/tools/check_onepass_sw_sync.py:109` | 锚点防篡改副本 | ★**不许改** ★ | 它的职责就是盯住基线 |
| `SW/tools/check_onepass_sw_sync.py:806/829/831/832` | `--selftest` 夹具里的假 md5 | ★**不许改** ★ | 它们是反向用例的输入, 不是判决锚 |
| `SW/SW_MD5_BASELINE_LEDGER.md:61` | 台账锚点里的保护基线 | ★**不许改** ★ | ISS-284 ④ |
| `SW/SW_MD5_BASELINE_LEDGER.md:114` | 落表台账行的格式模板 | ★**交 main 拍** ★ | ★那模板里的「改前 md5」在那一趟要换成当次的真值; ★但「模板本身要不要换成新基线」= main 的取舍 (★代价: 不换 ⇒ 模板永远停在旧基线; 换 ⇒ 模板失去恒定性与可读性★)★ |

### ★1.8 · 三类归属里【最容易判错】的三个坑 (★本单踩到了·记下来★)

★**坑 1**: ★同一个文件里三类都有 ★ —— `SW/SW_MD5_BASELINE_LEDGER.md` 一个文件里同时有【判据锚 L61 / 114】+【规格页引用 L131 / 134】+【历史留证 L164~L183 共 9 行】⇒ ★**不许按文件归并** ★
★**坑 2**: ★同一份 md5 在同一个页面里可能同时是「现状值」和「历史值」 ★ —— 例: `SW/BOARD_ONEPASS_LEGB_SW_IMPACT.md` L213/L221 (现状表 · 随板改) 与 L420 (零写板留痕 · 不许改) 在同一页 ⇒ ★**看那一行的角色, 不看那个文件§**
★**坑 3**: ★`.md` 页面里抄的判据脚本字面量, 归属是【规格页引用】不是【判据锚】 ★ —— 例: `SW/BOARD_ONEPASS_LEGB_SW_IMPACT.md` L75 抄了 `PROTECTED_MD5` 的字面量 ⇒ ★**它不参与判决, 但那一趟要跟着改 (免得页面与脚本说法不一致)★**

### ★1.9 · ★★扫描方法的一处实质订正 (★上一趟那套 grep 命令的坑★) ★

★**现象**: ★上一趟落的逐行清单 (`logs/iss372/02_scan_sw_md5_refs_lines.txt`) 只有 **46 行**, 而真实命中是 **47 行** —— ★**少的那一行是 `SW/SW_MD5_BASELINE_LEDGER.md` L173 (R-14 行)** ★
★**根因**: ★那套命令是 `grep -rn 611b869e SW/ | grep -v '\.bak\|__pycache__'` ⇒ ★**过滤是【行级】的, 不是【路径级】的** ⇒ ★L173 那行的正文里含 `state/.bak_iss220/HW_netlist_v1.csv.bak_iss220` ⇒ ★**整行被连带过滤掉了** ★
★**⇒ 计数没错 (57 处, 因为计数用的是另一条 `-o` 命令), 但【逐行清单】少一行** ★[实测]
★**⇒ 本单的做法**: ★**逐文件遍历 + 逐行计数** (★路径级排除 `.bak` / `__pycache__`·不做任何行级文本过滤★) ⇒ ★**不受该连带过滤影响**★ ⇒ ★机器闸 H1 也用同一口径 (⇒ 闸与本页读数永远一致)★

### ★1.10 · 机器可读清单 (★机器闸的判决源·本页 §1 的机器形态★)

★★**★下面这块 JSON 就是 `SW/tools/check_sw_board_md5_rebase_readiness.py` 的判决源★ ⇒ ★**它与 §1.3 的表格是同一份数据的两种形态★ (★由 `tmp/iss372/gen_manifest.py` 生成 ⇒ 不许手改这块 JSON★)★★**★

<!-- ISS372-MANIFEST:BEGIN -->
```json
{
 "schema": "iss372.sw_md5_rebase_readiness.v1",
 "generated_by": "tmp/iss372/gen_manifest.py (★ISS-372 · sw-lead · 2026-11-23★)",
 "board": {
  "rel": "HW/PCB/demo_mainboard.kicad_pcb",
  "md5": "611b869e13518c3c023fb178f91a0075",
  "mtime": "2026-11-06 07:07:17.362193413",
  "size": 4940213
 },
 "scan": {
  "needle_prefix": "611b869e",
  "exclude_paths": [
   "SW/BOARD_ONEPASS_SW_MD5_REBASE_READINESS.md",
   "SW/tools/check_sw_board_md5_rebase_readiness.py"
  ],
  "exclude_name_substr": [
   ".bak"
  ],
  "exclude_dirs": [
   "__pycache__"
  ],
  "method": "逐文件遍历 + 逐行计数 (★不用 grep·不受 grep -v 连带过滤影响★)"
 },
 "refs": [
  {
   "file": "SW/BOARD_ONEPASS_DEBUG_HEADER_FW_IMPACT.md",
   "line": 328,
   "occ": 1,
   "snippet": "…t -c '%y %s'`（开工前 / 交卷后各一次）★ | md5 **`611b869e13518c3c023fb178f91a0075`** · mtime **…",
   "cls": "历史留证",
   "action": "不许改",
   "note": "★【cont1 新增 · ISS-378 页 §7 边界自证表「零写板」那一行】★ ⇒ 记的是 2026-11-24 02:4x 交卷当时的三项读数 ⇒ 不许改★"
  },
  {
   "file": "SW/BOARD_ONEPASS_DEBUG_HEADER_FW_IMPACT.md",
   "line": 397,
   "occ": 1,
   "snippet": "\"board_md5\": \"611b869e13518c3c023fb178f91a0075\",",
   "cls": "判据锚",
   "action": "交 main 拍",
   "note": "★★【cont1 新增 · ★★本单最要紧的一条★★】★★ 这一行在 ```json iss378_contract``` 机器块的 ★\"baseline\".\"board_md5\"★ ⇒ ★它是闸 SW/tools/check_debug_header_fw_impact.py 的 W7 (w7_zero_write) 的【判决源】: W7 拿机器块里的 baseline.board_md5 跟盘上实测比 ⇒ 不等就红 ⇒ ★所以它【不是规格页引用】, 是【判据锚】★★ ⇒ ★★它是本单 H4 检测盲区的活证据: 该闸源码里【没有 32 位字面量】(它自己算 md5), 钉板 md5 靠的是【页面内嵌基线】⇒ 上一趟只扫 .py 字面量的检测网【抓不到它】★★ ⇒ 必须走 §2 补丁 P-G ⇒ 谁落/何时落 = main 排期"
  },
  {
   "file": "SW/BOARD_ONEPASS_DEBUG_PIN_ORDER_CONTRACT.md",
   "line": 282,
   "occ": 1,
   "snippet": "…at -c '%y %s'`（开工前 / 交卷后各一次） | md5 **`611b869e13518c3c023fb178f91a0075`** · mtime **…",
   "cls": "历史留证",
   "action": "不许改",
   "note": "★【cont1 新增 · ISS-375 页 §4-2 边界自证表「零写板」那一行】★ ⇒ 它记的是 2026-11-24 02:0x 交卷当时的三项读数 ⇒ 某一次交卷当时的事实 ⇒ 不许改★"
  },
  {
   "file": "SW/BOARD_ONEPASS_DEBUG_PIN_ORDER_CONTRACT.md",
   "line": 338,
   "occ": 1,
   "snippet": "…** (板 md5 / mtime / size 三项未动, 板指纹仍为 `611b869e13518c3c023fb178f91a0075` / `2026-11-0…",
   "cls": "历史留证",
   "action": "不许改",
   "note": "★【cont1 新增 · ISS-375 页【追加式订正 (2026-11-24 02:5x)】段末的「板指纹仍为 …」】★ ⇒ 它记的是那个追加时刻的事实 ⇒ 不许改★"
  },
  {
   "file": "SW/BOARD_ONEPASS_DEBUG_PIN_ORDER_CONTRACT.md",
   "line": 357,
   "occ": 1,
   "snippet": "…无冲突** (板 md5 / mtime / size 三项未动, 仍为 `611b869e13518c3c023fb178f91a0075` / `2026-11-0…",
   "cls": "历史留证",
   "action": "不许改",
   "note": "★【cont1 新增 · ISS-375 页【追加式订正 (2026-11-24 04:3x · cont3)】段首的「板 md5 / mtime / size 三项未动, 仍为 …」】★ ⇒ 它记的是那个追加时刻的事实 ⇒ 不许改★"
  },
  {
   "file": "SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md",
   "line": 164,
   "occ": 1,
   "snippet": "…链头取代的历史值 ⇒ 不许照抄 ⇒ 退休; ★它正文里另外那 2 个 (板 611b869e / .kicad_pro 3e504d2b) 是【受保护 5 件的盘上现值…",
   "cls": "规格页引用",
   "action": "随板改",
   "note": "★登记项: 板 md5 = 受保护 5 件的盘上现值 ⇒ 那一趟随板改★"
  },
  {
   "file": "SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md",
   "line": 217,
   "occ": 1,
   "snippet": "…1_reanchor_netlist_md5_sw | NEED-MD5: 611b869e13518c3c023fb178f91a0075 | PRODUCED-BY…",
   "cls": "规格页引用",
   "action": "随板改",
   "note": "★NEED-KEY 登记行 (板 md5 = 盘上现值) ⇒ 那一趟随板改★"
  },
  {
   "file": "SW/BOARD_ONEPASS_FP_TRUTH_READ_ENTRY.md",
   "line": 14,
   "occ": 1,
   "snippet": "…HW/PCB/demo_mainboard.kicad_pcb` ★ | `611b869e13518c3c023fb178f91a0075` | `2026-11-0…",
   "cls": "规格页引用",
   "action": "随板改",
   "note": "★§1 清单第 1 行 (板 + md5 + mtime + size) ⇒ 它是 ISS-363 闸 F4 的被检对象 ⇒ 那一趟随板改★"
  },
  {
   "file": "SW/BOARD_ONEPASS_LEGB_SW_IMPACT.md",
   "line": 75,
   "occ": 1,
   "snippet": "\"board_md5\": \"611b869e13518c3c023fb178f91a0075\",",
   "cls": "规格页引用",
   "action": "随板改",
   "note": "★页里抄了判据脚本的 PROTECTED_MD5 字面量 ⇒ 那一趟随板改 (它抄的是判据, 不是判决源)★"
  },
  {
   "file": "SW/BOARD_ONEPASS_LEGB_SW_IMPACT.md",
   "line": 213,
   "occ": 1,
   "snippet": "…d.kicad_pcb` | 2026-11-06 07:07:17 | `611b869e13518c3c023fb178f91a0075` (= 基线) | 未动…",
   "cls": "规格页引用",
   "action": "随板改",
   "note": "★现状表 (板 md5 = 基线 · 未动) ⇒ 那一趟随板改★"
  },
  {
   "file": "SW/BOARD_ONEPASS_LEGB_SW_IMPACT.md",
   "line": 221,
   "occ": 1,
   "snippet": "…`HW/PCB/demo_mainboard.kicad_pcb` | `611b869e13518c3c023fb178f91a0075` | 4,940,213…",
   "cls": "规格页引用",
   "action": "随板改",
   "note": "★板双证表 (md5 / size / mtime) ⇒ 那一趟随板改★"
  },
  {
   "file": "SW/BOARD_ONEPASS_LEGB_SW_IMPACT.md",
   "line": 420,
   "occ": 1,
   "snippet": "…只发生在 `tmp/iss370_sbx/` 的副本上 | ★板 md5 `611b869e13518c3c023fb178f91a0075` + mtime `202…",
   "cls": "历史留证",
   "action": "不许改",
   "note": "★零写板自证留痕 (交卷前后逐字节相同) ⇒ 某一次交卷当时的事实 ⇒ 不许改★"
  },
  {
   "file": "SW/BOARD_ONEPASS_SW09_LANDING_PATCH.md",
   "line": 36,
   "occ": 1,
   "snippet": "| R8 | 板 md5 / mtime | `611b869e13518c3c023fb178f91a0075` / `2026-11-0…",
   "cls": "规格页引用",
   "action": "随板改",
   "note": "★R8 判据表 (板 md5 / mtime) ⇒ 那一趟随板改★"
  },
  {
   "file": "SW/BOARD_ONEPASS_SW09_LANDING_PATCH.md",
   "line": 481,
   "occ": 1,
   "snippet": "| 零写板 | 板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `202…",
   "cls": "历史留证",
   "action": "不许改",
   "note": "★零写板留痕 (未变 [实测]) ⇒ 某一次交卷当时的事实 ⇒ 不许改★"
  },
  {
   "file": "SW/BOARD_ONEPASS_SW_SYNC.md",
   "line": 38,
   "occ": 1,
   "snippet": "…上 = §4 三方案★) ★ | ★**[实测]** 盘上板 md5 = `611b869e13518c3c023fb178f91a0075` · 台账 §1 `har…",
   "cls": "规格页引用",
   "action": "随板改",
   "note": "★★【SW01_PCB_MD5 清单第 1 条的 current_state】⇒ 它被 SW/tools/check_onepass_sw_sync.py 的 W5 当【现状值】读 ⇒ ★那一趟不换基线 ⇒ W5 当场红 (沙盒 T2 实测: B 闸 rc=1)★ ⇒ 必须随板改★"
  },
  {
   "file": "SW/BOARD_ONEPASS_SW_SYNC.md",
   "line": 94,
   "occ": 1,
   "snippet": "| SW 台账 `hard_protected` 钉死的板 md5 | `611b869e13518c3c023fb178f91a0075` | `SW/SW_MD5…",
   "cls": "规格页引用",
   "action": "随板改",
   "note": "★现状表 (台账钉死的板 md5) ⇒ 那一趟随板改★"
  },
  {
   "file": "SW/BOARD_ONEPASS_SW_SYNC.md",
   "line": 167,
   "occ": 1,
   "snippet": "…\"current_state\": \"[实测] 盘上板 md5 = 611b869e13518c3c023fb178f91a0075 · 台账 §1 hard_…",
   "cls": "规格页引用",
   "action": "随板改",
   "note": "★§6 机器可读 JSON 块里的 current_state (W5 读它) ⇒ 那一趟随板改★"
  },
  {
   "file": "SW/DEMO_BOARD_60MS_VERDICT_PLAN.md",
   "line": 328,
   "occ": 1,
   "snippet": "…cad_pcb HW/netlist_v1.csv           # 611b869e… / c78f9912… (逐字节未变)",
   "cls": "规格页引用",
   "action": "随板改",
   "note": "★命令式复现注记 (12 位前缀) ⇒ 台账 §2 S-04 已定口径「保留 + 标注 · 命令式引用跑出来就是现值」⇒ 那一趟随板改★"
  },
  {
   "file": "SW/LOAD_SWITCH_SELECTION_FACTS.md",
   "line": 338,
   "occ": 1,
   "snippet": "…本单对 `HW/` 的写入量 = **0 字节** (只读)。板 md5 `611b869e…` 自始至终一字未改。",
   "cls": "历史留证",
   "action": "不许改",
   "note": "★md5 漂移归属叙述 (板 md5 自始至终一字未改) ⇒ 某一次交卷当时的事实 ⇒ 不许改★"
  },
  {
   "file": "SW/ONETRIP_SW_POSTRENAME_GATE_SOP.md",
   "line": 18,
   "occ": 1,
   "snippet": "…`tmp/iss327/` 的沙盒副本上做; 真件板只读 | 板 md5 `611b869e13518c3c023fb178f91a0075` + mtime `202…",
   "cls": "历史留证",
   "action": "不许改",
   "note": "★零写板留痕 (交卷前后逐字节相同) ⇒ 不许改★"
  },
  {
   "file": "SW/ONETRIP_SW_POSTRENAME_GATE_SOP.md",
   "line": 63,
   "occ": 1,
   "snippet": "★**期望读数**: ★**板 md5 ≠ `611b869e13518c3c023fb178f91a0075`** (★改了板 ⇒ md…",
   "cls": "规格页引用",
   "action": "随板改",
   "note": "★【期望读数: 板 md5 ≠ 611b869e…】(改了板 ⇒ md5 必须变) ⇒ 这是改板那一趟的判据式描述 ⇒ 那一趟随板改 (改成「≠ <新板 md5>」)★"
  },
  {
   "file": "SW/ONETRIP_SW_POSTRENAME_GATE_SOP.md",
   "line": 310,
   "occ": 1,
   "snippet": "…的原文是 `基线就不绿: ['R6 硬保护: … (fadf2c2f… ≠ 611b869e…)', 'R6 台账链: …']` ⇒ ★**它红在步 7 (md5 重锚…",
   "cls": "历史留证",
   "action": "不许改",
   "note": "★某一次实测的报错原文引用 (rc=2 的原文) ⇒ 不许改★"
  },
  {
   "file": "SW/ONETRIP_SW_POSTRENAME_GATE_SOP.md",
   "line": 508,
   "occ": 1,
   "snippet": "…单号>/md5_pre_board.txt` | ★**改前的板指纹 = `611b869e13518c3c023fb178f91a0075`★** ⇒ ★**证明「板…",
   "cls": "规格页引用",
   "action": "随板改",
   "note": "★流程表「板 md5 (改前)」⇒ 那一趟的改前指纹 = 新基线 ⇒ 那一趟随板改★"
  },
  {
   "file": "SW/ONETRIP_SW_RENAME_SAFETY.md",
   "line": 409,
   "occ": 1,
   "snippet": "…m HW/PCB/demo_mainboard.kicad_pcb` = `611b869e13518c3c023fb178f91a0075` · mtime = `2…",
   "cls": "历史留证",
   "action": "不许改",
   "note": "★零写板留痕 ⇒ 不许改★"
  },
  {
   "file": "SW/ONETRIP_SW_SAMEBATCH_RENAME_LIST.md",
   "line": 492,
   "occ": 1,
   "snippet": "…HW/PCB/demo_mainboard.kicad_pcb (… ≠ 611b869e13518c3c023fb178f91a0075)']",
   "cls": "历史留证",
   "action": "不许改",
   "note": "★反向用例的报错原文引用 ⇒ 不许改★"
  },
  {
   "file": "SW/ONETRIP_SW_SAMEBATCH_RENAME_LIST.md",
   "line": 619,
   "occ": 1,
   "snippet": "…\"current_state\": \"[实测] 盘上板 md5 = 611b869e13518c3c023fb178f91a0075 · 台账 §1 hard_…",
   "cls": "规格页引用",
   "action": "随板改",
   "note": "★抄了清单页的 current_state (W5 同源口径) ⇒ 那一趟随板改★"
  },
  {
   "file": "SW/ONETRIP_SW_SAMEBATCH_RENAME_LIST.md",
   "line": 870,
   "occ": 1,
   "snippet": "…/PCB/demo_mainboard.kicad_pcb` md5 = `611b869e13518c3c023fb178f91a0075` · mtime = `2…",
   "cls": "历史留证",
   "action": "不许改",
   "note": "★零写板留痕 ⇒ 不许改★"
  },
  {
   "file": "SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md",
   "line": 211,
   "occ": 1,
   "snippet": "…b` + `stat -c '%y'` 开工前后各一次 | ★**md5 `611b869e13518c3c023fb178f91a0075` / mtime `202…",
   "cls": "历史留证",
   "action": "不许改",
   "note": "★零写板留痕 ⇒ 不许改★"
  },
  {
   "file": "SW/SW_MD5_BASELINE_LEDGER.md",
   "line": 61,
   "occ": 1,
   "snippet": "md5: 611b869e13518c3c023fb178f91a0075",
   "cls": "判据锚",
   "action": "不许改",
   "note": "★§1 锚点块 hard_protected[板].md5 = 保护基线 ⇒ ISS-284 ④: 保护基线必须留在台账链尾 ⇒ 永远不许改★"
  },
  {
   "file": "SW/SW_MD5_BASELINE_LEDGER.md",
   "line": 114,
   "occ": 1,
   "snippet": "…`HW/PCB/demo_mainboard.kicad_pcb` | `611b869e13518c3c023fb178f91a0075` | `<新板 md5>`…",
   "cls": "判据锚",
   "action": "交 main 拍",
   "note": "★§1 ISS-284 ⑥ 给 main 的落表台账行格式模板 (改前 md5 = 当次改板前的值) ⇒ 那一趟由 main 照此写新行; ★模板本身要不要换成新基线 = main 拍 (代价: 不换 = 模板永远是旧基线, 换 = 模板失去「格式样例」的恒定性与可读性)★"
  },
  {
   "file": "SW/SW_MD5_BASELINE_LEDGER.md",
   "line": 131,
   "occ": 1,
   "snippet": "…网表 `c78f9912…` / 脚表 `4814617e…` / 板 `611b869e…` / `.kicad_pro` `3e504d2b…` | ★**恒红*…",
   "cls": "规格页引用",
   "action": "随板改",
   "note": "★§2 S-01 行 = check_demo_panel_spec 的 PROTECTED_MD5 字面量【现状登记】⇒ 改板那一趟随板改★"
  },
  {
   "file": "SW/SW_MD5_BASELINE_LEDGER.md",
   "line": 134,
   "occ": 1,
   "snippet": "…PLAN.md` L328 | ★**文档 · 复现命令注记** ★ | `611b869e… / c78f9912…` (12 位前缀) | 文档口径**过期** |…",
   "cls": "规格页引用",
   "action": "随板改",
   "note": "★§2 S-04 行 = DEMO_BOARD_60MS_VERDICT_PLAN L328 的【现状登记】⇒ 改板那一趟随板改★"
  },
  {
   "file": "SW/SW_MD5_BASELINE_LEDGER.md",
   "line": 164,
   "occ": 2,
   "snippet": "…脚表 `ef436a37…` / BOM `2a730574…` / 板 `611b869e…` / `.kicad_pro` `3e504d2b…` 四件逐字节不变…",
   "cls": "历史留证",
   "action": "不许改",
   "note": "★§3 R-08 留痕行 (ISS-249 / ISS-254 第 5 跳重锚当时的事实) ⇒ 改它 = 改历史★"
  },
  {
   "file": "SW/SW_MD5_BASELINE_LEDGER.md",
   "line": 166,
   "occ": 2,
   "snippet": "…94642d07…` 不在 R6 的受管真源里 ⇒ 只登记不许改★; 板 `611b869e…` / `.kicad_pro` `3e504d2b…` 逐字节不变 ⇒…",
   "cls": "历史留证",
   "action": "不许改",
   "note": "★§3 R-09 留痕行 (ISS-257 / ISS-258 第 6 跳重锚当时的事实) ⇒ 改它 = 改历史★"
  },
  {
   "file": "SW/SW_MD5_BASELINE_LEDGER.md",
   "line": 168,
   "occ": 2,
   "snippet": "…/ 网表 / 脚表 / BOM 五个 md5 交卷前后逐字节不变** (★`611b869e…` / `3e504d2b…` / `e06c1dd6…` / `287e…",
   "cls": "历史留证",
   "action": "不许改",
   "note": "★§3 R-10 留痕行 (ISS-275 判决源换源当时的事实) ⇒ 改它 = 改历史★"
  },
  {
   "file": "SW/SW_MD5_BASELINE_LEDGER.md",
   "line": 170,
   "occ": 3,
   "snippet": "…W/PCB/demo_mainboard.kicad_pcb` (… ≠ `611b869e…`)」 ⇒ ★**「板只改一次」那一趟 (S1~S13) 合法地就要改板…",
   "cls": "历史留证",
   "action": "不许改",
   "note": "★§3 R-11 留痕行 (ISS-279「设计上无路」当时的事实) ⇒ 改它 = 改历史★"
  },
  {
   "file": "SW/SW_MD5_BASELINE_LEDGER.md",
   "line": 171,
   "occ": 3,
   "snippet": "…W/PCB/demo_mainboard.kicad_pcb` (… ≠ `611b869e…`)」 ⇒ ★**那一趟合法改板当天 SW R6 必红, 而手改 `har…",
   "cls": "历史留证",
   "action": "不许改",
   "note": "★§3 R-12 留痕行 (ISS-284 合法改板机制落地当时的事实) ⇒ 改它 = 改历史★"
  },
  {
   "file": "SW/SW_MD5_BASELINE_LEDGER.md",
   "line": 172,
   "occ": 2,
   "snippet": "…o` 的两个 md5 仍然一个字不许动** (★ISS-279 交卷基线 `611b869e…` / `3e504d2b…`★) ⇒ ★**「不许手改 md5 凑绿」照…",
   "cls": "历史留证",
   "action": "不许改",
   "note": "★§3 R-13 留痕行 (ISS-279 收口轮 W6 基线口径订正当时的事实) ⇒ 改它 = 改历史★"
  },
  {
   "file": "SW/SW_MD5_BASELINE_LEDGER.md",
   "line": 173,
   "occ": 2,
   "snippet": "…个字节**★ ⇒ ★**板 / `.kicad_pro` 逐字节不变 (★`611b869e…` / `3e504d2b…★)** ★ | ★**`python3 SW…",
   "cls": "历史留证",
   "action": "不许改",
   "note": "★§3 R-14 留痕行 (ISS-279 收口轮 W6 链头判据收严当时的事实) ⇒ 改它 = 改历史★ ★★【本机新发现 ★ 上两趟那套 `grep -v '\\.bak'` 的逐行清单把这一行漏掉了! ★ 原因: 这一行的正文里含 `state/.bak_iss220/…` ⇒ 被那条过滤规则【连带】过滤 ⇒ 计数 (57 处) 对, 但【逐行清单】少一行 ⇒ 本单改用逐文件遍历 + 逐行计数 (★不受该连带过滤影响★)★]"
  },
  {
   "file": "SW/SW_MD5_BASELINE_LEDGER.md",
   "line": 181,
   "occ": 1,
   "snippet": "…7` (同批同刻, ★不在 R6 受管真源里 ⇒ 只登记不许改★); 板 `611b869e13518c3c023fb178f91a0075` / `.kicad_pr…",
   "cls": "历史留证",
   "action": "不许改",
   "note": "★§3 追加段 (ISS-258 第 6 跳重锚当时的事实) ⇒ 不许改★"
  },
  {
   "file": "SW/SW_MD5_BASELINE_LEDGER.md",
   "line": 183,
   "occ": 1,
   "snippet": "…9b93607` (★不在 R6 受管真源里 ⇒ 只登记不许改★); 板 `611b869e13518c3c023fb178f91a0075` / `.kicad_pr…",
   "cls": "历史留证",
   "action": "不许改",
   "note": "★§3 追加段 (ISS-275 判决源换源当时的事实) ⇒ 不许改★"
  },
  {
   "file": "SW/SW_NEEDS_TRIAGE.md",
   "line": 186,
   "occ": 1,
   "snippet": "…7f62ac3…/脚表 a4270120…/BOM 5d02bece…/板 611b869e… 四个 md5 逐字节不变) ⇒ 且该禁令被新闸 SW/tools/che…",
   "cls": "历史留证",
   "action": "不许改",
   "note": "★已闭合 need 的闭环注 (四个 md5 逐字节不变) ⇒ 某一次交卷当时的事实 ⇒ 不许改★"
  },
  {
   "file": "SW/SW_NEEDS_TRIAGE.md",
   "line": 346,
   "occ": 1,
   "snippet": "| 板 md5 (钉板真值) | `611b869e13518c3c023fb178f91a0075` + mtime `202…",
   "cls": "规格页引用",
   "action": "随板改",
   "note": "★判据表行「板 md5 (钉板真值)」⇒ 那一趟随板改★"
  },
  {
   "file": "SW/SW_NEEDS_TRIAGE.md",
   "line": 359,
   "occ": 1,
   "snippet": "| 板 md5 `611b869e13518c3c023fb178f91a0075` + mtime `202…",
   "cls": "历史留证",
   "action": "不许改",
   "note": "★证据表行 ([实测] · 交卷前后逐字节相同) ⇒ 某一次交卷当时的事实 ⇒ 不许改★"
  },
  {
   "file": "SW/research/ISS250_r6_复核记录.md",
   "line": 25,
   "occ": 1,
   "snippet": "….py` 实跑, 2026-11-17 05:40★)**: 板 md5 `611b869e13518c3c023fb178f91a0075` (★自 11-06 07…",
   "cls": "历史留证",
   "action": "不许改",
   "note": "★★【本单唯一的「某次复核当时的读数留痕」⇒ 永远不许改】★★ 它的正文里还有板侧硬数字 (板 md5 / 18092 段走线 / 433 过孔 / unconnected=45 / 板↔网表 rc=1 / R3 矛盾 2 条 / G1 仍开) ⇒ 那都是 2026-11-17 05:40 的读数 ⇒ 一律不许改"
  },
  {
   "file": "SW/tools/check_debug_pin_order_contract.py",
   "line": 53,
   "occ": 1,
   "snippet": "BOARD_MD5 = \"611b869e13518c3c023fb178f91a0075\"",
   "cls": "判据锚",
   "action": "交 main 拍",
   "note": "★★【cont1 新增 · ISS-375 (2026-11-24 02:05 交付) 的闸 D7 硬钉目标】★★ BOARD_MD5/BOARD_MTIME/BOARD_SIZE 三个常量 ⇒ ★该闸 D7 判「盘上板指纹三项 == 这三个常量」⇒ 改板当天必红 ⇒ ★手改字面量 = 挖坑 ⇒ 不许★ ⇒ 必须走 §2 补丁 P-F ⇒ 谁落/何时落 = main 排期"
  },
  {
   "file": "SW/tools/check_fp_truth_read.py",
   "line": 87,
   "occ": 1,
   "snippet": "BOARD_BASELINE_MD5 = \"611b869e13518c3c023fb178f91a0075\"",
   "cls": "判据锚",
   "action": "交 main 拍",
   "note": "★F5 的板 md5 硬比较目标 (ISS-363 今天 17:27 交付) ⇒ 改板当天必红 ⇒ ★手改字面量 = 挖坑 ⇒ 不许★ ⇒ 必须走 §2 补丁 P-C ⇒ 谁落/何时落 = main 排期"
  },
  {
   "file": "SW/tools/check_onepass_legb_sw_impact.py",
   "line": 70,
   "occ": 1,
   "snippet": "\"board_md5\": \"611b869e13518c3c023fb178f91a0075\",",
   "cls": "判据锚",
   "action": "交 main 拍",
   "note": "★G8 的 PROTECTED_MD5['board_md5'] (ISS-370 今天 19:50 交付) ⇒ 改板当天必红 ⇒ ★手改字面量 = 挖坑 ⇒ 不许★ ⇒ 必须走 §2 补丁 P-D ⇒ 谁落/何时落 = main 排期"
  },
  {
   "file": "SW/tools/check_onepass_sw_sync.py",
   "line": 109,
   "occ": 1,
   "snippet": "…\"HW/PCB/demo_mainboard.kicad_pcb\": \"611b869e13518c3c023fb178f91a0075\",",
   "cls": "判据锚",
   "action": "不许改",
   "note": "★ANCHOR_MD5 = 锚点防篡改副本 ⇒ 它的角色是【盯住台账锚点里的保护基线有没有被手改】⇒ ISS-284 语义: 锚点里的 md5 永远不许改★ (已跑通的合法改板通道闸)"
  },
  {
   "file": "SW/tools/check_onepass_sw_sync.py",
   "line": 806,
   "occ": 2,
   "snippet": "\"611b869e13518c3c023fb178f91a0075\", \"611b869e13…",
   "cls": "判据锚",
   "action": "不许改",
   "note": "★--selftest 夹具里的假 md5 对 (基准/改后) ⇒ 是反向用例的输入, 不是判决锚★"
  },
  {
   "file": "SW/tools/check_onepass_sw_sync.py",
   "line": 829,
   "occ": 1,
   "snippet": "assert \"611b869e13518c3c023fb178f91a0075\" in t",
   "cls": "判据锚",
   "action": "不许改",
   "note": "★--selftest 夹具断言 ⇒ 同上★"
  },
  {
   "file": "SW/tools/check_onepass_sw_sync.py",
   "line": 831,
   "occ": 1,
   "snippet": "f.write(t.replace(\"md5: 611b869e13518c3c023fb178f91a0075\",",
   "cls": "判据锚",
   "action": "不许改",
   "note": "★--selftest 夹具写入 (把基线改成假值) ⇒ 同上★"
  },
  {
   "file": "SW/tools/check_onepass_sw_sync.py",
   "line": 832,
   "occ": 1,
   "snippet": "\"md5: 611b869e13518c3c023fb178f91a0076\", 1))",
   "cls": "判据锚",
   "action": "不许改",
   "note": "★--selftest 夹具写入 (假值那一侧) ⇒ 同上★"
  },
  {
   "file": "SW/BOARD_ONEPASS_ZERO_FALSE_CONNECTIVITY.md",
   "line": 23,
   "occ": 1,
   "snippet": "| 1 | 板指纹 | md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · size `4940213` ⇒ **19 天逐字节未动** |",
   "cls": "规格页引用",
   "action": "交 main 拍",
   "note": "★【ISS-408 补登记 · 第 54 行】★ 它在 ISS-381 页 §1「板面真值」表第 1 行 ⇒ 自述盘上【当前】板指纹 + 挂一条活的复现命令 ⇒ 它不是判决源 (既不是 .py 里的比较目标, 也不是任何闸的机器基线) ⇒ 按 §1.2 落在【规格页引用】这一侧 ⇒ ★**但归属方向归 main (§6 Q1)**: 若判【历史留证】⇒ 永远不许改 ⇒ 板那一趟板面变了这一行还写着旧 md5 ⇒ 页面说谎; 若判【规格页引用】⇒ 改板那一趟必须跟着改 ⇒ 要进 S9 换基线清单 ⇒ ★**两个方向结论相反 ⇒ 本单只登记 + 给代价, 不代拍**★"
  },
  {
   "file": "SW/BOARD_ONEPASS_ZERO_FALSE_CONNECTIVITY.md",
   "line": 241,
   "occ": 1,
   "snippet": "| ★零写板★ | 板 md5 `611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17.362193413` / size `4940213` 开工前后对照 `logs/iss381/baseline_fingerprints.txt` | ★**逐字相同** (开工前 / 交卷后两次实测输出见 `logs/iss381/boundary_proof.txt`) ★ |",
   "cls": "历史留证",
   "action": "不许改",
   "note": "★【ISS-408 补登记 · 第 55 行】★ 它在 ISS-381 页 §7「边界自证」表「零写板」那一行 ⇒ 记的是某一次交卷当时的前后对照结果 (并指向 logs/iss381/boundary_proof.txt 那两份实测输出) ⇒ ★**同款形状在 §1.3 第 1 行已有先例** (ISS-378 页 §7 的同款行 = 历史留证 / 不许改) ⇒ 口径一致 ⇒ 处置取 fail-safe 方向「不许改」 ⇒ ★**改历史留证 = 造假记录, 比留着旧数更坏** ⇒ 若 main 认为它应当随板改, 那是一次重签历史页的动作, 本单不代拍★"
  },
  {
   "file": "SW/EVT_CHARGE_CURRENT_CRITERION_CALIBER.md",
   "line": 215,
   "occ": 1,
   "snippet": "⑦ 板三项指纹 (md5 `611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17.362193413` / size 4940213) 前后逐字相同",
   "cls": "历史留证",
   "action": "不许改",
   "note": "★【ISS-408 补登记 · 第 56 行】★ 它在 ISS-385 页 §5「证据分级表」的 [实测] 行第 ⑦ 条 ⇒ 记的是那一次交卷当时「前后逐字相同」的对照结论 ⇒ 逐字对上 §1.2 的【历史留证】定义 ⇒ 处置取 fail-safe 方向「不许改」 ⇒ 若 main 认为它应当随板改, 那是一次重签历史页的动作, 本单不代拍★"
  },
  {
   "file": "SW/tools/check_sw_false_connectivity_gate.py",
   "line": 73,
   "occ": 1,
   "snippet": "BASELINE_BOARD_MD5 = \"611b869e13518c3c023fb178f91a0075\"",
   "cls": "判据锚",
   "action": "交 main 拍",
   "note": "★【ISS-408 补登记 · 第 57 行】★ 它是 ISS-381 那道零假连通闸的板 md5 硬比较目标 (★同文件 L448 `if md5 != BASELINE_BOARD_MD5:` 把它喂给失败清单 ⇒ 盘上一变必红★) ⇒ ★**H3 明确规定「历史留证不许落在 .py 判据脚本上」⇒ .py 里的板 md5 字面量只能是判据锚**★ ⇒ 处置方向归 main (§6 Q2): 停在补进 §2 账, 还是改成走合法改板通道 (★后者要动一道已签收闸 ⇒ 需重签★)"
  }
 ],
 "gates": [
  {
   "file": "SW/tools/check_fp_truth_read.py",
   "line": 87,
   "id": "F5",
   "title": "零写板 + 零落表自证 (★板双证 md5/mtime/size + 三源台账可查★)",
   "built_by": "ISS-363 (★2026-11-23 17:27 交付★)",
   "channel": false,
   "status": "已知缺口",
   "gap_id": "iss372_gap_f5_reboard_channel",
   "owner": "sw-lead 落补丁 (★但时点由 main 排期★)",
   "spec": "P-C"
  },
  {
   "file": "SW/tools/check_onepass_legb_sw_impact.py",
   "line": 70,
   "id": "G8",
   "title": "板/网表/脚表/BOM 四份真源 md5 逐字节等于受保护基线",
   "built_by": "ISS-370 (★2026-11-23 19:50 交付★)",
   "channel": false,
   "status": "已知缺口",
   "gap_id": "iss372_gap_g8_reboard_channel",
   "owner": "sw-lead 落补丁 (★但时点由 main 排期★)",
   "spec": "P-D"
  },
  {
   "file": "SW/tools/check_onepass_sw_sync.py",
   "line": 109,
   "id": "W6 / ANCHOR_MD5",
   "title": "受保护 5 件基线口径 + 硬保护两件走【合法改板通道】",
   "built_by": "ISS-279 (★2026-11-17★)",
   "channel": true,
   "status": "已有通道",
   "gap_id": null,
   "owner": "— (★已跑通: 台账链头 + reboard 四项原子映射 ★判据逐字照搬权威闸★)",
   "spec": "—"
  },
  {
   "file": "HW/check_iss354_manufacturability.py",
   "line": 40,
   "id": "A-5a / A-5b",
   "title": "零写板: 板指纹 md5 + mtime",
   "built_by": "ISS-354",
   "channel": false,
   "status": "已知缺口(★跨域·hw-lead 的域★)",
   "gap_id": "iss372_gap_iss354_reboard_channel",
   "owner": "hw-lead (★SW 侧只登记 + 给补丁规格 P-E·不越界改★)",
   "spec": "P-E"
  },
  {
   "file": "SW/tools/check_debug_pin_order_contract.py",
   "line": 53,
   "id": "D7",
   "title": "零写板: 板指纹三项 (md5 + mtime + size) 未动",
   "built_by": "ISS-375 (★2026-11-24 02:05 交付★)",
   "channel": false,
   "status": "已知缺口",
   "gap_id": "iss372_gap_iss375_d7_reboard_channel",
   "owner": "sw-lead 落补丁 (★但时点由 main 排期★)",
   "spec": "P-F"
  },
  {
   "file": "SW/tools/check_debug_header_fw_impact.py",
   "line": 397,
   "id": "W7",
   "title": "零写板 + 零落表自证: 板指纹三项 + 网表/脚表/BOM 三件 md5 全部与基线一致",
   "built_by": "ISS-378 (★2026-11-24 02:45 交付★)",
   "channel": false,
   "status": "已知缺口",
   "gap_id": "iss372_gap_iss378_w7_reboard_channel",
   "owner": "sw-lead 落补丁 (★但时点由 main 排期★)",
   "spec": "P-G"
  },
  {
   "file": "SW/tools/check_sw_false_connectivity_gate.py",
   "line": 73,
   "id": "ZFC-1",
   "title": "缺口归属: 零假连通自检闸的板指纹三项硬比较 (★类A · .py 内 32 位字面量 · L73/L74/L75★) ⇒ 改板当天必红 ⇒ 代码级没有合法改板通道",
   "built_by": "ISS-381 (★2026-11-24 交卷★)",
   "channel": false,
   "status": "已知缺口",
   "gap_id": "iss408_gap_zfc1_reboard_channel",
   "owner": "sw-lead 落补丁 (★但时点由 main 排期★)",
   "spec": "P-Z"
  }
 ],
 "evidence_levels": [
  "[官网]",
  "[实测]",
  "[媒体]",
  "[推算]",
  "[0数据]"
 ]
}
```
<!-- ISS372-MANIFEST:END -->

---

## ★2 · 「改板那天会假红」的逐闸账 (★沙盒实跑读数·不推理★)

### ★2.1 · 沙盒预演的形状 (★零写板★)

★**沙盒树**: `tmp/iss372/tree` (★从上一趟落的母本 `tmp/iss372_sbx/tree` 重拷 ⇒ 每次跑都可复现★) ★
★**脚本**: `tmp/iss372/exp2_reboard.py` (★驱动★) + `tmp/iss372/patch_spec.py` (★补丁规格原型★) + `tmp/iss372/legal_channel_sbx.py` (★通道原型★)
★**留证**: `logs/iss372/05_sbx_reboard_rehearsal.txt` (★全部读数★)
★**六个阶段**:

| 阶段 | 沙盒动作 | 读数意义 |
|---|---|---|
| **T0** | 原封不动 | 基线: 5 道闸全绿 |
| **T1** | ★**朴素改板**: 板追加一个字节, 不落表不写 reboard ★ | 未授权改板 ⇒ 各闸当场红 |
| **T2** | ★**合法改板**: ISS-284 四项原子映射 + 落表台账链头 + issue_log 留痕 ★ | 合法改板 ⇒ ★**只有已有通道的闸回绿** ★ |
| **T2b** | ★**S9 换基线**: 把【规格页引用】那一类一次改齐 (★17 处·12 个页面★) ★ | 规格页也换基线后 ⇒ 已有通道的闸全绿 |
| **T4** | ★**补丁规格原型化**: 只在沙盒副本上给那 3 道没通道的闸打上通道补丁 ★ | 证明补丁规格这个形状可行 |
| **T5** | ★**板改第二次** (★通道已经存在★) | ★**纯 md5 硬保护支路没被放松 ⇒ 板改第二次当场被抓住** ★

### ★2.2 · 逐闸账 (★7 道·逐道给「硬钉位置 / 判据原文 / 会不会红 / 真含义 vs 误读 / 走哪条通道」★)

#### ★闸 A · 权威闸 `SW/tools/check_demo_panel_spec.py` 的 R6 (★**已有通道**★)★

| 项 | 内容 |
|---|---|
| 硬钉位置 | ★**不在 SW 域硬钉** ★ —— 它读台账锚点 `anchors.hard_protected[]` (★`SW/SW_MD5_BASELINE_LEDGER.md` L61★) ⇒ 它是【读锚点】不是【自己抄一份字面量】 |
| 判据原文 | `check_r6_hard_protected()`: ① 保护基线自证 ② 台账里没有变更行 ⇒ 纯 md5 硬保护 (盘上必须 == 基线) ③ 有变更行 ⇒ 链头唯一/链不断/链头有单号 + reboard 四项逐字对上 + 盘上 == 台账链头 ④ 同组受保护件成对覆盖 |
| 改板当天会不会红 | ★**T0 绿 → T1 红 → T2 绿** ⇒ ★**它天生有通道 ⇒ 合法改板当天不红** ★[实测] |
| 红的真含义 vs 会被误读成什么 | 真含义 = 「板被换了 (未授权)」; 会被误读成 = 「板改坏了」 |
| 该走哪条通道 | ★**已有**: 台账链头 + reboard 四项原子映射 (★ISS-284 已跑通·REV-16~REV-21 六条反向用例★) ★ |

#### ★闸 B · `SW/tools/check_onepass_sw_sync.py` 的 W6 (★**已有通道**·★但它红在【规格页】不在【判据】★)★

| 项 | 内容 |
|---|---|
| 硬钉位置 | ★**L109** `ANCHOR_MD5 = {"HW/PCB/demo_mainboard.kicad_pcb": "611b869e13518c3c023fb178f91a0075", ...}` ★ |
| 判据原文 | ① W6: 盘上 md5 必须能在落表台账里查到 (合法落表自动前移 · 偷换照红) ② 硬保护两件走【合法改板通道】(★判据逐字照搬权威闸 `check_r6_hard_protected()`★) ③ ★**W5: 8 个现状探针 = 清单里的现状值 == 盘面实测 ⇒ `SW/BOARD_ONEPASS_SW_SYNC.md` 的 `current_state` 里写着旧 md5 ⇒ 红** ★ |
| 改板当天会不会红 | ★**T0 绿 → T1 红 → T2 仍红 → T2b 绿** ⇒ ★**它会红一次·但红在【规格页过期】而不是【判据没有通道】★** ★[实测] |
| 红的真含义 vs 会被误读成什么 | 真含义 = 「规格页还没换基线 (S9 没做完)」; 会被误读成 = 「板改坏了」⇒ ★**这是 §1.5 那一类存在的直接证据** ★ |
| 该走哪条通道 | ★**已有** (判据侧) + ★**S9 换基线那一趟必须把规格页一起改** (见 §1.5) ★ |

#### ★闸 C · `SW/tools/check_fp_truth_read.py` 的 F5 (★**没有通道**·★今天 17:27 才造★)★

| 项 | 内容 |
|---|---|
| 硬钉位置 | ★**L87** `BOARD_BASELINE_MD5 = "611b869e13518c3c023fb178f91a0075"` (★同块还有 L88 `BOARD_BASELINE_MTIME` / L89 `BOARD_BASELINE_SIZE`★) |
| 判据原文 | `f5_zero_write_selfproof()`: ★`if b["md5"] != BOARD_BASELINE_MD5:` ⇒ 追加「板 md5=%s ≠ 基线 %s ⇒ 判红 (★板被换过 ⇒ 零写板自证失败★)」★ + mtime 比对 + size 比对 |
| 改板当天会不会红 | ★**T0 绿 → T1 红 → T2 红 → T2b 红 → T4 (打了补丁) 绿** ⇒ ★**没有通道 ⇒ 合法改板当天【仍红】★** ★[实测] |
| 红的真含义 vs 会被误读成什么 | 真含义 = 「板被换了 (合法, 但你不知道它合法)」; ★会被误读成 = 「板改坏了」⇒ ⇒ ★**现场极可能去改板凑绿 ⇒ 板 md5 变第二次 ⇒ 整趟白跑** ★ |
| 该走哪条通道 | ★**缺口**: 没有合法改板通道 ⇒ ★**补丁规格 P-C** (§2.3) · ★谁落 / 什么时候落 = main 排期★ |

#### ★闸 D · `SW/tools/check_onepass_legb_sw_impact.py` 的 G8 (★**没有通道**·★今天 19:50 才造★)★

| 项 | 内容 |
|---|---|
| 硬钉位置 | ★**L70** `"board_md5": "611b869e13518c3c023fb178f91a0075",` (★在 `PROTECTED_MD5` 四件套里★) |
| 判据原文 | `check_page()` 的 G8: 逐个比 `PROTECTED_MD5` 的 4 个键 ⇒ 板 md5 不等 ⇒ `bad.append("%s 盘上 md5 = %r ≠ 受保护基线 %r ⇒ 真源被改了")` |
| 改板当天会不会红 | ★**T0 绿 → T1 红 → T2 红 → T2b 红 → T4 (打了补丁) 绿** ⇒ ★**没有通道 ⇒ 合法改板当天【仍红】★** ★[实测] |
| 红的真含义 vs 会被误读成什么 | 同 C |
| 该走哪条通道 | ★**缺口** ⇒ ★**补丁规格 P-D** (§2.3) · ★谁落 / 什么时候落 = main 排期★ |

#### ★闸 E · `HW/check_iss354_manufacturability.py` 的 A-5a/A-5b (★**没有通道**·★跨域·hw-lead 的域★)★

| 项 | 内容 |
|---|---|
| 硬钉位置 | ★**L40** `EXPECT_PCB_MD5 = "611b869e13518c3c023fb178f91a0075"` + ★**L41** `EXPECT_PCB_MTIME = "2026-11-06 07:07:17.362193413"` ★ |
| 判据原文 | `check()` 的 A-5: `ok_pcb = (pcb_md5 == EXPECT_PCB_MD5)` ⇒ 不等即红; ★`ok_mt = EXPECT_PCB_MTIME in pcb_mt` ⇒ mtime 变了也红★ |
| 改板当天会不会红 | ★**T0 绿 → T1 红 → T2 红 → T2b 红 → T4 (打了补丁) 绿** ⇒ ★**没有通道 ⇒ 合法改板当天【仍红】★** ★[实测] |
| 红的真含义 vs 会被误读成什么 | 同 C |
| 该走哪条通道 | ★**缺口** ⇒ ★**补丁规格 P-E** (§2.3) · ★**本单只登记, 不越界改 (HW 域)** ★ |


#### ★闸 F · `SW/tools/check_debug_pin_order_contract.py` 的 D7 (★**没有通道**·★ISS-375 · 2026-11-24 02:05 交付★)★

| 项 | 内容 |
|---|---|
| 硬钉位置 | ★**L53** `BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"` (★同块 L54 `BOARD_MTIME` / L55 `BOARD_SIZE`★) |
| 判据原文 | `d7_board_fingerprint()`: `ok = (st["md5"] == BOARD_MD5 and st["size"] == BOARD_SIZE and mt == BOARD_MTIME)` ⇒ 任一不等就红 |
| 改板当天会不会红 | ★**T0 绿 → T1 红 → T2 红 → T2b 红 → T4 (打了补丁) 绿 → T5 红** ⇒ ★**没有通道 ⇒ 合法改板当天【仍红】★** ★[实测] (★沙盒 T0~T5 六阶段读数·`logs/iss372/08_sbx_reboard_rehearsal_7gates.txt`★) |
| 红的真含义 vs 会被误读成什么 | 真含义 = 「板被换了 (合法, 但你不知道它合法)」; ★会被误读成 = 「板改坏了」⇒ ⇒ ★**现场极可能去改板凑绿 ⇒ 板 md5 变第二次 ⇒ 整趟白跑** ★ |
| 该走哪条通道 | ★**缺口**: 没有合法改板通道 ⇒ ★**补丁规格 P-F** (§2.3) · ★谁落 / 什么时候落 = main 排期★ |

#### ★闸 G · `SW/tools/check_debug_header_fw_impact.py` 的 W7 (★**没有通道**·★ISS-378 · 2026-11-24 02:45 交付·★★「页面内嵌基线类」★)★

| 项 | 内容 |
|---|---|
| 硬钉位置 | ★**不在 .py 里** ★ —— ★**L397 在 `SW/BOARD_ONEPASS_DEBUG_HEADER_FW_IMPACT.md` 的 ```json iss378_contract``` 机器块的 `"baseline"."board_md5"`** ★ ⇒ ★**该闸自己算盘上 md5, 再跟这个页面里的基线比** ★ |
| 判据原文 | `w7_zero_write()`: `for key, live in (("board_md5", fp["board_md5"]), ("board_size", …))`: `want = bl.get(key)` ⇒ `if str(want) != str(live): errs.append("板指纹 %s: 基线 %r vs 实测 %r")`; ★另比 mtime (纳秒级) + 网表/脚表/BOM 三件 md5★ |
| 改板当天会不会红 | ★**T0 绿 → T1 红 → T2 红 → T2b 红 → T4 红 → T5 红** ⇒ ★**没有通道 ⇒ 合法改板当天【仍红】★** ★[实测] (★沙盒 T0~T5·`logs/iss372/08_sbx_reboard_rehearsal_7gates.txt`★) |
| ★**T2b 的红原文 (★最要紧的一条读数★)** ★ | ★**只剩 `board_size` 与 `board_mtime` 两条; `board_md5` 那一条【已经绿了】** ★ ⇒ ★**因为 T2b 把【规格页引用】那一类换基线时, 那个页面的 `baseline.board_md5` 跟着换了 ⇒ ★★【只换 md5 不够: size + mtime 也得换】★★ ★[实测] |
| 红的真含义 vs 会被误读成什么 | 同 F |
| 该走哪条通道 | ★**缺口**: 没有合法改板通道 ⇒ ★**补丁规格 P-G** (§2.3) · ★谁落 / 什么时候落 = main 排期★ |
| ★**★cont1 的核心发现 (★本单最有价值的一条★)** ★ | ★**这个闸的源码里【没有那 32 位字面量】** ⇒ ★**上一趟 H4 的检测网 (只扫 .py 字面量) 【抓不到它】⇒ 它会从清单的缝里溜过去⇒ 改板当天照样假红** ★ ⇒ ★**cont1 已把 H4 扩成两个检测类 (类A 字面量 + 类B 页面内嵌基线) ⇒ 今天它就被当场抓住** ★[实测] |

#### ★闸 H · `SW/tools/check_sw_false_connectivity_gate.py` 的板指纹三项 (★**没有通道**·★ISS-381 · ★★【ISS-408 补登记】★★★)★

| 项 | 内容 |
|---|---|
| 硬钉位置 | ★**在 .py 里** ★ —— ★**L73 `BASELINE_BOARD_MD5` 的 32 位字面量 (★类A★); 同组 L74 `BASELINE_BOARD_MTIME` / L75 `BASELINE_BOARD_SIZE` (★这两条不是 md5 ⇒ 不产生 H1 命中, 不进 §1 清单★) ★ |
| 判据原文 | ★**L443 打表 + L448 `if md5 != BASELINE_BOARD_MD5:` ⇒ L449 追加失败项** ⇒ ★**盘上板 md5 一变, 这道闸必红** ★ |
| 改板当天会不会红 | ★**必红** ★ —— ★**代码级形态检测判定它【没有合法改板通道】**: `reboard` = 0 / `prev_md5` = 0 / `check_r6_hard_protected` = 0 / `check_demo_panel_spec` = 0 (★四个 token 全 0★) ⇒ ★**改板当天它【仍红】** ★[实测] |
| 红的真含义 vs 会被误读成什么 | 真含义 = 「板被换了 (未授权)」; 会被误读成 = 「板改坏了」★ ⇒ ★**这正是 §2 存在的理由: 不点名, 那天现场没人知道该等它红** ★ |
| 该走哪条通道 | ★**缺口** ⇒ 本单把它登记成「已知缺口」 (★`status` = 已知缺口 / `gap_id` = `iss408_gap_zfc1_reboard_channel` / `spec` = ★**P-Z**★, 见 §2.3 的补丁规格表·★只出规格·本单不落★) ⇒ ★**是否改成走合法改板通道 = main 拍 (§6 Q2)** ★ |
| ★**★ISS-408 补登记的理由 (★它为什么之前没进账★)** ★ | ★**H4 的类A 检测网本来就在扫它, 但它没进 §2 的账 ⇒ H4 红 ⇒ 「下一道新闸再硬钉板 md5 就是从这儿溜过去」这条防线当时是断的** ★ ⇒ ★**本单补进 §2 账之后, H4 转绿 ⇒ 这道防线今天才真的接上** ★[实测] |

### ★2.3 · 补丁规格 (★给那 5 道闸的·★只出规格·不落★)★

★**共同形状 (★照 §0.2 那张表·不自造第二套合法改板判据★)**: ★**判据方向一个字没改** —— 仍然是「盘上必须 == 期望值」; ★合法改板只是让【期望值】从「保护基线」前移到「落表台账链头」★
★**纯 md5 硬保护支路一条都不许松** —— ★没有合法改板记录时, 期望值 = 保护基线 (盘上必须逐字节相同)★

| 规格 | 落在哪 | 改什么 (★逐条·可执行·本单不落★) | 判据方向 | 缺口 (★必须一起解决·否则补丁只解决一半★) |
|---|---|---|---|---|
| ★**P-C** ★ | `SW/tools/check_fp_truth_read.py` 的 F5 | ★把「板 md5 的期望值」从字面量改成「合法改板链头」 (★照 `check_onepass_sw_sync.py` 的形状: ★只读调用权威闸★)★ | 不变 | ★**mtime / size 两条没有跟随口径** ★ —— reboard 四项原子只带 md5, 不带 mtime/size ⇒ ★**F5 除了 md5 还比 mtime + size ⇒ 合法改板后这两条仍红** ★ ⇒ 要么给 reboard 原子补 mtime/size, 要么给 F5 一条「合法改板分支下 mtime/size 怎么判」的明文口径 ⇒ ★**判据方向要不要动 = main 拍** ★ |
| ★**P-D** ★ | `SW/tools/check_onepass_legb_sw_impact.py` 的 G8 | ★只动 `board_md5` 那一项的期望值 (★另三件 网表/脚表/BOM 一个字都不许动★)★ | 不变 | ★**页里声明的那一处 md5 怎么办** —— G8 还比「页里声明的 md5」⇒ ★那一趟的规格页也要跟着换基线 (§1.5)★ |
| ★**P-E** ★ | `HW/check_iss354_manufacturability.py` 的 A-5a/A-5b | ★md5 期望值同上; mtime 那条同上 ⇒ ★**跨域 ⇒ 由 hw-lead 落** ★ | 不变 | ★**mtime 同 P-C** ★ (★跨域登记给 hw-lead·见 §5★) |
| ★**P-F** ★ | `SW/tools/check_debug_pin_order_contract.py` 的 D7 | ★把「板指纹三项的期望值」从三个常量改成「合法改板链头」 (★照 `check_onepass_sw_sync.py` 的形状: ★只读调用权威闸★)★ | 不变 | ★**mtime / size 两条没有跟随口径** (★同 P-C★) —— ★**reboard 四项原子只带 md5, 不带 mtime/size ⇒ 合法改板后这两条仍红** ★ ⇒ ★**而且补丁会移动函数行号 ⇒ 把闸 G 的 W2 打红 (★见 §3.5 的跨闸耦合★)★** ★ |
| ★**P-G** ★ | `SW/tools/check_debug_header_fw_impact.py` 的 W7 | ★把「机器块 baseline.board_md5 的期望值」改成「合法改板链头」 (★机器块是【判决源】⇒ 判据方向一个字不许改★)★ | 不变 | ★**size 那一条补不了** (★沙盒 T4 实测: 打上补丁后 W7 仍红在 `board_size`★) ⇒ ★**要么 reboard 原子补 size, 要么给 W7 一条「合法改板分支下 size 怎么判」的明文口径 ⇒ = main 拍 (★同 U3★)** ★ |

★**沙盒原型 (★证明这个形状可行·真件那 3 个闸一个字都不许改★)**: `tmp/iss372/patch_spec.py` (★9 条补丁·每条锚点必须恰好匹配 1 次·匹配不上就 AssertionError★) + `tmp/iss372/legal_channel_sbx.py` (★通道原型·照 ISS-284 四项原子 + 落表台账链头★) ★[实测]

### ★2.4 · 沙盒读数总表 (★rc·0 = 绿★)

| 闸 | T0 基线 | T1 朴素改板 | T2 合法改板 | T2b +规格页换基线 | T4 +补丁原型 | T5 板改第二次 |
|---|---|---|---|---|---|---|
| A 权威闸 R6 | **0** | 1 | **0** | **0** | **0** | 1 |
| B SW 通道闸 (W5/W6) | **0** | 1 | 1 | **0** | **0** | 1 |
| C F5 (ISS-363) | **0** | 1 | 1 | 1 | **0** | 1 |
| D G8 (ISS-370) | **0** | 1 | 1 | 1 | **0** | 1 |
| E A-5 (ISS-354) | **0** | 1 | 1 | 1 | **0** | 1 |
| ★**F D7 (ISS-375)** ★ | **0** | 1 | 1 | 1 | **0** | 1 |
| ★**G W7 (ISS-378)** ★ | **0** | 1 | 1 | 1 | 1 | 1 |

★**三句话读法 (★本单的招牌结论★)** ★[实测]
★**① 「改板那天会假红」的有几道? ⇒ SW 域 2 道 (C / D) + 跨域 1 道 (E) = 3 道** ★
★**② 现场会不会误读成「板改坏了」? ⇒ 会** ★ —— ★**T2b 时 C/D/E 红的原文就是「板 md5 = <新值> ≠ 基线 <旧值> ⇒ 真源被改了」★ 一读就是「板坏了」★ ⇒ ★**红色原文里【没有一个字】说「这是合法改板」★★ ⇒ 现场极可能去改板凑绿 ⇒ 板 md5 变第二次 ⇒ 整趟白跑 ★
★**③ 通道存在之后, 板改第二次还红不红? ⇒ 红 (T5 全红)** ★ —— ★**A 闸的原文: 「盘上 md5 340876b6bc55 ≠ 台账链头 801782db6fb2 (真源被换了或台账没更新)」★ ⇒ ★**合法改板只让【链头前移】, 不把判据放松 ⇒ 「板改第二次」当场被抓住** ★

---

## ★3 · 「清单过期」的账 (★本单第二个正题★)

### ★3.1 · 为什么那张表是 11-17 的而闸是 11-23 的

| 项 | 读数 | 复跑命令 |
|---|---|---|
| 清单生成时刻 | ★**2026-11-17 20:49** ★ (★由 `state/_gen_board_md5_pinned_gates.py` 一次性生成★) | `stat -c '%y' state/board_md5_pinned_gates.json` |
| 清单里的闸 | ★**9 条** (★HW 6 / MECH 2 / SW 1★) · ★**9 条全部标「已有 reboard 通道」** ★ | `python3 -c "import json;d=json.load(open('state/board_md5_pinned_gates.json'));print(len(d));[print(x['file'],x['cls']) for x in d]"` |
| 清单里的 SW 闸 | ★**只有 1 条**: `SW/tools/check_onepass_sw_sync.py` ★ | 同上 |
| 今天新造的 2 道 SW 闸 | ★`SW/tools/check_fp_truth_read.py` (★ISS-363 · 2026-11-23 17:27★) + `SW/tools/check_onepass_legb_sw_impact.py` (★ISS-370 · 2026-11-23 19:50★) ★ ⇒ ★**不在那张表里** ★ | `stat -c '%y' SW/tools/check_fp_truth_read.py SW/tools/check_onepass_legb_sw_impact.py` |
| 跨域第 3 道 | ★`HW/check_iss354_manufacturability.py` (★ISS-354★) ⇒ ★**也不在那张表里** ★ | `grep -n '611b869e' HW/check_iss354_manufacturability.py` |

★**⇒ 「清单过期」的活证据 = 表是 11-17 的, 闸是 11-23 造的, 谁都没提醒谁** ★[实测]

### ★3.2 · 为什么没有任何闸在守它新鲜 (★本机 grep 实读★)

```bash
grep -rn "board_md5_pinned_gates" --include=*.py .
```
★**实读结果**: ★命中的只有一次性脚本 `state/_apply_20261117_1845_main_open296_297_298.py` + 一份决策页 ⇒ ★**`state/gate_check.py` 零命中** ★ ⇒ ★**这张清单【自生自灭】· 下一道新闸硬钉板 md5 时没人拦** ★[实测]

### ★3.3 · 那张表的【收集口径】还有第二个盲区 (★本单新发现★)

★`state/_gen_board_md5_pinned_gates.py` 的收集口径是 ★**只收 `check_*.py` / `*_check.py`·排除 `state/_*.py` 与 `state/gen_*.py`★** ⇒ ★**`state/land_v_values.py` (落表器) 的 `PROTECTED` 段 L96 硬钉着板 md5, 却收不进那张表** ★[实测]
★**⇒ 刷新那张表时, 光重跑生成器不够 ⇒ 要么把收集口径放宽 (★落表器也收★), 要么单独登记一行★** ⇒ ★**归 main 裁 (见 §5)★**

### ★3.4 · 本单新建的自守闸怎么补这个洞 (★指向交付物②★)
### ★3.5 · ★★cont1 的活证据: 这张清单【签收后 4 小时就过期了】, 而且是被本单自己的闸抓到的★★

★**这一节是 cont1 (2026-11-24 04:xx) 新写的 ⇒ ★它是本单最硬的一条证据★** ★[实测]

| 项 | 读数 | 复跑命令 |
|---|---|---|
| ★**签收时刻** ★ | ★**2026-11-23 22:4x · main 独立复核签收 ISS-372 (verified)★** | `grep -A3 'id: ISS-372' state/issue_log.yaml` |
| ★**签收后 SW 域新落的文件** ★ | ★**`SW/tools/check_debug_pin_order_contract.py` (ISS-375 · 02:05) + `SW/BOARD_ONEPASS_DEBUG_PIN_ORDER_CONTRACT.md` (02:07) + `SW/tools/check_debug_header_fw_impact.py` (ISS-378 · 02:45) + `SW/BOARD_ONEPASS_DEBUG_HEADER_FW_IMPACT.md` (02:45)** ★ | `ls -la --time-style=full-iso SW/tools/check_debug_*.py` |
| ★**它们做了什么** ★ | ★**两道闸都硬钉板 md5, 且都没有合法改板通道** ⇒ ★**改板当天必假红** (§2.2 的闸 F / 闸 G) ★ | ★`grep -n '611b869e' SW/tools/check_debug_pin_order_contract.py`★ + ★`grep -n 'board_md5' SW/BOARD_ONEPASS_DEBUG_HEADER_FW_IMPACT.md`★ |
| ★**本单自守闸的反应 (★本单机制的活证据★)** ★ | ★**闸当场变红: H1 红 (5 处漏登记) + H4 红 (新闸不在册)** ⇒ ★**「下一道新闸再硬钉板 md5 时当场被抓住」这件事, 在签收后 4 小时就【真的发生了一次】** ★ | ★`python3 SW/tools/check_sw_board_md5_rebase_readiness.py` (cont1 开工时 rc=1·H1/H4 红) ★ |
| ★**清单过期对 SW 域的【真实代价】** ★ | ★**上一趟交卷时: 17 个活文件 / 47 行 / 57 处 ⇒ cont1 实扫: 20 个活文件 / 53 行 / 63 处** ⇒ ★**「钉板 md5 的闸清单」和「引用面清单」都会过期, 而且过期得比人记得住的快** ★ | ★`python3 tmp/iss372/gen_manifest.py`★ |

★**★⇒ 所以本单在 cont1 里做的两件事, 不是「补文档」, 是「把机制从【能抓】变成【抓得住新的抓法】」★★** ★
★**① H4 从 1 个检测类扩成 2 个**: 类A (★.py 内 32 位字面量★) + 类B (★闸自己算盘上板 md5 且期望值来自页面/台账内嵌基线·且该比较喂给判决清单★) ⇒ ★**闸 G 正是类B ⇒ 它当场被抓住** ★
★**② 清单页 §1.10 的机器清单重新生成** ⇒ ★**53 行 / 63 处 逐处归类 (含 6 处新增·5 处来自 ISS-375/ISS-378·1 处来自同页追加段)★** ⇒ ★**闸恢复绿 (rc=0)★**

#### ★3.5.1 · ★★一个必须让 main 知道的【跨闸耦合】(★沙盒 T4 实测出来的·★不在原任务书里★)★★

★**现象**: ★**给闸 F (ISS-375) 打补丁 P-F ⇒ 闸 G (ISS-378) 当场变红** ★[实测]
★**机理**: ★**闸 G 的 W2 判据是「`SW/tools/check_debug_pin_order_contract.py` 的第 287 行或之前有没有定义 `d1_current_board`」—— ★它把【另一个闸的【行号】】钉进了自己的机器块★ ⇒ ★**P-F 在 `BOARD_SIZE` 那行后面插了 7 行 ⇒ `d1_current_board` 从 287 行挪到 293 行 ⇒ W2 立刻红** ★
★**实测读数 (★沙盒 T4★)**: ★**闸 G 的红原文 = `✘ W2 : JTAG_TCK: 函数 d1_current_board 在 … 第 287 行或之前没有定义` (★5 行全部命中★)** ★[实测] (★`logs/iss372/08_sbx_reboard_rehearsal_7gates.txt`★)
★**⇒ 代价**: ★**P-C/P-D/P-F/P-G/P-E 这一批补丁【必须同批落】—— 否则先落哪一个都会把另一个闸打红, 现场又是一轮「误读成板坏了」** ★ ⇒ ★**已登记成 needs_from 的 U8 (见 §6) ⇒ 归 main 排期** ★



| 洞 | 补法 | 本单闸的哪一条 |
|---|---|---|
| ★**没人知道哪道闸钉了板 md5** ★ | ★**H4**: 自己扫 `SW/tools/*.py` 里【含 32 位字面量】的闸 ⇒ ★**今天新造的那两道今天就能被抓住** ★ | H4 |
| ★**知道了也没人给它建通道** ★ | ★**H5**: 每道闸要么【代码级已有合法改板通道】(★形态检测: `reboard` + `prev_md5` + 权威闸调用★), 要么【在 §2 登记成已知缺口 + 缺口归属 + 谁来补 + 补法规格】 ⇒ ★**「登记过的缺口」不红, 「没人知道的缺口」才红** ★ | H5 |
| ★**清单自己会过期** ★ | ★**H1**: 清单必须逐处覆盖盘面扫描结果 (★漏一行就红★) + ★**清单里登记了但盘上扫不到的 ⇒ 清单过期 ⇒ 也红** ★ | H1 |
| ★**有人想把某个文件从扫描面里摘掉** ★ | ★**H1 的声明式排除清单必须恰好是【本单新建的页 + 本闸自己】两个** ⇒ 扩一个就红 ★ | H1 |
| ★**活判据被伪装成历史留证** ★ | ★**H3**: 【历史留证】类不许落在 `.py` 上 ★ | H3 |

★**⇒ 合起来 = 「板只改一次」那道铁律在 SW 侧从此不再靠人记得** ★

---

## ★4 · `.kicad_sch` 能不能当锚 (★答那条挂了两周的 need★)

★**need**: `iss249_kicad_sch_md5_not_anchor_sw` (★`state/fragments/hw.yaml` 的 `needs_from` · `to: sw-lead` · `since: 2026-11-16·至今未闭合★)
★**need 原文的机理**: 「`state/check_sch_pinfull.py` 与 `state/check_sch_erc.py` 内部会 subprocess 调 `state/gen_kicad_sch.py` ⇒ 跑这两条门禁就会重铸随机 UUID ⇒ 任何门禁跑完 md5 都变」

### ★4.1 · 【结论不变·但机理要订正】

★**结论**: ★**`.kicad_sch` 的 md5 真的不能当锚点** ★ —— ★但★ **真正的随机源是 `state/gen_kicad_sch.py` 本身**, 不是 `check_sch_erc.py` / `check_sch_pinfull.py` ★[实测]

★**机理 (★沙盒实跑·`logs/iss372/03_exp1_sch_md5.txt`★)** ★[实测]
★**① `state/gen_kicad_sch.py` 就是随机源**: ★它 L119 `return str(uuid.uuid4())` + L345/358/378/398/426/448 处处 `uid()` ⇒ ★**它直接跑一次 ⇒ 11 个 `.kicad_sch` 的 raw md5 全部变 (11/11)★**
★**② 但图是同一张**: ★**归一化 (UUID + 时间戳) 之后 11/11 都不变 (0/11 变化)★ ⇒ ★ISS-249 实测「11/11 SAME」就是这件事★**
★**③ 而 `check_sch_erc.py` / `check_sch_pinfull.py`【不改它】**: ★沙盒里各跑一次 (rc=0) ⇒ ★**md5 变化的文件数 = 无** ⇒ ★**need 原文的「这两道门禁会 subprocess 调 gen_kicad_sch」这个机理不成立** ★ (★`check_sch_pinfull.py` 虽 `import gen_kicad_sch`, 但只用它的 `kicad_ref()` 纯函数, 并不重生成原理图; 它调的是 `kicad.sh sch export netlist`★)

### ★4.2 · 那这条 need 到底该怎么处置

| 问 | 答 | 证据等级 |
|---|---|---|
| ★`.kicad_sch` 的 md5 能当锚点吗? ★ | ★**不能** ★ —— ★只要有人跑一次 `state/gen_kicad_sch.py`, 11 个文件的 raw md5 就全变 ⇒ ★**它只能当【归一化 UUID + 时间戳后是否同图】的判据** ★ | [实测] |
| ★那两条门禁跑完 md5 会变吗? ★ | ★**不会** (★沙盒实跑: 变化文件数 = 无★) | [实测] |
| ★这个风险落到过谁头上吗? ★ | ★**没有** ★ —— ★SW 域活文件里 `.kicad_sch` 的 md5 命中 = **0 处** ⇒ ★**SW 侧从来没拿 `.kicad_sch` 的 md5 当过锚** ★ | [实测] |
| ★⇒ 这条 need 的正确处置? ★ | ★**结论订正 + 降级为「一条已知的注意事项」** —— ★不是「有个活的隐患」★ ⇒ ★**本单用同 key 在 `state/fragments/sw.yaml` 的 `answers` 里答掉 (★答方 = sw-lead·问方 = hw-lead★)★ | [实测] |

★**★注意 (★不改判据·只订正机理★)**: ★**结论一个字没变** —— 「不能当锚点」仍然成立; ★变的是 ★**为什么** ★(★真正的随机源是 `gen_kicad_sch.py` 本身·不是那两道门禁★) ⇒ ★**下一个 agent 不必再重查一遍「那两道门禁到底会不会改它」** ★

---

## ★5 · 跨域登记 (★只登记·不越界改★)

| # | 对象 | 归属域 | 本单的发现 | 本单做了什么 | 要 main 裁什么 |
|---|---|---|---|---|---|
| ★1 ★ | `HW/check_iss354_manufacturability.py` L40/L41 (★闸 E·跨域第 3 道没通道的闸★) | ★**hw-lead** ★ | 硬钉板 md5 + mtime ⇒ 改板当天必红 (★沙盒 T2b 实测 rc=1★) | ★**只给补丁规格 P-E (§2.3)** · ★**一个字都不许改那个文件** ★ | ★**谁落 P-E·什么时候落** (★建议: 与 P-C/P-D 同批落, 免得改板那天只补一半★) ★ |
| ★2 ★ | `state/land_v_values.py` L96 (★落表器·`PROTECTED` 段★) | ★**main** ★ | 落表器自己也硬钉着板 md5 ⇒ 改板那一趟它必须跟着改, 否则落表器自证红 | ★**只登记** ★ | ★**改板那一趟由谁改这一行** (★建议: 与落表台账链前移同一步·原子★) ★ |
| ★3 ★ | `state/board_md5_pinned_gates.json` + `.md` | ★**main** ★ | ★**清单过期** (★11-17 的表 · 11-23 的闸★) + ★**收集口径盲区** (§3.3) ★ | ★**只给「刷新后应有的内容」, 不许自己写那两个文件** ★ | ★**什么时候刷新 + 收集口径要不要放宽** (★见下面那张「刷新后应有的内容」★) ★ |

### ★5.1 · 「刷新后应有的内容」 (★给 main 的·★本单不落★)
★**★cont1 增补 (2026-11-24 04:xx) ⇒ 刷新后那张表应当是【现有 9 条 + 新增 5 条 + 口径补 1 条】★★** ★[实测]

| 应新增条目 | 文件 | 硬钉位置 | 应标的状态 | 依据 |
|---|---|---|---|---|
| ★**新增 4** ★ | `SW/tools/check_debug_pin_order_contract.py` | ★L53★ | ★**已知缺口 (无 reboard 通道)**★ ⇒ 缺口编号 `iss372_gap_iss375_d7_reboard_channel` · 谁来补 = sw-lead (时点由 main 排期) · 补法规格 = **P-F** | ISS-375 · 2026-11-24 02:05 交付 · 沙盒 T2b 实测 rc=1 |
| ★**新增 5** ★ | `SW/tools/check_debug_header_fw_impact.py` | ★★L397 在 `SW/BOARD_ONEPASS_DEBUG_HEADER_FW_IMPACT.md` 的机器块里 (★★不是 .py★)★★ | ★**已知缺口 (无 reboard 通道)**★ ⇒ 缺口编号 `iss372_gap_iss378_w7_reboard_channel` · 谁来补 = sw-lead (时点由 main 排期) · 补法规格 = **P-G** | ISS-378 · 2026-11-24 02:45 交付 · 沙盒 T2b 实测 rc=1 |
| ★**★口径补 2 (★cont1 新增·★比口径补 1 更要紧★)** ★ | ★**那张表的【收集口径】现在只收 `.py` 里含 32 位字面量的闸 ⇒ 闸 G 这种「页面内嵌基线类」压根收不进去** ★ | ★—★ | ★**要么把收集口径放宽到「闸自己算盘上板 md5 且期望值来自文档」, 要么在表页里明写「页面内嵌基线类闸由 SW 侧自守闸 (H4 类B) 收」** ★ | ★§3.5 的活证据 + 本单 H4 的类B 判据★ |


★**刷新后那张表应当包含 (★现有 9 条 + 新增 3 条 + 口径补 1 条★)** ★[实测]

| 应新增条目 | 文件 | 硬钉位置 | 应标的状态 | 依据 |
|---|---|---|---|---|
| ★新增 1 ★ | `SW/tools/check_fp_truth_read.py` | ★L87★ | ★**已知缺口 (无 reboard 通道)**★ ⇒ 缺口编号 `iss372_gap_f5_reboard_channel` · 谁来补 = sw-lead (时点由 main 排期) · 补法规格 = §2.3 的 **P-C** | ISS-363 · 2026-11-23 17:27 交付 · 沙盒 T2b 实测红 |
| ★新增 2 ★ | `SW/tools/check_onepass_legb_sw_impact.py` | ★L70★ | ★**已知缺口 (无 reboard 通道)**★ ⇒ 缺口编号 `iss372_gap_g8_reboard_channel` · 谁来补 = sw-lead (时点由 main 排期) · 补法规格 = **P-D** | ISS-370 · 2026-11-23 19:50 交付 · 沙盒 T2b 实测红 |
| ★新增 3 ★ | `HW/check_iss354_manufacturability.py` | ★L40★ | ★**已知缺口 (无 reboard 通道)**★ ⇒ 缺口编号 `iss372_gap_iss354_reboard_channel` · 谁来补 = hw-lead · 补法规格 = **P-E** | ISS-354 · 沙盒 T2b 实测红 |
| ★口径补 1 ★ | `state/land_v_values.py` | ★L96★ | ★**收集口径盲区** ⇒ 要么把 `state/land_v_values.py` 收进表, 要么在表页里明写「落表器自钉基线 · 由落表那一趟自己跟」 ★ | §3.3 · 本单实读 |

★**★刷新那张表时, 那 9 条「已有 reboard 通道」的判定不许顺手动★ —— ★通道形状照权威闸 R6 (`check_r6_hard_protected()`)★ · fail-closed 三条一条不许放宽★ ★**

---

## ★6 · 未决项 (★只登记·不代拍·每条给代价★)

| # | 未决项 | 归谁 | 本单的依据 | ★**代价 (不拍的代价)** ★ | 本单的建议 |
|---|---|---|---|---|---|
| ★U1 ★ | ★改板那一趟的「S9 换基线」到底一次改齐哪些 ★ | ★main→老板 ★ | §1.3 / §1.5 · 沙盒 T2b | ★不一次改齐 ⇒ ★**已有通道的闸 B 也会红** (★沙盒 T2 实测 rc=1★) ⇒ 现场又要多一次「误读成板坏了」的窗口 | ★**S9 一次改齐 = ① 落表台账链前移 ② 台账锚点 reboard 四项 ③ 【规格页引用】那 17 处 ④ issue_log 留痕** ★⇒ ★**顺序必须是「先落表 → 再换基线 → 最后跑闸」** ★ |
| ★U2 ★ | ★那 3 道闸的通道补丁 (P-C / P-D / P-E) 谁来落、什么时候落 ★ | ★main 排期 (★P-E 还要过 hw-lead★) ★ | §2.3 · 沙盒 T4 | ★**不落 ⇒ 改板当天 3 道闸必红** ⇒ 现场误读 ⇒ 板 md5 变第二次 ⇒ ★**整趟白跑 (这正是本单要防的那件事)★** | ★**建议: 与「板只改一次」那一趟【同批】落, 且【必须早于】改板当天** ★ |
| ★U3 ★ | ★reboard 四项原子 (by/file/prev_md5/md5) 够不够 ★ | ★main★ | §2.3 的 P-C/P-E 缺口列 | ★**不够** ⇒ ★F5 的 mtime + size 两条在合法改板后仍红 (★reboard 原子不带 mtime/size★) ⇒ ★**P-C 只解决一半 ⇒ 改板当天照样红** ★ | ★**要么给 reboard 原子补 mtime/size (★要动权威判据 ⇒ 老板拍★), 要么给 F5/E 的 mtime 判据一条明文口径 (★判据方向放宽 ⇒ 也要拍★)** ★⇒ ★**本单只登记, 不代拍** ★ |
| ★U4 ★ | ★历史留证那一类「永远不许改」这条禁令要不要写成机器判据 ★ | ★main ★ | §1.6 · H3 (★反向判据: 活判据不许伪装成历史留证★) | ★**不机器化** ⇒ ★下一个 agent 仍要靠人眼判断某一处是「现状值」还是「历史读数」 ⇒ ★**§1.9 那种「按文件归并」的错还会再犯** ★ | ★**本单已经把「反向判据」做进 H3 了 (活判据不许塞进历史留证)★ ⇒ ★**再加一条「历史留证不许出现在 .md 的现状表里」会误伤 ⇒ 不建议** ⇒ ★**建议维持现状 + 把本页 §1 当作唯一口径源** ★ |
| ★U5 ★ | ★「板改第二次」的兜底预案 ★ | ★main→老板 ★ | §2.4 的 T5 (★通道存在后仍当场红★) | ★**没有预案** ⇒ 现场第二次改板 ⇒ ★**闸红着, 但没人知道那是「第二次」而不是「第一次」** ★ | ★**本单已证明「当场红」这件事本身是可靠的** ⇒ ★**兜底预案是流程问题 (谁当场判定「这是第二次」并停手)· 不是判据问题** ★ |
| ★U6 ★ | ★`state/board_md5_pinned_gates.json` 的刷新时机与收集口径 ★ | ★main ★ | §3.1 / §3.3 | ★**不刷新** ⇒ ★**那张表继续漏新闸** ⇒ ★**下一个新闸再硬钉板 md5 时还是没人拦** ★ | ★**建议: 本单的自守闸落地后, 刷新一次 (★含 §5.1 那 3 条新增 + 1 条口径补★) ★⇒ ★**但那张表是 main 的域, 本单零写入** ★ |
| ★U8 ★ | ★**【跨闸耦合】: P-C/P-D/P-E/P-F/P-G 这批通道补丁【必须同批落】** ★ | ★main 排期 ★ | ★§3.5.1 · 沙盒 T4 实测 ★ | ★**不同时落** ⇒ ★**先落的那个补丁会移动【另一个闸】的行号 ⇒ 把那个闸当场打红** (★实测: P-F 一落 ⇒ 闸 G 的 W2 红·5 行全中★) ⇒ 现场又是一轮「误读成板坏了」 ⇒ ★**整趟白跑** ★ | ★**建议: 5 条补丁 (P-C/P-D/P-E/P-F/P-G) 合成【一批】落, 且批内顺序与闸的依赖顺序一致; 落完立刻在沙盒重跑一次 §2.4 的 T0~T5 读数表做交叉验证** ★⇒ ★**本单只登记, 不代拍** ★ |
| ★U9 ★ | ★**闸 G 的 W7 那条 `board_size` 判据在合法改板后怎么办** ★ | ★main (⇒ 可能要老板) ★ | ★§2.2 闸 G 的 T4 实测 (★打上 P-G 后 W7 仍红在 size★) ★ | ★**不处理** ⇒ ★**P-G 只解决一半 ⇒ 改板当天闸 G 照样红** ⇒ ★**现场又要多一次「误读成板坏了」的窗口** ★ | ★**要么给 reboard 原子补 size (★要动权威判据 ⇒ 老板拍★), 要么给 W7 一条明文口径** ★⇒ ★**与 U3 同款口径, 建议一并拍** ★ |

---

## ★7 · 证据分级表 (★逐条标档·不许出现无档措辞★)

| # | 结论 | 证据等级 | 复跑命令 / 留证路径 |
|---|---|---|---|
| E1 | 板 md5 / mtime / size = `611b869e13518c3c023fb178f91a0075` / `2026-11-06 07:07:17.362193413` / `4940213` | ★[实测] ★ | `md5sum HW/PCB/demo_mainboard.kicad_pcb && stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb` · `logs/iss372/07_board_double_evidence.txt` |
| E2 | SW 域板 md5 引用面 = ★**17 个活文件 / 47 命中行 / 57 命中处** ★ | ★[实测] ★ | `python3 SW/tools/check_sw_board_md5_rebase_readiness.py` (H1 自扫) |
| E3 | 三类分布 = 判据锚 9 / 规格页引用 17 / 历史留证 21 | ★[实测] ★ | 同上 + `tmp/iss372/gen_manifest.py` |
| E4 | ★上一趟那套 `grep -v '\\.bak'` 的逐行清单少 1 行 (台账 L173·正文里含 `.bak_iss220` ⇒ 被连带过滤) ★ | ★[实测] ★ | `grep -rn 611b869e SW/ \| grep -v '\.bak\|__pycache__' \| wc -l` (46) vs `grep -rn 611b869e SW/SW_MD5_BASELINE_LEDGER.md \| wc -l` (13) |
| E5 | ★闸 C / D / E 在合法改板当天【仍红】 (沙盒 T2b) ★ | ★[实测] ★ | `logs/iss372/05_sbx_reboard_rehearsal.txt` |
| E6 | ★打了补丁规格原型后 3 道闸回绿 (沙盒 T4) ★ | ★[实测] ★ | 同上 + `tmp/iss372/patch_spec.py` |
| E7 | ★通道存在后「板改第二次」当场红 (沙盒 T5) ⇒ 纯 md5 硬保护支路没被放松 ★ | ★[实测] ★ | 同上 |
| E8 | ★已有通道的闸 B 在 T2 仍红 ⇒ 红在【规格页 current_state 过期】⇒ S9 必须连规格页一起换基线 ★ | ★[实测] ★ | 同上 (T2 vs T2b 对比) |
| E9 | ★`state/board_md5_pinned_gates.json` = 11-17 生成的 9 条; 今天新造的 2 道 SW 闸 + 跨域 1 道不在表里 ★ | ★[实测] ★ | `python3 -c "import json;print(len(json.load(open('state/board_md5_pinned_gates.json'))))"` |
| E10 | ★没有任何闸在守那张清单的新鲜 (`state/gate_check.py` 零命中) ★ | ★[实测] ★ | `grep -rn "board_md5_pinned_gates" --include=*.py .` |
| E11 | ★`state/land_v_values.py` L96 也硬钉板 md5, 但那张表的收集口径只收 `check_*.py` ⇒ 收不进去 ★ | ★[实测] ★ | `grep -n '611b869e' state/land_v_values.py` + `grep -n 'check_\*' state/_gen_board_md5_pinned_gates.py` |
| E12 | ★`.kicad_sch` 跑一次 `state/gen_kicad_sch.py` ⇒ raw md5 11/11 变; 归一化后 0/11 变 ⇒ 同图 ★ | ★[实测] ★ | `logs/iss372/03_exp1_sch_md5.txt` |
| E13 | ★`check_sch_erc.py` / `check_sch_pinfull.py` 跑完 `.kicad_sch` 的 md5 逐字节不变 ⇒ need 原文的机理不成立 ★ | ★[实测] ★ | 同上 (沙盒 S0/①/②) |
| E14 | ★SW 域活文件里 `.kicad_sch` 的 md5 命中 = 0 处 ⇒ 该风险至今没伤到任何人 ★ | ★[实测] ★ | `grep -rn 'e433793b4a3ec321cc69f466d7e15de7' SW/` (空) |
| E15 | ★`state/check_demo_panel_spec.py` 的 `check_r6_hard_protected()` 是合法改板判据的唯一真源 ★ | ★[实测] ★ | `grep -n 'def check_r6_hard_protected' SW/tools/check_demo_panel_spec.py` (L748) |
| E16 | ★机器闸 H1~H7 + 8 条反向用例每条自证「红的集合 == {目标那一条}」 ★ | ★[实测] ★ | `python3 SW/tools/check_sw_board_md5_rebase_readiness.py --selftest` |
| E17 | ★S9「一次改齐」的具体清单 = 17 处规格页引用 + 落表台账链前移 + 台账锚点 reboard 四项 + issue_log 留痕 ★ | ★[推算] ★ (★依据 E8 的实测 + §1.3 的分类·具体到哪一步先跑 = U1 待 main 拍★) | `logs/iss372/05_sbx_reboard_rehearsal.txt` (T2b) |
| E18 | ★P-C / P-D / P-E 的 mtime/size 缺口 ★ | ★[实测] ★ (★「reboard 原子不带 mtime/size」是读代码 + 沙盒 T4 原型实测★) | `tmp/iss372/patch_spec.py` + `logs/iss372/05_sbx_reboard_rehearsal.txt` |
| E19 | ★历史留证 21 行的清单 ★ | ★[实测] ★ (★逐行人工判定 + §1.10 的机器清单双形态★) | 本页 §1.3 |
| E20 | ★`.kicad_sch` 的 md5 能不能当锚点 = 不能; 以及 need 的正确处置 = 结论订正 + 降级 ★ | ★[实测] ★ (★结论★) + ★[推算] ★ (★处置方式★) | 本页 §4 + `state/fragments/sw.yaml` 的 `answers` |
| E21 | ★**签收后 4 小时内 SW 域新落 2 道硬钉板 md5 且无通道的闸 (ISS-375 的 D7 / ISS-378 的 W7) ⇒ 本单自守闸当场变红 (H1 + H4)** ★ | ★[实测] ★ | ★`python3 SW/tools/check_sw_board_md5_rebase_readiness.py` (cont1 开工时 rc=1) + `logs/iss372/08_sbx_reboard_rehearsal_7gates.txt` ★ |
| E22 | ★**SW 域板 md5 引用面 (cont1 复扫) = 20 个活文件 / 53 命中行 / 63 命中处; 三类 = 判据锚 11 / 规格页引用 17 / 历史留证 25** ★ | ★[实测] ★ | ★`python3 tmp/iss372/gen_manifest.py` + `python3 SW/tools/check_sw_board_md5_rebase_readiness.py` (H1 自扫)★ |
| E23 | ★**闸 G (ISS-378) 属【页面内嵌基线类】: 它的 .py 里没有 32 位字面量 ⇒ 上一趟 H4 的单类检测网抓不到它 ⇒ cont1 把 H4 扩成两类** ★ | ★[实测] ★ | ★`grep -c 611b869e SW/tools/check_debug_header_fw_impact.py` (=0) + `grep -n 'board_md5' SW/BOARD_ONEPASS_DEBUG_HEADER_FW_IMPACT.md` (L397) ★ |
| E24 | ★**闸 F 在 T0~T5 的读数 = 绿/红/红/红/绿/红 ⇒ 与 F5/G8/A-5 同款「没有通道」画像** ★ | ★[实测] ★ | ★`logs/iss372/08_sbx_reboard_rehearsal_7gates.txt` (T0~T5 读数汇总表) ★ |
| E25 | ★**闸 G 在 T0~T5 的读数 = 绿/红/红/红/红/红; 且 T2b 的红原文只剩 size + mtime (md5 那条已绿) ⇒ 「S9 换基线」对这一页必须【md5 + size + mtime 三项一起换】** ★ | ★[实测] ★ | ★同上 (T2b 段 G 的原文) ★ |
| E26 | ★**跨闸耦合: 给闸 F 打 P-F ⇒ 闸 G 的 W2 当场红 (W2 把闸 F 的函数行号钉进了自己的机器块)** ★ | ★[实测] ★ | ★同上 (T4 段 G 的原文) + §3.5.1 ★ |
| E27 | ★**H4 两类检测 + 10 条反向用例 (含 2 条类B: 未在册⇒红 / 信号消失⇒全绿) 全过** ★ | ★[实测] ★ | ★`python3 SW/tools/check_sw_board_md5_rebase_readiness.py --selftest` (10/10 · ALL TESTS PASS) ★ |

---

## ★8 · 机器闸与复跑命令

### ★8.1 · 本单新建的闸 (★零挂链★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=$PWD/tmp
python3 SW/tools/check_sw_board_md5_rebase_readiness.py            # rc=0 · H1~H7 全绿
python3 SW/tools/check_sw_board_md5_rebase_readiness.py --selftest  # rc=0 · 10/10 (每条自证「只红目标那一条」·★含 2 条类B 反向用例★)
```

★**★本闸【零挂链】: `state/gate_check.py` 一个字都不许动 ⇒ 本闸不进 `EXTRA_GATES`★** ★⇒ ★**要不要挂 = main 的决定 (见 §6 U2 的同款口径)** ★

### ★8.2 · 本页的机器清单怎么再生成 (★不许手改 §1.10 那块 JSON★)

```bash
python3 tmp/iss372/gen_manifest.py            # → tmp/iss372/manifest.json + tmp/iss372/sec1_table.md
```

★**分类表覆盖不到扫描命中的任何一行 ⇒ 脚本直接 rc=2 退出 (fail-closed) ⇒ 不许出现「漏登记」★**

### ★8.3 · 既有闸复跑 (★本单交卷时必须仍全绿★)

```bash
python3 SW/tools/check_demo_panel_spec.py        # rc=0
python3 SW/tools/check_onepass_sw_sync.py         # rc=0
python3 SW/tools/check_fp_truth_read.py           # rc=0
python3 SW/tools/check_onepass_legb_sw_impact.py  # rc=0
python3 HW/check_iss354_manufacturability.py     # rc=0
```

### ★8.4 · 沙盒复跑 (★零写板★)

```bash
python3 tmp/iss372/exp2_reboard.py               # → logs/iss372/05_sbx_reboard_rehearsal.txt
```

---

> ★**本单零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 · 零改 state/ 下的清单 · 零挂链 · 零外发 · 不代老板拍板 · 不自签 issue_log** ★
> ★**本单自守: `SW/tools/check_sw_board_md5_rebase_readiness.py` (H1~H7 + 8 条反向用例)★**

---

## ★★9 · ★★【追加式订正块 · ISS-408 · 2026-11-25 · sw-lead】★★ ★★计数口径以本块为准 (§1 / §1.4 / §2.2 的标题与老表格是老字 ⇒ 本单一个字未删 ⇒ 新口径只写在本块里)★★ ★

### ★9.1 · 本块做了什么 (★5 处追加 · 零删除 · 零改写★)

| # | 追加位置 | 追加了什么 | 形状 |
|---|---|---|---|
| 1 | §1.10 机器块 `refs` 数组**末尾** | ★**4 条** (H1 那 4 处漏登记的板 md5 引用面) ★ | 追加式 |
| 2 | §1.10 机器块 `gates` 数组**末尾** | ★**1 条** (`check_sw_false_connectivity_gate.py` · `id` = ★**ZFC-1**★) ★ | 追加式 |
| 3 | §1.3 逐处清单表**末尾** | ★**第 54~57 行** (与机器块 `refs` 顺序一一对应) ★ | 追加式 |
| 4 | §2.2 逐闸账 | ★**闸 H** (`check_sw_false_connectivity_gate.py` 的板指纹三项) ★ | 追加式 |
| 5 | 文末 (本块) | ★**计数订正 + 补丁规格 P-Z + 收口前后 rc 对比** ★ | 追加式 |

### ★9.2 · 计数订正 (★新口径 ★)

| 口径 | 改前 (老字) | ★**改后 (本块为准)** ★ | 差 |
|---|---|---|---|
| §1 引用行数 | 53 | ★**57** ★ | +4 |
| 命中处数 | 63 | ★**67** ★ | +4 |
| 判据锚 (含 .py) | 11 (含 .py 8) | ★**12 (含 .py 9)** ★ | +1 (第 57 行) |
| 规格页引用 | 17 | ★**18** ★ | +1 (第 54 行) |
| 历史留证 | 25 | ★**27** ★ | +2 (第 55 / 56 行) |
| 处置「随板改」 | 17 | ★**17** ★ | ★**0** ★ |
| 处置「不许改」 | 31 | ★**33** ★ | +2 |
| 处置「交 main 拍」 | 5 | ★**7** ★ | +2 (第 54 / 57 行) |
| §2 逐闸账 | 7 道 (闸 A~G) | ★**8 道 (闸 A~H)** ★ | +1 |
| 机器块 `gates` | 6 条 | ★**7 条** ★ | +1 |

★**读法**: ★**「随板改」一条都没多 ⇒ 本单【没有】替板那一趟决定任何一处该怎么改** ⇒ ★**多出来的 2 条「交 main 拍」= 本单摆在 main 面前的 2 个方向性问题** ★[实测]

### ★9.3 · 补丁规格 P-Z (★给闸 H 的 · ★只出规格 · 本单不落★) ★

| 规格 | 落在哪 | 改什么 (★逐条·可执行·本单不落★) | 判据方向 | 缺口 (★必须一起解决★) |
|---|---|---|---|---|
| ★**P-Z** ★ | `SW/tools/check_sw_false_connectivity_gate.py` 的 L73/L74/L75 (★BASELINE_BOARD_MD5 / BASELINE_BOARD_MTIME / BASELINE_BOARD_SIZE★) | ★把「板指纹三项的期望值」从三个写死常量改成「合法改板链头」 (★照 `SW/tools/check_onepass_sw_sync.py` 的形状: ★只读调用权威闸 `check_demo_panel_spec.py` 的 `check_r6_hard_protected()`★) ★ | ★**不变** (★仍是「盘上必须 == 期望值」★) | ★**mtime / size 两条没有跟随口径** (★同 P-C★) ⇒ reboard 四项原子只带 md5, 不带 mtime/size ⇒ ★**合法改板后这两条仍红** ⇒ 要么给 reboard 原子补 mtime/size, 要么给这道闸一条「合法改板分支下 mtime/size 怎么判」的明文口径 ⇒ ★**判据方向要不要动 = main 拍 (§6 Q2)** ★ |

★**沙盒原型 (★证明这个形状可行·真件那 3 个闸一个字都不许改★)**: `tmp/iss372/patch_spec.py` (★9 条补丁·每条锚点必须恰好匹配 1 次·匹配不上就 AssertionError★) + `tmp/iss372/legal_channel_sbx.py` (★通道原型·照 ISS-284 四项原子 + 落表台账链头★) ★[实测]

### ★9.4 · 收口前后 rc 对比 (★本单的核心凭证 ★)

| 时刻 | 读数 | 留证 |
|---|---|---|
| ★**收口前** ★ | ★**rc=1 · 5/7 通过 (H1 红 + H4 红)** ★ | `logs/iss408/gate_before.txt` (上一趟留证) |
| ★**收口后** ★ | ★**rc=0 · 7/7 通过** ★ | `logs/iss408/gate_after.txt` |
| ★**反向用例** ★ | ★**3 条全部「红的集合 == {目标那一条}」** ★ | `logs/iss408/reverse_cases.txt` |
| ★**闸健康度 H0** ★ | ★**「点【本闸】坏」那条红消失** ★ (★因为这条闸的 `--selftest` 从 9/10 变成 10/10 ⇒ 末行从「★有用例 FAIL ⇒ 本闸不可信 ⇒ rc=1★」变成「ALL TESTS PASS」⇒ H0 对本闸的三条报错里的两条一并消失★) ★★**★精确口径: H0 整体仍红, 但点的是【另一道闸】`check_sw_ref_reachability_v2.py` (它的 ROSTER 成功标志声明过期 ⇒ 那是改另一道闸的判据 ⇒ 本单不碰 ⇒ 已登记 needs_from 交 main)★**★ ★ | `logs/iss408/gate_health_after.txt` |

### ★9.5 · 「老字一字未删」的自证 (★三条一起给 ★)

| 证 | 断言 |
|---|---|
| 证 A | ★**共同前缀逐字相同**: 改前全文到第一个插入点之前的那一段, 与改后全文的同一段**逐字节相同** ⇒ md5 相同 ★ |
| 证 B | ★**零删除 + 零改写**: 序列比对逐段对齐改前/改后 ⇒ ★**所有差异段都是【插入】, 没有一段是【删除】或【替换】** ★ |
| 证 C | ★**可逆还原**: 把改后全文里的 5 段插入块原样摘掉 ⇒ ★**md5 与改前全文的 md5 逐字相同** (`0ba9dfce5046e131465b4fbd3675614f`) ★ |

★**复跑**: `python3 tmp/iss408/append_only_proof.py` (★输出落 `logs/iss408/append_only_proof.txt`★) ★

### ★9.6 · 本块带来的未决项 (★不代拍 ★)

| 编号 | 问句 | 代价 |
|---|---|---|
| Q1 | ★第 54 / 55 / 56 / 57 行的三类归属方向 ⇒ 归【历史留证】还是归【活判据 / 规格页引用】? ★ | ★归属不同 ⇒ 板 md5 变了以后要不要跟着改, 结论相反 ★ ⇒ ★**第 54 行是悬的 ⇒ 板那一趟现场要么把历史留证改成新数 (造假), 要么漏改当前值 (页面说谎)** ★ |
| Q2 | ★闸 H 是停在「补进 §2 账」(★本单已落★), 还是改成走合法改板通道 (★P-Z★)? ★ | ★后者要动一道已签收闸 ⇒ 需重签 ⇒ 工期 + 重签成本 ★ |
| Q3 | ★这道守门闸要不要挂进 `state/gate_check.py`? ★ | ★它今天红 ⇒ 挂上去当天链会红; ★修好之后挂不挂 = 另一个决定 ★ |
| Q4 | ★「板 md5 变了之后 SW 侧要动哪几处」的总清单要不要成为板那一趟的必过项? ★ | ★不设 ⇒ 板那一趟的收工判据失真 ⇒ 白跑一次 Gerber/投产包重出 ★ |
| Q5 | ★要不要再补一道独立新闸 (守「漏登记机制本身」), 还是把反向用例固化进既有闸的 `--selftest`? ★ | ★**根因已查明: 这 4 处不是「漏填」, 是这三个文件在清单生成之后才落盘 ⇒ 清单不自证新鲜 ⇒ 光补这 4 行不够** ⇒ 两条路都要有人记得跑 (★这道闸零挂链★) ★ |

---

> ★**【追加式订正块 · ISS-408 · 2026-11-25 · sw-lead】结束** ★
> ★**本块零写板 · 零落表 · 零改既有闸判据 · 零挂链 · 零外发 · 不代拍 · 不自签 `state/issue_log.yaml`** ★
