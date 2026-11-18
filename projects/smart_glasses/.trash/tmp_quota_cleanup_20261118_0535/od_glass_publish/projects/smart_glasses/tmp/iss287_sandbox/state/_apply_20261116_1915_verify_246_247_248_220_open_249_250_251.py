#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20261116_1915_verify_246_247_248_220_open_249_250_251.py
★main (moli) · cron fb67af40「ARS45 队列自动派活」· 2026-11-16 19:15 ★

★★**本脚本只做两件事 (★不碰真源 / 不碰板 / 不碰分片 / 不发信★)** ★★
① ★**验收签字 4 条** (★main 自己实跑门禁, 不采信 agent 自述★):
   · ISS-246 (mech-lead) ⇒ 子会话 status=done @18:51:54 · 3 件交付物在盘 ⇒ 落 `verified`
   · ISS-247 (hw-lead)  ⇒ 子会话 status=done @18:48:02 · 5 件交付物在盘 ⇒ 落 `verified`
   · ISS-248 (sw-lead)  ⇒ 子会话 status=done @18:39:49 · 2 件交付物在盘 ⇒ 落 `verified`
   · ISS-220 (hw-lead)  ⇒ ★**04:1x 落 `fixed` 时唯一缺口 = 3 条分片声明没落盘** ⇒
     ★**main 本轮实测 `state/fragments/hw.yaml` 里 3 个 key 全在 (L3295/L3300/L3305, 由 ISS-223 补落)** ⇒ 缺口闭合 ⇒ 落 `verified`
② ★**新开 3 条 (★每个 agent 恰好 1 条, 全是内部活, 一条 PCB 布线/布局都没有★)**:
   · ISS-249 → hw-lead : ★**落表 F1** (ISS-247 作业包 → 真源 → 重生成 → 门禁转绿) ★**原理图主线正中央**
   · ISS-250 → sw-lead : ★**ISS-155 闭环** (rknn-toolkit2 对 RK3572 的 target 支持 = 自己查 + 证据等级 + 降级方案)
   · ISS-251 → mech-lead: ★**MECH 侧三处"只报不改"老账收口** (充电耗散口径 / 铝 k 保守侧 / 检修口 15mm→60×30)

