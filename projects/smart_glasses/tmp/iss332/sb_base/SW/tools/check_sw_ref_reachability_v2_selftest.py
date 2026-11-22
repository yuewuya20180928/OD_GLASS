#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=================================================================================================
SW/tools/check_sw_ref_reachability_v2_selftest.py — ISS-332 · 收紧版 SW 位号可达性闸的【自测脚本】
=================================================================================================
★**它是 `check_sw_ref_reachability_v2.py` 的配套自测·不是第二道闸**★ (★v2 挂链时跑的是 v2 本体·不是本文件★)
★**真件 `check_sw_ref_reachability.py` 一个字节没动** ★ (★本文件只【只读 import】它·用来逐字比对读数★)

★**四组自测 (★任务书 §② 第 ② 件的原文口径★)**:
  ① 正向        : 现状真件树跑 ⇒ rc=0 · 读数与【真件闸】逐字相同 (OK 78 / MISSING 3 / NET 9 / DOC 23)
  ② 4 条洗白面  : RT-5~RT-8 ⇒ 每条必须 rc≠0 且【点名那条 token】
  ③ 3 条对照    : CTL-1~CTL-3 (真隐患改个【板/网表里从来没有过的形状】) ⇒ 必须仍被抓住 (⇒ 证明不是把闸调死)
  ④ 假绿用例    : 判据分支匹配不上时必须【红】, 不许静悄悄不查了

