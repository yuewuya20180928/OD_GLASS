#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iss321_sb_make_s3.py —— ISS-321 · 场景 S3 造场 (★只写 tmp/iss321_sandbox/★)

★★场景 S3 = 「板那一趟全部做对之后」的盘面 ★★:
    · 板 / 网表 / 脚表 / BOM 【已改名】 (★186 个·kicad_ref 口径★)
    · SW 文档 【已同步改名】
    · ★落表台账 【已记合法落表行】 (★网表/脚表/BOM 三件 + 板一件·前后 md5 全写★)
    · ★issue_log 【已记 ISS-321 的落表留痕行】 (★文件名 + 前后 md5★)
    ⇒ ★跑完还是红的 ⇒ 【判据本身写死了旧位号 / 或判据方向要改】 ⇒ ★那是真炸★
    ⇒ ★跑完就绿的 ⇒ 【那批红只是「合法落表还没记账」⇒ 不是改名特有的炸★

★为什么必须造这个场景 (★本单最关键的一步★):
    · 场景 S1/S2 里 R6 那批红是 **md5 链红** (盘上 md5 ≠ 台账链头) ⇒ 那是【落表留痕】问题,
      ★不是【位号写死】问题★ ⇒ 不造 S3 就分不清这两类
    · 只有 S3 能把「md5 链红」摘掉, 剩下的红才是【位号写死】的真炸

