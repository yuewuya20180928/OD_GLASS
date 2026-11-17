# -*- coding: utf-8 -*-
"""ISS-278 计算脚本 (只读) —— 一次性实算, 数字全部来自盘上板 + 既有闸脚本常量"""
import importlib.util, math, os, json, sys
HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))
def load(p, name):
    spec = importlib.util.spec_from_file_location(name, p)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
cfc = load(os.path.join(PROJ, "MECH", "check_board_frame_coords.py"), "cfc_iss278")
s6  = load(os.path.join(PROJ, "MECH", "board_port_opening_s6_check.py"), "s6_iss278")
BASE, TOL, CRIT = dict(s6.BASE), dict(s6.TOL), s6.CRIT
OPEN_X, OPEN_Y = s6.OPEN_X, s6.OPEN_Y
board = cfc.read_board(PROJ); fps = board["fps"]; edge = board["edge"]
out = {}
out["edge"] = edge
out["const"] = {"OPEN_X": OPEN_X, "OPEN_Y": OPEN_Y, "CRIT": CRIT, "TOL": TOL,
                 "EDGE_KEEPOUT": cfc.EDGE_KEEPOUT, "BODY_H_assumption": cfc.BODY_H}

def conn(ref):
    f = fps[ref]; ps = f["pads"]
    cx = sum(p["x"] for p in ps)/len(ps); cy = sum(p["y"] for p in ps)/len(ps)
    return {"ref": ref, "origin": f["at"], "pad_center": (cx, cy), "npads": len(ps),
            "copper": cfc.copper_bbox(f), "fab": cfc.fab_bbox(f),
            # ★FIX(ISS-278 续做): "pads" 被打平成 tuple ⇒ 后面按 dict 索引报 TypeError ⇒ 另存原始 dict 列表
            "pads_raw": ps,
            "pads": [(p["num"], round(p["x"],4), round(p["y"],4), p["sx"], p["sy"]) for p in ps]}
CONNS = {r: conn(r) for r in ("J_DEBUG", "J_UART", "D_LED_G", "R_LED_G")}
out["conns"] = CONNS

# ---------- 座体宽三口径 ----------
def body_widths(ref):
    c = CONNS[ref]; cw = c["copper"][1]-c["copper"][0]; fb = c["fab"][1]-c["fab"][0]
    return {"copper": cw, "fab": fb}
out["body_widths"] = {r: body_widths(r) for r in ("J_DEBUG", "J_UART")}

# ---------- §3b 两条独立开口: 三套座体宽口径 ----------
def opening_spec(ref, body_w, h):
    c = CONNS[ref]; cx, cy = c["pad_center"]
    bx0, bx1 = cx - body_w/2, cx + body_w/2
    by0, by1 = cy - h/2, cy + h/2
    cl_x = (OPEN_X - body_w)/2; cl_y = (OPEN_Y - h)/2
    return {"body": (bx0, bx1, by0, by1), "open": (bx0-cl_x, bx1+cl_x, by0-cl_y, by1+cl_y),
            "cl_x": cl_x, "cl_y": cl_y, "worst_cl_x": cl_x - TOL["fdm_part"],
            "worst_cl_y": cl_y - TOL["fdm_part"], "cx": cx, "cy": cy}
def free_space(ref, body_w, h):
    """开口左下角可放行区间 (沿用 ISS-276 的 x0_range/y0_range 口径)"""
    s = opening_spec(ref, body_w, h)
    bx0, bx1, by0, by1 = s["body"]; ox0, ox1, oy0, oy1 = s["open"]
    return {"x0_range": (max(ox0, ox1-OPEN_X), min(bx0, edge["x1"]-cfc.EDGE_KEEPOUT-OPEN_X)),
            "y0_range": (max(oy0, oy1-OPEN_Y), min(by0, edge["y1"]-cfc.EDGE_KEEPOUT-OPEN_Y)),
            "open": s["open"]}
# MECH 现行模型: J_DEBUG 用铜箔宽 1.775, J_UART 用硬编 2.54
MECH_W = {"J_DEBUG": CONNS["J_DEBUG"]["copper"][1]-CONNS["J_DEBUG"]["copper"][0],
          "J_UART": 2.54}
out["mech_model_w"] = MECH_W
out["openings_mech_model"] = {}
for r in ("J_DEBUG", "J_UART"):
    out["openings_mech_model"][r] = {"h=2.54": {**opening_spec(r, MECH_W[r], 2.54),
                                                **free_space(r, MECH_W[r], 2.54)}}
# F.Fab 6.00 口径 (板自己占的座体框)
for r in ("J_DEBUG", "J_UART"):
    w = CONNS[r]["fab"][1]-CONNS[r]["fab"][0]
    out["openings_mech_model"][r]["h=2.54_fab6"] = {**opening_spec(r, w, 2.54),
                                                    **free_space(r, w, 2.54)}
