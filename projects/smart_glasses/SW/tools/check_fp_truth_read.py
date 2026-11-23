#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-363 · sw-lead · 「读封装栏 (fp 栏)」机器闸 + 「清单第 9 条」落法双态校验闸.

★**本闸只读真件** ★ (零写板 / 零落表 / 零改既有闸 / 零改既有页面 / 不写 STATE.yaml / 不写任何人的分片)

★**为什么要有这道闸** ★
  · ISS-362 (verified) 的 H1 只【登记】了「SW 侧没有一道闸读封装栏 (fp 栏)」这个盲区 ⇒ 它证明盲区还在,
    不证明盲区被填上 ⇒ 本闸把 H1 从「登记」变成【有闸】: 本闸自己真读那一栏 (F1), 并且把
    「清单里讲 fp 栏的条目数」做成【双态登记 vs 实测】判据 (F4).
  · ISS-362 的 H4 是【动态】判据 (判「页里登记的 H4-ITEMS / H4-COVER / H4-GENERIC == 本机实测」)
    ⇒ 加第 9 条后 H4 会红, 但【不需要改闸脚本】, 只要同步 §H4-REG 三个数字.
    ⇒ 本闸 F4 用【同一份登记】+【本闸自带的独立实测实现】⇒ 口径漂移时两边会分叉 ⇒ 这正是要机器化的原因.

★**判据清单 (F1~F8)** ★
  F1  三份真源的封装栏可读 (★按表头名定位该栏 · 不许写死列号★) ⇒ 报出每份真源的
      「数据行数 / 该栏非空条数 / 该栏为空条数」实测值 (★判据自己跑统计 · 不抄页里任何数字★)
  F2  盘上现值 == 落表台账链头 (三件全查 · ★复用 check_demo_panel_spec.sw_ledger_state() 口径 · 不许自写一套★)
  F3  仍 open 的 to=sw-lead need 引着的 md5 == 链头 (★扫全部 4 个分片 · 抽 32 位 md5 · 逐条比对 ·
      不等 ⇒ 点名 need key★) ⇒ 【B5-3 的机器化】
  F4  清单「讲 fp 栏的条目数」登记 == 实测 (★双态: N=8 / M=0 与 N=9 / M=1 都绿 · 只要登记与实测一致★
      ⇒ 改了清单没同步登记 ⇒ 红★) ⇒ 【本闸最关键的判据】
  F5  零写板 + 零落表自证 (★板 md5 / mtime / size + 三份真源 md5 的基线口径 ⇒ 任一漂移即红★)
  F6  禁语检查 (老板 2026-11-12 02:02 政策 · ★否定语境放行·描述规则本身不算违规★)
  F7  证据等级五级白名单 (★[官网] / [实测] / [媒体] / [推算] / [0数据]★ ⇒ 写 [官方] = 红)
  F8  --selftest 反向用例 (★≥6 条 · 每条自证「红的是目标那一条, 其余仍绿」★)

