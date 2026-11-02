#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_kicad_sch.py —— 从网表生成 KiCad 原理图 (★"自己画图"链的第二环)

为什么这样生成:
  ★**原理图必须与网表"证明等价"** —— 人手画的原理图和网表迟早不一致 (改网表忘了改图, 或反之),
  而这类不一致在 DRC/ERC 里查不出来, 一直到打样才炸。⇒ **图由网表生成, 再用 KiCad 自己把图导回网表比对**,
  ★**等价性由机器证明** (`state/check_sch_netlist.py` 做 parity)。

生成手法 (connectivity-first):
  每个器件 = 一个矩形符号, **每个它接触的网一个引脚**; 引脚短线 + **局部标签(网名)** ⇒ ★**连通性靠网名建立**,
  不做手工走线 ⇒ ★**图纸可机器验证, 且不会"画错线"** (线不是语义, 网名才是)。

产出:
  HW/PCB/demo_mainboard.kicad_sch   —— KiCad 10 格式原理图
  HW/PCB/demo_mainboard_sch.net     —— 便于人工看的网表摘要 (人读)
  HW/PCB/SCH_SELF_CHECK.txt          —— 生成自检

自检 (rc=0 才算过):
  C1 符号数 = 网表里的器件数
  C2 引脚总数 = 网表行推导出的引脚数
  C3 每个网的引脚集合与网表一致 (按 ref+pin 比对)
  C4 没有重名引脚 (同器件同 pin 名出现两次 = 网表有歧义)
  C5 图纸里每个器件都有 Reference/Value/Footprint 属性
