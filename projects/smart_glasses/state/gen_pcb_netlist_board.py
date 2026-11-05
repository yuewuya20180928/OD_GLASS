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
import json  # ★★2026-11-05 08:17 **修: 落盘时刻印用了 json 却没 import ⇒ 印没写成 ⇒ 收工闸判据失效**

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
import pcbnew  # noqa: E402
import sys as _sys
_sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from som_btb_footprint import add_som_connectors  # noqa: E402
from display_fpc_footprint import add_display_fpc  # noqa: E402
from usb_c_footprint import add_usb_c  # noqa: E402
from tmp117_footprint import add_tmp117  # noqa: E402
SOM_PARAMS = os.path.join(PROJ, "HW", "PCB", "som_btb_params.json")

NETLIST = os.path.join(PROJ, "HW", "netlist_v1.csv")
# ★2026-11-05: 输出路径可用环境变量改 (便于**并行做实验**而不动正式板)
PCB = os.environ.get("PCB_OUT") or os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb")
REPORT = os.path.join(PROJ, "HW", "PCB", "PCB_NETLIST_FILL.txt")

# ★★2026-11-05 03:45 加环境变量开关: **板子尺寸可临时放大** (缓解 BTB 密集区布线拥塞)
#   动机: 186 器件 / 400 个 0.4mm pitch BTB 焊盘 ⇒ 160×100 的板子布线拥塞 ⇒ unconnected 卡在 ~90
#   ⇒ 用 `PCB_BOARD_W=180 PCB_BOARD_H=120` 跑一轮试试 ⇒ 若 unconnected 明显下降 ⇒ 就把板子定大一点
#   (★**板尺寸是草案, 最终要按结构/整机定** ⇒ demo 板先以"能装下 + 能布通"为准)
# ★**改尺寸必须同步** `HW/PCB/demo_mainboard_params.json` 的 board 段 (否则叠层/阻抗文档会说错板子)
BOARD_W = float(os.environ.get("PCB_BOARD_W", 160.0))
BOARD_H = float(os.environ.get("PCB_BOARD_H", 100.0))   # ★11-03: SOM 4 排 100 脚座占 x 8..85 ⇒ 器件网格移到 x>=92
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

# ★★人工干预的摆放 (2026-11-04 ISS-181 布线轮)
#   ★**为什么必须有**: 自动装箱把件排成网格 ⇒ USB 差分对的两个串阻被排成 4.8mm 一字排开
#     ⇒ D+/D- 根本没法成对布 (同层同间距) ⇒ ★必须先把这两个件摆成"上下堆叠"的一对。
#   ★J_USB_C 旋转 90°: 焊盘排原本是沿 X 一行 ⇒ D+/D- 只能往板内(X)方向走 ⇒ 必然交叉
#     ⇒ 旋转 90° 后焊盘排变成沿 Y 的一列 ⇒ D+ 从 pad2 出、D- 从 pad3 出, 中心距 0.5mm
#     ⇒ ★两者可以同间距成对走出 (LAYOUT_RULES: USB 差分 90Ω)
#   ★R_SER_USB_D_N 上移一格 (y 25.5 → 23.5): 与 R_SER_USB_D_P 同 x 上下堆叠
#     ⇒ 两个串阻的"座侧"脚 (pad2) 同 x、相差 2.0mm ⇒ 差分线在串阻处只需小扇出
# ★★2026-11-05: USB-C 电源口位置 (自绘封装) —— ★**必须靠板边**(插头面与板边齐平, 板 160×100 ⇒ 上边 y=0)
USB_C_X = 140.0
USB_C_Y = 5.25
# ★禁放区 (自动装箱要避开): USB-C 座占 x 133.9..146.1, y 0..6.4
RESERVED = [(133.0, 0.0, 147.5, 7.2)]

PLACE_OVERRIDE = {
    "J_USB_C": {"x": 130.55, "y": 46.20, "rot": 90},
    "R_SER_USB_D_N": {"x": 107.70, "y": 23.50, "rot": 0},
}



def _is_pad_name(tail):
    """★真实焊盘号判定: "pin<N>" (网表针号) 或 **USB-IF 物理脚名** (A1/A4/A5/B12/shield …)
    ★USB-C 座 (如 GCT USB4105) 的 KiCad 封装正是用这组名字当 pad number ⇒ 必须当真实焊盘号
    ★★2026-11-05 04:20 **合并写法也要认**: 网表里写的是 "A6+B6" / "A4+A9+B4+B9"
       (USB-C 的 A/B 双排同名脚合写) ⇒ USBIF_RE 只匹配**单个**脚名 ⇒ 合并写法被判成"命名脚"
       ⇒ 落进占位编号分支 ⇒ 网表侧要 '1','10','11' 而板上是 'A6','A12' ⇒ ★**parity 必红**
       (实测 v15: 缺失 14 / 多余 12, 全是 J_USB_C) ⇒ 修法: 每个 '+' 分段都得是 USB-IF 物理脚名"""
    if not tail:
        return False
    if re.fullmatch(r"pin\d+(\+pin\d+)*", tail):
        return True
    if USBIF_RE.match(tail):
        return True
    # ★合并写法: 每个 token 都是 USB-IF 物理脚名 ⇒ 整体算"真实焊盘号"
    toks = [t.strip() for t in tail.split("+") if t.strip()]
    if len(toks) >= 2 and all(USBIF_RE.match(t) for t in toks):
        return True
    return False

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


