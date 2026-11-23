# ISS-359 · hw-lead · cont1 · ★★【main 订正版任务书】★★ (★brief 原文逐字保留在下方·未删一字★)

★★**派单人**: 项目总工 (main / moli) · ★**派活时间**: 2026-11-23 12:4x · ★**cron 775d9893** ★
★★**主线口径**: ★**当前主线 = 绘制 PCB 图** (老板 2026-11-17 00:43) ⇒ PCB 线可派 ⇒ ★**但「板只改一次」⇒ 本单是【纯分片卫生类】· 零写板·零落表·零外发** ★
★★**外发口径**: ★**零外发** (老板 2026-11-11 19:31 + 2026-11-12 02:02) ⇒ 不许发信/不许联系供应商/不许下采购单 ★

---

## ★★A. main 订正 (★3 条·★下面 B 段才是 brief 原文·★A 段只【更正事实】与【加安全规则】·不删 brief 任何一条任务项★★)

★★**A-1 · ★【brief 的一处机制事实错误·已订正】★★ (★承 ISS-358 cont1 先例: 同一类错已在 ISS-358 cont1 被订正过一次★) ★
- ★**brief 说**: 「★**合并器 `state/merge.py` 对「同一个 `_by` 的多条同 key answers」只认第一条 ⇒ 后写的不可见**★」
- ★**main 2026-11-23 12:4x 本机实读 `state/merge.py` (★行号为准★)**:
  - ★**L264-270**: `answers_by_key.setdefault(k, []).append({**a, "_by": aid})` ⇒ ★**同 key 的所有 answers 全部进列表** ★
  - ★**L295**: `ans = [a for a in answers_by_key.get(k, []) if a["_by"] == ask_to]` ⇒ ★**收集全部匹配项·不是只取第一条** ★
  - ★**L333-335**: need 的 `answers` 字段 = ★**全部匹配 answer 的 `{by,value,ref}` 列表** ★
- ⇒ ★**⇒ 事实订正: 同 key 多条 answers 对下游【全部可见】(进同一个 `answers[]` 数组), 不是"后写的不可见"** ★
  ⇒ ★**⇒ 因此 brief (1) 里「2 组高危 answers」的真实危害不是【丢数据】, 而是【同 key 并排 ⇒ 下游读到两条自相矛盾/不同时点的值 ⇒ 取值歧义】** ★
  ⇒ ★**★本单对 answers 的动作口径: 「让每个 key 唯一 + 一条内容都不许丢」照样做 (brief 的目标不变), 但★不许按「后写不可见」的假设去改·也不许因为"反正合并器全收"就跳过不处理★** ★
  ⇒ ★**★补测硬证据 (main 实读 STATE.yaml)★**: `iss081_pin_budget_carrier` 的 2 条 answers 在 hw-lead 域的 need 里★**并排可见** (2 个 `{by,value,ref}`); `iss287_baseline_readings` 同理 ★

★★**A-2 · ★【brief 的一处"合并取更全的那条"会丢内容 ⇒ 订正为"3 条 → 2 条"】★★
- ★**brief 说**: `s1_ref_rename_caliber_20261118` ×3 ⇒ 「★2 条逐字相同 + 1 条更长 ⇒ 合并成 1 条 (value = 更全的那条)★」
- ★**main 12:4x 本机实读 `state/fragments/hw.yaml` 的 3 条原文 (逐字比过)**:
  - ★**#0 与 #1: 逐字完全相同 (item 各 636 字, `0==1` 实测 True) ⇒ 合并成 1 条 = 零丢失** ★
  - ★**#2: 613 字, 与 #0/#1 【既不相同、也不是超集】** ★
    - ★**#0/#1 独有 (内容更长但 #2 没有)**: 「不拍的后果」成本账 ⇒ 板 md5 第二次变 (2-4 周 + ¥4-8K) + BOM 9 行证据消失并换成假话 + CPL 与 BOM 位号分叉 (贴片那天才炸) + 判据自检自崩 (假绿风险回来) + 依据行 `HW/PCB/ONETRIP_S1_REF_RENAME_CALIBER.md §2/§3/§4/§6 + logs/iss314/12_scenario_matrix.txt` ★
    - ★**#2 独有 (#0/#1 没有)**: NC 白名单三选项 甲/乙/丙-② + ★**丙-① (裸前缀 startswith) 已实测会放过真错 (反向用例② 非法 NC 0 vs 基座 4) ⇒ 本单不推荐** + 「判据解封是【两行】不是一行 (--selftest 目标 CONN_CAM 也必须跟着改名)」+ 四者 C1 三项实测 (缺失0/多余2/同号异网3) + 非法 NC 底座3/甲乙丙-②全0 + C3 不符 底座1/全0 + BOM 证据丢 17 行且无报警 (J1 判据实测) ★
- ⇒ ★**★订正: 「合并成 1 条, value 取更全的那条」★ 会静默丢掉上面一整块独有内容 ⇒ 违反 brief 自己最上面的约束「★一条内容都不许删★」★★
  ⇒ ★**★正确做法: #0/#1 (逐字重复) 合并成 1 条 (零丢失) + #2 (语义独立) 拆成独立 key 保留全文 (例 `s1_ref_rename_caliber_nc_whitelist_20261118`) ⇒ ★台账 3 条 → 2 条 (★不是 1 条★) ⇒ 老板那边看见 2 件事 (S1 改名口径 / S1 改名+NC 白名单方案) ⇒ ★**这 2 件确实是 2 件, 不是 3 件, 也不该硬压成 1 件** ★
  ⇒ ★**★配套义务 (★不许漏★)**: ★**#2 换新 key 后, 老板拍板时必须对【两个 key 各落一次 decision】(★否则只闭一条·另一条会一直挂 pending★) ⇒ 请在交卷页 §B4「接口取值声明」里写明这条, 并在交卷页 §B5「未决项与卡点」把「★新 key 需 main 在签收时把老板的决定同文落两次★」列为卡点 ★**

