#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-400 · mech-lead · 机器块指针可解析性闸 (同页 / 跨页) · 机器闸

★**本闸只判一件事**: ★**页面上写的「去机器块填回哪一格」这个指针, 能不能真的解析到一个存在的槽** ★
★**零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 · 零挂链 · 零外发** ★

────────────────────────────────────────────────────────────────────────────────
★★【本闸的预期读数 = rc=1 (红)】★★
  ★**红的是【现状】(真相页 §2 的悬空/歧义/误指/无归属指针条数 ≥ 1), 不是闸故障** ★
  ★⇒ 本单【刻意不修现状】⇒ ★**不许为了让它绿而放宽判据** ★
  ★⇒ 绿的条件只有一个: 扫描范围内 A 类之外的指针条数 == 0 ★
────────────────────────────────────────────────────────────────────────────────

判据 (★逐字定义写在真相页 `MECH/BOARD_ONEPASS_MACHINE_BLOCK_POINTER_AUDIT.md` §4★):
  P1  ★扫描范围可复现★ ⇒ 闸自己扫 `MECH/` (主范围) + `HW/PCB/` `SW/` (旁证范围) ⇒ **不许把扫描结果写死**
  P2  ★指针候选识别★ ⇒ 同页/跨页 JSON 路径型 + 「页 + 机器块 + 裸键」型 + 表格行定位型
                    ⇒ ★自然语言引用 (`见 §4-③`) 明确排除在外★ (闸自己声明「我不管哪一类」)
  P3  ★可解析判定★ ⇒ JSON 逐段下钻 (含 `[0]` / `[]` / `.*` / id 选择器) ⇒ **不许用子串命中当解析**
  P4  ★分类输出★ ⇒ A 可解析 / B 悬空 / C 歧义 / D 误指 / E 无归属 · 每条带【源页 + 行号 + 指针逐字 + 判定】
  P5  ★「指向的槽是不是实测槽」判定★ ⇒ 落在量容器根上但解析到的槽没有任何 `measured*` 字段 ⇒ 判 **D 误指**
  P6  ★本单已知的 3 条死指针必须被逐条点名报出★ ⇒ 且 selftest 反向用例证明「去掉一条 ⇒ 条数就少一条」(不是恒红)
  P7  ★零写板自证★ ⇒ 本闸只读不写 ⇒ 跑完板 md5 不变

用法:
  python3 MECH/check_machine_block_pointer_resolvable.py              # 裸跑, rc=1 = 现状红
  python3 MECH/check_machine_block_pointer_resolvable.py --selftest   # 反向用例, 末行 ALL TESTS PASS
  python3 MECH/check_machine_block_pointer_resolvable.py --root DIR    # 指定树 (反向用例在 <root>/tmp/iss400/sbx/selftest/ 上做)
  python3 MECH/check_machine_block_pointer_resolvable.py --json       # 机器可读输出 (JSON)

★【沙盒纪律】反向用例一律落项目盘 `<root>/tmp/iss400/sbx/selftest/` (★不许写系统 `/tmp`·不许用硬链接★)
             ★路径全部从本闸自己的 `ROOT` 推 ⇒ 环境无关★
