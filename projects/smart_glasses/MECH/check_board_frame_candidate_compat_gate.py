#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MECH/check_board_frame_candidate_compat_gate.py

ISS-341 · mech-lead (结构总工 · 带散热) · 2026-11-22
「板那一趟到底画的是哪块板?」 —— U-1 板框冻结三候选 × 现役板 【相容性机器判定闸】

======================================================================
性质: ★只读闸★ — 不写板 / 不写 HW/ / 不改任何既有 MECH 文件 / 不落表
======================================================================

本闸回答 **一个** 问题:
    U-1 拍成 ① B160x100 / ② F30A / ③ P60x15 哪一个, 决定「板那一趟」是
    「改现役那块板一次」 还是 「画一块新板」 —— 这两件事工作量差一个数量级。

判据 (逐帧输出):
    J1 装得下吗      —— 该帧矩形 vs 现役板占位并集 (原位外溢 + 尺寸包络)
                      vs J_SOM 承载区 bbox (原位外溢 + 尺寸包络), 差多少 mm
    J2 层数/板厚一致吗 —— 帧 layers/thickness vs 板实测铜层数/thickness
    J3 主控形态一致吗 —— 帧隐含形态 (SOM 承载区 / SoC 直上) vs 现役板形态
    J4 现役帧口径自洽吗 —— cal:FRAMES.current_frame 与盘上实测板框/层数/板厚是否一致
    J5 最终判决      —— 「这一趟 = 改现役板一次」 还是
                        「这一趟 = 重画一块新板 (现役板 186 封装 / 45 条未连接 /
                          作业包 S1~S13 全部作废)」

★**两层问题分层** (本闸只答下位参数, 上位问题单列):
    上位 = 这一趟画哪块物理产品 (台架板 / 产品板)
    下位 = 那一块板用哪个框/层数/板厚 (U-1)
    ⇒ 「建议默认值」那一栏必须分层填, 不能用「36 档结构判据唯一全绿」替上位问题作答。

用法:
    python3 MECH/check_board_frame_candidate_compat_gate.py              # 裸跑, 出三候选相容性表
    python3 MECH/check_board_frame_candidate_compat_gate.py --selftest   # 自测 (末行 ALL TESTS PASS)
    python3 MECH/check_board_frame_candidate_compat_gate.py --json       # 机器可读输出
    python3 MECH/check_board_frame_candidate_compat_gate.py --root DIR   # 指定根目录 (沙盒用)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import shutil
import sys

# ---------------------------------------------------------------- 常量 / 路径

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ROOT = os.path.dirname(HERE)

BOARD_REL = os.path.join("HW", "PCB", "demo_mainboard.kicad_pcb")
CALIBER_REL = os.path.join("HW", "PCB", "BOARD_FRAME_CALIBER.md")
GEOM_REL = os.path.join("MECH", "BOARD_GEOM_30MM.md")
PARAMS_REL = os.path.join("HW", "PCB", "demo_mainboard_params.json")
PM_REL = os.path.join("state", "fragments", "pm.yaml")

# ★**现役板封装数基线**★ —— 这是**声明的期望值** (规格), 不是闸的判决结果。
#   出处: ISS-341 §0 事实2 (main 本机实读) + 本机 2026-11-22 独立复算 = 186。
#   用 `--expect-footprints N` 可覆盖 (沙盒反向用例 E 用它证明闸对封装数变化有反应)。
EXPECTED_FOOTPRINTS = 186

TOL_DIM_MM = 0.05      # 板框尺寸判等容差
TOL_THK_MM = 0.01      # 板厚判等容差

VERDICT_MODIFY = "这一趟 = 改现役板一次"
VERDICT_NEW = "这一趟 = 重画一块新板 (现役板 186 封装 / 45 条未连接 / 作业包 S1~S13 全部作废)"

FORM_SOM = "SOM 承载区形态 (RK3572 SOM 直插 BTB 座)"
FORM_SOC = "SoC 直上板形态 (SoC 直接落板)"


class GateError(Exception):
    """可读错误 —— 闸遇到坏输入时抛这个, 绝不允许抛裸 Traceback。"""


# ---------------------------------------------------------------- s-expr 解析

class _QStr(str):
    """带引号的字符串 (与裸原子区分)。"""
    __slots__ = ()


def _tokenize(s):
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if c == "(" or c == ")":
            yield c
            i += 1
        elif c.isspace():
            i += 1
        elif c == '"':
            j = i + 1
            buf = []
            while j < n:
                if s[j] == "\\":
                    buf.append(s[j + 1])
                    j += 2
                    continue
                if s[j] == '"':
                    j += 1
                    break
                buf.append(s[j])
                j += 1
            yield _QStr("".join(buf))
            i = j
        else:
            j = i
            while j < n and not s[j].isspace() and s[j] not in '()"':
                j += 1
            yield s[i:j]
            i = j


class _Parser:
    """流式 s-expr 解析器 —— 逐个顶层 form 吐出来, 不把整棵树塞进内存。"""

    def __init__(self, text):
        self._t = _tokenize(text)
        self._push = None

    def _next(self):
        if self._push is not None:
            t, self._push = self._push, None
            return t
        return next(self._t, None)

    def _pushback(self, t):
        self._push = t

    def children(self):
        """'(' 已被消费。逐个吐出子 form, 直到 ')'; 括号不平衡抛 GateError。"""
        while True:
            t = self._next()
            if t is None:
                raise GateError("板文件 s-expr 解析提前结束 (括号不平衡)")
            if t == ")":
                return
            if t == "(":
                yield self.form()
            else:
                yield t

    def form(self):
        return list(self.children())

    def top_forms(self):
        """吐顶层 form (第一个是根节点本身)。"""
        while True:
            t = self._next()
            if t is None:
                return
            if t == "(":
                yield self.form()
            else:
                yield t


def _num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def _rot(px, py, deg):
    a = math.radians(deg)
    return px * math.cos(a) - py * math.sin(a), px * math.sin(a) + py * math.cos(a)


def top_level_spans(text):
    """扫描文本, 返回根节点 (kicad_pcb) 的【直接子 form】的字节区间。

    ★注意★: 整个 .kicad_pcb 文件本身就是一个 s-expr (根 = kicad_pcb),
    所以「顶层 form」= 根的子 form (general / layers / footprint / gr_line ...)。
    """
    spans = []
    i, n = 0, len(text)
    depth = 0
    start = None
    while i < n:
        c = text[i]
        if c == '"':
            j = i + 1
            while j < n:
                if text[j] == "\\":
                    j += 2
                    continue
                if text[j] == '"':
                    j += 1
                    break
                j += 1
            i = j
            continue
        if c == "(":
            if depth == 1:
                start = i
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 1 and start is not None:
                spans.append((start, i + 1))
                start = None
        i += 1
    return spans


# ---------------------------------------------------------------- 读板

