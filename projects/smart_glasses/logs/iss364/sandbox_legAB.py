#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-364 · 沙盒可达性证明 · 腿 A (换官方 land) + 腿 B (网表节点具名)

★ 必须用 KiCad python 跑: bash state/pcbnew_py.sh logs/iss364/sandbox_legAB.py
★ 零写板: 板副本落 tmp/iss364_sbx/ · 真板零改动
★ 零落表: 网表副本落 tmp/iss364_sbx/ · 真表零改动
★ **C1/C2/C3/C4 的读数由 state/check_pcb_nets.py 的真代码给出** (importlib 载入 + 只把 NET 常量指向副本)
   ⇒ 不复制闸代码 ⇒ 无「副本漂移」风险

四轮:
  S0 基线      : 真板 + 真网表
  S1 腿 A 单独 : 板副本(90 件换官方 land) + 真网表
  S2 腿 B 单独 : 真板 + 网表副本(90 件节点具名)
  S3 腿 A + 腿 B: 板副本 + 网表副本
"""
import csv
import importlib.util
import json
import os
import re
import shutil
import sys
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SBX = os.path.join(ROOT, "tmp", "iss364_sbx")
os.makedirs(SBX, exist_ok=True)
LIBROOT = "/home/yuewuya/kicad/AppDir/share/kicad/footprints"
BOARD = os.path.join(ROOT, "HW", "PCB", "demo_mainboard.kicad_pcb")
NET = os.path.join(ROOT, "HW", "netlist_v1.csv")
PINS = os.path.join(ROOT, "HW", "netlist_v1_pins.csv")

sys.path.insert(0, os.path.join(ROOT, "state"))
sys.path.insert(0, os.path.join(ROOT, "logs", "iss361"))
import pcbnew  # noqa: E402
import iss361_board_read as R  # noqa: E402

# ---- 载入真闸代码 (C1/C2/C3/C4 口径一个字节不抄)
_spec = importlib.util.spec_from_file_location("cpn", os.path.join(ROOT, "state", "check_pcb_nets.py"))
cpn = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cpn)


def load_jobs():
    with open(os.path.join(HERE, "12_legB_jobs.json"), encoding="utf-8") as fh:
        return json.load(fh)["jobs"]


def load_targets():
    with open(os.path.join(HERE, "10_recon90.json"), encoding="utf-8") as fh:
        d = json.load(fh)
    return {p["ref"]: p for p in d["pieces"]}


# ---------------------------------------------------------------- 腿 B: 网表节点具名

def build_legB_netlist(jobs, out_path):
    """按 12_legB_jobs.json 的 182 条指令改网表副本 (真表零改动)"""
    with open(NET, encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
        hdr = list(rows[0].keys())
    # 行号 → 指令
    by_line = {}
    for j in jobs:
        for r in j["renames"]:
            if r.get("new_node"):
                by_line.setdefault(r["lineno"], []).append((r["col"], r["new_node"]))
    n_ren = 0
    for i, r in enumerate(rows):
        ln = i + 2
        for col, newnode in by_line.get(ln, []):
            old = r[col]
            r[col] = newnode
            n_ren += 1
            assert old != newnode, (ln, col, old)
    # 补行: 脚表里有、网表里没以 bare 形态出现的脚
    add = []
    for j in jobs:
        for a in j["add_rows"]:
            add.append(a)
    for a in add:
        row = {h: "" for h in hdr}
        row["page"] = "P1"
        row["net"] = a["net"]
        row["node1"] = a["suggest_node1"]
        row["node2"] = a["suggest_node2"]
        row["ref"] = a["ref"]
        row["value"] = a.get("value", "")
        row["type"] = a.get("type", "")
        row["dnp"] = "必装"
        row["board"] = "MAIN_PCB"
        row["evidence"] = "[实测]"
        row["tbd"] = ""
        row["conn_id"] = ""
        row["footprint"] = a.get("footprint", "")
        row["opn"] = a.get("opn", "")
        row["note"] = ("★ISS-364 腿 B 补行: 脚表 netlist_v1_pins.csv 已有该脚 (pin%s · net %s), "
                       "但 netlist_v1.csv 里该器件没以节点形态出现 ⇒ 本行补齐具名脚★"
                       % (a["pin"], a["net"]))
        rows.append(row)
    with open(out_path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=hdr)
        w.writeheader()
        w.writerows(rows)
    return n_ren, len(add)


# ---------------------------------------------------------------- 腿 A: 换官方 land (★文本级★)
#
# ★为什么用文本级而不是 pcbnew 对象级★:
#   pcbnew 的 PAD/PCB_SHAPE 克隆会在 SWIG 侧留下悬空代理 ⇒ 后续 LoadBoard 拿回
#   'SwigPyObject' (无 GetFootprints) ⇒ 读数作废 (实测踩过, 2026-11-23 16:2x)
#   ⇒ 改成【板文件文本级 splice】: 板面 footprint 块里换掉 (pad ...) 与 F.Fab 图元块
#   ⇒ 确定性 · 无对象生命周期风险 · 真板零改动
#
# 板文件格式 (KiCad 10): footprint 块里
#   · (at X Y) 是绝对位置
#   · pad 的 (at dx dy) 与 fp_line 的 (start/end) 都是【相对 footprint 原点】⇒ 与 .kicad_mod 同坐标系 ⇒ 可直接搬
#   · pad 的网络写作 (net "NAME") (只有名字, 无编号) ⇒ 换 land 时顺手按脚表真值改 net


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
    """从 .kicad_mod 取 (pad ...) 块 (原样, 不改坐标)"""
    p = os.path.join(LIBROOT, "%s.pretty" % lib, "%s.kicad_mod" % nm)
    if not os.path.isfile(p):
        return None
    t = open(p, encoding="utf-8").read()
    return [b for (_s, _e, b) in _blocks_with_span(t, "pad")]


def _mod_fab_graphics(lib, nm):
    """从 .kicad_mod 取 F.Fab 图元块 (fp_line / fp_rect)"""
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
    """把块里的 (uuid "...") 换成新 uuid (★同一官方封装用在多件上 ⇒ uuid 必须逐件重生成★)"""
    return re.sub(r'\(uuid "[^"]*"\)', '(uuid "%s")' % _new_uuid(), block)


def _set_net(block, netname):
    """把 pad 块的网络改成 netname (板文件写法: (net "NAME"))"""
    if re.search(r'\n\t*\(net "[^"]*"\)', block):
        return re.sub(r'\(net "[^"]*"\)', '(net "%s")' % netname, block)
    # 无 net 块 ⇒ 插在 layers 之后
    m = re.search(r'\n(\t*)\(layers [^)]*\)', block)
    if not m:
        return block
    ind = m.group(1)
    return block[:m.end()] + '\n%s(net "%s")' % (ind, netname) + block[m.end():]


def _pad_num(block):
    m = re.search(r'pad\s+"([^"]*)"', block)
    return m.group(1) if m else ""


def build_legA_board(targets, jobs, out_path, skip_refs=()):
    """文本级: 90 件的 footprint 换成官方 land 的 pad 集 + F.Fab 外框"""
    text = open(BOARD, encoding="utf-8").read()
    net_of_pin = {}
    with open(PINS, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            ref = (r.get("ref") or "").strip()
            pin = (r.get("pin") or "").strip()
            net = (r.get("net") or "").strip()
            if ref and pin:
                net_of_pin[(ref, pin)] = net
    report = []
    n_sw = 0
    n_pad = 0
    # 逐个 footprint 块 (从后往前替换 ⇒ 偏移不变)
    blocks = []
    for m in re.finditer(r'\n\t\(footprint ', text):
        s = m.start() + 1
        cands = [text.find("\n\t(footprint ", s + 1), text.find("\n\t(net ", s + 1)]
        cands = [c for c in cands if c != -1]
        e = min(cands) if cands else len(text)
        blocks.append((s, e, text[s:e]))
    for (s, e, blk) in reversed(blocks):
        rm = re.search(r'\(property "Reference" "([^"]*)"', blk)
        if not rm:
            continue
        ref = rm.group(1)
        if ref in skip_refs:
            continue
        p = targets.get(ref)
        if not p:
            continue
        libname = p["ledger_libname"]
        if ":" not in libname:
            continue
        lib, nm = libname.split(":", 1)
        libdir = os.path.join(LIBROOT, "%s.pretty" % lib)
        if not os.path.isdir(libdir):
            report.append({"ref": ref, "ok": False, "why": "库目录不在盘: %s" % libdir})
            continue
        newpads = _mod_pads(lib, nm)
        newfab = _mod_fab_graphics(lib, nm)
        if newpads is None or newfab is None:
            report.append({"ref": ref, "ok": False, "why": "★.kicad_mod 读不到: %s:%s" % (lib, nm)})
            continue
        # ① 构造新 pad 块 (坐标照搬 .kicad_mod ⇒ 相对 footprint 原点; 网络按脚表真值)
        ind = "\t\t"
        built = []
        for pb in newpads:
            num = _pad_num(pb)
            digits = "".join(ch for ch in num if ch.isdigit()) or "1"
            netname = net_of_pin.get((ref, digits))
            if netname is None:
                netname = net_of_pin.get((ref, "1"))
            b = _reuuid(pb)
            if netname:
                b = _set_net(b, netname)
            built.append(b)
            n_pad += 1
        # ② 删掉旧 pad 块 + 旧 F.Fab 图元块
        inner = blk
        # 旧 pad
        for (ps, pe, pb) in reversed(_blocks_with_span(inner, "pad")):
            inner = inner[:ps] + inner[pe:]
        # 旧 F.Fab 图元
        for tag in ("fp_line", "fp_rect"):
            for (gs, ge, gb) in reversed(_blocks_with_span(inner, tag)):
                if re.search(r'\(layer "F\.Fab"\)', gb):
                    inner = inner[:gs] + inner[ge:]
        # ③ 插入新 pad + 新 F.Fab 图元 (放在 (embedded_fonts no) 之前)
        anchor = inner.rfind('\n\t\t(embedded_fonts')
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
    return n_sw, n_pad, report


# ---------------------------------------------------------------- 读数

def read_c4(mod, net_path, board_path):
    mod.NET = net_path
    rc, body, ctx = mod.run_checks(board_path)
    c4n = None
    c1 = ""
    c3 = ""
    for ln in body:
        if "C4" in ln and "占位" in ln:
            import re
            m = re.search(r"器件 (\d+) 个", ln)
            c4n = int(m.group(1)) if m else -1
        if ln.strip().startswith("✅ C1") or ln.strip().startswith("❌ C1"):
            c1 = ln.strip()
        if ln.strip().startswith("✅ C3") or ln.strip().startswith("❌ C3"):
            c3 = ln.strip()
    fails = ctx.get("fails", [])
    return {"rc": rc, "c4": c4n, "c1": c1, "c3": c3, "fails": fails,
            "body": body}


def main():
    jobs = load_jobs()
    targets = load_targets()
    out = {}

    # ---- 网表副本 (腿 B)
    netB = os.path.join(SBX, "netlist_v1_legB.csv")
    n_ren, n_add = build_legB_netlist(jobs, netB)
    print("[sbx] 腿 B 网表副本: 改名 %d 条 + 补行 %d 条 ⇒ %s" % (n_ren, n_add, netB))

    # ---- 板副本 (腿 A)
    boardA = os.path.join(SBX, "board_legA.kicad_pcb")
    n_sw, n_pad, report = build_legA_board(targets, jobs, boardA)
    print("[sbx] 腿 A 板副本: 换 land %d 件 / 落 %d 个焊盘 ⇒ %s" % (n_sw, n_pad, boardA))
    if report:
        print("[sbx] 腿 A 告警 %d 条: %s" % (len(report), report[:3]))
    # ---- 板副本 (腿 A · K3 走 (b) 路: 那 3 只 KMR2 按键不换 land, 保留 2 land 占位)
    K3_SW = ("SW_BOOT", "SW_KEY_PWR", "SW_RST")
    boardA2 = os.path.join(SBX, "board_legA_k3b.kicad_pcb")
    n_sw2, n_pad2, rep2 = build_legA_board(targets, jobs, boardA2, skip_refs=set(K3_SW))
    print("[sbx] 腿 A (K3-b) 板副本: 换 land %d 件 / 落 %d 个焊盘 ⇒ %s" % (n_sw2, n_pad2, boardA2))

    # ---- 四轮读数
    runs = [
        ("S0_基线_真板真表", BOARD, NET),
        ("S1_腿A单独", boardA, NET),
        ("S2_腿B单独", BOARD, netB),
        ("S3_腿A加腿B", boardA, netB),
        ("S4_腿A加腿B_K3走b路", boardA2, netB),
    ]
    allbody = []
    for name, bp, np_ in runs:
        r = read_c4(cpn, np_, bp)
        out[name] = {k: v for k, v in r.items() if k != "body"}
        out[name]["body_head"] = [x for x in r["body"][:6]]
        allbody.append("=" * 78)
        allbody.append("【%s】 板=%s  网表=%s  rc=%d  C4=%s" %
                       (name, os.path.basename(bp), os.path.basename(np_), r["rc"], r["c4"]))
        allbody.extend(r["body"])
        print("[sbx] %-22s rc=%d  C4=%s  %s" % (name, r["rc"], r["c4"], r["c1"]))
        for f in r["fails"]:
            print("        · %s" % f)
    with open(os.path.join(HERE, "20_sandbox_readings.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    with open(os.path.join(HERE, "21_sandbox_bodies.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(allbody) + "\n")
    print("[sbx] 已写 logs/iss364/20_sandbox_readings.json + 21_sandbox_bodies.txt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