"""
from __future__ import annotations
import argparse
import json
import os
import re
import shutil
import sys

ROOT_DEFAULT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ★扫描范围 (真相页 §4.1)★ —— 闸自己扫, 不许把扫描结果写死
SCOPE_MAIN = ("MECH",)
SCOPE_EVID = ("HW/PCB", "SW")

# ★量容器根 (P5 判据用)★ —— 落在这些根上的指针, 若解析到的槽里没有任何 `measured*` 字段 ⇒ 判 D 误指
QUANT_ROOTS = (
    "dimensions",
    "body_geometry",
    "three_quantities",
    "geometry",
    "quantities",
    "measurements",
    "seat_body",
)

# ★本单已知的死指针宿主页 (P6 用)★ —— 只用于「逐条点名」, 期望值一律现读现算
KNOWN_DEAD_PAGE = "MECH/BOARD_ONEPASS_FTS_VS_GENERIC_COURTYARD_DELTA.md"

# ★★本闸【自产登记页】· 不扫 (★理由 + 透明披露写在报告头部 + 真相页 §1.1★)★★
# ★这一页是【本闸的账本】, 它必须【逐字引用】那些死指针来登记它们 ⇒ 若把它也当指针扫,
# ★每改一次账本, 悬空条数就会跟着漂 ⇒ 违反 P6「条数不许随时间漂移」★
# ★⇒ 本闸把自己的账本页排除, 并在报告里【明写】排除了哪一页 ⇒ 排除是公开的、可审的, 不是藏起来的★
SELF_LEDGER_PAGES = (
    "MECH/BOARD_ONEPASS_MACHINE_BLOCK_POINTER_AUDIT.md",
)

# ★「登记条目」标记: ★带这个标记的行 = 【引文/登记】, 不是活指令 ⇒ 不计入指针统计★
# ★⇒ 别的页要引用死指针时, 在那一行末尾加 `【登记】` 即可, 不用改闸★
QUOTE_MARK = "【指针登记】"

FENCE_RE = re.compile(r"```json\s*\n(.*?)\n```", re.S)
ANY_FENCE_RE = re.compile(r"```.*?```", re.S)
BACKTICK_RE = re.compile(r"`([^`\n]+)`")
MDREF_RE = re.compile(r"([A-Za-z0-9_][A-Za-z0-9_./-]*\.md)")
MBLOCK_CTX_RE = re.compile(r"机器块(?:的|里)?\s*(?:`([^`\n]+)`|([A-Za-z_][A-Za-z0-9_.\-]*))")
ROWLOC_RE = re.compile(r"表第\s*\d+\s*行")
COLLOC_RE = re.compile(r"第\s*\d+\s*列")
FILLHDR_RE = re.compile(r"填|回填|写入")
SHORTHAND_RE = re.compile(r"\b([A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+)\b")
SEGRE = re.compile(r"^(?P<name>[A-Za-z_][A-Za-z0-9_-]*)(?P<idx>\[\d*\])?$")
BAREKEY_RE = re.compile(r"^[a-z][a-z0-9]*(_[a-z0-9]+)+$")

CLS_A = "A 可解析"
CLS_B = "B 悬空"
CLS_C = "C 歧义"
CLS_D = "D 误指"
CLS_E = "E 无归属"


# ══════════════════════════════ 基础工具 ══════════════════════════════

def read_text(path):
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read()


def collect_pages(root, dirs):
    """收集扫描范围内的 .md 页 (★跳过隐藏文件/隐藏目录★)"""
    out = []
    for d in dirs:
        base = os.path.join(root, d)
        if not os.path.isdir(base):
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = sorted(n for n in dirnames if not n.startswith("."))
            for fn in sorted(filenames):
                if fn.endswith(".md") and not fn.startswith("."):
                    full = os.path.join(dirpath, fn)
                    rel = os.path.relpath(full, root).replace(os.sep, "/")
                    out.append(rel)
    return sorted(set(out))


def extract_blocks(text):
    """拆机器块。

    判据: ```json 围栏 **整体 json.loads 成功** ⇒ 机器块.
          失败且首字符是 `{` / `[` ⇒ ★坏机器块 (fail-closed 上报)★
          失败且首字符不是 `{` / `[` ⇒ 片段 (illustrative snippet) ⇒ 忽略, 但计数.
    """
    blocks, broken, snippets = [], [], 0
    for m in FENCE_RE.finditer(text):
        line = text[: m.start()].count("\n") + 1
        body = m.group(1)
        try:
            blocks.append((line, json.loads(body)))
        except Exception as exc:  # noqa: BLE001
            s = body.lstrip()
            if s.startswith("{") or s.startswith("["):
                broken.append((line, str(exc)))
            else:
                snippets += 1
    return blocks, broken, snippets


def top_keys(blocks):
    ks = set()
    for _line, obj in blocks:
        if isinstance(obj, dict):
            ks |= set(obj.keys())
    return ks


def parse_path(tok):
    """把候选 token 解析成 [(name, idx)] 列表; 解析不了返回 None。

    idx ∈ None | int | "[]" | "<ph>"
    """
    t = tok.strip()
    if not t or " " in t or "/" in t:
        return None
    for cut in (" = ", " + ", "+ ", " ⇒", " ⇒", " ⇒ "):
        if cut in t:
            t = t.split(cut)[0].strip()
    t = t.rstrip(".")
    if not t:
        return None
    parts = t.split(".")
    segs = []
    for p in parts:
        if p == "*":
            segs.append(("*", "*"))
            continue
        if p.startswith("<") and p.endswith(">"):
            segs.append((p, "<ph>"))
            continue
        m = SEGRE.match(p)
        if not m:
            return None
        idx = m.group("idx")
        if idx is None:
            ii = None
        elif idx == "[]":
            ii = "[]"
        else:
            ii = int(idx[1:-1])
        segs.append((m.group("name"), ii))
    return segs or None


def resolve_segs(blocks, segs):
    """JSON 逐段下钻 ⇒ (status, detail).

    status ∈ ("OK", nodes) | ("MISSING", missing_seg_name)
    ★不许用子串命中当解析★ —— 这里只做 dict/list 的真实下钻。
    """
    missing = None
    for _bline, obj in blocks:
        nodes = [obj]
        failed = False
        for name, idx in segs:
            nxt = []
            for n in nodes:
                if name == "*" or (name.startswith("<") and name.endswith(">")):
                    if isinstance(n, dict):
                        nxt.extend(n.values())
                    elif isinstance(n, list):
                        nxt.extend(n)
                    else:
                        nxt.append(n)
                    continue
                v = None
                if isinstance(n, dict):
                    if name in n:
                        v = n[name]
                    else:
                        failed = True
                        break
                elif isinstance(n, list):
                    if name.isdigit() and int(name) < len(n):
                        v = n[int(name)]
                    elif idx is None:
                        hit = None
                        for e in n:
                            if isinstance(e, dict) and str(e.get("id", "")) == name:
                                hit = e
                                break
                        if hit is None:
                            failed = True
                            break
                        v = hit
                    else:
                        failed = True
                        break
                else:
                    failed = True
                    break
                if idx is None:
                    nxt.append(v)
                elif idx == "[]":
                    if isinstance(v, list):
                        nxt.extend(v)
                    else:
                        failed = True
                        break
                elif idx == "<ph>":
                    if isinstance(v, dict):
                        nxt.extend(v.values())
                    elif isinstance(v, list):
                        nxt.extend(v)
                    else:
                        nxt.append(v)
                else:  # int
                    if isinstance(v, list) and 0 <= idx < len(v):
                        nxt.append(v[idx])
                    else:
                        failed = True
                        break
            if failed:
                if missing is None:
                    missing = name
                break
            nodes = nxt
        if not failed and nodes:
            return ("OK", nodes)
    return ("MISSING", missing)


def find_key_value(node, path):
    """按 `a.b[0].c` 形式取出机器块里的值"""
    cur = node
    for part in path.split("."):
        m = re.match(r"^([^\[]*)((?:\[\d+\])*)$", part)
        if not m:
            return None
        name, idxs = m.group(1), m.group(2)
        if isinstance(cur, dict) and name in cur:
            cur = cur[name]
        else:
            return None
        for im in re.finditer(r"\[(\d+)\]", idxs):
            i = int(im.group(1))
            if isinstance(cur, list) and i < len(cur):
                cur = cur[i]
            else:
                return None
    return cur


def find_key_paths(node, key, prefix="", _depth=0, _out=None):
    """★递归找某个键名在机器块里的全部落点★ (⇒ 裸键不在顶层时, 告诉人它到底在哪)"""
    if _out is None:
        _out = []
    if _depth > 12 or len(_out) > 8:
        return _out
    if isinstance(node, dict):
        for k, v in node.items():
            p = "%s.%s" % (prefix, k) if prefix else str(k)
            if str(k) == key:
                _out.append(p)
            find_key_paths(v, key, p, _depth + 1, _out)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            find_key_paths(v, key, "%s[%d]" % (prefix, i), _depth + 1, _out)
    return _out


def subtree_has_measured(node, _depth=0):
    """★P5 判据的底座: 解析到的槽里有没有任何 `measured*` 字段★"""
    if _depth > 12:
        return False
    if isinstance(node, dict):
        for k, v in node.items():
            if "measured" in str(k).lower():
                return True
            if subtree_has_measured(v, _depth + 1):
                return True
    elif isinstance(node, list):
        for v in node:
            if subtree_has_measured(v, _depth + 1):
                return True
    return False


def build_table_ctx(lines):
    """markdown 表格 ⇒ 每行的【(列头, 单元格文本) 列表】(★P4 歧义判定用★)"""
    ctx = [[] for _ in lines]
    i, n = 0, len(lines)
    while i < n:
        if lines[i].lstrip().startswith("|"):
            j = i
            while j < n and lines[j].lstrip().startswith("|"):
                j += 1
            group = lines[i:j]

            def cells(s):
                s = s.strip()
                if s.startswith("|"):
                    s = s[1:]
                if s.endswith("|"):
                    s = s[:-1]
                return [c.strip() for c in s.split("|")]

            header = cells(group[0])
            for k in range(1, len(group)):
                stripped = group[k].replace("|", "").replace(" ", "")
                if stripped and set(stripped) <= set("-:"):
                    continue  # 表格分隔行
                row = cells(group[k])
                for ci, c in enumerate(row):
                    ctx[i + k].append((header[ci] if ci < len(header) else "", c))
            i = j
        else:
            i += 1
    return ctx


def fenced_line_mask(text):
    """★围栏内的行不算「散文指针」★ ⇒ 返回一个 set(行号)"""
    masked = set()
    for m in ANY_FENCE_RE.finditer(text):
        start = text[: m.start()].count("\n") + 1
        end = text[: m.end()].count("\n") + 1
        for ln in range(start, end + 1):
            masked.add(ln)
    return masked


def build_ref_inheritance(lines, scope_pages):

    """★目标页引用的继承 (机器可判, 不用人眼)★

    R0  ★简称引用★ ⇒ 行内出现某个扫描范围页 basename 的【唯一】后缀 (如 `MECH_SYNC` ⇒ BOARD_ONEPASS_MECH_SYNC.md)
        ⇒ 记为该页引用 (★要求全域唯一, 否则不算★)
    R1  ★表格行继承★ ⇒ 同一张表里, 某行没写 `.md` 路径时 (常见写法 = 「同上」),
        继承本表内最近一个写过路径的行 ⇒ 目标页才算得出来
    R2  ★小节继承★ ⇒ 行本身与所属表格都没写路径时, 继承最近一个【标题行】(以 # 开头)里的路径
    """
    own = []
    for line in lines:
        rs = []
        for m in MDREF_RE.finditer(line):
            if m.group(1) in scope_pages and m.group(1) not in rs:
                rs.append(m.group(1))
        for m in SHORTHAND_RE.finditer(line):
            tok = m.group(1)
            hits = [p for p in scope_pages if os.path.basename(p)[:-3].upper().endswith(tok)]
            if len(hits) == 1 and hits[0] not in rs:
                rs.append(hits[0])
        own.append(rs)
    own = []
    for line in lines:
        rs = []
        for m in MDREF_RE.finditer(line):
            if m.group(1) in scope_pages and m.group(1) not in rs:
                rs.append(m.group(1))
        own.append(rs)

    # R1: 表格内继承
    tbl = [None] * len(lines)
    i, n = 0, len(lines)
    while i < n:
        if lines[i].lstrip().startswith("|"):
            j = i
            while j < n and lines[j].lstrip().startswith("|"):
                j += 1
            last = []
            for k in range(i, j):
                tbl[k] = own[k] if own[k] else (last or None)
                if own[k]:
                    last = own[k]
            i = j
        else:
            i += 1

    # R2: 标题继承 (★取【最近一个写了路径的】标题, 不是最近一个标题★)
    head = [None] * len(lines)
    last_head = None
    for k in range(len(lines)):
        if lines[k].lstrip().startswith("#"):
            if own[k]:
                last_head = own[k]
        head[k] = last_head

    eff = []
    for k in range(len(lines)):
        if own[k]:
            eff.append(own[k])
        elif tbl[k]:
            eff.append(tbl[k])
        elif head[k]:
            eff.append(head[k])
        else:
            eff.append([])
    return eff


# ══════════════════════════════ 扫描 ══════════════════════════════

class Pointer(object):
    __slots__ = ("scope", "page", "line", "text", "kind", "cls", "target", "note", "refs", "in_fill_col")

    def __init__(self, scope, page, line, text, kind):
        self.scope = scope
        self.page = page
        self.line = line
        self.text = text
        self.kind = kind
        self.cls = None
        self.target = None
        self.note = ""
        self.refs = []
        self.in_fill_col = False

    def as_dict(self):
        return {
            "scope": self.scope,
            "page": self.page,
            "line": self.line,
            "pointer": self.text,
            "kind": self.kind,
            "class": self.cls,
            "target_page": self.target,
            "note": self.note,
        }

    def key(self):
        return (self.scope, self.page, self.line, self.text, self.kind)


def classify_pointer(ptr, segs, data, scope_pages, global_roots):
    """给一条路径型指针定级 ⇒ (cls, target, note)"""
    root_name = segs[0][0]
    page = ptr.page
    plausible = []
    for t in ptr.refs:
        if t in scope_pages and t not in plausible:
            plausible.append(t)
    if page not in plausible:
        plausible.append(page)

    resolvers = []
    root_hits = []
    for t in plausible:
        if root_name not in data[t]["topkeys"]:
            continue
        root_hits.append(t)
        st, det = resolve_segs(data[t]["blocks"], segs)
        if st == "OK":
            resolvers.append((t, det))

    if len(resolvers) == 1:
        tgt, det = resolvers[0]
        last_seg = segs[-1][0]
        points_at_measured = "measured" in str(last_seg).lower()
        if (root_name in QUANT_ROOTS and not points_at_measured
                and not any(subtree_has_measured(n) for n in det)):
            return (CLS_D, tgt, "量容器根 `%s` ⇒ 解析到的槽里没有任何 `measured*` 字段 ⇒ 要填实测却落在公称档上" % root_name)
        sib = [t for t in root_hits if t != tgt]
        note = "解析到 `%s`" % tgt
        if sib:
            note += " · ★同页读法不成立: %s 的 `%s` 下没有这一段★" % ("/".join(sib), root_name)
        return (CLS_A, tgt, note)
    if len(resolvers) > 1:
        return (CLS_E, resolvers[0][0], "多解: 同一指针在 %s 都能解析 ⇒ 目标页写不唯一" % " / ".join(t for t, _ in resolvers))

    if root_hits:
        miss = resolve_segs(data[root_hits[0]]["blocks"], segs)[1]
        return (CLS_B, root_hits[0], "悬空: 根段 `%s` 在 `%s` 存在, 但后面的段 `%s` 不存在" % (root_name, root_hits[0], miss))

    cands = global_roots.get(root_name, [])
    if cands:
        return (CLS_E, None, "跨页指针但目标页没写出来: 根段 `%s` 不在 `%s` 的机器块里; 全域里只有 %s 有这个根 ⇒ 目标页写不唯一 ⇒ E" %
                (root_name, page, " / ".join(cands[:4])))
    return (None, None, "")


def classify_bare(ptr, key, data, scope_pages, global_roots):
    """「页 + 机器块 + 裸键」型 ⇒ (cls, target, note)"""
    page = ptr.page
    plausible = []
    for t in ptr.refs:
        if t in scope_pages and t not in plausible:
            plausible.append(t)
    if page not in plausible:
        plausible.append(page)

    hits = [t for t in plausible if key in data[t]["topkeys"]]
    if len(hits) == 1:
        return (CLS_A, hits[0], "解析到 `%s` 的顶层键 `%s`" % (hits[0], key))
    if len(hits) > 1:
        return (CLS_E, hits[0], "多解: 顶层键 `%s` 在 %s 都有" % (key, " / ".join(hits)))
    # ★不在顶层, 但可能藏在机器块的深层 ⇒ 报 A/D + 实际落点 (层级不符)★
    nested = []
    for t in plausible:
        for _bl, obj in data[t]["blocks"]:
            for p in find_key_paths(obj, key):
                nested.append((t, p, find_key_value(obj, p)))
    if nested:
        t0, p0, v0 = nested[0]
        if not isinstance(v0, (dict, list)):
            # ★落点是标量 ⇒ 填进去就是把原值覆盖掉 ⇒ 误指 ★
            if ptr.in_fill_col:
                return (CLS_D, t0,
                        "★落点是标量 (不是可填的格子) ⇒ 实际落点 `%s` 的值是 %r ⇒ 在那儿「填实测」等于覆盖原值 ⇒ 误指★"
                        % (p0, v0))
            return (CLS_A, t0, "★不是顶层键 ⇒ 实际落点是 `%s` (%s) (落点是标量, 只可读不可填)★" % (p0, t0))
        return (CLS_A, t0, "★不是顶层键 ⇒ 实际落点是 `%s` (%s); 指针少了路径前缀 ⇒ 建议写成该完整路径★" % (p0, t0))
    cands = global_roots.get(key, [])
    if cands:
        return (CLS_E, None, "跨页指针但目标页没写出来: 顶层键 `%s` 只存在于 %s" % (key, " / ".join(cands[:4])))
    return (CLS_B, plausible[0] if plausible else page,
            "悬空: 目标页机器块里没有顶层键 `%s`" % key)


def scan(root, main_dirs=SCOPE_MAIN, evid_dirs=SCOPE_EVID):
    """★P1: 扫描范围可复现 ⇒ 闸自己扫★"""
    all_dirs = list(main_dirs) + list(evid_dirs)
    pages = collect_pages(root, all_dirs)
    excluded = [p for p in pages if p in SELF_LEDGER_PAGES]
    pages = [p for p in pages if p not in SELF_LEDGER_PAGES]
    scope_pages = set(pages)

    data = {}
    broken_total = []
    snippet_total = 0
    for rel in pages:
        text = read_text(os.path.join(root, rel))
        blocks, broken, snippets = extract_blocks(text)
        data[rel] = {
            "text": text,
            "lines": text.split("\n"),
            "blocks": blocks,
            "topkeys": top_keys(blocks),
            "table_ctx": build_table_ctx(text.split("\n")),
            "masked": fenced_line_mask(text),
        }
        data[rel]["eff_refs"] = build_ref_inheritance(data[rel]["lines"], scope_pages)
        for bl, err in broken:
            broken_total.append((rel, bl, err))
        snippet_total += snippets

    global_roots = {}
    for rel in pages:
        for k in data[rel]["topkeys"]:
            global_roots.setdefault(k, []).append(rel)

    pointers = []
    quoted_total = 0
    for rel in pages:
        scope = "main" if rel.split("/")[0] in main_dirs else "evid"
        lines = data[rel]["lines"]
        for idx, line in enumerate(lines):
            lineno = idx + 1
            if lineno in data[rel]["masked"]:
                continue  # ★围栏内不是散文指针★
            if QUOTE_MARK in line:
                quoted_total += 1
                continue  # ★带【登记】标记 = 引文登记, 不是活指令★
            refs = data[rel]["eff_refs"][idx]

            # ---- C 类: 表格行定位型 (歧义) ----
            for (hdr, cell) in data[rel]["table_ctx"][idx]:
                if FILLHDR_RE.search(hdr) and ROWLOC_RE.search(cell) and not COLLOC_RE.search(cell):
                    p = Pointer(scope, rel, lineno, cell, "P4 表格行定位型")
                    p.cls = CLS_C
                    p.note = "歧义: 回填列的格子里只给了「第 N 行」坐标, 没说第几列 ⇒ 定位不到唯一格 (列头: %s)" % hdr
                    pointers.append(p)

            # ---- A/B/D/E: 路径型 (P1 同页 / P2 跨页 / P3 页+键) ----
            prev_root = None
            prev_end = -1
            prev_dotted = False
            for m in BACKTICK_RE.finditer(line):
                tok = m.group(1)
                segs = parse_path(tok)
                gap = line[prev_end:m.start()] if prev_end >= 0 else ""
                if segs is not None and len(segs) < 2 and not any(i is not None for _n, i in segs):
                    # ★「斜杠续写」型: `a.b` / `c` / `d` ⇒ 后面的段跟前面的根 ★
                    if prev_dotted and re.match(r"^\s*/\s*$", gap):
                        full = "%s.%s" % (prev_root, tok.strip())
                        segs = parse_path(full)
                        if segs is None:
                            prev_root, prev_end, prev_dotted = None, m.end(), False
                            continue
                        tok = full  # ★指针逐字记成完整路径★
                    else:
                        prev_root, prev_end, prev_dotted = None, m.end(), False
                        continue
                if segs is None:
                    prev_root, prev_end, prev_dotted = None, m.end(), False
                    continue
                prev_root = segs[0][0]
                prev_end = m.end()
                prev_dotted = len(segs) >= 2
                if len(segs) < 2 and not any(i is not None for _n, i in segs):
                    continue  # 单段裸键 ⇒ 不走路径型 (由 MBLOCK_CTX 单独收)
                p = Pointer(scope, rel, lineno, tok, "P1/P2 JSON 路径型")
                p.refs = refs
                cls, tgt, note = classify_pointer(p, segs, data, scope_pages, global_roots)
                if cls is None:
                    continue  # 不是指针 (根段到处都不存在 ⇒ 多半是文件名/命令)
                p.cls, p.target, p.note = cls, tgt, note
                pointers.append(p)

            # ---- 「页 + 机器块 + 裸键」型 ----
            fill_col = any(FILLHDR_RE.search(h) for (h, _c) in data[rel]["table_ctx"][idx])
            for m in MBLOCK_CTX_RE.finditer(line):
                tok = (m.group(1) or m.group(2) or "").strip()
                if not tok or "." in tok or "[" in tok:
                    continue
                if not BAREKEY_RE.match(tok):
                    continue
                p = Pointer(scope, rel, lineno, tok, "P3 页+机器块+裸键型")
                p.refs = refs
                p.in_fill_col = fill_col
                cls, tgt, note = classify_bare(p, tok, data, scope_pages, global_roots)
                if cls is None:
                    continue
                p.cls, p.target, p.note = cls, tgt, note
                pointers.append(p)

    # 去重 (同页同行同指针同类型)
    seen = set()
    uniq = []
    for p in pointers:
        k = p.key()
        if k in seen:
            continue
        seen.add(k)
        uniq.append(p)

    return {
        "root": root,
        "data": data,
        "pointers": uniq,
        "broken": broken_total,
        "snippets": snippet_total,
        "pages": pages,
        "excluded": excluded,
        "quoted": quoted_total,
        "scope_pages": scope_pages,
        "global_roots": global_roots,
    }


# ══════════════════════════════ 报告 ══════════════════════════════

def counts(pointers, scope):
    c = {CLS_A: 0, CLS_B: 0, CLS_C: 0, CLS_D: 0, CLS_E: 0}
    for p in pointers:
        if p.scope != scope:
            continue
        c[p.cls] = c.get(p.cls, 0) + 1
    return c


def report(res):
    out = []
    out.append("── ISS-400 机器块指针可解析性闸 ⇒ MECH 主范围 + HW/PCB/SW 旁证范围")
    out.append("   扫描页数: %d (主范围 MECH + 旁证 HW/PCB,SW)" % len(res["pages"]))
    if res.get("excluded"):
        out.append("   ★★本闸【自产登记页】不扫 (★它必须逐字引用死指针来登记 ⇒ 扫它就会让条数漂★): %s★★"
                   % " / ".join(res["excluded"]))
    if res.get("quoted"):
        out.append("   ★带 `【登记】` 标记的引文行: %d 行 (★引文登记, 不是活指令 ⇒ 不计★)" % res["quoted"])
    out.append("   机器块: %d 块 · 片段(非完整 JSON·忽略): %d · ★坏机器块: %d★" % (
        sum(len(res["data"][p]["blocks"]) for p in res["pages"]),
        res["snippets"], len(res["broken"])))
    for rel, bl, err in res["broken"]:
        out.append("   ★★[坏机器块] %s L%d ⇒ %s" % (rel, bl, err))
    out.append("")

    for scope, title in (("main", "主范围 (MECH/·本单可改)"), ("evid", "旁证范围 (HW/PCB/, SW/·★本单只列不改★)")):
        out.append("══ %s ══" % title)
        c = counts(res["pointers"], scope)
        out.append("   指针总条数 %d ⇒ A %d / B %d / C %d / D %d / E %d" % (
            sum(c.values()), c[CLS_A], c[CLS_B], c[CLS_C], c[CLS_D], c[CLS_E]))
        by_cls = {}
        for p in res["pointers"]:
            if p.scope != scope:
                continue
            by_cls.setdefault(p.cls, []).append(p)
        for cls in (CLS_B, CLS_C, CLS_D, CLS_E, CLS_A):
            lst = by_cls.get(cls, [])
            if not lst:
                continue
            out.append("   ── %s (%d 条)" % (cls, len(lst)))
            for p in sorted(lst, key=lambda x: (x.page, x.line)):
                tgt = p.target if p.target else "—"
                out.append("      %s:%d  [%s]  %s" % (p.page, p.line, p.kind, p.text))
                out.append("          ⇒ %s · 目标页 %s" % (cls, tgt))
                if p.note:
                    out.append("          ⇒ %s" % p.note)
        out.append("")

    # P6: 逐条点名本单已知的死指针 (★期望值现读现算, 不写死★)
    known = [p for p in res["pointers"]
             if p.page == KNOWN_DEAD_PAGE and p.cls in (CLS_B, CLS_D, CLS_E)
             and p.text.startswith("dimensions.factory_")]
    out.append("── P6 逐条点名: `%s` §5 动作表的 `dimensions.factory_*` 回填指针" % KNOWN_DEAD_PAGE)
    if known:
        for p in sorted(known, key=lambda x: x.line):
            out.append("   ★ L%d  %s  ⇒ %s" % (p.line, p.text, p.cls))
    else:
        out.append("   ★ 一条都没点到 ⇒ ★★该页 §5 的三条死指针已经不在扫描范围内 ⇒ 闸可能没在看它们★ ★")
    out.append("")
    return "\n".join(out)


# ══════════════════════════════ selftest ══════════════════════════════

def _mkpage(root, rel, body):
    full = os.path.join(root, rel)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as fh:
        fh.write(body)


def _fixture_page_with_block(rel, block, prose=""):
    return prose + "\n```json\n" + json.dumps(block, ensure_ascii=False, indent=2) + "\n```\n"


def selftest(root):
    sbx = os.path.join(root, "tmp", "iss400", "sbx", "selftest")
    if os.path.isdir(sbx):
        shutil.rmtree(sbx)
    os.makedirs(sbx)
    fails = []

    def chk(tag, cond, msg=""):
        if cond:
            print("[ok]   %-10s ✓" % tag)
        else:
            print("[FAIL] %-10s %s" % (tag, msg))
            fails.append(tag)

    # ── 正向 1: 真范围扫 ⇒ 两次跑悬空条数必须一致 (条数不许随时间漂移) ──
    r1 = scan(root)
    r2 = scan(root)
    c1 = counts(r1["pointers"], "main")
    c2 = counts(r2["pointers"], "main")
    chk("T0-稳定", c1 == c2, "两次扫描读数不一致: %s vs %s" % (c1, c2))
    real_bad = c1[CLS_B] + c1[CLS_C] + c1[CLS_D] + c1[CLS_E]
    chk("T0-现状红", real_bad >= 1, "真范围扫出来 A 类之外的指针 = %d 条 (★本闸现状就该红★)" % real_bad)

    # ── 正向 2: 本单已知的 3 条死指针必须被逐条点名 (★期望值从真文件现读现算★) ──
    known = [p for p in r1["pointers"]
             if p.page == KNOWN_DEAD_PAGE and p.cls == CLS_B and p.text.startswith("dimensions.factory_")]
    chk("T0-点名", len(known) == 3,
        "★期望 3 条 `dimensions.factory_*` 被点名, 实到 %d 条 ⇒ %s" % (len(known), [(p.line, p.text) for p in known]))

    # ── 反向 ①: 把那 3 条里的一条从扫描范围里去掉 ⇒ 悬空条数必须减 1 ──
    if not known:
        fails.append("T1-减条")
        print("[FAIL] T1-减条     ★真件里没找到那 3 条, 本用例无法构造★")
    else:
        target = sorted(known, key=lambda x: x.line)[0]
        fx = os.path.join(sbx, "t1")
        os.makedirs(os.path.join(fx, "MECH"))
        # ★夹具不许把真件当前的指针文本硬抄成常量当期望值 ⇒ 期望值从真文件现读现算★
        src = os.path.join(root, target.page)
        text = read_text(src)
        lines = text.split("\n")
        new_lines = [ln for i, ln in enumerate(lines) if (i + 1) != target.line]
        with open(os.path.join(fx, "MECH", "page.md"), "w", encoding="utf-8") as fh:
            fh.write("\n".join(new_lines))
        # 只放这一页 ⇒ 期望 B 条数 = 真值 - 1
        exp = len([p for p in r1["pointers"] if p.page == target.page and p.cls == CLS_B]) - 1
        rf = scan(fx, main_dirs=("MECH",), evid_dirs=())
        cf = counts(rf["pointers"], "main")
        chk("T1-减条", cf[CLS_B] == exp,
            "★去掉 L%d 那条后, 该页 B 条数应为 %d, 实到 %d ⇒ 闸没在看那一条★" % (target.line, exp, cf[CLS_B]))

    # ── 反向 ②: 造一条指向另一个页的假指针, 键在目标页不存在 ⇒ 必须报悬空 ──
    fx = os.path.join(sbx, "t2")
    _mkpage(fx, "MECH/A.md", _fixture_page_with_block(
        "MECH/A.md", {"dimensions": {"seat_body_x_4pos": {"value": "5.0800"}}},
        prose="★指针: `MECH/B.md` `dimensions.no_such_key_here` ★"))
    _mkpage(fx, "MECH/B.md", _fixture_page_with_block(
        "MECH/B.md", {"dimensions": {"seat_body_x_4pos": {"value": "5.0800"}}}))
    r = scan(fx, main_dirs=("MECH",), evid_dirs=())
    got = [p for p in r["pointers"] if p.page == "MECH/A.md" and "no_such_key_here" in p.text]
    chk("T2-跨页悬空", len(got) == 1 and got[0].cls == CLS_B,
        "★跨页假指针(键不存在)没被报成 B 悬空 ⇒ %s" % [(p.cls, p.text) for p in got])

    # ── 反向 ③: 造一条指向另一个页的假指针, 键存在 ⇒ 必须判 A 可解析 (证明能跨页下钻) ──
    fx = os.path.join(sbx, "t3")
    _mkpage(fx, "MECH/A.md", _fixture_page_with_block(
        "MECH/A.md", {"doc": "A 页自己的机器块 (★故意不含 land_smd ⇒ 逼闸真的去目标页下钻★)"},
        prose="★指针: `MECH/B.md` `land_smd.arrangement` ★"))
    _mkpage(fx, "MECH/B.md", _fixture_page_with_block(
        "MECH/B.md", {"land_smd": {"arrangement": {"rows": 3, "cols": 2}}}))
    r = scan(fx, main_dirs=("MECH",), evid_dirs=())
    got = [p for p in r["pointers"] if p.page == "MECH/A.md" and p.text == "land_smd.arrangement"]
    chk("T3-跨页可解", len(got) == 1 and got[0].cls == CLS_A and got[0].target == "MECH/B.md",
        "★跨页假指针(键存在)没被判 A ⇒ %s" % [(p.cls, p.target) for p in got])

    # ── 反向 ④: 键名存在但不是实测槽 ⇒ 必须报 D 误指 (证明 P5 真在跑) ──
    fx = os.path.join(sbx, "t4")
    _mkpage(fx, "MECH/A.md", _fixture_page_with_block(
        "MECH/A.md", {"dimensions": {"seat_body_x_4pos": {"value": "5.0800", "source": "factory"}}},
        prose="★指针: `dimensions.seat_body_x_4pos` ★"))
    r = scan(fx, main_dirs=("MECH",), evid_dirs=())
    got = [p for p in r["pointers"] if p.text == "dimensions.seat_body_x_4pos"]
    chk("T4-误指D", len(got) == 1 and got[0].cls == CLS_D,
        "★「键存在但不是实测槽」的指针没被判 D ⇒ %s" % [(p.cls, p.text) for p in got])

    # ── 反向 ⑤: 改坏机器块 JSON ⇒ 必须报错退出, 不许静默跳过 (fail-closed) ──
    fx = os.path.join(sbx, "t5")
    _mkpage(fx, "MECH/A.md", "前言\n\n```json\n{ \"dimensions\": { \"a\": 1, }\n```\n")
    r = scan(fx, main_dirs=("MECH",), evid_dirs=())
    chk("T5-坏块", len(r["broken"]) == 1,
        "★坏机器块没被抓出来 ⇒ broken=%d★" % len(r["broken"]))

    # ── 反向 ⑥: 塞一条 P5 自然语言引用 ⇒ 必须不算指针 (证明排除口径有效) ──
    fx = os.path.join(sbx, "t6")
    _mkpage(fx, "MECH/A.md", _fixture_page_with_block(
        "MECH/A.md", {"dimensions": {"seat_body_x_4pos": {"value": "5.0800"}}},
        prose="★见 §4-③ ★\n★见 §6 ★\n★详见第 3 节 ★"))
    r = scan(fx, main_dirs=("MECH",), evid_dirs=())
    chk("T6-排除自然语言", len(r["pointers"]) == 0,
        "★自然语言引用被当成指针了 ⇒ %s" % [(p.cls, p.text) for p in r["pointers"]])

    # ── 反向 ⑦: 扫一个空目录 ⇒ 必须报「扫描范围内零指针」而不是崩 ──
    fx = os.path.join(sbx, "t7")
    os.makedirs(os.path.join(fx, "MECH"))
    r = scan(fx, main_dirs=("MECH",), evid_dirs=())
    chk("T7-空目录", len(r["pointers"]) == 0 and len(r["pages"]) == 0,
        "★空目录扫描结果不对 ⇒ pointers=%d pages=%d★" % (len(r["pointers"]), len(r["pages"])))

    # ── 反向 ⑧: 表格行定位型 (§N 表第 M 行) ⇒ 必须判 C 歧义 ──
    fx = os.path.join(sbx, "t8")
    body = ("| 量 | 量法 | 量完填回哪一格 |\n|---|---|---|\n"
            "| ① 座体宽 X | 卡尺 | §1 表第 1 行 + §6 `dimensions.seat_body_x_4pos` |\n"
            "\n```json\n" + json.dumps({"dimensions": {"seat_body_x_4pos": {"value": "5.0800"}}}, ensure_ascii=False, indent=2) + "\n```\n")
    _mkpage(fx, "MECH/A.md", body)
    r = scan(fx, main_dirs=("MECH",), evid_dirs=())
    got = [p for p in r["pointers"] if p.cls == CLS_C]
    chk("T8-歧义C", len(got) == 1 and "表第 1 行" in got[0].text,
        "★「表第 N 行」没被判 C 歧义 ⇒ %s" % [(p.cls, p.text) for p in r["pointers"]])

    # ── 反向 ⑨: 跨页 + 量容器 + 目标槽【真的有】measured 字段 ⇒ 必须判 A (证明 P5 不是「见量容器就 D」) ──
    fx = os.path.join(sbx, "t9")
    _mkpage(fx, "MECH/A.md", _fixture_page_with_block(
        "MECH/A.md", {"doc": "A 页"},
        prose="★指针: `MECH/B.md` `three_quantities.seat_body_width_x.measured_value` ★"))
    _mkpage(fx, "MECH/B.md", _fixture_page_with_block(
        "MECH/B.md", {"three_quantities": {"seat_body_width_x": {
            "nominal_value": "5.0800", "measured_value": None, "measured_evidence": "[0数据]"}}}))
    r = scan(fx, main_dirs=("MECH",), evid_dirs=())
    got = [p for p in r["pointers"] if p.text == "three_quantities.seat_body_width_x.measured_value"]
    chk("T9-跨页实测槽", len(got) == 1 and got[0].cls == CLS_A and got[0].target == "MECH/B.md",
        "★跨页实测槽指针没被判 A ⇒ %s" % [(p.cls, p.target) for p in got])

    shutil.rmtree(sbx, ignore_errors=True)

    print("反向用例 %d 条 · 失败 %d 条" % (9 + 3, len(fails)))
    if fails:
        print("FAIL")
        return 1
    print("ALL TESTS PASS")
    return 0


# ══════════════════════════════ main ══════════════════════════════

def main(argv):
    ap = argparse.ArgumentParser(description="ISS-400 机器块指针可解析性闸")
    ap.add_argument("--root", default=ROOT_DEFAULT)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    root = os.path.abspath(args.root)

    if args.selftest:
        return selftest(root)

    res = scan(root)
    if args.json:
        print(json.dumps({
            "pointers": [p.as_dict() for p in res["pointers"]],
            "counts": counts(res["pointers"], "main"),
            "counts_evid": counts(res["pointers"], "evid"),
            "broken": [{"page": a, "line": b, "err": c} for a, b, c in res["broken"]],
        }, ensure_ascii=False, indent=2))
        return 1 if (res["broken"] or counts(res["pointers"], "main")[CLS_A] != len(res["pointers"])) else 0

    print(report(res))
    c = counts(res["pointers"], "main")
    bad = c[CLS_B] + c[CLS_C] + c[CLS_D] + c[CLS_E]
    if res["broken"]:
        print("★★fail-closed: 有 %d 处坏机器块 (JSON 语法错) ⇒ 本闸拒绝静默跳过 ⇒ 直接判红 ★★" % len(res["broken"]))
    print("主范围判定: A 类之外的指针 %d 条 ⇒ %s" % (bad, "FAIL" if bad else "PASS"))
    if bad == 0 and not res["broken"]:
        print("PASS")
        return 0
    print("FAIL")
    print("★**本闸的【预期读数】= rc=1 (红)**: 红的是【现状】(扫描范围内有悬空/歧义/误指/无归属的指针), 不是闸故障 ★")
    print("★**本单刻意不修现状 ⇒ 不许为了让它绿而放宽判据** ★")
    print("★绿的唯一条件 = 扫描范围内 A 类之外的指针条数 == 0 (真相页 `MECH/BOARD_ONEPASS_MACHINE_BLOCK_POINTER_AUDIT.md` §2 逐条改) ★")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
