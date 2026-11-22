#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MECH/check_mech_dual_caliber_gate.py —— 结构侧「双口径判定脚本」机器闸 (ISS-352 第 2 批)

=====================================================================
★**性质**: 只读机器闸 · ★零写板 / 零落表 / 零改任何既有脚本 / 零外发** ★
★**派活**: 项目总工 (main / moli) · ISS-352 · 2026-11-23 · 交卷人 = 结构总工 (mech-lead) ★
★**关联**: `HANDOFF/2026-11-23_mech-lead_ISS352_MECH双口径第2批.md` ·
          `MECH/BOARD_FRAME_CALIBER_STATUS.md` (口径状态页) ·
          `HW/PCB/BOARD_FRAME_CALIBER.md` §6 `cal:FRAMES` (帧 id 唯一权威) ★

────────────────────────────────────────────────────────────────────────
【作用】★让「单口径脚本」以后进不了「板只改一次」那一趟★

  扫 ISS-345 派活单点名的 **8 个 MECH 判定脚本** (★名单写死·不扫全目录★) ⇒ 逐个断言:
    ① **同时含两档标识**: 60×30 档 (`F30A`) 与 160×100 档 (`B160x100`) 两边都在
    ② **默认档 = F30A** (★本闸【不许自己拍默认档】· 默认档归 U-1 拍完后 main 切★)
    ③ **档位切换开关存在** (`--frame` / `MECH_FRAME`) —— 没有开关 = main 切不了默认档
    ④ **已退役脚本必须带退役标记** (★不许两个都留当活件用★)
  另断言:
    ⑤ `MECH/hw_cross_review_check.py` md5 仍 = `e521387b87b0fcdf9f22d56f14199967`
       (★它被 `check_demo_struct_truth.py` / `cavity_recalc_check.py` 两个闸 md5 钉住·不许碰★)
    ⑥ 本闸自身的 `DEFAULT_FRAME_ID` = `F30A` (自证: 闸不许放过自己)

────────────────────────────────────────────────────────────────────────
【rc 语义】
  0 = 全部通过
  1 = 有断言不通过 (逐条列出 + 点名文件)
  2 = 参数/IO 错误

────────────────────────────────────────────────────────────────────────
【用法】
  python3 MECH/check_mech_dual_caliber_gate.py            # 扫真件 (只读)
  python3 MECH/check_mech_dual_caliber_gate.py --selftest  # 反向用例 (末行 ALL TESTS PASS)
  python3 MECH/check_mech_dual_caliber_gate.py --root DIR  # 扫指定树 (反向用例在 tmp/ 副本上做)
