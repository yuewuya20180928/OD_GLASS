#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
★ISS-369 独立复核脚本 (v2)★ —— ★板面【写盘机制】本机 KiCad 10.0.8 实测★
★不抄任何文档·不抄上一趟的脚本·自己造板、自己写、自己读回来★
测项:
  E1  python API: SetFPID(LIB_ID("Capacitor_SMD","C_0603_1608Metric")) + SaveBoard
      ⇒ 判: 重新 LoadBoard 后 GetFPIDAsString() 是否 == "Capacitor_SMD:C_0603_1608Metric"
           ★且整份文件除封装节点名行外是否一个字节没动★
  E2  文本层: (footprint "LIB:NAME"      ⇒ 读回是否正确
  E3  文本层: (footprint "NAME" (lib "LIB" "NAME")     ⇒ ★读回是否失败★
  E4a 文本层: (footprint "NAME" (lib_id "LIB:NAME")    ⇒ ★读回是否失败★
  E4c 文本层: (footprint "NAME"          (裸封装名)   ⇒ 读回 lib 项是否变成封装名
  E8  库名指向不存在的库 ⇒ 读回是否仍正常
只落 tmp/iss369/v2_wm/ ⇒ ★零写板★
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


def first_fp_line(txt):
    for ln in txt.splitlines():
        if ln.strip().startswith("(footprint "):
            return ln
    return None


def load_or_none(p):
    try:
        b = pcbnew.LoadBoard(p)
    except Exception as e:
        return None, "EXC:%s" % e
    if b is None:
        return None, "LoadBoard->None"
    return b, "ok"


def report(tag, path, extra=""):
    b, st = load_or_none(path)
    if b is None:
        print("[%s] 读回 = ❌ %s  %s" % (tag, st, extra))
        return None
    fps = sorted(list(b.GetFootprints()), key=lambda f: str(f.GetReference()))
    tgt = None
    for f in fps:
        if str(f.GetReference()) == "C1":
            tgt = f
            break
    if tgt is None:
        tgt = fps[0] if fps else None
    if tgt is None:
        print("[%s] 读回 = ok 但板里没有封装" % tag)
        return None
    print("[%s] 读回 = ok · ref=%s · GetFPIDAsString()=%r · GetLibItemName()=%r · GetUniStringLibId()=%r %s"
          % (tag, str(tgt.GetReference()), str(tgt.GetFPIDAsString()),
             str(tgt.GetFPID().GetLibItemName()), str(tgt.GetFPID().GetUniStringLibId()), extra))
    return tgt


def main():
    if os.path.isdir(SBX):
        shutil.rmtree(SBX)
    os.makedirs(SBX)
    print("=== ISS-369 v2 写盘机制实测 (KiCad %s) ===" % pcbnew.GetBuildVersion())
    print("real board md5 (前) = %s" % md5(REAL))

    # ---------- E1: python API ----------
    p1 = os.path.join(SBX, "e1_api.kicad_pcb")
    shutil.copy2(REAL, p1)
    b = pcbnew.LoadBoard(p1)
    tgt = None
    for f in b.GetFootprints():
        tgt = f
        break
    print("E1  选中的目标封装: %s" % str(tgt.GetReference()))
    tgt.SetFPID(pcbnew.LIB_ID("Capacitor_SMD", "C_0603_1608Metric"))
    pcbnew.SaveBoard(p1, b)
    report("E1 ", p1)
    # 整份文件差分行数 (只按行, 不做整体 diff)
    with open(REAL, encoding="utf-8", errors="replace") as f:
        a = f.read().splitlines()
    with open(p1, encoding="utf-8", errors="replace") as f:
        c = f.read().splitlines()
    diffs = []
    if len(a) == len(c):
        for i, (x, y) in enumerate(zip(a, c)):
            if x != y:
                diffs.append((i + 1, x.strip()[:120], y.strip()[:120]))
    print("E1  行数 原=%d 新=%d · 差异行数=%d" % (len(a), len(c), len(diffs)))
    for d in diffs[:5]:
        print("     L%-6d 旧=%r" % (d[0], d[1]))
        print("            新=%r" % (d[2],))

    # ---------- E2 / E3 / E4a / E4c / E8: 文本层 ----------
    with open(REAL, encoding="utf-8", errors="replace") as f:
        base_txt = f.read()
    src_line = first_fp_line(base_txt)
    print("\n原板第一行封装节点: %r" % src_line)
    idx = base_txt.index(src_line)
    head = base_txt[:idx]
    tail = base_txt[idx + len(src_line):]

    cases = {
        "E2_text_libname": '(footprint "Capacitor_SMD:C_0603_1608Metric"',
        "E3_text_lib_block": '(footprint "C_0603_1608Metric" (lib "Capacitor_SMD" "C_0603_1608Metric")',
        "E4a_text_libid_block": '(footprint "C_0603_1608Metric" (lib_id "Capacitor_SMD:C_0603_1608Metric")',
        "E4c_text_bare": '(footprint "C_0603_1608Metric"',
        "E8_text_noSuchLib": '(footprint "NoSuchLib_XYZ:NoSuchFootprint_XYZ"',
    }
    for tag, newline in cases.items():
        p = os.path.join(SBX, tag + ".kicad_pcb")
        with open(p, "w", encoding="utf-8") as f:
            f.write(head + newline + tail)
        report(tag, p)

    print("\nreal board md5 (后) = %s" % md5(REAL))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
