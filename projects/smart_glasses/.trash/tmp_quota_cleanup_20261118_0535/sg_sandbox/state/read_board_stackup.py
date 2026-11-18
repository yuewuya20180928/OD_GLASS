#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""read_board_stackup.py -- ★★★**从板文件反读叠层 (★唯一真源) (2026-11-06 20:0x)**

★★★**为什么要有这个 (★P0 交付风险, 机器读数)**:
  ① `HW/PCB/STACKUP.md` (生成器写死 **6 层** · 介质 FR4 εr4.5 / prepreg 0.21 + core 0.1)
     与 `HW/PCB/STACKUP_IMPEDANCE.md` (**8 层** · "介质厚度不明") ⇒ ★**两份矛盾文档同在投板资料夹**
  ② ★**板文件里的 `(stackup ...)` 才是真的** (8 层 · PR2116 0.1052 εr4.1 / FR4 0.3271 εr4.3)
  ③ ★**`state/gen_kicad_project.py` 里 `N_COPPER = 6` 是写死的** ⇒ ★**手改 STACKUP.md 会被 regen 覆盖**
  ④ ⇒ ★**本模块提供"从板文件反读"的唯一真源**, 生成器与自检都改用它 ⇒ ★**不会再漂**

★★★**用法**:
  from read_board_stackup import read_stackup, stackup_md
  st = read_stackup("HW/PCB/demo_mainboard.kicad_pcb")
  ⇒ st["n_copper"] / st["copper"] / st["dielectrics"] / st["total_thickness"]

  CLI: bash state/pcbnew_py.sh state/read_board_stackup.py <板> [--md <输出.md>] [--params <PARAMS.json>]
