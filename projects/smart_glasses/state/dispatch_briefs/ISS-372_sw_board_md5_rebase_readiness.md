# ISS-372 · sw-lead · 「板那一趟」S9 换基线 · SW 侧板 md5 引用面清账 + 一条「钉板 md5 闸清单」自守闸

★★**题**: ★**把「板那一趟」合法改板当天 (S9 换基线) SW 侧会「假红」的隐患查清并做成机器可查的东西** —— ★**具体是: SW 域有 17 个活文件 / 57 处硬写着旧板 md5 `611b869e…`, 其中 3 个是【判据脚本】; 而那张「钉板 md5 的闸清单」是 2026-11-17 生成的, 今天新造的 2 道 SW 闸根本没进那张表 ⇒ ★★改板当天它们会一起红, 而红的真含义是「板被换了」不是「板改坏了」 ⇒ 现场极可能误读成后者 ⇒ 去改板凑绿 ⇒ 板 md5 变第二次 ⇒ 整趟白跑★** ★★**⇒ 本单 = ① SW 域 md5 引用面逐处清账 (★哪些必须随板改 / 哪些是历史留证永远不许改★) ② 一条【清单新鲜度 + 缺口登记】自守闸 (★让下一道新闸再硬钉板 md5 时当场被抓住, 而不是等改板那天才炸★) ③ 答掉一条挂了两周的过期 need** ★★
★★**类别**: ★**纯分析 + 作业包 + 新建闸 + 沙盒预演 · 零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 · 零外发 · 不代老板拍板** ★★

---

## ★★〇 · main 的本机实读 (★2026-11-23 20:4x~20:5x · 全部数字本机可复跑 · 不抄任何 agent 报告★) ★★

### ★★〇.1 · SW 域硬写旧板 md5 的活文件 (★排除 `.bak` / `__pycache__`★) ★★

★**本机实跑 `grep -rl 611b869e SW/` 的结果 (★17 个活文件 · 57 处命中★)★**:

| 类别 | 文件 | 处数 |
|---|---|---|
| ★**判据脚本 (3 个)★** | `SW/tools/check_fp_truth_read.py` | 1 |
| | `SW/tools/check_onepass_sw_sync.py` | 5 |
| | `SW/tools/check_onepass_legb_sw_impact.py` | 1 |
| ★**规格页 / 台账 (14 个 .md)★** | `SW/SW_MD5_BASELINE_LEDGER.md` | 13 |
| | `SW/ONETRIP_SW_SAMEBATCH_RENAME_LIST.md` | 3 |
| | `SW/BOARD_ONEPASS_SW_SYNC.md` | 3 |
| | `SW/BOARD_ONEPASS_LEGB_SW_IMPACT.md` | 4 |
| | `SW/ONETRIP_SW_POSTRENAME_GATE_SOP.md` | 4 |
| | `SW/SW_NEEDS_TRIAGE.md` | 3 |
| | `SW/BOARD_ONEPASS_SW09_LANDING_PATCH.md` | 2 |
| | `SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md` | 2 |
| | `SW/BOARD_ONEPASS_FP_TRUTH_READ_ENTRY.md` | 1 |
| | `SW/ONETRIP_SW_RENAME_SAFETY.md` | 1 |
| | `SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md` | 1 |
| | `SW/DEMO_BOARD_60MS_VERDICT_PLAN.md` | 1 |
| | `SW/LOAD_SWITCH_SELECTION_FACTS.md` | 1 |
| ★**历史留证 (1 个)★** | `SW/research/ISS250_r6_复核记录.md` | 1 |

★**★关键判断 (★本单的正题★): 这 57 处不是同一种东西, 处置方式【完全相反】★★**
★**① 「判据锚」类 (★必须随板改·否则闸假红★)** ⇒ 判据脚本里那 7 处 + `SW/SW_MD5_BASELINE_LEDGER.md` 的 13 处 (★那 13 处是 R6/R7 的判决源★)
★**② 「规格页引用」类 (★改板那一趟随板改·平时不许动★)** ⇒ 其余 13 个 .md 里除台账外的那几处
★**③ 「历史留证」类 (★永远不许改!!★)** ⇒ `SW/research/ISS250_r6_复核记录.md` (★它是某次复核当时的读数留痕★) + 各页里记「当时板 md5 = xxx」的历史叙述段
★**⇒ ★★所以「改板那天把 611b869e 全仓 sed 替换一遍」这个做法是【错的】: 它会把历史留证改成假记录 (★比留着旧数更坏★) ⇒ ★★必须逐处分类, 不许一刀切★★** ★

