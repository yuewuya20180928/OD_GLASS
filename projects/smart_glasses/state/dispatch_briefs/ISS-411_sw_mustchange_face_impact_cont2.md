# ★★[cont2 续派 · ISS-411] sw-lead · 软件总工

【项目总工派活 · 队列自动推进 · 闭环 ISS-411 (cont2)】你是 软件总工 (sw-lead)。
★★【★★★ cont2 · 只补缺口 · 上一趟 (cont1) 又被【共因掐死】★★★】★★

★**死因 (main 本机实读 `~/.openclaw/subagents/runs.json` + 会话状态, 不抄任何 agent 报告)**:
  · cont1 的 `runTimeoutSeconds` = **5400 (90 分钟)**, **没到** ⇒ **不是你超时** (★会话状态 `timeout` + `abortedLastRun=true`★)
  · cont1 起于 **03:12:32**, 死于 **03:21:20**; 同一秒死的还有 mech-lead 的 cont1 (03:21:20)
    ⇒ **共因中断** (★与 03:03:28.846~03:03:29.972 同型 · 与 02:07:37~02:07:40 同型 · 与 2026-11-23 21:51:49 同型★)
  · ⇒ **本趟 = 从【已在盘的东西】接着做, 不是从零做 ⇒ 已在盘的读数直接用, 不要重跑** (★重跑一遍要几分钟到几十分钟, 而你可能又被掐★)

★★**三条硬纪律 (★因为【你随时可能被掐】★★)**:
  ① ★**先落盘, 后汇报**★ —— 每完成一件交付物**立刻**写盘 (★别攒到最后一起写★)
  ② ★**交卷页 + 自有分片 优先**★ —— 这两个是 main 签收的凭据 ⇒ **先把它们写完**, 其余往后排
  ③ ★**如果你感觉时间紧 ⇒ 交卷页 + 分片 + 一份短报告交上来, 剩下的写进交卷页的「未完成」段**★ ⇒ ★**不许交半份然后什么都不留★**

★**不许做的事 (★与原 brief 一致, 本头不放松★)**:
  ★**零写板 · 零落表 (除自有分片) · 零改既有闸判据 · 零改既有脚本 · 零改既有页正文 (★只许追加式改【你自己新建的真相页】★) · 零挂链 · 零外发 · 不代拍 · 不自签 `state/issue_log.yaml` ★**

---

## ★★一 · 已在盘 (★main 本机实测, 直接用, 不要重做★) ★★

| 交付物 | 状态 (main 03:3x 实读) |
|---|---|
| ★**① 真相页 `SW/BOARD_ONEPASS_SW_MUSTCHANGE_FACE_IMPACT.md`** ★ | ★**已在盘 · 66,293 B @ 03:16** ★ ⇒ ★**cont1 已把它写出来了 ⇒ 本趟【不许推倒重写】, 只许【追加式】补 (★补前记字节数 + md5, 补后记补后的, 两组数字都写进交卷页★)★** |
| ★**② 新闸 `SW/tools/check_sw_mustchange_face_impact.py`** ★ | ★**已在盘 · 39,727 B @ 03:17** ★ · ★**main 本机实测 `--selftest` rc=0 · 末行逐字 `ALL TESTS PASS` (★反向用例 15/15 通过★)** ★ · 裸跑 rc=1 (★红的是现状, 不是闸故障★) · ★**零挂链** ★ |
| ★**③ 留证 `logs/iss411/`** ★ | ★**已在盘** (gate_selftest.txt / gate_bare.txt / gates31_md5_after.txt / board_tables_after.txt / baseline_*.txt) ★ |
| ★**④ `state/fragments/sw.yaml` 收口** ★ | ★**✘ 还没写** ★★**main 实测: `state/fragments/sw.yaml` mtime 仍 = 02:31:00 · grep `iss411`/`mustchange_face` = 0 命中** ★★ ⇒ ★**cont1 是被掐在【写分片】这一步** (★它自己的 transcript 末条逐字: 「The fragment write was rejected (rc=2, file untouched — atomic). The values need shell-quoting. Fixing:」★) ★ |
| ★**⑤ 交卷页** ★ | ★**✘ 不在盘** ★★**main 实测: `HANDOFF/` 下没有任何 ISS-411 交卷页** ★ |

---

## ★★二 · ★本趟只补这 4 件 (★这才是你的活★) ★★

