#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""iss303 · 沙盒反向用例 (★每条: 原样 rc + 期望红组 vs 实际红组★)

★零写板 · 零落表: 全部构造都在临时沙盒目录里做, 真盘 5 件 md5 一个字节不许动 ★
★跑法: python3 logs/iss303/sandbox_reverse_cases.py
"""
import contextlib
import hashlib
import importlib.util
import io
import os
import shutil
import sys
import tempfile

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
GATE_REL = os.path.join("MECH", "check_onepass_struct_crosscheck.py")
LEDGER_REL = os.path.join("HW", "SCHEMATIC_LANDING_V1_LANDED.md")
NET_REL = os.path.join("HW", "netlist_v1.csv")
PINS_REL = os.path.join("HW", "netlist_v1_pins.csv")
PROTECTED5 = [
    os.path.join("HW", "PCB", "demo_mainboard.kicad_pcb"),
    os.path.join("HW", "PCB", "demo_mainboard.kicad_pro"),
    NET_REL, PINS_REL, os.path.join("HW", "BOM_v1.csv"),
]


def load_gate():
    spec = importlib.util.spec_from_file_location("gate_iss303", os.path.join(PROJ, GATE_REL))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


GATE = load_gate()


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def disk_md5s():
    return {rel: md5(os.path.join(PROJ, rel)) for rel in PROTECTED5}


def make_sandbox(tag):
    """★沙盒 = 最小镜像 (只拷 N6 判决要用的件 + 规格页)★"""
    dst = os.path.join(tempfile.gettempdir(), "iss303_sbx", tag)
    if os.path.exists(dst):
        shutil.rmtree(dst)
    os.makedirs(dst, exist_ok=True)
    rels = [GATE.SPEC_REL, GATE.SPEC2_REL, GATE.CALIB_REL, GATE.PCB_REL, LEDGER_REL] + PROTECTED5
    for rel in rels:
        src = os.path.join(PROJ, rel)
        if os.path.exists(src):
            d = os.path.join(dst, rel)
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copy2(src, d)
    return dst


def run_gate_on(sb):
    """★把闸的 PROJ 指到沙盒 ⇒ 跑真 main() ⇒ 拿原样 rc + 原样输出★"""
    old = GATE.PROJ
    GATE.PROJ = sb
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            rc = GATE.main()
    finally:
        GATE.PROJ = old
    res = GATE.run_checks(sb)
    return rc, buf.getvalue(), res


def drop_ledger_rows(sb, rel, md5_sub):
    p = os.path.join(sb, LEDGER_REL)
    text = open(p, encoding="utf-8").read()
    base = os.path.basename(rel)
    keep, dropped = [], 0
    for ln in text.splitlines():
        s = ln.strip()
        if s.startswith("|") and (rel in s or base in s) and md5_sub in s:
            dropped += 1
            continue
        keep.append(ln)
    open(p, "w", encoding="utf-8").write("\n".join(keep) + "\n")
    return dropped


def append_ledger_row(sb, rel, prev12, new12, iss="ISS-999"):
    p = os.path.join(sb, LEDGER_REL)
    with open(p, "a", encoding="utf-8") as fh:
        fh.write(f"\n| ★**{iss}** ★ | ★**`{rel}`** ★ | `{prev12}` | `{new12}` | ★**是**★ |\n")


def show(tag, expect_red, expect_hit, rc, out, res, note=""):
    errs = res["N6"]["errs"]
    actual_red = not res["N6"]["ok"]
    hit = any(expect_hit in e for e in errs) if expect_hit else True
    print("=" * 96)
    print(f"★{tag}")
    print(f"  期望红组 = {'N6 红' if expect_red else 'N6 绿'}  ·  期望命中 = {expect_hit or '—'}")
    print(f"  实际红组 = {'N6 红' if actual_red else 'N6 绿'}  (rc={rc})  ·  实际命中 = {'是' if hit else '否'}")
    print(f"  N6 错误 {len(errs)} 条:")
    for e in errs:
        print(f"    ✗ {e}")
    if note:
        print(f"  注: {note}")
    ok = (actual_red == expect_red) and hit
    print(f"  ★判定 = {'PASS' if ok else 'FAIL'}")
    return ok


def main():
    before = disk_md5s()
    results = []

    # ① 网表 md5 改成台账里查不到的假值 ⇒ N6 红
    sb = make_sandbox("c1_fake_netlist_md5")
    p = os.path.join(sb, NET_REL)
    b, a = md5(p), None
    with open(p, "a", encoding="utf-8") as fh:
        fh.write("\n★iss303 沙盒反向用例: 往网表里塞一行 ⇒ md5 变成台账查不到的值★\n")
    a = md5(p)
    rc, out, res = run_gate_on(sb)
    results.append(show("① 网表 md5 改成一个台账里查不到的假值 ⇒ N6 红", True, "∉ 合法集合", rc, out, res,
                        f"沙盒里网表 md5 {b[:8]} ⇒ {a[:8]} (真盘没动)"))
    print("  ---- 闸原样输出 (N6 段) ----")
    for ln in out.splitlines():
        if "N6" in ln or "受保护件" in ln or "合法集合" in ln or "【红】" in ln:
            print("  " + ln)

    # ② 脚表 md5 改成台账里查不到的假值 ⇒ N6 红
    sb = make_sandbox("c2_fake_pins_md5")
    p = os.path.join(sb, PINS_REL)
    b = md5(p)
    with open(p, "a", encoding="utf-8") as fh:
        fh.write("\n★iss303 沙盒反向用例: 往脚表里塞一行 ⇒ md5 变成台账查不到的值★\n")
    a = md5(p)
    rc, out, res = run_gate_on(sb)
    results.append(show("② 脚表 md5 改成一个台账里查不到的假值 ⇒ N6 红", True, "∉ 合法集合", rc, out, res,
                        f"沙盒里脚表 md5 {b[:8]} ⇒ {a[:8]} (真盘没动)"))
    print("  ---- 闸原样输出 (N6 段) ----")
    for ln in out.splitlines():
        if "N6" in ln or "受保护件" in ln or "合法集合" in ln or "【红】" in ln:
            print("  " + ln)

    # ③ 台账里把 ISS-302 那一行删掉 (链断) ⇒ 现值不在合法集合 ⇒ N6 红
    sb = make_sandbox("c3_ledger_drop_iss302")
    dropped = drop_ledger_rows(sb, NET_REL, "6aee500e")
    rc, out, res = run_gate_on(sb)
    results.append(show("③ 台账里把 ISS-302 那一行删掉 (链断) ⇒ 现值变回「不在合法集合」⇒ N6 红", True,
                        "∉ 合法集合", rc, out, res, f"沙盒台账删掉 {dropped} 行 (§19 行 + ISS302_ROWS 行)"))
    print("  ---- 闸原样输出 (N6 段) ----")
    for ln in out.splitlines():
        if "N6" in ln or "受保护件" in ln or "合法集合" in ln or "【红】" in ln:
            print("  " + ln)

    # ④ 台账里出现两条指向同一文件的链头 (链头不唯一) ⇒ N6 红
    sb = make_sandbox("c4_ledger_two_heads")
    append_ledger_row(sb, NET_REL, "aaaa11112222", "bbbb33334444")
    rc, out, res = run_gate_on(sb)
    results.append(show("④ 台账里出现两条指向同一文件的链头 (链头不唯一) ⇒ N6 红", True, "链头", rc, out, res,
                        "沙盒台账末尾追加一行伪造登记 (prev=aaaa11112222 → new=bbbb33334444)"))
    print("  ---- 闸原样输出 (N6 段) ----")
    for ln in out.splitlines():
        if "N6" in ln or "受保护件" in ln or "合法集合" in ln or "【红】" in ln:
            print("  " + ln)

    # ⑤ 台账里伪造一个 md5 但盘上不符 ⇒ 仍红
    sb = make_sandbox("c5_ledger_forged_md5")
    drop_ledger_rows(sb, NET_REL, "6aee500e")
    append_ledger_row(sb, NET_REL, "37f62ac3f0b8", "dddd55556666")
    rc, out, res = run_gate_on(sb)
    results.append(show("⑤ 台账里伪造一个 md5 但盘上不符 ⇒ 仍红", True, "∉ 合法集合", rc, out, res,
                        "沙盒台账: 删掉 ISS-302 行 + 伪造链头 dddd55556666 ⇒ 链仍合法, 但盘上值不符"))
    print("  ---- 闸原样输出 (N6 段) ----")
    for ln in out.splitlines():
        if "N6" in ln or "受保护件" in ln or "合法集合" in ln or "【红】" in ln:
            print("  " + ln)

    # ⑥ 台账文件缺失 ⇒ N6 红 (fail-closed)
    sb = make_sandbox("c6_ledger_missing")
    os.remove(os.path.join(sb, LEDGER_REL))
    rc, out, res = run_gate_on(sb)
    results.append(show("⑥ 台账文件缺失 ⇒ N6 红 (fail-closed: 判决源读不到)", True, "落表台账读不到", rc, out, res,
                        "沙盒里删掉落表台账副本"))
    print("  ---- 闸原样输出 (N6 段) ----")
    for ln in out.splitlines():
        if "N6" in ln or "受保护件" in ln or "合法集合" in ln or "【红】" in ln:
            print("  " + ln)

    # ⑦ 改板文件 (ISS-296 那条不许被放松) ⇒ N6 红
    sb = make_sandbox("c7_touch_board")
    p = os.path.join(sb, os.path.join("HW", "PCB", "demo_mainboard.kicad_pcb"))
    b = md5(p)
    with open(p, "a", encoding="utf-8") as fh:
        fh.write("\n; ★iss303 沙盒反向用例: 篡改受保护板文件★\n")
    a = md5(p)
    rc, out, res = run_gate_on(sb)
    results.append(show("⑦ 沙盒里改板文件 ⇒ N6 仍红 (ISS-296 那条不许被放松)", True, "受保护件被改", rc, out, res,
                        f"沙盒里板 md5 {b[:8]} ⇒ {a[:8]} (真盘没动)"))
    print("  ---- 闸原样输出 (N6 段) ----")
    for ln in out.splitlines():
        if "N6" in ln or "受保护件" in ln or "合法集合" in ln or "【红】" in ln:
            print("  " + ln)

    # ⑧ 正向对照: 一切如常 (现值 == 台账链头) ⇒ N6 绿
    sb = make_sandbox("c8_positive")
    rc, out, res = run_gate_on(sb)
    results.append(show("⑧ 正向对照: 一切如常 (现值 == 台账链头) ⇒ N6 绿", False, None, rc, out, res,
                        "证明闸不是恒红"))
    print("  ---- 闸原样输出 (N6 段) ----")
    for ln in out.splitlines():
        if "N6" in ln or "受保护件" in ln or "合法集合" in ln or "【绿】" in ln:
            print("  " + ln)

    after = disk_md5s()
    print("=" * 96)
    print("★真盘 5 件 md5 (跑前 ⇒ 跑后):")
    same = True
    for rel in PROTECTED5:
        eq = before[rel] == after[rel]
        same = same and eq
        print(f"  {'✔' if eq else '✘'} {rel:38s} {before[rel]} ⇒ {after[rel]}")
    print(f"  ⇒ 真盘 5 件 md5 一个字节未动 = {'是' if same else '否'}")
    npass = sum(1 for r in results if r)
    print(f"★沙盒反向用例 {npass}/{len(results)} 条 PASS")
    return 0 if (npass == len(results) and same) else 1


if __name__ == "__main__":
    sys.exit(main())
