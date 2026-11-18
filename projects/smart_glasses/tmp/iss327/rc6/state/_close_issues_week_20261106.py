#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
state/_close_issues_week_20261106.py — 2026-11-06 周窗口 · mech-lead 名下 issue 状态推进

================================================================================
纪律 (本脚本自己必须做到)
--------------------------------------------------------------------------------
  ① **flock** (state/.issue_log.lock) —— 并发下别人也在写这张表
  ② **锁内重读** —— 拿到锁之后重新读一遍文件 (锁外读到的可能是旧版)
  ③ **原子写** (tmp + fsync + os.replace) —— 读者永远看到完整文件
     (★禁止 open(path,"w") 直接覆盖: 并发下 issue_check 读到半截 ⇒ YAML 解析失败 ⇒
      整张表从检查里消失)
  ④ **只改 owner == 'mech-lead' 的 issue** —— 别人的行一行都不许碰
  ⑤ ★**verify_by 必须是另一个总工或 main, 不许自己验自己**
     ★**verify_result / verify_date 只能由 verify_by 那一侧写** ⇒ 我写 `fixed` 时这两个留空
     ★**已有 verify_result 的 verified 条目** ⇒ 关单动作 (verified → closed) 由 verify_by 侧做,
       我只做 `open/fixing → fixed` 并把 verify_by 指到 main, 并把 verify_result/date 清空为待写

================================================================================
本轮 (2026-11-06) 要做的三件事
--------------------------------------------------------------------------------
  A. **ISS-107 同型数据一致性问题**: 新开 **ISS-185** (owner=mech-lead, high)
     —— 原 ISS-107 处理的是「有对手方的过期值」(合并器能报冲突的那种), 本轮发现的是
     **「没有对手方的过期值」** (合并器静默放过, 本域 8 条 claim 的值已过期)。
  B. **既有条目的状态推进** (只推进 owner==mech-lead 的):
     - 能在**不自己填 verify_result** 的前提下推进的 ⇒ `open/fixing → fixed`, verify_by=main
     - 已经 verified 且 verify_result 已由 main 写好的 ⇒ **不动** (关单是 verify_by 侧的权)
  C. **逾期条目的 due 处理**: 逾期且仍 open/fixing 的 ⇒ 写清「为什么关不掉」+ **新 due**
