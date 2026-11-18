#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_dispatch_round_20261112_0320.py —— ★★本 job (ARS45 继续执行后继计划) 03:2x 这一轮的三处落账★★

★★为什么这三件事必须做 (★实测, 不是推测★)★★:
  ① ★**ISS-205 改派 owner: hw-lead → sw-lead** (★不是乱塞, 三条硬依据全查过★)
     · ★**hw-lead 名额被 ISS-195 占着** —— 会话 `dc510f7c` 于 03:17:37 仍在写 (transcript mtime 03:17:37,
       `HW/iss121_mic_magnet_check.py` mtime 03:17:37) ⇒ ★**真在飞, 不是僵尸** ⇒ 铁律「一个 agent 同时只能
       一个写会话」⇒ 本单不能给 hw-lead ★
     · ★**而本单是 high severity + due 11-14 + 卡整链重出第 3 步 (重出原理图)** ⇒ 干等 hw-lead = 把最高优先级
       压在它自己队列的 medium 单 (ISS-199 / ISS-204) 后面 ⇒ ★**这是排队逻辑自己把主线堵住了** ★
     · ★**sw-lead 实测无在跑写会话** (`sessions_list`: sw-lead 最后一条子会话 02:30 done) ⇒ ★**零撞车** ★
     · ★**文件交集 = 0 (实测)**: ISS-205 只写 `state/gen_kicad_sch.py` + `HW/PCB/demo_mainboard*.kicad_sch`
       + `HW/PCB/PIN_REALITY_GAP.md` + `HANDOFF/` + 本分片; ISS-195 只写 `HW/iss121_mic_magnet_check.py/.json`
       + `HW/ISS121_MIC_MAGNET_POSITION.md` + `state/fragments/hw.yaml` ⇒ ★**交集为空** ★
     · ★**随之唯一的一处改动**: 分片写入目标 `hw.yaml` → `sw.yaml` (★**不许写别人的分片**★)
       ⇒ ★**其余判据 / 边界 / 验收一条都没动** ★
  ② ★**新开 ISS-206 → mech-lead** (★结构侧 J_CHG 旧口径一次性收口★)
     · ISS-202 (你 02:34 交卷) + ISS-203 (你 02:46 交卷) 各登记了 need 给 main ⇒ ★**main 已逐条裁完**
       (8 条 need → 6 条要做 + 2 条明令不许动) ⇒ ★**本单 = 裁完之后的执行单, 不再等下一轮** ★
     · ★**mech-lead 实测无在跑写会话** ⇒ 零撞车 ★
     · ★**它不是 PCB 布线/布局类** (★结构侧文档 + 检查器夹具口径 ⇒ 属「网表/脚本 = 唯一真源, 文档 = 镜像」★)
       ⇒ 符合老板 2026-11-11 10:07 的主线口径 ★
  ③ ★**ISS-122 `fixing` → `deferred`** (★陈旧标记清理★)
     · owner = main · ★**从来没有任何会话在跑它** (★`dispatched_at` = None ⇒ 它的 `fixing` 从来没对应过在飞会话★)
     · 它的 brief 要求「必须问 PCB 厂 DFM 报告」⇒ ★**老板 2026-11-12 02:02「不再发信」⇒ 这条路已封死** ★
     · 且它本身 = ★**BGA 逃线层数 = PCB 布局类** ⇒ 老板 10:07 口径 = 排队等原理图定稿 ★
     · ⇒ `fixing` 是**假状态** ⇒ 改 `deferred` (= 排队, 不是办完) ⇒ ★**deferred 不会被自动派出去 (守住口径)** ★

★★落盘纪律 (★项目既有范式★)★★:
  flock + 锁内重读 + yaml 往返逐字节自检 (width=200 实测匹配) + 原子写 + 逐条 diff 实测 + 备份

