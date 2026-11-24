# ISS-386 · cont1 · mech-lead · 把「`J_DEBUG` + `J_UART` 座体/开口/清空区 合一件答」从【三件交付物已在盘 · 但零交卷】做到【独立复核 + 交卷】· 零写板 · 零落表 · 零改已签收件

★**本单 = ISS-386 cont1 (★不是新单 · 不是从零重做 · ★)** ★
★**本单 = 纯分析 + 新建机器闸 + 沙盒预演 (★闸与页已写好 · 本趟只做独立复核与交卷★) · 零写板 · 零落表 · 零改已签收件 · 零外发 · 不代拍** ⇒ 合「板只改一次」纪律 ① ★

---

## ★★一 · 上一趟怎么死的 (★main 本机实读 · 不抄任何 agent 报告★) ★★

★**上一趟 = 2026-11-24 08:28:50 起 · 08:45:36 止 · runtimeMs 993,331 (≈16.6 分钟) · `status=timeout` + `abortedLastRun=true`** ★
★**子会话** `agent:mech-lead:subagent:c8ed675b-e328-498f-8030-f3c86e846b07` / sessionId `b67b595d-4521-4ab3-b4e7-ae54cf523d92` · transcript 628,961 B @08:45:36 · 124 行 · ★**不是空壳 (有大量 tool_use 记录)** ★
★**死因 = 墙 (≈16.6 分钟) 掐在最后一次 `state/merge.py` / `state/gate_check.py` 复跑上 ⇒ ★★三件交付物全部已在盘, 但【交卷消息】没发出来 ⇒ 零交卷★★ ★
★★**⇒ 本趟定位: 【收尾趟】—— 独立复核 + 补缺 + 交卷消息 ⇒ ★★不许重做任何一件交付物★★ ★★**

★★**★上一趟已经在盘的产物 (★main 本机实读 2026-11-24 08:46~08:47 · 你要自己再核一遍★)★★ ★★

| ★产物★ | ★大小 / mtime / md5(前8)★ | ★本趟怎么用★ |
|---|---|---|
| ★`MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md` ★ | 51,765 B @08:37:11 · `3d0c8e7d` ★ | ★**真相页已在盘** ⇒ ★**只许读 + 只许追加式补注 (★正文一字不许删改★)** ★ |
| ★`MECH/check_debug_seat_3d_fit.py` ★ | 60,272 B @08:37:22 · `667e6006` ★ | ★**新闸已在盘** ⇒ ★**只许跑 + 只许修【误报/漏检/崩溃】(★不许放松任何判据★)** ★ |
| ★`HANDOFF/2026-11-24_mech-lead_ISS386_JDEBUG与JUART座体开口清空区合一件答.md` ★ | 24,733 B @08:38:40 · `99d724ed` ★ | ★**交卷页已在盘 (B1~B6 齐全)** ⇒ ★**本趟只追加 B7 (本趟复核段) · ★B1~B6 一字不许改★ ★ |
| ★`state/fragments/mech.yaml` ★ | 731,052 B @08:39:18 · `cc3c1fa8` ★ | ★**分片已写 (走 `state/frag_write.py` 的 `update_fragment` API: artifacts 204→207 · interface_claims 374→383 (+9) · needs_from 166→173 (+7))** ⇒ ★**本趟只在【确有必要】时补, ★不许重复 key★ ★ |
| ★留证 `logs/iss386/` ★ | `gate_run.txt` (4,596 B @08:40) · `gate_selftest.txt` (2,569 B @08:40) · `boundary_selfcheck.txt` (1,838 B @08:37) ★ | ★**闸裸跑 / selftest / 边界自证三份留证已在盘** ⇒ ★**不要重扫·直接引用★ ★ |

★★**★main 本机已复核过的读数 (2026-11-24 08:46~08:47 实跑 · ★你要自己再跑一遍, 别只抄本表★)★★ ★★

```
$ python3 MECH/check_debug_seat_3d_fit.py          ⇒ rc=0
  [ok] K9.3 / K10.1 / K10.2 / K10.3 / K10.4 / KCHAIN  全 ✓
  判据 201 条 · 失败 0 条
  PASS
$ md5sum HW/PCB/demo_mainboard.kicad_pcb   ⇒ 611b869e13518c3c023fb178f91a0075
$ stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb ⇒ 2026-11-06 07:07:17.362193413 · 4940213   (零写板)
$ md5sum HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
  ⇒ 6aee500e… / 9174309d… / 5b999399…  (零落表)
$ python3 state/gate_check.py                ⇒ rc=0  (Q1 18/18 · 钉板闸 10/10 道绿)
```

★★**★main 本机实读到的分片登记 (★7 条 needs · ★要 main 裁的都在里面★)★★: ★**`iss386_oi5_jdebug_clearance_x_pick_one` · `iss386_oi3_juart_landing_dependency` · `iss386_oi2_b33_land_scope` · `iss386_oi11_seat_height_h` · `iss386_oi12_cover_criterion_too_strict` · `iss386_oi13_y_zero_margin` · `iss386_oi14_iss377_dp1_gap`** ★

---

