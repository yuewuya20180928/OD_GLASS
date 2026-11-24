# ISS-399 · mech-lead · MECH 域【闸把别人的 md5 写死成硬基线】的全量清账 + 3 处已陈旧 pin 的裁定 + 一道自守闸 (零写板 · 零落表 · 不代拍)

> ★**owner**: mech-lead · ★**verify_by**: main · ★**单号**: ISS-399 · ★**零外发** ★
> ★**性质**: ★**纯分析 + 新建真相页 + 新建机器闸 + 出逐字补丁(不应用) · 零写板 · 零落表 · 零改既有闸的判据/阈值 · 零挂链 · 不代拍** ★
> ★**主线**: 绘制 PCB 图 ⇒ 合「板只改一次」纪律 ① (先派纯分析/作业包类, 不动板) ★

---

## ★★一 · 题 (来源 = ★main 2026-11-24 19:4x 本机实跑 · 不抄任何 agent 报告★) ★★

★★**★① 现象: MECH 域有 ★**9 道闸把「别的文件」的 md5 写死成常量**, 共 ★**35 处 pin** ★★ ⇒ ★**其中 ★3 处已经陈旧 ⇒ 2 道闸现在就是红的** ★★

| ★闸 (★全在 `MECH/`★) ★ | ★钉住别人 md5 的处数★ | ★**已陈旧★** ★ | ★**在不在官方门禁链★** ★ |
|---|---|---|---|
| ★`MECH/check_connector_clearance_caliber.py` ★ | ★5 ★ | ★**2** ★ | ★**零挂链** ★ |
| ★`MECH/check_fts_seat_sample_plan.py` ★ | ★9 ★ | 0 | ★**零挂链** ★ |
| ★`MECH/check_zoujuan_marker_consistency.py` ★ | ★4 ★ | ★**1** ★ | ★**零挂链** ★ |
| ★`MECH/check_demo_struct_truth.py` ★ | ★4 ★ | 0 | ★**✅ 在链 (钉板闸⑧)** ★ |
| ★`MECH/check_debug_seat_3d_fit.py` ★ | ★3 ★ | 0 | 零挂链 |
| ★`MECH/check_debug_seat_rework_spec.py` ★ | ★3 ★ | 0 | 零挂链 |
| ★`MECH/check_fts_seat_body_geometry.py` ★ | ★3 ★ | 0 | 零挂链 |
| ★`MECH/check_fts_vs_generic_courtyard_delta.py` ★ | ★3 ★ | 0 | 零挂链 |
| ★`MECH/check_mech_dual_caliber_gate.py` ★ | ★1 ★ | 0 | 零挂链 |

★★**★② 已陈旧的 3 处 (main 本机逐字实算·★你必须自己重算一遍·别只抄本表★) ★★**

| ★#★ | ★钉它的闸★ | ★被钉的文件★ | ★闸里写死的基线★ | ★盘上现值★ |
|---|---|---|---|---|
| ★**1** ★ | ★`MECH/check_connector_clearance_caliber.py` (K7) ★ | ★`MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md` ★ | ★`ffc099397dc573df207f265bff57dffb` ★ | ★`f1ce54c981dd1f64071a177a374df85d` ★ |
| ★**2** ★ | ★`MECH/check_connector_clearance_caliber.py` (K7) ★ | ★`MECH/check_juart_1p27_clearance.py` ★ | ★`ea89e0dd3b2f77828b69f06bbe76969d` ★ | ★`daf8fa367d89e22f6d3af3d5049bdfb6` ★ |
| ★**3** ★ | ★`MECH/check_zoujuan_marker_consistency.py` (K5) ★ | ★`MECH/check_demo_struct_truth.py` ★ | ★`fa9b59e593a13408ad9505d986276f63` ★ | ★`483d018a66d17d2ead25d1558a1f8ffe` ★ |

★★**★③ 这 3 处为什么陈旧 (main 本机查到的来源·★要自己复核★) ★★**
★**★⇒ #1/#2 = ★**ISS-374 cont2 对已签收页/闸做的【追加式订正】** ★★ ⇒ ★**这本身是合法动作 (★house 规矩: 追加式订正·老字一字未删★)·但【没人回头更新钉它的基线】⇒ 基线永久停在旧值 ⇒ K7 永久红** ★★
★**★⇒ #3 = ★**`MECH/check_demo_struct_truth.py` 在 ★**2026-11-17 20:25:32** ★被【别的单】合法改过 (★`HANDOFF/2026-11-17_mech-lead_ISS295_结构输入认领与防漂闸.md` 第 428 行自己记着这一行·★标注「别的单」★) ⇒ ★**而 `MECH/check_zoujuan_marker_consistency.py` 是 ★**2026-11-16 10:59** ★写的·它的 `GUARDED` 基线比那次改动早 ⇒ 又一处永久红** ★★

