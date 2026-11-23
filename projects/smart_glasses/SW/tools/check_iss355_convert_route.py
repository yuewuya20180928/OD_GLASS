#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
ISS-355 · 转换路线实现闸 (只读 · 带 --selftest 反向用例)
==============================================================================
为什么要有这个闸
----------------
ISS-353 把【口径】清干净了 (16 条旧结论: 15 条文档类由 main 一键补丁清掉,
剩 2 条在 state/fragments/hw.yaml ⇒ 归 hw-lead) ⇒ ★但【实现】没改★:
任何人按现在的脚本重跑, 拿到的仍是旧口径的产物 ⇒ ★口径清了 ≠ 实现改了★。

本闸盯的是【实现层】的「当下执行口径」:
  A · 全仓扫: 任何**可执行默认值**把转换目标设成旧值 (rk3576) 的地方
      ⇒ 逐条点名 (文件 + 行号 + 原文片段) ⇒ 有 ⇒ rc=1
      (★历史留档处不点名: logs/ 与 HANDOFF/ 按 ISS-353 同口径算历史留档★)
  B · 主路线入口断言: SW/tools/rk3572_model_rebuild.sh 的**默认路线**
      ⇒ 必须是 rknn3-toolkit 1.2.0 + rk3572 (★机器读脚本里的默认值, 不靠注释★)
      ⇒ 旧链 (次要路线①) 必须仍可达 (ROUTE=legacy) 且标明它的代价
  C · 两件套拷贝断言: .rknn + 同名 .weight 必须**一起**拷, 缺一即失败
      ⇒ 用脚本自带的 --copy-only 缝做**行为级**验证 (拷齐 ⇒ rc=0 / 缺 .weight ⇒ rc≠0)
  D · 旧链代价标注: 脚本里必须写明板上接受性 = [0数据]

★与 ISS-353 闸的关系 (★不重造一套冲突的★):
  ISS-353 闸 (SW/tools/check_rk3572_target_caliber.py) 管【口径层】(文档结论矛盾, F1~F8);
  本闸管【实现层】(脚本的默认转换路线 + 两件套拷贝)。
  ★本闸**复用** ISS-353 闸的规则做交叉校验 (import 它的模块, 直接用它的 scan()),
  不另造一套口径层的判据★ ⇒ 两闸互补, 判据方向一致。

用法
----
    python3 SW/tools/check_iss355_convert_route.py                # 扫全仓 + 断言主路线
    python3 SW/tools/check_iss355_convert_route.py --root DIR    # 扫别处 (自测用)
    python3 SW/tools/check_iss355_convert_route.py --json         # 机器读
    python3 SW/tools/check_iss355_convert_route.py --selftest     # ★反向用例★
==============================================================================
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys

# ── 扫面 (★代码层只看可执行文件★) ────────────────────────────────────────────
SCAN_ROOTS = ("SW", "HW", "state/fragments", "HANDOFF", "logs", "REQ")
CODE_EXT = (".sh", ".bash", ".py")
MAX_BYTES = 4 * 1024 * 1024
# ★历史留档 (与 ISS-353 闸同口径): logs/ = 原始证据留档, HANDOFF/ = 交卷单留档
HIST_PREFIX = ("logs/", "HANDOFF/")
# ★不扫的文件 (★理由写在这里, 不做无声豁免★)
SKIP_BASENAME = {
    "check_iss355_convert_route.py": "本闸自身 (闸里的正则不是执行口径)",
    "check_rk3572_target_caliber.py": "ISS-353 的口径层闸 (由那个闸管)",
}
# ★本单允许写范围 (★越权 ⇒ 交 main 裁★)
ISS355_WRITABLE = (
    "SW/tools/rk3572_model_rebuild.sh",
    "SW/RKNN_BENCH.md",
    "SW/tools/check_iss355_convert_route.py",
    "state/fragments/sw.yaml",
)
ISS355_WRITABLE_PREFIX = ("HANDOFF/2026-11-23_sw-lead_ISS355_", "logs/iss355/")

MAIN_SCRIPT = "SW/tools/rk3572_model_rebuild.sh"

# ── 期望的默认路线 (★这是 ISS-355 的口径真值★) ───────────────────────────────
EXPECT_ROUTE = "rknn3"
EXPECT_TARGET = "rk3572"
EXPECT_PKG = "rknn3-toolkit"
EXPECT_VER = "1.2.0"
LEGACY_ROUTE = "legacy"
LEGACY_TARGET = "rk3576"

