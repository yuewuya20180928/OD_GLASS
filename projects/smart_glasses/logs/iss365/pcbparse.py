#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""pcbparse.py —— ★★【ISS-365 · mech-lead】自写只读 s-expr 板解析器 ★★

★★★**★为什么自己写 (不 import 既有闸的解析器)★**★★
  `MECH/check_onepass_struct_crosscheck.py` 的 `Board` 类是【既有闸脚本的一部分】⇒
  ★**import 它 = 依赖它的内部实现, 而本单要证明的是「那一趟换封装后 MECH 侧判据漂不漂」**
  ⇒ 自己写一份, ★**只读板文件, 一个字节不写**★ ⇒ 两边口径可对照, 不互相污染。

  ★★**口径** ★★
    · `fab`   = `F.Fab` 图层的 `fp_line` / `fp_rect` 端点并集 (★座体/本体投影 = 结构侧最关心的量★)
    · `crtyd` = `F.CrtYd` 图层的 `fp_rect` (courtyard = 厂内 DRC 的器件占位, 用来判「贴不贴得住」)
    · `pads`  = 焊盘铜箔外框 (含旋转 90° 换算) + 焊盘号 + 焊盘尺寸
    · 中心距 = 同封装内两焊盘中心的距离 (★R_SEL_* 用的是「中心距 1.60」★)
