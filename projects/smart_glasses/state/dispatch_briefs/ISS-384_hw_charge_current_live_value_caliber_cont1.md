# ISS-384 · cont1 · hw-lead · 把「充电电流活值口径收口」从【四件交付物已在盘 · 但零交卷】做到【独立复核 + 交卷】· 零写板 · 零落表 · 零改既有闸

★**本单 = ISS-384 cont1 (★不是新单 · 不是从零重做 · ★)** ★
★**本单 = 纯文档口径订正 + 新建机器闸 (★闸与页已写好 · 本趟只做独立复核与交卷★) · 零写板 · 零落表 · 零改既有闸/既有页面正文 · 零外发 · 不代拍** ⇒ 合「板只改一次」纪律 ① (先派不动板的) ★

---

## ★★一 · 上一趟怎么死的 (★main 本机实读 · 不抄任何 agent 报告★) ★★

★**上一趟 = 2026-11-24 08:28:42 起 · 08:45:35 止 · runtimeMs 1,010,660 (≈16.8 分钟) · `status=timeout` + `abortedLastRun=true`** ★
★**子会话** `agent:hw-lead:subagent:5c3ed7dd-3483-49e4-91a4-8f3625fa4212` / sessionId `68f65987-eef8-4b4a-88d5-454504268a9d` · transcript 495,391 B @08:45:35 · 76 行 · ★**不是空壳 (有 27 次 exec + 5 次 write 的 tool_use 记录)★** ★
★**死因 = 墙 (≈16.8 分钟) 掐在最后一次 `state/gate_check.py` 上 ⇒ ★★四件交付物全部已在盘, 但【交卷消息】没发出来 ⇒ 零交卷★★ ★
★★**⇒ 本趟定位: 【收尾趟】—— 独立复核 + 补缺 + 交卷消息 ⇒ ★★不许重做任何一件交付物★★ ★★**

★★**★上一趟已经在盘的产物 (★main 本机实读 2026-11-24 08:46~08:47 · 你要自己再核一遍★)★★ ★★

| ★产物★ | ★大小 / mtime / md5(前8)★ | ★本趟怎么用★ |
|---|---|---|
| ★`HW/CHARGE_CURRENT_LIVE_VALUE_CALIBER.md` ★ | 22,908 B @08:38:41 · `3cb3d6a4` ★ | ★**真相页已在盘** ⇒ ★**只许读 + 只许追加式补注 (★正文一字不许删改★)** ★ |
| ★`HW/check_charge_current_live_value.py` ★ | 21,898 B @08:38:59 · `9f1dbd6c` ★ | ★**新闸已在盘** ⇒ ★**只许跑 + 只许修【误报/漏检/崩溃】(★不许放松任何判据★)** ★ |
| ★`HANDOFF/2026-11-24_hw-lead_ISS384_充电电流活值口径收口与R10判定面盲区.md` ★ | 22,304 B @08:39:59 · `f2f10dee` ★ | ★**交卷页已在盘 (B1~B6 齐全)** ⇒ ★**本趟只追加 B7 (本趟复核段) · ★B1~B6 一字不许改★ ★ |
| ★`state/fragments/hw.yaml` ★ | 736,680 B @08:40:28 · `2461f6a8` ★ | ★**分片已写 (走 `state/frag_write.py` 的 `update_fragment` API: artifacts +3 / interface_claims +12 / needs_from +4)** ⇒ ★**本趟只在【确有必要】时补 needs, ★不许重复 key★ ★ |
| ★三份活文档的追加式订正块 ★ | `HW/PCB_OUTLINE_60x15.md` / `HW/J_CHG_SELECTION.md` / `HW/POWER_BUDGET_V3.md` 全部 @08:38:41 ★ | ★**订正块已在盘** ⇒ ★★**本趟不许再追加第二块订正块** (★重复追加 = 页面自相矛盾 = 比不追加更坏★)★★ ★ |
| ★留证 `logs/iss384/` ★ | `docs_md5_before.txt` (170 B) · `hinge_calc_json.txt` (19,514 B) · `hw.yaml.before` (729,355 B) ★ | ★**开工前指纹与权威表读数已在盘** ⇒ ★**不要重扫·直接用★ ★ |

★★**★main 本机已复核过的读数 (2026-11-24 08:46~08:47 实跑 · ★你要自己再跑一遍, 别只抄本表★)★★ ★★

