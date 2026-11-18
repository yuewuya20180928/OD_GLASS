#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_onepass_sw_release.py —— ISS-335 · 「板只改一次」那一趟的 ★SW 侧【准出汇总闸】★

★★★**★这个闸守的是什么★**★★
  「板只改一次」那一趟 (S1 位号改名 + S6 重出板) 当天, SW 侧必跑 10 道闸。
  ★**以前是人工一条条跑**★ ⇒ ★**漏跑一条 ⇒ 没人知道**★ ⇒ ★**漏掉的那条一旦在收工验收时才炸,
  现场只剩两条路: ① 当场返工改板 (⇒ 板 md5 变第二次 ⇒ 整趟白跑) · ② 先签收再说 (⇒ 假绿流到下一趟)★**

  ★★**更要命的是: 板那一趟当天, 板 md5 会【合法地】变一次** ⇒ 若 SW 侧钉了板 md5 的闸当天必然从绿转红
  ⇒ ★**当天最容易误读成「板改坏了」→ 去改板凑绿 → 板 md5 变第二次 → 整趟白跑**★

  ⇒ ★**本闸的定位 = 一条命令给出「SW 侧能不能出 Gerber」的结论, 并且 fail-closed:
  任一道红 ⇒ 点名是哪一道红 ⇒ 汇总红; 脚本不存在 / 跑不起来 / 超时 ⇒ 一律算闸红
  (★绝不「没跑就当过」★)** ★

★★【fail-closed 语义 · ★照 `state/gate_check.py` 里 `run_external_gate` 的写法, 不自创★】★★
  ① 脚本不存在      ⇒ 闸红 (rc=None) — ★不许静默跳过★
  ② 跑不起来 (异常) ⇒ 闸红 (rc=None) — ★不许静默跳过★
  ③ 超时 (300s)     ⇒ 闸红 (rc=None) — ★不许静默跳过★
  ④ 跑完 rc≠0      ⇒ 闸红 (rc=该值) + 解析 stdout 的 `[FAIL]` / `❌` 行当详情
  ⑤ 跑完 rc=0      ⇒ 闸绿
  ★★**清单本身也参与判决**: 10 道里有 1 道不在清单里 ⇒ 汇总闸红
     (★「漏跑没人知道」这条路被堵死★) ★★

★**清单完备性基准 = ISS-321 实测表那 10 道** (★交卷页 `HANDOFF/2026-11-18_sw-lead_ISS321_SW侧改名安全性体检.md`
  §B1-3 的逐闸读数表★) ⇒ ★**链外那 4 道也收进来**★ ⇒ ★**少写一道 ⇒ 自己的闸先把自己抓住**★

★**零写板 · 零落表 · 零改既有 16 道 SW 闸 · 零改 `state/gate_check.py`** ★
  ★**本闸只【聚合】, 一个判据数字都不改** ★ —— ★**那 10 道闸本体一个字都没动** ★
  ★**(★本闸自己不在那 10 道清单里 ⇒ 不会递归★)** ★

★**TMPDIR 约定**: ★**子进程一律把 TMPDIR / TMP / TEMP 指到项目内** (`tmp/iss335_tmp`) ★
  —— ★本机系统临时目录带配额且本用户配额已到顶 ⇒ 不指会 EDQUOT 假红 (ISS-297 / ISS-299 两单都踩过)★ ★

用法:
    python3 SW/tools/check_onepass_sw_release.py              # rc=0 = SW 侧 10 道全绿 (★逐条列 rc★)
    python3 SW/tools/check_onepass_sw_release.py --json       # 机器读
    python3 SW/tools/check_onepass_sw_release.py --selftest   # rc=0 = 反向用例全抓到 (★沙盒副本上跑, 真件一个字节不碰★)
    python3 SW/tools/check_onepass_sw_release.py --ref-gate v2  # ★把位号可达性闸换成 v2 (★main 拍过之后才用★)
    python3 SW/tools/check_onepass_sw_release.py --ref-gate both # ★v1 + v2 都进判决★
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))     # SW/tools/ → 项目根

