#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
moli (项目总工) 2026-11-23 17:5x · job 775d9893「ARS45 继续执行后继计划」
★开 ISS-367 (mech-lead · E-9 LED 窗口规格同趟重算) + ISS-368 (sw-lead · SW09 三处同批落地补丁)
  + ISS-369 (hw-lead · 板面库封装名写盘作业包 · ★★落 open 状态排队, 不派★) ★
=========================================================================================
★**为什么这一组现在必须存在 (★main 17:5x 本机实读 · 不抄任何 agent 报告★)**:
  · ★**17:5x 本轮 main 自建签收闸 `state/_apply_20260723_1750_cron775d_sign_iss363_364.py` (fail-closed) 把 ISS-363 / ISS-364 签成 verified,
    并用预置闸把 ISS-365 签成 verified ⇒ 三个总工的槽位第一次【同时】空出来** ⇒ ★**不填 ⇒ 队列真空 ⇒ 下一轮 advance.py 又是 internal=0** ★
  · ★**ISS-365 (mech-lead) 交卷页点名「E-9 剩下两处仍归 main 派活」** ⇒ `MECH/BOARD_ONEPASS_MECH_SYNC.md` 机器块 + `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` 的 LED 窗口规格
  · ★**ISS-363 (sw-lead) 交卷页 + main 16:58 裁决** ⇒ 第 9 条「加」但【三处同批落地】= main 一键动作 ⇒ 缺一个【可执行幂等补丁 + 副本 dry-run 证明】
  · ★**ISS-361 / ISS-363 / ISS-364 三单合起来指向同一条最贵的缺口**: ★**板面 186 个封装的库名 0/186 全空** ⇒ 「换官方 land」这一跳【写不进 lib_id】
    ⇒ ★**它是 S10 那一跳的报废风险, 至今无人认领** ⇒ 本轮开给 hw-lead (★但 hw-lead 此刻正在跑 ISS-366 ⇒ 本单只落 open 排队, 下一轮 advance.py 自然派它★)
★**为什么这三单都属于「板只改一次」纪律允许的活**: ★**全是【纯分析 / 作业包 / 闸 / 文档定点改写】类** ——
  ★**没有一单写板、没有一单落表 (网表真源)、没有一单动布局或布线** ⇒ ★**真动板那一趟仍然是一次做完** ★
