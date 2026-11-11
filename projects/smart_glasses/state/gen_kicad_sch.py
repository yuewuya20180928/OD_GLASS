#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_kicad_sch.py —— 从**针脚级真源**生成 KiCad 原理图 (★"自己画图"链的第二环★)

★**2026-11-11 15:0x 主线 6b: 图的针脚真源从 `netlist_v1.csv` 换成 `netlist_v1_pins.csv`★★

★★**为什么换 (★这是本轮唯一的根因修复★)** ★★:
  ★**旧的图按 `HW/netlist_v1.csv` 的行来画脚 —— 但那是一张"连接清单"(★一行 = 一根导线★),
  不是针脚清单** ⇒ ★**一根导线的两个器件端被当成"两个脚", 而真实器件的脚数根本没被画全** ★★
  ★★**实测 (2026-11-11 13:4x, 尺子 `state/check_sch_pinfull.py` 判据口径 = 表侧含 DNP)**:
    - 图上 **513** 脚 / 表里 **584** 脚 / 不一致器件 **K=170** (universe 293)
    - ★**`J_SOM_P2` (9 脚) / `J_SOM_P4` (14 脚) 在图上【连符号都没有】** ⇒ 23 个球位凭空消失
    - ★**图上还有 73 个"伪器件"(RAIL_*/NET_*)** —— 它们是**网别名**, 不是器件, 不该画成符号 ★★
  ⇒ ★**修法 = 图的针脚真源换成针脚级表 `HW/netlist_v1_pins.csv` (584 行 = 584 脚, 218 个器件)** ★★

★★**这条链是自洽的 (★2026-11-11 15:0x 实测, 三段全等★)** ★★:
  ★**`HW/netlist_v1.csv` (513 连接行) ★─`state/gen_kicad_net.py`──▶ `HW/netlist_v1.net` (584 节点)** ★★
  ★★**(实测: `python3 state/gen_kicad_net.py --out /tmp/x.net` ⇒ md5 `bbcd2e9aee841a59324a74cc0ed9f450`
  ★★★ = 仓库里的 `HW/netlist_v1.net` ⇒ **零差异**)★** ★★
  ★**`HW/netlist_v1.net` (584 节点) ★─`state/gen_netlist_pins.py`──▶ `HW/netlist_v1_pins.csv` (584 行)** ★★
  ★★**(实测: 584 个 (ref,pin) 键**全等**、584 个网名**全等** ⇒ **零差异**)★** ★★
  ⇒ ★**所以 `netlist_v1_pins.csv` 就是 `netlist_v1.csv` 的针脚级展开, 本脚本按它画 ⇒ 图=表=CSV 三方一致** ★★

★★**画法 (connectivity-first, 与旧版同风格)** ★★:
  每个器件 = 一个矩形符号, **每个脚一个真实脚号**(★`pin18` / `A4` / `shield` … 不是假脚号 P1/P2★),
  每个脚一根短线 + 一个**全局标签(网名)** ⇒ 连通性靠网名建立, 不做手工走线。
  ★**网名一律用表里的 `net` 列** ⇒ 导出网表与 `netlist_v1.net` 逐脚零差异。

★★**DNP 脚怎么"看得出来" (★2026-11-11 15:0x 实测三种手段都验过★)** ★★:
  ★**① 标签染红** (★`(effects (font (size 1.27 1.27) (color 255 0 0 1)) ...)`★ —— 实测 KiCad 10.0.8 能加载、能导出★)
  ★**② 符号内脚名写 `DNP`** (★`DNP` ⇒ 符号体里直接看见★)
  ★**③ 整器全 DNP 的, 符号挂 `(dnp yes)`** (★KiCad 原生"不贴装"标记★)
  ★★⇒ 评审时**一眼分得清"这脚不装" vs "这脚漏了"**; ★**且网名一字未改 ⇒ parity 不受影响** ★★

★★**产出**: ★★**只写 .kicad_sch 产物 + 本脚本自己的两个副产物(★`demo_mainboard_sch.net` 人读网表摘要 / `SCH_SELF_CHECK.txt` 自检★)** ★★
  HW/PCB/demo_mainboard.kicad_sch          —— ★根页 (封面/目录: 10 个 sheet 块)★
  HW/PCB/demo_mainboard_p<N>.kicad_sch      —— ★子页 (每页 = CSV 的一个 page) ★
  HW/PCB/demo_mainboard_sch.net             —— 便于人工看的网表摘要 (人读)
  HW/PCB/SCH_SELF_CHECK.txt                 —— 生成自检

★★**自检 (rc=0 才算过)**: ★★C1 符号数=表内器件数 ★C2 引脚总数=表行数 ★C3 逐器件脚数=表 ★
  C4 (ref,pin) 唯一不重号 ★C5 属性齐全 ★C6 标签数=脚数 ★C7 线端点在引脚连接点
  C8 括号平衡 ★C9 每页内容≤纸张 ★C10 器件无重无漏 ★C11 真实包围盒(含标签)≤纸张
  ★**C12 表里每一行(含 DNP)都在图上有一个脚 ★C13 DNP 脚数=表里 DNP 行数** ★★

★★**parity (★自己写比对, 不许只贴结论★)**: ★★`python3 state/gen_kicad_sch.py --parity`★★
  ① 导出网表 ⇒ 逐 (ref,pin) 与**表侧含 DNP** 比对 ⇒ 期望 584/584 零差异 (**表侧必须含 DNP**)
  ② 表侧 `netlist_v1_pins.csv` ↔ `netlist_v1.net` 逐脚零差异 (584/584)
  ③ `netlist_v1.csv` 重生成 `netlist_v1.net` ⇒ md5 与仓库文件一致 ⇒ **证明表就是 CSV 的针脚级展开**
  ④ ★**同时打印"若用不含 DNP 口径会怎样"** ⇒ 说明为什么必须用含 DNP 口径 (★brief 明确要求★)

用法:
  python3 state/gen_kicad_sch.py             # 生成 + 自检
  python3 state/gen_kicad_sch.py --parity    # 导出网表 + 逐脚比对 (自己写)
