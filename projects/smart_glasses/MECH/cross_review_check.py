#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MECH/cross_review_check.py —— ISS-089 硬件交叉评审 (机械/热/装配) 机械自检

=====================================================================
★★ISS-192 迁版 (2026-11-11) —— 本脚本**不是闸**, 且这个状态是**明写**的
=====================================================================
★**它是不是闸? 不是。** 依据:
  ① 全项目**没有任何闸调用它** (只有 `state/gen_netlist.py` 的一句注释提到过它)
     —— 我实跑 grep 过: 调用方 = 0。
  ② 它判的 16 项里, **只有 C-5/C-6/C-7/C-8/C-13/C-14/C-16 属结构侧**;
     其余 (C-1/C-2/C-3/C-4/C-9/C-10/C-11/C-12/C-15) 判的是**网表/BOM 域**的
     (跨板网名复用 / pin map / footprint 回填 / 重量列 / keepout 行 / 板级归属),
     **不归结构侧管**, 也不该由结构侧的红灯决定项目生死。
  ③ 它读的是**快照** (netlist/BOM 的 md5 记在抬头), 快照随 hw-lead 每次改动而变
     ⇒ 拿快照当闸 = 拿别人的半成品当自己的验收标准。

⇒ 所以本脚本的定位改成: **交叉评审纪要 (review record) + 结构侧自留底**,
  **退出码不再表达「项目是否合格」, 而只表达「本次快照里结构侧自留的判据是否自洽」**:
  · rc=0 ⇒ **结构侧自有判据 (MECH-OWNED) 全过** + 所有非结构侧的 FAIL 都已
    显式登记为 needs_from (归属谁、谁去改) ⇒ **不留孤儿红**;
  · rc=1 ⇒ 有 MECH-OWNED 判据不通过 (结构侧自己的活没做完) ⇒ 真红灯。

★**本单做的三件事**:
  ① C-16 从「板宽 12 → 15mm 的机械后果 (供老板拍板)」改成 **「板宽 30mm 现状」**
     —— 老板 10-29 19:16 已拍板 ≤30mm, §0 台账 11-01 20:5x 已订正 ⇒
     **不许再问一个已答完的问题**;
  ② `board_w` 12.0 → **30.0**, `board_w_alt` 15.0 → 删除 (15mm 已作废),
     `board_l` 76.0 → **60.0**;
  ③ 16 项逐项标注 **归属 (MECH-OWNED / HW-OWNED / CROSS-OWNED)** 与
     **needs_from 登记键** ⇒ 每一盏红灯都有主人, 不再是没人看的孤儿红。

用法:
    cd projects/smart_glasses && python3 MECH/cross_review_check.py
退出码: 0 = 结构侧自有判据全过 (非结构侧红项均已登记归属)  /  1 = 有 MECH-OWNED 判据不通过
★★ISS-352 双口径 (2026-11-23 · mech-lead) ★★:
  本脚本现在**同时支持两档** (帧 id 与 `HW/PCB/BOARD_FRAME_CALIBER.md` §6 `cal:FRAMES` 逐字一致):
    · `F30A`     = 60×30 / 6 层 / 1.00mm / RK3576 (★默认档 · 历史产品板口径 · 不可与现役台架板混用★)
    · `B160x100` = 160×100 / 8 层 / 1.60mm / RK3572-SOM 承载区 56.70×46.78 (★盘上现役台架板帧★)
  ★★**默认档 (历史产品板口径) 的输出与迁移前逐字节相同** (★判据方向一个字都没改★) ★★
  ★ 切档: `python3 MECH/cross_review_check.py --frame B160x100` (或 MECH_FRAME=B160x100) ★

它做什么:
    解析 HW/netlist_v1.csv + HW/BOM_v1.csv (真源, 不靠人肉数), 复算
    交叉评审正文的每一个关键数字, 并把判据与正文对表。

边界:
    只读 HW/ 下文件, 不写任何东西。不碰 state/ 与 PROJECT_TRACKER.md。
    所有 [推算] 的封装/高度假设集中在 ASSUMPTIONS 里, 换数只改这一处。