# ==================================================================================================
# ★10 道闸清单 (★顺序 = 收工验收的执行顺序; 一条不许少 · 少一条 ⇒ 汇总闸红★) ★
#   ★**基线 = ISS-321 实测表那 10 道** (★交卷页 §B1-3 逐闸读数表·★本机实读★) ★
#   ★**含 4 道【链外闸】** (★今天不在 `state/gate_check.py` 链上 ⇒ 没人会注意到它们红了★): ★
#     #4 check_demo_panel_spec.py · #8 check_shutdown_semantics.py
#     #9 check_timing_review_adc_sync.py · #10 timing_check.py ★
# ==================================================================================================
REF_V1 = "SW/tools/check_sw_ref_reachability.py"            # ★ISS-318 · v1 · 已在链上★
REF_V2 = "SW/tools/check_sw_ref_reachability_v2.py"         # ★ISS-332 · v2 · 已 verified · ★还没挂链★

GATES = (
    ("SW/tools/check_onepass_sw_sync.py",
     "SW 侧板侧输入 / 合法改板闸 (ISS-279/298/321)", ()),
    (REF_V1,
     "SW 侧位号引用可达性闸 v1 (ISS-318)", ()),
    ("SW/tools/check_landing_trace_obligation.py",
     "SW 侧落表留痕义务闸 (ISS-315)", ()),
    ("SW/tools/check_demo_panel_spec.py",
     "SW 侧面板规格 / 三方对账闸 (ISS-275/315) ★链外★", ()),
    ("SW/tools/check_demo_panel_spec_r6_selftest.py",
     "SW 侧 R6 判决源反向用例 (ISS-309) ★裸跑★", ("--tmpdir", "@TMPDIR@")),
    ("SW/tools/check_demo_panel_spec_r6_chainjudge_selftest.py",
     "SW 侧 R6 链头落表单号交叉核对反向用例 (ISS-312) ★裸跑★", ("--tmpdir", "@TMPDIR@")),
    ("SW/tools/check_demo_panel_spec_r6_hardprot_iss315_selftest.py",
     "SW 侧 R6 硬保护路径反向用例 (ISS-315) ★裸跑★", ("--tmpdir", "@TMPDIR@")),
    ("SW/tools/check_shutdown_semantics.py",
     "SW 侧关机语义闸 (SW/SHUTDOWN_SEMANTICS_SPEC.md) ★链外★", ()),
    ("SW/tools/check_timing_review_adc_sync.py",
     "SW 侧时序评审 ADC 同步闸 (SW/SW_TIMING_REVIEW.md) ★链外★", ()),
    ("SW/tools/timing_check.py",
     "SW 侧上电 / 复位时序预算闸 (网表 → 时序) ★链外★", ()),
)

# ★清单完备性基准 (★与 GATES 分开定义 ⇒ 「漏一道」这件事本身才能被检出★) ★
MANIFEST_BASE = tuple(rel for rel, _n, _a in GATES)

# ★影子道 (★默认只跑、只打印读数、★不参与最终判决★) ★
#   ★理由: v2 比 v1 严 (ISS-332 收了 4 条洗白面) ⇒ 板那一趟当天若 v1 绿 / v2 红 ⇒ 那是【更严的判据】
#     而不是【板坏了】 ⇒ ★默认不许它单独把汇总闸拉红 (★否则当天会被误读成「板改坏了」★) ★
SHADOW_GATES = (
    (REF_V2, "SW 侧位号引用可达性闸 v2 (ISS-332) ★影子道·默认不参与判决★", ()),
)

GATE_TIMEOUT = 300           # ★与 state/gate_check.py 的 run_external_gate 同口径 (300s) ★
SANDBOX_REL = os.path.join("tmp", "iss335_release_selftest")
TMPDIR_REL = os.path.join("tmp", "iss335_tmp")
GATE_DIR_REL = os.path.join("tmp", "iss335_gates")


