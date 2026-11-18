#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_sch_pinfull.py —— ★★【原理图"脚数完整性"闸】★★ (★2026-11-11 新建·主线 6a★)

★★**为什么必须有这把尺子 (★背景一句话★)**:
  ★**我们这张原理图漏脚**: 逐器件【图上脚数 ≠ 表里脚数】 ⇒ 大量器件在图上只画了【一部分脚】★
  ⇒ ★**其中 `J_SOM_P2` / `J_SOM_P4` 图上【连符号都没有】(表里 9+14=23 个球位在图上不存在)★**
  ⇒ ★★**而此前我们没有任何闸能发现它** (ERC 只查"画出来的那部分对不对"· C1~C6 查的是生成器自己的账本)★★
  ⇒ ★**⇒ 本件 = 先把这把尺子做出来 ⇒ 尺子先立, 后面 (6b) 才照尺子改图** ★★

★★**判据 (★就这一条★)**:
  ★**逐器件比对: 【KiCad 从图纸里读出的脚数】 vs 【表里该 ref 的脚数(含 DNP)】 ⇒ 必须【逐个相等】**
  ⇒ 不等就点名"哪个器件差几个脚" ⇒ ★**rc=0 才算过**★

★★**"图里读出脚数"怎么取 (★踩过的坑★)**:
  ★**跑 `bash state/kicad.sh sch export netlist -o <out> HW/PCB/demo_mainboard.kicad_sch`**
  ⇒ 解析 **(nets ...)** 段里的 **(node (ref "X") (pin "N") ...)**
  ⇒ ★**每个 ref 的 node 数 = 图上脚数**★
  ⇒ ★★**⚠ `(comp (ref "X"))` 是【器件条目】不是 node ⇒ 不许混进脚数 (★main 今天踩过这个坑★)★★** ★★
  ⇒ ★★**本脚本只从 (nets ...) 段里取 node ⇒ (components ...) 段【物理上不可能】混进来**★★

★★**"表里脚数"怎么取**:
  ★**`HW/netlist_v1_pins.csv` 一行一个脚 ⇒ 按 `ref` 分组计数 (★含 DNP 的行★)** ⇒ 与图上脚数比
  ⇒ ★**为什么含 DNP**: DNP 器件【照样在 BOM 里、照样有符号、照样有脚】⇒ 它少画一个脚同样是漏脚
    ⇒ ★**且 main 自己的目标态是"把 584 脚全画出来"(584 = 含 DNP 的全部行数)⇒ 尺子必须以 584 为标尺** ★

★★**⚠ 两个口径的差 (★main 11:5x 记的 203 与本判据的 170 差在这儿★)**:
  ★**判据口径 (★默认·本闸的正式口径★) = "表里脚数【含 DNP 的行】" ⇒ K = 170**
  ★**对照口径 (★main 11:5x 用的★) = "表里脚数【只数非-DNP 行】" ⇒ K = 203**
  ⇒ ★**两者差 33 个器件**: 那 33 个是【表里整器全标 DNP】的器件 (★如 BT_432243 / C_BULK_*★)
    ⇒ 它们在图上其实【画全了】(图=表含DNP) ⇒ **去 DNP 口径会把它们误判成"图上多脚"**
  ⇒ ★**为什么判据口径取"含 DNP"**: DNP 器件【照样在 BOM 里 / 照样有符号 / 照样有脚】
    ⇒ 少画一个脚同样是漏脚 ⇒ ★**且 main 自己的目标态是"把 584 脚全画出来"(584 = 含 DNP 的全部行数)**
    ⇒ ★**尺子必须以 584 为标尺 ⇒ 6b 照这把尺子补完 ⇒ 图上才会正好 584 脚** ★
  ⇒ ★**两个口径都在输出里打印 ⇒ 差 33 的来龙去脉【可当场复核】(★不藏口径★)** ★
  ⇒ ★**复现 main 的 203: `python3 state/check_sch_pinfull.py --dnp-basis excl`★** ★

