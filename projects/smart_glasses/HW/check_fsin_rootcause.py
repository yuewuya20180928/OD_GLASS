#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-282 · `FSIN_OUT` 根因订正 + 【布线前置闸】机器闸 (D1~D5)
=================================================================================================
派活: 项目总工 (main / moli) 2026-11-17 09:5x (job cron 775d9893)

★**本闸守的是「盘上关于 `FSIN_OUT` 的根因口径是不是【订正过的那个】, 而不是【错的那个】」** ★
★**零写板 · 零落表 · 零跑布线臂 · 零跑生成器** ★ ⇒ ★**不许跑 `state/gen_pcb_routing.py` / `state/gen_pcb_netlist_board.py` / `state/gen_production_pack.sh`** ★

★**四条判据 (★D1~D5★)**:
  D1  根因订正页在盘 + 页里【同时】写着「逃逸方向 bug 不成立」和「布线排队顺序」两个口径 (★不许只写一半★)
  D2  页里引用的两个实测数字与【盘面重算结果】一致 (★R_SER_FSIN.1 / TP_FSIN.1 的最近异网焊盘边缘距离★)
      + 页里的 escape_stub 阈值与【路由器源码】里的阈值一致 + 两个距离都 ≥ 该阈值
      ⇒ ★**⇒ 「escape_stub 不适用」这个结论【可复现】** ★
  D3  逐网忽略法可复现: 【唯一挡路者】= 页里写的那个网 + 忽略它之后 A→B 直线净距 ≥ 判据 + 忽略任何别的网都还是 FAIL
      ⇒ ★**⇒ 「唯一挡路者是 `VDD_3V3_IO`」这条结论【可复现】** ★
  D4  作业包 §6.2 已追加订正行 + ★**老 S8 行仍在 (逐字未删)**★ + 新行明写「不是板侧项 / 不需要动板 / 挪到布线臂 env 配置」
  D5  受保护 5 件 md5 逐字节不变 (★板 / `.kicad_pro` / 网表 / 脚表 / BOM★)

★**★D2 / D3 的数全是本闸自己从盘面【重算】的 (★不许抄订正页上的字★) ⇒ 订正页变成第二份过期文档时, 本闸当场红★**

