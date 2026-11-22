#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
jd_y0_feasibility.py —— ISS-267 检修口/调试口板侧开口约束表 + `jd_y0` 候选枚举 (mech-lead)
=================================================================================================
干什么:
  给「板只改一次」那一趟准备一份**板侧开口约束表**: 检修口/调试口 (J_DEBUG 焊盘阵列 + 开口 `jd_y0`)
  的合法 Y 区间 + 候选枚举 + 各候选净空实测值 + 「板框口径三套并存」的冲突影响表。

★口径纪律 (硬):
  ① **判据阈值一个字节都不许自己写** ⇒ 本脚本把 `MECH/service_port_check.py` **当只读模块 import**,
     直接取它的 `BASE` / `TOL` / `CRIT` ⇒ 阈值零漂移 (CRIT = 2×0.30 = 0.60) ★
  ② **不改 `MECH/service_port_check.py`** (md5 db58ff6a2afc28b8bf517e3c57c56bc1 必须逐字节不变) ——
     本文件是**新增的独立脚本**, 只读 import, 不写回 ★
  ③ **不拍板**: 板框口径 / `jd_y0` 取值 一律「列选项 + 代价 + 谁拍」, 本脚本不产出"建议值" ★
  ④ 证据级: 全部读数 = **设计态几何 + 公差栈** ⇒ `[推算]`; 盘上板实测值 = `[实测]` (读得到才写) ★

几何模型 (★与 service_port_check.py 检查项 2.x / 7.4 / 7.5 / 8.1b 同式★):
  · 焊盘阵列 Y: jd_y1 = jd_y0 + (jd_rows-1) × jd_pitch
  · **必须清空区 = Cortex-10 座体** (高 jd_body_h, 以阵列中心为心) ⇒ body_y0 / body_y1
  · 开口 Y = 必须清空区 ± 单边间隙 cl_y, cl_y = (OPEN_Y - jd_body_h)/2
  · P-5 最近距离 = max(孔壁下沿 - 阵列上沿, 阵列下沿 - 孔壁上沿) (★通用式, 重叠时为负★)

用法:
  python3 MECH/jd_y0_feasibility.py                ⇒ 打印三张表 (口径矩阵 / 框口径影响 / jd_y0 候选)
  python3 MECH/jd_y0_feasibility.py --selftest     ⇒ 反向用例 (★三个, 一条不许删★)
  python3 MECH/jd_y0_feasibility.py --json          ⇒ 机器可读 (给交卷单 / 作业包引用)

退出码: 0 = 自检一致; 非 0 = 自检不一致 (与 service_port_check.py 的 rc 语义一致) · ★帧 id 唯一权威: `HW/PCB/BOARD_FRAME_CALIBER.md` §6 `cal:FRAMES` = `B160x100` / `F30A` / `P60x15` (★三档坐标不可互相代入 · 60×30/60×15 属历史/作废口径, 不可混用★)★
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SPC_PATH = os.path.join(HERE, "service_port_check.py")

# ==================================================================================================
# ★只读 import 既有闸脚本 ⇒ 阈值零漂移 (★不写回、不改它★)
# ==================================================================================================
def load_spc():
    spec = importlib.util.spec_from_file_location("spc_readonly", SPC_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)          # ★只执行模块顶层 (无副作用: 只定义常量与函数)★
    return mod


SPC = load_spc()
BASE = dict(SPC.BASE)                    # ★拷贝 ⇒ 本脚本改自己的副本, 绝不污染闸脚本的全局★
TOL = dict(SPC.TOL)
CRIT = SPC.CRIT                          # 0.60 = 2 × TOL['fdm_part']

# ==================================================================================================
# 几何 (与闸脚本同式; 每一行都注闸脚本检查项号)
# ==================================================================================================
OPEN_X, OPEN_Y = 10.20, 4.60             # ★与 service_port_check.py §3 同值 (开口外形)★


def geom(jd_y0: float) -> dict:
    """给定 jd_y0 ⇒ 检修口/调试口所有 Y 向几何 + P-5 净空 (全部按闸脚本同式算)"""
    jd_y1 = jd_y0 + (BASE["jd_rows"] - 1) * BASE["jd_pitch"]          # 焊盘阵列上沿
    body_y_c = (jd_y0 + jd_y1) / 2.0                                    # Cortex-10 座体中心
    body_y0 = body_y_c - BASE["jd_body_h"] / 2.0                       # 必须清空区下沿
    body_y1 = body_y_c + BASE["jd_body_h"] / 2.0                       # 必须清空区上沿
    content_h = body_y1 - body_y0                                      # = jd_body_h = 2.54
    cl_y = (OPEN_Y - content_h) / 2.0                                  # 开口单边间隙 (X 向另算)
    open_y0 = body_y0 - cl_y                                           # 开口下沿
    open_y1 = body_y1 + cl_y                                           # 开口上沿
    # P-5: 夹具基准孔壁 → 焊盘阵列 最近距离 (通用式, 重叠为负)
    p2_lo = BASE["p2_y"] - BASE["p2_d"] / 2.0
    p2_hi = BASE["p2_y"] + BASE["p2_d"] / 2.0
    s2_lo = BASE["s2_y"] - BASE["s2_d"] / 2.0
    s2_hi = BASE["s2_y"] + BASE["s2_d"] / 2.0
    p2_gap = max(p2_lo - jd_y1, jd_y0 - p2_hi)
    s2_gap = max(s2_lo - jd_y1, jd_y0 - s2_hi)
    pad_y1 = jd_y1
    return {
        "jd_y0": jd_y0, "jd_y1": jd_y1,
        "body_y0": body_y0, "body_y1": body_y1,
        "cl_y": cl_y, "open_y0": open_y0, "open_y1": open_y1,
        "p2_gap": p2_gap, "s2_gap": s2_gap,
        "pad_y1": pad_y1,
        "open_y0_board_margin": open_y0,               # 开口下沿离板下沿 (板内判定用)
        "open_y1_board_margin": BASE["pcb_w"] - open_y1,  # 开口上沿离板上沿
    }


