#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
★ISS-369 独立复核脚本 (v2b)★ —— ★板面【写盘机制】本机 KiCad 10.0.8 实测 (精确定位到被改的那个封装)★
只落 tmp/iss369/v2_wm/ ⇒ ★零写板★
测项:
  E1  python API SetFPID + SaveBoard       ⇒ 读回是否正确 + 整份文件差几行
  E2  文本层 (footprint "LIB:NAME"         ⇒ 读回是否正确
  E3  文本层 (footprint "NAME" (lib "LIB" "NAME")   ⇒ ★读回是否失败★
  E4a 文本层 (footprint "NAME" (lib_id "LIB:NAME")  ⇒ ★读回是否失败★
  E4c 文本层 (footprint "NAME"              ⇒ 读回 lib 项是不是变成封装名
  E8  文本层 (footprint "NoSuchLib_XYZ:NoSuchFootprint_XYZ" ⇒ 读回是否仍正常
"""
import hashlib
import os
import re
import shutil

import pcbnew

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SBX = os.path.join(ROOT, "tmp", "iss369", "v2_wm")
REAL = os.path.join(ROOT, "HW", "PCB", "demo_mainboard.kicad_pcb")


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def ref_of_block(txt, start):
    """从封装块起点往后找 reference 属性"""
    chunk = txt[start:start + 4000]
    m = re.search(r'\(property "Reference" "([^"]*)"', chunk)
    if m:
        return m.group(1)
    m = re.search(r'\(fp_text reference "([^"]*)"', chunk)
    if m:
        return m.group(1)
    return None


def read_back(tag, path, want_ref):
    try:
        b = pcbnew.LoadBoard(path)
    except Exception as e:
        print("[%s] 读回 = ❌ 抛异常 %s" % (tag, e))
        return None
    if b is None:
        print("[%s] 读回 = ❌ LoadBoard -> None  ★★整块板读不回来 = 板文件报废★★" % tag)
        return None
    tgt = None
    for f in b.GetFootprints():
        if str(f.GetReference()) == want_ref:
            tgt = f
            break
    if tgt is None:
        print("[%s] 读回 = ok · 但板上找不到 ref=%s" % (tag, want_ref))
        return None
    print("[%s] 读回 = ok · ref=%s · GetFPIDAsString()=%r · GetLibItemName()=%r · GetUniStringLibId()=%r"
          % (tag, want_ref, str(tgt.GetFPIDAsString()),
             str(tgt.GetFPID().GetLibItemName()), str(tgt.GetFPID().GetUniStringLibId())))
    return tgt


def main():
    if os.path.isdir(SBX):
        shutil.rmtree(SBX)
    os.makedirs(SBX)
    print("=== ISS-369 v2b 写盘机制实测 (KiCad build %s) ===" % pcbnew.GetBuildVersion())
    print("real board md5 (前) = %s" % md5(REAL))

    with open(REAL, encoding="utf-8", errors="replace") as f:
        base_txt = f.read()

    # ---------------- E1: python API ----------------
    p1 = os.path.join(SBX, "e1_api.kicad_pcb")
    shutil.copy2(REAL, p1)
    b = pcbnew.LoadBoard(p1)
    fps = list(b.GetFootprints())
    tgt = fps[0]
    want_ref = str(tgt.GetReference())
    print("\nE1  选中的目标封装 ref = %s" % want_ref)
    tgt.SetFPID(pcbnew.LIB_ID("Capacitor_SMD", "C_0603_1608Metric"))
    pcbnew.SaveBoard(p1, b)
    read_back("E1 ", p1, want_ref)
    with open(REAL, encoding="utf-8", errors="replace") as f:
        a = f.read().splitlines()
    with open(p1, encoding="utf-8", errors="replace") as f:
        c = f.read().splitlines()
    ndiff = 0
    samples = []
    if len(a) == len(c):
        for i, (x, y) in enumerate(zip(a, c)):
            if x != y:
                ndiff += 1
                if len(samples) < 3:
                    samples.append((i + 1, x.strip()[:100], y.strip()[:100]))
    print("E1  行数 原=%d 新=%d · ★差异行数=%d★" % (len(a), len(c), ndiff))
    for d in samples:
        print("     L%-6d 旧=%r" % (d[0], d[1]))
        print("            新=%r" % (d[2],))

    # ---------------- 文本层 ----------------
    m = re.search(r'^\s*\(footprint "', base_txt, re.M)
    start = m.start()
    line_end = base_txt.index("\n", start)
    src_line = base_txt[start:line_end]
    want_ref2 = ref_of_block(base_txt, start)
    head = base_txt[:start]
    tail = base_txt[line_end:]
    print("\n文本层目标: 第一行封装节点 = %r · 归属 ref = %s" % (src_line.strip(), want_ref2))

    cases = [
        ("E2_text_libname", '(footprint "Capacitor_SMD:C_0603_1608Metric"'),
        ("E3_text_lib_block", '(footprint "C_0603_1608Metric" (lib "Capacitor_SMD" "C_0603_1608Metric")'),
        ("E4a_text_libid_block", '(footprint "C_0603_1608Metric" (lib_id "Capacitor_SMD:C_0603_1608Metric")'),
        ("E4c_text_bare", '(footprint "C_0603_1608Metric"'),
        ("E8_text_noSuchLib", '(footprint "NoSuchLib_XYZ:NoSuchFootprint_XYZ"'),
    ]
    for tag, newline in cases:
        p = os.path.join(SBX, tag + ".kicad_pcb")
        with open(p, "w", encoding="utf-8") as f:
            f.write(head + newline + tail)
        read_back(tag, p, want_ref2)

    print("\nreal board md5 (后) = %s" % md5(REAL))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
