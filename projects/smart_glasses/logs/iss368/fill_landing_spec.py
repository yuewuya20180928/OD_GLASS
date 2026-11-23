#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-368 · sw-lead · 把一页 §1 里的占位符换成 apply 脚本 EDITS 表里的【逐字原文/新文】.

★**零手抄** ★: 页面上的每一段「原文 / 新文 / 定位串」都直接取自 `apply_sw09_three_place_patch.py` 的 EDITS 表
★**用法** ★: `python3 logs/iss368/fill_landing_spec.py`
"""
from __future__ import annotations

import os
import sys

PROJ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(PROJ, "SW", "tools"))
import apply_sw09_three_place_patch as P   # noqa: E402

PAGE = os.path.join(PROJ, "SW", "BOARD_ONEPASS_SW09_LANDING_PATCH.md")


def main() -> int:
    txt = open(PAGE, encoding="utf-8").read()
    by_id = {e["eid"]: e for e in P.EDITS}
    n = 0
    for eid, ed in by_id.items():
        for key in ("old", "new"):
            mk = "@@%s_%s@@" % (eid, key.upper())
            if mk in txt:
                txt = txt.replace(mk, ed[key])
                n += 1
        for key, field in (("ANCHOR", "anchor"), ("PAYLOAD", "payload")):
            mk = "@@%s_%s@@" % (eid, key)
            if mk in txt:
                txt = txt.replace(mk, ed[field])
                n += 1
        if "item" in ed:
            import json
            mk = "@@%s_ITEM@@" % eid
            if mk in txt:
                txt = txt.replace(mk, json.dumps(ed["item"], ensure_ascii=False, indent=2))
                n += 1
    with open(PAGE, "w", encoding="utf-8", newline="") as f:
        f.write(txt)
    left = [ln for ln in txt.split("\n") if "@@" in ln and "@@" in ln and ln.count("@@") >= 2]
    print("填入占位符 %d 处 · 剩余未填 %d 处" % (n, len(left)))
    for ln in left[:10]:
        print("  ★未填★ %s" % ln[:120])
    return 0 if not left else 1


if __name__ == "__main__":
    sys.exit(main())
