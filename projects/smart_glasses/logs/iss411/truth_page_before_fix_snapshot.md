# ★SW · 「板那一趟」SW 侧【必改面 → 闸的判据失效】影响面清账 ★

> ★**单号**: ISS-411 (cont1) · ★**派活**: 项目总工 (main / moli) · ★**执笔**: sw-lead (软件总工) · ★**日期**: 2026-11-25 ★
> ★**性质**: ★**纯查证 + 纯分析 + 新建真相页 + 新建机器闸 + 自有分片收口** ★ ⇒ ★**零写板 · 零落表 · 零改既有闸判据 · 零改既有页正文 · 零挂链 · 零外发 · 不代拍 · 不自签 `state/issue_log.yaml`** ★
> ★**主线关系**: ★老板 2026-11-17 00:43「接下来的目标是绘制 PCB 图」⇒ 本单属 ★**「板只改一次」纪律 ① (先派纯分析/作业包类, 不动板)** ★
> ★**新闸**: `SW/tools/check_sw_mustchange_face_impact.py` (★裸跑 rc=1 ★红的是现状★ · `--selftest` rc=0 末行 `ALL TESTS PASS` · ★零挂链★) ★
> ★**本单只出账, 不落改** ⇒ ★**「哪几道闸要改 / 怎么改 / 挂不挂链 / 顺序怎么排」全是 main 的地界 (机器块 `decision_taken_here` = `not_decided_here`)★** ★

---

## ★§0 · 一句话题面 ★

★★**「板只改一次」那一趟必改两个面: ① 位号改名 (B-1~B-8 · 脚表/网表/BOM/板面五侧同口径) ② 布线 45→0。★这两个面一落地, SW 域 31 道既有闸里 31 道的判据输入就变了 (改名面 18 道 + 布线面 11 道 + 文档面 12 道)★ ⇒ ★**其中 8 道硬编了位号字面量, 12 道钉死了板/三表 md5** ★ ⇒ ★**最要命的两条: 链上正在跑的 `check_sw_ref_reachability.py` 硬编 55 处 (口径B 78) · `check_onepass_sw_sync.py` 硬编 20 处 (其中 10 处是真位号) ⇒ 它们自己就在那 2 道里** ★ ⇒ ★**那一趟开工后, SW 侧会静默失守** ★★

★**三条坏结局 (★为什么这一格值钱★)** ★

① ★**改名面静默失效**: 位号加 `_1` 后缀 ⇒ 那 55+58 处硬编位号全部对不上 ⇒ 闸要么红 (★被当成真缺陷★) 要么静默跳过 (★前缀落进 C10/C11/C13 豁免分支·★更坏·因为它还绿着★) ⇒ SW 侧的真实可达性问题反而看不见了 ★
② ★**布线面基线漂移**: 布线 45→0 一落地, 18 道读板面的闸读数全变 ⇒ ★**它们钉的是旧基线 ⇒ 不重锚就红 ⇒ 而「红了」到底是【真缺陷】还是【基线该重锚】, 没人分得清** ★
③ ★**只读文档的闸**: 10 道闸一个真源都不读 ⇒ ★**真相页一改它们就漂, 而它们判的是「零假连通 / 亮度生物安全 / 目标兼容」这类放行级结论 ⇒ 放行级结论挂在一个自己会漂的读数上** ★

---

## ★§1 · 本机实测基线 (★全部可复现·不抄任何 agent 报告★) ★

| # | 事实 | 实测读数 | 复跑命令 |
|---|---|---|---|
| ① | ★**SW 域既有闸 = 31 道** ★ | `SW/tools/check_*.py` (30) + `SW/check_*.py` (0) = **31** | `ls SW/tools/check_*.py SW/check_*.py \| wc -l` |
| ② | ★**硬编位号闸 = 8 道 (口径A)** ★ | 逐闸从源码实读 (★闸的判据永远是【源码实读】, 不读登记册自己的数★) | `python3 SW/tools/check_sw_mustchange_face_impact.py --json` |
| ③ | ★**链内闸 = 6 道** ★ | 从 `state/gate_check.py` 的 ★**AST**★ 实算 (★不靠 grep★) | 同上 (T4 段) |
| ④ | ★**命门组合 = 2 条** ★ | ★**`SW/tools/check_onepass_sw_sync.py` (20 处) · `SW/tools/check_sw_ref_reachability.py` (55 处)** ★ | 同上 (T4 段) |
| ⑤ | ★**读板面闸 = 18 道** ★ | 板面关键词实扫 (`faces` 含 `board`) | 同上 (T2 段) |
| ⑥ | ★**无真源依赖闸 = 10 道** ★ | 六面关键词实扫 (`faces` ∩ {board,table,bom,firm} = ∅) | 同上 (T3 段) |
| ⑦ | ★**钉死基线的闸 = 12 道** ★ | 板 md5 形态 + 三表 md5 形态实扫 (`pin_board` / `pin_table`) | 同上 (T2 段) |
| ⑧ | ★**盘上闸总数 = 32 道 (含本闸自己)** ★ | ★**T1 要求登记册与盘上集合【逐条相等】⇒ 本闸自己也必须在册** ★ | `ls SW/**/check_*.py \| wc -l` |
| ⑨ | ★**板 / 网表 / 脚表 / BOM 四件指纹** ★ | 板 `611b869e13518c3c023fb178f91a0075` / `2026-11-06 07:07:17.362193413` / `4940213` · 网表 `6aee500e60ba0732f83a9cf557ba90ab` · 脚表 `9174309df1ec9411ac8e8d9e80ee386a` · BOM `5b9993992405904a60ac96a020b375d8` | `md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv` |

★**ISS-392 的链覆盖率现状 (★复核用·本单不擦它★)**: 盘上 31 道 · 链内 6 道 (19.4%) · 链外 25 道 · ★**元闸盲区: 它的 ROSTER 只扫 13 道, 盘上另外 18 道它看不见** ★[实测] ★

---

## ★§2 · 口径说明 (★本单的数与 main 的数对得上·以及 main 的口径漏了什么★) ★

### ★§2.1 · 口径A (★登记册主口径·★已逐字复现 main 的 8 个数字 8/8★) ★

★**定义**: ★**引号字面量** (单/双引号) + ★**前缀 ∈ {TP, J, U, C, Q, D, FB, SW}** + ★**后缀全大写** + ★**按【唯一 token 值】计数** ★

| 闸 | main 报数 | 本单口径A 实读 | 对拍 |
|---|---|---|---|
| `check_sw_ref_reachability_v2.py` | 58 | **58** | ✓ |
| `check_sw_ref_reachability.py` | 55 | **55** | ✓ |
| `check_onepass_sw_sync.py` | 20 | **20** | ✓ |
| `check_sw_ref_reachability_v2_selftest.py` | 8 | **8** | ✓ |
| `check_shutdown_semantics.py` | 6 | **6** | ✓ |
| `check_debug_pin_order_contract.py` | 2 | **2** | ✓ |
| `check_evt_charge_current_criterion.py` | 1 | **1** | ✓ |
| `check_load_switch_selection.py` | 1 | **1** | ✓ |

★★**⇒ 口径A 与 main 的口径逐字一致 (8/8) ⇒ main 题面 §1.1 事实② 的 8 个数字【可复现·本单不改动它】★** ★[实测] ★

### ★§2.2 · 口径A 漏了什么 (★本单发现的第二层★) ★

★**口径A 的前缀表里没有 `R_` (电阻) / `L_` / `BT_` (电芯) / `CONN_` (连接器) / `IC_`** ⇒ ★**本项目板上最多数的一族位号 (`R_*`) 被整体漏掉** ★

| 闸 | 口径A | 口径B (★补回 R_/L_/BT_/CONN_/IC_★) | 差 |
|---|---|---|---|
| `check_evt_charge_current_criterion.py` | **1** | **2** | **+1** |
| `check_debug_pin_order_contract.py` | **2** | **2** | — |
| `check_load_switch_selection.py` | **1** | **1** | — |
| `check_onepass_sw_sync.py` | **20** | **20** | — |
| `check_shutdown_semantics.py` | **6** | **7** | **+1** |
| `check_sw_ref_reachability.py` | **55** | **78** | **+23** |
| `check_sw_ref_reachability_v2.py` | **58** | **85** | **+27** |
| `check_sw_ref_reachability_v2_selftest.py` | **8** | **10** | **+2** |

★★**⇒ 口径A 与口径B 命中的【闸集合】相同 (还是那 8 道) ⇒ ★**改名的受影响面没有被口径漏掉闸**★; ★**但口径A 把每道闸的【硬编面大小】低估了 (v2: 58 → 85, +46%) ⇒ 谁先改、改多少, 口径A 会低估** ★** ⇒ 本单登记册【两个口径都登】(★T1 两条都判★) ★★

### ★§2.3 · 口径A 还有一处【语义误计】(★main 报 20, 真实硬编位号是 10★) ★

★**`check_onepass_sw_sync.py` 的 20 处里有 10 处是【环境变量键】不是位号** (`SW_SYNC_BOM` / `SW_SYNC_CHECKLIST` / `SW_SYNC_ISSUE_LOG` / `SW_SYNC_LANDING` / `SW_SYNC_LEDGER` / `SW_SYNC_NETLIST` / `SW_SYNC_PCB` / `SW_SYNC_PINS` / `SW_SYNC_PRO` / `SW_SYNC_TMPDIR`·源码 92/109 行) ⇒ ★**真实硬编位号 = 10 处** (`D_CHG_LED` / `D_LED_G` / `D_LED_R` / `Q_CHG_LED` / `SW_BOOT` / `SW_KEY_PWR` / `SW_KEY_VM` / `SW_KEY_VP` / `SW_RST` / `TP_INT`·源码 181~204 行) ⇒ ★**不影响本闸的判据 (口径A 原样登记), 但影响「改完之后还有几处要改」的算法** ★[实测] ★

---

## ★§3 · 表 (a) · 31 道既有闸 + 本闸 × 输入面 × 硬编位号 逐条清单 ★

★**读法**: 「改名面判定」列 = ★**那一趟落地之后这道闸的读数会怎么变**★; 最后一列给的是★**逐条判断依据 (★为什么是这一类·不是「应该没碰」★)★**。★**三分类定义 (★下一段)★** ★

★**三分类定义 (★本单口径★)**: ★**判绿变判红** = 今天判绿, 那一趟之后变红 (★误判阻塞★) · ★**判红变判绿** = 今天判红, 那一趟之后变绿 (★误判放行★) · ★**静默跳过** = ★**闸照样绿, 但它判的那件事它已经不判了** (★误判放行·★最危险的一类·★因为没有任何红告诉你★)** ★

