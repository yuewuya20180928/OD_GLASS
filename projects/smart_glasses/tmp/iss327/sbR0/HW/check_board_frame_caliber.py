#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-274 · 板框 / 坐标系口径机器闸 (C1~C6) + --selftest 反向用例
=====================================================================
派活: 项目总工 (main) · 执行: 硬件总工 (hw-lead) · 2026-11-17

用途:
    ★**把「板只改一次」那一趟 (S1~S13) 用的坐标系口径核准成【单一自洽的一套】** ★
    —— 让那一趟照单开工【不会撞 SoM 座】/【不会重复计算坐标】/【不会被三套基线搅乱】。

用法:
    python3 HW/check_board_frame_caliber.py                  # 跑 C1~C6, rc=0 = 全绿
    python3 HW/check_board_frame_caliber.py --selftest        # 反向用例 (>=6 条), rc=0 = 反向全被抓住
    python3 HW/check_board_frame_caliber.py --root DIR        # 指定根目录 (沙盒副本)
    python3 HW/check_board_frame_caliber.py --json OUT.json   # 机器可读报告
    python3 HW/check_board_frame_caliber.py --update-baseline # 重录受保护 5 件 md5 基线 (★需 main 批准★)

★只读板, 绝不写盘上板; --selftest 的所有改动都发生在沙盒副本上 (默认落 workspace/tmp, 不落 /tmp)。
★权威页 = HW/PCB/BOARD_FRAME_CALIBER.md 的 4 个 JSON 块 (cal:FRAMES / cal:S6_TARGETS /
  cal:ISS271_RECTS / cal:PROTECTED_MD5) —— 人读摘要与 JSON 冲突时以 JSON 为准, 闸只认 JSON。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ROOT = os.path.dirname(HERE)          # 项目根 (本文件在 HW/ 下)
WORKSPACE_TMP = "/home/yuewuya/.openclaw/workspace/tmp"
# ★★ISS-283 · ⑪: 落表台账的 md5 注册表 (★C6 的网表/脚表/BOM 三件改走「落表台账为准」★) ★★
sys.path.insert(0, HERE)
import landing_md5

CALIB_REL = "HW/PCB/BOARD_FRAME_CALIBER.md"
WORKPACKET_REL = "HW/PCB/BOARD_ONEPASS_WORKPACKET.md"
LAYOUT_REL = "HW/PCB/LAYOUT_FIX_SPEC.md"
BOARD_REL = "HW/PCB/demo_mainboard.kicad_pcb"
# ★★ISS-283 · ⑪: C6 里【网表/脚表/BOM】三件的基线改走它 (★落表台账为准★) ★★
LANDING_LEDGER_REL = "HW/SCHEMATIC_LANDING_V1_LANDED.md"
# ★★ISS-283 · ⑪: 这三件【归落表链管】⇒ 判据走落表台账; 板与 .kicad_pro 【不归】⇒ 基线写死 ★★
C6_LEDGER_MANAGED = ("HW/netlist_v1.csv", "HW/netlist_v1_pins.csv", "HW/BOM_v1.csv")

TOL = 0.01          # mm · S6 坐标比对容差 (与 ISS-265 / 作业包一致)
OVERLAP_TOL = 1.5   # mm · C4 判重叠阈值
SOM_PREFIX = "J_SOM_P"

FRAME_ALIASES = {
    "B160x100": ["B160x100", "160×100 台架板帧", "160×100 台架板坐标"],
    "F30A": ["F30A", "60×30 套A 帧", "60×30 套A 坐标"],
    "P60x15": ["P60x15", "60×15 帧", "60×15 坐标"],
}


# ======================================================================
# 板文件解析 (纯 python, 不依赖 pcbnew —— 闸必须能用系统 python3 跑)
# ======================================================================

_RE_AT_FP = re.compile(r"^\s*\(at\s+(-?[\d.]+)\s+(-?[\d.]+)(?:\s+(-?[\d.]+))?\s*\)\s*$")
_RE_PROP_REF = re.compile(r'\(property\s+"Reference"\s+"([^"]*)"')
_RE_ITEM = re.compile(r"^\t\t\((fp_line|fp_rect|fp_circle|fp_arc|pad)\b")
_RE_PAD_AT = re.compile(r"\(at\s+(-?[\d.]+)\s+(-?[\d.]+)")
_RE_SIZE = re.compile(r"\(size\s+(-?[\d.]+)\s+(-?[\d.]+)")
_RE_START = re.compile(r"\(start\s+(-?[\d.]+)\s+(-?[\d.]+)")
_RE_END = re.compile(r"\(end\s+(-?[\d.]+)\s+(-?[\d.]+)")
_RE_CENTER = re.compile(r"\(center\s+(-?[\d.]+)\s+(-?[\d.]+)")
_RE_RADIUS = re.compile(r"\(radius\s+([\d.]+)\)")
_RE_WIDTH = re.compile(r"\(width\s+([\d.]+)\)")
_RE_LAYER = re.compile(r'\(layer\s+"([^"]*)"')


def _sub_block(lines, i):
    """从 lines[i] 起收一个完整 s-表达式子块, 返回 (文本, 结束行号)。"""
    depth = 0
    buf = []
    j = i
    while j < len(lines):
        ln = lines[j]
        buf.append(ln)
        depth += ln.count("(") - ln.count(")")
        if depth == 0 and j > i:
            break
        if depth == 0 and j == i and ln.strip() == ")":
            break
        j += 1
    return "\n".join(buf), j


