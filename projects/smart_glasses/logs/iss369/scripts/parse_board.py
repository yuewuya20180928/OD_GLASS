#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-369 · 板面 186 个封装逐件实测 (纯 python 文本解析, 只读, 不写板)

输出 JSON: {"footprints": [ {...}, ... ], "count": N}
每件字段:
  ref, value, lib_id (footprint 节点名), uuid, at, layer,
  pads: [{num, type, shape, at, size, layers, net}],
  pad_count, pad_sizes (去重集合), pad_nets (list of (num,net)),
  fp_lines: N, fp_texts: N, fp_rects: N, fp_circles: N, fp_arcs: N, fp_polys: N,
  layers_used: [..], has_courtyard: bool, has_property_Footprint: bool,
  attr: str|None, embedded_fonts: bool,
  bbox: fab 外框 (fp_line on F.Fab) or None,
  centre_dist: 焊盘中心距 (max pairwise) or None
"""
import json
import re
import sys


def parse_board(path):
    txt = open(path, encoding="utf-8").read()
    lines = txt.splitlines()
    # 找每个 (footprint "..." 顶层块
    starts = []
    for i, ln in enumerate(lines):
        m = re.match(r'^\t\(footprint "(.*)"\s*$', ln)
        if m:
            starts.append((i, m.group(1)))
    out = []
    for idx, (i, fpid) in enumerate(starts):
        end = len(lines)
        for j in range(i + 1, len(lines)):
            if re.match(r'^\t\)\s*$', lines[j]):
                end = j
                break
        blk = lines[i:end + 1]
        body = "\n".join(blk)
        d = {"lib_id": fpid, "line": i + 1}
        # properties
        props = {}
        for pm in re.finditer(r'\(property "([^"]+)" "([^"]*)"', body):
            props[pm.group(1)] = pm.group(2)
        d["ref"] = props.get("Reference", "")
        d["value"] = props.get("Value", "")
        d["has_property_Footprint"] = "Footprint" in props
        d["property_footprint"] = props.get("Footprint", "")
        d["property_datasheet"] = props.get("Datasheet", "")
        am = re.search(r'^\t\t\(at ([-0-9.]+) ([-0-9.]+)(?: ([-0-9.]+))?\)\s*$', body, re.M)
        if am:
            d["at"] = [float(am.group(1)), float(am.group(2)),
                       float(am.group(3)) if am.group(3) else 0.0]
        else:
            d["at"] = None
        lm = re.search(r'^\t\t\(layer "([^"]+)"\)\s*$', body, re.M)
        d["layer"] = lm.group(1) if lm else ""
        # pads
        pads = []
        for pm in re.finditer(
                r'\(pad "([^"]*)" (\S+) (\S+)\s*\n\s*\(at ([-0-9.]+) ([-0-9.]+)(?: ([-0-9.]+))?\)'
                r'\s*\n\s*\(size ([-0-9.]+) ([-0-9.]+)\)\s*\n\s*\(layers ([^)]*)\)(.*?)(?=\n\t\t\)|$)',
                body, re.S):
            num, ptype, shape, x, y, rot, sw, sh, layers, rest = pm.groups()
            netm = re.search(r'\(net (\d+) "([^"]*)"\)', rest)
            pads.append({
                "num": num, "type": ptype, "shape": shape,
                "x": float(x), "y": float(y), "rot": float(rot) if rot else 0.0,
                "w": float(sw), "h": float(sh),
                "layers": re.findall(r'"([^"]+)"', layers),
                "net": netm.group(2) if netm else None,
                "net_num": int(netm.group(1)) if netm else None,
            })
        d["pads"] = pads
        d["pad_count"] = len(pads)
        d["pad_sizes"] = sorted({"%.3fx%.3f" % (p["w"], p["h"]) for p in pads})
        d["pad_nets"] = [[p["num"], p["net"]] for p in pads]
        d["fp_lines"] = len(re.findall(r'\(fp_line\b', body))
        d["fp_texts"] = len(re.findall(r'\(fp_text\b', body))
        d["fp_rects"] = len(re.findall(r'\(fp_rect\b', body))
        d["fp_circles"] = len(re.findall(r'\(fp_circle\b', body))
        d["fp_arcs"] = len(re.findall(r'\(fp_arc\b', body))
        d["fp_polys"] = len(re.findall(r'\(fp_poly\b', body))
        d["layers_used"] = sorted(set(re.findall(r'\(layer "([^"]+)"\)', body)))
        d["has_courtyard"] = any(".CrtYd" in x for x in d["layers_used"])
        am2 = re.search(r'^\t\t\(attr ([^)]*)\)\s*$', body, re.M)
        d["attr"] = am2.group(1).strip() if am2 else None
        d["embedded_fonts"] = "embedded_fonts" in body
        # fab 外框 (F.Fab 上的 fp_line 端点)
        fab = []
        for pm in re.finditer(
                r'\(fp_line\s*\n\s*\(start ([-0-9.]+) ([-0-9.]+)\)\s*\n\s*\(end ([-0-9.]+) ([-0-9.]+)\)'
                r'(?:.|\n)*?\(layer "F\.Fab"\)', body):
            x1, y1, x2, y2 = (float(pm.group(i)) for i in (1, 2, 3, 4))
            fab.append((x1, y1, x2, y2))
        if fab:
            xs = [v for f in fab for v in (f[0], f[2])]
            ys = [v for f in fab for v in (f[1], f[3])]
            d["bbox"] = [round(max(xs) - min(xs), 4), round(max(ys) - min(ys), 4)]
        else:
            d["bbox"] = None
        # 中心距: 焊盘中心两两最大距离 (只在有 >=2 焊盘时)
        if len(pads) >= 2:
            best = 0.0
            for a in range(len(pads)):
                for b in range(a + 1, len(pads)):
                    pa, pb = pads[a], pads[b]
                    dist = ((pa["x"] - pb["x"]) ** 2 + (pa["y"] - pb["y"]) ** 2) ** 0.5
                    best = max(best, dist)
            d["centre_dist"] = round(best, 4)
        else:
            d["centre_dist"] = 0.0
        out.append(d)
    return out


if __name__ == "__main__":
    src = sys.argv[1]
    dst = sys.argv[2]
    fps = parse_board(src)
    json.dump({"count": len(fps), "footprints": fps}, open(dst, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("footprints=%d -> %s" % (len(fps), dst))
