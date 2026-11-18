#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-326 · MECH 侧「崩 / 假绿」沙盒实证 (★4 条反向用例★)

★★铁律★★: 判据脚本 + 它读的数据, 整棵树【真拷贝】到 tmp/iss326/ 再改
            ⇒ 不许在真文件上改、改完再改回来 (★那叫擦产物, 不叫验证★)
★★只写 tmp/iss326/ + logs/iss326/★ ★零写板 · 零落表 · 零改闸 · 零改既有文档正文★

用法: python3 logs/iss326/iss326_sandbox.py
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TMP = os.path.join(ROOT, "tmp", "iss326")
LOGS = os.path.join(ROOT, "logs", "iss326", "sandbox")
BASE = os.path.join(TMP, "base")

# 沙盒要拷的输入面 (★只拷判据脚本读得到的东西★)
COPY_PLAN = [
    ("MECH", "MECH"),                                   # 判据脚本 + 规格/机器块文档
    (os.path.join("HW", "PCB"), os.path.join("HW", "PCB")),   # 板 + 板框口径 + 校准件
    (os.path.join("HW", "netlist_v1.csv"), os.path.join("HW", "netlist_v1.csv")),
    (os.path.join("HW", "netlist_v1_pins.csv"), os.path.join("HW", "netlist_v1_pins.csv")),
    (os.path.join("HW", "BOM_v1.csv"), os.path.join("HW", "BOM_v1.csv")),
    (os.path.join("HW", "SCHEMATIC_LANDING_V1_LANDED.md"), os.path.join("HW", "SCHEMATIC_LANDING_V1_LANDED.md")),
]

RESULTS: list[dict] = []


def log(*a):
    print(*a, flush=True)


def build_base():
    if os.path.isdir(BASE):
        shutil.rmtree(BASE)
    os.makedirs(BASE, exist_ok=True)
    for src_rel, dst_rel in COPY_PLAN:
        src = os.path.join(ROOT, src_rel)
        dst = os.path.join(BASE, dst_rel)
        assert not os.path.islink(src), f"★源是软链, 拒绝拷★ {src_rel}"
        if os.path.isdir(src):
            shutil.copytree(src, dst, symlinks=False)
        else:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
    # ★软链零容忍★
    for dirpath, _dirs, files in os.walk(BASE):
        for fn in files:
            p = os.path.join(dirpath, fn)
            assert not os.path.islink(p), f"★沙盒里出现软链★ {p}"
    return BASE


def fresh_case(name: str) -> str:
    dst = os.path.join(TMP, name)
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    shutil.copytree(BASE, dst, symlinks=False)
    for dirpath, _dirs, files in os.walk(dst):
        for fn in files:
            p = os.path.join(dirpath, fn)
            assert not os.path.islink(p), f"★沙盒里出现软链★ {p}"
    return dst


def read(p: str) -> str:
    with open(p, encoding="utf-8") as f:
        return f.read()


def write(p: str, s: str):
    assert not os.path.islink(p), f"★拒绝写软链★ {p}"
    with open(p, "w", encoding="utf-8") as f:
        f.write(s)


def board_rename(sb: str, old: str, new: str) -> int:
    """★只改板文件里 (property "Reference" "OLD") 的值★"""
    p = os.path.join(sb, "HW", "PCB", "demo_mainboard.kicad_pcb")
    txt = read(p)
    pat = re.compile(r'(\(property\s+"Reference"\s+")' + re.escape(old) + r'(")')
    txt2, n = pat.subn(r"\g<1>" + new + r"\g<2>", txt)
    if n:
        write(p, txt2)
    return n


def board_rename_many(sb: str, mapping: dict) -> int:
    p = os.path.join(sb, "HW", "PCB", "demo_mainboard.kicad_pcb")
    txt = read(p)
    n = 0
    for old, new in mapping.items():
        pat = re.compile(r'(\(property\s+"Reference"\s+")' + re.escape(old) + r'(")')
        txt, k = pat.subn(r"\g<1>" + new + r"\g<2>", txt)
        n += k
    if n:
        write(p, txt)
    return n


def run(cmd, cwd=None, timeout=900):
    t0 = time.time()
    pr = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    return {"cmd": " ".join(cmd), "rc": pr.returncode,
            "stdout": pr.stdout, "stderr": pr.stderr,
            "secs": round(time.time() - t0, 1)}