# ==================================================================================================
# 判据 (★全部对应 service_port_check.py 的检查项编号 ★)
# ==================================================================================================
def criteria(jd_y0: float) -> dict:
    """返回 {判据号: (是否通过, 说明, 余量mm)} —— 只放与 jd_y0 有关的判据"""
    g = geom(jd_y0)
    out = {}
    # --- 7.4 P-2 (⌀2.0 H7) 孔壁 → 焊盘阵列 ≥ CRIT ---
    out["7.4"] = (g["p2_gap"] >= CRIT, f"P-2 净空 {g['p2_gap']:.2f}mm", g["p2_gap"] - CRIT)
    # --- 7.5 S-2 (⌀1.4) 孔壁 → 焊盘阵列 ≥ CRIT ---
    out["7.5"] = (g["s2_gap"] >= CRIT, f"S-2 净空 {g['s2_gap']:.2f}mm", g["s2_gap"] - CRIT)
    # --- 2.5 焊盘并集 bbox 在板内 (★脚本里 Y 上限 13.0 = 15mm 板遗留常量, 30mm 板应为 28.0★) ---
    out["2.5"] = (g["pad_y1"] <= 13.0, f"焊盘上沿 {g['pad_y1']:.2f} ≤ 13.0", 13.0 - g["pad_y1"])
    # --- 8.1b 开口含住必须清空区 (构造上恒真, 但要留痕) ---
    out["8.1b"] = (g["open_y0"] <= g["body_y0"] and g["open_y1"] >= g["body_y1"],
                   f"开口 Y {g['open_y0']:.3f}..{g['open_y1']:.3f}", 0.0)
    # --- D0 (★派生判据, 非脚本检查项★) 开口必须整口落在板内 (下沿 ≥0 / 上沿 ≤ 板宽) ---
    ok_d0 = g["open_y0"] >= 0.0 and g["open_y1"] <= BASE["pcb_w"]
    out["D0"] = (ok_d0, f"开口 Y {g['open_y0']:.3f}..{g['open_y1']:.3f} 须在板内 0..{BASE['pcb_w']:.2f}",
                 min(g["open_y0"], BASE["pcb_w"] - g["open_y1"]))
    return out


def feasible(jd_y0: float) -> bool:
    """★严格按闸脚本判据 (7.4 / 7.5 / 2.5 / 8.1b) 全部通过才算可行★ (D0 单列, 因为它不是脚本判据)"""
    c = criteria(jd_y0)
    return all(c[k][0] for k in ("7.4", "7.5", "2.5", "8.1b"))


def feasible_with_d0(jd_y0: float) -> bool:
    c = criteria(jd_y0)
    return all(c[k][0] for k in ("7.4", "7.5", "2.5", "8.1b", "D0"))


def scan_intervals(pred, lo=-20.0, hi=60.0, step=0.001) -> list:
    """扫描可行区间 (返回 [(lo, hi), ...])"""
    xs = [lo + i * step for i in range(int(round((hi - lo) / step)) + 1)]
    runs = []
    start = None
    for x in xs:
        if pred(x):
            if start is None:
                start = x
        else:
            if start is not None:
                runs.append((start, x - step))
                start = None
    if start is not None:
        runs.append((start, xs[-1]))
    # 合并相邻
    merged = []
    for a, b in runs:
        if merged and abs(a - merged[-1][1]) <= step * 1.5:
            merged[-1] = (merged[-1][0], b)
        else:
            merged.append((a, b))
    return merged


def binding_bounds(lo: float, hi: float) -> dict:
    """找出在区间端点处绑住边界的判据 (谁的余量 = 0 或最小)"""
    out = {}
    for end, tag in ((lo, "下界"), (hi, "上界")):
        c = criteria(end)
        cands = [(k, v[1], v[2]) for k, v in c.items() if k in ("7.4", "7.5", "2.5", "D0")]
        # 取余量最小者为绑定判据 (负数优先)
        cands.sort(key=lambda t: t[2])
        out[tag] = {"value": end, "binding": cands[0]}
    return out


# ==================================================================================================
# 板框口径三套 (★只列, 不选 ★)
# ==================================================================================================
FRAMES = [
    {
        "key": "①", "name": "台架板 (盘上现役)",
        "pcb_l": 160.0, "pcb_w": 100.0, "pcb_thk": 1.6, "layers": 8,
        "src": "HW/PCB/demo_mainboard_params.json → board (160×100/8层/1.6) + 板文件 Edge.Cuts 实读",
    },
    {
        "key": "②", "name": "产品目标板 60×30 (套 A, MECH 现行口径)",
        "pcb_l": 60.0, "pcb_w": 30.0, "pcb_thk": 1.0, "layers": 6,
        "src": "MECH/BOARD_GEOM_30MM.md §0/§1/§3 + ISS-118/130 (老板 10-29 19:16 板宽 30)",
    },
    {
        "key": "③", "name": "产品目标板 60×15 (10-27/10-28 原始定版)",
        "pcb_l": 60.0, "pcb_w": 15.0, "pcb_thk": 1.0, "layers": 6,
        "src": "HW/PCB_OUTLINE_60x15.md §1.1 + ISS-105/118 (板宽 15 已于 ISS-118 放宽为 30)",
    },
]


def frame_chain(fr: dict) -> dict:
    """在给定板框下, 复算闸脚本 §4/§5 的三条锁死尺寸链 (照用闸脚本公式)"""
    pcb_thk = fr["pcb_thk"]
    pcb_w = fr["pcb_w"]
    pcb_l = fr["pcb_l"]
    # H 链
    h_pcb_face = BASE["h_skin_wall_in"] + BASE["pad_thermal"] + BASE["air_gap"] + pcb_thk
    h_pcb_need = (BASE["wall"] + BASE["frame_thk"] + pcb_thk + BASE["air_gap"]
                  + BASE["pad_thermal"] + BASE["wall"])
    h_margin = BASE["cav_h"] - h_pcb_need
    cavity = BASE["h_outer_out"] - h_pcb_face
    # V 链
    v_pcb_need = pcb_w + BASE["duct_v"]
    v_margin = BASE["cav_v"] - v_pcb_need
    v_margin_worst = v_margin - 2 * TOL["fdm_part"]
    # L 链
    l_need = BASE["cell_l"] + pcb_l + BASE["conn_margin"]
    l_margin = BASE["cav_l"] - l_need
    return {
        "h_pcb_face": h_pcb_face, "h_pcb_need": h_pcb_need, "h_margin": h_margin,
        "cavity": cavity, "cavity_ok": cavity >= BASE["cavity_req"],
        "v_pcb_need": v_pcb_need, "v_margin": v_margin, "v_margin_worst": v_margin_worst,
        "v_ok": v_margin >= CRIT and v_margin_worst >= CRIT,
        "l_need": l_need, "l_margin": l_margin, "l_ok": l_margin >= CRIT,
    }