### ★★〇.2 · 那张「钉板 md5 的闸清单」已经过期 (★本机的硬事实★) ★★

★**`state/board_md5_pinned_gates.json` + `.md`** (★由 `state/_gen_board_md5_pinned_gates.py` 一次性生成★) ★**生成时刻 = 2026-11-17 20:49** ★ ★**它自己页首写的目的 (★逐字★)**:

> ★**为什么要这张表**: ★**「板只改一次」那一趟 (S1~S13) 合法改板当天, 下面这 9 道闸会同时红** ★ ⇒ ★**而这些红的真实含义是「板被换了」, 不是「板改坏了」** ★ ⇒ ⇒ ★**现场的人极可能误读成后者 ⇒ 去改板凑绿 ⇒ 板 md5 变第二次 ⇒ 整趟白跑** ★ ⇒ ★**所以: 板那一趟开工前, 每道钉板 md5 的闸都必须先有【合法改板】通道 (照 ISS-284 的 `reboard` 原子映射形状)** ★

★**本机实读那张 json (★共 9 条 · HW 6 / MECH 2 / SW 1★)**: `HW/check_fsin_rootcause.py` · `HW/check_g1a7_selection_landed.py` · `HW/check_onepass_commit_order.py` · `HW/check_onepass_preflight_coverage.py` · `HW/check_pin_function_labels.py` · `HW/check_workpack_state_values.py` · `MECH/check_board_frame_coords.py` · `MECH/check_demo_struct_truth.py` · `SW/tools/check_onepass_sw_sync.py` ⇒ ★**9 条全部标「已有 reboard 通道」** ★

★**★本机实跑全仓扫描 (★只看【真钉板 md5 的活判据脚本】· 排除 `state/_*` 一次性脚本与文档提及·) ⇒ 找到了 3 道【今天新造、且没有 reboard 通道】的闸★★**:

| 闸文件 | 硬钉位置 | 造它的单 | 有 reboard 通道? | 建在清单里? |
|---|---|---|---|---|
| ★**`SW/tools/check_fp_truth_read.py`** | L87 `BOARD_BASELINE_MD5 = "611b869e…"` | ★**ISS-363** (今天 17:27 交付) | ★**否** ★ | ★**否** ★ |
| ★**`SW/tools/check_onepass_legb_sw_impact.py`** | L70 `PROTECTED_MD5 = {"board_md5": "611b869e…", …}` | ★**ISS-370** (今天 19:50 交付) | ★**否** ★ | ★**否** ★ |
| `HW/check_iss354_manufacturability.py` | L40 `EXPECT_PCB_MD5 = "611b869e…"` | ISS-354 | ★否** | ★否** ★ |

★**⇒ 三道闸的判据逻辑本机实读确认 (★所以「改板当天必红」不是猜测★)**:
★**① `check_fp_truth_read.py` 的 F5** (★L405 起★): 判 `b["md5"] != BOARD_BASELINE_MD5` ⇒ 追加一条 `"板 md5=%s ≠ 基线 %s ⇒ 判红 (★板被换过 ⇒ 零写板自证失败★)"` ⇒ ★**盘上板 md5 一变, F5 立刻红** ★
★**② `check_onepass_legb_sw_impact.py` 的 G8** (★L397 起★): 逐个比 `PROTECTED_MD5` 的 4 个键 ⇒ 板 md5 不等就 `bad.append("板/网表/脚表/BOM 四份真源 md5 逐字节等于受保护基线")` ⇒ ★**盘上板 md5 一变, G8 立刻红** ★
★**★⇒ 这 3 道闸就是「清单过期」的活证据: 表是 11-17 的, 闸是 11-23 造的, 谁都没提醒谁★** ★

★**⇒ 而那张表【没有任何闸在守它新鲜】**: ★**本机实跑: `grep -rn "board_md5_pinned_gates" --include=*.py` ⇒ 命中的只有一次性脚本 `state/_apply_20261117_1845_main_open296_297_298.py` + 一份决策页 ⇒ `state/gate_check.py` 零命中 ⇒ ★★这张清单【自生自灭】, 下一道新闸硬钉板 md5 时没人拦★★** ★

