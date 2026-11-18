#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_onepass_mech_sync.py —— ★★【ISS-278 · 「板只改一次」那一趟的 MECH 侧板侧输入 · 机器闸】★★

★★★**★这个闸守的是什么★**★★
  上一趟 (ISS-267/271) 的病根 = ★**「检修口/调试口」被当成一个开口**, 于是那一趟照抄了合并的错值 ⇒ 板改第二次。
  本闸把「板只改一次」那一趟要用的 MECH 侧输入收成【一份规格 (MECH/BOARD_ONEPASS_MECH_SYNC.md §5 机器块) + 一道闸】:

    M1  ★**帧标签齐全** —— 清单里出现的坐标组必须带帧标签 (漏标一条即红) 且帧 id ∈ {B160x100, F30A, P60x15} (不许造第四套)
    M2  ★**两条开口各自不压 SoM 座** —— 读板 ⇒ 检修口矩形压 J_SOM_P1..P4 焊盘数 = 0, 调试口矩形同样 = 0 (两条分别验, 不许合并验)
    M3  ★**座体高度参数式自洽** —— 代入 h 的三档 ⇒ 开口 Y 单调合理 + 落在现役板框内 + 不压 SoM 座 (任一档不过 ⇒ 红)
    M4  ★**判据命令真存在** —— 清单里每条 criterion 的命令必须在本机真实存在 (照 state/check_brief_commands.py 的口径)
    M5  ★**受保护 5 件 md5 逐字节不变** (板 / .kicad_pro / 网表 / 脚表 / BOM)
        ★★**2026-11-17 ISS-278 续做修订 (★实测发现的真缺口, 必须写清楚★)** ★★
        ★本闸原先只查 `CFC.PROTECTED` ⇒ ★**ISS-286 在 12:44 把 PROTECTED 从 5 件改成「板 + .kicad_pro」两件**
          (网表/脚表/BOM 改归【落表台账】管) ⇒ ★**本闸的 M5 跟着从 5 件缩成 2 件 = 覆盖面被悄悄削掉一半** ★
        ★⇒ 现在 M5 分两段, ★**5 件一件都不少** ★:
          ★**M5a 硬基线 2 件** (板 / .kicad_pro) ⇒ 基线写死, 一条不许动 ★
          ★**M5b 台账管理 3 件** (网表 / 脚表 / BOM) ⇒ ★**判决源 = 落表台账链头** (`HW/SCHEMATIC_LANDING_V1_LANDED.md`),
            ★**照 ISS-286 的 C4 同构口径** ⇒ 盘上 md5 必须 == 台账链头, 且链不许断 / 不许孤儿 / 链头要能取准,
            ★**取不准一律 fail-closed 判红 (★不许静默判绿★)** ★
        ★⇒ 净效果: 合法落表 (链头前移) ⇒ 绿; 偷改真源不更新台账 ⇒ 红; 台账读不到 / 链断 ⇒ 红 ★

  ★**只读 import MECH/check_board_frame_coords.py** ⇒ 阈值 (CRIT / TOL / OPEN_X / OPEN_Y / EDGE_KEEPOUT / PROTECTED) 零漂移,
    ★**本闸是【新建】文件, 一个字不改既有 MECH 判据脚本**★

用法:
    python3 MECH/check_onepass_mech_sync.py            # rc=0 = 全绿
    python3 MECH/check_onepass_mech_sync.py --json     # 机器读
    python3 MECH/check_onepass_mech_sync.py --selftest # rc=0 = 反向用例全抓到 (★沙盒副本上跑, 真件一个字节不碰★)
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, ".."))

SPEC_REL = os.path.join("MECH", "BOARD_ONEPASS_MECH_SYNC.md")
MACH_BEGIN = "<!-- MACHINE-BLOCK-BEGIN -->"
MACH_END = "<!-- MACHINE-BLOCK-END -->"

# ★帧 id 白名单 (★与 ISS-274 的口径一致, 不许造第四套★) ★
FRAMES_ALLOWED = ("B160x100", "F30A", "P60x15")

# ★ISS-294: 开口 id 【集合】 (★恰好三条, 一条不少一条不多★)
# ★★纪律: 合并禁令不靠【条数】守, 靠【期望 id 集合 + 任意两条矩形不许完全相同】守 ★★
# ★★⇒ 不许把 `!= 2` 改成 `!= 3` 就完事 (那是把「两条不许合并」偷换成「三条不许合并」⇒ 合并成一条照样能过) ★★
EXPECTED_OPENING_IDS = ("PORT_OPEN_DEBUG", "PORT_OPEN_UART", "PORT_OPEN_USBC")

# ★ISS-294: 边开口的语义标记 (★role 里写「边开口」+ 矩形下沿锚在板边线 ⇒ 两边必须同时成立★) ★
EDGE_ROLE_MARK = "边开口"

# ★判据命令里抠脚本路径用的正则 (★照 state/check_brief_commands.py 的口径: 只认带目录的相对路径 + 裸 .py/.sh★) ★
CMD_RE = re.compile(r"python3\s+([\w./+-]+\.py)")
# ★正文里「帧: xxx」的 id 抽取 (★只认 [A-Za-z] 开头的 id; 「帧: 160×100 台架板」这种描述性短语跳过★) ★
FRAME_ID_RE = re.compile(r"帧[:：]\s*([^\s,，。;；)）]{1,24})")


# ==================================================================================================
# ★只读 import 既有闸 (阈值零漂移) ★
# ==================================================================================================
def load_cfc():
    path = os.path.join(PROJ, "MECH", "check_board_frame_coords.py")
    spec = importlib.util.spec_from_file_location("cfc_iss278_readonly", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)          # ★只执行模块顶层 (无副作用)★
    return mod


CFC = load_cfc()


# ==================================================================================================
# 规格页机器块读取 (★只读★)
# ==================================================================================================
def read_spec(root: str) -> dict:
    path = os.path.join(root, SPEC_REL)
    if not os.path.exists(path):
        raise SystemExit(f"[check_onepass_mech_sync] 找不到规格页: {path}")
    text = open(path, "r", encoding="utf-8").read()
    b = text.find(MACH_BEGIN)
    e = text.find(MACH_END)
    if b < 0 or e < 0:
        raise SystemExit("[check_onepass_mech_sync] 规格页缺机器块标记 "
                         f"({MACH_BEGIN} / {MACH_END})")
    seg = text[b:e]
    m = re.search(r"```json\n(.*?)\n```", seg, re.S)
    if not m:
        raise SystemExit("[check_onepass_mech_sync] 规格页机器块不是 ```json 围栏")
    data = json.loads(m.group(1))
    if not isinstance(data, dict):
        raise SystemExit("[check_onepass_mech_sync] 机器块顶层不是 dict")
    data["_text"] = text
    data["_span"] = (text[:b].count("\n") + 1, text[:e].count("\n") + 1)
    return data


def _rect_of(d: dict):
    for k in ("rect", "space"):
        if isinstance(d.get(k), dict):
            r = d[k]
            try:
                return (float(r["x0"]), float(r["x1"]), float(r["y0"]), float(r["y1"]))
            except (KeyError, TypeError, ValueError):
                return None
    return None


def _walk_rects(obj, path, out):
    """★把机器块里所有带 rect / space 的坐标组连同它的 frame 一起抠出来★"""
    if isinstance(obj, dict):
        if _rect_of(obj) is not None:
            out.append((path, obj.get("frame"), _rect_of(obj)))
        for k, v in obj.items():
            _walk_rects(v, f"{path}.{k}", out)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            _walk_rects(v, f"{path}[{i}]", out)


# ==================================================================================================
# ★ISS-294: 座体 `F.Fab` 只读读取 (★自带小解析器, 不改既有判据脚本★)
# ★★为什么自带: `MECH/check_board_frame_coords.py` 的 fab 正则只认 `fp_line`,
#   而 `J_USB_C` 的 F.Fab 画的是 `fp_rect` ⇒ 那个闸读不到 ⇒ 边开口的座体几何在本闸里自己读★ ★
# ==================================================================================================
_FP_GEO_RE = re.compile(r"\((fp_rect|fp_line)\b(.*?)\n\t\t\)", re.S)


