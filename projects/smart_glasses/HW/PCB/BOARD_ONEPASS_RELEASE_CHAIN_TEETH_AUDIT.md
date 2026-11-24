# ★ISS-409 · 「板那一趟」投产/放行链【有没有牙齿】—— `check_pcb_drc.py` 全仓调用档位清账 + 「未布线 ⇒ 不可下单」机器闸 ★

- ★**单号**: ISS-409 · ★**owner**: hw-lead · ★**verify_by**: main · ★**派活**: 项目总工 (main / moli) · ★**日期**: 2026-11-25 ★
- ★**性质**: ★**纯查证 + 纯分析 + 新建真相页 + 新建机器闸 + 自有分片收口** ★ ⇒ ★**零写板 · 零落表 · 零改既有闸判据 · 零改既有脚本 · 零改既有页正文 · 零挂链 · 零外发 · 不代拍 · 不自签 `state/issue_log.yaml`** ★
- ★**项目根**: `/home/yuewuya/.openclaw/workspace/projects/smart_glasses` ★
- ★**交付物**: ① 本真相页 (★§0~§7 + §6 机器块台账★) · ② 新机器闸 `HW/check_onepass_release_chain_teeth.py` (T1~T7) · ③ 交卷页 `HANDOFF/2026-11-25_hw-lead_ISS409_放行链牙齿清账与闸.md` · ④ `state/fragments/hw.yaml` (走 `state/frag_write.py`) + 留证 `logs/iss409/` + 沙盒 `tmp/iss409/` ★

---

## §0 · 一句话结论

★★**投产链准入闸 `state/chain_gate.py` L296 跑的是 `check_pcb_drc.py` 的【宽松档】(argv 里没有 `--strict`) ⇒ ③PCB 环对 `unconnected` 零敏感; 而 L299 源码注释自己写着「★布线是否完成 (不阻塞"准出", 但要报出来 —— 现在 Gerber 不能下单)★」, L309 把 `lay_txt` 只拼进【输出字符串】、不进 `x3` 判定位 ⇒ ⇒ 「板那一趟」当天只要板侧同步 (C1) 清零, `check_pcb_nets` 转绿 ⇒ ③PCB 环 (绿·绿) 判绿 ⇒ ★**哪怕 unconnected 仍是 45, 投产链准入照样放行 ⇒ Gerber 可以下单 ⇒ 板改第二次** ★** 全仓 7 个真调用点里, 【只有 1 个】 (`state/verify_and_release.sh` L53) 带 `--strict` ⇒ 「放行章」那条路今天是有牙齿的, ★**缺口在投产链准入闸 + 每日巡检链 + 候选验证链 + 板报告** ★ ★**

### §0.1 · 与 ISS-406 的关系 (★不重做 · 也不推翻★)

| | ISS-406 (已交卷) | ★**本单 ISS-409** ★ |
|---|---|---|
| ★**被查对象** ★ | ★**门禁链 `state/gate_check.py` 上那 19 个挂链槽位 (18 个不同脚本)** ★ | ★**投产 / 放行 / 巡检 / 候选验证 / 生成器写盘守卫 这条链上【谁在跑 `check_pcb_drc.py`、用的是哪一档】** ★ |
| ★**回答的问题** ★ | 「闸在不在链上 · 被调用时用的是哪一档」 | ★**「这张板能不能下单」的那几道闸, 被调用时用的是哪一档** ★ |
| 关系 | ★**被查对象不同 ⇒ 不是重做, 是补另一条链** ★ | ★**ISS-406 自己在交卷页里明写「没有改 `check_pcb_drc.py` 的判据 (★`--strict` 开关一直在·问题是没人用它★)」—— ★**「没人用它」这句话在放行链上是【字面事实】: 全仓 7 个真调用点只有 1 个用它** ★** ★ |

---

## §1 · 本机实测事实 (★全部可复现 · 不抄任何 agent 报告★)

| # | 事实 | ★**实测读数** ★ | ★**出处 (本机实读/实跑)** ★ | ★**证据等级** ★ |
|---|---|---|---|---|
| ① | ★**命门闸的宽松档是恒真判据** ★ | `state/check_pcb_drc.py` L134-L139 逐字: `strict = "--strict" in sys.argv` · `ok4 = (n_unc == 0) if strict else True` ⇒ ★**不带 `--strict` ⇒ C4 unconnected 恒判绿** ★ | `state/check_pcb_drc.py` L134-L139 | ★`[实测]` ★ |
| ② | ★**投产链准入闸的 PCB 环跑的是宽松档** ★ | `state/chain_gate.py` L296 逐字: `rc2, _ = run([sys.executable, "state/check_pcb_drc.py"])` ⇒ ★**argv 里没有 `--strict`** ★ ⇒ ③PCB 环的 DRC 判定 ★**对 unconnected 零敏感** ★ | `state/chain_gate.py` L296 | ★`[实测]` ★ |
| ③ | ★**「布线未完成」在投产链里只"报出来"、不参与判定** ★ | L299 源码注释逐字: `★布线是否完成 (不阻塞"准出", 但要报出来 —— 现在 Gerber 不能下单)★` ⇒ `lay_txt` 只拼进 L309 的 `stage(...)` 输出字符串, ★**不进 `x3` / 不进任何判定位** ★ | `state/chain_gate.py` L299-L309 | ★`[实测]` ★ |
| ④ | ★**投产链 ③PCB 今天之所以红, 靠的是另一道闸, 不是 DRC** ★ | `check_pcb_nets` 今天 rc=**1** (C1: 缺失 **0** / 多余 **2** / 同号异网 **3**) ⇒ ③PCB 红; 而 `check_pcb_drc` 宽松档 rc=**0** ⇒ ★**「未布线」这一项今天完全没参与 ③PCB 的判定** ★ | `bash state/pcbnew_py.sh state/check_pcb_nets.py` (rc=1, `logs/iss409/check_pcb_nets.log`) + `bash state/pcbnew_py.sh state/check_pcb_drc.py` (rc=0, `logs/iss409/check_pcb_drc_lenient.log`) | ★`[实测]` ★ |
| ⑤ | ★**⇒ 本单最硬的一句推论 (★这就是「板改第二次」的机器级根因★)** ★ | ★**「板那一趟」做完板侧同步 (C1 多余焊盘/同号异网清零) ⇒ `check_pcb_nets` 必然转绿 ⇒ 此时 ③PCB 的两个因子变成 (绿·绿) ⇒ ★**哪怕 unconnected 仍是 45, 投产链准入闸的 PCB 环照样判绿 ⇒ Gerber 可下单** ★** ⇒ ★**「板改第二次」在今天这套闸上是【畅通无阻】的** ★ | 由 ②③④ 三条逐字源码 + 实跑读数推出 (★逻辑推论, 但每一步都可复现★) | ★`[推算]` (★基于 `[实测]` 源码与读数★) ★ |
| ⑥ | ★**宽松档的输出长什么样 (★假绿的样子, 必须原样留证★)** ★ | 宽松档实测打印 ★**「✅ C4 unconnected items = 45」** ★ + ★**「✅ 全过 —— 图纸可下单 (★前提: ISS-158 的三件规格回来后重跑生成器再验一遍)」** ★ 且 rc=**0** | `logs/iss409/check_pcb_drc_lenient.log` (本单实跑) | ★`[实测]` ★ |
| ⑦ | ★**严格档对照 (★unconnected 项必须不同★)** ★ | 严格档实测打印 ★**「❌ C4 unconnected items = 45 (--strict: 布线完成后必须为 0)」** ★ + ★**「❌ 不通过 1 项: C4 45 项未连接」** ★ 且 rc=**1** | `logs/iss409/check_pcb_drc_strict.log` (本单实跑) | ★`[实测]` ★ |
| ⑧ | ★**全仓清账: 谁在跑 `check_pcb_drc.py`, 谁带了 `--strict`** ★ | ★**真调用点 (invoke) 共 7 个 ⇒ 带 `--strict` 的只有 1 个 (`state/verify_and_release.sh` L53)** ★; ★**其余 6 个全是宽松档** ★ | `HW/check_onepass_release_chain_teeth.py` 的 AST/.sh 逻辑行实扫 ⇒ `logs/iss409/live_scan_inventory.txt` | ★`[实测]` ★ |
| ⑨ | ★**「抄日志里的 DRC 文本」的点共 5 处 / 4 个脚本** ★ | `state/finish_line.sh` L102 · `state/auto_release_if_ready.sh` L151 · `state/chain_next_round.sh` L61+L65 · `state/watch_v25.sh` L57 ⇒ ★**它们的日志全部由 `state/verify_and_release.sh` (严格档) 生产 ⇒ 只是展示真值, 不是判据** ★ | 同上实扫 + 各脚本上游实读 | ★`[实测]` ★ |
| ⑩ | ★**板 md5 自 2026-11-06 起未动, 19 天** ★ | `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` (ns `1793920037362193413`) · size `4940213` | `md5sum` + `stat` | ★`[实测]` ★ |
| ⑪ | ★**G1 仍开, 不许投板 (★所以这一趟现在是"唯一一次机会"★)** ★ | ★**`state/stage_gate.py` 当前 G1 · 还差 1 项 = PCB 布线 unconnected 45→0 (DRC 违规 0 已达标)** ★ | `python3 state/stage_gate.py` | ★`[实测]` ★ |
| ⑫ | ★**「未布线 ⇒ 不可下单」这条, 今天只有 3 道闸是【绝对闸】, 而它们都不在投产链准入闸上** ★ | ★**绝对闸 = `state/check_pcb_drc.py` (仅 `--strict` 时) · `state/verify_and_release.sh` L53 · `state/stage_gate.py` L220-225** ★ ⇒ ★**投产链准入闸 `chain_gate.py` 自己是【相对闸】(只判 C1 焊盘级等价)** ★ | 本单逐闸静态实读 ⇒ §4 表 (c) | ★`[实测]` ★ |

### §1.1 · ★**与派活单的一处精度修正 (★只改精度 · 不改结论★)** ★