def parse_board(path):
    """读 KiCad 板文件, 抽: 板框 / 铜层数 / 封装位置 / 焊盘 / 封装外形包络。"""
    src = open(path, encoding="utf-8").read()
    lines = src.split("\n")
    n = len(lines)

    # ---- 铜层数 ----
    m = re.search(r"\(layers\n(.*?)\n\t\)", src, re.S)
    copper = 0
    if m:
        copper = len(re.findall(r'\(\d+\s+"[^"]+\.Cu"\s+signal\)', m.group(1)))

    # ---- Edge.Cuts ----
    edge_pts = []
    edge_w = 0.0
    i = 0
    while i < n:
        if lines[i].strip() == "(gr_line":
            blk, j = _sub_block(lines, i)
            if '"Edge.Cuts"' in blk:
                st = _RE_START.search(blk)
                en = _RE_END.search(blk)
                wd = _RE_WIDTH.search(blk)
                if st and en:
                    edge_pts.append((float(st.group(1)), float(st.group(2)),
                                     float(en.group(1)), float(en.group(2))))
                    if wd:
                        edge_w = max(edge_w, float(wd.group(1)))
            i = j + 1
        else:
            i += 1
    if edge_pts:
        xs = [v for e in edge_pts for v in (e[0], e[2])]
        ys = [v for e in edge_pts for v in (e[1], e[3])]
        hw = edge_w / 2.0
        edge_geom = (min(xs), min(ys), max(xs), max(ys))
        edge_stroke = (min(xs) - hw, min(ys) - hw, max(xs) + hw, max(ys) + hw)
    else:
        edge_geom = edge_stroke = None

    # ---- footprint ----
    fps = {}
    i = 0
    while i < n:
        if lines[i].startswith("\t(footprint "):
            blk, j = _sub_block(lines, i)
            blines = blk.split("\n")
            ref = None
            at = None
            rot = 0.0
            for ln in blines:
                pm = _RE_PROP_REF.search(ln)
                if pm and ref is None:
                    ref = pm.group(1)
                if at is None:
                    am = _RE_AT_FP.match(ln)
                    if am:
                        at = (float(am.group(1)), float(am.group(2)))
                        if am.group(3):
                            rot = float(am.group(3))
            pads = []
            gfx = []
            k = 0
            while k < len(blines):
                im = _RE_ITEM.match(blines[k])
                if not im:
                    k += 1
                    continue
                kind = im.group(1)
                iblk, k2 = _sub_block(blines, k)
                k = k2 + 1
                if kind == "pad":
                    am = _RE_PAD_AT.search(iblk)
                    sm = _RE_SIZE.search(iblk)
                    if am:
                        px, py = float(am.group(1)), float(am.group(2))
                        w = float(sm.group(1)) if sm else 0.0
                        h = float(sm.group(2)) if sm else 0.0
                        pads.append((px, py, w, h))
                else:
                    st = _RE_START.search(iblk)
                    en = _RE_END.search(iblk)
                    ce = _RE_CENTER.search(iblk)
                    ra = _RE_RADIUS.search(iblk)
                    wd = _RE_WIDTH.search(iblk)
                    half = (float(wd.group(1)) / 2.0) if wd else 0.0
                    pts = []
                    if st:
                        pts.append((float(st.group(1)), float(st.group(2))))
                    if en:
                        pts.append((float(en.group(1)), float(en.group(2))))
                    if ce and ra:
                        cx, cy, r = float(ce.group(1)), float(ce.group(2)), float(ra.group(1))
                        pts += [(cx - r, cy - r), (cx + r, cy + r)]
                    if pts:
                        xs = [p[0] for p in pts] + [p[0] for p in pts]
                        ys = [p[1] for p in pts] + [p[1] for p in pts]
                        gfx.append((min(xs) - half, min(ys) - half,
                                    max(xs) + half, max(ys) + half))
            if ref:
                fx, fy = at if at else (0.0, 0.0)
                ca, sa = _rot(rot)
                abs_pads = []
                for (px, py, w, h) in pads:
                    gx = fx + px * ca + py * sa
                    gy = fy - px * sa + py * ca
                    abs_pads.append((gx, gy, w, h))
                boxes = [(gx - w / 2.0, gy - h / 2.0, gx + w / 2.0, gy + h / 2.0)
                         for (gx, gy, w, h) in abs_pads]
                boxes += [(fx + g[0], fy + g[1], fx + g[2], fy + g[3]) for g in gfx]
                if boxes:
                    bbox = (min(b[0] for b in boxes), min(b[1] for b in boxes),
                            max(b[2] for b in boxes), max(b[3] for b in boxes))
                else:
                    bbox = (fx, fy, fx, fy)
                fps[ref] = {"at": (fx, fy), "rot": rot, "pads": abs_pads,
                            "bbox": bbox, "line": i + 1}
            i = j + 1
        else:
            i += 1

    return {"path": path, "copper_layers": copper, "edge_geom": edge_geom,
            "edge_stroke": edge_stroke, "fps": fps, "footprint_count": len(fps),
            "edge_lines": len(edge_pts)}


def _rot(deg):
    import math
    a = math.radians(deg)
    return math.cos(a), math.sin(a)


# ======================================================================
# 校准页 / 文档读取
# ======================================================================

def load_json_block(md_text, block):
    """取 md 里 ```json cal:BLOCK ... ``` 之间的 JSON。"""
    pat = re.compile(r"```json\s+cal:" + re.escape(block) + r"\s*\n(.*?)\n```", re.S)
    m = pat.search(md_text)
    if not m:
        raise SystemExit(f"[calib] 校准页缺 JSON 块 cal:{block}")
    return json.loads(m.group(1))


def read_text(path):
    if not os.path.exists(path):
        return ""
    return open(path, encoding="utf-8").read()


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_part_pos_all(text):
    """抽全部 PCB_PART_POS="..." 串 → [(行号, {ref: (x, y)})]。"""
    out = []
    lines = text.split("\n")
    for i, ln in enumerate(lines):
        for m in re.finditer(r'PCB_PART_POS\s*=\s*"([^"]*)"', ln):
            d = {}
            for item in m.group(1).split(";"):
                item = item.strip()
                if not item:
                    continue
                ref, _, xy = item.partition(":")
                x, _, y = xy.partition(",")
                try:
                    d[ref.strip()] = (float(x), float(y))
                except ValueError:
                    continue
            if d:
                out.append((i, d))
    return out


def pick_primary(occ):
    """主串 = ref 数最多的那串 (S6 目标串 20 条); 其余为旁证串 (臂布局等)。"""
    if not occ:
        return None, []
    occ = sorted(occ, key=lambda o: -len(o[1]))
    return occ[0][1], occ[1:]


def section_of(lines, idx):
    """取第 idx 行所属的 markdown 小节 (最近的前置标题 → 下一个标题)。"""
    start = 0
    for i in range(idx, -1, -1):
        if re.match(r"^#{1,6}\s", lines[i]):
            start = i
            break
    end = len(lines)
    for i in range(idx + 1, len(lines)):
        if re.match(r"^#{1,6}\s", lines[i]):
            end = i
            break
    return "\n".join(lines[start:end])


def has_frame_tag(text, frame_id):
    for alias in FRAME_ALIASES.get(frame_id, [frame_id]):
        if alias in text:
            return alias
    return None


# ======================================================================
# C1 ~ C6
# ======================================================================

class Result:
    def __init__(self, code, title):
        self.code = code
        self.title = title
        self.ok = True
        self.lines = []
        self.anomalies = []

    def note(self, s):
        self.lines.append(s)

    def fail(self, s, anomaly=None):
        self.ok = False
        self.lines.append("✗ " + s)
        if anomaly:
            self.anomalies.append(anomaly)

    def warn(self, s):
        self.lines.append("! " + s)

    def okline(self, s):
        self.lines.append("✓ " + s)