★★**★④ 两道闸现在就是红的 (main 本机实跑·★你必须自己重跑一遍★) ★★**
```
$ python3 MECH/check_connector_clearance_caliber.py ; echo "rc=$?"
  [FAIL] K7  已签收件未被改动 (逐字节 md5 不变)
  MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md md5 f1ce54c981dd1f64071a177a374df85d != 已签收基线 ffc099397dc573df207f265bff57dffb;
  MECH/check_juart_1p27_clearance.py md5 daf8fa367d89e22f6d3af3d5049bdfb6 != 已签收基线 ea89e0dd3b2f77828b69f06bbe76969d
$ python3 MECH/check_zoujuan_marker_consistency.py ; echo "rc=$?"
  [FAIL] K5  受保护文件 md5 未变
  受保护文件被改: MECH/check_demo_struct_truth.py md5 483d018a66d17d2ead25d1558a1f8ffe≠fa9b59e593a13408ad9505d986276f63
```

★★**★⑤ ★**为什么没人看见★ (★这一条是本单最值钱的发现★) ★★**
★**★⇒ 这 9 道里只有 ★**1 道 (`check_demo_struct_truth.py`) 在官方门禁链 `state/gate_check.py` 里** ⇒ ★**另外 8 道是【零挂链】⇒ ★**它们红了【零通知】⇒ 只有 agent 手工当回归跑时才看得见** ★★**
★**★⇒ 而它们是 agent 的【既有闸零漂移回归项】(★`HANDOFF/2026-11-24_mech-lead_ISS382_JDEBUG排针排布标签订正与G5盲区.md` 第 38 行白纸黑字写着: 「★**K7 基线红 2 条是开工前就有的 (ISS-374 cont2 追加已签收页所致)**」★) ⇒ ★**每个跑这道闸的 agent 都得自己写一句「这红不是我造成的」★ ★★**
★**★⇒ ★**所以这不是「某个 agent 的红」, 是【MECH 域缺一本账】★★**

★★**★⑥ 为什么这件事卡在「板那一趟」的要害上 (★本单的价值定位★) ★★**
★**★⇒ 「板只改一次」那一趟 = ★**位号改名 + 板侧同步 + 布局修正 + 布线 45→0 + Gerber/投产包重出** ★★ ⇒ ★**那一趟必然要【追加式订正】MECH 域的一堆已签收页/闸** (★ISS-391/396 的 FTS 换件 + 座体那一串 J_DEBUG/J_UART 收口·★见 `HANDOFF/2026-11-24_mech-lead_ISS397_座体三量收样作业包.md` 与 `HANDOFF/2026-11-23_mech-lead_ISS374_JUART排针1.27净距真相.md`★) ★★**
★**★⇒ ⇒ 每一次合法追加 ⇒ 钉它的闸又陈旧一处 ⇒ ★**收工验收那天, 那几道 MECH 闸是红的 ⇒ 红是真的 (文件确实变了), 但【变的原因是对的】⇒ ★**现场极可能误读成「MECH 改坏了」⇒ 板白改第二遍** ★★**
★★**★⇒ ★★**这不是假想: ★3 处陈旧【此刻】已经发生了, 而它们至今没人归因★★** ★★**

