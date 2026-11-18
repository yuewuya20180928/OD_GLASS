#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
moli (项目总工) 2026-11-17 17:0x · job fb67af40「ARS45 队列自动派活」
★ISS-291 落 verified + ISS-292 僵尸 fixing 续做重排 + 新开 ISS-293 / ISS-294★
=========================================================================================
★**为什么有这一趟 (★main 17:0x 本机实查盘面 + 读会话, 不抄任何交卷报告★)**:
  · `python3 state/advance.py --json` ⇒ ★**`internal: []` (三条 internal 全被 `fixing` 占着 ⇒ 一个都派不出去)** ★
  · ★**但盘面 ≠ 名单 (★老坑, 第三次了★)** ⇒ ★**本 job 实查三个会话的生死** ★:
    - ★`agent:hw-lead:subagent:71c9e8bb` (ISS-292) ★: 15:52:21 → 16:08:07 · runtime 944s · **status=timeout ·
      abortedLastRun=true** ⇒ ★**死在超时, 不是活干完** ⇒ 交卷单只剩骨架 (★1341 B · B0~B6 全「施工中」★) ★
      ⇒ ★**僵尸 fixing** ⇒ hw-lead 名额被一条【没人干的单】占着 ★
    - ★`agent:sw-lead:subagent:b0a6d0ff` (ISS-291) ★: 16:13:10 → 16:13:28 · **status=done** · abortedLastRun=false
      ⇒ ★**活干完了, 但 issue_log 还挂在 `fixing`** ⇒ sw-lead 名额被一条【已经交卷的单】占着 ★
      (★交卷单 28306 B · 九节齐 · timing_check rc=0 SELFTEST 85/85 · rev_cases rc=0 · regress rc=0★)
    - ★`agent:mech-lead:subagent:cedabf25` (ISS-290) ★: status=done ⇒ ★**已由 main 16:0x 复验落 `verified`**
      ⇒ ★**mech-lead 名额本来就空着** ★
  · ⇒ ★**本趟做三件事**: ①ISS-291 落 verified (★main 17:0x 独立实跑复验★) ②ISS-292 僵尸 fixing 清理 + 【续做】重排
    (★不是从零重做: 生成器那一大块已在盘上, main 16:2x 沙盒实跑证明【重跑输出与真页逐字节相同】★) ③新开 ISS-293 (sw-lead)
    + ISS-294 (mech-lead) ⇒ ★**三个名额重新全部占满, 且内部待办不断线** ★
★**★铁律**: 干活的人不许自签 ⇒ verify_by=main · ★**零写板 · 零落表** ★
★**★零外发** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★) ⇒ ★**本 job 不发任何邮件/询价/采购** ★
★**边界**: ★**只写 `state/issue_log.yaml` + `state/dispatch_log.yaml` 两个文件** ⇒ ★**不碰任何 agent 的分片
  (★`state/fragments/*.yaml` 是三个总工的, main 不写★) · 不碰板 / 网表 / 脚表 / BOM / 决策页 / outbox / 任何闸脚本★**