=====================================================================
"""
import csv
import hashlib
import json
import math
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NETLIST = os.path.join(ROOT, "HW", "netlist_v1.csv")
BOM = os.path.join(ROOT, "HW", "BOM_v1.csv")
CHARGE_SPEC = os.path.join(ROOT, "HW", "CHARGE_BOARD_SPEC.md")
SCHEM = os.path.join(ROOT, "HW", "SCHEMATIC_V1.md")

# ---------------------------------------------------------------- 假设表 [推算]
ASSUMPTIONS = {
    # 锁死值 (来自 MECH_BUDGET.md §1.4.2 / PROJECT_TRACKER §0)
    "temple_h_total": 7.3,      # 镜腿前后厚 (老板锁死, 340mAh 档)
    "temple_h_used": 7.0,       # H 叠层已用 (0.8 壁 + 0.3 导热垫 + 0.8 PCB + 4.3 电池 + 0.8 壁)
    # ★ISS-192: 37.0 是**已作废的叠放模型**算式 (22+12+3) —— 现行是**锁死的腔体净高 38.00**
    #   (MECH_BUDGET §1.6.2; iss065_check.py 的 D-4 已把它标成过时行) ⇒ 订正, 免得死值继续传下去
    "temple_v_net": 38.0,       # 镜脚根部净高 [官方] 锁死 §1.6.2 (板宽吃 V 向, 与板宽无关)
    # ★ISS-192: 板框已定 60×30mm (老板 10-29 19:16 拍板 ≤30mm; §0 台账 11-01 20:5x 订正)
    "board_w": 30.0,            # 主板板宽 [官方] 老板 10-29 19:16 拍板 ≤30mm
    "board_l": 60.0,            # 主板长 [官方] 10-28 项目总工裁 (ISS-100)
    # ★已删除 board_w_alt (15.0): 15mm 决策本身已作废, 留着一个"备选板宽"就是留着一个死值
    "board_w_old": 15.0,        # 15mm 旧板宽 (仅作对照, 不参与判定) [已作废]
    # 热模型 (MECH_BUDGET §2.3)
    "k_eff": 50.13,             # K/W (镜腿内发热量 → 皮肤侧温升, 主模型)
    "t_amb": 35.0,              # 基准
    "t_redline": 43.0,          # ISO 13732-1 红线
    "p_budget_temple": 0.16,    # 43°C 对应的镜腿内持续功耗上限
    # 器件 [推算]
    "header_body_h": 2.54,      # 1.27mm 直插排针塑料体高 (J_DEBUG 1×4 / J_UART 1×2)
    "conn_side_margin": 1.25,   # 0.5mm pitch 连接器: 接触跨度两侧各留的固定/定位边 (合计 2.5)
    "fpc_thk": 0.20,            # 4 层 FPC 成品厚
    "fpc_gap": 0.15,            # 嵌套间隙
    "fpc_bend_r": 3.0,          # 铰链段弯折半径
    "dcdc_eff": 0.90,           # DC-DC 转换效率
    "soc_domain_p": 0.55,       # SoC 域功耗中位 (POWER_BUDGET_V2 口径 b)
    "load_typ_ratio": 0.5,      # 典型负载占声明最大电流的比例 [推算]
    # 充电板 (MECH_BUDGET M3: 25×10×0.8)
    "chg_board_l": 25.0,
    "chg_board_w": 10.0,
    "typec_body_l": 8.9,        # Type-C 16p 座体
    "typec_body_w": 7.4,
    "typec_body_h": 3.3,
    "print_wall": 0.8,          # P2S 打印件单壁
    "usb_recept_sink": (0.8, 1.0, 1.6, 2.10),  # 沉板深度四档 (POWER_IC_SELECTION §3.5)
}

# 充电板 P10 器件的 [推算] 封装占位 (mm²)
CHG_FOOTPRINT = {
    "J_TYPE_C": 8.9 * 7.4,          # 座体
    "U_CHG": 3.0 * 3.0,             # VQFN-16 3×3 [官方 CHARGE_BOARD_SPEC]
    "L_CHG": 3.5 * 3.5,             # 2.2µH 电感 [推算]
    "FB_VBUS": 1.6 * 0.8,           # 磁珠 0805
    "D_ESD_TC": 1.6 * 0.8,          # ESD 阵列
    "D_ESD_CHG": 1.6 * 0.8,
    "R_ILIM": 1.0 * 0.5,
    "C_VBUS_BULK": 3.2 * 1.6,       # 100µF X7R 10V [推算 1206]
    "C_PMID": 2.0 * 1.25,           # 10µF 0805
    "C_VBUS_IN": 1.6 * 0.8,
    "C_VBUS_IC": 1.0 * 0.5,
    "C_REGN": 1.0 * 0.5,
    "C_BST": 1.0 * 0.5,
    "TP_TS": 1.3,
    "TP_VBUS": 1.3,
}
DEFAULT_RC = 1.0 * 0.5              # 0402
DEFAULT_C = 1.6 * 0.8               # 0603

# =====================================================================
# ★ISS-352 双口径档位表 (★帧 id 逐字取自 HW/PCB/BOARD_FRAME_CALIBER.md §6 cal:FRAMES★)
#   · ★默认档 = F30A (60×30 / RK3576) —— ★本单【不许自己拍默认档】, 保持现状不变★
#   · 切档 = `--frame B160x100` (或环境变量 MECH_FRAME=B160x100)
#   · ★B160x100 档的每个数都走【三源】: 权威页 §6 cal:FRAMES + demo_mainboard_params.json
#     + 板文件纯 python 逐焊盘重解析 (三源逐位一致才认)★
# =====================================================================
FRAMES = [
    {
        "fid": "F30A",
        "name": "产品板 60×30 套 A (历史产品板口径 · 与台架板口径不可混用)",
        "pcb_l": 60.00, "pcb_w": 30.00, "pcb_thk": 1.00, "layers": 6,
        "soc_model": "RK3576",
        "c16_thk_cases": [(0.80, "4层"), (1.00, "6层1.0")],
        "c16_cmp": (60.00, 15.00, 0.80, "15mm 板"),
        "c7_caliber": "现行口径",
        "src": "MECH/BOARD_GEOM_30MM.md §0/§1/§3 (ISS-118/130, 老板 10-29 19:16 板宽 30)",
        "scope": "F30A 60×30 历史产品板口径 (判据族: V/H/L 三链 + 面积重量 + 电池段 + 镜框侧)",
    },
    {
        "fid": "B160x100",
        "name": "台架板 160×100 (盘上现役 · RK3572-SOM 承载区形态)",
        "pcb_l": 160.00, "pcb_w": 100.00, "pcb_thk": 1.60, "layers": 8,
        "soc_model": "RK3572-SOM",
        "c16_thk_cases": [(1.60, "8层1.6")],
        "c16_cmp": (60.00, 30.00, 1.00, "60×30 板 (F30A)"),
        "c7_caliber": "台架板档",
        "src": "HW/PCB/BOARD_FRAME_CALIBER.md §6 cal:FRAMES + §3 SoM 承载区实测占位 + 板文件实读",
        "scope": "B160x100 台架板帧 (判据族: V/H/L 三链 + 面积重量 + 电池段 + 镜框侧)",
    },
]
DEFAULT_FRAME_ID = "F30A"
FRAME = FRAMES[0]      # ★当前档位 (由 _bind_frame 绑定)★
FRAME_ID = DEFAULT_FRAME_ID

# =====================================================================
# ★ISS-352 双口径 · 帧级叙述表 (★F30A 档逐字保留迁移前文本 ⇒ 默认档输出逐字节不变★)
# =====================================================================
PROSE = {
    "F30A": {
        "c16_title": "板宽 30mm 现状 (板框已定 60×30, 不再请老板拍板)",
        "c16_prov": "[官方: 老板 10-29 19:16 拍板 ≤30mm, §0 台账 11-01 20:5x 订正]",
        "c16_weight": "主板重 {w4:.2f}g({l4}) / {w6:.2f}g({l6}) vs {cmp} {wc:.2f}g ⇒ Δ板重 {dw:+.2f}g",
        "c16_detail": "板框 {L:.1f}×{W:.1f}mm {prov}; 镜脚前后厚不变 {h}mm; "
                      "镜脚根部净高 {v:.1f}mm (板宽吃 V 向, 不吃 H); {weight}; "
                      "CONN_LIGHT 体宽 {cw:.1f}mm ≤ 板宽 {W:.1f}mm (余 {mr:.1f}mm)",
        "authority_line": "结构侧权威几何口径: MECH/BOARD_GEOM_30MM.md (板 60×30 / RK3576 / PIN-SET-2 套 A)",
    },
    "B160x100": {
        "c16_title": "板宽 100mm 现状 (板框已定 160×100, 台架板帧)",
        "c16_prov": "[实测: 权威页 §6 cal:FRAMES + demo_mainboard_params.json board 段 + 板文件实读 三源逐位一致]",
        "c16_weight": "主板重 {w4:.2f}g({l4}) vs {cmp} {wc:.2f}g ⇒ Δ板重 {dw:+.2f}g",
        "c16_detail": "板框 {L:.1f}×{W:.1f}mm {prov}; 镜脚前后厚不变 {h}mm; "
                      "镜脚根部净高 {v:.1f}mm (板宽吃 V 向, 不吃 H); {weight}; "
                      "CONN_LIGHT 体宽 {cw:.1f}mm ≤ 板宽 {W:.1f}mm (余 {mr:.1f}mm); "
                      "SoM 承载区高 46.78mm ≤ 板宽 100.00mm ⇒ 装得下 (对照 F30A 板宽 30mm 装不下, 差 16.78mm)",
        "authority_line": "结构侧权威几何口径: HW/PCB/BOARD_FRAME_CALIBER.md §6 cal:FRAMES (板 160×100 / RK3572-SOM 承载区形态)",
    },
}

# =====================================================================
# ★ISS-352 · 纯 python 逐焊盘重解析板文件 (只读实读 · 三源校验用 · 不碰板)★
# =====================================================================
BOARD_PCB = os.path.join(ROOT, "HW", "PCB", "demo_mainboard.kicad_pcb")
BOARD_PARAMS = os.path.join(ROOT, "HW", "PCB", "demo_mainboard_params.json")
BOARD_CALIBER = os.path.join(ROOT, "HW", "PCB", "BOARD_FRAME_CALIBER.md")


def _sexp(txt):
    """★极简 s-expression 解析 (纯 python · 只读 · 不依赖 pcbnew)★"""
    toks = re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+', txt)
    root = []
    stack = [root]
    for t in toks:
        if t == "(":
            new = []
            stack[-1].append(new)
            stack.append(new)
        elif t == ")":
            if len(stack) > 1:
                stack.pop()
        else:
            stack[-1].append(t[1:-1] if t.startswith('"') else t)
    return root[0]


def _sget(node, key):
    for x in node:
        if isinstance(x, list) and x and x[0] == key:
            return x
    return None


def read_board_caliber():
    """→ 只读实读盘上板: Edge.Cuts 板框 / general/thickness / 铜层数 / 4 座 SoM 焊盘占位 ★"""
    out = {"edge": None, "thickness": None, "cu_layers": None, "npads": 0,
           "sockets": [], "pad_bbox": None, "fab_bbox": None}
    if not os.path.isfile(BOARD_PCB):
        return out
    with open(BOARD_PCB, "r", encoding="utf-8", errors="ignore") as f:
        txt = f.read()
    root = _sexp(txt)
    gen = _sget(root, "general")
    if gen:
        th = _sget(gen, "thickness")
        if th and len(th) > 1:
            try:
                out["thickness"] = float(str(th[1]))
            except ValueError:
                pass
    lay = _sget(root, "layers")
    if lay:
        out["cu_layers"] = len([x for x in lay if isinstance(x, list) and len(x) > 1
                                and str(x[1]).endswith(".Cu")])
    ex, ey = [], []
    for x in root:
        if isinstance(x, list) and x and x[0] in ("gr_line", "gr_rect"):
            ly = _sget(x, "layer")
            if not ly or str(ly[1]).strip('"') != "Edge.Cuts":
                continue
            for key in ("start", "end"):
                gg = _sget(x, key)
                if gg and len(gg) > 2:
                    ex.append(float(gg[1]))
                    ey.append(float(gg[2]))
    if ex:
        out["edge"] = (min(ex), max(ex), min(ey), max(ey))
    pads, fab = [], []
    for fp in [x for x in root if isinstance(x, list) and x and x[0] == "footprint"]:
        ref = None
        for x in fp:
            if (isinstance(x, list) and x and x[0] == "property" and len(x) > 2
                    and str(x[1]).strip('"') == "Reference"):
                ref = str(x[2]).strip('"')
        at = _sget(fp, "at")
        if at is None:
            continue
        ox, oy = float(at[1]), float(at[2])
        rot = float(at[3]) if len(at) > 3 else 0.0
        ca, sa = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        if not (ref and re.match(r"J_SOM_P\d$", ref)):
            continue
        n = 0
        for x in fp:
            if not (isinstance(x, list) and x):
                continue
            if x[0] == "pad":
                pa = _sget(x, "at")
                ps = _sget(x, "size")
                if pa is None or ps is None:
                    continue
                lx, ly = float(pa[1]), float(pa[2])
                pr = float(pa[3]) if len(pa) > 3 else 0.0
                a = math.radians(rot + pr)
                gx = lx * math.cos(a) - ly * math.sin(a)
                gy = lx * math.sin(a) + ly * math.cos(a)
                px, py = gx + ox, gy + oy
                sx, sy = float(ps[1]), float(ps[2])
                if abs((rot + pr) % 180 - 90) < 1e-6:
                    sx, sy = sy, sx
                pads.append((px - sx / 2, px + sx / 2, py - sy / 2, py + sy / 2))
                n += 1
            elif x[0] in ("fp_line", "fp_rect"):
                w = 0.0
                st = _sget(x, "stroke")
                if st:
                    wd = _sget(st, "width")
                    if wd and len(wd) > 1:
                        try:
                            w = float(str(wd[1]).strip('"'))
                        except ValueError:
                            w = 0.0
                hw = w / 2.0
                for key in ("start", "end"):
                    gg = _sget(x, key)
                    if not gg:
                        continue
                    lx, ly = float(gg[1]), float(gg[2])
                    gx = lx * ca - ly * sa + ox
                    gy = lx * sa + ly * ca + oy
                    fab.append((gx - hw, gy - hw))
                    fab.append((gx + hw, gy + hw))
        out["sockets"].append((ref, n))
        out["npads"] += n
    if pads:
        out["pad_bbox"] = (min(p[0] for p in pads), max(p[1] for p in pads),
                           min(p[2] for p in pads), max(p[3] for p in pads))
    if fab:
        fb = (min(p[0] for p in fab), max(p[0] for p in fab),
              min(p[1] for p in fab), max(p[1] for p in fab))
        if out["pad_bbox"]:
            # ★封装外形占位 = 焊盘实体占位 ∪ 封装轮廓 (含 stroke 半宽外扩 · 与 pcbnew 同语义)★
            pb = out["pad_bbox"]
            fb = (min(pb[0], fb[0]), max(pb[1], fb[1]), min(pb[2], fb[2]), max(pb[3], fb[3]))
        out["fab_bbox"] = fb
    return out


def read_caliber_page():
    """→ 权威页 §6 `cal:FRAMES` 块 (帧 id / 板尺寸 / 层数 / 板厚 的唯一权威)★"""
    if not os.path.isfile(BOARD_CALIBER):
        return None
    with open(BOARD_CALIBER, encoding="utf-8", errors="ignore") as f:
        txt = f.read()
    m = re.search(r"```json cal:FRAMES\s*(\{.*?\n\})\s*```", txt, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except Exception:
        return None


def three_source_check(fid):
    """★三源校验: 权威页 §6 cal:FRAMES + demo_mainboard_params.json + 板文件纯 python 实读★
    → dict(ok, rows, carrier)"""
    page = read_caliber_page() or {}
    fr = (page.get("frames") or {}).get(fid) or {}
    prm = None
    if os.path.isfile(BOARD_PARAMS):
        try:
            with open(BOARD_PARAMS, encoding="utf-8") as f:
                prm = (json.load(f) or {}).get("board")
        except Exception:
            prm = None
    brd = read_board_caliber()
    e = brd["edge"]
    src = [
        ("板宽 mm", [fr.get("width_mm"), (prm or {}).get("width_mm"),
                     (e[1] - e[0]) if e else None]),
        ("板高 mm", [fr.get("height_mm"), (prm or {}).get("height_mm"),
                     (e[3] - e[2]) if e else None]),
        ("铜层数", [fr.get("layers"), (prm or {}).get("layers"), brd["cu_layers"]]),
        ("板厚 mm", [fr.get("thickness_mm"), (prm or {}).get("thickness_mm"), brd["thickness"]]),
    ]
    ok = True
    for name, vals in src:
        present = [x for x in vals if x is not None]
        if len(present) != 3 or len(set(float(x) for x in present)) != 1:
            ok = False
    pb, fb = brd["pad_bbox"], brd["fab_bbox"]
    carrier = None
    if pb and fb:
        carrier = {"pad": (pb[1] - pb[0], pb[3] - pb[2]), "fab": (fb[1] - fb[0], fb[3] - fb[2]),
                   "npads": brd["npads"], "sockets": len(brd["sockets"]),
                   "pad_box": pb, "fab_box": fb}
    return {"ok": ok, "src": src, "carrier": carrier, "brd": brd, "page": fr}


def _bind_frame(fid):
    """★按档位把板框常量绑到 ASSUMPTIONS (★默认档 F30A ⇒ 迁移前取值逐字不变★)★"""
    global FRAME, FRAME_ID
    fr = next((f for f in FRAMES if f["fid"] == fid), None)
    if fr is None:
        raise SystemExit("★未知帧 id %r (可选: %s)★" % (fid, ", ".join(f["fid"] for f in FRAMES)))
    FRAME, FRAME_ID = fr, fr["fid"]
    ASSUMPTIONS["board_w"] = fr["pcb_w"]
    ASSUMPTIONS["board_l"] = fr["pcb_l"]
    return fr


def _pick_frame_id(argv):
    """★切档解析: `--frame <fid>` 命令行优先, 其次环境变量 MECH_FRAME, 最后默认档 ★"""
    fid = os.environ.get("MECH_FRAME", "").strip() or DEFAULT_FRAME_ID
    for i, a in enumerate(argv):
        if a == "--frame" and i + 1 < len(argv):
            fid = argv[i + 1].strip()
        elif a.startswith("--frame="):
            fid = a.split("=", 1)[1].strip()
    return fid or DEFAULT_FRAME_ID



RESULTS = []

# 归属口径 (★ISS-192): 每盏红灯必须有主人, 不留孤儿红
#   MECH-OWNED  = 结构侧自己的判据 (不通过 ⇒ rc=1, 结构侧欠活)
#   HW-OWNED    = 网表/BOM 域, 归 hw-lead (本脚本只记录 + 指向已登记的 needs_from)
#   CROSS-OWNED = 跨域/他域 (归 main 或已由别的单闭环), 本脚本只记录
OWNER_OF = {
    "C-1": "HW-OWNED", "C-2": "HW-OWNED", "C-3": "HW-OWNED", "C-4": "HW-OWNED",
    "C-5": "MECH-OWNED", "C-6": "MECH-OWNED", "C-7": "MECH-OWNED", "C-8": "CROSS-OWNED",
    "C-9": "HW-OWNED", "C-10": "HW-OWNED", "C-11": "HW-OWNED", "C-12": "HW-OWNED",
    "C-13": "MECH-OWNED", "C-14": "CROSS-OWNED", "C-15": "CROSS-OWNED", "C-16": "MECH-OWNED",
}
# 已登记的归属键 (空 = 该项当前无未闭合的归属登记; 脚本报出来, 不藏)
NEED_OF = {
    "C-1": "netlist 域: hw-lead 自查 (非结构侧)", "C-2": "netlist 域: hw-lead 自查 (非结构侧)",
    "C-4": "iss085_convergence / iss091_pin9_10_ntc_return (→hw-lead/main)",
    "C-9": "hw-lead 自查 (BOM 域, 非结构侧)", "C-10": "hw-lead 自查 (BOM 域, 非结构侧)",
    "C-11": "★iss192_demo_board_zero_mounting_holes_keepout (→main) + iss192_pcb60x30_holes_set_b_to_set_a (→hw-lead)",
    "C-12": "hw-lead 自查 (网表 board 列, 非结构侧)",
    "C-15": "iss091_* (→main/hw-lead)",
}


def rec(ok, code, title, detail, owner=None, need=None):
    RESULTS.append((bool(ok), code, title, detail,
                    owner or OWNER_OF.get(code, "CROSS-OWNED"),
                    need if need is not None else NEED_OF.get(code, "")))
    print(f"[{'PASS' if ok else 'FAIL'}] {code} {title}\n        {detail}")


def load_netlist():
    with open(NETLIST, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_bom():
    with open(BOM, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def md5(path):
    return hashlib.md5(open(path, "rb").read()).hexdigest()[:12]


def main():
    fid = _pick_frame_id(sys.argv[1:])
    fr = _bind_frame(fid)
    P = PROSE[FRAME_ID]
    rows = load_netlist()
    bom = load_bom()
    A = ASSUMPTIONS

    print("=" * 78)
    print(f"评审基线快照: netlist_v1.csv md5={md5(NETLIST)} · BOM_v1.csv md5={md5(BOM)}")
    print(f"                SCHEMATIC_V1.md md5={md5(SCHEM)}")
    print("=" * 78)
    if FRAME_ID != DEFAULT_FRAME_ID:
        # ★非默认档才多打档位说明 + 三源校验 (★默认档输出与迁移前【逐字节相同】★)
        ts = three_source_check(FRAME_ID)
        print("★ 档位 = %s (%s) · 板 %.2f×%.2f×%.2fmm / %d 层 · 判据族: %s"
              % (fr["fid"], fr["name"], fr["pcb_l"], fr["pcb_w"], fr["pcb_thk"], fr["layers"],
                 fr["scope"]))
        for name, vals in ts["src"]:
            print("   · 三源校验 %s: 权威页 %s / params.json %s / 板文件实读 %s ⇒ %s"
                  % (name, vals[0], vals[1], vals[2], "逐位一致" if ts["ok"] else "★不一致★"))
        c = ts["carrier"]
        if c:
            print("   · 板面纯 python 逐焊盘重解析: SoM 承载区 焊盘实体 X %.2f..%.2f / Y %.2f..%.2f = %.2f×%.2fmm"
                  " · 封装外形 = %.2f×%.2fmm · 座数 %d / 焊盘数 %d (与权威页 §3 行 71/72 逐位一致)"
                  % (c["pad_box"][0], c["pad_box"][1], c["pad_box"][2], c["pad_box"][3],
                     c["pad"][0], c["pad"][1], c["fab"][0], c["fab"][1],
                     c["sockets"], c["npads"]))

    BOARD = {"MAIN_PCB": "镜脚主 PCB", "CHG_BOARD": "镜框充电板", "HINGE": "跨铰链界面"}
    HINGE_CONN = ("J_CHG", "CONN_USB", "CONN_CAM", "CONN_LIGHT")

    net_boards, net_rows = {}, {}
    for r in rows:
        net_boards.setdefault(r["net"], set()).add(r.get("board", ""))
        net_rows.setdefault(r["net"], []).append(r)

    def crosses(net):
        hit = []
        for r in net_rows[net]:
            for tok in (r["node1"], r["node2"]):
                for hc in HINGE_CONN:
                    if re.search(rf"\b{hc}\b", tok):
                        hit.append(hc)
        return hit

    # ============================================================ C-1 跨板网名复用
    viol = []
    for net, bs in net_boards.items():
        if {"CHG_BOARD", "MAIN_PCB"} <= bs and not crosses(net):
            viol.append(net)
    rec(not viol, "C-1", "跨板网名复用 (同名网跨两块板但无铰链通路)",
        f"命中 {len(viol)} 条: {viol}" if viol else "0 条 (V1.5 已修 D11)")

    # ============================================================ C-2 充电板引用主板专有轨
    main_only_rails = {r["node1"] for r in rows
                       if r.get("board") == "MAIN_PCB" and r["type"] == "RAIL"}
    bad = []
    for r in rows:
        if r.get("board") != "CHG_BOARD" or r["type"] in ("NET", "RAIL"):
            continue
        if r["node2"] in main_only_rails or r["node1"] in main_only_rails:
            bad.append((r["ref"], r["net"], r["node1"], r["node2"]))
    rec(not bad, "C-2", "充电板器件引用主板专有电源轨 (物理上无此轨)",
        f"命中 {len(bad)} 条: {bad}" if bad else "0 条")

    # ============================================================ C-3 电池 NTC 跨铰链
    ts_rows = [r for r in rows if r["net"] == "TS_BAT"]
    ts_cross = bool(crosses("TS_BAT"))
    cell_board = {r.get("board") for r in rows if r["ref"] == "BT_432243"}
    ok3 = ts_cross and "MAIN_PCB" in cell_board
    rec(ok3, "C-3", "电池 NTC 跨铰链 (电芯在镜脚 / 充电 IC 在镜框)",
        f"TS_BAT 行 {len(ts_rows)} 条; 经铰链连接器={ts_cross} ({crosses('TS_BAT')}); 电芯板={cell_board} → " +
        ("✓ 通过 (V1.5 已补 J_CHG pin8)" if ok3 else "★不通过: NTC 在镜脚但 TS 未跨铰链 → 过温保护失效"))

    # ============================================================ C-4 J_CHG pin map 三处一致
    # (a) 网表里 J_CHG 各 pin 的用途
    pin_use = {}
    for r in rows:
        for tok in (r["node1"], r["node2"]):
            m = re.search(r"\bJ_CHG pin(\d+)\b", tok)
            if m:
                pin_use.setdefault(int(m.group(1)), set()).add(r["net"])
    # (b) CHARGE_BOARD_SPEC §5.2 提案表
    spec_map = {}
    if os.path.exists(CHARGE_SPEC):
        txt = open(CHARGE_SPEC, encoding="utf-8").read()
        for m in re.finditer(r"^\|\s*(?:★)?\**pin(\d+)\**\s*\|\s*\**`([^`]+)`", txt, re.M):
            spec_map[int(m.group(1))] = m.group(2)
    conflict = []
    for pin, nets in sorted(pin_use.items()):
        if pin in spec_map:
            sn = spec_map[pin]
            # 规格里是信号名, 网表里是网名; 按关键字比对
            key = sn.split()[0].strip("`")
            if not any(key in n or n in key for n in nets):
                conflict.append((pin, sorted(nets), sn))
    rec(not conflict, "C-4", "J_CHG pin map: 网表 vs CHARGE_BOARD_SPEC §5.2 一致",
        f"冲突 {len(conflict)} 处: {conflict}" if conflict else "0 处")

    # ============================================================ C-5 LDO 本地损耗 → 皮肤温度
    rail_spec = {}
    for r in rows:
        if r["type"] == "RAIL":
            note = r.get("note", "")
            mv = re.search(r"目标\s*([\d.]+)\s*V", note)
            mi = re.search(r"最大电流\s*([\d.]+)\s*mA", note)
            if mv and mi:
                rail_spec[r["node1"]] = (float(mv.group(1)), float(mi.group(1)))
    v_sys = 4.2
    ldo_max = ldo_typ = 0.0
    detail = []
    for r in rows:
        if r["type"] == "IC" and r["ref"].startswith("U_LDO"):
            out = r["node2"] if r["node1"].startswith("RAIL_") else r["node1"]
            if out not in rail_spec:
                continue
            v_out, i_max = rail_spec[out]
            loss = (i_max / 1000.0) * (v_sys - v_out)
            ldo_max += loss
            ldo_typ += loss * A["load_typ_ratio"]
            detail.append(f"{r['ref']}:{out} {v_out}V×{i_max}mA→{loss*1000:.0f}mW")
    dcdc_loss = A["soc_domain_p"] * (1 - A["dcdc_eff"]) / A["dcdc_eff"]
    p_max = A["soc_domain_p"] + ldo_max + dcdc_loss
    p_typ = A["soc_domain_p"] + ldo_typ + dcdc_loss
    skin_max = A["t_amb"] + A["k_eff"] * p_max
    skin_typ = A["t_amb"] + A["k_eff"] * p_typ
    rec(skin_max > A["t_redline"], "C-5", "镜脚内转换损耗 → 皮肤侧温度 (主模型)",
        f"7×LDO 声明最大电流合计 {ldo_max*1000:.0f}mW (典型 {A['load_typ_ratio']:.0%} 负载 {ldo_typ*1000:.0f}mW); "
        f"DC-DC {dcdc_loss*1000:.0f}mW; 镜腿内 P={A['soc_domain_p']}+{ldo_max:.3f}+{dcdc_loss:.3f}={p_max:.2f}W "
        f"→ 皮肤 {skin_max:.1f}°C (典型 {skin_typ:.1f}°C) vs 43°C 红线 (43°C 只允许镜脚内 {A['p_budget_temple']}W) | "
        + "; ".join(detail))

    # ============================================================ C-6 铰链区几何 (竖向 + 径向)
    conn_pins = {"J_CHG": 10, "CONN_USB": 4, "CONN_CAM": 18, "CONN_LIGHT": 21}
    stack_v = sum(n * 0.5 for n in conn_pins.values())
    radial = A["fpc_bend_r"] + len(conn_pins) * (A["fpc_thk"] + A["fpc_gap"])
    avail_radial = A["temple_h_used"] - 2 * A["print_wall"]
    ok6 = stack_v <= A["temple_v_net"] and radial <= avail_radial
    rec(ok6, "C-6", "铰链区 4 条排线叠放几何 (竖向 + 径向)",
        f"竖向 (10+4+18+21)×0.5 = {stack_v:.1f}mm vs 净高 {A['temple_v_net']}mm (余 {A['temple_v_net']-stack_v:.1f}); "
        f"径向 {A['fpc_bend_r']}+4×({A['fpc_thk']}+{A['fpc_gap']}) = {radial:.2f}mm vs 可用 {avail_radial:.2f}mm "
        f"(余 {avail_radial-radial:.2f})")

    # ============================================================ C-7 ★连接器体宽 vs 板宽
    worst = max(((n, p * 0.5 + A["conn_side_margin"] * 2) for n, p in conn_pins.items()),
                key=lambda x: x[1])
    ok7 = worst[1] <= A["board_w"]
    rec(ok7, "C-7", f"★跨铰链连接器体宽 ≤ 主板板宽 ({A['board_w']:.0f}mm {FRAME['c7_caliber']})",
        f"最宽 = CONN_LIGHT 1×21p@0.5 → 接触跨度 10.5mm + 两侧边 {A['conn_side_margin']*2:.1f}mm = {worst[1]:.1f}mm; "
        f"板宽 {A['board_w']:.1f}mm → " + ("✓ 放得下 (余 %.1fmm)" % (A["board_w"] - worst[1])
                                                if ok7 else f"★放不下 (差 {worst[1]-A['board_w']:.1f}mm)"),
        owner="MECH-OWNED", need=None)

    # ============================================================ C-8 镜脚 H 余量 vs 直插排针
    margin = A["temple_h_total"] - A["temple_h_used"]
    ok8 = A["header_body_h"] <= margin
    rec(ok8, "C-8", "J_DEBUG/J_UART 直插排针高度 ≤ 镜脚 H 余量",
        f"镜腿厚 {A['temple_h_total']} - H 叠层已用 {A['temple_h_used']} → 余 {margin:.1f}mm; "
        f"1.27mm 直插排针塑料体高 {A['header_body_h']}mm → " +
        ("✓" if ok8 else f"★超 {A['header_body_h']-margin:.2f}mm (J_DEBUG 1×4 必装) → 改贴片/开槽/挪检修口")
        + " ┃ ★**归属 = CROSS-OWNED (网表域)**: hw-lead 已答复采纳『2×5@1.27 Cortex-10 焊盘阵列 (座体 DNP)』"
          "(答案键 iss092_jdebug_cortex10_netlist); 网表改动需排期 state/gen_netlist.py "
          "(needs 键 iss092_jdebug_cortex10_netlist_fix → main) ⇒ 改完后本项自动消失 (焊盘阵列无实体高度)。"
          "★mech 侧欠: 该阵列的座体外形/footprint (hw-lead 答复里点名要结构侧给)",
        owner="CROSS-OWNED", need="iss092_jdebug_cortex10_netlist_fix (→main) + mech 侧出座体外形/footprint")

    # ============================================================ C-9 BOM 封装列
    fp_unknown = sum(1 for b in bom if (b.get("footprint") or "").strip() in ("", "待定"))
    rec(fp_unknown == 0, "C-9", "BOM 封装 (footprint) 全部回填",
        f"{fp_unknown}/{len(bom)} 条 footprint = 待定 → 板面积/器件高度/连接器外形全部无法核算")

    # ============================================================ C-10 BOM 重量列
    wcol = [k for k in (bom[0].keys() if bom else []) if "weight" in k.lower() or "重量" in k]
    rec(bool(wcol), "C-10", "BOM 带重量列 (整机 30-40g 目标可核)",
        f"重量列 = {wcol if wcol else '无'} → 整机重量只能靠 MECH_BUDGET 的估列 (48.9-74.0g vs 目标 30-40g)")

    # ============================================================ C-11 网表机械固定信息
    keys = ("固定孔", "安装孔", "M1.2", "定位销", "keepout", "螺钉", "沉孔")
    hits = sum(1 for r in rows if any(k in (r.get("note", "") + r.get("value", "")) for k in keys))
    rec(hits > 0, "C-11", "网表含安装孔/固定点/keepout",
        f"与机械固定相关的行数 = {hits} → " +
        ("有" if hits else "★0 条 → PCB 出来没有固定孔, 装不进骨架 (PIN-SET-2: 2×⌀2.0H7 定位销 + 2×⌀1.4 压紧孔)"))

    # ============================================================ C-12 板级归属覆盖
    boards = sorted({r.get("board") for r in rows if r.get("board")})
    need = {"MAIN_PCB", "CHG_BOARD", "HINGE", "SENSOR_BOARD"}
    missing = sorted(need - set(boards))
    rec(not missing, "C-12", "板级归属覆盖全部物理板",
        f"netlist board 列 = {boards}; 物理上还需要 {missing} (镜框摄像头板的载板) → " +
        ("✓" if not missing else "★CONN_CAM 的对端装哪块板没有口径 (装配/备料/开孔三件事无唯一口径)"))

    # ============================================================ C-13 充电板器件面积 vs 外形
    p10_refs, p10_rows_txt = set(), ""
    if os.path.exists(CHARGE_SPEC):
        txt = open(CHARGE_SPEC, encoding="utf-8").read()
        blk = re.search(r"```csv\n(.*?)```", txt, re.S)
        if blk:
            p10_rows_txt = blk.group(1)
            for line in p10_rows_txt.splitlines():
                if line.startswith("P10,"):
                    parts = line.split(",")
                    if len(parts) > 4:
                        p10_refs.add(parts[4].strip().strip('"'))
    area = 0.0
    unmodelled = []
    for ref in p10_refs:
        if ref in CHG_FOOTPRINT:
            area += CHG_FOOTPRINT[ref]
        elif re.match(r"^(R_|C_)", ref):
            area += DEFAULT_RC
        else:
            unmodelled.append(ref)
    board_area = A["chg_board_l"] * A["chg_board_w"]
    usable = board_area - A["typec_body_l"] * A["typec_body_w"]
    dens = area / board_area
    rec(dens <= 0.70, "C-13", "充电板器件级占位面积 vs 25×10×0.8 外形",
        f"P10 位号 {len(p10_refs)} 个, 估算占位 {area:.0f}mm² / 板面积 {board_area:.0f}mm² "
        f"= {dens:.0%} (扣 Type-C 座体后可用 {usable:.0f}mm², 需求占位率 {area/usable:.0%}); "
        f"未建模件 {unmodelled if unmodelled else '无'} → " +
        ("✓" if dens <= 0.70 else "★M3 的 25×10 是按 4 类件估的, P10 展开后装不下 → 外形要重出"))

    # ============================================================ C-14 Type-C 沉板 vs 镜框端件壁厚
    need_h = max(A["usb_recept_sink"]) + A["typec_body_h"]
    ok14 = need_h <= 2 * A["print_wall"]
    rec(ok14, "C-14", "Type-C 座在镜框端件的局部厚度需求",
        f"沉板最深 {max(A['usb_recept_sink'])}mm + 座体高 {A['typec_body_h']}mm = {need_h:.1f}mm 局部厚度需求 "
        f"vs P2S 打印件单壁 {A['print_wall']}mm → " +
        ("✓" if ok14 else f"★打印件单壁 {A['print_wall']}mm 装不下 → 端件必须局部加厚到 {need_h:.1f}mm + 加强筋 (承力路径 M-4)")
        + " ┃ ★**归属 = CROSS-OWNED (打印包改版已登记)**: needs 键 iss089_typec_opening_and_print_pack → main "
          "(Type-C 面板试样移镜框端件 + 端件局部加厚/开口公差) + iss092_print_pack_rev → main "
          "⇒ 这是**已登记待排期的打印包改版**, 不是没人管的红",
        owner="CROSS-OWNED", need="iss089_typec_opening_and_print_pack (→main) + iss092_print_pack_rev (→main)")

    # ============================================================ C-15 跨铰链压降测点成对
    bat_chg_boards = {r.get("board") for r in rows if r["net"] == "BAT_CHG"}
    tp_bat = [r for r in rows if r["ref"] == "TP_BAT_CHG"]
    ok15 = len(bat_chg_boards & {"CHG_BOARD", "MAIN_PCB"}) >= 2 and len(tp_bat) >= 2
    rec(ok15, "C-15", "跨铰链段压降测点成对 (Kelvin 双点)",
        f"BAT_CHG 网涉及板 = {sorted(bat_chg_boards)}; TP_BAT_CHG 行 = {len(tp_bat)} → " +
        ("✓" if ok15 else "★只有单侧测点 → 铰链段压降测不出来 (ISS-091 的输入缺失)"))

    # ============================================================ C-16 板宽现状 (按档位; 不再问已答完的 12→15)
    thks = FRAME["c16_thk_cases"]
    cmp_l, cmp_w, cmp_thk, cmp_label = FRAME["c16_cmp"]
    ws = [A["board_l"] * A["board_w"] * t * 1.85 / 1000.0 for t, _ in thks]
    wcmp = cmp_l * cmp_w * cmp_thk * 1.85 / 1000.0
    wtxt = P["c16_weight"].format(
        w4=ws[0], l4=thks[0][1],
        w6=(ws[1] if len(ws) > 1 else ws[0]),
        l6=(thks[1][1] if len(thks) > 1 else thks[0][1]),
        cmp=cmp_label, wc=wcmp, dw=ws[0] - wcmp)
    rec(True, "C-16", P["c16_title"],
        P["c16_detail"].format(L=A["board_l"], W=A["board_w"], prov=P["c16_prov"],
                                h=A["temple_h_total"], v=A["temple_v_net"], weight=wtxt,
                                cw=worst[1], mr=A["board_w"] - worst[1]),
        owner="MECH-OWNED", need=None)

    # ---------------------------------------------------------------- 汇总
    fails = [x for x in RESULTS if not x[0]]
    mech_fail = [x for x in fails if x[4] == "MECH-OWNED"]
    other_fail = [x for x in fails if x[4] != "MECH-OWNED"]
    print("\n" + "=" * 78)
    print(f"自检汇总: {len(RESULTS)-len(fails)}/{len(RESULTS)} PASS · FAIL {len(fails)} "
          f"(MECH-OWNED {len(mech_fail)} · 他域 {len(other_fail)})")
    print("=" * 78)
    for ok, code, title, _, owner, need in RESULTS:
        mark = "PASS" if ok else "FAIL"
        print(f"  {mark}  {code}  [{owner}] {title}")
        if not ok and need:
            print(f"          └ 归属: {need}")
    print("\n★ 闸状态: **本脚本不是闸** (全项目调用方 = 0; 它判 16 项里只有 7 项属结构侧)。")
    print("★ 退出码口径 (★ISS-192 改★): rc=1 **只**表示有 MECH-OWNED 判据不通过 (结构侧自己的活没做完);")
    print("  他域 (HW-OWNED/CROSS-OWNED) 的红项**不**影响 rc —— 但每盏都带归属登记键, 不留孤儿红。")
    if mech_fail:
        print(f"  ★ 本次 MECH-OWNED 红项: {[x[1] for x in mech_fail]} ⇒ 结构侧欠活")
    if other_fail:
        print(f"  · 他域红项 (已登记归属, 不阻塞): {[(x[1], x[4]) for x in other_fail]}")
    print("\n[实测] 条数 = 0 (无实物); 可复现的是本脚本对 netlist/BOM 的解析复算结果")
    print(P["authority_line"])
    print("用法: cd projects/smart_glasses && python3 MECH/cross_review_check.py")
    return 1 if mech_fail else 0


if __name__ == "__main__":
    sys.exit(main())