def run_checks(root):
    root = os.path.abspath(root)
    p = lambda rel: os.path.join(root, rel)

    calib_md = read_text(p(CALIB_REL))
    wp_md = read_text(p(WORKPACKET_REL))
    lf_md = read_text(p(LAYOUT_REL))
    board = parse_board(p(BOARD_REL))

    frames_block = load_json_block(calib_md, "FRAMES")
    s6_block = load_json_block(calib_md, "S6_TARGETS")
    rects_block = load_json_block(calib_md, "ISS271_RECTS")
    prot_block = load_json_block(calib_md, "PROTECTED_MD5")

    frames = frames_block["frames"]
    current_frame = frames_block["current_frame"]
    targets = s6_block["targets"]
    legacy = s6_block.get("legacy_positions", {})
    allow_diff = s6_block.get("allow_board_diff", [])
    rects = rects_block["rects"]

    doc_wp_occ = parse_part_pos_all(wp_md)
    doc_lf_occ = parse_part_pos_all(lf_md)
    doc_wp, wp_others = pick_primary(doc_wp_occ)
    doc_lf, lf_others = pick_primary(doc_lf_occ)
    reg = {t["ref"]: (t["x"], t["y"]) for t in targets}

    results = []

    # ---------------- C1 帧一致性 ----------------
    r = Result("C1", "帧一致性 (坐标组必须带帧标签; 漏标一条即红)")
    # (a) 每个 S6 目标必须带合法帧标签, 且必须是现役帧
    for t in targets:
        ref = t.get("ref")
        fr = t.get("frame")
        if not fr:
            r.fail(f"S6 目标位 {ref} 缺帧标签 (frame 字段为空) ⇒ 该坐标不知道属于哪套框",
                   anomaly=("S6 帧标签缺失", ref))
        elif fr not in frames:
            r.fail(f"S6 目标位 {ref} 的帧标签 {fr} 不在 FRAMES 注册表里",
                   anomaly=("S6 帧标签非法", ref))
        elif fr != current_frame:
            r.fail(f"S6 目标位 {ref} 标的是 {fr} 帧, 不是现役帧 {current_frame} ⇒ 不许写进现役板",
                   anomaly=("S6 帧标签错帧", ref))
    if r.ok:
        r.okline(f"20 个 S6 目标位逐个带帧标签, 且全部 = 现役帧 {current_frame}")
    # (b) 异帧矩形必须标异帧, 且不得标成现役帧
    for rc in rects:
        nm = rc.get("name")
        fr = rc.get("frame")
        if not fr:
            r.fail(f"ISS-271 矩形 {nm} 缺帧标签", anomaly=("异帧矩形帧标签缺失", nm))
        elif fr not in frames:
            r.fail(f"ISS-271 矩形 {nm} 的帧标签 {fr} 不在 FRAMES 注册表里",
                   anomaly=("异帧矩形帧标签非法", nm))
        elif fr == current_frame:
            r.fail(f"ISS-271 矩形 {nm} 被标成现役帧 {fr} ⇒ 60×30 口径当 160×100 用 = 异帧误用",
                   anomaly=("异帧矩形被标现役", nm))
    # (d) 文档里的 PCB_PART_POS 串必须 20 条, 且彼此一致, 且与校准页登记一致
    for nm, d in (("BOARD_ONEPASS_WORKPACKET.md §3-S6", doc_wp),
                  ("LAYOUT_FIX_SPEC.md §3 方案 A", doc_lf)):
        if d is None:
            r.fail(f"{nm} 找不到 PCB_PART_POS 坐标串", anomaly=("文档缺坐标串", nm))
        elif len(d) != len(targets):
            r.fail(f"{nm} 的 PCB_PART_POS 主串 = {len(d)} 条, 校准页登记 = {len(targets)} 条 ⇒ 口径漂移",
                   anomaly=("文档坐标条数不符", nm))
    if doc_wp and doc_lf:
        diff = set(doc_wp) ^ set(doc_lf)
        bad = [k for k in set(doc_wp) & set(doc_lf)
               if abs(doc_wp[k][0] - doc_lf[k][0]) > TOL or abs(doc_wp[k][1] - doc_lf[k][1]) > TOL]
        if diff or bad:
            r.fail(f"两份文档的 S6 目标串不一致: ref 差集={sorted(diff)} 值差={sorted(bad)}",
                   anomaly=("文档坐标串互不一致", "workpacket vs layout"))
    if reg and doc_wp:
        bad = []
        for k in sorted(set(reg) | set(doc_wp)):
            if k not in doc_wp or k not in reg:
                bad.append(k)
            elif abs(reg[k][0] - doc_wp[k][0]) > TOL or abs(reg[k][1] - doc_wp[k][1]) > TOL:
                bad.append(k)
        if bad:
            r.fail(f"校准页登记的 S6 目标位与文档串不一致: {bad}",
                   anomaly=("校准页 vs 文档坐标不符", ",".join(bad)))
        else:
            r.okline(f"校准页登记的 {len(reg)} 个 S6 目标位与作业包/规格页文档串逐个一致")
    # (d2) 每一处 PCB_PART_POS 串 (含臂布局串) 所在小节必须带帧标签
    for nm, text, occ in (("BOARD_ONEPASS_WORKPACKET.md", wp_md, doc_wp_occ),
                           ("LAYOUT_FIX_SPEC.md", lf_md, doc_lf_occ)):
        lines = text.split("\n")
        for i, d in occ:
            sec = section_of(lines, i)
            primary = (d is doc_wp) or (d is doc_lf)
            want = current_frame if primary else None
            tag = None
            for fid in ([want] if want else list(frames)):
                if fid:
                    tag = has_frame_tag(sec, fid)
                    if tag:
                        break
            if not tag:
                r.fail(f"{nm} 第 {i + 1} 行的 PCB_PART_POS 串所在小节没有帧标签 "
                       f"({'必须是 ' + want if want else '必须是任一注册帧'}) ⇒ 坐标帧未声明",
                       anomaly=("文档段缺帧标签", nm))
            else:
                r.okline(f"{nm} 第 {i + 1} 行的 PCB_PART_POS 串"
                         f"{'(S6 主串)' if primary else '(旁证串)'} 所在小节带帧标签: {tag}")
    # (e) ISS-271 矩形数字出现在 S6 段时, 必须带 F30A 帧标 + 警语
    s6_sec = ""
    lines = wp_md.split("\n")
    for i, ln in enumerate(lines):
        if ln.startswith("### ") and "S6" in ln:
            s6_sec = section_of(lines, i)
            break
    if s6_sec:
        if "ISS-271" not in s6_sec:
            r.fail("作业包 §3-S6 段没有点名 ISS-271 ⇒ 60×30 帧的开口/LED 窗口可能被当 S6 坐标用",
                   anomaly=("S6 段缺 ISS-271 警语", "workpacket §3-S6"))
        else:
            r.okline("作业包 §3-S6 段已点名 ISS-271 (异帧坐标不得当 S6 坐标用)")
        for rc in rects:
            nums = [("%g" % rc["x0"]), ("%g" % rc["x1"]), ("%g" % rc["y0"]), ("%g" % rc["y1"])]
            hit = [s for s in nums if s in s6_sec]
            if hit:
                if not has_frame_tag(s6_sec, rc["frame"]):
                    r.fail(f"作业包 §3-S6 段出现了 {rc['name']} 的 60×30 帧坐标数字 {hit}, "
                           f"但该段没有 {rc['frame']} 帧标 ⇒ 异帧坐标误用",
                           anomaly=("S6 段混入异帧数字", rc["name"]))
                else:
                    r.okline(f"作业包 §3-S6 段里的 {rc['name']} 数字带 {rc['frame']} 帧标 "
                             f"({has_frame_tag(s6_sec, rc['frame'])})")
    results.append(r)

    # ---------------- C2 S6 坐标真值 ----------------
    r = Result("C2", "S6 坐标真值 (20 ref 逐个 ±0.01mm; 差异集合只允许 R_SEL_D3_P)")
    at_target, differ, missing = [], [], []
    anomalies = []
    for ref in sorted(set(reg) | set(doc_wp)):
        if ref not in doc_wp:
            anomalies.append(("文档缺 ref", ref))
            continue
        if ref not in reg:
            anomalies.append(("校准页缺 ref", ref))
            continue
        if ref not in board["fps"]:
            missing.append(ref)
            anomalies.append(("板上缺失", ref))
            continue
        bx, by = board["fps"][ref]["at"]
        tx, ty = doc_wp[ref]
        if abs(bx - tx) <= TOL and abs(by - ty) <= TOL:
            at_target.append(ref)
        else:
            differ.append(ref)
            if ref not in allow_diff:
                anomalies.append(("board≠doc", ref))
    for ref in sorted(set(reg) & set(doc_wp)):
        rx, ry = reg[ref]
        dx, dy = doc_wp[ref]
        if abs(rx - dx) > TOL or abs(ry - dy) > TOL:
            anomalies.append(("doc≠registry", ref))
        if ref in board["fps"]:
            bx, by = board["fps"][ref]["at"]
            if (abs(bx - rx) > TOL or abs(by - ry) > TOL) and ref not in allow_diff:
                anomalies.append(("registry≠board", ref))
    # 允许差异的 ref: 只允许在「目标位」或「已知前置位」
    for ref in allow_diff:
        if ref not in board["fps"]:
            continue
        bx, by = board["fps"][ref]["at"]
        tgt = doc_wp.get(ref)
        leg = legacy.get(ref)
        ok_pos = False
        if tgt and abs(bx - tgt[0]) <= TOL and abs(by - tgt[1]) <= TOL:
            ok_pos = True
        if leg and abs(bx - leg[0]) <= TOL and abs(by - leg[1]) <= TOL:
            ok_pos = True
        if not ok_pos:
            anomalies.append(("位置白名单违规", ref))
            anomalies.append(("board≠doc", ref))
    r.note(f"已在目标位 = {len(at_target)} / 不同 = {len(differ)} / 缺失 = {len(missing)}"
           f" (共 {len(set(reg) | set(doc_wp))} 个 ref, 容差 ±{TOL}mm)")
    if differ:
        r.note(f"不同项 = {sorted(differ)}  (逐个实测值: "
               + ", ".join(f"{k}=({board['fps'][k]['at'][0]:.2f},{board['fps'][k]['at'][1]:.2f})"
                           f" vs 目标({doc_wp[k][0]:.2f},{doc_wp[k][1]:.2f})" for k in sorted(differ))
               + ")")
    if missing:
        r.fail(f"板上找不到的 ref: {missing}", anomaly=("板上缺失", ",".join(missing)))
    if anomalies:
        for kind, ref in anomalies:
            r.fail(f"差异项: {kind} · {ref}", anomaly=(kind, ref))
    else:
        r.okline(f"硬违规 = 0 ⇒ 差异只出现在允许的前置差异 {sorted(allow_diff)} (S6 尚未执行)")
    r.anomalies = anomalies
    results.append(r)

    # ---------------- C3 S6 目标位越界 ----------------
    r = Result("C3", "S6 目标位必须落在现役板框内 (出界数 = 0)")
    eg = board["edge_geom"]
    out_of = []
    tgt_all = dict(doc_wp or {})
    tgt_all.update(reg or {})
    for ref, (x, y) in sorted(tgt_all.items()):
        if not (eg[0] - TOL <= x <= eg[2] + TOL and eg[1] - TOL <= y <= eg[3] + TOL):
            out_of.append(ref)
    r.note(f"现役板框 (Edge.Cuts 几何) = X {eg[0]:.2f}..{eg[2]:.2f} / Y {eg[1]:.2f}..{eg[3]:.2f} mm")
    es = board["edge_stroke"]
    r.note(f"板框包围盒 (含 0.1mm 线宽外扩) = X {es[0]:.2f}..{es[2]:.2f} / Y {es[1]:.2f}..{es[3]:.2f} mm")
    if out_of:
        for ref in out_of:
            r.fail(f"目标位越界: {ref} @ {tgt_all[ref]}", anomaly=("目标位出界", ref))
    else:
        r.okline(f"{len(tgt_all)} 个目标位全部落在现役板框内 ⇒ 出界数 = 0")
    results.append(r)

    # ---------------- C4 S6 目标位不压既有封装 ----------------
    r = Result("C4", "S6 目标位与既有封装重叠 <1.5mm ⇒ 重叠数 = 0")
    ov_all, ov_nons6 = [], []
    for ref, (x, y) in sorted(doc_wp.items()):
        for oref, d in board["fps"].items():
            if oref == ref:
                continue
            ox, oy = d["at"]
            dist = ((x - ox) ** 2 + (y - oy) ** 2) ** 0.5
            if dist < OVERLAP_TOL:
                ov_all.append((ref, oref, round(dist, 3)))
                if oref not in doc_wp:
                    ov_nons6.append((ref, oref, round(dist, 3)))
    r.note(f"重叠阈值 = {OVERLAP_TOL}mm; 判据 = 目标位到既有封装原点的距离")
    if ov_all:
        for a, b_, d in ov_all:
            r.fail(f"目标位重叠: {a} ↔ {b_} (间距 {d}mm < {OVERLAP_TOL}mm)",
                   anomaly=("目标位压封装", f"{a}/{b_}"))
    else:
        r.okline(f"{len(doc_wp)} 个目标位与既有封装零重叠 ⇒ 重叠数 = 0")
    if ov_nons6:
        r.warn(f"其中与 S6 之外的封装重叠 {len(ov_nons6)} 处")
    results.append(r)

    # ---------------- C5 异帧坐标误用检测 ----------------
    r = Result("C5", "异帧坐标误用检测 (60×30 帧矩形套到现役板上 ⇒ 报出压住哪些 SoM 焊盘)")
    som_refs = [k for k in sorted(board["fps"]) if k.startswith(SOM_PREFIX)]
    for rc in rects:
        nm = rc.get("name")
        x0, x1, y0, y1 = rc["x0"], rc["x1"], rc["y0"], rc["y1"]
        hits = {}
        for sref in som_refs:
            n = 0
            for (px, py, w, h) in board["fps"][sref]["pads"]:
                if x0 <= px <= x1 and y0 <= py <= y1:
                    n += 1
            if n:
                hits[sref] = n
        if hits:
            r.note(f"{nm} (帧 {rc.get('frame')}) → 压住 SoM 焊盘: "
                   + ", ".join(f"{k}×{v}" for k, v in sorted(hits.items()))
                   + f" (合计 {sum(hits.values())})")
        else:
            r.fail(f"{nm} (帧 {rc.get('frame')}) → 不压任何焊盘 (口径漂移或板已变 ⇒ 需人工复核)",
                   anomaly=("C5 矩形不压焊盘", nm))
            continue
        exp = rc.get("expect_hits") or {}
        if exp and hits != exp:
            r.fail(f"{nm} 压住焊盘 {hits} ≠ 基线 {exp} ⇒ 口径漂移",
                   anomaly=("C5 压焊盘数漂移", nm))
        else:
            r.okline(f"{nm} 压焊盘数与基线一致 ⇒ 异帧危害已机器化留存")
    results.append(r)

    # ---------------- C6 受保护 5 件 md5 ----------------
    # ★★ISS-283 · ⑪ (★2026-11-17 12:4x 实测★): 【网表 / 脚表 / BOM】三件的判据改成
    #   ★**「落表台账为准」**★ (★盘上 md5 == `HW/SCHEMATIC_LANDING_V1_LANDED.md` 里该文件
    #   最新一条落表链登记的 md5★) ⇒ ★★**理由: 只把基线数字改成新值 = 下次落表又红一遍
    #   ⇒ 判据的【取值来源】必须变·不是【取值】变**★★ ⇒ ★**不许用 `--update-baseline` 消红★**
    #   ⇒ ★**台账里查不到 / 链头不唯一 / 链断 / 链头无单号 / 四项不齐 ⇒ 一律红** ★
    # ★**板 / `.kicad_pro` 两件的基线照旧写死** (★它们不归落表链管 ⇒ 那两条一条不许动★) ★
    r = Result("C6", "受保护 5 件 md5 逐字节不变 (板 / .kicad_pro 写死基线 · 网表/脚表/BOM 走落表台账)")
    for rel, want in sorted((prot_block.get("files") or {}).items()):
        fpath = os.path.join(root, rel)
        if not os.path.exists(fpath):
            r.fail(f"受保护件缺失: {rel}", anomaly=("受保护件缺失", rel))
            continue
        got = md5(fpath)
        if rel in C6_LEDGER_MANAGED:
            # ★★ISS-283 · ⑪: 走落表台账 (★fail-closed·查不到/链断/四项不齐 ⇒ 红★) ★
            g, msg = landing_md5.check_registered(root, rel, fpath, md5)
            if g:
                r.okline("%s ⇒ %s" % (rel, msg))
            else:
                r.fail(msg, anomaly=("落表台账对不上", rel))
            continue
        if got == want:
            r.okline(f"{rel} md5 未变 ({got})")
        else:
            r.fail(f"{rel} md5 变了: 基线 {want} → 现值 {got}",
                   anomaly=("受保护件被改", rel))
    for rel in sorted(prot_block.get("extra_info_files") or {}):
        fpath = os.path.join(root, rel)
        if os.path.exists(fpath):
            r.note(f"[信息] {rel} md5 = {md5(fpath)} (零落表边界自证, 不参与判红)")
    results.append(r)

    extra = {
        "board_edge_geom": eg,
        "board_edge_stroke": es,
        "copper_layers": board["copper_layers"],
        "footprint_count": board["footprint_count"],
        "frame_current": current_frame,
        "at_target": at_target,
        "differ": differ,
        "missing": missing,
        "c2_anomalies": anomalies,
    }
    return results, extra


