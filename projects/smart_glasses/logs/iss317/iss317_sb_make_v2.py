#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iss317_sb_make_v2.py —— ISS-317 · 沙盒造场 v2 (★只写 tmp/iss317_sandbox/★)

★**项目板 / 网表 / 脚表 / BOM / 受保护闸脚本一个字节不许动** ★
★判据脚本 = ISS-314 留档的沙盒副本 `logs/iss314/check_pcb_nets_reflookup.py` (★只读取·拷进沙盒跑★)

★★★ v1 (iss317_sb_make.py) 的三个缺陷 · 本版修掉 ★★★
  缺陷 ① ★网表改名是【按行】做的★ (★ref 列按行判豁免·node 串整串不判★)
        ⇒ 甲方案里「ref=J_USB_C 的那行」它的 node2="R_CC1_D" 没被改名 ⇒
          表侧宇宙里 R_CC1_D 消失 ⇒ R_CC1_D_1 只剩 1 个脚 ⇒ 假 delta
        ⇒ 【修法】改名按【token】做: ★node 串里的每个器件名单独判豁免★
  缺陷 ② ★node 串里的裸网名也被改名★ (★GND ⇒ GND_1★)
        ⇒ 【修法】只有【真·器件宇宙 U】里的 token 才改名 (★裸网名不在 U ⇒ 不动★)
  缺陷 ③ ★J_USB_C 在 rename_node 里被硬编死豁免★ ⇒ 连「全改名」场里 node 串的
        J_USB_C 也没改名 ⇒ A0 场污染 (★缺失4/多余16 里有 14 条是假的★)
        ⇒ 【修法】豁免集合由参数传入, 没有任何硬编★

★★ 另加: 沙盒副本统一支持 `--pcb=<path>` (★原脚本只支持 --net=★)
   ⇒ 才能对【改名后的板】跑 `--selftest` (★否则 selftest 永远查官方板★)
   ⇒ 以及 selftest 的临时板写到沙盒目录 (★不写 /tmp★)
   ★★ 该改动只发生在【沙盒副本】(tmp/iss317_sandbox/chk_*.py) ⇒ ★**项目闸脚本 state/check_pcb_nets.py 一个字节没动** ★★

─── 判据副本矩阵 ────────────────────────────────────────────────────
  chk_base.py   ISS-314 原样 + 沙盒 harness (--pcb= / selftest 落沙盒)
  chk_optB.py   乙方案: 解封两行 (NC_ALLOWED.add("J_USB_C_1") + --selftest 目标 CONN_CAM_1)
  chk_optC1.py  丙方案-①(裸前缀): 白名单按 startswith("J_USB_C") 推导   ★★放宽真错★
  chk_optC2.py  丙方案-②(正则锚定): 白名单按 ^J_USB_C(_\d+)?$ 推导     ★★不放宽★
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
PIN_RE = re.compile(r'pin\d+(\+pin\d+)*')


def kicad_ref(ref):
    """★ISS-205 口径 (与 state/gen_kicad_sch.py::kicad_ref() 同源·逐字复刻★)"""
    r = (ref or "").strip()
    if r and r[-1].isdigit():
        return r
    return r + "_1"


def split_node(node):
    node = (node or "").strip()
    if not node:
        return None, None
    m = re.match(r"^([A-Za-z_0-9]+)\s+(.*)$", node)
    if not m:
        return node, None
    return m.group(1), m.group(2).strip()


# ════════════════════════════════════════════════════════════════════
# ★真·器件宇宙 U (★只算一次·从【原始】网表取★)
#   U = ref 列真实器件 ∪ 节点串里带编号脚 (pinN) 的器件
#   ★只有 U 里的 token 才是【器件】⇒ 改名只改 U 里的 token⇒ 裸网名 (GND 等) 不动★
# ════════════════════════════════════════════════════════════════════
def device_universe(rows):
    refs = set()
    for r in rows:
        ref = (r.get("ref") or "").strip()
        if ref:
            refs.add(ref)
    real = {x for x in refs if not x.startswith(PSEUDO)}
    extra = set()
    for r in rows:
        for k in ("node1", "node2"):
            comp, tail = split_node(r.get(k))
            if not comp or comp in real or comp.startswith(PSEUDO):
                continue
            if tail and PIN_RE.fullmatch(tail):
                extra.add(comp)
    return real | extra