def read_board(path):
    """读现役板 → 实测事实字典。任何结构性问题抛 GateError (可读)。"""
    if not os.path.isfile(path):
        raise GateError("板文件不存在: %s" % path)
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    except OSError as exc:
        raise GateError("板文件读不出来: %s (%s)" % (path, exc))

    p = _Parser(text)
    first = p._next()
    if first != "(":
        raise GateError("板文件不是 s-expr (首字符不是 '('): %s" % path)
    root_name = p._next()
    if root_name != "kicad_pcb":
        raise GateError("板文件根节点不是 kicad_pcb (读到 %r): %s" % (root_name, path))

    thickness = None
    copper_layers = []
    edge_lines = []
    edge_rects = []
    footprints = []

    for form in p.children():
        if not isinstance(form, list) or not form:
            continue
        tag = form[0]
        if tag == "footprint":
            footprints.append(_parse_footprint(form))
        elif tag == "general":
            for e in form[1:]:
                if isinstance(e, list) and e and e[0] == "thickness":
                    thickness = _num(e[1])
        elif tag == "layers":
            for e in form[1:]:
                if isinstance(e, list) and len(e) > 1:
                    nm = e[1]
                    if nm == "F.Cu" or nm == "B.Cu" or (isinstance(nm, str) and nm.startswith("In")):
                        copper_layers.append(str(nm))
        elif tag in ("gr_line", "gr_rect", "gr_poly", "gr_circle", "gr_arc"):
            layer = None
            start = end = None
            width = 0.0
            for e in form[1:]:
                if not isinstance(e, list) or not e:
                    continue
                if e[0] == "layer":
                    layer = str(e[1])
                elif e[0] == "start":
                    start = [_num(x) for x in e[1:] if _num(x) is not None]
                elif e[0] == "end":
                    end = [_num(x) for x in e[1:] if _num(x) is not None]
                elif e[0] == "stroke":
                    for q in e[1:]:
                        if isinstance(q, list) and q and q[0] == "width":
                            width = _num(q[1]) or 0.0
            if layer == "Edge.Cuts":
                if tag == "gr_line" and start and end:
                    edge_lines.append((start[0], start[1], end[0], end[1], width))
                elif tag == "gr_rect" and start and end:
                    edge_rects.append((start[0], start[1], end[0], end[1], width))

    if not footprints:
        raise GateError("板文件里一个 footprint 都没有 (封装数 = 0) ⇒ 板面读不出来: %s" % path)

    # --- Edge.Cuts 包围盒 -------------------------------------------------
    pts = []
    for (x1, y1, x2, y2, w) in edge_lines:
        pts.append((x1, y1, w))
        pts.append((x2, y2, w))
    for (x1, y1, x2, y2, w) in edge_rects:
        pts.append((x1, y1, w))
        pts.append((x2, y2, w))
    if not pts:
        raise GateError("板文件里没有 Edge.Cuts 几何 ⇒ 板框读不出来: %s" % path)
    cx0 = min(p[0] for p in pts)
    cy0 = min(p[1] for p in pts)
    cx1 = max(p[0] for p in pts)
    cy1 = max(p[1] for p in pts)
    maxw = max(p[2] for p in pts)
    edge_bbox = (cx0, cy0, cx1, cy1)
    edge_bbox_ink = (cx0 - maxw / 2.0, cy0 - maxw / 2.0, cx1 + maxw / 2.0, cy1 + maxw / 2.0)

    # --- 占位并集 ---------------------------------------------------------
    union = None
    som_union = None
    som_center = None
    som_fp = 0
    som_pads = 0
    for fp in footprints:
        ref = fp["ref"]
        is_som = bool(ref) and ref.startswith("J_SOM")
        if is_som:
            som_fp += 1
        for (x0, y0, x1, y1) in fp["pads_abs"]:
            union = _union(union, (x0, y0, x1, y1))
            if is_som:
                som_union = _union(som_union, (x0, y0, x1, y1))
                som_pads += 1
                cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
                som_center = _union(som_center, (cx, cy, cx, cy))
        for (x0, y0, x1, y1) in fp["outline_abs"]:
            fp["outline_bbox"] = (x0, y0, x1, y1)
    som_outline = None
    for fp in footprints:
        if fp["ref"] and fp["ref"].startswith("J_SOM") and fp.get("outline_bbox"):
            som_outline = _union(som_outline, fp["outline_bbox"])

    refs = [fp["ref"] for fp in footprints]
    dup = sorted({r for r in refs if r and refs.count(r) > 1})
    none_ref = sum(1 for r in refs if not r)
    # ★结构缺陷 → 直接抛可读错误 (ref 基础的分析在 ref 不干净时不成立)★
    if none_ref:
        raise GateError("板里有 %d 个封装没有 Reference 属性 ⇒ 位号级分析不成立: %s"
                        % (none_ref, path))
    if dup:
        raise GateError("板里有重复位号 %d 个 (%s) ⇒ 位号级分析不成立: %s"
                        % (len(dup), ", ".join(dup[:10]), path))

    return {
        "path": path,
        "md5": _md5(path),
        "bytes": len(text),
        "edge_bbox": edge_bbox,
        "edge_bbox_ink": edge_bbox_ink,
        "edge_n": len(edge_lines) + len(edge_rects),
        "edge_nominal": (round(edge_bbox[2] - edge_bbox[0], 4), round(edge_bbox[3] - edge_bbox[1], 4)),
        "copper_layers": copper_layers,
        "copper_layer_count": len(copper_layers),
        "thickness": thickness,
        "footprint_count": len(footprints),
        "distinct_refs": len(set(r for r in refs if r)),
        "dup_refs": dup,
        "none_ref_count": none_ref,
        "pad_union_bbox": union,
        "som_union_bbox": som_union,
        "som_center_bbox": som_center,
        "som_outline_bbox": som_outline,
        "som_fp_count": som_fp,
        "som_pad_count": som_pads,
        "form": FORM_SOM if som_fp > 0 else FORM_SOC,
        "footprints": footprints,
        "_text": text,
    }


def _union(a, b):
    if a is None:
        return b
    return (min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3]))


def _parse_footprint(form):
    ref = None
    at = None
    pads = []
    outline = []
    for e in form[1:]:
        if not isinstance(e, list) or not e:
            continue
        t = e[0]
        if t == "property" and len(e) > 1 and e[1] == "Reference":
            ref = str(e[2])
        elif t == "at":
            at = [_num(x) for x in e[1:] if _num(x) is not None]
        elif t == "pad":
            pa = ps = None
            for q in e[1:]:
                if isinstance(q, list) and q:
                    if q[0] == "at":
                        pa = [_num(x) for x in q[1:] if _num(x) is not None]
                    elif q[0] == "size":
                        ps = [_num(x) for x in q[1:] if _num(x) is not None]
            if pa and ps:
                pads.append((pa, ps))
        elif t in ("fp_line", "fp_rect", "fp_circle", "fp_arc", "fp_poly"):
            s = e2 = None
            for q in e[1:]:
                if isinstance(q, list) and q:
                    if q[0] == "start":
                        s = [_num(x) for x in q[1:] if _num(x) is not None]
                    elif q[0] == "end":
                        e2 = [_num(x) for x in q[1:] if _num(x) is not None]
                    elif q[0] == "center":
                        s = [_num(x) for x in q[1:] if _num(x) is not None]
                    elif q[0] == "mid":
                        e2 = [_num(x) for x in q[1:] if _num(x) is not None]
            if s and e2:
                outline.append((s[0], s[1], e2[0], e2[1]))

    ox, oy = (at[0], at[1]) if at else (0.0, 0.0)
    ang = at[2] if at and len(at) > 2 else 0.0

    def _abs(px, py):
        if ang:
            dx, dy = _rot(px, py, ang)
        else:
            dx, dy = px, py
        return ox + dx, oy + dy

    pads_abs = []
    for (pa, ps) in pads:
        ax, ay = _abs(pa[0], pa[1])
        pads_abs.append((ax - ps[0] / 2.0, ay - ps[1] / 2.0, ax + ps[0] / 2.0, ay + ps[1] / 2.0))
    outline_abs = []
    for (sx, sy, ex, ey) in outline:
        ax, ay = _abs(sx, sy)
        bx, by = _abs(ex, ey)
        outline_abs.append((min(ax, bx), min(ay, by), max(ax, bx), max(ay, by)))

    return {
        "ref": ref,
        "at": (ox, oy, ang),
        "pads_abs": pads_abs,
        "outline_abs": outline_abs,
        "outline_bbox": None,
        "pad_count": len(pads),
    }


# ---------------------------------------------------------------- 读帧