# ==================================================================================================
# 清单 / 基准 (★--ref-gate 决定位号可达性闸列 v1 还是 v2★)
# ==================================================================================================
def gates_for(ref_gate: str):
    """★返回 (判决清单, 清单完备性基准, 影子清单)★"""
    if ref_gate == "v1":
        return GATES, MANIFEST_BASE, SHADOW_GATES
    if ref_gate == "v2":
        g = tuple((REF_V2 if rel == REF_V1 else rel, name, a) for rel, name, a in GATES)
        base = tuple(REF_V2 if rel == REF_V1 else rel for rel in MANIFEST_BASE)
        shadow = ((REF_V1, "SW 侧位号引用可达性闸 v1 (ISS-318) ★影子道·默认不参与判决★", ()),)
        return g, base, shadow
    if ref_gate == "both":
        g = GATES + ((REF_V2, "SW 侧位号引用可达性闸 v2 (ISS-332) ★判决清单内★", ()),)
        base = MANIFEST_BASE + (REF_V2,)
        return g, base, ()
    raise SystemExit("★--ref-gate 只许 v1 / v2 / both")


def check_manifest(gates, required) -> dict:
    """★清单完备性 (★漏一道 ⇒ 汇总红★) ★"""
    rels = [g[0] for g in gates]
    missing = [r for r in required if r not in rels]
    dupes = sorted({r for r in rels if rels.count(r) > 1})
    extra = [r for r in rels if r not in required]
    return {"ok": (not missing) and (not dupes),
            "missing": missing, "dupes": dupes, "extra": extra,
            "n": len(rels), "n_required": len(required)}


# ==================================================================================================
# ★fail-closed 单闸执行 (★照 state/gate_check.py 的 run_external_gate 逐条照抄语义, 不自创★) ★
# ==================================================================================================
def child_env(root: str) -> dict:
    """★子进程环境: TMPDIR 一律指项目内 (★本机系统临时目录配额已到顶 ⇒ 不指会 EDQUOT 假红★) ★"""
    env = dict(os.environ)
    tmp = os.path.join(root, TMPDIR_REL)
    try:
        os.makedirs(tmp, exist_ok=True)
    except OSError:
        pass
    env["TMPDIR"] = tmp
    env["TMP"] = tmp
    env["TEMP"] = tmp
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def _fail_lines(out: str, err: str) -> list:
    """★抓失败详情行: `[FAIL] ...` 或带 ❌ 的行 (★SW 侧两种标记都有·实测★) ★"""
    lines = []
    for raw in (out or "").splitlines() + (err or "").splitlines():
        s = raw.strip()
        if not s:
            continue
        if s.startswith("[FAIL]") or "[FAIL]" in s or "❌" in s:
            lines.append(s)
    return lines


def run_gate(root: str, rel: str, name: str, timeout: int = GATE_TIMEOUT, args=()) -> dict:
    path = os.path.join(root, rel)
    if not os.path.exists(path):
        return {"ok": False, "rc": None, "rel": rel, "name": name, "argv": [],
                "detail": "★闸脚本不存在: %s ⇒ 视为闸红 (不许静默跳过)" % path}
    tmpdir = os.path.join(root, GATE_DIR_REL)
    argv = [sys.executable, path] + [a.replace("@TMPDIR@", tmpdir) for a in (args or ())]
    try:
        os.makedirs(tmpdir, exist_ok=True)
    except OSError:
        pass
    env = child_env(root)
    try:
        p = subprocess.run(argv, cwd=root, capture_output=True, text=True,
                           timeout=timeout, env=env)
    except subprocess.TimeoutExpired:
        return {"ok": False, "rc": None, "rel": rel, "name": name, "argv": argv[1:],
                "detail": "★闸脚本超时 (%ds) ⇒ 视为闸红" % timeout}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "rc": None, "rel": rel, "name": name, "argv": argv[1:],
                "detail": "★闸脚本跑不起来: %s ⇒ 视为闸红" % e}
    out = p.stdout or ""
    fails = _fail_lines(out, p.stderr or "")
    detail = ("; ".join(fails[:5]) if fails else "全部检查项通过")
    if p.returncode != 0 and not fails:
        detail = "rc=%s 但未解析出失败行: " % p.returncode + (p.stderr or out).strip()[-300:]
    return {"ok": p.returncode == 0, "rc": p.returncode, "rel": rel, "name": name,
            "argv": argv[1:], "detail": detail}


def run_all(root: str, gates, timeout: int = GATE_TIMEOUT) -> list:
    """★★gates 允许 2 元组 (rel, name) 或 3 元组 (rel, name, args)★★"""
    out = []
    for g in gates:
        rel, name = g[0], g[1]
        args = g[2] if len(g) > 2 else ()
        out.append(run_gate(root, rel, name, timeout, args))
    return out


