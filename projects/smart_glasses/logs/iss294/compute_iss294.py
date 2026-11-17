#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""compute_iss294.py —— ISS-294 · `J_USB_C` 结构边开口规格的几何自算 (★只读★)

只读 import:
  MECH/check_onepass_struct_crosscheck.py  (板解析器 + 只读 CFC)
  MECH/check_board_frame_coords.py        (阈值 CRIT / TOL / OPEN_* 零漂移)
★一个字节都不写板 / 网表 / BOM / 别人的文件★

输出: logs/iss294/compute_iss294.json
"""
from __future__ import annotations

import importlib.util
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))
sys_path = os.path.join(PROJ, "MECH", "check_onepass_struct_crosscheck.py")


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


SC = load("sc_iss294_readonly", sys_path)
CFC = SC.CFC
PCB = os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb")

CRIT = float(CFC.CRIT)                 # 0.60
TOL = float(CFC.TOL["fdm_part"])        # 0.30
OPEN_X = float(CFC.OPEN_X)             # 10.20
OPEN_Y = float(CFC.OPEN_Y)             # 4.60
ALLOW = CRIT + TOL                     # 0.90 结构净距余量
HIERS = [0.90, 2.54, 4.00]

board = SC.Board(PCB)
by = board.by_ref()
fp = by["J_USB_C"]

# ---- 座体 F.Fab (落位后) ----
fab = Board_fab = SC.Board.fab_at(fp, fp["x"], fp["y"])
# ---- 座体 F.CrtYd (落位后) ----
crtyd_pts = []
for poly in fp["crtyd"]:
    crtyd_pts.extend(poly)
crtyd = None
if crtyd_pts:
    # rect 形式: 局部 (x0,y0)..(x1,y1) ⇒ 落位后 (fp 旋转 = 0)
    lx = [p[0] for p in crtyd_pts]
    ly = [p[1] for p in crtyd_pts]
    crtyd = (fp["x"] + min(lx), fp["y"] + min(ly), fp["x"] + max(lx), fp["y"] + max(ly))

# ---- 焊盘 (含 NPTH) ----
pads = []
for (num, x0, y0, x1, y1), p in zip(SC.Board.abs_pad_boxes(fp), fp["pads"]):
    pads.append({"num": num, "type": p["type"], "cx": round((x0 + x1) / 2, 4),
                 "cy": round((y0 + y1) / 2, 4), "w": round(x1 - x0, 4), "h": round(y1 - y0, 4),
                 "x0": round(x0, 4), "y0": round(y0, 4), "x1": round(x1, 4), "y1": round(y1, 4)})

# ---- NPTH 的 drill (★本解析器不读 drill ⇒ 这里按原文块正则补读★) ----
text = open(PCB, encoding="utf-8").read()
blocks = []
i = 0
lines = text.split("\n")
while i < len(lines):
    if lines[i].lstrip().startswith("(footprint"):
        depth, j = 0, i
        while j < len(lines):
            depth += lines[j].count("(") - lines[j].count(")")
            if depth == 0 and j > i:
                break
            j += 1
        blk = "\n".join(lines[i:j + 1])
        if '"J_USB_C"' in blk:
            blocks.append(blk)
        i = j + 1
    else:
        i += 1
blk = blocks[0]
npth = []
for m in re.finditer(r'\(pad "" np_thru_hole circle\s*\n\s*\(at ([-\d.]+) ([-\d.]+)\)\s*\n\s*'
                     r'\(size ([-\d.]+) ([-\d.]+)\)\s*\n\s*\(drill ([-\d.]+)\)', blk):
    lx, ly, sw, sh, dr = (float(m.group(i)) for i in range(1, 6))
    npth.append({"local": (lx, ly), "abs": (fp["x"] + lx, fp["y"] + ly),
                  "pad_size": (sw, sh), "drill": dr})

# ---- 铜箔并集 (ISS-290 §4 口径) ----
cop = [p for p in pads if p["type"] != "np_thru_hole"]
cu_x0 = min(p["x0"] for p in pads); cu_x1 = max(p["x1"] for p in pads)
cu_y0 = min(p["y0"] for p in pads); cu_y1 = max(p["y1"] for p in pads)
sig_x0 = min(p["x0"] for p in cop); sig_x1 = max(p["x1"] for p in cop)
sig_y0 = min(p["y0"] for p in cop); sig_y1 = max(p["y1"] for p in cop)

# ---- 必须清空区 (三口径) ----
# MC-A: 座体 F.Fab
fab_x0, fab_y0, fab_x1, fab_y1 = fab
# MC-B: F.Fab ∪ NPTH pad 外缘 (size 口径) —— 与闸脚本能读到的口径一致
size_x0 = min(fab_x0, min(n["abs"][0] - n["pad_size"][0] / 2 for n in npth))
size_x1 = max(fab_x1, max(n["abs"][0] + n["pad_size"][0] / 2 for n in npth))
size_y0 = min(fab_y0, min(n["abs"][1] - n["pad_size"][1] / 2 for n in npth))
size_y1 = max(fab_y1, max(n["abs"][1] + n["pad_size"][1] / 2 for n in npth))
# MC-C: 物理孔 (drill 口径)
drill_x0 = min(fab_x0, min(n["abs"][0] - n["drill"] / 2 for n in npth))
drill_x1 = max(fab_x1, max(n["abs"][0] + n["drill"] / 2 for n in npth))
drill_y0 = min(fab_y0, min(n["abs"][1] - n["drill"] / 2 for n in npth))
drill_y1 = max(fab_y1, max(n["abs"][1] + n["drill"] / 2 for n in npth))

# ---- 开口 (板边缺口) ----
open_x0 = size_x0 - ALLOW
open_x1 = size_x1 + ALLOW
open_y0 = 0.0                      # ★板边线 (Edge.Cuts 中心线) = 缺口起点★
fab_depth = fab_y1 - fab_y0
open_y1 = open_y0 + max(fab_depth, OPEN_Y) + ALLOW

cl_x = (open_x1 - open_x0 - (size_x1 - size_x0)) / 2.0
cl_y = open_y1 - size_y1

# ---- 立柱 / 螺钉头外扩档 ----
boss_opts = []
for dh in (2.60, 3.00, 3.80):
    ext = (dh - 0.65) / 2.0
    boss_opts.append({"head_or_boss_od": dh, "extra_per_side": round(ext, 4),
                      "open_x": [round(open_x0 - ext, 4), round(open_x1 + ext, 4)],
                      "open_w": round((open_x1 + ext) - (open_x0 - ext), 4)})

# ---- 邻件冲突扫描 (开口矩形内有没有别的件) ----
hits = []
for r, f in by.items():
    if r == "J_USB_C":
        continue
    env = SC.Board.envelope_at(f, f["x"], f["y"])
    if env is None:
        continue
    if SC.rect_overlap(env, (open_x0, open_y0, open_x1, open_y1)) > 1e-9:
        hits.append({"ref": r, "env": [round(v, 4) for v in env]})

# ---- S6 的 20 个目标落位 vs 新开口 ----
calib = SC.read_s6_targets(PROJ)
s6 = []
for t in calib["targets"]:
    f = by.get(t["ref"])
    env = SC.Board.envelope_at(f, float(t["x"]), float(t["y"])) if f else None
    ov = SC.rect_overlap(env, (open_x0, open_y0, open_x1, open_y1)) if env else 0.0
    d = SC.rect_dist(env, (open_x0, open_y0, open_x1, open_y1)) if env else None
    s6.append({"ref": t["ref"], "target": [t["x"], t["y"]], "overlap": round(ov, 6),
               "dist": None if d is None else round(d, 4)})

out = {
    "issue": "ISS-294",
    "agent": "mech-lead",
    "frame": "B160x100",
    "ref": "J_USB_C",
    "footprint_at": [fp["x"], fp["y"]],
    "footprint_rot": fp["rot"],
    "value": fp["value"],
    "fab_abs": [round(v, 4) for v in fab],
    "fab_size": [round(fab_x1 - fab_x0, 4), round(fab_y1 - fab_y0, 4)],
    "crtyd_abs": None if crtyd is None else [round(v, 4) for v in crtyd],
    "crtyd_size": None if crtyd is None else [round(crtyd[2] - crtyd[0], 4),
                                              round(crtyd[3] - crtyd[1], 4)],
    "n_pads": len(pads),
    "pads": pads,
    "npth": [{"abs": [round(n["abs"][0], 4), round(n["abs"][1], 4)],
              "pad_size": list(n["pad_size"]), "drill": n["drill"]} for n in npth],
    "copper_union_all": [round(cu_x0, 4), round(cu_y0, 4), round(cu_x1, 4), round(cu_y1, 4)],
    "copper_union_signal": [round(sig_x0, 4), round(sig_y0, 4), round(sig_x1, 4), round(sig_y1, 4)],
    "mc_fab": [round(fab_x0, 4), round(fab_y0, 4), round(fab_x1, 4), round(fab_y1, 4)],
    "mc_fab_plus_npth_size": [round(size_x0, 4), round(size_y0, 4),
                              round(size_x1, 4), round(size_y1, 4)],
    "mc_fab_plus_npth_drill": [round(drill_x0, 4), round(drill_y0, 4),
                               round(drill_x1, 4), round(drill_y1, 4)],
    "consts": {"CRIT": CRIT, "TOL_fdm_part": TOL, "ALLOW_per_side": round(ALLOW, 4),
               "OPEN_X": OPEN_X, "OPEN_Y": OPEN_Y, "h_tiers": HIERS,
               "open_y_formula": "OPEN_Y_eff(h) = max(4.60, h+1.80)"},
    "open_usbc": {"x0": round(open_x0, 4), "x1": round(open_x1, 4),
                  "y0": round(open_y0, 4), "y1": round(open_y1, 4),
                  "w": round(open_x1 - open_x0, 4), "depth": round(open_y1 - open_y0, 4)},
    "clearance": {"cl_x": round(cl_x, 4), "cl_y": round(cl_y, 4),
                  "worst_cl_x": round(cl_x - TOL, 4), "worst_cl_y": round(cl_y - TOL, 4),
                  "drill_minus_padsize_per_side": round((0.762 - 0.65) / 2.0, 4),
                  "gap_to_drill_edge": round(open_x0 - drill_x0, 4)},
    "boss_options": boss_opts,
    "nearby_component_hits": hits,
    "s6_vs_new_open": s6,
    "evidence": "[实测] 板读 (F.Fab / F.CrtYd / 焊盘 / NPTH drill) + [推算] 净距与开口宽",
}
dst = os.path.join(HERE, "compute_iss294.json")
with open(dst, "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=2)
print(json.dumps(out, ensure_ascii=False, indent=2))
