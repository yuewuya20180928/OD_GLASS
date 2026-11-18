#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
probe_sch_src_diff.py —— ISS-311 自证探针 (hw-lead)
★**只读**: 不写任何文件 (只往 stdout 打)
★**目的**: 把 chain_gate 的「原理图源文件与 HW/PCB/ 内容不一致 11 个」展开成逐文件证据:
  · md5 (源 vs 投产包)
  · 归一化指纹 sha256 (去 uuid / 去时间戳 / 去 generator/rev 串) —— ★**照 ISS-256 口径** ★
  · 归一化后是否一致 (⇒ uuid 抖动 vs 真内容差异)
  · 差异行数 (原文 diff 行数 + 归一化后 diff 行数)
★**口径单一真源**: 直接 import `state/check_chain_content_anchor.py` 的 `normalize_sch_text()` ⇒ 零漂移 ★

用法:
  python3 logs/iss311/probe_sch_src_diff.py
"""
import difflib
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(PROJ, "state"))

import check_chain_content_anchor as CA  # noqa: E402

SRC_DIR = os.path.join(PROJ, "HW", "PCB")
DST_DIR = os.path.join(PROJ, "HW", "PCB", "production", "doc", "sch_src")


def md5_file(p):
    with open(p, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def sha_text(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def main():
    print("=" * 100)
    print("ISS-311 · 投产包 doc/sch_src/ 与 HW/PCB/ 原理图源文件逐文件差异探针 (只读)")
    print("=" * 100)

    names = sorted(set(os.path.basename(p) for p in
                       __import__("glob").glob(os.path.join(SRC_DIR, "*.kicad_sch"))))
    names.append("demo_mainboard.kicad_pro")

    print(f"\n源目录: HW/PCB/  ({len(names)} 个文件 = {len(names)-1} 个 .kicad_sch + 1 个 .kicad_pro)")
    print(f"目标目录: HW/PCB/production/doc/sch_src/")
    print(f"归一化口径: state/check_chain_content_anchor.py::normalize_sch_text() (★ISS-256 口径★)\n")

    hdr = (f"{'文件名':<26}{'md5源':<10}{'md5包':<10}{'归一化指纹源':<12}{'归一化指纹包':<12}"
           f"{'原文差异行':<11}{'归一化差异行':<13}{'判定'}")
    print(hdr)
    print("-" * 100)

    rows = []
    for n in names:
        src = os.path.join(SRC_DIR, n)
        dst = os.path.join(DST_DIR, n)
        if not os.path.exists(dst):
            print(f"{n:<26}{'—':<10}{'★缺':<10}{'—':<12}{'—':<12}{'—':<11}{'—':<13}★缺页 (投产包里没有这个文件)")
            rows.append((n, "缺页", None))
            continue
        m_src = md5_file(src)
        m_dst = md5_file(dst)
        t_src = read(src)
        t_dst = read(dst)
        n_src = CA.normalize_sch_text(t_src)
        n_dst = CA.normalize_sch_text(t_dst)
        f_src = sha_text(n_src)
        f_dst = sha_text(n_dst)
        dl_raw = sum(1 for _ in difflib.unified_diff(t_src.splitlines(), t_dst.splitlines(), n=0))
        dl_norm = sum(1 for _ in difflib.unified_diff(n_src.splitlines(), n_dst.splitlines(), n=0))
        if f_src == f_dst:
            verdict = "★uuid 抖动 (归一化后一致 ⇒ 不是真缺件)"
        else:
            verdict = "★内容不同 (真差异)"
        print(f"{n:<26}{m_src[:8]:<10}{m_dst[:8]:<10}{f_src[:10]:<12}{f_dst[:10]:<12}"
              f"{dl_raw:<11}{dl_norm:<13}{verdict}")
        rows.append((n, verdict, (m_src, m_dst, f_src, f_dst, dl_raw, dl_norm, t_src, t_dst)))

    # ---------------- 分类计数 ----------------
    print("\n" + "-" * 100)
    print("分类计数 (★本单要回答的关键一问 ★)")
    print("-" * 100)
    uuid_only, real_diff, missing, renamed = [], [], [], []
    for n, verdict, extra in rows:
        if verdict == "缺页":
            missing.append(n)
        elif extra is None:
            renamed.append(n)
        elif "uuid 抖动" in verdict:
            uuid_only.append(n)
        else:
            real_diff.append(n)
    print(f"★投产包里的原理图比 HW/PCB/ 旧 (★内容真不同 ⇒ 投板用的是旧原理图★): {len(real_diff)} 个")
    for n in real_diff:
        print(f"    · {n}")
    print(f"★只是 uuid 抖动 (★归一化后一致 ⇒ 不是真缺件·不必重出★): {len(uuid_only)} 个")
    for n in uuid_only:
        print(f"    · {n}")
    print(f"★缺页 (投产包里没有): {len(missing)} 个 → {missing}")
    print(f"★改名 (源里叫别的名字): {len(renamed)} 个 → {renamed}")

    # ---------------- 内容真差异的逐行明细 ----------------
    print("\n" + "-" * 100)
    print("★内容真差异 的逐行明细 (源 vs 投产包, 归一化后 diff)")
    print("-" * 100)
    for n in real_diff:
        _n, verdict, extra = None, None, None
        for r in rows:
            if r[0] == n:
                extra = r[2]
                break
        if not extra:
            continue
        m_src, m_dst, f_src, f_dst, dl_raw, dl_norm, t_src, t_dst = extra
        n_src = CA.normalize_sch_text(t_src)
        n_dst = CA.normalize_sch_text(t_dst)
        print(f"\n### {n}   原文差异行={dl_raw} · 归一化差异行={dl_norm}")
        sm = difflib.SequenceMatcher(None, n_src.splitlines(), n_dst.splitlines())
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == "equal":
                continue
            print(f"  [{tag}] 源 L{i1+1}~{i2} / 包 L{j1+1}~{j2}")
            for ln in n_src.splitlines()[i1:i2][:12]:
                print(f"    - {ln[:160]}")
            for ln in n_dst.splitlines()[j1:j2][:12]:
                print(f"    + {ln[:160]}")
            if (i2 - i1) > 12 or (j2 - j1) > 12:
                print("    … (截断)")

    # ---------------- 时间戳对照 ----------------
    print("\n" + "-" * 100)
    print("★源文件 vs 投产包文件 mtime (★投产包比源旧 ⇒ 投板用的是旧原理图★)")
    print("-" * 100)
    import time
    for n in names:
        src = os.path.join(SRC_DIR, n)
        dst = os.path.join(DST_DIR, n)
        if not (os.path.exists(src) and os.path.exists(dst)):
            continue
        ts_ = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(src)))
        td_ = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(dst)))
        flag = "★投产包旧" if os.path.getmtime(dst) < os.path.getmtime(src) else ""
        print(f"  {n:<26} 源 {ts_}   包 {td_}   {flag}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