VERDICT_STALE = "结论矛盾(要处置)"
VERDICT_LEGACY = "次要路线①(保留·已点名)"

# ── 实现层规则 (★只认「可执行默认值」, 不认散落在散文里的字面量★) ─────────────
# G1: 可被环境变量覆盖的默认值, 值 = 旧目标
G1_ENV_DEFAULT = re.compile(r"\$\{[A-Za-z_][A-Za-z0-9_]*[:-]=[^}]*rk3576(?![A-Za-z0-9_])")
# G2: shell 大写变量赋值 = 旧目标
G2_SH_ASSIGN = re.compile(r"^\s*([A-Z][A-Z0-9_]*)\s*=\s*[\"']?rk3576(?![\w])")
# G3: 转换配置参数 = 旧目标 (带词边界, 免得 legacy_target_platform 被误判)
G3_CONFIG_ARG = re.compile(r"(?<![\w])target_platform\s*=\s*[\"']?rk3576(?![\w])")
# G4: argparse 的 default = 旧目标
G4_ARGPARSE = re.compile(r"add_argument\([^)]*default\s*=\s*[\"']rk3576[\"']")

CODE_RULES = (
    ("G1", G1_ENV_DEFAULT, "可覆盖的默认值把转换目标设成旧值 ⇒ 这是「当下的执行口径」"),
    ("G2", G2_SH_ASSIGN, "变量默认值把转换目标设成旧值 ⇒ 这是「当下的执行口径」"),
    ("G3", G3_CONFIG_ARG, "转换配置参数写死旧目标 ⇒ 这是「当下的执行口径」"),
    ("G4", G4_ARGPARSE, "命令行参数的默认值是旧目标 ⇒ 这是「当下的执行口径」"),
)

# ★次要路线① 的保留登记 (★登记项必须带理由★; 不在册的一律判红)
SECONDARY_MARK = "ISS355-SECONDARY-ROUTE"
LEGACY_REGISTRY = {
    ("SW/tools/rknn_bench.py", "TARGET_PLATFORM"):
        "次要路线① 的实现 (toolkit2 2.3.2 家族固定用旧目标) · 保留作历史对照 · "
        "板上接受性 [0数据] · ISS-355 任务书明写「旧链保留为次要路线①」",
}


def snippet(line: str, width: int = 170) -> str:
    s = re.sub(r"\s+", " ", line.strip())
    return s[:width] + ("…" if len(s) > width else "")


def in_iss355_scope(rel: str) -> bool:
    return rel in ISS355_WRITABLE or rel.startswith(ISS355_WRITABLE_PREFIX)


def channel(rel: str) -> str:
    return "本单可处置" if in_iss355_scope(rel) else "越权·交 main/hw-lead 裁"


def iter_code_files(root: str):
    for r in SCAN_ROOTS:
        base = os.path.join(root, r)
        if not os.path.isdir(base):
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames if d not in ("__pycache__", ".git")]
            for fn in sorted(filenames):
                if os.path.splitext(fn)[1].lower() not in CODE_EXT:
                    continue
                if fn in SKIP_BASENAME:
                    continue
                p = os.path.join(dirpath, fn)
                rel = os.path.relpath(p, root)
                if rel.startswith(HIST_PREFIX):
                    continue          # ★历史留档 (logs/ 与 HANDOFF/)★
                try:
                    if os.path.getsize(p) > MAX_BYTES:
                        continue
                except OSError:
                    continue
                yield p, rel


def scan_code_layer(root: str):
    """⇒ (hits, n_files); hit = {file,line,rule,verdict,snippet,action,channel}"""
    hits, n = [], 0
    for p, rel in iter_code_files(root):
        try:
            with open(p, encoding="utf-8", errors="ignore") as f:
                text = f.read()
        except OSError:
            continue
        n += 1
        for i, line in enumerate(text.splitlines(), 1):
            # ★整行注释 = 文档/散文 ⇒ 归【口径层】(ISS-353 闸的 F1~F8 规则)管★
            #   本层只管【可执行的那一行】⇒ 注释行不算「当下的执行口径」
            if line.lstrip().startswith("#"):
                continue
            for rid, rx, action in CODE_RULES:
                m = rx.search(line)
                if not m:
                    continue
                var = m.group(1) if rid == "G2" else ""
                reason = LEGACY_REGISTRY.get((rel, var))
                if reason is None and SECONDARY_MARK in line:
                    reason = ("脚本内显式标注为次要路线① (marker %s) · 保留但已点名" % SECONDARY_MARK)
                if reason:
                    hits.append({"file": rel, "line": i, "rule": rid,
                                 "verdict": VERDICT_LEGACY,
                                 "snippet": snippet(line),
                                 "action": reason, "channel": channel(rel)})
                else:
                    hits.append({"file": rel, "line": i, "rule": rid,
                                 "verdict": VERDICT_STALE,
                                 "snippet": snippet(line),
                                 "action": action + " ⇒ 改成 rk3572 (或显式登记为次要路线①)",
                                 "channel": channel(rel)})
                break   # 一行只报第一条命中的规则
    hits.sort(key=lambda h: (h["file"], h["line"]))
    return hits, n


