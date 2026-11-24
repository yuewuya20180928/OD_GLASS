#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HW/check_hw_external_dep_closed.py —— HW 域「外部依赖自查收口」机器闸 (ISS-401)

======================================================================
★**这个闸是干什么的** ★
HW 域历史上是三个总工里【唯一没做外部依赖自查收口】的域:
  · SW 域  → ISS-270 (5 条) + ISS-357 (needs 144 条)  已 verified
  · MECH 域 → ISS-313 (needs 184 条 + 16 条外部依赖)   已 verified
  · HW 域  → ISS-401 (本单) ← 就是本闸的由来

★**判定口径 (与 SW 域 ISS-270 同一把尺)** ★
  「外部依赖」= 只有外部方能回答、而本仓库 / 公开资料 / 本机实跑都回答不了的问题。
  凡本仓库已有结论、公开官网已有、或本机能实跑出来的 ⇒ 一律不是外部依赖。
  ⇒ 于是: 「还挂着等原厂」本身就是要被机器拦住的状态。

★**5 条判据 (D1..D5)** ★
  D1  HW 域 needs_from 里不许再有 waiting_on ∈ {vendor, jbd}
  D2  HW 域 needs_from 里不许再有 to      ∈ {vendor, jbd}
  D3  网表 tbd 列的待清行 + evidence=[待原厂] 行 必须 100% 被真相页的收口登记块覆盖
      (含 5 个子判据: 13 个 TBD 标签全覆盖 / 每标签声明行数 == 实测行数 /
       [待原厂] 行必须落在已覆盖标签内 / 8 条外部 needs 全登记 / 7 条 blocker 全登记)
  D4  每条登记条目必须同时有【证据等级】和【降级方案 + 结论】
  D5  每条登记条目必须写【还卡不卡板那一趟】(卡/不卡/条件卡) + 判据出处

★**运行契约** ★
  裸跑       python3 HW/check_hw_external_dep_closed.py
             ★**rc=1 是【预期】** —— 红的是现状 (还有条目挂着等外部 / 真相页还没覆盖),
             不是闸故障。交卷时必须写明「红的是现状还是闸故障」。
  自测       python3 HW/check_hw_external_dep_closed.py --selftest
             ★**rc=0 · 末行必须打 ALL TESTS PASS** ★
             (正向 ≥1 + 反向 ≥6: 每个判据至少一条反向用例 + 伪造合规样例必须转绿)

★**这个闸【不许】做的事 (硬边界)** ★
  · 不许判 md5 (板 md5 由 HW/check_onepass_commit_order.py 管)
  · 不许改任何既有闸的阈值
  · 不许把「红」当成「闸坏了」
  · 不许挂进 state/gate_check.py / state/daily_check.py (挂不挂 = main 的地界)

★**只读不写**: 本闸只读 3 个文件 (分片 / 网表 / 真相页), 一个字节都不写。
======================================================================
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
FRAG = os.path.join(PROJ, "state", "fragments", "hw.yaml")
NETLIST = os.path.join(PROJ, "HW", "netlist_v1.csv")
TRUTH = os.path.join(PROJ, "HW", "HW_EXTERNAL_DEPENDENCY_SELFCHECK_CLOSURE.md")

EXTERNAL = ("vendor", "jbd")
EVIDENCE_TAGS = ("[官网]", "[实测]", "[媒体]", "[推算]", "[0数据]")
BOARD_STATES = ("不卡", "卡", "条件卡")
TBD_LABELS = tuple("TBD-%02d" % i for i in range(1, 14))
PEND_TAG = "[待原厂]"

AGENT = "hw-lead"


# ----------------------------------------------------------------------
# 读取 (只读)
# ----------------------------------------------------------------------
def load_needs(path=FRAG):
    """读 state/fragments/hw.yaml 的 needs_from 段。"""
    import yaml  # 局部 import: 便于 --selftest 用合成 fixture
    with open(path, encoding="utf-8") as f:
        d = yaml.safe_load(f)
    if not isinstance(d, dict):
        return [], []
    return list(d.get("needs_from") or []), list(d.get("blockers") or [])