★★**★⑦ 同型病在本仓已被治过两次 (★先例·★不要重新发明★) ★★**
| ★先例★ | ★治法★ | ★本单能不能照抄★ |
|---|---|---|
| ★**ISS-296 / ISS-303 (MECH 侧)** ★ | ★把「硬基线常量」换成「★**硬基线 ∪ 落表台账登记值**」★ (★只读台账·不许把新 md5 写死·fail-closed★) ⇒ ★`MECH/check_board_frame_coords.py` 的 C4 / `MECH/check_onepass_struct_crosscheck.py` 的 N6 ★**已经这么干了** ★ | ★★**能, 但★**落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` 里 ★**根本没有这 3 个 MECH 文件** (★main 实查: grep 全是 0 命中★) ⇒ ★**所以 MECH 域缺的不是「换一个源」, 是【缺一本自己的台账】** ★★ |
| ★**ISS-372 (SW 侧)** ★ | ★**《钉板 md5 闸清单》自守闸**: `SW/tools/check_sw_board_md5_rebase_readiness.py` ★**H4 = 「SW 域每道【真钉板 md5 的判据脚本】必须在 §2 有账」/ H5 = 「要么【代码级已有合法改板通道】, 要么登记为已知缺口 + 归属 + 谁来补 + 补法规格」** ★ | ★★**MECH 域★**至今没有这一道** ★★ ⇒ ★**本单交付的自守闸就是它的 MECH 对偶** ★★ |

---

## ★★二 · 本单要交的三件 (★缺一件 = 不算交卷★) ★★

### ★★交卷物 (3 件) ★★

1. ★**新建** `MECH/BOARD_ONEPASS_SIGNED_APPEND_LEDGER_DESIGN.md` — ★**真相页** ★§0 口径与边界 / §1 35 处 pin 全量清账表 / §2 三处陈旧逐条裁定 / §3 台账设计 / §4 三条逐字补丁(不应用) / §5 挂链建议 / §6 边界自证 + 机器块 ★
2. ★**新建** `MECH/check_mech_signed_append_ledger.py` — ★**新机器闸** ★M1~M8 判据 + `--selftest` ≥8 条反向用例 (★含一条专打 M4「悄悄改常量 ⇒ 必红」★) ★零挂链 ★
3. ★**新建** `HANDOFF/2026-11-24_mech-lead_ISS399_MECH域已签收件追加台账设计与自守闸.md` — ★**交卷页** ★B1 结论摘要 / B2 验收自评 / B3 证据分级 / B4 接口取值 / B5 未决项 / B6 自证命令+rc / B7 边界自证

### ★★2-1 · 真相页 `MECH/BOARD_ONEPASS_SIGNED_APPEND_LEDGER_DESIGN.md` (★新建★) ★★

★**§0** 口径与边界自证 (★零写板 / 零落表 / 零改既有闸 / 零外发 / 不代拍★)
★**§1** ★**MECH 域「钉别人 md5」全量清账表 (★35 处·逐处一行★)**: ★闸 / 被钉文件 / 闸里写死的基线 / 盘上现值 / ★**状态 (绿 / 已陈旧)** ★ / ★**陈旧原因 (合法追加 / 来源不明) + 证据出处** ★
★**§2** ★**3 处已陈旧的逐条裁定 (★#1/#2/#3 各一节★)**: ★**它是不是合法动作** (★给出证据: 哪个单、哪次追加、`append` 前后 md5、老字是否逐字保留★) / ★**如果合法 ⇒ 为什么没人更新基线** / ★**如果不合法 ⇒ 是什么缺陷** ★
★**§3** ★**MECH 域【已签收件追加登记台账】设计**: ★**台账长什么样 (★原子记录字段: by 单号 / file 文件 / prev_md5 / md5 / 追加位置 / 「老字逐字未删」的自证方式★)· 追加到哪个文件 (★自己提方案, ★**不替 main 拍**★) · ★**fail-closed 口径: 台账链断了 / 链头不唯一 / 链头无单号 ⇒ 判红** ★
★**§4** ★**逐字补丁 (★三条·★**不应用**★)**: ★**每处陈旧 pin 的判决源怎么从「写死常量」换成「硬基线 ∪ 台账链头」·给出逐字改法 + 改前改后逐字原文 + 改了哪几行 (★行号★)** ⇒ ★**本单【不许】真的去改那 9 道闸的任何一行** ★
★**§5** ★**逐字补丁 (★第 4 条·★不应用★)**: ★**给 `state/gate_check.py` 的挂链建议 (★本单零挂链·挂不挂是 main 的地界★)**
★**§6** 边界自证 + 机器块

### ★★2-2 · 新机器闸 `MECH/check_mech_signed_append_ledger.py` (★新建★)

★**判据 (★照 `SW/tools/check_sw_board_md5_rebase_readiness.py` 的 H4/H5 形状·★但 MECH 域口径★) ★**

| ★判据★ | ★内容★ |
|---|---|
| ★**M1** ★ | ★**枚举**: ★**MECH 域每一道闸里「把别的文件的 md5 写死成常量」的 pin (★代码级可查·★自己解析·不许手抄本单的表★) ⇒ ★**逐处列出来** ★ |
| ★**M2** ★ | ★**陈旧检测**: ★**每处 pin 的「写死基线」vs「盘上现值」不等 ⇒ 判红** (★★**红的是现状不是闸故障★**·★与 `MECH/check_fts_seat_sample_plan.py` 的既有口径一致★) ★ |
| ★**M3** ★ | ★**归因可查**: ★**每一处陈旧 pin ⇒ 必须在台账里查到一行 (★单号 + 文件 + prev_md5 + md5★) ⇒ 才算【已登记的合法追加】; 查不到 ⇒ ★**判红 = 「来源不明的漂移」** ★ |
| ★**M4** ★ | ★**★不许靠改常量消红★**: ★**判据里明确写死: ★**「某处 pin 从陈旧变成绿, 只有两条路: ① 它进了台账 (有单号) ② 它的基线常量被显式改成了现值 —— 而第 ② 条 ★**必须同时在台账留一行** ★**否则 = 「悄悄换基线」⇒ 判红** ★★** ⇒ ★**这条是本闸最核心的护栏 (★照 R7「悄悄换真源照样红」的思路·★照 `SW/SW_MD5_BASELINE_LEDGER.md` 里「替代防线 = 台账 append-only + 链完整性判据 fail-closed」的口径★)** ★ |
| ★**M5** ★ | ★**板三证未动** (★md5 / mtime / size 三项 == 基线★) |
| ★**M6** ★ | ★**证据分级五级白名单 + 零挂起措辞** (★`[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]`·★**零「等原厂回信」类措辞**★) |
| ★**M7** ★ | ★**零挂链** (★`grep -c check_mech_signed_append_ledger state/gate_check.py` 必须 = 0★) |
| ★**M8** ★ | ★**自证**: `--selftest` 须有 ★**反向用例 ≥8 条★·★**至少一条专打 M4 (「悄悄改常量 ⇒ 必红」)★** ★ |

★**★⚠ 预期读数 (★你的闸【今天】裸跑就是红的★)**: ★**M2 ⇒ M3 会判红那 3 处已陈旧 pin ⇒ rc≠0 是【现状】不是闸故障** ★
★**★⇒ ★**与 `MECH/check_fts_seat_sample_plan.py` 的既有口径完全一致 (★它裸跑 rc=1 · 自测 rc=0 · 末行 `ALL TESTS PASS`★) ★★** —— ★**★若你的闸裸跑 rc=0 ⇒ 说明你把 M4 写松了 ⇒ 收工验收就白搭★ ★★**

### ★★2-3 · 交卷页 `HANDOFF/2026-11-24_mech-lead_ISS399_MECH域已签收件追加台账设计与自守闸.md` (★新建★)

★**B1** 结论摘要 (★一句话★) ★**B2** 验收标准自评 (★逐条 通过/不通过/未验★) ★**B3** 证据分级 ★**B4** 接口取值声明 (★interface_claims★) ★**B5** 未决项与卡点 (★要 main 回话的·每条带代价·★**一条都不代拍**★) ★**B6** 自证复现命令 (★必跑命令原样输出 + rc★) ★**B7** 边界自证 (★含板三证指纹★)

---

## ★★三 · 必须交给 main 的四条 (★**本单一条都不代拍**★) ★★

| ★编号★ | ★问 main 什么★ | ★不答的后果★ | ★本单的建议默认值 (★仅供参考·★**决定权是 main 的**★) ★ |
|---|---|---|---|
| ★**M-A** ★ | ★**MECH 域【已签收件追加登记台账】放哪 / 叫什么 / 谁写** ★ (★候选: 新建 `MECH/SIGNED_APPEND_LEDGER.md` / 复用 `HW/SCHEMATIC_LANDING_V1_LANDED.md` 的 MECH 段 / 别的★) ★ | ★**台账没落位 ⇒ 3 处陈旧 pin 永远归不了因 ⇒ 板那一趟每一处合法追加都变成「来源不明」⇒ 收工验收的红没法判读** ★ | ★**新建 MECH 域自己的台账** (★理由: `HW/SCHEMATIC_LANDING_V1_LANDED.md` 是【板侧落表台账】, ★MECH 页的追加式订正**不是落表**·塞进去会污染那条链★) ★ |
| ★**M-B** ★ | ★**已陈旧的 3 处基线怎么追平 (★追平到「台账登记值」还是「显式改常量 + 台账留一行」★)** ★ | ★**3 处永久红 ⇒ 每个跑这道闸的 agent 都要自己写「这红不是我造成的」⇒ 噪音永续** ★ | ★**走台账登记值 (★与 ISS-303 N6 同形★)·★**但台账是 M-A 拍完才存在·所以本单只能出逐字补丁·不能自己落** ★ |
| ★**M-C** ★ | ★**M2/M3 这道自守闸挂不挂 `state/gate_check.py`** ★ | ★**不挂 ⇒ 下一个 agent 新造一道钉 md5 的闸, 照样从缝里溜过去 (★SW 侧 H4 抓的就是这个★)** ★ | ★**挂 (★与 SW 侧 `check_sw_board_md5_rebase_readiness.py` 同等待遇★)·但★**挂链是 main 的机制地界★ ⇒ 本单零挂链, 只出建议** ★ |
| ★**M-D** ★ | ★**「追加式订正」在 MECH 域到底算不算「合法变更」(★本单按 house 现有规矩默认【算】·★但 K7/K5 两条判据说【已签收件不许改】★)** ★ | ★**口径不定 ⇒ 台账与判据打架 ⇒ 闸永远红** ★ | ★**算合法, 但必须在台账留原子记录 (★与「老字逐字未删」的自证绑定★) ⇒ 判据从「不许改」变成「不许【悄悄】改」** ★ |

★★**★⇒ 本单【一条都不代拍】: 上面 4 条全部走 `needs_from` 交 main, 每条带代价。★★**

---

## ★★四 · 落盘顺序与时间预算 (★LESSONS.md L-13「先落盘, 再继续」★) ★★

★★**总预算: ★**90 分钟** (★`runTimeoutSeconds = 5400`·★★**不许再出现「读完了 60 分钟才打算写」的形状**★) ★★**

| ★步★ | ★时限★ | ★做什么★ | ★**这一步结束【必须】在盘 (★不然就是重蹈覆辙★)** ★ |
|---|---|---|---|
| ★**1** ★ | ★**≤10 min** ★ | ★**先建交卷页骨架** `HANDOFF/2026-11-24_mech-lead_ISS399_MECH域已签收件追加台账设计与自守闸.md` (★B1~B7 七个 `##` 标题先占位·正文可先空★) ★ | ★**交卷页骨架在盘** ★ |
| ★**2** ★ | ★**≤25 min** ★ | ★**自己写脚本枚举 MECH 域全部 pin** (★代码级解析·★**不许手抄本单 §1 的表**★) ⇒ ★**逐处落进真相页 §1 的清账表** ★ | ★**真相页 §1 清账表在盘 (★35 处逐处一行·★数得出来★)** ★ |
| ★**3** ★ | ★**≤40 min** ★ | ★**逐条裁定 3 处已陈旧 pin** (★自己跑 `md5sum` + 查哪个单改的 + 查老字是否逐字保留★) ⇒ 落进真相页 §2 ★ | ★**真相页 §2 三条裁定在盘** ★ |
| ★**4** ★ | ★**≤60 min** ★ | ★**写真相页 §3 台账设计 + §4 三条逐字补丁 (★不应用★)** ★ | ★**真相页 §3/§4 在盘** ★ |
| ★**5** ★ | ★**≤78 min** ★ | ★**写新闸** `MECH/check_mech_signed_append_ledger.py` (★M1~M8 + `--selftest` ≥8 条反向用例·★含一条专打 M4★) ★ | ★**新闸在盘 · 裸跑 rc≠0 (现状红) · `--selftest` rc=0 · 末行 `ALL TESTS PASS`** ★ |
| ★**6** ★ | ★**≤85 min** ★ | ★**写分片** (★`python3 state/frag_write.py --agent mech-lead`★: 产出物 + interface_claims + 4 条 needs_to_main★) ★ | ★**`grep -c "iss399" state/fragments/mech.yaml` ≥ 1** ★ |
| ★**7** ★ | ★**≤90 min** ★ | ★**验收全跑 + `merge.py` + `gate_check.py` + 贴 rc 收工** ★ | ★**交卷消息** ★ |

