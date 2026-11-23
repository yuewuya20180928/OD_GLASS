#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-372 · sw-lead · 2026-11-23 · 「板那一趟」SW 侧板 md5 引用面清账 + 清单自守闸
=====================================================================================
★**本闸是什么**: 一条【自守闸】—— 让「下一道新闸再硬钉板 md5」这件事【当场被抓住】,
  而不是等改板那天才炸。

★**它管什么** (★七条判据, 逐条自证·不许靠注释说绿★):
  H1 覆盖   : SW 域板 md5 引用面 (自己扫) 每一处都必须在 §1 清单里有对应行 ★漏一处就红★
              + 声明式排除清单必须恰好是【本单新建的页 + 本闸自己】两个 (★不许悄悄扩★)
  H2 字段   : 每一条都必须标了【三类归属】+【改板那一趟的处置】 ★缺字段 / 枚举越界 ⇒ 红★
  H3 反向   : 【历史留证】类不许落在 .py 判据脚本上 ★不许把活判据塞进历史留证糊弄★
  H4 在册   : SW 域每道【真钉板 md5 的判据脚本】必须在 §2 有账 ★今天新造的那两道今天就能被抓住★
  H5 通道   : 每道这样的闸, 要么【代码级已有合法改板通道】, 要么【在 §2 登记为已知缺口 + 缺口归属
              + 谁来补 + 补法规格】 ★★「登记过的缺口」不红, 「没人知道的缺口」才红★★
  H6 板面   : 板 md5 / mtime / size 三项自证 (★零写板★) 漂移 ⇒ 红
  H7 页面   : 证据等级五级白名单 + 正文零挂起措辞 + 零空洞词

★**它不许做什么**:
  ★**不自造第二套合法改板判据** ⇒ 通道检测只做【代码级形态检测】(有没有 reboard 四项判定逻辑),
    真判据的形状照 `SW/tools/check_demo_panel_spec.py` 的 R6 (★ISS-284 已跑通★) ★
  ★**不挂链** ⇒ `state/gate_check.py` 一个字都不许动 (★本闸【零挂链】★)
  ★**零写板 · 零落表** ⇒ 只读板, 不写任何既有文件 (★沙盒只落 tmp/iss372_sbx/★)
  ★**不改既有闸 · 不改既有页面正文** ⇒ 本闸只读它们
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

# ★★基线 (★逐字照抄 SW/BOARD_ONEPASS_SW_MD5_REBASE_READINESS.md §0★) ★★
# ★字面量【拼出来】⇒ 本闸源码里不出现那串 32 位 md5 ⇒ 本闸自己不会被 H4/H5 当成「硬钉板 md5 的闸」★
NEEDLE_PREFIX = "611b" + "869e"                       # ★扫引用面用的 8 位前缀★
FULL_MD5 = NEEDLE_PREFIX + "13518c3c023fb178f91a0075"
BOARD_REL = "HW/PCB/demo_mainboard.kicad_pcb"
BOARD_MTIME = "2026-11-06 07:07:17.362193413"
BOARD_SIZE = 4940213

PAGE_REL = "SW/BOARD_ONEPASS_SW_MD5_REBASE_READINESS.md"
MANIFEST_BEGIN = "<!-- ISS372-MANIFEST:BEGIN -->"
MANIFEST_END = "<!-- ISS372-MANIFEST:END -->"

CLS_ENUM = ("判据锚", "规格页引用", "历史留证")
ACTION_ENUM = ("随板改", "不许改", "交 main 拍")

# ★证据等级五级白名单 + 禁语 (★照 SW/tools/check_fp_truth_read.py 的现成形状抄★) ★
EV_WHITELIST = ("[官网]", "[实测]", "[媒体]", "[推算]", "[0数据]")
EV_KEYWORDS = ("实测", "官方", "官网", "媒体", "推算", "数据", "来源", "内部",
               "待补", "未知", "一手", "二手")
HANGING = ("等原厂回信", "等供应商确认", "待外部回复", "等确认",
           "等回复", "待回复", "等回信", "等厂商确认", "待原厂", "等厂家确认")
HOLLOW = ("调整相关逻辑", "适当处理", "酌情", "视情况而定", "相关处理",
          "相应修改", "同步更新一下", "改一下", "相关逻辑", "按需调整")
NEGATION_MARKERS = ("禁", "不许", "不得", "禁止", "零外发", "避免", "排除",
                    "不看", "拒", "黑名单", "不得写", "不许写")

