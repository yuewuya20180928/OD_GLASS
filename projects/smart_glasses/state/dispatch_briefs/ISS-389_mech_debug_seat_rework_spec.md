# ISS-389 · mech-lead · `J_DEBUG` / `J_UART` 两连接器的**座体 / 开口 / 清空区 三件合到一件**的结构侧**收口作业包** (★纯分析 + 新建闸 · 零写板 · 零落表★)

★**本单性质**: ★**纯分析 + 作业包 + 新建机器闸 + 沙盒预演 · 零写板 · 零落表 · 零改既有闸/既有页面正文 · 零外发 · 不代拍** ⇒ 合「板只改一次」纪律 ① (先派不动板的) ★

---

## ★★一 · 为什么是这一单 (★main 本机实读 · 不抄任何 agent 报告★) ★★

★**① main 已明确下令: 这两件事必须【合到一件】答, 不许分两票★**
★`state/fragments/pm.yaml` 的 need `iss379_q4_mech_opening_and_clearance` (★since 2026-11-24 · to=mech-lead★) 原文:
```
★★**main 提示: 这一条与 J_DEBUG 侧 (ISS-377 算出铜箔每边超清空区 1.5175) 是【同源问题】⇒
★**建议 mech-lead 把两条【合到一件】答 (一次给座体/开口/清空区的整体结论, 而不是分别给两个落点的结论,
★**否则两个连接器的答案可能互相矛盾, 而两个连接器在【同一趟】里改 ⇒ 矛盾就得改第二次 ⇒ 违「板只改一次」★★
★★**时限 (main 硬要求): 「板那一趟」开工前必须答完 ⇒ 因为结构件一旦开模/下单就没法回头**
⇒ ★**答复窗口 = 与板框上位问题 (boss_u1_upper_axis_board_trip_physical_product) 的答复窗口【同一个】★★
```
★**⇒ 本单 = 把这条 need 从「一条待答的 need」变成【一份可交结构件的收口作业包】★**

★**② ISS-386 交卷后, 8 条 OI 挂在 mech 分片上, 至今没人答 (★main 本机实读 `state/fragments/mech.yaml`★)**:
★`iss386_oi5_jdebug_clearance_x_pick_one` (★**清空区 X 宽三档 `1.7750`/`4.0850`/`4.8100` 选哪个**★) · ★`iss386_oi3_juart_landing_dependency` (★J_UART 落点三选一★) · ★`iss386_oi2_b33_land_scope` (★`B33_PIN_LAND_1P27` 含不含 J_UART★) · ★`iss386_oi11_seat_height_h` (★座体真实高 h = `[0数据]` ★) · ★`iss386_oi12_cover_criterion_too_strict` (★⑤ 罩住判据对 THT 排针是否过严★) · ★`iss386_oi13_y_zero_margin` (★Y 向零制造余量接受吗★) · ★`iss386_oi14_iss377_dp1_gap` (★ISS-377 `DP-1` 的 `3.4700` 要不要订正为 `4.0700`★) · ★`iss386_oi15_pad1_displacement_attribution` (★`0.2441` 归属笔误★) ★
★**⇒ ★**这 8 条里有 5 条是【结构侧自己能答的技术题】(OI-2/OI-5/OI-12/OI-13/OI-14), 只有 OI-3(落点)/OI-11(座体高, 归 boss)/OI-15(笔误) 要 main/boss 拍 ⇒ ★**【结构侧能自答的那部分, 现在就该收口, 不要一起拖到老板回信** ★★

★**③ ISS-386 自己已经把最要紧的结论写死了 (★main 本机实读★)**:
★**`J_DEBUG` 的「必须清空区 X 宽」三档算下来【红绿方向完全相同 (全红)】⇒ OI-5 选哪个只改【返工幅度】不改【方向】** ⇒ ★**⇒ `J_DEBUG` 的结构件在那一趟【无论如何都要动】⇒ 【不存在「先只改 J_UART」的省事方案】** ★
★**⇒ ★**所以真正要交给结构侧的不是一个「选择题」, 而是【一份改件要求单】+ 【三档返工幅度的代价账】★ ★

★**④ 结构侧那半还没答完的: ★**「那一趟」的结构件到底怎么改、怎么出件、改完哪几道闸会红★** ★
★**main 本机实读: `MECH/` 与 `HW/PCB/` 下【没有任何一页】叫「改件要求单 / 出件要求单 / 结构件改动清单」** ⇒ ★`(grep -rln "改件要求|出件要求单|改件清单|结构件改动清单" MECH/*.md HW/PCB/*.md ⇒ 0 命中)` ★
★**⇒ ★**⇒ 结构件那一侧现在有的是【判决】(红/绿), 缺的是【改件要求单 + 出件口径 + 闸】★★ ★**

