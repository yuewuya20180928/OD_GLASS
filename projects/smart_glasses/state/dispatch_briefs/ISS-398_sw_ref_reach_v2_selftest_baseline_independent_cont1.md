# ISS-398 · cont1 · sw-lead · 「第三道病闸 `--selftest` 0/7」上一趟【交白卷】⇒ 本趟把夹具改成基线无关型 + 出 SW_MD5 重锚补丁 (不代拍)

> ★**owner**: sw-lead · ★**verify_by**: main · ★**单号**: ISS-398 · ★**零外发** ★
> ★**性质**: ★**纯分析 + 改【自测夹具】 + 出补丁 · 零写板 · 零落表 · 零改判据 · 零挂链 · 不代拍** ★
> ★**主线**: 绘制 PCB 图 ⇒ 合「板只改一次」纪律 ① (先派纯分析/作业包类, 不动板) ★

★**完整题面/验收标准全文 (★已过命令存在性守卫 rc=0★)**: `state/dispatch_briefs/ISS-398_sw_ref_reach_v2_selftest_baseline_independent.md` (★126 行★) ⇒ ★**你要交的三件 (夹具改基线无关 / `SW_MD5` 重锚补丁 / 重签留痕) 的逐条规格以那份为准 ⇒ 本单只补三样东西: 【上一趟怎么死的】/【上一趟已经实测到的读数·直接用】/【这一趟的落盘顺序与时间预算】★**

---

## ★★一 · 上一趟怎么死的 (★main 本机实读 transcript + 逐条实检磁盘 · 不抄任何 agent 报告★) ★★

★**上一趟 = 2026-11-24 18:26:15 起 → ★19:26:16 止 · ★**60 分钟** ★**
★**子会话**: ★`agent:sw-lead:subagent:ef85edc1-321f-4d41-bef8-172d5fc17b58` / sessionId `a43c2d61-9de5-4930-a449-1c23c5700f8a` (★status=done★) ★

★★**★死因: ★**交白卷** ★★ —— ★它【跑满了 60 分钟·读完了全部资料·把分析写进了 `tmp/iss398/plan.md`】· 但 ★**一件交付物都没落** ★★

★**★这一条是本单存在的全部理由 (★main 本机逐条实检 · 两次采样·不靠会话 status★)★**:

| ★项★ | ★**磁盘实况 (main 本机实读)** ★ | ★判定★ |
|---|---|---|
| ★**`SW/tools/check_sw_ref_reachability_v2.py`** ★ | ★**md5 `1c4043ea26a1182b210e85f1b5130d8d` · size 59025 · mtime `2026-11-18 21:37:24`★ ⇒ ★**自 11-18 起一个字节都没动过**★ | ★**夹具【根本没改】** ★ |
| ★**改前副本** ★ | ★**`tmp/iss398/v2_proto.py` (★59025 B·md5 `1c4043ea26a1182b210e85f1b5130d8d`★) ⇒ ★**与盘上真件 `cmp` 逐字节相同**★ | ★**它自己抄了改前副本就停手了** ★ |
| ★**`HANDOFF/2026-11-24_sw-lead_ISS398_*.md`** ★ | ★**不在盘** ★ (`ls HANDOFF/ \| grep -i ISS398` ⇒ **0**) | ★**交卷页零** ★ |
| ★**`state/fragments/sw.yaml` 的 ISS-398 登记** ★ | ★**0 条** ★ (`grep -c "iss398" state/fragments/sw.yaml` ⇒ **0**) | ★**分片零** ★ |
| ★**`logs/iss398/selftest_after.log`** ★ | ★**不在盘** ★ (★`logs/iss398/` 里只有 `selftest_before.log` / `gate_health_before.log` / `gates_before.log` 三个★before★) | ★**改后读数零** ★ |
| ★**`SW/BOARD_ONEPASS_SW_GATE_CHAIN_COVERAGE.md`** ★ | ★**mtime `16:02:08`** ★ ⇒ ★**上一趟没碰过它** ★ | ★**真相页机器块未同步** ★ |
| ★**plan.md 里的 9 步落盘顺序** ★ | ★**第 1~4 步 ✅ · 第 5~9 步全部 ⬜** ★ | ★**它只做完了「读 + 存证」** ★ |

★★**★⇒ 判死: ★**真僵尸 (交白卷)** ★★ —— ★**不是超时被掐 (status=done) · 不是崩溃 (transcript 完整到最后一格) · 是【它把 60 分钟全花在读资料上, 读完把分析写进 `tmp/iss398/plan.md`, 然后【再没写任何交付物】就结束了】★★

