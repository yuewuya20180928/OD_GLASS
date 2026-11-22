【项目总工派活 · 后继计划 · 闭环 ISS-205】你是软件总工 (agent=`sw-lead`)。

★★**第一步 (★不许跳过★)**: ★**本文件往下第 ★★`任务书原文 (advance.py 给的 brief 全文)`★★ 那一段, 就是 `state/advance.py --json` 给你这单的 brief 原文, ★**一字未改★** ⇒ ★**照它做, 不要自己另写一套** ★★

★★**本单的真实状态 (★main 2026-11-15 20:5x 逐个文件实测, 不是推测★)** ★★:
★**① 上一次派活 (2026-11-12 03:2x) 的会话已死 (status=failed), 交卷没人落账 ⇒ 停在 `fixing` 3.5 天 (★同病第 11~13 次复发★)**
★**② 半交卷 —— 核心产出已经在盘上, 别重做**:
  · ✅ `state/gen_kicad_sch.py` mtime **2026-11-12 03:36:22** (★第 280~287 行 = 位号加 `_1` 后缀的生成逻辑★ ·
    第 553 行 = 图↔表 ref 的精确映射★)
  · ✅ `HW/PCB/demo_mainboard.kicad_sch` + `demo_mainboard_p1..p10.kicad_sch` **11 个文件全部 mtime 2026-11-12 03:36**
  · ✅ ★**实测图上位号**: `(property "Reference" ...)` 共 **218** 个, 其中带 `_1` 后缀 **187** 个
  · ✅ ★**实测 sheet_instances**: 根页 + 10 个子页 **11/11 都有** (★原缺件已补上★)
★**③ 你这单真正缺的 (★只做这些★)**:
  · ❌ **问号归零没有实测**: 投产包 BOM `HW/PCB/production/doc/demo_mainboard-kicad-bom.xml` 仍是 11-11 17:25 的旧件,
    带 `?` 的行 **186** ⇒ ★**这是 brief ⑦ 说的「投产包变旧 = 预期中间态」, 不是你没做完★** ⇒
    ★**你要做的是: 重新导出一次 BOM 并实测「带 `?` 的行数 = 0」, 把那个数字贴进交卷报告** ★
  · ❌ 三条闸 (ERC / pinfull / loadable) 的实测输出没贴
  · ❌ 受保护文件 md5 的实测对照没贴 (板 / 网表 / 脚表 / `.kicad_pro`)
  · ❌ 没有交卷报告 ⇒ ❌ `state/fragments/sw.yaml` 没登记本单
★**④ 一条硬要求**: ★**你必须自己跑一遍导出/校验, 不许拿 main 的转述当结论** ★

★**纪律 (★一条都不许破★)** ★★:
① ★**写分片必须走 `state/frag_write.py`** (★禁止 `open(p,"w")`★)
② ★**只写本单允许的文件, 不碰别人的分片** (★hw.yaml / sw.yaml / mech.yaml 各归各的★)
③ ★**证据分级必标**: `[官网]` / `[实测]` / `[媒体]` / `[推算]` / `[0数据]` ⇒ ★**查不到就写 `[0数据]` + 降级方案, 不许编** ★
④ ★**不许外发任何邮件 / 询价 / 问询 / 采购** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★)
   ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ⇒ ★**没有「批一句可以发」这个选项** ★
⑤ ★**交卷前跑**: `python3 state/merge.py` (★rc 必须 0★) && `python3 state/gate_check.py` (★【Q1】必须 18/18★)
   ⇒ ★**把输出原样贴进回复** ★
⑥ ★**不许改 `state/issue_log.yaml` 的 status** (★那是 main 的活★) · ★**不许改 `PROJECT_TRACKER.md` §0 锁死表** ★
⑦ ★**主线口径 (★老板 2026-11-11 10:07★)**: 当前主线 = ★**硬件原理图 demo 绘制** ★ ⇒
   ★**不许碰 PCB 布线 / 布局 / 逃线 / 层数** ★
⑧ ★**不许整文件读大文件** (★只许 `grep` / `sed -n` 取你要改的那几行★) ★
⑨ ★**交卷 ≤ 25 行** (★结论先行 + 逐条复现命令输出 + 缺口清单★) ★


================== `任务书原文 (advance.py 给的 brief 全文)` ==================