| # | 闸 | 链 | 硬编位号 (A/B) | 输入面 | 钉基线 | 改名面判定 | ★**逐条判断依据** ★ |
|---|---|---|---|---|---|---|---|
| 1 | `check_evt_charge_current_criterion.py` | 链外 | **1 / 2** | 脚表/网表 · 文档 | — | ★**判绿变判红** ★ | ★**判绿变判红** ★: 判据是「网表里读不到 `U_CHG` / `R_ILIM` 行 ⇒ `errors.append`」(源码 128/141/143 行) ⇒ 改名后 `U_CHG` 不在网表 ⇒ 直接红 (★误判阻塞★) · ★**静默跳过**: 无豁免分支, 找不到就是红 ⇒ 不会静默 ★ · ★**判红变判绿**: 无 (它今天判绿) ★ · ★**口径B 另含 `R_ILIM`** (源码 141 行) ⇒ 电阻族一改名它就同时失去充电电流判据的输入 ★ |
| 2 | `check_brightness_biosafety.py` | 链外 | **0 / 0** | 文档 | — | ★**不受影响** ★ | ★**不受影响** ★ (改名面/布线面都读不到它) ⇒ ★**但它一个真源都不读 (只读真相页) ⇒ 真相页一改它的读数就漂 ⇒ 放行级结论挂在一个会漂的读数上** ★ · ★**判绿变判红 / 判红变判绿 / 静默跳过 三分类对它都不适用 (它压根不看板) ★ |
| 3 | `check_debug_header_fw_impact.py` | 链外 | **0 / 0** | 板面 · 脚表/网表 · BOM · 文档 | 板 | ★**基线漂移-须重锚** ★ | ★**基线漂移-须重锚** ★: 判据 = 「板 md5/mtime/size 三项 + 网表/脚表/BOM 三件 md5 全部与基线一致」(源码 549/564/571 行) ⇒ ★**那一趟板文件必变 ⇒ 指纹三项全不一致 ⇒ 判绿变判红 (★误判阻塞★)** ★ · ★**静默跳过**: 无 (不一致就是红) ★ · ★**判红变判绿**: 无 ★ · ★**重锚办法已存在**: 它的基线块 (`baseline`) 由脚本自己写回 (源码 795 行 `blk.setdefault('baseline',{})['board_md5']='0'*32`) ⇒ 有合法重锚通道 ★ |
| 4 | `check_debug_pin_order_contract.py` | 链外 | **2 / 2** | 板面 · 脚表/网表 · 文档 | 板 | ★**判绿变判红** ★ | ★**判绿变判红** ★: 判据 = 用 `pcbnew` 读板 → 按 `J_DEBUG` / `J_UART` 两个 ref 找 land / pad1 形状 (源码 141/168/241/293 行) ⇒ ★**改名后这两个 ref 在板上不存在 ⇒ 读不到 land ⇒ 闸直接报不出/判红 (★误判阻塞★)** ★ · ★**静默跳过**: 无 (ref 找不到是硬错) ★ · ★**判红变判绿**: 无 ★ |
| 5 | `check_demo_panel_spec.py` | 链外 | **0 / 0** | 板面 · 脚表/网表 · 文档 · 台账 · 固件源码 | — | ★**有合法改板通道** ★ | ★**有合法改板通道** ★: 锚点**不住在脚本里** (住 `SW/SW_MD5_BASELINE_LEDGER.md` §1 的机器可读 YAML 块) ⇒ 台账刷新即可, 不必改判据; 且脚本自带 `--skip-md5` 开关 (★「hw-lead 合法改板后用」·源码 45 行★) ⇒ ★**那一趟有合法通道 ⇒ 不会误判放行, 也不会误判阻塞** ★ |
| 6 | `check_demo_panel_spec_r6_chainjudge_selftest.py` | ★**链上** ★ | **0 / 0** | 板面 · 脚表/网表 · 文档 · 台账 | — | ★**不受影响** ★ | ★**不受影响** ★: 它是夹具 (自造台账) ⇒ 改名面/布线面都改变不了它的读数 ⇒ ★**但它的绿不再覆盖真台账 ⇒ 覆盖失效 (★静默★) 而不是判据失效** ★ |
| 7 | `check_demo_panel_spec_r6_hardprot_iss315_selftest.py` | ★**链上** ★ | **0 / 0** | 台账 | — | ★**不受影响** ★ | ★**不受影响** ★ (只读台账, faces=`ledger`) ⇒ ★**文档面会漂**: 台账一改它就读数漂 ⇒ 随真相页/台账改即漂 ★ |
| 8 | `check_demo_panel_spec_r6_selftest.py` | ★**链上** ★ | **0 / 0** | 板面 · 脚表/网表 · 文档 · 台账 | — | ★**不受影响** ★ | ★**不受影响** ★ (夹具自造板/网表/台账) ⇒ ★**但它自己文档里写明 R6 分支 = 「硬保护件 (板 / .kicad_pro) md5 变 ⇒ 判红」, 且注明「★板变是板那一趟的事★」** ⇒ ★**真盘上那一趟必然红 ⇒ 真盘侧的对应闸是 `check_demo_panel_spec` (有合法通道) ⇒ 本夹具只是把「板变会红」这件事在沙盒里演了一遍** ★ |
| 9 | `check_fp_truth_read.py` | 链外 | **0 / 0** | 板面 · 脚表/网表 · BOM · 文档 · 台账 | 板 + 三表 | ★**基线漂移-须重锚** ★ | ★**基线漂移-须重锚** ★: 它把板三项 + 三表 md5 全钉死 (源码 87/88/89 行) ⇒ ★**那一趟板必改 ⇒ 三项指纹 + 三表 md5 全漂 ⇒ 判绿变判红 (★误判阻塞★)** ★ · ★**它在 592 行就写着「老 = 6aee500e60ba…」的自证对照 ⇒ 重锚路径现成** ★ |
| 10 | `check_iss250_rknn_target_gate.py` | 链外 | **0 / 0** | 文档 | — | ★**不受影响** ★ | ★**不受影响** ★ (只读文档) ⇒ ★**文档面会漂**: 真相页一改就漂 ⇒ 放行级结论挂在会漂的读数上 ★ |
| 11 | `check_iss355_convert_route.py` | 链外 | **0 / 0** | 文档 · 台账 | — | ★**不受影响** ★ | ★**不受影响** ★ (只读文档 + 台账) ⇒ ★**文档面会漂** ★ |
| 12 | `check_landing_trace_obligation.py` | ★**链上** ★ | **0 / 0** | 板面 · 脚表/网表 · BOM · 台账 |  + 三表 | ★**基线漂移-须重锚** ★ | ★**判绿变判红 (顺序依赖)** ★: 判据 = 「落表台账里每个新 md5 必须有留痕」+「硬保护件 `hard_protected[]` 两件」(源码 98/143 行) ⇒ ★**那一趟板改 ⇒ 台账必须先落一行写新 md5 ⇒ 这道闸才成立 ⇒ 不先落台账就红 (★误判阻塞·但这是【真的红】★)** ★ · ★**它明确不许硬编码 md5/单号** (源码 35 行) ⇒ 重锚路径 = 落台账, 不改判据** ★ |
| 13 | `check_load_switch_selection.py` | 链外 | **1 / 1** | 脚表/网表 · 文档 | — | ★**判绿变判红** ★ | ★**判绿变判红** ★: 判据 = 从真相页基准块 + 网表文本里找 `U_PWR_SW` (源码 156/173 行) ⇒ ★**改名后网表里没有 `U_PWR_SW` ⇒ 选型判据失去输入 ⇒ 判红 (★误判阻塞★)** ★ · ★**静默跳过**: 无 ★ |
| 14 | `check_onepass_legb_sw_impact.py` | 链外 | **0 / 0** | 板面 · 脚表/网表 · BOM · 文档 · 台账 | 板 + 三表 | ★**基线漂移-须重锚** ★ | ★**基线漂移-须重锚** ★: 它把板 + 网表 + 脚表 + BOM 四件 md5 全钉死 (源码 70~73 行) ⇒ ★**那一趟必改 ⇒ 四件指纹全漂 ⇒ 判绿变判红 (★误判阻塞★)** ★ |
| 15 | `check_onepass_sw_release.py` | 链外 | **0 / 0** | 文档 · 台账 | — | ★**不受影响** ★ | ★**不受影响** ★ (只读文档 + 台账) ⇒ ★**文档面会漂** ★ |
| 16 | `check_onepass_sw_sync.py` | ★**链上** ★ | **20 / 20** | 板面 · 脚表/网表 · BOM · 文档 · 台账 | 板 | ★**判绿变判红** ★ | ★★**★这是本单第二号命门 (在链上·硬编 20 处)★**★★ · ★**20 处里 10 处是环境变量键不是位号** (`SW_SYNC_BOM`/`SW_SYNC_CHECKLIST`/`SW_SYNC_ISSUE_LOG`/`SW_SYNC_LANDING`/`SW_SYNC_LEDGER`/`SW_SYNC_NETLIST`/`SW_SYNC_PCB`/`SW_SYNC_PINS`/`SW_SYNC_PRO`/`SW_SYNC_TMPDIR`·源码 92/109 行) ⇒ 板一改它们锚的 md5 必变 ⇒ W3/W4 红 (★判绿变判红·★误判阻塞★) ★ · ★**另 10 处是真位号** (`D_CHG_LED`/`D_LED_G`/`D_LED_R`/`Q_CHG_LED`/`SW_BOOT`/`SW_KEY_PWR`/`SW_KEY_VM`/`SW_KEY_VP`/`SW_RST`/`TP_INT`·源码 181~204 行), ★**它们出现在【探针命令串】里, 判据是【探针输出正则】 `(D_CHG_LED \d+ 次 · Q_CHG_LED \d+ 次)`** ⇒ ★**改名后探针 grep 不到 ⇒ 输出变成 `0 次` ⇒ 正则里的 `\d+` 照样匹配 `0` ⇒ 闸照样绿, 但它已经什么都没测 ⇒ ★★静默跳过 (★误判放行·最危险的一类★)★★** ★ · ★**判红变判绿**: 无 (它今天判绿) ★ |
| 17 | `check_rk3572_target_caliber.py` | 链外 | **0 / 0** | 文档 · 台账 | — | ★**不受影响** ★ | ★**不受影响** ★ (只读文档 + 台账) ⇒ ★**文档面会漂** ★ |
| 18 | `check_rk3572_vccio_domain.py` | 链外 | **0 / 0** | 脚表/网表 · 文档 | — | ★**不受影响** ★ | ★**不受影响** ★: 它读脚表 + 文档, ★**不钉任何 md5** ⇒ ★**前提**: B-1~B-8 的改名清单里【没有 VCIO 域的位号】⇒ 否则它的读数会变 ⇒ ★**这一条本单未拿到 B-1~B-8 的逐条清单 ⇒ 标 [推算]·留给 main 核对** ★ |
| 19 | `check_rknn_target_compat.py` | 链外 | **0 / 0** | ★**无 (读工具链产物)** ★ | — | ★**不受影响** ★ | ★**不受影响** ★: ★**它一个仓内真源都不读 (faces 全空) ⇒ 读的是 rknn 工具链产物** ⇒ 改名面/布线面都打不到它 ⇒ ★**只有工具链产物变了才漂** (drift_src=工具链产物) ★ |
| 20 | `check_shutdown_semantics.py` | 链外 | **6 / 7** | 脚表/网表 · 文档 | — | ★**条件性-随真相页字段** ★ | ★★**条件性-随真相页字段**★★: 判据 = R1「口径基准块字段齐全」+ R2「★真相页/HW 页/镜像页三处【关机语义字面量】必须一致★」(源码 294~326 行) ⇒ ★**6 处硬编位号 (`J_USB_C`/`Q_CHG_LED`/`Q_PG`/`U_CHG`/`U_EN_SW`/`U_PWR_SW`) 一旦有人随改名改了三页里的字面量而闸内 6 个没同步 ⇒ R2 比对失败 ⇒ 判绿变判红** ★ · ★**但若三页与闸在同一个改动里同步改 ⇒ 仍绿** ⇒ ★**⇒ 它的红绿取决于【真相页字段是否同步】, 不是恒红 ⇒ 条件性** ★ |
| 21 | `check_sw09_patch_dryrun.py` | 链外 | **0 / 0** | 文档 · 台账 | — | ★**不受影响** ★ | ★**不受影响** ★ (只读文档 + 台账) ⇒ ★**文档面会漂** ★ |
| 22 | `check_sw_board_md5_rebase_readiness.py` | 链外 | **0 / 0** | 板面 · 文档 | 板 | ★**基线漂移-须重锚** ★ | ★★**它是【板 md5 变化的守门人】本身 (ISS-408 已签收)⇒ 那一趟板一改它必然转红/转「待重锚」⇒ ★这是【设计意图】不是误判★**** ⇒ 登记为 rename=基线漂移-须重锚 · route=基线漂移-自守闸告警器 ⇒ ★**它自己还钉了 `NEEDLE_PREFIX='611b'+'869e'` (源码 47 行) 与 `CHANNEL_MIN=('reboard','prev_md5')` (88 行) ⇒ 那一趟必须有【重锚 + 落台账】两个通道都到位, 它才转绿** ★ |
| 23 | `check_sw_false_connectivity_gate.py` | 链外 | **0 / 0** | 板面 · 脚表/网表 · BOM · 文档 | 板 + 三表 | ★**基线漂移-须重锚** ★ | ★**基线漂移-须重锚** ★: 它把板三项 + 三表 md5 + 基线指纹文件 `logs/iss381/baseline_fingerprints.txt` 全钉死 (源码 65/73/74/75/77 行) ⇒ ★**那一趟板改 ⇒ 零假连通的全部基线漂 ⇒ 判绿变判红 (★误判阻塞★)** ★ · ★**重锚 = ISS-381 的基线指纹文件必须重出 (★那是 main 的动作★)** ★ |
| 24 | `check_sw_fp_truth_impact.py` | 链外 | **0 / 0** | 板面 · 脚表/网表 · BOM · 文档 · 台账 |  + 三表 | ★**基线漂移-须重锚** ★ | ★**判绿变判红 (但方向相反·红是真的)** ★: 它判的是「SW 侧待办 need 里引着的过期 md5 逐条登记清理」(源码 16/30 行, 今日实测 27 条陈旧) ⇒ ★**那一趟板 md5 一变 ⇒ 过期 md5 从 27 条变多 ⇒ 它转红 ⇒ 这是【真的红】不是误判, 但它会阻塞 ⇒ 必须与那一趟同批清** ★ |
| 25 | `check_sw_gate_chain_coverage.py` | 链外 | **0 / 0** | 板面 · 脚表/网表 · BOM · 文档 | 板 + 三表 | ★**基线漂移-须重锚** ★ | ★★**自守告警器 (ISS-392 已签收·链外闸)**★★: 它钉 `NEEDLE_PREFIX='611b'+'869e'` (源码 73 行) + 三表 md5 (79~81 行) ⇒ ★**它扫的是【全仓对板 md5 的引用面】⇒ 那一趟板 md5 一变 ⇒ 全仓几十处引用全部陈旧 ⇒ 它必然转红 ⇒ 这是它的本职工作** ★ · ★**但它在【链外】(链内只有 6 道) ⇒ 没人跑它 ⇒ ★它的红不会有人看见 ⇒ 静默风险** ★ · ★**判绿变判红 / 判红变判绿 / 静默跳过 三分类对它 = 判绿变判红 (★误判阻塞·但也是【真的红】★)** ★ |
| 26 | `check_sw_gate_health.py` | 链外 | **0 / 0** | 板面 · 脚表/网表 · BOM · 文档 | 板 + 三表 | ★**基线漂移-须重锚** ★ | ★★**自守告警器 (ISS-388 已签收·链外闸)**★★: 同样钉 `NEEDLE_PREFIX` (61 行) + 三表 md5 (67~69 行) ⇒ ★**那一趟板一改 ⇒ 它的读数漂 ⇒ 必然转红 ⇒ 它在【链外】⇒ 没人跑 ⇒ 静默风险** ★ |
| 27 | `check_sw_ref_reachability.py` | ★**链上** ★ | **55 / 78** | 板面 · 脚表/网表 · BOM · 文档 | — | ★**判绿变判红** ★ | ★★★**★这是本单头号命门 (在链上·硬编 55 处·口径B 78 处)★**★★★ · ★**判绿变判红** ★: 判据 = 文档里的位号 token 按 C1~C14 分类, 落 `DESIGNATOR_MISSING` (C14) 或 `DESIGNATOR_DRIFT` 就红 (源码 259 行 `FAIL_CLASSES` / 466 行) ⇒ ★**改名后旧 token 仍在文档与冻结表 `DESIGNATOR_REGISTRY` (55 处硬编·源码 161 行) 里、但不再是 live ⇒ 新增 missing ⇒ 红 (★误判阻塞★)** ★ · ★★★**★静默跳过 (最危险的一类)** ★★★: ★**若新位号前缀落进 `SIGNAL_PREFIXES` (C11·信号/电源轨命名空间) / `PHYSICS_PREFIXES` (C10·`L_` 物理量) / `SW_` (C13·软件命名空间) / 或成为 ≥2 个 live 位号的严格前缀 (C12) ⇒ 该 token 被判 `DOC_INTERNAL`/`NET_NAME` ⇒ 不进 `FAIL_CLASSES` ⇒ 闸照样绿, 但这条检查被跳过 ⇒ ★★误判放行★★** ★ · ★★**判红变判绿** ★★: `BASELINE_TOKENS` 三条 (`TP_INT`/`TP_TEMP`/`CONN_USB`, 源码 134 行) 是【已登记的真隐患】, 允许上限 `BASELINE_COUNT=3` (131 行) ⇒ ★**若改名把它们从文档里删掉 ⇒ `missing_total` 掉到 3 以下 ⇒ 基线豁免失配 ⇒ 闸转绿 ⇒ 真实缺陷被豁免掉 ⇒ 误判放行** ★ · ★★**修法已存在**: `--freeze-registry` 一条命令重建冻结表 (源码 56 行) ⇒ ★**但那是改判据 ⇒ main 的地界** ★ |
| 28 | `check_sw_ref_reachability_v2.py` | 链外 | **58 / 85** | 板面 · 脚表/网表 · BOM · 文档 | — | ★**判绿变判红** ★ | ★★★**★头号命门第二版 (链外·硬编 58 处·口径B 85 处)** ★★★ · ★**判绿变判红 / 静默跳过 / 判红变判绿 三条与 v1 同构** (同一套 C1~C14 分类 + 同一份 `BASELINE_TOKENS` 三条 + 同一份 `DESIGNATOR_REGISTRY` 冻结表, 源码 318/466/152/155 行) ⇒ ★**挂 v1 还是挂 v2 都会在改名后失守 ⇒ ISS-392 实测「v1 在链上 / v2 没挂」这件事本身不解决问题** ★ · ★**它比 v1 更紧**: 额外做【探针失配自检】(源码 511~529 行) ⇒ ★**冻结表与真盘失配时它会额外报「登记制闸门没在拦」⇒ 它的红里【多一层自证】⇒ 改名后它比 v1 更早暴露, 但也更会误红** ★ |
| 29 | `check_sw_ref_reachability_v2_selftest.py` | 链外 | **8 / 10** | 板面 · 文档 | — | ★**判绿变判红** ★ | ★**判绿变判红** ★: ★**它 8 处硬编里有 3 处是真位号** (`TP_INT`/`TP_TEMP`/`CONN_USB` = v1/v2 的 `BASELINE_TOKENS` 三条真隐患), ★**另 5 处是沙盒合成 token** (`U_TEMP`/`U_TEMP_1`/`TP_INT_ISSX`/`TP_TEMP_ISSX`/`SW_TEMP_ISSX`·源码 105 行自造) ⇒ ★**更要命的是它断言【真盘】的分类计数**: 源码 172/177 行 `c_v2.get('DESIGNATOR_OK')==78 and c_v2.get('DESIGNATOR_MISSING')==3` ⇒ ★**改名后真盘的 OK/MISSING 计数必变 ⇒ 断言失败 ⇒ 判绿变判红 (★误判阻塞·★但红是真的★)** ★ · ★**另注**: 它的 `EXPECT_REAL` 常量 (源码 53 行) 是 78/3/9/23 四元组 ⇒ 同一类失效的第二处 ★ |
| 30 | `check_sw_zero_copper_grade_consistency.py` | 链外 | **0 / 0** | 文档 | — | ★**不受影响** ★ | ★**不受影响** ★ (只读文档) ⇒ ★**文档面会漂** ★ |
| 31 | `check_timing_review_adc_sync.py` | 链外 | **0 / 0** | 文档 | — | ★**不受影响** ★ | ★**不受影响** ★ (只读文档) ⇒ ★**文档面会漂** ★ |
| 32 | `check_sw_mustchange_face_impact.py` | ★**本闸 (零挂链)** ★ | **0 / 0** | 板面 · 脚表/网表 · BOM · 文档 · 台账 · 固件源码 | 板 + 三表 | ★**不受影响** ★ | ★**不受影响** (改名面) ★: ★**本闸一个位号字面量都没硬编 (口径A 实读 0 处)** ⇒ 改名打不到它 ★ · ★**布线面 = 基线漂移-自守闸告警器** ★: T0 把板三项 (md5/mtime/size) + 三表 md5 钉死 ⇒ ★**板一改它就红 ⇒ 但它的红【是设计意图】(它守的就是「本单期间板不许被动」) ⇒ 那一趟开工时必须把三个常量同步重锚到新板, 否则谁跑它谁误红** ★ · ★**文档面 = 随真相页/台账改即漂** ★: T3 读本页机器块的 `counts` · T8 把本页登记册与闸内冻结快照对拍 ⇒ ★**本页被单方面改动 ⇒ T8 当场红 (★这是它防的就是这个★)** ★ |

