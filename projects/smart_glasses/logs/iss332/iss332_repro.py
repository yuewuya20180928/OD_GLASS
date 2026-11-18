#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iss332_repro.py —— ISS-332 · 第 8 道闸 (SW 位号引用可达性) 4 条【洗白面】复现 + 对照
================================================================================
★**零写板 · 零落表 · 零改真件闸** ★
  · 真件 `SW/tools/check_sw_ref_reachability.py` 一个字节都不改 (只 import, 只读)
  · 沙盒只写 `tmp/iss332/` (真拷贝, 零软链) · 证据只写 `logs/iss332/`
  · 沙盒机制直接用【真件自带的】`_copy_input_surface` / `_rewrite_ref` 两条工具 (★不自己另发明★)

★**为什么必须复现** ★: ★ISS-327 cont2 实测出 4 条洗白面 (C1/C7/C8/C13) ⇒ 但那是在【改名后沙盒】上量的
  ⇒ 本单必须在【当前真件树】上把 4 条洗白面 + 3 条【真隐患变形状】对照一起重测一遍 ⇒ 给出【期望/实际/判决】三列 ★

用法:
    python3 logs/iss332/iss332_repro.py                 # 只跑真件闸 (RT-5..RT-8 + CTL-1..3)
    python3 logs/iss332/iss332_repro.py --with-v2       # 再跑收紧版 v2 (对比判决)
