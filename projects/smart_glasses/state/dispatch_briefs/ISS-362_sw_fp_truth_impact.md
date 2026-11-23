# ISS-362 · sw-lead · 「板那一趟」的 SW 侧闸链在【S10 封装真值落表】那一跳会怎么变

★**题**: ★**「板只改一次」那一趟 (S1~S13) 会【合法地】把三份真源的 md5 一起换掉 (网表 / 脚表 / BOM) ⇒ SW 侧有 7 道闸 + 1 道准出汇总闸 + 8 条板侧输入清单全部盯着这些真源 ⇒ 但【S10 换封装真值】这一跳与【S1 改名】那一跳【换的东西根本不是一类】⇒ 而 SW 侧现在【没有任何一份文件】说明这一跳会发生什么** ★
★★**⇒ 本单 = 把「S10 换封装」这一跳对 SW 侧的全部影响, 做成【一页 + 一道沙盒预演闸】, 让那一趟当天 SW 侧【红的每一条都能被解释】· 而不是【现场抓瞎】** ★

★**本单只做 1 件 (★不许扩项·零写板·零落表·零外发·不代拍★)**: ★**纯分析 + 沙盒预演 + 新建一条只读闸** ★

---

## ★★一 · main 的本机实读 (★不抄任何 agent 报告·数字全部可复跑★) ★★

★**★先说清【这一跳是什么】 (★ISS-356 交卷页自己写的·★逐字★)**:

> ★**「本单不落表: 真值要落到原理图 `Footprint` 属性 / BOM `footprint` 栏 / 板生成器, 那是『板那一趟』的活」** ★

★⇒ ★**那 78 件 (镜脚主PCB) + 22 件 (镜框充电板) 的 `footprint` 栏会从 `待定` / `★板文件封装: …` 变成【真库封装名】⇒ 三份真源同时变** ★
★⇒ ★**main 实测 (★2026-11-23 13:5x 本机跑★)**: ★**三份真源的 `footprint` 栏都存在** ⇒ `HW/netlist_v1.csv` (★第 14 栏★) · `HW/netlist_v1_pins.csv` (★第 12 栏★) · `HW/BOM_v1.csv` (★第 10 栏★) ⇒ ★**这一跳必然换 3 个 md5** ★

★**★SW 侧现在盯住这些真源的闸 (★main 实跑·逐道 rc 已验★)**:

| # | 闸 | 它盯什么 | ★现状实跑 rc★ |
|---|---|---|---|
| 1 | `SW/tools/check_onepass_sw_sync.py` | ★**板侧输入清单 8 条 (SW01~SW08)· 9 字段 · 归属步 S1~S13 · 现状值 == 盘面实测 (W5) · 受保护 5 件台账对账 (W6)** ★ | ★**0** ★ |
| 2 | `SW/tools/check_sw_ref_reachability.py` | 位号引用可达性 | ★**0** ★ |
| 3 | `SW/tools/check_landing_trace_obligation.py` | ★**受管真源三件 (网表 / 脚表 / BOM) 的落表留痕义务** ★ | ★**0** ★ |
| 4 | `SW/tools/check_demo_panel_spec.py` | ★**R6 三方对账 (盘上 md5 ↔ 落表台账链头) + 硬保护两件的合法改板通道** ★ | ★**0** ★ |
| 5 | `SW/tools/check_demo_panel_spec_r6_selftest.py` | R6 判决源反向用例 | ★**0** ★ |
| 6 | `SW/tools/check_demo_panel_spec_r6_chainjudge_selftest.py` | R6 链头交叉核对反向用例 | ★**0** ★ |
| 7 | `SW/tools/check_demo_panel_spec_r6_hardprot_iss315_selftest.py` | R6 硬保护路径反向用例 | ★**0** ★ |
| 8 | `SW/tools/check_shutdown_semantics.py` | 关机语义 | ★**0** ★ |
| 9 | `SW/tools/check_timing_review_adc_sync.py` | 时序评审 ADC 同步 | ★**0** ★ |
| 10 | `SW/tools/timing_check.py` | 上电 / 复位时序预算 | ★**0** ★ |
| ★**汇总** ★ | ★`SW/tools/check_onepass_sw_release.py` ★ | ★**10 道聚合 · fail-closed · 脚本不存在/跑不起来/超时 ⇒ 一律算闸红** ★ | ★**0** (★`--selftest` 末行「✅ 一致 (反向用例全抓到)」★) ★ |