| 派活单写的 | ★**本机实算** ★ | 性质 |
|---|---|---|
| ⑦ 「`state/finish_line.sh` L102 · `state/auto_release_if_ready.sh` L151 逐字 = `grep -E ...` ⇒ ★**它们采信的是上游宽松档跑出来的日志文本 ⇒ 宽松档的假绿会一路被抄到「放行」结论里** ★」 | ★**这两处的上游是 `state/verify_and_release.sh` (★全仓唯一带 `--strict` 的真调用点★) ⇒ 它们抄到的是【严格档日志里的真值】(「❌ C4 unconnected items = 45」) ⇒ ★**不是假绿放大器** ★** —— 但真正被假绿污染的证据链在别处: `state/board_report.sh` L59 (★宽松档★) ⇒ L60 把「✅ C4 unconnected items = 45」抄进板报告 ⇒ 而 `state/promote_arm.sh` L67 把这份报告当「臂晋级官方板后的全量取证」** ★ | ★**结论方向不变 (假绿确实在放行链上), 但★**「谁抄了假绿」这一条指错了对象** ★** ⇒ 本单把它改到 `board_report.sh` 上 (见 §3 表 (b))** ★ |

★⇒ ★**本单【没有】推翻派活单的 ⑤ (板改第二次畅通无阻) —— ⑤ 的根因在 `chain_gate.py` L296, 与 ⑦ 无关** ★

---

## §2 · 表 (a) · 全仓 `check_pcb_drc.py` 调用点全集 × argv × 档位 × 链 × 后果

★**扫描口径 (本机实扫 · 判据从源码 AST/.sh 逻辑行实读 · 不许手抄清单)** ★
- ★**扫描范围**: `state/` `HW/` `SW/` `MECH/` 下全部 `*.sh` `*.py` = ★**1193 个脚本** ★
- ★**命中含 `check_pcb_drc` 的文件 = 50 个** (★≥ 8 ⇒ 扫描没漏·见 §6 新闸 T1a★)
- ★**两处显式排除 (写在台账里 · 不暗箱)**: ① `state/check_pcb_drc.py` (★被调用的工具本体, 不是调用点★) · ② `HW/check_onepass_release_chain_teeth.py` (★本闸自己·它的每一处提及都在字符串/文档里★)
- ★**分类法**: `invoke` (真执行) · `loggrep` (抄日志里的 DRC 文本) · `label` (回显名字/rc) · `doc` (散文/文档/一次性脚本)

### ★2.1 · 表 (a)-1 · ★**真调用点 (invoke) —— 7 个, 全表都在这里★** ★

| # | 文件 | 行 | argv (逐字) | `--strict`? | ★**链** ★ | ★**结果怎么用 (use)** ★ | ★**宽松档假绿的后果** ★ |
|---|---|---|---|---|---|---|---|
| ★**CS01** ★ | `state/chain_gate.py` | **296** | `run([sys.executable, "state/check_pcb_drc.py"])` | ★**❌ 无** ★ | ★**投产准入 (③PCB 环)** ★ | ★**judgement** ★ (L298 `x3 = x3 and rc2 == 0`) | ★★**这就是命门**: ③PCB 环今天之所以红靠的是 `check_pcb_nets` (C1), **不是 DRC** ⇒ ★**板侧同步一做完 ⇒ (绿·绿) ⇒ 投产链准入放行 ⇒ unconnected=45 的板过了投产链 ⇒ Gerber 可下单** ★ ★ |
| ★**CS02** ★ | `state/board_report.sh` | **59** | `bash state/pcbnew_py.sh state/check_pcb_drc.py "$PCB" >/tmp/_c2.log 2>&1` | ★**❌ 无** ★ | ★**放行 (板报告/取证)** ★ | ★**display** ★ (L59 回显 rc; L60 `grep -E "unconnected\|violations" /tmp/_c2.log`) | ★**假绿的物理传播口**: 宽松档日志里那行是 ★**「✅ C4 unconnected items = 45」** ★ ⇒ L60 原样抄进板报告 ⇒ ★**`state/promote_arm.sh` L67 把这份报告当「臂晋级官方板后的全量取证」⇒ 报告上写着绿勾** ★ |
| ★**CS03** ★ | `state/verify_candidate.sh` | **26** | `bash "$PROJ/state/pcbnew_py.sh" "$PROJ/state/check_pcb_drc.py" "$CAND" 2>&1 \| grep -vE "^$\|Debug:" \| tail -25` | ★**❌ 无** ★ | ★**候选验证** ★ | ★**discarded** ★ (rc 被管道吃掉) | ★**脚本注释 L11 承诺「① fresh DRC + unconnected ⇒ DRC 必须 0 · unc 必须比官方板低」, 但 L26 的 rc 从没被检查过 ⇒ 宽松档下 C4 又恒绿 ⇒ ★**① 号尺子对 unc 零牙齿** ★ ⇒ 候选板验收实际只靠 ② 号尺子 (`compare_arm_official.py`) 兜着 |
| ★**CS04** ★ | `state/daily_check.py` | **344** | `run("check_pcb_drc.py")` | ★**❌ 无** ★ | ★**巡检** ★ | ★**judgement** ★ (L345 `pcb_ok = (rc_pcb_rc == 0)` → L404 报红) | ★★**巡检失明**: 这条永远绿 ⇒ ★**每日巡检从来没看见过 unconnected=45** ★ ⇒ ★**这解释了为什么 daily 巡检那两条红是 `check_pcb_nets` / `chain_gate`, 而不是 unconnected** ★ ★ |
| ★**CS05** ★ | `state/replay_patch_chain.sh` | **240** | `bash state/pcbnew_py.sh state/check_pcb_drc.py "$WORK/final_chain.kicad_pcb" 2>&1 \| grep -E "C3 \|C4 " \| tee -a "$LOG"` | ★**❌ 无** ★ | 历史脚本 (臂重放) | ★**discarded** ★ | ★**臂操作员看到的是「✅ C4 unconnected items = N」(带绿勾)** ★ ⇒ 靠 ② 号尺子 `compare_arm_official.py` 兜底 |
| ★**CS06** ★ | `state/run_grid_ladder.sh` | **44** | `bash state/pcbnew_py.sh state/check_pcb_drc.py "$OUT" 2>&1 \| grep -E "C3 \|C4 \|C7 "` | ★**❌ 无** ★ | 历史脚本 (网格梯) | ★**discarded** ★ | ★**同上** ★ ⇒ 靠 `compare_arm_official.py` 兜底 |
| ★**CS07** ★ | `state/verify_and_release.sh` | **53** | `python3 state/check_pcb_drc.py --strict` | ★**✅ 有** ★ | ★**放行** ★ | ★**judgement** ★ (L54 `[ "$_rc" -ne 0 ] && FAIL=1` → L90-94 不盖章) | ★**无 (这一处是真闸)** ★ ⇒ ★**全仓唯一带 `--strict` 的真调用点** ★ ⇒ ★**「放行章」这条路今天是有牙齿的** ★ |

### ★2.2 · 表 (a)-2 · ★**抄日志里的 DRC 文本 (loggrep) —— 5 处 / 4 个脚本** ★

| # | 文件 | 行 | 抄什么 | ★**日志由谁生产** ★ | ★**上游是严格档?** ★ | 判决 |
|---|---|---|---|---|---|---|
| ★**LG01** ★ | `state/finish_line.sh` | 102 | `grep -E "unconnected items\|DRC violations\|check_pcb_nets rc\|check_pcb_drc\|chain_gate rc\|stage_gate rc\|G1\|放行" /tmp/verify_final.log \| head -14` | ★**`state/verify_and_release.sh` (严格档)** ★ | ★**✅ 是** ★ | ★**只是展示真值** ★ (不是判据) |
| ★**LG02** ★ | `state/auto_release_if_ready.sh` | 151 | `grep -E "DRC violations\|unconnected items\|C3 DRC\|C4 unconnected\|..." /tmp/auto_release.log \| head -24` | ★**`state/verify_and_release.sh` (严格档)** ★ | ★**✅ 是** ★ | ★**只是展示真值** ★ (盖章与否看 `$rc`) |
| ★**LG03** ★ | `state/chain_next_round.sh` | 61 | `grep -E "DRC violations\|unconnected items\|..." /tmp/chain_verify.log \| head -24` | ★**`state/verify_and_release.sh` (严格档)** ★ | ★**✅ 是** ★ | ★**只是展示真值** ★ |
| ★**LG04** ★ | `state/chain_next_round.sh` | 65 | 同上 (追加进 `CUR_LOG` 的那一份) | ★**`state/verify_and_release.sh` (严格档)** ★ | ★**✅ 是** ★ | ★**只是展示真值** ★ |
| ★**LG05** ★ | `state/watch_v25.sh` | 57 | `grep -E "unconnected items\|DRC violations\|..." /tmp/verify_v25.log \| head -20 \| tee -a "$OUT"` | ★**`state/verify_and_release.sh` (严格档)** ★ | ★**✅ 是** ★ | ★**只是展示真值** ★ |

★⇒ ★**这 5 处【不是】假绿放大器 (★上游全是严格档★) —— 但它们也【不是】保险: 它们只是在【显示】真值, 一旦上游哪天换成宽松档, 它们会立刻变成假绿的搬运工 ⇒ 本单把「上游是不是严格档」做成机器闸 T3d (★缺登记 / 非严格档 ⇒ 判红★)** ★

### ★2.3 · 表 (a)-3 · ★**回显名字/rc (label) —— 2 处** ★

| # | 文件 | 行 | 逐字 | 判决 |
|---|---|---|---|---|
| ★**LB01** ★ | `state/board_report.sh` | 59 | `echo "  check_pcb_drc   rc=$?"` | ★**回显宽松档的 rc=0 ⇒ 板报告上写着「check_pcb_drc rc=0」** ★ |
| ★**LB02** ★ | `state/verify_and_release.sh` | 53 | `echo "  check_pcb_drc(--strict) rc=$_rc"` | ★**回显严格档的 rc (今天 = 1)** ★ |

### ★2.4 · 表 (a)-4 · ★**散文/文档/一次性脚本 (doc + comment) —— 39 个文件** ★

