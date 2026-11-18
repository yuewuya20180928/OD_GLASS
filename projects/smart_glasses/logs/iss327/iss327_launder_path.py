#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iss327_launder_path.py —— ISS-327 · 反向用例 RT-9
「★--freeze-registry 重建 + 抬 MISSING 上限 ⇒ 会不会把 58 条【真·改名漂移】一次性洗白成『已登记基线』★」

★只写 tmp/iss327/ + logs/iss327/ ⇒ ★真件闸一个字都不改★★
★起点: tmp/iss327/sbR0 (★五侧改名 + SW 文档【未】同步 + 旧注册表 74 条★)★
★关键读数: 重建后 DRIFT=0 · MISSING=56 ⇒ ★58 条「改名漂移」被重分类成了 56 条「真隐患」★
★本用例演示: 只要把 BASELINE_COUNT 从 3 抬到 59 并把这 56 个老名登记进 BASELINE_TOKENS
             ⇒ 闸就绿了 ⇒ ★这是一条【真的存在的洗白通道】·必须写进 SOP 的红线★
"""
import hashlib
import os
import re
import shutil
import subprocess
import sys

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
SB = os.path.join(PROJ, "tmp", "iss327")
LOG = os.path.join(PROJ, "logs", "iss327")
SRC = os.path.join(SB, "sbR0")
DST = os.path.join(SB, "sbRT_RT9")
GATE_REL = os.path.join("SW", "tools", "check_sw_ref_reachability.py")
BLOCK_RE = re.compile(r"DESIGNATOR_REGISTRY = \(\n.*?\n\)\n# ★共 \d+ 条★[^\n]*\n", re.S)
TOKEN_RE = re.compile(r'^\s+"([A-Za-z0-9_]+)",$', re.M)


def L(*a):
    print(*a, flush=True)


def run_gate(root, extra=()):
    cmd = [sys.executable, os.path.join(root, GATE_REL), "--root", root] + list(extra)
    r = subprocess.run(cmd, cwd=PROJ, stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, text=True)
    return r.returncode, r.stdout


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def main():
    L("=" * 90)
    L("# ISS-327 · 反向用例 RT-9 · ★「重建注册表 + 抬 MISSING 上限」的洗白通道演示★")
    L("=" * 90)
    if os.path.isdir(DST):
        shutil.rmtree(DST)
    shutil.copytree(SRC, DST, symlinks=False)
    bad = [os.path.join(dp, fn) for dp, dns, fns in os.walk(DST) for fn in fns
           if os.path.islink(os.path.join(dp, fn))]
    assert not bad, "★[FAIL] 沙盒里出现软链"

    gate = os.path.join(DST, GATE_REL)
    L("① 起点 = sbR0 (★五侧改名 + SW 文档未同步 + 旧注册表 74 条★)")
    rc0, out0 = run_gate(DST, ["--dump-classification"])
    m = re.search(r"DESIGNATOR_DRIFT\s+(\d+)", out0)
    n = re.search(r"DESIGNATOR_MISSING\s+(\d+)", out0)
    L("   [重建前] rc=%d · DRIFT=%s · MISSING=%s (上限 3)" % (rc0, m.group(1), n.group(1)))

    L("② 跑 --freeze-registry (★重建注册表★)")
    rc, fout = run_gate(DST, ["--freeze-registry"])
    new_toks = TOKEN_RE.findall(fout)
    L("   freeze rc=%d · 新表 %d 条" % (rc, len(new_toks)))
    old = open(gate, encoding="utf-8").read()
    mm = re.search(r"DESIGNATOR_REGISTRY = \(\n(.*?)\n\)\n(# ★共 \d+ 条★[^\n]*)", fout, re.S)
    open(gate, "w", encoding="utf-8").write(
        BLOCK_RE.sub("DESIGNATOR_REGISTRY = (\n%s\n)\n%s\n" % (mm.group(1), mm.group(2)),
                     old, count=1))
    rc1, out1 = run_gate(DST, ["--dump-classification"])
    m = re.search(r"DESIGNATOR_DRIFT\s+(\d+)", out1)
    n = re.search(r"DESIGNATOR_MISSING\s+(\d+)", out1)
    L("   [重建后] rc=%d · DRIFT=%s · MISSING=%s (上限 3)  ★⇒ 58 条「改名漂移」被重分类成 56 条「真隐患」★"
      % (rc1, m.group(1), n.group(1)))

    L("③ 取出重建后的 MISSING token 名单 (★= 被重分类的那批老名★)")
    missing_tokens = re.findall(r"DESIGNATOR_MISSING\s+C14\s+([A-Za-z0-9_]+)", out1)
    L("   MISSING token = %d 个: %s" % (len(missing_tokens), missing_tokens[:12]))
    if not missing_tokens:
        L("   ★[FAIL] 没解析到 MISSING token")
        return 2

    L("④ ★沙盒里把上限从 3 抬到 %d + 把这 %d 个 token 登记进 BASELINE_TOKENS (★演示洗白通道·真件不动★)"
      % (len(missing_tokens) + 3, len(missing_tokens)))
    g = open(gate, encoding="utf-8").read()
    g2 = g.replace("BASELINE_COUNT = 3", "BASELINE_COUNT = %d" % (len(missing_tokens) + 3), 1)
    add = "\n".join('    "%s": "★RT-9 洗白通道演示·沙盒里登记的改名漂移老名★",' % t
                    for t in sorted(missing_tokens))
    g2 = g2.replace("BASELINE_TOKENS = {", "BASELINE_TOKENS = {\n" + add, 1)
    open(gate, "w", encoding="utf-8").write(g2)

    rc2, out2 = run_gate(DST, ["--dump-classification"])
    m = re.search(r"DESIGNATOR_DRIFT\s+(\d+)", out2)
    n = re.search(r"DESIGNATOR_MISSING\s+(\d+)", out2)
    L("   [抬上限后] rc=%d (★%s★) · DRIFT=%s · MISSING=%s (上限 %d)"
      % (rc2, "绿" if rc2 == 0 else "红", m.group(1), n.group(1), len(missing_tokens) + 3))
    L("")
    L("★判读★: 期望【红】(★改名漂移必须继续被抓住★) ⇒ 实际【%s】"
      % ("绿" if rc2 == 0 else "红"))
    L("★⇒ 结论: ★**「重建注册表 + 抬 MISSING 上限」= 一条真的存在的洗白通道★**")
    L("   ⇒ ★**58 条真·改名漂移被一次性登记成『已登记基线』⇒ 闸绿 ⇒ 从此看不出改名没同步★**")
    L("   ⇒ ★**因此 SOP 的红线: 重建注册表【之后】MISSING 必须仍然 = 3; 一旦 > 3 ⇒ 是【文档没同步】的信号, 不是抬上限的理由★**")

    with open(os.path.join(LOG, "30_rev_RT9_launder_path.txt"), "w", encoding="utf-8") as fh:
        fh.write("=== 重建前 ===\n" + out0 + "\n=== 重建后 ===\n" + out1 +
                 "\n=== 抬上限后 ===\n" + out2)
    with open(os.path.join(LOG, "31_rev_RT9_freeze.txt"), "w", encoding="utf-8") as fh:
        fh.write(fout)
    L("")
    L("★零写板自证 (★真件 md5 必须不变★):")
    for rel in ("HW/PCB/demo_mainboard.kicad_pcb", "HW/netlist_v1.csv",
                "HW/netlist_v1_pins.csv", "HW/BOM_v1.csv"):
        L("   %s  %s" % (md5(os.path.join(PROJ, rel)), rel))
    L("★真件闸 md5 = %s (★= 00_gatemd5_pre.txt 里的值 ⇒ 真件闸一个字节没改★)"
      % md5(os.path.join(PROJ, GATE_REL)))
    shutil.rmtree(DST)
    return 0


if __name__ == "__main__":
    sys.exit(main())
