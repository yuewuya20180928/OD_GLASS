# MECH · 机器块指针可解析性清账 (ISS-400 · mech-lead · 2026-11-24)

★**本单一句话**: ★**全仓「去机器块填回哪一格」的指针逐条抠出来, 逐条判能不能真的解析到一个存在的槽** ⇒
★**主范围 (MECH/) 115 条指针: A 可解析 64 / B 悬空 9 / C 歧义 3 / D 误指 19 / E 无归属 20** ⇒
★**「三量实测」这条数据链【一个可用的落点都没有】: 测完的数【落不了地】** ★

★**零写板 · 零落表 · 零改既有页正文 · 零改既有闸判据源码 · 零挂链 · 零外发 · 不代拍** ★

★**题源**: ★**main 2026-11-24 22:4x 本机实读 (不抄任何 agent 报告)** ★
★**新闸**: ★**`MECH/check_machine_block_pointer_resolvable.py`** ★(★裸跑 rc=1 · 红的是现状 · `--selftest` rc=0 末行 `ALL TESTS PASS`★)★

---

## ★§0 · 结论摘要 ★

| ★项★ | ★读数★ | ★证据★ |
|---|---|---|
| ★扫描页数★ | ★**188** (主范围 `MECH/` + 旁证 `HW/PCB/` `SW/`) ★ | ★`[实测]`★ |
| ★机器块★ | ★**53 块** (json.loads 成功的完整 JSON 围栏) + ★**14 块片段** (非完整 JSON ⇒ 忽略) + ★**0 块坏机器块** ★ | ★`[实测]`★ |
| ★主范围指针总条数★ | ★**115** ⇒ A 64 / B 9 / C 3 / D 19 / E 20 ★ | ★`[实测]`★ |
| ★旁证范围指针总条数★ | ★**28** ⇒ A 20 / B 1 / C 0 / D 0 / E 7 ★ | ★`[实测]`★ |
| ★本单已知的 3 条死指针是否全部命中★ | ★**是** ⇒ `MECH/BOARD_ONEPASS_FTS_VS_GENERIC_COURTYARD_DELTA.md` L176 / L177 / L178 逐条被点名 ★ | ★`[实测]`★ |
| ★新闸裸跑★ | ★**rc=1** (红的是现状: 主范围 A 类之外的指针 51 条) ★ | ★`[实测]`★ |
| ★新闸自测★ | ★**rc=0** · 末行逐字 `ALL TESTS PASS` · ★**12 条用例 (正向 3 + 反向 9) 全绿** ★ | ★`[实测]`★ |

### ★§0.1 · 一句话: 这一条对「板只改一次」意味着什么 ★

★**「座体三量实测」这件事, 从「量」到「数落进机器块」之间的【最后一米】整条断了** ★
★⇒ **板那一趟照样量得到数, 但数进不了任何闸读的格子** ⇒ ★**收样闸 `MECH/check_fts_seat_sample_plan.py` 永远红在 B.6** ⇒
★⇒ **两种坏结局二选一: ① 有人把「闸还红」读成「还没到收样时点」⇒ 带着两个 `[0数据]` 的公差放行投板 ⇒ 板改第二次; ② 永远卡住 ⇒ 那一趟永远不许开工** ★
★⇒ ★**这不是「算错」, 是【动作做完但数据落不了地】—— 「板只改一次」纪律最怕的那一类洞** ★

### ★§0.2 · 三条最要命的 (★本单新发现, 任务书未列★) ★

| ★#★ | ★发现★ | ★为什么最要命★ |
|---|---|---|
| ★**①** ★ | ★**ISS-393 页自己的机器块 §6 `degradation.measure_fill_back` 逐字登记的三条槽位 `dimensions.seat_body_x_4pos.measured` / `seat_body_y.measured` / `insulator_height_z.measured` 【一个都不存在】★ ⇒ ★**同一页 §5 写 `factory_*` (§6 没有), §6 写无前缀 (§6 也没有) ⇒ 该页【自相矛盾】** ★ | ★⇒ ★**按 ISS-397 §9-④ 挂了两天的那条问句「把三个 `factory_*` 键名改对」来答, 改完【仍然填不进去】⇒ 因为 `measured` 这个字段本身还不存在** ★ ⇒ ★**答了也白答** ★ |
| ★**②** ★ | ★**ISS-397 页 §1 表逐字断言「★三个 `measured` 槽位至今不存在★ ⇒ ★**槽位已开、内容为空**★」★ ⇒ ★**本机实读: 槽位【没开】, 不只是空** ★ | ★⇒ ★**这是「已签收页里的一句假话」⇒ 下一个读闸的人按这句去填, 会填进一个不存在的键** ★ |
| ★**③** ★ | ★**ISS-390 页 §3.1 乙-1 的回填格 `HW/PCB/BOARD_ONEPASS_FTS_SINGLE_ROW_LAND_TRUTH.md` 机器块 `keepout_dwg`「那一行」⇒ 该页机器块里 `keepout_dwg` 的真身是 `parts.FTS-104-01-F-S.keepout_dwg`, 值是一串【官网 URL 字符串】⇒ ★**在那一格「逐项写 X/Y/Z 实测」= 把来源 URL 覆盖掉** ★ | ★⇒ ★**这是「键名存在 ⇒ 机器查不出来 ⇒ 人照填 ⇒ 填错地方还不报错」的最典型样本 ⇒ 即 D 类误指** ★ |

---

## ★§1 · 扫描范围与指针形态定义 ★

### ★§1.1 · 扫描范围 (★闸自己扫, 不许把扫描结果写死 — P1★) ★

| ★范围★ | ★目录★ | ★处置★ |
|---|---|---|
| ★**主范围** ★ | ★`MECH/` 下全部 `.md` (★58 页·跳过隐藏文件★) ★ | ★**计数** ⇒ A 类之外的条数 > 0 ⇒ 判红 ★ |
| ★**旁证范围** ★ | ★`HW/PCB/` + `SW/` 下全部 `.md` ★ | ★**只列不改** ⇒ 别的域的条目标【归属域】+ 逐字改法建议, ★**本单一件都不许改** ★ |
| ★**本闸自产登记页 (★排除·公开披露★)** ★ | ★`MECH/BOARD_ONEPASS_MACHINE_BLOCK_POINTER_AUDIT.md` (★本页自己★) ★ | ★★**排除**★ ⇒ ★**理由: 这一页是【本闸的账本】, 它必须逐字引用那些死指针来登记 ⇒ 若把它也当指针扫, 每改一次账本悬空条数就跟着漂 ⇒ 违反 P6「条数不许随时间漂移」** ⇒ ★**排除项在闸的输出头部逐字打印 ⇒ 公开可审, 不是藏起来的** ★ |
| ★**引文登记标记 (★通用机制★)** ★ | ★任何一行末尾加 `【指针登记】` ★ | ★★**该行 = 引文/登记, 不是活指令 ⇒ 不计入指针统计**★ ⇒ ★**别的页要引用死指针时, 加这个标记即可, 不用改闸源码** ★ (★全仓 grep `【指针登记】` = 0 处 ⇒ 无撞名★) ★ |