★**表 (a) 的三个统计 (★机器可复算·闸的 T1/T2/T3/T5 就在判这三件事★)**: ★**硬编位号 8 道** ★ · ★**无真源依赖 10 道** ★ · ★**钉死基线 12 道** ★ · ★**链内 6 道 (其中命门 2 条)** ★

---

## ★§4 · 表 (b) · 改名面受影响闸 + 布线面要重锚的 18 道 逐道 ★

### ★§4.1 · 「改名面」受影响闸清单 (★硬编位号的 8 道 + 靠指纹间接受伤的 9 道★) ★

| 闸 | 硬编位号 (A/B) | 改名面判定 | 那一趟落地后它的读数为什么变 |
|---|---|---|---|
| `check_evt_charge_current_criterion.py` | **1 / 2** | ★**判绿变判红** ★ | ★**判绿变判红** ★: 判据是「网表里读不到 `U_CHG` / `R_ILIM` 行 ⇒ `errors.append`」(源码 128/141/143 行) ⇒ 改名后 `U_CHG` 不在网表 ⇒ 直接红 (★误判阻塞★) · ★**静默跳过**: 无豁免分支, 找不到就是红 ⇒ 不会静默 ★ · ★**判红变判绿**: 无 (它今天判绿) ★ · ★**口径B 另含 `R_ILIM`** (源码 141 行) ⇒ 电阻族一改名它就同时失去充电电流判据的输入 ★ |
| `check_debug_header_fw_impact.py` | **0 / 0** | ★**基线漂移-须重锚** ★ | ★**基线漂移-须重锚** ★: 判据 = 「板 md5/mtime/size 三项 + 网表/脚表/BOM 三件 md5 全部与基线一致」(源码 549/564/571 行) ⇒ ★**那一趟板文件必变 ⇒ 指纹三项全不一致 ⇒ 判绿变判红 (★误判阻塞★)** ★ · ★**静默跳过**: 无 (不一致就是红) ★ · ★**判红变判绿**: 无 ★ · ★**重锚办法已存在**: 它的基线块 (`baseline`) 由脚本自己写回 (源码 795 行 `blk.setdefault('baseline',{})['board_md5']='0'*32`) ⇒ 有合法重锚通道 ★ |
| `check_debug_pin_order_contract.py` | **2 / 2** | ★**判绿变判红** ★ | ★**判绿变判红** ★: 判据 = 用 `pcbnew` 读板 → 按 `J_DEBUG` / `J_UART` 两个 ref 找 land / pad1 形状 (源码 141/168/241/293 行) ⇒ ★**改名后这两个 ref 在板上不存在 ⇒ 读不到 land ⇒ 闸直接报不出/判红 (★误判阻塞★)** ★ · ★**静默跳过**: 无 (ref 找不到是硬错) ★ · ★**判红变判绿**: 无 ★ |
| `check_demo_panel_spec.py` | **0 / 0** | ★**有合法改板通道** ★ | ★**有合法改板通道** ★: 锚点**不住在脚本里** (住 `SW/SW_MD5_BASELINE_LEDGER.md` §1 的机器可读 YAML 块) ⇒ 台账刷新即可, 不必改判据; 且脚本自带 `--skip-md5` 开关 (★「hw-lead 合法改板后用」·源码 45 行★) ⇒ ★**那一趟有合法通道 ⇒ 不会误判放行, 也不会误判阻塞** ★ |
| `check_fp_truth_read.py` | **0 / 0** | ★**基线漂移-须重锚** ★ | ★**基线漂移-须重锚** ★: 它把板三项 + 三表 md5 全钉死 (源码 87/88/89 行) ⇒ ★**那一趟板必改 ⇒ 三项指纹 + 三表 md5 全漂 ⇒ 判绿变判红 (★误判阻塞★)** ★ · ★**它在 592 行就写着「老 = 6aee500e60ba…」的自证对照 ⇒ 重锚路径现成** ★ |
| `check_landing_trace_obligation.py` | **0 / 0** | ★**基线漂移-须重锚** ★ | ★**判绿变判红 (顺序依赖)** ★: 判据 = 「落表台账里每个新 md5 必须有留痕」+「硬保护件 `hard_protected[]` 两件」(源码 98/143 行) ⇒ ★**那一趟板改 ⇒ 台账必须先落一行写新 md5 ⇒ 这道闸才成立 ⇒ 不先落台账就红 (★误判阻塞·但这是【真的红】★)** ★ · ★**它明确不许硬编码 md5/单号** (源码 35 行) ⇒ 重锚路径 = 落台账, 不改判据** ★ |
| `check_load_switch_selection.py` | **1 / 1** | ★**判绿变判红** ★ | ★**判绿变判红** ★: 判据 = 从真相页基准块 + 网表文本里找 `U_PWR_SW` (源码 156/173 行) ⇒ ★**改名后网表里没有 `U_PWR_SW` ⇒ 选型判据失去输入 ⇒ 判红 (★误判阻塞★)** ★ · ★**静默跳过**: 无 ★ |
| `check_onepass_legb_sw_impact.py` | **0 / 0** | ★**基线漂移-须重锚** ★ | ★**基线漂移-须重锚** ★: 它把板 + 网表 + 脚表 + BOM 四件 md5 全钉死 (源码 70~73 行) ⇒ ★**那一趟必改 ⇒ 四件指纹全漂 ⇒ 判绿变判红 (★误判阻塞★)** ★ |
| `check_onepass_sw_sync.py` | **20 / 20** | ★**判绿变判红** ★ | ★★**★这是本单第二号命门 (在链上·硬编 20 处)★**★★ · ★**20 处里 10 处是环境变量键不是位号** (`SW_SYNC_BOM`/`SW_SYNC_CHECKLIST`/`SW_SYNC_ISSUE_LOG`/`SW_SYNC_LANDING`/`SW_SYNC_LEDGER`/`SW_SYNC_NETLIST`/`SW_SYNC_PCB`/`SW_SYNC_PINS`/`SW_SYNC_PRO`/`SW_SYNC_TMPDIR`·源码 92/109 行) ⇒ 板一改它们锚的 md5 必变 ⇒ W3/W4 红 (★判绿变判红·★误判阻塞★) ★ · ★**另 10 处是真位号** (`D_CHG_LED`/`D_LED_G`/`D_LED_R`/`Q_CHG_LED`/`SW_BOOT`/`SW_KEY_PWR`/`SW_KEY_VM`/`SW_KEY_VP`/`SW_RST`/`TP_INT`·源码 181~204 行), ★**它们出现在【探针命令串】里, 判据是【探针输出正则】 `(D_CHG_LED \d+ 次 · Q_CHG_LED \d+ 次)`** ⇒ ★**改名后探针 grep 不到 ⇒ 输出变成 `0 次` ⇒ 正则里的 `\d+` 照样匹配 `0` ⇒ 闸照样绿, 但它已经什么都没测 ⇒ ★★静默跳过 (★误判放行·最危险的一类★)★★** ★ · ★**判红变判绿**: 无 (它今天判绿) ★ |
| `check_shutdown_semantics.py` | **6 / 7** | ★**条件性-随真相页字段** ★ | ★★**条件性-随真相页字段**★★: 判据 = R1「口径基准块字段齐全」+ R2「★真相页/HW 页/镜像页三处【关机语义字面量】必须一致★」(源码 294~326 行) ⇒ ★**6 处硬编位号 (`J_USB_C`/`Q_CHG_LED`/`Q_PG`/`U_CHG`/`U_EN_SW`/`U_PWR_SW`) 一旦有人随改名改了三页里的字面量而闸内 6 个没同步 ⇒ R2 比对失败 ⇒ 判绿变判红** ★ · ★**但若三页与闸在同一个改动里同步改 ⇒ 仍绿** ⇒ ★**⇒ 它的红绿取决于【真相页字段是否同步】, 不是恒红 ⇒ 条件性** ★ |
| `check_sw_board_md5_rebase_readiness.py` | **0 / 0** | ★**基线漂移-须重锚** ★ | ★★**它是【板 md5 变化的守门人】本身 (ISS-408 已签收)⇒ 那一趟板一改它必然转红/转「待重锚」⇒ ★这是【设计意图】不是误判★**** ⇒ 登记为 rename=基线漂移-须重锚 · route=基线漂移-自守闸告警器 ⇒ ★**它自己还钉了 `NEEDLE_PREFIX='611b'+'869e'` (源码 47 行) 与 `CHANNEL_MIN=('reboard','prev_md5')` (88 行) ⇒ 那一趟必须有【重锚 + 落台账】两个通道都到位, 它才转绿** ★ |
| `check_sw_false_connectivity_gate.py` | **0 / 0** | ★**基线漂移-须重锚** ★ | ★**基线漂移-须重锚** ★: 它把板三项 + 三表 md5 + 基线指纹文件 `logs/iss381/baseline_fingerprints.txt` 全钉死 (源码 65/73/74/75/77 行) ⇒ ★**那一趟板改 ⇒ 零假连通的全部基线漂 ⇒ 判绿变判红 (★误判阻塞★)** ★ · ★**重锚 = ISS-381 的基线指纹文件必须重出 (★那是 main 的动作★)** ★ |
| `check_sw_fp_truth_impact.py` | **0 / 0** | ★**基线漂移-须重锚** ★ | ★**判绿变判红 (但方向相反·红是真的)** ★: 它判的是「SW 侧待办 need 里引着的过期 md5 逐条登记清理」(源码 16/30 行, 今日实测 27 条陈旧) ⇒ ★**那一趟板 md5 一变 ⇒ 过期 md5 从 27 条变多 ⇒ 它转红 ⇒ 这是【真的红】不是误判, 但它会阻塞 ⇒ 必须与那一趟同批清** ★ |
| `check_sw_gate_chain_coverage.py` | **0 / 0** | ★**基线漂移-须重锚** ★ | ★★**自守告警器 (ISS-392 已签收·链外闸)**★★: 它钉 `NEEDLE_PREFIX='611b'+'869e'` (源码 73 行) + 三表 md5 (79~81 行) ⇒ ★**它扫的是【全仓对板 md5 的引用面】⇒ 那一趟板 md5 一变 ⇒ 全仓几十处引用全部陈旧 ⇒ 它必然转红 ⇒ 这是它的本职工作** ★ · ★**但它在【链外】(链内只有 6 道) ⇒ 没人跑它 ⇒ ★它的红不会有人看见 ⇒ 静默风险** ★ · ★**判绿变判红 / 判红变判绿 / 静默跳过 三分类对它 = 判绿变判红 (★误判阻塞·但也是【真的红】★)** ★ |
| `check_sw_gate_health.py` | **0 / 0** | ★**基线漂移-须重锚** ★ | ★★**自守告警器 (ISS-388 已签收·链外闸)**★★: 同样钉 `NEEDLE_PREFIX` (61 行) + 三表 md5 (67~69 行) ⇒ ★**那一趟板一改 ⇒ 它的读数漂 ⇒ 必然转红 ⇒ 它在【链外】⇒ 没人跑 ⇒ 静默风险** ★ |
| `check_sw_ref_reachability.py` | **55 / 78** | ★**判绿变判红** ★ | ★★★**★这是本单头号命门 (在链上·硬编 55 处·口径B 78 处)★**★★★ · ★**判绿变判红** ★: 判据 = 文档里的位号 token 按 C1~C14 分类, 落 `DESIGNATOR_MISSING` (C14) 或 `DESIGNATOR_DRIFT` 就红 (源码 259 行 `FAIL_CLASSES` / 466 行) ⇒ ★**改名后旧 token 仍在文档与冻结表 `DESIGNATOR_REGISTRY` (55 处硬编·源码 161 行) 里、但不再是 live ⇒ 新增 missing ⇒ 红 (★误判阻塞★)** ★ · ★★★**★静默跳过 (最危险的一类)** ★★★: ★**若新位号前缀落进 `SIGNAL_PREFIXES` (C11·信号/电源轨命名空间) / `PHYSICS_PREFIXES` (C10·`L_` 物理量) / `SW_` (C13·软件命名空间) / 或成为 ≥2 个 live 位号的严格前缀 (C12) ⇒ 该 token 被判 `DOC_INTERNAL`/`NET_NAME` ⇒ 不进 `FAIL_CLASSES` ⇒ 闸照样绿, 但这条检查被跳过 ⇒ ★★误判放行★★** ★ · ★★**判红变判绿** ★★: `BASELINE_TOKENS` 三条 (`TP_INT`/`TP_TEMP`/`CONN_USB`, 源码 134 行) 是【已登记的真隐患】, 允许上限 `BASELINE_COUNT=3` (131 行) ⇒ ★**若改名把它们从文档里删掉 ⇒ `missing_total` 掉到 3 以下 ⇒ 基线豁免失配 ⇒ 闸转绿 ⇒ 真实缺陷被豁免掉 ⇒ 误判放行** ★ · ★★**修法已存在**: `--freeze-registry` 一条命令重建冻结表 (源码 56 行) ⇒ ★**但那是改判据 ⇒ main 的地界** ★ |
| `check_sw_ref_reachability_v2.py` | **58 / 85** | ★**判绿变判红** ★ | ★★★**★头号命门第二版 (链外·硬编 58 处·口径B 85 处)** ★★★ · ★**判绿变判红 / 静默跳过 / 判红变判绿 三条与 v1 同构** (同一套 C1~C14 分类 + 同一份 `BASELINE_TOKENS` 三条 + 同一份 `DESIGNATOR_REGISTRY` 冻结表, 源码 318/466/152/155 行) ⇒ ★**挂 v1 还是挂 v2 都会在改名后失守 ⇒ ISS-392 实测「v1 在链上 / v2 没挂」这件事本身不解决问题** ★ · ★**它比 v1 更紧**: 额外做【探针失配自检】(源码 511~529 行) ⇒ ★**冻结表与真盘失配时它会额外报「登记制闸门没在拦」⇒ 它的红里【多一层自证】⇒ 改名后它比 v1 更早暴露, 但也更会误红** ★ |
| `check_sw_ref_reachability_v2_selftest.py` | **8 / 10** | ★**判绿变判红** ★ | ★**判绿变判红** ★: ★**它 8 处硬编里有 3 处是真位号** (`TP_INT`/`TP_TEMP`/`CONN_USB` = v1/v2 的 `BASELINE_TOKENS` 三条真隐患), ★**另 5 处是沙盒合成 token** (`U_TEMP`/`U_TEMP_1`/`TP_INT_ISSX`/`TP_TEMP_ISSX`/`SW_TEMP_ISSX`·源码 105 行自造) ⇒ ★**更要命的是它断言【真盘】的分类计数**: 源码 172/177 行 `c_v2.get('DESIGNATOR_OK')==78 and c_v2.get('DESIGNATOR_MISSING')==3` ⇒ ★**改名后真盘的 OK/MISSING 计数必变 ⇒ 断言失败 ⇒ 判绿变判红 (★误判阻塞·★但红是真的★)** ★ · ★**另注**: 它的 `EXPECT_REAL` 常量 (源码 53 行) 是 78/3/9/23 四元组 ⇒ 同一类失效的第二处 ★ |

