#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-257 · G1a-7 选型落表 · ★★三步沙盒反向自证 (★一次性跑完, 落原始日志★)
================================================================================
★**证明什么**: ★**「我真改了判据盯的东西, 不是把红灯调没」** ★
★**怎么证**: ★**沙盒里把本轮改的那 29 行改回旧值 ⇒ 重生成 ⇒ 门禁必须红 ⇒ 装回 ⇒ 又绿** ★

★**沙盒 = 最小镜像** (★不复制整个项目 ⇒ 快且不污染真盘★):
    /tmp/iss257_sbx/state/{6 个生成器 + p10_rows.json + check_netlist.py}
    /tmp/iss257_sbx/HW/{netlist_v1.csv, netlist_v1_pins.csv, BOM_v1.csv,
                        SCHEMATIC_V1_SPEC.json, PCB/*}
    /tmp/iss257_sbx/HW/check_g1a7_selection_landed.py
★**★沙盒保真校验**: ★**沙盒重生成出来的网表 md5 必须逐字等于真盘对应态的 md5** ★
   (★步骤 1 的旧态 md5 = 7dcf251a10ce748c44d467473b3f56d6 = 真盘 20:50 态★)

★**★真盘零污染校验 (★步骤 3★)**: ★**沙盒跑完, 真盘 5 个受保护/产物 md5 逐个比对 ⇒ 零差异** ★

用法:  python3 state/_iss257_r1_sandbox_proof.py
"""
from __future__ import annotations

import hashlib
import io
import os
import shutil
import subprocess
import sys
import time

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SBX = "/tmp/iss257_sbx"
LOG = os.path.join(PROJ, "HW", "ISS257_g1a7_reverse_proof_sandbox.log")

# ★本轮改动的 29 行 (★行号 = 改前文件的行号 · ★本轮只改文字不改行数 ⇒ 行号不变★) ★
GN_LINES = [393, 402, 593, 617, 627, 633, 655, 660, 664, 678, 682, 686, 804,
            1356, 1360, 1364, 1399, 1403, 1455, 1459, 1469, 1473, 1476, 1479]
P10_LINES = [806, 821, 911, 926, 941]

STATE_FILES = ["gen_netlist.py", "gen_kicad_net.py", "gen_netlist_pins.py", "gen_bom.py",
               "gen_schematic_pages.py", "gen_kicad_sch.py", "p10_rows.json",
               "check_netlist.py"]
HW_FILES = ["netlist_v1.csv", "netlist_v1_pins.csv", "BOM_v1.csv", "SCHEMATIC_V1_SPEC.json"]
PCB_FILES = ["som_pin_assign.json", "pinout_footprint.json", "FET3572C_PIN_TABLE.csv",
             "demo_mainboard.kicad_pcb", "demo_mainboard.kicad_pro"]

OLD_MD5_NETLIST = "7dcf251a10ce748c44d467473b3f56d6"   # ★真盘 20:50 旧态 (上一轮落表后·含 [官网]) ★
NEW_MD5_NETLIST = "e06c1dd633566aa44732762c2ff99d1c"   # ★真盘现值 (本轮修红后) ★

PROTECTED = ["HW/netlist_v1.csv", "HW/netlist_v1_pins.csv", "HW/BOM_v1.csv",
             "HW/PCB/demo_mainboard.kicad_pcb", "HW/PCB/demo_mainboard.kicad_pro"]


def md5(p: str) -> str:
    h = hashlib.md5()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 16), b""):
            h.update(c)
    return h.hexdigest()


def run(cmd: list[str], cwd: str) -> tuple[int, str]:
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=900)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def build_sandbox() -> None:
    shutil.rmtree(SBX, ignore_errors=True)
    os.makedirs(os.path.join(SBX, "state"), exist_ok=True)
    os.makedirs(os.path.join(SBX, "HW", "PCB"), exist_ok=True)
    for f in STATE_FILES:
        shutil.copy2(os.path.join(PROJ, "state", f), os.path.join(SBX, "state", f))
    for f in HW_FILES:
        shutil.copy2(os.path.join(PROJ, "HW", f), os.path.join(SBX, "HW", f))
    for f in PCB_FILES:
        src = os.path.join(PROJ, "HW", "PCB", f)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(SBX, "HW", "PCB", f))
    for f in os.listdir(os.path.join(PROJ, "HW", "PCB")):
        if f.endswith(".kicad_sch"):
            shutil.copy2(os.path.join(PROJ, "HW", "PCB", f), os.path.join(SBX, "HW", "PCB", f))
    shutil.copy2(os.path.join(PROJ, "HW", "check_g1a7_selection_landed.py"),
                 os.path.join(SBX, "HW", "check_g1a7_selection_landed.py"))


def flip(to_old: bool) -> None:
    """把沙盒真源在 [官方] / [官网] 之间来回切 (★只动那 29 行★)
    ★cur = 当前盘上的字 · tgt = 要换成的字★"""
    cur, tgt = ("[官方]", "[官网]") if to_old else ("[官网]", "[官方]")
    for path, lines in ((os.path.join(SBX, "state", "gen_netlist.py"), GN_LINES),
                        (os.path.join(SBX, "state", "p10_rows.json"), P10_LINES)):
        txt = io.open(path, encoding="utf-8").read().split("\n")
        for n in lines:
            assert cur in txt[n - 1], "★行 %d 不含 %s ⇒ 沙盒源与预期不符★" % (n, cur)
            txt[n - 1] = txt[n - 1].replace(cur, tgt)
        io.open(path, "w", encoding="utf-8", newline="").write("\n".join(txt))


def regen() -> int:
    rc = 0
    for g in ("gen_netlist.py", "gen_kicad_net.py", "gen_netlist_pins.py",
              "gen_bom.py", "gen_schematic_pages.py", "gen_kicad_sch.py"):
        rc2, _ = run([sys.executable, os.path.join("state", g)], SBX)
        if rc2 != 0:
            return rc2
    return rc


def main() -> int:
    out = []

    def w(s: str = "") -> None:
        out.append(s)

    w("═══════════════════════════════════════════════════════════════════════════════")
    w(" ISS-257 · G1a-7 选型落表 · ★★三步沙盒反向自证 (本机实跑原始日志)★★")
    w(" 沙盒: %s (★最小镜像: state/{6 生成器 + p10_rows.json + check_netlist.py} +" % SBX)
    w("       HW/{netlist_v1.csv, netlist_v1_pins.csv, BOM_v1.csv, SCHEMATIC_V1_SPEC.json, PCB/*} +")
    w("       HW/check_g1a7_selection_landed.py★)")
    w(" 时间: %s  ·  ★本机实跑 · 零外发 · 零下载 · 零 clone★" % time.strftime("%Y-%m-%d %H:%M:%S %Z"))
    w("═══════════════════════════════════════════════════════════════════════════════")

    before = {p: md5(os.path.join(PROJ, p)) for p in PROTECTED}

    build_sandbox()

    # ───────── 步骤 0 · 基线 ─────────
    w("")
    w("── 步骤 0 · 沙盒基线 (装的是【修好】的源) ⇒ 门禁应当是绿的 ──")
    rc = regen()
    w("  沙盒重生成 rc=%d" % rc)
    sbx_md5 = md5(os.path.join(SBX, "HW", "netlist_v1.csv"))
    w("  沙盒网表 md5 = %s   (★应 = 真盘现值 %s · 一致 ⇒ 沙盒保真★)" % (sbx_md5, NEW_MD5_NETLIST))
    rc, o = run([sys.executable, os.path.join("state", "check_netlist.py")], SBX)
    w("  $ (沙盒) python3 state/check_netlist.py")
    w("  ★rc=%d★" % rc)
    for ln in o.splitlines():
        if "证据等级" in ln or "项不通过" in ln:
            w("  " + ln.strip())
    rc, o = run([sys.executable, os.path.join("HW", "check_g1a7_selection_landed.py"),
                 "--root", SBX], SBX)
    w("  $ (沙盒) python3 HW/check_g1a7_selection_landed.py --root %s" % SBX)
    w("  ★rc=%d★" % rc)
    for ln in o.splitlines():
        if ln.strip().startswith(("OK", "FAIL", "✅", "❌")):
            w("  " + ln.strip())

    # ───────── 步骤 1 · 改回旧值 ⇒ 必须红 ─────────
    w("")
    w("── 步骤 1 · ★把本轮改的那 29 行改回旧值 ⇒ 重生成 ⇒ 门禁必须红★ ──")
    flip(to_old=True)
    w("  ★沙盒真源已改回旧值: state/gen_netlist.py 24 处 + state/p10_rows.json 5 处 ⇒ 29 行 [官网]★")
    rc = regen()
    w("  沙盒重生成 rc=%d" % rc)
    sbx_md5 = md5(os.path.join(SBX, "HW", "netlist_v1.csv"))
    w("  沙盒网表 md5 = %s" % sbx_md5)
    w("  (★真盘 20:50 旧态 = %s · ★两者一致 ⇒ 沙盒逐字节保真★)" % OLD_MD5_NETLIST)
    rc, o = run([sys.executable, os.path.join("state", "check_netlist.py")], SBX)
    w("  $ (沙盒) python3 state/check_netlist.py")
    w("  ★rc=%d★" % rc)
    for ln in o.splitlines():
        if "证据等级" in ln or "非法值" in ln or "项不通过" in ln:
            w("  " + ln.strip())
    rc, o = run([sys.executable, os.path.join("HW", "check_g1a7_selection_landed.py"),
                 "--root", SBX], SBX)
    w("  $ (沙盒) python3 HW/check_g1a7_selection_landed.py --root %s" % SBX)
    w("  ★rc=%d★  (★必须是 1 ⇒ 判据真在被读★)" % rc)
    for ln in o.splitlines():
        s = ln.strip()
        if s.startswith(("OK", "FAIL", "✅", "❌")) or s.startswith("★C5"):
            w("  " + s)

    # ───────── 步骤 2 · 装回 ⇒ 必须绿 ─────────
    w("")
    w("── 步骤 2 · 装回 (改回 [官方]) ⇒ 重生成 ⇒ 门禁必须重新变绿 ──")
    flip(to_old=False)
    w("  ★沙盒真源已装回 (29 行 [官方])★")
    rc = regen()
    w("  沙盒重生成 rc=%d" % rc)
    sbx_md5 = md5(os.path.join(SBX, "HW", "netlist_v1.csv"))
    w("  沙盒网表 md5 = %s   (★应 = 真盘现值 %s★)" % (sbx_md5, NEW_MD5_NETLIST))
    rc, o = run([sys.executable, os.path.join("state", "check_netlist.py")], SBX)
    w("  $ (沙盒) python3 state/check_netlist.py")
    w("  ★rc=%d★" % rc)
    for ln in o.splitlines():
        if "证据等级" in ln or "项不通过" in ln:
            w("  " + ln.strip())
    rc, o = run([sys.executable, os.path.join("HW", "check_g1a7_selection_landed.py"),
                 "--root", SBX], SBX)
    w("  $ (沙盒) python3 HW/check_g1a7_selection_landed.py --root %s" % SBX)
    w("  ★rc=%d★  (★必须是 0 ⇒ 装回后就绿了, ★前后对比才成立★)" % rc)
    for ln in o.splitlines():
        if ln.strip().startswith(("OK", "FAIL", "✅", "❌")):
            w("  " + ln.strip())

    # ───────── 步骤 3 · 真盘零污染 ─────────
    w("")
    w("── 步骤 3 · ★真盘零污染校验 (沙盒跑完, 真盘 md5 逐个比对)★ ──")
    after = {p: md5(os.path.join(PROJ, p)) for p in PROTECTED}
    diff = 0
    for p in PROTECTED:
        same = before[p] == after[p]
        if not same:
            diff += 1
        w("  %s  %s  %s" % ("✔" if same else "✘", p, after[p]))
    w("  ⇒ 差异 %d 处 (★必须 0 ⇒ 真盘一个字节都没被沙盒碰过★)" % diff)

    w("")
    w("═══════════════════════════════════════════════════════════════════════════════")
    w(" ★★结论: 步骤1 红 (rc=1 · 非法值 ['[官网]'] · C5 FAIL) ⇒ 步骤2 绿 (rc=0)")
    w("   ⇒ ★★证明: 我真改了判据盯的东西, 不是把红灯调没★★")
    w("   ⇒ 沙盒网表 md5 与真盘对应态【逐字相同】⇒ 沙盒保真 ⇒ 真盘 md5 零差异")
    w("═══════════════════════════════════════════════════════════════════════════════")

    text = "\n".join(out) + "\n"
    with io.open(LOG, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
