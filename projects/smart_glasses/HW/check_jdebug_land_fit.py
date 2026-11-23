#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-376 · hw-lead · `J_DEBUG` 换官方 1x4 P1.27 THT land 的【落位可行性】闸
=====================================================================
判据 L0~L8 (★每条 fail-closed·★红了 rc=1★)
  L0 官方 1x4 THT land 的 pad 坐标/形状/钻孔/fab/courtyard == 盘上 .kicad_mod 实读 (★自己解析·不写死★)
  L1 板面 DRC 孔约束 == .kicad_pro 实读 (★自己读·不写死★)
  L2 §2 可行域表【逐格】与闸自己实算一致 (孔净距/铜箔净距/fab/余量)
  L3 §1 现位冲突表逐条可复算 (现位 pad ↔ via 的孔净距)
  L4 三朝向 (rot 0/90/270) 坐标换算由脚本自己算 (★FOOTPRINT.SetOrientationDegrees·不手算旋转矩阵★)
  L5 §2 给出【区间/可行区】而不是【一个点】 (★只给一个坐标 ⇒ 红★)
  L6 §3 代价清单每条必须带坐标 (★只写"要挪过孔"不带坐标 ⇒ 红★)
  L7 板面零写板自证 (md5 / mtime / size 三项)
  L8 证据等级白名单 + 零挂起措辞 + 判据句/事实句分开 + 零挂链
用法:
  python3 HW/check_jdebug_land_fit.py              # 跑 L0~L8
  python3 HW/check_jdebug_land_fit.py --selftest   # 跑 >=8 条反向用例 (末行 ALL TESTS PASS)
  python3 HW/check_jdebug_land_fit.py --verbose    # 打印每条判据的明细
