#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MECH/hinge_usb_check.py —— ISS-085 跨铰链 USB / 连接器复核 的**机械自检**
=====================================================================
目的: 让"跨铰链链路的几何账算得对不对、连接器 pin 占用统计得对不对"变成可复核的判定,
      而不是"读起来觉得差不多"。

它做三件事:
  ① 从 HW/netlist_v1.csv **解析**每个连接器实际用到的 pin (不靠人肉数)
  ② 用 MECH_BUDGET 已锁死的结构基线 (镜脚净高 37mm / 板宽 12mm / 前后厚 7.0-7.3mm /
     铰链区 ~15mm / FPC 弯折 R≥3.0mm) 算**铰链区几何账**
  ③ 把算出来的数与 MECH/USB_HINGE_STRUCTURE.md 正文里的数**对表**
     (正文写错 → 这里报 FAIL, 防止文档与脚本各说各话)

★ 纪律: 本文所有几何输入都是 [推算] (镜框截面未定义 / 波导未选型 / JBD 未回),
  本脚本只做**算术自洽性**判定, 不代表任何实物已验证。
  ★ 本文 [实测] 条数 = 0 (无样机)。

用法:
    python3 MECH/hinge_usb_check.py            # 人读报告
    python3 MECH/hinge_usb_check.py --json     # 机读

退出码: 0 = 全部自洽 ; 1 = 有不自洽项
=====================================================================
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
DOC = os.path.join(HERE, "USB_HINGE_STRUCTURE.md")

# ---------------------------------------------------------------- 几何基线
# 全部来自 MECH/MECH_BUDGET.md (锁死/已推算值), 每条注明来源章节
GEOM = {
    "temple_h_mm":      (37.0,  "镜脚根部净高 = 电池22 + PCB12 + 走线槽3 (MECH_BUDGET §1.4.2)"),
    "board_w_mm":       (12.0,  "主板板宽 (暂锁 12mm, HW/PCB_FORM_FACTOR_RECHECK §7)"),
    "temple_t_mm":      (7.0,   "镜脚前后厚需求 7.0mm (MECH_BUDGET §1.4.2)"),
    "wall_mm":          (0.8,   "打印件单壁 0.8mm (FDM 最小可靠壁)"),
    "hinge_zone_mm":    (15.0,  "铰链区轴向占位 ~15mm (MECH_BUDGET §1.4.2)"),
    "cavity_len_mm":    (120.0, "镜脚内腔可用长 ~120-125mm (同上)"),
    "bend_R_mm":        (3.0,   "跨铰链 FPC 弯折半径 R≥3.0mm (MECH_BUDGET §1.3 M9)"),
    "fpc_t_mm":         (0.20,  "4 层 0.5mm pitch FPC 成品厚 0.20mm (通用值, [推算])"),
    "fpc_gap_mm":       (0.15,  "FPC 嵌套间隙 0.15mm (装配靠导槽, [推算])"),
    "ffc_pitch_mm":     (0.50,  "跨铰链 FPC 统一 0.5mm pitch (HW/RELIABILITY_DESIGN §(11))"),
    "j_chg_pitch_mm":   (1.27,  "J_CHG 自拟 1.27mm 排线座 (HW/netlist_v1.csv C-02)"),
    "frame_h_mm":       (40.0,  "镜框高度 ~40mm (推算, MECH_BUDGET §1.4.2 根高区间)"),
}

# 跨铰链链路清单: (连接器, 网表里的声明 pin 数, 实际用到 pin 数, 跨铰链?)
# 实际用到 pin 数由 netlist 解析, 不写死
CROSS_LINKS = ["J_CHG", "CONN_USB", "CONN_CAM", "CONN_LIGHT"]

