# ★★[cont1 续派 · ISS-409] hw-lead · 硬件总工

【项目总工派活 · 队列自动推进 · 闭环 ISS-409 (cont1)】你是 硬件总工。
★★【★★★ cont1 · 断点续做 · 上一趟被【共因掐死】★★★】★★
★**死因 (main 本机实读 `~/.openclaw/subagents/runs.json` + 三个 transcript 末条, 不抄任何 agent 报告)**:
  · 上一趟的 `runTimeoutSeconds` = **5400 (90 分钟)**, **没到** ⇒ **不是你超时**
  · 三条会话 (ISS-409 / ISS-410 / ISS-411) 在起后 ~11 分钟、且在【**同一 1.2 秒窗口 03:03:28.846~03:03:29.972**】一起死
    ⇒ **共因中断** (与 2026-11-23 21:51:49、2026-11-25 02:07:37~02:07:40 同型)
  · ⇒ **本趟 = 从【已在盘的东西】接着做, 不是从零做 ⇒ 已在盘的读数直接用, 不要重跑** (★重跑一遍要几分钟到几十分钟, 而你可能又被掐★)
★★**三条硬纪律 (★因为【你随时可能被掐】★★)**:
  ① ★**先落盘, 后汇报**★ —— 每完成一件交付物**立刻**写盘 (★别攒到最后一起写★)
  ② ★**交卷页 + 自有分片 优先**★ —— 这两个是 main 签收的凭据 ⇒ **先把它们写完**, 其余往后排
  ③ ★**如果你感觉时间紧 ⇒ 交卷页 + 分片 + 一份短报告交上来, 剩下的写进交卷页的「未完成」段**★ ⇒ ★**不许交半份然后什么都不留★**
★★**不许做的事 (★与原 brief 一致, 本头不放松★)**:
  ★**零写板 · 零落表 (除自有分片) · 零改既有闸判据 · 零改既有脚本 · 零改既有页正文 · 零挂链 · 零外发 · 不代拍 · 不自签 `state/issue_log.yaml` ★**
★★**已在盘的真相页/新闸 ⇒ 【不许推倒重写】, 只许【追加式】补 (★补之前先记下它现在的字节数 + md5, 补之后记补后的, 两组数字都写进交卷页★)** ★

★★【已在盘 (★main 本机实测, 直接用, 不要重做★)】★★
| 交付物 | 状态 |
|---|---|
| ★**① 真相页 `HW/PCB/BOARD_ONEPASS_RELEASE_CHAIN_TEETH_AUDIT.md`** ★ | ★**已在盘 · 58,163 B @ 02:58:55** ★ |
| ★**② 新闸 `HW/check_onepass_release_chain_teeth.py`** ★ | ★**已在盘 · 58,081 B @ 02:57:23** ★ · ★**main 本机实测裸跑 rc=1 (★红的是现状, 不是闸故障★)** ★ |
| ★**③ `state/fragments/hw.yaml` 收口** ★ | ★**已在盘 (★mtime 02:59:51 · 命中 ISS-409 17 处★)** ★ |
★★【本趟【还缺】的 (★这才是你的活★)】★★
| # | 待补 | 说明 |
|---|---|---|
| ★**④ 交卷页** ★ | ★**新建 `HANDOFF/2026-11-25_hw-lead_ISS409_放行链牙齿清账与闸.md`** ★ | ★**main 实测: 不在盘 ⇒ 上一趟被掐在写交卷页之前★** · ★**B1~B7 全填 (★`state/gate_check.py` Q1 六块齐全★) ★** |
| ★**⑤ `--selftest` 实跑留证 + merge / gate_check 终跑 + 边界自证表** ★ | ★**上一趟的最后一条工具调用是在跑 `state/gate_check.py` 时被掐的 ⇒ merge 已 rc=0 (★产出 927★) 但 gate_check 的终跑输出【没进交卷页】★★ ⇒ ★**必跑一次并把输出逐字贴进交卷页★** ★ |
| ★**⑥ 交卷报告 (回复正文)** ★ | ★**按 main 的验收口径写: 读数 / 交付物 / rc 逐条 / 边界自证 / 留给 main 的问句 (★一条都不代拍★) ★** |
★★**两条特别提醒**★★
  · ★**真相页/新闸已经 58 KB 级, 是上一趟的成果 ⇒ 本趟只许追加式补 (★不许推倒重写★) ★**
  · ★**板 `611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17.362193413` / size `4940213` —— 19 天逐字节未动 ⇒ 本趟必须仍是这三项逐字相同★** ★