# ======================================================================
# --selftest 反向用例 (每条自证「真的改到了目标那一处」)
# ======================================================================

SELF_FILES = [
    CALIB_REL, WORKPACKET_REL, LAYOUT_REL, BOARD_REL,
    "HW/PCB/demo_mainboard.kicad_pro", "HW/netlist_v1.csv",
    "HW/netlist_v1_pins.csv", "HW/BOM_v1.csv",
    # ★★ISS-283 · ⑪: C6 的网表/脚表/BOM 改走落表台账 ⇒ 沙盒必须带上台账 (★不然查不到登记·那是假红★) ★
    LANDING_LEDGER_REL,
]


def build_sandbox(root, base):
    src = os.path.join(root)
    dst = os.path.join(base, "iss274_selftest")
    if os.path.exists(dst):
        shutil.rmtree(dst)
    for rel in SELF_FILES:
        s = os.path.join(src, rel)
        if not os.path.exists(s):
            continue
        d = os.path.join(dst, rel)
        os.makedirs(os.path.dirname(d), exist_ok=True)
        shutil.copy2(s, d)
    return dst


def move_footprint_in_text(text, ref, nx, ny):
    """把板上某个封装的原点改成 (nx, ny); 返回 (新文本, 改了没)。"""
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        if lines[i].startswith("\t(footprint "):
            blk, j = _sub_block(lines, i)
            if f'"Reference" "{ref}"' in blk:
                blines = blk.split("\n")
                for k, ln in enumerate(blines):
                    m = _RE_AT_FP.match(ln)
                    if m:
                        blines[k] = f"\t\t(at {nx} {ny})"
                        newblk = "\n".join(blines)
                        return "\n".join(lines[:i]) + "\n" + newblk + "\n" + "\n".join(lines[j + 1:]), True
                return text, False
            i = j + 1
        else:
            i += 1
    return text, False


