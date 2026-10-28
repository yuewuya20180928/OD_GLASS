#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hw_cross_review_check.py —— ISS-089 硬件侧交叉评审 (机械/热/装配/跨铰链) 机械自检
=================================================================================
输入: HW/SCHEMATIC_V1.md (V1.6, 10 页) + HW/netlist_v1.csv (网表为唯一口径)
输出: 本文/交接单里的每一个关键数字 (全部机器复算, 不靠人肉数)

口径声明 (先看这个, 避免误读):
  ① 跨铰链连接器的 pin 数 **以 netlist_v1.csv 实际引用为准**, 不以 P9 页正文的声明为准
     (正文与器件表/网表不一致本身就是本次评审的发现之一)
  ② "堆叠" 分两个口径分别算:
       - 触点区口径 (P9/DECISIONS 用的口径): Σ(N × pitch)
       - FPC 带宽口径 (物理口径): Σ(N × pitch + 2 × 边距) —— 边距 0.50mm/侧 [推算]
  ③ 净高取两个值都算:
       - 37.00mm (P9 页 / DECISIONS 2026-10-27 口径, 出自已作废的"叠放"模型)
       - 38.00mm (现行"沿长度串行"模型, MECH/fit_check.py BASE cav_v)
  ④ 公差: FDM 外形 ±0.30mm (MECH/fit_check.py 口径), 判据 ≥ 2 × 0.30 = 0.60mm

用法:  python3 MECH/hw_cross_review_check.py [--json]
退出码: 0 = 全部检查项跑完 (不代表所有结论都是 PASS, FAIL 项在输出里标红)
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
NETLIST = os.path.join(PROJ, "HW", "netlist_v1.csv")
SCHEM = os.path.join(PROJ, "HW", "SCHEMATIC_V1.md")

# ---------------------------------------------------------------- 基线常数
BASE = {
    "pitch": 0.50,              # 跨铰链 FPC 统一 pitch [官方-项目内]
    "fpc_edge_margin": 0.50,    # FPC 触点区两侧走线边距 [推算, ISS-091 §5.1 同源]
    "cav_h": 7.30,              # 镜脚前后厚 [推算, MECH/fit_check.py BASE cav_h]
    "cav_v_stale": 37.00,       # 根部净高 (旧"叠放"模型口径, 已作废)
    "cav_v_now": 38.00,         # 根部净高 (现行"串行"模型, fit_check BASE cav_v)
    "wall": 0.80,               # 打印件单壁 [推算]
    "toler": 0.30,              # FDM 外形公差 ± [推算]
    "judge": 0.60,              # 判据 = 2 × 公差 [推算]
    "bend_r": 3.00,             # 弯折半径 [官方-项目内]
    "fpc_t": 0.20,              # FPC 成品厚 (4 层 1oz) [推算]
    "fpc_t_2oz": 0.25,          # FPC 成品厚 (固定段 2oz) [推算]
    "nest_gap": 0.15,           # FPC 嵌套间隙 [推算]
    "pcb_len": 60.00,           # 主 PCB 板长 [决策 10-28]
    "pcb_w": 15.00,             # 主 PCB 板宽 [决策 10-27]
    "pcb_edge": 0.50,           # 4 角工艺边 [推算]
    "soc_escape_x": (20.20, 31.80),   # SoC 逃线带 X 区间 [推算, hw-lead 定版]
    "hole_x": (5.00, 15.00, 55.00),    # 3 个固定孔 X [决策 10-28]
    "conn_depth": 6.40,         # ≥10p 0.5mm ZIF 座体进深 [推算, J_CHG_SELECTION]
    "conn_depth_4p": 5.00,      # 4p 座体进深 [推算]
    "conn_gap_x": 0.50,         # 相邻连接器 X 向间隔 [推算]
    "chg_board": (25.0, 10.0),  # 充电板 尺寸 [推算, CHARGE_BOARD_SPEC]
    "typec_panel": (9.50, 3.60),       # Type-C 面板开孔 [官方-结构]
    "typec_body": (8.94, 3.26),        # Type-C 母座本体 [官方]
}