def record(case_id, title, expect, actual, verdict, proof_path, extra=""):
    RESULTS.append({"case": case_id, "title": title, "expect": expect,
                    "actual": actual, "verdict": verdict, "proof": proof_path, "extra": extra})
    log(f"  · {case_id}: 期望={expect} · 实际={actual} · 判决={verdict}")


# ==================================================================================================
def case1_fakegreen():
    """① 把 R_SEL_D0_N 改成别的名字 ⇒ 那条判据必须变成不匹配 ⇒ 证明它【红不出来】= 假绿"""
    log("[case1] 假绿探针 R_SEL_D0_N")
    uni = json.load(open(os.path.join(ROOT, "logs", "iss326", "mech_ref_universe.json"), encoding="utf-8"))["universe"]
    new = uni["R_SEL_D0_N"]["new"]
    calib_rel = os.path.join("MECH", "BOARD_PORT_OPENING_S6_FRAME_CALIBER.md")

    # --- A: 未改名的基线 ⇒ 判据今天能抓到 (期望: 反向用例 ① 判红)
    sbA = fresh_case("case1A_baseline")
    rA = run([sys.executable, os.path.join(sbA, "MECH", "check_onepass_struct_crosscheck.py"), "--selftest"],
             cwd=sbA)
    okA = "没能真改到目标文件" not in rA["stdout"] and rA["rc"] == 0
    record("1A", "★基线★ 未改名时, 判据脚本的 --selftest 反向用例 ① 应当能抓到 (N2 红)",
           "rc=0 且 反向用例① 判红",
           f"rc={rA['rc']} · ①行: " + next((l.strip() for l in rA["stdout"].splitlines() if "① 把 S6 目标位" in l), "(没找到)"),
           "✔ 符合期望" if okA else "✘ 不符合期望",
           "logs/iss326/sandbox/case1A_baseline.log")

    # --- B: 假绿 —— 模拟「世界改完名了, 判据脚本的字面量没跟着改」
    #     ★做法: 只改【判据脚本副本】里的字面量 ("R_SEL_D0_N" → 新名), 判据读的数据不动★
    #     ★为什么这样做★: 若直接改数据 (机器块) ⇒ N1/N2 立刻红 (数据↔板不一致) ⇒ 那是【响的失败】,
    #       反而看不出「判据分支静悄悄失配」; ★判据失配的机制只取决于「字面量 ≠ 数据里的位号」,
    #       与哪一边是新名无关★ ⇒ 只改字面量是等价的、更干净的实验设计★
    sbB = fresh_case("case1B_literal_stale")
    scr = os.path.join(sbB, "MECH", "check_onepass_struct_crosscheck.py")
    txt = read(scr)
    n = txt.count('"R_SEL_D0_N"')
    write(scr, txt.replace('"R_SEL_D0_N"', '"%s"' % new))
    rB = run([sys.executable, scr, "--selftest"], cwd=sbB)
    line1 = next((l.strip() for l in rB["stdout"].splitlines() if "① 把 S6 目标位" in l), "(没找到)")
    baseline = next((l.strip() for l in rB["stdout"].splitlines() if "[基线]" in l), "(没找到)")
    vacuous = ("N2 红: 否" in line1) or ("没能真改到目标文件" in rB["stdout"])
    still_green = "N1=OK" in baseline and "N2=OK" in baseline
    record("1B", "★假绿★ 判据脚本里的 `== \"R_SEL_D0_N\"` 失配 (世界已改名, 脚本没改) ⇒ 判据分支再也匹配不上",
           "★期望红不出来 (假绿)★ ⇒ ① 反向用例空转 (N2 红: 否) ★且主判据 N1..N6 仍全绿 ⇒ 缺陷对闸隐形",
           f"脚本副本字面量改 {n} 处 · rc={rB['rc']} · 基线行: {baseline} · ①行: {line1}",
           ("✔ 假绿已证实 (判据红不出来, 且主判据仍全绿)" if (vacuous and still_green)
            else ("⚠ 假绿成立但主判据有红" if vacuous else "✘ 判据仍能判红 (非假绿)")),
           "logs/iss326/sandbox/case1B_literal_stale.log",
           extra=f"新名 = {new} · ★主判据仍全绿这一点才是「假绿」的要害: 缺陷存在但闸看不见★")

    # --- C: 对照 —— 字面量与数据同步时, 判据重新能抓到 (⇒ 修复配方 = 字面量必须跟着改)
    sbC = fresh_case("case1C_literal_synced")
    scr = os.path.join(sbC, "MECH", "check_onepass_struct_crosscheck.py")
    rC = run([sys.executable, scr, "--selftest"], cwd=sbC)
    line1c = next((l.strip() for l in rC["stdout"].splitlines() if "① 把 S6 目标位" in l), "(没找到)")
    fixed = "N2 红: 是" in line1c
    record("1C", "★对照/修复配方★ 字面量与数据同步时, 反向用例 ① 必须能抓到 (⇒ 改名时判据脚本必须一起改)",
           "★期望 ① 判红 (N2 红: 是)★",
           f"rc={rC['rc']} · ①行: {line1c}",
           "✔ 修复配方成立 (字面量同步 ⇒ 能抓)" if fixed else "✘ 抓不到 (根因另有其人)",
           "logs/iss326/sandbox/case1C_literal_synced.log")

    # --- D: 反证 —— 只改数据不改板 ⇒ 必须【响地】红 (⇒ 假绿只发生在「数据+板一起改、脚本忘了改」)
    sbD = fresh_case("case1D_data_only")
    p = os.path.join(sbD, "HW", "PCB", "BOARD_FRAME_CALIBER.md")
    txt = read(p)
    n2 = txt.count("R_SEL_D0_N")
    write(p, txt.replace("R_SEL_D0_N", new))
    rD = run([sys.executable, os.path.join(sbD, "MECH", "check_onepass_struct_crosscheck.py"), "--selftest"],
             cwd=sbD)
    baseD = next((l.strip() for l in rD["stdout"].splitlines() if "[基线]" in l), "(没找到)")
    record("1D", "★反证★ 只改【数据】里的位号 (板不改) ⇒ 必须立刻【响地】红",
           "★期望红 (N1/N2 立刻 NG)★",
           f"数据替换 {n2} 处 · rc={rD['rc']} · 基线行: {baseD}",
           "✔ 半改必红 (⇒ 假绿只出现在「数据+板同改、脚本漏改」)" if ("N1=NG" in baseD or "N2=NG" in baseD) else "✘ 半改竟没红 (需重判)",
           "logs/iss326/sandbox/case1D_data_only.log")
    return rA, rB, rC, rD
    return rA, rB, rC


