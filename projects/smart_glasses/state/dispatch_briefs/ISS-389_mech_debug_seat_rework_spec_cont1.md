# ISS-389 · cont1 · mech-lead · 把「两连接器座体/开口/清空区 三件合到一件」从【要求单+闸已在盘 · 交卷页/分片全缺】做到【三件交付物齐全 + 交卷】· 零写板 · 零落表 · 零改既有闸

★**本单 = ISS-389 cont1 (★不是新单 · 不是从零重做 · ★)** ★
★**本单 = 纯分析 + 作业包 + 新建机器闸 + 沙盒预演 · 零写板 · 零落表 · 零改既有闸/既有页面正文 · 零外发 · 不代拍** ⇒ 合「板只改一次」纪律 ① (先派不动板的) ★

★**主线 (★老板 2026-11-17 00:43「接下来的目标是绘制 PCB 图」★)**: ★**本单是 PCB 主线的【结构侧收口层】· 纯分析不动板 ⇒ 属纪律 ①「先派纯分析/作业包类」⇒ 本单【可派】且【不动板】★** ★

---

## ★★一 · 上一趟怎么死的 (★main 本机实读 · 不抄任何 agent 报告★) ★★

★**上一趟 = 2026-11-24 09:45:58 起 · 10:11:09 止 · 墙钟 25.18 分钟** ★
★**子会话** `agent:mech-lead:subagent:c6a0fb40-e81f-41ee-b628-4b811d5970e3` / sessionId `c6a0fb40-e81f-41ee-b628-4b811d5970e3` · transcript 145 行 · 87 次 toolCall ★
★★**★死因 = ★**spawn 时的 `runTimeoutSeconds=1500` (25 分钟) 到点被掐** ★★ (★main 本机实算: 09:45:58 + 1500s = 10:10:58 ≈ 实测 10:11:09 止 ⇒ 逐字对齐 ⇒ ★**不是墙, 是本 job 自己给的上限**★) ★★
★★**★掐死的位置 = 【正在写交卷页的第一步 (★`write` 工具调用的参数里已有交卷页全文, 但写盘动作被掐在半路★)】★** ★★ ⇒ ★**上一趟的最后一条 toolCall 是 `write` 一个交卷页, 之后没有 toolResult ⇒ 交卷页没落盘★** ★★
★★**⇒ 本趟的 spawn 已改成 `runTimeoutSeconds=2400` (40 分钟) ⇒ 本单【不会再被 25 分钟掐死】★★ ★★
★★**★本趟定位: 【收尾趟】—— 要求单 + 新闸【两件都在盘且已跑通】⇒ 只做【交卷页 + 分片 + 交卷消息】⇒ ★★要求单与闸一个字不许重做★ ★★**

### ★★★上一趟已经在盘的产物 (★main 本机实读 2026-11-24 10:4x~10:5x · 你要自己再核一遍★) ★★★

| ★产物★ | ★大小 / mtime / md5(前8)★ | ★本趟怎么用★ |
|---|---|---|
| ★`MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md` ★ | 65,851 B @10:08:14 · `8a56a3eb` ★ | ★**要求单已在盘 (§0~§9 齐全 + 机器块)** ⇒ ★**只许读 + 只许追加式补注 (★正文一字不许删改★)** ★ |
| ★`MECH/check_debug_seat_rework_spec.py` ★ | 47,102 B @10:08:25 · `babadd6b` ★ | ★**新闸已在盘且【已跑通】⇒ 只许跑 + 只许修【误报/漏检/崩溃】(★不许放松任何判据★)** ★ |
| ★`tmp/iss389_sbx/` 沙盒 ★ | `feas.py` / `feas2.py` / `feas2_out.txt` / `probe_apply.py` / `probe/` (33M) / `selftest/` ★ | ★**闸的反向用例沙盒就在这 ⇒ 本趟直接用, 不要重建★** ★ |

★★**★main 本机已复核过的读数 (2026-11-24 10:4x~10:5x 实跑 · ★你要自己再跑一遍, 别只抄本表★)★★ ★★