★**★main 实测到的三条关键事实 (★这就是本单存在的理由★)**:

★**① 「S1 改名」那一跳, SW 侧已经做过完整体检 (★ISS-321 / ISS-323 / ISS-327 三单·全部 verified★) ⇒ ★**但那三单从头到尾【一个字都没提 `footprint`】** ★
- ★`SW/ONETRIP_SW_SAMEBATCH_RENAME_LIST.md` (★74,942 B·11-18 16:17★) 全文 `footprint` 命中 = ★**1** ★ ⇒ ★**它讲的是【位号字面量】不是【封装栏】★**
- ★`HANDOFF/2026-11-18_sw-lead_ISS323_SW侧同批改动可执行清单.md` 全文 `footprint` 命中 = ★**1** ★ ⇒ 同上
- ★`SW/tools/check_onepass_sw_sync.py` 全文 `footprint` 命中 = ★**0** ★ ⇒ ★**SW 侧现在【没有任何一道闸读 `footprint` 栏】** ★

★**② 「S10 换封装」这一跳, 在整个 SW 侧【没有任何一份文件】登记过** ★
- ★`SW/BOARD_ONEPASS_SW_SYNC.md` 的 8 条清单 (★SW01~SW08·★归属步 S2/S4/S8/S9/S10★) ⇒ ★**没有一条是关于 `footprint` 栏的** ★
- ★8 条里 6 条的 `current_state` 里【嵌着会改名的位号】 (★`SW_BOOT` / `SW_KEY_PWR` / `SW_KEY_VM` / `SW_KEY_VP` / `SW_RST` / `D_CHG_LED` / `D_LED_G` / `D_LED_R` / `TP_INT` / `C_VBUS_GND` / `D_ESD_USB_D`★) ⇒ ★**这是 ISS-323 第 3 件要处理的那批 (★三条现状探针改成「从网表实读」★)★** ⇒ ★**也就是说 S1 那条线 SW 侧【有准备】· 而 S10 这条线【连登记都没有】** ★

★**③ SW 侧的落表台账锚点【已经落后 6 跳】, 而 8 条待办 need 里引的 md5 【全部是陈旧值】 ★
- ★main 实测 `SW/SW_MD5_BASELINE_LEDGER.md` 的 `source_ledger.entries[]` 只有 ★**2 条** (★`HW/netlist_v1.csv` by ISS-257 · `HW/netlist_v1_pins.csv` by ISS-257★) ⇒ ★**登记值 `e06c1dd6…` / `287e7861…` ⇒ 盘上现值是 `6aee500e…` / `9174309d…` (★已差 6 跳·ISS-302 落的★)** ★
- ★main 实跑 `sw_ledger_state()` 对【判决源台账】(★`HW/SCHEMATIC_LANDING_V1_LANDED.md`★) ⇒ ★**三件的链头都对** (★网表 `6aee500e…` by ISS-302 · 脚表 `9174309d…` by ISS-302 · BOM `5b999399…` by ISS-302★) ⇒ ★**闸的判决源是【台账链头】不是【域侧锚点副本】⇒ 这就是它今天 rc=0 的原因·是设计·不是侥幸** ★
- ★**但台账里那 8 条 to=sw-lead 的待办 need (★`iss233_sw_md5_reanchor` / `iss236_h1_reanchor` / `iss239_h1_reanchor_sw` / `iss249_h1_reanchor_netlist_md5_sw` / `iss257_h1_reanchor_to_sw_lead` / `iss260_h1_reanchor_after_v2_land` / `iss236_h1_reanchor_v2` / `iss283_sw_anchor_reanchor_after_landing`★) 里引的 32 位 md5, ★**main 实测: 逐个跟盘上现值 + 台账链头比对 ⇒ 【一条都不等】⇒ 全部是陈旧值** ★** ⇒ 而它们各自的触发单 (ISS-233 / 236 / 249 / 257 / 260 / 283) ★**已经全部 verified** ⇒ 这 8 条 need 是【已过期但还挂在未闭合队列里】的 ⇒ ★**它们正在虚增 SW 侧的未闭合需求数, 且若被误当成「待执行的重锚指令」照抄 md5 ⇒ 会把锚点写到错误的值上** ★