### ★§4.2 · 「布线面」基线要重锚的闸 (★读板面的 18 道 逐道: 基线钉在哪 / 那一趟后会不会变 / 变了对判据意味着什么★) ★

| # | 闸 | ★**基线钉在哪** ★ | ★**那一趟后会不会变** ★ | ★**变了对判据意味着什么** ★ |
|---|---|---|---|---|
| 1 | `check_debug_header_fw_impact.py` | 板 md5/mtime/size 三项 + 网表/脚表/BOM 三件 md5 (源码 549/564/571 行) | ★**会** ★ (板与三表在那一趟都动) | ★**判绿变判红 (误判阻塞)· 红是假的** ⇒ 须重锚 (重锚路径 = 脚本自带 baseline 回写, 源码 795 行) ★ |
| 2 | `check_debug_pin_order_contract.py` | `J_DEBUG`/`J_UART` 两个 ref 的 land / pad1 形状 (源码 141/241/293 行) + 板 md5 (源码 53 行) | ★**会** ★ (位号改 + 布线改 ⇒ land 动) | ★**判绿变判红 (误判阻塞)** ⇒ 须先重锚位号与 land 期望值 ★ |
| 3 | `check_demo_panel_spec.py` | `SW/SW_MD5_BASELINE_LEDGER.md` §1 的机器可读锚点块 (不在脚本里) | ★**会** ★ (台账链头 md5 必变) | ★**台账刷新即可 + `--skip-md5` 合法通道 ⇒ 不误判** ★ |
| 4 | `check_demo_panel_spec_r6_chainjudge_selftest.py` | 夹具自造的台账 + 链头 md5 唯一性 | ★**不会 (夹具自造)** ★ | ★**不受影响 (但覆盖失效·静默)** ★ |
| 5 | `check_demo_panel_spec_r6_selftest.py` | 夹具自造的板/网表/台账 + R6 硬保护件 md5 | ★**不会 (夹具自造)** ★ | ★**不受影响 (但覆盖失效·静默)** ★ |
| 6 | `check_fp_truth_read.py` | 板三项 (源码 87/88/89 行) + 三表 md5 + 链头 md5 短写形态 (源码 592 行) | ★**会** ★ | ★**判绿变判红 (误判阻塞)** ⇒ 须重锚 (重锚路径现成) ★ |
| 7 | `check_landing_trace_obligation.py` | 落表台账里的【链头 md5】+ `hard_protected[]` 两件 (源码 72/80/98 行) | ★**会** ★ | ★**判绿变判红 (顺序依赖·红是真的)** ⇒ 那一趟必须先落台账留痕, 这道闸才成立 ★ |
| 8 | `check_onepass_legb_sw_impact.py` | 板 + 网表 + 脚表 + BOM 四件 md5 (源码 70~73 行) | ★**会** ★ | ★**判绿变判红 (误判阻塞)** ⇒ 须重锚 ★ |
| 9 | `check_onepass_sw_sync.py` | 板 md5 锚 (源码 109 行) + 十个 `SW_SYNC_*` 环境变量键 + 十个真位号的探针输出正则 (源码 181~204 行) | ★**会** ★ | ★**判绿变判红 (md5 锚) + ★★静默跳过 (探针正则吃 `0 次`)★★** ⇒ 两类都要处理, 只处理前者不够 ★ |
| 10 | `check_sw_board_md5_rebase_readiness.py` | `NEEDLE_PREFIX='611b'+'869e'` (源码 47 行) + `CHANNEL_MIN=('reboard','prev_md5')` (88 行) | ★**会** ★ (它就是为这件事造的) | ★**自守闸告警器 (★红是设计意图★)** ⇒ 那一趟开工时它会先红, 必须由 main 重锚 + 落台账转绿 ★ |
| 11 | `check_sw_false_connectivity_gate.py` | 板三项 (源码 73/74/75 行) + 三表 md5 (77~79 行) + `logs/iss381/baseline_fingerprints.txt` (65 行) | ★**会** ★ | ★**判绿变判红 (误判阻塞)** ⇒ 须重锚 (ISS-381 基线指纹文件必须重出) ★ |
| 12 | `check_sw_fp_truth_impact.py` | SW 侧待办 need 里引着的过期 md5 清单 (源码 16/30 行·今日 27 条) | ★**会** ★ (过期项会变多) | ★**判绿变判红 (红是真的)** ⇒ 那一趟必须同批清, 否则它挡在那里 ★ |
| 13 | `check_sw_gate_chain_coverage.py` | `NEEDLE_PREFIX='611b'+'869e'` (源码 73 行) + 三表 md5 (79~81 行) ⇒ 扫的是【全仓 md5 引用面】 | ★**会** ★ | ★**自守闸告警器 (红是真的)** ⇒ ★**但它在链外 ⇒ 没人跑 ⇒ 静默风险** ★ |
| 14 | `check_sw_gate_health.py` | `NEEDLE_PREFIX` (61 行) + 三表 md5 (67~69 行) ⇒ 扫的是【全仓 md5 引用面】 | ★**会** ★ | ★**自守闸告警器 (红是真的)** ⇒ ★**但它在链外 ⇒ 没人跑 ⇒ 静默风险** ★ |
| 15 | `check_sw_mustchange_face_impact.py` | 板三项 (源码 79~81 行) + 三表 md5 (83~87 行) ⇒ T0 钉死 | ★**会** ★ | ★**自守闸告警器 (本闸自己的红是设计意图)** ⇒ 那一趟开工时必须同步重锚三个常量 ★ |
| 16 | `check_sw_ref_reachability.py` | `BASELINE_COUNT=3` + `BASELINE_TOKENS` 三条 (源码 131/134 行) + `DESIGNATOR_REGISTRY` 冻结表 (161 行) | ★**会** ★ (冻结表整张作废) | ★**判绿变判红 + 静默跳过 + 判红变判绿 三条全中** ⇒ ★**唯一有现成修法的一道 (`--freeze-registry`)★ ★ |
| 17 | `check_sw_ref_reachability_v2.py` | `BASELINE_COUNT=3` + `BASELINE_TOKENS` 三条 (源码 152/155 行) + 冻结表 + 探针失配自检 (511~529 行) | ★**会** ★ | ★**同 v1, 且多一层探针失配 ⇒ 更早暴露也更会误红** ★ |
| 18 | `check_sw_ref_reachability_v2_selftest.py` | 真盘分类计数断言 78/3 (源码 172/177 行) + `EXPECT_REAL` 78/3/9/23 (53 行) | ★**会** ★ | ★**判绿变判红 (红是真的)** ⇒ 须重锚计数期望 ★ |