# ==================================================================================================
# 报告
# ==================================================================================================
def _hr(t: str) -> None:
    print("=" * 96)
    print(t)
    print("=" * 96)


def build_report(root: str, gates=GATES, required=MANIFEST_BASE, shadow=SHADOW_GATES,
                 timeout: int = GATE_TIMEOUT, shadow_strict: bool = False) -> dict:
    manifest = check_manifest(gates, required)
    results = run_all(root, gates, timeout)
    shadow_results = run_all(root, shadow, timeout) if shadow else []
    reds = [r for r in results if not r["ok"]]
    shadow_reds = [r for r in shadow_results if not r["ok"]]
    ok = manifest["ok"] and not reds and (not shadow_strict or not shadow_reds)
    return {"root": root, "manifest": manifest, "results": results,
            "shadow_results": shadow_results, "shadow_strict": shadow_strict,
            "n_total": len(results), "n_green": len(results) - len(reds),
            "n_red": len(reds), "reds": reds,
            "n_shadow": len(shadow_results), "shadow_reds": shadow_reds,
            "ok": ok, "rc": 0 if ok else 1}


def print_report(rep: dict) -> None:
    _hr("【SW 侧「板只改一次」准出汇总闸】 (ISS-335)")
    print("  汇总根 (root) = %s" % rep["root"])
    print("  闸数 = %d  ·  ★清单缺一道 ⇒ 汇总直接红 (不许「没跑就当过」)★" % rep["n_total"])
    m = rep["manifest"]
    if m["missing"]:
        print("  ★★ 清单缺: %s ⇒ 汇总闸红 ★★" % m["missing"])
    if m["dupes"]:
        print("  ★★ 清单重复: %s ⇒ 汇总闸红 ★★" % m["dupes"])
    if m["extra"]:
        print("  · 附加闸 (不在基准清单里, 但照样跑、照样参与判决): %s" % m["extra"])
    print("")

    for i, r in enumerate(rep["results"], 1):
        mark = "✅ 绿" if r["ok"] else "❌ 红"
        rc = "None" if r["rc"] is None else str(r["rc"])
        print("  [%d/%d] %s" % (i, rep["n_total"], r["rel"]))
        print("        名称: %s" % r["name"])
        print("        调用: %s %s" % (os.path.basename(r["argv"][0]) if r["argv"] else "-",
                                   " ".join(r["argv"][1:]) if r["argv"] else ""))
        print("        rc  : %-5s ⇒ %s" % (rc, mark))
        print("        详情: %s" % r["detail"])
        print("")

    if rep["shadow_results"]:
        _hr("【影子道 (★默认【不参与判决】· 只跑 + 只打印读数★)】")
        for i, r in enumerate(rep["shadow_results"], 1):
            mark = "✅ 绿" if r["ok"] else "❌ 红"
            rc = "None" if r["rc"] is None else str(r["rc"])
            print("  [影子 %d/%d] %s" % (i, rep["n_shadow"], r["rel"]))
            print("        名称: %s" % r["name"])
            print("        rc  : %-5s ⇒ %s" % (rc, mark))
            print("        详情: %s" % r["detail"])
            print("")
        print("  ★影子道红了怎么办: ★**不等于板坏了**★ ⇒ ★**先看它点名的是哪条判据**★")
        print("    · v2 比 v1 严 (ISS-332 收了 4 条洗白面) ⇒ v1 绿 / v2 红 ⇒ 通常是【v2 抓到了 v1 放过的东西】")
        print("    · ★**默认口径下影子道不把汇总闸拉红**★ (★--shadow-strict 才参与判决★)")
        print("    · ★**绝不许因为影子道红就去改板凑绿**★ ⇒ ★停了 · 回 main · 板 md5 只许变一次★")
        print("")

    _hr("【汇总】")
    print("  %d 道闸: 绿 %d / 红 %d" % (rep["n_total"], rep["n_green"], rep["n_red"]))
    if rep["reds"]:
        print("  ★★ 红了的那道闸 (★点名·不许只出一个总 rc★) ★★:")
        for i, r in enumerate(rep["reds"], 1):
            rc = "None" if r["rc"] is None else str(r["rc"])
            print("     ❌ [%d] %s  —  %s  (rc=%s)" % (i, r["rel"], r["name"], rc))
            print("        详情: %s" % r["detail"])
    if rep["ok"]:
        print("  ★汇总 rc = 0 ⇒ ★SW 侧软件可以出 Gerber★")
        print("    (★只代表 SW 侧这 %d 道闸全绿; ★不等于整条板链全绿·HW/MECH 侧的闸另算★)"
              % rep["n_total"])
    else:
        print("  ★汇总 rc = 1 ⇒ ★SW 侧【不准出 Gerber】★")
        print("    ★先看上面【点名】的那道红闸★")
        print("    ★★【板只改一次】铁律: ★★")
        print("      ★**板 md5 当天变更是【合法】的 (走【合法改板通道】·ISS-296) ⇒ 钉板 md5 的闸当天转红是【正常】★")
        print("      ★**但【绝不许】为了「让闸变绿」去改板 / 改闸里的基线 / 放宽判据 ⇒ 板 md5 变第二次 ⇒ 整趟白跑★** ★")
        print("      ★**正确做法: 读那道红闸的详情, 按【合法改板通道】落台账, 让判决源跟着板走★** ★")
        print("      ★**红了 = 停下来 = 回 main; 不是「红了 = 去改板」★** ★")