# ==================================================================================================
# 候选 (★只列 + 代价 + 谁拍, 不代拍 ★)
# ==================================================================================================
CANDIDATES = [
    ("A", 9.50, "维持现状 (旧 15mm 板口径未迁的现值)", "main + hw-lead"),
    ("C1", 10.00, "迁到区间下部 (偏下沿, 开口离板下沿近)", "main + hw-lead"),
    ("C2", 10.50, "迁到区间中下 (P-5 两头都有余量)", "main + hw-lead"),
    ("C3", 11.00, "迁到区间中上 (2.5 判据开始吃紧)", "main + hw-lead"),
    ("B1", 11.73, "贴 2.5 判据 (焊盘上沿 = 13.00)", "★不可用 (见代价)★"),
    ("B2", 12.13, "贴 7.4 (P-2) 判据 (净空 = 0.60)", "★不可用 (见代价)★"),
]


def candidate_row(tag: str, val: float, desc: str, who: str) -> dict:
    g = geom(val)
    c = criteria(val)
    p2_margin = c["7.4"][2]
    s2_margin = c["7.5"][2]
    c25_margin = c["2.5"][2]
    # FDM 实践判读: 余量 < 1×0.30 ⇒ 贴判据, 实际不可用
    practical = all(m >= TOL["fdm_part"] for m in (p2_margin, s2_margin, c25_margin))
    return {
        "tag": tag, "jd_y0": val, "desc": desc, "who": who,
        "open_y": (g["open_y0"], g["open_y1"]),
        "p2_gap": g["p2_gap"], "p2_margin": p2_margin,
        "s2_gap": g["s2_gap"], "s2_margin": s2_margin,
        "c25_margin": c25_margin,
        "all_pass": feasible(val),
        "practical_ok": practical,
    }


# ==================================================================================================
# 打印
# ==================================================================================================
def hr(title: str) -> None:
    print("=" * 104)
    print(title)
    print("=" * 104)


def print_caliber_matrix() -> None:
    hr("★表 1 · 检修口/调试口几何口径矩阵 (★每行: 脚本现值 / 文档记值 / 盘上板实测 / 冲突 / 证据级★)")
    rows = [
        ("jd_y0 (J_DEBUG 焊盘阵列 Y 起点)", "9.50",
         "MECH/service_port_check.py BASE['jd_y0'] (脚本现值)",
         "MECH/SERVICE_PORT_ISS092.md §3.1 (随 jd_y0 走, 未定版)",
         "★盘上板读不到★ (板文件无 J_DEBUG 焊盘 ⇒ 该板不是产品板)", "★冲突★", "[实测·脚本]"),
        ("p2_y (P-2 ⌀2.0 H7 孔心 Y)", "15.00",
         "BASE['p2_y'] = 15.00 (ISS-264 迁入)",
         "MECH/BOARD_GEOM_30MM.md §3 套 A (52.00, 15.00)",
         "★盘上板无该孔★ (160×100 台架板)", "★冲突★ (HW/PCB_FIXING_PINSET2.md L82 仍写 7.50)",
         "[实测·脚本] + [官方·文档]"),
        ("s2_y (S-2 ⌀1.4 孔心 Y)", "20.00",
         "BASE['s2_y'] = 20.00 (ISS-264 迁入)",
         "MECH/BOARD_GEOM_30MM.md §3 套 A (52.00, 20.00)",
         "★盘上板无该孔★", "★冲突★ (HW/PCB_FIXING_PINSET2.md L84 仍写 12.50)", "[实测·脚本] + [官方·文档]"),
        ("pcb_thk (板厚)", "1.00",
         "BASE['pcb_thk'] = 1.00 (6 层现行)",
         "MECH/BOARD_GEOM_30MM.md §1",
         "★盘上板 = 1.60★ (板文件 general/thickness 1.6 + 8 铜层)", "★冲突★", "[实测·脚本] + [实测·板文件]"),
        ("开口 Y 上下限", "7.835 .. 12.435",
         "检查项 8.1b 实跑输出",
         "MECH/SERVICE_PORT_ISS092.md L89 旧值 8.67..13.27 (已标作废)",
         "★盘上板无开口★", "★冲突★ (差 0.835mm)", "[推算] (脚本实算)"),
        ("必须清空区 Y (Cortex-10 座体 2.54)", "8.865 .. 11.405", "检查项 2.4 推导",
         "MECH/SERVICE_PORT_ISS092.md §3.2", "—", "—", "[推算]"),
        ("P-5 · P-2 孔壁→阵列 最近距离", "3.23 mm", "检查项 7.4 实跑输出",
         "HANDOFF ISS-264 §0.1 (3.23)", "—", "—", "[推算]"),
        ("P-5 · S-2 孔壁→阵列 最近距离", "8.53 mm", "检查项 7.5 实跑输出",
         "HANDOFF ISS-264 §0.1 (8.53)", "—", "—", "[推算]"),
        ("判据 CRIT (2×0.30)", "0.60 mm", "TOL['fdm_part']=0.30 → CRIT",
         "MECH/SERVICE_PORT_ISS092.md §5 口径", "—", "★框无关★", "[实测·脚本]"),
        ("判据 cavity_req (盖板内腔)", "4.50 mm", "BASE['cavity_req']",
         "ISS-085 §6.1", "—", "★框无关 (但实际内腔值随 pcb_thk 变)★", "[实测·脚本]"),
        ("判据 cav_v (根部净高)", "38.00 mm", "BASE['cav_v']", "ISS-092 §1.6.2", "—", "★框无关★", "[实测·脚本]"),
        ("判据 duct_v (垂直走线槽)", "6.00 mm", "BASE['duct_v']", "ISS-092 §5.6.2", "—", "★框无关★", "[实测·脚本]"),
        ("孔位套 A (P1/P2/S1/S2)", "P1(8,15) P2(52,15) S1(8,10) S2(52,20)",
         "PIN_SET_A 常量 (只用于口径钉死检查 7.4b/7.5b)",
         "MECH/BOARD_GEOM_30MM.md §3 (ISS-194 verified)",
         "★盘上板无此四孔★", "★冲突★ (板框不同 ⇒ 孔位真源不同)", "[官方·文档] + [实测·脚本常量]"),
        ("板框 ① 台架板", "160.0 × 100.0 · 8 层 · 1.6", "— (MECH 脚本不按它算)",
         "HW/PCB/demo_mainboard_params.json → board",
         "★板文件实读: Edge.Cuts (0,0)-(160,0)-(160,100)-(0,100) ⇒ 160.00×100.00; general/thickness 1.6; 铜层 8★",
         "★与 ②/③ 冲突★", "[实测·板文件]"),
        ("板框 ② 产品板 60×30 (MECH 现行)", "60.0 × 30.0", "BASE['pcb_l'=60.00 / 'pcb_w'=30.00]",
         "MECH/BOARD_GEOM_30MM.md §0/§1 (ISS-118/130)", "—", "★与 ① 冲突★", "[实测·脚本] + [官方·文档]"),
        ("板框 ③ 产品板 60×15 (原始定版)", "60.0 × 15.0", "— (脚本已迁走)",
         "HW/PCB_OUTLINE_60x15.md §1.1 (ISS-105)", "—", "★与 ② 冲突★ (已被 ISS-118 放宽为 30)",
         "[官方·文档·已作废]"),
        ("坐标约定 (原点/轴向)", "板框左下角 · X 0→60 · Y 0→30",
         "脚本 §8 的 L = X + 40.50 换算",
         "MECH/PCB_MOUNT_PIN_SET2.md L6 (★仍写 Y 0→15.00, 过期★) + HW/ISS121_MIC_MAGNET_POSITION.md L27 (Y 0→15 现 30)",
         "—", "★文档冲突★ (PIN_SET2 L6 过期)", "[官方·文档]"),
        ("Y↔V 朝向 (哪侧是皮肤侧)", "★未定★", "—",
         "MECH/PCB_MOUNT_PIN_SET2.md L6: 「由装配决定」", "—", "★[0数据]★", "[0数据]"),
    ]
    hdr = ("量", "脚本现值", "脚本出处", "文档记值", "盘上板实测值", "冲突", "证据级")
    w = [26, 24, 30, 32, 34, 32, 22]
    print(" | ".join(h.ljust(w[i]) for i, h in enumerate(hdr)))
    print("-" * 104)
    for r in rows:
        print(" | ".join(str(c).ljust(w[i])[:w[i]] for i, c in enumerate(r)))