"""
import fcntl
import os
import shutil

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
DL = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
BAK = LOG + ".bak_20261117_1700_cronfb67_verify291_cont292_open293_294"
TODAY = "2026-11-17"

BRIEF_293 = os.path.join(HERE, "dispatch_briefs", "ISS-293_sw_adc_fullscale_caliber_review_sync.md")
BRIEF_294 = os.path.join(HERE, "dispatch_briefs", "ISS-294_mech_usbc_edge_opening_spec.md")
BRIEF_292_CONT = os.path.join(HERE, "dispatch_briefs", "ISS-292_hw_preflight_generator_realign_cont1.md")

VERIFY_291 = """★main 2026-11-17 16:4x~17:0x 本机独立实跑复验 (★自己实跑, 不抄交卷报告★) ⇒ 交卷单 `HANDOFF/2026-11-17_sw-lead_ISS291_ADC满量程与判决对象口径收口.md` = **28306 B** · §0 / §B1~§B5 / §6 分片 / §7 边界自查 / §8 留给 main 三件事 / §9 复现命令 **九节齐全** (★占位符 grep **0 处**★) ⇒ ★**新闸实跑**: `python3 SW/tools/timing_check.py` ⇒ **rc=0 · SELFTEST 85/85 通过** (★反向后仍 85/85·0 条红★) ⇒ `python3 SW/tools/timing_check.py --only F4_adc_det` ⇒ 实读 **active_chain = BAT_DET / pin38 / SARADC_VIN5 / 1.8V 域 · full_scale_v = 1.8 · adc_bits = 12 · lsb_mv = 0.439 · rth_ohm = 37500.0 · tau_ms = 3.75 · t_settle_to_half_lsb_ms = 33.791 · leak_offset_v = 0.0375 · leak_offset_pct_fs = 2.1 · standby_ua = 26.25 · node_v_at_supply = 1.575 ≤ node_max_abs_v = 1.98 · fs_utilization_pct = 87.5 · criteria 全 True ⇒ verdict 判通过** ⇒ ★**口径改对两处逐条对上**: ① 满量程 `DEVICE["V_DET_FS"]` = 3.3 → **1.8** (★闸 L81 实读现值★) ② 判决对象 = 装机链 `BAT_DET` (★取链规则 `by_landing_pin` · 判决源 = SoM 脚表 `SARADC_VIN5`★) ⇒ ★**反向用例**: `python3 logs/iss291/rev_cases.py` ⇒ **rc=0** (★6 条全抓到: 满量程 / 判决对象 / 建链规则 / 漏电阈值 / 数字链静态电流 / 数字链节点电平 逐条变红★) ⇒ ★**回归**: `bash logs/iss291/regress.sh` ⇒ **rc=0** (★9 项全过, 含 `state/issue_check.py` rc=0 + 受保护 5 件 md5 逐字节不变 + `timing_check.py` md5 `cf09c921002937920bfa40701d523b33`·2632 行★) ⇒ 口径对照页 `SW/ADC_CALIBER_TABLE.md` = **9221 B** 在盘 ⇒ ★**分片**: `state/fragments/sw.yaml` 里 `grep -c iss291` = **6** (★含 2 条 need + artifacts + answer★) ⇒ ★**need 闭合**: `iss223_sw_vdet_fs_domain_fix` 的答案写在 sw-lead 自己的分片 `answers` 段 (★key=`iss223_sw_vdet_fs_domain_fix` · to=sw-lead★) ⇒ ★**不是 foreign_answer** ⇒ merge 配对后 `state: answered` (★main 本机实查 STATE.yaml 确认★) ⇒ `iss285_sw_apply_after_iss283_verified` 已标 `resolved_by: ISS-288` ⇒ ⇒ `python3 state/merge.py` **rc=0** (★未闭合需求 296 → 295★) ⇒ `python3 state/gate_check.py` **rc=0** (★Q1 交付齐备率 **18/18**★) ⇒ 受保护 5 件逐字节未变: 板 `611b869e13518c3c023fb178f91a0075` (★mtime 仍 `2026-11-06 07:07:17`★) · `.kicad_pro` `3e504d2be83152e337949723e909be1b` · 网表 `37f62ac3f0b81d92ca7d48fdea717f07` · 脚表 `a4270120454aedf7a23c92cd8985c8a6` · BOM `5d02bece9477ffce5fbe0193c7d5cce4` ⇒ ★**零写板 · 零落表**★ ⇒ ★**本单顺带查出的一个后续缺口 (★已开 ISS-293 交给 sw-lead★)**: `SW/SW_TIMING_REVIEW.md` 这份复评文档还停在 ISS-291 之前的旧口径 (★判决对象仍写 `VBUS_DET_D` · 15.2%FS · 「BAT_DET 三颗全 DNP」· §7-4 那条 P0 整条不成立★) ⇒ ★**若放着, 下一个人照它判「ADC 链不合格 ⇒ 改板」⇒ 板白改第二遍** ⇒ ⇒ 已开 ISS-293 收口★"""

NOTE_292 = """
★★2026-11-17 17:0x 队列自动派活 job (fb67af40) **僵尸 fixing 清理 + 【cont1 续做】重排 (★不是从零做★)** ★★: 子会话 `agent:hw-lead:subagent:71c9e8bb` (sessionId 54b83bdf) 15:52:21 → 16:08:07 (runtime 944s · status=timeout · abortedLastRun=true) ⇒ ★**死在超时, 不是活干完** ⇒ 交卷单只剩骨架 `HANDOFF/2026-11-17_hw-lead_ISS292_清单页生成器对齐.md` = **1341 B · B0~B6 全是「★(施工中★)」** ★ ⇒ ★**盘上已有实测成果 (★main 16:2x~17:0x 本机实跑, 不是抄报告★)**: ① 生成器 `state/_iss277_build_preflight.py` 已改写 (★md5 `0767fcc5…` → `f80a094fc1d8e497295bb543a06ee109` · 25077 B → 41748 B · mtime 16:04:45★) ⇒ R3-A4 三个数改成从真源 `HW/check_netlist_contradiction_r3.py` 读 (★读不到 ⇒ fail-closed 拒写页★) + 脚表缺陷条数改成从真源 `HW/check_pin_function_labels.py` 读 (★同样 fail-closed★) + ★**补上了 `B32_V2_NET_RENAME`** ★ + `B17_DNP_43` 这个 id **没改名** (★只订正值·符合原任务书要求★) ② 新增追加式 sidecar `state/_iss277_preflight_appendix.md` = 27293 B (★承载 ISS-283 §3-追加 + ISS-289 现状值订正块; sidecar 缺 ⇒ 拒写页★) ③ ★★**main 16:2x 沙盒实跑证明【重跑幂等已达成】★★: 把生成器 OUT 改到 `tmp/iss292_sbx/gen_out.md` 跑 ⇒ rc=0 · 读数 R3_T/R3_O/R3_Z = 51/40/40 · P_T/P_F/P_W/P_M/P_MD5 = 18/15/14/1/3 · 32 条 ⇒ ★**沙盒输出 md5 = `159bf20fe71c36e48292f39dafc46a35` == 真页 md5 `159bf20fe71c36e48292f39dafc46a35` · `diff` rc=0 (零行差异) ⇒ 重跑后页【零回退】★★ ⇒ ⇒ ★**⇒ 生成器那一大块已经做完了, 本趟【不许重做】, 真正剩下的活 = 作业包 §3-S1 指针改对 + 「收工后重锚」写成收工清单强制项 + 反向用例 ≥3 条 + 回归 8 条 + E-1~E-6 并进清单页 + 沙盒 README + 交卷单 B0~B6 填满 + 分片 (★`grep -c iss292` 现在 = 0, 一条都没写★)** ★ ⇒ ★**续做任务书全文 = `state/dispatch_briefs/ISS-292_hw_preflight_generator_realign_cont1.md` (★9880 B · 已过 `python3 state/check_brief_commands.py --brief-file` ⇒ rc=0★) ⇒ 第一件事先 cat 全文** ★ ⇒ ★**本 job 实测受保护 5 件逐字节未变** (板 611b869e… mtime 仍 2026-11-06 07:07:17 · .kicad_pro 3e504d2b… · 网表 37f62ac3… · 脚表 a4270120… · BOM 5d02bece…) ⇒ 零写板 · 零落表 仍成立 ★"""

CONT_292 = """