# ==================================================================================================
# 沙盒 (★真件一个字节不许动★)
# ==================================================================================================
def md5_of(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _copytree(src: str, dst: str) -> None:
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))


def make_sandbox(root: str, tag: str) -> str:
    """★沙盒 = 项目根 + 软链, SW/ 与 state/ 做【真拷贝】 (★沙盒里改的必须是副本★) ★"""
    base = os.path.join(root, SANDBOX_REL)
    dst = os.path.join(base, tag)
    if os.path.exists(dst):
        shutil.rmtree(dst)
    os.makedirs(dst, exist_ok=True)
    # ① 顶层: 除 SW/ 与 state/ 外全部做符号链接 (只读用)
    for entry in sorted(os.listdir(root)):
        if entry in ("SW", "state", "tmp", "logs", ".git", "__pycache__", ".trash"):
            continue
        src = os.path.join(root, entry)
        d = os.path.join(dst, entry)
        if os.path.isdir(src):
            os.symlink(src, d)
        else:
            shutil.copy2(src, d)
    # ② SW/ = 真拷贝 (★改的是副本★)
    _copytree(os.path.join(root, "SW"), os.path.join(dst, "SW"))
    # ③ state/ = 白名单拷贝 (★只拷闸真正读得到的那几个·不拷 600+ MB 的 .bak★)
    sd = os.path.join(dst, "state")
    os.makedirs(sd, exist_ok=True)
    ssrc = os.path.join(root, "state")
    for f in sorted(os.listdir(ssrc)):
        p = os.path.join(ssrc, f)
        if os.path.isfile(p) and f.endswith((".py", ".sh", ".md")):
            shutil.copy2(p, os.path.join(sd, f))
    for sub in ("fragments", "dispatch_briefs", "outbox", "_os_snapshots"):
        s = os.path.join(ssrc, sub)
        if os.path.isdir(s):
            _copytree(s, os.path.join(sd, sub))
    shutil.copy2(os.path.join(ssrc, "issue_log.yaml"), os.path.join(sd, "issue_log.yaml"))
    return dst


