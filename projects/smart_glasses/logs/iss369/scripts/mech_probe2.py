#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-369 §2 续 · 写盘机制深挖 (本机 KiCad 10.0.8 实测)

E4: (footprint "NAME" (lib "A" "B")) 到底为什么 LoadBoard 返回 None ⇒ 单独隔离
E5: (footprint "NAME" (lib_id "A:B")) 这种写法
E6: SaveBoard 整份文件是不是只有那一行变了 (全文件行级 diff)
E7: 库名写上后, pad / fp_line / fp_text / net / uuid 会不会被动
E8: 库名指向不存在的库 ⇒ 行为
"""
import difflib
import hashlib
import json
import os
import re
import shutil
import sys

import pcbnew

WORK = sys.argv[1]
ROOT = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
SRC = os.path.join(ROOT, "HW", "PCB", "demo_mainboard.kicad_pcb")
os.makedirs(WORK, exist_ok=True)
rep = {"kicad_version": pcbnew.GetBuildVersion(), "experiments": []}


def block_of(text, ref):
    for m in re.finditer(r'^\t\(footprint ', text, re.M):
        s = m.start()
        cands = [text.find("\n\t(footprint ", s + 1), text.find("\n\t(net ", s + 1)]
        cands = [c for c in cands if c != -1]
        e = min(cands) if cands else len(text)
        blk = text[s:e]
        if '(property "Reference" "%s"' % ref in blk:
            return s, e, blk
    return None


REF = "C_BULK_SENSOR_CORE"
orig = open(SRC, encoding="utf-8").read()

# ---- E4/E5: 各种写法的加载行为 (纯文本层) ----
variants = {
    "E4a_footprint_name_plus_lib_tag": '\t(footprint "C_0603_1608Metric" (lib "Capacitor_SMD" "C_0603_1608Metric")',
    "E4b_footprint_name_plus_libid_tag": '\t(footprint "C_0603_1608Metric" (lib_id "Capacitor_SMD:C_0603_1608Metric")',
    "E4c_footprint_name_only": '\t(footprint "C_0603_1608Metric"',
    "E4d_footprint_libid_string": '\t(footprint "Capacitor_SMD:C_0603_1608Metric"',
}
s, e, _blk = block_of(orig, REF)
for name, ins in variants.items():
    p = os.path.join(WORK, "mech_%s.kicad_pcb" % name)
    t = orig[:s] + orig[s:e].replace('\t(footprint ""', ins, 1) + orig[e:]
    open(p, "w", encoding="utf-8").write(t)
    rec = {"id": name, "inserted": ins}
    try:
        b = pcbnew.LoadBoard(p)
        if b is None:
            rec["load"] = "★LoadBoard 返回 None (整板读不回来)"
            rec["verdict"] = "★本机 KiCad 10.0.8 **不接受**这个写法"
        else:
            rec["load"] = "OK · footprints=%d" % len(list(b.GetFootprints()))
            for f in b.GetFootprints():
                if f.GetReference() == REF:
                    rec["fpid"] = f.GetFPIDAsString()
                    rec["lib"] = f.GetFPID().GetUniStringLibId()
                    rec["name"] = f.GetFPID().GetLibItemName().wx_str()
                    rec["pads"] = len(list(f.Pads()))
                    break
    except Exception as ex:
        rec["load"] = "★抛异常 %r" % (ex,)
        rec["verdict"] = "★本机 KiCad 10.0.8 **不接受**这个写法"
    rep["experiments"].append(rec)

# ---- E6/E7: API 路径整文件行级 diff + 板面属性是否被动 ----
w = os.path.join(WORK, "mech_api_full.kicad_pcb")
shutil.copy2(SRC, w)
b = pcbnew.LoadBoard(w)
for f in b.GetFootprints():
    if f.GetReference() == REF:
        before = {
            "pads": [(p.GetNumber(), p.GetNetname(), p.GetSize().x, p.GetSize().y,
                      p.GetPosition().x, p.GetPosition().y) for p in f.Pads()],
            "bbox": (f.GetBoundingBox().GetWidth(), f.GetBoundingBox().GetHeight()),
            "nfp_lines": len(list(f.GraphicalItems())),
            "uuid": f.m_Uuid.AsString(),
            "value": f.GetValue(),
            "layer": f.GetLayerName(),
            "at": (f.GetPosition().x, f.GetPosition().y),
        }
        f.SetFPID(pcbnew.LIB_ID("Capacitor_SMD", "C_0603_1608Metric"))
pcbnew.SaveBoard(w, b)
after_text = open(w, encoding="utf-8").read()
b2 = pcbnew.LoadBoard(w)
for f in b2.GetFootprints():
    if f.GetReference() == REF:
        after = {
            "pads": [(p.GetNumber(), p.GetNetname(), p.GetSize().x, p.GetSize().y,
                      p.GetPosition().x, p.GetPosition().y) for p in f.Pads()],
            "bbox": (f.GetBoundingBox().GetWidth(), f.GetBoundingBox().GetHeight()),
            "nfp_lines": len(list(f.GraphicalItems())),
            "uuid": f.m_Uuid.AsString(),
            "value": f.GetValue(),
            "layer": f.GetLayerName(),
            "at": (f.GetPosition().x, f.GetPosition().y),
        }
diff = list(difflib.unified_diff(orig.splitlines(), after_text.splitlines(),
                                 "orig", "after", lineterm="", n=0))
rep["experiments"].append({
    "id": "E6_E7_api_wholefile_diff",
    "orig_md5": hashlib.md5(orig.encode()).hexdigest(),
    "after_md5": hashlib.md5(after_text.encode()).hexdigest(),
    "diff_line_count": len(diff),
    "diff_head": diff[:40],
    "fp_props_before": {k: str(v) for k, v in before.items()},
    "fp_props_after": {k: str(v) for k, v in after.items()},
    "props_identical": before == after,
})

# ---- E8: 库名指向不存在的库 ----
w8 = os.path.join(WORK, "mech_nonexistent_lib.kicad_pcb")
shutil.copy2(SRC, w8)
b8 = pcbnew.LoadBoard(w8)
for f in b8.GetFootprints():
    if f.GetReference() == REF:
        f.SetFPID(pcbnew.LIB_ID("NoSuchLib_XYZ", "NoSuchFootprint_XYZ"))
pcbnew.SaveBoard(w8, b8)
b9 = pcbnew.LoadBoard(w8)
rec = {"id": "E8_nonexistent_lib_after_reload"}
for f in b9.GetFootprints():
    if f.GetReference() == REF:
        rec["load"] = "OK · footprints=%d" % len(list(b9.GetFootprints()))
        rec["fpid"] = f.GetFPIDAsString()
        rec["pads"] = len(list(f.Pads()))
        break
rep["experiments"].append(rec)

# ---- E9: 库名写上后, 板面其它 185 个封装有没有被动 ----
rep["experiments"].append({
    "id": "E9_other_footprints_untouched",
    "block_head_counts_after": {
        "empty_libid_blocks_before": len(re.findall(r'^\t\(footprint ""', orig, re.M)),
        "empty_libid_blocks_after": len(re.findall(r'^\t\(footprint ""', after_text, re.M)),
        "named_blocks_after": len(re.findall(r'^\t\(footprint "[^"]+"', after_text, re.M)),
    },
})

json.dump(rep, open(os.path.join(WORK, "mech_report2.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(json.dumps(rep, ensure_ascii=False, indent=1))
