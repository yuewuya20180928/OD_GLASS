#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_onepass_s10_swap_set_truth.py —— ★★【ISS-373 · hw-lead · 「板那一趟」S10 换件集合唯一真源 · 机器闸】★★

★★★**★这个闸守的是什么★**★★
  「板只改一次」那一趟 (= 板 md5 只许变 1 次) 要换几件件封装 land, 这个数在同一个项目里
  ★**同时有 90 和 91 两套口径活着** (四份页面/脚本各写各的) ⇒
  ★**开工当天只要还有第二种口径, 就有人按错的那份布局 ⇒ 板 md5 变第二次 ⇒ 整趟白跑** ⇒
  ⇒ ★**本闸把「到底换几件」收成一条谁也改不掉的机器判据**:
     ★**集合算法自算 → 差集自己算 → 四处口径逐条对表 → `J_DEBUG` 四条腿齐全 → 写库名联动手在页里
     → 板面零写板自证 → 证据等级与零挂起措辞 → 本闸零挂链** ★

  闸的九条 (★每条 fail-closed · 每条带反向用例★):
    L0  ★**集合算法自算** ★ —— 脚本自己从 BOM + 网表 + ISS-356 基准块 + 覆盖缺口表算出
         (inter + gap) 与 (iss + gap) 两个数 ⇒ ★**页里写的数 ≠ 脚本实算 ⇒ 红** ★
         ★★**不许把 90 / 91 写死成常量**★★
    L1  ★**差集恰为 1 件且是脚本自己算出来的那件** ★ ⇒ 不是 1 件 ⇒ 红 ⇒ 差集变了 ⇒
         两套口径的差变了 ⇒ 全部下游数都要重算 ★
         ★★**不许写死一个名字就算过** ★★
    L2  页 §0 口径表两行都在, 且都带复跑命令
    L3  ★**四处口径逐条可查** ★ (路径 + 行号 + 那个数 + 定义还是算例) ⇒ 少一条 ⇒ 红 ⇒
         ★**行号处那一行必须真的含那一句原文; 写死的数还要活体复跑对得上** ★
    L4  ★**`J_DEBUG` 四条腿逐条齐全** ★ + 与 `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 的
         `B33_PIN_LAND_1P27` 交叉引到 ⇒ ★**该件换不换 land 的两边说法必须同时在页里出现,
         不许只留一边** ★
    L5  ★**写库名名单的联动手算式在页里** ★ (94 / 92 与 95 / 91 四个数 + 算式)
    L6  ★**板面零写板自证** ★ (md5 / mtime / size 三项)
    L7  ★**证据等级五级白名单** ★ (`[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]`) +
         ★**零挂起措辞** ★ + ★**判据句 / 事实句分开写** ★
    L8  ★**零挂链** ★ (★本闸【不许】挂进 `state/gate_check.py` ⇒ 挂不挂归 main★)

  ★**只读 import 既有闸** (`HW/check_fp_truth_coverage_gap.py` / `MECH/check_onepass_s10_fp_swap_impact.py`)
  ⇒ C4 / 靶子 / 缺口 三集合口径零漂移 ★
  ★**本闸是【新建】文件, 一个字节不改既有判据脚本; 也不改既有页面正文** ★

用法:
    python3 HW/check_onepass_s10_swap_set_truth.py            # rc=0 = 全绿
    python3 HW/check_onepass_s10_swap_set_truth.py --json     # 机器读
    python3 HW/check_onepass_s10_swap_set_truth.py --selftest # rc=0 = 反向用例全抓到
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, ".."))

PAGE_REL = os.path.join("HW", "PCB", "BOARD_ONEPASS_S10_SWAP_SET_TRUTH.md")
BOARD_REL = os.path.join("HW", "PCB", "demo_mainboard.kicad_pcb")
GATE_CHECK_REL = os.path.join("state", "gate_check.py")

MACH_BEGIN = "<!-- BEGIN ISS373 S10 换件集合真源机器块 -->"
MACH_END = "<!-- END ISS373 S10 换件集合真源机器块 -->"

# ★板面三项指纹 (★本单开工前 / 交卷后各打一次·逐字相同★) ★
BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"
BOARD_MTIME = "2026-11-06 07:07:17.362193413"
BOARD_SIZE = 4940213

EVIDENCE_WHITELIST = ("[官网]", "[实测]", "[媒体]", "[推算]", "[0数据]")
FORBIDDEN_EVIDENCE = ("[官方]",)
FORBIDDEN_PENDING = ("待补", "等原厂", "等供应商确认", "待外部回复", "等确认", "应该没问题")

# ★L4 要求的两个「说法」的锚点 (★两边必须同时出现·不许只留一边★) ★
B33_ANCHOR = "B33_PIN_LAND_1P27"
B33_SIDE = "0.50→1.27mm"
ISS369_SIDE = "不在 ISS-364 的 90 件换 land 名单里"


# ==================================================================================================
# 只读 import 既有闸 (三集合口径零漂移)
# ==================================================================================================
def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def recompute_sets(root):
    """★自己算三个集合 + 两套口径 + 差集 (★不许写死任何数★) ★"""
    cov = _load("iss373_cov_readonly", os.path.join(root, "HW", "check_fp_truth_coverage_gap.py"))
    mech = _load("iss373_mech_readonly",
                 os.path.join(root, "MECH", "check_onepass_s10_fp_swap_impact.py"))
    bom = cov.load_bom(os.path.join(root, "HW", "BOM_v1.csv"))
    c4 = set(cov.netlist_placeholder(os.path.join(root, "HW", "netlist_v1.csv")))
    iss = set(mech.read_iss356_targets(root))
    gap = set(cov.coverage_gap(bom, c4))
    inter = iss & c4
    set90 = set(inter) | gap
    set91 = set(iss) | gap
    return {"c4": c4, "iss": iss, "gap": gap, "inter": inter,
            "set90": set90, "set91": set91,
            "diff": set91 - set90,
            "n_c4": len(c4), "n_iss": len(iss), "n_inter": len(inter), "n_gap": len(gap),
            "n_set90": len(set90), "n_set91": len(set91)}


def md5_of(path):
    return hashlib.md5(open(path, "rb").read()).hexdigest()


# ==================================================================================================
# 上下文
# ==================================================================================================
class Ctx(object):
    """★一次判定的全部输入 (★自测要能逐个替换, 所以拆开★) ★"""

    def __init__(self, root, page_path=None, board_path=None, gate_check_path=None,
                 page_text=None):
        self.root = root
        self.page_path = page_path or os.path.join(root, PAGE_REL)
        self.board_path = board_path or os.path.join(root, BOARD_REL)
        self.gate_check_path = gate_check_path or os.path.join(root, GATE_CHECK_REL)
        self._text = page_text
        self._json = None
        self.sets = None

    @property
    def text(self):
        if self._text is None:
            self._text = open(self.page_path, encoding="utf-8").read()
        return self._text

    def set_text(self, t):
        self._text = t
        self._json = None

    @property
    def page(self):
        if self._json is None:
            t = self.text
            b = t.find(MACH_BEGIN)
            e = t.find(MACH_END)
            if b < 0 or e < 0:
                raise ValueError("★页里缺机器块标记 (BEGIN/END)★")
            m = re.search(r"```json\n(.*?)\n```", t[b:e], re.S)
            if not m:
                raise ValueError("★机器块不是 ```json 围栏★")
            self._json = json.loads(m.group(1))
        return self._json

    def set_page(self, obj):
        """★把机器块整体换掉 (★自测改 JSON 用★) ★"""
        t = self.text
        b = t.find(MACH_BEGIN)
        e = t.find(MACH_END)
        m = re.search(r"```json\n(.*?)\n```", t[b:e], re.S)
        new_blk = "```json\n" + json.dumps(obj, ensure_ascii=False, indent=1) + "\n```"
        # ★★m.start()/m.end() 是相对 t[b:e] 的偏移 ⇒ 必须加回 b 才是绝对位置★★
        #   (v1 的 bug: 忘了加 b ⇒ 正文被错位截断 ⇒ 「复跑命令在正文里」这条判据失效)
        self._text = t[:m.start() + b] + new_blk + t[m.end() + b:]
        self._json = obj

    @property
    def prose(self):
        """★正文 (★去掉机器块★) ⇒ 「复跑命令要在正文里」这条不能拿机器块自己糊弄过去★"""
        t = self.text
        b = t.find(MACH_BEGIN)
        e = t.find(MACH_END)
        if b < 0 or e < 0:
            return t
        return t[:b] + t[e:]

    def compute_sets(self):
        if self.sets is None:
            self.sets = recompute_sets(self.root)
        return self.sets