# 建议收敛后的 pin 数 (方案A = 2-lane CSI / 原生 DSI / 无桥)
RECOMMENDED_PINS = {
    "J_CHG":      8,   # SYS×2(载流) + VBUS_DET + BAT_DET + CHG_STAT + PWR_GOOD + GND×2
    "CONN_USB":   4,   # D+ D- GND SHIELD
    "CONN_CAM":  16,   # 2-lane CSI 13 + 3 备用
    "CONN_LIGHT":20,   # 原生 DSI 15 + 5 备用
}

# 网表里没写 pin 数时的**上游规划口径** (来源必须写清, 不许含糊)
DECL_FALLBACK = {
    "CONN_LIGHT": (40, "HW/RELIABILITY_DESIGN.md §(11) 按 40pin 预留; 网表值列只写 "
                        "'板对板/FFC, 待 JBD 确认' → 声明缺失"),
}

# 连接器座体壁厚 (通用值, [推算]) —— 只影响"装得上吗", 不影响铰链区占位
SOCKET_WALL_MM = 1.0


# ---------------------------------------------------------------- netlist 解析
def parse_connector_pins(path: str) -> dict:
    """返回 {ref: {used_pins:set, connector_pins:set, dnp_pins:set}}"""
    out = {k: {"used": set(), "conn": set(), "dnp": set()} for k in
           ("J_CHG", "J_TYPE_C", "CONN_CAM", "CONN_LIGHT", "CONN_USB", "J_DEBUG", "J_UART")}
    pat = re.compile(r"^(J_CHG|J_TYPE_C|CONN_CAM|CONN_LIGHT|CONN_USB|J_DEBUG|J_UART)"
                     r"(?:\s+pin(\d+))?$")
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            for col in ("node1", "node2"):
                v = (row.get(col) or "").strip()
                m = pat.match(v)
                if not m:
                    continue
                ref, pin = m.group(1), m.group(2)
                if pin is None:
                    continue
                p = int(pin)
                out[ref]["conn"].add(p)
                # DNP 判定: 该器件行是 DNP 时, 其 pin 不算"必装占用"
                if (row.get("dnp") or "").strip() == "DNP":
                    out[ref]["dnp"].add(p)
                else:
                    out[ref]["used"].add(p)
    return out


def declared_counts(path: str) -> dict:
    """从连接器器件行的说明里抽 '40p' / '1×6' / '16p' 之类的声明 pin 数"""
    decl = {}
    pat = re.compile(r"(?:(\d+)\s*[×x]\s*(\d+)\s*p?)|(?:(\d+)\s*p\b)")
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            ref = (row.get("ref") or "").strip()
            if ref not in ("J_CHG", "J_TYPE_C", "CONN_CAM", "CONN_LIGHT",
                           "CONN_USB", "J_DEBUG", "J_UART"):
                continue
            if (row.get("type") or "").strip() != "CONN":
                continue
            val = (row.get("value") or "")
            m = pat.search(val)
            n = None
            if m:
                if m.group(1):
                    n = int(m.group(1)) * int(m.group(2))
                else:
                    n = int(m.group(3))
            if n:
                decl[ref] = (n, val)
    return decl


# ---------------------------------------------------------------- 几何计算
def fpc_width_mm(n_pins: int, pitch: float) -> float:
    """FPC/FFC 排线**触点区**宽度 = 触点数 × pitch (忽略两端留边, 偏小值 -> 保守)"""
    return round(n_pins * pitch, 3)


def socket_width_mm(n_pins: int, pitch: float) -> float:
    """连接器**座体**宽度 = 触点区 + 两侧座壁 (座体只出现在刚性 PCB 上, 不进铰链区)"""
    return round(fpc_width_mm(n_pins, pitch) + 2 * SOCKET_WALL_MM, 3)


def hinge_radial_mm(n_links: int, g: dict) -> float:
    """铰链区前后向 (径向) 占位 = R_min + N × (FPC 厚 + 嵌套间隙)"""
    return round(g["bend_R_mm"] + n_links * (g["fpc_t_mm"] + g["fpc_gap_mm"]), 3)


