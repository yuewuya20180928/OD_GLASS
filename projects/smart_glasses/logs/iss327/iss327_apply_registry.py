#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iss327_apply_registry.py —— 把 `--freeze-registry` 的输出【贴回沙盒里的闸副本】

★只改沙盒副本 (tmp/iss327/...)★ ⇒ ★真件 SW/tools/check_sw_ref_reachability.py 一个字节都不动★

用法: python3 iss327_apply_registry.py <sandbox_root> <freeze_stdout_file>
"""
import re
import sys
import os

GATE_REL = os.path.join("SW", "tools", "check_sw_ref_reachability.py")
BLOCK_RE = re.compile(r"DESIGNATOR_REGISTRY = \(\n.*?\n\)\n# ★共 \d+ 条★[^\n]*\n", re.S)


def main():
    root = sys.argv[1]
    freeze_out = sys.argv[2]
    gate = os.path.join(root, GATE_REL)
    txt = open(freeze_out, encoding="utf-8").read()
    m = re.search(r"DESIGNATOR_REGISTRY = \(\n(.*?)\n\)\n(# ★共 \d+ 条★[^\n]*)", txt, re.S)
    if not m:
        print("[FAIL] 冻结输出里找不到 DESIGNATOR_REGISTRY 块")
        return 2
    new_block = "DESIGNATOR_REGISTRY = (\n%s\n)\n%s\n" % (m.group(1), m.group(2))
    old = open(gate, encoding="utf-8").read()
    if not BLOCK_RE.search(old):
        print("[FAIL] 闸副本里找不到旧的 DESIGNATOR_REGISTRY 块")
        return 2
    new = BLOCK_RE.sub(new_block, old, count=1)
    # ★★cont1 规矩 ②: 写前 assert not islink ⇒ 软链当场炸 (★上一趟就是栽在这★)★★
    if os.path.islink(gate):
        print("[FAIL] 闸副本是软链 ⇒ 拒绝写穿: %s" % gate)
        return 2
    open(gate, "w", encoding="utf-8").write(new)
    n = len([x for x in m.group(1).splitlines() if x.strip()])
    print("★已把冻结表 (%d 条) 贴回沙盒闸副本: %s" % (n, gate))
    return 0


if __name__ == "__main__":
    sys.exit(main())