# ==================================================================================================
# 九条判据
# ==================================================================================================
def _norm(s):
    return re.sub(r"\s+", " ", s or "").strip()


def check_L0(ctx):
    """★集合算法自算: 页里写的数 ≠ 脚本实算 ⇒ 红 ★"""
    errs = []
    s = ctx.compute_sets()
    p = ctx.page
    counts = p.get("counts") or {}
    pairs = [
        ("c4_total", s["n_c4"], "C4 集合件数"),
        ("iss356_main_board_total", s["n_iss"], "ISS-356 靶子(本板)件数"),
        ("inter_total", s["n_inter"], "靶子 ∩ C4 件数"),
        ("gap_total", s["n_gap"], "缺口件数"),
        ("set90_total", s["n_set90"], "90 口径件数"),
        ("set91_total", s["n_set91"], "91 口径件数"),
        ("diff_total", len(s["diff"]), "两套口径差集件数"),
    ]
    for k, v, label in pairs:
        if k not in counts:
            errs.append("L0 页里 counts 缺 %s (%s)" % (k, label))
        elif counts[k] != v:
            errs.append("L0 页里 %s = %s, 脚本实算 = %s ⇒ 不一致 (%s)"
                        % (k, counts[k], v, label))
    # ★页里 sets[] 两条的 total / contains_jdebug 也必须与实算一致 ★
    for entry in p.get("sets") or []:
        sid = entry.get("id")
        if sid == "90":
            if entry.get("total") != s["n_set90"]:
                errs.append("L0 页里 sets[90].total = %s ≠ 实算 %s"
                            % (entry.get("total"), s["n_set90"]))
            jd_in = bool(s["diff"]) and (s["set90"] & s["diff"])
            if bool(entry.get("contains_jdebug")) != bool(jd_in):
                errs.append("L0 页里 sets[90].contains_jdebug = %s ≠ 实算 %s"
                            % (entry.get("contains_jdebug"), bool(jd_in)))
        elif sid == "91":
            if entry.get("total") != s["n_set91"]:
                errs.append("L0 页里 sets[91].total = %s ≠ 实算 %s"
                            % (entry.get("total"), s["n_set91"]))
            jd_in = bool(s["diff"]) and (s["set91"] & s["diff"])
            if bool(entry.get("contains_jdebug")) != bool(jd_in):
                errs.append("L0 页里 sets[91].contains_jdebug = %s ≠ 实算 %s"
                            % (entry.get("contains_jdebug"), bool(jd_in)))
    return errs