---

## ★★二 · 本单要交 3 件 ★★

1. ★**`MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md`** (★作业包 · 结构件改件要求单★)
2. ★**`MECH/check_debug_seat_rework_spec.py`** (★新闸 · 零挂链★)
3. ★**`HANDOFF/2026-11-24_mech-lead_ISS389_两连接器座体开口清空区收口作业包.md`** (★交卷页 · B1~B6★)

### ★★① 作业包 `MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md` ★★
★**这是本单的主交付物: 一份结构件能直接照着改/出件的要求单** ★
★**§0 一句话结论** (★两件各一句 + 「结构件在那一趟动不动」一句★) ★
★**§1 两件合到一件的【统一口径表】** (★**不许分两票**★) ★
★**§2 `J_DEBUG` 改件要求单** (★逐轴: 现状值 / 那一趟后的值 / 判据来源行号 / 证据等级★) ★
★**§3 `J_UART` 改件要求单** (★同上★) ★
★**§4 三档返工幅度代价账 (OI-5)** (★三档各算一遍, 只给代价不给裁决★) ★
★**§5 `OI-2` / `OI-12` / `OI-13` / `OI-14` 四条【结构侧能自答的】逐条答** (★**只答技术面, 不代 main/boss 拍★★) ★
★**§6 「那一趟」的闸链影响** (★改件完成后, 哪几道既有闸会红 / 哪几道要同批落★) ★
★**§7 降级方案 + 待裁项** (★`to=main` / `to=boss`★) ★
★**§8 复跑命令 + 机器块** ★

★**§1 统一口径表必须有的列**: ★`件` · ★`轴(X/Y/Z)` · ★`现状值` · ★`那一趟后目标值` · ★`余量` · ★`最坏余量 (余量 − TOL)` · ★`CRIT` · ★`红/绿` · ★`判据来源 (页:行)` · ★`证据等级` ★
★★**§2/§3 每条改件要求单必须写清三件事**: ★**① 现状是什么 (页:行 + 实测) ② 那一趟后要变成什么 (具体 mm 数, 不许只写「放大」) ③ 谁改哪一处 (板侧铜箔 / 开口 / 清空区 / 座体选型) ★★ ★★**不许出现「按需放大」这种没有数的说法★ ★★

★★**§4 三档代价账必须逐档给**: ★`清空区 X 宽档` (`1.7750`/`4.0850`/`4.8100`) · ★`单边超出量` (`1.5175`/`0.3625`/`0.0000`) · ★`最坏余量` (`-1.8175`/`-0.6625`/`-0.3000`) · ★`要过判据需的清空区 X 宽` (`6.6100` 三档同) · ★**`结构件总宽增量`** · ★**`三档红绿方向` (全红 ⇒ 选哪档不改方向, 只改返工幅度)** ★

★**★注意 §4 的一处已有事实 (★main 实读, 你要复核★)★**: ★**`6.6100` 比官方 land 自己的 `F.CrtYd` `6.0900` 还大 `0.5200`** ⇒ ★**OI-12「⑤ 罩住判据对 THT 排针是否过严」不是空谈, 是有 `0.5200` 的硬差额** ⇒ ★**你 §5 答 OI-12 时要把这个差额摆出来, 并给「判据该不该改」的两条路 + 各自代价, 不代裁** ★

### ★★② 新闸 `MECH/check_debug_seat_rework_spec.py` ★★
★**零挂链** (★`state/gate_check.py` 命中 = 0★) ★
★**判据建议 (★fail-closed · 每条有反向用例★)**:
- ★**K0** 作业包在盘 + 机器块在盘 + ★**§2/§3 的改件要求单【每条都有具体 mm 数】⇒ 有「按需放大 / 适当加宽 / 视情况」这类无数说法 ⇒ 判红并点名** ★
- ★**K1** ★**本单的命门★**: ★**§1 统一口径表里, `J_DEBUG` 与 `J_UART` 两件的【罩住轴判据方向必须一致】** (★ISS-386 实测: 两件都红 ⇒ **若你的表里出现「一件红一件绿」⇒ 判红并点名是口径没统一, 不许两件分头判**★) ★
- ★**K2** §4 三档必须**三档齐全** (`1.7750`/`4.0850`/`4.8100`) 且每档都有 `单边超出量` + `最坏余量` ⇒ 缺一档判红
- ★**K3** §2/§3 的每个数都要能**回指到判据来源 (页:行)** ⇒ 指不出来的判红
- ★**K4** §5 的四条 (OI-2/OI-12/OI-13/OI-14) 必须逐条有结论 (★**结论可以是「本单不裁, 理由是 X」, 但不许没有条目**★) ⇒ 缺一条判红
- ★**K5** 证据分级白名单 + ★**零挂起措辞** (★语境判据: ★「等原厂回信」/「待外部确认」/「等回复」/「待定」/「pending」等★) ★
- ★**K6** 板三项指纹未动 + 零落表 + ★**零挂链** ★
★**`--selftest` 至少 8 条反向用例**, ★**至少 2 条专打命门**: ★① 把 §1 表里 `J_UART` 的方向改成「绿」⇒ 必须 K1 红 ★② 把 §2 的某个 mm 数换成「按需放大」⇒ 必须 K0 红 ★
★★**★你的新闸自己必须【环境无关】★** (★★**沙盒临时目录放在项目盘 `tmp/` 下, 路径从本闸自己的 `ROOT` 推, 不许依赖系统 `/tmp` 的深度★★) ★★