def read_frames(path):
    """读 HW/PCB/BOARD_FRAME_CALIBER.md §2 ```json cal:FRAMES``` 块。"""
    if not os.path.isfile(path):
        raise GateError("帧口径文件不存在: %s" % path)
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        text = fh.read()
    m = re.search(r"```json\s+cal:FRAMES\s*\n(.*?)\n```", text, re.S)
    if not m:
        raise GateError("在 %s 里找不到 ```json cal:FRAMES``` 块" % path)
    try:
        data = json.loads(m.group(1))
    except ValueError as exc:
        raise GateError("cal:FRAMES 块不是合法 JSON: %s (%s)" % (path, exc))
    frames = data.get("frames")
    if not isinstance(frames, dict) or not frames:
        raise GateError("cal:FRAMES 里没有 frames 字典: %s" % path)
    cur = data.get("current_frame")
    if cur not in frames:
        raise GateError("cal:FRAMES.current_frame = %r 不在 frames 里 (%s)" % (cur, ", ".join(sorted(frames))))
    out = {}
    for fid, f in frames.items():
        try:
            out[fid] = {
                "id": fid,
                "name": f.get("name", ""),
                "width_mm": float(f["width_mm"]),
                "height_mm": float(f["height_mm"]),
                "layers": int(f["layers"]),
                "thickness_mm": float(f["thickness_mm"]),
                "current": bool(f.get("current", False)),
                "desc": f.get("desc", ""),
            }
        except (KeyError, TypeError, ValueError) as exc:
            raise GateError("帧 %s 的字段不全/类型不对: %s (%s)" % (fid, path, exc))
    return {"current_frame": cur, "frames": out, "path": path}


# ---------------------------------------------------------------- 读结构侧口径

def read_mech_caliber(path):
    """只读 MECH/BOARD_GEOM_30MM.md §1 (板框/板厚/层数/主控) —— 结构侧权威表口径。"""
    if not os.path.isfile(path):
        return {"path": path, "present": False}
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        text = fh.read()
    sec = text.split("\n## 1.")[1].split("\n## ")[0] if "\n## 1." in text else ""
    def grab(pat, src=None):
        m = re.search(pat, sec if src is None else src)
        return m.group(1) if m else None
    return {
        "path": path,
        "present": True,
        "board_len_mm": grab(r"板长 X\s*\|\s*\*\*([\d.]+)mm"),
        "board_width_mm": grab(r"板宽 Y\s*\|\s*\*\*([\d.]+)mm"),
        "thickness_mm": grab(r"板厚\s*\|\s*\*\*([\d.]+)mm"),
        "layers_from_thk": grab(r"板厚\s*\|\s*\*\*[\d.]+mm\*\*\s*\((\d+)\s*层"),
        # 主控口径在 §0 声明行 (整篇文档口径, 不限 §1)
        "soc_model": grab(r"主控\s*\*\*(RK\d+)\*\*", text),
        "soc_pkg": grab(r"FCCSP698L,\s*\*\*([\d.]+)\s*\(X\)\s*×\s*\*\*([\d.]+)\s*\(Y\)", text),
        "board_weight_g": grab(r"板重\s*\|\s*\*\*([\d.]+)g"),
        "rk3576_hits": len(re.findall(r"RK3576", text)),
        "rk3572_hits": len(re.findall(r"RK3572", text)),
        "md5": _md5(path),
    }


def read_params(path):
    """只读 HW/PCB/demo_mainboard_params.json 的 board 段 (板框真源)。"""
    if not os.path.isfile(path):
        return {"path": path, "present": False}
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError) as exc:
        raise GateError("demo_mainboard_params.json 读不出来: %s (%s)" % (path, exc))
    b = data.get("board", {})
    return {
        "path": path,
        "present": True,
        "width_mm": b.get("width_mm"),
        "height_mm": b.get("height_mm"),
        "layers": b.get("layers"),
        "thickness_mm": b.get("thickness_mm"),
        "md5": _md5(path),
    }


def read_pm_suggestion(path):
    """只读 state/fragments/pm.yaml 里 ISS-310 的 U-1 建议默认值 (可选 · 读不到不算失败)。"""
    out = {"present": False, "key": "iss310_main_board_frame_u1_decision", "value": None}
    if not os.path.isfile(path):
        return out
    try:
        import yaml  # 本机有 PyYAML; 没有就优雅降级
    except ImportError:
        return out
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
    except Exception:
        return out
    for it in (data or {}).get("answers", []) or []:
        if isinstance(it, dict) and it.get("key") == out["key"]:
            out["present"] = True
            out["value"] = str(it.get("value", ""))
            out["ref"] = str(it.get("ref", ""))
            out["to"] = str(it.get("to", ""))
            break
    return out


# ---------------------------------------------------------------- 相容性判定

def _fit_frame(frame_w, frame_h, bbox):
    """把一个 bbox (x0,y0,x1,y1) 放进 frame (原点在 0,0, 尺寸 W×H) 的两种口径。

    口径 A 【原位外溢 as-is】: 保持盘上现有坐标不动, 看它有没有掉出框。
    口径 B 【尺寸包络 envelope】: 允许重排, 只比「元件包络尺寸 vs 框尺寸」。
    """
    if bbox is None:
        return {"as_is": False, "envelope": False, "overflow_x": 0.0, "overflow_y": 0.0,
                "delta_w": 0.0, "delta_h": 0.0, "w": 0.0, "h": 0.0, "bbox": None}
    x0, y0, x1, y1 = bbox
    w = x1 - x0
    h = y1 - y0
    ov_x = max(0.0, x1 - frame_w, -x0)
    ov_y = max(0.0, y1 - frame_h, -y0)
    return {
        "as_is": ov_x <= 1e-9 and ov_y <= 1e-9,
        "envelope": (w <= frame_w + 1e-9) and (h <= frame_h + 1e-9),
        "overflow_x": round(ov_x, 4),
        "overflow_y": round(ov_y, 4),
        "delta_w": round(frame_w - w, 4),
        "delta_h": round(frame_h - h, 4),
        "w": round(w, 4),
        "h": round(h, 4),
        "bbox": tuple(round(v, 4) for v in bbox),
    }


