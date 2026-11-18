【ISS-336 · mech-lead · ★★「板只改一次」那一趟的【板框冻结闸 U-1 机器闸实现】★★ · ★★对标 ISS-316 §2 已出好的 C1~C7 七条判据 + 6 条反向用例 (★设计稿已在盘·★机器闸文件至今【不存在】★)★★ · ★★纯新建闸类 · 零写板 · 零落表 · 零改既有闸 · 零改 `state/gate_check.py`★★】

★**这是 main 2026-11-19 00:1x 新开的单 (job cron fb67af40「ARS45 队列自动派活」)· ★派活前置三条 (★全部本机实读·不许抄任何文档里的旧数★)**:
★**① `python3 state/advance.py --json` ⇒ `internal: []`** ⇒ ★**三个总工名下零 `open` 零 `fixing`** (★hw-lead 名下 ISS-334 是 `fixing` 且**有活会话在跑** ⇒ 本轮不碰 hw-lead★)
★**② 老板 2026-11-17 00:43「接下来的目标是绘制 PCB 图」⇒ PCB 线可派**
★**③ ★★「板只改一次」铁律 ⇒ 本单只出【纯新建闸 + 作业包】, 一个字节都不许写板★**

---

## ★★★【① 病灶 (★本机实读·2026-11-19 00:0x★)】★★★

★**「板只改一次」那一趟, 【板框冻结闸】是它的【第一前置】—— 而这道闸【今天在盘上不存在】★**

★**ISS-316 (verified) 已经把判据【设计稿】全部出好了, 但机器闸一直没建**:
- ★**交卷页**: `HANDOFF/2026-11-18_mech-lead_ISS316_板那一趟结构侧输入包.md` · ★**§2 = 冻结闸判据 + 6 条反向用例** ★
- ★**决策包**: `MECH/BOARD_FRAME_FREEZE_DECISION_PACK.md` · ★**§2 的 C1~C7 七条判据 (★L167~L173★) + RC-1~RC-6 六条反向用例 (★L182~L187★) ★★已经逐条写好, 阈值一律只读 `MECH/service_port_check.py` 与 `MECH/board_frame_feasibility.py` 的现值★★**
- ★**★本机实读确认: ★★`ls MECH/check_board_frame_freeze_gate.py` ⇒ 【不存在】★★ ⇒ ★★全仓 `grep -rn "check_board_frame_freeze_gate"` ⇒ 只在 `MECH/ONETRIP_MECH_DIFF_OWNERSHIP.md` / ISS-319 的交卷单 / 决策页 / 台账里作为「待建的闸」被【引用】, 【没有文件本体】★★**

★**★★后果 (★ISS-319 §D-2-1 已逐字写明·★本机实读 `HANDOFF/2026-11-18_mech-lead_ISS319_差集归属与电芯订正影响面.md` L44 + `MECH/ONETRIP_MECH_DIFF_OWNERSHIP.md` L123★)★★**:
> ★**「闸 `proto_pcb_freeze_gate` 永远不满足 ⇒ 板那一趟没有第一前置; HW 作业包硬顺序首行是「网表」而不是「板框冻结」⇒ S1~S8 可在 U-1 未拍时开工 ⇒ 板 md5 第二次变 ⇒ Gerber / 投产包 / 留证链全部作废重做 = 2-4 周 + ¥4-8K」★★**

★**★而 main 已经在 2026-11-18 09:4x 把决策码 M-B18 的 (a) 项裁成【路 B = 做成机器闸】★★ (★本机实读 `DECISION_INDEX_2026-11-18.md` §E-1 第 2 行 + `DECISION_PENDING_2026-11-16.md` 对应段★)** ⇒ ★★**裁都裁了, 闸却一直没建 ⇒ 【裁了不做 = 裁了跟没裁一样】★★**

★**★★本机的真实读数 (★2026-11-19 00:0x 本机实跑/实读★)★★**:
```
★ls MECH/check_board_frame_freeze_gate.py                ⇒ 【不存在】★★
★python3 -c "import sys; sys.path.insert(0,'MECH'); import board_frame_feasibility as B; print(len(B.all_rows()))"
   ⇒ 36            ★★36 档矩阵本机可跑, 字段: frame_id / layers / thk / can_open / red_reasons / holes / cavity / margins / weight_g ★★
★HW/PCB/BOARD_FRAME_CALIBER.md 的 `cal:FRAMES` JSON 块 ⇒ 现役帧 current_frame = "B160x100" (三套 id = B160x100 / F30A / P60x15)★★
★MECH/service_port_check.py ⇒ BASE / TOL={"fdm_part":0.30,"fdm_feat":0.25} / CRIT = 2*TOL["fdm_part"] = 0.60mm ★★判据阈值只读这里★★
★state/fragments/mech.yaml ⇒ needs_from 里有 key=proto_pcb_freeze_gate (to=main, since=2026-10-29, due=2026-10-31) ★★⇒ 这条 need【还没闭合】⇒ C7 今天【必然红】★★
```