---以下是原 brief 全文 (★题面 / 交付口径 / 边界 / 自检命令 一律以它为准★)---

# ★ISS-409 · hw-lead · 板那一趟【投产/放行链有没有牙齿】—— `check_pcb_drc.py` 在放行路径上的调用档位全仓清账 + 「未布线 ⇒ 不可下单」机器闸 ★

★**单号**: ISS-409 · ★**派活**: 项目总工 (main / moli) · ★**执笔**: hw-lead (硬件总工) · ★**日期**: 2026-11-25
★**性质**: ★**纯查证 + 纯分析 + 新建真相页 + 新建机器闸 + 自有分片收口** ★ ⇒ ★**零写板 · 零落表 · 零改既有闸判据 · 零改既有脚本 · 零改既有页正文 · 零挂链 · 零外发 · 不代拍 · 不自签 `state/issue_log.yaml`** ★
★**主线关系**: ★老板 2026-11-17 00:43「接下来的目标是绘制 PCB 图」⇒ 本单属 ★**「板只改一次」纪律 ① (先派纯分析/作业包类, 不动板)** ★

---

## ★0 · 一句话题面 ★

★★**ISS-406 已经查清「门禁链那 18 道闸被调用时用的是哪一档」; 但生产链上真正决定「这张板能不能下单」的那几道闸 —— `state/chain_gate.py` (投产链准入闸) · `state/board_report.sh` · `state/verify_candidate.sh` · `state/daily_check.py` —— 全仓实测【只有 `state/verify_and_release.sh` 一处带 `--strict`】⇒ 「板那一趟」当天, 投产链准入闸的 PCB 环对「unconnected = 45」【零敏感】⇒ 板没布完, 投产链这一环照样判绿 ⇒ Gerber 可以下单 ⇒ 板改第二次 ★★**

---

## ★★一 · 题面 (★main 2026-11-25 02:4x~02:5x 本机实读 + 本机实算, 不抄任何 agent 报告★) ★★

### ★1.1 · 本机实测事实 (★全部可复现★) ★

