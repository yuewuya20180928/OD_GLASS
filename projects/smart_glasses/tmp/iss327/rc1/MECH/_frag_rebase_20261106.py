#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MECH/_frag_rebase_20261106.py — ISS-107 同型问题 (数据一致性) 的**分片侧更正**

================================================================================
为什么有第二个 ISS-107 (原单已于 10-29 verified)
--------------------------------------------------------------------------------
原 ISS-107 处理的是**有对手方的**过期值:
    pcb_mounting = '2xM1.2+1x⌀2.0H7'  vs  hw-lead 'PIN-SET-2:2x⌀2.0H7+2x⌀1.4'
⇒ 两家都声明同一个 key ⇒ **合并器会报冲突** ⇒ 靠"改自己那份"就能消。

★**本单处理的是没有对手方的**过期值 —— 合并器**根本检不出来** (因为没第二家声明同 key):
    · 9 条 claim 的值停留在 **2026-10-28 那一轮的基线** (板宽 15 / 40p / 8p / 340mAh / 470Ω / 净高 37.0)
    · 而基线在 **10-29 ~ 11-04** 之间动了 5 次 (板宽 30 / SiOLED / demo 跨铰链取消 /
      CONN_CAM 31p@0.3 / CONN_LIGHT 22p@0.5)
    ⇒ 这些值**静默过期**: 合并器说"冲突 0", 看着很干净, 实际上有 8 条的值是错的。

★**这才是 ISS-107 的完整形态**: 不是"合并器报冲突"才算问题, 而是
  **"值与当前基线不符"** 才是问题 —— 冲突检测只是它的一个**子集**(有对手方的那部分)。

【本脚本做什么】
  ① 用 `MECH/rebase_20261106.py` 的同一套判据, 逐条比对 mech 分片的取值 vs 当前基线
  ② 对**确认已过期**的 key 改值 (只改**值**, note 里写清依据 + 为什么原值过期)
  ③ 对**不打算改**的 key 追加 note (标明"历史口径, 仅供追溯, 不代表现行基线") —— ★不改值,
     因为它们记的是"某一轮的结论"这个事实本身, 改了反而丢历史
  ④ 补新增 key (本轮新算出来的数)

【写分片铁律】
  ★ 走 `state/frag_write.py` 的 `update_fragment()` (tmp + fsync + os.replace)
  ★ 禁止 `open(path, "w")` —— 并发下合并器读到半截 ⇒ 整个域从快照里静默消失
    (10-25 压测实测 99.6% 概率)

用法:  python3 MECH/_frag_rebase_20261106.py [--dry-run]
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(PROJ, "state"))

from frag_write import update_fragment, load_fragment  # noqa: E402

AGENT = "mech-lead"