```
$ python3 MECH/check_debug_seat_rework_spec.py             ⇒ rc=0
    判据 472 条 · 失败 0 条 · PASS
$ python3 MECH/check_debug_seat_rework_spec.py --selftest   ⇒ rc=0
    反向用例 17 条, 通过 17 条 · ALL TESTS PASS   (★实测耗时 ~1.0s★)
$ python3 MECH/check_debug_seat_3d_fit.py                  ⇒ rc=0
$ python3 MECH/check_jdebug_1p27_clearance.py              ⇒ rc=0
$ python3 MECH/check_juart_1p27_clearance.py               ⇒ rc=0
$ python3 MECH/check_jdebug_arrangement_truth.py           ⇒ rc=0  (★--selftest 也是 rc=0 · 10/10 ALL TESTS PASS★)
$ python3 MECH/check_onepass_mech_sync.py                  ⇒ rc=0
$ python3 MECH/check_onepass_struct_crosscheck.py          ⇒ rc=0
$ python3 state/merge.py                                   ⇒ rc=0 (产出 839 | 冲突 0)
$ python3 state/gate_check.py                              ⇒ rc=0 (【Q1】18/18)
$ grep -c check_debug_seat_rework_spec state/gate_check.py ⇒ 0  (★零挂链·挂不挂归 main★)
```

★**★机器块 (要求单 §8.2 的 `json` 代码块) ★★** ★**main 本机实跑 `json.loads` ⇒ rc=0 解析通过** ★ ★**键**: `schema` / `issue` / `agent` / `updated` / `criterion` / `unified_rows` / `clearance_x_tiers` / `rework_items` / `oi_answers` / `gate_chain_impact` / `decisions` / `open_items` ★

★**★一条必须如实报进交卷的事实 (★main 本机实读★)** ★★: ★**`MECH/check_connector_clearance_caliber.py` 裸跑 rc=1 (K7 FAIL) ⇒ ★这是【已知基线红】(★源于 ISS-374 cont2 对已签收页的追加★), 与本单无关 ⇒ ★本单交卷时要把它写成【基线红 · 前后逐字相同 · 不是本单引入】★ ★★

---

## ★★二 · 本趟的时间预算 (★本项目子会话的真实墙 ★★runTimeout 2400s = 40 分钟★★) ★★

★**顺序不许改 (★每一步都落盘★)**:
1. ★**第 1 步 (≤5 分钟) · 独立复核**: 跑下面 §四 的必跑命令 ①②③ ⇒ ★**把原样输出落 `logs/iss389/cont1_verify.log`** ⇒ ★**逐条对照 §一 的「已在盘」清单 ⇒ 有任何对不上, 如实写出来 (★不许糊过去★)★ ★
2. ★**第 2 步 (≤10 分钟) · 交卷页** ★**新建** `HANDOFF/2026-11-24_mech-lead_ISS389_两连接器座体开口清空区收口作业包.md` (★B1~B6 六段齐全 + B6 贴必跑命令原样输出 + rc★) ★
3. ★**第 3 步 (≤4 分钟) · 分片** ⇒ ★**只走 `state/frag_write.py`** (★**禁止 `open(p,"w")` 直接写分片**★) ⇒ ★**产出物 ≥3 + `interface_claims` ≥5 + `needs_from` (`to=main` / `to=boss`)★** ★
4. ★**第 4 步 (★最关键★)**: ★**交卷消息 (★上一趟就是死在这★)** ★

★★**★如果时间在第 2 步用完 ⇒ 允许交卷页先写 B1~B5 (B6 可后补) ⇒ ★★但交卷消息【绝对不许省】★★ ★★**

---

## ★★三 · 本单的地界事实 (★不许越★) ★★

