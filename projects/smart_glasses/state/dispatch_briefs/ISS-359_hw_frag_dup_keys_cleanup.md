# ISS-359 · hw-lead · ★★分片重名 key 清理 (★`s1_ref_rename_caliber_20261118` 被登记 3 次 ⇒ 老板那条待拍项在台账里算成 3 条未闭合★)·纯分片·零写板★

★**题**: ★**`state/fragments/hw.yaml` 里有 2 组 answers 与 3 组 needs_from 用了同一个 key 登记多次** ⇒ ★**合并器 `state/merge.py` 对「同一个 `_by` 的多条同 key answers」只认第一条 ⇒ 后写的不可见; 而 needs_from 同 key 登记 N 次 ⇒ 台账里这一条会被算成 N 条未闭合需求** ⇒ ★**其中最要命的是 `s1_ref_rename_caliber_20261118` ×3 —— 它正是「★S1 位号改名口径必须开工前拍★」这条【老板待拍项】⇒ 同一件事在台账里占了 3 条 ⇒ 未闭合需求数虚高, 且老板一眼看过去会以为有 3 件事要拍** ★

★**main 2026-11-23 09:1x 本机实读 (不抄任何 agent 报告)★**: ★**体检器 `state/check_frag_dup_keys.py --agent hw-lead`** ⇒ ★**高危 5 组**:
- ★`answers[iss081_pin_budget_carrier]` **×2** ⇒ ★**被 `mech.yaml` 的 need `iss081_pin_budget_carrier` (to=hw-lead) 问到 ⇒ 合并只认第一条·★另一条对下游不可见★** ★
- ★`answers[iss287_baseline_readings]` **×2** ⇒ 同型 (★暂无 need 问它·但仍会污染同 key 的取值★) ★
- ★`needs_from[iss249_h1_reanchor_netlist_md5]` **×2** ⇒ ★**同一件事登记给两个不同收件人 (sw-lead / mech-lead) ⇒ 语义上应该是 2 个不同 key** ★
- ★`needs_from[iss249_kicad_sch_md5_not_anchor]` **×2** ⇒ 同上 ★
- ★`needs_from[s1_ref_rename_caliber_20261118]` **×3** ⇒ ★**★老板待拍项被登记 3 次 (★2 条完全同文 + 1 条更长·含 NC 白名单方案★) ⇒ 台账未闭合数虚高·★这正是「待拍板面 39/42 条」这类数被算歪的来源之一★** ★
★**另: 24 组 artifacts 重名 = 低危 (同一路径登记两次·不影响取值·可顺手清)** ★

★**本单只做 3 件 (★不许扩项·零写板·零落表·零外发★)★★

### (1) ★**2 组高危 answers: 一条内容都不许删, 只让每个 key 唯一 (★按语义拆 key★)★★
- ★`iss081_pin_budget_carrier` ×2 ⇒ 两条讲的是不是同一件事? ★**若是 ⇒ 合并成一条 (★value 取更全的那条·★另一条的独有信息要并进去, 不许丢★)★; 若否 ⇒ 拆成两个语义独立的 key★** ⇒ ★**★并检查 `mech.yaml` 里那条 need 问的是哪个 key ⇒ 改完不许出现「没人答」的破口★** ★
- ★`iss287_baseline_readings` ×2 ⇒ 同上 (★先查有没有 need 问它★) ★

### (2) ★**3 组 needs_from 重名: 拆 key, 别让同一条事占 N 个坑位 ★★
- ★`iss249_h1_reanchor_netlist_md5` ×2 ⇒ ★**收件人不同 (sw-lead / mech-lead) ⇒ 拆成两个 key (★例 `iss249_h1_reanchor_netlist_md5_sw` / `..._mech`★)⇒ ★**内容各自指向自己那份文件 (SW/SW_MD5_BASELINE_LEDGER.md vs MECH/HW_CROSS_REVIEW_TRIAGE.md)⇒ 本来就是两件事, 只是 key 写重了★** ★
- ★`iss249_kicad_sch_md5_not_anchor` ×2 ⇒ 同上 (★收件人不同⇒ 拆两个 key★) ★
- ★`s1_ref_rename_caliber_20261118` ×3 ⇒ ★**★3 条里 2 条逐字相同、1 条更长 (多了「NC 白名单方案」那段) ⇒ 合并成 1 条 (★value = 更全的那条, ★短的那两条作为「同文重复登记」写进交卷页·不许静默丢★)⇒ ★**⇒ 台账里这一条从 3 条变回 1 条·老板那边只看见 1 件事★** ★
- ★**★改 needs_from 的 key 前必须先查: 有没有 answers 段用同名 key 答过它** ⇒ ★**有 ⇒ 两侧一起改 (★否则那个 need 变孤儿·★合并后会显示「未答复」★)** ★

### (3) ★**自证 + 交卷 (★零写板★)★★
- ★**自检命令 (★交卷前跑, 原样输出贴进交卷页★)**: ★`python3 state/check_frag_dup_keys.py --agent hw-lead` ⇒ ★**rc=0 (高危 0 组)** ★
- ★**必跑**: `python3 state/merge.py` (rc=0) · `python3 state/gate_check.py` (rc=0 · Q1 18/18) · `python3 state/frag_write.py --agent hw-lead --show` · `md5sum HW/PCB/demo_mainboard.kicad_pcb` (必须 `611b869e13518c3c023fb178f91a0075`)
- ★**交卷页**: `HANDOFF/2026-11-23_hw-lead_ISS359_分片重名key清理.md` (★B1~B6 六个 `##` 标题里必须分别出现: B1 `结论` · B2 `验收标准自评` · B3 `证据分级` · B4 `接口取值声明` · B5 `未决项与卡点` · B6 `自证复现命令`) + `state/fragments/hw.yaml` 分片 (★只走 `state/frag_write.py`★) + `logs/iss359/`
- ★**★并发注意**: ★**hw-lead 此刻可能还有别的会话在写 `hw.yaml` (★ISS-356 cont2 在跑★) ⇒ ★**★写之前先 `md5sum state/fragments/hw.yaml` 记下读时基线, 写完再比一次; 若期间被别人改过 ⇒ 停下并写进交卷页 (★不要静默覆盖·★这正是本单要治的病★)** ★**

★**边界 (★一条不许越★)★★: ★**零写板** (板 md5 `611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17.362193413`) · ★**零落表** · ★**只写 `state/fragments/hw.yaml`** (★只走 `state/frag_write.py`·★**不许写 pm.yaml / sw.yaml / mech.yaml — 别人的地界★**) · ★**零外发/零采购** · ★**不替老板拍板 · 不新增拍板项** (★`s1_ref_rename_caliber_20261118` 是【老板要拍的那件事】·★你只清重名登记, 不许自己给口径★) · ★**证据分级必标** · ★**不许改 `state/merge.py` / `state/gate_check.py` / `state/frag_write.py` / `state/check_frag_dup_keys.py`** (★**根治 = 给 frag_write.py 加乐观并发断言, 那是 main 的地界·本单只清已攒下的重名★**) ★
★**做不完不许假装做完**: 交卷页写清「已做 / 未做」分界 (逐组名单) ★