def evaluate(root, expect_footprints=EXPECTED_FOOTPRINTS, read_pm=True):
    """跑一遍完整判定 → 报告字典。任何输入坏了抛 GateError (可读)。"""
    board = read_board(os.path.join(root, BOARD_REL))
    frames_src = read_frames(os.path.join(root, CALIBER_REL))
    mech = read_mech_caliber(os.path.join(root, GEOM_REL))
    params = read_params(os.path.join(root, PARAMS_REL))
    pm = read_pm_suggestion(os.path.join(root, PM_REL)) if read_pm else {"present": False}

    # --- 板面异常 (可读, 不崩) -------------------------------------------
    anomalies = []
    if board["dup_refs"]:
        anomalies.append("重复位号 %d 个: %s" % (len(board["dup_refs"]), ", ".join(board["dup_refs"][:10])))
    if board["none_ref_count"]:
        anomalies.append("有 %d 个封装没有 Reference 属性" % board["none_ref_count"])
    if expect_footprints and board["footprint_count"] != expect_footprints:
        anomalies.append("封装数 %d ≠ 基线 %d (基线出处: 现役板 2026-11-06 实测; 删/改封装会被本闸抓到)"
                         % (board["footprint_count"], expect_footprints))
    if board["thickness"] is None:
        anomalies.append("板文件里读不到 (general (thickness ...))")
    if board["copper_layer_count"] == 0:
        anomalies.append("板文件里读不到铜层")
    if params.get("present"):
        pd = []
        if params.get("width_mm") is not None and abs(float(params["width_mm"]) - board["edge_nominal"][0]) > TOL_DIM_MM:
            pd.append("宽 %s vs 板框 %.2f" % (params["width_mm"], board["edge_nominal"][0]))
        if params.get("height_mm") is not None and abs(float(params["height_mm"]) - board["edge_nominal"][1]) > TOL_DIM_MM:
            pd.append("高 %s vs 板框 %.2f" % (params["height_mm"], board["edge_nominal"][1]))
        if params.get("layers") is not None and int(params["layers"]) != board["copper_layer_count"]:
            pd.append("层数 %s vs 板实测 %d" % (params["layers"], board["copper_layer_count"]))
        if params.get("thickness_mm") is not None and board["thickness"] is not None \
                and abs(float(params["thickness_mm"]) - board["thickness"]) > TOL_THK_MM:
            pd.append("板厚 %s vs 板实测 %s" % (params["thickness_mm"], board["thickness"]))
        if pd:
            anomalies.append("demo_mainboard_params.json 与板面不一致: " + "; ".join(pd))

    cur_id = frames_src["current_frame"]
    cur = frames_src["frames"][cur_id]

    # --- 现役帧口径自洽 (J4) ---------------------------------------------
    def frame_matches_board(f):
        d = []
        if abs(f["width_mm"] - board["edge_nominal"][0]) > TOL_DIM_MM:
            d.append("宽 %.2f vs 板 %.2f" % (f["width_mm"], board["edge_nominal"][0]))
        if abs(f["height_mm"] - board["edge_nominal"][1]) > TOL_DIM_MM:
            d.append("高 %.2f vs 板 %.2f" % (f["height_mm"], board["edge_nominal"][1]))
        if f["layers"] != board["copper_layer_count"]:
            d.append("层数 %d vs 板 %d" % (f["layers"], board["copper_layer_count"]))
        if board["thickness"] is None or abs(f["thickness_mm"] - board["thickness"]) > TOL_THK_MM:
            d.append("板厚 %.2f vs 板 %s" % (f["thickness_mm"], board["thickness"]))
        return d

    cur_mismatch = frame_matches_board(cur)
    cur_agrees = not cur_mismatch

    # --- 逐帧判定 ---------------------------------------------------------
    per_frame = []
    for fid in sorted(frames_src["frames"]):
        f = frames_src["frames"][fid]
        W, H = f["width_mm"], f["height_mm"]
        fit_all = _fit_frame(W, H, board["pad_union_bbox"])
        fit_som = _fit_frame(W, H, board["som_union_bbox"])
        fit_som_c = _fit_frame(W, H, board["som_center_bbox"])

        layers_ok = (f["layers"] == board["copper_layer_count"])
        thk_ok = (board["thickness"] is not None and abs(f["thickness_mm"] - board["thickness"]) <= TOL_THK_MM)
        mismatch = frame_matches_board(f)
        same_as_board = not mismatch

        frame_form = FORM_SOM if fit_som["envelope"] else FORM_SOC
        form_ok = (frame_form == board["form"])

        is_cur = (fid == cur_id)
        if is_cur:
            verdict = VERDICT_MODIFY if (same_as_board and fit_all["as_is"]) else VERDICT_NEW
        else:
            verdict = VERDICT_NEW

        reasons = []
        if not same_as_board:
            reasons.append("框/层数/板厚与盘上板不一致 (" + "; ".join(mismatch) + ")")
        if not fit_all["as_is"]:
            reasons.append("现役板占位并集原位外溢 X+%.2f / Y+%.2f mm (框 %0.2f×%0.2f vs 占位 %0.2f×%0.2f)"
                           % (fit_all["overflow_x"], fit_all["overflow_y"], W, H, fit_all["w"], fit_all["h"]))
        if not fit_som["as_is"]:
            reasons.append("J_SOM 承载区原位外溢 X+%.2f / Y+%.2f mm" % (fit_som["overflow_x"], fit_som["overflow_y"]))
        if not fit_som["envelope"]:
            reasons.append("J_SOM 承载区尺寸包络 %0.2f×%0.2f vs 框 %0.2f×%0.2f ⇒ 宽余 %+0.2f / 高差 %+0.2f mm (★负 = 装不下★)"
                           % (fit_som["w"], fit_som["h"], W, H, fit_som["delta_w"], fit_som["delta_h"]))
        if not layers_ok:
            reasons.append("层数不一致: 帧 %d 层 vs 板实测 %d 铜层" % (f["layers"], board["copper_layer_count"]))
        if not thk_ok:
            reasons.append("板厚不一致: 帧 %.2f mm vs 板实测 %s mm" % (f["thickness_mm"], board["thickness"]))
        if not form_ok:
            reasons.append("形态换架构: 帧隐含 %s, 现役板是 %s" % (frame_form, board["form"]))
        if is_cur and cur_mismatch:
            reasons.append("★口径自相矛盾★ cal:FRAMES.current_frame 指向本帧, 但本帧与盘上实测板框不符")
        if verdict == VERDICT_MODIFY and not reasons:
            reasons.append("帧 id / 尺寸 / 层数 / 板厚 / 形态 / 占位装载 与盘上板逐项一致 ⇒ 框不变")

        per_frame.append({
            "id": fid,
            "name": f["name"],
            "desc": f["desc"],
            "width_mm": W,
            "height_mm": H,
            "layers": f["layers"],
            "thickness_mm": f["thickness_mm"],
            "is_current_frame": is_cur,
            "same_as_board": same_as_board,
            "mismatch": mismatch,
            "fit_all": fit_all,
            "fit_som": fit_som,
            "fit_som_center": fit_som_c,
            "layers_ok": layers_ok,
            "thickness_ok": thk_ok,
            "form_ok": form_ok,
            "frame_form": frame_form,
            "verdict": verdict,
            "reasons": reasons,
        })

    # --- 建议默认值交叉核对 (只读 pm.yaml) -------------------------------
    suggest = {"present": pm.get("present", False), "value": pm.get("value"), "ref": pm.get("ref"),
               "frame": None, "machine_verdict": None, "note": ""}
    if pm.get("present"):
        m = re.search(r"(F30A|B160x100|P60x15)", pm.get("value") or "")
        if m:
            suggest["frame"] = m.group(1)
            for pf in per_frame:
                if pf["id"] == suggest["frame"]:
                    suggest["machine_verdict"] = pf["verdict"]
        suggest["note"] = ("★建议·非已决定★; 本闸只判【该帧与现役板的相容性】, "
                           "不替老板拍『这一趟画台架板还是产品板』这个上位问题")

    return {
        "root": root,
        "board": board,
        "frames_src": frames_src,
        "mech": mech,
        "params": params,
        "anomalies": anomalies,
        "current_frame": cur_id,
        "current_frame_agrees_with_board": cur_agrees,
        "current_frame_mismatch": cur_mismatch,
        "per_frame": per_frame,
        "suggest": suggest,
    }


# ---------------------------------------------------------------- 渲染

def _dw(s):
    """显示宽度 (CJK 按 2)。"""
    w = 0
    for ch in str(s):
        w += 2 if ord(ch) > 0x2E7F else 1
    return w


def _pad(s, n):
    s = str(s)
    return s + " " * max(0, n - _dw(s))


def _f(v, n=2):
    if v is None:
        return "n/a"
    return ("%." + str(n) + "f") % v


