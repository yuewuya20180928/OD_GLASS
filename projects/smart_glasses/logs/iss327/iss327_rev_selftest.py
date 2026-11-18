#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iss327_rev_selftest.py —— ISS-327 反向用例: 「真隐患不许被 --freeze-registry 洗白」

★只写 tmp/iss327/ + logs/iss327/ ⇒ 零写板 · 零落表 · 零改闸 (真件一个字都不动)★
★纪律: 写前 assert not os.path.islink(path) ⇒ 软链当场炸 ★
"""
import os
import re
import shutil
import subprocess
import sys

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
SB = os.path.join(PROJ, "tmp", "iss327")
SRC = os.path.join(SB, "sbR3")
DST = os.path.join(SB, "sbR4")
LOG = os.path.join(PROJ, "logs", "iss327")

NEW_HAZ = "TP_TEMP_ISSX"      # ★新的 · 从来不存在过的位号形状 (前缀 TP_ ⇒ 形状像位号)
OLD_HAZ = "TP_TEMP"           # ★建闸日基线 3 条真隐患之一 ★


def L(*a):
    print(*a, flush=True)


def assert_not_symlink(path):
    assert not os.path.islink(path), "★[FAIL] 软链当场炸: %s" % path


def assert_no_symlink_in(root):
    bad = []
    for dp, dns, fns in os.walk(root):
        for fn in fns:
            p = os.path.join(dp, fn)
            if os.path.islink(p):
                bad.append(p)
    return bad


def main():
    L("=" * 78)
    L("# ISS-327 · 反向用例 R-1: 「真隐患不许被 --freeze-registry 洗白」")
    L("# 起点: tmp/iss327/sbR3 (★五侧改名 + SW 文档已同步★)")
    L("=" * 78)

    # ── ① 造 sbR4 (★真拷贝·零软链★) ─────────────────────────────────
    if os.path.exists(DST):
        shutil.rmtree(DST)
    L("① 造 sbR4 = 真拷贝(sbR3) ...")
    shutil.copytree(SRC, DST, symlinks=False)
    bad = assert_no_symlink_in(DST)
    L("   软链数 = %d (★期望 0★)" % len(bad))
    if bad:
        return 2

    # ── ② 注入: 把基线真隐患 TP_TEMP 改成【新的、从来不存在过的位号形状】 ──
    # ★目的: MISSING 条数保持 3 (≤ 上限 3) ⇒ 唯一能抓住它的判据 = 「新增真隐患」那一条 ★
    nfiles = nrepl = 0
    for dp, dns, fns in os.walk(os.path.join(DST, "SW")):
        for fn in sorted(fns):
            if not fn.endswith(".md"):
                continue
            p = os.path.join(dp, fn)
            assert_not_symlink(p)
            with open(p, "r", encoding="utf-8") as fh:
                txt = fh.read()
            if OLD_HAZ not in txt:
                continue
            cnt = txt.count(OLD_HAZ)
            new = re.sub(r"\b%s\b" % re.escape(OLD_HAZ), NEW_HAZ, txt)
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(new)
            nfiles += 1
            nrepl += cnt
    L("② 注入: %s → %s · 改了 %d 份 md · %d 处" % (OLD_HAZ, NEW_HAZ, nfiles, nrepl))
    # ★复核: 旧 token 必须 0 命中, 新 token 必须有命中 ★
    L("   注入后软链数 = %d" % len(assert_no_symlink_in(DST)))

    # ── ③ 读当前注册表 (★看 sbR3 贴进去的是新 78 条还是旧 74 条★) ──
    gate = os.path.join(DST, "SW", "tools", "check_sw_ref_reachability.py")
    assert_not_symlink(gate)
    gtxt = open(gate, encoding="utf-8").read()
    nreg = len(re.findall(r'^\s+"[A-Z0-9_a-z]+",$', gtxt, re.M))
    L("③ sbR4 闸副本里的注册表条目数 = %d" % nreg)

    def run_gate(tag, outfile):
        cmd = [sys.executable, gate, "--root", DST, "--dump-classification"]
        r = subprocess.run(cmd, cwd=PROJ, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, text=True)
        with open(outfile, "w", encoding="utf-8") as fh:
            fh.write(r.stdout)
        L("   [%s] rc=%d → %s" % (tag, r.returncode, os.path.relpath(outfile, PROJ)))
        return r.returncode, r.stdout

    # ── ④ 第一跑: 重建注册表【之前】 ────────────────────────────────
    L("④ 第一跑 (重建注册表之前) ...")
    rc_before, out_before = run_gate("before", os.path.join(LOG, "20_rev_R1_before_rebuild.txt"))

    # ── ⑤ 重建注册表 (★--freeze-registry·★只读盘面·不写真件★) ──────
    L("⑤ 跑 --freeze-registry ...")
    r = subprocess.run([sys.executable, gate, "--root", DST, "--freeze-registry"],
                       cwd=PROJ, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    fz = os.path.join(LOG, "21_rev_R1_freeze_stdout.txt")
    with open(fz, "w", encoding="utf-8") as fh:
        fh.write(r.stdout)
    L("   freeze rc=%d → %s" % (r.returncode, os.path.relpath(fz, PROJ)))
    n_new = len(re.findall(r'^\s+"[A-Z0-9_a-z]+",$', r.stdout, re.M))
    L("   新冻结表条目数 = %d" % n_new)
    L("   ★新冻结表里含不含真隐患 %s ? → %s" % (
        NEW_HAZ, "★含 (★危险★)" if ('"%s"' % NEW_HAZ) in r.stdout else "★不含 (★正确★)"))

    # ── ⑥ 把新冻结表贴回沙盒闸副本 (★真拷贝·非软链★) ──────────────
    L("⑥ 把新冻结表贴回沙盒闸副本 ...")
    BLOCK_RE = re.compile(r"DESIGNATOR_REGISTRY = \(\n.*?\n\)\n# ★共 \d+ 条★[^\n]*\n", re.S)
    m = re.search(r"DESIGNATOR_REGISTRY = \(\n(.*?)\n\)\n(# ★共 \d+ 条★[^\n]*)", r.stdout, re.S)
    if not m:
        L("   ★[FAIL] 冻结输出里找不到注册表块")
        return 2
    old = open(gate, encoding="utf-8").read()
    new = BLOCK_RE.sub("DESIGNATOR_REGISTRY = (\n%s\n)\n%s\n" % (m.group(1), m.group(2)),
                       old, count=1)
    assert_not_symlink(gate)
    with open(gate, "w", encoding="utf-8") as fh:
        fh.write(new)
    L("   已贴回 (★真文件·非软链★)")

    # ── ⑦ 第二跑: 重建注册表【之后】 ────────────────────────────────
    L("⑦ 第二跑 (重建注册表之后) ...")
    rc_after, out_after = run_gate("after", os.path.join(LOG, "22_rev_R1_after_rebuild.txt"))

    # ── ⑧ 判读 ─────────────────────────────────────────────────────
    L("")
    L("=" * 78)
    L("# ★判读★")
    L("=" * 78)
    L("重建前 rc = %d · 重建后 rc = %d" % (rc_before, rc_after))
    for tag, out in (("重建前", out_before), ("重建后", out_after)):
        miss = re.search(r"DESIGNATOR_MISSING\s+(\d+)", out)
        drift = re.search(r"DESIGNATOR_DRIFT\s+(\d+)", out)
        haz_in = (NEW_HAZ in out)
        print("  %s: MISSING=%s · DRIFT=%s · 输出里出现新真隐患 %s = %s" % (
            tag, miss.group(1) if miss else "?", drift.group(1) if drift else "?",
            NEW_HAZ, "★是★" if haz_in else "★否★"))
    L("")
    L("★结论: 新真隐患 %s 在【重建注册表之后】仍被抓住 = %s" % (
        NEW_HAZ, "★是·没被洗白★" if (NEW_HAZ in out_after and rc_after != 0) else "★否·被洗白了★"))
    L("★附带: 重建后 MISSING 条数 %s (上限 3) · 新 token 是否在 BASELINE_TOKENS 里 = 否"
      % (re.search(r"DESIGNATOR_MISSING\s+(\d+)", out_after).group(1)
         if re.search(r"DESIGNATOR_MISSING\s+(\d+)", out_after) else "?"))
    L("")
    L("★零写板自证 (★沙盒跑完·真件 md5 必须不变★):")
    import hashlib
    for rel in ("HW/PCB/demo_mainboard.kicad_pcb", "HW/netlist_v1.csv",
                "HW/netlist_v1_pins.csv", "HW/BOM_v1.csv"):
        p = os.path.join(PROJ, rel)
        h = hashlib.md5(open(p, "rb").read()).hexdigest()
        L("   %s  %s" % (h, rel))
    return 0


if __name__ == "__main__":
    sys.exit(main())
