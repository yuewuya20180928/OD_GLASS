#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iss317_sb_make_t5t6.py —— ISS-317 · U-1 补跑: T5 (映射歧义) / T6 (板侧 ref 改成表侧没有的名字)

★**只写 tmp/iss317_sandbox/** ★ ⇒ ★**项目板/网表/脚表/BOM/闸脚本一个字节不许动** ★
★判据脚本 = ISS-314 留档的沙盒副本 `logs/iss314/check_pcb_nets_reflookup.py` (★只读取·拷进沙盒跑★)

★T5 造法 (★ISS-314 §3-6 逐字设计★):
    造法: 在沙盒网表里放两个表侧 ref X 与 X_1 (⇒ kicad_ref(X)=X_1, kicad_ref(X_1)=X_1 ⇒ 映射非单射)
    期望: ③ 红, 文案「★口径歧义: …」或「★单射校验失败 …」⇒ ★不许静默丢掉一个器件★
  ★本单的实测实现方式 (★不新建器件·避免污染 C1★):
    把沙盒网表里某个【本来就叫 X_1 的 ref】改成一个【会撞名的】名字, 让板侧两个不同 ref
    反查到同一个表侧 ref ⇒ 触发 build_ref_map() 的歧义分支 (base in m.values())
    ⇒ 具体: 板侧 `R_BAT_DET_1` (原生 _1, 不动) 与 `R_BAT_DET_2` (不动) —— ★这俩本来就不动★
    ⇒ 换一组: 板侧 `X_1` (改名来的) 与表侧 `X` —— 若表侧同时存在 `X` 与 `X_1` 两个器件
    ⇒ 做法: 在沙盒网表里把某个 ref 改成另一个 ref + "_1" ⇒ 制造 (X, X_1) 共存

★T6 造法 (★ISS-314 §3-6 逐字设计★):
    造法: 沙盒板副本里把某个封装的 ref 改成 <原名>_2 (⇒ 去掉 _1 也不命中, 也不以 _1 结尾 ⇒ 反查不命中)
    期望: ③ 红, 文案「★口径未同步: 1 个板上位号在网表里找不到」⇒ ★不许当成「反查漏了」而放过★
"""
import csv
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))          # logs/iss317/
PROJ = os.path.dirname(os.path.dirname(HERE))              # 项目根
SB = os.path.join(PROJ, "tmp", "iss317_sandbox")
os.makedirs(SB, exist_ok=True)

SRC_NET = os.path.join(PROJ, "HW", "netlist_v1.csv")
SRC_PCB = os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb")
REFLOOKUP = os.path.join(PROJ, "logs", "iss314", "check_pcb_nets_reflookup.py")


def kicad_ref(ref):
    r = (ref or "").strip()
    if r and r[-1].isdigit():
        return r
    return r + "_1"


def rename_node(node):
    node = (node or "").strip()
    if not node:
        return node
    m = re.match(r"^([A-Za-z_0-9]+)(\s+.*)?$", node)
    if not m:
        return node
    comp = m.group(1)
    tail = m.group(2) or ""
    if comp.startswith(("RAIL_", "NET_")):
        return node
    return kicad_ref(comp) + tail


def load_rows(p):
    rows = list(csv.DictReader(open(p, encoding="utf-8")))
    return rows, list(rows[0].keys())


def write_rows(rows, flds, out):
    with open(out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=flds)
        w.writeheader()
        for r in rows:
            w.writerow(r)


# ════════════════════════════════════════════════════════════════════
# 基础: 三侧同口径改名版板 + 网表 (= ISS-314 的 S4/S5 场景, 作为 T5/T6 的底座)
# ════════════════════════════════════════════════════════════════════
def make_base():
    rows, flds = load_rows(SRC_NET)
    out = os.path.join(SB, "netlist_ref1.csv")
    o = []
    for r in rows:
        r2 = dict(r)
        r2["ref"] = kicad_ref(r.get("ref"))
        r2["node1"] = rename_node(r.get("node1"))
        r2["node2"] = rename_node(r.get("node2"))
        o.append(r2)
    write_rows(o, flds, out)
    print("★底座网表 (三侧同口径改名): %s" % out)
    return out


def make_base_board():
    """★板副本: 给末字符是字母的 ref 加 _1 (★只用文本改, 不 import pcbnew·不碰项目板★)"""
    src = open(SRC_PCB, encoding="utf-8", errors="replace").read()
    rx = re.compile(r'(\(property "Reference" ")([^"]*)(")')
    seen = {}

    def rep(m):
        ref = m.group(2)
        if not ref:
            return m.group(0)
        new = kicad_ref(ref)
        if new != ref:
            seen[ref] = new
        return m.group(1) + new + m.group(3)

    out_txt = rx.sub(rep, src)
    out = os.path.join(SB, "board_ref1.kicad_pcb")
    open(out, "w", encoding="utf-8", errors="replace").write(out_txt)
    print("★底座板副本 (改名 %d 个): %s" % (len(seen), out))
    return out, seen


# ════════════════════════════════════════════════════════════════════
# T5: 制造 (X, X_1) 共存 ⇒ 映射非单射 ⇒ 期望「口径歧义」红
# ════════════════════════════════════════════════════════════════════
def make_t5(base_net):
    """
    ★手法 (★最小污染★):
      选一个板侧【改名来的】ref A (= 表侧 a ⇒ 板侧 a_1)
      再把网表里另一个【表侧本来叫 b】的 ref 改成 `a` (⇒ 表侧就同时有 a 和 a_1 两个器件)
      ⇒ 板侧 a_1 反查 ⇒ base='a' 命中表侧 ⇒ 但若板侧另有一个 ref 也反查到 'a' ⇒ 歧义
    ★更直接的实现 (★用板侧两个 ref★):
      板侧 a_1 (来自表侧 a) 与板侧 b_1 (来自表侧 b)
      把表侧 b 改名成 a ⇒ 表侧 = {a, a_1}
      ⇒ 板侧 a_1: base='a' 命中 ⇒ 映射到 'a' (OK)
      ⇒ 板侧 b_1: base='b' 不在表侧 ⇒ miss (未同步) —— 这是 T6 型, 不是 T5
    ★★所以 T5 的正确造法 = 让【两个板侧 ref】都反查到【同一个表侧 ref】★★
      ⇒ 需要板侧同时存在 `a_1` 和 `a` (两个 ref)
      ⇒ 办法: 沙盒板副本里【手工加一个 ref=a 的封装副本】(★只加, 不删·只动沙盒★)
      ⇒ 板侧 {a_1, a}: a_1 → base 'a' 命中表侧 'a'; a 本身在表侧 ⇒ 跳过 (同名不反查)
      ⇒ ★这样也不产生歧义★ ⇒ 因为 build_ref_map 只对【表侧没有的名字】做反查
      ⇒ ★★真正的歧义造法 (★ISS-314 原文: 表侧同时存在 X 与 X_1★★):
         表侧 = {X, X_1} ⇒ kicad_ref(X)=X_1 与 kicad_ref(X_1)=X_1 ⇒ 两个表侧 ref 映到同一个图上位号
         ⇒ 板侧有 X_1 (一个封装) ⇒ 反查 X_1 → base 'X' 命中表侧 'X' ⇒ 映射 X_1 → X
         ⇒ ★此时表侧的 X_1 器件在板侧【没有对应封装】⇒ C1 报「缺失」⇒ 这就是歧义的危害
         ⇒ 但 build_ref_map 的歧义分支 (base in m.values()) 只有在【两个板侧 ref】都映射到同一 base 时才触发
      ⇒★★最终采用 (★能真正触发歧义分支★): 板侧【同一个 base 的两个形态】★★
         板侧同时有 `a_1` 和 `a_1_1`? — 不行, a_1_1 的 base 是 'a_1'
         ★⇒ 板侧同时有 `a_1` 和 `a`★ ⇒ 但 a 在表侧 ⇒ 跳过反查 ⇒ 不触发歧义
      ⇒★★那就【把表侧的 a 改名掉】★★: 表侧 = {a_1, ...} (没有 a)
         板侧 = {a_1, a} ⇒ 两个都不在表侧 (a_1 不在表侧, a 不在表侧)
         ⇒ a_1: base='a' ⇒ 'a' 在表侧? 否 ⇒ miss
         ⇒ 不行
      ⇒★★正解 (★读源码确认★): 需要 base 相同 ★且★ base 在表侧
         板侧 {a_1, a_1}? — 同名封装不会重复
         板侧 {X_1, X_1}?
         ⇒ ★★唯一的自然触发: 两个【不同的板侧 ref】去掉 _1 后【同名】★★
            即板侧 {a_1, a_1} 不可能 ⇒ 但 {a_1, a_1}…
         ⇒ ★★换个角度: 板侧 ref = `a_1` 和 `a` —— 若表侧【没有】a, 则:
            a_1 → base 'a' 不在表侧 ⇒ miss (未同步)
            a  → 不以 _1 结尾 ⇒ 不反查 ⇒ 【也不在表侧 ⇒ 也不判歧义, 只是 C1 多余】
         ⇒ ★★结论: build_ref_map 的歧义分支需要【表侧有 base】且【两个板侧 ref 的 base 相同】★★
            ⇒ 只有当板侧同时存在 `X_1` 与 `X` (去掉 _1 后同 base) 且【表侧没有 X】时才走 miss
            ⇒ ★★所以真正的歧义造法 = 表侧同时存在 X 和 X_1 (ISS-314 原文)★★
               此时板侧: X_1 (改名来的) ⇒ base='X' 命中 ⇒ 映射到 'X'
                          ★表侧的 X_1 器件 ⇒ 板侧没有 ⇒ C1 「缺失」⇒ ★这就是「静默丢掉一个器件」★
               ⇒ ★★而 build_ref_map 的 ambig 分支, 触发条件是【两个板侧 ref 映射到同一 base】★★
                  ⇒ 板侧要有两个 ref 都能反查到 'X' ⇒ 例如板侧有 `X_1` 和 `X_1`(重复) 不可能
                  ⇒ ★★除非板侧同时有 `X_1` 和 `X` 且表侧【没有】X ⇒ 那就是 miss 不是 ambig
               ⇒ ★★★所以我按【ISS-314 原文的 T5 造法】实测: 表侧放 X 与 X_1 共存★★★
                  并【额外】在板侧加一个 `X` 的封装副本 ⇒ 让两个板侧 ref (X_1 / X) 都反查到 'X'?
                  —— 不行, 'X' 同名在表侧 ⇒ 跳过
               ⇒ ★★★最终: 用【表侧 X 与 X_1 共存】+ 板侧【把 X_1 的封装改成 X_2】? ⇒ 那是 T6
    ★★★⇒ 所以我把 T5 拆成【两个可实测的子场景】, 各自报读数 (★不硬凑★) ★★★
        T5a: 表侧造 (X, X_1) 共存 ⇒ 观测 C1 是否报「缺失」(★= 静默丢掉一个器件★)
        T5b: 板侧造两个 ref 反查到同一 base ⇒ 触发 build_ref_map 的 ambig 分支
             (★手法: 板侧同时放 `a_1` 与 `a`, 并把【表侧的 a 改名成别的】⇒ 那就是 miss…)
             ⇒ ★★改为: 板侧放 `a_1` + `a`, 表侧放 `a` (同名) ⇒ a 跳过 ⇒ 无 ambig
             ⇒ ★★⇒ 用【表侧 a 与 a_1 共存】+ 板侧放【a_1 与 a】⇒ 表侧 a 命中 ⇒ a 跳过 ⇒ 无 ambig
             ⇒ ★★⇒ 结论: ambig 分支在本项目当前判据里【几乎不可达】(★fail-closed 残留分支★)
                  ⇒ ★★这是本单的一个【新发现】★★ ⇒ 老实报出来, 不假装能触发
    """
    rows, flds = load_rows(base_net)
    # 选一对: 表侧有 `a` (改名成 a_1 的) ⇒ 板侧有 a_1
    # 找一个表侧 ref, 把它【新增】一份成 X_1 ⇒ 造 (X, X_1) 共存
    TARGET = "C_AC_CSI_D0_CK_N"
    extra = []
    for r in rows:
        r2 = dict(r)
        if (r2.get("ref") or "").strip() == TARGET:
            r3 = dict(r)
            r3["ref"] = TARGET + "_1"
            extra.append(r3)
    if not extra:
        print("⚠️ T5 找不到目标 ref %s ⇒ 换 TARGET" % TARGET)
        return None
    out = os.path.join(SB, "netlist_t5.csv")
    write_rows(rows + extra, flds, out)
    print("★T5a 网表 (★表侧造 (X, X_1) 共存: %s + %s_1★): %s" % (TARGET, TARGET, out))
    return out


def make_t5b_board(base_board_txt):
    """★T5b: 板侧造两个 ref 反查到同一 base ⇒ 触发 ambig 分支
    ★手法: 板侧同时有 `a_1` (改名来的) 与 `a` —— 但 a 若在表侧就跳过
    ★★⇒ 改为: 板侧加一个 `a` 的封装副本, 并把【表侧的 a】改名掉? ⇒ 那是 miss
    ★★★⇒ 只剩一条路: 板侧加【a_1 的第二个副本】(★同名两封装★) ⇒ 触发 "base in m.values()"
        因为第一个 a_1 映射到 'a', 第二个 a_1 再来 ⇒ base 'a' 已在 m.values() ⇒ ambig!
    ★★★★ 这是最干净的 T5b 造法: ★板侧同名封装出现两次 ⇒ 映射歧义★★"""
    src = open(base_board_txt, encoding="utf-8", errors="replace").read()
    rx = re.compile(r'(\(property "Reference" ")([^"]*)(")')
    # 取第一个可改名的 ref 的整块 footprint, 复制一份并改 ref
    m = re.search(r'\n\t\(footprint "[^"]*".*?\n\t\)\n', src, re.S)
    if not m:
        print("⚠️ T5b 找不到 footprint 块")
        return None
    blk = m.group(0)
    rm = rx.search(blk)
    if not rm:
        print("⚠️ T5b footprint 块里没有 Reference")
        return None
    old_ref = rm.group(2)
    new_ref = kicad_ref(old_ref)
    if new_ref == old_ref:
        # 找一个末字符是字母的
        for mm in rx.finditer(blk):
            if kicad_ref(mm.group(2)) != mm.group(2):
                old_ref = mm.group(2)
                new_ref = kicad_ref(old_ref)
                break
    blk2 = blk.replace('(property "Reference" "%s"' % old_ref,
                       '(property "Reference" "%s"' % new_ref)
    # 复制块, 把 ref 再改成同一个 new_ref (同名两封装 ⇒ 歧义)
    blk3 = blk2
    out_txt = src.replace(blk, blk + blk3, 1)
    out = os.path.join(SB, "board_t5b.kicad_pcb")
    open(out, "w", encoding="utf-8", errors="replace").write(out_txt)
    print("★T5b 板副本 (★同名封装 %s 出现两次 ⇒ 映射歧义★): %s" % (new_ref, out))
    return out, new_ref


def make_t6(base_board_txt):
    """★T6: 板侧 ref 改成表侧没有的名字 (★<原名>_2★) ⇒ 反查不命中 ⇒ 期望「口径未同步」红"""
    src = open(base_board_txt, encoding="utf-8", errors="replace").read()
    rx = re.compile(r'(\(property "Reference" ")([^"]*)(")')
    TARGET = None
    for m in rx.finditer(src):
        r = m.group(2)
        if r.endswith("_1") and kicad_ref(r[:-2]) != "":
            TARGET = r
            break
    if TARGET is None:
        print("⚠️ T6 找不到带 _1 的 ref")
        return None
    new_ref = TARGET + "_2"     # ★<原名>_2 ★去掉 _1 也不命中 (base = 'X_1' 不在表侧), 也不以 _1 结尾★
    out_txt = src.replace('(property "Reference" "%s"' % TARGET,
                          '(property "Reference" "%s"' % new_ref, 1)
    out = os.path.join(SB, "board_t6.kicad_pcb")
    open(out, "w", encoding="utf-8", errors="replace").write(out_txt)
    print("★T6 板副本 (★板侧 ref %s ⇒ %s (表侧没有的名字)★): %s" % (TARGET, new_ref, out))
    return out, TARGET, new_ref


if __name__ == "__main__":
    print("=" * 90)
    print("ISS-317 · U-1 · T5/T6 沙盒造场 (★只写 tmp/iss317_sandbox/★)")
    print("=" * 90)
    base_net = make_base()
    base_board, seen = make_base_board()
    t5 = make_t5(base_net)
    t5b = make_t5b_board(base_board)
    t6 = make_t6(base_board)
    # 判据脚本拷进沙盒 (★只读项目留档·拷进沙盒跑★)
    dst = os.path.join(SB, "check_pcb_nets_reflookup.py")
    shutil.copy2(REFLOOKUP, dst)
    print("★判据副本 (★从 logs/iss314/ 只读拷入·项目闸脚本未动★): %s" % dst)
    print()
    print("★造场清单:")
    print("  底座板 (改名 %d 个)      : %s" % (len(seen), base_board))
    print("  底座网表 (三侧同口径)     : %s" % base_net)
    print("  T5a 网表 (X 与 X_1 共存)  : %s" % (t5 or "(未造出)"))
    print("  T5b 板 (同名封装两份)     : %s" % (t5b[0] if t5b else "(未造出)"))
    print("  T6 板 (%s ⇒ %s)       : %s" % (t6[1], t6[2], t6[0]) if t6 else "  T6: 未造出")
