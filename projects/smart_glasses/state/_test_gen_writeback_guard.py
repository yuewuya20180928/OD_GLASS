#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_test_gen_writeback_guard.py -- ★★【守卫】state/gen_kicad_project.py 的「内容等价就不写」守卫★★ ★

★★★**这个守卫守住什么 (★ISS-280 同型复发·2026-11-18 17:0x main 修于产生点★)** ★★★
★**病根**: 生成器 4 处无条件写盘 ⇒ 任何跑 `check_pcb_drc.py` 的动作 (臂跑链 / daily_check / chain_gate)
★          都改 `HW/PCB/` 下 4 个产物的 mtime+md5 ⇒ ① 用 mtime 判「有没有被改过」的判据【永久失效】
★          ② 每次巡检都制造一次假变更 ⇒ 「零写板双证」这类自证要每次重做一遍
★★★**守卫判据 (★三条都要, 缺一条就红★)** ★★★
★ ① **正向**: 内容等价 ⇒ **第二次跑不许写** (mtime + md5 双不变) ⇒ ★跑在【沙盒目录】, 一个字节都不碰真件★
★ ② **反向**: 内容真变了 ⇒ **必须照写** (⇒ 守卫不是"永远不写"的假绿)
★ ③ **真件零写**: 守卫自己跑完之后, `HW/PCB/` 下那 4 个文件的 md5+mtime **逐个不变**
★★**反向用例怎么造 (★不许靠"手改真件"★)**: ★在沙盒里手改【沙盒副本】的 STACKUP.md ⇒
★★   下一次跑生成器 ⇒ 它必须被【改回成生成器的真内容】⇒ 证明守卫只在"内容等价"时沉默, 真变了照写★★