★★**★⇒ 这正是 LESSONS.md L-13 记的那条: 「攒了一堆读数在上下文里, 最后一步才开始写交付物」⇒ 墙钟到 ⇒ 什么都没留下★** ★★
★★**★⇒ 所以本趟的纪律只有一条, 但它决定生死: ★★【先落盘, 再继续】★★ ★★**
★★**★⇒ 任何一条读数, 你【一旦读到】就【立刻写进真相页/交卷页的对应格】⇒ 绝不许「先想着, 最后一起写」★** ★★

---

## ★★二 · 上一趟已经实测到的读数 (★★直接用, 不要重跑★★)

★★**★main 本机实读上一趟 transcript 的最后几条 thinking 块, 逐字摘出来的实测结果 (★它自己跑出来的·不是抄别人的报告★)★★** ★★

★**★★A · 根因已在盘 (`tmp/iss398/plan.md` ★**上一趟自己写的·逐字可用**★) ★★**
★**★⇒ 根因 = 【夹具被基线漂移染红】, 不是判据错 ★★**
★**★⇒ 三条用例 RC-5/RC-6/RC-7 的断言形态都是「★**破坏前必须 rc=0** ⇒ 才叫『不是巧合自证』★」★**
★**★⇒ 而「破坏前」实测就是 `rc=1` ⇒ 整棵沙盒树在动手之前已经红了 ⇒ 三条全灭 ★★**

★**★★B · 破坏前为什么红 (★plan.md 逐字★) ★★**
```
★裸跑红项逐字 = 新增真隐患:SW_MD5, 真隐患 4 > 基线 3
★自查: analyze(ROOT) ⇒ missing = ['CONN_USB','SW_MD5','TP_INT','TP_TEMP']
★       BASELINE_TOKENS = ['CONN_USB','TP_INT','TP_TEMP']
★⇒ 差集 = SW_MD5 ⇒ 账本落后一跳 (★不是判据错★)
```

★★**★main 本机独立复核过这三行 (★不是抄 plan.md·是本机重跑★): ★★** ★★
```
$ python3 SW/tools/check_sw_ref_reachability_v2.py ; echo "rc=$?"
  [FAIL] 位号引用解析不到 (新增真隐患·超基线): SW_MD5 @ SW/BOARD_ONEPASS_LEGB_SW_IMPACT.md:453 ⇒ 板与网表里现在叫: (无近似名)
  【判决】 ✘ 红 (rc≠0)
$ python3 SW/tools/check_sw_ref_reachability_v2.py --selftest ; echo "rc=$?"
  反向用例: 0/7 通过
  ❌ 有用例没抓到 ⇒ 判据可能没被真读
```
★**★⇒ 逐字一致 ⇒ 根因确认 (★不是本单要重新发现的·是本单要修的★) ★★**

★★**★C · `SW_MD5` 这个 token 的来处 (★main 本机实读★) ★★**
★**★⇒ `SW_MD5` 是【网表里已经不存在的位号】, 但 SW 文档还在引用它 ⇒ 形状像位号 ⇒ 落到 C14 真隐患 ★★**
★★**★`BASELINE_TOKENS` 只有三条 (★我本机读 `SW/tools/check_sw_ref_reachability_v2.py` L152~L170 核对过★): ★★**
★★**★`TP_INT` / `TP_TEMP` / `CONN_USB` ⇒ ★**`SW_MD5` 压根不在里面** ★★ ⇒ ★**所以它是【第 4 个真隐患】· 超了 `BASELINE_COUNT = 3` ⇒ 判红 ★★**

★★**★D · 夹具不许动的地方 (★main 本机实读源码★) ★★**
★**★⇒ `EXEMPT_LEDGER` (★L186 起★) 是一张【登记制】台账: 「只有【登记在 `EXEMPT_LEDGER` 里】的 token 才允许按形状豁免」 ★★**
★**★⇒ 里面已登记的 `SW_` (★C8: `SW_` 命名空间的截断写法★) ★**不等于** `SW_MD5` (★那是完整 token·不是截断写法★) ★★**
★★**★⇒ ★**登记 `SW_MD5` 进 `EXEMPT_LEDGER` = 口径 B = 【留一个漏检窗口】= ★**那是 main 的地界·本单只出补丁不应用** ★★**

---

## ★★三 · 这一趟的落盘顺序与时间预算 (★L-13: 先落盘, 再继续★) ★★

★★**★总预算: ★**90 分钟** (★`runTimeoutSeconds = 5400`·★比上一趟的 3600 多一半·但★**不许再花 60 分钟只读不写**★) ★★**

