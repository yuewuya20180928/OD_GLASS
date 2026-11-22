#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
audit_pcb_geom.py —— ★**独立几何审计** (★不依赖生成器的内存状态, 只读 .kicad_pcb 文本)

★**为什么要有这个 (别再靠 DRC 一家说话)**:
  ★ISS-181 的 5 条 `track_dangling` 根因 = "出脚直道 → 栅格路径"衔接处的**退化图元**:
    ① **零长段** (start == end) ⇒ KiCad 报 dangling
    ② **接不上的短段** (层间过渡段两端没落到过孔上)
  ★**DRC 只报"有 5 条"**, 不会告诉你**哪条网、哪个坐标** ⇒ ⇒ 必须有个能指名道姓的审计器
  ★而且 DRC 归零**不代表几何干净** (例如"删干净了但把整条网删没了" ⇒ DRC 也不报)

判据 (全 0 才算干净):
  A1 零长段 (start == end) = 0
  A2 悬空段 (某个端点只被 1 个图元碰到, 且不在任何焊盘/过孔上) = 0
  A3 异网过孔铜净距不足 (< 0.80mm 中心距 ⇒ 铜间隙 < 0.20mm) = 0
  A4 同网过孔孔到孔不足 (< 0.55mm 中心距) = 0

用法: python3 state/audit_pcb_geom.py [板文件]
退出码: 0 = 干净; 1 = 有问题 (逐条列出)
"""
import math
import os
import re
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
DEFAULT_PCB = os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb")

EPS = 1e-4
# 板规则 (来自 .kicad_pro design_settings.rules)
CLEAR = 0.20            # 铜净距 (netclass 默认)
MIN_HOLE_TO_HOLE = 0.25  # 孔到孔
VIA_DIA = 0.60
VIA_DRILL = 0.30
# ★**异网两过孔的铜净距**: (dia/2 + CLEAR + dia/2)
VIA_COPPER_CENTER = VIA_DIA / 2.0 + CLEAR + VIA_DIA / 2.0      # = 0.80
# ★**同网两过孔的孔到孔**: (drill/2 + MIN_HOLE_TO_HOLE + drill/2)
VIA_HOLE_CENTER = VIA_DRILL / 2.0 + MIN_HOLE_TO_HOLE + VIA_DRILL / 2.0   # = 0.55


def _blocks(txt, marker):
    """扫 s-expression 块: 返回 [(start_idx, block_text), ...]"""
    out = []
    pos = 0
    while True:
        i = txt.find(marker, pos)
        if i < 0:
            break
        # 往回找 '('
        b = txt.rfind("(", 0, i)
        if b < 0:
            break
        depth = 0
        j = b
        while j < len(txt):
            if txt[j] == "(":
                depth += 1
            elif txt[j] == ")":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        out.append((b, txt[b:j + 1]))
        pos = j + 1
    return out


def parse_board(path):
    txt = open(path, encoding="utf-8", errors="ignore").read()
    tracks, vias, pads = [], [], []

    # ---- 过孔 ----
    for _b, blk in _blocks(txt, "(via "):
        ma = re.search(r'\(at ([-\d.]+) ([-\d.]+)\)', blk)
        mn = re.search(r'\(net (?:"([^"]+)"|(\d+))\)', blk)
        mw = re.search(r'\(size ([\d.]+) ([\d.]+)\)', blk)
        md = re.search(r'\(drill ([\d.]+)\)', blk)
        if not (ma and mn):
            continue
        net = mn.group(1) if mn.group(1) else "#" + mn.group(2)
        vias.append({
            "net": net,
            "x": float(ma.group(1)), "y": float(ma.group(2)),
            "dia": float(mw.group(1)) if mw else VIA_DIA,
            "drill": float(md.group(1)) if md else VIA_DRILL,
        })

    # ---- 走线 (segment) ----
    for _b, blk in _blocks(txt, "(segment"):
        ma = re.search(r'\(start ([-\d.]+) ([-\d.]+)\)', blk)
        mb = re.search(r'\(end ([-\d.]+) ([-\d.]+)\)', blk)
        mn = re.search(r'\(net (?:"([^"]+)"|(\d+))\)', blk)
        mw = re.search(r'\(width ([\d.]+)\)', blk)
        ml = re.search(r'\(layer "?([^"\)\s]+)"?\)', blk)
        if not (ma and mb and mn):
            continue
        net = mn.group(1) if mn.group(1) else "#" + mn.group(2)
        tracks.append({
            "net": net,
            "x1": float(ma.group(1)), "y1": float(ma.group(2)),
            "x2": float(mb.group(1)), "y2": float(mb.group(2)),
            "w": float(mw.group(1)) if mw else 0.25,
            "layer": ml.group(1) if ml else "?",
        })

    # ---- 焊盘 (只取矩形中心 + 半径, 用于"端点落在焊盘上"判定) ----
    for _b, blk in _blocks(txt, "(pad "):
        mn = re.search(r'\(net (?:"([^"]+)"|(\d+))\)', blk)
        ma = re.search(r'\(at ([-\d.]+) ([-\d.]+)\)', blk)
        ms = re.search(r'\(size ([\d.]+) ([\d.]+)\)', blk)
        if not (mn and ma):
            continue
        net = mn.group(1) if mn.group(1) else "#" + mn.group(2)
        w = float(ms.group(1)) if ms else 0.5
        h = float(ms.group(2)) if ms else 0.5
        pads.append({"net": net, "x": float(ma.group(1)), "y": float(ma.group(2)),
                     "w": w, "h": h})
    return tracks, vias, pads


def _pt_seg_dist(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    L2 = dx * dx + dy * dy
    if L2 < 1e-12:
        return math.hypot(px - x1, py - y1)
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / L2))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))


def audit(path):
    tracks, vias, pads = parse_board(path)
    print("=" * 72)
    print("  独立几何审计 · audit_pcb_geom  (%s)" % path)
    print("=" * 72)
    print("  图元: 走线 %d 段 / 过孔 %d 个 / 焊盘 %d 个" % (len(tracks), len(vias), len(pads)))

    fails = []

    # ---------- A1 零长段 ----------
    zero = [t for t in tracks
            if abs(t["x1"] - t["x2"]) < EPS and abs(t["y1"] - t["y2"]) < EPS]
    print("  %s A1 零长段 = %d" % ("✅" if not zero else "❌", len(zero)))
    for t in zero[:8]:
        print("       - [%s] %s @ (%.2f, %.2f)" % (t["net"], t["layer"], t["x1"], t["y1"]))
    if zero:
        fails.append("A1 零长段 %d" % len(zero))

    # ---------- 索引: 过孔点 / 焊盘 / 段端点计数 ----------
    via_pts = defaultdict(set)   # (layer-ish, x, y) → {net}
    for v in vias:
        via_pts[(round(v["x"], 4), round(v["y"], 4))].add(v["net"])

    def on_pad(net, x, y):
        for p in pads:
            if p["net"] != net:
                continue
            if (abs(x - p["x"]) <= p["w"] / 2.0 + EPS
                    and abs(y - p["y"]) <= p["h"] / 2.0 + EPS):
                return True
        return False

    ep_cnt = defaultdict(int)
    for t in tracks:
        ep_cnt[(t["net"], t["layer"], round(t["x1"], 4), round(t["y1"], 4))] += 1
        ep_cnt[(t["net"], t["layer"], round(t["x2"], 4), round(t["y2"], 4))] += 1

    # ---------- A2 悬空段 ----------
    dangling = []
    for i, t in enumerate(tracks):
        bad = False
        for (px, py) in ((t["x1"], t["y1"]), (t["x2"], t["y2"])):
            vp = via_pts.get((round(px, 4), round(py, 4)))
            if vp:
                if t["net"] in vp:
                    continue
                bad = True       # 落在别网过孔上 ⇒ 短路风险
                break
            if on_pad(t["net"], px, py):
                continue
            if ep_cnt.get((t["net"], t["layer"], round(px, 4), round(py, 4)), 0) > 1:
                continue
            # T 型接头: 端点落在**同网同层**另一段中段上
            hit = False
            for j, u in enumerate(tracks):
                if j == i or u["net"] != t["net"] or u["layer"] != t["layer"]:
                    continue
                if _pt_seg_dist(px, py, u["x1"], u["y1"], u["x2"], u["y2"]) <= u["w"] / 2.0 + EPS:
                    hit = True
                    break
            if hit:
                continue
            bad = True
            break
        if bad:
            dangling.append(t)
    print("  %s A2 悬空/跨网段 = %d" % ("✅" if not dangling else "❌", len(dangling)))
    for t in dangling[:8]:
        print("       - [%s] %s (%.2f,%.2f)->(%.2f,%.2f)"
              % (t["net"], t["layer"], t["x1"], t["y1"], t["x2"], t["y2"]))
    if dangling:
        fails.append("A2 悬空段 %d" % len(dangling))

    # ---------- A3 异网过孔铜净距 ----------
    copper_bad = []
    for i in range(len(vias)):
        for j in range(i + 1, len(vias)):
            a, b = vias[i], vias[j]
            if a["net"] == b["net"]:
                continue
            d = math.hypot(a["x"] - b["x"], a["y"] - b["y"])
            need = a["dia"] / 2.0 + CLEAR + b["dia"] / 2.0
            if d < need - 1e-6:
                copper_bad.append((round(d, 4), round(need, 4), a["net"], b["net"],
                                   a["x"], a["y"], b["x"], b["y"]))
    print("  %s A3 异网过孔铜净距不足 = %d" % ("✅" if not copper_bad else "❌", len(copper_bad)))
    for c in copper_bad[:8]:
        print("       - 中心距 %.4f < 需 %.4f  [%s](%.2f,%.2f) vs [%s](%.2f,%.2f)"
              % (c[0], c[1], c[2], c[4], c[5], c[3], c[6], c[7]))
    if copper_bad:
        fails.append("A3 异网过孔铜净距 %d" % len(copper_bad))

    # ---------- A4 同网过孔孔到孔 ----------
    hole_bad = []
    for i in range(len(vias)):
        for j in range(i + 1, len(vias)):
            a, b = vias[i], vias[j]
            d = math.hypot(a["x"] - b["x"], a["y"] - b["y"])
            need = a["drill"] / 2.0 + MIN_HOLE_TO_HOLE + b["drill"] / 2.0
            if d < need - 1e-6:
                hole_bad.append((round(d, 4), round(need, 4), a["net"], b["net"],
                                 a["x"], a["y"], b["x"], b["y"]))
    print("  %s A4 同网过孔孔到孔不足 = %d" % ("✅" if not hole_bad else "❌", len(hole_bad)))
    for c in hole_bad[:8]:
        print("       - 中心距 %.4f < 需 %.4f  [%s](%.2f,%.2f) vs [%s](%.2f,%.2f)"
              % (c[0], c[1], c[2], c[4], c[5], c[3], c[6], c[7]))
    if hole_bad:
        fails.append("A4 同网孔到孔 %d" % len(hole_bad))

    print("-" * 72)
    if fails:
        print("❌ 不通过: %s" % "; ".join(fails))
        return 1
    print("✅ 几何干净 (零长/悬空/跨网过孔净距/孔到孔 全 0)")
    return 0


if __name__ == "__main__":
    pcb = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PCB
    if not os.path.exists(pcb):
        print("❌ 板文件不存在: %s" % pcb)
        sys.exit(1)
    sys.exit(audit(pcb))