★**布线面的一句话结论**: ★**18 道读板面的闸里, 没有一道能靠「板没变就没事」躲过去** ⇒ ★**要么它钉的是 md5 (重锚), 要么它钉的是形状/计数 (重出期望), 要么它是台账驱动的 (落台账), 要么它本来就该在那一趟红 (自守告警器) ⇒ ★**没有第五种「不用管」★** ★

---

## ★§5 · 表 (c) · 「那一趟之前必须先改 / 先重锚的闸」排序清单 ★

★**排序口径 (★按后果·main 题面给的口径★)**: ★**误判放行 > 误判阻塞 > 静默跳过** ★ ⇒ ★**第一档 = 会【放行】假结论的 (最危险)· 第二档 = 会【挡住真缺陷】的 · 第三档 = 会【在链上挡路】的 · 第四档 = 只在链外会红的 (没人跑)· 第五档 = 台账/文档面会漂的 (放行级结论挂在会漂的读数上)** ★

| 档 | 闸 | 后果 | ★**为什么排在这一档 (逐条依据)** ★ | 先改还是先重锚 |
|---|---|---|---|---|
| ★**① 误判放行 (最危险)** ★ | `check_sw_ref_reachability.py` (链上) | ★**闸照样绿, 但位号可达性已经不再被检查** ★ | ★**新位号前缀若落进 C10/C11/C13 豁免分支或是 ≥2 个 live 位号的严格前缀 (C12) ⇒ token 被判 `DOC_INTERNAL`/`NET_NAME` ⇒ 不进 `FAIL_CLASSES` ⇒ 静默跳过; 且 `BASELINE_TOKENS` 三条若被改名删掉 ⇒ `missing_total` 掉到 3 以下 ⇒ 闸转绿** ★ | ★**先改** (重建冻结表 `--freeze-registry`) ★
| ★**① 误判放行 (最危险)** ★ | `check_onepass_sw_sync.py` (链上) | ★**探针输出正则吃 `0 次` ⇒ 改名后探针 grep 不到位号, 输出 `0 次` 仍匹配 ⇒ 闸照样绿, 但它已经什么都没测** ★ | ★**判据正则 `\d+` 匹配 `0` (源码 190 行) ⇒ 静默跳过** ★ | ★**先改** (探针期望随改名同步) ★
| ★**① 误判放行** ★ | `check_sw_ref_reachability_v2.py` (链外) | ★**同 v1·多一层探针失配自检 ⇒ 改名后它会更早暴露, 但**只要没人跑它 (它没挂链) ⇒ 等于没有** ★ | ★**ISS-392 实测「v1 在链上 / v2 没挂」⇒ 两个版本都硬编 ⇒ 挂哪个都会失守** ★ | ★**先改** + ★**挂不挂链是 main 的地界** ★
| ★**② 误判阻塞** ★ | `check_sw_ref_reachability.py` (链上) | ★**冻结表整张作废 ⇒ 新增 `DESIGNATOR_MISSING` ⇒ 链上门禁直接红 ⇒ 挡住那一趟的每一次提交** ★ | ★**判红变判绿方向的反面: 今天绿→明天红 (红是假的)** ★ | ★**先改 (重建冻结表)** ★
| ★**② 误判阻塞** ★ | `check_debug_pin_order_contract.py` | ★**改名后 `J_DEBUG`/`J_UART` 在板上不存在 ⇒ 读不到 land ⇒ 闸红** ★ | ★**源码 141/241/293 行硬取这两个 ref** ★ | ★**先改** (期望值随改名同步) ★
| ★**② 误判阻塞** ★ | `check_evt_charge_current_criterion.py` | ★**网表里读不到 `U_CHG` ⇒ 充电电流判据失去输入 ⇒ 闸红** ★ | ★**源码 128/141/143 行** ★ | ★**先改** ★
| ★**② 误判阻塞** ★ | `check_load_switch_selection.py` | ★**网表里读不到 `U_PWR_SW` ⇒ 选型判据失去输入 ⇒ 闸红** ★ | ★**源码 156/173 行** ★ | ★**先改** ★
| ★**② 误判阻塞** ★ | `check_shutdown_semantics.py` | ★**R2 三页字面量比对失败 (条件性)** ★ | ★**源码 294~326 行·6 处硬编** ★ | ★**先改** (随真相页字段同步) ★
| ★**② 误判阻塞** ★ | `check_sw_ref_reachability_v2_selftest.py` | ★**断言真盘计数 78/3 ⇒ 改名后计数必变 ⇒ 夹具红** ★ | ★**源码 172/177 行 + `EXPECT_REAL` (53 行)** ★ | ★**先重锚** (计数期望) ★
| ★**③ 在链上挡路** ★ | `check_demo_panel_spec_r6_selftest.py` (链上) | ★**R6 硬保护件 md5 变 ⇒ 红** ★ | ★**夹具自造 ⇒ 真盘侧的对应闸是 `check_demo_panel_spec` (有 `--skip-md5` 合法通道)** ★ | ★**先重锚** ★
| ★**③ 在链上挡路** ★ | `check_landing_trace_obligation.py` (链上) | ★**台账里没有新 md5 的留痕 ⇒ 红** ★ | ★**源码 98/143 行** ★ | ★**先落台账** (不改判据) ★
| ★**③ 在链上挡路** ★ | `check_demo_panel_spec_r6_chainjudge_selftest.py` (链上) | ★**链头 md5 唯一性口径** ★ | ★**夹具自造** ★ | ★**先重锚** ★
| ★**③ 在链上挡路** ★ | `check_demo_panel_spec_r6_hardprot_iss315_selftest.py` (链上) | ★**只读台账 ⇒ 台账一改就漂** ★ | ★**doc_only** ★ | ★**先重锚** ★
| ★**④ 链外会红 (没人跑)** ★ | `check_sw_gate_chain_coverage.py` | ★**它就是【全仓 md5 引用面】的守门人 ⇒ 那一趟必然红, 但它在链外 ⇒ 没人跑 ⇒ 静默** ★ | ★**源码 73/79~81 行** ★ | ★**先重锚** ★
| ★**④ 链外会红 (没人跑)** ★ | `check_sw_gate_health.py` | ★**同上** ★ | ★**源码 61/67~69 行** ★ | ★**先重锚** ★
| ★**④ 链外会红 (没人跑)** ★ | `check_sw_board_md5_rebase_readiness.py` | ★**它是重锚守门人 ⇒ 那一趟它先红 ⇒ 它红了才知道要重锚 ⇒ 这是设计意图** ★ | ★**源码 47/88 行** ★ | ★**先重锚** ★
| ★**④ 链外会红 (没人跑)** ★ | `check_sw_false_connectivity_gate.py` | ★**零假连通基线全漂 ⇒ 闸红** ★ | ★**源码 65/73~79 行** ★ | ★**先重锚** ★
| ★**④ 链外会红 (没人跑)** ★ | `check_sw_fp_truth_impact.py` | ★**过期 md5 从 27 条变多 ⇒ 闸红 (红是真的)** ★ | ★**源码 16/30 行** ★ | ★**先重锚** ★
| ★**④ 链外会红 (没人跑)** ★ | `check_fp_truth_read.py` / `check_onepass_legb_sw_impact.py` / `check_debug_header_fw_impact.py` | ★**指纹三项 + 三表 md5 全漂 ⇒ 闸红** ★ | ★**源码 87~89 / 70~73 / 549~571 行** ★ | ★**先重锚** ★
| ★**⑤ 放行级结论挂在会漂的读数上** ★ | ★**10 道无真源依赖闸 (逐条见 §3 表 (a))** ★ | ★**真相页/台账一改 ⇒ 它们的读数就漂 ⇒ 亮度生物安全 / 目标兼容 / 放行级结论全在动** ★ | ★**§3 表 (a) 的「逐条判断依据」列逐条给了各自的漂移源** ★ | ★**先改 (把它们接到真源上)·★那是 main 的地界★ ★

