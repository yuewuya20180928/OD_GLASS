#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SW/tools/check_sw_fp_truth_impact.py — ISS-362 「板那一趟」S10 换封装真值 ⇒ SW 侧影响面闸
======================================================================================
目的: 让「板只改一次」那一趟 (S1~S13) 里【S10 换封装真值落表】这一跳, 当天 SW 侧
      【红的每一条都能被解释】—— 而不是现场抓瞎。

★**本闸是只读闸 + 沙盒预演闸**: 真件 (板 / 网表 / 脚表 / BOM / 落表台账 / 既有闸脚本 /
  既有页面) 一个字节都不许动 ⇒ 所有写操作只发生在项目内 `tmp/iss362_gate_sbx/` ★

★**判据七条 (H0~H7)** ★:
  H0 基线闸全绿 (10 道 SW 闸逐道跑 · fail-closed: 脚本不存在 / 跑不起来 / 超时 ⇒ 一律算红)
  H1 「SW 侧读封装栏 (fp 栏)」这件事被登记了 (★今天实测 0 处 ⇒ 这是【盲区】⇒ 登记即绿★)
  H2 台账链头 == 盘上现值 (三件全查 · ★用 sw_ledger_state() 自己算·不许自己另写一套★)
  H3 SW 侧待办 need 里引着的过期 md5 逐条给了清理口径 (★今天实测 27 条陈旧·登记即绿★)
  H4 8 条板侧输入清单里没有「S10 换封装真值」这一条 (★今天实测 0 条覆盖·登记即绿★)
  H5 SOP 三件套齐全 (§1 逐闸影响表 / §2 need 清理口径 / §3 当天 SOP)
  H6 禁语检查 (老板 2026-11-12 02:02 政策)
  H7 证据等级五级白名单 (`[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` · 写 `[官方]` = 红)

★★**设计纪律 (★照抄 ISS-335 准出汇总闸 + ISS-309 铁律★)** ★:
  · H1 / H3 / H4 三条【今天必然红】⇒ 它们【不是坏消息】⇒ 它们是【本单登记下来的缺口清单】
  · ⇒ 交卷时它们变绿的方式 = 【页里把缺口登记清楚了】· 不是【把缺口删掉】
  · ⇒ ★绝对不许把 H1/H3/H4 改成「扫到 0 处就当没问题」那种同义改写★

★**H1/H3/H4 的「登记式绿」怎么被机器证明 (★不是靠人眼★)** ★:
  · H1: 页里必须同时登记【实测读数 H1-READERS=N】+【盲区】+【影响】+【对策】;
         且 §1 逐闸表里 G01~G10 每一行的「现状 rc」必须 == H0 实测 rc (★篡改任一闸读数 ⇒ H1 红★)
  · H3: 页里必须逐条登记【need key + 那条 md5 + 处置词】+ 处置词必须符合机器判据
         (该值在落表链上 ⇒ 必须写「退休」· 不在链上 ⇒ 必须写「改写」)
  · H4: 页里必须登记【清单条目数 8】+【覆盖条数 0】+【泛封装提及条数 3】+【影响】+【对策】

用法:
    python3 SW/tools/check_sw_fp_truth_impact.py                # 核对 (rc=0 = 八条全过)
    python3 SW/tools/check_sw_fp_truth_impact.py --selftest      # 反向用例 (≥6 条 · 必须全 PASS)
    python3 SW/tools/check_sw_fp_truth_impact.py --json          # 机读输出
    python3 SW/tools/check_sw_fp_truth_impact.py --page <路径>   # 指定被检页 (★沙盒用★)

★边界 (★本闸只读真件★): 不写板 / 不落表 / 不改既有闸 / 不改既有页面 / 不改 STATE.yaml /
  不改任何人的分片 ⇒ 沙盒只落项目内 `tmp/iss362_gate_sbx/` · ★禁止 os.symlink() (ISS-327 cont1 根因)★
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

import check_demo_panel_spec as dps            # noqa: E402  ★只读 import · 不改它★

PAGE_REL = os.path.join("SW", "BOARD_ONEPASS_FP_TRUTH_IMPACT.md")
SYNC_REL = os.path.join("SW", "BOARD_ONEPASS_SW_SYNC.md")

MANAGED = ("HW/netlist_v1.csv", "HW/netlist_v1_pins.csv", "HW/BOM_v1.csv")
PROTECTED = ("HW/PCB/demo_mainboard.kicad_pcb", "HW/PCB/demo_mainboard.kicad_pro")

SBX_REL = os.path.join("tmp", "iss362_gate_sbx")
TMPDIR_REL = os.path.join("tmp", "iss362_tmp")
GATE_TMP_REL = os.path.join("tmp", "iss362_gate_sbx", "gates")

GATE_TIMEOUT = 300          # ★与 state/gate_check.py 的 run_external_gate 同口径★