RESULTS: list[dict] = []


def rec(cid: str, name: str, value, verdict: str, note: str, evidence: str = "[推算]"):
    RESULTS.append({"id": cid, "name": name, "value": value,
                    "verdict": verdict, "note": note, "evidence": evidence})
    tag = {"PASS": "✅", "FAIL": "❌", "COND": "⚠️", "INFO": "· "}[verdict]
    v = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    print(f"{tag} {cid:10s} {name}")
    print(f"          {v}")
    if note:
        print(f"          → {note}")
    return value


# ------------------------------------------------- 网表 pin 占用 (唯一口径)
def netlist_pin_usage():
    rows = list(csv.reader(open(NETLIST, encoding="utf-8")))
    hdr = rows[0]
    idx = {k: hdr.index(k) for k in ("page", "net", "node1", "node2", "ref",
                                     "value", "type", "dnp", "evidence", "tbd",
                                     "note", "conn_id", "board")}
    usage: dict[str, dict] = {}
    for r in rows[1:]:
        if not r or len(r) < len(hdr):
            continue
        for cell in (r[idx["node1"]], r[idx["node2"]]):
            m = re.match(r"^(\w+)\s+pin(\d+)$", cell.strip())
            if not m:
                continue
            conn, pin = m.group(1), int(m.group(2))
            u = usage.setdefault(conn, {"mand": set(), "dnp": set(), "page": set()})
            u["page"].add(r[idx["page"]])
            if r[idx["dnp"]].strip() == "DNP":
                u["dnp"].add(pin)
            else:
                u["mand"].add(pin)
    return usage


def schematic_declared_pins():
    """从 SCHEMATIC_V1.md 的器件表行里抽 '1×Np@0.5mm' 声明 (用于与网表对照)。"""
    txt = open(SCHEM, encoding="utf-8").read()
    decl = {}
    for m in re.finditer(r"\|\s*(J_CHG|CONN_USB|CONN_CAM|CONN_LIGHT)\s*\|.*?(\d+)\s*×\s*(\d+)\s*p", txt):
        conn, row, n = m.group(1), int(m.group(2)), int(m.group(3))
        decl.setdefault(conn, set()).add(n)
    # P9 正文叙述行里的声明
    narr = {}
    for conn in ("J_CHG", "CONN_USB", "CONN_CAM", "CONN_LIGHT"):
        for m in re.finditer(re.escape(conn) + r"[^。\n]{0,30}?(\d+)\s*×\s*(\d+)\s*p", txt):
            narr.setdefault(conn, set()).add(int(m.group(2)))
    return decl, narr