| ★步★ | ★时限★ | ★做什么★ | ★**落盘物 (★这一步结束【必须】在盘·不然就是重蹈覆辙★)** ★ |
|---|---|---|---|
| ★**1** ★ | ★**≤8 min** ★ | ★**先跑一遍 `--selftest` 并把 0/7 原始输出存成 `logs/iss398/selftest_before.log` (★若已存在则核对内容一致即可·不许重复造★)** ★ | ★**`logs/iss398/selftest_before.log` 在盘** ★ |
| ★**2** ★ | ★**≤15 min** ★ | ★**★立刻建交卷页骨架★ `HANDOFF/2026-11-24_sw-lead_ISS398_第三道病闸自测基线无关化.md` ★(★B1~B6 六个标题先占位·正文可以先空★) ⇒ ★**这是防死的关键一步** ★ | ★**交卷页骨架 (含 B1~B6 六个 `##` 标题) 在盘** ★ |
| ★**3** ★ | ★**≤40 min** ★ | ★**改夹具**: ★**只许**改 `SW/tools/check_sw_ref_reachability_v2.py` 里 ★**`--selftest` 的夹具与断言前置** ★★ ★**判据/阈值/红线定义/真患算式/`EXEMPT_LEDGER` 语义 ⇒ 一个字都不许动** ★ | ★**改夹具 + 跑 `--selftest` ⇒ ≥7/7 · 末行 `ALL TESTS PASS` · rc=0** ★ |
| ★**4** ★ | ★**≤50 min** ★ | ★**写重签留痕 (★追加式·老字一字未删★)** ★**到 `SW/tools/check_sw_ref_reachability_v2.py` 末尾** ★ | ★**留痕节在盘** ★ |
| ★**5** ★ | ★**≤60 min** ★ | ★**落 `logs/iss398/selftest_after.log` + `logs/iss398/bare_after.log` ★ | ★**两个 after 日志在盘** ★ |
| ★**6** ★ | ★**≤70 min** ★ | ★**★同步 `SW/BOARD_ONEPASS_SW_GATE_CHAIN_COVERAGE.md` 的机器块★** (★v2 的 rc/last_line 两处⇒ ★**不改它 `check_sw_gate_chain_coverage.py` 会当场红 (C1/C5 账实一致)**★) ★ | ★**真相页机器块已同步 (★追加式★)** ★ |
| ★**7** ★ | ★**≤78 min** ★ | ★**出 `SW_MD5` 重锚的两条口径补丁 (★口径 A / 口径 B·★**不应用**★)** + 交卷页 B1~B6 填实 ★ | ★**交卷页六段填实** ★ |
| ★**8** ★ | ★**≤85 min** ★ | ★**写分片** (★`state/frag_write.py --agent sw-lead`★) ★ | ★**`grep -c "iss398" state/fragments/sw.yaml` ≥ 1** ★ |
| ★**9** ★ | ★**≤90 min** ★ | ★**验收全跑 + `merge.py` + `gate_check.py` + 贴 rc 收工** ★ | ★**交卷消息** ★ |

★★**★⇒ ★**第 2 步 (★建交卷页骨架★) 是本单最关键的一步 ★★** —— ★**上一趟死在哪: 读完了 60 分钟才打算写 · 这一趟: 8 分钟内先把骨架立起来, 剩下 80 分钟全部用来【填内容】★★**
★★**★⇒ ★**第 3 步 (★改夹具★) 是本单唯一的技术难点 ⇒ ★**如果你在这一步卡住超过 25 分钟 ⇒ 立刻停下, 把卡点写进交卷页 B5, 把已完成的部分交上来 ★★** —— ★**半成品交上来 > 交白卷 ★★**

---

## ★★四 · 边界自证 (★交卷时逐条写进交卷页★) ★★