def load_netlist_rows(path=NETLIST):
    """读网表 CSV → 行字典列表。"""
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_registry(path=TRUTH):
    """从真相页里抠出 ```json 围栏块 (含 entries 的那个)。"""
    with open(path, encoding="utf-8", errors="ignore") as f:
        text = f.read()
    best = None
    for m in re.finditer(r"```json\s*\n(.*?)```", text, re.S):
        try:
            obj = json.loads(m.group(1))
        except Exception:
            continue
        if isinstance(obj, dict) and isinstance(obj.get("entries"), list):
            best = obj
    if best is None:
        raise SystemExit("[gate] X 真相页里找不到含 entries 的 ```json 登记块: %s" % path)
    return best


def tbd_of(row):
    return (row.get("tbd") or "").strip()


def evidence_of(row):
    return (row.get("evidence") or "").strip()


# ----------------------------------------------------------------------
# 核心判定 (纯函数: 输入 → 判据结果) —— --selftest 用它跑合成 fixture
# ----------------------------------------------------------------------
def evaluate(needs, blockers, netlist_rows, registry):
    """⇒ {判据代号: {"ok": bool, "detail": str, "fails": [str, ...]}}"""
    entries = list(registry.get("entries") or [])
    res = {}

    def add(code, ok, detail, fails=None):
        res[code] = {"ok": bool(ok), "detail": detail, "fails": list(fails or [])}

    # ---------- D1: waiting_on 外部 ----------
    d1 = [n for n in needs if (n.get("waiting_on") or "") in EXTERNAL]
    add(
        "D1",
        not d1,
        "HW 域 needs_from 里 waiting_on ∈ {vendor, jbd} 的条目 = %d 条 (要求 0)" % len(d1),
        ["%s (waiting_on=%s)" % (n.get("key"), n.get("waiting_on")) for n in d1],
    )

    # ---------- D2: to 外部 ----------
    d2 = [n for n in needs if (n.get("to") or "") in EXTERNAL]
    add(
        "D2",
        not d2,
        "HW 域 needs_from 里 to ∈ {vendor, jbd} 的条目 = %d 条 (要求 0)" % len(d2),
        ["%s (to=%s)" % (n.get("key"), n.get("to")) for n in d2],
    )

    # ---------- D3: 网表待清行 + [待原厂] 行 必须被登记块 100% 覆盖 ----------
    tbd_rows = [r for r in netlist_rows if tbd_of(r)]
    pend_rows = [r for r in netlist_rows if evidence_of(r) == PEND_TAG]
    total = len(tbd_rows)

    # 实测: 每个 TBD 标签的行数 / [待原厂] 行数
    rows_by_label = {}
    pend_by_label = {}
    for r in tbd_rows:
        rows_by_label.setdefault(tbd_of(r), 0)
        rows_by_label[tbd_of(r)] += 1
        if evidence_of(r) == PEND_TAG:
            pend_by_label[tbd_of(r)] = pend_by_label.get(tbd_of(r), 0) + 1
    # [待原厂] 但 tbd 列为空的行 (若有) ⇒ 也要计入分母 (保守)
    orphan_pend = [r for r in pend_rows if not tbd_of(r)]

    # 登记块侧: 按标签汇总声明行数
    declared = {}
    declared_entries = {}
    for e in entries:
        if e.get("scope") != "tbd":
            continue
        labels = e.get("tbd_labels") or []
        if not labels and e.get("ref", "").startswith("TBD-"):
            labels = [e.get("ref")]
        for lb in labels:
            declared[lb] = declared.get(lb, 0) + int(e.get("rows") or 0)
            declared_entries.setdefault(lb, []).append(e.get("ref"))

    d3_fails = []

    # D3a: 13 个 TBD 标签必须全部有登记条目
    missing_labels = [lb for lb in TBD_LABELS if lb not in declared_entries]
    if missing_labels:
        d3_fails.append("D3a 13 项 TBD 标签未全覆盖, 缺: %s" % ", ".join(missing_labels))

    # D3b: 每个标签的声明行数必须 == 实测行数
    for lb in sorted(rows_by_label):
        got = declared.get(lb, 0)
        if got != rows_by_label[lb]:
            d3_fails.append(
                "D3b 标签 %s 声明行数 %d != 实测行数 %d" % (lb, got, rows_by_label[lb])
            )

    # D3c: 每标签的 [待原厂] 行数必须 <= 该标签声明行数 (即被覆盖)
    for lb in sorted(pend_by_label):
        got = declared.get(lb, 0)
        if pend_by_label[lb] > got:
            d3_fails.append(
                "D3c 标签 %s 的 [待原厂] 行 %d > 声明覆盖行数 %d" % (lb, pend_by_label[lb], got)
            )
    if orphan_pend:
        d3_fails.append("D3c 有 %d 行 [待原厂] 落在 tbd 列之外, 未被任何标签覆盖" % len(orphan_pend))

    # D3d: 每条外部 needs 必须有登记条目
    ext_keys = set()
    for n in needs:
        if (n.get("to") or "") in EXTERNAL or (n.get("waiting_on") or "") in EXTERNAL:
            ext_keys.add(n.get("key"))
    reg_need_refs = {e.get("ref") for e in entries if e.get("scope") == "needs"}
    missing_needs = sorted(k for k in ext_keys if k not in reg_need_refs)
    if missing_needs:
        d3_fails.append("D3d 外部 needs 未全部登记, 缺: %s" % ", ".join(str(k) for k in missing_needs))

    # D3e: 每条 blocker 必须有登记条目
    blk_ids = {b.get("id") for b in blockers if b.get("id")}
    reg_blk_refs = {e.get("ref") for e in entries if e.get("scope") == "blocker"}
    missing_blks = sorted(b for b in blk_ids if b not in reg_blk_refs)
    if missing_blks:
        d3_fails.append("D3e blocker 未全部登记, 缺: %s" % ", ".join(str(b) for b in missing_blks))

    covered_rows = sum(min(declared.get(lb, 0), rows_by_label[lb]) for lb in rows_by_label)
    covered_rows += len(orphan_pend) and 0  # orphan 不计入覆盖
    pct = (100.0 * covered_rows / total) if total else 100.0
    add(
        "D3",
        not d3_fails,
        "网表待清行 %d 行 (tbd 列) + [待原厂] %d 行 (其中 %d 行在 tbd 列外) ⇒ 登记块覆盖率 %.1f%% (要求 100%%)"
        % (total, len(pend_rows), len(orphan_pend), pct),
        d3_fails,
    )

    # ---------- D4: 证据等级 + 降级方案/结论 ----------
    d4_fails = []
    for e in entries:
        ref = e.get("ref") or "<no-ref>"
        ev = (e.get("evidence") or "").strip()
        if ev not in EVIDENCE_TAGS:
            d4_fails.append("D4 %s 证据等级非法/缺: %r (要求 ∈ %s)" % (ref, ev, list(EVIDENCE_TAGS)))
        if not (e.get("downgrade") or "").strip():
            d4_fails.append("D4 %s 缺【降级方案】" % ref)
        if not (e.get("conclusion") or "").strip():
            d4_fails.append("D4 %s 缺【结论】" % ref)
    add("D4", not d4_fails, "登记条目 %d 条, 缺证据等级/降级方案/结论的 = %d 处 (要求 0)" % (len(entries), len(d4_fails)), d4_fails)

    # ---------- D5: 还卡不卡板那一趟 + 判据出处 ----------
    d5_fails = []
    for e in entries:
        ref = e.get("ref") or "<no-ref>"
        st = (e.get("blocks_board") or "").strip()
        if st not in BOARD_STATES:
            d5_fails.append("D5 %s 【还卡不卡板那一趟】非法/缺: %r (要求 ∈ %s)" % (ref, st, list(BOARD_STATES)))
        if not (e.get("judgement_ref") or "").strip():
            d5_fails.append("D5 %s 缺【判据出处】" % ref)
    add("D5", not d5_fails, "登记条目 %d 条, 缺【卡/不卡/条件卡】或判据出处的 = %d 处 (要求 0)" % (len(entries), len(d5_fails)), d5_fails)

    return res


