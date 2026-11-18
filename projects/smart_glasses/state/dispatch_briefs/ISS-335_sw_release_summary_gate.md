【ISS-335 · sw-lead · ★★「板只改一次」那一趟的【SW 侧准出汇总闸】★★ · ★★对标 MECH 侧 ISS-300 的 `MECH/check_onepass_mech_release.py` · SW 侧目前【没有对标物】★★ · ★★纯新建闸类 · 零写板 · 零落表 · 零改既有闸 · 零改 `state/gate_check.py`★★】

★**这是 main 2026-11-19 00:1x 新开的单 (job cron fb67af40「ARS45 队列自动派活」)· ★派活前置三条 (★全部本机实读·不许抄任何文档里的旧数★)**:
★**① `python3 state/advance.py --json` ⇒ `internal: []`** ⇒ ★**三个总工名下零 `open` 零 `fixing`** (★hw-lead 名下 ISS-334 是 `fixing` 且**有活会话在跑** ⇒ 本轮不碰 hw-lead★)
★**② 老板 2026-11-17 00:43「接下来的目标是绘制 PCB 图」⇒ PCB 线可派**
★**③ ★★「板只改一次」铁律 ⇒ 本单只出【纯新建闸 + 作业包】, 一个字节都不许写板★**

---

## ★★★【① 病灶 (★本机实读·2026-11-19 00:0x★)】★★★

★**「板只改一次」那一趟 (S1~S13) 当天, SW 侧必跑的闸有一堆, 但【没有任何一条命令能回答「SW 侧能不能出 Gerber」】★**

★**MECH 侧【有】对标物 (ISS-300 已交卷)**:
- ★**`MECH/check_onepass_mech_release.py`** (★21,227 B · Nov 17 21:53★) ⇒ ★**一条命令给出「结构侧能不能出 Gerber」的结论 + fail-closed (★脚本不存在 / 跑不起来 / 超时 ⇒ 一律算闸红★) + 清单完备性检查 (★6 道里有 1 道不在清单里 ⇒ 汇总红★) + `--selftest` 反向用例 (★沙盒副本跑, 真件一个字节不碰★)★**
- ★**交卷单**: `HANDOFF/2026-11-17_mech-lead_ISS300_结构侧准出汇总闸.md` (★B0~B6 齐全 + 追加节★)

★**SW 侧【没有】对标物 (★本机实读确认★)**:
- ★**`ls SW/tools/` ⇒ ★【零个】release / 准出 / summary 类闸★** (★只有 16 个 `check_*.py` 单闸★)
- ★**`ls SW/` ⇒ 44 个文件里【零个】汇总闸★** ⇒ ★**⇒ 「SW 侧能不能出 Gerber」这个问题, 今天在 SW 域【没有任何机器答案】★**

★**★后果 (★与 MECH 侧 ISS-300 立单时的理由同款★)★★**:
- ★**「板只改一次」那一趟当天, SW 侧必跑闸【漏跑一条 ⇒ 没人知道】** ⇒ ★**要么先签收 (⇒ 假绿流到下一趟) · 要么收工验收时才炸 (⇒ 现场只剩两条路: ① 当场返工改板 ⇒ 板 md5 变第二次 ⇒ 整趟白跑 ② 先签收再说 ⇒ 假绿流到下一趟)★★**
- ★**★★更要命的是: 板那一趟当天, 板 md5 会【合法地】变一次 ⇒ 若 SW 侧有【钉板 md5 闸】当天必然从绿转红 ⇒ 现场最容易误读成「板改坏了」→ 去改板凑绿 → 板 md5 变第二次 → 整趟白跑★★**

