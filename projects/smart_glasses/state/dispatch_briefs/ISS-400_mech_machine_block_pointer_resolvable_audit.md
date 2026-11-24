# ISS-400 · MECH 侧 · 跨页机器块指针可解析性清账 + 新建机器闸 · 零写板

★**题源**: ★**main 2026-11-24 22:4x 本机实读 (不抄任何 agent 报告)★**
★**主线**: 绘制 PCB 图 (★老板 2026-11-17 00:43★) ⇒ 本单属 ★**纯查证 + 纯分析 + 新建真相页 + 新建机器闸**★ ⇒ ★**零写板** ★

---

## §0 铁律 (★违反任一条 ⇒ 本单交卷无效★)

| ★边界★ | ★怎么自证 (交卷页 B4 要贴实测输出)★ |
|---|---|
| ★**零写板** ★ | `HW/PCB/demo_mainboard.kicad_pcb` 的 md5 / mtime / size 三项与基线**逐字相同** (基线 md5 = `611b869e13518c3c023fb178f91a0075`) |
| ★**零落表** ★ | 网表 / 脚表 / BOM 三张表 md5 与基线逐字相同 |
| ★**零改既有页正文** ★ | `MECH/BOARD_ONEPASS_FTS_VS_GENERIC_COURTYARD_DELTA.md` · `MECH/BOARD_ONEPASS_FTS_SEAT_SAMPLE_MEASURE_PLAN.md` · `MECH/BOARD_ONEPASS_SIGNED_APPEND_LEDGER_DESIGN.md` 三页 md5 与基线逐字相同 (★基线 md5 已在 §2 给出, 自己重算★) |
| ★**零改既有闸判据源码** ★ | §2 列的 11 道既有 MECH 闸 md5 全部与基线逐字相同 |
| ★**零挂链** ★ | `grep -c "check_machine_block_pointer_resolvable" state/gate_check.py` ⇒ **0** (★新闸只交卷, 不挂链; 挂不挂链交 main 拍 = §7 问句之一★) |
| ★**零外发** ★ | 不发任何邮件 / 询价 / 问询 / 采购 (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★) |
| ★**不代拍** ★ | ★**ISS-399 的 M-A / M-B / M-C / M-D 四条仍归 main** ★ ⇒ 本单只出逐字改法建议, 一条都不代拍 |
| ★**不自签 issue_log** ★ | `state/issue_log.yaml` 本单一字未写 (mtime 留证) |
| ★**只写自己分片** ★ | 只写 `state/fragments/mech.yaml` (★必须走 `state/frag_write.py`★ · 禁止 `open(p,"w")`) |
| ★**证据必须分级** ★ | `[官网]` / `[实测]` / `[媒体]` / `[推算]` / `[0数据]` 逐条标 |

