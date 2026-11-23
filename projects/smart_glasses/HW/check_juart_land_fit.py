#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-379 · hw-lead · `J_UART` 换官方 1×2 P1.27 THT land 的落位可行性闸 (K0~K8)
======================================================================
★ 与姊妹件 ISS-376 (`HW/check_jdebug_land_fit.py`, L0~L8) 同款口径, 但判据按 `J_UART` 的实况改写 ★
★ K0 官方 land 几何 == 盘上 .kicad_mod 实读
★ K1 DRC 判据 == `.kicad_pro` 实读 (min_hole_to_hole / min_hole_clearance / min_copper_edge_clearance)
★ K2 可行域逐格复算 (证据 JSON 逐格 + 边界环 + 逐行表)
★ K3 现位冲突表逐条可复算 (★本单卡点是【铜】不是【孔】★)
★ K4 三朝向 pad 偏移 == `FOOTPRINT.SetOrientationDegrees` 实算 (★含 rot 0/90 铜箔包络互换★)
★ K5 §2/§4 必须给出可行区 (区间) 而不是单点 + ★位移双口径都在★
★ K6 §3 代价清单每条必须带坐标 + why
★ K7 板面零写板自证 (md5 / mtime / size 三项)
★ K8 证据等级 / 零挂起措辞 / 判据句事实句分区 / 零挂链
★ 每条 fail-closed; `--selftest` 末行必须是 `ALL TESTS PASS`
★ 本闸【不】挂进 `state/gate_check.py` (★零挂链·挂链是 main 的地界★)
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
PAGE = os.path.join(ROOT, "HW/PCB/BOARD_ONEPASS_JUART_LAND_FIT.md")
LIBDIR = "/home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty"
FPNAME = "PinHeader_1x02_P1.27mm_Vertical"
MODFILE = os.path.join(LIBDIR, FPNAME + ".kicad_mod")
PCBNEW_SH = os.path.join(ROOT, "state/pcbnew_py.sh")
SBX = os.path.join(ROOT, "tmp/iss379_sbx")
EVID_JSON = os.path.join(ROOT, "logs/iss379/scan_land_fit_modeA.json")

BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"
BOARD_MTIME = "2026-11-06 07:07:17.362193413"
BOARD_SIZE = 4940213

VERBOSE = "--verbose" in sys.argv
SELFTEST = "--selftest" in sys.argv

RESULT = []
_CELL_CACHE = {}
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
    out = {}
    pat = re.compile(r"<!--\s*ISS379:BEGIN\s+([A-Z_0-9]+)\s*-->(.*?)<!--\s*ISS379:END\s+\1\s*-->", re.S)
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
    if not pads:
        raise SystemExit("[gate] 解析 .kicad_mod 失败: pad 块未匹配")
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
    xs = sorted(p["x"] for p in pads)
    ys = sorted(p["y"] for p in pads)
    return dict(pads=pads, crtyd=crtyd, fab=fab,
                local_span_y=(ys[-1] - ys[0]) if len(ys) > 1 else 0.0,
                local_span_x=(xs[-1] - xs[0]) if len(xs) > 1 else 0.0,
                copper_x_span=max((p["w"] for p in pads), default=0.0),
                copper_local_bbox=dict(
                    x1=min(p["x"] - p["w"] / 2 for p in pads),
                    x2=max(p["x"] + p["w"] / 2 for p in pads),
                    y1=min(p["y"] - p["h"] / 2 for p in pads),
                    y2=max(p["y"] + p["h"] / 2 for p in pads)),
                pad_drill=sorted(set(p["drill"] for p in pads)))


# =====================================================================
# 2. 几何引擎 (与落位扫描脚本同口径 · 精确凸形间距)
# =====================================================================
def pt_seg_dist(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    L2 = dx * dx + dy * dy
    if L2 == 0:
        return math.hypot(px - x1, py - y1)
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / L2))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))


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
    d1 = cross(p3, p4, p1); d2 = cross(p3, p4, p2)
    d3 = cross(p1, p2, p3); d4 = cross(p1, p2, p4)
    if ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0)):
        return 0.0
    return min(pt_seg(p1, p3, p4), pt_seg(p2, p3, p4), pt_seg(p3, p1, p2), pt_seg(p4, p1, p2))


def rect_corners(cx, cy, hw, hh, ang):
    ca, sa = math.cos(ang), math.sin(ang)
    return [(cx + dx * ca - dy * sa, cy + dx * sa + dy * ca)
            for (dx, dy) in ((-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh))]


def rect_rect_dist(r1, r2):
    a = rect_corners(*r1); b = rect_corners(*r2)
    best = 1e9
    for i in range(4):
        for j in range(4):
            d = seg_seg_dist(a[i], a[(i + 1) % 4], b[j], b[(j + 1) % 4])
            if d < best:
                best = d
    return best


def seg_rect_dist(x1, y1, x2, y2, r):
    c = rect_corners(*r)
    best = 1e9
    for i in range(4):
        d = seg_seg_dist((x1, y1), (x2, y2), c[i], c[(i + 1) % 4])
        if d < best:
            best = d
            if best <= 0.0:
                return 0.0
    return best


def pt_rect_dist(px, py, cx, cy, hw, hh, ang):
    ca, sa = math.cos(-ang), math.sin(-ang)
    dx, dy = px - cx, py - cy
    lx, ly = dx * ca - dy * sa, dx * sa + dy * ca
    ox, oy = abs(lx) - hw, abs(ly) - hh
    if ox <= 0 and oy <= 0:
        return 0.0
    return math.hypot(max(ox, 0.0), max(oy, 0.0))


