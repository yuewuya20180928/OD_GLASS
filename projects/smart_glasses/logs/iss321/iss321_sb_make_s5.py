#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iss321_sb_make_s5.py —— ISS-321 · 场景 S5 造场 (★对照组·零改名·只加台账行★)

★★场景 S5 = 【S0 基线盘面】+ 【落表台账加一条板变更行 + SW 台账锚点补 reboard】
    ★★【一个位号都不改】★★ ⇒ ★只测「台账里多了一条板变更记录」这件事本身的影响★

★★为什么必须造这个对照组 ★★:
    场景 S4 里三道 r6 selftest 闸红了 (HP-4 「链头不唯一 = ['ba8aebf261b1', 'fadf2c2f6f49']」)
    ⇒ ★到底是【改名】把它炸的, 还是【台账里多了一条板变更行】把它炸的?★
    ⇒ ★S5 = 零改名 + 同样的一条板变更行 ⇒ ★同样红 ⇒ 证明是【台账行】造成的, 不是改名★
    ⇒ ★S5 绿 而 S4 红 ⇒ 证明是改名造成的★ ★

★★边界 ★★: 只写 tmp/iss321_sandbox/rootS5/ · 项目真件一个字节都不动 ★★
"""
import hashlib
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(HERE))
SB = os.path.join(PROJ, "tmp", "iss321_sandbox")
S0 = os.path.join(SB, "rootS0")
S5 = os.path.join(SB, "rootS5")
TICKET = "ISS-321"


def md5_of(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    if os.path.isdir(S5):
        shutil.rmtree(S5)
    shutil.copytree(S0, S5, symlinks=True)
    os.makedirs(os.path.join(S5, "tmp"), exist_ok=True)

    pcb_base = md5_of(os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb"))
    pro_base = md5_of(os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pro"))

    # ── ① SW 台账锚点块: 只补【板的 reboard】(★改成什么 md5 无所谓·这闸只看「台账里有没有变更行」★) ──
    led_rel = "SW/SW_MD5_BASELINE_LEDGER.md"
    led_dst = os.path.join(S5, led_rel)
    if os.path.lexists(led_dst):
        os.remove(led_dst)
    txt = open(os.path.join(S0, led_rel), encoding="utf-8").read()
    old = ("    - file: HW/PCB/demo_mainboard.kicad_pcb\n"
           "      md5: %s\n"
           "      reboard: null\n" % pcb_base)
    new = ("    - file: HW/PCB/demo_mainboard.kicad_pcb\n"
           "      md5: %s\n"
           "      reboard:\n"
           "        by: %s\n"
           "        file: HW/PCB/demo_mainboard.kicad_pcb\n"
           "        prev_md5: %s\n"
           "        md5: %s\n" % (pcb_base, TICKET, pcb_base, pcb_base))
    if old not in txt:
        raise RuntimeError("★锚点没找到⇒abort★")
    txt = txt.replace(old, new, 1)
    open(led_dst, "w", encoding="utf-8").write(txt)

    # ── ② 落表台账: 加【一条板变更行】(★改后 md5 = 假的 fadf2c2f6f49…★·★它【不】等于盘上 md5★
    #      ⇒ 目的是【让台账里有变更行】⇒ 逼闸走「合法改板」那条分支★) ──
    led2_rel = "HW/SCHEMATIC_LANDING_V1_LANDED.md"
    led2_dst = os.path.join(S5, led2_rel)
    if os.path.lexists(led2_dst):
        os.remove(led2_dst)
    txt2 = open(os.path.join(S0, led2_rel), encoding="utf-8").read()
    txt2 += ("\n<!--ISS321_S5_ROWS:BEGIN-->\n"
             "### ★★ISS-321 · 沙盒对照组 (★零改名·只加一条板变更行★) ★★\n\n"
             "| 批次 | 文件 | 改前 md5 | 改后 md5 | 落表时刻 | 单号 |\n"
             "|---|---|---|---|---|---|\n"
             "| ★**%s** ★ | `HW/PCB/demo_mainboard.kicad_pcb` | `%s` | `%s` | ★**2026-11-18** ★ | ★**%s** ★ |\n"
             "<!--ISS321_S5_ROWS:END-->\n"
             % (TICKET, pcb_base, "fadf2c2f6f4985ed291b87c3f856a98c", TICKET))
    open(led2_dst, "w", encoding="utf-8").write(txt2)

    print("=" * 92)
    print("ISS-321 · 场景 S5 造场完成 (★对照组·零改名·只加台账行★)")
    print("=" * 92)
    print("  ★板 md5 (盘上, 未改): %s" % pcb_base)
    print("  ★台账里加的板变更行: prev=%s → new=fadf2c2f6f49 (★故意与盘上不等★)"
          % pcb_base[:12])
    print("★这个场景回答的是: 「三道 r6 selftest 闸的红」到底归因于【改名】还是【台账多了一行】★")


if __name__ == "__main__":
    main()
