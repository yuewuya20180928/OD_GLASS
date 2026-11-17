#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-285 · sw-lead · ★沙盒反向用例自测器★ (★情形一 ⇒ 真盘一个字节不许动★)

=====================================================================
跑法 (★全部在沙盒里跑★):

    # 0) 先备好一个「已套补丁」的干净沙盒 (★补丁套用器的 --apply 只在沙盒里跑★)
    python3 SW/patches/ISS-285_sw_judgment_alignment/sbx_iss285_reverse_cases.py \
            --make-base /tmp/iss285_sbx_base

    # 1) 跑 5 条 (正向 + 4 条反向)
    python3 SW/patches/ISS-285_sw_judgment_alignment/sbx_iss285_reverse_cases.py \
            --base /tmp/iss285_sbx_base

退出码: 0 = 5 条全符合「期望红组 vs 实际红组」 · 1 = 有条不符

★设计要点★:
  · 每条用例都从【基线沙盒】整份重铺 ⇒ 互不污染
  · 反向用例只改沙盒里的 [网表 / 落表台账] ⇒ 真盘 (网表/脚表/BOM/板/.kicad_pro) 零字节改动
  · 用例 ④ 改完网表后 ★顺手在沙盒落表台账里补一行合法落表记录 (四项同行)★
    ⇒ 链头自动前移 ⇒ 网表锚点两条判据保持绿 ⇒ 【只有 F4' 变红】⇒ 证明是 F4' 自己在看网表
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))      # projects/smart_glasses
APPLIER = os.path.join(HERE, "apply_iss285_sw_judgment_alignment.py")

NETLIST_REL = os.path.join("HW", "netlist_v1.csv")
LEDGER_REL = os.path.join("HW", "SCHEMATIC_LANDING_V1_LANDED.md")
TIMING_REL = os.path.join("SW", "tools", "timing_check.py")
DPS_REL = os.path.join("SW", "tools", "check_demo_panel_spec.py")

# ★三条判据的短键 ⇄ 全文 (★判决源在 timing_check.py 的 NEW_TESTS 里★)
K_ALLOWED = "网表锚点: 现行网表 md5 ∈ 落表台账登记的状态 (落表前 / 落表后)"
K_THREEWAY = "网表锚点: 锚点 ↔ 落表台账 ↔ 盘上真源 三方对账成立 (不许悄悄换真源)"
K_F4 = "F4' 实读: ADC 装机链是 VBUS_DET_D; BAT_DET 三颗必装 (V-3=E 落表后)"
K_REV11 = ("REV-11 反向: 把 BAT_DET 三颗 (R_BAT_DET_1 / R_BAT_DET_2 / C_DET_BAT) 改回 DNP ⇒ "
           "F4'『BAT_DET 三颗必装』必须变红")


def md5_of(path: str) -> str:
    return hashlib.md5(open(path, "rb").read()).hexdigest()


def load_timing(sbx: str):
    p = os.path.join(sbx, TIMING_REL)
    spec = importlib.util.spec_from_file_location("_iss285_timing", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run(cmd, cwd):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=300)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def red_group(out: str):
    """从 timing_check 输出里抽出【红组】(= [FAIL] 的判据名)。"""
    return [ln.split("] ", 1)[1].strip() for ln in out.splitlines() if "  [FAIL] " in ln]


def green_group(out: str):
    return [ln.split("] ", 1)[1].strip() for ln in out.splitlines() if "  [PASS] " in ln]


# ===================================================================== 构造器
def mut_case1_fake_md5(sbx: str) -> str:
    """① 盘上网表 md5 落在台账登记的任何状态之外 (伪造 md5)。

    ★手法: 原地改【最后一行】的 `conn_id` 一个字段 (★conn_id 这列没有任何闸读★
      ⇒ 行数不变 (仍是 513 数据行) · 结构不变 ⇒ 【只有 md5 变了】
      ⇒ 盘上 md5 ∉ 台账登记的任何状态 ⇒ 两条网表锚点判据必须红★)
    """
    mod = load_timing(sbx)
    p = os.path.join(sbx, NETLIST_REL)
    with open(p, "r", encoding="utf-8-sig", newline="") as fh:
        lines = fh.read().split("\n")
    idx = len(lines) - 1
    while idx > 0 and not lines[idx].strip():
        idx -= 1
    body, term = (lines[idx].rstrip("\r"), "\r") if lines[idx].endswith("\r") else (lines[idx], "")
    fields, quoted = mod._split_csv_line(body)
    before = fields[11]
    fields[11] = "C-99"
    lines[idx] = mod._join_csv_line(fields, quoted) + term
    open(p, "w", encoding="utf-8-sig", newline="").write("\n".join(lines))
    return ("最后一行 L%d 的 conn_id: %s → C-99 (★行数不变 · 结构不变 · 只有 md5 变★); "
            "盘上网表 md5 = %s (台账链头 = 2f17650cfbef …)" % (idx + 1, before, md5_of(p)))