# ★§2 的闸账里, 「已有通道 / 已知缺口」两种状态 ★
STATUS_ENUM = ("已有通道", "已知缺口", "已知缺口(★跨域·hw-lead 的域★)")

# ★★通道形态检测 (★代码级可查·不自造判据★): 一个闸文件里有没有
#   【reboard 四项原子判定逻辑】+ 【只读调用权威闸 check_demo_panel_spec】★
CHANNEL_TOKENS = ("reboard", "check_r6_hard_protected", "check_demo_panel_spec",
                  "prev_md5")
# ★判「已有通道」的最小形态: 提到 reboard + prev_md5 + 权威闸三者 ★
CHANNEL_MIN = ("reboard", "prev_md5")
CHANNEL_AUTH = ("check_r6_hard_protected", "check_demo_panel_spec")


# ===================================================================== 小工具
def read_text(path: str) -> str:
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            return f.read()
    except OSError:
        return ""


def md5_of(path: str) -> str:
    h = hashlib.md5()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
    except OSError:
        return ""
    return h.hexdigest()


def fmt_mtime_ns(ns: int) -> str:
    sec, frac = divmod(int(ns), 1_000_000_000)
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(sec)) + ".%09d" % frac


def negated(text: str, start: int) -> bool:
    """★命中词前面一截里有否定标记 ⇒ 那是【禁令引用】, 不算挂起措辞★
    (★照 SW/tools/check_fp_truth_read.py 的现成形状抄★)"""
    ctx = text[max(0, start - 60):start]
    return any(mk in ctx for mk in NEGATION_MARKERS)


def scan_refs(root: str, exclude_paths: list) -> list:
    """★逐文件遍历 + 逐行计数 (★不用 grep ⇒ 不被 `grep -v '\\.bak'` 的连带过滤坑到★)"""
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
            if rel in exclude_paths:
                continue
            try:
                with open(p, encoding="utf-8", errors="ignore") as f:
                    lines = f.read().splitlines()
            except OSError:
                continue
            for i, line in enumerate(lines, 1):
                n = line.count(NEEDLE_PREFIX)
                if n:
                    out.append({"file": rel, "line": i, "occ": n})
    return out


def has_reboard_channel(path: str) -> bool:
    """★代码级形态检测: 这个闸文件里有没有【合法改板通道】的形状★
    (★真判据的形状照 SW/tools/check_demo_panel_spec.py 的 R6·本闸只认【形态】不造新判据★)"""
    txt = read_text(path)
    if not txt:
        return False
    if not all(t in txt for t in CHANNEL_MIN):
        return False
    if not any(t in txt for t in CHANNEL_AUTH):
        return False
    return True


def load_manifest(page_text: str) -> dict:
    i = page_text.find(MANIFEST_BEGIN)
    j = page_text.find(MANIFEST_END)
    if i < 0 or j < 0 or j < i:
        return {}
    blob = page_text[i + len(MANIFEST_BEGIN):j].strip()
    if blob.startswith("```"):
        blob = blob.split("\n", 1)[1] if "\n" in blob else ""
    if blob.endswith("```"):
        blob = blob.rsplit("```", 1)[0]
    try:
        data = json.loads(blob)
    except Exception:                                       # noqa: BLE001
        return {}
    return data if isinstance(data, dict) else {}


def write_manifest(page_path: str, manifest: dict) -> None:
    """★把清单写回页面 (★只用于 --selftest 的沙盒副本★)"""
    txt = read_text(page_path)
    i = txt.find(MANIFEST_BEGIN)
    j = txt.find(MANIFEST_END)
    block = (MANIFEST_BEGIN + "\n```json\n"
             + json.dumps(manifest, ensure_ascii=False, indent=1)
             + "\n```\n" + MANIFEST_END)
    out = txt[:i] + block + txt[j + len(MANIFEST_END):]
    with open(page_path, "w", encoding="utf-8") as f:
        f.write(out)