def _rot_pt(x, y, rot):
    r = int(round(rot)) % 360
    if r == 90:
        return (-y, x)
    if r == 180:
        return (-x, -y)
    if r == 270:
        return (y, -x)
    return (x, y)


def fab_bbox_of(root: str, ref: str):
    """读板 ⇒ 某 ref 的 F.Fab 外框 (落位后) = (x0, x1, y0, y1); 读不到返回 None (★只读★)"""
    path = os.path.join(root, CFC.PCB_REL)
    if not os.path.exists(path):
        return None
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
            i = j + 1
            if f'(property "Reference" "{ref}"' not in blk:
                continue
            m = re.search(r'\n\t\t\(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)', blk)
            if not m:
                return None
            ox, oy = float(m.group(1)), float(m.group(2))
            rot = float(m.group(3) or 0.0)
            pts = []
            for gm in _FP_GEO_RE.finditer(blk):
                body = gm.group(2)
                lay = re.search(r'\(layer "([^"]+)"\)', body)
                if not lay or lay.group(1) != "F.Fab":
                    continue
                st = re.search(r'\(start ([-\d.]+) ([-\d.]+)\)', body)
                en = re.search(r'\(end ([-\d.]+) ([-\d.]+)\)', body)
                if not st or not en:
                    continue
                for (lx, ly) in ((float(st.group(1)), float(st.group(2))),
                                 (float(en.group(1)), float(en.group(2)))):
                    dx, dy = _rot_pt(lx, ly, rot)
                    pts.append((ox + dx, oy + dy))
            if not pts:
                return None
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            return (min(xs), max(xs), min(ys), max(ys))
        else:
            i += 1
    return None


def _edge_geometry(root: str, ref: str, fps: dict):
    """★边开口的板读几何: 座体 F.Fab 外框 ∪ 两个壳体固定孔 (NPTH) 外缘 ⇒ 必须清空区★"""
    f = fps.get(ref)
    if not f:
        return None
    fab = fab_bbox_of(root, ref)
    if fab is None:
        return None
    npth = []
    for p in f["pads"]:
        if p.get("type") != "np_thru_hole":
            continue
        npth.append((p["x"] - p["sx"] / 2.0, p["x"] + p["sx"] / 2.0,
                     p["y"] - p["sy"] / 2.0, p["y"] + p["sy"] / 2.0))
    x0 = min([fab[0]] + [b[0] for b in npth]) if npth else fab[0]
    x1 = max([fab[1]] + [b[1] for b in npth]) if npth else fab[1]
    y0 = min([fab[2]] + [b[2] for b in npth]) if npth else fab[2]
    y1 = max([fab[3]] + [b[3] for b in npth]) if npth else fab[3]
    return {"fab": fab, "npth": npth, "mc": (x0, x1, y0, y1),
            "fab_depth": fab[3] - fab[2]}


def _is_edge_opening(o: dict, edge: dict):
    """★边开口判定: role 写「边开口」与「矩形下沿锚在板边线」必须同时成立 (★任一不成立 ⇒ 红★)★
    返回 (是否边开口, 说明)"""
    role = str(o.get("role") or "")
    by_role = EDGE_ROLE_MARK in role
    r = _rect_of(o)
    by_geom = bool(r) and abs(r[2] - float(edge["y0"])) <= 1e-6
    if by_role and by_geom:
        return True, "role 标「边开口」+ 下沿锚在板边线"
    if by_role and not by_geom:
        return False, f"role 标「边开口」但矩形下沿 {r[2] if r else None} 没锚在板边线 {edge['y0']}"
    if by_geom and not by_role:
        return False, f"矩形下沿锚在板边线但 role 没标「边开口」 (role={role!r})"
    return False, "板内洞 (老规则)"


# ==================================================================================================
# M1 · 帧标签
# ==================================================================================================
def check_m1(root: str, spec: dict) -> dict:
    errs = []
    allowed = set(spec.get("frames_allowed") or FRAMES_ALLOWED)
    allowed |= set(FRAMES_ALLOWED)
    rows = []

    # --- M1a 机器块: 每个坐标组必须带 frame 且 ∈ 白名单 ---
    rects = []
    _walk_rects(spec.get("openings"), "openings", rects)
    _walk_rects(spec.get("led"), "led", rects)
    for path, fid, rect in rects:
        ok = bool(fid) and fid in allowed
        rows.append({"where": path, "frame": fid, "rect": rect, "ok": ok})
        if not fid:
            errs.append(f"M1a 坐标组 '{path}' 缺 frame 标签")
        elif fid not in allowed:
            errs.append(f"M1a 坐标组 '{path}' 的 frame='{fid}' 不在白名单 {sorted(allowed)} "
                        f"⇒ 不许造第四套帧")
    if not rects:
        errs.append("M1a 机器块里一个坐标组都没抠到 ⇒ 闸没东西可查")

    # --- M1b 清单条目: 每条都必须带 frame 且 ∈ 白名单 ---
    items = spec.get("items") or []
    if not items:
        errs.append("M1b 机器块 items[] 为空 ⇒ 清单没落")
    for it in items:
        fid = it.get("frame")
        if not fid:
            errs.append(f"M1b 条目 '{it.get('id')}' 缺 frame 标签")
        elif fid not in allowed:
            errs.append(f"M1b 条目 '{it.get('id')}' 的 frame='{fid}' 不在白名单 {sorted(allowed)}")

    # --- M1c 正文: 坐标行必须挂帧标签 (照 ISS-276 C1b 的严格口径: 本行 / 表头 / 标题) ---
    text = spec["_text"]
    ls, le = spec["_span"]
    lines = text.split("\n")
    detail = []
    for i, line in enumerate(lines):
        if ls <= i + 1 <= le:
            continue                                    # ★机器块本身跳过 (机器块由 M1a/M1b 管)★
        if len(CFC.NUM_RE.findall(line)) < 2:
            continue
        ok, src = CFC._frame_source(lines, i)
        if not ok:
            errs.append(f"M1c 规格页第 {i + 1} 行坐标组漏帧标签 ({src}): {line.strip()[:90]}")
            detail.append({"line": i + 1, "text": line.strip()[:90], "src": src})

    # --- M1d 正文里出现的帧 id 必须 ∈ 白名单 ---
    body = "\n".join(lines[:ls - 1] + lines[le - 1:])
    for m in FRAME_ID_RE.finditer(body):
        tok = m.group(1).strip().strip("*`").strip()
        if re.fullmatch(r"[A-Za-z][A-Za-z0-9]*", tok) and tok not in allowed:
            errs.append(f"M1d 正文出现白名单外的帧 id '{tok}' ⇒ 不许造第四套帧")

    # --- M1e 默认帧必须 ∈ 白名单 ---
    fd = spec.get("frame_default")
    if fd not in allowed:
        errs.append(f"M1e frame_default='{fd}' 不在白名单 {sorted(allowed)}")

    return {"ok": not errs, "errs": errs, "detail": detail,
            "frames_allowed": sorted(allowed), "n_rects": len(rects),
            "n_items": len(items)}