★**【owner 已于 2026-11-12 03:2x 由 main (项目总工) 改派: `hw-lead` → `sw-lead`】**
  · ★**原因**: hw-lead 名额被 ISS-195 (★真在飞, 会话 `dc510f7c`, 03:17 仍在写★) 占住 ⇒ 铁律「一个 agent 同时只能
    一个写会话」⇒ 本单不能给 hw-lead; ★**而本单是 high + due 11-14 + 卡整链重出第 3 步** ⇒ 干等会把最高优先级
    压在 medium 队列后面 ⇒ sw-lead 实测无在跑写会话 ⇒ 改派 sw-lead;
  · ★**冲突已核**: 与在飞的 ISS-195 文件交集 = 0;
  · ★**随之唯一的一处改动**: 分片写入目标从 `state/fragments/hw.yaml` 改成 `state/fragments/sw.yaml`
    (★**不许写别人的分片**★) ⇒ ★**其余判据 / 边界 / 验收一条都没动** ★

★**目标 (★内部活·不是原厂的事·不是 PCB 布线/布局类★)**: ★**在 `state/gen_kicad_sch.py` 里给位号加 `_1` 数字后缀** ⇒ ★**让 KiCad 导出的 BOM 不再带 `?`** ⇒ ★**★只改原理图生成器, 不碰板/网表/BOM台账★★**

★**★① 根因 (★main 已实测坐实·你不用重查·零例外★)★**:
  · ★**KiCad 判「已标注」的条件 = 【位号最后一个字符是数字】** ⇒ ★**末字符是字母 ⇒ 判未标注 ⇒ BOM 里打 `?`**
  · ★**实测: 带 `?` 的 186 个位号末字符 100% 是字母; 不带 `?` 的 32 个末字符 100% 是数字**
  · ★**★旧记录说的「根因是下划线命名」是错的 ⇒ 不要去动下划线★★**
  · ★**★解法: 加 `_1` 后缀 (★已在本机副本上跑通: 问号行数 0 + annotation errors 警告消失 + 零撞名★★)**
  · ★**完整证据: `HW/PCB/KICAD_REF_QUESTIONMARK_ROOTCAUSE.md` (★建议先读这一份, 里面有全部对照实验★)**

★**★② 要改哪三处 (★必须同步, 少改一处 KiCad 就报 annotation errors★)★**:
  1. ★**子页的 `(property "Reference" "X" …)`** ⇒ `X` → `X_1`
  2. ★**子页的 `(instances … (reference "X") (unit 1))`** ⇒ `X` → `X_1` (★KiCad 导出 BOM 实际读这里★)
  3. ★**`lib_symbols` 里的 `(symbol "SYM_X" …)` + 两个子符号 `SYM_X_0_1` / `SYM_X_1_1`** ⇒ 同步改
  ⇒ ★**落点 = `state/gen_kicad_sch.py` 的符号生成处 (★★改在产生点★★) ⇒ ★★不许手改 `HW/PCB/demo_mainboard*.kicad_sch` (★那是产物, 重跑就被冲掉★)★★**

★**★③ 顺带补 (★同一趟做完★)★**: ★**10 个子页都缺 `(sheet_instances (path "/<根页uuid>" (page "N")))`** ⇒ ★**根页有 `(sheet_instances (path "/" (page "1")))` 而子页一个都没有 ⇒ KiCad 官方模板的子页是有的** ⇒ ⇒ ★**在生成器里给每个子页补上 (★page 号 = 根页里那个 sheet 的 `(instances … (path "/<root>" (page "N")))` 的 N★)**

★**★④ 判据 (★六条, 缺一条不算交卷★)★★**:
  ① ★**`bash state/kicad.sh sch export bom -o /tmp/x.csv --fields Reference HW/PCB/demo_mainboard.kicad_sch` ⇒ 输出里带 `?` 的行数 = 0** (★当前实测 **186**★)
  ② ★**导出时 stderr 【不许出现】`schematic has annotation errors`** (★当前实测出现★)
  ③ ★**`python3 state/check_sch_erc.py` rc=0** · ★**`python3 state/check_sch_pinfull.py` rc=0 (★K=0★)** · ★**`python3 state/check_sch_loadable.py` rc=0**
  ④ ★**位号唯一性: 218 个位号无重复** (★实测加 `_1` 后缀零撞名, 你落完再核一遍★)
  ⑤ ★**受保护文件 md5 全未变**: 板 `611b869e13518c3c023fb178f91a0075` · 网表 `c78f991283cc82d56c8e3dd31657c785` · 脚表 `4814617e22b567d76164e56bc5e39dc8` · `.kicad_pro` `3e504d2be83152e337949723e909be1b`
  ⑥ ★**板里 186 个封装位号 【本单不许动】** ⇒ 原理图位号与板位号此刻【会不一致】⇒ ★**这是【预期的中间态】** (★板侧改动属整链重出第 1 步★) ⇒ ★★**不许因此去改板★★**