"""
from __future__ import annotations

import hashlib
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)

# ★本闸的期望默认档 (★F30A = 历史产品板口径·与现役台架板口径不可混用★)★
DEFAULT_FRAME_ID = "F30A"

# ★档位标识 (帧 id 逐字取自 HW/PCB/BOARD_FRAME_CALIBER.md §6 cal:FRAMES★)★
CALIBER_TOKENS = {
    "60x30": ("60×30 档 (F30A)", ("F30A", "60×30", "60x30")),
    "160x100": ("160×100 档 (B160x100)", ("B160x100", "160×100", "160x100")),
}

# ★8 个脚本名单 (ISS-345 派活单 §0② 点名的 8 个·写死·不扫全目录)★
#   mode = dual   → 必须双口径 + 默认档 F30A + 有切档开关
#   mode = retired → 已退役件: 必须带退役标记 + 点名接班件 + 不许自带默认档开关
#   mode = multi  → 既有帧表脚本: 三档一次跑完 (无「默认档」概念) + 必须逐字带权威帧 id
SCRIPTS = [
    ("MECH/pinset2_mech_check.py", "dual"),
    ("MECH/skeleton_section_check.py", "dual"),
    ("MECH/fit_check_v3_30mm.py", "dual"),
    ("MECH/fit_check.py", "retired"),
    ("MECH/cross_review_check.py", "dual"),
    ("MECH/board_frame_feasibility.py", "multi"),
    ("MECH/board_port_opening_s6_check.py", "multi"),
    ("MECH/jd_y0_feasibility.py", "multi"),
]

RETIRED_MARK = "MECH_CALIBER_RETIRED"
RETIRED_SUCCESSOR = "fit_check_v3_30mm.py"
PROTECTED_MD5 = {
    "MECH/hw_cross_review_check.py": "e521387b87b0fcdf9f22d56f14199967",
}
ALL_FRAME_IDS = ("B160x100", "F30A", "P60x15")

RE_DEFAULT_FID = re.compile(r"DEFAULT_FRAME_ID\s*=\s*[\"']?([A-Za-z0-9_]+)")
RE_SWITCH = re.compile(r"--frame|MECH_FRAME")


def md5_of(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def check_tree(root):
    """→ (ok, [失败条目], [通过条目])"""
    fails, passes = [], []

    def ok(rel, cond, msg):
        if cond:
            passes.append((rel, msg))
        else:
            fails.append((rel, msg))
        return cond

    # ---- ⑥ 本闸自证: 默认档不许被偷偷改掉 ----
    ok("(闸自证)", DEFAULT_FRAME_ID == "F30A",
       "本闸 DEFAULT_FRAME_ID = F30A (期望 60×30 档)")

    # ---- ① ② ③ ④ 逐个脚本 ----
    for rel, mode in SCRIPTS:
        p = os.path.join(root, rel)
        if not os.path.isfile(p):
            fails.append((rel, "★文件不在盘上 (期望 %s)★" % rel))
            continue
        with open(p, "r", encoding="utf-8", errors="ignore") as fh:
            txt = fh.read()
        for ck, (cname, toks) in CALIBER_TOKENS.items():
            hit = next((t for t in toks if t in txt), None)
            ok(rel, hit is not None,
               "%s 档标识: %s" % (cname, ("命中 %r" % hit) if hit else
                                  "★缺 (三个写法 %s 一个都没有)★" % "/".join(toks)))
        if mode == "dual":
            m = RE_DEFAULT_FID.search(txt)
            ok(rel, m is not None and m.group(1) == "F30A",
               "默认档 = F30A (期望 60×30 档 · 历史产品板口径): %s" %
               (("读到 %r" % m.group(1)) if m else "★没有 DEFAULT_FRAME_ID★"))
            ok(rel, bool(RE_SWITCH.search(txt)),
               "切档开关存在 (--frame / MECH_FRAME)")
        elif mode == "retired":
            ok(rel, RETIRED_MARK in txt,
               "退役标记 `%s` 在位" % RETIRED_MARK)
            ok(rel, RETIRED_SUCCESSOR in txt,
               "点名接班件 `%s`" % RETIRED_SUCCESSOR)
            ok(rel, not RE_DEFAULT_FID.search(txt),
               "已退役件不许自带默认档开关 (不许冒充双口径活件)")
        else:  # multi
            miss = [f for f in ALL_FRAME_IDS if f not in txt]
            ok(rel, not miss,
               "三档权威帧 id 齐备 (B160x100 / F30A / P60x15 · 末档已作废): %s" %
               ("全在" if not miss else "★缺 %s★" % ",".join(miss)))
            m = RE_DEFAULT_FID.search(txt)
            ok(rel, (m is None) or (m.group(1) == "F30A"),
               "若自带默认档则必须是 F30A: %s" %
               (("读到 %r" % m.group(1)) if m else "无默认档 (三档一次跑完)"))

    # ---- ⑤ md5 钉死文件 ----
    for rel, want in PROTECTED_MD5.items():
        p = os.path.join(root, rel)
        if not os.path.isfile(p):
            fails.append((rel, "★文件不在盘上 (期望 %s)★" % rel))
            continue
        got = md5_of(p)
        ok(rel, got == want, "md5 钉死 = %s (实读 %s)" % (want, got))

    return (not fails), fails, passes


def _sandbox(root, name):
    """→ 沙盒目录 (真件只读复制·★反向用例不许在真件上动手脚★)"""
    sb = os.path.join(root, "tmp", "iss352", "selftest", name)
    if os.path.isdir(sb):
        shutil.rmtree(sb)
    for rel, _ in SCRIPTS:
        dst = os.path.join(sb, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(os.path.join(root, rel), dst)
    for rel in PROTECTED_MD5:
        dst = os.path.join(sb, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(os.path.join(root, rel), dst)
    return sb


def _red_names(fails):
    """→ 失败条目里点名的文件名集合"""
    return set(r for r, _ in fails)


def self_test(root):
    """★反向用例: 沙盒副本上动手脚 ⇒ 闸必须判红并点名; 恢复 ⇒ 判绿★"""
    cases = []
    errs = []

    def ok(cond, msg):
        print("  [%s] %s" % ("PASS" if cond else "FAIL", msg))
        if not cond:
            errs.append(msg)
        return bool(cond)

    # ---- 用例① · 正向: 真件全绿 ----
    good, f, p = check_tree(root)
    cases.append(("正向: 真件 8 个脚本双口径 + md5 钉死 ⇒ 判绿", good,
                  "失败 %d 条 / 通过 %d 条" % (len(f), len(p))))
    ok(good, "正向: 真件判绿 (失败 %d 条)" % len(f))

    # ---- 用例② · 反向: 删掉某脚本的 160×100 标识 ⇒ 判红并点名 ----
    sb = _sandbox(root, "rev_b160")
    tgt = os.path.join(sb, "MECH/cross_review_check.py")
    with open(tgt, "r", encoding="utf-8") as fh:
        txt = fh.read()
    stripped = txt
    for t in CALIBER_TOKENS["160x100"][1]:
        stripped = stripped.replace(t, "")
    with open(tgt, "w", encoding="utf-8") as fh:
        fh.write(stripped)
    good2, f2, p2 = check_tree(sb)
    named = _red_names(f2)
    hit = "MECH/cross_review_check.py" in named
    cases.append(("反向: 沙盒删掉 cross_review_check.py 的 160×100 标识 ⇒ 判红并点名该脚本",
                  (not good2) and hit,
                  "判绿=%s · 点名命中=%s · 失败 %d 条" % (good2, hit, len(f2))))
    ok((not good2) and hit,
       "反向①: 删 160×100 标识 ⇒ 判红 (%s) 且点名 cross_review_check.py (%s)"
       % ("绿了★不对" if good2 else "红", "点名了" if hit else "没点名★不对"))

    # ---- 用例③ · 反向: 把默认档偷偷改成 160×100 ⇒ 判红并点名 ----
    sb3 = _sandbox(root, "rev_default")
    tgt3 = os.path.join(sb3, "MECH/pinset2_mech_check.py")
    with open(tgt3, "r", encoding="utf-8") as fh:
        txt3 = fh.read()
    bad3 = re.sub(r'DEFAULT_FRAME_ID\s*=\s*"F30A"', 'DEFAULT_FRAME_ID = "B160x100"', txt3, count=1)
    with open(tgt3, "w", encoding="utf-8") as fh:
        fh.write(bad3)
    good3, f3, p3 = check_tree(sb3)
    named3 = _red_names(f3)
    hit3 = "MECH/pinset2_mech_check.py" in named3
    cases.append(("反向: 沙盒把 pinset2_mech_check.py 的默认档改成 B160x100 ⇒ 判红并点名该脚本",
                  (not good3) and hit3,
                  "判绿=%s · 点名命中=%s · 失败 %d 条" % (good3, hit3, len(f3))))
    ok((not good3) and hit3,
       "反向②: 默认档偷偷改成 B160x100 ⇒ 判红 (%s) 且点名 pinset2_mech_check.py (%s)"
       % ("绿了★不对" if good3 else "红", "点名了" if hit3 else "没点名★不对"))

    # ---- 用例④ · 反向: 动 md5 钉死文件一个字节 ⇒ 判红 ----
    sb4 = _sandbox(root, "rev_md5")
    tgt4 = os.path.join(sb4, "MECH/hw_cross_review_check.py")
    with open(tgt4, "a", encoding="utf-8") as fh:
        fh.write("\n# ★反向用例: 动 1 字节★\n")
    good4, f4, p4 = check_tree(sb4)
    hit4 = "MECH/hw_cross_review_check.py" in _red_names(f4)
    cases.append(("反向: 沙盒给 md5 钉死文件追加 1 行 ⇒ 判红并点名", (not good4) and hit4,
                  "判绿=%s · 点名命中=%s" % (good4, hit4)))
    ok((not good4) and hit4,
       "反向③: 动 md5 钉死文件 ⇒ 判红 (%s) 且点名 (%s)"
       % ("绿了★不对" if good4 else "红", "点名了" if hit4 else "没点名★不对"))

    # ---- 用例⑤ · 恢复 ⇒ 判绿 ----
    sb5 = _sandbox(root, "rev_b160")     # ★从真件重新复制 = 还原 (★真件只读·没被动过★)
    good5, f5, p5 = check_tree(sb5)
    cases.append(("恢复: 沙盒副本还原后 ⇒ 判绿", good5,
                  "失败 %d 条 / 通过 %d 条" % (len(f5), len(p5))))
    ok(good5, "恢复: 沙盒还原后判绿 (失败 %d 条)" % len(f5))

    print("-" * 78)
    n_ok = sum(1 for _, c, _ in cases if c)
    for i, (name, c, detail) in enumerate(cases, 1):
        print("  %s 用例 %d: %s" % ("✅" if c else "❌", i, name))
        print("        %s" % detail)
    print("-" * 78)
    print("self-test: %d/%d 用例符合预期 ⇒ %s"
          % (n_ok, len(cases), "全部通过" if n_ok == len(cases) else "★有用例不符合预期★"))
    if n_ok == len(cases):
        print("ALL TESTS PASS")
        return 0
    print("★SELF-TEST FAILED★")
    return 1


def main():
    root = PROJ
    args = sys.argv[1:]
    if "--root" in args:
        i = args.index("--root")
        root = args[i + 1] if i + 1 < len(args) else PROJ
        args = [a for a in args if a != "--root"]
    if "--selftest" in args:
        return self_test(root)

    good, fails, passes = check_tree(root)
    print("=" * 88)
    print("MECH 双口径机器闸 (ISS-352) —— 扫 %s" % root)
    print("=" * 88)
    print("断言 ① 双口径标识 ② 默认档 = F30A ③ 切档开关 ④ 退役标记 ⑤ md5 钉死 ⑥ 闸自证")
    print("-" * 88)
    for rel, msg in passes:
        print("  ✅ %-42s %s" % (rel, msg))
    if fails:
        print("-" * 88)
        for rel, msg in fails:
            print("  ❌ %-42s %s" % (rel, msg))
    print("-" * 88)
    print("判定: %s (通过 %d 条 / 失败 %d 条)" % ("✅ 全绿" if good else "❌ 判红",
                                                 len(passes), len(fails)))
    print("★ 帧 id 唯一权威: HW/PCB/BOARD_FRAME_CALIBER.md §6 `cal:FRAMES` "
          "(B160x100 / F30A / P60x15)")
    print("★ 默认档归属: 本闸【不许自己拍默认档】⇒ 默认档恒为 F30A, 切档权归 U-1 拍完后 main")
    print("=" * 88)
    return 0 if good else 1


if __name__ == "__main__":
    sys.exit(main())
