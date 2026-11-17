#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_onepass_struct_crosscheck.py —— ★★【ISS-290 · 「板只改一次」那一趟 · 结构侧最后一道交叉核对 · 机器闸】★★

★★★**★这个闸守的是什么★**★★
  「板只改一次」那一趟, 结构侧最后两个【没人交叉验过】的接口:
    ① S6 的 20 个目标落位 × MECH 保留区 —— hw-lead 的闸 (`HW/check_board_frame_caliber.py`) 只查帧标签/缺位/重叠/出界,
       ★**不查结构保留区**; MECH 自己的闸 (M1~M5) 只查 MECH 自洽, ★**不碰 S6 目标落位** ⇒ 两边各自绿, 合起来可能撞
       ⇒ 那一趟 S6 一跑就撞 ⇒ 板 md5 变第二次。本闸 N2/N3/N4 就是补这段没人验的缝。
    ② 座体类器件三方对照 (BOM/网表 vs 板上 land pattern vs 结构占位) —— N5
    ③ `corner_radius` 3.0 vs 0.0 的贴角 keep-out 口径 —— 机器块 `corner` + §6

  闸的六条:
    N1  ★**帧标签** —— S6 的 20 个目标位逐个带帧标签, 且帧 = `B160x100` (漏标一条 / 错帧 ⇒ 红)
    N2  ★**SoM 承载区零冲突** —— 20 个目标位 (按目标原点 + 该 ref 的 footprint 外形) 与 SoM 承载区
          (焊盘实体 + 封装外形 + 保守包络) 零冲突; 且规格页里的 SoM 三个口径必须与板读一致 (防文档漂移)
    N3  ★**两条开口** —— 20 个目标位不得落在检修口开口 / 调试口开口矩形内 —— ★**两条分别验, 不许合并验**★
          (机器块里必须恰好两条开口; 合并成一条 ⇒ 红); 每条开口按 h 三档逐档验
    N4  ★**必清空区净距** —— 20 个目标位到两条「座体必须清空区」的最小净距 ≥ ★**CRIT (0.60, 取自既有 MECH 判据, 不许新造)**★
          + 规格页里的 `consts.crit` 必须与既有判据逐字相等 (改了 ⇒ 红)
    N5  ★**座体三方对照表完整** —— §4 表里每个 `J_*` 行的四个字段 (BOM 规格 / 板读 land / 结构占位 / verdict) 都不许为空
          (★不许用「待定」糊过去★)
    N6  ★**受保护 5 件 md5 逐字节不变** (板 / `.kicad_pro` / 网表 / 脚表 / BOM)

  ★**只读 import MECH/check_board_frame_coords.py** ⇒ 阈值 (CRIT / EDGE_KEEPOUT / OPEN_X / PROTECTED) 零漂移,
    ★**本闸是【新建】文件, 一个字不改既有 MECH 判据脚本**★ ⇒ ★**板解析器自带 (自写 s-expr 解析, 不抄任何交卷单)**★

用法:
    python3 MECH/check_onepass_struct_crosscheck.py            # rc=0 = 全绿
    python3 MECH/check_onepass_struct_crosscheck.py --json     # 机器读
    python3 MECH/check_onepass_struct_crosscheck.py --selftest # rc=0 = 反向用例全抓到 (★沙盒副本上跑, 真件一个字节不碰★)
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, ".."))

SPEC_REL = os.path.join("MECH", "BOARD_ONEPASS_STRUCT_CROSSCHECK.md")
CALIB_REL = os.path.join("HW", "PCB", "BOARD_FRAME_CALIBER.md")
PCB_REL = os.path.join("HW", "PCB", "demo_mainboard.kicad_pcb")
MACH_BEGIN = "<!-- MACHINE-BLOCK-BEGIN -->"
MACH_END = "<!-- MACHINE-BLOCK-END -->"

FRAME = "B160x100"
N_S6 = 20

# ★受保护 5 件 (★板/.kicad_pro 取自既有闸 CFC.PROTECTED ⇒ 零漂移; 网表/脚表/BOM 取自 ISS-290 任务书基线★) ★
PROTECTED_LEDGER_MD5 = {
    os.path.join("HW", "netlist_v1.csv"): "37f62ac3f0b81d92ca7d48fdea717f07",
    os.path.join("HW", "netlist_v1_pins.csv"): "a4270120454aedf7a23c92cd8985c8a6",
    os.path.join("HW", "BOM_v1.csv"): "5d02bece9477ffce5fbe0193c7d5cce4",
}

# ★§4 三方对照表必须覆盖的位号 (★至少 J_DEBUG/J_UART/J_USB_C/J_CHG/J_SOM_P1..P4★) ★
CONN_REFS = ["J_DEBUG", "J_UART", "J_USB_C", "J_CHG",
             "J_SOM_P1", "J_SOM_P2", "J_SOM_P3", "J_SOM_P4"]
# ★verdict 不许糊过去的词 ★
FORBIDDEN_VERDICT = ("待定", "TBD", "tbd", "-", "—", "?", "？", "未知", "N/A")