★**表 (c) 的一句话结论**: ★**第一档 (误判放行) 只有 3 道闸, 但它们是【链上正在跑的那两道 + 一道没挂链的】⇒ ★**那一趟开工前必须先处理它们, 否则那一趟的「SW 侧绿灯」就是假的** ★★ ⇒ ★**「先改」还是「先重锚」是 main 的动作, 本单只把后果排出来** ★

---

## ★§6 · 机器块 (★本页的主本 = 下面的登记册★) ★

★**登记册的主本在本页机器块里 (人改得动·所以要能被抓)** ⇒ 新闸 `SW/tools/check_sw_mustchange_face_impact.py` 内嵌一份【建册日冻结快照】, 两条判据把它俩钉在一起: ★**T8 双绑** (页面单方面漂 ⇒ 红; 闸单方面漂 ⇒ 红; 两边一起漂 ⇒ 闸源码变了·可见) ★ ★**T1/T2/T5 的判据来源永远是【源码实读】, 不读登记册自己的数** ⇒ 登记册漂了 T1/T2/T5 会当场红 ★

★**机器块字段**: `registry` (逐闸登记) · `registry_sha256` (登记册摘要·自报值·与闸内冻结快照对拍) · `counts` (各类计数) · `decision_taken_here` = ★**`not_decided_here`** ★ (★「哪几道闸要改 / 怎么改 / 挂不挂链 / 顺序怎么排」全是 main 的地界★) ★