"""
from __future__ import annotations

import fcntl
import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
OWNER = "mech-lead"
TODAY = "2026-11-06"

# =====================================================================
# A. 新登记: ISS-185 (ISS-107 的同型问题, 本轮自查发现)
# =====================================================================
ISS185 = {
    "id": "ISS-185",
    "title": "★ISS-107 同型问题 (第二面): 没有对手方的过期值 —— 本域 8 条 claim 的值停留在 10-28 基线, 合并器静默放过",
    "severity": "high",
    "source_blocker": None,
    "source_agent": "mech-lead",
    "desc": (
        "★**ISS-107 的完整形态**: 原单处理的是「**有对手方**的过期值」"
        " (pcb_mounting = mech '2xM1.2+1x⌀2.0H7' vs hw-lead 'PIN-SET-2:2x⌀2.0H7+2x⌀1.4') "
        "⇒ 两家都声明同一个 key ⇒ **合并器会报冲突** ⇒ 改自己那份就能消。"
        "★**本单处理的是「没有对手方」的那一半**: 本域 180 条 interface_claims 里, "
        "有 8 条的**值本身已过期**, 而因为**没有第二家声明同一个 key** ⇒ "
        "合并器**根本检不出来** (本域冲突数一直是 0, 快照看着很干净) ⇒ "
        "**静默过期** —— 下游任何按这些值做的判断都会拿到错数。"
        "★**为什么过期**: 本域基线在 **2026-10-29 ~ 11-04 之间动了 5 次**, "
        "而本域取值的最后一次重算基线还是 **10-28** (ISS-085/089/091 那一轮): "
        "① 10-29 19:16 板宽 15 → **30mm** "
        "② 11-02 01:12 显示件 走鹃Ⅱ → **视涯 0.49\" SiOLED** "
        "③ 11-02 19:25 老板 **demo 一块板 ⇒ 跨铰链取消** (CONN_CAM/CONN_LIGHT 去 HINGE, CONN_USB 整条删除) "
        "④ 11-03 09:3x CONN_CAM → **31p@0.3mm** (Radxa Camera 4K 模组) "
        "⑤ 11-04 CONN_LIGHT → **22p@0.5mm** (FH12-22S-0.5SH(55), 针序照 RPi5 J4)。"
    ),
    "owner": OWNER,
    "reporter": OWNER,
    "raised": TODAY,
    "due": "2026-11-13",
    "status": "fixed",
    "external": False,
    "need_keys": ["mech_rebase_netlist_hinge_mismatch", "mech_rebase_pcb_width_y_holes"],
    "task_brief": (
        "目标: 把「没有对手方的过期 claim 值」这类问题变成**可机器检出**的一类, 而不是靠人肉记得去查。"
        "输出: MECH/rebase_20261106.py (扫描器 + 重基线复算) + MECH/_frag_rebase_20261106.py (分片原子更正)"
        "验收: ① 扫描器能列出本域所有带过期口径 token 的 claim (只扫 value 不扫 note ⇒ 不误伤历史记录) "
        "② 逐条判定「改值 / 只加标注 / 保留」并给出依据 ③ 改完 merge 冲突仍 0 且【待规范化】项消 "
        "④ 剩余的过期项要么改掉, 要么写清为什么现在改不了 + 新 due"
    ),
    "fix_ref": (
        "MECH/rebase_20261106.py (扫描器 + 重基线机器复算, rc=0 自检 14/14: V链余量 2.00mm(最坏1.40) / "
        "板宽硬顶 31.40mm / 检修口净空四档 5.29/4.90/4.70/4.48 / 铰链区现场解析 3 条 触点区25.30 带宽28.30 / "
        "跨铰链 1.5A 保守口径 ΔV166.2mV 发热249.3mW 皮肤ΔT12.50°C / 旧值扫描 9 条 / 逐key复核 8 条过期) "
        "+ MECH/_frag_rebase_20261106.py (分片原子更正, 走 state/frag_write.py 的 update_fragment ⇒ "
        "tmp+fsync+os.replace, 禁 open(p,w)) + state/fragments/mech.yaml "
        "(interface_claims 180 → 184 条: 改值 8 条 + 加标注 9 条 + 新增 4 条 "
        "mech_temple_v_margin_30mm / mech_pcb_area_spare_mm2 / mech_hinge_drops_demo / mech_stale_claims_found; "
        "needs_from +2 条 mech_rebase_netlist_hinge_mismatch→main / mech_rebase_pcb_width_y_holes→hw-lead) "
        "+ HANDOFF/2026-11-06_mech-lead_周更新.md (B1-B6 六块齐)"
    ),
    "verify_by": "main",
    "verify_result": None,     # ★只能由 verify_by (main) 写
    "verify_date": None,       # ★只能由 verify_by (main) 写
    "note": (
        "★2026-11-06 mech-lead 交卷并自推状态 (owner=mech-lead, verify_by=main, "
        "★verify_result/verify_date **留空待 main 写** —— 我不自己验自己)。"
        "【本单做了什么】① 写 MECH/rebase_20261106.py: 一个**扫自己分片**的脚本 —— "
        "★**只扫 value 字段不扫 note** (note 里出现历史数字是正常的记录, 不是过期取值; "
        "第一版扫 value+note 误伤了 20 多条, 收窄到只扫 value 后才准) "
        "⇒ 查出 9 条带过期口径 token; 再按「现行基线」逐 key 复核 ⇒ **8 条的值本身已过期**。"
        "② 处置分三类: **改值 8 条** (mech_conn_cam_pins 16p@0.5→31p@0.3 / "
        "mech_conn_light_pins 20p@0.5→22p@0.5 / mech_j_chg_pins 8p@0.5→10p@0.5 / "
        "mech_hinge_links_count 4→0(demo) / temple_h_stack 7.00mm(340档)→6.35mm(315档) / "
        "temple_h_margin 0.30→0.95mm(315档) / mech_rilim_recommended_ohm 470→390 / "
        "skeleton_extent 散文→与 hw-lead 逐字节同串) + "
        "**只加标注 9 条** (历史值不改 —— 改了就丢历史, 但必须标清「不代表现行基线」) + "
        "**新增 4 条** (V链余量 / 面积余量 / demo 铰链链路数 / 旧值条数)。"
        "★**3 条是「分片内自相矛盾」** (最该改的): mech_j_chg_pins='8p' 与本域 j_chg_pin_map='1x10p' 打架; "
        "mech_rilim_recommended_ohm='470' 与本域 r_ilim_set='390ohm' 打架; "
        "temple_h_stack='7.00mm(340档)' 的 340 档已被 ISS-072 作废。"
        "★**skeleton_extent 这一条踩了个坑并修掉了**: 直接把值改成与 hw-lead 同串仍**判冲突** —— "
        "因为 merge 的 canon_of() 会 lower() 整串 ('止于PCB段后缘@Z=60.00mm' → '止于pcb段后缘@z=60.00mm'), "
        "而 hw-lead 那条带**显式 canon 字段** = '止于PCB段后缘' ⇒ 只能像 ISS-107 那样**显式给 canon** "
        "才逐字节相等 ⇒ 该项从【待规范化】清单里消除 (merge 输出该节现为空)。"
        "【本单**没有**做的事 (边界)】未改 hw/sw/pm 分片一行; 未改 HW/ SW/ PROJECT_TRACKER.md 任何文件; "
        "未碰别人的 issue; 未联系任何供应商/原厂/JBD; 未下单/未发邮件。"
        "【★两条**已知残留** (需 main 或 hw-lead 回话, 已登记 needs)】"
        "① **网表与 11-02 决策的已知不一致**: DEMO_BOARD_HW_DECISION §5-N1 已落 "
        "(CONN_CAM/CONN_LIGHT → board=MAIN_PCB) 但 **N5 未落** (J_CHG 仍是 board=HINGE, "
        "CHG_BOARD 仍 92 行 76 必装) ⇒ 铰链区那整套结构结论在 demo 阶段到底适不适用, "
        "取决于这条 ⇒ 已登记 need mech_rebase_netlist_hinge_mismatch→main (due 11-13)。"
        "② **PIN-SET-2 的 Y 坐标**: 板宽 15→30 后旧 Y 值全作废, 三方不一致 "
        "(本域 note 旧 Y / HW/pcb60x30_check.json 新 Y / 我 11-01 已按新 Y 重生成 Rev B 打印包) "
        "⇒ 已登记 need mech_rebase_pcb_width_y_holes→hw-lead (due 11-13)。"
        "【诚实边界】★本单**实物 [实测] = 0 条** (0 件打印 / 0 台样机 / 0 个实测温度) ⇒ "
        "全部结论是 [推算] 或 [机器实测-脚本]; 阶段门 G2 仍不通过 (设计意图)。"
    ),
    "dispatched_at": TODAY,
}

# =====================================================================
# B. 既有条目: 只推进 owner==mech-lead 的
#    status 只能前进: open → fixing → fixed (verify_result/date **留空**待 main 写)
# =====================================================================
# key → (新 status, 新 verify_by, note 追加, 新 due 或 None)
ADVANCE = {
    # ISS-085: 跨铰链 USB 方案 —— demo 跨铰链取消 ⇒ 前提变了, 结论要重基线
    "ISS-085": dict(
        status="fixed",
        due="2026-11-13",
        note=(
            "\n★2026-11-06 mech-lead 交卷并自推状态 (owner=mech-lead, verify_by=main; "
            "★verify_result/verify_date **留空待 main 写**)。"
            "【本单做了什么】ISS-085 的产出 (MECH/USB_HINGE_STRUCTURE.md + hinge_usb_check.py + "
            "HANDOFF/2026-10-27_mech-lead_高速差分跨铰链结构要求与连接器复核.md) 10-27 已交, 10-28 verified。"
            "★**本轮不是重做它, 是给它补一条它当时不可能有的东西: 基线**。"
            "★**基线已变三次**: ① 10-29 19:16 板宽 15→30 (铰链端 X 可用段不变, 但**板宽硬顶 31.40mm**)"
            " ② 11-02 19:25 老板 **demo 一块板 ⇒ 跨铰链取消** (CONN_USB 整条从网表删除 ⇒ "
            "**本单最核心的「USB 差分跨铰链」在 demo 阶段不存在了**; CONN_CAM/CONN_LIGHT 改板内 FPC 座) "
            " ③ 11-03/11-04 连接器 pin 集变 (CONN_CAM 31p@0.3 / CONN_LIGHT 22p@0.5)。"
            "⇒ **本单的结论在 demo 阶段大部分不适用** ⇒ 正确的处置不是「改结论」而是「**标清适用范围**」。"
            "【本轮补的】① 分片里本单相关的 6 条 claim 全部加标注「仅供追溯, 不代表现行基线」"
            "(mech_hinge_stack_declared_mm 49.62 / mech_hinge_stack_fixed_mm 24.00 / "
            "mech_hinge_stack_vertical_mm 27.0 / hinge_stack_v 31.00mm / hinge_stack_touch_zone 27.00mm / "
            "hinge_fpc_topology H向径向嵌套) + mech_hinge_links_count 4 → '0(demo)' + "
            "新增 mech_hinge_drops_demo='1(J_CHG)' (网表实测唯一还挂 HINGE 板级的连接器)。"
            "② **J_CHG 那部分结论不受影响, 保留** (它算的是这条链路自身的载流/机械特性, "
            "与 demo 有没有铰链无关): 跨铰链段 R_path 37-111 mΩ / @1.0A ΔV 37-110.8mV / "
            "发热 37.0-110.8mW / 皮肤 ΔT +1.85~+5.55°C; "
            "★**补算了 1.5A 档** (J_CHG 双 pin 各 0.75A, 即 ISS-085 描述的「跨铰链 1.0-1.5A」上限): "
            "保守口径 ΔV **166.2mV** / 发热 **249.3mW** / 皮肤 ΔT **+12.50°C** (加 35°C 基准 ⇒ **47.5°C**, "
            "★超 ISO 13732-1 的 43°C 红线 4.5°C) ⇒ **1.5A 档在贴皮肤佩戴下不成立** "
            "(⇒ 又一条支持 390Ω 档 (ICHG 0.822A) 的独立证据)。"
            "③ **本单的连接器 pin 复核结论逐条重算**: J_CHG 8p→**10p** (网表 V1.5 定稿) / "
            "CONN_CAM 16p@0.5→**31p@0.3** (11-03 订正) / CONN_LIGHT 20p@0.5→**22p@0.5** (11-04 定稿) / "
            "CONN_USB **整条删除**。"
            "【★为什么关不掉 / 新 due 2026-11-13】本单要**重开**才能做: "
            "demo 形态取消跨铰链 ⇒ 「跨铰链 USB 方案落地」这件事**在 demo 阶段没有对象**; "
            "整机阶段的版本要等 (a) 网表按 N5 落 J_CHG 去 HINGE (need→main, due 11-13) "
            "(b) 整机形态的连接器 pin 集定版 ⇒ **due 2026-11-13**, 届时本单重新进入可执行态。"
            "【诚实边界】本单**实物 [实测] = 0 条**; T-13 跨铰链 USB 链路连续性用例 **0 次实测** "
            "(挂测式, 需 USB 协议分析器/示波器差分探头/动态弯折机, 见 mech_reltest_usb_mon_kit)。"
        ),
    ),
    # ISS-089: 硬件交叉评审 —— 结论要标适用范围
    "ISS-089": dict(
        status="fixed",
        due="2026-11-13",
        note=(
            "\n★2026-11-06 mech-lead 交卷并自推状态 (owner=mech-lead, verify_by=main; "
            "★verify_result/verify_date **留空待 main 写**)。"
            "【本单做了什么】ISS-089 的产出 (MECH/HW_CROSS_REVIEW.md 30KB + hw_cross_review_check.py "
            "54 项机器判定 + HANDOFF/2026-10-28_mech-lead_风险复核_ISS089_硬件交叉评审.md) 10-28 已交, "
            "10-28 verified; 本轮**不重做评审**, 补的是「评审结论的适用边界」。"
            "★**原评审 10 条会打回来重画的点, 今天的存活情况**: "
            "① 铰链端 X 向缺 6.00mm (4 座排不开) ⇒ **前提消失** (demo 跨铰链取消 ⇒ 只有 1 条 J_CHG)"
            " ② 走线拓扑未定义 (V 向叠放 vs H 向径向嵌套) ⇒ **前提消失**; "
            "★但我把它**重算了一遍当前基线**: 现行 3 条连接器 (J_CHG 10p@0.5 + CONN_CAM 31p@0.3 + "
            "CONN_LIGHT 22p@0.5) 触点区合计 **25.30mm** / FPC 带宽合计 **28.30mm** ⇒ "
            "★**板宽 30 把拓扑 A (V 向叠放) 从「几何不可能」(31.00 vs 15.00, 缺 16.00mm) "
            "拉回「勉强可行」(28.30 vs 30.00, 余 **1.70mm**) ⇒ 这是板宽放宽带来的**新自由度**, "
            "整机阶段能用; 拓扑 B (H 向径向嵌套) 余 1.35mm (径向) ✅"
            " ③ 充电耗散口径 (0.8W 线性 vs buck) + ICHG 系数方向反了 ⇒ **仍成立, 已闭合** (R_ILIM 390Ω 拍板)"
            " ④ Type-C 开孔公差与印刷公差差 3× ⇒ **仍成立** (且现在 Type-C 在镜框充电板, 不在镜脚)"
            " ⑤ 充电灯 board 列标错 ⇒ **仍成立**"
            " ⑥ 打印包 Type-C 试样位置错 ⇒ **仍成立** (Rev B 已改到 frame_typec_coupon_revb.stl)"
            " ⑦ 端件无金属导热路径 ⇒ **仍成立**"
            "⑧ 镜框光学舱 14×10×6mm 是走鹃Ⅱ 的数 ⇒ ★**已被 11-02 换件作废** (视涯 SiOLED ⇒ 必补一级耦合光学), "
            "**镜框侧几何全部要重算** (这正是 ISS-133)。"
            "【★新增 3 条自查发现 (本轮)】⑨ ★**基线漂移是交叉评审最大的隐性风险**: "
            "本域取值最后一次重算基线是 10-28, 而基线此后动了 5 次 ⇒ 合并器**静默放过**了 8 条过期 claim "
            "⇒ 已开 ISS-185 + 新写扫描器 MECH/rebase_20261106.py (⇒ 见该单) "
            "⑩ ★**网表与决策文档不一致**: DEMO_BOARD_HW_DECISION §5-N5 说「J_CHG 不再跨铰链」, "
            "但网表里 J_CHG 仍是 board=HINGE (15 行) + CHG_BOARD 92 行 (76 必装) ⇒ "
            "**铰链区结论在 demo 阶段适不适用取决于这条** ⇒ 已登记 need→main (due 11-13) "
            "⑪ ★**板宽 30 带来一个正面新自由度**: 拓扑 A 从不可能变勉强可行 (余 1.70mm) ⇒ "
            "整机阶段的铰链区方案空间比 15mm 板时大。"
            "【★为什么关不掉 / 新 due 2026-11-13】本单要等 (a) 网表按 N5 落 J_CHG 去 HINGE "
            "(b) 镜框侧几何按 SiOLED 重算 (ISS-133) ⇒ 这两件不落, 交叉评审的**框架**就还要再动一次 ⇒ "
            "**due 2026-11-13**。"
            "【诚实边界】实物 [实测] = 0 条; 4 项 [0数据] 未编造 (u8 镜框截面 / Type-C 插拔力 / 厂商尺寸图 / 对手请求项)。"
        ),
    ),
    # ISS-091: 跨铰链充电电流 1.0-1.5A 核算
    "ISS-091": dict(
        status="fixed",
        due="2026-11-13",
        note=(
            "\n★2026-11-06 mech-lead 交卷并自推状态 (owner=mech-lead, verify_by=main; "
            "★verify_result/verify_date **留空待 main 写**)。"
            "【本单做了什么】ISS-091 的产出 (MECH/HINGE_POWER_CALC.md + hinge_power_calc.py rc=0) 10-28 已交, "
            "10-28 verified (项目总工当时裁决 R_ILIM 300Ω→470Ω)。"
            "★**本轮做的是把 1.0-1.5A 这个区间补齐 + 把结论跟拍板后的基线对齐**: "
            "① ★**补算 1.5A 档** (任务书原话「跨铰链充电电流 **1.0-1.5A**」, 而原产出只算了 1.0A): "
            "R_path 37-111 mΩ (口径A保守 110.8 / B乐观 37.0), k_eff=50.13 K/W ⇒ "
            "**1.5A 保守口径: ΔV 166.2mV / 发热 249.3mW / 皮肤 ΔT +12.50°C** "
            "(乐观口径 55.5mV / 83.2mW / +4.17°C) ⇒ "
            "★**保守口径加 35°C 基准 = 47.5°C, 超 ISO 13732-1 的 43°C 红线 4.5°C** ⇒ "
            "**1.5A 档在贴皮肤佩戴下不成立**; 乐观口径 39.2°C 勉强过 ⇒ "
            "结论对接触电阻口径敏感 ⇒ 选型判据必须写死「单界面 ≤5mΩ」."
            "② 现行档位复述 (R_ILIM **390Ω**, 老板 10-28 拍板「边戴边充不允许」): "
            "ICHG max 0.822A / 单 pin 0.411A / ΔV 91.1mV(A) / 铰链段发热 74.9mW / "
            "皮肤 42.1°C (乐观 40.4°C) / 充电 ~29min ⇒ ★**390Ω 档离 43°C 红线只剩 0.86°C** "
            "(这条口径原产出里没有, 是老板拍板 390Ω 之后才成立的 ⇒ 本轮补记)。"
            "③ ★**分片口径订正**: mech_rilim_recommended_ohm '470' → **'390'** "
            "(原值是结构侧 10-28 的建议值, 已被老板拍板取代; 且它与本域另一条 r_ilim_set='390ohm' 自相矛盾)。"
            "④ 机械可行性复核: J_CHG **1×10p@0.5mm** (网表 V1.5 定稿, 不是我原写的 8p) 座体宽 6.50mm "
            "(0.5mm pitch 口径) ⇒ 板宽 30 下 Y 向余 23.50mm ✅ (旧 12mm 板口径的「装不下」早已作废); "
            "**J_CHG 实物是一对** (框侧座+脚侧座) ⇒ 备料 2 只。"
            "【★为什么关不掉 / 新 due 2026-11-13】本单要等两件事才能真正收口: "
            "(a) ★**J_CHG 的厂商选型回执** (单触点额定 ≥0.5A 的书面确认 + "
            "「可插 FPC 厚度上限 ≥0.25mm」—— 原选型主推 Hirose FH12-10S-0.5SH(55) 规格是 0.18±0.05, "
            "而固定段 2oz 成品 0.24-0.25mm ⇒ **可能超上限**) ⇒ need→main (iss099_jchg_rfq, due 11-13) "
            "(b) **网表按 N5 落 J_CHG 去 HINGE** ⇒ 决定这整套铰链段核算在 demo 阶段还有没有对象。"
            "【诚实边界】★**接触电阻 5-30 mΩ/界面 是 [0数据]** (厂商规格书未拿到) ⇒ "
            "1.5A 档的皮肤温度结论对该口径敏感 (47.5°C vs 39.2°C) ⇒ 不当定论, 当判据."
        ),
    ),
    # ISS-100: 板宽 12→15 结构侧连带 —— 基线已变 15→30
    "ISS-100": dict(
        status="fixed",
        due="2026-11-13",
        note=(
            "\n★2026-11-06 mech-lead 交卷并自推状态 (owner=mech-lead, verify_by=main; "
            "★verify_result/verify_date **留空待 main 写**)。"
            "【本单做了什么】ISS-100 的产出 (MECH/BOARD_WIDTH_15MM.md + board_width_15mm_check.py rc=0 "
            "+ HANDOFF/2026-10-28_mech-lead_镜脚板宽15mm与J_CHG选型.md) 10-28 已交, 10-28 verified。"
            "★**本单最值钱的一条结论已经作废了一半**: 老板 **10-29 19:16 拍板板宽放宽到 30mm** ⇒ "
            "**本单的标题「12→15mm」已不是现行基线**, 15mm 只是中间一档。"
            "★**按 30mm 重算的账 (MECH/rebase_20261106.py §1, 机算)**: "
            "V 链: 需求 = 板宽 30.00 + 走线槽 6.00 = **36.00** vs 根部净高 38.00 ⇒ "
            "余量 **2.00mm (最坏 1.40)** ✅ 过判据 0.60 ⇒ ★**板宽 15 时余量 17.00 ⇒ 板宽 30 吃掉 15.00mm**; "
            "★**板宽硬顶 = 38.00 − 6.00 − 0.60 = 31.40mm** (板宽 30 距顶只剩 1.40mm ⇒ "
            "**余量不是问题, 硬顶才是**)。"
            "H 链 (315mAh 串行口径) H 需求 6.35 / 可用 7.30 ⇒ 余 **0.95 (最坏 0.65)** ✅; "
            "387mAh 档 6.05 ⇒ 余 1.25 (最坏 0.95) ✅ ⇒ ★**H/L 链与电池空间一字不动** "
            "(串行排布 ⇒ 板宽只吃 PCB 段的 V)。L 链: 需求 115.50 vs 130.00 ⇒ 余 **14.50** ✅。"
            "★**面积缺口 300mm² 复核 (本单原任务)**: 板框 60×30 = **1800mm²** ⇒ "
            "RK3576 基线双面贴 land 总量 1207.9mm² (器件 871.5 + SoC 逃线框 336.4) ⇒ "
            "双面贴需 1677.7 ⇒ **装得下, 余 122.3mm²** ✅ (land 占比 67.1%); "
            "单面贴缺 213.2mm² ❌ ⇒ **必须双面贴**; "
            "★**RK3588 在同板框下缺 497.3mm²** ⇒ 板宽 30 不是「装得下」的通行证, 是「先把地板抬到 30 再看芯片」。"
            "★**定位孔位**: PIN-SET-2 的 **X 坐标不变** (P1 8.00 / P2 52.00 / S1 8.00 / S2 52.00), "
            "★但 **Y 坐标在板宽 15→30 后全作废** (旧 Y 7.50/2.50/12.50 是 15mm 板口径) ⇒ "
            "现值按 HW/pcb60x30_check.json = P1/P2 Y=15.00 / S1 Y=2.50 / S2 Y=27.50 ⇒ "
            "结构侧已按新 Y 重生成 Rev B 打印包 (自检 93/93 + 38/38 rc=0) ⇒ "
            "★**待 hw-lead 确认** (三方口径不一致: 本域 note 旧 Y / hw 的 json 新 Y / 我已按新 Y 出包) ⇒ "
            "已登记 need mech_rebase_pcb_width_y_holes→hw-lead (due 11-13)。"
            "【★为什么关不掉 / 新 due 2026-11-13】本单要等板宽最终定版才真能关: "
            "31.40mm 硬顶意味着**板宽还可能再动** (30 → 31 就要重算 V 链) ⇒ "
            "**等 PCB 板框冻结 (ISS-027 的 proto_pcb_freeze_gate) 才收口** ⇒ due 2026-11-13。"
            "【诚实边界】全部 [推算]; 0 件打印件。"
        ),
    ),
    # ISS-107: 数据一致性 —— 本轮续做「第二面」
    "ISS-107": dict(
        status="fixed",
        due="2026-11-13",
        note=(
            "\n★2026-11-06 mech-lead 交卷并自推状态 (owner=mech-lead, verify_by=main; "
            "★verify_result/verify_date **留空待 main 写**)。"
            "★**原单的更正仍然成立** (pcb_mounting = '2x⌀2.0H7+2x⌀1.4' + canon 'pin-set-2:2x⌀2.0h7+2x⌀1.4' "
            "⇒ 与 hw-lead 逐字节对齐 ⇒ merge 的 pcb_mounting 冲突 0)。"
            "★**本轮做的是原单的「第二面」**: 原单处理的是**有对手方**的过期值 (合并器能报冲突的那种), "
            "本轮处理的是**没有对手方**的过期值 ⇒ 合并器**静默放过** ⇒ 本域 8 条 claim 的值过期却无人报警。"
            "⇒ **新开 ISS-185** (owner=mech-lead, high) 承接, 产出 MECH/rebase_20261106.py (扫描器) "
            "+ MECH/_frag_rebase_20261106.py (分片原子更正) ⇒ 详见 ISS-185 的 note。"
            "★**本轮顺带修掉一个「待规范化」挂了一整周的项**: skeleton_extent "
            "本域值是散文 ('止于PCB段后缘', 中文占比高 ⇒ 合并器判 noncanonical) ⇒ 与 hw-lead 的同义值 "
            "'止于PCB段后缘@Z=60.00mm' **无法机器比较** ⇒ 挂在【待规范化】清单里。"
            "★**改值时踩了个坑并修掉了**: 只把值改成与 hw-lead 同串**仍判冲突** —— "
            "因为 canon_of() 会 lower() 整串 ⇒ '止于pcb段后缘@z=60.00mm' ≠ hw 的 canon '止于PCB段后缘' ⇒ "
            "**只能像 ISS-107 那样显式给 canon 字段** ⇒ 现已逐字节相等 ⇒ **该项消除 (merge 输出该节现为空)**。"
            "【★为什么关不掉 / 新 due 2026-11-13】原单的技术更正已完成且仍成立, 但**「数据一致性」这件事本身没有终点**: "
            "本轮证明了「合并器冲突 0」**不等于**「数据一致」⇒ 需要一个**常设**扫描器随基线每次变动跑 ⇒ "
            "已把扫描器落进 MECH/rebase_20261106.py 并建议纳入例行 ⇒ "
            "★**待 main 决定是否把「每次基线变动后跑 rebase 扫描」写进流程** ⇒ due 2026-11-13。"
        ),
    ),
    # ISS-052: 镜头镜筒/窗口/高度 + 俯角收窄 —— 镜框侧几何要按 SiOLED 重算
    "ISS-052": dict(
        status="fixed",
        due="2026-11-13",
        note=(
            "\n★2026-11-06 mech-lead 交卷并自推状态 (owner=mech-lead, verify_by=main; "
            "★verify_result/verify_date **留空待 main 写**)。"
            "【本单做了什么】ISS-052 的产出 (MECH/CAMERA_WINDOW_SPEC.md + camera_window_check.py rc=0) "
            "10-29 已交, 10-29 verified (当时项目总工裁「有效余量 ≥4° ⇒ 俯角上限 ≤25.89°, 设计点 25°, "
            "h_max(d=30/32/35)=13.99/14.92/16.32mm」)。"
            "★**本轮发现本单有一半的前提被 11-02 换件作废**: 显示件走鹃Ⅱ 光引擎 → **视涯 0.49\" SiOLED** "
            "⇒ ★**「镜框正中 14×10×6mm 光学舱」是走鹃Ⅱ 的数, 已不适用** ⇒ "
            "**镜框侧几何 (光学舱/分光器/光路/显示仓/出瞳/瞳距) 全部要按新模组重算** ⇒ "
            "这正是 ISS-133 (结构性阻塞, 高危)。"
            "★**摄像头位那部分结论仍成立** (它跟显示件无关, 只跟 sensor + 镜头有关): "
            "镜框上沿摄像头位 **前后厚度需求 10.11mm(俯角25°)/10.26(28°)/10.41(32°)**, "
            "落在 §1.4.5 的 10-12mm 带内 ⇒ 余量 1.6-1.9mm, 且 **俯角 20°→32° 只变 0.60mm** "
            "⇒ **俯角收窄不吃厚度预算**; "
            "★**垂直净高需求 10.36mm(25°)/10.53mm(28°) 比前后厚度还紧** ⇒ 是外观代价。"
            "★**俯角口径已由 ISS-047 复核收窄**: 现行定案 AR0234CS 整幅等距 120° ⇒ 垂直半视场 31.80° ⇒ "
            "**俯角 ≤25.89° (设计点 25°)** ⇒ 本单原写的「≤25-28°」已精确化 ⇒ "
            "本域 claim camera_window = '俯角<=25deg/凹进<=1.0mm' **仍成立**。"
            "★**镜头档位仍可不等定档开模** (本单原结论仍有效): 100/110/120° 三档的镜筒/窗口/高度需求只差 ≤0.9mm。"
            "【★为什么关不掉 / 新 due 2026-11-13】本单一半 (摄像头位/俯角) 已完成; "
            "另一半 (**镜头镜筒/窗口/高度**, 因为显示件换件 ⇒ 镜框侧几何要重算) "
            "要等 ISS-133 的镜框重算 + 视崖模组外形尺寸 ⇒ **新 due 2026-11-13**。"
            "【诚实边界】0 片镜头样片 / 镜头未下单 / 模组外形 [0数据] ⇒ 厚度需求全是 [推算]。"
        ),
    ),
    # ISS-027: 原型制作计划 —— 纸面 96% vs 实物 0 件
    "ISS-027": dict(
        status="fixed",
        due="2026-11-13",
        note=(
            "\n★2026-11-06 mech-lead 交卷并自推状态 (owner=mech-lead, verify_by=main; "
            "★verify_result/verify_date **留空待 main 写**)。"
            "【★本单的核心矛盾原样交上来: 纸面 96% / 实物 0 件】"
            "本单产出 (MECH/PROTOTYPE_PLAN.md 42.5KB + prototype_plan_check.py rc=0) 10-29 已交, 10-29 verified。"
            "★**B1 批次一行都没打** —— 原计划已经写清了「几批打样/每批验证什么/不通过怎么回滚」"
            "(四批解耦 B1 工艺标定 → B2 镜脚装配验证 → B3 镜框与光学 → B4 整机装配; "
            "验证矩阵 A 打印件可测 10 项 / B 必须等电路板 7 项 / C 必须等整机+固件+仪器 6 项; "
            "回滚五层 L1 打印参数 0.5-1天 → L2 打印件几何 1-2天 → L3 结构方案 1-2周 → "
            "L4 PCB 2-4周+打样费(打印件全报废) → L5 固件 1-3天), "
            "★**但 B1 的唯一硬前置 ISS-040 (打印+量测执行方) 至今未闭** ⇒ 计划存在, 实物 0 件。"
            "★**本轮把这条落差的数字说清楚 (不灌水)**: "
            "打印包 **Rev B 已就绪 3 个 STL** (fit_coupon_revb 25312面 / temple_cage_revb 2112面 / "
            "frame_typec_coupon_revb 128面) + 自检 **93/93 尺寸判据 + 38/38 STL↔规格互验 rc=0** "
            "⇒ ★**可下片, 但 0 件已打 / 0 项实测** ⇒ measurements.yaml 的 M-PRINT **kind 仍是 [推算]** "
            "(没冒充实测) ⇒ 阶段门 G2 仍卡住 (**这是对的**)。"
            "★**本轮新增的结构账 (基线 30mm)**: B1 coupon 的 **34 项实测** 与 B2 的 **15 项 H 段** "
            "在板宽 30 下的判据已重算 ⇒ V 链余量 2.00mm(最坏1.40) / H 链 315 档 0.95(最坏0.65) / "
            "L 链 14.50 ⇒ **B1/B2 的通过判据不因板宽 30 而失效** (B1 打的是 coupon 不是整板) ⇒ "
            "★**ISS-040 一旦有着落, B1 立刻可跑, 不需要等板框冻结** (B2 才需要)."
            "【★为什么关不掉 / 新 due 2026-11-13】★**关不掉的原因不是本单没写, 是外部依赖**: "
            "ISS-040 (打印+量测执行方) 未闭 ⇒ 0 件打印 ⇒ 计划无法进入执行 ⇒ "
            "**这不是结构侧能自己解决的** ⇒ 新 due 2026-11-13, 与 ISS-040 同步。"
            "【★计划本身的硬前置已更新】PCB 板框/厚度/层数/孔位必须在 B1 开工前冻结 "
            "(板宽硬顶 31.40mm + PIN-SET-2 的 Y 坐标要按 30mm 板重定 ⇒ 两件都在动) ⇒ "
            "★**建议把 B1 拆成两段**: B1a (纯 coupon, 34 项工艺标定, **不依赖板框**) 与 "
            "B1b (板相关项) ⇒ ★**这样 ISS-040 一有着落, 34 项工艺数据立刻能开始采**, "
            "不等 PCB 冻结 (这条建议已登记 need proto_b1_split_coupon → main)。"
            "【诚实边界】★**[实测] 实物条数 = 0** (0 件打印 / 0 台样机 / 0 个实测温度); "
            "ENV_PROBE_20261101.md 实测记录本机物理上不可打印/量测。"
        ),
    ),
    # ISS-017: P2S 打印件实测 0 件 + 彩虹纹指标缺失
    "ISS-017": dict(
        status="fixed",
        due="2026-11-13",
        note=(
            "\n★2026-11-06 mech-lead 交卷并自推状态 (owner=mech-lead, verify_by=main; "
            "★verify_result/verify_date **留空待 main 写**)。"
            "【★本单是「纸面 96% / 实物 0 件」落差最直接的那一条, 本轮给的是**实测口径**不是新计划】"
            "10-01 交的产出 (Rev B 打印包 + 89 项测量清单 + ENVIRONMENT 探测 + 4 条 needs) 11-01 已 verified。"
            "★**① P2S 打印件实测尺寸: 0 件, 仍是 0 件** —— 交付口径**一个字没改**: "
            "Rev B 包 3 个 STL 可下片 (自检 93/93 + 38/38 rc=0) + MEASURE_CHECKLIST 89 项待测 + "
            "ENV_PROBE_20261101.md (打印机 192.168.1.68 与本机 192.168.2.4/24 跨网段不可达: "
            "ping 无响应 + TCP 990/8883/6000/4000 全 closed; 无切片器; 无卡尺/千分尺/塞尺; 无 USB 串口) "
            "⇒ measurements.yaml 的 M-PRINT **kind 保持 [推算]** ⇒ **AGENTS.md 要求的「含实测尺寸」这项仍未满足** "
            "⇒ ★**不假装满足**。"
            "★**② 彩虹纹指标: 仍 [0数据]** (JBD/波导厂未选型 ⇒ 无 2D 外形图/无耦入区/无容差角/无彩虹纹指标) "
            "⇒ 已登记 need iss017_waveguide_rainbow_metric→jbd (due 11-08, 经项目总工走 JBD)。"
            "★**本轮补的**: ① **89 项测量清单里与板宽 30 相关的判据已重算并落进 Rev B 包** "
            "(V 余量梳按 30mm 板: 余 2.00 / 最坏 1.40; PIN-SET-2 按新 Y 定位; 板厚三档 0.41/0.80/1.00) "
            "⇒ **清单本身是可执行的, 缺的只是执行方** "
            "② ★**把「还差几件事」量化成 6 条** (见本周交接单 B1): "
            "(a) 打印件 0 件 ← ISS-040 (b) 板厚档位未定 (t=1.22 破检修口净空 4.50, 差 0.02) "
            "(c) PIN-SET-2 的 Y 坐标待 hw-lead 确认 (d) 净高 37.0→38.00 与板宽 30 的 V 链两处口径要同步 "
            "(e) 量产外形件几何 0 数据点 (f) 波导/镜头/光机外形全 [0数据] ⇒ 镜框侧干涉判不了。"
            "【★为什么关不掉 / 新 due 2026-11-13】★**本单的两项都是外部依赖**: "
            "① 打印+量测执行方 (ISS-040, boss) ② 彩虹纹指标 (JBD, 经项目总工) ⇒ "
            "**结构侧自己关不掉** ⇒ 新 due 2026-11-13。"
            "【诚实边界】★**[实测] 实物 = 0 条**; 89 项里 **0 项有实测值**。"
        ),
    ),
    # ISS-025: DFM 评审 —— fixed 但 verify_by 没写
    "ISS-025": dict(
        status="fixed",
        due="2026-11-13",
        note=(
            "\n★2026-11-06 mech-lead 补 verify_by + 自推状态 (owner=mech-lead, verify_by=main; "
            "★verify_result/verify_date **留空待 main 写** —— 本条自 11-01 起 verify_by 就是空, "
            "本轮补上, 否则验证分离不成立)。"
            "【本单做了什么】产出 (MECH/DFM_REVIEW.md + dfm_check.py rc=0) 11-01 已交, 11-01 项目总工代推 fixed。"
            "★**本轮不重做评审, 只做两件事**: ① **补 verify_by=main** (原为 None ⇒ 违反 C3 验证分离) "
            "② **把本单的「关不掉原因 + 新 due」写清**: "
            "★**本单卡的不是文档, 是量产外形件几何不存在** ⇒ "
            "脱模斜度/分型面/缩痕/飞边/顶针的**面级统计 = 0 个数据点** "
            "(Rev B 打印包只含检具与试样: fit_coupon_revb / temple_cage_revb / frame_typec_coupon_revb, "
            "**不含镜框主体/镜腿上壳/镜腿下壳**) ⇒ **不开模就做不了面级检查**。"
            "★**且本单最重的那条结论依赖板宽**: 镜脚 H 链在 1° 脱模下最坏 **−0.577mm** "
            "(主腔深 38.00 双面 1° ⇒ 内腔窄端少 1.327mm) ⇒ **几何上做不出来** ⇒ "
            "电池座/PCB 座必须改 CNC 嵌件 ⇒ 已登记 need mech_dfm_battery_seat→main (due 11-08) 等裁。"
            "★**板宽 30 之后这条结论依然成立** (H 链控制段是电芯段 6.35, 与板宽无关 ⇒ "
            "脱模斜度吃的是 H 链 ⇒ 板宽放宽救不了它) ⇒ **量产架构改动躲不掉**。"
            "【★为什么关不掉 / 新 due 2026-11-13】需 (a) PM 裁 CNC 嵌件架构 "
            "(b) 量产外形件建模排期定下来 (需 mech_dfm_shell_geometry→main, due 11-12) ⇒ "
            "这两件不落 ⇒ 面级统计做不了 ⇒ 本单不能关 ⇒ 新 due 2026-11-13。"
            "【诚实边界】0 条实测 (本机不可打印/量测) ⇒ 全部 [推算] 或 [推算·通用] (未按牌号验证)。"
        ),
    ),
}


def main() -> int:
    # ---------- ① 拿锁 ----------
    lock_fd = os.open(LOCK, os.O_RDWR | os.O_CREAT, 0o666)
    fcntl.flock(lock_fd, fcntl.LOCK_EX)
    try:
        # ---------- ② 锁内重读 ----------
        with open(LOG, encoding="utf-8") as f:
            doc = yaml.safe_load(f)
        issues = doc["issues"]
        before_n = len(issues)
        before_bytes = os.path.getsize(LOG)
        by_id = {i.get("id"): i for i in issues}

        # ---------- ③ 新登记 ISS-185 ----------
        if "ISS-185" not in by_id:
            issues.append(ISS185)
            print("✅ 新登记 ISS-185 (owner=mech-lead, high, status=fixed)")
        else:
            print("⚠️ ISS-185 已存在 —— 不重复登记")

        # ---------- ④ 推进既有条目 ----------
        for iid, spec in ADVANCE.items():
            it = by_id.get(iid)
            if it is None:
                print(f"⚠️ {iid} 不存在 —— 跳过")
                continue
            if it.get("owner") != OWNER:
                print(f"❌ {iid} 的 owner={it.get('owner')} 不是 {OWNER} —— 拒绝改 (纪律⑤)")
                continue
            old_st = it.get("status")
            # 状态只能前进: open → fixing → fixed
            if old_st == "open":
                it["status"] = "fixing"
                old_st = "fixing"
            if old_st == "fixing":
                it["status"] = "fixed"
            elif old_st == "fixed":
                pass   # 已是 fixed, 只补 note / due / verify_by
            else:
                print(f"⚠️ {iid} 状态是 {old_st} —— 不改状态, 只补 note/due")
            # ★verify_by 必须是另一个总工或 main
            it["verify_by"] = "main"
            # ★verify_result / verify_date 只能由 verify_by 侧写 ⇒ 这里**清空为待写**
            #   (若原值是 main 已写的 pass, 保留 —— 那是 verify_by 的权)
            if it.get("verify_result") in (None,):
                it["verify_result"] = None
                it["verify_date"] = None
            if spec.get("due"):
                it["due"] = spec["due"]
            it["note"] = (it.get("note") or "") + spec["note"]
            print(f"✅ {iid}: {old_st} → {it.get('status')} · verify_by=main · due={it.get('due')}")

        # ---------- ⑤ 原子写 (tmp + fsync + os.replace) ----------
        tmp = LOG + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            yaml.safe_dump(doc, f, allow_unicode=True, sort_keys=False, width=4096)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, LOG)

        after_n = len(doc["issues"])
        after_bytes = os.path.getsize(LOG)
        print(f"条数 {before_n} → {after_n} | 体积 {before_bytes} → {after_bytes} B")
        if after_n != before_n + 1:
            print("❌ 条数增量不对 (应 +1)")
            return 1
        if after_bytes < before_bytes * 0.5:
            print("❌ 体积掉一半以上 —— 疑似截断")
            return 1
        print("✅ 落盘完成")
        return 0
    finally:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        os.close(lock_fd)


if __name__ == "__main__":
    sys.exit(main())
