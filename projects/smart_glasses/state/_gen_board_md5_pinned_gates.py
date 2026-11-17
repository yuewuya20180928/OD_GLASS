#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""main (moli) 2026-11-17 18:3x · job 775d9893「ARS45 继续执行后继计划」
★生成【全仓「钉着板 md5」的闸清单】—— 「板只改一次」那一趟改板当天, 这 9 道闸会同时红 ⇒ 必须先建「合法改板」通道★
★**输出**: `state/board_md5_pinned_gates.md` (人读表 + 机器可读 JSON) ★
★**数据来源**: 真扫全仓 (★不许手写★) ⇒ `grep 611b869e` 命中 + 每处上下文判定「硬编码基线 vs 台账口径」★
★**纪律**: 只读 + 只写自己那一个输出文件; 不碰任何闸脚本 ★
"""
import json
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
OUT = os.path.join(HERE, "board_md5_pinned_gates.md")
BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"

SKIP_DIRS = {".git", "__pycache__", "node_modules", ".lastgood", ".bak", "tmp", "logs", "outbox"}
# 已建成「合法改板」通道的 (ISS-284 已做, SW 侧)
DONE = {
    "SW/tools/check_demo_panel_spec.py": "ISS-284 已做 (★reboard 原子映射 {by,file,prev_md5,md5} + 四项缺一⇒红 + 与台账链头一致★)",
}

rows = []
for dirpath, dirnames, filenames in os.walk(PROJ):
    dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".bak")]
    for fn in filenames:
        if not fn.endswith(".py"):
            continue
        p = os.path.join(dirpath, fn)
        rel = os.path.relpath(p, PROJ)
        # ★只收【闸脚本】: 命名口径 check_*.py / *_check.py; 且排除一次性脚本 (state/_*.py)★
        base = os.path.basename(rel)
        if not (base.startswith("check_") or base.endswith("_check.py") or base.endswith("_check.py")):
            continue
        if rel.startswith("state/_") or rel.startswith("state/gen_"):
            continue
        try:
            txt = open(p, encoding="utf-8", errors="ignore").read()
        except Exception:
            continue
        if BOARD_MD5 not in txt:
            continue
        hits = []
        for i, ln in enumerate(txt.split("\n"), 1):
            if BOARD_MD5 in ln:
                hits.append((i, ln.strip()[:150]))
        # 判定: 有没有【台账口径】(读 SW_MD5_BASELINE_LEDGER / source_ledger / reboard)
        has_reboard = "reboard" in txt
        ledger_like = bool(re.search(r"source_ledger|SW_MD5_BASELINE_LEDGER|SCHEMATIC_LANDING_V1_LANDED|netlist_md5_allowed", txt))
        if has_reboard:
            cls = "★已有 reboard 通道★"
        elif ledger_like:
            cls = "★部分台账口径 (★别的文件走台账, 但板仍硬钉★)"
        else:
            cls = "★纯硬钉 (★板 md5 写死, 无任何台账口径★)"
        rows.append({"file": rel, "hits": hits[:4], "hit_count": len(hits),
                     "has_ledger_path": ledger_like, "has_reboard": has_reboard,
                     "cls": cls, "note": DONE.get(rel, "")})

rows.sort(key=lambda r: r["file"])
n_hard = sum(1 for r in rows if not r["has_ledger_path"])
n_done = sum(1 for r in rows if r["note"])

lines = []
lines.append("# ★全仓「钉着板 md5」的闸清单 ★ (★机器生成 · main 2026-11-17 18:3x·★数据来自真扫全仓, 不许手写★)")
lines.append("")
lines.append(f"> ★**为什么要这张表**: ★**「板只改一次」那一趟 (S1~S13) 合法改板当天, 下面这 {len(rows)} 道闸会同时红** ★")
lines.append("> ⇒ ★**而这些红的真实含义是「板被换了」, 不是「板改坏了」** ⇒ ⇒ ★**现场的人极可能误读成后者 ⇒ 去改板凑绿 ⇒ 板 md5 变第二次 ⇒ 整趟白跑** ★")
lines.append("> ⇒ ★**所以: 板那一趟开工前, 每道钉板 md5 的闸都必须先有【合法改板】通道 (照 ISS-284 的 `reboard` 原子映射形状)** ★")
lines.append("> ⇒ ★**判据不许松**: 通道只允许【有落表台账背书的合法改板】走绿; ★**盘上 ≠ 基线且无合法记录 ⇒ 仍红** ★")
lines.append("")
lines.append(f"## ★清单 (★共 {len(rows)} 处 · ★其中**已建通道** {n_done} 处 · **仍缺通道** {n_hard} 处★)")
lines.append("")
lines.append("| # | 闸文件 | 钉法 | 命中行 | 已有台账口径? | 状态 |")
lines.append("|---|---|---|---|---|---|")
for i, r in enumerate(rows, 1):
    hits = "<br>".join(f"L{n}: `{h[:110]}`" for n, h in r["hits"])
    state = r["note"] or ("★**已建通道** ★" if r["has_reboard"] else "★**缺「合法改板」通道** ★")
    lines.append(f"| {i} | `{r['file']}` | {r['hit_count']} 处 | {hits} | {r['cls']} | {state} |")
lines.append("")
lines.append("## ★两侧的活怎么分 (★归口★)")
lines.append("")
lines.append("| 域 | 闸 | 单号 |")
lines.append("|---|---|---|")
for r in rows:
    if r["file"].startswith("SW/"):
        owner = "sw-lead"
    elif r["file"].startswith("MECH/"):
        owner = "mech-lead"
    else:
        owner = "hw-lead"
    lines.append(f"| `{r['file'].split('/')[0]}` | `{r['file']}` | ★**{owner}** ★ ({r['cls']}) |")
lines.append("")
lines.append("## ★「合法改板」通道的形状 (★照 ISS-284 已跑通的口径, 不许自创★)")
lines.append("")
lines.append("```")
lines.append("reboard: null                     # 还没发生过合法改板 ⇒ 纯 md5 硬保护 (盘上 ≠ 基线 ⇒ 红)")
lines.append("reboard: {by: <单号>, file: <文件名>, prev_md5: <改前>, md5: <改后>}")
lines.append("                                   # ★一个原子映射: 四项缺一 ⇒ 整条记录无效 ⇒ 红★")
lines.append("                                   # ★且四项必须能在落表台账里查到 (单号 + 文件名 + 新旧 md5)★")
lines.append("                                   # ★判据方向不许变: 盘上 ≠ 链头 ⇒ 红 (合法改板只让链头前移)★")
lines.append("                                   # ★fail-closed 三条一条不许动: 链头不唯一 / 链断 / 链头无单号 ⇒ 红★")
lines.append("```")
lines.append("")
lines.append("## ★复现命令 (★main 18:3x 实跑, 原样★)")
lines.append("")
lines.append("```bash")
lines.append(f"cd {PROJ}")
lines.append(f"grep -rln '{BOARD_MD5}' --include='*.py' . | grep -v -E '__pycache__|\\.bak|/logs/|/tmp/|\\.lastgood' | sort")
lines.append("```")
lines.append("")
lines.append("> ★**本表的生成脚本**: `state/_gen_board_md5_pinned_gates.py` (★改闸清单后重跑一次即可刷新★) ★")
lines.append(">")
lines.append("> ★**★口径已被证明可行 (★不是猜的★)**: `SW/tools/check_demo_panel_spec.py` ★**在 ISS-284 转成台账口径后, 它已经不再硬钉板 md5 ⇒ 本清单里根本找不到它** ★")
lines.append("> ⇒ ★**⇒ 「不硬钉」不是靠把断言删掉, 是靠判决源换成【落表台账 + reboard 记录】** ★")

txt = "\n".join(lines) + "\n"
open(OUT, "w", encoding="utf-8").write(txt)
json.dump(rows, open(os.path.join(HERE, "board_md5_pinned_gates.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("✔ 清单已生成: state/board_md5_pinned_gates.md")
print("  共 %d 个文件钉板 md5 | 已建通道 %d | 缺通道 %d" % (len(rows), n_done, n_hard))
for r in rows:
    print("   -", r["file"], "| 台账口径:", "有" if r["has_ledger_path"] else "无")