def temple_cavity_throat_mm(g: dict) -> float:
    """镜脚铰链段前后向内净空 = 前后厚 - 前后两道壁"""
    return round(g["temple_t_mm"] - 2 * g["wall_mm"], 3)


# ---------------------------------------------------------------- 长度预算
# 跨铰链走线长度 (mm): 框内段 + 铰链段 + 脚内段  —— 供 EMC D8/D9 用
LENGTH_BUDGET = {
    # 链路: (框内段 min, max), (铰链段 min, max), (脚内段 min, max), 依据
    "CSI (CONN_CAM)": ((70, 80), (7, 9), (25, 55),
                       "摄像头在镜框上沿正中→端件 ~70mm + 铰链弧 4.71+间隙 2-4 + 主 PCB 前端→SoC 25-55"),
    "DSI (CONN_LIGHT)": ((55, 65), (7, 9), (25, 55),
                         "光机在镜框正中→端件 ~60mm + 同上 + 主 PCB 前端→SoC 25-55"),
    "USB (CONN_USB)": ((10, 20), (7, 9), (25, 55),
                       "Type-C 在镜框端件 ~15mm + 同上 + 主 PCB USB 接收端 25-55"),
    "PWR (J_CHG)": ((10, 25), (7, 9), (10, 25),
                    "充电板在镜框端件 ~18mm + 同上 + 主 PCB 前端 10-25"),
}


def length_total(entry):
    (a0, a1), (b0, b1), (c0, c1), _ = entry
    return (a0 + b0 + c0, a1 + b1 + c1)


# ---------------------------------------------------------------- 正文对表
DOC_MUST_CONTAIN = [
    "USB_HINGE_STRUCTURE",
    "跨铰链",
    "ESD",
    "共模扼流",
    "防呆",
]


def doc_check(path: str) -> list:
    problems = []
    if not os.path.exists(path):
        return [f"找不到正文 {path}"]
    txt = open(path, encoding="utf-8").read()
    for kw in DOC_MUST_CONTAIN:
        if kw not in txt:
            problems.append(f"正文缺关键词: {kw}")
    return problems