★**额外纪律 (由派活方附加)★**:
① 写分片必须用 `state/frag_write.py` (禁止 `open(p,"w")`) ② 只写本任务允许的文件, 不碰别人的 ③ 证据分级 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` 必须标
④ ★**不许外发任何邮件/询价/问询/采购 (老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料) ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ⇒ 没有"批一句可以发"这个选项** ★
⑤ 交卷前跑 `python3 state/merge.py` (rc 必须 0) && `python3 state/gate_check.py` (Q1 必须 18/18) 并把输出贴进回复

---

## §1 题 (★main 2026-11-24 22:4x 本机实读·不抄任何 agent 报告★)

### 1.1 现象: ★三个"回填格"指针打到了不存在的键★

★**`MECH/BOARD_ONEPASS_FTS_VS_GENERIC_COURTYARD_DELTA.md` (ISS-393 真相页) 的 §5「量完填回哪一格」动作表, L176 / L177 / L178 三行逐字写的是★**:

```
| ① 座体宽 X (跨排, 4 位件) | … | §1 表第 1 行 + §6 `dimensions.factory_seat_body_x_4pos.measured` | … |
| ② 座体深 Y (跨排距, 前后壁) | … | §1 表第 3 行 + §6 `dimensions.factory_seat_body_y.measured` | … |
| ③ 绝缘体高 Z | … | §1 表第 4 行 + §6 `dimensions.factory_insulator_height_z.measured` | … |
```

★**⇒ 这三个键名在同页 §6 机器块 `dimensions` 里【一个都不存在】★**
★**同页 §6 机器块 `dimensions` 的真键是** (★行号是本机实读时的行号, 你自己重读一遍★):

| ★真键★ | ★行★ | ★结构★ |
|---|---|---|
| `seat_body_x_4pos` | L518 | `value` / `source` / `old_value` / `old_source` / `class` / `note` / `evidence` / `consumed_by` |
| `seat_body_y` | L538 | 同上 |
| `insulator_height_z` | L548 | 同上 |
| `factory_drill` | L568 | 同上 (★它是钻孔, 不属三量★) |

★**⇒ 全仓 grep `factory_seat_body` / `factory_insulator` 只命中 5 处**: ★ISS-393 页那 3 行 (死指针本体) + ★ISS-397 页 2 处**转述** (L199 登记 + L338 问 main) + ★`HANDOFF/2026-11-24_mech-lead_ISS397_座体三量收样作业包.md` 1 处转述 ★
★**⇒ 没有任何闸读这三个路径 ⇒ 这是一条【死路径】**: 照着 §5 表去填 ⇒ 填进一个不存在的格 ⇒ **什么都不会变** ★

### 1.2 ★就算把前缀改对, 那一格还是填不了★

★**同页 §6 的 `seat_body_x_4pos` / `seat_body_y` / `insulator_height_z` 三个真键里【没有 `measured` 这个字段】★**
★**⇒ 即使把 `factory_` 前缀改对 (§5 就会变成 `dimensions.seat_body_x_4pos.measured`), 那一格【依然不存在】★**
★**⇒ 也就是说 §5 的 §6 那一半指针【指错了页】, 不只是【指错了键名】★** ★★

### 1.3 唯一真实的实测槽在【另一页】★

★**`MECH/BOARD_ONEPASS_FTS_SEAT_SAMPLE_MEASURE_PLAN.md` (ISS-397 收样作业包页) 的机器块里有 `three_quantities`** (★L386 起★), 三个量各占一格:

| ★槽名★ | ★行★ | ★现在的值★ |
|---|---|---|
| `three_quantities.insulator_height_z` | L387 | `measured_value: null` · `measured_evidence: "[0数据]"` · `measured_readings: []` |
| `three_quantities.seat_body_width_x` | L400 | 同上 |
| `three_quantities.seat_body_depth_y` | L413 | 同上 |

★**⇒ 这才是全仓唯一的"三量实测回填格", 现在是空的 (符合 `[0数据]` 的定义)★**
★**⇒ 而且【槽名和 §5 写的连拼法都不一样】**: ★§5 写 `seat_body_x_4pos` / `seat_body_y`, 真槽叫 `seat_body_width_x` / `seat_body_depth_y` ⇒ ★**改前缀仍对不上** ★

### 1.4 收样闸只认这三个槽 ⇒ 钉死了"唯一真槽"★

★**`MECH/check_fts_seat_sample_plan.py`**:
- ★L45: `PAGE_REL = "MECH/BOARD_ONEPASS_FTS_SEAT_SAMPLE_MEASURE_PLAN.md"` ★
- ★L71: 钉了 ISS-393 页的 md5 = `0cb3ff2de940522b467ca3b01feda11c` (★本单不改那一页 ⇒ 这枚 pin 本单不许动★) ★
- ★L75: `QUANT_KEYS = ("insulator_height_z", "seat_body_width_x", "seat_body_depth_y")` ★
- ★L223: `tq = blk.get("three_quantities") or {}` ⇒ ★**闸只从 ISS-397 页那三个槽取实测值** ★

★**⇒ 所以"三量实测"这条数据链【只有一条合法通路】: ISS-397 页 `three_quantities.*` ⇒ ISS-393 §5 的指针【不在这条通路上】★**

### 1.5 为什么至今没人做: ★它挂在一个"要不要改"的问句上★

★**ISS-397 页 L199 (逐字登记) + L338 (逐字问 main)**:
> 「★**该页 §5 的动作表逐字写的是 `dimensions.factory_seat_body_x_4pos.measured` / `factory_seat_body_y.measured` / `factory_insulator_height_z.measured`, 而 §6 机器块里的真键是 `dimensions.seat_body_x_4pos` / `seat_body_y` / `insulator_height_z` ⇒ 三个 `factory_*` 键名是笔误, 回填必须用真键名 ⇒ 这条登记为 §9-④ 交 main 订正 (本单零改既有页正文)★」
> 「★**问法 (给 main)**: 要不要落一个追加式订正块把三个键名改对?★」

★**⇒ ISS-397 把它当"要 main 点头才能改" ⇒ 搁到今天没人答 ⇒ 死指针还在★**
★**⇒ ★这是本单存在的理由: 把"到底有多少这种悬空指针"从【一条问句】变成【一份可判的清单 + 一道机器闸】, 顺带把这一条的逐字改法写好交 main★**

### 1.6 ★为什么这是「板只改一次」关键路径上的死路★

★**事实链 (全部本机实读)**:
1. ★座体深 Y 与绝缘体高 Z 的**公差是 `[0数据]`** (官网只有 `REF` 基准尺寸, 图纸未给公差带) ⇒ ★**这两个量只能靠实测升档** ★
2. ★降级方案 = 落 FTS 时先打一块单板样 + 卡尺量三量 ★**⇒ 这件事被写死在「板只改一次」那一趟投板前** ★
3. ★**回填格指错 ⇒ 测完的数落不了地 ⇒ `three_quantities.*.measured_value` 永远是 `null`** ★
4. ★⇒ `MECH/check_fts_seat_sample_plan.py` 裸跑**永远红在 B.6** (★该闸裸跑 rc=1, 且**红的是现状**; 全闸其余 32 条绿★) ★
5. ★⇒ 两种坏结局: ① **有人把"闸还红"读成"还没到收样时点" ⇒ 带着两个 `[0数据]` 的公差放行投板 ⇒ 板改第二次**; ② **永远卡在"闸红"上 ⇒ 那一趟永远不许开工** ★

★**⇒ 这就是【板只改一次】纪律最怕的那类洞: 不是算错, 是【动作做完但数据落不了地】★**

### 1.7 本单要干什么 (★三句★)

① ★**全仓清账**: 把 PCB 线各真相页里"指向机器块某个槽"的指针**逐条抠出来**, 逐条判定【能不能真的解析到一个存在的槽】⇒ 出一份**悬空指针清单** (★本单已知的至少有上面 3 条, 你要找的是**全部**★)
② ★**把这件事变成机器闸**: 新建一道闸, 判据 = "扫描范围内零悬空指针"; ★**裸跑必须 rc=1 (红的是现状)**, `--selftest` 必须 rc=0 且末行 `ALL TESTS PASS` ★
③ ★**把这一条的逐字改法写好交 main** (★追加式订正块的候选文本 + 连带要刷新的 md5 pin 清单 + 连带会红的既有闸清单★) ⇒ **本单零改 ISS-393 页正文, 一条都不代拍** ★

---

## §2 实读清单 (★★你自己独立复核一遍, 不许抄 §1 的结论★★)

★**§1 的每一条都要你自己重读一遍再动手; 下面 8 条是最低复核集 (★命令 + 你该看到什么★)**:

| # | ★你该跑什么★ | ★你该看到什么 (★不符就说明题面口径有错 ⇒ 先在交卷页 B2 披露, 别硬改★)★ |
|---|---|---|
| 1 | `sed -n '170,180p' MECH/BOARD_ONEPASS_FTS_VS_GENERIC_COURTYARD_DELTA.md` | ★§5 动作表三行, 每行含 `dimensions.factory_...` ★ |
| 2 | `grep -n '"seat_body_x_4pos"\|"seat_body_y"\|"insulator_height_z"\|"factory_drill"\|"factory_seat_body\|"factory_insulator' MECH/BOARD_ONEPASS_FTS_VS_GENERIC_COURTYARD_DELTA.md` | ★四个真键存在 + 三个 `factory_*` 指针不存在 ★ |
| 3 | `sed -n '515,560p' MECH/BOARD_ONEPASS_FTS_VS_GENERIC_COURTYARD_DELTA.md` | ★三个真键里【没有 `measured` 字段】 ★ |
| 4 | `grep -n "three_quantities" -A 42 MECH/BOARD_ONEPASS_FTS_SEAT_SAMPLE_MEASURE_PLAN.md` | ★三个槽 + `measured_value: null` / `measured_evidence: "[0数据]"` ★ |
| 5 | `sed -n '40,50p;70,80p;220,226p' MECH/check_fts_seat_sample_plan.py` | ★`PAGE_REL` · `QUANT_KEYS` · `blk.get("three_quantities")` ★ |
| 6 | `grep -rn "factory_seat_body\|factory_insulator" --include=*.md --include=*.py . \| grep -v "^./tmp/"` | ★**全仓只有那 5 处**; ★**没有任何闸读它** ★ |
| 7 | `python3 MECH/check_fts_seat_sample_plan.py` | ★rc=1; ★**红的是 B.6 一条** (★"红的是现状"不是闸故障★) ★ |
| 8 | `python3 MECH/check_fts_vs_generic_courtyard_delta.py` | ★rc=0 (★这页自己没坏: 它管的是厂件 vs 库件, 不管指针可解析性★) ★ |

★**板侧基线 (§0 要自证的)**: `md5sum HW/PCB/demo_mainboard.kicad_pcb` ⇒ **`611b869e13518c3c023fb178f91a0075`** ★
★**既有闸基线 (§2 要自证的 11 道, 全在 MECH/)**: `check_onepass_mech_release.py` · `check_onepass_mech_sync.py` · `check_fts_seat_body_geometry.py` · `check_fts_vs_generic_courtyard_delta.py` · `check_onepass_struct_crosscheck.py` · `check_jdebug_arrangement_truth.py` · `check_debug_seat_3d_fit.py` · `check_onepass_s10_fp_swap_impact.py` · `check_mech_verdict_freshness.py` · `check_fts_seat_sample_plan.py` · `check_mech_signed_append_ledger.py` ★

---

## §3 交卷物 (3 件)

1. ★**`MECH/BOARD_ONEPASS_MACHINE_BLOCK_POINTER_AUDIT.md`** ★★ ★**本单新建·真相页** ★ ⇒ §0 结论摘要 · §1 扫描范围与指针形态定义 · §2 悬空指针清单 (★逐条: 源页 + 行号 + 指针逐字 + 指向的目标页 + 判定 + 为什么悬空 + 逐字改法建议★) · §3 真槽登记表 (★哪个页的哪个键是【唯一真槽】+ 谁消费它★) · §4 新闸判据 P1~P7 与机器块 · §5 连带影响面 (★哪些既有闸钉了被改页的 md5 / 哪些闸会因为改指针而变红 / 哪些页把指针抄了三遍★) · §6 实跑留证索引 ★
2. ★**`MECH/check_machine_block_pointer_resolvable.py`** ★★ ★**本单新建·机器闸** ★ ⇒ ★**裸跑 rc=1** (★红的是现状: 扫描范围内悬空指针 ≥1★) · ★**`--selftest` rc=0 且末行逐字 `ALL TESTS PASS`** ★ · 判据与机器块写在真相页 §4 ★
3. ★**`HANDOFF/2026-11-24_mech-lead_ISS400_机器块指针可解析性清账.md`** ★★ ★**本单新建·交卷页** ★ ⇒ B1~B7 全填 (★B6 贴 §六 实跑输出原文★)

★**三件都要真的在盘上; 路径不许改 (★派活方已按 `state/check_brief_commands.py` 验过这三个是本单产出★)** ★

★**分片**: ★**只写 `state/fragments/mech.yaml`** (★走 `state/frag_write.py`★) ⇒ 3 产出物 + interface_claims (★每条标 `to=main`★) + needs_from (★每条带代价 + 不答后果★) ★

---

## §4 扫描范围与指针形态 (★闸要机器可判, 不许靠人眼★)

### 4.1 扫描范围 (★本单只【读】别的域, 只【写】MECH 域★)

- ★**主范围**: `MECH/` 下全部 `.md` 里的机器块指针 ★
- ★**旁证范围 (只列不修)**: `HW/PCB/` 与 `SW/` 下全部 `.md` 里的机器块指针 ⇒ ★**别的域的问题只在清单里标【归属域】+【逐字改法建议】, 本单一件都不许改** ★
- ★**机器块识别**: 每页 ```json 围栏块 ⇒ ★用 `json.loads` 解析 (★不许用正则硬啃 JSON★) ★