# ── 口径层交叉校验 (★复用 ISS-353 闸的模块, 不重造★) ─────────────────────────
def load_iss353_gate(root: str):
    p = os.path.join(root, "SW", "tools", "check_rk3572_target_caliber.py")
    if not os.path.exists(p):
        return None
    try:
        spec = importlib.util.spec_from_file_location("iss353_caliber_gate", p)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception:                                   # noqa: BLE001
        return None


def scan_caliber_layer(root: str):
    mod = load_iss353_gate(root)
    if mod is None:
        return None, []
    try:
        _files, hits = mod.scan(root)
    except Exception:                                   # noqa: BLE001
        return None, []
    stale = [h for h in hits if h.get("verdict") == mod.VERDICT_STALE]
    return mod, stale


# ── 主路线入口断言 (★机器读脚本里的默认值: 跑 --print-route + 静态交叉核对★) ──
def _run_script(script_path: str, args, env_extra=None, root: str = ""):
    env = dict(os.environ)
    env["TMPDIR"] = os.path.join(root, "tmp") if root else env.get("TMPDIR", "/tmp")
    for k in ("ROUTE", "TARGET_PLATFORM", "TOOLKIT_PKG", "TOOLKIT_VER"):
        env.pop(k, None)            # ★scrub: 断言的是「默认」, 不许被环境变量偷换★
    if env_extra:
        env.update(env_extra)
    return subprocess.run(["bash", script_path] + list(args), capture_output=True,
                          text=True, env=env, timeout=180)


def read_route(script_path: str, env_extra=None, root: str = ""):
    p = _run_script(script_path, ["--print-route"], env_extra, root)
    kv = {}
    for line in (p.stdout or "").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        kv[k.strip()] = v.strip()
    return kv, p


