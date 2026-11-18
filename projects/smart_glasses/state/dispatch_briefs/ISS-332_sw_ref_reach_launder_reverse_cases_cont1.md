【ISS-332 · sw-lead · ★★cont1 续做单 · ★★不是从零·是【把上一趟的半成品补完】★★】

★**派活人**: 项目总工 (main / cron fb67af40 · 2026-11-18 21:2x)
★**任务书全文 (上一趟那份 · 仍然有效·你必须逐条对着它交)**: `state/dispatch_briefs/ISS-332_sw_ref_reach_launder_reverse_cases.md` (10,358 B)
★**本单 = 上一趟那一条的续做**: ★**你的成果大部分在盘, 但【核心判据没抓住洗白面】+ 【交卷三件套一件没写】⇒ 这一趟把这几件补完** ★

---

## ★★★【① 为什么派这一条 (★本机实跑读数·不抄任何 agent 报告★)★★★】

| ★项★ | ★21:1x~21:2x 本机实跑★ | ★判★ |
|---|---|---|
| ★上一趟会话★ | `~/.openclaw/agents/sw-lead/sessions/dc869eaf-….jsonl` ★**最后一条 = assistant · `stopReason: error` · `errorMessage: "invalid params, context window exceeds limit (2013)"` @ 21:05:32** ★ | ★**会话死了 (★不是活链, 是上下文爆掉★)** ⇒ ★**本单从新会话起·不要试图接续那条死会话的上下文** ★ |
| ★在盘 ①★ | ★**`SW/tools/check_sw_ref_reachability_v2.py` (45,339 B · 21:05:29)** ★ ⇒ main 21:1x 实跑 `python3 SW/tools/check_sw_ref_reachability_v2.py` ⇒ **rc=0** (TP_TEMP 仍判 C14 · U_DCDC 判 C12 · VBUS_DET_uA 判 C7) ★ | ★**在盘·能跑** ★ |
| ★在盘 ②★ | ★**`python3 SW/tools/check_sw_ref_reachability_v2.py --selftest` ⇒ rc=0 · 反向用例 7/7 (RC-1~RC-7) 通过** ★ | ★**在盘·绿** ★ |
| ★在盘 ③★ | ★**`logs/iss332/` 12 件**: `00_real_gate_baseline.txt` / `01_real_gate_full_class.txt` / `02_gate_check_pre.txt` / `10_base_tree_readings.txt` / `2RT-5_RT-5_real.txt` ~ `2RT-8_RT-8_real.txt` (4 件) / `2CTL-1_CTL-1_real.txt` ~ `2CTL-3_CTL-3_real.txt` (3 件) / `iss332_repro.py` (★11,074 B·自带 `--with-v2` 入口★) ★ | ★**在盘·证据够用** ★ |
| ★在盘 ④★ | ★**`tmp/iss332/sb_base/` 沙盒在盘** ★ | ★**在盘** ★ |
| ★★缺 ①★★ | ★**★`SW/tools/check_sw_ref_reachability_v2_selftest.py` 【不存在】★** (★main 21:1x 实跑 ⇒ `No such file or directory`★) ★ | ★**缺** ★ |
| ★★缺 ②★★ | ★**★`HANDOFF/2026-11-18_sw-lead_ISS332_SW位号可达性闸4条洗白面收紧.md` 【不存在】★** ★ | ★**缺** ★ |
| ★★缺 ③★★ | ★**★`grep -c "iss332" state/fragments/sw.yaml` = 0** (★分片一字没写·★必须走 `python3 state/frag_write.py --agent sw-lead`★) ★ | ★**缺** ★ |
| ★★缺 ④★★ | ★**挂闸/切换写法三问 (怎么切 / 怎么挂 / 旧闸要不要退役) 没写进任何文件** ★ | ★**缺** ★ |

---

## ★★★【② ★★最要紧的一条: ★★你上一趟的 v2 ★【没抓住那 4 条洗白面】★★】★★★

★**main 21:2x 本机实跑 (★你自带的复现脚本 + `--with-v2`★) ⇒ 判决表逐字如下 (★自己复跑一遍核对★)**:

```
用例     旧 token      -> 新 token        | 期望[v2]    | 实际[v2]    | 判决
RT-5   TP_TEMP      -> U_TEMP_1       | rc=1      | rc=0      | ✘ 不符
RT-6   TP_TEMP      -> TP_temp        | rc=1      | rc=0      | ✘ 不符
RT-7   TP_TEMP      -> SW_TEMP_ISSX   | rc=1      | rc=0      | ✘ 不符
RT-8   TP_TEMP      -> TP_TEMP_       | rc=1      | rc=0      | ✘ 不符
CTL-1  TP_TEMP      -> TP_TEMP_ISSX   | rc=1      | rc=1      | ✔ 抓住+点名
CTL-2  TP_INT       -> TP_INT_ISSX    | rc=1      | rc=1      | ✔ 抓住+点名
CTL-3  CONN_USB     -> CONN_USB_ISSX  | rc=1      | rc=1      | ✔ 抓住+点名
```

★**读法 (★别读反★)**: ★**4 条洗白面 (RT-5~RT-8) 现在还是绿 (rc=0) ⇒ ★v2 没收紧住 ⇒ 这正是本单要修的东西** ★
★**3 条对照 (CTL-1~CTL-3) 在 v2 下仍然红 ⇒ ★v2 至少没有把闸调死** ★

★**★⇒ 你的第一个动作 = 把 v2 修到 RT-5~RT-8 四条全红 + CTL-1~CTL-3 三条仍红** ★
★**★⇒ 复跑命令 (★自己跑·不要只信本文档★)**: `python3 logs/iss332/iss332_repro.py --with-v2` ⇒ ★**判决表里 4 条洗白面的「实际[v2]」必须变成 rc=1** ★

★**★为什么现在还是绿的 (★main 实读 v2 源码得出的线索·不是猜·你自己复核★)**:
- ★v2 里 ★**执法点 A 用的是新台账 `EXEMPT_LEDGER`** (★v2 L15/L17 附近★) ⇒ ★**而任务书原文写的是「只有【在 `BASELINE_TOKENS` 里登记过的 token】才允许按 C1/C7/C8/C12/C13 判成 DOC_INTERNAL/NET_NAME」** ⇒ ★**⇒ 两本台账的关系你必须在交卷页里写清楚** (★是同一本还是两本? 哪几条 token 在 A 不在 B? ★main 要据此拍切不切★)
- ★**C1 那条分支 (★"板上真存在的位号名" 洗白面 RT-5·任务书点名的第 1 条·最容易漏★)**: ★**登记制必须落在【解析出 live 位号名】这条路上** ⇒ ★**凡是被登记台账之外的 token 解析成的 live 位号, 一律不许直接判 OK** ★
- ★**★改判据的方向不许变**: ★**不许把任何一条洗白面改成【新加一条豁免规则】来"合法放过"** ⇒ ★**收紧 = 【真隐患 token 必须在册】· 形状豁免只对在册 token 生效** ★

---

## ★★★【③ 本单要交的五件 (★就这五件·★不要顺手多跑别的★)★★★】

| ★#★ | ★交付物★ | ★路径★ | ★状态★ |
|---|---|---|---|
| ★1★ | ★**把 v2 修到 4 条洗白面全红** ★ | ★`SW/tools/check_sw_ref_reachability_v2.py` (★已在盘·**只许改这一个文件**★) ★ | ★**改** ★ |
| ★2★ | ★**自测脚本 (★新建★)** ★ | ★**★新建★** `SW/tools/check_sw_ref_reachability_v2_selftest.py` ⇒ ★**带 `--selftest` 入口★** ★ | ★**新建** ★ |
| ★3★ | ★**交卷页 (★新建★)** ★ | ★**★新建★** `HANDOFF/2026-11-18_sw-lead_ISS332_SW位号可达性闸4条洗白面收紧.md` ⇒ ★**B0~B6 齐全** ★ | ★**新建** ★ |
| ★4★ | ★**分片** ★ | ★`state/fragments/sw.yaml` ⇒ ★**必须走 `python3 state/frag_write.py --agent sw-lead`** (★**禁止 `open(p,"w")`★) ★ | ★**写** ★ |
| ★5★ | ★**证据补齐** ★ | ★`logs/iss332/` ⇒ ★**v2 侧的 RT-5~RT-8 + CTL-1~CTL-3 判决表要有对应 raw 文件 (★`--with-v2` 已经会写·自己确认落盘了★)** ★ | ★**补** ★ |