---

## ★★⑭ 追加 (★2026-11-17 17:0x 队列自动派活 job fb67af40 · ★**本单改【续做】, 不许从零重做★**★)

★**★上一趟的会话死了 (★不是活干完★)★**: `agent:hw-lead:subagent:71c9e8bb` 15:52:21 → 16:08:07 · status=timeout · abortedLastRun=true ⇒ 交卷单只剩骨架 (★1341 B·B0~B6 全「施工中」★) ★

★**★但生成器那一大块【已经在盘上了】⇒ 不许重做★**: `state/_iss277_build_preflight.py` 已改写成从真源读 (★R3-A4 ← `HW/check_netlist_contradiction_r3.py` · 脚表缺陷条数 ← `HW/check_pin_function_labels.py` · 两处都 fail-closed★) + 已补 `B32_V2_NET_RENAME` + `B17_DNP_43` 未改名 + 新增 sidecar `state/_iss277_preflight_appendix.md` (★27293 B★) ⇒ ★**main 16:2x 沙盒实跑: 重跑输出 md5 `159bf20f…` == 真页 md5 `159bf20f…` · diff rc=0 ⇒ 重跑零回退 (B2 硬判据已达成)★** ★

★**⇒ 本趟真正的活 = 补下面 7 件 (★只有这 7 件★)** ★:

★**B3** 作业包 §3-S1 位号真源指针改对 (★现在还写着 `HW/SCHEMATIC_V1_SPEC.json` 的 `devices` 段·而那个 JSON 顶层**没有** `devices` 键 ⇒ 真源 = `HW/netlist_v1_pins.csv`·218 器件·**追加式订正·老字不删**★) ★

★**B4** 「收工后同一次重锚」写成收工清单强制项 (★现在工作包里 grep「重锚」= 0 处·完全没写★) ★

★**B5** 反向用例 ≥3 条 (★`logs/iss292/` 现在只有 `baseline_before.txt`·一条都没跑★) ★

★**B6** 回归 8 条 (★一条都没跑过★) ★

★**⑬** E-1~E-6 六条并进清单页 (★`grep -c "E-1" HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` = 0 ⇒ 一条都没并·★E-1/E-2/E-6 是老板级 ⇒ 只交选项与代价·不代拍·生成器不许写死六条·从真源读★) ★

★**R** 沙盒 README (`tmp/iss292/README.md` 不存在) ★

★**F** 交卷单 B0~B6 填满 + 分片 (`state/fragments/hw.yaml` 里 `grep -c iss292` = 0 ⇒ 一条都没写) ★

★**★★完整续做任务书全文 = `state/dispatch_briefs/ISS-292_hw_preflight_generator_realign_cont1.md` (★9880 B ★) ⇒ ★**第一件事先 cat 全文** ★ (★已过 `python3 state/check_brief_commands.py --brief-file` ⇒ rc=0★) ★