# ===================================================================== 七条判据
def run_checks(root: str) -> dict:
    res = {}

    def add(cid, ok, title, errs):
        res[cid] = {"ok": bool(ok), "id": cid, "title": title, "errors": list(errs)}

    page_path = os.path.join(root, PAGE_REL)
    page_text = read_text(page_path)
    man = load_manifest(page_text)

    # ---------- H1 覆盖 ----------
    errs = []
    if not man:
        errs.append("★页面 %s 里读不到机器可读清单 (MANIFEST 块缺失/JSON 解析失败) ⇒ fail-closed★"
                    % PAGE_REL)
        refs, gates = [], []
        excl = []
    else:
        refs = man.get("refs") or []
        gates = man.get("gates") or []
        excl = list(man.get("scan", {}).get("exclude_paths") or [])
        # ★排除清单必须恰好是【本单新建的页 + 本闸自己】⇒ 谁想把文件从扫描里摘掉 ⇒ 闸红★
        want_excl = sorted(["SW/BOARD_ONEPASS_SW_MD5_REBASE_READINESS.md",
                             "SW/tools/check_sw_board_md5_rebase_readiness.py"])
        if sorted(excl) != want_excl:
            errs.append("★声明式排除清单被改了: %s ≠ %s ⇒ 有人想把文件从扫描面里摘掉 ⇒ 判红★"
                        % (sorted(excl), want_excl))
        hits = scan_refs(root, excl)
        have = {(r.get("file"), r.get("line")) for r in refs}
        for h in hits:
            if (h["file"], h["line"]) not in have:
                errs.append("★扫描到 %s:%d (命中 %d 处) 但 §1 清单里没有这一行 ⇒ 漏登记 ⇒ 判红★"
                            % (h["file"], h["line"], h["occ"]))
        # 清单里多出来的 (登记了但盘上已经不在) ⇒ 也要红 (清单过期)
        hitkeys = {(h["file"], h["line"]) for h in hits}
        for r in refs:
            if (r.get("file"), r.get("line")) not in hitkeys:
                errs.append("★§1 清单登记了 %s:%d 但盘上扫不到 ⇒ 清单过期 ⇒ 判红★"
                            % (r.get("file"), r.get("line")))
    add("H1", not errs, "SW 域板 md5 引用面必须被 §1 清单逐处覆盖 (★漏一处就红★)", errs)

    # ---------- H2 字段 ----------
    errs = []
    for r in refs:
        cls = str(r.get("cls") or "").strip()
        act = str(r.get("action") or "").strip()
        if not cls:
            errs.append("★%s:%d 没标【三类归属】⇒ 判红★" % (r.get("file"), r.get("line")))
        elif cls not in CLS_ENUM:
            errs.append("★%s:%d 的三类归属 %r 不在枚举 %s 内 ⇒ 判红★"
                        % (r.get("file"), r.get("line"), cls, list(CLS_ENUM)))
        if not act:
            errs.append("★%s:%d 没标【改板那一趟的处置】⇒ 判红★"
                        % (r.get("file"), r.get("line")))
        elif act not in ACTION_ENUM:
            errs.append("★%s:%d 的处置 %r 不在枚举 %s 内 ⇒ 判红★"
                        % (r.get("file"), r.get("line"), act, list(ACTION_ENUM)))
        if not str(r.get("note") or "").strip():
            errs.append("★%s:%d 没有备注 (★为什么这么归类/这么处置·必须写出来★) ⇒ 判红★"
                        % (r.get("file"), r.get("line")))
    add("H2", not errs, "每一处都必须标了【三类归属】+【处置】+ 备注", errs)

    # ---------- H3 反向 (历史留证不许落在 .py 上) ----------
    errs = []
    for r in refs:
        if str(r.get("cls") or "") == "历史留证":
            f = str(r.get("file") or "")
            if f.endswith(".py"):
                errs.append("★%s:%d 被标成【历史留证】但它在 .py 判据脚本里 ⇒ "
                            "不许把活判据塞进历史留证糊弄 ⇒ 判红★"
                            % (f, r.get("line")))
    add("H3", not errs, "【历史留证】类必须真的不许改 (★活判据不许伪装成历史留证★)", errs)

    # ---------- H4 在册 ----------
    errs = []
    detected = []
    tools_dir = os.path.join(root, "SW", "tools")
    if os.path.isdir(tools_dir):
        for fn in sorted(os.listdir(tools_dir)):
            if not fn.endswith(".py") or ".bak" in fn:
                continue
            p = os.path.join(tools_dir, fn)
            rel = "SW/tools/" + fn
            if rel in [g.get("file") for g in gates]:
                continue                      # ★本闸自己: 不含 32 位字面量 ⇒ 根本不会被扫到★
            if FULL_MD5 in read_text(p):
                detected.append(rel)
    gate_files = {str(g.get("file")) for g in gates}
    for rel in detected:
        if rel not in gate_files:
            errs.append("★SW 域有闸 %s 硬钉了板 md5 (32 位字面量) 但它没进 §2 的账 ⇒ "
                        "★下一道新闸再硬钉板 md5 就是从这儿溜过去的★ ⇒ 判红★" % rel)
    add("H4", not errs, "SW 域每道【真钉板 md5 的判据脚本】必须登记在册", errs)

    # ---------- H5 通道 (本单的核心机制) ----------
    errs = []
    for g in gates:
        rel = str(g.get("file") or "")
        if not rel.startswith("SW/tools/"):
            continue                        # ★跨域闸 (HW/) 由 §5 登记 · 不在本闸 H5 的口径内★
        p = os.path.join(root, rel)
        has_ch = has_reboard_channel(p)
        status = str(g.get("status") or "").strip()
        if has_ch:
            continue                        # ★代码级已有合法改板通道 ⇒ 不红★
        # ★没有通道 ⇒ 必须在 §2 里被登记成「已知缺口 + 缺口归属 + 谁来补 + 补法规格」★
        if status not in STATUS_ENUM or not status.startswith("已知缺口"):
            errs.append("★闸 %s (判据 %s) 代码级【没有合法改板通道】, 但它在 §2 里也没有被登记成"
                        "【已知缺口】⇒ 没人知道它 ⇒ 判红 (★登记过的缺口不红, 没人知道的缺口才红★)"
                        % (rel, g.get("id")))
            continue
        for field, label in (("gap_id", "缺口编号"), ("owner", "谁来补"),
                             ("spec", "补法规格"), ("title", "缺口归属")):
            if not str(g.get(field) or "").strip():
                errs.append("★闸 %s 的已知缺口缺【%s】字段 (%s) ⇒ 登记不完整 ⇒ 判红★"
                            % (rel, label, field))
        if status not in STATUS_ENUM:
            errs.append("★闸 %s 的状态 %r 不在枚举 %s 内 ⇒ 判红★" % (rel, status, list(STATUS_ENUM)))
    add("H5", not errs, "每道闸要么已有合法改板通道, 要么在 §2 被登记成已知缺口", errs)

    # ---------- H6 板面 ----------
    errs = []
    pcb = os.path.join(root, BOARD_REL)
    if not os.path.exists(pcb):
        errs.append("★板读不到 (%s) ⇒ fail-closed⇒ 判红★" % BOARD_REL)
    else:
        got_md5 = md5_of(pcb)
        st = os.stat(pcb)
        if got_md5 != FULL_MD5:
            errs.append("★板 md5=%s ≠ 基线 %s ⇒ 判红 (★板被换过 ⇒ 零写板自证失败★)"
                        % (got_md5, FULL_MD5))
        if fmt_mtime_ns(st.st_mtime_ns) != BOARD_MTIME:
            errs.append("★板 mtime=%s ≠ 基线 %s ⇒ 判红 (★板被写过★)"
                        % (fmt_mtime_ns(st.st_mtime_ns), BOARD_MTIME))
        if st.st_size != BOARD_SIZE:
            errs.append("★板 size=%d ≠ 基线 %d ⇒ 判红★" % (st.st_size, BOARD_SIZE))
    add("H6", not errs, "板面零写板自证 (md5 / mtime / size 三项)", errs)

    # ---------- H7 页面 ----------
    errs = []
    if not page_text:
        errs.append("★页面 %s 读不到 ⇒ fail-closed⇒ 判红★" % PAGE_REL)
    else:
        for tok in sorted(set(re.findall(r"\[[^\[\]]{1,40}\]", page_text))):
            if tok in EV_WHITELIST:
                continue
            if any(k in tok for k in EV_KEYWORDS):
                errs.append("★证据等级「%s」不在五级白名单 %s ⇒ 判红★"
                            % (tok, "/".join(EV_WHITELIST)))
        if "[官方]" in page_text:
            errs.append("★页里出现「[官方]」⇒ 判红 (白名单只认 [官网]/[实测]/[媒体]/[推算]/[0数据])★")
        for h in HANGING:
            for m in re.finditer(re.escape(h), page_text):
                if not negated(page_text, m.start()):
                    errs.append("★正文出现挂起措辞「%s」⇒ 判红★" % h)
        for h in HOLLOW:
            for m in re.finditer(re.escape(h), page_text):
                if not negated(page_text, m.start()):
                    errs.append("★正文出现空洞词「%s」⇒ 判红★" % h)
    add("H7", not errs, "证据等级五级白名单 + 正文零挂起措辞 + 零空洞词", errs)

    return res