★★**A-3 · ★【孤儿安全规则 · brief 里没有 · 承 ISS-358 cont1 的教训补上】★★
- ★**规则**: ★**改 needs_from 的 key 之前必须先查: 有没有 answers 段用【同名 key】答过它 ⇒ 有 ⇒ 两侧一起改 ⇒ 否则那个 need 变孤儿 (合并后显示"未答复") ⇒ 未闭合数反而上涨** ★
- ★**main 12:4x 已替你查过一遍 (★写之前你必须再查一遍, 因为期间别人可能写过★)**:
  - ★`iss249_h1_reanchor_netlist_md5` ×2 ⇒ 收件人 to=sw-lead / to=mech-lead ⇒ ★**全仓 4 个分片实读: 没有任何 answers 用这两个 key** ⇒ ★**拆 key 安全** ★
  - ★`iss249_kicad_sch_md5_not_anchor` ×2 ⇒ to=sw-lead / to=mech-lead ⇒ 同上 ⇒ ★**拆 key 安全** ★
  - ★`s1_ref_rename_caliber_20261118` ×3 ⇒ ★**全仓没有任何 answers 用这个 key** ⇒ ★**改/拆安全** ★
  - ★★★**`iss081_pin_budget_carrier` ★★★ ⇒ ★★★**`state/fragments/mech.yaml` 里有 1 条 need 引用了这个 key (to=hw-lead, waiting_on 缺省) ⇒ ★★★hw.yaml 里必须【保留原 key `iss081_pin_budget_carrier` 至少一条 answer】, 否则 mech 那条 need 变未答 ⇒ 未闭合数反涨 ★★★** ⇒ ★**这一组的动作 = 把 2 条 answer 并成 1 条 (value 两条都保留: 「<=50脚仅C-min可行」「BTB按60位/载板16x16预留(勿因pin预算缩到40位)」「封装球数非风险」「建议BTB 60位+载板16x16」四段语义都要在) ⇒ 不许拆成两个 key ★**

★★**A-4 · ★【main 12:4x 实读补数 (★以你的实读为准, 数字会随并发变动·但高危 5 组不变★)】★★
- ★`python3 state/check_frag_dup_keys.py --agent hw-lead` ⇒ rc=1 · ★**高危 5 组 / 低危 24 组** (★brief 写的低危 24 组一致★) ★
- ★`s1_ref_rename_caliber_20261118` 在 STATE.yaml 的 hw-lead 域 = ★**3 条 needs_from, to 全是 main, state 全是 pending** ⇒ ★**⇒ 实锤: 同 key 登记 N 次 ⇒ 台账里就是 N 条未闭合需求 (这条老板拍板项在台账里被算成 3 条)★** ★
- ★**板面双证**: `HW/PCB/demo_mainboard.kicad_pcb` md5 = ★`611b869e13518c3c023fb178f91a0075` · mtime = ★`2026-11-06 07:07:17.362193413` ⇒ 逐字节未动 (18 天) ★
- ★**分片基线 (★给你当并发哨兵★)**: `state/fragments/hw.yaml` md5 = ★`dd73d31621ebac6105d19cfc2469d0f0` (★main 12:43 实读★) ⇒ ★**你写之前再记一次 md5; 若与上面这个不同 ⇒ 说明期间有人写过 ⇒ 按 brief 的并发规则: 停下 + 写进交卷页 (不要静默覆盖)★** ★
- ★**期望结果 (★用来验收, 不是用来交差★)**: ★**hw-lead 域 needs_from 里 pending 条数 3 → 2 (本单只减这 1 条; 其余 4 组的拆分/合并不改变 need 计数 ⇒ 全局"内部未闭合"应从 301 → 300)** ⇒ ★**若你的实测不是这个数 ⇒ 说明没改到位或改坏了 ⇒ 交卷页写清实测数** ★

★★**A-5 · ★【边界补充 · 与 brief 一致, 只是重申】★★: ★**零写板** (板 md5 不许变) · ★**零落表** (不许改 `PROJECT_TRACKER.md` §0 锁死表) · ★**只写 `state/fragments/hw.yaml`** (★只走 `state/frag_write.py`★·★**不许写 pm.yaml / sw.yaml / mech.yaml —— 那是别人的地界★**) · ★**零外发/零采购** · ★**不替老板拍板 · 不新增拍板项** (★`s1_ref_rename_caliber_20261118` 与 A-2 的新 key 都是【老板要拍的那件事】·★你只清重名登记, 不许自己给口径★) · ★**证据分级必标** · ★**不许改 `state/merge.py` / `state/gate_check.py` / `state/frag_write.py` / `state/check_frag_dup_keys.py`** ★

---

## ★★B. brief 原文 (★`state/advance.py --json` 给的 ISS-359 task_brief 全文·★md5 `91fb4fc2831a9f47d9280dc947f450f8` · len 3554 · ★一字未删未改★★)

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