★**★★C7 的真源在哪 (★本单必须用对·★不许自创一个来源★)★★**:
- ★**ISS-316 §2 的 C7 原文**: 「`proto_pcb_freeze_gate` 在 `state/issue_log.yaml` 里有【闭合记录】, 且该记录的答案里【逐字含帧 id + 板厚 + 层数】」★
- ★**★本机实读纠正一处: `state/issue_log.yaml` 的顶层只有 `_schema` / `_owners_legal` / `issues` 三项, 【没有 need 闭合记录表】⇒ ★★need 的闭合记录真源是【分片】: `state/fragments/mech.yaml` 的 `needs_closed` (★本机实读: 64 条·★每条含 key / iss / closed_at / closed_by / cls / action / reason / evidence / evidence_level / answer_key / answer_ref★) 与 `answers` (★79 条★) ⇒ ★★C7 应当读【分片侧】的闭合记录, 不是 issue_log★★**
- ★**★⇒ 本单必须【先实测确认】C7 到底读哪份文件才判得对 ⇒ 并在交卷页里【逐字写出它读的文件 + 读的字段 + 匹配口径】⇒ 不许写「读 issue_log」这种【盘上不存在的字段】★ (★这正是 ISS-281 §3-S10 那一类「引用了盘上不存在的字段」的病★)★**

---

## ★★★【② 本单要交的东西 (★6 件·全部新建·★不许改任何既有文件★)★★★

★**★交卷物 (6 件)★★**
1. ★**`MECH/check_board_frame_freeze_gate.py`** (★新建★) ⇒ ★**板框冻结闸本体** ★ ★**判据逐字照 ISS-316 §2 的 C1~C7, 阈值一律只读 `MECH/service_port_check.py` + `MECH/board_frame_feasibility.py` + `HW/PCB/BOARD_FRAME_CALIBER.md` 的 `cal:FRAMES` ⇒ 【不许写死一个自己的阈值表】★★**
2. ★**`MECH/check_board_frame_freeze_gate_selftest.py`** (★新建★) ⇒ ★**反向用例: ★RC-1~RC-6 六条逐条复现 + 1 条正向对照 ⇒ 全部在【沙盒副本】上跑, 真件一个字节不碰★** ★★(★RC-1 只拍帧 id 没拍板厚 · RC-2 板厚写 1.22 · RC-3 帧 id 写 P60x15 · RC-4 帧 id 写 B160x100 · RC-5 认领句 F30A 但 current_frame 仍 B160x100 · RC-6 need 闭合了但答案只有一句「板框已定」★)★★
3. ★**`MECH/ONETRIP_BOARD_FRAME_FREEZE_GATE.md`** (★新建★) ⇒ ★**一页说明: C1~C7 逐条对应到代码里哪一段 + 阈值来源表 + 反向用例表 + 「闸红了怎么办」+ ★★「今天这闸【应该红】还是【应该绿】」的诚实判断★★**
4. ★**`HANDOFF/2026-11-19_mech-lead_ISS336_板框冻结闸实现.md`** (★新建★) ⇒ ★**交卷页 (★对标 `HANDOFF/2026-11-18_mech-lead_ISS333_MECH侧位号可达性闸实现.md` 的 B0~B6 结构★) ★★B0 交付物清单 · B1 结论摘要 · B2 验收标准逐条自评 · B3 证据分级 · B4 接口取值声明 · B5 未决项与卡点 · B6 自证复现命令★★**
5. ★**`logs/iss336/`** (★新建目录★) ⇒ ★**全部机器原始输出 (★36 档实跑 / 七条判据逐条读数 / 六条反向用例 / 零写板双证 / 闸链复跑★)★★**
6. ★**`state/fragments/mech.yaml`** (★只写这一份·★必须走 `state/frag_write.py` 原子写★) ⇒ ★**`--add-artifact` ≥3 · `--add-claim` ≥2 · `--status` 一段** ★★另: 把「这闸【挂不挂链】+ 【挂哪儿】」登记成一条 `needs_from` (★key 自拟·★`to=main`·★`waiting_on` 留空=等 main 拍·不是等外部·不标 `waiting_on=boss`★)★★**

