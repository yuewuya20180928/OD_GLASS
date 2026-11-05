# -*- coding: utf-8 -*-
"""★_test_edge_strict.py -- v50 概念 缝合路径验收 + 板边 fail-closed 单测

★★★**验的是真实代码路径** (★与 _test_ripup_alive 同思路):
  ① ★**抠出真方法** `stitch_same_net` / `_edge_seg_ok` 绑到假 router 上真跑
  ② ★**交叉验证 (★关键)**: 拿 v47 的真板 (★它有 10 条板边违规) ⇒
     ★**用真 `_edge_seg_ok` 逐段筛** ⇒ ★**凡是 KiCad DRC 报 `copper_edge_clearance`
     的那条铜, 路由器自己的判据也必须抓到** (★零漏报) ⇒
     ⇒ ★**这就证明"落线前就拦" (①②) 能把 DRC 报的这类违规全部挡在板外**

★**为什么不"落板后剔铜"**: ★★实测剔掉 10 条板边违规铜后 DRC 反而 12→8
   ⇒ 剔链中间那段会留悬空端 ⇒ ★**又生出新的违规** ⇒ ★**只有"预防"是正收益**
"""
import ast
import io
import json
import os
import re
import subprocess
import textwrap
import types

SRC = "state/gen_pcb_routing.py"
src = io.open(SRC, encoding="utf-8").read()
ast.parse(src)

# ★**源码级前置断言**
assert 'EDGE_STRICT = os.environ.get("PCB_EDGE_STRICT", "0") == "1"' in src, "★缺 env 旋钮"
assert 'os.environ.get("PCB_EDGE_STRICT", "0")' in src, "★默认值不是关"
assert "if EDGE_STRICT and not self._edge_seg_ok(a[2], a[3], b[2], b[3], width):" in src, \
    "★缝合直连没加板边闸"
assert "if EDGE_STRICT and not all(" in src, "★缝合 L 形没加板边闸"
assert "if EDGE_STRICT:\n            for _k in range(len(pts) - 1):" in src, \
    "★_emit_path 没逐段查板边"
assert "self.rebuild_halo()" in src, "★rebuild_halo 不见了"


# ── 抠出真方法 (★用真实实现, 不复刻) ──
def grab_method(name):
    m = re.search(r"\n    def %s\(self.*?(?=\n    def |\nclass |\Z)" % re.escape(name), src, re.S)
    assert m, "★抠不出方法 %s" % name
    return textwrap.dedent(m.group(0))


def grab_func(name):
    """★模块级函数按行抠 (★正则会跨过 class 体)"""
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

NS = {"EDGE_CLEAR": 0.50, "os": os, "math": __import__("math")}
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
          "_pt_seg_dist": lambda *a: 9.9, "math": __import__("math")}
    ns.update(NS)
    exec(compile(m_stitch, "<stitch>", "exec"), ns)
    ns["stitch_same_net"](r, nets=["GND"], width=0.30, verbose=False)
    return r.tracks


tr_on = run_stitch(True)
tr_off = run_stitch(False)
assert len(tr_on) == 0, "★EDGE_STRICT=1 时不该落这段板边违规铜 (落了 %d 条)" % len(tr_on)
assert len(tr_off) > 0, "★EDGE_STRICT=0 时老行为必须保持 (落 0 条 ⇒ 行为被改了)"
print("  ✔ 缝合板边闸: EDGE_STRICT=1 拒 %d 条 · =0 仍落 %d 条 (老行为不变)"
      % (len(tr_on), len(tr_off)))

# ── 用例 ②: 交叉验证 (★路由器判据 vs KiCad DRC, ★零漏报) ──
import pcbnew
MM = 1000000.0
V47 = "/tmp/v47_R.kicad_pcb"
if not os.path.exists(V47):
    V47 = "state/.lastgood/board_v46R_arm_13707seg_20261106_0154.kicad_pcb"
assert os.path.exists(V47), "★找不到真板"

b = pcbnew.LoadBoard(V47)
edge_segs = []
for d in b.GetDrawings():
    try:
        if d.GetLayerName() != "Edge.Cuts":
            continue
        if d.GetShape() == pcbnew.SHAPE_T_SEGMENT:
            edge_segs.append((d.GetStart().x / MM, d.GetStart().y / MM,
                              d.GetEnd().x / MM, d.GetEnd().y / MM))
    except Exception:
        pass
assert len(edge_segs) >= 4, "★没读到 Edge.Cuts (%d 条)" % len(edge_segs)

fake = types.SimpleNamespace(edge_segs=edge_segs)
router_flagged = []
for t in b.GetTracks():
    if t.GetClass() != "PCB_TRACK":
        continue
    s, e = t.GetStart(), t.GetEnd()
    w = t.GetWidth() / MM
    if not EDGE_SEGFN(fake, s.x / MM, s.y / MM, e.x / MM, e.y / MM, w):
        router_flagged.append((s.x / MM, s.y / MM, e.x / MM, e.y / MM))
print("  ✔ 路由器判据在真板上抓到 %d 条板边违规铜" % len(router_flagged))
assert len(router_flagged) >= 5, "★该板应至少有 5 条 (实测 %d)" % len(router_flagged)

# ★**跑 KiCad DRC, 取 copper_edge_clearance 的每一条, 看路由器判据有没有漏报**
subprocess.run(["bash", "state/kicad.sh", "pcb", "drc", "--output",
                "/tmp/_edge_strict_drc.json", "--severity-error", "--severity-warning",
                "--format", "json", V47],
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
d = json.load(open("/tmp/_edge_strict_drc.json"))
drc_items = []
for v in (d.get("violations") or []):
    if v.get("type") != "copper_edge_clearance":
        continue
    for it in (v.get("items") or []):
        # ★每个违规报 2 个 item: 违规铜 (Track) + 板边线 (Segment on Edge.Cuts)
        #   ⇒ ★**只拿 Track 类 item 对账** (板边线不是铜)
        desc = it.get("description") or ""
        if "Track" not in desc:
            continue
        pos = it.get("pos") or {}
        if "x" in pos and "y" in pos:
            drc_items.append((float(pos["x"]), float(pos["y"])))
print("  ✔ KiCad DRC 报板边违规位置 %d 个" % len(drc_items))

missed = 0
for (px, py) in drc_items:
    hit = False
    for (x1, y1, x2, y2) in router_flagged:
        if (abs(x1 - px) < 0.02 and abs(y1 - py) < 0.02) or \
           (abs(x2 - px) < 0.02 and abs(y2 - py) < 0.02):
            hit = True
            break
    if not hit:
        missed += 1
assert missed == 0, "★★**路由器判据漏报了 %d 条 DRC 板边违规 ⇒ 预防不完整**" % missed
print("  ✔ 交叉验证: DRC 报的 %d 个板边违规, 路由器判据**零漏报** ⇒ ①② 预防完整"
      % len(drc_items))

print("ALL TESTS PASS")
