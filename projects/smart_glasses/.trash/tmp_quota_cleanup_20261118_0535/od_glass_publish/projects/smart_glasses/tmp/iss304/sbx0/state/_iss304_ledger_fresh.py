#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-304 · `state_baseline` 登记表的【台账口径 `fresh` 值】解析器 (★路 B·永不再漂★)

=====================================================================
★**它解决什么 (★ISS-304 · hw-lead · 2026-11-18★)** ★★:

    ★**2026-11-18 00:21 ISS-302 又合法落表一次 ⇒ 网表/脚表/BOM 三件的 md5 变了** ★
    ⇒ ★两份页面里那 4 条台账口径登记 (`W10_MD5_NETLIST` / `W10B_MD5_PINS` /
      `W10C_MD5_BOM` / `C07_B26_MD5_LEDGER`) 的 `fresh` 格还停在 ISS-283 那一跳** ★
    ⇒ ★**闸 `HW/check_workpack_state_values.py` 的 V4 当场红** (★「订正句里的现值没跟上盘面」★) ★

★**为什么不能只把那 4 格改成新 md5 (★路 A 的代价★)** ★:
    ★**下次落表还会漂一遍** ⇒ 每落一次表就要人手工改一遍页面 ⇒ 迟早漏 ⇒ 闸红 ⇒ 板那一趟不许开工★ ★
    ⇒ ★**本模块 = 把「取值来源」从【写死的数字】换成【落表台账现读】 (★换来源·不是换取值★)★ ★★

★**三条铁律 (★破了就是不合格★)** ★★:
    ① ★**只改 `fresh` 那一格里的 32 位十六进制串** ★ ⇒ ★`anchor` / `correction_anchor` /
       `probe` / `probe_regex` / `expect` / `expect_target` / `expect_mode` / `category` /
       `doc` / `note` 一个字都不许动★ ★
    ② ★**fail-closed** ★ ⇒ ★台账读不到 / 链头不唯一 / 链断 / 链头无单号 / 登记行四项不齐
       ⇒ ★**抛 `LedgerResolveError` ⇒ 上层拒写页 (★不许静默回退到硬基线★)★** ★
    ③ ★**改完必须逐字节可复现** ★ ⇒ ★原 JSON 块必须能被 `json.dumps(ensure_ascii=False,
       indent=2)` 逐字节还原 ⇒ 否则说明它不是那套序列化器的产物 ⇒ ★拒改 (★不许顺手重排格式★)★ ★

★**用法** ★:
    from _iss304_ledger_fresh import resolve_registry_json, resolve_state_block_text
    new_json, changes = resolve_registry_json(json_text, proj)
    new_text, changes = resolve_state_block_text(page_text, proj)
