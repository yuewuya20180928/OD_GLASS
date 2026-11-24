# ★ISS-408 · cont1 · sw-lead · 【板 md5 重锚定的守门闸自己坏了】—— 上一趟【交白卷】⇒ 本趟先落盘骨架再补内容 ★

★**owner**: sw-lead · ★**verify_by**: main · ★**单号**: ISS-408 · ★**零外发** ★
★**性质**: ★**纯查证 + 纯分析 + 追加式订正 + 反向用例 + 自有分片收口 · 零写板 · 零落表 · 零改既有页正文 (★只许追加式★) · 零挂链 · 不代拍** ★
★**主线**: 绘制 PCB 图 ⇒ 合「板只改一次」纪律 ① (先派纯分析/作业包类, 不动板) ★

★**完整题面/验收标准全文 (★已过命令存在性守卫 rc=0★)**: `state/dispatch_briefs/ISS-408_sw_md5_rebase_gate_truth.md` (★**本单的全部逐条规格以那份为准 ⇒ 本单只补四样东西: 【上一趟怎么死的】/【上一趟已经实测到的读数·直接用】/【这一趟的落盘顺序】/【这一趟的时间预算与防再死措施】★**

---

## ★★一 · 上一趟怎么死的 (★main 本机实读 transcript + 逐条实检磁盘 · 不抄任何 agent 报告★) ★★

★**上一趟 = 2026-11-25 01:56:15 起 → ★02:07:37 止 · ★**11 分 22 秒** ★**
★**子会话**: ★`agent:sw-lead:subagent:49b0f39b-fbde-4066-90fd-28ae31ae569c` / sessionId `223a97cd-5a09-4105-afd7-3671752c738a` (★status=timeout★) ★
★**runId**: `eb5a662c-f102-4f21-bde6-41a2785a533b` · ★**runTimeoutSeconds = 0** ★

★★**★死因: ★**不是它自己超时 (runTimeoutSeconds=0 ⇒ 无超时上限) · 不是崩溃 (transcript 完整) · 是【★**外部同时中断**★】—— ★**同一 3 秒窗口里 (02:07:37~02:07:40) `mech-lead` 的 ISS-407 也死了** ⇒ ★**两条同型任务同时死 ⇒ 共因 ⇒ 这是 LESSONS.md L-33-a 记的同型事故 (★21:51:49 那次三条同秒死·一模一样★)★ ★★

★**★⇒ 它最后一条 transcript 消息是 ★**「missing tool result in session history; inserted synthetic error result for transcript repair」★ ⇒ ★**它是在等一个长命令 (`check_brief_commands.py` 全仓扫描) 的返回时被一起掐掉的** ★★

★★**★⇒ 判死: ★**真僵尸 (交白卷)** ★★ —— ★**三件交付物一件都没落** ★★:

| ★项★ | ★**磁盘实况 (main 本机实读)** ★ | ★判定★ |
|---|---|---|
| ★**`SW/BOARD_ONEPASS_SW_MD5_REBASE_GATE_TRUTH.md`** ★ | ★**不在盘** ★ | ★**真相页零** ★ |
| ★**`SW/BOARD_ONEPASS_SW_MD5_REBASE_READINESS.md` 的 §1/§2 收口** ★ | ★**md5 仍是 `0ba9dfce5046e131465b4fbd3675614f`** ★ (★与上一趟开工前逐字相同★) ⇒ ★**一个字都没改** ★ | ★**核心动作零** ★ |
| ★**`HANDOFF/2026-11-25_sw-lead_ISS408_板md5重锚定守门闸修可信.md`** ★ | ★**不在盘** ★ (`ls HANDOFF/ \| grep -i 408` ⇒ **0**) | ★**交卷页零** ★ |
| ★**`state/fragments/sw.yaml` 的 ISS-408 登记** ★ | ★**0 条** ★ (`grep -c "iss408" state/fragments/sw.yaml` ⇒ **0**) | ★**分片零** ★ |

★★**★⇒ 但它【已经把开工基线全部留证在盘了】(★这是它的真实贡献·直接用·不许重跑★)★** ★★

★**`logs/iss408/` 里有 4 个文件 (★02:0x 写的★)**:

| ★文件★ | ★**内容 (main 已逐条实读)** ★ |
|---|---|
| ★**`baseline_md5_pre.txt`** ★ | ★**5 件受保护件的改前 md5 (★收口前的指纹基线·追加式自证要拿它比对★)** ★: `SW/BOARD_ONEPASS_SW_MD5_REBASE_READINESS.md` = `0ba9dfce5046e131465b4fbd3675614f` · `SW/BOARD_ONEPASS_ZERO_FALSE_CONNECTIVITY.md` = `151a9fbbd0faea7166817c62b667bb4a` · `SW/EVT_CHARGE_CURRENT_CRITERION_CALIBER.md` = `185355d83b82f97953ad37d49ecbcce6` · `SW/tools/check_sw_false_connectivity_gate.py` = `4630948f3949cb9a588c74d6f7f69633` · `SW/tools/check_sw_board_md5_rebase_readiness.py` = `2099ca42a946f64b620e896ba8d2be0b` ★ |
| ★**`gate_before.txt`** ★ | ★**收口前 `check_sw_board_md5_rebase_readiness.py` 的原样输出 (★rc=1)★** ★ |
| ★**`gate_health_before.txt`** ★ | ★**收口前 `check_sw_gate_health.py` 的原样输出 (★ISS-388 那道闸·不许被本单弄红★)★** ★ |
| ★**`brief_cmds_before.txt`** ★ | ★**0 字节 (★它被掐时正在写这个★) ⇒ 用 `state/check_brief_commands.py --brief-file` 现跑一次补上** ★ |

★**★⇒ 它还读懂了 3 件关键的事 (★直接用, 不许重读★)★**:
1. ★**`SW/BOARD_ONEPASS_SW_MD5_REBASE_READINESS.md` 的机器可读清单在 `<!-- ISS372-MANIFEST:BEGIN -->` (★L181★) ~ `<!-- ISS372-MANIFEST:END -->` (★L768★) 之间的 JSON 块里 ⇒ ★**`refs` 53 条 + `gates` 6 条 + `board` + `scan` + `evidence_levels` + `schema`** ★
2. ★**那 6 条 `gates` 账现在登的是**: `check_fp_truth_read.py` (F5) · `check_onepass_legb_sw_impact.py` (G8) · `check_onepass_sw_sync.py` (W6/ANCHOR_MD5 · ★已有通道★) · `HW/check_iss354_manufacturability.py` (A-5a/A-5b · ★跨域 hw-lead 的域★) · `check_debug_pin_order_contract.py` (D7) · `check_debug_header_fw_impact.py` (W7) ⇒ ★**`check_sw_false_connectivity_gate.py` 不在其中 ⇒ 这就是 H4 红的根因** ★
3. ★**闸自己的判据源码位置** (★`SW/tools/check_sw_board_md5_rebase_readiness.py`): `MANIFEST_BEGIN`/`MANIFEST_END` 常量在 L54/L55 · `scan_refs()` L124 · `detect_pinned_gates()` L249 · `load_manifest()` L280 · `write_manifest()` L297 · H1 判据 L350 一带 · H4 判据 L395 一带 · `selftest()` L495 ★

★★**★⇒ 纪律 (★决定生死★): ★★【先落盘, 再继续】★★ ★★**
★★**★⇒ LESSONS.md L-13 记的那条: 「攒了一堆读数在上下文里, 最后一步才开始写交付物」⇒ 墙钟到 ⇒ 什么都没留下★ ★★**
★★**★⇒ L-33 记的那条: 「『再死一次也不丢东西』的唯一做法 = 每件交付物先落盘再跑它」⇒ ★**这一趟的落盘顺序见 §三·不许再攒到最后★** ★★

---

## ★★二 · 本机实测基线 (★main 2026-11-25 02:1x 本机实跑 · 可复现·直接引用★) ★★

★**★main 本轮亲手复跑 `python3 SW/tools/check_sw_board_md5_rebase_readiness.py` ⇒ rc=1 · 读数与上一趟的 `logs/iss408/gate_before.txt` 逐字一致 ⇒ 两红未变★**

| ★判据★ | ★**实测读数 (main 本轮实跑)** ★ |
|---|---|
| ★**H1 红** ★ | ★**4 处板 md5 引用面漏登记**: `SW/BOARD_ONEPASS_ZERO_FALSE_CONNECTIVITY.md:23` · `SW/BOARD_ONEPASS_ZERO_FALSE_CONNECTIVITY.md:241` · `SW/EVT_CHARGE_CURRENT_CRITERION_CALIBER.md:215` · `SW/tools/check_sw_false_connectivity_gate.py:73` ★ |
| ★**H2 / H3 绿** ★ | 每一处都标了【三类归属】+【处置】+ 备注 / 【历史留证】类真不许改 ★ |
| ★**H4 红** ★ | ★**`SW/tools/check_sw_false_connectivity_gate.py` 硬钉了板 md5 (类A · .py 内 32 位字面量) 但没进 §2 的账** ⇒ ★「下一道新闸再硬钉板 md5 就是从这儿溜过去的」这条防线今天没有** ★ |
| ★**H5 / H6 / H7 绿** ★ | 通道 / 零写板自证 / 证据分级白名单 ★ |
| ★**板 md5 / mtime / size** ★ | ★**`611b869e13518c3c023fb178f91a0075` / `2026-11-06 07:07:17.362193413` / `4940213`** ★ ⇒ ★**19 天逐字节未动 ⇒ G1 仍开, 不许投板** ★ |
| ★**`check_sw_gate_health.py` 收口前读数** ★ | ★**H0 红 (★点名 `check_sw_board_md5_rebase_readiness.py` 的 `--selftest` rc=1 ⇒ 「它自己坏了」★) · H1 红 (`check_debug_pin_order_contract.py` 在两个 TMPDIR 深度下 rc 不同 ⇒ 环境无关性·★本单不许碰它★) · H2 红 (★`check_sw_false_connectivity_gate.py` 硬钉板 md5 却没进 §2 的账 ⇒ ★**这正是本单要修的那条**★)★** ★ |

★**★⇒ 关键: ★**本单修好这道闸, `check_sw_gate_health.py` 的 H0 就会从「点它坏」变成「不点它」⇒ ★**收口后 H0 那条红必须消失 (或至少不再点这一道) ⇒ 这是本单「修可信」的机器凭证★** ★★

---

## ★★三 · 这一趟的落盘顺序 (★★再死一次也不丢东西的唯一做法★ ★★)

★**★按这个顺序做, 每一步做完就落盘 (★不许攒到最后一起写★)★** ★★

| ★步★ | ★**做什么** ★ | ★**落什么盘 (★这一步做完立刻落★)** ★ |
|---|---|---|
| ★**0** ★ | ★**先建骨架 (★10 分钟内★)** ★ | ★**先把真相页 `SW/BOARD_ONEPASS_SW_MD5_REBASE_GATE_TRUTH.md` 的 §0 + §1 写出来 + 把 4 处漏登记的清单先列成表** ★ ⇒ ★**哪怕后面死了, 真相页在盘** ★ |
| ★**1** ★ | ★**改 §1 清单 (追加式)** ★ | ★**在 `SW/BOARD_ONEPASS_SW_MD5_REBASE_READINESS.md` 的 MANIFEST 块 `refs` 里**追加**那 4 条 (★每条含 file / line / occ / snippet / cls / action / note★) ⇒ ★**★注意: 追加式 = 老字一字未删 ⇒ 改完必须用 md5 前缀比对自证 (★改前全文 = 改后前缀★)★** ★ ⇒ ★**同时在 §1 的表格正文里**追加**对应 4 行 (★机器块与正文必须一致★)★** ★ |
| ★**2** ★ | ★**改 §2 账 (追加式)** ★ | ★**在 MANIFEST 块 `gates` 里**追加** `check_sw_false_connectivity_gate.py` 那一条 (★含 id / title / built_by / channel / status / gap_id / owner★) ⇒ ★**再在 §2 的逐闸账正文里**追加**对应的闸条目 ⇒ ★**老字一字未删** ★ |
| ★**3** ★ | ★**跑闸验证** ★ | ★**`python3 SW/tools/check_sw_board_md5_rebase_readiness.py` ⇒ ★**收口后必须 rc=0**★ ⇒ 输出存 `logs/iss408/gate_after.txt` (★与 `gate_before.txt` 成对★)★** ★ |
| ★**4** ★ | ★**构造反向用例** ★ | ★**★3 条 (★逐条贴原样输出★): ① 删 §1 清单里某一行 ⇒ 闸必须红 ② 删 §2 账里 `check_sw_false_connectivity_gate.py` 那行 ⇒ 闸必须红 ③ 在盘上某处新加一处板 md5 引用面而不登记 ⇒ 闸必须红★** ⇒ 存 `logs/iss408/reverse_cases.txt` ★ |
| ★**5** ★ | ★**写交卷页** ★ | ★**`HANDOFF/2026-11-25_sw-lead_ISS408_板md5重锚定守门闸修可信.md` (B1~B7 · ★必须贴收口前后该闸的原样输出 + rc 对比★)★** ★ |
| ★**6** ★ | ★**写分片** ★ | ★**`state/fragments/sw.yaml` (★只走 `state/frag_write.py`★) ★** ★ |
| ★**7** ★ | ★**收尾** ★ | ★**`python3 state/merge.py` (rc=0) && `python3 state/gate_check.py` (Q1 18/18) ⇒ 原样贴进回复 ★** ★ |

★**★⇒ 落盘顺序的机器理由 (★L-33 的原话★): 「每件交付物先落盘再跑它」⇒ ★**万一第 4 步的反向用例把你搞崩了, 前面 3 步的收口已经在盘 (★那才是本单的核心价值★)★ ★★**

---

## ★★四 · 时间预算与防再死措施 ★★

★**预算**: ★**60 分钟** ★ (★上一趟 11 分钟就死了 ⇒ 这趟按 60 分钟排, 但★**每 10 分钟必须有一次落盘**★)
★**★防再死 4 条 (★全是实测出来的·不是空话★)★**:
1. ★**每 10 分钟落一次盘** (★上面那张表的步 0~6 就是落盘点★) ⇒ ★**再死一次, 至少「真相页 + §1/§2 收口」在盘 (★那正是本单的核心动作★)★**
2. ★**不要整文件读大文件** ⇒ ★**`SW/BOARD_ONEPASS_SW_MD5_REBASE_READINESS.md` 有 1000+ 行 ⇒ ★**只用 offset/limit 读你要的那几段 (★上一趟读了很多, 一行没写★)★**
3. ★**★长命令先跑短的★** ⇒ ★**上一趟死在「等一个全仓扫描命令返回」上 ⇒ ★**这一趟先跑 `state/check_brief_commands.py --brief-file <本 brief>` (★短·几秒★) ⇒ 别把长扫描放在开工第一步** ★
4. ★**分片放在倒数第二步** (★不是最后一步★) ⇒ ★**分片是「已交卷」的机器凭证, 早写一分钟就多一分留证★ ★★

---

## ★★五 · 本单交付物 (★与上一趟完全一致, 一件都不许少★) ★★

| # | 交付物 | 路径 | 验收口径 |
|---|---|---|---|
| ① | 真相页 | ★**新建** `SW/BOARD_ONEPASS_SW_MD5_REBASE_GATE_TRUTH.md` ★ | §0~§6 + 机器块; ★**逐条**写清 H1 那 4 处漏登记【分别是什么内容 · 属于三类归属的哪一类 · 该怎么处置 · 谁负责】+ H4 那道漏登记的闸【它硬钉的板 md5 是哪个字面量 · 为什么该进 §2 · 登记后怎么防下一道新闸再溜】+ ★**「板 md5 变了之后 SW 侧要动哪几处」的总清单** ★ |
| ② | ★**收口动作 (★本单的核心★)** ★ | ★**追加式** 写进 `SW/BOARD_ONEPASS_SW_MD5_REBASE_READINESS.md` 的 §1 / §2 ★ | ★**4 处漏登记逐条补进 §1 清单 + `check_sw_false_connectivity_gate.py` 补进 §2 账** ⇒ ★**追加式: 老字一字未删 (★用 md5 前缀比对自证★) ★** ⇒ ★**正文若需要改, 一律写成追加式订正块, 不许改正文 ★** ★ |
| ③ | 交卷页 | ★**新建** `HANDOFF/2026-11-25_sw-lead_ISS408_板md5重锚定守门闸修可信.md` ★ | B1~B7 全填 (★标题用仓里规范口径, gate_check Q1 六块齐全★) ★★**必须贴出收口前后 `check_sw_board_md5_rebase_readiness.py` 的原样输出 + rc 对比** ★★ |
| ④ | 自有分片收口 | `state/fragments/sw.yaml` | ★**只走 `state/frag_write.py`** ★ (★禁止 `open(p,"w")`★) · 写后四项自检: 条数 / 丢 key / 多的 key / 内容有变的条 ★ |
| ⑤ | 留证 | `logs/iss408/` + 沙盒 `tmp/iss408/` | ★**不硬链接真件 · 不写系统 `/tmp`** ★ |

★**★本单的关键在于「证明这条闸真的有牙齿」★**: ★**S1 收口前红 ⇒ 收口后必须绿 (rc=1 ⇒ rc=0)★**; ★**S2 必须构造至少 3 条反向用例并逐条贴原样输出** ★
★**★注意 (★主线的纪律, 别踩★)★**: ★**本单【不许】为了让闸变绿去改那 4 处引用面的正文** (★`SW/BOARD_ONEPASS_ZERO_FALSE_CONNECTIVITY.md` / `SW/EVT_CHARGE_CURRENT_CRITERION_CALIBER.md` 是已签收页, 正文一字不许改★) ⇒ ★**只补登记 (让漏登记消失), 不改被登记的内容** ⇒ ★**若某处的内容本身是错的 (⇒ 该由谁修), 写成 needs_from 交 main, 一条都不许代拍★ ★**

---

## ★★六 · 边界 (★违反任一条 = 本单不算交卷★) ★★

| 边界 | 怎么自证 |
|---|---|
| ★**零写板** ★ | 板 md5 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413` + size `4940213` 三项逐字未动 |
| ★**零落表** ★ | 网表 / 脚表 / BOM md5 逐字未动 |
| ★**零改既有页正文 (★只许追加式★)** ★ | ★**`SW/BOARD_ONEPASS_SW_MD5_REBASE_READINESS.md` 的 md5 前缀比对 (★老字一字未删★) + `SW/BOARD_ONEPASS_ZERO_FALSE_CONNECTIVITY.md` / `SW/EVT_CHARGE_CURRENT_CRITERION_CALIBER.md` / `SW/tools/check_sw_false_connectivity_gate.py` 三件 md5 逐字未动** ★ |
| ★**零挂链** ★ | ★**`grep -c check_sw_board_md5_rebase_readiness state/gate_check.py` = 0** (★它本来就没挂★) ★ |
| ★**零外发** ★ | ★**不许发任何邮件 / 询价 / 问询 / 采购** (★老板 2026-11-11 19:31 + 2026-11-12 02:02★) ⇒ `state/outbox/` 逐字未动 ⇒ **没有「批一句可以发」这个选项** ★ |
| ★**不代拍** ★ | 「这 4 处该怎么处置 / 那道闸归不归 §2 / 板 md5 变了以后谁先动」 ⇒ 交 main, 机器块写 `not_decided_here` |
| ★**不自签** ★ | ★**不许写 `state/issue_log.yaml`** ★ |

---

## ★★七 · 纪律 (★与其它单一样的硬规矩★) ★★

① ★**写分片必须用 `state/frag_write.py`** (★禁止 `open(p,"w")`★)
② ★**只写本任务允许的文件, 不碰别人的** (★`HW/` · `MECH/` 一页都不许写★)
③ ★**证据分级** `[官网]` / `[实测]` / `[媒体]` / `[推算]` / `[0数据]` 必须标
④ ★**不许外发任何邮件/询价/问询/采购** ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案
⑤ ★**交卷前跑 `python3 state/merge.py` (rc 必须 0) && `python3 state/gate_check.py` (Q1 必须 18/18) 并把输出贴进回复** ★
⑥ ★**不许把这道闸挂进 `state/gate_check.py`** (★它本来就没挂★ ⇒ `grep -c` = 0) ★
⑦ ★**不许写 `state/issue_log.yaml`** (★签收由 main 做★)

---

## ★★八 · 留给 main 的问句 (★你只摆代价, 一条都不许代拍★) ★★

- ★**Q1**: H1 那 4 处漏登记的引用面, 该按「历史留证」还是「活判据」归属? (★归属不同 ⇒ 板 md5 变了以后要不要跟着改, 结论相反★)
- ★**Q2**: `check_sw_false_connectivity_gate.py` 硬钉板 md5 ⇒ 是补进 §2 账, 还是把它改成走合法改板通道 (★后者要动已签收闸 ⇒ 需重签★)?
- ★**Q3**: 这道守门闸要不要挂进 `state/gate_check.py`? (★它今天红 ⇒ 挂上去当天链会红★)
- ★**Q4**: 「板 md5 变了以后 SW 侧要动哪几处」的总清单要不要成为板那一趟的必过项?
- ★**Q5**: 本单要不要再补一道独立新闸 (★守「漏登记机制本身」★), 还是把反向用例固化进既有闸的 `--selftest`?