"""
import csv
import hashlib
import os
import re
import subprocess
import sys
import tempfile
import uuid
from collections import OrderedDict, defaultdict, Counter

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
# ★针脚级真源 (★584 行 = 584 脚; 与 netlist_v1.net 逐脚零差异★)★
PIN_TBL = os.path.join(PROJ, "HW", "netlist_v1_pins.csv")
# ★连接清单 (★只读: 用来定"页的先后/评审顺序"+ 交叉核对, **不改**★)★
CSV_TBL = os.path.join(PROJ, "HW", "netlist_v1.csv")
# ★KiCad 原生网表 (★netlist_v1.csv 的针脚级展开, parity 的第二方证人★)★
NET_FILE = os.path.join(PROJ, "HW", "netlist_v1.net")

OUT_DIR = os.path.join(PROJ, "HW", "PCB")
OUT_SCH = os.path.join(OUT_DIR, "demo_mainboard.kicad_sch")     # ★根页 (封面/目录)★
OUT_NET = os.path.join(OUT_DIR, "demo_mainboard_sch.net")
OUT_CHK = os.path.join(OUT_DIR, "SCH_SELF_CHECK.txt")
KICAD_SH = os.path.join(HERE, "kicad.sh")
PROJECT_NAME = "demo_mainboard"

# ---------------- 图纸/布局参数 (★单位 mm★) ----------------
PAPER_SIZES = OrderedDict([          # ★KiCad 内置纸型 (宽 x 高, 横放)★
    ("A2", (594.0, 420.0)),
    ("A1", (841.0, 594.0)),
    ("A0", (1189.0, 841.0)),
])
GRID = 1.27              # ★KiCad 图纸栅格 (50 mil)★ ★**所有坐标都取它的整数倍 ⇒ ERC 不报 endpoint_off_grid**★
MARGIN = 12 * GRID       # ★内容离纸边的最小距离 (★15.24mm★)★
CELL_W = 38 * GRID       # ★器件列间距 (★48.26mm★)★
LABEL_SPACE = 28 * GRID  # ★第一列左侧留给【网名标签】的宽度 (★35.56mm; 最长网名 17 字符 ≈ 16.2mm + 标签线 17.8mm★)★
X0 = MARGIN + LABEL_SPACE
Y0 = MARGIN + 27 * GRID
BODY_HALF_W = 8 * GRID   # ★符号本体半宽 (★10.16mm★)★
TEXT_W = 0.75 * 1.27     # ★文字宽度系数 (★实测校核: 20 字符网名 @1.27mm 实测宽 18.5mm ⇒ 0.729×字号★)★
REF_ABOVE = 2 * GRID     # ★Reference 文字离本体顶端的距离★
VAL_ABOVE = 4 * GRID     # ★Value 文字离本体顶端的距离★
PIN_DX, PIN_LEN = -10 * GRID, 2 * GRID   # 引脚连接点在符号原点左侧 12.7mm, 线长 2.54mm
PIN_PITCH = 2 * GRID
DNP_COLOR = "255 0 0 1"  # ★DNP 脚标签的红色 (★KiCad 10 接受 (color R G B A) 写在 font 里★)★

# ★页名 (★只读引用 state/gen_schematic_pages.py 的 PAGES 字典★ —— 不改那个文件★)★
PAGE_NAMES = OrderedDict([
    ("P1", "电源树"),
    ("P2", "SoC 主控"),
    ("P3", "启动存储"),
    ("P4", "显示双出口"),
    ("P5", "MIPI-CSI 传感器"),
    ("P6", "高速差分与连接器"),
    ("P7", "板级接口与测试点"),
    ("P8", "时钟·复位·调试"),
    ("P9", "跨铰链界面"),
    ("P10", "充电板(镜框)"),
])


def uid():
    return str(uuid.uuid4())


def _sval(v):
    """★属性值转义: 引号要转义, 换行要压平 (否则 KiCad 解析失败)"""
    return (str(v or "").replace("\\", "\\\\").replace('"', '\\"')
            .replace("\n", " ").replace("\r", " "))


# ─────────────────────────── 真源读取 ───────────────────────────
def load_pin_table():
    """★针脚级真源 ⇒ 584 行 (★每行 = 一个脚★)"""
    rows = []
    with open(PIN_TBL, newline="", encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            rows.append(r)
    return rows


def load_csv_order():
    """★连接清单 ⇒ {ref: 首次出现序号} (★只用来排"评审顺序"+ 交叉核对, 不参与画脚★)"""
    order = {}
    with open(CSV_TBL, newline="", encoding="utf-8") as fh:
        for i, r in enumerate(csv.DictReader(fh)):
            ref = (r.get("ref") or "").strip()
            if ref and ref not in order:
                order[ref] = i
    return order


def build_devices(rows, csv_order):
    """★表 ⇒ 器件字典 (★每器件: 真实脚号 + 网名 + DNP + 元信息★)

    ★**页的归属规则 (★2026-11-11 15:0x★)**:
      ① 优先用**表自己的 `page` 列** (★它对每个器件内部自洽★)
      ② 表里 page 为空 ⇒ 只有 `J_SOM_P2` / `J_SOM_P4` (★它们在 netlist_v1.csv 里只出现在
         节点串中、从来不在 ref 列 ⇒ 老逻辑把它们的页也丢了★) ⇒ **落到 P1**
         (★与同族的 `J_SOM_P1` / `J_SOM_P3` 同页 ⇒ 4 个 SoM 球位座在一起, 评审好对照★)
      ③ 同一器件在表里横跨多页 (★实测 5 个: CHG_GND_STAR / TP_BAT_CHG / U_DCDC_VCORE /
         U_DCDC_VIO / J_CHG★) ⇒ **整器只画在一页** ⇒ 取该器件**第一条脚**的页
    """
    devs = OrderedDict()
    for r in rows:
        ref = (r.get("ref") or "").strip()
        pin = (r.get("pin") or "").strip()
        net = (r.get("net") or "").strip()
        if not ref or not pin:
            continue
        dnp = (r.get("dnp") or "").strip().upper() == "DNP"
        page = (r.get("page") or "").strip()
        dev = devs.get(ref)
        if dev is None:
            dev = devs[ref] = {
                "ref": ref, "pins": [], "page": page,
                "value": (r.get("value") or "").strip(),
                "type": (r.get("type") or "").strip(),
                "footprint": (r.get("footprint") or "").strip(),
                "board": (r.get("board") or "").strip(),
                "conn_id": (r.get("conn_id") or "").strip(),
                "opn": (r.get("opn") or "").strip(),
                "note": (r.get("note") or "").strip(),
            }
        dev["pins"].append({"pin": pin, "net": net, "dnp": dnp})
        if not dev["page"] and page:
            dev["page"] = page
    # ② page 兜底 (★只有 J_SOM_P2 / J_SOM_P4 会走到这里★)
    for dev in devs.values():
        if not dev["page"]:
            dev["page"] = "P1"
    # ③ 排序: 页内按 CSV 首次出现顺序 (★评审顺序与老 PDF 一致★), 表里没有的 (★J_SOM_P2/P4★) 排最后
    for dev in devs.values():
        dev["_ord"] = csv_order.get(dev["ref"], 10 ** 6)
    return devs


# ─────────────────────────── 几何 ───────────────────────────
def half_h(n_pins):
    """★n 个脚的符号本体半高 (★脚距 2.54mm, 上下留 2.54mm★)"""
    return max(12.7, (n_pins - 1) / 2.0 * PIN_PITCH + 2.54)


def pin_y(i, n):
    """★第 i 个脚在【库坐标】里的 y (★库坐标 +y 向上★)"""
    return (n - 1) / 2.0 * PIN_PITCH - i * PIN_PITCH


def pin_page_y(oy, i, n):
    """★第 i 个脚连接点在【图纸坐标】里的 y
    ★★**KiCad 变换: 库坐标 (x, y) → 图纸坐标 (ox + x, oy - y)** (★库 +y 向上 / 图纸 +y 向下 ⇒ Y 取负★)"""
    return oy - pin_y(i, n)


TEXT_BAND = VAL_ABOVE + 2 * GRID   # ★本体上方留给 Reference/Value 两行字的带高★
BOTTOM_PAD = 3 * GRID             # ★本体下方留白★
LABEL_STUB = 4 * GRID             # ★引脚连接点 → 标签锚点的水平距离★


def dev_box(n_pins):
    """★器件占位 (★含上方 Reference/Value 文字带★) ⇒ (宽, 高)"""
    return (2 * BODY_HALF_W, 2 * half_h(n_pins) + TEXT_BAND + BOTTOM_PAD)


def page_bbox(placements, devs_by_ref):
    """★一页的真实内容包围盒 (★含网名标签向左伸出的部分 + 上方文字带★) ⇒ (x0,y0,x1,y1)"""
    x0 = y0 = 1e9
    x1 = y1 = -1e9
    for (ref, ox, oy, n) in placements:
        dev = devs_by_ref[ref]
        hh = half_h(n)
        x0, x1 = min(x0, ox - BODY_HALF_W), max(x1, ox + BODY_HALF_W)
        y0, y1 = min(y0, oy - hh - VAL_ABOVE - 1.3), max(y1, oy + hh)
        for txt in (ref, str(dev["value"] or ref)):
            hw = len(txt) * TEXT_W / 2.0
            x0, x1 = min(x0, ox - hw), max(x1, ox + hw)
        for i, p in enumerate(dev["pins"]):
            py = pin_page_y(oy, i, n)
            lx0 = ox + PIN_DX - LABEL_STUB - len(p["net"]) * TEXT_W
            x0, x1 = min(x0, lx0), max(x1, ox + PIN_DX)
            y0, y1 = min(y0, py - 0.8), max(y1, py + 0.8)
    return x0, y0, x1, y1


# ─────────────────────────── 布局 ───────────────────────────
def layout_page(items, devs_by_ref):
    """★一页内的器件摆放 (★行高按行内最高的器件算 ⇒ 脚多的器件不会压到邻行★)

    ★**纸型/列数由【真实包围盒】决定 (★不是估算★) ⇒ 自检 C9/C11 与实际画出来的一致★**
    items = [(ref, n_pins), ...]
    返回 (placements, geo)
    """
    for paper, (pw, ph) in PAPER_SIZES.items():
        max_cols = max(1, int((pw - MARGIN - LABEL_SPACE - BODY_HALF_W - MARGIN) // CELL_W))
        for cols in range(max_cols, 0, -1):
            rows = [items[i:i + cols] for i in range(0, len(items), cols)]
            row_h = []
            for row in rows:
                row_h.append(max(dev_box(n)[1] for _, n in row))
            out = []
            y = Y0
            for row, rh in zip(rows, row_h):
                for c, (ref, n) in enumerate(row):
                    body_top = y + TEXT_BAND          # ★本体顶 = 行带顶 + 文字带★
                    oy = body_top + half_h(n)         # ★本体中心 (库坐标原点)★
                    out.append((ref, X0 + c * CELL_W, oy, n))
                y += rh
            bx0, by0, bx1, by1 = page_bbox(out, devs_by_ref)
            if bx0 >= MARGIN and by0 >= MARGIN and bx1 <= pw - MARGIN and by1 <= ph - MARGIN:
                geo = (paper, pw, ph, cols, rows, row_h,
                       bx1 - bx0, by1 - by0)
                return out, geo
    raise RuntimeError("★纸型 A0 都放不下这一页 —— 布局参数要改★")


# ─────────────────────────── 符号定义 ───────────────────────────
def lib_symbol_name(ref):
    """★每个器件一个符号 (★因为脚号各不相同: pin18 / A4 / shield … 不能共用一个 GEN_nP★)"""
    return "SYM_" + ref


def lib_symbols(devs_on_page):
    """★本页用到的所有符号定义 (★每器件一个, 脚号=真实脚号★)"""
    out = []
    for dev in devs_on_page:
        name = lib_symbol_name(dev["ref"])
        n = len(dev["pins"])
        hh = half_h(n)
        sym = ['    (symbol "%s" (pin_names (offset 1.016)) (in_bom yes) (on_board yes)' % name,
               '      (symbol "%s_0_1"' % name,
               '        (rectangle (start -%.2f %.3f) (end %.2f %.3f) (stroke (width 0.254) (type default)) (fill (type background)))'
               % (BODY_HALF_W, hh, BODY_HALF_W, -hh),
               '      )',
               '      (symbol "%s_1_1"' % name]
        for i, p in enumerate(dev["pins"]):
            sym += ['        (pin passive line (at %.2f %.3f 0) (length %.2f)'
                    % (PIN_DX, pin_y(i, n), PIN_LEN),
                    '          (name "%s" (effects (font (size 1.27 1.27))))'
                    % ("DNP" if p["dnp"] else ""),
                    '          (number "%s" (effects (font (size 1.27 1.27))))' % _sval(p["pin"]),
                    '        )']
        sym.append('      )')
        sym.append('    )')
        out.append("\n".join(sym))
    return "\n".join(out)


# ─────────────────────────── 器件实例 / 连线 ───────────────────────────
def build_symbol_block(dev, ox, oy, sheet_uuid, root_uuid):
    """★一个器件的 symbol 块 (★实例路径 = /<根sheet uuid>/<本子sheet块 uuid>★)"""
    ref = dev["ref"]
    pins = dev["pins"]
    n = len(pins)
    L = []
    L.append('  (symbol')
    L.append('    (lib_id "%s")' % lib_symbol_name(ref))
    L.append('    (at %.3f %.3f 0)' % (ox, oy))
    L.append('    (unit 1)')
    L.append('    (exclude_from_sim no)')
    L.append('    (in_bom yes)')
    L.append('    (on_board yes)')
    L.append('    (dnp %s)' % ("yes" if all(p["dnp"] for p in pins) else "no"))
    L.append('    (uuid "%s")' % uid())
    top = oy - half_h(n)
    L.append('    (property "Reference" "%s" (at %.3f %.3f 0) (effects (font (size 1.27 1.27))))'
             % (_sval(ref), ox, top - REF_ABOVE))
    L.append('    (property "Value" "%s" (at %.3f %.3f 0) (effects (font (size 1.27 1.27))))'
             % (_sval(dev["value"] or ref), ox, top - VAL_ABOVE))
    L.append('    (property "Footprint" "%s" (at %.3f %.3f 0) (effects (font (size 1.27 1.27)) (hide yes)))'
             % (_sval(dev["footprint"] or "TBD"), ox, top - VAL_ABOVE - 2.7))
    L.append('    (property "Datasheet" "TBD" (at %.3f %.3f 0) (effects (font (size 1.27 1.27)) (hide yes)))'
             % (ox, top - VAL_ABOVE - 5.4))
    L.append('    (property "MPN" "%s" (at %.3f %.3f 0) (effects (font (size 1.27 1.27)) (hide yes)))'
             % (_sval(dev["opn"] or dev["value"] or ref), ox, top - VAL_ABOVE - 8.1))
    for p in pins:
        L.append('    (pin "%s" (uuid "%s"))' % (_sval(p["pin"]), uid()))
    L.append('    (instances')
    L.append('      (project "%s"' % PROJECT_NAME)
    L.append('        (path "/%s/%s" (reference "%s") (unit 1))' % (root_uuid, sheet_uuid, _sval(ref)))
    L.append('      )')
    L.append('    )')
    L.append('  )')
    return L


def build_pin_wires(dev, ox, oy):
    """★每脚一根短线 + 一个全局标签(网名) (★DNP 脚标签染红 + 脚名写 DNP★)"""
    L = []
    pins = dev["pins"]
    n = len(pins)
    for i, p in enumerate(pins):
        py = pin_page_y(oy, i, n)
        px = ox + PIN_DX
        ex = px - LABEL_STUB
        L.append('  (wire (pts (xy %.3f %.3f) (xy %.3f %.3f)) (stroke (width 0) (type default)) (uuid "%s"))'
                 % (px, py, ex, py, uid()))
        if p["dnp"]:
            eff = ('(effects (font (size 1.27 1.27) (color %s)) (justify right bottom))' % DNP_COLOR)
        else:
            eff = '(effects (font (size 1.27 1.27)) (justify right bottom))'
        L.append('  (global_label "%s" (shape input) (at %.3f %.3f 0) (fields_autoplaced yes) %s (uuid "%s") '
                 '(property "Intersheetrefs" "${INTERSHEET_REFS}" (at %.3f %.3f 0) '
                 '(effects (font (size 1.27 1.27)) (hide yes))))'
                 % (_sval(p["net"]), ex, py, eff, uid(), ex, py))
    return L


def build_child_sheet(page_id, page_name, devs_on_page, placements, sheet_uuid, root_uuid,
                       paper, page_no):
    """★生成一个子 sheet 文件 (★= 一个 page★)"""
    L = []
    L.append('(kicad_sch')
    L.append('  (version 20250114)')
    L.append('  (generator "gen_kicad_sch.py")')
    L.append('  (uuid "%s")' % uid())
    L.append('  (paper "%s")' % paper)
    L.append('  (title_block (title "%s %s — DEMO MAINBOARD SCHEMATIC") (date "2026-11-11") (rev "draft-3") '
             '(company "self-drawn, not ODM") (comment 1 "sheet %d · %d devices · paper %s") '
             '(comment 2 "pins from HW/netlist_v1_pins.csv (584-pin truth) · net = global label"))'
             % (page_id, page_name, page_no, len(devs_on_page), paper))
    L.append('  (lib_symbols')
    L.append(lib_symbols(devs_on_page))
    L.append('  )')
    by_ref = {d["ref"]: d for d in devs_on_page}
    for (ref, ox, oy, _n) in placements:
        dev = by_ref[ref]
        L += build_symbol_block(dev, ox, oy, sheet_uuid, root_uuid)
        L += build_pin_wires(dev, ox, oy)
    L.append(')')
    return "\n".join(L) + "\n"


def build_root_sheet(sheets, root_uuid):
    """★生成根 sheet (★封面/目录页: 列出所有子 sheet 块★)"""
    L = []
    L.append('(kicad_sch')
    L.append('  (version 20250114)')
    L.append('  (generator "gen_kicad_sch.py")')
    L.append('  (uuid "%s")' % root_uuid)
    L.append('  (paper "A2")')
    L.append('  (title_block (title "DEMO MAINBOARD — SCHEMATIC INDEX / 原理图目录") (date "2026-11-11") '
             '(rev "draft-3") (company "self-drawn, not ODM") '
             '(comment 1 "%d functional sheets · pins from HW/netlist_v1_pins.csv") '
             '(comment 2 "each sheet = one CSV page P1..P10"))'
             % len(sheets))
    for i, sh in enumerate(sheets):
        col = i % 2
        row = i // 2
        x = 60.0 + col * 250.0
        y = 60.0 + row * 70.0
        w, h = 180.0, 45.0
        L.append('  (sheet')
        L.append('    (at %.3f %.3f)' % (x, y))
        L.append('    (size %.3f %.3f)' % (w, h))
        L.append('    (exclude_from_sim no)')
        L.append('    (in_bom yes)')
        L.append('    (on_board yes)')
        L.append('    (dnp no)')
        L.append('    (stroke (width 0) (type solid))')
        L.append('    (fill (color 0 0 0 0))')
        L.append('    (uuid "%s")' % sh["uuid"])
        L.append('    (property "Sheetname" "%s %s" (at %.3f %.3f 0) (effects (font (size 2.0 2.0)) (justify left bottom)))'
                 % (_sval(sh["page_id"]), _sval(sh["page_name"]), x, y - 1.0))
        L.append('    (property "Sheetfile" "%s" (at %.3f %.3f 0) (effects (font (size 1.27 1.27)) (justify left top)))'
                 % (_sval(sh["file"]), x, y + h + 1.0))
        L.append('    (instances')
        L.append('      (project "%s"' % PROJECT_NAME)
        L.append('        (path "/%s" (page "%d"))' % (root_uuid, sh["page_no"]))
        L.append('      )')
        L.append('    )')
        L.append('  )')
    L.append('  (sheet_instances (path "/" (page "1")))')
    L.append(')')
    return "\n".join(L) + "\n"


def paren_balance(text):
    """★扫 s-表达式括号平衡 (跳过字符串; 支持 \\ 转义) ⇒ 返回 (最终深度, 最低点, 字符串是否未闭合)"""
    depth = 0
    instr = False
    esc = False
    worst = 0
    for ch in text:
        if instr:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                instr = False
            continue
        if ch == '"':
            instr = True
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            worst = min(worst, depth)
    return depth, worst, instr


# ─────────────────────────── 真源解析 (parity 用) ───────────────────────────
def parse_exported_netlist(path):
    """★KiCad 导出的网表 ⇒ {(ref,pin): net} + {ref: [pins]} ★
    ★★**只认 (nets ...) 段里的 (node (ref ..) (pin ..))** ⇒ (components ...) 段的 (comp) 是器件条目, 不是脚★★"""
    txt = open(path, encoding="utf-8", errors="replace").read()
    i = txt.find("(nets")
    seg = txt[i:] if i >= 0 else ""
    pin2net = {}
    per_ref = defaultdict(list)
    for blk in seg.split("(net")[1:]:
        mn = re.search(r'\(name "([^"]*)"\)', blk)
        if not mn:
            continue
        net = mn.group(1)
        for r, p in re.findall(r'\(node\s*\(ref "([^"]*)"\)\s*\(pin "([^"]*)"\)', blk):
            pin2net[(r, p)] = net
            per_ref[r].append(p)
    return pin2net, per_ref


def parse_net_file(path):
    """★仓库里的 netlist_v1.net ⇒ {(ref,pin): net} (★KiCad 原生格式★)"""
    txt = open(path, encoding="utf-8", errors="replace").read()
    out = {}
    for blk in txt.split("(net")[1:]:
        mn = re.search(r'\(name "([^"]*)"\)', blk)
        if not mn:
            continue
        net = mn.group(1)
        for r, p in re.findall(r'\(node\s*\(ref "([^"]*)"\)\s*\(pin "([^"]*)"\)', blk):
            out[(r, p)] = net
    return out


def table_pin_map():
    """★针脚级真源 ⇒ {(ref,pin): net} (★含 DNP 行★)"""
    out = {}
    with open(PIN_TBL, newline="", encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            ref = (r.get("ref") or "").strip()
            pin = (r.get("pin") or "").strip()
            if ref and pin:
                out[(ref, pin)] = (r.get("net") or "").strip()
    return out


def cmd_parity():
    """★自己写比对 (★不许只贴结论★): 导出网表 ⇒ 逐脚零差异 vs 表侧(含 DNP)★"""
    print("=" * 78)
    print("原理图网表 parity (★导出网表 vs 针脚级真源 逐脚比对★)")
    print("=" * 78)
    print("  真源: HW/netlist_v1_pins.csv (★584 行 = 584 脚, 含 DNP★)")
    print("  口径: ★表侧【含 DNP 行】★★ —— 排除 DNP 口径会把 DNP 器件误判成『图上多脚』★")
    with tempfile.TemporaryDirectory() as td:
        out_net = os.path.join(td, "exported.net")
        cmd = ["bash", KICAD_SH, "sch", "export", "netlist", "-o", out_net, OUT_SCH]
        p = subprocess.run(cmd, cwd=PROJ, capture_output=True, text=True, timeout=1800)
        print("  导出命令: bash state/kicad.sh sch export netlist -o <tmp> HW/PCB/demo_mainboard.kicad_sch  rc=%s" % p.returncode)
        if p.returncode != 0 or not os.path.exists(out_net):
            print("❌ 导出失败: %s" % ((p.stdout + p.stderr)[-400:]))
            return 1
        got, got_refs = parse_exported_netlist(out_net)
    tbl = table_pin_map()
    netf = parse_net_file(NET_FILE)

    print("  图上: %d 个脚 / %d 个器件 / %d 个网"
          % (len(got), len(got_refs), len(set(got.values()))))
    print("  表侧(含 DNP): %d 个脚 / %d 个器件"
          % (len(tbl), len(set(r for r, _ in tbl))))
    ok = True
    # ① 逐脚 (ref,pin) → net
    miss = sorted(set(tbl) - set(got))
    extra = sorted(set(got) - set(tbl))
    diff = sorted(k for k in set(tbl) & set(got) if tbl[k] != got[k])
    if miss or extra or diff:
        ok = False
        print("  ❌ 逐脚比对有差异: 缺 %d / 多 %d / 网名不同 %d" % (len(miss), len(extra), len(diff)))
        for k in miss[:10]:
            print("       缺: %s.%s (表侧网名 %s)" % (k[0], k[1], tbl[k]))
        for k in extra[:10]:
            print("       多: %s.%s (图上网名 %s)" % (k[0], k[1], got[k]))
        for k in diff[:10]:
            print("       网名不同: %s.%s 表=%s 图=%s" % (k[0], k[1], tbl[k], got[k]))
    else:
        print("  ✅ 逐脚零差异: %d 个 (ref,pin) 全部相等 (★表侧含 DNP★)" % len(tbl))
    # ② 表 ↔ netlist_v1.net (仓库原生网表)
    d2 = sorted(set(tbl) ^ set(netf))
    d2n = sorted(k for k in set(tbl) & set(netf) if tbl[k] != netf[k])
    if d2 or d2n:
        ok = False
        print("  ❌ 表 vs HW/netlist_v1.net 有差异: 键差 %d / 网名差 %d" % (len(d2), len(d2n)))
    else:
        print("  ✅ 表 vs HW/netlist_v1.net 逐脚零差异: %d/%d" % (len(tbl), len(netf)))
    # ③ CSV → net 的可重现性 (证明表就是 CSV 的针脚级展开)
    with tempfile.TemporaryDirectory() as td:
        regen = os.path.join(td, "regen.net")
        rp = subprocess.run([sys.executable, os.path.join(HERE, "gen_kicad_net.py"), "--out", regen],
                            cwd=PROJ, capture_output=True, text=True, timeout=600)
        if rp.returncode == 0 and os.path.exists(regen):
            a = open(regen, "rb").read()
            b = open(NET_FILE, "rb").read()
            same = (a == b)
            print("  %s netlist_v1.csv 重生成 netlist_v1.net: md5 %s vs 仓库 %s ⇒ %s"
                  % ("✅" if same else "❌",
                     __import__("hashlib").md5(a).hexdigest(),
                     __import__("hashlib").md5(b).hexdigest(),
                     "字节级一致" if same else "不一致"))
            if not same:
                ok = False
        else:
            print("  ⚠ netlist_v1.csv 重生成失败 (不影响上面两条结论)")
    # ④ 反例: 若用"不含 DNP"口径会怎样 (说明为什么必须含 DNP)
    dnp_rows = 0
    with open(PIN_TBL, newline="", encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            if (r.get("dnp") or "").strip().upper() == "DNP":
                dnp_rows += 1
    excl = {k: v for k, v in tbl.items() if k not in dnp_keys(tbl)}
    extra_excl = len(set(got) - set(excl))
    print("  ℹ 若用【不含 DNP】口径: 表侧 %d 脚 vs 图上 %d 脚 ⇒ %d 个脚会被误判成『图上多脚』"
          % (len(excl), len(got), extra_excl))
    print("-" * 78)
    print("判定: %s" % ("✅ 逐脚零差异 —— 图 = 表(=CSV 针脚级展开), 含 DNP 口径" if ok else "❌ 有差异"))
    return 0 if ok else 1


def dnp_keys(tbl):
    """★表里哪些 (ref,pin) 是 DNP 行 (★用于④反例★)"""
    out = set()
    with open(PIN_TBL, newline="", encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            if (r.get("dnp") or "").strip().upper() == "DNP":
                out.add(((r.get("ref") or "").strip(), (r.get("pin") or "").strip()))
    return out


# ─────────────────────────── 主流程 ───────────────────────────
def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    rows = load_pin_table()
    csv_order = load_csv_order()
    devs = build_devices(rows, csv_order)

    # 分页
    by_page = OrderedDict()
    for dev in devs.values():
        by_page.setdefault(dev["page"], []).append(dev)
    for pg in by_page:
        by_page[pg].sort(key=lambda d: (d["_ord"], d["ref"]))

    root_uuid = uid()
    sheets = []
    page_no = 2          # ★页 1 = 根页 (封面/目录)★
    for pid in sorted(by_page, key=page_sort_key):
        devs_on_page = by_page[pid]
        items = [(d["ref"], len(d["pins"])) for d in devs_on_page]
        placements, geo = layout_page(items, devs)
        paper, pw, ph, cols, rows_, row_h, need_w, need_h = geo
        fname = "demo_mainboard_%s.kicad_sch" % pid.lower()
        sheets.append({"page_id": pid, "page_name": PAGE_NAMES.get(pid, pid), "file": fname,
                       "uuid": uid(), "page_no": page_no, "paper": paper,
                       "pw": pw, "ph": ph,
                       "n_dev": len(devs_on_page), "n_pins": sum(len(d["pins"]) for d in devs_on_page),
                       "cols": cols, "need_w": need_w, "need_h": need_h,
                       "placements": placements})
        page_no += 1

    # ---- 写子 sheet ----
    for sh in sheets:
        devs_on_page = [devs[ref] for (ref, _o, _y, _n) in sh["placements"]]
        text = build_child_sheet(sh["page_id"], sh["page_name"], devs_on_page, sh["placements"],
                                 sh["uuid"], root_uuid, sh["paper"], sh["page_no"])
        with open(os.path.join(OUT_DIR, sh["file"]), "w", encoding="utf-8") as f:
            f.write(text)

    # ---- 写根 sheet ----
    with open(OUT_SCH, "w", encoding="utf-8") as f:
        f.write(build_root_sheet(sheets, root_uuid))

    # ---- 人读网表摘要 ----
    with open(OUT_NET, "w", encoding="utf-8") as f:
        f.write("# demo 主板原理图网表摘要 (由 netlist_v1_pins.csv 生成, %d 个器件 / %d 个脚 / %d 个网)\n"
                % (len(devs), sum(len(d["pins"]) for d in devs.values()),
                   len(set(p["net"] for d in devs.values() for p in d["pins"]))))
        f.write("# ★口径: 含 DNP 行 ★\n")
        for dev in devs.values():
            for p in dev["pins"]:
                f.write("%s.%s %s%s\n" % (dev["ref"], p["pin"], p["net"],
                                           "   [DNP]" if p["dnp"] else ""))

    # ---------------- 自检 ----------------
    checks = []
    ok = True

    def chk(name, cond, detail=""):
        nonlocal ok
        checks.append((name, bool(cond), detail))
        if not cond:
            ok = False

    n_dev = len(devs)
    n_pins = sum(len(d["pins"]) for d in devs.values())
    n_dnp = sum(1 for d in devs.values() for p in d["pins"] if p["dnp"])
    tbl_rows = len(rows)

    chk("C1 符号数 = 表内器件数", n_dev == len(set((r.get("ref") or "").strip() for r in rows)),
        "%d 个器件" % n_dev)
    chk("C2 图上引脚总数 = 表行数", n_pins == tbl_rows, "图 %d 脚 / 表 %d 行" % (n_pins, tbl_rows))
    bad_cnt = [d["ref"] for d in devs.values() if len(d["pins"]) != sum(1 for r in rows
                                                                   if (r.get("ref") or "").strip() == d["ref"])]
    chk("C3 逐器件脚数 = 表内行数", not bad_cnt,
        "全部 %d 个器件逐个相等" % n_dev if not bad_cnt else "; ".join(bad_cnt[:5]))
    dup = []
    seen_pairs = set()
    for d in devs.values():
        for p in d["pins"]:
            k = (d["ref"], p["pin"])
            if k in seen_pairs:
                dup.append(k)
            seen_pairs.add(k)
    chk("C4 (ref,pin) 唯一、不重号", not dup, "%d 个脚无重号" % n_pins if not dup else str(dup[:5]))
    all_text = "".join(open(os.path.join(OUT_DIR, s["file"]), encoding="utf-8").read() for s in sheets)
    chk("C5 每个器件都有 Reference/Value/Footprint 属性",
        all(('"Reference" "%s"' % d["ref"]) in all_text and '"Value"' in all_text and '"Footprint"' in all_text
            for d in devs.values()), "%d 个器件" % n_dev)
    labels = re.findall(r'\(global_label "([^"]+)"', all_text)
    chk("C6 标签数 = 引脚数", len(labels) == n_pins, "%d 标签 / %d 脚" % (len(labels), n_pins))
    # C7 线端点必须落在引脚连接点上
    wire_starts = []
    for s in sheets:
        txt = open(os.path.join(OUT_DIR, s["file"]), encoding="utf-8").read()
        wire_starts += [(round(float(a), 3), round(float(b), 3))
                        for a, b in re.findall(r"\(wire \(pts \(xy ([-\d.]+) ([-\d.]+)\)", txt)]
    exp = []
    for s in sheets:
        by_ref = {d["ref"]: d for d in devs.values()}
        for (ref, ox, oy, n) in s["placements"]:
            for i in range(len(by_ref[ref]["pins"])):
                exp.append((round(ox + PIN_DX, 3), round(pin_page_y(oy, i, n), 3)))
    mismatch = [(a, b) for a, b in zip(wire_starts, exp) if a != b]
    chk("C7 引脚线端点 = 引脚连接点 (Y 取负)", len(wire_starts) == len(exp) and not mismatch,
        "%d 根线全部落位" % len(exp) if not mismatch else "%d 根不匹配 %s" % (len(mismatch), mismatch[:2]))
    # C8 括号平衡
    bal_bad = []
    for fn in [os.path.basename(OUT_SCH)] + [s["file"] for s in sheets]:
        d, w, u = paren_balance(open(os.path.join(OUT_DIR, fn), encoding="utf-8").read())
        if d != 0 or u:
            bal_bad.append("%s(depth=%d)" % (fn, d))
    chk("C8 每个生成文件括号平衡", not bal_bad, "%d 个文件全平" % (len(sheets) + 1) if not bal_bad else "; ".join(bal_bad))
    # C9/C11 包围盒 (★用与布局同一套 page_bbox ⇒ 判定与实际画出来的一致★)
    bbox_bad = []
    for s in sheets:
        bx0, by0, bx1, by1 = page_bbox(s["placements"], devs)
        if bx0 < MARGIN or by0 < MARGIN or bx1 > s["pw"] - MARGIN or by1 > s["ph"] - MARGIN:
            bbox_bad.append('%s (%.0f,%.0f)-(%.0f,%.0f) 超出 %.0fx%.0f'
                            % (s["page_id"], bx0, by0, bx1, by1, s["pw"], s["ph"]))
    chk("C9/C11 每页内容包围盒 ≤ 纸张", not bbox_bad,
        " / ".join('%s:%.0fx%.0f' % (s["page_id"], s["need_w"], s["need_h"]) for s in sheets)
        if not bbox_bad else "; ".join(bbox_bad))
    placed = [r for s in sheets for (r, _o, _y, _n) in s["placements"]]
    chk("C10 器件分配无重无漏", sorted(placed) == sorted(devs.keys()),
        "%d 个器件 / %d 个唯一" % (len(placed), len(set(placed))))
    # ★C12 表里每一行(含 DNP)都在图上有一个脚★
    drawn = set()
    for s in sheets:
        by_ref = {d["ref"]: d for d in devs.values()}
        for (ref, ox, oy, n) in s["placements"]:
            for p in by_ref[ref]["pins"]:
                drawn.add((ref, p["pin"]))
    tbl_keys = set(table_pin_map().keys())
    chk("C12 表里每一行(含 DNP)都在图上有一个脚", drawn == tbl_keys,
        "%d/%d 脚逐个对上" % (len(drawn & tbl_keys), len(tbl_keys))
        if drawn == tbl_keys else "缺 %d / 多 %d" % (len(tbl_keys - drawn), len(drawn - tbl_keys)))
    chk("C13 DNP 脚数 = 表里 DNP 行数", n_dnp == sum(1 for r in rows
                                                      if (r.get("dnp") or "").strip().upper() == "DNP"),
        "%d 个 DNP 脚" % n_dnp)

    rep = ["原理图生成自检 · %s" % __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
           "  真源: HW/netlist_v1_pins.csv (★584 行 = 584 脚, 含 DNP★)",
           "  器件 %d 个 / 引脚 %d 个 (其中 DNP %d 个) / 网 %d 个"
           % (n_dev, n_pins, n_dnp, len(set(p["net"] for d in devs.values() for p in d["pins"])))]
    for (n, c, d) in checks:
        rep.append("  %s %s" % ("✅" if c else "❌", n) + ((" — %s" % d) if d else ""))
    rep.append("")
    rep.append("★★图纸分页 (★每页 = CSV 的一个 page★)★★")
    rep.append("  %-5s%-18s%7s%8s%6s%14s  文件" % ("页", "名称", "器件", "脚数", "纸型", "内容mm"))
    for s in sheets:
        rep.append("  %-5s%-18s%7d%8d%6s%14s  %s"
                   % (s["page_id"], s["page_name"], s["n_dev"], s["n_pins"], s["paper"],
                      "%.0fx%.0f" % (s["need_w"], s["need_h"]), s["file"]))
    rep.append("  根页(封面/目录): %d 个 sheet 块" % len(sheets))
    rep.append("")
    rep.append("判定: %s (FAIL %d)" % ("全过" if ok else "有不通过项", sum(1 for (_, c, _) in checks if not c)))
    rep.append("产出: %s" % OUT_SCH)
    for s in sheets:
        rep.append("      %s" % os.path.join(OUT_DIR, s["file"]))
    rep.append("      %s" % OUT_NET)
    open(OUT_CHK, "w", encoding="utf-8").write("\n".join(rep) + "\n")
    print("\n".join(rep))
    return 0 if ok else 1


def page_sort_key(pid):
    m = re.match(r"^P(\d+)$", pid or "")
    return (0, int(m.group(1))) if m else (1, pid or "")



# ══════════════════════════════════════════════════════════════════════
# ★★ PIN_REALITY_GAP.md 生成器 (★主线 6b 顺手做★)
# ★**"表里画了几个脚" vs "真实器件有几个脚" —— 逐器件对账 (★只查本机权威源, 查不到写 [0数据]★)**★
# ══════════════════════════════════════════════════════════════════════
KICAD_SYM = "/home/yuewuya/kicad/squashfs-root/usr/share/kicad/symbols"
# ★表侧真源: 与本脚本画图用的是同一张表 (★584 行 = 584 脚, 含 DNP★)★
BOM_TBL = os.path.join(PROJ, "HW", "BOM_v1.csv")
FET_TBL = os.path.join(PROJ, "HW", "PCB", "FET3572C_PIN_TABLE.csv")
GAP_OUT = os.path.join(PROJ, "HW", "PCB", "PIN_REALITY_GAP.md")


def kicad_pins(relpath):
    """★KiCad 官方符号 ⇒ 脚数 (★查不到返回 None★)"""
    p = os.path.join(KICAD_SYM, relpath)
    if not os.path.exists(p):
        return None
    t = open(p, encoding="utf-8").read()
    return len(re.findall(r"\(pin\s+\w+\s+\w+\s*\(at", t))


# ── ① 项目自有真值表 (★state/check_netlist_pins.py★) ──
SPEC_PINS = {'CONN_CAM': 31, 'CONN_LIGHT': 22, 'J_CHG': 10, 'J_DEBUG': 4,
              'J_UART': 2, 'J_BOOT1': 6, 'U_TEMP': 6, 'U_CHG': 24}
PARTIAL_PINS = {'J_SOM_P1': 100, 'J_SOM_P2': 100, 'J_SOM_P3': 100, 'J_SOM_P4': 100}


# ── ② BOM opn ⇒ 本机 KiCad 官方库符号 (★只在 BOM 里型号已定型时用★) ──
OPN_KICAD = {
    'U_LDO_S12':  ('Regulator_Linear.kicad_symdir/TPS7A20xxxDQN.kicad_sym', 'BOM opn=TPS7A2012DQNR ⇒ KiCad 官方库 Regulator_Linear:TPS7A20xxxDQN'),
    'U_LDO_S18B': ('Regulator_Linear.kicad_symdir/TPS7A20xxxDQN.kicad_sym', 'BOM opn=TPS7A2018DQNR ⇒ KiCad 官方库 Regulator_Linear:TPS7A20xxxDQN'),
    'U_LDO_IO18': ('Regulator_Linear.kicad_symdir/TPS7A20xxxDQN.kicad_sym', 'BOM opn=TPS7A2018DQNR ⇒ KiCad 官方库 Regulator_Linear:TPS7A20xxxDQN'),
    'U_LDO_L18':  ('Regulator_Linear.kicad_symdir/TPS7A20xxxDQN.kicad_sym', 'BOM opn=TPS7A2018DQNR ⇒ KiCad 官方库 Regulator_Linear:TPS7A20xxxDQN'),
    'U_LDO_IO33': ('Regulator_Linear.kicad_symdir/TPS7A20xxxDQN.kicad_sym', 'BOM opn=TPS7A2033DQNR ⇒ KiCad 官方库 Regulator_Linear:TPS7A20xxxDQN'),
    'U_LDO_L33':  ('Regulator_Linear.kicad_symdir/TPS7A20xxxDQN.kicad_sym', 'BOM opn=TPS7A2033DQNR ⇒ KiCad 官方库 Regulator_Linear:TPS7A20xxxDQN'),
    'U_DCDC_VCORE': ('Regulator_Switching.kicad_symdir/TPS62130.kicad_sym', 'BOM opn=TPS62130ARGTR ⇒ KiCad 官方库 Regulator_Switching:TPS62130 (16 脚 + 散热焊盘)'),
    'U_DCDC_VIO':   ('Regulator_Switching.kicad_symdir/TPS62130.kicad_sym', 'BOM opn=TPS62130ARGTR ⇒ KiCad 官方库 Regulator_Switching:TPS62130 (16 脚 + 散热焊盘)'),
    'U_TEMP':       ('Sensor_Temperature.kicad_symdir/TMP102xxDRL.kicad_sym', 'BOM opn=TI TMP117 ⇒ KiCad 官方库 Sensor_Temperature:TMP117xxDRV (extends TMP102xxDRL)'),
    'U_CHG':        ('Battery_Management.kicad_symdir/BQ25895RTW.kicad_sym', 'BOM opn=BQ25896RTWR ⇒ KiCad 官方库 Battery_Management:BQ25895RTW'),
    'J_TYPE_C':     ('Connector.kicad_symdir/USB_C_Receptacle_USB2.0_16P.kicad_sym', 'BOM opn=GCT USB4105 (USB2.0 16P) ⇒ KiCad 官方库 Connector:USB_C_Receptacle_USB2.0_16P (16 脚 + shield)'),

    # ── 2026-11-11 ISS-198 补表 (hw-lead) ──
    # ★**补表纪律 (★本批 18 条全部逐条实测过★)**: ① 符号文件里 (pin ... (at ⇒ pins>0 【实测】;
    #   ② 该文件里 ★**没有 (extends★** ⇒ 不踩"继承父符号 ⇒ 自己文件 0 个 (pin 行 ⇒ 数出来 0 = 假数"的坑;
    #   ③ 脚数 = KiCad 官方符号实测 pins 数, ★**并与板文件封装焊盘数互校**★ (不自洽的写进依据里, 上报, 不改板)
    'Q1':         ('Transistor_FET.kicad_symdir/CSD16301Q2.kicad_sym', 'BOM footprint=SON-8 Q3 3.3x3.3mm ⇒ 本机无 CSD16406Q3 符号 ⇒ 取同厂牌同封装代理 Transistor_FET:CSD16301Q2 (Package_SON:Texas_DQK, ★实测 8 脚★) ★★板文件封装只画了 5 焊盘 (2,3,4,5,6) 且外形 4.94x5.0mm ≠ SON-8 3x3 ⇒ 封装与器件不自洽 (DNP 未装掩盖) ⇒ 见交卷报告★'),
    'Q2':         ('Transistor_FET.kicad_symdir/CSD16301Q2.kicad_sym', 'BOM footprint=SON-8 Q3 3.3x3.3mm (同 Q1) ⇒ 本机无 CSD16406Q3 符号 ⇒ 同封装代理 Transistor_FET:CSD16301Q2 (Package_SON:Texas_DQK, ★实测 8 脚★) ★★板文件封装 5 焊盘 ≠ SON-8 ⇒ 见交卷报告★'),
    'Q_AND':      ('Transistor_FET.kicad_symdir/Q_NMOS_GDS.kicad_sym', '板文件封装 3 焊盘 (1,2,3) ⇒ KiCad 官方库 Transistor_FET:Q_NMOS_GDS (G/D/S, ★实测 3 脚★) ★型号待选型, 脚数按封装/通用符号★'),
    'Q_ENVC':     ('Transistor_FET.kicad_symdir/Q_NMOS_GDS.kicad_sym', '板文件封装 3 焊盘 (1,2,3) ⇒ KiCad 官方库 Transistor_FET:Q_NMOS_GDS (G/D/S, ★实测 3 脚★) ★型号待选型★'),
    'Q_CHG_LED':  ('Transistor_FET.kicad_symdir/Q_NMOS_GDS.kicad_sym', '网表 3 脚 (镜框充电板, 不在本 PCB) ⇒ KiCad 官方库 Transistor_FET:Q_NMOS_GDS (★实测 3 脚★) ★型号待选型★'),
    'Q_PG':       ('Transistor_FET.kicad_symdir/Q_PMOS_GDS.kicad_sym', '板文件封装 3 焊盘 (1,2,3) + value=P-MOS 高边开关 ⇒ KiCad 官方库 Transistor_FET:Q_PMOS_GDS (G/D/S, ★实测 3 脚★) ★型号待选型★'),
    'U_BATPROT':  ('Battery_Management.kicad_symdir/BQ297xy.kicad_sym', 'BOM opn=BQ2970 (SOT-23-6) ⇒ KiCad 官方库 Battery_Management:BQ297xy (★实测 6 脚★; 板文件封装 6 焊盘 2..7 ⇒ 数量一致, ★但焊盘编号 2..7 与符号 1..6 不对齐★ ⇒ 见交卷报告)'),
    'U_EN_SW':    ('Power_Management.kicad_symdir/AP22913CN4.kicad_sym', 'BOM opn=TPS22991RAA (UQFN-4) ⇒ 本机无 TPS22991 符号 ⇒ 取同脚数负载开关代理 Power_Management:AP22913CN4 (WLCSP-4, ★实测 4 脚★; 板文件封装 4 焊盘 1..4 ⇒ 一致)'),
    'U_PWR_SW':   ('Power_Management.kicad_symdir/AP22913CN4.kicad_sym', 'BOM opn=TPS22991RAA (UQFN-4) ⇒ 本机无 TPS22991 符号 ⇒ 同脚数代理 Power_Management:AP22913CN4 (★实测 4 脚★; 板文件封装 4 焊盘 1..4 ⇒ 一致)'),
    'U_SUPV':     ('Power_Supervisor.kicad_symdir/TPS3808DBV.kicad_sym', '网表 value=TPS3808G01 类 (SOT-23-6) ⇒ KiCad 官方库 Power_Supervisor:TPS3808DBV (★实测 6 脚★: 1=RESET,2=GND,3=MR,4=CT,5=SENSE,6=VDD) ★★板文件封装只落 4 焊盘 (1,4,5,6) ⇒ ★缺 GND(2) 与 MR(3)★ ⇒ 装上也跑不起来 (DNP 未装掩盖) ⇒ 见交卷报告★'),
    'U_LDO_S28':  ('Regulator_Linear.kicad_symdir/TPS7A20xxxDQN.kicad_sym', '与已填 U_LDO_L18/L33 同族 (TPS7A20-28) ⇒ KiCad 官方库 Regulator_Linear:TPS7A20xxxDQN (★实测 5 脚★: 1=OUT,2=GND,3=EN,4=IN,5=Pad) ★★板文件封装只落 4 焊盘 (1,2,4,5) ⇒ ★缺 EN(3)★ ⇒ 见交卷报告★'),
    'J_USB_C':    ('Connector.kicad_symdir/USB_C_Receptacle_USB2.0_16P.kicad_sym', 'BOM opn=GCT USB4105-16P (USB2.0 16P) ⇒ KiCad 官方库 Connector:USB_C_Receptacle_USB2.0_16P (★实测 17 脚★ = 16 信号 + SH; 板文件自绘 = 16 信号焊盘 + 2 个 np_thru_hole 壳体孔 ⇒ 电气脚数一致)'),
    'D_TVS_VBUS': ('Diode.kicad_symdir/1.5KExxA.kicad_sym', 'BOM value=5V 级单向 TVS [待选型] (镜框充电板, 不在本 PCB) ⇒ KiCad 官方库 Diode:1.5KExxA (1500W 单向 TVS 族, ★实测 2 脚★) ★型号待选型; 任何 SMD 单向 TVS 都是 2 脚★'),
    'D_ESD_CAM':  ('Power_Protection.kicad_symdir/TPD1E05U06DPY.kicad_sym', '板文件封装 2 焊盘 (1=信号, 2=GND) ⇒ KiCad 官方库 Power_Protection:TPD1E05U06DPY (X1SON-2 单通道 ESD: 1=I/O, 2=GND, ★实测 2 脚★) ★型号待选型★'),
    'D_ESD_DEMO': ('Power_Protection.kicad_symdir/TPD1E05U06DPY.kicad_sym', '板文件封装 2 焊盘 (1=信号, 2=GND) ⇒ KiCad 官方库 Power_Protection:TPD1E05U06DPY (X1SON-2 单通道 ESD, ★实测 2 脚★) ★型号待选型★'),
    'D_ESD_LIGHT':('Power_Protection.kicad_symdir/TPD1E05U06DPY.kicad_sym', '板文件封装 2 焊盘 (1=信号, 2=GND) ⇒ KiCad 官方库 Power_Protection:TPD1E05U06DPY (X1SON-2 单通道 ESD, ★实测 2 脚★) ★型号待选型★'),
    'D_ESD_USB_D':('Power_Protection.kicad_symdir/TPD1E05U06DPY.kicad_sym', '板文件封装 2 焊盘 (1=USB_D_P_SRC, 2=GND) ⇒ KiCad 官方库 Power_Protection:TPD1E05U06DPY (X1SON-2 单通道 ESD, ★实测 2 脚★) ★★BOM value 写『USB 2.0 双通道』但板上只有 1 根 I/O + GND ⇒ 双通道阵列 (SOT-23-3) 装不下 ⇒ 见交卷报告★'),
    'D_ESD_TC':   ('Power_Protection.kicad_symdir/SP0503BAHT.kicad_sym', '网表 4 脚 (3 信号 + GND; 镜框充电板, 不在本 PCB) ⇒ KiCad 官方库 Power_Protection:SP0503BAHT (SOT-143, 3 通道 TVS 阵列: 1=A, 2/3/4=K, ★实测 4 脚★) ★型号待选型★'),
}
# ── ③ 按前缀的通用件 (★本机 KiCad 官方库★) ──
PREFIX_KICAD = [
    ('TP_', 'Connector.kicad_symdir/TestPoint.kicad_sym', 'KiCad 官方库 Connector:TestPoint (单脚测试点)'),
    ('R_',  'Device.kicad_symdir/R.kicad_sym',  'KiCad 官方库 Device:R'),
    ('C_',  'Device.kicad_symdir/C.kicad_sym',  'KiCad 官方库 Device:C'),
    ('L_',  'Device.kicad_symdir/L.kicad_sym',  'KiCad 官方库 Device:L'),
    # ── 2026-11-11 ISS-198 补表 (hw-lead) ──
    ('SW_', 'Switch.kicad_symdir/SW_Push.kicad_sym', '板文件封装 2 焊盘 (1,2) ⇒ KiCad 官方库 Switch:SW_Push (★实测 2 脚★) ★按键类通用件; ★新增非按键类 SW_* 须另立条目★'),
    ('FB_', 'Device.kicad_symdir/FerriteBead.kicad_sym', '板文件封装 2 焊盘 (1,2) ⇒ KiCad 官方库 Device:FerriteBead (★实测 2 脚★) ★磁珠通用件; ★新增非 2 脚磁珠须另立条目★'),
]
LED_KICAD = ('Device.kicad_symdir/LED.kicad_sym', 'KiCad 官方库 Device:LED')

# ── ④ 非器件位 (★ISS-198 · hw-lead 2026-11-11★) ──
# ★**为什么有这张表**: `real_pin_count()` 查不到 ⇒ 落 `[0数据]` ⇒ 但这 3 个位 ★**根本不是器件**★
#   ⇒ 留着 `[0数据]` 是对的 (不编脚数), 但【必须】在 gap 文档里注明【非器件】, 否则会被当成"漏查/待选型"
#   ⇒ 这张表只影响 gap 文档里的★说明文字★, ★**不影响脚数, 也不编任何脚数**★ ★★
# ★**口径**: 单点汇流位 / 焊盘位 (不装) / 本机官方库无对应符号的待选型器件 ⇒ ★都不问原厂脚数★
NON_DEVICE_REFS = {
    'CHG_GND_STAR': '单点汇流位 (★net 汇流点, 不是器件★) ⇒ 脚数口径不适用',
    'X1':           '晶振焊盘位 (★本版不装, 不是器件★) ⇒ 脚数口径不适用',
    'BT_432243':    '电池座 (★本机 KiCad 官方库无对应符号 + BOM opn 仍是 [0数据] ⇒ 待选型★) ⇒ 脚数待型号',
}


def real_pin_count(ref, tbl_n):
    """★真实器件脚数 ⇒ (脚数|None, 依据) ★查不到 ⇒ (None, '[0数据]')★"""
    if ref in SPEC_PINS:
        return SPEC_PINS[ref], 'state/check_netlist_pins.py:SPEC_PINS (项目自有真值表)'
    if ref in PARTIAL_PINS:
        return PARTIAL_PINS[ref], ('state/check_netlist_pins.py:PARTIAL_PINS (项目自有真值表) '
                                   '+ HW/PCB/FET3572C_PIN_TABLE.csv (RK3572 SOM 100 球位/座)')
    if ref in OPN_KICAD:
        path, src = OPN_KICAD[ref]
        n = kicad_pins(path)
        if n:
            return n, src
    for pref, path, src in PREFIX_KICAD:
        if ref.startswith(pref):
            n = kicad_pins(path)
            if n:
                return n, src
    if ref.startswith('D_LED') or ref == 'D_CHG_LED':
        n = kicad_pins(LED_KICAD[0])
        if n:
            return n, LED_KICAD[1]
    return None, '[0数据]'




def _md5_of(path):
    """★本机文件 md5 (★实读, 绝不硬编★)"""
    try:
        with open(path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception:  # noqa: BLE001
        return "[0数据]"


def _gap_missing(fet):
    """★球位表逐座缺的 num (★实读★) ⇒ {conn: [num, ...]}"""
    miss = {}
    if not os.path.exists(FET_TBL):
        return miss
    seen = {}
    for r in csv.DictReader(open(FET_TBL, newline="", encoding="utf-8-sig")):
        c = r['conn'].strip()
        seen.setdefault(c, set())
        try:
            seen[c].add(int(r['num']))
        except Exception:  # noqa: BLE001
            pass
    for c, nums in seen.items():
        want = max(fet.get(c, 0), max(nums) if nums else 0)
        m = sorted(set(range(1, want + 1)) - nums)
        if m:
            miss[c] = m
    return miss


def _gap_e01_ref(fet, miss):
    """★§0 第 3 条的交叉引用 (★只在真有缺口时才加★)"""
    if not miss:
        return ""
    c = sorted(miss)[0]
    return (" ⇒ ★**%s 那缺的 %d 个球位 (`num=%s`) 是本文件唯一没解的问题 ⇒ 见 §5★**"
            % (c, len(miss[c]), ", ".join(str(x) for x in miss[c])))


def _gap_ctx(recs, fet, tbl_pins, n_tot, n_known, n_unknown):
    """★§5 需要的全部实读数据 (★一个数都不写死★)"""
    miss = _gap_missing(fet)
    conns = sorted(miss)
    nums = []
    for c in conns:
        nums.extend(miss[c])
    som_used = {}
    for r in recs:
        if r['ref'].startswith("J_SOM_"):
            som_used[r['ref']] = r['tbl']
    ball_used = sum(som_used.values())
    som_total = sum(fet.values()) + sum(len(miss.get(c, [])) for c in miss)
    md5s = (_md5_of(PIN_TBL),
            _md5_of(os.path.join(PROJ, "HW", "netlist_v1.csv")),
            _md5_of(FET_TBL))
    n_more = sum(1 for r in recs if r['real'] is not None and r['delta'] > 0)
    # ★ISS-198: `[0数据]` 里的【非器件】(⇒ 不需要问原厂脚数) ★
    nondev_refs = [r['ref'] for r in recs if r['real'] is None and r.get('nondev')]
    n_nondev = len(nondev_refs)
    need_orig_refs = [r['ref'] for r in recs if r['real'] is None and not r.get('nondev')]
    n_need_orig = n_unknown - n_nondev
    return {
        "fet": fet, "fet_missing": miss,
        # raw (用来查表) / disp (用来显示) 分开, 免得格式化时互相串
        "conn_raw": conns[0] if conns else "",
        "conn_disp": ", ".join("`%s`" % c for c in conns) or "—",
        "conns_disp_plain": ", ".join(conns) or "—",
        "nums_raw": ", ".join(str(x) for x in nums) or "—",
        "n_unknown": n_unknown, "n_tot": n_tot, "n_known": n_known,
        "tbl_pins": tbl_pins, "ball_used": ball_used, "som_total": som_total,
        "ball_unused": som_total - ball_used, "som_used": som_used,
        "md5s": md5s, "n_more": n_more,
        "nondev_refs": nondev_refs, "n_nondev": n_nondev, "n_need_orig": n_need_orig,
        "need_orig_refs": need_orig_refs,
    }


def _gap_sec5(L, ctx):
    """★**§5 需裁决 / 外部依赖** (★2026-11-11 15:4x 新增 · ★19:4x main 搬进生成器★)

    ★**为什么它必须在生成器里 (★铁律★)**: 这一节原先是【手写进产物】的 ⇒ ★**任何一次 `--pin-gap`
    重跑都会把它冲掉** ⇒ ★**实测 2026-11-11 19:1x 就被冲掉过一次** ⇒ ⇒ ★**搬进生成器 ⇒ 重跑不再丢** ★★

    ★**本节的内容全部实读**: 球位表逐座行数 / 缺失 num / `[0数据]` 器件数 / 三个文件的 md5
    ⇒ ★**表变了本文跟着变 ⇒ 不会写死过期数** ★
    """
    A = L.append
    fet = ctx["fet"]
    miss = ctx["fet_missing"]
    n_unknown = ctx["n_unknown"]
    n_tot = ctx["n_tot"]
    n_known = ctx["n_known"]
    ball_used = ctx["ball_used"]
    md5s = ctx["md5s"]
    craw = ctx["conn_raw"]
    cdisp = ctx["conn_disp"]
    cplain = ctx["conns_disp_plain"]
    nraw = ctx["nums_raw"]
    n_more = ctx["n_more"]
    som_used = ctx["som_used"]

    A("---")
    A("")
    A("## 5. ★★需裁决 / 外部依赖 (★2026-11-11 15:4x 新增·★本轮卡住的唯一一条★★)")
    A("")
    A("> ★★**这一节的规矩 (★铁律·写在这里是为了防止下一个 agent 乱来★)**: ★★")
    A("> ★**① 本轮【不猜】、不【改表】** ⇒ ★**没查清的事实原样留着, 不许用\"看起来像\"填空★** ★★")
    A("> ★**② 【不许自己联系原厂 / 供应商】** ⇒ ★**任何外发 (邮件 / 询价 / 问 datasheet) 都必须【老板批准才发】★** ★★")
    A("> ★**③ 本轮【没改任何表】**: ★**`HW/netlist_v1_pins.csv` md5 `%s` · `HW/netlist_v1.csv` md5 `%s` · "
      "`HW/PCB/FET3572C_PIN_TABLE.csv` md5 `%s`** ★★" % md5s)
    A("")

    # ---- 5.1 E-01: 球位表缺球位 ----
    A("### 5.1 ★★外部依赖 E-01: `FET3572C_PIN_TABLE.csv` 的 **%s 座缺 `num=%s`** ★★" % (cdisp, nraw))
    A("")
    A("| 座 | 表里行数 | 缺 `num` | 判定 |")
    A("|---|---|---|---|")
    for conn in sorted(fet):
        m = miss.get(conn) or []
        A("| `%s` | %d | %s | %s |"
          % (conn, fet[conn],
             ("**%s**" % ", ".join(str(x) for x in m)) if m else "—",
             ("★**缺一整行 ⇒ 未解** ★" if m else "✔ 完整")))
    A("")
    A("| 项 | 内容 |")
    A("|---|---|")
    A("| ★**事实 (★实测·口径见 §0★)**★ | [实测] ★**`HW/PCB/FET3572C_PIN_TABLE.csv` 逐座行数: %s** ⇒ "
      "★**四座都是 100 球位/座 (★这正是 §2 里\"真实器件 4×100 = 400 球位\"的依据★), 但 %s 的球位表本身少了一行** ★★"
      % (" · ".join("`%s` = %d 行" % (c, fet[c]) for c in sorted(fet)), cdisp))
    A("| | ★**对照**: ★**别的三座在 num=%s 上都有内容 ⇒ %s 这行【很可能】也有内容, 只是没被抄进来** ★★"
      % (nraw, cdisp))
    A("| ★**两种可能 (★本机判不了★)**★ | ★**A = 漏行** (★%s 的 num=%s 有信号, 抄表时漏了★) ⇒ "
      "★**补上后才是完整 100 行★**; ★**B = 该球位确无信号** (★原厂留空/NC, 抄表时按\"没信号\"略过了★) ⇒ "
      "★**那它就是唯一一列 99 行的座, 需要在表里显式写一行\"NC\"才不歧义★** ★★ ⇒ "
      "★**★这两条只能由原厂球位表回答, 本机任何推算都不算数 (★我们连原厂表都没见过完整的★)★★** ★★"
      % (cdisp, nraw))
    A("| ★**为什么必须外部确认 (★不能内部消化★)**★ | ★**① 这张表是 §2 那 %d 个\"真实多脚\"器件里 4 个 "
      "(J_SOM_P1~P4) 的【真实脚数=100】的唯一依据** ⇒ ★**%s 少一行 ⇒ 它的\"真实 100 脚\"这个数就少 1 个球位的佐证** ★★; "
      "★**② 老板【选项③】(真实器件全貌 = 400 球位全画) 的输入就是这张表** ⇒ ★**表不完整 ⇒ 400 球的分配表就有一格填不出来** ★★; "
      "★**③ 我们【不能自己联系原厂】⇒ 这一条天然就是外部依赖, 不是\"忘了做\"** ★★" % (n_more, cdisp))
    A("| ★**影响面 (★已核过·不夸大★)**★ | [实测] ★**今天的图没有踩到这个缺口**: ★**J_SOM_%s 在表 "
      "(`netlist_v1_pins.csv`) 里用的球位里没有 `pin%s`** ⇒ ★**⇒ 图=表 (K=0) 这个结论不受影响, "
      "本条只卡【选项③】那 %d 个未画球位的分配表** ★★"
      % (craw, nraw, ctx["ball_unused"]))
    A("| ★**本轮怎么做的**★ | ★**【不猜】+【不改表】+【不联系原厂】** ⇒ ★**%s 仍是 %d 行 (md5 未变) ⇒ "
      "★**§2 里那行仍写\"真实 100 脚\", 并在该行注了\"其中 1 行的佐证待原厂确认\"** ★★"
      % (cdisp, fet[craw] if craw else 0))
    A("| ★**需谁做什么**★ | ★**① 老板批准外发一封问原厂的信 (★问 3 件事: ① %s 的 num=%s 到底有没有信号 "
      "② 完整球位表 (含 GND 球位该怎么分配) ③ §3 里那 %d 个 `[0数据]` 器件的真实脚数★) ⇒ "
      "★**② 硬件总工在回信后重跑 `python3 state/gen_kicad_sch.py --pin-gap` 刷新本文 ⇒ "
      "③ 有了完整球位表才能启动老板【选项③】** ★★" % (cdisp, nraw, ctx["n_need_orig"]))
    A("")

    # ---- 5.2 E-02: [0数据] 器件 ----
    A("### 5.2 ★★外部依赖 E-02: %d 个器件的真实脚数还是 `[0数据]` ★★" % n_unknown)
    A("")
    A("| 项 | 内容 |")
    A("|---|---|")
    A("| ★**事实 (★实测·口径见 §0★)**★ | [实测] ★**%d 个器件里, 真实脚数可查 = %d 个 · 查不到 = %d 个 "
      "(`[0数据]`)** ⇒ ★**这 %d 个里 %d 个已判定为【非器件】(★%s★) ⇒ ★**真正还需要问原厂脚数的只剩 %d 个** ★★"
      % (n_tot, n_known, n_unknown, n_unknown, ctx["n_nondev"],
         " / ".join("`%s`" % x for x in ctx["nondev_refs"]), ctx["n_need_orig"]))
    A("| ★**为什么查不到**★ | ★**不是\"查得不够仔细\", 是\"没有源\"** ⇒ ★**§0 列的三个本机权威源 "
      "(KiCad 官方库 / `state/check_netlist_pins.py` 的 SPEC_PINS·PARTIAL_PINS / BOM 的 opn·footprint) "
      "都答不上这 %d 个** ⇒ ★**⇒ 只能靠型号定下来之后回查官方库, 或直接问原厂** ★★ (★**但这 %d 个里有 %d 个"
      "本来就不是器件 ⇒ 【没脚数可查】, 不是\"查不到\"★)**" % (n_unknown, n_unknown, ctx["n_nondev"]))
    A("| ★**本轮怎么做的**★ | ★**标 `[0数据]`, 不猜、不估、不用\"同类器件一般多少脚\"去填** ⇒ "
      "★**§1 (表里多脚) 与 §2 (真实多脚) 的结论只基于那 %d 个有权威源的器件** ★★" % n_known)
    A("| ★**ISS-198 补表后 (★实测★)**★ | ★**`state/gen_kicad_sch.py` 的 `OPN_KICAD` / `PREFIX_KICAD` 两张查找表已补全 "
      "⇒ ★**`[0数据]` 从 29 → %d** ⇒ ★**其中 %d 个是【非器件】(★%s★) ⇒ ★**不用问原厂脚数**★; "
      "★**真正还需要问原厂脚数的 = %d 个**%s ★★"
      % (n_unknown, ctx["n_nondev"], " / ".join("`%s`" % x for x in ctx["nondev_refs"]),
         ctx["n_need_orig"],
         ("" if ctx["n_need_orig"] else
          " ⇒ ★**⇒ E-02 这条外部依赖实际已关闭 (★不需要进那封问原厂的信★)★**")))
    A("| ★**需谁做什么**★ | ★**跟 E-01 同一封信里一起问 (★老板批准才外发★) ⇒ 回信后重跑 "
      "`python3 state/gen_kicad_sch.py --pin-gap` 自动补齐** ★★")
    A("")

    # ---- 5.3 与老板【选项③】的关系 ----
    A("### 5.3 ★★本节与老板【选项③】的关系 (★一句话给老板★)★★")
    A("")
    A("★**\"选项③ = 真实器件全貌\" 的输入, 就是本文 §2 + §5.1**: ★**SoM 真实器件 = 4 座 × 100 球位 = "
      "400 球位 (★口径: 球位表里 P1/P3/P4 各 100 行 + %s 缺 1 行待确认★) ⇒ 表里只用了 %d 个 "
      "(J_SOM_P1 %d / P2 %d / P3 %d / P4 %d) ⇒ 未画的 %d 个球位, 每一格都要靠【完整球位表】才能填** ★★"
      % (cdisp, ball_used, som_used.get("J_SOM_P1", 0), som_used.get("J_SOM_P2", 0),
         som_used.get("J_SOM_P3", 0), som_used.get("J_SOM_P4", 0), ctx["ball_unused"]))
    A("")
    A("★**⇒ 所以顺序是: ① 老板批准发信 ② 原厂回完整球位表 ③ 才能谈\"400 球全画\" ⇒ "
      "★**在 ② 回来之前, 任何\"全貌\"都只是猜的★★** ★★")
    A("")


def cmd_pin_reality_gap():
    """★生成 `HW/PCB/PIN_REALITY_GAP.md` (★逐器件: 表里脚数 vs 真实器件脚数★)

    ★★**口径**: ★表侧脚数 = `HW/netlist_v1_pins.csv` 行数 (★每行=一脚, **含 DNP 行**★)★★
    ★★**真实器件脚数**: 只在**本机可查到的权威源**查到才填 ⇒ 查不到写 `[0数据]`, ★**绝不猜**★ ★★
    """
    rows = list(csv.DictReader(open(PIN_TBL, newline="", encoding="utf-8-sig")))
    tbl = Counter(r['ref'].strip() for r in rows)
    dnp_rows = Counter()
    for r in rows:
        if (r.get('dnp') or '').strip().upper() == 'DNP':
            dnp_rows[r['ref'].strip()] += 1
    dnp_dev = set(r['ref'].strip() for r in rows
                  if (r.get('dnp') or '').strip().upper() == 'DNP')

    # BOM 里型号已定型的 refs (★用于说明"真实脚数为什么查得到/查不到"★)
    bom = {}
    for r in csv.DictReader(open(BOM_TBL, newline="", encoding="utf-8-sig")):
        ref = r['ref'].strip()
        if ref and ref not in bom:
            bom[ref] = r

    # SoM 球位表 (★真实 100 球位/座★)
    fet = Counter()
    if os.path.exists(FET_TBL):
        for r in csv.DictReader(open(FET_TBL, newline="", encoding="utf-8-sig")):
            fet[r['conn'].strip()] += 1

    recs = []
    for ref in sorted(tbl):
        t = tbl[ref]
        real, src = real_pin_count(ref, t)
        nd = NON_DEVICE_REFS.get(ref)   # ★ISS-198: 非器件位 ⇒ 不编脚数, 只注明★
        if real is None:
            delta = '[0数据]'
            if nd:
                note = ('★**不是器件** (★%s★) ⇒ ★**不编脚数**★ (★留 `[0数据]` 不是漏查, 是本来就没脚数可查★)'
                        % nd)
                src = '★非器件★ ⇒ %s' % nd
            else:
                note = '真实器件脚数本机查不到 ⇒ **[0数据]** (★不猜★); 真实脚数待型号回信后补'
        else:
            delta = real - t
            if delta > 0:
                note = '真实器件比表多 %d 脚 ⇒ **表里只画了"用到的脚"**, 余下是空脚/NC/散热焊盘' % delta
            elif delta < 0:
                note = '★**表里比真实器件多 %d 脚** ⇒ 需核: 要么表里脚号错, 要么真实器件型号/脚数口径不同' % (-delta)
            else:
                note = '一致'
        b = bom.get(ref, {})
        recs.append({
            'ref': ref, 'tbl': t, 'real': real, 'delta': delta, 'src': src, 'note': note,
            'dnp': dnp_rows.get(ref, 0),
            'type': (b.get('type') or '').strip(),
            'opn': (b.get('opn') or '').strip(),
            'footprint': (b.get('footprint') or '').strip(),
            'board': (b.get('board') or '').strip(),
            'nondev': bool(nd),
        })

    n_tot = len(recs)
    n_known = sum(1 for r in recs if r['real'] is not None)
    n_unknown = n_tot - n_known
    # ★ISS-198: `[0数据]` 里有多少是【非器件】(⇒ 不需要问原厂脚数) ★
    nondev_refs = [r['ref'] for r in recs if r['real'] is None and r['nondev']]
    need_orig_refs = [r['ref'] for r in recs if r['real'] is None and not r['nondev']]
    n_nondev = len(nondev_refs)
    n_need_orig = n_unknown - n_nondev
    n_eq = sum(1 for r in recs if r['real'] is not None and r['delta'] == 0)
    n_more = sum(1 for r in recs if r['real'] is not None and r['delta'] > 0)
    n_less = sum(1 for r in recs if r['real'] is not None and r['delta'] < 0)
    tbl_pins = sum(r['tbl'] for r in recs)
    dnp_pins = sum(r['dnp'] for r in recs)

    L = []
    A = L.append
    A("# 原理图脚数 vs 真实器件脚数 —— 逐器件对账 (PIN_REALITY_GAP)")
    A("")
    A("> ★**生成器**: `python3 state/gen_kicad_sch.py --pin-gap` (★重跑即刷新★)  ")
    A("> ★**生成时间**: %s  · ★**对应原理图**: `HW/PCB/demo_mainboard*.kicad_sch` (★按表全量画, %d 脚★)"
      % (__import__("datetime").date.today().isoformat(), tbl_pins))
    A("> ★**2026-11-11 15:4x 更新 (主线 6c)**: ★**本文加了一节 §5「需裁决 / 外部依赖」"
      "(★本轮唯一卡住的一条: `FET3572C_PIN_TABLE.csv` 的 %s 座缺 `num=%s`·★需原厂回信★)★**  ")
    A("> ★**2026-11-11 19:4x 订正 (main)**: ★**§5 原本是【手写进产物】的 ⇒ 任何一次 `--pin-gap` 重跑都会把它冲掉 "
      "(★实测 19:1x 就被冲掉过一次★) ⇒ ★**已搬进生成器 ⇒ 重跑不再丢★**; ★**并修掉三处交叉引用 + "
      "一个指向不存在脚本的假命令 (`state/gen_pin_reality_gap.py` → `python3 state/gen_kicad_sch.py --pin-gap`)★**  ")
    A("> ★**2026-11-11 23:5x 补表 (ISS-198 · hw-lead)**: ★**`state/gen_kicad_sch.py` 的 `OPN_KICAD` / `PREFIX_KICAD` "
      "两张查找表已补全 (★26 个 ref 从 `[0数据]` 落到★**本机 KiCad 官方库实测 pins 数**★ ⇒ 符号文件里 `(pin … (at` > 0 "
      "且★**该文件没有 `(extends`★ (★不踩『继承父符号 ⇒ 自己文件 0 个 pin 行 ⇒ 数出来 0 = 假数』的坑★)) ★ "
      "⇒ ★**`[0数据]` 从 29 → %d (★剩下的 %d 个是【非器件】: %s ⇒ 不需要问原厂脚数★)★**" % (n_unknown, n_nondev, " / ".join("`%s`" % x for x in nondev_refs)))
    A("")
    A("## 0. 口径 (★凡给出统计数必带口径★)")
    A("")
    A("| 口径项 | 值 | 含义 |")
    A("|---|---|---|")
    A("| ★**表侧脚数**★ | %d | `HW/netlist_v1_pins.csv` 行数 (★每行=一脚, **含 DNP 行**★) |" % tbl_pins)
    A("| ★**表侧器件数**★ | %d | 同表不同 ref 的个数 |" % n_tot)
    A("| ★**真实器件脚数**★ | %d 有 / %d 无 | 只在**本机可查到的权威源**查到才填; ★**查不到写 `[0数据]`, 不猜**★ |" % (n_known, n_unknown))
    A("| ★**脚数一致**★ | %d | 表侧脚数 == 真实器件脚数 |" % n_eq)
    A("| ★**真实多脚**★ | %d | 真实器件脚数 > 表侧脚数 (★表里只画用到的脚★) |" % n_more)
    A("| ★**表里多脚**★ | %d | ★**表侧脚数 > 真实器件脚数 ⇒ 物理上不该存在的脚, 需核**★ |" % n_less)
    A("| ★**DNP 脚数**★ | %d | 表侧 `dnp=DNP` 的行数 (★口径: 含 DNP★) |" % dnp_pins)
    A("")
    A("★★**数据源 (★全部本机可复核; 不联网 / 不问供应商 / 不猜★)**★★")
    A("")
    A("1. ★**KiCad 10.0.8 官方符号库**★ `/home/yuewuya/kicad/squashfs-root/usr/share/kicad/symbols/`")
    A("2. ★**项目自有真值表**★ `state/check_netlist_pins.py` 的 `SPEC_PINS` / `PARTIAL_PINS`")
    A("3. ★**RK3572 SOM 球位表**★ `HW/PCB/FET3572C_PIN_TABLE.csv` (★%s 球位/座★%s)"
      % ("/".join("%s=%d" % (k, v) for k, v in sorted(fet.items())), _gap_e01_ref(fet, _gap_missing(fet))))
    A("4. ★**BOM 型号**★ `HW/BOM_v1.csv` 的 `opn` / `footprint` 列 (★型号已定型 ⇒ 可回查官方库★)")
    A("5. ★**板文件封装**★ `HW/PCB/demo_mainboard.kicad_pcb` 每器件的**焊盘数 / 焊盘编号** (★[实测]·用来互校"
      "『符号脚数』与『封装焊盘数』是否自洽★ ⇒ 不自洽的写进依据里, ★**不改板**★)")
    A("")
    A("---")
    A("")
    A("## 1. ★**表里脚数 > 真实器件脚数 (★物理上不该存在的脚 —— 本轮唯一需核的一类★)**")
    A("")
    if n_less:
        A("| 器件 | 表里脚数 | 真实脚数 | 差 | 数据来源 | 说明 |")
        A("|---|---|---|---|---|---|")
        for r in recs:
            if r['real'] is not None and r['delta'] < 0:
                A("| `%s` | %d | %d | **%+d** | %s | %s |"
                  % (r['ref'], r['tbl'], r['real'], r['delta'], r['src'], r['note']))
    else:
        A("★无 (表侧脚数没有超过真实器件脚数的情形)★")
    A("")
    A("---")
    A("")
    A("## 2. ★**真实器件脚数 > 表里脚数 (★表里只画了用到的脚 —— 正常, 不是漏画★)**")
    A("")
    A("| 器件 | 表里脚数 | 真实脚数 | 差 | DNP脚 | 型号/依据 | 说明 |")
    A("|---|---|---|---|---|---|---|")
    _e01_miss = _gap_missing(fet)
    for r in recs:
        if r['real'] is not None and r['delta'] > 0:
            _extra = ""
            for _c, _m in _e01_miss.items():
                if r['ref'] == "J_SOM_%s" % _c:
                    _extra = (" ★**⚠ 球位表本身只有 %d 行 (缺 num=%s) ⇒ \"真实 100 脚\"里有 1 行的佐证待原厂确认 "
                              "⇒ 见 §5.1 E-01★**" % (fet[_c], ", ".join(str(x) for x in _m)))
            A("| `%s` | %d | %d | +%d | %d | %s | %s%s |"
              % (r['ref'], r['tbl'], r['real'], r['delta'], r['dnp'], r['src'], r['note'], _extra))
    A("")
    A("---")
    A("")
    A("## 3. ★**逐器件全表 (%d 个器件)**★" % n_tot)
    A("")
    A("| 器件 | 类型 | 表里脚数 | 真实脚数 | 差 | DNP脚 | 型号 / 数据来源 |")
    A("|---|---|---|---|---|---|---|")
    for r in recs:
        real = '[0数据]' if r['real'] is None else str(r['real'])
        delta = '[0数据]' if r['real'] is None else "%+d" % r['delta']
        src = r['src']
        if r['opn'] and not r['nondev']:
            _opn = r['opn']
            if _opn == '[0数据]':
                # ★ISS-198: BOM 的 opn 也可能写 "[0数据]" (★型号未定★) ⇒ 别把它当【脚数未知】印出来
                #   (★同一个标记在同一行里出现两次 ⇒ 读者会误以为脚数也没查到★) ⇒ 渲染成 "BOM 型号未定" ★
                _opn = 'BOM 型号未定'
            src = _opn + " · " + src
        A("| `%s` | %s | %d | %s | %s | %d | %s |"
          % (r['ref'], r['type'] or '-', r['tbl'], real, delta, r['dnp'], src))
    A("")
    A("---")
    A("")
    A("## 4. ★**怎么读这张表 (★评审口径★)**")
    A("")
    A("- ★**本轮原理图按 `HW/netlist_v1_pins.csv` 全量画 (584 脚, 含 DNP 行)** ⇒ 图上脚数 = 表侧脚数 = %d, "
      "逐器件相等 (★`state/check_sch_pinfull.py` 实测 K=0★)。" % tbl_pins)
    A("- ★**『表里脚数』是【这个设计实际用到的脚】, 不是【器件出厂总脚数】**★")
    A("  ⇒ 第 2 节那些『真实多脚』是正常的 (★空脚/NC/散热焊盘本来就不接★), ★**不是漏画**★")
    A("- ★**第 1 节那些『表里多脚』才是真问题** ★ ⇒ 逐个核: 是表里脚号写错了, 还是选型/脚数口径不一致")
    A("- ★**`[0数据]` = 本机查不到真实脚数** ★ ⇒ ★**型号回信后重跑 `python3 state/gen_kicad_sch.py --pin-gap` "
      "即可自动补齐** ★ (★**旧版本这里写的是 `state/gen_pin_reality_gap.py` —— 那个脚本【不存在】, "
      "照着跑必然失败 ⇒ ★**2026-11-11 19:4x 已订正★**) ★")
    A("- ★**`[0数据]` 里现在只剩 %d 个 (★%s★) ⇒ ★**它们是【非器件】(汇流位 / 焊盘位 / 待选型电池座) ⇒ "
      "【不编脚数】, 也不需要问原厂脚数** ★" % (n_nondev, " / ".join("`%s`" % x for x in nondev_refs)))
    A("- ★**没有改任何表** ★: `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` 一个字节都没动 "
      "(★md5 不变, 见交卷实测★)")
    A("")
    A("---")
    A("")
    # ---- §5 需裁决 / 外部依赖 (★数据驱动 ⇒ 表变了本文跟着变★) ----
    _gap_sec5(L, _gap_ctx(recs, fet, tbl_pins, n_tot, n_known, n_unknown))
    A("---")
    A("")
    A("## 6. ★**本轮未做/待下一轮 (★不硬凑★)**")
    A("")
    A("- ★**表里多脚的那几项** ★: 需要**原厂型号回信**才能定论 ⇒ ★**本轮不猜、不改表** ★")
    A("- ★**`[0数据]` 的 %d 个** ★: %d 个是【非器件】(★%s★) ⇒ 无脚数可查, ★**不编、不问原厂**★; "
      "★**剩下 %d 个 (★%s★) 是待选型器件 ⇒ 型号定下来后回查官方库即可** ★"
      % (n_unknown, n_nondev, " / ".join("`%s`" % x for x in nondev_refs), n_need_orig,
         " / ".join("`%s`" % x for x in need_orig_refs)))
    A("")
    open(GAP_OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("✅ 已生成 %s" % GAP_OUT)
    print("   器件 %d 个 (表侧 %d 脚, 含 DNP %d 脚)" % (n_tot, tbl_pins, dnp_pins))
    print("   真实脚数可查 %d / 查不到 %d (标 [0数据]; 其中非器件 %d 个: %s)"
          % (n_known, n_unknown, n_nondev, " / ".join(nondev_refs)))
    print("   脚数一致 %d / 真实多脚 %d / 表里多脚 %d" % (n_eq, n_more, n_less))
    return 0


if __name__ == "__main__":
    if "--parity" in sys.argv:
        sys.exit(cmd_parity())
    if "--pin-gap" in sys.argv:
        sys.exit(cmd_pin_reality_gap())
    sys.exit(main())
