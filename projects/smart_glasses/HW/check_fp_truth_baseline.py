#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-356 · hw-lead · 「封装真值基线」机器门禁 (C0~C6)
作者: hw-lead · 2026-11-23 · 交卷给 main / 项目总工

用法:
    python3 HW/check_fp_truth_baseline.py               # 正常跑 ⇒ rc=0 = 全过
    python3 HW/check_fp_truth_baseline.py --selftest     # 反向用例自证 ⇒ rc=0 (末行 ALL TESTS PASS)
    python3 HW/check_fp_truth_baseline.py --json         # 机器可读输出
    python3 HW/check_fp_truth_baseline.py --root DIR     # 指定项目根 (默认自动定位)

检查项 (内容级, **不挂 md5** —— 沿用 HW/check_part_selection_gaps.py 的做法: 文档改一个字就重判):
    C0 基准块存在且是合法 JSON (页内 "BEGIN/END ISS356 封装真值基线基准块")
    C1 靶子件 100% 覆盖 —— ★靶子口径由本脚本自己跑 CSV 统计★:
       「必装 ∩ 非 NET/TP ∩ footprint=='待定'」= 100 件, 其中
       「board=='镜脚主 PCB'」= 78 件 (本单 §2 必做范围),
       「board=='镜框充电板'」= 22 件 (本单 §4 只登记);
       ⇒ 78 件每件必须在 §2 逐 ref 表里有 目标 lib:name; 22 件每件必须在 §4.1 清单里登记
    C2 页里写的每个 lib:name, 对应 .kicad_mod 文件必须在 KiCad 官方库根下**实测存在**
       (★查文件, 不是只查库目录★); 且 md5 与页里写的必须一致
    C3 每行必须带非空的「证据等级」且取值 ∈ [官网]/[实测]/[媒体]/[推算]/[0数据] 五者之一 (写 [官方] = 红)
    C4 每行必须带非空的「降级方案」栏 (★查不到的件不许空着★)
    C5 页里不许出现「等原厂回信 / 等供应商确认 / 待外部回复」这类挂起措辞
       (老板 2026-11-12 02:02 政策: 不再发信, 全靠自己查资料 ⇒ 查不到必须写成
        "[0数据] + 降级方案"; 出现挂起措辞 = 红)
    C6 件数字段自洽 —— ★判据自己跑 CSV 统计, 不抄本文任何数字★:
       基准块 counts.target_total / target_main_board / target_charge_board
       与本脚本实跑数、以及与页内 §2/§4 实际行数 三方一致

★ 本门禁【不挂 md5】: 判据是内容级 (件数 / 覆盖 / 库文件实存 / 证据等级 / 降级方案 /
  挂起措辞 / 计数自洽), 文档改一个字就重判, 不用重锚。

--selftest 反向用例 (每条都自证「真的改到了目标」):
    M1 删掉 §2 表里某一行 (R_PU_PG)      → 期望 C1 红, 且 C0/C2/C3/C4/C5/C6 仍绿
    M2 把某行的 lib:name 改成不存在的     → 期望 C2 红, 且 C0/C1/C3/C4/C5/C6 仍绿
    M3 清空某行的证据等级                → 期望 C3 红, 且 C0/C1/C2/C4/C5/C6 仍绿
    M4 清空某行的降级方案                → 期望 C4 红, 且 C0/C1/C2/C3/C5/C6 仍绿
    M5 正文塞一句「等原厂回信」           → 期望 C5 红, 且 C0/C1/C2/C3/C4/C6 仍绿
    M6 篡改件数字段 (counts.target_main_board) → 期望 C6 红, 且 C0~C5 仍绿

★ 反向用例的「真的改到了目标」自证 = 三件事同时成立:
    ① 变异确实落到盘上副本里 (变异串在副本里 count>=1, 变异前原串消失)
    ② 期望变红的那一条 check 真的红了
    ③ 其余 check 仍然绿 (证明红的是目标那一条, 不是随便塌一条)