def mut_case2_ledger_row_incomplete(sbx: str) -> str:
    """② 落表台账那一行四项不齐 (缺『改后 md5』⇒ 该行不算落表记录 ⇒ 链头不前移)。"""
    p = os.path.join(sbx, LEDGER_REL)
    text = open(p, encoding="utf-8").read()
    head_md5 = "2f17650cfbef48d5efd71821505c3343"
    lines = text.split("\n")
    hit = 0
    for i, ln in enumerate(lines):
        if "HW/netlist_v1.csv" in ln and head_md5 in ln:
            lines[i] = ln.replace(head_md5, "★缺改后md5★")
            hit += 1
    open(p, "w", encoding="utf-8").write("\n".join(lines))
    return "台账里 %s 的落表行被改成『缺改后 md5』(四项不齐) ⇒ 命中 %d 行" % (NETLIST_REL, hit)


def mut_case3_head_not_unique(sbx: str) -> str:
    """③ 链头不唯一 (台账里两条指向同一文件 ⇒ 两条都像链头 ⇒ 取不准 ⇒ 判红)。

    ★手法: 追加一条落表行, 它的【改前 md5 = 同一个 e06c1dd6…】而【改后 md5 = 另一个】
      ⇒ 台账里从同一前驱分出两条分支 ⇒ 链头 = {2f17650c…, deadbeef…} 两个 ⇒ 不唯一 ★
      (★追加 prev=2f17650c 那种是【把链拉长】不是【分叉】⇒ 链头仍唯一 ⇒ 那不算本用例★)
    """
    p = os.path.join(sbx, LEDGER_REL)
    fake = "deadbeefdeadbeefdeadbeefdeadbeef"
    row = ("| ★**ISS-285** ★ | ★**`HW/netlist_v1.csv`** ★ | "
           "★**`e06c1dd633566aa44732762c2ff99d1c`** ★ | ★**`%s`** ★ | ★**是**★ |" % fake)
    with open(p, "a", encoding="utf-8") as f:
        f.write("\n" + row + "\n")
    return ("台账尾部追加第二条指向 HW/netlist_v1.csv 的落表行 (★改前同一个 e06c1dd6…, "
            "改后 = %s…★ ⇒ 链头分叉 = 两个 ⇒ 取不准 ⇒ fail-closed 判红)" % fake[:12])


def mut_case4_bat_det_back_to_dnp(sbx: str) -> str:
    """④ 把 BAT_DET 三颗改回 DNP (期望值被改坏) ⇒ 只有 F4' 变红。

    ★改完网表后顺手在沙盒落表台账补一行【合法落表记录 (四项同行)】★
      ⇒ 链头自动前移到新 md5 ⇒ 网表锚点两条判据保持绿
      ⇒ 【红组里只剩 F4'】⇒ 证明 F4' 真的在读网表, 不是被别的红盖住了
    """
    mod = load_timing(sbx)
    nl = mod.Netlist(os.path.join(sbx, NETLIST_REL))
    want = {("BAT", "R_BAT_DET_1"), ("BAT_DET", "R_BAT_DET_2"),
            ("BAT_DET", "C_DET_BAT"), ("GND", "C_DET_BAT")}
    line_nos = [x["_line_no"] for x in nl.rows
                if ((x.get("net") or ""), (x.get("ref") or "")) in want]
    tmp = tempfile.mkdtemp(prefix="iss285_case4_")
    try:
        dst = os.path.join(tmp, "netlist_v1.csv")
        mod.set_dnp_at_lines_copy(nl, dst, line_nos, "DNP")
        shutil.copy2(dst, os.path.join(sbx, NETLIST_REL))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    new_md5 = md5_of(os.path.join(sbx, NETLIST_REL))
    lp = os.path.join(sbx, LEDGER_REL)
    row = ("| ★**ISS-285** ★ | ★**`HW/netlist_v1.csv`** ★ | "
           "★**`2f17650cfbef48d5efd71821505c3343`** ★ | ★**`%s`** ★ | ★**是**★ |" % new_md5)
    with open(lp, "a", encoding="utf-8") as f:
        f.write("\n" + row + "\n")
    return ("BAT_DET 三颗的器件本体行 L%s 改回 DNP ⇒ 盘上 md5 = %s ; "
            "台账补一行合法落表记录 (链头前移) ⇒ 锚点两条判据保持绿" % (sorted(line_nos), new_md5))


def mut_none(sbx: str) -> str:
    """⑤ 正向对照: 一切如常。"""
    return "什么都不改 (正向对照 ⇒ 证明闸不是恒红)"