### 4.2 指针形态 (★机器可判的候选形态, 你可以再加, 但每个都要能自动判定★)

| ★形态★ | ★例 (★来自本单已实测的那 3 条★)★ | ★判定口径★ |
|---|---|---|
| ★P1 同页 JSON 路径型★ | ★`dimensions.factory_seat_body_x_4pos.measured` ★ | ★在**本页**机器块里逐段下钻 ⇒ 段段存在 ⇒ 可解析; ★任一段不存在 ⇒ 悬空 ★ |
| ★P2 跨页 JSON 路径型★ | ★另一个 .md 页 (★目标页由指针自己写出来★) 的 `three_quantities.seat_body_width_x.measured_value` ★ | ★**必须写得出目标页** ⇒ 在目标页机器块里下钻 ★ |
| ★P3 页 + 键名同现型★ | ★`§6 \`dimensions.factory_...measured\`` ★ | ★**同页 P1 的变体** ⇒ 归 P1 判 ★ |
| ★P4 表格定位型★ | ★`§1 表第 1 行` ★ | ★★**本单发现的第二个歧义点**: ★"第 N 行"**没写清填哪一格** ⇒ §1 表有 5 列 ⇒ ★**"行"是唯一坐标、"格"缺失 ⇒ 人填也会填歪** ⇒ 归【歧义指针】单列一类 ★ |
| ★P5 自由文本引用型★ | ★`见 §4-③` / `见 §6` ★ | ★★**本单不要求判它** (自然语言引用不算机器块指针) ⇒ ★但清单里要**分开列**并说明"机器闸不管这一类, 为什么" ★ |

