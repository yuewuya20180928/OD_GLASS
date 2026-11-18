#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iss321_sb_make_s7.py —— ISS-321 · 场景 S7 造场 (★对照组·板真改了·但一个位号都没改★)

★★场景 S7 = 【板文件真的被改了】(★改一个无关字节⇒md5 变★) + 【落表台账记合法改板行】
    ★★+【SW 台账锚点补 reboard】+【.kicad_pro 覆盖行】★★
    ★★【位号一个字都没改】★★ ⇒ ★网表/脚表/BOM/SW 文档全部原样★

★★为什么必须有 S7 (★本单最关键的一次归因★) ★★:
    S4 = 改名 + 台账 ⇒ 三道 r6 selftest 闸红了
    ⇒ ★到底是【改名】炸的, 还是【板改了 + 台账记了】炸的?★
    ★S7 = 板真改了 + 台账记了, 但零改名 ⇒ ★同样的红 ⇒ 归因于【板改了】, 不是【改名】★
    ★⇒ 结论: 那批红【板那一趟不管改不改名都会红】⇒ 是【既有闸的夹具跟真实板变更不兼容】★
             ⇒ ★不是本单能改的 ⇒ 交 need 给 main 拍★

★★边界 ★★: 只写 tmp/iss321_sandbox/rootS7/ · 项目真件一个字节都不动 ★★
"""
import hashlib
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(HERE))
SB = os.path.join(PROJ, "tmp", "iss321_sandbox")
S0 = os.path.join(SB, "rootS0")
S7 = os.path.join(SB, "rootS7")
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
    if os.path.isdir(S7):
        shutil.rmtree(S7)
    shutil.copytree(S0, S7, symlinks=True)
    os.makedirs(os.path.join(S7, "tmp"), exist_ok=True)

    # ── ① 板文件真改一个字节 (★改 title 行·与位号无关★) ──
    bdst = os.path.join(S7, BOARD)
    if os.path.lexists(bdst):
        os.remove(bdst)
    src = open(os.path.join(PROJ, BOARD), encoding="utf-8", errors="replace").read()
    # ★在文件末尾追加一行注释 (★不改任何封装/网络/位号★) ★
    new_txt = src.rstrip("\n") + "\n"
    # ★KiCad 板文件末尾加一个自定义 comment (★用 (comment 1 "…") 语法·不碰封装★) ★
    new_txt = new_txt.replace("(kicad_pcb (version 20240108)",
                              "(kicad_pcb (version 20240108)", 1)
    # ★真改: 改 (paper "A4") 的 title 注释 ★
    import re
    new_txt2, n = re.subn(r'\(title_block\s*\n(\s*title\s+"[^"]*")',
                          r'\1 "ARS45-DEMO-MAINBOARD-ISS321-S7"',
                          new_txt, count=1)
    if n == 0:
        # ★退化: 追加一个顶层 comment (★KiCad 允许 (comment N "…") 在板级★) ★
        new_txt2 = new_txt.rstrip("\n") + '\n\t(comment 1 "ARS45 ISS-321 S7 sandbox board byte change")\n'
    open(bdst, "w", encoding="utf-8", errors="replace").write(new_txt2)

    pcb_base = md5_of(os.path.join(PROJ, BOARD))
    pro_base = md5_of(os.path.join(PROJ, PRO))
    pcb_new = md5_of(bdst)
    pro_new = md5_of(os.path.join(PROJ, PRO))

    # ── ② SW 台账锚点: 补板的 reboard 四项原子记录 ──
    led_rel = "SW/SW_MD5_BASELINE_LEDGER.md"
    led_dst = os.path.join(S7, led_rel)
    if os.path.lexists(led_dst):
        os.remove(led_dst)
    txt = open(os.path.join(S0, led_rel), encoding="utf-8").read()
    old = ("    - file: %s\n"
           "      md5: %s\n"
           "      reboard: null\n" % (BOARD, pcb_base))
    new = ("    - file: %s\n"
           "      md5: %s\n"
           "      reboard:\n"
           "        by: %s\n"
           "        file: %s\n"
           "        prev_md5: %s\n"
           "        md5: %s\n" % (BOARD, pcb_base, TICKET, BOARD, pcb_base, pcb_new))
    if old not in txt:
        raise RuntimeError("★锚点没找到⇒abort★")
    txt = txt.replace(old, new, 1)
    open(led_dst, "w", encoding="utf-8").write(txt)

    # ── ③ 落表台账: 板一行变更 + .kicad_pro 一行「逐字节不变」 (★同一单号★) ──
    led2_rel = "HW/SCHEMATIC_LANDING_V1_LANDED.md"
    led2_dst = os.path.join(S7, led2_rel)
    if os.path.lexists(led2_dst):
        os.remove(led2_dst)
    txt2 = open(os.path.join(S0, led2_rel), encoding="utf-8").read()
    txt2 += ("\n<!--ISS321_S7_ROWS:BEGIN-->\n"
             "### ★★ISS-321 · 沙盒对照组 S7 (★板真改了·位号零改动★) ★★\n\n"
             "| 批次 | 文件 | 改前 md5 | 改后 md5 | 落表时刻 | 单号 |\n"
             "|---|---|---|---|---|---|\n"
             "| ★**%s** ★ | `%s` | `%s` | `%s` | ★**2026-11-18** ★ | ★**%s** ★ |\n"
             "| ★**%s** ★ | `%s` | `%s` | `%s` | ★**2026-11-18** ★ | ★**%s** ★ |\n"
             "<!--ISS321_S7_ROWS:END-->\n"
             % (TICKET, BOARD, pcb_base, pcb_new, TICKET,
                TICKET, PRO, pro_base, pro_base, TICKET))
    open(led2_dst, "w", encoding="utf-8").write(txt2)

    print("=" * 92)
    print("ISS-321 · 场景 S7 造场完成 (★对照组·板真改了·位号零改动★)")
    print("=" * 92)
    print("  ★板 md5: %s → %s (★位号一个字都没改★)" % (pcb_base[:12], pcb_new[:12]))
    print("  ★.kicad_pro md5: %s (★逐字节不变★)" % pro_base[:12])
    print("★这个场景回答的是: 「三道 r6 selftest 闸的红」到底归因于【改名】还是【板改了】★")


if __name__ == "__main__":
    main()
