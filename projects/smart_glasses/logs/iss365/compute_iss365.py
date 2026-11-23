#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""compute_iss365.py —— ★★【ISS-365 · mech-lead · S10 换封装对 MECH 侧影响面 · 实算脚本】★★

★**一句话**: ★**把「板只改一次」那一趟 S10 要把 90 件占位 land 换成官方封装这一跳, 对 MECH 侧几何判据的影响【提前算出来】** ★

★★**它算什么 (★全部本机实读 · 零抄任何 agent 报告★)** ★★
  ① ★**90 件集合 = 脚本自己算** ★: 读 `HW/BOM_v1.csv` (靶子口径) + `HW/netlist_v1.csv` (C4 口径) + 读板
     ⇒ 靶内 77 + 缺口 13 = 90
  ② ★**10 个 `R_SEL_*` 是否落在 90 件里** ⇒ 脚本实算交集
  ③ ★**负结论**: 座体类 6 组 ref + 10 个 `TP_DSI_*` 与 90 件的交集 = ∅
  ④ ★**逐件几何**: 现占位 (读板) + 目标封装 (读 `.kicad_mod` 的 fab 外框 / courtyard / 本体 / 焊盘数)
  ⑤ ★**换封装前后**: 落位包络 (F.Fab ∪ 焊盘铜箔) 对 MECH 保留区 (禁入 + 必清空) 的净距与冲突, 逐件重算
  ⑥ ★**S6 专项**: 10 个 `R_SEL_*` 换封装前后净距两列 + Δ + 相邻落位间距

★★**判据阈值零漂移** ★: `CRIT` / `EDGE_KEEPOUT` / 开口矩形 / 必清空区 / SoM 三口径 全部
  ★**只读** `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` 与 `MECH/BOARD_ONEPASS_MECH_SYNC.md` 的机器块 ★
  ⇒ 本单不新造一个数 ★

用法:
    python3 logs/iss365/compute_iss365.py            # ⇒ 落 logs/iss365/compute_iss365.json + 打印摘要
    python3 logs/iss365/compute_iss365.py --json     # 只打印 JSON
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

import pcbparse as P  # noqa: E402  (★本单自写只读解析器★)