### ★★★【第 2 件 · 自测脚本必须覆盖的四组 (★任务书 §② 第 ② 件的原文口径★)★★★】★★
1. ★**① 正向**: ★**现状真件树跑 ⇒ rc=0 · 读数与真件逐字相同 (★DESIGNATOR_OK 78 / DESIGNATOR_MISSING 3 / NET_NAME 9 / DOC_INTERNAL 23 · 真隐患 = CONN_USB, TP_INT, TP_TEMP · ★这组数 main 21:2x 实测过★)** ★
2. ★**② 4 条洗白面反向用例 (RT-5~RT-8)**: ★**每条必须 rc≠0 且【点名那条 token】** ★
3. ★**③ 3 条「真隐患变个形状」反向用例 (CTL-1~CTL-3)**: ★**必须仍被抓住 ⇒ 证明不是把闸调死** ★
4. ★**④ 假绿用例**: ★**判据分支匹配不上时必须【红】, 不许静悄悄不查了** ★

### ★★★【第 3 件 · 交卷页 B0~B6 必须写到的内容 (★任务书 §② 第 ③ 件的三小问不许含糊★)★★★】★★
- ★**B1 结论摘要**: ★**v2 到底收紧了没有 (★4 条洗白面现在红不红·逐条给 rc★)· 基线数动不动 (★`BASELINE_COUNT` 仍是 3·**不许调大**★)** ★
- ★**B2 验收标准自评**: ★**逐条「通过 / 不通过 / 未验」· 不许留空** ★
- ★**B3 证据分级**: ★**每条读数带 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` 标签 ★**实测=本机跑出来的★**
- ★**B4 接口取值声明 + 挂闸/切换写法三问**: ★**① 怎么切 (真件与 v2 的逐条差异清单·带行号·建议 main 怎么做·各自代价) ★② 怎么挂 (★实读 `state/gate_check.py` 的 `EXTRA_GATES` 结构·不许猜·给出「挂第几位 / 调用形态 / 参数怎么传」的逐字写法 + 行号·★**你不许动手改**) ★③ 旧闸要不要退役 (★给明确建议 + 理由·不许含糊★) ★**
- ★**B5 未决项与卡点**: ★**★至少写清「`EXEMPT_LEDGER` 与 `BASELINE_TOKENS` 是不是同一本台账」这一条 (★main 要据此拍切不切★)★**
- ★**B6 自证复现命令**: ★**原样贴输出** ★
- ★**★不许留「(施工中)」占位符** ★

---

## ★★★【④ 边界 (★违反就是不合格★)★★★】★★
- ★**零写板**: ★**`HW/PCB/demo_mainboard.kicad_pcb` md5 必须还是 `611b869e13518c3c023fb178f91a0075` · mtime 必须还是 `2026-11-06 07:07:17.362193413`** (★main 21:2x 实测过·★变了一律不合格★) ★
- ★**零落表** (★网表/脚表/BOM/原理图真源一个字节不许动★)
- ★★★**零改真件 `SW/tools/check_sw_ref_reachability.py`** (★★它是链上那道闸·★改了就失真★) ★★★ · ★**零改 `state/gate_check.py`** (★挂闸是 main 的机制地界★) ★ · ★**零改 `state/check_*.py`** · ★**零改 `SW/SW_MD5_BASELINE_LEDGER.md`** (★它是判据的锚点账★)
- ★**沙盒只写 `tmp/iss332/` + `logs/iss332/`** · ★**只写 `state/fragments/sw.yaml`** · ★**零外发** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信 ⇒ **没有「批一句可以发」这个选项**★) · ★**不替老板拍板** · ★**不自签 `state/issue_log.yaml`** ★
- ★**沙盒里凡要【写】的文件 ⇒ 一律真拷贝; 写前 `assert not os.path.islink(path)`** (★你 11-18 14:39 因为软链写穿过一次真件★) ★
- ★**文档纪律 (★你 11-18 16:3x 自踩过的坑·必须继续守★)**: ★**SW 侧任何要写「改名后名」或「形状像位号但不是位号」的文档 (★方案文档 / 作业包 / 交接页★) ⇒ ★**一律写进 `logs/iss332/`, 不许写进 `SW/`** ⇒ ★**否则会把 ISS-318 那道闸带红 (★实测: 「把大写注入名原样写进 SOP」⇒ 闸判 5 条新增真隐患 ⇒ MISSING 8 > 上限 3 ⇒ rc=1★)** ★
- ★★★**★★这一趟专门给你的抗上下文护栏 (★上一趟就是死在这上面·★21:05:32「context window exceeds limit」★)★★**: ★★★
  1. ★**不要通读 v2 全文 (900 行) ⇒ 用 `grep -n` 定位到行再 `sed -n 'a,bp'` 看那一小段** ★
  2. ★**不要把大文件整段贴回对话 ⇒ 只贴你改的那几行 + rc 读数** ★
  3. ★**一次 write ≤ 3000 字 ⇒ 先 write 骨架 (B0~B6 标题 + 每节 1~2 行), 再 edit 逐块补** (★ISS-326 连挂两趟都是死在超长 write 上★) ★
  4. ★**不要重跑已经跑过的东西** ⇒ `logs/iss332/` 里 4 条 RT + 3 条 CTL 的真件读数已经在盘, ★**你只需要跑 v2 侧的那 7 条** ★
  5. ★**回复控制在 ~800 字以内 · 只贴判决表 + rc + 文件清单** ★

---

## ★★★【⑤ 交卷前必跑 (★原样输出贴进交卷页 B6·★期望值写在后面★)★★★】★★】
```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 logs/iss332/iss332_repro.py --with-v2   # ★4 条洗白面实际[v2] 必须全 rc=1 · 3 条对照必须仍 rc=1
python3 SW/tools/check_sw_ref_reachability_v2.py --selftest   # ★rc 必须 0
python3 SW/tools/check_sw_ref_reachability_v2_selftest.py --selftest   # ★rc 必须 0 · 四组全过 (★新建文件·★建完再跑★)
python3 SW/tools/check_sw_ref_reachability.py   # ★真件闸 rc 必须 0 (★基线读数·不许你改它★)
python3 state/merge.py   # rc 必须 0
python3 state/gate_check.py   # rc 必须 0
python3 state/issue_check.py   # rc 必须 0
md5sum HW/PCB/demo_mainboard.kicad_pcb   # 必须 611b869e13518c3c023fb178f91a0075
stat -c '%y' HW/PCB/demo_mainboard.kicad_pcb   # 必须 2026-11-06 07:07:17.362193413
grep -cE "🔄|待填|PLACEHOLDER|施工中|__[A-Z_]+__" "HANDOFF/2026-11-18_sw-lead_ISS332_SW位号可达性闸4条洗白面收紧.md"   # 必须 0
grep -c "iss332" state/fragments/sw.yaml   # 必须 >= 1
find tmp/iss332 -type l | wc -l   # 必须 0 (★不许有软链★)
```
★额外纪律: ★**证据分级 [官网]/[实测]/[媒体]/[推算]/[0数据] 必须标** ★ · ★**不许外发任何邮件/询价/问询/采购 ⇒ 缺口一律自己网上查 + 标证据等级 + 写降级方案** ★ · ★**交卷前跑 merge.py (rc=0) && gate_check.py (rc=0) 并把输出贴进回复** ★

---

★派活标记=CONT-20261118-2120★
★**本单 status 仍是 fixing ⇒ 无 open 窗口 ⇒ 兄弟 job 775d9893 不会重复派** ★