### 4.3 判定分类 (★清单里每条指针必须落在且只落一类★)

- ★**A 可解析** ⇒ 逐段下钻全部命中 ⇒ 顺带记下**它指向的槽是不是"该量的那个槽"** (★例如 §5 想填的是实测值, 就不该指向只有公称值的键★) ★
- ★**B 悬空 (键不存在)** ⇒ ★**本单已知的 3 条全在这一类** ★
- ★**C 歧义 (定位不到唯一格)** ⇒ ★P4 那类 ("第 N 行"没说是哪一格) ★
- ★**D 误指 (键存在但不是想要的槽)** ⇒ ★例如"要填实测却指向只有 `value` 的公称键" ⇒ ★★**这是比 B 更阴的一类: 键名存在 ⇒ 机器查不出来 ⇒ 人照填 ⇒ 填错地方还不报错** ★
- ★**E 无归属 (写不出目标页)** ⇒ 跨页指针没写目标页 ⇒ 归一 / 归二要能判 ⇒

★**⇒ 闸的判据核心: ★A 类之外的指针条数 == 0 ⇒ 才算绿★**

---

## §5 新闸判据 (★`MECH/check_machine_block_pointer_resolvable.py`★)

| ★判据★ | ★内容★ |
|---|---|
| ★P1★ | ★扫描范围可复现: ★闸自己扫 §4.1 的范围 ⇒ **不许把扫描结果写死** ★ |
| ★P2★ | ★指针候选识别: §4.2 的 P1/P2/P3 形态 + ★§4.2 的 P5 自然语言引用**明确排除在外** (★闸自己声明"我不管哪一类"★) ★ |
| ★P3★ | ★可解析判定: JSON 逐段下钻 ⇒ 命中 / 不命中 ⇒ ★**不许用子串命中当解析** (★`"seat_body_x_4pos" in json.dumps(...)` 这种是错的做法★) ★ |
| ★P4★ | ★分类输出: A / B / C / D / E 五类, 每条带【源页 + 行号 + 指针逐字 + 判定】★ |
| ★P5★ | ★**"这一条指针指向的槽是不是实测槽"判定** (★即 D 类★) ⇒ ★**判据必须能独立跑出 D 类, 不能只报 B 类** ★ |
| ★P6★ | ★**本单已知的 3 条死指针必须被逐条点名报出** (★★闸的 selftest 反向用例之一: ★把这 3 条从扫描范围里去掉 ⇒ 闸必须从红变绿 ⇒ 证明闸真的在看这 3 条, 不是恒红★) ★ |
| ★P7★ | ★**零写板自证**: 闸自己跑的时候不得写板 / 不得改页 ⇒ 闸跑完板 md5 不变 ★ |