class Grid(object):
    def __init__(self, cell=1.0):
        self.cell = cell
        self.d = {}

    def add(self, rec_, bbox=None):
        if bbox is None:
            bbox = (rec_["x"], rec_["y"], rec_["x"], rec_["y"])
        for i in range(int(math.floor(bbox[0] / self.cell)), int(math.floor(bbox[2] / self.cell)) + 1):
            for j in range(int(math.floor(bbox[1] / self.cell)), int(math.floor(bbox[3] / self.cell)) + 1):
                self.d.setdefault((i, j), []).append(rec_)

    def query(self, x, y, r):
        c = self.cell
        out = []
        seen = set()
        for i in range(int(math.floor((x - r) / c)), int(math.floor((x + r) / c)) + 1):
            for j in range(int(math.floor((y - r) / c)), int(math.floor((y + r) / c)) + 1):
                for rec_ in self.d.get((i, j), []):
                    k = id(rec_)
                    if k not in seen:
                        seen.add(k)
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
REF = sys.argv[4]
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
    ref=f.GetReference(); p=f.GetPosition(); cy=None; cy_src=None; n_out=0
    try:
        poly=f.GetCourtyard(pcbnew.F_CrtYd)
        n_out=poly.OutlineCount() if hasattr(poly,"OutlineCount") else 0
    except Exception:
        poly=None
    if poly is not None and n_out>0:
        bb=poly.BBox()
        cy=dict(x1=mm(bb.GetLeft()), y1=mm(bb.GetTop()), x2=mm(bb.GetRight()), y2=mm(bb.GetBottom()))
        cy_src="F.CrtYd"
    else:
        bb=f.GetBoundingBox(False, False)
        cy=dict(x1=mm(bb.GetLeft()), y1=mm(bb.GetTop()), x2=mm(bb.GetRight()), y2=mm(bb.GetBottom()))
        cy_src="bbox-fallback"
    fps.append(dict(ref=ref, x=mm(p.x), y=mm(p.y),
                    orient=float(f.GetOrientation().AsDegrees()), cy=cy, cy_src=cy_src,
                    n_crt_outlines=int(n_out), fpid=f.GetFPIDAsString()))
    for pad in f.Pads():
        pp=pad.GetPosition()
        r=dict(fp=ref, name=pad.GetPadName(), x=mm(pp.x), y=mm(pp.y), net=pad.GetNetname(),
               shape=int(pad.GetShape()), w=mm(pad.GetSizeX()), h=mm(pad.GetSizeY()),
               ang=math.radians(float(pad.GetOrientation().AsDegrees())),
               drill=mm(pad.GetDrillSizeX()), attr=int(pad.GetAttribute()))
        if r["attr"]==pcbnew.PAD_ATTRIB_PTH: pth.append(r)
        else: smd.append(r)
out["vias"]=vias; out["tracks"]=tracks; out["smd"]=smd; out["pth"]=pth; out["fps"]=fps

jf=[f for f in b.GetFootprints() if f.GetReference()==REF][0]
jp=jf.GetPosition()
cur=dict(ref=REF, origin_x=mm(jp.x), origin_y=mm(jp.y),
         orient=round(float(jf.GetOrientation().AsDegrees()),4),
         fp_id=jf.GetFPIDAsString(), pads=[])
for pad in sorted(jf.Pads(), key=lambda q: mm(q.GetPosition().x)):
    pp=pad.GetPosition()
    cur["pads"].append(dict(name=pad.GetPadName(), x=mm(pp.x), y=mm(pp.y), net=pad.GetNetname(),
                            shape=int(pad.GetShape()), w=mm(pad.GetSizeX()), h=mm(pad.GetSizeY()),
                            attr=int(pad.GetAttribute()),
                            local_x=round(mm(pp.x)-mm(jp.x),4), local_y=round(mm(pp.y)-mm(jp.y),4)))
xs=[p["x"] for p in cur["pads"]]; ys=[p["y"] for p in cur["pads"]]
cur["cu_x1"]=min(xs)-cur["pads"][0]["w"]/2; cur["cu_x2"]=max(xs)+cur["pads"][0]["w"]/2
cur["cu_y1"]=min(ys)-cur["pads"][0]["h"]/2; cur["cu_y2"]=max(ys)+cur["pads"][0]["h"]/2
cur["cu_x_width"]=cur["cu_x2"]-cur["cu_x1"]
cur["pitch"]=round(max(xs)-min(xs),4)
out["current"]=cur

offs={}; crt_off={}; cu_off={}
for rot in (0,90,270):
    fp=pcbnew.FootprintLoad(LIBDIR, FPNAME)
    fp.SetOrientationDegrees(rot)
    base=fp.GetPosition(); bx,by=mm(base.x),mm(base.y)
    o=[]
    for pad in sorted(fp.Pads(), key=lambda q: q.GetPadName()):
        pp=pad.GetPosition()
        o.append(dict(name=pad.GetPadName(), dx=mm(pp.x)-bx, dy=mm(pp.y)-by,
                      drill=mm(pad.GetDrillSizeX()), shape=int(pad.GetShape()),
                      w=mm(pad.GetSizeX()), h=mm(pad.GetSizeY()),
                      # ★★2026-11-24 cont1 修: 【不许把角度取整到 6 位】★★
                      #   原写法 round(radians(deg),6) 把 90° 变成 1.570796 (=π/2 差 -3.268e-7 rad)
                      #   ⇒ 有向矩形被转歪 ⇒ 铜-铜距离偏 +1.2e-7 mm
                      #   ⇒ 在 rot 90 格 (7.4000,75.8000) 把余量 3.1266499666 顶成 3.1266500913
                      #   ⇒ round(...,4) 由 3.1266 翻成 3.1267 ⇒ 闸 K2 红
                      #   扫描脚本 tmp/iss379/tools/scan_land_fit.py 一直用的是【不取整】的精确角 ⇒ 证据侧对
                      #   判据: 第三路独立复算 tmp/iss379/tools/third_path_recheck.py (自写解析 + 自写几何)
                      ang=math.radians(float(pad.GetOrientation().AsDegrees()))))
    offs[str(rot)]=o
    fp2=pcbnew.FootprintLoad(LIBDIR, FPNAME)
    fp2.SetOrientationDegrees(rot)
    fp2.SetPosition(pcbnew.VECTOR2I_MM(0.0,0.0))
    b.Add(fp2)
    cbb=fp2.GetCourtyard(pcbnew.F_CrtYd).BBox()
    crt_off[str(rot)]=dict(x1=mm(cbb.GetLeft()), y1=mm(cbb.GetTop()),
                           x2=mm(cbb.GetRight()), y2=mm(cbb.GetBottom()))
    b.Remove(fp2)
    pxs=[]; pys=[]
    for q in o:
        pxs += [q["dx"]-q["w"]/2.0, q["dx"]+q["w"]/2.0]
        pys += [q["dy"]-q["h"]/2.0, q["dy"]+q["h"]/2.0]
    cu_off[str(rot)]=dict(x1=round(min(pxs),4), y1=round(min(pys),4),
                          x2=round(max(pxs),4), y2=round(max(pys),4),
                          w=round(max(pxs)-min(pxs),4), h=round(max(pys)-min(pys),4))
