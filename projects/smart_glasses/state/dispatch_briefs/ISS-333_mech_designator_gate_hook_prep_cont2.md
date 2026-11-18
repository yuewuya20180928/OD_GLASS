【ISS-333 · mech-lead · ★★cont2 续做单 · ★★只补【交卷两件套】★★】

★**派活人**: 项目总工 (main / cron fb67af40 · 2026-11-18 21:2x)
★**任务书全文 (上一趟那份 · 仍然有效)**: `state/dispatch_briefs/ISS-333_mech_designator_gate_hook_prep.md` (10,496 B)
★**上一趟 cont1 任务书**: `state/dispatch_briefs/ISS-333_mech_designator_gate_hook_prep_cont1.md` (15,640 B)
★**本单 = 只补最后两件 (★交卷页 + 分片·★其余全在盘·★不要重做★)**

---

## ★★★【① 为什么派这一条 (★21:1x 本机实跑读数·不抄任何 agent 报告★)★★★】

| ★项★ | ★21:1x 本机实跑★ | ★判★ |
|---|---|---|
| ★cont1 会话★ | ★`~/.openclaw/agents/mech-lead/sessions/1ea24d8e-….jsonl` ★**最后一条 = `openclaw:prompt-error` · "This operation was aborted" @ 21:00:45** ★ | ★**会话被掐·活儿没干完** ★ |
| ★在盘 ①★ | ★**`MECH/tools/check_mech_ref_reachability.py` (56,550 B · 19:36:31)** ★ ⇒ main 20:4x 实跑 `--selftest` ⇒ **rc=0 · 反向用例 14/14 (MC-1~MC-14) 通过** ★ | ★**在盘·绿** ★ |
| ★在盘 ②★ | ★**`logs/iss333/` 11 件**: `baseline_repro.json` / `baseline_repro_raw.txt` / `freeze_guard.txt` / `freeze_registry_output.txt` / `gate_dump_classification.txt` / `gate_main_run.txt` / `repro_baseline.py` / `repro_iss326_caliber.py` (★19:3x 那批★) + ★**`gate_run_posthook.txt` (20:49:31) / `gate_check_json_extra_gates.txt` (20:51:00) / `gate_check_posthook.txt` (20:51:05)** (★你 cont1 补的三件 posthook·★不许覆盖那 8 件原始证据★)** ★ | ★**在盘·证据够用** ★ |
| ★★缺 ①★★ | ★**★`HANDOFF/2026-11-18_mech-lead_ISS333_MECH侧位号可达性闸实现.md` 【不存在】★** ★ | ★**缺** ★ |
| ★★缺 ②★★ | ★**★`grep -c "iss333" state/fragments/mech.yaml` = 0** (★分片一字没写·★必须走 `python3 state/frag_write.py --agent mech-lead`★) ★ | ★**缺** ★ |

★**★★最要紧的一条 (★main 20:2x 已把这道闸挂进链上了·★所以你这一趟【不许再改那道闸】★★)**:
★**`state/gate_check.py` 的 `EXTRA_GATES` 里已经有「MECH 侧位号引用可达性闸 (ISS-326 设计稿 / ISS-333 实现)」这一行 (★owner=main 的 ISS-330 落的·★挂完五门 rc 全绿★)** ⇒ ★**⇒ 闸脚本一个字节都不许改** (★改了链上那道闸就与盘面不一致 ⇒ 全项目门禁失真★) ⇒ ★**有 bug 就写进 B5 交 main 拍, 不许自己修** ★

---

## ★★★【② ★★这一趟只干两件 (★上一趟就是死在【多余探查】上·★21:00 前它还在 dump J_CHG_SELECTION 分类★)★★】★★★

### ★★★【第 ① 件: 交卷页 (★新建★·★B0~B6 齐全·★不许留占位符★)】★★★】
★**★新建★ `HANDOFF/2026-11-18_mech-lead_ISS333_MECH侧位号可达性闸实现.md`**
★**★它必须回答的问题 (★逐条·★读数全部从 `logs/iss333/` 里引·★不要重新跑一遍★)**:

| ★节★ | ★必须写什么★ | ★读数从哪来★ |
|---|---|---|
| ★B1 结论摘要★ | ★**这道闸做了什么 (★扫描面 = `MECH/**/*.py` + `MECH/**/*.md` 递归·113 份/48 md + 65 py/唯一 token 230★) · 基线数 = 16 (★MECH 侧自己的·★**不许抄 SW 侧的 3**★) · 自测 14/14 通过** ★ | ★`logs/iss333/baseline_repro.json` · `logs/iss333/gate_main_run.txt`★ |
| ★B2 验收标准自评★ | ★**ISS-333 §② 那 5 条硬要求逐条「通过 / 不通过 / 未验」** (★fail-closed 三条 / 基线 fresh 测出 16 / 反向用例 ≥5 / 扫描面递归 / 基线只许收紧不许放宽★) ★ | ★你自己对着 §② 逐条打勾★ |
| ★B3 证据分级★ | ★**每条读数带 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` 标签** ★ | ★ |
| ★B4 接口取值声明★ | ★**闸的调用形态 + 参数 + 退出码语义 (★rc=0 绿 / rc≠0 红·★fail-closed 三条具体是哪三条★)** ★ | ★`MECH/tools/check_mech_ref_reachability.py` 的 `--selftest` 入口与 `--help`★ |
| ★B5 未决项与卡点★ | ★**★必须写「基线 16 是建闸日值·今天实测若 ≠ 16 ⇒ 建议收不收·给建议 + 理由」★** · ★**另: 闸挂在 `EXTRA_GATES` 第几位 (★自己实读 `state/gate_check.py`·不许猜·给行号★)· 「挂了会不会把现在的门禁链带红」的分析 (★main 20:2x 实挂后 rc 全绿·但你仍要给独立判断★)** ★ | ★`logs/iss333/gate_check_posthook.txt` · `logs/iss333/gate_check_json_extra_gates.txt`★ |
| ★B6 自证复现命令★ | ★**原样贴输出 (★§⑤ 那 9 条全跑一遍·★输出贴进来★)** ★ | ★ |

★**★B4/B5 的挂闸写法三小问 (★任务书 §③ 第 ③ 件·★你只出写法不执行★)**:
★**① 挂哪**: ★**实读 `state/gate_check.py` 的 `EXTRA_GATES` 结构 ⇒ 给出「挂第几位 / 用什么调用形态 / 参数怎么传」的逐字写法 + 行号** ★
★**② 挂完自检**: ★**给出 main 挂完之后应当看到的期望输出 (★Q1 18/18 · Q2 3/3 · Q6 ✅ · Q7 9/9 + 新闸那一行 rc★)** ★
★**③ 挂不挂的风险**: ★**给明确建议 + 理由 (★不许含糊★)** ★

### ★★★【第 ② 件: 分片 (★必须走 frag_write.py★)】★★★】
```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 state/frag_write.py --agent mech-lead --show      # ★先看自己现有分片长什么样★
python3 state/frag_write.py --agent mech-lead --add-artifact 'path=MECH/tools/check_mech_ref_reachability.py summary="MECH 侧位号引用可达性闸 (★自测 14/14·基线 16·扫描面 MECH/**/*.py + MECH/**/*.md★)" kind=script' --add-artifact 'path=HANDOFF/2026-11-18_mech-lead_ISS333_MECH侧位号可达性闸实现.md summary="ISS-333 交卷页 B0~B6"' --status 'phase=done progress_pct=100 health=green summary="ISS-333 MECH 侧位号可达性闸已实现并挂链 (★挂闸由 main 执行·ISS-330★)"'
```
★**★写完必须复核**: ★`grep -c "iss333" state/fragments/mech.yaml` 必须 ≥ 1 ★
★**★禁止 `open(p,"w")`** ★

---

## ★★★【③ 边界 (★违反就是不合格★)★★★】★★
- ★**零写板**: ★**`HW/PCB/demo_mainboard.kicad_pcb` md5 必须还是 `611b869e13518c3c023fb178f91a0075` · mtime 必须还是 `2026-11-06 07:07:17.362193413`** (★main 21:1x 实测过·★变了一律不合格★) ★
- ★**零落表** (★网表/脚表/BOM/原理图真源一个字节不许动★)
- ★★★**零改 `MECH/tools/check_mech_ref_reachability.py`** (★★它已经在链上·★改了就与盘面不一致★) ★★★ · ★**零改 `state/gate_check.py`** (★挂闸是 main 的机制地界★) · ★**零改 `state/check_*.py`** · ★**零改 `SW/tools/check_sw_ref_reachability.py`** (★只读 import★) · ★**零改既有 `MECH/**/*.md` 正文** · ★**零改既有 `MECH/**/*.py`** · ★**零改 `logs/iss326/`** (★已落的交卷证据·只读★)
- ★**沙盒只写 `tmp/iss333/` + `logs/iss333/`** · ★**只写 `state/fragments/mech.yaml`** · ★**零外发** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信 ⇒ **没有「批一句可以发」这个选项**★) · ★**不替老板拍板** · ★**不自签 `state/issue_log.yaml`** ★
- ★**沙盒里凡要【写】的文件 ⇒ 一律真拷贝; 写前 `assert not os.path.islink(path)`** ★
- ★★**文档纪律 (★这一条最容易踩·★照做★)**: ★**`MECH/**/*.md` 现在是这道闸的扫描面** ⇒ ★**你在 MECH 域任何一个 .md 里写死一个盘上没有的位号 ⇒ 闸当场判新增真隐患 ⇒ rc=1 ⇒ 全项目门禁变红** ⇒ ★**⇒ 交卷页必须放 `HANDOFF/` (★不在扫描面里★) · MECH 域文档一律写 `logs/iss333/`** ★
- ★★★**抗上下文护栏 (★上一趟 21:00:45 被掐·★这一趟活少·★别再展开★)★★★**: ★**不要做新的探查 / 不要 dump 新的分类 / 不要重跑已在盘的复现** ⇒ ★**读数全部从 `logs/iss333/` 引** ★ · ★**一次 write ≤ 3000 字 ⇒ 先 write 骨架 (B0~B6 标题 + 每节 1~2 行), 再 edit 逐块补** ★ · ★**回复控制在 ~500 字以内** ★

---

## ★★★【④ 交卷前必跑 (★原样输出贴进交卷页 B6·★期望值写在后面★)★★★】★★】
```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 MECH/tools/check_mech_ref_reachability.py --selftest   # ★rc 必须 0 · 14/14
python3 state/merge.py   # rc 必须 0
python3 state/gate_check.py   # rc 必须 0 (★本单不挂闸 ⇒ 门禁链与今天一样·**不许自己去改它**★)
python3 state/issue_check.py   # rc 必须 0
md5sum HW/PCB/demo_mainboard.kicad_pcb   # 必须 611b869e13518c3c023fb178f91a0075
stat -c '%y' HW/PCB/demo_mainboard.kicad_pcb   # 必须 2026-11-06 07:07:17.362193413
grep -cE "🔄|待填|PLACEHOLDER|施工中|__[A-Z_]+__" "HANDOFF/2026-11-18_mech-lead_ISS333_MECH侧位号可达性闸实现.md"   # 必须 0
grep -c "iss333" state/fragments/mech.yaml   # 必须 >= 1
find tmp/iss333 -type l | wc -l   # 必须 0
```
★**★补一条 main 20:4x 踩到并记进 cont1 的坑 (★自己核实时别找错地方★)**:
★**`extra_gates` 这一段【只出现在 `--json` 模式里】⇒ 默认 stdout (62 行那种) 【根本不打印 extra_gates】⇒ 你要是只 grep 默认输出, 会以为「链上没这道闸」⇒ ★**那是找错地方, 不是闸没挂上** ★ ⇒ ★**要看链上那道闸 ⇒ 跑 `python3 state/gate_check.py --json` ★**

★额外纪律: ★**证据分级 [官网]/[实测]/[媒体]/[推算]/[0数据] 必须标** ★ · ★**不许外发任何邮件/询价/问询/采购 ⇒ 缺口一律自己网上查 + 标证据等级 + 写降级方案** ★ · ★**交卷前跑 merge.py (rc=0) && gate_check.py (rc=0) 并把输出贴进回复** ★

---

★派活标记=CONT-20261118-2120★
★**本单 status 仍是 fixing ⇒ 无 open 窗口 ⇒ 兄弟 job 775d9893 不会重复派** ★
★**★本单不是从零: 闸脚本 + 11 件证据 + 挂闸后 rc 三件全在盘·★这一趟只补【交卷页 + 分片】★**
