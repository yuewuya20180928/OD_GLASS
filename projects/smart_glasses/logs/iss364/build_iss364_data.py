#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-364 · HW 侧 90 件换封装作业包 + C4 目标 68 可达性 · 真源实算脚本

★ 零写板 · 零落表 · 零改既有页 · 零改既有闸 · 只读真源 + 只写 logs/iss364/ 与 tmp/iss364_sbx/
★ 输出: logs/iss364/10_recon90.json (90 件逐件事实) + logs/iss364/11_recon90.txt (人读摘要)

口径全部与 state/check_pcb_nets.py (C4) 同源但独立实现 (纯 python 文本解析, 零 pcbnew 依赖):
  · 网表行按 board 列过滤 ⇒ 只留 MAIN_PCB
  · 节点串 "DEV" (bare) ⇒ 占位脚号 (按行序 1..M)
  · 节点串 "DEV pin<N>" ⇒ 真实脚号
  · USB-IF 物理脚名 (A1/A4/.../shield) ⇒ 真实脚号
"""
import csv
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "logs", "iss361"))
import iss361_board_read as R  # noqa: E402  (ISS-361 的纯 python 读板/网表/BOM 口径, 只读复用)

LIBROOT = "/home/yuewuya/kicad/AppDir/share/kicad/footprints"
BOM = os.path.join(ROOT, "HW", "BOM_v1.csv")
NET = os.path.join(ROOT, "HW", "netlist_v1.csv")
PINS = os.path.join(ROOT, "HW", "netlist_v1_pins.csv")
PCB = os.path.join(ROOT, "HW", "PCB", "demo_mainboard.kicad_pcb")
FPTRUTH = os.path.join(ROOT, "HW", "FP_TRUTH_BASELINE.md")
GAPDOC = os.path.join(ROOT, "HW", "PCB", "FP_TRUTH_COVERAGE_GAP.md")
OUT_JSON = os.path.join(HERE, "10_recon90.json")
OUT_TXT = os.path.join(HERE, "11_recon90.txt")

PSEUDO = ("RAIL_", "NET_")
BOARD_FILTER = "MAIN_PCB"
PIN_RE = re.compile(r"pin\d+(\+pin\d+)*")
USBIF_RE = re.compile(r"^(?:[AB](?:1|4|5|6|7|9|12)|shield)$")


# ------------------------------------------------------------------ 板面读取

def _blocks(text, name):
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
        out.append(text[s:j + 1])
        i = j + 1
    return out


def _layer_bbox(blk, layer):
    xs, ys = [], []
    for tag in ("fp_line", "fp_rect"):
        for b in _blocks(blk, tag):
            lm = re.search(r'\(layer "([^"]*)"\)', b)
            if not lm or lm.group(1) != layer:
                continue
            for grp in ("start", "end"):
                m = re.search(r"\(%s ([-\d\.]+) ([-\d\.]+)\)" % grp, b)
                if m:
                    xs.append(float(m.group(1)))
                    ys.append(float(m.group(2)))
    if not xs:
        return (0.0, 0.0)
    return (max(xs) - min(xs), max(ys) - min(ys))


def read_board_full(path):
    """⇒ {ref: {"libid","value","pads":[(num,net,x,y,w,h)], "fab":(w,h), "crtyd":(w,h)}}"""
    text = open(path, encoding="utf-8").read()
    out = {}
    for m in re.finditer(r'^\t\(footprint ', text, re.M):
        s = m.start()
        cands = [text.find("\n\t(footprint ", s + 1), text.find("\n\t(net ", s + 1)]
        cands = [c for c in cands if c != -1]
        e = min(cands) if cands else len(text)
        blk = text[s:e]
        rm = re.search(r'\(property "Reference" "([^"]*)"', blk)
        if not rm:
            continue
        ref = rm.group(1)
        vm = re.search(r'\(property "Value" "([^"]*)"', blk)
        libm = re.match(r'\(footprint "([^"]*)"', blk)
        pads = []
        for pb in _blocks(blk, "pad"):
            num = re.search(r'pad\s+"([^"]*)"', pb).group(1)
            at = re.search(r"\(at ([^)]*)\)", pb)
            sz = re.search(r"\(size ([^)]*)\)", pb)
            net = re.search(r'\(net (?:\d+ )?"([^"]*)"\)', pb)
            a = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", at.group(1))] if at else [0, 0]
            s2 = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", sz.group(1))] if sz else [0, 0]
            pads.append((num, net.group(1) if net else "", a[0], a[1], s2[0], s2[1]))
        out[ref] = {"libid": libm.group(1) if libm else "",
                    "value": vm.group(1) if vm else "",
                    "pads": pads,
                    "fab": _layer_bbox(blk, "F.Fab"),
                    "crtyd": _layer_bbox(blk, "F.CrtYd")}
    return out


# ------------------------------------------------------------------ .kicad_mod 读取

def read_mod(lib, name):
    """⇒ {"path","md5","pads":[(num,x,y,w,h)], "fab":(w,h), "crtyd":(w,h)} 或 None"""
    p = os.path.join(LIBROOT, "%s.pretty" % lib, "%s.kicad_mod" % name)
    if not os.path.isfile(p):
        return None
    text = open(p, encoding="utf-8").read()
    pads = []
    for pb in _blocks(text, "pad"):
        nm = re.search(r'pad\s+"([^"]*)"', pb)
        if not nm:
            continue
        at = re.search(r"\(at ([^)]*)\)", pb)
        sz = re.search(r"\(size ([^)]*)\)", pb)
        a = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", at.group(1))] if at else [0, 0]
        s2 = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", sz.group(1))] if sz else [0, 0]
        pads.append((nm.group(1), a[0], a[1], s2[0], s2[1]))
    return {"path": "%s.pretty/%s.kicad_mod" % (lib, name),
            "md5": hashlib.md5(open(p, "rb").read()).hexdigest(),
            "pads": pads,
            "fab": _layer_bbox(text, "F.Fab"),
            "crtyd": _layer_bbox(text, "F.CrtYd")}


def center_dist(pts):
    """焊盘中心两两最大距离 (mm)"""
    d = 0.0
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            d = max(d, ((pts[i][0] - pts[j][0]) ** 2 + (pts[i][1] - pts[j][1]) ** 2) ** 0.5)
    return round(d, 3)


# ------------------------------------------------------------------ 既有页解析

def md_rows_of(doc, start_pat, end_pat, header_contains):
    lines = open(doc, encoding="utf-8").read().splitlines()
    i = next(k for k, l in enumerate(lines) if re.search(start_pat, l))
    j = next(k for k, l in enumerate(lines) if k > i and re.search(end_pat, l))
    seg = lines[i:j]
    out = []
    for k, l in enumerate(seg):
        s = l.strip()
        if not s.startswith("|"):
            continue
        if set(s.replace("|", "").replace(" ", "")) <= set("-:"):
            continue
        if k == 0:
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        out.append(cells)
    # 表头 = 第一个非分隔行
    hdr = None
    for k, l in enumerate(seg):
        s = l.strip()
        if s.startswith("|") and header_contains in s:
            hdr = [c.strip() for c in s.strip("|").split("|")]
            break
    return hdr, out


def cell_of(hdr, row, key):
    kk = key.replace("`", "")
    for k, c in enumerate(hdr):
        if c.replace("`", "") == kk:
            return row[k] if k < len(row) else ""
    for k, c in enumerate(hdr):
        if kk and kk in c.replace("`", ""):
            return row[k] if k < len(row) else ""
    return ""


# ------------------------------------------------------------------ 主流程

def main():
    bom_rows = R.load_bom(BOM)
    bom = {r["ref"]: r for r in bom_rows}
    main_t, chg_t, total_t = R.iss356_targets(bom_rows)
    ph, per_ref, notes = R.netlist_placeholder(NET)
    board = read_board_full(PCB)
    c4 = set(ph)
    iss = set(total_t)
    inter = c4 & iss
    diff = c4 - iss
    gap = R.coverage_gap(bom_rows, c4)

    bucket_of = {}
    for r in c4:
        if r in inter:
            bucket_of[r] = "靶内"
        elif bom[r]["type"] == "TP":
            bucket_of[r] = "TP"
        elif bom[r]["dnp"] == "DNP":
            bucket_of[r] = "DNP"
        else:
            bucket_of[r] = "缺口"

    # ---- 既有页逐件字段
    fh78, rows78 = md_rows_of(FPTRUTH, r"^## §2 逐 ref 表", r"^### §2\.1",
                              "目标 `lib:name`")
    fg13, rows13 = md_rows_of(GAPDOC, r"^## §2 ", r"^## §3 ", "目标 `lib:name`")
    base = {}
    for r in rows78:
        ref = cell_of(fh78, r, "ref").strip("`").strip()
        if not ref:
            continue
        base[ref] = {
            "libname": cell_of(fh78, r, "目标 `lib:name`").strip("`").strip(),
            "pathmd5": cell_of(fh78, r, "库文件实存路径 + md5"),
            "padcheck": cell_of(fh78, r, "焊盘数 / 网络核对结论 (实测)"),
            "opn": cell_of(fh78, r, "候选 OPN"),
            "ev": cell_of(fh78, r, "证据等级"),
            "chg": cell_of(fh78, r, "是否触发布局/布线改动"),
            "fb": cell_of(fh78, r, "降级方案"),
            "present_ledger": cell_of(fh78, r, "现占位族 (焊盘编号+尺寸+fab外框+中心距)"),
            "src": "FP_TRUTH_BASELINE §2",
        }
    for r in rows13:
        ref = cell_of(fg13, r, "ref").strip("`").strip()
        if not ref:
            continue
        base[ref] = {
            "libname": cell_of(fg13, r, "目标 `lib:name`").strip("`").strip(),
            "pathmd5": cell_of(fg13, r, "库文件实存路径 + md5"),
            "padcheck": cell_of(fg13, r, "焊盘数 / 网络核对结论 (实测)"),
            "opn": cell_of(fg13, r, "候选 OPN"),
            "ev": cell_of(fg13, r, "证据等级"),
            "chg": cell_of(fg13, r, "是否触发布局/布线改动"),
            "fb": cell_of(fg13, r, "降级方案"),
            "present_ledger": cell_of(fg13, r, "现占位族 (板面实测)"),
            "src": "FP_TRUTH_COVERAGE_GAP §2",
        }

    # ---- 脚表 (pin 真值已在脚表里)
    pins_rows = list(csv.DictReader(open(PINS, encoding="utf-8")))
    pin_of = {}   # (ref, net) -> pin 字符串
    for r in pins_rows:
        ref = (r.get("ref") or "").strip()
        pin = (r.get("pin") or "").strip()
        net = (r.get("net") or "").strip()
        if ref and pin:
            pin_of.setdefault((ref, net), []).append(pin)

    # ---- 网表行 (bare 节点串定位)
    net_rows = list(csv.DictReader(open(NET, encoding="utf-8")))
    main_rows = [r for r in net_rows
                 if (r.get("board") or "MAIN_PCB").strip() == BOARD_FILTER]
    bare_rows = {}    # ref -> [ (row_idx, col, net) ]
    for idx, r in enumerate(main_rows):
        for col in ("node1", "node2"):
            node = (r.get(col) or "").strip()
            if not node:
                continue
            comp, tail = R.split_node(node)
            if not comp or comp in PSEUDO:
                continue
            if tail and R.is_pad_name(tail):
                continue
            if tail:
                continue
            bare_rows.setdefault(comp, []).append(
                {"row": idx, "col": col, "node": node, "net": (r.get("net") or "").strip(),
                 "ref_col": (r.get("ref") or "").strip()})

    # ---- 90 件对象
    targets = sorted(inter) + sorted(gap)
    pieces = []
    for ref in targets:
        b = bom[ref]
        bd = board.get(ref)
        row = base.get(ref, {})
        libname = row.get("libname", "")
        mod = None
        if ":" in libname:
            lib, nm = libname.split(":", 1)
            mod = read_mod(lib, nm)
        # 板面几何
        bpads = bd["pads"] if bd else []
        b_present = {
            "pads_n": len(bpads),
            "pad_nums": [p[0] for p in bpads],
            "pad_sizes": sorted({"%s×%s" % ("%.3f" % p[4], "%.3f" % p[5]) for p in bpads}),
            "fab": [round(v, 3) for v in (bd["fab"] if bd else (0, 0))],
            "center": center_dist([(p[2], p[3]) for p in bpads]),
            "pad_net": ["%s=%s" % (p[0], p[1]) for p in bpads],
        }
        # 目标几何
        if mod:
            mpads = mod["pads"]
            t_present = {
                "pads_n": len(mpads),
                "pad_nums": [p[0] for p in mpads],
                "pad_sizes": sorted({"%s×%s" % ("%.3f" % p[3], "%.3f" % p[4]) for p in mpads}),
                "fab": [round(v, 3) for v in mod["fab"]],
                "crtyd": [round(v, 3) for v in mod["crtyd"]],
                "center": center_dist([(p[1], p[2]) for p in mpads]),
                "path": mod["path"],
                "md5": mod["md5"],
            }
        else:
            t_present = None
        # 具名脚作业包 (腿 B)
        legs = []
        for br in bare_rows.get(ref, []):
            pins = pin_of.get((ref, br["net"]), [])
            legs.append({"row": br["row"], "col": br["col"], "net": br["net"],
                         "bare": br["node"], "pins_table": pins})
        pieces.append({
            "ref": ref,
            "bucket": "靶内" if ref in inter else "缺口",
            "type": b["type"], "value": b["value"], "dnp": b["dnp"], "board": b["board"],
            "bom_footprint": b["footprint"], "bom_opn": b["opn"],
            "ledger_src": row.get("src", ""),
            "ledger_libname": libname,
            "ledger_pathmd5": row.get("pathmd5", ""),
            "ledger_padcheck": row.get("padcheck", ""),
            "ledger_opn": row.get("opn", ""),
            "ledger_ev": row.get("ev", ""),
            "ledger_chg": row.get("chg", ""),
            "ledger_fb": row.get("fb", ""),
            "ledger_present": row.get("present_ledger", ""),
            "board_geom": b_present,
            "target_geom": t_present,
            "c4_placeholder_pads": ph.get(ref, 0),
            "legB": legs,
        })

    data = {
        "counts": {
            "c4_total": len(c4),
            "iss356_total": len(iss),
            "iss356_main": len(main_t),
            "iss356_chg": len(chg_t),
            "inter_total": len(inter),
            "diff_total": len(diff),
            "gap_total": len(gap),
            "board_footprints": len(board),
            "target_total": len(targets),
        },
        "buckets": {"TP": sum(1 for r in c4 if bucket_of[r] == "TP"),
                    "DNP": sum(1 for r in c4 if bucket_of[r] == "DNP"),
                    "in_target": len(inter), "gap": len(gap)},
        "target_refs": targets,
        "gap_refs": gap,
        "c4_refs": sorted(c4),
        "pieces": pieces,
    }
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=1)

    # ---- 人读摘要
    T = []
    A = T.append
    A("=== ISS-364 实算摘要 (本机实跑) ===")
    A("C4=%d ISS356=%d (main %d / chg %d) 交集=%d 差集=%d 缺口=%d 板面封装=%d"
      % (len(c4), len(iss), len(main_t), len(chg_t), len(inter), len(diff), len(gap), len(board)))
    A("四桶: TP=%d DNP=%d 靶内=%d 缺口=%d  (和=%d)"
      % (data["buckets"]["TP"], data["buckets"]["DNP"], data["buckets"]["in_target"],
         data["buckets"]["gap"], sum(data["buckets"].values())))
    A("目标 90 件: %s" % ", ".join(targets))
    A("")
    A("--- 板面占位几何 vs 目标几何 (Δ) ---")
    A("%-26s %-4s %-34s %-34s %s" % ("ref", "桶", "现占位(板读)", "目标(读 .kicad_mod)", "Δ"))
    for p in pieces:
        g = p["board_geom"]
        t = p["target_geom"]
        cur = "%dpad %s fab %.2f×%.2f ctr %.3f" % (g["pads_n"], "/".join(g["pad_sizes"]),
                                                    g["fab"][0], g["fab"][1], g["center"])
        if t:
            tgt = "%dpad %s fab %.2f×%.2f ctr %.3f" % (t["pads_n"], "/".join(t["pad_sizes"]),
                                                        t["fab"][0], t["fab"][1], t["center"])
            d = "Δpad %+d · Δfab %+.2f×%+.2f · Δctr %+.3f" % (
                t["pads_n"] - g["pads_n"], t["fab"][0] - g["fab"][0],
                t["fab"][1] - g["fab"][1], t["center"] - g["center"])
        else:
            tgt = "★无 .kicad_mod★"
            d = "—"
        A("%-26s %-4s %-34s %-34s %s" % (p["ref"], p["bucket"], cur, tgt, d))
    A("")
    A("--- 腿 B 具名脚 (bare → pinN) ---")
    tot = 0
    for p in pieces:
        if not p["legB"]:
            A("★ %s: 无 bare 节点串 (已在网表里具名?)" % p["ref"])
            continue
        s = ", ".join("%s→%s(net %s)" % (l["bare"], l["pins_table"], l["net"]) for l in p["legB"])
        tot += len(p["legB"])
        A("%-26s %s" % (p["ref"], s))
    A("裸端总数 = %d · 90 件覆盖 %d 件" % (tot, sum(1 for p in pieces if p["legB"])))
    with open(OUT_TXT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(T) + "\n")
    print("\n".join(T))
    print("\n[build] 已写 %s" % OUT_JSON)
    return 0


if __name__ == "__main__":
    sys.exit(main())