★★**D5 的两层口径 (★为什么要两层★)★★:
  · ★**D5a = 落表台账链头 + 合法改板通道 (★ISS-297 改★)** ★: 板 / `.kicad_pro` 两件 ⇒ ★**判据方向一字未变:
    盘上 ≠ 判决源 ⇒ 红** ★ ⇒ ★**判决源 = 落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` 的链头** ★
    ⇒ ★**合法改板 (台账里有【单号 + 文件名 + 改前 md5 + 改后 md5】齐全的记录 + 锚点里有四项原子 `reboard` 记录)
    ⇒ 盘上 == 链头 ⇒ 放行 (★合法改板只让链头前移, 不是把判据放松★)** ★
    ⇒ ★**记录缺失 / 四项不齐 / 盘上 ≠ 链头 ⇒ 红 (★fail-closed: 链头不唯一 / 链断 / 链头无单号 ⇒ 仍红★)** ★
    ⇒ ★**基线仍是 append-only 的历史事实 (★不许改基线来「让它绿」★)** ★
    ⇒ ★**板 mtime 只在【没发生合法改板】时硬校验 (★合法改板那一趟 mtime 本来就会变★)** ★
  · ★**D5b = 变更感知** ★: 网表 / 脚表 / BOM 三件 ⇒ 盘面 md5 必须落在【权威基线台账的基线值】∪【落表台账 §16.2 登记的落表后值】这个集合里
    ⇒ ★**V 值落表是【已授权的、有留证的】盘面变更 (★`HW/SCHEMATIC_LANDING_V1_LANDED.md` §16.2 有前后 md5 对照★) ⇒ 不该把闸打红** ★
    ⇒ ★**但任何【没登记】的改动 (★偷改 CSV★) 都不在集合里 ⇒ 当场红** ★
★★

退出码: 0 = 全过 · 1 = 有不通过项 · 2 = 用法错
用法:
  python3 HW/check_fsin_rootcause.py             # ★主模式 (★只读★)
  python3 HW/check_fsin_rootcause.py --dump      # ★打印 D2/D3 的实测表 (★给订正页复算用★)
  python3 HW/check_fsin_rootcause.py --selftest   # ★反向用例 (★端到端跑沙盒副本★)
  ★自检用 --root 把闸指向沙盒副本★
"""
from __future__ import annotations

import argparse
import hashlib
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
# ★★ISS-297 · 2026-11-17 18:5x (hw-lead): 「合法改板」通道 (★判决源 = 落表台账链头★) ★★
#   ★机制照抄 SW 侧 ISS-284 已跑通的口径; ★但本域【自己写】(★不 import 别人地界★) ★
sys.path.insert(0, HERE)
import board_reboard

REL = {
    "page":       "HW/PCB/FSIN_OUT_ROOTCAUSE.md",
    "workpacket": "HW/PCB/BOARD_ONEPASS_WORKPACKET.md",
    "pcb":        "HW/PCB/demo_mainboard.kicad_pcb",
    "pro":        "HW/PCB/demo_mainboard.kicad_pro",
    "netlist":    "HW/netlist_v1.csv",
    "pins":       "HW/netlist_v1_pins.csv",
    "bom":        "HW/BOM_v1.csv",
    "router":     "state/gen_pcb_routing.py",
    "ledger":     "HW/PCB/BOARD_ONEPASS_MD5_LEDGER.md",
    "landing":    "HW/SCHEMATIC_LANDING_V1_LANDED.md",
    "rules":      "HW/PCB/ROUTING_REPORT.md",
}

# ★受保护件的硬基线 (★板 + .kicad_pro = 铁律本体★)
HARD_BASELINE = {
    "pcb": "611b869e13518c3c023fb178f91a0075",
    "pro": "3e504d2be83152e337949723e909be1b",
}
HARD_MTIME_PREFIX = "2026-11-06 07:07:17"

# ★老 S8 行 (★D4 的「逐字未删」基准★)
OLD_S8_ROW = ("| ★**S8** ★ | ★**hw + 路由器作者** ★ | ★**`FSIN_OUT` 3.01 mm 布不通** ★ | "
              "★**★疑似逃逸方向 bug, 不是布局问题 ⇒ 找错方向会白跑一轮路由** ★ |")

# ★订正行必须写的口径 (★D4★)
NEW_ROW_PHRASES = ("不是板侧项", "不需要动板", "布线臂 env 配置",
                   "布线排队顺序", "VDD_3V3_IO", "划掉")

# ★D1 必须【同时】出现的两个口径 ★
D1_PHRASES = ("逃逸方向", "不成立", "布线排队顺序")

TOL = 1e-6          # ★页上数字 vs 重算数字 的容差 (mm)★
NEAR = 1e-9

HEX32 = re.compile(r"^[0-9a-f]{32}$")


# ── 小工具 ────────────────────────────────────────────────────────────────
def md5_of(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def resolve(root: str, key: str) -> str:
    return os.path.join(root, REL[key])


# ── 板面解析 (★纯 python · 只读 · 复刻路由器 `state/gen_pcb_routing.py` 的 `_pad_rect()` 口径★) ──
def _tokenize(text: str):
    out = []
    i = 0
    n = len(text)
    while i < n:
        c = text[i]
        if c in "()":
            out.append(("atom", c))
            i += 1
        elif c == '"':
            j = i + 1
            buf = []
            while j < n:
                if text[j] == "\\" and j + 1 < n:
                    buf.append(text[j + 1])
                    j += 2
                    continue
                if text[j] == '"':
                    break
                buf.append(text[j])
                j += 1
            out.append(("str", "".join(buf)))
            i = j + 1
        elif c.isspace():
            i += 1
        else:
            j = i
            while j < n and not text[j].isspace() and text[j] not in '()"':
                j += 1
            out.append(("atom", text[i:j]))
            i = j
    return out


def _parse(toks, pos=0):
    kind, val = toks[pos]
    if kind == "atom" and val == "(":
        children = []
        pos += 1
        while toks[pos][1] != ")":
            child, pos = _parse(toks, pos)
            children.append(child)
        return ("list", children), pos + 1
    return (kind, val), pos + 1


def _kids(node):
    return node[1] if node[0] == "list" else []


def _head(node):
    k = _kids(node)
    return k[0][1] if k and k[0][0] == "atom" else None


def _sub(node, key):
    for c in _kids(node):
        if _head(c) == key:
            return c
    return None


def _num(node, idx=1, default=None):
    try:
        return float(_kids(node)[idx][1])
    except Exception:
        return default


def _at(node):
    a = _sub(node, "at")
    if a is None:
        return None
    vals = []
    for c in _kids(a)[1:]:
        if c[0] == "atom":
            try:
                vals.append(float(c[1]))
            except ValueError:
                pass
    return vals


def _netname(node):
    nt = _sub(node, "net")
    if not nt:
        return ""
    k = _kids(nt)
    if len(k) < 2:
        return ""
    return k[1][1]


class Board:
    """★只读板面模型★"""

    def __init__(self, path: str):
        text = read_text(path)
        root, _ = _parse(_tokenize(text), 0)
        self.pads = []    # (ref, num, net, cx, cy, x0, y0, x1, y1, layers)
        self.segs = []    # (net, x1, y1, x2, y2, width, layer)
        self.vias = []    # (net, x, y, dia, layers)
        for c in _kids(root):
            h = _head(c)
            if h == "footprint":
                self._fp(c)
            elif h == "segment":
                self._seg(c)
            elif h == "via":
                self._via(c)

    def _fp(self, fp):
        ref = None
        for p in _kids(fp):
            if _head(p) == "property":
                k = _kids(p)
                if len(k) >= 3 and k[1][1] == "Reference":
                    ref = k[2][1]
        fat = _at(fp)
        if not fat:
            return
        fx, fy = fat[0], fat[1]
        frot = fat[2] if len(fat) > 2 else 0.0
        for p in _kids(fp):
            if _head(p) != "pad":
                continue
            k = _kids(p)
            num_s = k[1][1]
            at = _at(p)
            sz = _sub(p, "size")
            if not at or not sz:
                continue
            dx, dy = at[0], at[1]
            prot = at[2] if len(at) > 2 else 0.0
            th = math.radians(frot + prot)
            ax = fx + dx * math.cos(th) - dy * math.sin(th)
            ay = fy + dx * math.sin(th) + dy * math.cos(th)
            w = _num(sz, 1, 0.0)
            h = _num(sz, 2, 0.0)
            r = prot % 180
            if 45 <= r <= 135:          # ★路由器的 `_pad_rect()` 口径: 45~135 ⇒ 宽高互换★
                w, h = h, w
            layers = []
            ly = _sub(p, "layers")
            if ly:
                layers = [l[1] for l in _kids(ly)[1:]]
            nn = _netname(p) or "%s.%s" % (ref or "?", num_s)
            self.pads.append((ref or "?", num_s, nn, ax, ay,
                              ax - w / 2.0, ay - h / 2.0, ax + w / 2.0, ay + h / 2.0,
                              layers))

    def _seg(self, c):
        st = _sub(c, "start")
        en = _sub(c, "end")
        wd = _sub(c, "width")
        ly = _sub(c, "layer")
        if not (st and en):
            return
        lay = _kids(ly)[1][1] if ly else ""
        self.segs.append((_netname(c), _num(st, 1, 0.0), _num(st, 2, 0.0),
                           _num(en, 1, 0.0), _num(en, 2, 0.0),
                           _num(wd, 1, 0.25), lay))

    def _via(self, c):
        at = _at(c)
        sz = _sub(c, "size")
        if not at:
            return
        layers = []
        ly = _sub(c, "layers")
        if ly:
            layers = [l[1] for l in _kids(ly)[1:]]
        self.vias.append((_netname(c), at[0], at[1], _num(sz, 1, 0.6), layers))


# ── 几何 ──────────────────────────────────────────────────────────────────
def _pt_seg_dist(px, py, ax, ay, bx, by):
    vx, vy = bx - ax, by - ay
    L2 = vx * vx + vy * vy
    if L2 <= 0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * vx + (py - ay) * vy) / L2))
    return math.hypot(px - (ax + t * vx), py - (ay + t * vy))


def _seg_seg_dist(x1, y1, x2, y2, x3, y3, x4, y4):
    def orient(ax, ay, bx, by, cx, cy):
        v = (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)
        if v > 1e-12:
            return 1
        if v < -1e-12:
            return -1
        return 0

    o1 = orient(x1, y1, x2, y2, x3, y3)
    o2 = orient(x1, y1, x2, y2, x4, y4)
    o3 = orient(x3, y3, x4, y4, x1, y1)
    o4 = orient(x3, y3, x4, y4, x2, y2)
    if o1 != o2 and o3 != o4:
        return 0.0
    return min(_pt_seg_dist(x1, y1, x3, y3, x4, y4),
               _pt_seg_dist(x2, y2, x3, y3, x4, y4),
               _pt_seg_dist(x3, y3, x1, y1, x2, y2),
               _pt_seg_dist(x4, y4, x1, y1, x2, y2))


def _pt_rect_dist(px, py, r):
    x0, y0, x1, y1 = r
    dx = max(x0 - px, 0.0, px - x1)
    dy = max(y0 - py, 0.0, py - y1)
    return math.hypot(dx, dy)


def _seg_rect_dist(x1, y1, x2, y2, r):
    """★线段到矩形 (凸) 的精确距离 (相交 ⇒ 0)★"""
    x0, y0, x1r, y1r = r
    def inside(px, py):
        return x0 - 1e-12 <= px <= x1r + 1e-12 and y0 - 1e-12 <= py <= y1r + 1e-12
    if inside(x1, y1) or inside(x2, y2):
        return 0.0
    best = min(_pt_rect_dist(x1, y1, r), _pt_rect_dist(x2, y2, r))
    for (px, py) in ((x0, y0), (x1r, y0), (x1r, y1r), (x0, y1r)):
        best = min(best, _pt_seg_dist(px, py, x1, y1, x2, y2))
    # 边-边相交判定
    # ★★2026-11-17 11:0x 【★bug 修 (★只修变量名 + 边索引, 不改判据方向★)★】★★
    #   ★老代码这里写的是 `e[0]` / `e[1]` —— ★变量 `e` 从未定义 ⇒ 抛 `NameError` ★
    #   ⇒ ★上层 `per_net_worst()` 一炸, 异常被吞掉 ⇒ ★D2 / D3 报成「读不到板面 / 读不到那两个焊盘」★
    #   ⇒ ★⇒ ★**这是一个【闸自己的代码 bug】, 不是板不在, 也不是焊盘不在** ★
    #   ★并且老代码第二段还把「边0 的端点」和「边1 的端点」混着比 (★`e[0][1]` vs `e[1][0]` 其实是同一个点★)
    #   ⇒ ★⇒ 修法: ★**逐条边测一次, 每条边用自己的两个端点★** ⇒ ★判据方向一字未改★
    def ccw(ax, ay, bx, by, cx, cy):
        return (cy - ay) * (bx - ax) > (by - ay) * (cx - ax)
    edges = (((x0, y0), (x1r, y0)), ((x1r, y0), (x1r, y1r)),
             ((x1r, y1r), (x0, y1r)), ((x0, y1r), (x0, y0)))
    for (ea, eb) in edges:
        if (ccw(x1, y1, x2, y2, ea[0], ea[1]) != ccw(x1, y1, x2, y2, eb[0], eb[1])) and \
           (ccw(ea[0], ea[1], eb[0], eb[1], x1, y1) != ccw(ea[0], ea[1], eb[0], eb[1], x2, y2)):
            return 0.0
    return best


# ── D2 / D3 的实跑复算 ─────────────────────────────────────────────────────
def nearest_other_pad(board: Board, net: str, cx: float, cy: float):
    """★复刻路由器 `_nearest_other_pad()`: 焊盘中心到别的网的焊盘外接矩形的最小距离★"""
    best = (1e9, None)
    for p in board.pads:
        if p[2] == net:
            continue
        dx = max(p[5] - cx, 0.0, cx - p[7])
        dy = max(p[6] - cy, 0.0, cy - p[8])
        d = math.hypot(dx, dy)
        if d < best[0]:
            best = (d, p)
    return best


def find_pad(board: Board, ref: str, num: str = "1"):
    """★**严格版**: ★`ref` = 【脚位引用】(★**不含脚号★) · `num` = 脚号 ★
    ★★2026-11-17 11:3x 回头修 (★main 11:0x 补充实测后的指示★): ★**老版本让 `find_pad` 自己按【最后一个点】
    去猜脚号** ⇒ ⇒ ★**main 明确: 「不许放宽 `find_pad` 本身去『猜』」** ⇒ ⇒ ★**拆脚号的活儿归【页面锚点契约】,
    不归 `find_pad`★ ⇒ ⇒ ★**本函数只做【逐字匹配】, 契约破了就匹配不上 (★fail-closed: 不猜★)** ★"""
    for p in board.pads:
        if p[0] == ref and p[1] == num:
            return p
    return None


def per_net_worst(board: Board, net: str, ax: float, ay: float, bx: float, by: float,
                  layer: str = "F.Cu"):
    """★逐网算「A→B 直线中心线 → 该网铜的最近边缘」距离 (★负数 = 穿铜★)★"""
    worst = {}
    for (nn, sx, sy, ex, ey, tw, ly) in board.segs:
        if nn == net or ly != layer:
            continue
        d = _seg_seg_dist(ax, ay, bx, by, sx, sy, ex, ey) - tw / 2.0
        if nn not in worst or d < worst[nn][0]:
            worst[nn] = (d, "seg (%.3f,%.3f)->(%.3f,%.3f) w=%.3f" % (sx, sy, ex, ey, tw))
    for (nn, vx, vy, dia, lys) in board.vias:
        if nn == net or layer not in lys:
            continue
        d = _pt_seg_dist(vx, vy, ax, ay, bx, by) - dia / 2.0
        if nn not in worst or d < worst[nn][0]:
            worst[nn] = (d, "via @(%.3f,%.3f) dia=%.3f" % (vx, vy, dia))
    for p in board.pads:
        nn = p[2]
        if nn == net or layer not in p[9]:
            continue
        d = _seg_rect_dist(ax, ay, bx, by, (p[5], p[6], p[7], p[8]))
        if nn not in worst or d < worst[nn][0]:
            worst[nn] = (d, "pad %s.%s" % (p[0], p[1]))
    return worst


def worst_excluding(per_net: dict, exclude: str):
    best = (1e9, None, None)
    for nn, (d, who) in per_net.items():
        if nn == exclude:
            continue
        if d < best[0]:
            best = (d, nn, who)
    return best


# ── 阈值来源 (★读源码 / 读规格, 不写死★) ─────────────────────────────────
def esc_threshold_from_source(router_src: str):
    """★从 `state/gen_pcb_routing.py` 里读 escape_stub 的 0.45 判据★"""
    m = re.search(r"_nearest_other_pad\(\s*net\s*,\s*cx\s*,\s*cy\s*\)\s*>=\s*([0-9]*\.?[0-9]+)", router_src)
    return float(m.group(1)) if m else None


def clearance_need_from_sources(router_src: str, rules_txt: str):
    """★判据 0.395 = W_SIG/2 (0.125) + CLEAR (0.20) + 栅格余量 (0.07)★"""
    mw = re.search(r"^W_SIG\s*=\s*([0-9]*\.?[0-9]+)", router_src, re.M)
    mc = re.search(r"^CLEAR\s*=\s*([0-9]*\.?[0-9]+)", router_src, re.M)
    if not (mw and mc):
        return None, None, None
    w = float(mw.group(1))
    clear = float(mc.group(1))
    mg = re.search(r"([0-9]*\.?[0-9]+)\s*mm\s*栅格量化余量", rules_txt)
    if not mg:
        return None, None, None
    grid = float(mg.group(1))
    return w / 2.0 + clear + grid, w, clear


# ── 订正页锚点 (★机器可读★) ──────────────────────────────────────────────
ANCHOR_RE = re.compile(r"<!--\s*fsin-anchor(.*?)-->", re.S)


def parse_anchor(page_txt: str):
    m = ANCHOR_RE.search(page_txt)
    if not m:
        return None
    out = {}
    for line in m.group(1).splitlines():
        line = line.strip()
        if not line or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip()
    return out


# ── D5: 受保护 5 件 ───────────────────────────────────────────────────────
def ledger_baselines(ledger_txt: str):
    out = {}
    for key, name in (("netlist", "baseline_netlist_md5"), ("pins", "baseline_pins_md5"),
                      ("bom", "baseline_bom_md5")):
        m = re.search(name + r"\s*:\s*([0-9a-f]{32})", ledger_txt)
        if m:
            out[key] = m.group(1)
    return out


def landing_latest_md5s(landing_txt: str):
    """★从落表台账里取【每个文件的【最新一条】落表记录】(★文件 → [(md5, 行号)])★
    ★★落表台账是【按落表批次往后追加】的 ⇒ 文件里【最后】提到该文件的那一行 = 最新一条落表记录★★
    ★★2026-11-17 11:3x (★main 11:0x 建议★): ★**取最新一条, 而不是把三个值写死, 更不是把全部历史值都放行★**
      · ★**写死三个值** ⇒ ★下一轮落表 md5 还会变 ⇒ ★**又一次假红★ ⇒ 本单一开始就没写死 (★是读出来的★)** ★
      · ★**放行全部历史登记值** ⇒ ★**回滚到中间态 (★悄悄撤销一次已拍板的落表★)也会放行** ⇒ ★**太宽** ★
      · ★**取最新一条** ⇒ ★**下一轮落表只要在台账里登记了, 闸自动跟上 (★不用改代码★)⇒ ★**同时把「回滚到中间态」拦成红** ★
    ⇒ ★**这是【收紧】不是放宽 ⇒ fail-closed 更强★** ★"""
    rows = {}
    if not landing_txt:
        return rows
    in_sec = False
    for i, ln in enumerate(landing_txt.splitlines(), 1):
        if ln.lstrip().startswith("#"):
            in_sec = ("前后对照" in ln)
            continue
        if not in_sec:
            continue
        hexes = re.findall(r"\b[0-9a-f]{32}\b", ln)
        if not hexes:
            continue
        for fname in re.findall(r"`([^`]+?\.(?:csv|pcb|pro|json|md|txt))`", ln):
            rows.setdefault(fname, []).append((i, hexes))
    out = {}
    for fname, lst in rows.items():
        i, hexes = lst[-1]          # ★最新一条 (★最后一次提到该文件的那一行★)★
        out[fname] = [(h, i) for h in hexes]
    return out


def latest_landing_row(landing_txt: str, fname: str):
    """★落表台账里【最后】提到 fname 的那一行 (★在「前后对照」段内·与 `landing_latest_md5s` 同口径★)
       ⇒ (行号, 行文本) · 找不到 ⇒ None

    ★★ISS-297 · 2026-11-17 19:3x (hw-lead) 新增 ★★
      ★**为什么要有它**: 反向用例 ⑭/⑮ 的 fixture 原来把 md5 **写死** ⇒ ISS-283 合法落表后
      那两个值就过期了 ⇒ fixture 变成空操作 ⇒ 用例假红 ⇒ ★**必须动态读台账当前链头** ★
      ⇒ ★**这条 helper 是「动态 fixture」的唯一取值口** ★
    """
    in_sec = False
    hit = None
    if not landing_txt:
        return None
    for i, ln in enumerate(landing_txt.splitlines(), 1):
        if ln.lstrip().startswith("#"):
            in_sec = ("前后对照" in ln)
            continue
        if not in_sec:
            continue
        if fname not in ln:
            continue
        if not re.findall(r"\b[0-9a-f]{32}\b", ln):
            continue
        hit = (i, ln)
    return hit


# ── 判据 ──────────────────────────────────────────────────────────────────
def check(root: str, only: str | None = None):
    results = []
    page_p = resolve(root, "page")
    wp_p = resolve(root, "workpacket")
    pcb_p = resolve(root, "pcb")
    pro_p = resolve(root, "pro")
    router_p = resolve(root, "router")
    ledger_p = resolve(root, "ledger")
    landing_p = resolve(root, "landing")
    rules_p = resolve(root, "rules")

    page_txt = read_text(page_p) if os.path.isfile(page_p) else ""
    wp_txt = read_text(wp_p) if os.path.isfile(wp_p) else ""
    router_src = read_text(router_p) if os.path.isfile(router_p) else ""
    ledger_txt = read_text(ledger_p) if os.path.isfile(ledger_p) else ""
    landing_txt = read_text(landing_p) if os.path.isfile(landing_p) else ""
    rules_txt = read_text(rules_p) if os.path.isfile(rules_p) else ""

    anchor = parse_anchor(page_txt) or {}

    # ── D1 ────────────────────────────────────────────────────────────────
    if only in (None, "D1"):
        if not os.path.isfile(page_p):
            results.append(("D1", False, "★**根因订正页不在盘: %s** ★" % REL["page"]))
        else:
            missing = [p for p in D1_PHRASES if p not in page_txt]
            if missing:
                results.append(("D1", False,
                                "★**订正页缺口径 %s ⇒ 「逃逸方向 bug 不成立」与「布线排队顺序」必须【同时】出现** ★"
                                % missing))
            elif not anchor:
                results.append(("D1", False,
                                "★**订正页缺机器可读锚点块 (`<!-- fsin-anchor … -->`) ⇒ D2/D3 无从核对** ★"))
            else:
                results.append(("D1", True,
                                "★订正页在盘 · 「逃逸方向」+「不成立」+「布线排队顺序」三个口径齐全 · 锚点块可解析 (%d 项)★"
                                % len(anchor)))

    # ── D2 / D3 共用的盘面复算 ────────────────────────────────────────────
    board = None
    pa = pb = None
    need = None
    esc_src = None
    # ★★2026-11-17 11:3x 回头修 (★main 11:0x 补充实测★): ★**拆脚号的活儿归【锚点契约】, 不归 find_pad★**
    #   ⇒ ★锚点契约 = `pad_a=<脚位引用>` + `pad_a_num=<脚号>` (★两个字段分开写, 闸不猜★)
    #   ⇒ ★老锚点 (★`pad_a=R_SER_FSIN.1` 把位号.脚号整串塞进 ref★) ⇒ 【契约破了】⇒ 下面显式报出来, 不猜不蒙★
    pad_a_spec = anchor.get("pad_a", "R_SER_FSIN")
    pad_b_spec = anchor.get("pad_b", "TP_FSIN")
    pad_a_num = anchor.get("pad_a_num", "1")
    pad_b_num = anchor.get("pad_b_num", "1")
    spec_probs = []
    for nm, sp in (("pad_a", pad_a_spec), ("pad_b", pad_b_spec)):
        if "." in sp:
            spec_probs.append("★**锚点 `%s=%s` 里还带着脚号后缀 ⇒ 【契约破了】⇒ 应写成 `%s=<脚位引用>` + "
                              "`%s_num=<脚号>` (★闸不许猜脚号★)** ★" % (nm, sp, nm, nm))
    if os.path.isfile(pcb_p):
        board = Board(pcb_p)
        pa = find_pad(board, pad_a_spec, pad_a_num)
        pb = find_pad(board, pad_b_spec, pad_b_num)
    esc_src = esc_threshold_from_source(router_src)
    need, w_sig, clear = clearance_need_from_sources(router_src, rules_txt)

    # ── D2 ────────────────────────────────────────────────────────────────
    if only in (None, "D2"):
        if spec_probs:
            results.append(("D2", False, " ".join(spec_probs)))
        elif board is None or pa is None or pb is None:
            results.append(("D2", False, "★**读不到板面 / 读不到那两个焊盘** ★ (★pa=%s pb=%s · 锚点 pad_a=%s/#%s · pad_b=%s/#%s★)"
                             % (pa is not None, pb is not None, pad_a_spec, pad_a_num, pad_b_spec, pad_b_num)))
        elif esc_src is None:
            results.append(("D2", False, "★**从路由器源码里读不到 escape_stub 的 0.45 判据** ★"))
        else:
            da, whoa = nearest_other_pad(board, pa[2], pa[3], pa[4])
            db, whob = nearest_other_pad(board, pb[2], pb[3], pb[4])
            try:
                p_da = float(anchor.get("d_a", "nan"))
                p_db = float(anchor.get("d_b", "nan"))
                p_th = float(anchor.get("esc_threshold", "nan"))
            except ValueError:
                p_da = p_db = p_th = float("nan")
            probs = []
            if abs(p_da - da) > TOL:
                probs.append("页上 d_a=%.6f ≠ 重算 %.6f" % (p_da, da))
            if abs(p_db - db) > TOL:
                probs.append("页上 d_b=%.6f ≠ 重算 %.6f" % (p_db, db))
            if abs(p_th - esc_src) > NEAR:
                probs.append("页上 esc_threshold=%.6f ≠ 源码 %.6f" % (p_th, esc_src))
            if da < esc_src:
                probs.append("%s 到最近异网焊盘 %.6f < 阈值 %.2f ⇒ escape_stub 【会】被调用" % (pa[0], da, esc_src))
            if db < esc_src:
                probs.append("%s 到最近异网焊盘 %.6f < 阈值 %.2f ⇒ escape_stub 【会】被调用" % (pb[0], db, esc_src))
            if probs:
                results.append(("D2", False, "★**" + " · ".join(probs) + "** ★"))
            else:
                results.append(("D2", True,
                                "★重算: %s→最近异网焊盘 %.6f (%s.%s/%s) · %s→最近异网焊盘 %.6f (%s.%s/%s) · "
                                "两者 ≥ 源码阈值 %.2f ⇒ escape_stub 不适用 · 页上三个数与重算逐字一致★"
                                % (pa[0], da, whoa[0], whoa[1], whoa[2], pb[0], db, whob[0], whob[1], whob[2],
                                   esc_src)))

    # ── D3 ────────────────────────────────────────────────────────────────
    if only in (None, "D3"):
        if spec_probs:
            results.append(("D3", False, " ".join(spec_probs)))
        elif board is None or pa is None or pb is None:
            results.append(("D3", False, "★**读不到板面 / 读不到那两个焊盘** ★ (★pa=%s pb=%s · 锚点 pad_a=%s/#%s · pad_b=%s/#%s★)"
                             % (pa is not None, pb is not None, pad_a_spec, pad_a_num, pad_b_spec, pad_b_num)))
        elif need is None:
            results.append(("D3", False,
                            "★**从源码 (`W_SIG`/`CLEAR`) + 规格 (`ROUTING_REPORT.md` 栅格余量) 读不出净距判据** ★"))
        else:
            net = pa[2]
            ax, ay = pa[3], pa[4]
            bx, by = pb[3], pb[4]
            L = math.hypot(bx - ax, by - ay)
            per_net = per_net_worst(board, net, ax, ay, bx, by)
            d_all, blk, who = worst_excluding(per_net, None)
            d_ign, _, who_ign = worst_excluding(per_net, blk)
            page_blk = anchor.get("blocker", "")
            probs = []
            if page_blk != blk:
                probs.append("页上 blocker=%s ≠ 重算的唯一挡路者=%s (%s)" % (page_blk, blk, who))
            if d_ign < need:
                probs.append("忽略 %s 之后净距 %.4f < 判据 %.4f ⇒ 并没有「只挡一路」" % (blk, d_ign, need))
            try:
                p_bd = float(anchor.get("blocker_d", "nan"))
                if abs(p_bd - d_ign) > TOL:
                    probs.append("页上 blocker_d=%.6f ≠ 重算 %.6f" % (p_bd, d_ign))
            except ValueError:
                probs.append("锚点块 blocker_d 不是数")
            # ★忽略任何别的网都还是 FAIL (⇒ 唯一挡路者)★
            others = []
            for nn in sorted(per_net.keys()):
                if nn == blk:
                    continue
                d_other, _, _ = worst_excluding(per_net, nn)
                if d_other >= need:
                    others.append("%s(%.4f)" % (nn, d_other))
            if others:
                probs.append("忽略这些网时直线仍能过 ⇒ 挡路者不唯一: %s" % ", ".join(others[:6]))
            if probs:
                results.append(("D3", False, "★**" + " · ".join(probs) + "** ★"))
            else:
                results.append(("D3", True,
                                "★重算: A→B 直线 L=%.4f · 唯一挡路者=%s (%s) · 忽略它之后净距 %.4f ≥ 判据 %.4f · "
                                "忽略任何别的网都还是 FAIL ⇒ 页上结论可复现★"
                                % (L, blk, who, d_ign, need)))

    # ── D4 ────────────────────────────────────────────────────────────────
    if only in (None, "D4"):
        if not os.path.isfile(wp_p):
            results.append(("D4", False, "★**作业包不在盘** ★"))
        else:
            lines = wp_txt.splitlines()
            old_idx = [i for i, ln in enumerate(lines) if ln == OLD_S8_ROW]
            new_idx = [i for i, ln in enumerate(lines) if "ISS-282 追加式订正" in ln]
            probs = []
            if not old_idx:
                probs.append("★**老 S8 行不在了 (逐字未删这一条破了)** ★")
            if not new_idx:
                probs.append("★**没有追加订正行** ★")
            else:
                row = lines[new_idx[0]]
                missing = [p for p in NEW_ROW_PHRASES if p not in row]
                if missing:
                    probs.append("订正行缺口径 %s" % missing)
                if old_idx and new_idx[0] < old_idx[0]:
                    probs.append("订正行不在老 S8 行下面")
            if probs:
                results.append(("D4", False, " · ".join(probs)))
            else:
                results.append(("D4", True,
                                "★老 S8 行逐字仍在 (L%d) · 订正行在其下 (L%d) · 「不是板侧项 / 不需要动板 / "
                                "布线臂 env 配置 / 布线排队顺序 / VDD_3V3_IO / 划掉」六个口径齐全★"
                                % (old_idx[0] + 1, new_idx[0] + 1)))

    # ── D5 ────────────────────────────────────────────────────────────────
    if only in (None, "D5"):
        probs = []
        msgs = []
        # ★★ISS-297 · 2026-11-17 18:5x (hw-lead): 板 / `.kicad_pro` 两件改走【落表台账链头 + 合法改板通道】★★
        #   ★判据方向一字未变 (盘上 ≠ 判决源 ⇒ 红); ★变的只是【判决源】: 硬钉常量 → 落表台账链头 ★
        ch = board_reboard.check_pair(root, pcb_p, HARD_BASELINE["pcb"],
                                      pro_p, HARD_BASELINE["pro"],
                                      md5fn=md5_of, ledger=landing_txt)
        if not ch["ok"]:
            for e in ch["errs"]:
                probs.append("★**%s** ★" % e)
        else:
            msgs.append(ch["pcb"]["msg"])
            msgs.append(ch["pro"]["msg"])
        # ★板 mtime: ★**合法改板那一趟 mtime 本来就会变** ⇒ 只有【没发生合法改板】时才硬校验 ★
        if ch["ok"] and not ch["reboarded"]:
            mtime = os.stat(pcb_p).st_mtime
            import time as _t
            ts = _t.strftime("%Y-%m-%d %H:%M:%S", _t.localtime(mtime))
            if not ts.startswith(HARD_MTIME_PREFIX):
                probs.append("★**板 mtime 变了: %s ≠ %s…** ★" % (ts, HARD_MTIME_PREFIX))
            else:
                msgs.append("板 mtime 未变 (★无合法改板 ⇒ mtime 仍硬校验★)")
        elif ch["ok"] and ch["reboarded"]:
            msgs.append("★已发生合法改板 ⇒ 板 mtime 不再硬校验 (★判据方向未变: 盘上仍须 == 链头★)★")
        # ★D5b: 网表 / 脚表 / BOM (变更感知: 基线 ∪ 最新一条落表记录)★
        base = ledger_baselines(ledger_txt)
        reg = landing_latest_md5s(landing_txt)
        for key, fname in (("netlist", "HW/netlist_v1.csv"),
                           ("pins", "HW/netlist_v1_pins.csv"),
                           ("bom", "HW/BOM_v1.csv")):
            fp = resolve(root, key)
            cur = md5_of(fp) if os.path.isfile(fp) else "(缺)"
            accepted = {}
            if base.get(key):
                accepted[base[key]] = "MD5 台账基线"
            for h, ln in reg.get(fname, []):
                accepted.setdefault(h, "落表台账「前后对照」L%d (★最新一条落表记录★)" % ln)
            if cur not in accepted:
                probs.append("★**%s md5=%s 不在【基线 %s ∪ 落表台账最新一条落表记录】里 ⇒ 有未登记的改动** ★"
                             % (fname, cur, base.get(key, "?")))
            else:
                msgs.append("%s = %s (出处: %s)" % (os.path.basename(fname), cur[:8], accepted[cur]))
        if probs:
            results.append(("D5", False, " · ".join(probs)))
        else:
            results.append(("D5", True, "★受保护 5 件逐字节未变 (板/`.kicad_pro` 走【落表台账链头 + 合法改板通道】 + 网表/脚表/BOM 有出处) ★ · " +
                            " · ".join(msgs)))

    return results


# ── --dump: 把 D2/D3 的实测表打出来 (★给订正页复算用★) ───────────────────
def dump(root: str):
    board = Board(resolve(root, "pcb"))
    pa = find_pad(board, "R_SER_FSIN", "1")
    pb = find_pad(board, "TP_FSIN", "1")
    da, whoa = nearest_other_pad(board, pa[2], pa[3], pa[4])
    db, whob = nearest_other_pad(board, pb[2], pb[3], pb[4])
    esc = esc_threshold_from_source(read_text(resolve(root, "router")))
    need, w, clear = clearance_need_from_sources(read_text(resolve(root, "router")),
                                                  read_text(resolve(root, "rules")))
    print("=== D2 · escape_stub 判据实测 (阈值取自路由器源码) ===")
    print("  阈值 (源码) = %.2f mm" % esc)
    print("  %-14s center=(%.6f,%.6f)  最近异网焊盘 = %.6f mm  by %s.%s/%s   %s"
          % (pa[0] + "." + pa[1], pa[3], pa[4], da, whoa[0], whoa[1], whoa[2],
             "不进 escape_stub" if da >= esc else "★进 escape_stub★"))
    print("  %-14s center=(%.6f,%.6f)  最近异网焊盘 = %.6f mm  by %s.%s/%s   %s"
          % (pb[0] + "." + pb[1], pb[3], pb[4], db, whob[0], whob[1], whob[2],
             "不进 escape_stub" if db >= esc else "★进 escape_stub★"))
    ax, ay, bx, by = pa[3], pa[4], pb[3], pb[4]
    L = math.hypot(bx - ax, by - ay)
    per_net = per_net_worst(board, pa[2], ax, ay, bx, by)
    d_all, blk, who = worst_excluding(per_net, None)
    print()
    print("=== D3 · 逐网忽略法实测 (A→B 直线 L=%.4f, 判据 %.4f) ===" % (L, need))
    print("  %-16s %-10s %-8s %s" % ("忽略的网", "净距 D", "判定", "挡路者"))
    for nn in sorted(per_net.keys(), key=lambda k: per_net[k][0]):
        d, _, w2 = worst_excluding(per_net, nn)
        print("  %-16s %-10.4f %-8s %s" % (nn, d, "PASS" if d >= need else "FAIL",
                                           per_net.get(nn, (0, ""))[1]))
    d_ign, _, who_ign = worst_excluding(per_net, blk)
    print()
    print("  ⇒ 唯一挡路者 = %s (%s)" % (blk, who))
    print("  ⇒ 忽略它之后净距 = %.4f ≥ %.4f ⇒ PASS" % (d_ign, need))
    print("  ⇒ 忽略任何别的网都还是 FAIL")
    print()
    print("=== 现状 ===")
    n_fs = sum(1 for s in board.segs if s[0] == pa[2]) + sum(1 for v in board.vias if v[0] == pa[2])
    print("  %s 铜件数 (走线+过孔) = %d ⇒ %s" % (pa[2], n_fs, "整网无铜" if n_fs == 0 else "有铜"))
    return 0


# ── --selftest: 反向用例 (★全部在 /tmp 沙盒跑, 真盘零写★) ─────────────────
SANDBOX_FILES = ("HW/PCB/demo_mainboard.kicad_pcb", "HW/PCB/demo_mainboard.kicad_pro",
                 "HW/netlist_v1.csv", "HW/netlist_v1_pins.csv", "HW/BOM_v1.csv",
                 "HW/PCB/FSIN_OUT_ROOTCAUSE.md", "HW/PCB/BOARD_ONEPASS_WORKPACKET.md",
                 "HW/PCB/BOARD_ONEPASS_MD5_LEDGER.md", "HW/SCHEMATIC_LANDING_V1_LANDED.md",
                 "state/gen_pcb_routing.py", "HW/PCB/ROUTING_REPORT.md")


def build_sandbox(root: str, dst: str):
    for rel in SANDBOX_FILES:
        src = os.path.join(root, rel)
        if not os.path.isfile(src):
            continue
        d = os.path.join(dst, rel)
        os.makedirs(os.path.dirname(d), exist_ok=True)
        shutil.copy2(src, d)


def run_gate(root: str):
    cmd = [sys.executable, os.path.join(HERE, "check_fsin_rootcause.py"), "--root", root]
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def selftest(root: str):
    cases = []
    tmp = tempfile.mkdtemp(prefix="iss282_selftest_")
    try:
        def sandbox(name):
            d = os.path.join(tmp, name)
            os.makedirs(d, exist_ok=True)
            build_sandbox(root, d)
            return d

        def run_case(label, d, expect_d=None, extra_ok=None):
            """★跑一条用例并【立刻把这个沙盒删掉】★
            ★★2026-11-17 11:5x 修: ★**老写法把 15 份沙盒留到最后一次性删 ⇒ 峰值占 ~86 MB
            ⇒ ★`/tmp` 是带 usrquota 的 tmpfs (★实测「OSError: [Errno 122] Disk quota exceeded」★)
            ⇒ ★**闸自己会跑挂** (★不是判据坏了, 是环境没空间★) ⇒ ★**修法: 每条用例跑完立刻 rmtree
            ⇒ 峰值只剩 1 份沙盒 (~5.7 MB)★** ★"""
            try:
                rc, out = run_gate(d)
                if expect_d is None:                 # ★正向对照 / 「仍绿」类★
                    ok = (rc == 0 and "\u274c" not in out)
                else:
                    ok = (rc == 1 and ("\u274c " + expect_d) in out)
                if extra_ok:
                    ok = ok and extra_ok in out
                cases.append((label, ok, out))
            finally:
                shutil.rmtree(d, ignore_errors=True)

        # ① 订正页删掉「布线排队顺序」⇒ D1 红
        d = sandbox("c1")
        p = os.path.join(d, REL["page"])
        t = read_text(p).replace("布线排队顺序", "布线先后次序")
        with open(p, "w", encoding="utf-8") as f:
            f.write(t)
        run_case("① 订正页把「布线排队顺序」口径删掉 ⇒ D1 红", d, "D1")

        # ② 锚点里的 0.45 阈值改成 1.50 ⇒ D2 红
        d = sandbox("c2")
        p = os.path.join(d, REL["page"])
        t = read_text(p).replace("esc_threshold=0.45", "esc_threshold=1.50")
        with open(p, "w", encoding="utf-8") as f:
            f.write(t)
        run_case("② 把 D2 的 0.45 阈值改成 1.50 ⇒ D2 红", d, "D2")

        # ③ 锚点里的 blocker 改成 V_SOC_IO ⇒ D3 红
        d = sandbox("c3")
        p = os.path.join(d, REL["page"])
        t = read_text(p).replace("blocker=VDD_3V3_IO", "blocker=V_SOC_IO")
        with open(p, "w", encoding="utf-8") as f:
            f.write(t)
        run_case("③ 把 D3 忽略的网名从 VDD_3V3_IO 改成 V_SOC_IO ⇒ D3 红", d, "D3")

        # ④ 作业包老 S8 行删掉 ⇒ D4 红
        d = sandbox("c4")
        p = os.path.join(d, REL["workpacket"])
        lines = read_text(p).splitlines()
        lines = [ln for ln in lines if ln != OLD_S8_ROW]
        with open(p, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        run_case("④ 把作业包老 S8 行删掉 ⇒ D4 红", d, "D4")

        # ⑤ 订正行里的「不是板侧项」删掉 ⇒ D4 红
        d = sandbox("c5")
        p = os.path.join(d, REL["workpacket"])
        lines = read_text(p).splitlines()
        for i, ln in enumerate(lines):
            if "ISS-282 追加式订正" in ln:
                lines[i] = ln.replace("不是板侧项", "板侧项")
        with open(p, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        run_case("⑤ 把订正行里的「不是板侧项」删掉 ⇒ D4 红", d, "D4")

        # ⑥ 改受保护件 (板) ⇒ D5 红
        d = sandbox("c6")
        p = os.path.join(d, REL["pcb"])
        with open(p, "a", encoding="utf-8") as f:
            f.write("\n")
        run_case("⑥ 改受保护件 (板) ⇒ D5 红", d, "D5")

        # ⑦ 改受保护件 (网表 CSV) ⇒ D5 红
        d = sandbox("c7")
        p = os.path.join(d, REL["netlist"])
        with open(p, "a", encoding="utf-8") as f:
            f.write("\n")
        run_case("⑦ 改受保护件 (网表 CSV · 无落表出处) ⇒ D5 红", d, "D5")

        # ⑧ 订正页把页上 d_a 改掉 ⇒ D2 红 (页 ≠ 盘面)
        d = sandbox("c8")
        p = os.path.join(d, REL["page"])
        t = read_text(p).replace("d_a=1.300000", "d_a=1.150000")
        with open(p, "w", encoding="utf-8") as f:
            f.write(t)
        run_case("⑧ 订正页把页上的 d_a 改成 1.150000 ⇒ D2 红 (页 ≠ 盘面)", d, "D2")

        # ⑨ 订正页把「逃逸方向」口径写坏 ⇒ D1 红
        # ★★2026-11-17 11:1x 修: ★**老用例写的是 replace("逃逸方向", "逃逸方向XX") ⇒ 子串还在 ⇒ D1 照样绿
        # ⇒ ★**那条反向用例其实是空转的 (★自证: 改完 D1 仍绿★)** ⇒ ★**改成真正把口径写坏★**
        d = sandbox("c9")
        p = os.path.join(d, REL["page"])
        t = read_text(p).replace("逃逸方向", "出脚方向")
        with open(p, "w", encoding="utf-8") as f:
            f.write(t)
        run_case("⑨ 订正页把「逃逸方向」口径写坏 ⇒ D1 红", d, "D1")

        # ⑩ 正向对照: 沙盒原样 ⇒ rc=0 (★证明闸不是恒红★)
        d = sandbox("c10")
        run_case("⑩ 正向对照: 沙盒原样不动 ⇒ rc=0 (★证明闸不是恒红★)", d, None)

        # ⑪ 订正页把 blocker_d 改错 ⇒ D3 红 (页上的数必须跟盘面重算逐字一致★)
        d = sandbox("c11")
        p = os.path.join(d, REL["page"])
        t = read_text(p).replace("blocker_d=0.438361", "blocker_d=0.500000")
        with open(p, "w", encoding="utf-8") as f:
            f.write(t)
        run_case("⑪ 订正页把 blocker_d 改成 0.500000 ⇒ D3 红 (页 ≠ 盘面)", d, "D3")

        # ⑫ 拿掉落表台账 ⇒ D5 红 (★D5b 的 fail-closed 必须还在: 无出处就不放行★)
        d = sandbox("c12")
        p = os.path.join(d, REL["landing"])
        if os.path.isfile(p):
            os.remove(p)
        run_case("⑫ 拿掉落表台账 ⇒ D5 红 (★无出处的落表值不许默认放行★)", d, "D5")

        # ⑬ ★★锚点契约破了 (★把位号.脚号整串塞回 pad_a★) ⇒ D2 红 ★★
        #   ★★2026-11-17 11:3x: ★**main 明确「不许放宽 find_pad 本身去猜」⇒ 拆脚号归【锚点契约】★
        #   ⇒ ⇒ ★**这条用例就是那道契约的守卫: 契约破了必须显式红, 不能蒙一个焊盘出来★**
        d = sandbox("c13")
        p = os.path.join(d, REL["page"])
        t = read_text(p).replace("pad_a=R_SER_FSIN\npad_a_num=1", "pad_a=R_SER_FSIN.1")
        with open(p, "w", encoding="utf-8") as f:
            f.write(t)
        run_case("⑬ 锚点把「位号.脚号」整串塞回 pad_a ⇒ D2 红 (★锚点契约破了★)", d, "D2", "契约")

        # ⑭ ★★落表台账里【最新一条】的后值被改 ⇒ D5 红 (★证明闸是【读台账】的, 不是把三个值写死★)★★
        #   ★★ISS-297 · 2026-11-17 19:3x (hw-lead) ★**: 原 fixture 把 md5 写死 (`2f17650c…`)
        #   ⇒ ISS-283 合法落表后网表 md5 已是 `37f62ac3…` ⇒ 那个 replace 是【空操作】
        #   ⇒ 用例永远绿 ⇒ 假红 ★ ⇒ ★**改成动态: 从台账读【当前最新一条】那一行, 只把它的【后值】换成 deadbeef ★**
        d = sandbox("c14")
        p = os.path.join(d, REL["landing"])
        t = read_text(p)
        hit = latest_landing_row(t, REL["netlist"])
        if hit is None:
            raise AssertionError("★台账里找不到 %s 的最新一条落表记录 ⇒ fixture 没法动态构造★" % REL["netlist"])
        row_no, row_txt = hit
        hexes = re.findall(r"\b[0-9a-f]{32}\b", row_txt)
        if not hexes:
            raise AssertionError("★台账最新那一行里没有 32 位 md5 ⇒ fixture 没法动态构造★")
        new_row = row_txt.replace(hexes[-1], "deadbeefdeadbeefdeadbeefdeadbeef")
        lines = t.splitlines(keepends=True)
        old_line = lines[row_no - 1]
        lines[row_no - 1] = new_row + ("\n" if old_line.endswith("\n") else "")
        with open(p, "w", encoding="utf-8") as f:
            f.write("".join(lines))
        run_case("⑭ 落表台账最新一条的后值被改 ⇒ D5 红 (★闸是读台账的, 不是写死三个值★)", d, "D5")

        # ⑮ ★★台账末尾追加一条【更新的】落表记录 ⇒ D5 仍绿 (★取最新一条 ⇒ 下一轮落表自动跟上, 不假红★)★★
        #   ★★ISS-297 · 2026-11-17 19:3x (hw-lead) ★**: 原 fixture 的前后值写死 (`2f17650c…`) ⇒ 已过期
        #   ⇒ ★**改成动态: 沙盒里真做一次【下一轮落表】(网表改一个字节 ⇒ 新 md5) + 台账末尾追加新记录 ★★
        #   ⇒ ★**判据方向不许变**: 盘上 md5 必须落在【最新一条落表记录】里 ⇒ 追加的是新值 ⇒ 盘上 == 新值 ⇒ 绿 ★
        d = sandbox("c15")
        p = os.path.join(d, REL["landing"])
        np = os.path.join(d, REL["netlist"])
        prev = md5_of(np)
        with open(np, "a", encoding="utf-8") as f:
            f.write("\n# ISS-297 selftest: 沙盒注入 (★模拟下一轮落表·只存在于沙盒★)\n")
        nxt = md5_of(np)
        with open(p, "a", encoding="utf-8") as f:
            f.write("\n### ★★99 · 新旧 md5 前后对照 (★沙盒自检用 · 模拟下一轮落表★) ★★\n\n"
                    "| 文件 | 前 | 后 | 变了? |\n|---|---|---|---|\n"
                    "| ★**`%s`** ★ | `%s` | `%s` | ★**是**★ |\n"
                    % (REL["netlist"], prev, nxt))
        run_case("⑮ 台账末尾追加更新的落表记录 ⇒ D5 仍绿 (★取最新一条 ⇒ 下一轮落表自动跟上★)", d, None)

        # ── ★★ISS-297 · ⑯~㉕ 「合法改板」通道的反向用例 (★跑在沙盒副本上·真盘零写★) ──
        #   ★机制: `HW/board_reboard.py` 的 CASES (★照 ISS-284 已跑通的口径★) ★
        #   ★每条都【真跑本闸】(★--root 指向沙盒★) ⇒ 判据变红/变绿都必须是本闸自己的结论★
        def ch_prepare(sb):
            for rel in SANDBOX_FILES:
                src = os.path.join(root, rel)
                d = os.path.join(sb, rel)
                os.makedirs(os.path.dirname(d), exist_ok=True)
                shutil.copy2(src, d)

        def ch_judge(sb):
            rc, out = run_gate(sb)
            return rc == 0, out

        for _name, _exp, _got, _note in board_reboard.run_cases(
                root, os.path.join(tmp, "iss297_channel"), ch_judge, prepare=ch_prepare):
            cases.append(("⑯★ISS-297★ " + _name,
                          (_exp == _got), _note))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("=" * 78)
    print("  ISS-282 · `FSIN_OUT` 根因订正闸 · ★--selftest 反向用例 (%d 条)★" % len(cases))
    print("=" * 78)
    ok = 0
    for i, (name, passed, out) in enumerate(cases):
        print("  %s %s" % ("✅" if passed else "❌", name))
        if not passed:
            print("     ---- 闸的输出 ----")
            for ln in out.splitlines():
                print("     " + ln)
        ok += 1 if passed else 0
    print("-" * 78)
    print("  ⇒ %d/%d 条反向用例全部符合预期" % (ok, len(cases)))
    print("=" * 78)
    return 0 if ok == len(cases) else 1


# ── main ──────────────────────────────────────────────────────────────────
def main() -> int:
    ap = argparse.ArgumentParser(description="ISS-282 · FSIN_OUT 根因订正 + 布线前置闸")
    ap.add_argument("--root", default=PROJ, help="★项目根 (★自检用它指向沙盒★)")
    ap.add_argument("--selftest", action="store_true", help="★反向用例★")
    ap.add_argument("--dump", action="store_true", help="★打印 D2/D3 实测表★")
    ap.add_argument("--only", default=None, help="★只跑某一条判据 (D1..D5)★")
    args = ap.parse_args()
    root = os.path.abspath(args.root)

    if args.selftest:
        return selftest(root)
    if args.dump:
        return dump(root)

    print("=" * 78)
    print("  ISS-282 · `FSIN_OUT` 根因订正 + 布线前置闸 (★主模式 · root=%s★)" % root)
    print("=" * 78)
    results = check(root, args.only)
    nbad = 0
    for key, ok, msg in results:
        if not ok:
            nbad += 1
        print("  %s %-4s %s" % ("✅" if ok else "❌", key, msg))
    print("-" * 78)
    print("  ⇒ %d 项不通过" % nbad)
    print("=" * 78)
    return 0 if nbad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