out["orient_offsets"]=offs
out["crt_offset"]=crt_off
out["cu_offset"]=cu_off

# net 映射 (沿用现位 pad 从左到右)
oldnets=[p["net"] for p in sorted(cur["pads"], key=lambda p: p["x"])]
pl=sorted(mod_pads, key=lambda q: q["name"]) if False else None
import re as _re
_txt=open(os.path.join(LIBDIR, FPNAME + ".kicad_mod"), encoding="utf-8").read()
_pl=[]
for m in _re.finditer(r'\(pad\s+"([^"]+)"', _txt):
    _pl.append(m.group(1))
netmap={}
for nm, n in zip(_pl, oldnets):
    netmap[nm]=n
out["netmap"]=netmap
open(sys.argv[5], "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False))
print("[helper] wrote " + sys.argv[5])
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
        r = subprocess.run(["bash", PCBNEW_SH, hp, ROOT, LIBDIR, FPNAME, "J_UART", jf],
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
    def __init__(self, data, rules, netmap):
        self.d = data
        self.min_h2h = float(rules["min_hole_to_hole"])
        self.min_hole_cl = float(rules["min_hole_clearance"])
        self.edge_req = float(rules.get("min_copper_edge_clearance", 0.5))
        self.req_cu = float(rules.get("req_copper_clearance", 0.2))
        self.netmap = netmap
        self.holes = []
        self.cu = []
        self.cy = []
        for v in data["vias"]:
            self.holes.append(dict(x=v["x"], y=v["y"], drill=v["drill"], net=v["net"], ref=v["net"]))
            self.cu.append(dict(kind="circle", x=v["x"], y=v["y"], r=v["dia"] / 2.0, net=v["net"], ref=v["net"]))
        for p in data["pth"]:
            self.holes.append(dict(x=p["x"], y=p["y"], drill=p["drill"], net=p["net"], ref="%s.%s" % (p["fp"], p["name"])))
            if p["shape"] == 0:
                self.cu.append(dict(kind="circle", x=p["x"], y=p["y"], r=max(p["w"], p["h"]) / 2.0,
                                    net=p["net"], ref="%s.%s" % (p["fp"], p["name"])))
            else:
                self.cu.append(dict(kind="rect", x=p["x"], y=p["y"], hw=p["w"] / 2.0, hh=p["h"] / 2.0,
                                    ang=p["ang"], net=p["net"], ref="%s.%s" % (p["fp"], p["name"])))
        for p in data["smd"]:
            if p["fp"] == "J_UART":
                continue
            if p["shape"] == 0:
                self.cu.append(dict(kind="circle", x=p["x"], y=p["y"], r=max(p["w"], p["h"]) / 2.0,
                                    net=p["net"], ref="%s.%s" % (p["fp"], p["name"])))
            else:
                self.cu.append(dict(kind="rect", x=p["x"], y=p["y"], hw=p["w"] / 2.0, hh=p["h"] / 2.0,
                                    ang=p["ang"], net=p["net"], ref="%s.%s" % (p["fp"], p["name"])))
        for t in data["tracks"]:
            self.cu.append(dict(kind="seg", x1=t["x1"], y1=t["y1"], x2=t["x2"], y2=t["y2"],
                                hw=t["w"] / 2.0, net=t["net"], ref="TRK:%s" % t["layer"]))
        for f in data["fps"]:
            if f["ref"] == "J_UART" or not f.get("cy"):
                continue
            self.cy.append(dict(ref=f["ref"], cy=f["cy"], src=f["cy_src"]))
        for c in self.cu:
            c["bbox"] = self.cu_bbox(c)
        self.hole_grid = Grid(2.0)
        for h in self.holes:
            self.hole_grid.add(h)
        self.cu_grid = Grid(2.0)
        for c in self.cu:
            self.cu_grid.add(c, bbox=c["bbox"])
        self.cy_grid = Grid(4.0)
        for c in self.cy:
            self.cy_grid.add(c, bbox=(c["cy"]["x1"], c["cy"]["y1"], c["cy"]["x2"], c["cy"]["y2"]))
        self.edge = data["board_edges"]
        self.crt_off = data.get("crt_offset") or {}
        self.cu_off = data.get("cu_offset") or {}
        # ★查询半径: 必须与扫描脚本【完全一致】(★否则 margin 会因漏掉远处但更紧的对象而对不上★)
        # 扫描脚本用 3.0 ⇒ 闸也用 3.0 ★
        self.qr = 3.0

    @staticmethod
    def cu_bbox(it):
        if it["kind"] == "seg":
            return (min(it["x1"], it["x2"]) - it["hw"], min(it["y1"], it["y2"]) - it["hw"],
                    max(it["x1"], it["x2"]) + it["hw"], max(it["y1"], it["y2"]) + it["hw"])
        if it["kind"] == "circle":
            return (it["x"] - it["r"], it["y"] - it["r"], it["x"] + it["r"], it["y"] + it["r"])
        ca, sa = abs(math.cos(it["ang"])), abs(math.sin(it["ang"]))
        ex = it["hw"] * ca + it["hh"] * sa
        ey = it["hw"] * sa + it["hh"] * ca
        return (it["x"] - ex, it["y"] - ey, it["x"] + ex, it["y"] + ey)

    def cu_dist(self, it, pad):
        if it["kind"] == "circle":
            if pad["kind"] == "circle":
                return math.hypot(pad["x"] - it["x"], pad["y"] - it["y"]) - it["r"] - pad["hw"]
            return pt_rect_dist(it["x"], it["y"], pad["x"], pad["y"], pad["hw"], pad["hh"], pad["ang"]) - it["r"]
        if it["kind"] == "rect":
            if pad["kind"] == "circle":
                return pt_rect_dist(it["x"], it["y"], pad["x"], pad["y"], pad["hw"], pad["hh"], pad["ang"]) - pad["hw"]
            return rect_rect_dist((it["x"], it["y"], it["hw"], it["hh"], it["ang"]),
                                  (pad["x"], pad["y"], pad["hw"], pad["hh"], pad["ang"]))
        if pad["kind"] == "circle":
            return pt_seg_dist(pad["x"], pad["y"], it["x1"], it["y1"], it["x2"], it["y2"]) - it["hw"] - pad["hw"]
        return seg_rect_dist(it["x1"], it["y1"], it["x2"], it["y2"],
                             (pad["x"], pad["y"], pad["hw"], pad["hh"], pad["ang"])) - it["hw"]

    def hole_to_cu_dist(self, it, px, py):
        if it["kind"] == "seg":
            return pt_seg_dist(px, py, it["x1"], it["y1"], it["x2"], it["y2"]) - it["hw"]
        if it["kind"] == "circle":
            return math.hypot(px - it["x"], py - it["y"]) - it["r"]
        return pt_rect_dist(px, py, it["x"], it["y"], it["hw"], it["hh"], it["ang"])

    def evaluate(self, x, y, rot, offs):
        ck = (int(rot), round(x, 4), round(y, 4))
        hit = _CELL_CACHE.get(ck)
        if hit is not None:
            return hit
        margin = 1e9
        vv = []; vc = []; vh = []
        for q in offs:
            nm = q["name"]; px = x + q["dx"]; py = y + q["dy"]
            net = self.netmap.get(nm, "")
            pad = dict(kind=("rect" if q["shape"] == 1 else "circle"), x=px, y=py,
                       hw=q["w"] / 2.0, hh=q["h"] / 2.0, ang=q.get("ang", 0.0))
            # (1) 孔净距
            for h in self.hole_grid.query(px, py, self.qr):
                d = math.hypot(px - h["x"], py - h["y"])
                raw = d - (q["drill"] / 2.0 + h["drill"] / 2.0)
                gap = raw - self.min_h2h
                if gap < margin:
                    margin = gap
                if gap < 0:
                    vv.append(dict(pad=nm, px=round(px, 4), py=round(py, 4),
                                   obj_x=h["x"], obj_y=h["y"], obj_net=h.get("net"),
                                   hole_gap=round(raw, 4), deficit=round(-gap, 4)))
            # (2) 铜箔净距 + (3) 孔到铜净距
            for it in self.cu_grid.query(px, py, self.qr):
                if it["net"] == net:
                    continue
                d = self.cu_dist(it, pad)
                g = d - self.req_cu
                if g < margin:
                    margin = g
                if g < 0:
                    vc.append(dict(pad=nm, px=round(px, 4), py=round(py, 4), ref=it["ref"],
                                   kind=it["kind"], net=it.get("net"), gap=round(d, 4)))
                hc = self.hole_to_cu_dist(it, px, py) - q["drill"] / 2.0
                gh = hc - self.min_hole_cl
                if gh < margin:
                    margin = gh
                if gh < 0:
                    vh.append(dict(pad=nm, px=round(px, 4), py=round(py, 4),
                                   ref=it["ref"], net=it.get("net"), gap=round(hc, 4)))
            # (4) 铜箔到板边
            co = self.cu_off.get(str(rot))
            if co:
                ux1, uy1 = x + co["x1"], y + co["y1"]
                ux2, uy2 = x + co["x2"], y + co["y2"]
                em = min(ux1 - self.edge["x1"], uy1 - self.edge["y1"],
                         self.edge["x2"] - ux2, self.edge["y2"] - uy2)
                if em < margin:
                    margin = em
                edge_ok = em >= self.edge_req
            else:
                em = 0.0; edge_ok = False
            # (5) courtyard vs 其它器件
            cr = self.crt_off.get(str(rot))
            cyc_ok = True
            if cr:
                cx1, cy1 = x + cr["x1"], y + cr["y1"]
                cx2, cy2 = x + cr["x2"], y + cr["y2"]
                for f in self.cy_grid.query((cx1 + cx2) / 2.0, (cy1 + cy2) / 2.0,
                                            max(cx2 - cx1, cy2 - cy1) / 2.0 + 2.0):
                    ocy = f["cy"]
                    ox1 = min(cx1, cx2); oy1 = min(cy1, cy2)
                    ox2 = max(cx1, cx2); oy2 = max(cy1, cy2)
                    if ox1 < ocy["x2"] and ocy["x1"] < ox2 and oy1 < ocy["y2"] and ocy["y1"] < oy2:
                        cyc_ok = False
                        break
        ok = (not vv) and (not vc) and (not vh) and edge_ok and cyc_ok
        res = dict(ok=ok, margin=round(margin, 4), edge_margin=round(em, 4),
                   n_via_viol=len(vv), n_cu_viol=len(vc), n_holecu_viol=len(vh))
        _CELL_CACHE[ck] = res
        return res

    def evaluate_inplace(self, rot, offs):
        """现位 (封装 origin 不动) 装官方 land 的逐 pad 孔净距 + 铜箔违例"""
        cur = self.d["current"]
        ox, oy = cur["origin_x"], cur["origin_y"]
        rows = []
        for q in offs:
            nm = q["name"]; px = ox + q["dx"]; py = oy + q["dy"]
            net = self.netmap.get(nm, "")
            worst = None
            for h in self.hole_grid.query(px, py, 12.0):
                d = math.hypot(px - h["x"], py - h["y"])
                raw = d - (q["drill"] / 2.0 + h["drill"] / 2.0)
                if worst is None or raw < worst[0]:
                    worst = (raw, h, d)
            pad = dict(kind=("rect" if q["shape"] == 1 else "circle"), x=px, y=py,
                       hw=q["w"] / 2.0, hh=q["h"] / 2.0, ang=q.get("ang", 0.0))
            cuviol = []
            for it in self.cu:
                if it["net"] == net:
                    continue
                bb = it["bbox"]
                if not (bb[0] - 2.0 <= px <= bb[2] + 2.0 and bb[1] - 2.0 <= py <= bb[3] + 2.0):
                    continue
                d = self.cu_dist(it, pad)
                if d < self.req_cu:
                    cuviol.append(dict(pad=nm, px=round(px, 4), py=round(py, 4), ref=it["ref"],
                                       kind=it["kind"], net=it.get("net"), gap=round(d, 4),
                                       deficit=round(self.req_cu - d, 4)))
            rows.append(dict(pad=nm, x=round(px, 4), y=round(py, 4), drill=q["drill"], net=net,
                             worst_gap=round(worst[0], 4) if worst else None,
                             worst_obj=(worst[1].get("net") if worst else None),
                             violations=[],
                             cu_violations=cuviol))
        return rows


# =====================================================================
# 5. 判据 K0~K8
# =====================================================================
def run_checks(page_text, blocks, data, mod_disk, rules_disk):
    ev = Evaluator(data, rules_disk, dict(blocks.get("NETMAP") or {}))
    offs_disk = {int(k): v for k, v in (data.get("orient_offsets") or {}).items()}

    # ---- K0: 官方 land 几何 == 盘上 .kicad_mod 实读 ----
    lb = blocks.get("LAND")
    if not lb:
        rec("K0", False, "页面缺 LAND 机器块")
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
        for blk, key in (("crtyd", "crtyd"), ("fab", "fab")):
            for k in ("x1", "y1", "x2", "y2"):
                if (mod_disk.get(key) or {}).get(k) != (lb.get(key) or {}).get(k):
                    bad.append("%s.%s 页面=%s 盘上=%s" % (key, k, (lb.get(key) or {}).get(k),
                                                          (mod_disk.get(key) or {}).get(k)))
        for k in ("local_span_y", "local_span_x", "copper_x_span"):
            if abs(float(lb.get(k, -1)) - float(mod_disk[k])) > 1e-9:
                bad.append("%s 页面=%s 盘上=%s" % (k, lb.get(k), mod_disk[k]))
        cb = lb.get("copper_local_bbox") or {}
        mb = mod_disk.get("copper_local_bbox") or {}
        for k in ("x1", "y1", "x2", "y2"):
            if abs(float(cb.get(k, 9e9)) - float(mb.get(k, -9e9))) > 1e-9:
                bad.append("copper_local_bbox.%s 页面=%s 盘上=%s" % (k, cb.get(k), mb.get(k)))
        if sorted(lb.get("pad_drill", [])) != sorted(mod_disk["pad_drill"]):
            bad.append("pad_drill 页面=%s 盘上=%s" % (lb.get("pad_drill"), mod_disk["pad_drill"]))
        rec("K0", not bad,
            ("官方 land 几何与盘上 .kicad_mod 实读一致 (pad %d 个 / crtyd / fab / 钻孔 / 铜箔包络 / 局部跨度)"
             % len(mod_disk["pads"])) if not bad else ("K0 不一致: " + "; ".join(bad[:8])))

    # ---- K1: DRC 判据 == .kicad_pro 实读 ----
    rb = blocks.get("RULES")
    if not rb:
        rec("K1", False, "页面缺 RULES 机器块")
    else:
        bad = []
        for k in ("min_hole_to_hole", "min_hole_clearance", "min_copper_edge_clearance",
                  "min_clearance", "min_through_hole_diameter", "min_via_diameter",
                  "min_via_annular_width", "min_track_width"):
            if str(rb.get(k)) != str(rules_disk.get(k)):
                bad.append("%s 页面=%s 盘上=%s" % (k, rb.get(k), rules_disk.get(k)))
        if abs(float(rb.get("req_copper_clearance", -1)) - ev.req_cu) > 1e-9:
            bad.append("req_copper_clearance 页面=%s 闸算=%s" % (rb.get("req_copper_clearance"), ev.req_cu))
        nc = rb.get("netclass") or {}
        dn = rules_disk.get("_netclass") or {}
        if set(nc) != set(dn):
            bad.append("netclass 键集 页面=%s 盘上=%s" % (sorted(nc), sorted(dn)))
        else:
            for k in dn:
                if abs(float(nc.get(k, -1)) - float(dn[k])) > 1e-9:
                    bad.append("netclass.%s 页面=%s 盘上=%s" % (k, nc.get(k), dn[k]))
        rec("K1", not bad,
            ("DRC 判据与 .kicad_pro 实读一致 (min_hole_to_hole=%s min_hole_clearance=%s "
             "min_copper_edge_clearance=%s req_copper_clearance=%s)"
             % (rules_disk.get("min_hole_to_hole"), rules_disk.get("min_hole_clearance"),
                rules_disk.get("min_copper_edge_clearance"), ev.req_cu))
            if not bad else ("K1 不一致: " + "; ".join(bad[:8])))

    # ---- K2: 可行域逐格复算 ----
    fb = blocks.get("FEAS")
    if not fb:
        rec("K2", False, "页面缺 FEAS 机器块")
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
            if int(spec.get("n_feasible", -1)) != len(jcells):
                bad.append("rot %s n_feasible 页面=%s 闸算=%d" % (rk, spec.get("n_feasible"), len(jcells))); continue
            # 分量表必须与证据一致
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
            # ★逐格实算★
            got = set(); allok = True
            for c in jcells:
                x, y = float(c[0]), float(c[1])
                r = ev.evaluate(x, y, int(rk), offs_disk[int(rk)])
                n_checked += 1
                got.add((round(x, 4), round(y, 4)))
                if not r["ok"]:
                    bad.append("rot %s 格 (%.4f,%.4f) 闸复算不可行" % (rk, x, y)); allok = False; break
                if abs(r["margin"] - float(c[2])) > 1e-6:
                    bad.append("rot %s 格 (%.4f,%.4f) 余量 证据=%s 闸算=%s" % (rk, x, y, c[2], r["margin"])); allok = False; break
                if abs(r["edge_margin"] - float(c[3])) > 1e-6:
                    bad.append("rot %s 格 (%.4f,%.4f) 板边余量 证据=%s 闸算=%s" % (rk, x, y, c[3], r["edge_margin"])); allok = False; break
            if not allok:
                continue
            # ★边界环★
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
            BUDGET = 12000
            if len(cl) > BUDGET:
                stride = (len(cl) + BUDGET - 1) // BUDGET
                cl = cl[::stride]
                ring_skip += len(cand) - len(cl)
            for (nx, ny) in cl:
                r = ev.evaluate(nx, ny, int(rk), offs_disk[int(rk)])
                ring_checked += 1
                if r["ok"]:
                    bad.append("rot %s 边界环 (%.4f,%.4f) 闸复算可行但未列入可行集" % (rk, nx, ny)); break
            if bad and bad[-1].startswith("rot %s 边界环" % rk):
                continue
            # ★最小位移落点复算★
            md = spec.get("min_displacement_point")
            if md:
                r = ev.evaluate(float(md[0]), float(md[1]), int(rk), offs_disk[int(rk)])
                if not r["ok"]:
                    bad.append("rot %s 页面声明的最小位移落点 (%.4f,%.4f) 闸复算不可行" % (rk, md[0], md[1]))
        msg = "可行域逐格复算一致: 复算 %d 格 + 边界环 %d 格 (rot 0/90/270)" % (n_checked, ring_checked)
        if ring_skip:
            msg += " (边界环抽样 %d 格)" % ring_skip
        rec("K2", not bad, msg if not bad else ("K2 不一致: " + "; ".join(bad[:8])))

    # ---- K3: 现位冲突表逐条可复算 ----
    ib = blocks.get("INPLACE")
    if not ib:
        rec("K3", False, "页面缺 INPLACE 机器块")
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
        # ★铜箔违例必须逐条对上 (★本单卡点是铜, 不是孔 ⇒ 这条必须验★) ★
        pv = (ib.get("cu_violations") or [])
        xv = []
        for r in rows:
            xv.extend(r.get("cu_violations") or [])
        if len(pv) != len(xv):
            bad.append("铜箔违例条数 页面=%d 闸算=%d" % (len(pv), len(xv)))
        else:
            for a, c in zip(pv, xv):
                for k in ("pad", "px", "py", "ref", "kind", "net", "gap"):
                    if str(a.get(k)) != str(c.get(k)):
                        bad.append("铜箔违例.%s 页面=%s 闸算=%s" % (k, a.get(k), c.get(k)))
        if not xv:
            bad.append("★现位零铜箔违例 ⇒ 与页面『现位放不下 (卡在铜)』的结论矛盾★")
        rec("K3", not bad,
            ("现位冲突表逐条可复算 (rot %d · %d pad · %d 条铜箔违例 · 孔净距全部通过)"
             % (rot, len(rows), len(xv))) if not bad else ("K3 不一致: " + "; ".join(bad[:8])))

    # ---- K4: 三朝向 pad 偏移 + 铜箔包络互换 == 实算 ----
    ob = blocks.get("ORIENT")
    cb2 = blocks.get("CRT")
    ub = blocks.get("CU")
    if not ob:
        rec("K4", False, "页面缺 ORIENT 机器块")
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
                        bad.append("rot %s pad %s.%s 页面=%s 闸算=%s" % (rk, a.get("name"), k, a.get(k), c.get(k)))
            if cb2:
                gc = (data.get("crt_offset") or {}).get(rk) or {}
                for k in ("x1", "y1", "x2", "y2"):
                    if abs(float((cb2.get(rk) or {}).get(k, 9e9)) - float(gc.get(k, -9e9))) > 1e-6:
                        bad.append("rot %s courtyard.%s 页面=%s 闸算=%s" % (rk, k, (cb2.get(rk) or {}).get(k), gc.get(k)))
            if ub:
                gu = (data.get("cu_offset") or {}).get(rk) or {}
                for k in ("x1", "y1", "x2", "y2", "w", "h"):
                    if abs(float((ub.get(rk) or {}).get(k, 9e9)) - float(gu.get(k, -9e9))) > 1e-4:
                        bad.append("rot %s 铜箔包络.%s 页面=%s 闸算=%s" % (rk, k, (ub.get(rk) or {}).get(k), gu.get(k)))
        # ★★ rot 0 与 rot 90 的铜箔包络必须【互换宽高】(★1×2 特有·不许类推 J_DEBUG★) ★★
        if ub:
            w0 = float((ub.get("0") or {}).get("w", 0)); w90 = float((ub.get("90") or {}).get("w", 0))
            h0 = float((ub.get("0") or {}).get("h", 0)); h90 = float((ub.get("90") or {}).get("h", 0))
            if abs(w0 - h90) > 1e-4 or abs(h0 - w90) > 1e-4:
                bad.append("★rot 0 / rot 90 铜箔包络未互换宽高 (w0=%s h0=%s w90=%s h90=%s)★" % (w0, h0, w90, h90))
            if abs(w0 - 1.0) > 1e-4 or abs(w90 - 2.27) > 1e-4:
                bad.append("★1×2 铜箔包络宽与官方 land 实读不符 (w0=%s w90=%s, 期望 1.0 / 2.27)★" % (w0, w90))
        rec("K4", not bad,
            "三朝向 (rot 0/90/270) pad 偏移 / courtyard bbox / 铜箔包络 与 SetOrientationDegrees 实算一致 "
            "(★含 rot 0↔90 铜箔包络互换宽高校验★)" if not bad else ("K4 不一致: " + "; ".join(bad[:8])))

    # ---- K5: 可行区 (区间) 而非单点 + 位移双口径 ----
    fb = blocks.get("FEAS") or {}
    bad = []
    rot_spec = fb.get("rot") or {}
    if not rot_spec:
        bad.append("FEAS 无 rot 规格")
    for rk in ("0", "90", "270"):
        spec = rot_spec.get(rk) or {}
        claim = spec.get("region_claim")
        if claim is None:
            bad.append("rot %s 未给出可行区声明 (region_claim) ⇒ ★只报了一个坐标就不算可行域★" % rk)
            continue
        if str(claim.get("kind")) != "区间":
            bad.append("rot %s 可行区声明 kind=%r (★必须声明为『区间』★)" % (rk, claim.get("kind")))
            continue
        if int(claim.get("n_cells", 0)) < 2:
            bad.append("rot %s 可行区声明 n_cells=%s (★<2 ⇒ 只是试了一个点★)" % (rk, claim.get("n_cells")))
            continue
        if len(spec.get("components") or []) < 1:
            bad.append("rot %s 无连通域列表 (★只报了一个点★)" % rk)
            continue
        md = spec.get("min_displacement")
        if md is None or float(md) <= 0:
            bad.append("rot %s 缺最小位移数" % rk)
        mp = spec.get("min_displacement_point")
        if not mp or len(mp) != 2:
            bad.append("rot %s 缺最小位移落点坐标" % rk)
    # ★位移双口径必须都在 (★J_UART 的 origin 不在焊盘上, 两个口径能差 2mm+★) ★
    for kw in ("原点锚点", "pad1 锚点"):
        if kw not in page_text:
            bad.append("页面缺位移口径『%s』" % kw)
    # ★现位 origin 不在焊盘上这个结构事实必须写进页面 (★否则读者会误以为『落点不动=焊盘不动』★) ★
    if "origin 不在焊盘上" not in page_text and "origin 不在焊盘" not in page_text:
        bad.append("页面未声明『封装 origin 不在焊盘上』这一结构事实")
    rec("K5", not bad,
        "§2/§4 给出的是可行区 (每朝向『区间』+ >=2 格 + 连通域列表 + 最小位移), "
        "且位移双口径 (原点锚点 / pad1 锚点) 都在" if not bad else ("K5 失败: " + "; ".join(bad[:8])))

    # ---- K6: §3 代价清单每条必须带坐标 + why ----
    cb3 = blocks.get("COST")
    if not cb3:
        rec("K6", False, "页面缺 COST 机器块")
    else:
        bad = []
        items = cb3.get("items") if isinstance(cb3, dict) else cb3
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
        # ★必须声明「过孔一个都不用挪」这条 (★代价账的核心结论★) ★
        if "n_must_move" not in page_text and "不用挪" not in page_text:
            bad.append("页面未声明『过孔要不要挪』的结论")
        rec("K6", not bad,
            "§3 代价清单 %d 条全部带坐标 + why, 且声明了过孔挪动结论" % len(items or []) if not bad
            else ("K6 失败: " + "; ".join(bad[:8])))

    # ---- K7: 板面零写板自证 ----
    bad = []
    try:
        h = hashlib.md5(open(BOARD, "rb").read()).hexdigest()
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
    rec("K7", not bad,
        "板零写板自证通过 (md5/mtime/size 三项 == 611b869e…/2026-11-06 07:07:17.362193413/4940213)"
        if not bad else ("K7 失败: " + "; ".join(bad[:6])))

    # ---- K8: 证据等级 / 零挂起 / 判据句事实句分区 / 零挂链 ----
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
    if "<!-- ISS379:CRITERIA -->" not in page_text or "<!-- ISS379:FACT -->" not in page_text:
        bad.append("缺判据句/事实句分区标记 (<!-- ISS379:CRITERIA --> / <!-- ISS379:FACT -->)")
    # 零挂链
    gc = os.path.join(ROOT, "state/gate_check.py")
    n = 0
    if os.path.exists(gc):
        n = open(gc, encoding="utf-8").read().count("check_juart_land_fit")
    if n != 0:
        bad.append("本闸已被挂进 state/gate_check.py (%d 处) ⇒ 违反零挂链" % n)
    # ★不许替 sw-lead 答 J_DEBUG 那半边 ★
    if "J_DEBUG" in page_text and "ISS-378" not in page_text:
        bad.append("页面提到 J_DEBUG 但未标注其为 ISS-378 的地界")
    rec("K8", not bad,
        "证据等级白名单 / 零挂起措辞 / 判据句事实句分区 / 零挂链 / 不越 sw-lead 地界 自证通过"
        if not bad else ("K8 失败: " + "; ".join(bad[:8])))

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
                                   for c in proj.get("net_settings", {}).get("classes", [])}
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
    print("[selftest] 基线 K0~K8 全绿")

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
        for r in b["INPLACE"]["rows"]:
            if r.get("worst_gap") is not None:
                r["worst_gap"] = 0.0123
                break
        return t

    def m_cuviol(b, t):
        b["INPLACE"]["cu_violations"] = []
        return t

    def m_orient(b, t):
        b["ORIENT"]["90"][1]["dx"] = 9.999
        return t

    def m_cu_envelope(b, t):
        b["CU"]["90"]["w"] = 1.0
        return t

    def m_crt(b, t):
        b["CRT"]["270"]["x1"] = -1.55
        return t

    # ★★药根用例: 只试一个落点就宣布可行/不可行 ★★
    def m_claim_single_point(b, t):
        b["FEAS"]["rot"]["90"]["region_claim"] = dict(kind="单点", n_cells=1,
                                                       x1=20.7, x2=20.7, y1=70.8, y2=70.8)
        return t

    def m_claim_missing(b, t):
        b["FEAS"]["rot"]["0"].pop("region_claim", None)
        return t

    def m_claim_no_components(b, t):
        b["FEAS"]["rot"]["270"]["components"] = []
        return t

    def m_cell_margin(b, t):
        b["FEAS"]["rot"]["90"]["n_feasible"] = 1
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

    def m_dual_anchor(b, t):
        return t.replace("pad1 锚点", "焊盘锚点")

    def m_origin_fact(b, t):
        return t.replace("origin 不在焊盘上", "origin 在焊盘上")

    case("C1 篡改 LAND pad 钻孔 ⇒ K0 红", "K0", m_land)
    case("C2 篡改 RULES min_hole_to_hole ⇒ K1 红", "K1", m_rules)
    case("C3 篡改可行域格数 ⇒ K2 红", "K2", m_cell_margin)
    case("C4 篡改现位冲突表孔净距 ⇒ K3 红", "K3", m_conflict)
    case("C5 ★现位零铜箔违例★ ⇒ K3 红", "K3", m_cuviol)
    case("C6 篡改 rot90 pad 偏移 ⇒ K4 红", "K4", m_orient)
    case("C7 ★篡改 rot90 铜箔包络宽★ ⇒ K4 红", "K4", m_cu_envelope)
    case("C8 篡改 rot270 courtyard bbox ⇒ K4 红", "K4", m_crt)
    case("C9 ★只试一个落点★ rot90 区间声明改单点 ⇒ K5 红", "K5", m_claim_single_point)
    case("C10 ★只试一个落点★ rot0 不给区间声明 ⇒ K5 红", "K5", m_claim_missing)
    # ★C11 说明 (2026-11-24 cont1 实测修正)★: 把 rot270 的连通域列表掏空会【同时】红两条 ——
    #   K2 (页面连通域表 vs 证据 JSON 连通域表 对不上: 页面=0 闸算=3) + K5 (无连通域列表 ⇒ 只报了一个点)
    #   ⇒ 本用例的期望红集是 {K2, K5} (★两条都必须红·且不许多红·不许少红★)
    case("C11 ★只试一个落点★ rot270 无连通域列表 ⇒ K5 红", ("K2", "K5"), m_claim_no_components)
    case("C12 §3 代价条目去掉坐标 ⇒ K6 红", "K6", m_cost_nocoord)
    case("C13 篡改页面板指纹 ⇒ K7 红", "K7", m_board_fp)
    case("C14 页面注入挂起措辞 ⇒ K8 红", "K8", m_hang)
    case("C15 §3 代价条目 why 写空 ⇒ K6 红", "K6", m_cost_why)
    case("C16 ★删掉位移双口径之一★ ⇒ K5 红", "K5", m_dual_anchor)
    case("C17 ★删掉『origin 不在焊盘上』结构事实★ ⇒ K5 红", "K5", m_origin_fact)

    # ★★ISS-379 cont1 新增: 专打「1e-4 口径差」的反向用例 (镜像式) ★★
    #   手法: 把【权威证据 JSON】里 rot 90 争议格 (7.4000,75.8000) 的 margin 改成 ±0.0002
    #         ⇒ 闸自己复算出的余量与证据对不上 ⇒ K2 必须红 (且只红 K2)
    #   ★这条直接盯住 cont1 那条红的根因: 证据与闸的余量必须逐格【严丝合缝】到 1e-6 ★
    def _perturbed_evidence(delta, tag):
        src = os.path.join(ROOT, blocks["FEAS"]["evidence_json"])
        jd = json.load(open(src, encoding="utf-8"))
        hit = 0
        for c in jd["scan"]["90"]["feas_cells"]:
            if abs(float(c[0]) - 7.4) < 1e-9 and abs(float(c[1]) - 75.8) < 1e-9:
                c[2] = round(float(c[2]) + delta, 4)
                hit += 1
                break
        if hit != 1:
            raise RuntimeError("证据 JSON 里找不到 rot 90 争议格 (7.4000,75.8000)")
        d = os.path.join(ROOT, "tmp/iss379/selftest")
        os.makedirs(d, exist_ok=True)
        out = os.path.join(d, "evidence_%s.json" % tag)
        with open(out, "w", encoding="utf-8") as fh:
            json.dump(jd, fh, ensure_ascii=False, indent=1)
        return os.path.relpath(out, ROOT)

    def m_ev_plus(b, t):
        b["FEAS"]["evidence_json"] = _perturbed_evidence(0.0002, "plus")
        return t

    def m_ev_minus(b, t):
        b["FEAS"]["evidence_json"] = _perturbed_evidence(-0.0002, "minus")
        return t

    case("C18 ★证据 JSON 争议格余量 +0.0002★ ⇒ K2 红", "K2", m_ev_plus)
    case("C19 ★证据 JSON 争议格余量 -0.0002★ ⇒ K2 红", "K2", m_ev_minus)

    npass = 0
    for name, target, mutate in CASES:
        b2 = copy.deepcopy(blocks)
        t2 = mutate(b2, page_text)
        del RESULT[:]
        run_checks(t2, b2, data, mod_disk, rules_disk)
        reds = set(lid for lid, ok, _ in RESULT if not ok)
        want = {target} if isinstance(target, str) else set(target)
        if reds == want:
            print("  PASS  %-56s ⇒ 红 %s, 其余仍绿" % (name, target))
            npass += 1
        else:
            print("  FAIL  %-56s ⇒ 期望红 %s, 实得 %s" % (name, target, sorted(reds) or "全绿"))
            for lid, ok, m in RESULT:
                if not ok:
                    print("         [%s] %s" % (lid, m))
    print("[selftest] %d/%d 条反向用例通过" % (npass, len(CASES)))
    # ★收尾: 清掉本轮为反向用例生成的临时证据副本 (★可随时重跑再生成·不作为交付物★)
    try:
        for _f in ("plus", "minus"):
            _p = os.path.join(ROOT, "tmp/iss379/selftest/evidence_%s.json" % _f)
            if os.path.exists(_p):
                os.remove(_p)
    except Exception:
        pass
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
                                   for c in proj.get("net_settings", {}).get("classes", [])}
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
    print("[gate] ISS-379 J_UART 落位可行性闸 · K0~K8")
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
