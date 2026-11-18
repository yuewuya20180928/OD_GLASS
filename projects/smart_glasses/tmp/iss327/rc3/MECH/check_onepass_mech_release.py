#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_onepass_mech_release.py —— ISS-300 「板只改一次」那一趟的 ★MECH 侧【准出汇总闸】★

★★★**★这个闸守的是什么★**★★
  「板只改一次」那一趟 (S6 重出板) 当天, MECH 侧必跑 6 道闸。★**以前是人工一条条跑**★
  ⇒ ★**漏跑一条 ⇒ 没人知道** ★ ⇒ ★**漏掉的那条一旦在收工验收时才炸, 现场只剩两条路:
  ① 当场返工改板 (⇒ 板 md5 变第二次 ⇒ 整趟白跑) · ② 先签收再说 (⇒ 假绿流到下一趟) ★**

  ★★**更要命的是那 6 道里有 2 道是「钉板 md5 闸」** (★`check_board_frame_coords.py` 的 C4 /
  `check_onepass_mech_sync.py` 的 M5★) —— ★**板那一趟当天, 板 md5 会【合法地】变** ⇒
  ★**那 2 道当天必然从绿转红** (★只有走【合法改板通道】·ISS-296 已把通道建好·才走得绿★) ★
  ⇒ ★**当天最容易误读成「板改坏了」→ 去改板凑绿 → 板 md5 变第二次 → 整趟白跑** ★

  ⇒ ★**本闸的定位 = 一条命令给出「结构侧能不能出 Gerber」的结论, 并且 fail-closed:
  任一道红 ⇒ 点名是哪一道红 ⇒ 汇总红; 脚本不存在 / 跑不起来 / 超时 ⇒ 一律算闸红
  (★绝不「没跑就当过」★)** ★

★★【fail-closed 语义 · ★照 `state/gate_check.py` 里 `run_external_gate` 的写法, 不自创★】★★
  ① 脚本不存在     ⇒ 闸红 (rc=None) — ★不许静默跳过★
  ② 跑不起来 (异常) ⇒ 闸红 (rc=None) — ★不许静默跳过★
  ③ 超时 (300s)    ⇒ 闸红 (rc=None) — ★不许静默跳过★
  ④ 跑完 rc≠0     ⇒ 闸红 (rc=该值) + 解析 stdout 的 `[FAIL]` 行当详情
  ⑤ 跑完 rc=0     ⇒ 闸绿
  ★★**清单本身也参与判决**: 6 道里有 1 道不在清单里 ⇒ 汇总闸红 (★「漏跑没人知道」这条路被堵死★) ★★

★**零写板 · 零落表 · 零改既有 MECH 判据脚本** ★
  ★**本闸只【聚合】, 一个判据数字都不改** ★ —— ★**那 6 道闸本体一个字都没动** ★
  ★**(★本闸自己也是 6 道闸之一的话会递归 ⇒ 本闸【不在】那 6 道清单里★) ★

用法:
    python3 MECH/check_onepass_mech_release.py            # rc=0 = MECH 侧 6 道全绿 (★逐条列 rc★)
    python3 MECH/check_onepass_mech_release.py --json     # 机器读
    python3 MECH/check_onepass_mech_release.py --selftest # rc=0 = 反向用例全抓到 (★沙盒副本上跑, 真件一个字节不碰★)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, ".."))

# ==================================================================================================
# ★6 道闸清单 (★顺序 = 收工验收的执行顺序; 一条不许少·少一条 ⇒ 汇总闸红★) ★
# ==================================================================================================
GATES = (
    ("MECH/check_board_frame_coords.py", "坐标系闸 (C1~C4 · ISS-276)"),
    ("MECH/check_demo_struct_truth.py", "结构侧真值闸 (G1~G8 / C21~C22 · ISS-213/224/273)"),
    ("MECH/check_onepass_mech_sync.py", "MECH 侧板侧输入闸 (M1~M5 · ISS-278/286)"),
    ("MECH/check_onepass_struct_crosscheck.py", "结构侧交叉核对闸 (N1~N6 · ISS-290)"),
    ("MECH/board_port_opening_s6_check.py", "S6 板侧开口复算闸 (ISS-271)"),
    ("MECH/check_mech_verdict_freshness.py", "结构结论防漂闸 (F1~F6 · ISS-295)"),
)

# ★清单完备性基准 (★与 GATES 分开定义 ⇒ 「漏一道」这件事本身才能被检出★) ★
MANIFEST_REQUIRED = (
    "MECH/check_board_frame_coords.py",
    "MECH/check_demo_struct_truth.py",
    "MECH/check_onepass_mech_sync.py",
    "MECH/check_onepass_struct_crosscheck.py",
    "MECH/board_port_opening_s6_check.py",
    "MECH/check_mech_verdict_freshness.py",
)

