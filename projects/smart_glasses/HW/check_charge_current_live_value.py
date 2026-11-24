#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-384 · hw-lead · 2026-11-24 · 充电电流活值口径守卫 (新闸)

★ 定位: ★**纯文档口径闸** —— 扫描三份 HW 活文档, 若某处仍把【0.822 旧系数 / 0.411A /
  1.22× / 旧充电时间 / 旧 TS 偏移】当【活值】写在页面上 ⇒ 判红并点名「文件:行号」。

★ 三条命门 (本闸最容易写错的地方):
  ① 【不许误伤历史留痕】ISS-230 留下的两处作废标记 (PCB_OUTLINE L151 / L193) 必须【不红】
     ⇒ 判据按【语境】判 (那两行的语境含「作废」二字), 不是按【子串】判
     ⇒ 反向用例: 删掉 L151 的作废标记 ⇒ 必须变红
  ② 【不许误伤落表真源】HW/netlist_v1.csv 里那 2 处 0.822 是【合法的历史说明】
     ⇒ 本闸的扫描范围【不许】包含网表 / 脚表 / BOM / PCB 文件
     ⇒ 反向用例: 把网表路径加进扫描范围 ⇒ 必须变红
  ③ 【不许误伤真值】文档里必须带上 680Ω 档真值三数 (0.697 / 0.349 / 1.43×) 与当前系数
     (1.216 @3.70V / 1.071 @4.20V) ⇒ 缺红

★ 零挂链: 本闸【不挂进】state/gate_check.py (挂链是 main 的地界) ⇒
  `grep -c check_charge_current_live_value state/gate_check.py` = 0

★ 权威源 (只读): MECH/HINGE_POWER_CALC.md §0-A / §0-A.1 (ISS-229 · mech-lead · 已 verified)
  + MECH/hinge_power_calc.json 的 rilim_table ⇒ 复现 `python3 MECH/hinge_power_calc.py --json`

用法:
  python3 HW/check_charge_current_live_value.py             # 裸跑, rc=0 ⇒ 全过
  python3 HW/check_charge_current_live_value.py --selftest  # 反向用例, 末行 ALL TESTS PASS
  python3 HW/check_charge_current_live_value.py --json      # 机器可读输出