def case2_crash():
    """② 把 D_LED_G 改掉 ⇒ fps[LED_REF] 必须抛异常 ⇒ 贴出异常类型与那一行"""
    log("[case2] 崩探针 D_LED_G")
    uni = json.load(open(os.path.join(ROOT, "logs", "iss326", "mech_ref_universe.json"), encoding="utf-8"))["universe"]
    new = uni["D_LED_G"]["new"]
    sb = fresh_case("case2_led_renamed")
    n = board_rename(sb, "D_LED_G", new)
    r = run([sys.executable, os.path.join(sb, "MECH", "check_board_frame_coords.py"), "--root", sb], cwd=sb)
    rc2 = run([sys.executable, os.path.join(sb, "MECH", "check_board_frame_coords.py"),
               "--root", sb, "--compute"], cwd=sb)
    key = "KeyError" in rc2["stderr"]
    tb = ""
    if key:
        lines = [l.strip() for l in rc2["stderr"].splitlines()
                 if "Error" in l or "fps[" in l or "LED_REF" in l or "led_space" in l]
        tb = " ⏎ ".join(lines[-4:])
    record("2", "★崩★ 板上 D_LED_G 改名成 " + new + " ⇒ `fps[LED_REF]` 必须抛异常",
           "★期望红 (抛异常)★ ⇒ KeyError: 'D_LED_G'",
           f"板内改名 {n} 处 · 默认模式 rc={r['rc']} (只红在 md5 闸) · --compute 模式 rc={rc2['rc']} · " + (tb or "(stderr 无 KeyError)"),
           "✔ 已崩 (异常类型 + 那一行如上)" if key else "✘ 没崩 (异常未出现)",
           "logs/iss326/sandbox/case2_led_renamed.log",
           extra="★注★ 默认模式 (run_checks) 不走 LED 空间复算 ⇒ 只红在 C4 md5; ★`--compute` 才进 `led_space()` ⇒ 崩在那里★")
    return r, rc2