★**★★⑤ 交卷 (★≤8 行·别写长篇★)**: ① 问号行数 (前→后) ② annotation errors 警告 (前→后) ③ 三条闸 rc ④ 位号唯一性实测 ⑤ 板/网表/脚表/.kicad_pro md5 未变的实测 ⑥ 改了哪个文件 + 【原理图与板位号暂时不一致】的说明 ★★

★**★★⑥ 边界 (★再强调一次★)**: ★**不许碰**: `HW/PCB/demo_mainboard.kicad_pcb` · `HW/netlist_v1.csv` · `HW/netlist_v1_pins.csv` · `HW/PCB/demo_mainboard.kicad_pro` · `HW/BOM_v1.csv` · `HW/PCB/FET3572C_PIN_TABLE.csv` · `state/issue_log.yaml` · `PROJECT_TRACKER.md` §0 · 别人的分片 ⇒ ★**只许写**: `state/gen_kicad_sch.py` · `HW/PCB/demo_mainboard*.kicad_sch` (★产物·由生成器重跑产生★) · `HW/PCB/PIN_REALITY_GAP.md` (★若生成器会重跑它★) · `HANDOFF/` 交卷报告 · ★**必要时** `state/fragments/sw.yaml` (走 `frag_write.py`·只许新增本单相关条目★)
★**★不许发任何邮件 / 询价 / 问询 (★老板 2026-11-12 02:02: 不再发信, 全靠自己查资料★) ⇒ 所有资料一律【自己网上查】+ 标证据等级 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` ⇒ ★**查不到就写 `[0数据]` + 已知缺口 + 降级方案 ⇒ 没有「批一句可以发」这个选项★★**

★**★★⑦ ★★本单交卷时【投产包一定会变旧】⇒ 这是【预期中间态】, 不是你没做完★★** ★★
★**实测依据**: `state/chain_gate.py` 的 `check_sch_src_pack()` 校【投产包 `doc/sch_src/` 里每个文件的 md5 == 源文件 md5】⇒ ★**你一改原理图 ⇒ 源变新 · 投产包还是旧 ⇒ `chain_gate.py` rc=1** ★★
★**★所以交卷时照下面二选一 (★别自己去纠结 rc★)** ★★:
  ★**(A)【推荐】本单一并重出投产包**: 跑 `bash state/gen_production_pack.sh` ⇒ ★**然后 `chain_gate.py` 必须 rc=0** (★**注意**: 这个脚本会 `rm -rf` 整个 `HW/PCB/production/` ⇒ ★**跑之前确认没人在飞别的单碰投产包★)**
  ★**(B) 或者: 不跑, 但在交卷报告里明写【投产包已变旧, 待 main 重出】** ⇒ ★**main 验收时会替你重出** ★★
★**★★无论 (A) 还是 (B), 交卷报告都必须写一句: 「投产包 sch_src 与新原理图的 md5 是否已同步」★★**

★**★★⑧ ★★地界提醒 (★你是软件总工, 但这单改的是硬件生成器★)★★** ★★
★**`state/gen_kicad_sch.py` 历史上一直是 hw-lead 在改 (★`state/fragments/hw.yaml` 里 440 行提到它★)** ⇒ ★**本单改派给你是因为【hw-lead 名额被 ISS-195 占着 + 文件交集实测 = 0 + 你空闲】⇒ 改派是对的** ★★
★**★但你只许【按本 brief 的字面指令改】**: ★**答案(main 03:0x 实测)已经全算好塞在上面的判据里了** ⇒ ★**不许自己重新设计位号规则** (★别去改 `RAIL_*`/`NET_*` 的保留口径★) · ★**不许顺手改别的生成器逻辑** (★`gen_bom.py` / `gen_netlist.py` / `gen_pcb_netlist_board.py` 一律不许碰★) · ★**不许把"顺手改一下"当改进** (★本单只求【问号清零 + 三条闸绿 + md5 不变】三个判据, 别的都不许动★) ★★