# ==================================================================================================
# M2 · 两条开口各自不压 SoM 座 (★两条分别验, 不许合并验★)
# ==================================================================================================
def check_m2(root: str, spec: dict, board: dict) -> dict:
    errs = []
    fps = board["fps"]
    som_pads = []
    for r in CFC.SOM_REFS:
        f = fps.get(r)
        if f:
            som_pads += f["pads"]
    openings = spec.get("openings") or []
    ids = [o.get("id") for o in openings]
    # ★ISS-294: 【条数断言】⇒【期望 id 集合断言】(★恰好三条, 一条不少一条不多★)
    # ★★合并禁令不靠条数守 (★靠 M2b「任意两条矩形不许完全相同」+ 这条集合断言双守★) ★★
    if sorted(ids) != sorted(EXPECTED_OPENING_IDS):
        errs.append(f"M2 开口 id 集合 = {ids} (期望恰好 {sorted(EXPECTED_OPENING_IDS)}: "
                    f"检修口 + 调试口 + USB-C 边开口; 少一条 / 改 id / 合并成一条 ⇒ 红)")
    if len(set(ids)) != len(ids):
        errs.append(f"M2 开口 id 有重复 = {ids} ⇒ 等于把两条合并成一条 ⇒ 红")
    rows = []
    for o in openings:
        rect = _rect_of(o)
        if rect is None:
            errs.append(f"M2 开口 '{o.get('id')}' 没有 rect")
            continue
        n = CFC.rect_hits(rect, som_pads)
        per = CFC.rect_hits_per(rect, fps, CFC.SOM_REFS)
        rows.append({"id": o.get("id"), "role": o.get("role"), "covers": o.get("covers"),
                     "frame": o.get("frame"), "rect": rect, "som_hits": n, "per_ref": per})
        if n != 0:
            errs.append(f"M2 开口 '{o.get('id')}' ({o.get('role')}) 压住 {n} 个 SoM 焊盘 {per}")
        if o.get("frame") != CFC.BENCH_FRAME:
            errs.append(f"M2 开口 '{o.get('id')}' 的 frame='{o.get('frame')}' 不是现役板帧 "
                        f"{CFC.BENCH_FRAME} ⇒ M2 无法在现役板上验它")

    # --- M2b 任意两条开口必须真的不同 (★不许合并成一个矩形 / 不许把 USB-C 并进检修口·调试口★) ---
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            a, b = rows[i]["rect"], rows[j]["rect"]
            if all(abs(x - y) < 1e-9 for x, y in zip(a, b)):
                errs.append(f"M2b 开口 '{rows[i]['id']}' 与 '{rows[j]['id']}' 的矩形完全相同 ⇒ "
                            f"等于合并 ⇒ 红")

    # --- M2c 合并禁令必须登记, 且缺口 = 板读实算值 ---
    mo = spec.get("merged_opening") or {}
    if not mo:
        errs.append("M2c 机器块缺 merged_opening (合并禁令的登记)")
    else:
        if not mo.get("forbidden"):
            errs.append("M2c merged_opening.forbidden 不为 true ⇒ 合并禁令没登记")
        gap = mo.get("gap_mm")
        # ★ISS-294: 合并缺口的复算【只取 merged_opening.covers 点名的那些座体】
        # ★★⇒ 否则多一条开口 (USB-C 边开口) 就会把「恰好两条」的判据悄悄跳过 ⇒ 防线反而松了★★
        refs = [r.strip() for r in str(mo.get("covers") or "").split("+") if r.strip()]
        if len(refs) < 2:
            errs.append(f"M2c merged_opening.covers = {mo.get('covers')!r} 点名的座体不足 2 个 ⇒ "
                        f"合并禁令的复算无从下手 ⇒ 红")
        conns = {}
        for r in refs:
            f = fps.get(r)
            if not f:
                errs.append(f"M2c merged_opening.covers 里的 '{r}' 在盘上读不到 ⇒ 红")
                continue
            if r not in {o.get("covers") for o in openings}:
                errs.append(f"M2c merged_opening.covers 里的 '{r}' 不在 openings[] 里 ⇒ "
                            f"合并禁令指向的座体不存在 ⇒ 红")
            ps = f["pads"]
            cx = sum(p["x"] for p in ps) / len(ps)
            w = 0.0
            for o in openings:
                if o.get("covers") == r:
                    w = float(o.get("body_w") or 0.0)
                    break
            conns[r] = (cx - w / 2, cx + w / 2)
        if len(refs) >= 2 and len(conns) == len(refs):
            xs = [v for c in conns.values() for v in c]
            content_w = max(xs) - min(xs)
            real_gap = content_w - float(mo.get("open_w") or 0.0)
            if gap is None or abs(float(gap) - real_gap) > 0.01:
                errs.append(f"M2c 合并缺口声明 {gap} 与实算 {real_gap:.6f} 不符 (差 >0.01)")
            if real_gap <= 0:
                errs.append(f"M2c 实算合并缺口 {real_gap:.6f} ≤ 0 ⇒ 合并本可行 ⇒ "
                            f"「必须拆两条」的前提没了")
    return {"ok": not errs, "errs": errs, "rows": rows, "som_pads": len(som_pads),
            "ids": ids, "expected_ids": list(EXPECTED_OPENING_IDS)}


def _m3_edge_rows(root, o, fps, edge, tiers, open_y, crit, tol, keep, som_pads,
                  h_ref, errs):
    """★ISS-294: 【边开口】分支 (板边缺口) 的逐档判据 ★
      · ★**下沿必须锚在板边线** (另一侧是板外 ⇒ 缺口【没有中心】 ⇒ 不许用「Y 居中于器件中心」的公式)★
      · ★**X 必须 = (座体 F.Fab ∪ 两个壳体固定孔外缘) ± (CRIT + TOL)** (固定孔比座体外形还往外 1.46 ⇒ 开口必须更宽)★
      · ★**Y 深度 = max(座体 Y 深度, OPEN_Y_eff(h)) + (CRIT + TOL)** ⇒ h 三档逐档代入 (不把 2.54 当事实)
    """
    rows = []
    ref = o.get("covers")
    g = _edge_geometry(root, ref, fps)
    if g is None:
        errs.append(f"M3 边开口 '{o.get('id')}' 读不到座体 F.Fab / 固定孔 (板读失败) ⇒ 红")
        return rows
    mc, fab = g["mc"], g["fab"]
    fab_h = fab[3] - fab[2]
    allow = crit + tol
    decl = _rect_of(o)
    prev_eff = None
    for h in tiers:
        need = h + 2 * (crit + tol)
        eff = max(open_y, need)
        depth = max(g["fab_depth"], eff) + allow
        rect = (mc[0] - allow, mc[1] + allow, float(edge["y0"]),
                float(edge["y0"]) + depth)
        in_frame = (rect[0] >= edge["x0"] + keep and rect[1] <= edge["x1"] - keep
                    and rect[3] <= edge["y1"] - keep)
        som = CFC.rect_hits(rect, som_pads)
        cl_x = (rect[1] - rect[0] - (mc[1] - mc[0])) / 2.0
        cl_y = rect[3] - mc[3]
        worst_cl_x = cl_x - tol
        worst_cl_y = cl_y - tol
        row = {"id": o.get("id"), "h": h, "need": round(need, 6), "eff": round(eff, 6),
               "rect": tuple(round(v, 4) for v in rect), "in_frame": in_frame,
               "som_hits": som, "worst_cl_y": round(worst_cl_y, 6),
               "worst_cl_x": round(worst_cl_x, 6),
               "fab_h_physical": round(fab_h, 4), "kind": "edge_notch"}
        rows.append(row)
        # ① 物理合理性: 0 < h ≤ 座体 F.Fab 盒高
        if not (0 < h <= fab_h + 1e-9):
            errs.append(f"M3 边开口 '{o.get('id')}' h={h} 不在物理合理区间 (0, {fab_h:.2f}] "
                        f"⇒ 座体高度这一档不合理")
        # ② 单调: eff 随 h 非减
        if prev_eff is not None and eff < prev_eff - 1e-9:
            errs.append(f"M3 边开口 '{o.get('id')}' 开口 Y 随 h 不单调 (eff {prev_eff} ⇒ {eff})")
        prev_eff = eff
        # ③ 落板框内 (★下沿本来就锚在板边线 ⇒ 不判下沿★)
        if not in_frame:
            errs.append(f"M3 边开口 '{o.get('id')}' h={h} 的开口 {row['rect']} 超出板框 "
                        f"(边距带 {keep})")
        # ④ 不压 SoM 座
        if som != 0:
            errs.append(f"M3 边开口 '{o.get('id')}' h={h} 的开口压住 {som} 个 SoM 焊盘")
        # ⑤ 最坏单边净距 ≥ CRIT (X 向 + Y 向)
        if worst_cl_x < crit - 1e-9:
            errs.append(f"M3 边开口 '{o.get('id')}' h={h} 的 X 向单边间隙最坏 "
                        f"{worst_cl_x:.6f} < CRIT {crit} ⇒ 判红")
        if worst_cl_y < crit - 1e-9:
            errs.append(f"M3 边开口 '{o.get('id')}' h={h} 的 Y 向单边间隙最坏 "
                        f"{worst_cl_y:.6f} < CRIT {crit} ⇒ 判红")
        # ⑥ 声明矩形必须【覆盖】该档算出来的矩形 (不许比要求的小)
        if decl and (decl[0] > rect[0] + 0.01 or decl[1] < rect[1] - 0.01
                     or decl[2] > rect[2] + 0.01 or decl[3] < rect[3] - 0.01):
            errs.append(f"M3 边开口 '{o.get('id')}' h={h} 的声明矩形 {decl} 没覆盖该档算出来的 "
                        f"{tuple(round(v, 4) for v in rect)} ⇒ 声明值与参数式不自洽")
    # ⑦ 声明矩形 == h_ref 档算出来的矩形 (自洽, 与老开口同一个口径)
    if decl and h_ref in tiers:
        need = h_ref + 2 * (crit + tol)
        eff = max(open_y, need)
        depth = max(g["fab_depth"], eff) + allow
        calc = (mc[0] - allow, mc[1] + allow, float(edge["y0"]),
                float(edge["y0"]) + depth)
        if any(abs(a - b) > 0.01 for a, b in zip(calc, decl)):
            errs.append(f"M3 边开口 '{o.get('id')}' 声明矩形 {decl} 与按公式算的 "
                        f"{tuple(round(v, 4) for v in calc)} 不符 (差 >0.01) ⇒ "
                        f"声明值与参数式不自洽")
    return rows