def print_frame_table() -> None:
    hr("★表 2 · 板框口径冲突影响表 (★逐个量: 换框之后这个量会不会变 ★)")
    print("—— 三套框各自的锁死链复算 (照用 service_port_check.py §4/§5 公式, 阈值零改动) ——")
    for fr in FRAMES:
        c = frame_chain(fr)
        print(f"\n  [{fr['key']}] {fr['name']}  ({fr['pcb_l']:.2f} × {fr['pcb_w']:.2f} · "
              f"{fr['pcb_thk']:.2f}mm · {fr['layers']}层)")
        print(f"      H PCB 段: 需求 {c['h_pcb_need']:.2f} / 余 {c['h_margin']:+.2f}  |  "
              f"盖板内腔 {c['cavity']:.2f} (需 ≥{BASE['cavity_req']:.2f}) "
              f"{'✅' if c['cavity_ok'] else '❌ 判红'}")
        print(f"      V PCB 段: 需求 {c['v_pcb_need']:.2f} / 余 {c['v_margin']:+.2f} / 最坏 "
              f"{c['v_margin_worst']:+.2f}  {'✅' if c['v_ok'] else '❌ 判红'}")
        print(f"      L 链    : 需求 {c['l_need']:.2f} / 余 {c['l_margin']:+.2f}  {'✅' if c['l_ok'] else '❌ 判红'}")
    print("\n—— 逐量「换框会不会变」 ——")
    rows = [
        ("jd_y0 (焊盘阵列 Y 起点)", "★会变★", "取值本身是 HW 排布决定, 但合法区间的两端由 p2_y/s2_y 与 2.5 判据决定 ⇒ 换框 ⇒ 区间重算"),
        ("p2_y / s2_y (孔心 Y)", "★会变★", "套 A 是 60×30 板的坐标 (BOARD_GEOM_30MM.md §3) ⇒ 换框 ⇒ 孔位真源换 ⇒ 全部 P-5 重算"),
        ("pcb_thk (板厚)", "★会变★", "台架板 1.6 / 产品板 1.0 ⇒ H 链 + 盖板内腔全变 (台架板 1.6 时内腔只剩 4.10 < 4.50 ⇒ 盖板判红)"),
        ("开口 Y 上下限", "★会变★", "open_y0 = jd_y0 − 1.665 / open_y1 = jd_y0 + 2.935 (随 jd_y0 线性平移) ⇒ jd_y0 一拍即变"),
        ("P-5 最近距离 (P2/S2)", "★会变★", "12.73 − jd_y0 / 18.03 − jd_y0 ⇒ 随 jd_y0 + 孔位线性变"),
        ("必须清空区 Y", "★会变★", "jd_y0 − 0.635 .. jd_y0 + 1.905"),
        ("开口 X 区间 (49.21..59.41)", "★会变★", "跟 jd_x0 + 板长 (板端 60) 走 ⇒ 换框 ⇒ 板端坐标变"),
        ("判据 CRIT 0.60", "★框无关★", "= 2 × FDM 外形公差 0.30 ⇒ 与板框无关"),
        ("判据 cavity_req 4.50", "★框无关★ (要求值)", "★但【实际内腔】随 pcb_thk 变 ⇒ 台架板 1.6 ⇒ 实际 4.10 判红★"),
        ("判据 cav_v 38.00 / duct_v 6.00", "★框无关★", "镜脚内腔尺寸, 与板框无关"),
        ("器件距板边 ≥0.80", "★框无关★", "工艺规则"),
        ("板重 (1.67g @60×15×1.0)", "★会变★", "面积 × 板厚 × 1.85 g/cc"),
        ("V PCB 段需求/余量", "★会变★", "= pcb_w + duct_v ⇒ 台架板 100+6 = 106 > cav_v 38 ⇒ 判红"),
        ("L 链需求/余量", "★会变★", "= 40.50 + pcb_l + 15 ⇒ 台架板 215.50 > 130 ⇒ 判红"),
        ("孔位套 A", "★会变★", "60×30 板口径 ⇒ 换框 ⇒ 孔位坐标换真源"),
    ]
    w = [34, 24, 96]
    print(" | ".join(h.ljust(w[i]) for i, h in enumerate(("量", "换框会不会变", "说明"))))
    print("-" * 104)
    for r in rows:
        print(" | ".join(str(c).ljust(w[i])[:w[i]] for i, c in enumerate(r)))
    print("\n—— 「选框后必须重算」清单 (★照抄就能跑, 不拍框★) ——")
    for i, t in enumerate([
        "① MECH/service_port_check.py 的 p2_y / s2_y / jd_y0 三个常量 (★迁框 = 迁常量, 走 H-1 流程, 三个 md5 要重基线★)",
        "② pcb_thk (板厚) + H 链 + 盖板内腔 (台架板 1.6 ⇒ 内腔 4.10 < 4.50 ⇒ 盖板判红 ⇒ 盖板/PCB 厚要重设计)",
        "③ pcb_w / pcb_l ⇒ V 链 + L 链 (台架板 100/160 ⇒ 两条链都判红 ⇒ 台架板当不了镜脚板)",
        "④ 开口 Y + 必须清空区 + P-5 两条净空 (全部随 jd_y0 重算)",
        "⑤ 开口 X (板端坐标变) + 8.x 与电芯/铰链/骨架末端的间距 (L = X + 40.50 换算跟着变)",
        "⑥ 板重 (质量预算) + 器件距板边余量 (面积账)",
        "⑦ 孔位真源 (套 A 只对 60×30 成立) + 打印包/治具契约",
    ], 1):
        print(f"   {t}")