★★边界★★: 不改 C 段任何一条的建议默认值 · 不发邮件 · 不改 §0 锁死表 · 不写任何子总工的分片
"""
import fcntl
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import yaml  # noqa: E402

LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
BAK = LOG + ".bak_dispatch_20261112_0320"
WIDTH = 200

# ---------------------------------------------------------------- ISS-205 改派
NOTE_205 = (
    "\n\n★**【2026-11-12 03:2x 项目总工改派: owner `hw-lead` → `sw-lead`】**\n"
    "★**依据 (★三条全查过, 不是推测★)**:\n"
    "  ① ★**hw-lead 名额被 ISS-195 占着** —— 会话 `dc510f7c` 于 03:17:37 仍在写 (transcript mtime 03:17:37,\n"
    "    `HW/iss121_mic_magnet_check.py` mtime 03:17:37) ⇒ ★**真在飞, 不是僵尸** ⇒ 铁律「一个 agent 同时只能\n"
    "    一个写会话」⇒ 本单不能给 hw-lead ★\n"
    "  ② ★**本单是 high severity + due 11-14 + 卡整链重出第 3 步 (重出原理图)** ⇒ 干等 hw-lead = 把最高优先级\n"
    "    压在它自己队列的 medium 单 (ISS-199 / ISS-204) 后面 ⇒ ★**是排队逻辑自己把主线堵住了** ★\n"
    "  ③ ★**sw-lead 实测无在跑写会话** (`sessions_list`: sw-lead 最后一条子会话 02:30 done) ⇒ ★**零撞车** ★\n"
    "★**文件交集实测 = 0**: 本单写 `state/gen_kicad_sch.py` + `HW/PCB/demo_mainboard*.kicad_sch` +\n"
    "`HW/PCB/PIN_REALITY_GAP.md` + `HANDOFF/` + 本分片; ISS-195 只写 `HW/iss121_mic_magnet_check.py/.json` +\n"
    "`HW/ISS121_MIC_MAGNET_POSITION.md` + `state/fragments/hw.yaml` ⇒ ★**交集为空** ★\n"
    "★**随之唯一的一处改动**: 分片写入目标从 `state/fragments/hw.yaml` 改成 `state/fragments/sw.yaml`\n"
    "(★**不许写别人的分片**★) ⇒ ★**其余判据 / 边界 / 验收一条都没动** ★"
)

BRIEF_205_HEADER = (
    "★**【owner 已于 2026-11-12 03:2x 由 main (项目总工) 改派: `hw-lead` → `sw-lead`】**\n"
    "  · ★**原因**: hw-lead 名额被 ISS-195 (★真在飞, 会话 `dc510f7c`, 03:17 仍在写★) 占住 ⇒ 铁律「一个 agent 同时只能\n"
    "    一个写会话」⇒ 本单不能给 hw-lead; ★**而本单是 high + due 11-14 + 卡整链重出第 3 步** ⇒ 干等会把最高优先级\n"
    "    压在 medium 队列后面 ⇒ sw-lead 实测无在跑写会话 ⇒ 改派 sw-lead;\n"
    "  · ★**冲突已核**: 与在飞的 ISS-195 文件交集 = 0;\n"
    "  · ★**随之唯一的一处改动**: 分片写入目标从 `state/fragments/hw.yaml` 改成 `state/fragments/sw.yaml`\n"
    "    (★**不许写别人的分片**★) ⇒ ★**其余判据 / 边界 / 验收一条都没动** ★\n\n"
)

# ---------------------------------------------------------------- ISS-122 退队
NOTE_122 = (
    "\n\n★**【2026-11-12 03:2x 项目总工改状态: `fixing` → `deferred` (= 排队, 不是办完)】**\n"
    "★**依据 (★先说事实, 再说结论★)**:\n"
    "  ① ★**本单从来没有任何在飞工作** —— `dispatched_at` = None ⇒ ★**它的 `fixing` 标记从来没对应过任何会话**\n"
    "    (★owner = main, 没有子 agent 会话★) ⇒ 这是**假状态** ★\n"
    "  ② ★**它的结论前提已被两条政策封死**: brief 要求「必须问 PCB 厂 DFM 报告」⇒ ★**老板 2026-11-12 02:02\n"
    "    「不再发信, 全靠自己查资料」⇒ 这条路已封死**; 且它本身 = ★**BGA 逃线层数 = PCB 布局类** ⇒\n"
    "    ★**老板 2026-11-11 10:07 口径: PCB 布线/布局类一律排队等原理图定稿** ★\n"
    "  ③ ★**它没有卡住任何名额** (owner=main 不在 `advance.py` 的 AGENT_ROLE 里) ⇒ ★**改状态不影响派活**,\n"
    "    但它会让「在飞清单」长期挂一条不存在的活 ⇒ ★**清掉才是真账** ★\n"
    "★**deferred 的三条后果都查过**: ① `advance.py` 直接跳过 deferred ⇒ ★**不会被自动派出去**\n"
    "  (守住「PCB 类不派」) ② ★**G1 仍卡**: G1 判据读 `HW/PCB/.layout_done.json` 的 unc=45, **不读 issue 状态**\n"
    "  ⇒ ★**「不许投板」的口径一点没松** ③ ★**G4「问题单未闭环」清单仍会列出本单** ⇒ ★**没藏账** ★\n"
    "★**恢复条件 (写死, 免得又被当成已办)**: ① 老板拍板走**整链重出** (`state/RECHAIN_ONEPASS_PLAN.md` §5)\n"
    "  ⇒ PCB 线重启 ⇒ ② 届时按 ★**「自己查资料」** 政策做: 公开的 PCB 厂设计指南 / DFM 公开资料 +\n"
    "  `[官网]`/`[媒体]` 证据等级 ⇒ ★**查不到就写 `[0数据]` + 已知缺口 + 降级方案** ⇒ ★**不许再把「等一句\n"
    "  可以发」当成选项** ★\n"
    "★**唯一会变的数字**: 逾期未闭环会 −1 (C4 规则「deferred 不算逾期」) ⇒ ★**这是口径纠正, 不是活干完了** ★"
)

# ---------------------------------------------------------------- ISS-206 新单
ISS_206 = {
    "id": "ISS-206",
    "title": "★★[主线内·接口契约侧·内部活] ★★结构侧 J_CHG 旧口径一次性收口 (★第 3 套 pin map `8p@0.5` +\n"
             "11 处文档旧口径 + 3 份文档 + 板长 claim 69/76 + SERVICE_PORT 15mm 口径 + pcb_thk 0.80 +\n"
             "脚本 `RECOMMENDED_PINS[\"J_CHG\"]=8`★) ⇒ 按「网表/脚本 = 唯一真源, 文档 = 镜像」一次做完 ★★",
    "severity": "medium",
    "source_blocker": "MECH-JCHG-PINMAP-3SET",
    "source_agent": "main",
    "desc": "★2026-11-12 03:2x 项目总工开单 (★依据 = ISS-202 (02:34 交卷) + ISS-203 (02:46 交卷) 各登记给\n"
            "main 的 need, **main 已逐条裁完**★)。\n"
            "★**为什么现在做 (★实测, 不是推测★)**:\n"
            "  · ★**ISS-202 与 ISS-203 各登记了 7 条 need 给 main** ⇒ ★**它们都卡在「等 main 裁」这一步**\n"
            "    ⇒ 本单 = ★**裁完之后的一次性执行单** ⇒ ★**结构侧不用再等下一轮才能收口** ★\n"
            "  · ★**问题的性质 = 【同一个接口不许再有第 3 套 pin map】** ⇒ ★**这正是主线要求的\n"
            "    「网表 = 唯一真源, 文档是它的镜像」在结构侧的最后一截** ⇒ ★**不是 PCB 布线/布局类** ★\n"
            "  · ★**真源 (★main 已逐脚对拍过, 你自己也要再复算一遍★)**:\n"
            "    ★**`pin1/2=BAT_CHG` · `pin3/4=GND` · `pin5=CHG_STAT` · `pin6=PWR_GOOD` · `pin7=NC`\n"
            "    · `pin8=TS_BAT` · `pin9/10=HINGE_RSV`** ★\n"
            "    ★**依据**: `HW/netlist_v1.csv` 逐脚 net 名 + `HW/CHARGE_BOARD_SPEC.md` §5.2 (★ISS-136 已定版★)\n"
            "  · ★**结构侧现在还藏着第 3 套 pin map**: `MECH/USB_HINGE_STRUCTURE.md` §9 的 `mech_j_chg_pins`\n"
            "    仍写 `8p@0.5mm` ⇒ ★**与本分片 claim `mech_j_chg_pins` 的 value `10p@0.5mm` 直接矛盾** ⇒\n"
            "    ⇒ ★**同一个接口, 结构侧文档里有两套, 分片里还有一套** ★\n"
            "  · ★**注意一条容易踩的坑**: ★**`VBUS_DET` 这个网没废** (网表里还有 9 处, 主板本地分压),\n"
            "    废的是「VBUS_DET 跨铰链走 J_CHG pin7/pin8」这句话 ⇒ ★**订正时只改「走哪一脚 / 是否跨铰链」,\n"
            "    不许把 VBUS_DET 本地分压的描述一起删掉** ★",
    "owner": "mech-lead",
    "reporter": "main",
    "raised": "2026-11-12",
    "due": "2026-11-13",
    "status": "open",
    "external": False,
    "need_keys": [],
    "fix_ref": "",
    "verify_by": "main",
    "verify_result": None,
    "note": "",
    "task_brief": (
        "★**目标**: ★**把结构侧剩下的 J_CHG 旧口径一次性收口到真源** ⇒ ★**同一个接口不许再有第 3 套 pin map** ★\n\n"
        "★**为什么现在做 (★main 2026-11-12 03:2x 实测, 不是推测★)**\n"
        "· ★**ISS-202 (你 02:34 交卷) 与 ISS-203 (你 02:46 交卷) 各登记了 7 条 need 给 main** ⇒ ★**它们全卡在\n"
        "  「等 main 裁」** ⇒ ★**main 已逐条裁完 (★下面的【main 裁决】段就是裁完的结果★) ⇒ ★**本单 = 裁完之后\n"
        "  的一次性执行单** ⇒ ★**你不用再等下一轮★** ★\n"
        "· ★**真源 (★main 已逐脚对拍过; ★**你自己也要再复算一遍并写清依据★, 不要照抄题单★)**:\n"
        "  ★**`pin1/2=BAT_CHG` · `pin3/4=GND` · `pin5=CHG_STAT` · `pin6=PWR_GOOD` · `pin7=NC` · `pin8=TS_BAT`\n"
        "  · `pin9/10=HINGE_RSV`** ★\n"
        "  ★**依据**: `HW/netlist_v1.csv` 逐脚 net 名 + `HW/CHARGE_BOARD_SPEC.md` §5.2 (★ISS-136 已定版★)\n"
        "· ★**一条容易踩的坑 (★别删错★)**: ★**`VBUS_DET` 这个网没废** (网表里还有 9 处, 主板本地分压)\n"
        "  ⇒ ★**废的是「VBUS_DET 跨铰链走 J_CHG pin7/pin8」这句话** ⇒ ★**订正时只改「走哪一脚 / 是否跨铰链」,\n"
        "  不许把 VBUS_DET 本地分压的描述一起删掉** ★\n\n"
        "★**★★【main 裁决】(★8 条 need 逐条裁完 ⇒ 6 条要做 + 2 条明令不许动★)★★**\n"
        "★**裁 1 (要改)**: `MECH/hinge_usb_check.py` 第 77 行 `RECOMMENDED_PINS[\"J_CHG\"] = 8` ⇒ ★**改成 10**,\n"
        "  ★**注释里的老 6 脚期拆脚说法 (「SYS×2(载流) + VBUS_DET + BAT_DET + CHG_STAT + PWR_GOOD + GND×2」)\n"
        "  一并改掉** ⇒ ★**注释里不许再出现 SYS 跨铰链 / VBUS_DET 跨铰链 / BAT_DET 跨铰链**\n"
        "  (★**SYS 根本不跨铰链, VBUS_DET 是主板本地分压, BAT_DET 镜脚本地**★)\n"
        "  ★**判据**: ★**改前 / 改后两套跑法输出都要贴** (`python3 MECH/hinge_usb_check.py`) ⇒ ★**若改后有\n"
        "  PASS→FAIL ⇒ 那是几何事实 (10 脚比 8 脚宽), 如实贴, ★不许调阈值/判据掩盖★** ⇒ ★**若 FAIL→PASS ⇒\n"
        "  必须说清根因是不是 pin 数本身** ★\n"
        "★**裁 2 (要改)**: `MECH/USB_HINGE_STRUCTURE.md` 里那 ★**11 处 + §5.2 F-3 的 8p**\n"
        "  (★完整清单见你登记的 need `iss202_mech_doc_residual_jchg_old_6pin`★) ⇒ ★**文字口径全部按 10p 真源改**\n"
        "  (★脚数 6p/8p → 10p · pin map · 跨铰链归属 · 防呆措辞 · 反插风险描述★)\n"
        "  ★**★但几何数字不许手算★** ⇒ ★**`49.62 mm` / `24.00 mm` / `25.62 mm` 这三个数一律以\n"
        "  `python3 MECH/hinge_usb_check.py` 跑出来的输出为准** (★它是机器可查的那一份, 文档只做镜像★) ⇒\n"
        "  ★**§3.2b 声明版行 / 收敛版行 / §7 占位行 / §9 claim 注 / §5.3 C-4 算式行, 五处引用同一组数 ⇒ 必须一致**\n"
        "  (★C-4 行现在自相矛盾: 上格已写 1×10p, 算式还是 8+20+4+8=40脚/24.0mm★)\n"
        "  ★**★两套算式的差异, main 已裁 (照这个写, 别自己另发明一套★)★**: ★**【收敛版堆叠占位】以脚本算式为准;\n"
        "  【触点区】以行内算式为准** ⇒ ★**文档里按【触点区 21.0 mm / 堆叠 25.0 mm】写, 并加一句注记说明两套算式的\n"
        "  connectors 组成不同 (脚本 16+20+4+10=50脚@0.5=25.0mm; 行内 8+20+4+10=42脚@0.5=21.0mm 触点区 +\n"
        "  4×1.0mm 间隙 = 25.0mm 堆叠) ⇒ ★**两套算式最终都落在 25.0 mm 堆叠, 差的只是【触点区】那一格** ★ ★\n"
        "★**裁 3 (要改)**: `MECH/FPC_FAB_NOTES.md` (★N-6 · I-5★) + `MECH/RELIABILITY_TEST_PLAN.md`\n"
        "  (★R10 · §T-14 失效模式 · T-14 判据 · K-11 · K-12★) + `MECH/STRUCT_REVIEW_ISS065.md` (★R3★)\n"
        "  ⇒ ★**只改 pin map / 跨铰链归属 / 防呆措辞, 不改任何几何数字** ★\n"
        "  ★**★T-14 的判据本身必须改 (★本单最要紧的一处★)★**: ★**现行 10p 下反插 (pin i ↔ pin 11-i) 的真实风险\n"
        "  = `GND(pin3) ↔ TS_BAT(pin8)` 短 + `CHG_STAT(pin5) ↔ PWR_GOOD(pin6)` 短; 而 `BAT_CHG(pin1/2)` 落到\n"
        "  `HINGE_RSV` 预留脚 = 【断路】, 不是短接** ⇒ ★**旧文写的「反插 = SYS 短接 GND = MOS 直通」已作废**\n"
        "  ⇒ ★**新判据写成: 反插位型下 BAT_CHG 对 HINGE_RSV 为断路 (不得导通); GND↔TS_BAT 与 CHG_STAT↔PWR_GOOD\n"
        "  各自成短 (必须由防呆阻断)** ⇒ ★**防呆仍必需, 但理由换了** ★\n"
        "★**裁 4 (要改)**: `MECH/SERVICE_PORT_ISS092.md` 正文 15mm 口径 → 现行 60×30 口径\n"
        "  (★V PCB 段: 需求 `21.00` → `36.00`, 余 `+17.00` → `+2.00` (最坏 `+1.40`, 单边口径 `+1.70`);\n"
        "  §1.6.2 三条余量 `0.95/17.00/14.50` → 按现行重算★) ⇒ ★**数字以 `python3 MECH/service_port_check.py`\n"
        "  的输出为准, 不许手算** ★ (★**顺序: 先做裁 5 (板厚 0.80→1.00), 再跑脚本取数填裁 4★)\n"
        "★**裁 5 (要改)**: `MECH/service_port_check.py` 的 `pcb_thk = 0.80` (★4 层口径★) → ★**`1.00`**\n"
        "  (★6 层现行, `MECH/BOARD_GEOM_30MM.md` §1★) ⇒ ★**H 链需求 `4.20` → `4.40`, 余 `+3.10` → `+2.90`\n"
        "  (仍 > 判据 0.60)★ ★\n"
        "★**裁 6 (要改·但有一道闸)**: 本分片 `interface_claims` 的 `mainboard_len_carrier = 69mm` /\n"
        "  `mainboard_len_direct = 76mm` ⇒ ★**板长现行值 = `60.00mm`** (★`MECH/BOARD_GEOM_30MM.md` §1 +\n"
        "  打印包 `MECH/print/gen_print_pack_revb.py:85` 的 `pcb_len = 60.00` + 该文件 §7 的【作废值】表明确含\n"
        "  「板长 76」「板长 50」★) ⇒ ★**授权把这两条 claim 的板长取值订正到 60.00mm + 注明来源** ★\n"
        "  ★**★但有一个例外, 不许擅自改 (★main 特意留的闸★)★**: ★**若这两条 claim 描述的是【两种互斥方案】的板长\n"
        "  (载板化方案 vs 直接焊方案), 而不是【同一块板的两个口径】 ⇒ 那不是数值订正, 是【方案取舍】, 属老板级\n"
        "  ⇒ ★**这种情况下: 只报不改 + 登记 need 给 main** ⇒ ★**怎么判? 看 claim 语义 + 同一文件里是否还有别的\n"
        "  60.00 板长取值 ⇒ 你自己复算后写清依据, 别猜★** ★\n"
        "★**裁 7 (★明令不许动·只许加注记★)**: `MECH/service_port_check.py` 的夹具基准 `p2_y = 7.50` /\n"
        "  `s2_y = 12.50` / `jd_y0 = 9.50` ⇒ ★**不许改数字★** ⇒ ★**理由 (★main 踩过的坑★)**: 现行套 A =\n"
        "  `P2(52.00,15.00)` / `S2(52.00,20.00)`, ★**但脚本 7.4 式的符号/系数是按旧基准写的 ⇒ 只换数字会让\n"
        "  公式反过来 ⇒ 造出【假红】★** ⇒ ★**本单只许加一行注记, 标明【这套夹具基准已作废, 现行基准见\n"
        "  BOARD_GEOM_30MM.md §1】⇒ 真正的迁移留到整链重出 (公式与基准一起迁)★** ★\n"
        "★**裁 8 (★明令不许动·只报★)**: `MECH/hw_cross_review_check.py` 的 `soc_escape_x = (20.20, 31.80)` /\n"
        "  `hole_x = (5.00, 15.00, 55.00)` ⇒ ★**不许改★** ⇒ ★**理由**: ★**① 老板 2026-11-11 10:07 口径:\n"
        "  PCB 布线/布局类一律排队等原理图定稿; ② 主控已从 RK3576 换成 RK3572 ⇒ 逃线带本身要重算 ⇒ 属整链重出的\n"
        "  一步★** ⇒ ★**只报不改 (★登记 need 给 main★) ★\n\n"
        "★**★★验收自证 (交卷前跑, 把输出贴进回复)★★**\n"
        "```\n"
        "python3 MECH/hinge_usb_check.py        # ★改前/改后两套输出都要贴★\n"
        "python3 MECH/service_port_check.py     # rc=0\n"
        "python3 MECH/hw_cross_review_check.py  # ★不许因本单变红 (裁 8 不许动它的理由之一)★\n"
        "python3 state/merge.py                 # rc=0\n"
        "python3 state/gate_check.py            # rc=0, 【Q1】必须 18/18\n"
        "grep -rn '8p@0.5\\|8p @0.5\\|1×6@1.27\\|1×6 1.27' MECH/ | head -40\n"
        "md5sum HW/netlist_v1.csv HW/PCB/demo_mainboard.kicad_pcb\n"
        "```\n"
        "★**md5 期望**: 网表 `c78f991283cc82d56c8e3dd31657c785` · 板 `611b869e13518c3c023fb178f91a0075`\n"
        "  ⇒ ★**两者必须一字未变** ★\n"
        "★**`grep` 的期望**: ★**允许剩下【历史沿革】与【已作废注记】里的提及, 但不许有【当前口径断言】里的\n"
        "  8p / 1×6@1.27 ⇒ 逐行看, 说不清哪一行属于哪一类 = 没做完** ★\n\n"
        "★**交卷 (≤10 行)**: ① 逐条列出 6 个「要改」改了哪些处 (改前 → 改后) ② `hinge_usb_check.py` 改前/改后两套\n"
        "  输出 ③ 两个脚本的汇总 (PASS/FAIL/条件 各多少) ④ md5 未变实测 ⑤ 裁 6 你最后改没改 (依据是什么)\n"
        "  ⑥ 裁 7 / 裁 8 你怎么处理的 + 还剩哪些 need ★\n\n"
        "★**边界 (不许越)**\n"
        "· ★**只写**: `MECH/hinge_usb_check.py` (★只许动第 77 行 `RECOMMENDED_PINS[\"J_CHG\"]` + 它的注释★) ·\n"
        "  `MECH/USB_HINGE_STRUCTURE.md` (★只许动 J_CHG 相关的 pin 口径 + §3.2b/§5.3 C-4/§7/§9 的堆叠数★) ·\n"
        "  `MECH/FPC_FAB_NOTES.md` (★只许动 N-6/I-5★) · `MECH/RELIABILITY_TEST_PLAN.md` (★只许动\n"
        "  R10/§T-14/K-11/K-12★) · `MECH/STRUCT_REVIEW_ISS065.md` (★只许动 R3★) ·\n"
        "  `MECH/SERVICE_PORT_ISS092.md` (★只许动 §1.6.2 + §5.1 表 V PCB 段★) · `MECH/service_port_check.py`\n"
        "  (★只许动 `pcb_thk` + 加一行基准作废注记★) · ★**只许新增/改写** 本分片 `state/fragments/mech.yaml` 里\n"
        "  ★**裁 6 那两条 claim** 与 ★**本单相关的 need/artifact 条目** (走 `state/frag_write.py`·**不许删改别人的 key**★) ·\n"
        "  `HANDOFF/` 交卷报告\n"
        "· ★**不许碰**: `HW/**` (★那是 hw-lead 的地界★) · `state/gen_*.py` · `state/issue_log.yaml`\n"
        "  (★**改 issue 状态是 main 的活**★) · `PROJECT_TRACKER.md` §0 · **别人的分片**\n"
        "  (★`state/fragments/{hw,sw,pm}.yaml` 一律不许写★) · `MECH/print/**` · `MECH/BOARD_GEOM_30MM.md`\n"
        "  (★现行几何真源, 只读★)\n"
        "· ★**不许发任何邮件 / 询价 / 问询 (★老板 2026-11-12 02:02: 不再发信, 全靠自己查资料★) ⇒ 所有资料一律\n"
        "  【自己网上查】+ 标证据等级 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` ⇒ ★**查不到就写 `[0数据]` +\n"
        "  已知缺口 + 降级方案 ⇒ 没有「批一句可以发」这个选项** ★\n"
        "· ★**不许改判据阈值 (★`judge/CRIT 0.60` / `cav_v 38.00` / `duct_v 6.00` 一律不动★) ⇒ 放宽判据 = 负收益 ★\n\n"
        "★**★最后一条纪律 (★今天学的, 别踩★)★**: ★**「改完还是 FAIL」不许靠调阈值变绿** ⇒ ★**本单的\n"
        "PASS/FAIL 分布只允许因为【真源变了 (8p→10p / 板厚 0.80→1.00 / 板宽 15→30)】而变, 不许因为【判据松了】\n"
        "而变** ⇒ ★**交卷时要写清每个数字变化属于哪一类** ★"
    ),
    "dispatched_at": "",
    "fixed_at": "",
}


def dump_atomic(text, path):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
    dfd = os.open(os.path.dirname(path), os.O_RDONLY)
    try:
        os.fsync(dfd)
    finally:
        os.close(dfd)


def main() -> int:
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        raw = open(LOG, encoding="utf-8").read()
        doc = yaml.safe_load(raw)
        if yaml.safe_dump(doc, allow_unicode=True, sort_keys=False,
                          default_flow_style=False, width=WIDTH) != raw:
            print("❌ yaml 往返不一致 (width=%d) ⇒ 中止" % WIDTH)
            return 2
        items = doc.get("issues") or []
        before = {it.get("id"): dict(it) for it in items}

        # ★幂等守卫: 已应用过就不要再写一遍 (★上一轮跑完时最后一条自证炸了, 但落盘已完成★)
        _by_id = {it.get("id"): it for it in items}
        if (_by_id.get("ISS-205") or {}).get("owner") == "sw-lead" and "ISS-206" in _by_id \
                and (_by_id.get("ISS-122") or {}).get("status") == "deferred":
            print("ℹ️ 本轮三处落账【已应用】⇒ 不再写 (幂等守卫)")
            print("   ISS-205 owner=%s · ISS-122 status=%s · ISS-206 存在"
                  % (_by_id["ISS-205"]["owner"], _by_id["ISS-122"]["status"]))
            return 0

        hit205 = hit122 = 0
        for it in items:
            iid = it.get("id")
            if iid == "ISS-205":
                assert it.get("status") == "open", "ISS-205 状态已变 ⇒ 中止"
                assert it.get("owner") == "hw-lead", "ISS-205 owner 已变 ⇒ 中止"
                it["owner"] = "sw-lead"
                brief = it.get("task_brief") or ""
                n_hw = brief.count("state/fragments/hw.yaml")
                assert n_hw >= 1, "ISS-205 brief 里没有 hw.yaml ⇒ 中止 (口径变了?)"
                brief = brief.replace("state/fragments/hw.yaml", "state/fragments/sw.yaml")
                assert "fragments/hw.yaml" not in brief, "ISS-205 brief 仍有 fragments/hw.yaml ⇒ 中止"
                print("   ℹ️ ISS-205 brief: 分片写入目标 hw.yaml → sw.yaml (改 %d 处)" % n_hw)
                it["task_brief"] = BRIEF_205_HEADER + brief
                it["note"] = (it.get("note") or "") + NOTE_205
                hit205 += 1
            elif iid == "ISS-122":
                assert it.get("status") == "fixing", "ISS-122 状态已变 ⇒ 中止"
                it["status"] = "deferred"
                it["note"] = (it.get("note") or "") + NOTE_122
                hit122 += 1
        assert hit205 == 1 and hit122 == 1, "目标单未唯一命中 ⇒ 中止"

        if any(str(i.get("id")) == "ISS-206" for i in items):
            print("ℹ️ ISS-206 已存在 ⇒ 不新增")
        else:
            items.append(ISS_206)

        text = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False,
                              default_flow_style=False, width=WIDTH)
        # 自证: yaml 往返两次一致
        a = yaml.safe_load(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False,
                                           default_flow_style=False, width=WIDTH))
        b = yaml.safe_load(yaml.safe_dump(a, allow_unicode=True, sort_keys=False,
                                           default_flow_style=False, width=WIDTH))
        if yaml.safe_dump(a, allow_unicode=True, sort_keys=False,
                          default_flow_style=False, width=WIDTH) != \
           yaml.safe_dump(b, allow_unicode=True, sort_keys=False,
                          default_flow_style=False, width=WIDTH):
            print("❌ yaml 往返不一致 ⇒ 放弃写")
            return 1

        shutil.copy2(LOG, BAK)
        dump_atomic(text, LOG)

        # 自证: 除三条外, 其余 issue 逐字段零变化
        after_doc = yaml.safe_load(open(LOG, encoding="utf-8").read())
        after = {it.get("id"): dict(it) for it in (after_doc.get("issues") or [])}
        assert set(before) == set(after) - {"ISS-206"}, "issue 集合变化异常 ⇒ 中止"
        changed = [iid for iid in before if before[iid] != after[iid]]
        assert sorted(changed) == ["ISS-122", "ISS-205"], changed
        a205 = after["ISS-205"]
        assert a205["owner"] == "sw-lead" and "state/fragments/sw.yaml" in a205["task_brief"]
        # ★抬头说明里本就提到 hw.yaml (「从 hw.yaml 改成 sw.yaml」) ⇒ 只查【正文段】
        _body = a205["task_brief"].split("】**", 1)[-1]
        assert "fragments/hw.yaml" not in _body, "ISS-205 正文段仍有 fragments/hw.yaml ⇒ 中止"
        assert after["ISS-122"]["status"] == "deferred"
        print("✅ 落账完成: 改动 issue =", sorted(changed), "+ 新增 ISS-206")
        print("   ISS-205: owner hw-lead → sw-lead (hw-lead 真在飞 ISS-195 ⇒ 铁律; brief 分片目标改 sw.yaml)")
        print("   ISS-122: fixing → deferred (陈旧标记; PCB 类排队 + 外发已禁)")
        print("   ISS-206: 新开 → mech-lead (结构侧 J_CHG 旧口径一次性收口, 8 条 need 已裁)")
        print("   其余 %d 条 issue 逐字段零变化 (已实测) · 备份 %s"
              % (len(before) - 2, os.path.basename(BAK)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