★**用法**: `python3 state/_test_gen_writeback_guard.py` (★沙盒自测·不碰真件★) ⇒ rc=0 全过 / rc=1 有红项
★**反向自检**: ★把守卫改坏 (★去掉"等价就不写"★) ⇒ 本脚本必须红 ⇒ ⇒ 本脚本自己也有反向用例★
"""
from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
GEN = os.path.join(HERE, "gen_kicad_project.py")
PCB_DIR = os.path.join(PROJ, "HW", "PCB")
ARTIFACTS = ("STACKUP.md", "LAYOUT_RULES.md", "GEN_SELF_CHECK.txt", "_frame_reference.kicad_pcb")

fails: list[str] = []


def _md5(p: str) -> str:
    with open(p, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def _snap(d: str) -> dict:
    out = {}
    for name in ARTIFACTS:
        p = os.path.join(d, name)
        if os.path.exists(p):
            st = os.stat(p)
            out[name] = (_md5(p), st.st_mtime_ns, st.st_size)
        else:
            out[name] = None
    return out


def _run_gen(out_dir: str) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["PCB_DOC_OUT"] = out_dir
    return subprocess.run([sys.executable, GEN], cwd=PROJ, env=env,
                          capture_output=True, text=True, timeout=300)


def main() -> int:
    # ---------- 真件基线 (守卫自己不许碰真件) ----------
    real_before = _snap(PCB_DIR)

    tmp = tempfile.mkdtemp(prefix="genwb_")
    try:
        # ---------- ① 正向: 第一次跑 = 写 (沙盒) ----------
        r1 = _run_gen(tmp)
        if r1.returncode != 0:
            fails.append("★沙盒第 1 次跑生成器 rc=%d (期望 0): %s"
                         % (r1.returncode, (r1.stderr or r1.stdout)[-300:]))
        s1 = _snap(tmp)
        missing = [n for n in ARTIFACTS if s1.get(n) is None]
        if missing:
            fails.append("★沙盒第 1 次跑后缺产物: %s" % missing)

        # ---------- ① 正向: 第二次跑 = 不许写 (mtime+md5 双不变) ----------
        r2 = _run_gen(tmp)
        if r2.returncode != 0:
            fails.append("★沙盒第 2 次跑生成器 rc=%d (期望 0): %s"
                         % (r2.returncode, (r2.stderr or r2.stdout)[-300:]))
        s2 = _snap(tmp)
        changed = [n for n in ARTIFACTS if s1.get(n) != s2.get(n)]
        if changed:
            fails.append("★★【守卫失效】第 2 次跑【内容等价】却改写了: %s ⇒ "
                         "⇒ '内容等价就不写' 没生效 ⇒ 巡检仍会每天改这 4 个产物的 mtime" % changed)

        # ---------- ② 反向: 内容真变了 ⇒ 必须照写 (不许"永远不写") ----------
        # ★在沙盒里手改 STACKUP.md ⇒ 下一次跑生成器必须把它改回真内容★
        sp = os.path.join(tmp, "STACKUP.md")
        tampered = False
        if os.path.exists(sp):
            with open(sp, "a", encoding="utf-8") as f:
                f.write("\n<!-- TAMPERED-BY-GUARD-SELFTEST -->\n")
            tampered = True
        if tampered:
            r3 = _run_gen(tmp)
            if r3.returncode != 0:
                fails.append("★沙盒第 3 次跑生成器 rc=%d (期望 0): %s"
                             % (r3.returncode, (r3.stderr or r3.stdout)[-300:]))
            body = open(sp, encoding="utf-8").read() if os.path.exists(sp) else ""
            if "TAMPERED-BY-GUARD-SELFTEST" in body:
                fails.append("★★【反向用例失败】内容真变了 (手改过) 却【没被写回】⇒ "
                             "⇒ 守卫变成'永远不写' ⇒ 真内容变化会被静默吞掉 ⇒ 比原缺陷更坏")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # ---------- ③ 真件零写 ----------
    real_after = _snap(PCB_DIR)
    touched = [n for n in ARTIFACTS if real_before.get(n) != real_after.get(n)]
    if touched:
        fails.append("★★【真件被写】守卫跑完之后 HW/PCB/ 下这 4 个文件变了: %s" % touched)

    for f in fails:
        print("[FAIL] " + f)
    if fails:
        print("★★守卫自测: 红 (%d 条)" % len(fails))
        return 1
    print("✅ 守卫自测: 绿")
    print("   · ① 正向: 内容等价 ⇒ 第 2 次跑 4 个产物 mtime+md5 全不变 (沙盒)")
    print("   · ② 反向: 内容真变 ⇒ 照写 (沙盒手改 STACKUP.md ⇒ 被写回真内容)")
    print("   · ③ 真件: HW/PCB/ 下 4 个产物 md5+mtime 逐个未变")
    return 0


# ★★【反向自检 (★证明本守卫自己不是假绿★)】★★
def reverse_proof() -> int:
    """★把【旧版生成器 (无条件写盘)】与【新版生成器 (内容等价就不写)】各放进【假项目】里跑两遍★
    ★★ 期望: 旧版 ⇒ 第 2 次跑【改了】mtime (缺陷复现 ⇒ 本守卫的正向判据【能抓住它】)
    ★★         新版 ⇒ 第 2 次跑【没改】mtime (修复生效)
    ★★ 全部在 tmp 假项目里 ⇒ **一个字节都不碰真件** ★★"""
    old_gen = GEN + ".bak_20261118_1700_main_writeback_guard"
    if not os.path.exists(old_gen):
        print("[FAIL] ★找不到旧版生成器备份: %s ⇒ 反向自检无法做" % os.path.basename(old_gen))
        return 1
    board = os.path.join(PCB_DIR, "demo_mainboard.kicad_pcb")
    params = os.path.join(PCB_DIR, "demo_mainboard_params.json")
    imp = os.path.join(PCB_DIR, "STACKUP_IMPEDANCE.md")
    tmp = tempfile.mkdtemp(prefix="genwb_rev_")
    fails2: list[str] = []
    try:
        for label, gen_src in (("旧版(缺陷)", old_gen), ("新版(已修)", GEN)):
            fake = os.path.join(tmp, label)
            os.makedirs(os.path.join(fake, "state"), exist_ok=True)
            os.makedirs(os.path.join(fake, "HW", "PCB"), exist_ok=True)
            shutil.copy2(gen_src, os.path.join(fake, "state", "gen_kicad_project.py"))
            shutil.copy2(os.path.join(HERE, "read_board_stackup.py"),
                         os.path.join(fake, "state", "read_board_stackup.py"))
            shutil.copy2(params, os.path.join(fake, "HW", "PCB", "demo_mainboard_params.json"))
            shutil.copy2(board, os.path.join(fake, "HW", "PCB", "demo_mainboard.kicad_pcb"))
            if os.path.exists(imp):
                shutil.copy2(imp, os.path.join(fake, "HW", "PCB", "STACKUP_IMPEDANCE.md"))
            outdir = os.path.join(fake, "HW", "PCB")
            a = _run_gen_at(os.path.join(fake, "state", "gen_kicad_project.py"), outdir)
            s_a = _snap(outdir)
            b = _run_gen_at(os.path.join(fake, "state", "gen_kicad_project.py"), outdir)
            s_b = _snap(outdir)
            changed = [n for n in ARTIFACTS if s_a.get(n) != s_b.get(n)]
            if label.startswith("旧版"):
                if not changed:
                    fails2.append("★★旧版生成器第 2 次跑竟然没改 mtime ⇒ 缺陷没复现 ⇒ "
                                   "⇒ 本守卫的正向判据【抓不住真缺陷】⇒ 守卫形同虚设")
                else:
                    print("   · 反向: 旧版生成器第 2 次跑改了 %d 个产物的 mtime+md5 (缺陷复现 ✓)" % len(changed))
            else:
                if changed:
                    fails2.append("★★新版生成器第 2 次跑仍改了 %s ⇒ 修复无效" % changed)
                else:
                    print("   · 反向: 新版生成器第 2 次跑 0 个产物变化 (修复生效 ✓)")
            for rc in (a, b):
                if rc.returncode != 0:
                    fails2.append("★假项目[%s] 跑生成器 rc=%d" % (label, rc.returncode))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    for f in fails2:
        print("[FAIL] " + f)
    if fails2:
        print("★★反向自检: 红 (%d 条)" % len(fails2))
        return 1
    print("✅ 反向自检: 绿 (守卫能区分【旧版缺陷】与【新版修复】)")
    return 0


def _run_gen_at(gen_path: str, out_dir: str) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["PCB_DOC_OUT"] = out_dir
    return subprocess.run([sys.executable, gen_path], cwd=PROJ, env=env,
                          capture_output=True, text=True, timeout=300)


if __name__ == "__main__":
    if "--reverse-proof" in sys.argv:
        sys.exit(reverse_proof())
    sys.exit(main())