★**① 要求单正文一个字不许删改** —— `MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md` 的 §0~§9 全部在盘且已定稿 ⇒ ★**只许追加式补注 (★追加块要在页尾, 不许插在正文中间★)** ★
★★**② 结构件那一趟的结论已经算清 (本单的核心资产, 不许推翻, 只许补证据)★★ ★★
· ★**`J_DEBUG`**: ★座体必须清空区从 `1.7750` 改到 `6.6100` (X) / `2.5400` 改到 `2.8000` (Y) —— 铜箔每边超出清空区 `1.5175`, 装不进; ★**罩开口 X `10.2000` 一字不动, 罩开口 Y `4.6000` 也不动 (但余量恰好卡在 `CRIT`, 零容差)** ★
· ★**`J_UART`**: ★座体必须清空区从 `2.5400` 改到 `4.0700` (X) / `2.5400` 改到 `2.8000` (Y) —— 中心随落点走 (`17.9650`/`19.0350`/`18.9350`); ★**罩开口 Y `4.6000` 只有在落点 `C1`/`C3` 下才成立, 落点 `C2` 差 `0.2000` 放不下 ⇒ 必须把开口 Y 改到含 `66.1000..70.7000`** ★
· ★**「结构件动不动」**: ★**要动 —— 而且是【两件同批都动】** ⇒ ★**板只改一次的纪律要求: 改件要求单必须在那一趟开工前定死 (★本单 §0/§1/§2/§3/§4 就是那份定死用的单子★)** ★
★★**③ 「答复窗口」是硬约束** —— ★main 已明说: ★**答复窗口 = 板框上位问题的答复窗口, 结构件开模/下单后不可回头** ⇒ ★**你交卷时必须明确写一句: 这 8 条 OI 里, 哪几条结构侧自答了、哪几条留给 main/boss、留给的那几条【答复窗口是哪个】★★ ★
★★**④ 三档返工幅度只给代价, 不给裁决** —— ★**`OI-5` 清空区 X 三档 (`1.7750` / `4.0850` / `4.8100`) 是 main 的裁决权, 你只摆代价账 ⇒ 机器块里要有 `*_decision = not_decided_here` 这类字段** ★
★★**⑤ 「落点裁决已被 ISS-379 挂起」不许重开** —— ★**`J_UART` 落点三选一 (`OI-3`) 归 main, 本单不重复开** ★
★★**⑥ 板只改一次 ⇒ 本单零写板零落表** —— ★**不许碰 `HW/PCB/demo_mainboard.kicad_pcb` / `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv`; 也不许碰 MECH 侧已签收页的正文 (★`MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md` 等★)** ★

---

## ★★四 · 本单要交 3 件 (★三件都要在盘 + 交卷页 B1~B6 齐全★) ★★

### ★★交卷物 (3 件) ★★

1. ★**`MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md`** (★要求单 · ★**已在盘 · 本趟只许追加式补注, 正文一字不许删改**★) ★
2. ★**`MECH/check_debug_seat_rework_spec.py`** (★新闸 · ★**已在盘且已跑通 · 只许跑 + 只许修【误报/漏检/崩溃】· 不许放松任何判据**★) ★
3. ★**`HANDOFF/2026-11-24_mech-lead_ISS389_两连接器座体开口清空区收口作业包.md`** (★★新建★★ 交卷页 · B1~B6) ★

### ★★① 要求单 (★已在盘 · 只许追加式补注★) ★★
★**§0 一句话结论 (三句 · 每件一句 + 结构件动不动一句)** · ★**§1 两件合到一件的【统一口径表】 (★不许分两票★)** · ★**§2 `J_DEBUG` 改件要求单** · ★**§3 `J_UART` 改件要求单** · ★**§4 三档返工幅度代价账 (`OI-5`)** · ★**§5 四条结构侧能自答的 (`OI-2`/`OI-12`/`OI-13`/`OI-14`)** · ★**§6 「那一趟」的闸链影响 (★沙盒预演实测·★不是推的★)** · ★**§7 降级方案 + 待裁项** · ★**§8 复跑命令 + 机器块** · ★**§9 边界自证** ★
★**★本趟只做一件小事**: ★**复核页里每个数还能不能复现出 (★§8.1 的命令逐条能跑 ⇒ 跑一遍, 对不上的在页尾写追加块订正★) ⇒ ★**不许改 §8.2 机器块既有字段的值★ ★**

### ★★② 新闸 `MECH/check_debug_seat_rework_spec.py` (★★已在盘 · 本趟只复核★) ★★
★**零挂链** (★`grep -c check_debug_seat_rework_spec state/gate_check.py` 必须 = 0 · 挂链是 main 的地界★) ★
★**★已实测: 裸跑 rc=0 (判据 472 条 · 失败 0 条 · PASS) · `--selftest` rc=0 (17 条反向用例全过 · ALL TESTS PASS · ~1.0s)★** ★
★**本趟只有两种情况允许改它**: ★**(甲)** 独立复核发现【误报 / 漏检 / 崩溃】⇒ ★**只许修这三类, 一条判据都不许放松** ★**(乙)** 交卷页要新增字段而闸需要读 ⇒ ★**只许【追加】读取, 不许改既有判据逻辑** ★
★**★`--selftest` 必须与环境无关** (★★**沙盒落【项目盘】`tmp/iss389_sbx/selftest/` (★上一趟就是这么做的★), 不许写系统 `/tmp`·不许硬链接·不许 `cp -al`★) ★★

