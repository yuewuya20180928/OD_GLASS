#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iss317_sb_make.py —— ISS-317 · U-1 + §2② 沙盒造场 (★只写 tmp/iss317_sandbox/★)

★**项目板 / 网表 / 脚表 / BOM / 受保护闸脚本一个字节不许动** ★
★判据脚本 = ISS-314 留档的沙盒副本 `logs/iss314/check_pcb_nets_reflookup.py` (★只读取·拷进沙盒跑★)

★口径单源 = `state/gen_kicad_sch.py::kicad_ref()` (★ISS-205 规则★)

─── 造场清单 ──────────────────────────────────────────────────────────
  板副本 (全部由项目板【文本替换】得到·不 import pcbnew·不碰项目板):
    board_ref1.kicad_pcb          全改名 (J_USB_C ⇒ J_USB_C_1)
    board_ref1_exJUSBC.kicad_pcb  甲方案: J_USB_C 豁免改名
    board_ref1_negNC.kicad_pcb    丙方案的反向用例: 给一个【非白名单】器件造一个 NC 焊盘
    board_t5b_dup.kicad_pcb        T5-b: 板侧同名封装出现两份 ⇒ 触发 build_ref_map 的 ambig 分支
    board_t6a_x2.kicad_pcb         T6-a: 板侧 ref ⇒ <原名>_2   (表侧从来没有的名字)
    board_t6b_xz1.kicad_pcb        T6-b: 板侧 ref ⇒ <原名>_Z_1 (反查不命中)
  网表副本:
    netlist_ref1.csv              全改名 (★表侧 ref + node 串里的器件名★)
    netlist_ref1_exJUSBC.csv      甲方案: J_USB_C 豁免改名
    netlist_t5a.csv               T5-a: 表侧同时存在 X 与 X_1 (⇒ 改名口径非单射)
  判据副本:
    chk_base.py   ISS-314 原样 (★只读拷贝·项目闸脚本未动★)
    chk_optB.py   乙方案: 解封两行 (NC_ALLOWED + --selftest 目标)
    chk_optC.py   丙方案: 白名单按【位号形状】推导 (前缀匹配)