<!-- ISS411-MUSTCHANGE:BEGIN -->
```json
{
 "author": "sw-lead",
 "board_baseline": {
  "md5": "611b869e13518c3c023fb178f91a0075",
  "mtime": "2026-11-06 07:07:17.362193413",
  "size": 4940213
 },
 "combo_chain_hard_ref": [
  "SW/tools/check_onepass_sw_sync.py(20)",
  "SW/tools/check_sw_ref_reachability.py(55)"
 ],
 "counts": {
  "board_face_gate_count": 18,
  "chain_gate_count": 6,
  "combo_chain_hard_ref_count": 2,
  "doc_only_gate_count": 10,
  "gate_total_on_disk": 32,
  "gate_total_pre_existing": 31,
  "hard_ref_gate_count": 8,
  "pinned_baseline_gate_count": 12,
  "rename_face_affected_count": 18,
  "route_face_affected_count": 11
 },
 "date": "2026-11-25",
 "decision_taken_here": "not_decided_here",
 "gate": "SW/tools/check_sw_mustchange_face_impact.py",
 "issue": "ISS-411",
 "registry": {
  "SW/check_evt_charge_current_criterion.py": {
   "a": 1,
   "b": 2,
   "doc": "不受影响",
   "doc_only": false,
   "drift_src": "无",
   "faces": [
    "table",
    "doc"
   ],
   "hard_ref": true,
   "pin_board": false,
   "pin_table": false,
   "rename": "判绿变判红",
   "route": "不受影响",
   "truth_faces": [
    "table"
   ]
  },
  "SW/tools/check_brightness_biosafety.py": {
   "a": 0,
   "b": 0,
   "doc": "随真相页/台账改即漂",
   "doc_only": true,
   "drift_src": "真相页",
   "faces": [
    "doc"
   ],
   "hard_ref": false,
   "pin_board": false,
   "pin_table": false,
   "rename": "不受影响",
   "route": "不受影响",
   "truth_faces": []
  },
  "SW/tools/check_debug_header_fw_impact.py": {
   "a": 0,
   "b": 0,
   "doc": "不受影响",
   "doc_only": false,
   "drift_src": "无",
   "faces": [
    "board",
    "table",
    "bom",
    "doc"
   ],
   "hard_ref": false,
   "pin_board": true,
   "pin_table": false,
   "rename": "基线漂移-须重锚",
   "route": "基线漂移-须重锚",
   "truth_faces": [
    "board",
    "bom",
    "table"
   ]
  },
  "SW/tools/check_debug_pin_order_contract.py": {
   "a": 2,
   "b": 2,
   "doc": "不受影响",
   "doc_only": false,
   "drift_src": "无",
   "faces": [
    "board",
    "table",
    "doc"
   ],
   "hard_ref": true,
   "pin_board": true,
   "pin_table": false,
   "rename": "判绿变判红",
   "route": "基线漂移-须重锚",
   "truth_faces": [
    "board",
    "table"
   ]
  },
  "SW/tools/check_demo_panel_spec.py": {
   "a": 0,
   "b": 0,
   "doc": "不受影响",
   "doc_only": false,
   "drift_src": "无",
   "faces": [
    "board",
    "table",
    "doc",
    "ledger",
    "firm"
   ],
   "hard_ref": false,
   "pin_board": false,
   "pin_table": false,
   "rename": "有合法改板通道",
   "route": "有合法改板通道",
   "truth_faces": [
    "board",
    "firm",
    "table"
   ]
  },
  "SW/tools/check_demo_panel_spec_r6_chainjudge_selftest.py": {
   "a": 0,
   "b": 0,
   "doc": "不受影响",
   "doc_only": false,
   "drift_src": "无",
   "faces": [
    "board",
    "table",
    "doc",
    "ledger"
   ],
   "hard_ref": false,
   "pin_board": false,
   "pin_table": false,
   "rename": "不受影响",
   "route": "不受影响",
   "truth_faces": [
    "board",
    "table"
   ]
  },
  "SW/tools/check_demo_panel_spec_r6_hardprot_iss315_selftest.py": {
   "a": 0,
   "b": 0,
   "doc": "随真相页/台账改即漂",
   "doc_only": true,
   "drift_src": "台账",
   "faces": [
    "ledger"
   ],
   "hard_ref": false,
   "pin_board": false,
   "pin_table": false,
   "rename": "不受影响",
   "route": "不受影响",
   "truth_faces": []
  },
  "SW/tools/check_demo_panel_spec_r6_selftest.py": {
   "a": 0,
   "b": 0,
   "doc": "不受影响",
   "doc_only": false,
   "drift_src": "无",
   "faces": [
    "board",
    "table",
    "doc",
    "ledger"
   ],
   "hard_ref": false,
   "pin_board": false,
   "pin_table": false,
   "rename": "不受影响",
   "route": "不受影响",
   "truth_faces": [
    "board",
    "table"
   ]
  },
  "SW/tools/check_fp_truth_read.py": {
   "a": 0,
   "b": 0,
   "doc": "不受影响",
   "doc_only": false,
   "drift_src": "无",
   "faces": [
    "board",
    "table",
    "bom",
    "doc",
    "ledger"
   ],
   "hard_ref": false,
   "pin_board": true,
   "pin_table": true,
   "rename": "基线漂移-须重锚",
   "route": "基线漂移-须重锚",
   "truth_faces": [
    "board",
    "bom",
    "table"
   ]
  },
  "SW/tools/check_iss250_rknn_target_gate.py": {
   "a": 0,
   "b": 0,
   "doc": "随真相页/台账改即漂",
   "doc_only": true,
   "drift_src": "真相页",
   "faces": [
    "doc"
   ],
   "hard_ref": false,
   "pin_board": false,
   "pin_table": false,
   "rename": "不受影响",
   "route": "不受影响",
   "truth_faces": []
  },
  "SW/tools/check_iss355_convert_route.py": {
   "a": 0,
   "b": 0,
   "doc": "随真相页/台账改即漂",
   "doc_only": true,
   "drift_src": "真相页+台账",
   "faces": [
    "doc",
    "ledger"
   ],
   "hard_ref": false,
   "pin_board": false,
   "pin_table": false,
   "rename": "不受影响",
   "route": "不受影响",
   "truth_faces": []
  },
  "SW/tools/check_landing_trace_obligation.py": {
   "a": 0,
   "b": 0,
   "doc": "不受影响",
   "doc_only": false,
   "drift_src": "无",
   "faces": [
    "board",
    "table",
    "bom",
    "ledger"
   ],
   "hard_ref": false,
   "pin_board": false,
   "pin_table": true,
   "rename": "基线漂移-须重锚",
   "route": "不受影响",
   "truth_faces": [
    "board",
    "bom",
    "table"
   ]
  },
  "SW/tools/check_load_switch_selection.py": {
   "a": 1,
   "b": 1,
   "doc": "不受影响",
   "doc_only": false,
   "drift_src": "无",
   "faces": [
    "table",
    "doc"
   ],
   "hard_ref": true,
   "pin_board": false,
   "pin_table": false,
   "rename": "判绿变判红",
   "route": "不受影响",
   "truth_faces": [
    "table"
   ]
  },
  "SW/tools/check_onepass_legb_sw_impact.py": {
   "a": 0,
   "b": 0,
   "doc": "不受影响",
   "doc_only": false,
   "drift_src": "无",
   "faces": [
    "board",
    "table",
    "bom",
    "doc",
    "ledger"
   ],
   "hard_ref": false,
   "pin_board": true,
   "pin_table": true,
   "rename": "基线漂移-须重锚",
   "route": "基线漂移-须重锚",
   "truth_faces": [
    "board",
    "bom",
    "table"
   ]
  },
  "SW/tools/check_onepass_sw_release.py": {
   "a": 0,
   "b": 0,
   "doc": "随真相页/台账改即漂",
   "doc_only": true,
   "drift_src": "真相页+台账",
   "faces": [
    "doc",
    "ledger"
   ],
   "hard_ref": false,
   "pin_board": false,
   "pin_table": false,
   "rename": "不受影响",
   "route": "不受影响",
   "truth_faces": []
  },
  "SW/tools/check_onepass_sw_sync.py": {
   "a": 20,
   "b": 20,
   "doc": "随真相页/台账改即漂",
   "doc_only": false,
   "drift_src": "无",
   "faces": [
    "board",
    "table",
    "bom",
    "doc",
    "ledger"
   ],
   "hard_ref": true,
   "pin_board": true,
   "pin_table": false,
   "rename": "判绿变判红",
   "route": "有合法改板通道",
   "truth_faces": [
    "board",
    "bom",
    "table"
   ]
  },
  "SW/tools/check_rk3572_target_caliber.py": {
   "a": 0,
   "b": 0,
   "doc": "随真相页/台账改即漂",
   "doc_only": true,
   "drift_src": "真相页+台账",
   "faces": [
    "doc",
    "ledger"
   ],
   "hard_ref": false,
   "pin_board": false,
   "pin_table": false,
   "rename": "不受影响",
   "route": "不受影响",
   "truth_faces": []
  },
  "SW/tools/check_rk3572_vccio_domain.py": {
   "a": 0,
   "b": 0,
   "doc": "不受影响",
   "doc_only": false,
   "drift_src": "无",
   "faces": [
    "table",
    "doc"
   ],
   "hard_ref": false,
   "pin_board": false,
   "pin_table": false,
   "rename": "不受影响",
   "route": "不受影响",
   "truth_faces": [
    "table"
   ]
  },
  "SW/tools/check_rknn_target_compat.py": {
   "a": 0,
   "b": 0,
   "doc": "不受影响",
   "doc_only": true,
   "drift_src": "工具链产物",
   "faces": [],
   "hard_ref": false,
   "pin_board": false,
   "pin_table": false,
   "rename": "不受影响",
   "route": "不受影响",
   "truth_faces": []
  },
  "SW/tools/check_shutdown_semantics.py": {
   "a": 6,
   "b": 7,
   "doc": "随真相页/台账改即漂",
   "doc_only": false,
   "drift_src": "无",
   "faces": [
    "table",
    "doc"
   ],
   "hard_ref": true,
   "pin_board": false,
   "pin_table": false,
   "rename": "条件性-随真相页字段",
   "route": "不受影响",
   "truth_faces": [
    "table"
   ]
  },
  "SW/tools/check_sw09_patch_dryrun.py": {
   "a": 0,
   "b": 0,
   "doc": "随真相页/台账改即漂",
   "doc_only": true,
   "drift_src": "真相页+台账",
   "faces": [
    "doc",
    "ledger"
   ],
   "hard_ref": false,
   "pin_board": false,
   "pin_table": false,
   "rename": "不受影响",
   "route": "不受影响",
   "truth_faces": []
  },
  "SW/tools/check_sw_board_md5_rebase_readiness.py": {
   "a": 0,
   "b": 0,
   "doc": "不受影响",
   "doc_only": false,
   "drift_src": "无",
   "faces": [
    "board",
    "doc"
   ],
   "hard_ref": false,
   "pin_board": true,
   "pin_table": false,
   "rename": "基线漂移-须重锚",
   "route": "基线漂移-自守闸告警器",
   "truth_faces": [
    "board"
   ]
  },
  "SW/tools/check_sw_false_connectivity_gate.py": {
   "a": 0,
   "b": 0,
   "doc": "不受影响",
   "doc_only": false,
   "drift_src": "无",
   "faces": [
    "board",
    "table",
    "bom",
    "doc"
   ],
   "hard_ref": false,
   "pin_board": true,
   "pin_table": true,
   "rename": "基线漂移-须重锚",
   "route": "基线漂移-须重锚",
   "truth_faces": [
    "board",
    "bom",
    "table"
   ]
  },
  "SW/tools/check_sw_fp_truth_impact.py": {
   "a": 0,
   "b": 0,
   "doc": "不受影响",
   "doc_only": false,
   "drift_src": "无",
   "faces": [
    "board",
    "table",
    "bom",
    "doc",
    "ledger"
   ],
   "hard_ref": false,
   "pin_board": false,
   "pin_table": true,
   "rename": "基线漂移-须重锚",
   "route": "不受影响",
   "truth_faces": [
    "board",
    "bom",
    "table"
   ]
  },
  "SW/tools/check_sw_gate_chain_coverage.py": {
   "a": 0,
   "b": 0,
   "doc": "不受影响",
   "doc_only": false,
   "drift_src": "无",
   "faces": [
    "board",
    "table",
    "bom",
    "doc"
   ],
   "hard_ref": false,
   "pin_board": true,
   "pin_table": true,
   "rename": "基线漂移-须重锚",
   "route": "基线漂移-须重锚",
   "truth_faces": [
    "board",
    "bom",
    "table"
   ]
  },
  "SW/tools/check_sw_gate_health.py": {
   "a": 0,
   "b": 0,
   "doc": "不受影响",
   "doc_only": false,
   "drift_src": "无",
   "faces": [
    "board",
    "table",
    "bom",
    "doc"
   ],
   "hard_ref": false,
   "pin_board": true,
   "pin_table": true,
   "rename": "基线漂移-须重锚",
   "route": "基线漂移-须重锚",
   "truth_faces": [
    "board",
    "bom",
    "table"
   ]
  },
  "SW/tools/check_sw_mustchange_face_impact.py": {
   "a": 0,
   "b": 0,
   "doc": "随真相页/台账改即漂",
   "doc_only": false,
   "drift_src": "无",
   "faces": [
    "board",
    "table",
    "bom",
    "doc",
    "ledger",
    "firm"
   ],
   "hard_ref": false,
   "pin_board": true,
   "pin_table": true,
   "rename": "不受影响",
   "route": "基线漂移-自守闸告警器"
  },
  "SW/tools/check_sw_ref_reachability.py": {
   "a": 55,
   "b": 78,
   "doc": "不受影响",
   "doc_only": false,
   "drift_src": "无",
   "faces": [
    "board",
    "table",
    "bom",
    "doc"
   ],
   "hard_ref": true,
   "pin_board": false,
   "pin_table": false,
   "rename": "判绿变判红",
   "route": "不受影响",
   "truth_faces": [
    "board",
    "bom",
    "table"
   ]
  },
  "SW/tools/check_sw_ref_reachability_v2.py": {
   "a": 58,
   "b": 85,
   "doc": "不受影响",
   "doc_only": false,
   "drift_src": "无",
   "faces": [
    "board",
    "table",
    "bom",
    "doc"
   ],
   "hard_ref": true,
   "pin_board": false,
   "pin_table": false,
   "rename": "判绿变判红",
   "route": "不受影响",
   "truth_faces": [
    "board",
    "bom",
    "table"
   ]
  },
  "SW/tools/check_sw_ref_reachability_v2_selftest.py": {
   "a": 8,
   "b": 10,
   "doc": "不受影响",
   "doc_only": false,
   "drift_src": "无",
   "faces": [
    "board",
    "doc"
   ],
   "hard_ref": true,
   "pin_board": false,
   "pin_table": false,
   "rename": "判绿变判红",
   "route": "不受影响",
   "truth_faces": [
    "board"
   ]
  },
  "SW/tools/check_sw_zero_copper_grade_consistency.py": {
   "a": 0,
   "b": 0,
   "doc": "随真相页/台账改即漂",
   "doc_only": true,
   "drift_src": "真相页",
   "faces": [
    "doc"
   ],
   "hard_ref": false,
   "pin_board": false,
   "pin_table": false,
   "rename": "不受影响",
   "route": "不受影响",
   "truth_faces": []
  },
  "SW/tools/check_timing_review_adc_sync.py": {
   "a": 0,
   "b": 0,
   "doc": "随真相页/台账改即漂",
   "doc_only": true,
   "drift_src": "真相页",
   "faces": [
    "doc"
   ],
   "hard_ref": false,
   "pin_board": false,
   "pin_table": false,
   "rename": "不受影响",
   "route": "不受影响",
   "truth_faces": []
  }
 },
 "registry_sha256": "5084c0115ff62aa7e7c8e706007706a35e1bf0116f50106744b891e65a176d32",
 "table_baseline_md5": {
  "HW/BOM_v1.csv": "5b9993992405904a60ac96a020b375d8",
  "HW/netlist_v1.csv": "6aee500e60ba0732f83a9cf557ba90ab",
  "HW/netlist_v1_pins.csv": "9174309df1ec9411ac8e8d9e80ee386a"
 },
 "title": "板那一趟 SW 侧必改面 (位号改名 + 布线 45→0) → 闸的判据失效 影响面清账"
}
```
<!-- ISS411-MUSTCHANGE:END -->

