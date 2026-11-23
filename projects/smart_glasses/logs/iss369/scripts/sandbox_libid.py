#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-369 · 沙盒可达性证明: 「90 件换官方 land + 同时写 lib_id」⇒ C1/C2/C3/C4 读数

★必须用 KiCad python 跑: bash state/pcbnew_py.sh tmp/iss369/tools/sandbox_libid.py
★零写板: 所有副本落 tmp/iss369/sbx/ · 真板零改动
★零落表: 网表/脚表/BOM 只读
★C1~C4 读数由 state/check_pcb_nets.py 的**真代码**给出 (importlib 载入, 只把 NET 常量指向副本)

五轮:
  S0 基线            : 真板 + 真网表                              ⇒ 期望 C4=158
  S1 换land不写库名  : 板副本(90 件换官方 land) + 真网表         ⇒ 期望 C4=158 (腿A 对 C4 贡献 0)
  S2 换land+写库名   : S1 + 90 件写 lib_id + 4 件 J_SOM 写库名   ⇒ 期望 C4=158 ★本题核心★
  S3 只写库名        : 真板 + 94 件写 lib_id (零几何改动)         ⇒ 期望 C4=158 ★纯库名零影响★
  S4 反向对照        : 真板 + 90 件写 lib_id 但**不换 land**       ⇒ 期望 C4=158 (库名不参与网表推导)
