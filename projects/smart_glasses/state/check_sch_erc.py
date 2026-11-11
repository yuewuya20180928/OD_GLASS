#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_sch_erc.py —— ★★【原理图 ERC 闸】★★ (★2026-11-11 10:15 新建★)

★★**为什么必须有这道闸 (★老板 10:07 把主线切到"原理图优先"后的第一件事★)**:
  ★**实测**: ★**2026-11-11 10:15 第一次对 `HW/PCB/demo_mainboard.kicad_sch` 跑 KiCad ERC
     ⇒ 【46 条违规】, 全部是 `label_dangling` (★"Label not connected"★)**
  ⇒ ★★**而在此之前: 从来没有跑过 ERC, 也从来没有一道 ERC 闸** ⇒ ★
     ★**我们自己的原理图自检 (C1~C6) 只查语义 (符号数/引脚数/网集合一致) ⇒ 全过** ⇒ ★
     ★★**⇒ 一张"ERC 46 条违规"的原理图, 在我们的闸体系里一直是【全绿】⇒ 这就是盲区★★
  ⇒ ★**⇒ 修法: ERC 必须成为原理图的一道机器闸 (rc=0 才算过) ⇒ 禁止"只改图纸不落闸"**

★★**判据**: ★**ERC 违规数必须 = 0** ⇒ ★**rc=0 = 过 · rc=1 = 不过 (并逐条点名)**

用法:
  python3 state/check_sch_erc.py              # 跑 ERC 并判定
  python3 state/check_sch_erc.py --json       # 机器读格式
  python3 state/check_sch_erc.py --self-test  # 自测 (★含反向用例★)
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import io

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.normpath(os.path.join(HERE, ".."))
SCH = os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_sch")
KICAD_SH = os.path.join(HERE, "kicad.sh")

# ★★**ERC 报告是一份【文本】(★不是 JSON!★)**: 形如
#   Found 46 violations
#   ***** Sheet /
#   [label_dangling]: Label not connected
#       ; error
#       @(2.30 mm, 41.27 mm): Label 'BAT_CELL_P'
_VIOL_RE = re.compile(r"^\[([A-Za-z0-9_]+)\]:\s*(.*)$", re.M)
_FOUND_RE = re.compile(r"^Found (\d+) violations?", re.M)
_SHEET_RE = re.compile(r"^\*+ Sheet (.*)$", re.M)


def parse_report(text: str) -> dict:
    """★把 ERC 文本报告解析成结构 (★唯一实现★) ⇒ 自测打的就是它"""
    m = _FOUND_RE.search(text)
    declared = int(m.group(1)) if m else None
    sheet = ""
    ms = _SHEET_RE.search(text)
    if ms:
        sheet = ms.group(1).strip()
    items = []
    for mm in _VIOL_RE.finditer(text):
        kind = mm.group(1)
        desc = mm.group(2).strip()
        # ★**取该条下面的定位信息 (@(x, y): Label 'X' / @(...): ...) ★**
        tail = text[mm.end():]
        nxt = _VIOL_RE.search(tail)
        seg = tail[: nxt.start()] if nxt else tail
        loc = ""
        ml = re.search(r"@\([^)]*\):\s*(.*)", seg)
        if ml:
            loc = ml.group(1).strip()
        items.append({"type": kind, "desc": desc, "loc": loc})
    by_type = {}
    for it in items:
        by_type[it["type"]] = by_type.get(it["type"], 0) + 1
    return {
        "declared": declared,
        "count": len(items),
        "by_type": by_type,
        "sheet": sheet,
        "items": items,
    }


def run_erc(out_path: str) -> tuple[int, str]:
    """★跑 KiCad ERC ⇒ (rc, 报告全文)"""
    cmd = ["bash", KICAD_SH, "sch", "erc", "--output", out_path, "--severity-error", SCH]
    p = subprocess.run(cmd, cwd=PROJ, capture_output=True, text=True, timeout=900)
    body = ""
    if os.path.exists(out_path):
        try:
            body = open(out_path, encoding="utf-8", errors="replace").read()
        except Exception:
            body = ""
    # ★★**实测 (★10:2x★): `Found N violations` 这行是打在【stdout】上的, 【不在报告文件里】**
    #   ⇒ 只读文件会漏掉"自称条数" ⇒ 解析器少一个交叉校验 ⇒ 报告文件 + stdout 一起拼上 ★★
    text = (p.stdout or "") + "\n" + (p.stderr or "") + "\n" + body
    return p.returncode, text