★**★这一单为什么值得存在 (★一句话★)**: ★**「板只改一次」那一趟当天, SW 侧会因为【S1 改名】和【S10 换封装】两次合法地换掉三份真源 md5 ⇒ 而 SW 侧对 S1 有准备 (ISS-321/323/327 三单) · 对 S10 【零准备】⇒ 且现在 SW 侧还挂着 8 条引着【过期 md5】的重锚 need ⇒ ★**那一趟当天若 S10 这一跳红了, SW 侧【没有任何一份文件】能解释「这是预期的」还是「这是坏了」⇒ ⇒ 最坏的结果是有人为了「让闸变绿」去改真源/改锚点/放宽判据 ⇒ 违反 ISS-273/275/284 三单花大力气堵掉的「悄悄换真源」漏洞** ★**

---

## ★★二 · 本单交付物 (★3 件·不许扩项★) ★★

### ★★① 交卷物 (3 件) · 第 1 件 · 一页: ★**新建** `SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md` ★★

★**必须包含 (★逐条·不许少★)**:
- ★**§0 口径与读数** ★: ★**S1 与 S10 两跳的对照表** ★ (★改什么 · 换哪几个 md5 · SW 侧哪几道闸会跟着动 · SW 侧现有什么准备 · ★**S1 有 / S10 无**★) ⇒ ★**页里每个数字都要能被下面 §4 的命令复现·不许抄 main 的转述** ★
- ★**§1 S10 这一跳的 SW 侧影响面 (逐闸)** ★: ★**10 道闸逐道写** ⇒ ★**「会不会红」·「红了是谁的锅」·「红了怎么判它是预期还是坏了」·「今天有没有准备」** ★ ⇒ ★**凡写「会红」的, 必须给出可复跑的命令 + 期望输出** ★ ⇒ ★**凡写「不会红」的, 必须给出【为什么不会红】的机制依据 (★例: `check_landing_trace_obligation` 走台账链头 ⇒ 合法落表自动前移⇒ 不红·依据是 ISS-275 换源那套机制★)** ★
- ★**§2 那 8 条待办 need 的清理口径 (★只给方案·不改 need·不改锚点★)** ★: ★**逐条写清它引的 md5 是第几跳的值 / 现在的链头是哪一跳 / 它该退休还是该改写** ⇒ ★**★不许直接改 `state/fragments/sw.yaml` 的 need 条目★** (★那是「改未闭合数」⇒ 要么 main 裁·要么你自己走 frag_write 改 answer·★本单只出【建议表】+【判据】**) ★ ⇒ ★**★另**: 你可以在【自己的分片】里登记一条 answer 把它们闭合 (★走 `state/frag_write.py`★) ⇒ ★**但 answer 的 value 必须写清「依据 = 哪一跳的链头 + 实测 md5」·不许写「已处理」三个字** ★
- ★**§3 S10 这一跳的【当天 SOP】(★给那一趟当班的人照着念★)** ★: ★**逐条: 当天先跑什么 ⇒ 红了先看哪一条 ⇒ 什么情况可以判「预期」⇒ 什么情况必须停 ⇒ 什么情况绝对不许做 (★改锚点 md5 / 改判据阈值 / 改盘上真源 / 回退落表★)** ★ ⇒ ★**★「绝对不许做」那几条必须逐字照抄 ISS-275 §R-10 + ISS-284 的红线表述·不许自己改写★** ★
- ★**§4 复现命令清单 (★全部真实存在·main 本机实测过·见 §四★)** ★