GATE_TIMEOUT = 300           # ★与 state/gate_check.py 的 run_external_gate 同口径 (300s) ★
SANDBOX_REL = os.path.join("tmp", "iss300_release_selftest")


# ==================================================================================================
# 清单完备性 (★漏一道 ⇒ 汇总红★)
# ==================================================================================================
def check_manifest(gates) -> dict:
    rels = [g[0] for g in gates]
    missing = [r for r in MANIFEST_REQUIRED if r not in rels]
    dupes = sorted({r for r in rels if rels.count(r) > 1})
    extra = [r for r in rels if r not in MANIFEST_REQUIRED]
    return {"ok": (not missing) and (not dupes),
            "missing": missing, "dupes": dupes, "extra": extra,
            "n": len(rels)}


# ==================================================================================================
# ★fail-closed 单闸执行 (★照 state/gate_check.py 的 run_external_gate 逐条照抄语义, 不自创★) ★
# ==================================================================================================
def run_gate(root: str, rel: str, name: str, timeout: int = GATE_TIMEOUT) -> dict:
    path = os.path.join(root, rel)
    if not os.path.exists(path):
        return {"ok": False, "rc": None, "rel": rel, "name": name,
                "detail": f"★闸脚本不存在: {path} ⇒ 视为闸红 (不许静默跳过)"}
    try:
        p = subprocess.run([sys.executable, path], cwd=root, capture_output=True,
                           text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"ok": False, "rc": None, "rel": rel, "name": name,
                "detail": f"★闸脚本超时 ({timeout}s) ⇒ 视为闸红"}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "rc": None, "rel": rel, "name": name,
                "detail": f"★闸脚本跑不起来: {e} ⇒ 视为闸红"}
    out = p.stdout or ""
    fails = [ln.strip() for ln in out.splitlines() if ln.strip().startswith("[FAIL]")]
    detail = ("; ".join(fails) if fails else "全部检查项通过")
    if p.returncode != 0 and not fails:
        detail = f"rc={p.returncode} 但未解析出 FAIL 行: " + (p.stderr or out).strip()[-300:]
    return {"ok": p.returncode == 0, "rc": p.returncode, "rel": rel, "name": name,
            "detail": detail}


def run_all(root: str, gates=GATES, timeout: int = GATE_TIMEOUT) -> list:
    return [run_gate(root, rel, name, timeout) for rel, name in gates]


# ==================================================================================================
# 报告
# ==================================================================================================
def _hr(t: str) -> None:
    print("=" * 96)
    print(t)
    print("=" * 96)


def build_report(root: str, gates=GATES, timeout: int = GATE_TIMEOUT) -> dict:
    manifest = check_manifest(gates)
    results = run_all(root, gates, timeout)
    reds = [r for r in results if not r["ok"]]
    ok = manifest["ok"] and not reds
    return {"root": root, "manifest": manifest, "results": results,
            "n_total": len(results), "n_green": len(results) - len(reds),
            "n_red": len(reds), "reds": reds, "ok": ok,
            "rc": 0 if ok else 1}


def print_report(rep: dict) -> None:
    _hr("【MECH 侧「板只改一次」准出汇总闸】 (ISS-300)")
    print(f"  汇总根 (root) = {rep['root']}")
    print(f"  闸数 = {rep['n_total']}  ·  ★清单缺一道 ⇒ 汇总直接红 (不许「没跑就当过」)★")
    m = rep["manifest"]
    if m["missing"]:
        print(f"  ★★ 清单缺: {m['missing']} ⇒ 汇总闸红 ★★")
    if m["dupes"]:
        print(f"  ★★ 清单重复: {m['dupes']} ⇒ 汇总闸红 ★★")
    if m["extra"]:
        print(f"  · 附加闸 (不在基准清单里, 但照样跑、照样参与判决): {m['extra']}")
    print("")

    for i, r in enumerate(rep["results"], 1):
        mark = "✅ 绿" if r["ok"] else "❌ 红"
        rc = "None" if r["rc"] is None else str(r["rc"])
        print(f"  [{i}/{rep['n_total']}] {r['rel']}")
        print(f"        名称: {r['name']}")
        print(f"        rc  : {rc:<5} ⇒ {mark}")
        print(f"        详情: {r['detail']}")
        print("")

    _hr("【汇总】")
    print(f"  6 道闸: 绿 {rep['n_green']} / 红 {rep['n_red']}")
    if rep["reds"]:
        print("  ★★ 红了的那道闸 (★点名·不许只出一个总 rc★) ★★:")
        for i, r in enumerate(rep["reds"], 1):
            rc = "None" if r["rc"] is None else str(r["rc"])
            print(f"     {'❌' if not r['ok'] else '❌'} [{i}] {r['rel']}  —  {r['name']}  (rc={rc})")
            print(f"        详情: {r['detail']}")
    if rep["ok"]:
        print("  ★汇总 rc = 0 ⇒ ★MECH 侧结构可以出 Gerber★")
        print("    (★只代表结构侧 6 道闸全绿; ★不等于整条板链全绿·HW/SW 侧的闸另算★)")
    else:
        print("  ★汇总 rc = 1 ⇒ ★MECH 侧【不准出 Gerber】★")
        print("    ★先看上面【点名】的那道红闸★")
        print("    ★★【板只改一次】铁律: ★★")
        print("      ★**板 md5 当天变更是【合法】的 (走【合法改板通道】·ISS-296) ⇒ 那 2 道「钉板 md5 闸」当天转红是【正常】★")
        print("      ★**但【绝不许】为了「让闸变绿」去改板 / 改闸里的基线 / 放宽判据 ⇒ 板 md5 变第二次 ⇒ 整趟白跑★** ★")
        print("      ★**正确做法: 读那道红闸的详情, 按【合法改板通道】落台账, 让判决源跟着板走★** ★")