## ★★二 · 本趟的时间预算 (★本项目子会话的真实墙 ★★约 16~17 分钟★★) ★★

★**墙 = 实测 16.6 分钟 (上一趟被掐) ⇒ ★本趟必须按【收尾趟】切★** ★
★**★顺序不许改 (★每一步都落盘★)**:
1. ★**第 1 步 (≤6 分钟) · 独立复核**: 跑下面 §四 的必跑命令 ⇒ ★**把原样输出落 `logs/iss386/cont1_verify.log`** ⇒ ★**逐条对照 §一 的「已在盘」清单 + §一 的「main 已复核读数」⇒ 有任何对不上, 如实写出来 (★不许糊过去★)★ ★
   ★★★**★一条硬约束 (★上一趟就在这一步把时间吃光★)★**: ★**`--selftest` 上一趟跑得很慢 (上一趟 transcript 里它跑了 `timeout 600` 都没完, 后来 `timeout 900` 才拿到结果) ⇒ ★本趟给它【上限 6 分钟】★ ⇒ ★**若 6 分钟内没跑完 ⇒ 不要死磕 ⇒ 直接引用 `logs/iss386/gate_selftest.txt` 的【已在盘留证】+ 在 B7 与交卷消息里如实写明「本趟未重跑 selftest, 引用上一趟留证 (mtime 08:40)」**★ ⇒ ★**不许写「selftest 通过」而不给来源★ ★
2. ★**第 2 步 (≤3 分钟)**: 交卷页 ★**追加** B7 段 (★只追加, ★B1~B6 一字不许改★) ⇒ ★**B7 = 本趟独立复核段: 逐条复核结论 + 必跑命令原样输出 + 板/网表/脚表/BOM 四项指纹前后对比 + 7 条 needs 复述 (逐条「要谁回答什么」) + 本趟发现的任何缺口** ★
3. ★**第 3 步 (≤2 分钟)**: 分片 —— ★**上一趟已写 (frag @08:39:18) ⇒ 本趟默认【零写入】** ⇒ ★**只有在复核发现【真缺一条 need】时才补, 且必须走 `state/frag_write.py`, key 不许重复** ★
4. ★**第 4 步 (★最关键★)**: ★**交卷消息 (★上一趟就是死在这★)** ★

★★**★如果时间在第 2 步用完 ⇒ 允许直接交卷 (B7 可只写前半段) ⇒ ★★但交卷消息【绝对不许省】★★ ★★**

---

## ★★三 · 本单的地界事实 (★不许越★) ★★

★**① 本单的命门是「同源」** —— ★**`J_DEBUG` 与 `J_UART` 必须落在【同一张同源主表】(★两件 × 两档 = 4 行)· 同判据链 · 同 `CRIT`/`TOL` 取法** ⇒ ★**这是本单存在的理由: ★不许分两页 · 不许分两票★** ★
★★**② 落点选择权不在你这里** ⇒ ★**新闸只判「三个候选是否都被判了 + 判定是否自洽」, 不判「哪个候选最好」** ⇒ ★**`J_UART` 三个候选必须【全部】有判决, 不许偷偷挑掉一个** ★
★★**③ 帧依赖必须显式处理** —— 三个候选坐标挂在帧 `B160x100` 上 ⇒ ★**若上位问题落乙, 三个坐标全部作废** ⇒ ★**结论必须写成【与帧无关的形式】, 不许把坐标钉死在 160×100 上** ★
★★**④ `CRIT`/`TOL` 必须从 `MECH/service_port_check.py` 源码读, 不许写死** ★
★★**⑤ 零改已签收件** ⇒ ★**`MECH/BOARD_ONEPASS_CONNECTOR_CLEARANCE_CALIBER.md` / `MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md` / `MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` / `MECH/BOARD_ONEPASS_JDEBUG_ARRANGEMENT_TRUTH.md` / `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` / `MECH/BOARD_ONEPASS_MECH_CLAIMS.md` / `MECH/BOARD_ONEPASS_MECH_SYNC.md` / `HW/PCB/BOARD_ONEPASS_JUART_LAND_FIT.md` + 八个既有闸 ⇒ ★**一个字节都不许动** ★
★★**⑥ 零挂链** ⇒ ★**不许把新闸挂进 `state/gate_check.py`** (★挂链是 main 的地界·先例同款★) ⇒ ★**`grep -c check_debug_seat_3d_fit state/gate_check.py` 必须 = 0** ★
★★**⑦ 零外发** ⇒ ★**不许发任何邮件/询价/问询/采购 (老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料) ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ⇒ 没有「批一句可以发」这个选项** ★
★★**⑧ 不代拍** ⇒ ★**`OI-5` (`J_DEBUG` 清空区 X 宽以哪个数为准) 是 main 的裁决权 ⇒ ★**你只摆三值各自的后果与代价, 不许写「应该用 4.8100」★** ★
★★**⑨ 不自签台账** ⇒ ★**`state/issue_log.yaml` 你一个字节都不许动** (★签收归 main★)★ ★
★★**⑩ 零挂起** ⇒ ★**不许在页里写「等原厂回信 / 等外部确认」⇒ 查不到就 `[0数据]` + 降级方案** ★

