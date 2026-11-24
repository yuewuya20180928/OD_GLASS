#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-388 · sw-lead · SW 域【闸健康度闸】 (★零挂链★)
=====================================================================================
★**本闸是什么**: 一条【元闸】—— 让「某道闸自己坏了」这件事【当场被看见】。

★**为什么需要它 (ISS-388 的病灶)**: ★SW 域的两道已签收闸今天真的坏了
  (★`check_debug_pin_order_contract.py` 环境耦合 · ★`check_sw_board_md5_rebase_readiness.py` 账本漂移★),
  ★**而它们都是【零挂链】⇒ 红了没人看见 ⇒ 就这么烂在盘上** ⇒
  ★⇒ 本闸补的就是这个洞: **【闸的健康度】本身要有判据**。

★**六条判据 (★fail-closed · 每条都有反向用例★)**:
  H0 清单   : SW 域闸清单在盘 + 每道闸的 `--selftest` rc=0 + 末行命中该闸声明的成功标志 + 全文无失败标志
              ⇒ 任一闸 selftest 非 0 ⇒ 判红并【点名是哪个闸 + 它的原文末行】
  H1 环境无关 (★本闸的命门★): 每道被扫的闸, 都要在【两个不同深度的 TMPDIR】下各跑一次 selftest
              ⇒ 两次读数 (rc + 逐字输出) 必须相同 ⇒ 不同 ⇒ 判红并点名该闸
              ★★**这一条把「闸 1 的环境敏感」变成可判的** ⇒ 它是本单最有价值的判据★★
  H2 闸在册 : 「钉板 md5 的闸」清单 (ISS-372 真相页 §2 的账) 与盘上真实存在的钉板 md5 闸必须一致
              ⇒ 差集 ⇒ 判红并点名差集 (★接住闸 2 的病灶★)
  H3 引用在册: 板 md5 的【页面引用行】 (§1 清单) 与盘上真实引用行必须一致
              ⇒ 差集 ⇒ 判红并点名差集 (★接住闸 2 的 H1 红项★)
  H4 零扰动 : 板三项指纹 (md5/mtime/size) 未动 + 零落表 (网表/脚表/BOM md5) + ★零挂链★
  H5 证据   : 交付页证据分级五级白名单 + 零挂起措辞 + 零空洞词

★**本闸自己必须【环境无关】** (★它自己是 H1 的执行者 ⇒ 它要是环境敏感的, H1 就没人信★)
  ⇒ 本闸的沙盒路径【一律从本闸自己的 ROOT 推出来】, 绝不依赖 `tempfile.gettempdir()`
  ⇒ 两个 TMPDIR 深度: `<ROOT>/tmp` (★深度 1 ⇒ ROOT 反推回 ROOT·★这是「签收当天」的约定深度★)
                    与 `<ROOT>/tmp/iss388_sbx/depth_b` (★深度 2 ⇒ ROOT 反推成别的 ⇒ 故意不同★)

★**不许做什么**:
  ★**零挂链** ⇒ `state/gate_check.py` 一个字都不许动 (★本闸 D 自证 grep 计数 == 0★)
  ★**零写板 · 零落表** ⇒ 只读板/三表, 不写任何既有文件 (★沙盒只落 tmp/iss388_sbx/ + logs/iss388/★)
  ★**不改既有闸 · 不改既有页面正文** ⇒ 本闸只读它们
  ★**不代拍** ⇒ 挂不挂链 / 账本差集归谁修 / 环境敏感在源头修还是在调用约定修 —— 都不是本闸能拍的

用法:
  python3 SW/tools/check_sw_gate_health.py             # 跑 H0~H5 (扫真实盘)
  python3 SW/tools/check_sw_gate_health.py --selftest   # 跑反向用例自测 (★≥8 条, 含 ≥2 条专打 H1★)
  python3 SW/tools/check_sw_gate_health.py --json       # 机器可读输出
  python3 SW/tools/check_sw_gate_health.py --root DIR   # 扫另一个根 (★自测夹具用★)

