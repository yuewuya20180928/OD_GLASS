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
    rows = []
    if len(openings) != 2:
        errs.append(f"M2 开口必须【两条】(检修口 / 调试口), 机器块里只有 {len(openings)} 条 "
                    f"⇒ 不许合并")
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

    # --- M2b 两条必须真的不同 (不许合并成一个矩形) ---
    if len(rows) == 2:
        a, b = rows[0]["rect"], rows[1]["rect"]
        if all(abs(x - y) < 1e-9 for x, y in zip(a, b)):
            errs.append("M2b 两条开口的矩形完全相同 ⇒ 等于合并 ⇒ 红")

    # --- M2c 合并禁令必须登记, 且缺口 = 板读实算值 ---
    mo = spec.get("merged_opening") or {}
    if not mo:
        errs.append("M2c 机器块缺 merged_opening (合并禁令的登记)")
    else:
        if not mo.get("forbidden"):
            errs.append("M2c merged_opening.forbidden 不为 true ⇒ 合并禁令没登记")
        gap = mo.get("gap_mm")
        # ★实算: 两座体必须清空区并集宽 vs 开口宽 ⇒ 缺口 (★用板读的连接器位置 + 声明的座体宽★) ★
        conns = {}
        for o in openings:
            ref = o.get("covers")
            f = fps.get(ref)
            if not f:
                continue
            ps = f["pads"]
            cx = sum(p["x"] for p in ps) / len(ps)
            cy = sum(p["y"] for p in ps) / len(ps)
            w = float(o.get("body_w") or 0.0)
            conns[ref] = (cx - w / 2, cx + w / 2)
        if len(conns) == 2:
            xs = [v for c in conns.values() for v in c]
            content_w = max(xs) - min(xs)
            real_gap = content_w - float(mo.get("open_w") or 0.0)
            if gap is None or abs(float(gap) - real_gap) > 0.01:
                errs.append(f"M2c 合并缺口声明 {gap} 与实算 {real_gap:.6f} 不符 (差 >0.01)")
            if real_gap <= 0:
                errs.append(f"M2c 实算合并缺口 {real_gap:.6f} ≤ 0 ⇒ 合并本可行 ⇒ "
                            f"「必须拆两条」的前提没了")
    return {"ok": not errs, "errs": errs, "rows": rows, "som_pads": len(som_pads)}


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
# ==================================================================================================
def check_m5(root: str) -> dict:
    errs = []
    rows = []
    for rel, base in CFC.PROTECTED.items():
        p = os.path.join(root, rel)
        if not os.path.exists(p):
            errs.append(f"M5 受保护件缺失: {rel}")
            continue
        got = CFC.md5_of(p)
        rows.append({"path": rel, "baseline": base, "got": got, "same": got == base})
        if got != base:
            errs.append(f"M5 受保护件被改: {rel} 基线 {base} ⇒ 现值 {got}")
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
    print(f"  M2 两条开口不压 SoM  {'✅ 绿' if res['M2']['ok'] else '❌ 红'}")
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
    print(f"  M5 受保护 5 件 md5 . {'✅ 绿' if res['M5']['ok'] else '❌ 红'}")
    for r in res["M5"]["rows"]:
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
    sb = make_sandbox(root, "case7_touch_protected")
    bom = os.path.join(sb, "HW", "BOM_v1.csv")
    before = CFC.md5_of(bom)
    with open(bom, "a", encoding="utf-8") as fh:
        fh.write("\n#ISS278-SELFTEST-TOUCH\n")
    after = CFC.md5_of(bom)
    r7 = run_checks(sb)
    red7 = not r7["M5"]["ok"]
    print(f"  [{'OK ' if red7 else 'NG '}] ⑦ 改受保护件 (HW/BOM_v1.csv) ⇒ M5 红: "
          f"{'是' if red7 else '否'} · md5 {before[:8]} ⇒ {after[:8]} (确实改了: {before != after}) · "
          f"M5 错误 {len(r7['M5']['errs'])} 条")
    if not red7:
        errs.append("⑦ 改受保护件后 M5 没红")
    if before == after:
        errs.append("⑦ 没能真改到目标文件")

    # ---- ⑧ 真件跑完自检后仍逐字节不变 ----
    rows = []
    same = True
    for rel, base_md5 in CFC.PROTECTED.items():
        got = CFC.md5_of(os.path.join(root, rel))
        rows.append((rel, got, got == base_md5))
        same = same and (got == base_md5)
    print(f"  [{'OK ' if same else 'NG '}] ⑧ 自检跑完, 真件 5 件 md5 仍逐字节不变: "
          f"{'是' if same else '否'} · " + " · ".join(f"{os.path.basename(r)}={g[:8]}" for r, g, _ in rows))
    if not same:
        errs.append("⑧ 自检跑完真件被改了 ⇒ 沙盒机制失效")

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