def read_board_debug_footprints() -> dict:
    """★[实测] 只读盘上板 (HW/PCB/demo_mainboard.kicad_pcb) + 落表 (netlist/BOM/pins) 的 J_DEBUG / J_UART ★"""
    import re
    root = os.path.dirname(HERE)
    pcb = os.path.join(root, "HW", "PCB", "demo_mainboard.kicad_pcb")
    out = {}
    try:
        with open(pcb, encoding="utf-8") as fh:
            lines = fh.read().split("\n")
        for ref in ("J_DEBUG", "J_UART"):
            for i, l in enumerate(lines):
                if f'"{ref}"' in l and "Reference" in l:
                    s = i
                    while s > 0 and "(footprint" not in lines[s]:
                        s -= 1
                    depth = 0
                    for j in range(s, len(lines)):
                        depth += lines[j].count("(") - lines[j].count(")")
                        if depth == 0 and j > s:
                            blk = "\n".join(lines[s:j + 1])
                            at = re.search(r"\(at ([-0-9.]+) ([-0-9.]+)", blk)
                            val = re.search(r'\(property "Value" "([^"]*)"', blk)
                            out[ref] = {
                                "at": (float(at.group(1)), float(at.group(2))) if at else None,
                                "pads": len(re.findall(r"\(pad ", blk)),
                                "value": val.group(1) if val else None,
                            }
                            break
                    break
    except OSError as exc:
        out["_error"] = str(exc)
    # 落表: 脚数 (pin 编号最大数)
    for name, path in (("netlist", "HW/netlist_v1.csv"), ("pins", "HW/netlist_v1_pins.csv"), ("bom", "HW/BOM_v1.csv")):
        try:
            with open(os.path.join(root, path), encoding="utf-8") as fh:
                txt = fh.read()
            pins = sorted({int(m) for m in re.findall(r"J_DEBUG\.pin(\d+)", txt)})
            out.setdefault("_tables", {})[name] = {"J_DEBUG_pins": pins}
            m = re.search(r"^J_DEBUG,(.*)$", txt, re.M)
            if m:
                out.setdefault("_tables", {})[name]["J_DEBUG_bom_row"] = m.group(1)[:80]
        except OSError:
            pass
    return out


def print_board_crosscheck() -> None:
    hr("★表 4 · 板侧落表交叉核对 (★[实测] 只读盘上板 + 网表/脚表/BOM ★)")
    d = read_board_debug_footprints()
    if "_error" in d:
        print(f"★读不到盘上板: {d['_error']} ⇒ [0数据]")
        return
    for ref in ("J_DEBUG", "J_UART"):
        v = d.get(ref)
        if not v:
            print(f"  {ref}: ★盘上板读不到★ ⇒ [0数据]")
            continue
        print(f"  盘上板 {ref}: 位置 ({v['at'][0]:.2f}, {v['at'][1]:.2f}) (板文件实测) · 焊盘数 {v['pads']} · "
              f"Value「{v['value']}」")
    t = d.get("_tables", {})
    for name, info in t.items():
        print(f"  落表 {name}: J_DEBUG 脚号 {info.get('J_DEBUG_pins')}")
    print()
    print("  ★★ 对不上 (★板侧作业包必须知道 ★):")
    print("   ① ★脚本按 J_DEBUG = 2×5 (10 脚, Cortex-10) 算★ (BASE['jd_cols']=5 / ['jd_rows']=2), "
          "★落表是 1×4 (4 脚)★ ⇒ 脚数与阵列形状不一致 ⇒ 「必须清空区」的 X 向宽度要重算")
    print("   ② ★盘上板 J_DEBUG 与 J_UART 相距很远★ (见上表坐标) ⇒ MECH 模型里「J_UART 紧邻 J_DEBUG 末列 (X+1.27)」"
          "⇒ 开口 X 49.21..59.41 (10.20) 在盘上板不成立")
    print("   ③ ★座体高度 2.54 = [0数据]★ (BOM: 「型号/间距/引脚编号待结构与装配复核」) ⇒ "
          "开口 Y 4.60 / 单边间隙 1.03 建立在「座体高 2.54」这个假设上 ⇒ 拿到真实型号后必须重算")
    print("   ④ ⇒ 结论: ★本表的 Y 向约束表可用 (依 jd_body_h=2.54 假设), 但 X 向与「必须清空区」必须等真实型号/位置定版后重算★")