def check_L1(ctx):
    """★差集恰为 1 件, 且是脚本自己算出来的那件 (★不许写死名字就算过★) ★"""
    errs = []
    s = ctx.compute_sets()
    d = ctx.page.get("diff") or {}
    real = sorted(s["diff"])
    if len(real) != 1:
        errs.append("L1 脚本实算差集 = %d 件 (%s) ⇒ 不是 1 件 ⇒ 两套口径的差变了 ⇒ 红"
                    % (len(real), real))
    if d.get("count") != len(real):
        errs.append("L1 页里 diff.count = %s ≠ 脚本实算 %d" % (d.get("count"), len(real)))
    page_refs = sorted(d.get("refs") or [])
    if page_refs != real:
        errs.append("L1 页里 diff.refs = %s ≠ 脚本实算差集 %s ⇒ 那 1 件被改了 ⇒ 红"
                    % (page_refs, real))
    if not (d.get("algo") or "").strip():
        errs.append("L1 页里 diff.algo 空")
    return errs


def check_L2(ctx):
    """★页 §0 口径表两行都在, 且都带复跑命令 ★"""
    errs = []
    p = ctx.page
    sets = p.get("sets") or []
    ids = [x.get("id") for x in sets]
    for want in ("90", "91"):
        if want not in ids:
            errs.append("L2 页里 §0 口径表缺「%s」那一行" % want)
    if len(ids) != len(set(ids)):
        errs.append("L2 页里 §0 口径表有重复行: %s" % ids)
    for x in sets:
        for k in ("algo", "total", "contains_jdebug", "repro"):
            if k not in x:
                errs.append("L2 页里 §0 口径表 %s 行缺字段 %s" % (x.get("id"), k))
        repro = (x.get("repro") or "").strip()
        if not repro:
            errs.append("L2 页里 §0 口径表 %s 行的复跑命令为空" % x.get("id"))
        elif repro not in ctx.prose:
            errs.append("L2 页里 §0 口径表 %s 行的复跑命令在正文里找不到: %s"
                        % (x.get("id"), repro))
    return errs


