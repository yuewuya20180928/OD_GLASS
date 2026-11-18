#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iss321_sb_make.py —— ISS-321 · SW 侧改名沙盒造场 (★只写 tmp/iss321_sandbox/★)

★★边界 (★硬★★) ★★:
  · ★零写板★: 项目板 `HW/PCB/demo_mainboard.kicad_pcb` 一个字节不许动 (★只读+文本替换出副本★)
  · ★零落表★: 网表 / 脚表 / BOM / 原理图 一律不许改 (★只读+出副本★)
  · ★零改闸★: `SW/tools/*.py` 一个字节不许改 (★只出改法, 不改闸★)
  · ★沙盒只写 tmp/ + logs/iss321/★

★口径单源 = `state/gen_kicad_sch.py::kicad_ref()` (★ISS-205 规则·与 ISS-317 同源·逐字复刻★)
★真集 = `logs/iss321/rename_sets.json` (★① 的机器解析结果★)

─── 造场清单 ──────────────────────────────────────────────────────────
  沙盒根 tmp/iss321_sandbox/root/
    HW/netlist_v1.csv           ★改名后的网表副本 (ref 列 + node1/node2 里的器件名)
    HW/netlist_v1_pins.csv      ★改名后的脚表副本 (ref 列 + pin_id 前缀)
    HW/BOM_v1.csv               ★改名后的 BOM 副本 (ref 列)
    HW/PCB/demo_mainboard.kicad_pcb  ★改名后的板副本 (property "Reference")
    SW/*.md                    ★**改名后的 SW 文档副本** (★位号字面量同步改★
                                ⇒ 用来证明「SW 侧同步改了就绿」)
    SW/tools/*.py              ★**真闸脚本的软链** (★不改闸本体★)
    state/issue_log.yaml       ★真件软链 (★只读★)
    HW/SCHEMATIC_LANDING_V1_LANDED.md  ★真件软链
    SW/SW_MD5_BASELINE_LEDGER.md       ★真件软链

  ★★为什么 SW 文档要出副本而不是只跑「板改名 + 文档不改」★★:
    · 场景 S1 (板/表改名 + SW 文档【没】改) ⇒ 期望【check_sw_ref_reachability 判红·改名漂移】
    · 场景 S2 (板/表改名 + SW 文档【同步】改) ⇒ 期望【全绿 ⇒ 证明闸 rename-safe】
    · ★两个场景都要跑, 才能把「闸的问题」与「文档没跟上的问题」分开★ ★
"""
import csv
import io
import json
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))          # logs/iss321/
PROJ = os.path.dirname(os.path.dirname(HERE))              # 项目根
SB = os.path.join(PROJ, "tmp", "iss321_sandbox")
ROOT = os.path.join(SB, "root")
SETS = os.path.join(HERE, "rename_sets.json")

PSEUDO = ("RAIL_", "NET_")
REF_RE = re.compile(r'(\(property "Reference" ")([^"]*)(")')


def kicad_ref(ref):
    """★ISS-205 口径 (与 state/gen_kicad_sch.py::kicad_ref() 同源·逐字复刻)★"""
    r = (ref or "").strip()
    if r and r[-1].isdigit():
        return r
    return r + "_1"


def load_map():
    d = json.load(open(SETS, encoding="utf-8"))
    m = d["map"]
    # ★只对「要改」的做映射; 不动的保持原样★
    return {k: v for k, v in m.items() if k != v}


def rename_ref(tok, mapping):
    """按真集映射改名; 伪器件/不在真集 ⇒ 原样"""
    tok = (tok or "").strip()
    if not tok or tok.startswith(PSEUDO):
        return tok
    return mapping.get(tok, tok)


# ════════════════════════════════════════════════════════════════════
# 板副本
# ════════════════════════════════════════════════════════════════════
def build_board(out_path, mapping):
    src = os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb")
    txt = open(src, encoding="utf-8", errors="replace").read()
    n = 0
    out = []
    last = 0
    for m in REF_RE.finditer(txt):
        old = m.group(2)
        new = rename_ref(old, mapping)
        if new != old:
            n += 1
        out.append(txt[last:m.start(2)])
        out.append(new)
        last = m.end(2)
    out.append(txt[last:])
    open(out_path, "w", encoding="utf-8", errors="replace").write("".join(out))
    return n


# ════════════════════════════════════════════════════════════════════
# 网表副本
# ════════════════════════════════════════════════════════════════════
NODE_RE = re.compile(r"^([A-Za-z_0-9]+)(\s+.*)?$")


def rename_node(node, mapping):
    node = (node or "").strip()
    if not node:
        return node
    m = NODE_RE.match(node)
    if not m:
        return node
    comp = m.group(1)
    tail = m.group(2) or ""
    if comp.startswith(PSEUDO):
        return node
    return rename_ref(comp, mapping) + tail


def build_netlist(out_path, mapping):
    src = os.path.join(PROJ, "HW", "netlist_v1.csv")
    rows = list(csv.DictReader(open(src, encoding="utf-8")))
    flds = list(rows[0].keys())
    n = 0
    out = []
    for r in rows:
        r2 = dict(r)
        ref = (r2.get("ref") or "").strip()
        if ref and not ref.startswith(PSEUDO):
            new = rename_ref(ref, mapping)
            if new != ref:
                n += 1
            r2["ref"] = new
        for col in ("node1", "node2"):
            if col in r2:
                r2[col] = rename_node(r2[col], mapping)
        out.append(r2)
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=flds)
        w.writeheader()
        for r in out:
            w.writerow(r)
    return n


def build_pins(out_path, mapping):
    src = os.path.join(PROJ, "HW", "netlist_v1_pins.csv")
    rows = list(csv.DictReader(open(src, encoding="utf-8")))
    flds = list(rows[0].keys())
    n = 0
    out = []
    for r in rows:
        r2 = dict(r)
        ref = (r2.get("ref") or "").strip()
        if ref and not ref.startswith(PSEUDO):
            new = rename_ref(ref, mapping)
            if new != ref:
                n += 1
            r2["ref"] = new
            # pin_id 形如 "REF.pin1" / "REF.B" ⇒ 前缀跟着改
            pid = r2.get("pin_id") or ""
            if pid.startswith(ref + "."):
                r2["pin_id"] = new + pid[len(ref):]
        out.append(r2)
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=flds)
        w.writeheader()
        for r in out:
            w.writerow(r)
    return n


def build_bom(out_path, mapping):
    src = os.path.join(PROJ, "HW", "BOM_v1.csv")
    rows = list(csv.DictReader(open(src, encoding="utf-8")))
    flds = list(rows[0].keys())
    n = 0
    out = []
    for r in rows:
        r2 = dict(r)
        ref = (r2.get("ref") or "").strip()
        if ref and not ref.startswith(PSEUDO):
            new = rename_ref(ref, mapping)
            if new != ref:
                n += 1
            r2["ref"] = new
        out.append(r2)
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=flds)
        w.writeheader()
        for r in out:
            w.writerow(r)
    return n


# ════════════════════════════════════════════════════════════════════
# SW 文档副本 (★位号字面量同步改·用真集精确匹配·不许靠前缀猜★)
# ════════════════════════════════════════════════════════════════════
def build_sw_docs(out_dir, mapping, rename_docs=True):
    """★rename_docs=False ⇒ 出【没改】的副本 (场景 S1)★"""
    os.makedirs(out_dir, exist_ok=True)
    sd = os.path.join(PROJ, "SW")
    n_files = 0
    n_hits = 0
    # ★长的名字先替换 (★避免 "R_PU" 先替掉 "R_PU_BOOT_N"★)
    keys = sorted(mapping.keys(), key=len, reverse=True)
    for name in sorted(os.listdir(sd)):
        if not name.endswith(".md"):
            continue
        txt = open(os.path.join(sd, name), encoding="utf-8", errors="replace").read()
        if rename_docs:
            for old in keys:
                new = mapping[old]
                pat = re.compile(r"(?<![A-Za-z0-9_])" + re.escape(old) + r"(?![A-Za-z0-9_])")
                txt, c = pat.subn(new, txt)
                n_hits += c
        open(os.path.join(out_dir, name), "w", encoding="utf-8", errors="replace").write(txt)
        n_files += 1
    return n_files, n_hits


# ════════════════════════════════════════════════════════════════════
def link(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.lexists(dst):
        os.remove(dst)
    os.symlink(src, dst)


def mirror(src_dir, dst_dir, skip_names=()):
    """★递归软链镜像 (★不复制字节·省磁盘·保证【真件一个字节都没动】★)★"""
    os.makedirs(dst_dir, exist_ok=True)
    for name in sorted(os.listdir(src_dir)):
        if name in skip_names:
            continue
        s = os.path.join(src_dir, name)
        d = os.path.join(dst_dir, name)
        if os.path.isdir(s) and not os.path.islink(s):
            mirror(s, d, skip_names)
        else:
            link(s, d)


def build_root(root, mapping, rename_docs, tag):
    """造一棵沙盒虚拟根 (★HW/SW/state 等全部递归软链到真件·只有要改的那几件是副本★)"""
    if os.path.isdir(root):
        shutil.rmtree(root)
    os.makedirs(root)
    # ── ① 递归软链镜像 (HW / SW / state / MECH / REF / REQ / PRINT / config / docs / deploy) ──
    for d in ("HW", "SW", "state", "MECH", "REF", "REQ", "PRINT", "config", "docs",
              "deploy", "HANDOFF"):
        p = os.path.join(PROJ, d)
        if os.path.isdir(p):
            mirror(p, os.path.join(root, d), skip_names=("tmp", "__pycache__"))
    # ── ② tmp (★沙盒临时树·不许落 /tmp★) ──
    os.makedirs(os.path.join(root, "tmp"), exist_ok=True)

    # ── ③ 要改的那几件: 换成副本 (★覆盖掉软链★) ──
    def replace(rel, builder):
        dst = os.path.join(root, rel)
        if os.path.lexists(dst):
            os.remove(dst)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        return builder(dst)

    nb = replace("HW/netlist_v1.csv", lambda p: build_netlist(p, mapping))
    np_ = replace("HW/netlist_v1_pins.csv", lambda p: build_pins(p, mapping))
    nbo = replace("HW/BOM_v1.csv", lambda p: build_bom(p, mapping))
    npcb = replace("HW/PCB/demo_mainboard.kicad_pcb", lambda p: build_board(p, mapping))

    # ── ④ SW 文档副本 (★场景 S1 = 没改 / S2 = 同步改了★) ──
    swdir = os.path.join(root, "SW")
    ndocs = 0
    nhits = 0
    sd = os.path.join(PROJ, "SW")
    for name in sorted(os.listdir(sd)):
        if not name.endswith(".md"):
            continue
        dst = os.path.join(swdir, name)
        if os.path.lexists(dst):
            os.remove(dst)
        txt = open(os.path.join(sd, name), encoding="utf-8", errors="replace").read()
        if rename_docs:
            for old in sorted(mapping.keys(), key=len, reverse=True):
                new = mapping[old]
                pat = re.compile(r"(?<![A-Za-z0-9_])" + re.escape(old) + r"(?![A-Za-z0-9_])")
                txt, c = pat.subn(new, txt)
                nhits += c
        open(dst, "w", encoding="utf-8", errors="replace").write(txt)
        ndocs += 1

    print("  ★沙盒根 %-28s 网表改 %3d · 脚表改 %3d · BOM改 %3d · 板改 %3d · SW文档 %d 份/位号替换 %d 处"
          % (tag, nb, np_, nbo, npcb, ndocs, nhits))
    return root


def main():
    os.makedirs(SB, exist_ok=True)
    mapping = load_map()
    print("=" * 92)
    print("ISS-321 · SW 侧改名沙盒造场 (★只写 tmp/iss321_sandbox/★)")
    print("=" * 92)
    print("★改名映射条数 = %d (★来自 logs/iss321/rename_sets.json 的①机器解析★)" % len(mapping))

    # 场景 S1: 板/表改名 + SW 文档【没】改
    build_root(os.path.join(SB, "rootS1"), mapping, rename_docs=False, tag="rootS1 (SW 文档未改)")
    # 场景 S2: 板/表改名 + SW 文档【同步】改
    build_root(os.path.join(SB, "rootS2"), mapping, rename_docs=True, tag="rootS2 (SW 文档同步改)")
    # 场景 S0: 什么都没改 (对照基线 · 全部软链指向真件)
    s0 = os.path.join(SB, "rootS0")
    if os.path.isdir(s0):
        shutil.rmtree(s0)
    os.makedirs(s0)
    for d in ("HW", "SW", "state", "MECH", "REF", "REQ", "PRINT", "config", "docs",
              "deploy", "HANDOFF"):
        p = os.path.join(PROJ, d)
        if os.path.isdir(p):
            mirror(p, os.path.join(s0, d), skip_names=("tmp", "__pycache__"))
    os.makedirs(os.path.join(s0, "tmp"), exist_ok=True)
    print("  ★沙盒根 %-28s (全部软链指向真件 · 不改任何东西)" % "rootS0 (基线)")
    print("\n★沙盒造场完成 · 只写 tmp/iss321_sandbox/")


if __name__ == "__main__":
    main()