# ---------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    fails, warns, findings = [], [], []
    if not os.path.exists(NETLIST):
        print(f"[FAIL] 找不到网表 {NETLIST}")
        return 1

    pins = parse_connector_pins(NETLIST)
    decl = declared_counts(NETLIST)
    g = {k: v[0] for k, v in GEOM.items()}

    rep = {"geom": {k: v[0] for k, v in GEOM.items()},
           "geom_src": {k: v[1] for k, v in GEOM.items()},
           "connectors": {}, "hinge": {}, "length": {}}

    print("=" * 78)
    print("MECH/hinge_usb_check.py —— ISS-085 跨铰链 USB / 连接器复核 机械自检")
    print("=" * 78)
    print("\n[0] 几何基线 (全部 [推算], 来源 MECH_BUDGET)")
    for k, v in GEOM.items():
        print(f"    {k:22s} = {v[0]:>7}   {v[1]}")

    # ---- ① 连接器 pin 占用 ----
    print("\n[1] 连接器 pin 占用 (从 HW/netlist_v1.csv 解析)")
    hdr = f"    {'连接器':<12}{'声明':>6}{'用到':>6}{'必装':>6}{'DNP':>6}{'0.5mm宽':>10}{'12mm板宽':>10}"
    print(hdr)
    for ref in ("J_CHG", "J_TYPE_C", "CONN_USB", "CONN_CAM", "CONN_LIGHT", "J_DEBUG", "J_UART"):
        d = pins[ref]
        used, dnp = d["used"], d["dnp"]
        dcount, dval = decl.get(ref, DECL_FALLBACK.get(ref, (None, "")))
        req = sorted(used - dnp)
        pitch = g["j_chg_pitch_mm"] if ref == "J_CHG" else (
            g["ffc_pitch_mm"] if ref in ("CONN_CAM", "CONN_LIGHT", "CONN_USB") else None)
        width = fpc_width_mm(len(req), pitch) if pitch else None
        sock = socket_width_mm(len(req), pitch) if pitch else None
        decl_width = fpc_width_mm(dcount, pitch) if (pitch and dcount) else None
        fit = "-"
        if width is not None:
            fit = "OK" if sock <= g["board_w_mm"] else "放不下"
            if sock > g["board_w_mm"]:
                fails.append(f"{ref}: 座体宽 {sock}mm (触点区 {width}mm) > 主板板宽 "
                             f"{g['board_w_mm']}mm -> 12mm 板放不下这个座")
        print(f"    {ref:<12}{str(dcount or '-'):>6}{len(d['conn']):>6}{len(req):>6}"
              f"{len(dnp):>6}{(f'{width:.1f}' if width else '-'):>10}{fit:>10}")
        rep["connectors"][ref] = {
            "declared": dcount, "used": len(d["conn"]), "required": len(req),
            "dnp": len(dnp), "strip_width_mm": width, "socket_width_mm": sock,
            "declared_strip_width_mm": decl_width,
            "fits_12mm_board": (None if sock is None else sock <= g["board_w_mm"]),
            "decl_value": dval,
        }
        if ref == "J_CHG" and 6 not in d["conn"]:
            findings.append("J_CHG: 器件行声明 pin6=GND, 但网表里 J_CHG pin6 没有任何网表行 "
                            "(信号地在铰链处断开) -> 见正文 §5.2 F-1")
        if ref == "CONN_USB" and len(d["conn"]) < 4:
            findings.append(f"CONN_USB: 声明 4p, 网表只落到 {sorted(d['conn'])} "
                            "(跨铰链 USB 链路在网表上还没展开完整: 需 D+/D−/GND/SHIELD) "
                            "-> 见正文 §5.2 F-2; 注: hw-lead 正在改 netlist (ISS-086), "
                            "本条以'未展开完整'表述, 结论不随快照变")

    # ---- ② 铰链区几何账 ----
    print("\n[2] 铰链区几何账")
    radial = hinge_radial_mm(len(CROSS_LINKS), g)
    throat = temple_cavity_throat_mm(g)
    print(f"    跨铰链链路数 N            = {len(CROSS_LINKS)}  {CROSS_LINKS}")
    print(f"    径向(前后)占位            = R_min {g['bend_R_mm']} + N×(t {g['fpc_t_mm']} "
          f"+ gap {g['fpc_gap_mm']}) = {radial} mm")
    print(f"    镜脚铰链段前后内净空      = {g['temple_t_mm']} - 2×{g['wall_mm']} = {throat} mm")
    margin = round(throat - radial, 3)
    print(f"    余量                      = {throat} - {radial} = {margin} mm")
    if margin < 0:
        fails.append(f"铰链区径向放不下: 需 {radial}mm > 可用 {throat}mm")
    elif margin < 0.5:
        warns.append(f"铰链区径向余量只有 {margin}mm (<0.5mm, 装配公差吃紧)")
    rep["hinge"] = {"n_links": len(CROSS_LINKS), "radial_mm": radial,
                    "throat_mm": throat, "margin_mm": margin}

    # 垂直方向 (高度) 占位: 声明版 vs 收敛版 (只算 FPC 触点区宽度; 座体在刚性 PCB 上)
    decl_stack = sum(fpc_width_mm(rep["connectors"][c]["declared"] or 0, g["ffc_pitch_mm"])
                     for c in ("CONN_CAM", "CONN_LIGHT", "CONN_USB"))
    decl_stack += fpc_width_mm(rep["connectors"]["J_CHG"]["declared"] or 0, g["j_chg_pitch_mm"])
    rec_stack = sum(fpc_width_mm(RECOMMENDED_PINS[c], g["ffc_pitch_mm"])
                    for c in ("CONN_CAM", "CONN_LIGHT", "CONN_USB"))
    rec_stack += fpc_width_mm(RECOMMENDED_PINS["J_CHG"], g["ffc_pitch_mm"])
    print(f"    垂直(高度)占位 声明版     = {decl_stack} mm  "
          f"(40p×2 + 4p + 1×6@1.27) vs 镜脚净高 {g['temple_h_mm']} mm")
    print(f"    垂直(高度)占位 收敛版     = {rec_stack} mm  "
          f"(16p/20p/4p/8p 全 0.5mm) vs 镜脚净高 {g['temple_h_mm']} mm")
    if decl_stack > g["temple_h_mm"]:
        findings.append(f"声明版 4 条链路在铰链区高度方向堆不下: {decl_stack} > "
                        f"{g['temple_h_mm']} mm -> 必须缩 pin, 见正文 §5.2 F-3 / §3.2")
    if rec_stack > g["temple_h_mm"]:
        fails.append(f"收敛版仍放不下: {rec_stack} > {g['temple_h_mm']} mm")
    rep["hinge"]["stack_declared_mm"] = decl_stack
    rep["hinge"]["stack_recommended_mm"] = rec_stack

    # ---- ③ 跨铰链走线长度预算 (EMC D8/D9) ----
    print("\n[3] 跨铰链走线长度预算 (框内段 + 铰链段 + 脚内段) —— 供 EMC D8/D9")
    for name, ent in LENGTH_BUDGET.items():
        lo, hi = length_total(ent)
        print(f"    {name:<20} {ent[0][0]:>3}-{ent[0][1]:<3} + {ent[1][0]:>2}-{ent[1][1]:<2} "
              f"+ {ent[2][0]:>3}-{ent[2][1]:<3} = {lo:>3}-{hi:<3} mm")
        rep["length"][name] = {"frame_mm": ent[0], "hinge_mm": ent[1],
                               "temple_mm": ent[2], "total_mm": [lo, hi], "basis": ent[3]}

    # ---- ④ 正文对表 ----
    print("\n[4] 正文对表 (MECH/USB_HINGE_STRUCTURE.md)")
    probs = doc_check(DOC)
    for p in probs:
        fails.append(p)
    print(f"    关键词检查: {'✅ 全过' if not probs else '❌ ' + str(len(probs)) + ' 项'}")
    if not probs:
        txt = open(DOC, encoding="utf-8").read()
        for tok in (f"{radial}", f"{rec_stack}"):
            if tok not in txt:
                fails.append(f"正文里找不到脚本算出的关键数 {tok} (文档与脚本不一致)")
        print(f"    关键数字一致性: 检查 {radial} / {rec_stack} 出现于正文")
        # 正文必须承接 3 条 finding, 否则"发现问题但没人看见"
        for need in ("F-1", "F-2", "F-3"):
            if need not in txt:
                fails.append(f"正文未承接 finding {need} (脚本发现的问题没进文档)")
        print("    finding 承接: 检查 F-1 / F-2 / F-3 出现于正文")

    # ---- 结论 ----
    print("\n" + "=" * 78)
    if findings:
        print(f"[FIND] {len(findings)} 条 (设计/网表层面的发现, 已写进正文, 不算脚本不自洽)")
        for f in findings:
            print(f"  · {f}")
    if warns:
        print("[WARN]")
        for w in warns:
            print(f"  · {w}")
    if fails:
        print("[FAIL]")
        for f in fails:
            print(f"  · {f}")
        print("\n结论: ❌ 不自洽 (修完再交)")
        if args.json:
            print(json.dumps({"fail": fails, "warn": warns, "finding": findings,
                              "report": rep}, ensure_ascii=False, indent=2, default=str))
        return 1
    print("[FAIL] 0 项")
    print("\n结论: ✅ 算术与文档自洽 (不代表任何实物已验证; 本文 [实测] 条数 = 0)")
    if args.json:
        print(json.dumps({"fail": fails, "warn": warns, "finding": findings,
                          "report": rep}, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
