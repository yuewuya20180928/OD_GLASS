#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
★**cron fb67af40 (ARS45 队列自动派活) · 2026-11-23 18:0x · 新开 ISS-367 (sw-lead) + ISS-368 (mech-lead) 并直接派出** ★

★**为什么新开 (★逐条本机实读·不抄任何 agent 报告★)**:
  ① `python3 state/advance.py --json` ⇒ ★**`internal: []`** ⇒ 三个总工名下**零 `open` 可派** ⇒ 队列真空 ⇒ 不开单就断线 ★
  ② sw-lead 名下 ISS-363 = ★**17:5x 已 verified** (★兄弟 job 775d9893 签收·本机台账实读★) ⇒ ★**槽位真空出来 ⇒ 可派** ★
  ③ mech-lead 名下 ISS-365 = `fixing` (★交卷页在盘 17:23·但兄弟 job 还没签·★**签收归 main/兄弟 job·本 job 不签**★) ⇒ ★**⇒ 本轮【不碰 mech-lead 的 ISS-365】·但 ISS-365 交卷页自己写明「剩下两处仍归 main 派活」⇒ 那是【另一件活】⇒ 本 job 另开 ISS-368 给 mech-lead (★E-9 重算·★纯准备·零写板★)★** ★
  ④ hw-lead 名下 ISS-366 会话**真在飞** (★transcript 17:44:18 仍在写·17:50 实测★) ⇒ ★**本轮不碰 hw-lead** ★
  ⑤ 派活前置闸 `python3 state/check_brief_commands.py --brief-file` ⇒ ★**两份 brief 都 rc=0** ★