### ★★③ 交卷页 `HANDOFF/2026-11-24_mech-lead_ISS389_两连接器座体开口清空区收口作业包.md` (★★新建★★) ★★
★**B1~B6 六段齐全** (★**闸认这六段, 缺一段就红**★) + ★**B6 必须贴必跑命令的原样输出 + rc** ★
★★**★B1~B6 的标题必须含 gate_check.py 认的关键词 (★本机实读 `state/gate_check.py` 的 `REQUIRED_BLOCKS`★)★★ ★★
| 块 | ★标题里必须出现★ |
|---|---|
| B1 | ★`结论` (或 `结论摘要` / `一句话`) ★ |
| B2 | ★`验收标准自评` (或 `自评` / `验收标准`) ★ |
| B3 | ★`证据分级` (或 `证据等级` / `证据`) ★ |
| B4 | ★`接口取值` (或 `接口声明` / `interface_claims` / `接口请求`) ★ |
| B5 | ★`未决` (或 `卡点` / `阻塞` / `待办`) ★ |
| B6 | ★`复现` (或 `复现命令` / `自证`) ★ |
★★**★命门: `state/gate_check.py` 的 `pick_handoff` 规则 = 「取最新一份交接单评分; 若最新一份自称 B 块结构但缺块 ⇒ 【不许回退】⇒ 真倒退 ⇒ Q1 立刻掉」⇒ ★★你这份一旦自称 B1~B6, 六段就必须真齐全, 不许缺一块★ ★★** ★★
★★**★B5 必须逐条写清「要谁回答什么」★** ★**★本单要交给 main/boss 的 OI 一共 8 条 (★`OI-2`/`OI-3`/`OI-5`/`OI-11`/`OI-12`/`OI-13`/`OI-14` + 座体高定版那一条★) ⇒ ★★每条都要写「要谁回答什么 + 不答的后果 + 答复窗口」★★ ★★**

---

## ★★五 · 分片 ★★
★**只走 `state/frag_write.py`** (★**禁止 `open(p,"w")` 直接写分片**★) ★
★**产出物 ≥3 + `interface_claims` ≥5 + `needs_from` (`to=main` / `to=boss`) ★**
★**★`needs_from` 必须逐条写清「要谁回答什么 + 代价」, 不许只写「请裁决」★** ★
★**★要求单机器块里的 `open_items` 就是本单 needs 的底稿 ⇒ 照抄进 `needs_from` 即可★** ★
★★**坑 (★main 本机实测过的★) ★★**: ★**`state/frag_write.py --add-*` 的分隔符是【空格】不是【分号】** (★`shlex.split()` 切参数 ⇒ 写成 `path=…;summary=…` 会把整串吞进 `path` ⇒ **写出畸形条目却照样打印「✅ 已原子更新」**★) ⇒ ★**写完必须 `grep` 复验条目唯一, 不许只信它打印的那行** ★

---

## ★★六 · ★★本单必跑的坑 (★main 本机实测踩过, 你不要重踩★) ★★

★★**坑 1 ★★ 交卷页的 `write` 动作可能被打断** ⇒ ★**上一趟就死在写交卷页的第一步 ⇒ 本趟【第 2 步就把交卷页整页写完落盘】, 不要先跑一堆命令再写★** ★
★★**坑 2 ★★ `--selftest` 必须与环境无关** (★沙盒落项目盘 `tmp/iss389_sbx/selftest/`, 不许写系统 `/tmp`·不许硬链接·不许 `cp -al`★) ★
★★**坑 3 ★★ `MECH/check_connector_clearance_caliber.py` 裸跑 rc=1 是【已知基线红】** ⇒ ★**交卷时要写成「基线红 · 前后逐字相同 · 不是本单引入」, 不许说成是你改坏的, 也不许为了让它变绿去改它或改基线★ ★
★★**坑 4 ★★ 沙盒已建好** ⇒ ★**`tmp/iss389_sbx/probe/` 已含 `state/fragments/mech.yaml` 副本等依赖 (33M) ⇒ 直接用, 不要重跑 `cp -a` 整棵树★** ★

---

## ★★七 · 必跑命令 (★全部实测存在的真命令 ★· 不许自己编★) ★★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=$PWD/tmp