### ★① `state/fragments/sw.yaml` 收口 (★最高优先 · main 签收的凭据★) ★
★**只走 `state/frag_write.py` 的原子写 API (★禁止 `open(p,"w")`★) · 值里带空格/引号/冒号 ⇒ 正确 quoting, 别再被 rc=2 拒★** ★
★**四项自检必须过**: ① 丢 key = 0 ② 多的 key = 全部是本单新增 ③ 老条目内容逐条 md5 未变 ④ 文件仍是合法 YAML ★
★**建议登记项 (★ID 用 ISS-411·键名前缀 `iss411_`·不许碰别人的键★)**:
  · `artifacts`: ★`SW/BOARD_ONEPASS_SW_MUSTCHANGE_FACE_IMPACT.md` · `SW/tools/check_sw_mustchange_face_impact.py` · ★`HANDOFF/2026-11-25_sw-lead_ISS411_SW必改面影响面清账与闸.md` ★
  · `interface_claims`: ★必改面 (改名面 / 布线面) 对 31 道 SW 闸的逐条影响 + 哪些是【判绿变判红 / 判红变判绿 / 静默跳过】 ★
  · `needs_open_ledger`: ★**一条不代拍** (★「哪几道闸要改 / 怎么改 / 挂不挂链」全是 main 的地界★) ★
  · `answers`: ★若你确实能答的 (★带证据等级★) ★

### ★② ★★交卷页 ★★ (★main 签收的第二个凭据★)
★**新建 `HANDOFF/2026-11-25_sw-lead_ISS411_SW必改面影响面清账与闸.md`** ★
★**B1~B7 全填 (★`state/gate_check.py` 的 Q1 六块齐全★)**: 结论摘要 / 验收标准自评 / 证据分级 (★`[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]`★) / 接口取值声明 / 未决项 (★一律 `to=main`, 一条不代拍★) / 自证复现命令 / 边界自证逐条读数 ★

### ★③ ★★【★★本趟最要紧的一件★★】真相页里 3 个【沙盒合成 token】把链上的闸打红了 ⇒ 必须修回绿 ★★
★**main 03:28 本机实跑 `state/gate_check.py` ⇒ rc=1 (★r92~r95 的基线是 rc=0 ⇒ 这是【本单带出来的新红】★)** ★
★**红项逐字 (main 实跑 `python3 SW/tools/check_sw_ref_reachability.py` ⇒ rc=1)**:
```
[FAIL] 位号引用解析不到 (新增真隐患·超基线): TP_INT_ISSX  @ SW/BOARD_ONEPASS_SW_MUSTCHANGE_FACE_IMPACT.md:119 ⇒ 板与网表里现在叫: (无近似名)
[FAIL] 位号引用解析不到 (新增真隐患·超基线): TP_TEMP_ISSX @ SW/BOARD_ONEPASS_SW_MUSTCHANGE_FACE_IMPACT.md:119 ⇒ 板与网表里现在叫: (无近似名)
[FAIL] 位号引用解析不到 (新增真隐患·超基线): U_TEMP_1     @ SW/BOARD_ONEPASS_SW_MUSTCHANGE_FACE_IMPACT.md:119 ⇒ 板与网表里现在叫: U_TEMP
[FAIL] 真隐患条数 6 > 基线上限 3 (★基线只许收紧不许放宽★)
```
★**根因 (main 实读)**: 这道闸 (`SW/tools/check_sw_ref_reachability.py`) 扫【全仓文档里的位号形状 token】⇒ 你真相页第 119 行那一格把三个**沙盒合成 token** 原样写了出来 (★你自己在第 29 行也写了「另 5 处是沙盒合成 token」★) ⇒ 它们长得像真位号 ⇒ 被判成【新增真隐患】⇒ 计数 6 > 基线 3 ⇒ **链上这道闸红了** ★
★**处置 (★只许改【你自己新建的真相页】的写法, 不许改既有闸的任何东西★)**:
  ★**改页面写法** ⇒ 把那三个合成 token 改成【长得不像真位号】的写法 (★例: `TP_INT_ISS<X>` / `TP_TEMP_ISS<X>` / `U_TEMP_<N>` 这类带尖括号/下划线占位的写法 ⇒ 语义一字不丢, 但闸扫不到★) ⇒ **然后实跑 `python3 SW/tools/check_sw_ref_reachability.py` 必须 rc=0** ★
  ★**不许做的事**: ★不许放宽 `BASELINE_COUNT` · 不许往 `BASELINE_TOKENS` 里塞新 token (★那叫放宽基线·方向反了★) · 不许改那道闸的任何判据 · 不许改任何别的既有闸 ★
  ★**改完在交卷页里写明**: 改前 md5 + 字节数 / 改后 md5 + 字节数 / 实跑读数 (★rc=0 的输出逐字贴上★) ★

