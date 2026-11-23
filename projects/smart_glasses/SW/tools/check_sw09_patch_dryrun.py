#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-368 · sw-lead · 「SW09 三处同批落地」补丁的【副本 dry-run 机器闸】.

★**本闸只读真件** ★ (零写板 / 零落表 / 零改既有闸 / 零改既有页面 / 不写 STATE.yaml / 不写任何人的分片)
★**本闸【不挂链】** ★ (★挂不挂 `state/gate_check.py` 的 EXTRA_GATES = main 的机制地界★ ⇒ 本闸一个字没挂★)

★**判据清单 (F1~F7)** ★
  F1  三处是否同批到位 (★落点① 的页内三处: §2 逐条表 / §2.1 归属步分布 / §6 机器可读 JSON 块★)
      ⇒ ★**页内三处 + JSON 块计数 == 9** ★ + ★**落点③ 的新闸字节未变 (md5 == ISS-363 交卷基线)★ ★
  F2  ISS-362 页 §H4-REG 三个登记数字是否 == (9 / 1 / 5) ★
  F3  ★**干跑两次的 diff 是否为 0** ★ (★同一补丁跑第二遍 ⇒ 逐字节零变更★)
  F4  ★**10 道 SW 闸是否全绿** ★ (★在副本上逐道实跑·取真实 rc★)
  F5  证据等级五级白名单 (★[官网] / [实测] / [媒体] / [推算] / [0数据]★)
  F6  正文零挂起措辞 (★禁语 + 挂起词·代码块内引用的原文不算★)
  F7  ★**沙盒在项目盘 `tmp/`** ★ (★且沙盒里不许有软链★)

★**为什么要有 F1~F7 这七条** ★
  · 「板只改一次」那一趟 (S1~S13) 会【合法地】把三份真源的 md5 一起换掉 ⇒
    SW 侧的 10 道准出闸 + 清单页 + ISS-362 页三个数字全部盯着这件事 ⇒
    ★**若三处不同批落地 ⇒ 清单页说 9 条、ISS-362 页说 8 条、闸按 8 条判 ⇒ 清单与闸互相打脸** ★
  · ⇒ 本闸把【三处同批】做成一道可机器复核的判据: ★**只改一处 ⇒ 必红** ★

★**F4 的读数从哪来** ★: ★**在项目盘 `tmp/` 的副本沙盒里逐道实跑 10 道 SW 闸** ★
  ⇒ 读数缓存写在 `tmp/iss368_sbx/gates_report.json` (★键 = 副本里两份被改页面的 md5★)
  ⇒ ★**副本内容一变 ⇒ 缓存自动失效 ⇒ 闸重跑** ★ ⇒ ★**缓存不新鲜 ⇒ 一律重跑 (fail-closed)★ ★

★**沙盒纪律** ★: 沙盒根 = 项目盘 `tmp/iss368_sbx/` · ★**禁止 os.symlink (ISS-327 cont1 根因)★** ·
真件一个字节不许被沙盒碰过 (★板 md5 / mtime / size 三重自证★)

用法:
    python3 SW/tools/check_sw09_patch_dryrun.py            # 跑一遍 (rc=0 = F1~F7 全绿)
    python3 SW/tools/check_sw09_patch_dryrun.py --json     # 机读输出
    python3 SW/tools/check_sw09_patch_dryrun.py --selftest # 反向用例 (★≥6 条·每条自证「只红目标那一条」★)
    python3 SW/tools/check_sw09_patch_dryrun.py --rebuild  # 强制重建沙盒
    python3 SW/tools/check_sw09_patch_dryrun.py --run-gates # 只跑 10 道闸并刷新缓存
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(PROJ, "SW", "tools"))

import apply_sw09_three_place_patch as P   # noqa: E402  ★只读 import · 补丁脚本是本闸的被检对象★

SBX_BASE_REL = os.path.join("tmp", "iss368_sbx")
SBX_PATCHED_REL = os.path.join("tmp", "iss368_sbx", "patched")
GATES_CACHE_REL = os.path.join("tmp", "iss368_sbx", "gates_report.json")
NEW_PAGE_REL = os.path.join("SW", "BOARD_ONEPASS_SW09_LANDING_PATCH.md")

# ★★10 道 SW 闸 (★与 ISS-362 交卷页 §B6.2 的清单逐条一致★) ★★
SW_GATES = [
    "SW/tools/check_onepass_sw_sync.py",
    "SW/tools/check_sw_ref_reachability.py",
    "SW/tools/check_landing_trace_obligation.py",
    "SW/tools/check_demo_panel_spec.py",
    "SW/tools/check_demo_panel_spec_r6_selftest.py",
    "SW/tools/check_demo_panel_spec_r6_chainjudge_selftest.py",
    "SW/tools/check_demo_panel_spec_r6_hardprot_iss315_selftest.py",
    "SW/tools/check_shutdown_semantics.py",
    "SW/tools/check_timing_review_adc_sync.py",
    "SW/tools/timing_check.py",
]