# ==================================================================================================
# 沙盒 (★真件一个字节不许动★)
# ==================================================================================================
def md5_of(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def make_sandbox(root: str, tag: str) -> str:
    """★沙盒 = 真目录 + 软链★ —— ★MECH/ 与 HW/ 做【真拷贝】(★沙盒里改的必须是副本★)★"""
    base = os.path.join(root, SANDBOX_REL)
    dst = os.path.join(base, tag)
    if os.path.exists(dst):
        shutil.rmtree(dst)
    os.makedirs(dst, exist_ok=True)
    # ① 顶层: 目录软链 (只读用), 文件拷贝
    for entry in sorted(os.listdir(root)):
        if entry in ("MECH", "HW", "state", "tmp", "logs", ".git", "__pycache__"):
            continue
        src = os.path.join(root, entry)
        d = os.path.join(dst, entry)
        if os.path.isdir(src):
            os.symlink(src, d)
        else:
            shutil.copy2(src, d)
    # ② MECH/ + HW/ = 真拷贝 (★改的是副本★)
    for sub in ("MECH", "HW"):
        shutil.copytree(os.path.join(root, sub), os.path.join(dst, sub),
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "_os_snapshots"))
    # ③ state/ = 真目录 (只放被读到的几个文件; ★不许软链整个 state ⇒ 防误写真盘★)
    sd = os.path.join(dst, "state")
    os.makedirs(os.path.join(sd, "fragments"), exist_ok=True)
    ssrc = os.path.join(root, "state")
    for f in sorted(os.listdir(ssrc)):
        p = os.path.join(ssrc, f)
        if os.path.isfile(p) and f.endswith(".py"):
            shutil.copy2(p, os.path.join(sd, f))
    shutil.copy2(os.path.join(ssrc, "fragments", "mech.yaml"),
                 os.path.join(sd, "fragments", "mech.yaml"))
    return dst


def _mutate_calib_rect(sb: str, key: str, field: str, old: str, new: str) -> bool:
    """★在沙盒副本里篡改 1 个开口坐标常量 (★真件一个字节不许动★)★"""
    p = os.path.join(sb, "MECH", "BOARD_PORT_OPENING_S6_FRAME_CALIBER.md")
    text = open(p, encoding="utf-8").read()
    i = text.find('"%s"' % key)
    if i < 0:
        return False
    j = text.find("rect: {", i)
    if j < 0:
        return False
    k = text.find("}", j)
    if k < 0:
        return False
    seg = text[j:k]
    if ("%s: %s" % (field, old)) not in seg:
        return False
    text2 = text[:j] + seg.replace("%s: %s" % (field, old), "%s: %s" % (field, new), 1) + text[k:]
    open(p, "w", encoding="utf-8").write(text2)
    return True