# ════════════════════════════════════════════════════════════════════
# 板副本
# ════════════════════════════════════════════════════════════════════
def _footprint_blocks(txt):
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
    ★overrides: {板侧现值ref: 目标ref} (T6 造场 / A6 造场)
    ★dup_ref:   要复制成两份的 ref (T5-b 映射歧义)
    ★neg_nc:    (ref, padname) ⇒ 删掉它的 (net ...) 行 ⇒ 该焊盘变 NC
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
    n_dup = 0
    if dup_ref:
        for blk in list(out_blocks):
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
    print("  ★板副本 %-30s 改名 %3d 个 · 复制 %d 份 · → %s"
          % (out_name, n_renamed, n_dup, os.path.relpath(out, PROJ)))
    return out


def _drop_net(blk, padname):
    pat = re.compile(r'(\(pad "%s" [^\n]*\n(?:\t\t\t[^\n]*\n)*?)\t\t\t\(net "[^"]*"\)\n' % re.escape(padname))
    out, n = pat.subn(r'\1', blk)
    if n == 0:
        print("  ⚠️ 没找到 pad %s 的 (net ...) 行" % padname)
    return out


# ════════════════════════════════════════════════════════════════════
# 网表副本 (★v2: 按 token 改名★)
# ════════════════════════════════════════════════════════════════════
def rename_node(node, exempt, universe):
    """★node 串 → 改名后的 node 串
    ★只有【器件宇宙 U】里的 token 才改名 ⇒ 裸网名 (GND / USB_CC1 等) 一个字节不动★
    ★豁免按【token】判 (★不按行判★) ⇒ 甲方案里 J_USB_C 相关的每一处都保持 J_USB_C★"""
    node = (node or "").strip()
    if not node:
        return node
    m = re.match(r"^([A-Za-z_0-9]+)(\s+.*)?$", node)
    if not m:
        return node
    comp, tail = m.group(1), m.group(2) or ""
    if comp not in universe:
        return node                       # ★裸网名 ⇒ 不动★
    if comp in exempt:
        return node                       # ★豁免 ⇒ 不动★
    return kicad_ref(comp) + tail


def build_netlist(out_name, exempt=(), universe=None, extra_rows=None, overrides=None):
    """★overrides: {原ref: 目标ref} (★A6 造场: 把器件改名成 J_USB_C_X★)"""
    overrides = overrides or {}
    rows = list(csv.DictReader(open(SRC_NET, encoding="utf-8")))
    flds = list(rows[0].keys())
    U = universe if universe is not None else device_universe(rows)
    out = []
    n_ref = 0
    for r in rows:
        r2 = dict(r)
        ref = (r2.get("ref") or "").strip()
        if ref and ref in U and ref not in exempt:
            newref = kicad_ref(ref)
            if newref != ref:
                n_ref += 1
            r2["ref"] = newref
        if ref in overrides:
            r2["ref"] = overrides[ref]
        for col in ("node1", "node2"):
            if col in r2:
                r2[col] = rename_node(r2[col], exempt, U)
                if ref in overrides:
                    # ★node 串里若指的就是这个器件 ⇒ 同步换成 override 后的名字★
                    _c, _t = split_node(r2[col])
                    if _c == kicad_ref(ref) or _c == ref:
                        _tail = r2[col][len(_c):]
                        r2[col] = overrides[ref] + _tail
        out.append(r2)
    if extra_rows:
        out.extend(extra_rows)
    p = os.path.join(SB, out_name)
    with open(p, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=flds)
        w.writeheader()
        for r in out:
            w.writerow(r)
    print("  ★网表副本 %-30s 行数 %d (★ref 列改名 %d 个★) · → %s"
          % (out_name, len(out), n_ref, os.path.relpath(p, PROJ)))
    return p