# ==================================================================================================
# M3 · 座体高度参数式自洽 (★h = [0数据] ⇒ 三档逐档代入★)
# ==================================================================================================
def check_m3(root: str, spec: dict, board: dict) -> dict:
    errs = []
    fps = board["fps"]
    edge = board["edge"]
    consts = spec.get("consts") or {}
    open_x = float(consts.get("open_x_spec") or CFC.OPEN_X)
    open_y = float(consts.get("open_y_spec") or CFC.OPEN_Y)
    crit = float(consts.get("crit") or CFC.CRIT)
    tol = float(consts.get("tol_fdm_part") or CFC.TOL["fdm_part"])
    keep = float(consts.get("edge_keepout") or CFC.EDGE_KEEPOUT)
    tiers = [float(v) for v in (consts.get("h_tiers") or [])]
    if len(tiers) < 3:
        errs.append(f"M3 h 三档不足 (只有 {len(tiers)} 档) ⇒ 座体高度参数化没落地")
    if not tiers:
        return {"ok": False, "errs": errs, "rows": []}

    som_pads = []
    for r in CFC.SOM_REFS:
        f = fps.get(r)
        if f:
            som_pads += f["pads"]

    rows = []
    for o in (spec.get("openings") or []):
        ref = o.get("covers")
        f = fps.get(ref)
        if not f:
            errs.append(f"M3 开口 '{o.get('id')}' 的 covers='{ref}' 在盘上板读不到")
            continue
        # ★ISS-294: 边开口走【边开口分支】(★另两条还是老规则, 一行没改★)
        edge_open, why = _is_edge_opening(o, edge)
        if edge_open:
            rows += _m3_edge_rows(root, o, fps, edge, tiers, open_y, crit, tol, keep,
                                  som_pads, float(consts.get("body_h_ref") or 0.0), errs)
            continue
        if why != "板内洞 (老规则)":
            errs.append(f"M3 开口 '{o.get('id')}' 的语义判据不成立: {why}")
        ps = f["pads"]
        cx = sum(p["x"] for p in ps) / len(ps)
        cy = sum(p["y"] for p in ps) / len(ps)
        w = float(o.get("body_w") or 0.0)
        cl_x = (open_x - w) / 2.0
        bx0, bx1 = cx - w / 2.0, cx + w / 2.0
        # ★座体物理上界 = 板自己给该连接器占的 F.Fab 盒高 (★板读★) ★
        fb = CFC.fab_bbox(f)
        # ★fab_bbox 返回 (x0, x1, y0, y1) ⇒ 高 = fb[3] - fb[2]★
        fab_h = (fb[3] - fb[2]) if fb else 0.0
        prev_eff = None
        for h in tiers:
            need = h + 2 * (crit + tol)
            eff = max(open_y, need)
            y0, y1 = cy - eff / 2.0, cy + eff / 2.0
            rect = (bx0 - cl_x, bx1 + cl_x, y0, y1)
            in_frame = (rect[0] >= edge["x0"] + keep and rect[1] <= edge["x1"] - keep
                        and rect[2] >= edge["y0"] + keep and rect[3] <= edge["y1"] - keep)
            som = CFC.rect_hits(rect, som_pads)
            worst_cl_y = (eff - h) / 2.0 - tol
            row = {"id": o.get("id"), "h": h, "need": round(need, 6), "eff": round(eff, 6),
                   "rect": tuple(round(v, 4) for v in rect), "in_frame": in_frame,
                   "som_hits": som, "worst_cl_y": round(worst_cl_y, 6),
                   "fab_h_physical": round(fab_h, 4)}
            rows.append(row)
            # ① 物理合理性: 0 < h ≤ 板自己给的座体盒高
            if not (0 < h <= fab_h + 1e-9):
                errs.append(f"M3 '{o.get('id')}' h={h} 不在物理合理区间 (0, {fab_h:.2f}] "
                            f"⇒ 座体高度这一档不合理")
            # ② 单调: eff 随 h 非减
            if prev_eff is not None and eff < prev_eff - 1e-9:
                errs.append(f"M3 '{o.get('id')}' 开口 Y 随 h 不单调 (eff {prev_eff} ⇒ {eff})")
            prev_eff = eff
            # ③ 落板框内
            if not in_frame:
                errs.append(f"M3 '{o.get('id')}' h={h} 的开口 {row['rect']} 超出板框 (边距带 {keep})")
            # ④ 不压 SoM 座
            if som != 0:
                errs.append(f"M3 '{o.get('id')}' h={h} 的开口压住 {som} 个 SoM 焊盘")
            # ⑤ 单边间隙最坏口径 ≥ CRIT
            if worst_cl_y < crit - 1e-9:
                errs.append(f"M3 '{o.get('id')}' h={h} 的单边间隙最坏 {worst_cl_y:.6f} < "
                            f"CRIT {crit} ⇒ 判红")
        # ⑥ 声明矩形 == h_ref 档算出来的矩形 (自洽)
        h_ref = float(consts.get("body_h_ref") or 0.0)
        if h_ref in tiers:
            need = h_ref + 2 * (crit + tol)
            eff = max(open_y, need)
            calc = (bx0 - cl_x, bx1 + cl_x, cy - eff / 2.0, cy + eff / 2.0)
            decl = _rect_of(o)
            if decl and any(abs(a - b) > 0.01 for a, b in zip(calc, decl)):
                errs.append(f"M3 '{o.get('id')}' 声明矩形 {decl} 与按公式算的 {tuple(round(v,4) for v in calc)} "
                            f"不符 (差 >0.01) ⇒ 声明值与参数式不自洽")
    return {"ok": not errs, "errs": errs, "rows": rows,
            "formula": f"OPEN_Y_eff(h) = max({open_y:.2f}, h + 2*({crit:.2f}+{tol:.2f})) "
                       f"= max({open_y:.2f}, h + {2*(crit+tol):.2f})",
            "tiers": tiers}