★**用法**: `python3 SW/tools/check_sw_ref_reachability_v2_selftest.py --selftest` (★带不带这个 flag 都跑同一套★)
★**沙盒**: 只写 `tmp/iss332/selftest/` (★真拷贝·写前 assert not os.path.islink★) · 真盘一个字节都不写 ★
=================================================================================================
"""
import importlib.util
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))
SANDBOX = os.path.join(PROJ, "tmp", "iss332", "selftest")
V2_PATH = os.path.join(HERE, "check_sw_ref_reachability_v2.py")
REAL_PATH = os.path.join(HERE, "check_sw_ref_reachability.py")

# ★**用例表 (★与 logs/iss332/iss332_repro.py 的 CASES 同源·★口径一致★)** ★
#   (id, 旧 token, 新 token, 期望 v2 rc, 期望点名 token, 用途)
WASH_CASES = [
    ("RT-5", "TP_TEMP", "U_TEMP_1", 1, "U_TEMP_1",
     "★C1 面: 真隐患被换成【一个板上真存在的位号名】⇒ 旧闸命中 C1 ⇒ 判绿 (洗白成功)"),
    ("RT-6", "TP_TEMP", "TP_temp", 1, "TP_temp",
     "★C7 面: 真隐患改成【含小写】⇒ 旧闸命中 C7 ⇒ 判绿 (洗白成功)"),
    ("RT-7", "TP_TEMP", "SW_TEMP_ISSX", 1, "SW_TEMP_ISSX",
     "★C13 面: 真隐患改成【SW_ 前缀】⇒ 旧闸命中 C13 ⇒ 判绿 (洗白成功)"),
    ("RT-8", "TP_TEMP", "TP_TEMP_", 1, "TP_TEMP_",
     "★C8 面: 真隐患改成【以 _ 结尾】⇒ 旧闸命中 C8 ⇒ 判绿 (洗白成功)"),
]
CTRL_CASES = [
    ("CTL-1", "TP_TEMP", "TP_TEMP_ISSX", 1, "TP_TEMP_ISSX",
     "★对照: 真隐患改成【板/网表里从来没有过的形状】⇒ 仍被 C14 抓住"),
    ("CTL-2", "TP_INT", "TP_INT_ISSX", 1, "TP_INT_ISSX",
     "★对照: 第二条基线真患同款处理 ⇒ 仍被 C14 抓住"),
    ("CTL-3", "CONN_USB", "CONN_USB_ISSX", 1, "CONN_USB_ISSX",
     "★对照: 第三条基线真患同款处理 ⇒ 仍被 C14 抓住"),
]

EXPECT_REAL = {"DESIGNATOR_OK": 78, "DESIGNATOR_MISSING": 3, "NET_NAME": 9, "DOC_INTERNAL": 23}


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _guard(path, what=""):
    p = os.path.abspath(path)
    if os.path.islink(p):
        raise RuntimeError("★[ABORT] 要写的路径是软链 ⇒ 拒绝写穿: %s (%s)" % (p, what))
    return p


def _run_v2(v2, root):
    """在沙盒根上跑 v2 的主判定 ⇒ (rc, [FAIL] 行, 报告全文)"""
    try:
        res = v2.analyze(root)
    except v2.InputError as exc:
        return 2, ["[FAIL] fail-closed: %s" % exc], ""
    res["_live"] = res["live_refs"]
    rep = v2.format_report(res, verbose=False)
    fails = [ln.strip() for ln in rep.splitlines() if ln.strip().startswith("[FAIL]")]
    ok = (res["baseline_ok"] and not res["drift"] and not res["laundered"]
          and not res["probe_failures"] and res["ledger_ok"])
    return (0 if ok else 1), fails, rep


def _counts(v2, res):
    c = {}
    for r in res["rows"]:
        c[r["cls"]] = c.get(r["cls"], 0) + 1
    return c


def _build_base(v2, real):
    """★造沙盒基树: 真拷贝输入面 + 把板面 U_TEMP 改名成 U_TEMP_1 (板+网表+文档三侧同改)
       ⇒ 使 U_TEMP_1 成为【板上真存在】的位号名 (RT-5 的洗白面需要这个前提)★"""
    if os.path.isdir(SANDBOX):
        shutil.rmtree(SANDBOX)
    os.makedirs(SANDBOX, exist_ok=True)
    base = os.path.join(SANDBOX, "sb_base")
    real._copy_input_surface(PROJ, base)
    bp = _guard(os.path.join(base, "HW", "PCB", "demo_mainboard.kicad_pcb"), "board")
    txt = open(bp, encoding="utf-8").read()
    old = '(property "Reference" "U_TEMP"'
    assert txt.count(old) == 1, "板面 U_TEMP 引用数异常: %d" % txt.count(old)
    open(bp, "w", encoding="utf-8").write(txt.replace(old, '(property "Reference" "U_TEMP_1"'))
    for rel in real.NETLIST_CSVS:
        real._rewrite_ref(_guard(os.path.join(base, rel), "netlist"), "U_TEMP", "U_TEMP_1")
    for fn in sorted(os.listdir(os.path.join(base, "SW"))):
        if not fn.endswith(".md"):
            continue
        p = _guard(os.path.join(base, "SW", fn), "doc")
        txt = open(p, encoding="utf-8").read()
        if "U_TEMP" in txt:
            open(p, "w", encoding="utf-8").write(re.sub(r"\bU_TEMP\b", "U_TEMP_1", txt))
    return base


def _inject(base, case_dir, old, new):
    """把沙盒里 SW/*.md 的 old token 换掉 (词边界·逐个文件真写·写前守卫)"""
    if os.path.isdir(case_dir):
        shutil.rmtree(case_dir)
    shutil.copytree(base, case_dir, symlinks=False)
    pat = re.compile(r"\b%s\b" % re.escape(old))
    nf = nr = 0
    for fn in sorted(os.listdir(os.path.join(case_dir, "SW"))):
        if not fn.endswith(".md"):
            continue
        p = _guard(os.path.join(case_dir, "SW", fn), "inject")
        txt = open(p, encoding="utf-8").read()
        if old not in txt:
            continue
        cnt = len(pat.findall(txt))
        open(p, "w", encoding="utf-8").write(pat.sub(new, txt))
        nf += 1
        nr += cnt
    assert nf >= 1, "沙盒里找不到 %s" % old
    return nf, nr


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    print("=" * 92)
    print("# ISS-332 · 收紧版 SW 位号可达性闸 · 自测 (★四组★)")
    print("# 真件闸只读 (只 import + 用它自带的沙盒工具) · 沙盒在 tmp/iss332/selftest/ · 真盘一个字节都不写")
    print("=" * 92)

    v2 = _load(V2_PATH, "v2")
    real = _load(REAL_PATH, "real_gate")
    results = []

    def rec(gid, name, ok, detail):
        results.append((gid, name, bool(ok), detail))
        print("  %s %-10s %s" % ("✅" if ok else "❌", gid, name))
        if detail:
            print("        %s" % detail)

    # ─────────────────────────────────────────────────────────────────────
    # ① 正向: 现状真件树跑 ⇒ rc=0 · 读数与真件闸逐字相同
    # ─────────────────────────────────────────────────────────────────────
    print("\n【① 正向 · 现状真件树】")
    rc_v2, fails_v2, _rep = _run_v2(v2, PROJ)
    try:
        res_real = real.analyze(PROJ)
        rows_real = {(r["token"], r["cls"], r["rule"], r["note"]) for r in res_real["rows"]}
        c_real = _counts(real, res_real)
    except real.InputError as exc:
        rows_real, c_real = set(), {}
        rec("G1", "真件闸读数抽取", False, "★真件闸读不到: %s★" % exc)
    res_v2 = v2.analyze(PROJ)
    rows_v2 = {(r["token"], r["cls"], r["rule"], r["note"]) for r in res_v2["rows"]}
    c_v2 = _counts(v2, res_v2)
    rec("G1-1", "v2 在真件树上 rc=0", rc_v2 == 0, "实际 rc=%d (★期望 0★)" % rc_v2)
    rec("G1-2", "v2 读数 = 期望值 78/3/9/23",
        c_v2.get("DESIGNATOR_OK") == 78 and c_v2.get("DESIGNATOR_MISSING") == 3
        and c_v2.get("NET_NAME") == 9 and c_v2.get("DOC_INTERNAL") == 23,
        "实际 OK=%s MISSING=%s NET=%s DOC=%s" % (c_v2.get("DESIGNATOR_OK"), c_v2.get("DESIGNATOR_MISSING"),
                                                c_v2.get("NET_NAME"), c_v2.get("DOC_INTERNAL")))
    rec("G1-3", "真件闸读数 = 期望值 78/3/9/23",
        c_real.get("DESIGNATOR_OK") == 78 and c_real.get("DESIGNATOR_MISSING") == 3
        and c_real.get("NET_NAME") == 9 and c_real.get("DOC_INTERNAL") == 23,
        "实际 OK=%s MISSING=%s NET=%s DOC=%s" % (c_real.get("DESIGNATOR_OK"), c_real.get("DESIGNATOR_MISSING"),
                                                c_real.get("NET_NAME"), c_real.get("DOC_INTERNAL")))
    diff = rows_real ^ rows_v2
    rec("G1-4", "逐 token 分类/规则/理由 与真件闸【逐字相同】", not diff,
        ("★差异 %d 条: %s★" % (len(diff), sorted(diff)[:6])) if diff else "★113 个 token 逐条相同★")

    # ─────────────────────────────────────────────────────────────────────
    # 沙盒基树
    # ─────────────────────────────────────────────────────────────────────
    base = _build_base(v2, real)
    rc_base, _f, _r = _run_v2(v2, base)
    rec("G0", "★沙盒基树在 v2 下仍绿 (★证明下面 ② ③ 组的红不是基树带来的★)", rc_base == 0,
        "基树 rc=%d (★期望 0★)" % rc_base)

    # ─────────────────────────────────────────────────────────────────────
    # ② 4 条洗白面 / ③ 3 条对照
    # ─────────────────────────────────────────────────────────────────────
    def run_cases(gid, cases, label):
        print("\n【%s】" % label)
        for cid, old, new, exp_rc, name_tok, purpose in cases:
            case_dir = os.path.join(SANDBOX, "case_" + cid)
            _inject(base, case_dir, old, new)
            rc, fails, _rep = _run_v2(v2, case_dir)
            named = any(name_tok in ln for ln in fails)
            rec(gid + "-" + cid, "%s  rc≠0 且点名 `%s`" % (cid, name_tok),
                (rc == exp_rc and rc != 0 and named),
                "rc=%d (★期望 %d★) · 点名=%s (★期望 是★) · 目的: %s" % (rc, exp_rc, "是" if named else "否", purpose))
            for ln in fails:
                print("        %s" % ln[:190])
            shutil.rmtree(case_dir, ignore_errors=True)

    run_cases("G2", WASH_CASES, "② 4 条洗白面反向用例 (RT-5~RT-8) · 每条必须红 + 点名")
    run_cases("G3", CTRL_CASES, "③ 3 条「真隐患变个形状」反向用例 (CTL-1~CTL-3) · 必须仍被抓住")

    # ─────────────────────────────────────────────────────────────────────
    # ④ 假绿用例: 判据分支匹配不上时必须红, 不许静悄悄不查了
    # ─────────────────────────────────────────────────────────────────────
    print("\n【④ 假绿用例】")

    # ④-1 输入面读不到 ⇒ fail-closed 判红 (rc=2)
    case_dir = os.path.join(SANDBOX, "case_FG1")
    _inject(base, case_dir, "TP_TEMP", "TP_TEMP")
    os.remove(_guard(os.path.join(case_dir, "HW", "PCB", "demo_mainboard.kicad_pcb"), "rm-board"))
    rc, fails, _r = _run_v2(v2, case_dir)
    rec("G4-1", "输入面读不到 ⇒ 必须红 (fail-closed)", rc != 0, "rc=%d (★期望 ≠0★)" % rc)
    shutil.rmtree(case_dir, ignore_errors=True)

    # ④-2 未登记的形状 token ⇒ 必须红 (登记制闸门不许静悄悄放过)
    case_dir = os.path.join(SANDBOX, "case_FG2")
    _inject(base, case_dir, "TP_TEMP", "TP_TEMP")
    p = _guard(os.path.join(case_dir, "SW", "SW_TIMING_REVIEW.md"), "fg2")
    with open(p, "a", encoding="utf-8") as fh:
        fh.write("\n<!-- ISS332 FG-2 -->\nprobe shape token: `SW_zz_probe` 形状像豁免但不在册\n")
    rc, fails, _r = _run_v2(v2, case_dir)
    named = any("SW_zz_probe" in ln for ln in fails)
    rec("G4-2", "未登记的形状 token ⇒ 必须红且点名", rc != 0 and named,
        "rc=%d (★期望 ≠0★) · 点名=%s" % (rc, "是" if named else "否"))
    shutil.rmtree(case_dir, ignore_errors=True)

    # ④-3 静悄悄把【登记制闸门】拆掉 ⇒ ② 组的【形状面】证据必须消失 (⇒ 证明本自测不是假绿)
    case_dir = os.path.join(SANDBOX, "case_FG3")
    _inject(base, case_dir, "TP_TEMP", "TP_temp")
    orig_gate = v2._shape_gate
    try:
        # ★sabotage: 把登记制闸门拆掉 (= 形状类豁免无条件放行) ⇒ 等于“把 v2 悄悄退回真件闸的老样子”★
        v2._shape_gate = lambda token, rule, cls, note: (cls, rule, note)
        rc_sab, fails_sab, _r = _run_v2(v2, case_dir)
    finally:
        v2._shape_gate = orig_gate
    shape_gone = not any(ln.startswith("[FAIL] 位号引用解析不到") and "TP_temp" in ln for ln in fails_sab)
    rec("G4-3", "★登记制闸门被静悄悄拆掉 ⇒ RT-6 的【形状面·C14】证据消失 (⇒ 本自测能抓到这种假绿★)",
        shape_gone,
        "拆闸后 RT-6 rc=%d · C14 FAIL 行还在=%s (★期望 否★ ⇒ 证明 ② 组确实在读登记制闸门·不是摆设★)"
        % (rc_sab, "是" if not shape_gone else "否"))
    shutil.rmtree(case_dir, ignore_errors=True)

    # ─────────────────────────────────────────────────────────────────────
    print("\n" + "=" * 92)
    ok = all(r[2] for r in results)
    npass = sum(1 for r in results if r[2])
    for gid, name, good, detail in results:
        if not good:
            print("❌ 不通过: %s %s · %s" % (gid, name, detail))
    print("★自测结果: %d/%d 通过 · %s" % (npass, len(results), "✔ 全过" if ok else "✘ 有不过的"))
    print("=" * 92)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