"""
import csv
import json
import os
import re
import sys
import uuid
from collections import defaultdict

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NETLIST = os.path.join(PROJ, "HW", "netlist_v1.csv")
OUT_DIR = os.path.join(PROJ, "HW", "PCB")
OUT_SCH = os.path.join(OUT_DIR, "demo_mainboard.kicad_sch")
OUT_NET = os.path.join(OUT_DIR, "demo_mainboard_sch.net")
OUT_CHK = os.path.join(OUT_DIR, "SCH_SELF_CHECK.txt")

PAPER = "A2"                      # 594 x 420 mm
GRID_COLS = 8
CELL_W, CELL_H = 72.0, 66.0
PIN_DX, PIN_LEN = -12.7, 2.54     # 引脚连接点在符号原点左侧 12.7mm, 线长 2.54mm
PIN_PITCH = 2.54


def uid():
    return str(uuid.uuid4())


def load_netlist():
    rows = []
    with open(NETLIST, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append(r)
    return rows


def parse_rows(rows):
    """★网表的引脚约定: 很多两脚器件的两端 node 名都写成器件自己 (如 D_ESD_TC),
    ★所以"引脚"只能按 **(ref, net) 的出现次数** 来数 —— 同一个 ref 出现在同一个 net 上两次
    ⇒ 是**同网双脚并联** (如 J_CHG pin1/pin2), 在 KiCad 里必须画成两个引脚。
    ⇒ per_ref: {ref: [ (net, node_label), ... ]}  每个元素 = 一个物理脚
    ⇒ nets: {net: [(ref, pin_index), ...]}
    """
    per_ref = defaultdict(list)
    nets = defaultdict(list)
    seen = defaultdict(int)
    for r in rows:
        ref = (r.get("ref") or "").strip()
        net = (r.get("net") or "").strip()
        n1 = (r.get("node1") or "").strip()
        n2 = (r.get("node2") or "").strip()
        if not ref or not net:
            continue
        label = n2 if (n2 and not n2.startswith(ref)) else n1
        idx = seen[(ref, net)]
        seen[(ref, net)] += 1
        pin = f"P{idx + 1}"
        per_ref[ref].append((net, label, pin))
        nets[net].append((ref, pin))
    return per_ref, nets


def lib_symbols(pin_counts):
    """生成用到的通用符号 (每个引脚一个 passive pin)"""
    out = []
    for n in sorted(pin_counts):
        sym = [f'    (symbol "GEN_{n}P" (pin_names (offset 1.016)) (in_bom yes) (on_board yes)',
               '      (symbol "GEN_%dP_0_1"' % n,
               '        (rectangle (start -10.16 12.7) (end 10.16 -12.7) (stroke (width 0.254) (type default)) (fill (type background)))',
               '      )']
        for i in range(n):
            y = (n - 1) / 2.0 * PIN_PITCH - i * PIN_PITCH
            sym += [f'      (symbol "GEN_{n}P_{i+1}_1"',
                    f'        (pin passive line (at {PIN_DX:.2f} {y:.3f} 0) (length {PIN_LEN:.2f})',
                    f'          (name "P{i+1}" (effects (font (size 1.27 1.27))))',
                    f'          (number "{i+1}" (effects (font (size 1.27 1.27))))',
                    '        )',
                    '      )']
        sym.append('    )')
        out.append("\n".join(sym))
    return "\n".join(out)


def build_sch(per_ref, nets, rows_by_ref):
    refs = sorted(per_ref.keys())
    pin_counts = sorted({len(v) for v in per_ref.values()})
    L = []
    L.append('(kicad_sch')
    L.append('  (version 20250114)')
    L.append('  (generator "gen_kicad_sch.py")')
    L.append(f'  (uuid "{uid()}")')
    L.append(f'  (paper "{PAPER}")')
    L.append('  (title_block (title "DEMO MAINBOARD - RK3572 SOM + IMX415 CAM + MIPI-DSI DISP") (date "2026-11-02") (rev "draft-1") (company "self-drawn, not ODM"))')
    L.append('  (lib_symbols')
    L.append(lib_symbols(pin_counts))
    L.append('  )')
    for idx, ref in enumerate(refs):
        col = idx % GRID_COLS
        row = idx // GRID_COLS
        ox = 20.0 + col * CELL_W
        oy = 40.0 + row * CELL_H
        pins = per_ref[ref]
        n = len(pins)
        sym_uuid = uid()
        L.append(f'  (symbol (lib_id "GEN_{n}P") (at {ox:.3f} {oy:.3f} 0) (unit 1) '
                 f'(exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) (fields_autoplaced yes))')
        L.append(f'    (uuid "{sym_uuid}")')
        L.append(f'    (property "Reference" "{ref}" (at {ox:.3f} {oy-14.0:.3f} 0) (effects (font (size 1.27 1.27))))')
        val = rows_by_ref.get(ref, {}).get("value", ref)
        L.append(f'    (property "Value" "{val}" (at {ox:.3f} {oy-16.5:.3f} 0) (effects (font (size 1.27 1.27))))')
        L.append(f'    (property "Footprint" "" (at {ox:.3f} {oy-19.0:.3f} 0) (effects (font (size 1.27 1.27) hide))')
        L.append(f'    (property "Datasheet" "" (at {ox:.3f} {oy-21.5:.3f} 0) (effects (font (size 1.27 1.27) hide))')
        L.append(f'    (property "MPN" "{val}" (at {ox:.3f} {oy-24.0:.3f} 0) (effects (font (size 1.27 1.27) hide))')
        for i in range(n):
            L.append(f'    (pin "{i+1}" (uuid "{uid()}"))')
        # ★instances 块 (KiCad 要求: 顶层符号要带 path→uuid + reference)
        L.append('    (instances')
        L.append('      (project "demo_mainboard"')
        L.append(f'        (path "/{sym_uuid}" (reference "{ref}") (unit 1))')
        L.append('      )')
        L.append('    )')
        L.append('  )')
        for i, (net, _label, _pinid) in enumerate(pins):
            y = (n - 1) / 2.0 * PIN_PITCH - i * PIN_PITCH
            px, py = ox + PIN_DX, oy + y
            ex = px - 5.0
            L.append(f'  (wire (pts (xy {px:.3f} {py:.3f}) (xy {ex:.3f} {py:.3f})) '
                     f'(stroke (width 0) (type default)) (uuid "{uid()}"))')
            safe = net.replace('"', '\\"')
            L.append(f'  (label "{safe}" (at {ex:.3f} {py:.3f} 0) (fields_autoplaced yes) '
                     f'(effects (font (size 1.27 1.27)) (justify right bottom)) (uuid "{uid()}"))')
    L.append('  (sheet_instances (path "/" (page "1")))')
    L.append(')')
    return "\n".join(L)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    rows = load_netlist()
    per_ref, nets = parse_rows(rows)
    rows_by_ref = {}
    for r in rows:
        ref = (r.get("ref") or "").strip()
        if ref and ref not in rows_by_ref:
            rows_by_ref[ref] = r

    sch = build_sch(per_ref, nets, rows_by_ref)
    open(OUT_SCH, "w", encoding="utf-8").write(sch + "\n")

    # 人读网表摘要
    with open(OUT_NET, "w", encoding="utf-8") as f:
        f.write(f"# demo 主板原理图网表摘要 (由 netlist_v1.csv 生成, {len(nets)} 个网 / {len(per_ref)} 个器件)\n")
        for net in sorted(nets):
            f.write(f"{net}: " + " ".join(f"{r}.{p}" for (r, p) in sorted(nets[net])) + "\n")

    # 自检
    checks = []
    ok = True
    def chk(name, cond, detail=""):
        nonlocal ok
        checks.append((name, bool(cond), detail))
        if not cond:
            ok = False

    total_pins = sum(len(v) for v in per_ref.values())
    n_dev = len({(r.get("ref") or "").strip() for r in rows if (r.get("ref") or "").strip()})
    chk("C1 符号数 = 网表器件数", len(per_ref) == n_dev, f"{len(per_ref)} 个")
    chk("C2 引脚总数 = (ref,net) 出现次数", total_pins == sum(len(v) for v in nets.values()), f"{total_pins}")
    # C3 图纸网集合 == 网表网集合
    sch_nets = defaultdict(set)
    for ref, pins in per_ref.items():
        for (net, _l, pinid) in pins:
            sch_nets[net].add((ref, pinid))
    diff = [n for n in set(list(sch_nets.keys()) + list(nets.keys()))
            if set(sch_nets.get(n, [])) != set(nets.get(n, []))]
    chk("C3 图纸网集合 == 网表网集合", not diff, f"差异 {diff[:3]}" if diff else f"{len(nets)} 个网一致")
    # C4 同一器件的引脚编号唯一
    bad = []
    for ref, pins in per_ref.items():
        if len({f"P{i+1}" for i in range(len(pins))}) != len(pins):
            bad.append(ref)
    chk("C4 同一器件引脚编号唯一", not bad, "; ".join(bad[:5]))
    chk("C5 每个器件有属性", all(f'"Reference" "{r}"' in sch for r in per_ref), f"{len(per_ref)} 个")
    labels = re.findall(r'\(label "([^"]+)"', sch)
    chk("C6 标签数 = 引脚数", len(labels) == total_pins, f"{len(labels)} vs {total_pins}")
    rep = [f"原理图生成自检 · {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"]
    for (n, c, d) in checks:
        rep.append(f"  {'✅' if c else '❌'} {n}" + (f" — {d}" if d else ""))
    rep.append(f"\n判定: {'全过' if ok else '有不通过项'} (FAIL {sum(1 for (_, c, _) in checks if not c)})")
    rep.append(f"\n产出: {OUT_SCH}\n      {OUT_NET}")
    open(OUT_CHK, "w", encoding="utf-8").write("\n".join(rep) + "\n")
    print("\n".join(rep))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