★**★⇒ ★★这就是「板只改一次」铁律最贵的一个漏洞形态: 不是判据写错了, 是【清单漏了】⇒ 漏的那几道闸在改板当天集体假红 ⇒ 现场误读 ⇒ 板改第二次 ⇒ 整趟白跑★ ★**

### ★★〇.3 · 挂了两周的一条过期 need (★你顺手答掉·省下一个人再查一遍★) ★★

★**`state/fragments/sw.yaml` → `needs_from` → key `iss249_kicad_sch_md5_not_anchor_sw` · `to: sw-lead` · `since: 2026-11-16` · ★**至今未闭合** ★ ★**need 原文要点**:

> ★**ISS-249 新发现**: `HW/PCB/demo_mainboard*.kicad_sch` (11 个) 的 md5 真的不能当锚点 —— 比之前判断的更严重: `state/check_sch_pinfull.py` 与 `state/check_sch_erc.py` 内部会 subprocess 调 `state/gen_kicad_sch.py` ⇒ 跑这两条门禁就会重铸随机 UUID ⇒ 任何门禁跑完 md5 都变 ⇒ 只能当【归一化 UUID+时间戳后是否同图】的判据 (ISS-249 实测 11/11 SAME ⇒ F1 对图形零影响)★

★**★main 本机实测 (★2026-11-23 20:4x·两条命令·前后各打一次 md5★)⇒ 这条 need 的两个前提, 现在一个不成立、一个没落地★★**:

```
$ md5sum HW/PCB/demo_mainboard.kicad_sch   ⇒ e433793b4a3ec321cc69f466d7e15de7
$ python3 state/check_sch_erc.py            ⇒ rc=0
$ md5sum HW/PCB/demo_mainboard.kicad_sch   ⇒ e433793b4a3ec321cc69f466d7e15de7   ← ★一字未变★
$ python3 state/check_sch_pinfull.py        ⇒ rc=0
$ md5sum HW/PCB/demo_mainboard.kicad_sch   ⇒ e433793b4a3ec321cc69f466d7e15de7   ← ★一字未变★
```

★**⇒ 前提①「跑这两条门禁就会重铸随机 UUID」★【实测不成立】★**: 两条门禁跑完 `.kicad_sch` 的 md5 逐字节不变 (★`check_sch_pinfull.py` 虽 `import gen_kicad_sch`, 但只用它的 `kicad_ref()` 纯函数, 并不重生成原理图; 它调的是 `kicad.sh sch export netlist`★)
★**⇒ 前提②「风险已落地」★【实测没落地】★**: ★**SW 域活文件里 `.kicad_sch` 的 md5 命中 = 0 处** (★`grep -rn e433793b SW/` ⇒ 空★) ⇒ SW 侧从来没有拿 `.kicad_sch` 的 md5 当过锚 ⇒ 这个风险至今没有伤到任何人
★**⇒ ★★所以这条 need 的正确处置是: 【结论订正 + 降级为「一条已知的注意事项」】而不是继续挂着让人以为有个活的隐患★ ★**
★**★但★你必须自己把「`.kicad_sch` 到底能不能当锚」查到底, 不许只抄 main 上面那两条命令★★**: ★**main 那两条只证了「这两条门禁不改它」; 真正的问题是「谁会改它」—— `state/gen_kicad_sch.py` 直接跑会不会重铸 UUID (★它 L119 `return str(uuid.uuid4())` + L345/358/378/398/426/448 处处 `uid()` ⇒ ★★它【本身】就是随机源★) ⇒ ★★请在【沙盒副本】上实跑一次 `gen_kicad_sch.py` 看 md5 是否变 (★★绝不许在真件上跑 —— 那会重铸真原理图★)⇒ 结论才完整★** ★

### ★★〇.4 · 权威口径与现成范本 (★照抄, 不许自创★) ★★