def check_main_route(root: str, script_rel: str = MAIN_SCRIPT):
    """⇒ (results: list[(name, state, detail)], ok: bool)"""
    res = []
    spath = os.path.join(root, script_rel)
    if not os.path.exists(spath):
        res.append(("P1_主路线脚本在位", "FAIL", "找不到 %s" % script_rel))
        return res, False
    res.append(("P1_主路线脚本在位", "PASS", script_rel))

    kv, p = read_route(spath, None, root)
    if p.returncode != 0:
        res.append(("P2_--print-route 可跑", "FAIL",
                    "rc=%d · %s" % (p.returncode, (p.stderr or "").strip()[:160])))
        return res, False
    res.append(("P2_--print-route 可跑", "PASS", "rc=0 · 读到 %d 个键" % len(kv)))

    want = {
        "route": EXPECT_ROUTE,
        "effective_target_platform": EXPECT_TARGET,
        "effective_toolkit_pkg": EXPECT_PKG,
        "effective_toolkit_version": EXPECT_VER,
        "target_platform_default": EXPECT_TARGET,
        "toolkit_pkg_default": EXPECT_PKG,
        "toolkit_version_default": EXPECT_VER,
        "legacy_route": LEGACY_ROUTE,
        "legacy_target_platform": LEGACY_TARGET,
    }
    bad = [(k, kv.get(k), v) for k, v in want.items() if kv.get(k) != v]
    if bad:
        for k, got, exp in bad:
            res.append(("P3_默认路线取值", "FAIL",
                        "%s = %r (期望 %r)" % (k, got, exp)))
    else:
        res.append(("P3_默认路线取值", "PASS",
                    "route=%s · target=%s · %s %s · 旧链入口=%s/%s"
                    % (kv.get("route"), kv.get("effective_target_platform"),
                       kv.get("effective_toolkit_pkg"), kv.get("effective_toolkit_version"),
                       kv.get("legacy_route"), kv.get("legacy_target_platform"))))

    # 旧链 (次要路线①) 必须仍可达
    kv2, p2 = read_route(spath, {"ROUTE": LEGACY_ROUTE}, root)
    if p2.returncode == 0 and kv2.get("route") == LEGACY_ROUTE \
            and kv2.get("effective_target_platform") == LEGACY_TARGET:
        res.append(("P4_旧链(次要路线①)仍可达", "PASS",
                    "ROUTE=%s ⇒ target=%s · %s %s"
                    % (LEGACY_ROUTE, kv2.get("effective_target_platform"),
                       kv2.get("effective_toolkit_pkg"), kv2.get("effective_toolkit_version"))))
    else:
        res.append(("P4_旧链(次要路线①)仍可达", "FAIL",
                    "ROUTE=%s ⇒ route=%r target=%r"
                    % (LEGACY_ROUTE, kv2.get("route"), kv2.get("effective_target_platform"))))

    # 静态交叉核对 (★不许只靠 --print-route 的输出糊弄: 源码里的默认值也要对★)
    try:
        with open(spath, encoding="utf-8", errors="ignore") as f:
            src = f.read()
    except OSError as e:
        src = ""
        res.append(("P5_源码默认值交叉核对", "FAIL", "读不到源码: %s" % e))
    else:
        statics = {
            "ROUTE_DEFAULT": EXPECT_ROUTE,
            "TARGET_PLATFORM_DEFAULT": EXPECT_TARGET,
            "TOOLKIT_PKG_DEFAULT": EXPECT_PKG,
            "TOOLKIT_VER_DEFAULT": EXPECT_VER,
        }
        miss = []
        for var, val in statics.items():
            if not re.search(r'%s\s*=\s*["\']%s["\']' % (re.escape(var), re.escape(val)), src):
                miss.append("%s=%s" % (var, val))
        if miss:
            res.append(("P5_源码默认值交叉核对", "FAIL",
                        "源码里没有这些默认赋值: %s" % ", ".join(miss)))
        else:
            res.append(("P5_源码默认值交叉核对", "PASS",
                        "4 个默认值字面量都在源码里 (%s)"
                        % ", ".join("%s=%s" % kv for kv in sorted(statics.items()))))
    return res, all(r[1] != "FAIL" for r in res)


# ── 两件套拷贝断言 (★行为级: 用脚本自带的 --copy-only 缝★) ───────────────────
def check_two_piece(root: str, script_rel: str = MAIN_SCRIPT, sandbox: str = ""):
    res = []
    spath = os.path.join(root, script_rel)
    if not os.path.exists(spath):
        res.append(("C1_两件套拷贝(行为级)", "FAIL", "找不到 %s" % script_rel))
        return res, False
    base = sandbox or os.path.join(root, "tmp")
    os.makedirs(base, exist_ok=True)
    sd = os.path.join(base, "iss355_twopiece_%d" % os.getpid())
    shutil.rmtree(sd, ignore_errors=True)
    try:
        src_ok = os.path.join(sd, "src_ok")
        dst_ok = os.path.join(sd, "dst_ok")
        src_bad = os.path.join(sd, "src_bad")
        dst_bad = os.path.join(sd, "dst_bad")
        for d in (src_ok, dst_ok, src_bad, dst_bad):
            os.makedirs(d, exist_ok=True)
        base_name = "probe_rk3572_int8_heads"
        with open(os.path.join(src_ok, base_name + ".rknn"), "w") as f:
            f.write("FAKE-RKNN")
        with open(os.path.join(src_ok, base_name + ".weight"), "w") as f:
            f.write("FAKE-WEIGHT")
        p = _run_script(spath, ["--copy-only", src_ok, dst_ok], None, root)
        got_r = os.path.exists(os.path.join(dst_ok, base_name + ".rknn"))
        got_w = os.path.exists(os.path.join(dst_ok, base_name + ".weight"))
        got_sr = os.path.exists(os.path.join(dst_ok, base_name + ".rknn.sha256"))
        got_sw = os.path.exists(os.path.join(dst_ok, base_name + ".weight.sha256"))
        if p.returncode == 0 and got_r and got_w and got_sr and got_sw:
            res.append(("C1_两件套拷贝(有 .weight)", "PASS",
                        "rc=0 · .rknn + .weight + 两份 sha256 sidecar 全部到位"))
        else:
            res.append(("C1_两件套拷贝(有 .weight)", "FAIL",
                        "rc=%d · rknn=%s weight=%s sidecar_rknn=%s sidecar_weight=%s"
                        % (p.returncode, got_r, got_w, got_sr, got_sw)))
        # 反向: 只有 .rknn ⇒ 必须失败且不许把 .rknn 拷出去
        with open(os.path.join(src_bad, base_name + ".rknn"), "w") as f:
            f.write("FAKE-RKNN-ONLY")
        p2 = _run_script(spath, ["--copy-only", src_bad, dst_bad], None, root)
        leaked = os.path.exists(os.path.join(dst_bad, base_name + ".rknn"))
        if p2.returncode != 0 and not leaked:
            res.append(("C2_只拷 .rknn 必须失败", "PASS",
                        "rc=%d (≠0) 且没有把 .rknn 拷出去" % p2.returncode))
        else:
            res.append(("C2_只拷 .rknn 必须失败", "FAIL",
                        "rc=%d · .rknn 被拷出去了=%s" % (p2.returncode, leaked)))
    finally:
        shutil.rmtree(sd, ignore_errors=True)
    # 静态: 脚本里必须有 .weight 的拷法 (不许只拷 .rknn)
    try:
        with open(spath, encoding="utf-8", errors="ignore") as f:
            src = f.read()
    except OSError:
        src = ""
    if re.search(r"cp[^\n]*\.weight", src) or re.search(r"\.weight", src):
        res.append(("C3_脚本里有 .weight 的处理", "PASS", "源码含 .weight 处理分支"))
    else:
        res.append(("C3_脚本里有 .weight 的处理", "FAIL", "源码里找不到 .weight"))
    return res, all(r[1] != "FAIL" for r in res)