def _live_number(ctx, src, s):
    """★按 live_kind 活体复跑, 返回那个数 (拿不到 ⇒ None) ★"""
    kind = src.get("live_kind")
    if kind == "gate_set90":
        return s["n_set90"]
    if kind == "gate_set91":
        return s["n_set91"]
    if kind == "m1_json":
        cmd = ["python3", os.path.join(ctx.root, "MECH", "check_onepass_s10_fp_swap_impact.py"),
               "--json"]
        p = subprocess.run(cmd, cwd=ctx.root, capture_output=True, text=True)
        if p.returncode != 0:
            return None
        t = p.stdout
        i = t.find("{")
        if i < 0:
            return None
        try:
            d = json.loads(t[i:])
        except Exception:
            return None
        try:
            cur = d
            for k in (src.get("live_key") or "").split("."):
                if not k:
                    continue
                cur = cur[k]
            return cur
        except Exception:
            return None
    if kind == "m4_compute":
        cmd = ["python3", os.path.join(ctx.root, "MECH", "check_onepass_s10_led_spec_sync.py"),
               "--compute"]
        p = subprocess.run(cmd, cwd=ctx.root, capture_output=True, text=True)
        m = re.search(r'"swap_all90_n"\s*:\s*(\d+)', p.stdout)
        return int(m.group(1)) if m else None
    return None


def check_L3(ctx):
    """★四处口径逐条可查 (路径 + 行号 + 那个数 + 定义还是算例) ★"""
    errs = []
    s = ctx.compute_sets()
    p = ctx.page
    srcs = p.get("four_sources") or []
    if len(srcs) != 4:
        errs.append("L3 页里 four_sources = %d 条 ⇒ 必须恰 4 条" % len(srcs))
    for i, src in enumerate(srcs):
        sid = src.get("id") or ("#%d" % (i + 1))
        path = src.get("path") or ""
        ap = os.path.join(ctx.root, path)
        if not path or not os.path.isfile(ap):
            errs.append("L3 %s 的路径不存在: %s" % (sid, path))
            continue
        lines = open(ap, encoding="utf-8").read().splitlines()
        ln = src.get("line")
        if not isinstance(ln, int) or ln < 1 or ln > len(lines):
            errs.append("L3 %s 的行号 %s 越界 (文件 %d 行)" % (sid, ln, len(lines)))
            continue
        line = lines[ln - 1]
        quote = _norm(src.get("quote"))
        if quote:
            # ★quote 可能写成表格行的多段 (用 | 分隔) ⇒ 逐段都要在这一行里出现★
            segs = [_norm(x) for x in src.get("quote").split("|")] if "|" in (src.get("quote") or "") \
                else [quote]
            miss = [x for x in segs if x and x not in _norm(line)]
            if miss:
                errs.append("L3 %s 的第 %d 行不含它自己写的那句原文\n        行: %s\n        缺: %s"
                            % (sid, ln, line.strip()[:120], miss))
        num = src.get("number")
        if not isinstance(num, int):
            errs.append("L3 %s 的那个数不是整数: %s" % (sid, num))
        else:
            in_quote = (str(num) in (src.get("quote") or ""))
            live = _live_number(ctx, src, s)
            if in_quote:
                pass
            elif live is None:
                errs.append("L3 %s 的那个数 %s 既不在原文里, 活体复跑也拿不到" % (sid, num))
            elif live != num:
                errs.append("L3 %s 的那个数 %s ≠ 活体复跑 %s ⇒ 红" % (sid, num, live))
        kind = src.get("kind")
        if kind not in ("集合定义", "敏感度算例"):
            errs.append("L3 %s 的「定义还是算例」取值非法: %s" % (sid, kind))
        elif kind not in ctx.text:
            errs.append("L3 %s 的「定义还是算例」判定 %s 在正文里找不到" % (sid, kind))
        for k in ("path", "line", "number", "kind"):
            if k not in src:
                errs.append("L3 %s 缺字段 %s" % (sid, k))
    return errs


def check_L4(ctx):
    """★J_DEBUG 四条腿齐全 + 与 B33 交叉引到 + 两边说法同时出现 ★"""
    errs = []
    p = ctx.page
    legs = p.get("jdebug_legs") or []
    if len(legs) != 4:
        errs.append("L4 页里 jdebug_legs = %d 条 ⇒ 必须恰 4 条 (四条腿)" % len(legs))
    got = sorted(x.get("leg") for x in legs)
    if got != [1, 2, 3, 4]:
        errs.append("L4 页里四条腿的编号不全: %s" % got)
    for x in legs:
        for k in ("leg", "claim", "how", "evidence"):
            if not (x.get(k) or "").strip() if k != "leg" else x.get(k) is None:
                errs.append("L4 第 %s 腿缺字段 %s" % (x.get("leg"), k))
        ev = (x.get("evidence") or "")
        if not any(e in ev for e in EVIDENCE_WHITELIST):
            errs.append("L4 第 %s 腿的证据等级不在五级白名单: %s" % (x.get("leg"), ev))
    t = ctx.text
    if B33_ANCHOR not in t:
        errs.append("L4 页里没有交叉引到 %s" % B33_ANCHOR)
    if B33_SIDE not in t:
        errs.append("L4 页里没有 B33 那边的说法 (锚点 %s)" % B33_SIDE)
    if ISS369_SIDE not in t:
        errs.append("L4 页里没有 ISS-369 那边的说法 (锚点 %s) ⇒ 只留一边 ⇒ 红" % ISS369_SIDE)
    return errs