# ----------------------------------------------------------------------
# 打印
# ----------------------------------------------------------------------
def print_report(res, verbose=True):
    order = ["D1", "D2", "D3", "D4", "D5"]
    print("=" * 96)
    print("HW 域外部依赖自查收口 · 机器闸 (ISS-401)")
    print("=" * 96)
    red = 0
    for code in order:
        r = res.get(code)
        if r is None:
            print("[SKIP] %s 未产出结果" % code)
            red += 1
            continue
        tag = "PASS" if r["ok"] else "FAIL"
        if not r["ok"]:
            red += 1
        print("[%s] %s  %s" % (tag, code, r["detail"]))
        if not r["ok"] and verbose:
            for f in r["fails"]:
                print("        · %s" % f)
    print("-" * 96)
    if red:
        print("★结论: 红 %d 条判据 ⇒ 【现状未收口】(这是预期中的红, 不是闸故障)" % red)
        print("★      判据全绿的条件见 HW/HW_EXTERNAL_DEPENDENCY_SELFCHECK_CLOSURE.md §4 登记块 + §6.1")
    else:
        print("★结论: 5 条判据全绿 ⇒ HW 域外部依赖已收口")
    print("=" * 96)
    return red


# ----------------------------------------------------------------------
# --selftest: 正向 ≥1 + 反向 ≥6
# ----------------------------------------------------------------------
def _mk_entry(ref, scope="needs", labels=None, rows=0, pend=0, ev="[官网]",
              downgrade="降级方案", conclusion="结论", board="不卡", judge="判据出处"):
    e = {"scope": scope, "ref": ref, "conclusion": conclusion, "evidence": ev,
         "evidence_ref": "fixture", "downgrade": downgrade, "blocks_board": board,
         "judgement_ref": judge}
    if labels is not None:
        e["tbd_labels"] = list(labels)
        e["rows"] = rows
        e["pend_rows"] = pend
    return e


