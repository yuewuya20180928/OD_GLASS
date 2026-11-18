#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sb05_make_patched_check.py —— ISS-314 沙盒: 生成两版【副本版判据】

  A) check_pcb_nets_sandbox.py    = 项目正本 + 【--net 切换网表】 (★不含反查层★)
  B) check_pcb_nets_reflookup.py  = 项目正本 + 【--net 切换网表】 + 【ISS-314 反查层】

★只写沙盒目录 (tmp/iss314_sandbox/) ⇒ 项目脚本 state/check_pcb_nets.py 一个字节不许动 ★
★做法: 对原文做【定点文本替换】⇒ diff 可逐行复核 (★不是重写, 是最小补丁★)
"""
import hashlib
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(PROJ, "state", "check_pcb_nets.py")

BASE = os.path.join(HERE, "check_pcb_nets_sandbox.py")
DST = os.path.join(HERE, "check_pcb_nets_reflookup.py")

src = open(SRC, encoding="utf-8").read()

# ---------------------------------------------------------------- 通用补丁 A: 沙盒路径
OLD_A = """HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
"""
NEW_A = """HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
# ★ISS-314 沙盒: 副本放在 tmp/ 下 ⇒ PROJ 会被算到 tmp/ ⇒ 这里【指回项目根】(★只读网表★)
if not os.path.exists(os.path.join(PROJ, "HW", "netlist_v1.csv")):
    PROJ = os.path.dirname(os.path.dirname(HERE))
"""
assert OLD_A in src, "补丁A 锚点没命中"
src = src.replace(OLD_A, NEW_A)

# ---------------------------------------------------------------- 通用补丁 B: --net 切换网表
OLD_B = '''    _args = [a for a in sys.argv[1:] if not a.startswith("--")]
'''
NEW_B = '''    _args = [a for a in sys.argv[1:] if not a.startswith("--")]
    # ★ISS-314 沙盒: --net=<path> ⇒ 换网表 (★只读★)
    for a in sys.argv[1:]:
        if a.startswith("--net="):
            globals()["NET"] = os.path.abspath(a[6:])
            print("  (沙盒换网表: %s)" % globals()["NET"])
'''
assert OLD_B in src, "补丁B 锚点没命中"
src = src.replace(OLD_B, NEW_B)

open(BASE, "w", encoding="utf-8").write(src)
print("★已生成沙盒判据 (无反查层): %s" % BASE)

# ================================================================ 反查层版
src2 = src

OLD1 = '''def board_pads(path):
    """板 → {(ref, 焊盘号): 网络} + {ref: [焊盘号...]}"""
    b = pcbnew.LoadBoard(path)
    if b is None:
        return None, None
    pairs, per_ref = {}, {}
    for fp in list(b.GetFootprints()):
        ref = fp.GetReference()
        for pad in list(fp.Pads()):
            num = str(pad.GetNumber())
            pairs[(ref, num)] = pad.GetNetname()
            per_ref.setdefault(ref, []).append(num)
    return pairs, per_ref
'''

NEW1 = '''def build_ref_map(board_refs, table_refs):
    """★ISS-314 反查层: 板侧 ref → 表侧 ref 的【单向】反查映射 (★板 → 表★)

    ★规则 (★与 ISS-205 改名规则严格对称★): 板侧 ref 以 `_1` 结尾 且 去掉 `_1` 后
      在【网表 ref 全集】里【确实存在】⇒ 反查为那个表侧 ref
    ★fail-closed 三条:
      ① 反查只认"去掉 `_1` 后网表里确实存在同名器件" ⇒ 真·多余器件洗不掉 (⇒ 仍判红)
      ② 歧义 (两个板侧 ref 指向同一表侧 ref) ⇒ 映射记 None ⇒ 判红, 不猜
      ③ 反查只改 ref 键, 不改网络 ⇒ 脚位对调 (同号异网) 照样红
    ★返回 (映射 dict, 歧义 list, 未命中 list)
    """
    m, ambig, miss = {}, [], []
    for r in board_refs:
        if not r or r in table_refs:
            continue                       # ★同名 ⇒ 无需反查 (含原生 R_BAT_DET_1)
        if r.endswith("_1"):
            base = r[:-2]
            if base in table_refs:
                if base in m.values():
                    m[r] = None
                    ambig.append((r, base))
                else:
                    m[r] = base
            else:
                miss.append(r)
    return m, ambig, miss


def board_pads(path, table_refs=None):
    """板 → {(ref, 焊盘号): 网络} + {ref: [焊盘号...]} (+ 反查映射)"""
    b = pcbnew.LoadBoard(path)
    if b is None:
        return None, None, {}
    all_refs = [fp.GetReference() for fp in list(b.GetFootprints())]
    rmap, ambig, miss = build_ref_map(all_refs, table_refs or set())
    pairs, per_ref = {}, {}
    for fp in list(b.GetFootprints()):
        ref = fp.GetReference()
        if ref in rmap and rmap[ref] is not None:
            ref = rmap[ref]                 # ★反查: 板侧 X_1 ⇒ 表侧 X
        for pad in list(fp.Pads()):
            num = str(pad.GetNumber())
            pairs[(ref, num)] = pad.GetNetname()
            per_ref.setdefault(ref, []).append(num)
    return pairs, per_ref, rmap
'''
assert OLD1 in src2, "补丁1 锚点没命中"
src2 = src2.replace(OLD1, NEW1)

OLD2 = """    per_ref, numbered, placeholder, notes = netlist_pads(rows)
    have, board_refs = board_pads(path)
    if have is None:
        return 1, ["❌ 板文件读不回来: %s" % path], {}