★**全表在 §6 机器块的 `candidates` 数组里 (逐个文件一行, 机器闸 T1b 双向对拍)** ★
★**要点**: 其中 ★**`state/chain_tool_stamp.py` L54 把 `check_pcb_drc.py` 列进 `TOOLS` 只是要算它的 sha256 戳 (不跑它)** ★ · ★**`state/gen_pcb_netlist_board.py` L9 · `state/gen_pcb_components.py` L15 · `state/gen_kicad_project.py` L38 都只是文档提及** ★ · ★**`state/_apply_*.py` / `state/_land_*.py` / `state/.gen_src_*.py` 共 28 个是一次性工单/落账脚本, 它们的提及全在散文里 (AST 实读确认)** ★ · ★**`state/_apply_20261122_2150_cronfb67_sign_iss339.py` AST 解析失败 (L11 `invalid decimal literal`) ⇒ 按 T4【显式登记为 `unparsed`】(★不装没看见★) ⇒ 其 L30 的提及经人工读源码确认是散文 (记 md5) ★**

---

## §3 · 表 (b) · 逐点判决表 (★必须带 `--strict` / 骨架阶段故意宽松 + 兜底闸 + 兜底在不在链上★)

| # | 调用点 | ★**判决** ★ | ★**依据** ★ | ★**该改成什么 (★建议 · 落不落由 main 拍★)** ★ |
|---|---|---|---|---|
| ★**CS01** ★ `state/chain_gate.py` L296 | ★**必须带 `--strict`** ★ | ★**这是投产链准入闸的 PCB 环; 它现在是【相对闸】(只判 C1), 而投产链准入的语义要求它是【绝对闸】(unconnected=0) ⇒ 判红** ★ | L296 argv 无 `--strict`; L299 注释自写「不阻塞准出」; L309 `lay_txt` 不进 `x3` | ★**一行**: `run([sys.executable, "state/check_pcb_drc.py", "--strict"])` ★ ⇒ ★**③PCB 环当天会红 (unconnected=45) —— 这正是「板只改一次」想要的效果** ★ |
| ★**CS02** ★ `state/board_report.sh` L59 | ★**必须带 `--strict`** ★ | ★**这份报告是 `promote_arm.sh` (臂→官方板) 与 `finish_line.sh` (终点线) 的取证材料; 报告上带绿勾的「✅ C4 unconnected items = 45」= 假绿进证据链** ★ | L59 argv 无 `--strict`; L60 把宽松档日志原样抄进报告; `promote_arm.sh` L67 消费该报告 | ★**一行**: 加 `--strict` ★ ⇒ ★**但注意: 这会让板报告天天红 —— 因为板真的没布完 ⇒ 这道红是对的** ★ |
| ★**CS03** ★ `state/verify_candidate.sh` L26 | ★**必须带 `--strict` + ★**必须把 rc 接住** ★ | ★**脚本注释承诺「unc 必须比官方板低」, 但 L26 的 rc 被 `\| grep \| tail` 吃掉 ⇒ 承诺没有机器兑现** ★ | L26 管道; L11 注释; 消费方 `v74_arms.sh`~`v77_arms.sh` | ★**两处**: ① 加 `--strict` ② 用 `set -o pipefail` 或先存 rc 再打印 ★ ⇒ ★**但候选板本来就不是官方板, unconnected 常常 > 官方板 ⇒ 严格档在这里是【相对改善】的语义, 绝对 0 不合理 ⇒ 建议这一处改成【按候选板自身比较】而不是简单加 `--strict`** ★ (★口径属 main 地界·本单不代拍★) |
| ★**CS04** ★ `state/daily_check.py` L344 | ★**必须带 `--strict`** ★ | ★**每日巡检是「谁在看着 unconnected」的唯一常设机制; 今天它是瞎的** ★ | L344 argv 无 `--strict`; L345/L404 是 judgement | ★**一行**: `run("check_pcb_drc.py", "--strict")` ★ ⇒ ★**巡检会新增一条红 (unconnected=45) —— 那正是巡检该报的** ★ |
| ★**CS07** ★ `state/verify_and_release.sh` L53 | ★**保持现状 (已是绝对闸)** ★ | ★**全仓唯一带 `--strict` 的真调用点; 放行章这条路今天有牙齿** ★ | L53-54 | ★**不改** ★ (★只需让它被 T2/T3 点名备案★) |
| ★**CS05** ★ `state/replay_patch_chain.sh` L240 | ★**骨架阶段故意宽松** ★ | ★**兜底闸 = `state/compare_arm_official.py` (名单制闸) ⇒ ★**兜底闸【在链上】** (被 `state/verify_candidate.sh` ② 与 `state/daily_check.py` 调用) ⇒ 不标红** ★ | ★**但宽松档会让日志里那行带绿勾 ⇒ 建议至少把它抄的行改成不带 ✅ 的原样输出** ★ | ★**可选**: 加 `--strict` (臂级 unconnected 本来就要压到 0 才可能 ACCEPT, 加了会提前红) ⇒ ★**本单建议【加 `--strict`】, 因为 `compare_arm_official` 已经要求「至少一项严格变好」⇒ 臂没布完就不该被当赢家** ★ |
| ★**CS06** ★ `state/run_grid_ladder.sh` L44 | ★**骨架阶段故意宽松** ★ | ★**兜底闸 = `state/compare_arm_official.py` ⇒ ★**兜底闸【在链上】** ⇒ 不标红** ★ | 同上 | ★**可选**: 加 `--strict` ★ |

★⇒ ★**逐点判决表结论**: ★**7 个真调用点里, 4 个【必须带 `--strict`】(CS01/CS02/CS03/CS04 —— 正是派活单点名的投产准入 / 板报告 / 候选验证 / 巡检), 2 个是【骨架阶段故意宽松但兜底闸在链上】(CS05/CS06), 1 个已经是严格档 (CS07)** ★
★⇒ ★**没有一处的兜底闸【不在链上】⇒ 本单没有「标红」的兜底缺失项; ★**真正的红是那 4 处 `must_strict`** ★**

---

## §4 · 表 (c) · 「未布线 ⇒ Gerber 不可下单」这条必须成立在哪几道闸上 · 现状缺哪几道

★**判据语义**: ★**「板没布完 ⇒ 这份 Gerber 不许下单」必须由【某一道闸】以【绝对判据】(unconnected == 0) 判红, 而不是靠人看** ★

| # | 闸点 | ★**类型** ★ | ★**在链上?** ★ | ★**它今天实际判什么 (逐字)** ★ | ★**缺口** ★ |
|---|---|---|---|---|---|
| ★**NG01** ★ | `state/check_pcb_drc.py` | ★**绝对闸** ★ | ★**✅** ★ | L135-136 `ok4 = (n_unc == 0) if strict else True` ⇒ ★**只有带 `--strict` 才判红** ★ | ★**默认是恒真 ⇒ 必须靠调用方加 `--strict`** ★ |
| ★**NG02** ★ | `state/verify_and_release.sh` L53 | ★**绝对闸** ★ | ★**✅** ★ | `python3 state/check_pcb_drc.py --strict` ⇒ L54 `FAIL=1` ⇒ L90-94 不放行 + 不盖章 | ★**无缺口 (唯一一处正确的绝对闸)** ★ |
| ★**NG03** ★ | `state/stage_gate.py` L220-225 | ★**绝对闸** ★ | ★**✅** ★ | 读 `HW/PCB/.layout_done.json` ⇒ `unconnected==0 且 drc_violations==0`; 缺失/读不出 ⇒ 视为未布线 (★宁可红★) | ★**无缺口, 但它读的是【上一次 verify_and_release 写下的实测值】⇒ 该文件的写者必须是严格档 (今天是)** ★ |
| ★**NG04** ★ | `state/chain_gate.py` L291-L309 | ★**相对闸** ★ | ★**✅** ★ | ③PCB 环 = `check_pcb_nets`(C1 焊盘级等价) ∧ `check_pcb_drc`(**宽松**) ⇒ ★**只判 C1, 不判 unconnected** ★ | ★★**核心缺口: 投产链准入闸【不判】unconnected ⇒ 板没布完也能过投产链** ★ ★ |
| ★**NG05** ★ | `state/promote_arm.sh` L19-L29 | ★**相对闸** ★ | ★**✅** ★ | 晋级闸只校 parity (`check_pcb_nets`); 臂板 unconnected ★**只打印不判** ★ (L19-24) | ★**缺口: 臂板只要 C1 等价就能晋级成官方板, 不看 unconnected ⇒ 绝对闸只落在第 ⑨ 步的 verify_and_release** ★ |
| ★**NG06** ★ | `state/promote_board_file.sh` | ★**相对闸** ★ | ★**✅** ★ | ① `compare_arm_official` ACCEPT + ② parity ⇒ ★**绝对闸在第 ⑨ 步 verify_and_release** ★ | ★**同 NG05** ★ |
| ★**NG07** ★ | `state/compare_arm_official.py` | ★**相对闸** ★ | ★**✅** ★ | 只认「相对官方板变好」(`unc` 变少 / 零铜变少) ⇒ ★**拦得住「变坏」, 拦不住「一直差」** ★ | ★**它不是「布完了」的闸, 是「比现在好」的闸 ⇒ 不能替代绝对闸** ★ |
| ★**NG08** ★ | `state/gen_production_pack.sh` | ★**无闸** ★ | ★**✅** ★ | 直接 `pcb export gerbers/drill/pos/ipc2581` ⇒ ★**对 unconnected 零判据 ⇒ 板没布完也能出 Gerber** ★ | ★**缺口: 「产出投产包」这一环不看布线 ⇒ 出包 ≠ 可下单, 这件事在脚本层没有任何机器拦住** ★ |
| ★**NG09** ★ | `state/check_pcb_nets.py` | ★**无闸** ★ | ★**✅** ★ | 只校焊盘级等价 (缺失/多余/同号异网) ⇒ ★**与布线完成无关** ★ | ★**今天它红 ≠ 板布完了 ⇒ ★**不能拿它当「板好了」的证据** ★ ★ |

### ★4.1 · 现状缺哪几道 (★机器闸 T7 盯的就是这张表★)