★**selftest 要求 (★`--selftest` 必须 rc=0 且末行逐字 `ALL TESTS PASS`★)**:
- ★**正向 ≥1**: 真范围扫 ⇒ 恒定报出同样的悬空指针条数 (★条数不许随时间漂移★) ★
- ★**反向 ≥6**, 每条都要"**故意破坏 ⇒ 闸必须变红 / 变绿**", 建议覆盖:
  ① 把 §1 已知 3 条指针之一从扫描范围去掉 ⇒ 悬空条数减 1 ⇒ 闸必须抓到"条数变了" ★
  ② 造一条**指向另一个页**的假指针, 但那个键在目标页**不存在** ⇒ 闸必须报悬空 ★
  ③ 造一条**指向另一个页**的假指针, 键**存在** ⇒ 闸必须判 A 可解析 (★**证明闸能跨页下钻, 不是只会查自己页**★) ★
  ④ 造一条**键名存在但不是实测槽**的指针 ⇒ 闸必须报 D 类 (★证明 P5 真在跑★) ★
  ⑤ 改坏机器块 JSON (语法错) ⇒ 闸必须**报错退出**, 不许静默跳过 (★fail-closed★) ★
  ⑥ 把 §4.2 的 P5 自然语言引用塞进去 ⇒ 闸必须**不**把它算成指针 (★证明排除口径有效★) ★
  ⑦ 扫一个**空目录** ⇒ 闸必须报"扫描范围内零指针"而不是崩 (★证明不会恒红★) ★
