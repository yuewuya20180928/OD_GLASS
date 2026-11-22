#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★_test_edge_strict.py -- v50 概念 缝合路径验收 + 板边 fail-closed 单测

★★★**验的是真实代码路径** (★与 _test_ripup_alive 同思路):
  ① ★**抠出真方法** `stitch_same_net` / `_edge_seg_ok` 绑到假 router 上真跑
  ② ★**交叉验证 (★关键)**: ★**"KiCad DRC 报 `copper_edge_clearance` 的那条铜,
     路由器自己的 `_edge_seg_ok` 也必须抓到"** (★零漏报) ⇒
     ⇒ ★**这就证明"落线前就拦" 能把 DRC 报的这类违规全部挡在板外**

★★★**★2026-11-10 11:1x 【★本文件重写: 原版是坏的 (rc=1)★】★★★ ★★
  ★★**原版的病**: ★**夹具板换成了 `.lastgood` 里的【成品好板】**
     ⇒ ★**那块板板边违规 = 0** ⇒ ★**断言"应 ≥5 条"不成立**
     ⇒ ★**assert 在 DRC 之前就抛出** ⇒ ★★**⇒ "零漏报交叉验证"根本没在跑** ★★
  ★★**⇒ 本版改成: 夹具板由测试【自己造】** ★★
     · ★**夹具 A = 自造违规铜的合成板** (★6 条明确出板/贴边的铜 + 4 条合法凸起★)
       ⇒ ★**跑真 KiCad DRC ⇒ DRC 必须报那 6 条 ⇒ `_edge_seg_ok` 必须全抓到** ★★
     · ★**夹具 B = 实测坏案例** (★`state/.lastgood/board_v47R_arm_13833seg_*.kicad_pcb`
       ⇒ ★**实测 DRC 报 10 条 `copper_edge_clearance`**) ⇒ ★**当回归用例** ★★
  ★★**⇒ 两层夹具互为备份: 一层坏了另一层还在 ⇒ 不会出现"空夹具糊过去"** ★★

★★★**★为什么还加了"反向验证用例"(★D1/D2★)★★★ ★★
  ★★**项目铁律: 判据退化 = 停机级事故** ⇒ ★**"交叉验证"本身也可能退化成空壳** ★★
  ⇒ ★**D1: 把判据改弱 (need=0 ⇒ 永远放行) ⇒ 交叉验证必须【抓到漏报】** ★★
  ⇒ ★**D2: 把判据改过头 (永远判死) ⇒ 交叉验证必须【抓到误报】** ★★
  ⇒ ★★**⇒ 这两条保证"零漏报/零误报"不是一句空话** ★★

★**为什么不"落板后剔铜"**: ★★实测剔掉 10 条板边违规铜后 DRC 反而 12→8
   ⇒ 剔链中间那段会留悬空端 ⇒ ★**又生出新的违规** ⇒ ★**只有"预防"是正收益**

用法:
  bash state/pcbnew_py.sh state/_test_edge_strict.py
  ⇒ 全部断言过 ⇒ 打印 "ALL PASS" ⇒ rc=0; 任一失败 ⇒ rc=1

  ★★**【故意弄坏 ⇒ 守卫必须抓到】的回归实验 (★不动真路由器★)** ★★
    # ① 造一个【判据被改弱】的路由器副本 (★_edge_seg_ok 变成永远放行★)
    python3 - <<'PY'
    src = open("state/gen_pcb_routing.py", encoding="utf-8").read()
    src = src.replace("        need = EDGE_CLEAR + w / 2.0",
                      "        return True   # ★故意改弱★\n        need = EDGE_CLEAR + w / 2.0")
    open("/tmp/_mutant_router.py", "w", encoding="utf-8").write(src)
    PY
    # ② 拿副本跑本测试 ⇒ ★必须 rc≠0 (★实测: 失败 5 项 / rc=1★)
    EDGE_STRICT_SRC=/tmp/_mutant_router.py bash state/pcbnew_py.sh state/_test_edge_strict.py
