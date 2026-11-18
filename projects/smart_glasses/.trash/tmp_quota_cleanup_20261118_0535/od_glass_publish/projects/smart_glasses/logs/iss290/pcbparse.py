#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-290 · 只读 KiCad s-expr 板解析器 (mech-lead)

只读 `HW/PCB/demo_mainboard.kicad_pcb`, 抽出:
  - Edge.Cuts 几何 (线/弧/圆) => 板框 + 圆角口径
  - 每个 footprint: Reference / Value / at(x,y,rot) / pads(number, at, size) /
                    F.Fab 图形 / F.CrtYd 图形
  - 绝对坐标 (含封装旋转)

★零写板 · 零落表 · 零改 HW/ ★
"""
import math
import re

BOARD = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses/HW/PCB/demo_mainboard.kicad_pcb"


# ---------------------------------------------------------------- tokenizer
def tokenize(text):
    i, n = 0, len(text)
    toks = []
    while i < n:
        c = text[i]
        if c in "()":
            toks.append(c)
            i += 1
        elif c.isspace():
            i += 1
        elif c == '"':
            j = i + 1
            buf = []
            while j < n:
                if text[j] == "\\" and j + 1 < n:
                    buf.append(text[j + 1])
                    j += 2
                    continue
                if text[j] == '"':
                    break
                buf.append(text[j])
                j += 1
            toks.append(("str", "".join(buf)))
            i = j + 1
        else:
            j = i
            while j < n and not text[j].isspace() and text[j] not in "()":
                j += 1
            toks.append(("atom", text[i:j]))
            i = j
    return toks


def parse(text):
    toks = tokenize(text)
    pos = 0

    def parse_node():
        nonlocal pos
        t = toks[pos]
        if t == "(":
            pos += 1
            node = []
            while pos < len(toks) and toks[pos] != ")":
                node.append(parse_node())
            pos += 1
            return node
        else:
            pos += 1
            return t

    root = parse_node()
    # root = [(kicad_pcb ...)] => 取 kicad_pcb 的子节点表
    if (isinstance(root, list) and len(root) == 1 and isinstance(root[0], list)
            and root[0] and root[0][0] == "kicad_pcb"):
        return root[0]
    return root


def nname(node):
    if isinstance(node, list) and node and isinstance(node[0], tuple):
        return node[0][1]
    if isinstance(node, list) and node:
        return node[0]
    return None


def kids(node, name):
    return [c for c in node if isinstance(c, list) and nname(c) == name]


def kid(node, name):
    k = kids(node, name)
    return k[0] if k else None


def val(node, idx=1, default=None):
    if isinstance(node, list) and len(node) > idx:
        v = node[idx]
        if isinstance(v, tuple):
            return v[1]
        return v
    return default


def fv(node, idx=1, default=None):
    v = val(node, idx, default)
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


# ---------------------------------------------------------------- geometry
def rot_xy(x, y, deg):
    """KiCad 封装旋转: 正角 = 屏幕逆时针 (Y 向下 ⇒ 矩阵带 Y 取负)。"""
    r = math.radians(deg)
    c, s = math.cos(r), math.sin(r)
    return (x * c + y * s, -x * s + y * c)


def bbox_of(points):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return (min(xs), min(ys), max(xs), max(ys))


def add_bbox(b, p):
    if b is None:
        return (p[0], p[1], p[0], p[1])
    return (min(b[0], p[0]), min(b[1], p[1]), max(b[2], p[0]), max(b[3], p[1]))


def rect_to_pts(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


class Board(object):
    def __init__(self, path=BOARD):
        with open(path, "r", encoding="utf-8") as fh:
            self.text = fh.read()
        self.root = parse(self.text)
        self.fps = []
        self.edge = []
        self._scan()

    # -- scan ---------------------------------------------------------------
    def _scan(self):
        for node in self.root:
            if not isinstance(node, list) or not node:
                continue
            nm = nname(node)
            if nm == "footprint":
                self.fps.append(self._read_fp(node))
            elif nm == "gr_line":
                self.edge.append(("gr_line", self._gr_line_pts(node)))
            elif nm == "gr_rect":
                self.edge.append(("gr_rect", self._gr_rect_pts(node)))
            elif nm == "gr_arc":
                self.edge.append(("gr_arc", self._gr_arc_pts(node)))
            elif nm == "gr_circle":
                self.edge.append(("gr_circle", self._gr_circle_pts(node)))

    @staticmethod
    def _gr_line_pts(n):
        s = kid(n, "start")
        e = kid(n, "end")
        return [(fv(s, 1), fv(s, 2)), (fv(e, 1), fv(e, 2))]

    @staticmethod
    def _gr_rect_pts(n):
        s = kid(n, "start")
        e = kid(n, "end")
        x0, x1 = sorted([fv(s, 1), fv(e, 1)])
        y0, y1 = sorted([fv(s, 2), fv(e, 2)])
        return rect_to_pts(x0, y0, x1, y1)

    @staticmethod
    def _gr_arc_pts(n):
        s = kid(n, "start")
        m = kid(n, "mid")
        e = kid(n, "end")
        # 三点定圆弧, 采样成折线
        p0 = (fv(s, 1), fv(s, 2))
        pm = (fv(m, 1), fv(m, 2))
        p1 = (fv(e, 1), fv(e, 2))
        ax, ay = p0
        bx, by = pm
        cx, cy = p1
        d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
        if abs(d) < 1e-9:
            return [p0, pm, p1]
        ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) +
              (cx * cx + cy * cy) * (ay - by)) / d
        uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) +
              (cx * cx + cy * cy) * (bx - ax)) / d
        r = math.hypot(ax - ux, ay - uy)
        a0 = math.atan2(ay - uy, ax - ux)
        a1 = math.atan2(by - uy, bx - ux)
        a2 = math.atan2(cy - uy, cx - ux)
        # 保证 a1 落在 a0→a2 的弧上
        def norm(a):
            while a < 0:
                a += 2 * math.pi
            while a >= 2 * math.pi:
                a -= 2 * math.pi
            return a
        sweep = norm(a2 - a0)
        mid = norm(a1 - a0)
        if mid > sweep:
            sweep -= 2 * math.pi
        pts = []
        steps = 24
        for i in range(steps + 1):
            ang = a0 + sweep * i / steps
            pts.append((ux + r * math.cos(ang), uy + r * math.sin(ang)))
        return pts

    @staticmethod
    def _gr_circle_pts(n):
        c = kid(n, "center")
        e = kid(n, "end")
        cx, cy = fv(c, 1), fv(c, 2)
        r = math.hypot(fv(e, 1) - cx, fv(e, 2) - cy)
        return [(cx + r * math.cos(2 * math.pi * i / 32),
                 cy + r * math.sin(2 * math.pi * i / 32)) for i in range(33)]

    @staticmethod
    def _read_fp(node):
        at = kid(node, "at")
        x = fv(at, 1, 0.0)
        y = fv(at, 2, 0.0)
        rot = fv(at, 3, 0.0) or 0.0
        props = {}
        for p in kids(node, "property"):
            props[val(p, 1, "")] = val(p, 2, "")
        fp = {
            "ref": props.get("Reference", ""),
            "value": props.get("Value", ""),
            "x": x, "y": y, "rot": rot,
            "pads": [],
            "fab": [],     # (x0,y0,x1,y1) 局部矩形
            "crtyd": [],
            "lib": "",
        }
        for pad in kids(node, "pad"):
            pat = kid(pad, "at")
            px = fv(pat, 1, 0.0)
            py = fv(pat, 2, 0.0)
            prot = fv(pat, 3, 0.0) or 0.0
            sz = kid(pad, "size")
            sw = fv(sz, 1, 0.0)
            sh = fv(sz, 2, 0.0)
            fp["pads"].append({
                "num": val(pad, 1, ""),
                "type": val(pad, 2, ""),
                "shape": val(pad, 3, ""),
                "px": px, "py": py, "prot": prot,
                "sw": sw, "sh": sh,
                "net": val(kid(pad, "net"), 1, ""),
            })
        for name in ("fp_line", "fp_rect"):
            for g in kids(node, name):
                lay = val(kid(g, "layer"), 1, "")
                if lay != "F.Fab":
                    continue
                s = kid(g, "start")
                e = kid(g, "end")
                if name == "fp_rect":
                    fp["fab"].append(rect_to_pts(fv(s, 1), fv(s, 2), fv(e, 1), fv(e, 2)))
                else:
                    fp["fab"].append([(fv(s, 1), fv(s, 2)), (fv(e, 1), fv(e, 2))])
        for g in kids(node, "fp_rect"):
            lay = val(kid(g, "layer"), 1, "")
            if lay != "F.CrtYd":
                continue
            s = kid(g, "start")
            e = kid(g, "end")
            fp["crtyd"].append(rect_to_pts(fv(s, 1), fv(s, 2), fv(e, 1), fv(e, 2)))
        return fp

    # -- accessors ----------------------------------------------------------
    def by_ref(self):
        d = {}
        for fp in self.fps:
            if fp["ref"]:
                d.setdefault(fp["ref"], fp)
        return d

    @staticmethod
    def abs_pad_boxes(fp):
        """绝对焊盘铜箔外框 (含封装旋转)。"""
        out = []
        for p in fp["pads"]:
            dx, dy = rot_xy(p["px"], p["py"], fp["rot"])
            cx = fp["x"] + dx
            cy = fp["y"] + dy
            # 焊盘自身旋转 ⇒ 尺寸交换
            w, h = p["sw"], p["sh"]
            if abs((p["prot"] + fp["rot"]) % 180.0 - 90.0) < 1e-6:
                w, h = h, w
            out.append((p["num"], cx - w / 2.0, cy - h / 2.0, cx + w / 2.0, cy + h / 2.0))
        return out

    @staticmethod
    def fab_bbox_abs(fp):
        """封装 F.Fab 外形绝对外框 (含封装旋转)。"""
        pts = []
        for poly in fp["fab"]:
            for (lx, ly) in poly:
                dx, dy = rot_xy(lx, ly, fp["rot"])
                pts.append((fp["x"] + dx, fp["y"] + dy))
        if not pts:
            return None
        return bbox_of(pts)

    @staticmethod
    def crtyd_bbox_abs(fp):
        pts = []
        for poly in fp["crtyd"]:
            for (lx, ly) in poly:
                dx, dy = rot_xy(lx, ly, fp["rot"])
                pts.append((fp["x"] + dx, fp["y"] + dy))
        if not pts:
            return None
        return bbox_of(pts)

    @staticmethod
    def local_extent(fp):
        """封装局部坐标下的「焊盘铜箔 ∪ F.Fab 外形」外框 = 落位后外形范围。"""
        pts = []
        for poly in fp["fab"]:
            pts.extend(poly)
        for p in fp["pads"]:
            w, h = p["sw"], p["sh"]
            if abs((p["prot"] + fp["rot"]) % 180.0 - 90.0) < 1e-6:
                w, h = h, w
            pts.extend(rect_to_pts(p["px"] - w / 2.0, p["py"] - h / 2.0,
                                   p["px"] + w / 2.0, p["py"] + h / 2.0))
        if not pts:
            return None
        return bbox_of(pts)

    @staticmethod
    def local_fab(fp):
        """封装局部坐标下的 F.Fab 外形外框。"""
        pts = []
        for poly in fp["fab"]:
            pts.extend(poly)
        if not pts:
            return None
        return bbox_of(pts)

    def edge_bbox(self):
        pts = []
        for _, p in self.edge:
            pts.extend(p)
        return bbox_of(pts)

    def edge_stats(self):
        kinds = {}
        for k, _ in self.edge:
            kinds[k] = kinds.get(k, 0) + 1
        return kinds


def rect_dist(a, b):
    """两个轴对齐矩形之间的最小间隙 (重叠时 = 负的重叠深度, 负值)。"""
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b
    dx = max(bx0 - ax1, ax0 - bx1)
    dy = max(by0 - ay1, ay0 - by1)
    if dx >= 0 or dy >= 0:
        return max(dx, dy) if (dx >= 0 and dy >= 0) else max(dx, dy, 0.0)
    # 重叠: 取最小穿透轴
    ox = min(ax1, bx1) - max(ax0, bx0)
    oy = min(ay1, by1) - max(ay0, by0)
    return -min(ox, oy)


def rect_overlap_area(a, b):
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b
    ox = min(ax1, bx1) - max(ax0, bx0)
    oy = min(ay1, by1) - max(ay0, by0)
    if ox <= 0 or oy <= 0:
        return 0.0
    return ox * oy


if __name__ == "__main__":
    b = Board()
    print("edge kinds:", b.edge_stats())
    print("edge bbox:", b.edge_bbox())
    refs = b.by_ref()
    print("footprints:", len(b.fps), "refs:", len(refs))
    for r in ["J_DEBUG", "J_UART", "J_USB_C", "J_CHG", "J_SOM_P1"]:
        fp = refs.get(r)
        if not fp:
            print(r, "MISSING")
            continue
        pb = Board.abs_pad_boxes(fp)
        print(r, "at", (fp["x"], fp["y"], fp["rot"]), "npads", len(fp["pads"]),
              "copper", bbox_of([(b_[1], b_[2], b_[3], b_[4]) for b_ in pb]),
              "fab", Board.fab_bbox_abs(fp))