| ★边界★ | ★要求★ |
|---|---|
| ★**零写板 / 零落表** ★ | 板 / 网表 / 脚表 / BOM / 原理图真源 一个字节不许动 (★**板 md5 必须是 `611b869e13518c3c023fb178f91a0075`·mtime `2026-11-06 07:07:17.362193413`·size `4940213`** ★) |
| ★**零改判据** ★ | v2 的阈值 / 判定逻辑 / 红线定义 / 真患算式 / `EXEMPT_LEDGER` 语义 / `BASELINE_COUNT` 一个字不许动 ⇒ ★**只许改 `--selftest` 的夹具与断言前置** ★ ⇒ ★**自证 = 改前 `md5 1c4043ea26a1182b210e85f1b5130d8d` + §SELFTEST 之前的判据段前缀 md5 `3111dfb21d8233bb137e4d694c8abc04` (★offset 45580·★main 本机实算过★) 两个数在改后必须逐字不变** ★ |
| ★**★裸跑必须仍红★** ★ | ★**`python3 SW/tools/check_sw_ref_reachability_v2.py` 改后仍然 rc≠0 · 红因仍是 `新增真隐患:SW_MD5`★** ⇒ ★**你要是把裸跑刷绿了 = 你放宽了判据 或 动了盘上真件 `SW/SW_MD5_BASELINE_LEDGER.md` 的锚点 ⇒ 两种都违边界 ⇒ 交卷不算数** ★ |
| ★**零挂链** ★ | v2 仍然零挂链 (★`grep -c check_sw_ref_reachability_v2 state/gate_check.py` 必须 = 0★) ⇒ ★**挂不挂是 main 的地界** ★ |
| ★**零改已签收页正文** ★ | ★**`SW/BOARD_ONEPASS_SW_GATE_CHAIN_COVERAGE.md` 只许改【机器块里 v2 的 rc/last_line 两处】(★追加式·★其它正文一字不许动★)★ —— ★**★若你判断连这两处都不许动 ⇒ 那就在交卷页 B5 写明并给出逐字改法, 由 main 落·不许你私自改正文★** ★ |
| ★**零外发** ★ | ★**不发任何邮件 / 询价 / 问询 / 采购 ⇒ 缺口一律【自己网上查】+ 标证据等级 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` + 查不到就写降级方案 ⇒ 没有「批一句可以发」这个选项** ★ |
| ★**不代拍** ★ | 口径 A / B、挂不挂链、基线必须先绿通则 ⇒ 全交 main, 每条带「问法 + 不答后果 + 建议默认值」 |
| ★**不自签 issue_log** ★ | ★**`state/issue_log.yaml` 一个字节不许动** ★ |
| ★**只写自己分片** ★ | ★**只写 `state/fragments/sw.yaml` (★走 `python3 state/frag_write.py --agent sw-lead`★)★** |
| ★**沙盒只落项目盘** ★ | 临时产物只写 `tmp/iss398/` · 留证只写 `logs/iss398/` ⇒ **不许往系统 `/tmp` 写** (★本机 `/tmp` 配额打满 ⇒ 写那儿会出假读数 rc=120★) |

---

## ★★五 · 交卷消息必须含 (★缺一条算没交★) ★★

★① 改前 `--selftest` 0/7 原始输出 + 改后 ≥7/7 原始输出 (★两份都要有★) ★
★② 裸跑改前/改后**都红**的原文 + 红因逐字 (★`新增真隐患:SW_MD5`★) ★
★③ 「判据一个字未改」的自证 (★**判据段前缀 md5 `3111dfb2…` 改前改后逐字相同**★) ★
★④ 重签留痕 (★改前 md5 / 改后 md5 / 改了哪几行 (★行号 + 改前原文 + 改后原文★) / 审签人 = main 待签★) ★
★⑤ `SW_MD5` 重锚的两条口径补丁 (★A / B★) + 代价 + 建议默认值 (★**不应用**★) ★
★⑥ 自己独立复核出来的 `SW_MD5` 现值 (★自己 `md5sum` + 自己读锚点行·★**不许抄上一趟或本单的数**★) ★
★⑦ `merge.py` rc=0 + `gate_check.py` rc=0 + Q1 18/18 ★
★⑧ 板三项指纹未动 (★md5 / mtime / size 三项★) ★
★⑨ ★**★`grep -c "iss398" state/fragments/sw.yaml` ≥ 1 (★你这一趟的登记·上一趟是 0★)★** ★

---

## ★★六 · 必跑命令 (★全部本机实跑 · 交卷时贴输出★) ★★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 SW/tools/check_sw_ref_reachability_v2.py --selftest   # ★必须 rc=0 · ≥7/7 · 末行 ALL TESTS PASS★
python3 SW/tools/check_sw_ref_reachability_v2.py               # ★仍红 (红因 = SW_MD5 基线落后一跳) ⇒ 本单不代拍★
python3 SW/tools/check_sw_gate_health.py                       # ★改前/改后读数对比 (H0 点名的病闸清单不许变长★
python3 SW/tools/check_sw_gate_chain_coverage.py               # ★必须 rc=0 ★
python3 SW/tools/check_onepass_sw_release.py                   # ★必须 rc=0 ★
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
python3 state/merge.py && python3 state/gate_check.py          # ★rc 必须 0 · Q1 必须 18/18★
grep -c "iss398" state/fragments/sw.yaml                       # ★必须 ≥1★
grep -c check_sw_ref_reachability_v2 state/gate_check.py       # ★必须 = 0 (零挂链)★
```

★**★板三项基线 (★只读比对★)**: 板 `611b869e13518c3c023fb178f91a0075` · 网表 `6aee500e60ba0732f83a9cf557ba90ab` · 脚表 `9174309df1ec9411ac8e8d9e80ee386a` · BOM `5b9993992405904a60ac96a020b375d8` ★
★**★v2 判据段前缀 md5 (★改后必须逐字不变★)**: ★**`3111dfb21d8233bb137e4d694c8abc04`** ★ (★offset 45580★)
★**★v2 整文件 md5 (★改前★)**: ★**`1c4043ea26a1182b210e85f1b5130d8d`** ★