---

## ★§7 · 边界自证 + 未完成项 + 留给 main 的问句 ★

### ★§7.1 · 边界 (★每一项都有本机实跑读数·写在交卷页 §B6★) ★

| ★边界★ | ★自证方式 ★ |
|---|---|
| ★**零写板** ★ | `md5sum` + `stat` 三项与开工前逐字相同 ★ |
| ★**零落表** ★ | 网表 / 脚表 / BOM 三件 md5 与开工前逐字相同 ★ |
| ★**零改既有闸判据** ★ | ★**31 道既有 SW 闸逐个 md5 与开工前逐字相同 (★含题面点名的 5 道★)** ★ |
| ★**零改既有页正文** ★ | ★**引用到的既有 SW 页 md5 对拍** ★ |
| ★**零挂链** ★ | `grep -c check_sw_mustchange_face_impact state/gate_check.py` = 0 ★ |
| ★**零外发** ★ | ★**`state/outbox/` 全树逐文件 md5 未动** ★ |
| ★**不代拍** ★ | ★**机器块 `decision_taken_here` = `not_decided_here`** ★ |
| ★**不自签** ★ | ★**`state/issue_log.yaml` 未写** ★ |
| ★**只写本单允许的文件** ★ | ★**新建 3 个 · 改 1 个 (`state/fragments/sw.yaml`·走 `state/frag_write.py`) · 留证 (`logs/iss411/` + `tmp/iss411/`)★ ★ |

### ★§7.2 · 本单【没做】的 (★不藏★) ★

★**① 「哪几道闸要改 / 改成什么 / 挂不挂链 / 先改还是先重锚」本单【一条都没拍】** ⇒ 全部交 main (★表 (c) 只排后果, 不排决定★) ★
★**② B-1~B-8 的逐条改名清单本单【没有拿到】** ⇒ ★**表 (b) 里 `check_rk3572_vccio_domain.py` 的「不受影响」结论标 [推算]·前提是改名清单不碰 VCIO 域位号 ⇒ 这是本单唯一一条依赖外部清单的结论** ★
★**③ 那一趟的【具体布线拓扑】本单没有** ⇒ 「布线 45→0」对每道闸的影响只能判到【基线会不会漂】这一层, 判不到【漂成什么样】★
★**④ 三表 (脚表/网表/BOM) 的【逐行改名影响】本单没有逐行清** ⇒ 结论只到「谁钉了三表 md5」这一层 ★
★**⑤ 本单【零外发】⇒ 没有查外部资料** ⇒ §B3 的 [官网]/[媒体] 两级本单零条 ★

### ★§7.3 · 留给 main 的问句 (★一条都不代拍★) ★

| # | 问句 | 为什么要 main 答 |
|---|---|---|
| Q1 | ★**「先改」还是「先重锚」, 哪几道闸走哪条路? ★** | ★**表 (c) 只排了后果, 顺序与动作是 main 的地界 (★`decision_taken_here=not_decided_here`★)** ★ |
| Q2 | ★**`check_sw_ref_reachability_v2.py` 挂不挂链? (★它硬编 58 处, 比在链上的 v1 还多 3 处·但它多一层探针失配自检★)** | ★**ISS-392 已签收「v1 在链上 / v2 没挂」⇒ 本单实测【挂哪个都会失守】⇒ 挂链是 main 的动作, 本单不碰 `state/gate_check.py` 一个字节★** ★ |
| Q3 | ★**`check_onepass_sw_sync.py` 的探针期望 (`D_CHG_LED \d+ 次`) 要不要改成【位号非 0 才算通过】? ★** | ★**现状 `\d+` 吃 `0` ⇒ 改名后闸照样绿却什么都没测 ⇒ ★**这是「静默跳过」那一档, 改法有两种 (改期望 / 改闸), 本单不代拍★** ★ |
| Q4 | ★**B-1~B-8 的逐条改名清单能给吗? ★** | ★**表 (a) 里 `check_rk3572_vccio_domain.py` 的「不受影响」是 [推算] ⇒ 拿到清单才能升级成 [实测]★** ★ |
| Q5 | ★**那 10 道无真源依赖闸, 要不要在那一趟里接真源? (★还是继续让它们漂?★)** | ★**它们判的是放行级结论 ⇒ 「漂」比「红」更危险 ⇒ 但改法是改既有闸判据 ⇒ main 的地界★** ★

---

★**本页到此为止 · 机器块在上面 · 本单零写板 · 零落表 · 零改既有闸判据 · 零改既有页正文 · 零挂链 · 零外发 · 不代拍 · 不自签** ★