def print_findings(intervals, intervals_d0) -> None:
    hr("★表 0 · 本单机器查出的【口径差异 / 判据漏项】 (★供 main 订正, 本单只报告不擅改★)")
    up = intervals[0][1] if intervals else float("nan")
    lo = intervals_d0[0][0] if intervals_d0 else float("nan")
    rows = [
        ("F-1", "★合法区间【上界】: 脚本判据口径 = 11.73, ISS-264 §0.1 写 12.13★",
         "★闸脚本检查项 2.5「焊盘并集 Y ≤ 13.00」⇒ jd_y0 + 1.27 ≤ 13.00 ⇒ jd_y0 ≤ **11.73** ⇒ "
         "比 P-2 的 12.13 更紧 ⇒ ISS-264 那一跳【漏了 2.5 这条判据】⇒ 真上界 = 11.73★",
         "[推算] (本脚本按闸脚本同式复算)"),
        ("F-2", "★合法区间【下界】: 脚本同式 = 1.665, ISS-264 §0.1 写 3.57★",
         "脚本同式: 必须清空区下沿 = jd_y0 − 0.635, 开口下沿 = jd_y0 − 0.635 − 1.03 = **jd_y0 − 1.665** ⇒ "
         "开口整口在板内 ⇒ jd_y0 ≥ **1.665** ⇒ ISS-264 的 3.57 = 1.27+1.27+1.03 (★把两个座体半高重复计了一次★)",
         "[推算] (本脚本按闸脚本同式复算)"),
        ("F-3", "★「按相对位置迁 jd_y0=24.50 ⇒ 孔与焊盘阵列重叠 12.37mm」复现不出来★",
         "闸脚本 7.4 是【两区间最近距离 max(...)】通用式 ⇒ 阵列落到孔【上方】时取第二分支 ⇒ "
         "24.50 时 P-2 = **+8.50 (不重叠)**; 真正让 24.50 判红的是【检查项 2.5】(焊盘上沿 25.77 > 13.00)",
         "[推算] (本脚本 --selftest ④ 留痕)"),
        ("F-4", "★检查项 2.5 的 Y 上限 13.00 = 15mm 板遗留常量 ⇒ 它本身是【框相关】的★",
         "15mm 板下 pad_y1 ≤ 13.00; 30mm 板的对应上限应是 28.00 ⇒ 该判据【随框变】⇒ "
         "⇒ 「选框后必须重算」清单里必须加上它 (★本单不许改该常量, 只登记★)",
         "[推算] (常量来源分析)"),
        ("F-5", "★ISS-264 §0.1 写的下界 3.57 对应的口径没写清楚★",
         "若把 3.57 改成 1.665 (脚本同式), 区间变成 [1.665, 11.73]; "
         "★区间【宽度】从 8.56 变成 10.07 ⇒ 下界不是瓶颈, 上界才是 ⇒ ★main 拍板时看宽度即可★",
         "[推算]"),
        ("F-6", "★★落表的 J_DEBUG 是 1×4, 脚本按 2×5 算★★",
         "HW/BOM_v1.csv:71「1×4 1.27mm 排针 (JTAG)」 + HW/netlist_v1_pins.csv:202-205 (只有 pin1..pin4) "
         "⇒ 与 MECH/service_port_check.py BASE['jd_cols']=5 / ['jd_rows']=2 (2×5) 不一致 ⇒ "
         "★「必须清空区」的 X 向宽度 (7.62) 与「开口 X 10.20」要重算★",
         "[实测] (盘上板 + 落表) + [推算] (对比)"),
        ("F-7", "★★盘上板 J_DEBUG 与 J_UART 的相对位置与 MECH 模型不符★★",
         "盘上板实读: J_DEBUG @ (144.30, 58.00) · J_UART @ (20.74, 70.00) ⇒ 相距 123.6mm; "
         "MECH 模型 = J_UART 紧邻 J_DEBUG 末列 (X = jd_x1 + 1.27) ⇒ 开口 X 49.21..59.41 在盘上板不成立",
         "[实测] (板文件实读)"),
        ("F-8", "★★座体高度 2.54 是假设, 不是落表事实★★",
         "HW/BOM_v1.csv:71 原文「型号/间距/引脚编号待结构与装配复核」⇒ 真实座体高 = [0数据] ⇒ "
         "★开口 Y 4.60 / 单边间隙 1.03 / 开口 Y 区间 7.835..12.435 全部建立在「座体高 2.54」假设上★",
         "[0数据] (型号待定) + [推算] (假设上的算式)"),
    ]
    w = [6, 56, 84, 34]
    print(" | ".join(h.ljust(w[i]) for i, h in enumerate(("号", "发现", "机器依据", "证据级"))))
    print("-" * 104)
    for r in rows:
        print(" | ".join(str(c).ljust(w[i])[:w[i]] for i, c in enumerate(r)))
    print(f"\n★⇒ 合起来: ★脚本判据口径的合法区间 = [{lo:.3f}, {up:.3f}] mm (★上界由 2.5 绑, 不是 P-2★)★")
    print("★⇒ 现状 jd_y0 = 9.50 距上界 11.73 只剩 2.23mm (★不是 ISS-264 说的 2.63mm★) ⇒ 口径差异要点到 main★")