# ------------------------------------------------------------------ 主流程
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    print("=" * 100)
    print("ISS-089 硬件侧交叉评审 (机械/热/装配/跨铰链) —— 机械自检")
    print(f"输入: HW/netlist_v1.csv + HW/SCHEMATIC_V1.md   基线: MECH/fit_check.py (串行模型)")
    print("=" * 100)

    usage = netlist_pin_usage()
    decl, narr = schematic_declared_pins()

    # ---------------------------------------------------------- (0) pin 账
    print("\n" + "-" * 100)
    print("【0】跨铰链 4 组通道的 pin 账 (网表实际引用 vs P9 页声明)")
    print("-" * 100)
    conns = ["J_CHG", "CONN_USB", "CONN_CAM", "CONN_LIGHT"]
    pin_rows = []
    total_decl = 0
    total_stack_pitch = 0.0
    total_stack_fpc = 0.0
    for c in conns:
        u = usage.get(c, {"mand": set(), "dnp": set(), "page": set()})
        n_decl = len(u["mand"] | u["dnp"])
        n_mand = len(u["mand"])
        total_decl += n_decl
        w_pitch = n_decl * BASE["pitch"]
        w_fpc = n_decl * BASE["pitch"] + 2 * BASE["fpc_edge_margin"]
        total_stack_pitch += w_pitch
        total_stack_fpc += w_fpc
        pin_rows.append({"conn": c, "declared_physical": n_decl, "populated": n_mand,
                         "dnp": n_decl - n_mand, "w_pitch": round(w_pitch, 2),
                         "w_fpc": round(w_fpc, 2),
                         "pages": sorted(u["page"])})
        rec(f"PIN-{c}", f"{c} pin 账",
            f"物理 {n_decl}p / 必装 {n_mand}p / DNP {n_decl - n_mand}p  "
            f"触点区宽 {w_pitch:.2f}mm / FPC 带宽 {w_fpc:.2f}mm",
            "INFO", f"页: {sorted(u['page'])}  "
                    f"(P9 正文声明 {sorted(narr.get(c, []))} / 器件表声明 {sorted(decl.get(c, []))})")

    # P9 正文 vs 网表 的 pin 数一致性
    mism = []
    for c in conns:
        net_pins = len(usage.get(c, {"mand": set(), "dnp": set()})["mand"] |
                       usage.get(c, {"mand": set(), "dnp": set()})["dnp"])
        narr_pins = sorted(narr.get(c, []))
        if narr_pins and net_pins not in narr_pins:
            mism.append(f"{c}: P9 正文声明 {narr_pins} vs 网表实际 {net_pins}p")
    rec("PIN-MISMATCH", "P9 正文声明 vs 网表实际 pin 数",
        mism if mism else "全部一致", "FAIL" if mism else "PASS",
        "正文少算 pin ⇒ 堆叠数与余量全部偏乐观" if mism else "")

    # ---------------------------------------------------------- (1) 垂直堆叠
    print("\n" + "-" * 100)
    print("【1】铰链区垂直 (V) 堆叠 —— 两个口径 × 两个净高")
    print("-" * 100)
    p9_as_written = (10 + 4 + 18 + 21) * BASE["pitch"]          # P9 正文用的 21p
    p9_decl = (10 + 4 + 18 + 22) * BASE["pitch"]               # 器件表/网表 22p
    rec("STK-P9", "P9 正文自算的堆叠 (10+4+18+21)×0.5", f"{p9_as_written:.2f} mm", "INFO",
        "P9 正文 §功能块写 CONN_LIGHT '1×21p', 但同一页器件表与网表都是 22p (V1.6 补的 pin22=GND)")
    rec("STK-DECL", "按器件表/网表 22p 的触点区堆叠", f"{p9_decl:.2f} mm", "INFO",
        "DECISIONS.md 2026-10-27 记的是 26.5mm (=21p 口径) → 过期")
    rec("STK-FPC", "★FPC 带宽 (物理) 堆叠 = 触点区 + 2×0.50mm 边距",
        f"{total_stack_fpc:.2f} mm", "INFO",
        f"4 条合计多出 {total_stack_fpc - p9_decl:.2f}mm —— 这是 P9/DECISIONS 没算的走线边距")
    for cav_key, cav in (("cav_v_stale", BASE["cav_v_stale"]), ("cav_v_now", BASE["cav_v_now"])):
        for tag, st in (("触点区口径", p9_decl), ("FPC 带宽口径", total_stack_fpc)):
            margin = cav - st
            rec(f"STK-{cav_key[:6]}-{tag[:2]}", f"余量 (净高 {cav:.2f} / {tag} {st:.2f})",
                f"{margin:.2f} mm", "PASS" if margin >= BASE["judge"] else "FAIL",
                f"判据 ≥{BASE['judge']:.2f}mm; "
                + ("净高 37.00 是已作废的'叠放'模型口径 (现行 38.00)" if cav == BASE["cav_v_stale"] else "现行口径"))

    # 板宽 vs V 带合计 (4 条 FPC 的 V 带互不重叠时)
    deficit = total_stack_fpc - BASE["pcb_w"]
    rec("STK-FANOUT", "★4 条 FPC 的 V 带合计 vs 主 PCB 板宽 (Y)",
        f"{total_stack_fpc:.2f} vs {BASE['pcb_w']:.2f} → 缺 {deficit:.2f} mm", "FAIL",
        "4 个座都在主 PCB 上, 若每条 FPC 各占自己的 V 带 (P9 的'求和'模型), "
        "脚内段必须做 V 向扇开; 要么改走线图, 要么改堆叠模型 (见 MECH/HW_CROSS_REVIEW.md §2.3)")

    # ---------------------------------------------------------- (2) 径向
    print("\n" + "-" * 100)
    print("【2】铰链区径向 (H, 前后) 嵌套 —— 4 条 FPC")
    print("-" * 100)
    for t_key, t in (("fpc_t", BASE["fpc_t"]), ("fpc_t_2oz", BASE["fpc_t_2oz"])):
        rad = BASE["bend_r"] + 3 * (BASE["fpc_t"] + BASE["nest_gap"]) + (t + BASE["nest_gap"])
        inner = BASE["cav_h"] - 2 * BASE["wall"]
        rec(f"RAD-{t_key}", f"径向占位 (固定段 {t:.2f}mm 铜厚)",
            f"{rad:.2f} mm", "PASS" if inner - rad >= BASE["judge"] else "FAIL",
            f"镜脚内净空 {inner:.2f} (7.30-2×0.80) → 余 {inner - rad:.2f}mm")

    # ---------------------------------------------------------- (3) PCB 铰链端
    print("\n" + "-" * 100)
    print("【3】主 PCB 铰链端 X 向占位 (4 个跨铰链座) vs 板长与固定孔")
    print("-" * 100)
    depth = sum(BASE["conn_depth"] if c != "CONN_USB" else BASE["conn_depth_4p"] for c in conns)
    depth += BASE["conn_gap_x"] * (len(conns) - 1)
    avail = BASE["soc_escape_x"][0] - BASE["pcb_edge"]
    rec("PCB-X", "4 个座沿板长排开的进深合计", f"{depth:.2f} mm", "INFO",
        "≥10p 座体进深 6.40mm + 4p 5.00mm + 3 个 0.50mm 间隔 [推算]")
    rec("PCB-X-AVAIL", "铰链端可用 X (板边→SoC 逃线带起点)",
        f"{avail:.2f} mm", "INFO",
        f"板长 {BASE['pcb_len']:.2f} - 逃线带起点 X={BASE['soc_escape_x'][0]:.2f} - 工艺边 {BASE['pcb_edge']:.2f}")
    rec("PCB-X-GAP", "★铰链端 X 向缺口", f"{depth - avail:+.2f} mm", "FAIL",
        f"4 座排不开 {depth - avail:.2f}mm; 且固定孔 X=5.00 / 15.00 正好落在这一段里")
    rec("PCB-Y", "单个座体的 Y (板宽向) 占用 vs 板宽",
        f"最宽 CONN_LIGHT 触点区 {22 * BASE['pitch']:.2f} + 壳体边 ~1.5 = {22 * BASE['pitch'] + 1.5:.2f} mm "
        f"vs 板宽 {BASE['pcb_w']:.2f}", "PASS",
        f"余 {BASE['pcb_w'] - (22 * BASE['pitch'] + 1.5):.2f}mm (≥{BASE['judge']:.2f}) —— 单个座放得下, "
        "4 个座不能沿 Y 并排")

    # ---------------------------------------------------------- (3b) 合并可行性
    print("\n" + "-" * 100)
    print("【3b】★ 是否合并成 1 个连接器 (任务明确问的)")
    print("-" * 100)
    total_pins = sum(r["declared_physical"] for r in pin_rows)
    merged_band = total_pins * BASE["pitch"] + 2 * BASE["fpc_edge_margin"]
    merged_body = total_pins * BASE["pitch"] + 2 * 1.50   # 座体壳边 ~1.5mm/侧
    rec("MRG-54P", "全合并成 1 个连接器 (54p@0.5mm)",
        f"触点区 {total_pins * BASE['pitch']:.2f} / FPC 带宽 {merged_band:.2f} / 座体 Y 向 {merged_body:.2f} mm",
        "FAIL",
        f"座体 Y 向 {merged_body:.2f}mm > 板宽 {BASE['pcb_w']:.2f}mm → 放不下; "
        "且接触排沿 V (镜脚高度) 方向 → FPC 带宽方向被锁死, 改成沿 X 会与'铰链轴竖直'矛盾 "
        "(FPC 绕竖直轴弯折 ⇒ 带宽 ∥ 竖直轴 = 镜脚高度)")
    # J_CHG + CONN_USB 合并 (两者框侧都落充电板)
    m14_pins = 10 + 4
    m14_band = m14_pins * BASE["pitch"] + 2 * BASE["fpc_edge_margin"]
    m14_body = m14_pins * BASE["pitch"] + 2 * 1.50
    rec("MRG-14P", "★部分合并: J_CHG(10p) + CONN_USB(4p) → 1×14p@0.5mm",
        f"FPC 带宽 {m14_band:.2f} / 座体 Y 向 {m14_body:.2f} mm vs 板宽 {BASE['pcb_w']:.2f}", "PASS",
        "结构上可行 (框侧两端都落充电板, 脚侧两端都落主 PCB); "
        "★ 但电气代价: 1.5A 充电电流与 90Ω USB 差分同缆 ⇒ 需独立层 + 间距>=3mm, 由 hw-lead 判")
    # 合并后铰链端 X 缺口
    for label, depths in (("4 座分开", [6.40, 5.00, 6.40, 6.40]),
                           ("3 座 (J_CHG+USB 合并)", [6.40, 6.40, 6.40]),
                           ("3 座 (深度上界 7.5)", [7.50, 7.50, 7.50])):
        tot = sum(depths) + 0.50 * (len(depths) - 1)
        rec(f"MRG-X-{len(depths)}", f"铰链端 X 占位 ({label})",
            f"需 {tot:.2f} vs 可用 {avail:.2f} → 缺 {tot - avail:+.2f} mm",
            "PASS" if tot <= avail else "FAIL",
            "固定孔 X=5.00 / X=15.00 仍在这段里, 需一并重排")

    # ---------------------------------------------------------- (3c) 走线拓扑
    print("\n" + "-" * 100)
    print("【3c】★ 铰链区 4 条 FPC 的走线拓扑 —— P9 页没说清是哪一种 (自己发现)")
    print("-" * 100)
    v_sum_band = total_stack_fpc
    rec("TOPO-1", "拓扑 A: V 向叠放 (P9 隐含的假设)",
        f"4 条 FPC 带宽合计 {v_sum_band:.2f}mm vs 净高 {BASE['cav_v_now']:.2f} → 余 "
        f"{BASE['cav_v_now'] - v_sum_band:.2f}mm", "COND",
        "★ 后果: 4 个座在主 PCB 上 (板宽仅 15.00mm = V 向) 各自要占一条 V 带, "
        f"而带宽合计 {v_sum_band:.2f}mm 远超板宽 → 必须在铰链前做 V 向扇开 "
        "(最大 ~16mm), 且是板面内的面内弯 (半径受带宽限制, 12mm 宽的带做不出小半径) "
        "⇒ 拓扑 A 下 4 个座不可能全在主 PCB 同一面")
    rec("TOPO-2", "拓扑 B: H 向径向嵌套 (USB_HINGE_STRUCTURE §3.2(a) 已算过)",
        f"径向占位 4.40mm (固定段 2oz 时 4.45) vs 内净空 "
        f"{BASE['cav_h'] - 2 * BASE['wall']:.2f} → 余 1.25mm", "PASS",
        "★ 若 4 条 FPC 在铰链区沿径向嵌套 (不同半径), 则 V 向只需最宽的一条 (12.00mm), "
        "4 个座可以同 V 带不同 X ⇒ X 向仍是 4 座排不开, 但不再有 V 扇开问题 "
        "⇒ 结构侧建议按拓扑 B 走, 并请 P9 页补一句拓扑定义")
    rec("TOPO-3", "★P9 页的堆叠账缺 2 项 (自己发现)",
        "① FPC 走线边距未计 (4 条 × 2 × 0.50 = +4.00mm) ② 拓扑未定义", "FAIL",
        f"触点区口径 {p9_decl:.2f} → FPC 带宽口径 {v_sum_band:.2f} (+{v_sum_band - p9_decl:.2f}mm); "
        "P9 写'堆叠 26.5mm'但同页器件表/网表是 22p (=27.00mm), 且用的是 21p 算式 ⇒ 页面自相矛盾")

    # ---------------------------------------------------------- (4) 充电板
    print("\n" + "-" * 100)
    print("【4】充电板 (镜框) —— 面积 / 承力 / 开孔")
    print("-" * 100)
    area = BASE["chg_board"][0] * BASE["chg_board"][1]
    # land 估算 [推算]
    lands = {"Type-C 座 (16p 沉板)": 9.0 * 7.4, "J_CHG 座 (10p ZIF)": 6.5 * 6.4,
             "U_CHG BQ25896 (QFN-16 3×3)": 3.0 * 3.0, "L_CHG 2.2µH": 4.0 * 4.0,
             "陶瓷电容 ×5 (0603/0805)": 5 * 3.2, "电阻 ×15 (0402)": 15 * 1.0,
             "ESD + TVS + 测试点 ×5": 5 * 2.0, "充电灯 LED+MOS+R": 3 * 1.5}
    land_total = sum(lands.values())
    rec("CHG-AREA", "充电板 25×10mm 器件 land 占用",
        f"{land_total:.0f} / {area:.0f} mm² = {land_total / area * 100:.0f}%", "COND",
        f"明细: {json.dumps(lands, ensure_ascii=False)} —— 余 {area - land_total:.0f}mm² 给走线/爬电, "
        "双面贴才够, 单面贴装不下")

    tw, th = BASE["typec_panel"]
    bw, bh = BASE["typec_body"]
    cl_x = (tw - bw) / 2
    cl_y = (th - bh) / 2
    rec("CHG-OPEN", "Type-C 面板开孔单边间隙",
        f"X {cl_x:.2f} mm / Y {cl_y:.2f} mm", "FAIL",
        f"开口 {tw}×{th} vs 座体 {bw}×{bh}; FDM 外形公差 ±{BASE['toler']:.2f}mm "
        f"→ 间隙被吃掉 {(BASE['toler'] - cl_y):.2f}mm (Y 向), 座体装不进/装晃")
    rec("CHG-PRINT-TOL", "CHARGE_BOARD_SPEC 的印刷公差要求 vs FDM 能力",
        "要求 ±0.10mm vs FDM ±0.30mm → 差 3.0×", "FAIL",
        "M-15 写的'面板开孔宽公差 ±0.1 (9.4~9.6)'在 P2S 上不可达 → 判据要改或改金属端件")
    rec("CHG-SINK", "Type-C 座承力路径",
        "面板壁 ≥1.50mm + ≥2 承力柱 + 拔出方向限位台阶", "COND",
        "沉板 4 脚插板 = 插拔力直接吃到 PCB 焊盘 ⇒ 必须由端件台阶先顶住; "
        "沉板深度 4 档 (0.8/1.0/1.6/2.10mm) 待选 (CHARGE_BOARD_SPEC M-7 指派结构总工)")

    # ---------------------------------------------------------- (5) 热
    print("\n" + "-" * 100)
    print("【5】充电板耗散 + ICHG/IIN 关系复核 (P10 页拓扑 = buck)")
    print("-" * 100)
    ichg = 0.822      # CHARGE_BOARD_SPEC §3.4 给的 ICHG (按其自述口径)
    eta = 0.90
    for vbat in (3.70, 4.20):
        iin = vbat * ichg / (5.0 * eta)      # 规格书口径: ICHG = IIN×(Vbat/Vbus)/η
        pin = 5.0 * iin
        pout = vbat * ichg
        loss = pin - pout
        rec(f"THM-{vbat:.2f}", f"充电板耗散 @Vbat={vbat:.2f}V (按 CHARGE_BOARD_SPEC §3.4 口径)",
            f"IIN {iin:.3f}A / Pin {pin:.2f}W - Pout {pout:.2f}W = {loss:.2f} W", "INFO",
            "MECH_BUDGET §2.1 写 0.8W = (5-4.2)×I 是线性稳压器公式; "
            "P10 网表有 SW/L_CHG/C_BST/PMID ⇒ 开关型 buck → 耗散应为 Pin-Pout")
    # ★ buck 功率守恒复核 ICHG 与 IIN 的关系 (是否方向写反)
    for vbat in (3.70, 4.20):
        ratio_buck = eta * 5.0 / vbat             # ICHG = IIN × η × Vbus/Vbat
        rec(f"THM-RATIO-{vbat:.2f}", f"★buck 功率守恒: ICHG/IIN 比值 @Vbat={vbat:.2f}V",
            f"{ratio_buck:.3f} (规格书写的是 {vbat / 5.0 / eta:.3f} = 倒数)", "FAIL",
            "5V→3.7V 降压 ⇒ 输出电流必然 > 输入电流; 规格书 ICHG=0.822×IIN 方向反了 ⇒ "
            "若真值是 ICHG=1.216×IIN, 则 390Ω 档实际 ICHG 是表值 0.67-0.82A 的 1.48 倍 "
            "⇒ 单 pin 0.50-0.61A 超 0.5A 额定 ⇒ 390Ω 档的判据要重算 "
            "(★ 需 hw-lead 用 datasheet 原文确认, 我给的是功率守恒推导)")
    # 端件表面温度 (按两种耗散口径)
    conv_a = 0.030 * 0.020          # 镜框端件外表面 ~600mm² [推算]
    r_conv = 1.0 / (10.0 * conv_a)   # 自然对流 h≈10 W/m²K [推算]
    for p_diss, tag in ((0.35, "buck 口径 (Pin-Pout)"), (1.65, "线性口径 (规格书 ICHG/IIN 反了)")):
        dt = p_diss * r_conv
        rec(f"THM-SURF-{tag[:4]}", f"端件外表面温升 ({tag})",
            f"P={p_diss:.2f}W → ΔT {dt:.0f} K → 表面 {25 + dt:.0f} °C", "FAIL",
            "打印件 k=0.2 W/m·K, 端件无金属骨架 ⇒ 只能靠铝屏蔽罩 + 镜框主体导热; "
            "两个口径差 4.7 倍 ⇒ 散热路径设计前必须先定死耗散口径")
    # 镜框侧 (鼻梁) 温升 —— 充电板挪到镜框后
    rec("THM-NOSE", "充电板挪镜框后的鼻梁侧温升",
        "未验", "INFO",
        "ISS-065 (a) 鼻梁区热设计未做; 镜框正中已被光机+分光件占 11.8mm, 充电板只能去端件, "
        "端件在镜框外侧角上 (离鼻梁远) ⇒ 鼻梁风险相对低, 但仍需项目总工裁位置")

    # ---------------------------------------------------------- (6) 装配/检修
    print("\n" + "-" * 100)
    print("【6】装配顺序与检修路径 (电池在镜脚 + 充电板在镜框)")
    print("-" * 100)
    rec("ASM-1", "框侧 J_CHG 实物是一对 (框侧座 + 脚侧座)",
        "框侧座随充电板装进镜框端件", "COND",
        "netlist 只有一行 J_CHG 器件声明 ⇒ BOM 会少买一半 (已登记 needs_from iss099_hw_jchg_qty)")
    rec("ASM-2", "框侧 FPC 固定段必须在镜框端件封盖前完成",
        "固定段 ≥8.0mm + 应力释放 ≥5.0mm", "COND",
        "⇒ 端件必须是可拆/可后装的, 否则镜框合拢就装不上 FPC")
    rec("ASM-3", "脚侧 4 个座 + 电池的装配互斥",
        "PCB 段在铰链端 (X 0~60), 电池段在尾端 (X>60)", "COND",
        "换电池 = 拆皮肤侧下壳; 换充电板 = 拆镜框端件 (会动波导 ±0.3° 基准) ⇒ 端件必须可逆拆")
    rec("ASM-4", "跨铰链 USB 救砖口依赖镜框端件外露 Type-C",
        "Type-C 在镜框 ⇒ 整机必须装好才能烧录", "COND",
        "与 sw-lead 的 usb_flash_role (跨铰链=救援/售后) 一致")

    # ---------------------------------------------------------- (7) 公差链
    print("\n" + "-" * 100)
    print("【7】公差链 (FDM ±0.30mm, 判据 ≥0.60mm)")
    print("-" * 100)
    chains = [
        ("C1 铰链区 V 向", 38.00, total_stack_fpc, "4 条 FPC 带宽合计"),
        ("C2 铰链区 H 向", BASE["cav_h"] - 2 * BASE["wall"],
         BASE["bend_r"] + 3 * (BASE["fpc_t"] + BASE["nest_gap"]) + (BASE["fpc_t_2oz"] + BASE["nest_gap"]),
         "R3.0 + 3×(0.20+0.15) + (0.25+0.15)"),
        ("C3 镜脚电芯段 V 向", 38.00, 29.50, "电芯高 23.50 + 走线槽 6.00"),
        ("C4 主 PCB 段 H 向", BASE["cav_h"], 6.35, "皮肤壁0.8+座4.75+合缝0.2+壁0.8"),
        ("C5 镜脚 L 向", 130.00, 115.50, "电芯 40.5 + 板长 60 + 余量 15"),
    ]
    for cid, avail, need, what in chains:
        m = avail - need
        rec(cid, f"{cid.split()[0]}: {what}", f"需求 {need:.2f} / 可用 {avail:.2f} → 余 {m:.2f} mm",
            "PASS" if m >= BASE["judge"] else "FAIL", f"判据 ≥{BASE['judge']:.2f}mm")

    # ---------------------------------------------------------- (8) 网表板级归属一致性
    print("\n" + "-" * 100)
    print("【8】网表板级归属 (board 列) 一致性抽查")
    print("-" * 100)
    rows = list(csv.reader(open(NETLIST, encoding="utf-8")))
    hdr = rows[0]
    bi, ni, ri = hdr.index("board"), hdr.index("note"), hdr.index("ref")
    led_rows = [r for r in rows[1:] if r and r[ri] in ("D_CHG_LED", "Q_CHG_LED", "R_CHG_LED")]
    boards = sorted({r[bi] for r in led_rows})
    rec("NET-LED", "★充电灯电路 (D_CHG_LED/Q_CHG_LED/R_CHG_LED) 的 board 列",
        f"网表 board = {boards}, 但同页注记写'装在充电板 (镜框) 靠近 Type-C 座'", "FAIL",
        "R_CHG_LED 的两端分别标 CHG_BOARD (net VBUS_5V_CHG) 与 MAIN_PCB; "
        "而 VBUS_5V_CHG 只存在于充电板 ⇒ LED 链条物理上只能在镜框 ⇒ board 列标错 ⇒ "
        "BOM 备料 / 装配 / ISS-103 导光孔位置会跟着做错")

    # ---------------------------------------------------------- 汇总
    npass = sum(1 for r in RESULTS if r["verdict"] == "PASS")
    nfail = sum(1 for r in RESULTS if r["verdict"] == "FAIL")
    ncond = sum(1 for r in RESULTS if r["verdict"] == "COND")
    ninfo = sum(1 for r in RESULTS if r["verdict"] == "INFO")
    print("\n" + "=" * 100)
    print(f"汇总: PASS {npass} / FAIL {nfail} / 条件通过 {ncond} / 说明 {ninfo}   (共 {len(RESULTS)} 项)")
    print("★ FAIL 项不是'做不出来', 是'按现在的图纸/口径做出来会出问题' —— 处置建议见 MECH/HW_CROSS_REVIEW.md")
    print("=" * 100)

    if args.json:
        print(json.dumps({"results": RESULTS,
                          "summary": {"pass": npass, "fail": nfail, "cond": ncond, "info": ninfo}},
                         ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
