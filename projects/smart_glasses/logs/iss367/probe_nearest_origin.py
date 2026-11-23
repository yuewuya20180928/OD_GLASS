#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-367 · 「最近落位封装原点」逐档实算 (BEFORE / AFTER)
   口径 = MECH/check_board_frame_coords.py 的 led_space() -> nearest_to_r_led_g[0].origin
   ★只读 · 不写板 ★"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(PROJ, "MECH"))
import importlib.util
spec = importlib.util.spec_from_file_location("G", os.path.join(PROJ, "MECH", "check_onepass_s10_led_spec_sync.py"))
G = importlib.util.module_from_spec(spec); spec.loader.exec_module(G)

root = PROJ
cfc = G.load_cfc(root); fp_gate = G.load_fp_gate(root)
board = cfc.read_board(root); comp = cfc.compute(root)
rots = G.board_footprint_rots(root); tmap = G.target_map(root, fp_gate)
patched, used = G.swap_set(board, G.S10_MECH_REFS, tmap, rots)

out = {"swap_n": len(used), "before": [], "after": []}
for clr in G.CLR_LIST:
    sp = cfc.led_space(board, comp, clr=clr)
    n = sp["nearest_to_r_led_g"][0] if sp["nearest_to_r_led_g"] else None
    out["before"].append({"clr": clr, "n": len(sp["placeable"]),
                          "origin": list(n["origin"]) if n else None,
                          "dist": round(n["dist"], 6) if n else None,
                          "band": [round(sp["nearest_band"]["ox0"],4), round(sp["nearest_band"]["ox1"],4),
                                   round(sp["nearest_band"]["oy0"],4), round(sp["nearest_band"]["oy1"],4)] if sp.get("nearest_band") else None})
    sp2 = cfc.led_space(patched, comp, clr=clr)
    n2 = sp2["nearest_to_r_led_g"][0] if sp2["nearest_to_r_led_g"] else None
    out["after"].append({"clr": clr, "n": len(sp2["placeable"]),
                         "origin": list(n2["origin"]) if n2 else None,
                         "dist": round(n2["dist"], 6) if n2 else None,
                         "band": [round(sp2["nearest_band"]["ox0"],4), round(sp2["nearest_band"]["ox1"],4),
                                  round(sp2["nearest_band"]["oy0"],4), round(sp2["nearest_band"]["oy1"],4)] if sp2.get("nearest_band") else None})
print(json.dumps(out, ensure_ascii=False, indent=1))