- ★★**夹具要求 (★踩过坑, 必看★)**: ★**夹具不许把"真件当前的指针文本"硬抄成常量当期望值** ⇒ ★**期望值要从真文件现读现算** ⇒ ★**否则真件一改, 夹具立刻假红/假绿** (★这是 ISS-398 cont1 翻过的车★) ★

---

## §6 §六 必跑命令 (★全部本机实跑, rc 贴进交卷页 B6 原文★)

```bash
# ★新闸 (★本单新建·★裸跑红的是现状★)★
python3 MECH/check_machine_block_pointer_resolvable.py            # ★期望 rc=1 (红的是现状: 悬空指针 ≥1)★
python3 MECH/check_machine_block_pointer_resolvable.py --selftest # ★期望 rc=0 · 末行逐字 ALL TESTS PASS★

# ★既有 MECH 闸不许被本单弄红 (★11 道·★全部本机实跑·★rc 贴进 B6★)★
python3 MECH/check_onepass_mech_release.py            # 期望 rc=0
python3 MECH/check_onepass_mech_sync.py                # 期望 rc=0
python3 MECH/check_fts_seat_body_geometry.py           # 期望 rc=0
python3 MECH/check_fts_vs_generic_courtyard_delta.py   # 期望 rc=0
python3 MECH/check_onepass_struct_crosscheck.py        # 期望 rc=0
python3 MECH/check_jdebug_arrangement_truth.py         # 期望 rc=0
python3 MECH/check_debug_seat_3d_fit.py                # 期望 rc=0
python3 MECH/check_onepass_s10_fp_swap_impact.py       # 期望 rc=0
python3 MECH/check_mech_verdict_freshness.py           # 期望 rc=0
python3 MECH/check_fts_seat_sample_plan.py             # ★期望 rc=1 (★红的是 B.6 一条·★现状·★不是本单弄坏的★)★
python3 MECH/check_mech_signed_append_ledger.py       # ★期望 rc=1 (★红的是现状·★不是本单弄坏的★)★

# ★收尾 (★rc 必须达标★)★
python3 state/merge.py                                  # ★rc 必须 0★
python3 state/gate_check.py                             # ★rc 必须 0 · Q1 必须 18/18★
python3 state/check_brief_commands.py                   # ★rc 必须 0★

# ★边界自证 (★B4 贴输出★)★
md5sum HW/PCB/demo_mainboard.kicad_pcb                  # ★必须 611b869e13518c3c023fb178f91a0075★
grep -c "check_machine_block_pointer_resolvable" state/gate_check.py   # ★必须 0 (零挂链)★
grep -c "iss400" state/fragments/mech.yaml              # ★必须 ≥1★
```

