#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HW/landing_md5.py —— 落表台账的【md5 注册表】 (★落表链的唯一真源★)

=====================================================================
★**为什么要它 (★ISS-283 · ⑪ · main 2026-11-17 11:2x 实跑抓出来的病灶·一字未改★)** ★★:

    ★**落表成功 ≠ 全链绿** ⇒ 落表完必须扫一遍【所有以真源 md5 / 现状值为基线的闸与自测】★★
    而【以 md5 为基线的闸】★**每次落表都会过期**★ ⇒ ★**只把基线数字改成新值 = 下次落表又红一遍**★
    ⇒ ★**判据的【取值来源】必须变, 不是【取值】变** ★★
    ⇒ 本模块把【落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` 的 §16.2『新旧 md5 前后对照』】
       变成【机器可查的注册表】 ⇒ ★**闸去查它, 而不是写死一个数字** ★★
    ⇒ ★★**不许用 `--update-baseline` 之类「只改基线数字」的手法消红 (★那是「换取值」不是「换来源」★)**★★

★**fail-closed (★查不到 / 链头不唯一 / 链断 / 链头无单号 ⇒ 一律红★)** ★:
    ① 台账文件不存在                                       ⇒ 红
    ② 台账里【查不到落表链头】(没有『V 值拍板即落』段)      ⇒ 红
    ③ 链头【没有单号】(ISS-xxx)                            ⇒ 红
    ④ 链头【链断】(缺 §16.2 新旧 md5 前后对照表)           ⇒ 红
    ⑤ 链头【不唯一】(同一链头里有 ≥2 张 §16.2 表)           ⇒ 红
    ⑥ 该文件在【最新一条链】的 §16.2 表里【查不到】        ⇒ 红
    ⑦ 该文件的登记行【四项不齐】(文件名 / 旧 md5 / 新 md5 缺一) ⇒ 红

★**口径 (★取哪一条链★)**:
    台账里每追加一次落表就多一条链 ⇒ ★**按台账里的先后顺序, 最后一条 = 最新一次落表**★
    ⇒ ★**板 / `.kicad_pro` 不归落表链管** ⇒ 那两件的基线照旧写死 (★不许动★)★

用法:
    from landing_md5 import registered_md5, check_registered
    want, issue, why = registered_md5(root, "HW/netlist_v1.csv")
    ok, msg = check_registered(root, "HW/netlist_v1.csv", path, md5fn)
"""

from __future__ import annotations

import os
import re

LEDGER_REL = "HW/SCHEMATIC_LANDING_V1_LANDED.md"

# ★落表链的 §16.2 表 (★新旧 md5 前后对照★) 的段头 ★
_SEC162_RE = re.compile(r"^###\s+.*16\.2\s+·\s+新旧\s*md5")
# ★台账的一级段头 (★落表链的链头★) ★
_HEAD_RE = re.compile(r"^##\s+")
_ISSUE_RE = re.compile(r"ISS-\d+")
# ★§16.2 表的一行: | ★**`文件`** ★ | `旧 md5` | `新 md5` | 变了? | ★
_ROW_RE = re.compile(r"^\|\s*[^|]*`([^`]+)`[^|]*\|\s*`([^`]*)`\s*\|\s*`([^`]*)`\s*\|")
_MD5_RE = re.compile(r"^[0-9a-f]{32}$")


def ledger_path(root: str) -> str:
    """★台账路径 (★可用 `LANDING_LEDGER` 环境变量改 ⇒ 反向用例能指向沙盒副本★)"""
    return os.environ.get("LANDING_LEDGER") or os.path.join(root, LEDGER_REL)


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def ledger_chains(root: str) -> list[dict]:
    """★落表台账里的每一条【落表链】 (★按台账里的先后顺序★)

    ★**一条链 = 一个 `##` 段头到下一个 `##` 段头之间的内容** ★
    """
    p = ledger_path(root)
    if not os.path.exists(p):
        return []
    lines = _read(p).split("\n")
    heads = [i for i, l in enumerate(lines) if _HEAD_RE.match(l)]
    chains: list[dict] = []
    for i, s in enumerate(heads):
        e = heads[i + 1] if i + 1 < len(heads) else len(lines)
        block = lines[s:e]
        secs = [k for k, l in enumerate(block) if _SEC162_RE.match(l)]
        ch = {
            "head_line": s + 1,
            "head": lines[s],
            "issue": (_ISSUE_RE.search(lines[s]).group(0) if _ISSUE_RE.search(lines[s]) else ""),
            "n_sec162": len(secs),
            "rows": {},          # file → (old_md5, new_md5)
        }
        if len(secs) == 1:
            for l in block[secs[0]:]:
                m = _ROW_RE.match(l.strip())
                if m:
                    ch["rows"][m.group(1)] = (m.group(2), m.group(3))
        chains.append(ch)
    return chains


def latest_chain(root: str) -> tuple[dict | None, list[str]]:
    """★台账里【最新一条落表链】 + 【问题清单】 (★fail-closed★)"""
    problems: list[str] = []
    chains = ledger_chains(root)
    if not chains:
        return None, ["★落表台账里【查不到落表链头】(★`%s` 里没有『V 值拍板即落』段★) ⇒ 红" % LEDGER_REL]
    last = chains[-1]
    if not last["issue"]:
        problems.append("★链头 (台账 L%d) 【没有单号】⇒ 红" % last["head_line"])
    if last["n_sec162"] == 0:
        problems.append("★链头 (台账 L%d · %s) 【链断】: 缺 §16.2 新旧 md5 前后对照表 ⇒ 红"
                        % (last["head_line"], last["issue"] or "★无单号★"))
    elif last["n_sec162"] > 1:
        problems.append("★链头 (台账 L%d · %s) 【链头不唯一】: §16.2 表有 %d 张 ⇒ 取不准 ⇒ 红"
                        % (last["head_line"], last["issue"] or "★无单号★", last["n_sec162"]))
    return last, problems


def registered_md5(root: str, rel: str) -> tuple[str, str, str]:
    """★台账登记的 md5 ⇒ (md5, 落表单号, 为什么查不到) ★

    ★**md5 为空 ⇒ 第三段说明为什么查不到 (★fail-closed·不许猜★)** ★
    """
    chain, problems = latest_chain(root)
    if chain is None or problems:
        return "", "", " / ".join(problems)
    row = chain["rows"].get(rel)
    if row is None:
        return "", chain["issue"], ("★落表台账里【查不到 %s 的登记】(★最新链 = 台账 L%d · %s★) ⇒ 红"
                                    % (rel, chain["head_line"], chain["issue"] or "★无单号★"))
    old_md5, new_md5 = row
    miss = []
    if not old_md5 or not _MD5_RE.match(old_md5):
        miss.append("旧 md5")
    if not new_md5 or not _MD5_RE.match(new_md5):
        miss.append("新 md5")
    if miss:
        return "", chain["issue"], ("★落表台账里 %s 的登记【四项不齐】(★缺 %s★) ⇒ 红"
                                    % (rel, " / ".join(miss)))
    return new_md5, chain["issue"], ""


def check_registered(root: str, rel: str, path: str, md5fn) -> tuple[bool, str]:
    """★盘上 md5 == 台账登记的 md5 ⇒ 绿 ⇒ (绿?, 说明) ★"""
    want, issue, why = registered_md5(root, rel)
    if not want:
        return False, why
    if not os.path.exists(path):
        return False, "%s 不存在: %s" % (rel, path)
    got = md5fn(path)
    chain, _p = latest_chain(root)
    head = ("·台账 L%d·§16.2" % chain["head_line"]) if chain else ""
    if got == want:
        return True, ("%s md5 == 落表台账登记 %s (★落表单号 %s%s★) ⇒ 未被绕过改动"
                      % (rel, want, issue, head))
    return False, ("%s md5 = %s ≠ 落表台账登记 %s (★落表单号 %s%s★) ⇒ 落表了但台账没登记 / 被绕过改动"
                   % (rel, got, want, issue, head))
