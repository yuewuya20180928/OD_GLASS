#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-284 · 网表/脚表链头读数前后逐字比对 (★ISS-275 那条已跑通的逻辑不许动★)。

用法: python3 logs/iss284/probe_netlist_reading.py <老脚本路径> <新脚本路径> <项目根>
⇒ 两份脚本各自算出网表/脚表的【链头/链/产出单号/锚点副本核对】, 打印原样, 两边 diff 为空 = 读数逐字相同
"""
import importlib.util
import json
import os
import sys


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    old_path, new_path, root = sys.argv[1], sys.argv[2], sys.argv[3]
    old = load(old_path, "iss284_old")
    new = load(new_path, "iss284_new")
    out = {}
    for tag, mod in (("old", old), ("new", new)):
        anchors, err = mod.load_sw_anchor(root)
        if anchors is None:
            print("!! %s 读不到锚点: %s" % (tag, err))
            return 2
        led_text, led_spec = mod.sw_ledger_canonical_text(root, anchors)
        rec = {}
        for rel in ("HW/netlist_v1.csv", "HW/netlist_v1_pins.csv"):
            st = mod.sw_ledger_state(rel, led_text)
            rec[rel] = {
                "head": st["head"], "chain": st["chain"], "why": st["why"],
                "head_iss": st["head_iss"], "known": sorted(st["known"]),
                "producer": {k: sorted(v) for k, v in sorted(st["producer"].items())},
                "records": [{kk: r[kk] for kk in ("prev", "new", "iss", "sec", "row")}
                            for r in st["records"]],
            }
        out[tag] = rec
    a = json.dumps(out["old"], ensure_ascii=False, sort_keys=True, indent=1)
    b = json.dumps(out["new"], ensure_ascii=False, sort_keys=True, indent=1)
    print("=== 老脚本 (ISS-275 版) 网表/脚表链头读数 ===")
    print(a)
    print("=== 新脚本 (ISS-284 版) 网表/脚表链头读数 ===")
    print(b)
    print("=== DIFF (空 = 逐字相同) ===")
    if a == b:
        print("IDENTICAL: True")
        return 0
    import difflib
    for line in difflib.unified_diff(a.split("\n"), b.split("\n"), "old", "new", lineterm=""):
        print(line)
    print("IDENTICAL: False")
    return 1


if __name__ == "__main__":
    sys.exit(main())