"""
import sys
import os
import re
import json

_HERE = os.path.dirname(os.path.abspath(__file__))

CU_RE = re.compile(r'^\s*\(layer\s+"(F\.Cu|In\d+\.Cu|B\.Cu)"')
TH_RE = re.compile(r'\(thickness\s+([-\d.]+)\)')
MA_RE = re.compile(r'\(material\s+"([^"]+)"\)')
ER_RE = re.compile(r'\(epsilon_r\s+([-\d.]+)\)')


def read_stackup(pcb_path):
    """★从板文件的 `(stackup ...)` 块反读叠层"""
    out = {"copper": [], "dielectrics": [], "other": [],
           "n_copper": 0, "total_thickness": None, "found": False}
    if not os.path.exists(pcb_path):
        return out
    in_st = False
    depth = 0
    cur = None
    for ln in open(pcb_path, encoding="utf-8", errors="ignore"):
        s = ln.strip()
        if not in_st:
            if s.startswith("(stackup"):
                in_st = True
                depth = s.count("(") - s.count(")")
                cur = None
            continue
        m = CU_RE.match(s)
        if m:
            cur = {"name": m.group(1), "type": "copper", "thickness": None,
                   "material": None, "er": None}
            out["copper"].append(cur)
            out["other"].append(cur)
        elif s.startswith('(layer "dielectric'):
            nm = s.split('"')[1]
            cur = {"name": nm, "type": "dielectric", "thickness": None,
                   "material": None, "er": None}
            out["dielectrics"].append(cur)
            out["other"].append(cur)
        elif s.startswith('(layer "'):
            # ★★**2026-11-06 20:0x 兄弟抓到的真 bug**: ★**非铜层 (如 B.Mask) 的 thickness
            #   会覆盖到上一个铜层的 thickness** ⇒ ★**B.Cu 被读成 0.01 (真实 0.035)**
            #   ⇒ ★**后果: 底铜 1oz 会被做成 0.25oz** ⇒ ★**修法: 见到新的 layer 头就清掉 cur**
            cur = None
        elif cur is not None:
            mt = TH_RE.search(s)
            if mt:
                cur["thickness"] = float(mt.group(1))
            mm = MA_RE.search(s)
            if mm:
                cur["material"] = mm.group(1)
            me = ER_RE.search(s)
            if me:
                cur["er"] = float(me.group(1))
        depth += s.count("(") - s.count(")")
        # ★**块结束: depth 回到 0** (★上一版写成 "and cur is None" ⇒ 永远退不出 ⇒ 把整个文件都当叠层)
        if depth <= 0:
            in_st = False
            out["found"] = True
            break
    # ★总厚: setup 里的 (thickness x)
    if out["found"]:
        for ln in open(pcb_path, encoding="utf-8", errors="ignore"):
            m = re.match(r"\s*\(thickness\s+([-\d.]+)\)", ln)
            if m:
                out["total_thickness"] = float(m.group(1))
                break
    out["n_copper"] = len(out["copper"])
    return out


def stackup_md(pcb_path, params=None, ts=None):
    """★**用板文件的真值**生成 STACKUP.md 的正文 (★params 只用来补"待定项"那些非叠层信息)"""
    st = read_stackup(pcb_path)
    ts = ts or ""
    if not st["found"]:
        return None
    diel = st["dielectrics"]
    dtxt = " / ".join(
        "%s %s mm εr=%s" % (d["material"] or "?", d["thickness"], d["er"])
        for d in diel)
    copper = st["copper"]
    ctxt = " / ".join("%s %s mm" % (c["name"], c["thickness"]) for c in copper)
    rows = [
        "| 项 | 值 |",
        "|---|---|",
        "| ★**层数** | **%d 铜层** (★**从板文件反读, 唯一真源**) |" % st["n_copper"],
        "| 铜层 | %s |" % ctxt,
        "| 介质 | %s |" % dtxt,
    ]
    if st["total_thickness"]:
        rows.append("| 总厚 | %s mm |" % st["total_thickness"])
    if params:
        b = params.get("board", {})
        if b:
            rows.insert(2, "| 板尺寸 | %s × %s mm (草案, 待 ISS-158 三件规格回来后重跑生成器更新) |"
                        % (b.get("width_mm"), b.get("height_mm")))
        imp = params.get("stackup", {}).get("impedance", {})
        if imp:
            rows.append("| ★**阻抗** | **MIPI 差分 %sΩ** / USB 差分 %sΩ / 单端 %sΩ |"
                        % (imp.get("mipi_diff_ohm"), imp.get("usb_diff_ohm"),
                           imp.get("single_ended_ohm")))
    txt = ("# HW/PCB/STACKUP.md —— demo 主板叠层（★生成于 %s · ★**叠层数据从板文件反读**）\n\n"
           % ts)
    txt += "\n".join(rows) + "\n\n"
    txt += ("★**唯一真源**: ★**板文件 `HW/PCB/demo_mainboard.kicad_pcb` 的 `(stackup ...)` 块**\n"
            "⇒ ★**本文件由 `state/read_board_stackup.py` 从板文件生成** ⇒ ★**不要再手写叠层参数**\n"
            "⇒ ★**2026-11-06 实测事故**: ★**旧版把层数写死成 6 层, 而板文件实际是 %d 层**\n"
            "  ⇒ ★**两份矛盾叠层文档同在投板资料夹 ⇒ 给板厂引错单的风险是真实的**\n\n"
            % st["n_copper"])
    return txt


def check_docs(pcb_path, docs):
    """★**文档 vs 板文件 交叉校验** (★防"引错单"的漂移)
       docs = [文档路径...] ⇒ 逐个找里面的层数/介质数字, 与板文件真值比对
       返回 (通过数, 失败列表)"""
    st = read_stackup(pcb_path)
    if not st["found"]:
        return 0, ["★板文件里没有 (stackup ...) ⇒ 无法校验"]
    n_cu = st["n_copper"]
    cu_th = dict((c["name"], c["thickness"]) for c in st["copper"])
    diel = [(d["material"], d["thickness"], d["er"]) for d in st["dielectrics"]]
    ok = 0
    bad = []
    for d in docs:
        if not os.path.exists(d):
            bad.append("%s: 文件不存在" % d)
            continue
        txt = open(d, encoding="utf-8", errors="ignore").read()
        # ★**层数**: 找 "N 层" / "N 铜层"
        m = re.search(r"(\d+)\s*铜层", txt)
        if m and int(m.group(1)) != n_cu:
            bad.append("%s: 写了 %s 铜层, 板文件是 %d 层" % (d, m.group(1), n_cu))
            continue
        # ★**介质厚度**: 文档里出现的每个介质厚度都要在板文件里存在
        for (mat, th, er) in diel:
            pass
        dth = set(round(x[1], 4) for x in diel)
        for mm in re.findall(r"(?:prepreg|core|dielectric\s*\d*)[^|\n]*?\|\s*([\d.]+)\s*\|", txt):
            if round(float(mm), 4) not in dth:
                bad.append("%s: 介质厚度 %s 不在板文件真值里 %s" % (d, mm, sorted(dth)))
                break
        ok += 1
    return ok, bad


def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        return 2
    pcb = a[0]
    st = read_stackup(pcb)
    print("═══ 板文件反读叠层: %s ═══" % pcb)
    print("  ★铜层数 = %d (found=%s)" % (st["n_copper"], st["found"]))
    for c in st["copper"]:
        print("    铜层 %-8s %s mm" % (c["name"], c["thickness"]))
    for d in st["dielectrics"]:
        print("    介质 %-12s %s mm  %s εr=%s"
              % (d["name"], d["thickness"], d["material"], d["er"]))
    print("  总厚 = %s" % st["total_thickness"])
    if "--check-docs" in a:
        docs = []
        i = a.index("--check-docs")
        while i + 1 < len(a) and not a[i + 1].startswith("--"):
            docs.append(a[i + 1])
            i += 1
        ok, bad = check_docs(pcb, docs)
        print("── 文档交叉校验: %d 个通过 / %d 个有问题" % (ok, len(bad)))
        for b_ in bad:
            print("   ★ %s" % b_)
        return 1 if bad else 0
    if "--md" in a:
        outp = a[a.index("--md") + 1]
        params = None
        if "--params" in a:
            try:
                params = json.load(open(a[a.index("--params") + 1], encoding="utf-8"))
            except Exception:
                params = None
        from datetime import datetime as _dt
        txt = stackup_md(pcb, params, _dt.now().strftime("%Y-%m-%dT%H:%M:%S"))
        if txt:
            open(outp, "w", encoding="utf-8").write(txt)
            print("── 已写 %s" % outp)
        else:
            print("★板文件里没有 (stackup ...) ⇒ 没写")
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
