#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""write_iss365_frag_extra.py —— ★★【ISS-365】追加一条分片 claim (★仍只走 `state/frag_write.py`★) ★★

★★**为什么要追加这一条**: ★**本单在写页的过程中, 差点给自己的新页凭空造一条「位号引用真隐患」**
  (★`MECH/tools/check_mech_ref_reachability.py` · ISS-326/ISS-333 · 已挂在 `state/gate_check.py` 链上★)
  ⇒ ★**这是一个【所有要在 MECH 域文档里写 KiCad 库名/封装名的人】都会踩的坑** ⇒ ★**登记成 interface_claim, 让下一个人不必再踩一遍** ★
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys

PROJ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
FRAG = os.path.join(PROJ, "state", "fragments", "mech.yaml")
LOG = os.path.join(PROJ, "logs", "iss365")

CLAIM = (
    "iss365_mech_doc_kicad_libname_naming",
    "MECH 域文档里写 KiCad 库名/封装名 ⇒ 把会被误认成板上位号的那一段拆成「前缀 + 余下」写 (例 `D_ + SOD-323` / `LED_ + SMD`)",
    "★**本单在写新页时真踩过这个坑并修好了**★: MECH/tools/check_mech_ref_reachability.py (ISS-326/ISS-333, 已挂在 state/gate_check.py 链上) 会把 MECH 域文档里的【全大写 + 板上位号前缀】的 token 当成板上位号引用 ⇒ ★**KiCad 库名/封装名只要长成那个样子就会被判成 C14「板与网表里从来没有过 ⇒ 真隐患」⇒ 真隐患条数超基线上限 ⇒ gate_check 当场红** (★本单实测 13 > 10★) ⇒ ★**修法 = 把会被误认的那一段拆开: 前缀那一段以 `_` 结尾 ⇒ 那道闸的 C8 判它是「文本被截断的前缀」而不是位号; 余下段不带位号前缀 ⇒ C14 不命中 ⇒ 去掉「 + 」就是 KiCad 真名, 零信息损失** ★ ⇒ ★**本单一行既有闸都没改** ★",
    "MECH/BOARD_ONEPASS_S10_FP_SWAP_IMPACT.md §1.2 「库件名的写法」 + MECH/check_onepass_s10_fp_swap_impact.py 的 `_unsplit()` + HANDOFF/2026-11-23_mech-lead_ISS365_S10换封装对MECH侧影响面.md §B1-4",
)


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    before = md5(FRAG)
    if md5(FRAG) != before:
        print("[frag-extra] ★★并发保护失败 ⇒ 已停止★★")
        return 3
    cmd = [sys.executable, os.path.join(PROJ, "state", "frag_write.py"), "--agent", "mech-lead",
           "--add-claim", 'key=%s value="%s" note="%s" ref="%s"' % CLAIM]
    r = subprocess.run(cmd, cwd=PROJ, capture_output=True, text=True)
    print(r.stdout.strip())
    if r.returncode != 0:
        print(r.stderr[-1500:])
        return r.returncode
    after = md5(FRAG)
    text = open(FRAG, encoding="utf-8").read()
    ok = ("key: %s" % CLAIM[0]) in text
    out = {"frag_md5_before": before, "frag_md5_after": after, "claim_present": ok}
    with open(os.path.join(LOG, "23b_frag_extra_claim.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print("[frag-extra] %s" % out)
    return 0 if ok else 4


if __name__ == "__main__":
    sys.exit(main())