"""

from __future__ import annotations

import importlib.util
import json
import os
import re

# ★一个 32 位小写十六进制串 (★前后不能再接十六进制字符·免得 `37f62ac3…` 里切出半截★) ★
HEX32_RE = re.compile(r"(?<![0-9a-f])[0-9a-f]{32}(?![0-9a-f])")

# ★文档里的 ```json … ``` 块 (★与闸 `HW/check_workpack_state_values.py` 的 `find_state_block` 同口径★) ★
JSON_BLOCK_RE = re.compile(r"```json\s*\n(\{.*?\n\})\s*\n```", re.S)

# ★台账现值占位符: `«LEDGER_MD5:HW/netlist_v1.csv»` ⇒ 解析成台账登记的 md5 ★
#   ★**为什么要有它**: ★闸 V3 要求 `fresh` 原句【逐字】出现在文档正文里 (★不在登记表里★) ★
#   ⇒ ★正文里那几句现值也得跟着台账走 ⇒ 用占位符 ⇒ 落表一次不必人改正文★ ★
PLACEHOLDER_RE = re.compile(r"«LEDGER_MD5:([^»]+)»")


class LedgerResolveError(RuntimeError):
    """★fail-closed: 取不到台账现值 / 块结构认不出 ⇒ 抛这个 ⇒ 上层拒写页★"""


def load_landing_md5(proj: str):
    """★按 `proj` 显式加载 `<proj>/HW/landing_md5.py` (★不靠 sys.path·免得串到真盘★) ★

    ★**沙盒跑法** (`PREFLIGHT_PROJ` / `WORKPACKET_PROJ` 指向沙盒根) ⇒ ★沙盒读沙盒的台账★ ★
    """
    path = os.path.join(proj, "HW", "landing_md5.py")
    if not os.path.exists(path):
        raise LedgerResolveError("★%s 不存在 ⇒ 取不到落表台账现值 (★fail-closed★)" % path)
    name = "_iss304_landing_md5_%s" % re.sub(r"\W+", "_", os.path.abspath(proj))
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise LedgerResolveError("★%s 加载不了 ⇒ 拒改 (★fail-closed★)" % path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def resolve_fresh(fresh: str, want: str, entry_id: str) -> str:
    """★把 `fresh` 句里那一个 32 位 md5 换成台账现值 (★别的字一个字不动★) ★

    ★**必须恰好一个 32 位十六进制串** ⇒ 0 个或 ≥2 个 ⇒ ★拒改 (★不许瞎猜哪个是该换的★)★ ★
    """
    hits = HEX32_RE.findall(fresh)
    if len(hits) != 1:
        raise LedgerResolveError(
            "★id=%s 的 `fresh` 句里 32 位十六进制串不是恰好 1 个 (★找到 %d 个: %s★) ⇒ 拒改 (★fail-closed★)"
            % (entry_id, len(hits), hits))
    return HEX32_RE.sub(lambda _m: want, fresh, count=1)


def resolve_registry_json(json_text: str, proj: str) -> tuple[str, list]:
    """★把 `state_baseline` JSON 块里【台账口径】条目的 `fresh` 格换成台账现值 ⇒ (新文本, 变更清单) ★

    ★**只有 `expect_mode == "ledger"` 的条目会被动** ★ (★其余 25 条写死现状值的条目一个字不动★) ★
    """
    try:
        data = json.loads(json_text)
    except Exception as e:                                       # pragma: no cover
        raise LedgerResolveError("★`state_baseline` JSON 块解析失败 ⇒ 拒改 (★fail-closed★): %s" % e)
    if not (isinstance(data, dict) and isinstance(data.get("state_baseline"), dict)):
        raise LedgerResolveError("★`state_baseline` JSON 块结构认不出 ⇒ 拒改 (★fail-closed★)")
    # ★★自证: 原文本必须能被同一套序列化器逐字节还原 ⇒ 否则不许动它 (★免得顺手把格式重排了★)★★
    canon = json.dumps(data, ensure_ascii=False, indent=2)
    if canon != json_text:
        raise LedgerResolveError(
            "★`state_baseline` JSON 块与 `json.dumps(ensure_ascii=False, indent=2)` 不逐字节一致 "
            "⇒ 拒改 (★fail-closed·不许顺手重排格式★)")
    lm = load_landing_md5(proj)
    entries = data["state_baseline"].get("entries") or []
    changes: list = []
    for e in entries:
        if e.get("expect_mode") != "ledger":
            continue
        rel = str(e.get("expect_target") or "")
        if not rel:
            raise LedgerResolveError("★id=%s 声明 `expect_mode=ledger` 却没有 `expect_target` ⇒ 拒改"
                                     % e.get("id"))
        want, issue, why = lm.registered_md5(proj, rel)
        if not want:
            raise LedgerResolveError(
                "★id=%s: 落表台账里取不到 %s 的登记 ⇒ 拒改 (★fail-closed★): %s"
                % (e.get("id"), rel, why or issue))
        old = str(e.get("fresh") or "")
        new = resolve_fresh(old, want, e.get("id"))
        if new != old:
            e["fresh"] = new
            changes.append({"id": e.get("id"), "target": rel,
                            "old": old, "new": new, "issue": issue})
    if not changes:
        return json_text, changes
    return json.dumps(data, ensure_ascii=False, indent=2), changes


def resolve_placeholders(text: str, proj: str) -> str:
    """★把正文里的 `«LEDGER_MD5:<相对路径>»` 占位符解析成台账登记的 md5 ★

    ★**fail-closed**: ★台账里取不到 ⇒ 抛 `LedgerResolveError` ⇒ 上层拒写页★ ★
    """
    if "«LEDGER_MD5:" not in text:
        return text
    lm = load_landing_md5(proj)

    def _sub(m):
        rel = m.group(1)
        want, issue, why = lm.registered_md5(proj, rel)
        if not want:
            raise LedgerResolveError(
                "★占位符 `«LEDGER_MD5:%s»` 在落表台账里取不到登记 ⇒ 拒写 (★fail-closed★): %s"
                % (rel, why or issue))
        return want

    return PLACEHOLDER_RE.sub(_sub, text)


def resolve_state_block_text(text: str, proj: str) -> tuple[str, list]:
    """★在一段文本里找第一块 `state_baseline` JSON 并解析台账现值 ⇒ (新文本, 变更清单) ★

    ★**只处理第一块** (★与闸 `find_state_block` 同口径★) ⇒ 后面若还有别的 JSON 块, 一律不动★ ★
    """
    for m in JSON_BLOCK_RE.finditer(text):
        try:
            d = json.loads(m.group(1))
        except Exception:
            continue
        if not (isinstance(d, dict) and "state_baseline" in d):
            continue
        new_json, changes = resolve_registry_json(m.group(1), proj)
        if new_json == m.group(1):
            return text, changes
        return text[:m.start(1)] + new_json + text[m.end(1):], changes
    return text, []


def read_registry_json(text: str):
    """★取第一块 `state_baseline` JSON 原文 ⇒ (json_text, 整块原文) 或 (None, None) ★"""
    for m in JSON_BLOCK_RE.finditer(text):
        try:
            d = json.loads(m.group(1))
        except Exception:
            continue
        if isinstance(d, dict) and "state_baseline" in d:
            return m.group(1), m.group(0)
    return None, None


if __name__ == "__main__":                                      # ★自证跑法 ★
    import sys
    proj = os.environ.get("PREFLIGHT_PROJ") or \
        "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
    for rel in ("state/_iss277_preflight_appendix.md",
                "HW/PCB/BOARD_ONEPASS_PREFLIGHT.md",
                "HW/PCB/BOARD_ONEPASS_WORKPACKET.md"):
        p = os.path.join(proj, rel)
        if not os.path.exists(p):
            print("★跳过 (不存在): %s" % p)
            continue
        txt = open(p, encoding="utf-8").read()
        new, ch = resolve_state_block_text(txt, proj)
        print("★%s ⇒ %d 处台账口径 fresh 要改" % (rel, len(ch)))
        for c in ch:
            print("   - %s (%s): %s ⇒ %s" % (c["id"], c["target"], c["old"], c["new"]))
        sys.stdout.flush()