| 事实 | 位置 | 本机实读 |
|---|---|---|
| 合法改板机制的**唯一真源** | `SW/tools/check_demo_panel_spec.py` 的 **R6** (★ISS-284 已跑通★) | ★`SW/tools/check_onepass_sw_sync.py` L500-L530 是照搬它的读法 (★`cdps()` + `build_virtual_root()` + `reboard` 四项★)★ |
| SW 侧**已跑通**的通道样板 | `SW/tools/check_onepass_sw_sync.py` (★20 处 `reboard`★) | ★它的交卷页 `HANDOFF/2026-11-17_sw-lead_ISS298_合法改板通道.md` (★37,070 B★) ★ |
| `reboard` 的**四项原子映射** | `by` / `file` / `prev_md5` / `md5` | ★缺一 ⇒ 红 ★四项必须与落表台账链头**逐字**对上 ★ |
| **fail-closed 三条** | 链头不唯一 / 链断 / 链头无单号 ⇒ 红 | ★一条不许放宽 ★ |
| `reboard: null` 的含义 | 还没发生过合法改板 ⇒ **纯 md5 硬保护** | ★★不许为了「将来会改」就把基线放松★★ ★ |
| 反向用例 (★已跑通的 5 条★) | `check_onepass_sw_sync.py` L880-L894 | ★⑪ 台账查不到那行 ⇒ 红 · ⑫ 链头不唯一 ⇒ 红 · ⑬ 链断 ⇒ 红 · ⑭ 只改板不动 `.kicad_pro` ⇒ 红 · ⑮ 四项齐全 ⇒ 绿 (★正向★) ★ |

★**★⇒ 你要交付的闸【不许自己造第二套合法改板判据】★ ⇒ 照 §〇.4 那张表的形状 (★像 `check_onepass_sw_sync.py` 那样【只读调用】权威闸★) ★**

---

## ★★一 · 本单要交什么 (★3 件 · 不许扩项★) ★★

### ★★① ★**新建** 一页: `SW/BOARD_ONEPASS_SW_MD5_REBASE_READINESS.md` ★★

★**必含 (每节带复跑命令 + 证据等级)★**:

- ★**§0 口径与读数**: 板 md5 基线 `611b869e13518c3c023fb178f91a0075` (★来源行号 + 复跑命令★) · 落表台账真身 `HW/SCHEMATIC_LANDING_V1_LANDED.md` (★链头从哪读★) · 权威 R6 判据位置
- ★**§1 SW 域 57 处 md5 引用逐处清单** (★★这是本单的正题★): ★**每一处**给 ★`文件` + `行号` + `原文` + ★**三类归属 (判据锚 / 规格页引用 / 历史留证)**★ + ★**改板那一趟的处置 (随板改 / 永远不许改 / 交 main 拍)** ★ ⇒ ★★必须逐处, 不许按文件归并 (★一个文件里可能同时有三类★)★★ ★
- ★**§2 「改板那天会假红」的逐闸账**: ★**3 道闸** (★`check_fp_truth_read.py` F5 / `check_onepass_legb_sw_impact.py` G8 / `check_iss354_manufacturability.py`★) ★逐道给: 硬钉位置 (行号) · 判据原文 · ★**改板当天它会红吗 (★引用你实跑的沙盒读数, 不许推理★)** · 红的真含义 vs 会被误读成什么 · ★**该走哪条通道 (照 §〇.4 的形状·给出【补丁规格】但不落)**★
- ★**§3 「清单过期」的账**: ★**为什么那张 json 是 11-17 的而闸是 11-23 的** + ★**为什么没有任何闸在守它新鲜 (★引用 §〇.2 的 grep 实读★)** + ★**本单新建的自守闸怎么补这个洞 (★指向交付物②★)★**
- ★**§4 `.kicad_sch` 能不能当锚 (★答那条挂了两周的 need★)**: ★**给出完整结论 (★含「谁会改它」这一问的沙盒实跑★)** + ★**把 `iss249_kicad_sch_md5_not_anchor_sw` 的结论写进 `sw.yaml` 的 `answers` (★同 key★)**
- ★**§5 跨域登记 (★只登记·不越界改★)**: ★**`HW/check_iss354_manufacturability.py`** (★hw-lead 的域★) + ★**`state/land_v_values.py` L96** (★落表器·main 的域★) + ★**`state/board_md5_pinned_gates.json` 与 `state/board_md5_pinned_gates.md` 需要刷新** (★main 的域·你只给「刷新后应有的内容」, 不许自己写那两个文件★) ⇒ ★**三条都登记成 `sw.yaml` 的 `needs_from` (`to: main`)**
- ★**§6 未决项 (★只登记·不代拍·每条给代价★)**: ★**改板那一趟的「S9 换基线」到底一次改齐哪些 (★按 §1 的三类处置·S9 是 B 类终段步·只能在板改完之后最后跑一次★)** · 那 3 道闸的通道补丁 ★**谁来落、什么时候落 (★你的建议 + 理由)**★ · 历史留证那一类 ★**「永远不许改」这条禁令要不要写成机器判据★**
- ★**§7 证据分级表**: 每条结论标 `[实测]` / `[推算]` / `[0数据]` (★不许出现「可能」「大概」这种无档措辞★)