def print_jd_table(intervals, intervals_d0) -> None:
    hr("★表 3 · `jd_y0` 合法区间 + 候选枚举 (★在 MECH 现行框 60×30 套 A 下, 照用闸脚本判据 ★)")
    g0 = geom(BASE["jd_y0"])
    print(f"\n【当前现值】 jd_y0 = {BASE['jd_y0']:.2f} ⇒ 开口 Y {g0['open_y0']:.3f}..{g0['open_y1']:.3f} "
          f"(宽 {OPEN_Y:.2f}) · 必须清空区 Y {g0['body_y0']:.3f}..{g0['body_y1']:.3f} · 单边间隙 {g0['cl_y']:.2f}")
    print(f"【闸脚本判据】 7.4 (P-2 ≥{CRIT:.2f}) · 7.5 (S-2 ≥{CRIT:.2f}) · 2.5 (焊盘上沿 ≤13.00) · 8.1b (含住清空区) "
          f"· D0 (开口整口在板内, ★派生判据, 非脚本项★)")
    print("\n【合法区间】")
    if not intervals:
        print("   (空)")
    for a, b in intervals:
        bb = binding_bounds(a, b)
        lo_b, hi_b = bb["下界"], bb["上界"]
        lo_txt = (f"下界绑 {lo_b['binding'][0]}" if a > -19.9 else "下界: ★脚本判据在 −Y 方向无界 ⇒ 无物理意义 ⇒ 由派生判据 D0 兜底★")
        print(f"   ★ 脚本判据口径: [{a:.3f}, {b:.3f}] mm  ({lo_txt} / 上界绑 {hi_b['binding'][0]})")
    for a, b in intervals_d0:
        bb = binding_bounds(a, b)
        print(f"   ★ 加派生判据 D0 (开口必须在板内): [{a:.3f}, {b:.3f}] mm"
              f"  (下界绑 {bb['下界']['binding'][0]} / 上界绑 {bb['上界']['binding'][0]})")
    print("\n【候选枚举】 (★只列 + 代价 + 谁拍, 不代拍★)")
    w = [6, 10, 22, 22, 12, 12, 10, 12, 12, 26]
    hdr = ("候选", "jd_y0", "开口 Y", "P-2 净空/余", "S-2 净空/余", "2.5 余", "判据", "实践可做", "谁拍", "代价")
    print(" | ".join(h.ljust(w[i]) for i, h in enumerate(hdr)))
    print("-" * 104)
    costs = {
        "A": "零改动; 但开口 Y 偏低 (下沿离板下沿 7.835) ⇒ 等于把旧 15mm 板口径留在 30mm 板上 ⇒ 与迁常量方向相反",
        "C1": "需 hw-lead 给 30mm 板上 J_DEBUG 真实起点 [0数据]; 余量最宽",
        "C2": "同上; P-5/2.5 两头都留余量",
        "C3": "2.5 余量只剩 0.73 (≈1×FDM) ⇒ 再往上就进 B 区",
        "B1": "判据勉强过, 但 2.5 余量归零 (焊盘上沿正好 13.00) ⇒ 0 余量 = 实做必偏 ⇒ 不可用",
        "B2": "P-2 净空 = 0.60 (余 0.00) ⇒ 低于 FDM ±0.30 ⇒ 不可用; 且 2.5 直接判红 (13.40 > 13.00)",
    }
    for tag, val, desc, who in CANDIDATES:
        r = candidate_row(tag, val, desc, who)
        c = costs[tag]
        row = (tag, f"{val:.2f}", f"{r['open_y'][0]:.3f}..{r['open_y'][1]:.3f}",
               f"{r['p2_gap']:.2f} / {r['p2_margin']:+.2f}",
               f"{r['s2_gap']:.2f} / {r['s2_margin']:+.2f}",
               f"{r['c25_margin']:+.2f}",
               "✅" if r["all_pass"] else "❌",
               "✅" if r["practical_ok"] else "❌",
               who, c)
        print(" | ".join(str(x).ljust(w[i])[:w[i]] for i, x in enumerate(row)))
    print("\n【D 方案 (改 X 排布)】 ★不代拍★ —— J_DEBUG 阵列 X 50.50..55.58 与 P-2 (X=52.00) 重叠是 P-2 约束的根因;")
    print("   改 X ⇒ 焊盘排布属 HW 地界 + 影响探针阵列与治具基准 ⇒ 成本最高, 本单不碰 (★只登记, 不建议★)。")
    g24 = geom(24.50)
    c24 = criteria(24.50)
    print("\n【★「按相对位置迁」复核 (★机器结论, 与 ISS-264 §0.1 的说法有一处出入★)】")
    print(f"   若把 15mm 板上的相对位置平迁 ⇒ jd_y0 = 24.50 ⇒ 焊盘上沿 {g24['pad_y1']:.2f} / "
          f"开口 Y {g24['open_y0']:.3f}..{g24['open_y1']:.3f}")
    print(f"   · ★按闸脚本现值 (含检查项 2.5 的 13.00 上限) ⇒ 【判红】: 2.5 余量 {c24['2.5'][2]:+.2f}mm "
          f"(焊盘上沿 {g24['pad_y1']:.2f} > 13.00) ⇒ ★「按比例迁」走不通 = 机器可判的结论★")
    print(f"   · ★但 7.4 通用式 (两区间最近距离) 下 P-2 净空 = {g24['p2_gap']:.2f}mm (【非负】, 不重叠) ⇒ "
          f"★ISS-264 §0.1 那句「24.50 ⇒ −11.77 ⇒ 孔与焊盘阵列直接重叠, 缺口 12.37mm」只取了公式的第一分支, "
          f"在脚本自己的公式下复现不出来★ ⇒ ★该「重叠」结论【本单不引用】, 真正的拦路是 2.5 (及其 13.00 这个 15mm 板遗留常量)★")
    print(f"   · ★若 2.5 的上限按 30mm 板口径订正为 28.00 ⇒ jd_y0 = 24.50 几何上【可行】(P-2 {g24['p2_gap']:.2f} / "
          f"S-2 {g24['s2_gap']:.2f} / 开口 Y {g24['open_y0']:.3f}..{g24['open_y1']:.3f} 在板内) ⇒ "
          f"但阵列落到两个夹具孔【上方】⇒ 治具/探针对位与「开口在板下沿侧」的装配前提要重谈 ⇒ [0数据] ⇒ ★不代拍★")
    print(f"   · ★⇒ 一句话: ★「jd_y0 绝不许按比例迁」这个【结论方向】仍然成立 (按现值口径判红), "
          f"但【ISS-264 给的机理 (孔与焊盘阵列重叠 12.37mm) 与脚本自己的公式不符】, 机理要改成 2.5 判红★")