# ★★10 道 SW 闸清单 (★逐字照抄 SW/tools/check_onepass_sw_release.py 的 GATES · 一条不许少★) ★
BASELINE_GATES = (
    ("SW/tools/check_onepass_sw_sync.py",
     "SW 侧板侧输入 / 合法改板闸 (ISS-279/298/321)", ()),
    ("SW/tools/check_sw_ref_reachability.py",
     "SW 侧位号引用可达性闸 v1 (ISS-318)", ()),
    ("SW/tools/check_landing_trace_obligation.py",
     "SW 侧落表留痕义务闸 (ISS-315)", ()),
    ("SW/tools/check_demo_panel_spec.py",
     "SW 侧面板规格 / 三方对账闸 (ISS-275/315) ★链外★", ()),
    ("SW/tools/check_demo_panel_spec_r6_selftest.py",
     "SW 侧 R6 判决源反向用例 (ISS-309) ★裸跑★", ("--tmpdir", "@GATE_TMP@")),
    ("SW/tools/check_demo_panel_spec_r6_chainjudge_selftest.py",
     "SW 侧 R6 链头落表单号交叉核对反向用例 (ISS-312) ★裸跑★", ("--tmpdir", "@GATE_TMP@")),
    ("SW/tools/check_demo_panel_spec_r6_hardprot_iss315_selftest.py",
     "SW 侧 R6 硬保护路径反向用例 (ISS-315) ★裸跑★", ("--tmpdir", "@GATE_TMP@")),
    ("SW/tools/check_shutdown_semantics.py",
     "SW 侧关机语义闸 (SW/SHUTDOWN_SEMANTICS_SPEC.md) ★链外★", ()),
    ("SW/tools/check_timing_review_adc_sync.py",
     "SW 侧时序评审 ADC 同步闸 (SW/SW_TIMING_REVIEW.md) ★链外★", ()),
    ("SW/tools/timing_check.py",
     "SW 侧上电 / 复位时序预算闸 (网表 → 时序) ★链外★", ()),
)

# ★★禁语 (★老板 2026-11-12 02:02 政策 ★) ★
FORBIDDEN_PHRASES = ("等原厂回信", "等供应商确认", "待外部回复", "等确认")
NEGATION_MARKERS = ("禁", "不许", "不得", "禁止", "零外发", "避免", "排除", "不看", "拒", "黑名单")

# ★★证据等级五级白名单 ★
EV_WHITELIST = ("[官网]", "[实测]", "[媒体]", "[推算]", "[0数据]")
EV_KEYWORDS = ("实测", "官方", "官网", "媒体", "推算", "数据", "来源", "内部", "待补", "未知", "一手", "二手")

# ★★H1 主题: 「fp 栏 / 封装真值 / 库封装名 / 封装栏」= S10 这一跳专有的说法 ★
# ★★【自匹配陷阱 · 已堵】★★: 本闸要扫【SW 侧有没有闸读 fp 栏】⇒ 若本闸源码里写了那个
#   字面量, 本闸会把自己算成「读者」⇒ 自证失真 ⇒ 所以:
#     ① 字面量用拼接造 (FP_TOKEN) ⇒ 本闸源码里【没有】那个连续字面量
#     ② 扫描时本闸自身也【不计入】读者 (它只做字符串扫描·不读那一栏)
#   ★★ISS-293 cont2b 同款教训: 「自检命令里不许出现被检形态的字面量 ⇒ 一律用拼接/字节转义」★★
FP_TOKEN = "foot" + "print"
FP_TOPIC_RE = re.compile(re.escape(FP_TOKEN) + "|封装真值|库封装名|封装栏", re.I)
FP_GENERIC_RE = re.compile(re.escape(FP_TOKEN) + "|封装", re.I)
SELF_NAME = os.path.basename(__file__)

# ★★H1 措辞红线: 把盲区写成「无问题 / 不影响 / 忽略」⇒ 红 ★
H1_BAD_WORDS = ("无问题", "不影响", "忽略", "无所谓", "不用管", "可以不管")

HEX32_RE = re.compile(r"\b[0-9a-f]{32}\b")
HEX8_RE = re.compile(r"(?<![0-9a-f])([0-9a-f]{8})(?![0-9a-f])")