★★**口径 (老板 2026-11-11 10:07 + 2026-11-11 19:31 + 2026-11-12 02:02)★★ ★★
· ★**主线 = 硬件原理图 demo 绘制** ⇒ ★**PCB 布线/布局类一条都不派** (owner=main/boss 的 ISS-122/126/128/160/169 继续压着) ★
· ★**零外发** ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到写降级方案 ⇒ 没有"批一句可以发"这个选项 ★
· ★**不许替老板拍板** ⇒ V-2/V-3/V-4 / 屏版本 / d 值 / u8 / 集热面材质 / 板长 一律只列选项 + 量化代价 ★
"""
import os
import shutil
import datetime as dt

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
TODAY = "2026-11-16"
NOW = "2026-11-16 19:1x"

# ======================================================================================
# ① 验收签字 4 条 (★verify_result = main 自己实跑的输出, 不抄 agent 自述★)
# ======================================================================================
VERIFY = {
    "ISS-246": (
        "★main 独立复核 (★2026-11-16 19:1x, 自己实跑, 不抄交卷报告★):\n"
        "  · `python3 MECH/check_demo_struct_truth.py` ⇒ rc=0 (23/23 · FAIL 0 · ★6 个 PCB 类 FAIL 是正确状态, 排队等原理图定稿★)\n"
        "  · `python3 MECH/check_demo_struct_truth.py --selftest` ⇒ rc=0 (反向 14/14 全抓到)\n"
        "  · 交卷单 `HANDOFF/2026-11-16_mech-lead_ISS245_MECH侧H1重锚第3跳.md` B1~B6 + ★附 6 段已填 (8816 B → 55892 B) ★\n"
        "  · 沙盒三步留档 `HANDOFF/2026-11-16_mech-lead_ISS246_沙盒反向自证_step{A,B,C}.log` (stepA 23/23 → stepB 21/23 FAIL 2 真红 → stepC 23/23 绿)\n"
        "  · `state/fragments/mech.yaml` 命中 `iss246` 6 处 (frag_write.py 原子写) · `/tmp/iss246_mech/sandbox/` 已删\n"
        "  · `python3 state/merge.py` ⇒ rc=0 · `python3 state/gate_check.py` ⇒ rc=0 (Q1 18/18)\n"
        "  · 受保护 md5: 板 `611b869e13518c3c023fb178f91a0075` + `.kicad_pro` `3e504d2be83152e337949723e909be1b` 逐字节不变\n"
        "★**main 的两条如实登记**: ① 交卷单 B1 §1.10 原写「HW/ 全目录 md5 diff 为空」不成立 (是 hw-lead ISS-247 产物 + 板侧生成器重生成 ⇒ 已在 B5 ⑦ 归属表逐项订正) "
        "② Q5 里 mech-lead 5/5 是假阳性 (扫到了 sw-lead 那行) ⇒ 本单实质新增硬指标 = 0 条 (已在 B5 ④ 加注)\n"
        "⇒ ★**本单通过, 落 verified** ★",
        "★**本轮 (19:1x) 补记**: 上一轮 18:3x 续做重派 (runTimeout 5400s) 的交卷物已全部在盘 ⇒ main 独立复核通过 ⇒ 落 verified ⇒ **mech-lead 名额释放** ★",
    ),
    "ISS-247": (
        "★main 独立复核 (★2026-11-16 19:1x, 自己实跑, 不抄交卷报告★):\n"
        "  · `python3 HW/check_iss247_f1_landed.py` ⇒ rc=1 (★**这是正确状态**: F1 还没落表 ⇒ 门禁如实判红; 落表后必须转 rc=0)\n"
        "  · `python3 HW/check_iss247_f1_landed.py --selftest` ⇒ rc=0 (10 条反向用例 + 1 条正向全抓到)\n"
        "  · 门禁命中行 (main 读到): L8 `net=VBUS_5V_F1 ref=C_VBUS_OUT` 的对端裸位号 = `C_VBUS_GND` · L12 `net=VBUS_5V_CHG ref=C_VBUS_GND` 的对端裸位号 = `C_VBUS_OUT` ⇒ 与 ISS-242 F1 病灶一致\n"
        "  · 5 件交付物在盘: `HW/SCHEMATIC_LANDING_F1_WORKPACKET_V1.md` · `HW/SCHEMATIC_LANDING_NEXT_BATCH_V1.md` · `HW/check_iss247_f1_landed.py` · `HANDOFF/2026-11-16_hw-lead_ISS247_F1落表作业包v1.md` · `state/fragments/hw.yaml` (命中 `iss247` 6 处)\n"
        "  · `python3 state/merge.py` ⇒ rc=0 · `python3 state/gate_check.py` ⇒ rc=0 (Q1 18/18 · Q6 硬件真源闸 ✅)\n"
        "  · 受保护 md5: 网表 `611c3ba3db3dc7de7213063375b96d01` · 脚表 `ef436a37412ac9b6eac3c9f41f1edca4` · BOM `2a7305741134788dfee9f13f34c656b4` · 板 `611b869e…` · `.kicad_pro` `3e504d2b…` 全部与交卷报告一致 (真盘零写入成立)\n"
        "★**订正一处**: 交卷报告说改法在 `state/gen_netlist.py` L381/L393, 而上一轮 brief 写的 L369/L381 与盘上现号不符 ⇒ **以 hw-lead 实测行号为准** ★\n"
        "⇒ ★**本单通过 (作业包 + 门禁 + 清单三件齐), 落 verified** ⇒ ★**下一步 = 真落表 (已开 ISS-249 → hw-lead)** ★",
        "★**本轮 (19:1x) 补记**: 上一轮 18:0x 续做重派 (runTimeout 5400s) 的 5 件交付物已全部在盘 ⇒ main 独立复核通过 ⇒ 落 verified ⇒ **hw-lead 名额释放** ⇒ 同轮开 ISS-249 (落表 F1) 把它续上 ★",
    ),
    "ISS-248": (
        "★main 独立复核 (★2026-11-16 19:1x, 自己实跑, 不抄交卷报告★):\n"
        "  · `python3 SW/tools/timing_check.py` ⇒ rc=0 (★SELFTEST 71/71 通过★ · ★注意: 该脚本没有 `--selftest` flag, 71 条 selftest 就是默认路径★)\n"
        "  · `python3 SW/tools/timing_check.py --reverse-demo` ⇒ rc=0 (末行「反向演示: ✅ 变红 ⇒ 它真在读网表 (不是演常量)」)\n"
        "  · `python3 SW/tools/check_demo_panel_spec.py` ⇒ rc=0 (R1~R7 全过) · `--selftest` ⇒ rc=0 (16/16)\n"
        "  · 交付物在盘: `HANDOFF/2026-11-16_sw-lead_ISS248_reverse-demo演示段口径对齐.md` · `state/fragments/sw.yaml` (命中 `iss248` 5 处)\n"
        "  · `python3 state/merge.py` ⇒ rc=0 · `python3 state/gate_check.py` ⇒ rc=0 (Q1 18/18)\n"
        "  · 受保护 md5 逐字节不变: 网表 `611c3ba3…` · 脚表 `ef436a37…` · BOM `2a730574…` · 板 `611b869e…` · `.kicad_pro` `3e504d2b…`\n"
        "⇒ ★**本单通过, 落 verified** ⇒ **sw-lead 名额释放** ⇒ 同轮开 ISS-250 (ISS-155 闭环) 把它续上 ★",
        "★**本轮 (19:1x) 补记**: 子会话 18:31~18:39 交卷 ⇒ main 独立复核四条门禁全绿 ⇒ 落 verified ⇒ **sw-lead 名额释放** ★",
    ),
    "ISS-220": (
        "★main 补签 (★2026-11-16 19:1x): 04:1x 落 `fixed` 时**唯一缺口 = 交付物④ (3 条跨模块口径声明进分片) 没落盘** ⇒\n"
        "  · ★**main 本轮实测 `state/fragments/hw.yaml`**: 3 个 key 全部在盘 (L3295 `iss220_chgboard_white_list_scope` / L3300 `iss220_i2ca_pullup_domain_1v8` / L3305 `iss220_ichg_ratio_true_value`) ⇒ **由 ISS-223 补落** ⇒ ★**缺口闭合** ★\n"
        "  · 落表本体 main 04:1x 已复核通过 (落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` 在盘 · 交接单 `HANDOFF/2026-11-16_hw-lead_ISS220_落表第1批.md` 在盘 · 板 md5 `611b869e…` + `.kicad_pro` `3e504d2b…` 逐字节未变)\n"
        "  · 本轮 `python3 HW/check_netlist_selfconsistency.py --expect-resolved` ⇒ rc=1 (★**这是正确状态**: 剩余未落表条目已分别由 ISS-233 / ISS-243 / ISS-247 / ISS-249 接力, 不是本单失职★)\n"
        "⇒ ★**本单落 verified** (★6 条 V-x 一条没代拍 · 落表范围没越界·板一个字节没碰★) ★",
        "★**本轮 (19:1x) 补签**: 唯一遗留缺口 (3 条分片声明) 已由 ISS-223 补齐并经 main 实测在盘 ⇒ 落 verified ★",
    ),
}

# ======================================================================================
# ② 新开 3 条
# ======================================================================================
BRIEF_249 = """★★**目标 (★内部活·原理图/网表侧·★不是 PCB 布线/布局类·不是老板级拍板★)** ★★
★**把 ISS-247 交卷的 F1 落表作业包【真的落进真源】** ⇒ ★**改 `state/gen_netlist.py` 两行 node2 → 重生成 6 件生成物 → 新门禁 `HW/check_iss247_f1_landed.py` 从 rc=1 转 rc=0** ★★
⇒ ★**目标状态: 真盘上 F1 已落 (2 脚电容一颗只落 2 个网) + 8 条门禁全绿 + 落表台账有本单新段 + 交卷单 + 分片 + 反向自证** ★★