# ==================================================================================================
# ★自检 (★反向用例 ≥6 条; ★含真件真闸真篡改的沙盒用例·真盘一个字节不许动★) ★
# ==================================================================================================
def selftest(root: str) -> int:
    errs = []
    root = os.path.abspath(root)
    _hr("【自检】check_onepass_mech_release.py 反向用例 (★沙盒副本上跑, 真件一个字节不许碰★)")
    print("  汇总根 = %s" % root)
    print("")

    # ---------------------------------------------------------------- ① 清单完备性
    man = check_manifest(GATES)
    ok1 = man["ok"] and man["n"] == len(MANIFEST_REQUIRED)
    print("  [%s] ① 6 道闸都在清单里 (漏一道 ⇒ 红)"
          % ("OK " if ok1 else "NG "))
    print("        清单 = %d 道 · 漏 = %s · 重复 = %s"
          % (man["n"], man["missing"] or "无", man["dupes"] or "无"))
    if not ok1:
        errs.append("① 清单不完备 (漏=%s 重复=%s)" % (man["missing"], man["dupes"]))

    # ①b 抽掉一道 ⇒ 必须判红
    short = GATES[:-1]
    man2 = check_manifest(short)
    red1b = (not man2["ok"]) and man2["missing"] == [GATES[-1][0]]
    print("  [%s] ①b 抽掉《%s》⇒ 清单判红 (漏=%s)"
          % ("OK " if red1b else "NG ", GATES[-1][0], man2["missing"]))
    if not red1b:
        errs.append("①b 抽掉一道闸后清单没有判红")

    # ---------------------------------------------------------------- ②~⑤ 桩闸 (临时目录)
    import tempfile
    tb = tempfile.mkdtemp(prefix="iss300_stub_")
    try:
        def _stub(name: str, body: str) -> str:
            p = os.path.join(tb, name)
            open(p, "w", encoding="utf-8").write(body)
            return p

        green_p = _stub("stub_green.py", "import sys\nprint('[OK] 桩闸绿')\nsys.exit(0)\n")
        red_p = _stub("stub_red.py",
                      "import sys\nprint('[FAIL] 桩闸红: 我是 STUB_RED_MARKER')\nsys.exit(1)\n")
        raise_p = _stub("stub_raise.py", "raise RuntimeError('boom')\n")
        hang_p = _stub("stub_hang.py", "import time\ntime.sleep(60)\n")
        miss_p = os.path.join(tb, "stub_missing.py")   # ★故意不建★

        green2_p = _stub("stub_green2.py", "import sys\nprint('[OK] 桩闸绿2')\nsys.exit(0)\n")
        stub_gates = [
            (green_p, "桩闸绿"),
            (red_p, "桩闸红 (★被点名的那道★)"),
            (green2_p, "桩闸绿2"),
        ]
        res2 = run_all(tb, stub_gates, 60)
        reds2 = [r for r in res2 if not r["ok"]]
        ok2 = len(reds2) == 1 and reds2[0]["rel"] == red_p and "STUB_RED_MARKER" in reds2[0]["detail"]
        print("  [%s] ② 任一道红 ⇒ 汇总红 + 点名那道红"
              % ("OK " if ok2 else "NG "))
        print("        红的 = %s · 详情含标记 = %s"
              % ([r["rel"] for r in reds2], "STUB_RED_MARKER" in (reds2[0]["detail"] if reds2 else "")))
        if not ok2:
            errs.append("② 桩闸红了但汇总没红 / 没点名")

        res3 = run_gate(tb, miss_p, "★故意不存在的闸★", 60)
        ok3 = (res3["ok"] is False) and (res3["rc"] is None) and ("不存在" in res3["detail"])
        print("  [%s] ③ 脚本不存在 ⇒ 算闸红 (rc=None), 不是跳过"
              % ("OK " if ok3 else "NG "))
        print("        ok=%s rc=%s 详情=%s" % (res3["ok"], res3["rc"], res3["detail"][:80]))
        if not ok3:
            errs.append("③ 脚本不存在没有算闸红")

        res4 = run_gate(tb, raise_p, "★跑不起来的闸★", 60)
        ok4 = (res4["ok"] is False) and (res4["rc"] not in (0, None))
        print("  [%s] ④ 闸脚本抛异常 ⇒ 算闸红 (rc≠0)"
              % ("OK " if ok4 else "NG "))
        print("        ok=%s rc=%s 详情=%s" % (res4["ok"], res4["rc"], res4["detail"][:80]))
        if not ok4:
            errs.append("④ 闸脚本抛异常没有算闸红")

        res5 = run_gate(tb, hang_p, "★超时的闸★", 3)
        ok5 = (res5["ok"] is False) and (res5["rc"] is None) and ("超时" in res5["detail"])
        print("  [%s] ⑤ 闸脚本超时 ⇒ 算闸红 (rc=None)"
              % ("OK " if ok5 else "NG "))
        print("        ok=%s rc=%s 详情=%s" % (res5["ok"], res5["rc"], res5["detail"][:80]))
        if not ok5:
            errs.append("⑤ 闸脚本超时没有算闸红")
    finally:
        shutil.rmtree(tb, ignore_errors=True)

    # ---------------------------------------------------------------- ⑥ 真沙盒真篡改 (★本单最要紧的一条★)
    print("")
    print("  ★★ ⑥ 真件真闸真篡改 (★沙盒副本: MECH/ + HW/ 真拷贝, 真盘一个字节不许动★) ★★")
    sb = make_sandbox(root, "case_real_reverse")
    base = run_all(sb, GATES, GATE_TIMEOUT)
    base_reds = [r for r in base if not r["ok"]]
    base_ok = not base_reds
    print("        ⑥-0 沙盒基线: 绿 %d / 红 %d %s"
          % (len(base) - len(base_reds), len(base_reds),
             "" if base_ok else " (★基线就红 ⇒ 反向用例无意义★)"))
    for r in base_reds:
        print("              基线红: %s · %s" % (r["rel"], r["detail"][:120]))
    if not base_ok:
        errs.append("⑥ 沙盒基线不绿 ⇒ 反向用例无意义")

    calib_rel = os.path.join("MECH", "BOARD_PORT_OPENING_S6_FRAME_CALIBER.md")
    p_real = os.path.join(root, calib_rel)
    p_sb = os.path.join(sb, calib_rel)
    real_before = md5_of(p_real)
    orig_text = open(p_sb, encoding="utf-8").read()
    sb_before = md5_of(p_sb)

    mutated = _mutate_calib_rect(sb, "port_open_uart_bench", "y0", "66.300", "52.000")
    sb_after = md5_of(p_sb)
    red = run_all(sb, GATES, GATE_TIMEOUT)
    reds = [r for r in red if not r["ok"]]
    named = [r for r in reds if r["rel"] == "MECH/check_board_frame_coords.py"]
    others_green = all(r["ok"] for r in red if r["rel"] != "MECH/check_board_frame_coords.py")
    ok6 = mutated and sb_before != sb_after and len(reds) == 1 and named and others_green
    print("        [%s] ⑥ 篡改 1 个开口坐标常量 (port_open_uart_bench.y0 66.300 ⇒ 52.000)"
              % ("OK " if ok6 else "NG "))
    print("              真改了 = %s (md5 %s ⇒ %s)"
              % (sb_before != sb_after, sb_before[:8], sb_after[:8]))
    print("              汇总 = 红 %d 道: %s" % (len(reds), [r["rel"] for r in reds]))
    print("              点名到 = %s · 其余 5 道仍绿 = %s"
          % ([r["rel"] for r in named], others_green))
    for r in reds:
        print("              详情: %s" % r["detail"][:200])
    if not ok6:
        errs.append("⑥ 沙盒篡改后汇总没有红 / 没点名 / 其余闸受影响")

    # 恢复 ⇒ 必须回绿
    open(p_sb, "w", encoding="utf-8").write(orig_text)
    green = run_all(sb, GATES, GATE_TIMEOUT)
    green_reds = [r for r in green if not r["ok"]]
    real_after = md5_of(p_real)
    ok6b = (not green_reds) and (real_before == real_after)
    print("        [%s] ⑥b 恢复 ⇒ 回绿 (红 %d 道) · ★真件 md5 不变 = %s (%s ⇒ %s)"
              % ("OK " if ok6b else "NG ", len(green_reds), real_before == real_after,
                 real_before[:12], real_after[:12]))
    if not ok6b:
        errs.append("⑥b 恢复后没有回绿, 或真件 md5 变了")

    shutil.rmtree(sb, ignore_errors=True)

    # ---------------------------------------------------------------- 收尾
    print("")
    if errs:
        _hr("【自检结论】❌ 有 %d 条没抓到" % len(errs))
        for e in errs:
            print("   ✗ %s" % e)
        return 1
    _hr("【自检结论】✅ 一致 (反向用例全抓到 · 真盘一个字节不许动)")
    return 0


# ==================================================================================================
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="ISS-300 MECH 侧「板只改一次」准出汇总闸")
    ap.add_argument("--root", default=PROJ, help="★项目根 (默认本脚本所在项目; 沙盒复现用)")
    ap.add_argument("--json", action="store_true", help="机器读")
    ap.add_argument("--selftest", action="store_true", help="★反向用例自检 (沙盒副本上跑)")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest(args.root)

    root = os.path.abspath(args.root)
    rep = build_report(root, GATES, GATE_TIMEOUT)
    if args.json:
        print(json.dumps(rep, ensure_ascii=False, indent=2, default=str))
    else:
        print_report(rep)
    return rep["rc"]


if __name__ == "__main__":
    sys.exit(main())
