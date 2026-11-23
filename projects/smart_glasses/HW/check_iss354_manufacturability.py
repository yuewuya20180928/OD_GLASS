#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-354 · demo 主板可制造性收口 · 本单自带闸 (只读判定)
======================================================================
★**只读**: 本脚本【不写板 · 不落表 · 不改任何既有文件】 ⇒ 只读文件 + 算 md5 + 判定。
★**用途**: 保证下面 5 件东西【在盘】, 防止交卷后被误删 / 被改坏:

  A-1  5 个 ref (Q1/Q2/U_BATPROT/U_LDO_S28/U_SUPV) 的【改项清单】在盘
       (★逐个点名 · 不许只报数★)
  A-2  4 类不自洽 (类-1 脚数脚号 / 类-2 land 几何 / 类-3 缺关键焊盘 / 类-4 BOM 栏) 在盘
  A-3  SoM pin1 排向的【降级方案 (a)(b)(c)】在盘
  A-4  【下料前一票否决项 V-01..V-15】在盘
  A-5  板指纹零写板 (md5) + PREFLIGHT 零手改 (md5)

★**为什么 PREFLIGHT 只查 md5 不改内容**: PREFLIGHT 是生成器产物 (state/_iss277_build_preflight.py)
   且有逐字比对闸 ⇒ ★**手改它 ⇒ 闸当场红 ⇒ 那个红会被误读成「板改坏了」** ⇒ 本单零手改。

用法:
  python3 HW/check_iss354_manufacturability.py                 # 只读判定 (rc 0 = 全过)
  python3 HW/check_iss354_manufacturability.py --selftest       # ★反向用例★ (末行 ALL TESTS PASS)
  python3 HW/check_iss354_manufacturability.py --root DIR        # 指定根 (自测用)

★**沙盒纪律**: 临时副本一律落项目盘 $PWD/tmp/ (★不许写 /tmp★)
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(HERE)

# ★常量: 本单钉死的期望值 (★改了这里 = 改了判据方向 ⇒ 需 main 拍板★)★
EXPECT_PCB_MD5 = "611b869e13518c3c023fb178f91a0075"
EXPECT_PCB_MTIME = "2026-11-06 07:07:17.362193413"
# ★PREFLIGHT 是生成器产物 ⇒ 【不许用冻结 md5 判它】★ (★2026-11-23 06:11 另一个并发会话走了生成器路线,
#   md5 合法地从 581f116a 变成 ade0d124 ⇒ 冻结 md5 会误报)★
#   ⇒ 改为断言「PREFLIGHT 里的 ISS-354 段同时存在于生成器数据源里」= 它走的是生成器路线, 不是人手改页。
REL_PREFLIGHT_SRC = "state/_iss277_preflight_appendix.md"
PREFLIGHT_MARK = "ISS-354 追加式订正"

REFS5 = ("Q1", "Q2", "U_BATPROT", "U_LDO_S28", "U_SUPV")
CLASSES4 = ("类-1", "类-2", "类-3", "类-4")
# ★降级方案 (a)(b)(c): 用【可区分的标题词】而不是裸 "(c)" (★裸串会误命中别的行★)★
PLAN_PAT = (
    ("(a)", re.compile(r"\*\*\(a\)[^\n]*焊盘图落盘")),
    ("(b)", re.compile(r"\*\*\(b\)[^\n]*防呆")),
    ("(c)", re.compile(r"\*\*\(c\)[^\n]*镜像兼容")),
)
VETO_IDS = tuple("V-%02d" % i for i in range(1, 16))
# ★每个 ref 的【官方查得的应为封装】的关键词 (★语义级断言·不是只查 ref 字符串在不在★)★
EXPECT_FP = {
    "Q1": ("VSON-CLIP", "DQG"),
    "Q2": ("VSON-CLIP", "DQG"),
    "U_BATPROT": ("DSE", "WSON-6"),
    "U_LDO_S28": ("X2SON", "DQN"),
    "U_SUPV": ("SOT-23",),
}

