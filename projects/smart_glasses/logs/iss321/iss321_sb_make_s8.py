#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iss321_sb_make_s8.py —— ISS-321 · 场景 S8 造场 (★对照组·板真改了·零改名·台账/留痕全齐★)

★★场景 S8 = S7 + 【issue_log 的 ISS-321 留痕行】★★
    ⇒ ★★这是一次【完整的合法改板】(零位号改名)★★
    ⇒ ★跑完的读数 = 「板那一趟做完所有该做的事 · 但不涉及改名」时的盘面读数★

★★S4 vs S8 的差 = 【只有「位号改名」这一项】★★
    ⇒ ★S4 红 而 S8 绿 ⇒ 【改名】特有的炸 ⇒ 本单必须出改法★
    ⇒ ★S4 红 且 S8 也红 ⇒ 【板改了就会红】(既有闸的夹具跟真实板变更不兼容) ⇒ 不是改名特有的 ⇒ 交 need★
"""
import hashlib
import os
import re
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(HERE))
SB = os.path.join(PROJ, "tmp", "iss321_sandbox")
S7 = os.path.join(SB, "rootS7")
S8 = os.path.join(SB, "rootS8")
TICKET = "ISS-321"
BOARD = "HW/PCB/demo_mainboard.kicad_pcb"
PRO = "HW/PCB/demo_mainboard.kicad_pro"


def md5_of(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    if os.path.isdir(S8):
        shutil.rmtree(S8)
    shutil.copytree(S7, S8, symlinks=True)
    os.makedirs(os.path.join(S8, "tmp"), exist_ok=True)

    pcb_base = md5_of(os.path.join(PROJ, BOARD))
    pro_base = md5_of(os.path.join(PROJ, PRO))
    pcb_new = md5_of(os.path.join(S8, BOARD))
    pro_new = md5_of(os.path.join(PROJ, PRO))

    # ── issue_log: 在 ISS-321 真条目里补落表留痕行 (★文件名 + 前后 md5★) ──
    il_rel = "state/issue_log.yaml"
    il_dst = os.path.join(S8, il_rel)
    if os.path.lexists(il_dst):
        os.remove(il_dst)
    il = open(os.path.join(PROJ, il_rel), encoding="utf-8").read()
    traces = [
        "  evidence: '★落表留痕★ %s 改前 %s → 改后 %s (★合法改板·沙盒对照组 S8·零改名★)'"
        % (BOARD, pcb_base, pcb_new),
        "  evidence: '★落表留痕★ %s 改前 %s → 改后 %s (★逐字节不变·沙盒对照组 S8·零改名★)'"
        % (PRO, pro_base, pro_new),
    ]
    il = il.replace("- id: ISS-321\n", "- id: ISS-321\n" + "\n".join(traces) + "\n", 1)
    open(il_dst, "w", encoding="utf-8").write(il)

    print("=" * 92)
    print("ISS-321 · 场景 S8 造场完成 (★对照组·板真改了·零改名·台账/留痕全齐★)")
    print("=" * 92)
    print("  ★板 md5: %s → %s (★位号零改动★)" % (pcb_base[:12], pcb_new[:12]))
    print("★S4 vs S8 的差 = 【只有「位号改名」这一项】★")


if __name__ == "__main__":
    main()