def _fixture_ok():
    """一份【完全合规】的合成 fixture。"""
    needs = [
        {"key": "q16_display_iface", "to": "main", "waiting_on": "boss", "item": "x"},
        {"key": "n_internal", "to": "main", "waiting_on": None, "item": "x"},
    ]
    blockers = [{"id": "HW-B1"}, {"id": "HW-B2"}]
    rows = []
    # 标签 TBD-01 有 2 行 (其中 1 行 [待原厂]); TBD-02 有 1 行 (无 [待原厂])
    rows.append({"tbd": "TBD-01", "evidence": "[待原厂]", "net": "A"})
    rows.append({"tbd": "TBD-01", "evidence": "[推算]", "net": "B"})
    rows.append({"tbd": "TBD-02", "evidence": "[官方]", "net": "C"})
    entries = [
        _mk_entry("q16_display_iface", "needs"),
        _mk_entry("HW-B1", "blocker"),
        _mk_entry("HW-B2", "blocker"),
        _mk_entry("TBD-01", "tbd", labels=["TBD-01"], rows=2, pend=1),
        _mk_entry("TBD-02", "tbd", labels=["TBD-02"], rows=1, pend=0),
        # 13 标签全覆盖需要 13 条 —— 补齐
    ]
    for lb in TBD_LABELS:
        if lb not in ("TBD-01", "TBD-02"):
            entries.append(_mk_entry(lb, "tbd", labels=[lb], rows=0, pend=0))
    registry = {"entries": entries}
    return needs, blockers, rows, registry