### ★★② 新建机器闸: `SW/tools/check_sw_board_md5_rebase_readiness.py` (★新建★) ★★

★**判据 (★自证型·不许靠注释说绿★)**:

| # | 判据 | 要点 |
|---|---|---|
| H1 | ★**SW 域板 md5 引用面必须被 §1 的清单逐处覆盖** | ★自己扫 `SW/` (★排除 `.bak` / `__pycache__`★) 得出 (文件, 行号) 集合 ⇒ ★**扫出来的每一处都必须在 §1 清单里有对应行, 且三类归属非空** ★ ⇒ ★**漏一处就红** ★ |
| H2 | ★**每个判据锚必须标了它的处置 (随板改 / 交 main / 不许改)** | 处置字段缺失 ⇒ 红 |
| H3 | ★**「历史留证」类必须真的不许改** | ★**反向判据**: 若某处被标成「历史留证」而它其实在 `.py` 判据脚本里 ⇒ 红 (★不许把活判据塞进历史留证类糊弄过去★) |
| H4 | ★**SW 域每道【真钉板 md5 的判据脚本】必须登记在册** | ★扫 `SW/tools/*.py` 找出硬钉板 md5 的闸 ⇒ ★**每一道都必须在 §2 有账** ⇒ ★**今天新造的那两道今天就能被抓住** ★ |
| H5 | ★**闸清单新鲜度 (★本单的核心机制★)** | ★**每道 SW 判据脚本要么 (a) 已有合法改板通道 (★代码级可查: 文件里有 `reboard` 四项判定逻辑★)· 要么 (b) 在 §2 里被显式登记为「已知缺口 + 缺口归属 + 谁来补 + 补法规格」⇒ ★**两者都不是 ⇒ 红** ★ ⇒ ★★「登记过的缺口」不红, 「没人知道的缺口」才红 ★★ ★ |
| H6 | ★**板面零写板自证** (板 md5/mtime/size 三项) | 漂移 ⇒ 红 |
| H7 | ★**证据等级五级白名单 + 正文零挂起措辞** | ★照 `SW/tools/check_onepass_sw_sync.py` 的现成判据形状 ★ |

★**★`--selftest` 反向用例 ≥ 7 条 · 每条必须自证「红的集合 == {目标那一条}」(★多红一条即判该用例 FAIL★)★** ★建议至少含: ①在 §1 清单里删掉一处扫描得到的命中 ⇒ H1 红 ②把某处归属改成空 ⇒ H2 红 ③把一个 `.py` 里的命中标成「历史留证」⇒ H3 红 ④把一道新闸从 §2 的账里删掉 ⇒ H4 红 ⑤让某道闸既没通道也没登记 ⇒ H5 红 ⑥在沙盒里把板改一个字节 ⇒ H6 红 ⑦把证据等级写成第六级 ⇒ H7 红 ★
★**★沙盒纪律: 沙盒一律落项目盘 `tmp/iss372_sbx/` (★不许写 `/tmp` — ★★2026-11-23 04:4x 实测系统 `/tmp` 配额已满, 写 `/tmp` 会让闸拿到假读数★)★★ ★
★**★★沙盒预演必须包含这一条 (★本单的招牌动作★): 在沙盒里把【板的 md5 合法改掉】(★按 ISS-284 的四项原子映射 + 落表台账链头★) ⇒ 逐道证明 ★① 3 道闸各自的判据在改板前红 / 改板后绿 (★照通道走★) ② 通道没建的闸在改板后【仍红】(★这才是要登记成缺口的那些★) ③ 「改板前=基线」的纯 md5 硬保护支路在改板后仍红 (★= `reboard: null` 那条不许松★)★ ★**

### ★★③ 交卷页 + 分片 + 留证 ★★

- ★**交卷页**: `HANDOFF/2026-11-23_sw-lead_ISS372_SW侧板md5引用面清账与清单自守.md` (★**B1~B6 六段齐全** + 验收线逐条判定 + 落盘清单 + 沙盒留证路径★)
- ★**分片**: `state/fragments/sw.yaml` ★**只走 `state/frag_write.py`** ★ ⇒ 写前写后各记一次 md5 基线 · 期间被别人改过 ⇒ 停下并在交卷页 B5 写清「已停止」· 不许静默覆盖
- ★**留证**: `logs/iss372/` (★基线 md5 / 实扫脚本与输出 / 沙盒三闸前后读数 / selftest 全量输出 / 既有闸复跑输出★) (★≥10 件★)
- ★**★必须用同 key 答掉 `iss249_kicad_sch_md5_not_anchor_sw` (★在 `sw.yaml` 的 `answers` 里记★)** ⇒ ★★否则它会一直挂在 `needs_from` 里, 下一个 agent 还得重查一遍★ ★