def case3_keep():
    """③ 改一个【不该改的】 ref (J_SOM_P1 · 在【不动的 32 个】里) ⇒ 闸必须不受影响 ⇒ 证明没误伤"""
    log("[case3] 不动集探针 J_SOM_P1")
    uni = json.load(open(os.path.join(ROOT, "logs", "iss326", "mech_ref_universe.json"), encoding="utf-8"))["universe"]
    move_map = {k: v["new"] for k, v in uni.items() if v.get("move") == "改名"}
    keep = [k for k, v in uni.items() if v.get("move") != "改名"]

    # --- A: 按改名计划只改 186 个改名位号, 32 个不动位号一律不动 ⇒ J_SOM_P1 必须不受影响
    sbA = fresh_case("case3A_plan_only")
    n = board_rename_many(sbA, move_map)
    rA = run([sys.executable, os.path.join(sbA, "MECH", "check_board_frame_coords.py"), "--root", sbA], cwd=sbA)
    som_ok = "J_SOM" not in rA["stderr"]
    recA = "J_SOM_P1" in read(os.path.join(sbA, "HW", "PCB", "demo_mainboard.kicad_pcb"))
    record("3A", "★只改 186 个改名位号 (32 个不动位号一律不动) ⇒ J_SOM_P1 必须完全不受影响",
           "★期望绿 (不动集没被误伤)★ ⇒ 板上 J_SOM_P1 原样在, 且没有 J_SOM 相关异常",
           f"板上改名 {n} 处 · 板上 J_SOM_P1 仍在 = {recA} · 无 J_SOM 异常 = {som_ok} · rc={rA['rc']}",
           "✔ 不动集没被误伤" if (recA and som_ok) else "✘ 误伤了不动集",
           "logs/iss326/sandbox/case3A_plan_only.log")

    # --- B: 反证 —— 连 J_SOM_P1 也一起改 ⇒ 判据必须失配 (证明「它确实在不动集里, 不该动」)
    sbB = fresh_case("case3B_keep_broken")
    m2 = dict(move_map)
    m2["J_SOM_P1"] = uni["J_SOM_P1"]["new"] + "_X"   # 故意改成别的名字
    board_rename_many(sbB, m2)
    rB = run([sys.executable, os.path.join(sbB, "MECH", "check_board_frame_coords.py"), "--root", sbB], cwd=sbB)
    somB = "J_SOM_P1" in rB["stdout"]
    c3_red = "C3 负向断言失效" in rB["stdout"] or "--- C3 --- ❌" in rB["stdout"]
    diff_lines = [l for l in rB["stdout"].splitlines() if "J_SOM" in l or "C3" in l][:3]
    record("3B", "★反证★ 连不动集里的 J_SOM_P1 也改掉 ⇒ 判据必须失配 (证明它确实不该改)",
           "★期望红 / 判据失配★ ⇒ SoM 焊盘总数 400 → 300, J_SOM_P1 从判据里消失, C3 负向断言判红",
           f"rc={rB['rc']} (基线 rc={rA['rc']}) · 输出里还有 J_SOM_P1 = {somB} · C3 判红 = {c3_red} · " + " ⏎ ".join(diff_lines),
           "✔ 证实 J_SOM_P1 在不动集里 (改了 ⇒ 判据失配)" if (c3_red or not somB) else "✘ 改坏了它也不影响判据 (需重判)",
           "logs/iss326/sandbox/case3B_keep_broken.log")
    return rA, rB


def case4_comment():
    """④ 注释里的 ref 名改成别的 ⇒ 闸必须不受影响 ⇒ 证明「注释里的 ref 不需要改」"""
    log("[case4] 注释里的 ref 探针")
    sbA = fresh_case("case4A_baseline")
    rA = run([sys.executable, os.path.join(sbA, "MECH", "check_board_frame_coords.py"), "--root", sbA], cwd=sbA)
    # 找一条【只在注释/文档串里出现】的 ref (ISS-320 同型: service_port_check.py L51 型号名在注释里)
    src_rel = os.path.join("MECH", "check_board_frame_coords.py")
    p = os.path.join(sbA, src_rel)
    txt = read(p)
    # L9 文档串里的 J_SOM_P1..P4 —— 改成别的名字
    old_line = None
    for i, ln in enumerate(txt.splitlines(), 1):
        if "J_SOM_P1" in ln and ln.strip().startswith(("#", '"""', "'''")) or (
                "J_SOM_P1" in ln and ln.lstrip().startswith("#")):
            old_line = (i, ln)
            break
    if old_line is None:
        # 退而求其次: 文档串行
        for i, ln in enumerate(txt.splitlines(), 1):
            if "J_SOM_P1" in ln:
                old_line = (i, ln)
                break
    ln_no, ln_txt = old_line
    new_txt = txt.replace(ln_txt, ln_txt.replace("J_SOM_P1", "ZZ_COMMENT_PROBE_1"))
    write(p, new_txt)
    rB = run([sys.executable, p, "--root", sbA], cwd=sbA)
    same = (rA["rc"] == rB["rc"]) and (rA["stdout"] == rB["stdout"])
    record("4", "★注释里的 ref★ 把判据脚本【注释/文档串】里的位号名改成别的 ⇒ 闸必须不受影响",
           "★期望绿且输出与基线逐字节相同★",
           f"改的是 L{ln_no}: {ln_txt.strip()[:70]} · rc {rA['rc']} → {rB['rc']} · stdout 完全相同 = {rA['stdout'] == rB['stdout']}",
           "✔ 注释里的 ref 无功能影响" if same else "✘ 注释里的 ref 竟然有影响 (需重判)",
           "logs/iss326/sandbox/case4_comment.log")
    return rA, rB


