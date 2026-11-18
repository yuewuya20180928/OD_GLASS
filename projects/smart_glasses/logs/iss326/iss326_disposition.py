#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-326 · MECH 侧「S1 改名」命中处置表生成器

★只读真件, 只写 logs/iss326/★ (零写板 · 零落表 · 零改闸)
输入: logs/iss326/mech_ref_hits.tsv (上一趟产物, 不重扫)
输出: logs/iss326/mech_ref_disposition.tsv (逐行 1,935 行, 三清单分开 + 失效形态逐条判)

判据口径 (本单自定义, 供 §5 引用):
  RED    直接报错/判红   —— 显式失败, 会被发现
  SILENT 静悄悄不查了   —— 判据分支再也匹配不上 ⇒ 假绿 ⇒ 最坏
  SAFE   不受影响
"""
from __future__ import annotations

import csv
import os
import re
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOG = os.path.join(ROOT, "logs", "iss326")
HITS = os.path.join(LOG, "mech_ref_hits.tsv")
OUT = os.path.join(LOG, "mech_ref_disposition.tsv")

# ---------------------------------------------------------------- 读命中表
rows = []
with open(HITS, encoding="utf-8") as f:
    rdr = csv.reader(f, delimiter="\t")
    head = next(rdr)
    for r in rdr:
        if len(r) < 8:
            continue
        f_, ln, hk, fc, ref, new, mv = r[0], r[1], r[2], r[3], r[4], r[5], r[6]
        ctx = r[7] if len(r) == 8 else "\t".join(r[7:])
        rows.append(dict(file=f_, line=int(ln), hit_kind=hk, file_class=fc,
                         ref=ref, new_ref=new, move=mv, context=ctx))
# ★口径澄清★: `wc -l mech_ref_hits.tsv` = 1935 (含 1 行表头) ⇒ 数据行 = 1934
#   ⇒ main 报的「1,935 行」与本单的「口径A = 1,934 出现次数」差的那 1 行 = 表头
assert len(rows) == 1934, f"数据行数不是 1934, 是 {len(rows)}"

# ---------------------------------------------------------------- 源文件缓存
SRC: dict[str, list[str]] = {}
def srclines(rel: str) -> list[str]:
    if rel not in SRC:
        p = os.path.join(ROOT, rel)
        if os.path.exists(p):
            with open(p, encoding="utf-8", errors="replace") as f:
                SRC[rel] = f.read().splitlines()
        else:
            SRC[rel] = []
    return SRC[rel]

def srctext(rel: str) -> str:
    return "\n".join(srclines(rel))

# ---------------------------------------------------------------- 判据脚本的 md 依赖
# 判据脚本读哪些 md (常量路径) ⇒ md 里改位号 ⇒ 可能让判据失配
DOC_CONSUMERS: dict[str, list[str]] = defaultdict(list)
# ★只认【真读】: 常量赋值行 (XXX_REL/DOC/FILE/PATH = ...) 或 open(...md) ★
#   ⇒ 避免把 docstring 里「提到某 md」误判成「读某 md」(BOARD_GEOM_30MM.md 就是这种)
for rel in sorted({r["file"] for r in rows if r["file_class"] == "判据脚本"}):
    t = srctext(rel)
    for ln in t.splitlines():
        s = ln.strip()
        if s.startswith("#"):
            continue
        if not (re.match(r"^[A-Z_][A-Z0-9_]*(REL|DOC|FILE|PATH|WP|CALIB|SPEC|LEDGER)?\w*\s*=\s*.*\.md", s)
                or re.search(r"open\([^)]*\.md", s)):
            continue
        for m in re.finditer(r'"((?:MECH|HW)/[A-Za-z0-9_./-]+\.md)"', ln):
            DOC_CONSUMERS[m.group(1)].append(rel)
        for m in re.finditer(r'os\.path\.join\(HERE,\s*"([A-Za-z0-9_.-]+\.md)"', ln):
            DOC_CONSUMERS[os.path.join("MECH", m.group(1))].append(rel)

# ---------------------------------------------------------------- 逐 (文件, ref) 的匹配模式
# EXACT 精确等值/精确成员 ⇒ 改名(_1 后缀)后失配 ⇒ SILENT
# PREFIX 前缀/正则前缀锚 ⇒ 改名后仍匹配 ⇒ SAFE
# SUBSCRIPT 硬下标取键 ⇒ 改名后 KeyError ⇒ RED
# DOCONLY 只在散文/打印里 ⇒ SAFE
FILE_MODE: dict[tuple[str, str], tuple[str, str]] = {}

def ref_literal(ref: str) -> re.Pattern:
    return re.compile(r"(['\"])" + re.escape(ref) + r"\1")

def analyse_file_ref(rel: str, ref: str) -> tuple[str, str]:
    lines = srclines(rel)
    text = srctext(rel)
    # --selftest 反向用例区起点 (在该区里的命中 = 自测会红, 不是主判据路径)
    selftest_at = None
    for i, ln in enumerate(lines, 1):
        if re.match(r"\s*#\s*=+\s*selftest", ln, re.I) or re.match(r"\s*def\s+selftest\b", ln):
            selftest_at = i
            break
    modes: list[tuple[str, str, int]] = []
    notes = []
    # ---- 多行 re.compile 模式收集 (★pattern 跨行时单行判会看漏结尾的 $ 锚★) ----
    mpat: list[tuple[int, int, str]] = []   # (起行, 止行, 模式串)
    for cm in re.finditer(r"re\.compile\(\s*r?(['\"])", text):
        q = cm.group(1)
        i = cm.end()          # ★从引号【之后】开始扫 (★否则 pat 恒为空★)
        pat = ""
        sl = text[:cm.start()].count("\n") + 1
        el = sl
        while True:
            buf = []
            while i < len(text):
                c = text[i]
                if c == "\\" and i + 1 < len(text):
                    buf.append(text[i:i + 2]); i += 2; continue
                if c == q:
                    break
                buf.append(c); i += 1
            pat += "".join(buf)
            el = text[:i].count("\n") + 1
            if i >= len(text):
                break
            # ★相邻字符串字面量隐式拼接 (r"..." r"...") ⇒ 继续拼★
            j = i + 1
            while j < len(text) and text[j] in " \t\n":
                j += 1
            if j < len(text) and text[j] in "rR" and j + 1 < len(text) and text[j + 1] in "\"'":
                q2 = text[j + 1]
                i = j + 2
                q = q2
                continue
            if j < len(text) and text[j] in "\"'":
                q2 = text[j]
                i = j + 1
                q = q2
                continue
            break
        if pat:
            mpat.append((sl, el, pat))
    def pat_at(ln_no: int) -> str | None:
        for sl, el, pat in mpat:
            if sl <= ln_no <= el:
                return pat
        return None
    rx = ref_literal(ref)
    rxw = re.compile(r"\b" + re.escape(ref) + r"\b")
    for i, ln in enumerate(lines, 1):
        if not rxw.search(ln):          # ★词边界匹配 (★含正则模式里的裸位号★)
            continue
        stripped = ln.strip()
        tag = " [在 --selftest 反向用例区]" if (selftest_at and i >= selftest_at) else ""
        if stripped.startswith("#"):
            modes.append(("SAFE", f"L{i} 注释行{tag}", i))
            continue
        if re.search(r"\[\s*" + re.escape(f'"{ref}"') + r"\s*\]", ln) or \
           re.search(r"\[\s*" + re.escape(f"'{ref}'") + r"\s*\]", ln):
            modes.append(("RED", f"L{i} 硬下标取键 ⇒ 改名后 KeyError{tag}", i))
            continue
        if re.search(r"[!=]=\s*" + re.escape(f'"{ref}"'), ln) or \
           re.search(r"[!=]=\s*" + re.escape(f"'{ref}'"), ln) or \
           re.search(r"(['\"])" + re.escape(ref) + r"\1\s*[!=]=", ln):
            if stripped.startswith("assert"):
                modes.append(("RED", f"L{i} assert 等值 ⇒ 改名后断言失败{tag}", i))
            else:
                modes.append(("SILENT", f"L{i} 精确等值分支 ⇒ 改名后分支失配 (假绿){tag}", i))
            continue
        # 多行 re.compile ⇒ 用完整 pattern 判 (前缀锚 vs $ 锚)
        pat_full = pat_at(i)
        if pat_full is not None and ref in pat_full:
            if "^" in pat_full and not re.search(r"\$", pat_full) and not re.search(r"\\b", pat_full):
                modes.append(("SAFE", f"L{i} 前缀锚正则 ⇒ 加 _1 后缀仍匹配前缀{tag}", i))
            else:
                modes.append(("SILENT", f"L{i} 正则含位号字面量且带 $ 锚/词边界 ⇒ 改名后失配 (假绿){tag}", i))
            continue
        # re.compile(...) 里的字面量 ⇒ 看是不是前缀锚
        for cm in re.finditer(r"re\.compile\(\s*r?(['\"])(.*?)\1", ln):
            pat = cm.group(2)
            if ref in pat:
                if "^" in pat and not re.search(r"\$", pat) and not re.search(r"\\b", pat):
                    modes.append(("SAFE", f"L{i} 前缀锚正则 ⇒ 加 _1 后缀仍匹配前缀{tag}", i))
                else:
                    modes.append(("SILENT", f"L{i} 正则含位号字面量且非纯前缀 ⇒ 改名后失配{tag}", i))
                break
        else:
            # 集合字面量 ⇒ 看该集合被谁消费
            am = re.match(r"([A-Z_][A-Z0-9_]*)\s*=\s*[\[\{]", stripped)
            if am:
                var = am.group(1)
                prefix_use = re.search(
                    r"re\.compile\([^)]*\b" + re.escape(var) + r"\b", text) or \
                    re.search(r"startswith\([^)]*\b" + re.escape(var) + r"\b", text)
                member_use = re.search(r"\bin\b\s+" + re.escape(var) + r"\b", text) or \
                             re.search(r"\bfor\b[^\n]*\bin\b\s+" + re.escape(var) + r"\b", text) or \
                             re.search(r"\bfor\b[^\n]*\bin\b\s+" + re.escape(var) + r"\b", text)
                if prefix_use:
                    modes.append(("SAFE", f"L{i} 集合 {var} 以【前缀/正则】消费 ⇒ 改名后仍命中{tag}", i))
                elif member_use:
                    modes.append(("SILENT", f"L{i} 集合 {var} 以【精确成员】消费 ⇒ 改名后失配 (假绿){tag}", i))
                else:
                    modes.append(("SILENT", f"L{i} 集合 {var} 仅用于计数/打印 ⇒ 主判据不失配 (保守判假绿){tag}", i))
            elif re.search(r"\b" + re.escape(ref) + r"\b", ln) and (
                    "print(" in ln or 'f"' in ln or "f'" in ln or "#" in ln):
                modes.append(("SAFE", f"L{i} 只在打印/散文里出现 ⇒ 无功能影响{tag}", i))
            else:
                modes.append(("SAFE", f"L{i} 仅字面量出现, 无比较/取键语义 ⇒ 无功能影响{tag}", i))
    if not modes:
        return ("SAFE", "源文件内未再出现该字面量 (命中来自扫描口径, 非代码语义)")
    order = {"RED": 0, "SILENT": 1, "SAFE": 2}
    worst = min(modes, key=lambda x: order[x[0]])[0]   # ★不许用字符串比大小 (★"SAFE" < "SILENT" 会反★)★
    same = [m for m in modes if m[0] == worst]
    uniq: list[str] = []
    for _, d, _ in same:
        if d not in uniq:
            uniq.append(d)
    tail = f" (同类共 {len(same)} 处)" if len(same) > len(uniq) else ""
    other = [m for m in modes if m[0] != worst]
    extra = ""
    if other:
        extra = " · 另有较弱形态: " + "; ".join(sorted({m[1] for m in other})[:2])
    return (worst, "; ".join(uniq[:3]) + tail + extra)

def mode_of(rel: str, ref: str) -> tuple[str, str]:
    key = (rel, ref)
    if key not in FILE_MODE:
        FILE_MODE[key] = analyse_file_ref(rel, ref)
    return FILE_MODE[key]

# ---------------------------------------------------------------- md 被读 + 判据含该位号 ⇒ 文档改名 ⇒ 红
def doc_cross_effect(md_rel: str, ref: str) -> tuple[str, str] | None:
    for scr in DOC_CONSUMERS.get(md_rel, []):
        m, why = mode_of(scr, ref)
        if m in ("RED", "SILENT"):
            return (m, f"★跨文件★ {md_rel} 被 {scr} 读取, 该脚本含位号 {ref} ({m}: {why}) ⇒ 改 md 即失配")
    return None

# ---------------------------------------------------------------- 生成处置表
out_rows = []
counts = Counter()
for r in rows:
    rel, ref = r["file"], r["ref"]
    fc, hk = r["file_class"], r["hit_kind"]
    # ---- 清单归属
    if fc == "历史脚本":
        owner = "历史脚本 · 不改"
        form, why = "SAFE", "一次性落地脚本, 跑完即退 ⇒ 改名不回溯 ⇒ 不受影响"
        adv = "不列改动清单 (历史脚本 · 不改)"
    elif hk == "py-注释":
        owner = "注释 · 无功能影响"
        form, why = "SAFE", "注释行不参与求值 ⇒ 无功能影响 (ISS-320 同型先例: service_port_check.py L51 型号名在注释里, md5 钉死 ⇒ 不该改)"
        adv = "不列改动清单 (注释 · 无功能影响)"
    elif fc == "判据脚本":
        owner = "判据脚本 · 要改"
        form, why = mode_of(rel, ref)
        if form == "RED":
            adv = "★必须改★ 精确对齐新名, 否则该闸直接报错 (红)"
        elif form == "SILENT":
            adv = "★必须改★ 精确对齐新名, 否则判据分支失配 ⇒ 静悄悄不查了 (假绿, 最坏)"
        else:
            adv = "可不改 (前缀/散文口径 ⇒ 改名后仍匹配)"
    else:  # 文档
        owner = "文档 · 无功能影响"
        eff = doc_cross_effect(rel, ref)
        if eff:
            form, why = eff
            adv = "★必须走合法通道★ 改本 md 会让判据脚本失配 (且 md5 受保护件不许硬改)"
        else:
            form, why = "SAFE", "散文/规格正文, 无判据脚本按位号读取本文件 ⇒ 不受影响"
            adv = "不列改动清单 (文档 · 无功能影响)"
    counts[(owner, form)] += 1
    out_rows.append([rel, r["line"], hk, fc, ref, r["new_ref"], r["move"],
                     owner, form, why, adv])

os.makedirs(LOG, exist_ok=True)
with open(OUT, "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter="\t", lineterminator="\n")
    w.writerow(["文件", "行", "命中形态", "文件类别", "旧位号", "新位号", "改不改",
                "清单归属", "失效形态", "判据依据", "处置建议"])
    w.writerows(out_rows)

print(f"[disposition] 写出 {OUT} · {len(out_rows)} 行")
print("[disposition] 清单归属 × 失效形态 分布:")
for (owner, form), c in sorted(counts.items(), key=lambda x: (-x[1])):
    print(f"  {owner:<22} {form:<8} {c:>6}")
print("[disposition] 失效形态合计:", dict(Counter(f for (_, f), c in counts.items() for _ in range(c))))
print("[disposition] 按失效形态:", dict(Counter(r[8] for r in out_rows)))
print("[disposition] 判据脚本里 RED/SILENT 的文件分布:")
per = Counter((r[0], r[8]) for r in out_rows if r[7] == "判据脚本 · 要改" and r[8] != "SAFE")
for (f_, fo), c in per.most_common():
    print(f"  {fo:<8} {c:>4}  {f_}")
sys.exit(0)