def self_test(e2e: bool = True) -> int:
    """★自测 (★铁律: 必须带反向用例 —— 判据改弱 ⇒ 自测必须红★)"""
    fails = []

    # ① 解析器: 有违规的报告 ⇒ 数量与分类要对
    dirty = """ERC report (2026-11-11T10:15:38, Encoding UTF8)
Report includes: Errors
Found 3 violations

***** Sheet /
[label_dangling]: Label not connected
    ; error
    @(2.30 mm, 41.27 mm): Label 'BAT_CELL_P'
[label_dangling]: Label not connected
    ; error
    @(2.30 mm, 371.27 mm): Label 'PMID'
[pin_not_connected]: Pin not connected
    ; error
    @(10.00 mm, 20.00 mm): Pin '1' of 'U3'
"""
    r = parse_report(dirty)
    if r["count"] != 3:
        fails.append("① 解析条数 = %d (期望 3)" % r["count"])
    if r["by_type"].get("label_dangling") != 2:
        fails.append("① 分类 label_dangling = %s (期望 2)" % r["by_type"].get("label_dangling"))
    if r["declared"] is None:
        fails.append("① 没抓到 'Found N violations'")

    # ② 干净报告 ⇒ 0 条 (★不许把干净板判死★)
    clean = "ERC report (2026-11-11T10:15:38, Encoding UTF8)\nReport includes: Errors\nFound 0 violations\n\n***** Sheet /\n"
    r2 = parse_report(clean)
    if r2["count"] != 0:
        fails.append("② 干净报告被判成 %d 条 (期望 0)" % r2["count"])

    # ③ ★反向用例 (★判据改弱的突变体必须被抓到★)★:
    #    假设解析器被改成"永远返回 0 条" ⇒ 上面 ① 的断言必然红 ⇒ 这就是它的证伪点
    def mutant(text):
        return {"declared": 0, "count": 0, "by_type": {}, "sheet": "", "items": []}

    if mutant(dirty)["count"] == 0 and parse_report(dirty)["count"] != 0:
        pass  # ★突变体与本体结论不同 ⇒ 说明断言真的在区分它们 ★
    else:
        fails.append("③ 反向用例失效: 突变体与本体结论相同 ⇒ 断言没在区分")

    # ④ 真实板跑一次 (★端到端: 必须报出真实现状★) ⇒ ★e2e=False 时跳过 (★巡检段用快的那个★)
    if not e2e:
        print("   [端到端] 跳过 (--self-test 不带 e2e)")
    elif os.path.exists(SCH):
        with tempfile.TemporaryDirectory() as td:
            out = os.path.join(td, "erc.txt")
            rc, text = run_erc(out)
            real = parse_report(text)
        if real["declared"] is None and real["count"] == 0:
            fails.append("④ 真实板 ERC 报告解析不出来 (rc=%d, 文本长度 %d)" % (rc, len(text)))
        else:
            print("   [端到端] 真实板: %d 条 (报告自称 %s) · 分类 %s"
                  % (real["count"], real["declared"], real["by_type"]))
    else:
        fails.append("④ 原理图文件不存在: %s" % SCH)

    if fails:
        for f in fails:
            print("❌", f)
        print("SELFTEST FAILED")
        return 1
    print("ALL TESTS PASS (%d 条: 解析器 / 干净板 / 反向用例%s)" % (4 if e2e else 3, " / 端到端" if e2e else ""))
    return 0


def main() -> int:
    args = sys.argv[1:]
    if "--self-test" in args:
        return self_test(e2e=False)
    if "--self-test-full" in args:
        return self_test(e2e=True)
    if not os.path.exists(SCH):
        print("❌ 原理图不存在: %s" % SCH)
        return 2
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, "erc.txt")
        rc, text = run_erc(out)
    rep = parse_report(text)
    # ★★**落缓存 (★让巡检能零成本报出 ERC 现状, 不用每次重跑 ERC★)** ★★
    try:
        import datetime
        cache = {
            "count": rep["count"], "by_type": rep["by_type"],
            "at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
            "sch_mtime": os.path.getmtime(SCH) if os.path.exists(SCH) else None,
        }
        cpath = os.path.join(HERE, ".erc_last.json")
        tmp = cpath + ".tmp"
        io.open(tmp, "w", encoding="utf-8").write(json.dumps(cache, ensure_ascii=False))
        os.replace(tmp, cpath)
    except Exception:
        pass
    if "--json" in args:
        print(json.dumps({
            "rc": rc, "count": rep["count"], "declared": rep["declared"],
            "by_type": rep["by_type"], "items": rep["items"][:60],
        }, ensure_ascii=False, indent=1))
    else:
        print("═══ 原理图 ERC 闸 (★sch_erc · %s★)" % os.path.relpath(SCH, PROJ))
        print("  ERC 违规数 = %d (★报告自称 %s★) · 分类 %s" % (rep["count"], rep["declared"], rep["by_type"]))
        for it in rep["items"][:40]:
            print("   · [%s] %s %s" % (it["type"], it["desc"], it["loc"]))
        if rep["count"] > 40:
            print("   · …… 还有 %d 条" % (rep["count"] - 40))
        print("  判定: %s" % ("✅ 过 (ERC=0)" if rep["count"] == 0 else "❌ 不过 (ERC≠0) ⇒ 原理图不许进投产包"))
    return 0 if rep["count"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