def run_selftest():
    cases = []      # (name, expect_all_green, needs, blockers, rows, registry)
    fails = []

    def check(name, cond, msg):
        if cond:
            print("  [PASS] %s" % name)
        else:
            print("  [FAIL] %s :: %s" % (name, msg))
            fails.append(name)

    print("=" * 96)
    print("--selftest · 正向 ≥1 + 反向 ≥6")
    print("=" * 96)

    # ---------- 正向: 合规 fixture 必须全绿 ----------
    n, b, rows, reg = _fixture_ok()
    res = evaluate(n, b, rows, reg)
    all_green = all(res[c]["ok"] for c in ("D1", "D2", "D3", "D4", "D5"))
    check("正向-1 合规样例 ⇒ 5 条判据全绿", all_green,
          "绿/红: %s" % {c: res[c]["ok"] for c in ("D1", "D2", "D3", "D4", "D5")})
    cases.append(("正向-1", all_green))

    # ---------- 反向 1: D1 (waiting_on 外部) ----------
    n, b, rows, reg = _fixture_ok()
    n[1]["waiting_on"] = "vendor"
    res = evaluate(n, b, rows, reg)
    check("反向-1 needs 有 waiting_on=vendor ⇒ D1 红", (not res["D1"]["ok"]) and res["D2"]["ok"],
          "D1.ok=%s" % res["D1"]["ok"])
    cases.append(("反向-1", (not res["D1"]["ok"]) and res["D2"]["ok"]))

    # ---------- 反向 2: D2 (to 外部) ----------
    n, b, rows, reg = _fixture_ok()
    n[1]["to"] = "jbd"
    res = evaluate(n, b, rows, reg)
    check("反向-2 needs 有 to=jbd ⇒ D2 红", (not res["D2"]["ok"]) and res["D1"]["ok"],
          "D2.ok=%s" % res["D2"]["ok"])
    cases.append(("反向-2", (not res["D2"]["ok"]) and res["D1"]["ok"]))

    # ---------- 反向 3: D3a 13 标签未全覆盖 ----------
    n, b, rows, reg = _fixture_ok()
    reg["entries"] = [e for e in reg["entries"] if e["ref"] != "TBD-07"]
    res = evaluate(n, b, rows, reg)
    check("反向-3 缺 TBD-07 登记 ⇒ D3 红", (not res["D3"]["ok"]) and
          any("D3a" in f for f in res["D3"]["fails"]), "D3.fails=%s" % res["D3"]["fails"])
    cases.append(("反向-3", (not res["D3"]["ok"])))

    # ---------- 反向 4: D3b 声明行数 != 实测行数 ----------
    n, b, rows, reg = _fixture_ok()
    for e in reg["entries"]:
        if e["ref"] == "TBD-01":
            e["rows"] = 99
    res = evaluate(n, b, rows, reg)
    check("反向-4 TBD-01 声明行数写错 ⇒ D3 红", (not res["D3"]["ok"]) and
          any("D3b" in f for f in res["D3"]["fails"]), "D3.fails=%s" % res["D3"]["fails"])
    cases.append(("反向-4", (not res["D3"]["ok"])))

    # ---------- 反向 5: D3d 外部 needs 未登记 ----------
    n, b, rows, reg = _fixture_ok()
    n[1]["to"] = "vendor"   # 变成外部 need, 但登记块里没有这条 key
    res = evaluate(n, b, rows, reg)
    check("反向-5 外部 needs 未登记 ⇒ D3 红 (且 D2 红)", (not res["D3"]["ok"]) and
          any("D3d" in f for f in res["D3"]["fails"]), "D3.fails=%s" % res["D3"]["fails"])
    cases.append(("反向-5", (not res["D3"]["ok"])))

    # ---------- 反向 6: D3e blocker 未登记 ----------
    n, b, rows, reg = _fixture_ok()
    b.append({"id": "HW-B9"})
    res = evaluate(n, b, rows, reg)
    check("反向-6 有未登记的 blocker HW-B9 ⇒ D3 红", (not res["D3"]["ok"]) and
          any("D3e" in f for f in res["D3"]["fails"]), "D3.fails=%s" % res["D3"]["fails"])
    cases.append(("反向-6", (not res["D3"]["ok"])))

    # ---------- 反向 7: D4 缺证据等级 ----------
    n, b, rows, reg = _fixture_ok()
    reg["entries"][0]["evidence"] = "[瞎写]"
    res = evaluate(n, b, rows, reg)
    check("反向-7 非法证据等级 ⇒ D4 红", (not res["D4"]["ok"]) and res["D3"]["ok"],
          "D4.fails=%s" % res["D4"]["fails"])
    cases.append(("反向-7", (not res["D4"]["ok"]) and res["D3"]["ok"]))

    # ---------- 反向 8: D4 缺降级方案 ----------
    n, b, rows, reg = _fixture_ok()
    reg["entries"][0]["downgrade"] = ""
    res = evaluate(n, b, rows, reg)
    check("反向-8 缺降级方案 ⇒ D4 红", (not res["D4"]["ok"]), "D4.fails=%s" % res["D4"]["fails"])
    cases.append(("反向-8", (not res["D4"]["ok"])))

    # ---------- 反向 9: D5 缺「卡/不卡/条件卡」 ----------
    n, b, rows, reg = _fixture_ok()
    reg["entries"][1]["blocks_board"] = "大概不卡"
    res = evaluate(n, b, rows, reg)
    check("反向-9 blocks_board 非法值 ⇒ D5 红", (not res["D5"]["ok"]), "D5.fails=%s" % res["D5"]["fails"])
    cases.append(("反向-9", (not res["D5"]["ok"])))

    # ---------- 反向 10: D5 缺判据出处 ----------
    n, b, rows, reg = _fixture_ok()
    reg["entries"][2]["judgement_ref"] = ""
    res = evaluate(n, b, rows, reg)
    check("反向-10 缺判据出处 ⇒ D5 红", (not res["D5"]["ok"]), "D5.fails=%s" % res["D5"]["fails"])
    cases.append(("反向-10", (not res["D5"]["ok"])))

    # ---------- 反向 11: D3c [待原厂] 行未被覆盖 (tbd 列外) ----------
    n, b, rows, reg = _fixture_ok()
    rows.append({"tbd": "", "evidence": "[待原厂]", "net": "D"})
    res = evaluate(n, b, rows, reg)
    check("反向-11 tbd 列外的 [待原厂] 行 ⇒ D3 红", (not res["D3"]["ok"]) and
          any("D3c" in f for f in res["D3"]["fails"]), "D3.fails=%s" % res["D3"]["fails"])
    cases.append(("反向-11", (not res["D3"]["ok"])))

    positives = sum(1 for _, ok in cases if ok and _.startswith("正向"))
    negatives = sum(1 for _, ok in cases if ok and _.startswith("反向"))
    print("-" * 96)
    print("正向用例 %d 个 (要求 ≥1) · 反向用例 %d 个 (要求 ≥6)" % (positives, negatives))
    if fails:
        print("★有 %d 条用例失败: %s" % (len(fails), ", ".join(fails)))
        print("SELFTEST FAILED")
        return 1
    if positives < 1 or negatives < 6:
        print("★用例数量不足 (正向 %d / 反向 %d)" % (positives, negatives))
        print("SELFTEST FAILED")
        return 1
    print("ALL TESTS PASS")
    return 0


# ----------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(description="HW 域外部依赖自查收口机器闸 (ISS-401)")
    ap.add_argument("--selftest", action="store_true", help="跑自测用例 (rc=0 · 末行 ALL TESTS PASS)")
    ap.add_argument("--quiet", action="store_true", help="不打印逐条失败明细")
    ap.add_argument("--frag", default=FRAG,
                    help="分片路径 (默认 state/fragments/hw.yaml; 指向备份可复现收口前的红)")
    ap.add_argument("--truth", default=TRUTH,
                    help="真相页路径 (默认 HW/HW_EXTERNAL_DEPENDENCY_SELFCHECK_CLOSURE.md)")
    args = ap.parse_args()

    if args.selftest:
        return run_selftest()

    try:
        needs, blockers = load_needs(args.frag)
        rows = load_netlist_rows()
        registry = load_registry(args.truth)
    except SystemExit:
        raise
    except Exception as e:  # noqa: BLE001
        print("[FAIL] 闸跑不起来: %s" % e)
        print("★红的是【闸故障】(fail-closed), 不是现状")
        return 1

    res = evaluate(needs, blockers, rows, registry)
    red = print_report(res, verbose=not args.quiet)
    return 1 if red else 0


if __name__ == "__main__":
    sys.exit(main())