---

## ★★四 · 必跑命令 (★rc 实测 · ★全部真实存在 · ★main 本机跑过·你自己也要跑一遍★) ★★

```
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 MECH/check_debug_seat_3d_fit.py                # rc=0  新闸裸跑 (已在盘) · 判据 201 条 · 失败 0 条
python3 MECH/check_debug_seat_3d_fit.py --selftest     # rc=0  末行 ALL TESTS PASS  ★**上限 6 分钟·超时就引用 logs/iss386/gate_selftest.txt 并如实写明★**
python3 MECH/check_onepass_struct_crosscheck.py        # rc=0  ★**既有闸·前后读数必须逐字相同★**
python3 MECH/check_onepass_mech_sync.py                # rc=0  ★**既有闸·前后读数必须逐字相同★**
python3 MECH/check_jdebug_arrangement_truth.py         # rc=0  ★**既有闸·前后读数必须逐字相同★**
python3 MECH/check_jdebug_1p27_clearance.py            # rc=0  ★**既有闸·前后读数必须逐字相同★**
python3 MECH/check_juart_1p27_clearance.py             # rc=0  ★**既有闸·前后读数必须逐字相同★**
python3 MECH/check_board_frame_coords.py --compute     # rc=0  帧坐标机器复算
python3 MECH/check_mech_verdict_freshness.py           # rc=0  ★**既有闸·前后读数必须逐字相同★**
python3 state/merge.py                                 # rc=0
python3 state/gate_check.py                            # rc=0  【Q1 18/18】
python3 state/check_brief_commands.py                   # rc=0
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv MECH/service_port_check.py MECH/check_onepass_struct_crosscheck.py
grep -c check_debug_seat_3d_fit state/gate_check.py   # ★必须 = 0 (零挂链)★
```

★**★基线 (★main 本机实跑 · 交卷后必须逐字相同 · ★别把别人的红当成你的★)★★: ★**`python3 MECH/check_connector_clearance_caliber.py` rc=1 (★那是【基线】·★K7 本来就红 2 条·★前后逐字相同即可·★不是你的锅★)** ★ · ★**其余上面列的既有闸 rc 全 0** ★ · ★**`python3 state/gate_check.py` rc=0 (Q1 18/18)** ★
★**★板指纹 (★零写板 · 开工前后各打一次 · 纳秒级比★)★★: ★**md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · size `4940213`** ★

---

## ★★五 · 交卷消息怎么写 (★上一趟零交卷的就是这个 · ★必须贴数, 不许写「已全部完成」的空话★) ★★

★**① 三件交付物** 路径 + md5 + 大小 (★逐条★) ★
★**② §四 的必跑命令原样输出 + rc** (★一条都不许省·★省一条 = 交卷无效★) ★
★**③ 板 / 网表 / 脚表 / BOM 四项指纹的前后对比** (★零写板 · 零落表的自证★) ★
★**④ 7 条 needs 复述 (逐条「要谁回答什么」)** ⇒ ★**`OI-5` / `OI-2` / `OI-3` / `OI-11` / `OI-12` / `OI-13` / `OI-14` ⇒ ★**不代拍·只登记★ ★
★**⑤ 三条结构侧硬结论复述** (★① `J_DEBUG` 结构件那一趟无论如何都要动 ② 过罩住判据的清空区 X 宽需求 `4.0700`/`6.6100` ③ Y 向零余量★) + ★**一处订正** (★ISS-377 `DP-1` 的 `3.4700` 缺 `0.6000`★) ⇒ ★**这两条是本单唯一的新增事实, 交卷消息里必须点名** ★
★**⑥ 本趟发现的任何缺口** (★包括「上一趟有某件没写全」·★不许糊过去★) ★
★**⑦ 边界自证**: ★**零写板 / 零落表 / 零改已签收件 / 零挂链 / 零外发 / 不代拍 / 未自签 issue_log / 没写别人的分片** ★

---

## ★★六 · ★额外纪律 (★派活层附加 · ★逐条都要做到★) ★★

★**① 写分片必须用 `state/frag_write.py` (★禁止 `open(p,"w")`★)** ★
★**② 只写本任务允许的文件, 不碰别人的** (★`HW/` / `SW/` / `state/fragments/{hw,sw,pm}.yaml` / `state/issue_log.yaml` 一律不许动★) ★
★**③ 证据分级 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` 必须标** ★
★**④ 不许外发任何邮件/询价/问询/采购 (老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料) ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ⇒ 没有「批一句可以发」这个选项** ★
★**⑤ 交卷前跑 `python3 state/merge.py` (rc 必须 0) && `python3 state/gate_check.py` (Q1 必须 18/18) 并把输出贴进回复** ★
★★**⑥ 项目根路径 = `/home/yuewuya/.openclaw/workspace/projects/smart_glasses` (★所有命令都在这里跑★)** ★
★★**⑦ 你这一趟是【独占写会话】** ⇒ ★**同路径写盘不许并发 (★先例: 04:11:42 发生过一次交付页被并发写盘吞掉★) ⇒ 落盘用 `cat >>` / 原子替换, 不要中途写一半的文件** ★