REL_WP = "HW/PCB/BOARD_ONEPASS_WORKPACKET.md"
REL_VL = "HW/PCB/ISS354_DOWNCUT_VETO_LIST.md"
REL_PCB = "HW/PCB/demo_mainboard.kicad_pcb"
REL_PF = "HW/PCB/BOARD_ONEPASS_PREFLIGHT.md"

GREEN, RED, YEL, DIM, RST = "\033[32m", "\033[31m", "\033[33m", "\033[2m", "\033[0m"
if not sys.stdout.isatty():
    GREEN = RED = YEL = DIM = RST = ""


def md5_of(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read(path: str) -> str:
    with open(path, encoding="utf-8", errors="ignore") as f:
        return f.read()


class Result:
    def __init__(self) -> None:
        self.rows = []          # (assert_id, ok, title, detail)
        self.failed = 0

    def add(self, aid: str, ok: bool, title: str, detail: str = "") -> bool:
        self.rows.append((aid, ok, title, detail))
        if not ok:
            self.failed += 1
        return ok

    def report(self) -> int:
        print("=" * 78)
        print("ISS-354 · demo 主板可制造性收口 · 自带闸 (只读)")
        print("=" * 78)
        for aid, ok, title, detail in self.rows:
            mark = f"{GREEN}PASS{RST}" if ok else f"{RED}FAIL{RST}"
            print(f"[{mark}] {aid:<5s} {title}")
            if detail:
                print(f"        {DIM}{detail}{RST}")
        print("-" * 78)
        if self.failed:
            print(f"{RED}★结论: {self.failed} 条断言未过 ⇒ 交卷内容不在盘 / 被改坏{RST}")
            return 1
        print(f"{GREEN}★结论: 全部断言通过 ⇒ 交卷内容在盘且未改坏{RST}")
        return 0


def check(root: str) -> Result:
    r = Result()
    wp_path = os.path.join(root, REL_WP)
    vl_path = os.path.join(root, REL_VL)
    pcb_path = os.path.join(root, REL_PCB)
    pf_path = os.path.join(root, REL_PF)

    for p in (wp_path, vl_path, pcb_path, pf_path):
        if not os.path.exists(p):
            r.add("A-0", False, "在盘文件存在", f"缺失: {os.path.relpath(p, root)}")
            return r
    r.add("A-0", True, "在盘文件存在", f"{REL_WP} / {REL_VL} / {REL_PCB} / {REL_PF}")

    wp = read(wp_path)
    vl = read(vl_path)

    # ---- A-1: 5 个 ref 的改项清单在盘 (逐个点名) ----
    wp_96 = wp[wp.find("§9-6"):] if "§9-6" in wp else ""
    missing = []
    for ref in REFS5:
        if ref not in wp_96:
            missing.append(ref)
    r.add("A-1", not missing,
          f"5 个 ref 的改项清单在盘 (WORKPACKET §9-6.1): {', '.join(REFS5)}",
          ("全部点名命中" if not missing else "缺失 ref: " + ", ".join(missing)))
    # 每条还要带【官方查得的应为封装】的关键词 (★语义级断言: 不能只证明 ref 字符串在盘★)
    no_col = []
    for ref in REFS5:
        kws = EXPECT_FP[ref]
        hit = any(ref in ln and any(k in ln for k in kws) for ln in wp_96.splitlines())
        if not hit:
            no_col.append(f"{ref}({'/'.join(kws)})")
    r.add("A-1b", not no_col,
          "每个 ref 都写出了【官方查得的应为封装】(语义级断言, 不是只报数)",
          ("全部命中" if not no_col else "缺官方封装证据的行: " + ", ".join(no_col)))

    # ---- A-2: 4 类不自洽在盘 ----
    miss_cls = [c for c in CLASSES4 if c not in vl]
    r.add("A-2", not miss_cls,
          f"4 类不自洽在盘 (VETO_LIST §0.5): {', '.join(CLASSES4)}",
          ("全部命中" if not miss_cls else "缺失: " + ", ".join(miss_cls)))

    # ---- A-3: SoM pin1 排向降级方案 (a)(b)(c) 在盘 ----
    miss_plan = [tag for tag, rx in PLAN_PAT if not rx.search(vl)]
    r.add("A-3", not miss_plan,
          "SoM pin1 排向的降级方案 (a)(b)(c) 在盘 (VETO_LIST §2.3)",
          ("全部命中" if not miss_plan else "缺失: " + ", ".join(miss_plan)))
    plan_wp = [tag for tag, rx in PLAN_PAT if not rx.search(wp_96)]
    r.add("A-3b", not plan_wp,
          "降级方案同时在 WORKPACKET §9-6.2 段",
          ("全部命中" if not plan_wp else "缺失: " + ", ".join(plan_wp)))
    r.add("A-3c", "V-01" in vl and "pin1" in vl,
          "SoM pin1 排向的实物实测判据 (V-01) 在盘",
          "V-01 + pin1 关键字命中" if ("V-01" in vl and "pin1" in vl) else "V-01 或 pin1 缺失")

    # ---- A-4: 下料前一票否决项 V-01..V-15 在盘 ----
    miss_v = [v for v in VETO_IDS if v not in vl]
    r.add("A-4", not miss_v,
          f"下料前一票否决项在盘 (VETO_LIST §1): {VETO_IDS[0]}..{VETO_IDS[-1]} ({len(VETO_IDS)} 条)",
          ("全部命中" if not miss_v else "缺失: " + ", ".join(miss_v)))

    # ---- A-5: 板指纹 + PREFLIGHT 零手改 ----
    pcb_md5 = md5_of(pcb_path)
    pcb_mt = os.popen('stat -c "%y" ' + '"' + pcb_path + '"').read().strip()
    ok_pcb = (pcb_md5 == EXPECT_PCB_MD5)
    r.add("A-5a", ok_pcb,
          f"零写板: {REL_PCB} md5 == {EXPECT_PCB_MD5}",
          f"实测 {pcb_md5}" if ok_pcb else f"实测 {pcb_md5} ≠ 期望 {EXPECT_PCB_MD5}")
    ok_mt = EXPECT_PCB_MTIME in pcb_mt
    r.add("A-5b", ok_mt,
          f"零写板: 板 mtime == {EXPECT_PCB_MTIME}",
          f"实测 {pcb_mt}" if ok_mt else f"实测 {pcb_mt} ≠ 期望 {EXPECT_PCB_MTIME}")
    pf_md5 = md5_of(pf_path)
    pf = read(pf_path)
    src_path = os.path.join(root, REL_PREFLIGHT_SRC)
    if os.path.exists(src_path):
        src = read(src_path)
        # ★PREFLIGHT 的追加块必须【逐字】来自生成器 sidecar ⇒ 有人手改页 ⇒ 该块对不上 ⇒ 判红★
        # ★只查【含 ISS-354 段的块】(★MD5_ANCHOR 块带占位符·生成器会替换·不能逐字比★)★
        blocks = re.findall(r"<!-- ([^:]+:[A-Z0-9_]+):BEGIN -->\n(.*?)<!-- \1:END -->", src, re.S)
        iss354_blocks = [(tag, body) for tag, body in blocks if PREFLIGHT_MARK in body]
        bad = []
        for tag, body in iss354_blocks:
            b = body.rstrip("\n")
            if b and b not in pf:
                bad.append(tag)
        ok_pf = (not iss354_blocks) or not bad
        r.add("A-5c", ok_pf,
              "零手改 PREFLIGHT: 含 ISS-354 段的追加块必须逐字来自生成器 sidecar (不是手改页)",
              (f"sidecar 中 {len(iss354_blocks)} 个含 ISS-354 段的块逐字命中 ✔ (PREFLIGHT md5 = {pf_md5})" if ok_pf
               else f"★以下追加块在 PREFLIGHT 里对不上 ⇒ 判定为【手改页】: {', '.join(bad)}★"))
    else:
        r.add("A-5c", True,
              "零手改 PREFLIGHT: 生成器数据源不在盘 (跳过该项判定)",
              f"{REL_PREFLIGHT_SRC} 缺失; PREFLIGHT md5 = {pf_md5}")
    return r


# ─────────────────────────────────────────────────────────────
# --selftest: ★反向用例★ (★在临时副本里破坏 ⇒ 闸必须红并点名★)
# ─────────────────────────────────────────────────────────────
def selftest(root: str) -> int:
    print("=" * 78)
    print("ISS-354 自带闸 · --selftest 反向用例 (★临时副本落项目盘 tmp/★)")
    print("=" * 78)
    sandbox_root = os.path.join(root, "tmp", "iss354", "selftest_sandbox")
    if os.path.exists(sandbox_root):
        shutil.rmtree(sandbox_root)
    pcb_dir = os.path.join(sandbox_root, "HW", "PCB")
    os.makedirs(pcb_dir, exist_ok=True)
    for rel in (REL_WP, REL_VL, REL_PCB, REL_PF):
        shutil.copy2(os.path.join(root, rel), os.path.join(sandbox_root, rel))
    # 生成器数据源也要在沙盒里 (A-5c 要读它)
    src = os.path.join(root, REL_PREFLIGHT_SRC)
    if os.path.exists(src):
        d = os.path.dirname(os.path.join(sandbox_root, REL_PREFLIGHT_SRC))
        os.makedirs(d, exist_ok=True)
        shutil.copy2(src, os.path.join(sandbox_root, REL_PREFLIGHT_SRC))

    fails = 0

    def run(label: str, expect_fail: bool, must_mention: str = "") -> int:
        nonlocal fails
        res = check(sandbox_root)
        red = res.failed > 0
        text = "\n".join(f"{aid} {title} | {detail}" for aid, ok, title, detail in res.rows)
        named = (must_mention in text) if must_mention else True
        ok = (red == expect_fail) and named
        if ok:
            print(f"[{GREEN}PASS{RST}] {label}  (期望{'红' if expect_fail else '绿'} · "
                  f"{'点名命中 ' + must_mention if must_mention else '无点名要求'})")
        else:
            print(f"[{RED}FAIL{RST}] {label}  (期望{'红' if expect_fail else '绿'} · "
                  f"must_mention={must_mention!r} · 实际红={red} 点名命中={named})")
            for aid, o, title, detail in res.rows:
                if not o:
                    print(f"        未过: {aid} {title} | {detail}")
            fails += 1
        return 0 if ok else 1

    # 0) 基线: 副本必须是绿的 (★否则下面的红没意义★)
    print(f"{DIM}--- 用例 0: 基线 (副本应当全绿) ---{RST}")
    run("用例 0 · 基线绿", expect_fail=False)

    # 1) 删掉一条一票否决项 (V-07) ⇒ 必须红并点名 V-07
    print(f"{DIM}--- 用例 1: 删掉 V-07 ⇒ 闸必须红并点名 ---{RST}")
    vl_path = os.path.join(sandbox_root, REL_VL)
    vl_lines = read(vl_path).splitlines(keepends=True)
    kept = [ln for ln in vl_lines if "V-07" not in ln]
    removed = len(vl_lines) - len(kept)
    with open(vl_path, "w", encoding="utf-8") as f:
        f.writelines(kept)
    print(f"{DIM}  (副本里已删掉 {removed} 行含 V-07){RST}")
    run("用例 1 · 删 V-07 ⇒ 红 + 点名 V-07", expect_fail=True, must_mention="V-07")
    # 还原
    shutil.copy2(os.path.join(root, REL_VL), vl_path)

    # 2) 改板 md5 ⇒ 必须红并点名板指纹
    print(f"{DIM}--- 用例 2: 篡改板文件 ⇒ 闸必须红并点名板指纹 ---{RST}")
    pcb_path = os.path.join(sandbox_root, REL_PCB)
    with open(pcb_path, "ab") as f:
        f.write(b"\n; iss354 selftest tamper\n")
    run("用例 2 · 篡改板 ⇒ 红 + 点名板指纹", expect_fail=True, must_mention="零写板")
    shutil.copy2(os.path.join(root, REL_PCB), pcb_path)

    # 3) 手改 PREFLIGHT 页里的追加块 (不动生成器 sidecar) ⇒ 必须红并点名
    print(f"{DIM}--- 用例 3: 手改 PREFLIGHT 追加块 (不动生成器 sidecar) ⇒ 闸必须红并点名 ---{RST}")
    pf_path = os.path.join(sandbox_root, REL_PF)
    pf_txt = read(pf_path)
    # 在 ISS-354 段里改一个字 (V-1-① → V-1-X) ⇒ 该块不再逐字命中 sidecar
    tampered = pf_txt.replace("V-1-①", "V-1-X", 1)
    if tampered == pf_txt:
        tampered = pf_txt.replace("ISS-354 追加式订正", "ISS-354 追加式订正 ★手改★", 1)
    with open(pf_path, "w", encoding="utf-8") as f:
        f.write(tampered)
    run("用例 3 · 手改 PREFLIGHT ⇒ 红 + 点名", expect_fail=True, must_mention="手改页")
    shutil.copy2(os.path.join(root, REL_PF), pf_path)

    # 4) 删掉 WORKPACKET 里所有 Q2 改项行 ⇒ 必须红并点名 Q2
    print(f"{DIM}--- 用例 4: 删掉 WORKPACKET 里的 Q2 改项行 ⇒ 闸必须红并点名 Q2 ---{RST}")
    wp_path = os.path.join(sandbox_root, REL_WP)
    wp_lines = read(wp_path).splitlines(keepends=True)
    kept = [ln for ln in wp_lines if not ("Q2" in ln and "VSON-CLIP" in ln)]
    removed = len(wp_lines) - len(kept)
    with open(wp_path, "w", encoding="utf-8") as f:
        f.writelines(kept)
    print(f"{DIM}  (副本里已删掉 {removed} 行 Q2 的官方封装证据){RST}")
    run("用例 4 · 删 Q2 改项行 ⇒ 红 + 点名 Q2", expect_fail=True, must_mention="Q2")
    shutil.copy2(os.path.join(root, REL_WP), wp_path)

    # 5) 删掉降级方案 (c) ⇒ 必须红并点名
    print(f"{DIM}--- 用例 5: 删掉降级方案 (c) ⇒ 闸必须红并点名 ---{RST}")
    vl_lines = read(vl_path).splitlines(keepends=True)
    kept = [ln for ln in vl_lines if "两排镜像兼容" not in ln]
    with open(vl_path, "w", encoding="utf-8") as f:
        f.writelines(kept)
    run("用例 5 · 删方案 (c) ⇒ 红 + 点名", expect_fail=True, must_mention="(c)")
    shutil.copy2(os.path.join(root, REL_VL), vl_path)

    # 6) 还原后必须回到绿 (★证明闸不是恒红★)
    print(f"{DIM}--- 用例 6: 全部还原 ⇒ 必须回到绿 (证明闸不是恒红) ---{RST}")
    run("用例 6 · 还原后绿", expect_fail=False)

    shutil.rmtree(sandbox_root, ignore_errors=True)

    print("-" * 78)
    if fails:
        print(f"{RED}★selftest FAIL: {fails} 条反向用例没过{RST}")
        return 1
    print(f"{GREEN}★selftest 全过 (★闸会红·不是恒绿·点名有效★){RST}")
    print("ALL TESTS PASS")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=REPO_ROOT, help="仓库根 (自测用)")
    ap.add_argument("--selftest", action="store_true", help="★反向用例★")
    args = ap.parse_args()
    root = os.path.abspath(args.root)
    if args.selftest:
        return selftest(root)
    res = check(root)
    return res.report()


if __name__ == "__main__":
    sys.exit(main())