★**边界**: ★**只写 `state/issue_log.yaml` + `state/dispatch_log.yaml` 两个文件** (★老条目一字未删·追加式★
  ⇒ 不碰板 / 网表 / 脚表 / BOM / 任何分片 / PROJECT_TRACKER.md §0 / DECISIONS / outbox ★
"""
import fcntl
import os
import shutil
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
DLOG = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
STAMP = "20260723_1755_cron775d_open_iss367_368_369"

TITLE367 = (
    "★★[★新主线·PCB 线·MECH 侧·「板那一趟」S10 换官方 0805 后的【LED 窗口规格同趟重算】·纯文档定点改写+新建闸+沙盒重算·零写板·零落表] ★★"
    "【ISS-365 (mech-lead) 交卷实测: `D_LED_G` 换官方 0805 后 `led_space` 铜箔相对原点偏移变 ⇒ 两条可放行带 + 可落位块数全变 "
    "(1992→2183, 带 A 宽 −0.875), 且 sweep 不再单调 (clr=0.5 的 2197 < clr=0.2 的 2253) ⇒ 既有页 "
    "`MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` §3.2 那句「块数不变」的后半句【作废】, 必须同趟重算 "
    "⇒ ★★ISS-365 交卷页明写「E-9 剩下两处 (MECH_SYNC 机器块 + BOARD_PORT_OPENING_S6_FRAME_CALIBER 的 LED 窗口规格) 仍归 main 派活」★★】★★ "
    "⇒ ★★本单 = ① 一页 (漂移本体 + 两处逐字改法 + 同趟重算清单) ② 一条机器闸 (L0~L6·判内容不判 md5·selftest ≥6/6) "
    "③ 交卷页 + 分片 + 留证★ "
    "★★【纯文档定点改写 + 新建闸 + 沙盒重算类 · 零写板 · 零落表 · 零改既有闸 · 零外发 · 不代老板拍板】★★"
)

DESC367 = (
    "★2026-11-23 17:5x main 本机实读 · 全部数字可复跑 · 不抄任何 agent 报告★\n"
    "★**① main 已独立复核过的三个数 (只认这三个, 其余自己重算)**: 可落位块数 **1992 → 2183 (+191)** · "
    "两条整高自由带 X **1.550..3.450 / 72.540..73.660 → 2.225..3.250 / 73.215..74.385** (带 A 宽 **−0.875**) · "
    "clr sweep **1992/2016/2031/2075 → 2183/2241/2253/2197 ⇒ 非单调**\n"
    "★**② 为什么必须现在做**: 「板只改一次」那一趟开工当天, 若这两处仍按旧口径 ⇒ 那一趟按旧数布局 ⇒ LED 落位超框 / 结构件装不下 "
    "⇒ 板 md5 第二次变 ⇒ 整趟白跑 ⇒ ★**这是【板那一趟之前必须收口的前置件】**\n"
    "★**③ main 的定点改写授权**: 只许改 `MECH/BOARD_ONEPASS_MECH_SYNC.md` 里与 `D_LED_G`/`led_space`/可放行带/块数有关的那几行 + 机器块对应字段, "
    "以及 `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` 里 LED 窗口规格那几行 ⇒ 其余老字逐字节不许动 ⇒ 改前 md5 + 逐行 diff + 一键回滚说明 都要留证\n"
    "★**④ 不许改**: `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` (ISS-365 那一轮已改过 §3.2) · 既有 4 道 MECH 闸 · `state/gate_check.py` · `state/merge.py` · `state/frag_write.py`\n"
    "★**⑤ 老板项只登记不代拍**: `D_LED_G` 结构光孔有/无 (U-365-3) · 5 只按键 3N vs 1.5N\n"
    "★**⑥ 签收前置**: 交卷前请自己先跑 `python3 state/gate_check.py` 看 Q1 是不是 18/18 "
    "(★不是 18/18 ⇒ 先在交卷页写明, 别自己背这个锅★)"
)

TITLE368 = (
    "★★[★新主线·PCB 线·SW 侧·「板那一趟」SW09 清单第 9 条的【三处同批落地】补丁·纯作业包+沙盒 dry-run+新建闸·零写板·零落表] ★★"
    "【main 2026-11-23 16:58 已裁: 「加第 9 条」= 加, 但必须三处同批落地 (① `SW/BOARD_ONEPASS_SW_SYNC.md` 的 §2 表 + §2.1 分布表 + §6 JSON 块 "
    "② `SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md` 的 H4-REG 三数字 8→9/0→1/4→新值 ③ 本单新闸 `SW/tools/check_fp_truth_read.py`); "
    "★**真件落地 = main 的一键动作 (落表批次地界)** ⇒ 本单只交【幂等补丁 + 副本 dry-run 证明 + 回滚说明】· 真件零改★ "
    "⇒ ★★「板只改一次」那一趟 (S1~S13) 会【合法地】把三份真源的 md5 一起换掉 ⇒ 若三处不同批落地 ⇒ 清单页说 9 条 / ISS-362 页说 8 条 / 闸按 8 条判 "
    "⇒ 那一趟当天必然「清单与闸互相打脸」⇒ 最坏是有人为让闸绿去改锚点/改判据 (★正是 ISS-273/275/284 堵掉的漏洞★)★★】★★ "
    "⇒ ★★本单 = ① 一页 (三处逐字规格 + 幂等性 + dry-run 证明 + 回滚) ② 幂等补丁脚本 (★默认干跑·只许写副本★) + 一条机器闸 (selftest ≥6/6) "
    "③ 交卷页 + 分片 + 留证★ "
    "★★【纯作业包 + 沙盒 dry-run + 新建闸类 · 零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 · 零外发 · 不代老板拍板】★★"
)

DESC368 = (
    "★2026-11-23 16:58 main 裁决 (原文在 `state/fragments/pm.yaml` 的 answer `iss363_b5_1_checklist_ninth_item_verdict_20261123` 等 4 条) + 17:5x 本机实读★\n"
    "★**① 裁决四条**: ① 第 9 条 = **加** (三处同批落地·真件落地归 main) ② 新闸 = **加** (★交脚本·挂不挂链 = main 的机制地界★) "
    "③ 9 条过期 need 的正文 = **不改** (★改用机器闸 F3 判「open need 引着的 md5 == 落表台账链头」★) ④ 锚点副本跟到 ISS-302 链头 = **跟**, "
    "★但走合法换源通道 (落 decision + 留痕)· 不许手改 md5 ⇒ ISS-363 零改那个文件★\n"
    "★**② 本单要交的**: 三处落点的**唯一锚点 + 原文 + 新文 + 改完自证**; 一个**默认干跑**的幂等补丁脚本 (★只有显式 `--apply` 才写·且只许写副本目录★); "
    "副本上跑第二遍 **diff = 0** 的幂等证明; 「只改一处 ⇒ H4 红 + F4 红」的反证; 逐字节反向补丁 + 回滚命令\n"
    "★**③ 真件三处零改**: `SW/BOARD_ONEPASS_SW_SYNC.md` · `SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md` · `SW/tools/check_fp_truth_read.py` 一字不许改 "
    "⇒ dry-run 一律在项目盘 `tmp/` 的副本上做\n"
    "★**④ 零挂链**: 本单的新闸也不挂 `state/gate_check.py` / `SW/tools/check_onepass_sw_release.py`\n"
    "★**⑤ 签收前置**: 交卷前请自己先跑 `python3 state/gate_check.py` 看 Q1 是不是 18/18 (★不是 18/18 ⇒ 先在交卷页写明★)"
)

TITLE369 = (
    "★★[★新主线·PCB 线·HW 侧·「板那一趟」S10 的【板面库封装名 0/186 全空】写盘作业包·纯作业包+沙盒+新建闸·零写板·零落表] ★★"
    "【ISS-361 实测: 板面 186 个封装 · 库名 (`GetFPIDAsString()`) 唯一值 = `''` ⇒ 板是【自绘通用占位】; "
    "ISS-363 交卷: 「板面 186 个封装库封装名 0/186 非空 ⇒ S10 那一跳必须先把『板面补库封装名』排进板那一趟」; "
    "ISS-364 交卷: 90 件换封装作业包 (§1 每件 12 字段: 目标 lib:name + .kicad_mod 路径 + md5 + 几何 Δ) 已在盘; "
    "★**main 独立重算 (真闸代码): 真网表 C4 = 158 ⇒ 腿 B 后 C4 = 68 ⇒ 四桶 TP42/DNP26/靶内77/缺口13 = 158 ⇒ 腿 A (换官方 land) 对 C4 贡献实测为 0**★ "
    "⇒ ★★「换封装」与「补库封装名」是同一件事的两半: 缺任一半, 那一趟都交不出可投产的板 (装配厂拿不到正确封装 + BOM 与板面对不上 + 板 md5 第二次变)★★】★★ "
    "⇒ ★★本单 = ① 一页 (板面现状 + 本机 KiCad 写盘机制实测 + 90+96 件目标清单 + 「写库名不改语义」的判定) "
    "② 沙盒 (副本上换 land + 写 lib_id ⇒ 真闸 C1~C4 ⇒ C4 仍 158) + 一条几何闸 (selftest ≥6/6) ③ 交卷页 + 分片 + 留证★ "
    "★★【纯作业包 + 沙盒 + 新建闸类 · 零写板 · 零落表 · 零改既有闸 · 零改既有页面 · 零外发 · 不代老板拍板】★★"
)

DESC369 = (
    "★2026-11-23 17:5x main 本机实读 (ISS-361 / ISS-363 / ISS-364 交卷 + main 独立重算)★\n"
    "★**① 病灶**: 板面 186 个封装库名全空 ⇒ 换官方 land 时【写不进 lib_id】⇒ 装配/贴片拿不到正确封装 ⇒ BOM 与板面对不上 ⇒ C1/C3 在那一趟会红 ⇒ 板 md5 第二次变\n"
    "★**② 已知输入**: ISS-364 的 90 件作业包 `HW/PCB/FP_TRUTH_LAND_SWAP_WORKPACKET.md` §1 (★你要自己复核, 不许照抄★) · ISS-361 的四桶分解\n"
    "★**③ 本单要证明的一件事**: ★**写库名不改变电气语义** ⇒ 沙盒上换 land + 写 lib_id ⇒ 用真闸 `state/check_pcb_nets.py` 跑 C1~C4 ⇒ C4 仍 158 ⇒ 可复跑★\n"
    "★**④ 纪律**: 换 land 只许在 `tmp/` 副本上做; 真板零写; 网表/脚表/BOM 真源零改; 既有闸与既有页面零改; 新闸零挂链\n"
    "★**⑤ 老板项只登记不代拍**: `D_ESD_USB_D` 2 脚 vs 3 脚 (W-1/W-2) · 5 只按键 3N vs 1.5N · `C_VBUS_GND` 留位还是下板\n"
    "★**⑥ 本单此刻【不派】**: hw-lead 正在跑 ISS-366 (★一个 agent 同时只有一个写会话★) ⇒ 本单只落 `open` 排队 ⇒ 下一轮 `advance.py` 自然派它\n"
)

BRIEF367 = (
    "★**任务书全文**: `state/dispatch_briefs/ISS-367_mech_s10_led_spec_sync.md` (5,394 B)★\n"
    "★**题**: ★**把「换官方 0805」这一跳在【结构侧】留下的两处未收口项 (MECH_SYNC 机器块 + LED 窗口规格) 做成【同趟重算 + 定点改写 + 一条机器闸】** ★★\n"
    "★**类别**: ★**纯文档定点改写 + 新建闸 + 沙盒重算 · 零写板 · 零落表 · 零改既有闸 · 零外发 · 不代老板拍板** ★★\n"
    "★**main 已独立复核过的三个数 (★只认这三个·其余自己重算★)**: ★**可落位块数 1992 → 2183 (+191)** · "
    "★**两条整高自由带 X 1.550..3.450 / 72.540..73.660 → 2.225..3.250 / 73.215..74.385 (带 A 宽 −0.875)** · "
    "★**clr sweep 1992/2016/2031/2075 → 2183/2241/2253/2197 ⇒ 非单调** ★\n"
    "★**定点改写授权 (★只有这两处·其余老字一字不许动★)**: ① `MECH/BOARD_ONEPASS_MECH_SYNC.md` 里与 `D_LED_G`/`led_space`/可放行带/块数有关的那几行 + 机器块对应字段 "
    "② `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` 里 LED 窗口规格那几行 ⇒ ★**改前 md5 + 改后逐行 diff + 一键回滚说明都要留证**★\n"
    "★**不许改**: `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` (★ISS-365 已改过 §3.2★) · 既有 4 道 MECH 闸 · `state/gate_check.py` · `state/merge.py` · `state/frag_write.py`★\n"
    "★**★新建 (★这三个路径本单才存在·别去别处找★)**: ★**`MECH/BOARD_ONEPASS_S10_LED_SPEC_SYNC.md`** · "
    "★**`MECH/check_onepass_s10_led_spec_sync.py`** · ★**`HANDOFF/2026-11-23_mech-lead_ISS367_S10换封装LED窗口规格同趟重算.md`**★\n"
    "★**零写板** (★板 md5 必须仍 `611b869e13518c3c023fb178f91a0075` · mtime 必须仍 `2026-11-06 07:07:17.362193413`★) · "
    "★**零落表** (★`HW/netlist_v1.csv` · `HW/netlist_v1_pins.csv` · `HW/BOM_v1.csv` · 原理图 · `state/issue_log.yaml` 一字不改★) · "
    "★**零外发** (★老板 2026-11-11 19:31 + 2026-11-12 02:02★) · ★**不代老板拍板** (★`D_LED_G` 光孔有/无 = 老板项 U-365-3 · 只登记代价★) · "
    "★**只写 `state/fragments/mech.yaml`** (★只走 `state/frag_write.py`★) · ★**不改 `PROJECT_TRACKER.md` §0** ★\n"
    "★**必跑命令**: `python3 MECH/check_onepass_s10_fp_swap_impact.py` · `python3 MECH/check_onepass_mech_sync.py` · "
    "`python3 MECH/check_onepass_struct_crosscheck.py` · `python3 MECH/check_board_frame_coords.py` · `python3 MECH/check_demo_struct_truth.py` · "
    "★**`python3 MECH/check_onepass_s10_led_spec_sync.py`** (★本单新建★) · ★**`python3 MECH/check_onepass_s10_led_spec_sync.py --selftest`** · "
    "`python3 state/merge.py` · `python3 state/gate_check.py` · `python3 state/frag_write.py --agent mech-lead --show` · "
    "`md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv` · `stat -c '%y' HW/PCB/demo_mainboard.kicad_pcb`★\n"
    "★**验收线 (★20 条·main 会自己复跑·不采信你的自述★)**: ① 页存在且非空 ② 四个数与脚本实算一致 ③ sweep 非单调被显式承认 "
    "④ MECH_SYNC 机器块与页一致 ⑤ 证据等级全在五级白名单 ⑥ 正文零挂起措辞 ⑦ 新闸 rc=0 ⑧ `--selftest` ≥6/6 且每条自证「只红目标那条」 "
    "⑨ 沙盒在项目盘 `tmp/` ⑩ 两处定点改写之外老字逐字节未变 ⑪ `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` 逐字节未变 ⑫ 既有闸脚本一个字节未改 "
    "⑬ 板 md5/mtime 逐字节未变 ⑭ 网表/脚表/BOM md5 逐字节未变 ⑮ `merge.py` rc=0 且 `gate_check.py` rc=0 (★Q1 = 18/18★) "
    "⑯ 既有 4 道 MECH 闸读完仍全 rc=0 ⑰ 分片写入只走 `state/frag_write.py` ⑱ 交卷页 B1~B6 齐全 ⑲ `logs/iss367/` 留证在盘 (≥ 10 件) "
    "⑳ 一键回滚说明在盘 (★改前/改后原文 + 回滚命令★) ★\n"
    "★**收工后按老规矩回卷**: ★**交卷摘要 + 必跑命令的 rc + 三件交付物路径 + 边界自证 + 要 main 裁的事 (逐条写清「要谁回答什么」)★ ★"
)

BRIEF368 = (
    "★**任务书全文**: `state/dispatch_briefs/ISS-368_sw_sw09_三处同批落地补丁.md` (5,119 B)★\n"
    "★**题**: ★**把「板那一趟」SW 侧清单第 9 条 (SW09_FP_TRUTH_READ) 的【三处同批落地】做成【幂等补丁脚本 + 副本 dry-run 证明 + 回滚说明】** ★★\n"
    "★**类别**: ★**纯作业包 + 沙盒 dry-run + 新建闸 · 零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 · 零外发 · 不代老板拍板** ★★\n"
    "★**main 16:58 已裁的四条**: ① 第 9 条 = **加** (三处同批落地·★真件落地 = main 的一键动作★) ② 新闸 = **加** (★挂不挂链 = main 的机制地界★) "
    "③ 9 条过期 need 正文 = **不改** (★改用机器闸 F3 判「open need 引的 md5 == 落表台账链头」★) ④ 锚点副本跟到 ISS-302 链头 = **跟** "
    "(★走合法换源通道·不许手改 md5★) ★\n"
    "★**★新建 (★这三个路径本单才存在·别去别处找★)**: ★**`SW/BOARD_ONEPASS_SW09_LANDING_PATCH.md`** · "
    "★**`SW/tools/apply_sw09_three_place_patch.py`** · ★**`SW/tools/check_sw09_patch_dryrun.py`** · "
    "★**`HANDOFF/2026-11-23_sw-lead_ISS368_SW09三处同批落地补丁.md`**★\n"
    "★**★真件三处零改 (★本单只交补丁·dry-run 一律在项目盘 `tmp/` 的副本上做★)**: ★**`SW/BOARD_ONEPASS_SW_SYNC.md` · "
    "★**`SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md` · `SW/tools/check_fp_truth_read.py` 一字不许改** ★\n"
    "★**零写板** (★板 md5 必须仍 `611b869e13518c3c023fb178f91a0075` · mtime 必须仍 `2026-11-06 07:07:17.362193413`★) · "
    "★**零落表** (★`HW/netlist_v1.csv` · `HW/netlist_v1_pins.csv` · `HW/BOM_v1.csv` · `SW/SW_MD5_BASELINE_LEDGER.md` · `state/issue_log.yaml` 一字不改★) · "
    "★**零改既有闸** (★`SW/tools/check_onepass_sw_sync.py` · `SW/tools/check_sw_fp_truth_impact.py` · `SW/tools/check_onepass_sw_release.py` · "
    "★`state/gate_check.py` · `state/merge.py` · `state/frag_write.py`★) · ★**零挂链** (★本单新闸也不挂★) · ★**零外发** · ★**不代老板拍板** · "
    "★**只写 `state/fragments/sw.yaml`** (★只走 `state/frag_write.py`★) · ★**不改 `PROJECT_TRACKER.md` §0** ★\n"
    "★**必跑命令**: `python3 SW/tools/check_fp_truth_read.py` · `python3 SW/tools/check_fp_truth_read.py --selftest` · "
    "`python3 SW/tools/check_sw_fp_truth_impact.py` · `python3 SW/tools/check_onepass_sw_sync.py` · `python3 SW/tools/check_onepass_sw_release.py` · "
    "★**`python3 SW/tools/apply_sw09_three_place_patch.py --dry-run`** · ★**`python3 SW/tools/check_sw09_patch_dryrun.py`** (★本单新建★) · "
    "★**`python3 SW/tools/check_sw09_patch_dryrun.py --selftest`** · `python3 state/merge.py` · `python3 state/gate_check.py` · "
    "`python3 state/frag_write.py --agent sw-lead --show` · "
    "`md5sum HW/PCB/demo_mainboard.kicad_pcb SW/BOARD_ONEPASS_SW_SYNC.md SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md SW/SW_MD5_BASELINE_LEDGER.md`★\n"
    "★**验收线 (★20 条·main 会自己复跑·不采信你的自述★)**: ① 页存在且非空 ② 三处落点各给「定位串 + 原文 + 新文 + 自证」 ③ 补丁脚本默认干跑·写不进真件 "
    "④ 干跑两次 diff = 0 ⑤ 副本上三处同批落地后 10 道 SW 闸全绿 ⑥ 新闸 F1~F7 全绿 ⑦ 反证「只改一处 ⇒ H4 红 + F4 红」成立 ⑧ 新闸 rc=0 "
    "⑨ `--selftest` ≥6/6 且每条自证「只红目标那条」 ⑩ 沙盒在项目盘 `tmp/` ⑪ 真件三处逐字节未变 ⑫ 板 md5/mtime 逐字节未变 "
    "⑬ 网表/脚表/BOM/锚点台账 md5 逐字节未变 ⑭ 既有闸脚本一个字节未改 ⑮ `merge.py` rc=0 且 `gate_check.py` rc=0 (★Q1 = 18/18★) "
    "⑯ 证据等级全在五级白名单 ⑰ 正文零挂起措辞 ⑱ 分片写入只走 `state/frag_write.py` ⑲ 交卷页 B1~B6 齐全 + `logs/iss368/` 留证在盘 (≥ 10 件) "
    "⑳ 回滚说明 + 反向补丁在盘 ★\n"
    "★**收工后按老规矩回卷**: ★**交卷摘要 + 必跑命令的 rc + 三件交付物路径 + 边界自证 + 要 main 裁的事 (逐条写清「要谁回答什么」)★ ★"
)

BRIEF369 = (
    "★**任务书全文**: `state/dispatch_briefs/ISS-369_hw_fp_libid_truth.md` (5,430 B)★\n"
    "★**题**: ★**把「板面 186 个封装的库名 0/186 全空」这条【S10 那一跳的报废风险】做成【写盘作业包 + 沙盒可达性证明 + 一条几何闸】** ★★\n"
    "★**类别**: ★**纯作业包 + 沙盒 + 新建闸 · 零写板 · 零落表 · 零改既有闸 · 零改既有页面 · 零外发 · 不代老板拍板** ★★\n"
    "★**★新建 (★这两个路径本单才存在·别去别处找★)**: ★**`HW/PCB/FP_LIBID_TRUTH_WORKPACKET.md`** · "
    "★**`HW/check_fp_libid_truth.py`** · ★**`HANDOFF/2026-11-23_hw-lead_ISS369_板面库封装名写盘作业包.md`**★\n"
    "★**★主线口径**: ★**板只改一次 ⇒ 真动板那一趟必须一次做完** ⇒ 本单属【纯作业包/沙盒/闸】类·★不动板★ ★\n"
    "★**边界**: ★**零写板** (★板 md5 必须仍 `611b869e13518c3c023fb178f91a0075` · mtime 必须仍 `2026-11-06 07:07:17.362193413` · "
    "★**换 land 只许在 `tmp/` 的副本上做**★) · ★**零落表** (★`HW/netlist_v1.csv` · `HW/netlist_v1_pins.csv` · `HW/BOM_v1.csv` · 原理图 · "
    "★`state/issue_log.yaml` 一字不改★) · ★**零改既有闸** (★`HW/check_fp_truth_baseline.py` · `HW/check_fp_truth_coverage_gap.py` · "
    "★`HW/check_fp_truth_land_swap.py` · `HW/check_onepass_preflight_coverage.py` · `HW/check_onepass_s10_manifest.py` · `state/check_pcb_nets.py` · "
    "★`state/gate_check.py` · `state/merge.py` · `state/frag_write.py`★) · ★**零改既有页面** (★`HW/FP_TRUTH_BASELINE.md` · "
    "★`HW/PCB/FP_TRUTH_COVERAGE_GAP.md` · `HW/PCB/FP_TRUTH_LAND_SWAP_WORKPACKET.md` · `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` · "
    "★`HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` · `state/board_trip_baseline_20260723.txt` 老字一字不许删/不许改★) · ★**零挂链** · ★**零外发** · "
    "★**不代老板拍板** (★`D_ESD_USB_D` 2 脚 vs 3 脚 (W-1/W-2) · 5 只按键 3N vs 1.5N · `C_VBUS_GND` 留位还是下板 = 只登记★) · "
    "★**只写 `state/fragments/hw.yaml`** (★只走 `state/frag_write.py`★) · ★**不改 `PROJECT_TRACKER.md` §0** ★\n"
    "★**必跑命令**: ★**`bash state/pcbnew_py.sh state/check_pcb_nets.py`** (★C1~C4 真闸·要 KiCad python★) · `python3 HW/check_fp_truth_baseline.py` · "
    "`python3 HW/check_fp_truth_coverage_gap.py` · `python3 HW/check_fp_truth_land_swap.py` · `python3 HW/check_onepass_preflight_coverage.py` · "
    "★**`python3 HW/check_fp_libid_truth.py`** (★本单新建★) · ★**`python3 HW/check_fp_libid_truth.py --selftest`** · `python3 state/merge.py` · "
    "`python3 state/gate_check.py` · `python3 state/frag_write.py --agent hw-lead --show` · "
    "`md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv` · `stat -c '%y' HW/PCB/demo_mainboard.kicad_pcb`★\n"
    "★**验收线 (★20 条·main 会自己复跑·不采信你的自述★)**: ① 页存在且非空 ② 板面 186 个封装逐个实测 ③ 写盘机制写明【本机 KiCad 实测】 "
    "④ 目标清单 90 + 96 逐件给目标 `lib:name` 或「不需要写 + 理由」 ⑤ 每个 `.kicad_mod` 实测在盘 + md5 对得上 ⑥ 沙盒: 换 land + 写库名后 **C4 仍是 158** "
    "⑦ 沙盒: C1/C2/C3 不因写库名而变红 ⑧ 新闸 rc=0 ⑨ `--selftest` ≥6/6 且每条自证「只红目标那条」 ⑩ 沙盒在项目盘 `tmp/` ⑪ 板 md5/mtime 逐字节未变 "
    "⑫ 网表/脚表/BOM md5 逐字节未变 ⑬ 既有闸脚本一个字节未改 ⑭ 既有页面老字逐字节未变 ⑮ `merge.py` rc=0 且 `gate_check.py` rc=0 (★Q1 = 18/18★) "
    "⑯ 证据等级全在五级白名单 ⑰ 正文零挂起措辞 ⑱ 分片写入只走 `state/frag_write.py` ⑲ 交卷页 B1~B6 齐全 + `logs/iss369/` 留证在盘 (≥ 10 件) "
    "⑳ 回滚说明在盘 ★\n"
    "★**收工后按老规矩回卷**: ★**交卷摘要 + 必跑命令的 rc + 三件交付物路径 + 边界自证 + 要 main 裁的事 (逐条写清「要谁回答什么」)★ ★"
)

NEW = [
    {
        "id": "ISS-367", "title": TITLE367, "severity": "high",
        "source_blocker": "ISS-365", "source_agent": "main", "desc": DESC367,
        "owner": "mech-lead", "reporter": "main", "raised": "2026-11-23",
        "due": "2026-11-25", "status": "fixing", "external": False,
        "need_keys": [], "task_brief": BRIEF367,
        "note": "★2026-11-23 17:5x cron 775d9893 新开并直接派出 (★main 17:5x 自建签收闸把 ISS-363/364/365 全签成 verified ⇒ mech-lead 槽位空出来★) "
                "★类别: 纯文档定点改写 + 新建闸 + 沙盒重算 · 零写板 · 零落表 · 零改既有闸 ★",
        "dispatched_at": "2026-11-23",
    },
    {
        "id": "ISS-368", "title": TITLE368, "severity": "high",
        "source_blocker": "ISS-363", "source_agent": "main", "desc": DESC368,
        "owner": "sw-lead", "reporter": "main", "raised": "2026-11-23",
        "due": "2026-11-25", "status": "fixing", "external": False,
        "need_keys": ["iss363_b5_1_checklist_ninth_item_verdict_20261123"],
        "task_brief": BRIEF368,
        "note": "★2026-11-23 17:5x cron 775d9893 新开并直接派出 (★main 16:58 已裁「加第 9 条·三处同批落地」⇒ 本单只交幂等补丁 + 副本 dry-run 证明★) "
                "★类别: 纯作业包 + 沙盒 dry-run + 新建闸 · 零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 ★",
        "dispatched_at": "2026-11-23",
    },
    {
        "id": "ISS-369", "title": TITLE369, "severity": "high",
        "source_blocker": "ISS-361", "source_agent": "main", "desc": DESC369,
        "owner": "hw-lead", "reporter": "main", "raised": "2026-11-23",
        "due": "2026-11-26", "status": "open", "external": False,
        "need_keys": [], "task_brief": BRIEF369,
        "note": "★2026-11-23 17:5x cron 775d9893 新开 · ★★落 open 排队, 不派 (★hw-lead 此刻正在跑 ISS-366 ⇒ 一个 agent 同时只有一个写会话★)★★ "
                "★⇒ 下一轮 `state/advance.py --json` 会把本单列进 internal (★hw-lead 槽位空出来那一轮·本 job 按 A 段派·兄弟 job fb67af40 也可能派·"
                "★两个 job 都按「该 agent 无 running 写会话」判定 ⇒ 不会撞车★) ★",
    },
]


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


def main() -> int:
    applied = []
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)

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
                it["status"] = spec["status"]
                it["task_brief"] = spec["task_brief"]
                it["note"] = spec["note"]
                applied.append("%s 已存在 ⇒ status→%s + brief/note 刷新 (幂等)" % (iid, spec["status"]))
            else:
                issues.append(dict(spec))
                applied.append("新开 %s (%s) · status=%s" % (iid, spec["owner"], spec["status"]))
        log["issues"] = issues
        atomic_write(LOG, yaml.safe_dump(log, allow_unicode=True, sort_keys=False, width=10**6))

        dlog = yaml.safe_load(open(DLOG, encoding="utf-8")) or []
        if isinstance(dlog, dict):
            entries = dlog.get("dispatches") or []
            dlog_is_dict = True
        else:
            entries = dlog
            dlog_is_dict = False
        for iid, ag in (("ISS-367", "mech-lead"), ("ISS-368", "sw-lead")):
            if any((x.get("issue") == iid) for x in entries):
                applied.append("dispatch_log 已有 %s 条目 ⇒ 幂等不重复追加" % iid)
                continue
            entries.append({
                "issue": iid, "agent": ag, "at": "2026-11-23",
                "brief": "「板那一趟」前置件 · %s · 纯分析/作业包/闸类 · 零写板 · 零落表" % iid,
                "job": "cron 775d9893 (ARS45 继续执行后继计划) · 2026-11-23 17:5x GMT+8",
            })
            applied.append("dispatch_log +1 条 (%s → %s)" % (iid, ag))
        out = {"dispatches": entries} if dlog_is_dict else entries
        atomic_write(DLOG, yaml.safe_dump(out, allow_unicode=True, sort_keys=False, width=10**6))

        # 自检
        chk = yaml.safe_load(open(LOG, encoding="utf-8")) or {}
        chk_issues = chk.get("issues") or []
        chk_idx = {i.get("id"): i for i in chk_issues}
        for iid, owner, st in (("ISS-367", "mech-lead", "fixing"), ("ISS-368", "sw-lead", "fixing"), ("ISS-369", "hw-lead", "open")):
            assert iid in chk_idx, "★%s 没落进 issue_log★" % iid
            assert chk_idx[iid].get("owner") == owner, "★%s owner 不对★" % iid
            assert chk_idx[iid].get("status") == st, "★%s status 不对 (期望 %s)★" % (iid, st)
        assert len(chk_issues) == len(issues), "★issue_log 条数对不上 (自检失败)★"
        dchk = yaml.safe_load(open(DLOG, encoding="utf-8")) or []
        dlist = dchk.get("dispatches") if isinstance(dchk, dict) else dchk
        assert dlist[-1].get("issue") == "ISS-368", "★dispatch_log 末条不是 ISS-368★"
        applied.append("自检通过: issue_log %d 条 / dispatch_log 末条 = ISS-368" % len(chk_issues))

    for a in applied:
        print("✅ " + a)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