def check_L5(ctx):
    """★写库名名单的联动手算式在页里 ★"""
    errs = []
    link = ctx.page.get("libid_linkage") or {}
    if not (link.get("formula") or "").strip():
        errs.append("L5 页里 libid_linkage.formula 空")
    for key, want_w, want_n in (("if_set90", 94, 92), ("if_set91", 95, 91)):
        sub = link.get(key) or {}
        if sub.get("write") != want_w:
            errs.append("L5 页里 %s.write = %s ≠ %s" % (key, sub.get("write"), want_w))
        if sub.get("not_write") != want_n:
            errs.append("L5 页里 %s.not_write = %s ≠ %s" % (key, sub.get("not_write"), want_n))
        if sub.get("table_a") is None or sub.get("table_b") is None:
            errs.append("L5 页里 %s 缺 table_a / table_b" % key)
        elif sub.get("table_a") + sub.get("table_b") != 186:
            errs.append("L5 页里 %s 的表 A + 表 B ≠ 186" % key)
    t = ctx.text
    for n in ("94", "92", "95", "91"):
        if n not in t:
            errs.append("L5 页里找不到写库名联动的那个数 %s" % n)
    if (link.get("formula") or "") and link["formula"] not in t:
        errs.append("L5 页里找不到写库名联动的算式原文")
    return errs


def check_L6(ctx):
    """★板面零写板自证 (md5 / mtime / size 三项) ★"""
    errs = []
    if not os.path.isfile(ctx.board_path):
        return ["L6 板文件不存在: %s" % ctx.board_path]
    got_md5 = md5_of(ctx.board_path)
    st = os.stat(ctx.board_path)
    if got_md5 != BOARD_MD5:
        errs.append("L6 板 md5 = %s ≠ %s ⇒ 板被写过" % (got_md5, BOARD_MD5))
    got_size = st.st_size
    if got_size != BOARD_SIZE:
        errs.append("L6 板 size = %s ≠ %s" % (got_size, BOARD_SIZE))
    # ★mtime 要到纳秒位 (★stat 的 %y 给的是 9 位小数★) ★
    ns = st.st_mtime_ns
    sec, rem = divmod(ns, 1000000000)
    got_mtime = "%s.%09d" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(sec)), rem)
    if got_mtime != BOARD_MTIME:
        errs.append("L6 板 mtime = %s ≠ %s" % (got_mtime, BOARD_MTIME))
    fp = ctx.page.get("board_fingerprint") or {}
    if fp.get("md5") != got_md5:
        errs.append("L6 页里记的板 md5 = %s ≠ 板实际 %s" % (fp.get("md5"), got_md5))
    if fp.get("size") != got_size:
        errs.append("L6 页里记的板 size = %s ≠ 板实际 %s" % (fp.get("size"), got_size))
    return errs


def check_L7(ctx):
    """★证据等级五级白名单 + 零挂起措辞 + 判据句/事实句分开 ★"""
    errs = []
    t = ctx.text
    tags = re.findall(r"\[([^\[\]\s]{1,12})\]", t)
    for tg in set(tags):
        if ("[%s]" % tg) in EVIDENCE_WHITELIST:
            continue
        if ("[%s]" % tg) in FORBIDDEN_EVIDENCE:
            errs.append("L7 页里出现禁用证据等级 [%s] ⇒ 只许五级白名单" % tg)
        elif tg in ("官网", "实测", "媒体", "推算", "0数据", "官方"):
            errs.append("L7 页里出现不在白名单的证据标签 [%s]" % tg)
    for w in FORBIDDEN_PENDING:
        if w in t:
            errs.append("L7 页里出现挂起措辞「%s」" % w)
    paths = ctx.page.get("paths") or []
    if len(paths) < 2:
        errs.append("L5/L7 页里 paths[] 少于 2 条 (两条路都要写判据与事实)")
    for pth in paths:
        if not (pth.get("判据") or "").strip():
            errs.append("L7 页里路 %s 的判据栏空 ⇒ 判据句/事实句没分开" % pth.get("id"))
        if not (pth.get("事实") or "").strip():
            errs.append("L7 页里路 %s 的事实栏空 ⇒ 判据句/事实句没分开" % pth.get("id"))
    return errs


