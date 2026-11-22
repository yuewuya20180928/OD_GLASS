#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
reverse_case.py —— ISS-344 新闸的反向用例 (★沙盒纪律: 只在 tmp/ 副本上做★)
================================================================================
★**干什么**: ★**在 `tmp/iss344/rev/` 的副本上, 把 §3 表里某条【必需】网的「建议的板侧标记」
  改回「NC (不连)」⇒ ★**闸必须判红并点名那条网名** ⇒ 然后恢复 ⇒ ★**闸必须判绿** ★

★**沙盒纪律 (★本项目铁律★)**: ★**真件 `SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md`
  一个字节都不许在反向用例里被动** ★ ⇒ ★**本脚本跑完会核对真件 md5 与开工前一致** ★

★**用法**: python3 logs/iss344/reverse_case.py [网名] (★默认 `JTAG_TDI`★)
"""
import hashlib
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(HERE))
REAL = os.path.join(PROJ, "SW", "ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md")
GATE = os.path.join(PROJ, "SW", "tools", "check_sw_zero_copper_grade_consistency.py")
REV_DIR = os.path.join(PROJ, "tmp", "iss344", "rev")
REV_DOC = os.path.join(REV_DIR, "ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md")

CORR = "【ISS344-CORR】"
CORR_END = "【/ISS344-CORR】"


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def pipe_positions(line):
    out = []
    i = 0
    while i < len(line):
        if line[i] == "|" and (i == 0 or line[i - 1] != "\\"):
            out.append(i)
        i += 1
    return out


def run_gate(doc):
    r = subprocess.run([sys.executable, GATE, "--doc", doc],
                       cwd=PROJ, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return r.returncode, r.stdout.decode("utf-8", "ignore")


def revert_mark_cell(lines, net):
    """把 §3 表里 net 那一行的【最后一格】(建议的板侧标记) 里的订正块删掉
    ⇒ 该格回到订正前的原样 (含「NC (不连)」)"""
    hit = 0
    for i, l in enumerate(lines):
        if not l.startswith("|"):
            continue
        ps = pipe_positions(l)
        if len(ps) < 3:
            continue
        cell0 = l[ps[0] + 1:ps[1]]
        m = re.search(r"`([^`]+)`", cell0)
        if not m or m.group(1).strip() != net:
            continue
        s, e = ps[-2] + 1, ps[-1]
        cell = l[s:e]
        if CORR not in cell:
            continue
        newcell = re.sub(re.escape(CORR) + ".*?" + re.escape(CORR_END), "", cell, flags=re.S)
        lines[i] = l[:s] + newcell + l[e:]
        hit += 1
    return hit


def main():
    net = sys.argv[1] if len(sys.argv) > 1 else "JTAG_TDI"
    md5_real_before = md5(REAL)
    os.makedirs(REV_DIR, exist_ok=True)
    shutil.copyfile(REAL, REV_DOC)

    print("═══ ISS-344 新闸 · 反向用例 (★只在 tmp/ 副本上做·真件不动★) ═══")
    print("  真件     : %s" % REAL)
    print("  真件 md5 (开工前): %s" % md5_real_before)
    print("  副本     : %s" % REV_DOC)
    print("  目标网   : %s (★REQUIRED_SINGLE 里的必需网★)" % net)

    # ① 基线: 副本必须是绿的
    rc0, out0 = run_gate(REV_DOC)
    print("\n── ① 基线 (副本 = 订正后的样子) ──")
    print(out0.rstrip())
    print("  ⇒ BASELINE_RC=%d (★期望 0★)" % rc0)

    # ② 反向: 把 §3 表该条的「建议的板侧标记」改回「NC (不连)」
    lines = open(REV_DOC, encoding="utf-8").read().split("\n")
    n = revert_mark_cell(lines, net)
    with open(REV_DOC, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("\n── ② 反向注入: §3 表 %s 的「建议的板侧标记」改回「NC (不连)」 (★改了 %d 处★) ──"
          % (net, n))
    rc1, out1 = run_gate(REV_DOC)
    print(out1.rstrip())
    print("  ⇒ REVERSE_RC=%d (★期望 1=判红★)" % rc1)
    named = ("✘ [C2] %s " % net) in out1 or ("✘ [C1] %s " % net) in out1 \
        or ("✘ [C3] %s " % net) in out1 or ("✘ [C0] %s " % net) in out1
    print("  ⇒ 点名了 %s ? %s" % (net, "✔ 是" if named else "✘ 否"))

    # ③ 恢复 ⇒ 必须绿
    shutil.copyfile(REAL, REV_DOC)
    rc2, out2 = run_gate(REV_DOC)
    print("\n── ③ 恢复 (副本 = 订正后的样子) ──")
    tail = [l for l in out2.split("\n") if l.startswith("★★结论")]
    for l in tail:
        print("  " + l)
    print("  ⇒ RESTORE_RC=%d (★期望 0=判绿★)" % rc2)

    # ④ 真件没被动
    md5_real_after = md5(REAL)
    print("\n── ④ 真件零被动自证 ──")
    print("  真件 md5 (开工前) = %s" % md5_real_before)
    print("  真件 md5 (跑完后) = %s" % md5_real_after)
    print("  ⇒ 真件逐字节未动 ? %s" % ("✔ 是" if md5_real_before == md5_real_after else "✘ 否"))

    ok = (rc0 == 0 and rc1 == 1 and named and rc2 == 0
          and md5_real_before == md5_real_after)
    print("\n★★结论: ★**反向用例 %s** ★" % ("成立 ✔ (判红并点名 %s·恢复后判绿·真件零被动)" % net
                                        if ok else "★不成立★"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