### ★★③ 交卷页 `HANDOFF/2026-11-24_mech-lead_ISS389_两连接器座体开口清空区收口作业包.md` ★★
★**B1~B6 六段齐全** + ★**B6 贴必跑命令原样输出 + rc** ★

---

## ★★三 · 分片 ★★
★**只走 `state/frag_write.py`** (★禁止 `open(p,"w")`★) ★
★**产出物 ≥3 + `interface_claims` ≥5 + `needs_from` (`to=main` / `to=boss`) ★**

---

## ★★四 · 必跑命令 (★全部实测存在的真命令 · 不许自己编★) ★★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses

# ① 命令存在性守卫
python3 state/check_brief_commands.py

# ② 已签收的相关闸 (★只读对照, 不许改★)
python3 MECH/check_debug_seat_3d_fit.py
python3 MECH/check_debug_seat_3d_fit.py --selftest
python3 MECH/check_jdebug_1p27_clearance.py --selftest
python3 MECH/check_juart_1p27_clearance.py --selftest
python3 MECH/check_jdebug_arrangement_truth.py --selftest
python3 MECH/check_onepass_mech_sync.py
python3 MECH/check_onepass_struct_crosscheck.py

# ③ 本单新闸 (★你自己写的★)
python3 MECH/check_debug_seat_rework_spec.py
python3 MECH/check_debug_seat_rework_spec.py --selftest

# ④ 板 / 三表 指纹 (★开工前后各打一次★)
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb

# ⑤ 收尾 (★rc 必须 0 · Q1 必须 18/18★)
python3 state/frag_write.py --agent mech-lead --show
python3 state/merge.py
python3 state/gate_check.py
```

★★**基线 (★main 2026-11-24 09:1x 本机实跑, 你自己再核一遍★)** ★★
```
板 md5 = 611b869e13518c3c023fb178f91a0075 · mtime = 2026-11-06 07:07:17.362193413 · size = 4940213
⇒ ★**板 18 天逐字节未动 ⇒ G1 仍开, 不许投板** ★
gate_check.py ⇒ rc=0 · 【Q1 交付齐备率】18/18 · 【Q7 钉板 md5 闸链】10/10 道绿
MECH/check_onepass_mech_sync.py ⇒ rc=0 (★M1~M5 全过★)
```

---

## ★★五 · 边界自证 (★交卷页里必须有这一段★) ★★

| 边界 | 怎么自证 |
|---|---|
| ★零写板★ | ★板 md5/mtime/size 前后逐字相同★ |
| ★零落表★ | ★网表/脚表/BOM 三件 md5 前后逐字相同★ |
| ★零改既有闸/既有页面正文★ | ★`MECH/check_debug_seat_3d_fit.py` / `MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md` 等 md5 与基线同★ |
| ★零挂链★ | ★`grep -c check_debug_seat_rework_spec state/gate_check.py` = 0★ |
| ★零外发★ | ★全程只读本机; ★`state/outbox/` 一个字节未动★ |
| ★不代拍★ | ★★**结构件【动不动】是事实 (已实测), 但【三档选哪个 / 落点选哪个 / 座体高定哪档】是 main/boss 的裁决权 ⇒ ★**你只给代价账与改件要求单, 不写「应采用 X」★★ ⇒ 机器块里要有 `*_decision = not_decided_here` 这类字段★ |
| ★不自签台账★ | ★`state/issue_log.yaml` 你一个字节未动★ |
| ★没写别人的分片★ | ★只写 `state/fragments/mech.yaml`★ |
| ★证据分级★ | ★每条结论标五级之一★ |

★★**★你交卷时必须明确写一句: ★**这 8 条 OI 里, 哪几条结构侧自答了、哪几条留给 main/boss、留给的那几条【答复窗口是哪个**★★ (★★**main 已明说: 答复窗口 = 板框上位问题的答复窗口, 结构件开模/下单后不可回头**★★) ★★