# ════════════════════════════════════════════════════════════════════
# 判据副本 (★定点文本替换·可逐行复核★)
# ════════════════════════════════════════════════════════════════════
HARNESS = [
    # ★★ 沙盒 harness ①: 把原 --net= 解析块【静音】(★它的语义被上移到 selftest 之前★)
    ('    # ★ISS-314 沙盒: --net=<path> ⇒ 换网表 (★只读★)\n'
     '    for a in sys.argv[1:]:\n'
     '        if a.startswith("--net="):\n'
     '            globals()["NET"] = os.path.abspath(a[6:])\n'
     '            print("  (沙盒换网表: %s)" % globals()["NET"])',
     '    # ★ISS-317 沙盒 harness: --net=/--pcb= 的解析已【上移到 selftest 分支之前】(★见上★)'),
    # ★★ 沙盒 harness ②: 在 selftest 分支【之前】插入 --net=/--pcb= 解析
    #    (★原脚本只在 selftest 分支【之后】解析 ⇒ --selftest 永远查官方板★)
    ('    selftest = "--selftest" in sys.argv',
     '    # ★ISS-317 沙盒 harness: --net=/--pcb= 先解析 (★这样 --selftest 也能换板/换网表★)\n'
     '    for a in sys.argv[1:]:\n'
     '        if a.startswith("--net="):\n'
     '            globals()["NET"] = os.path.abspath(a[6:])\n'
     '            print("  (沙盒换网表: %s)" % globals()["NET"])\n'
     '        if a.startswith("--pcb="):\n'
     '            globals()["PCB"] = os.path.abspath(a[6:])\n'
     '            print("  (沙盒换板: %s)" % globals()["PCB"])\n'
     '    selftest = "--selftest" in sys.argv'),
    # ★★ selftest 的临时板写到沙盒目录 (★不写 /tmp★) ★★
    ('    tmp = "/tmp/_pcb_swap_test.kicad_pcb"',
     '    tmp = os.path.join(os.path.dirname(os.path.abspath(__file__)),\n'
     '                        "_selftest_swap_%s.kicad_pcb" % os.getpid())'),
]


def patch_check(out_name, extra=()):
    txt = open(REFLOOKUP, encoding="utf-8").read()
    log = []
    for old, new in list(HARNESS) + list(extra):
        if old not in txt:
            raise RuntimeError("★补丁锚点没找到 ⇒ abort★: %r" % old[:70])
        txt = txt.replace(old, new, 1)
        log.append("      替换: %s" % old.replace("\n", "\\n")[:92])
        log.append("      成  : %s" % new.replace("\n", "\\n")[:92])
    p = os.path.join(SB, out_name)
    open(p, "w", encoding="utf-8").write(txt)
    print("  ★判据副本 %-24s (%d 处定点替换) · → %s"
          % (out_name, len(HARNESS) + len(extra), os.path.relpath(p, PROJ)))
    for l in log:
        print(l)
    return p


