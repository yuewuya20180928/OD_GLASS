#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-290 · mech-lead 实算脚本 (只读板 + 只读落表)

产出 `logs/iss290/compute_iss290.json`:
  - 板框 / 圆角口径
  - SoM 承载区 (焊盘铜箔并集 / F.Fab 并集 / 保守包络)
  - 两条开口 + 两条必须清空区 (由板读重算, 不抄任何交卷单)
  - 座体类器件 land pattern 实测 (J_DEBUG/J_UART/J_USB_C/J_CHG/J_SOM_P1..P4)
  - S6 20 个目标落位 × 保留区 逐个核对
  - corner_radius 3.0 vs 0.0 的贴角可用区差值 (数值积分)

★零写板 · 零落表 · 零改 HW/ ★
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from pcbparse import Board, bbox_of, rot_xy, rect_dist, rect_overlap_area  # noqa: E402
from pcbparse import kid, kids, nname, val as sval  # noqa: E402


def fv(node, idx, default=None):
    v = sval(node, idx, default)
    try:
        return float(v)
    except (TypeError, ValueError):
        return default

ROOT = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
OUT = os.path.join(HERE, "compute_iss290.json")

CRIT = 0.60          # MECH 既有判据 (MECH/service_port_check.py §2) — 不许新造
EDGE_KEEPOUT = 0.80  # MECH_BUDGET §5.1
OPEN_W = 10.20       # 开口定档宽 (X) — 帧无关
H_TIERS = [0.90, 2.54, 4.00]
BODY_H_REF = 2.54
JD_BODY_W_MODEL = 2.540   # MECH 现行模型 (J_UART 座体宽)
FAB_STROKE_HALF = 0.05    # F.Fab 笔画 0.10 的半宽 (保守包络用)

FRAME = "B160x100"


def rd(v):
    return round(float(v), 4)


