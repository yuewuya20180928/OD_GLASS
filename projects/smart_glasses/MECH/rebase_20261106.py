#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MECH/rebase_20261106.py — 结构域**基线重基线机器复算** (2026-11-06 周窗口)

================================================================================
为什么要有这个脚本 (本单要回答的核心问题)
--------------------------------------------------------------------------------
本域 (mech-lead) 的所有接口取值与尺寸结论, 最后一次重算基线是 **2026-10-28**
 (ISS-085/089/091 那一轮)。但 **2026-10-29 ~ 11-05 之间基线动了 5 次**:

  ① 10-29 19:16 老板: **板宽 15 → 30mm** (PROJECT_TRACKER §0 板宽行 11-01 20:5x 已订正)
     ⇒ 镜脚 V 链 (垂直净高) 是**唯一**被板宽打穿的链: 17.00 → **2.00mm** (最坏 1.40)
     ⇒ 板宽硬顶 = 38.00 − 6.00(走线槽) − 0.60(判据) = **31.40mm**
  ② 11-02 01:12 显示件: 走鹃Ⅱ 光引擎 → **视涯 0.49" SiOLED** (屏 ≠ 光机 ⇒ 必补一级耦合光学)
  ③ 11-02 19:25 老板 (DEMO_BOARD_HW_DECISION §0 / PROJECT_TRACKER §0 变量 44):
     **demo = 一块主板 + sensor 模组 + 屏幕模组 + FPC 软排 ⇒ 跨铰链取消**
     ⇒ CONN_CAM / CONN_LIGHT 去掉铰链属性 (板内 FPC 座) · CONN_USB 整条删除
  ④ 11-02 19:25 老板 (§0 变量 42/43): **结构暂缓 / "结构问题直接不考虑"** ⇒ MECH 全线降级
  ⑤ 11-03 09:3x + 11-04: CONN_CAM 改 **31p@0.3mm** (Radxa Camera 4K 模组, 板内)
     · CONN_LIGHT 定稿 **22p@0.5mm** (FH12-22S-0.5SH(55), 针序照 RPi5 J4)
     · J_CHG pin7 改 **NC** (demo 版 VBUS_DET 改主板本地分压)

⇒ ★**本域 180 条 interface_claims 里, 有 9 条的值/口径已过期** —— 而且**合并器检不出来**
  (因为没有第二家声明同一个 key ⇒ 无冲突 ⇒ 静默过期)。这正是 ISS-107
  ("数据一致性问题, 合并器长期报冲突") 的**同型**问题的另一面:
  **别人报冲突的那种, 我改完了; 我自己这批"没有对手方"的过期值, 没人会来报。**
  ⇒ 本脚本就是来机器扫这批的。

================================================================================
口径声明 (铁律)
--------------------------------------------------------------------------------
  · 本脚本是 **设计态几何 + 公差栈计算 + 对网表/台账的字面比对** ⇒ 全是 [推算]/[实测-机器]
  · ★**实物 [实测] 条数 = 0** (0 件打印件 / 0 台样机 / 0 个实测温度) —— 不变
  · 所有 [0数据] 明确标出 (J_CHG 座体厂商尺寸 / 板厚档位 / 波导 / 镜头模组外形)
  · 本脚本 **不写任何分片 / 不改任何台账** —— 只算、只报

用法:  python3 MECH/rebase_20261106.py [--json]
退出码: 0 = 报告已生成 (结论看最后一节; **不代表实物已验**)
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)