★**留证**: 把 §六 全部输出落 `logs/iss400/` (★`cmd_*.log` 一条一文件★) ⇒ 交卷页 B6 贴原文 ★

---

## §7 留给 main 的问句 (★每条带代价 + 不答后果 + 归属; ★一条都不许代拍★)

★**你至少要回答这 4 条 (★可多不可少★)**:

| ★#★ | ★问句★ | ★不答的后果 (★你自己写清楚, 带代价★)★ |
|---|---|---|
| ★1★ | ★**ISS-393 页 §5 的 3 个死指针要不要按【追加式订正块】改对?** ★ (★候选逐字文本你写好, 但**本单零改那一页**★) | ★⇒ §5 一直把人指向不存在的格 ⇒ 三量实测永远落不了地 ⇒ 「投板前必量」这个前置动作永远不成立 ⇒ **板改第二次** 或 **那一趟永远不开工** ★ |
| ★2★ | ★**改指针时, `MECH/check_fts_seat_sample_plan.py` L71 那枚 ISS-393 页 md5 pin 要不要同批刷新?** ★ (★基线刷新 = 改既有闸的常量 ⇒ 属 main 的地界★) | ★⇒ 改了页不刷 pin ⇒ **收样闸当场变红** ⇒ 与"现状就该红"混在一起 ⇒ 以后没人分得清"红是现状"还是"红是我刚改坏的" ★ |
| ★3★ | ★**ISS-397 页 §9-④ 那条"要不要落订正块"的问句, 是不是就由本单的逐字改法来答?** ★ (★它已经挂了两天没人答★) | ★⇒ 这条问句继续挂着 ⇒ 下一趟还会有人重新发现一遍 ⇒ **同一个坑重复踩** ★ |
| ★4★ | ★**新闸 `MECH/check_machine_block_pointer_resolvable.py` 挂不挂链?** ★ (★本单零挂链★) | ★⇒ 零挂链 = 红了没人知道 (★这正是 ISS-398 交卷自曝的那一类: "零挂链 ⇒ 它红了没人知道"★) ⇒ ★**但挂链要占 G1 链的一个位, 且它裸跑就是红的 ⇒ 挂链前得先想清楚"红 = 现状"怎么在链上表达** ★ |

★**再加一条你自己的 (★如果你在 §5 扫出了别的域的悬空指针★)**: ★**那些别的域的条目要不要另开单? 归属哪个总工?** ★ ⇒ **本单只列不改** ★

---

## §8 交卷格式 (★B1~B7 全填, 不许留占位符★)

| ★块★ | ★内容★ |
|---|---|
| ★B1★ | ★**结论摘要**: ★悬空指针**总条数** + ★按类 (A/B/C/D/E) 分布 + ★**本单已知的 3 条是否全部命中** + ★**新闸裸跑/自测读数** + ★**一句话: 这一条对「板只改一次」意味着什么** ★ |
| ★B2★ | ★**独立复核自证**: ★§2 八条**你自己跑的结果** (★与题面口径不符的地方**如实披露**, 别硬改★) ★ |
| ★B3★ | ★**证据分级**: ★逐条标 `[官网]` / `[实测]` / `[媒体]` / `[推算]` / `[0数据]` ★ |
| ★B4★ | ★**边界自证**: ★板三项指纹 + 三表 md5 + 11 道既有闸 md5 + 三页 md5 + 零挂链 grep + 不自签 issue_log + 只写自己分片 ★ |
| ★B5★ | ★**留给 main 的问句** (★§7 四条 + 你自己加的★) 每条带: ★问法 + 建议默认值 + 不答后果 + 代价 + 归属★ ★ |
| ★B6★ | ★**复现命令 + rc**: ★§六 全部命令的 rc + 原文 (★`logs/iss400/` 的路径★) ★ |
| ★B7★ | ★**本单对自己新闸做的任何修正都要主动交代** (★改了判据 / 改了夹具 / 改了阈值 ⇒ 一律逐条列出来★) ★★**不许悄悄改**★ ★ |

★**加分项 (不强制)**: ★**把 §1 那 3 条死指针的逐字订正块候选文本直接写进真相页 §2** ⇒ ★这样 main 一句话就能拍, 不用再回头翻 ★