# ---------- 合并开口不可行 ----------
jd, ju = CONNS["J_DEBUG"], CONNS["J_UART"]
b1 = opening_spec("J_DEBUG", MECH_W["J_DEBUG"], 2.54)["body"]
b2 = opening_spec("J_UART",  MECH_W["J_UART"],  2.54)["body"]
content_w = max(b1[1], b2[1]) - min(b1[0], b2[0])
out["merged"] = {"content_w": content_w, "open_w": OPEN_X,
                 "cl_x": (OPEN_X-content_w)/2, "gap": content_w-OPEN_X,
                 "feasible": content_w <= OPEN_X,
                 "union_body_x": (min(b1[0],b2[0]), max(b1[1],b2[1]))}
dx = jd["origin"][0]-ju["origin"][0]; dy = jd["origin"][1]-ju["origin"][1]
out["separation"] = {"dX": dx, "dY": dy, "straight": math.hypot(dx,dy),
                      "pad_center_dX": jd["pad_center"][0]-ju["pad_center"][0],
                      "pad_center_dY": jd["pad_center"][1]-ju["pad_center"][1]}

# ---------- §4b 座体高度参数化 ----------
def open_y_formula(cy, h, open_y_spec=OPEN_Y):
    """OPEN_Y_eff(h) = max(定档, h + 2*(CRIT+TOL)) ; 开口 Y = [cy - OPEN_Y_eff/2, cy + OPEN_Y_eff/2]"""
    need = h + 2*(CRIT + TOL["fdm_part"])
    eff = max(open_y_spec, need)
    return {"need": need, "eff": eff, "y0": cy-eff/2, "y1": cy+eff/2,
            "grew": eff > open_y_spec + 1e-9}
H_TIERS = [("h_lo", 0.90, "座体不可能低于焊盘铜箔高 0.90 (板读)"),
           ("h_ref", 2.54, "MECH 现行假设 BASE['jd_body_h'] (★[0数据] 不是事实★)"),
           ("h_hi", 4.00, "板自己给连接器占的 F.Fab 盒高 4.00 (板读) ⇒ 座体不得高于它")]
out["h_tiers"] = []
for tag, h, why in H_TIERS:
    row = {"tag": tag, "h": h, "why": why}
    for r in ("J_DEBUG", "J_UART"):
        c = CONNS[r]; cy = c["pad_center"][1]; cx = c["pad_center"][0]
        w = MECH_W[r]
        f = open_y_formula(cy, h)
        bx0, bx1 = cx-w/2, cx+w/2
        cl_x = (OPEN_X-w)/2
        ox0, ox1 = bx0-cl_x, bx1+cl_x
        rect = (ox0, ox1, f["y0"], f["y1"])
        som_hits = cfc.rect_hits(rect, [p for rr in ("J_SOM_P1","J_SOM_P2","J_SOM_P3","J_SOM_P4") for p in fps[rr]["pads"]])
        row[r] = {"cy": cy, "cx": cx, "body_w": w, "body_x": (bx0,bx1),
                  "body_y": (cy-h/2, cy+h/2),
                  "open_y_need": f["need"], "open_y_eff": f["eff"], "grew": f["grew"],
                  "open": rect, "cl_x": cl_x, "worst_cl_x": cl_x-TOL["fdm_part"],
                  "in_frame": (ox0 >= edge["x0"]+cfc.EDGE_KEEPOUT and ox1 <= edge["x1"]-cfc.EDGE_KEEPOUT
                               and f["y0"] >= edge["y0"]+cfc.EDGE_KEEPOUT and f["y1"] <= edge["y1"]-cfc.EDGE_KEEPOUT),
                  "som_hits": som_hits,
                  "cl_y_nominal": (f["eff"]-h)/2,
                  "cl_y_worst": (f["eff"]-h)/2 - TOL["fdm_part"]}
    out["h_tiers"].append(row)
out["h_feasibility"] = {"OPEN_Y_fixed_4.60_ok_for_h_max": OPEN_Y - 2*(CRIT+TOL["fdm_part"]),
                         "formula": "OPEN_Y_eff(h) = max(4.60, h + 2*(0.60+0.30)) = max(4.60, h+1.80)"}