def check_L8(ctx):
    """★零挂链: 本闸不许挂进 state/gate_check.py ⇒ 挂不挂归 main ★"""
    errs = []
    if not os.path.isfile(ctx.gate_check_path):
        return ["L8 找不到 %s" % ctx.gate_check_path]
    txt = open(ctx.gate_check_path, encoding="utf-8").read()
    if "check_onepass_s10_swap_set_truth" in txt:
        n = txt.count("check_onepass_s10_swap_set_truth")
        errs.append("L8 本闸已被挂进 state/gate_check.py (%d 处) ⇒ 零挂链判红 ⇒ 挂不挂归 main"
                    % n)
    return errs


ALL_CHECKS = [("L0", check_L0), ("L1", check_L1), ("L2", check_L2), ("L3", check_L3),
              ("L4", check_L4), ("L5", check_L5), ("L6", check_L6), ("L7", check_L7),
              ("L8", check_L8)]


def run_all(ctx):
    out = {}
    for name, fn in ALL_CHECKS:
        try:
            errs = fn(ctx)
        except Exception as e:
            errs = ["%s 判据执行异常: %s" % (name, e)]
        out[name] = {"ok": not errs, "errs": errs}
    return out


# ==================================================================================================
# 自测 (反向用例: 每条自证「红的是目标那一条, 其余仍绿」)
# ==================================================================================================
def _clone_ctx(base, tmpdir):
    """★复制一份上下文: 页 / 板 / gate_check 全部指到临时目录 (★真板零改动★) ★"""
    # ★每个用例一份独立子目录 ⇒ 互不污染 (★否则 L8 那一例会把闸名写进共享的 gate_check 副本★) ★
    os.makedirs(tmpdir, exist_ok=True)
    page_dst = os.path.join(tmpdir, "page.md")
    with open(base.page_path, encoding="utf-8") as fh:
        text = fh.read()
    with open(page_dst, "w", encoding="utf-8") as fh:
        fh.write(text)
    board_dst = os.path.join(tmpdir, "board.kicad_pcb")
    with open(base.board_path, "rb") as fh:
        data = fh.read()
    with open(board_dst, "wb") as fh:
        fh.write(data)
    # ★copyfile 不保留 mtime ⇒ 手动按【纳秒位】回填真板的 mtime (★L6 校验到纳秒★) ★
    st = os.stat(base.board_path)
    os.utime(board_dst, ns=(st.st_atime_ns, st.st_mtime_ns))
    gc_dst = os.path.join(tmpdir, "gate_check.py")
    # ★★写临时副本, 不是写真文件★★ (★v1 的 bug: 这里写成 base.gate_check_path ⇒ 把真
    #   state/gate_check.py 覆写成了一行注释 ⇒ 2026-11-23 当场发现并从
    #   tmp/iss372_sbx/tree/state/gate_check.py 逐字节还原, md5 回到 5f370bb8…★)
    with open(gc_dst, "w", encoding="utf-8") as fh:
        fh.write("# 临时副本 (自测用) · 真 state/gate_check.py 零改动\n")
    return Ctx(base.root, page_path=page_dst, board_path=board_dst,
               gate_check_path=gc_dst, page_text=text)


def _mutate_json(ctx, fn):
    p = json.loads(json.dumps(ctx.page, ensure_ascii=False))
    fn(p)
    ctx.set_page(p)


