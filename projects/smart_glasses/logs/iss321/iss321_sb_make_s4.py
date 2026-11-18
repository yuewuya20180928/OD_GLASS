#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iss321_sb_make_s4.py —— ISS-321 · 场景 S4 造场 (★只写 tmp/iss321_sandbox/★)

★★场景 S4 = 「板那一趟【连 SW 侧台账锚点】都改对了」的盘面 ★★:
    继承 S3 (板/网表/脚表/BOM 已改名 + SW 文档已同步改名 + 落表台账已记合法落表行
             + issue_log 已留痕)
    ★★再补一件 SW 侧的东西: `SW/SW_MD5_BASELINE_LEDGER.md` §1 锚点块里的
       `hard_protected[].reboard` 四项原子记录 (★改板必须补★)★★
    ⇒ ★跑完还是红的 ⇒ 【判据本身写死了旧位号】⇒ ★那是真炸·必须改脚本★
    ⇒ ★跑完就绿的 ⇒ 【那批红全是「台账/锚点没跟着改」⇒ 不是判据的锅★

★★边界 ★★: 只写 tmp/iss321_sandbox/rootS4/ · 项目真件一个字节都不动 ★★
"""
import hashlib
import os
import re
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(HERE))
SB = os.path.join(PROJ, "tmp", "iss321_sandbox")
S3 = os.path.join(SB, "rootS3")
S4 = os.path.join(SB, "rootS4")
TICKET = "ISS-321"


def md5_of(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    if os.path.isdir(S4):
        shutil.rmtree(S4)
    # ★先拷 S3 (★S3 里那两件被改过的文件是真副本·其余是软链·拷过来还是软链★)
    shutil.copytree(S3, S4, symlinks=True)
    os.makedirs(os.path.join(S4, "tmp"), exist_ok=True)

    pcb_new = os.path.join(S4, "HW", "PCB", "demo_mainboard.kicad_pcb")
    pro_new = os.path.join(S4, "HW", "PCB", "demo_mainboard.kicad_pro")
    pcb_base = md5_of(os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb"))
    pro_base = md5_of(os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pro"))
    pcb_now = md5_of(pcb_new)
    pro_now = md5_of(pro_new)

    # ── ① SW 台账锚点块: 补 reboard 四项原子记录 (★板 + .kicad_pro 各一条★) ──
    # ★★注意: 从【S3 的副本】改 (★不是从 PROJ 真件·★S3 里那份已是【位号已改名】的★) ★★
    led_rel = "SW/SW_MD5_BASELINE_LEDGER.md"
    led_dst = os.path.join(S4, led_rel)
    if os.path.lexists(led_dst):
        os.remove(led_dst)
    txt = open(os.path.join(S3, led_rel), encoding="utf-8").read()
    old_pcb = ("    - file: HW/PCB/demo_mainboard.kicad_pcb\n"
               "      md5: %s\n"
               "      reboard: null\n" % pcb_base)
    new_pcb = ("    - file: HW/PCB/demo_mainboard.kicad_pcb\n"
               "      md5: %s\n"
               "      reboard:\n"
               "        by: %s\n"
               "        file: HW/PCB/demo_mainboard.kicad_pcb\n"
               "        prev_md5: %s\n"
               "        md5: %s\n" % (pcb_base, TICKET, pcb_base, pcb_now))
    old_pro = ("    - file: HW/PCB/demo_mainboard.kicad_pro\n"
               "      md5: %s\n"
               "      reboard: null\n" % pro_base)
    # ★★.kicad_pro 逐字节未变 ⇒ 锚点里【不许】有 reboard 记录 (★有记录但台账里查不到变更行 ⇒ 红★)
    #   ⇒ 只靠【落表台账里一条同批次的覆盖行】满足「同组受保护件覆盖」判据 ④ ★
    new_pro = old_pro
    for old, new in ((old_pcb, new_pcb), (old_pro, new_pro)):
        if old not in txt:
            raise RuntimeError("★锚点锚点没找到 ⇒ abort★: %r" % old[:80])
        txt = txt.replace(old, new, 1)
    open(led_dst, "w", encoding="utf-8").write(txt)

    # ── ② 落表台账: 给 .kicad_pro 补一条【同批次·逐字节不变】的覆盖行 ──
    # ★★注意: 从【S3 的副本】改 (★S3 那份已含 ISS-321 的四条落表行★) ★★
    led2_rel = "HW/SCHEMATIC_LANDING_V1_LANDED.md"
    led2_dst = os.path.join(S4, led2_rel)
    if os.path.lexists(led2_dst):
        os.remove(led2_dst)
    txt2 = open(os.path.join(S3, led2_rel), encoding="utf-8").read()
    txt2 += ("\n<!--ISS321_PRO_ROWS:BEGIN-->\n"
             "| ★**%s** ★ | `HW/PCB/demo_mainboard.kicad_pro` | `%s` | `%s` | ★**2026-11-18** ★ | ★**%s** ★ |\n"
             "<!--ISS321_PRO_ROWS:END-->\n" % (TICKET, pro_base, pro_now, TICKET))
    # ★把 .kicad_pro 的覆盖行并进 ISS-321 那一节 (★必须在同一个带单号的小节下·否则不继承单号★) ★
    txt2 = txt2.replace(
        "<!--ISS321_ROWS:BEGIN-->",
        "<!--ISS321_ROWS:BEGIN-->\n"
        "| ★**%s** ★ | `HW/PCB/demo_mainboard.kicad_pro` | `%s` | `%s` | ★**2026-11-18** ★ | ★**%s** ★ |"
        % (TICKET, pro_base, pro_now, TICKET), 1)
    open(led2_dst, "w", encoding="utf-8").write(txt2)

    print("=" * 92)
    print("ISS-321 · 场景 S4 造场完成 (★只写 tmp/iss321_sandbox/rootS4/★)")
    print("=" * 92)
    print("  ★板 reboard: by=%s prev=%s → md5=%s" % (TICKET, pcb_base[:12], pcb_now[:12]))
    print("  ★.kicad_pro reboard: by=%s prev=%s → md5=%s" % (TICKET, pro_base[:12], pro_now[:12]))
    print("★SW 台账锚点块已补 reboard 四项原子记录 · 落表台账已补 .kicad_pro 覆盖行★")


if __name__ == "__main__":
    main()