# ==================================================================================================
# ★只读 import 既有闸 (阈值零漂移) ★
# ==================================================================================================
def load_cfc():
    path = os.path.join(PROJ, "MECH", "check_board_frame_coords.py")
    spec = importlib.util.spec_from_file_location("cfc_iss290_readonly", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


CFC = load_cfc()


# ==================================================================================================
# ★自写 s-expr 板解析器 (★只读 · 不抄任何交卷单★) ★
# ==================================================================================================
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


def _rot(x, y, deg):
    r = math.radians(deg)
    c, s = math.cos(r), math.sin(r)
    return (x * c + y * s, -x * s + y * c)


def _bbox(pts):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return (min(xs), min(ys), max(xs), max(ys))


def _rect_pts(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


class Board(object):
    """★只读 kicad_pcb ⇒ 封装/焊盘/座体外形/板框★"""

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
                lay = _v(_kid(node, "layer"), 1, "")
                if lay == "Edge.Cuts":
                    self.edge.append((_f(st, 1), _f(st, 2), _f(en, 1), _f(en, 2)))

    @staticmethod
    def _fp(node):
        at = _kid(node, "at")
        props = {}
        for p in _kids(node, "property"):
            props[_v(p, 1, "")] = _v(p, 2, "")
        fp = {"ref": props.get("Reference", ""), "value": props.get("Value", ""),
              "x": _f(at, 1, 0.0), "y": _f(at, 2, 0.0), "rot": _f(at, 3, 0.0) or 0.0,
              "pads": [], "fab": [], "crtyd": []}
        for pad in _kids(node, "pad"):
            pat = _kid(pad, "at")
            sz = _kid(pad, "size")
            fp["pads"].append({"num": _v(pad, 1, ""), "type": _v(pad, 2, ""),
                               "px": _f(pat, 1, 0.0), "py": _f(pat, 2, 0.0),
                               "prot": _f(pat, 3, 0.0) or 0.0,
                               "sw": _f(sz, 1, 0.0), "sh": _f(sz, 2, 0.0)})
        for name, bucket in (("fp_line", "fab"), ("fp_rect", "fab")):
            for g in _kids(node, name):
                if _v(_kid(g, "layer"), 1, "") != "F.Fab":
                    continue
                st, en = _kid(g, "start"), _kid(g, "end")
                if name == "fp_rect":
                    fp[bucket].append(_rect_pts(_f(st, 1), _f(st, 2), _f(en, 1), _f(en, 2)))
                else:
                    fp[bucket].append([(_f(st, 1), _f(st, 2)), (_f(en, 1), _f(en, 2))])
        for g in _kids(node, "fp_rect"):
            if _v(_kid(g, "layer"), 1, "") != "F.CrtYd":
                continue
            st, en = _kid(g, "start"), _kid(g, "end")
            fp["crtyd"].append(_rect_pts(_f(st, 1), _f(st, 2), _f(en, 1), _f(en, 2)))
        return fp

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

    @staticmethod
    def local_envelope(fp):
        """★封装局部坐标下 (F.Fab 外形 ∪ 焊盘铜箔) 外框 = 落位后的外形包络★"""
        pts = []
        for poly in fp["fab"]:
            pts.extend(poly)
        for p in fp["pads"]:
            w, h = p["sw"], p["sh"]
            if abs((p["prot"] + fp["rot"]) % 180.0 - 90.0) < 1e-6:
                w, h = h, w
            pts.extend(_rect_pts(p["px"] - w / 2.0, p["py"] - h / 2.0,
                                 p["px"] + w / 2.0, p["py"] + h / 2.0))
        return _bbox(pts) if pts else None

    @staticmethod
    def local_fab(fp):
        pts = []
        for poly in fp["fab"]:
            pts.extend(poly)
        return _bbox(pts) if pts else None

    @staticmethod
    def envelope_at(fp, tx, ty):
        loc = Board.local_envelope(fp)
        if loc is None:
            return None
        pts = []
        for (lx, ly) in _rect_pts(loc[0], loc[1], loc[2], loc[3]):
            dx, dy = _rot(lx, ly, fp["rot"])
            pts.append((tx + dx, ty + dy))
        return _bbox(pts)

    @staticmethod
    def fab_at(fp, tx, ty):
        loc = Board.local_fab(fp)
        if loc is None:
            return None
        pts = []
        for (lx, ly) in _rect_pts(loc[0], loc[1], loc[2], loc[3]):
            dx, dy = _rot(lx, ly, fp["rot"])
            pts.append((tx + dx, ty + dy))
        return _bbox(pts)

    def by_ref(self):
        d = {}
        for fp in self.fps:
            if fp["ref"]:
                d.setdefault(fp["ref"], fp)
        return d

    def edge_bbox(self):
        if not self.edge:
            return None
        pts = []
        for (x0, y0, x1, y1) in self.edge:
            pts.extend([(x0, y0), (x1, y1)])
        return _bbox(pts)

    def som_zones(self, refs=("J_SOM_P1", "J_SOM_P2", "J_SOM_P3", "J_SOM_P4"),
                  fab_stroke_half=0.05):
        """★SoM 承载区三口径 (焊盘铜箔并集 / 座体 F.Fab 并集 / 保守包络) —— 板读★"""
        by = self.by_ref()
        copper, fab = [], []
        for r in refs:
            fp = by.get(r)
            if fp is None:
                continue
            for (_, x0, y0, x1, y1) in Board.pad_boxes(fp):
                copper.extend([(x0, y0), (x1, y1)])
            loc = Board.local_fab(fp)
            if loc is None:
                continue
            for (lx, ly) in _rect_pts(loc[0], loc[1], loc[2], loc[3]):
                dx, dy = _rot(lx, ly, fp["rot"])
                fab.extend([(fp["x"] + dx, fp["y"] + dy)])
        if not copper or not fab:
            return None
        cb, fb = _bbox(copper), _bbox(fab)
        env = _bbox(list(copper) + [(fb[0] - fab_stroke_half, fb[1] - fab_stroke_half),
                                    (fb[2] + fab_stroke_half, fb[3] + fab_stroke_half)])
        return {"copper": cb, "fab": fb, "env": env}


def rect_overlap(a, b):
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b
    ox = min(ax1, bx1) - max(ax0, bx0)
    oy = min(ay1, by1) - max(ay0, by0)
    if ox <= 0 or oy <= 0:
        return 0.0
    return ox * oy


def rect_dist(a, b):
    """★两矩形最小间隙 (重叠时返回负穿透深度)★"""
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b
    dx = max(bx0 - ax1, ax0 - bx1)
    dy = max(by0 - ay1, ay0 - by1)
    if dx >= 0 and dy >= 0:
        return max(dx, dy)
    if dx >= 0 or dy >= 0:
        return max(dx, dy)
    ox = min(ax1, bx1) - max(ax0, bx0)
    oy = min(ay1, by1) - max(ay0, by0)
    return -min(ox, oy)


# ==================================================================================================
# 规格页 / 校准页 读取
# ==================================================================================================
def read_spec(root):
    path = os.path.join(root, SPEC_REL)
    if not os.path.exists(path):
        raise SystemExit(f"[check_onepass_struct_crosscheck] 找不到规格页: {path}")
    text = open(path, "r", encoding="utf-8").read()
    b, e = text.find(MACH_BEGIN), text.find(MACH_END)
    if b < 0 or e < 0:
        raise SystemExit("[check_onepass_struct_crosscheck] 规格页缺机器块标记")
    m = re.search(r"```json\n(.*?)\n```", text[b:e], re.S)
    if not m:
        raise SystemExit("[check_onepass_struct_crosscheck] 机器块不是 ```json 围栏")
    data = json.loads(m.group(1))
    data["_text"] = text
    return data


def read_s6_targets(root):
    path = os.path.join(root, CALIB_REL)
    if not os.path.exists(path):
        raise SystemExit(f"[check_onepass_struct_crosscheck] 找不到校准页: {path}")
    text = open(path, "r", encoding="utf-8").read()
    if "```json cal:S6_TARGETS" not in text:
        raise SystemExit("[check_onepass_struct_crosscheck] 校准页缺 cal:S6_TARGETS 块")
    seg = text.split("```json cal:S6_TARGETS", 1)[1].split("```", 1)[0]
    return json.loads(seg[seg.index("{"):])


def md5_of(path):
    import hashlib
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def _md_table_rows(text, header_needles):
    """★抠出 markdown 表里符合表头的那些行 (返回 list[list[str]])★"""
    rows = []
    lines = text.split("\n")
    in_tbl = False
    for ln in lines:
        if ln.startswith("|"):
            if all(n in ln for n in header_needles):
                in_tbl = True
                continue
            if in_tbl:
                if re.match(r"^\|[\s:|-]+\|$", ln.strip()):
                    continue
                cells = [c.strip() for c in ln.strip().strip("|").split("|")]
                rows.append(cells)
        else:
            in_tbl = False
    return rows


# ==================================================================================================
# N1 · 帧标签
# ==================================================================================================
def check_n1(root, spec, calib):
    errs, rows = [], []
    targets = calib.get("targets") or []
    refs = [t.get("ref") for t in targets]
    if len(targets) != N_S6:
        errs.append(f"N1 S6 目标位条数 = {len(targets)} (期望 {N_S6})")
    if len(set(refs)) != len(refs):
        errs.append("N1 S6 目标位 ref 有重复")
    if calib.get("frame") != FRAME:
        errs.append(f"N1 校准页 cal:S6_TARGETS 顶层 frame = {calib.get('frame')} (期望 {FRAME})")
    for t in targets:
        f = t.get("frame")
        ok = (f == FRAME)
        rows.append({"ref": t.get("ref"), "frame": f, "ok": ok})
        if not ok:
            errs.append(f"N1 S6 目标位 {t.get('ref')} 的帧标签 = {f!r} (期望 {FRAME!r})")
    # ★规格页 §3 表: 20 行逐个带帧标签 ★
    tbl = _md_table_rows(spec["_text"], ["`ref`", "`frame`", "`target_x`", "`verdict`"])
    tmap = {r[0].strip("`"): r for r in tbl}
    for t in targets:
        ref = t.get("ref")
        if ref not in tmap:
            errs.append(f"N1 规格页 §3 表缺 S6 目标位 {ref}")
            continue
        cells = tmap[ref]
        if len(cells) < 3 or cells[1].strip("`") != FRAME:
            errs.append(f"N1 规格页 §3 表 {ref} 的帧标签 = {cells[1] if len(cells) > 1 else '<缺>'} (期望 {FRAME})")
    # ★机器块 s6_rows 逐个带帧标签 + 与校准页 ref 集合一致 ★
    s6 = spec.get("s6_rows") or []
    if len(s6) != N_S6:
        errs.append(f"N1 机器块 s6_rows 条数 = {len(s6)} (期望 {N_S6})")
    for r in s6:
        if r.get("frame") != FRAME:
            errs.append(f"N1 机器块 s6_rows {r.get('ref')} 的 frame = {r.get('frame')!r} (期望 {FRAME!r})")
    if set(r.get("ref") for r in s6) != set(refs):
        errs.append("N1 机器块 s6_rows 的 ref 集合与校准页 cal:S6_TARGETS 不一致")
    return {"ok": not errs, "errs": errs, "rows": rows, "n_targets": len(targets)}


# ==================================================================================================
# N2 · SoM 承载区零冲突
# ==================================================================================================
def check_n2(root, spec, calib, board):
    errs, rows = [], []
    by = board.by_ref()
    zones = {z["id"]: z for z in (spec.get("zones") or [])}
    som_ids = ["SOM-COPPER", "SOM-FAB", "SOM-ENV"]
    # --- 规格页里的 SoM 三口径必须与板读一致 (防文档漂移) ---
    read = board.som_zones()
    for zid, key in (("SOM-COPPER", "copper"), ("SOM-FAB", "fab"), ("SOM-ENV", "env")):
        z = zones.get(zid)
        if z is None:
            errs.append(f"N2 机器块缺保留区 {zid}")
            continue
        g = z.get("geometry") or {}
        doc = (float(g.get("x0", 1e9)), float(g.get("x1", -1e9)),
               float(g.get("y0", 1e9)), float(g.get("y1", -1e9)))
        rd_ = read[key]
        for a, b, nm in ((doc[0], rd_[0], "x0"), (doc[1], rd_[2], "x1"),
                         (doc[2], rd_[1], "y0"), (doc[3], rd_[3], "y1")):
            if abs(a - b) > 0.002:
                errs.append(f"N2 规格页 {zid}.{nm} = {a} 与板读 {b} 不一致 (文档漂移)")
    # --- 20 个目标位零冲突 ---
    for t in calib.get("targets") or []:
        ref = t.get("ref")
        tx, ty = float(t.get("x")), float(t.get("y"))
        fp = by.get(ref)
        if fp is None:
            errs.append(f"N2 S6 目标位 {ref} 在板上找不到封装")
            continue
        env = Board.envelope_at(fp, tx, ty)
        hits = []
        for zid in som_ids:
            z = zones.get(zid)
            if z is None:
                continue
            g = z.get("geometry") or {}
            r = (float(g["x0"]), float(g["x1"]), float(g["y0"]), float(g["y1"]))
            if rect_overlap(env, r) > 1e-9:
                hits.append(zid)
        rows.append({"ref": ref, "envelope": [round(v, 4) for v in env], "hits": hits})
        if hits:
            errs.append(f"N2 S6 目标位 {ref} 落进 SoM 承载区 {hits}")
    # --- 与机器块 s6_rows 的 hit_zones 对账 ---
    s6map = {r.get("ref"): r for r in (spec.get("s6_rows") or [])}
    for row in rows:
        r = s6map.get(row["ref"])
        if r is None:
            continue
        doc_hits = [h for h in (r.get("hit_zones") or []) if h in som_ids]
        if sorted(doc_hits) != sorted(row["hits"]):
            errs.append(f"N2 {row['ref']} 的 hit_zones (机器块 {doc_hits}) 与复算 {row['hits']} 不一致")
    return {"ok": not errs, "errs": errs, "rows": rows}


# ==================================================================================================
# N3 · 两条开口 (★两条分别验, 不许合并验★)
# ==================================================================================================
def check_n3(root, spec, calib, board):
    errs, rows = [], []
    by = board.by_ref()
    openings = spec.get("openings") or []
    ids = [o.get("id") for o in openings]
    if len(openings) != 2:
        errs.append(f"N3 机器块开口条数 = {len(openings)} (期望恰好 2 条: 检修口 + 调试口; "
                    f"合并成一条 ⇒ 红)")
    if sorted(ids) != ["PORT_OPEN_DEBUG", "PORT_OPEN_UART"]:
        errs.append(f"N3 机器块开口 id = {ids} (期望 ['PORT_OPEN_DEBUG','PORT_OPEN_UART'] 两条分开)")
    for o in openings:
        tiers = o.get("tiers") or {}
        if not tiers:
            errs.append(f"N3 开口 {o.get('id')} 没有 h 三档")
    # --- 20 个目标位 vs 每条开口 (逐档, 分别验) ---
    for o in openings:
        for h, t in (o.get("tiers") or {}).items():
            r = t.get("open_rect") or {}
            rect = (float(r["x0"]), float(r["x1"]), float(r["y0"]), float(r["y1"]))
            for tg in calib.get("targets") or []:
                ref = tg.get("ref")
                fp = by.get(ref)
                if fp is None:
                    continue
                env = Board.envelope_at(fp, float(tg.get("x")), float(tg.get("y")))
                if rect_overlap(env, rect) > 1e-9:
                    errs.append(f"N3 S6 目标位 {ref} 落进 {o.get('id')} 的 h={h} 开口 {rect}")
                    rows.append({"opening": o.get("id"), "h": h, "ref": ref, "rect": rect})
    return {"ok": not errs, "errs": errs, "rows": rows,
            "n_openings": len(openings), "ids": ids}


# ==================================================================================================
# N4 · 必清空区净距 ≥ CRIT
# ==================================================================================================
def check_n4(root, spec, calib, board):
    errs, rows = [], []
    by = board.by_ref()
    crit = CFC.CRIT
    spec_crit = (spec.get("consts") or {}).get("crit")
    if spec_crit is None or abs(float(spec_crit) - crit) > 1e-9:
        errs.append(f"N4 规格页 consts.crit = {spec_crit} 与既有 MECH 判据 CRIT = {crit} 不一致 "
                    f"(★CRIT 不许新造 / 不许改小★)")
    mcs = spec.get("must_clear") or []
    if len(mcs) != 2:
        errs.append(f"N4 机器块 must_clear 条数 = {len(mcs)} (期望恰好 2 条)")
    for mc in mcs:
        r = mc.get("rect") or {}
        rect = (float(r["x0"]), float(r["x1"]), float(r["y0"]), float(r["y1"]))
        for tg in calib.get("targets") or []:
            ref = tg.get("ref")
            fp = by.get(ref)
            if fp is None:
                continue
            env = Board.envelope_at(fp, float(tg.get("x")), float(tg.get("y")))
            d = rect_dist(env, rect)
            rows.append({"mc": mc.get("id"), "ref": ref, "dist": round(d, 4)})
            if d < crit - 1e-9:
                errs.append(f"N4 S6 目标位 {ref} 到必须清空区 {mc.get('id')} 的净距 {d:.4f} < CRIT {crit}")
    return {"ok": not errs, "errs": errs, "rows": rows, "crit": crit}


# ==================================================================================================
# N5 · 座体三方对照表完整
# ==================================================================================================
def check_n5(root, spec):
    errs, rows = [], []
    # --- §4 表 (人读) ---
    tbl = _md_table_rows(spec["_text"], ["BOM", "land pattern", "结构占位", "`verdict`"])
    tmap = {}
    for cells in tbl:
        ref = cells[0].strip("`").strip()
        if ref:
            tmap[ref] = cells
    for ref in CONN_REFS:
        cells = tmap.get(ref)
        if cells is None:
            errs.append(f"N5 §4 三方对照表缺 {ref} 行")
            continue
        # 4 个必填字段: BOM 规格 / 板读 land / 结构占位 / verdict
        need = {1: "BOM·网表规格串", 2: "板上 land pattern 实测", 3: "结构占位要求", 4: "verdict"}
        for idx, nm in need.items():
            val = cells[idx].strip() if len(cells) > idx else ""
            if not val:
                errs.append(f"N5 §4 {ref} 行的【{nm}】字段为空")
            elif idx == 4 and any(f in val for f in FORBIDDEN_VERDICT):
                errs.append(f"N5 §4 {ref} 行的 verdict = {val!r} (★不许用「待定」糊过去★)")
        rows.append({"ref": ref, "n_fields": len(cells), "ok": not any(
            e.startswith(f"N5 §4 {ref}") for e in errs)})
    # --- 机器块 connectors[] ---
    conns = spec.get("connectors") or []
    cmap = {c.get("ref"): c for c in conns}
    for ref in CONN_REFS:
        c = cmap.get(ref)
        if c is None:
            errs.append(f"N5 机器块 connectors 缺 {ref}")
            continue
        for key in ("bom_netlist_spec", "board_land_measured", "struct_requirement", "verdict"):
            val = c.get(key)
            if not val or not str(val).strip():
                errs.append(f"N5 机器块 connectors[{ref}].{key} 为空")
            elif key == "verdict" and any(f in str(val) for f in FORBIDDEN_VERDICT):
                errs.append(f"N5 机器块 connectors[{ref}].verdict = {val!r} (★不许用「待定」糊过去★)")
    return {"ok": not errs, "errs": errs, "rows": rows}


# ==================================================================================================
# N6 · 受保护 5 件 md5 逐字节不变
# ==================================================================================================
def check_n6(root):
    errs, rows = [], []
    items = dict(CFC.PROTECTED)
    items.update(PROTECTED_LEDGER_MD5)
    for rel, base in items.items():
        p = os.path.join(root, rel)
        if not os.path.exists(p):
            errs.append(f"N6 受保护件缺失: {rel}")
            continue
        got = md5_of(p)
        rows.append({"path": rel, "baseline": base, "got": got, "same": got == base})
        if got != base:
            errs.append(f"N6 受保护件被改: {rel} 基线 {base} ⇒ 现值 {got}")
    return {"ok": not errs, "errs": errs, "rows": rows}


# ==================================================================================================
# 汇总
# ==================================================================================================
def run_checks(root):
    spec = read_spec(root)
    calib = read_s6_targets(root)
    board = Board(os.path.join(root, PCB_REL))
    return {
        "N1": check_n1(root, spec, calib),
        "N2": check_n2(root, spec, calib, board),
        "N3": check_n3(root, spec, calib, board),
        "N4": check_n4(root, spec, calib, board),
        "N5": check_n5(root, spec),
        "N6": check_n6(root),
    }


def _hr(t):
    print("\n" + "=" * 96)
    print(t)
    print("=" * 96)


def print_checks(res):
    _hr("【ISS-290 · 「板只改一次」那一趟 · 结构侧最后一道交叉核对闸】")
    print(f"  N1 帧标签 ............... {'✅ 绿' if res['N1']['ok'] else '❌ 红'}  "
          f"(S6 目标位 {res['N1']['n_targets']} 条, 帧必须 = {FRAME})")
    print(f"  N2 SoM 承载区零冲突 ..... {'✅ 绿' if res['N2']['ok'] else '❌ 红'}  "
          f"(20 个落位 × 焊盘/座体/保守包络 三口径)")
    print(f"  N3 两条开口 (分别验) ... {'✅ 绿' if res['N3']['ok'] else '❌ 红'}  "
          f"(开口 {res['N3']['n_openings']} 条: {res['N3']['ids']})")
    print(f"  N4 必清空区净距 ≥ CRIT . {'✅ 绿' if res['N4']['ok'] else '❌ 红'}  "
          f"(CRIT = {res['N4']['crit']} · 取自既有 MECH 判据)")
    print(f"  N5 座体三方对照表完整 .. {'✅ 绿' if res['N5']['ok'] else '❌ 红'}  "
          f"(位号 {len(CONN_REFS)} 个 × 4 字段)")
    print(f"  N6 受保护 5 件 md5 ..... {'✅ 绿' if res['N6']['ok'] else '❌ 红'}")
    for r in res["N6"]["rows"]:
        print(f"      · {r['path']:44s} {r['got']} {'==' if r['same'] else '!='} {r['baseline']}")
    errs = []
    for k in ("N1", "N2", "N3", "N4", "N5", "N6"):
        errs += res[k]["errs"]
    if errs:
        _hr(f"【红】{len(errs)} 条")
        for e in errs:
            print(f"  ✗ {e}")
    else:
        _hr("【绿】N1~N6 全过")


# ==================================================================================================
# 沙盒 (★反向用例一律在副本上跑, 真件一个字节不碰★)
# ==================================================================================================
def sandbox_base(root):
    env = os.environ.get("MECH_SANDBOX_DIR")
    if env:
        return env
    return os.path.abspath(os.path.join(root, "..", "..", "tmp", "iss290_crosscheck_selftest"))


def make_sandbox(root, tag):
    base = sandbox_base(root)
    dst = os.path.join(base, tag)
    if os.path.exists(dst):
        shutil.rmtree(dst)
    os.makedirs(dst, exist_ok=True)
    rels = [SPEC_REL, CALIB_REL, PCB_REL] + list(CFC.PROTECTED.keys()) + list(PROTECTED_LEDGER_MD5)
    for rel in rels:
        src = os.path.join(root, rel)
        if os.path.exists(src):
            d = os.path.join(dst, rel)
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copy2(src, d)
    return dst


def _edit_spec_json(sb, fn):
    p = os.path.join(sb, SPEC_REL)
    text = open(p, encoding="utf-8").read()
    b, e = text.find(MACH_BEGIN), text.find(MACH_END)
    seg = text[b:e]
    m = re.search(r"```json\n(.*?)\n```", seg, re.S)
    data = json.loads(m.group(1))
    fn(data)
    new = "```json\n" + json.dumps(data, ensure_ascii=False, indent=1) + "\n```"
    text2 = text[:b] + text[b:e].replace(m.group(0), new) + text[e:]
    open(p, "w", encoding="utf-8").write(text2)


def _edit_spec_text(sb, old, new):
    p = os.path.join(sb, SPEC_REL)
    text = open(p, encoding="utf-8").read()
    if old not in text:
        return False
    open(p, "w", encoding="utf-8").write(text.replace(old, new, 1))
    return True


def _edit_calib_json(sb, fn):
    p = os.path.join(sb, CALIB_REL)
    text = open(p, encoding="utf-8").read()
    head = "```json cal:S6_TARGETS"
    seg = text.split(head, 1)[1].split("```", 1)[0]
    data = json.loads(seg[seg.index("{"):])
    fn(data)
    new = "```json" + head + "\n" + json.dumps(data, ensure_ascii=False, indent=1) + "\n"
    text2 = text.replace(seg, new, 1)
    open(p, "w", encoding="utf-8").write(text2)


def selftest(root):
    errs = []
    _hr("【自检】check_onepass_struct_crosscheck.py 反向用例 (★沙盒副本上跑, 真件一个字节不碰★)")
    base = run_checks(root)
    print("  [基线] " + " ".join(f"{k}={'OK' if base[k]['ok'] else 'NG'}"
                                 for k in ("N1", "N2", "N3", "N4", "N5", "N6")))
    if not all(base[k]["ok"] for k in ("N1", "N2", "N3", "N4", "N5", "N6")):
        errs.append("基线就不绿 ⇒ 自检无意义")
        print("  ✗ 基线不绿, 自检无意义")
        return 1

    # ---- ① 把某个 S6 目标位挪进 SoM 承载区 ⇒ N2 红 ----
    sb = make_sandbox(root, "case1_move_into_som")
    p = os.path.join(sb, CALIB_REL)
    before = md5_of(p)

    def _c1(d):
        for t in d["targets"]:
            if t["ref"] == "R_SEL_D0_N":
                t["x"] = 25.0
                t["y"] = 9.5          # ★SoM 承载区 J_SOM_P3 的地盘★
    _edit_calib_json(sb, _c1)
    after = md5_of(p)
    r1 = run_checks(sb)
    red = not r1["N2"]["ok"]
    print(f"  [{'OK ' if red else 'NG '}] ① 把 S6 目标位 R_SEL_D0_N 挪进 SoM 承载区 ⇒ N2 红: "
          f"{'是' if red else '否'} · md5 {before[:8]} ⇒ {after[:8]} (确实改了: {before != after}) · "
          f"N2 错误 {len(r1['N2']['errs'])} 条")
    if not red:
        errs.append("① 挪进 SoM 承载区后 N2 没红")
    if before == after:
        errs.append("① 没能真改到目标文件")

    # ---- ② 把某个目标位挪进调试口开口 ⇒ N3 红 ----
    sb = make_sandbox(root, "case2_move_into_debug_opening")
    p = os.path.join(sb, CALIB_REL)
    before = md5_of(p)

    def _c2(d):
        for t in d["targets"]:
            if t["ref"] == "R_SEL_D1_N":
                t["x"] = 144.30
                t["y"] = 56.60        # ★调试口开口 (罩 J_DEBUG) 正中★
    _edit_calib_json(sb, _c2)
    after = md5_of(p)
    r2 = run_checks(sb)
    red = not r2["N3"]["ok"]
    print(f"  [{'OK ' if red else 'NG '}] ② 把 S6 目标位 R_SEL_D1_N 挪进调试口开口 ⇒ N3 红: "
          f"{'是' if red else '否'} · md5 {before[:8]} ⇒ {after[:8]} (确实改了: {before != after}) · "
          f"N3 错误 {len(r2['N3']['errs'])} 条")
    if not red:
        errs.append("② 挪进调试口开口后 N3 没红")
    if before == after:
        errs.append("② 没能真改到目标文件")

    # ---- ③ 抽掉一个帧标签 ⇒ N1 红 ----
    sb = make_sandbox(root, "case3_strip_frame_tag")
    p = os.path.join(sb, SPEC_REL)
    before = md5_of(p)
    hit = _edit_spec_text(sb, "| `TP_DSI_CK_P` | `B160x100` |",
                           "| `TP_DSI_CK_P` |  |")
    after = md5_of(p)
    r3 = run_checks(sb)
    red = not r3["N1"]["ok"]
    print(f"  [{'OK ' if red else 'NG '}] ③ 抽掉 §3 表里 TP_DSI_CK_P 的帧标签 ⇒ N1 红: "
          f"{'是' if red else '否'} · 命中: {hit} · md5 {before[:8]} ⇒ {after[:8]} "
          f"(确实改了: {before != after}) · N1 错误 {len(r3['N1']['errs'])} 条")
    if not red:
        errs.append("③ 抽帧标签后 N1 没红")
    if not hit or before == after:
        errs.append("③ 没能真改到目标文件")

    # ---- ④ 把两条开口合并成一条 ⇒ N3 红 ----
    sb = make_sandbox(root, "case4_merge_openings")
    p = os.path.join(sb, SPEC_REL)
    before = md5_of(p)

    def _c4(d):
        o = d["openings"][0]
        o["rect"] = {"x0": 17.620, "x1": 143.838, "y0": 55.330, "y1": 69.870}
        o["id"] = "PORT_OPEN_MERGED"
        d["openings"] = [o]
    _edit_spec_json(sb, _c4)
    after = md5_of(p)
    r4 = run_checks(sb)
    red = not r4["N3"]["ok"]
    print(f"  [{'OK ' if red else 'NG '}] ④ 把两条开口合并成一条 ⇒ N3 红: "
          f"{'是' if red else '否'} · md5 {before[:8]} ⇒ {after[:8]} (确实改了: {before != after}) · "
          f"开口条数 {r4['N3']['n_openings']} · N3 错误 {len(r4['N3']['errs'])} 条")
    if not red:
        errs.append("④ 合并两条开口后 N3 没红")
    if before == after:
        errs.append("④ 没能真改到目标文件")

    # ---- ⑤ 把 CRIT 改小 ⇒ N4 红 (★CRIT 漂移即红, 不许靠改小阈值放行★) ----
    sb = make_sandbox(root, "case5_shrink_crit")
    p = os.path.join(sb, SPEC_REL)
    before = md5_of(p)

    def _c5(d):
        d["consts"]["crit"] = 0.10
    _edit_spec_json(sb, _c5)
    after = md5_of(p)
    r5 = run_checks(sb)
    red = not r5["N4"]["ok"]
    print(f"  [{'OK ' if red else 'NG '}] ⑤ 把规格页 CRIT 改小 (0.60 ⇒ 0.10) ⇒ N4 红: "
          f"{'是' if red else '否'} · md5 {before[:8]} ⇒ {after[:8]} (确实改了: {before != after}) · "
          f"N4 错误 {len(r5['N4']['errs'])} 条")
    if not red:
        errs.append("⑤ 把 CRIT 改小后 N4 没红")
    if before == after:
        errs.append("⑤ 没能真改到目标文件")

    # ---- ⑤b 把 CRIT 改大 ⇒ N4 红 (净距不足也红) ----
    sb = make_sandbox(root, "case5b_raise_crit")
    p = os.path.join(sb, SPEC_REL)
    before = md5_of(p)

    def _c5b(d):
        d["consts"]["crit"] = 60.00
    _edit_spec_json(sb, _c5b)
    after = md5_of(p)
    r5b = run_checks(sb)
    red = not r5b["N4"]["ok"]
    print(f"  [{'OK ' if red else 'NG '}] ⑤b 把规格页 CRIT 改大 (0.60 ⇒ 60.00) ⇒ N4 红 (净距不足): "
          f"{'是' if red else '否'} · md5 {before[:8]} ⇒ {after[:8]} (确实改了: {before != after}) · "
          f"N4 错误 {len(r5b['N4']['errs'])} 条")
    if not red:
        errs.append("⑤b 把 CRIT 改大后 N4 没红")
    if before == after:
        errs.append("⑤b 没能真改到目标文件")

    # ---- ⑥ 清空 §4 某行一个字段 ⇒ N5 红 ----
    sb = make_sandbox(root, "case6_empty_conn_field")
    p = os.path.join(sb, SPEC_REL)
    before = md5_of(p)

    def _c6(d):
        for c in d["connectors"]:
            if c["ref"] == "J_DEBUG":
                c["struct_requirement"] = ""
    _edit_spec_json(sb, _c6)
    after = md5_of(p)
    r6 = run_checks(sb)
    red = not r6["N5"]["ok"]
    print(f"  [{'OK ' if red else 'NG '}] ⑥ 清空 §4 里 J_DEBUG 行的【结构占位要求】⇒ N5 红: "
          f"{'是' if red else '否'} · md5 {before[:8]} ⇒ {after[:8]} (确实改了: {before != after}) · "
          f"N5 错误 {len(r6['N5']['errs'])} 条")
    if not red:
        errs.append("⑥ 清空 §4 字段后 N5 没红")
    if before == after:
        errs.append("⑥ 没能真改到目标文件")

    # ---- ⑦ 改受保护件 ⇒ N6 红 ----
    sb = make_sandbox(root, "case7_touch_protected")
    p = os.path.join(sb, PCB_REL)
    before = md5_of(p)
    with open(p, "a", encoding="utf-8") as fh:
        fh.write("\n; ★ISS-290 反向用例: 篡改受保护板文件★\n")
    after = md5_of(p)
    r7 = run_checks(sb)
    red = not r7["N6"]["ok"]
    print(f"  [{'OK ' if red else 'NG '}] ⑦ 篡改受保护板文件 ⇒ N6 红: "
          f"{'是' if red else '否'} · md5 {before[:8]} ⇒ {after[:8]} (确实改了: {before != after}) · "
          f"N6 错误 {len(r7['N6']['errs'])} 条")
    if not red:
        errs.append("⑦ 改受保护件后 N6 没红")
    if before == after:
        errs.append("⑦ 没能真改到目标文件")

    # ---- 收尾: 真件 md5 再核一遍 (★自检不许碰真件★) ----
    tail = check_n6(root)
    print(f"  [收尾] 真件 N6 = {'OK' if tail['ok'] else 'NG'} (自检跑完真件 md5 仍逐字节不变)")
    if not tail["ok"]:
        errs.append("自检跑完真件受保护 5 件被改了")

    _hr(f"【自检结果】{len(errs)} 条问题")
    for e in errs:
        print(f"  ✗ {e}")
    return 0 if not errs else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest(PROJ)
    res = run_checks(PROJ)
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=1))
    else:
        print_checks(res)
    errs = []
    for k in ("N1", "N2", "N3", "N4", "N5", "N6"):
        errs += res[k]["errs"]
    return 0 if not errs else 1


if __name__ == "__main__":
    sys.exit(main())
