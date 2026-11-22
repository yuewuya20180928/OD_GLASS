【项目总工派活 · 队列自动派活 · 闭环 ISS-300】你是 结构总工 (mech-lead)。

★★【主线口径】★★ 当前主线 = 绘制 PCB 图 (老板 2026-11-17 00:43)。但「板只改一次」铁律仍在 ⇒ **本单是【纯门禁类·零写板】活**, 不是「真动板那一趟」。

★**本单一句话**: 新建一道 MECH 侧【准出汇总闸】——「板只改一次」那一趟 S6 重出板当天, **一条命令**给出结构侧能不能出 Gerber 的结论 (现在这 6 道闸要人工一条条跑, 漏一条就没人知道)。

★**为什么值得做 (★main 2026-11-17 21:3x 本机实跑, 不是抄任何报告★)**:
- 「板只改一次」那一趟当天 MECH 侧必跑 6 道闸, main 21:3x 实跑**当前 6 道全 rc=0**: `MECH/check_board_frame_coords.py` · `MECH/check_demo_struct_truth.py` · `MECH/check_onepass_mech_sync.py` · `MECH/check_onepass_struct_crosscheck.py` · `MECH/board_port_opening_s6_check.py` · `MECH/check_mech_verdict_freshness.py`
- ★**这 6 道里有 2 道是「钉板 md5 闸」**(★板那一趟当天必然从绿转红·只有合法改板通道能走绿·ISS-296 已把通道建好★) ⇒ ★**当天最容易误读成「板改坏了」→ 去改板凑绿 → 板 md5 变第二次 → 整趟白跑★**
- ⇒ ★**一条命令 + fail-closed 语义 = 当天不会漏、不会误读★** (★这正是 MEMORY 铁律④「新闸交卷后第一件事不是验收通过, 是挂进门禁链 + 让它真跑一次」★)

★**本单只做这一件 (★3 小步·不许扩★)**:
① 新建 `MECH/check_onepass_mech_release.py` = **聚合跑**上面那 6 道闸, **逐条打印每道的 rc + 汇总 rc**
   - ★**fail-closed 同款语义 (★照 `state/gate_check.py` 里 `run_external_gate` 的写法, 不自创★)**: 脚本不存在 / 跑不起来 / 超时 ⇒ **一律算闸红** ⇒ ★**绝不「没跑就当过」★**
   - ★**任一道红 ⇒ 汇总闸红 ⇒ 且必须点名是哪一道红了 (不许只出一个总 rc)★**
   - ★**不许改那 6 道闸本体的任何一行 (只聚合·判据不许动)★**
② **反向用例 (★不许只做「跑一遍全绿」的假闸★)**: 在**沙盒副本**里把其中任一道弄红 (★例: 篡改 1 个开口坐标常量 / 删 1 条防漂锚点 / 把 1 条落位改成越界值★) ⇒ ★**汇总闸必须红 + 必须点名那道红了★** ⇒ 恢复 ⇒ 必须回绿 ⇒ **真盘一个字节不许动**
③ **`--selftest` 模式**: 汇总闸自己的自检 (★至少 3 条: ① 6 道都在清单里 (漏一道 ⇒ 红) ② 任一道红 ⇒ 汇总红 ③ 脚本不存在 ⇒ 算红不是跳过★)

★**边界 (★写在这里是为了防止越界★)**:
- ★**零写板**: 板 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413` + `.kicad_pro` `3e504d2be83152e337949723e909be1b` + 网表 `37f62ac3f0b81d92ca7d48fdea717f07` + 脚表 `a4270120454aedf7a23c92cd8985c8a6` + BOM `5d02bece9477ffce5fbe0193c7d5cce4` ⇒ **六件逐字节不变**
- ★**零落表** (不许动 `HW/SCHEMATIC_LANDING_V1_LANDED.md`)
- ★**不许改那 6 道闸本体** · 不许改 `state/gate_check.py` (★挂闸是 main 的活★) · 不许碰 `HW/` 与 `SW/` 地界 · 不许改 `state/fragments/hw.yaml` / `state/fragments/sw.yaml`

★**验收读数 (★一条不许将就★)**:
- `python3 MECH/check_onepass_mech_release.py` ⇒ rc=0 且**逐条列出 6 道各自的 rc**
- `python3 MECH/check_onepass_mech_release.py --selftest` ⇒ rc=0
- ★**6 道闸本体各自读数不许变** (今天全 rc=0): `python3 MECH/check_board_frame_coords.py` · `python3 MECH/check_demo_struct_truth.py` · `python3 MECH/check_onepass_mech_sync.py` · `python3 MECH/check_onepass_struct_crosscheck.py` · `python3 MECH/board_port_opening_s6_check.py` · `python3 MECH/check_mech_verdict_freshness.py`
- `python3 state/merge.py` ⇒ rc=0 · `python3 state/gate_check.py` ⇒ rc=0 (★Q1 18/18★) · `python3 state/issue_check.py` ⇒ rc=0
- ★**分片**: 走 `python3 state/frag_write.py --agent mech-lead` (★原子写·禁止 `open(p,"w")★) ⇒ `interface_claims` ≥3 条 + `needs_from` ≥1 条 (给 main, 只列事实与代价, 不替 main/老板拍板) + `status` 块 (phase=delivered · progress_pct=100 · health=绿) ⇒ `grep -c iss300 state/fragments/mech.yaml` ≥ 4
- ★**交卷单**: 新建 (文件名以 `2026-11-17_mech-lead_ISS300_` 开头 · 放在 `HANDOFF/` 目录) ⇒ **B1~B6 六块齐全** (结论摘要 / 验收标准自评逐条 / 证据分级 / 接口取值声明 / 未决项与卡点 / 自证复现命令) + 反向用例原样 rc + 边界自证

★**证据分级**: 固定五级 `[官网]` / `[实测]` / `[媒体]` / `[推算]` / `[0数据]` ⇒ 本单全是 `[实测]` (本机实跑读数), 实物 `[实测]` = 0 条。

★★**额外纪律**:
① 写分片必须用 `state/frag_write.py` (禁止 `open(p,"w")`)
② 只写本任务允许的文件 (`MECH/` 地界 + 自己的分片 `state/fragments/mech.yaml` + 自己的交卷单), 不碰别人的
③ 证据分级 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` 必须标
④ ★**不许外发任何邮件/询价/问询/采购 (老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料) ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ⇒ 没有"批一句可以发"这个选项**
⑤ 交卷前跑 `python3 state/merge.py` (rc 必须 0) && `python3 state/gate_check.py` (Q1 必须 18/18) 并把输出贴进回复