★★**① 病灶 (★main 2026-11-16 19:1x 本机实跑, 原样输出★)** ★★
· ★**`python3 HW/check_iss247_f1_landed.py` ⇒ rc=1** ★ 末行: 「判定: ❌ F1 未落表 (★网表里 node2 槽仍借用了别的器件裸位号★)」
· ★**`python3 HW/check_iss247_f1_landed.py --selftest` ⇒ rc=0** (10 条反向用例 + 1 条正向全抓到 ⇒ 门禁不是摆设)
· ★**命中行 (main 读到)**: ★**L8** `net=VBUS_5V_F1 ref=C_VBUS_OUT` 的对端裸位号 = `C_VBUS_GND` · ★**L12** `net=VBUS_5V_CHG ref=C_VBUS_GND` 的对端裸位号 = `C_VBUS_OUT`
  ⇒ ⇒ ★**一颗 2 脚件落进 3 个网 = 导出后一脚悬空** (ISS-242 F1)
· ★**当前真源 md5 (main 实测)**: 网表 `611c3ba3db3dc7de7213063375b96d01` · 脚表 `ef436a37412ac9b6eac3c9f41f1edca4` · BOM `2a7305741134788dfee9f13f34c656b4` · 板 `611b869e13518c3c023fb178f91a0075` · `.kicad_pro` `3e504d2be83152e337949723e909be1b`

★★**② 改法 (★ISS-247 沙盒实测过, 行号以你本机 grep 为准★)** ★★
· ★**`state/gen_netlist.py`**: 两处 `add()` 的 ★**node2 槽** ★ 从「借用的别人的裸位号」改成「本行自己的网名」:
  · ★**L381** (FB_VBUS 后级行 / `C_VBUS_OUT`) ⇒ node2 = ★**`VBUS_5V_F1`** ★
  · ★**L393** (C_VBUS_GND 信号端行) ⇒ node2 = ★**`VBUS_5V_CHG`** ★
· ★★**两处缺一不可**: ISS-247 实测过 ★**改成 `C_VBUS_GND` 照样红** (C_VBUS_GND 被登记 3 次 > 脚数 2) ⇒ ★**必须改成各自的网名** ★
· ★**上一轮 brief 写的 L369/L381 与盘上现号不符 ⇒ 以本机 grep 为准** ★
· ★**预期 (ISS-247 沙盒值, 以你实跑为准)**: 网表 md5 `611c3ba3…` → `16ac89f7…`; ★**脚表 / BOM / 板 / `.kicad_pro` 逐字节不变** ★

★★**③ 落表链路 (★照抄 ISS-243 台账里的既有顺序, 不许自创★)** ★★
```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
# ★★开工前先留回滚副本: cp -a state/gen_netlist.py state/.bak_iss249/ (★含 HW/netlist_v1.csv 等生成物基线★)
python3 state/gen_netlist.py && python3 state/gen_kicad_net.py && \\
python3 state/gen_netlist_pins.py && python3 state/gen_bom.py && \\
python3 state/gen_schematic_pages.py && python3 state/gen_kicad_sch.py
```
★★**④ 必跑门禁 (★原样贴输出, 少一条即无效★)** ★★
```bash
python3 HW/check_iss247_f1_landed.py                # ★rc=0 (★本单的核心目标★)
python3 HW/check_iss247_f1_landed.py --selftest     # rc=0 (反向用例仍全过)
python3 HW/check_netlist_selfconsistency.py          # rc=0 (现状守卫)
python3 HW/check_netlist_selfconsistency.py --expect-resolved   # rc=1 是预期 (★条数不许上升; 下降更好★)
python3 state/check_netlist.py                      # rc=0
python3 state/check_netlist_pins.py                 # rc=0
python3 state/check_sch_erc.py                      # rc=0
python3 state/check_sch_pinfull.py                  # rc=0 (图上 584 脚 = 表里 584 脚 · K=0)
python3 HW/check_netlist_contradiction_r3.py        # rc=1 · ★恰 3 条 findings★ (F1 消失 ⇒ 剩 F2+F3; ★若条数变了照实说★)
python3 state/merge.py && python3 state/gate_check.py   # rc=0 · Q1 18/18
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro   # 611b869e… / 3e504d2b… ★逐字节不变★
```
★★**★反向自证 (必做★)**: 把那 2 行 node2 改回旧值 ⇒ ★**`HW/check_iss247_f1_landed.py` 必须重新红** ⇒ 装回 ⇒ 又绿 ⇒ ★**证明你真改了判据盯的东西, 不是把红灯调没** ★
★★**★落表台账 (新段, 写进 `HW/SCHEMATIC_LANDING_V1_LANDED.md`)★**: ★**单号 = `ISS-249`** ★ + 改了哪个真源哪一行 + 改前/改后字面值 + 新旧 md5 + 复现命令 + 证据等级 ★

