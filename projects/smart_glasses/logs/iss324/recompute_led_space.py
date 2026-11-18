#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-324 · mech-lead · 独立复算器 (READ-ONLY, 自己写的 s-expr 解析器)

★为什么自己写★: MECH/check_board_frame_coords.py 的 led_space() 是既有受保护脚本 (md5 钉死),
  本单不能改它, 也不能把它的输出当自己的结论抄。本脚本:
  (1) 自己写一个最小 s-expr 解析器, 直接读 HW/PCB/demo_mainboard.kicad_pcb;
  (2) 自己算 Edge.Cuts / 铜箔外框 / LED_G_D 直线距离;
  (3) 自己重跑一遍 "D_LED_G 可放行空间" 的几何推导 (判据与 check_board_frame_coords.py 同口径:
      器件距板边 0.80 + 零重叠 + 开口窗口避让 + 净距 clr 可调);
  (4) 用自己的空间去校验候选落位点, 并算候选点到最近邻器件的铜箔净距;
  (5) 顺带算【真·焊盘到焊盘】网长 (pad-to-pad), 与既有脚本用的【铜箔外框角点代理量】并列给出。

★零写板★: 只 open(..., 'r'), 不写任何文件。
用法: python3 logs/iss324/recompute_led_space.py
"""
import math
import re
import sys

ROOT = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
PCB = ROOT + "/HW/PCB/demo_mainboard.kicad_pcb"

LED_REF = "D_LED_G"
RES_REF = "R_LED_G"
EDGE_KEEPOUT = 0.80      # 器件距板边 (MECH_BUDGET.md §5.1)
OPEN_X, OPEN_Y = 10.20, 4.60   # 检修口开口定档 (SERVICE_PORT_ISS092 §4.1)
BODY_H = 2.54            # 座体高假设 [0数据]
CLR_SWEEP = (0.0, 0.10, 0.20, 0.50)

LED_FAMILY = ("R_LED_G", "R_LED_R", "R_LED_B",
              "D_LED_G", "D_LED_R", "D_LED_B",
              "TP_LED_G", "TP_LED_R", "TP_LED_B")


# ---------------------------------------------------------------- s-expr 解析
TOKEN_RE = re.compile(r'"(?:[^"\\]|\\.)*"|\(|\)|[^\s()]+')


def parse_sexp(text):
    tokens = TOKEN_RE.findall(text)
    pos = 0

    def node():
        nonlocal pos
        tok = tokens[pos]
        pos += 1
        if tok == "(":
            out = []
            while pos < len(tokens) and tokens[pos] != ")":
                out.append(node())
            pos += 1
            return out
        if tok.startswith('"'):
            return tok[1:-1]
        return tok

    root = []
    while pos < len(tokens):
        root.append(node())
    return root


def head(node):
    if isinstance(node, list) and node and isinstance(node[0], str):
        return node[0]
    return None


def children(node, name):
    return [c for c in node if head(c) == name]


def child(node, name):
    c = children(node, name)
    return c[0] if c else None


def fnum(s):
    return float(s)


def rot_apply(dx, dy, deg):
    if not deg:
        return dx, dy
    a = math.radians(deg)
    ca, sa = math.cos(a), math.sin(a)
    # KiCad: 板面 Y 向下; 封装旋转角为逆时针 ⇒ 绝对坐标变换
    return dx * ca + dy * sa, -dx * sa + dy * ca


# ---------------------------------------------------------------- 板读取
def read_board(path):
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()
    root = parse_sexp(text)[0]

    fps = {}
    for fp in children(root, "footprint"):
        at = child(fp, "at")
        ox, oy = fnum(at[1]), fnum(at[2])
        rot = fnum(at[3]) if len(at) > 3 else 0.0
        ref = val = None
        for prop in children(fp, "property"):
            if prop[1] == "Reference":
                ref = prop[2]
            elif prop[1] == "Value":
                val = prop[2]
        pads = []
        for pad in children(fp, "pad"):
            pat = child(pad, "at")
            px, py = fnum(pat[1]), fnum(pat[2])
            # pad 相对封装原点, 且受封装旋转影响
            rx, ry = rot_apply(px, py, rot)
            size = child(pad, "size")
            sx, sy = fnum(size[1]), fnum(size[2])
            netn = child(pad, "net")
            pads.append({
                "num": pad[1],
                "x": ox + rx, "y": oy + ry,
                "sx": sx, "sy": sy,
                "net": netn[1] if netn else "",
            })
        fps[ref] = {"ref": ref, "value": val, "at": (ox, oy), "rot": rot, "pads": pads}

    # Edge.Cuts: gr_line / gr_rect / gr_poly
    xs, ys = [], []
    for g in root:
        h = head(g)
        if h not in ("gr_line", "gr_rect", "gr_poly", "gr_arc", "gr_circle"):
            continue
        lay = child(g, "layer")
        if not lay or lay[1] != "Edge.Cuts":
            continue
        st = child(g, "start")
        en = child(g, "end")
        mg = child(g, "mid")
        for node in (st, en, mg):
            if node:
                xs.append(fnum(node[1]))
                ys.append(fnum(node[2]))
    edge = {"x0": min(xs), "x1": max(xs), "y0": min(ys), "y1": max(ys)}
    return {"fps": fps, "edge": edge, "root": root}


def copper_bbox(fp):
    ps = fp["pads"]
    if not ps:
        return None
    return (min(p["x"] - p["sx"] / 2 for p in ps), max(p["x"] + p["sx"] / 2 for p in ps),
            min(p["y"] - p["sy"] / 2 for p in ps), max(p["y"] + p["sy"] / 2 for p in ps))


def rect_gap(a, b):
    """两矩形 (x0,x1,y0,y1) 之间的最短间隙 (相交则 0)。"""
    dx = max(a[0] - b[1], b[0] - a[1], 0.0)
    dy = max(a[2] - b[3], b[2] - a[3], 0.0)
    return math.hypot(dx, dy)


def opening_rect(fp, body_w):
    """按 check_board_frame_coords.py 同式算开口窗口 (10.20 x 4.60 罩住座体)。"""
    ps = fp["pads"]
    cx = sum(p["x"] for p in ps) / len(ps)
    cy = sum(p["y"] for p in ps) / len(ps)
    bx0, bx1 = cx - body_w / 2, cx + body_w / 2
    by0, by1 = cy - BODY_H / 2, cy + BODY_H / 2
    cl_x = (OPEN_X - body_w) / 2
    cl_y = (OPEN_Y - BODY_H) / 2
    return (bx0 - cl_x, bx1 + cl_x, by0 - cl_y, by1 + cl_y)


# ---------------------------------------------------------------- 可放行空间 (自己推导)
def led_space(board, clr=0.0):
    fps = board["fps"]
    edge = board["edge"]
    led = fps[LED_REF]
    lb = copper_bbox(led)
    lox, loy = led["at"]
    rel = (lb[0] - lox, lb[1] - lox, lb[2] - loy, lb[3] - loy)

    obst = []
    for ref, f in fps.items():
        if ref == LED_REF:
            continue
        b = copper_bbox(f)
        if b:
            obst.append((ref, b))
    obst.append(("OPEN_DEBUG", opening_rect(fps["J_DEBUG"],
                                            copper_bbox(fps["J_DEBUG"])[1]
                                            - copper_bbox(fps["J_DEBUG"])[0])))
    obst.append(("OPEN_UART", opening_rect(fps["J_UART"], 2.54)))

    ox0 = edge["x0"] + EDGE_KEEPOUT - rel[0]
    ox1 = edge["x1"] - EDGE_KEEPOUT - rel[1]
    oy0 = edge["y0"] + EDGE_KEEPOUT - rel[2]
    oy1 = edge["y1"] - EDGE_KEEPOUT - rel[3]

    cuts = sorted({ox0, ox1}
                  | {b[1][0] - clr - rel[1] for b in obst}
                  | {b[1][1] + clr - rel[0] for b in obst})
    bands = []
    for a, b in zip(cuts[:-1], cuts[1:]):
        if b - a <= 1e-9:
            continue
        xc = (a + b) / 2
        if not (ox0 <= xc <= ox1):
            continue
        ys = [(oy0, oy1)]
        for nm, (bx0, bx1, by0, by1) in obst:
            if not (bx0 - clr - rel[1] <= xc <= bx1 + clr - rel[0]):
                continue
            nxt = []
            for (y0, y1) in ys:
                if by1 + clr - rel[2] <= y0 or by0 - clr - rel[3] >= y1:
                    nxt.append((y0, y1))
                    continue
                if by0 - clr - rel[3] > y0:
                    nxt.append((y0, by0 - clr - rel[3]))
                if by1 + clr - rel[2] < y1:
                    nxt.append((by1 + clr - rel[2], y1))
            ys = nxt
        for (y0, y1) in ys:
            if y1 - y0 <= 1e-9:
                continue
            bands.append({"ox0": a, "ox1": b, "oy0": y0, "oy1": y1,
                          "w": b - a, "h": y1 - y0})
    merged = []
    for bd in bands:
        if merged and abs(merged[-1]["ox1"] - bd["ox0"]) < 1e-9 \
                and abs(merged[-1]["oy0"] - bd["oy0"]) < 1e-9 \
                and abs(merged[-1]["oy1"] - bd["oy1"]) < 1e-9:
            merged[-1]["ox1"] = bd["ox1"]
            merged[-1]["w"] = merged[-1]["ox1"] - merged[-1]["ox0"]
        else:
            merged.append(dict(bd))
    full = [b for b in merged
            if abs(b["oy0"] - oy0) < 1e-6 and abs(b["oy1"] - oy1) < 1e-6]
    place = []
    for b in merged:
        px0 = max(b["ox0"], ox0)
        px1 = min(b["ox1"], ox1)
        py0 = max(b["oy0"], oy0)
        py1 = min(b["oy1"], oy1)
        if px1 - px0 > 1e-9 and py1 - py0 > 1e-9:
            place.append({"ox0": px0, "ox1": px1, "oy0": py0, "oy1": py1})
    return {"clearance": clr, "rel": rel, "led_copper": lb, "led_origin": led["at"],
            "origin_window": (ox0, ox1, oy0, oy1), "bands": merged,
            "full_height_bands": full, "placeable": place, "obstacles": obst}


def band_of(sp, px, py):
    for b in sp["placeable"]:
        if b["ox0"] - 1e-9 <= px <= b["ox1"] + 1e-9 and b["oy0"] - 1e-9 <= py <= b["oy1"] + 1e-9:
            return b
    return None


def main():
    board = read_board(PCB)
    fps = board["fps"]
    edge = board["edge"]
    print("=" * 80)
    print("ISS-324 recompute_led_space.py · 自写 s-expr 解析器 · 只读")
    print("=" * 80)
    print("\n[A] Edge.Cuts 板框实读: X %.3f .. %.3f  Y %.3f .. %.3f  ⇒ %.2f x %.2f mm"
          % (edge["x0"], edge["x1"], edge["y0"], edge["y1"],
             edge["x1"] - edge["x0"], edge["y1"] - edge["y0"]))
    print("    ⇒ 现役帧 = B160x100 (160.00 x 100.00 台架板)")

    print("\n[B] LED 族器件自读 (封装原点 / 焊盘绝对坐标 / 器件值)")
    for ref in LED_FAMILY:
        f = fps.get(ref)
        if not f:
            continue
        lb = copper_bbox(f)
        print("  %-9s origin=(%.2f, %.2f) rot=%.1f value=%-12s copper X %.3f..%.3f Y %.3f..%.3f"
              % (ref, f["at"][0], f["at"][1], f["rot"], f["value"],
                 lb[0], lb[1], lb[2], lb[3]))
        for p in sorted(f["pads"], key=lambda d: d["num"]):
            print("        pad%-3s abs=(%.2f, %.2f) size=%.2f x %.2f net=%s"
                  % (p["num"], p["x"], p["y"], p["sx"], p["sy"], p["net"]))

    r2 = [p for p in fps[RES_REF]["pads"] if p["num"] == "2"][0]
    d1 = [p for p in fps[LED_REF]["pads"] if p["num"] == "1"][0]
    dx, dy = d1["x"] - r2["x"], d1["y"] - r2["y"]
    dist = math.hypot(dx, dy)
    print("\n[C] LED_G_D 直线距离独立复算 (pad-to-pad)")
    print("    R_LED_G.2 = (%.2f, %.2f)   D_LED_G.1 = (%.2f, %.2f)"
          % (r2["x"], r2["y"], d1["x"], d1["y"]))
    print("    dx = %.2f  dy = %.2f  ⇒  hypot = %.6f mm  (期望 93.492727, 偏差 %.6f)"
          % (dx, dy, dist, dist - 93.492727))
    print("    X 向占比 %.3f%%  /  Y 向占比 %.3f%%"
          % (abs(dx) / dist * 100, abs(dy) / dist * 100))

    print("\n[D] D_LED_G 可放行空间 (自推导 · 判据: 零重叠 + 器件距板边 %.2f + 开口避让 + clr)" % EDGE_KEEPOUT)
    sweep = []
    for clr in CLR_SWEEP:
        sp = led_space(board, clr)
        full = sp["full_height_bands"]
        # 最近落位原点 (真 pad-to-pad 网长口径)
        best = None
        for b in sp["placeable"]:
            for px in (b["ox0"], b["ox1"], (b["ox0"] + b["ox1"]) / 2):
                for py in (b["oy0"], b["oy1"], (b["oy0"] + b["oy1"]) / 2):
                    pad1 = (px + sp["rel"][0] + 0.30, py + sp["rel"][2] + 0.45)
                    d = math.hypot(pad1[0] - r2["x"], pad1[1] - r2["y"])
                    if best is None or d < best[0]:
                        best = (d, px, py)
        sweep.append((clr, len(sp["placeable"]), len(full), full, best, sp))
        print("    clr %.2f ⇒ 可放行带 %d 条 · 整高带 %d 条 · 最近落位原点 (%.3f, %.3f) "
              "⇒ pad-to-pad 网长 %.3f mm"
              % (clr, len(sp["placeable"]), len(full), best[1], best[2], best[0]))
        for f in full:
            print("            整高带 X %.3f..%.3f (宽 %.3f)  Y %.3f..%.3f"
                  % (f["ox0"], f["ox1"], f["w"], f["oy0"], f["oy1"]))

    # 最近落位带 (最近那块矩形)
    sp0 = sweep[0][5]
    r2x, r2y = r2["x"], r2["y"]
    bestband = None
    for b in sp0["placeable"]:
        cand = min(math.hypot(px + sp0["rel"][0] + 0.30 - r2x, py + sp0["rel"][2] + 0.45 - r2y)
                   for px in (b["ox0"], b["ox1"], (b["ox0"] + b["ox1"]) / 2)
                   for py in (b["oy0"], b["oy1"], (b["oy0"] + b["oy1"]) / 2))
        if bestband is None or cand < bestband[0]:
            bestband = (cand, b)
    print("    ★最近落位带 (封装原点窗口) = X %.3f..%.3f × Y %.3f..%.3f"
          % (bestband[1]["ox0"], bestband[1]["ox1"], bestband[1]["oy0"], bestband[1]["oy1"]))

    print("\n[E] 候选落位点校验 (自算: 落位是否在可放行空间内 / pad 绝对坐标 / "
          "到 R_LED_G.2 的 pad-to-pad 直线长 / 到最近邻器件的铜箔净距)")
    cands = [
        ("C1", 8.250, 63.700, "clr 0.00 最近落位原点 (既有闸口径)"),
        ("C2", 8.050, 63.900, "clr 0.20 最近落位原点 (板内网络类默认 clearance)"),
        ("C3", 8.420, 64.200, "clr 0.50 最近落位原点 (板 zones.min_clearance)"),
        ("C4", 2.500, 60.000, "整高自由带 X 1.550..3.450 内 (假设 B 无光孔口径)"),
        ("C5", 8.250, 66.000, "最近落位带内 Y 偏上 (给光孔留高度余量)"),
    ]
    rel = sp0["rel"]
    for name, ox, oy, why in cands:
        pad1 = (ox + rel[0] + 0.30, oy + rel[2] + 0.45)
        pad2 = (ox + rel[0] + 2.30, oy + rel[2] + 0.45)
        net = math.hypot(pad1[0] - r2x, pad1[1] - r2y)
        # 落位后 D_LED_G 的铜箔外框
        newbox = (ox + rel[0], ox + rel[1], oy + rel[2], oy + rel[3])
        # 到所有其它器件铜箔的净距
        gaps = []
        for ref, f in fps.items():
            if ref == LED_REF:
                continue
            b = copper_bbox(f)
            if b:
                gaps.append((rect_gap(newbox, b), ref))
        gaps.sort()
        inb = band_of(sp0, ox, oy)
        print("    %s 原点 (%.3f, %.3f)  pad1 (%.2f, %.2f)  pad2 (%.2f, %.2f)" %
              (name, ox, oy, pad1[0], pad1[1], pad2[0], pad2[1]))
        print("        依据: %s" % why)
        print("        pad-to-pad 网长 = %.3f mm   (既有闸代理量 = %.3f mm)"
              % (net, math.hypot(ox + rel[0] - r2x, oy + rel[2] - r2y)))
        print("        最近邻器件净距: %s = %.3f mm · 次近 %s = %.3f mm"
              % (gaps[0][1], gaps[0][0], gaps[1][1], gaps[1][0]))
        print("        落在可放行空间内: %s%s"
              % ("是" if inb else "★否★",
                 ("  [带 X %.3f..%.3f × Y %.3f..%.3f]" % (inb["ox0"], inb["ox1"], inb["oy0"], inb["oy1"]))
                 if inb else ""))
        print("        现状对比: 网长 %.6f mm ⇒ 缩短 %.3f mm (%.2f%%)"
              % (dist, dist - net, (dist - net) / dist * 100))

    print("\n[F] 净距敏感度表 (自算, pad-to-pad 口径)")
    for clr, nplace, nfull, full, best, sp in sweep:
        print("    clr %.2f | 可放行带 %4d | 整高带 %d | 最近原点 (%.3f, %.3f) | pad-to-pad %.3f mm | "
              "省 %.3f mm" % (clr, nplace, nfull, best[1], best[2], best[0], dist - best[0]))

    print("\n[END] 独立复算跑完 · 只读 · 未写任何文件")


if __name__ == "__main__":
    sys.exit(main())