# =====================================================================
# ① 要**改值**的 key (值已确认过期 —— 依据见 note)
# =====================================================================
REVALUE = {
    # ---- 连接器 pin 集: netlist V1.9/REV2 定稿后已变 ----
    "mech_conn_cam_pins": (
        "31p@0.3mm",
        "★ISS-107 同型更正 (2026-11-06): 原值 '16p@0.5mm' 是 **10-28 那轮的建议值**, "
        "已被 11-03 09:3x 订正作废 —— 现行 = **31p@0.3mm** (HIROSE FH35C-31S-0.3SHW(50), "
        "Radxa Camera 4K 模组, 机械 10.9×4.2×0.9mm, 翻盖式 ZIF 横向插拔, 兼容 0.2mm 厚 FPC); "
        "来源 HW/NETLIST_REV2_SPEC.md §1.1 + HW/netlist_v1.csv 实解析 (31 行引用 pin1..31)。"
        "★结构侧注: 0.3mm pitch 翻盖座 + 横向插拔 ⇒ **不能直接当跨铰链件** (铰链要反复弯折), "
        "demo 已按 11-02 决策把它改成**板内** FPC 座 (board=MAIN_PCB) ⇒ 本条只在整机阶段复活时再用。",
    ),
    "mech_conn_light_pins": (
        "22p@0.5mm",
        "★ISS-107 同型更正 (2026-11-06): 原值 '20p@0.5mm' 已过期 —— "
        "**22p@0.5mm** (HIROSE FH12-22S-0.5SH(55), 右角/底接触/1固定柱) 是 11-04 定稿, "
        "针序照 Raspberry Pi 5 官方 DISPLAY 座 (J4)。"
        "★注意 NETLIST_REV2_SPEC.md §1.2 写的是 40p/0.5mm, 而网表实际落地的是 22p —— "
        "**两个上游文件口径不一致**, 本值取网表实测 (板内 FPC 座, board=MAIN_PCB)。",
    ),
    "mech_j_chg_pins": (
        "10p@0.5mm",
        "★ISS-107 同型更正 (2026-11-06): 原值 '8p@0.5mm' 是 ISS-085 早期的 8p 口径, "
        "网表 **V1.5 已定稿 1×10p@0.5mm** (pin1/2=BAT_CHG 载流双pin, pin3/4=GND 回流双pin, "
        "pin5=CHG_STAT, pin6=PWR_GOOD, pin7=NC (11-04 demo 改本地分压), pin8=TS, pin9=RSV, "
        "pin10=TS 专用回流)。原值与本域另一条 claim 'j_chg_pin_map' 自相矛盾 ⇒ 属典型的**分片内不一致**。",
    ),
    # ---- 跨铰链链路数 ----
    "mech_hinge_links_count": (
        "0(demo)",
        "★ISS-107 同型更正 (2026-11-06): 原值 '4' (J_CHG/CONN_USB/CONN_CAM/CONN_LIGHT) 是 10-28 那轮; "
        "**11-02 19:25 老板拍板 demo 形态 ⇒ 跨铰链取消** (一块主板 + sensor 模组 + 屏幕模组 + FPC 软排), "
        "CONN_CAM/CONN_LIGHT 去 HINGE 板级归属, CONN_USB 整条从网表删除 ⇒ **demo 跨铰链链路数 = 0**。"
        "⇒ 铰链区那一整套结构结论 (V 向堆叠 31.00 / 径向 4.40 / 铰链端 X 缺 6.00mm) "
        "**全部转入整机阶段**再算, demo 板本期不适用。",
    ),
    # ---- H 链 (串行口径, 315/387 两档) ----
    "temple_h_stack": (
        "6.35mm(315档)",
        "★ISS-107 同型更正 (2026-11-06): 原值 '7.00mm(340档)' 是 **340/575/675 三档旧口径** "
        "(那三档已随 ISS-072 作废) 且算式含隔热垫+空气隙 (叠放模型)。"
        "现行 = **串行口径 315mAh 档 H 需求 6.35mm** (皮肤壁0.8 + 非对称座深4.75 + 顶板0.8, "
        "MECH/fit_check_v3_30mm.py §2 第180行同式); 387mAh 档 = 6.05mm。"
        "电芯段不设隔热垫/空气隙 (那两项在 PCB/SoC 段)。",
    ),
    "temple_h_margin": (
        "0.95mm(315档)",
        "★ISS-107 同型更正 (2026-11-06): 原值 '0.30mm' 是 340 档旧算法的余量 "
        "(7.30 − 7.00)。现行串行口径 = 315档 **0.95mm** (最坏 0.65) / 387档 1.25mm (最坏 0.95), "
        "余量 ≥ 判据 0.60 ✅。",
    ),
    # ---- R_ILIM ----
    "mech_rilim_recommended_ohm": (
        "390",
        "★ISS-107 同型更正 (2026-11-06): 原值 '470' 是**结构侧 10-28 的建议值**; "
        "**老板 10-28 拍板『边戴边充不允许』⇒ 390Ω** (ICHG 0.822A / 单 pin 0.411A / 充电 ~29min), "
        "网表 R_ILIM 行已是 390Ω。⇒ 本条 '建议' 已被拍板取代, 现行值 = 390。"
        "★注意: 本域另一条 claim 'r_ilim_set' 已写 390ohm ⇒ 原值 470 与它自相矛盾。",
    ),
    # ---- skeleton_extent: 消除"待规范化" ----
    # ★★ 必须同时给显式 canon: hw-lead 那条的 value 同串, 但它带 canon='止于PCB段后缘';
    #    而 canon_of('止于PCB段后缘@Z=60.00mm') = '止于pcb段后缘@z=60.00mm' (小写化) ⇒ 两者不等 ⇒ 反而判冲突!
    #    ⇒ 只能像 ISS-107 (pcb_mounting) 那样**显式给 canon 字段** 逐字节对齐。
    "skeleton_extent": (
        "止于PCB段后缘@Z=60.00mm",
        "★ISS-107 同型更正 (2026-11-06): 原值 '止于PCB段后缘' 是**散文** (中文占比高) ⇒ "
        "合并器判它 noncanonical ⇒ 与 hw-lead 的同义值 '止于PCB段后缘@Z=60.00mm' **无法机器比较** ⇒ "
        "在【待规范化】清单里挂了整周。改成与 hw-lead **逐字节同串 + 同 canon** ⇒ 该项立即消。"
        "语义不变: 金属骨架/石墨止于 PCB 段后缘 (板坐标 X=60.00mm), "
        "延伸进电池段 = 并联热路 4.50→皮肤侧热量 92.5%→95.7% (MECH/CLEARANCE_FIX.md)。",
    ),
}

