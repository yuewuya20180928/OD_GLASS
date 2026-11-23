#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe_led_spec.py —— ★★【ISS-367 · mech-lead】`D_LED_G` 换官方 0805 ⇒
LED 两条可放行带 / 可落位块数 / 净距敏感度 sweep 的【本单独立实算】 ★★

★★★**为什么本单要自己再算一遍 (不抄 ISS-365)** ★★★
  ISS-365 是【用 pcbnew 在沙盒里真换 land】算出来的 (板副本 md5 每次重存会变) ⇒
  ★**那个数没有一条【不依赖 pcbnew】的复跑路径** ★ ⇒ ★**本单用另一条路复算** ★
  ⇒ ★**本脚本只做两件事: (a) 从本机 KiCad 库里读官方 0805 `.kicad_mod` 的两个焊盘
    (b) 把 `D_LED_G` 的铜箔外框【按官方 land】换掉, 喂给
    `MECH/check_board_frame_coords.py` 自己的 `led_space()`** ★
  ⇒ ★**判据函数一个字节没改 (只读 import) · 真板一个字节没碰** ★

★**为什么这条路径比 pcbnew 沙盒更适合当【闸的判决源】** ★
  ① 不依赖 pcbnew Python 模块 (换台机器 / 换个 KiCad 版本不会炸) ★
  ② 不落板副本 (零写板) ★
  ③ 判据函数与既有闸【逐字同一个函数对象】 ⇒ 口径零漂移 ★

用法:
    python3 logs/iss367/probe_led_spec.py            # 打印 BEFORE / AFTER 四组数
    python3 logs/iss367/probe_led_spec.py --json     # 机器读
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))

LED_REF = "D_LED_G"

# ★**官方 0805 目标封装** ★ (★与 `HW/FP_TRUTH_BASELINE.md` §2 的靶子一致 · ISS-356/ISS-365 同源★)
TARGET_LIB = "LED_SMD:LED_0805_2012Metric"
LIBROOT = "/home/yuewuya/kicad/AppDir/share/kicad/footprints"

CLR_LIST = (0.0, 0.10, 0.20, 0.50)


