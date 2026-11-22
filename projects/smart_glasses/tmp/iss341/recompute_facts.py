#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-341 · 六条事实的【独立复算】脚本 (与闸脚本 check_board_frame_candidate_compat_gate.py 互为独立实现)

只读。不写板、不写任何文件 (只往 stdout 打印)。

两种实现互不共用代码:
  · 闸脚本  = 流式 s-expr 解析器 (token 级)
  · 本脚本  = 行级正则 + 缩进作用域切分 (逐行扫描, 按 "\n\t(footprint " 切块)
"""
import re
import sys

BOARD = "HW/PCB/demo_mainboard.kicad_pcb"
CALIBER = "HW/PCB/BOARD_FRAME_CALIBER.md"
GEOM = "MECH/BOARD_GEOM_30MM.md"

print("=" * 100)
print("ISS-341 · 六条事实独立复算 (行级正则法 · 与闸的 s-expr 解析法互为独立)")
print("=" * 100)

lines = open(BOARD, encoding="utf-8", errors="replace").read().split("\n")

# ---------------- 事实 1: 板框 Edge.Cuts ----------------
print("\n--- 事实 1: 现役板板框 = 4 条 Edge.Cuts gr_line ---")
edge = []
for i, ln in enumerate(lines):
    if ln.strip() == "(gr_line":
        blk = "\n".join(lines[i:i + 12])
        if '"Edge.Cuts"' in blk:
            s = re.search(r"\(start ([-\d.]+) ([-\d.]+)\)", blk)
            e = re.search(r"\(end ([-\d.]+) ([-\d.]+)\)", blk)
            w = re.search(r"\(width ([-\d.]+)\)", blk)
            if s and e:
                edge.append((float(s.group(1)), float(s.group(2)), float(e.group(1)), float(e.group(2)),
                             float(w.group(1)) if w else 0.0))
for (x1, y1, x2, y2, w) in edge:
    print("  gr_line (%.2f,%.2f) -> (%.2f,%.2f)  width=%.2f" % (x1, y1, x2, y2, w))
if edge:
    xs = [v for (a, b, c, d, w) in edge for v in (a, c)]
    ys = [v for (a, b, c, d, w) in edge for v in (b, d)]
    mw = max(w for (a, b, c, d, w) in edge)
    print("  ⇒ 名义板框 = %.2f × %.2f mm  (含线宽包围盒 %.2f × %.2f)"
          % (max(xs) - min(xs), max(ys) - min(ys), max(xs) - min(xs) + mw, max(ys) - min(ys) + mw))

# ---------------- 事实 2: 铜层 / 板厚 / 封装数 ----------------
print("\n--- 事实 2: 铜层数 / 板厚 / 封装数 ---")
cu = []
in_layers = False
for ln in lines:
    if ln.strip() == "(layers":
        in_layers = True
        continue
    if in_layers:
        m = re.match(r'\s*\(\d+ "([^"]+)"', ln)
        if m:
            nm = m.group(1)
            if nm in ("F.Cu", "B.Cu") or re.match(r"In\d+\.Cu$", nm):
                cu.append(nm)
        if ln.strip() == ")":
            break
print("  铜层 %d 层: %s" % (len(cu), " ".join(cu)))
thk = None
for ln in lines[:40]:
    m = re.search(r"\(thickness ([-\d.]+)\)", ln)
    if m:
        thk = float(m.group(1))
        break
print("  板厚 (general (thickness ...)) = %s mm" % thk)
fps = [i for i, ln in enumerate(lines) if re.match(r"^\t\(footprint ", ln)]
print("  footprint 块数 = %d" % len(fps))
refs = []
for i, ln in enumerate(lines):
    m = re.match(r'\s*\(property "Reference" "([^"]*)"', ln)
    if m:
        refs.append(m.group(1))
print("  distinct Reference = %d  (重复: %s)" % (len(set(refs)), sorted({r for r in refs if refs.count(r) > 1}) or "无"))

# ---------------- 事实 3: 现役帧 ----------------
print("\n--- 事实 3: 现役帧 (cal:FRAMES) ---")
cal = open(CALIBER, encoding="utf-8", errors="replace").read()
m = re.search(r'"current_frame"\s*:\s*"([^"]+)"', cal)
print("  cal:FRAMES.current_frame = %s" % (m.group(1) if m else "?"))
blk = re.search(r"```json\s+cal:FRAMES\s*\n(.*?)\n```", cal, re.S).group(1)
for fid in re.finditer(r'"([A-Za-z0-9_]+)":\s*\{', blk):
    name = fid.group(1)
    if name == "frames":
        continue
    seg = blk[fid.end():]
    w = re.search(r'"width_mm"\s*:\s*([\d.]+)', seg).group(1)
    h = re.search(r'"height_mm"\s*:\s*([\d.]+)', seg).group(1)
    ly = re.search(r'"layers"\s*:\s*(\d+)', seg).group(1)
    tk = re.search(r'"thickness_mm"\s*:\s*([\d.]+)', seg).group(1)
    cur = bool(re.search(r'"current"\s*:\s*true', seg[:600]))
    print("  %-10s %sx%s mm · %s 层 · %s mm · current=%s" % (name, w, h, ly, tk, cur))

# ---------------- 事实 4: J_SOM 承载区 (逐 footprint 作用域切分) ----------------
print("\n--- 事实 4: J_SOM 承载区 bbox (逐封装作用域 · 不跨块) ---")
starts = fps
som_all = None
som_ctr = None
for k, st in enumerate(starts):
    end = starts[k + 1] if k + 1 < len(starts) else len(lines)
    blk = "\n".join(lines[st:end])
    rm = re.search(r'\(property "Reference" "(J_SOM_P\d)"', blk)
    if not rm:
        continue
    ref = rm.group(1)
    am = re.search(r"^\t\t\(at ([-\d.]+) ([-\d.]+)\)", blk, re.M)
    ox, oy = float(am.group(1)), float(am.group(2))
    pads = re.findall(r'\(pad "[^"]*" smd rect\s*\n\s*\(at ([-\d.]+) ([-\d.]+)\)\s*\n\s*\(size ([-\d.]+) ([-\d.]+)\)', blk)
    xs = []
    ys = []
    cxs = []
    cys = []
    for (px, py, w, h) in pads:
        px, py, w, h = float(px), float(py), float(w), float(h)
        ax, ay = ox + px, oy + py
        xs.append((ax - w / 2, ax + w / 2))
        ys.append((ay - h / 2, ay + h / 2))
        cxs.append(ax)
        cys.append(ay)
    print("  %-9s at=(%g,%g) pads=%3d  外形并集 x %.2f..%.2f / y %.2f..%.2f  中心并集 x %.2f..%.2f / y %.2f..%.2f"
          % (ref, ox, oy, len(pads),
             min(a for a, b in xs), max(b for a, b in xs), min(a for a, b in ys), max(b for a, b in ys),
             min(cxs), max(cxs), min(cys), max(cys)))
    xs2 = [v for t in xs for v in t]
    ys2 = [v for t in ys for v in t]
    cxs2 = list(cxs)
    cys2 = list(cys)
    box = (min(xs2), min(ys2), max(xs2), max(ys2))
    som_all = box if som_all is None else (min(som_all[0], box[0]), min(som_all[1], box[1]),
                                          max(som_all[2], box[2]), max(som_all[3], box[3]))
    cbox = (min(cxs2), min(cys2), max(cxs2), max(cys2))
    som_ctr = cbox if som_ctr is None else (min(som_ctr[0], cbox[0]), min(som_ctr[1], cbox[1]),
                                            max(som_ctr[2], cbox[2]), max(som_ctr[3], cbox[3]))
print("  ⇒ 四座并集 (焊盘实体) : %.2f × %.2f mm  (x %.2f..%.2f / y %.2f..%.2f)"
      % (som_all[2] - som_all[0], som_all[3] - som_all[1], som_all[0], som_all[2], som_all[1], som_all[3]))
print("  ⇒ 四座并集 (焊盘中心) : %.2f × %.2f mm  (x %.2f..%.2f / y %.2f..%.2f)"
      % (som_ctr[2] - som_ctr[0], som_ctr[3] - som_ctr[1], som_ctr[0], som_ctr[2], som_ctr[1], som_ctr[3]))

# ---------------- 事实 4b: 全板占位并集 ----------------
print("\n--- 事实 4b: 全板 186 封装占位并集 (焊盘实体) ---")
allb = None
for k, st in enumerate(starts):
    end = starts[k + 1] if k + 1 < len(starts) else len(lines)
    blk = "\n".join(lines[st:end])
    am = re.search(r"^\t\t\(at ([-\d.]+) ([-\d.]+)\)", blk, re.M)
    if not am:
        continue
    ox, oy = float(am.group(1)), float(am.group(2))
    pads = re.findall(r'\(pad "[^"]*" smd rect\s*\n\s*\(at ([-\d.]+) ([-\d.]+)\)\s*\n\s*\(size ([-\d.]+) ([-\d.]+)\)', blk)
    for (px, py, w, h) in pads:
        px, py, w, h = float(px), float(py), float(w), float(h)
        ax, ay = ox + px, oy + py
        b = (ax - w / 2, ay - h / 2, ax + w / 2, ay + h / 2)
        allb = b if allb is None else (min(allb[0], b[0]), min(allb[1], b[1]), max(allb[2], b[2]), max(allb[3], b[3]))
print("  ⇒ 占位并集 = %.2f × %.2f mm  (x %.2f..%.2f / y %.2f..%.2f)"
      % (allb[2] - allb[0], allb[3] - allb[1], allb[0], allb[2], allb[1], allb[3]))

# ---------------- 事实 5: 算术 ----------------
print("\n--- 事实 5: 承载区高 vs 候选板高 (算术) ---")
for fh in (30.0, 15.0):
    print("  焊盘实体 46.78 - %4.1f = %+.2f mm   |   焊盘中心 46.08 - %4.1f = %+.2f mm"
          % (fh, 46.78 - fh, fh, 46.08 - fh))
for label, fw, fh2 in (("F30A", 60.0, 30.0), ("P60x15", 60.0, 15.0)):
    print("  %s  原位外溢 (框原点钉在 0,0): 占位并集 X+%.2f/Y+%.2f  ·  承载区 X+%.2f/Y+%.2f"
          % (label, allb[2] - fw, allb[3] - fh2, som_all[2] - fw, som_all[3] - fh2))

# ---------------- 事实 6: 结构侧口径 ----------------
print("\n--- 事实 6: 结构侧权威表口径 (MECH/BOARD_GEOM_30MM.md) ---")
gt = open(GEOM, encoding="utf-8", errors="replace").read()
print("  RK3576 命中 %d 次 / RK3572 命中 %d 次" % (len(re.findall(r"RK3576", gt)), len(re.findall(r"RK3572", gt))))
for ln in gt.split("\n"):
    if re.search(r"板长 X|板宽 Y|^\| 板厚 |主控 ", ln):
        print("  %s" % ln.strip())
print("=" * 100)
sys.exit(0)