```
$ python3 HW/check_charge_current_live_value.py            ⇒ rc=0
  ✅ 三份 HW 活文档的充电电流活值已追平到 680Ω 落表真值 (ISS-384)
  · 真值: 680Ω → ICHG 0.697A / 单 pin 0.349A / 余量 1.43× · 系数 1.216 @3.70V / 1.071 @4.20V
  · 历史留痕 (ISS-230 作废标记 L151/L193): 未误伤
$ md5sum HW/PCB/demo_mainboard.kicad_pcb   ⇒ 611b869e13518c3c023fb178f91a0075
$ stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb ⇒ 2026-11-06 07:07:17.362193413 · 4940213   (零写板)
$ md5sum HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
  ⇒ 6aee500e… / 9174309d… / 5b999399…  (零落表)
$ python3 state/gate_check.py                ⇒ rc=0  (Q1 18/18 · 钉板闸 10/10 道绿)
```

★**★一条要如实报进交卷的事实 (★main 本机实读★)**: ★**`MECH/hinge_power_calc.json` 的 mtime 变成了 08:29 (★上一趟跑了 `python3 MECH/hinge_power_calc.py --json` ⇒ 那是本单 §三 明写的【权威源重新生成】命令★) ⇒ ★**内容与 git HEAD 逐字相同 (`git diff` 输出为空) ⇒ 只换了 mtime, 不是内容漂移** ★ ⇒ ★**但它是一份【已签收件 (ISS-229 verified)】⇒ 本趟要自己 `git diff -- MECH/hinge_power_calc.json` 复核一遍并把结论写进 B7** ★

---

## ★★二 · 本趟的时间预算 (★本项目子会话的真实墙 ★★约 16~17 分钟★★) ★★

★**墙 = 实测 16.8 分钟 (上一趟被掐) ⇒ ★本趟必须按【收尾趟】切★** ★
★**★顺序不许改 (★每一步都落盘★)**:
1. ★**第 1 步 (≤4 分钟) · 独立复核**: 跑下面 §四 的必跑命令 ⇒ ★**把原样输出落 `logs/iss384/cont1_verify.log`** ⇒ ★**逐条对照 §一 的「已在盘」清单 + §一 的「main 已复核读数」⇒ 有任何对不上, 如实写出来 (★不许糊过去★)★ ★
2. ★**第 2 步 (≤3 分钟)**: 交卷页 ★**追加** B7 段 (★只追加, ★B1~B6 一字不许改★) ⇒ ★**B7 = 本趟独立复核段: 逐条复核结论 + 必跑命令原样输出 + 板/网表/脚表/BOM 四项指纹前后对比 + `MECH/hinge_power_calc.json` 的 git diff 复核结论 + 要 main 裁的事 (逐条「要谁回答什么」) + 本趟发现的任何缺口 (★包括「上一趟有某件没写全」★)★ ★
3. ★**第 3 步 (≤2 分钟)**: 分片 —— ★**上一趟已写 (frag @08:40:28) ⇒ 本趟默认【零写入】** ⇒ ★**只有在 §一 复核发现【真缺一条 need】时才补, 且必须走 `state/frag_write.py`, key 不许重复** ★
4. ★**第 4 步 (★最关键★)**: ★**交卷消息 (★上一趟就是死在这★)** ★

★★**★如果时间在第 2 步用完 ⇒ 允许直接交卷 (B7 可只写前半段) ⇒ ★★但交卷消息【绝对不许省】★★ ★★**

---

## ★★三 · 本单的地界事实 (★不许越★) ★★

★**① 网表一个字不许动** —— `HW/netlist_v1.csv` L47/L48 的 `R_ILIM` 自 2026-11-16 (V-4 裁定) 起已落成 **680Ω** ⇒ ★**网表侧早就对了, 错的是三份文档还在说 390Ω 档 + 0.822 系数** ⇒ ★**本单 = 把文档追平到已落表的真值, 不是改一个数** ⇒ ★**动网表 = 违「板只改一次」★ ★
★★**② 「历史留痕」格只加不删** —— `HW/PCB_OUTLINE_60x15.md` L151 / L193 是 ISS-230 留下的作废标记 ⇒ ★**这两个地方一个字都不许删** ★
★★**③ `MECH/HINGE_POWER_CALC.md` + `MECH/hinge_power_calc.json` = ISS-229 已 verified 的【已签收权威源】⇒ ★**只许引用, 不许改** (★`hinge_power_calc.py --json` 是「重新生成」不是「改内容」★)★ ★
★★**④ 本单不许改既有闸** (`HW/check_netlist_selfconsistency.py` 及其任何一行) ⇒ ★**只许新建 `HW/check_charge_current_live_value.py`** ★
★★**⑤ 零挂链** ⇒ ★**不许把新闸挂进 `state/gate_check.py`** (★挂链是 main 的地界·先例同款: ISS-300/309/312/315/372/379/381/382/383 全同款★) ⇒ ★**`grep -c check_charge_current_live_value state/gate_check.py` 必须 = 0** ★
★★**⑥ 零外发** ⇒ ★**不许发任何邮件/询价/问询/采购 (老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料) ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ⇒ 没有「批一句可以发」这个选项** ★
★★**⑦ 不代拍** ⇒ ★**要 main/老板裁的一律只登记 (分片 needs_from) + 在交卷页写清「要谁回答什么」** ★
★★**⑧ 不自签台账** ⇒ ★**`state/issue_log.yaml` 你一个字节都不许动** (★签收归 main★)★ ★
★★**⑨ 零挂起** ⇒ ★**不许在页里写「等原厂回信 / 等外部确认」⇒ 查不到就 `[0数据]` + 降级方案** ★

