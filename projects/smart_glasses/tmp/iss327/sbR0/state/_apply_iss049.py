#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-049 一次性分片更新器 (原子写, 走 state/frag_write.py 的 update_fragment)

纪律: 只写 hw-lead 自己的分片; 禁止 open(p,"w")。
内容: PCB 固定孔位改版 (PIN-SET-2) + 骨架长度上限 + 石墨铺装范围 + 6 条接口请求。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from frag_write import update_fragment  # noqa: E402

FULL = "P1(8,7.5)P2(52,7.5)S1(8,2.5)S2(52,12.5)"


def claim(d, key):
    for c in d.get("interface_claims") or []:
        if c.get("key") == key:
            return c
    return None


def upsert(d, key, value, note, ref, canon=None):
    c = claim(d, key)
    if c is None:
        c = {"key": key, "value": value, "note": note, "ref": ref}
        d.setdefault("interface_claims", []).append(c)
    else:
        c["value"] = value
        c["note"] = note
        c["ref"] = ref
    if canon is not None:
        c["canon"] = canon
    return c


def mutate(d):
    # ---------- ① pcb_mount_holes_xy: ISS-105 旧值 -> PIN-SET-2 (原地更新, 不产生重复 key) ----------
    c = claim(d, "pcb_mount_holes_xy")
    assert c is not None, "pcb_mount_holes_xy 缺失"
    c["value"] = FULL
    c["note"] = ("★ISS-049 定版 PIN-SET-2 (板 60x15, 原点左下角, X=板长0..60 铰链端在X=0, Y=板宽0..15): "
                 "P1(8.00,7.50) ⌀2.0H7 主定位(配骨架压装⌀2.0 h6圆销, 全基准) + P2(52.00,7.50) ⌀2.0H7 副定位"
                 "(配菱形销对边1.94, 只定Y, 消过定位) + S1(8.00,2.50)/S2(52.00,12.50) ⌀1.4 M1.2 压紧孔(纯压紧零定位); "
                 "★4/4孔与 SoC 逃线带 X[20.20,31.80] 2D 重叠 = 0.000mm² (HW/pinset2_check.py rc=0); "
                 "老口径(2xM1.2+1x⌀2.0H7 @边距2.50) 在 15mm 板下 3/3 孔压带 -> 作废; "
                 "★本单把 ISS-105 的旧值(单销 H7(15,7.5)) 改掉, 板框不变")
    c["ref"] = "HW/PCB_FIXING_PINSET2.md#3"

    # ---------- ② pcb_mounting: 与 mech-lead 同 key → 合并器会把"方案已变"报成冲突 (要 PM 裁) ----------
    upsert(d, "pcb_mounting", "PIN-SET-2:2x⌀2.0H7+2x⌀1.4",
           "★PCB 固定方式定版 (ISS-049): 定位全部由骨架压装的 ⌀2.0 H7 销承担 (P1圆销全基准 + P2菱形销只定Y); "
           "2xM1.2 降级为纯压紧 (⌀1.4 过孔, 径向间隙0.10/边, 零定位功能); 打印件只留 ⌀2.4 间隙孔 => 打印公差不进定位链; "
           "★mech-lead 的旧值 '2xM1.2+1x⌀2.0H7' 已过期 —— 合并器会报冲突, 请 PM 转告 mech 更新",
           "HW/PCB_FIXING_PINSET2.md#3.1")

    # ---------- ③ skeleton_extent: 任务指定的登记项 (canon 与 mech 同串, 不产生假冲突) ----------
    upsert(d, "skeleton_extent", "止于PCB段后缘@Z=60.00mm",
           "★任务指定登记项; 金属骨架/石墨不得延伸进电池段 (否则新增并联热路 4.50 K/W, 进皮肤热量 92.5%->95.7%); "
           "数值化: PCB 段后缘 = 板坐标 X=60.00mm (板长 60 定版), 电池段起点 = 60.00mm; 建议实现 58.00mm "
           "(退2.00: 与电池段前沿件>=1.0空气隙 + 上壳后端壁0.8 + 合缝0.2); 复算见 HW/pinset2_check.py ③④节",
           "HW/PCB_FIXING_PINSET2.md#4", canon="止于PCB段后缘")

    # ---------- ④ 骨架 / 石墨 的数值化取值 ----------
    upsert(d, "skeleton_max_len", "60.00mm",
           "金属骨架沿镜脚轴向的**硬**长度上限 = PCB 段后缘 (板坐标 X=60.00); 建议实现 58.00mm; "
           "骨架在 SoC 段 (X 19..33) V 向必须满板宽 15.00mm (SoC10.00+两侧3.50横向扩散), 其余段>=10.00mm; 厚1.00铝; "
           "安装面铣削平面度<=5µm; ⚠️重量: 满宽 2.43g/侧(4.86g/对)判死, 台阶形1.81g/侧(3.62g/对)超 MECH '+1-3g' 0.62g → 截面形状待 mech 定",
           "HW/PCB_FIXING_PINSET2.md#4")

    upsert(d, "graphite_cover_x", "0.00-60.00mm",
           "石墨片轴向铺装范围 (与 PCB 段同长); 硬上限 60.00mm = PCB 段后缘, 不得进电池段 (同 skeleton_extent); "
           "前端默认止于板前缘 Z=0 (是否可延伸进铰链端余量区待 mech 授权)",
           "HW/PCB_FIXING_PINSET2.md#5")

    upsert(d, "graphite_cover_y", "0.00-15.00mm",
           "石墨片 V 向铺装范围 = 满板宽; 依据: SoC 10.00mm + 两侧各 3.50mm 横向热扩散通道 (12mm 板宽时该通道被板边物理截断); "
           "石墨贴在骨架外侧面, 与上壳内壁之间留 0.30mm (待 mech 确认 H 链)",
           "HW/PCB_FIXING_PINSET2.md#5")

    upsert(d, "graphite_thk", "0.30mm",
           "石墨片厚 [推算] 柔性石墨膜常用档; ⚠️MECH_BUDGET 未给石墨厚度, 且未进 PCB 段 H 链 (4.20mm) → 已列接口请求请 mech 补; "
           "单片重量 0.54g (900mm2 x 0.30mm x 2.00 g/cc)",
           "HW/PCB_FIXING_PINSET2.md#5")

    upsert(d, "pcb_mount_scheme", "PIN-SET-2",
           "方案代号: 双 ⌀2.0 H7 定位销孔 (骨架压装销, 打印件只留 ⌀2.4 间隙孔) + 2x⌀1.4 M1.2 压紧孔 (对角分布, 压紧力矩对角); "
           "与 ISS-105 的单销初版不同, 以 HW/PCB_FIXING_PINSET2.md 为准",
           "HW/PCB_FIXING_PINSET2.md#3")

    upsert(d, "pcb_mount_dowel_hole", "⌀2.0 H7",
           "PCB 侧定位销孔 (P1 圆销全基准 / P2 菱形销对边1.94 只定Y); 配骨架压装 ⌀2.0 h6 销, 滑配径向间隙 0.008-0.041mm; "
           "定位链 = 骨架铣削面<=5µm + H7销 => 重复性<=0.046mm, 打印公差(±0.30)不进定位链",
           "HW/PCB_FIXING_PINSET2.md#3.1")

    upsert(d, "pcb_mount_screw_hole", "⌀1.4",
           "PCB 侧 M1.2 压紧孔 (过孔, 径向间隙0.10/边 => 零定位功能, 只提供压紧力); "
           "★螺钉从皮肤侧穿入, 头压 PCB 皮肤侧 ⌀2.4x0.6 沉孔, 严禁压皮肤侧下壳 (否则金属跨过隔热层=新并联热路); 隔热垫在2处开⌀3.0让位孔",
           "HW/PCB_FIXING_PINSET2.md#3.4")

    upsert(d, "pcb_mount_hole_windows", "X[4,12]+X[46,56]",
           "★孔位窗口规则: 布局冻结前所有固定/压紧孔必须落在 X[4,12] 与 X[46,56] 两个窗口内 (SoC 逃线带 X[20.20,31.80] 不动); "
           "给 eMMC/SPI-NOR 与铰链端4条连接器的落位留余量 —— 将来布局变动只平移孔位, 不改板框",
           "HW/PCB_FIXING_PINSET2.md#3.3")

    upsert(d, "mount_screw_insert_side", "skin-side",
           "M1.2 压紧螺钉的穿入方向 = 皮肤侧 (往骨架里拧); 螺钉头落 PCB 皮肤侧沉孔; "
           "★隔热层必须在 SoC 与皮肤之间 => 螺钉头不得接触下壳, 隔热垫2处开⌀3.0让位孔; "
           "螺钉热旁路已量化: 2颗并联 9.6 K/W (M1.2钢, 有效导热长1-3mm) → 交 mech 入热模型",
           "HW/PCB_FIXING_PINSET2.md#6")

    upsert(d, "mount_screw_count", "2",
           "2 颗 M1.2 压紧 (对角分布, 分居销轴两侧, 防板绕销轴翘); 骨架上两个攻丝孔不在同一侧 => 多一个方向加工面 (mech N2 的延续, 建议保留对角)",
           "HW/PCB_FIXING_PINSET2.md#3.1")

    upsert(d, "temple_segment_order", "PCB-hinge/cell-tail",
           "★本单骨架/石墨上限建立在这个前提上: 沿镜脚轴向, PCB 段在铰链端 (BOARD_WIDTH_15MM §2.4 明写'铰链端 PCB 段'), "
           "电池段在尾端 => 'PCB 段后缘' = PCB 板坐标 X=60.00 = 电池段起点; 请 mech 确认 (若顺序相反, 骨架上限与石墨范围要重定)",
           "HW/PCB_FIXING_PINSET2.md#4")

    # ---------- ⑤ 接口请求 (6 条: 5 给 mech-lead, 1 给 main) ----------
    needs = d.setdefault("needs_from", [])
    new_needs = [
        {"key": "iss049_skeleton_profile", "to": "mech-lead", "since": "2026-10-28",
         "item": "骨架截面形状 + 重量口径 (ISS-049): 满宽 60x15x1.0 铝 = 4.86g/对 已判死; 台阶形(SoC段X19..33满宽15.00, 其余10.00)=1.81g/侧=3.62g/对, "
                 "仍超 MECH_BUDGET §2.4 B '+1-3g' 0.62g。请定截面形状(台阶/U形/槽形)并复核重量口径; 另: 骨架后端面与电芯前壁建议留>=1.0mm 空气隙(骨架做58.00mm而非60.00mm)"},
        {"key": "iss049_graphite_hchain", "to": "mech-lead", "since": "2026-10-28",
         "item": "石墨厚度与装配位置 (ISS-049): 石墨 0.30mm 未进 PCB 段 H 链 (4.20mm: 外壁0.8+骨架1.0+PCB0.8+空隙0.3+隔热垫0.5+皮肤壁0.8) "
                 "=> 要么石墨占骨架外侧空隙(链要+0.30), 要么它不是'面内扩展到镜腿上表面'的原件; 请在下一版 H 链补上并给装配位置; "
                 "另: 骨架/石墨前端(Z<0) 是否允许延伸进铰链端余量区以增大前端对流面 (默认按不延伸)"},
        {"key": "iss049_mount_screw", "to": "mech-lead", "since": "2026-10-28",
         "item": "螺钉穿入方向与打印件配合 (ISS-049): M1.2 必须从皮肤侧穿入拧进骨架, 头落 PCB 皮肤侧 ⌀2.4x0.6 沉孔; "
                 "★螺钉头严禁接触皮肤侧下壳 (否则金属跨过 0.50隔热垫+0.30空气隙 = 新并联热路); 隔热垫需在2处螺钉位开 ⌀3.0 让位孔; "
                 "上壳需 2x⌀2.4 + 2x⌀1.6 让过孔; 请确认 FDM 沉孔可打性(层纹方向)与装配顺序"},
        {"key": "iss049_hole_windows", "to": "mech-lead", "since": "2026-10-28",
         "item": "固定孔窗口需锁定 (ISS-049): PCB 固定/压紧孔已定在 X[4,12] 与 X[46,56] 两个窗口 (P1/S1@X=8, P2/S2@X=52), "
                 "SoC 逃线带 X[20.20,31.80] 不动; 但铰链端 4 条跨铰链连接器 (54触点) 的 X 占位仍未定 (我 ISS-105 的 F-2), "
                 "eMMC/SPI-NOR 也未落位 => 请锁连接器占位, 否则将来孔位要平移"},
        {"key": "iss049_segment_order", "to": "mech-lead", "since": "2026-10-28",
         "item": "镜脚轴向分段顺序确认 (ISS-049): 我按 'PCB 段在铰链端、电池段在尾端' 取值 (依据 BOARD_WIDTH_15MM §2.4 '铰链端 PCB 段' + "
                 "CLEARANCE_FIX §3.1 电池段前端壁引电极), 因而 'PCB 段后缘' = 板坐标 X=60.00 = 电池段起点, 骨架/石墨上限建立在此之上; 请确认"},
        {"key": "iss049_budget_version", "to": "main", "since": "2026-10-28",
         "item": "MECH_BUDGET 版本口径 (ISS-049): 任务写'与 MECH_BUDGET v1.2 对齐', 但 MECH/MECH_BUDGET.md 文件头仍标 v1.1 ('首轮预算'), "
                 "我按 v1.1 正文 + MECH/BOARD_WIDTH_15MM.md (10-28) 两份对齐并逐条列了表; 请确认结构侧是否另有 v1.2 修订版, 若在我手上我再核一遍"},
    ]
    for n in new_needs:
        assert not any(x.get("key") == n["key"] for x in needs), f"need key 已存在: {n['key']}"
        needs.append(n)

    # ---------- ⑥ 产出登记 ----------
    arts = d.setdefault("artifacts", [])
    new_arts = [
        {"path": "HW/PCB_FIXING_PINSET2.md", "kind": "doc", "version": "1.0", "updated_at": "2026-10-28",
         "summary": "ISS-049 主文件: PCB 固定孔位改版 PIN-SET-2 (2x⌀2.0H7 定位销孔 + 2x⌀1.4 M1.2 压紧孔, 孔位图) + 骨架长度上限 60.00mm(建议58.00) + 石墨铺装 X[0,60]xY[0,15]x0.30 + 热路逐条复核(隔热层未动/螺钉不跨隔热层/4.50K/W 并联热路不成立) + 6 条接口请求"},
        {"path": "HW/pinset2_check.py", "kind": "script", "version": "1.0", "updated_at": "2026-10-28",
         "summary": "ISS-049 机械复算脚本 (rc=0): 36 项 (孔位几何/老口径失效/骨架石墨上限/热路/挠度) + 生成 JSON 与 SVG 孔位图"},
        {"path": "HW/pinset2_check.json", "kind": "data", "version": "1.0", "updated_at": "2026-10-28",
         "summary": "ISS-049 机读复算结果 (35/36 通过, WARN 1 = 骨架重量超 MECH 口径)"},
        {"path": "HW/pinset2_holes.svg", "kind": "drawing", "version": "1.0", "updated_at": "2026-10-28",
         "summary": "ISS-049 孔位图 (矢量 10px/mm): 板框 60x15 + SoC 逃线带 + SoC + J_CHG keep-out + 4 个固定孔 + 骨架/石墨覆盖范围"},
        {"path": "HANDOFF/2026-10-28_hw-lead_ISS049_定位孔位与骨架石墨范围.md", "kind": "handoff", "version": "1.0",
         "updated_at": "2026-10-28", "summary": "ISS-049 交接单 (B1-B6 六块齐全)"},
    ]
    for a in new_arts:
        if not any(x.get("path") == a["path"] for x in arts):
            arts.append(a)

    # ---------- ⑦ 状态 ----------
    d["updated_at"] = "2026-10-28T08:40:00+08:00"
    d["updated_by"] = "hw-lead"
    d["status"] = {
        "phase": "P2(原理图/BOM)+结构接口",
        "progress_pct": 50,
        "health": "red",
        "summary": ("ISS-049 闭: PCB 固定方式定版 PIN-SET-2 = 2x⌀2.0H7 定位销孔(P1(8,7.5)圆销全基准 / P2(52,7.5)菱形销只定Y) + "
                    "2x⌀1.4 M1.2 压紧孔(S1(8,2.5)/S2(52,12.5), 纯压紧零定位); 4/4孔与 SoC 逃线带 X[20.20,31.80] 重叠 0.000mm²; "
                    "老口径(2xM1.2+1x⌀2.0H7@边距2.50)在15mm板下 3/3孔压带(0.50/2.00x2.00)已机械判死 -> 作废; "
                    "骨架长度上限 60.00mm(止于PCB段后缘, 建议实现58.00退2.00给电芯前壁空气隙), 石墨铺装 X[0,60]xY[0,15]x0.30; "
                    "★隔热层未牺牲(0.50垫+0.30空隙 R=165.1K/W), 新增硬约束: 螺钉头只压PCB皮肤侧沉孔严禁压下壳(否则金属跨隔热层), "
                    "隔热垫2处开⌀3.0让位孔; 新引入螺钉热旁路 2颗并联 9.6K/W 已量化交mech; "
                    "⚠️骨架重量 满宽4.86g/对判死/台阶3.62g/对超MECH口径0.62g -> 截面形状待mech; "
                    "新增12条interface_claims(含任务指定的 skeleton_extent, canon与mech同串不判冲突)+6条接口请求+5条产出; "
                    "未改MECH/SW/tracker/netlist/BOM, 未碰他人分片, 未联系供应商; merge rc=0 + gate Q1 18/18"),
    }


if __name__ == "__main__":
    update_fragment("hw-lead", mutate)
    print("[apply_iss049] ✅ hw.yaml 已原子更新")