### ★④ 交卷报告 (★短·一份就够★)
★**五条以内**: 交了什么 / 验了什么 (逐条 rc) / 还差什么 (写进交卷页「未完成」段) / 板三证 / 未代拍声明 ★

---

## ★★三 · 自检命令 (★交卷前必须逐条跑, 把输出贴进交卷页★) ★★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 state/check_brief_commands.py --brief-file state/dispatch_briefs/ISS-411_sw_mustchange_face_impact_cont2.md   # 期望 rc=0
python3 SW/tools/check_sw_ref_reachability.py             # ★★必须 rc=0 (★main 03:28 实读 rc=1 ⇒ 这就是你本趟要修的那条★)
python3 SW/tools/check_sw_mustchange_face_impact.py        # ★裸跑 rc=1 (★红的是现状★)
python3 SW/tools/check_sw_mustchange_face_impact.py --selftest   # ★rc=0 · 末行 ALL TESTS PASS (★main 03:2x 实跑已过·复核一下★)
python3 state/merge.py                                    # rc 必须 0
python3 state/gate_check.py                               # ★rc 必须 0 · Q1 必须 18/18 (★main 03:28 实读 rc=1 ⇒ 修完那 3 个 token 就该回 0★)
md5sum HW/PCB/demo_mainboard.kicad_pcb                    # 必须是 611b869e13518c3c023fb178f91a0075
```

---

## ★★四 · 边界自证 (★每一条都要有实测读数, 不许写「应该没碰」★) ★★

| ★边界★ | ★自证方式 (★本机实跑★) ★ |
|---|---|
| ★**零写板** ★ | `md5sum` + `stat` 三项与开工前逐字相同 (★板 md5 `611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17.362193413` / size `4940213`★) ★ |
| ★**零落表** ★ | 网表 `6aee500e60ba0732f83a9cf557ba90ab` · 脚表 `9174309df1ec9411ac8e8d9e80ee386a` · BOM `5b9993992405904a60ac96a020b375d8` 三件 md5 与开工前逐字相同 ★ |
| ★**零改既有闸判据** ★ | ★**31 道 SW 闸的 md5 汇总与开工前逐字相同 (★至少点名 `check_sw_ref_reachability.py` / `check_sw_ref_reachability_v2.py` / `check_onepass_sw_sync.py` 三道·给出全量 md5 汇总★)** ★ |
| ★**零改既有页正文** ★ | ★**你引用到的既有 SW 页 md5 对拍 (★注意: `SW/BOARD_ONEPASS_SW_MUSTCHANGE_FACE_IMPACT.md` 是【你自己新建的】⇒ 本趟只许【追加式】改它·其余既有页一律不许动★)** ★ |
| ★**零挂链** ★ | `grep -c check_sw_mustchange_face_impact state/gate_check.py` = 0 ★ |
| ★**零外发** ★ | ★`state/outbox/` 全树逐文件 md5 未动 (★22 件★) ★ |
| ★**不代拍** ★ | 机器块 `decision_taken_here` = `"not_decided_here"` ★ |
| ★**不自签** ★ | ★**不许写 `state/issue_log.yaml`** ★ |
| ★**只写本单允许的文件** ★ | ★**新建 1 个** (交卷页) · ★**改 2 个** (★`SW/BOARD_ONEPASS_SW_MUSTCHANGE_FACE_IMPACT.md` 追加式 · `state/fragments/sw.yaml` 走 `frag_write.py`·★不许写别人的分片★) · ★**留证** (`logs/iss411/` + `tmp/iss411/`) ★ |

---

> ★**本单零写板 · 零落表 (除自有分片) · 零改既有闸判据 · 零改既有页正文 · 零挂链 · 零外发 · 不代拍 · 不自签** ★
> ★**留证** = `logs/iss411/` + `tmp/iss411/` (★不许硬链接真件·不许往系统 `/tmp` 写字节★) ★

★额外纪律: ① 写分片必须用 `state/frag_write.py` (禁止 `open(p,"w")`) ② 只写本任务允许的文件, 不碰别人的 ③ 证据分级 [官网]/[实测]/[媒体]/[推算]/[0数据] 必须标 ④ ★**不许外发任何邮件/询价/问询/采购 (老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料) ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ⇒ 没有"批一句可以发"这个选项** ⑤ ★**交卷前必须自己实跑 `python3 state/gate_check.py` 并把 rc 贴进交卷页** (★main 03:28 实读 rc=1 ⇒ 你的活之一就是把它修回 0★)