---

## ★★★【③ 判据 (★必须逐条实跑 + 贴原样输出★)★★★

★**【K-1】★ 七条判据逐条可见**: `python3 MECH/check_board_frame_freeze_gate.py` ⇒ ★**逐条打印 C1~C7 的通过/不通过 + 理由** ★ ★不许只给一个总 rc★★
★**【K-2】★ ★★C7 的真源必须实测确认★**: ★**交卷页里逐字写出【读哪个文件 / 读哪个字段 / 怎么匹配】, 且给出实测证据 (★例: 用一条真的闭合记录跑 ⇒ 命中; 用一条只有「板框已定」四个字的 ⇒ 不命中★)** ★★(★不许写「读 issue_log」这种盘上不存在的字段★)★
★**【K-3】★ RC-1~RC-6 六条反向用例**: ★**`python3 MECH/check_board_frame_freeze_gate_selftest.py --selftest` ⇒ 6/6 全抓到 · rc=0** ★ ★**必须在沙盒副本上跑 ⇒ 真件一个字节不许碰★★
★**【K-4】★ 正向对照**: ★**造一条【逐字含帧 id + 板厚 + 层数】的合法闭合记录 ⇒ C7 必须绿** ★★(★反向: 只有「板框已定」四个字 ⇒ 必须红★)★
★**【K-5】★ 阈值只读**: ★**C3 (板厚 ∈ {0.80, 1.00}) / C4 (层数 ∈ {4, 6, 8}) / C6 (36 档 can_open) 必须从 `MECH/service_port_check.py` 与 `MECH/board_frame_feasibility.py` 现读 ⇒ 代码里不许出现第二份写死的阈值表** ★★(★自证: 在沙盒里把现值改掉 ⇒ 闸的读数跟着变·★说明它真的在读·不是抄的★)★★
★**【K-6】★ ★★今天这闸【应该红还是应该绿】, 必须给一个诚实判断★★**:
- ★**C7 (need 未闭合) ⇒ 今天是红的** ⇒ ★★这是【如实报告病灶】, 不是闸坏了★ ⇒ ★★交卷页必须写清: 「今天红 = U-1 还没拍, 正确」★★
- ★**★但 C1~C6 【今天应该全绿】 (若不绿 ⇒ 那是本单要查的病灶·★不许改阈值去凑绿★)★★**
- ★**★★⇒ 交卷页必须明确区分: 「C7 红 = 等老板拍 U-1 (★不是本单的活★)」vs 「C1~C6 红 = 本单的活」★★**
★**【K-7】★ 零写板双证**: ★**板 md5 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413` 交卷前后逐字节相同** ★
★**【K-8】★ 零落表**: ★**`HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` 三个 md5 + mtime 交卷前后不变** ★
★**【K-9】★ 交卷前必跑 (★原样贴进回复★)**:
```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 state/merge.py      ; echo "MERGE_RC=$?"
python3 state/gate_check.py ; echo "GATE_RC=$?"
python3 state/issue_check.py; echo "ISSUE_RC=$?"
python3 MECH/check_board_frame_freeze_gate.py ; echo "FREEZE_RC=$?"
python3 MECH/check_board_frame_freeze_gate_selftest.py --selftest ; echo "FREEZE_ST_RC=$?"
md5sum HW/PCB/demo_mainboard.kicad_pcb ; stat -c "%y" HW/PCB/demo_mainboard.kicad_pcb
grep -cE "🔄|待填|PLACEHOLDER|施工中" MECH/ONETRIP_BOARD_FRAME_FREEZE_GATE.md
grep -cE "🔄|待填|PLACEHOLDER|施工中" HANDOFF/2026-11-19_mech-lead_ISS336_板框冻结闸实现.md
grep -c iss336 state/fragments/mech.yaml
```
★**★合卷门禁 (★Q1 必须 18/18★)★★**

---

## ★★★【④ 边界 (★一条都不许越★)★★★

- ★**零写板** (★板 md5 必须仍 `611b869e13518c3c023fb178f91a0075`·★mtime 必须仍 `2026-11-06 07:07:17.362193413`★)
- ★**零落表** (★网表 / 脚表 / BOM 三个 md5 + mtime 交卷前后不变★)
- ★**★零改 `state/gate_check.py`** (★★挂链是 main 的机制地界·★本单只交「给 main 的写法 + 挂链前体检结论」★★)
- ★**零改既有 `MECH/*.py`** (★尤其 `MECH/service_port_check.py` / `MECH/board_frame_feasibility.py` / `MECH/check_board_frame_coords.py` / `MECH/check_onepass_mech_release.py` —— 本单只【只读调用 / 只读 import】★) ★★`MECH/check_onepass_mech_release.py` 【不在】本单的清单里 (★它管的是「结构侧能不能出 Gerber」·本单管的是「板框冻结了没有」·★两件事不许混·★交卷页 §B5 说清这个边界★)★★
- ★**零改既有 `MECH/*.md` 与 `HW/**/*.md` 正文** (★只新建本单自己的 `MECH/ONETRIP_BOARD_FRAME_FREEZE_GATE.md`★) ★★(★`MECH/BOARD_FRAME_FREEZE_DECISION_PACK.md` / `MECH/ONETRIP_MECH_DIFF_OWNERSHIP.md` 是别人交卷的产物·★本单只读不碰·★要引用就引用, 不要改★)★★
- ★**零改 `HW/` 任何文件** (★含网表 / 脚表 / BOM / 板 / 作业包 / `HW/PCB/BOARD_FRAME_CALIBER.md`★)
- ★**零改 `state/issue_log.yaml`** (★★不许自签 issue_log★) · ★**零改 `state/fragments/pm.yaml` / `state/fragments/sw.yaml` / `state/fragments/hw.yaml`★★**
- ★**★不许代老板拍 U-1★** (★板框三选一 = 老板级·★本单只交【机器判据】+【今天为什么红】+【谁来拍·拍什么格式】★★) ★★**不许把 U-1 的答案写进任何文件·不许制造一条假的闭合记录让闸变绿★★**
- ★**沙盒只写 `tmp/iss336/` + `logs/iss336/` 新增件** ★★不许 `rm -rf /tmp/*` (★本机有别的 agent 在建沙盒·★且 `/tmp` 配额问题不许用删目录解决·★要写沙盒就把 `--tmpdir` 指项目内★)★★
- ★**不替 main 拍机制地界的活** (★挂链不许自己做★)
- ★**★零外发 (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★) ⇒ ★★不许发任何邮件 / 询价 / 问询 / 采购 ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ⇒ 没有「批一句可以发」这个选项★★**
- ★**证据分级必须标**: `[官网]` / `[实测]` / `[媒体]` / `[推算]` / `[0数据]` ★★本单绝大多数读数应是 `[实测]` (★本机实跑★)★★

---

## ★★★【⑤ 交卷时必须回答 main 的 4 个问题 (★写在交卷页 §B5★)★★★

1. ★**这闸今天红不红? 红的到底是哪几条?** ⇒ ★**逐条给 C1~C7 的红/绿 + 红的是「等老板」还是「本单能做」** ★★(★今天 C7 必红 (need 未闭合)·★C1~C6 该全绿·★若不绿就是病灶★)★★
2. ★**C7 到底读哪份文件?** ⇒ ★**逐字写出【文件 + 字段 + 匹配口径】+ 实测证据** ★★(★本机已发现 ISS-316 §2 的「读 issue_log」指向盘上不存在·★这一条必须纠正·★纠正后要跟 ISS-316 交卷页对齐 (★是订正·★不是偷偷改★)·★在交卷页 §B5 显式登记这条订正★★)★★
3. ★**这闸挂不挂链? 挂哪儿?** ⇒ ★**给建议 + 依据 + 不挂的后果** ★★(★提醒: 挂上去之后它【会红】⇒ 天天红 ⇒ ★**建议【不挂日常链】, 只在板那一趟开工前跑一次★】·★这一条要写清, 不然 main 挂上去就天天红★)★★
4. ★**U-1 拍完之后, 这闸【怎么变绿】?** ⇒ ★**逐字写出「老板的答案必须以什么格式、落在哪个文件、包含哪三个数, 这闸才会转绿」** ★★(★= 交一份【落表格式说明】给 main + 老板, 让 main 拿到答案后【一次落表】就能转绿★)★★

---

## ★★ 附加纪律 (★统一段·每单都有·照做★) ★★
★**① 写分片必须用 `state/frag_write.py` (★禁止 `open(p,"w")`★) ② 只写本任务允许的文件, 不碰别人的 ③ 证据分级 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` 必须标 ④ ★★不许外发任何邮件/询价/问询/采购 (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★) ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ⇒ 没有「批一句可以发」这个选项★ ⑤ 交卷前跑 `python3 state/merge.py` (★rc 必须 0★) && `python3 state/gate_check.py` (★Q1 必须 18/18★) 并把输出贴进回复★**