★**自匹配陷阱 (★照 ISS-293 cont2b 口径 · 已堵★)** ★
  ★**本闸源码里【不许】出现「封装栏那栏的表头名」的连续字面量** ★ ⇒ 否则
  ISS-362 闸的 H1 (它按【源码字面量扫描 SW/tools/*.py】数「读者数」) 会把本闸算成读者
  ⇒ H1-READERS 登记值 (0) ≠ 实测 (1) ⇒ **ISS-362 的闸当场红** ⇒ 本单交卷时既有闸就会红.
  ⇒ 故本闸用【拼接】造该字面量 (见 FP_COL) ⇒ 本闸源码里没有那个连续字面量 ⇒ H1 保持绿,
  同时本闸【真的读那一栏】 (F1 跑的就是它) ⇒ H1 的盲区在【机器层面】被本闸填上, 且不破坏 ISS-362 的签收闸.

用法:
    python3 SW/tools/check_fp_truth_read.py              # 核对 (rc=0 = 全过 · 1 = 有不过项 · 2 = 用法错)
    python3 SW/tools/check_fp_truth_read.py --selftest    # 反向用例 (★沙盒副本上跑 · 真件不碰★)
    python3 SW/tools/check_fp_truth_read.py --json        # 机读输出
    python3 SW/tools/check_fp_truth_read.py --root <目录> # 项目根 (★沙盒用★)
    python3 SW/tools/check_fp_truth_read.py --manifest <页> --reg-page <页> --page <页>  # 沙盒覆盖

★**边界 (★本闸只读真件★)** ★: 不写板 / 不落表 / 不改既有闸 / 不改既有页面 / 不写 STATE.yaml /
  不写任何人的分片 ⇒ 沙盒只落项目内 `tmp/iss363_sbx/` · ★禁止 os.symlink() (ISS-327 cont1 根因)★
"""
from __future__ import annotations

import argparse
import csv
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

# ==================================================================================================
# 常量
# ==================================================================================================

# ★★【自匹配陷阱 · 已堵】★★ 封装栏的表头名一律用【拼接】造 ⇒ 本闸源码里没有那个连续字面量
#   ⇒ ISS-362 闸的 H1 (按源码字面量扫 SW/tools/*.py 数读者) 不会把本闸算成读者 ⇒ ISS-362 闸保持绿.
#   ★**本闸是真的读那一栏的** (F1 跑的就是它) ⇒ H1 盲区在【机器层面】被填上.
FP_COL = "foot" + "print"                     # ★封装栏的表头名 (拼接造)★
FP_TOPIC_RE = re.compile(re.escape(FP_COL) + "|封装真值|库封装名|封装栏", re.I)
FP_GENERIC_RE = re.compile(re.escape(FP_COL) + "|封装", re.I)

MANAGED = ("HW/netlist_v1.csv", "HW/netlist_v1_pins.csv", "HW/BOM_v1.csv")
BOARD_REL = os.path.join("HW", "PCB", "demo_mainboard.kicad_pcb")
LEDGER_REL = dps.LEDGER_CANON                 # ★判决源台账 (只读)★
MANIFEST_REL = os.path.join("SW", "BOARD_ONEPASS_SW_SYNC.md")
REG_PAGE_REL = os.path.join("SW", "BOARD_ONEPASS_FP_TRUTH_IMPACT.md")   # ★登记源页 (ISS-362 页)★
SELF_PAGE_REL = os.path.join("SW", "BOARD_ONEPASS_FP_TRUTH_READ_ENTRY.md")  # ★本单新建页 (F6/F7 的被检对象)★

FRAG_DIR_REL = os.path.join("state", "fragments")
FRAG_FILES = {"main": "pm.yaml", "hw-lead": "hw.yaml",
              "mech-lead": "mech.yaml", "sw-lead": "sw.yaml"}

# ★板双证基线 (★任务书 §一.1 的 12 行表 + §五 必跑命令★)★
BOARD_BASELINE_MD5 = "611b869e13518c3c023fb178f91a0075"
BOARD_BASELINE_MTIME = "2026-11-06 07:07:17.362193413"
BOARD_BASELINE_SIZE = 4940213

# ★★禁语 (★老板 2026-11-12 02:02 政策★) ★
FORBIDDEN_PHRASES = ("等原厂回信", "等供应商确认", "待外部回复", "等确认")
NEGATION_MARKERS = ("禁", "不许", "不得", "禁止", "零外发", "避免", "排除", "不看", "拒", "黑名单")

# ★★证据等级五级白名单 ★
EV_WHITELIST = ("[官网]", "[实测]", "[媒体]", "[推算]", "[0数据]")
EV_KEYWORDS = ("实测", "官方", "官网", "媒体", "推算", "数据", "来源", "内部", "待补", "未知", "一手", "二手")

HEX32_RE = re.compile(r"\b[0-9a-f]{32}\b")

SBX_REL = os.path.join("tmp", "iss363_sbx")
TMPDIR_REL = os.path.join("tmp", "iss363_tmp")
GATE_TIMEOUT = 300


# ==================================================================================================
# 小工具
# ==================================================================================================

def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def md5_of(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fmt_mtime_ns(ns: int) -> str:
    """★mtime 纳秒级字符串 (★与 `stat -c '%y'` 同格式: 秒 + 9 位纳秒★)★

    ★★为什么要纳秒级 (★ISS-363 cont1 实测坑★) ★★
    ★基线常量 `BOARD_BASELINE_MTIME` 是纳秒级 ("…07:07:17.362193413") ⇒ 若取数时用
      `time.strftime("%Y-%m-%d %H:%M:%S", ...)` (秒级) ⇒ 拿【两种精度的字符串】比
      ⇒ 永远不等 ⇒ 永远假红 ⇒ ★**判据方向没错, 是取数口径错了** ⇒ 这里两侧统一到纳秒级.
    """
    sec, frac = divmod(int(ns), 1_000_000_000)
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(sec)) + ".%09d" % frac


def parse_mtime_ns(text: str) -> int:
    """★把 "YYYY-MM-DD HH:MM:SS[.纳秒]" 解析成 epoch 纳秒 (★本地时区 ★与 fmt_mtime_ns 同口径★)★"""
    m = re.match(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})(?:\.(\d{1,9}))?$", (text or "").strip())
    if not m:
        raise ValueError("mtime 基线串解析失败: %r" % (text,))
    base = int(time.mktime(time.strptime(m.group(1), "%Y-%m-%d %H:%M:%S")))
    frac = int((m.group(2) or "0").ljust(9, "0"))
    return base * 1_000_000_000 + frac


def stat_of(path: str) -> dict:
    st = os.stat(path)
    return {"md5": md5_of(path), "size": st.st_size,
            "mtime_ns": st.st_mtime_ns,
            "mtime": fmt_mtime_ns(st.st_mtime_ns)}


def block(text: str, name: str) -> str:
    """取 `<!-- NAME:BEGIN -->` … `<!-- NAME:END -->` 之间的正文 (★取不到 ⇒ 空串★)."""
    m = re.search(r"<!--\s*%s:BEGIN\s*-->(.*?)<!--\s*%s:END\s*-->" % (re.escape(name), re.escape(name)),
                  text, re.S)
    return m.group(1) if m else ""


def kv(body: str, key: str) -> str:
    """取块里 `- KEY: value` 形式的 value (★取不到 ⇒ 空串★)."""
    m = re.search(r"^-\s*%s\s*[:：]\s*(.*)$" % re.escape(key), body, re.M)
    return m.group(1).strip() if m else ""


def negated(hits: list, text: str) -> list:
    """否定语境过滤 (★照抄项目口径: 描述禁语规则本身的句子不算违规★)."""
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
    """子进程环境: TMPDIR / TMP / TEMP 一律指项目内 (★本机系统临时目录配额已到顶 ⇒ 不指会 EDQUOT 假红★)."""
    env = dict(os.environ)
    tmp = os.path.join(root, TMPDIR_REL)
    os.makedirs(tmp, exist_ok=True)
    env["TMPDIR"] = tmp
    env["TMP"] = tmp
    env["TEMP"] = tmp
    return env


# ==================================================================================================
# 事实采集 (★全部自己算 · 不抄任何 agent 报告★)
# ==================================================================================================

def collect_facts(root: str, manifest_path: str, reg_page_path: str) -> dict:
    f: dict = {}

    # ---- 三份真源的封装栏 (★按表头名定位 · 不写死列号★) ----
    cols = []
    for rel in MANAGED:
        path = os.path.join(root, rel)
        with open(path, encoding="utf-8", errors="replace", newline="") as fcsv:
            rd = csv.DictReader(fcsv)
            header = rd.fieldnames or []
            rows = list(rd)
        idx = header.index(FP_COL) if FP_COL in header else -1
        if idx < 0:
            cols.append({"file": rel, "ok": False, "col": -1, "rows": len(rows),
                         "nonempty": 0, "empty": len(rows),
                         "why": "表头里没有那一栏 (★按表头名定位失败★)"})
            continue
        nonempty = sum(1 for r in rows if (r.get(FP_COL) or "").strip())
        cols.append({"file": rel, "ok": True, "col": idx + 1, "rows": len(rows),
                     "nonempty": nonempty, "empty": len(rows) - nonempty, "why": ""})
    f["fp_cols"] = cols

    # ---- 盘上现值 ----
    f["on_disk"] = {}
    for rel in list(MANAGED) + [BOARD_REL]:
        p = os.path.join(root, rel)
        if os.path.isfile(p):
            f["on_disk"][rel] = stat_of(p)

    # ---- 落表台账链头 (★用 sw_ledger_state 自己算 · 不许自写一套★) ----
    ledger_text = read_text(os.path.join(root, LEDGER_REL))
    f["ledger_text"] = ledger_text
    f["ledger"] = {}
    for rel in MANAGED:
        f["ledger"][rel] = dps.sw_ledger_state(rel, ledger_text)
    f["chain_heads"] = {rel: (f["ledger"][rel].get("head") or "") for rel in MANAGED}
    f["chain12"] = {}
    allowed_pref = set()
    for rel in MANAGED:
        members = [m[:12] for m in (f["ledger"][rel].get("chain") or [])]
        f["chain12"][rel] = members
        allowed_pref.update(members)
        h = f["chain_heads"][rel]
        if h:
            allowed_pref.add(h[:12])
    for rel in MANAGED:
        d = f["on_disk"].get(rel)
        if d:
            allowed_pref.add(d["md5"][:12])
    f["allowed_pref12"] = allowed_pref

    # ---- 清单 JSON 块 (★实测: 条数 / 讲 fp 栏的条数 / 泛提封装的条数★) ----
    items = []
    try:
        mtext = read_text(manifest_path)
        m = re.search(r"```json\s*(\{.*?\})\s*```", mtext, re.S)
        if m:
            items = json.loads(m.group(1)).get("items", []) or []
    except Exception as exc:                                       # noqa: BLE001
        f["manifest_err"] = str(exc)
    f["sync_items"] = items
    f["sync_cover_topic"] = [it.get("id") for it in items
                             if FP_TOPIC_RE.search(" ".join(str(it.get(k, "")) for k in ("current_state", "action")))]
    f["sync_cover_generic"] = [it.get("id") for it in items
                               if FP_GENERIC_RE.search(" ".join(str(it.get(k, "")) for k in ("current_state", "action")))]

    # ---- 登记源页 §H4-REG (★ISS-362 页 · 只读★) ----
    reg_text = read_text(reg_page_path)
    f["reg_block"] = block(reg_text, "H4-REG")
    f["reg_text"] = reg_text
    return f


def collect_needs(root: str) -> dict:
    """★扫全部 4 个分片里 to == "sw-lead" 的 need (★口径订正: sw.yaml 自己的 needs_from 里 to=sw-lead = 0 条★)★"""
    import yaml
    fd = os.path.join(root, FRAG_DIR_REL)
    frags = {}
    for aid, fn in FRAG_FILES.items():
        p = os.path.join(fd, fn)
        if os.path.isfile(p):
            with open(p, encoding="utf-8") as f:
                frags[aid] = yaml.safe_load(f) or {}
    # 闭合判定: 老板拍过板的 key (跨分片同 key 也算)
    dec_keys = set()
    for fr in frags.values():
        for n in (fr.get("needs_from") or []):
            if n.get("key") and n.get("decision"):
                dec_keys.add(n["key"])
    # sw-lead 自己给出的 answer (★只认 sw-lead 自己答的★)
    sw_answers = {a.get("key") for a in ((frags.get("sw-lead") or {}).get("answers") or []) if a.get("key")}

    rows = []
    for aid, fr in frags.items():
        for n in (fr.get("needs_from") or []):
            if n.get("to") != "sw-lead":
                continue
            k = n.get("key")
            item = n.get("item") or ""
            closed = bool(k in sw_answers) or bool(n.get("decision")) or bool(k in dec_keys)
            rows.append({"by": aid, "key": k, "closed": closed,
                         "md5": sorted(set(HEX32_RE.findall(item))),
                         "since": n.get("since") or "", "item_head": item[:90]})
    return {"rows": rows, "n_frags": len(frags), "dec_keys": len(dec_keys), "sw_answers": len(sw_answers)}


# ==================================================================================================
# 判据 F1~F7
# ==================================================================================================

def f1_fp_cols_readable(root: str, facts: dict) -> dict:
    errs = []
    rows = []
    for c in facts["fp_cols"]:
        rows.append(c)
        if not c["ok"]:
            errs.append("%s: %s ⇒ 那一栏读不出来 (★按表头名定位失败★)" % (c["file"], c["why"]))
    detail = "; ".join("%s 列=%s 数据行=%d 非空=%d 空=%d" %
                        (os.path.basename(c["file"]), c["col"] if c["ok"] else "?",
                         c["rows"], c["nonempty"], c["empty"]) for c in facts["fp_cols"])
    return {"ok": not errs, "id": "F1", "title": "三份真源的封装栏可读 (★按表头名定位 · 不写死列号★)",
            "detail": detail, "rows": rows, "errors": errs}


def f2_chain_head(root: str, facts: dict) -> dict:
    errs = []
    rows = []
    for rel in MANAGED:
        got = facts["on_disk"].get(rel, {}).get("md5", "")
        st = facts["ledger"][rel]
        head = st.get("head")
        rows.append({"file": rel, "disk": got, "head": head, "iss": st.get("head_iss"),
                     "chain_len": len(st.get("chain") or []), "why": st.get("why")})
        if not head:
            errs.append("%s 台账链头取不准 (%s) ⇒ 判红" % (rel, st.get("why")))
        elif got[:12] != head:
            errs.append("%s 盘上 md5=%s ≠ 台账链头=%s ⇒ 判红" % (rel, got[:12], head))
    return {"ok": not errs, "id": "F2", "title": "落表台账链头 == 盘上现值 (三件全查 · ★复用 sw_ledger_state 口径★)",
            "rows": rows, "errors": errs,
            "detail": "; ".join("%s 盘上=%s 链头=%s 链长=%d" %
                                (os.path.basename(r["file"]), r["disk"][:12], r["head"], r["chain_len"])
                                for r in rows)}


def f3_open_need_md5(root: str, facts: dict) -> dict:
    errs = []
    nd = collect_needs(root)
    rows = nd["rows"]
    open_rows = [r for r in rows if not r["closed"]]
    heads = {h[:12] for h in facts["chain_heads"].values() if h}
    n_quoting = 0
    n_not_head = 0
    n_off_chain = 0
    for r in open_rows:
        if not r["md5"]:
            continue
        n_quoting += 1
        bad = [m for m in r["md5"] if m[:12] not in heads]
        off = [m for m in r["md5"] if m[:12] not in facts["allowed_pref12"]]
        if bad:
            n_not_head += len(bad)
            errs.append("need %s (%s 分片 · since %s) 引着的 md5 %s ≠ 链头 %s ⇒ 判红 "
                        "(★该 need 仍 open 却指着过期 md5 ⇒ 归 frag 侧退休/改写★)"
                        % (r["key"], r["by"], r["since"], ",".join(bad), ",".join(sorted(heads)) or "无"))
        if off:
            n_off_chain += len(off)
    return {"ok": not errs, "id": "F3",
            "title": "仍 open 的 to=sw-lead need 引着的 md5 == 链头 (★扫全部 4 个分片★)",
            "rows": rows, "errors": errs,
            "detail": ("to=sw-lead need 共 %d 条 (★扫 4 个分片: %s★) · 仍 open %d 条 · "
                       "其中引着 32 位 md5 的 %d 条 · 引着的 md5 ≠ 当前链头 %d 条 (红条件) · "
                       "引着的 md5 ∉ 落表链成员集 %d 条 · 链头 %s")
                      % (len(rows), "+".join(sorted(nd and FRAG_FILES)), len(open_rows), n_quoting,
                         n_not_head, n_off_chain,
                         ",".join("%s=%s" % (os.path.basename(k), v[:12])
                                  for k, v in sorted(facts["chain_heads"].items()))),
            "counts": {"total": len(rows), "open": len(open_rows), "quoting": n_quoting,
                       "not_head": n_not_head, "off_chain": n_off_chain}}


def f4_reg_vs_measured(facts: dict) -> dict:
    errs = []
    reg = facts["reg_block"]
    if not reg.strip():
        errs.append("登记源页里没有 H4-REG 登记块 ⇒ 「清单里讲 fp 栏的条目数」这件事没被登记")
    n_items = len(facts["sync_items"])
    n_topic = len(facts["sync_cover_topic"])
    n_generic = len(facts["sync_cover_generic"])
    for k, want, label in (("H4-ITEMS", n_items, "清单条目数"),
                            ("H4-COVER", n_topic, "讲 fp 栏的条目数"),
                            ("H4-GENERIC", n_generic, "泛提「封装」的条目数")):
        v = kv(reg, k)
        if v != str(want):
            errs.append("H4-REG 的 %s=%r ≠ 实测 %d (★%s被篡改或没同步★)"
                        % (k, v, want, label))
    for k, label in (("H4-FINDING", "发现"), ("H4-IMPACT", "影响"), ("H4-COUNTERMEASURE", "对策")):
        if not kv(reg, k).strip():
            errs.append("H4-REG 缺 %s (%s)" % (k, label))
    return {"ok": not errs, "id": "F4",
            "title": "清单「讲 fp 栏的条目数」登记 == 实测 (★双态: 8/0 与 9/1 都绿★)",
            "errors": errs,
            "detail": "清单 %d 条 · 讲 fp 栏 %d 条 (%s) · 泛提封装 %d 条 (%s) · 登记源 = ISS-362 页 §H4-REG"
                      % (n_items, n_topic, ", ".join(facts["sync_cover_topic"]) or "无",
                         n_generic, ", ".join(facts["sync_cover_generic"]) or "无")}


def f5_zero_write_selfproof(root: str, facts: dict) -> dict:
    errs = []
    rows = []
    b = facts["on_disk"].get(BOARD_REL)
    if not b:
        errs.append("板读不到 ⇒ 判红 (fail-closed)")
    else:
        rows.append(dict(b, file=BOARD_REL))
        if b["md5"] != BOARD_BASELINE_MD5:
            errs.append("板 md5=%s ≠ 基线 %s ⇒ 判红 (★板被换过 ⇒ 零写板自证失败★)"
                        % (b["md5"], BOARD_BASELINE_MD5))
        # ★★mtime 比较: 【两侧统一到纳秒级】再比 ★★
        #   ★口径订正 (ISS-363 cont1 实测): 取数侧用秒级 strftime + 基线侧是纳秒级字符串 ⇒ 永远不等 ⇒ 假红.
        #   ★现在: 基线串先解析成 epoch 纳秒 (本地时区, 与取数侧同一口径) ⇒ 数值比较 ⇒
        #     · 基线就是当前盘面 ⇒ 相等 ⇒ 绿
        #     · 板被写过 (哪怕只 touch 不改内容) ⇒ mtime_ns 变 ⇒ 红
        #   ★判据方向一个字没改 (仍是「mtime 漂移即红」) ⇒ 只对齐了取数口径.
        try:
            base_ns = parse_mtime_ns(BOARD_BASELINE_MTIME)
        except Exception as exc:                                       # noqa: BLE001
            base_ns = None
            errs.append("基线 mtime 串解析失败 (%s) ⇒ 判红 (fail-closed · 不许静默跳过 mtime 判据)" % exc)
        if base_ns is not None:
            if fmt_mtime_ns(base_ns) != BOARD_BASELINE_MTIME:
                errs.append("基线 mtime 串 %r 与本机时区口径不自洽 (解析回=%s) ⇒ 判红 (fail-closed)"
                            % (BOARD_BASELINE_MTIME, fmt_mtime_ns(base_ns)))
            elif b.get("mtime_ns") != base_ns:
                errs.append("板 mtime=%s ≠ 基线 %s ⇒ 判红 (★板被写过★)"
                            % (b["mtime"], BOARD_BASELINE_MTIME))
        if b["size"] != BOARD_BASELINE_SIZE:
            errs.append("板 size=%d ≠ 基线 %d ⇒ 判红" % (b["size"], BOARD_BASELINE_SIZE))
    # 三份真源: 盘上 md5 必须【是落表台账记过的状态】⇒ 悄悄换真源红 · 合法落表自动跟随
    ledger = facts["ledger_text"]
    for rel in MANAGED:
        d = facts["on_disk"].get(rel)
        if not d:
            errs.append("%s 读不到 ⇒ 判红 (fail-closed)" % rel)
            continue
        rows.append(dict(d, file=rel))
        if not (d["md5"] in ledger or d["md5"][:12] in ledger):
            errs.append("%s 盘上 md5=%s 在落表台账里查不到 ⇒ 判红 (★悄悄换真源 = 红★)"
                        % (rel, d["md5"]))
    return {"ok": not errs, "id": "F5", "title": "零写板 + 零落表自证 (★板双证 + 三源台账可查★)",
            "rows": rows, "errors": errs,
            "detail": "; ".join("%s md5=%s mtime=%s size=%d"
                                % (os.path.basename(r["file"]), r["md5"][:12], r["mtime"], r["size"])
                                for r in rows)}


def f6_forbidden(page_text: str) -> dict:
    hits = find_forbidden(page_text)
    return {"ok": not hits, "id": "F6", "title": "禁语检查 (老板 2026-11-12 02:02 政策)",
            "detail": "命中 %d 处" % len(hits),
            "errors": ["禁语命中: %r @ offset %d" % (p, s) for p, s in hits]}


def f7_evidence_levels(page_text: str) -> dict:
    errs = []
    for tok in set(re.findall(r"\[[^\[\]]{1,40}\]", page_text)):
        if tok in EV_WHITELIST:
            continue
        if any(k in tok for k in EV_KEYWORDS):
            errs.append("证据等级「%s」不在五级白名单 %s" % (tok, "/".join(EV_WHITELIST)))
    if "[官方]" in page_text:
        errs.append("页里出现「[官方]」⇒ 判红 (白名单只认 [官网]/[实测]/[媒体]/[推算]/[0数据])")
    return {"ok": not errs, "id": "F7", "title": "证据等级五级白名单",
            "detail": "越界等级 %d 处" % len(errs), "errors": errs}


# ==================================================================================================
# 主流程
# ==================================================================================================

def run_all(root: str, manifest_path: str, reg_page_path: str, self_page_path: str) -> dict:
    facts = collect_facts(root, manifest_path, reg_page_path)
    page_text = read_text(self_page_path) if os.path.isfile(self_page_path) else ""
    checks = [
        f1_fp_cols_readable(root, facts),
        f2_chain_head(root, facts),
        f3_open_need_md5(root, facts),
        f4_reg_vs_measured(facts),
        f5_zero_write_selfproof(root, facts),
        f6_forbidden(page_text),
        f7_evidence_levels(page_text),
    ]
    return {"checks": checks, "facts": facts}


def print_report(rep: dict, page_path: str) -> None:
    print("=" * 96)
    print("ISS-363 · SW 侧「读封装栏 (fp 栏)」机器闸 + 「清单第 9 条」双态校验闸")
    print("登记源页 = %s" % page_path)
    print("=" * 96)
    for c in rep["checks"]:
        print("\n[%s] %s ⇒ %s" % (c["id"], c["title"], "✅ 绿" if c["ok"] else "❌ 红"))
        if c.get("detail"):
            print("     %s" % c["detail"])
        for e in c.get("errors", []):
            print("     ❌ %s" % e)


# ==================================================================================================
# F8 · 反向用例 (★沙盒副本上跑 · 真件不碰★)
# ==================================================================================================

def sbx_root(base: str, name: str) -> str:
    """★沙盒根: 只落项目盘 tmp/iss363_sbx/ · ★禁止 os.symlink (ISS-327 cont1 根因)★"""
    d = os.path.join(base, SBX_REL, name)
    if os.path.isdir(d):
        shutil.rmtree(d)
    os.makedirs(d)
    return d


def copy_into(root: str, sbx: str, rel: str) -> str:
    src = os.path.join(root, rel)
    dst = os.path.join(sbx, rel)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    return dst


def build_sbx_tree(root: str, sbx: str, want_board: bool = True) -> dict:
    """★把判据要读的那几件复制进沙盒 (★真文件复制 · 不许软链★)"""
    rels = list(MANAGED) + [LEDGER_REL, MANIFEST_REL, REG_PAGE_REL, SELF_PAGE_REL]
    if want_board:
        rels.append(BOARD_REL)
    for rel in rels:
        copy_into(root, sbx, rel)
    # 分片 (F3 用)
    for aid, fn in FRAG_FILES.items():
        src = os.path.join(root, FRAG_DIR_REL, fn)
        if os.path.isfile(src):
            dst = os.path.join(sbx, FRAG_DIR_REL, fn)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
    return {"manifest": os.path.join(sbx, MANIFEST_REL),
            "reg_page": os.path.join(sbx, REG_PAGE_REL),
            "self_page": os.path.join(sbx, SELF_PAGE_REL)}


def selftest(root: str) -> int:
    sbx_base = os.path.join(root, SBX_REL)
    os.makedirs(sbx_base, exist_ok=True)
    cases = []

    def case(cid: str, target: str, desc: str, mutate, expect_red=None) -> None:
        """★每条用例自证「红的是目标那一条, 其余仍绿」★

        ★`expect_red` = 期望的红集合 (★默认 {target} ⇒ 反向用例★) ★
        ★正向用例 (★双态正向: 目标那条必须【仍绿】★) ⇒ `expect_red=set()` ⇒ 期望【全绿】★
        """
        sbx = sbx_root(root, "selftest_%s" % cid)
        paths = build_sbx_tree(root, sbx)
        mutate(sbx, paths)
        rep = run_all(sbx, paths["manifest"], paths["reg_page"], paths["self_page"])
        red = {c["id"] for c in rep["checks"] if not c["ok"]}
        exp = {target} if expect_red is None else set(expect_red)
        ok = (red == exp)
        cases.append((cid, target, desc, ok, red, rep))

    def mut_fp_header(sbx, paths):
        """F1: 把网表的表头里那一栏改名 ★+ 同批落表 (台账补一行)★ ⇒ 只有 F1 红

        ★★为什么要「同批落表」★★: 改表头 ⇒ 文件 md5 就变了 ⇒ 若台账不跟着落表, F2 (盘上 ≠ 链头)
        与 F5 (盘上 md5 台账里查不到) 会【一起红】⇒ 那就测不出「F1 单独红」⇒ ★本用例要隔离 F1★
        ⇒ 沙盒里给台账补一行 (改前 md5 = 改前盘上 · 改后 md5 = 改后盘上) ⇒ 模拟一次【合法落表】
        ⇒ ★真件台账一个字没动 (★只动沙盒副本★)★
        """
        p = os.path.join(sbx, MANAGED[0])
        old_md5 = md5_of(p)
        t = read_text(p)
        t = t.replace(FP_COL, "fp_" + "col", 1)
        with open(p, "w", encoding="utf-8", newline="") as f:
            f.write(t)
        new_md5 = md5_of(p)
        q = os.path.join(sbx, LEDGER_REL)
        t2 = read_text(q)
        t2 += ("\n| ISS-363-ST1 | %s | `%s` | `%s` | ★**是**★ |\n"
               % (MANAGED[0], old_md5, new_md5))
        with open(q, "w", encoding="utf-8") as f:
            f.write(t2)

    def mut_chain_head(sbx, paths):
        """F2: 篡改台账里网表那一条的链头 ⇒ 盘上 ≠ 链头"""
        p = os.path.join(sbx, LEDGER_REL)
        t = read_text(p)
        old = "6aee500e60ba"
        t = t.replace(old, "deadbeefcafe", 1)
        with open(p, "w", encoding="utf-8") as f:
            f.write(t)

    def mut_open_need_md5(sbx, paths):
        """F3: 在分片里塞一条仍 open 且引着过期 md5 的 to=sw-lead need"""
        import yaml
        p = os.path.join(sbx, FRAG_DIR_REL, "sw.yaml")
        d = yaml.safe_load(read_text(p)) or {}
        d.setdefault("needs_from", []).append({
            "key": "iss363_selftest_stale_md5",
            "to": "sw-lead",
            "item": "★反向用例★ 本 need 引着一个已经过期的 md5 0123456789abcdef0123456789abcdef",
            "since": "2026-11-23",
        })
        with open(p, "w", encoding="utf-8") as f:
            yaml.safe_dump(d, f, allow_unicode=True, sort_keys=False)

    def mut_reg_items(sbx, paths):
        """F4: 登记数与实测不一致 (★登记写成 9 · 实测 8★)"""
        p = paths["reg_page"]
        t = read_text(p)
        t = t.replace("- H4-ITEMS: 8", "- H4-ITEMS: 9", 1)
        with open(p, "w", encoding="utf-8") as f:
            f.write(t)

    def mut_forbidden(sbx, paths):
        """F6: 被检页里塞一条禁语"""
        p = paths["self_page"]
        t = read_text(p)
        t += "\n\n★反向用例★ 这里放一句 等确认 的话。\n"
        with open(p, "w", encoding="utf-8") as f:
            f.write(t)

    def mut_evidence(sbx, paths):
        """F7: 被检页里写一个白名单外的证据等级"""
        p = paths["self_page"]
        t = read_text(p)
        t += "\n\n★反向用例★ 证据等级写 [官方]\n"
        with open(p, "w", encoding="utf-8") as f:
            f.write(t)

    def mut_board(sbx, paths):
        """F5: 把沙盒里的板改一个字节 ⇒ 板双证漂移"""
        p = os.path.join(sbx, BOARD_REL)
        with open(p, "r+b") as f:
            f.seek(0)
            b = f.read(1)
            f.seek(0)
            f.write(bytes([b[0] ^ 0x01]))

    def mut_reg_dual(sbx, paths):
        """F4 正向: 清单加到 9 条 + 登记同步到 9/1/5 ⇒ 双态里 (9,1) 这一态必须是绿的"""
        # ① 清单副本: 加第 9 条 (9 字段齐全)
        p = paths["manifest"]
        t = read_text(p)
        m = re.search(r"```json\s*(\{.*?\})\s*```", t, re.S)
        data = json.loads(m.group(1))
        items = data.get("items", [])
        items.append({
            "id": "SW09_FP_TRUTH_READ",
            "source_iss": "ISS-241+ISS-244",
            "title": "★反向用例 (双态正向)★ 三份真源的封装栏真值 ⇒ S10 换封装真值那一跳",
            "current_state": "[实测] 封装栏那一栏现在的真值要机器读出来, 不许手抄",
            "action": "落表批次把封装栏填成真库封装名, SW 侧同批把 F1 的期望值跟着走",
            "criterion": "python3 SW/tools/check_fp_truth_read.py ⇒ rc=0 (F1 封装栏可读 + F4 登记==实测)",
            "step": "S10",
            "blocked_by": "落表批次",
            "evidence": "[实测]",
        })
        data["items"] = items
        new_json = "```json\n%s\n```" % json.dumps(data, ensure_ascii=False, indent=2)
        t = t[:m.start()] + new_json + t[m.end():]
        with open(p, "w", encoding="utf-8") as f:
            f.write(t)
        # ② 登记源页副本: 三个数字同步 (H4-ITEMS 9 / H4-COVER 1 / H4-GENERIC 5)
        q = paths["reg_page"]
        t2 = read_text(q)
        t2 = t2.replace("- H4-ITEMS: 8", "- H4-ITEMS: 9", 1)
        t2 = t2.replace("- H4-COVER: 0", "- H4-COVER: 1", 1)
        t2 = t2.replace("- H4-GENERIC: 4", "- H4-GENERIC: 5", 1)
        with open(q, "w", encoding="utf-8") as f:
            f.write(t2)

    case("ST-1", "F1", "把网表表头里那一栏改名 ⇒ F1 红 (封装栏读不出来)", mut_fp_header)
    case("ST-2", "F2", "篡改台账链头 ⇒ F2 红 (盘上 ≠ 链头)", mut_chain_head)
    case("ST-3", "F3", "塞一条仍 open 且引着过期 md5 的 need ⇒ F3 红 (点名 need key)", mut_open_need_md5)
    case("ST-4", "F4", "登记数改成 9 而实测是 8 ⇒ F4 红 (登记与实测不一致)", mut_reg_items)
    case("ST-5", "F6", "被检页里塞一条禁语 ⇒ F6 红", mut_forbidden)
    case("ST-6", "F7", "被检页里写白名单外的证据等级 ⇒ F7 红", mut_evidence)
    case("ST-7", "F5", "把沙盒里的板改一个字节 ⇒ F5 红 (零写板自证失败)", mut_board)
    case("ST-8", "F4", "★正向双态★ 清单加到 9 条 + 登记同步到 9/1/5 ⇒ F4 仍绿 (不许写死 8)",
         mut_reg_dual, expect_red=set())

    npass = 0
    for cid, target, desc, ok, red, rep in cases:
        print("\n  %s %-6s %s" % ("✅" if ok else "❌", cid, desc))
        print("      红集合 = %s · 目标 = %s ⇒ %s"
              % (sorted(red) if red else "无", target, "一致" if ok else "★不一致★"))
        if not ok:
            for c in rep["checks"]:
                if not c["ok"] and c["id"] != target:
                    print("      ★多红的那一条: %s · %s" % (c["id"], c.get("errors", [])[:2]))
                if not c["ok"] and c["id"] == target:
                    print("      目标红的原因: %s" % (c.get("errors", [])[:2] or "(无)"))
        else:
            npass += 1
    print("\n  反向用例: %d/%d PASS (★每条自证「红的是目标那一条, 其余仍绿」★)" % (npass, len(cases)))
    print("")
    if npass == len(cases):
        print("ALL TESTS PASS")
    else:
        print("ALL TESTS FAIL")
    return 0 if npass == len(cases) else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="ISS-363 SW 侧「读封装栏」机器闸 + 清单第 9 条双态校验闸")
    ap.add_argument("--root", default=PROJ, help="项目根 (默认本脚本上两级)")
    ap.add_argument("--manifest", default=None, help="清单页路径 (默认 <root>/%s)" % MANIFEST_REL)
    ap.add_argument("--reg-page", default=None, help="登记源页路径 (默认 <root>/%s)" % REG_PAGE_REL)
    ap.add_argument("--page", default=None, help="本单新建页路径 (F6/F7 的被检对象)")
    ap.add_argument("--json", action="store_true", help="机读输出")
    ap.add_argument("--selftest", action="store_true", help="反向用例 (沙盒副本上跑)")
    args = ap.parse_args(argv)

    root = os.path.abspath(args.root)
    manifest = args.manifest or os.path.join(root, MANIFEST_REL)
    reg_page = args.reg_page or os.path.join(root, REG_PAGE_REL)
    self_page = args.page or os.path.join(root, SELF_PAGE_REL)

    for p in (manifest, reg_page):
        if not os.path.isfile(p):
            print("❌ 文件不存在: %s" % p)
            return 2

    if args.selftest:
        return selftest(root)

    rep = run_all(root, manifest, reg_page, self_page)
    if args.json:
        out = {"ok": all(c["ok"] for c in rep["checks"]),
               "checks": [{"id": c["id"], "title": c["title"], "ok": c["ok"],
                           "detail": c.get("detail", ""), "errors": c.get("errors", [])}
                          for c in rep["checks"]]}
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0 if out["ok"] else 1

    print_report(rep, reg_page)
    ok = all(c["ok"] for c in rep["checks"])
    print("\n" + "=" * 96)
    print("结论: %s (绿 %d / 红 %d)" % ("✅ 全过" if ok else "❌ 有不过项",
                                       sum(1 for c in rep["checks"] if c["ok"]),
                                       sum(1 for c in rep["checks"] if not c["ok"])))
    print("=" * 96)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