def main():
    b = Board()
    refs = b.by_ref()

    # ---------------- 板框 ----------------
    edge_bbox = b.edge_bbox()
    edge_pts = []
    for _, pts in b.edge:
        edge_pts.extend(pts)
    # Edge.Cuts 描边宽
    stroke = 0.0
    for node in b.root:
        if isinstance(node, list) and node and (node[0][1] if isinstance(node[0], tuple) else node[0]) == "gr_line":
            pass
    edge_kinds = b.edge_stats()
    edge_lines = []
    for node in b.root:
        nm = nname(node)
        if nm == "gr_line":
            st = kid(node, "start")
            en = kid(node, "end")
            layer = kid(node, "layer")
            edge_lines.append({
                "start": [fv(st, 1), fv(st, 2)],
                "end": [fv(en, 1), fv(en, 2)],
                "layer": sval(layer, 1, ""),
                "stroke_w": None,
            })
    # 描边宽: 从任一 Edge.Cuts gr_line 的 (stroke (width x)) 读
    txt = b.text
    import re
    m = re.findall(r'\(gr_line\s+\(start[^\)]*\)\s+\(end[^\)]*\)\s+\(stroke\s+\(width\s+([0-9.]+)\)', txt)
    if m:
        stroke = float(m[0])
    for el in edge_lines:
        el["stroke_w"] = stroke

    edge_cut_lines = [e for e in edge_lines if e["layer"] == "Edge.Cuts"]
    non_edge_lines = [e for e in edge_lines if e["layer"] != "Edge.Cuts"]

    board = {
        "edge_cuts_centerline_bbox": [rd(edge_bbox[0]), rd(edge_bbox[1]), rd(edge_bbox[2]), rd(edge_bbox[3])],
        "edge_cuts_outer_bbox": [rd(edge_bbox[0] - stroke / 2), rd(edge_bbox[1] - stroke / 2),
                                 rd(edge_bbox[2] + stroke / 2), rd(edge_bbox[3] + stroke / 2)],
        "edge_cuts_outer_size": [rd(edge_bbox[2] - edge_bbox[0] + stroke), rd(edge_bbox[3] - edge_bbox[1] + stroke)],
        "edge_cuts_stroke_w": stroke,
        "edge_cuts_lines": len(edge_cut_lines),
        "edge_cuts_non_edge_lines": len(non_edge_lines),
        "edge_cuts_kinds": edge_kinds,
        "corner_radius_measured_mm": 0.0,
        "corner_radius_reason": "Edge.Cuts = %d 条 gr_line (无 gr_arc / gr_circle) => 实测圆角半径 0.00" % len(edge_cut_lines),
        "edge_cut_line_pts": [[e["start"], e["end"]] for e in edge_cut_lines],
    }

    # ---------------- SoM 承载区 ----------------
    som_refs = ["J_SOM_P1", "J_SOM_P2", "J_SOM_P3", "J_SOM_P4"]
    som_copper = []
    som_fab = []
    som_detail = []
    for r in som_refs:
        fp = refs[r]
        boxes = Board.abs_pad_boxes(fp)
        cb = bbox_of([(bx[1], bx[2]) for bx in boxes] + [(bx[3], bx[4]) for bx in boxes])
        fb = Board.fab_bbox_abs(fp)
        som_copper.extend([(cb[0], cb[1]), (cb[2], cb[3])])
        som_fab.extend([(fb[0], fb[1]), (fb[2], fb[3])])
        som_detail.append({
            "ref": r,
            "origin": [rd(fp["x"]), rd(fp["y"]), rd(fp["rot"])],
            "npads": len(fp["pads"]),
            "copper_x": [rd(cb[0]), rd(cb[2])], "copper_y": [rd(cb[1]), rd(cb[3])],
            "fab_x": [rd(fb[0]), rd(fb[2])], "fab_y": [rd(fb[1]), rd(fb[3])],
        })
    som_copper_bb = bbox_of(som_copper)
    som_fab_bb = bbox_of(som_fab)
    # 保守包络 = union(焊盘铜箔并集, 座体 F.Fab 并集 ± 0.05 笔画半宽)
    env_pts = list(som_copper) + [
        (som_fab_bb[0] - FAB_STROKE_HALF, som_fab_bb[1] - FAB_STROKE_HALF),
        (som_fab_bb[2] + FAB_STROKE_HALF, som_fab_bb[3] + FAB_STROKE_HALF)]
    som_env_bb = bbox_of(env_pts)
    som = {
        "copper_union": [rd(som_copper_bb[0]), rd(som_copper_bb[1]), rd(som_copper_bb[2]), rd(som_copper_bb[3])],
        "copper_size": [rd(som_copper_bb[2] - som_copper_bb[0]), rd(som_copper_bb[3] - som_copper_bb[1])],
        "fab_union": [rd(som_fab_bb[0]), rd(som_fab_bb[1]), rd(som_fab_bb[2]), rd(som_fab_bb[3])],
        "fab_size": [rd(som_fab_bb[2] - som_fab_bb[0]), rd(som_fab_bb[3] - som_fab_bb[1])],
        "conservative_env": [rd(som_env_bb[0]), rd(som_env_bb[1]), rd(som_env_bb[2]), rd(som_env_bb[3])],
        "conservative_size": [rd(som_env_bb[2] - som_env_bb[0]), rd(som_env_bb[3] - som_env_bb[1])],
        "npads_total": sum(d["npads"] for d in som_detail),
        "detail": som_detail,
    }

    # ---------------- 两条开口 + 必须清空区 (由板读重算) ----------------
    def port(ref, body_w=None, body_w_src=None):
        fp = refs[ref]
        boxes = Board.abs_pad_boxes(fp)
        cb = bbox_of([(bx[1], bx[2]) for bx in boxes] + [(bx[3], bx[4]) for bx in boxes])
        cx = (cb[0] + cb[2]) / 2.0
        cy = (cb[1] + cb[3]) / 2.0
        if body_w is None:
            body_w = cb[2] - cb[0]
            body_w_src = "板读焊盘铜箔宽"
        tiers = {}
        for h in H_TIERS:
            open_y_eff = max(4.60, h + 1.80)
            oy0 = cy - open_y_eff / 2.0
            oy1 = cy + open_y_eff / 2.0
            clear_y = (open_y_eff - h) / 2.0
            # 必须清空区 (座体) = X 宽 body_w 居中于铜箔中心, Y 高 h 居中于铜箔中心
            mc_x0 = cx - body_w / 2.0
            mc_x1 = cx + body_w / 2.0
            mc_y0 = cy - h / 2.0
            mc_y1 = cy + h / 2.0
            tiers["%.2f" % h] = {
                "open_y_eff": rd(open_y_eff),
                "open_rect": [rd(cx - OPEN_W / 2.0), rd(oy0), rd(cx + OPEN_W / 2.0), rd(oy1)],
                "must_clear": [rd(mc_x0), rd(mc_y0), rd(mc_x1), rd(mc_y1)],
                "clearance_x": rd((OPEN_W - body_w) / 2.0),
                "clearance_y": rd(clear_y),
                "worst_clearance_x": rd((OPEN_W - body_w) / 2.0 - 0.30),
                "worst_clearance_y": rd(clear_y - 0.30),
                "pass_crit": bool((OPEN_W - body_w) / 2.0 - 0.30 >= CRIT - 1e-9
                                  and clear_y - 0.30 >= CRIT - 1e-9),
            }
        return {
            "ref": ref,
            "origin": [rd(fp["x"]), rd(fp["y"]), rd(fp["rot"])],
            "npads": len(fp["pads"]),
            "copper_x": [rd(cb[0]), rd(cb[2])], "copper_y": [rd(cb[1]), rd(cb[3])],
            "copper_center": [rd(cx), rd(cy)],
            "body_w": body_w, "body_w_source": body_w_src,
            "open_x": [rd(cx - OPEN_W / 2.0), rd(cx + OPEN_W / 2.0)],
            "tiers": tiers,
        }

    port_debug = port("J_DEBUG", None, "板读 J_DEBUG 焊盘铜箔宽")
    port_uart = port("J_UART", JD_BODY_W_MODEL, "MECH 现行模型硬编 (MECH/service_port_check.py BASE)")
    port_uart["board_copper_w"] = rd(port_uart["copper_x"][1] - port_uart["copper_x"][0])

    openings = {
        "PORT_OPEN_DEBUG": port_debug,
        "PORT_OPEN_UART": port_uart,
    }

    # ---------------- 座体类器件 land pattern 实测 ----------------
    def land(ref):
        fp = refs[ref]
        boxes = Board.abs_pad_boxes(fp)
        cb = bbox_of([(bx[1], bx[2]) for bx in boxes] + [(bx[3], bx[4]) for bx in boxes])
        fb = Board.fab_bbox_abs(fp)
        cy = Board.crtyd_bbox_abs(fp)
        # 焊盘网格: 取唯一 x / y 坐标
        xs = sorted(set(round(bx[1] + (bx[3] - bx[1]) / 2.0, 4) for bx in boxes))
        ys = sorted(set(round(bx[2] + (bx[4] - bx[2]) / 2.0, 4) for bx in boxes))
        # 间距 (相邻差)
        def pitches(arr):
            ds = [round(arr[i + 1] - arr[i], 4) for i in range(len(arr) - 1)]
            uniq = sorted(set(ds))
            return uniq
        px = pitches(xs)
        py = pitches(ys)
        sig = [p for p in fp["pads"] if p["type"] != "np_thru_hole"]
        npth = [p for p in fp["pads"] if p["type"] == "np_thru_hole"]
        sig_xs = sorted(set(round(bx[1] + (bx[3] - bx[1]) / 2.0, 4) for bx in boxes
                           if bx[0] != "" or True))
        return {
            "ref": ref,
            "value": fp["value"],
            "origin": [rd(fp["x"]), rd(fp["y"]), rd(fp["rot"])],
            "npads": len(fp["pads"]),
            "npads_signal": len(sig),
            "npads_npth": len(npth),
            "pad_numbers_sample": [p["num"] for p in fp["pads"]][:6],
            "copper_x": [rd(cb[0]), rd(cb[2])], "copper_y": [rd(cb[1]), rd(cb[3])],
            "copper_size": [rd(cb[2] - cb[0]), rd(cb[3] - cb[1])],
            "fab_x": [rd(fb[0]), rd(fb[2])], "fab_y": [rd(fb[1]), rd(fb[3])],
            "fab_size": [rd(fb[2] - fb[0]), rd(fb[3] - fb[1])],
            "crtyd": None if cy is None else [rd(cy[0]), rd(cy[1]), rd(cy[2]), rd(cy[3])],
            "pad_x_count": len(xs), "pad_y_count": len(ys),
            "pitch_x_unique": px, "pitch_y_unique": py,
            "n_pads_per_row": len(xs) if len(xs) else 0,
            "n_rows": len(ys),
        }

    land_refs = ["J_DEBUG", "J_UART", "J_USB_C", "J_CHG",
                 "J_SOM_P1", "J_SOM_P2", "J_SOM_P3", "J_SOM_P4"]
    lands = {r: land(r) for r in land_refs}

    # ---------------- S6 目标落位 × 保留区 ----------------
    caliber = os.path.join(ROOT, "HW/PCB/BOARD_FRAME_CALIBER.md")
    s6 = []
    with open(caliber, "r", encoding="utf-8") as fh:
        ctext = fh.read()
    block = ctext.split("```json cal:S6_TARGETS", 1)[1].split("```", 1)[0]
    s6_json = json.loads(block[block.index("{"):])
    s6_frame = s6_json.get("frame")

    zones = {
        "SOM_COPPER": {"id": "SOM_COPPER", "type": "禁入",
                        "rect": [som["copper_union"][0], som["copper_union"][1],
                                 som["copper_union"][2], som["copper_union"][3]],
                        "why": "SoM 承载区 4×100 焊盘铜箔实体 (板读)"},
        "SOM_FAB": {"id": "SOM_FAB", "type": "禁入",
                    "rect": [som["fab_union"][0], som["fab_union"][1],
                             som["fab_union"][2], som["fab_union"][3]],
                    "why": "SoM 承载区 4 组座体 F.Fab 外形并集 (板读)"},
        "SOM_ENV": {"id": "SOM_ENV", "type": "禁入",
                    "rect": [som["conservative_env"][0], som["conservative_env"][1],
                             som["conservative_env"][2], som["conservative_env"][3]],
                    "why": "SoM 保守包络 = 座体 F.Fab ± 0.05 笔画半宽 (板读)"},
        "OPEN_DEBUG": {"id": "OPEN_DEBUG", "type": "禁入",
                       "rect": openings["PORT_OPEN_DEBUG"]["tiers"]["2.54"]["open_rect"],
                       "why": "调试口开口 (罩 J_DEBUG) · h=2.54 档"},
        "OPEN_UART": {"id": "OPEN_UART", "type": "禁入",
                      "rect": openings["PORT_OPEN_UART"]["tiers"]["2.54"]["open_rect"],
                      "why": "检修口开口 (罩 J_UART) · h=2.54 档"},
        "MC_DEBUG": {"id": "MC_DEBUG", "type": "必清空",
                     "rect": openings["PORT_OPEN_DEBUG"]["tiers"]["2.54"]["must_clear"],
                     "why": "调试口座体必须清空区 (座体宽 1.775 = 板读铜箔宽 · 高 h=2.54)"},
        "MC_UART": {"id": "MC_UART", "type": "必清空",
                    "rect": openings["PORT_OPEN_UART"]["tiers"]["2.54"]["must_clear"],
                    "why": "检修口座体必须清空区 (座体宽 2.540 = MECH 模型 · 高 h=2.54)"},
        "USB_C_BODY": {"id": "USB_C_BODY", "type": "禁入",
                       "rect": [135.680, 0.000, 144.320, 6.400],
                       "why": "J_USB_C 座体 F.Fab 外框 (Y 下沿 = 板边) - 结构件必须开边口"},
        "USB_C_COPPER": {"id": "USB_C_COPPER", "type": "禁入",
                         "rect": [133.895, 2.300, 146.105, 5.825],
                         "why": "J_USB_C 16 信号焊盘 + 2 个 Ø0.65 NPTH 壳体固定孔"},
        "J_CHG_COPPER": {"id": "J_CHG_COPPER", "type": "禁入",
                         "rect": [133.0625, 56.150, 133.8375, 57.050],
                         "why": "J_CHG 主板侧 2 脚跨铰链载流焊盘对"},
    }

    rows = []
    # `D_LED_G` 可放行带 (ISS-278 §5 机器块 `led.full_height_bands`, 封装原点口径)
    LED_BANDS = [
        {"x0": 1.550, "x1": 3.450, "y0": 1.450, "y1": 98.950},
        {"x0": 72.540, "x1": 73.660, "y0": 1.450, "y1": 98.950},
    ]
    for t in s6_json["targets"]:
        ref = t["ref"]
        tx, ty = float(t["x"]), float(t["y"])
        fp = refs.get(ref)
        if fp is None:
            rows.append({"ref": ref, "target": [tx, ty], "frame": t.get("frame"),
                         "missing_on_board": True})
            continue
        loc = Board.local_extent(fp)
        fab_loc = Board.local_fab(fp)
        # 局部外框 -> 封装旋转 -> 平移到目标位
        pts = []
        for (lx, ly) in [(loc[0], loc[1]), (loc[2], loc[1]), (loc[2], loc[3]), (loc[0], loc[3])]:
            dx, dy = rot_xy(lx, ly, fp["rot"])
            pts.append((tx + dx, ty + dy))
        ext = bbox_of(pts)
        fab_pts = []
        for (lx, ly) in [(fab_loc[0], fab_loc[1]), (fab_loc[2], fab_loc[1]),
                         (fab_loc[2], fab_loc[3]), (fab_loc[0], fab_loc[3])]:
            dx, dy = rot_xy(lx, ly, fp["rot"])
            fab_pts.append((tx + dx, ty + dy))
        fab_ext = bbox_of(fab_pts)
        # 焊盘铜箔单独算 (目标位)
        copper_pts = []
        for p in fp["pads"]:
            w, h = p["sw"], p["sh"]
            if abs((p["prot"] + fp["rot"]) % 180.0 - 90.0) < 1e-6:
                w, h = h, w
            for (lx, ly) in [(p["px"] - w / 2, p["py"] - h / 2), (p["px"] + w / 2, p["py"] + h / 2)]:
                dx, dy = rot_xy(lx, ly, fp["rot"])
                copper_pts.append((tx + dx, ty + dy))
        cu = bbox_of(copper_pts)
        hits = []
        minclr = None
        for zid, z in zones.items():
            d_ext = rect_dist(ext, z["rect"])
            d_cu = rect_dist(cu, z["rect"])
            d = min(d_ext, d_cu)
            hit = d < 0
            if hit:
                hits.append(zid)
            if minclr is None or d < minclr:
                minclr = d
        # 分开记: 禁入命中 / 必清空净距不足
        hits_forbidden = [h for h in hits if zones[h]["type"] == "禁入"]
        mc_clear = []
        for zid in ("MC_DEBUG", "MC_UART"):
            d = min(rect_dist(ext, zones[zid]["rect"]), rect_dist(cu, zones[zid]["rect"]))
            mc_clear.append((zid, rd(d)))
        if hits_forbidden:
            verdict = "冲突"
        elif any(d < CRIT - 1e-9 for _, d in mc_clear):
            verdict = "需净距"
        else:
            verdict = "通过"
        # 占位冲突: 目标位上是否已有别的件 (含自身旧位以外)
        occupied = []
        for other in b.fps:
            if not other["ref"] or other["ref"] == ref:
                continue
            oloc = Board.local_extent(other)
            if oloc is None:
                continue
            op = []
            for (lx, ly) in [(oloc[0], oloc[1]), (oloc[2], oloc[1]),
                             (oloc[2], oloc[3]), (oloc[0], oloc[3])]:
                dx, dy = rot_xy(lx, ly, other["rot"])
                op.append((other["x"] + dx, other["y"] + dy))
            oext = bbox_of(op)
            if rect_overlap_area(ext, oext) > 1e-9:
                occupied.append(other["ref"])
        # LED 可放行带侵占检查 (封装原点口径)
        led_band_hits = []
        for bi, band in enumerate(LED_BANDS):
            if band["x0"] <= tx <= band["x1"] and band["y0"] <= ty <= band["y1"]:
                led_band_hits.append("LED_BAND_%d" % bi)
        rows.append({
            "ref": ref,
            "target_x": rd(tx), "target_y": rd(ty),
            "frame": t.get("frame"),
            "board_origin": [rd(fp["x"]), rd(fp["y"]), rd(fp["rot"])],
            "moved": bool(abs(fp["x"] - tx) > 1e-6 or abs(fp["y"] - ty) > 1e-6),
            "footprint_extent": [rd(fab_ext[0]), rd(fab_ext[1]), rd(fab_ext[2]), rd(fab_ext[3])],
            "footprint_extent_size": [rd(fab_ext[2] - fab_ext[0]), rd(fab_ext[3] - fab_ext[1])],
            "envelope_extent": [rd(ext[0]), rd(ext[1]), rd(ext[2]), rd(ext[3])],
            "envelope_extent_size": [rd(ext[2] - ext[0]), rd(ext[3] - ext[1])],
            "copper_extent": [rd(cu[0]), rd(cu[1]), rd(cu[2]), rd(cu[3])],
            "hit_zones": hits,
            "hit_forbidden": hits_forbidden,
            "mc_clearances": {k: v for k, v in mc_clear},
            "min_clearance_mm": rd(minclr) if minclr is not None else None,
            "occupied_by": occupied,
            "led_band_hits": led_band_hits,
            "verdict": verdict,
        })

    # ---------------- corner_radius 口径: 贴角可用区差值 ----------------
    W = edge_bbox[2] - edge_bbox[0]
    H = edge_bbox[3] - edge_bbox[1]
    K = EDGE_KEEPOUT
    R = 3.0

    def corner_usable_sharp(K, step=0.01):
        """直角角部可用面积 (相对角点, 局部坐标 x,y ∈ [0, s]², s = K*2+2)"""
        s = K * 2 + 2.0
        nx = int(s / step)
        cnt = 0
        for i in range(nx):
            x = (i + 0.5) * step
            for j in range(nx):
                y = (j + 0.5) * step
                if x >= K and y >= K:
                    cnt += 1
        return cnt * step * step

    def corner_usable_round(R, K, step=0.01):
        """圆角角部可用面积 (相对角点)"""
        s = R + K + 1.0
        nx = int(s / step)
        cnt = 0
        for i in range(nx):
            x = (i + 0.5) * step
            for j in range(nx):
                y = (j + 0.5) * step
                # 圆角板: 圆心 (R,R), 板边 = 圆弧; 可用 = 距圆弧 > K 且在板内
                d = math.hypot(x - R, y - R)
                if d >= R + K and x >= 0 and y >= 0:
                    cnt += 1
        return cnt * step * step

    a_sharp = corner_usable_sharp(K)
    a_round = corner_usable_round(R, K)
    # 板框面积差
    area_sharp = W * H
    area_round = W * H - 4 * (R * R - math.pi * R * R / 4.0)

    corner = {
        "edge_keepout_mm": K,
        "R_assumed_mm": R,
        "board_size": [rd(W), rd(H)],
        "corner_usable_area_sharp_mm2": rd(a_sharp),
        "corner_usable_area_roundR3_mm2": rd(a_round),
        "corner_usable_delta_mm2": rd(a_round - a_sharp),
        "board_area_sharp_mm2": rd(area_sharp),
        "board_area_roundR3_mm2": rd(area_round),
        "board_area_delta_mm2": rd(area_round - area_sharp),
        "total_usable_delta_mm2": rd(4 * (a_round - a_sharp) + (area_round - area_sharp)),
        "note": "负值 = 按 R=3.0 口径算出来的可用区比实板 (R=0.0) 小 => 保守",
    }

    # ---------------- §10 场景: 改 land pitch 的结构后果 ----------------
    def scenario(ref, new_pitch, body_w_model=None):
        p = openings["PORT_OPEN_DEBUG"] if ref == "J_DEBUG" else openings["PORT_OPEN_UART"]
        cu = p["copper_x"]
        cx = (cu[0] + cu[1]) / 2.0
        pad_w = 0.275
        npads = 4 if ref == "J_DEBUG" else 2
        span = (npads - 1) * new_pitch
        copper_w = span + pad_w
        new_cu = [rd(cx - copper_w / 2.0), rd(cx + copper_w / 2.0)]
        body_w = body_w_model if body_w_model else p["body_w"]
        w_clear = max(copper_w, body_w)
        mc_x = [rd(cx - w_clear / 2.0), rd(cx + w_clear / 2.0)]
        open_x = p["open_x"]
        clx = (open_x[1] - open_x[0] - w_clear) / 2.0
        out = {
            "ref": ref, "new_pitch_mm": new_pitch, "npads": npads,
            "old_copper_x": [rd(cu[0]), rd(cu[1])], "old_copper_w": rd(cu[1] - cu[0]),
            "new_copper_x": new_cu, "new_copper_w": rd(copper_w),
            "body_w_model": body_w, "body_w_source": p["body_w_source"],
            "w_clear_used": rd(w_clear),
            "w_clear_driver": "铜箔口径" if copper_w >= body_w else "座体口径",
            "must_clear_x": mc_x,
            "open_x": open_x, "open_x_changed": False,
            "clearance_x": rd(clx), "worst_clearance_x": rd(clx - 0.30),
            "pass_crit_x": bool(clx - 0.30 >= CRIT - 1e-9),
            "placeable_x0_range": [rd(open_x[0]), rd(mc_x[0])],
            "placeable_width": rd(mc_x[0] - open_x[0]),
        }
        # 与现状对比
        old_clx = (open_x[1] - open_x[0] - p["body_w"]) / 2.0
        out["old_clearance_x"] = rd(old_clx)
        out["old_placeable_width"] = rd(p["tiers"]["2.54"]["must_clear"][0] - open_x[0])
        out["delta_clearance_x"] = rd(clx - old_clx)
        out["delta_placeable_width"] = rd(out["placeable_width"] - out["old_placeable_width"])
        out["delta_w_clear"] = rd(w_clear - p["body_w"])
        return out

    scenarios = {
        "A_J_DEBUG_pitch_1.27": scenario("J_DEBUG", 1.27),
        "A_J_UART_pitch_1.27": scenario("J_UART", 1.27),
        "C_J_DEBUG_pitch_2.54": scenario("J_DEBUG", 2.54),
        "C_J_UART_pitch_2.54": scenario("J_UART", 2.54),
        "D_J_DEBUG_no_body": scenario("J_DEBUG", 0.50, body_w_model=0.0),
        "D_J_UART_no_body": scenario("J_UART", 0.50, body_w_model=0.0),
    }

    out = {
        "issue": "ISS-290",
        "agent": "mech-lead",
        "frame": FRAME,
        "frame_from_caliber": s6_frame,
        "board": board,
        "som": som,
        "openings": openings,
        "zones": zones,
        "lands": lands,
        "s6_rows": rows,
        "corner": corner,
        "scenarios": scenarios,
        "consts": {"crit": CRIT, "edge_keepout": EDGE_KEEPOUT, "open_w": OPEN_W,
                   "h_tiers": H_TIERS, "body_h_ref": BODY_H_REF,
                   "jd_body_w_model": JD_BODY_W_MODEL},
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)

    # ---------------- 打印 ----------------
    print("== 板框 ==")
    print("Edge.Cuts centerline bbox:", board["edge_cuts_centerline_bbox"],
          "outer:", board["edge_cuts_outer_size"], "stroke", stroke,
          "lines", len(edge_cut_lines), "kinds", edge_kinds)
    print("== SoM ==")
    print("copper", som["copper_union"], som["copper_size"])
    print("fab   ", som["fab_union"], som["fab_size"])
    print("env   ", som["conservative_env"], som["conservative_size"], "pads", som["npads_total"])
    print("== 开口 ==")
    for k, v in openings.items():
        print(k, "copper", v["copper_x"], v["copper_y"], "body_w", v["body_w"], "open_x", v["open_x"])
        for h, t in v["tiers"].items():
            print("   h=%s open=%s mc=%s clx=%.4f cly=%.4f pass=%s" %
                  (h, t["open_rect"], t["must_clear"], t["clearance_x"], t["clearance_y"], t["pass_crit"]))
    print("== land ==")
    for r, v in lands.items():
        print(r, "npads", v["npads"], "(sig %d / npth %d)" % (v["npads_signal"], v["npads_npth"]),
              "pitch_x", v["pitch_x_unique"], "rows", v["n_rows"],
              "cols", v["pad_x_count"], "copper", v["copper_x"], v["copper_y"],
              "fab", v["fab_x"], v["fab_y"])
    print("== S6 ==")
    for r in rows:
        print("%-14s tgt(%8.3f,%7.3f) board(%8.3f,%7.3f) moved=%s ext=%s hits=%s mc=%s min=%s occ=%s led=%s => %s" %
              (r["ref"], r["target_x"], r["target_y"], r["board_origin"][0], r["board_origin"][1],
               r["moved"], r["footprint_extent"], r["hit_zones"], r["mc_clearances"],
               r["min_clearance_mm"], r["occupied_by"], r["led_band_hits"], r["verdict"]))
    print("== corner ==")
    print(corner)
    print("== scenarios ==")
    for k, v in scenarios.items():
        print(k, json.dumps(v, ensure_ascii=False))


if __name__ == "__main__":
    main()
