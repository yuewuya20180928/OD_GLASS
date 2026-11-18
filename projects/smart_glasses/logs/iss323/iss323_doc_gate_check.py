#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iss323_doc_gate_check.py —— ISS-323 · 本单两份交卷文档 × ISS-318 闸 的预演自检

★★为什么需要这个 ★★:
    ISS-318 的 `check_sw_ref_reachability.py` 扫 `SW/*.md` ⇒ ★任何文档里出现的
    「形状像位号但现在盘上解析不到」的 token ⇒ 都被判成【新增真隐患】⇒ 闸红★
    ⇒ ★本单自己新写的 `SW/ONETRIP_SW_SAMEBATCH_RENAME_LIST.md` 里【必然】出现
       【改名后名】(盘上还没有) 与【纯形状假阳性】⇒ ★闸会红★
    ⇒ ★本脚本用【闸自己的 classify() 逻辑】逐 token 预演 ⇒ 交卷前自查★★

★★与 ISS-321 的 `iss321_doc_gate_check.py` 的差别 ★★:
    · 输出落 `logs/iss323/` (★不覆盖 ISS-321 的留档★)
    · 默认查本单的【两份】交卷文档

用法:
    python3 logs/iss323/iss323_doc_gate_check.py [文件 ...]
"""
import importlib.util
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(HERE))
GATE = os.path.join(PROJ, "SW", "tools", "check_sw_ref_reachability.py")
OUT = os.path.join(HERE, "16_doc_gate_check.txt")

DEFAULT = [
    "SW/ONETRIP_SW_SAMEBATCH_RENAME_LIST.md",
]

spec = importlib.util.spec_from_file_location("g", GATE)
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)


def main():
    files = sys.argv[1:] or DEFAULT
    root = PROJ
    res = g.analyze(root)
    doc_files, anchors, env_keys = g.build_aux_index(root)
    nets = g.read_net_names(root)
    idx = {"live_refs": res["live_refs"], "net_names": nets, "board_refs": set(),
           "netlist_refs": set(), "registry": set(g.DESIGNATOR_REGISTRY),
           "doc_files": doc_files, "anchors": anchors, "env_keys": env_keys}

    bad = {}
    base = {}
    pat = re.compile(r"\b(?:" + "|".join(re.escape(p) for p in g.TOKEN_PREFIXES)
                       + r")[A-Za-z0-9_]*")
    for rel in files:
        p = os.path.join(root, rel)
        with open(p, encoding="utf-8", errors="replace") as f:
            for ln, line in enumerate(f, 1):
                for m in pat.finditer(line):
                    tok = m.group(0)
                    cls = g.classify(tok, idx, [(rel, ln, line.rstrip("\n"))])[0]
                    if cls in g.FAIL_CLASSES:
                        if cls == "DESIGNATOR_MISSING" and tok in g.BASELINE_TOKENS:
                            base.setdefault(tok, []).append(ln)
                            continue
                        bad.setdefault((rel, tok, cls), []).append(ln)

    out = []
    out.append("=" * 92)
    out.append("ISS-323 · 本单交卷文档 × ISS-318 闸 预演 (★用闸自己的 classify()·不重写★)")
    out.append("=" * 92)
    out.append("  ★闸的 fail 类: %s" % (g.FAIL_CLASSES,))
    out.append("  ★检查的文件: %s" % ", ".join(files))
    if base:
        out.append("  ★闸基线已登记的 token (★允许对不上·不计入新增真隐患★): %s"
                   % ", ".join("%s(x%d)" % (t, len(v)) for t, v in sorted(base.items())))
    if not bad:
        out.append("  ✅ 本单交卷文档【零个【新增】真隐患】⇒ ★闸保持绿★ (★rc 仍 = 0·MISSING 仍 = 基线 3★)")
        rc = 0
    else:
        out.append("  ❌ 有 %d 个 (文件, token) 会被闸判红:" % len(bad))
        for (rel, tok, cls), lns in sorted(bad.items()):
            out.append("     %-46s %-22s %-20s 行 %s" % (rel, tok, cls, lns[:8]))
        rc = 1
    out.append("=" * 92)
    txt = "\n".join(out) + "\n"
    print(txt)
    open(OUT, "w", encoding="utf-8").write(txt)
    print("★写出: logs/iss323/16_doc_gate_check.txt")
    return rc


if __name__ == "__main__":
    sys.exit(main())