"""
import ast
import io
import json
import math
import os
import re
import subprocess
import sys
import textwrap
import types

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
SRC = os.environ.get("EDGE_STRICT_SRC") or os.path.join(HERE, "gen_pcb_routing.py")
KICAD_SH = os.path.join(HERE, "kicad.sh")
# ★**相对路径行为保持不变 (★原版假定 cwd=项目根)** ★**
os.chdir(PROJ)

FAIL = []
OK = []


def chk(name, cond, detail=""):
    if cond:
        OK.append(name)
        print("  ✔ %s" % name)
    else:
        FAIL.append(name)
        print("  ✘ %s  ★%s" % (name, detail))
    return bool(cond)


src = io.open(SRC, encoding="utf-8").read()
ast.parse(src)


def _md5(p):
    import hashlib
    h = hashlib.md5()
    with open(p, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


print("★ 被测判据源码: %s" % SRC)
print("★ md5=%s%s" % (_md5(SRC),
                       ("   ★★【★覆盖模式: 这是故意改坏的副本, 守卫必须判它不合格★】★★"
                        if os.environ.get("EDGE_STRICT_SRC") else "")))

# ★**源码级前置断言 (★"闸真的接上了" ⇒ 不许只测判据本身★)**
chk("A1 源码: EDGE_STRICT env 旋钮存在且默认关",
    'EDGE_STRICT = os.environ.get("PCB_EDGE_STRICT", "0") == "1"' in src
    and 'os.environ.get("PCB_EDGE_STRICT", "0")' in src,
    "★缺 env 旋钮或默认值不是关")
chk("A2 源码: 缝合直连加了板边闸",
    "if EDGE_STRICT and not self._edge_seg_ok(a[2], a[3], b[2], b[3], width):" in src,
    "★缝合直连没加板边闸")
chk("A3 源码: 缝合 L 形加了板边闸",
    "if EDGE_STRICT and not all(" in src,
    "★缝合 L 形没加板边闸")
chk("A4 源码: _emit_path 逐段查板边",
    "if EDGE_STRICT:\n            for _k in range(len(pts) - 1):" in src,
    "★_emit_path 没逐段查板边")
chk("A5 源码: rebuild_halo 还在", "self.rebuild_halo()" in src, "★rebuild_halo 不见了")


# ── 抠出真方法 (★用真实实现, 不复刻★) ──
def grab_method(name):
    m = re.search(r"\n    def %s\(self.*?(?=\n    def |\nclass |\Z)" % re.escape(name), src, re.S)
    assert m, "★抠不出方法 %s" % name
    return textwrap.dedent(m.group(0))


def grab_func(name):
    """★模块级函数按行抠 (★正则会跨过 class 体★)"""
    out = []
    started = False
    for ln in src.split("\n"):
        if not started:
            if ln.startswith("def %s(" % name):
                started = True
                out.append(ln)
            continue
        if ln.startswith("def ") or ln.startswith("class "):
            break
        out.append(ln)
    assert out, "★抠不出函数 %s" % name
    return "\n".join(out)


m_edge = grab_method("_edge_seg_ok")
m_stitch = grab_method("stitch_same_net")

NS = {"EDGE_CLEAR": 0.50, "os": os, "math": math}
exec(compile(grab_func("_pt_seg_dist"), "<pt>", "exec"), NS)
exec(compile(grab_func("_seg_seg_dist"), "<dist>", "exec"), NS)
exec(compile(m_edge, "<edge>", "exec"), NS)
EDGE_SEGFN = NS["_edge_seg_ok"]


# ── 用例 ①: 缝合段跑出板框 ⇒ EDGE_STRICT=1 拒绝, =0 放行 (老行为不变) ──
class FakeRouter(object):
    def __init__(self):
        # ★第二个焊盘放在 y=0.2 ⇒ 距板边 0.2mm ⇒ 铜外缘 0.05mm < 0.5mm ⇒ **板边违规**
        self.net_pads = {"GND": [("U1", "1", 2.0, 2.0), ("U1", "2", 20.0, 0.2)]}
        self.tracks = []
        self.halo = [[dict() for _ in range(8)] for _ in range(3)]
        self.edge_segs = [(0.0, 0.0, 100.0, 0.0), (0.0, 0.0, 0.0, 100.0),
                          (100.0, 0.0, 100.0, 100.0), (0.0, 100.0, 100.0, 100.0)]
        self._geom_clear = lambda net, segs, lay, width: True
        self._add_track_halo = lambda *a, **k: None
        self.pad_rects = []

    def _edge_seg_ok(self, x1, y1, x2, y2, w):
        return EDGE_SEGFN(self, x1, y1, x2, y2, w)


def run_stitch(alive):
    """★真方法绑到假 router 上跑一遍 (alive 独立注入 ⇒ 能对比开/关)"""
    r = FakeRouter()
    ns = {"EDGE_STRICT": alive, "W_MIN": 0.25, "W_SIG": 0.25,
          "_pt_seg_dist": lambda *a: 9.9, "math": math}
    ns.update(NS)
    exec(compile(m_stitch, "<stitch>", "exec"), ns)
    ns["stitch_same_net"](r, nets=["GND"], width=0.30, verbose=False)
    return r.tracks


tr_on = run_stitch(True)
tr_off = run_stitch(False)
chk("B1 用例①: EDGE_STRICT=1 ⇒ 出板缝合段被拒 (落 0 条)",
    len(tr_on) == 0, "★落了 %d 条 (应 0)" % len(tr_on))
chk("B2 用例①: EDGE_STRICT=0 ⇒ 老行为不变 (仍落 ≥1 条)",
    len(tr_off) > 0, "★落了 0 条 ⇒ 行为被改了")

# ══════════════════════════════════════════════════════════════════════
# ★★★**夹具 A: 【自造违规铜】的合成板 (★★本版新增的核心★★)** ★★★
# ══════════════════════════════════════════════════════════════════════
import pcbnew                                          # noqa: E402

MM = 1000000.0
SYNTH_BOARD = "/tmp/_edge_strict_synth_fixture.kicad_pcb"
SYNTH_DRC = "/tmp/_edge_strict_synth_drc_%d.json" % os.getpid()

# ★**违规组 (★6 条: 明确出板/贴板边的铜★)**
SYNTH_BAD = [
    ("V1 v47R实测 DSI_D0_D1_N 越界段 (33.9463,0.4537)->(31.725,2.475)",
     33.9463, 0.4537, 31.725, 2.475, 0.25),
    ("V2 贴下板边 (20.00,0.20)->(30.00,0.20) (铜外缘距边 0.075mm)",
     20.0, 0.20, 30.0, 0.20, 0.25),
    ("V3 贴上板边 (80.00,99.90)->(90.00,99.90) (铜外缘距边 0.075mm)",
     80.0, 99.90, 90.0, 99.90, 0.25),
    ("V4 贴左板边 (0.10,50.00)->(0.10,60.00) (铜外缘距边 0.075mm)",
     0.10, 50.0, 0.10, 60.0, 0.25),
    ("V5 贴右板边 (159.90,50.00)->(159.90,60.00) (铜外缘距边 0.075mm)",
     159.90, 50.0, 159.90, 60.0, 0.25),
    ("V6 完全出板 (10.00,-0.50)->(20.00,-0.50) (在板外 0.5mm)",
     10.0, -0.50, 20.0, -0.50, 0.25),
]
# ★**合法组 (★4 条: 官方板风格的合法凸起 + 板内深处的铜★)**
SYNTH_OK = [
    ("L1 官方板 DSI_D0_D0_N 合法凸起 (37.45,2.70)->(36.95,3.20)",
     37.45, 2.70, 36.95, 3.20, 0.25),
    ("L2 官方板 DSI_D0_D0_N 合法凸起 (41.75,2.90)->(41.45,3.20)",
     41.75, 2.90, 41.45, 3.20, 0.25),
    ("L3 官方板 DSI_D0_D0_N 合法凸起 (40.20,3.20)->(39.95,3.10)",
     40.20, 3.20, 39.95, 3.10, 0.25),
    ("L4 板内深处的铜 (50.00,50.00)->(60.00,50.00)",
     50.0, 50.0, 60.0, 50.0, 0.25),
]

EDGE_RECT = [(0.0, 0.0, 160.0, 0.0), (0.0, 100.0, 0.0, 0.0),
             (160.0, 0.0, 160.0, 100.0), (160.0, 100.0, 0.0, 100.0)]


def build_synth_board(path):
    """★★**自己造一块带违规铜的板** (★不是拿成品好板当夹具★)"""
    b = pcbnew.CreateEmptyBoard()
    bds = b.GetDesignSettings()
    bds.m_CopperEdgeClearance = pcbnew.FromMM(0.50)      # ★与官方板一致
    bds.m_MinClearance = pcbnew.FromMM(0.20)
    for (x1, y1, x2, y2) in EDGE_RECT:
        s = pcbnew.PCB_SHAPE(b)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(x1), pcbnew.FromMM(y1)))
        s.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(x2), pcbnew.FromMM(y2)))
        s.SetLayer(pcbnew.Edge_Cuts)
        s.SetWidth(pcbnew.FromMM(0.1))
        b.Add(s)
    net = pcbnew.NETINFO_ITEM(b, "SYNTH", 0)
    b.Add(net)
    for (_lbl, x1, y1, x2, y2, w) in (SYNTH_BAD + SYNTH_OK):
        t = pcbnew.PCB_TRACK(b)
        t.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(x1), pcbnew.FromMM(y1)))
        t.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(x2), pcbnew.FromMM(y2)))
        t.SetWidth(pcbnew.FromMM(w))
        t.SetLayer(pcbnew.F_Cu)
        t.SetNet(net)
        b.Add(t)
    pcbnew.SaveBoard(path, b)


def board_edges(path):
    b = pcbnew.LoadBoard(path)
    edges = []
    for d in b.GetDrawings():
        try:
            if d.GetLayerName() != "Edge.Cuts":
                continue
            if d.GetShape() == pcbnew.SHAPE_T_SEGMENT:
                edges.append((d.GetStart().x / MM, d.GetStart().y / MM,
                              d.GetEnd().x / MM, d.GetEnd().y / MM))
        except Exception:                                # noqa: BLE001
            pass
    return b, edges


def board_tracks(b):
    out = []
    for t in b.GetTracks():
        if t.GetClass() != "PCB_TRACK":
            continue
        s, e = t.GetStart(), t.GetEnd()
        out.append((s.x / MM, s.y / MM, e.x / MM, e.y / MM,
                    t.GetWidth() / MM, t.GetLayerName(), t.GetNetname()))
    return out


def run_drc(board_path, json_path):
    """★跑真 KiCad DRC (★交叉验证的另一半★)"""
    if os.path.exists(json_path):
        os.remove(json_path)
    r = subprocess.run(["bash", KICAD_SH, "pcb", "drc", "--output", json_path,
                        "--severity-error", "--severity-warning",
                        "--format", "json", board_path],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=PROJ)
    if not os.path.exists(json_path):
        raise RuntimeError("★KiCad DRC 没产出 json (rc=%d): %s"
                           % (r.returncode, r.stderr.decode("utf-8", "replace")[:300]))
    return json.load(open(json_path, encoding="utf-8"))


def drc_edge_track_points(drc):
    """★取 DRC 报的每条 `copper_edge_clearance` 里的【违规铜 (Track)】的位置"""
    pts = []
    for v in (drc.get("violations") or []):
        if v.get("type") != "copper_edge_clearance":
            continue
        for it in (v.get("items") or []):
            desc = it.get("description") or ""
            if "Track" not in desc:            # ★板边线 (Segment on Edge.Cuts) 不是铜
                continue
            pos = it.get("pos") or {}
            if "x" in pos and "y" in pos:
                pts.append((float(pos["x"]), float(pos["y"]), desc))
    return pts


def _pt_seg_dist_local(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    if dx == 0 and dy == 0:
        return math.hypot(px - x1, py - y1)
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))


TOL = 0.05          # ★mm · 位置比对容差


def _covered(pt, seg):
    x1, y1, x2, y2 = seg
    px, py = pt
    if (abs(x1 - px) <= TOL and abs(y1 - py) <= TOL) or \
       (abs(x2 - px) <= TOL and abs(y2 - py) <= TOL):
        return True
    return _pt_seg_dist_local(px, py, x1, y1, x2, y2) <= TOL


def cross_validate(board_path, drc_json, edge_ok_fn):
    """★★**核心交叉验证** (★零漏报 + 零误报★)

    ★**返回值**: (drc点数, 判据抓到的段, 漏报的DRC点, 误报的段)
    """
    b, edges = board_edges(board_path)
    fake = types.SimpleNamespace(edge_segs=edges)
    tracks = board_tracks(b)
    flagged = [t for t in tracks if not edge_ok_fn(fake, t[0], t[1], t[2], t[3], t[4])]
    drc = run_drc(board_path, drc_json)
    pts = drc_edge_track_points(drc)
    missed = []
    for (px, py, desc) in pts:
        if not any(_covered((px, py), (t[0], t[1], t[2], t[3])) for t in flagged):
            missed.append((px, py, desc))
    fps = []
    for t in flagged:
        if not any(_covered((px, py), (t[0], t[1], t[2], t[3])) for (px, py, _d) in pts):
            fps.append(t)
    return pts, flagged, missed, fps


# ---- 造夹具板 ----
build_synth_board(SYNTH_BOARD)
chk("C0 夹具A: 自造违规铜的合成板已落盘 (★不是拿成品好板当夹具★)",
    os.path.exists(SYNTH_BOARD) and os.path.getsize(SYNTH_BOARD) > 0,
    "★合成板没生成出来")

_b, _e = board_edges(SYNTH_BOARD)
chk("C0b 夹具A: 合成板读到 Edge.Cuts (≥4 条)",
    len(_e) >= 4, "★读到 %d 条" % len(_e))

_fake = types.SimpleNamespace(edge_segs=_e)
_missed_bad = []
for (lbl, x1, y1, x2, y2, w) in SYNTH_BAD:
    if EDGE_SEGFN(_fake, x1, y1, x2, y2, w):
        _missed_bad.append(lbl)
chk("C1 夹具A: 真 `_edge_seg_ok` 必须把【自造违规铜】全部判不合格 (%d/%d)"
    % (len(SYNTH_BAD) - len(_missed_bad), len(SYNTH_BAD)),
    not _missed_bad, "★漏判: %s" % _missed_bad)

_fp_ok = []
for (lbl, x1, y1, x2, y2, w) in SYNTH_OK:
    if not EDGE_SEGFN(_fake, x1, y1, x2, y2, w):
        _fp_ok.append(lbl)
chk("C2 夹具A: 真 `_edge_seg_ok` 必须把【合法凸起/板内铜】全部判合格 (%d/%d)"
    % (len(SYNTH_OK) - len(_fp_ok), len(SYNTH_OK)),
    not _fp_ok, "★误判: %s" % _fp_ok)

# ---- 夹具A 交叉验证 (★零漏报★) ----
_pts, _flagged, _missed, _fps = cross_validate(SYNTH_BOARD, SYNTH_DRC, EDGE_SEGFN)
chk("C3 夹具A: KiCad DRC 必须报出那 6 条自造违规铜 (实测 %d 条)" % len(_pts),
    len(_pts) == len(SYNTH_BAD),
    "★DRC 报 %d 条 (应 %d 条) ⇒ 夹具没造对" % (len(_pts), len(SYNTH_BAD)))
chk("C4 夹具A 零漏报: DRC 报的每条违规铜, `_edge_seg_ok` 都抓到 (漏报 %d)" % len(_missed),
    not _missed, "★漏报 %d 条: %s" % (len(_missed), _missed[:5]))
chk("C5 夹具A 零误报: DRC 没报的合法铜, `_edge_seg_ok` 也不许报 (误报 %d)" % len(_fps),
    not _fps, "★误报 %d 条: %s" % (len(_fps), [(round(t[0], 3), round(t[1], 3)) for t in _fps[:5]]))

# ══════════════════════════════════════════════════════════════════════
# ★★★**D1/D2: 交叉验证本身的反向验证 (★防"空壳交叉验证"★)** ★★★
# ══════════════════════════════════════════════════════════════════════


def weak_never_flag(self, x1, y1, x2, y2, w):
    """★**故意把判据改弱**: 净距需求设成 0 ⇒ 永远放行 ⇒ 必须被抓出漏报**"""
    return True


def strong_always_flag(self, x1, y1, x2, y2, w):
    """★**故意把判据改过头**: 永远判死 ⇒ 必须被抓出误报**"""
    return False


_p2, _f2, _missed2, _fps2 = cross_validate(SYNTH_BOARD, SYNTH_DRC + ".weak",
                                            weak_never_flag)
chk("D1 反向验证: 判据改弱 (永远放行) ⇒ 交叉验证必须抓到漏报 (实测漏报 %d 条)" % len(_missed2),
    len(_missed2) > 0, "★改弱了却没抓到漏报 ⇒ 交叉验证是空壳")

_p3, _f3, _missed3, _fps3 = cross_validate(SYNTH_BOARD, SYNTH_DRC + ".strong",
                                            strong_always_flag)
chk("D2 反向验证: 判据改过头 (永远判死) ⇒ 交叉验证必须抓到误报 (实测误报 %d 条)" % len(_fps3),
    len(_fps3) > 0, "★改过头了却没抓到误报 ⇒ 零误报检查是空壳")

# ══════════════════════════════════════════════════════════════════════
# ★★★**夹具 B: 【实测坏案例】回归 (★v47R 板 ⇒ 实测 10 条板边违规★)** ★★★
# ══════════════════════════════════════════════════════════════════════
V47 = "/tmp/v47_R.kicad_pcb"
if not os.path.exists(V47):
    V47 = os.path.join(HERE, ".lastgood", "board_v47R_arm_13833seg_20261106_0158.kicad_pcb")
chk("E0 夹具B: 实测坏案例板在位 (★v47R ⇒ 实测 10 条板边违规★)",
    os.path.exists(V47), "★找不到 %s" % V47)

if os.path.exists(V47):
    _pb, _eb = board_edges(V47)
    chk("E0b 夹具B: 读到 Edge.Cuts (≥4 条)", len(_eb) >= 4, "★读到 %d 条" % len(_eb))
    _fakeb = types.SimpleNamespace(edge_segs=_eb)
    _flagb = [t for t in board_tracks(_pb)
              if not EDGE_SEGFN(_fakeb, t[0], t[1], t[2], t[3], t[4])]
    chk("E1 夹具B: `_edge_seg_ok` 在实测坏板上抓到 ≥5 条板边违规铜 (实测 %d 条)"
        % len(_flagb), len(_flagb) >= 5, "★只抓到 %d 条" % len(_flagb))

    _ptsB, _flagB, _missedB, _fpsB = cross_validate(V47, "/tmp/_edge_strict_drc_%d.json" % os.getpid(),
                                                     EDGE_SEGFN)
    chk("E2 夹具B: KiCad DRC 报 ≥5 条 copper_edge_clearance (实测 %d 条)" % len(_ptsB),
        len(_ptsB) >= 5, "★只报 %d 条" % len(_ptsB))
    chk("E3 夹具B 零漏报: DRC 报的 %d 条板边违规, `_edge_seg_ok` 全部抓到 (漏报 %d)"
        % (len(_ptsB), len(_missedB)),
        not _missedB, "★漏报 %d 条: %s" % (len(_missedB), _missedB[:5]))
    chk("E4 夹具B 零误报: 判据抓到的段都能在 DRC 里找到对应 (误报 %d)" % len(_fpsB),
        not _fpsB, "★误报 %d 条" % len(_fpsB))

print()
if FAIL:
    print("═══ 失败 %d 项 ═══" % len(FAIL))
    for f in FAIL:
        print("   ✘ %s" % f)
    sys.exit(1)
print("═══ ALL PASS (%d 项) ═══" % len(OK))
print("ALL PASS")
sys.exit(0)