"""
from __future__ import annotations

import math


def _tokenize(text):
    i, n, toks = 0, len(text), []
    while i < n:
        c = text[i]
        if c in "()":
            toks.append(c)
            i += 1
        elif c.isspace():
            i += 1
        elif c == '"':
            j, buf = i + 1, []
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


def _parse(text):
    toks = _tokenize(text)
    pos = 0

    def node():
        nonlocal pos
        if toks[pos] == "(":
            pos += 1
            out = []
            while pos < len(toks) and toks[pos] != ")":
                out.append(node())
            pos += 1
            return out
        t = toks[pos]
        pos += 1
        return t

    root = node()
    if (isinstance(root, list) and len(root) == 1 and isinstance(root[0], list)
            and root[0] and _nn(root[0]) == "kicad_pcb"):
        return root[0]
    return root


def _nn(node):
    if isinstance(node, list) and node:
        return node[0][1] if isinstance(node[0], tuple) else node[0]
    return None


def _kids(node, name):
    return [c for c in node if isinstance(c, list) and _nn(c) == name]


def _kid(node, name):
    k = _kids(node, name)
    return k[0] if k else None


def _v(node, idx=1, default=None):
    if isinstance(node, list) and len(node) > idx:
        x = node[idx]
        return x[1] if isinstance(x, tuple) else x
    return default


def _f(node, idx=1, default=None):
    try:
        return float(_v(node, idx, default))
    except (TypeError, ValueError):
        return default


def _bbox(pts):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return (min(xs), min(ys), max(xs), max(ys))


def _rect_pts(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def _fab_pts(node):
    """★F.Fab 图层的 fp_line / fp_rect 端点★"""
    out = []
    for g in _kids(node, "fp_line"):
        if _v(_kid(g, "layer"), 1, "") != "F.Fab":
            continue
        st, en = _kid(g, "start"), _kid(g, "end")
        out.append((_f(st, 1), _f(st, 2)))
        out.append((_f(en, 1), _f(en, 2)))
    for g in _kids(node, "fp_rect"):
        if _v(_kid(g, "layer"), 1, "") != "F.Fab":
            continue
        st, en = _kid(g, "start"), _kid(g, "end")
        out.extend(_rect_pts(_f(st, 1), _f(st, 2), _f(en, 1), _f(en, 2)))
    return out


def _crtyd_pts(node):
    """★F.CrtYd 图层的 fp_line / fp_rect (★KiCad 9 的库件两种都画·漏一种就会把 courtyard 读成空★)★"""
    out = []
    for g in _kids(node, "fp_line"):
        if _v(_kid(g, "layer"), 1, "") != "F.CrtYd":
            continue
        st, en = _kid(g, "start"), _kid(g, "end")
        out.append((_f(st, 1), _f(st, 2)))
        out.append((_f(en, 1), _f(en, 2)))
    for g in _kids(node, "fp_rect"):
        if _v(_kid(g, "layer"), 1, "") != "F.CrtYd":
            continue
        st, en = _kid(g, "start"), _kid(g, "end")
        out.extend(_rect_pts(_f(st, 1), _f(st, 2), _f(en, 1), _f(en, 2)))
    return out


def _pads(node):
    out = []
    for pad in _kids(node, "pad"):
        pat = _kid(pad, "at")
        sz = _kid(pad, "size")
        out.append({
            "num": _v(pad, 1, ""),
            "type": _v(pad, 2, ""),
            "px": _f(pat, 1, 0.0), "py": _f(pat, 2, 0.0),
            "prot": _f(pat, 3, 0.0) or 0.0,
            "sw": _f(sz, 1, 0.0), "sh": _f(sz, 2, 0.0),
        })
    return out


class Board(object):
    """★只读 kicad_pcb⇒ 封装 / 焊盘 / fab 外框 / 板框★"""

    def __init__(self, path):
        with open(path, "r", encoding="utf-8") as fh:
            self.text = fh.read()
        self.root = _parse(self.text)
        self.fps = []
        self.edge = []
        for node in self.root:
            nm = _nn(node)
            if nm == "footprint":
                self.fps.append(self._fp(node))
            elif nm == "gr_line":
                st, en = _kid(node, "start"), _kid(node, "end")
                if _v(_kid(node, "layer"), 1, "") == "Edge.Cuts":
                    self.edge.append((_f(st, 1), _f(st, 2), _f(en, 1), _f(en, 2)))
        self.by_ref = {}
        for fp in self.fps:
            self.by_ref.setdefault(fp["ref"], fp)

    @staticmethod
    def _fp(node):
        at = _kid(node, "at")
        props = {}
        for p in _kids(node, "property"):
            props[_v(p, 1, "")] = _v(p, 2, "")
        return {
            "ref": props.get("Reference", ""),
            "value": props.get("Value", ""),
            "x": _f(at, 1, 0.0), "y": _f(at, 2, 0.0),
            "rot": _f(at, 3, 0.0) or 0.0,
            "pads": _pads(node),
            "fab": _fab_pts(node),
            "crtyd": _crtyd_pts(node),
            "fpname": _v(node, 1, ""),
        }

    @staticmethod
    def pad_boxes(fp):
        out = []
        for p in fp["pads"]:
            w, h = p["sw"], p["sh"]
            if abs((p["prot"] + fp["rot"]) % 180.0 - 90.0) < 1e-6:
                w, h = h, w
            out.append((p["num"], p["px"] - w / 2.0, p["py"] - h / 2.0,
                        p["px"] + w / 2.0, p["py"] + h / 2.0))
        return out

    def fab_bbox_local(self, fp):
        """★返回 fab 外框的本地 (相对封装原点) bbox, 无 fab 则 None★"""
        if not fp["fab"]:
            return None
        return _bbox(fp["fab"])

    def crtyd_bbox_local(self, fp):
        if not fp["crtyd"]:
            return None
        return _bbox(fp["crtyd"])

    def pad_bbox_local(self, fp):
        bs = self.pad_boxes(fp)
        if not bs:
            return None
        return _bbox([(b[1], b[2], b[3], b[4]) for b in bs])

    def center_distances(self, fp):
        """★同封装内焊盘中心两两距离 (去重, 升序)★"""
        pts = []
        for p in fp["pads"]:
            key = (round(p["px"], 6), round(p["py"], 6))
            if key not in [(round(a, 6), round(b, 6)) for a, b in pts]:
                pts.append((p["px"], p["py"]))
        ds = []
        for i in range(len(pts)):
            for j in range(i + 1, len(pts)):
                d = math.hypot(pts[i][0] - pts[j][0], pts[i][1] - pts[j][1])
                ds.append(round(d, 4))
        return sorted(set(ds))


# ------------------------------------------------------------------ .kicad_mod


def parse_kicad_mod(path):
    """★读官方 .kicad_mod ⇒ fab 外框 / courtyard / 焊盘 / 本体尺寸★"""
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()
    root = _parse(text)
    if isinstance(root, list) and root and _nn(root) == "footprint":
        root = root
    elif isinstance(root, list) and len(root) == 1 and isinstance(root[0], list):
        root = root[0]
    fab = _fab_pts(root)
    crtyd = _crtyd_pts(root)
    pads = _pads(root)
    return {
        "fab_bbox": _bbox(fab) if fab else None,
        "crtyd_bbox": _bbox(crtyd) if crtyd else None,
        "npads": len(pads),
        "pads": pads,
        "pad_nums": [p["num"] for p in pads],
        "pad_sizes": sorted(set((round(p["sw"], 4), round(p["sh"], 4)) for p in pads)),
        "center_distances": _mod_center_distances(pads),
    }


def _mod_center_distances(pads):
    pts = []
    for p in pads:
        key = (round(p["px"], 6), round(p["py"], 6))
        if key not in [(round(a, 6), round(b, 6)) for a, b in pts]:
            pts.append((p["px"], p["py"]))
    ds = []
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            ds.append(round(math.hypot(pts[i][0] - pts[j][0], pts[i][1] - pts[j][1]), 4))
    return sorted(set(ds))


def size_of(bbox):
    if not bbox:
        return None
    return (round(bbox[2] - bbox[0], 4), round(bbox[3] - bbox[1], 4))