# ==================================================================================================
# 基础工具
# ==================================================================================================
def read_text(path: str) -> str:
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def md5_of(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def block(text: str, name: str) -> str:
    """取 `<!-- NAME:BEGIN -->` … `<!-- NAME:END -->` 之间的正文 (★取不到 ⇒ 空串★)。"""
    m = re.search(r"<!--\s*%s:BEGIN\s*-->(.*?)<!--\s*%s:END\s*-->" % (re.escape(name), re.escape(name)),
                  text, re.S)
    return m.group(1) if m else ""


def kv(body: str, key: str) -> str:
    """取块里 `- KEY: value` 形式的 value (★取不到 ⇒ 空串★)。"""
    m = re.search(r"^-\s*%s\s*[:：]\s*(.*)$" % re.escape(key), body, re.M)
    return m.group(1).strip() if m else ""


def negated(hits: list, text: str) -> list:
    """否定语境过滤 (★照抄项目口径: 描述禁语规则本身的句子不算违规★)。"""
    out = []
    for phrase, start in hits:
        ctx = text[max(0, start - 45):start]
        if any(mk in ctx for mk in NEGATION_MARKERS):
            continue
        out.append((phrase, start))
    return out


def find_forbidden(text: str) -> list:
    hits = []
    for p in FORBIDDEN_PHRASES:
        for m in re.finditer(re.escape(p), text):
            hits.append((p, m.start()))
    return negated(hits, text)


def child_env(root: str) -> dict:
    """子进程环境: TMPDIR / TMP / TEMP 一律指项目内 (★本机系统临时目录配额已到顶 ⇒ 不指会 EDQUOT 假红★)。"""
    env = dict(os.environ)
    tmp = os.path.join(root, TMPDIR_REL)
    os.makedirs(tmp, exist_ok=True)
    env["TMPDIR"] = tmp
    env["TMP"] = tmp
    env["TEMP"] = tmp
    return env


def run_gate(root: str, rel: str, args: tuple) -> dict:
    """fail-closed 单闸执行 (★照 state/gate_check.py 的 run_external_gate 语义·不自创★)。"""
    path = os.path.join(root, rel)
    if not os.path.isfile(path):
        return {"ok": False, "rc": None, "detail": "脚本不存在 ⇒ 算闸红 (fail-closed)"}
    real_args = [os.path.join(root, GATE_TMP_REL) if a == "@GATE_TMP@" else a for a in args]
    try:
        p = subprocess.run([sys.executable, path] + list(real_args), cwd=root,
                           env=child_env(root), capture_output=True, text=True,
                           timeout=GATE_TIMEOUT)
    except subprocess.TimeoutExpired:
        return {"ok": False, "rc": None, "detail": "超时 %ds ⇒ 算闸红 (fail-closed)" % GATE_TIMEOUT}
    except Exception as exc:                                     # noqa: BLE001
        return {"ok": False, "rc": None, "detail": "跑不起来 (%s) ⇒ 算闸红 (fail-closed)" % exc}
    out = (p.stdout or "") + (p.stderr or "")
    tail = "\n".join([ln for ln in out.splitlines() if ln.strip()][-4:])
    return {"ok": (p.returncode == 0), "rc": p.returncode, "detail": tail}


# ==================================================================================================
# 事实采集 (★全部自己算·不抄任何 agent 报告★)
# ==================================================================================================
def collect_facts(root: str) -> dict:
    f = {}
    # ---- 盘上现值 (受保护 5 件) ----
    f["on_disk"] = {}
    for rel in list(MANAGED) + list(PROTECTED):
        p = os.path.join(root, rel)
        if os.path.isfile(p):
            f["on_disk"][rel] = md5_of(p)
    # ---- 台账链头 (★用 sw_ledger_state 自己算·不许自己另写一套★) ----
    led_text = read_text(os.path.join(root, dps.LEDGER_CANON))
    f["ledger"] = {}
    for rel in MANAGED:
        st = dps.sw_ledger_state(rel, led_text)
        f["ledger"][rel] = st
    # ---- 允许集 (H3 判据用) ----
    allowed = set(f["on_disk"].values())
    for rel in MANAGED:
        h = f["ledger"][rel].get("head")
        if h:
            allowed.add(h)
    f["allowed_md5"] = allowed
    allowed_pref = {v[:12] for v in f["on_disk"].values()}
    for rel in MANAGED:
        h = f["ledger"][rel].get("head")
        if h:
            allowed_pref.add(h[:12])
    f["allowed_pref12"] = allowed_pref
    # ---- 链成员 (含 12 位) ----
    f["chain12"] = {}
    for rel in MANAGED:
        f["chain12"][rel] = list(f["ledger"][rel].get("chain") or [])
    # ---- fp 栏读者 (H1) ★本闸自身不计入 (★它只做字符串扫描·不读那一栏★) ★
    readers = []
    self_mentions = 0
    n_py = 0
    tools_dir = os.path.join(root, "SW", "tools")
    if os.path.isdir(tools_dir):
        for fn in sorted(os.listdir(tools_dir)):
            if not fn.endswith(".py"):
                continue
            n_py += 1
            txt = read_text(os.path.join(tools_dir, fn))
            if fn == SELF_NAME:
                self_mentions = txt.count(FP_TOKEN)
                continue
            if FP_TOKEN in txt:
                readers.append("SW/tools/" + fn)
    f["fp_readers"] = readers
    f["fp_self_mentions"] = self_mentions
    f["fp_n_py"] = n_py
    # ---- 文档侧提及 (fp 栏) · 供人工核对 (★不是读者★) ----
    md_files = []
    sw_dir = os.path.join(root, "SW")
    if os.path.isdir(sw_dir):
        for fn in sorted(os.listdir(sw_dir)):
            if fn.endswith(".md"):
                n = read_text(os.path.join(sw_dir, fn)).count(FP_TOKEN)
                if n:
                    md_files.append(("SW/" + fn, n))
    f["fp_md_mentions"] = md_files
    # ---- 8 条板侧输入清单 (H4) ----
    sync_text = read_text(os.path.join(root, SYNC_REL))
    items = []
    m = re.search(r"```json\s*(\{.*?\})\s*```", sync_text, re.S)
    if m:
        try:
            items = json.loads(m.group(1)).get("items", [])
        except Exception:                                          # noqa: BLE001
            items = []
    f["sync_items"] = items
    f["sync_cover_topic"] = [it.get("id") for it in items
                             if FP_TOPIC_RE.search(" ".join(str(it.get(k, "")) for k in ("current_state", "action")))]
    f["sync_cover_generic"] = [it.get("id") for it in items
                               if FP_GENERIC_RE.search(" ".join(str(it.get(k, "")) for k in ("current_state", "action")))]
    # ---- SW 侧待办 need 里的 md5 (H3) ----
    st = _load_state(root)
    sw = [n for n in (st.get("needs_matrix", {}).get("pending") or []) if n.get("to") == "sw-lead"]
    f["sw_needs"] = sw
    # ---- sw-lead 自己登记的 answer (★合并后的视图·domains.sw-lead.answers★) ★
    dom = ((st.get("domains") or {}).get("sw-lead") or {})
    f["sw_answers"] = list(dom.get("answers") or [])
    f["sw_pending_total"] = len(st.get("needs_matrix", {}).get("pending") or [])
    return f


def _load_state(root: str) -> dict:
    import yaml
    return yaml.safe_load(read_text(os.path.join(root, "STATE.yaml"))) or {}


def need_md5_rows(facts: dict) -> list:
    """把 sw-lead 待办 need 里引的 md5 逐条判定 ⇒ [{key, md5, stale, on_chain, producer, disposition}]."""
    rows = []
    allowed = facts["allowed_md5"]
    for n in facts["sw_needs"]:
        item = n.get("item", "") or ""
        for m32 in sorted(set(HEX32_RE.findall(item))):
            stale = m32 not in allowed
            on_chain = None
            producer = None
            for rel, chain in facts["chain12"].items():
                for c in chain:
                    if c.startswith(m32[:12]):
                        on_chain = rel
                        for r in facts["ledger"][rel].get("records") or []:
                            if r["new"] == c:
                                producer = r.get("iss")
                        break
                if on_chain:
                    break
            disp = ""
            if stale:
                disp = "退休" if on_chain else "改写"
            rows.append({"key": n.get("key"), "md5": m32, "stale": stale, "on_chain": on_chain,
                         "producer": producer, "disposition": disp, "since": n.get("since")})
    return _dedup(rows)


def _dedup(rows: list) -> list:
    seen, out = set(), []
    for r in rows:
        k = (r["key"], r["md5"])
        if k in seen:
            continue
        seen.add(k)
        out.append(r)
    return out


def machine_disposition(facts: dict, md5: str) -> str:
    """处置词的机器判据 (★与页 §2 的口径一字对应★):
         落在落表链上 ⇒ 退休 (已被链头取代的历史值)
         不在链上     ⇒ 改写 (排练值 / 预估值 · 从来没落到过盘上)
         是允许集里的值 ⇒ 保持 (板 / .kicad_pro 的盘上现值)
    """
    m = (md5 or "").strip().lower()
    if not m:
        return ""
    if m in facts["allowed_md5"]:
        return "保持"
    if any(v.startswith(m) for v in facts["allowed_pref12"]):
        return "保持"
    for chain in facts["chain12"].values():
        for c in chain:
            if c.startswith(m[:12]):
                return "退休"
    return "改写"


def need_prefix_rows(facts: dict) -> list:
    """8 位短写 md5 (★iss239 / iss283 / iss232 三条用的是 8 位短写★) ⇒ 同口径判定。"""
    rows = []
    allowed12 = facts["allowed_pref12"]
    for n in facts["sw_needs"]:
        item = n.get("item", "") or ""
        m32 = set(HEX32_RE.findall(item))
        for m in HEX8_RE.finditer(item):
            p = m.group(1)
            if any(x.startswith(p) for x in m32):
                continue
            if any(v.startswith(p) for v in allowed12):
                continue
            on_chain = None
            producer = None
            for rel, chain in facts["chain12"].items():
                for c in chain:
                    if c.startswith(p):
                        on_chain = rel
                        for r in facts["ledger"][rel].get("records") or []:
                            if r["new"] == c:
                                producer = r.get("iss")
                        break
                if on_chain:
                    break
            rows.append({"key": n.get("key"), "md5": p, "stale": True, "on_chain": on_chain,
                         "producer": producer, "disposition": ("退休" if on_chain else "改写"),
                         "since": n.get("since")})
    return _dedup(rows)


# ==================================================================================================
# 七条判据
# ==================================================================================================
def h0_baseline(root: str) -> dict:
    res = []
    ok = True
    for rel, name, args in BASELINE_GATES:
        r = run_gate(root, rel, args)
        res.append({"gate": rel, "name": name, "rc": r["rc"], "ok": r["ok"], "detail": r["detail"]})
        if not r["ok"]:
            ok = False
    return {"ok": ok, "id": "H0", "title": "基线闸全绿 (10 道 SW 闸逐道跑)",
            "rows": res, "detail": "绿 %d / 红 %d" % (sum(1 for r in res if r["ok"]), sum(1 for r in res if not r["ok"]))}


def h1_fp_registered(root: str, page: str, facts: dict, h0: dict) -> dict:
    errs = []
    reg = block(page, "H1-REG")
    s1 = block(page, "S1-TABLE")
    if not reg.strip():
        errs.append("页里没有 H1-REG 登记块 ⇒ 「SW 侧读封装栏 (fp 栏)」这件事没被登记")
    if not s1.strip():
        errs.append("页里没有 S1-TABLE 逐闸影响表块")
    measured = len(facts["fp_readers"])
    # ① 登记块读数必须 == 实测
    rv = kv(reg, "H1-READERS")
    if rv != str(measured):
        errs.append("H1-REG 的 H1-READERS=%r ≠ 实测 %d (★页里的读数被改过或没写★)" % (rv, measured))
    # ② §1 表里也必须写同一读数 (两处互相锁)
    m = re.search(r"H1-READERS\s*=\s*(\d+)", s1)
    if not m:
        errs.append("§1 逐闸表里没有 H1-READERS=<n> 这一行读数")
    elif int(m.group(1)) != measured:
        errs.append("§1 逐闸表的 H1-READERS=%s ≠ 实测 %d" % (m.group(1), measured))
    # ③ 盲区 / 影响 / 对策 三件套
    for k, label in (("H1-BLINDSPOT", "盲区"), ("H1-IMPACT", "影响"), ("H1-COUNTERMEASURE", "对策")):
        if not kv(reg, k).strip():
            errs.append("H1-REG 缺 %s (%s)" % (k, label))
    if "盲区" not in reg:
        errs.append("H1-REG 里没写「盲区」⇒ 不许把「0 处读者」当成没问题")
    for bad in H1_BAD_WORDS:
        if bad in reg:
            errs.append("H1-REG 里出现禁止措辞「%s」⇒ 盲区不许被写成「没事」" % bad)
    # ④ §1 逐闸表的 10 行「现状 rc」必须 == H0 实测 rc (★篡改任一闸读数 ⇒ 红★)
    for i, (rel, _n, _a) in enumerate(BASELINE_GATES, start=1):
        tag = "<!-- G%02d -->" % i
        if tag not in s1:
            errs.append("§1 逐闸表缺 %s 这一行 (%s)" % (tag, rel))
            continue
        row = s1[s1.index(tag):]
        row = row[:row.find("\n") if "\n" in row else len(row)]
        mm = re.search(r"现状\s*rc\s*=\s*(\d+)", row)
        want = None
        for r in h0["rows"]:
            if r["gate"] == rel:
                want = r["rc"]
        if mm is None:
            errs.append("%s 这一行没写「现状 rc=」" % tag)
        elif want is not None and mm.group(1).strip() != str(want):
            errs.append("%s 的「现状 rc=%s」≠ H0 实测 rc=%s (★§1 闸读数被篡改★)" % (tag, mm.group(1), want))
    return {"ok": not errs, "id": "H1", "title": "「SW 侧读封装栏 (fp 栏)」这件事被登记了",
            "detail": "实测读者文件数 = %d (扫 SW/tools/*.py 共 %d 份; 本闸自身不计入·源码里该字面量出现 %d 次; 读者 = %s) · 文档侧提及 %d 份"
                      % (measured, facts.get("fp_n_py", 0), facts.get("fp_self_mentions", 0),
                         ", ".join(facts["fp_readers"]) or "无", len(facts.get("fp_md_mentions", []))),
            "errors": errs}


def h2_chain_head(root: str, facts: dict) -> dict:
    errs = []
    rows = []
    for rel in MANAGED:
        got = facts["on_disk"].get(rel, "")
        st = facts["ledger"][rel]
        head = st.get("head")
        rows.append({"file": rel, "disk": got, "head": head, "iss": st.get("head_iss"),
                     "why": st.get("why"), "chain_len": len(st.get("chain") or [])})
        if not head:
            errs.append("%s 台账链头取不准 (%s) ⇒ 判红" % (rel, st.get("why")))
        elif got[:12] != head:
            errs.append("%s 盘上 md5=%s ≠ 台账链头=%s ⇒ 判红" % (rel, got[:12], head))
    return {"ok": not errs, "id": "H2", "title": "台账链头 == 盘上现值 (三件全查)",
            "rows": rows, "detail": "; ".join("%s 盘上=%s 链头=%s" % (r["file"].split("/")[-1], r["disk"][:12], (r["head"] or "None")) for r in rows),
            "errors": errs}


def h3_need_cleanup(root: str, page: str, facts: dict) -> dict:
    errs = []
    reg = block(page, "H3-REG")
    if not reg.strip():
        errs.append("页里没有 H3-REG 登记块 ⇒ 那批引着过期 md5 的待办 need 没有清理口径")
    md5_rows = need_md5_rows(facts)
    pref_rows = need_prefix_rows(facts)
    stale = [r for r in md5_rows if r["stale"]] + pref_rows
    # 页里登记的行
    reg_lines = {}
    for ln in reg.splitlines():
        m = re.search(r"NEED-KEY\s*[:：]\s*(\S+).*?NEED-MD5\s*[:：]\s*([0-9a-f]{8,32}).*?"
                      r"DISPOSITION\s*[:：]\s*(退休|改写|保持)", ln)
        if m:
            reg_lines[(m.group(1), m.group(2))] = m.group(3)
    for r in stale:
        key = (r["key"], r["md5"])
        if key not in reg_lines:
            errs.append("§2 没登记 need %s 引的 md5 %s (★这条 need 引的是过期值·照抄会把锚点写错★)" % (r["key"], r["md5"]))
            continue
        got = reg_lines[key]
        if got != r["disposition"]:
            errs.append("need %s / md5 %s 的处置词 %r ≠ 机器判据 %r (★在链上⇒退休·不在链上⇒改写★)"
                         % (r["key"], r["md5"], got, r["disposition"]))
    # ★★对【每一条登记行】无条件复核处置词 (★与 pending 扫描面无关 ⇒ need 闭合之后照样复核·不许靠「已闭合」把判据变松★) ★★
    for (rk, rm), got in sorted(reg_lines.items()):
        want = machine_disposition(facts, rm)
        if want and got != want:
            errs.append("§2 登记的 need %s / md5 %s 的处置词 %r ≠ 机器判据 %r (★在链上⇒退休·不在链上⇒改写·是现值⇒保持★)"
                         % (rk, rm, got, want))
    # need 级: 每条引着 md5 字面量的 to=sw-lead 未闭合 need 都得在 §2 有登记
    need_keys = []
    for n in facts["sw_needs"]:
        item = n.get("item", "") or ""
        if HEX32_RE.search(item) or HEX8_RE.search(item):
            need_keys.append(n.get("key"))
    for k in need_keys:
        if not any(rk == k for rk, _ in reg_lines):
            errs.append("§2 没登记 need %s (★它引着 md5 字面量·必须有清理口径★)" % k)
    # ★页里登记的 need: 必须仍然【未闭合】(在待办队列里) 或【已由 sw-lead 自己答复闭合】★
    #   ⇒ 已闭合的那批 (★本单走 frag_write 登记 answer 闭掉的 9 条★) 不许因为「不在待办队列里」而判红
    #   ⇒ 但它的答复里必须【带链头证据】(★不许只写「已处理」三个字★) ⇒ 且答复里引的每个陈旧 md5 都必须在 §2 登记
    pending_keys = {n.get("key") for n in facts["sw_needs"]}
    ans_by_key = {}
    for a in facts.get("sw_answers") or []:
        ans_by_key.setdefault(a.get("key"), []).append(a)
    registered = sorted({rk for rk, _ in reg_lines})
    for rk in registered:
        if rk in pending_keys:
            continue
        ans = ans_by_key.get(rk) or []
        if not ans:
            errs.append("§2 登记了 need %s · 但 STATE.yaml 的待办队列里已没有它、也没有 sw-lead 的答复 (★登记名对不上★)" % rk)
            continue
        blob = " ".join("%s %s %s" % (a.get("value") or "", a.get("note") or "", a.get("ref") or "") for a in ans)
        heads = [facts["ledger"][r].get("head") for r in MANAGED if facts["ledger"][r].get("head")]
        if not any(h and h in blob for h in heads):
            errs.append("§2 登记的 need %s 已被答复闭合, 但那条答复里没有落表台账链头的实测 md5 (★答复不许只写「已处理」★)" % rk)
        for m in HEX32_RE.findall(blob) + [x.group(1) for x in HEX8_RE.finditer(blob)]:
            if m in facts["allowed_md5"]:
                continue
            # ★短写形态 (8/12 位) 也要按前缀认: 「6aee500e」就是链头 6aee500e60ba 的短写 ⇒ 合法值★
            if any(v.startswith(m) for v in facts["allowed_pref12"]):
                continue
            if not any(rk2 == rk and m2.startswith(m[:12]) for (rk2, m2) in reg_lines):
                errs.append("need %s 的答复里引了 md5 %s · §2 没登记它 (★答复不许引未登记的陈旧值★)" % (rk, m))
    return {"ok": not errs, "id": "H3", "title": "待办 need 里引着的过期 md5 逐条给了清理口径",
            "detail": "未闭合需求共 %d 条 · to=sw-lead 未闭合 %d 条 (★本单走 frag_write 闭掉 9 条重锚 need★) · "
                      "§2 已登记 need %d 条 · 当前扫描面里的陈旧 md5 %d 条"
                      % (facts.get("sw_pending_total", 0), len(facts["sw_needs"]), len(registered), len(stale)),
            "rows": stale, "errors": errs}


def h4_no_s10_item(root: str, page: str, facts: dict) -> dict:
    errs = []
    reg = block(page, "H4-REG")
    if not reg.strip():
        errs.append("页里没有 H4-REG 登记块 ⇒ 「S10 换封装真值在 8 条清单里无条目」这个事实没被登记")
    n_items = len(facts["sync_items"])
    n_topic = len(facts["sync_cover_topic"])
    n_generic = len(facts["sync_cover_generic"])
    for k, want, label in (("H4-ITEMS", n_items, "清单条目数"), ("H4-COVER", n_topic, "讲 fp 栏的条目数"),
                            ("H4-GENERIC", n_generic, "泛提「封装」的条目数")):
        v = kv(reg, k)
        if v != str(want):
            errs.append("H4-REG 的 %s=%r ≠ 实测 %d (★%s被篡改或没写★)" % (k, v, want, label))
    for k, label in (("H4-FINDING", "发现"), ("H4-IMPACT", "影响"), ("H4-COUNTERMEASURE", "对策")):
        if not kv(reg, k).strip():
            errs.append("H4-REG 缺 %s (%s)" % (k, label))
    if not kv(reg, "H4-FINDING").strip() and not kv(reg, "H4-COVER"):
        errs.append("H4-REG 没写发现")
    return {"ok": not errs, "id": "H4", "title": "8 条板侧输入清单里没有「S10 换封装真值」这一条",
            "detail": "清单 %d 条 · 讲 fp 栏 %d 条 · 泛提封装 %d 条 (%s)"
                      % (n_items, n_topic, n_generic, ", ".join(facts["sync_cover_generic"]) or "无"),
            "errors": errs}


def h5_sop_triplet(page: str) -> dict:
    errs = []
    s1 = block(page, "S1-TABLE")
    s2 = block(page, "S2-NEEDS")
    s3 = block(page, "S3-SOP")
    for name, body in (("§1 逐闸影响表", s1), ("§2 need 清理口径", s2), ("§3 当天 SOP", s3)):
        if not body.strip():
            errs.append("%s 块缺失或为空" % name)
    for i in range(1, 11):
        if ("<!-- G%02d -->" % i) not in s1:
            errs.append("§1 逐闸影响表缺 G%02d 行 (10 道闸一行不许缺)" % i)
    if s3.strip():
        for kw in ("当天先跑什么", "红了先看哪一条", "绝对不许做"):
            if kw not in s3:
                errs.append("§3 当天 SOP 缺「%s」这一段" % kw)
    if s2.strip():
        for kw in ("退休", "改写"):
            if kw not in s2:
                errs.append("§2 need 清理口径 缺处置词「%s」" % kw)
    return {"ok": not errs, "id": "H5", "title": "SOP 三件套齐全 (§1 / §2 / §3)",
            "detail": "§1 %d 字 · §2 %d 字 · §3 %d 字" % (len(s1), len(s2), len(s3)), "errors": errs}


def h6_forbidden(page: str) -> dict:
    hits = find_forbidden(page)
    return {"ok": not hits, "id": "H6", "title": "禁语检查 (老板 2026-11-12 02:02 政策)",
            "detail": "命中 %d 处" % len(hits),
            "errors": ["禁语命中: %r @ offset %d" % (p, s) for p, s in hits]}


def h7_evidence_levels(page: str) -> dict:
    errs = []
    for tok in set(re.findall(r"\[[^\[\]]{1,40}\]", page)):
        if tok in EV_WHITELIST:
            continue
        if any(k in tok for k in EV_KEYWORDS):
            errs.append("证据等级「%s」不在五级白名单 %s" % (tok, "/".join(EV_WHITELIST)))
    if "[官方]" in page:
        errs.append("页里出现「[官方]」⇒ 判红 (白名单只认 [官网]/[实测]/[媒体]/[推算]/[0数据])")
    return {"ok": not errs, "id": "H7", "title": "证据等级五级白名单",
            "detail": "越界等级 %d 处" % len(errs), "errors": errs}


# ==================================================================================================
# 主流程
# ==================================================================================================
def run_all(root: str, page_path: str, skip_h0: bool = False, h0_cached: dict = None) -> dict:
    page = read_text(page_path)
    facts = collect_facts(root)
    h0 = h0_cached if h0_cached is not None else ({"ok": True, "rows": [{"gate": r, "rc": None, "ok": True}
                                                                     for r, _n, _a in BASELINE_GATES]}
                                                   if skip_h0 else h0_baseline(root))
    checks = [
        h0,
        h1_fp_registered(root, page, facts, h0),
        h2_chain_head(root, facts),
        h3_need_cleanup(root, page, facts),
        h4_no_s10_item(root, page, facts),
        h5_sop_triplet(page),
        h6_forbidden(page),
        h7_evidence_levels(page),
    ]
    return {"checks": checks, "facts": facts, "page": page_path}


def print_report(rep: dict) -> None:
    print("=" * 78)
    print("ISS-362 · SW 侧「S10 换封装真值」影响面闸")
    print("页 = %s" % rep["page"])
    print("=" * 78)
    for c in rep["checks"]:
        print("\n[%s] %s ⇒ %s" % (c["id"], c["title"], "✅ 绿" if c["ok"] else "❌ 红"))
        print("     %s" % c.get("detail", ""))
        for e in c.get("errors", [])[:14]:
            print("       · %s" % e)
        if c["id"] == "H0":
            for r in c["rows"]:
                print("       · %-58s rc=%s %s" % (r["gate"], r["rc"], "✔" if r["ok"] else "✘"))
        if c["id"] == "H2":
            for r in c.get("rows", []):
                print("       · %-26s 盘上=%s 链头=%s 产出单号=%s 链长=%d"
                      % (r["file"], r["disk"][:12], (r["head"] or "None"), r["iss"], r["chain_len"]))
        if c["id"] == "H3":
            for r in c.get("rows", [])[:40]:
                print("       · %-46s %-34s %s" % (r["key"], r["md5"], r["disposition"]))
    red = [c["id"] for c in rep["checks"] if not c["ok"]]
    print("\n" + "-" * 78)
    print("判决: %s" % ("✅ rc=0 · 八条全过" if not red else "❌ rc=1 · 红的判据: %s" % ",".join(red)))
    print("-" * 78)


# ==================================================================================================
# --selftest (★反向用例 ≥6 条 · 每条自证「红的是目标那一条, 其余仍绿」★)
# ==================================================================================================
def selftest(root: str, page_path: str) -> int:
    sbx = os.path.join(root, SBX_REL)
    if os.path.isdir(sbx):
        shutil.rmtree(sbx)
    os.makedirs(sbx, exist_ok=True)
    base = read_text(page_path)

    # 基线快照 (★H0 只跑一次 · 后面 6 条用例复用 ★)
    print("★ selftest: 先跑一遍基线 (H0 十道闸) …")
    h0 = h0_baseline(root)
    rep0 = run_all(root, page_path, h0_cached=h0)
    red0 = {c["id"] for c in rep0["checks"] if not c["ok"]}
    print("   基线红的判据 = %s" % (sorted(red0) or "无"))

    cases = []

    def case(cid, target, desc, mutate):
        cases.append((cid, target, desc, mutate))

    def mut_replace(old, new):
        def _m(t):
            assert old in t, "★用例夹具坏了: 页里找不到 %r★" % old
            return t.replace(old, new, 1)
        return _m

    def mut_delete_block(name):
        def _m(t):
            pat = re.compile(r"<!--\s*%s:BEGIN\s*-->.*?<!--\s*%s:END\s*-->" % (re.escape(name), re.escape(name)),
                             re.S)
            assert pat.search(t), "★用例夹具坏了: 页里找不到 %s 块★" % name
            return pat.sub("", t, count=1)
        return _m

    # ① 页里删掉 §3 ⇒ H5 红
    case("ST-1", "H5", "页里删掉 §3 当天 SOP ⇒ H5 红", mut_delete_block("S3-SOP"))
    # ② 页里塞禁语 ⇒ H6 红
    case("ST-2", "H6", "页里塞进禁语 ⇒ H6 红",
         mut_replace("## §4 · 复现命令清单",
                     "## §4 · 复现命令清单\n\n★处置: 等原厂回信 ★\n"))
    # ③ 篡改 §1 的某个闸读数 ⇒ H1 红
    def mut_st1(t):
        m = re.search(r"(<!-- G05 -->.{0,400}?现状\s*rc\s*=\s*)(\S+)", t, re.S)
        assert m, "★用例夹具坏了: 找不到 G05 的现状 rc★"
        return t[:m.start(2)] + "999" + t[m.end(2):]
    case("ST-3", "H1", "篡改 §1 逐闸表里 G05 的「现状 rc」⇒ H1 红", mut_st1)
    # ④ 把「盲区」写成「无问题」⇒ H1 红
    def mut_blind(t):
        m = re.search(r"(H1-BLINDSPOT\s*[:：]\s*)([^\n]*)", t)
        assert m, "★用例夹具坏了: 找不到 H1-BLINDSPOT★"
        return t[:m.start(2)] + "S10 这一跳在 SW 侧无问题" + t[m.end(2):]
    case("ST-4", "H1", "把 H1 登记里的「盲区」改写成「无问题」⇒ H1 红", mut_blind)
    # ⑤ 篡改 §2 某条 need 的清理口径 (处置词) ⇒ H3 红
    def mut_need(t):
        m = re.search(r"(NEED-KEY\s*[:：]\s*iss233_sw_md5_reanchor[^\n]*?DISPOSITION\s*[:：]\s*)(退休|改写|保持)",
                      t)
        assert m, "★用例夹具坏了: 找不到 iss233_sw_md5_reanchor 的登记行★"
        return t[:m.start(2)] + ("改写" if m.group(2) != "改写" else "退休") + t[m.end(2):]
    case("ST-5", "H3", "篡改 §2 里 iss233_sw_md5_reanchor 的处置词 ⇒ H3 红", mut_need)
    # ⑥ 篡改 H4 提到的清单条目数 ⇒ H4 红
    case("ST-6", "H4", "篡改 H4-REG 的 H4-ITEMS 条目数 ⇒ H4 红",
         mut_replace("H4-ITEMS: 8", "H4-ITEMS: 9"))

    npass = 0
    for cid, target, desc, mutate in cases:
        sbx_page = os.path.join(sbx, "page_%s.md" % cid)
        with open(sbx_page, "w", encoding="utf-8") as f:
            f.write(mutate(base))
        # ★沙盒纪律: 必须是真文件·不许软链 (ISS-327 cont1 根因)★
        assert not os.path.islink(sbx_page), "★沙盒里出现了软链★"
        rep = run_all(root, sbx_page, h0_cached=h0)
        red = {c["id"] for c in rep["checks"] if not c["ok"]}
        want = red0 | {target}
        ok = (red == want)
        print("\n  %s %-4s %s" % ("✅" if ok else "❌", cid, desc))
        print("      期望红集合 = %s ; 实际红集合 = %s ⇒ %s"
              % (sorted(want), sorted(red), "一致" if ok else "★不一致★"))
        if ok:
            npass += 1
        else:
            for c in rep["checks"]:
                if not c["ok"] and c["id"] != target:
                    print("      ★多红的那一条: %s · %s" % (c["id"], c.get("errors", [])[:3]))

    # 沙盒卫生
    links = []
    for dirpath, _dirs, files in os.walk(sbx):
        for fn in files:
            p = os.path.join(dirpath, fn)
            if os.path.islink(p):
                links.append(p)
    print("\n  ★沙盒卫生: find -type l 命中 = %d (★必须 = 0·禁止 os.symlink()★)" % len(links))
    if links:
        npass = 0

    print("\n" + "-" * 78)
    print("SELFTEST %d/%d 通过 ⇒ %s" % (npass, len(cases), "✅ 一致 (反向用例全抓到)" if npass == len(cases) else "❌ 有用例没抓到"))
    print("-" * 78)
    return 0 if npass == len(cases) else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="ISS-362 SW 侧 S10 换封装真值影响面闸")
    ap.add_argument("--selftest", action="store_true", help="反向用例")
    ap.add_argument("--json", action="store_true", help="机读输出")
    ap.add_argument("--page", default=None, help="指定被检页路径 (★沙盒用★)")
    args = ap.parse_args()

    page_path = args.page or os.path.join(PROJ, PAGE_REL)
    if not os.path.isfile(page_path):
        print("❌ 被检页不存在: %s" % page_path)
        return 2

    if args.selftest:
        return selftest(PROJ, page_path)

    rep = run_all(PROJ, page_path)
    if args.json:
        out = {"ok": all(c["ok"] for c in rep["checks"]),
               "checks": [{"id": c["id"], "title": c["title"], "ok": c["ok"],
                           "detail": c.get("detail", ""), "errors": c.get("errors", [])} for c in rep["checks"]]}
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print_report(rep)
    return 0 if all(c["ok"] for c in rep["checks"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