| # | 事实 | 实测读数 | 出处 (★本机实读★) |
|---|---|---|---|
| ① | ★**命门闸的宽松档是恒真判据** ★ | `state/check_pcb_drc.py` L134-L139 逐字: `strict = "--strict" in sys.argv` · `ok4 = (n_unc == 0) if strict else True` ⇒ ★**不带 `--strict` ⇒ C4 unconnected 恒判绿** ★ | ★**本机实读源码★** |
| ② | ★★**投产链准入闸 `state/chain_gate.py` 的 PCB 环跑的是宽松档** ★★ | ★**L296 逐字**: `rc2, _ = run([sys.executable, "state/check_pcb_drc.py"])` ⇒ ★**argv 里没有 `--strict`** ★ ⇒ ③PCB 环的 DRC 判定 **对 unconnected 零敏感** ★ | ★**本机实读源码★** (★本机 `sed -n '280,320p' state/chain_gate.py` 实跑★) |
| ③ | ★**「布线未完成」在投产链里只"报出来"、不参与判定** ★ | ★**L301-L310 逐字**: 源码注释 `★布线是否完成 (不阻塞"准出", 但要报出来 —— 现在 Gerber 不能下单)★` ⇒ `lay_txt` 只拼进输出字符串, **不进 `x3` / 不进任何 `stage(...)` 的判定位** ★ | ★**本机实读源码★** |
| ④ | ★★**投产链 ③PCB 今天之所以红, 靠的是另一道闸, 不是 DRC** ★★ | `state/chain_gate.py` ③PCB 环 = `check_pcb_nets rc` (C1 焊盘级等价) **AND** `check_pcb_drc rc` ⇒ ★**`check_pcb_nets` 今天 rc=1 (C1: 缺失 0 / 多余 2 / 同号异网 3) ⇒ ③PCB 红; 而 `check_pcb_drc` 宽松档 rc=0 ⇒ ★**「未布线」这一项今天完全没参与 ③PCB 的判定★** ★ | ★**本机实跑 `bash state/pcbnew_py.sh state/check_pcb_nets.py` (rc=1) + `bash state/pcbnew_py.sh state/check_pcb_drc.py` (rc=0, 宽松档)★** |
| ⑤ | ★★**⇒ 由此得到本单最硬的一句推论 (★这就是"板改第二次"的机器级根因★)★★** | ★**「板那一趟」做完板侧同步 (C1 多余焊盘/同号异网清零) ⇒ `check_pcb_nets` 必然转绿 ⇒ 此时 ③PCB 的两个因子变成 (绿 · 绿) ⇒ ★**哪怕 unconnected 仍是 45, 投产链准入闸的 PCB 环照样判绿 ⇒ Gerber 可下单** ★★ ⇒ ★**「板改第二次」在今天这套闸上是【畅通无阻】的★** | ★**由 ②③④ 三条逐字源码 + 实跑读数推出 (★逻辑推论, 但每一步都可复现★)** ★ |
| ⑥ | ★**全仓清账: 谁在跑 `check_pcb_drc.py`, 谁带了 `--strict`** ★ | ★**本机 `grep -rl check_pcb_drc.py` 逐文件扫 + 逐文件逐行数 `--strict` 命中★** ⇒ ★**可执行脚本里【只有 `state/verify_and_release.sh` 命中 `--strict`】**; ★**下列全部是宽松档**: `state/chain_gate.py` · `state/board_report.sh` L59 · `state/verify_candidate.sh` L26 · `state/daily_check.py` · `state/replay_patch_chain.sh` · `state/chain_tool_stamp.py` · `state/gen_pcb_netlist_board.py` · `state/gen_pcb_components.py` ★ | ★**本机实跑 (★脚本全文扫, 不是抽样★)** ★ |
| ⑦ | ★**两道放行脚本只 grep 日志文本、自己不跑 DRC** ★ | `state/finish_line.sh` L102 · `state/auto_release_if_ready.sh` L151 逐字 = `grep -E "unconnected items\|DRC violations\|check_pcb_nets rc\|check_pcb_drc\|chain_gate rc\|stage_gate rc\|G1\|放行" /tmp/verify_final.log \| head -14` ⇒ ★**它们采信的是上游宽松档跑出来的日志文本 ⇒ 宽松档的假绿会一路被抄到「放行」结论里★** | ★**本机实读源码★** |
| ⑧ | ★**宽松档的输出长什么样 (★假绿的样子, 必须原样留证★)** | ★**宽松档实测打印「✅ C4 unconnected items = 45」+「✅ 全过 —— 图纸可下单」且 rc=0** (★ISS-406 已留证 `logs/iss406/check_pcb_drc_lenient.log`·★你复跑一次并存自己的留证★) | ★**本机实跑 + ISS-406 留证 (★独立复核一致★)** ★ |
| ⑨ | ★**板 md5 自 2026-11-06 起未动, 19 天** ★ | `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · size `4940213` | ★**本机 `md5sum` + `stat`★** |
| ⑩ | ★**G1 仍开, 不许投板 (★所以这一趟现在是"唯一一次机会"★)** | ★**`state/stage_gate.py` 当前 G1 · 还差 1 项 = PCB 布线 unconnected 45→0 (DRC 违规 0 已达标)** ★ | ★**本机实跑 `python3 state/stage_gate.py`★** |

### ★1.2 · ★为什么 ISS-406 不覆盖这一格 (★不重复它, 也不推翻它★) ★

★**ISS-406 查的是「门禁链 `state/gate_check.py` 上那 18 道闸被调用时用的是哪一档」—— 本单查的是「【投产/放行/巡检/候选验证/生成器写盘守卫】这条链上, 谁在跑 `check_pcb_drc.py`、用的是哪一档」—— 两者的【被查对象】不同 (门禁链 18 道闸 vs 放行链 8 个脚本) ⇒ ★**不是重做, 是补另一条链★** ★
★**并且: ISS-406 自己在交卷页里明写「没有改 `state/check_pcb_drc.py` 的判据 (★`--strict` 开关一直在·问题是没人用它★)」—— ★**「没人用它」这句话在放行链上是【字面事实】**: 全仓只有一处用了★** ★

### ★1.3 · ★坏结局 (★为什么值钱★) ★

★**「板只改一次」= 板 md5 全生命周期只许变 1 次** ⇒ ★**投板前的每一道检查, 都是「板改第二次」的最后一道闸** ★
⇒ 坏结局三选一:
① ★**宽松档假绿**: 那一趟当天, 板侧同步做完 ⇒ C1 绿 ⇒ ③PCB 环 (绿·绿) 判绿 ⇒ ★**unconnected=45 的板过了投产链准入 ⇒ Gerber 下单 ⇒ 板改第二次 (2-4 周 + 一批板的钱 + 一轮全部留证链作废)★** ★
② ★**日志抄写**: `finish_line.sh` / `auto_release_if_ready.sh` 抄的是宽松档日志里的「✅ 全过 —— 图纸可下单」 ⇒ ★**假绿被二次放大成"放行依据"★** ★
③ ★**巡检失明**: `state/daily_check.py` 也是宽松档 ⇒ ★**巡检从来没看见过 unconnected=45 ⇒ 这一格今天处于"没人看"的状态 (★这解释了为什么 daily 巡检那两条红是 check_pcb_nets / chain_gate, 而不是 unconnected★)** ★

---

## ★★二 · 本单交付 (★5 件 · 全部零写板·零改既有文件★) ★★

| # | 交付物 | 路径 | 验收口径 |
|---|---|---|---|
| ① | 真相页 | ★**新建** `HW/PCB/BOARD_ONEPASS_RELEASE_CHAIN_TEETH_AUDIT.md` ★ | §0~§7 + 机器块; ★**三张表**: (a) ★**全仓 `check_pcb_drc.py` 调用点全集 × 逐个的 argv × 是否带 `--strict` × 该调用点处在【哪条链】(投产准入 / 放行 / 巡检 / 候选验证 / 生成器写盘守卫 / 生成器 / 历史脚本) × 宽松档假绿的后果** ★ (b) ★**逐点判决表**: 哪几处【必须带 `--strict`】· 哪几处是【骨架阶段故意宽松】(那就必须点名【由哪一道别的闸兜底】· 兜底闸不在链上 ⇒ 标红)★ (c) ★**「未布线 ⇒ Gerber 不可下单」这条必须成立在哪几道闸上, 现状缺哪几道** ★ |
| ② | 新闸 | ★**新建** `HW/check_onepass_release_chain_teeth.py` ★ | ★**裸跑 rc=1** (★红的是现状, 不是闸故障★) · `--selftest` **rc=0** · 末行逐字 `ALL TESTS PASS` (★正向 ≥1 + 反向 ≥8★) · ★**零挂链** (★`grep -c check_onepass_release_chain_teeth state/gate_check.py` = 0★) |
| ③ | 交卷页 | ★**新建** `HANDOFF/2026-11-25_hw-lead_ISS409_放行链牙齿清账与闸.md` ★ | B1~B7 全填 (★标题用仓里规范口径, `state/gate_check.py` Q1 六块齐全★) |
| ④ | 自有分片收口 | `state/fragments/hw.yaml` | ★**只走 `state/frag_write.py`** ★ (★禁止 `open(p,"w")`★) · 写后四项自检: 条数 / 丢 key / 多的 key / 内容有变的条 (★老条目逐字比对★) |
| ⑤ | 留证 | `logs/iss409/` + 沙盒 `tmp/iss409/` | ★**不硬链接真件 · 不写系统 `/tmp`** ★ (★本机 `/tmp` 用户配额已打满, 写 `/tmp` 会出假读数★) |

### ★2.1 · 新闸的判据骨架 (★main 给的方向, 具体实现你定, 但不许放松★) ★

| 判据 | 要求 |
|---|---|
| ★**T1 调用点全集自洽** ★ | ★**扫描全仓**引用 `check_pcb_drc.py` 的可执行脚本 (`state/` `HW/` `SW/` `MECH/` 下的 `*.sh` `*.py`), 逐个判 argv 是否含 `--strict` ⇒ ★**判据从源码 AST/正则实读, 不许手抄清单★** · ★**扫描条数必须 ≥ 8 (★主给的口径: 宽松档脚本 ≥ 8 个★) ⇒ 少于这个数说明你的扫描漏了 ⇒ 判红** ★ |
| ★**T2 放行链必须严格档** ★ | ★**点名的那几道闸 (★投产准入 `state/chain_gate.py` · `state/board_report.sh` · `state/verify_candidate.sh` · `state/daily_check.py`★) 的调用点若不带 `--strict` ⇒ 判红** ★ ⇒ ★**这是本闸的命门判据: 现状必红** ★ |
| ★**T3 「假绿输出」不得被当放行凭据** ★ | ★**判: 有没有哪道脚本把宽松档的输出文本 (★含「图纸可下单」/「unconnected items = N」/「全过」这类字样★) 直接当成放行结论** ⇒ **判红并点名** ★ (★`state/finish_line.sh` L102 / `state/auto_release_if_ready.sh` L151 是候选★) |
| ★**T4 fail-closed** ★ | ★**输入文件缺失 / 目标被改名 / 路径不对 ⇒ 判红, 不许判绿** ★ (★扫不到任何调用点 ⇒ 也判红, 不许「没扫到就算过」★) |
| ★**T5 零挂链 + 零外发自证** ★ | `grep -c` 本闸名在 `state/gate_check.py` = 0; ★`state/outbox/` 未动 ★ |
| ★**T6 板指纹自证** ★ | ★**新闸自己不许写板** ⇒ 跑完板 md5/mtime/size 必须与开工前逐字相同 (★`611b869e13518c3c023fb178f91a0075` / `2026-11-06 07:07:17.362193413` / `4940213`★) ★ |

### ★2.2 · ★★本单【不许做】的事 (★写死, 别越界★) ★★

| ★不许★ | ★原因★ |
|---|---|
| ★**不许改 `state/check_pcb_drc.py` 一个字节** ★ | ★**它自己的判据是 main 的地界★** ⇒ 本单只出**审计 + 新闸 + 现成的一行补丁建议 (★写在真相页里给 main, 不许落进文件★)** ★ |
| ★**不许改 `state/chain_gate.py` / `state/board_report.sh` / `state/verify_candidate.sh` / `state/daily_check.py` / `state/finish_line.sh` / `state/auto_release_if_ready.sh`** ★ | ★**同上 —— 改在产生点是 main 的动作, 不是你的★** ⇒ ★**本单只负责【把哪些地方该改、该改成什么、依据是什么】一次说清, 交 main 落★** ★ |
| ★**不许挂链** ★ | `state/gate_check.py` 一个字节都不许动 ★ |
| ★**不许改既有页正文** ★ | ★**真相页必须是【新建】文件; 既有页只许引用, 不许改写★** ★ |
| ★**不许写 `state/issue_log.yaml`** ★ | ★**签收由 main 做★** ★ |
| ★**不许发任何邮件 / 询价 / 问询 / 采购** ★ | ★**老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★** ⇒ ★**没有「批一句可以发」这个选项** ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ★ |

---

## ★★三 · 自检命令 (★交卷前必须逐条跑, 把输出贴进交卷页★) ★★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 state/check_brief_commands.py --brief-file state/dispatch_briefs/ISS-409_hw_release_chain_teeth_audit.md   # 期望 rc=0
bash state/pcbnew_py.sh state/check_pcb_drc.py             # ★宽松档读数 (★留证: 假绿对照·单跑要几分钟, 只跑一次★)
bash state/pcbnew_py.sh state/check_pcb_drc.py --strict    # ★严格档读数 (★对照: unconnected 项必须不同★)
bash state/pcbnew_py.sh state/check_pcb_nets.py             # ★C1 读数 (★用来坐实「③PCB 今天红的是 C1 不是 DRC」★)
python3 HW/check_onepass_release_chain_teeth.py            # ★裸跑 rc=1 (★红的是现状★)
python3 HW/check_onepass_release_chain_teeth.py --selftest # ★rc=0 · 末行 ALL TESTS PASS
python3 state/merge.py                                     # rc 必须 0
python3 state/gate_check.py                                # rc 必须 0 · Q1 必须 18/18
python3 state/stage_gate.py                                # ★当前 G1 · 还差 1 项 = unconnected 45→0 (★不许擦它★)
md5sum HW/PCB/demo_mainboard.kicad_pcb                     # 必须是 611b869e13518c3c023fb178f91a0075
```