CASES = [
    # ★说明: 补丁里【链头取不准 (不唯一 / 链断 / 有记录不在链上 / 链头没单号)】
    #   ⇒ 「允许状态集合」降级为空集 ⇒ 连「盘上 md5 ∈ 台账登记的状态」这一条也判红
    #   ⇒ fail-closed 贯穿两条网表锚点判据 (★比 R6 更保守: R6 只有一条★)★
    ("①", "盘上网表 md5 落在台账登记的任何状态之外 (伪造 md5)",
     mut_case1_fake_md5, {K_ALLOWED, K_THREEWAY}),
    ("②", "落表台账那一行四项不齐 (单号 / 文件名 / 前后 md5)",
     mut_case2_ledger_row_incomplete, {K_ALLOWED, K_THREEWAY}),
    ("③", "链头不唯一 (台账里两条指向同一文件) ⇒ fail-closed 不许动",
     mut_case3_head_not_unique, {K_ALLOWED, K_THREEWAY}),
    ("④", "把 BAT_DET 三颗改回 DNP (期望值被改坏)",
     mut_case4_bat_det_back_to_dnp, {K_F4, K_REV11}),
    ("⑤", "正向对照: 一切如常 (证明闸不是恒红)",
     mut_none, set()),
]


# ★沙盒最小镜像 (★只拷这两个门禁真正读到的文件 ⇒ 沙盒 5.6 MB, 不占盘★)
MIN_FILES = [
    "HW/netlist_v1.csv",
    "HW/netlist_v1_pins.csv",
    "HW/BOM_v1.csv",
    "HW/SCHEMATIC_LANDING_V1_LANDED.md",
    "HW/PCB/demo_mainboard.kicad_pcb",
    "HW/PCB/demo_mainboard.kicad_pro",
    "SW/tools/timing_check.py",
    "SW/tools/check_demo_panel_spec.py",
    "SW/SW_MD5_BASELINE_LEDGER.md",
    "SW/DEMO_PANEL_WAVESHARE_2P8_SPEC.md",
    "SW/DEMO_PANEL_SPEC_TRIAGE.md",
    "SW/DEMO_OD_PIPELINE_SPEC.md",
]


def copy_min(src: str, dst: str) -> None:
    """把 MIN_FILES 拷到 dst (★目录结构原样★)。"""
    os.makedirs(os.path.join(dst, "state"), exist_ok=True)
    for rel in MIN_FILES:
        s = os.path.join(src, rel)
        d = os.path.join(dst, rel)
        os.makedirs(os.path.dirname(d), exist_ok=True)
        shutil.copy2(s, d)


def make_base(base: str) -> int:
    """造一个【已套补丁】的干净基线沙盒。"""
    if os.path.isdir(base):
        shutil.rmtree(base)
    os.makedirs(base)
    copy_min(PROJ, base)
    rc, out = run([sys.executable, APPLIER, "--root", base, "--apply"], cwd=base)
    print(out)
    if rc != 0:
        return rc
    rc, out = run([sys.executable, os.path.join(base, TIMING_REL)], cwd=base)
    print(out.splitlines()[-1] if out else "")
    return 0 if rc == 0 else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=os.path.join(PROJ, "logs", "iss285", "sbx_base"))
    ap.add_argument("--work", default=os.path.join(PROJ, "logs", "iss285", "sbx_work"))
    ap.add_argument("--make-base", action="store_true")
    args = ap.parse_args()

    if args.make_base:
        return make_base(args.base)

    if not os.path.isdir(args.base):
        print("★基线沙盒不存在: %s (先跑 --make-base)" % args.base)
        return 1

    allok = True
    for tag, desc, mut, expect in CASES:
        if os.path.isdir(args.work):
            shutil.rmtree(args.work)
        os.makedirs(args.work)
        copy_min(args.base, args.work)
        note = mut(args.work)
        rc, out = run([sys.executable, os.path.join(args.work, TIMING_REL)], cwd=args.work)
        got = set(red_group(out))
        rc2, out2 = run([sys.executable, os.path.join(args.work, DPS_REL)], cwd=args.work)
        print("=" * 78)
        print("【%s】%s" % (tag, desc))
        print("  构造: %s" % note)
        print("  ---- timing_check.py (沙盒) ---- rc=%d" % rc)
        for ln in out.splitlines():
            if "  [FAIL] " in ln or "SELFTEST" in ln:
                print("  " + ln)
        print("  ---- check_demo_panel_spec.py (沙盒) ---- rc=%d" % rc2)
        for ln in out2.splitlines():
            if ln.startswith("❌") or ln.startswith("   - "):
                print("  " + ln)
        print("  ★期望红组 (%d 条): %s" % (len(expect), sorted(expect) or "(空 ⇒ 期望全绿)"))
        print("  ★实际红组 (%d 条): %s" % (len(got), sorted(got) or "(空 ⇒ 实际全绿)"))
        ok = (got == expect)
        print("  ★判定: %s" % ("✅ 一致" if ok else "❌ 不一致 (期望 %s / 实际 %s)"
                               % (sorted(expect), sorted(got))))
        allok = allok and ok

    print("=" * 78)
    print("★5 条用例总判定: %s" % ("✅ 全符合" if allok else "❌ 有条不符"))
    return 0 if allok else 1


if __name__ == "__main__":
    sys.exit(main())