def render(rep):
    b = rep["board"]
    L = []
    W = 100
    L.append("=" * W)
    L.append("ISS-341 · U-1 板框三候选 × 现役板 —— 相容性机器判定闸 (只读)")
    L.append("根目录: %s" % rep["root"])
    L.append("=" * W)

    L.append("")
    L.append("【§1 现役板实测 (读盘面 · 本机独立复算)】")
    L.append("  板文件            : %s" % BOARD_REL)
    L.append("  板框 Edge.Cuts    : %d 条几何 · 名义 %0.2f × %0.2f mm (含线宽包围盒 %0.2f × %0.2f)"
             % (b["edge_n"], b["edge_nominal"][0], b["edge_nominal"][1],
                b["edge_bbox_ink"][2] - b["edge_bbox_ink"][0], b["edge_bbox_ink"][3] - b["edge_bbox_ink"][1]))
    L.append("  铜层              : %d 层 (%s)" % (b["copper_layer_count"], " ".join(b["copper_layers"])))
    L.append("  板厚              : %s mm" % _f(b["thickness"]))
    L.append("  封装数            : %d (distinct ref %d · 重复 %d · 无 Reference %d)"
             % (b["footprint_count"], b["distinct_refs"], len(b["dup_refs"]), b["none_ref_count"]))
    pu = b["pad_union_bbox"]
    L.append("  占位并集 (焊盘)   : %0.2f × %0.2f mm  (x %0.2f..%0.2f / y %0.2f..%0.2f)"
             % (pu[2] - pu[0], pu[3] - pu[1], pu[0], pu[2], pu[1], pu[3]))
    sb = b["som_union_bbox"]
    sc = b["som_center_bbox"]
    L.append("  J_SOM 承载区(焊盘): %0.2f × %0.2f mm  (x %0.2f..%0.2f / y %0.2f..%0.2f) · %d 座 / %d 焊盘"
             % (sb[2] - sb[0], sb[3] - sb[1], sb[0], sb[2], sb[1], sb[3], b["som_fp_count"], b["som_pad_count"]))
    L.append("  J_SOM 承载区(中心): %0.2f × %0.2f mm" % (sc[2] - sc[0], sc[3] - sc[1]))
    if b["som_outline_bbox"]:
        so = b["som_outline_bbox"]
        L.append("  J_SOM 线框并集    : %0.2f × %0.2f mm  (★口径 = fp_line 并集, ≠ CALIBER §3 的 GetBoundingBox 口径★)"
                 % (so[2] - so[0], so[3] - so[1]))
    L.append("  形态              : %s" % b["form"])

    L.append("")
    L.append("【§2 候选帧 (读 %s §2 cal:FRAMES)】" % CALIBER_REL)
    L.append("  现役帧 (current_frame) = %s · 与盘上实测板框/层数/板厚一致? %s"
             % (rep["current_frame"], "是" if rep["current_frame_agrees_with_board"] else "★否★"))
    if rep["current_frame_mismatch"]:
        L.append("    ★口径与盘面不符: %s" % "; ".join(rep["current_frame_mismatch"]))

    L.append("")
    L.append("【§3 三候选相容性矩阵】")
    hdr = ["帧 id", "尺寸 mm", "层", "板厚", "现役帧", "装得下现役板?", "差多少 mm", "形态一致?", "这一趟 = 改一次 / 重画新板"]
    rows = []
    for pf in rep["per_frame"]:
        fa = pf["fit_all"]
        fs = pf["fit_som"]
        fits = "相容" if (fa["as_is"] and fs["as_is"]) else ("装载相容·尺寸装不下" if fa["as_is"] else "不相容")
        if fa["as_is"] and fs["as_is"]:
            fits = "相容"
        d = []
        if fa["overflow_x"] > 0 or fa["overflow_y"] > 0:
            d.append("占位外溢 X+%0.2f/Y+%0.2f" % (fa["overflow_x"], fa["overflow_y"]))
        if fs["overflow_x"] > 0 or fs["overflow_y"] > 0:
            d.append("承载区外溢 X+%0.2f/Y+%0.2f" % (fs["overflow_x"], fs["overflow_y"]))
        if not d:
            d.append("无外溢 (占位余量 X%0.2f/Y%0.2f)" % (fa["delta_w"], fa["delta_h"]))
        verdict = "改现役板一次" if pf["verdict"] == VERDICT_MODIFY else "★重画一块新板★"
        rows.append([pf["id"], "%0.2f×%0.2f" % (pf["width_mm"], pf["height_mm"]), str(pf["layers"]),
                     _f(pf["thickness_mm"]), "是" if pf["is_current_frame"] else "否",
                     fits, "; ".join(d), "一致" if pf["form_ok"] else "★换架构★", verdict])
    widths = [max(_dw(hdr[i]), max(_dw(r[i]) for r in rows)) for i in range(len(hdr))]
    L.append("  " + " | ".join(_pad(hdr[i], widths[i]) for i in range(len(hdr))))
    L.append("  " + "-+-".join("-" * w for w in widths))
    for r in rows:
        L.append("  " + " | ".join(_pad(r[i], widths[i]) for i in range(len(r))))

    L.append("")
    L.append("【§4 逐帧判决 (机器可判的那一句)】")
    for pf in rep["per_frame"]:
        L.append("  ── %s (%s) %0.2f×%0.2f mm · %d 层 · %0.2f mm%s"
                 % (pf["id"], pf["name"], pf["width_mm"], pf["height_mm"], pf["layers"],
                    pf["thickness_mm"], "  ←现役帧" if pf["is_current_frame"] else ""))
        L.append("     J1 装得下吗      : 占位并集 原位=%s (外溢 X+%0.2f/Y+%0.2f, 余量 X%0.2f/Y%0.2f) · 尺寸包络=%s | "
                 "J_SOM 承载区 原位=%s (外溢 X+%0.2f/Y+%0.2f) · 尺寸包络=%s (宽余 %+0.2f / 高差 %+0.2f)"
                 % ("装得下" if pf["fit_all"]["as_is"] else "装不下",
                    pf["fit_all"]["overflow_x"], pf["fit_all"]["overflow_y"],
                    pf["fit_all"]["delta_w"], pf["fit_all"]["delta_h"],
                    "装得下" if pf["fit_all"]["envelope"] else "装不下",
                    "装得下" if pf["fit_som"]["as_is"] else "装不下",
                    pf["fit_som"]["overflow_x"], pf["fit_som"]["overflow_y"],
                    "装得下" if pf["fit_som"]["envelope"] else "装不下",
                    pf["fit_som"]["delta_w"], pf["fit_som"]["delta_h"]))
        L.append("     J2 层数/板厚一致 : %s (层数 %d vs %d · 板厚 %0.2f vs %s)"
                 % ("一致" if (pf["layers_ok"] and pf["thickness_ok"]) else "★不一致★",
                    pf["layers"], b["copper_layer_count"], pf["thickness_mm"], _f(b["thickness"])))
        L.append("     J3 形态一致吗    : %s (帧隐含 %s / 现役板 %s)"
                 % ("一致" if pf["form_ok"] else "★换架构★", pf["frame_form"], b["form"]))
        L.append("     ★J5 最终判决    : %s" % pf["verdict"])
        for r in pf["reasons"]:
            L.append("        · %s" % r)

    L.append("")
    L.append("【§5 结构侧口径交叉核对 (只读 %s)】" % GEOM_REL)
    m = rep["mech"]
    if not m.get("present"):
        L.append("  ★文件不在*")
    else:
        L.append("  §1 板框口径      : 板长 %s mm × 板宽 %s mm · 板厚 %s mm · %s 层 · 主控 %s"
                 % (m.get("board_len_mm"), m.get("board_width_mm"), m.get("thickness_mm"),
                    m.get("layers_from_thk"), m.get("soc_model")))
        L.append("  RK3576 命中 %d 次 / RK3572 命中 %d 次  ⇒ 结构侧权威表的主控口径 = %s"
                 % (m["rk3576_hits"], m["rk3572_hits"], m.get("soc_model")))
        L.append("  ★口径漂移登记 (★本闸只读, 一字不改★): 主控 2026-11-02 已换 RK3572 (ISS-128/129/130), "
                 "而本表仍是 RK3576 口径")
        mech_f30a = [pf for pf in rep["per_frame"] if pf["id"] == "F30A"]
        if mech_f30a and m.get("board_len_mm") and m.get("board_width_mm"):
            pf = mech_f30a[0]
            L.append("  ★F30A 与本表一致性: 帧 %0.2f×%0.2f vs 表 %s×%s ⇒ %s"
                     % (pf["width_mm"], pf["height_mm"], m.get("board_len_mm"), m.get("board_width_mm"),
                        "一致 (F30A = 本表的 60×30 现行板框)" if
                        abs(pf["width_mm"] - float(m["board_len_mm"])) < TOL_DIM_MM and
                        abs(pf["height_mm"] - float(m["board_width_mm"])) < TOL_DIM_MM else "不一致"))
            L.append("  ★⇒ 结构侧权威表描述的是【60×30 / RK3576 SoC 直上板】= 另一种物理产品, "
                     "不是盘上那块 160×100 / RK3572-SOM 承载区的台架板")

    L.append("")
    L.append("【§6 U-1 建议默认值交叉核对 (只读 %s · ★建议·非已决定★)】" % PM_REL)
    s = rep["suggest"]
    if not s.get("present"):
        L.append("  ★pm.yaml 里读不到 iss310_main_board_frame_u1_decision (可选读, 不算失败)")
    else:
        L.append("  已落表建议默认值 指向帧 : %s" % (s.get("frame") or "★读不出★"))
        L.append("  该帧的机器判决           : %s" % (s.get("machine_verdict") or "n/a"))
        L.append("  ★口径分层提醒            : %s" % s.get("note"))

    L.append("")
    L.append("【§7 本机异常登记 (可读 · 不崩)】")
    if not rep["anomalies"]:
        L.append("  无")
    for a in rep["anomalies"]:
        L.append("  ★ %s" % a)

    L.append("")
    L.append("【§8 结论】")
    cur_pf = [pf for pf in rep["per_frame"] if pf["id"] == rep["current_frame"]][0]
    L.append("  · 现役板 = %0.2f × %0.2f mm · %d 铜层 · %0.2f mm · %d 封装 · %s"
             % (b["edge_nominal"][0], b["edge_nominal"][1], b["copper_layer_count"],
                b["thickness"], b["footprint_count"], b["form"]))
    L.append("  · 只有与现役板【同框同层同厚】的那一帧才可能让「板那一趟」= 改现役板一次 ⇒ 本机实测: %s"
             % (rep["current_frame"] if cur_pf["verdict"] == VERDICT_MODIFY else "★无★"))
    for pf in rep["per_frame"]:
        if pf["verdict"] == VERDICT_NEW:
            L.append("    · %s (%0.2f×%0.2f / %d 层 / %0.2f mm) ⇒ %s"
                     % (pf["id"], pf["width_mm"], pf["height_mm"], pf["layers"], pf["thickness_mm"], pf["verdict"]))
    L.append("  · 页尾铁律: 「板只改一次」只有在【框不变】时成立 —— 换框 = 新板第一版, 不是修一次")
    L.append("=" * W)
    return "\n".join(L)