# ==================================================================================================
# M4 · 判据命令真存在 (★照 state/check_brief_commands.py 的口径★)
# ==================================================================================================
def check_m4(root: str, spec: dict) -> dict:
    errs = []
    rows = []
    items = spec.get("items") or []
    n_cmd = 0
    for it in items:
        crit = it.get("criterion") or ""
        cmds = CMD_RE.findall(crit)
        if not cmds:
            errs.append(f"M4 条目 '{it.get('id')}' 的 criterion 里没有命令 ⇒ 不成判据")
            continue
        for p in cmds:
            n_cmd += 1
            full = os.path.join(root, p)
            exists = os.path.exists(full)
            rows.append({"id": it.get("id"), "cmd_path": p, "exists": exists})
            if not exists:
                errs.append(f"M4 条目 '{it.get('id')}' 的判据命令 '{p}' 在本机不存在 "
                            f"⇒ 不许把不存在的命令写进清单")
    if n_cmd == 0:
        errs.append("M4 一条判据命令都没抠到 ⇒ 闸没东西可查")
    return {"ok": not errs, "errs": errs, "rows": rows, "n_commands": n_cmd}


# ==================================================================================================
# M5 · 受保护 5 件 md5 逐字节不变
# --------------------------------------------------------------------------------------------------
# ★★【ISS-278 续做 · 实测发现的真缺口】★★
#   本闸原先: `for rel, base in CFC.PROTECTED.items()` ⇒ ★**只查 2 件** (板 / .kicad_pro) ★
#   原因: ISS-286 (★2026-11-17 12:44★) 把 `CFC.PROTECTED` 从 5 件改成 2 件 ——
#         网表 / 脚表 / BOM 改由【落表台账】管 (★病根 = 判决源选错了 ⇒ 修法落在取值来源上★)。
#   ⇒ ★**本闸的覆盖面被悄悄从 5 件削成 2 件 = 任务书 §③ 要求的「M5 受保护 5 件」没兑现** ★
#   ⇒ ★★改法 (★不碰任何既有脚本, 只在本闸内实现★): ★
#       M5a 硬基线 2 件 (板 / .kicad_pro)  ⇒ 基线写死, 一条不许动
#       M5b 台账管理 3 件 (网表/脚表/BOM) ⇒ 判决源 = 落表台账链头 (★与 ISS-286 的 C4 同构口径★)
#   ⇒ 净效果: 合法落表 ⇒ 绿 · 偷改真源不更新台账 ⇒ 红 · 台账读不到 / 链断 / 链头取不准 ⇒ 判红
# ==================================================================================================
def check_m5(root: str) -> dict:
    errs = []
    rows = []

    # ---- M5a · 硬基线 2 件 (板 / .kicad_pro) ⇒ 基线写死, 一条不许动 ----
    for rel, base in CFC.PROTECTED.items():
        p = os.path.join(root, rel)
        if not os.path.exists(p):
            errs.append(f"M5a 受保护件缺失: {rel}")
            continue
        got = CFC.md5_of(p)
        rows.append({"path": rel, "baseline": base, "got": got, "same": got == base,
                     "mode": "硬基线 (真·不许变)"})
        if got != base:
            errs.append(f"M5a 受保护件被改: {rel} 基线 {base} ⇒ 现值 {got}")

    # ---- M5b · 台账管理 3 件 (网表 / 脚表 / BOM) ⇒ 判决源 = 落表台账链头 (★fail-closed★) ----
    led_rel = getattr(CFC, "LEDGER_CANON", "HW/SCHEMATIC_LANDING_V1_LANDED.md")
    led_path = os.path.join(root, led_rel)
    led_text = ""
    if os.path.isfile(led_path):
        with open(led_path, encoding="utf-8") as fh:
            led_text = fh.read()
    else:
        errs.append(f"M5b 落表台账读不到: {led_rel} (★判决源缺失 ⇒ fail-closed 判红★)")
    for rel in getattr(CFC, "PROTECTED_LEDGER", ()):
        p = os.path.join(root, rel)
        if not os.path.exists(p):
            errs.append(f"M5b 受保护件缺失: {rel}")
            continue
        got = CFC.md5_of(p)
        if led_text:
            st = CFC.ledger_state(rel, led_text)
        else:
            st = {"records": [], "head": None, "chain": [], "why": "落表台账读不到",
                  "head_iss": [], "known": set(), "producer": {}}
        recs = st.get("records") or []
        head = st.get("head")
        why = st.get("why")
        iss = st.get("head_iss") or []
        chain = st.get("chain") or []
        rows.append({"path": rel, "baseline": f"落表台账链头 ({led_rel})", "got": got,
                     "same": bool(head) and got[:12] == head, "mode": "落表台账链头",
                     "head": head, "iss": iss, "chain_len": len(chain),
                     "records": len(recs)})
        # ---- fail-closed 六条 (★一条不许放宽★) ----
        if not led_text:
            errs.append(f"M5b 台账管理件判决失败: {rel} 落表台账读不到 ({led_rel}) ⇒ fail-closed 判红")
            continue
        if not recs:
            errs.append(f"M5b 台账管理件判决失败: {rel} 落表台账里查不到任何登记 "
                        f"(★台账查不到 ⇒ 判红★)")
            continue
        if not head:
            errs.append(f"M5b 台账管理件判决失败: {rel} 台账链头取不准 ({why}) ⇒ 取不准不许判绿")
            continue
        if not iss:
            errs.append(f"M5b 台账管理件判决失败: {rel} 台账链头 ({head}) 无落表单号 "
                        f"(★单号/文件名/前后 md5 四项不齐 ⇒ 判红★)")
            continue
        if not chain:
            errs.append(f"M5b 台账管理件判决失败: {rel} 落表链断了 / 不唯一 ({why}) ⇒ 判红")
            continue
        orphan = sorted({r["new"] for r in recs} - set(chain))
        if orphan:
            errs.append(f"M5b 台账管理件判决失败: {rel} 台账里有记录不在链上 = {orphan} "
                        f"(★前后 md5 不齐 ⇒ 链断了 ⇒ 判红★)")
            continue
        if got[:12] != head:
            errs.append(f"M5b 台账管理件判决失败: {rel} 盘上 md5 {got[:12]}… ≠ 台账链头 {head}… "
                        f"(★真源被换了? 或台账没更新★)")
    return {"ok": not errs, "errs": errs, "rows": rows}


# ==================================================================================================
# 汇总
# ==================================================================================================
def run_checks(root: str) -> dict:
    spec = read_spec(root)
    board = CFC.read_board(root)
    return {
        "M1": check_m1(root, spec),
        "M2": check_m2(root, spec, board),
        "M3": check_m3(root, spec, board),
        "M4": check_m4(root, spec),
        "M5": check_m5(root),
    }


def _hr(t):
    print("\n" + "=" * 96)
    print(t)
    print("=" * 96)