def do_selftest(root):
    import shutil
    import tempfile
    base = Ctx(root)
    results = []
    tmpdir = tempfile.mkdtemp(prefix="iss373_selftest_")
    try:
        cases = []
        _ci = [0]

        def _newctx():
            _ci[0] += 1
            return _clone_ctx(base, os.path.join(tmpdir, "case_%02d" % _ci[0]))

        # ---------- 正向: 全绿 ----------
        ctx = _newctx()
        r = run_all(ctx)
        bad = [k for k, v in r.items() if not v["ok"]]
        results.append(("正向基线 (应当全绿)", "全绿" if not bad else "红: %s" % bad,
                        None, bad))

        # 1. L0 红: 把页里的 90 改成 89
        ctx = _newctx()
        _mutate_json(ctx, lambda p: p["counts"].__setitem__("set90_total", 89))
        cases.append(("L0 改页里的 90 件数 (90→89)", "L0", ctx))

        # 2. L0 红: 把页里的 91 改成 90
        ctx = _newctx()
        _mutate_json(ctx, lambda p: p["counts"].__setitem__("set91_total", 90))
        cases.append(("L0 改页里的 91 件数 (91→90)", "L0", ctx))

        # 3. L0 红: 改 inter 件数
        ctx = _newctx()
        _mutate_json(ctx, lambda p: p["counts"].__setitem__("inter_total", 76))
        cases.append(("L0 改页里的 inter 件数 (77→76)", "L0", ctx))

        # 4. L1 红: 差集件数改成 2
        ctx = _newctx()

        def _d2(p):
            p["diff"]["count"] = 2
            p["diff"]["refs"] = ["J_DEBUG", "J_UART"]
        _mutate_json(ctx, _d2)
        cases.append(("L1 差集件数改成 2 (⇒ 差集变了)", "L1", ctx))

        # 5. L1 红: 差集那件换成别的名字 (件数仍是 1)
        ctx = _newctx()

        def _d3(p):
            p["diff"]["refs"] = ["J_UART"]
        _mutate_json(ctx, _d3)
        cases.append(("L1 差集那件换成别的名字 (件数仍 1)", "L1", ctx))

        # 6. L2 红: 删掉 §0 口径表里的一行
        ctx = _newctx()

        def _s2(p):
            p["sets"] = [x for x in p["sets"] if x.get("id") != "91"]
        _mutate_json(ctx, _s2)
        cases.append(("L2 删掉 §0 口径表的 91 那一行", "L2", ctx))

        # 7. L2 红: 复跑命令改成页里没有的
        ctx = _newctx()

        def _s2b(p):
            p["sets"][0]["repro"] = "python3 不存在的脚本.py"
        _mutate_json(ctx, _s2b)
        cases.append(("L2 §0 口径表的复跑命令指向不存在的命令", "L2", ctx))

        # 8. L3 红: 改一处口径的行号
        ctx = _newctx()

        def _s3(p):
            p["four_sources"][0]["line"] = 451
        _mutate_json(ctx, _s3)
        cases.append(("L3 把 ① 的行号挪一行 (⇒ 该行不含它写的那句)", "L3", ctx))

        # 9. L3 红: 把 ③ 的那个数改成 90 (原文与活体都对不上)
        ctx = _newctx()

        def _s3b(p):
            p["four_sources"][2]["number"] = 90
        _mutate_json(ctx, _s3b)
        cases.append(("L3 把 ③ 的那个数 91 改成 90", "L3", ctx))

        # 10. L3 红: 删掉一条口径
        ctx = _newctx()

        def _s3c(p):
            p["four_sources"] = p["four_sources"][:3]
        _mutate_json(ctx, _s3c)
        cases.append(("L3 删掉一处口径 (四条变三条)", "L3", ctx))

        # 11. L4 红: 删掉一条腿
        ctx = _newctx()

        def _l4(p):
            p["jdebug_legs"] = [x for x in p["jdebug_legs"] if x.get("leg") != 3]
        _mutate_json(ctx, _l4)
        cases.append(("L4 删掉 J_DEBUG 第 ③ 腿 (B33 那条)", "L4", ctx))

        # 12. L4 红: 正文里删掉 ISS-369 那边的说法 (只留 B33 一边)
        ctx = _newctx()
        ctx.set_text(ctx.text.replace(ISS369_SIDE, "★那一句被删掉了★"))
        cases.append(("L4 正文删掉 ISS-369 那边的说法 (只留一边)", "L4", ctx))

        # 13. L4 红: 正文里删掉 B33 的交叉引用
        ctx = _newctx()
        ctx.set_text(ctx.text.replace(B33_ANCHOR, "★那一句被删掉了★"))
        cases.append(("L4 正文删掉 B33 的交叉引用", "L4", ctx))

        # 14. L5 红: 把 91 件口径的写库名件数改成 94
        ctx = _newctx()

        def _l5(p):
            p["libid_linkage"]["if_set91"]["write"] = 94
        _mutate_json(ctx, _l5)
        cases.append(("L5 把 91 件口径的写库名件数 95 改成 94", "L5", ctx))

        # 15. L5 红: 把 90 件口径的不写件数改成 91
        ctx = _newctx()

        def _l5b(p):
            p["libid_linkage"]["if_set90"]["not_write"] = 91
        _mutate_json(ctx, _l5b)
        cases.append(("L5 把 90 件口径的不写库名件数 92 改成 91", "L5", ctx))

        # 16. L6 红: 板被写了一个字节
        ctx = _newctx()
        with open(ctx.board_path, "ab") as fh:
            fh.write(b"\n")
        cases.append(("L6 板副本被写了一个字节 (⇒ 指纹三项全变)", "L6", ctx))

        # 17. L7 红: 塞一个禁用证据等级
        ctx = _newctx()
        ctx.set_text(ctx.text + "\n\n★补一句 [官方] 这是官方说法★\n")
        cases.append(("L7 页里塞一个 [官方] 标签", "L7", ctx))

        # 18. L7 红: 塞一句挂起措辞
        ctx = _newctx()
        ctx.set_text(ctx.text + "\n\n★这块等原厂回信再说★\n")
        cases.append(("L7 页里塞一句挂起措辞", "L7", ctx))

        # 19. L7 红: 把判据栏清空
        ctx = _newctx()

        def _l7(p):
            p["paths"][0]["判据"] = ""
        _mutate_json(ctx, _l7)
        cases.append(("L7 把路的判据栏清空 (判据句/事实句没分开)", "L7", ctx))

        # 20. L8 红: 把本闸挂进 gate_check.py
        ctx = _newctx()
        with open(ctx.gate_check_path, "a", encoding="utf-8") as fh:
            fh.write('EXTRA_GATES.append(("S10 换件集合真源闸 (ISS-373)",\n'
                     '               ("HW/check_onepass_s10_swap_set_truth.py",)))\n')
        cases.append(("L8 把本闸挂进 gate_check.py", "L8", ctx))

        # ---- 逐条跑反向用例 ----
        all_ok = True
        for label, target, c in cases:
            r = run_all(c)
            red = [k for k, v in r.items() if not v["ok"]]
            if target not in red:
                all_ok = False
                print("❌ 自测失败: %s ⇒ 目标 %s 没红 (红了的是 %s)"
                      % (label, target, red))
                continue
            others = [k for k in red if k != target]
            if others:
                all_ok = False
                print("❌ 自测失败: %s ⇒ 除 %s 外还有别的红了: %s"
                      % (label, target, others))
                continue
            print("✅ %-52s ⇒ 只有 %s 红, 其余八条仍绿" % (label, target))
            results.append((label, "只 %s 红" % target, target, [target]))
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

    if not all_ok:
        print("❌ 自测失败: 至少一条反向用例没有做到「只红目标那一条」")
        return 1
    print("-" * 72)
    print("✅ 自测通过 —— %d 条反向用例全部做到「红的是目标那一条, 其余仍绿」" % len(cases))
    print("ALL TESTS PASS")
    return 0