if __name__ == "__main__":
    print("=" * 96)
    print("ISS-317 · 沙盒造场 v2 (★只写 tmp/iss317_sandbox/★ · v1 三个缺陷已修★)")
    print("=" * 96)

    _rows = list(csv.DictReader(open(SRC_NET, encoding="utf-8")))
    U = device_universe(_rows)
    print("\n---- 口径 ----")
    print("  ★真·器件宇宙 U (★只有 U 里的 token 才改名★) : %d 个" % len(U))
    print("  ★裸网名判定样例: 'GND' 在 U 里吗 ⇒ %s" % ("GND" in U))

    print("\n---- 板副本 ----")
    build_board("board_ref1.kicad_pcb")
    build_board("board_ref1_exJUSBC.kicad_pcb", exempt=(EXEMPT_JUSBC,))
    build_board("board_ref1_negNC.kicad_pcb", neg_nc=("C_BULK_SENSOR_CORE", "1"))
    # ★★ A6: 把一个【非白名单】器件改名叫 J_USB_C_X (★裸前缀白名单会放过它★) + 造 NC 焊盘
    build_board("board_ref1_prefixtrap.kicad_pcb",
                overrides={"C_BULK_SENSOR_CORE": "J_USB_C_X"}, neg_nc=("C_BULK_SENSOR_CORE", "1"))
    build_board("board_t5b_dup.kicad_pcb", dup_ref="CHG_GND_STAR_1")
    build_board("board_t6a_x2.kicad_pcb", overrides={"CHG_GND_STAR_1": "CHG_GND_STAR_2"})
    build_board("board_t6b_xz1.kicad_pcb", overrides={"CHG_GND_STAR_1": "CHG_GND_STAR_Z_1"})

    print("\n---- 网表副本 (★v2: 按 token 改名★) ----")
    build_netlist("netlist_ref1.csv", universe=U)
    build_netlist("netlist_ref1_exJUSBC.csv", exempt=(EXEMPT_JUSBC,), universe=U)
    # ★★ A6 的配套网表: C_BULK_SENSOR_CORE ⇒ J_USB_C_X (★两侧同口径★)
    build_netlist("netlist_ref1_prefixtrap.csv", universe=U,
                  overrides={"C_BULK_SENSOR_CORE": "J_USB_C_X"})

    print("\n---- 判据副本 ----")
    patch_check("chk_base.py")

    patch_check("chk_optB.py", extra=[
        ('    NC_ALLOWED.add("J_USB_C")',
         '    NC_ALLOWED.add("J_USB_C_1")   # ★ISS-317 乙方案: 白名单跟着改名走★'),
        ('        if len(pads) >= 2 and fp.GetReference() == "CONN_CAM":',
         '        if len(pads) >= 2 and fp.GetReference() == "CONN_CAM_1":'
         '  # ★ISS-317 乙方案: --selftest 目标跟着改名走★'),
    ])

    patch_check("chk_optC1.py", extra=[
        ('    NC_ALLOWED.add("J_USB_C")',
         '    NC_ALLOWED_PREFIX = ("J_USB_C",)   # ★ISS-317 丙方案-①: 裸前缀匹配★\n'
         '\n'
         '    def _nc_allowed(ref):\n'
         '        """★丙方案-①: 裸前缀 (★J_USB_C ⇒ J_USB_C_1 自动跟随·★但也放过 J_USB_C_X★)"""\n'
         '        return (ref in NC_ALLOWED) or any(ref.startswith(p) for p in NC_ALLOWED_PREFIX)'),
        ('    bad_nc = sorted(k for k in nc_pads if k[0] not in NC_ALLOWED)',
         '    bad_nc = sorted(k for k in nc_pads if not _nc_allowed(k[0]))'),
        ('    def _nc_ok(ref):\n'
         '        """该器件的 NC 脚是否都是允许的 (USB-C 屏蔽/A8/B8)"""\n'
         '        return ref in NC_ALLOWED',
         '    def _nc_ok(ref):\n'
         '        """该器件的 NC 脚是否都是允许的 (USB-C 屏蔽/A8/B8)"""\n'
         '        return _nc_allowed(ref)'),
    ])

    patch_check("chk_optC2.py", extra=[
        ('    NC_ALLOWED.add("J_USB_C")',
         '    NC_ALLOWED_RE = re.compile(r"^J_USB_C(_\\d+)?$")   # ★ISS-317 丙方案-②: 正则锚定★\n'
         '\n'
         '    def _nc_allowed(ref):\n'
         '        """★丙方案-②: 正则锚定 (★只有 J_USB_C / J_USB_C_1 命中·★J_USB_C_X 不命中★)"""\n'
         '        return (ref in NC_ALLOWED) or bool(NC_ALLOWED_RE.match(ref))'),
        ('    bad_nc = sorted(k for k in nc_pads if k[0] not in NC_ALLOWED)',
         '    bad_nc = sorted(k for k in nc_pads if not _nc_allowed(k[0]))'),
        ('    def _nc_ok(ref):\n'
         '        """该器件的 NC 脚是否都是允许的 (USB-C 屏蔽/A8/B8)"""\n'
         '        return ref in NC_ALLOWED',
         '    def _nc_ok(ref):\n'
         '        """该器件的 NC 脚是否都是允许的 (USB-C 屏蔽/A8/B8)"""\n'
         '        return _nc_allowed(ref)'),
    ])

    print("\n★沙盒造场完成 (v2) · 只写 tmp/iss317_sandbox/")