def main() -> int:
    os.makedirs(TMP, exist_ok=True)
    os.makedirs(LOGS, exist_ok=True)
    log("[sandbox] 建 base 拷贝 (真拷贝, 软链零容忍) ...")
    build_base()
    rA1, rB1, rC1, rD1 = case1_fakegreen()
    r2, r2c = case2_crash()
    r3a, r3b = case3_keep()
    r4a, r4b = case4_comment()

    # ---- 落原始日志
    for name, r in (("case1A_baseline", rA1), ("case1B_literal_stale", rB1),
                    ("case1C_literal_synced", rC1), ("case1D_data_only", rD1),
                    ("case2_led_renamed", r2), ("case3A_plan_only", r3a),
                    ("case3B_keep_broken", r3b), ("case4_comment", r4a)):
        with open(os.path.join(LOGS, name + ".log"), "w", encoding="utf-8") as f:
            f.write(f"$ {r['cmd']}\nrc={r['rc']}  ({r['secs']}s)\n----- stdout -----\n{r['stdout']}")
            f.write(f"\n----- stderr -----\n{r['stderr']}\n")
    with open(os.path.join(LOGS, "case2_led_renamed_compute.log"), "w", encoding="utf-8") as f:
        f.write(f"$ {r2c['cmd']}\nrc={r2c['rc']}  ({r2c['secs']}s)\n----- stdout -----\n{r2c['stdout']}")
        f.write(f"\n----- stderr -----\n{r2c['stderr']}\n")
    with open(os.path.join(LOGS, "case4_comment_after_edit.log"), "w", encoding="utf-8") as f:
        f.write(f"$ {r4b['cmd']}\nrc={r4b['rc']}  ({r4b['secs']}s)\n----- stdout -----\n{r4b['stdout']}")
        f.write(f"\n----- stderr -----\n{r4b['stderr']}\n")

    # ---- RESULTS.md
    with open(os.path.join(LOGS, "RESULTS.md"), "w", encoding="utf-8") as f:
        f.write("# ISS-326 · MECH 侧「崩 / 假绿」沙盒实证 · 结果表\n\n")
        f.write(f"> ★**实跑机**: `yuewuya-RedmiBook-14` · Linux 7.0.0-42-generic · Python 3 · 2026-11-18\n")
        f.write("> ★**铁律**: 判据脚本 + 它读的数据, 整棵树【真拷贝】到 `tmp/iss326/` 再改 ⇒ 真件一个字节不碰\n")
        f.write("> ★**软链**: 拷贝时 `symlinks=False` + 每文件 `assert not os.path.islink` ⇒ 沙盒内软链数 = 0\n\n")
        f.write("| 用例 | 内容 | 期望 | 实际 | 判决 |\n|---|---|---|---|---|\n")
        for r in RESULTS:
            f.write(f"| **{r['case']}** | {r['title']} | {r['expect']} | {r['actual']} | **{r['verdict']}** |\n")
        f.write("\n## 逐条原始读数\n")
        for r in RESULTS:
            f.write(f"\n### {r['case']} · {r['title']}\n\n")
            f.write(f"- **期望**: {r['expect']}\n- **实际**: {r['actual']}\n- **判决**: {r['verdict']}\n")
            if r["extra"]:
                f.write(f"- **备注**: {r['extra']}\n")
            f.write(f"- **原始日志**: `{r['proof']}`\n")
    with open(os.path.join(LOGS, "results.json"), "w", encoding="utf-8") as f:
        json.dump(RESULTS, f, ensure_ascii=False, indent=2)
    log(f"[sandbox] 结果落 {LOGS}/RESULTS.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
