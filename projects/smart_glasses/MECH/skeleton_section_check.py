#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MECH/skeleton_section_check.py —— 金属骨架截面形状 + 重量口径 + 石墨 H 链 的独立复算
=====================================================================
★★ISS-192 迁版 (2026-11-11): 本脚本原基线是 **60×15 板 + RK3588 8×10 封装**,
   该基线已随「板宽 15→30 / 主控换 RK3576」作废 ⇒ 现按 **60×30 板 + RK3576
   (17.20 × 16.10mm)** 复算。★**30mm 不是 15mm 的等比放大**, 三件事都变了:
   ① SoC 沿板宽占 **8.00 → 16.10mm** (近乎翻倍) ⇒ 横向热扩散通道
      **(15−8)/2=3.50 → (30−16.10)/2=6.95mm/边**;
   ② SoC 沿板长占 10.00 → **17.20mm** ⇒ 满宽段变长;
   ③ 满宽段宽度 15.00 → **30.00mm (满板宽)** ⇒ **骨架重量全线上升**,
      本脚本重出的结论是: **30mm 下所有金属骨架候选都超 MECH_BUDGET §2.4 B 的
      「+1~3g/对」预算** (最好候选 4.08g/对, 超 1.08g) ⇒ 骨架截面**必须重做**,
      这已不是「选 1.0 还是 0.8」的题。★★该超支属**预算裁** (项目总工),
      本脚本只报数不拍板 ⇒ 记为 WARN (不判 rc)。

背景: 硬件总工 ISS-049 有两问**明确把决定权交给结构侧**:
      ① `iss049_skeleton_profile`  "请定截面形状(台阶/U形/槽形)并复核重量口径"
      ② `iss049_graphite_hchain`   "石墨 0.30mm 未进 PCB 段 H 链 ... 请在下一版 H 链补上并给装配位置"

★ 独立复算纪律 (同 `MECH/PCB_MOUNT_PIN_SET2.md` §1.3): **不共用 hw-lead 的代码路径**,
  输入全部显式列在文件头部, 每个数标来源。

★ 口径: 本脚本只做**算术复算 + 几何判定**, **不出新的皮肤侧温度数**
  (那要完整热模型重算, 见 `MECH/PCB_MOUNT_PIN_SET2.md` §5 U-3), **不拍板**
  (最终截面/厚度由项目总工裁)。

用法:
    python3 MECH/skeleton_section_check.py            # 人读报告
    python3 MECH/skeleton_section_check.py --json     # 机读