# ---------- §6b D_LED_G 光孔两假设 ----------
led = CONNS["D_LED_G"]; res = CONNS["R_LED_G"]
lb = led["copper"]; lox, loy = led["origin"]
rel = (lb[0]-lox, lb[1]-lox, lb[2]-loy, lb[3]-loy)
rp = {p["num"]: p for p in res["pads_raw"]}; r2 = rp["2"]
dp = {p["num"]: p for p in led["pads_raw"]}; d1 = dp["1"]
def led_net_len(origin):
    """pad-to-pad: R_LED_G.2 ↔ D_LED_G.1"""
    ox, oy = origin
    p1 = (ox + (d1["x"]-lox), oy + (d1["y"]-loy))
    return math.hypot(p1[0]-r2["x"], p1[1]-r2["y"]), p1
def corner_len(origin):
    """ISS-276 §4.2 的口径: R_LED_G.2 ↔ D_LED_G 铜箔外框左下角"""
    ox, oy = origin
    return math.hypot(ox+rel[0]-r2["x"], oy+rel[2]-r2["y"])
out["led"] = {"led_origin": (lox,loy), "led_copper": lb, "led_rel": rel,
              "r_origin": (res["origin"][0],res["origin"][1]),
              "r_pad2": (r2["x"], r2["y"]), "d_pad1": (d1["x"], d1["y"]),
              "d_pad1_rel": (d1["x"]-lox, d1["y"]-loy),
              "current_pad_to_pad": math.hypot(d1["x"]-r2["x"], d1["y"]-r2["y"])}
sp = cfc.led_space(board, {"openings": {"J_DEBUG": {"open": opening_spec("J_DEBUG", MECH_W["J_DEBUG"], 2.54)["open"]},
                                        "J_UART":  {"open": opening_spec("J_UART",  MECH_W["J_UART"],  2.54)["open"]}}})
out["led"]["placeable_n"] = len(sp["placeable"]); out["led"]["full_height_n"] = len(sp["full_height_bands"])
out["led"]["full_height_bands"] = [tuple(round(v,3) for v in (b["ox0"],b["ox1"],b["oy0"],b["oy1"])) for b in sp["full_height_bands"]]
out["led"]["nearest_band"] = tuple(round(v,3) for v in (sp["nearest_band"]["ox0"],sp["nearest_band"]["ox1"],
                                                        sp["nearest_band"]["oy0"],sp["nearest_band"]["oy1"])) if sp["nearest_band"] else None
out["led"]["nearest_corner_len"] = [round(n["dist"],6) for n in sp["nearest_to_r_led_g"][:5]]
# 净距敏感度 (ISS-276 §4.2 口径) + pad-to-pad 对照
sweep = []
for clr in (0.0, 0.10, 0.20, 0.50):
    s2 = cfc.led_space(board, {"openings": {"J_DEBUG": {"open": opening_spec("J_DEBUG", MECH_W["J_DEBUG"], 2.54)["open"]},
                                             "J_UART":  {"open": opening_spec("J_UART",  MECH_W["J_UART"],  2.54)["open"]}}}, clr=clr)
    near = s2["nearest_to_r_led_g"][0] if s2["nearest_to_r_led_g"] else None
    row = {"clr": clr, "n_placeable": len(s2["placeable"]),
           "corner_origin": tuple(round(v,3) for v in near["origin"]) if near else None,
           "corner_len": round(near["dist"],6) if near else None}
    if near:
        # ★FIX(ISS-278 续做): led_net_len 返回 (dist, (x,y)) ⇒ 不能整体 round
        _len, _p1 = led_net_len(near["origin"])
        row["pad_to_pad_len"] = round(_len, 6)
        row["pad1_at"] = tuple(round(v, 4) for v in _p1)
    sweep.append(row)
out["led"]["sweep"] = sweep
out["led"]["net_formula"] = "L_pad2pad(Xled,Yled) = hypot((Xled-0.45) - 7.50, (Yled-0.20) - 62.60) = hypot(Xled-7.95, Yled-62.80)"

# ---------- §7b 连接器占位参数对照 ----------
import csv
params = json.load(open(os.path.join(PROJ, "HW", "PCB", "demo_mainboard_params.json"), encoding="utf-8"))
out["params_connectors"] = params["connectors"]
out["params_som"] = params["som"]
out["params_board"] = {k: v for k, v in params["board"].items() if not k.startswith("_")}
# 网表里 J_DEBUG/J_UART 的器件行
rows = []
with open(os.path.join(PROJ, "HW", "netlist_v1.csv"), encoding="utf-8") as fh:
    for r in csv.reader(fh):
        rows.append(r)
for r in rows:
    if len(r) > 3 and r[3] in ("J_DEBUG", "J_UART", "J_USB_C", "U_SOM_RK3572"):
        out.setdefault("netlist_rows", {})[r[3]] = {"ref": r[3], "value": r[4], "kind": r[6] if len(r) > 6 else "",
                                                    "note": (r[10] if len(r) > 10 else "")[:200]}
print(json.dumps(out, ensure_ascii=False, indent=1, default=str))