def print_checks(res):
    _hr("【ISS-278 · 「板只改一次」那一趟 · MECH 侧板侧输入闸】")
    print(f"  规格页: {SPEC_REL}")
    print(f"  帧白名单: {res['M1']['frames_allowed']}")
    print(f"  M1 帧标签 ........ {'✅ 绿' if res['M1']['ok'] else '❌ 红'}"
          f"  (坐标组 {res['M1']['n_rects']} 个 / 条目 {res['M1']['n_items']} 条)")
    print(f"  M2 三条开口不压 SoM  {'✅ 绿' if res['M2']['ok'] else '❌ 红'}  "
          f"(期望 id 集合 {res['M2'].get('expected_ids')})")
    for r in res["M2"]["rows"]:
        print(f"      · {r['id']:18s} {r['role']:6s} 罩 {r['covers']:22s} "
              f"rect={tuple(round(v,3) for v in r['rect'])} ⇒ 压 SoM 焊盘 {r['som_hits']}")
    print(f"  M3 座体高度参数式 . {'✅ 绿' if res['M3']['ok'] else '❌ 红'}"
          f"  (公式 {res['M3'].get('formula')})")
    for r in res["M3"]["rows"]:
        print(f"      · {r['id']:18s} h={r['h']:<5.2f} eff={r['eff']:<5.2f} "
              f"rect={r['rect']} 落框={r['in_frame']} 压SoM={r['som_hits']} "
              f"最坏间隙Y={r['worst_cl_y']:.3f}")
    print(f"  M4 判据命令真存在 .. {'✅ 绿' if res['M4']['ok'] else '❌ 红'}"
          f"  (命令 {res['M4']['n_commands']} 条)")
    for r in res["M4"]["rows"]:
        print(f"      · {r['id']:22s} {r['cmd_path']:52s} {'存在' if r['exists'] else '★不存在★'}")
    print(f"  M5 受保护 5 件 md5 . {'✅ 绿' if res['M5']['ok'] else '❌ 红'}"
          f"  (M5a 硬基线 {len(CFC.PROTECTED)} 件 + M5b 台账链头 {len(getattr(CFC, 'PROTECTED_LEDGER', ()))} 件)")
    for r in res["M5"]["rows"]:
        if r.get("mode", "").startswith("落表台账"):
            print(f"      · {r['path']:42s} {r['got'][:12]}… {'==' if r['same'] else '!='} "
                  f"台账链头 {r.get('head')}…  落表单号 {r.get('iss')}  链长 {r.get('chain_len')}"
                  f"  记录 {r.get('records')}")
        else:
            print(f"      · {r['path']:42s} {r['got']} {'==' if r['same'] else '!='} {r['baseline']}")
    errs = []
    for k in ("M1", "M2", "M3", "M4", "M5"):
        errs += res[k]["errs"]
    if errs:
        _hr(f"【红】{len(errs)} 条")
        for e in errs:
            print(f"  ✗ {e}")
    else:
        _hr("【绿】M1~M5 全过")


# ==================================================================================================
# 沙盒 (★反向用例一律在副本上跑, 真件一个字节不碰★)
# ==================================================================================================
def sandbox_base(root: str) -> str:
    env = os.environ.get("MECH_SANDBOX_DIR")
    if env:
        return env
    return os.path.abspath(os.path.join(root, "..", "..", "tmp", "iss278_sync_selftest"))


def make_sandbox(root: str, tag: str) -> str:
    base = sandbox_base(root)
    dst = os.path.join(base, tag)
    if os.path.exists(dst):
        shutil.rmtree(dst)
    os.makedirs(dst, exist_ok=True)
    rels = [SPEC_REL] + list(CFC.PROTECTED.keys())
    # ★ISS-278 续做: M5b 查台账管理 3 件 ⇒ 沙盒必须连【落表台账】一起复制, 否则 M5b 永远 fail-closed
    #   (★沙盒只读副本, 真件一个字节不碰★)
    rels += list(getattr(CFC, "PROTECTED_LEDGER", ()))
    led_rel = getattr(CFC, "LEDGER_CANON", "HW/SCHEMATIC_LANDING_V1_LANDED.md")
    if led_rel not in rels:
        rels.append(led_rel)
    for rel in rels:
        src = os.path.join(root, rel)
        if os.path.exists(src):
            d = os.path.join(dst, rel)
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copy2(src, d)
    return dst


def _edit_spec_json(sb: str, fn):
    """在沙盒里改机器块 JSON (★只改副本★)"""
    p = os.path.join(sb, SPEC_REL)
    text = open(p, encoding="utf-8").read()
    b = text.find(MACH_BEGIN)
    e = text.find(MACH_END)
    seg = text[b:e]
    m = re.search(r"```json\n(.*?)\n```", seg, re.S)
    data = json.loads(m.group(1))
    fn(data)
    new = "```json\n" + json.dumps(data, ensure_ascii=False, indent=2) + "\n```"
    text2 = text[:b] + text[b:e].replace(m.group(0), new) + text[e:]
    open(p, "w", encoding="utf-8").write(text2)


def _edit_spec_text(sb: str, old: str, new: str) -> bool:
    p = os.path.join(sb, SPEC_REL)
    text = open(p, encoding="utf-8").read()
    if old not in text:
        return False
    open(p, "w", encoding="utf-8").write(text.replace(old, new, 1))
    return True


