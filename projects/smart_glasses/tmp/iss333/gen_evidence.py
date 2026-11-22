#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-333 · 基线复现证据生成器 (★只读·产物只写 logs/iss333/★)

复现 ISS-326 设计稿 §5 的实测链 (60 → -4 自污染 → -40 py 变量名 = 16),
并给出本单口径细化后的最终分区 (基线 10 / C17 非位号 12)。
"""
from __future__ import annotations
import glob, hashlib, importlib.util, json, os, re, sys, tokenize

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "logs", "iss333")
spec = importlib.util.spec_from_file_location("sw_gate", os.path.join(ROOT, "SW", "tools", "check_sw_ref_reachability.py"))
sw = importlib.util.module_from_spec(spec); sys.modules["sw_gate"] = sw; spec.loader.exec_module(sw)
GATE_REL = "MECH/tools/check_mech_ref_reachability.py"

md = sorted(glob.glob(os.path.join(ROOT, "MECH", "**", "*.md"), recursive=True))
py = [p for p in sorted(glob.glob(os.path.join(ROOT, "MECH", "**", "*.py"), recursive=True))
      if os.path.relpath(p, ROOT) != GATE_REL]
py_names = set()
for p in py:
    with open(p, "rb") as fh:
        for t in tokenize.tokenize(fh.readline):
            if t.type == tokenize.NAME:
                py_names.add(t.string)

TOK = re.compile(r"\b(?:" + "|".join(re.escape(p) for p in sw.TOKEN_PREFIXES) + r")[A-Za-z0-9_]*")
BARE = re.compile(r"\b(?:Q|X)\d+\b")
SELF_DOC = "MECH/ONETRIP_S1_RENAME_SAFETY_AUDIT.md"

occ = {}
occ_bare = {}
for path in md + py:
    rel = os.path.relpath(path, ROOT)
    with open(path, encoding="utf-8", errors="replace") as fh:
        for ln, line in enumerate(fh, 1):
            for m in TOK.finditer(line):
                occ.setdefault(m.group(0), []).append((rel, ln, line.rstrip("\n")))
            for m in BARE.finditer(line):
                occ_bare.setdefault(m.group(0), []).append((rel, ln, line.rstrip("\n")))
occ_all = dict(occ)
for k, v in occ_bare.items():
    occ_all.setdefault(k, []).extend(v)

board = sw.read_board_refs(os.path.join(ROOT, sw.BOARD_REL))
net = sw.read_netlist_refs({"root": ROOT})
live = set(board) | set(net)
registry = {t for t in occ if t in live}


def aux(mode):
    if mode == "sw":
        df, an, ek = sw.build_aux_index(ROOT)
        return set(df), set(an), set(ek)
    df, an, ek = set(), set(), set()
    for p in md:
        rel = os.path.relpath(p, ROOT)
        df.add(os.path.splitext(rel)[0]); df.add(os.path.splitext(os.path.basename(rel))[0])
        for m in re.finditer(r"#\s*(?:BEGIN|END)\s+([A-Za-z0-9_]+)",
                             open(p, encoding="utf-8", errors="replace").read()):
            an.add(m.group(1))
    ep = re.compile(r"os\.environ(?:\.get\(|\.setdefault\(|\.pop\(|\[)\s*[\"']([A-Za-z0-9_]+)[\"']")
    for p in py:
        for m in ep.finditer(open(p, encoding="utf-8", errors="replace").read()):
            ek.add(m.group(1))
    return df, an, ek


def c14_set(aux_mode, with_bare):
    df, an, ek = aux(aux_mode)
    idx = {"root": ROOT, "board_refs": board, "netlist_refs": net, "live_refs": live,
           "net_names": sw.read_net_names(ROOT), "doc_files": df, "anchors": an,
           "env_keys": ek, "registry": registry}
    src = occ_all if with_bare else occ
    out = {}
    for tok, o in src.items():
        cls, rule, why = sw.classify(tok, idx, o)
        if cls == "DESIGNATOR_MISSING":
            files = sorted({x[0] for x in o})
            out[tok] = {"n": len(o), "files": files,
                        "py_only": all(f.endswith(".py") for f in files),
                        "md_hit": any(f.endswith(".md") for f in files),
                        "in_self_doc": SELF_DOC in files,
                        "ident": tok in py_names}
    return out


iss326_raw = c14_set("mech", False)          # ★ISS-326 原型口径: MECH-only aux · 不含裸编号★
iss326_v = {t: v for t, v in iss326_raw.items() if not v["in_self_doc"] and not v["py_only"]}

today_sw_raw = c14_set("sw", False)          # ★零漂移 aux (SW 的 build_aux_index) · 不含裸编号★
today_sw_bare = c14_set("sw", True)
today_sw_v = {t: v for t, v in today_sw_raw.items() if not v["in_self_doc"] and not v["py_only"]}

# ★本单最终口径: C15 (Python 标识符) + C16 (裸编号) + C17 (已登记非位号)★
g = importlib.util.spec_from_file_location("mechgate", os.path.join(ROOT, GATE_REL))
mg = importlib.util.module_from_spec(g); sys.modules["mechgate"] = mg; g.loader.exec_module(mg)

final_missing = []
pre_c17 = []
for tok in sorted(today_sw_bare):
    _df, _an, _ek = aux("sw")
    _idx = {"root": ROOT, "board_refs": board, "netlist_refs": net, "live_refs": live,
            "net_names": sw.read_net_names(ROOT), "doc_files": set(_df),
            "anchors": set(_an), "env_keys": set(_ek),
            "registry": registry, "py_idents": py_names,
            "non_designator_registry": set(mg.MECH_NON_DESIGNATOR_REGISTRY)}
    cls, rule, why = mg.classify_mech(tok, _idx, occ_all[tok])
    if cls == "DESIGNATOR_MISSING":
        final_missing.append((tok, rule, today_sw_bare.get(tok, {})))
    # ★C17 之前的那一层 (★用来把 C17 那几条单独拎出来记账★)
    _idx2 = dict(_idx); _idx2["non_designator_registry"] = set()
    cls2, rule2, _w2 = mg.classify_mech(tok, _idx2, occ_all[tok])
    if cls2 == "DESIGNATOR_MISSING":
        pre_c17.append((tok, rule2, today_sw_bare.get(tok, {})))

baseline_now = sorted(t for t, _r, _v in pre_c17 if t in mg.BASELINE_TOKENS)
c17_now = sorted(t for t, _r, _v in pre_c17 if t in mg.MECH_NON_DESIGNATOR_REGISTRY)
unlisted = sorted(t for t, _r, _v in pre_c17
                  if t not in mg.BASELINE_TOKENS and t not in mg.MECH_NON_DESIGNATOR_REGISTRY)

out = {
    "machine": "yuewuya-RedmiBook-14",
    "generated_at": "2026-11-18 (ISS-333)",
    "scan_surface": {"md": len(md), "py": len(py), "total": len(md) + len(py),
                     "glob": "MECH/**/*.md (递归) + MECH/**/*.py (递归)",
                     "self_excluded": GATE_REL},
    "live_refs": len(live),
    "iss326_design_chain": {
        "note": "★ISS-326 设计稿 §5 的实测链, 原样复现 (ISS-326 原型口径: MECH-only aux · 不含裸编号)★",
        "raw_C14_2026-11-18_iss326": 60,
        "raw_C14_reproduced_today": len(iss326_raw),
        "minus_self_pollution_iss326": 4,
        "minus_self_pollution_today": sum(1 for v in iss326_raw.values() if v["in_self_doc"]),
        "minus_py_varnames_iss326": 40,
        "minus_py_varnames_today": sum(1 for v in iss326_raw.values() if v["py_only"]),
        "baseline_iss326": 16,
        "baseline_reproduced_today_same_caliber": len(iss326_v),
        "baseline_reproduced_today_same_caliber_list": sorted(iss326_v),
        "diff_vs_iss326": {
            "added_today": sorted(set(iss326_v) - set(json.load(open(os.path.join(ROOT, "logs/iss326/gate_design/mech_gate_baseline.json")))["baseline_tokens"])),
            "gone_today": sorted(set(json.load(open(os.path.join(ROOT, "logs/iss326/gate_design/mech_gate_baseline.json")))["baseline_tokens"]) - set(iss326_v)),
        },
    },
    "zero_drift_aux_caliber_today": {
        "note": "★换成 SW 的 build_aux_index (口径零漂移) 后的今日读数★",
        "raw_C14_no_bare": len(today_sw_raw),
        "raw_C14_with_bare": len(today_sw_bare),
        "minus_self_doc": sum(1 for v in today_sw_raw.values() if v["in_self_doc"]),
        "minus_py_only": sum(1 for v in today_sw_raw.values() if v["py_only"]),
        "baseline_same_caliber": len(today_sw_v),
        "baseline_same_caliber_list": sorted(today_sw_v),
        "bare_numbers_excluded_by_C16": sorted(t for t in today_sw_bare if BARE.fullmatch(t)),
    },
    "final_partition_iss333": {
        "baseline_count": mg.BASELINE_COUNT,
        "baseline_tokens": baseline_now,
        "c17_non_designator": c17_now,
        "unlisted_new_hazard": unlisted,
        "final_C14_total": len(final_missing),
        "detail": [{"token": t, "rule": r, "n": v.get("n"), "files": v.get("files", [])[:3]}
                   for t, r, v in pre_c17],
    },
    "registry": {"count": len(mg.MECH_DESIGNATOR_REGISTRY),
                 "fingerprint": mg.REGISTRY_BOARD_FINGERPRINT,
                 "current_fingerprint": hashlib.sha256(("\n".join(sorted(live))).encode()).hexdigest()},
}
os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "baseline_repro.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

lines = []
A = lines.append
A("ISS-333 · MECH 侧位号可达性闸 · 基线复现原始记录")
A(f"机器: yuewuya-RedmiBook-14 · 生成: 2026-11-18")
A(f"扫描面: md={len(md)} py={len(py)} (递归, 闸自身 {GATE_REL} 已排除)")
A(f"live 位号 = {len(live)}")
A("")
A("=== ① ISS-326 设计稿 §5 实测链 · 原样复现 (ISS-326 原型口径) ===")
A(f"原始 C14      ISS-326 建闸日 = 60   |  今天复现 = {len(iss326_raw)}")
A(f"剔本单自污染  ISS-326 = 4        |  今天 = {sum(1 for v in iss326_raw.values() if v['in_self_doc'])}")
A(f"剔 py 变量名  ISS-326 = 40       |  今天 = {sum(1 for v in iss326_raw.values() if v['py_only'])}")
A(f"★基线         ISS-326 = 16       |  ★今天同口径复现 = {len(iss326_v)}")
A("")
A("--- 今天同口径下的 16→%d 逐条明细 ---" % len(iss326_v))
for t in sorted(iss326_v):
    v = iss326_v[t]
    A(f"  {t:28s} n={v['n']:3d}  {v['files'][:2]}")
A("")
A("=== ② 换成 SW 零漂移 aux (口径零漂移) 后的今日读数 ===")
A(f"原始 C14 (不含裸编号) = {len(today_sw_raw)}  (含裸编号 = {len(today_sw_bare)})")
A(f"剔本单自污染 = {sum(1 for v in today_sw_raw.values() if v['in_self_doc'])}   剔 py-only = {sum(1 for v in today_sw_raw.values() if v['py_only'])}")
A(f"★同口径基线 = {len(today_sw_v)}")
for t in sorted(today_sw_v):
    A(f"  {t:28s} {iss326_raw[t]['files'][:2] if t in iss326_raw else ''}")
A("")
A("--- C16 摘掉的裸编号 (MECH 域 = 老板的问题编号 / 坐标轴变量, 不是位号) ---")
for t in sorted(t for t in today_sw_bare if BARE.fullmatch(t)):
    A(f"  {t:10s} n={today_sw_bare[t]['n']:3d}  {today_sw_bare[t]['files'][:2]}")
A("")
A("=== ③ 本单最终分区 (C15 + C16 + C17 落地后) ===")
A(f"最终 C14 总数 = {len(final_missing)}")
A(f"  ▸ 基线 (真隐患) = {len(baseline_now)} 条: {', '.join(baseline_now)}")
A(f"  ▸ C17 (已登记的非位号) = {len(c17_now)} 条: {', '.join(c17_now)}")
A(f"  ▸ 未登记 (新增真隐患) = {len(unlisted)} 条: {', '.join(unlisted) or '无'}")
A("")
A("--- 逐条明细 (token / 出现次数 / 出现位置) ---")
for t, r, v in pre_c17:
    A(f"  {t:28s} rule={r:4s} n={v.get('n')}  {v.get('files', [])[:3]}")
A("")
A("=== ④ 注册表与盘面指纹 ===")
A(f"MECH_DESIGNATOR_REGISTRY = {len(mg.MECH_DESIGNATOR_REGISTRY)} 条")
A(f"建闸日指纹 = {mg.REGISTRY_BOARD_FINGERPRINT}")
A(f"当前指纹   = {out['registry']['current_fingerprint']}")
A(f"★两者一致 = {out['registry']['fingerprint'] == out['registry']['current_fingerprint']}")
with open(os.path.join(OUT, "baseline_repro_raw.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
print("\n".join(lines))