# 需要**显式 canon** 的 key (⇒ 与 hw-lead 的 canon 逐字节对齐, 否则反而制造冲突)
# canon_of() 会 lower() 整串 ⇒ 中文字串两侧若不显式给 canon, 永远对不上
CANON = {
    "skeleton_extent": "止于PCB段后缘",
}

# =====================================================================
# ② **不改值**、只追加 note 的 key (记的是"某一轮的结论"这个事实本身)
#    —— 改值反而丢历史, 但必须标清"不代表现行基线", 否则下游会拿旧数当现行结论
# =====================================================================
ANNOTATE = {
    "mech_hinge_stack_declared_mm": (
        "49.62",
        " | ★2026-11-06 标注: 本值是 **40p 声明版**的堆叠 (10-28 那轮的 P9 页口径), "
        "随 demo 跨铰链取消 (11-02) **已不适用于任何现行板** ⇒ **仅供追溯, 不代表现行基线**; "
        "现行 demo 无跨铰链, 整机阶段重算见 MECH/rebase_20261106.py。",
    ),
    "mech_hinge_stack_fixed_mm": (
        "24.00",
        " | ★2026-11-06 标注: 本值是 **收敛版 (16p/20p/4p/8p)** 的堆叠, 同上**仅供追溯**; "
        "现行板无跨铰链。",
    ),
    "mech_hinge_stack_vertical_mm": (
        "27.0",
        " | ★2026-11-06 标注: 本值是**触点区口径**的铰链区垂直堆叠 (10-28 那轮), "
        "对应净高分母 37.0mm (已作废的叠放模型); 物理 FPC 带宽口径是 31.00mm vs 净高 38.00mm (余 7.00)。"
        "★两值均随 demo 跨铰链取消而**仅供追溯**。",
    ),
    "hinge_stack_v": (
        "31.00mm",
        " | ★2026-11-06 标注: 物理 FPC 带宽口径 (4条×2×0.50 走线边距) vs 净高 38.00 ⇒ 余 7.00mm; "
        "★随 demo 跨铰链取消 (11-02) **仅供追溯**。",
    ),
    "hinge_stack_touch_zone": (
        "27.00mm",
        " | ★2026-11-06 标注: 触点区口径 (10-28 那轮); **仅供追溯** (demo 无跨铰链)。",
    ),
    "hinge_fpc_topology": (
        "H向径向嵌套",
        " | ★2026-11-06 标注: 本拓扑建议是 10-28 那轮针对**4 条**跨铰链链路给的; "
        "demo 取消跨铰链后该建议**当期不适用**, 整机阶段需按新的连接器集合重判。",
    ),
    "mech_hinge_chg_path_resistance_mohm": (
        "37-111",
        " | ★2026-11-06 标注: 铰链段总电阻 (口径A保守 110.8 / B乐观 37.0 mOhm) —— "
        "**该数与跨铰链在不在 demo 无关** (它算的是 J_CHG 这条链路本身的载流特性), "
        "整机阶段仍有效; ★只有 note 里引用的净高 37.0 (旧叠放模型) 已作废, 现行 38.00。",
    ),
    "temple_cross_section": (
        "7.30x38.00x130.00mm",
        " | ★2026-11-06 标注: 三条锁死尺寸链本身**不变**; "
        "★但**板宽 30 (V 向) 吃 V 链** ⇒ 根部净高余量 17.00 → **2.00mm (最坏 1.40)**, "
        "板宽硬顶 **31.40mm** (见 temple_v_margin / pcb_board_width)。",
    ),
    "pcb_mounting": (
        "2x⌀2.0H7+2x⌀1.4",
        " | ★2026-11-06 复核: 原 ISS-107 更正**仍然成立** (value + canon 与 hw-lead 逐字节对齐 ⇒ "
        "合并器 pcb_mounting 冲突 0); ★但 **板宽 15→30 后 Y 坐标全作废** "
        "(P1/P2 Y=7.50 / S1 Y=2.50 / S2 Y=12.50 是 15mm 板口径) ⇒ "
        "板宽 30 的 Y 坐标按 hw-lead ISS-118 重定 (P1/P2 Y=15.00 / S1 Y=2.50 / S2 Y=27.50), "
        "结构侧已按新 Y 重生成 Rev B 打印包 (MECH/print/gen_print_pack_revb.py)。",
    ),
}