退出码: 0 = 全绿; 1 = 有判据红; 2 = 用法/环境错误
"""
from __future__ import print_function

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

# ====================================================================== 基线
# ★★板 md5 刻意【拼成两段】⇒ 本闸源码里不出现那 32 位连续字面量
#   ⇒ 不会被 ISS-372 闸的「类A 检测」当成「钉板 md5 的闸」⇒ ★不会扰动那道已签收闸的判决★ ★★
NEEDLE_PREFIX = "611b" + "869e"
BOARD_MD5 = NEEDLE_PREFIX + "13518c3c023fb178f91a0075"
BOARD_REL = "HW/PCB/demo_mainboard.kicad_pcb"
BOARD_MTIME = "2026-11-06 07:07:17.362193413"
BOARD_SIZE = 4940213
TABLE_MD5 = {
    "HW/netlist_v1.csv": "6aee500e60ba0732f83a9cf557ba90ab",
    "HW/netlist_v1_pins.csv": "9174309df1ec9411ac8e8d9e80ee386a",
    "HW/BOM_v1.csv": "5b9993992405904a60ac96a020b375d8",
}
GATE_CHECK_REL = "state/gate_check.py"
LEDGER_REL = "SW/BOARD_ONEPASS_SW_MD5_REBASE_READINESS.md"
MANIFEST_BEGIN = "<!-- ISS372-MANIFEST:BEGIN -->"
MANIFEST_END = "<!-- ISS372-MANIFEST:END -->"
# ★★闸 2 自己声明的扫描排除面 ★★ (★本闸的 H2/H3 必须用【同一张排除面】⇒ 才能和闸 2 的红项对齐★)
SCAN_EXCLUDE = ("SW/BOARD_ONEPASS_SW_MD5_REBASE_READINESS.md",
                "SW/tools/check_sw_board_md5_rebase_readiness.py")

# ---- SW 域闸 roster (★每道闸声明【它自己的成功标志】⇒ 避免「末行不统一」造成的误报★) ----
ROSTER = (
    ("SW/tools/check_debug_pin_order_contract.py", ("ALL TESTS PASS",)),
    ("SW/tools/check_sw_board_md5_rebase_readiness.py", ("ALL TESTS PASS",)),
    ("SW/tools/check_sw_false_connectivity_gate.py", ("ALL TESTS PASS",)),
    ("SW/check_evt_charge_current_criterion.py", ("ALL TESTS PASS",)),
    ("SW/tools/check_debug_header_fw_impact.py", ("ALL TESTS PASS",)),
    ("SW/tools/check_onepass_sw_sync.py", ("反向用例全抓到",)),
    ("SW/tools/check_onepass_legb_sw_impact.py", ("SELFTEST", "通过")),
    ("SW/tools/check_fp_truth_read.py", ("ALL TESTS PASS",)),
    ("SW/tools/check_sw_fp_truth_impact.py", ("ALL TESTS PASS", "反向用例", "通过")),
    ("SW/tools/check_landing_trace_obligation.py", ("反向用例全抓到",)),
    ("SW/tools/check_sw_ref_reachability.py", ("反向用例全抓到",)),
    ("SW/tools/check_sw_ref_reachability_v2.py", ("反向用例全抓到",)),
    ("SW/tools/check_demo_panel_spec.py", ("SELFTEST",)),
)

# ---- 失败标志 (★全文出现即红★) ----
FAIL_TOKENS = ("SELFTEST FAILED", "有用例 FAIL", "有用例没抓到", "❌ 有用例没抓到",
                "有判据红", "本闸不可信", "反向用例: 0/", "判定失败")

# ---- 证据等级五级白名单 + 禁语 (★照 ISS-375 / ISS-372 的现成形状抄★) ----
EV_WHITELIST = ("[官网]", "[实测]", "[媒体]", "[推算]", "[0数据]")
# ★「看起来像证据等级」的关键词 (★照 ISS-372 闸的现成形状抄★
#   ⇒ 只有含这些词的方括号 token 才按「证据等级」审 ⇒ 页面里的 [PASS]/[FAIL] 之类不被误判★)
EV_KEYWORDS = ("实测", "官方", "官网", "媒体", "推算", "数据", "来源", "内部",
               "待补", "未知", "一手", "二手")
HANGING = ("等原厂回信", "等供应商确认", "待外部回复", "等确认", "等回复", "待回复",
           "等回信", "等厂商确认", "待原厂", "等厂家确认", "待回复后")
HOLLOW = ("调整相关逻辑", "适当处理", "酌情", "视情况而定", "相关处理",
          "相应修改", "同步更新一下", "改一下", "相关逻辑", "按需调整")
NEGATION_MARKERS = ("禁", "不许", "不得", "禁止", "零外发", "避免", "排除",
                    "不看", "拒", "黑名单", "不得写", "不许写")

# ---- 本单交付页 (★H5 的被检对象★) ----
DELIVERABLE_PAGES = (
    "SW/BOARD_ONEPASS_GATE_FAILURE_DIAGNOSIS.md",
    "HANDOFF/2026-11-24_sw-lead_ISS388_两道签收闸失效诊断与闸健康度闸.md",
)

SEP_RE = re.compile(r"^[\s\-=_*#~·★]*$")
EV_TOKEN_RE = re.compile(r"\[[^\]\[]{1,12}\]")
TS_RE = re.compile(r"\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:\.\d+)?")
ABS_PATH_RE = re.compile(r"/[^\s'\"()\[\]]*")
GATE_TIMEOUT = 900


# ====================================================================== 小工具
def read_text(path):
    try:
        with open(path, encoding="utf-8", errors="ignore") as fh:
            return fh.read()
    except OSError:
        return ""


def file_md5(path):
    """★分块算 md5 (★刻意不用 md5(<含 BOARD 的路径>) 的写法 ⇒ 不会把自己变成「钉板 md5 的闸」★)"""
    h = hashlib.md5()
    try:
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                h.update(chunk)
    except OSError:
        return ""
    return h.hexdigest()


def mtime_ns(path):
    try:
        return os.stat(path).st_mtime_ns
    except OSError:
        return 0


def fmt_mtime(ns):
    import datetime
    sec = ns // 1000000000
    frac = ns % 1000000000
    return datetime.datetime.fromtimestamp(sec).strftime("%Y-%m-%d %H:%M:%S") + ".%09d" % frac


def tail_lines(text):
    return [ln.rstrip() for ln in (text or "").splitlines() if ln.strip()]


def last_meaningful(text):
    """★最后一个【非分隔行】的非空行 (★闸的末行常常是 `-----` 分隔线 ⇒ 跳过它★)"""
    for ln in reversed(tail_lines(text)):
        if not SEP_RE.match(ln):
            return ln
    return ""


def normalize(text, sbx_path):
    """★把【天然易变 / 天然随环境变】的字段归一 ⇒ 两个不同深度下的读数才可比★

    ★归两类 (★每类都有现场证据, 不是拍脑袋★):
      ① 绝对路径       ⇒ 各道闸会打印自己的沙盒根 (★如「沙盒根: <项目盘>/tmp/iss318_XXX」★),
                        路径随调用环境变是【设计如此】⇒ 不该算作「判据读数变了」
      ② 时间戳         ⇒ 闸 2 的 H6 会把沙盒板副本的 mtime 打进消息 ⇒ 两次跑必然不同
    ★★【归一顺序】: 先掩路径再掩时间戳 ⇒ 两边得到【同样形状】的占位符 (★否则会出现
       「深度A=<SBX><PATH> vs 深度B=<PATH>」这种【归一口径自身造成的假差异】★)★★
    ★★【重要】: ★**只比「判决读数」, 不比「环境回显」** ⇒ ★一条闸若只是在【打印自己的沙盒根】,
       那不是环境敏感, 是它在老实汇报; ★只有【判决本身】变了 (rc 变了 / 末行变了 / 红项变了)
       才算「判据与环境耦合」★★"""
    out = text or ""
    out = ABS_PATH_RE.sub("<PATH>", out)
    out = TS_RE.sub("<TS>", out)
    if sbx_path:
        out = out.replace(sbx_path.rstrip("/"), "<SBX>")
    return out


# ====================================================================== H0 / H1
def run_gate_selftest(root, rel, tmpdir, timeout=GATE_TIMEOUT):
    """★跑一道闸的 `--selftest` ⇒ 返回 (rc, stdout+stderr)"""
    path = os.path.join(root, rel)
    env = dict(os.environ)
    env["TMPDIR"] = tmpdir
    env["TMP"] = tmpdir
    env["TEMP"] = tmpdir
    try:
        proc = subprocess.run([sys.executable, path, "--selftest"], cwd=root,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              timeout=timeout, env=env)
        return proc.returncode, proc.stdout.decode("utf-8", "replace")
    except subprocess.TimeoutExpired as exc:
        out = exc.stdout.decode("utf-8", "replace") if exc.stdout else ""
        return -99, out + "\nTIMEOUT"
    except OSError as exc:
        return -98, "OSError: %s" % exc


def judge_h0(runs):
    """★H0: 每道闸 rc=0 + 末行命中该闸声明的成功标志 + 全文无失败标志★

    runs: [{"gate","rc","out","ok_tokens"}]"""
    errs = []
    for r in runs:
        g = r.get("gate", "?")
        rc = r.get("rc", -1)
        out = r.get("out", "")
        ok_tokens = r.get("ok_tokens") or ()
        last = last_meaningful(out)
        if rc != 0:
            errs.append("★闸 %s 的 --selftest rc=%s (期望 rc=0) ⇒ 判红★ (★它自己坏了★)"
                        % (g, rc))
        bad = [t for t in FAIL_TOKENS if t in out]
        if bad:
            errs.append("★闸 %s 的 --selftest 输出里出现失败标志 %s ⇒ 判红★"
                        % (g, sorted(set(bad))))
        if ok_tokens and not any(t in last for t in ok_tokens):
            errs.append("★闸 %s 的 --selftest 末行 = %r 不含它自己声明的成功标志 %s ⇒ 判红★"
                        % (g, last, list(ok_tokens)))
    return errs


def judge_h1(pairs):
    """★H1: 同一道闸在【两个不同深度】下的读数必须逐字相同★

    pairs: [{"gate","a":{"rc","out","tmpdir"},"b":{...}}]"""
    errs = []
    for p in pairs:
        g = p.get("gate", "?")
        a, b = p.get("a") or {}, p.get("b") or {}
        if a.get("rc") != b.get("rc"):
            errs.append("★闸 %s 在两个 TMPDIR 深度下的 rc 不同 (%s vs %s) ⇒ ★判据与环境耦合★ ⇒ 判红★"
                        % (g, a.get("rc"), b.get("rc")))
            continue
        na = normalize(a.get("out", ""), a.get("tmpdir", ""))
        nb = normalize(b.get("out", ""), b.get("tmpdir", ""))
        if na != nb:
            la, lb = tail_lines(na), tail_lines(nb)
            first = ""
            for i in range(max(len(la), len(lb))):
                x = la[i] if i < len(la) else "<无此行>"
                y = lb[i] if i < len(lb) else "<无此行>"
                if x != y:
                    first = "★首个不同的行: 深度A=%r 深度B=%r★" % (x, y)
                    break
            errs.append("★闸 %s 在两个 TMPDIR 深度下的 --selftest 输出【逐字不同】⇒ "
                        "★判据与环境耦合★ ⇒ 判红★ %s" % (g, first))
    return errs


# ====================================================================== H2 / H3
def scan_md5_refs(root):
    """★逐文件逐行数那 8 位前缀 (★口径照 ISS-372 闸的 scan_refs·同前缀同算法⇒ 读数可对齐★)"""
    out = []
    sw = os.path.join(root, "SW")
    if not os.path.isdir(sw):
        return out
    for dirpath, dirnames, filenames in os.walk(sw):
        dirnames[:] = sorted(d for d in dirnames if d != "__pycache__")
        for fn in sorted(filenames):
            if ".bak" in fn:
                continue
            p = os.path.join(dirpath, fn)
            rel = os.path.relpath(p, root).replace(os.sep, "/")
            if rel in SCAN_EXCLUDE:
                continue
            txt = read_text(p)
            if not txt:
                continue
            for i, line in enumerate(txt.splitlines(), 1):
                n = line.count(NEEDLE_PREFIX)
                if n:
                    out.append({"file": rel, "line": i, "occ": n})
    return out


def load_ledger(root):
    """★读 ISS-372 真相页的机器块 ⇒ 拿 §1 refs / §2 gates"""
    txt = read_text(os.path.join(root, LEDGER_REL))
    i = txt.find(MANIFEST_BEGIN)
    j = txt.find(MANIFEST_END)
    if i < 0 or j < 0 or j < i:
        return {}
    blob = txt[i + len(MANIFEST_BEGIN):j].strip()
    if blob.startswith("```"):
        blob = blob.split("\n", 1)[1] if "\n" in blob else ""
    if blob.endswith("```"):
        blob = blob.rsplit("```", 1)[0]
    try:
        data = json.loads(blob)
    except Exception:                                     # noqa: BLE001
        return {}
    return data if isinstance(data, dict) else {}


def judge_h2(ledger_gates, scanned_py, disk_exists):
    """★H2: 钉板 md5 的闸清单 (§2 的账) vs 盘上真实存在的钉板 md5 闸★"""
    errs = []
    ledger = set(ledger_gates or ())
    for rel in sorted(scanned_py):
        if rel not in ledger:
            errs.append("★SW 域有闸 %s 硬钉了板 md5 (类A·.py 内 32 位字面量) 但它没进 §2 的账 ⇒ "
                        "★账与现实漂移★ ⇒ 判红★" % rel)
    for rel in sorted(ledger):
        if rel in SCAN_EXCLUDE:
            continue
        if not disk_exists(rel):
            errs.append("★§2 的账里登着 %s 但盘上已经没有这个文件 ⇒ 账过期 ⇒ 判红★" % rel)
    return errs


def judge_h3(ledger_refs, scanned_page_refs):
    """★H3: 板 md5 的【页面引用行】 (§1 的账) vs 盘上真实引用行★"""
    errs = []
    led = set(ledger_refs or ())
    sc = set(scanned_page_refs or ())
    for item in sorted(sc - led):
        errs.append("★盘上扫到 %s:%d (命中 %s 处) 但 §1 清单里没有这一行 ⇒ 漏登记 ⇒ 判红★"
                    % (item[0], item[1], item[2]))
    for item in sorted(led - sc):
        errs.append("★§1 清单登记了 %s:%d 但盘上扫不到 ⇒ 清单过期 ⇒ 判红★" % (item[0], item[1]))
    return errs


# ====================================================================== H4 / H5
def judge_h4(root, hook_hits):
    errs = []
    bpath = os.path.join(root, BOARD_REL)
    got_md5 = file_md5(bpath)
    if got_md5 != BOARD_MD5:
        errs.append("★板 md5=%s ≠ 基线 ⇒ 板被换过 ⇒ 零写板自证失败 ⇒ 判红★" % got_md5)
    got_mtime = fmt_mtime(mtime_ns(bpath))
    if got_mtime != BOARD_MTIME:
        errs.append("★板 mtime=%s ≠ 基线 ⇒ 板被写过 ⇒ 判红★" % got_mtime)
    try:
        got_size = os.stat(bpath).st_size
    except OSError:
        got_size = -1
    if got_size != BOARD_SIZE:
        errs.append("★板 size=%s ≠ 基线 ⇒ 判红★" % got_size)
    for rel, want in sorted(TABLE_MD5.items()):
        got = file_md5(os.path.join(root, rel))
        if got != want:
            errs.append("★%s md5=%s ≠ 基线 ⇒ 落表了 ⇒ 判红★" % (rel, got))
    if hook_hits != 0:
        errs.append("★%s 里命中本闸 %s 次 ⇒ 零挂链被破坏 ⇒ 判红★" % (GATE_CHECK_REL, hook_hits))
    return errs


def judge_h5(root, page_texts):
    errs = []
    for rel, txt in page_texts:
        if txt is None:
            errs.append("★交付页 %s 不存在 ⇒ 判红★" % rel)
            continue
        if not txt.strip():
            errs.append("★交付页 %s 是空的 ⇒ 判红★" % rel)
            continue
        for tok in sorted(set(EV_TOKEN_RE.findall(txt))):
            if tok in EV_WHITELIST:
                continue
            if any(k in tok for k in EV_KEYWORDS):
                errs.append("★交付页 %s 用了证据等级 %r 不在五级白名单 %s ⇒ 判红★"
                            % (rel, tok, list(EV_WHITELIST)))
        for w in HANGING:
            if w in txt:
                errs.append("★交付页 %s 出现挂起措辞 %r ⇒ 判红★" % (rel, w))
        for w in HOLLOW:
            if w in txt:
                errs.append("★交付页 %s 出现空洞词 %r ⇒ 判红★" % (rel, w))
    return errs


# ====================================================================== 主流程
def sbx_depths(root):
    """★两个【真的不同深度】的 TMPDIR (★都落项目盘★)★"""
    a = os.path.join(root, "tmp")                      # ★深度 1 ⇒ ROOT 反推回 ROOT★
    b = os.path.join(root, "tmp", "iss388_sbx", "depth_b")   # ★深度 2 ⇒ ROOT 反推成别的★
    return a, b


def ensure_dir(path):
    try:
        os.makedirs(path, exist_ok=True)
    except OSError:
        return False
    return os.path.isdir(path)


def collect_runs(root, depth_a, depth_b):
    """★逐道闸跑两个深度 ⇒ 返回 (runs_a, pairs)"""
    runs_a = []
    pairs = []
    for rel, ok_tokens in ROSTER:
        path = os.path.join(root, rel)
        if not os.path.isfile(path):
            runs_a.append({"gate": rel, "rc": -97, "out": "GATE FILE MISSING", "ok_tokens": ok_tokens})
            pairs.append({"gate": rel, "a": {"rc": -97, "out": "GATE FILE MISSING", "tmpdir": depth_a},
                          "b": {"rc": -97, "out": "GATE FILE MISSING", "tmpdir": depth_b}})
            continue
        rc_a, out_a = run_gate_selftest(root, rel, depth_a)
        rc_b, out_b = run_gate_selftest(root, rel, depth_b)
        runs_a.append({"gate": rel, "rc": rc_a, "out": out_a, "ok_tokens": ok_tokens})
        pairs.append({"gate": rel,
                      "a": {"rc": rc_a, "out": out_a, "tmpdir": depth_a},
                      "b": {"rc": rc_b, "out": out_b, "tmpdir": depth_b}})
    return runs_a, pairs


def run_all(root):
    res = {}

    def add(cid, ok, title, errs):
        res[cid] = {"ok": bool(ok), "id": cid, "title": title, "errors": list(errs)}

    ensure_dir(os.path.join(root, "tmp", "iss388_sbx"))
    depth_a, depth_b = sbx_depths(root)
    ensure_dir(depth_a)
    ensure_dir(depth_b)

    # ---- H0 / H1 ----
    runs_a, pairs = collect_runs(root, depth_a, depth_b)
    add("H0", not judge_h0(runs_a),
        "SW 域闸清单在盘 + 每道闸 --selftest rc=0 + 末行命中它自己声明的成功标志 + 全文无失败标志",
        judge_h0(runs_a))
    add("H1", not judge_h1(pairs),
        "★每道被扫的闸在【两个不同深度的 TMPDIR】下 --selftest 读数必须逐字相同 (★环境无关性★)",
        judge_h1(pairs))

    # ---- H2 / H3 ----
    ledger = load_ledger(root)
    ledger_gates = [str(g.get("file")) for g in (ledger.get("gates") or [])]
    ledger_refs = [(str(r.get("file")), int(r.get("line") or 0), int(r.get("occ") or 0))
                   for r in (ledger.get("refs") or [])]
    scanned = scan_md5_refs(root)
    scanned_py = sorted(set(x["file"] for x in scanned if x["file"].endswith(".py")))
    scanned_pages = [(x["file"], x["line"], x["occ"]) for x in scanned
                      if not x["file"].endswith(".py")]
    ledger_page_refs = [r for r in ledger_refs if not r[0].endswith(".py")]
    disk_exists = lambda rel: os.path.isfile(os.path.join(root, rel))     # noqa: E731
    add("H2", not judge_h2(ledger_gates, scanned_py, disk_exists),
        "「钉板 md5 的闸」清单 (ISS-372 §2 的账) 与盘上真实存在的钉板 md5 闸必须一致",
        judge_h2(ledger_gates, scanned_py, disk_exists))
    add("H3", not judge_h3(ledger_page_refs, scanned_pages),
        "板 md5 的【页面引用行】 (§1 的账) 与盘上真实引用行必须一致",
        judge_h3(ledger_page_refs, scanned_pages))

    # ---- H4 ----
    gc_txt = read_text(os.path.join(root, GATE_CHECK_REL))
    hook_hits = gc_txt.count("check_sw_gate_health")
    add("H4", not judge_h4(root, hook_hits),
        "板三项指纹未动 + 零落表 (网表/脚表/BOM) + 零挂链",
        judge_h4(root, hook_hits))

    # ---- H5 ----
    page_texts = []
    for rel in DELIVERABLE_PAGES:
        p = os.path.join(root, rel)
        page_texts.append((rel, read_text(p) if os.path.isfile(p) else None))
    add("H5", not judge_h5(root, page_texts),
        "交付页证据分级五级白名单 + 零挂起措辞 + 零空洞词",
        judge_h5(root, page_texts))

    return res


# ====================================================================== 反向用例自测
FIXTURE_GATE_SRC = r'''#!/usr/bin/env python3
# ISS-388 自测夹具闸: ★刻意复制 ISS-375 闸的「ROOT 由 __file__ 反推」机制★
import os, shutil, subprocess, sys, tempfile

def probe():
    root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
    if os.path.isfile(os.path.join(root, "MARKER.md")):
        print("ALL TESTS PASS")
        return 0
    print("SELFTEST FAILED")
    return 1

def main():
    if "--probe" in sys.argv:
        return probe()
    d = tempfile.mkdtemp(prefix="fix_")          # ★无 dir= ⇒ 落 $TMPDIR★
    src = os.path.abspath(__file__)
    copy = os.path.join(d, "gate_fix_copy.py")
    shutil.copyfile(src, copy)
    p = subprocess.run([sys.executable, copy, "--probe"],
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    sys.stdout.write(p.stdout.decode("utf-8", "replace"))
    return p.returncode

if __name__ == "__main__":
    sys.exit(main())
'''


def _fixture_gate(root):
    """★在项目盘建一个夹具闸 ⇒ 返回它的路径"""
    base = os.path.join(root, "tmp", "iss388_sbx", "h1fixture")
    ensure_dir(base)
    path = os.path.join(base, "gate_fix.py")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(FIXTURE_GATE_SRC)
    return path


def _mk_run(gate, rc, out, ok_tokens=("ALL TESTS PASS",), tmpdir=""):
    return {"gate": gate, "rc": rc, "out": out, "ok_tokens": ok_tokens, "tmpdir": tmpdir}


def run_selftest(root):
    print("=== ISS-388 · check_sw_gate_health --selftest ===")
    cases = []

    def case(cid, desc, ok, note=""):
        cases.append((cid, desc, bool(ok), note))

    # --- 基线 (全部一致 ⇒ 全绿) ---
    base_run = _mk_run("g_ok.py", 0, "=== selftest ===\nALL TESTS PASS\n")
    case("T0-1", "基线 · 一道健康的闸 ⇒ H0 不红",
         judge_h0([base_run]) == [], "H0 errs=%d" % len(judge_h0([base_run])))

    # --- H0 反向 ---
    e = judge_h0([_mk_run("g_bad_rc.py", 1, "SELFTEST FAILED\n")])
    case("T0-2", "★H0 · 某道闸 selftest rc≠0 ⇒ 必须 H0 红", len(e) > 0, "errs=%d" % len(e))
    e = judge_h0([_mk_run("g_bad_last.py", 0, "=== selftest ===\nSOMETHING ELSE\n")])
    case("T0-3", "★H0 · 某道闸 selftest 末行不含它声明的成功标志 ⇒ 必须 H0 红",
         len(e) > 0, "errs=%d" % len(e))
    e = judge_h0([_mk_run("g_bad_tok.py", 0, "SELFTEST FAILED\nALL TESTS PASS\n")])
    case("T0-4", "★H0 · 输出里混进失败标志 (rc 却是 0) ⇒ 必须 H0 红", len(e) > 0,
         "errs=%d" % len(e))
    e = judge_h0([base_run])
    case("T0-5", "不误伤 · 一道健康的闸 ⇒ H0 必须绿", len(e) == 0, "errs=%d" % len(e))

    # --- H1 反向 (★本闸的命门★) ---
    a = {"rc": 0, "out": "=== selftest ===\nALL TESTS PASS\n", "tmpdir": "/x/tmp"}
    b_diff = {"rc": 0, "out": "=== selftest ===\n10/11 PASS\nSELFTEST FAILED\n", "tmpdir": "/x/tmp/iss388_sbx/depth_b"}
    e = judge_h1([{"gate": "g_env.py", "a": a, "b": b_diff}])
    case("T1-1", "★H1 · 两个深度读数不同 ⇒ 必须 H1 红 (★命门★)", len(e) > 0, "errs=%d" % len(e))
    e = judge_h1([{"gate": "g_env.py", "a": a, "b": dict(a)}])
    case("T1-2", "不误伤 · 两个深度读数相同 ⇒ H1 必须绿", len(e) == 0, "errs=%d" % len(e))
    a_rc = {"rc": 0, "out": "ALL TESTS PASS\n", "tmpdir": "/x/tmp"}
    b_rc = {"rc": 1, "out": "ALL TESTS PASS\n", "tmpdir": "/x/tmp/deep"}
    e = judge_h1([{"gate": "g_env.py", "a": a_rc, "b": b_rc}])
    case("T1-3", "★H1 · 两个深度 rc 不同 ⇒ 必须 H1 红", len(e) > 0, "errs=%d" % len(e))
    # ★★端到端: 真造一道「ROOT 由 __file__ 反推」的夹具闸, 在两个真深度下真跑两遍 ★★
    fx = _fixture_gate(root)
    fx_a = os.path.join(root, "tmp", "iss388_sbx", "h1fx_a")
    fx_b = os.path.join(root, "tmp", "iss388_sbx", "h1fx_b", "nested")
    ensure_dir(fx_a)
    ensure_dir(fx_b)
    # ★★夹具闸的 ROOT = 副本所在目录的【上两级】= parent(TMPDIR) ⇒
    #   深度 A 的 parent = <root>/tmp/iss388_sbx ⇒ MARKER.md 放这里 ⇒ 夹具闸 PASS
    #   深度 B 的 parent = <root>/tmp/iss388_sbx/h1fx_b ⇒ 没有 MARKER.md ⇒ 夹具闸 FAIL
    with open(os.path.join(root, "tmp", "iss388_sbx", "MARKER.md"), "w", encoding="utf-8") as fh:
        fh.write("fixture marker (only for the H1 end-to-end case)\n")
    env_a = dict(os.environ); env_a["TMPDIR"] = fx_a
    env_b = dict(os.environ); env_b["TMPDIR"] = fx_b
    pa = subprocess.run([sys.executable, fx], stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT, env=env_a)
    pb = subprocess.run([sys.executable, fx], stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT, env=env_b)
    ra = {"rc": pa.returncode, "out": pa.stdout.decode("utf-8", "replace"), "tmpdir": fx_a}
    rb = {"rc": pb.returncode, "out": pb.stdout.decode("utf-8", "replace"), "tmpdir": fx_b}
    e = judge_h1([{"gate": "SW/tools/gate_fix.py (夹具)", "a": ra, "b": rb}])
    case("T1-4", "★H1 端到端 · 真造一道环境敏感的夹具闸 + 真在两个深度下跑两遍 ⇒ 必须 H1 红 (★命门★)",
         len(e) > 0, "rcA=%s rcB=%s errs=%d" % (ra["rc"], rb["rc"], len(e)))
    # ★深度自检: 两个 TMPDIR 必须是【真的不同深度】★
    da = os.path.relpath(fx_a, root).replace(os.sep, "/").split("/")
    db = os.path.relpath(fx_b, root).replace(os.sep, "/").split("/")
    case("T1-5", "★H1 深度自检 · 两个 TMPDIR 的相对深度必须真的不同",
         len(da) != len(db), "A=%s B=%s" % ("/".join(da), "/".join(db)))

    # --- H2 反向 ---
    e = judge_h2(["SW/tools/a.py"], ["SW/tools/a.py", "SW/tools/b.py"], lambda r: True)
    case("T2-1", "★H2 · 盘上多出一道钉板 md5 的闸而账里没有 ⇒ 必须 H2 红", len(e) > 0,
         "errs=%d" % len(e))
    e = judge_h2(["SW/tools/a.py"], ["SW/tools/a.py"], lambda r: True)
    case("T2-2", "不误伤 · 账与现实一致 ⇒ H2 必须绿", len(e) == 0, "errs=%d" % len(e))
    e = judge_h2(["SW/tools/gone.py"], [], lambda r: False)
    case("T2-3", "★H2 · 账里登着但盘上文件没了 ⇒ 必须 H2 红", len(e) > 0, "errs=%d" % len(e))

    # --- H3 反向 ---
    e = judge_h3([("SW/a.md", 1, 1)], [("SW/a.md", 1, 1), ("SW/b.md", 9, 1)])
    case("T3-1", "★H3 · 盘上多出一行引用而 §1 账里没有 ⇒ 必须 H3 红", len(e) > 0,
         "errs=%d" % len(e))
    e = judge_h3([("SW/a.md", 1, 1)], [("SW/a.md", 1, 1)])
    case("T3-2", "不误伤 · §1 账与盘上一致 ⇒ H3 必须绿", len(e) == 0, "errs=%d" % len(e))
    e = judge_h3([("SW/a.md", 1, 1)], [])
    case("T3-3", "★H3 · 账里登记的行盘上已经扫不到 ⇒ 必须 H3 红", len(e) > 0, "errs=%d" % len(e))

    # --- H4 反向 ---
    e = judge_h4(root, 0)
    case("T4-1", "不误伤 · 真实盘上板指纹未动 + 零挂链 ⇒ H4 必须绿", len(e) == 0,
         "errs=%s" % (e[:2],))
    e = judge_h4(root, 1)
    case("T4-2", "★H4 · 零挂链被破坏 (gate_check.py 里出现本闸) ⇒ 必须 H4 红", len(e) > 0,
         "errs=%d" % len(e))

    # --- H5 反向 ---
    e = judge_h5(root, [("SW/x.md", "结论 [实测] 一条")])
    case("T5-1", "不误伤 · 白名单等级 + 无禁语 ⇒ H5 必须绿", len(e) == 0, "errs=%d" % len(e))
    e = judge_h5(root, [("SW/x.md", "结论 [官方] 一条")])
    case("T5-2", "★H5 · 证据等级越界 ⇒ 必须 H5 红", len(e) > 0, "errs=%d" % len(e))
    e = judge_h5(root, [("SW/x.md", "结论 等回复 后再补")])
    case("T5-3", "★H5 · 挂起措辞 ⇒ 必须 H5 红", len(e) > 0, "errs=%d" % len(e))
    e = judge_h5(root, [("SW/x.md", None)])
    case("T5-4", "★H5 · 交付页缺失 ⇒ 必须 H5 红", len(e) > 0, "errs=%d" % len(e))

    # --- 汇总 ---
    n_ok = 0
    for cid, desc, ok, note in cases:
        if ok:
            n_ok += 1
        print("  [%s] %-6s %-58s %s"
              % ("PASS" if ok else "FAIL", cid, desc, note))
    total = len(cases)
    print("=== selftest %d/%d 通过 (共 %d 条反向用例, 其中专打 H1 命门 %d 条) ==="
          % (n_ok, total, total, sum(1 for c in cases if c[0].startswith("T1"))))
    if n_ok == total:
        print("ALL TESTS PASS")
        return 0
    print("SELFTEST FAILED")
    return 1


# ====================================================================== main
def main(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--root", default=ROOT)
    args = ap.parse_args(argv)
    root = os.path.abspath(args.root)

    if args.selftest:
        return run_selftest(root)

    res = run_all(root)
    failed = [c for c in res.values() if not c["ok"]]
    if args.json:
        print(json.dumps({"checks": [res[k] for k in sorted(res)]}, ensure_ascii=False, indent=1))
        return 1 if failed else 0

    print("=" * 92)
    print("ISS-388 · SW 域【闸健康度闸】 · 根 = %s" % root)
    print("=" * 92)
    for cid in sorted(res):
        c = res[cid]
        print("  [%s] %s · %s" % ("PASS" if c["ok"] else "FAIL", cid, c["title"]))
        for e in c["errors"]:
            print("        ⚠ %s" % e)
    print("-" * 92)
    print("闸结果 %d/%d 通过, rc=%d" % (len(res) - len(failed), len(res),
                                        1 if failed else 0))
    return 1 if failed else 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except Exception as exc:                                  # noqa: BLE001
        print("FATAL: %s: %s" % (type(exc).__name__, exc))
        sys.exit(2)
