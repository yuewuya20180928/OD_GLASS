#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_pcb_netlist_board.py —— 用 pcbnew 从零生成 demo 主板 (网表驱动的真板子)

产出: HW/PCB/demo_mainboard.kicad_pcb
  ★**板上的每一个器件都来自网表** ⇒ ★**每个焊盘都带真实网络** ⇒ ⇒
  ★**可以用 pcbnew 机器验证 "板子 ↔ 网表" 100% 一致** (state/check_pcb_nets.py)
  ★**可以用 KiCad DRC 验几何** (state/check_pcb_drc.py)
  ★⇒ ★**"自己画图" 的验收标准不是"画得像", 而是"板子与网表逐点等价 + DRC 干净"**。

★★ 焊盘编号规则 (2026-11-03 焊盘编号修正, ★**唯一真源**):
  网表 CSV 里一个器件的引脚有两种写法:
    · **编号脚** —— 节点串形如 "<器件> pin<N>" 或 "<器件> pin<N>+pin<M>"
        ⇒ 该脚属于 **节点串里的器件名** (★**不以行的 ref 为准**),
          ★**焊盘号 = 网表里的真实针号 N (和 M)** —— 连接器脚位由此对齐规格
    · **命名脚 / 裸端** —— 节点串形如 "<器件> EN" / "<器件> A4" / "<器件>"
        ⇒ 封装还没定 ⇒ **焊盘号 = 按出现顺序的占位号 1..M** (记入占位清单)

  归属规则 (与 state/check_pcb_nets.py 里的门禁判据同源):
    R1 节点串的归属以**节点串里的器件名**为准, 不以行的 ref 为准
       (例: ref=C_AC_CSI_D0_CK_P 的行里 node2="CONN_CAM pin18" ⇒ 占的是 CONN_CAM 的 18 脚)
    R2 ★**退化行**: node1 与 node2 是**同一个裸器件** ⇒ 该行是网别名/清单行, **不占任何引脚**
       (例: net=CONN_CAM n1=CONN_CAM n2=CONN_CAM —— 规格明写"本行不再占用任何针脚")
    R3 行的 ref 若在本行两个节点串里都没出现 ⇒ ref 自己占一个裸端
    R4 裸端按 (器件, 网络) 去重; 若该网络**已被同一器件的编号脚占用** ⇒ 裸端是编号脚的
       粗略别名 ⇒ **不另占焊盘** (例: 裸 'U_CHG' @VBUS_5V_CHG ⇒ 已被 pin1 覆盖)
    R5 命名脚按 (器件, 脚名, 网络) 去重; **同名不同网 ⇒ 算两个脚** (网表缺陷, 只报告)
    R6 伪器件 (ref 以 RAIL_ / NET_ 开头) 不画封装

布局 (草案, 等 ISS-158 三件规格回填后重跑):
  · 板 160×100mm
  · 左侧 = RK3572 核心板 FET3572-C 承载区 (68×50mm)
  · 右侧 = 网表器件网格 (真实 0603/SOIC 尺寸 ⇒ 间距有意义, DRC 才有价值)
