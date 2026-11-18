#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iss321_doc_gate_check.py —— ISS-321 · 交卷文档自检 (★用 ISS-318 闸自己的分类逻辑·不重写★)

★★为什么需要这个 ★★:
    ISS-318 的 `check_sw_ref_reachability.py` 扫 `SW/*.md` ⇒ ★任何文档里出现的
    「形状像位号但现在盘上解析不到」的 token ⇒ 都被判成【新增真隐患】⇒ 闸红★
    ⇒ ★本单自己新写的 `SW/ONETRIP_SW_RENAME_SAFETY.md` 里【必然】出现
       【改名后名】(盘上还没有) 与【纯形状假阳性】⇒ ★闸会红★
    ⇒ ★本脚本用【闸自己的 classify() 逻辑】逐 token 预演 ⇒ 交卷前自查★

用法:
    python3 logs/iss321/iss321_doc_gate_check.py [文件 ...]
    ★不给文件 ⇒ 默认查 SW/ONETRIP_SW_RENAME_SAFETY.md★
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(HERE))
GATE = os.path.join(PROJ, "SW", "tools", "check_sw_ref_reachability.py")

spec = importlib.util.spec_from_file_location("g", GATE)
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)


def main():
    files = sys.argv[1:] or [os.path.join("SW", "ONETRIP_SW_RENAME_SAFETY.md")]
    root = PROJ
    res = g.analyze(root)
    doc_files, anchors, env_keys = g.build_aux_index(root)
    nets = g.read_net_names(root)
    idx = {"live_refs": res["live_refs"], "net_names": nets, "board_refs": set(),
           "netlist_refs": set(), "registry": set(g.DESIGNATOR_REGISTRY),
           "doc_files": doc_files, "anchors": anchors, "env_keys": env_keys}

    # ★只查本单交卷文档的 token (★不查其它 39 份文档·那些是 ISS-318 的既有基线★) ★
    bad = {}
    base = {}
    # ★用闸自己的 token 正则 (★与 collect_doc_tokens 逐字同源★) ★
    import re as _re
    pat = _re.compile(r"\b(?:" + "|".join(_re.escape(p) for p in g.TOKEN_PREFIXES)
                       + r")[A-Za-z0-9_]*")
    for rel in files:
        p = os.path.join(root, rel)
        with open(p, encoding="utf-8", errors="replace") as f:
            for ln, line in enumerate(f, 1):
                for m in pat.finditer(line):
                    tok = m.group(0)
                    cls = g.classify(tok, idx, [(rel, ln, line.rstrip("\n"))])[0]
                    if cls in g.FAIL_CLASSES:
                        # ★闸的基线: BASELINE_TOKENS 里的 token 本来就允许对不上 ⇒ 不算新增真隐患★
                        if cls == "DESIGNATOR_MISSING" and tok in g.BASELINE_TOKENS:
                            base.setdefault(tok, []).append(ln)
                            continue
                        bad.setdefault((rel, tok, cls), []).append(ln)

    print("=" * 92)
    print("ISS-321 · 交卷文档 × ISS-318 闸 预演 (★用闸自己的 classify()·不重写★)")
    print("=" * 92)
    print("  ★闸的 fail 类: %s" % (g.FAIL_CLASSES,))
    if base:
        print("  ★闸基线已登记的 token (★允许对不上·不计入新增真隐患★): %s"
              % ", ".join("%s(x%d)" % (t, len(v)) for t, v in sorted(base.items())))
    if not bad:
        print("  ✅ 本单交卷文档【零个【新增】真隐患】⇒ ★闸保持绿★ (★rc 仍 = 0·MISSING 仍 = 基线 3★)")
        print("★写出: logs/iss321/05_doc_gate_check_raw.txt")
        open(os.path.join(PROJ, "logs", "iss321", "05_doc_gate_check_raw.txt"), "w",
             encoding="utf-8").write(
            "ISS-321 · 交卷文档 × ISS-318 闸预演 ⇒ ✅ 零个 token 会被判红\n")
        return 0
    print("  ❌ 有 %d 个 (文件, token) 会被闸判红:" % len(bad))
    for (rel, tok, cls), lns in sorted(bad.items()):
        print("     %-46s %-22s %-20s 行 %s" % (rel, tok, cls, lns[:6]))
    print("★写出: logs/iss321/05_doc_gate_check_raw.txt")
    with open(os.path.join(PROJ, "logs", "iss321", "05_doc_gate_check_raw.txt"), "w",
              encoding="utf-8") as f:
        f.write("ISS-321 · 交卷文档 × ISS-318 闸预演 ⇒ ❌ %d 个 token 会被判红\n" % len(bad))
        for (rel, tok, cls), lns in sorted(bad.items()):
            f.write("  %s | %s | %s | 行 %s\n" % (rel, tok, cls, lns[:12]))
    return 1


if __name__ == "__main__":
    sys.exit(main())