"""
import csv
import hashlib
import importlib.util
import json
import os
import re
import shutil
import sys
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SBX = os.path.join(ROOT, "tmp", "iss369", "sbx")
os.makedirs(SBX, exist_ok=True)
LIBROOT = "/home/yuewuya/kicad/AppDir/share/kicad/footprints"
BOARD = os.path.join(ROOT, "HW", "PCB", "demo_mainboard.kicad_pcb")
NET = os.path.join(ROOT, "HW", "netlist_v1.csv")
PINS = os.path.join(ROOT, "HW", "netlist_v1_pins.csv")

_spec = importlib.util.spec_from_file_location(
    "cpn", os.path.join(ROOT, "state", "check_pcb_nets.py"))
cpn = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cpn)


def load_targets():
    d = json.load(open(os.path.join(ROOT, "tmp", "iss369", "targets186.json"), encoding="utf-8"))
    return {r["ref"]: r for r in d}


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


# ---------------------------------------------------------------- 文本级工具

def _blocks_with_span(text, name):
    out = []
    i = 0
    while True:
        m = re.search(r"\(%s\b" % re.escape(name), text[i:])
        if not m:
            break
        s = i + m.start()
        depth = 0
        j = s
        while j < len(text):
            if text[j] == "(":
                depth += 1
            elif text[j] == ")":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        out.append((s, j + 1, text[s:j + 1]))
        i = j + 1
    return out


def _new_uuid():
    return str(uuid.uuid4())


def _mod_pads(lib, nm):
    p = os.path.join(LIBROOT, "%s.pretty" % lib, "%s.kicad_mod" % nm)
    if not os.path.isfile(p):
        return None
    t = open(p, encoding="utf-8").read()
    return [b for (_s, _e, b) in _blocks_with_span(t, "pad")]


def _mod_fab_graphics(lib, nm):
    p = os.path.join(LIBROOT, "%s.pretty" % lib, "%s.kicad_mod" % nm)
    if not os.path.isfile(p):
        return None
    t = open(p, encoding="utf-8").read()
    out = []
    for tag in ("fp_line", "fp_rect"):
        for (_s, _e, b) in _blocks_with_span(t, tag):
            if re.search(r'\(layer "F\.Fab"\)', b):
                out.append(b)
    return out


def _reuuid(block):
    return re.sub(r'\(uuid "[^"]*"\)', '(uuid "%s")' % _new_uuid(), block)


def _set_net(block, netname):
    if re.search(r'\n\t*\(net "[^"]*"\)', block):
        return re.sub(r'\(net "[^"]*"\)', '(net "%s")' % netname, block)
    m = re.search(r'\n(\t*)\(layers [^)]*\)', block)
    if not m:
        return block
    ind = m.group(1)
    return block[:m.end()] + '\n%s(net "%s")' % (ind, netname) + block[m.end():]


def _pad_num(block):
    m = re.search(r'pad\s+"([^"]*)"', block)
    return m.group(1) if m else ""


def fp_blocks(text):
    out = []
    for m in re.finditer(r'\n\t\(footprint ', text):
        s = m.start() + 1
        cands = [text.find("\n\t(footprint ", s + 1), text.find("\n\t(net ", s + 1)]
        cands = [c for c in cands if c != -1]
        e = min(cands) if cands else len(text)
        out.append((s, e, text[s:e]))
    return out


def build_legA_board(targets, out_path):
    """文本级: 90 件的 footprint 换成官方 land 的 pad 集 + F.Fab 外框 (不写库名)"""
    text = open(BOARD, encoding="utf-8").read()
    net_of_pin = {}
    with open(PINS, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            ref = (r.get("ref") or "").strip()
            pin = (r.get("pin") or "").strip()
            net = (r.get("net") or "").strip()
            if ref and pin:
                net_of_pin[(ref, pin)] = net
    n_sw = 0
    n_pad = 0
    for (s, e, blk) in reversed(fp_blocks(text)):
        rm = re.search(r'\(property "Reference" "([^"]*)"', blk)
        if not rm:
            continue
        ref = rm.group(1)
        p = targets.get(ref)
        if not p or p["action"] != "写" or p["reason_code"] != "R90":
            continue
        libname = p["target_libname"]
        lib, nm = libname.split(":", 1)
        newpads = _mod_pads(lib, nm)
        newfab = _mod_fab_graphics(lib, nm)
        if newpads is None or newfab is None:
            continue
        built = []
        for pb in newpads:
            num = _pad_num(pb)
            digits = "".join(ch for ch in num if ch.isdigit()) or "1"
            netname = net_of_pin.get((ref, digits)) or net_of_pin.get((ref, "1"))
            b = _reuuid(pb)
            if netname:
                b = _set_net(b, netname)
            built.append(b)
            n_pad += 1
        inner = blk
        for (ps, pe, _pb) in reversed(_blocks_with_span(inner, "pad")):
            inner = inner[:ps] + inner[pe:]
        for tag in ("fp_line", "fp_rect"):
            for (gs, ge, gb) in reversed(_blocks_with_span(inner, tag)):
                if re.search(r'\(layer "F\.Fab"\)', gb):
                    inner = inner[:gs] + inner[ge:]
        anchor = inner.rfind("\n\t\t(embedded_fonts")
        if anchor == -1:
            anchor = inner.rfind("\n\t)")
        ins = ""
        for gb in newfab:
            ins += "\n\t\t" + _reuuid(gb)
        for pb in built:
            ins += "\n\t\t" + pb.replace("\n", "\n\t\t")
        inner = inner[:anchor] + ins + inner[anchor:]
        text = text[:s] + inner + text[e:]
        n_sw += 1
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return n_sw, n_pad


def write_libids(src_path, out_path, targets, only=None):
    """文本级: 把 (footprint "" 改成 (footprint "Lib:Name" (★只改节点名一行★)"""
    text = open(src_path, encoding="utf-8").read()
    n = 0
    for (s, e, blk) in reversed(fp_blocks(text)):
        rm = re.search(r'\(property "Reference" "([^"]*)"', blk)
        if not rm:
            continue
        ref = rm.group(1)
        p = targets.get(ref)
        if not p or p["action"] != "写":
            continue
        if only is not None and p["reason_code"] not in only:
            continue
        libname = p["target_libname"]
        new_blk = blk.replace('\t(footprint ""', '\t(footprint "%s"' % libname, 1)
        if new_blk == blk:
            continue
        text = text[:s] + new_blk + text[e:]
        n += 1
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return n


def read_c4(board_path, net_path=NET):
    cpn.NET = net_path
    rc, body, ctx = cpn.run_checks(board_path)
    c4n = None
    c1 = c2 = c3 = ""
    c2bad = []
    c3bad = []
    for ln in body:
        if "C4" in ln and "占位" in ln:
            m = re.search(r"器件 (\d+) 个", ln)
            c4n = int(m.group(1)) if m else -1
        s = ln.strip()
        if s.startswith(("✅ C1", "❌ C1")):
            c1 = s
        if s.startswith(("✅ C2", "❌ C2")):
            c2 = s
        if s.startswith(("✅ C3", "❌ C3")):
            c3 = s
        if "C2 针号/针数不符" in ln:
            c2bad.append(ln.strip())
        if "C3 焊盘数不符" in ln:
            c3bad.append(ln.strip())
    return {"rc": rc, "c4": c4n, "c1": c1, "c2": c2, "c3": c3,
            "fails": ctx.get("fails", []), "c2bad": c2bad, "c3bad": c3bad,
            "body": body}


def libid_count(board_path):
    """★用真 KiCad python 读板, 数 GetFPIDAsString() 非空的封装数★"""
    import pcbnew
    b = pcbnew.LoadBoard(board_path)
    fps = list(b.GetFootprints())
    named = [f for f in fps if f.GetFPIDAsString()]
    return {"total": len(fps), "named": len(named),
            "named_refs": sorted(f.GetReference() for f in named)}


def main():
    targets = load_targets()
    out = {}
    pre_board_md5 = md5(BOARD)

    # ---- S1: 换 land (不写库名)
    b1 = os.path.join(SBX, "board_legA_only.kicad_pcb")
    n_sw, n_pad = build_legA_board(targets, b1)
    print("[sbx] S1 换land (不写库名): 换 %d 件 / 落 %d 焊盘 => %s" % (n_sw, n_pad, b1))

    # ---- S2: 换 land + 写库名 (90 + 4 J_SOM)
    b2 = os.path.join(SBX, "board_legA_plus_libid.kicad_pcb")
    n_lib2 = write_libids(b1, b2, targets)
    print("[sbx] S2 换land+写库名: 写 %d 件库名 => %s" % (n_lib2, b2))

    # ---- S3: 只写库名 (零几何改动)
    b3 = os.path.join(SBX, "board_libid_only.kicad_pcb")
    n_lib3 = write_libids(BOARD, b3, targets)
    print("[sbx] S3 只写库名 (零几何改动): 写 %d 件 => %s" % (n_lib3, b3))

    # ---- S4: 反向对照 (90 件写库名但不换 land)
    b4 = os.path.join(SBX, "board_libid_no_landswap.kicad_pcb")
    n_lib4 = write_libids(BOARD, b4, targets, only={"R90"})
    print("[sbx] S4 反向对照 (90件写库名·不换land): 写 %d 件 => %s" % (n_lib4, b4))

    runs = [
        ("S0_基线_真板真表", BOARD),
        ("S1_换land不写库名", b1),
        ("S2_换land加写库名", b2),
        ("S3_只写库名零几何改动", b3),
        ("S4_反向对照_90件写库名不换land", b4),
    ]
    allbody = []
    for name, bp in runs:
        r = read_c4(bp)
        lc = libid_count(bp)
        out[name] = {k: v for k, v in r.items() if k != "body"}
        out[name]["libid_named"] = lc["named"]
        out[name]["libid_total"] = lc["total"]
        out[name]["board_md5"] = md5(bp)
        allbody.append("=" * 78)
        allbody.append("【%s】 板=%s  rc=%d  C4=%s  库名非空=%d/%d"
                       % (name, os.path.basename(bp), r["rc"], r["c4"],
                          lc["named"], lc["total"]))
        allbody.extend(r["body"])
        print("[sbx] %-28s rc=%d C4=%s 库名=%d/%d | %s"
              % (name, r["rc"], r["c4"], lc["named"], lc["total"], r["c1"][:60]))
        for f in r["fails"]:
            print("        · %s" % f)

    out["_meta"] = {
        "real_board_md5_pre": pre_board_md5,
        "real_board_md5_post": md5(BOARD),
        "real_board_untouched": pre_board_md5 == md5(BOARD),
        "s1_swapped": n_sw, "s1_pads": n_pad,
        "s2_libids": n_lib2, "s3_libids": n_lib3, "s4_libids": n_lib4,
        "sandbox_dir": SBX,
    }
    json.dump(out, open(os.path.join(ROOT, "logs", "iss369", "10_sandbox_readings.json"),
                        "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    with open(os.path.join(ROOT, "logs", "iss369", "11_sandbox_bodies.txt"), "w",
              encoding="utf-8") as fh:
        fh.write("\n".join(allbody) + "\n")
    print("[sbx] 真板 md5 pre/post 一致:", out["_meta"]["real_board_untouched"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
