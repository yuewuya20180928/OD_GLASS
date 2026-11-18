#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""arm_reading_guard.py -- ★【读数体检: 任何一条臂的读数, 先过这把尺】★★★

★★**它要拦什么 (★今晚反复咬人的三个坑★)** ★★
  ① ★**`.kicad_pro` 不在板旁 ⇒ DRC 读数作废** ★★
     ★★**⇒ KiCad 读不到工程文件 ⇒ 退回默认 `min_track_width` = 0.20mm ⇒ ⇒ 0.15mm 走线全成【假 `track_width` 违规】★★
     ★★**⇒ 实测 (臂A `v76mv0`): 裸板 DRC 90 (87 条假 track_width + 3 条真) ⇒ 真值是 3** ★★
     ★★**⇒ 同一块板 md5 相同, DRC 读数却差 87 条 ⇒ ⇒ 这就是"读数纪律"要防的东西** ★★
  ② ★**同名 `.drc.json` 可能是【上一步输入板】的 DRC ⇒ 不是终板的** ★★
     ★★**⇒ 只能信 fresh DRC (★本脚本会自己跑一次★)** ★★
  ③ ★**裸板 unc 与终板 unc 不一样 (★链会修★) ⇒ ⇒ 只看裸板会判错** ★★
     ★★**⇒ 晋级判决必须看【终板】三数: DRC / unc(条+网名) / 名单闸** ★★

用法:
  python3 state/arm_reading_guard.py <板.kicad_pcb> [--label 名字]
      体检该板并打印【可用的读数】(★跑 fresh DRC★)
  python3 state/arm_reading_guard.py --check-env
      只检查工程文件是否齐 (★不跑 DRC★·快★)
"""
import json
import os
import shutil
import subprocess
import sys

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
REF_PRO = PROJ + "/HW/PCB/demo_mainboard.kicad_pro"
REF_PRL = PROJ + "/HW/PCB/demo_mainboard.kicad_prl"


def ensure_pro(board):
    """★把工程文件补到板旁 (★缺 ⇒ DRC 读数作废★)"""
    pro = board[:-len(".kicad_pcb")] + ".kicad_pro" if board.endswith(".kicad_pcb") else board + ".kicad_pro"
    prl = pro[:-len(".kicad_pro")] + ".kicad_prl"
    made = []
    for src, dst in ((REF_PRO, pro), (REF_PRL, prl)):
        if not os.path.exists(dst) and os.path.exists(src):
            shutil.copyfile(src, dst)
            made.append(os.path.basename(dst))
    return pro, made


def fresh_drc(board, out):
    cmd = ("bash state/kicad.sh pcb drc --output %s --severity-error --severity-warning "
           "--format json %s" % (out, board))
    subprocess.run(cmd, shell=True, cwd=PROJ, capture_output=True, text=True, timeout=1800)
    return os.path.exists(out)


def read_drc(path):
    d = json.load(open(path, encoding="utf-8"))
    import re
    u = d.get("unconnected_items") or []
    nets = set()
    for it in u:
        nets |= set(re.findall(r"\[([A-Za-z0-9_]+)\]", json.dumps(it, ensure_ascii=False)))
    return d, len(u), len(nets), d.get("violations") or []


def main():
    argv = sys.argv[1:]
    if "--check-env" in argv:
        bad = 0
        for b in argv:
            if b.startswith("--") or not b.endswith(".kicad_pcb"):
                continue
            pro = b[:-len(".kicad_pcb")] + ".kicad_pro"
            ok = os.path.exists(pro)
            print("  %s %s" % ("✔" if ok else "✘", os.path.basename(b)))
            if not ok:
                bad += 1
        return 1 if bad else 0

    if not argv:
        print(__doc__)
        return 2
    board = argv[0]
    label = ""
    if "--label" in argv:
        label = argv[argv.index("--label") + 1]
    if not os.path.exists(board):
        print("❌ 没有板: %s" % board)
        return 1

    pro, made = ensure_pro(board)
    if made:
        print("  ✓ 已补工程文件 (★规则同源·否则 DRC 假违规★): %s" % ", ".join(made))

    out = board + ".guard.drc.json"
    if not fresh_drc(board, out):
        print("❌ fresh DRC 没跑出来 ⇒ 读数不可信")
        return 2
    d, unc_items, unc_nets, viol = read_drc(out)
    print("═══ 读数体检 %s ═══" % (label or os.path.basename(board)))
    print("  板          : %s" % board)
    print("  ★DRC 违规   : %d" % len(viol))
    for x in viol[:6]:
        print("     - [%s] %s" % (x.get("type"), str(x.get("description"))[:100]))
    print("  ★unc        : %d 条 / %d 个网名" % (unc_items, unc_nets))
    print("  ★网名       : %s" % ", ".join(sorted(n for n in _nets(d))))
    if made:
        print("  ★★**注意: 刚补了 .kicad_pro ⇒ 上面的读数【才是有效的】(★补之前的读数作废★)** ★★")
    return 0


def _nets(d):
    import re
    s = set()
    for it in (d.get("unconnected_items") or []):
        s |= set(re.findall(r"\[([A-Za-z0-9_]+)\]", json.dumps(it, ensure_ascii=False)))
    return s


if __name__ == "__main__":
    sys.exit(main())