★**★★三条最硬的边界 (★原任务书 + 续做说明合起来★)★★: ★**① 零写板 (板 md5 + mtime 双重自证) · 零落表 (网表/脚表/BOM 一个字节不许动) · ② 不许改 `HW/check_workpack_state_values.py` (★那是 ISS-289 的闸·本单不许碰★) · ③ 不许改 `SW/` 与 `MECH/` 的文件与分片** ★ ⇒ ★**本单零外发 (老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料) ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ⇒ 没有「批一句可以发」这个选项** ★"""

TITLE_293 = """★★[主线内·SW 侧·复评文档口径收口 + 机器闸类·内部活] ★★【`SW/SW_TIMING_REVIEW.md` 停在 ISS-291 之前的旧口径 ⇒ 判决对象仍写 `VBUS_DET_D` (实为 USB 数字检测脚) + 满量程隐含 3.3V (官方 1.8V 域) + 「BAT_DET 三颗全 DNP」(09:58 落表后已必装) + §7-4 那条 P0 整条不成立】★★ ⇒ ★**照它判「ADC 链不合格 ⇒ 改板」⇒ 板白改第二遍** ★ ⇒ ★**本单 = 按真值订正 6 处 + 新建一道「文档不许再漂」的机器闸 (★纯文档 + 闸·零写板·零落表·零改网表真源★)** ★"""

DESC_293 = """★main 2026-11-17 16:4x~17:0x 本机实读 + 实跑 (★不抄任何 agent 报告★)★
★**① 判决对象过期**: `SW/SW_TIMING_REVIEW.md` L38 (F6 行) / L56 / L207 仍写「装机的是 `VBUS_DET_D` 链 (1M+1M+100nF) ⇒ 500kΩ / 50ms / 451ms / 0.50V (15.2%FS)」⇒ ★**而 ISS-291 已把判决对象改成 `BAT_DET`** (★取链规则 `by_landing_pin` · 判决源 = SoM 脚表 `HW/PCB/FET3572C_PIN_TABLE.csv` L39 `SARADC_VIN5` = 1.8V 域 ⇒ 落点 `J_SOM_P1 pin38` = ADC 脚; 而 `J_SOM_P1 pin100` = `USB_DRD1_VBUSDET` = **数字脚**★) ⇒ ★**`VBUS_DET_D` 现在按【数字检测输入】口径单判 (F4D 段)·不参与 ADC 判决**★
★**② 满量程过期**: 文档里的 15.2%FS / 0.8057mV LSB 都是【按 3.3V 算出来的数】⇒ ★**官方是 1.8V 域** (★脚表 L39 + datasheet L2454 `SARADC_AVDD1V8 = 1.62/1.8/1.98V` + L2864 `Analog Input Range = AVSS18~AVDD18` ⇒ [官网]★) ⇒ LSB = 0.439mV · 2.1%FS ⇒ **文档隐含的整条算式全错**★
★**③ BAT_DET 已不是 DNP (★这条最重★)**: 文档 L343 (§7-4 P0) / L370 (CR-4) / L433 / L556 仍写「三颗全 DNP」+ 「`R_BAT_DET_1`/`R_BAT_DET_2` = 1M」⇒ ★**main 16:4x 本机实读 `HW/netlist_v1.csv` L182~L186**: `R_BAT_DET_1` = **100k ±1% 必装** · `R_BAT_DET_2` = **60k ±1% 必装** · `C_DET_BAT` = **100nF ±10% 必装** · `NET_BAT_DET` → `J_SOM_P1 pin38` = 必装 ⇒ ⇒ **那条 P0 整条不成立 + 连阻值 (1M ⇒ 100k+60k) 都错** ⇒ ★**文档 §7-4 现在是一条【已被推翻的 P0】· §3.3 判定表里那两行「❌ 不通过」是【假红被当成结论记着】** ★
★**④ 正确现值 (★main 16:4x 实跑 `python3 SW/tools/timing_check.py --only F4_adc_det` 的原样读数·**这是本单要写进文档的数·一字都不许自己编★)★**: active_chain=BAT_DET / pin38 / SARADC_VIN5 / 1.8V 域 · full_scale_v=1.8 · adc_bits=12 · lsb_mv=0.439 · rth_ohm=37500.0 · tau_ms=3.75 · t_settle_to_half_lsb_ms=33.791 · leak_offset_v=0.0375 · leak_offset_pct_fs=2.1 · standby_ua=26.25 · node_v_at_supply=1.575 ≤ node_max_abs_v=1.98 · fs_utilization_pct=87.5 · criteria 全 True ⇒ **判通过** ★
★**⑤ 复发防护**: 这份文档是【手工写的】⇒ 闸变了文档不会跟着变 ⇒ ★**本单要新建 `SW/tools/check_timing_review_adc_sync.py` 把文档的 ADC 现值钉住 (★判决对象 / 满量程 / BAT_DET 已必装 三条★) + ≥4 条反向用例 (★在沙盒副本上做·真件一个字节不许碰★) ★"""

TITLE_294 = """★★[主线内·MECH 侧·规格补缺 + 机器闸类·内部活] ★★【`J_USB_C` 缺一条结构边开口规格 (★座体 `F.Fab` Y 下沿 = 0.000 = 板边 ⇒ 插头从板边进出, 但 MECH 规格页 + 两道 MECH 闸里【只有】检修口/调试口两条开口·第三边完全不存在★)】★★ ⇒ ★**结构件没有这条开口 ⇒ USB-C 插头根本插不进去 ⇒ 板装上了也用不了** ★ ⇒ ★**本单 = 补第三条开口规格 (含固定孔清空区) + 把两道闸从「条数断言」改成【集合 + 两两不相同】(★合并禁令不许松★) + ≥4 条反向用例 (★纯 MECH 侧·零写板·零落表·零改网表★)** ★"""

DESC_294 = """★main 2026-11-17 16:3x~17:0x 本机实读盘面 + 实跑 (★不抄任何 agent 报告★)★
★**① 缺口本体**: ISS-290 (mech-lead · 结构侧交叉核对·已由 main 16:0x 复验落 verified) §5 留了一条它【做不了也没做】的缺口 = ★**E-6 · `J_USB_C` 缺一条结构边开口规格** ★ ⇒ ★**ISS-290 已把 `J_USB_C` 登记为 `USB-C-BODY` 禁入区 (X 135.680..144.320 × Y 0.000..6.400)·但 MECH 的【规格页 + 机器闸】里还只有两条开口·第三边完全不存在** ★ ⇒ ★**E-1~E-6 六条已由 main 转给 hw-lead 的 ISS-292 (任务书「⑬ 追加」节)·唯独 E-6 的 MECH 侧规格本体没人接** ★
★**② 板面实测 (★main 16:3x 本机 `bash state/pcbnew_py.sh` 读板★)**: `J_USB_C` 座体 `F.Fab` = X 135.680..144.320 × Y 0.000..6.400 (8.64 × 6.40·座体高 3.50) ⇒ **Y 下沿 = 0.000 = 板边** ⇒ 插头从板边进出 ★ ⇒ 18 个焊盘: 16 信号 (A1/A4/A5/A6/A7/A8/A9/A12/B1/B4/B5/B6/B7/B8/B9/B12·Y 中心全 5.25·焊盘 0.30×1.15) + **2 个 Ø0.65 固定孔 (NPTH) @ (134.22, 2.625) 与 (145.78, 2.625)** ⇒ ★**固定孔 X 间距 11.56·中心 140.00·比座体 `F.Fab` (135.680..144.320) 还往外 1.46 ⇒ 结构件边开口必须比座体更宽才容得下螺丝头/结构柱** ★
★**③ 规格页现状 (★main 16:3x 本机 json 解析实读 `MECH/BOARD_ONEPASS_MECH_SYNC.md` §5 机器块★)**: 顶层键 = issue / agent / updated / frame_default / frames_allowed / consts / **openings (len=2 → ['PORT_OPEN_DEBUG','PORT_OPEN_UART'])** / merged_opening / led / connectors / items (len=9) ⇒ ★**没有任何一条是 `J_USB_C` 的板边开口** ★
★**④ 两道闸把「恰好两条」写死 (★这是本单最关键的一条纪律★)★**: `MECH/check_onepass_mech_sync.py` L191~L193 `if len(openings) != 2: errs.append("M2 开口必须【两条】…⇒ 不许合并")` · `MECH/check_onepass_struct_crosscheck.py` L544~L548 同样 `!= 2` + `sorted(ids) != ["PORT_OPEN_DEBUG","PORT_OPEN_UART"]` ⇒ ★**★这两条断言的【本意】是「不许把检修口/调试口【合并】成一条」⇒ ★**所以不许把 `!= 2` 改成 `!= 3` 就完事 (★那是把「两条不许合并」偷换成「三条不许合并」⇒ 合并成【一条】照样能过 ⇒ 防线反而松了★) ⇒ ★**正确改法 = 【集合断言 + 任意两条矩形不许完全相同 + 三条分别验】⇒ 合并成一条 / 把 USB-C 并进检修口 ⇒ 照样红** ★
★**⑤ 一个 E-6 没说清的问题 (★本单要点出来★)**: 检修口/调试口是【罩住一个器件的洞】(在板内部), 而 USB-C 边开口是【插头从板边插进来的缺口】(在板边界上·**另一侧是板外**) ⇒ ★**它【不可能】像另两条那样做「h 三档 Y 净距」判定** ⇒ ★**你只交【几何 + 代价 + 建议】, 结构开口的最终尺寸归 main→boss 拍** ★"""


def main() -> int:
    for p in (BRIEF_293, BRIEF_294, BRIEF_292_CONT):
        if not os.path.exists(p):
            print("⚠ 缺 brief 文件: %s ⇒ 中止" % p)
            return 1

    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        with open(LOG, encoding="utf-8") as f:
            log = yaml.safe_load(f)
        issues = log["issues"]
        by_id = {it["id"]: it for it in issues}

        # ---------- ① ISS-291: fixing → verified ----------
        i291 = by_id.get("ISS-291")
        if i291 is None:
            print("⚠ ISS-291 不存在 ⇒ 中止")
            return 1
        if i291.get("status") == "verified":
            print("· ISS-291 已是 verified ⇒ 幂等跳过")
        else:
            i291["status"] = "verified"
            i291["verify_by"] = "main"
            i291["verify_result"] = "pass"
            i291["verify_date"] = TODAY
            i291["fix_ref"] = "HANDOFF/2026-11-17_sw-lead_ISS291_ADC满量程与判决对象口径收口.md (★28306 B ★)"
            i291["note"] = (i291.get("note") or "") + (
                "\n\n★★ " + TODAY + " 17:0x (cron fb67af40 队列自动派活) ★main 独立复验通过 ⇒ 落 verified ★★ ⇒ "
                "★**依据 = 本机实跑 timing_check.py rc=0 (SELFTEST 85/85) + rev_cases rc=0 (6 条反向) + regress rc=0 "
                "(9 项) + 交卷单 28306 B 九节齐/占位符 0 处 + 分片 grep -c iss291 = 6 + merge rc=0 + gate_check rc=0 "
                "(Q1 18/18) + 受保护 5 件 md5 逐字节未变** ⇒ ★**sw-lead 名额已释放 ⇒ 本轮新开 ISS-293 "
                "(★`SW/SW_TIMING_REVIEW.md` 停在 ISS-291 之前的旧口径·判决对象/满量程/BAT_DET 已必装 三处都要订正 "
                "★ + 一道防漂的新闸)★ ★")
            print("✅ ISS-291 fixing → verified (main 独立复验)")

        # ---------- ② ISS-292: 僵尸 fixing 清理 + 续做重排 (保持 fixing·不留 open 窗口) ----------
        i292 = by_id.get("ISS-292")
        if i292 is None:
            print("⚠ ISS-292 不存在 ⇒ 中止")
            return 1
        if i292.get("status") != "fixing":
            print("· ISS-292 status=%s (不是 fixing) ⇒ 幂等跳过" % i292.get("status"))
        else:
            i292["note"] = (i292.get("note") or "") + NOTE_292
            if "⑭ 追加" not in (i292.get("task_brief") or ""):
                i292["task_brief"] = (i292.get("task_brief") or "") + CONT_292
            i292["dispatched_at"] = TODAY
            print("✅ ISS-292 僵尸清理 + ⑭ 续做说明已追加 (status 保持 fixing ⇒ 无 open 窗口)")

        # ---------- ③ 新开 ISS-293 (sw-lead) + ISS-294 (mech-lead) ----------
        with open(BRIEF_293, encoding="utf-8") as f:
            brief293 = f.read()
        with open(BRIEF_294, encoding="utf-8") as f:
            brief294 = f.read()

        new_issues = [
            {
                "id": "ISS-293",
                "title": TITLE_293,
                "severity": "high",
                "source_blocker": None,
                "source_agent": "main",
                "desc": DESC_293,
                "owner": "sw-lead",
                "reporter": "main",
                "raised": TODAY,
                "due": "2026-11-20",
                # ★★ 直接落 fixing (★先落 fixing 再 spawn·不留 open 窗口·防兄弟 job 重复派★)
                "status": "fixing",
                "external": False,
                "need_keys": [],
                "fix_ref": "",
                "verify_by": "main",
                "verify_result": "",
                "verify_date": "",
                "note": ("★main 2026-11-17 17:0x 新开 (cron fb67af40 队列自动派活) ⇒ ★**零写板 · 零落表 · 零改网表真源** ★"
                         "⇒ ★**任务书全文 = `state/dispatch_briefs/ISS-293_sw_adc_fullscale_caliber_review_sync.md` "
                         "(★11794 B · 已过 `python3 state/check_brief_commands.py --brief-file` ⇒ rc=0★)** ⇒ "
                         "★**第一条 (必做)**: 先 cat 那份任务书全文 ★ ⇒ ★**本单是 ISS-291 复验时查出的后续缺口: "
                         "复评文档还停在旧口径 ⇒ 照它判「ADC 链不合格 ⇒ 改板」⇒ 板白改第二遍** ★ ⇒ "
                         "★**本单零外发 (老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料) ⇒ "
                         "缺口一律自己网上查 + 标证据等级 + 查不到就写降级方案** ★"),
                "dispatched_at": TODAY,
                "task_brief": brief293,
            },
            {
                "id": "ISS-294",
                "title": TITLE_294,
                "severity": "high",
                "source_blocker": None,
                "source_agent": "main",
                "desc": DESC_294,
                "owner": "mech-lead",
                "reporter": "main",
                "raised": TODAY,
                "due": "2026-11-20",
                "status": "fixing",
                "external": False,
                "need_keys": [],
                "fix_ref": "",
                "verify_by": "main",
                "verify_result": "",
                "verify_date": "",
                "note": ("★main 2026-11-17 17:0x 新开 (cron fb67af40 队列自动派活) ⇒ ★**零写板 · 零落表 · 零改网表/脚表/BOM** ★"
                         "⇒ ★**任务书全文 = `state/dispatch_briefs/ISS-294_mech_usbc_edge_opening_spec.md` "
                         "(★10962 B · 已过 `python3 state/check_brief_commands.py --brief-file` ⇒ rc=0★)** ⇒ "
                         "★**第一条 (必做)**: 先 cat 那份任务书全文 ★ ⇒ ★**本单是 ISS-290 留下的 E-6 (J_USB_C 结构边开口)"
                         "的 MECH 侧规格本体** ★ ⇒ ★**本单零外发 (老板 2026-11-11 19:31 + 2026-11-12 02:02: "
                         "不再发信, 全靠自己查资料) ⇒ 缺口一律自己网上查 + 标证据等级 + 查不到就写降级方案** ★"),
                "dispatched_at": TODAY,
                "task_brief": brief294,
            },
        ]

        for ni in new_issues:
            if ni["id"] in by_id:
                print("· %s 已存在 ⇒ 幂等跳过" % ni["id"])
                continue
            issues.append(ni)
            print("✅ %s 已开 (owner=%s · status=fixing · due=%s)" % (ni["id"], ni["owner"], ni["due"]))

        shutil.copy2(LOG, BAK)
        tmp = LOG + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)
        os.replace(tmp, LOG)

        # ---------- 派活日志 ----------
        with open(DL, encoding="utf-8") as f:
            dl = yaml.safe_load(f) or {}
        dl.setdefault("dispatches", []).append({
            "issue": "ISS-291",
            "agent": "sw-lead",
            "at": TODAY,
            "brief": ("★main 17:0x 独立复验落 verified (★timing_check rc=0 SELFTEST 85/85 · rev_cases rc=0 · "
                      "regress rc=0 · 交卷单 28306 B 九节齐 · 分片 6 条 · merge/gate_check rc=0 · 受保护 5 件未变★) "
                      "⇒ sw-lead 名额释放"),
            "job": "★派活方 = cron fb67af40 (ARS45 队列自动派活) 于 17:0x 复验签 · "
                   "★**本 job 不派活·只签字** ⇒ 该名额随即由 ISS-293 占 (见下条)★",
        })
        dl.setdefault("dispatches", []).append({
            "issue": "ISS-292",
            "agent": "hw-lead",
            "at": TODAY,
            "brief": ("★**僵尸 fixing 清理 + 【cont1 续做】重排 (★不是从零做★)★**: 会话 "
                      "`agent:hw-lead:subagent:71c9e8bb` 16:08:07 timeout/aborted ⇒ 交卷单只剩 1341 B 骨架 ⇒ "
                      "★**但生成器那一大块已在盘上** (★main 16:2x 沙盒实跑: 重跑输出 md5 159bf20f… == 真页 md5 159bf20f… "
                      "· diff rc=0 ⇒ 重跑零回退★) ⇒ ★**本趟只补 7 件**: 作业包 §3-S1 指针 / 收工重锚强制项 / 反向用例≥3 / "
                      "回归 8 条 / E-1~E-6 并清单页 / 沙盒 README / 交卷单 B0~B6 + 分片 ★"),
            "job": "★派活方 = cron fb67af40 (ARS45 队列自动派活) 于 17:0x 续做重派 · "
                   "★**brief = issue_log 里 ISS-292 的 task_brief (★已含本 job 追加的「⑭ 追加」节★) ⇒ "
                   "★完整续做任务书 = `state/dispatch_briefs/ISS-292_hw_preflight_generator_realign_cont1.md` "
                   "(★9880 B · check_brief_commands --brief-file ⇒ rc=0★)★ · "
                   "★**status 全程保持 fixing ⇒ 无 open 窗口 ⇒ 兄弟 job 775d9893 不会重复派**★",
        })
        for ni in new_issues:
            bpath = os.path.basename(BRIEF_293 if ni["id"] == "ISS-293" else BRIEF_294)
            dl.setdefault("dispatches", []).append({
                "issue": ni["id"],
                "agent": ni["owner"],
                "at": TODAY,
                "brief": ni["task_brief"][:300],
                "job": ("★派活方 = cron fb67af40 (ARS45 队列自动派活) 于 17:0x 新开并派出 · "
                        "★**brief = issue_log 里 %s 的 task_brief 全文 (= state/dispatch_briefs/%s)★ · "
                        "★**先落 fixing 再 spawn ⇒ 无 open 窗口 ⇒ 兄弟 job 775d9893 不会重复派**★"
                        % (ni["id"], bpath)),
            })
        tmpd = DL + ".tmp"
        with open(tmpd, "w", encoding="utf-8") as f:
            yaml.safe_dump(dl, f, allow_unicode=True, sort_keys=False, width=200)
        os.replace(tmpd, DL)
        fcntl.flock(lk, fcntl.LOCK_UN)

    print("备份: %s" % BAK)
    print("dispatch_log 已追加 4 条 (ISS-291 验签 / ISS-292 续做 / ISS-293 / ISS-294)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