★★**★⇒ ★**第 1 步 (建骨架) 是本单最关键的一步 ★★** —— ★**本仓已吃过 3 次同款亏 (★ISS-393 cont1 读 45 分钟零落盘 / ISS-387 cont1 25 分钟零落盘 / ★**上一轮 ISS-398 读 60 分钟零落盘**★) ⇒ ★**8 分钟内先把骨架立起来, 剩下 80 分钟全部用来【填内容】★★**

---

## ★★五 · 边界自证 (★交卷时逐条写进交卷页★) ★★

| ★边界★ | ★要求★ |
|---|---|
| ★**零写板 / 零落表** ★ | 板 / 网表 / 脚表 / BOM / 原理图真源 一个字节不许动 (★**板 md5 必须是 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · size `4940213`** ★) |
| ★**★零改既有闸★** ★ | ★**那 9 道闸 (★含 `MECH/check_connector_clearance_caliber.py` / `MECH/check_zoujuan_marker_consistency.py`★) 的判据 / 阈值 / 常量 / 正文, ★**一个字都不许动** ★★ ⇒ ★**逐字补丁只写在真相页 §4, ★**不许真的落** ★★ ⇒ ★**自证 = 那 9 道闸的 md5 开工前后逐字相同** ★ |
| ★**零改既有页面正文** ★ | 只许**新建**真相页 + 交卷页; ★**已有 MECH 页面一个字不许改** ★ |
| ★**零挂链** ★ | 新闸零挂链 (★`grep -c check_mech_signed_append_ledger state/gate_check.py` 必须 = 0★) ⇒ 挂不挂是 main 的地界 |
| ★**零外发** ★ | ★**不发任何邮件 / 询价 / 问询 / 采购 ⇒ 缺口一律【自己网上查】+ 标证据等级 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` + 查不到就写降级方案 ⇒ 没有「批一句可以发」这个选项** ★ |
| ★**不代拍** ★ | M-A / M-B / M-C / M-D 四条全交 main, 每条带「问法 + 不答后果 + 建议默认值 + 归属」 ⇒ ★**台账位置 / 口径 / 挂不挂 三件事本单一条都不许自己定** ★ |
| ★**不自签 issue_log** ★ | ★**`state/issue_log.yaml` 一个字节不许动** ★ |
| ★**只写自己分片** ★ | ★**只写 `state/fragments/mech.yaml` (★走 `python3 state/frag_write.py --agent mech-lead`★)★** |
| ★**沙盒只落项目盘** ★ | 临时产物只写 `tmp/iss399/` · 留证只写 `logs/iss399/` ⇒ **不许往系统 `/tmp` 写** (★本机 `/tmp` 配额打满 ⇒ 写那儿会出假读数 rc=120★) |

---

## ★★六 · 必跑命令 (★全部本机实跑 · 交卷时贴输出★) ★★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 MECH/check_mech_signed_append_ledger.py            # ★预期 rc≠0 (现状红·★红的是现状不是闸故障★)★
python3 MECH/check_mech_signed_append_ledger.py --selftest  # ★必须 rc=0 · 末行 ALL TESTS PASS · 反向用例 ≥8★
python3 MECH/check_connector_clearance_caliber.py          # ★基线红 2 条 (★开工前就有·★本单不许让它多红一条★)★
python3 MECH/check_zoujuan_marker_consistency.py            # ★基线红 1 条 (★同上★)★
python3 MECH/check_onepass_mech_release.py                 # ★必须 rc=0 (★MECH 侧准出汇总闸·★本单不许扰动它★)★
python3 MECH/check_demo_struct_truth.py                    # ★必须 rc=0 (★钉板闸⑧·在链★)★
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
python3 state/merge.py && python3 state/gate_check.py      # ★rc 必须 0 · Q1 必须 18/18★
grep -c "iss399" state/fragments/mech.yaml                 # ★必须 ≥1★
grep -c check_mech_signed_append_ledger state/gate_check.py # ★必须 = 0 (零挂链)★
```

★**★那 9 道 MECH 闸的 md5 (★开工前后必须逐字相同·★自己先算一遍存着·交卷时贴出来★)★**
```
★MECH/check_connector_clearance_caliber.py   ★MECH/check_debug_seat_3d_fit.py
★MECH/check_debug_seat_rework_spec.py        ★MECH/check_demo_struct_truth.py
★MECH/check_fts_seat_body_geometry.py        ★MECH/check_fts_seat_sample_plan.py
★MECH/check_fts_vs_generic_courtyard_delta.py ★MECH/check_mech_dual_caliber_gate.py
★MECH/check_zoujuan_marker_consistency.py
```
★**★板三项基线 (★只读比对★)**: 板 `611b869e13518c3c023fb178f91a0075` · 网表 `6aee500e60ba0732f83a9cf557ba90ab` · 脚表 `9174309df1ec9411ac8e8d9e80ee386a` · BOM `5b9993992405904a60ac96a020b375d8` ★