---

## ★★二 · 边界 (★逐条·不许越★) ★★

| 边界 | 要求 |
|---|---|
| ★**零写板** | 板 md5 必须仍 `611b869e13518c3c023fb178f91a0075` · mtime 必须仍 `2026-11-06 07:07:17.362193413` · size 仍 4940213 · ★**开工前 + 交卷后各打一次双证★** · ★★沙盒里也不许对真件做任何写 ★★ |
| ★**零落表** | `HW/netlist_v1.csv` · `HW/netlist_v1_pins.csv` · `HW/BOM_v1.csv` · `HW/SCHEMATIC_LANDING_V1_LANDED.md` · 原理图 (★`HW/PCB/demo_mainboard*.kicad_sch` 11 个★) · `state/issue_log.yaml` 一字不改 |
| ★**零改既有闸** | ★`SW/tools/check_fp_truth_read.py` · `SW/tools/check_onepass_sw_sync.py` · `SW/tools/check_onepass_legb_sw_impact.py` · `SW/tools/check_demo_panel_spec.py` · `SW/tools/timing_check.py` · `SW/tools/check_shutdown_semantics.py` · `state/check_pcb_nets.py` · `state/gate_check.py` · `state/merge.py` · `state/frag_write.py` · `state/check_sch_erc.py` · `state/check_sch_pinfull.py` 一字不改 ★★★**你交的是【补丁规格】不是补丁本身 ⇒ 那 3 道闸的通道谁来落, 交 main 排期 (§5/§6 已登记)★ ★★ |
| ★**零改既有页面正文** | ★`SW/SW_MD5_BASELINE_LEDGER.md` (★那 13 处是 R6/R7 的判决源, 一个字都不许动★) · `SW/BOARD_ONEPASS_SW_SYNC.md` · `SW/BOARD_ONEPASS_LEGB_SW_IMPACT.md` · `SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md` · `SW/BOARD_ONEPASS_FP_TRUTH_READ_ENTRY.md` · `SW/ONETRIP_*.md` · `SW/SW_NEEDS_TRIAGE.md` · `SW/research/ISS250_r6_复核记录.md` (★历史留证, 更不许动★) ⇒ ★**只许新建你那一页 + 新闸 + 交卷页** ★ |
| ★**零改 `state/` 下的清单** | ★`state/board_md5_pinned_gates.json` / `.md` (★main 的域★) / `state/_gen_board_md5_pinned_gates.py` 一字不改 ⇒ ★**你只给「刷新后应有的内容」, 登记成 need 给 main** ★ |
| ★**零挂链** | ★**本单新建的闸也不许挂** ★(`state/gate_check.py` 的 `EXTRA_GATES` 一行都不许动) |
| ★**只写自己的分片** | 只写 `state/fragments/sw.yaml` (只走 `frag_write.py`) |
| ★**不代老板拍板** | ★**改板那一趟 S9 的执行时点 / 那 3 道闸的通道谁来落 / 历史留证禁令要不要机器化 / 「板改第二次」的兜底预案** ⇒ ★**只登记 + 给代价**★ |
| ★**零外发 / 零采购** | ★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料 ★★本单不许发任何邮件/询价/问询 ★ |
| ★**不自签 issue_log** | 不许改 `state/issue_log.yaml` 的任何字段 (★签收归 main★) |

---

## ★★三 · 必跑命令 (★全部真实存在 · main 2026-11-23 20:5x 本机实测过★) ★★