★**机器块识别 (★不许用正则硬啃 JSON★)**: ★每页 ```json 围栏块 ⇒ `json.loads` 整体解析★
★**⇒ 解析成功 = 机器块; 解析失败且首字符是 `{` / `[` = 坏机器块 ⇒ fail-closed 报错退出; 解析失败且首字符不是 `{` / `[` = 片段 (illustrative snippet) ⇒ 忽略但计数** ★
★**当前盘面: 53 块机器块 + 14 块片段 + 0 块坏机器块** ★(`[实测]`)

### ★§1.2 · 指针形态 (★机器可判, 不用人眼★) ★

| ★形态★ | ★例★ | ★判定口径★ |
|---|---|---|
| ★**P1 同页 JSON 路径型** ★ | ★`dimensions.factory_seat_body_x_4pos.measured` ★ | ★在**本页**机器块里逐段下钻 ⇒ 段段存在 ⇒ 可解析; 任一段不存在 ⇒ 悬空 ★ |
| ★**P2 跨页 JSON 路径型** ★ | ★`MECH/B.md` 的 `three_quantities.seat_body_width_x.measured_value` ★ | ★**必须写得出目标页** ⇒ 在目标页机器块里下钻 ★ |
| ★**P3 页 + 机器块 + 裸键型** ★ | ★`HW/PCB/…FTS_SINGLE_ROW_LAND_TRUTH.md` 机器块 `keepout_dwg` 那一行 ★ | ★键在目标页机器块的【顶层】⇒ A; 在【深层】⇒ A + 报实际落点; 落点是【标量】且该格在【回填列】⇒ D 误指; 键根本不存在 ⇒ B 悬空 ★ |
| ★**P4 表格行定位型** ★ | ★`§1 表第 1 行` ★ | ★**"第 N 行"没写清填哪一格** ⇒ 归【歧义指针】C 类单列 ★ |
| ★**P5 自由文本引用型** ★ | ★`见 §4-③` / `见 §6` / `详见第 3 节` ★ | ★★**本闸明确不判它** (自然语言引用不算机器块指针) ⇒ ★**清单里分开列并说明为什么** ★ |
| ★**P6 引文登记型** ★ | ★任何一行末尾带 `【指针登记】` ★ | ★★**该行是引文/登记, 不是活指令 ⇒ 不计入指针统计**★ (★机制通用, 别的页要引用死指针时自己加标记, 不用改闸★) ★ |

★**判据正文 (★闸源码逐条对应★)**: ★`MECH/check_machine_block_pointer_resolvable.py` §`scan()` / `classify_pointer()` / `classify_bare()` / `build_ref_inheritance()` ★

### ★§1.3 · 目标页怎么算出来 (★这一段决定了本闸的准确度·逐条给规则★) ★

| ★规则★ | ★内容★ |
|---|---|
| ★R0 简称引用★ | ★行内出现某个扫描范围页 basename 的【唯一】后缀 (如 `MECH_SYNC` ⇒ `BOARD_ONEPASS_MECH_SYNC.md`) ⇒ 记为该页引用 (★要求全域唯一, 否则不算★) ★ |
| ★R1 表格行继承★ | ★同一张表里, 某行没写 `.md` 路径时 (常见写法 = 「同上」) ⇒ 继承本表内最近一个写过路径的行 ★ |
| ★R2 小节继承★ | ★行本身与所属表格都没写路径时 ⇒ 继承最近一个【写了路径的标题行】里的路径 ★ |
| ★R3 多解★ | ★同一指针在 ≥2 个候选页都能解析 ⇒ 判 E (目标页写不唯一) ★ |

### ★§1.4 · 根段过滤器 (★这一条把 2332 个噪声挡在外面★) ★

★**全仓带点号的反引号 token 共 **2558** 条 (MECH 1053 / HW-PCB 589 / SW 916·裸扫) ⇒ 绝大多数是文件名 / 命令名 (`gen_pcb_netlist_board.py` / `F.Fab` / `onnx.utils.extract_model`) ⇒ 不是指针** ★
★**⇒ 过滤口径: ★一个路径型 token 只有在它的【根段】确实是某个候选页机器块的顶层键时才算指针; 否则一律不算** ★
★**⇒ 效果: 2558 → **主范围 115 条 + 旁证 28 条 = 143 条**指针 (可解析 + 悬空 + 歧义 + 误指 + 无归属全算) ⇒ **噪声挡掉约 94%** ★** (`[实测]`)

### ★§1.5 · P5 自然语言引用为什么单列 (★本闸不管这一类·但清单里要说明★) ★

★**`见 §4-③` / `见 §6` / `详见第 3 节` 这类写法: ① 不是 JSON 路径; ② 目标是【章节】不是【机器块槽】; ③ 机器无法把「§4-③」下钻成一个 JSON 键 ⇒ 机器闸判不了它** ★
★⇒ ★**但它仍然是「动作做完但数据落不了地」的温床** ⇒ ★**本单把它列为【人工清账项】, 不进机器闸判据 (进闸 ⇒ 必然误报)** ★

---

## ★§2 · 悬空 / 歧义 / 误指 / 无归属指针清单 (★逐条: 源页 + 行号 + 指针逐字 + 目标页 + 判定 + 为什么 + 逐字改法建议★) ★

### ★§2.1 · B 悬空 (★键不存在★) —— 主范围 9 条 ★

| ★#★ | ★源页 : 行★ | ★指针逐字★ | ★目标页★ | ★为什么悬空★ | ★逐字改法建议 (★本单零改·交 main 拍★) ★ |
|---|---|---|---|---|---|
| ★B1★ | ★`MECH/BOARD_ONEPASS_FTS_VS_GENERIC_COURTYARD_DELTA.md` : **176** ★ | ★`dimensions.factory_seat_body_x_4pos.measured` ★ | ★同页 §6 `dimensions` ★ | ★`dimensions` 存在, 但 `factory_seat_body_x_4pos` 这个键**在本页机器块里不存在** (真键 = `seat_body_x_4pos`); 且 `seat_body_x_4pos` 下**也没有 `measured` 字段** ⇒ ⇒ **就算把前缀改对, 那一格依然不存在** ★ | ★见 ★§2.4 订正块候选文本 (★**必须与 ISS-397 §5.2 的 T2 追加块同批落**, 否则改完还是填不进去★) ★ |
| ★B2★ | ★同上 : **177** ★ | ★`dimensions.factory_seat_body_y.measured` ★ | ★同页 §6 `dimensions` ★ | ★同上 (真键 `seat_body_y`, 无 `measured` 字段) ★ | ★同上 ★ |
| ★B3★ | ★同上 : **178** ★ | ★`dimensions.factory_insulator_height_z.measured` ★ | ★同页 §6 `dimensions` ★ | ★同上 (真键 `insulator_height_z`, 无 `measured` 字段) ★ | ★同上 ★ |
| ★B4★ | ★`MECH/BOARD_ONEPASS_FTS_SEAT_SAMPLE_MEASURE_PLAN.md` : **46** ★ | ★`dimensions.seat_body_x_4pos.measured` ★ | ★`MECH/…FTS_VS_GENERIC_COURTYARD_DELTA.md` §6 ★ | ★★**前缀对了, 但 `measured` 字段在 ISS-393 页机器块里【不存在】** ★ ⇒ ★**这一条证明: 单改前缀不够** ★ | ★同上 (与 B1~B3 同批) ★ |
| ★B5★ | ★同上 : **46** ★ | ★`dimensions.seat_body_y.measured` ★ | ★同上 ★ | ★同上 ★ | ★同上 ★ |
| ★B6★ | ★同上 : **46** ★ | ★`dimensions.insulator_height_z.measured` ★ | ★同上 ★ | ★同上 ★ | ★同上 ★ |
| ★B7★ | ★`MECH/BOARD_ONEPASS_FTS_SEAT_SAMPLE_MEASURE_PLAN.md` : **199** ★ | ★`dimensions.factory_seat_body_x_4pos.measured` ★ | ★同上 ★ | ★ISS-397 页 §5.2 对 ISS-393 页 §5 的【逐字转述】⇒ 同样悬空 ★ | ★同上 ★ |
| ★B8★ | ★`MECH/BOARD_ONEPASS_FTS_SEAT_SAMPLE_MEASURE_PLAN.md` : **338** ★ | ★`dimensions.factory_seat_body_x_4pos.measured` ★ | ★同上 ★ | ★ISS-397 页 §9-④ 给 main 的问句里的【逐字转述】⇒ 同样悬空 ★ | ★同上 ★ |
| ★**B9** ★ | ★`MECH/BOARD_ONEPASS_FTS_SEAT_BODY_GEOMETRY.md` : **113** ★ | ★`degradation.fallback_b` ★ | ★同页 §6 `degradation` ★ | ★★**本单新发现★**: 该页机器块 `degradation` 的真键是 `path_a` / `path_b` / `blocked_on_external_reply` ⇒ **没有 `fallback_b`** (★`path_b.id` 的**值**才是字符串 `"fallback_b_caliper"`★); ⇒ §3.1 乙-3 那句「本页机器块 `degradation.fallback_b` 的 `status` 由 `armed` 改 `closed`」⇒ ★**`status` 字段真身是 `degradation.path_b.status`, 现值 `armed_for_preassembly_crosscheck` (★不是 `armed`★)** ★ | ★★**逐字改法 (★本单零改★)**: 「本页机器块 `degradation.path_b.status` 由 `armed_for_preassembly_crosscheck` 改 `closed`」★ ⇒ ★**⇒ 这一条一改, `OI-387-4` 才有得关** ★ |

### ★§2.2 · C 歧义 (★定位不到唯一格★) —— 主范围 3 条 ★

| ★#★ | ★源页 : 行★ | ★指针逐字★ | ★为什么歧义★ |
|---|---|---|---|
| ★C1~C3★ | ★`MECH/BOARD_ONEPASS_FTS_VS_GENERIC_COURTYARD_DELTA.md` : **176 / 177 / 178** ★ | ★`§1 表第 1 行 + §6 \`dimensions.factory_…\`` / `§1 表第 3 行 + §6 …` / `§1 表第 4 行 + §6 …` ★ | ★★**双重歧义**★: ① **只给了行坐标, 没给列坐标** ⇒ §1 表有 **6 列** (`#` / `几何量` / `现在的出处` / `换厂件后的新值` / `差` / `证据等级`) ⇒ 人填也会填歪; ② ★**更狠的是: §1 这张表【没有一个列是放实测值的】** —— `换厂件后的新值` 是标称档, `证据等级` 放的是等级不是数值 ⇒ ★**「填 §1 表第 N 行」这句话本身就指错了地方** ⇒ 实测档的正确落法是 **§1 之后追加一段** (★ISS-397 §5.2 的 T2 设计正是这么写的★) ★ |

★**逐字改法建议**: ★把「§1 表第 N 行 + §6 `…`」整格换成「★**§1 之后追加的实测档块 (§1-ISS397 追加式订正块) + §6 `dimensions.<量>.measured`★」★ ⇒ ★**行坐标与列坐标一起消掉** ★

### ★§2.3 · D 误指 (★键存在, 但不是要填的槽 / 或落点是标量★) —— 主范围 19 条 ★

★**D1 组 (★最要命的一组·本单新发现★)**: ★`MECH/BOARD_ONEPASS_FTS_SEAT_BODY_GEOMETRY.md` L111 与 L113 的 `keepout_dwg`★

| ★项★ | ★内容★ |
|---|---|
| ★指针逐字★ | ★§3.1 乙-1 的回填格: 「★**`HW/PCB/BOARD_ONEPASS_FTS_SINGLE_ROW_LAND_TRUTH.md` 机器块 `keepout_dwg` 那一行** ⇒ ★**逐项写 `X = <实测> / Y = <实测> / Z = <实测>` + 标注 `[实测]` + 记测量日期 + 记「样件 = 第几块」**★」★ |
| ★实际落点★ | ★`parts.FTS-104-01-F-S.keepout_dwg` (= `parts.FTS-102-01-F-S.keepout_dwg`) ★ |
| ★落点的值是什么★ | ★★**一串官网 URL 字符串**★: ★`"https://suddendocs.samtec.com/prints/fts-1xx-xx-xx-dx-xx-footprint.pdf + 官网 3D/CAD 下载 (THT 档外形尺寸 = [0数据])"`★ ⇒ ★**它不是「一行」, 它是「来源出处」** ★ |
| ★为什么是 D 误指★ | ★★**键名存在 ⇒ 机器查不出来 ⇒ 人照填 ⇒ 在那儿「逐项写实测」= 把来源 URL 覆盖掉 ⇒ 原始记录没了, 实测也没落进任何可读的格子** ★ ⇒ ★**「板只改一次」那一趟白测一遍** ★ |
| ★逐字改法建议★ | ★★**回填格必须改成【机器可写 + 有闸读】的槽** ⇒ 全仓唯一符合的是 `MECH/BOARD_ONEPASS_FTS_SEAT_SAMPLE_MEASURE_PLAN.md` §6 机器块 `three_quantities.{insulator_height_z, seat_body_width_x, seat_body_depth_y}.measured_value` / `measured_evidence` / `measured_readings` (§3 真槽登记表) ⇒ ★**原句里那句「机器块 `keepout_dwg` 那一行」应当改成指向该三槽, 并且【只追加不覆盖】** ★ |

★**D2 组**: ★`MECH/BOARD_ONEPASS_FTS_SEAT_BODY_GEOMETRY.md` L112 的 `body_geometry.*` ★
★⇒ **落点存在, 但 `body_geometry.<料号>.<量>_mm` 的子字段只有 `value` / `evidence` / `degradation_id` / `drawing_callout` / `cross_check` ⇒ 没有任何 `measured*` 字段** ⇒
★⇒ ★**在那一格「填实测」= 覆盖标称 `value` ⇒ 把官网标称档和实测档混成一档** ⇒ ★★**这正是 ISS-397 §5.1 明令不许做的事** (★逐字: 「老键 `value` / `evidence` 【不许动】⇒ 动它 = 把官网图和实测混成一档」★) ⇒ ★**⇒ 原句要么改成「追加 `measured_value` / `measured_evidence` / `measured_readings` 三个新键」, 要么直接指向 §3 的真槽** ★

★**D3 组 (★15 条·ISS-397 页对 ISS-393 页的三条真键的逐字转述★)**: ★`dimensions.seat_body_x_4pos` / `dimensions.seat_body_y` / `dimensions.insulator_height_z` 出现在 ISS-397 页 L46 / L188 / L199 / L338 与 ISS-390 页 L112★
★⇒ **根段 `dimensions` 是量容器, 但解析到的格子里只有标称字段 (`value` / `source` / `old_value` / `old_source` / `class` / `note` / `evidence` / `consumed_by`) ⇒ 没有任何 `measured*` 字段** ⇒
★⇒ ★★★**最要命的一条: ISS-397 页 L199 与 L338 提出的「把三个 `factory_*` 键名改对」这个修法本身, 改完就是 D 类误指** ⇒ ★**改对了键名, 还是落在只有标称值的格子上 ⇒ 还是填不进实测** ⇒ ★**⇒ ISS-397 §9-④ 那条挂了两天没人答的问句, ★**即使答「要改」, 也只能改到「不报错但填错地方」这一档** ⇒ 真正的答案必须同时落 T2 追加块 (把 `measured` 字段开出来) ★★★★

★**D4 组 (★1 条★)**: ★`MECH/BOARD_ONEPASS_FTS_SEAT_SAMPLE_MEASURE_PLAN.md` L172 / L177 的 `body_geometry.<料号>.<量>` (模板路径) 与 L193 的 `dimensions.<量>`★
★⇒ **模板路径解析得到的是「量容器 + 一层只有标称值的子树」⇒ 同 D2 组 ⇒ 逐字改法同 D2 组** ★

### ★§2.4 · ★加分项: §5 那 3 条死指针的逐字订正块候选文本 (★main 一句话就能拍, 不用再回头翻★) ★

★★**前提 (★两条必须同批落, 少一条都白做★)** ★★
★**前提①**: ★ISS-393 页 §6 机器块 `dimensions.<量>` 里【必须先追加】 `measured` / `measured_evidence` / `measured_readings` 三个键 (★这正是 ISS-397 §5.2 的 T2 设计, owner=main★) ⇒ ★**没有前提①, 下面三条改完仍然是 B 悬空** ★
★**前提②**: ★收样闸 `MECH/check_fts_seat_sample_plan.py` 【只读】ISS-397 页自己的 `three_quantities.*.measured_value` ⇒ ★**前提①落完, 收样闸依然红在 B.6** ⇒ ★**真闭环还差第三条: 要么同时填 ISS-397 页的 `three_quantities.*.measured_value`, 要么新建一道读 T1/T2 落点的闸 (★见 §5.3★)** ★

★★**订正块候选文本 (★追加式 · 老字一字未删 · 落在 ISS-393 页 §5 之后★)** ★★
> **§5-ISS400 追加式订正块 (2026-11-24 · ISS-400 · mech-lead)**: ★**上表 §5「量完填回哪一格」一列的三条指针键名有误** ★。本块只追加, **不改老字**。
> 原表写 `dimensions.factory_seat_body_x_4pos.measured` / `factory_seat_body_y.measured` / `factory_insulator_height_z.measured`; ★**本块机器块 `dimensions` 里没有 `factory_` 前缀** ⇒ 三条指针均**落不到任何键**。
> **订正后的三条落点 (逐字)**:
> ① 座体宽 X (4 位) ⇒ `dimensions.seat_body_x_4pos.measured` (★与 T2 追加块同批落★)
> ② 座体深 Y ⇒ `dimensions.seat_body_y.measured`
> ③ 绝缘体高 Z ⇒ `dimensions.insulator_height_z.measured`
> ★**「§1 表第 N 行」一列同时订正**: §1 两本对照账是**标称档**表, **没有放实测值的列** ⇒ 实测档落点是 **§1 之后追加的 §1-ISS397 追加式订正块**, 不是 §1 的某一格。
> ★**落点纪律 (★不许变★)**: 只**追加** `measured` / `measured_evidence` / `measured_readings` 三个键; **老键 `value` / `source` / `old_value` / `old_source` / `class` / `note` / `evidence` / `consumed_by` 一律不动** ⇒ ★**不许把实测写进标称 `value`** ★
> **证据等级升级条件**: 原始 3 读数 + 中位数 + 极差 + 量具 + 日期 + 样件号 + md5 全部在 `logs/iss397/fts_seat_sample_measurements.json` ⇒ 缺一件仍是 `[0数据]`。

★**本单零改 ISS-393 页正文 ⇒ 以上是【候选文本】, 落不落归 main (★见交卷页 B5 问句 1★)** ★

### ★§2.5 · E 无归属 (★写不出目标页 / 目标页写不唯一★) —— 主范围 20 条 ★

| ★分组★ | ★条数★ | ★条目 (★逐条★) ★ | ★性质★ | ★逐字改法建议 (★本单零改★) ★ |
|---|---|---|---|---|
| ★**E-a 路径型 · 目标页没写出来** ★ | ★**18** ★ | ★`MECH/BOARD_FRAME_DECISION_INPUT.md` L163 `board._pending` · `MECH/DEBUG_PORT_LAYOUT_CONSTRAINTS.md` L66 `board._pending` (★根段 `board` 在 STRUCT_CROSSCHECK 页 + SW 页都有 ⇒ 真·多解★) · `MECH/BOARD_ONEPASS_S10_FP_SWAP_IMPACT.md` L325 `led.full_height_bands` + `led.clearance_sweep` (★根在 MECH_SYNC 页★) · `MECH/BOARD_ONEPASS_S10_LED_SPEC_SYNC.md` L103 `zones.min_clearance` · `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` L255 `zones.min_clearance` · `MECH/ONETRIP_D_LED_G_PLACEMENT_CALIBER.md` L272 `zones.min_clearance` (★根在 STRUCT_CROSSCHECK 页★) · `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` L496~L500 的 `som.ref` / `som.pins_x` / `som.pins_y` / `som.width_mm` / `som.height_mm` / `som.position_mm` (★6 条·根在 STRUCT_CROSSCHECK 页★) · `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` L506~L510 的 `board.width_mm` / `board.height_mm` / `board.thickness_mm` / `board.layers` / `board.corner_radius_mm` (★5 条·根在 STRUCT_CROSSCHECK 页 + SW 页★) ★ | ★**人读得懂, 机器读不懂** ⇒ ★**要补一句「目标页 = XXX」** ★ | ★凡跨页指针, **把目标页全路径写进同一句里** (★例: 「`MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` 机器块 `zones.min_clearance`」★) ⇒ ★**闸就能下钻, 人也不会找错页** ★ |
| ★**E-b 路径型 · 多解** ★ | ★**1** ★ | ★`MECH/BOARD_ONEPASS_MECH_SYNC.md` L825 `openings[]` (★根 `openings` 在 MECH_SYNC 页与 STRUCT_CROSSCHECK 页都有 ⇒ 同一指针两个页都能解析★) ★ | ★**目标页写不唯一** ⇒ ★**必须写全路径** ★ | ★同上 ★ |
| ★**E-c 裸键型 · 顶层键只存在于另一个页** ★ | ★**1** ★ | ★`MECH/BOARD_ONEPASS_FTS_SEAT_SAMPLE_MEASURE_PLAN.md` L206 `body_geometry` (★顶层键 `body_geometry` 只存在于 ISS-390 页★) ★ | ★★**这一条正好是【真槽错位】的另一个侧面: ISS-397 页自己说「机器块 `body_geometry`」却没写那是哪一页的机器块 ⇒ 闸只能靠上下文继承猜★** ★ | ★写全路径: ★`MECH/BOARD_ONEPASS_FTS_SEAT_BODY_GEOMETRY.md` 机器块 `body_geometry`★ |

### ★§2.6 · 旁证范围 (★HW/PCB + SW·★只列不改·一件都不许改★) ★

| ★判定★ | ★条数★ | ★条目★ | ★归属域★ | ★逐字改法建议★ |
|---|---|---|---|---|
| ★B 悬空★ | ★1★ | ★`SW/EVT_CHARGE_CURRENT_CRITERION_CALIBER.md` L229 `evt_current_criterion_a` (目标页 `SW/EVT_TEMPLATE.md`) ★ | ★**sw-lead** ★ | ★补全路径或改键名 (★本单不判其对错, 只登记★) ★ |
| ★E 无归属★ | ★7★ | ★`HW/PCB/SCHEMATIC_REVIEW_READY.md` L198/L199 `board.design_settings.rules` / `board.design_settings.rule_severities` ; `SW/BOARD_ONEPASS_DEBUG_HEADER_FW_IMPACT.md` L201 `pins.csv` ; `SW/BOARD_ONEPASS_SW09_LANDING_PATCH.md` L331/L456 `items[]` ; `SW/ONETRIP_SW_SAMEBATCH_RENAME_LIST.md` L564 `gate.R6_TREE_FILES` ; `SW/RK3572_TARGET_COMPAT_V2.md` L270 `gates.log` ★ | ★**hw-lead / sw-lead** ★ | ★写全路径或改成文件名引用 (★`pins.csv` / `gates.log` 这两个是文件名, 不是槽名★) ★ |

---

## ★§3 · 真槽登记表 (★哪个页的哪个键是【唯一真槽】+ 谁消费它★) ★

### ★§3.1 · ★★全仓唯一的「三量实测回填格」★★ ★

| ★项★ | ★内容★ | ★证据★ |
|---|---|---|
| ★**宿主页** ★ | ★`MECH/BOARD_ONEPASS_FTS_SEAT_SAMPLE_MEASURE_PLAN.md` (ISS-397 收样作业包页) §6 机器块 `three_quantities` (L386 起) ★ | ★`[实测]`★ |
| ★**槽名 (三个)** ★ | ★`three_quantities.insulator_height_z` / `three_quantities.seat_body_width_x` / `three_quantities.seat_body_depth_y` ★ | ★`[实测]`★ |
| ★**每个槽里的可写字段** ★ | ★`measured_value` (★现在是 `null`★) / `measured_evidence` (★`"[0数据]"`★) / `measured_readings` (★`[]`★) ★ | ★`[实测]`★ |
| ★**同槽里的只读字段 (不许动)** ★ | ★`label` / `definition` / `nominal_value` (★**按料号分开的 dict**: `{"FTS-104-01-F-S": "5.0800", "FTS-102-01-F-S": "2.5400"}`★) / `nominal_evidence` / `nominal_callout` / `tolerance_evidence` / `target_evidence` / `degradation_id` ★ | ★`[实测]`★ |
| ★**★槽名拼法与 ISS-393 §5 写的连拼法都不一样★★** ★ | ★ISS-393 §5 写 `seat_body_x_4pos` / `seat_body_y`; 真槽叫 `seat_body_width_x` / `seat_body_depth_y`; 且真槽在**另一页** ⇒ ★**改前缀仍对不上** ★ | ★`[实测]`★ |
| ★**唯一消费者** ★ | ★★**`MECH/check_fts_seat_sample_plan.py`** ★: ★L45 `PAGE_REL = "MECH/BOARD_ONEPASS_FTS_SEAT_SAMPLE_MEASURE_PLAN.md"` · L75 `QUANT_KEYS = ("insulator_height_z", "seat_body_width_x", "seat_body_depth_y")` · L223 `tq = blk.get("three_quantities") or {}` · L258 `got = cell.get("measured_value")` (★**允许按料号开 dict**★) ★ | ★`[实测]`★ |
| ★**★全仓还有谁读 `measured*`?★** ★ | ★★**没有第二个**★ ⇒ ★`grep -rn "measured" --include=*.py MECH HW SW` ⇒ **只有 `MECH/check_fts_seat_sample_plan.py` 读 `measured_value` / `measured_evidence`** ★ (★`check_jdebug_arrangement_truth.py` 里的 `measured_token` 是另一个概念 — 装配排布对比, 不是尺寸实测★) ★ | ★`[实测]`★ |

### ★§3.2 · ★★三个候选落点, 没有一条通路把它们连起来★★ ★

| ★候选落点★ | ★槽位★ | ★有没有闸读★ | ★谁来填★ | ★结论★ |
|---|---|---|---|---|
| ★**T1** ★ | ★`MECH/BOARD_ONEPASS_FTS_SEAT_BODY_GEOMETRY.md` (ISS-390) `body_geometry.<料号>.<量>_mm` ★ | ★★**没有**★ ⇒ 且该格【没有 `measured*` 字段】⇒ 填了会覆盖标称 `value` ★ | ★ISS-390 §3.1 乙-2 (mech-lead) ★ | ★**D 误指** ★ |
| ★**T2** ★ | ★`MECH/BOARD_ONEPASS_FTS_VS_GENERIC_COURTYARD_DELTA.md` (ISS-393) `dimensions.<量>` ★ | ★★**没有**★ ⇒ 且该格【现在也没有 `measured*` 字段】⇒ 需先追加块 ★ | ★ISS-397 §5.2 T2 (owner=main) ★ | ★**B 悬空 (待 T2 落) ★** |
| ★**真槽** ★ | ★ISS-397 页 `three_quantities.*.measured_value` ★ | ★★**有**★ ⇒ `check_fts_seat_sample_plan.py` 唯一读它 ★ | ★?**没人写** ⇒ 三处动作表都没指它 ★ | ★**★唯一真槽, 但没人被指到它★** ★ |

★⇒ ★**★★这就是本单最核心的一句话: 「量完填回哪一格」这个问题, 在全仓有三个候选答案, 而唯一有闸读的那个 (真槽) 没有被任何一个动作表指到; 被指到的两个 (T1/T2) 一个是误指、一个还不存在 ⇒ ⇒ 「板只改一次」那一趟量完的数, 进不了任何闸读的格子。★★** ★

### ★§3.3 · 一个必须写下来的残留风险 (★`[实测]`★) ★

★**真槽的 `measured_value` 允许按料号开 dict (★闸 L258~L260 就是这么读的★) ⇒ 6 格 (3 量 × 2 料号) 能装下; 但同槽的 `measured_readings` 现在是**平铺的 `[]`** ⇒ **两料号的 3 读数没有分料号的落点** ⇒ ★**填的时候要么把 6 格的读数塞进一个平铺数组 (闸读不出分料号), 要么把 `measured_readings` 也改成按料号的 dict (★那是改 ISS-397 页机器块的结构, 属 main 地界★)** ★

---

## ★§4 · 新闸判据 (★`MECH/check_machine_block_pointer_resolvable.py`★) ★

| ★判据★ | ★内容★ | ★源码落点★ |
|---|---|---|
| ★**P1** ★ | ★扫描范围可复现 ⇒ 闸自己扫 §1.1 的范围 ⇒ **不许把扫描结果写死** ⇒ ★**本闸自产登记页被排除, 且该排除在报告头部逐字打印 (★公开披露, 不是藏★) ★** | ★`SCOPE_MAIN` / `SCOPE_EVID` / `SELF_LEDGER_PAGES` / `collect_pages()` / `scan()` / `report()` ★ |
| ★**P2** ★ | ★指针候选识别: P1/P2/P3/P4 四形态; ★**P5 自然语言引用明确排除在外** (闸自己声明「我不管哪一类」) ★ | ★`parse_path()` / `MBLOCK_CTX_RE` / `ROWLOC_RE` / `T6` 反向用例 ★ |
| ★**P3** ★ | ★可解析判定: JSON 逐段下钻 (含 `name[0]` / `name[]` / `name.*` / `<占位>` / list 按 `id` 选元素) ⇒ 命中 / 不命中 ⇒ ★**不许用子串命中当解析** ★ | ★`resolve_segs()` (★`"seat_body_x_4pos" in json.dumps(...)` 这种写法本闸里一处都没有★) ★ |
| ★**P4** ★ | ★分类输出: A / B / C / D / E 五类, 每条带【源页 + 行号 + 指针逐字 + 判定 + 目标页 + 为什么】 ★ | ★`classify_pointer()` / `classify_bare()` / `report()` ★ |
| ★**P5** ★ | ★★**「这一条指针指向的槽是不是实测槽」判定 (⇒ D 类)**: ★落在量容器根 (`dimensions` / `body_geometry` / `three_quantities` / `geometry` / `quantities` / `measurements` / `seat_body`) 上、且解析到的槽【没有任何 `measured*` 字段】⇒ 判 **D 误指** ⇒ ★**判据必须能独立跑出 D 类, 不能只报 B 类** ★ | ★`QUANT_ROOTS` / `subtree_has_measured()` / `classify_pointer()` / `T4` + `T9` 反向用例 ★ |
| ★**P6** ★ | ★★**本单已知的 3 条死指针必须被逐条点名报出** ★ ⇒ 且 ★**selftest 反向用例证明: 去掉其中一条 ⇒ 悬空条数就少一条 (⇒ 闸真在看这 3 条, 不是恒红)** ★ | ★`KNOWN_DEAD_PAGE` / 报告末尾「P6 逐条点名」段 / `T0-点名` + `T1-减条` 反向用例 ★ |
| ★**P7** ★ | ★零写板自证 ⇒ 闸自己跑的时候不得写板 / 不得改页 ⇒ 闸跑完板 md5 不变 (★`611b869e13518c3c023fb178f91a0075`★) ★ | ★闸内无任何写操作 (只 `open(..., "r")`) ★ |

### ★§4.1 · selftest 判据 (★`--selftest` ⇒ rc=0 · 末行逐字 `ALL TESTS PASS`★) ★

| ★#★ | ★用例★ | ★期望★ | ★实测★ |
|---|---|---|---|
| ★正向 1★ | ★T0-稳定: 真范围扫两遍 ★ | ★两次读数完全一致 (条数不许随时间漂移) ★ | ★绿★ |
| ★正向 2★ | ★T0-现状红: 真范围扫 ★ | ★A 类之外的指针 ≥ 1 (★现状就该红★) ★ | ★绿 (51 条)★ |
| ★正向 3★ | ★T0-点名: ISS-393 页 `dimensions.factory_*` ★ | ★**恰好 3 条**被点名 ★ | ★绿 (3 条)★ |
| ★反向 1★ | ★T1-减条: 把那 3 条里的一条从扫描范围里去掉 ★ | ★该页 B 条数 **正好少 1** ⇒ 证明闸真在看它 ★ | ★绿★ |
| ★反向 2★ | ★T2-跨页悬空: 造一条指向另一个页、键不存在的假指针 ★ | ★报 **B 悬空** ★ | ★绿★ |
| ★反向 3★ | ★T3-跨页可解: 造一条指向另一个页、键存在的假指针 ★ | ★判 **A 可解析** 且目标页 = 那个页 (★证明闸能跨页下钻, 不是只会查自己页★) ★ | ★绿★ |
| ★反向 4★ | ★T4-误指D: 造一条「键名存在但不是实测槽」的指针 ★ | ★报 **D 误指** (★证明 P5 真在跑★) ★ | ★绿★ |
| ★反向 5★ | ★T5-坏块: 改坏机器块 JSON (语法错) ★ | ★**报错退出 (fail-closed)**, 不许静默跳过 ★ | ★绿★ |
| ★反向 6★ | ★T6-排除自然语言: 塞 `见 §4-③` / `见 §6` / `详见第 3 节` ★ | ★**不算成指针** (★证明排除口径有效★) ★ | ★绿★ |
| ★反向 7★ | ★T7-空目录: 扫一个空目录 ★ | ★报「扫描范围内零指针」而不是崩 (★证明不会恒红★) ★ | ★绿★ |
| ★反向 8★ | ★T8-歧义C: 造一条「§N 表第 M 行」回填格 ★ | ★判 **C 歧义** ★ | ★绿★ |
| ★反向 9★ | ★T9-跨页实测槽: 跨页 + 量容器 + 目标槽【真的有】`measured*` 字段 ★ | ★判 **A** (★证明 P5 不是「见量容器就 D」★) ★ | ★绿★ |

★★**夹具纪律 (★踩过坑, 必看★)**: ★**夹具不许把「真件当前的指针文本」硬抄成常量当期望值** ⇒ ★**T0-点名 / T1-减条 的期望值一律从真文件现读现算** (★T1 是把真件那一页复制到沙盒、动态删掉命中行, 再比条数★) ⇒ ★**真件一改, 夹具不会假红/假绿** ★

★★**沙盒纪律**: ★反向用例一律落项目盘 `<root>/tmp/iss400/sbx/selftest/` (★不许写系统 `/tmp`·不许用硬链接★) ★

---

## ★§5 · 连带影响面 (★哪些既有闸钉了被改页的 md5 / 哪些闸会因为改指针而变红 / 哪些页把指针抄了三遍★) ★

### ★§5.1 · md5 pin 清单 (★改页 ⇒ 必须同批刷的 pin★) ★

| ★被改页★ | ★现 md5★ | ★谁钉了它★ | ★改页后会发生什么★ |
|---|---|---|---|
| ★`MECH/BOARD_ONEPASS_FTS_VS_GENERIC_COURTYARD_DELTA.md` (ISS-393) ★ | ★`0cb3ff2de940522b467ca3b01feda11c` ★ | ★★**`MECH/check_fts_seat_sample_plan.py` L71** ★ (★已验: 全仓只有这一处 py 钉它★) ★ | ★★**收样闸当场变红 (且是「md5 pin」红, 不是 B.6 红) ⇒ 与「现状就该红」混在一起 ⇒ 以后没人分得清「红是现状」还是「红是我刚改坏的」** ★ ⇒ ★**必须同批刷 pin (★改既有闸的常量 ⇒ 属 main 地界★)** ★ |
| ★`MECH/BOARD_ONEPASS_FTS_SEAT_BODY_GEOMETRY.md` (ISS-390) ★ | ★`15697668d10368e971710069c9b73994` ★ | ★★**`MECH/check_fts_seat_sample_plan.py` L70** ★ ★ | ★同上 ★ |
| ★`MECH/BOARD_ONEPASS_FTS_SEAT_SAMPLE_MEASURE_PLAN.md` (ISS-397) ★ | ★`f977bc86b52b3a43d32d4d06d2f8ddc4` ★ | ★★**没有任何闸钉它**★ (★全仓 grep 该 md5 只命中本页自身 + 交卷页, 无 py★) ★ | ★★**⇒ 这一页是【改指针不破 pin 的那一页】⇒ 真槽所在页最安全** ★ |

★**另一处连带**: ★`MECH/BOARD_ONEPASS_SIGNED_APPEND_LEDGER_DESIGN.md` (ISS-399 真相页) 的 §1.2 清账表 L93 / L94 与 §1.5 机器块 L301 / L307 **逐字登记了上面两枚 pin** ⇒ ★**改页 ⇒ 那张清账表也要同批刷新 (★否则它自己就陈旧了★)** ★

### ★§5.2 · 哪些闸会因为「改指针」而变红 ★

| ★闸★ | ★现状 rc★ | ★改指针后★ | ★为什么★ |
|---|---|---|---|
| ★`MECH/check_fts_seat_sample_plan.py` ★ | ★**1** (★红的是 B.6 一条·现状★) ★ | ★**1, 但红的理由会变** ★ | ★① 改 ISS-393 / ISS-390 页 ⇒ L70/L71 md5 pin 变红 (★新理由★); ② 就算 pin 刷了, B.6 仍红 (★除非真槽被填★) ⇒ ★**⇒ 收样闸【红】这件事在改完之后依然成立, 只是红的行号变了 ⇒ ★必须把「红在哪一条」写进交割** ★ |
| ★`MECH/check_fts_vs_generic_courtyard_delta.py` ★ | ★**0** ★ | ★**0** (★前提: 不改它的判据源码★) ★ | ★它管的是厂件 vs 库件, 不管指针可解析性 ⇒ ★**改 ISS-393 页若触发它的 md5 pin, 需另刷 (★本机实读: 它【不钉】ISS-393 页 md5, 钉的是三张表 + 闸自身★) ⇒ 不受影响** ★ |
| ★`MECH/check_fts_seat_body_geometry.py` ★ | ★**0** ★ | ★**0** (★前提: 不改它的判据源码★) ★ | ★它只查 `value` 非空, **不查 `measured`** (★ISS-397 §5.3 逐字登记过★) ⇒ **T1 落点填进去它也不会红** ⇒ ★**它拦不住「把实测写进标称 `value`」** ★ |
| ★**本单新闸** ★`MECH/check_machine_block_pointer_resolvable.py` ★ | ★**1** (★红的是现状·51 条★) ★ | ★**1 ⇒ 0** (★前提: 上面 B/C/D/E 全部改对★) ★ | ★★**它是唯一一道会因为「把指针改对」而变绿的闸 ⇒ ★它天然就是「改完了没有」的那道收据** ★★ |
| ★其余 8 道既有 MECH 闸 ★ | ★全 0 ★ | ★**全 0** ★ | ★本单零改它们 ⇒ 不受影响 (★B6 实跑证明★) ★ |

### ★§5.3 · ★★哪些页把指针抄了三遍 (★同一处缺陷被复制到三个域★) ★★

| ★处★ | ★谁抄的★ | ★抄的是哪一段★ |
|---|---|---|
| ★**ISS-393 页 §5 动作表 (死指针本体)** ★ | ★`MECH/BOARD_ONEPASS_FTS_VS_GENERIC_COURTYARD_DELTA.md` L176/L177/L178 ★ | ★`dimensions.factory_*.measured` 三条 ★ |
| ★★**转述 ①** ★ | ★★`MECH/BOARD_ONEPASS_FTS_SEAT_SAMPLE_MEASURE_PLAN.md` L199 (★「只登记·不许自己改」★) ★ | ★同一三条的逐字转述 ★ |
| ★★**转述 ②** ★ | ★★`MECH/BOARD_ONEPASS_FTS_SEAT_SAMPLE_MEASURE_PLAN.md` L338 (★给 main 的问句★) ★ | ★同一三条的逐字转述 ★ |
| ★★**转述 ③** ★ | ★★`HANDOFF/2026-11-24_mech-lead_ISS397_座体三量收样作业包.md` L91 ★ | ★同一三条的逐字转述 ★ |
| ★★**转述 ④ (★四份手抄本里的第四份★)** ★ | ★★`state/dispatch_briefs/ISS-400_mech_machine_block_pointer_resolvable_audit.md` L37/L38/L39 (★任务书本身★) + `state/_apply_20261124_2245_cronfb67af40_open_iss400.py` L20/L21/L104/L105 ★ | ★同一三条的逐字转述 (★⇒ **改完那页, 这两处也得同批刷, 否则下一趟的人又会被带偏★)** ★ |

★⇒ ★★**⇒ 改指针是【一次改、四个地方跟着改】的活, 不是改一行★ ⇒ ★★这正是必须走「追加式订正块 + 一道机器闸收据」的原因: ★**机器闸会自动把这几处一起点出来 (本单闸已把 B7/B8 两条转述单独列了出来)★★ ★

### ★§5.4 · 真闭环还差的那一步 (★写给 main 的一句话★) ★

★**即使 §2.4 的订正块 + T2 追加块都落了, 收样闸依然红在 B.6** ⇒ ★**因为 `check_fts_seat_sample_plan.py` 只读 ISS-397 页自己的 `three_quantities.*.measured_value`** ⇒
★⇒ ★**要么把真槽 (ISS-397 页 `three_quantities.*`) 也指给「量完填回哪一格」那一步 (★最省事: 三个动作表都指真槽, 放弃 T1/T2 两个无人读的落点★), 要么新建一道读 T1/T2 的闸** ⇒ ★**这是一条【要 main 拍的口径选择】, 本单不代拍 (★见交卷页 B5 问句 3★)** ★

---

## ★§6 · 实跑留证索引 ★

| ★留证★ | ★路径★ |
|---|---|
| ★本单全部命令输出 (★一条一文件★) ★ | ★`logs/iss400/cmd_*.log` ★ |
| ★新闸裸跑报告 (★完整 A~E 清单★) ★ | ★`logs/iss400/cmd_new_gate_bare.log` ★ |
| ★新闸 selftest 输出 (★12 条用例★) ★ | ★`logs/iss400/cmd_new_gate_selftest.log` ★ |
| ★既有 11 道 MECH 闸 rc (★逐条一文件★) ★ | ★`logs/iss400/cmd_existing_gate_*.log` ★ |
| ★边界自证 (★板三项指纹 + 11 闸 md5 + 三页 md5 + 零挂链 grep★) ★ | ★`logs/iss400/cmd_boundary_proof.log` ★ |
| ★收尾 (★merge / gate_check / check_brief_commands★) ★ | ★`logs/iss400/cmd_merge.log` · `cmd_gate_check.log` · `cmd_check_brief_commands.log` ★ |

★**本单边界自证摘要**: ★板 md5 `611b869e13518c3c023fb178f91a0075` (★mtime `2026-11-06 07:07:17.362193413` · size `4940213`·与基线逐字相同★) · ★ISS-393 / ISS-397 / ISS-399 三页 md5 与基线逐字相同★ · ★11 道既有 MECH 闸 md5 与基线逐字相同★ · ★`grep -c "check_machine_block_pointer_resolvable" state/gate_check.py` = **0** (★零挂链★)★ ★

---

## ★§7 · 本页的边界 (★再抄一遍, 免得被误读★) ★

★**本页只【登记 + 出改法】, 一件都不许代拍**: ★**零改既有页正文 · 零改既有闸判据源码 · 零写板 · 零落表 · 零挂链 · 零外发 · 不自签 `state/issue_log.yaml`** ★
★**§2 的「逐字改法建议」与 §2.4 的「订正块候选文本」都是【候选】, 落不落、怎么落、何时落 ⇒ 全部归 main** ★
★**ISS-399 的 M-A / M-B / M-C / M-D 四条仍归 main, 本页一条都没碰** ★