★★**⑤ 交付物 (5 件, 少一件即无效)** ★★
① ★**落表台账新段** (上面⑤) ★
② ★**真源改动 + 重生成** ★ (★**不许手工编辑任何生成产物 CSV★**)
③ ★**门禁输出 (10 条命令原样)** + ★**反向自证三步** ★
④ ★**交接单 `HANDOFF/2026-11-16_hw-lead_ISS249_F1落表.md`** (★B1~B6 六块齐全★) + ★**分片 `state/fragments/hw.yaml`** (★必须走 `python3 state/frag_write.py` 原子写, ★不许 `open(p,"w")`★)
⑤ ★**H-1 重锚预告 + 板侧同步清单 (★只报告, 不许改板★)** ★
  · 你落表 ⇒ ★**网表 md5 必变** ⇒ ★**SW 侧 `SW/SW_MD5_BASELINE_LEDGER.md` §1 与 MECH 侧 `MECH/HW_CROSS_REVIEW_TRIAGE.md` §1 锚点会按设计变红** ⇒ ★**你只登记 need (含落表单号 + 新旧 md5 + 文件名), 不许自己动那两份台账 (那是 sw-lead / mech-lead 的地界)** ★
  · ★**板侧同步**: 本单改的是网表真源 ⇒ 板面要不要跟着动 (★只报告, 不许改板★) ⇒ 写进交接单
  · ★**下一批**: `HW/SCHEMATIC_LANDING_NEXT_BATCH_V1.md` 已写明 ★**内容撞车 0 / 行号漂移撞车 1 处 (V-3 删 DEMO_DNP 3 行 ⇒ F1 行号 -3) / md5 撞车 4 处 ⇒ 必须同批落** ★ ⇒ ★**你落完 F1 后, 请把下一批清单按【F1 已落】更新一版 (哪些行号漂移了 / 哪些 md5 撞车解除了)★** ★