```bash
# ★板双证 (开工前 + 交卷后各一次)★
md5sum HW/PCB/demo_mainboard.kicad_pcb && stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb

# ★SW 域 md5 引用面实扫 (★★不许写死计数, 你的闸要自己扫★)★
grep -rn 611b869e SW/ --include=*.py --include=*.md | grep -v '\.bak\|__pycache__'

# ★三道新闸的硬钉位置 (★逐个定位★)★
grep -n 611b869e SW/tools/check_fp_truth_read.py SW/tools/check_onepass_legb_sw_impact.py HW/check_iss354_manufacturability.py

# ★权威 R6 判据 + 已跑通的通道样板 (★照抄形状·不许多造★)★
grep -n 'reboard' SW/tools/check_demo_panel_spec.py SW/tools/check_onepass_sw_sync.py
sed -n '1,80p' HANDOFF/2026-11-17_sw-lead_ISS298_合法改板通道.md

# ★那条过期 need 的前提复核 (★★只读·不许跑会改真件的命令★)★
md5sum HW/PCB/demo_mainboard.kicad_sch
python3 state/check_sch_erc.py     && md5sum HW/PCB/demo_mainboard.kicad_sch
python3 state/check_sch_pinfull.py && md5sum HW/PCB/demo_mainboard.kicad_sch

# ★既有 SW 闸 (★你交卷时必须仍全绿★)★
python3 SW/tools/check_onepass_sw_sync.py       # rc=0
python3 SW/tools/check_fp_truth_read.py         # rc=0
python3 SW/tools/check_onepass_legb_sw_impact.py # rc=0
python3 SW/tools/check_demo_panel_spec.py       # rc=0

# ★本单新建的闸 (★交卷时它还不存在·本单产出★)★
python3 SW/tools/check_sw_board_md5_rebase_readiness.py            # rc=0
python3 SW/tools/check_sw_board_md5_rebase_readiness.py --selftest  # rc=0 (反向用例全过)

# ★门禁三件套★
python3 state/merge.py                                 # rc=0
python3 state/gate_check.py                            # rc=0 (Q1 = 18/18)
python3 state/frag_write.py --agent sw-lead --show     # rc=0
```

★**★本单不许跑 `state/gen_kicad_sch.py` 在真件上 (★它 L119 就是 `uuid.uuid4()` ⇒ 会重铸真原理图的 UUID★) ⇒ 要跑就在 `tmp/iss372_sbx/` 的副本树上跑★ ★**

---

## ★★四 · 交卷格式 (★照本仓惯例★) ★★

★**交卷页 B1~B6 六段 (★标题关键词要能被 `state/gate_check.py` 的 Q1 认出来★)★**: B1 结论 · B2 交付物 · B3 沙盒预演 · B4 接口取值/声明 · B5 边界自证 · B6 必跑命令输出 (★原文贴, 不许只写「全过」★)
★**★`state/gate_check.py` 的 Q1 判「B4 标题必须含 `接口取值` / `接口声明` / `interface_claims` / `接口请求` 之一」★ ★⇒ 你的 B4 标题就照抄这个词★ ★
★**★`state/gate_check.py` 的 Q1 还判「交卷页占位符 = 0」⇒ 交卷页里不许留 `TBD` / `待填` / `???` ★★**
★**★必跑命令的输出必须原样贴进 B6 (★rc 数字 + 关键行★), 并贴进 `logs/iss372/` ★**

---

## ★★五 · 一句话总结 (★你要回答的那个问题★) ★★

★**「改板那天, SW 侧有几道闸会因为『板被合法换了』而假红? 假红的那几道, 现场会不会误读成『板改坏了』而去改板凑绿? 以及: 怎么让下一道新闸再硬钉板 md5 时当场就被抓住, 而不是等改板那天才炸?」** ★
★**main 的本机实读已经指向答案 (★你必须独立复算一遍并自证, 不许直接抄★): SW 域 17 个活文件 / 57 处硬写旧板 md5, 其中 3 处判据脚本 + 13 处台账锚是「判据锚」类、其余是「规格页引用」类、只有 1 处 (复核记录) 是「历史留证」类 ⇒ ★★三者处置方式相反, 绝不许一刀切 sed★; 而那张「钉板 md5 的闸清单」是 11-17 的, 今天新造的 2 道 SW 闸 (ISS-363 / ISS-370) 既没进清单、也没有合法改板通道 ⇒ ★★改板当天它们必红, 而红的真含义是「板被换了」★ ★**
★**★⇒ 你要交的是: ① 57 处逐处清账 (哪处随板改 / 哪处永远不许改) ② 一道让【下一个新闸再硬钉板 md5 时当场被抓住】的自守闸 ③ 一条「判据锚不许伪装成历史留证」的反向判据 ⇒ ★★三条合起来 = 「板只改一次」那道铁律在 SW 侧从此不再靠人记得★ ★**