用法:
  python3 state/check_sch_pinfull.py               # 跑闸并判定 (rc=0 过 / rc=1 不过)
  python3 state/check_sch_pinfull.py --json        # 机器读格式
  python3 state/check_sch_pinfull.py --self-test   # 自测 (★含反向用例★)
  python3 state/check_sch_pinfull.py --netlist F   # 复用已导出的网表 (不再调 kicad)
  python3 state/check_sch_pinfull.py --dnp-basis excl   # ★复现 main 11:5x 的 203 口径★
"""
from __future__ import annotations

import collections
import csv
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.normpath(os.path.join(HERE, ".."))
SCH = os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_sch")
KICAD_SH = os.path.join(HERE, "kicad.sh")
TABLE = os.path.join(PROJ, "HW", "netlist_v1_pins.csv")


# ★★**KiCad 网表导出是 s-expression (★缩进用 tab, 一行一个字段★)** ★★
def _tokenize(text: str):
    """★把 s-expression 切成 token 流: '(' / ')' / ('sym', s) / ('str', s)★"""
    out = []
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c in "()":
            out.append(c)
            i += 1
        elif c.isspace():
            i += 1
        elif c == '"':
            j = i + 1
            buf = []
            while j < n:
                if text[j] == "\\":
                    buf.append(text[j + 1])
                    j += 2
                    continue
                if text[j] == '"':
                    break
                buf.append(text[j])
                j += 1
            out.append(("str", "".join(buf)))
            i = j + 1
        else:
            j = i
            while j < n and not text[j].isspace() and text[j] not in "()":
                j += 1
            out.append(("sym", text[i:j]))
            i = j
    return out


def _parse(tokens, i=0):
    """★递归解析一棵 s-expression ⇒ 返回 (节点列表, 下一个下标)★"""
    if i >= len(tokens) or tokens[i] != "(":
        raise ValueError("s-expression 语法错: 位置 %d 处期待 '('" % i)
    i += 1
    node = []
    while i < len(tokens):
        tok = tokens[i]
        if tok == "(":
            child, i = _parse(tokens, i)
            node.append(child)
        elif tok == ")":
            return node, i + 1
        else:
            node.append(tok)
            i += 1
    raise ValueError("s-expression 语法错: 括号不配对")


def _find(node, name):
    """★取 node 下面第一层里 head 为 name 的所有子节点★"""
    return [c for c in node
            if isinstance(c, list) and c and isinstance(c[0], tuple) and c[0][0] == "sym"
            and c[0][1] == name]


def _head(node):
    if node and isinstance(node[0], tuple) and node[0][0] == "sym":
        return node[0][1]
    return None


def _val(tok):
    """★取一个【裸 token】的字符串值 (★token 形如 ('str', 'U1')★)"""
    if isinstance(tok, tuple) and len(tok) >= 2 and tok[0] == "str":
        return tok[1]
    if isinstance(tok, list) and tok and isinstance(tok[0], tuple) and tok[0][0] == "str":
        return tok[0][1]
    return ""


def parse_netlist_pin_counts(text: str):
    """★从 KiCad 导出的网表里抽【每个 ref 的脚数】⇒ (counts, stats)★

    ★★**只认 (nets ...) 段里的 (node (ref "X") (pin "N") ...)★**
    ⇒ ★**(components ...) 段的 (comp (ref "X")) 【器件条目】绝不会被当成脚 (★main 踩过的坑★)**★★
    """
    tree, _ = _parse(_tokenize(text))
    nets_sec = _find(tree, "nets")
    if not nets_sec:
        raise ValueError("网表里找不到 (nets ...) 段 ⇒ 导出格式不符预期")
    counts = collections.Counter()
    nodes = 0
    no_ref = 0
    for net in _find(nets_sec[0], "net"):
        for node in _find(net, "node"):
            nodes += 1
            ref = None
            for kid in node:
                if isinstance(kid, list) and _head(kid) == "ref":
                    ref = _val(kid[1])
                    break
            if ref:
                counts[ref] += 1
            else:
                no_ref += 1
    stats = {
        "nets": len(_find(nets_sec[0], "net")),
        "nodes": nodes,
        "nodes_without_ref": no_ref,
        "refs_on_schematic": len(counts),
        "total_pins_on_schematic": sum(counts.values()),
        "components_section_entries": len(_find(_find(tree, "components")[0], "comp"))
        if _find(tree, "components") else 0,
    }
    return counts, stats


def parse_table_pin_counts(path: str):
    """★从 `HW/netlist_v1_pins.csv` 抽【每个 ref 的脚数】⇒ (counts_incl_dnp, counts_excl_dnp, stats)★

    ★**含 DNP 的行一律计入 (★判据口径★)**: DNP 器件照样在 BOM 里 / 照样有符号 / 照样有脚
    ⇒ ★**另出一个"去掉 DNP 行"的口径, 只作对照打印 (★main 11:5x 记的 203 就是这个口径★)** ★
    """
    incl = collections.Counter()
    excl = collections.Counter()
    dnp_rows = 0
    blank_ref = 0
    with open(path, newline="", encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            ref = (row.get("ref") or "").strip()
            if not ref:
                blank_ref += 1
                continue
            incl[ref] += 1
            if (row.get("dnp") or "").strip().upper() == "DNP":
                dnp_rows += 1
            else:
                excl[ref] += 1
    stats = {
        "rows": sum(incl.values()),
        "refs": len(incl),
        "dnp_rows": dnp_rows,
        "rows_without_ref": blank_ref,
        "total_pins_incl_dnp": sum(incl.values()),
        "total_pins_excl_dnp": sum(excl.values()),
    }
    return incl, excl, stats


def compare_refs(sch_counts, tbl_counts):
    """★【唯一的比对函数】⇒ (universe, mismatches, stats)★

    ★**逐 ref 比较: 图上脚数 vs 表里脚数 ⇒ 必须逐个相等** ★
    """
    universe = sorted(set(sch_counts) | set(tbl_counts))
    mismatches = []
    for ref in universe:
        a = sch_counts.get(ref, 0)
        b = tbl_counts.get(ref, 0)
        if a != b:
            mismatches.append({"ref": ref, "sch": a, "tbl": b, "delta": a - b})
    return universe, mismatches, {
        "universe": len(universe),
        "equal": len(universe) - len(mismatches),
        "mismatched": len(mismatches),
        "sch_pins": sum(sch_counts.get(r, 0) for r in universe),
        "tbl_pins": sum(tbl_counts.get(r, 0) for r in universe),
    }


def evaluate(sch_counts, tbl_counts, comparator=compare_refs):
    """★跑一次比对 ⇒ (rc, universe, mismatches, stats)★  ★**rc=0 只在【逐个相等】时给** ★"""
    universe, mismatches, stats = comparator(sch_counts, tbl_counts)
    rc = 0 if not mismatches else 1
    return rc, universe, mismatches, stats


# ─────────────────────────── 跑闸 ───────────────────────────
def export_netlist(out_path: str):
    """★跑 KiCad 导网表 ⇒ (rc, stdout/stderr 尾巴)★"""
    cmd = ["bash", KICAD_SH, "sch", "export", "netlist", "-o", out_path,
           os.path.relpath(SCH, PROJ)]
    p = subprocess.run(cmd, cwd=PROJ, capture_output=True, text=True, timeout=1800)
    tail = ((p.stdout or "") + (p.stderr or "")).strip().splitlines()
    return p.returncode, (tail[-1] if tail else "")


def run_gate(netlist_path=None, dnp_basis="incl"):
    """★主流程 ⇒ (rc, report_dict)★

    ★**dnp_basis**: "incl" (★默认·判据口径: 表里脚数含 DNP 行★) | "excl" (★main 11:5x 口径: 只数非-DNP 行★)
    """
    if dnp_basis not in ("incl", "excl"):
        raise ValueError("dnp_basis 只能是 incl / excl, 收到 %r" % dnp_basis)
    tmp = None
    if netlist_path:
        nl_path = netlist_path
    else:
        tmp = tempfile.NamedTemporaryFile(prefix="_pinfull_", suffix=".net", delete=False)
        nl_path = tmp.name
        tmp.close()
    try:
        export_note = ""
        if not netlist_path:
            rc_exp, export_note = export_netlist(nl_path)
            if rc_exp != 0 or not os.path.exists(nl_path) or os.path.getsize(nl_path) == 0:
                return 2, {"error": "KiCad 网表导出失败 (rc=%s) %s" % (rc_exp, export_note)}
        text = open(nl_path, encoding="utf-8", errors="replace").read()
        sch_counts, sch_stats = parse_netlist_pin_counts(text)
        tbl_incl, tbl_excl, tbl_stats = parse_table_pin_counts(TABLE)
        rc, universe, mismatches, stats = evaluate(sch_counts, tbl_incl)

        # ★对照口径: 去掉 DNP 行 (★main 11:5x 的 203 就是这个口径★) ⇒ 两种口径都算出来, 便于当场复核
        _, _, mm_excl, st_excl = evaluate(sch_counts, tbl_excl)
        if dnp_basis == "excl":
            # ★显式切到 main 的口径 ⇒ 判定也按它走 (★复现 203 用★)★
            rc, universe, mismatches, stats = evaluate(sch_counts, tbl_excl)
        return rc, {
            "sch_stats": sch_stats,
            "tbl_stats": tbl_stats,
            "stats": stats,
            "mismatches": mismatches,
            "universe": universe,
            "note_export": export_note,
            "dnp_basis": dnp_basis,
            "alt_excl_dnp": {
                "mismatched": st_excl["mismatched"],
                "sch_pins": st_excl["sch_pins"],
                "tbl_pins": st_excl["tbl_pins"],
            },
            "alt_incl_dnp": {
                "mismatched": stats["mismatched"] if dnp_basis == "incl" else None,
            },
        }
    finally:
        if tmp and not netlist_path:
            try:
                os.unlink(nl_path)
            except OSError:
                pass


# ─────────────────────────── 自测 ───────────────────────────
_SYNTH_NETLIST = """(export
  (version "E")
  (design (source "synth"))
  (components
    (comp (ref "U1") (value "SYNTH") (libsource (lib "")))
    (comp (ref "C1") (value "SYNTH") (libsource (lib "")))
    (comp (ref "R1") (value "SYNTH") (libsource (lib "")))
    (comp (ref "J_GHOST") (value "ONLY_COMP_NO_NODE") (libsource (lib "")))
  )
  (nets
    (net (code "1") (name "VCC")
      (node (ref "U1") (pin "1") (pinfunction "P1_1") (pintype "passive"))
      (node (ref "C1") (pin "1") (pinfunction "P1_1") (pintype "passive"))
    )
    (net (code "2") (name "GND")
      (node (ref "U1") (pin "2") (pinfunction "P2_2") (pintype "passive"))
    )
  )
)
"""

# ★合成小样本: ★含 DNP 行★ (U1 两脚都必装 / C1 一脚必装一脚DNP / R1 两脚DNP / J_GHOST 只在表里)
_SYNTH_CSV = (
    "pin_id,net,ref,pin,page,value,type,dnp,board,conn_id,footprint,opn,evidence,tbd,note\n"
    "U1.1,VCC,U1,1,P1,V,,IC,必装,MAIN_PCB,,,,[推算],,\n"
    "U1.2,GND,U1,2,P1,V,,IC,必装,MAIN_PCB,,,,[推算],,\n"
    "C1.1,VCC,C1,1,P1,C,,C,必装,MAIN_PCB,,,,[推算],,\n"
    "C1.2,GND,C1,2,P1,C,,C,DNP,MAIN_PCB,,,,[推算],,\n"
    "R1.1,NC,R1,1,P1,R,,R,DNP,MAIN_PCB,,,,[推算],,\n"
    "R1.2,NC,R1,2,P1,R,,R,DNP,MAIN_PCB,,,,[推算],,\n"
    "J_GHOST.1,NC,J_GHOST,1,P1,J,,CONN,必装,MAIN_PCB,,,,[推算],,\n"
)


def _self_battery(sch_counts, tbl_counts, comparator):
    """★自测断言组 ⇒ (failures[])★  ★**参数化 comparator ⇒ 反向用例能把比对函数换掉** ★"""
    fails = []
    rc, universe, mismatches, stats = evaluate(sch_counts, tbl_counts, comparator)

    # ① node 数解析: 只认 (nets) 段的 node ⇒ (comp) 里的 J_GHOST 必须是 0 脚
    if sch_counts.get("J_GHOST", 0) != 0:
        fails.append("① (comp (ref ...)) 混进脚数了: J_GHOST 图上脚数=%d (期望 0)"
                     % sch_counts.get("J_GHOST", 0))
    if sch_counts.get("U1") != 2:
        fails.append("① U1 图上脚数=%s (期望 2)" % sch_counts.get("U1"))
    if sch_counts.get("C1") != 1:
        fails.append("① C1 图上脚数=%s (期望 1)" % sch_counts.get("C1"))
    if sch_counts.get("R1", 0) != 0:
        fails.append("① R1 图上脚数=%s (期望 0: 图上没画)" % sch_counts.get("R1", 0))

    # ② 表里脚数解析: ★含 DNP 的行★ ⇒ C1 应为 2 / R1 应为 2
    if tbl_counts.get("C1") != 2:
        fails.append("② C1 表里脚数=%s (期望 2: 含 DNP 行)" % tbl_counts.get("C1"))
    if tbl_counts.get("R1") != 2:
        fails.append("② R1 表里脚数=%s (期望 2: 含 DNP 行)" % tbl_counts.get("R1"))
    if tbl_counts.get("U1") != 2:
        fails.append("② U1 表里脚数=%s (期望 2)" % tbl_counts.get("U1"))

    # ③ 判据: U1 相等 ⇒ 2 脚全画了 ⇒ 不该被点名; C1/R1/J_GHOST 图上都少脚 ⇒ 必须被点名
    flagged = {m["ref"] for m in mismatches}
    if "U1" in flagged:
        fails.append("③ U1 脚数相等却被点名 (误报)")
    for ref in ("C1", "R1", "J_GHOST"):
        if ref not in flagged:
            fails.append("③ %s 漏脚却没被点名 (漏报)" % ref)
    if rc != 1:
        fails.append("③ 合成样本应判不过 (rc 期望 1, 实得 %d)" % rc)
    if stats["universe"] != 4:
        fails.append("③ universe=%s (期望 4: U1/C1/R1/J_GHOST)" % stats["universe"])

    # ④ 全部相等时必须 rc=0 (★不许把好板判死★)
    ok_rc, _, ok_mm, _ = evaluate({"X1": 3}, {"X1": 3}, comparator)
    if ok_rc != 0 or ok_mm:
        fails.append("④ 相等的样本被判成不过 (rc=%d, 点名 %d 个)" % (ok_rc, len(ok_mm)))
    return fails


def self_test() -> int:
    """★自测 (★铁律: 必须带反向用例 —— 判据改弱 ⇒ 自测必须红 rc=1★)"""
    fails = []

    # ① 合成小样本 (★含 DNP 行★)
    sch_counts, _ = parse_netlist_pin_counts(_SYNTH_NETLIST)
    tbl_counts, _, _ = _parse_synth_table(_SYNTH_CSV)
    fails += _self_battery(sch_counts, tbl_counts, compare_refs)

    # ② ★反向用例: 把比对函数改弱成"永远相等" ⇒ 同一份断言必须【红】 ★
    def _always_equal(sch, tbl):
        universe = sorted(set(sch) | set(tbl))
        return universe, [], {"universe": len(universe), "equal": len(universe),
                              "mismatched": 0, "sch_pins": 0, "tbl_pins": 0}

    bad_fails = _self_battery(sch_counts, tbl_counts, _always_equal)
    if not bad_fails:
        fails.append("② 反向用例失效: 比对函数被改成'永远相等'后自测仍然全绿 "
                     "⇒ 断言没在区分真判据和弱判据")
    else:
        print("   [反向用例] 比对函数改弱成'永远相等' ⇒ 自测如期变红 (%d 条断言失败) ✔"
              % len(bad_fails))

    # ③ 真网表解析不许把 (comp) 当脚 (★main 踩过的坑★ ⇒ 单独再钉一次★)
    for tag, txt in (("(nets) 段", _SYNTH_NETLIST),):
        c, st = parse_netlist_pin_counts(txt)
        if st["nodes"] != 3:
            fails.append("③ %s node 数=%d (期望 3)" % (tag, st["nodes"]))
        if st["components_section_entries"] != 4:
            fails.append("③ %s (comp) 条目数=%d (期望 4) ⇒ 说明段被认错了"
                         % (tag, st["components_section_entries"]))

    if fails:
        for f in fails:
            print("❌", f)
        print("SELFTEST FAILED")
        return 1
    print("ALL TESTS PASS (合成样本含DNP / comp-不算脚 / 反向用例)")
    return 0


def _parse_synth_table(text: str):
    """★合成 CSV 文本 ⇒ (counts_incl_dnp, counts_excl_dnp, stats)★"""
    import io
    rows = list(csv.DictReader(io.StringIO(text)))
    incl = collections.Counter()
    excl = collections.Counter()
    for row in rows:
        ref = (row.get("ref") or "").strip()
        if not ref:
            continue
        incl[ref] += 1
        if (row.get("dnp") or "").strip().upper() == "DNP":
            pass
        else:
            excl[ref] += 1
    stats = {"rows": sum(incl.values()), "refs": len(incl),
             "dnp_rows": sum(incl.values()) - sum(excl.values())}
    return incl, excl, stats


def main() -> int:
    args = sys.argv[1:]
    if "--self-test" in args:
        return self_test()
    if "--netlist" in args:
        nl = args[args.index("--netlist") + 1]
    else:
        nl = None
    dnp_basis = "incl"
    if "--dnp-basis" in args:
        dnp_basis = args[args.index("--dnp-basis") + 1]
    if not os.path.exists(SCH):
        print("❌ 原理图不存在: %s" % SCH)
        return 2
    if not os.path.exists(TABLE):
        print("❌ 引脚表不存在: %s" % TABLE)
        return 2
    rc, rep = run_gate(netlist_path=nl, dnp_basis=dnp_basis)
    if "error" in rep:
        print("❌", rep["error"])
        return rc

    st = rep["stats"]
    alt = rep["alt_excl_dnp"]
    if "--json" in args:
        print(json.dumps({"rc": rc, "sch_stats": rep["sch_stats"],
                          "tbl_stats": rep["tbl_stats"], "stats": st,
                          "alt_excl_dnp": alt,
                          "mismatches": rep["mismatches"]}, ensure_ascii=False, indent=1))
        return rc

    print("═══ 原理图脚数完整性闸 (★sch_pinfull · %s★)" % os.path.relpath(SCH, PROJ))
    if rep.get("note_export"):
        print("  [KiCad] %s" % rep["note_export"])
    print("  [口径] 表里脚数 = %s" % ("含 DNP 行 (★判据口径·默认★)" if rep.get("dnp_basis") == "incl"
                                    else "只数非-DNP 行 (★main 11:5x 口径★)"))
    print("  总数: 图上 %d 脚 / 表里 %d 脚 · 不一致器件数 K=%d (universe=%d)"
          % (st["sch_pins"], st["tbl_pins"], st["mismatched"], st["universe"]))
    print("  (图上: %d 个器件 · %d 个网 · %d 个 node | 表里: %d 行 · %d 个 ref · 其中 DNP 行 %d)"
          % (rep["sch_stats"]["refs_on_schematic"], rep["sch_stats"]["nets"],
             rep["sch_stats"]["nodes"], rep["tbl_stats"]["rows"],
             rep["tbl_stats"]["refs"], rep["tbl_stats"]["dnp_rows"]))
    print("  逐个点名 (ref: 图= a 表= b):")
    for m in rep["mismatches"]:
        print("   · %-24s 图=%3d 表=%3d  (差 %+d)" % (m["ref"], m["sch"], m["tbl"], m["delta"]))
    print("  [对照口径] 去掉 DNP 行 (★main 11:5x 口径★): 图上 %d 脚 / 表里 %d 脚 · 不一致 %d"
          % (alt["sch_pins"], alt["tbl_pins"], alt["mismatched"]))
    print("  判定: %s" % ("✅ 过 (逐器件脚数全相等)" if rc == 0 else
                           "❌ 不过 (K=%d ≠ 0) ⇒ 图上漏脚 ⇒ 原理图不许进投产包" % st["mismatched"]))
    return rc


if __name__ == "__main__":
    sys.exit(main())