★★边界 ★★: 只写 tmp/iss321_sandbox/rootS3/ · 项目真件一个字节都不动 ★★
"""
import csv
import hashlib
import json
import os
import re
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))          # logs/iss321/
PROJ = os.path.dirname(os.path.dirname(HERE))              # 项目根
SB = os.path.join(PROJ, "tmp", "iss321_sandbox")
S3 = os.path.join(SB, "rootS3")
SETS = os.path.join(HERE, "rename_sets.json")

PSEUDO = ("RAIL_", "NET_")
REF_RE = re.compile(r'(\(property "Reference" ")([^"]*)(")')
NODE_RE = re.compile(r"^([A-Za-z_0-9]+)(\s+.*)?$")
TICKET = "ISS-321"


def kicad_ref(ref):
    r = (ref or "").strip()
    if r and r[-1].isdigit():
        return r
    return r + "_1"


def md5_of(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_map():
    d = json.load(open(SETS, encoding="utf-8"))
    return {k: v for k, v in d["map"].items() if k != v}


def rename_ref(tok, mapping):
    tok = (tok or "").strip()
    if not tok or tok.startswith(PSEUDO):
        return tok
    return mapping.get(tok, tok)


def rename_node(node, mapping):
    node = (node or "").strip()
    if not node:
        return node
    m = NODE_RE.match(node)
    if not m:
        return node
    comp = m.group(1)
    if comp.startswith(PSEUDO):
        return node
    return rename_ref(comp, mapping) + (m.group(2) or "")


def rewrite_csv(src, dst, mapping, mode):
    rows = list(csv.DictReader(open(src, encoding="utf-8")))
    flds = list(rows[0].keys())
    out = []
    for r in rows:
        r2 = dict(r)
        ref = (r2.get("ref") or "").strip()
        if ref and not ref.startswith(PSEUDO):
            r2["ref"] = rename_ref(ref, mapping)
            if mode == "pins":
                pid = r2.get("pin_id") or ""
                if pid.startswith(ref + "."):
                    r2["pin_id"] = r2["ref"] + pid[len(ref):]
        for col in ("node1", "node2"):
            if col in r2:
                r2[col] = rename_node(r2[col], mapping)
        out.append(r2)
    with open(dst, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=flds)
        w.writeheader()
        for r in out:
            w.writerow(r)


def rewrite_board(src, dst, mapping):
    txt = open(src, encoding="utf-8", errors="replace").read()
    out, last = [], 0
    for m in REF_RE.finditer(txt):
        out.append(txt[last:m.start(2)])
        out.append(rename_ref(m.group(2), mapping))
        last = m.end(2)
    out.append(txt[last:])
    open(dst, "w", encoding="utf-8", errors="replace").write("".join(out))


def mirror(src_dir, dst_dir, skip_names=()):
    os.makedirs(dst_dir, exist_ok=True)
    for name in sorted(os.listdir(src_dir)):
        if name in skip_names:
            continue
        s = os.path.join(src_dir, name)
        d = os.path.join(dst_dir, name)
        if os.path.isdir(s) and not os.path.islink(s):
            mirror(s, d, skip_names)
        else:
            if os.path.lexists(d):
                os.remove(d)
            os.symlink(s, d)


def main():
    mapping = load_map()
    if os.path.isdir(S3):
        shutil.rmtree(S3)
    os.makedirs(S3)

    # ── ① 递归软链镜像 ──
    for d in ("HW", "SW", "state", "MECH", "REF", "REQ", "PRINT", "config", "docs",
              "deploy", "HANDOFF"):
        p = os.path.join(PROJ, d)
        if os.path.isdir(p):
            mirror(p, os.path.join(S3, d), skip_names=("tmp", "__pycache__"))
    os.makedirs(os.path.join(S3, "tmp"), exist_ok=True)

    # ── ② 改名四件 (板/网表/脚表/BOM) ──
    def replace(rel, fn):
        dst = os.path.join(S3, rel)
        if os.path.lexists(dst):
            os.remove(dst)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        fn(dst)
        return dst

    p_net = replace("HW/netlist_v1.csv",
                     lambda p: rewrite_csv(os.path.join(PROJ, "HW", "netlist_v1.csv"), p, mapping, "net"))
    p_pins = replace("HW/netlist_v1_pins.csv",
                     lambda p: rewrite_csv(os.path.join(PROJ, "HW", "netlist_v1_pins.csv"), p, mapping, "pins"))
    p_bom = replace("HW/BOM_v1.csv",
                    lambda p: rewrite_csv(os.path.join(PROJ, "HW", "BOM_v1.csv"), p, mapping, "bom"))
    p_pcb = replace("HW/PCB/demo_mainboard.kicad_pcb",
                    lambda p: rewrite_board(os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb"),
                                            p, mapping))

    # ── ③ SW 文档同步改名 ──
    sd = os.path.join(PROJ, "SW")
    for name in sorted(os.listdir(sd)):
        if not name.endswith(".md"):
            continue
        dst = os.path.join(S3, "SW", name)
        if os.path.lexists(dst):
            os.remove(dst)
        txt = open(os.path.join(sd, name), encoding="utf-8", errors="replace").read()
        for old in sorted(mapping.keys(), key=len, reverse=True):
            pat = re.compile(r"(?<![A-Za-z0-9_])" + re.escape(old) + r"(?![A-Za-z0-9_])")
            txt = pat.subn(mapping[old], txt)[0]
        open(dst, "w", encoding="utf-8", errors="replace").write(txt)

    # ── ④ 落表台账: 追加【合法落表行】 (★网表/脚表/BOM/板 四件的前后 md5★) ──
    led_rel = "HW/SCHEMATIC_LANDING_V1_LANDED.md"
    led_dst = os.path.join(S3, led_rel)
    if os.path.lexists(led_dst):
        os.remove(led_dst)
    led_txt = open(os.path.join(PROJ, led_rel), encoding="utf-8").read()
    pairs = [
        ("HW/netlist_v1.csv", os.path.join(PROJ, "HW", "netlist_v1.csv"), p_net),
        ("HW/netlist_v1_pins.csv", os.path.join(PROJ, "HW", "netlist_v1_pins.csv"), p_pins),
        ("HW/BOM_v1.csv", os.path.join(PROJ, "HW", "BOM_v1.csv"), p_bom),
        ("HW/PCB/demo_mainboard.kicad_pcb", os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb"), p_pcb),
    ]
    rows = []
    for rel, oldp, newp in pairs:
        rows.append("| ★**ISS-321 (★S1 位号改名·合法落表★)** | `%s` | `%s` | `%s` | ★**2026-11-18** ★ | ★**%s** ★ |"
                    % (rel, md5_of(oldp), md5_of(newp), TICKET))
    led_txt += ("\n\n<!--ISS321_ROWS:BEGIN-->\n"
                "### ★★ISS-321 · S1 位号改名 (★合法落表·沙盒造场★) ★★\n\n"
                "| 批次 | 文件 | 改前 md5 | 改后 md5 | 落表时刻 | 单号 |\n"
                "|---|---|---|---|---|---|\n" + "\n".join(rows) + "\n<!--ISS321_ROWS:END-->\n")
    open(led_dst, "w", encoding="utf-8").write(led_txt)

    # ── ⑤ issue_log: 追加 ISS-321 条目 (★落表留痕行 = 文件名 + 前后 md5★) ──
    il_rel = "state/issue_log.yaml"
    il_dst = os.path.join(S3, il_rel)
    if os.path.lexists(il_dst):
        os.remove(il_dst)
    il_txt = open(os.path.join(PROJ, il_rel), encoding="utf-8").read()
    traces = []
    for rel, oldp, newp in pairs:
        traces.append("  evidence: '★落表留痕★ %s 改前 %s → 改后 %s (★S1 位号改名·合法落表·沙盒造场★)'"
                      % (rel, md5_of(oldp), md5_of(newp)))
    il_txt += ("\n- id: ISS-321-SANDBOX-LANDING\n"
               "  title: '★沙盒造场用的落表留痕条目 (★真 issue_log 一个字节都没动★)★'\n"
               "  owner: sw-lead\n"
               "  status: verified\n"
               "  severity: low\n"
               "  created_at: '2026-11-18'\n"
               + "\n".join(traces) + "\n")
    # ★把留痕写进【真单号 ISS-321】的条目里 (★R6 修法 B 要在真单号上查★) ★
    il_txt = il_txt.replace(
        "- id: ISS-321\n",
        "- id: ISS-321\n" + "\n".join(traces) + "\n", 1)
    open(il_dst, "w", encoding="utf-8").write(il_txt)

    print("=" * 92)
    print("ISS-321 · 场景 S3 造场完成 (★只写 tmp/iss321_sandbox/rootS3/★)")
    print("=" * 92)
    for rel, oldp, newp in pairs:
        print("  %-40s %s → %s" % (rel, md5_of(oldp)[:12], md5_of(newp)[:12]))
    print("★落表台账已追加 %d 条合法落表行 · issue_log 已在 ISS-321 条目里补留痕★" % len(rows))


if __name__ == "__main__":
    main()