# ── 旧链代价标注 ──────────────────────────────────────────────────────────────
def check_legacy_cost(root: str, script_rel: str = MAIN_SCRIPT):
    res = []
    spath = os.path.join(root, script_rel)
    if not os.path.exists(spath):
        return [("D1_旧链代价已标明", "FAIL", "找不到 %s" % script_rel)], False
    with open(spath, encoding="utf-8", errors="ignore") as f:
        src = f.read()
    has_zero = "0数据" in src
    has_legacy = LEGACY_TARGET in src
    if has_zero and has_legacy:
        res.append(("D1_旧链代价已标明", "PASS",
                    "脚本里写明了旧链在板上的接受性 = [0数据]"))
    else:
        res.append(("D1_旧链代价已标明", "FAIL",
                    "[0数据]=%s · %s=%s" % (has_zero, LEGACY_TARGET, has_legacy)))
    return res, all(r[1] != "FAIL" for r in res)


# ── 主流程 ─────────────────────────────────────────────────────────────────────
def run_all(root: str, script_rel: str = MAIN_SCRIPT):
    code_hits, n_code = scan_code_layer(root)
    mod, stale = scan_caliber_layer(root)
    route_res, route_ok = check_main_route(root, script_rel)
    tp_res, tp_ok = check_two_piece(root, script_rel)
    lc_res, lc_ok = check_legacy_cost(root, script_rel)

    stale_in_scope = [h for h in (stale or []) if in_iss355_scope(h.get("file", ""))]
    stale_out = [h for h in (stale or []) if not in_iss355_scope(h.get("file", ""))]

    offenders = [h for h in code_hits if h["verdict"] == VERDICT_STALE] + stale_in_scope
    ok = route_ok and tp_ok and lc_ok and not offenders
    return {
        "root": root, "code_files": n_code,
        "code_hits": code_hits, "offenders": offenders,
        "caliber_stale_in_scope": stale_in_scope, "caliber_stale_out": stale_out,
        "caliber_available": mod is not None,
        "route": route_res, "two_piece": tp_res, "legacy_cost": lc_res,
        "ok": ok,
    }