### ★★② 交卷物 (3 件) · 第 2 件 · 一条沙盒预演闸: ★**新建** `SW/tools/check_sw_fp_truth_impact.py` ★★

★**判据 (★**只读 + 沙盒预演·真件一个字节不许动**★)**:
- ★**H0** ★**基线闸全绿** ★: ★**10 道 SW 闸逐道跑 ⇒ 全绿 ⇒ 才算基线成立** (★脚本不存在 / 跑不起来 / 超时 ⇒ 一律算红·fail-closed★) ★
- ★**H1** ★**「SW 侧读 footprint 栏」这件事被登记了** ★: ★**脚本自己扫 `SW/tools/*.py` + `SW/*.md` ⇒ 统计有多少处读 `footprint` 栏 ⇒ ★**当前实测 = 0 处 ⇒ 判红 + 点名「S10 这一跳在 SW 侧是盲区」** ⇒ ★**这一条【今天必然红】· 你交卷时它变成绿的条件是: 你在页里【明确登记了这个盲区 + 对应影响 + 对策】⇒ 闸判「已登记」即绿·不许用「扫到 0 处所以没问题」凑绿** ★ (★★照抄 ISS-309 铁律: 不许把闸修成永远红·但也不许把红灯调没★★) ★
- ★**H2** ★**台账链头与盘上现值一致 (三件全查)** ★: ★**用 `sw_ledger_state()` 自己算 (★照抄 `SW/tools/check_demo_panel_spec.py` 的现成 helper·**不许自己另写一套**★) ⇒ 网表 / 脚表 / BOM 三件的链头 == 盘上现值 ⇒ **一条不许红** ★ ⇒ ★**★这一条是「S10 会红但不算坏」的机制依据·必须能被机器证明★** ★
- ★**H3** ★**SW 侧待办 need 里没有引着过期 md5 的** ★: ★**脚本自己读 `STATE.yaml` 的 `needs_matrix.pending` 里 to=sw-lead 的条目 ⇒ 抠出 32 位 md5 ⇒ 逐个跟【盘上现值 + 台账链头】比对 ⇒ ★**命中任何一条不在 {盘上现值 ∪ 台账链头} 的 ⇒ 判红 + 点名 need key + 点名那个 md5** ★ ⇒ ★**★今天这条必然红 (实测 8 条 need 里的 md5 全是陈旧值) ⇒ 交卷时它变绿的条件是: 你在 §2 里逐条给出退休/改写口径·并在页里登记★** ★
- ★**H4** ★**8 条板侧输入清单没有「S10 换封装」这一条** ★: ★**脚本自己读 `SW/BOARD_ONEPASS_SW_SYNC.md` 的 JSON 块 ⇒ 判 8 条里有没有一条 `current_state` 或 `action` 提到 `footprint` / 封装 ⇒ **当前 = 没有 ⇒ 判红 + 点名** ★ ⇒ ★**交卷时它变绿的条件是: 页里 §1/§3 明确登记了「S10 这一跳 SW 侧无清单条目」这个事实 + 它对该跳的影响 + 对策** ★ (★★**本单【不许】直接往 `SW/BOARD_ONEPASS_SW_SYNC.md` 加第 9 条 ⇒ 那是「改那一趟的清单」⇒ 归 main 裁★** ★)
- ★**H5** ★**SOP 三件套齐全** ★: ★**§1 逐闸影响表 / §3 当天 SOP / §2 need 清理口径 ⇒ 三块都在页里且非空 ⇒ 不齐即红** ★
- ★**H6** ★**禁语检查** ★: ★**页里不许出现「等原厂回信 / 等供应商确认 / 待外部回复 / 等确认」** ★ (★老板 2026-11-12 02:02 政策★) ★
- ★**H7** ★**证据等级五级白名单** ★: ★**`[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]`·写 `[官方]` = 红** ★