# =====================================================================
# ③ 本轮**新增**的 key (新算出来的数)
# =====================================================================
NEWCLAIM = [
    ("mech_temple_v_margin_30mm",
     "2.00mm(最坏1.40)",
     "★板宽 30 (老板 10-29 拍板) 后 V 链余量: 需求 = 板宽 30.00 + 走线槽 6.00 = 36.00, "
     "可用 = 根部净高 38.00 ⇒ 余 **2.00mm** (最坏 1.40) ✅ 过判据 0.60; "
     "★板宽 15 时余量 17.00 ⇒ **板宽 30 吃掉 15.00mm**; "
     "★板宽**硬顶** = 38.00 − 6.00 − 0.60 = **31.40mm** (板宽 30 距顶只剩 1.40)。"
     "H/L 链与电池空间**一字不动** (串行排布 ⇒ 板宽只吃 PCB 段的 V)。",
     "MECH/rebase_20261106.py §1 + MECH/fit_check_v3_30mm.py"),
    ("mech_pcb_area_spare_mm2",
     "122.3mm2",
     "★板宽 30 后的**面积余量** (板框 60×30 = 1800mm²): RK3576 基线双面贴 land 总量 1207.9mm² "
     "(器件 871.5 + SoC 逃线框 336.4) ⇒ 双面贴需 1677.7 ⇒ **装得下, 余 122.3mm²** ✅ "
     "(land 占比 67.1%); 单面贴缺 213.2mm² ❌ ⇒ **必须双面贴**。"
     "★RK3588 在同板框下**缺 497.3mm²** ⇒ 板宽 30 不是装得下的通行证, 是先把地板抬到 30 再看芯片。",
     "HW/pcb60x30_check.json sec3_area (ISS-118 实算) + MECH/rebase_20261106.py"),
    ("mech_hinge_drops_demo",
     "1(J_CHG)",
     "★demo 形态下**唯一还挂 HINGE 板级**的连接器 = J_CHG (1×10p@0.5mm, 网表实测 15 行 HINGE 板级); "
     "CONN_CAM (31p@0.3mm) 与 CONN_LIGHT (22p@0.5mm) 已改为**板内** (board=MAIN_PCB), "
     "CONN_USB 整条删除 ⇒ 跨铰链链路数 4 → **1**。"
     "★但 J_CHG 这条**不代表 demo 要保留跨铰链** (11-02 决策 N5: 充电板并板 / demo 直接 USB 供电) ⇒ "
     "网表的 HINGE 归属**尚未随决策更新**, 属 netlist 与决策文档的**已知不一致**, 已登记 needs。",
     "MECH/rebase_20261106.py §4 (现场解析 HW/netlist_v1.csv) + HW/DEMO_BOARD_HW_DECISION.md §5-N1/N5"),
    ("mech_stale_claims_found",
     "9条",
     "★2026-11-06 自查: 本域分片 180 条 interface_claims 里, **9 条带过期口径 token**, "
     "其中 **8 条的值本身已过期** (7 条已改值 + 1 条 skeleton_extent 改同串消待规范化) "
     "+ 6 条历史值只加标注不改值。"
     "★★**关键认知**: 合并器只报**有对手方**的冲突 (本域冲突 0) ⇒ "
     "**没有对手方的过期值, 合并器根本检不出来** ⇒ 这才是 ISS-107 的完整形态 "
     "(原单只处理了有对手方的那一半)。"
     "★扫描器: MECH/rebase_20261106.py §6 (只扫 value 字段, 不扫 note ⇒ 不误伤历史记录)。",
     "MECH/rebase_20261106.py §6 + §7"),
]

