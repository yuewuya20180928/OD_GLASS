#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HW/board_reboard.py —— HW 侧「合法改板」通道 (★照 ISS-284 已跑通的口径·不许自创★)
=========================================================================================
★**单号**: ISS-297 · ★**owner**: hw-lead · ★**建通道时刻**: 2026-11-17 18:5x (Asia/Shanghai)
★**零写板 · 零落表 · 零外发** ★

★**为什么要有它 (★main 18:3x 真扫全仓, 原样★)** ★★:
    ★**全仓有 9 道闸硬钉着板 md5 `611b869e…`; 板那一趟 (S1~S13) 合法改板当天, 它们会一起红** ★
    ⇒ ★**而这些红的真实含义是「板被换了」, 不是「板改坏了」** ⇒ ⇒ ★**现场极可能误读成后者
      ⇒ 去改板凑绿 ⇒ 板 md5 变第二次 ⇒ 整趟白跑** ★
    ⇒ ★**本模块给 HW 域那 6 道闸建一条【合法改板】通道** ★

★**★口径已被证明可行 (★不是猜的★)**: `SW/tools/check_demo_panel_spec.py` 在 ISS-284 转成台账口径后,
它已经不再硬钉板 md5 ⇒ 那份清单里根本找不到它 ⇒ ★**⇒ 「不硬钉」不是靠把断言删掉,
是靠判决源换成【落表台账 + 合法改板记录】** ★

★**★通道形状 (★照 ISS-284 已跑通的口径·一个字都不许自创★)★★**:

    reboard: null                     # 还没发生过合法改板 ⇒ 纯 md5 硬保护 (盘上 ≠ 基线 ⇒ 红)
    reboard: {by: <单号>, file: <文件名>, prev_md5: <改前>, md5: <改后>}
                                       # ★一个原子映射: 四项缺一 ⇒ 整条记录无效 ⇒ 红★
                                       # ★且四项必须能在落表台账里【同一行】查到 (单号 + 文件名 + 新旧 md5)★
                                       # ★判据方向不许变: 盘上 ≠ 链头 ⇒ 红 (合法改板只让链头前移)★
                                       # ★fail-closed 三条一条不许动: 链头不唯一 / 链断 / 链头无单号 ⇒ 红★