★**★本机的真实读数 (★2026-11-19 00:0x 本机实跑·★全部裸跑·TMPDIR 指项目内★)★★**:
```
★SW/tools/check_brightness_biosafety.py                     rc=0
★SW/tools/check_demo_panel_spec.py                           rc=0
★SW/tools/check_demo_panel_spec_r6_chainjudge_selftest.py    rc=0
★SW/tools/check_demo_panel_spec_r6_hardprot_iss315_selftest.py  rc=0
★SW/tools/check_demo_panel_spec_r6_selftest.py               rc=0
★SW/tools/check_iss250_rknn_target_gate.py                   rc=0
★SW/tools/check_landing_trace_obligation.py                  rc=0
★SW/tools/check_load_switch_selection.py                     rc=0
★SW/tools/check_onepass_sw_sync.py                           rc=0
★SW/tools/check_rk3572_vccio_domain.py                       rc=0
★SW/tools/check_rknn_target_compat.py                        rc=0
★SW/tools/check_shutdown_semantics.py                        rc=0
★SW/tools/check_sw_ref_reachability.py                       rc=0
★SW/tools/check_sw_ref_reachability_v2.py                    rc=0
★SW/tools/check_sw_ref_reachability_v2_selftest.py           rc=0
★SW/tools/check_timing_review_adc_sync.py                   rc=0
```
★**⇒ ★★16 道单闸今天全绿 ⇒ ★【绿不是问题】· ★【没有汇总闸才是问题】★★**

★**★★两条【已实测的接线事实】★ (★本单必须照它们设计, 不许自创★)★★**:

★**【事实 1】★ 「板只改一次」那一趟当天 SW 侧必跑的闸 = ISS-321 实测的那 10 道 (★交卷页 §B1-3 逐闸读数表·★本机实读 `HANDOFF/2026-11-18_sw-lead_ISS321_SW侧改名安全性体检.md` L93~L112★)**:
| # | 闸 (★相对项目根★) | ISS-321 表里 S0 基线 | ★**今天挂在 `state/gate_check.py` 链上了吗 (★本机 `grep -c` 实读★)★★** |
|---|---|---:|---|
| 1 | `SW/tools/check_onepass_sw_sync.py` | 0 | ★**是 (2 处: EXTRA_GATES + 钉板闸⑨)★★** |
| 2 | `SW/tools/check_sw_ref_reachability.py` | 0 | ★**是 (EXTRA_GATES)★★** |
| 3 | `SW/tools/check_landing_trace_obligation.py` | 0 | ★**是 (EXTRA_GATES)★★** |
| 4 | `SW/tools/check_demo_panel_spec.py` | 0 | ★**★否 (grep -c = 0)★★** |
| 5 | `SW/tools/check_demo_panel_spec_r6_selftest.py` | 0 | ★**是 (EXTRA_GATES)★★** |
| 6 | `SW/tools/check_demo_panel_spec_r6_chainjudge_selftest.py` | 0 | ★**是 (EXTRA_GATES)★★** |
| 7 | `SW/tools/check_demo_panel_spec_r6_hardprot_iss315_selftest.py` | 0 | ★**是 (EXTRA_GATES)★★** |
| 8 | `SW/tools/check_shutdown_semantics.py` | 0 | ★**★否 (grep -c = 0)★★** |
| 9 | `SW/tools/check_timing_review_adc_sync.py` | 0 | ★**★否 (grep -c = 0)★★** |
| 10 | `SW/tools/timing_check.py` | 0 | ★**★否 (grep -c = 0)★★** |

