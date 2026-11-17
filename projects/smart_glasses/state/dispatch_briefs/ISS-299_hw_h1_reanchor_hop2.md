【项目总工派活 · 队列自动派活 · 闭环 ISS-299】你是 硬件总工 (hw-lead)。

★★【主线口径】★★ 当前主线 = 绘制 PCB 图 (老板 2026-11-17 00:43)。但「板只改一次」铁律仍在 ⇒ **本单是【纯重锚类·零写板】活**, 不是「真动板那一趟」。

★**本单一句话**: 把 9 道「钉板 md5」闸里**唯一红的那一道**修到能挂进门禁链 —— 具体 = `HW/check_pin_function_labels.py` 的 H-1 重锚**第 2 跳**。

★**为什么是你这件事 (★main 2026-11-17 21:3x 本机实跑, 不是抄任何报告★)**:
- `python3 HW/check_pin_function_labels.py` ⇒ **rc=1 · 18 条缺陷** = 15 条脚表功能缺陷 (14 串号 + 1 缺脚) + **3 条 `MD5_CHANGED`**
  (★BOM/网表/脚表 的基线常量还停在 **ISS-257** 落表时的旧值 `94642d07…` / `e06c1dd6…` / `287e7861…` ★, 而真盘自 **ISS-283** 合法落表 (台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` §16.2 链头 L1353 · 2026-11-17 12:30:23) 起已是 `5d02bece…` / `37f62ac3…` / `a4270120…`★)
- `python3 HW/check_pin_function_labels.py --expect-known` ⇒ **rc=1** (★同样被那 3 条拖死★)
- `python3 HW/check_pin_function_labels.py --selftest` ⇒ **rc=1**: `❌ T5 前提不成立: 正常基线本应干净` + `❌ T11 前提不成立: 正常基线本应干净` (★**通道用例 10/10 通过 · 0 条通道失效** ⇒ reboard 通道本身是好的, 坏的是**基线陈旧**★)
- ⇒ ★**9 道闸里第 5 道是唯一红的 ⇒ main 不能把它挂进 `state/gate_check.py` 的 `EXTRA_GATES` (挂上去链当场红) ⇒ 「9 道闸通道齐 = 板那一趟开工前最后一道硬前置」现在卡在你这一道★**

★**本单只做这一件 (★3 小步 + 1 个附带小修★)**:
① **重锚基线常量**: `HW/check_pin_function_labels.py` 的 `PROTECTED_MD5` 里 **网表 / 脚表 / BOM 三个基线** = 改成 **ISS-283 落表后的真盘实测值**
   ⇒ 网表 `37f62ac3f0b81d92ca7d48fdea717f07` · 脚表 `a4270120454aedf7a23c92cd8985c8a6` · BOM `5d02bece9477ffce5fbe0193c7d5cce4`
   ⇒ ★**板 / `.kicad_pro` 两个基线一个字节都不许动** (硬保护: 板 `611b869e13518c3c023fb178f91a0075` · `.kicad_pro` `3e504d2be83152e337949723e909be1b`)★
   ⇒ ★**重锚的是【脚本里写的基线常量】, 不是那三个文件本身 ⇒ 三个文件必须逐字节不变★**
② **锚链追加第 2 跳**: 在同一脚本的 `MD5_ANCHOR_CHAIN` 里**追加**一跳 (★照第 1 跳的字段形状: 单号 / 旧 md5 / 新 md5 / 落表时刻 / 台账行号★) ⇒ ★**新基线值必须能在落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` 里查到, 否则该闸的 ④b 台账对账会红★** ⇒ ★**第 1 跳的历史值一个字不许抹 (历史事实·逐跳留痕)★**
③ **不许做的事 (★写在这里就是为了防止你顺手"修绿"★)**: 不许改判据方向 / 不许改那 15 条脚表功能缺陷的冻结快照 / **不许为了让 `--selftest` 变绿而放宽 T5/T11 的前提** (★T5/T11 的前提就是「正常基线必须干净」·那是承重的·放宽 = 判据被松开 = 假闸★) / 不许改 `state/gate_check.py` (★那是 main 的活★)
④ **附带一条小修 (★不做的话 main 挂链时会看漏★)**: ★**ISS-297 的交卷单 (文件名以 `2026-11-17_hw-lead_ISS297_` 开头 · 放在 `HANDOFF/` 目录) 的标题不含 `state/gate_check.py` 的标准 B2/B3/B4 关键词 ⇒ 最新一份自己评不满 6/6 (现在靠回退到 ISS-283 那份计分)★** ⇒ ★**在该交卷单末尾【追加】3 行标准标题行 (★只追加·不许改 B0~B6 老字★) ⇒ 复跑 `python3 state/gate_check.py` 确认最新一份自己也 6/6★**
   - 标准关键词在 `state/gate_check.py` 的 `REQUIRED_BLOCKS`: B2 = `验收标准自评` / `自评` / `验收标准` · B3 = `证据分级` / `证据等级` / `证据` · B4 = `接口取值` / `接口声明` / `interface_claims` / `接口请求`

★**验收读数 (★目标态·一条不许将就★)**:
- `python3 HW/check_pin_function_labels.py` ⇒ rc=1 但**恰好 15 条** (★15 条脚表功能缺陷一条不许少/不许多★ · ★3 条 `MD5_CHANGED` 必须消失★)
- `python3 HW/check_pin_function_labels.py --expect-known` ⇒ **rc=0**
- `python3 HW/check_pin_function_labels.py --selftest` ⇒ **rc=0** (★T5/T11 前提自然成立·不许改前提★)
- ★**其余 8 道闸读数不许变**: `HW/check_fsin_rootcause.py` rc=0 · `HW/check_g1a7_selection_landed.py` rc=0 · `HW/check_onepass_commit_order.py` rc=0 · `HW/check_onepass_preflight_coverage.py` rc=0 · `HW/check_workpack_state_values.py` rc=0 (★前 5 道各自 `--selftest` 也须 rc=0★) · `HW/board_reboard.py --selftest` rc=0 (10/10) · `MECH/check_board_frame_coords.py` rc=0 · `MECH/check_demo_struct_truth.py` rc=0 · `SW/tools/check_onepass_sw_sync.py` rc=0
- `python3 state/merge.py` ⇒ rc=0 · `python3 state/gate_check.py` ⇒ rc=0 (★Q1 18/18★) · `python3 state/issue_check.py` ⇒ rc=0
- ★**零写板 / 零落表自证 (md5 + mtime 双证)**: 板 `611b869e13518c3c023fb178f91a0075` (mtime 仍 `2026-11-06 07:07:17.362193413`) · `.kicad_pro` `3e504d2be83152e337949723e909be1b` · 网表 `37f62ac3f0b81d92ca7d48fdea717f07` · 脚表 `a4270120454aedf7a23c92cd8985c8a6` · BOM `5d02bece9477ffce5fbe0193c7d5cce4` ⇒ ★**六件逐字节不变★**
- ★**分片**: 走 `python3 state/frag_write.py --agent hw-lead` (★原子写·禁止 `open(p,"w")★) ⇒ `interface_claims` ≥3 条 + `needs_from` ≥1 条 (给 main, 只列事实与代价, 不替 main/老板拍板) + `status` 块 (phase=delivered · progress_pct=100 · health=绿) ⇒ `grep -c iss299 state/fragments/hw.yaml` ≥ 4
- ★**交卷单**: 新建 (文件名以 `2026-11-17_hw-lead_ISS299_` 开头 · 放在 `HANDOFF/` 目录) ⇒ **B1~B6 六块齐全** (结论摘要 / 验收标准自评逐条 / 证据分级 / 接口取值声明 / 未决项与卡点 / 自证复现命令) + 反向用例 + 边界自证

★**证据分级**: 固定五级 `[官网]` / `[实测]` / `[媒体]` / `[推算]` / `[0数据]` ⇒ 本单全是 `[实测]` (本机实跑读数), 实物 `[实测]` = 0 条。

★★**额外纪律**:
① 写分片必须用 `state/frag_write.py` (禁止 `open(p,"w")`)
② 只写本任务允许的文件 (`HW/` 地界 + 自己的分片 `state/fragments/hw.yaml` + 自己的交卷单), 不碰别人的 (`MECH/` / `SW/` / `state/fragments/mech.yaml` / `state/fragments/sw.yaml` / `state/gate_check.py` 一律不许改)
③ 证据分级 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` 必须标
④ ★**不许外发任何邮件/询价/问询/采购 (老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料) ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ⇒ 没有"批一句可以发"这个选项**
⑤ 交卷前跑 `python3 state/merge.py` (rc 必须 0) && `python3 state/gate_check.py` (Q1 必须 18/18) 并把输出贴进回复