# ① 命令存在性守卫 (★派活前 main 已跑过 rc=0, 你开工再跑一遍★)
python3 state/check_brief_commands.py

# ② 本单新闸 (★上一趟已写好, 裸跑 + selftest★)
python3 MECH/check_debug_seat_rework_spec.py
python3 MECH/check_debug_seat_rework_spec.py --selftest

# ③ 已签收的相关闸 (★只读对照, 不许改★)
python3 MECH/check_debug_seat_3d_fit.py
python3 MECH/check_debug_seat_3d_fit.py --selftest
python3 MECH/check_jdebug_1p27_clearance.py
python3 MECH/check_jdebug_1p27_clearance.py --selftest
python3 MECH/check_juart_1p27_clearance.py
python3 MECH/check_juart_1p27_clearance.py --selftest
python3 MECH/check_jdebug_arrangement_truth.py
python3 MECH/check_jdebug_arrangement_truth.py --selftest
python3 MECH/check_onepass_mech_sync.py
python3 MECH/check_onepass_struct_crosscheck.py

# ④ 板 / 三表 指纹 (★开工前后各打一次★)
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb

# ⑤ 收尾 (★rc 必须 0 · Q1 必须 18/18★)
python3 state/frag_write.py --agent mech-lead --show
python3 state/merge.py
python3 state/gate_check.py
```

★★**基线 (★main 2026-11-24 10:4x 本机实跑, 你自己再核一遍★)** ★★
```
板 md5 = 611b869e13518c3c023fb178f91a0075 · mtime = 2026-11-06 07:07:17.362193413 · size = 4940213
网表 6aee500e60ba0732f83a9cf557ba90ab · 脚表 9174309df1ec9411ac8e8d9e80ee386a · BOM 5b9993992405904a60ac96a020b375d8
要求单 md5 = 8a56a3eb5a4b1c77e48c283633ec5fe6 · 65,851 B   (★本趟只许追加式补注★)
新闸   md5 = babadd6b073d691374051ea7409a6a1f · 47,102 B   (★本趟只许跑 + 修误报/漏检/崩溃★)
gate_check.py md5 = 5f370bb8cf828473e70ccc5d6412da98 (★不许碰★)
MECH/check_debug_seat_3d_fit.py = 667e6006280cc8c0533d8ce8fa39f8be (★不许碰★)
MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md = 3d0c8e7de86e0f853450dcb7404d9f44 (★不许碰★)
⇒ ★**板 18 天逐字节未动 ⇒ G1 仍开, 不许投板** ★
merge.py ⇒ rc=0 · gate_check.py ⇒ rc=0 · 【Q1】18/18 · 【Q7】钉板 md5 闸链 10/10 道绿
```

---

## ★★八 · 边界自证 (★交卷页里必须有这一段★) ★★

| 边界 | 怎么自证 |
|---|---|
| ★零写板★ | ★板 md5/mtime/size 前后逐字相同★ |
| ★零落表★ | ★网表/脚表/BOM 三件 md5 前后逐字相同★ |
| ★零改既有闸/既有页面正文★ | ★`MECH/check_debug_seat_3d_fit.py` / `MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md` 等 md5 与基线同★ |
| ★零改要求单正文★ | ★要求单只许追加式补注; ★追加前后 §0~§9 正文 md5 与基线同★ |
| ★零挂链★ | ★`grep -c check_debug_seat_rework_spec state/gate_check.py` = 0★ |
| ★零外发★ | ★全程只读本机; ★`state/outbox/` 一个字节未动★ |
| ★不代拍★ | ★★**结构件【动不动】是事实 (已实测), 但【三档选哪个 / 落点选哪个 / 座体高定哪档】是 main/boss 的裁决权 ⇒ ★**你只给代价账与改件要求单, 不写「应采用 X」★★ ⇒ 机器块里要有 `*_decision = not_decided_here` 这类字段★ |
| ★不自签台账★ | ★`state/issue_log.yaml` 你一个字节未动★ |
| ★没写别人的分片★ | ★只写 `state/fragments/mech.yaml`★ |
| ★沙盒纪律★ | ★只落 `tmp/iss389_sbx/` 与 `logs/iss389/`; ★不许写系统 `/tmp`·不许 `cp -al`·不许硬链接★ |
| ★证据分级★ | ★每条结论标五级之一★ |