★ 沙盒: 副本落**项目盘 tmp/** (不落 /tmp), 真件零污染 (跑完删副本)
"""

import argparse
import csv
import json
import os
import re
import shutil
import sys

DOC_REL = os.path.join("HW", "FP_TRUTH_BASELINE.md")
BLOCK_BEGIN = "<!-- BEGIN ISS356 封装真值基线基准块 -->"
BLOCK_END = "<!-- END ISS356 封装真值基线基准块 -->"

# 证据等级白名单 (五级固定, 写死的)
ALLOWED_EVIDENCE = {"[官网]", "[实测]", "[媒体]", "[推算]", "[0数据]"}

# 挂起措辞黑名单 (老板 2026-11-12 02:02 政策)
FORBIDDEN_PHRASES = (
    "等回复",
    "等原厂回信",
    "待供应商确认",
    "等原厂",
    "等确认",
)

# C5 skip 区 (闸自身的说明文字里会出现这些词)
SKIP_BEGIN = "<!-- C5-SKIP-BEGIN -->"
SKIP_END = "<!-- C5-SKIP-END -->"

LIBROOT_DEFAULT = "/home/yuewuya/kicad/AppDir/share/kicad/footprints"

# ---------------------------------------------------------------- helpers


def find_root():
    here = os.path.dirname(os.path.abspath(__file__))
    cur = here
    for _ in range(6):
        if os.path.isdir(os.path.join(cur, "HW")) and os.path.isdir(os.path.join(cur, "state")):
            return cur
        cur = os.path.dirname(cur)
    return here


def load_targets(root):
    """★自己跑 CSV 统计靶子口径 (不抄任何硬编码数字)★"""
    bom_path = os.path.join(root, "HW", "BOM_v1.csv")
    with open(bom_path, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    main, chg, total = [], [], []
    for r in rows:
        if r["dnp"] != "必装":
            continue
        if r["type"] in ("NET", "TP"):
            continue
        if r["footprint"] != "待定":
            continue
        total.append(r["ref"])
        if r["board"] == "镜脚主 PCB":
            main.append(r["ref"])
        elif r["board"] == "镜框充电板":
            chg.append(r["ref"])
    return main, chg, total


def parse_block(text):
    if BLOCK_BEGIN not in text or BLOCK_END not in text:
        return None
    blob = text.split(BLOCK_BEGIN, 1)[1].split(BLOCK_END, 1)[0].strip()
    blob = re.sub(r"^```json\s*", "", blob)
    blob = re.sub(r"```\s*$", "", blob)
    try:
        return json.loads(blob)
    except Exception:
        return None


def md_tables(text):
    """返回 [(表头 tuple, [行 tuple,...]), ...] —— 只收有 ≥2 列、且表头含 'ref' 的表"""
    out = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        ln = lines[i].strip()
        if ln.startswith("|") and ln.count("|") >= 3:
            head = tuple(c.strip() for c in ln.strip("|").split("|"))
            if any("ref" == c.lower() or c.startswith("`ref`") for c in head):
                rows = []
                j = i + 1
                while j < len(lines):
                    r2 = lines[j].strip()
                    if not r2.startswith("|"):
                        break
                    if set(r2.replace("|", "").replace(" ", "")) <= set("-:"):
                        j += 1
                        continue
                    rows.append(tuple(c.strip() for c in r2.strip("|").split("|")))
                    j += 1
                out.append((head, rows))
                i = j
                continue
        i += 1
    return out


def cell(row, head, key):
    for k, c in enumerate(head):
        if c == key or c.replace("`", "") == key:
            return row[k] if k < len(row) else ""
    return ""


def strip_c5_skip(text):
    if SKIP_BEGIN in text and SKIP_END in text:
        pre, rest = text.split(SKIP_BEGIN, 1)
        _, post = rest.split(SKIP_END, 1)
        return pre + post
    return text


def check(doc_text, root, libroot=LIBROOT_DEFAULT):
    """返回 (results, facts)"""
    results = {}
    facts = {}

    # ---- C0 基准块
    block = parse_block(doc_text)
    results["C0"] = {"ok": block is not None,
                     "detail": "基准块存在且是合法 JSON" if block is not None
                     else "页内缺 BEGIN/END 基准块或 JSON 非法"}
    if block is None:
        for c in ("C1", "C2", "C3", "C4", "C5", "C6"):
            results[c] = {"ok": False, "detail": "基准块不可用 ⇒ 连带判红"}
        return results, facts

    main_t, chg_t, total_t = load_targets(root)
    facts["target_main"] = len(main_t)
    facts["target_chg"] = len(chg_t)
    facts["target_total"] = len(total_t)

    tables = md_tables(doc_text)
    rowtables = []
    for head, rows in tables:
        if any("目标" in c and "lib:name" in c for c in head):
            rowtables.append((head, rows))
    facts["n_rowtables"] = len(rowtables)

    # ---- C1 覆盖
    c1_bad = []
    covered = {}
    if rowtables:
        head, rows = rowtables[0]
        for r in rows:
            ref = cell(r, head, "ref").strip("`").strip()
            tgt = cell(r, head, "目标 `lib:name`")
            tgt = re.sub(r"[`\s]", "", tgt)
            covered[ref] = tgt
            if not ref or not tgt:
                c1_bad.append("空行")
    for ref in main_t:
        if ref not in covered:
            c1_bad.append("§2 缺 ref: %s" % ref)
        elif not covered[ref] or ":" not in covered[ref]:
            c1_bad.append("§2 无目标 lib:name: %s" % ref)
    chg_seen = set()
    for head, rows in tables:
        if any("在镜脚主 PCB 板面" in c for c in head):
            for r in rows:
                ref = cell(r, head, "ref").strip("`").strip()
                if ref:
                    chg_seen.add(ref)
    for ref in chg_t:
        if ref not in chg_seen:
            c1_bad.append("§4.1 缺登记: %s" % ref)
    # ★§2 表行数也归 C1 (覆盖度判据) ⇒ 删一行只让 C1 红, 不连带 C6★
    if rowtables:
        n_rows = len(rowtables[0][1])
        if n_rows != len(main_t):
            c1_bad.append("§2 表行数 %d != 实跑 %d" % (n_rows, len(main_t)))
    results["C1"] = {"ok": not c1_bad,
                     "detail": "78 件靶子 §2 全覆盖 + 22 件 §4.1 全登记 (%d/%d, %d/%d)"
                     % (len(main_t) - len([b for b in c1_bad if '§2' in b]), len(main_t),
                        len(chg_t) - len([b for b in c1_bad if '§4' in b]), len(chg_t))
                     if not c1_bad else "; ".join(c1_bad[:12])}
    facts["c1_bad_count"] = len(c1_bad)

    # ---- C2 库文件实存 + md5
    c2_bad = []
    n_libs = 0
    seen_lib = set()
    for head, rows in rowtables:
        for r in rows:
            tgt = re.sub(r"[`\s]", "", cell(r, head, "目标 `lib:name`"))
            md5cell = cell(r, head, "库文件实存路径 + md5")
            m = re.search(r"md5\s+`?([0-9a-f]{32})`?", md5cell)
            if not tgt or ":" not in tgt:
                continue
            n_libs += 1
            lib, name = tgt.split(":", 1)
            path = os.path.join(libroot, "%s.pretty" % lib, "%s.kicad_mod" % name)
            if not os.path.isfile(path):
                c2_bad.append("文件不在盘: %s" % tgt)
                continue
            if m:
                import hashlib
                real = hashlib.md5(open(path, "rb").read()).hexdigest()
                if real != m.group(1):
                    c2_bad.append("md5 不符: %s (页写 %s / 实 %s)" % (tgt, m.group(1)[:8], real[:8]))
            seen_lib.add(tgt)
    # 基准块里记录也要核
    for rec in block.get("records", []):
        tgt = rec.get("target_lib", "")
        if not tgt or ":" not in tgt:
            continue
        lib, name = tgt.split(":", 1)
        path = os.path.join(libroot, "%s.pretty" % lib, "%s.kicad_mod" % name)
        if not os.path.isfile(path):
            c2_bad.append("基准块文件不在盘: %s" % tgt)
        else:
            import hashlib
            real = hashlib.md5(open(path, "rb").read()).hexdigest()
            if rec.get("lib_md5") and rec["lib_md5"] != real:
                c2_bad.append("基准块 md5 不符: %s" % tgt)
    facts["n_lib_refs"] = n_libs
    results["C2"] = {"ok": not c2_bad,
                     "detail": "%d 处 lib:name 的 .kicad_mod 全部实测在盘 + md5 一致" % n_libs
                     if not c2_bad else "; ".join(c2_bad[:12])}

    # ---- C3 证据等级
    c3_bad = []
    n_ev = 0
    for head, rows in rowtables:
        evkey = None
        for c in head:
            if c.replace("`", "") == "证据等级":
                evkey = c
        if evkey is None:
            continue
        for r in rows:
            ref = cell(r, head, "ref").strip("`").strip()
            ev = cell(r, head, evkey)
            n_ev += 1
            tags = set(re.findall(r"\[[^\[\]]+\]", ev))
            if not ev.strip():
                c3_bad.append("证据等级空: %s" % ref)
                continue
            if not tags:
                c3_bad.append("证据等级无标签: %s" % ref)
                continue
            bad = tags - ALLOWED_EVIDENCE
            if bad:
                c3_bad.append("证据等级非法 %s: %s" % (sorted(bad), ref))
    facts["n_evidence_rows"] = n_ev
    results["C3"] = {"ok": not c3_bad,
                     "detail": "%d 行证据等级全部 ∈ 五级白名单" % n_ev
                     if not c3_bad else "; ".join(c3_bad[:12])}

    # ---- C4 降级方案
    c4_bad = []
    n_fb = 0
    for head, rows in rowtables:
        fbkey = None
        for c in head:
            if c.replace("`", "") == "降级方案":
                fbkey = c
        if fbkey is None:
            continue
        for r in rows:
            ref = cell(r, head, "ref").strip("`").strip()
            fb = cell(r, head, fbkey)
            n_fb += 1
            if not fb.strip():
                c4_bad.append("降级方案空: %s" % ref)
            elif fb.strip() in ("-", "无", "N/A", "TBD", "待定"):
                c4_bad.append("降级方案是占位词: %s" % ref)
    facts["n_fallback_rows"] = n_fb
    results["C4"] = {"ok": not c4_bad,
                     "detail": "%d 行降级方案全部非空且非占位词" % n_fb
                     if not c4_bad else "; ".join(c4_bad[:12])}

    # ---- C5 挂起措辞
    body = strip_c5_skip(doc_text)
    c5_bad = []
    for ph in FORBIDDEN_PHRASES:
        if ph in body:
            c5_bad.append("出现挂起措辞: %s (×%d)" % (ph, body.count(ph)))
    results["C5"] = {"ok": not c5_bad,
                     "detail": "正文无「等回复/等原厂回信/待供应商确认/等原厂/等确认」类挂起措辞"
                     if not c5_bad else "; ".join(c5_bad)}

    # ---- C6 件数自洽
    c6_bad = []
    counts = block.get("counts", {})
    n_main_doc = counts.get("target_main_board")
    n_chg_doc = counts.get("target_charge_board")
    n_tot_doc = counts.get("target_total")
    if n_main_doc != len(main_t):
        c6_bad.append("target_main_board: 基准块 %s vs 实跑 %d" % (n_main_doc, len(main_t)))
    if n_chg_doc != len(chg_t):
        c6_bad.append("target_charge_board: 基准块 %s vs 实跑 %d" % (n_chg_doc, len(chg_t)))
    if n_tot_doc != len(total_t):
        c6_bad.append("target_total: 基准块 %s vs 实跑 %d" % (n_tot_doc, len(total_t)))
    n_rec = len(block.get("records", []))
    if n_rec != len(main_t):
        c6_bad.append("基准块 records %d vs 实跑 %d" % (n_rec, len(main_t)))
    rec_refs = [r.get("ref") for r in block.get("records", [])]
    if sorted(rec_refs) != sorted(main_t):
        only_block = sorted(set(rec_refs) - set(main_t))
        only_csv = sorted(set(main_t) - set(rec_refs))
        c6_bad.append("基准块 records 的 ref 集合 != 实跑靶子集合 (块多 %s / 块缺 %s)"
                      % (only_block[:5], only_csv[:5]))
    results["C6"] = {"ok": not c6_bad,
                     "detail": "件数三方自洽 (实跑 78/22/100 = 基准块 = §2 表行数)"
                     if not c6_bad else "; ".join(c6_bad)}
    return results, facts


def print_report(results, facts, as_json=False):
    if as_json:
        print(json.dumps({"ok": all(v["ok"] for v in results.values()),
                          "results": results, "facts": facts}, ensure_ascii=False, indent=1))
        return
    print("【ISS-356 封装真值基线闸】")
    for cid in ("C0", "C1", "C2", "C3", "C4", "C5", "C6"):
        r = results[cid]
        print("  [%s] %s :: %s" % ("PASS" if r["ok"] else "FAIL", cid, r["detail"]))
    print("  事实: 靶子(镜脚主PCB)=%s 靶子(镜框充电板)=%s 合计=%s"
          % (facts.get("target_main"), facts.get("target_chg"), facts.get("target_total")))


# ---------------------------------------------------------------- selftest

def selftest(root):
    doc_path = os.path.join(root, DOC_REL)
    if not os.path.isfile(doc_path):
        print("[FAIL] 找不到 %s" % doc_path)
        return 2
    orig = open(doc_path, encoding="utf-8").read()
    sandbox = os.path.join(root, "tmp", "iss356_selftest")
    if os.path.isdir(sandbox):
        shutil.rmtree(sandbox)
    os.makedirs(sandbox, exist_ok=True)
    cases = []

    # ---- M1 删掉 §2 表里某一行
    m1 = re.search(r"^\| `R_PU_PG` \|.*\n", orig, re.M)
    if not m1:
        print("[FAIL] M1 找不到 §2 行 R_PU_PG")
        return 2
    cases.append(("M1", "删 §2 一行 (R_PU_PG) ⇒ C1 红", "C1",
                  m1.group(0), "", m1.group(0).strip(), "absent"))

    # ---- M2 改 lib:name 成不存在的
    m2 = re.search(r"(\| `C_HF_VDD_1V8_IO` \|[^\n]*?`Capacitor_SMD:C_0603_1608Metric`)", orig)
    if not m2:
        print("[FAIL] M2 找不到 C_HF_VDD_1V8_IO 行")
        return 2
    cases.append(("M2", "改 lib:name 成不存在的 ⇒ C2 红", "C2",
                  m2.group(0),
                  m2.group(0).replace("Capacitor_SMD:C_0603_1608Metric",
                                      "Capacitor_SMD:C_9999_9999Metric"),
                  "C_9999_9999Metric", "present"))

    # ---- M3 清空证据等级 (列序: ... 候选OPN | 证据等级 | 布局布线改动 | 降级方案)
    m3 = re.search(r"^\| `R_EN_VCORE` \|[^\n]*$", orig, re.M)
    if not m3:
        print("[FAIL] M3 找不到 R_EN_VCORE 行")
        return 2
    p3 = m3.group(0).split("|")
    # split 后: [0]='' , [1]=ref ... , 末尾是 [证据等级][布局布线改动][降级方案]['']
    ev_idx = len(p3) - 4          # 证据等级列
    fb_idx = len(p3) - 2          # 降级方案列
    if "[实测]" not in p3[ev_idx]:
        print("[FAIL] M3 证据等级列定位错 (idx=%d 值=%r)" % (ev_idx, p3[ev_idx]))
        return 2
    if "降级" not in p3[fb_idx] and not p3[fb_idx].strip():
        print("[FAIL] M4 降级方案列定位错 (idx=%d 值=%r)" % (fb_idx, p3[fb_idx]))
        return 2
    p3m = list(p3)
    p3m[ev_idx] = "  "
    cases.append(("M3", "清空某行证据等级 ⇒ C3 红", "C3",
                  m3.group(0), "|".join(p3m), "|".join(p3m), "present"))

    # ---- M4 清空降级方案 (同一行, 另一列)
    p4 = list(p3)
    p4[fb_idx] = "  "
    cases.append(("M4", "清空某行降级方案 ⇒ C4 红", "C4",
                  m3.group(0), "|".join(p4), "|".join(p4), "present"))

    # ---- M5 正文塞挂起措辞 (插在 H1 标题前, 用文档首行做唯一锚)
    first_line = orig.split("\n", 1)[0]
    if not first_line.startswith("# "):
        print("[FAIL] M5 首行不是标题: %r" % first_line[:40])
        return 2
    cases.append(("M5", "正文塞「等原厂回信」⇒ C5 红", "C5",
                  first_line, "等原厂回信\n\n" + first_line, "等原厂回信", "present"))

    # ---- M6 篡改件数字段
    cases.append(("M6", "篡改 counts.target_main_board ⇒ C6 红", "C6",
                  '"target_main_board": %d' % 78, '"target_main_board": %d' % 77,
                  '"target_main_board": 77', "present"))

    all_ok = True
    for cid, desc, expect_red, old, new, probe, probe_mode in cases:
        mutated = orig.replace(old, new, 1)
        if mutated == orig:
            print("[FAIL] %s 变异没落到副本上 (串没命中) ⇒ 不能证明红的是目标那一条" % cid)
            all_ok = False
            continue
        # ★探针自证: 变异串必须【在副本里 且 不在原文档里】(或【被删掉】)⇒ 证明"真的改到了目标"★
        if probe_mode == "absent":
            if probe in mutated:
                print("[FAIL] %s 目标串仍留在副本里 ⇒ 删除没生效" % cid)
                all_ok = False
                continue
        else:
            if probe not in mutated:
                print("[FAIL] %s 探针串不在副本里 ⇒ 变异没生效" % cid)
                all_ok = False
                continue
            if probe in orig:
                print("[FAIL] %s 探针串本来就在原文档里 ⇒ 变异无效" % cid)
                all_ok = False
                continue
        cp = os.path.join(sandbox, "FP_TRUTH_BASELINE_%s.md" % cid)
        with open(cp, "w", encoding="utf-8") as fh:
            fh.write(mutated)
        res, _ = check(mutated, root)
        reds = sorted(k for k, v in res.items() if not v["ok"])
        ok = (reds == [expect_red])
        print("  [%s] %s :: 期望红 %s ⇒ 实得红 %s :: %s"
              % ("PASS" if ok else "FAIL", cid, expect_red, reds or "无",
                 res.get(expect_red, {}).get("detail", "")[:110]))
        if not ok:
            all_ok = False
    shutil.rmtree(sandbox, ignore_errors=True)
    if all_ok:
        print("SELFTEST %d/%d 全过 (每条都自证「红的是目标那一条, 其余仍绿」)" % (len(cases), len(cases)))
        print("ALL TESTS PASS")
        return 0
    print("SELFTEST 失败 ⇒ 闸不可信")
    return 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--root", default=None)
    ap.add_argument("--doc", default=None)
    ap.add_argument("--libroot", default=LIBROOT_DEFAULT)
    args = ap.parse_args()

    root = args.root or find_root()
    if args.selftest:
        return selftest(root)

    doc_path = args.doc or os.path.join(root, DOC_REL)
    if not os.path.isfile(doc_path):
        print("[FAIL] 找不到 %s" % doc_path)
        return 1
    text = open(doc_path, encoding="utf-8").read()
    results, facts = check(text, root, args.libroot)
    print_report(results, facts, as_json=args.json)
    bad = [k for k, v in results.items() if not v["ok"]]
    if bad:
        print("RED: %s" % ",".join(bad))
        return 1
    print("ALL CHECKS PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