★**★★⇒ 汇总闸的清单【必须】把【链外的 4 道 (★#4 / #8 / #9 / #10★)】也收进去 ★★ ⇒ ★★因为 ISS-321 的实测表已证明: 板那一趟当天这 4 道【会红】, 而它们【不在日常链上 ⇒ 没人会注意到它们红了】★★**
★**★⇒ 清单完备性基准 (★对标 MECH 侧 `MANIFEST_REQUIRED`★) 必须【至少】含这 10 道 ⇒ 【少一道 ⇒ 汇总红】★★**

★**【事实 2】★ ★【三道 R6 selftest 闸必须裸跑】★★ (★ISS-318 交卷页 §B4-2 实测结论·★本机复验: 这 3 个文件的 argparse 【没有】`--selftest` 参数, 只有 `--root` / `--tmpdir` ⇒ 带 `--selftest` 会 rc=2 usage 错误★)**:
- `SW/tools/check_demo_panel_spec_r6_selftest.py`
- `SW/tools/check_demo_panel_spec_r6_chainjudge_selftest.py`
- `SW/tools/check_demo_panel_spec_r6_hardprot_iss315_selftest.py`
★**⇒ 这 3 道在汇总闸里【必须裸跑 (★args 传 `()` 或只传 `--tmpdir`★)】⇒ 传 `--selftest` ⇒ 汇总闸【自己】红 ⇒ 假红 ⇒ ★★这是本单最容易踩的坑★★**

★**【事实 3】★ ★【TMPDIR 必须指项目内】★★ (★本机 `/tmp` 带 `usrquota` 且本用户配额已到顶 ⇒ 沙盒写 `/tmp` ⇒ `OSError [Errno 122] Disk quota exceeded` ⇒ 6 道闸【一起假红】★ ⇒ ISS-297 / ISS-299 两单都踩过★)**:
- ★**⇒ 汇总闸在调任何要写沙盒的闸时, 必须把 `--tmpdir` / `TMPDIR` 指向【项目内】(★例 `tmp/iss335/…`★) ⇒ 不得依赖系统临时目录★**

★**【事实 4】★ ★【`check_sw_ref_reachability_v2.py` 已交卷但【还没挂链】★★ (★本机实读: `grep -c "check_sw_ref_reachability_v2" state/gate_check.py` = **0**★)**:
- ★**ISS-332 已 verified, 交卷页 §B4-1 给出了【逐字写法】: `state/gate_check.py` 的 `EXTRA_GATES` 第 3 位 (★L222-223★) · 路径换成 v2 · `args` 传 `()` 裸跑 ⇒ ★★只改 1 行★★ · ★旧闸建议【不删文件、退出链】 (★回滚 = 改回 1 行★)★**
- ★**★★但【挂链是 main 的机制地界】⇒ ★★本单【不许改】`state/gate_check.py`★★ ⇒ ★★本单只交【给 main 的一行改法 + 挂链前的体检结论】★★**
- ★**★⇒ 因此本单必须【同时】回答一个真问题: 「汇总闸的清单里, 位号可达性闸到底该列 v1 还是 v2?」★★ ⇒ ★**给建议 + 依据, 不代拍**★**

---

## ★★★【② 本单要交的东西 (★8 件·全部新建·★不许改任何既有文件★)★★★

★**★交卷物 (8 件)★★**
1. ★**`SW/tools/check_onepass_sw_release.py`** (★新建★) ⇒ ★**SW 侧准出汇总闸本体** ★ ★**对标 `MECH/check_onepass_mech_release.py` 的 fail-closed 语义, 但判定对象是 SW 侧★**
2. ★**`SW/tools/check_onepass_sw_release_selftest.py`** (★新建·可选·★若第 1 件已内建 `--selftest` 则可不建·★建了就必须是独立入口★) ⇒ ★**反向用例: 闸脚本被挪走 / 闸跑不起来 / 闸超时 / 清单里少一道 / 闸返回非 0 ⇒ 汇总【必须红】★★**
3. ★**`SW/ONETRIP_SW_RELEASE_GATE_SPEC.md`** (★新建★) ⇒ ★**清单页: 逐道闸的 [路径 / 怎么调 (★裸跑还是带参★) / 期望 rc / 清单完备性基准 / fail-closed 四条语义 / TMPDIR 约定 / 为什么这 10 道 / 链外 4 道的来源与后果]★★**
4. ★**`HANDOFF/2026-11-19_sw-lead_ISS335_SW侧准出汇总闸.md`** (★新建★) ⇒ ★**交卷页 (★对标 `HANDOFF/2026-11-17_mech-lead_ISS300_结构侧准出汇总闸.md` 的 B0~B6 结构★) ★★B0 交付物清单 · B1 结论摘要 · B2 验收标准逐条自评 · B3 证据分级 · B4 接口取值声明 · B5 未决项与卡点 · B6 自证复现命令★★**
5. ★**`logs/iss335/`** (★新建目录★) ⇒ ★**全部机器原始输出 (★裸跑读数 / selftest 读数 / 沙盒反向用例逐条 / 零写板双证 / 闸链复跑★)★★**
6. ★**`state/fragments/sw.yaml`** (★只写这一份·★必须走 `state/frag_write.py` 原子写★) ⇒ ★**`--add-artifact` ≥3 · `--add-claim` ≥2 · `--status` 一段 ★★另: 把「汇总闸清单里 v1 还是 v2」这个问题登记成一条 `needs_from` (★key 自拟·★`to=main`·★item 写清两个选项 + 建议默认值 + 不选的后果·★★`waiting_on` 留空=等 main 拍·不是等外部·不标 `waiting_on=boss`★)★★**
7. ★**给 main 的挂链写法 (★写在交卷页 §B5 里·★不许自己改 `state/gate_check.py`★)** ⇒ ★**汇总闸若要挂链, 应进 `EXTRA_GATES` 的哪一位 + `args` 怎么传 + 挂链前必须先满足什么 (★例: v2 换链是前置★)★★**
8. ★**一条「板那一趟当天 SW 侧怎么跑」的逐字 SOP (★写在第 3 件的清单页里或交卷页 §B6★)** ⇒ ★**当天从哪一条命令开始 · 每一步期望读数 · 红了怎么办 (★★不许改板凑绿 ⇒ 停·回 main·板 md5 只许变一次★★) · 回滚三档★★**

---

## ★★★【③ 判据 (★必须逐条实跑 + 贴原样输出★)★★★

★**【J-1】★ 新闸裸跑全绿**: `python3 SW/tools/check_onepass_sw_release.py` ⇒ ★**rc=0** ★ ★并逐道列出 10 道闸各自的 rc (★不许只写「全绿」三个字★)★★
★**【J-2】★ fail-closed 四条语义【必须实测】** (★对标 MECH 侧那一份的写法★):
- ① ★**脚本不存在 ⇒ 汇总红** (★把清单里某道闸的路径临时改成不存在的名字·★沙盒副本·★不许碰真件★) ★
- ② ★**脚本跑不起来 (异常) ⇒ 汇总红** ★
- ③ ★**超时 ⇒ 汇总红** (★GATE_TIMEOUT 口径建议 300s·★对标 MECH 侧那一份的常量★) ★
- ④ ★**跑完 rc≠0 ⇒ 汇总红 + 解析 stdout 的 `[FAIL]` 行当详情** ★
★**【J-3】★ 清单完备性**: ★**清单里少一道 ⇒ 汇总红** (★对标 `MANIFEST_REQUIRED`★) ★★并且【清单完备性基准本身】必须至少含 ISS-321 那 10 道 ⇒ ★★自己少写一道也要被自己的闸抓住★★
★**【J-4】★ `--selftest` 反向用例全过**: ★**≥6 条反向用例 + ≥1 条正向对照 · rc=0** ★ ★且【必须真的在沙盒副本上跑】⇒ ★★沙盒外的真件一个字节不许碰★★
★**【J-5】★ 三道 R6 selftest 闸【裸跑】**: ★**汇总闸里这 3 道不许传 `--selftest`** ★ ★(★传了 ⇒ 汇总自己红 ⇒ 假红·★必须实测确认汇总闸调它们时 rc=0★)★
★**【J-6】★ TMPDIR 指向项目内**: ★**汇总闸全程不许依赖系统临时目录** ★ ★(★本机 `/tmp` 配额已到顶·★抄一次假红即为不合格★)★
★**【J-7】★ 零写板双证**: ★**板 md5 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413` 交卷前后逐字节相同** ★
★**【J-8】★ 零落表**: ★**`HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` 三个 md5 + mtime 交卷前后不变** ★
★**【J-9】★ 交卷前必跑 (★原样贴进回复★)**:
```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 state/merge.py      ; echo "MERGE_RC=$?"
python3 state/gate_check.py ; echo "GATE_RC=$?"
python3 state/issue_check.py; echo "ISSUE_RC=$?"
python3 SW/tools/check_onepass_sw_release.py ; echo "RELEASE_RC=$?"
python3 SW/tools/check_onepass_sw_release.py --selftest ; echo "RELEASE_ST_RC=$?"
md5sum HW/PCB/demo_mainboard.kicad_pcb ; stat -c "%y" HW/PCB/demo_mainboard.kicad_pcb
grep -cE "🔄|待填|PLACEHOLDER|施工中" SW/ONETRIP_SW_RELEASE_GATE_SPEC.md
grep -cE "🔄|待填|PLACEHOLDER|施工中" HANDOFF/2026-11-19_sw-lead_ISS335_SW侧准出汇总闸.md
grep -c iss335 state/fragments/sw.yaml
```
★**★合卷门禁 (★Q1 必须 18/18★)★★**

---

## ★★★【④ 边界 (★一条都不许越★)★★★

- ★**零写板** (★板 md5 必须仍 `611b869e13518c3c023fb178f91a0075`·★mtime 必须仍 `2026-11-06 07:07:17.362193413`★)
- ★**零落表** (★网表 / 脚表 / BOM 三个 md5 + mtime 交卷前后不变★)
- ★**★零改 `state/gate_check.py`** (★★挂链是 main 的机制地界·★本单只交「给 main 的写法」★★)
- ★**★零改既有 16 道 `SW/tools/check_*.py` 一个字节** (★本单只【聚合】·★一个判据数字都不改★) ★★尤其 `SW/tools/check_sw_ref_reachability.py` 与 `SW/tools/check_sw_ref_reachability_v2.py` 【只读调用】★★
- ★**零改既有 `SW/*.md` 正文** (★只新建本单自己的 `SW/ONETRIP_SW_RELEASE_GATE_SPEC.md`★)
- ★**零改 `HW/` 任何文件** (★含网表 / 脚表 / BOM / 板 / 作业包★)
- ★**零改 `MECH/` 任何文件**
- ★**零改 `state/issue_log.yaml`** (★★不许自签 issue_log★) · ★**零改 `state/fragments/pm.yaml` / `state/fragments/hw.yaml` / `state/fragments/mech.yaml`★★
- ★**沙盒只写 `tmp/iss335/` + `logs/iss335/` 新增件** ★★不许 `rm -rf /tmp/*` (★本机有别的 agent 在建沙盒·★且 `/tmp` 配额问题不许用删目录解决★)★★
- ★**不替老板拍板** (★板框 U-1 / P7 / W-1 / W-2 / A1 / W-4 都不许代拍★) · ★**不替 main 拍机制地界的活** (★挂链不许自己做★)★
- ★**★零外发 (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★) ⇒ ★★不许发任何邮件 / 询价 / 问询 / 采购 ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ⇒ 没有「批一句可以发」这个选项★★**
- ★**证据分级必须标**: `[官网]` / `[实测]` / `[媒体]` / `[推算]` / `[0数据]` ★★本单绝大多数读数应是 `[实测]` (★本机实跑★)★★

★**★★本单【不许做】的两件事 (★说清为什么, 免得下轮又有人踩★)★★**
- ★**① 不许把 v2 挂进门禁链** (★挂链 = main 地界·★本单只交「一行改法 + 挂链前体检」★)
- ★**② 不许把汇总闸当成「日常门禁」挂链** (★它是【板那一趟当天】的准出闸·★不是每天跑的闸·★日常链已经有 9 道钉板闸 + 8 道 EXTRA_GATES★) ★★挂不挂、挂哪儿 ⇒ 交 main 拍★★

---

## ★★★【⑤ 交卷时必须回答 main 的 4 个问题 (★写在交卷页 §B5★)★★★

1. ★**清单里的位号可达性闸 = v1 还是 v2?** ⇒ ★**给建议默认值 + 依据 + 不选的后果** ★ ★(★事实: v2 已 verified 且交卷页给了逐字写法·★但还没挂链·★本机 `grep -c` = 0★)★★
2. ★**清单里的 10 道是不是【全集】?** ⇒ ★**逐道说清「为什么它属于『板那一趟当天必跑』」+ 「有没有第 11 道漏在外面」** ★★(★本单至少要核 ISS-321 表里的 10 道 + `state/gate_check.py` 链上的 SW 闸 + `SW/tools/` 下 16 道单闸·★核完给出【差集】★★)
3. ★**汇总闸红了以后, 人该怎么办?** ⇒ ★**逐条说清「红 = 停下来」而不是「红 = 去改板」** ★★(★板 md5 只许变一次·★这是本单最重要的一句话★)★★
4. ★**本闸会不会自己假红?** ⇒ ★**逐条列出会假红的路径 (★R6 三道裸跑 / TMPDIR 配额 / 链外 4 道今天本来就红·★说明各自怎么处理★)★**

---

## ★★ 附加纪律 (★统一段·每单都有·照做★) ★★
★**① 写分片必须用 `state/frag_write.py` (★禁止 `open(p,"w")`★) ② 只写本任务允许的文件, 不碰别人的 ③ 证据分级 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` 必须标 ④ ★★不许外发任何邮件/询价/问询/采购 (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★) ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ⇒ 没有「批一句可以发」这个选项★ ⑤ 交卷前跑 `python3 state/merge.py` (★rc 必须 0★) && `python3 state/gate_check.py` (★Q1 必须 18/18★) 并把输出贴进回复★**
