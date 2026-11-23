#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-369 §2 · 写盘机制【本机 KiCad 实测】(只动 tmp/ 副本)

用法: bash state/pcbnew_py.sh tmp/iss369/tools/mech_probe.py <workdir>
产出: <workdir>/mech_*.kicad_pcb + mech_report.json
"""
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

rep = {"kicad_version": pcbnew.GetBuildVersion(),
       "board_src_md5": hashlib.md5(open(SRC, "rb").read()).hexdigest(),
       "experiments": []}


def fp_block(text, ref):
    """取板文件里某个 ref 的 footprint 整块文本"""
    out = []
    for m in re.finditer(r'^\t\(footprint ', text, re.M):
        s = m.start()
        cands = [text.find("\n\t(footprint ", s + 1), text.find("\n\t(net ", s + 1)]
        cands = [c for c in cands if c != -1]
        e = min(cands) if cands else len(text)
        blk = text[s:e]
        if '(property "Reference" "%s"' % ref in blk:
            out.append(blk)
    return out[0] if out else None


# ============ 实验 1: pcbnew API SetFPID → SaveBoard → 看板文件变了哪些字段 ============
w1 = os.path.join(WORK, "mech_w1_api.kicad_pcb")
shutil.copy2(SRC, w1)
b = pcbnew.LoadBoard(w1)
before_text = open(w1, encoding="utf-8").read()
REF = "C_BULK_SENSOR_CORE"
fp = None
for f in b.GetFootprints():
    if f.GetReference() == REF:
        fp = f
        break
assert fp is not None, "找不到 " + REF
old_fpid = fp.GetFPIDAsString()
fp.SetFPID(pcbnew.LIB_ID("Capacitor_SMD", "C_0603_1608Metric"))
new_fpid_api = fp.GetFPIDAsString()
pcbnew.SaveBoard(w1, b)
after_text = open(w1, encoding="utf-8").read()
blk_before = fp_block(before_text, REF)
blk_after = fp_block(after_text, REF)
rep["experiments"].append({
    "id": "E1_api_SetFPID_SaveBoard",
    "ref": REF,
    "fpid_before": old_fpid,
    "fpid_after_api": new_fpid_api,
    "block_head_before": blk_before.splitlines()[0] if blk_before else None,
    "block_head_after": blk_after.splitlines()[0] if blk_after else None,
    "block_changed_lines": sorted(set(blk_after.splitlines()) ^ set(blk_before.splitlines())),
    "file_md5_before": hashlib.md5(before_text.encode()).hexdigest(),
    "file_md5_after": hashlib.md5(after_text.encode()).hexdigest(),
})
# 重读回来
b2 = pcbnew.LoadBoard(w1)
for f in b2.GetFootprints():
    if f.GetReference() == REF:
        rep["experiments"][-1]["fpid_after_reload"] = f.GetFPIDAsString()
        rep["experiments"][-1]["pad_count_after_reload"] = len(list(f.Pads()))
        break

# ============ 实验 2: 文本层写 `(footprint "Lib:Name"` ============
w2 = os.path.join(WORK, "mech_w2_text_libid.kicad_pcb")
t = open(SRC, encoding="utf-8").read()
lines = t.splitlines(True)
n = 0
for i, ln in enumerate(lines):
    if re.match(r'^\t\(footprint ""\s*$', ln):
        # 只改第 3 个 (REF 所在) —— 改成 REF 名
        pass
# 精确定位 REF 块
blocks = list(re.finditer(r'^\t\(footprint ""', t, re.M))
# 找到 REF 的块起点
mref = None
for m in blocks:
    s = m.start()
    cands = [t.find("\n\t(footprint ", s + 1), t.find("\n\t(net ", s + 1)]
    cands = [c for c in cands if c != -1]
    e = min(cands) if cands else len(t)
    if '(property "Reference" "%s"' % REF in t[s:e]:
        mref = (s, e)
        break
assert mref
t2 = t[:mref[0]] + t[mref[0]:mref[1]].replace(
    '\t(footprint ""', '\t(footprint "Capacitor_SMD:C_0603_1608Metric"', 1) + t[mref[1]:]
open(w2, "w", encoding="utf-8").write(t2)
b3 = pcbnew.LoadBoard(w2)
for f in b3.GetFootprints():
    if f.GetReference() == REF:
        rep["experiments"].append({
            "id": "E2_text_footprint_node_libid_string",
            "ref": REF,
            "fpid_after_reload": f.GetFPIDAsString(),
            "lib_after_reload": f.GetFPID().GetUniStringLibId(),
            "name_after_reload": f.GetFPID().GetLibItemName().wx_str(),
            "pad_count_after_reload": len(list(f.Pads())),
            "file_md5": hashlib.md5(open(w2, "rb").read()).hexdigest(),
            "note": "★(footprint \"Lib:Name\" 节点名写法 ⇒ 重新加载后 GetFPIDAsString() 实测",
        })
        break

# ============ 实验 3: 文本层写 `(footprint "Name" (lib "nickname" "libname")` ============
for order in ("libname_nick", "nick_libname"):
    w3 = os.path.join(WORK, "mech_w3_text_lib_%s.kicad_pcb" % order)
    if order == "libname_nick":
        ins = '\t(footprint "C_0603_1608Metric" (lib "Capacitor_SMD" "C_0603_1608Metric")'
    else:
        ins = '\t(footprint "C_0603_1608Metric" (lib "C_0603_1608Metric" "Capacitor_SMD")'
    t3 = t[:mref[0]] + t[mref[0]:mref[1]].replace('\t(footprint ""', ins, 1) + t[mref[1]:]
    open(w3, "w", encoding="utf-8").write(t3)
    rec = {"id": "E3_text_lib_tag_%s" % order, "ref": REF, "inserted": ins}
    try:
        b4 = pcbnew.LoadBoard(w3)
        got = None
        for f in b4.GetFootprints():
            if f.GetReference() == REF:
                got = f
                break
        if got is None:
            rec["load"] = "★加载成功但找不到 ref"
        else:
            rec["load"] = "OK"
            rec["fpid_after_reload"] = got.GetFPIDAsString()
            rec["lib_after_reload"] = got.GetFPID().GetUniStringLibId()
            rec["name_after_reload"] = got.GetFPID().GetLibItemName().wx_str()
            rec["pad_count_after_reload"] = len(list(got.Pads()))
    except Exception as e:
        rec["load"] = "★抛异常: %r" % (e,)
    rep["experiments"].append(rec)

json.dump(rep, open(os.path.join(WORK, "mech_report.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(json.dumps(rep, ensure_ascii=False, indent=1))