# ==================================================================================================
# 自检 (★≥5 条反向用例, 每条自证真改到目标★)
# ==================================================================================================
def selftest(root: str) -> int:
    errs = []
    _hr("【自检】check_onepass_mech_sync.py 反向用例 (★沙盒副本上跑, 真件一个字节不碰★)")
    base = run_checks(root)
    print(f"  [基线] M1={'OK' if base['M1']['ok'] else 'NG'} "
          f"M2={'OK' if base['M2']['ok'] else 'NG'} "
          f"M3={'OK' if base['M3']['ok'] else 'NG'} "
          f"M4={'OK' if base['M4']['ok'] else 'NG'} "
          f"M5={'OK' if base['M5']['ok'] else 'NG'}")
    if not all(base[k]["ok"] for k in ("M1", "M2", "M3", "M4", "M5")):
        errs.append("基线就不绿 ⇒ 自检无意义")

    # ---- ① 改检修口矩形一个角 ⇒ M2 红 ----
    sb = make_sandbox(root, "case1_move_uart_corner")
    p = os.path.join(sb, SPEC_REL)
    before = CFC.md5_of(p)

    def _c1(d):
        for o in d["openings"]:
            if o["id"] == "PORT_OPEN_UART":
                o["rect"]["y0"] = 52.000      # ★把左下角的 Y 挪进 SoM P3/P4 的 Y 带★
    _edit_spec_json(sb, _c1)
    after = CFC.md5_of(p)
    r1 = run_checks(sb)
    red = not r1["M2"]["ok"]
    print(f"  [{'OK ' if red else 'NG '}] ① 改检修口矩形一个角 (y0 66.300 ⇒ 52.000) ⇒ M2 红: "
          f"{'是' if red else '否'} · md5 {before[:8]} ⇒ {after[:8]} (确实改了: {before != after}) · "
          f"M2 命中={[(x['id'], x['som_hits']) for x in r1['M2']['rows']]}")
    if not red:
        errs.append("① 改检修口矩形角点后 M2 没红")
    if before == after:
        errs.append("① 没能真改到目标文件")

    # ---- ② 把两条开口合并 ⇒ M2/M3 红 ----
    sb = make_sandbox(root, "case2_merge_openings")
    p = os.path.join(sb, SPEC_REL)
    before = CFC.md5_of(p)

    def _c2(d):
        merged = {"id": "PORT_OPEN_MERGED", "role": "合并", "covers": "J_DEBUG+J_UART",
                  "frame": "B160x100", "body_w": 126.2175,
                  "rect": {"x0": 17.620, "x1": 143.838, "y0": 55.330, "y1": 69.870},
                  "som_hits": 0}
        d["openings"] = [merged]
    _edit_spec_json(sb, _c2)
    after = CFC.md5_of(p)
    r2 = run_checks(sb)
    red2 = (not r2["M2"]["ok"]) and (not r2["M3"]["ok"])
    print(f"  [{'OK ' if red2 else 'NG '}] ② 把两条开口合并成一个 ⇒ M2/M3 红: "
          f"{'是' if red2 else '否'} · md5 {before[:8]} ⇒ {after[:8]} (确实改了: {before != after}) · "
          f"M2 错误 {len(r2['M2']['errs'])} 条 / M3 错误 {len(r2['M3']['errs'])} 条")
    if not red2:
        errs.append("② 合并两条开口后 M2/M3 没红")
    if before == after:
        errs.append("② 没能真改到目标文件")

    # ---- ③ 抽帧标签 (正文表头) ⇒ M1 红 ----
    sb = make_sandbox(root, "case3_strip_frame_tag")
    p = os.path.join(sb, SPEC_REL)
    before = CFC.md5_of(p)
    hit = _edit_spec_text(sb, "| current_state (帧: 160×100 台架板) |",
                           "| current_state (档位已抽) |")
    after = CFC.md5_of(p)
    r3 = run_checks(sb)
    red3 = not r3["M1"]["ok"]
    print(f"  [{'OK ' if red3 else 'NG '}] ③ 抽掉正文表头的帧标签 ⇒ M1 红: "
          f"{'是' if red3 else '否'} · 命中模式: {hit} · md5 {before[:8]} ⇒ {after[:8]} "
          f"(确实改了: {before != after}) · M1 错误 {len(r3['M1']['errs'])} 条")
    if not red3:
        errs.append("③ 抽帧标签后 M1 没红")
    if not hit or before == after:
        errs.append("③ 没能真改到目标文件")

    # ---- ④ 抽帧标签 (机器块 JSON) ⇒ M1 红 ----
    sb = make_sandbox(root, "case4_strip_json_frame")
    p = os.path.join(sb, SPEC_REL)
    before = CFC.md5_of(p)

    def _c4(d):
        for o in d["openings"]:
            if o["id"] == "PORT_OPEN_DEBUG":
                o.pop("frame", None)
    _edit_spec_json(sb, _c4)
    after = CFC.md5_of(p)
    r4 = run_checks(sb)
    red4 = not r4["M1"]["ok"]
    print(f"  [{'OK ' if red4 else 'NG '}] ④ 抽掉机器块里的 frame 字段 ⇒ M1 红: "
          f"{'是' if red4 else '否'} · md5 {before[:8]} ⇒ {after[:8]} (确实改了: {before != after}) · "
          f"M1 错误 {len(r4['M1']['errs'])} 条")
    if not red4:
        errs.append("④ 抽机器块帧标签后 M1 没红")
    if before == after:
        errs.append("④ 没能真改到目标文件")

    # ---- ⑤ 把 h 三档之一改到不合理 ⇒ M3 红 ----
    sb = make_sandbox(root, "case5_bad_h_tier")
    p = os.path.join(sb, SPEC_REL)
    before = CFC.md5_of(p)

    def _c5(d):
        d["consts"]["h_tiers"] = [0.90, 2.54, 40.00]      # ★40.00 > 板给的座体盒高 4.00★

    _edit_spec_json(sb, _c5)
    after = CFC.md5_of(p)
    r5 = run_checks(sb)
    red5 = not r5["M3"]["ok"]
    print(f"  [{'OK ' if red5 else 'NG '}] ⑤ 把 h 三档之一改到不合理 (4.00 ⇒ 40.00) ⇒ M3 红: "
          f"{'是' if red5 else '否'} · md5 {before[:8]} ⇒ {after[:8]} (确实改了: {before != after}) · "
          f"M3 错误 {len(r5['M3']['errs'])} 条")
    if not red5:
        errs.append("⑤ h 三档改坏后 M3 没红")
    if before == after:
        errs.append("⑤ 没能真改到目标文件")

    # ---- ⑥ 判据命令改成不存在的 ⇒ M4 红 ----
    sb = make_sandbox(root, "case6_fake_command")
    p = os.path.join(sb, SPEC_REL)
    before = CFC.md5_of(p)

    def _c6(d):
        d["items"][0]["criterion"] = "python3 MECH/does_not_exist_iss278.py => rc=0"

    _edit_spec_json(sb, _c6)
    after = CFC.md5_of(p)
    r6 = run_checks(sb)
    red6 = not r6["M4"]["ok"]
    print(f"  [{'OK ' if red6 else 'NG '}] ⑥ 把判据命令改成不存在的脚本 ⇒ M4 红: "
          f"{'是' if red6 else '否'} · md5 {before[:8]} ⇒ {after[:8]} (确实改了: {before != after}) · "
          f"M4 错误 {len(r6['M4']['errs'])} 条")
    if not red6:
        errs.append("⑥ 判据命令改成假命令后 M4 没红")
    if before == after:
        errs.append("⑥ 没能真改到目标文件")

    # ---- ⑦ 改受保护件 ⇒ M5 红 ----
    # ★★2026-11-17 ISS-294 修: 本条原先篡改 `HW/BOM_v1.csv`, ★但 BOM 不在 `CFC.PROTECTED` 里
    #   (★ISS-286 把 PROTECTED 从 5 件改成「板 + .kicad_pro」两件, 网表/脚表/BOM 归台账管★)
    #   ⇒ 沙盒里根本没有那个文件 ⇒ 自检直接崩 (FileNotFoundError) ⇒ 本条从未真正跑过。
    #   ★★改法: 篡改 M5 真正查的板文件 (★与 MECH/check_onepass_struct_crosscheck.py 第 ⑦ 条同做法★),
    #   语义与目的不变 (★改受保护件 ⇒ M5 必须红★), 且这条反向用例现在真的能跑。
    sb = make_sandbox(root, "case7_touch_protected")
    pcb = os.path.join(sb, "HW", "PCB", "demo_mainboard.kicad_pcb")
    before = CFC.md5_of(pcb)
    with open(pcb, "a", encoding="utf-8") as fh:
        fh.write("\n; ★ISS-294 反向用例: 篡改受保护板文件★\n")
    after = CFC.md5_of(pcb)
    r7 = run_checks(sb)
    red7 = not r7["M5"]["ok"]
    print(f"  [{'OK ' if red7 else 'NG '}] ⑦ 改受保护件 (HW/PCB/demo_mainboard.kicad_pcb) ⇒ M5 红: "
          f"{'是' if red7 else '否'} · md5 {before[:8]} ⇒ {after[:8]} (确实改了: {before != after}) · "
          f"M5 错误 {len(r7['M5']['errs'])} 条")
    if not red7:
        errs.append("⑦ 改受保护件后 M5 没红")
    if before == after:
        errs.append("⑦ 没能真改到目标文件")

    # ---- ⑦b 改【台账管理件】(网表/脚表/BOM 之一) 而台账不更新 ⇒ M5b 红 (★ISS-278 续做新增★) ----
    # ★★为什么必须有这条: M5b 现在才真查这 3 件 (原先 M5 只查 2 件 ⇒ 这 3 件【没人管】) ★★
    #   ⇒ 必须有一条反向用例自证「偷改真源不更新台账 ⇒ 判红」这个行为真的存在, 不许是【摆设】 ★★
    sb = make_sandbox(root, "case7b_touch_ledger_managed")
    ledger_rel = getattr(CFC, "PROTECTED_LEDGER", ())
    if not ledger_rel:
        errs.append("⑦b 本机读不到 CFC.PROTECTED_LEDGER (台账管理件清单) ⇒ 没法自证 M5b")
        print("  [NG ] ⑦b 读不到台账管理件清单 ⇒ M5b 自证不了")
    else:
        rel_b = ledger_rel[0]
        p_b = os.path.join(sb, rel_b)
        before_b = CFC.md5_of(p_b)
        with open(p_b, "a", encoding="utf-8") as fh:
            fh.write("\n★ISS-278 反向用例: 偷改台账管理件 (台账不更新)★\n")
        after_b = CFC.md5_of(p_b)
        r7b = run_checks(sb)
        red7b = not r7b["M5"]["ok"]
        hit7b = any("M5b" in e for e in r7b["M5"]["errs"])
        print(f"  [{'OK ' if red7b else 'NG '}] ⑦b 偷改台账管理件 ({rel_b}) 而台账不更新 ⇒ M5b 红: "
              f"{'是' if red7b else '否'} · 命中 M5b 断言: {'是' if hit7b else '否'} · "
              f"md5 {before_b[:8]} ⇒ {after_b[:8]} (确实改了: {before_b != after_b}) · "
              f"M5 错误 {len(r7b['M5']['errs'])} 条")
        if not red7b:
            errs.append("⑦b 偷改台账管理件后 M5 没红")
        if not hit7b:
            errs.append("⑦b M5b 断言没触发")
        if before_b == after_b:
            errs.append("⑦b 没能真改到目标文件")

    # ---- ⑨ 删掉第三条开口 (USB-C 边开口) ⇒ M2 红 (★期望 id 集合不许少★) ----
    sb = make_sandbox(root, "case9_drop_usbc")
    p = os.path.join(sb, SPEC_REL)
    before = CFC.md5_of(p)

    def _c9(d):
        d["openings"] = [o for o in d["openings"] if o.get("id") != "PORT_OPEN_USBC"]
    _edit_spec_json(sb, _c9)
    after = CFC.md5_of(p)
    r9 = run_checks(sb)
    red9 = not r9["M2"]["ok"]
    hit9 = any("M2 开口 id 集合" in e for e in r9["M2"]["errs"])
    print(f"  [{'OK ' if red9 else 'NG '}] ⑨ 把机器块里的 PORT_OPEN_USBC 删掉 ⇒ M2 红: "
          f"{'是' if red9 else '否'} · 命中集合断言: {'是' if hit9 else '否'} · "
          f"md5 {before[:8]} ⇒ {after[:8]} (确实改了: {before != after}) · "
          f"M2 错误 {len(r9['M2']['errs'])} 条")
    if not red9:
        errs.append("⑨ 删掉第三条开口后 M2 没红")
    if not hit9:
        errs.append("⑨ 期望 id 集合断言没触发")
    if before == after:
        errs.append("⑨ 没能真改到目标文件")

    # ---- ⑩ 把第三条开口的 id 改掉 ⇒ M2 红 (★集合不匹配★) ----
    sb = make_sandbox(root, "case10_rename_usbc")
    p = os.path.join(sb, SPEC_REL)
    before = CFC.md5_of(p)

    def _c10(d):
        for o in d["openings"]:
            if o.get("id") == "PORT_OPEN_USBC":
                o["id"] = "PORT_OPEN_USB_C"
    _edit_spec_json(sb, _c10)
    after = CFC.md5_of(p)
    r10 = run_checks(sb)
    red10 = not r10["M2"]["ok"]
    hit10 = any("M2 开口 id 集合" in e for e in r10["M2"]["errs"])
    print(f"  [{'OK ' if red10 else 'NG '}] ⑩ 把 PORT_OPEN_USBC 改名成 PORT_OPEN_USB_C ⇒ M2 红: "
          f"{'是' if red10 else '否'} · 命中集合断言: {'是' if hit10 else '否'} · "
          f"md5 {before[:8]} ⇒ {after[:8]} (确实改了: {before != after}) · "
          f"M2 错误 {len(r10['M2']['errs'])} 条")
    if not red10:
        errs.append("⑩ 改掉第三条开口的 id 后 M2 没红")
    if not hit10:
        errs.append("⑩ 期望 id 集合断言没触发")
    if before == after:
        errs.append("⑩ 没能真改到目标文件")

    # ---- ⑪ 把第三条开口的矩形改成跟调试口完全一样 ⇒ M2b 红 (★合并禁令不许松★) ----
    sb = make_sandbox(root, "case11_usbc_same_rect_as_debug")
    p = os.path.join(sb, SPEC_REL)
    before = CFC.md5_of(p)

    def _c11(d):
        for o in d["openings"]:
            if o.get("id") == "PORT_OPEN_USBC":
                o["rect"] = {"x0": 137.850, "x1": 148.050, "y0": 54.300, "y1": 58.900}
    _edit_spec_json(sb, _c11)
    after = CFC.md5_of(p)
    r11 = run_checks(sb)
    red11 = not r11["M2"]["ok"]
    hit11 = any("M2b" in e for e in r11["M2"]["errs"])
    print(f"  [{'OK ' if red11 else 'NG '}] ⑪ 把边开口的矩形改成跟调试口完全一样 ⇒ M2b 红 "
          f"(合并禁令): {'是' if red11 else '否'} · 命中合并禁令: {'是' if hit11 else '否'} · "
          f"md5 {before[:8]} ⇒ {after[:8]} (确实改了: {before != after}) · "
          f"M2 错误 {len(r11['M2']['errs'])} 条")
    if not red11:
        errs.append("⑪ 把边开口并进调试口后 M2 没红")
    if not hit11:
        errs.append("⑪ 合并禁令 (M2b 任意两条矩形不许完全相同) 没触发")
    if before == after:
        errs.append("⑪ 没能真改到目标文件")

    # ---- ⑫ 正向对照: 三条齐全且互不相同 ⇒ 绿 ----
    sb = make_sandbox(root, "case12_positive_three_openings")
    r12 = run_checks(sb)
    ids12 = sorted(o.get("id") for o in (read_spec(sb).get("openings") or []))
    green12 = r12["M2"]["ok"] and r12["M3"]["ok"] and ids12 == sorted(EXPECTED_OPENING_IDS)
    print(f"  [{'OK ' if green12 else 'NG '}] ⑫ 正向对照 (三条齐全且互不相同) ⇒ 绿: "
          f"{'是' if green12 else '否'} · 开口集合 {ids12}")
    if not green12:
        errs.append("⑫ 正向对照 (三条齐全) 不绿")

    # ---- ⑧ 真件跑完自检后仍逐字节不变 (★5 件一件都不少★) ----
    # ★ISS-278 续做修: 原先只遍历 `CFC.PROTECTED` ⇒ 只查 2 件却宣称「5 件」 ⇒
    #   现在把台账管理 3 件也纳入 (★按台账链头判, 与 M5b 同口径★) ⇒ 宣称的与实查的件数一致。
    rows = []
    same = True
    for rel, base_md5 in CFC.PROTECTED.items():
        got = CFC.md5_of(os.path.join(root, rel))
        rows.append((rel, got, got == base_md5))
        same = same and (got == base_md5)
    led_path = os.path.join(root, getattr(CFC, "LEDGER_CANON",
                                           "HW/SCHEMATIC_LANDING_V1_LANDED.md"))
    led_text = open(led_path, encoding="utf-8").read() if os.path.isfile(led_path) else ""
    for rel in getattr(CFC, "PROTECTED_LEDGER", ()):
        got = CFC.md5_of(os.path.join(root, rel))
        st = CFC.ledger_state(rel, led_text) if led_text else {"head": None}
        head = st.get("head")
        ok8 = bool(head) and got[:12] == head
        rows.append((rel, got, ok8))
        same = same and ok8
    print(f"  [{'OK ' if same else 'NG '}] ⑧ 自检跑完, 真件 5 件 md5 仍逐字节不变: "
          f"{'是' if same else '否'} · " + " · ".join(f"{os.path.basename(r)}={g[:8]}" for r, g, _ in rows))
    if not same:
        errs.append("⑧ 自检跑完真件被改了 ⇒ 沙盒机制失效")
    if len(rows) != 5:
        errs.append(f"⑧ 自证只查了 {len(rows)} 件 (★宣称 5 件, 覆盖面必须一件不少★)")

    _hr(f"【自检结论】{'✅ 全抓到' if not errs else '❌ 有漏 —— ' + '; '.join(errs)}")
    return 0 if not errs else 2


# ==================================================================================================
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--root", default=PROJ)
    args = ap.parse_args()
    root = os.path.abspath(args.root)
    if args.selftest:
        return selftest(root)
    res = run_checks(root)
    ok = all(res[k]["ok"] for k in ("M1", "M2", "M3", "M4", "M5"))
    if args.json:
        out = {k: {kk: vv for kk, vv in v.items() if kk != "rows"} for k, v in res.items()}
        out["_ok"] = ok
        print(json.dumps(out, ensure_ascii=False, indent=1, default=str))
    else:
        print_checks(res)
        print("\n口径提醒: 本闸一切「实测」= 文件实读 + 脚本实跑; **实物 [实测] = 0 条**;"
              " 座体真实高度 = [0数据] ⇒ 开口 Y 一切数按公式取值。")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