---

## ★★四 · 边界自证 (★每一条都要有实测读数, 不许写「应该没碰」★) ★★

| ★边界★ | ★自证方式 (★本机实跑★) ★ |
|---|---|
| ★**零写板** ★ | `md5sum` + `stat` 三项与开工前逐字相同 (★板 md5 `611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17.362193413` / size `4940213`★) ★ |
| ★**零落表** ★ | 网表 / 脚表 / BOM 三件 md5 与开工前逐字相同 (★口径见 `state/issue_log.yaml` 里已签收单的记法★) ★ |
| ★**零改既有闸判据 / 零改既有脚本** ★ | ★**点名的 8 个文件 (`state/check_pcb_drc.py` · `state/chain_gate.py` · `state/board_report.sh` · `state/verify_candidate.sh` · `state/daily_check.py` · `state/finish_line.sh` · `state/auto_release_if_ready.sh` · `state/gate_check.py`) 的 md5 与开工前逐字相同** ★ |
| ★**零挂链** ★ | `grep -c check_onepass_release_chain_teeth state/gate_check.py` = 0 ★ |
| ★**零改既有页正文** ★ | 你引用到的既有真相页/作业包页 md5 对拍 (★逐条列出你读过的既有页 + md5★) ★ |
| ★**零外发** ★ | ★`state/outbox/` 全树逐文件 md5 未动 ★ (★22 件·不许增删改★) ★ |
| ★**不代拍** ★ | 机器块 `decision_taken_here` = `"not_decided_here"` ★ (★「该不该带 --strict」「哪道闸该挂链」都是 main 的地界★) ★ |
| ★**不自签** ★ | ★**不许写 `state/issue_log.yaml`** ★ |
| ★**只写本单允许的文件** ★ | ★**新建 3 个** (真相页 / 新闸 / 交卷页) · ★**改 1 个** (`state/fragments/hw.yaml`·走 `state/frag_write.py`·★不许写别人的分片★) · ★**留证** (`logs/iss409/` + `tmp/iss409/`) ★ |

---

> ★**本单零写板 · 零落表 (除自有分片) · 零改既有闸判据 · 零改既有脚本 · 零改既有页正文 · 零挂链 · 零外发 · 不代拍 · 不自签** ★
> ★**真相页** = `HW/PCB/BOARD_ONEPASS_RELEASE_CHAIN_TEETH_AUDIT.md` · ★**新闸** = `HW/check_onepass_release_chain_teeth.py` · ★**留证** = `logs/iss409/` + `tmp/iss409/` ★


---

★额外纪律: ① 写分片必须用 state/frag_write.py (禁止 open(p,"w")) ② 只写本任务允许的文件, 不碰别人的 ③ 证据分级 [官网]/[实测]/[媒体]/[推算]/[0数据] 必须标 ④ ★**不许外发任何邮件/询价/问询/采购 (老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料) ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ⇒ 没有"批一句可以发"这个选项** ⑤ 交卷前跑 python3 state/merge.py (rc 必须 0) && python3 state/gate_check.py (Q1 必须 18/18) 并把输出贴进回复