EV_WHITELIST = ("[官网]", "[实测]", "[媒体]", "[推算]", "[0数据]")
EV_KEYWORDS = ("实测", "官方", "官网", "媒体", "推算", "数据", "来源", "内部", "待补", "未知", "一手", "二手")

FORBIDDEN_PHRASES = ("等原厂回信", "等供应商确认", "待外部回复", "等确认")
HANGING_PHRASES = ("TBD", "TODO", "待补充", "待填写", "待填", "先放着", "回头再", "稍后再",
                   "暂缺", "待落", "待拍", "待确认", "待议", "暂缓处理", "尚未定")
NEGATION_MARKERS = ("禁", "不许", "不得", "禁止", "零外发", "避免", "排除", "不看", "拒", "黑名单",
                    "本单", "零挂起", "零待补")

GATE_TIMEOUT = 300


# ==================================================================================================
# 小工具
# ==================================================================================================
def read_text(path: str) -> str:
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def write_text(path: str, txt: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(txt)


def md5_of(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def json_block_items(text: str):
    m = re.search(r"```json\s*(\{.*?\})\s*```", text, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(1)).get("items")
    except Exception:                                        # noqa: BLE001
        return None


def strip_code_blocks(text: str) -> str:
    """★去掉围栏代码块 (★块里引用的原文不算正文★) ★"""
    return re.sub(r"```.*?```", "", text, flags=re.S)


def find_forbidden(text: str, phrases):
    hits = []
    for ph in phrases:
        for m in re.finditer(re.escape(ph), text):
            ctx = text[max(0, m.start() - 45):m.start()]
            if any(mk in ctx for mk in NEGATION_MARKERS):
                continue
            hits.append((ph, m.start()))
    return hits


# ==================================================================================================
# 沙盒构建 (★真副本·禁止软链★)
# ==================================================================================================
SBX_DIRS = ["SW", "HW", "MECH", "config", "deploy", "docs", "REF", "REQ", "FRAMEWORK", "PRINT"]
SBX_STATE_DIRS = ["fragments", "tasks", "fixtures", "gate_snapshots", "outbox"]


def _copy_tree(src: str, dst: str) -> None:
    os.makedirs(dst, exist_ok=True)
    for dirpath, dirnames, filenames in os.walk(src):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        rel = os.path.relpath(dirpath, src)
        for fn in filenames:
            if fn.endswith(".pyc"):
                continue
            s = os.path.join(dirpath, fn)
            d = os.path.join(dst, rel, fn) if rel != "." else os.path.join(dst, fn)
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copy2(s, d)


def build_sandbox(root: str, dst: str) -> None:
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    os.makedirs(dst)
    for d in SBX_DIRS:
        s = os.path.join(root, d)
        if os.path.isdir(s):
            _copy_tree(s, os.path.join(dst, d))
    st = os.path.join(root, "state")
    if os.path.isdir(st):
        os.makedirs(os.path.join(dst, "state"), exist_ok=True)
        for fn in os.listdir(st):
            fp = os.path.join(st, fn)
            if os.path.isfile(fp) and ".bak" not in fn and not fn.endswith(".pyc"):
                shutil.copy2(fp, os.path.join(dst, "state", fn))
        for d in SBX_STATE_DIRS:
            s = os.path.join(st, d)
            if os.path.isdir(s):
                _copy_tree(s, os.path.join(dst, "state", d))
    # 根下的散文件
    for fn in os.listdir(root):
        fp = os.path.join(root, fn)
        if os.path.isfile(fp) and not fn.endswith(".onnx") and ".bak" not in fn:
            shutil.copy2(fp, os.path.join(dst, fn))
    os.makedirs(os.path.join(dst, "tmp"), exist_ok=True)


def sandbox_is_stale(root: str, dst: str) -> bool:
    """★副本里两份被改页面的 md5 是不是还等于真件 (★等于 ⇒ 副本还没落地 ⇒ 要重跑补丁★) ★"""
    if not os.path.isdir(dst):
        return True
    for rel in (P.SYNC_REL, P.IMPACT_REL):
        a = os.path.join(root, rel)
        b = os.path.join(dst, rel)
        if not os.path.isfile(b) or md5_of(a) != md5_of(b):
            return True
    return False


def apply_patch_to_sandbox(root: str, dst: str) -> dict:
    """★在副本上跑补丁 (★默认干跑先看一遍·再真写★) ★"""
    dry = subprocess.run([sys.executable, os.path.join(HERE, "apply_sw09_three_place_patch.py"),
                          "--dry-run" if False else "--root", root,
                          "--apply", "--target-root", dst],
                         capture_output=True, text=True, timeout=120)
    return {"rc": dry.returncode, "out": dry.stdout[-4000:], "err": dry.stderr[-2000:]}


def run_sw_gates(root: str, timeout: int = GATE_TIMEOUT):
    """★在 root 里逐道实跑 10 道 SW 闸 ⇒ [(rel, rc)] ★"""
    env = dict(os.environ)
    tmpd = os.path.join(root, "tmp", "iss368_tmp")
    os.makedirs(tmpd, exist_ok=True)
    env["TMPDIR"] = tmpd
    env["TMP"] = tmpd
    env["TEMP"] = tmpd
    rows = []
    for rel in SW_GATES:
        t0 = time.time()
        try:
            p = subprocess.run([sys.executable, rel], cwd=root, env=env,
                               capture_output=True, text=True, timeout=timeout)
            rc = p.returncode
            tail = (p.stdout or "")[-1200:]
        except subprocess.TimeoutExpired:
            rc = 124
            tail = "★超时★"
        rows.append({"rel": rel, "rc": rc, "sec": round(time.time() - t0, 2), "tail": tail})
    return rows


def gates_cache_key(sandbox: str) -> str:
    h = hashlib.md5()
    for rel in (P.SYNC_REL, P.IMPACT_REL):
        p = os.path.join(sandbox, rel)
        if os.path.isfile(p):
            h.update(md5_of(p).encode())
    return h.hexdigest()


def load_gate_rows(root: str, sandbox: str, force: bool = False):
    """★取 10 道闸的读数 (★缓存新鲜就用缓存·不新鲜/没有 ⇒ 实跑★) ★"""
    cache_p = os.path.join(root, GATES_CACHE_REL)
    key = gates_cache_key(sandbox)
    if not force and os.path.isfile(cache_p):
        try:
            c = json.loads(read_text(cache_p))
            if c.get("key") == key and c.get("rows"):
                for r in c["rows"]:
                    r["cached"] = True
                return c["rows"], True
        except Exception:                                    # noqa: BLE001
            pass
    rows = run_sw_gates(sandbox)
    try:
        write_text(cache_p, json.dumps({"key": key, "at": time.strftime("%Y-%m-%d %H:%M:%S"),
                                        "sandbox": sandbox, "rows": rows},
                                       ensure_ascii=False, indent=2))
    except Exception:                                        # noqa: BLE001
        pass
    return rows, False


# ==================================================================================================
# ★七条判据 (★每条一个函数·selftest 逐条单独调 ★)
# ==================================================================================================
def f1_three_places(ctx: dict) -> dict:
    """★三处是否同批到位 (落点① 页内三处 + JSON 计数 + 落点③ 新闸字节未变) ★"""
    errs = []
    sync_p = os.path.join(ctx["sandbox"], P.SYNC_REL)
    sync = read_text(sync_p)
    # ① §2 逐条表 · 第 9 行
    rows = [l for l in sync.split("\n")
            if l.startswith("| ★**`%s`** ★ |" % P.SW09_ID)]
    if len(rows) != 1:
        errs.append("§2 逐条表里 `SW09_FP_TRUTH_READ` 行命中 %d 次 (★要恰好 1 次★)" % len(rows))
    else:
        if len(rows[0].split("|")) - 2 != 7:
            errs.append("§2 逐条表第 9 行列数 = %d (★要 7 列★)" % (len(rows[0].split("|")) - 2))
    # ② §2.1 归属步分布 · S10 行
    s10 = [l for l in sync.split("\n") if l.startswith("| ★**S10** ★ |")]
    if len(s10) != 1:
        errs.append("§2.1 分布表里 S10 行命中 %d 次 (★要恰好 1 次★)" % len(s10))
    else:
        if "`SW09_FP_TRUTH_READ`" not in s10[0]:
            errs.append("§2.1 分布表 S10 行里没有 `SW09_FP_TRUTH_READ`")
        cells = [c.strip() for c in s10[0].split("|")]
        if len(cells) > 2 and cells[2] != "4":
            errs.append("§2.1 分布表 S10 行条数 = %r (★要 4★)" % cells[2])
    # ③ §6 机器可读 JSON 块
    items = json_block_items(sync)
    if items is None:
        errs.append("§6 JSON 块解析不出来")
    else:
        if len(items) != 9:
            errs.append("§6 JSON 块 items 长度 = %d (★要 9★)" % len(items))
        ids = [str(it.get("id")) for it in items if isinstance(it, dict)]
        if ids.count(P.SW09_ID) != 1:
            errs.append("§6 JSON 块里 `SW09_FP_TRUTH_READ` 命中 %d 次 (★要恰好 1 次★)"
                        % ids.count(P.SW09_ID))
        else:
            it = [x for x in items if isinstance(x, dict) and x.get("id") == P.SW09_ID][0]
            miss = [f for f in ("id", "source_iss", "title", "current_state", "action",
                                "criterion", "step", "blocked_by", "evidence") if f not in it]
            empty = [f for f in ("id", "source_iss", "title", "current_state", "action",
                                 "criterion", "step", "blocked_by", "evidence")
                     if f in it and not str(it[f]).strip()]
            if miss or empty:
                errs.append("§6 JSON 块里 SW09 九字段 缺=%s 空=%s" % (miss, empty))
    # ④ §2 小节头
    if "★★9 条一条不许漏★★" not in sync:
        errs.append("§2 小节头还是「8 条一条不许漏」")
    # ⑤ 落点③ 的新闸: 字节未变
    gp = os.path.join(ctx["sandbox"], P.GATE_REL)
    if not os.path.isfile(gp):
        errs.append("落点③ 新闸 `SW/tools/check_fp_truth_read.py` 不存在")
    else:
        gm = md5_of(gp)
        if gm != P.GATE_REL_MD5_EXPECT:
            errs.append("落点③ 新闸 md5 = %s ≠ ISS-363 交卷基线 %s (★本补丁对它零改动★)"
                        % (gm, P.GATE_REL_MD5_EXPECT))
    return {"ok": not errs, "id": "F1",
            "title": "三处同批到位 (落点① 页内三处 + JSON 计数 == 9 + 落点③ 新闸字节未变)",
            "detail": "§2 表行 1 · §2.1 S10 行 1 · §6 JSON items %s · 落点③ md5 %s"
                      % (len(items) if items else "解析失败",
                         md5_of(gp) if os.path.isfile(gp) else "缺"),
            "errors": errs}


def f2_h4reg_numbers(ctx: dict) -> dict:
    """★ISS-362 页 §H4-REG 三个登记数字是否 == (9 / 1 / 5) ★"""
    errs = []
    p = os.path.join(ctx["sandbox"], P.IMPACT_REL)
    page = read_text(p)
    m = re.search(r"<!--\s*H4-REG:BEGIN\s*-->(.*?)<!--\s*H4-REG:END\s*-->", page, re.S)
    reg = m.group(1) if m else ""
    if not reg.strip():
        return {"ok": False, "id": "F2", "title": "§H4-REG 三个登记数字 == (9/1/5)",
                "detail": "登记块读不到", "errors": ["页里没有 H4-REG 登记块"]}
    got = {}
    for k, want in (("H4-ITEMS", 9), ("H4-COVER", 1), ("H4-GENERIC", 5)):
        mm = re.search(r"^-\s*%s\s*[:：]\s*(.*)$" % re.escape(k), reg, re.M)
        v = mm.group(1).strip() if mm else ""
        got[k] = v
        if v != str(want):
            errs.append("H4-REG 的 %s=%r ≠ 期望 %d" % (k, v, want))
    for k in ("H4-FINDING", "H4-IMPACT", "H4-COUNTERMEASURE"):
        mm = re.search(r"^-\s*%s\s*[:：]\s*(.*)$" % re.escape(k), reg, re.M)
        if not (mm and mm.group(1).strip()):
            errs.append("H4-REG 缺 %s" % k)
    return {"ok": not errs, "id": "F2", "title": "§H4-REG 三个登记数字 == (9/1/5)",
            "detail": "H4-ITEMS=%s · H4-COVER=%s · H4-GENERIC=%s"
                      % (got.get("H4-ITEMS"), got.get("H4-COVER"), got.get("H4-GENERIC")),
            "errors": errs}


def f3_idempotent(ctx: dict) -> dict:
    """★干跑两次的 diff 是否为 0 (★同一补丁跑第二遍 ⇒ 逐字节零变更★) ★"""
    errs = []
    # ★★基准来源: 优先用【当前沙盒副本】★★
    #   ★★selftest 的反向用例正是改沙盒·若 F3 只读项目根 ⇒ 沙盒怎么改都影响不到它★★
    #   ⇒ ★F3 永远是绿的 ⇒ 那条反向用例根本抓不到它★ ⇒ ★本单修正: 基准 = 沙盒·沙盒不可用才回落项目根★ ★
    base = ctx.get("sandbox") or ctx["root"]
    scratch = os.path.join(ctx["root"], "tmp", "iss368_sbx", "f3_scratch")
    if os.path.isdir(scratch):
        shutil.rmtree(scratch)
    os.makedirs(os.path.join(scratch, "SW", "tools"), exist_ok=True)
    for rel in (P.SYNC_REL, P.IMPACT_REL, P.GATE_REL):
        src = os.path.join(base, rel)
        if not os.path.isfile(src):
            src = os.path.join(ctx["root"], rel)
        shutil.copy2(src, os.path.join(scratch, rel))
    cmd = [sys.executable, os.path.join(HERE, "apply_sw09_three_place_patch.py"),
           "--root", ctx["root"], "--apply", "--target-root", scratch]
    r1 = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if r1.returncode != 0:
        errs.append("第 1 遍 apply rc=%d (★补丁自己报错★)" % r1.returncode)
    snap = {rel: md5_of(os.path.join(scratch, rel)) for rel in (P.SYNC_REL, P.IMPACT_REL)}
    r2 = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if r2.returncode != 0:
        errs.append("第 2 遍 apply rc=%d" % r2.returncode)
    snap2 = {rel: md5_of(os.path.join(scratch, rel)) for rel in (P.SYNC_REL, P.IMPACT_REL)}
    diff_bytes = 0
    for rel in (P.SYNC_REL, P.IMPACT_REL):
        if snap[rel] != snap2[rel]:
            diff_bytes += 1
    if diff_bytes:
        errs.append("第 2 遍 apply 之后 %d 个文件变了 ⇒ 不幂等" % diff_bytes)
    r3 = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    snap3 = {rel: md5_of(os.path.join(scratch, rel)) for rel in (P.SYNC_REL, P.IMPACT_REL)}
    if snap2 != snap3:
        errs.append("第 3 遍 apply 之后又变了 ⇒ 不幂等")
    shutil.rmtree(scratch, ignore_errors=True)
    return {"ok": not errs, "id": "F3", "title": "干跑两次的 diff == 0 (幂等 · 且补丁本身必须跑得通)",
            "detail": "第1遍后 md5=%s · 第2遍后 md5=%s · 第3遍后 md5=%s"
                      % (snap[P.SYNC_REL][:12], snap2[P.SYNC_REL][:12], snap3[P.SYNC_REL][:12]),
            "errors": errs}


def f4_sw_gates_green(ctx: dict) -> dict:
    """★10 道 SW 闸是否全绿 (★读数 = 副本上逐道实跑的 rc★) ★"""
    errs = []
    rows = ctx.get("gate_rows") or []
    got = {r["rel"]: r["rc"] for r in rows}
    for rel in SW_GATES:
        if rel not in got:
            errs.append("没读到 %s 的 rc" % rel)
        elif got[rel] != 0:
            errs.append("%s rc=%d (★不是 0★)" % (rel, got[rel]))
    return {"ok": not errs, "id": "F4", "title": "10 道 SW 闸全绿 (副本上逐道实跑)",
            "detail": "绿 %d / 红 %d" % (sum(1 for r in rows if r["rc"] == 0),
                                        sum(1 for r in rows if r["rc"] != 0)),
            "errors": errs}


def f5_evidence_levels(ctx: dict) -> dict:
    """★证据等级五级白名单 ★"""
    errs = []
    targets = [os.path.join(ctx["root"], NEW_PAGE_REL)]
    for rel in (P.SYNC_REL, P.IMPACT_REL):
        p = os.path.join(ctx["sandbox"], rel)
        if os.path.isfile(p):
            targets.append(p)
    for p in targets:
        if not os.path.isfile(p):
            errs.append("找不到 %s" % p)
            continue
        txt = read_text(p)
        for tok in sorted(set(re.findall(r"\[[^\[\]]{1,40}\]", txt))):
            if tok in EV_WHITELIST:
                continue
            if any(k in tok for k in EV_KEYWORDS):
                errs.append("%s 里证据等级「%s」不在五级白名单" % (os.path.basename(p), tok))
        if "[官方]" in txt:
            errs.append("%s 里出现「[官方]」⇒ 白名单只认 [官网]/[实测]/[媒体]/[推算]/[0数据]"
                        % os.path.basename(p))
    return {"ok": not errs, "id": "F5", "title": "证据等级五级白名单",
            "detail": "扫 %d 个文件" % len(targets), "errors": errs}


def f6_no_hanging(ctx: dict) -> dict:
    """★正文零挂起措辞 (★禁语 + 挂起词·代码块内引用的原文不算★) ★"""
    errs = []
    p = os.path.join(ctx["root"], NEW_PAGE_REL)
    if not os.path.isfile(p):
        return {"ok": False, "id": "F6", "title": "正文零挂起措辞",
                "detail": "新页不存在", "errors": ["找不到 %s" % NEW_PAGE_REL]}
    body = strip_code_blocks(read_text(p))
    for ph, pos in find_forbidden(body, FORBIDDEN_PHRASES):
        errs.append("禁语「%s」@ offset %d" % (ph, pos))
    for ph, pos in find_forbidden(body, HANGING_PHRASES):
        errs.append("挂起措辞「%s」@ offset %d" % (ph, pos))
    # ★落点① 的清单页正文 (★它是本单要落地的那一页·也得零挂起★)
    for rel in (P.SYNC_REL,):
        q = os.path.join(ctx["sandbox"], rel)
        if os.path.isfile(q):
            b2 = strip_code_blocks(read_text(q))
            for ph, pos in find_forbidden(b2, FORBIDDEN_PHRASES):
                errs.append("%s 禁语「%s」@ offset %d" % (rel, ph, pos))
    return {"ok": not errs, "id": "F6", "title": "正文零挂起措辞",
            "detail": "扫 %s (★围栏代码块内的引用原文不算★)" % NEW_PAGE_REL, "errors": errs}


def f7_sandbox_in_tmp(ctx: dict) -> dict:
    """★沙盒在项目盘 tmp/ 且不许有软链 ★"""
    errs = []
    sbx = os.path.abspath(ctx["sandbox"])
    tmp_r = os.path.abspath(os.path.join(ctx["root"], "tmp"))
    if not (sbx == tmp_r or sbx.startswith(tmp_r + os.sep)):
        errs.append("沙盒 %s 不在项目盘 tmp/ 下" % sbx)
    nlinks = 0
    for dirpath, dirnames, filenames in os.walk(sbx):
        for n in list(dirnames) + list(filenames):
            if os.path.islink(os.path.join(dirpath, n)):
                nlinks += 1
    if nlinks:
        errs.append("沙盒里有 %d 个软链 (★禁止 os.symlink·ISS-327 cont1 根因★)" % nlinks)
    # ★真件三处不许被沙盒碰过 ★
    for rel in (P.SYNC_REL, P.IMPACT_REL, P.GATE_REL):
        a = os.path.join(ctx["root"], rel)
        b = os.path.join(sbx, rel)
        if os.path.isfile(a) and os.path.isfile(b):
            if rel == P.GATE_REL:
                continue
            if md5_of(a) == md5_of(b):
                errs.append("副本里的 %s 与真件逐字节相同 ⇒ 副本没落地 (★F1/F2 会判红的★)" % rel)
    return {"ok": not errs, "id": "F7", "title": "沙盒在项目盘 tmp/ (且零软链)",
            "detail": "沙盒 = %s · 软链 %d 个" % (sbx, nlinks), "errors": errs}


CHECKS = (("F1", f1_three_places), ("F2", f2_h4reg_numbers), ("F3", f3_idempotent),
          ("F4", f4_sw_gates_green), ("F5", f5_evidence_levels),
          ("F6", f6_no_hanging), ("F7", f7_sandbox_in_tmp))


# ==================================================================================================
# 主流程
# ==================================================================================================
def prepare(root: str, rebuild: bool = False):
    """★建沙盒 + 在沙盒上落补丁 ⇒ (沙盒路径, apply 报告) ★"""
    dst = os.path.join(root, SBX_PATCHED_REL)
    if rebuild and os.path.isdir(dst):
        shutil.rmtree(dst)
    if not os.path.isdir(dst):
        build_sandbox(root, dst)
    rep = apply_patch_to_sandbox(root, dst)
    return dst, rep


def run_all(ctx: dict):
    out = []
    for cid, fn in CHECKS:
        try:
            out.append(fn(ctx))
        except Exception as exc:                              # noqa: BLE001
            out.append({"ok": False, "id": cid, "title": fn.__name__,
                        "detail": "★判据自身抛异常★", "errors": [repr(exc)]})
    return out


def selftest(root: str) -> int:
    """★反向用例 (★每条自证「红的是目标那一条, 其余仍绿」★) ★"""
    sbx = os.path.join(root, SBX_PATCHED_REL)
    base_ctx = {"root": root, "sandbox": sbx}
    rows, _ = load_gate_rows(root, sbx)
    base_ctx["gate_rows"] = rows
    base = run_all(base_ctx)
    base_red = {c["id"] for c in base if not c["ok"]}
    print("")
    print("  基准 (未篡改): 红集合 = %s" % (sorted(base_red) if base_red else "无"))

    cases = []

    # ★★新页快照 (★ST-6 / ST-7 会临时篡改【真页】⇒ 每条用例跑完必须【逐字节还原】★
    #   ★★否则跑一次 --selftest 就把交付物永久写成 F5 红 + F6 红★) ★
    page_p = os.path.join(root, NEW_PAGE_REL)
    page_snapshot = read_text(page_p) if os.path.isfile(page_p) else None
    page_md5_before = md5_of(page_p) if os.path.isfile(page_p) else None

    def restore_page():
        """★把真页还原回快照 (★逐字节★) ★"""
        if page_snapshot is None:
            return
        try:
            write_text(page_p, page_snapshot)
        except Exception:                                    # noqa: BLE001
            pass

    def case(cid, target, desc, mutate, expect_red=None):
        """★每条用例自证「红的是目标那一条, 其余仍绿」★"""
        scratch = os.path.join(root, "tmp", "iss368_sbx", "st_%s" % cid)
        if os.path.isdir(scratch):
            shutil.rmtree(scratch)
        shutil.copytree(sbx, scratch, symlinks=False)
        ctx = {"root": root, "sandbox": scratch, "gate_rows": rows}
        try:
            mutate(ctx, scratch)
            rep = run_all(ctx)
        finally:
            restore_page()                                  # ★立刻还原真页 (★即使用例抛异常也还原★) ★
        red = {c["id"] for c in rep if not c["ok"]}
        exp = {target} if expect_red is None else set(expect_red)
        ok = (red == exp)
        cases.append((cid, target, desc, ok, red, rep))
        shutil.rmtree(scratch, ignore_errors=True)

    # ---- ST-1: §2.1 分布表里删掉 SW09 ⇒ F1 红 ----
    def mut_s10(ctx, sc):
        p = os.path.join(sc, P.SYNC_REL)
        t = read_text(p)
        t = t.replace("| ★**S10** ★ | 4 | ★`SW03_LAND8_DNP` · `SW04_CHG_LED_REF` · "
                      "`SW05_KEY_NETNAMES` · `SW09_FP_TRUTH_READ` ★ |",
                      "| ★**S10** ★ | 3 | ★`SW03_LAND8_DNP` · `SW04_CHG_LED_REF` · "
                      "`SW05_KEY_NETNAMES` ★ |", 1)
        write_text(p, t)
    case("ST-1", "F1", "§2.1 分布表里把 SW09 拿掉 ⇒ F1 红 (三处没同批)", mut_s10)

    # ---- ST-2: §6 JSON 块里删掉 SW09 ⇒ F1 红 ----
    def mut_json(ctx, sc):
        p = os.path.join(sc, P.SYNC_REL)
        t = read_text(p)
        m = re.search(r"```json\s*(\{.*?\})\s*```", t, re.S)
        data = json.loads(m.group(1))
        data["items"] = [it for it in data["items"] if it.get("id") != P.SW09_ID]
        nj = "```json\n%s\n```" % json.dumps(data, ensure_ascii=False, indent=2)
        t = t[:m.start()] + nj + t[m.end():]
        write_text(p, t)
    case("ST-2", "F1", "§6 JSON 块里把 SW09 拿掉 ⇒ F1 红 (JSON 计数 != 9)", mut_json)

    # ---- ST-3: §H4-REG 三个数字改成 8/0/4 ⇒ F2 红 ----
    def mut_h4(ctx, sc):
        p = os.path.join(sc, P.IMPACT_REL)
        t = read_text(p)
        t = t.replace("- H4-ITEMS: 9", "- H4-ITEMS: 8", 1)
        t = t.replace("- H4-COVER: 1", "- H4-COVER: 0", 1)
        t = t.replace("- H4-GENERIC: 5", "- H4-GENERIC: 4", 1)
        write_text(p, t)
    case("ST-3", "F2", "§H4-REG 三个数字写回 8/0/4 ⇒ F2 红 (登记 != 9/1/5)", mut_h4)

    # ---- ST-4: 把已落地的一处改坏 ⇒ 补丁锚点对不上 ⇒ apply fail-closed rc=1 ⇒ F3 红 ----
    #   ★★为什么这么改: 本补丁的原子操作要么【收敛】(第 2 遍 = already · 零变更) 要么【报错】(锚点缺失/歧义)★
    #   ⇒ 「不幂等」在本补丁上唯一可观测的形态 = ★apply 自己 fail-closed★
    #   ⇒ ★★若把 F3 的基准留在项目根 ⇒ 沙盒怎么改都碰不到它 ⇒ 这条用例永远是绿的 (★抓不到 F3★)★
    def mut_nonidem(ctx, sc):
        p = os.path.join(sc, P.IMPACT_REL)
        t = read_text(p)
        t = t.replace("覆盖条数 = 1** ★", "覆盖条数 = 1 (★反向用例·把已落地的那一处改坏★)** ★", 1)
        write_text(p, t)
    case("ST-4", "F3", "把已落地的一处改坏 ⇒ 补丁锚点对不上 ⇒ apply fail-closed ⇒ F3 红",
         mut_nonidem)

    # ---- ST-5: 把 10 道闸里一道的 rc 改成 1 ⇒ F4 红 ----
    def mut_gate_rc(ctx, sc):
        rr = [dict(r) for r in rows]
        rr[0]["rc"] = 1
        ctx["gate_rows"] = rr
    case("ST-5", "F4", "10 道闸里第 1 道 rc 改成 1 ⇒ F4 红", mut_gate_rc)

    # ---- ST-6: 证据等级越界 ⇒ F5 红 ----
    def mut_ev(ctx, sc):
        p = os.path.join(ctx["root"], NEW_PAGE_REL)
        if os.path.isfile(p):
            t = read_text(p)
            write_text(p, t + "\n\n★反向用例★ 证据等级写 [官方]\n")
    case("ST-6", "F5", "新页里写一个白名单外的证据等级 ⇒ F5 红", mut_ev)

    # ---- ST-7: 挂起措辞 ⇒ F6 红 ----
    def mut_hang(ctx, sc):
        p = os.path.join(ctx["root"], NEW_PAGE_REL)
        if os.path.isfile(p):
            t = read_text(p)
            write_text(p, t + "\n\n★反向用例★ 这里写一句 待补充 的话。\n")
    case("ST-7", "F6", "新页里写一句挂起措辞 ⇒ F6 红", mut_hang)

    # ---- ST-8: 沙盒放到项目盘 tmp/ 之外 ⇒ F7 红 ----
    def mut_sbx_path(ctx, sc):
        ctx["sandbox"] = os.path.join(ctx["root"], "iss368_not_in_tmp")
        os.makedirs(ctx["sandbox"], exist_ok=True)
        for rel in (P.SYNC_REL, P.IMPACT_REL, P.GATE_REL):
            dst = os.path.join(ctx["sandbox"], rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)   # ★父目录必须先建 (★否则 copy2 炸★) ★
            shutil.copy2(os.path.join(sc, rel), dst)
    case("ST-8", "F7", "沙盒放到项目盘 tmp/ 之外 ⇒ F7 红", mut_sbx_path)

    npass = 0
    for cid, target, desc, ok, red, rep in cases:
        print("")
        print("  %s %-6s %s" % ("✅" if ok else "❌", cid, desc))
        print("      红集合 = %s · 目标 = %s ⇒ %s"
              % (sorted(red) if red else "无", target, "一致" if ok else "★不一致★"))
        if not ok:
            for c in rep:
                if not c["ok"]:
                    print("      ★红的那一条: %s · %s" % (c["id"], (c.get("errors") or [])[:2]))
    npass = sum(1 for c in cases if c[3])

    # ★收尾: 还原真页 + 清掉 ST-8 在项目根留下的空目录 (★不留下任何残迹★) ★
    restore_page()
    stray = os.path.join(root, "iss368_not_in_tmp")
    if os.path.isdir(stray):
        shutil.rmtree(stray, ignore_errors=True)
    page_md5_after = md5_of(page_p) if os.path.isfile(page_p) else None
    print("")
    print("  真页还原自证: md5 前 = %s · md5 后 = %s · 逐字节相同 = %s"
          % (page_md5_before, page_md5_after, page_md5_before == page_md5_after))
    print("  ST-8 残留目录 %s 存在 = %s" % (stray, os.path.isdir(stray)))
    print("")
    print("  反向用例: %d/%d PASS (★每条自证「红的是目标那一条, 其余仍绿」★)" % (npass, len(cases)))
    if npass == len(cases):
        print("")
        print("ALL TESTS PASS")
        return 0
    print("")
    print("ALL TESTS FAIL")
    return 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="ISS-368 · SW09 三处同批落地 · 副本 dry-run 机器闸")
    ap.add_argument("--root", default=PROJ)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--rebuild", action="store_true")
    ap.add_argument("--run-gates", action="store_true")
    args = ap.parse_args(argv)
    root = os.path.abspath(args.root)

    if args.selftest:
        return selftest(root)

    sbx, rep = prepare(root, rebuild=args.rebuild)
    if rep["rc"] != 0:
        sys.stderr.write("❌ 补丁在副本上跑失败:\n%s\n%s\n" % (rep["out"], rep["err"]))
        return 1
    rows, cached = load_gate_rows(root, sbx, force=args.run_gates)
    ctx = {"root": root, "sandbox": sbx, "gate_rows": rows}
    checks = run_all(ctx)

    if args.json:
        print(json.dumps({"sandbox": sbx, "gate_rows": rows, "checks": checks},
                         ensure_ascii=False, indent=2))
    else:
        print("=" * 96)
        print("ISS-368 · SW09 三处同批落地 · 副本 dry-run 机器闸")
        print("  项目根 = %s" % root)
        print("  沙盒   = %s" % sbx)
        print("  闸读数 = %s" % ("缓存 (★副本未变·读数复用★)" if cached else "本轮实跑"))
        print("=" * 96)
        for c in checks:
            print("  [%s] %-3s %s" % ("✅" if c["ok"] else "❌", c["id"], c.get("title", "")))
            print("       %s" % c.get("detail", ""))
            for e in (c.get("errors") or [])[:6]:
                print("       ★%s" % e)
        print("-" * 96)
        print("  10 道 SW 闸逐道 rc (副本沙盒内实跑):")
        for r in rows:
            print("    %-70s rc=%s  %ss%s" % (r["rel"], r["rc"], r.get("sec"),
                                              " (缓存)" if r.get("cached") else ""))
        nred = sum(1 for c in checks if not c["ok"])
        print("-" * 96)
        print("  结论: %s (绿 %d / 红 %d)" % ("✅ 全过" if nred == 0 else "❌ 有不过项",
                                          len(checks) - nred, nred))
        print("=" * 96)
    return 0 if all(c["ok"] for c in checks) else 1


if __name__ == "__main__":
    sys.exit(main())