"""

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── 扫描范围 (★只有这三份是【活文档】· 加网表/脚表/BOM/板文件一律判红) ──────────────
SCAN_DOCS = [
    "HW/PCB_OUTLINE_60x15.md",
    "HW/J_CHG_SELECTION.md",
    "HW/POWER_BUDGET_V3.md",
]

# ── 扫描范围禁入清单 (落表真源 / 板文件 / 别人地界) ─────────────────────────────────
FORBIDDEN_SCOPE_PATTERNS = [
    (re.compile(r"\.csv$", re.I), "CSV 表 (网表/脚表/BOM) 属落表真源, 文档闸不许碰"),
    (re.compile(r"\.kicad_(pcb|sch|pro)$", re.I), "KiCad 板/原理图文件属板侧, 文档闸不许碰"),
    (re.compile(r"netlist", re.I), "网表属落表真源, 文档闸不许碰"),
    (re.compile(r"\bbom", re.I), "BOM 属落表真源, 文档闸不许碰"),
    (re.compile(r"^state/"), "state/ 是流程地界, 文档闸不许碰"),
    (re.compile(r"^(MECH|SW|PM)/"), "MECH/SW/PM 是别人地界, 文档闸不许碰"),
]

# ── 旧值 token (★每个 token 都有唯一码, 订正块的「锚点」列引用这些码) ───────────────
TOKEN_PATTERNS = [
    ("T0822", r"(?<![\d.])0\.822(?![\d])"),          # 旧系数 (倒数方向) / 旧 ICHG 0.822A
    ("T082A", r"(?<![\d.])0\.82\s*A(?![A-Za-z0-9])"),  # 旧 ICHG 0.82A (390Ω 档)
    ("T0411", r"(?<![\d.])0\.411(?![\d])"),           # 旧 单 pin 0.411A (390Ω 档)
    ("T0534", r"(?<![\d.])0\.534(?![\d])"),           # 旧 单 pin 0.534A (300Ω 档)
    ("T0236", r"(?<![\d.])0\.236(?![\d])"),           # 旧 单 pin 0.236A (680Ω 档)
    ("T047A", r"(?<![\d.])0\.47\s*A(?![A-Za-z0-9])"),  # 旧 ICHG 0.47 A (680Ω 档)
    ("T107A", r"(?<![\d.])1\.07\s*A(?![A-Za-z0-9])"),  # 旧 ICHG 1.07 A (300Ω 档)
    ("T1069", r"(?<![\d.])1\.069(?![\d])"),           # 旧 ICHG 1.069A (300Ω 档)
    ("T122X", r"1\.22\s*[×x]"),                       # 旧 触点余量 1.22×
    ("T29M1", r"29\.20\s*min"),                     # 旧 充电时间 29.20min
    ("T3208", r"32\.08\s*min"),                   # 旧 充电时间 32.08min
    ("T29M2", r"(?<![\d.])29\s*min"),              # 旧 充电时间 29min
    ("T51M", r"(?<![\d.])51\s*min"),               # 旧 充电时间 51min
    ("TTSMV", r"14-32\s*mV"),                       # 旧 TS 参考地偏移 14-32mV
    ("TTSC", r"0\.44-0\.99"),                       # 旧 TS 等效温度偏差 0.44-0.99°C
]

# ── 语境豁免 (★历史留痕 / 本次订正标注 / 作废标记) ─────────────────────────────────
VOID_CTX = re.compile(r"作废|legacy_void|【历史留痕】|历史留痕")
ANNO_CTX = re.compile(r"ISS-384")

BLOCK_MARK = "ISS-384 充电电流活值订正块"

# ── 真值 (来自 MECH/HINGE_POWER_CALC.md §0-A.1 对照表 + rilim_table · [实测]) ───────
TRUTH_COEF_MAIN = 1.216
TRUTH_COEF_CV = 1.071
TRUTH_R = 680
TRUTH_ICHG = 0.697
TRUTH_PIN = 0.349
TRUTH_MARGIN = 1.43
TRUTH_TOKENS = ["1.216", "1.071", "0.697", "0.349", "1.43"]

TRUTH_PAGE = "HW/CHARGE_CURRENT_LIVE_VALUE_CALIBER.md"


def tokens_in(line):
    out = set()
    for code, pat in TOKEN_PATTERNS:
        if re.search(pat, line):
            out.add(code)
    return out


def read(path):
    with open(os.path.join(ROOT, path), "r", encoding="utf-8") as f:
        return f.read()


def check_scope(scan_paths):
    """★命门②: 扫描范围不许含落表真源/板文件 ⇒ 越界即红"""
    v = []
    for p in scan_paths:
        for pat, why in FORBIDDEN_SCOPE_PATTERNS:
            if pat.search(p):
                v.append({
                    "file": p, "line": 0, "code": "SCOPE",
                    "msg": "扫描范围越界: %s ⇒ %s (落表真源/板文件/别人地界不许被文档闸扫)" % (p, why),
                })
                break
    return v


def parse_corr_rows(lines, region_start):
    """★解析订正块里的逐处订正表 ⇒ {行号: {锚点码集合}} + 行号→cells"""
    rows = {}
    cells_map = {}
    for idx in range(region_start, len(lines)):
        raw = lines[idx].strip()
        m = re.match(r"^\|\s*(\d+)\s*\|", raw)
        if not m:
            continue
        cells = [c.strip() for c in re.split(r"(?<!\\)\|", raw.strip().strip("|"))]
        lineno = int(m.group(1))
        anchors = set(re.findall(r"\bT[A-Z0-9]{3,5}\b", cells[3] if len(cells) > 3 else ""))
        rows[lineno] = anchors
        cells_map[lineno] = cells
    return rows, cells_map


def analyze(docs, scan_paths, truth_text=None, truth_present=True):
    """docs: {relpath: text}; 返回 violation 列表"""
    v = []
    v += check_scope(scan_paths)

    for rel in scan_paths:
        if rel not in docs:
            continue
        lines = docs[rel].split("\n")

        # ── 定位订正块 ──
        region_start = None
        for i, ln in enumerate(lines):
            if BLOCK_MARK in ln:
                region_start = i
                break
        coverage = {}
        region_text = ""
        if region_start is None:
            v.append({"file": rel, "line": 0, "code": "NO_BLOCK",
                      "msg": "%s: 缺 ISS-384 充电电流活值订正块 ⇒ 活值无口径追平依据" % rel})
        else:
            coverage, cells_map = parse_corr_rows(lines, region_start)
            region_text = "\n".join(lines[region_start:])

            # ── 真值必须出现在订正块里 (命门③) ──
            for t in TRUTH_TOKENS:
                if t not in region_text:
                    v.append({"file": rel, "line": region_start + 1, "code": "NO_TRUTH",
                              "msg": "%s:%d: 订正块缺当前真值 `%s` (680Ω 档真值三数 0.697/0.349/1.43× "
                                     "或当前系数 1.216/1.071)" % (rel, region_start + 1, t)})

        # ── 逐行判定 ──
        for i, ln in enumerate(lines):
            lineno = i + 1
            toks = tokens_in(ln)
            if not toks:
                continue
            in_region = region_start is not None and i >= region_start
            if in_region:
                stripped = ln.strip()
                if stripped.startswith("|"):
                    continue           # 订正表自身 (旧值逐字是留痕) ⇒ 豁免
                if ANNO_CTX.search(ln) or VOID_CTX.search(ln):
                    continue           # 块内说明行 (含 ISS-384 或 作废/历史留痕) ⇒ 豁免
                v.append({"file": rel, "line": lineno, "code": "STRAY",
                          "msg": "%s:%d: 订正块内出现未登记的旧值 token %s ⇒ 判红"
                                 % (rel, lineno, "/".join(sorted(toks)))})
                continue
            # 区域外
            if VOID_CTX.search(ln):
                continue               # ★历史留痕 (ISS-230 作废标记) ⇒ 不红
            if ANNO_CTX.search(ln):
                continue               # ★本次订正标注行 ⇒ 不红
            if lineno in coverage:
                anchors = coverage[lineno]
                if not anchors:
                    v.append({"file": rel, "line": lineno, "code": "NO_ANCHOR",
                              "msg": "%s:%d: 该行含旧值 token %s 但订正表未给锚点 ⇒ 判红"
                                     % (rel, lineno, "/".join(sorted(toks)))})
                elif not toks.issubset(anchors):
                    extra = sorted(toks - anchors)
                    v.append({"file": rel, "line": lineno, "code": "UNREGISTERED",
                              "msg": "%s:%d: 该行出现锚点表之外的旧值 token %s ⇒ 判红"
                                     % (rel, lineno, "/".join(extra))})
            else:
                v.append({"file": rel, "line": lineno, "code": "LIVE_LEFTOVER",
                          "msg": "%s:%d: 旧系数/旧活值 token %s 未被订正 ⇒ 判红"
                                 % (rel, lineno, "/".join(sorted(toks)))})

        # ── 订正表自身必须与实际行对得上 (防「只登记不订正」+ 防行号位移) ──
        for lineno, anchors in coverage.items():
            if lineno < 1 or lineno > len(lines):
                v.append({"file": rel, "line": lineno, "code": "BAD_LINENO",
                          "msg": "%s: 订正表登记的行号 %d 越界 ⇒ 判红" % (rel, lineno)})
                continue
            if not anchors:
                continue                 # 说明行 (锚点列 = —) ⇒ 不校验 token
            line_toks = tokens_in(lines[lineno - 1])
            if not line_toks:
                v.append({"file": rel, "line": lineno, "code": "STALE_ROW",
                          "msg": "%s:%d: 订正表登记了该行但该行已无旧值 token ⇒ 订正表与实际行不符"
                                 % (rel, lineno)})
            elif not line_toks.issubset(anchors):
                v.append({"file": rel, "line": lineno, "code": "STALE_ROW",
                          "msg": "%s:%d: 该行旧值 token %s 与订正表锚点 %s 不符 ⇒ 判红"
                                 % (rel, lineno, "/".join(sorted(line_toks)),
                                    "/".join(sorted(anchors)))})

    # ── 真相页 (机器块) ──
    if not truth_present:
        v.append({"file": TRUTH_PAGE, "line": 0, "code": "NO_TRUTH_PAGE",
                  "msg": "%s: 真相页缺失 ⇒ 判红" % TRUTH_PAGE})
    elif truth_text is not None:
        v += check_truth_page(truth_text)

    return v


def parse_machine_block(text):
    """解析真相页机器块 (手写小解析器, 不引第三方依赖)"""
    res = {"coef_main": None, "coef_cv": None, "rilim": {}}
    cur = None
    in_block = False
    for ln in text.split("\n"):
        if ln.strip().startswith("```"):
            in_block = not in_block
            continue
        if not in_block:
            continue
        if "charge_current_live_value:" in ln:
            continue
        m = re.match(r"^\s*-?\s*r_ohm\s*:\s*([0-9.]+)", ln)
        if m:
            cur = int(float(m.group(1)))
            res["rilim"][cur] = {}
            continue
        m = re.match(r"^\s*coef_main\s*:\s*([0-9.]+)", ln)
        if m:
            res["coef_main"] = float(m.group(1))
            continue
        m = re.match(r"^\s*coef_cv\s*:\s*([0-9.]+)", ln)
        if m:
            res["coef_cv"] = float(m.group(1))
            continue
        if cur is not None:
            m = re.match(r"^\s*(ichg_max|per_pin_max|margin_to_0p5A)\s*:\s*([0-9.]+)", ln)
            if m:
                res["rilim"][cur][m.group(1)] = float(m.group(2))
    return res


def check_truth_page(text):
    v = []
    for sec in ("## §0", "## §1", "## §2", "## §3", "## §4", "## §5"):
        if sec not in text:
            v.append({"file": TRUTH_PAGE, "line": 0, "code": "TRUTH_SEC",
                      "msg": "%s: 缺章节 `%s` ⇒ 判红" % (TRUTH_PAGE, sec)})
    if "charge_current_live_value:" not in text:
        v.append({"file": TRUTH_PAGE, "line": 0, "code": "TRUTH_BLOCK",
                  "msg": "%s: 缺机器块 `charge_current_live_value:` ⇒ 判红" % TRUTH_PAGE})
        return v
    mb = parse_machine_block(text)
    if mb["coef_main"] is None or abs(mb["coef_main"] - TRUTH_COEF_MAIN) > 1e-6:
        v.append({"file": TRUTH_PAGE, "line": 0, "code": "TRUTH_COEF",
                  "msg": "%s: 机器块 coef_main 应为 %s, 实为 %s ⇒ 判红"
                         % (TRUTH_PAGE, TRUTH_COEF_MAIN, mb["coef_main"])})
    if mb["coef_cv"] is None or abs(mb["coef_cv"] - TRUTH_COEF_CV) > 1e-6:
        v.append({"file": TRUTH_PAGE, "line": 0, "code": "TRUTH_COEF",
                  "msg": "%s: 机器块 coef_cv 应为 %s, 实为 %s ⇒ 判红"
                         % (TRUTH_PAGE, TRUTH_COEF_CV, mb["coef_cv"])})
    r = mb["rilim"].get(TRUTH_R)
    if not r:
        v.append({"file": TRUTH_PAGE, "line": 0, "code": "TRUTH_RILIM",
                  "msg": "%s: 机器块缺 %dΩ 档 ⇒ 判红" % (TRUTH_PAGE, TRUTH_R)})
    else:
        for key, want in (("ichg_max", TRUTH_ICHG), ("per_pin_max", TRUTH_PIN),
                          ("margin_to_0p5A", TRUTH_MARGIN)):
            got = r.get(key)
            if got is None or abs(got - want) > 1e-6:
                v.append({"file": TRUTH_PAGE, "line": 0, "code": "TRUTH_RILIM",
                          "msg": "%s: 机器块 %dΩ 的 %s 应为 %s, 实为 %s ⇒ 判红"
                                 % (TRUTH_PAGE, TRUTH_R, key, want, got)})
    return v


# ────────────────────────────── 自测 ───────────────────────────────────────────────
def _mutate_line(lines, lineno, fn):
    out = list(lines)
    out[lineno - 1] = fn(out[lineno - 1])
    return "\n".join(out)


def _drop_block(text):
    lines = text.split("\n")
    for i, ln in enumerate(lines):
        if BLOCK_MARK in ln:
            return "\n".join(lines[:i])
    return text


def selftest():
    docs = {}
    for rel in SCAN_DOCS:
        docs[rel] = read(rel)
    truth_present = os.path.exists(os.path.join(ROOT, TRUTH_PAGE))
    truth_text = read(TRUTH_PAGE) if truth_present else None

    results = []

    def case(name, cond, detail=""):
        results.append((name, bool(cond), detail))
        print("  [%s] %s%s" % ("PASS" if cond else "FAIL", name,
                               ("" if cond else "  <<< " + detail)))

    # T1 基线: 三份文档 + 真相页 现状必须全过
    v = analyze(docs, list(SCAN_DOCS), truth_text, truth_present)
    case("T1 基线: 现状零违规", not v, "违规: %s" % v[:2])

    pcb = "HW/PCB_OUTLINE_60x15.md"
    jchg = "HW/J_CHG_SELECTION.md"

    # T2 ★命门① 反向: 删掉 L151 的作废标记 ⇒ 必须变红
    d2 = dict(docs)
    lines = docs[pcb].split("\n")
    d2[pcb] = _mutate_line(lines, 151, lambda s: s.replace("作废", "已废弃"))
    v = analyze(d2, list(SCAN_DOCS), truth_text, truth_present)
    case("T2 命门① 反向: 删 L151 作废标记 ⇒ 变红",
         any(x["file"] == pcb and x["line"] == 151 for x in v), str(v[:2]))

    # T3 ★命门① 反向: 删掉 L193 的作废标记 ⇒ 必须变红
    d3 = dict(docs)
    lines = docs[pcb].split("\n")
    d3[pcb] = _mutate_line(lines, 193, lambda s: s.replace("作废", "已废弃"))
    v = analyze(d3, list(SCAN_DOCS), truth_text, truth_present)
    case("T3 命门① 反向: 删 L193 作废标记 ⇒ 变红",
         any(x["file"] == pcb and x["line"] == 193 for x in v), str(v[:2]))

    # T4 ★命门② 反向: 把网表加进扫描范围 ⇒ 必须变红
    v = analyze(docs, list(SCAN_DOCS) + ["HW/netlist_v1.csv"], truth_text, truth_present)
    case("T4 命门② 反向: 扫描范围加网表 ⇒ 变红",
         any(x["code"] == "SCOPE" and "netlist_v1.csv" in x["msg"] for x in v), str(v[:2]))

    # T5 ★命门② 反向: 把脚表/BOM 加进扫描范围 ⇒ 必须变红
    v = analyze(docs, list(SCAN_DOCS) + ["HW/netlist_v1_pins.csv", "HW/BOM_v1.csv"],
                truth_text, truth_present)
    case("T5 命门② 反向: 扫描范围加脚表/BOM ⇒ 变红",
         len([x for x in v if x["code"] == "SCOPE"]) == 2, str(v[:3]))

    # T6 ★命门② 反向: 把板文件加进扫描范围 ⇒ 必须变红
    v = analyze(docs, list(SCAN_DOCS) + ["HW/PCB/demo_mainboard.kicad_pcb"],
                truth_text, truth_present)
    case("T6 命门② 反向: 扫描范围加板文件 ⇒ 变红",
         any(x["code"] == "SCOPE" for x in v), str(v[:2]))

    # T7 活值残留: 在已订正行上偷偷塞一个未登记的旧值 token ⇒ 必须变红
    d7 = dict(docs)
    lines = docs[pcb].split("\n")
    d7[pcb] = _mutate_line(lines, 20, lambda s: s + "  (旁注 0.822A)")
    v = analyze(d7, list(SCAN_DOCS), truth_text, truth_present)
    case("T7 活值残留: 已订正行塞入未登记旧值 ⇒ 变红",
         any(x["file"] == pcb and x["line"] == 20 for x in v), str(v[:2]))

    # T8 订正块整体丢失 ⇒ 旧活值全部暴露 ⇒ 变红
    d8 = dict(docs)
    d8[jchg] = _drop_block(docs[jchg])
    v = analyze(d8, list(SCAN_DOCS), truth_text, truth_present)
    case("T8 订正块丢失 ⇒ 变红",
         any(x["file"] == jchg and x["code"] == "LIVE_LEFTOVER" for x in v), str(v[:2]))

    # T9 ★命门③ 反向: 订正块里抹掉真值三数 ⇒ 必须变红
    d9 = dict(docs)
    d9[pcb] = docs[pcb].replace("1.43", "X.XX")
    v = analyze(d9, list(SCAN_DOCS), truth_text, truth_present)
    case("T9 命门③ 反向: 订正块缺真值 ⇒ 变红",
         any(x["code"] == "NO_TRUTH" for x in v), str(v[:2]))

    # T10 真相页机器块被改坏 ⇒ 变红
    d10_truth = truth_text.replace("ichg_max: 0.697", "ichg_max: 0.822", 1)
    v = analyze(docs, list(SCAN_DOCS), d10_truth, True)
    case("T10 真相页机器块被改坏 ⇒ 变红",
         any(x["code"] == "TRUTH_RILIM" for x in v), str(v[:2]))

    # T11 真相页缺失 ⇒ 变红
    v = analyze(docs, list(SCAN_DOCS), None, False)
    case("T11 真相页缺失 ⇒ 变红",
         any(x["code"] == "NO_TRUTH_PAGE" for x in v), str(v[:2]))

    # T12 订正表登记的行号与实际行不符 (行号位移) ⇒ 变红
    d12 = dict(docs)
    d12[jchg] = docs[jchg].replace("\n| 32 | ", "\n| 33 | ", 1)
    v = analyze(d12, list(SCAN_DOCS), truth_text, truth_present)
    case("T12 订正表行号与实际行不符 ⇒ 变红",
         any(x["code"] in ("STALE_ROW", "LIVE_LEFTOVER") and x["file"] == jchg for x in v),
         str(v[:3]))

    # T13 订正表锚点被改小 (只登记一个 token) ⇒ 变红
    d13 = dict(docs)
    d13[jchg] = docs[jchg].replace("| T0822 / T0411 |", "| T0411 |", 1)
    v = analyze(d13, list(SCAN_DOCS), truth_text, truth_present)
    case("T13 订正表锚点不全 ⇒ 变红",
         any(x["code"] == "UNREGISTERED" for x in v), str(v[:3]))

    # T14 真相页缺章节 ⇒ 变红
    v = analyze(docs, list(SCAN_DOCS), (truth_text or "").replace("## §3", "## X3"), True)
    case("T14 真相页缺章节 ⇒ 变红",
         any(x["code"] == "TRUTH_SEC" for x in v), str(v[:2]))

    print("-" * 70)
    npass = sum(1 for _, ok, _ in results if ok)
    print("selftest: %d/%d 通过" % (npass, len(results)))
    if npass != len(results):
        print("SELFTEST FAILED")
        return 1
    print("ALL TESTS PASS")
    return 0


def main(argv):
    as_json = "--json" in argv
    if "--selftest" in argv:
        return selftest()
    docs = {}
    for rel in SCAN_DOCS:
        p = os.path.join(ROOT, rel)
        if os.path.exists(p):
            docs[rel] = read(rel)
    truth_present = os.path.exists(os.path.join(ROOT, TRUTH_PAGE))
    truth_text = read(TRUTH_PAGE) if truth_present else None
    v = analyze(docs, list(SCAN_DOCS), truth_text, truth_present)
    if as_json:
        print(json.dumps({"ok": not v, "violations": v}, ensure_ascii=False, indent=1))
        return 1 if v else 0
    if not v:
        print("✅ rc=0: 三份 HW 活文档的充电电流活值已追平到 680Ω 落表真值 (ISS-384)")
        print("   · 旧系数 0.822 / 0.411A / 1.22× 等旧活值: 已全部被订正块覆盖或已标作废")
        print("   · 真值: 680Ω → ICHG 0.697A / 单 pin 0.349A / 余量 1.43× · 系数 1.216 @3.70V / 1.071 @4.20V")
        print("   · 历史留痕 (ISS-230 作废标记 L151/L193): 未误伤")
        print("   · 扫描范围: %s (不含网表/脚表/BOM/板文件 ⇒ 零落表零写板)" % ", ".join(SCAN_DOCS))
        print("   · 本闸零挂链 (grep -c check_charge_current_live_value state/gate_check.py = 0)")
        return 0
    print("❌ rc=1: 充电电流活值口径不合格 (%d 条)" % len(v))
    for x in v:
        print("   [%s] %s" % (x["code"], x["msg"]))
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