# =====================================================================
# ④ 本轮新增 needs_from (要别人回答什么 —— 走项目总工, 不直接联系其他总工)
# =====================================================================
NEWNEED = [
    ("mech_rebase_netlist_hinge_mismatch",
     "main",
     "★网表与 11-02 demo 决策的**已知不一致** (2026-11-06 自查发现): "
     "DEMO_BOARD_HW_DECISION §5-N1/N5 写「CONN_CAM/CONN_LIGHT 去掉 HINGE 板级归属」+"
     "「J_CHG 不再跨铰链, 充电 IC 与电池位改 DNP 占位」, "
     "但 HW/netlist_v1.csv (11-05 10:57) 现状 = **CONN_CAM/CONN_LIGHT 已是 board=MAIN_PCB ✅ (N1 已落)** "
     "而 **J_CHG 仍是 board=HINGE ❌ (N5 未落) + CHG_BOARD 仍有 92 行 (76 必装) 未转 DNP**。"
     "★结构侧的影响: J_CHG 这条跨铰链链路若保留 ⇒ 铰链区那整套结构结论 (V 向堆叠/径向/铰链端 X 缺口) "
     "在 demo 阶段**仍需成立**; 若按 N5 取消 ⇒ 铰链区结构需求整体转入**整机阶段**。"
     "★我的假设 (不回应我就按这个走): **demo 阶段按 N5 取消 J_CHG 跨铰链** ⇒ "
     "本域铰链区结论 (ISS-085/089/091) 转 deferred 到整机阶段, **demo 板不做铰链结构**; "
     "但**J_CHG 1×10p 的选型/载流/机械结论保留** (整机阶段直接复用)。",
     "2026-11-06",
     "2026-11-13"),
    ("mech_rebase_pcb_width_y_holes",
     "hw-lead",
     "★ISS-107 同型数据一致性问题 (2026-11-06 自查, 需你确认后我才改文档): "
     "**PIN-SET-2 的 Y 坐标在板宽 15→30 之后全部作废**, 而我方多份 MECH 文档里还写着 15mm 板的 Y 值。"
     "现状三方不一致: (a) 本域 claim 'pcb_mounting' 的 note = 旧 Y (7.50/2.50/12.50) "
     "(b) HW/pcb60x30_check.json sec4_holes (RK3576) = **P1(8.00,15.00) / P2(52.00,15.00) / "
     "S1(8.00,2.50) / S2(52.00,27.50)** (c) 我 11-01 已按 (b) 重生成 Rev B 打印包 "
     "(MECH/print/gen_print_pack_revb.py, 自检 93/93 + 38/38 rc=0)。"
     "★请确认 (b) 是定版 ⇒ 我就把 MECH/ 里引用的旧 Y 值统一订正 (不改你的文件)。"
     "★另: 你的 NETLIST_REV2_SPEC §1.2 写 CONN_LIGHT = 40p/0.5mm, 而网表实际落地 = **22p** "
     "(FH12-22S-0.5SH(55), 11-04 定稿, 针序照 RPi5 J4) ⇒ 两个上游文件口径不一致, "
     "本域 claim 取网表实测, 请你确认哪个为准。",
     "2026-11-06",
     "2026-11-13"),
]


def main() -> int:
    dry = "--dry-run" in sys.argv
    d = load_fragment(AGENT)
    claims = d.get("interface_claims") or []
    by_key = {c.get("key"): c for c in claims}
    print(f"[frag_rebase] 分片现有 interface_claims {len(claims)} 条")

    n_revalue = n_annotate = n_new = 0
    for k, (val, note) in REVALUE.items():
        c = by_key.get(k)
        if c is None:
            print(f"  ⚠️ {k}: 分片里没有这条 claim ⇒ 跳过 (不凭空造)")
            continue
        old = c.get("value")
        c["value"] = val
        c["note"] = (c.get("note") or "") + note
        if k in CANON:
            c["canon"] = CANON[k]
            print(f"  ✏️ 改值+canon {k}: {old!r} → {val!r} (canon={CANON[k]!r})")
        else:
            print(f"  ✏️ 改值 {k}: {old!r} → {val!r}")
        n_revalue += 1
    for k, (val, extra) in ANNOTATE.items():
        c = by_key.get(k)
        if c is None:
            print(f"  ⚠️ {k}: 分片里没有这条 claim ⇒ 跳过")
            continue
        assert c.get("value") == val, f"{k} 现值与预期不符: {c.get('value')!r} != {val!r}"
        c["note"] = (c.get("note") or "") + extra
        n_annotate += 1
        print(f"  📌 加标注 {k} (值不变: {val!r})")
    for key, value, note, ref in NEWCLAIM:
        if key in by_key:
            print(f"  ⚠️ {key}: 已存在 ⇒ 不重复加")
            continue
        claims.append({"key": key, "value": value, "note": note, "ref": ref})
        n_new += 1
        print(f"  ➕ 新增 {key} = {value!r}")

    if dry:
        print("[dry-run] 未落盘")
        return 0

    def mutate(doc):
        doc["interface_claims"] = claims
        doc.setdefault("needs_from", [])
        have = {n.get("key") for n in doc["needs_from"]}
        for key, to, item, since, due in NEWNEED:
            if key in have:
                continue
            doc["needs_from"].append({
                "key": key, "to": to, "item": item, "since": since, "due": due,
                "waiting_on": "agent",
            })
            print(f"  ➕ 新增 need {key} → {to} (due {due})")

    update_fragment(AGENT, mutate)
    print(f"\n[frag_rebase] ✅ 已原子写回 {AGENT} 分片 "
          f"(改值 {n_revalue} · 加标注 {n_annotate} · 新增 {n_new} · 新增 need {len(NEWNEED)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