# ==================================================================================================
# ★自检 (★反向用例 ≥6 条 + ≥1 条正向对照; ★真件真闸真篡改在沙盒副本上跑★) ★
# ==================================================================================================
def selftest(root: str) -> int:
    errs = []
    root = os.path.abspath(root)
    _hr("【自检】check_onepass_sw_release.py 反向用例 (★沙盒副本上跑, 真件一个字节不许碰★)")
    print("  汇总根 = %s" % root)
    print("")

    # ---------------------------------------------------------------- ① 清单完备性 (正向对照之一)
    gates, required, shadow = gates_for("v1")
    man = check_manifest(gates, required)
    ok1 = man["ok"] and man["n"] == len(required) == 10
    print("  [%s] ① 10 道闸都在清单里 (漏一道 ⇒ 红)"
          % ("OK " if ok1 else "NG "))
    print("        清单 = %d 道 · 基准 = %d 道 · 漏 = %s · 重复 = %s"
          % (man["n"], man["n_required"], man["missing"] or "无", man["dupes"] or "无"))
    if not ok1:
        errs.append("① 清单不完备 (漏=%s 重复=%s)" % (man["missing"], man["dupes"]))

    # ①b 抽掉一道 ⇒ 必须判红 (★反向用例 1★)
    short = tuple(g for g in gates if g[0] != "SW/tools/check_shutdown_semantics.py")
    man2 = check_manifest(short, required)
    red1b = (not man2["ok"]) and man2["missing"] == ["SW/tools/check_shutdown_semantics.py"]
    print("  [%s] ①b 抽掉《check_shutdown_semantics.py》⇒ 清单判红 (漏=%s)"
          % ("OK " if red1b else "NG ", man2["missing"]))
    if not red1b:
        errs.append("①b 抽掉一道闸后清单没有判红")

    # ①c 基准自身必须是 ISS-321 那 10 道 (★清单完备性基准的完备性★)
    iss321 = {
        "SW/tools/check_onepass_sw_sync.py", "SW/tools/check_sw_ref_reachability.py",
        "SW/tools/check_landing_trace_obligation.py", "SW/tools/check_demo_panel_spec.py",
        "SW/tools/check_demo_panel_spec_r6_selftest.py",
        "SW/tools/check_demo_panel_spec_r6_chainjudge_selftest.py",
        "SW/tools/check_demo_panel_spec_r6_hardprot_iss315_selftest.py",
        "SW/tools/check_shutdown_semantics.py", "SW/tools/check_timing_review_adc_sync.py",
        "SW/tools/timing_check.py",
    }
    ok1c = set(required) >= iss321
    print("  [%s] ①c 清单完备性基准 ⊇ ISS-321 实测表那 10 道 (差集 = %s)"
          % ("OK " if ok1c else "NG ", sorted(iss321 - set(required)) or "无"))
    if not ok1c:
        errs.append("①c 清单完备性基准不含 ISS-321 那 10 道")

    # ---------------------------------------------------------------- ②~⑤ 桩闸 (临时目录在项目内)
    print("")
    tb = os.path.join(root, os.path.join(SANDBOX_REL, "stubs"))
    if os.path.exists(tb):
        shutil.rmtree(tb, ignore_errors=True)
    os.makedirs(tb, exist_ok=True)
    try:
        def _stub(name: str, body: str) -> str:
            p = os.path.join(tb, name)
            with open(p, "w", encoding="utf-8") as f:
                f.write(body)
            return p

        green_p = _stub("stub_green.py", "import sys\nprint('[OK] 桩闸绿')\nsys.exit(0)\n")
        red_p = _stub("stub_red.py",
                      "import sys\nprint('[FAIL] 桩闸红: 我是 STUB_RED_MARKER')\nsys.exit(1)\n")
        raise_p = _stub("stub_raise.py", "raise RuntimeError('boom')\n")
        hang_p = _stub("stub_hang.py", "import time\ntime.sleep(60)\n")
        miss_p = os.path.join(tb, "stub_missing.py")   # ★故意不建★

        stub_gates = [(green_p, "桩闸绿"), (red_p, "桩闸红 (★被点名的那道★)")]
        res2 = run_all(tb, stub_gates, 60)
        reds2 = [r for r in res2 if not r["ok"]]
        ok2 = len(reds2) == 1 and reds2[0]["rel"] == red_p and "STUB_RED_MARKER" in reds2[0]["detail"]
        print("  [%s] ② 任一道红 ⇒ 汇总红 + 点名那道红 + 解析 [FAIL] 行当详情"
              % ("OK " if ok2 else "NG "))
        print("        红的 = %s · 详情含标记 = %s"
              % ([os.path.basename(r["rel"]) for r in reds2],
                 "STUB_RED_MARKER" in (reds2[0]["detail"] if reds2 else "")))
        if not ok2:
            errs.append("② 桩闸红了但汇总没红 / 没点名 / 没解析出 [FAIL] 行")

        res3 = run_gate(tb, miss_p, "★故意不存在的闸★", 60)
        ok3 = (res3["ok"] is False) and (res3["rc"] is None) and ("不存在" in res3["detail"])
        print("  [%s] ③ 脚本不存在 ⇒ 算闸红 (rc=None), 不是跳过"
              % ("OK " if ok3 else "NG "))
        print("        ok=%s rc=%s 详情=%s" % (res3["ok"], res3["rc"], res3["detail"][:90]))
        if not ok3:
            errs.append("③ 脚本不存在没有算闸红")

        res4 = run_gate(tb, raise_p, "★跑不起来的闸★", 60)
        ok4 = (res4["ok"] is False) and (res4["rc"] is not None)
        print("  [%s] ④ 闸脚本抛异常 ⇒ 算闸红 (rc≠None·不是 0)"
              % ("OK " if ok4 else "NG "))
        print("        ok=%s rc=%s 详情=%s" % (res4["ok"], res4["rc"], res4["detail"][:90]))
        if not ok4:
            errs.append("④ 闸脚本抛异常没有算闸红")

        res5 = run_gate(tb, hang_p, "★超时的闸★", 3)
        ok5 = (res5["ok"] is False) and (res5["rc"] is None) and ("超时" in res5["detail"])
        print("  [%s] ⑤ 闸脚本超时 ⇒ 算闸红 (rc=None)"
              % ("OK " if ok5 else "NG "))
        print("        ok=%s rc=%s 详情=%s" % (res5["ok"], res5["rc"], res5["detail"][:90]))
        if not ok5:
            errs.append("⑤ 闸脚本超时没有算闸红")

        # ---------------------------------------------------------------- ⑥ R6 三道必须裸跑 (★最大的坑★)
        print("")
        print("  ★★ ⑥ 三道 R6 selftest 闸【必须裸跑】(★ISS-318 §B4-2 实测: 它们没有 --selftest 参数★)")
        r6 = ["SW/tools/check_demo_panel_spec_r6_selftest.py",
              "SW/tools/check_demo_panel_spec_r6_chainjudge_selftest.py",
              "SW/tools/check_demo_panel_spec_r6_hardprot_iss315_selftest.py"]
        args_ok = all("--selftest" not in (a or ()) for _r, _n, a in gates)
        print("        [%s] ⑥a 判决清单里没有任何一道带 --selftest 参数"
              % ("OK " if args_ok else "NG "))
        if not args_ok:
            errs.append("⑥a 判决清单里有闸带了 --selftest")
        pitfall_ok = True
        for rel in r6:
            p = os.path.join(root, rel)
            r = subprocess.run([sys.executable, p, "--selftest"], cwd=root,
                               capture_output=True, text=True, timeout=120,
                               env=child_env(root))
            hit = (r.returncode != 0)
            print("        [%s] ⑥b 手动加 --selftest ⇒ %s ⇒ ★证明「传 --selftest 会假红」这条坑是真的★"
                  % ("OK " if hit else "NG ", "rc=%s" % r.returncode))
            if not hit:
                pitfall_ok = False
        if not pitfall_ok:
            errs.append("⑥b 三道 R6 闸加 --selftest 没有报错 ⇒ 坑的结论不成立")
    finally:
        shutil.rmtree(tb, ignore_errors=True)

    # ---------------------------------------------------------------- ⑦ TMPDIR 必须指项目内
    print("")
    env = child_env(root)
    ok7 = env.get("TMPDIR", "").startswith(root) and env.get("TMPDIR", "") != "/tmp"
    print("  [%s] ⑦ 子进程 TMPDIR 指项目内 (TMPDIR=%s)"
          % ("OK " if ok7 else "NG ", env.get("TMPDIR")))
    if not ok7:
        errs.append("⑦ TMPDIR 没有指到项目内")

    # ---------------------------------------------------------------- ⑧ 真沙盒真篡改 (★本单最要紧的一条★)
    print("")
    print("  ★★ ⑧ 真件真闸真篡改 (★沙盒副本: SW/ 与 state/ 真拷贝, 真盘一个字节不许动★) ★★")
    sb = make_sandbox(root, "case_real_reverse")
    probe_rel = "SW/ONETRIP_SW_RENAME_SAFETY.md"
    p_real = os.path.join(root, probe_rel)
    p_sb = os.path.join(sb, probe_rel)
    real_before = md5_of(p_real)
    try:
        base = run_all(sb, gates, GATE_TIMEOUT)
        base_reds = [r for r in base if not r["ok"]]
        base_ok = not base_reds
        print("        ⑧-0 沙盒基线: 绿 %d / 红 %d %s"
              % (len(base) - len(base_reds), len(base_reds),
                 "" if base_ok else " (★基线就红 ⇒ 反向用例无意义★)"))
        for r in base_reds:
            print("              基线红: %s · %s" % (r["rel"], r["detail"][:120]))
        if not base_ok:
            errs.append("⑧ 沙盒基线不绿 ⇒ 反向用例无意义")

        orig_text = open(p_sb, encoding="utf-8").read()
        sb_before = md5_of(p_sb)
        # ★在沙盒副本里写一条【板上有、SW 文档里没有】的位号引用 ⇒ 模仿「板改了但 SW 文档没跟上」★
        with open(p_sb, "a", encoding="utf-8") as f:
            f.write("\n★ISS-335 自检探针★ U_ISS335_PROBE (★只写在沙盒副本里★)\n")
        sb_after = md5_of(p_sb)

        red = run_all(sb, gates, GATE_TIMEOUT)
        reds = [r for r in red if not r["ok"]]
        named = [r for r in reds if r["rel"] == REF_V1]
        ok8 = (sb_before != sb_after) and len(reds) >= 1 and bool(named)
        print("        [%s] ⑧ 篡改 1 份 SW 文档 (加 1 条位号引用) ⇒ 汇总红 + 点名到位号可达性闸"
              % ("OK " if ok8 else "NG "))
        print("              真改了 = %s (md5 %s ⇒ %s)"
              % (sb_before != sb_after, sb_before[:8], sb_after[:8]))
        print("              汇总 = 红 %d 道: %s" % (len(reds), [r["rel"] for r in reds]))
        print("              点名到 = %s" % [r["rel"] for r in named])
        for r in reds:
            print("              详情: %s" % r["detail"][:200])
        if not ok8:
            errs.append("⑧ 沙盒篡改后汇总没有红 / 没点名到位号可达性闸")

        # 恢复 ⇒ 必须回绿
        with open(p_sb, "w", encoding="utf-8") as f:
            f.write(orig_text)
        green = run_all(sb, gates, GATE_TIMEOUT)
        green_reds = [r for r in green if not r["ok"]]
        real_after = md5_of(p_real)
        ok8b = (not green_reds) and (real_before == real_after)
        print("        [%s] ⑧b 恢复 ⇒ 回绿 (红 %d 道) · ★真件 md5 不变 = %s (%s ⇒ %s)"
              % ("OK " if ok8b else "NG ", len(green_reds), real_before == real_after,
                 real_before[:12], real_after[:12]))
        if not ok8b:
            errs.append("⑧b 恢复后没有回绿, 或真件 md5 变了")
    finally:
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
    ap = argparse.ArgumentParser(description="ISS-335 SW 侧「板只改一次」准出汇总闸")
    ap.add_argument("--root", default=PROJ, help="★项目根 (默认本脚本上两级; 沙盒复现用)")
    ap.add_argument("--json", action="store_true", help="机器读")
    ap.add_argument("--selftest", action="store_true", help="★反向用例自检 (沙盒副本上跑)")
    ap.add_argument("--ref-gate", default="v1", choices=["v1", "v2", "both"],
                    help="★清单里的位号可达性闸: v1 (默认·ISS-321 实测基线) / v2 / both★")
    ap.add_argument("--shadow-strict", action="store_true",
                    help="★让影子道 (v2) 也参与判决 (默认: 只跑 + 只打印读数)★")
    ap.add_argument("--shadow-off", action="store_true", help="★不跑影子道 (更省时间)★")
    ap.add_argument("--timeout", type=int, default=GATE_TIMEOUT, help="★单闸超时 (默认 300s)★")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest(args.root)

    root = os.path.abspath(args.root)
    gates, required, shadow = gates_for(args.ref_gate)
    if args.shadow_off:
        shadow = ()
    rep = build_report(root, gates, required, shadow, args.timeout, args.shadow_strict)
    if args.json:
        print(json.dumps(rep, ensure_ascii=False, indent=2, default=str))
    else:
        print_report(rep)
    return rep["rc"]


if __name__ == "__main__":
    sys.exit(main())