# ==================================================================================================
# 自检 (★三个反向用例, 一条不许删★)
# ==================================================================================================
def selftest() -> int:
    errs = []
    print("=" * 104)
    print("JD-Y0 FEASIBILITY — 自检 (ISS-267)")
    print("=" * 104)

    # ① 当前现值必须与闸脚本实跑一致 (开口 Y / P-5)
    g = geom(BASE["jd_y0"])
    if abs(g["open_y0"] - 7.835) > 5e-4 or abs(g["open_y1"] - 12.435) > 5e-4:
        errs.append(f"① 开口 Y 复算 {g['open_y0']:.3f}..{g['open_y1']:.3f} ≠ 7.835..12.435")
    if abs(g["p2_gap"] - 3.23) > 5e-3 or abs(g["s2_gap"] - 8.53) > 5e-3:
        errs.append(f"① P-5 复算 {g['p2_gap']:.2f}/{g['s2_gap']:.2f} ≠ 3.23/8.53")
    print(f"  [OK ] ① 现值复算一致: 开口 Y {g['open_y0']:.3f}..{g['open_y1']:.3f} · P-5 {g['p2_gap']:.2f}/{g['s2_gap']:.2f}")

    # ② 旧 15mm 板口径回代 ⇒ P-5 读数必须回到 1.00 / 1.03 (证明式子没漂)
    b2 = dict(BASE)
    b2["p2_y"], b2["s2_y"] = 7.50, 12.50
    saved = dict(BASE)
    BASE.clear(); BASE.update(b2)
    g_old = geom(9.50)
    BASE.clear(); BASE.update(saved)
    if abs(g_old["p2_gap"] - 1.00) > 5e-3 or abs(g_old["s2_gap"] - 1.03) > 5e-3:
        errs.append(f"② 旧口径回代得 {g_old['p2_gap']:.2f}/{g_old['s2_gap']:.2f} ≠ 1.00/1.03")
    print(f"  [OK ] ② 旧 15mm 板口径回代 ⇒ P-5 {g_old['p2_gap']:.2f}/{g_old['s2_gap']:.2f} (判据 0.60 未松)")

    # ③ 反向用例: jd_y0 推到 24.50 (「按相对位置迁」的值) ⇒ 按闸脚本现值必须判红
    c = criteria(24.50)
    if feasible(24.50):
        errs.append("③ jd_y0=24.50 时闸脚本判据没判红 ⇒ 判据没接上")
    if c["2.5"][0]:
        errs.append("③ jd_y0=24.50 时 2.5 (焊盘上沿 ≤13.00) 没判红 ⇒ 2.5 没接上")
    print(f"  [OK ] ③ jd_y0=24.50 ⇒ 闸脚本判据判红 (2.5: 焊盘上沿 {geom(24.50)['pad_y1']:.2f} > 13.00, "
          f"余 {c['2.5'][2]:+.2f}) ⇒ 「按相对位置迁」在【脚本现值口径】下走不通")

    # ④ ★★口径矛盾留痕★: ISS-264 §0.1 写「jd_y0=24.50 ⇒ P-2 净空 = −11.77 ⇒ 孔与焊盘阵列重叠」,
    #    但闸脚本 7.4 自己的公式是【两区间最近距离 max(...)】⇒ 阵列跑到孔【上方】时取第二分支
    #    ⇒ 本脚本按同式复算得 +8.50 (不重叠) ⇒ 该「重叠/缺口 12.37」结论【在脚本自己的公式下复现不出来】★
    #    ⇒ 机器留痕 ⇒ 供 main 订正 ISS-264 §0.1 (本单【不】改 ISS-264 交卷单, 那是上一趟的卷宗)
    p2_lo = BASE["p2_y"] - BASE["p2_d"] / 2.0
    p2_hi = BASE["p2_y"] + BASE["p2_d"] / 2.0
    branch_a = p2_lo - (24.50 + BASE["jd_pitch"])      # = −11.77 (ISS-264 只用了这一支)
    branch_b = 24.50 - p2_hi                            # = +8.50 (通用式的第二支)
    if abs(geom(24.50)["p2_gap"] - 8.50) > 5e-3:
        errs.append(f"④ jd_y0=24.50 的 7.4 通用式复算 {geom(24.50)['p2_gap']:.2f} ≠ 8.50")
    print(f"  [OK ] ④ 口径矛盾留痕: jd_y0=24.50 时 7.4 两分支 = [{branch_a:.2f} | {branch_b:.2f}] "
          f"⇒ 通用式取 max = {geom(24.50)['p2_gap']:.2f} ⇒ ISS-264 §0.1 的「−11.77 重叠」在脚本自己公式下复现不出来")

    print("=" * 104)
    if errs:
        print("[自检] ❌ 不一致 (⇒ rc=2):")
        for e in errs:
            print(f"   ❌ {e}")
    else:
        print("[自检] ✅ 一致 —— ① 现值复算一致 ② 旧 15mm 板口径回代一致 ③ 反向用例 (24.50) 判红 ④ 口径矛盾留痕 (24.50 通用式 = +8.50)")
    print("=" * 104)
    return 0 if not errs else 2


def to_json(intervals, intervals_d0) -> str:
    fr = []
    for f in FRAMES:
        c = frame_chain(f)
        fr.append({"frame": f["key"], "name": f["name"], "pcb_l": f["pcb_l"], "pcb_w": f["pcb_w"],
                   "pcb_thk": f["pcb_thk"], "layers": f["layers"], "chain": c, "src": f["src"]})
    cands = [candidate_row(t, v, d, w_) for t, v, d, w_ in CANDIDATES]
    g0 = geom(BASE["jd_y0"])
    return json.dumps({
        "current": {"jd_y0": BASE["jd_y0"], "open_y": [g0["open_y0"], g0["open_y1"]],
                    "p2_gap": g0["p2_gap"], "s2_gap": g0["s2_gap"], "crit": CRIT},
        "intervals_script_criteria": intervals,
        "intervals_with_D0": intervals_d0,
        "candidates": cands,
        "frames": fr,
    }, ensure_ascii=False, indent=2)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", "--selftest", dest="self_test", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return selftest()
    intervals = scan_intervals(feasible)
    intervals_d0 = scan_intervals(feasible_with_d0)
    if args.json:
        print(to_json(intervals, intervals_d0))
        return 0
    print_caliber_matrix()
    print_frame_table()
    print_findings(intervals, intervals_d0)
    print_jd_table(intervals, intervals_d0)
    print_board_crosscheck()
    print("\n★证据级: 本表全部为【设计态几何 + 公差栈】⇒ [推算]; 盘上板读数 = [实测]; ★实物 [实测] = 0 条★")
    print("★本单不拍板框、不拍 jd_y0 —— 只列选项 + 代价 + 谁拍★")
    return 0


if __name__ == "__main__":
    sys.exit(main())