★★**边界 (★越界即无效★)** ★★
· ★**不许碰板** (`HW/PCB/demo_mainboard.kicad_pcb` / `.kicad_pro` / 布线 / 布局 / 板框 一律不碰★) ⇒ ★**板侧 B-1~B-8 继续排队 (老板 11-11 10:07 口径)★**
· ★**不许落任何 V 值** (V-2 / V-3 / V-4 老板都没拍) ⇒ ★**本单只落 F1** ★
· ★**不许改判据阈值** (`HW/check_iss247_f1_landed.py` 的 S1~S6 判据 / `HW/check_netlist_selfconsistency.py` 的 EXPECT 一律不许为了变绿而放松★)
· ★**不改 `SW/` · 不改 `MECH/` · 不写别人的分片 · 不改 `state/issue_log.yaml` (status 留给 main 落 verified★) · 不改 `PROJECT_TRACKER.md` §0**
· ★**零外发** (★不发邮件 / 询价 / 问询 / 采购 / 原厂问询★) ⇒ 缺口一律【自己网上查】+ 标 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` + ★**查不到必须写降级方案** ★ ⇒ ★**没有"批一句可以发"这个选项** ★
· ★**实物 [实测] = 0 条** (板不在本机) ⇒ 标 [实测] 的只允许是「本机脚本 / 本机文件实读」 ★
· ★**时间纪律**: ① 先落真源 + 重生成 (跑一次就够) ② 再跑门禁 ③ 写台账 + 交卷单 ④ 写分片 ⑤ 贴验收输出交卷 ⇒ ★**交卷单骨架先落盘, 再逐段填 (不许攒到最后一次写)★** ★
"""

BRIEF_250 = """★★**目标 (★内部活·软件侧·★不是 PCB 布线/布局类·不是老板级拍板★)** ★★
★**把 ISS-155 这条【demo 头号卡点】从「等外部回复」变成【自己查出来的结论 + 证据等级 + 降级方案 + 板可达时的执行清单】** ★★
⇒ ★**目标状态: 一份查证表 (查了什么 / 去哪查 / 结论 / 证据等级) + ≥2 条降级方案 (各带量化代价) + 板端可达时的【一条命令 + 执行清单】+ 交接单 + 分片** ★★

★★**① 题面 (★ISS-155 · open · blocker · owner=main★)** ★★
★**「rk3572 不是 rknn-toolkit2 合法 target ⇒ 用 rk3576 target 转的 .rknn 能否在 RK3572 上跑通 (板端验证) —— 且板子当前不可达」** ★★

★★**② 已知事实 (★你上次交卷时自己实测写下的, 这次直接用★)** ★★
· ★**`SW/RKNN_BENCH.md` §5 只证过 target 列表【含 rk3576】** (证据: `rknn/api/rknn.py:89`) ⇒ ★**rk3572 在不在, 从来没验过** ★
· ★**核法 (你自己的原始记录)**: 构建机上 `python -c "from rknn.api import RKNN; print(RKNN.RKNN_TARGET_PLATFORM)"` + `grep rknn/api/rknn.py` ★
· ★**本机 (★main 与你本轮都实测过★)**: ★**没有 RKNN 工具链 / 没有源 ONNX / 没有 100 张校准集 / 没有 .rknn 产物** ⇒ ★**本机跑不了转换链** ★ ⇒ ★**板端也不可达** ⇒ ⇒ ★**"等板子" 不能当阻塞项** ★

★★**③ 硬口径 (★老板 2026-11-11 19:31 + 2026-11-12 02:02★)** ★★
★**「不再做任何邮件咨询」+「不再发信, 全靠自己查资料」** ⇒ ★**① 不许外发任何邮件 / 询价 / 问询 / 采购 / 原厂问询** ⇒ ★**② 凡标着「等原厂回信 / 待外部确认」的地方, 一律换成【自己查的结果 + 证据等级 + 查不到就写降级方案】** ⇒ ★**③ 证据等级固定五级: `[官网]` / `[实测]` / `[媒体]` / `[推算]` / `[0数据]`** ⇒ ★**④ 降级方案是必须项, 不是可选项** ★ ⇒ ★**没有"等老板批一句可以发"这个选项** ★

★★**④ 你要交的东西 (4 件 + 交卷, 少一件即无效)** ★★
① ★**查证表 (★机器可读的表都行, 但一行一条★)** ★
  ⇒ 每行: ★**要查的命题** (★例如「rknn-toolkit2 2.3.x 的 target_platform 是否含 rk3572」★) · ★**去哪查的** (★GitHub release notes / Rockchip 官方文档 / PyPI wheel 里的 `rknn/api/rknn.py` 字符串 / 官方 model zoo 目录★) · ★**结论** · ★**证据等级** · ★**原文摘录 (★能引一句就引★)**
  ⇒ ★**必须至少覆盖这 4 条**: ① rknn-toolkit2 各版本 target 列表里有没有 rk3572 ② 有没有「rk3576 转出来的 .rknn 在 RK3572 上跑得动」的官方说明或已知结论 ③ RK3572 的 NPU 与 RK3576 的差异 (★只写能查到的, 查不到标 [0数据]★) ④ 官方 model zoo 有没有 RK3572 预编译模型 (★有 ⇒ 就是降级方案的一条★)
② ★**降级方案 ≥2 条 (★每条带代价, 不许只写"换模型"三个字★)** ★
  ⇒ ★**每条格式: 方案 + 技术依据 + 代价 (★工作量 / 精度影响 / 是否要重新标定 / 是否阻塞首台板★) + 适用前提** ★
  ⇒ ★**候选 (不限定, 你自己查出来更准)**: 升级工具链版本 / 换模型路线 M2 (yolov5n@640, ★推算 52.91ms 那条口径在 `SW/RKNN_BENCH.md` 里★) / 芯片名映射写法 / 直接用官方预编译模型 / 改判据口径 (★demo 验收里到底有没有 60ms 那条 = 老板级, ★你只列选项不拍★)
③ ★**板端可达时的执行清单 (★本机现在跑不了, 所以必须写成【等人也能照做】★)** ★
  ⇒ ★**一条能跑的验证命令 (贴命令原文)** + ★**前置条件** (工具链版本 / 模型文件 / 板子怎么连 / 模型头 chip ID 怎么核) + ★**「跑通了」与「跑不通」的判据各是什么** + ★**失败时的下一步动作**
  ⇒ ★**不许写「等板子回来再说」这种话** ⇒ ★**写成【板可达 → 执行第 1 步 → 出这个读数 → 若不符 → 走第 2 步】★**
④ ★**交接单 `HANDOFF/2026-11-16_sw-lead_ISS250_rknn-toolkit2_RK3572_target查证与降级方案.md`** (★B1~B6 六块齐全★) + ★**分片 `state/fragments/sw.yaml`** (★必须走 `python3 state/frag_write.py` 原子写, ★不许 `open(p,"w")`★) + ★**给 main 的 need** (★若还有查不到又绕不开的点, 明确写清【还差什么 / 谁能解 / 阻塞的是哪一步】★)
⇒ ★**可选第 5 件 (★时间紧就跳过, 但跳过要在交卷单里写明并登记 need★)**: 一道机器门禁 (★判据: 查证表里每条都有证据等级 + 降级方案 ≥2 条 + 判据不许写「等回信」★) + `--selftest` 反向用例

★★**边界 (★越界即无效★)** ★★
· ★**不改 `HW/` · 不改 `MECH/` · 不改 `state/issue_log.yaml` (status 留给 main★) · 不改 `PROJECT_TRACKER.md` §0 · 不写别人的分片** ★
· ★**零外发** · ★**实物 [实测] = 0 条** (板不可达) ⇒ ★**别把推算写成实测** ★
· ★**不许替老板拍板**: demo 阶段到底挂不挂 60ms 门限 / 换不换模型路线 ⇒ ★**只列选项 + 量化代价 + 推荐默认值 (★推荐 ≠ 已决定★)** ★
· ★**不许改 `SW/tools/timing_check.py` / `SW/tools/check_demo_panel_spec.py` / `SW/tools/demo_e2e_budget.py` 这三道现有判据脚本** ★
· ★**不许碰 PCB 布线 / 布局 / 板框** ★
· ★**时间纪律**: ★**先落查证表骨架 → 再逐条填 → 再写降级方案 → 交卷单 → 分片 → 贴输出交卷** ⇒ ★**不许攒到最后一次写** ★
"""

BRIEF_251 = """★★**目标 (★内部活·结构侧·★不是 PCB 布线/布局类·不是老板级拍板★)** ★★
★**把 MECH 侧三处「只报不改 ⇒ 现在授权改」的老账一次收口** ⇒ ★**三处全部落在 MECH 自己的地界, 全部有机械判据, 全部不依赖任何外部回复** ★★
⇒ ★**目标状态: 三个文档/脚本口径逐条订正 (旧值 → 新值 → 文件 → 行号) + 一道机器门禁 (rc=0 且 `--selftest` 全过) + 交接单 + 分片** ★★

★★**① 三处老账 (★全部是你自己 (mech-lead) 登记给 main 的 need, main 本轮裁完派下来★)** ★★

**【A】充电耗散口径 (need `iss213_mech_mech_budget_charge_caliber_text`)** ★
· ★**现状**: `MECH/MECH_BUDGET.md` §2.1 写「**0.8 W @1A** (IC 自身耗散 = (5−4.2)V × 1A)」= ★**线性充电 IC 公式** ★
· ★**真相**: P10 充电板是 ★**开关型 buck** (网表有 `SW` / `L_CHG` / `C_BST` / `PMID`) ⇒ 耗散应按 ★**Pin − Pout + DCR = 0.45–0.57 W** ★
· ★**连带**: `MECH/verify_budget.py` 的 ★**`P_CHARGE` 常量** 一并订正 (★脚本里这个常量现在还在用旧值★)
· ★**为什么现在做**: 你在 ISS-213 里已明写「本单没改 (它牵 §2.3 皮肤热链与 §3 重量表, 不是我一个单能收的)」⇒ ★**本单授权你改这两处** ★
· ★**不许越界**: ★**§2.3 皮肤热链 / §3 重量表本单不许连带改** ⇒ 只改 §2.1 那一段 + 脚本常量, 并把「受影响的连带项」写成交接单里的清单交回 main ★

**【B】铝导热系数取保守侧 (need `iss218_mech_alu_k_201_vs_237`)** ★
· ★**现状**: `MECH/MECH_BUDGET.md` §3 与 `MECH/verify_budget.py` 用 ★**k = 237 W/m·K** ★
· ★**官方值**: 6063-T6 = ★**201 W/m·K** (Aalco/AA datasheet) ⇒ ★**现值乐观 18%** ⇒ 同几何热阻 R 从 ★**1.641 → 1.935 K/W** ★
· ★**结论方向一条没变** (金属热路仍然必须 / 打印件 1944 K/W 仍然出局) ⇒ ★**只把数换成保守侧, 不改判据** ★
· ★**授权**: ★**统一改成 201 + 同步脚本常量** ⇒ 改完在交接单里回一声 (★门禁锚点好对齐★) ★

**【C】检修口文档口径过期 (need `iss203_mech_service_port_doc_15mm_margin`)** ★
· ★**现状**: `MECH/SERVICE_PORT_ISS092.md` 仍是 ★**15mm 板宽口径** ⇒ §5.1 表 V PCB 段 需求 21.00 / 余 +17.00; §1.6.2 三条余量 0.95 / 17.00 / 14.50 ★
· ★**现行**: 60×30 (板宽 30.00) ⇒ V PCB 段 = ★**需求 36.00 / 余 +2.00 (最坏 +1.40, 单边口径 +1.70)** ★
· ★**做法**: ★**逐处订正文与表 (旧值 → 新值 + 行号), 不许只加一句「已作废」** ⇒ 并与 `MECH/BOARD_GEOM_30MM.md` §1/§3 逐字对齐 ★
· ★**不许越界**: ★**`MECH/service_port_check.py` 的夹具基准 / 焊盘阵列 Y / `pcb_thk` 属于别的单的地界** (★它们要等 main + hw-lead 定 30mm 板上的最终值★) ⇒ ★**本单只改文档, 不碰那个脚本的常量** ★

★★**② 交付物 (4 件, 少一件即无效)** ★★
① ★**三处逐条订正表** (★每条: 旧值 → 新值 + 文件 + 行号 + 证据等级 + 依据出处★)
② ★**`MECH/verify_budget.py` 常量同步 + 实跑输出前后对比** (★改前 / 改后各贴一遍, 差多少要能解释★)
③ ★**一道机器门禁 (★新建 `MECH/check_budget_caliber.py`★)** + ★**`--selftest` (★反向用例 ≥4 条: 改回旧口径 / 改数字 / 删依据出处 / 改文档数字 ⇒ 必须红★) ★
④ ★**交接单 `HANDOFF/2026-11-16_mech-lead_ISS251_MECH侧三处老账收口.md`** (★B1~B6 六块齐全★) + ★**分片 `state/fragments/mech.yaml`** (★必须走 `python3 state/frag_write.py` 原子写, ★不许 `open(p,"w")`★) + ★**给 main 的 need** (★连带项 / 待别人定的项, 逐条写清★)

★★**③ ★★并发告警 (★必读, 不读会误判自己失败★)★★** ★★
★**同一时刻 hw-lead 正在落表 ISS-249 (改网表真源) ⇒ 网表 md5 会变 ⇒ `MECH/check_demo_struct_truth.py` 的 G5b / C21 会【按设计变红】** ★
⇒ ★**那不是你的失败, 也不许你去修它** (★那是 H-1 重锚那一跳的活★) ⇒ ★**你只跑你自己 3 项的门禁 + `MECH/verify_budget.py`, 并在交卷单里写一行并发说明 (★写明「G5b/C21 红是并发落表导致, 非本单」★)** ★

★★**④ 边界 (★越界即无效★)** ★★
· ★**不许碰 `HW/` (★网表 / 脚表 / BOM / 板 / `.kicad_pro` 一个字节不许动★) · 不许碰板 / PCB 布线 / 布局 / 板框** ★
· ★**不许改 `MECH/check_demo_struct_truth.py` (★md5 `fa9b59e5…` 前后必须不变★) · 不许改 `MECH/service_port_check.py` · 不许改 `MECH/hinge_usb_check.py`** ★
· ★**不许替老板拍板**: d 值 (15/18/20) · u8 端件截面 · 集热面材质 / 面积 · 板长 · 板厚档位 ⇒ ★**一律只列选项 + 量化代价, 不代拍** ★
· ★**零外发** (★不发信 / 不询价 / 不问询 / 不采购★) ⇒ 缺口一律【自己网上查】+ 标 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` + ★**查不到必须写降级方案** ★
· ★**实物 [实测] = 0 条** (本机无量具/无打印机) ★
· ★**不改 `state/issue_log.yaml` (status 留给 main 落 verified★) · 不改 `PROJECT_TRACKER.md` §0 · 不写别人的分片** ★
· ★**时间纪律**: ① 三处订正各自先落盘再验 ② 门禁 + selftest ③ 交卷单 ④ 分片 ⑤ 贴输出交卷 ⇒ ★**不许攒到最后一次写** ★
"""

NEW_ISSUES = [
    {
        "id": "ISS-249",
        "title": "★★[主线内·原理图/网表侧·落表执行·内部活] ★★ISS-247 的 F1 落表作业包 → 真落进真源 (★`state/gen_netlist.py` 两行 node2: L381 `C_VBUS_OUT`→`VBUS_5V_F1` · L393 `C_VBUS_OUT`→`VBUS_5V_CHG`★) ⇒ 一颗 2 脚电容只落 2 个网 (★现在一颗落 3 个网 = 导出后一脚悬空★) ⇒ 重生成 6 件生成物 ⇒ `HW/check_iss247_f1_landed.py` 从 rc=1 转 rc=0 + 落表台账新段 (单号 ISS-249) + 反向自证 (★板零改动·不碰 V-2/V-3/V-4★)",
        "severity": "high",
        "source_blocker": "ISS-247",
        "source_agent": "main",
        "desc": "★main 2026-11-16 19:1x **自己实跑核出来的** (★不抄任何交卷报告★) ★\n"
                 "· ★**`python3 HW/check_iss247_f1_landed.py` ⇒ rc=1** (末行「判定: ❌ F1 未落表 (网表里 node2 槽仍借用了别的器件裸位号)」) · ★**`--selftest` ⇒ rc=0** (10 反向 + 1 正向全抓到 ⇒ 门禁不是摆设)\n"
                 "· ★**命中行**: L8 `net=VBUS_5V_F1 ref=C_VBUS_OUT` 的对端裸位号 = `C_VBUS_GND` · L12 `net=VBUS_5V_CHG ref=C_VBUS_GND` 的对端裸位号 = `C_VBUS_OUT` ⇒ ★**一颗 2 脚件落进 3 个网** (ISS-242 F1)\n"
                 "· ★**改法 (ISS-247 沙盒实测)**: `state/gen_netlist.py` L381/L393 的 node2 改成各自的网名 ⇒ ★**改成 `C_VBUS_GND` 照样红** (登记 3 次 > 脚数 2) ⇒ **两处缺一不可**\n"
                 "· ★**落表链路 / 10 条必跑门禁 / 落表台账格式** 全部照抄 ISS-243 台账里的既有顺序与口径\n"
                 "· ★**为什么现在派**: ISS-247 已 verified (作业包 + 下一批清单 + 新门禁三件齐) ⇒ ★**hw-lead 名额空出来** ⇒ ★**作业包不改真源就永远停在「规格」★ ⇒ 老板 11-11 10:07 主线 = 原理图 demo 绘制 ⇒ ★**本单是主线正中央的一步** ★",
        "owner": "hw-lead",
        "reporter": "main",
        "raised": TODAY,
        "due": "2026-11-20",
        "status": "open",
        "external": False,
        "need_keys": [],
        "fix_ref": None,
        "verify_by": "main",
        "verify_result": None,
        "verify_date": None,
        "note": "★main 2026-11-16 19:1x 开单 (job fb67af40「队列自动派活」): ★**本轮 advance.py 的 internal 段起初为空** (hw-lead ISS-247 / mech-lead ISS-246 / sw-lead ISS-248 各自 fixing, 但三条子会话实测全部 status=done 且交付物在盘) ⇒ ★**main 先把三条验收签字落 verified (自己实跑门禁), 再开本单** ⇒ ★**本单 = hw-lead 释放出来的名额上的原理图主线活 (★不是 PCB 类, 不违反老板 11-11 10:07 口径★)** ★\n"
             "★**边界**: 不碰板 / 不碰布线布局板框 · 不落 V-2/V-3/V-4 · 不改判据阈值 · 不改 SW/ 与 MECH/ · 零外发 · 不自签 issue_log ★",
        "task_brief": BRIEF_249,
    },
    {
        "id": "ISS-250",
        "title": "★★[主线内·SW 侧·demo 头号卡点·内部活] ★★ISS-155: 「rk3572 不是 rknn-toolkit2 合法 target ⇒ 用 rk3576 target 转的 .rknn 能否在 RK3572 上跑通 (板端验证) —— 且板子当前不可达」⇒ ★**不许挂「等板子 / 等回复」** ⇒ 自己查 (rknn-toolkit2 各版本 target 列表 / 官方 model zoo / Rockchip 文档) + 标证据等级 ([官网]/[实测]/[媒体]/[推算]/[0数据]) + ≥2 条降级方案 (各带量化代价) + 板可达时的【一条命令 + 执行清单】+ 交接单 + 分片",
        "severity": "high",
        "source_blocker": "ISS-155",
        "source_agent": "main",
        "desc": "★main 2026-11-16 19:1x 开单 (job fb67af40「队列自动派活」) ★\n"
                 "· ★**依据 = sw-lead 自己交卷时写下的 need `demo_od_p0_1_rk3572_target`**: `SW/RKNN_BENCH.md` §5 ★**只证过 target 列表含 rk3576** (证据 `rknn/api/rknn.py:89`) ⇒ rk3572 在不在从来没验过 ★\n"
                 "· ★**本机与板端都不可用** (need `demo_od_p0_3_build_env`: 无 RKNN 工具链 / 无源 ONNX / 无校准集 / 无 .rknn; 板子不可达) ⇒ ★**按老板 2026-11-11 19:31 + 2026-11-12 02:02: 「不再发信, 全靠自己查资料」⇒ 外部依赖不许挂着当阻塞项** ★\n"
                 "· ★**本单 = sw-lead 释放出来的名额上的软件类内部活 (★不是 PCB 类★)** ★",
        "owner": "sw-lead",
        "reporter": "main",
        "raised": TODAY,
        "due": "2026-11-20",
        "status": "open",
        "external": False,
        "need_keys": [],
        "fix_ref": None,
        "verify_by": "main",
        "verify_result": None,
        "verify_date": None,
        "note": "★main 2026-11-16 19:1x 开单 (job fb67af40「队列自动派活」): ★**本轮 advance.py 的 internal 段起初为空** (sw-lead ISS-248 fixing 但子会话已 done 且交付物在盘) ⇒ ★**main 先验收签字落 verified, 再开本单** ⇒ ★**本单 = sw-lead 名额释放出来的软件类活** ★\n"
             "★**外发口径 (★老板 2026-11-11 19:31 + 2026-11-12 02:02★)**: ★**零外发** ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到写降级方案 ⇒ ★**没有「等老板批一句可以发」这个选项** ★\n"
             "★**边界**: 不改 HW/ 与 MECH/ · 不改三道现有判据脚本 · 不许替老板拍板 (demo 是否挂 60ms 门限 / 换不换模型路线) · 板端实测 0 条 · 不自签 issue_log ★",
        "task_brief": BRIEF_250,
    },
    {
        "id": "ISS-251",
        "title": "★★[主线内·MECH 侧·口径收口·内部活] ★★mech-lead 自己登记给 main 的 3 条「只报不改 ⇒ 现在授权改」老账一次收口: ① `MECH/MECH_BUDGET.md` §2.1 充电耗散口径 (线性公式 0.8W@1A ⇒ 开关型 buck 0.45–0.57W) + `MECH/verify_budget.py` 的 `P_CHARGE` 常量 ② 铝导热 k 237⇒201 W/m·K (6063-T6 官方值, 同几何 R 1.641→1.935 K/W, 结论方向不变) + 脚本常量 ③ `MECH/SERVICE_PORT_ISS092.md` 15mm⇒60×30 口径 (V PCB 段 需求 21.00/余+17.00 ⇒ 36.00/余+2.00, 最坏+1.40) ⇒ 逐条订正 + 新门禁 + 交接单 + 分片",
        "severity": "medium",
        "source_blocker": "MECH-CALIBER",
        "source_agent": "main",
        "desc": "★main 2026-11-16 19:1x 开单 (job fb67af40「队列自动派活」) ★\n"
                 "· ★**三条全部是 mech-lead 登记给 main 的 need, 且都明写「本单没改, 请 main 派单 / 授权」**: `iss213_mech_mech_budget_charge_caliber_text` · `iss218_mech_alu_k_201_vs_237` · `iss203_mech_service_port_doc_15mm_margin` ⇒ ★**main 本轮逐条裁完 ⇒ 派成执行单** ★\n"
                 "· ★**三条都在 MECH 自己的地界** ⇒ 零跨域 · 零外部依赖 · 零老板级拍板 ★\n"
                 "· ★**并发告警**: 同时 hw-lead 在落 ISS-249 ⇒ 网表 md5 会变 ⇒ `MECH/check_demo_struct_truth.py` 的 G5b/C21 会按设计变红 ⇒ ★**不是本单失败, 本单不许去修它** ★\n"
                 "· ★**本单 = mech-lead 释放出来的名额上的结构类内部活 (★不是 PCB 布线/布局类★)** ★",
        "owner": "mech-lead",
        "reporter": "main",
        "raised": TODAY,
        "due": "2026-11-20",
        "status": "open",
        "external": False,
        "need_keys": [],
        "fix_ref": None,
        "verify_by": "main",
        "verify_result": None,
        "verify_date": None,
        "note": "★main 2026-11-16 19:1x 开单 (job fb67af40「队列自动派活」): ★**本轮 advance.py 的 internal 段起初为空** (mech-lead ISS-246 fixing 但子会话已 done 且 3 件补齐在盘) ⇒ ★**main 先验收签字落 verified, 再开本单** ⇒ ★**本单 = mech-lead 名额释放出来的结构类活** ★\n"
             "★**边界**: 不碰 HW/ 与板 · 不碰 `check_demo_struct_truth.py` / `service_port_check.py` / `hinge_usb_check.py` · 不替老板拍板 (d 值 / u8 / 集热面 / 板长 / 板厚) · 零外发 · 不自签 issue_log ★",
        "task_brief": BRIEF_251,
    },
]


def main() -> int:
    log = yaml.safe_load(open(LOG, encoding="utf-8")) or {}
    issues = log.setdefault("issues", [])
    by_id = {it.get("id"): it for it in issues}

    # ---- ① 验收签字 ----
    for iid, (vres, note_tail) in VERIFY.items():
        it = by_id.get(iid)
        if not it:
            print(f"⚠ {iid} 不在 issue_log ⇒ 跳过")
            continue
        if it.get("status") in ("verified", "closed", "deferred", "wontfix"):
            print(f"⚠ {iid} 已是 {it.get('status')} ⇒ 幂等跳过")
            continue
        it["status"] = "verified"
        it["verify_result"] = vres
        it["verify_by"] = "main"
        it["verify_date"] = TODAY
        it["note"] = (str(it.get("note") or "") + "\n" + note_tail).strip()
        print(f"✔ {iid} ⇒ verified")

    # ---- ② 新开 3 条 ----
    for new in NEW_ISSUES:
        iid = new["id"]
        if iid in by_id:
            print(f"⚠ {iid} 已存在 ⇒ 幂等跳过")
            continue
        issues.append(dict(new))
        print(f"＋ 新开 {iid} → {new['owner']}")

    # ---- 备份 + 原子替换 ----
    bak = LOG + ".bak_20261116_1915_verify_open249_250_251"
    shutil.copy2(LOG, bak)
    tmp = LOG + ".tmp_20261116_1915"
    with open(tmp, "w", encoding="utf-8") as f:
        yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=100000)
    os.replace(tmp, LOG)
    print(f"✔ 已写盘 (备份: {os.path.basename(bak)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