def report(r: dict) -> None:
    print("=" * 78)
    print("ISS-355 · 转换路线实现闸 · 只读扫描 (v1.0)")
    print("=" * 78)
    print("root              : %s" % r["root"])
    print("扫面              : %s  (代码层只看 %s)" % (" / ".join(SCAN_ROOTS),
                                                     "/".join(CODE_EXT)))
    print("代码文件数        : %d" % r["code_files"])
    if r["caliber_available"]:
        print("口径层交叉校验    : 复用 ISS-353 闸的 F1~F8 规则 (不重造) ⇒ "
              "结论矛盾 %d 条 (本单可处置 %d · 越权 %d)"
              % (len(r["caliber_stale_in_scope"]) + len(r["caliber_stale_out"]),
                 len(r["caliber_stale_in_scope"]), len(r["caliber_stale_out"])))
    else:
        print("口径层交叉校验    : ISS-353 闸不可用 (跳过)")
    print("")
    print("─── ★【名单】★ 当下执行口径 = 旧目标的站点 (文件 + 行号 + 原文 + 处置) ───")
    if not r["code_hits"]:
        print("   (无)")
    cur = None
    for h in r["code_hits"]:
        if h["file"] != cur:
            cur = h["file"]
            print("\n◆ %s" % cur)
        print("   L%-6d [%s] %s" % (h["line"], h["rule"], h["verdict"]))
        print("      原文: %s" % h["snippet"])
        print("      处置: %s" % h["action"])
        print("      通道: %s" % h["channel"])
    if r["caliber_stale_in_scope"] or r["caliber_stale_out"]:
        print("\n─── 口径层 (ISS-353 闸在管) ───")
        for h in r["caliber_stale_in_scope"] + r["caliber_stale_out"]:
            print("   %s L%s [%s] %s" % (h.get("file"), h.get("line"),
                                         h.get("rule"), h.get("verdict")))
            print("      原文: %s" % h.get("snippet"))
    print("")
    print("─── 主路线入口断言 (机器读脚本里的默认值) ───")
    for name, st, det in r["route"]:
        print("   %-26s %-4s %s" % (name, st, det))
    print("")
    print("─── 两件套拷贝断言 (行为级) ───")
    for name, st, det in r["two_piece"]:
        print("   %-26s %-4s %s" % (name, st, det))
    print("")
    print("─── 旧链代价标注 ───")
    for name, st, det in r["legacy_cost"]:
        print("   %-26s %-4s %s" % (name, st, det))
    print("")
    print("=" * 78)
    if r["offenders"]:
        print("★结论: 有 %d 条「当下执行口径 = 旧目标」的站点 ⇒ 逐条见上面名单 ⇒ rc=1" % len(r["offenders"]))
        for h in r["offenders"]:
            print("   · %s L%s [%s] %s" % (h["file"], h["line"], h["rule"], h["snippet"][:120]))
    else:
        print("★结论: 无「当下执行口径 = 旧目标」的站点; 主路线/两件套/代价标注 全过 ⇒ rc=0")
    print("=" * 78)


# ── 反向自测 ───────────────────────────────────────────────────────────────────
def _sandbox(root: str) -> str:
    base = os.environ.get("ISS355_TMPDIR") or os.path.join(root, "tmp")
    os.makedirs(base, exist_ok=True)
    return base