# ---------------------------------------------------------------- 自测

PROTECTED_REL = [
    os.path.join("HW", "PCB", "demo_mainboard.kicad_pcb"),
    os.path.join("HW", "PCB", "BOARD_FRAME_CALIBER.md"),
    os.path.join("MECH", "BOARD_GEOM_30MM.md"),
    os.path.join("MECH", "check_board_frame_freeze_gate.py"),
    os.path.join("MECH", "board_frame_feasibility.py"),
    os.path.join("MECH", "pinset2_mech_check.py"),
]


def _md5(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def _mtime(path):
    return os.stat(path).st_mtime


def _snapshot(root):
    snap = {}
    for rel in PROTECTED_REL:
        p = os.path.join(root, rel)
        if os.path.isfile(p):
            snap[rel] = (_md5(p), _mtime(p))
    return snap


def _mk_sandbox(root, name):
    """把闸的输入复制进沙盒目录 (返回沙盒 root)。"""
    sb = os.path.join(root, "tmp", "iss341", "selftest", name)
    if os.path.isdir(sb):
        shutil.rmtree(sb)
    for rel in [BOARD_REL, CALIBER_REL, GEOM_REL, PARAMS_REL, PM_REL]:
        src = os.path.join(root, rel)
        dst = os.path.join(sb, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if os.path.isfile(src):
            shutil.copy2(src, dst)
    return sb


def _mutate_caliber(root, old, new):
    p = os.path.join(root, CALIBER_REL)
    with open(p, "r", encoding="utf-8") as fh:
        t = fh.read()
    if old not in t:
        raise GateError("沙盒手术失败: 在 %s 里找不到待改串 %r" % (CALIBER_REL, old))
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(t.replace(old, new, 1))


def _mutate_board_ref(root, old_ref, new_ref):
    p = os.path.join(root, BOARD_REL)
    with open(p, "r", encoding="utf-8") as fh:
        t = fh.read()
    old = '(property "Reference" "%s"' % old_ref
    if old not in t:
        raise GateError("沙盒手术失败: 板里找不到 %r" % old_ref)
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(t.replace(old, '(property "Reference" "%s"' % new_ref, 1))


def _mutate_board_delete_fp(root, ref):
    """删掉指定 ref 的整个 footprint 块 (按顶层 span 切)。"""
    p = os.path.join(root, BOARD_REL)
    with open(p, "r", encoding="utf-8") as fh:
        t = fh.read()
    for (s0, s1) in top_level_spans(t):
        blk = t[s0:s1]
        if blk.startswith("(footprint") and ('(property "Reference" "%s"' % ref) in blk:
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(t[:s0] + t[s1:])
            return True
    raise GateError("沙盒手术失败: 板里找不到 footprint %r" % ref)


def _mutate_som_origins(root, mapping):
    """把 J_SOM_P1..P4 的封装原点改到 mapping 里的坐标 (用来做反向 B)。

    只改 J_SOM_* 四个块的封装级 `(at x y)`; 其余字节逐字不动。
    """
    p = os.path.join(root, BOARD_REL)
    with open(p, "r", encoding="utf-8") as fh:
        text = fh.read()
    out = []
    last = 0
    hit = 0
    for (s0, s1) in top_level_spans(text):
        blk = text[s0:s1]
        m = re.search(r'\(property "Reference" "(J_SOM_P\d)"', blk)
        if not m:
            continue
        ref = m.group(1)
        if ref not in mapping:
            continue
        nx, ny = mapping[ref]
        nb, n = re.subn(r"^(\t\t\(at )([-\d.]+)( [-\d.]+)(\))", r"\g<1>%s %s\g<4>" % (nx, ny),
                        blk, count=1, flags=re.M)
        if n == 0:
            raise GateError("沙盒手术失败: %s 找不到封装级 (at ...)" % ref)
        out.append(text[last:s0])
        out.append(nb)
        last = s1
        hit += 1
    out.append(text[last:])
    if hit != len(mapping):
        raise GateError("沙盒手术失败: 只改到 %d 个 J_SOM 封装 (要 %d 个)" % (hit, len(mapping)))
    with open(p, "w", encoding="utf-8") as fh:
        fh.write("".join(out))
    return True


def run_selftest(root):
    results = []
    before = _snapshot(root)

    def check(cid, title, ok, detail):
        results.append({"id": cid, "title": title, "ok": bool(ok), "detail": detail})

    # ---------- T1 正向: B160x100 对现役板 ⇒ 相容 ⇒ 判决「改一次」 ----------
    try:
        rep = evaluate(root)
        pf = [p for p in rep["per_frame"] if p["id"] == "B160x100"][0]
        ok = (pf["fit_all"]["as_is"] and pf["fit_som"]["as_is"] and pf["layers_ok"]
              and pf["thickness_ok"] and pf["form_ok"] and pf["verdict"] == VERDICT_MODIFY)
        check("T1", "正向: B160×100 对现役板 ⇒ 相容 ⇒ 判决「改现役板一次」", ok,
              "占位外溢 X%.2f/Y%.2f · 承载区外溢 X%.2f/Y%.2f · 层数 %s · 板厚 %s · 形态 %s · 判决=%s"
              % (pf["fit_all"]["overflow_x"], pf["fit_all"]["overflow_y"],
                 pf["fit_som"]["overflow_x"], pf["fit_som"]["overflow_y"],
                 "一致" if pf["layers_ok"] else "不一致", "一致" if pf["thickness_ok"] else "不一致",
                 "一致" if pf["form_ok"] else "换架构", pf["verdict"]))
    except Exception as exc:
        check("T1", "正向: B160×100 对现役板 ⇒ 相容 ⇒ 判决「改现役板一次」", False, "异常: %s" % exc)

    # ---------- T2 反向 A: F30A 板高 30→60 ⇒ 承载区尺寸包络判据必须翻 ----------
    try:
        sb = _mk_sandbox(root, "T2_f30a_h60")
        _mutate_caliber(sb, '"height_mm": 30.0,\n      "layers": 6,',
                        '"height_mm": 60.0,\n      "layers": 6,')
        rep2 = evaluate(sb)
        pf2 = [p for p in rep2["per_frame"] if p["id"] == "F30A"][0]
        base = [p for p in rep["per_frame"] if p["id"] == "F30A"][0]
        flipped = (not base["fit_som"]["envelope"]) and pf2["fit_som"]["envelope"]
        rec_changed = (pf2["fit_som"]["delta_h"] != base["fit_som"]["delta_h"])
        ok = flipped and rec_changed
        check("T2", "反向A: F30A 板高 30→60 ⇒ 承载区「尺寸包络装得下」判据必须翻转 (证明闸在读盘面)", ok,
              "基线 尺寸包络=%s (差Y%.2f) → 改后 尺寸包络=%s (差Y%.2f) · 记录已变=%s · 注: 主判决仍为「重画新板」"
              "是正确的 (60×60 仍不是盘上那块 160×100), 详见用例 T2b"
              % (base["fit_som"]["envelope"], base["fit_som"]["delta_h"],
                 pf2["fit_som"]["envelope"], pf2["fit_som"]["delta_h"], rec_changed))
    except Exception as exc:
        check("T2", "反向A: F30A 板高 30→60 ⇒ 承载区「尺寸包络装得下」判据必须翻转", False, "异常: %s" % exc)

    # ---------- T2b 反向 A': F30A 改成 160×100/8 层/1.60 且 current_frame 指向它 ⇒ 主判决必须翻 ----------
    try:
        sb = _mk_sandbox(root, "T2b_f30a_is_board")
        _mutate_caliber(sb, '"width_mm": 60.0,\n      "height_mm": 30.0,\n      "layers": 6,\n      "thickness_mm": 1.0,',
                        '"width_mm": 160.0,\n      "height_mm": 100.0,\n      "layers": 8,\n      "thickness_mm": 1.6,')
        _mutate_caliber(sb, '"current_frame": "B160x100"', '"current_frame": "F30A"')
        rep2 = evaluate(sb)
        pf2 = [p for p in rep2["per_frame"] if p["id"] == "F30A"][0]
        pfB = [p for p in rep2["per_frame"] if p["id"] == "B160x100"][0]
        ok = (pf2["verdict"] == VERDICT_MODIFY and pfB["verdict"] == VERDICT_NEW
              and rep2["current_frame_agrees_with_board"])
        check("T2b", "反向A': F30A 改成 160×100/8层/1.60 且 current_frame→F30A ⇒ 主判决必须从「重画新板」翻成「改一次」", ok,
              "F30A 判决=%s · B160x100 判决=%s · current_frame=%s · 口径自洽=%s"
              % (pf2["verdict"], pfB["verdict"], rep2["current_frame"], rep2["current_frame_agrees_with_board"]))
    except Exception as exc:
        check("T2b", "反向A': F30A 改成 160×100/8层/1.60 且 current_frame→F30A ⇒ 主判决必须翻", False, "异常: %s" % exc)

    # ---------- T3 反向 B: 改小 J_SOM 承载区读数 ⇒ F30A 承载区判据必须翻转 ----------
    try:
        sb = _mk_sandbox(root, "T3_som_small")
        _mutate_som_origins(sb, {"J_SOM_P1": (12.0, 8.0), "J_SOM_P2": (36.0, 8.0),
                                  "J_SOM_P3": (12.0, 18.0), "J_SOM_P4": (36.0, 18.0)})
        rep2 = evaluate(sb)
        pf2 = [p for p in rep2["per_frame"] if p["id"] == "F30A"][0]
        base = [p for p in rep["per_frame"] if p["id"] == "F30A"][0]
        flipped = (not base["fit_som"]["as_is"]) and pf2["fit_som"]["as_is"]
        ok = flipped
        check("T3", "反向B: 把 J_SOM 承载区坐标改小 ⇒ F30A 的「承载区原位装得下」判据必须翻转", ok,
              "基线 承载区原位=%s (外溢 X%.2f/Y%.2f) → 改后 承载区原位=%s (外溢 X%.2f/Y%.2f) · "
              "承载区包络尺寸 %.2f×%.2f → %.2f×%.2f"
              % (base["fit_som"]["as_is"], base["fit_som"]["overflow_x"], base["fit_som"]["overflow_y"],
                 pf2["fit_som"]["as_is"], pf2["fit_som"]["overflow_x"], pf2["fit_som"]["overflow_y"],
                 base["fit_som"]["w"], base["fit_som"]["h"], pf2["fit_som"]["w"], pf2["fit_som"]["h"]))
    except Exception as exc:
        check("T3", "反向B: 把 J_SOM 承载区坐标改小 ⇒ F30A 承载区判据必须翻转", False, "异常: %s" % exc)

    # ---------- T4 反向 C: 某帧 layers 8→6 ⇒ 层数不一致必须报出来 ----------
    try:
        sb = _mk_sandbox(root, "T4_layers")
        _mutate_caliber(sb, '"B160x100": {\n      "name": "160×100 台架板帧",\n      "width_mm": 160.0,\n      "height_mm": 100.0,\n      "layers": 8,',
                        '"B160x100": {\n      "name": "160×100 台架板帧",\n      "width_mm": 160.0,\n      "height_mm": 100.0,\n      "layers": 6,')
        rep2 = evaluate(sb)
        pf2 = [p for p in rep2["per_frame"] if p["id"] == "B160x100"][0]
        base = [p for p in rep["per_frame"] if p["id"] == "B160x100"][0]
        flipped = base["layers_ok"] and not pf2["layers_ok"]
        ok = flipped and pf2["verdict"] == VERDICT_NEW and any("层数不一致" in r for r in pf2["reasons"])
        check("T4", "反向C: 把 B160×100 的 layers 从 8 改成 6 ⇒ 「层数不一致」必须报出来且判决翻成「重画新板」", ok,
              "基线 层数一致=%s · 改后 层数一致=%s · 判决 %s → %s · 理由含「层数不一致」=%s"
              % (base["layers_ok"], pf2["layers_ok"], base["verdict"], pf2["verdict"],
                 any("层数不一致" in r for r in pf2["reasons"])))
    except Exception as exc:
        check("T4", "反向C: 把 B160×100 的 layers 从 8 改成 6 ⇒ 层数不一致必须报出来", False, "异常: %s" % exc)

    # ---------- T5 反向 D: current_frame 改成 F30A ⇒ 现役帧相关判据必须翻转 ----------
    try:
        sb = _mk_sandbox(root, "T5_current_frame")
        _mutate_caliber(sb, '"current_frame": "B160x100"', '"current_frame": "F30A"')
        rep2 = evaluate(sb)
        pfB2 = [p for p in rep2["per_frame"] if p["id"] == "B160x100"][0]
        pfF2 = [p for p in rep2["per_frame"] if p["id"] == "F30A"][0]
        baseB = [p for p in rep["per_frame"] if p["id"] == "B160x100"][0]
        flipped = (baseB["is_current_frame"] and not pfB2["is_current_frame"]
                   and pfF2["is_current_frame"]
                   and rep["current_frame_agrees_with_board"] and not rep2["current_frame_agrees_with_board"]
                   and baseB["verdict"] == VERDICT_MODIFY and pfB2["verdict"] == VERDICT_NEW)
        check("T5", "反向D: 把 cal:FRAMES.current_frame 改成 F30A ⇒ 现役帧相关判据必须翻转", flipped,
              "B160x100 现役帧 True→%s (判决 %s → %s) · F30A 现役帧 →%s · 口径自洽 %s → %s"
              % (pfB2["is_current_frame"], baseB["verdict"], pfB2["verdict"], pfF2["is_current_frame"],
                 rep["current_frame_agrees_with_board"], rep2["current_frame_agrees_with_board"]))
    except Exception as exc:
        check("T5", "反向D: 把 cal:FRAMES.current_frame 改成 F30A ⇒ 现役帧相关判据必须翻转", False, "异常: %s" % exc)

    # ---------- T6 反向 E-1: 改名一个封装 (⇒ 重复位号) ⇒ 闸不许崩, 给可读报错 ----------
    try:
        sb = _mk_sandbox(root, "T6e1_rename")
        _mutate_board_ref(sb, "J_SOM_P4", "J_SOM_P1")
        try:
            evaluate(sb)
            ok = False
            detail = "★闸没有报错★ (重复位号 J_SOM_P1 未被抓住)"
        except GateError as exc:
            ok = True
            detail = "闸抛 GateError (可读): %s" % exc
        except Exception as exc:
            ok = False
            detail = "★闸抛了裸 Traceback (不可接受): %r" % exc
        check("T6e1", "反向E-1: 把一个封装改名成已有位号 ⇒ 闸不许崩, 必须给出可读报错", ok, detail)
    except Exception as exc:
        check("T6e1", "反向E-1: 改名 ⇒ 可读报错", False, "异常: %s" % exc)

    # ---------- T6 反向 E-2: 删掉一个封装 ⇒ 闸不许崩, 必须报出封装数异常 ----------
    try:
        sb = _mk_sandbox(root, "T6e2_delete")
        _mutate_board_delete_fp(sb, "J_SOM_P4")
        try:
            rep2 = evaluate(sb)
            hit = any("封装数" in a for a in rep2["anomalies"])
            ok = hit and rep2["board"]["footprint_count"] == EXPECTED_FOOTPRINTS - 1
            detail = ("闸正常跑完 · 封装数 %d · 异常登记: %s"
                      % (rep2["board"]["footprint_count"], "; ".join(rep2["anomalies"]) or "无"))
        except GateError as exc:
            ok = True
            detail = "闸抛 GateError (可读): %s" % exc
        except Exception as exc:
            ok = False
            detail = "★闸抛了裸 Traceback (不可接受): %r" % exc
        check("T6e2", "反向E-2: 删掉一个封装 ⇒ 闸不许崩, 必须报出封装数异常 (185 ≠ 基线 186)", ok, detail)
    except Exception as exc:
        check("T6e2", "反向E-2: 删掉一个封装 ⇒ 可读报错", False, "异常: %s" % exc)

    # ---------- T7 正向补充: P60x15 ⇒ 不相容, 差值 mm 给对 ----------
    try:
        pf = [p for p in rep["per_frame"] if p["id"] == "P60x15"][0]
        exp_ovx = round(rep["board"]["pad_union_bbox"][2] - 60.0, 4)
        ok = (not pf["fit_all"]["as_is"] and not pf["fit_som"]["as_is"]
              and abs(pf["fit_all"]["overflow_x"] - exp_ovx) < 1e-6
              and pf["verdict"] == VERDICT_NEW)
        check("T7", "正向补充: P60×15 ⇒ 不相容, 且外溢 mm 读数与手算一致", ok,
              "占位并集外溢 X+%.2f/Y+%.2f (手算 X+%.2f) · 承载区包络差 X%.2f/Y%.2f · 判决=%s"
              % (pf["fit_all"]["overflow_x"], pf["fit_all"]["overflow_y"], exp_ovx,
                 pf["fit_som"]["delta_w"], pf["fit_som"]["delta_h"], pf["verdict"]))
    except Exception as exc:
        check("T7", "正向补充: P60×15 ⇒ 不相容", False, "异常: %s" % exc)

    # ---------- T8 真源自证: 闸读到的板实测值 == main 报的 6 条事实 ----------
    try:
        b = rep["board"]
        facts = [
            ("现役板板框 = 160 × 100 mm", (abs(b["edge_nominal"][0] - 160.0) < 1e-6 and abs(b["edge_nominal"][1] - 100.0) < 1e-6),
             "%0.2f × %0.2f" % b["edge_nominal"]),
            ("现役板 = 8 铜层", b["copper_layer_count"] == 8, str(b["copper_layer_count"])),
            ("现役板 = 1.60mm", b["thickness"] is not None and abs(b["thickness"] - 1.6) < 1e-9, str(b["thickness"])),
            ("现役板 = 186 封装", b["footprint_count"] == 186, str(b["footprint_count"])),
            ("SoM 承载区 = 53.80 × 46.78 mm", (abs((b["som_union_bbox"][2] - b["som_union_bbox"][0]) - 53.80) < 1e-6
                                          and abs((b["som_union_bbox"][3] - b["som_union_bbox"][1]) - 46.78) < 1e-6),
             "%0.2f × %0.2f" % (b["som_union_bbox"][2] - b["som_union_bbox"][0],
                               b["som_union_bbox"][3] - b["som_union_bbox"][1])),
            ("现役帧 = B160x100", rep["current_frame"] == "B160x100", rep["current_frame"]),
        ]
        ok = all(f[1] for f in facts)
        check("T8", "真源自证: 闸读到的板实测值 == main §0.1 报的 6 条事实 (逐条)", ok,
              "; ".join("%s⇒%s(%s)" % (f[0], "对" if f[1] else "错", f[2]) for f in facts))
    except Exception as exc:
        check("T8", "真源自证: 6 条事实", False, "异常: %s" % exc)

    # ---------- T9 真件零改动自证 ----------
    after = _snapshot(root)
    changed = [k for k in before if before.get(k) != after.get(k)]
    check("T9", "零写板 / 零改既有 MECH+HW 文件自证 (自测前后 md5+mtime 逐字节对拍)", not changed,
          "受保护文件 %d 件 · 变化: %s" % (len(before), ", ".join(changed) if changed else "无"))

    n_ok = sum(1 for r in results if r["ok"])
    print("=" * 104)
    print("ISS-341 · 相容性判定闸 · 自测 (%d 条用例)" % len(results))
    print("=" * 104)
    for r in results:
        print("  %-6s %s %s" % (r["id"], "✅ 与预期一致" if r["ok"] else "❌ 与预期不一致", r["title"]))
        print("         %s" % r["detail"])
    print("-" * 104)
    print("★结论: %d/%d 条用例与预期一致" % (n_ok, len(results)))
    print("=" * 104)
    if n_ok == len(results):
        print("ALL TESTS PASS")
        return 0
    print("SELFTEST FAILED")
    return 2


# ---------------------------------------------------------------- main

def main(argv=None):
    ap = argparse.ArgumentParser(description="ISS-341 U-1 板框三候选 × 现役板 相容性机器判定闸 (只读)")
    ap.add_argument("--selftest", action="store_true", help="跑自测 (末行 ALL TESTS PASS)")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    ap.add_argument("--root", default=DEFAULT_ROOT, help="项目根目录 (沙盒用)")
    ap.add_argument("--expect-footprints", type=int, default=EXPECTED_FOOTPRINTS,
                    help="现役板封装数基线 (默认 %d)" % EXPECTED_FOOTPRINTS)
    ap.add_argument("--no-pm", action="store_true", help="不读 pm.yaml 的建议默认值 (可选读)")
    args = ap.parse_args(argv)

    root = os.path.abspath(args.root)
    try:
        if args.selftest:
            return run_selftest(root)
        rep = evaluate(root, expect_footprints=args.expect_footprints, read_pm=not args.no_pm)
    except GateError as exc:
        sys.stderr.write("GATE-ERROR: %s\n" % exc)
        return 3
    except Exception as exc:  # 绝不留裸 Traceback
        sys.stderr.write("GATE-ERROR: 未预期异常 %r (根目录 %s)\n" % (exc, root))
        return 3

    if args.json:
        out = {
            "current_frame": rep["current_frame"],
            "current_frame_agrees_with_board": rep["current_frame_agrees_with_board"],
            "anomalies": rep["anomalies"],
            "board": {k: v for k, v in rep["board"].items() if k not in ("footprints", "_text")},
            "per_frame": rep["per_frame"],
            "suggest": rep["suggest"],
            "mech": rep["mech"],
        }
        print(json.dumps(out, ensure_ascii=False, indent=2, default=str))
        return 0 if rep["current_frame_agrees_with_board"] and not rep["anomalies"] else 2

    print(render(rep))
    return 0 if (rep["current_frame_agrees_with_board"] and not rep["anomalies"]) else 2


if __name__ == "__main__":
    sys.exit(main())