def edit_json_block(md_text, block, fn):
    """在 md 的 ```json cal:BLOCK``` 块里跑 fn(obj) → 返回 (新文本, 改了没)。"""
    pat = re.compile(r"(```json\s+cal:" + re.escape(block) + r"\s*\n)(.*?)(\n```)", re.S)
    m = pat.search(md_text)
    if not m:
        return md_text, False
    obj = json.loads(m.group(2))
    before = json.dumps(obj, ensure_ascii=False, sort_keys=True)
    fn(obj)
    after = json.dumps(obj, ensure_ascii=False, indent=2)
    if before == json.dumps(obj, ensure_ascii=False, sort_keys=True):
        return md_text, False
    return md_text[:m.start(2)] + after + md_text[m.end(2):], True


def selftest(root, base):
    cases = []

    def case(name, target_rel, mutate, expect_code, expect_ref, expect_msg=None):
        cases.append({"name": name, "target": target_rel, "mutate": mutate,
                      "code": expect_code, "ref": expect_ref, "msg": expect_msg})

    # ① 改一个 S6 目标坐标 (校准页登记) ⇒ C2 红
    def m1(sb):
        f = os.path.join(sb, CALIB_REL)
        txt = open(f, encoding="utf-8").read()
        new, ch = edit_json_block(txt, "S6_TARGETS", lambda o: o["targets"].__setitem__(
            next(i for i, t in enumerate(o["targets"]) if t["ref"] == "R_SEL_CK_P"),
            {"ref": "R_SEL_CK_P", "x": 103.9, "y": 5.5, "frame": "B160x100"}))
        open(f, "w", encoding="utf-8").write(new)
        return ch
    case("① 改一个 S6 目标坐标 (R_SEL_CK_P 102.90→103.90) ⇒ C2 红", CALIB_REL, m1, "C2", "R_SEL_CK_P")

    # ② 把 R_SEL_D3_P 挪到别处 (板上) ⇒ C2 红 (差异集合 = 2 项)
    def m2(sb):
        f = os.path.join(sb, BOARD_REL)
        txt = open(f, encoding="utf-8").read()
        new, ch = move_footprint_in_text(txt, "R_SEL_D3_P", 70.0, 20.0)
        open(f, "w", encoding="utf-8").write(new)
        return ch
    case("② 把 R_SEL_D3_P 挪到第三处 (板 78.90,9.50→70.00,20.00) ⇒ C2 红", BOARD_REL, m2, "C2", "R_SEL_D3_P")

    # ③ 抽掉一个 ref 的帧标签 ⇒ C1 红
    def m3(sb):
        f = os.path.join(sb, CALIB_REL)
        txt = open(f, encoding="utf-8").read()
        def fn(o):
            for t in o["targets"]:
                if t["ref"] == "TP_DSI_CK_N":
                    t.pop("frame", None)
        new, ch = edit_json_block(txt, "S6_TARGETS", fn)
        open(f, "w", encoding="utf-8").write(new)
        return ch
    case("③ 抽掉一个 ref 的帧标签 (TP_DSI_CK_N) ⇒ C1 红", CALIB_REL, m3, "C1", "TP_DSI_CK_N")

    # ④ 把 C5 的矩形换到 SoM 区外 ⇒ C5 报「不压任何焊盘」并红
    def m4(sb):
        f = os.path.join(sb, CALIB_REL)
        txt = open(f, encoding="utf-8").read()
        def fn(o):
            for rc in o["rects"]:
                if rc["name"] == "D_LED_G_window":
                    rc["x0"] = 3.0
                    rc["x1"] = 10.0
        new, ch = edit_json_block(txt, "ISS271_RECTS", fn)
        open(f, "w", encoding="utf-8").write(new)
        return ch
    case("④ 把 C5 矩形换到 SoM 区外 (x 33.00..47.71→3.00..10.00) ⇒ C5 报「不压任何焊盘」并红",
         CALIB_REL, m4, "C5", "D_LED_G_window", "不压任何焊盘")

    # ⑤ 改受保护 5 件之一 (BOM) ⇒ C6 红
    def m5(sb):
        f = os.path.join(sb, "HW/BOM_v1.csv")
        with open(f, "a", encoding="utf-8") as fh:
            fh.write("X_TAMPER_PROBE,0,0,0,0,0,0,0,0,0\n")
        return True
    case("⑤ 改受保护 5 件之一 (BOM_v1.csv 追加一行) ⇒ C6 红", "HW/BOM_v1.csv", m5, "C6", "HW/BOM_v1.csv")

    # ⑥ 把 S6 目标位改到板框外 ⇒ C3 红
    def m6(sb):
        f = os.path.join(sb, CALIB_REL)
        txt = open(f, encoding="utf-8").read()
        def fn(o):
            for t in o["targets"]:
                if t["ref"] == "TP_DSI_D0_P":
                    t["x"] = 187.5
        new, ch = edit_json_block(txt, "S6_TARGETS", fn)
        open(f, "w", encoding="utf-8").write(new)
        return ch
    case("⑥ 把 S6 目标位改到板框外 (TP_DSI_D0_P 87.50→187.50) ⇒ C3 红", CALIB_REL, m6, "C3", "TP_DSI_D0_P")

    # ⑦ 把 ISS-271 矩形错标成现役帧 ⇒ C1 红
    def m7(sb):
        f = os.path.join(sb, CALIB_REL)
        txt = open(f, encoding="utf-8").read()
        def fn(o):
            for rc in o["rects"]:
                if rc["name"] == "service_opening":
                    rc["frame"] = "B160x100"
        new, ch = edit_json_block(txt, "ISS271_RECTS", fn)
        open(f, "w", encoding="utf-8").write(new)
        return ch
    case("⑦ 把 ISS-271 矩形错标成现役帧 ⇒ C1 红", CALIB_REL, m7, "C1", "service_opening")

    # ⑧ 抽掉作业包 S6 段的帧标签 ⇒ C1 红
    def m8(sb):
        f = os.path.join(sb, WORKPACKET_REL)
        txt = open(f, encoding="utf-8").read()
        lines = txt.split("\n")
        s6 = None
        for i, ln in enumerate(lines):
            if ln.startswith("### ") and "S6" in ln:
                s6 = i
                break
        if s6 is None:
            return False
        for i in range(s6, len(lines)):
            if lines[i].startswith("### ") and i > s6:
                break
            lines[i] = lines[i].replace("160×100 台架板帧", "【帧标签被抽掉】").replace("B160x100", "【帧id被抽掉】")
        new = "\n".join(lines)
        open(f, "w", encoding="utf-8").write(new)
        return new != txt
    case("⑧ 抽掉作业包 S6 段的帧标签 ⇒ C1 红", WORKPACKET_REL, m8, "C1", "BOARD_ONEPASS_WORKPACKET.md")

    # ── ★★ISS-283 · ⑪: C6 的【落表台账为准】口径的反向用例 (★≥4 条★) ★─
    #   ① 台账有登记且一致 ⇒ 绿   ⇒ 见下面的【正向基线】检查 (★正向·必须绿★)
    #   ② 台账查不到 ⇒ 红          ⇒ ⑤b
    #   ③ 台账有登记但盘上 ≠ ⇒ 红  ⇒ ⑤ (★BOM 追加一行★)
    #   ④ 台账四项不齐 ⇒ 红        ⇒ ⑤c
    #   ★再加两条 fail-closed: 链断 (⑤d) / 链头无单号 (⑤e) ★

    def _ledger_lines(sb):
        f = os.path.join(sb, LANDING_LEDGER_REL)
        return f, open(f, encoding="utf-8").read()

    # ★★ISS-283 · ⑪ (★cont2 修★): 台账里【每落一次表就多一条链】⇒ 同一张 §16.2 表会出现【多次】
    #   ⇒ ★突变必须锚到【最新一条链】的那张表★ ⇒ 否则突变会打到【旧链】上 ⇒ 最新链完好 ⇒ C6 仍绿
    #   ⇒ ★★cont2 实测到的 ⑤b / ⑤c 两条反向用例「没改到 / 没判红」的根因就是这里★★
    #   (★实测: 旧写法按「整份台账里第一个匹配行」改 ⇒ 打到第 1 条链 (L1252) 上 ⇒ 最新链 (L1353) 完好
    #     ⇒ ⑤b 的计数条件 (n==1) 永远不成立 ⇒ 突变根本没发生; ⑤c 改了旧链 ⇒ C6 仍绿★)
    def _latest_162_row(sb, rel):
        """★定位【最新一条链】的 §16.2 表里【某个文件】的那一行 ⇒ (文件, 行数组, 行号) ★"""
        f, txt = _ledger_lines(sb)
        lines = txt.split("\n")
        heads = [i for i, ln in enumerate(lines) if ln.startswith("## ")]
        if not heads:
            return None
        start = heads[-1]                       # ★最新一条链 = 台账里最后一个 `##` 段头★
        secs = [i for i in range(start, len(lines))
                if lines[i].startswith("### ") and "16.2" in lines[i] and "新旧 md5" in lines[i]]
        if not secs:
            return None
        s = secs[-1]
        for i in range(s + 1, len(lines)):
            if lines[i].startswith("### ") or lines[i].startswith("## "):
                break                          # ★表到下一个段头为止★
            if lines[i].startswith("|") and ("`%s`" % rel) in lines[i]:
                return f, lines, i
        return None

    # ⑤b: 台账【最新一条链】的 §16.2 表里删掉 BOM 的登记行 ⇒ 查不到 ⇒ C6 红
    def m5b(sb):
        got = _latest_162_row(sb, "HW/BOM_v1.csv")
        if not got:
            return False
        f, lines, i = got
        del lines[i]
        open(f, "w", encoding="utf-8").write("\n".join(lines))
        return True
    case("⑤b ★★ISS-283·⑪: 落表台账【最新一条链】里删掉 BOM 的登记行 ⇒ 【查不到】⇒ C6 红",
         LANDING_LEDGER_REL, m5b, "C6", "HW/BOM_v1.csv")

    # ⑤c: 台账【最新一条链】的 §16.2 表里 BOM 那行的【新 md5】写成非 md5 串 ⇒ 四项不齐 ⇒ C6 红
    def m5c(sb):
        got = _latest_162_row(sb, "HW/BOM_v1.csv")
        if not got:
            return False
        f, lines, i = got
        parts = lines[i].split("|")
        if len(parts) < 4:
            return False
        # | 文件 | 旧 md5 | 新 md5 | 变了? |
        parts[3] = " `★(缺)★` "
        lines[i] = "|".join(parts)
        open(f, "w", encoding="utf-8").write("\n".join(lines))
        return True
    case("⑤c ★★ISS-283·⑪: 落表台账【最新一条链】里 BOM 的【新 md5】缺了 ⇒ 【四项不齐】⇒ C6 红",
         LANDING_LEDGER_REL, m5c, "C6", "HW/BOM_v1.csv")

    # ⑤d: 最新那条链的 §16.2 表整段改名 ⇒ 链断 ⇒ C6 红
    def m5d(sb):
        f, txt = _ledger_lines(sb)
        lines = txt.split("\n")
        idx = [i for i, ln in enumerate(lines)
               if ln.startswith("### ") and "16.2" in ln and "新旧 md5" in ln]
        if not idx:
            return False
        i = idx[-1]
        lines[i] = lines[i].replace("16.2", "16.9")
        open(f, "w", encoding="utf-8").write("\n".join(lines))
        return True
    case("⑤d ★★ISS-283·⑪: 落表台账里最新那条链的 §16.2 表没了 ⇒ 【链断】⇒ C6 红",
         LANDING_LEDGER_REL, m5d, "C6", "HW/BOM_v1.csv")

    # ⑤e: 最新那条链的链头单号被抹掉 ⇒ 链头无单号 ⇒ C6 红
    def m5e(sb):
        f, txt = _ledger_lines(sb)
        lines = txt.split("\n")
        idx = [i for i, ln in enumerate(lines)
               if ln.startswith("### ") and "16.2" in ln and "新旧 md5" in ln]
        if not idx:
            return False
        i = idx[-1]
        j = i
        while j >= 0 and not lines[j].startswith("## "):
            j -= 1
        if j < 0:
            return False
        lines[j] = lines[j].replace("ISS-283", "★(单号被抹掉)★")
        open(f, "w", encoding="utf-8").write("\n".join(lines))
        return True
    case("⑤e ★★ISS-283·⑪: 落表台账里最新那条链的【链头无单号】⇒ C6 红",
         LANDING_LEDGER_REL, m5e, "C6", "HW/BOM_v1.csv")

    # ⑤f (★cont2 增★): 台账【最新一条链】里 BOM 那行的【旧 md5】写成非 md5 串 ⇒ 四项不齐 ⇒ C6 红
    #   ★★反向用例只许增不许减★ ⇒ 这条补上「旧 md5 缺」那一路 (★旧写法的四项不齐只测了「新 md5 缺」★)
    def m5f(sb):
        got = _latest_162_row(sb, "HW/BOM_v1.csv")
        if not got:
            return False
        f, lines, i = got
        parts = lines[i].split("|")
        if len(parts) < 4:
            return False
        # | 文件 | 旧 md5 | 新 md5 | 变了? |
        parts[2] = " `★(缺)★` "
        lines[i] = "|".join(parts)
        open(f, "w", encoding="utf-8").write("\n".join(lines))
        return True
    case("⑤f ★★ISS-283·⑪·cont2: 落表台账【最新一条链】里 BOM 的【旧 md5】缺了 ⇒ 【四项不齐】⇒ C6 红",
         LANDING_LEDGER_REL, m5f, "C6", "HW/BOM_v1.csv")

    # ⑤g (★cont2 增★): 台账【最新一条链】里有【两张】§16.2 表 ⇒ 链头不唯一 ⇒ 取不准 ⇒ C6 红
    def m5g(sb):
        f, txt = _ledger_lines(sb)
        lines = txt.split("\n")
        heads = [i for i, ln in enumerate(lines) if ln.startswith("## ")]
        if not heads:
            return False
        start = heads[-1]
        secs = [i for i in range(start, len(lines))
                if lines[i].startswith("### ") and "16.2" in lines[i] and "新旧 md5" in lines[i]]
        if not secs:
            return False
        s = secs[-1]
        lines.insert(s + 1, lines[s])          # ★复制一张 §16.2 表头 ⇒ 链头不唯一★
        open(f, "w", encoding="utf-8").write("\n".join(lines))
        return True
    case("⑤g ★★ISS-283·⑪·cont2: 落表台账【最新一条链】的 §16.2 表【有两张】⇒ 【链头不唯一】⇒ C6 红",
         LANDING_LEDGER_REL, m5g, "C6", "HW/BOM_v1.csv")

    # ★正向基线 (★ISS-283 · ⑪ 的 ①: 台账有登记且一致 ⇒ 绿★) ★
    sb0 = build_sandbox(root, base)
    _res0, _ = run_checks(sb0)
    _c6 = {x.code: x for x in _res0}.get("C6")
    _pos_ok = _c6 is not None and _c6.ok
    if not _pos_ok:
        print("★ 正向基线: 沙盒原样 (台账有登记且一致) ⇒ C6 必须绿 ★★FAIL★★")
        for _ln in (_c6.lines if _c6 else []):
            print("      " + _ln[:160])
    else:
        print("★ 正向基线: 沙盒原样 (台账有登记且一致) ⇒ C6 绿 ✔")

    print("=" * 78)
    print("ISS-274 · --selftest 反向用例 (每条自证「真的改到了目标那一处」)")
    print("=" * 78)
    print(f"沙盒副本 = {base}")
    failed = 0
    for idx, c in enumerate(cases, 1):
        sb = build_sandbox(root, base)
        tgt = os.path.join(sb, c["target"])
        before = md5(tgt)
        changed = c["mutate"](sb)
        after = md5(tgt)
        res, _ = run_checks(sb)
        by_code = {x.code: x for x in res}
        r = by_code.get(c["code"])
        red = (r is not None) and (not r.ok)
        hit_ref = (r is not None) and any(c["ref"] in str(a) for a in r.anomalies) or \
            (r is not None) and any(c["ref"] in ln for ln in r.lines)
        msg_ok = True
        if c["msg"]:
            msg_ok = any(c["msg"] in ln for ln in (r.lines if r else []))
        tampered = (before != after) and changed
        good = tampered and red and hit_ref and msg_ok
        if not good:
            failed += 1
        print(f"\n[{idx}] {c['name']}")
        print(f"    改动目标 : {c['target']}")
        print(f"    自证改动 : md5 {before[:8]}… → {after[:8]}…  "
              f"({'确实改到了目标那一处' if tampered else '★没改到★'})")
        print(f"    期望判红 : {c['code']}  实测: {'RED' if red else 'GREEN'} "
              f"{'★没判红★' if not red else ''}")
        print(f"    期望点名 : {c['ref']}  实测命中: {'是' if hit_ref else '★否★'}")
        if c["msg"]:
            print(f"    期望文本 : 「{c['msg']}」  实测命中: {'是' if msg_ok else '★否★'}")
        print(f"    结论     : {'PASS' if good else '★FAIL★'}")
        if r is not None and not r.ok:
            for ln in r.lines:
                if ln.startswith("✗"):
                    print("      " + ln[:160])
    print("\n" + "=" * 78)
    print(f"反向用例: {len(cases)} 条, 失败 {failed} 条 ⇒ "
          + ("全部被闸抓住 ✔" if failed == 0 else "★有漏网★"))
    if not _pos_ok:
        failed += 1
    print("=" * 78)
    return 0 if failed == 0 else 1