# ==================================================================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return do_selftest(PROJ)

    ctx = Ctx(PROJ)
    res = run_all(ctx)
    out = {"page": PAGE_REL, "results": {k: {"ok": v["ok"], "errs": v["errs"]}
                                         for k, v in res.items()}}
    s = ctx.compute_sets()
    out["facts"] = {"n_c4": s["n_c4"], "n_iss": s["n_iss"], "n_inter": s["n_inter"],
                    "n_gap": s["n_gap"], "n_set90": s["n_set90"], "n_set91": s["n_set91"],
                    "diff": sorted(s["diff"])}
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=1))
        return 0 if all(v["ok"] for v in res.values()) else 1

    print("=" * 72)
    print("  ISS-373 · 「板那一趟」S10 换件集合唯一真源 · 机器闸")
    print("=" * 72)
    print("  集合自算: C4=%d / 靶子=%d / 靶子∩C4=%d / 缺口=%d ⇒ %d 件口径 %d 件 / %d 件口径 %d 件"
          % (s["n_c4"], s["n_iss"], s["n_inter"], s["n_gap"],
             90, s["n_set90"], 91, s["n_set91"]))
    print("  差集 (脚本自己算): %s" % sorted(s["diff"]))
    for name, _fn in ALL_CHECKS:
        v = res[name]
        print("  %s %s" % ("✅" if v["ok"] else "❌", name))
        for e in v["errs"]:
            print("      · %s" % e)
    print("-" * 72)
    if all(v["ok"] for v in res.values()):
        print("✅ 全绿 —— 「那一趟换几件」的两套口径与差集, 页里写的数与脚本实算逐项相等")
        return 0
    print("❌ 不通过 —— 页里的数 / 口径 / 判据与机器实算对不上")
    return 1


if __name__ == "__main__":
    sys.exit(main())