def load_coverage_gate(root):
    """★**只读 import** 既有闸 `HW/check_fp_truth_coverage_gap.py` ⇒ C4/靶子/缺口 三集合口径零漂移★

    ★**为什么 import 而不是重写**: C4 (158) 的口径 = 「网表节点串是 bare」的逐条判定,
      里面含 USB-IF 物理脚名白名单 / 伪位号前缀 / bare 节点消歧 ⇒ ★**自己重写必然漂**★
      ⇒ ★**只读 import 既有闸的 `netlist_placeholder` / `iss356_targets` / `coverage_gap` 三函数★**
      ⇒ 本单与 `HW/check_fp_truth_coverage_gap.py` 永远给同一个 77 / 13 / 90★
    """
    path = os.path.join(root, "HW", "check_fp_truth_coverage_gap.py")
    spec = importlib.util.spec_from_file_location("iss365_cov_gate_readonly", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

LIBROOT = "/home/yuewuya/kicad/AppDir/share/kicad/footprints"

PCB_REL = os.path.join("HW", "PCB", "demo_mainboard.kicad_pcb")
BOM_REL = os.path.join("HW", "BOM_v1.csv")
NET_REL = os.path.join("HW", "netlist_v1.csv")
BASE_REL = os.path.join("HW", "FP_TRUTH_BASELINE.md")
GAP_REL = os.path.join("HW", "PCB", "FP_TRUTH_COVERAGE_GAP.md")
XC_REL = os.path.join("MECH", "BOARD_ONEPASS_STRUCT_CROSSCHECK.md")
SYNC_REL = os.path.join("MECH", "BOARD_ONEPASS_MECH_SYNC.md")
CALIB_REL = os.path.join("HW", "PCB", "BOARD_FRAME_CALIBER.md")

MACH_BEGIN = "<!-- MACHINE-BLOCK-BEGIN -->"
MACH_END = "<!-- MACHINE-BLOCK-END -->"

# ★★S6 的 20 个目标落位 = 10 个 R_SEL_* + 10 个 TP_DSI_* (★由 §2 的脚本实算校验★) ★★
R_SEL_REFS = ["R_SEL_D0_N", "R_SEL_D0_P", "R_SEL_D1_N", "R_SEL_D1_P",
              "R_SEL_CK_N", "R_SEL_CK_P", "R_SEL_D2_N", "R_SEL_D2_P",
              "R_SEL_D3_N", "R_SEL_D3_P"]
TP_DSI_REFS = ["TP_DSI_D0_N", "TP_DSI_D0_P", "TP_DSI_D1_N", "TP_DSI_D1_P",
               "TP_DSI_CK_N", "TP_DSI_CK_P", "TP_DSI_D2_N", "TP_DSI_D2_P",
               "TP_DSI_D3_N", "TP_DSI_D3_P"]
# ★座体类 6 组 (★`J_SOM_P1` / `J_SOM_P3` 的 BOM type=NET ⇒ 进不了「必装 ∩ 非 NET/TP」★)
CONNECTOR_REFS = ["J_DEBUG", "J_UART", "J_USB_C", "J_CHG",
                  "J_SOM_P1", "J_SOM_P2", "J_SOM_P3", "J_SOM_P4"]

EVIDENCE_WHITELIST = ("[官网]", "[实测]", "[媒体]", "[推算]", "[0数据]")


# ==================================================================================================
# 读取: 机器块 / BOM / 网表 / 覆盖缺口表
# ==================================================================================================
def read_machine_block(path):
    text = open(path, encoding="utf-8").read()
    b, e = text.find(MACH_BEGIN), text.find(MACH_END)
    if b < 0 or e < 0:
        raise SystemExit(f"[iss365] 缺机器块标记: {path}")
    m = re.search(r"```json\n(.*?)\n```", text[b:e], re.S)
    if not m:
        raise SystemExit(f"[iss365] 机器块不是 ```json 围栏: {path}")
    return json.loads(m.group(1))


def read_fenced_json_named(path, fence_name):
    """★读 `HW/FP_TRUTH_BASELINE.md` 里 ```json <name> 围栏 (带名字的那种)★"""
    text = open(path, encoding="utf-8").read()
    pat = re.compile(r"```json\s+" + re.escape(fence_name) + r"\n(.*?)\n```", re.S)
    m = pat.search(text)
    if not m:
        raise SystemExit(f"[iss365] 找不到 json 围栏 {fence_name}: {path}")
    return json.loads(m.group(1))


def load_bom(path):
    with open(path, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def netlist_placeholder(path, cov):
    """★C4 口径 = 既有闸 `HW/check_fp_truth_coverage_gap.py` 的 `netlist_placeholder` (★只读 import★)★"""
    return cov.netlist_placeholder(path)


def read_gap_table(path):
    """★读 `HW/PCB/FP_TRUTH_COVERAGE_GAP.md` §2 那张表 ⇒ ref → 目标 lib:name★"""
    text = open(path, encoding="utf-8").read()
    out = {}
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 6:
            continue
        m = re.match(r"^`([A-Za-z0-9_]+)`$", cells[0])
        if not m:
            continue
        ref = m.group(1)
        tm = re.search(r"`([A-Za-z0-9_]+):([^`]+)`", cells[5])
        if not tm:
            continue
        out[ref] = {"target_lib": "%s:%s" % (tm.group(1), tm.group(2)),
                    "lib_rel_path": cells[6]}
    return out


# ==================================================================================================
# 几何
# ==================================================================================================
def rect_overlap_area(a, b):
    ox = min(a[2], b[2]) - max(a[0], b[0])
    oy = min(a[3], b[3]) - max(a[1], b[1])
    if ox <= 0 or oy <= 0:
        return 0.0
    return ox * oy


def rect_dist(a, b):
    """★两矩形最小间隙 (重叠 ⇒ 负穿透深度) —— 与既有闸同口径★"""
    dx = max(b[0] - a[2], a[0] - b[2])
    dy = max(b[1] - a[3], a[1] - b[3])
    if dx >= 0 and dy >= 0:
        return max(dx, dy)
    if dx >= 0 or dy >= 0:
        return max(dx, dy)
    ox = min(a[2], b[2]) - max(a[0], b[0])
    oy = min(a[3], b[3]) - max(a[1], b[1])
    return -min(ox, oy)


def rot_pt(x, y, deg):
    r = math.radians(deg)
    c, s = math.cos(r), math.sin(r)
    return (x * c + y * s, -x * s + y * c)


def board_envelope_at(fp, tx, ty):
    """★现占位的落位包络 = F.Fab 外形 ∪ 焊盘铜箔, 平移+旋转到 (tx,ty)★"""
    pts = []
    for p in fp["fab"]:
        dx, dy = rot_pt(p[0], p[1], fp["rot"])
        pts.append((tx + dx, ty + dy))
    for p in fp["pads"]:
        w, h = p["sw"], p["sh"]
        if abs((p["prot"] + fp["rot"]) % 180.0 - 90.0) < 1e-6:
            w, h = h, w
        x0, x1 = p["px"] - w / 2.0, p["px"] + w / 2.0
        y0, y1 = p["py"] - h / 2.0, p["py"] + h / 2.0
        for (lx, ly) in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
            dx, dy = rot_pt(lx, ly, fp["rot"])
            pts.append((tx + dx, ty + dy))
    if not pts:
        return None
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return (min(xs), min(ys), max(xs), max(ys))


def board_fab_at(fp, tx, ty):
    if not fp["fab"]:
        return None
    pts = []
    for p in fp["fab"]:
        dx, dy = rot_pt(p[0], p[1], fp["rot"])
        pts.append((tx + dx, ty + dy))
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return (min(xs), min(ys), max(xs), max(ys))


def mod_envelope_at(mod, tx, ty, rot=0.0):
    """★官方 .kicad_mod 的落位包络 (fab ∪ 铜箔) 放到 (tx,ty)·rot★"""
    pts = []
    for p in mod["pads"]:
        w, h = p["sw"], p["sh"]
        if abs((p["prot"] + rot) % 180.0 - 90.0) < 1e-6:
            w, h = h, w
        x0, x1 = p["px"] - w / 2.0, p["px"] + w / 2.0
        y0, y1 = p["py"] - h / 2.0, p["py"] + h / 2.0
        for (lx, ly) in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
            dx, dy = rot_pt(lx, ly, rot)
            pts.append((tx + dx, ty + dy))
    if mod["fab_bbox"]:
        fb = mod["fab_bbox"]
        for (lx, ly) in ((fb[0], fb[1]), (fb[2], fb[1]), (fb[2], fb[3]), (fb[0], fb[3])):
            dx, dy = rot_pt(lx, ly, rot)
            pts.append((tx + dx, ty + dy))
    if not pts:
        return None
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return (min(xs), min(ys), max(xs), max(ys))


def mod_fab_at(mod, tx, ty, rot=0.0):
    if not mod["fab_bbox"]:
        return None
    fb = mod["fab_bbox"]
    pts = []
    for (lx, ly) in ((fb[0], fb[1]), (fb[2], fb[1]), (fb[2], fb[3]), (fb[0], fb[3])):
        dx, dy = rot_pt(lx, ly, rot)
        pts.append((tx + dx, ty + dy))
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return (min(xs), min(ys), max(xs), max(ys))


def bbox_size(bb):
    if not bb:
        return None
    return [round(bb[2] - bb[0], 4), round(bb[3] - bb[1], 4)]


# ==================================================================================================
# 主计算
# ==================================================================================================
def compute(root=PROJ, libroot=LIBROOT):
    out = {}
    board = P.Board(os.path.join(root, PCB_REL))
    by_ref = board.by_ref

    # ---- ① 90 件集合 (脚本实算) ★
    bom_rows = load_bom(os.path.join(root, BOM_REL))
    cov = load_coverage_gate(root)
    iss356_main, iss356_chg, iss356_total = cov.iss356_targets(bom_rows)
    c4_map = netlist_placeholder(os.path.join(root, NET_REL), cov)
    c4 = set(c4_map)
    in_target = sorted(c4 & set(iss356_total))
    gap = cov.coverage_gap(bom_rows, c4)
    set90 = sorted(set(in_target) | set(gap))
    out["set90"] = {"in_target_total": len(in_target), "gap_total": len(gap),
                    "total": len(set90), "refs": set90,
                    "in_target_refs": in_target, "gap_refs": gap,
                    "c4_total": len(c4), "iss356_total": len(iss356_total),
                    "iss356_main": len(iss356_main)}

    # ---- ② 10 个 R_SEL_* ⊂ 90 件 (脚本实算) ★
    rsel_in90 = sorted(set(R_SEL_REFS) & set(set90))
    out["rsel"] = {"refs": R_SEL_REFS, "in_set90": rsel_in90,
                   "in_set90_count": len(rsel_in90),
                   "not_in_set90": sorted(set(R_SEL_REFS) - set(set90))}

    # ---- ③ 负结论 (脚本实算) ★
    conn_inter = sorted(set(CONNECTOR_REFS) & set(set90))
    tp_inter = sorted(set(TP_DSI_REFS) & set(set90))
    out["neg"] = {"connector_refs": CONNECTOR_REFS, "tp_dsi_refs": TP_DSI_REFS,
                  "connector_intersection": conn_inter, "tp_dsi_intersection": tp_inter,
                  "union_intersection": sorted(set(conn_inter) | set(tp_inter)),
                  "intersection_total": len(set(conn_inter) | set(tp_inter))}

    # ---- 目标 lib:name 映射 ★
    base = read_fenced_json_named(os.path.join(root, BASE_REL), "cal:ISS356_TARGETS") \
        if False else None
    # ISS-356 靶子基准块 (带 BEGIN/END 注释块)
    txt = open(os.path.join(root, BASE_REL), encoding="utf-8").read()
    bb = txt.find("<!-- BEGIN ISS356 封装真值基线基准块 -->")
    ee = txt.find("<!-- END ISS356")
    if bb < 0:
        bb = txt.find("```json")
    if ee < 0:
        ee = txt.find("```", txt.find("```json", bb) + 7)
    seg = txt[bb:ee]
    m = re.search(r"```json\n(.*?)\n```", seg, re.S)
    base_blk = json.loads(m.group(1))
    tgt_map = {}
    for rec in base_blk["records"]:
        tgt_map[rec["ref"]] = {"target_lib": rec["target_lib"],
                               "lib_rel_path": rec["lib_rel_path"],
                               "lib_md5": rec.get("lib_md5", "")}
    for ref, d in read_gap_table(os.path.join(root, GAP_REL)).items():
        tgt_map[ref] = d
    out["target_map_sources"] = {"iss356_block_records": len(base_blk["records"]),
                                 "gap_table_records": len(read_gap_table(os.path.join(root, GAP_REL))),
                                 "merged": len(tgt_map)}

    # ---- MECH 保留区 (只读既有机器块 ⇒ 阈值零漂移) ★
    #   ★三套口径 (★前两套与既有闸逐字同款·第三套是本单的加严口径★) ★
    #   (1) zones_gate = ISS-290 页 `zones[]` 里 type ∈ {禁入, 必清空} ⇒ 11 条
    #       ⇒ **与 `MECH/check_onepass_struct_crosscheck.py` 打印的 `min_clr(全)` 逐字同口径** ★
    #   (2) mc3 = 必清空区 3 条 (ISS-290 页 2 条 + 边开口规格页 h_ref 档 MC_USBC 1 条)
    #       ⇒ **与该闸打印的 `min_clr(必清空)` 逐字同口径** ★
    #   (3) zones_all = (1) ∪ (2) ∪ 边开口规格页的三条开口矩形 ⇒ 18 条 (本单加严口径)
    xc = read_machine_block(os.path.join(root, XC_REL))
    sync = read_machine_block(os.path.join(root, SYNC_REL))
    H_REF = "2.54"
    zones_gate = []
    for z in xc["zones"]:
        if z["type"] not in ("禁入", "必清空"):
            continue
        g = z["geometry"]
        if "x0" in g:
            rect = (g["x0"], g["y0"], g["x1"], g["y1"])
        elif "x" in g:
            rect = (g["x"], g["y"], g["x"] + g["w"], g["y"] + g["h"])
        else:
            continue
        zones_gate.append({"id": z["id"], "type": z["type"], "rect": rect,
                           "source": z["source_iss"]})
    mc3 = []
    for mc in xc["must_clear"]:
        r = mc["rect"]
        mc3.append({"id": mc["id"], "type": "必清空",
                    "rect": (r["x0"], r["y0"], r["x1"], r["y1"]), "source": "ISS-290"})
    for o in sync["openings"]:
        if o.get("id") != "PORT_OPEN_USBC":
            continue
        mc = ((o.get("tiers") or {}).get(H_REF) or {}).get("must_clear")
        if mc:
            mc3.append({"id": "MC_USBC", "type": "必清空",
                        "rect": (mc["x0"], mc["y0"], mc["x1"], mc["y1"]),
                        "source": "ISS-278 h_ref=%s" % H_REF})
    zones_all = list(zones_gate)
    for o in sync["openings"]:
        r = o["rect"]
        zones_all.append({"id": o["id"], "type": "禁入",
                          "rect": (r["x0"], r["y0"], r["x1"], r["y1"]), "source": "ISS-278"})
    zones_all += mc3
    seen, zall = set(), []
    for z in zones_all:
        k = (z["id"], z["rect"])
        if k in seen:
            continue
        seen.add(k)
        zall.append(z)
    zlist = zall
    out["zones_gate"] = [{"id": z["id"], "type": z["type"],
                          "rect": [round(v, 4) for v in z["rect"]], "source": z["source"]}
                         for z in zones_gate]
    out["must_clear3"] = [{"id": z["id"], "rect": [round(v, 4) for v in z["rect"]]}
                          for z in mc3]
    out["zones"] = [{"id": z["id"], "type": z["type"],
                     "rect": [round(v, 4) for v in z["rect"]], "source": z["source"]}
                    for z in zlist]
    crit = xc["consts"]["crit"]
    edge_keepout = xc["consts"]["edge_keepout"]
    out["consts"] = {"crit": crit, "edge_keepout": edge_keepout,
                     "frame": xc["frame_default"], "h_ref": H_REF}
    # LED 可放行带
    led_bands = []
    for z in xc["zones"]:
        if z["id"].startswith("LED-") and z["type"] == "可放行":
            g = z["geometry"]
            led_bands.append((z["id"], (g["x0"], g["y0"], g["x1"], g["y1"])))
    out["led_bands"] = [{"id": b[0], "rect": [round(v, 4) for v in b[1]]} for b in led_bands]

    # ---- S6 目标落位 (只读 CALIBER) ★
    calib = open(os.path.join(root, CALIB_REL), encoding="utf-8").read()
    m = re.search(r"```json cal:S6_TARGETS\n(.*?)\n```", calib, re.S)
    s6 = json.loads(m.group(1))
    s6_pos = {t["ref"]: (t["x"], t["y"]) for t in s6["targets"]}
    out["s6_frame"] = s6["frame"]
    out["s6_target_count"] = len(s6_pos)

    # ---- 逐件几何 + 前后重算 ★
    items = []
    for ref in set90:
        fp = by_ref.get(ref)
        if fp is None:
            items.append({"ref": ref, "board_found": False})
            continue
        tx, ty = s6_pos.get(ref, (fp["x"], fp["y"]))
        moved = (abs(tx - fp["x"]) > 1e-6 or abs(ty - fp["y"]) > 1e-6)
        # 现占位
        ph_fab = board_fab_at(fp, tx, ty)
        ph_env = board_envelope_at(fp, tx, ty)
        ph = {
            "origin": [round(fp["x"], 4), round(fp["y"], 4)],
            "rot": fp["rot"],
            "place_origin": [round(tx, 4), round(ty, 4)],
            "moved_for_s6": moved,
            "fab_size": bbox_size(ph_fab),
            "fab_rect": [round(v, 4) for v in ph_fab] if ph_fab else None,
            "envelope_rect": [round(v, 4) for v in ph_env] if ph_env else None,
            "npads": len(fp["pads"]),
            "pad_sizes": sorted(set((round(p["sw"], 4), round(p["sh"], 4)) for p in fp["pads"])),
            "center_distances": board.center_distances(fp),
        }
        # 目标封装
        tm = tgt_map.get(ref)
        tgt = None
        if tm and tm.get("target_lib"):
            lp = os.path.join(libroot, "%s.pretty" % tm["target_lib"].split(":", 1)[0],
                              "%s.kicad_mod" % tm["target_lib"].split(":", 1)[1])
            if os.path.exists(lp):
                mod = P.parse_kicad_mod(lp)
                t_fab = mod_fab_at(mod, tx, ty, fp["rot"])
                t_env = mod_envelope_at(mod, tx, ty, fp["rot"])
                tgt = {
                    "target_lib": tm["target_lib"],
                    "lib_rel_path": tm["lib_rel_path"],
                    "lib_path": lp,
                    "fab_size": bbox_size(mod["fab_bbox"]),
                    "crtyd_size": bbox_size(mod["crtyd_bbox"]),
                    "npads": mod["npads"],
                    "pad_nums": mod["pad_nums"],
                    "pad_sizes": [[round(a, 4), round(b, 4)] for (a, b) in mod["pad_sizes"]],
                    "center_distances": mod["center_distances"],
                    "fab_rect": [round(v, 4) for v in t_fab] if t_fab else None,
                    "envelope_rect": [round(v, 4) for v in t_env] if t_env else None,
                }
        # 前后净距 / 冲突 (★三套口径: 闸口径 min_clr(全) / 闸口径 min_clr(必清空) / 本单加严 18 区★)
        def probe(env):
            if env is None:
                return {"min_clearance": None, "min_clearance_gate": None,
                        "min_clearance_mc": None, "hits": [], "per_zone": {}}
            per, hits = {}, []
            for z in zlist:
                d = rect_dist(env, z["rect"])
                per[z["id"]] = round(d, 4)
                if d < 0:
                    hits.append({"id": z["id"], "type": z["type"], "depth": round(-d, 4),
                                 "overlap_area": round(rect_overlap_area(env, z["rect"]), 6)})
            pg = {z["id"]: rect_dist(env, z["rect"]) for z in zones_gate}
            pm = {z["id"]: rect_dist(env, z["rect"]) for z in mc3}
            return {"min_clearance": round(min(per.values()), 4) if per else None,
                    "min_clearance_gate": round(min(pg.values()), 4) if pg else None,
                    "min_clearance_mc": round(min(pm.values()), 4) if pm else None,
                    "hits": hits, "per_zone": per}
        before = probe(ph_env)
        after = probe(tgt["envelope_rect"] if tgt else None)
        # LED 带侵占
        def led_hits(env):
            if env is None:
                return []
            return [b[0] for b in led_bands if rect_overlap_area(env, b[1]) > 0]
        # 板边 keep-out
        def edge_ok(env):
            if env is None:
                return None
            return (env[0] >= edge_keepout and env[1] >= edge_keepout
                    and env[2] <= 160.0 - edge_keepout and env[3] <= 100.0 - edge_keepout)
        rec = {
            "ref": ref, "board_found": True, "target_found": bool(tgt),
            "placeholder": ph, "target": tgt,
            "before": before, "after": after,
            "led_hits_before": led_hits(ph_env),
            "led_hits_after": led_hits(tgt["envelope_rect"] if tgt else None),
            "edge_keepout_ok_before": edge_ok(ph_env),
            "edge_keepout_ok_after": edge_ok(tgt["envelope_rect"] if tgt else None),
            "is_s6_target": ref in s6_pos,
            "is_rsel": ref in R_SEL_REFS,
        }
        items.append(rec)
    out["items"] = items

    # ---- S6 专项: 10 个 R_SEL_* 前后净距 + 相邻落位间距 ★
    rsel_rows = []
    rsel_sorted = sorted(R_SEL_REFS, key=lambda r: (s6_pos.get(r, (0, 0))[1], s6_pos.get(r, (0, 0))[0]))
    for i, ref in enumerate(rsel_sorted):
        rec = next(x for x in items if x["ref"] == ref)
        prev_ref = rsel_sorted[i - 1] if i > 0 else None
        next_ref = rsel_sorted[i + 1] if i + 1 < len(rsel_sorted) else None
        prev_rec = next((x for x in items if x["ref"] == prev_ref), None) if prev_ref else None
        next_rec = next((x for x in items if x["ref"] == next_ref), None) if next_ref else None

        def gap_to(other):
            if other is None:
                return None
            a = rec["placeholder"]["envelope_rect"]
            b = other["placeholder"]["envelope_rect"]
            if not a or not b:
                return None
            return round(rect_dist(a, b), 4)

        def gap_to_after(other):
            if other is None:
                return None
            ta = rec["target"]["envelope_rect"] if rec["target"] else None
            tb = other["target"]["envelope_rect"] if other.get("target") else None
            if not ta or not tb:
                return None
            return round(rect_dist(ta, tb), 4)

        row = {
            "ref": ref,
            "target_origin": [round(v, 4) for v in s6_pos.get(ref, (0, 0))],
            "board_origin": rec["placeholder"]["origin"] if rec.get("placeholder") else None,
            "moved": rec["placeholder"]["moved_for_s6"] if rec.get("placeholder") else None,
            "ph_fab_size": rec["placeholder"]["fab_size"] if rec.get("placeholder") else None,
            "ph_center_distances": rec["placeholder"]["center_distances"] if rec.get("placeholder") else None,
            "ph_npads": rec["placeholder"]["npads"] if rec.get("placeholder") else None,
            "tg_fab_size": rec["target"]["fab_size"] if rec.get("target") else None,
            "tg_crtyd_size": rec["target"]["crtyd_size"] if rec.get("target") else None,
            "tg_center_distances": rec["target"]["center_distances"] if rec.get("target") else None,
            "tg_npads": rec["target"]["npads"] if rec.get("target") else None,
            "clearance_before": rec["before"]["min_clearance"],
            "clearance_after": rec["after"]["min_clearance"],
            "clearance_delta": (round(rec["after"]["min_clearance"] - rec["before"]["min_clearance"], 4)
                                if rec["before"]["min_clearance"] is not None
                                and rec["after"]["min_clearance"] is not None else None),
            "clr_gate_before": rec["before"]["min_clearance_gate"],
            "clr_gate_after": rec["after"]["min_clearance_gate"],
            "clr_gate_delta": (round(rec["after"]["min_clearance_gate"] - rec["before"]["min_clearance_gate"], 4)
                               if rec["before"]["min_clearance_gate"] is not None
                               and rec["after"]["min_clearance_gate"] is not None else None),
            "clr_mc_before": rec["before"]["min_clearance_mc"],
            "clr_mc_after": rec["after"]["min_clearance_mc"],
            "clr_mc_delta": (round(rec["after"]["min_clearance_mc"] - rec["before"]["min_clearance_mc"], 4)
                             if rec["before"]["min_clearance_mc"] is not None
                             and rec["after"]["min_clearance_mc"] is not None else None),
            "per_zone_before": rec["before"]["per_zone"],
            "per_zone_after": rec["after"]["per_zone"],
            "hits_before": rec["before"]["hits"],
            "hits_after": rec["after"]["hits"],
            "neighbor_prev": prev_ref, "neighbor_next": next_ref,
            "gap_prev_before": gap_to(prev_rec), "gap_prev_after": gap_to_after(prev_rec),
            "gap_next_before": gap_to(next_rec), "gap_next_after": gap_to_after(next_rec),
        }
        rsel_rows.append(row)
    out["rsel_rows"] = rsel_rows

    # ---- S6 全 20 个目标落位的闸口径复算 (★含 10 个 TP_DSI_*, 它们在 TP 桶 ⇒ 豁免·不换封装★) ★
    s6_all = []
    for t in s6["targets"]:
        ref = t["ref"]
        tx, ty = float(t["x"]), float(t["y"])
        fp = by_ref.get(ref)
        if fp is None:
            continue
        env = board_envelope_at(fp, tx, ty)
        pg = {z["id"]: rect_dist(env, z["rect"]) for z in zones_gate}
        pm = {z["id"]: rect_dist(env, z["rect"]) for z in mc3}
        row = {"ref": ref, "frame": t.get("frame"),
               "target": [tx, ty],
               "board_origin": [round(fp["x"], 4), round(fp["y"], 4)],
               "moved": abs(tx - fp["x"]) > 1e-6 or abs(ty - fp["y"]) > 1e-6,
               "envelope": [round(v, 4) for v in env],
               "clr_gate": round(min(pg.values()), 4),
               "clr_mc": round(min(pm.values()), 4),
               "in_set90": ref in set90,
               "bucket": ("TP" if ref.startswith("TP_") else
                          ("靶内" if ref in in_target else
                           ("缺口" if ref in gap else "其它")))}
        if ref in set90:
            rec = next((x for x in items if x["ref"] == ref), None)
            if rec and rec.get("target"):
                aenv = tuple(rec["target"]["envelope_rect"])
                apg = {z["id"]: rect_dist(aenv, z["rect"]) for z in zones_gate}
                apm = {z["id"]: rect_dist(aenv, z["rect"]) for z in mc3}
                row["clr_gate_after"] = round(min(apg.values()), 4)
                row["clr_mc_after"] = round(min(apm.values()), 4)
                row["clr_gate_delta"] = round(row["clr_gate_after"] - row["clr_gate"], 4)
                row["clr_mc_delta"] = round(row["clr_mc_after"] - row["clr_mc"], 4)
                row["env_after"] = [round(v, 4) for v in aenv]
            else:
                row["clr_gate_after"] = row["clr_gate"]
                row["clr_mc_after"] = row["clr_mc"]
                row["clr_gate_delta"] = 0.0
                row["clr_mc_delta"] = 0.0
        else:
            row["clr_gate_after"] = row["clr_gate"]
            row["clr_mc_after"] = row["clr_mc"]
            row["clr_gate_delta"] = 0.0
            row["clr_mc_delta"] = 0.0
        s6_all.append(row)
    out["s6_rows"] = s6_all
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--out", default=os.path.join(HERE, "compute_iss365.json"))
    args = ap.parse_args()
    res = compute()
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(res, fh, ensure_ascii=False, indent=1)
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=1))
        return 0
    s = res["set90"]
    print("[iss365] 90 件集合: 靶内 %d + 缺口 %d = %d" % (s["in_target_total"], s["gap_total"], s["total"]))
    print("[iss365] 10 个 R_SEL_* 落在 90 件里: %d 个 -> %s" % (res["rsel"]["in_set90_count"], res["rsel"]["in_set90"]))
    print("[iss365] 负结论交集: 座体 %s / TP_DSI %s / 合计 %d"
          % (res["neg"]["connector_intersection"], res["neg"]["tp_dsi_intersection"],
             res["neg"]["intersection_total"]))
    print("[iss365] 保留区条数: %d  LED 带: %d  S6 目标: %d"
          % (len(res["zones"]), len(res["led_bands"]), res["s6_target_count"]))
    print("[iss365] R_SEL 专项:")
    for r in res["rsel_rows"]:
        print("   %-12s 换前净距 %8s  换后净距 %8s  Δ %8s   fab %s -> %s  中心距 %s -> %s  焊盘 %s -> %s"
              % (r["ref"], r["clearance_before"], r["clearance_after"], r["clearance_delta"],
                 r["ph_fab_size"], r["tg_fab_size"], r["ph_center_distances"],
                 r["tg_center_distances"], r["ph_npads"], r["tg_npads"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