def load_gate(root):
    path = os.path.join(root, "MECH", "check_board_frame_coords.py")
    spec = importlib.util.spec_from_file_location("iss367_cfc_readonly", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ==================================================================================================
# 官方 0805 `.kicad_mod` 只读解析 (★只取两个焊盘的 (x, y, sx, sy)★)
# ==================================================================================================
PAD_MOD_RE = re.compile(
    r'\(pad\s+"([^"]*)"\s+(\S+)\s+(\S+)\s+\(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)'
    r'(?:\s*\(size ([-\d.]+) ([-\d.]+)\))?')


def read_mod_pads(path):
    text = open(path, "r", encoding="utf-8").read()
    out = []
    for m in PAD_MOD_RE.finditer(text):
        num, ptype, shape, px, py, _rot, sx, sy = m.groups()
        try:
            sx = float(sx) if sx else 0.0
            sy = float(sy) if sy else 0.0
        except (TypeError, ValueError):
            sx = sy = 0.0
        out.append({"num": num, "type": ptype, "shape": shape,
                    "px": float(px), "py": float(py), "sx": sx, "sy": sy})
    return out


def rotate(dx, dy, deg):
    r = math.radians(deg)
    return (dx * math.cos(r) - dy * math.sin(r), dx * math.sin(r) + dy * math.cos(r))


def patch_led_footprint(fp, mod_pads, rot_deg=0.0):
    """★把 `D_LED_G` 的铜箔按官方 land 换掉 (★位置/旋转沿用板上原封装 · 不挪位★) ★"""
    ox, oy = fp["at"]
    pads = []
    for p in mod_pads:
        dx, dy = rotate(p["px"], p["py"], rot_deg)
        sx, sy = p["sx"], p["sy"]
        if abs(rot_deg % 180.0 - 90.0) < 1e-6:
            sx, sy = sy, sx
        pads.append({"num": p["num"], "type": p["type"],
                     "x": ox + dx, "y": oy + dy, "sx": sx, "sy": sy})
    return dict(fp, pads=pads)


def slim(ls):
    def band(b):
        return {"ox0": round(b["ox0"], 4), "ox1": round(b["ox1"], 4),
                "oy0": round(b["oy0"], 4), "oy1": round(b["oy1"], 4),
                "w": round(b.get("w", 0.0), 4), "h": round(b.get("h", 0.0), 4)}
    return {
        "n_placeable": len(ls.get("placeable", [])),
        "full_height_bands": [band(b) for b in ls.get("full_height_bands", [])],
        "origin_window": [round(v, 4) for v in (ls.get("origin_window") or [])],
        "led_rel_bbox": [round(v, 4) for v in (ls.get("led_rel_bbox") or [])],
        "nearest_dist": round(ls["nearest_to_r_led_g"][0]["dist"], 6)
                        if ls.get("nearest_to_r_led_g") else None,
    }


def run(root):
    g = load_gate(root)
    comp = g.compute(root)                       # ★含 openings + BEFORE 的 led_space + BEFORE 的 sweep★
    board = g.read_board(root)
    fp = board["fps"][LED_REF]

    lib, name = TARGET_LIB.split(":", 1)
    mod_path = os.path.join(LIBROOT, "%s.pretty" % lib, "%s.kicad_mod" % name)
    if not os.path.exists(mod_path):
        raise SystemExit("★目标封装 %s 在本机库内找不到: %s★" % (TARGET_LIB, mod_path))
    mod_pads = read_mod_pads(mod_path)

    # ★板上封装旋转角 (★read_board 不解析旋转 ⇒ 这里自己从板文件里读那一行★) ★
    rot = board_footprint_rot(root, LED_REF)

    before = {"led_space": slim(comp["led_space"]),
              "sweep": [(s["clearance"], s["n_placeable_bands"]) for s in comp["led_space_sweep"]]}

    patched = dict(board)
    patched["fps"] = dict(board["fps"])
    patched["fps"][LED_REF] = patch_led_footprint(fp, mod_pads, rot)

    after_space = g.led_space(patched, comp, clr=0.0)
    after_sweep = []
    for clr in CLR_LIST:
        sp = g.led_space(patched, comp, clr=clr)
        near = sp["nearest_to_r_led_g"][0] if sp["nearest_to_r_led_g"] else None
        after_sweep.append({"clearance": clr,
                            "n_placeable_bands": len(sp["placeable"]),
                            "n_full_height": len(sp["full_height_bands"]),
                            "nearest_origin": near["origin"] if near else None,
                            "led_gd_dist": near["dist"] if near else None})
    after = {"led_space": slim(after_space), "sweep": after_sweep}

    return {
        "target_lib": TARGET_LIB,
        "mod_path": mod_path,
        "mod_pads": [{"num": p["num"], "px": p["px"], "py": p["py"],
                      "sx": p["sx"], "sy": p["sy"]} for p in mod_pads],
        "board_rot": rot,
        "led_origin": list(fp["at"]),
        "BEFORE": before,
        "AFTER": after,
    }


FOOTPRINT_RE = re.compile(r'\(footprint[^\n]*\n')


def board_footprint_rot(root, ref):
    """★从板文件里读该封装的 `(at x y [rot])` 的旋转角★"""
    path = os.path.join(root, "HW", "PCB", "demo_mainboard.kicad_pcb")
    text = open(path, "r", encoding="utf-8").read()
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        if lines[i].lstrip().startswith("(footprint"):
            depth, j = 0, i
            while j < len(lines):
                depth += lines[j].count("(") - lines[j].count(")")
                if depth == 0 and j > i:
                    break
                j += 1
            blk = "\n".join(lines[i:j + 1])
            m = re.search(r'\(property "Reference" "%s"' % re.escape(ref), blk)
            if m:
                at = re.search(r'\n\t\t\(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)', blk)
                if at and at.group(3):
                    return float(at.group(3))
                return 0.0
            i = j + 1
        else:
            i += 1
    raise SystemExit("★板上找不到 %s★" % ref)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--root", default=PROJ)
    args = ap.parse_args()
    out = run(args.root)
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=1))
        return 0
    print("★目标封装 = %s (★本机库 .kicad_mod 实读★)" % out["target_lib"])
    print("  焊盘 = %s" % out["mod_pads"])
    print("  板上封装原点 = %s · 旋转 = %s" % (out["led_origin"], out["board_rot"]))
    for tag in ("BEFORE", "AFTER"):
        d = out[tag]
        ls = d["led_space"]
        print("[%s] rel 铜箔包络 = %s" % (tag, ls["led_rel_bbox"]))
        print("[%s] 封装原点窗口 = %s" % (tag, ls["origin_window"]))
        print("[%s] 可落位块数 (clr=0) = %d" % (tag, ls["n_placeable"]))
        for b in ls["full_height_bands"]:
            print("[%s] 整高自由带 = X %.3f..%.3f (宽 %.3f) × Y %.3f..%.3f"
                  % (tag, b["ox0"], b["ox1"], b["w"], b["oy0"], b["oy1"]))
        print("[%s] sweep = %s" % (tag, d["sweep"]))
    b, a = out["BEFORE"], out["AFTER"]
    bs = [s[1] for s in b["sweep"]]
    as_ = [s[1] for s in a["sweep"]]
    print("★块数 Δ = %+d" % (a["led_space"]["n_placeable"] - b["led_space"]["n_placeable"]))
    print("★sweep BEFORE %s → AFTER %s" % (bs, as_))
    mono = all(as_[i] <= as_[i + 1] for i in range(len(as_) - 1))
    print("★AFTER sweep 单调? = %s (★clr=0.5 的 %s vs clr=0.2 的 %s★)"
          % ("是" if mono else "★否·非单调★", as_[3], as_[2]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
