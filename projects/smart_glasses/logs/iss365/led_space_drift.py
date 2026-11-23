#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""led_space_drift.py —— ★★【ISS-365】`D_LED_G` 换封装 ⇒ LED 可放行带/原点窗口 漂不漂 ★★

★★★**为什么这条必须单独算** ★★★
  `D_LED_G` 的两条【可放行带】(X 1.550..3.450 / X 72.540..73.660) 与【封装原点窗口】
  (X 6.940..8.250) **不是从板面量出来的** —— 它们由 `MECH/check_board_frame_coords.py`
  的 `led_space()` 从 **`D_LED_G` 的铜箔外框相对封装原点的偏移 `rel`** 算出来
  ⇒ ★**换 land ⇒ `rel` 变 ⇒ 两条带/窗口就变** ⇒ ★**结构侧必须重算, 否则 §3.2 那句
  「led_space 的可落位块数 (1992 / 2016 / 2031 / 2075) 不变」就变成一句没有依据的旧结论** ★

★★**本脚本只读 import 既有闸的 `compute()` ⇒ 口径零漂移; 同一个函数分别喂【真板】与【沙盒换过的板】★★
"""
from __future__ import annotations

import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))
SBX = os.path.join(PROJ, "tmp", "iss365_sbx")


def load_gate(root):
    path = os.path.join(root, "MECH", "check_board_frame_coords.py")
    spec = importlib.util.spec_from_file_location("iss365_cfc_readonly_%s" % abs(hash(root)), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def slim(ls):
    def band(b):
        return {"ox0": round(b["ox0"], 4), "ox1": round(b["ox1"], 4),
                "oy0": round(b["oy0"], 4), "oy1": round(b["oy1"], 4),
                "w": round(b.get("w", 0.0), 4), "h": round(b.get("h", 0.0), 4)}
    return {
        "placeable": [band(b) for b in ls.get("placeable", [])],
        "n_placeable": len(ls.get("placeable", [])),
        "bands": [band(b) for b in ls.get("bands", [])],
        "full_height_bands": [band(b) for b in ls.get("full_height_bands", [])],
        "nearest_band": band(ls["nearest_band"]) if ls.get("nearest_band") else None,
        "nearest_to_r_led_g": [{"origin": [round(x["origin"][0], 4), round(x["origin"][1], 4)],
                                "dist": round(x["dist"], 4)}
                               for x in ls.get("nearest_to_r_led_g", [])][:3],
        "led_rel_bbox": [round(v, 4) for v in (ls.get("led_rel_bbox") or [])],
        "origin_window": [round(v, 4) for v in (ls.get("origin_window") or [])],
        "led_copper": [round(v, 4) for v in (ls.get("led_copper") or [])],
    }


def main():
    out = {}
    for tag, root in (("BEFORE", PROJ), ("AFTER", SBX)):
        if not os.path.isdir(root):
            continue
        g = load_gate(root)
        comp = g.compute(root)
        ls = comp.get("led_space") or {}
        out[tag] = {
            "led_space": slim(ls),
            "sweep": comp.get("led_space_sweep"),
            "led_rel": [round(v, 4) for v in (ls.get("led_rel_bbox") or [])],
            "led_copper": [round(v, 4) for v in ((comp.get("connectors") or {}).get("D_LED_G", {}).get("copper") or [])],
            "led_origin": (comp.get("connectors") or {}).get("D_LED_G", {}).get("origin"),
            "led_gd": comp.get("led_gd"),
        }
        print("[led] %s: led_rel_bbox=%s  n_placeable=%d  净距敏感度 sweep=%s"
              % (tag, out[tag]["led_rel"], out[tag]["led_space"]["n_placeable"],
                 [(s["clearance"], s["n_placeable_bands"]) for s in (comp.get("led_space_sweep") or [])]))
    json.dump(out, open(os.path.join(HERE, "led_space_drift.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    if "BEFORE" in out and "AFTER" in out:
        b, a = out["BEFORE"], out["AFTER"]
        print("[led] rel 漂移: %s -> %s" % (b["led_rel"], a["led_rel"]))
        print("[led] 可落位块数: %d -> %d" % (b["led_space"]["n_placeable"], a["led_space"]["n_placeable"]))
        print("[led] 整高自由带 BEFORE: %s" % b["led_space"]["full_height_bands"])
        print("[led] 整高自由带 AFTER : %s" % a["led_space"]["full_height_bands"])
        for tag in ("BEFORE", "AFTER"):
            print("[led] %s sweep: %s" % (tag, [(s["clearance"], s["n_placeable_bands"],
                                                 s["led_gd_dist"]) for s in out[tag]["sweep"]]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