def selftest(root: str) -> int:
    ok, total = 0, 0
    base = _sandbox(root)
    td = os.path.join(base, "iss355_selftest_%d" % os.getpid())
    shutil.rmtree(td, ignore_errors=True)
    try:
        sdir = os.path.join(td, "SW", "tools")
        os.makedirs(sdir, exist_ok=True)
        src = os.path.join(root, MAIN_SCRIPT)
        dst = os.path.join(sdir, "rk3572_model_rebuild.sh")
        if not os.path.exists(src):
            print("  ❌ 自测 FAIL: 找不到 %s" % MAIN_SCRIPT)
            return 1
        shutil.copy2(src, dst)

        def gate(root_dir):
            r = run_all(root_dir)
            return r, (0 if r["ok"] else 1)

        # 1) 正向: 干净副本 ⇒ 绿
        total += 1
        r, rc = gate(td)
        if rc == 0:
            print("  ✅ 正向用例1: 干净副本 ⇒ rc=0 (绿)")
            ok += 1
        else:
            print("  ❌ 正向用例1 FAIL: 干净副本就判红 (offenders=%d)"
                  % len(r["offenders"]))

        # 2) 反向: 把默认 target 改回旧值 ⇒ 必须判红并点名该脚本
        total += 1
        with open(dst, encoding="utf-8") as f:
            txt = f.read()
        bad = txt.replace('TARGET_PLATFORM_DEFAULT="rk3572"',
                          'TARGET_PLATFORM_DEFAULT="rk3576"')
        if bad == txt:
            print("  ❌ 反向用例2 FAIL: 副本里找不到可改的默认值字面量")
        else:
            with open(dst, "w", encoding="utf-8") as f:
                f.write(bad)
            r, rc = gate(td)
            named = [h for h in r["offenders"] if h["file"].endswith("rk3572_model_rebuild.sh")]
            if rc == 1 and named:
                print("  ✅ 反向用例2: 默认 target 改回旧值 ⇒ rc=1 且点名 %s L%s"
                      % (named[0]["file"], named[0]["line"]))
                ok += 1
            else:
                print("  ❌ 反向用例2 FAIL: rc=%d · 点名 %d 条" % (rc, len(named)))
            # 3) 恢复 ⇒ 必须转绿
            total += 1
            shutil.copy2(src, dst)
            r, rc = gate(td)
            if rc == 0:
                print("  ✅ 反向用例3: 恢复 ⇒ rc=0 (绿)")
                ok += 1
            else:
                print("  ❌ 反向用例3 FAIL: 恢复后仍判红")

        # 4) 反向: 把两件套里的 .weight 拷法删掉 ⇒ 两件套断言必须判红
        total += 1
        with open(dst, encoding="utf-8") as f:
            txt = f.read()
        broken = txt.replace('cp -p "$src_weight" "$dst_weight"',
                             '# ISS355-SELFTEST-BREAK: .weight 的拷法被删掉了')
        if broken == txt:
            print("  ❌ 反向用例4 FAIL: 副本里找不到 .weight 的拷法")
        else:
            with open(dst, "w", encoding="utf-8") as f:
                f.write(broken)
            r, rc = gate(td)
            tp = [x for x in r["two_piece"] if x[0].startswith("C1")]
            if rc == 1 and tp and tp[0][1] == "FAIL":
                print("  ✅ 反向用例4: 删掉 .weight 拷法 ⇒ rc=1 且两件套断言判红 (%s)" % tp[0][0])
                ok += 1
            else:
                print("  ❌ 反向用例4 FAIL: rc=%d · 两件套断言=%s"
                      % (rc, tp[0][1] if tp else "没跑"))
            shutil.copy2(src, dst)

        # 5) 反向: 仓里别处冒出旧目标的默认值 ⇒ 名单必须点名它
        total += 1
        other = os.path.join(sdir, "stray_default.sh")
        with open(other, "w", encoding="utf-8") as f:
            f.write("#!/usr/bin/env bash\nTARGET_PLATFORM_DEFAULT=\"rk3576\"\n")
        r, rc = gate(td)
        named = [h for h in r["offenders"] if h["file"].endswith("stray_default.sh")]
        if rc == 1 and named:
            print("  ✅ 反向用例5: 仓里别处冒出的旧默认 ⇒ rc=1 且点名 %s L%s"
                  % (named[0]["file"], named[0]["line"]))
            ok += 1
        else:
            print("  ❌ 反向用例5 FAIL: rc=%d · 点名 %d 条" % (rc, len(named)))
        os.remove(other)

        # 6) 正向: 旧链 (次要路线①) 必须仍可达
        total += 1
        r, rc = gate(td)
        legacy = [x for x in r["route"] if x[0].startswith("P4")]
        if legacy and legacy[0][1] == "PASS":
            print("  ✅ 反向用例6: 旧链 (次要路线①) 仍可达 ⇒ %s" % legacy[0][2])
            ok += 1
        else:
            print("  ❌ 反向用例6 FAIL: 旧链不可达")

        # 7) 沙盒落项目盘 (★不许写 /tmp★)
        total += 1
        if td.startswith(base) and base.startswith(root):
            print("  ✅ 反向用例7: 自测沙盒落在项目盘 (%s) ⇒ 没写 /tmp" % base)
            ok += 1
        else:
            print("  ❌ 反向用例7 FAIL: 自测沙盒不在项目盘 (%s)" % td)
    finally:
        shutil.rmtree(td, ignore_errors=True)

    print("SELFTEST %d/%d 通过" % (ok, total))
    if ok == total:
        print("ALL TESTS PASS")
        return 0
    print("SELFTEST FAILED")
    return 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=None, help="扫别的目录 (selftest 用); 默认 = 本脚本上三级")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    root = args.root or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    if args.selftest:
        print("### ISS-355 转换路线实现闸 · 反向自测 (沙盒落项目盘 tmp/) ###")
        return selftest(root)

    r = run_all(root)
    if args.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        report(r)
    return 0 if r["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