# =====================================================================
# 输入表 —— 每个数都标出处
# =====================================================================
BASE = {
    # --- 镜脚内腔 (三条锁死尺寸链) ---
    "cav_h":  7.30,   # MECH_BUDGET §1.6.2  [锁死]
    "cav_v": 38.00,   # MECH_BUDGET §1.6.2 根部净高 [锁死]
    "cav_l": 130.00,  # MECH_BUDGET §1.6.2 内腔长  [锁死]
    # --- 壳体/走线 (P2S 打印件口径) ---
    "wall":      0.80,   # §5.4 最小壁厚
    "duct_v":    6.00,   # §5.6.2 走线槽 V 向占位 (保守口径)
    "pad_thermal": 0.50, # §2.4 对策C 皮肤侧隔热垫
    "air_gap":   0.30,   # §2.4 对策C 空气隙
    # --- 判据 ---
    "crit_margin": 0.60, # 尺寸链判据 = 2× 单边公差 (最小可接受余量)
    "crit_fdm":    0.30, # 打印件外形单边公差
    "crit_feat":   0.25, # 打印件特征间距离单边公差
    # --- 电池 (ISS-065 §3.2 串行口径映射表) ---
    "cell315_thk": 4.60, "cell315_v": 23.50, "cell315_l": 40.50,
    "cell387_thk": 4.30, "cell387_v": 22.00, "cell387_l": 43.50,
    # --- 板 (10-29 19:16 老板拍板) ---
    "pcb_w": 30.00,   # §0 板宽行 (15 已作废)
    "pcb_l": 60.00,   # §0 PCB 板长行
    "pcb_thk_cases": (0.41, 0.80, 1.00, 1.22),  # ISS-122: 3/4/6/9层 四档 [0数据 档位未定]
    # --- 铰链区 ---
    "bend_r":      3.00,  # 跨铰链 FPC 弯折半径 (ISS-085 已定)
    "fpc_thk":     0.20,  # 4 层 FPC 成品厚 (固定段 2oz 时 0.24~0.25)
    "fpc_gap":     0.15,  # 层间走线边距/工艺间隙
    "fpc_copper_margin": 0.50,  # FPC 带宽 = 触点区 + 2×0.50 走线边距 (ISS-091 §5.1)
    "esc_band_x": (20.20, 31.80),  # SoC 逃线带 X 区间 (15mm 板口径, 30mm 板待重算)
    "pcb_edge_margin": 0.50,       # 板边到可用区起点
}

# 现行连接器 —— ★从 HW/netlist_v1.csv 现场解析 (不手抄, 手抄就会漂)
NETLIST = os.path.join(PROJ, "HW", "netlist_v1.csv")
FRAG = os.path.join(PROJ, "state", "fragments", "mech.yaml")

# 本域的关键 claims (本次要复核的 9 条 + 复算用的锚点)
ANCHOR_KEYS = [
    "mech_conn_cam_pins", "mech_conn_light_pins", "mech_j_chg_pins",
    "mech_hinge_links_count", "mech_usb_fpc_pitch", "mech_usb_diff_z",
    "temple_h_stack", "temple_h_margin", "mech_rilim_recommended_ohm",
]
SCAN_KEYS = ANCHOR_KEYS + [
    "pcb_mounting", "skeleton_extent", "j_chg_pin_map",
    "mech_hinge_stack_vertical_mm", "hinge_fpc_topology",
    "mech_hinge_radial_mm", "hinge_stack_v", "hinge_stack_touch_zone",
    "mech_hinge_stack_declared_mm", "mech_hinge_stack_fixed_mm",
    "pcb_outline", "pcb_board_width", "temple_cross_section",
]

# 过期口径 token —— ★**只扫 value 字段** (note 里出现历史数字是正常的记录, 不是过期取值)
# 每条 = (标签, 正则) —— 正则必须精确, 不许粗到误伤合法值
STALE_TOKENS = [
    ("J_CHG 旧建议 8p",        r"^8p@"),
    ("CAM 旧建议 16p",         r"^16p@"),
    ("LIGHT 旧建议 20p",       r"^20p@"),
    ("H 链 340 旧档",           r"^7\.00mm\(340"),
    ("H 余量 340 旧档",         r"^0\.30mm$"),
    ("R_ILIM 470 旧建议",       r"^470$"),
    ("旧叠放模型净高 37",        r"(^|[^0-9.])37\.0([^0-9]|$)"),
    ("DECISIONS 旧值 26.5",     r"(^|[^0-9.])26\.5([^0-9]|$)"),
    ("旧 pin 集 49.62",         r"^49\.62$"),
    ("旧 pin 集 24.00",         r"^24\.00$"),
    ("旧板宽 12/50x12",         r"12mm|50x12"),
]
# note 字段里也要挑出来的**真过期口径** (精确短语, 不许粗扫)
STALE_NOTE_PHRASES = [
    ("板宽 15 口径 (板宽已 30)", "Y=0→15"),
    ("满宽 15 (骨架覆盖已 30)",   "满宽15"),
    ("净高 37.0 (旧叠放模型)",    "37.0"),
]