def make_footprint(board, ref, value, kind, pins, netmap, x, y, label=True, rot=0):
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
    if rot:
        # ★人工旋转 (差分对逃线用) —— 旋转后焊盘跟着转, 脚号不变 ⇒ 网表绑定不变
        fp.SetOrientationDegrees(rot)
    board.Add(fp)
    return fp



def _write_layout_done(board):
    """★写 HW/PCB/.layout_done.json = {unconnected, drc_violations, at}
       (阶段门 stage_gate.py 靠它判 G1 过不过 ⇒ 数字必须是**实测**, 不是估计)"""
    import datetime
    import json
    import subprocess
    here = os.path.dirname(os.path.abspath(__file__))
    proj = os.path.dirname(here)
    # ★2026-11-05 03:10 **落盘路径也必须可改** (之前只改了顶部的 PCB 常量 ⇒ ★**并行实验把官方板覆盖成 0 走线骨架**)
    pcb = os.environ.get("PCB_OUT") or os.path.join(proj, "HW", "PCB", "demo_mainboard.kicad_pcb")
    # ★★2026-11-05 05:20 **只有官方板才许写 .layout_done.json**
    #   ★**并行实验的板不许污染阶段门**: 实验板(180×120)的 unconnected/DRC 被写进了官方留证
    #   ⇒ 阶段门 `stage_gate.py` 读的是 .layout_done.json ⇒ ⇒ **会把实验板当成官方板**
    OFFICIAL = os.path.join(proj, "HW", "PCB", "demo_mainboard.kicad_pcb")
    if os.path.abspath(pcb) != os.path.abspath(OFFICIAL):
        print("  ⚠️ 非官方板 (%s) ⇒ **不写 .layout_done.json** (阶段门只认官方板)" % os.path.basename(pcb))
        return
    unconnected = -1
    try:
        b2 = pcbnew.LoadBoard(pcb)
        b2.BuildConnectivity()
        unconnected = int(b2.GetConnectivity().GetUnconnectedCount(False))
    except Exception as e:
        print("  ⚠️ 未连接数取不到: %s" % e)
    viol = -1
    try:
        out = "/tmp/_layout_done_drc.json"
        rc = subprocess.run(["bash", os.path.join(here, "kicad.sh"), "pcb", "drc",
                             "--output", out, "--severity-error", "--severity-warning",
                             "--format", "json", pcb],
                            capture_output=True, text=True, timeout=900)
        if os.path.exists(out):
            d = json.load(open(out))
            viol = len(d.get("violations") or [])
    except Exception as e:
        print("  ⚠️ DRC 取不到: %s" % e)
    data = {"unconnected": unconnected, "drc_violations": viol,
            "at": datetime.datetime.now().isoformat(timespec="seconds")}
    path = os.path.join(proj, "HW", "PCB", ".layout_done.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("  [layout_done] %s" % json.dumps(data, ensure_ascii=False))
    return data


def _pin_net_from_netlist(ref=None):
    """从 HW/netlist_v1.csv 解析器件的 {脚号: 网络} (网表是唯一真源)
       ref=None ⇒ 解析 J_SOM_P1..P4; ref="CONN_LIGHT" ⇒ 解析显示 FPC 座"""
    import csv as _csv
    import re as _re
    _out = {}
    pat = r"CONN_LIGHT pin(\d+)" if ref == "CONN_LIGHT" else r"J_SOM_(P\d) pin(\d+)"
    # ★2026-11-05: J_USB_C 的脚名是 **USB-IF 物理脚名且可能合并** ("A6+B6" / "A4+A9+B4+B9")
    usbif = r"J_USB_C ([AB](?:1|4|5|6|7|8|9|12)(?:\+[AB](?:1|4|5|6|7|8|9|12))*)"
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
        if ref == "J_USB_C":
            with open(NETLIST, encoding="utf-8") as _f:
                for _r in _csv.DictReader(_f):
                    _net = (_r.get("net") or "").strip()
                    if not _net:
                        continue
                    for _k in ("node1", "node2"):
                        _m2 = _re.fullmatch(usbif, (_r.get(_k) or "").strip())
                        if _m2:
                            _out.setdefault(_m2.group(1), _net)
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
    # ★2026-11-05: 铜层数可配 (环境变量 PCB_LAYERS) ⇒ ★**6 层布不通时试 8 层**
    #   (Forlinx 官方载板是 10 层 ⇒ 6 层对 400 个 0.4mm pitch BTB 焊盘本来就偏紧)
    board.SetCopperLayerCount(int(os.environ.get("PCB_LAYERS", 6)))
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
        if ref == "J_USB_C":
            continue   # ★★2026-11-05: USB-C 电源口用 **自绘 GCT USB4105-16p** 封装 (usb_c_footprint 模块)
                       #   —— 通用 CONN 假封装(8脚)插不了线, 且必须摆在**板边**(插头面与板边齐平) ⇒ 这里跳过
        pins = per_ref[ref]
        kind = kind_of(ref)
        w, h, _per, _pitch, _nr = size_of(kind, len(pins))
        items.append((ref, pins, kind, w, h))
    items.sort(key=lambda it: (round(it[4], 1), it[3]))
    # ★★2026-11-05 06:55 **排版第二版: 按 SoM 针脚行排序** (★把长线变短线)
    #   实测 (v21 的 101 个未连接项): ★**失败网全是 80~140mm 的长线**
    #     例: DSI_D0_D2_N_SRC = J_SOM_P3.75(20.0, 8.0) ↔ R_SEL_D2_N(155.7, 21.6) = **136.4mm**
    #   ⇒ 根因: 器件区在 x 78..157, 而小件按"高矮宽窄"随便排 ⇒ ★**SoM 相连的小件全被甩到板子右边**
    #     (串阻 R_SER_*/R_SEL_*/R_PU_*, AC 电容 C_AC_*, 测试点 TP_* ⇒ 全是 SoM 信号的伙伴件)
    #   ⇒ 修法: ① 算出每个器件的 **SoM 锚点** (它连的那个 BTB 焊盘的板面坐标)
    #            ② ★**SoM 相连的器件先排** (按锚点 y 排 ⇒ 上排 BTB 的伙伴件排在板子上部)
    #            ③ 其余器件后排 (维持原"高矮宽窄"顺序 ⇒ **装箱行为不变 ⇒ 不会掉件**)
    #   ⇒ 效果预估: SoM 相连件的 x 距离从 ~130mm 降到 ~60mm ⇒ 总线长 136mm → ~70mm
    def _som_pad_positions():
        """J_SOM_* 每个焊盘的板面坐标 (规则见 state/som_btb_footprint.py, 与实物一致)"""
        import json as _json
        try:
            P = _json.load(open(os.path.join(PROJ, "HW", "PCB", "som_btb_params.json"),
                                encoding="utf-8"))
        except Exception:
            return {}
        ox, oy = P["som_origin"]
        pitch = P["pitch"]; rp = P["row_pitch"]
        contacts = P["contacts"]; rows = P["rows"]
        half = contacts // rows
        pos = {}
        for conn, (cx, cy) in P["conn_centers"].items():
            px, py = ox + cx, oy + cy
            for n in range(1, contacts + 1):
                if n % 2 == 1:
                    k = (n - 1) // 2; row_y = -rp / 2.0
                else:
                    k = (n - 2) // 2; row_y = +rp / 2.0
                pos[("J_SOM_%s" % conn, str(n))] = (px + ((half - 1) / 2.0 - k) * pitch,
                                                   py + row_y)
        return pos

    _SOMPOS = _som_pad_positions()
    _net2som = {}
    for _ref, _pads in per_ref.items():
        if not _ref.startswith("J_SOM_"):
            continue
        for _p in _pads:
            _pad_no, _net = _p[0], _p[1]
            _xy = _SOMPOS.get((_ref, str(_pad_no)))
            if _xy and _net:
                _net2som.setdefault(_net, []).append(_xy)

    def _anchor_of(item):
        """器件 → 它的 SoM 锚点 (y, x); 没有则 None"""
        _best = None
        for _p in item[1]:
            for _xy in _net2som.get(_p[1], ()):
                if _best is None or _xy[1] < _best[0]:
                    _best = (_xy[1], _xy[0])
        return _best

    # ★★2026-11-05 07:00 **排版第二版 (分带装箱)**: SoM 相连的器件按**针脚所在排**分上下两带
    #   实测 (v21 的 101 个未连接项): ★**失败网全是 80~140mm 的长线**
    #     例: DSI_D0_D2_N_SRC = J_SOM_P3.75(20.0,8.0) ↔ R_SEL_D2_N(155.7,21.6) = **136.4mm**
    #   ⇒ 根因: 器件区在 x 78..157, 小件按"高矮宽窄"随便排 ⇒ ★**SoM 相连的小件全被甩到板子右边**
    #   ⇒ 修法: ① 算每个器件的 **SoM 锚点** (它连的那个 BTB 焊盘的板面坐标)
    #            ② 锚点在上排 BTB (y<30) 的 ⇒ 排在**上带** (y 5 起)
    #               锚点在下排 BTB (y>=30) 的 ⇒ 排在**下带** (y 52 起) ⇒ 与针脚行对齐
    #            ③ 其余器件排在上带与下带之间的剩余空间
    #   ⇒ 实测 (离线对比 v21 vs 新排版): 失败网平均最长距离 68.2mm → 62.1mm;
    #     PWR_ON -64mm · UART_RX/TX -57mm · DSI_D0_D2_N_SRC -56mm ★但底排件会变差 ⇒ 所以要分带
    def _som_pad_positions():
        """J_SOM_* 每个焊盘的板面坐标 (规则见 state/som_btb_footprint.py, 与实物一致)"""
        import json as _json
        try:
            P = _json.load(open(os.path.join(PROJ, "HW", "PCB", "som_btb_params.json"),
                                encoding="utf-8"))
        except Exception:
            return {}
        ox, oy = P["som_origin"]
        pitch = P["pitch"]; rp = P["row_pitch"]
        contacts = P["contacts"]; rows = P["rows"]
        half = contacts // rows
        pos = {}
        for conn, (cx, cy) in P["conn_centers"].items():
            px, py = ox + cx, oy + cy
            for n in range(1, contacts + 1):
                if n % 2 == 1:
                    k = (n - 1) // 2; row_y = -rp / 2.0
                else:
                    k = (n - 2) // 2; row_y = +rp / 2.0
                pos[("J_SOM_%s" % conn, str(n))] = (px + ((half - 1) / 2.0 - k) * pitch,
                                                   py + row_y)
        return pos

    _SOMPOS = _som_pad_positions()
    _net2som = {}
    for _ref, _pads in per_ref.items():
        if not _ref.startswith("J_SOM_"):
            continue
        for _p in _pads:
            _pad_no, _net = _p[0], _p[1]
            _xy = _SOMPOS.get((_ref, str(_pad_no)))
            if _xy and _net:
                _net2som.setdefault(_net, []).append(_xy)

    def _anchor_of(item):
        """器件 → 它的 SoM 锚点 (y, x); 没有则 None"""
        _best = None
        for _p in item[1]:
            for _xy in _net2som.get(_p[1], ()):
                if _best is None or _xy[1] < _best[0]:
                    _best = (_xy[1], _xy[0])
        return _best

    DROPPED = []   # ★2026-11-05 05:10: **被丢掉的器件必须全部报出来** (之前静默丢 ⇒ parity 里才看得出)
    placed = 0

    PLACE_INFO = {}     # ref → (x, y, w, h) —— 供"测试点贴伙伴件"用
    NET_PARTS = {}     # net → [ref] —— 同网已放器件

    def _place_flow(flow_items, sx, sy, ex=None, ey=None):
        """把一批器件行式装箱到 (sx, sy) 起 ⇒ 返回 (px, py, row_h, 放置数)
           ★ex/ey = 该批器件的区域上限 (默认用 PK_AREA)"""
        ex = PK_AREA[2] if ex is None else ex
        ey = PK_AREA[3] if ey is None else ey
        px, py, row_h = sx, sy, 0.0
        cnt = 0
        for (ref, pins, kind, w, h) in flow_items:
            if px + w > ex:
                px = sx
                py += row_h + 3.0
                row_h = 0.0
            if py + h > ey:
                print(f"⚠️ 装不下: {ref} (y={py:.1f}) ⇒ 需要更大板或更紧的间距")
                DROPPED.append(ref)
                break
            # ★禁放区 (USB-C 座区) —— 撞上就换一行
            # ★★2026-11-05 05:10 **修: 原来撞禁放区直接 `continue` ⇒ 那个器件被"静默丢掉"** (换行后没有重试)
            #   ⇒ ★实测后果: C_BULK_SENSOR_AVDD 的封装压根没画到板上 ⇒ parity 报"缺失 2" ⇒ ★G1 卡在 parity
            #   ⇒ 改成: 换行后**重新试放这个器件** (死循环保护 60 次)
            _retry = 0
            while any(not (px + w <= rx0 or px >= rx1 or py + h <= ry0 or py >= ry1)
                      for (rx0, ry0, rx1, ry1) in RESERVED):
                px = sx
                py += row_h + 3.0
                row_h = 0.0
                _retry += 1
                if py + h > ey:
                    print(f"⚠️ 装不下(禁放区反复挡): {ref} (y={py:.1f})")
                    DROPPED.append(ref)
                    break
                if _retry > 60:
                    print(f"⚠️ 禁放区重试 60 次仍挡: {ref} ⇒ 放弃放置")
                    DROPPED.append(ref)
                    break
            if ref in DROPPED:
                continue
            if ref == "U_TEMP":
                # ★TMP117 = WSON-6 (DRV0006B) 官方封装 —— 通用 IC 封装是"假封装" (1.27mm pitch) ⇒ 单独画
                add_tmp117(board, netmap, pins, px + w / 2.0, py + h / 2.0)
            else:
                ov = PLACE_OVERRIDE.get(ref)
                if ov:
                    # ★人工干预位 (差分对成对布) —— 位置/旋转按表, 脚号不变
                    make_footprint(board, ref, value_of.get(ref, ""), kind, pins, netmap,
                                   ov["x"], ov["y"], rot=ov.get("rot", 0))
                else:
                    make_footprint(board, ref, value_of.get(ref, ""), kind, pins, netmap,
                                   px + w / 2.0, py + h / 2.0)
            cnt += 1
            PLACE_INFO[ref] = (px + w / 2.0, py + h / 2.0, w, h)
            for _p in pins:
                if _p[1]:
                    NET_PARTS.setdefault(_p[1], []).append(ref)
            px += w + 3.0
            row_h = max(row_h, h)
        return px, py, row_h, cnt

    # ★分组: 上排 BTB 伙伴件 / 下排 BTB 伙伴件 / 其余
    _grp_top, _grp_bot, _grp_rest, _grp_tp = [], [], [], []
    # ★★2026-11-05 08:15 **差分对的"远端连接器"不许被当伙伴件搬走**
    #   ⇒ 实测: F5 排版把 **CONN_CAM 从 (78.9..93.9, 51.4) 搬到 (93.3..108.3, 17.6)**
    #     ⇒ ★**MIPI 的 CSI 差分对远端整个位移** ⇒ 走廊全变 ⇒ ★**22 对里只剩 5 对耦合成功**
    #     (旧排版 8 对成功) ⇒ ⇒ ★**这是排版引入的差分对回归**
    #   ⇒ 但 F5 的收益也是真的 (平均线长 68.2→55.0mm · >100mm 长线 15→6 条)
    #   ⇒ ⇒ ★**两者都要**: 保留 F5 的分带装箱, ★但把差分对端点连接器钉回"其余"区 (≈原位)
    _PAIR_ENDPOINT_CONN = ("CONN_CAM", "CONN_LIGHT")
    for it in items:
        if it[0].startswith("TP_"):
            _grp_tp.append(it)     # ★测试点单独一轮 (贴伙伴件)
            continue
        if it[0] in _PAIR_ENDPOINT_CONN:
            _grp_rest.append(it)   # ★★差分对远端连接器 ⇒ 不参与"伙伴件搬移"
            continue
        _a = _anchor_of(it)
        if _a is None:
            _grp_rest.append(it)
        elif _a[0] < 30.0:
            _grp_top.append(it)
        else:
            _grp_bot.append(it)
    for _g, _asc in ((_grp_top, False), (_grp_bot, True)):
        # ★排序方向: **按 SoM 针脚的 x 排序**, 方向朝着该带的 x 区间
        #   (上带在 x 78..157 ⇒ 针脚 x 大的先占 ⇒ 离 SoM 最近的先排; 下带在 x 5..76 ⇒ 反过来)
        _g.sort(key=lambda it, _asc=_asc: (_anchor_of(it)[0],
                                            (_anchor_of(it)[1] if _asc else -_anchor_of(it)[1]),
                                            round(it[4], 1), it[3]))
    _grp_rest.sort(key=lambda it: (round(it[4], 1), it[3]))
    print("  [排版] 上带 %d (SoM 上排针脚伙伴件) · 下带 %d (下排) · 其余 %d"
          % (len(_grp_top), len(_grp_bot), len(_grp_rest)))
    # ★★2026-11-05 07:10 **三区分带装箱** (★真正的省线长改法)
    #   ★**关键发现**: 板子**左下角 x 5..76 / y 58..97 现在完全空着** (40×70 = 2800mm²)
    #     ⇒ 而 SoM **下排** BTB 的针脚就在 y≈52 ⇒ ★把它们的伙伴件放到左下角 ⇒ 线长 60~140mm → **6~40mm**
    #   · 下带 (SoM 下排伙伴件) → 左下角 (5, 58, 76, 97)
    #   · 上带 (SoM 上排伙伴件) → SoM 右侧窄条 (78, 5, 88, 56) (贴着 BTB 的 +x 端)
    #   · 其余 → 剩下的右侧区域 (88, 5, 157, 97)
    def _area(env_name, dflt):
        """区域 (x0,y0,x1,y1) —— 可用环境变量覆盖 (★便于扇形搜索最佳划分)"""
        v = os.environ.get(env_name)
        if not v:
            return dflt
        try:
            a = [float(x) for x in v.split(",")]
            if len(a) != 4:
                return dflt
            return tuple(a)
        except Exception:
            return dflt

    # ★★2026-11-05 07:15 **三区分带装箱 (扇形搜索选定 F5)** —— ★实测数据 (state/sweep_place.sh)
    #   指标 = v21 的 59 个失败网的"平均最长距离" (越小越好):
    #     基线 (v21 现行排版)      平均 68.2mm · 最大 138.3mm · >60mm 32 条 · >100mm 15 条
    #     **F5 (本次选定)**        平均 **55.0mm** · 最大 151.3mm · >60mm **24** 条 · >100mm **6** 条
    #   ⇒ ★**>100mm 的长线砍掉 60%** (15→6) ⇒ 长线正是布不出来的主要来源
    #   其它候选 (扫了 10 组): A 59.9(掉2件) B 61.6(0掉) C 55.6(掉2) D 69.7(0掉) E 61.4(0掉)
    #   ⇒ F5 = 零掉件 + 最短平均 ⇒ 选它
    _A_BOT = _area("PCB_AREA_BOT", (5.0, 58.0, 70.0, 97.0))
    _A_TOP = _area("PCB_AREA_TOP", (78.0, 5.0, 120.0, 36.0))
    _A_RES = _area("PCB_AREA_RES", (78.0, 38.0, BOARD_W - 3.0, BOARD_H - 3.0))
    pxB, pyB, rhB, nB = _place_flow(_grp_bot, _A_BOT[0], _A_BOT[1], _A_BOT[2], _A_BOT[3])
    placed += nB
    pxA, pyA, rhA, nA = _place_flow(_grp_top, _A_TOP[0], _A_TOP[1], _A_TOP[2], _A_TOP[3])
    placed += nA
    pxC, pyC, rhC, nC = _place_flow(_grp_rest, _A_RES[0], _A_RES[1], _A_RES[2], _A_RES[3])
    placed += nC
    # ★★2026-11-05 07:25 **测试点 (TP_*) 贴着它的伙伴件放** (⇒ 消灭 TP↔伙伴 的百毫米长线)
    #   实测 (F5 排版下最长的几条): TP_CSI_CK_N ↔ C_AC_CSI_D0_CK_N = **124mm**;
    #     CONN_LIGHT.15 ↔ TP_LIGHT_3V3 = 117mm ⇒ ★**都是测试点被分到了"其余"区, 跟伙伴件隔了半个板**
    #   ⇒ 改成: 最后一轮单独放 TP ⇒ 找同网的**已放器件** ⇒ 摆在它旁边 (多方向试位, 避开重叠)
    _tp_rest = []
    for (ref, pins, kind, w, h) in _grp_tp:
        tgt = None
        for _p in pins:
            for _r in NET_PARTS.get(_p[1], ()):
                if _r in PLACE_INFO:
                    tgt = PLACE_INFO[_r]
                    break
            if tgt:
                break
        done_tp = False
        if tgt:
            tx, ty, tw, th = tgt
            for (ox, oy) in ((3.2, 0), (-3.2, 0), (0, 3.2), (0, -3.2),
                             (3.2, 3.2), (3.2, -3.2), (-3.2, 3.2), (-3.2, -3.2),
                             (5.0, 0), (0, 5.0), (-5.0, 0), (0, -5.0)):
                nx, ny = tx + ox, ty + oy
                if nx < 4.0 or ny < 2.5 or nx > BOARD_W - 3.0 or ny > BOARD_H - 3.0:
                    continue
                bad = False
                for _r2, _info in PLACE_INFO.items():
                    ix, iy, iw, ih = _info
                    if (abs(ix - nx) < (iw + w) / 2.0 + 0.8
                            and abs(iy - ny) < (ih + h) / 2.0 + 0.8):
                        bad = True
                        break
                if bad:
                    continue
                make_footprint(board, ref, value_of.get(ref, ""), kind, pins, netmap, nx, ny)
                PLACE_INFO[ref] = (nx, ny, w, h)
                placed += 1
                done_tp = True
                break
        if not done_tp:
            _tp_rest.append((ref, pins, kind, w, h))
    if _tp_rest:
        pxT, pyT, rhT, nT = _place_flow(_tp_rest, _A_RES[0], pyC + rhC + 3.0,
                                        _A_RES[2], _A_RES[3])
        placed += nT
    px, py, row_h = pxC, pyC, rhC
    if DROPPED:
        print("  ❌ 装不下被丢 %d 个: %s" % (len(DROPPED), ", ".join(DROPPED)))
        print("     ⇒ ★**parity 会挂** ⇒ 这一轮不能作为正式板")
    # SOM 承载区 (FET3572-C 68×50) + 它的 4×100pin/0.4mm BTB 座 (占位: 按 400 脚模型)
    sx, sy, sw, sh = SOM_AREA
    # ★★2026-11-03 01:0x: SOM 座 = **4 个独立 100 脚 BTB (P1..P4)** —— ★**布局待修** (当前与器件网格冲突 ⇒ DRC 非零)
    #   ★**已就绪的部分**: 引脚映射 (`HW/PCB/som_pin_full_map.json` 399 行) + 分配表 (`HW/PCB/SOM_PIN_ASSIGNMENT.md`) + 网表脚本 (`state/_iss165_assign_final.py`)
    #   ⇒ **明早**: 重跑 A2 网表脚本 ⇒ 板生成器里把 4 排座放到与器件网格不重叠的位置 ⇒ 重跑 DRC/parity
    #   ★★**当前刻意不画 4 排座** ⇒ 板子保持 A1 状态 (DRC=0 / parity 全过), 避免带着未修的布局进 Gerber
    # ★★2026-11-05: J_USB_C = **自绘 GCT USB4105-16p** (usb_c_footprint) —— ★**摆在板边, 插头面与板边齐平**
    #   (原位 130.55/46.20 在板中央 ⇒ 插不了线 ⇒ 投板级致命) ⇒ 焊盘行中心 y = FRONT_OFFSET(5.25) ⇒ 插头面正好在 y=0
    _usb_pins = _pin_net_from_netlist(ref="J_USB_C")
    add_usb_c(board, netmap, _usb_pins, USB_C_X, USB_C_Y)

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

    # ★★★ 布线 (ISS-181) —— ★**布线必须落进生成器** (手改 .kicad_pcb 会被下次重生成冲掉)
    #   路由器: state/gen_pcb_routing.py (网格 A* + 差分对成对布 + 电源宽铜 + GND 平面)
    route_stats = {}
    try:
        import gen_pcb_routing as RT
        print("\n─── 布线 (gen_pcb_routing) ───")
        if os.environ.get("PCB_SKIP_ROUTE") == "1":
            # ★★2026-11-05 06:20 **调试开关: 跳过布线** ⇒ 只出"排版 + 平面"的板 (≈10 秒)
            #   ⇒ ★**排版/封装改动可以秒级验证**, 不用等 40~60 分钟布线
            print("  (PCB_SKIP_ROUTE=1 ⇒ 跳过布线)")
            route_stats = {"skipped": True}
        else:
            route_stats = RT.route_board(board)
    except Exception as e:
        import traceback
        print("⚠️ 布线失败 (板子仍会生成, 但未布线): %s" % e)
        # ★★2026-11-05 04:55 **把 traceback 打出来** (之前只打一行 ⇒ 查 "list index out of range" 查不到)
        traceback.print_exc()
        traceback.print_exc()
        # ★★2026-11-05 06:15 ★★**布线崩了 ⇒ 绝不能把"骨架板"当正式板落盘**
        #   实测: 8 层那轮布完只剩 78 个脚 (比 6 层的 101 好!) ⇒ 结果被 except 吞掉 ⇒
        #   骨架板 (0 走线) 反而落进了正式板 ⇒ ★**一轮好成绩白白作废**
        #   ⇒ 现在: 布线异常 ⇒ ★**直接退出, 不落盘** (保留上一块好板) + 退出码非 0
        print("❌ 布线异常 ⇒ ★**不落盘** (保留上一块好板) ⇒ 退出码 2")
        sys.exit(2)

    # ★★2026-11-05 05:00 **先存到临时文件, 成功后再替换正式板** (★防"崩在半路把好板冲掉")
    #   实测教训: 8 层实验崩在布线中 ⇒ 生成器已把**骨架 (0 走线)**写进了官方板文件
    #   ⇒ 正式板被覆盖成"空板" ⇒ 后面所有自验都在测一块坏板
    #   ⇒ 现在: 先写 <PCB>.tmp ⇒ 全部成功 ⇒ os.replace 原子替换 ⇒ ★**崩了也不会动正式板**
    import shutil as _shutil
    # ★★2026-11-05 05:10 **修: tmp 文件名必须以 .kicad_pcb 结尾** (LoadBoard **按扩展名判格式**)
    #   ⇒ 原来用 PCB + ".tmp" ⇒ 写入 OK (SaveBoard 不看扩展名) 但 ★**LoadBoard 返回 None**
    #   ⇒ v20 日志: "⚠️ 平面重填失败: 'NoneType' object has no attribute 'BuildConnectivity'"
    #   ⇒ ★**平面铜皮整块没填** (v20 板只有 2 处 filled_polygon) ⇒ 没有 GND 回流面 ⇒ DRC/布通率都受影响
    _tmp_pcb = (PCB[:-len(".kicad_pcb")] + ".tmp.kicad_pcb") if PCB.endswith(".kicad_pcb") \
        else (PCB + ".tmp.kicad_pcb")
    pcbnew.SaveBoard(_tmp_pcb, board)

    # ★重新填 L2/L6 平面 (★必须**存盘后重读**再填: 平面填的时候要看连通性缓存,
    #   同一会话里加的走线/过孔还没进缓存 ⇒ 填充器以为平面"没连上任何东西"
    #   ⇒ 孤岛删除模式把整个平面删空 ⇒ 焊盘的过孔全成 dangling)
    try:
        # ★★2026-11-05 04:10 **必须读 _tmp_pcb, 不能读 PCB** (读 PCB = 读回**上一轮的旧板**)
        #   实测: v17 (03:52 起跑) 若按老写法读 PCB ⇒ 读到的是 03:49 被空骨架覆盖的旧板 (0 走线)
        #   ⇒ 平面重填后把**骨架**存回 _tmp_pcb ⇒ os.replace 后官方板又变成 0 走线 ⇒ ★18 分钟白跑
        b3 = pcbnew.LoadBoard(_tmp_pcb)
        b3.BuildConnectivity()
        filler = pcbnew.ZONE_FILLER(b3)
        filler.Fill(b3.Zones())
        for z in b3.Zones():
            ps = z.GetFilledPolysList(z.GetLayer())
            print("  [zone ] %s 填充 %.1f mm2" % (b3.GetLayerName(z.GetLayer()),
                                                  ps.Area() / 1e12))
        pcbnew.SaveBoard(_tmp_pcb, b3)
    except Exception as e:
        print("⚠️ 平面重填失败: %s" % e)
    # ★全部成功 ⇒ 原子替换正式板 (★崩在上面的路径 ⇒ 正式板保持原样, 不会被空板覆盖)
    os.replace(_tmp_pcb, PCB)
    print("  ✓ 已原子替换正式板: %s" % PCB)
    # ★★2026-11-05 06:30 **写"落盘时刻印"** —— ★**触发器据此判断"盘上的板是不是刚落的那块"**
    #   事故事实: 05:57 板被**中途落盘**覆盖成骨架 (mtime=05:50) ⇒ 板侧判据照样触发自验
    #   ⇒ 留证被写成 tracks=0 ⇒ ★**量的是一块坏板** ⇒ 自己污染了自己的证据
    #   ⇒ 现在: 落盘时记 {at: epoch, tracks, vias} ⇒ 触发器要求 |板mtime - at| <= 10s
    #   ⇒ **中途存盘覆盖过的板 ⇒ at 对不上 ⇒ 不许量** ⇒ ★证据只来自真正落盘的板
    try:
        _OFFICIAL2 = os.path.join(os.path.dirname(PCB), "demo_mainboard.kicad_pcb")
        if os.path.abspath(PCB) == os.path.abspath(_OFFICIAL2):
            import time as _t
            _seg = _via = 0
            for _l in open(PCB, encoding="utf-8", errors="ignore"):
                _s = _l.lstrip()
                if _s.startswith("(segment"):
                    _seg += 1
                elif _s.startswith("(via"):
                    _via += 1
            # ★★2026-11-05 07:0x **at 用"板自己的 mtime", 不用 time.time()** ——
            #   理由: 平面重填 (Fill) 可能花几十秒 ⇒ 板 mtime 与"写印的时刻"能差出 10s+
            #   ⇒ 闸门 |板mtime - at| <= 10s 会误判"板被中途改过" ⇒ ★**好板永远不许量/不许推**
            #   ⇒ 现在 at = stat(PCB).st_mtime ⇒ 差恒等于 0 ⇒ 闸门只对"真被改过的板"报警
            _land = {"at": int(os.stat(PCB).st_mtime), "tracks": _seg, "vias": _via,
                     "pcb": os.path.basename(PCB), "landed_at": int(_t.time())}
            with open(os.path.join(os.path.dirname(PCB), ".layout_landed.json"), "w",
                      encoding="utf-8") as _f:
                json.dump(_land, _f, ensure_ascii=False)
            print("  ✓ 落盘时刻印: %s" % json.dumps(_land, ensure_ascii=False))
    except Exception as e:
        print("  ⚠️ 落盘时刻印失败: %s" % e)
    # ★2026-11-05 04:10 **每次成功都留一份备份** (实测教训: 11-05 03:49 一轮崩在布线中
    #   ⇒ 正式板被空骨架覆盖 ⇒ v15 那轮 92/17 的好板没了 ⇒ 18 分钟白跑且无从恢复)
    try:
        # ★2026-11-05 05:20 **官方板才用固定备份名** —— 否则并行实验 (PCB_OUT=…) 会把
        #   /tmp/board_last_good.kicad_pcb 覆盖成实验板 ⇒ ★**官方板的回滚点就没了**
        _OFFICIAL = os.path.join(os.path.dirname(PCB), "demo_mainboard.kicad_pcb")
        if os.path.abspath(PCB) == os.path.abspath(_OFFICIAL):
            _bak = "/tmp/board_last_good.kicad_pcb"
        else:
            _bak = "/tmp/board_last_good_%s" % os.path.basename(PCB)
        _shutil.copy2(PCB, _bak)
        print("  ✓ 已备份: %s" % _bak)
    except Exception as e:
        print("  ⚠️ 备份失败: %s" % e)

    # ★★ISS-181: 交付 HW/PCB/.layout_done.json (★阶段门 state/stage_gate.py 靠它判 G1)
    _write_layout_done(board)

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