"""
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
import pcbnew  # noqa: E402
import sys as _sys
_sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from som_btb_footprint import add_som_connectors  # noqa: E402
from display_fpc_footprint import add_display_fpc  # noqa: E402
from tmp117_footprint import add_tmp117  # noqa: E402
SOM_PARAMS = os.path.join(PROJ, "HW", "PCB", "som_btb_params.json")

NETLIST = os.path.join(PROJ, "HW", "netlist_v1.csv")
PCB = os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb")
REPORT = os.path.join(PROJ, "HW", "PCB", "PCB_NETLIST_FILL.txt")

BOARD_W, BOARD_H = 160.0, 100.0   # ★11-03: SOM 4 排 100 脚座占 x 8..85 ⇒ 器件网格移到 x>=92
GRID_X0, GRID_Y0 = 92.0, 8.0   # ★避开 SOM 座区 (x 8..85)
GRID_PITCH_X, GRID_PITCH_Y = 4.2, 4.2
GRID_COLS = 16
SOM_AREA = (8.0, 6.0, 68.0, 50.0)   # SOM 承载区 x,y,w,h
MM = 1e6
PSEUDO = ("RAIL_", "NET_")
# ★USB-IF 物理脚名 (A1/A4/A5/A6/A7/A8/A9/A12 · B 同 · shield) 就是**真实焊盘号**
USBIF_RE = re.compile(r"^(?:[AB](?:1|4|5|6|7|8|9|12)|shield)$")   # ★网别名伪器件 —— 不是元件, 不画封装


def V(x, y):
    return pcbnew.VECTOR2I(int(round(x * MM)), int(round(y * MM)))


# ★★2026-11-03 09:54 老板口径: "没有整机, 没有镜脚, demo/主板用 type-c 供电"
#   ⇒ **这块板子就是 demo 主板** ⇒ 网表里 board=CHG_BOARD (充电链那套) 与 board=HINGE (跨铰链两个座)
#   的件**不在这块板上** ⇒ ⇒ 板生成器按 board 列过滤 (只取 MAIN_PCB)
#   ⇒ ⇒ 网表仍是"产品级真源"(充电链那套留档), 但**板子只画 demo 主板**
BOARD_FILTER = "MAIN_PCB"



def _is_pad_name(tail):
    """★真实焊盘号判定: "pin<N>" (网表针号) 或 **USB-IF 物理脚名** (A1/A4/A5/B12/shield …)
    ★USB-C 座 (如 GCT USB4105) 的 KiCad 封装正是用这组名字当 pad number ⇒ 必须当真实焊盘号"""
    if not tail:
        return False
    return bool(re.fullmatch(r"pin\d+(\+pin\d+)*", tail)) or bool(USBIF_RE.match(tail))

def load_rows():
    with open(NETLIST, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    keep = [r for r in rows if (r.get("board") or "MAIN_PCB").strip() == BOARD_FILTER]
    print(f"  [板级过滤] {BOARD_FILTER}: {len(keep)}/{len(rows)} 行进板 "
          f"(CHG_BOARD / HINGE 的件不在 demo 主板上)")
    return keep


# ---------------------------------------------------------------- 网表 → 焊盘

def split_node(node):
    """节点串 → (器件名, 脚名 or None)
    ★ 归属以**节点串里的器件名**为准, 不以行的 ref 为准。"""
    node = (node or "").strip()
    if not node:
        return None, None
    m = re.match(r"^([A-Za-z_0-9]+)\s+(.*)$", node)
    if not m:
        return node, None            # 裸端 (没有脚名)
    return m.group(1), m.group(2).strip()


def split_names(tail):
    """命名脚里的 '+' 只有后面还跟着字符时才是**分隔符**
    (B+ 是一个脚名; A1+A12+B1+B12 是四个脚)。"""
    return [p.strip() for p in re.split(r"\+(?=\w)", tail) if p.strip()]


def derive_pads(rows):
    """★网表 → 器件 → [(焊盘号, 网络, 脚类型)]   (焊盘编号规则见文件头)

    返回 (per_ref, placeholder, notes):
      per_ref    : {器件: [(焊盘号, 网络, 'P'|'N'|'B')]}
      placeholder: {器件: 焊盘数} —— 焊盘号是占位(行序)的器件
      notes      : 网表缺陷提示 (同名脚挂两个网等)
    """
    refs = set()
    for r in rows:
        ref = (r.get("ref") or "").strip()
        if ref:
            refs.add(ref)
    real = {x for x in refs if not x.startswith(PSEUDO)}
    # ★器件宇宙 = ref 列里的真实器件 ∪ **节点串里带编号脚的器件**
    #   (J_SOM_P1..P4 是 SoM 的 4 组 100 脚 BTB —— 只出现在节点串里, 不在 ref 列,
    #    但它们**有真实针号**, ⇒ 必须建封装, 否则 SoM 的信号在板上是断的)
    for r in rows:
        for k in ("node1", "node2"):
            comp, tail = split_node(r.get(k))
            if not comp or comp in real or comp.startswith(PSEUDO):
                continue
            if tail and _is_pad_name(tail):
                real.add(comp)

    # dev -> OrderedDict[term_key] = (net, kind)
    terms = {}
    notes = []
    for r in rows:
        net = (r.get("net") or "").strip()
        ref = (r.get("ref") or "").strip()
        if not net:
            continue
        parsed = [split_node(r.get(k)) for k in ("node1", "node2")]
        # R2 退化行: 两个节点是同一个裸器件 ⇒ 不占引脚
        if (parsed[0][0] == parsed[1][0]
                and parsed[0][1] is None and parsed[1][1] is None):
            continue
        seen_here = set()
        for comp, tail in parsed:
            if comp is None or comp not in real:
                continue
            d = terms.setdefault(comp, {})
            if tail and _is_pad_name(tail):
                for tok in tail.split("+"):          # 编号脚 ⇒ 真实针号
                    tok = tok.strip()
                    # ★"pin<N>" ⇒ 数字脚号; ★USB-IF 物理脚名 (A1/B12/shield) ⇒ **字符串脚号**
                    key = ("P", int(tok[3:])) if tok.startswith("pin") else ("P", tok)
                    if key in d and d[key][0] != net:
                        notes.append(f"{comp} {key[1]} 同时挂 {d[key][0]} 与 {net}")
                    d.setdefault(key, (net, "P"))
                    seen_here.add(comp)
            elif tail:
                for nm in split_names(tail):        # 命名脚 ⇒ 占位
                    key = ("N", nm, net)
                    if key not in d:
                        same = [k for k in d if k[0] == "N" and k[1] == nm]
                        if same:
                            notes.append(f"{comp} 脚 {nm} 同时挂 {d[same[0]][0]} 与 {net}"
                                        f" (同名脚多网 ⇒ 封装定脚号后才能收敛)")
                    d.setdefault(key, (net, "N"))
                    seen_here.add(comp)
            else:
                d.setdefault(("B", net), (net, "B"))   # 裸端 (同器件同网 ⇒ 同一个)
                seen_here.add(comp)
        # R3 行的 ref 若本行没出现 ⇒ ref 自己占一个裸端
        if ref and ref in real and ref not in seen_here:
            terms.setdefault(ref, {}).setdefault(("B", net), (net, "B"))

    # R4 裸端若被同器件的编号脚覆盖 ⇒ 粗略别名, 不另占焊盘
    for comp, d in terms.items():
        pinnets = {v[0] for k, v in d.items() if k[0] == "P"}
        for k in [k for k in d if k[0] == "B" and k[1] in pinnets]:
            del d[k]

    # 焊盘号: 有编号脚 ⇒ 真实针号; 无编号脚 ⇒ 按出现顺序占位
    per_ref, placeholder = {}, {}
    for comp, d in terms.items():
        if not d:
            continue
        if any(k[0] == "P" for k in d):
            pins = sorted(((k[1], v[0], "P") for k, v in d.items() if k[0] == "P"),
                          key=lambda x: (0, x[0]) if isinstance(x[0], int) else (1, x[0]))
            # ★防御: 若还有没被编号脚覆盖的命名脚/裸端 ⇒ 从 max(针号)+1 往后排
            rest = [v for k, v in d.items() if k[0] != "P"]
            if rest:
                # ★脚号可能是数字 (pin<N>) 或字符串 (USB-IF 的 A1/B12) ⇒ 排序与续号分开处理
                _nums = [x[0] for x in pins if isinstance(x[0], int)]
                nxt = (max(_nums) + 1) if _nums else 1
                for (net, kind) in rest:
                    pins.append((nxt, net, kind))
                    nxt += 1
            per_ref[comp] = pins
        else:
            pins = []
            n = 0
            for k, v in d.items():
                n += 1
                pins.append((n, v[0], v[1]))
            per_ref[comp] = pins
            placeholder[comp] = n
    return per_ref, placeholder, notes


def group_refs(rows):
    """★兼容旧接口: 返回 {器件: [(焊盘号, 网络, 类型)]}"""
    per_ref, _ph, _notes = derive_pads(rows)
    return per_ref


def kind_of(ref):
    R = ref.upper()
    for k, pref in (("R", ("R_", "RN_")), ("C", ("C_", "CN_")), ("FB", ("FB_", "L_")),
                     ("D", ("D_", "TVS")), ("IC", ("U_", "IC_", "Q_")),
                     ("CONN", ("J_", "CONN_")), ("SW", ("SW_", "BT_")),
                     ("LED", ("LED_",)), ("TP", ("TP_",))):
        if R.startswith(pref):
            return k
    return "IC"


def size_of(kind, npins):
    """(w, h, 每排脚数, 脚距, 排数) —— ★排数决定焊盘排布 (单排件不能被拆成两排!)"""
    if kind in ("R", "C", "LED"):
        return 1.8, 1.0, 1, 1.6, 1
    if kind == "D":
        return 2.7, 1.6, 1, 2.3, 1
    if kind == "FB":
        return 2.0, 1.6, 2, 1.0, 2
    if kind == "SW":
        return 3.0, 3.0, 1, 2.2, 1
    if kind == "TP":
        return 1.4, 1.4, 1, 0.0, 1
    if kind == "CONN":
        # ★单排! (FPC 座就是一条排线) ⇒ 之前被拆两排 ⇒ 两排焊盘在同 x 区间重叠 ⇒ 短路
        return max(6.0, (npins - 1) * 0.5 + 2.6), 4.0, npins, 0.5, 1
    per = max(1, (npins + 1) // 2)
    return max(4.0, (per - 1) * 1.27 + 2.4), 5.0, per, 1.27, 2


def add_outline(board):
    w, h = BOARD_W, BOARD_H
    pts = [(0, 0), (w, 0), (w, h), (0, h), (0, 0)]
    for i in range(len(pts) - 1):
        seg = pcbnew.PCB_SHAPE(board)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetLayer(pcbnew.Edge_Cuts)
        seg.SetStart(V(*pts[i]))
        seg.SetEnd(V(*pts[i + 1]))
        seg.SetWidth(int(0.1 * MM))
        board.Add(seg)


def _mkpad(fp, num, net, px, py, pitch, netmap):
    pad = pcbnew.PAD(fp)
    pad.SetNumber(str(num))
    pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
    pad.SetShape(pcbnew.PAD_SHAPE_RECT)
    pw = min(0.6, max(0.18, pitch * 0.55))
    pad.SetSize(V(pw, 0.9))
    pad.SetPosition(V(px, py))
    pad.SetLayerSet(pad.SMDMask())
    if net in netmap:
        pad.SetNet(netmap[net])
    fp.Add(pad)
    return pad


def make_footprint(board, ref, value, kind, pins, netmap, x, y, label=True):
    """pins = [(焊盘号, 网络, 类型)] —— ★焊盘号直接用网表给的号 (编号脚=真实针号)"""
    w, h, per_side, pitch, nrows = size_of(kind, len(pins))
    fp = pcbnew.FOOTPRINT(board)
    fp.SetReference(ref)
    fp.SetValue(value)
    # ★位号/值文字放 F.Fab 并隐藏 ⇒ 丝印层只留人工加的装配标识 ⇒ 消除 silk_overlap
    try:
        fp.Reference().SetLayer(pcbnew.F_Fab)
        fp.Reference().SetVisible(False)
        fp.Value().SetLayer(pcbnew.F_Fab)
        fp.Value().SetVisible(False)
    except Exception:
        pass
    # 本体矩形 (Edge.Cuts)
    r = pcbnew.PCB_SHAPE(board)
    r.SetShape(pcbnew.SHAPE_T_SEGMENT)
    r.SetLayer(pcbnew.F_Fab)
    r.SetStart(V(-w / 2, -h / 2))
    r.SetEnd(V(w / 2, -h / 2))
    r.SetWidth(int(0.1 * MM))
    fp.Add(r)
    r2 = pcbnew.PCB_SHAPE(board)
    r2.SetShape(pcbnew.SHAPE_T_SEGMENT)
    r2.SetLayer(pcbnew.F_Fab)
    r2.SetStart(V(w / 2, -h / 2))
    r2.SetEnd(V(w / 2, h / 2))
    r2.SetWidth(int(0.1 * MM))
    fp.Add(r2)
    r3 = pcbnew.PCB_SHAPE(board)
    r3.SetShape(pcbnew.SHAPE_T_SEGMENT)
    r3.SetLayer(pcbnew.F_Fab)
    r3.SetStart(V(w / 2, h / 2))
    r3.SetEnd(V(-w / 2, h / 2))
    r3.SetWidth(int(0.1 * MM))
    fp.Add(r3)
    r4 = pcbnew.PCB_SHAPE(board)
    r4.SetShape(pcbnew.SHAPE_T_SEGMENT)
    r4.SetLayer(pcbnew.F_Fab)
    r4.SetStart(V(-w / 2, h / 2))
    r4.SetEnd(V(-w / 2, -h / 2))
    r4.SetWidth(int(0.1 * MM))
    fp.Add(r4)
    # 焊盘 —— ★按焊盘号排序 ⇒ 焊盘在封装上的顺序 = 脚号顺序
    ordered = sorted(pins, key=lambda t: (0, t[0], 0) if isinstance(t[0], int) else (1, str(t[0]), 0))
    n = len(ordered)
    if nrows == 1:
        for i, (pnum, net, _kind) in enumerate(ordered):
            px = -w / 2 + 0.9 + i * pitch
            py = -h / 2 + 0.6
            _mkpad(fp, pnum, net, px, py, pitch, netmap)
    else:
        half = (n + 1) // 2
        for i, (pnum, net, _kind) in enumerate(ordered):
            side = 0 if i < half else 1
            k = i if side == 0 else i - half
            # ★两排件: 左右两侧对称排 (之前两排落在 w 中间 ⇒ 相距仅 0.2mm ⇒ 短路)
            px = (-w / 2 + 0.6 + k * pitch) if side == 0 else (w / 2 - 0.6 - k * pitch)
            py = (-h / 2 + 0.5) if side == 0 else (h / 2 - 0.5)
            _mkpad(fp, pnum, net, px, py, pitch, netmap)
    fp.SetPosition(V(x, y))
    board.Add(fp)
    return fp



def _pin_net_from_netlist(ref=None):
    """从 HW/netlist_v1.csv 解析器件的 {脚号: 网络} (网表是唯一真源)
       ref=None ⇒ 解析 J_SOM_P1..P4; ref="CONN_LIGHT" ⇒ 解析显示 FPC 座"""
    import csv as _csv
    import re as _re
    _out = {}
    pat = r"CONN_LIGHT pin(\d+)" if ref == "CONN_LIGHT" else r"J_SOM_(P\d) pin(\d+)"
    with open(NETLIST, encoding="utf-8") as _f:
        for _r in _csv.DictReader(_f):
            _net = (_r.get("net") or "").strip()
            if not _net:
                continue
            for _k in ("node1", "node2"):
                _m = _re.fullmatch(pat, (_r.get(_k) or "").strip())
                if _m:
                    if ref == "CONN_LIGHT":
                        _out[int(_m.group(1))] = _net
                    else:
                        _out.setdefault(_m.group(1), {})[int(_m.group(2))] = _net
    return _out


def main():
    rows = load_rows()
    per_ref, placeholder, notes = derive_pads(rows)
    value_of = {}
    for r in rows:
        ref = (r.get("ref") or "").strip()
        if ref and ref not in value_of:
            value_of[ref] = (r.get("value") or "")[:40]
    for ref in per_ref:
        if ref not in value_of:
            # ★只在节点串里出现的器件 (J_SOM_P1..P4) —— ref 列没有它 ⇒ 值给个占位
            value_of[ref] = "SoM BTB %s (100pin, 部分已分配)" % ref.split("_")[-1]
    board = pcbnew.BOARD()
    board.SetCopperLayerCount(6)
    add_outline(board)

    # 网络 (只建真实被焊盘用到的网)
    used_nets = sorted({net for pins in per_ref.values() for (_p, net, _k) in pins})
    netmap = {}
    for nm in used_nets:
        ni = pcbnew.NETINFO_ITEM(board, nm)
        board.Add(ni)
        netmap[nm] = ni

    # 网表器件: 行式装箱 (按实际宽高排, 留 2mm 间距 ⇒ 不重叠 ⇒ DRC 有意义)
    # ★器件排布区: x 从 78 起 (SOM 承载区 8..76 ⇒ 留 2mm) · 右边到板边 3mm
    #   ★11-03: 4 个 BTB 座按手册底面图的 2×2 位置放 ⇒ 座实际占 x 13.7..70.3 ⇒ 器件区可以更宽
    PK_AREA = (78.0, 5.0, BOARD_W - 3.0, BOARD_H - 3.0)   # x0,y0,x1,y1
    items = []
    for ref in sorted(per_ref.keys()):
        if ref.startswith(PSEUDO):
            continue   # ★网别名伪器件 (RAIL_SYS / NET_*) —— 不是元件, 不画封装
        if ref.startswith("J_SOM_"):
            continue   # ★**SoM 的 4 组 100pin BTB 座由 som_btb_footprint 模块专门画**
                       #   (0.4mm pitch / 0.2mm 焊盘 / 双排奇偶脚) ⇒ 这里跳过, 否则会多画一套重复焊盘
        if ref == "CONN_LIGHT":
            continue   # ★**显示 FPC 座 (22p/0.5mm, HiROSE FH12-22S) 由 display_fpc_footprint 模块按官方封装画**
                       #   (通用 CONN 封装是"假封装": 焊盘尺寸/位置都不对) ⇒ 这里跳过
        pins = per_ref[ref]
        kind = kind_of(ref)
        w, h, _per, _pitch, _nr = size_of(kind, len(pins))
        items.append((ref, pins, kind, w, h))
    items.sort(key=lambda it: (round(it[4], 1), it[3]))
    px, py = PK_AREA[0], PK_AREA[1]
    row_h = 0.0
    placed = 0
    for (ref, pins, kind, w, h) in items:
        if px + w > PK_AREA[2]:
            px = PK_AREA[0]
            py += row_h + 3.0
            row_h = 0.0
        if py + h > PK_AREA[3]:
            print(f"⚠️ 装不下: {ref} (y={py:.1f}) ⇒ 需要更大板或更紧的间距")
            break
        if ref == "U_TEMP":
            # ★TMP117 = WSON-6 (DRV0006B) 官方封装 —— 通用 IC 封装是"假封装" (1.27mm pitch) ⇒ 单独画
            add_tmp117(board, netmap, pins, px + w / 2.0, py + h / 2.0)
        else:
            make_footprint(board, ref, value_of.get(ref, ""), kind, pins, netmap,
                           px + w / 2.0, py + h / 2.0)
        placed += 1
        px += w + 3.0
        row_h = max(row_h, h)
    py += row_h + 3.0
    # SOM 承载区 (FET3572-C 68×50) + 它的 4×100pin/0.4mm BTB 座 (占位: 按 400 脚模型)
    sx, sy, sw, sh = SOM_AREA
    # ★★2026-11-03 01:0x: SOM 座 = **4 个独立 100 脚 BTB (P1..P4)** —— ★**布局待修** (当前与器件网格冲突 ⇒ DRC 非零)
    #   ★**已就绪的部分**: 引脚映射 (`HW/PCB/som_pin_full_map.json` 399 行) + 分配表 (`HW/PCB/SOM_PIN_ASSIGNMENT.md`) + 网表脚本 (`state/_iss165_assign_final.py`)
    #   ⇒ **明早**: 重跑 A2 网表脚本 ⇒ 板生成器里把 4 排座放到与器件网格不重叠的位置 ⇒ 重跑 DRC/parity
    #   ★★**当前刻意不画 4 排座** ⇒ 板子保持 A1 状态 (DRC=0 / parity 全过), 避免带着未修的布局进 Gerber
    som = pcbnew.FOOTPRINT(board)
    som.SetReference("J_SOM")
    som.SetValue("Forlinx FET3572-C SoM 68x50 (4x100pin BTB) - FOOTPRINT PENDING")

    # SOM 承载区外形 (68×50mm) —— 只作装配参考, 不是铜
    _so = pcbnew.PCB_SHAPE(board)
    _so.SetShape(pcbnew.SHAPE_T_SEGMENT)
    _so.SetLayer(pcbnew.F_Fab)
    _so.SetStart(V(sx, sy))
    _so.SetEnd(V(sx + sw, sy))
    _so.SetWidth(int(0.1 * MM))
    board.Add(_so)

    # ★★A2 段: SoM 的 4 组 100pin BTB 座 (Hirose DF40C-100DS-0.4V(51))
    #   脚号编排: **奇数脚 = 一排 / 偶数脚 = 另一排** ⇒ 我们的焊盘 n 正好对插 SoM 的 n 脚
    _som_pins = _pin_net_from_netlist()
    add_som_connectors(board, netmap, SOM_PARAMS, _som_pins)

    # ★★2026-11-04: 显示 FPC 座 (Pi5 22p/0.5mm DISPLAY 座口径) —— **官方封装** (RPi CM5IO 的 FH12-22S)
    #   针序见 HW/PCB/PI5_DSI_22P_PINOUT.md; 焊盘号 = 网表真实针号 (1..22)
    _light_pins = _pin_net_from_netlist(ref="CONN_LIGHT")
    add_display_fpc(board, netmap, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                "..", "HW", "PCB", "display_fpc_params.json"),
                    _light_pins)

    board.BuildListOfNets()
    pcbnew.SaveBoard(PCB, board)

    # 自检: 重新载入, 比对 **(ref, 焊盘号) → 网络** (焊盘级, 不是 (ref,net) 集合!)
    b2 = pcbnew.LoadBoard(PCB)
    if b2 is None:
        print("❌ 存盘后读不回来 (板文件无效)")
        return 1
    pairs = set()
    npads = 0
    for fp in list(b2.GetFootprints()):
        for pad in list(fp.Pads()):
            npads += 1
            nm = pad.GetNetname()
            if nm:
                pairs.add((fp.GetReference(), str(pad.GetNumber()), nm))
    want = {(ref, str(p[0]), p[1]) for ref, pins in per_ref.items()
            if not ref.startswith(PSEUDO) for p in pins}
    missing, extra = want - pairs, pairs - want
    n_num = sum(1 for ref, pins in per_ref.items()
                if any(k == "P" for (_n, _t, k) in pins))
    n_ph = len(placeholder)
    rep = [f"PCB 网表驱动生成 · {len(per_ref)} 个器件 · {npads} 个焊盘 · 板 {BOARD_W}×{BOARD_H}mm",
           f"  焊盘编号来源: 编号脚=网表真实针号 ({n_num} 个器件) / 命名脚=行序占位 ({n_ph} 个器件)",
           f"  板上 (ref,焊盘号)→网络 绑定: {len(pairs)}  (网表推出 {len(want)})",
           f"  ★缺失: {len(missing)} {sorted(missing)[:5]}",
           f"  ★多余: {len(extra)} {sorted(extra)[:5]}",
           f"  SOM 占位: 68×50mm + 4×100pin/0.4mm BTB (400 焊盘)"]
    if notes:
        rep.append(f"  ★网表提示 {len(notes)} 条: {notes[:3]}")
    ok = not missing and not extra
    rep.append(f"\n判定: {'全过 (板子与网表 100% 一致)' if ok else '有不一致'}")
    open(REPORT, "w", encoding="utf-8").write("\n".join(rep) + "\n")
    print("\n".join(rep))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