★**★三个真源, 各管一段 (★不许混★)★★**:
    ① 保护基线 (append-only 的历史事实)  = 锚点 `hard_protected[].md5` (★HW 侧板 md5 台账§5★)
       ⇒ ★**基线不许改来「让它绿」**: 基线必须在落表台账里与该文件【同行】查得到 ⇒ 查不到 ⇒ 红★
    ② 判决源 (链头)                       = 落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` 的【变更行】
       (★只读·append-only 的信任边界★) ⇒ ★合法改板只让【链头前移】, 不许把判据放松★
    ③ 合法改板的背书                       = 锚点 `hard_protected[].reboard` 四项原子映射
       ⇒ ★四项缺一 ⇒ 整条记录无效 ⇒ 红★

★**★判据强度不许减 (★逐条对照·ISS-297 任务书 §2-2★)★★**:
    | 原来                    | 本模块改完必须仍然                          | 不许                        |
    |------------------------|---------------------------------------------|-----------------------------|
    | 盘上 ≠ 基线 ⇒ 红        | ★盘上 ≠ 链头且无合法记录 ⇒ 红★              | 不许改成「取最近一条就绿」    |
    | 基线写死                | ★基线仍是 append-only 的历史事实★           | 不许改基线来「让它绿」        |
    | (无)                   | ★新增 fail-closed 三条★                    | 链头不唯一/链断/链头无单号 ⇒ 仍红 |

★**★与 SW 侧的关系 (★跨域·不许互相 import·各自写自己的★)★**:
    ★机制照抄 `SW/tools/check_demo_panel_spec.py` 的 R6 (★只读参照, SW/ 一个字节没碰★)
    ★但本文件【自己写】(★那是别人地界★) ⇒ 与 SW 侧两套实现、同一口径★

用法 (给 HW 域那 6 道闸用):
    import sys; sys.path.insert(0, "HW")
    import board_reboard
    res = board_reboard.check_file(root, "HW/PCB/demo_mainboard.kicad_pcb",
                                   os.path.join(root, "HW/PCB/demo_mainboard.kicad_pcb"),
                                   "611b869e13518c3c023fb178f91a0075")
    res["ok"], res["msg"], res["reboarded"]
"""
from __future__ import annotations

import hashlib
import os
import re
import shutil
import sys

# ── 三个真源的路径 (★相对项目根★) ────────────────────────────────────────────
LEDGER_REL = "HW/SCHEMATIC_LANDING_V1_LANDED.md"          # ★落表台账 (只读·append-only 的信任边界)★
ANCHOR_REL = "HW/PCB/BOARD_ONEPASS_MD5_LEDGER.md"         # ★HW 侧板 md5 台账 (锚点住这儿)★
ANCHOR_BEGIN = "<!-- BEGIN HW_BOARD_REBOARD_ANCHORS"
ANCHOR_END = "<!-- END HW_BOARD_REBOARD_ANCHORS -->"

PCB_REL = "HW/PCB/demo_mainboard.kicad_pcb"
PRO_REL = "HW/PCB/demo_mainboard.kicad_pro"
GROUP = (PCB_REL, PRO_REL)

# ★★reboard 原子映射的四项 (★缺一 ⇒ 整条记录无效 ⇒ 红★) ★★
REBOARD_FIELDS = ("by", "file", "prev_md5", "md5")

# ★md5 token (★照 SW 侧口径: 32 位全量 + 12 位前缀★) ★
MD_RE = re.compile(r"\b[0-9a-f]{32}\b|\b[0-9a-f]{12}\b")
ISS_RE = re.compile(r"ISS-\d+")


# ── 小工具 ──────────────────────────────────────────────────────────────────
def m12(value) -> str:
    """★md5 归一到 12 位小写前缀 (★落表台账里落表记录用的就是前缀★) ★"""
    return str(value or "").strip().lower()[:12]


def md5_of(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def ledger_path(root: str) -> str:
    """★落表台账路径 (★env `LANDING_LEDGER` 可改 ⇒ 反向用例能指向沙盒副本★) ★"""
    return os.environ.get("LANDING_LEDGER") or os.path.join(root, LEDGER_REL)


def anchor_path(root: str) -> str:
    """★锚点文件路径 (★env `BOARD_REBOARD_ANCHOR` 可改 ⇒ 反向用例能指向沙盒副本★) ★"""
    return os.environ.get("BOARD_REBOARD_ANCHOR") or os.path.join(root, ANCHOR_REL)


def ledger_text(root: str) -> str:
    p = ledger_path(root)
    return read_text(p) if os.path.isfile(p) else ""


def group_aliases(rel: str) -> set:
    """★同组其它受保护件的名字别名 (★用于剔「一行两件两值」的歧义行★) ★"""
    out: set = set()
    for other in GROUP:
        if other == rel:
            continue
        out.add(other)
        out.add(os.path.basename(other))
        out.add(os.path.splitext(os.path.basename(other))[1])
    return out


# ── 锚点 (★reboard 原子映射住这儿★) ────────────────────────────────────────
def load_anchor(root: str):
    """★读锚点块 ⇒ (锚点 dict | None, 错误说明) · ★读不到 ⇒ fail-closed★ """
    p = anchor_path(root)
    if not os.path.isfile(p):
        return None, "★锚点文件不存在: %s★" % p
    txt = read_text(p)
    m = re.search(re.escape(ANCHOR_BEGIN) + r"(.*?)" + re.escape(ANCHOR_END), txt, re.S)
    if not m:
        return None, "★锚点文件里找不到锚点块 (%s ... %s) ⇒ 通道被删了 ⇒ fail-closed★" % (
            ANCHOR_BEGIN, ANCHOR_END)
    try:
        import yaml
    except ImportError as exc:                                # noqa: BLE001
        return None, "★PyYAML 不可用 (%s) ⇒ 读不了锚点块 ⇒ fail-closed★" % exc
    try:
        data = yaml.safe_load(m.group(1))
    except Exception as exc:                                  # noqa: BLE001
        return None, "★锚点块 YAML 解析失败: %s ⇒ fail-closed★" % exc
    if not isinstance(data, dict) or not isinstance(data.get("hard_protected"), list):
        return None, "★锚点块里没有 hard_protected 段 (★或格式不对★) ⇒ fail-closed★"
    return data, ""


def anchor_entry(anchor: dict, rel: str):
    """★锚点里该受保护件的条目 (★找不到 ⇒ None★) """
    for e in (anchor.get("hard_protected") or []):
        if str(e.get("file") or "").strip() == rel:
            return e
    return None


# ── 落表台账解析 (★照 SW 侧口径·自己写·不 import 别人地界★) ─────────────────
def ledger_cover_rows(text: str, rel: str) -> list:
    """★落表台账里提到 rel 的【覆盖行】(表格行 + 至少一个 md5) ⇒ [{'md5s','iss','sec','row','full'}] ★

    ★口径 (★照 SW 侧 `sw_ledger_cover_rows`★): 只认表格行 (行首 `|`) · 文件名同行 (全路径或基名) ·
      单号取行内 `ISS-xxx`, 行内没写就继承【本段段头】的 `ISS-xxx` (★段头没有单号 ⇒ 该段行无单号·比 SW 侧更严★
      ⇒ ★fail-closed 方向★) ★
    """
    out: list = []
    ctx_iss = None
    sec = "(文首)"
    base = os.path.basename(rel)
    for line in (text or "").splitlines():
        s = line.strip()
        if s.startswith("#"):
            sec = s
            hit = ISS_RE.findall(s)
            ctx_iss = hit[0] if hit else None
            continue
        if not s.startswith("|"):
            continue
        if rel not in s and base not in s:
            continue
        toks = [m12(t) for t in MD_RE.findall(s)]
        if not toks:
            continue
        row_iss = ISS_RE.findall(s)
        out.append({"md5s": toks,
                    "iss": row_iss[0] if row_iss else ctx_iss,
                    "sec": sec, "row": s[:200], "full": s})
    return out


def ledger_change_rows(text: str, rel: str, exclude_aliases=()) -> list:
    """★落表台账里 rel 的【变更行】(★改前 md5 ≠ 改后 md5★) ⇒ 合法改板只认这种行 ★

    ★`exclude_aliases` = 同组其它受保护件的名字别名 ⇒ ★一行两件两值 = 歧义行 ⇒ 不算变更行★
    """
    out: list = []
    for r in ledger_cover_rows(text, rel):
        toks = r["md5s"]
        if len(toks) < 2:
            continue
        prev, new = toks[0], toks[-1]
        if prev == new:
            continue
        if any(a and a in r["full"] for a in exclude_aliases):
            continue
        out.append({"prev": prev, "new": new, "iss": r["iss"],
                    "sec": r["sec"], "row": r["row"]})
    return out


def chain_state(recs: list) -> dict:
    """★变更行上的链头 / 链 / 产出单号表 (★取不准 ⇒ head=None ⇒ 判红★) ★"""
    new_keys = {r["new"] for r in recs}
    prev_keys = {r["prev"] for r in recs}
    heads = sorted(new_keys - prev_keys)
    producer: dict = {}
    for r in recs:
        if not r.get("iss"):
            continue
        producer.setdefault(r["new"], set()).add(r["iss"])
    why = ""
    head = None
    if not recs:
        why = "台账里一条变更行都没有"
    elif not heads:
        why = "没有链头 (每条记录都是别人的前驱 ⇒ 台账不成链)"
    elif len(heads) > 1:
        why = "链头不唯一 = %s (取不准 ⇒ 不许判绿)" % (heads,)
    else:
        head = heads[0]
    chain: list = []
    if head:
        by_new: dict = {}
        for r in recs:
            by_new.setdefault(r["new"], []).append(r)
        cur, seen = head, {head}
        chain = [head]
        while True:
            rs = by_new.get(cur) or []
            if not rs:
                break                                  # 链尾 (起源值, 没有产出记录)
            prevs = {r["prev"] for r in rs if r["prev"] != r["new"]}
            if len(prevs) != 1:
                why = why or "链上 %s 的前驱不唯一 = %s" % (cur, sorted(prevs))
                chain = []
                break
            p = prevs.pop()
            if p in seen:
                why = why or "链成环 (%s)" % p
                chain = []
                break
            cur = p
            seen.add(cur)
            chain.append(cur)
    return {"records": recs, "head": head, "chain": chain, "producer": producer,
            "why": why, "head_iss": sorted(producer.get(head, set())) if head else [],
            "known": new_keys | prev_keys}


def row_has_four(text: str, rel: str, by: str, prev: str, new: str) -> bool:
    """★落表台账里有没有【同一行】同时写着 单号 + 文件名 + 改前 md5 + 改后 md5 (★四项缺一 ⇒ 不算查到★) ★"""
    for r in ledger_cover_rows(text, rel):
        if by and r.get("iss") != by:
            continue
        if prev and prev not in r["md5s"]:
            continue
        if new and new not in r["md5s"]:
            continue
        return True
    return False


# ── 判决 (★每个受保护件一次★) ──────────────────────────────────────────────
def check_file(root: str, rel: str, path: str, baseline: str, md5fn=None,
               ledger: str | None = None, anchor: dict | None = None) -> dict:
    """★一个受保护件的判决 ⇒ {'ok','msg','reboarded','head','base','errs'} ★

    ★★判据 (逐条; ★fail-closed: 取不准一律判红★)★★
      ① ★基线自证★: 基线必须在落表台账里与该文件【同行】查到 ⇒ 查不到 ⇒ 红 (★「改基线凑绿」被堵死★)
      ② ★闸里的基线 == 锚点里的基线★ ⇒ 两边不许各改一边
      ③ 台账里该文件【没有变更行】⇒ 不许有 reboard 记录; 且 盘上 md5 必须 == 基线 (★纯 md5 硬保护★)
      ④ 台账里【有变更行】⇒ 链头必须唯一 / 链不断 / 链头有单号 (★fail-closed 三条一条不许动★)
         ⇒ 锚点必须带 reboard 原子记录 (★四项缺一 ⇒ 红★) ⇒ 且四项必须与台账链头逐字对上
         ⇒ 且四项必须能在落表台账里【同一行】查到
         ⇒ 保护基线必须留在链尾 (★不许把基线偷偷前移★)
         ⇒ 盘上 md5 必须 == 台账链头 (★判据方向不许变★)
    """
    md5fn = md5fn or md5_of
    base_in = str(baseline or "").strip()
    if anchor is None:
        anchor, aerr = load_anchor(root)
        if anchor is None:
            return {"ok": False, "reboarded": False, "head": "", "base": base_in,
                    "errs": [aerr],
                    "msg": "★%s: %s ⇒ fail-closed (★通道读不到 ⇒ 一律红★)★" % (rel, aerr)}
    if ledger is None:
        ledger = ledger_text(root)

    errs: list = []
    entry = anchor_entry(anchor, rel)
    if entry is None:
        msg = "★%s: 锚点里没有这个受保护件的条目 ⇒ fail-closed★" % rel
        return {"ok": False, "reboarded": False, "head": "", "base": base_in,
                "errs": [msg], "msg": msg}
    a_base = str(entry.get("md5") or "").strip()
    a_rec = entry.get("reboard")
    if not a_base:
        errs.append("★锚点里 %s 缺基线 md5★" % rel)
    base = a_base or base_in
    if base_in and a_base and m12(base_in) != m12(a_base):
        errs.append("★闸里的基线 %s ≠ 锚点基线 %s ⇒ 有人单独改了一边 ⇒ 判红★"
                    % (m12(base_in), m12(a_base)))
    # ① 基线自证 (★落表台账是 append-only 的见证★)
    covers = ledger_cover_rows(ledger, rel)
    if not any(m12(base) in r["md5s"] for r in covers):
        errs.append("★基线 md5 %s 在落表台账里与 %s 【同行】查不到 ⇒ 疑似【改基线凑绿】⇒ 判红★"
                    % (m12(base), rel))
    # 盘上
    if not os.path.exists(path):
        errs.append("★文件不存在: %s★" % path)
        got = ""
    else:
        got = md5fn(path)

    excl = group_aliases(rel)
    chg = ledger_change_rows(ledger, rel, excl)
    head = ""
    if not chg:
        # ③ 台账里没有变更行 ⇒ 纯 md5 硬保护
        if a_rec not in (None, "", {}, []):
            errs.append("★锚点里有合法改板记录 (reboard), 但落表台账里查不到任何变更行 "
                        "⇒ 单号背书落不了地 ⇒ 判红★")
        if got and m12(got) != m12(base):
            errs.append("★盘上 md5 %s ≠ 基线 %s ⇒ 被改了又没有【合法改板】记录 ⇒ 判红★"
                        % (got, m12(base)))
        head = base
    else:
        # ④ 台账里有变更行 ⇒ 走【合法改板】路径
        st = chain_state(chg)
        head = st.get("head") or ""
        if not head:
            errs.append("★落表台账最新记录取不准 (%s) ⇒ 取错记录可能假绿 ⇒ 判红★" % st.get("why"))
        else:
            if not st.get("head_iss"):
                errs.append("★落表台账链头 (%s) 缺落表单号 ⇒ 判红★" % head)
            chain = st.get("chain") or []
            if not chain:
                errs.append("★落表台账链断了 / 不唯一 (%s) ⇒ 判红★" % st.get("why"))
            else:
                orphan = sorted({r["new"] for r in chg} - set(chain))
                if orphan:
                    errs.append("★落表台账里有记录不在链上 = %s ⇒ 判红★" % orphan)
                if m12(base) != m12(chain[-1]):
                    errs.append("★基线 %s 不在落表台账链尾 (链尾 = %s) ⇒ ★基线被偷偷前移 = 判红★★"
                                % (m12(base), m12(chain[-1])))
            if not isinstance(a_rec, dict):
                errs.append("★落表台账里有变更行, 但锚点没有 reboard 原子记录 "
                            "(★单号/文件名/改前 md5/改后 md5 四项不齐★) ⇒ 判红★")
            else:
                missing = [k for k in REBOARD_FIELDS if not str(a_rec.get(k) or "").strip()]
                if missing:
                    errs.append("★%s 的 reboard 记录四项不齐: 缺 %s ⇒ 判红★"
                                % (rel, ",".join(missing)))
                else:
                    rfile = str(a_rec.get("file")).strip()
                    rprev = m12(a_rec.get("prev_md5"))
                    rmd5 = m12(a_rec.get("md5"))
                    rby = str(a_rec.get("by")).strip()
                    if rfile != rel:
                        errs.append("★%s 的 reboard 记录写的是 %s (≠ 条目文件名) ⇒ 判红★" % (rel, rfile))
                    if rmd5 != head:
                        errs.append("★%s 的 reboard 改后 md5 %s 与落表台账链头 %s 不一致 ⇒ "
                                    "★单号与 md5 不许各自独立编辑 = 判红★" % (rel, rmd5, head))
                    head_prevs = sorted({r["prev"] for r in chg if r["new"] == head})
                    if len(head_prevs) == 1 and rprev != head_prevs[0]:
                        errs.append("★%s 的 reboard 改前 md5 %s 与落表台账链头那一行的改前 %s 不一致 "
                                    "(链断) ⇒ 判红★" % (rel, rprev, head_prevs[0]))
                    if rby not in (st.get("producer") or {}).get(head, set()):
                        errs.append("★%s 的 reboard 单号 %s 与落表台账产出该 md5 的单号对不上 "
                                    "(台账 = %s) ⇒ 判红★"
                                    % (rel, rby or "(空)",
                                       sorted((st.get("producer") or {}).get(head, []))))
                    if not row_has_four(ledger, rel, rby, rprev, rmd5):
                        errs.append("★%s 的四项 (单号 / 文件名 / 改前 md5 / 改后 md5) 在落表台账里"
                                    "【同一行】查不到 ⇒ 判红★" % rel)
            if got and m12(got) != m12(head):
                errs.append("★盘上 md5 %s ≠ 落表台账链头 %s ⇒ 真源被换了或台账没更新 ⇒ 判红★"
                            % (got, m12(head)))

    ok = not errs
    reboarded = ok and bool(chg)
    by = ""
    if isinstance(a_rec, dict):
        by = str(a_rec.get("by") or "").strip()
    if ok:
        if reboarded:
            msg = ("★%s: 盘上 md5 %s == 落表台账链头 (★合法改板·四项齐全·单号 %s★) ⇒ 放行★"
                   % (rel, m12(got), by or "★无单号★"))
        else:
            msg = ("★%s: 盘上 md5 %s == 保护基线 (★落表台账里没有变更行 ⇒ 纯 md5 硬保护·逐字节未变★) ⇒ 放行★"
                   % (rel, m12(got)))
    else:
        msg = ("★%s: %s★" % (rel, " · ".join(errs)))
    return {"ok": ok, "reboarded": reboarded, "head": m12(head), "base": m12(base),
            "errs": errs, "msg": msg, "got": m12(got), "changes": len(chg)}


def check_trip_coverage(ledger: str, heads: dict) -> list:
    """★同组受保护件覆盖: 一次合法改板必须覆盖同组全部件 (★只来一条记录 ⇒ 红★) ★"""
    errs: list = []
    board_rel = PCB_REL
    chg = ledger_change_rows(ledger, board_rel, group_aliases(board_rel))
    trip_iss = sorted({r["iss"] for r in chg if r.get("iss")})
    if not trip_iss:
        return errs
    for iss in trip_iss:
        for rel in GROUP:
            expect = (heads or {}).get(rel)
            if not expect:
                continue
            rows = [r for r in ledger_cover_rows(ledger, rel) if r.get("iss") == iss]
            if not any(expect in r["md5s"] for r in rows):
                errs.append("★%s 没有被同一次合法改板 (%s) 的落表台账登记覆盖 "
                            "(★记录只来一条 ⇒ 判红★)" % (rel, iss))
    return errs


def check_pair(root: str, pcb_path: str, pcb_base: str, pro_path: str, pro_base: str,
               md5fn=None, ledger: str | None = None, anchor: dict | None = None) -> dict:
    """★板 + `.kicad_pro` 两件的判决 (★HW 域 6 道闸共用★) ⇒ dict ★"""
    md5fn = md5fn or md5_of
    if anchor is None:
        anchor, aerr = load_anchor(root)
        if anchor is None:
            return {"ok": False, "reboarded": False, "pcb": None, "pro": None,
                    "errs": [aerr], "msg": "★%s ⇒ fail-closed (★通道读不到 ⇒ 一律红★)★" % aerr}
    if ledger is None:
        ledger = ledger_text(root)
    r_pcb = check_file(root, PCB_REL, pcb_path, pcb_base, md5fn=md5fn, ledger=ledger, anchor=anchor)
    r_pro = check_file(root, PRO_REL, pro_path, pro_base, md5fn=md5fn, ledger=ledger, anchor=anchor)
    heads = {PCB_REL: r_pcb.get("head"), PRO_REL: r_pro.get("head")}
    trip_errs = check_trip_coverage(ledger, heads)
    errs = list(r_pcb.get("errs") or []) + list(r_pro.get("errs") or []) + trip_errs
    ok = not errs
    reboarded = bool(r_pcb.get("reboarded"))
    if ok:
        msg = "%s · %s" % (r_pcb.get("msg"), r_pro.get("msg"))
    else:
        msg = " · ".join(errs)
    return {"ok": ok, "reboarded": reboarded, "pcb": r_pcb, "pro": r_pro,
            "trip_errs": trip_errs, "errs": errs, "msg": msg}


# ── 反向用例沙盒 (★真盘零写★) ─────────────────────────────────────────────
CASE_TICKET = "ISS-9901"          # ★沙盒专用假单号 (★不许硬编码任何真单号★)
CASE_FILES = (ANCHOR_REL, LEDGER_REL, PCB_REL, PRO_REL)


def _bump(path: str) -> str:
    """★在沙盒里给文件加一行 ⇒ 返回新 md5 (★真盘那一份一个字节都不动★) ★"""
    with open(path, "a", encoding="utf-8") as f:
        f.write("\n# ISS-297 selftest: 沙盒注入 (★只存在于沙盒★)\n")
    return md5_of(path)


def _read(path: str) -> str:
    return read_text(path)


def _write(path: str, txt: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(txt)


def _anchor_set(root: str, rel: str, **fields) -> None:
    """★只用于沙盒★: 改锚点里该受保护件的条目 (reboard 原子映射 / 基线) ★"""
    import yaml
    p = anchor_path(root)
    txt = _read(p)
    m = re.search(re.escape(ANCHOR_BEGIN) + r"(.*?)" + re.escape(ANCHOR_END), txt, re.S)
    if not m:
        raise AssertionError("沙盒锚点里找不到锚点块")
    data = yaml.safe_load(m.group(1)) or {}
    for e in data.get("hard_protected") or []:
        if e.get("file") == rel:
            for k, v in fields.items():
                if v is None:
                    e.pop(k, None)
                else:
                    e[k] = v
    block = (ANCHOR_BEGIN + "\n"
             + yaml.safe_dump(data, allow_unicode=True, sort_keys=False, default_flow_style=False)
             + ANCHOR_END)
    _write(p, txt[:m.start()] + block + txt[m.end():])


def _ledger_append(root: str, rows: list) -> None:
    """★只用于沙盒★: 往落表台账末尾追加行 (★真盘的落表台账本单不许碰★) ★"""
    p = ledger_path(root)
    with open(p, "a", encoding="utf-8") as f:
        f.write("\n" + "\n".join(rows) + "\n")


def _row(ticket, rel, prev, new, note="★**是** ★"):
    """★落表台账行 (★格式契约: 单号 | 文件名 | 改前 md5 | 改后 md5 四项同行★) ★"""
    return "| %s | `%s` | `%s` | `%s` | %s |" % (ticket, rel, prev, new, note)


def build_sandbox(root: str, dst: str) -> str:
    """★把通道要读的四件拷进沙盒 (★保持项目内相对路径 ⇒ --root 可直接指过去★) ★"""
    for rel in CASE_FILES:
        src = os.path.join(root, rel)
        d = os.path.join(dst, rel)
        os.makedirs(os.path.dirname(d), exist_ok=True)
        shutil.copy2(src, d)
    return dst


def make_legal(root: str, ticket: str = CASE_TICKET, board_base: str = "", pro_base: str = ""):
    """★沙盒里做一次「合法改板」: ① 板文件改一个字节 ② 锚点写原子 reboard 记录 ③ 台账追加行 ★"""
    pcb = os.path.join(root, PCB_REL)
    pro = os.path.join(root, PRO_REL)
    new = _bump(pcb)
    if not board_base:
        board_base = _anchor_base(root, PCB_REL)
    if not pro_base:
        pro_base = _anchor_base(root, PRO_REL)
    _anchor_set(root, PCB_REL, reboard={"by": ticket, "file": PCB_REL,
                                         "prev_md5": board_base, "md5": new})
    _ledger_append(root, [
        _row(ticket, PCB_REL, board_base, new, "★**是 (★合法改板·板只改一次★)** ★"),
        _row(ticket, PRO_REL, pro_base, pro_base, "★**否 (★逐字节不变★)** ★"),
    ])
    return new


def _anchor_base(root: str, rel: str) -> str:
    anchor, err = load_anchor(root)
    if anchor is None:
        raise AssertionError("沙盒读不到锚点 (%s)" % err)
    e = anchor_entry(anchor, rel)
    if not e:
        raise AssertionError("锚点里没有 %s 的保护基线" % rel)
    return str(e.get("md5") or "")


# ★★用例表 (★ISS-297 任务书 §2-3 的 ①~⑤, 每条都拆到能单独判红★) ★★
#   (用例名, 期望绿?, 构造函数) —— 构造函数吃 (sandbox_root)
CASES = [
    ("① 台账里有合法改板记录 (四项齐全) 且盘上 == 新 md5 ⇒ 绿 (★这就是「合法改板」的样子★)", True,
     lambda r: make_legal(r)),
    ("② 只改了基线里的 md5, 没有台账记录 ⇒ 红 (★这就是「挖坑」, 必须堵死★)", False,
     lambda r: _dig(r)),
    ("③a 台账记录缺单号 (reboard 记录没有 by) ⇒ 红", False,
     lambda r: _make_then_break(r, "by")),
    ("③b 台账记录缺改前 md5 (reboard 记录没有 prev_md5) ⇒ 红", False,
     lambda r: _make_then_break(r, "prev_md5")),
    ("③c 台账记录文件名对不上 (reboard.file 写成 .kicad_pro) ⇒ 红", False,
     lambda r: _make_then_break(r, "file")),
    ("③d 落表台账那一行与它所在段都没有单号 ⇒ 链头无单号 ⇒ 红 (★fail-closed★)", False,
     lambda r: _make_no_iss(r)),
    ("④ 台账里有记录但盘上 md5 ≠ 记录里的新 md5 ⇒ 红 (★合法改板 ≠ 随便改★)", False,
     lambda r: _make_disk_mismatch(r)),
    ("⑤a 链头不唯一 (两条变更行指向同一个文件) ⇒ 红 (★fail-closed★)", False,
     lambda r: _make_two_heads(r)),
    ("⑤b 链断 (链上一个节点有两个前驱) ⇒ 红 (★fail-closed★)", False,
     lambda r: _make_broken_chain(r)),
    ("⑤c 锚点 reboard 的改前 md5 与台账链头那一行的改前对不上 (链断) ⇒ 红 (★fail-closed★)", False,
     lambda r: _make_prev_mismatch(r)),
]


def _dig(root: str) -> str:
    """★② 挖坑: 板改了 + 锚点里的基线也跟着改成新 md5, 但落表台账里一个字都没记 ⇒ 必须红 ★"""
    pcb = os.path.join(root, PCB_REL)
    new = _bump(pcb)
    _anchor_set(root, PCB_REL, md5=new)            # ★只改基线, 不写 reboard 记录, 不落表 ★
    return new


def _make_then_break(root: str, field: str) -> str:
    """★③ 四项不齐: 先做一次合法改板, 再把锚点原子记录里的某一项弄坏 ⇒ 必须红 ★"""
    new = make_legal(root)
    anchor, err = load_anchor(root)
    if anchor is None:
        raise AssertionError("沙盒读不到锚点 (%s)" % err)
    rec = None
    for e in anchor.get("hard_protected") or []:
        if e.get("file") == PCB_REL:
            rec = dict(e.get("reboard") or {})
    if rec is None:
        raise AssertionError("锚点里没有板件的 reboard 记录")
    if field == "file":
        rec["file"] = PRO_REL
    elif field == "by":
        rec["by"] = ""
    else:
        rec[field] = ""
    _anchor_set(root, PCB_REL, reboard=rec)
    return new


def _make_no_iss(root: str) -> str:
    """★③d 落表台账那一行与它所在段都没有单号 ⇒ 链头无单号 ⇒ 红 (★fail-closed★) ★"""
    pcb = os.path.join(root, PCB_REL)
    new = _bump(pcb)
    base = _anchor_base(root, PCB_REL)
    with open(ledger_path(root), "a", encoding="utf-8") as f:
        f.write("\n## ★★沙盒自检 · 这一节没有单号 ★★\n\n"
                "| ★**`%s`** ★ | `%s` | `%s` | ★**是 (★这一行也没有单号★)** ★ |\n"
                % (PCB_REL, base, new))
    _anchor_set(root, PCB_REL, reboard={"by": CASE_TICKET, "file": PCB_REL,
                                         "prev_md5": base, "md5": new})
    return new


def _make_disk_mismatch(root: str) -> str:
    """★④ 台账里有记录, 但盘上板文件没跟着改 ⇒ 盘上 ≠ 记录里的新 md5 ⇒ 红 ★"""
    pcb = os.path.join(root, PCB_REL)
    keep = _read(pcb)                       # ★先把原始字节留一份 (★改完再写回去★)
    new = make_legal(root)
    _write(pcb, keep)                       # ★盘上板回到基线版 (台账却说它已经改了★) ★
    return new


def _make_two_heads(root: str) -> str:
    """★⑤a 两条变更行指向同一个文件 ⇒ 链头不唯一 ⇒ 红 ★"""
    new = make_legal(root)
    base = _anchor_base(root, PCB_REL)
    _ledger_append(root, [
        _row("ISS-9902", PCB_REL, base, "deadbeefdeadbeefdeadbeefdeadbeef",
             "★**是 (★第二跳·另一个头★)** ★"),
    ])
    return new


def _make_broken_chain(root: str) -> str:
    """★⑤b 链上一个节点有两个前驱 ⇒ 链断 ⇒ 红 ★"""
    pcb = os.path.join(root, PCB_REL)
    new = _bump(pcb)
    base = _anchor_base(root, PCB_REL)
    other = "0123456789abcdef0123456789abcdef"
    _ledger_append(root, [
        _row(CASE_TICKET, PCB_REL, base, new, "★**是 (★这一跳★)** ★"),
        _row("ISS-9903", PCB_REL, other, new, "★**是 (★另一个前驱·链断★)** ★"),
    ])
    _anchor_set(root, PCB_REL, reboard={"by": CASE_TICKET, "file": PCB_REL,
                                         "prev_md5": base, "md5": new})
    return new


def _make_prev_mismatch(root: str) -> str:
    """★⑤c 锚点 reboard 的改前 md5 与台账链头那一行的改前对不上 ⇒ 链断 ⇒ 红 ★"""
    new = make_legal(root)
    anchor, err = load_anchor(root)
    if anchor is None:
        raise AssertionError("沙盒读不到锚点 (%s)" % err)
    rec = None
    for e in anchor.get("hard_protected") or []:
        if e.get("file") == PCB_REL:
            rec = dict(e.get("reboard") or {})
    if rec is None:
        raise AssertionError("锚点里没有板件的 reboard 记录")
    rec["prev_md5"] = "0123456789abcdef0123456789abcdef"
    _anchor_set(root, PCB_REL, reboard=rec)
    return new


def run_cases(root: str, workdir: str, judge, prepare=None) -> list:
    """★把 CASES 逐条在沙盒里跑一遍 ⇒ [(用例名, 期望绿?, 实得绿?, 说明)] ★

    ★`judge(root)` = 跑闸的回调 ⇒ 返回 (ok: bool, 说明: str) ★
    ★`prepare(root)` = 可选: 把闸自己还要读的文件也铺进沙盒 (★给需要整棵树的闸用★) ★
    """
    out = []
    for idx, (name, expect_green, mutate) in enumerate(CASES):
        sb = os.path.join(workdir, "case_%02d" % idx)
        build_sandbox(root, sb)
        old = {k: os.environ.get(k) for k in ("LANDING_LEDGER", "BOARD_REBOARD_ANCHOR")}
        try:
            if prepare is not None:
                prepare(sb)
            mutate(sb)
            os.environ["LANDING_LEDGER"] = ledger_path(sb)
            os.environ["BOARD_REBOARD_ANCHOR"] = anchor_path(sb)
            ok, note = judge(sb)
        except AssertionError as exc:
            ok, note = False, "★用例自身坏了: %s★" % exc
        finally:
            for k, v in old.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v
            # ★每条用例跑完立刻删沙盒 (★/tmp 是带 usrquota 的 tmpfs ⇒ 峰值不能堆 10 份 5MB 的板★) ★
            shutil.rmtree(sb, ignore_errors=True)
        out.append((name, expect_green, bool(ok), note))
    return out


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="HW 侧「合法改板」通道 (★判决源 = 落表台账链头★)")
    ap.add_argument("--root", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    help="项目根 (默认 = 本文件上一级)")
    ap.add_argument("--selftest", action="store_true", help="★跑反向用例 (真盘零写)")
    args = ap.parse_args()
    root = os.path.abspath(args.root)

    if args.selftest:
        import tempfile
        with tempfile.TemporaryDirectory(prefix="iss297_channel_") as tmp:
            def judge(sb: str):
                res = check_pair(sb, os.path.join(sb, PCB_REL), _anchor_base(sb, PCB_REL),
                                 os.path.join(sb, PRO_REL), _anchor_base(sb, PRO_REL))
                return res["ok"], res["msg"]
            rows = run_cases(root, tmp, judge)
        bad = 0
        for name, exp, got, note in rows:
            ok = (exp == got)
            if not ok:
                bad += 1
            print("  %s %s" % ("✅" if ok else "❌", name))
            print("      ⇒ 实得: %s" % (("绿" if got else "红") + " · " + str(note)[:150]))
        print("─" * 78)
        print("  ⇒ %d/%d 条符合预期" % (len(rows) - bad, len(rows)))
        return 0 if bad == 0 else 1

    res = check_pair(root, os.path.join(root, PCB_REL), "611b869e13518c3c023fb178f91a0075",
                     os.path.join(root, PRO_REL), "3e504d2be83152e337949723e909be1b")
    print(res["msg"])
    return 0 if res["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