"""
NEW2 = """    per_ref, numbered, placeholder, notes = netlist_pads(rows)
    # ★ISS-314 反查层: 表侧 ref 全集 (网表 ref 列 ∪ 网表推出的器件)
    table_refs = set(per_ref.keys())
    for r in rows:
        rr = (r.get("ref") or "").strip()
        if rr:
            table_refs.add(rr)
    have, board_refs, rmap = board_pads(path, table_refs=table_refs)
    if have is None:
        return 1, ["❌ 板文件读不回来: %s" % path], {}
    _b_all = [fp.GetReference() for fp in list(pcbnew.LoadBoard(path).GetFootprints())]
    _amb = [(k, v) for k, v in rmap.items() if v is None]
    _miss = [r for r in _b_all if r not in table_refs and r not in rmap]
"""
assert OLD2 in src2, "补丁2 锚点没命中"
src2 = src2.replace(OLD2, NEW2)

OLD3 = """    body = c1 + c2 + c3 + c4 + c5
    return (0 if not fails else 1), body, {"want": want, "have": have, "fails": fails}
"""
NEW3 = """    # ---- ★ISS-314 反查层口径报告 (★只报告, 不改判据方向★) ----
    cal = []
    if rmap:
        cal.append("  ℹ️ ★口径: 反查层命中 %d 个板上位号 (板侧 X_1 ⇒ 表侧 X) ⇒ "
                   "【板侧位号与网表 ref 不同名】这件事【仍然成立】★" % len(rmap))
        for k in sorted(rmap)[:8]:
            cal.append("       · %s ⇒ %s" % (k, rmap[k]))
        if len(rmap) > 8:
            cal.append("       · …共 %d 个" % len(rmap))
        cal.append("       ★⇒ 这不是'板坏了', 是【图上位号口径 与 表侧 ref 口径没同步】★")
        cal.append("       ★⇒ 作业包 §3-S1 (板侧加 _1) 与 §5 (网表逐字节不变) 【自相矛盾】★")
    if _amb:
        cal.append("  ❌ ★口径歧义: %d 个板上位号反查后指向同一表侧 ref ⇒ 判红★" % len(_amb))
        for k, v in _amb[:8]:
            cal.append("       ★ %s ⇒ %s" % (k, v))
    if _miss:
        cal.append("  ❌ ★口径未同步: %d 个板上位号在网表里找不到 (且反查不命中) ⇒ "
                   "它们是【真·多余器件】, 判红★" % len(_miss))
        for k in _miss[:8]:
            cal.append("       ★ %s" % k)

    body = c1 + c2 + c3 + c4 + c5 + cal
    return (0 if not fails else 1), body, {"want": want, "have": have, "fails": fails}
"""
assert OLD3 in src2, "补丁3 锚点没命中"
src2 = src2.replace(OLD3, NEW3)

OLD4 = '''退出码: 全过 0; 否则 1
'''
NEW4 = '''退出码: 全过 0; 否则 1

★★ ISS-314 反查层 (★沙盒副本版 · ★项目正本未改★):
   ★板侧位号改名 (X → X_1) 而网表不改名 ⇒ C1 会从「缺失 0 / 多余 2 / 同号异网 3」
     变成「缺失 350 / 多余 352 / 同号异网 0」⇒ 本副本加【单向反查层 (板 → 表)】
     把板侧 ref 归一到表侧 ref ⇒ C1 回到原读数
   ★★ 但反查层【只归一 ref 键, 不改判据方向, 不豁免任何一项】⇒ 同号异网照样红 ★★
'''
assert OLD4 in src2, "补丁4 锚点没命中"
src2 = src2.replace(OLD4, NEW4, 1)

open(DST, "w", encoding="utf-8").write(src2)

print("★已生成沙盒判据 (带反查层): %s" % DST)
for tag, p in (("正本", SRC), ("沙盒无反查", BASE), ("沙盒带反查", DST)):
    print("★ md5 %-10s %s  %s" % (tag, hashlib.md5(open(p, "rb").read()).hexdigest(), p))