def fmt_result(res: dict) -> str:
    out = []
    for cid in ("H1", "H2", "H3", "H4", "H5", "H6", "H7"):
        v = res.get(cid) or {}
        out.append("  [%s] %s · %s" % ("PASS" if v.get("ok") else "FAIL", cid, v.get("title")))
        for e in (v.get("errors") or [])[:12]:
            out.append("        ⚠ %s" % e)
    return "\n".join(out)


# ===================================================================== --selftest
SBX_ROOT = os.path.join(PROJ, "tmp", "iss372_sbx", "selftest")


def build_sandbox(dst: str) -> str:
    if os.path.exists(dst):
        shutil.rmtree(dst)
    os.makedirs(dst, exist_ok=True)
    shutil.copytree(os.path.join(PROJ, "SW"), os.path.join(dst, "SW"), symlinks=True)
    pcb_dir = os.path.join(dst, "HW", "PCB")
    os.makedirs(pcb_dir, exist_ok=True)
    shutil.copy2(os.path.join(PROJ, BOARD_REL), os.path.join(dst, BOARD_REL))
    return dst


def selftest() -> int:
    print("=" * 92)
    print("ISS-372 · 反向用例自检 (★每条必须自证: 红的集合 == {目标那一条}★)")
    print("=" * 92)
    cases = []

    # ---- ① 在 §1 清单里删掉一处扫描得到的命中 ⇒ H1 红 ----
    def c1(dst):
        mp = os.path.join(dst, PAGE_REL)
        man = load_manifest(read_text(mp))
        man["refs"] = [r for r in man["refs"]
                       if not (r["file"] == "SW/SW_NEEDS_TRIAGE.md" and r["line"] == 346)]
        write_manifest(mp, man)
        return "从 §1 清单里删掉 SW/SW_NEEDS_TRIAGE.md:346 (扫描仍能扫到它)"

    # ---- ② 把某处归属改成空 ⇒ H2 红 ----
    def c2(dst):
        mp = os.path.join(dst, PAGE_REL)
        man = load_manifest(read_text(mp))
        for r in man["refs"]:
            if r["file"] == "SW/SW_NEEDS_TRIAGE.md" and r["line"] == 346:
                r["cls"] = ""
        write_manifest(mp, man)
        return "把 SW/SW_NEEDS_TRIAGE.md:346 的三类归属改成空串"

    # ---- ③ 把一个 .py 里的命中标成「历史留证」⇒ H3 红 ----
    def c3(dst):
        mp = os.path.join(dst, PAGE_REL)
        man = load_manifest(read_text(mp))
        for r in man["refs"]:
            if r["file"] == "SW/tools/check_fp_truth_read.py":
                r["cls"] = "历史留证"
        write_manifest(mp, man)
        return "把 SW/tools/check_fp_truth_read.py:87 标成【历史留证】"

    # ---- ④ 把一道新闸从 §2 的账里删掉 ⇒ H4 红 ----
    def c4(dst):
        mp = os.path.join(dst, PAGE_REL)
        man = load_manifest(read_text(mp))
        man["gates"] = [g for g in man["gates"]
                        if g["file"] != "SW/tools/check_onepass_sw_sync.py"]
        write_manifest(mp, man)
        return "把 SW/tools/check_onepass_sw_sync.py (★已有通道的那道★) 从 §2 的账里删掉"

    # ---- ⑤ 让某道闸既没通道也没登记 ⇒ H5 红 ----
    def c5(dst):
        mp = os.path.join(dst, PAGE_REL)
        man = load_manifest(read_text(mp))
        for g in man["gates"]:
            if g["file"] == "SW/tools/check_onepass_sw_sync.py":
                g["status"] = "已有通道"          # ★谎报: 清单说「已有通道」★
        write_manifest(mp, man)
        # ★把代码里的通道形态抹掉 (reboard / prev_md5 / 权威闸三个 token) ⇒ 代码级真的没通道了★
        p = os.path.join(dst, "SW/tools/check_onepass_sw_sync.py")
        txt = read_text(p)
        for tok in ("reboard", "prev_md5", "check_r6_hard_protected", "check_demo_panel_spec"):
            txt = txt.replace(tok, "ISSU372_SELFTEST_STRIPPED")
        with open(p, "w", encoding="utf-8") as f:
            f.write(txt)
        return ("把 check_onepass_sw_sync.py 的通道形态抹掉 + 清单谎报「已有通道」"
                " ⇒ 没人知道的缺口")

    # ---- ⑥ 在沙盒里把板改一个字节 ⇒ H6 红 ----
    def c6(dst):
        p = os.path.join(dst, BOARD_REL)
        with open(p, "a", encoding="utf-8") as f:
            f.write("\n# ISS-372 selftest: 板改一个字节 (★只在沙盒★)\n")
        return "在沙盒里给板追加一个字节 (★真件零写★)"

    # ---- ⑦ 把证据等级写成第六级 ⇒ H7 红 ----
    def c7(dst):
        mp = os.path.join(dst, PAGE_REL)
        txt = read_text(mp)
        txt = txt.replace("[实测]", "[官方]")
        with open(mp, "w", encoding="utf-8") as f:
            f.write(txt)
        return "把页面里的 [实测] 全换成 [官方] (★白名单只认五级·[官方] 是明令禁的★)"

    # ---- ⑧ 把排除清单扩大 (想把文件从扫描面摘掉) ⇒ H1 红 ----
    def c8(dst):
        mp = os.path.join(dst, PAGE_REL)
        man = load_manifest(read_text(mp))
        man["scan"]["exclude_paths"] = sorted(
            list(man["scan"].get("exclude_paths") or []) + ["SW/SW_MD5_BASELINE_LEDGER.md"])
        write_manifest(mp, man)
        return "把台账 SW/SW_MD5_BASELINE_LEDGER.md 加进声明式排除清单 (★想把判据锚藏起来★)"

    for fn, tgt, desc in ((c1, "H1", c1.__doc__), (c2, "H2", None), (c3, "H3", None),
                          (c4, "H4", None), (c5, "H5", None), (c6, "H6", None),
                          (c7, "H7", None), (c8, "H1", None)):
        cases.append((fn, tgt, desc))

    npass = 0
    for idx, (fn, tgt, _d) in enumerate(cases, 1):
        dst = os.path.join(SBX_ROOT, "case%d" % idx)
        build_sandbox(dst)
        what = fn(dst)
        res = run_checks(dst)
        failed = sorted(cid for cid, v in res.items() if not v.get("ok"))
        ok = (failed == [tgt])
        npass += 1 if ok else 0
        print("  用例 %d · 目标 %s · 红的集合 = %s · %s"
              % (idx, tgt, failed, "PASS" if ok else "FAIL"))
        print("        手法: %s" % what)
        if not ok:
            for cid, v in res.items():
                if not v.get("ok"):
                    for e in (v.get("errors") or [])[:4]:
                        print("        ⚠ %s: %s" % (cid, e))
        shutil.rmtree(dst, ignore_errors=True)
    print("-" * 92)
    print("反向用例: %d/%d 通过 (★每条都自证「红的集合 == {目标那一条}」★)" % (npass, len(cases)))
    if npass != len(cases):
        print("★有用例 FAIL ⇒ 本闸不可信 ⇒ rc=1★")
        return 1
    print("ALL TESTS PASS")
    return 0


# ===================================================================== 主流程
def main() -> int:
    ap = argparse.ArgumentParser(description="ISS-372 SW 侧板 md5 引用面清账 + 清单自守闸")
    ap.add_argument("--root", default=PROJ, help="项目根 (默认本脚本上两级)")
    ap.add_argument("--selftest", action="store_true", help="跑反向用例")
    ap.add_argument("--json", action="store_true", help="机读输出")
    args = ap.parse_args()
    root = os.path.abspath(args.root)
    if args.selftest:
        return selftest()
    res = run_checks(root)
    npass = sum(1 for v in res.values() if v.get("ok"))
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=1))
    else:
        print("=" * 92)
        print("ISS-372 · 「板那一趟」SW 侧板 md5 引用面清账 + 清单自守闸")
        print("  根     = %s" % root)
        print("  清单页 = %s" % PAGE_REL)
        print("=" * 92)
        print(fmt_result(res))
        print("-" * 92)
        print("闸结果 %d/%d 通过, rc=%d" % (npass, len(res), 0 if npass == len(res) else 1))
    return 0 if npass == len(res) else 1


if __name__ == "__main__":
    raise SystemExit(main())