★**★★这一条闸的设计纪律 (★照抄 ISS-335 的准出汇总闸·★它已经做对了★)**: ★**H1 / H3 / H4 三条【今天必然红】⇒ 它们【不是坏消息】⇒ 它们是【本单登记下来的缺口清单】⇒ 交卷时它们变绿的方式是【页里把缺口登记清楚了】·不是【把缺口删掉】** ★ ⇒ ★**★绝对不许把 H1/H3/H4 改成「扫到 0 处就当没问题」那种同义改写★** ★

★**`--selftest` 反向用例 ≥6 条, 每条自证「红的是目标那一条, 其余仍绿」**: ★**① 页里删掉 §3 ⇒ H5 红 · ② 页里塞「等原厂回信」⇒ H6 红 · ③ 篡改 §1 的某个闸读数 ⇒ H1 红 · ④ 在页里把「盲区」写成「无问题」⇒ H1 红 (★措辞判据: 出现「无问题 / 不影响 / 忽略」等 ⇒ 红★) · ⑤ 篡改 §2 某条 need 的清理口径 ⇒ H3 红 · ⑥ 篡改 H4 提到的清单条目数 ⇒ H4 红** ★
★**沙盒一律落项目盘 `tmp/` (★不许写 /tmp: 2026-11-23 04:4x 实测系统 /tmp 配额已满★)** ★
★**★禁止 `os.symlink()` (★ISS-327 cont1 写穿真件的根因★)★★** ★ — ★**沙盒里要复制就真复制 (`shutil.copytree`)·不许软链·不许「出真副本」这一步** ★

### ★★③ 交卷物 (3 件) · 第 3 件 · 交卷页 + 分片 + 留证 ★★
- ★**交卷页** `HANDOFF/2026-11-23_sw-lead_ISS362_SW侧S10换封装影响面.md` (★B1~B6 六段齐全 + 20 条验收逐条判定 + 落盘清单 + 沙盒留证路径★) ★
- ★**分片** `state/fragments/sw.yaml` ★**只走 `state/frag_write.py`** ★ ⇒ ★**写前后各记一次 md5 基线·期间被别人改过 ⇒ 停下并在交卷页 B5 写清「已停止」·不许静默覆盖** ★
- ★**留证** `logs/iss362/` (★基线 md5 / 10 道闸基线逐道 rc / 链头实测 / 8 条 need 的 md5 逐条比对表 / 沙盒预演全量输出 / selftest 全量输出 / 闸复跑输出★) ★

---

## ★★三 · 边界 (★逐条·不许越★) ★★

★**零写板** ★ (★板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · 4,940,213 B ⇒ **开工前 + 交卷后各打一次双证**★) ★
★**零落表** ★ (★`HW/netlist_v1.csv` · `HW/netlist_v1_pins.csv` · `HW/BOM_v1.csv` · 原理图 · `HW/SCHEMATIC_LANDING_V1_LANDED.md` · `state/issue_log.yaml` 一字不改★) ★
★**零改既有闸** ★ (★`SW/tools/check_onepass_sw_sync.py` · `SW/tools/check_sw_ref_reachability.py` · `SW/tools/check_landing_trace_obligation.py` · `SW/tools/check_demo_panel_spec.py` · `SW/tools/check_onepass_sw_release.py` · `SW/tools/timing_check.py` · `state/gate_check.py` · `state/merge.py` · `state/frag_write.py` 一字不改★) ★
★**零改既有页面正文** ★ (★`SW/BOARD_ONEPASS_SW_SYNC.md` ★**本单【不许】给它加第 9 条·不许改那 8 条的任何一个字**★ · `SW/SW_MD5_BASELINE_LEDGER.md` ★**§1 锚点块一个字不许动**★ · `SW/ONETRIP_SW_SAMEBATCH_RENAME_LIST.md` · `SW/SHUTDOWN_SEMANTICS_SPEC.md` · `SW/SW_TIMING_REVIEW.md` 一字不改★) ★
★**零改台账锚点 md5** ★ (★★「手改 md5 凑绿」这条路是 ISS-275/ISS-284 花大力气堵掉的⇒ 本单【绝对不许】走·哪怕是为了让 H3 变绿★★) ★
★**零外发 / 零采购 / 零联系供应商** ★
★**不替老板拍板** ★
★**不写别人的分片** ★ (★只写 `state/fragments/sw.yaml`★) ★
★**不改 `PROJECT_TRACKER.md` §0 锁死表** ★
★**证据分级必标** ★
★**单条 `exec` ≤ ~120 秒** ★