★**纪律**: ★**status 直接落 `fixing` ⇒ 无 `open` 窗口 ⇒ 下一轮 in_flight 规则会跳过这两个 agent ⇒ 窗口消失 ⇒ 不与兄弟 job 775d9893 撞车** ★
★**零写板 · 零落表 · 零改既有闸 · 零改既有页面 · 零外发 (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信·本 job 自己也不发★)**
"""
from __future__ import annotations

import fcntl
import os
import shutil
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
DLOG = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
STAMP = "20261123_1800_cronfb67_open_iss367_368"
BRIEF367 = "ISS-367_sw_legb_node_rename_sw_impact.md"
BRIEF368 = "ISS-368_mech_e9_led_band_recalc.md"

B367 = ""  # ★★作废脚本·不再读 brief (★原 ISS-367_sw_legb… 已改名为 ISS-370_sw_legb…★)★★
B368 = ""  # ★★作废脚本·不再读 brief (★原 ISS-368_mech_e9… 已改名并标注 SUPERSEDED★)★★

TITLE367 = (
    "★★[★新主线·PCB 线·SW 侧「腿 B 网表节点具名」对 SW 判据链的影响面·纯分析+作业包+新建闸+沙盒预演·零写板] ★★"
    "【ISS-364 (hw-lead) 已把腿 B 的 200 条指令 (改名 196 + 补行 4) 做成逐条可执行作业包, 并用沙盒证明 C4 158→68 只靠腿 B; "
    "而 main 17:4x~17:5x 本机实跑发现: ★★把腿 B 的网表喂给 SW 侧闸, `SW/tools/timing_check.py` 从 85/85 全过掉到 70/85 (15 条红)★ ★ "
    "⇒ 对照组 (同内容换路径) 85/85 ⇒ 是内容不是路径; 再拆: 只改名 = 14 条红 / 只补行 = 2 条红 (且那 2 条是【落表义务】不是语义破坏) "
    "⇒ 根因 = 腿 B 把节点串从裸位号改成 `ref pinN`, 而 timing_check 的 `resolve_chain_landing()` 判中点网用的是【精确字符串相等】★ "
    "⇒ ⇒ ★★不查清 ⇒ 那一趟开工当天 SW 门禁当场红 ⇒ 要么硬改闸 (把红项调没) 要么板 md5 变第二次 (违「板只改一次」)★★ "
    "⇒ ★★本单 = ① 15 条红逐条表 (红因/归类/修法/自证回绿) ② 「腿 B ⇒ SW 侧必须同批改的活」逐件清单 (照 ISS-323 范本) "
    "③ 一条机器闸 (含「语义红 vs 落表义务红 可分离」判据) + 沙盒三组对照预演 + 一页 + 交卷页 + 分片 + 留证** "
    "★【纯分析 + 作业包 + 新建闸类 · 零写板 · 零落表 · 零改既有闸 · 零改既有页面 · 零外发 · 不代老板拍板】★★"
)

DESC367 = (
    "★**main 2026-11-23 17:4x~17:5x 本机实读 (不抄任何 agent 报告)★** ⇒ "
    "★**① 腿 B 只改两栏**: main 逐格比对 `HW/netlist_v1.csv` vs `tmp/iss364_sbx/netlist_v1_legB.csv` ⇒ ★**196 格改动全在 `node1` (120) + `node2` (76)** · "
    "`net`/`ref`/`value`/`type`/`dnp`/`board`/`footprint` 一格未动 · ★**行数 513 → 517** ★ "
    "★**② ★★三组对照 (★main 本机实跑·★可复跑★)★★**: 基线真网表 = ★**85/85 · rc=0** ★; 对照组 (真内容换路径 `tmp/iss367_sbx/netlist_REAL_copy.csv`) = ★**85/85 · rc=0** ★ "
    "⇒ ★**⇒ 红不是路径造成的** ★; 腿 B 全量 = ★**70/85 · rc=1 · 15 条红** ★ "
    "★**③ 再拆一层 (★把改名与补行分开·★否则只能拿到症状拿不到根因★)★**: 只改名 (196 格·513 行·main 已落 `tmp/iss367_sbx/netlist_v1_rename_only.csv`) = ★**71/85 · 14 红** ★; "
    "只补行 (4 行·0 改名·main 已落 `tmp/iss367_sbx/netlist_v1_rowadd_only.csv`) = ★**73/85 · 2 红** ★ ⇒ ★**那 2 条全是【锚点/行数】类 (落表义务)·不是语义破坏** ★ "
    "★**④ 根因 (★main 读源码定位★)**: `SW/tools/timing_check.py` 的 `resolve_chain_landing()` (★L1013★) 判中点网用 ★**`{node1,node2} == {上臂位号,下臂位号}` 的精确字符串相等** ★ "
    "⇒ 改名后 node1/node2 变成 `R_BAT_DET_1 pin1` / `R_BAT_DET_2 pin1` ⇒ 精确相等不成立 ⇒ 中点网取不到 ⇒ 落点/判决对象/源阻抗/τ 一整串 ADC 判据塌 (★13 条语义红·★4 条是反向用例随正向一起塌★) ★ "
    "★**⑤ 15 条红逐条 (★main 实跑原文·★不是推测★)★**: ADC 源阻抗 37.5k / ADC tau 3.75ms / ADC 12bit 建立 33.8ms / ADC 漏电偏移 37.5mV / "
    "网表锚点 513 数据行 / 网表锚点 md5 ∈ 落表台账登记状态 / F4' 判决对象 = BAT_DET 链 / F4 漏电偏移 2.1% FS / F4 判决源 = SoM 脚表 signal 列 / "
    "F4 ADC 节点 @4.2V = 1.575V / F4D VBUS_DET_D 落点 = J_SOM_P1 pin100 / REV-12 / REV-13 / REV-14 / REV-15 (★四条反向用例★) ★ "
    "★**⑥ 第二处同批必须动的 (★main 实跑★)**: `SW/tools/check_demo_panel_spec.py` 的 R6 在腿 B 网表下红 ⇒ ★**`R6 台账链: 盘上真源 md5 HW/netlist_v1.csv = 724f0bf71cb7 ≠ 台账最新记录 6aee500e60ba`** ★ "
    "⇒ ★**⇒ 腿 B 一落地网表 md5 必变 ⇒ R6 三方对账必红 ⇒ 必须同批【落表 + 重锚】(★那是 hw-lead 的地界·本单只给改法与时序★)★ ★ "
    "★**⑦ negative 结论也要写 (★main 实跑·★沙盒 = 腿 B 网表★)★**: `check_shutdown_semantics.py` rc=0 · `check_sw_ref_reachability_v2.py` rc=0 · "
    "`check_load_switch_selection.py` rc=0 · `check_landing_trace_obligation.py` rc=0 ⇒ ★**这四道不受腿 B 影响** ★ "
    "★**⑧ 已有范本**: `SW/ONETRIP_SW_SAMEBATCH_RENAME_LIST.md` (★ISS-323 · S1 改名那一趟的 7 件必须同批改的活·逐字可执行清单★) ⇒ ★**本单 = 腿 B 那一趟的同款清单★ ★ "
    "★**⑨ 台账**: `SW/SW_MD5_BASELINE_LEDGER.md` (★R6 锚点 + 落表台账链 + H-1 重锚机制★) · `HW/SCHEMATIC_LANDING_V1_LANDED.md` (★落表台账本体★) · "
    "`SW/BOARD_ONEPASS_SW_SYNC.md` (★SW 侧板侧输入收口·§2 8 条逐条表·★只登记不许改正文★) ★ "
    "★**⑩ 沙盒落项目盘 `tmp/iss367_sbx/` (★不许写 /tmp: 2026-11-23 04:4x 实测系统 /tmp 配额已满·写 /tmp 会让闸拿到假读数★)** ★ "
    "★**⇒ 本单只出【纯分析 + 作业包 + 新建闸 + 沙盒预演】, 一个字节都不许写板** ★"
)

NOTE367 = (
    "★2026-11-23 18:00 cron fb67af40 新开并直接派出 (status 落 fixing ⇒ 下一轮 in_flight 规则会跳过 sw-lead ⇒ 窗口消失 ⇒ 不与兄弟 job 775d9893 撞车)★ "
    "★**开单依据**: ① `state/advance.py --json` ⇒ internal=[] (三个总工名下零 open 可派) "
    "② sw-lead 名下 ISS-363 已 verified (17:5x·兄弟 job 签收) ⇒ 槽位空出来 ⇒ 可派 "
    "③ hw-lead 名下 ISS-366 会话真在飞 (transcript 17:44:18 仍在写) ⇒ 本轮不碰 "
    "④ mech-lead 名下 ISS-365 仍是 fixing (交卷页在盘但未签·★签收归 main/兄弟 job·本 job 不签·也不重派它★) ⇒ 本轮给 mech-lead 另开 ISS-368 (E-9 重算·★纯准备类·零写板★) ⇒ 不凑数 "
    "⑤ 派活前置闸 `state/check_brief_commands.py --brief-file` ⇒ ★**本 brief rc=0** ★ "
    "★**任务书全文**: `state/dispatch_briefs/%s` (12,048 B)★ "
    "★**边界**: 零写板 (md5 必须仍 611b869e13518c3c023fb178f91a0075 · mtime 必须仍 2026-11-06 07:07:17.362193413) · "
    "零落表 (网表/脚表/BOM/落表台账/issue_log 一字不改) · 零改既有闸 (timing_check.py / check_demo_panel_spec.py / check_shutdown_semantics.py / "
    "check_sw_ref_reachability_v2.py / check_onepass_sw_sync.py / check_fp_truth_read.py / check_sw_fp_truth_impact.py / gate_check.py / merge.py / frag_write.py 一字不改) · "
    "零改既有页面 (SW/BOARD_ONEPASS_SW_SYNC.md / SW/SW_MD5_BASELINE_LEDGER.md / SW/ONETRIP_SW_SAMEBATCH_RENAME_LIST.md / "
    "HW/PCB/FP_TRUTH_LAND_SWAP_WORKPACKET.md 老字零改动) · 零挂链 · 只写自己的分片 state/fragments/sw.yaml (只走 frag_write.py) · "
    "沙盒只落 tmp/iss367_sbx/ + logs/iss367/ · 不替老板拍板 · 零外发 (老板 2026-11-11 19:31 + 2026-11-12 02:02) · 不自签 issue_log★"
) % BRIEF367

TITLE368 = (
    "★★[★新主线·PCB 线·MECH 侧「E-9 · D_LED_G 换封装后 LED 落位带同趟重算」·纯分析+作业包+新建闸+沙盒重扫·零写板] ★★"
    "【ISS-365 (mech-lead) 已把换官方 land 对 MECH 侧的影响面查清, 并实测挖到真漂移: `D_LED_G` 换官方 0805 后 `led_space` 可落位块数 1992→2183, "
    "两条整高自由带由 X 1.550..3.450 / 72.540..73.660 变成 X 2.225..3.250 / 73.215..74.385 (带 A 宽 −0.875), 且 clearance sweep 由 1992/2016/2031/2075 变成 "
    "2183/2241/2253/2197 ⇒ ★★不再单调 (clr 0.50 的 2197 < clr 0.20 的 2253) ⇒ 必须重扫不能插值★★ "
    "⇒ ★★而这组数现在写在 `MECH/BOARD_ONEPASS_MECH_SYNC.md` 机器块 + `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` 五处, 且【不在任何闸的射程里】★ "
    "⇒ ⇒ ★★ISS-365 交卷页写明「剩下两处仍归 main 派活, 在那一趟换 land 时同一次重算 (E-9)」⇒ 本单 = 把那次重算提前做成【照着就能干的作业包 + 一条机器闸 + 沙盒重扫预演】★★ "
    "⇒ ★★做完本单, 那一趟的 E-9 就变成「照着抄」而不是「到时候再算」⇒ 避免板改到一半才发现 ⇒ 板 md5 变第二次** "
    "★【纯分析 + 作业包 + 新建闸类 · 零写板 · 零落表 · 零改既有闸 · 零改既有页面 · 零外发 · 不代老板拍板】★★"
)

DESC368 = (
    "★**main 2026-11-23 17:4x~17:5x 本机实读 (不抄任何 agent 报告)★** ⇒ "
    "★**① 病灶 (★main 实读 `logs/iss365/led_space_drift.json` 的 BEFORE/AFTER 两段★)**: 可落位块数 ★**1992 → 2183** ★; "
    "整高自由带 ★**X 1.550..3.450 (宽 1.900) + X 72.540..73.660 (宽 1.120)** ★ ⇒ ★**X 2.225..3.250 (宽 1.025) + X 73.215..74.385 (宽 1.170)** ★ "
    "(★带 A 宽 −0.875 · 带 B 宽 +0.050★); clearance sweep ★**1992/2016/2031/2075 → 2183/2241/2253/2197** ★ "
    "★**② ★★两个致命推论 (★main 实算★)★★**: ① 带 A 收窄 0.875 mm 而官方 0805 的 fab 外框比现占位【大 0.70×0.40 mm】⇒ 【窗口变窄 + 器件变大】是同一件事 ⇒ 那一趟必须重排; "
    "② sweep 不再单调 ⇒ 任何「按 clr 线性插值」的写法在换 land 后会算错 ⇒ 必须真重扫 ⇒ 这组数【必须同一次重算】不许「差不多沿用」 ★ "
    "★**③ ★★那组数现在写在哪些地方 (★main 本机 grep 定位·★这是本单的作业面★)★★**: "
    "`MECH/BOARD_ONEPASS_MECH_SYNC.md` 机器块 ★**`full_height_bands` (L301 附近) + `clearance_sweep` (L327~L330) 仍是 BEFORE 旧值** ★; "
    "`MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` ★**L32 / L243 / L289 / L447 / L535 五处** ★ 都写着「整高自由带 X 1.550..3.450 (宽 1.900) + X 72.540..73.660 (宽 1.120)」+「最近落位带 X 6.940..8.250 × Y 63.700..67.900」; "
    "`MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` §3.2 ★**你上一单已按 main 16:55 整改改写过了 (旧 md5 41fe11f2… → 新 8a38ac93…, 对照件 logs/iss365/29b_…txt) ⇒ 本单不许再动** ★ "
    "★**④ 授权依据 (★main 本机读交卷页★)**: ISS-365 交卷页原文 = ★**「剩下两处 (BOARD_ONEPASS_MECH_SYNC.md 机器块的 led.full_height_bands + led.clearance_sweep + BOARD_PORT_OPENING_S6_FRAME_CALIBER.md 的 LED 窗口规格) 仍归 main 派活, 在那一趟换 land 时同一次重算 (E-9)」** ★ "
    "★**⑤ MECH 三道闸现状 (★main 实跑★)**: `check_onepass_struct_crosscheck.py` (N1~N6) · `check_onepass_mech_sync.py` (M1~M5) · `check_board_frame_coords.py` ★**全绿** ★ "
    "⇒ ★**它们读的是当前板 ⇒ 换 land 后会自动重判 ⇒ 本单要做的正是【提前把这个重判算出来】** ★ "
    "★**⑥ 沙坑提醒 (★main 读源码★)**: `MECH/check_onepass_struct_crosscheck.py` ★**没有 `--root`** ★ (★靠 `PROJ = HERE/..`★) ⇒ 沙盒做法 = 把 `MECH/` 整目录 + 板副本 + 它要读的表复制到 `tmp/iss368_sbx/` ⇒ "
    "跑 `tmp/iss368_sbx/MECH/check_onepass_struct_crosscheck.py` ⇒ ★**真闸一个字节不许改 (只改沙盒副本)** ★ "
    "★**⑦ 你上一单的坑 (★必须避开★)**: 上一单因在页里写【全大写 + 位号前缀】形态的库名/封装名, 触发 `MECH/check_mech_ref_reachability.py` 的 C15 而把 `gate_check.py` 拖红 (Q1 15/18) ⇒ "
    "★**新页/新闸不许出现那种形态 (★写法: 「前缀 + 余下」两段写, 或反引号包原名 + 括号里写库★)** ⇒ ★**闸 rc=0 但 `gate_check.py` 红了照样是失败** ★ "
    "★**⑧ 已有资产 (★你直接用·不许重做★)**: `MECH/check_onepass_s10_fp_swap_impact.py` (M0~M7 · `--selftest` 8/8) · `MECH/BOARD_ONEPASS_S10_FP_SWAP_IMPACT.md` (85,675 B) · "
    "`logs/iss365/led_space_drift.json` (★1,001,851 B·★只许脚本抽读·不许整份读进上下文★) · `logs/iss365/compute_iss365.json` (266,340 B) ★ "
    "★**⑨ 老板项 (★只登记不代拍★)**: `D_LED_G` 结构光孔有/无 (U-365-1) · 光孔孔径取决于最终 OPN 镜头 Ø ⇒ `[0数据]` ★ "
    "★**⑩ 沙盒落项目盘 `tmp/iss368_sbx/` (★不许写 /tmp★)** ★ "
    "★**⇒ 本单只出【纯分析 + 作业包 + 新建闸 + 沙盒重扫】, 一个字节都不许写板** ★"
)

NOTE368 = (
    "★2026-11-23 18:00 cron fb67af40 新开并直接派出 (status 落 fixing ⇒ 下一轮 in_flight 规则会跳过 mech-lead ⇒ 窗口消失 ⇒ 不与兄弟 job 775d9893 撞车)★ "
    "★**开单依据**: ① `state/advance.py --json` ⇒ internal=[] (三个总工名下零 open 可派) "
    "② sw-lead 名下 ISS-363 已 verified ⇒ 槽位空出来 ⇒ 同批派 ISS-367 "
    "③ hw-lead 名下 ISS-366 会话真在飞 ⇒ 本轮不碰 "
    "④ ★**mech-lead 名下 ISS-365 仍是 fixing (★交卷页在盘 17:23 但兄弟 job 还没签⇒ 签收归 main/兄弟 job·本 job 不签·也不重派它★) ⇒ 但 ISS-365 交卷页【自己写明】"
    "「剩下两处仍归 main 派活·在那一趟换 land 时同一次重算 (E-9)」⇒ 那是【另一件活·纯准备类】⇒ 本 job 另开 ISS-368 (★**不是重派 ISS-365**★) ⇒ 不凑数★ "
    "⑤ 派活前置闸 `state/check_brief_commands.py --brief-file` ⇒ ★**本 brief rc=0** ★ "
    "★**任务书全文**: `state/dispatch_briefs/%s` (11,112 B)★ "
    "★**边界**: 零写板 (md5 必须仍 611b869e13518c3c023fb178f91a0075 · mtime 必须仍 2026-11-06 07:07:17.362193413) · "
    "零落表 (网表/脚表/BOM/issue_log 一字不改) · 零改既有闸 (check_onepass_struct_crosscheck.py / check_onepass_mech_sync.py / check_board_frame_coords.py / "
    "check_demo_struct_truth.py / check_mech_ref_reachability.py / check_onepass_s10_fp_swap_impact.py / gate_check.py / merge.py / frag_write.py 一字不改) · "
    "零改既有页面 (MECH/BOARD_ONEPASS_MECH_SYNC.md / BOARD_PORT_OPENING_S6_FRAME_CALIBER.md / BOARD_ONEPASS_STRUCT_CROSSCHECK.md (★上一单已改过·不许再动★) / "
    "BOARD_GEOM_30MM.md / HW/PCB/BOARD_ONEPASS_WORKPACKET.md / HW/PCB/BOARD_FRAME_CALIBER.md 老字零改动) · 零挂链 · 只写自己的分片 state/fragments/mech.yaml (只走 frag_write.py) · "
    "沙盒只落 tmp/iss368_sbx/ + logs/iss368/ · 不替老板拍板 (D_LED_G 光孔有/无) · 零外发 (老板 2026-11-11 19:31 + 2026-11-12 02:02) · 不自签 issue_log★"
) % BRIEF368


def atomic_write(path: str, text: str) -> None:
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_", suffix=".yaml")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


NEW = [
    {
        "id": "ISS-367",
        "title": TITLE367,
        "severity": "high",
        "source_blocker": "ISS-364",
        "source_agent": "main",
        "desc": DESC367,
        "owner": "sw-lead",
        "reporter": "main",
        "raised": "2026-11-23",
        "due": "2026-11-25",
        "status": "fixing",
        "external": False,
        "need_keys": [],
        "task_brief": B367,
        "note": NOTE367,
        "dispatched_at": "2026-11-23",
    },
    {
        "id": "ISS-368",
        "title": TITLE368,
        "severity": "high",
        "source_blocker": "ISS-365",
        "source_agent": "main",
        "desc": DESC368,
        "owner": "mech-lead",
        "reporter": "main",
        "raised": "2026-11-23",
        "due": "2026-11-25",
        "status": "fixing",
        "external": False,
        "need_keys": [],
        "task_brief": B368,
        "note": NOTE368,
        "dispatched_at": "2026-11-23",
    },
]


def main() -> int:
    applied = []
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)

        # ★★★【★2026-11-23 18:0x fail-closed 守卫★】★★★
        # ★★本脚本的幂等分支「已存在 ⇒ status→fixing + brief/note 刷新」在 18:0x 真的闯了祸: ★★
        # ★★兄弟 job 775d9893 在同一分钟 (17:5x) 已新开并派出 ISS-367 (mech-lead) + ISS-368 (sw-lead) ★★
        # ★★⇒ 本脚本的幂等分支把兄弟 job 那两条的 task_brief/note【覆盖成了本 job 的版本】★★
        # ★★⇒ 台账指向的任务书与 agent 正在跑的那份对不上 ⇒ 兄弟 job 的签收闸会假红 ⇒ ★★
        # ★★⇒ 已由 `state/_apply_20261123_1805_cronfb67_restore_iss367_368.py` 从备份逐字还原 ★★
        # ★★⇒ 本脚本【已被作废】: 它的 ISS-367/368 全部内容与兄弟 job 撞 ID ⇒ 一律不许再跑 ★★
        # ★★⇒ 保留本文件仅作留痕 (★本项目的 _apply_*.py 一律是历史留档★) ⇒ ★★直接退出, 不写盘 ★★
        print("★★本脚本已作废 (★2026-11-23 18:0x 撞 ID 事故★): ISS-367/368 由兄弟 job 775d9893 在 17:5x 新开并派出, ")
        print("   本脚本的幂等分支曾覆盖它们的 task_brief/note (★已由 _apply_20261123_1805_cronfb67_restore_iss367_368.py 还原★)。")
        print("   ⇒ 本 job 的新发现改用 ISS-370 (见 _apply_20261123_1805_cronfb67_open_iss370.py) ⇒ ★★本脚本一律不许再跑 ★★")
        return 2

        shutil.copy2(LOG, LOG + ".bak_" + STAMP)
        shutil.copy2(DLOG, DLOG + ".bak_" + STAMP)
        applied.append("备份: issue_log.yaml + dispatch_log.yaml")

        log = yaml.safe_load(open(LOG, encoding="utf-8")) or {}
        issues = log.get("issues") or []
        idx = {i.get("id"): i for i in issues}

        for spec in NEW:
            iid = spec["id"]
            if iid in idx:
                it = idx[iid]
                it["status"] = "fixing"
                it["task_brief"] = spec["task_brief"]
                it["note"] = spec["note"]
                applied.append("%s 已存在 ⇒ status→fixing + brief/note 刷新 (幂等)" % iid)
            else:
                issues.append(dict(spec))
                applied.append("新开 %s (%s) · status 直接落 fixing" % (iid, spec["owner"]))

        log["issues"] = issues
        atomic_write(LOG, yaml.safe_dump(log, allow_unicode=True, sort_keys=False, width=10**6))

        dlog = yaml.safe_load(open(DLOG, encoding="utf-8")) or []
        if isinstance(dlog, dict):
            entries = dlog.get("dispatches") or []
            dlog_is_dict = True
        else:
            entries = dlog
            dlog_is_dict = False
        for spec in NEW:
            iid = spec["id"]
            if not any(e.get("issue") == iid for e in entries):
                entries.append({
                    "issue": iid,
                    "agent": spec["owner"],
                    "at": "2026-11-23",
                    "brief": spec["note"],
                    "job": (
                        "cron fb67af40 (ARS45 队列自动派活) · ★派活时刻 2026-11-23 18:00 · "
                        "★**status 全程 fixing ⇒ 无 open 窗口 ⇒ 兄弟 job 775d9893 不会重复派** ★"
                    ),
                })
                applied.append("dispatch_log.yaml += %s %s 1 条" % (iid, spec["owner"]))
        out = dlog
        if dlog_is_dict:
            out["dispatches"] = entries
        else:
            out = entries
        atomic_write(DLOG, yaml.safe_dump(out, allow_unicode=True, sort_keys=False, width=10**6))

    for a in applied:
        print("·", a)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