| ★**缺口** ★ | ★**今天的样子** ★ | ★**后果** ★ | ★**修法归属** ★ |
|---|---|---|---|
| ★**G1 · 投产链准入闸 (NG04) 不判 unconnected** ★ | `chain_gate.py` L296 宽松档 | ★★**板侧同步一做完 ⇒ 投产链准入放行 ⇒ unconnected=45 的板可以下单 ⇒ 板改第二次** ★ ★ | ★**main 地界 (改 `chain_gate.py` 那一行 argv)** ★ |
| ★**G2 · 每日巡检 (CS04) 不判 unconnected** ★ | `daily_check.py` L344 宽松档 | ★**没人看见 unconnected=45** ★ | ★**main 地界** ★ |
| ★**G3 · 板报告 (CS02) 把假绿抄进取证材料** ★ | `board_report.sh` L59 宽松档 + L60 grep | ★**假绿进了「臂晋级官方板」的取证报告** ★ | ★**main 地界** ★ |
| ★**G4 · 候选验证 (CS03) ① 号尺子的 rc 被管道吃掉** ★ | `verify_candidate.sh` L26 | ★**注释承诺的判据没有机器兑现** ★ | ★**main 地界 (口径可能是「相对改善」而不是绝对 0)** ★ |
| ★**G5 · 出投产包这一环 (NG08) 对布线零判据** ★ | `gen_production_pack.sh` | ★**「出包」与「可下单」在脚本层没有任何机器联系** ★ | ★**main 地界** ★ |
| ★**G6 · 臂晋级 (NG05/NG06) 只校 parity, 不校布线** ★ | `promote_arm.sh` / `promote_board_file.sh` | ★**臂板 unconnected 高也能量产 (只要第 ⑨ 步没跑到)** ★ | ★**main 地界** ★ |

★⇒ ★**一句话: 「未布线 ⇒ 不可下单」今天只由 ★**NG02 (verify_and_release.sh 严格档)** ★ + ★**NG03 (stage_gate.py)** ★ 两处真正兜着, 而这两处都不在【投产链准入闸】上 ⇒ ★**投产链准入这一环【没有牙齿】** ★**

---

## §5 · 坏结局推演 (★为什么值钱★)

★**「板只改一次」= 板 md5 全生命周期只许变 1 次** ⇒ ★**投板前的每一道检查, 都是「板改第二次」的最后一道闸** ★

| # | 坏结局 | ★**触发链 (本机实读的源码路径)** ★ | ★**今天拦得住吗** ★ |
|---|---|---|---|
| ★**① 宽松档假绿** ★ | ★**板侧同步做完 ⇒ 投产链准入放行 ⇒ Gerber 下单 ⇒ 板改第二次 (2-4 周 + 一批板的钱 + 一轮全部留证链作废)** ★ | ★**`chain_gate.py` L296 (宽松) → L298 `x3 = x3 and rc2 == 0` → L309 `stage("③ PCB", ..., x3, ...)` ⇒ `x3` 只反映 C1** ★ | ★**❌ 拦不住** ★ ⇒ ★**今天 ③PCB 红只是因为 C1 恰好还红着** ★ |
| ★**② 假绿进证据链** ★ | ★**臂晋级官方板 ⇒ 板报告上写着「✅ C4 unconnected items = 82」+「✅ 全过 —— 图纸可下单」+「check_pcb_drc rc=0」** ★ | ★**`promote_arm.sh` L67 → `board_report.sh` L59 (宽松) → L60 grep 原样抄** ★ | ★**❌ 拦不住** ★ |
| ★**③ 巡检失明** ★ | ★**每日巡检从来没看见过 unconnected=45 ⇒ 这一格处于「没人看」的状态** ★ | ★**`daily_check.py` L344 (宽松) → L345 `pcb_ok = (rc==0)` → L404 报红 (永远不会)** ★ | ★**❌ 拦不住** ★ |
| ★**④ 注释承诺落空** ★ | ★**候选验证脚本注释白纸黑字写「unc 必须比官方板低」, 而 L26 的 rc 被管道吃掉 ⇒ 承诺没有机器兑现** ★ | ★**`verify_candidate.sh` L11 (注释) vs L26 (管道)** ★ | ★**❌ 拦不住** ★ |
| ★**⑤ 唯一守住的** ★ | ★**「放行章」这条路有牙齿** ★ | ★**`verify_and_release.sh` L53 (`--strict`) → L54 `FAIL=1` → L90-94 不盖章 → `auto_release_if_ready.sh` L142-150 按 `$rc` 决定盖章** ★ | ★**✅ 拦得住** ★ ⇒ ★**★这是今天唯一没坏的环节★★** ★ |

---

## §6 · 机器块 (★台账 + 新闸 T1~T7★)

### §6.1 · 新闸 `HW/check_onepass_release_chain_teeth.py` 判据

| 判据 | 要求 | ★**今天读数** ★ |
|---|---|---|
| ★**T1 调用点全集自洽** ★ | ★**扫描全仓** (`state/` `HW/` `SW/` `MECH/` 下 `*.sh` `*.py`) 里引用 `check_pcb_drc` 的文件, ★**逐个用 AST / .sh 逻辑行实读** 判 argv 是否带 `--strict`; ★**T1a 命中文件数 ≥ 8** ⇒ 少了说明扫描漏了 ⇒ 判红; ★**T1b 台账 ↔ 实读双向一致** (候选文件集合 / (文件,行,kind) / strict 逐字相同) ⇒ 判红; ★**T1c 台账必须点名宽松档真调用点** ⇒ 判红 | ★**T1a 命中 50 个 (≥8) ✅ · T1b 双向一致 ✅ · T1c 点名 6 个宽松档真调用点 ✅ ⇒ T1 绿** ★ |
| ★**T2 放行链必须严格档** ★ | ★**投产准入 `state/chain_gate.py` · `state/board_report.sh` · `state/verify_candidate.sh` · `state/daily_check.py`** 四道闸的调用点若不带 `--strict` ⇒ 判红 | ★**❌ 4/4 全是宽松档 ⇒ T2 红 (★这就是本闸的命门判据★)** ★ |
| ★**T3 假绿输出不得被当放行凭据** ★ | ★**T3a** 「图纸可下单」在工具本体之外的每处出现都要被登记为 `quoted` ⇒ 登记为「断言」/未登记 ⇒ 判红 · ★**T3b** 每个真调用点必须登记 `use` ∈ {judgement, display, discarded} ⇒ 判红 · ★**T3c** `use=judgement` 的必须带 `--strict` ⇒ 判红 · ★**T3d** 每个抄日志的点必须登记日志源 + 生产脚本 + 生产脚本是否严格档 ⇒ 判红 · ★**T3e** `must_strict=true` 的必须登记消费方 ⇒ 判红 · ★**T3f** `must_strict=false` 的必须登记兜底闸且兜底在链上 ⇒ 判红 | ★**T3a 2 处全登记为 quoted ✅ · T3b 7/7 登记 ✅ · T3c 3 个 judgement 点 (CS01/CS04/CS07) 里 CS01/CS04 是宽松档 ⇒ ❌ 红 · T3d 5/5 上游严格档 ✅ · T3e 5/5 有消费方 ✅ · T3f 2/2 兜底在链上 ✅ ⇒ T3 红** ★ |
| ★**T4 fail-closed** ★ | ★**真相页 / 机器块 / 板文件 / `state/gate_check.py` / `state/outbox/` 任一缺失 ⇒ 判红**; ★**扫不到任何真调用点 ⇒ 判红**; ★**候选文件 AST 解析失败 ⇒ 必须被台账显式登记 (`unparsed`) ⇒ 没登记 ⇒ 判红** | ★**输入全在 ✅ · 7 个真调用点扫到 ✅ · 1 个解析失败文件已登记 ✅ ⇒ T4 绿** ★ |
| ★**T5 零挂链 + 零外发自证** ★ | 本闸名在 `state/gate_check.py` 里的行数 = 0 · `state/outbox/` 逐件 md5 + 文件集合与基线相同 | ★**grep = 0 ✅ · outbox 22 件逐件 md5 未动 ✅ ⇒ T5 绿** ★ |
| ★**T6 板指纹自证** ★ | 板 md5 / mtime(ns) / size 三项与基线逐字相同 | ★**611b869e… / 1793920037362193413 ns / 4940213 ✅ ⇒ T6 绿** ★ |
| ★**T7 「未布线 ⇒ 不可下单」闸点台账** ★ | 9 个闸点必须逐个登记 `kind` ∈ {绝对闸, 相对闸, 无闸} + `on_chain` ⇒ 缺一 ⇒ 判红; 必须 ≥1 道绝对闸 `on_chain=true` ⇒ 否则判红 | ★**9/9 已登记 ✅ · 3 道绝对闸 (NG01/NG02/NG03) 在链上 ✅ ⇒ T7 绿** ★ |

★**新闸裸跑读数: rc=1** (★红的是现状: T2 + T3 ⇒ ★**4 处放行链跑在宽松档**★, 不是闸故障) ★
★**新闸 `--selftest` 读数: rc=0 · 末行逐字 `ALL TESTS PASS` · ★**1 正向 + 20 反向 = 21 条全抓到**★ ★

### §6.2 · 机器块 (★台账 · 供新闸逐字对拍★)

★**台账字段**: `candidates` (★50 个命中文件逐个一行★) · `call_sites` (★14 条 invoke/loggrep/label, 逐条带 argv/档位/链/use/must_strict/消费方/兜底闸★) · `quoted_markers` (★假绿标记串的每处出现★) · `no_order_gates` (★9 道闸★) · `meta.outbox_baseline` (★22 件 md5★) · `meta.board_baseline` (★板三证★) ★