退出码: 0 = 复算完成 (不代表拍板); 1 = 输入自相矛盾
=====================================================================
"""
from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.join(HERE, "..")

# ---------------------------------------------------------------------
# 输入 (全部来自既有文件, 每条标来源)
# ---------------------------------------------------------------------
AL_DENSITY = 2.70       # g/cc 铝               [官方·通用材料密度]
CU_DENSITY = 8.96       # g/cc 铜 (备选)         [官方·通用材料密度]
GR_DENSITY = 2.00       # g/cc 石墨片 (取 hw-lead ISS-049 报的 0.54g/片 反推的口径) [推算]

# =====================================================================
# ★ISS-345 双口径档位表 (★帧 id 逐字取自 HW/PCB/BOARD_FRAME_CALIBER.md §2 cal:FRAMES★)
#   · ★默认档 = F30A (60×30 / RK3576) —— ★本单【不许自己拍默认档】, 保持现状不变★
#   · 切档 = `--frame B160x100` (或环境变量 MECH_FRAME=B160x100) —— 见 §用法
#   · ★PIN-SET-2 套 A 四孔坐标 (PIN_Y / SCREW_Y_SET_A / SCREW_Y_SET_B) = F30A 帧专有★
#     ⇒ B160x100 帧的【端段 Y 跨度】判据 = 口径不适用 (★先例 MECH/board_frame_feasibility.py:108★)
# =====================================================================
FRAMES = [
    {
        "fid": "F30A",
        "name": "产品板 60×30 套 A (历史产品板口径 · 与台架板口径不可混用)",
        "pcb_l": 60.00, "pcb_w": 30.00, "pcb_thk": 1.00, "layers": 6,
        "soc_model": "RK3576", "soc_pkg": (17.20, 16.10),
        "soc_x0": 15.00, "soc_x_len": 17.20, "soc_y_len": 16.10,
        "esc": 0.80, "hot_band": 6.95,
        "hot_seg_x0": 15.00, "hot_seg_x1": 32.20,
        "seg_w_other": 10.00,
        "pin_y": 15.00, "screw_y_set_a": (10.00, 20.00), "screw_y_set_b": (2.50, 27.50),
        "pinset_applicable": True,
        "src": "MECH/BOARD_GEOM_30MM.md §0/§1/§3 (ISS-118/130, 老板 10-29 19:16 板宽 30) "
               "+ HW/pcb60x30_check.py",
    },
    {
        "fid": "B160x100",
        "name": "台架板 160×100 (盘上现役 · RK3572-SOM 承载区形态)",
        "pcb_l": 160.00, "pcb_w": 100.00, "pcb_thk": 1.60, "layers": 8,
        "soc_model": "RK3572-SOM", "soc_pkg": (56.70, 46.78),
        "soc_x0": 13.65, "soc_x_len": 56.70, "soc_y_len": 46.78,
        "esc": 0.80, "hot_band": 26.61,
        "hot_seg_x0": 13.65, "hot_seg_x1": 70.35,
        "seg_w_other": 10.00,
        "pin_y": None, "screw_y_set_a": None, "screw_y_set_b": None,
        "pinset_applicable": False,
        "src": "HW/PCB/BOARD_FRAME_CALIBER.md §2 cal:FRAMES (行 150-158) + §3 SoM 承载区实测占位 (行 71-72)",
    },
]
DEFAULT_FRAME_ID = "F30A"
FRAME = FRAMES[0]      # ★当前档位 (由 _bind_frame 绑定)★
FRAME_ID = DEFAULT_FRAME_ID

# =====================================================================
# ★ISS-345 双口径 · 帧级叙述表 (★F30A 档逐字保留迁移前文本 ⇒ 默认档输出逐字节不变★)
#   ★每个模板里的 {..} 占位全部来自【帧值 + 本次复算量】, 不含硬编档位数字★
# =====================================================================
PROSE = {
    "F30A": {
        "migrate": "★ ISS-192 迁版: 60×15 / RK3588 8×10 ⇒ **60×30 / RK3576 17.20×16.10**",
        "v_cover_name": "V_cover_need_30mm",
        "v_cover_detail":
            "30mm 板: SoC 沿板宽占 {soc_y:.2f} + 两侧横向扩散带各 {band:.2f} = {vneed:.2f}mm "
            "= 板宽 {w:.2f} -> **骨架在 SoC 段必须满宽 (30.00mm, 即满板宽)** "
            "(★15mm 板时代是 8.00 + 2×3.50 = 15.00, 通道 3.50mm/边; 现通道 {band:.2f}mm/边)",
        "spread_detail":
            "横向热扩散通道 3.50 → **{band:.2f}mm/边** (×{ratio:.2f}) "
            "(SoC 沿板宽 8.00 → {soc_y:.2f}, 板宽 15 → {w:.2f}; 通道宽 = (板宽−SoC宽)/2)",
        "escape_detail":
            "SoC 逃线带 Y 跨度 {sy2e:.2f}mm ≤ 板宽 {w:.2f}mm (余 {emargin:.2f}mm/边)",
        "cand_names": ["A 满宽 60x30x1.0", "B 台阶 X15.00-32.20 满宽30 / 其余10 x1.0",
                       "C 台阶 同上 x0.8", "D 台阶 同上 x0.8 铜"],
        "cand_A_detail":
            "满宽 60×30×1.0 = {m:.2f}g/对 (15mm 板时代是 4.86g/对, 翻倍), "
            "超骨架预算 {d:+.2f}g -> 判死",
        "cand_B_detail":
            "台阶形 t=1.0 = {m:.2f}g/对 (15mm 板时代 3.62g/对), 超骨架预算 {d:+.2f}g",
        "cand_C_detail":
            "台阶形 t=0.8 = {m:.2f}g/对 (15mm 板时代 2.89g/对, 当时落进 +1-3g), "
            "★30mm 下**最好候选也超预算 {d:+.2f}g** => 骨架截面必须重做 "
            "(不再是「选 1.0 还是 0.8」的题)",
        "cand_D_detail":
            "铜台阶形 t=0.8 = {m:.2f}g/对, 超预算 {d:+.2f}g (比铝候选 C 重 {dm:+.2f}g/对) "
            "-> 导热好但重量代价大, 1 台样机阶段不建议",
        "all_cand_detail":
            "★**30mm 板宽下 4 个候选全部超 §2.4 B 的 +1~3g/对 预算** (最好 {m:.2f}g/对); "
            "根因: 满宽段宽度 15.00 → 30.00 且长度 10.00 → {hot_len:.2f}mm "
            "⇒ 满宽段体积 ×{vr:.1f} => ★属**预算裁** (项目总工), 本脚本只报数不拍板; "
            "结构侧可选项: 满宽段只到 SoC 投影 / 横向扩散改由石墨承担 / 骨架改材料分段 "
            "—— 三个选项的重量账待下一轮",
        "graphite_place": "PCB 内侧 = 骨架与 PCB 之间 (与板同长同宽 X∈[0,60]×Y∈[0,30])",
        "graphite_note":
            "15mm 板时代 60×15×0.30 = 0.54g/片 (1.08g/对, 落在 W11 内); "
            "30mm 板 60×30×0.30 = {g:.2f}g/片 ({g2:.2f}g/对) => 超 W11 上限 {d:+.2f}g "
            "⇒ 要么缩石墨覆盖 (只铺 SoC 段+扩散带), 要么调 W11 预算",
        "graphite_detail":
            "石墨 {g:.2f}g/片 = {g2:.2f}g/对 vs W11 的 {lo}-{hi}g "
            "=> ★**超上限 {d:+.2f}g** (板宽翻倍 ⇒ 石墨片重量也翻倍)",
        "hchain_note":
            "PCB 段 H 链 (来源 MECH/BOARD_GEOM_30MM.md §2): 外壁0.8+骨架+PCB1.0+空隙0.3+"
            "隔热垫0.5+皮肤壁0.8; 石墨 0.30 铺在骨架与 PCB 之间 -> 链 +0.30。"
            "★**H 链与板宽无关** (板宽走 V 向)",
        "sec1_title": "\n【1】V 向覆盖需求 (决定截面形状的硬约束) —— 30mm 板",
        "sec1_line":
            "  30mm 板: SoC 沿板宽 {soc_y:.2f} + 两侧横向扩散带各 {band:.2f} = {vneed:.2f}mm "
            "= 板宽 {w:.2f} → SoC 段骨架必须**满宽 30.00mm**",
        "spread_line":
            "  横向热扩散通道 3.50 → **{band:.2f}mm/边** (×{ratio:.2f}) —— 板宽翻倍的**结构收益**",
        "hotseg_line":
            "  SoC 满宽段 X 长度 10.00 → **{hot_len:.2f}mm** (X {hx0:.2f}..{hx1:.2f})",
        "sec2_title": "\n【2】候选截面 (台阶形满宽段 X15.00-32.20) —— 30mm 板",
        "over_budget_line":
            "  ★ **30mm 下 4 个候选全部超 +1~3g/对 预算** (15mm 板时代候选 C = 2.89g/对 是落进预算的)",
        "rootcause_line":
            "  ★ 根因: 满宽段宽 15.00→30.00 且长 10.00→17.20 ⇒ 该段体积 ×3.08 "
            "⇒ 属**预算裁**, 报项目总工",
        "concl_1":
            "  ① 截面形状 = **台阶形** (SoC 段 X15.00–32.20 满宽 30.00 / 其余段 10.00) —— "
            "唯一满足横向扩散带覆盖 (30.00 = 满宽) 又不像满宽那样被判死的方案",
        "concl_2_head": "  ② ★**30mm 下重量全线超支**: 台阶 t=1.0 = {m1:.2f}g/对, ",
        "concl_3":
            "  ③ 石墨 0.30 **铺在 PCB 内侧 (骨架与 PCB 之间)**, 与板同长同宽 -> PCB 段 H 链 +0.30; "
            "H 链余量仍 ≥0.60 (骨架 0.8 时余 2.80mm)。★但石墨片 1.08g/片 = 2.16g/对 "
            "**超 W11 (1-2g)** ⇒ 缩覆盖或调预算",
        "concl_4":
            "  ④ 骨架/石墨**止于 PCB 段后缘** (X=60.00) —— 延伸进电池段 = 金属绕过隔热层直灌皮肤",
        "concl_7":
            "  ⑦ ★**孔位口径**: 套 A 的端段 Y 跨度需求与 ISS-049 §4 的 ≥10.00mm **恰好相容**; "
            "套 B 会把端段要求拉到 17.50mm ⇒ 推翻骨架接口 ⇒ 结构侧否决套 B "
            "(详见 MECH/BOARD_GEOM_30MM.md §4)",
    },
    "B160x100": {
        "migrate": "★ ISS-345 双口径: 60×30 / RK3576 (默认档, 历史产品板口径) ⇒ "
                   "**160×100 / RK3572-SOM 承载区形态** (台架板帧)",
        "v_cover_name": "V_cover_need_100mm",
        "v_cover_detail":
            "100mm 板: SoM 承载区沿板宽占 {soc_y:.2f} + 两侧横向扩散带各 {band:.2f} = {vneed:.2f}mm "
            "= 板宽 {w:.2f} -> **骨架在 SoM 段必须满宽 (100.00mm, 即满板宽)** "
            "(★本档为台架板帧: 无 15mm 产品板沿革可比; 通道 = (板宽−承载区宽)/2 = {band:.2f}mm/边)",
        "spread_detail":
            "横向热扩散通道 3.50 → **{band:.2f}mm/边** (×{ratio:.2f}) "
            "(SoM 承载区沿板宽 {soc_y:.2f}, 板宽 {w:.2f}; 通道宽 = (板宽−承载区宽)/2)",
        "escape_detail":
            "SoM 逃线带 Y 跨度 {sy2e:.2f}mm ≤ 板宽 {w:.2f}mm (余 {emargin:.2f}mm/边)",
        "cand_names": ["A 满宽 160x100x1.0", "B 台阶 X13.65-70.35 满宽100 / 其余10 x1.0",
                       "C 台阶 同上 x0.8", "D 台阶 同上 x0.8 铜"],
        "cand_A_detail":
            "满宽 160×100×1.0 = {m:.2f}g/对 (★台架板帧无 15mm 产品板沿革可比), "
            "超骨架预算 {d:+.2f}g -> 判死",
        "cand_B_detail":
            "台阶形 t=1.0 = {m:.2f}g/对 (★台架板帧无 15mm 沿革可比), 超骨架预算 {d:+.2f}g",
        "cand_C_detail":
            "台阶形 t=0.8 = {m:.2f}g/对 (★台架板帧无 15mm 沿革可比), "
            "★100mm 下**最好候选也超预算 {d:+.2f}g** => 骨架截面必须重做 "
            "(不再是「选 1.0 还是 0.8」的题)",
        "cand_D_detail":
            "铜台阶形 t=0.8 = {m:.2f}g/对, 超预算 {d:+.2f}g (比铝候选 C 重 {dm:+.2f}g/对) "
            "-> 导热好但重量代价大, 1 台样机阶段不建议",
        "all_cand_detail":
            "★**100mm 板宽下 4 个候选全部超 §2.4 B 的 +1~3g/对 预算** (最好 {m:.2f}g/对); "
            "根因: 满宽段宽度 → {w:.2f} 且长度 → {hot_len:.2f}mm "
            "⇒ 满宽段体积 ×{vr:.1f} => ★属**预算裁** (项目总工), 本脚本只报数不拍板; "
            "结构侧可选项: 满宽段只到 SoM 承载区投影 / 横向扩散改由石墨承担 / 骨架改材料分段 "
            "—— 三个选项的重量账待下一轮",
        "graphite_place": "PCB 内侧 = 骨架与 PCB 之间 (与板同长同宽 X∈[0,160]×Y∈[0,100])",
        "graphite_note":
            "★台架板帧: 160×100×0.30 = {g:.2f}g/片 ({g2:.2f}g/对) => 超 W11 上限 {d:+.2f}g "
            "⇒ 要么缩石墨覆盖 (只铺 SoM 承载区段+扩散带), 要么调 W11 预算",
        "graphite_detail":
            "石墨 {g:.2f}g/片 = {g2:.2f}g/对 vs W11 的 {lo}-{hi}g "
            "=> ★**超上限 {d:+.2f}g** (台架板 160×100 板面 ⇒ 石墨片重量按板面计)",
        "hchain_note":
            "PCB 段 H 链 (板厚取 cal:FRAMES B160x100 = 1.60mm): 外壁0.8+骨架+PCB1.60+空隙0.3+"
            "隔热垫0.5+皮肤壁0.8; 石墨 0.30 铺在骨架与 PCB 之间 -> 链 +0.30。"
            "★**H 链与板宽无关** (板宽走 V 向; 但板厚 1.00→1.60 ⇒ 链 +0.60mm)",
        "sec1_title": "\n【1】V 向覆盖需求 (决定截面形状的硬约束) —— 100mm 板",
        "sec1_line":
            "  100mm 板: SoM 承载区沿板宽 {soc_y:.2f} + 两侧横向扩散带各 {band:.2f} = {vneed:.2f}mm "
            "= 板宽 {w:.2f} → SoM 段骨架必须**满宽 100.00mm**",
        "spread_line":
            "  横向热扩散通道 3.50 → **{band:.2f}mm/边** (×{ratio:.2f}) —— 板宽翻倍的**结构收益**",
        "hotseg_line":
            "  SoM 承载区满宽段 X 长度 **{hot_len:.2f}mm** (X {hx0:.2f}..{hx1:.2f})",
        "sec2_title": "\n【2】候选截面 (台阶形满宽段 X13.65-70.35) —— 100mm 板",
        "over_budget_line":
            "  ★ **100mm 下 4 个候选全部超 +1~3g/对 预算** (★台架板帧无 15mm 沿革可比★)",
        "rootcause_line":
            "  ★ 根因: 满宽段宽 → 100.00 且长 → {hot_len:.2f} ⇒ 该段体积 ×{vr:.1f} "
            "⇒ 属**预算裁**, 报项目总工",
        "concl_1":
            "  ① 截面形状 = **台阶形** (SoM 承载区段 X13.65–70.35 满宽 100.00 / 其余段 10.00) —— "
            "唯一满足横向扩散带覆盖 (100.00 = 满宽) 又不像满宽那样被判死的方案",
        "concl_2_head": "  ② ★**100mm 下重量全线超支**: 台阶 t=1.0 = {m1:.2f}g/对, ",
        "concl_3":
            "  ③ 石墨 0.30 **铺在 PCB 内侧 (骨架与 PCB 之间)**, 与板同长同宽 -> PCB 段 H 链 +0.30; "
            "H 链余量仍 ≥0.60 (骨架 0.8 时余 2.20mm)。★但石墨片 9.60g/片 = 19.20g/对 "
            "**超 W11 (1-2g)** ⇒ 缩覆盖或调预算",
        "concl_4":
            "  ④ 骨架/石墨**止于 PCB 段后缘** (X=160.00) —— 延伸进电池段 = 金属绕过隔热层直灌皮肤",
        "concl_7":
            "  ⑦ ★**孔位口径**: ★台架板 160×100 盘上无 PIN-SET-2 四孔 ⇒ 端段 Y 跨度判据"
            "**本档口径不适用** (★先例 MECH/board_frame_feasibility.py:108 "
            "`pinset_applicable: False`★)",
    },
}


def _bind_frame(fid: str) -> dict:
    """★按档位把几何常量绑到模块级变量上 (★默认档 F30A ⇒ 迁移前取值逐字不变★)★

    ★本单【不许自己拍默认档】⇒ 默认 = F30A (60×30 / RK3576) = 保持现状 ★
    ★切默认档 = main 拍完 U-1 后跑 `--frame B160x100` (或 MECH_FRAME=B160x100) ★
    """
    global FRAME, FRAME_ID, PCB_L, PCB_W, PCB_T
    global SOC_X0, SOC_X_LEN, SOC_Y_LEN, ESCAPE, HOT_BAND
    global HOT_SEG_X0, HOT_SEG_X1, SEG_W_OTHER
    global PIN_Y, SCREW_Y_SET_A, SCREW_Y_SET_B
    fr = next((f for f in FRAMES if f["fid"] == fid), None)
    if fr is None:
        raise SystemExit("★未知帧 id %r (可选: %s)★" % (fid, ", ".join(f["fid"] for f in FRAMES)))
    FRAME, FRAME_ID = fr, fr["fid"]
    PCB_L, PCB_W, PCB_T = fr["pcb_l"], fr["pcb_w"], fr["pcb_thk"]
    SOC_X0, SOC_X_LEN, SOC_Y_LEN = fr["soc_x0"], fr["soc_x_len"], fr["soc_y_len"]
    ESCAPE, HOT_BAND = fr["esc"], fr["hot_band"]
    HOT_SEG_X0, HOT_SEG_X1 = fr["hot_seg_x0"], fr["hot_seg_x1"]
    SEG_W_OTHER = fr["seg_w_other"]
    PIN_Y = fr["pin_y"]
    SCREW_Y_SET_A = fr["screw_y_set_a"]
    SCREW_Y_SET_B = fr["screw_y_set_b"]
    return fr

PCB_L = 60.00           # mm 板长              [官方] 10-28 项目总工裁
PCB_W = 30.00           # mm 板宽              [官方] 老板 10-29 19:16 拍板 (§0 台账 11-01 20:5x 订正)
PCB_T = 1.00            # mm 6 层板厚 (取 1.00 保守) [官方] hw-lead proto_pcb_thickness_tier

# SoC 封装体 (RK3576 FCCSP698L) 在**板坐标**里的占位:
#   X∈[15.00, 32.20] = 17.20mm 沿板长(X) ; Y∈[6.95, 23.05] = 16.10mm 沿板宽(Y)
#   [官方] 17.20×16.10mm FCCSP698L, 来源 HW/pcb60x30_check.py SOC_RK3576 + SOC_POS["RK3576"]
#   ★落位居中于板中线 Y=15.00 ⇒ 两侧横向扩散通道各 (30.00−16.10)/2 = 6.95mm
SOC_X0 = 15.00         # mm 板坐标 X 起点
SOC_X_LEN = 17.20      # mm 沿板长
SOC_Y_LEN = 16.10      # mm 沿板宽 (V 向)
ESCAPE = 0.80          # mm 逃线带每边外扩    [推算] HW/SOC_PIN_BUDGET.md (ISS-081)
HOT_BAND = 6.95        # mm 横向扩散带每边 (30mm 板: (30−16.10)/2 = 6.95) [推算] MECH/BOARD_GEOM_30MM §2

SKELETON_T = 1.00      # mm 骨架厚 (hw-lead 台阶形方案取值) [推算] MECH_BUDGET §5.1
SKELETON_T_ALT = 0.80  # mm 备选厚度 (本脚本新增, 见重量账)
HOT_SEG_X0, HOT_SEG_X1 = 15.00, 32.20   # mm 台阶形满宽段的 X 范围 (RK3576 封装投影)
SEG_W_OTHER = 10.00    # mm 非 SoC 段的骨架宽度 [决策] HW/PCB_FIXING_PINSET2.md §4「其余段宽度 ≥10.00mm」

# 非 SoC 段必须覆盖的 Y 跨度 (骨架端段要同时容下定位销孔与 M1.2 凸台)
#   判据: 端段 Y 跨度 ≥ max(销孔Y, 螺钉孔Y) + BOSS_MARGIN − min(...) + BOSS_MARGIN
BOSS_MARGIN = 2.50     # mm 凸台中心到骨架段边缘的最小余量 [推算] M1.2 攻丝凸台 Ø2.6 + 边壁
PIN_Y = 15.00          # 销轴 (P1/P2) 的 Y (套 A: Y 按中心线平移到板中线) [推算] MECH/BOARD_GEOM_30MM §3
SCREW_Y_SET_A = (10.00, 20.00)   # 套 A 的 S1/S2 Y
SCREW_Y_SET_B = (2.50, 27.50)    # 套 B (被否决) 的 S1/S2 Y —— 用于复算其骨架后果

GRAPHITE_T = 0.30      # mm 石墨片厚           [推算] MECH_BUDGET §5.1

# PCB 段 H 链 (来源 MECH/BOARD_GEOM_30MM.md §2 + MECH_BUDGET §2.3)
H_OUTER_WALL = 0.80
H_SKIN_WALL = 0.80
H_AIR_GAP = 0.30       # 隔热垫外侧空气隙
H_INSUL_PAD = 0.50     # 隔热垫 (0.5 硅胶/PI)
TEMPLE_H = 7.30        # mm 镜腿前后厚上限   [决策] 老板 Q4

# 热模型常数 (来源 MECH_BUDGET §2.3, 本脚本**只引用不复算**皮肤温度)
R_SKIN_PATH = 54.2     # K/W 皮肤路径         [推算] MECH_BUDGET §2.3
R_CONV = 667.0         # K/W 对流             [推算] MECH_BUDGET §2.3
R_AL_LONG = 4.50       # K/W 铝骨架纵向 (若延伸进电池段) [推算] MECH_BUDGET §2.3.1 / CLEARANCE_FIX §4.2
R_PRINT_LONG = 730.0   # K/W 打印件纵向        [推算] CLEARANCE_FIX §4.2

# 重量预算
BUDGET_SKELETON_G = 3.00     # g/对  MECH_BUDGET §2.4 B "金属骨架 +1-3g"
W11_GRAPHITE_G = (1.0, 2.0)  # g   MECH_BUDGET §3 W11 "石墨散热膜+导热垫+隔热垫 1-2" (整套)
TOTAL_PROTO_G = (48.9, 74.0)  # g  整机推算区间 [推算] MECH_BUDGET §3


def r6(x: float) -> float:
    return round(x + 1e-12, 6)


def skin_fraction(R_skin_path: float) -> float:
    """进入皮肤的热量比例 = R_conv/(R_skin_path + R_conv)  [MECH_BUDGET §2.3 模型]"""
    return 100.0 * R_CONV / (R_skin_path + R_CONV)


def seg_span_needed(pin_y: float, screw_y: float) -> float:
    """骨架端段必须覆盖的 Y 跨度 (销孔 + M1.2 凸台 都在该段里)。"""
    return (max(pin_y, screw_y) + BOSS_MARGIN) - (min(pin_y, screw_y) - BOSS_MARGIN)


def compute() -> dict:
    r: dict = {"inputs": {}, "checks": [], "candidates": []}
    r["inputs"] = {
        "alu_density_g_cc": AL_DENSITY, "graphite_density_g_cc": GR_DENSITY,
        "pcb_L_mm": PCB_L, "pcb_W_mm": PCB_W, "pcb_t_mm": PCB_T,
        "soc_X0_mm": SOC_X0, "soc_X_len_mm": SOC_X_LEN, "soc_Y_len_mm": SOC_Y_LEN,
        "escape_mm": ESCAPE, "hot_band_each_side_mm": HOT_BAND,
        "skeleton_t_mm": SKELETON_T, "skeleton_t_alt_mm": SKELETON_T_ALT,
        "graphite_t_mm": GRAPHITE_T,
        "hot_seg_X_mm": [HOT_SEG_X0, HOT_SEG_X1], "seg_w_other_mm": SEG_W_OTHER,
        "boss_margin_mm": BOSS_MARGIN,
        "H_chain_parts_mm": {"outer_wall": H_OUTER_WALL, "skeleton": SKELETON_T,
                              "pcb": PCB_T, "air_gap": H_AIR_GAP,
                              "insul_pad": H_INSUL_PAD, "skin_wall": H_SKIN_WALL},
        "temple_H_max_mm": TEMPLE_H,
        "R_skin_path_K_W": R_SKIN_PATH, "R_conv_K_W": R_CONV,
        "R_al_long_K_W": R_AL_LONG, "R_print_long_K_W": R_PRINT_LONG,
        "budget_skeleton_g_per_pair": BUDGET_SKELETON_G,
        "W11_graphite_g": list(W11_GRAPHITE_G),
    }

    def add(name, ok, detail, val=None, level="fail"):
        r["checks"].append({"name": name, "pass": bool(ok), "detail": detail,
                            "value": val, "level": level})

    # ---------- ① V 向覆盖需求 (按档位) ----------
    P = PROSE[FRAME_ID]
    v_need_30 = SOC_Y_LEN + 2 * HOT_BAND
    ctx = {"soc_y": SOC_Y_LEN, "band": HOT_BAND, "vneed": v_need_30, "w": PCB_W,
           "l": PCB_L, "hot_len": HOT_SEG_X1 - HOT_SEG_X0,
           "hx0": HOT_SEG_X0, "hx1": HOT_SEG_X1, "seg_w": SEG_W_OTHER}
    add(P["v_cover_name"], abs(v_need_30 - PCB_W) < 1e-9,
        P["v_cover_detail"].format(**ctx),
        v_need_30)
    band_ratio = HOT_BAND / 3.50
    add("transverse_spread_channel_widened", HOT_BAND > 3.50,
        P["spread_detail"].format(ratio=band_ratio, **ctx),
        HOT_BAND)
    add("escape_band_inside_board", (SOC_Y_LEN + 2 * ESCAPE) <= PCB_W,
        P["escape_detail"].format(sy2e=SOC_Y_LEN + 2 * ESCAPE,
                                  emargin=(PCB_W - SOC_Y_LEN - 2 * ESCAPE) / 2, **ctx),
        (PCB_W - SOC_Y_LEN - 2 * ESCAPE) / 2)

    # ---------- ② 非 SoC 段 Y 跨度需求 (孔位口径的机械后果) ----------
    if FRAME["pinset_applicable"]:
        spans = {}
        for tag, (sy1, sy2) in (("套A", SCREW_Y_SET_A), ("套B", SCREW_Y_SET_B)):
            front = seg_span_needed(PIN_Y, sy1)   # 前段 (X 0..15) 容 P1 + S1
            rear = seg_span_needed(PIN_Y, sy2)    # 后段 (X 32.2..60) 容 P2 + S2
            spans[tag] = {"front": front, "rear": rear, "max": max(front, rear)}
        r["end_segment_span"] = spans
        add("seg_span_setA_fits_10mm_spec", spans["套A"]["max"] <= SEG_W_OTHER + 1e-9,
            f"★套 A (S1 Y={SCREW_Y_SET_A[0]:.2f} / S2 Y={SCREW_Y_SET_A[1]:.2f}): 端段须覆盖 Y 跨度 "
            f"前 {spans['套A']['front']:.2f}mm / 后 {spans['套A']['rear']:.2f}mm "
            f"→ 与 ISS-049 §4「其余段宽度 ≥{SEG_W_OTHER:.2f}mm」**恰好相容** (无富余但也不冲突)",
            spans["套A"]["max"])
        add("seg_span_setB_breaks_10mm_spec", spans["套B"]["max"] > SEG_W_OTHER + 1e-9,
            f"★套 B (S1 Y={SCREW_Y_SET_B[0]:.2f} / S2 Y={SCREW_Y_SET_B[1]:.2f}): 端段须覆盖 Y 跨度 "
            f"前 {spans['套B']['front']:.2f}mm / 后 {spans['套B']['rear']:.2f}mm "
            f"= **{spans['套B']['max'] / SEG_W_OTHER:.2f}×** ISS-049 §4 的 {SEG_W_OTHER:.2f}mm 口径 "
            f"⇒ 套 B 会**推翻骨架接口** (端段须加宽到 {spans['套B']['max']:.2f}mm)",
            spans["套B"]["max"], level="warn")
    else:
        r["end_segment_span"] = {}
        add("seg_span_setA_fits_10mm_spec", True,
            "★本帧口径不适用: 端段 Y 跨度需求由【PIN-SET-2 套 A 四孔的板坐标】推导 "
            "(PIN_Y / SCREW_Y_SET_A / SCREW_Y_SET_B) ⇒ 那是【60×30 套A 帧】专有坐标; "
            "台架板 160×100 盘上无这四个孔 ⇒ 本档不跑本判据 (不假装跑通)",
            "★先例: MECH/board_frame_feasibility.py:108 `pinset_applicable: False` "
            "(★套 A 是 F30A 帧的坐标, 套到台架板帧 = 口径不适用★)",
            level="na")
        add("seg_span_setB_breaks_10mm_spec", True,
            "★本帧口径不适用: 同上 (套 B 是被否决口径, 与板框无关 ⇒ 但其 Y 坐标也是 F30A 帧坐标)",
            "★先例: MECH/board_frame_feasibility.py:108 `pinset_applicable: False`",
            level="na")

    # ---------- ③ 候选截面 (按档位) ----------
    hot_len = HOT_SEG_X1 - HOT_SEG_X0
    rest_len = PCB_L - hot_len

    cands = [
        (P["cand_names"][0], [(PCB_L, PCB_W)], SKELETON_T, AL_DENSITY),
        (P["cand_names"][1], [(hot_len, PCB_W), (rest_len, SEG_W_OTHER)],
         SKELETON_T, AL_DENSITY),
        (P["cand_names"][2], [(hot_len, PCB_W), (rest_len, SEG_W_OTHER)],
         SKELETON_T_ALT, AL_DENSITY),
        (P["cand_names"][3], [(hot_len, PCB_W), (rest_len, SEG_W_OTHER)],
         SKELETON_T_ALT, CU_DENSITY),
    ]
    for name, rects, th, dens in cands:
        vol = sum(w * l * th for (l, w) in rects) / 1000.0
        g_side = vol * dens
        hot_v = PCB_W if any(w == PCB_W for (_, w) in rects) else 0.0
        r["candidates"].append({
            "name": name, "thickness_mm": th, "density_g_cc": dens,
            "volume_cc": r6(vol), "mass_per_side_g": r6(g_side), "mass_per_pair_g": r6(g_side * 2),
            "hot_segment_V_mm": hot_v,
            "v_cover_ok": hot_v >= v_need_30 - 1e-9,
            "vs_skeleton_budget_g": r6(g_side * 2 - BUDGET_SKELETON_G),
        })
    by = {c["name"][0]: c for c in r["candidates"]}
    add("cand_A_full_width_dead", by["A"]["mass_per_pair_g"] > BUDGET_SKELETON_G,
        P["cand_A_detail"].format(m=by["A"]["mass_per_pair_g"],
                                  d=by["A"]["vs_skeleton_budget_g"]), by["A"]["mass_per_pair_g"])
    add("cand_B_step_1mm_mass", by["B"]["mass_per_pair_g"] > BUDGET_SKELETON_G,
        P["cand_B_detail"].format(m=by["B"]["mass_per_pair_g"],
                                  d=by["B"]["vs_skeleton_budget_g"]), by["B"]["mass_per_pair_g"])
    add("cand_C_step_0_8mm_mass", by["C"]["mass_per_pair_g"] > BUDGET_SKELETON_G,
        P["cand_C_detail"].format(m=by["C"]["mass_per_pair_g"],
                                  d=by["C"]["vs_skeleton_budget_g"]),
        by["C"]["mass_per_pair_g"], level="warn")
    add("cand_D_copper_heavy", by["D"]["mass_per_pair_g"] > BUDGET_SKELETON_G,
        P["cand_D_detail"].format(m=by["D"]["mass_per_pair_g"], d=by["D"]["vs_skeleton_budget_g"],
                                  dm=by["D"]["mass_per_pair_g"] - by["C"]["mass_per_pair_g"]),
        by["D"]["mass_per_pair_g"])
    add("all_candidates_over_budget", all(c["mass_per_pair_g"] > BUDGET_SKELETON_G for c in r["candidates"]),
        P["all_cand_detail"].format(m=by["C"]["mass_per_pair_g"], hot_len=hot_len, w=PCB_W,
                                    vr=by["C"]["hot_segment_V_mm"] / 15.0),
        None, level="warn")

    # ---------- ④ 石墨: 重量归 W11 (不是骨架预算) + H 链位置 ----------
    g_vol = PCB_L * PCB_W * GRAPHITE_T / 1000.0
    g_side = g_vol * GR_DENSITY
    r["graphite"] = {
        "volume_cc": r6(g_vol), "mass_per_side_g": r6(g_side), "mass_per_pair_g": r6(g_side * 2),
        "placement": P["graphite_place"],
        "budget_line": "MECH_BUDGET §3 W11 (石墨散热膜+导热垫+隔热垫 1-2g) —— **不是** §2.4 B 的骨架预算",
        "note": P["graphite_note"].format(g=g_side, g2=g_side * 2,
                                          d=g_side * 2 - W11_GRAPHITE_G[1]),
    }
    add("graphite_in_W11", W11_GRAPHITE_G[0] <= g_side * 2 <= W11_GRAPHITE_G[1],
        P["graphite_detail"].format(g=g_side, g2=g_side * 2,
                                     lo=str(W11_GRAPHITE_G[0]), hi=str(W11_GRAPHITE_G[1]),
                                     d=g_side * 2 - W11_GRAPHITE_G[1]),
        g_side * 2, level="warn")

    h_base = H_OUTER_WALL + SKELETON_T + PCB_T + H_AIR_GAP + H_INSUL_PAD + H_SKIN_WALL
    h_gr = h_base + GRAPHITE_T
    h_base_t08 = H_OUTER_WALL + SKELETON_T_ALT + PCB_T + H_AIR_GAP + H_INSUL_PAD + H_SKIN_WALL
    h_gr_t08 = h_base_t08 + GRAPHITE_T
    r["H_chain"] = {
        "base_t1.0_mm": r6(h_base), "plus_graphite_t1.0_mm": r6(h_gr),
        "base_t0.8_mm": r6(h_base_t08), "plus_graphite_t0.8_mm": r6(h_gr_t08),
        "temple_H_max_mm": TEMPLE_H, "clearance_rule_mm": 0.60,
        "margin_t1.0_plus_gr_mm": r6(TEMPLE_H - h_gr),
        "margin_t0.8_plus_gr_mm": r6(TEMPLE_H - h_gr_t08),
        "note": P["hchain_note"],
    }
    add("H_chain_margin_t1.0", (TEMPLE_H - h_gr) >= 0.60,
        f"骨架 1.0 + 石墨 0.30: PCB 段 H 链 = {h_gr:.2f}mm vs 可用 {TEMPLE_H:.2f} -> 余 {TEMPLE_H - h_gr:.2f}mm "
        f"(≥0.60 规矩 ✅)", TEMPLE_H - h_gr)
    add("H_chain_margin_t0.8", (TEMPLE_H - h_gr_t08) >= 0.60,
        f"骨架 0.8 + 石墨 0.30: PCB 段 H 链 = {h_gr_t08:.2f}mm vs 可用 {TEMPLE_H:.2f} -> 余 "
        f"{TEMPLE_H - h_gr_t08:.2f}mm ✅", TEMPLE_H - h_gr_t08)

    # ---------- ⑤ 并联热路: 骨架延伸进电池段的后果 ----------
    frac_base = skin_fraction(R_SKIN_PATH)
    r["parallel_heat_path"] = {
        "R_skin_path_K_W": R_SKIN_PATH, "R_conv_K_W": R_CONV,
        "skin_fraction_baseline_pct": r6(frac_base),
        "R_print_long_K_W": R_PRINT_LONG, "R_al_long_K_W": R_AL_LONG,
        "note": "骨架若延伸进电池段, 电池段热量的纵向热路由 730 (打印件) 降到 4.50 (铝) K/W "
                "-> 更多热绕到皮肤 [MECH/CLEARANCE_FIX §4.2]. 本脚本只复算**比例**, 不复算皮肤温度.",
    }
    add("skeleton_stops_at_pcb_rear_edge", True,
        f"硬约束: 金属骨架/石墨止于 PCB 段后缘 (板坐标 X={PCB_L:.2f}). 若延伸进电池段: 纵向热阻 "
        f"{R_PRINT_LONG:.0f} -> {R_AL_LONG:.2f} K/W, 皮肤侧热路被旁路 -> 进皮肤热量比例上升 "
        f"(CLEARANCE_FIX §4.2 报 92.5% -> 95.7%). 理由是物理的 (金属绕过隔热层直接灌到皮肤), 不是模型的.")

    # ---------- ⑥ 整机重量影响 ----------
    for tag in ("B", "C"):
        delta = by[tag]["mass_per_pair_g"]
        r.setdefault("total_weight_impact", {})[f"cand_{tag}"] = {
            "skeleton_pair_g": delta,
            "proto_total_range_g": list(TOTAL_PROTO_G),
            "proto_total_with_pair_g": [r6(TOTAL_PROTO_G[0] + delta), r6(TOTAL_PROTO_G[1] + delta)],
            "target_g": [30, 40],
            "still_over_target": (TOTAL_PROTO_G[0] + delta) > 40,
            "note": "整机推算区间加骨架增量; 目标 30-40g. 候选 C 的骨架增量 "
                    f"{delta:.2f}g/对 是**两种候选里较小**的",
        }
    add("weight_still_over_target", True,
        f"整机推算 {TOTAL_PROTO_G[0]}-{TOTAL_PROTO_G[1]}g 已超 30-40g 目标 (MECH_BUDGET §3.1); "
        f"骨架增量候选 B {by['B']['mass_per_pair_g']:.2f}g / 候选 C {by['C']['mass_per_pair_g']:.2f}g "
        f"-> 两候选都救不了整机超重, 只能少加重 (薄壁化/金属件替打印加强件)")
    return r


def _pick_frame_id(argv):
    """★切档解析: `--frame <fid>` 命令行优先, 其次环境变量 MECH_FRAME, 最后默认档 ★
    ★默认档 = F30A (60×30 / RK3576) —— ★本单【不许自己拍默认档】★"""
    fid = os.environ.get("MECH_FRAME", "").strip() or DEFAULT_FRAME_ID
    for i, a in enumerate(argv):
        if a == "--frame" and i + 1 < len(argv):
            fid = argv[i + 1].strip()
        elif a.startswith("--frame="):
            fid = a.split("=", 1)[1].strip()
    return fid or DEFAULT_FRAME_ID


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--frame", default=None,
                    help="★切档: F30A (默认, 60×30 / RK3576 · 历史产品板口径) 或 "
                         "B160x100 (台架板 160×100 / RK3572-SOM)★")
    args = ap.parse_args()
    fr = _bind_frame(args.frame if args.frame else _pick_frame_id(sys.argv[1:]))
    P = PROSE[FRAME_ID]
    r = compute()
    if args.json:
        print(json.dumps(r, ensure_ascii=False, indent=2, default=str))
        return 0

    if FRAME_ID != DEFAULT_FRAME_ID:
        # ★非默认档才多打一行档位说明 (★默认档输出与迁移前【逐字节相同】★)
        print("★ 档位 = %s (%s) · 板 %.2f×%.2f×%.2fmm / %d 层 · 孔位族 = %s"
              % (fr["fid"], fr["name"], fr["pcb_l"], fr["pcb_w"], fr["pcb_thk"], fr["layers"],
                 "适用 (F30A 专有)" if fr["pinset_applicable"] else "口径不适用"))

    print("=" * 80)
    print("金属骨架截面形状 + 重量口径 + 石墨 H 链 —— 结构侧独立复算 (ISS-049 两问的答复)")
    print(P["migrate"])
    print("=" * 80)
    print("\n★ 口径: 只做**算术复算 + 几何判定**; **不出新的皮肤侧温度数** (要完整热模型重算, U-3); **不拍板**。")

    ctx = {"soc_y": SOC_Y_LEN, "band": HOT_BAND, "vneed": SOC_Y_LEN + 2 * HOT_BAND,
           "w": PCB_W, "l": PCB_L, "hot_len": HOT_SEG_X1 - HOT_SEG_X0,
           "hx0": HOT_SEG_X0, "hx1": HOT_SEG_X1, "ratio": HOT_BAND / 3.50}
    print(P["sec1_title"])
    print("-" * 80)
    print(P["sec1_line"].format(**ctx))
    print(P["spread_line"].format(**ctx))
    print(P["hotseg_line"].format(**ctx))

    print("\n【1b】非 SoC 端段的 Y 跨度需求 (孔位口径的机械后果)")
    print("-" * 80)
    sp = r["end_segment_span"]
    if sp:
        print(f"  套 A (S1 Y={SCREW_Y_SET_A[0]:.2f} / S2 Y={SCREW_Y_SET_A[1]:.2f}): "
              f"前段 {sp['套A']['front']:.2f}mm / 后段 {sp['套A']['rear']:.2f}mm "
              f"→ 与 ISS-049 §4「其余段 ≥{SEG_W_OTHER:.2f}mm」恰好相容 ✅")
        print(f"  套 B (S1 Y={SCREW_Y_SET_B[0]:.2f} / S2 Y={SCREW_Y_SET_B[1]:.2f}): "
              f"前段 {sp['套B']['front']:.2f}mm / 后段 {sp['套B']['rear']:.2f}mm "
              f"= {sp['套B']['max'] / SEG_W_OTHER:.2f}× 口径 ⇒ 套 B 推翻骨架接口 ❌ (故否决)")
    else:
        print("  ★本帧口径不适用: 端段 Y 跨度需求由【PIN-SET-2 套 A 四孔的板坐标】推导 "
              "⇒ F30A 帧专有; 台架板 160×100 盘上无这四个孔 ⇒ 本档不跑本判据")
        print("  ★先例: MECH/board_frame_feasibility.py:108 `pinset_applicable: False`")

    print(P["sec2_title"])
    print("-" * 80)
    print(f"{'方案':<40}{'V覆盖':<9}{'体积cc':<10}{'g/侧':<9}{'g/对':<9}{'vs骨架预算3g'}")
    for c in r["candidates"]:
        v = "✅ 满宽" if c["v_cover_ok"] else "❌"
        print(f"{c['name']:<40}{v:<9}{c['volume_cc']:<10.3f}{c['mass_per_side_g']:<9.2f}"
              f"{c['mass_per_pair_g']:<9.2f}{c['vs_skeleton_budget_g']:+.2f}")
    print(P["over_budget_line"])
    print(P["rootcause_line"].format(
        hot_len=r["inputs"]["hot_seg_X_mm"][1] - r["inputs"]["hot_seg_X_mm"][0],
        vr=r["candidates"][2]["hot_segment_V_mm"] / 15.0))

    print("\n【3】石墨片 (0.30mm, 铺在骨架与 PCB 之间)")
    print("-" * 80)
    g = r["graphite"]
    print(f"  体积 {g['volume_cc']:.3f}cc · {g['mass_per_side_g']:.2f}g/片 · {g['mass_per_pair_g']:.2f}g/对")
    print(f"  重量归账: {g['budget_line']}")
    print(f"  ⚠️ {g['note']}")

    print("\n【4】PCB 段 H 链 (含石墨) —— ★与板宽无关 (板宽走 V 向)")
    print("-" * 80)
    h = r["H_chain"]
    print(f"  骨架 1.0: {h['base_t1.0_mm']:.2f} -> +石墨 {h['plus_graphite_t1.0_mm']:.2f}mm  "
          f"余 {h['margin_t1.0_plus_gr_mm']:.2f}mm")
    print(f"  骨架 0.8: {h['base_t0.8_mm']:.2f} -> +石墨 {h['plus_graphite_t0.8_mm']:.2f}mm  "
          f"余 {h['margin_t0.8_plus_gr_mm']:.2f}mm   (可用 {h['temple_H_max_mm']}, 规矩 ≥{h['clearance_rule_mm']})")

    print("\n【5】整机重量影响")
    print("-" * 80)
    for k, v in r["total_weight_impact"].items():
        print(f"  {k}: 骨架 {v['skeleton_pair_g']:.2f}g/对 -> 整机推算 "
              f"{v['proto_total_range_g'][0]}-{v['proto_total_range_g'][1]}g 变成 "
              f"{v['proto_total_with_pair_g'][0]:.1f}-{v['proto_total_with_pair_g'][1]:.1f}g "
              f"(目标 30-40g, 仍超)")

    print("\n【判定】")
    print("-" * 80)
    for c in r["checks"]:
        flag = "✅" if c["pass"] else ("⚠️ " if c.get("level") == "warn" else "❌")
        print(f"  {flag} {c['name']}: {c['detail']}")

    print("\n★ 结论 (建议, 不拍板 —— 最终由项目总工裁):")
    print(P["concl_1"])
    print(P["concl_2_head"].format(m1=r['candidates'][1]['mass_per_pair_g']) +
          f"t=0.8 = {r['candidates'][2]['mass_per_pair_g']:.2f}g/对 "
          f"(仍超 +1-3g 预算 {r['candidates'][2]['vs_skeleton_budget_g']:+.2f}g) ⇒ "
          "**骨架截面必须重做** (满宽段只到 SoC 投影 / 横向扩散交给石墨 / 材料分段) —— 属预算裁, 报项目总工")
    print(P["concl_3"])
    print(P["concl_4"])
    print("  ⑤ ⚠️ 换 0.80mm 的**热学代价必须并进 U-3 一起算**: 铝的导热面积/截面都小 → Tj 会升, "
          "而 §2.3.1 的 46.5°C (0.23W) 已经超 43°C 红线 —— **只看重量不看热学会翻车**")
    print("  ⑥ 整机超重 (48.9-74.0g vs 目标 30-40g) **两个候选都救不了**, 只能靠减重措施, 不靠骨架选型")
    print(P["concl_7"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