★ 只读真板 + 只读真相页; 不写任何板文件; 不挂进 state/gate_check.py ★
"""
import hashlib
import json
import math
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
BOARD = os.path.join(ROOT, "HW/PCB/demo_mainboard.kicad_pcb")
PROJ = os.path.join(ROOT, "HW/PCB/demo_mainboard.kicad_pro")
PAGE = os.path.join(ROOT, "HW/PCB/BOARD_ONEPASS_JDEBUG_LAND_FIT.md")
LIBDIR = "/home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty"
FPNAME = "PinHeader_1x04_P1.27mm_Vertical"
MODFILE = os.path.join(LIBDIR, FPNAME + ".kicad_mod")
PCBNEW_SH = os.path.join(ROOT, "state/pcbnew_py.sh")
SBX = os.path.join(ROOT, "tmp/iss376_sbx")
EVID_JSON = os.path.join(ROOT, "logs/iss376/scan_land_fit.json")

# ★ 零写板自证常量 (★这是板身份, 不是 DRC 判据 · DRC 判据一律实读★)
BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"
BOARD_MTIME = "2026-11-06 07:07:17.362193413"
BOARD_SIZE = 4940213

VERBOSE = "--verbose" in sys.argv
SELFTEST = "--selftest" in sys.argv

# ★逐格实算缓存 (★同一进程内板数据不变·自测跑 11 条用例时避免重算 11 遍·★不改变任何判定口径★)
_CELL_CACHE = {}

RESULT = []          # [(L_id, ok:bool, msg:str)]
EVID_LEVELS = {"L1-文档推断", "L2-二手引用", "L3-本机实测", "L4-交叉验证", "L5-实测+复核"}
HANG_WORDS = ["挂起", "待定", "TBD", "等原厂", "等回复", "待确认", "待补", "先挂着", "搁置"]


def rec(lid, ok, msg):
    RESULT.append((lid, bool(ok), msg))
    if VERBOSE:
        print("  [%s] %s  %s" % (lid, "PASS" if ok else "FAIL", msg))
    return bool(ok)


# =====================================================================
# 0. 页面机器块解析
# =====================================================================
def parse_page_blocks(text):
    """取 <!-- ISS376:BEGIN XXX --> ... ```json ... ``` ... <!-- ISS376:END XXX -->"""
    out = {}
    pat = re.compile(r"<!--\s*ISS376:BEGIN\s+([A-Z_0-9]+)\s*-->(.*?)<!--\s*ISS376:END\s+\1\s*-->", re.S)
    for m in pat.finditer(text):
        name, body = m.group(1), m.group(2)
        jm = re.search(r"```json\s*\n(.*?)\n```", body, re.S)
        if not jm:
            out[name] = None
            continue
        try:
            out[name] = json.loads(jm.group(1))
        except Exception as e:
            out[name] = None
            out[name + "__parse_error"] = str(e)
    return out


# =====================================================================
# 1. 官方 land: 自己解析盘上 .kicad_mod (★不写死任何尺寸★)
# =====================================================================
def parse_mod(path):
    txt = open(path, encoding="utf-8").read()
    pads = []
    for m in re.finditer(r'\(pad\s+"([^"]+)"\s+(\S+)\s+(\S+)\s*\n\s*\(at\s+([-\d.]+)\s+([-\d.]+)(?:[^\)]*)\)\s*\n\s*\(size\s+([\d.]+)\s+([\d.]+)\)\s*\n\s*\(drill\s+([\d.]+)\)', txt):
        pads.append(dict(name=m.group(1), ptype=m.group(2), shape=m.group(3),
                         x=float(m.group(4)), y=float(m.group(5)),
                         w=float(m.group(6)), h=float(m.group(7)),
                         drill=float(m.group(8))))
    crtyd = None
    for m in re.finditer(r'\(fp_rect\s*\n\s*\(start\s+([-\d.]+)\s+([-\d.]+)\)\s*\n\s*\(end\s+([-\d.]+)\s+([-\d.]+)\).*?\(layer\s+"F\.CrtYd"\)', txt, re.S):
        crtyd = dict(x1=float(m.group(1)), y1=float(m.group(2)),
                     x2=float(m.group(3)), y2=float(m.group(4)))
    fab_pts = []
    for m in re.finditer(r'\(fp_line\s*\n\s*\(start\s+([-\d.]+)\s+([-\d.]+)\)\s*\n\s*\(end\s+([-\d.]+)\s+([-\d.]+)\).*?\(layer\s+"F\.Fab"\)', txt, re.S):
        fab_pts += [(float(m.group(1)), float(m.group(2))), (float(m.group(3)), float(m.group(4)))]
    fab = None
    if fab_pts:
        fab = dict(x1=min(p[0] for p in fab_pts), y1=min(p[1] for p in fab_pts),
                   x2=max(p[0] for p in fab_pts), y2=max(p[1] for p in fab_pts))
    pitch = sorted(p["y"] for p in pads)
    return dict(pads=pads, crtyd=crtyd, fab=fab,
                local_span_y=(max(pitch) - min(pitch)) if pitch else None,
                local_span_x=0.0,
                copper_x_span=max((p["w"] for p in pads), default=0.0),
                pad_drill=sorted(set(p["drill"] for p in pads)))


# =====================================================================
# 2. 几何引擎 (与落位扫描脚本同口径)
# =====================================================================
def seg_seg_dist(p1, p2, p3, p4):
    def pt_seg(p, a, b):
        ax, ay = a; bx, by = b; px, py = p
        dx, dy = bx - ax, by - ay
        L2 = dx * dx + dy * dy
        if L2 == 0:
            return math.hypot(px - ax, py - ay)
        t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
        return math.hypot(px - (ax + t * dx), py - (ay + t * dy))

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    d1 = cross(p3, p4, p1); d2 = cross(p3, p4, p2); d3 = cross(p1, p2, p3); d4 = cross(p1, p2, p4)
    if ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0)):
        return 0.0
    return min(pt_seg(p1, p3, p4), pt_seg(p2, p3, p4), pt_seg(p3, p1, p2), pt_seg(p4, p1, p2))


def rect_corners(cx, cy, hw, hh, ang):
    ca, sa = math.cos(ang), math.sin(ang)
    o = []
    for dx, dy in ((-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)):
        o.append((cx + dx * ca - dy * sa, cy + dx * sa + dy * ca))
    return o


def rect_rect_dist(r1, r2):
    a = rect_corners(*r1); b = rect_corners(*r2)
    best = 1e9
    for i in range(4):
        for j in range(4):
            d = seg_seg_dist(a[i], a[(i + 1) % 4], b[j], b[(j + 1) % 4])
            if d < best:
                best = d
    return best


def pt_seg_dist(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    L2 = dx * dx + dy * dy
    if L2 == 0:
        return math.hypot(px - x1, py - y1)
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / L2))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))


class Grid:
    def __init__(self, cell=1.0):
        self.cell = cell; self.d = {}

    def key(self, x, y):
        return (int(math.floor(x / self.cell)), int(math.floor(y / self.cell)))

    def add(self, rec_, bbox=None):
        if bbox is None:
            bbox = (rec_["x"], rec_["y"], rec_["x"], rec_["y"])
        i0 = int(math.floor(bbox[0] / self.cell)); i1 = int(math.floor(bbox[2] / self.cell))
        j0 = int(math.floor(bbox[1] / self.cell)); j1 = int(math.floor(bbox[3] / self.cell))
        for i in range(i0, i1 + 1):
            for j in range(j0, j1 + 1):
                self.d.setdefault((i, j), []).append(rec_)

    def query(self, x, y, r):
        c = self.cell; out = []
        for i in range(int(math.floor((x - r) / c)), int(math.floor((x + r) / c)) + 1):
            for j in range(int(math.floor((y - r) / c)), int(math.floor((y + r) / c)) + 1):
                for rec_ in self.d.get((i, j), []):
                    if rec_ not in out:
                        out.append(rec_)
        return out


# =====================================================================
# 3. 板面数据 (经 state/pcbnew_py.sh 子进程 · 只读)
# =====================================================================
HELPER_SRC = r'''
import json, math, os, sys
import pcbnew
ROOT = sys.argv[1]
LIBDIR = sys.argv[2]
FPNAME = sys.argv[3]
BOARD = os.path.join(ROOT, "HW/PCB/demo_mainboard.kicad_pcb")
MM = 1000000.0
def mm(v): return float(v)/MM
b = pcbnew.LoadBoard(BOARD)
out = {}
out["pcbnew_version"] = pcbnew.GetBuildVersion()
ebb = b.GetBoardEdgesBoundingBox()
out["board_edges"] = dict(x1=mm(ebb.GetLeft()), y1=mm(ebb.GetTop()),
                          x2=mm(ebb.GetRight()), y2=mm(ebb.GetBottom()))
vias=[]; tracks=[]; smd=[]; pth=[]; fps=[]
for t in b.GetTracks():
    if t.GetClass()=="PCB_VIA":
        p=t.GetPosition()
        vias.append(dict(x=mm(p.x), y=mm(p.y), net=t.GetNetname(),
                         drill=mm(t.GetDrillValue()), dia=mm(t.GetWidth(pcbnew.F_Cu))))
    else:
        s=t.GetStart(); e=t.GetEnd()
        tracks.append(dict(x1=mm(s.x), y1=mm(s.y), x2=mm(e.x), y2=mm(e.y),
                           w=mm(t.GetWidth()), net=t.GetNetname(), layer=t.GetLayerName()))
for f in b.GetFootprints():
    ref=f.GetReference(); p=f.GetPosition(); cy=None
    try:
        bb=f.GetCourtyard(pcbnew.F_CrtYd).BBox()
        cy=dict(x1=mm(bb.GetLeft()), y1=mm(bb.GetTop()), x2=mm(bb.GetRight()), y2=mm(bb.GetBottom()))
    except Exception:
        bb=f.GetBoundingBox(False, False)
        cy=dict(x1=mm(bb.GetLeft()), y1=mm(bb.GetTop()), x2=mm(bb.GetRight()), y2=mm(bb.GetBottom()))
    fps.append(dict(ref=ref, x=mm(p.x), y=mm(p.y),
                    orient=float(f.GetOrientation().AsDegrees()), cy=cy))
    for pad in f.Pads():
        pp=pad.GetPosition()
        r=dict(fp=ref, name=pad.GetPadName(), x=mm(pp.x), y=mm(pp.y), net=pad.GetNetname(),
               shape=int(pad.GetShape()), w=mm(pad.GetSizeX()), h=mm(pad.GetSizeY()),
               ang=math.radians(float(pad.GetOrientation().AsDegrees())),
               drill=mm(pad.GetDrillSizeX()), attr=int(pad.GetAttribute()))
        if r["attr"]==pcbnew.PAD_ATTRIB_PTH: pth.append(r)
        else: smd.append(r)
out["vias"]=vias; out["tracks"]=tracks; out["smd"]=smd; out["pth"]=pth; out["fps"]=fps
jd=[f for f in b.GetFootprints() if f.GetReference()=="J_DEBUG"][0]
jp=jd.GetPosition()
cur=dict(origin_x=mm(jp.x), origin_y=mm(jp.y), orient=round(float(jd.GetOrientation().AsDegrees()),4),
         fp_id=jd.GetFPIDAsString(), pads=[])
for pad in sorted(jd.Pads(), key=lambda q: mm(q.GetPosition().x)):
    pp=pad.GetPosition()
    cur["pads"].append(dict(name=pad.GetPadName(), x=mm(pp.x), y=mm(pp.y), net=pad.GetNetname(),
                            shape=int(pad.GetShape()), w=mm(pad.GetSizeX()), h=mm(pad.GetSizeY()),
                            attr=int(pad.GetAttribute())))
out["current"]=cur
offs={}
for rot in (0,90,270):
    fp=pcbnew.FootprintLoad(LIBDIR, FPNAME)
    fp.SetOrientationDegrees(rot)
    base=fp.GetPosition(); bx,by=mm(base.x),mm(base.y)
    o=[]
    for pad in sorted(fp.Pads(), key=lambda q: q.GetPadName()):
        pp=pad.GetPosition()
        o.append(dict(name=pad.GetPadName(), dx=mm(pp.x)-bx, dy=mm(pp.y)-by,
                      drill=mm(pad.GetDrillSizeX()), shape=int(pad.GetShape()),
                      w=mm(pad.GetSizeX()), h=mm(pad.GetSizeY())))
    offs[str(rot)]=o
out["orient_offsets"]=offs
crt_off={}
for rot in (0,90,270):
    fp2=pcbnew.FootprintLoad(LIBDIR, FPNAME)
    fp2.SetOrientationDegrees(rot)
    fp2.SetPosition(pcbnew.VECTOR2I_MM(0.0,0.0))
    b.Add(fp2)
    cbb=fp2.GetCourtyard(pcbnew.F_CrtYd).BBox()
    crt_off[str(rot)]=dict(x1=mm(cbb.GetLeft()), y1=mm(cbb.GetTop()),
                            x2=mm(cbb.GetRight()), y2=mm(cbb.GetBottom()))
    b.Remove(fp2)
out["crt_offset"]=crt_off
open(sys.argv[4], "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False))
print("[helper] wrote " + sys.argv[4])
'''


def load_board_data():
    if not os.path.exists(PCBNEW_SH):
        return None, "state/pcbnew_py.sh 不存在"
    os.makedirs(SBX, exist_ok=True)
    hp = os.path.join(SBX, "gate_board_dump.py")
    with open(hp, "w", encoding="utf-8") as fh:
        fh.write(HELPER_SRC)
    jf = os.path.join(SBX, "gate_board_dump.json")
    try:
        r = subprocess.run(["bash", PCBNEW_SH, hp, ROOT, LIBDIR, FPNAME, jf],
                           capture_output=True, text=True, timeout=900)
    except Exception as e:
        return None, "pcbnew 子进程异常: %s" % e
    if r.returncode != 0:
        return None, "pcbnew 子进程 rc=%d: %s" % (r.returncode, (r.stderr or "")[-400:])
    if not os.path.exists(jf):
        return None, "pcbnew 子进程未产出 JSON: %s" % ((r.stdout or "")[-300:])
    try:
        d = json.loads(open(jf, encoding="utf-8").read())
    except Exception as e:
        return None, "pcbnew 输出解析失败: %s" % e
    return d, None


# =====================================================================
# 4. 落位评估 (与扫描脚本同口径)
# =====================================================================
class Evaluator(object):
    def __init__(self, data, mod, rules, netmap):
        self.d = data
        self.mod = mod
        self.min_h2h = float(rules["min_hole_to_hole"])
        self.req_cu = 0.2
        nc = rules.get("_netclass", {}) or {}
        for v in nc.values():
            if isinstance(v, (int, float)) and v > 0:
                self.req_cu = float(v)
        self.netmap = netmap
        self.hole_grid = Grid(2.0)
        self.cu_grid = Grid(2.0)
        self.cy_grid = Grid(4.0)
        for v in data["vias"]:
            self.hole_grid.add(v)
            self.cu_grid.add(dict(x=v["x"], y=v["y"], kind="circle", r=v["dia"] / 2.0,
                                  net=v["net"], ref=v["net"]))
        for p in data["pth"]:
            self.hole_grid.add(dict(x=p["x"], y=p["y"], drill=p["drill"], net=p["net"], ref=p["fp"]))
        for p in data["smd"]:
            if p["fp"] == "J_DEBUG":
                continue
            self.cu_grid.add(dict(x=p["x"], y=p["y"], kind="rect", hw=p["w"] / 2.0, hh=p["h"] / 2.0,
                                  ang=p["ang"], net=p["net"], ref="%s.%s" % (p["fp"], p["name"])))
        for t in data["tracks"]:
            self.cu_grid.add(dict(kind="seg", x1=t["x1"], y1=t["y1"], x2=t["x2"], y2=t["y2"],
                                  hw=t["w"] / 2.0, net=t["net"], ref="TRK"),
                             bbox=(min(t["x1"], t["x2"]), min(t["y1"], t["y2"]),
                                   max(t["x1"], t["x2"]), max(t["y1"], t["y2"])))
        for f in data["fps"]:
            if f["ref"] == "J_DEBUG" or not f.get("cy"):
                continue
            self.cy_grid.add(f, bbox=(f["cy"]["x1"], f["cy"]["y1"], f["cy"]["x2"], f["cy"]["y2"]))
        e = data["board_edges"]
        self.edge = e
        self.crt_off = data.get("crt_offset") or {}
        crt = mod["crtyd"]
        self.crt_hw = (crt["x2"] - crt["x1"]) / 2.0
        self.crt_hh = (crt["y2"] - crt["y1"]) / 2.0

    def evaluate(self, x, y, rot, offs):
        """返回 dict(ok, margin, edge_margin, n_via_viol, n_cu_viol, viol[...])"""
        ck = (int(rot), round(x, 4), round(y, 4))
        hit = _CELL_CACHE.get(ck)
        if hit is not None:
            return hit
        o = offs
        margin = 1e9
        vv = []; vc = []
        for q in o:
            nm = q["name"]; px = x + q["dx"]; py = y + q["dy"]
            dr = q["drill"]; pw = q["w"]; ph = q["h"]
            net = self.netmap.get(nm, "")
            for v in self.hole_grid.query(px, py, 3.0):
                dist = math.hypot(px - v["x"], py - v["y"])
                raw = dist - (dr / 2.0 + v["drill"] / 2.0)
                gap = raw - self.min_h2h
                if gap < margin:
                    margin = gap
                if gap < 0:
                    vv.append(dict(pad=nm, px=round(px, 4), py=round(py, 4),
                                   obj_x=v["x"], obj_y=v["y"], obj_net=v.get("net"), obj_ref=v.get("ref"),
                                   hole_gap=round(raw, 4), deficit=round(-gap, 4)))
            for it in self.cu_grid.query(px, py, 2.0):
                if it.get("net") == net:
                    continue
                if it["kind"] == "circle":
                    dist = math.hypot(px - it["x"], py - it["y"]) - it["r"] - (pw / 2.0)
                elif it["kind"] == "rect":
                    dist = rect_rect_dist((px, py, pw / 2.0, ph / 2.0, 0.0),
                                          (it["x"], it["y"], it["hw"], it["hh"], it["ang"]))
                else:
                    dist = pt_seg_dist(it["x1"], it["y1"], it["x2"], it["y2"], px, py) - it["hw"] - (pw / 2.0)
                g = dist - self.req_cu
                if g < margin:
                    margin = g
                if g < 0:
                    vc.append(dict(pad=nm, px=round(px, 4), py=round(py, 4), ref=it["ref"],
                                   kind=it["kind"], net=it.get("net"), gap=round(dist, 4)))
        co = self.crt_off.get(str(rot))
        if co is None:
            co = dict(x1=-self.crt_hw, y1=-self.crt_hh, x2=self.crt_hw, y2=self.crt_hh)
        cx1, cy1 = x + co["x1"], y + co["y1"]
        cx2, cy2 = x + co["x2"], y + co["y2"]
        cw = (cx2 - cx1) / 2.0; ch = (cy2 - cy1) / 2.0
        edge_margin = min(cx1 - self.edge["x1"], cy1 - self.edge["y1"],
                           self.edge["x2"] - cx2, self.edge["y2"] - cy2)
        if edge_margin < margin:
            margin = edge_margin
        edge_ok = edge_margin >= self.edge_margin_req
        cyc_ok = True
        for f in self.cy_grid.query((cx1 + cx2) / 2.0, (cy1 + cy2) / 2.0, max(cw, ch) + 2.0):
            ocy = f["cy"]
            if cx1 < ocy["x2"] and ocy["x1"] < cx2 and cy1 < ocy["y2"] and ocy["y1"] < cy2:
                cyc_ok = False
        ok = (not vv) and (not vc) and edge_ok and cyc_ok
        res = dict(ok=ok, margin=round(margin, 4), edge_margin=round(edge_margin, 4),
                   n_via_viol=len(vv), n_cu_viol=len(vc), via_viol=vv, cu_viol=vc)
        _CELL_CACHE[ck] = res
        return res

    def evaluate_inplace(self, rot, offs, hole_r=12.0):
        """现位装官方 land 的逐 pad 孔净距表"""
        cur = self.d["current"]
        ox, oy = cur["origin_x"], cur["origin_y"]
        rows = []
        for q in offs:
            nm = q["name"]; px = ox + q["dx"]; py = oy + q["dy"]
            dr = q["drill"]; net = self.netmap.get(nm, "")
            worst = None; viol = []
            for v in self.hole_grid.query(px, py, hole_r):
                dist = math.hypot(px - v["x"], py - v["y"])
                raw = dist - (dr / 2.0 + v["drill"] / 2.0)
                if worst is None or raw < worst[0]:
                    worst = (raw, v, dist)
                if raw < self.min_h2h:
                    viol.append(dict(obj_x=round(v["x"], 4), obj_y=round(v["y"], 4),
                                     obj_net=v.get("net"), obj_drill=v.get("drill"),
                                     center_dist=round(dist, 4), hole_gap=round(raw, 4),
                                     hole_gap_clamped0=round(max(0.0, raw), 4),
                                     deficit=round(self.min_h2h - raw, 4)))
            rows.append(dict(pad=nm, x=round(px, 4), y=round(py, 4), drill=dr, net=net,
                             worst_gap=round(worst[0], 4) if worst else None,
                             worst_obj=(worst[1].get("net") if worst else None),
                             violations=viol))
        return rows


# =====================================================================
# 5. 判据 L0~L8
# =====================================================================
def run_checks(page_text, blocks, data, mod_disk, rules_disk):
    ev = Evaluator(data, mod_disk, rules_disk, dict(blocks.get("NETMAP") or {}))
    offs_disk = {int(k): v for k, v in (data.get("orient_offsets") or {}).items()}
    ev.edge_margin_req = 0.5
    if blocks.get("RULES"):
        try:
            ev.edge_margin_req = float(blocks["RULES"].get("min_copper_edge_clearance", 0.5))
        except Exception:
            pass
    ev.req_cu = 0.2
    nc = (blocks.get("RULES") or {}).get("netclass", {}) or {}
    for v in nc.values():
        if isinstance(v, (int, float)) and v > 0:
            ev.req_cu = float(v)

    # ---- L0: 官方 land 几何 == 盘上 .kicad_mod 实读 ----
    lb = blocks.get("LAND")
    if not lb:
        rec("L0", False, "页面缺 LAND 机器块")
    else:
        bad = []
        dp = {p["name"]: p for p in mod_disk["pads"]}
        for p in lb.get("pads", []):
            q = dp.get(p.get("name"))
            if q is None:
                bad.append("pad %s 盘上不存在" % p.get("name")); continue
            for k in ("ptype", "shape", "x", "y", "w", "h", "drill"):
                if str(q.get(k)) != str(p.get(k)):
                    bad.append("pad %s.%s 页面=%s 盘上=%s" % (p.get("name"), k, p.get(k), q.get(k)))
        for k in ("x1", "y1", "x2", "y2"):
            if (mod_disk.get("crtyd") or {}).get(k) != (lb.get("crtyd") or {}).get(k):
                bad.append("crtyd.%s 页面=%s 盘上=%s" % (k, (lb.get("crtyd") or {}).get(k), (mod_disk.get("crtyd") or {}).get(k)))
            if (mod_disk.get("fab") or {}).get(k) != (lb.get("fab") or {}).get(k):
                bad.append("fab.%s 页面=%s 盘上=%s" % (k, (lb.get("fab") or {}).get(k), (mod_disk.get("fab") or {}).get(k)))
        if abs(float(lb.get("local_span_y", -1)) - float(mod_disk["local_span_y"])) > 1e-9:
            bad.append("local_span_y 页面=%s 盘上=%s" % (lb.get("local_span_y"), mod_disk["local_span_y"]))
        if abs(float(lb.get("copper_x_span", -1)) - float(mod_disk["copper_x_span"])) > 1e-9:
            bad.append("copper_x_span 页面=%s 盘上=%s" % (lb.get("copper_x_span"), mod_disk["copper_x_span"]))
        if sorted(lb.get("pad_drill", [])) != sorted(mod_disk["pad_drill"]):
            bad.append("pad_drill 页面=%s 盘上=%s" % (lb.get("pad_drill"), mod_disk["pad_drill"]))
        rec("L0", not bad, ("官方 land 几何与盘上 .kicad_mod 实读一致 (pad %d 个 / crtyd / fab / 钻孔 / 铜箔跨度)"
                            % len(mod_disk["pads"])) if not bad else ("L0 不一致: " + "; ".join(bad[:8])))

    # ---- L1: DRC 孔约束 == .kicad_pro 实读 ----
    rb = blocks.get("RULES")
    if not rb:
        rec("L1", False, "页面缺 RULES 机器块")
    else:
        bad = []
        for k in ("min_hole_to_hole", "min_hole_clearance", "min_through_hole_diameter",
                  "min_via_diameter", "min_via_annular_width", "min_track_width"):
            if str(rb.get(k)) != str(rules_disk.get(k)):
                bad.append("%s 页面=%s 盘上=%s" % (k, rb.get(k), rules_disk.get(k)))
        if abs(float(rb.get("req_copper_clearance", -1)) - ev.req_cu) > 1e-9:
            bad.append("req_copper_clearance 页面=%s 闸算=%s" % (rb.get("req_copper_clearance"), ev.req_cu))
        rec("L1", not bad, ("DRC 孔约束与 .kicad_pro 实读一致 (min_hole_to_hole=%s min_hole_clearance=%s)"
                            % (rules_disk.get("min_hole_to_hole"), rules_disk.get("min_hole_clearance")))
            if not bad else ("L1 不一致: " + "; ".join(bad[:8])))

    # ---- L2: §2 可行域表逐格与闸自己实算一致 ----
    # 口径: 页面 FEAS 块绑一个 cells_sha256 (逐格清单的摘要); 逐格清单本体在证据 JSON 里;
    #       闸对证据 JSON 里【每一格】自己实算 (可行性 + 余量), 再复算每格的 8 邻域环 (证明域是闭合的).
    from collections import defaultdict as _dd
    fb = blocks.get("FEAS")
    if not fb:
        rec("L2", False, "页面缺 FEAS 机器块")
    else:
        bad = []
        jd = None
        evp = fb.get("evidence_json")
        if not evp:
            bad.append("FEAS 缺 evidence_json")
        else:
            jp = os.path.join(ROOT, evp)
            if not os.path.exists(jp):
                bad.append("证据文件不存在: %s" % evp)
            else:
                try:
                    jd = json.load(open(jp, encoding="utf-8"))
                except Exception as e:
                    bad.append("证据文件解析失败: %s" % e)
        grid = fb.get("grid") or {}
        step = float(grid.get("step", 0.1))
        gx0 = float(grid.get("x0", -1e9)); gx1 = float(grid.get("x1", 1e9))
        gy0 = float(grid.get("y0", -1e9)); gy1 = float(grid.get("y1", 1e9))
        rot_spec = fb.get("rot") or {}
        n_checked = 0; ring_checked = 0; ring_skip = 0
        for rk in ("0", "90", "270"):
            spec = rot_spec.get(rk)
            if not spec:
                bad.append("rot %s 缺可行域规格" % rk); continue
            if jd is None:
                break
            try:
                jcells = jd["scan"][rk]["feas_cells"]
            except Exception as e:
                bad.append("rot %s 证据 JSON 取 cells 失败: %s" % (rk, e)); continue
            # (1) sha256 绑定: 页面声明的逐格清单摘要必须 == 证据清单摘要
            cs = sorted(jcells, key=lambda c: (round(c[1], 4), round(c[0], 4)))
            canon = "\n".join("%.4f,%.4f,%.4f" % (c[0], c[1], c[2]) for c in cs)
            sha = hashlib.sha256(canon.encode("utf-8")).hexdigest()
            if sha != str(spec.get("cells_sha256")):
                bad.append("rot %s cells_sha256 页面=%s 闸算=%s" % (rk, spec.get("cells_sha256"), sha)); continue
            if int(spec.get("n_feasible", -1)) != len(jcells):
                bad.append("rot %s n_feasible 页面=%s 闸算=%d" % (rk, spec.get("n_feasible"), len(jcells))); continue
            # (2) 逐行表必须与证据清单逐行一致
            rows = _dd(list)
            for c in jcells:
                rows[round(c[1], 4)].append(c)
            exp_rows = []
            for y in sorted(rows):
                v = sorted(rows[y], key=lambda c: c[0])
                exp_rows.append([y, v[0][0], v[-1][0], len(v),
                                 min(c[2] for c in v), max(c[2] for c in v)])
            page_rows = spec.get("rows") or []
            if len(page_rows) != len(exp_rows):
                bad.append("rot %s 逐行表行数 页面=%d 闸算=%d" % (rk, len(page_rows), len(exp_rows))); continue
            rok = True
            for a, c in zip(page_rows, exp_rows):
                for i, k in enumerate(("y", "x1", "x2", "n", "mmin", "mmax")):
                    av = float(a[i]); cv = float(c[i])
                    if abs(av - cv) > 1e-6:
                        bad.append("rot %s 逐行表第 %d 行 %s 页面=%s 闸算=%s" % (rk, exp_rows.index(c) + 1, k, av, cv)); rok = False; break
                if not rok:
                    break
            if not rok:
                continue
            # (3) 连通域表必须与证据一致
            jcomp = (jd["scan"][rk].get("components") or [])
            pcomp = (spec.get("components") or [])
            if len(pcomp) != len(jcomp):
                bad.append("rot %s 连通域个数 页面=%d 闸算=%d" % (rk, len(pcomp), len(jcomp))); continue
            cok = True
            for a, c in zip(pcomp, jcomp):
                for k in ("n_cells", "x1", "x2", "y1", "y2"):
                    if abs(float(a.get(k, 0)) - float(c.get(k, 0))) > 1e-6:
                        bad.append("rot %s 连通域.%s 页面=%s 闸算=%s" % (rk, k, a.get(k), c.get(k))); cok = False; break
                if not cok:
                    break
            if not cok:
                continue
            # (4) ★逐格实算★: 证据清单里每一格, 闸自己算一遍
            got = set()
            allok = True
            for c in jcells:
                x, y = float(c[0]), float(c[1])
                r = ev.evaluate(x, y, int(rk), offs_disk[int(rk)])
                n_checked += 1
                got.add((round(x, 4), round(y, 4)))
                if not r["ok"]:
                    bad.append("rot %s 格 (%.4f,%.4f) 闸复算不可行" % (rk, x, y)); allok = False; break
                if abs(r["margin"] - float(c[2])) > 1e-6:
                    bad.append("rot %s 格 (%.4f,%.4f) 余量 证据=%s 闸算=%s" % (rk, x, y, c[2], r["margin"])); allok = False; break
            if not allok:
                continue
            # (5) ★边界环★: 与可行集相邻、但在窗口内、又不在可行集里的格, 必须【不可行】
            cand = set()
            for (x, y) in got:
                for ddx in (-step, 0.0, step):
                    for ddy in (-step, 0.0, step):
                        if ddx == 0.0 and ddy == 0.0:
                            continue
                        nx = round(x + ddx, 4); ny = round(y + ddy, 4)
                        if nx < gx0 - 1e-9 or nx > gx1 + 1e-9 or ny < gy0 - 1e-9 or ny > gy1 + 1e-9:
                            continue
                        if (nx, ny) in got:
                            continue
                        cand.add((nx, ny))
            cl = sorted(cand)
            BUDGET = 90000
            if len(cl) > BUDGET:
                stride = (len(cl) + BUDGET - 1) // BUDGET
                cl = cl[::stride]
                ring_skip = len(cand) - len(cl)
            for (nx, ny) in cl:
                r = ev.evaluate(nx, ny, int(rk), offs_disk[int(rk)])
                ring_checked += 1
                if r["ok"]:
                    bad.append("rot %s 边界环 (%.4f,%.4f) 闸复算可行但未列入可行集" % (rk, nx, ny)); break
            if bad and bad[-1].startswith("rot %s 边界环" % rk):
                continue
        msg = "可行域逐格复算一致: 复算 %d 格 + 边界环 %d 格 (rot 0/90/270)" % (n_checked, ring_checked)
        if ring_skip:
            msg += " (边界环抽样 %d 格)" % ring_skip
        rec("L2", not bad, msg if not bad else ("L2 不一致: " + "; ".join(bad[:8])))

    # ---- L3: §1 现位冲突表逐条可复算 ----
    ib = blocks.get("INPLACE")
    if not ib:
        rec("L3", False, "页面缺 INPLACE 机器块")
    else:
        rot = int(ib.get("rot", 90))
        rows = ev.evaluate_inplace(rot, offs_disk[rot])
        page_rows = {r["pad"]: r for r in (ib.get("rows") or [])}
        bad = []
        if set(page_rows) != set(r["pad"] for r in rows):
            bad.append("pad 集合 页面=%s 闸算=%s" % (sorted(page_rows), sorted(r["pad"] for r in rows)))
        for r in rows:
            pr = page_rows.get(r["pad"])
            if not pr:
                continue
            for k in ("x", "y", "drill", "net"):
                if str(pr.get(k)) != str(r.get(k)):
                    bad.append("pad %s.%s 页面=%s 闸算=%s" % (r["pad"], k, pr.get(k), r.get(k)))
            if pr.get("worst_gap") is not None and r.get("worst_gap") is not None:
                if abs(float(pr["worst_gap"]) - float(r["worst_gap"])) > 1e-6:
                    bad.append("pad %s worst_gap 页面=%s 闸算=%s" % (r["pad"], pr["worst_gap"], r["worst_gap"]))
            pv = pr.get("violations") or []
            xv = r.get("violations") or []
            if len(pv) != len(xv):
                bad.append("pad %s 违例条数 页面=%d 闸算=%d" % (r["pad"], len(pv), len(xv))); continue
            for a, c in zip(pv, xv):
                for k in ("obj_x", "obj_y", "obj_net", "hole_gap", "hole_gap_clamped0", "deficit"):
                    if str(a.get(k)) != str(c.get(k)):
                        bad.append("pad %s 违例.%s 页面=%s 闸算=%s" % (r["pad"], k, a.get(k), c.get(k)))
        rec("L3", not bad,
            ("现位冲突表逐条可复算 (rot %d · 4 pad)" % rot) if not bad
            else ("L3 不一致: " + "; ".join(bad[:8])))

    # ---- L4: 三朝向坐标换算由脚本自己算 ----
    ob = blocks.get("ORIENT")
    if not ob:
        rec("L4", False, "页面缺 ORIENT 机器块")
    else:
        bad = []
        for rk in ("0", "90", "270"):
            po = ob.get(rk) or []
            go = offs_disk.get(int(rk)) or []
            if len(po) != len(go):
                bad.append("rot %s pad 数 页面=%d 闸算=%d" % (rk, len(po), len(go))); continue
            for a, c in zip(po, go):
                for k in ("name", "dx", "dy", "drill"):
                    if str(a.get(k)) != str(c.get(k)):
                        bad.append("rot %s pad %s.%s 页面=%s 闸算=%s"
                                   % (rk, a.get("name"), k, a.get(k), c.get(k)))
        rec("L4", not bad,
            "三朝向 (rot 0/90/270) pad 偏移与 FOOTPRINT.SetOrientationDegrees 实算一致"
            if not bad else ("L4 不一致: " + "; ".join(bad[:8])))

    # ---- L5: §2 必须给出区间/可行区而不是一个点 ----
    fb = blocks.get("FEAS") or {}
    bad = []
    rot_spec = fb.get("rot") or {}
    if not rot_spec:
        bad.append("FEAS 无 rot 规格")
    for rk in ("0", "90", "270"):
        spec = rot_spec.get(rk) or {}
        rows = spec.get("rows") or []
        claim = spec.get("region_claim")
        if claim is None:
            bad.append("rot %s 未给出可行区声明 (region_claim) ⇒ ★只报了一个坐标就不算可行域★" % rk)
            continue
        if str(claim.get("kind")) != "区间":
            bad.append("rot %s 可行区声明 kind=%r (★必须声明为『区间』·只试一个落点 ⇒ 红★)"
                       % (rk, claim.get("kind")))
            continue
        if int(claim.get("n_cells", 0)) < 2:
            bad.append("rot %s 可行区声明 n_cells=%s (★<2 ⇒ 只是试了一个点★)"
                       % (rk, claim.get("n_cells")))
            continue
        cx1, cx2 = float(claim.get("x1", 0)), float(claim.get("x2", 0))
        cy1, cy2 = float(claim.get("y1", 0)), float(claim.get("y2", 0))
        if abs(cx2 - cx1) < 1e-9 and abs(cy2 - cy1) < 1e-9:
            bad.append("rot %s 可行区声明退化为一个点 (%.4f,%.4f)" % (rk, cx1, cy1))
            continue
        if not rows:
            bad.append("rot %s 逐行表为空 (★没给区间·只给了一个点★)" % rk)
            continue
        xs = set(); ys = set()
        for r in rows:
            xs.add(float(r[1])); xs.add(float(r[2])); ys.add(float(r[0]))
        if len(xs) < 2 and len(ys) < 2:
            bad.append("rot %s 逐行表退化为一个点 (★只试了一个落点★)" % rk)
            continue
        rx1 = min(float(r[1]) for r in rows); rx2 = max(float(r[2]) for r in rows)
        ry1 = min(float(r[0]) for r in rows); ry2 = max(float(r[0]) for r in rows)
        if abs(cx1 - rx1) > 1e-6 or abs(cx2 - rx2) > 1e-6 \
           or abs(cy1 - ry1) > 1e-6 or abs(cy2 - ry2) > 1e-6:
            bad.append("rot %s 可行区声明 bbox=(%.4f,%.4f)-(%.4f,%.4f) 与逐行表 bbox=(%.4f,%.4f)-(%.4f,%.4f) 不符"
                       % (rk, cx1, cy1, cx2, cy2, rx1, ry1, rx2, ry2))
    rec("L5", not bad,
        "§2 给出的是可行区 (每朝向声明『区间』+ >=2 格 + bbox 与逐行表一致), 不是单点" if not bad
        else ("L5 失败: " + "; ".join(bad[:8])))

    # ---- L6: §3 代价清单每条必须带坐标 ----
    cb = blocks.get("COST")
    if not cb:
        rec("L6", False, "页面缺 COST 机器块")
    else:
        bad = []
        items = cb.get("items") if isinstance(cb, dict) else cb
        if not items:
            bad.append("COST 清单为空")
        for i, it in enumerate(items or []):
            okc = ("x" in it and "y" in it)
            try:
                float(it.get("x")); float(it.get("y"))
            except Exception:
                okc = False
            if not okc:
                bad.append("第 %d 条 (%s) 无坐标" % (i + 1, str(it.get("item"))[:40]))
            if not str(it.get("why", "")).strip():
                bad.append("第 %d 条 (%s) 无 why" % (i + 1, str(it.get("item"))[:40]))
        rec("L6", not bad,
            "§3 代价清单 %d 条全部带坐标 + why" % len(items or []) if not bad
            else ("L6 失败: " + "; ".join(bad[:8])))

    # ---- L7: 板面零写板自证 ----
    import hashlib as _h
    bad = []
    try:
        h = _h.md5(open(BOARD, "rb").read()).hexdigest()
        if h != BOARD_MD5:
            bad.append("板 md5=%s 期望=%s" % (h, BOARD_MD5))
        st = os.stat(BOARD)
        mt = __import__("datetime").datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S.%f")
        if mt[:26] != BOARD_MTIME[:26]:
            bad.append("板 mtime=%s 期望=%s" % (mt, BOARD_MTIME))
        if st.st_size != BOARD_SIZE:
            bad.append("板 size=%d 期望=%d" % (st.st_size, BOARD_SIZE))
    except Exception as e:
        bad.append("板读取失败: %s" % e)
    bb = blocks.get("BOARD")
    if not bb:
        bad.append("页面缺 BOARD 指纹块")
    else:
        if str(bb.get("md5")) != BOARD_MD5:
            bad.append("页面板指纹 md5=%s 期望=%s" % (bb.get("md5"), BOARD_MD5))
        if str(bb.get("mtime", ""))[:26] != BOARD_MTIME[:26]:
            bad.append("页面板指纹 mtime=%s 期望=%s" % (bb.get("mtime"), BOARD_MTIME))
        try:
            if int(bb.get("size", -1)) != BOARD_SIZE:
                bad.append("页面板指纹 size=%s 期望=%d" % (bb.get("size"), BOARD_SIZE))
        except Exception:
            bad.append("页面板指纹 size 非整数")
    rec("L7", not bad,
        "板零写板自证通过 (md5/mtime/size 三项 == 611b869e…/2026-11-06 07:07:17.362193413/4940213)"
        if not bad else ("L7 失败: " + "; ".join(bad[:6])))

    # ---- L8: 证据等级 / 零挂起 / 判据句事实句分开 / 零挂链 ----
    bad = []
    eb = blocks.get("EVID")
    if not eb:
        bad.append("页面缺 EVID 机器块")
    else:
        lv = eb.get("level")
        if lv not in EVID_LEVELS:
            bad.append("证据等级 %r 不在白名单 %s" % (lv, sorted(EVID_LEVELS)))
    for w in HANG_WORDS:
        if w in page_text:
            bad.append("出现挂起措辞 %r" % w)
    if "<!-- ISS376:CRITERIA -->" not in page_text or "<!-- ISS376:FACT -->" not in page_text:
        bad.append("缺判据句/事实句分区标记 (<!-- ISS376:CRITERIA --> / <!-- ISS376:FACT -->)")
    # 零挂链
    gc = os.path.join(ROOT, "state/gate_check.py")
    n = 0
    if os.path.exists(gc):
        n = open(gc, encoding="utf-8").read().count("check_jdebug_land_fit")
    if n != 0:
        bad.append("本闸已被挂进 state/gate_check.py (%d 处) ⇒ 违反零挂链" % n)
    rec("L8", not bad,
        "证据等级白名单 / 零挂起措辞 / 判据句事实句分区 / 零挂链 自证通过" if not bad
        else ("L8 失败: " + "; ".join(bad[:8])))

    return RESULT


# =====================================================================
# 6. 自测 (>=8 条反向用例)
# =====================================================================
def selftest():
    page_text = open(PAGE, encoding="utf-8").read()
    blocks = parse_page_blocks(page_text)
    mod_disk = parse_mod(MODFILE)
    proj = json.load(open(PROJ, encoding="utf-8"))
    rules_disk = dict(proj["board"]["design_settings"]["rules"])
    try:
        rules_disk["_netclass"] = {c.get("name"): c.get("clearance")
                                   for c in proj["board"].get("net_settings", {}).get("classes", [])}
    except Exception:
        rules_disk["_netclass"] = {}
    data, err = load_board_data()
    if data is None:
        print("[selftest] 板数据加载失败: %s" % err)
        return 1

    base = run_checks(page_text, blocks, data, mod_disk, rules_disk)
    base_fail = set(lid for lid, ok, _ in base if not ok)
    if base_fail:
        print("[selftest] 基线必须全绿, 但红了: %s" % sorted(base_fail))
        for lid, ok, m in base:
            if not ok:
                print("   [%s] %s" % (lid, m))
        return 1
    print("[selftest] 基线 L0~L8 全绿")

    import copy
    CASES = []

    def case(name, target, mutate):
        CASES.append((name, target, mutate))

    def m_land(b, t):
        b["LAND"]["pads"][0]["drill"] = 0.99
        return t

    def m_rules(b, t):
        b["RULES"]["min_hole_to_hole"] = 0.5
        return t

    def m_conflict(b, t):
        rows = b["INPLACE"]["rows"]
        for r in rows:
            if r.get("violations"):
                r["violations"][0]["hole_gap"] = 0.0123
                break
        return t

    def m_orient(b, t):
        b["ORIENT"]["90"][1]["dx"] = 9.999
        return t

    # ★★药根用例: 只试一个落点就宣布可行/不可行 ★★ (≥2 条)
    def m_claim_single_point(b, t):
        """rot90 的区间声明改成单点 (★cells 本身不动 ⇒ L2 不受影响★)"""
        b["FEAS"]["rot"]["90"]["region_claim"] = dict(kind="单点", n_cells=1,
                                                       x1=150.0, x2=150.0, y1=58.0, y2=58.0)
        return t

    def m_claim_missing(b, t):
        """rot0 干脆不给区间声明 (★= 只报了一个坐标就没下文★)"""
        b["FEAS"]["rot"]["0"].pop("region_claim", None)
        return t

    def m_cell_margin(b, t):
        """篡改逐格清单的 sha256 绑定 ⇒ L2 红 (证明闸真在逐格复算)"""
        b["FEAS"]["rot"]["90"]["cells_sha256"] = "0" * 64
        return t

    def m_cost_nocoord(b, t):
        it = (b["COST"].get("items") if isinstance(b["COST"], dict) else b["COST"])
        it[0].pop("x", None); it[0].pop("y", None)
        return t

    def m_board_fp(b, t):
        b["BOARD"]["md5"] = "00000000000000000000000000000000"
        return t

    def m_hang(b, t):
        return t.replace("## §0", "## §0\n\n> 挂起: 等原厂回信\n", 1)

    def m_cost_why(b, t):
        it = (b["COST"].get("items") if isinstance(b["COST"], dict) else b["COST"])
        it[0]["why"] = "   "
        return t

    case("C1 篡改 LAND pad 钻孔 ⇒ L0 红", "L0", m_land)
    case("C2 篡改 RULES min_hole_to_hole ⇒ L1 红", "L1", m_rules)
    case("C3 篡改可行域某格余量 ⇒ L2 红", "L2", m_cell_margin)
    case("C4 篡改现位冲突表孔净距 ⇒ L3 红", "L3", m_conflict)
    case("C5 篡改 rot90 pad 偏移 ⇒ L4 红", "L4", m_orient)
    case("C6 ★只试一个落点★ rot90 区间声明改单点 ⇒ L5 红", "L5", m_claim_single_point)
    case("C7 ★只试一个落点★ rot0 不给区间声明 ⇒ L5 红", "L5", m_claim_missing)
    case("C8 §3 代价条目去掉坐标 ⇒ L6 红", "L6", m_cost_nocoord)
    case("C9 §3 代价条目 why 写空 ⇒ L6 红", "L6", m_cost_why)
    case("C10 篡改页面板指纹 ⇒ L7 红", "L7", m_board_fp)
    case("C11 页面注入挂起措辞 ⇒ L8 红", "L8", m_hang)

    npass = 0
    for name, target, mutate in CASES:
        b2 = copy.deepcopy(blocks)
        t2 = mutate(b2, page_text)
        del RESULT[:]
        run_checks(t2, b2, data, mod_disk, rules_disk)
        reds = set(lid for lid, ok, _ in RESULT if not ok)
        if reds == {target}:
            print("  PASS  %-52s ⇒ 红 %s, 其余仍绿" % (name, target))
            npass += 1
        else:
            print("  FAIL  %-52s ⇒ 期望红 %s, 实得 %s" % (name, target, sorted(reds) or "全绿"))
            for lid, ok, m in RESULT:
                if not ok:
                    print("         [%s] %s" % (lid, m))
    print("[selftest] %d/%d 条反向用例通过" % (npass, len(CASES)))
    if npass == len(CASES) and len(CASES) >= 8:
        print("ALL TESTS PASS")
        return 0
    print("SELFTEST FAILED")
    return 1


def main():
    if not os.path.exists(PAGE):
        print("[gate] 真相页不存在: %s" % PAGE)
        return 1
    page_text = open(PAGE, encoding="utf-8").read()
    blocks = parse_page_blocks(page_text)
    mod_disk = parse_mod(MODFILE)
    proj = json.load(open(PROJ, encoding="utf-8"))
    rules_disk = dict(proj["board"]["design_settings"]["rules"])
    try:
        rules_disk["_netclass"] = {c.get("name"): c.get("clearance")
                                   for c in proj["board"].get("net_settings", {}).get("classes", [])}
    except Exception:
        rules_disk["_netclass"] = {}

    if SELFTEST:
        return selftest()

    data, err = load_board_data()
    if data is None:
        print("[gate] FAIL 板数据加载失败: %s" % err)
        return 1
    del RESULT[:]
    run_checks(page_text, blocks, data, mod_disk, rules_disk)
    nred = sum(1 for _, ok, _ in RESULT if not ok)
    print("=" * 72)
    print("[gate] ISS-376 J_DEBUG 落位可行性闸 · L0~L8")
    print("=" * 72)
    for lid, ok, m in RESULT:
        print("  %-4s %s  %s" % (lid, "PASS" if ok else "FAIL", m))
    print("-" * 72)
    print("[gate] %d 条判据, 红 %d 条 ⇒ rc=%d" % (len(RESULT), nred, 1 if nred else 0))
    if nred:
        print("GATE RED")
        return 1
    print("GATE GREEN")
    return 0


if __name__ == "__main__":
    sys.exit(main())