---

## ★★四 · 必跑命令 (★全部真实存在·2026-11-23 13:5x main 本机实测过★) ★★

```
python3 SW/tools/check_onepass_sw_sync.py
python3 SW/tools/check_sw_ref_reachability.py
python3 SW/tools/check_landing_trace_obligation.py
python3 SW/tools/check_demo_panel_spec.py
python3 SW/tools/check_demo_panel_spec_r6_selftest.py
python3 SW/tools/check_demo_panel_spec_r6_chainjudge_selftest.py
python3 SW/tools/check_demo_panel_spec_r6_hardprot_iss315_selftest.py
python3 SW/tools/check_shutdown_semantics.py
python3 SW/tools/check_timing_review_adc_sync.py
python3 SW/tools/timing_check.py
python3 SW/tools/check_onepass_sw_release.py
python3 SW/tools/check_onepass_sw_release.py --selftest
python3 SW/tools/check_sw_fp_truth_impact.py          # ★本单新建★
python3 SW/tools/check_sw_fp_truth_impact.py --selftest
python3 state/merge.py
python3 state/gate_check.py
python3 state/check_brief_commands.py
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv SW/SW_MD5_BASELINE_LEDGER.md
```

★**★TMPDIR 约定 (★照抄 ISS-335 的做法·实测本机 /tmp 配额已满★)**: ★**子进程一律把 `TMPDIR` / `TMP` / `TEMP` 指到项目内 `tmp/iss362_tmp` ⇒ 不指会 EDQUOT 假红** ★

★**验收线 (★20 条·main 会自己复跑·不采信你的自述★)**:
① 页存在且非空 ② §0 S1/S10 对照表齐全 ③ §1 逐闸影响表 10 道闸一行不缺 ④ 「会红」项都有可复跑命令+期望输出 ⑤ 「不会红」项都有机制依据 ⑥ §2 八条 need 逐条给清理口径 ⑦ §3 当天 SOP 含「绝对不许做」且逐字照抄红线 ⑧ 新闸 rc=0 ⑨ `--selftest` ≥6/6 全 PASS 且每条自证「只红目标那条」 ⑩ H1/H3/H4 三条在交卷时是【登记式绿】而不是【同义改写绿】 ⑪ 链头实测三件全对 ⑫ 10 道 SW 闸基线逐道 rc=0 ⑬ 沙盒在项目盘 `tmp/` 且无 `os.symlink` ⑭ 板 md5/mtime 逐字节未变 ⑮ 网表/脚表/BOM md5 逐字节未变 ⑯ `SW/SW_MD5_BASELINE_LEDGER.md` §1 锚点块逐字节未变 ⑰ `SW/BOARD_ONEPASS_SW_SYNC.md` 逐字节未变 ⑱ 既有闸脚本一个字节未改 ⑲ `merge.py` rc=0 且 `gate_check.py` rc=0 ⑳ 分片写入只走 `frag_write.py` + 交卷页 B1~B6 齐全 + `logs/iss362/` 留证在盘