<!-- RELEASE_CHAIN_TEETH_LEDGER_BEGIN -->
```json
{
 "meta": {
  "iss": "ISS-409",
  "tool": "state/check_pcb_drc.py",
  "generated_at": "2026-11-25T03:40:00+08:00",
  "generated_by": "hw-lead",
  "board_baseline": {
   "md5": "611b869e13518c3c023fb178f91a0075",
   "size": 4940213,
   "mtime_ns": 1793920037362193413
  },
  "outbox_baseline": {
   "state/outbox/NO_OUTBOUND_POLICY.md": "ee23fba8b708b3535f2e8bc4ff60006b",
   "state/outbox/README.md": "bb415a7948346afd3d8e429b80f0aabf",
   "state/outbox/R_GEO_2_DECISION_MAP.md": "8e70d17a7cadd79c76175fe81a91546f",
   "state/outbox/bridge_chip_rfq.md": "f174665e3ef10713c0366eb12d2fa4bb",
   "state/outbox/j_chg_rfq.md": "79ec574be6f9f1e44f1000f65b570a90",
   "state/outbox/jbd_query.md": "b62675dda43fc84861bb9065ad7c6929",
   "state/outbox/jbd_query_addendum.md": "687ac2e080fb4a43b85c87aa125ac492",
   "state/outbox/lens_rfq_rgeo2_addendum.md": "c95a53b13823fa7a939e7a0ee0faa10b",
   "state/outbox/onsemi_ar0234cs_query.md": "009c645108d22a594fa9b0e9ed745a6a",
   "state/outbox/pcb_foundry_layer_query.md": "1f8105e7efd5b48f1ca4d4fd4229df43",
   "state/outbox/s2_rk3576_module_vendor_query.md": "963395a7f9cff7d9721909262d03ed7a",
   "state/outbox/som_balltable_inquiry.md": "1c39347cb28432b687e055ed8f1f5ab9",
   "state/outbox/ti_bq25896_query.md": "0cf06881ef22d9aa2bcc374250f89ccc",
   "state/outbox/vendor_round2_email.md": "9a55d233b91cf6c997979d5879039777",
   "state/outbox/vendor_round3_addendum.md": "c367984dbcf4065236ea48b1b1a70a8e",
   "state/outbox/vendor_round4_geo_isp_addendum.md": "dae237af315f12065f057e6578117eda",
   "state/outbox/vendor_via_agent_email.md": "25334d43acf7ea3945a32930b6b2d44f",
   "state/outbox/visionox_display_dsc_mode_query.md": "f126785d5fd8f902b66648767c86759a",
   "state/outbox/visionox_display_inquiry.md": "1e6ebdc4ceff247a2b380491c57c6c0d",
   "state/outbox/attach/01_ARS45_技术确认项_21条.md": "d38566a2a774e23847d6abc9c6f94e75",
   "state/outbox/attach/02_第二轮问询全文.md": "d997d35a04b841db8f948ae4e4c451f3",
   "state/outbox/attach/README.md": "e62b5f1e71fe9f1e208a8c0cfa7a8a4b"
  },
  "scan_dirs": [
   "state",
   "HW",
   "SW",
   "MECH"
  ],
  "excluded": [
   "state/check_pcb_drc.py",
   "HW/check_onepass_release_chain_teeth.py"
  ],
  "min_candidates": 8,
  "decision_taken_here": "not_decided_here",
  "hook_status": "待 main 挂链"
 },
 "candidates": [
  {
   "file": "HW/check_onepass_gate_hook_coverage.py",
   "kind": "doc",
   "note": "★散文/文档/一次性脚本★ (非调用点)"
  },
  {
   "file": "HW/check_onepass_gate_teeth.py",
   "kind": "doc",
   "note": "★散文/文档/一次性脚本★ (非调用点)"
  },
  {
   "file": "HW/check_onepass_preflight_coverage.py",
   "kind": "doc",
   "note": "★散文/文档/一次性脚本★ (非调用点)"
  },
  {
   "file": "HW/check_s8_target_list.py",
   "kind": "doc",
   "note": "★散文/文档/一次性脚本★ (非调用点)"
  },
  {
   "file": "state/.gen_src_v36S_v37R.py",
   "kind": "doc",
   "note": "★散文/文档/一次性脚本★ (非调用点)"
  },
  {
   "file": "state/.gen_src_v39.py",
   "kind": "doc",
   "note": "★散文/文档/一次性脚本★ (非调用点)"
  },
  {
   "file": "state/.gen_src_v42.py",
   "kind": "doc",
   "note": "★散文/文档/一次性脚本★ (非调用点)"
  },
  {
   "file": "state/.gen_src_v43.py",
   "kind": "doc",
   "note": "★散文/文档/一次性脚本★ (非调用点)"
  },
  {
   "file": "state/_add_need_9gates_20261117.py",
   "kind": "doc",
   "note": "★散文/文档/一次性脚本★ (非调用点)"
  },
  {
   "file": "state/_append_decision_page_20261117_0800_r50.py",
   "kind": "doc",
   "note": "★散文/文档/一次性脚本★ (非调用点)"
  },
  {
   "file": "state/_append_decision_page_20261117_2055_r61.py",
   "kind": "doc",
   "note": "★散文/文档/一次性脚本★ (非调用点)"
  },
  {
   "file": "state/_apply_20260723_0600_main_sign_iss348.py",
   "kind": "doc",
   "note": "★散文/文档/一次性脚本★ (非调用点)"
  },
  {
   "file": "state/_apply_20260725_0250_cronfb67af40_sign406_407_408_open409_410_411.py",
   "kind": "doc",
   "note": "★散文/文档/一次性脚本★ (非调用点)"
  },
  {
   "file": "state/_apply_20261117_0815_main_verify277_unlock278_279.py",
   "kind": "doc",
   "note": "★散文/文档/一次性脚本★ (非调用点)"
  },
  {
   "file": "state/_apply_20261117_0850_main_verify279_280.py",
   "kind": "doc",
   "note": "★散文/文档/一次性脚本★ (非调用点)"
  },
  {
   "file": "state/_apply_20261117_1345_cron775d_verify_iss283_open_iss287.py",
   "kind": "doc",
   "note": "★散文/文档/一次性脚本★ (非调用点)"
  },
  {
   "file": "state/_apply_20261117_1350_cronfb67_zombie_iss287_rollback.py",
   "kind": "doc",
   "note": "★散文/文档/一次性脚本★ (非调用点)"
  },
  {
   "file": "state/_apply_20261118_0430_cronfb67_open_iss308.py",
   "kind": "doc",
   "note": "★散文/文档/一次性脚本★ (非调用点)"
  },
  {
   "file": "state/_apply_20261118_1105_cronfb67_land317_open322.py",
   "kind": "doc",
   "note": "★散文/文档/一次性脚本★ (非调用点)"
  },
  {
   "file": "state/_apply_20261118_1426_cronfb67_iss325_cont1_log.py",
   "kind": "doc",
   "note": "★散文/文档/一次性脚本★ (非调用点)"
  },
  {
   "file": "state/_apply_20261118_1700_main_fix_gen_writeback.py",
   "kind": "doc",
   "note": "★散文/文档/一次性脚本★ (非调用点)"
  },
  {
   "file": "state/_apply_20261118_1715_main_writeback_invariant.py",
   "kind": "doc",
   "note": "★散文/文档/一次性脚本★ (非调用点)"
  },
  {
   "file": "state/_apply_20261118_1730_main_land_iss329.py",
   "kind": "doc",
   "note": "★散文/文档/一次性脚本★ (非调用点)"
  },
  {
   "file": "state/_apply_20261119_0230_cronfb67_dispatch_iss337_cont1.py",
   "kind": "doc",
   "note": "★散文/文档/一次性脚本★ (非调用点)"
  },
  {
   "file": "state/_apply_20261122_2125_main_sign_iss337_answer_3needs.py",
   "kind": "doc",
   "note": "★散文/文档/一次性脚本★ (非调用点)"
  },
  {
   "file": "state/_apply_20261122_2150_cronfb67_sign_iss339.py",
   "kind": "unparsed",
   "note": "★**AST 解析失败** (invalid decimal literal @ L11) ⇒ 其中的 check_pcb_drc 提及无法用 AST 分类; ★已人工读源码确认是散文提及 (L30 记 md5)★ ⇒ 按 T4 显式登记为 unparsed (★不装没看见★)"
  },
  {
   "file": "state/_apply_20261122_2155_cronfb67_signoff_logged.py",
   "kind": "doc",
   "note": "★散文/文档/一次性脚本★ (非调用点)"
  },
  {
   "file": "state/_apply_20261125_0120_cronfb67af40_sign402_403_open404_405.py",
   "kind": "doc",
   "note": "★散文/文档/一次性脚本★ (非调用点)"
  },
  {
   "file": "state/_apply_20261125_0200_cronfb67af40_sign404_405_open406_407_408.py",
   "kind": "doc",
   "note": "★散文/文档/一次性脚本★ (非调用点)"
  },
  {
   "file": "state/_apply_iss191_verify_20261111.py",
   "kind": "doc",
   "note": "★散文/文档/一次性脚本★ (非调用点)"
  },
  {
   "file": "state/_iss277_build_preflight.py",
   "kind": "doc",
   "note": "★散文/文档/一次性脚本★ (非调用点)"
  },
  {
   "file": "state/_land_20261103_b.py",
   "kind": "doc",
   "note": "★散文/文档/一次性脚本★ (非调用点)"
  },
  {
   "file": "state/_land_iss162.py",
   "kind": "doc",
   "note": "★散文/文档/一次性脚本★ (非调用点)"
  },
  {
   "file": "state/_land_iss165_progress.py",
   "kind": "doc",
   "note": "★散文/文档/一次性脚本★ (非调用点)"
  },
  {
   "file": "state/_test_gen_writeback_guard.py",
   "kind": "doc",
   "note": "★散文/文档/一次性脚本★ (非调用点)"
  },
  {
   "file": "state/auto_release_if_ready.sh",
   "kind": "loggrep",
   "note": "★含调用点★"
  },
  {
   "file": "state/board_report.sh",
   "kind": "invoke,label",
   "note": "★含调用点★"
  },
  {
   "file": "state/chain_gate.py",
   "kind": "doc,invoke",
   "note": "★含调用点★"
  },
  {
   "file": "state/chain_next_round.sh",
   "kind": "loggrep",
   "note": "★含调用点★"
  },
  {
   "file": "state/chain_tool_stamp.py",
   "kind": "doc",
   "note": "★散文/文档/一次性脚本★ (非调用点)"
  },
  {
   "file": "state/daily_check.py",
   "kind": "doc,invoke",
   "note": "★含调用点★"
  },
  {
   "file": "state/finish_line.sh",
   "kind": "loggrep",
   "note": "★含调用点★"
  },
  {
   "file": "state/gen_kicad_project.py",
   "kind": "comment",
   "note": "★散文/文档/一次性脚本★ (非调用点)"
  },
  {
   "file": "state/gen_pcb_components.py",
   "kind": "doc",
   "note": "★散文/文档/一次性脚本★ (非调用点)"
  },
  {
   "file": "state/gen_pcb_netlist_board.py",
   "kind": "doc",
   "note": "★散文/文档/一次性脚本★ (非调用点)"
  },
  {
   "file": "state/replay_patch_chain.sh",
   "kind": "invoke",
   "note": "★含调用点★"
  },
  {
   "file": "state/run_grid_ladder.sh",
   "kind": "invoke",
   "note": "★含调用点★"
  },
  {
   "file": "state/verify_and_release.sh",
   "kind": "invoke,label",
   "note": "★含调用点★"
  },
  {
   "file": "state/verify_candidate.sh",
   "kind": "invoke",
   "note": "★含调用点★"
  },
  {
   "file": "state/watch_v25.sh",
   "kind": "loggrep",
   "note": "★含调用点★"
  }
 ],
 "call_sites": [
  {
   "id": "CS01",
   "file": "state/auto_release_if_ready.sh",
   "line": 151,
   "kind": "loggrep",
   "strict": false,
   "argv": "grep -E \"DRC violations|unconnected items|C3 DRC|C4 unconnected|check_pcb_nets rc|check_pcb_drc|chain_gate rc|stage_gate rc|缺失|多余\" /tmp/auto_release.log",
   "chain": "放行",
   "use": "display",
   "must_strict": false,
   "consumed_by": [],
   "fallback_gate": "state/verify_and_release.sh",
   "fallback_on_chain": true,
   "log_source": "/tmp/auto_release.log",
   "upstream_script": "state/verify_and_release.sh",
   "upstream_strict": true,
   "note": "自动放行: 盖章与否看 $rc (来自 verify_and_release.sh 严格档) ⇒ 这段 grep 只是展示",
   "evidence": "[实测]"
  },
  {
   "id": "CS02",
   "file": "state/board_report.sh",
   "line": 59,
   "kind": "invoke",
   "strict": false,
   "argv": "bash state/pcbnew_py.sh state/check_pcb_drc.py \"$PCB\" >/tmp/_c2.log 2>",
   "chain": "放行",
   "use": "display",
   "must_strict": true,
   "consumed_by": [
    "state/promote_arm.sh",
    "state/finish_line.sh"
   ],
   "fallback_gate": "",
   "fallback_on_chain": null,
   "log_source": "",
   "upstream_script": "",
   "upstream_strict": null,
   "note": "★**假绿的传播口** ★ 宽松档 ⇒ L60 的 grep 会把「✅ C4 unconnected items = 45」原样抄进板报告; 而 `promote_arm.sh` L67 把这份报告当「臂晋级官方板后的全量取证」",
   "evidence": "[实测]"
  },
  {
   "id": "CS03",
   "file": "state/board_report.sh",
   "line": 59,
   "kind": "label",
   "strict": false,
   "argv": "echo \"  check_pcb_drc   rc=$?\"",
   "chain": "放行",
   "use": "display",
   "must_strict": false,
   "consumed_by": [],
   "fallback_gate": "state/verify_and_release.sh",
   "fallback_on_chain": true,
   "log_source": "",
   "upstream_script": "",
   "upstream_strict": null,
   "note": "★只是把 rc/名字回显出来 (不判绿红)★",
   "evidence": "[实测]"
  },
  {
   "id": "CS04",
   "file": "state/chain_gate.py",
   "line": 296,
   "kind": "invoke",
   "strict": false,
   "argv": "run(state/check_pcb_drc.py)",
   "chain": "投产准入",
   "use": "judgement",
   "must_strict": true,
   "consumed_by": [
    "state/verify_and_release.sh",
    "state/daily_check.py",
    "state/board_report.sh"
   ],
   "fallback_gate": "",
   "fallback_on_chain": null,
   "log_source": "",
   "upstream_script": "",
   "upstream_strict": null,
   "note": "★**命门** ★ L296 argv 无 `--strict` ⇒ ③PCB 环对 unconnected 零敏感; L299 源码注释自写「不阻塞准出」; L309 `lay_txt` 只拼进输出字符串不进 `x3` 判定位",
   "evidence": "[实测]"
  },
  {
   "id": "CS05",
   "file": "state/chain_next_round.sh",
   "line": 61,
   "kind": "loggrep",
   "strict": false,
   "argv": "grep -E \"DRC violations|unconnected items|C3 DRC|C4 unconnected|check_pcb_nets rc|check_pcb_drc|chain_gate rc|stage_gate rc|★缺失|★多余|判定\" /tmp/chain_verify.log",
   "chain": "放行",
   "use": "display",
   "must_strict": false,
   "consumed_by": [],
   "fallback_gate": "state/verify_and_release.sh",
   "fallback_on_chain": true,
   "log_source": "/tmp/chain_verify.log",
   "upstream_script": "state/verify_and_release.sh",
   "upstream_strict": true,
   "note": "下一轮起跑前先自验: 上游严格档 ⇒ 只是展示",
   "evidence": "[实测]"
  },
  {
   "id": "CS06",
   "file": "state/chain_next_round.sh",
   "line": 65,
   "kind": "loggrep",
   "strict": false,
   "argv": "grep -E \"DRC violations|unconnected items|check_pcb_nets rc|check_pcb_drc|chain_gate rc|stage_gate rc|★缺失|★多余\" /tmp/chain_verify.log",
   "chain": "放行",
   "use": "display",
   "must_strict": false,
   "consumed_by": [],
   "fallback_gate": "state/verify_and_release.sh",
   "fallback_on_chain": true,
   "log_source": "/tmp/chain_verify.log",
   "upstream_script": "state/verify_and_release.sh",
   "upstream_strict": true,
   "note": "同上 (追加进 CUR_LOG 的那一份)",
   "evidence": "[实测]"
  },
  {
   "id": "CS07",
   "file": "state/daily_check.py",
   "line": 344,
   "kind": "invoke",
   "strict": false,
   "argv": "run(check_pcb_drc.py)",
   "chain": "巡检",
   "use": "judgement",
   "must_strict": true,
   "consumed_by": [
    "state/alignment_check.py",
    "state/publish_github.sh"
   ],
   "fallback_gate": "",
   "fallback_on_chain": null,
   "log_source": "",
   "upstream_script": "",
   "upstream_strict": null,
   "note": "★**巡检失明** ★ L345 `pcb_ok = (rc_pcb_rc == 0)` ⇒ L404 才拿它判红; 宽松档 ⇒ 这条永远绿 ⇒ 巡检从来没看见过 unconnected=45",
   "evidence": "[实测]"
  },
  {
   "id": "CS08",
   "file": "state/finish_line.sh",
   "line": 102,
   "kind": "loggrep",
   "strict": false,
   "argv": "grep -E \"unconnected items|DRC violations|check_pcb_nets rc|check_pcb_drc|chain_gate rc|stage_gate rc|G1|放行\" /tmp/verify_final.log",
   "chain": "放行",
   "use": "display",
   "must_strict": false,
   "consumed_by": [],
   "fallback_gate": "state/verify_and_release.sh",
   "fallback_on_chain": true,
   "log_source": "/tmp/verify_final.log",
   "upstream_script": "state/verify_and_release.sh",
   "upstream_strict": true,
   "note": "终点线: grep 的是 verify_and_release.sh 的严格档日志 ⇒ 只是展示真值, 不是判据",
   "evidence": "[实测]"
  },
  {
   "id": "CS09",
   "file": "state/replay_patch_chain.sh",
   "line": 240,
   "kind": "invoke",
   "strict": false,
   "argv": "bash state/pcbnew_py.sh state/check_pcb_drc.py \"$WORK/final_chain.kicad_pcb\" 2>",
   "chain": "历史脚本",
   "use": "discarded",
   "must_strict": false,
   "consumed_by": [],
   "fallback_gate": "state/compare_arm_official.py",
   "fallback_on_chain": true,
   "log_source": "",
   "upstream_script": "",
   "upstream_strict": null,
   "note": "臂重放脚本; 宽松档 ⇒ 抄进日志的是「✅ C4 unconnected items = N」(带绿勾); 兜底 = 名单制闸 compare_arm_official.py (臂级 ACCEPT 才许晋级)",
   "evidence": "[实测]"
  },
  {
   "id": "CS10",
   "file": "state/run_grid_ladder.sh",
   "line": 44,
   "kind": "invoke",
   "strict": false,
   "argv": "bash state/pcbnew_py.sh state/check_pcb_drc.py \"$OUT\" 2>",
   "chain": "历史脚本",
   "use": "discarded",
   "must_strict": false,
   "consumed_by": [],
   "fallback_gate": "state/compare_arm_official.py",
   "fallback_on_chain": true,
   "log_source": "",
   "upstream_script": "",
   "upstream_strict": null,
   "note": "网格梯脚本; 同上, 宽松档 ⇒ 只给人眼看「✅ C4」; 兜底 = compare_arm_official.py",
   "evidence": "[实测]"
  },
  {
   "id": "CS11",
   "file": "state/verify_and_release.sh",
   "line": 53,
   "kind": "invoke",
   "strict": true,
   "argv": "python3 state/check_pcb_drc.py --strict",
   "chain": "放行",
   "use": "judgement",
   "must_strict": true,
   "consumed_by": [
    "state/auto_release_if_ready.sh",
    "state/finish_line.sh",
    "state/chain_next_round.sh",
    "state/watch_v25.sh",
    "state/promote_board_file.sh",
    "state/board_progress.py"
   ],
   "fallback_gate": "",
   "fallback_on_chain": null,
   "log_source": "",
   "upstream_script": "",
   "upstream_strict": null,
   "note": "★**全仓唯一带 `--strict` 的真调用点** ★ L53-54 `[ \"$_rc\" -ne 0 ] && FAIL=1` ⇒ 「放行章」这条路今天是有牙齿的; ★缺口在投产链准入闸 + 巡检链, 不在放行章★",
   "evidence": "[实测]"
  },
  {
   "id": "CS12",
   "file": "state/verify_and_release.sh",
   "line": 53,
   "kind": "label",
   "strict": true,
   "argv": "echo \"  check_pcb_drc(--strict) rc=$_rc\"",
   "chain": "放行",
   "use": "display",
   "must_strict": false,
   "consumed_by": [],
   "fallback_gate": "state/verify_and_release.sh",
   "fallback_on_chain": true,
   "log_source": "",
   "upstream_script": "",
   "upstream_strict": null,
   "note": "★只是把 rc/名字回显出来 (不判绿红)★",
   "evidence": "[实测]"
  },
  {
   "id": "CS13",
   "file": "state/verify_candidate.sh",
   "line": 26,
   "kind": "invoke",
   "strict": false,
   "argv": "bash \"$PROJ/state/pcbnew_py.sh\" \"$PROJ/state/check_pcb_drc.py\" \"$CAND\" 2>",
   "chain": "候选验证",
   "use": "discarded",
   "must_strict": true,
   "consumed_by": [
    "state/v74_arms.sh",
    "state/v75_arms.sh",
    "state/v76_arms.sh",
    "state/v77_arms.sh"
   ],
   "fallback_gate": "",
   "fallback_on_chain": null,
   "log_source": "",
   "upstream_script": "",
   "upstream_strict": null,
   "note": "★**rc 被管道吃掉** ★ L26 直接 `| grep -vE | tail -25` ⇒ ① 号尺子的 rc 从没被检查过; 脚本注释 L11 承诺「DRC 必须 0 · unc 必须比官方板低」⇒ 该判据没有机器兑现",
   "evidence": "[实测]"
  },
  {
   "id": "CS14",
   "file": "state/watch_v25.sh",
   "line": 57,
   "kind": "loggrep",
   "strict": false,
   "argv": "grep -E \"unconnected items|DRC violations|check_pcb_nets rc|check_pcb_drc|chain_gate rc|stage_gate rc|单边零铜|Δ>0.13|布不动的脚\" /tmp/verify_v25.log",
   "chain": "放行",
   "use": "display",
   "must_strict": false,
   "consumed_by": [],
   "fallback_gate": "state/verify_and_release.sh",
   "fallback_on_chain": true,
   "log_source": "/tmp/verify_v25.log",
   "upstream_script": "state/verify_and_release.sh",
   "upstream_strict": true,
   "note": "收工监控: 上游严格档 ⇒ 只是展示",
   "evidence": "[实测]"
  }
 ],
 "quoted_markers": [
  {
   "file": "state/_apply_20260725_0250_cronfb67af40_sign406_407_408_open409_410_411.py",
   "line": 120,
   "marker": "图纸可下单",
   "verdict": "quoted",
   "context": "★一次性工单脚本里【引述】ISS-406 的留证输出 (不是对当前板的断言)★"
  },
  {
   "file": "HW/check_onepass_gate_teeth.py",
   "line": 22,
   "marker": "图纸可下单",
   "verdict": "quoted",
   "context": "★ISS-406 闸的模块 docstring 里【引述】宽松档的输出 (不是对当前板的断言)★"
  }
 ],
 "no_order_gates": [
  {
   "id": "NG01",
   "file": "state/stage_gate.py",
   "kind": "绝对闸",
   "on_chain": true,
   "criterion": "读 `HW/PCB/.layout_done.json` ⇒ unconnected==0 且 drc_violations==0 (L220-225); 缺失/读不出 ⇒ 视为未布线 (宁可红)",
   "evidence": "[实测]"
  },
  {
   "id": "NG02",
   "file": "state/verify_and_release.sh",
   "kind": "绝对闸",
   "on_chain": true,
   "criterion": "L53 `python3 state/check_pcb_drc.py --strict` ⇒ rc≠0 ⇒ FAIL=1 ⇒ L90-94 不放行 + 不盖章",
   "evidence": "[实测]"
  },
  {
   "id": "NG03",
   "file": "state/check_pcb_drc.py",
   "kind": "绝对闸",
   "on_chain": true,
   "criterion": "C4 判据 `ok4 = (n_unc == 0) if strict else True` (L135-136) ⇒ ★**只有带 `--strict` 才是绝对闸**★",
   "evidence": "[实测]"
  },
  {
   "id": "NG04",
   "file": "state/chain_gate.py",
   "kind": "相对闸",
   "on_chain": true,
   "criterion": "③PCB 环 = `check_pcb_nets` ∧ `check_pcb_drc`(宽松) ⇒ 只判 C1 焊盘级等价 ⇒ **不判 unconnected**",
   "evidence": "[实测]"
  },
  {
   "id": "NG05",
   "file": "state/promote_arm.sh",
   "kind": "相对闸",
   "on_chain": true,
   "criterion": "晋级闸只校 parity (check_pcb_nets) ⇒ 臂板 unconnected **只打印不判** (L19-29) ⇒ 绝对闸在第 ⑨ 步",
   "evidence": "[实测]"
  },
  {
   "id": "NG06",
   "file": "state/promote_board_file.sh",
   "kind": "相对闸",
   "on_chain": true,
   "criterion": "① compare_arm_official ACCEPT + ② parity ⇒ 绝对闸在第 ⑨ 步 verify_and_release.sh",
   "evidence": "[实测]"
  },
  {
   "id": "NG07",
   "file": "state/compare_arm_official.py",
   "kind": "相对闸",
   "on_chain": true,
   "criterion": "只认「相对官方板变好」(unc 变少 / 零铜变少) ⇒ 不要求绝对 0 ⇒ ★**它拦得住「变坏」, 拦不住「一直差」**★",
   "evidence": "[实测]"
  },
  {
   "id": "NG08",
   "file": "state/gen_production_pack.sh",
   "kind": "无闸",
   "on_chain": true,
   "criterion": "直接 `pcb export gerbers/drill/pos/ipc2581` ⇒ ★**对 unconnected 零判据 ⇒ 板没布完也能出 Gerber**★",
   "evidence": "[实测]"
  },
  {
   "id": "NG09",
   "file": "state/check_pcb_nets.py",
   "kind": "无闸",
   "on_chain": true,
   "criterion": "只校焊盘级等价 (缺失/多余/同号异网) ⇒ 与布线完成无关 ⇒ 今天它红 ≠ 板布完了",
   "evidence": "[实测]"
  }
 ]
}
```
<!-- RELEASE_CHAIN_TEETH_LEDGER_END -->

---

## §7 · 边界自证 (★逐条 · 全部本机实跑★)

| ★**边界** ★ | ★**自证方式** ★ | ★**读数** ★ |
|---|---|---|
| ★**零写板** ★ | `md5sum` + `stat` 三项与开工前逐字相同 | ★**`611b869e13518c3c023fb178f91a0075` / `2026-11-06 07:07:17.362193413` (ns `1793920037362193413`) / `4940213`** ★ |
| ★**零落表** ★ | 网表 / 脚表 / BOM 三件 md5 与开工前逐字相同 | ★**`HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` md5 未动 (见交卷页 B7.1)** ★ |
| ★**零改既有闸判据 / 零改既有脚本** ★ | ★**点名的 8 个文件 (`check_pcb_drc.py` · `chain_gate.py` · `board_report.sh` · `verify_candidate.sh` · `daily_check.py` · `finish_line.sh` · `auto_release_if_ready.sh` · `gate_check.py`) md5 与开工前逐字相同** ★ | ★**见交卷页 B7.1 的逐行 md5 对拍** ★ |
| ★**零挂链** ★ | `grep -c check_onepass_release_chain_teeth state/gate_check.py` | ★**0** ★ |
| ★**零改既有页正文** ★ | 引用到的既有页 md5 对拍 | ★**`BOARD_ONEPASS_GATE_TEETH_AUDIT.md` `a0926de6…` · `BOARD_ONEPASS_PREFLIGHT.md` `192873f6…` · `BOARD_ONEPASS_WORKPACKET.md` `00b0ea5b…` · `BOARD_ONEPASS_COMMIT_ORDER.md` `106ba9e0…` · ISS-406 交卷页 `a4fed6e6…` · `state/issue_log.yaml` `8ea096e1…` —— 全部与开工前逐字相同** ★ |
| ★**零外发** ★ | `state/outbox/` 全树逐文件 md5 未动 | ★**22 件 (含 `attach/` 3 件) 逐件 md5 与基线相同** ★ |
| ★**不代拍** ★ | 机器块 `decision_taken_here` | ★**`not_decided_here`** ★ (★「该不该带 `--strict`」「哪道闸该挂链」「候选验证是绝对 0 还是相对改善」全是 main 的地界★) ★ |
| ★**不自签** ★ | `state/issue_log.yaml` md5 未动 | ★**`8ea096e12f7a1e834c16b4ee943193cf` —— 未动** ★ |
| ★**只写本单允许的文件** ★ | ★**新建 3 个** (本真相页 / 新闸 / 交卷页) · ★**改 1 个** (`state/fragments/hw.yaml` · 走 `state/frag_write.py` · ★**不许 `open(p,"w")`★) · ★**留证** (`logs/iss409/` + `tmp/iss409/`) ★ | ★**见交卷页 B7.2/B7.3** ★ |

### §7.1 · 引用到的既有产出 (★只引用 · 一个字节都没改★)

| 文件 | md5 (开工前 = 交卷后) |
|---|---|
| `HW/PCB/BOARD_ONEPASS_GATE_TEETH_AUDIT.md` (ISS-406 真相页) | `a0926de63a3e50bfb300ba85ddd672d3` |
| `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` | `192873f6c977b376c28785824a82f9f1` |
| `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` | `00b0ea5bae70b7f663b55b9b80014d03` |
| `HW/PCB/BOARD_ONEPASS_COMMIT_ORDER.md` | `106ba9e041123e08bf22bac4a91dd356` |
| `HANDOFF/2026-11-25_hw-lead_ISS406_验收链牙齿清账与闸.md` | `a4fed6e6055eac01047046ae539f0cb2` |
| `state/issue_log.yaml` | `8ea096e12f7a1e834c16b4ee943193cf` |

---

## §8 · ★**留给 main 的问题 (★本单不代拍·一条都没拍★)** ★

| # | 问题 | ★**不答的后果** ★ |
|---|---|---|
| ★**Q1** ★ | ★**`state/chain_gate.py` L296 要不要加 `--strict`?** ★ 加了当天 ③PCB 会红 (unconnected=45) | ★**不加 = 投产链准入闸对「板没布完」零敏感 ⇒ 板改第二次畅通无阻** ★ |
| ★**Q2** ★ | ★**`state/board_report.sh` L59 / `state/daily_check.py` L344 要不要加 `--strict`?** ★ | ★**不加 = 假绿继续进取证报告 + 巡检继续瞎** ★ |
| ★**Q3** ★ | ★**`state/verify_candidate.sh` ① 号尺子: 加 `--strict` (绝对 0) 还是保留「相对官方板变好」的语义?** ★ ★**候选板的 unconnected 常常 > 官方板 ⇒ 简单加 `--strict` 会让候选验证永远红 ⇒ 这是【口径】不是【档位】问题** ★ | ★**不答 = 这道尺子的注释继续承诺一件机器没做的事** ★ |
| ★**Q4** ★ | ★**本闸 `HW/check_onepass_release_chain_teeth.py` 挂不挂链?** ★ (★机制已备好: 把台账 `meta.hook_status` 改成「已挂链」并把本闸加进 `state/gate_check.py` ⇒ 闸脚本一字节都不用改★) | ★**不挂 = 又一个没人跑的闸 (同 ISS-388 病)** ★ |
| ★**Q5** ★ | ★**`state/gen_production_pack.sh` (出投产包) 要不要加一道「unconnected=0 才许出包」的闸?** ★ | ★**不加 = 「出包」与「可下单」在脚本层没有任何机器联系** ★ |
| ★**Q6** ★ | ★**`state/promote_arm.sh` / `state/promote_board_file.sh` (臂→官方板) 要不要把「unconnected=0」加进晋级闸?** ★ | ★**不加 = 臂板只要 C1 等价就能晋级 (绝对闸只落在第 ⑨ 步)** ★ |

---

> ★**本单零写板 · 零落表 (除自有分片) · 零改既有闸判据 · 零改既有脚本 · 零改既有页正文 · 零挂链 · 零外发 · 不代拍 · 不自签** ★
> ★**真相页** = `HW/PCB/BOARD_ONEPASS_RELEASE_CHAIN_TEETH_AUDIT.md` · ★**新闸** = `HW/check_onepass_release_chain_teeth.py` · ★**留证** = `logs/iss409/` + `tmp/iss409/` ★

---

## §9 · ★**cont1 续做补记 (2026-11-25 03:12~03:2x · 追加式 · 不推倒重写)★** ★

★**本节是【追加】, 前面 §0~§8 正文一个字都没改★**
★**上一趟 (cont1 前身) 在写交卷页之前被【共因中断】掐死 (★main 本机实读 `~/.openclaw/subagents/runs.json` + 三条 transcript 末条: 三条会话在起后 ~11 分钟、同一 1.2 秒窗口 03:03:28.846~03:03:29.972 一起死, `runTimeoutSeconds`=5400 没到 ⇒ 不是超时★) ⇒ 本趟 = 从已在盘的东西接着做, 已在盘读数直接用, 不重跑★ ★**

### ★9.1 · ★**追加前后的两件交付物指纹 (★补之前记下它现在的字节数 + md5, 补之后记补后的 — 两组数字都写进交卷页★)★**

| 交付物 | ★**追加前** ★ | ★**追加后 (本节写完后)** ★ | 性质 |
|---|---|---|---|
| ★**真相页 `HW/PCB/BOARD_ONEPASS_RELEASE_CHAIN_TEETH_AUDIT.md`** ★ | ★**size `58163` B · md5 `4f51dfc69dd845051844c1f75661588e`** ★ (★mtime 2026-11-25 02:58:55★) | ★**见 `logs/iss409/truthpage_gate_fingerprint_AFTER.txt` (原始输出) + 交卷页 B7.1 (两组数字都写在那里)** ★ —— ★**本行不能硬编自己的 size/md5: 写进去就变, 变了就不再是那个值 ⇒ 以原始输出文件 + 交卷页为准★** ★ | ★**只追加 §9 一节; §0~§8 正文零改动** ★ |
| ★**新闸 `HW/check_onepass_release_chain_teeth.py`** ★ | ★**size `58081` B · md5 `800b85fa5cad1ccda7e9465b42e7fd47`** ★ (★mtime 2026-11-25 02:57:23★) | ★**size `58081` B · md5 `800b85fa5cad1ccda7e9465b42e7fd47`** ★ | ★**零改动 (本趟不需要改闸脚本)** ★ |

★**追加前指纹的原始输出留证**: `logs/iss409/truthpage_gate_fingerprint_BEFORE.txt` ★
★**追加后指纹的原始输出留证**: `logs/iss409/truthpage_gate_fingerprint_AFTER.txt` ★

### ★9.2 · ★**本趟 (cont1) 复跑留证 · 逐条 rc (★全部本机实跑, 输出原文见交卷页 B6★)★**

| 命令 | ★**读数** ★ | 留证 |
|---|---|---|
| `python3 HW/check_onepass_release_chain_teeth.py --selftest` | ★**rc=0 · 末行逐字 `ALL TESTS PASS` · 正向 1 + 反向 20 = 21 条全抓到** ★ | `logs/iss409/selftest_20261125_031305.log` |
| `python3 HW/check_onepass_release_chain_teeth.py` (裸跑) | ★**rc=1** ★ (★红的是现状: T2 4 处放行链跑宽松档 + T3c 2 个 judgement 点跑宽松档★) | `logs/iss409/bare_run_20261125_031310.log` |
| `python3 state/merge.py` | ★**rc=0 · 产出 927 · 阻塞 43 (高危 33) · 未闭合需求 467 · 冲突 0** ★ | `logs/iss409/merge_20261125_031316.log` |
| `python3 state/gate_check.py` | ★**rc=0 · Q1 交付齐备率 18/18 · Q2 3/3 · Q7 钉板 md5 闸 10/10 绿** ★ | `logs/iss409/gate_check_20261125_031331.log` |
| `python3 state/stage_gate.py` | ★**rc=0 · 当前 G1 · 还差 1 项 = PCB 布线 unconnected 45→0 (★没擦它★)** ★ | 见交卷页 B6 逐字 |
| `python3 state/check_brief_commands.py --brief-file state/dispatch_briefs/ISS-409_hw_release_chain_teeth_audit.md` | ★**rc=0** ★ | 见交卷页 B6 |

★**★本趟【没有】重跑两档 DRC (★`check_pcb_drc.py` 宽松档/严格档的读数直接用已在盘的 `logs/iss409/check_pcb_drc_lenient.log` · `check_pcb_drc_strict.log` · `check_pcb_nets.log`★ — ★上一趟已实跑并留证, 重跑要几分钟到几十分钟, 而本趟随时可能被共因掐死 ⇒ 按 cont1 头「已在盘的读数直接用, 不要重跑」执行★)★ ★**

### ★9.3 · ★**本趟的边界自证 (★全部本机实跑·不是「应该没碰」★)★**

| ★边界★ | ★**读数 (本机实跑)** ★ |
|---|---|
| ★**零写板** ★ | 板 md5 `611b869e13518c3c023fb178f91a0075` · size `4940213` · mtime `2026-11-06 07:07:17.362193413` (ns `1793920037362193413`) ★**19 天逐字节未动** ★ |
| ★**零落表** ★ | 网表 `6aee500e60ba0732f83a9cf557ba90ab` · 脚表 `9174309df1ec9411ac8e8d9e80ee386a` · BOM `5b9993992405904a60ac96a020b375d8` ★**三件逐字未动** ★ |
| ★**零改既有闸判据 / 零改既有脚本** ★ | ★**点名的 8 个文件 md5 逐字未动** (见交卷页 B7.1 的逐行对拍) ★ |
| ★**零挂链** ★ | `grep -c check_onepass_release_chain_teeth state/gate_check.py` = **0** ★ (★由新闸 T5 每次跑时自证★) ★ |
| ★**零改既有页正文** ★ | §7.1 列的 6 个既有产出 md5 逐字未动 ★ |
| ★**零外发** ★ | `state/outbox/` **22 件** 逐件 md5 与基线相同 (`tmp/iss409/outbox_baseline.md5` vs `tmp/iss409/outbox_now.md5` ⇒ `diff` 空) ★ |
| ★**不代拍** ★ | 机器块 `meta.decision_taken_here` = **`not_decided_here`** ★ (★未改★) ★ |
| ★**不自签** ★ | `state/issue_log.yaml` md5 `8ea096e12f7a1e834c16b4ee943193cf` ★**未动** ★ |
| ★**只写本单允许的文件** ★ | ★**新建**: 交卷页 `HANDOFF/2026-11-25_hw-lead_ISS409_放行链牙齿清账与闸.md` · ★**追加**: 本真相页 §9 (本节) · ★**留证**: `logs/iss409/` + `tmp/iss409/` ★ (★真相页/新闸/分片是上一趟已在盘的, 本趟没推倒重写★) ★ |

### ★9.4 · ★**一处留痕 (★诚实起见: 台账里有一个字段是【写死的预填值】, 不是实跑时刻★)★**

★**§6.2 机器块 `meta.generated_at` 写的是 `2026-11-25T03:40:00+08:00` —— 那是生成台账脚本里的预填常量 (★`tmp/iss409/build_ledger.py` L154 写死★), 台账实际落盘时刻是 **2026-11-25 02:58:55** (★真相页 mtime 实测★)★**
★⇒ ★**该字段【不参与】新闸任何一条判据 (★`HW/check_onepass_release_chain_teeth.py` 全文实读: `generated_at` 只在沙盒自检路径 L1009 出现, 主路径【不读】它★) ⇒ 不影响任何结论★ ★**
★⇒ ★**本单【不改】它 (★改它就是改机器块正文, 违反「只许追加式补」纪律★) ⇒ 在此留痕, 交 main 知悉★ ★**

---

> ★**本单零写板 · 零落表 (除自有分片) · 零改既有闸判据 · 零改既有脚本 · 零改既有页正文 · 零挂链 · 零外发 · 不代拍 · 不自签** ★
> ★**真相页** = `HW/PCB/BOARD_ONEPASS_RELEASE_CHAIN_TEETH_AUDIT.md` (§0~§9) · ★**新闸** = `HW/check_onepass_release_chain_teeth.py` · ★**留证** = `logs/iss409/` + `tmp/iss409/` ★