"""
from __future__ import annotations

import argparse
import importlib.util
import os
import re
import shutil
import subprocess
import sys

PROJ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SB = os.path.join(PROJ, "tmp", "iss332")
LOG = os.path.join(PROJ, "logs", "iss332")
REAL_GATE = os.path.join(PROJ, "SW", "tools", "check_sw_ref_reachability.py")
V2_GATE = os.path.join(PROJ, "SW", "tools", "check_sw_ref_reachability_v2.py")


def load_real_gate():
    """只读 import 真件闸 (★不执行任何写动作★)"""
    spec = importlib.util.spec_from_file_location("real_gate", REAL_GATE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def guard_write(path, what=""):
    p = os.path.abspath(path)
    if os.path.islink(p):
        raise RuntimeError("★[ABORT] 要写的路径是软链 ⇒ 拒绝写穿: %s (%s)" % (p, what))
    return p


def inject(sandbox, old, new):
    """把沙盒里 SW/*.md 的 old token 换掉 (词边界·逐个文件真写·写前守卫)"""
    nfiles = nrepl = 0
    pat = re.compile(r"\b%s\b" % re.escape(old))
    for fn in sorted(os.listdir(os.path.join(sandbox, "SW"))):
        if not fn.endswith(".md"):
            continue
        p = guard_write(os.path.join(sandbox, "SW", fn), "inject")
        txt = open(p, encoding="utf-8").read()
        if old not in txt:
            continue
        cnt = len(pat.findall(txt))
        open(p, "w", encoding="utf-8").write(pat.sub(new, txt))
        nfiles += 1
        nrepl += cnt
    return nfiles, nrepl


def run_gate(gate, root, extra=()):
    cmd = [sys.executable, gate, "--root", root] + list(extra)
    r = subprocess.run(cmd, cwd=PROJ, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return r.returncode, r.stdout


def readings(out):
    """从闸的 stdout 里抽读数 (★分类统计 5 行 + 基线行 + MISSING 清单★)"""
    stat = {}
    for cls in ("DESIGNATOR_OK", "DESIGNATOR_DRIFT", "DESIGNATOR_MISSING", "NET_NAME", "DOC_INTERNAL"):
        m = re.search(r"^\s+%s\s+(\d+)$" % cls, out, re.M)
        stat[cls] = int(m.group(1)) if m else -1
    m = re.search(r"DESIGNATOR_MISSING` 实测 = (\d+) 条 · 允许上限 = (\d+) 条", out)
    base = (int(m.group(1)), int(m.group(2))) if m else (-1, -1)
    missing = re.findall(r"^\s+★?基线内·已登记★?\s+(\S+)\s+\(", out, re.M)
    missing += re.findall(r"^\s+★★超基线★★\s+(\S+)\s+\(", out, re.M)
    fails = [ln.strip() for ln in out.splitlines() if ln.strip().startswith("[FAIL]")]
    return stat, base, missing, fails


def missing_tokens(out):
    """★闸报告里【真隐患 (C14)】那段列出的 token (按出现顺序)★"""
    m = re.search(r"【★真隐患 \(C14\).*?\n(.*?)\n\s*\n", out, re.S)
    if not m:
        return []
    return re.findall(r"^\s+★?★?[^★]*★?\s*(\S+)\s+\(\S+:\d+\)", m.group(1), re.M)


# ════════════════════════════════════════════════════════════════════
# §CASES · 用例表
#   (id, 基树, 旧 token, 新 token, 期望[真件闸 rc], 期望[v2 rc], 期望点名 token, 目的)
#   ★RT-5~RT-8 = ISS-327 cont2 实测出的 4 条【洗白面】★
#   ★CTL-1~CTL-3 = ISS-327 RT-1~RT-3 那类【真隐患改成板/网表里从来没有过的形状】(必须仍被 C14 抓住)★
# ════════════════════════════════════════════════════════════════════
CASES = [
    ("RT-5", "TP_TEMP", "U_TEMP_1", 0, 1, "U_TEMP_1",
     "★C1 面: 真隐患被换成【一个板上真存在的位号名】⇒ 命中 C1 ⇒ 判绿 (洗白成功)"),
    ("RT-6", "TP_TEMP", "TP_temp", 0, 1, "TP_temp",
     "★C7 面: 真隐患改成【含小写】⇒ 命中 C7 ⇒ 判绿 (洗白成功)"),
    ("RT-7", "TP_TEMP", "SW_TEMP_ISSX", 0, 1, "SW_TEMP_ISSX",
     "★C13 面: 真隐患改成【SW_ 前缀】⇒ 命中 C13 ⇒ 判绿 (洗白成功)"),
    ("RT-8", "TP_TEMP", "TP_TEMP_", 0, 1, "TP_TEMP_",
     "★C8 面: 真隐患改成【以 _ 结尾】⇒ 命中 C8 ⇒ 判绿 (洗白成功)"),
    ("CTL-1", "TP_TEMP", "TP_TEMP_ISSX", 1, 1, "TP_TEMP_ISSX",
     "★对照: 真隐患改成【板/网表里从来没有过的形状】⇒ 仍被 C14 抓住 (真件闸就红)"),
    ("CTL-2", "TP_INT", "TP_INT_ISSX", 1, 1, "TP_INT_ISSX",
     "★对照: 第二条基线真隐患同款处理 ⇒ 仍被 C14 抓住"),
    ("CTL-3", "CONN_USB", "CONN_USB_ISSX", 1, 1, "CONN_USB_ISSX",
     "★对照: 第三条基线真隐患同款处理 ⇒ 仍被 C14 抓住"),
]


def build_base(g):
    """★造场: 用【真件闸自带的 _copy_input_surface】把输入面真拷贝进沙盒★
       ★基树 = 再把 U_TEMP 改名成 U_TEMP_1 (板+网表+文档三侧同改)
       ⇒ 使 U_TEMP_1 成为【板上真存在】的位号名 (RT-5 的洗白面需要这个前提)★"""
    sb = os.path.join(SB, "sb_base")
    if os.path.isdir(sb):
        shutil.rmtree(sb)
    g._copy_input_surface(PROJ, sb)
    bp = guard_write(os.path.join(sb, "HW", "PCB", "demo_mainboard.kicad_pcb"), "board")
    txt = open(bp, encoding="utf-8").read()
    old = '(property "Reference" "U_TEMP"'
    assert txt.count(old) == 1, "板面 U_TEMP 引用数异常: %d" % txt.count(old)
    open(bp, "w", encoding="utf-8").write(txt.replace(old, '(property "Reference" "U_TEMP_1"'))
    for rel in g.NETLIST_CSVS:
        n = g._rewrite_ref(guard_write(os.path.join(sb, rel), "netlist"), "U_TEMP", "U_TEMP_1")
        assert n >= 1, "网表 %s 里 U_TEMP 行数为 0" % rel
    for fn in sorted(os.listdir(os.path.join(sb, "SW"))):
        if not fn.endswith(".md"):
            continue
        p = guard_write(os.path.join(sb, "SW", fn), "doc")
        txt = open(p, encoding="utf-8").read()
        if "U_TEMP" in txt:
            open(p, "w", encoding="utf-8").write(re.sub(r"\bU_TEMP\b", "U_TEMP_1", txt))
    return sb


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--with-v2", action="store_true", help="同时跑收紧版 v2")
    args = ap.parse_args()

    g = load_real_gate()
    os.makedirs(SB, exist_ok=True)
    os.makedirs(LOG, exist_ok=True)

    print("=" * 96)
    print("# ISS-332 · 第 8 道闸 4 条【洗白面】复现 (★期望 / 实际 / 判决 三列★)")
    print("# 真件闸只读 (只 import + 用它自带的沙盒工具) · 沙盒在 tmp/iss332/ · 证据在 logs/iss332/")
    print("=" * 96)

    base = build_base(g)
    rc0, out0 = run_gate(REAL_GATE, base)
    stat0, base0, miss0, fail0 = readings(out0)
    print("\n【基树自检】%s\n           真件闸 rc=%d · 分类统计=%s\n           基线读数=%s · 真隐患清单=%s"
          % (base, rc0, stat0, base0, miss0))
    open(os.path.join(LOG, "10_base_tree_readings.txt"), "w", encoding="utf-8").write(out0)

    rows = []
    for cid, old, new, exp_real, exp_v2, name_tok, purpose in CASES:
        sb = os.path.join(SB, "case_" + cid)
        if os.path.isdir(sb):
            shutil.rmtree(sb)
        shutil.copytree(base, sb, symlinks=False)
        nf, nr = inject(sb, old, new)
        assert nf >= 1, "%s: 沙盒里找不到 %s" % (cid, old)
        rc_r, out_r = run_gate(REAL_GATE, sb)
        stat_r, base_r, miss_r, fail_r = readings(out_r)
        row = {"id": cid, "old": old, "new": new, "purpose": purpose,
               "exp_real": exp_real, "act_real": rc_r, "files": nf, "repl": nr,
               "real_missing": miss_r, "real_fails": fail_r}
        if args.with_v2 and os.path.isfile(V2_GATE):
            rc_v, out_v = run_gate(V2_GATE, sb)
            stat_v, base_v, miss_v, fail_v = readings(out_v)
            row.update({"exp_v2": exp_v2, "act_v2": rc_v, "v2_missing": miss_v,
                        "v2_fails": re.findall(r"\[FAIL\][^\n]*", out_v),
                        "v2_names": name_tok in out_v})
            open(os.path.join(LOG, "2%s_%s_v2.txt" % (cid, cid)), "w", encoding="utf-8").write(out_v)
        open(os.path.join(LOG, "2%s_%s_real.txt" % (cid, cid)), "w", encoding="utf-8").write(out_r)
        rows.append(row)
        shutil.rmtree(sb, ignore_errors=True)

    print("\n" + "=" * 96)
    print("# ★核心证据表: 4 条洗白面 + 3 条对照 (期望 / 实际 / 判决)★")
    print("=" * 96)
    hdr = "%-6s %-12s -> %-14s | %-9s | %-9s | %-8s | %s"
    print(hdr % ("用例", "旧 token", "新 token", "期望[真件]", "实际[真件]", "判决", "真件闸真隐患清单"))
    print("-" * 96)
    n_green = n_red = 0
    for r in rows:
        verdict = "✔ 符合" if r["act_real"] == r["exp_real"] else "✘ 不符"
        if r["act_real"] == 0:
            n_green += 1
        else:
            n_red += 1
        print(hdr % (r["id"], r["old"], r["new"], "rc=%d" % r["exp_real"], "rc=%d" % r["act_real"],
                     verdict, ",".join(r["real_missing"]) or "(空)"))
    print("-" * 96)
    print("★4 条洗白面 (RT-5~RT-8) 现在绿 = %d 条 / 3 条对照 (CTL-1~CTL-3) 现在红 = %d 条" % (n_green, n_red))
    if args.with_v2:
        print("\n" + "=" * 96)
        print("# ★收紧版 v2 判决表★")
        print("=" * 96)
        print(hdr % ("用例", "旧 token", "新 token", "期望[v2]", "实际[v2]", "判决", "v2 是否点名该 token"))
        print("-" * 96)
        for r in rows:
            ok = (r["act_v2"] == r["exp_v2"]) and (r["exp_v2"] == 1) and r["v2_names"]
            print(hdr % (r["id"], r["old"], r["new"], "rc=%d" % r["exp_v2"], "rc=%d" % r["act_v2"],
                         "✔ 抓住+点名" if ok else "✘ 不符",
                         ("是" if r["v2_names"] else "★否★")))
            for fl in r["v2_fails"]:
                print("        %s" % fl[:160])
    return 0


if __name__ == "__main__":
    sys.exit(main())