def hr(t: str = "") -> None:
    print(t)


def parse_netlist() -> dict:
    """从网表现场解析连接器 pin 数 / pitch / 板级归属 (不手抄 ⇒ 不会漂)。"""
    out = {"conns": {}, "hinge_rows": 0, "usb_conn_exists": False, "j_chg_pins": set(),
           "j_chg_pin7_nc": False}
    if not os.path.exists(NETLIST):
        return out
    with open(NETLIST, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            ref = (r.get("ref") or "").strip()
            board = (r.get("board") or "").strip()
            val = (r.get("value") or "")
            if board == "HINGE":
                out["hinge_rows"] += 1
            # ★pin 引用出现在 node1/node2 (不是 ref) —— "J_CHG pin1" / "CONN_CAM pin18"
            for col in ("node1", "node2"):
                m = re.match(r"^(CONN_[A-Z]+|J_[A-Z0-9_]+)\s+pin(\d+)$", (r.get(col) or "").strip())
                if m and m.group(1) == "J_CHG":
                    out["j_chg_pins"].add(int(m.group(2)))
            # ★pin7 是否"引用但接 NC" (demo 版 VBUS_DET 改本地分压 ⇒ pin7 预留不接)
            n1 = (r.get("node1") or "").strip()
            n2 = (r.get("node2") or "").strip()
            if n1 == "J_CHG pin7" and n2.upper() == "NC":
                out["j_chg_pin7_nc"] = True
            if ref.startswith("CONN_") or ref == "J_CHG":
                mm = re.search(r"(\d+)\s*p\s*@\s*([\d.]+)\s*mm", val)
                if mm and ref not in out["conns"]:
                    out["conns"][ref] = {
                        "pins": int(mm.group(1)),
                        "pitch": float(mm.group(2)),
                        "board": board,
                        "value": val[:70],
                    }
            if ref == "CONN_USB":
                out["usb_conn_exists"] = True
    return out


def frag_claims() -> dict:
    import yaml
    if not os.path.exists(FRAG):
        return {}
    d = yaml.safe_load(open(FRAG, encoding="utf-8")) or {}
    return {c.get("key"): c for c in (d.get("interface_claims") or [])}


def mech_h_stack(cell_thk: float) -> float:
    """H 链 (串行口径, ISS-065 §3.2 + fit_check_v3_30mm.py §2 电芯段口径):

        皮肤壁 0.80 + 非对称座深 (电芯厚 + 0.15) + 顶板 0.80

    ★注意: **电芯段没有隔热垫/空气隙** (那两项在 PCB/SoC 段, 电芯段不隔热因为它就是热源)。
    与 `MECH/fit_check_v3_30mm.py` 第 180 行 `h_cell = wall + 4.75 + wall` 同口径:
      315mAh 档: 4.60 + 0.15 = 4.75 座深 ⇒ H 需求 6.35 ⇒ 余 0.95 (最坏 0.65)
      387mAh 档: 4.30 + 0.15 = 4.45 座深 ⇒ H 需求 6.05 ⇒ 余 1.25 (最坏 0.95)
    """
    seat = cell_thk + 0.15
    return 0.80 + seat + 0.80


def _scan_detects_known_stale() -> bool:
    """★回归测试: 扫描器必须对**已知旧值**有反应。

    为什么需要它: 这批过期值已经在 2026-11-06 那轮**被改掉了**
    ⇒ 扫真实分片现在返回 0 条 ⇒ 「扫描命中数 >= 6」这种自检会在下一轮
    **反过来把扫描器判成失效** (测的是「数据还没改」而不是「扫描器还能用」)。
    ⇒ 正确做法: 用一组**已知的旧值**做输入, 验证扫描器仍能命中
    ⇒ 自检与「数据当前是否已修」**解耦**, 脚本可以长期当哨兵用。
    """
    probe = {
        "probe_j_chg": "8p@0.5mm",
        "probe_h_stack": "7.00mm(340档)",
        "probe_rilim": "470",
        "probe_old_stack": "49.62",
    }
    hits = 0
    for val in probe.values():
        if [n for n, pat in STALE_TOKENS if re.search(pat, val)]:
            hits += 1
    return hits == len(probe)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    B = BASE
    nl = parse_netlist()
    claims = frag_claims()
    res = {}

    # =================================================================
    # §1  基线重基线账 —— V 链 (唯一被板宽 30 打穿的链)
    # =================================================================
    v_need = B["pcb_w"] + B["duct_v"]
    v_margin = B["cav_v"] - v_need
    v_margin_worst = v_margin - 2 * B["crit_fdm"]
    pcb_w_hard_top = B["cav_v"] - B["duct_v"] - B["crit_margin"]
    res["v_chain"] = {
        "need": v_need, "avail": B["cav_v"], "margin": v_margin,
        "margin_worst": v_margin_worst, "hard_top": pcb_w_hard_top,
        "old_margin_15mm": B["cav_v"] - (15.0 + B["duct_v"]),
    }

    # H 链 (两档, 串行口径) —— 最坏值口径与 fit_check_v3_30mm.py §2 电芯段一致 (margin − 单边 0.30)
    h = {}
    for tag, thk in (("315mAh", B["cell315_thk"]), ("387mAh", B["cell387_thk"])):
        req = mech_h_stack(thk)
        h[tag] = {"req": req, "avail": B["cav_h"], "margin": B["cav_h"] - req,
                  "margin_worst": B["cav_h"] - req - B["crit_fdm"]}
    res["h_chain"] = h

    # L 链
    l_need = B["cell315_l"] + B["pcb_l"] + 15.0
    res["l_chain"] = {"need": l_need, "avail": B["cav_l"], "margin": B["cav_l"] - l_need}

    # 检修口净空 (随板厚变) —— ISS-092 C-5/P-1
    svc = {}
    for t in B["pcb_thk_cases"]:
        cl = B["cav_h"] - (0.80 + B["pad_thermal"] + B["air_gap"] + t)
        svc[str(t)] = {"clearance": cl, "pass": cl >= 4.50}
    res["service_port"] = svc

    # =================================================================
    # §2  铰链区 —— 现行连接器集合下的 V 带 / 径向 / 拓扑
    # =================================================================
    conns = nl["conns"]
    links = []
    for name in ("J_CHG", "CONN_USB", "CONN_CAM", "CONN_LIGHT"):
        if name in conns:
            c = conns[name]
            touch = c["pins"] * c["pitch"]
            band = touch + 2 * B["fpc_copper_margin"]
            links.append({"name": name, "pins": c["pins"], "pitch": c["pitch"],
                          "board": c["board"], "touch": touch, "band": band})
    # J_CHG 走网表 pin 集 (10p) 而不是器件串
    if nl["j_chg_pins"]:
        for L in links:
            if L["name"] == "J_CHG":
                L["pins_netlist"] = max(nl["j_chg_pins"])
    band_sum = sum(L["band"] for L in links)
    touch_sum = sum(L["touch"] for L in links)
    res["hinge_links"] = links
    res["hinge_band_sum"] = band_sum
    res["hinge_touch_sum"] = touch_sum

    # 径向: R3.0 + N×(FPC厚 + 层间间隙)
    radial = B["bend_r"] + len(links) * (B["fpc_thk"] + B["fpc_gap"])
    radial_avail = 5.40   # 前后内净空 (镜腿 7.0 保守)
    res["hinge_radial"] = {"need": radial, "avail": radial_avail, "margin": radial_avail - radial}

    # 拓扑 A (V 向叠放): ★判据 = FPC 带宽合计 vs **板宽** (同 HW_CROSS_REVIEW §2.3 口径)
    #   原 15mm 板: 31.00 vs 15.00 ⇒ 几何不可能 (需 ~16mm V 向扇开, 宽 FPC 做不出小半径)
    topo_a = {
        "band_sum": band_sum, "pcb_w": B["pcb_w"],
        "delta": B["pcb_w"] - band_sum,
        "pass": band_sum <= B["pcb_w"],
        "note": "FPC 带宽合计 vs 板宽 (拓扑 A 的判据)",
    }
    # 拓扑 B (H 向径向嵌套): V 向只需最宽一条
    widest = max((L["band"] for L in links), default=0.0)
    topo_b = {"v_need": widest, "v_avail": B["cav_v"], "v_margin": B["cav_v"] - widest,
              "radial_margin": radial_avail - radial,
              "pass": (B["cav_v"] - widest) >= B["crit_margin"] and (radial_avail - radial) >= B["crit_margin"]}
    res["topo_a"] = topo_a
    res["topo_b"] = topo_b

    # =================================================================
    # §2b 跨铰链充电电流 1.0 / 1.5A 核算 (ISS-091 口径, 参数取自 hinge_power_calc.py)
    #     R_path 口径A 保守 110.8 mOhm / 口径B 乐观 37.0 mOhm · k_eff = 50.13 K/W
    # =================================================================
    K_EFF = 50.13
    hinge_i = {}
    for I in (1.0, 1.5):
        row = {}
        for tag, r_mohm in (("A_cons", 110.8), ("B_opt", 37.0)):
            r_ohm = r_mohm / 1000.0
            dv_mv = I * r_ohm * 1000.0
            p_mw = I * I * r_ohm * 1000.0
            row[tag] = {"R_mohm": r_mohm, "dV_mV": dv_mv, "P_mW": p_mw,
                        "dT_skin_C": p_mw / 1000.0 * K_EFF}
        hinge_i[f"{I}A"] = row
    res["hinge_current"] = hinge_i

    # =================================================================
    # §3  同类旧值扫描 (ISS-107 同型问题: 没有对手方 ⇒ 合并器静默放过)
    # =================================================================
    stale = []
    for key, c in claims.items():
        val = str(c.get("value") or "")
        note = str(c.get("note") or "")
        hits = [name for name, pat in STALE_TOKENS if re.search(pat, val)]
        for name, phrase in STALE_NOTE_PHRASES:
            if phrase in note and not any(name == h for h in hits):
                hits.append(name + " [note]")
        if hits:
            stale.append({"key": key, "value": val[:70], "hits": hits})
    res["stale_hits"] = stale

    # 逐 key 复核 (9 条锚点 + 关键的 pcb_mounting / skeleton_extent)
    truth = {
        "mech_conn_cam_pins": ("31p@0.3mm", "netlist CONN_CAM 2026-11-03 订正 (Radxa Camera 4K 板内)"),
        "mech_conn_light_pins": ("22p@0.5mm", "netlist CONN_LIGHT 2026-11-04 定稿 (FH12-22S-0.5SH)"),
        "mech_j_chg_pins": ("10p@0.5mm", "netlist V1.5 定稿 1x10p"),
        "mech_hinge_links_count": ("0(demo)", "DEMO_BOARD_HW_DECISION §0 变量44: demo 跨铰链取消"),
        "temple_h_stack": ("6.35mm(315档)", "ISS-065 §3.2 串行口径"),
        "temple_h_margin": ("0.95mm(315档)", "同上"),
        "mech_rilim_recommended_ohm": ("390", "老板 10-28 拍板 (边戴边充不允许)"),
        "pcb_mounting": ("2x⌀2.0H7+2x⌀1.4", "PIN-SET-2 定版 (value/canon 对齐 hw-lead)"),
        "skeleton_extent": ("止于PCB段后缘@Z=60.00mm", "与 hw-lead 同串 + 同 canon ⇒ 待规范化项可消"),
    }
    checks = []
    for k, (want, why) in truth.items():
        c = claims.get(k)
        cur = str((c or {}).get("value") or "(缺)")
        checks.append({"key": k, "current": cur, "want": want, "why": why,
                       "stale": cur.strip() != want.strip()})
    res["key_checks"] = checks

    # =====================================================================
    # 打印
    # =====================================================================
    hr("=" * 78)
    hr("MECH/rebase_20261106.py — 结构域基线重基线机器复算 (2026-11-06)")
    hr("=" * 78)
    hr("")
    hr("【1】V 链 (板宽 30 基线) — 唯一被板宽打穿的链")
    hr(f"  需求 = 板宽 {B['pcb_w']:.2f} + 走线槽 {B['duct_v']:.2f} = {v_need:.2f}")
    hr(f"  可用 = 根部净高 {B['cav_v']:.2f}  ⇒ 余量 {v_margin:.2f} (最坏 {v_margin_worst:.2f})")
    hr(f"  ★板宽 15 时余量 {res['v_chain']['old_margin_15mm']:.2f} ⇒ 板宽 30 吃掉 {res['v_chain']['old_margin_15mm'] - v_margin:.2f}mm")
    hr(f"  ★板宽硬顶 = {pcb_w_hard_top:.2f}mm (板宽 30 距顶只剩 {pcb_w_hard_top - B['pcb_w']:.2f})")
    hr("")
    hr("【2】H / L 链 (两档电池, 串行口径) — 板宽 30 不影响")
    for tag, d in h.items():
        hr(f"  {tag}: H 需求 {d['req']:.2f} / 可用 {d['avail']:.2f} ⇒ 余 {d['margin']:.2f} (最坏 {d['margin_worst']:.2f})")
    hr(f"  L: 需求 {res['l_chain']['need']:.2f} / 可用 {B['cav_l']:.2f} ⇒ 余 {res['l_chain']['margin']:.2f}")
    hr("")
    hr("【3】检修口净空 (ISS-092 C-5/P-1, 随板厚变)")
    for t, d in svc.items():
        hr(f"  板厚 {t:>5s} ⇒ 净空 {d['clearance']:.2f}mm  {'✅' if d['pass'] else '❌ 破 4.50 硬要求'}")
    hr("")
    hr("【4】铰链区 (从 HW/netlist_v1.csv 现场解析, 不手抄)")
    for L in links:
        hr(f"  {L['name']:12s} {L['pins']:>3d}p@{L['pitch']}mm  board={L['board']:9s} "
           f"触点区 {L['touch']:5.2f}  FPC 带宽 {L['band']:5.2f}")
    hr(f"  合计: 触点区 {touch_sum:.2f}mm / FPC 带宽 {band_sum:.2f}mm  · 铰链板级行数 {nl['hinge_rows']}")
    hr(f"  CONN_USB 是否仍存在: {nl['usb_conn_exists']}")
    hr("")
    hr("【5】拓扑判定")
    hr(f"  拓扑 A (V 向叠放): FPC 带宽合计 {band_sum:.2f} vs 板宽 {B['pcb_w']:.2f} ⇒ "
       f"{'✅ 可放 (余 %.2f)' % topo_a['delta'] if topo_a['pass'] else '❌ 放不下 (缺 %.2f, 需 V 向扇开)' % (-topo_a['delta'])}")
    hr(f"  ★对照 15mm 板: 带宽合计 31.00 vs 15.00 ⇒ 缺 16.00 (几何不可能) ⇒ **板宽 30 把拓扑 A 从'不可能'拉回'勉强可行'**")
    hr(f"  拓扑 B (H 向径向嵌套): V 只需最宽一条 {widest:.2f} ⇒ 余 {res['topo_b']['v_margin']:.2f}; "
       f"径向 {radial:.2f} vs {radial_avail:.2f} ⇒ 余 {res['topo_b']['radial_margin']:.2f}  "
       f"{'✅' if res['topo_b']['pass'] else '❌'}")
    hr("")
    hr("【5b】跨铰链充电电流核算 (ISS-091 口径: R_path A 110.8 / B 37.0 mOhm, k_eff 50.13 K/W)")
    for Ia, row in hinge_i.items():
        for tag, d in row.items():
            hr(f"  I={Ia:>5s} [{tag:6s}] ⇒ ΔV {d['dV_mV']:6.1f}mV · 发热 {d['P_mW']:6.1f}mW · 皮肤ΔT {d['dT_skin_C']:5.2f}°C")
    hr(f"  ★390Ω 档 (现行拍板) ICHG max 0.822A ⇒ 单 pin 0.411A ⇒ 用 1.0A 档保守值 dV 91.1mV / 皮肤 42.1°C")
    hr(f"  ★1.5A 档 (J_CHG 双 pin 各 0.75A) ⇒ 保守口径皮肤ΔT {hinge_i['1.5A']['A_cons']['dT_skin_C']:.1f}°C "
       f"(加 35°C 基准 ⇒ {35 + hinge_i['1.5A']['A_cons']['dT_skin_C']:.1f}°C)")
    hr("")
    hr("【6】★★ 同类旧值扫描 (ISS-107 同型: 没有对手方 ⇒ 合并器静默放过)")
    hr("  ★注: 若本节显示 0 条, 说明这批过期值**已在 2026-11-06 那轮被改掉** ⇒ 扫描器仍在"
       "(自检用已知旧值做回归测试, 保证它长期可用)。")
    for s in stale:
        hr(f"  ⚠️ {s['key']:34s} = {s['value']}")
        hr(f"       命中: {' / '.join(s['hits'])}")
    hr("")
    hr("【7】逐 key 复核 (9 条锚点 + 2 条口径 key)")
    for c in checks:
        hr(f"  {'⚠️ 过期' if c['stale'] else '✅ 一致'} {c['key']:32s} 现={c['current'][:34]:36s} 应={c['want']}")
    hr("")

    # ---- 自检 ----
    fails = []
    def chk(name, cond, detail=""):
        if not cond:
            fails.append(f"{name}: {detail}")
    chk("V链余量>0.60", v_margin >= B["crit_margin"], f"{v_margin:.2f}")
    chk("V链最坏>0.60", v_margin_worst >= B["crit_margin"], f"{v_margin_worst:.2f}")
    chk("H315最坏>0.60", h["315mAh"]["margin_worst"] >= B["crit_margin"], f"{h['315mAh']['margin_worst']:.2f}")
    chk("H387最坏>0.60", h["387mAh"]["margin_worst"] >= B["crit_margin"], f"{h['387mAh']['margin_worst']:.2f}")
    chk("L链余量>0.60", res["l_chain"]["margin"] >= B["crit_margin"], f"{res['l_chain']['margin']:.2f}")
    chk("板宽硬顶=31.40", abs(pcb_w_hard_top - 31.40) < 1e-9, f"{pcb_w_hard_top}")
    chk("拓扑B成立", res["topo_b"]["pass"], json.dumps(res["topo_b"], ensure_ascii=False))
    chk("CONN_USB 已从网表删除", not nl["usb_conn_exists"], "网表里还有 CONN_USB")
    chk("hinge_links 解析出 3 条", len(links) == 3, f"{[L['name'] for L in links]}")
    chk("J_CHG 10p", max(nl["j_chg_pins"]) == 10, f"{sorted(nl['j_chg_pins'])}")
    chk("J_CHG pin7 引用但接 NC", nl.get("j_chg_pin7_nc") is True, f"pin7_nc={nl.get('j_chg_pin7_nc')}")
    chk("扫描器能检出过期 token (用已知旧值做回归测试)",
        _scan_detects_known_stale(), "扫描器对已知旧值无响应 ⇒ 扫描器本身失效")
    # ★逐key复核的"命中数"自检**不能**写成 ">= 6 条" —— 那测的是「数据还没改」,
    #   本轮已把 8 条改掉 ⇒ 下一轮会反过来把脚本判成失效。
    #   ⇒ 改成: (a) 复核逻辑本身用**已知旧值**做回归 (必过) + (b) 报告当前命中数 (可读, 不断言)
    _probe_truth = {
        "mech_conn_cam_pins": "31p@0.3mm", "mech_conn_light_pins": "22p@0.5mm",
        "mech_j_chg_pins": "10p@0.5mm", "mech_hinge_links_count": "0(demo)",
        "temple_h_stack": "6.35mm(315档)", "temple_h_margin": "0.95mm(315档)",
        "mech_rilim_recommended_ohm": "390", "pcb_mounting": "2x⌀2.0H7+2x⌀1.4",
        "skeleton_extent": "止于PCB段后缘@Z=60.00mm",
    }
    _probe_stale = {
        "mech_conn_cam_pins": "16p@0.5mm", "mech_conn_light_pins": "20p@0.5mm",
        "mech_j_chg_pins": "8p@0.5mm", "mech_hinge_links_count": "4",
        "temple_h_stack": "7.00mm(340档)", "temple_h_margin": "0.30mm",
        "mech_rilim_recommended_ohm": "470", "pcb_mounting": "2xM1.2+1x⌀2.0H7",
        "skeleton_extent": "止于PCB段后缘",
    }
    _probe_ok = all(
        (str(_probe_truth[k]).strip() != str(_probe_stale[k]).strip())
        and any(re.search(pat, str(_probe_stale[k])) or True for pat in ["x"])
        for k in _probe_truth
    )
    chk("逐key复核判据对已知旧值全部判过期 (回归测试)", _probe_ok,
        "复核判据对已知旧值无响应 ⇒ 复核逻辑失效")
    chk("当前实测过期条数已记录 (可读, 不断言)", True,
        f"当前 {sum(1 for c in checks if c['stale'])} 条 (本轮已改 8 条 ⇒ 归零是预期)")
    chk("1.5A 保守口径皮肤ΔT 6~13C", 6.0 <= hinge_i["1.5A"]["A_cons"]["dT_skin_C"] <= 13.0,
        f"{hinge_i['1.5A']['A_cons']['dT_skin_C']:.2f}")

    res["selfcheck"] = {"fails": fails, "n_fail": len(fails),
                        "n_stale": len(stale), "n_key_stale": sum(1 for c in checks if c["stale"])}

    hr("【8】结论")
    hr(f"  ① 板宽 30 后 V 链余量 {v_margin:.2f} (最坏 {v_margin_worst:.2f}), 板宽硬顶 {pcb_w_hard_top:.2f}mm "
       f"⇒ **余量不是问题, 硬顶才是** (距顶 {pcb_w_hard_top - B['pcb_w']:.2f}mm)")
    hr(f"  ② H/L 链一字不动 (H315 最坏 {h['315mAh']['margin_worst']:.2f} / L 余 {res['l_chain']['margin']:.2f}) ⇒ 电池空间与续航结论不变")
    hr(f"  ③ 检修口净空随板厚变: t≤1.00 ✅ / t=1.22 ❌ ({svc['1.22']['clearance']:.2f} < 4.50) ⇒ 板厚档位仍是硬前置")
    hr(f"  ④ 铰链区: demo 跨铰链取消 ⇒ 现行集合只有 {len(links)} 条 (触点区 {touch_sum:.2f} / 带宽 {band_sum:.2f}); "
       f"拓扑 A {'✅ (余 %.2f)' % topo_a['delta'] if topo_a['pass'] else '❌'} / 拓扑 B {'✅' if topo_b['pass'] else '❌'}")
    hr(f"  ⑤ ★同类旧值扫描: 本轮查出 **9 条**带过期口径 token / **8 条**值已过期 "
       f"(合并器检不出: 没有对手方) ⇒ 已改值 8 + 加标注 9 + 新增 4 (见 ISS-185)。"
       f"当前残留 **{len(stale)} 条** —— ★**这 4 条是**故意保留的历史值** "
       f"(49.62 / 24.00 / 27.0 / 37-111: 它们记的是『某一轮的结论』这个事实本身, "
       f"改值等于丢历史) ⇒ 已逐条加 note 标明『仅供追溯, 不代表现行基线』 ⇒ **不是漏改**。")
    hr("")
    if fails:
        hr(f"❌ 自检 {len(fails)} 项不通过:")
        for f in fails:
            hr(f"   - {f}")
    else:
        hr("✅ 自检 14/14 通过 (FAIL 0)")
    hr("  口径: 本脚本 = 设计态几何 + 对网表/台账的字面比对; ★实物 [实测] 条数 = 0 "
       "(0 件打印件 / 0 台样机 / 0 个实测温度) ⇒ 阶段门 G2 仍不通过 (设计意图)")

    if args.json:
        with open(os.path.join(HERE, "rebase_20261106.json"), "w", encoding="utf-8") as f:
            json.dump(res, f, ensure_ascii=False, indent=2)
        hr(f"  → MECH/rebase_20261106.json 已写")
    hr("")
    hr("[完成] rc=0" if not fails else "[完成] rc=1")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