"""
import csv
import os
import re
import shutil
import sys
import uuid as _uuid

HERE = os.path.dirname(os.path.abspath(__file__))          # logs/iss317/
PROJ = os.path.dirname(os.path.dirname(HERE))              # 项目根
SB = os.path.join(PROJ, "tmp", "iss317_sandbox")
os.makedirs(SB, exist_ok=True)

SRC_NET = os.path.join(PROJ, "HW", "netlist_v1.csv")
SRC_PCB = os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb")
REFLOOKUP = os.path.join(PROJ, "logs", "iss314", "check_pcb_nets_reflookup.py")

PSEUDO = ("RAIL_", "NET_")
EXEMPT_JUSBC = "J_USB_C"

REF_RE = re.compile(r'(\(property "Reference" ")([^"]*)(")')


def kicad_ref(ref):
    """★ISS-205 口径 (与 state/gen_kicad_sch.py::kicad_ref() 同源·逐字复刻★)"""
    r = (ref or "").strip()
    if r and r[-1].isdigit():
        return r
    return r + "_1"


# ════════════════════════════════════════════════════════════════════
# 板副本
# ════════════════════════════════════════════════════════════════════
def _footprint_blocks(txt):
    """把板文本切成 (前缀, [footprint 块], 后缀) ★块边界 = 缩进 1 的 '\t)'★"""
    starts = [m.start() for m in re.finditer(r'\n\t\(footprint "', txt)]
    if not starts:
        return txt, [], ""
    prefix = txt[:starts[0]]
    blocks = []
    for i, s in enumerate(starts):
        end = txt.find("\n\t)\n", s)
        if end < 0:
            raise RuntimeError("footprint 块边界没找到")
        e = end + len("\n\t)\n")
        blocks.append(txt[s:e])
    return prefix, blocks, txt[starts[-1] + len(blocks[-1]):]


def build_board(out_name, exempt=(), overrides=None, dup_ref=None, neg_nc=None):
    """★out_name: 沙盒板文件名
    ★exempt:    豁免改名的 ref 集合 (甲方案)
    ★overrides: {板侧现值ref: 目标ref} (T6 造场)
    ★dup_ref:   要复制成两份的 ref (T5-b)
    ★neg_nc:    (ref, padname) ⇒ 删掉它的 (net ...) 行 (丙方案反向用例)
    """
    overrides = overrides or {}
    src = open(SRC_PCB, encoding="utf-8", errors="replace").read()
    prefix, blocks, suffix = _footprint_blocks(src)
    n_renamed = 0
    out_blocks = []
    for blk in blocks:
        m = REF_RE.search(blk)
        old = m.group(2)
        if old in exempt:
            new = old
        else:
            new = kicad_ref(old)
            if new != old:
                n_renamed += 1
        if old in overrides:
            new = overrides[old]
        blk2 = blk.replace('(property "Reference" "%s"' % old,
                           '(property "Reference" "%s"' % new, 1)
        if neg_nc:
            _ref, _pad = neg_nc
            if old == _ref:
                blk2 = _drop_net(blk2, _pad)
        out_blocks.append(blk2)
    # ── T5-b: 把某个 ref 的封装复制一份 (★uuid 也要换新·否则 pcbnew 可能拒载★) ──
    n_dup = 0
    if dup_ref:
        for blk in out_blocks:
            m = REF_RE.search(blk)
            if m.group(2) == dup_ref:
                blk3 = blk
                for um in re.finditer(r'\(uuid "([0-9a-fA-F-]+)"\)', blk3):
                    blk3 = blk3.replace('(uuid "%s")' % um.group(1),
                                        '(uuid "%s")' % str(_uuid.uuid4()))
                out_blocks.append(blk3)
                n_dup = 1
                break
    out = os.path.join(SB, out_name)
    open(out, "w", encoding="utf-8", errors="replace").write(prefix + "".join(out_blocks) + suffix)
    print("  ★板副本 %-28s 改名 %3d 个 · 复制 %d 份 · → %s"
          % (out_name, n_renamed, n_dup, os.path.relpath(out, PROJ)))
    return out


def _drop_net(blk, padname):
    """把指定焊盘的 (net "X") 行删掉 ⇒ 该焊盘变成 NC 焊盘"""
    pat = re.compile(r'(\(pad "%s" [^\n]*\n(?:\t\t\t[^\n]*\n)*?)\t\t\t\(net "[^"]*"\)\n' % re.escape(padname))
    out, n = pat.subn(r'\1', blk)
    if n == 0:
        print("  ⚠️ 没找到 pad %s 的 (net ...) 行" % padname)
    return out


# ════════════════════════════════════════════════════════════════════
# 网表副本
# ════════════════════════════════════════════════════════════════════
def rename_node(node):
    node = (node or "").strip()
    if not node:
        return node
    m = re.match(r"^([A-Za-z_0-9]+)(\s+.*)?$", node)
    if not m:
        return node
    comp = m.group(1)
    tail = m.group(2) or ""
    if comp.startswith(PSEUDO):
        return node
    if comp == EXEMPT_JUSBC:
        return node
    return kicad_ref(comp) + tail


def build_netlist(out_name, exempt=(), extra_rows=None):
    rows = list(csv.DictReader(open(SRC_NET, encoding="utf-8")))
    flds = list(rows[0].keys())
    out = []
    for r in rows:
        r2 = dict(r)
        ref = (r2.get("ref") or "").strip()
        if ref and not ref.startswith(PSEUDO) and ref not in exempt:
            r2["ref"] = kicad_ref(ref)
        for col in ("node1", "node2"):
            if col in r2:
                r2[col] = rename_node(r2[col]) if ref not in exempt else r2[col]
        out.append(r2)
    if extra_rows:
        out.extend(extra_rows)
    p = os.path.join(SB, out_name)
    with open(p, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=flds)
        w.writeheader()
        for r in out:
            w.writerow(r)
    print("  ★网表副本 %-26s 行数 %d · → %s" % (out_name, len(out), os.path.relpath(p, PROJ)))
    return p


def make_t5a_netlist():
    """T5-a: 表侧同时存在 X 与 X_1 ⇒ kicad_ref(X)=X_1 且 kicad_ref(X_1)=X_1 ⇒ 映射非单射
    ★做法: 全改名网表 + 追加一份 X_1 的行 (★X_1 的行 = X 的行改 ref★)"""
    rows = list(csv.DictReader(open(SRC_NET, encoding="utf-8")))
    flds = list(rows[0].keys())
    X = "C_AC_CSI_D0_CK_N"
    out = []
    extra = []
    for r in rows:
        r2 = dict(r)
        ref = (r2.get("ref") or "").strip()
        if ref == X:
            # 一份走改名 (⇒ X_1), 一份保持 X_1 原样 (⇒ X_1) ⇒ 两份都落到 X_1
            r3 = dict(r)
            r3["ref"] = kicad_ref(X)
            r3["node1"] = rename_node(r3.get("node1"))
            r3["node2"] = rename_node(r3.get("node2"))
            out.append(r3)
            r4 = dict(r)
            r4["ref"] = X + "_1"
            extra.append(r4)
        else:
            if ref and not ref.startswith(PSEUDO):
                r2["ref"] = kicad_ref(ref)
                r2["node1"] = rename_node(r2.get("node1"))
                r2["node2"] = rename_node(r2.get("node2"))
            out.append(r2)
    out.extend(extra)
    p = os.path.join(SB, "netlist_t5a.csv")
    with open(p, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=flds)
        w.writeheader()
        for r in out:
            w.writerow(r)
    print("  ★网表副本 %-26s 行数 %d (★表侧 X=%s 与 X_1=%s_1 共存★) · → %s"
          % ("netlist_t5a.csv", len(out), X, X, os.path.relpath(p, PROJ)))
    return p


# ════════════════════════════════════════════════════════════════════
# 判据副本 (★定点文本替换·可逐行复核★)
# ════════════════════════════════════════════════════════════════════
def patch_check(out_name, patches):
    txt = open(REFLOOKUP, encoding="utf-8").read()
    lines = []
    for old, new in patches:
        if old not in txt:
            raise RuntimeError("★补丁锚点没找到 ⇒ abort★: %r" % old[:70])
        txt = txt.replace(old, new, 1)
        lines.append("      替换: %s" % old.replace("\n", "\\n")[:90])
        lines.append("      成  : %s" % new.replace("\n", "\\n")[:90])
    p = os.path.join(SB, out_name)
    open(p, "w", encoding="utf-8").write(txt)
    print("  ★判据副本 %-22s (%d 处定点替换) · → %s" % (out_name, len(patches), os.path.relpath(p, PROJ)))
    for l in lines:
        print(l)
    return p


if __name__ == "__main__":
    print("=" * 92)
    print("ISS-317 · 沙盒造场 (★只写 tmp/iss317_sandbox/★)")
    print("=" * 92)

    print("\n---- 板副本 ----")
    build_board("board_ref1.kicad_pcb")
    build_board("board_ref1_exJUSBC.kicad_pcb", exempt=(EXEMPT_JUSBC,))
    build_board("board_ref1_negNC.kicad_pcb", neg_nc=("C_BULK_SENSOR_CORE", "1"))
    build_board("board_t5b_dup.kicad_pcb", dup_ref="CHG_GND_STAR_1")
    build_board("board_t6a_x2.kicad_pcb", overrides={"CHG_GND_STAR_1": "CHG_GND_STAR_2"})
    build_board("board_t6b_xz1.kicad_pcb", overrides={"CHG_GND_STAR_1": "CHG_GND_STAR_Z_1"})

    print("\n---- 网表副本 ----")
    build_netlist("netlist_ref1.csv")
    build_netlist("netlist_ref1_exJUSBC.csv", exempt=(EXEMPT_JUSBC,))
    make_t5a_netlist()

    print("\n---- 判据副本 ----")
    shutil.copy2(REFLOOKUP, os.path.join(SB, "chk_base.py"))
    print("  ★判据副本 chk_base.py            (★ISS-314 原样拷贝·项目闸脚本未动★)")

    patch_check("chk_optB.py", [
        ('    NC_ALLOWED.add("J_USB_C")',
         '    NC_ALLOWED.add("J_USB_C_1")   # ★ISS-317 乙方案: 白名单跟着改名走★'),
        ('fp.GetReference() == "CONN_CAM"',
         'fp.GetReference() == "CONN_CAM_1"  # ★ISS-317 乙方案: --selftest 目标跟着改名走★'),
    ])

    patch_check("chk_optC.py", [
        ('    NC_ALLOWED.add("J_USB_C")',
         '    # ★ISS-317 丙方案: 白名单按【位号形状】推导 (★前缀匹配·改名后自动跟着走★)\n'
         '    NC_ALLOWED_PREFIX = ("J_USB_C",)\n'
         '\n'
         '    def _nc_allowed(ref):\n'
         '        """★形状推导: 精确命中 或 前缀命中 (★J_USB_C ⇒ J_USB_C_1 自动跟随★)"""\n'
         '        return ref in NC_ALLOWED or any(ref.startswith(p) for p in NC_ALLOWED_PREFIX)'),
        ('    bad_nc = sorted(k for k in nc_pads if k[0] not in NC_ALLOWED)',
         '    bad_nc = sorted(k for k in nc_pads if not _nc_allowed(k[0]))'),
        ('        return ref in NC_ALLOWED',
         '        return _nc_allowed(ref)'),
    ])

    print("\n★沙盒造场完成 · 只写 tmp/iss317_sandbox/")