# ======================================================================
# main
# ======================================================================

def update_baseline(root):
    root = os.path.abspath(root)
    path = os.path.join(root, CALIB_REL)
    txt = open(path, encoding="utf-8").read()
    pat = re.compile(r"(```json\s+cal:PROTECTED_MD5\s*\n)(.*?)(\n```)", re.S)
    m = pat.search(txt)
    if not m:
        raise SystemExit("[calib] 找不到 cal:PROTECTED_MD5 块")
    obj = json.loads(m.group(2))
    for rel in obj.get("files", {}):
        fp = os.path.join(root, rel)
        obj["files"][rel] = md5(fp)
    obj["note"] = obj.get("note", "") + " · 基线重录于 ISS-274 校准页更新"
    new = json.dumps(obj, ensure_ascii=False, indent=2)
    open(path, "w", encoding="utf-8").write(txt[:m.start(2)] + new + txt[m.end(2):])
    print("[calib] 受保护件 md5 基线已重录 →", obj["files"])
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=DEFAULT_ROOT, help="项目根 (默认 = 本文件上级)")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--json", default=None, help="机器可读报告输出路径")
    ap.add_argument("--update-baseline", action="store_true",
                    help="重录受保护 5 件 md5 基线 (★需 main 批准★)")
    ap.add_argument("--sandbox-base", default=WORKSPACE_TMP,
                    help="--selftest 的沙盒副本根 (★不许用 /tmp★)")
    args = ap.parse_args()

    if args.update_baseline:
        return update_baseline(args.root)

    if args.selftest:
        base = args.sandbox_base
        if not os.path.isdir(base):
            raise SystemExit(f"[selftest] 沙盒根不存在: {base} (★不许用 /tmp★)")
        return selftest(args.root, base)

    results, extra = run_checks(args.root)
    print("=" * 78)
    print("ISS-274 · 板框 / 坐标系口径机器闸 (C1~C6)")
    print(f"根目录 = {os.path.abspath(args.root)}")
    print("=" * 78)
    allok = True
    for r in results:
        print(f"\n[{r.code}] {r.title}")
        for ln in r.lines:
            print("    " + ln)
        print(f"    ⇒ {r.code} {'PASS' if r.ok else 'FAIL'}")
        allok = allok and r.ok
    print("\n" + "-" * 78)
    print(f"板框 (含线宽) = {extra['board_edge_stroke'][2] - extra['board_edge_stroke'][0]:.2f} × "
          f"{extra['board_edge_stroke'][3] - extra['board_edge_stroke'][1]:.2f} mm · "
          f"铜层 {extra['copper_layers']} · 封装 {extra['footprint_count']} · "
          f"现役帧 {extra['frame_current']}")
    print(f"S6: 已在目标位 {len(extra['at_target'])} / 不同 {len(extra['differ'])} "
          f"{sorted(extra['differ'])} / 缺失 {len(extra['missing'])}")
    print(f"总判: {'全部通过 ✔' if allok else '★有红项★'}")
    print("-" * 78)

    if args.json:
        payload = {
            "issue": "ISS-274",
            "root": os.path.abspath(args.root),
            "all_ok": allok,
            "checks": [{"code": r.code, "title": r.title, "ok": r.ok,
                        "lines": r.lines, "anomalies": r.anomalies} for r in results],
            "extra": {k: (list(v) if isinstance(v, tuple) else v) for k, v in extra.items()},
        }
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=1, default=str)
        print(f"机器可读报告 → {args.json}")

    return 0 if allok else 1


if __name__ == "__main__":
    sys.exit(main())