---

## ★★四 · 必跑命令 (★rc 实测 · ★全部真实存在 · ★main 本机跑过·你自己也要跑一遍★) ★★

```
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 HW/check_charge_current_live_value.py               # rc=0  新闸裸跑 (已在盘)
python3 HW/check_charge_current_live_value.py --selftest    # rc=0  末行 ALL TESTS PASS
python3 HW/check_netlist_selfconsistency.py                 # rc=0  ★**既有闸·前后读数必须逐字相同★**
python3 state/merge.py                                      # rc=0
python3 state/gate_check.py                                 # rc=0  【Q1 18/18】
python3 state/check_brief_commands.py                        # rc=0
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv HW/check_netlist_selfconsistency.py
git diff --stat -- MECH/hinge_power_calc.json               # ★必须为空 (内容零漂移)★
grep -c check_charge_current_live_value state/gate_check.py   # ★必须 = 0 (零挂链)★
```

★**★基线 (★main 本机实跑 · 交卷后必须逐字相同 · ★别把别人的红当成你的★)★★: ★**`python3 HW/check_netlist_selfconsistency.py` rc=0** ★ · ★**`python3 state/gate_check.py` rc=0 (Q1 18/18)** ★ · ★**`MECH/check_connector_clearance_caliber.py` rc=1 (★那是【基线】·★K7 本来就红 2 条·★前后逐字相同即可·★不是你的锅★)** ★
★**★板指纹 (★零写板 · 开工前后各打一次 · 纳秒级比★)★★: ★**md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · size `4940213`** ★

---

## ★★五 · 交卷消息怎么写 (★上一趟零交卷的就是这个 · ★必须贴数, 不许写「已全部完成」的空话★) ★★

★**① 四件交付物** 路径 + md5 + 大小 (★逐条★) ★
★**② §四 的必跑命令原样输出 + rc** (★一条都不许省·★省一条 = 交卷无效★) ★
★**③ 板 / 网表 / 脚表 / BOM 四项指纹的前后对比** (★零写板 · 零落表的自证★) ★
★**④ 要 main 裁的事 (逐条「要谁回答什么」)** ⇒ ★**上一趟分片里已登记 4 条 (★`iss384_gate_hook_decision` / `iss384_rilim_档位确认` / `iss384_jchg_触点额定` / `iss384_evt_板端实测`★) ⇒ ★**逐条复述 + 补「代价」** ★
★**⑤ 本趟发现的任何缺口** (★包括「上一趟有某件没写全」·★不许糊过去★) ★
★**⑥ 边界自证**: ★**零写板 / 零落表 / 零改既有闸 / 零改既有页面正文 / 零挂链 / 零外发 / 不代拍 / 未自签 issue_log / 没写别人的分片** ★

---

## ★★六 · ★额外纪律 (★派活层附加 · ★逐条都要做到★) ★★

★**① 写分片必须用 `state/frag_write.py` (★禁止 `open(p,"w")`★)** ★
★**② 只写本任务允许的文件, 不碰别人的** (★`SW/` / `MECH/` / `state/fragments/{sw,mech,pm}.yaml` / `state/issue_log.yaml` 一律不许动★) ★
★**③ 证据分级 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` 必须标** ★
★**④ 不许外发任何邮件/询价/问询/采购 (老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料) ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ⇒ 没有「批一句可以发」这个选项** ★
★**⑤ 交卷前跑 `python3 state/merge.py` (rc 必须 0) && `python3 state/gate_check.py` (Q1 必须 18/18) 并把输出贴进回复** ★
★★**⑥ 项目根路径 = `/home/yuewuya/.openclaw/workspace/projects/smart_glasses` (★所有命令都在这里跑★)** ★
★★**⑦ 你这一趟是【独占写会话】** ⇒ ★**同路径写盘不许并发 (★先例: 04:11:42 发生过一次交付页被并发写盘吞掉★) ⇒ 落盘用 `cat >>` / 原子替换, 不要中途写一半的文件** ★
