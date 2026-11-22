#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-349 · 「板只改一次」板侧项全集页的【重跑不蒸发】机器闸
=================================================================================================
派活: state/dispatch_briefs/ISS-349_hw_preflight_regen_idempotent.md (项目总工 2026-11-23 01:4x)

★**它守的是什么**: ★**「清单页」必须是生成器的产物, 且生成器重跑不许把任何一条蒸发掉** ★

  ★**病根 (★ISS-343 那一单留下的★)**: `B33_PIN_LAND_1P27` (E-1 排针 land pitch) 被【手写】进了
    `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` —— ★**那一份是 `state/_iss277_build_preflight.py` 的产物**★ ⇒
    ★**下一次重跑生成器, 这一条【静默蒸发】** ⇒ 「板只改一次」那一趟的板侧项全集少一条 ⇒
    ★**实物排针照样装不进 ⇒ 补做 = 板 md5 变第二次 (2-4 周 + ¥4-8K)** ★

  ★**为什么既有覆盖度闸抓不住**: `HW/check_onepass_preflight_coverage.py` 判的是「清单页里有没有这条」
    ⇒ 页里现在【有】⇒ 判绿 ⇒ ★**但下一次重跑之后页里【没有】了 ⇒ 它从不读生成器 ⇒ 绿是骗的** ★

四条判据 (★每条都要能当场判红, 不许是装饰★):
  C1 表/JSON 同源 : §2 表的 id 集合 == §7 JSON 的 id 集合 (★逐个相等, 不是只比个数★)
  C2 重跑幂等     : ★**真页 == 生成器沙盒重跑输出 (逐字节)**★ ⇒ 不等 ⇒ 判红并贴 diff
                    (★沙盒 = 项目盘副本·`PREFLIGHT_PROJ` 指向它·★真页/真板零写★)
  C3 来源在册     : 每一条 item 的 `source_iss` 必须在 `HW/check_onepass_preflight_coverage.py` 的
                    `SOURCES` 里 (★**只读那个文件·一个字不许改**★) ⇒ 不在 ⇒ 判红并点名
  C4 必需项在场   : ★**加严块 (ISS-349 新增)**: `B33_PIN_LAND_1P27` (★E-1 排针 land pitch 那一条★)
                    必须在清单里 ⇒ ★**生成器里那条被删掉 / 页里那条被手改掉 ⇒ 都命中这里** ★

★**方向纪律 (★本项目铁律★)**: ★**只许【加严】不许【放宽】** ★
  ⇒ ① `HW/check_onepass_preflight_coverage.py` 一个字未改 (★它是钉板闸⑥·只读★)
  ⇒ ② `HW/check_workpack_state_values.py` 一个字未改 (★ISS-289 的闸★)
  ⇒ ③ `state/gate_check.py` 一个字未改 (★那是 main 的地界·挂载行写进交卷页 §B4★)
  ⇒ ④ 本闸【只读盘 + 只写项目盘沙盒】⇒ ★**零写板 · 零落表 · 零改既有闸★ ★

退出码: 0 = 全过 · 1 = 有不通过项 (★闸红★) · 2 = 用法错 · 3 = ★闸崩 (★工具/沙盒跑不起来·与「闸红」严格区分★)
用法:
  python3 -B HW/check_preflight_regen_idempotent.py             # 主模式
  python3 -B HW/check_preflight_regen_idempotent.py --selftest   # 反向用例 (R1/R2/R3 + 正例)
★**自检用 env 覆盖★:
  PREFLIGHT_PROJ      项目根 (★默认 = 本文件的上一级目录★)
  PREFLIGHT_CHECKLIST 被判的清单页 (★默认 = PROJ/HW/PCB/BOARD_ONEPASS_PREFLIGHT.md★)
  PREFLIGHT_GEN_PROJ  ★**生成器与真源的出处**★ (★默认 = PROJ·R1 用它指向被改坏的沙盒★)
  PREFLIGHT_SANDBOX   重跑沙盒的落点 (★默认 = PROJ/tmp/iss349/regen_gate·★绝不落 /tmp★★)
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.environ.get("PREFLIGHT_PROJ") or os.path.join(HERE, ".."))
CHECKLIST = os.environ.get("PREFLIGHT_CHECKLIST") or os.path.join(
    PROJ, "HW", "PCB", "BOARD_ONEPASS_PREFLIGHT.md")
GEN_PROJ = os.environ.get("PREFLIGHT_GEN_PROJ") or PROJ
SANDBOX = os.environ.get("PREFLIGHT_SANDBOX") or os.path.join(PROJ, "tmp", "iss349", "regen_gate")
COVERAGE_GATE = os.path.join(PROJ, "HW", "check_onepass_preflight_coverage.py")

# ★★C4 的必需项 (★ISS-349 加进来的那一条·★id 与 ISS-343 已写进 JSON 的保持一致·不许改★ ★)
#   ★**以后再加板侧项 ⇒ 走【加严】流程: 往这个清单里加一行 (不许改既有条目的 id)★ ★
REQUIRED_ITEMS = ("B33_PIN_LAND_1P27",)

FIELDS = ("id", "source_iss", "title", "current_state", "action",
          "criterion", "step", "blocked_by", "evidence")


# ==============================================================================
# 基础读数
# ==============================================================================
def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_text(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def parse_page(path):
    """★清单页 ⇒ (表 id 列表, JSON items, 全文) ★

    ★**§2 表 id**: 只在 `## §2` 那一节里抓 (★不许把别的表的行算进来★) ★
    ★**§7 JSON**: 取页里【第一个】```json 块 (★与 `HW/check_onepass_preflight_coverage.py`
      的 `load_items()` 同口径·免得两个闸读的不是同一块★) ★
    """
    txt = read_text(path)
    m2 = re.search(r"^##\s*§2\b(.*?)^##\s*§3\b", txt, re.S | re.M)
    tbl_sec = m2.group(1) if m2 else ""
    tbl = re.findall(r"^\|\s*★\*\*`([A-Za-z0-9_]+)`\*\*\s*★\s*\|", tbl_sec, re.M)
    mj = re.search(r"```json\s*(\{.*?\})\s*```", txt, re.S)
    items = None
    if mj:
        try:
            data = json.loads(mj.group(1))
            items = data.get("items") if isinstance(data, dict) else None
        except Exception:
            items = None
    return tbl, items, txt


def read_coverage_sources(gate_path):
    """★从覆盖度闸里读 `SOURCES` 集合 (★只读·一个字不许改★) ★"""
    if not os.path.exists(gate_path):
        raise RuntimeError("★找不到覆盖度闸 %s ⇒ 闸崩 (★fail-closed★)" % gate_path)
    txt = read_text(gate_path)
    m = re.search(r"^SOURCES\s*=\s*\{(.*?)\}", txt, re.S | re.M)
    if not m:
        raise RuntimeError("★覆盖度闸里读不到 SOURCES ⇒ 闸崩 (★fail-closed★)")
    return set(re.findall(r"ISS-\d+", m.group(1)))


# ==============================================================================
# 沙盒 (★项目盘 · 绝不落 /tmp ★)
# ==============================================================================
# ★沙盒要装的东西 (★生成器 + 它的全部真源输入★)
SANDBOX_STATE_FILES = ("*.py", "*.md", "*.sh")
SANDBOX_SKIP_DIRS = (os.path.join("HW", "PCB", "production"),
                     os.path.join("HW", "PCB", "_tmp_pi5"))


def make_sandbox(src, dst):
    """★把 `src` 项目根复制成沙盒 `dst` (★只读 src·只写 dst★) ★

    ⇒ 装: `state/*.py|*.md|*.sh` + `state/fragments/pm.yaml` (★E-1 裁决原文的出处★) + `HW/` 全量
    ⇒ 不装: `HW/PCB/production` / `HW/PCB/_tmp_pi5` (★生成器不读它们·省 28M★)
    """
    if os.path.exists(dst):
        shutil.rmtree(dst)
    os.makedirs(os.path.join(dst, "state", "fragments"), exist_ok=True)
    for pat in SANDBOX_STATE_FILES:
        for fn in sorted(os.listdir(os.path.join(src, "state"))):
            if fn.endswith(pat.lstrip("*")):
                s = os.path.join(src, "state", fn)
                if os.path.isfile(s):
                    shutil.copy2(s, os.path.join(dst, "state", fn))
    pm = os.path.join(src, "state", "fragments", "pm.yaml")
    if os.path.exists(pm):
        shutil.copy2(pm, os.path.join(dst, "state", "fragments", "pm.yaml"))
    hw_src = os.path.join(src, "HW")
    shutil.copytree(hw_src, os.path.join(dst, "HW"),
                    ignore=shutil.ignore_patterns("production", "_tmp_pi5"))
    os.makedirs(os.path.join(dst, "tmp"), exist_ok=True)
    return dst


def regen(gen_proj, sandbox_root):
    """★在沙盒里跑一次真生成器 ⇒ (rc, 输出, 沙盒页路径) ★

    ★**真页/真板零写**: 生成器只往沙盒的 `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 写 ★
    """
    dst = os.path.join(sandbox_root, "regen")
    make_sandbox(gen_proj, dst)
    env = dict(os.environ)
    env["PREFLIGHT_PROJ"] = dst
    env["TMPDIR"] = os.path.join(dst, "tmp")
    cmd = [sys.executable, "-B", os.path.join(dst, "state", "_iss277_build_preflight.py")]
    p = subprocess.run(cmd, cwd=dst, env=env, stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, timeout=1800)
    out = (p.stdout or b"").decode("utf-8", "replace")
    page = os.path.join(dst, "HW", "PCB", "BOARD_ONEPASS_PREFLIGHT.md")
    return p.returncode, out, page


# ==============================================================================
# 四条判据
# ==============================================================================
def check_C1(tbl_ids, items):
    """★C1 · §2 表 id 集合 == §7 JSON id 集合 (★逐个相等, 不是只比个数★) ★"""
    ok, bad = True, []
    if items is None:
        return False, ["     ❌ 清单页里读不到可解析的 JSON 块 ⇒ C1 fail-closed"]
    js_ids = [str(it.get("id")) for it in items]
    if len(tbl_ids) != len(set(tbl_ids)):
        dup = sorted({i for i in tbl_ids if tbl_ids.count(i) > 1})
        ok = False
        bad.append("❌ §2 表里 id 重复: %s" % dup)
    if len(js_ids) != len(set(js_ids)):
        dup = sorted({i for i in js_ids if js_ids.count(i) > 1})
        ok = False
        bad.append("❌ §7 JSON 里 id 重复: %s" % dup)
    only_tbl = sorted(set(tbl_ids) - set(js_ids))
    only_js = sorted(set(js_ids) - set(tbl_ids))
    if only_tbl or only_js:
        ok = False
        bad.append("❌ 表与 JSON 的 id 集合不相等 ⇒ 差集: 只在表里 = %s · 只在 JSON 里 = %s"
                   % (only_tbl, only_js))
    return ok, ["     §2 表 %d 行 (唯一 id %d) · §7 JSON %d 条 (唯一 id %d) · 集合逐一相等: %s"
                % (len(tbl_ids), len(set(tbl_ids)), len(js_ids), len(set(js_ids)),
                   "✔" if ok else "❌")] + ["     ❌ %s" % b for b in bad]


def check_C2(checklist, gen_proj, sandbox_root):
    """★C2 · 真页 == 生成器沙盒重跑输出 (★逐字节★) ⇒ 不等 ⇒ 判红并贴 diff ★"""
    if not os.path.exists(checklist):
        return False, ["     ❌ 找不到被判的清单页 %s ⇒ C2 fail-closed" % checklist]
    rc, out, page = regen(gen_proj, sandbox_root)
    if rc != 0 or not os.path.exists(page):
        return False, ["     ❌ ★**闸崩**★: 沙盒重跑生成器失败 (rc=%d) ⇒ 本判据判不了 (★与「闸红」严格区分★)"
                       % rc, "     --- 生成器输出 (末尾 40 行) ---"] + \
            ["     " + l for l in out.splitlines()[-40:]]
    a = read_text(checklist).split("\n")
    b = read_text(page).split("\n")
    if a == b:
        return True, ["     真页 md5 = %s · 沙盒重跑输出 md5 = %s · 零行差异: ✔"
                      % (md5(checklist), md5(page))]
    d = list(difflib.unified_diff(a, b, "真页(%s)" % checklist, "重跑输出(%s)" % page,
                                  lineterm="", n=0))
    only_a = sorted(set(re.findall(r"^\s*\"id\": \"([A-Za-z0-9_]+)\"", "\n".join(a), re.M)) -
                    set(re.findall(r"^\s*\"id\": \"([A-Za-z0-9_]+)\"", "\n".join(b), re.M)))
    only_b = sorted(set(re.findall(r"^\s*\"id\": \"([A-Za-z0-9_]+)\"", "\n".join(b), re.M)) -
                    set(re.findall(r"^\s*\"id\": \"([A-Za-z0-9_]+)\"", "\n".join(a), re.M)))
    bad = ["❌ 真页 != 沙盒重跑输出 ⇒ ★**页与生成器不同源 (重跑会改页)★** ⇒ md5 %s vs %s"
           % (md5(checklist), md5(page))]
    if only_a or only_b:
        bad.append("❌ id 差集: 只在真页里 = %s · 只在重跑输出里 = %s" % (only_a, only_b))
    bad.append("--- diff (前 40 行) ---")
    bad += ["    " + l for l in d[:40]]
    if len(d) > 40:
        bad.append("    ... (diff 共 %d 行·截断)" % len(d))
    return False, ["     真页 md5 = %s · 沙盒重跑输出 md5 = %s · 差异行数 = %d"
                   % (md5(checklist), md5(page), len(d))] + bad


def check_C3(items, sources):
    """★C3 · 每条 item 的 `source_iss` 必须在覆盖度闸的 `SOURCES` 里 ⇒ 不在 ⇒ 判红并点名 ★"""
    ok, bad = True, []
    if items is None:
        return False, ["     ❌ 清单页里读不到可解析的 JSON 块 ⇒ C3 fail-closed"]
    for it in items:
        s = str(it.get("source_iss", "")).strip()
        if s not in sources:
            ok = False
            bad.append("❌ id=%s 的 source_iss=%r 不在覆盖度闸的 SOURCES 里 ⇒ 来源不明"
                       % (it.get("id"), s))
    return ok, ["     %d 条 item 的 source_iss 全在 SOURCES (%d 个来源单) 里: %s"
                % (len(items), len(sources), "✔" if ok else "❌")] + \
        ["     ❌ %s" % b for b in bad]


def check_C4(items, tbl_ids):
    """★C4 · 必需项在场 (★加严块: 生成器里那条被删 / 页里那条被手改掉 ⇒ 都命中这里★) ★"""
    ok, bad = True, []
    if items is None:
        return False, ["     ❌ 清单页里读不到可解析的 JSON 块 ⇒ C4 fail-closed"]
    js_ids = [str(it.get("id")) for it in items]
    for rid in REQUIRED_ITEMS:
        where = []
        if rid in tbl_ids:
            where.append("§2 表")
        if rid in js_ids:
            where.append("§7 JSON")
        if not where:
            ok = False
            bad.append("❌ 必需板侧项缺失: %s (★表里没有·JSON 里也没有★) ⇒ ★**生成器里那条被删掉 / "
                       "页里那条被手改掉 ⇒ 命中这里** ★" % rid)
        else:
            bad.append("     ✔ 必需板侧项在场: %s (%s)" % (rid, " + ".join(where)))
    return ok, ["     必需项 %d 个: %s" % (len(REQUIRED_ITEMS), "✔" if ok else "❌")] + bad


# ==============================================================================
# 主流程
# ==============================================================================
def run_checks(checklist, gen_proj, sandbox_root, sources):
    tbl, items, _txt = parse_page(checklist)
    res = []
    c1, l1 = check_C1(tbl, items)
    res.append(("C1 表/JSON 同源 (★id 集合逐个相等★)", c1, l1))
    c2, l2 = check_C2(checklist, gen_proj, sandbox_root)
    res.append(("C2 重跑幂等 (★真页 == 沙盒重跑输出★)", c2, l2))
    c3, l3 = check_C3(items, sources)
    res.append(("C3 来源在册 (★source_iss ∈ 覆盖度闸 SOURCES★)", c3, l3))
    c4, l4 = check_C4(items, tbl)
    res.append(("C4 必需项在场 (★加严块★)", c4, l4))
    ok = all(c for _, c, _ in res)
    return ok, res


def banner():
    print("=" * 98)
    print("  ISS-349 · 「板侧项全集」页【重跑不蒸发】闸 (★C1 表/JSON 同源 · C2 重跑幂等 · "
          "C3 来源在册 · C4 必需项★)")
    print("=" * 98)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true", help="★反向用例 (R1/R2/R3 + 正例)★")
    ap.add_argument("--makesandbox", metavar="DIR", help="★只建沙盒并退出 (给 run 脚本用)★")
    args = ap.parse_args(argv)

    if args.makesandbox:
        make_sandbox(GEN_PROJ, os.path.abspath(args.makesandbox))
        print("★沙盒已建: %s" % os.path.abspath(args.makesandbox))
        return 0

    try:
        sources = read_coverage_sources(COVERAGE_GATE)
    except Exception as e:
        print("★闸崩: %s" % e)
        return 3

    if args.selftest:
        return selftest(sources)

    banner()
    print("  PROJ      = %s" % PROJ)
    print("  CHECKLIST = %s" % CHECKLIST)
    print("  GEN_PROJ  = %s" % GEN_PROJ)
    print("  SANDBOX   = %s" % SANDBOX)
    print("-" * 98)
    ok, res = run_checks(CHECKLIST, GEN_PROJ, SANDBOX, sources)
    for name, c, lines in res:
        print("  %s  %s" % ("OK  " if c else "FAIL", name))
        for l in lines:
            print("    %s" % l)
    print("-" * 98)
    if ok:
        print("  ✅ rc=0: ★★页与生成器同源 · 重跑零差异 · 来源全在册 · 必需项在场 ★★")
        return 0
    print("  ❌ rc=1: ★★闸红 (★上面点名的那几条就是不许过的那几条★) ★★")
    return 1


# ==============================================================================
# ★★反向用例 (★端到端跑真生成器·不许只测纯函数★) ★★
# ==============================================================================
def _page_json_span(txt):
    """★页里 §7 JSON 块的 (起, 止) 下标 (★改 JSON 用★) ★"""
    m = re.search(r"```json\s*(\{.*?\})\s*```", txt, re.S)
    if not m:
        raise RuntimeError("★页里找不到 JSON 块")
    return m.span(1)


def _rewrite_json(txt, fn):
    """★把页里 JSON 块的 items 交给 fn 改一遍 ⇒ 新文本 (★其余部分一字不动★) ★"""
    s, e = _page_json_span(txt)
    data = json.loads(txt[s:e])
    fn(data)
    new = json.dumps(data, ensure_ascii=False, indent=2)
    return txt[:s] + new + txt[e:]


def selftest(sources):
    banner()
    print("  ★反向用例沙盒: %s" % SANDBOX)
    sb = os.path.join(SANDBOX, "selftest")
    make_sandbox(GEN_PROJ, sb)
    gen_src = os.path.join(sb, "state", "_iss277_build_preflight.py")
    page_sb = os.path.join(sb, "HW", "PCB", "BOARD_ONEPASS_PREFLIGHT.md")
    page_real = os.path.join(PROJ, "HW", "PCB", "BOARD_ONEPASS_PREFLIGHT.md")
    cases = []

    def restore():
        shutil.copy2(os.path.join(PROJ, "state", "_iss277_build_preflight.py"), gen_src)
        shutil.copy2(page_real, page_sb)

    def run_generator():
        env = dict(os.environ)
        env["PREFLIGHT_PROJ"] = sb
        env["TMPDIR"] = os.path.join(sb, "tmp")
        p = subprocess.run([sys.executable, "-B", gen_src], cwd=sb, env=env,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=1800)
        return p.returncode, (p.stdout or b"").decode("utf-8", "replace")

    # ★正例 (★闸不是只会在坏情况下红, 也要能在好情况下绿★) ★
    rc, out = run_generator()
    same = rc == 0 and os.path.exists(page_sb) and md5(page_sb) == md5(page_real)
    cases.append(("正例 · 沙盒重跑 == 真页 (★零行差异·零蒸发★)", same,
                  "★生成器 rc=%d · 沙盒页 md5=%s · 真页 md5=%s"
                  % (rc, md5(page_sb) if os.path.exists(page_sb) else "?",
                     md5(page_real))))

    # ★R1 · 生成器里 B33 那条被删掉 ⇒ 重跑 ⇒ 页回到 32 条 ⇒ 闸必须判红并点名「B33 缺失」 ★
    restore()
    lines = open(gen_src, encoding="utf-8").read().split("\n")
    i0 = next(i for i, l in enumerate(lines) if '"B33_PIN_LAND_1P27"' in l)
    i1 = next(i for i in range(i0, len(lines)) if lines[i].rstrip().endswith('"[实测]"),'))
    del lines[i0:i1 + 1]
    open(gen_src, "w", encoding="utf-8").write("\n".join(lines))
    rc, out = run_generator()
    _, items_sb, _ = parse_page(page_sb)
    n_after = len(items_sb) if items_sb else -1
    ok_r1, res = run_checks(page_sb, sb, os.path.join(SANDBOX, "r1"), sources)
    txt_r1 = "\n".join(l for _, _, ls in res for l in ls)
    named = ("B33_PIN_LAND_1P27" in txt_r1) and ("缺失" in txt_r1)
    cases.append(("R1 · 生成器里删掉 B33 ⇒ 重跑 ⇒ 页回到 %d 条 ⇒ 闸红并点名「B33 缺失」"
                  % n_after, (not ok_r1) and named,
                  "★闸 rc 判红=%s · 点名到 B33=%s★\n     %s"
                  % (not ok_r1, named, " / ".join(
                      l.strip() for _, c, ls in res for l in ls if l.strip().startswith("❌"))[:300])))
    restore()

    # ★R2 · 真页 JSON 块里 B33 的 pitch 改成假值 ⇒ 闸必须判红 (★真页 != 重跑输出★) ★
    restore()
    txt = read_text(page_sb)

    def fake_pitch(data):
        for it in data["items"]:
            if it.get("id") == "B33_PIN_LAND_1P27":
                it["current_state"] = it["current_state"].replace("pitch 0.50", "pitch 9.99")
    open(page_sb, "w", encoding="utf-8").write(_rewrite_json(txt, fake_pitch))
    ok_r2, res = run_checks(page_sb, GEN_PROJ, os.path.join(SANDBOX, "r2"), sources)
    c2r = [c for name, c, _ in res if name.startswith("C2")][0]
    txt_r2 = "\n".join(l for _, _, ls in res for l in ls)
    cases.append(("R2 · 真页 JSON 里 B33 的 pitch 改成假值 9.99 ⇒ 闸红 (★真页 != 重跑输出★)",
                  (not ok_r2) and (not c2r),
                  "★闸 rc 判红=%s · C2 判红=%s · 贴了 diff=%s★\n     %s"
                  % (not ok_r2, not c2r, ("diff" in txt_r2),
                     " / ".join(l.strip() for _, c, ls in res for l in ls
                                if l.strip().startswith("❌"))[:300])))
    restore()

    # ★R3 · 真页 JSON 块里某条 item 的 source_iss 改成不在 SOURCES 里的号 ⇒ 闸红并点名该 id ★
    restore()
    txt = read_text(page_sb)

    def bad_source(data):
        for it in data["items"]:
            if it.get("id") == "B33_PIN_LAND_1P27":
                it["source_iss"] = "ISS-999"
    open(page_sb, "w", encoding="utf-8").write(_rewrite_json(txt, bad_source))
    ok_r3, res = run_checks(page_sb, GEN_PROJ, os.path.join(SANDBOX, "r3"), sources)
    c3r = [c for name, c, _ in res if name.startswith("C3")][0]
    txt_r3 = "\n".join(l for _, _, ls in res for l in ls)
    named3 = ("B33_PIN_LAND_1P27" in txt_r3) and ("ISS-999" in txt_r3)
    cases.append(("R3 · 真页 JSON 里 B33 的 source_iss 改成 ISS-999 (不在 SOURCES) ⇒ 闸红并点名",
                  (not ok_r3) and (not c3r) and named3,
                  "★闸 rc 判红=%s · C3 判红=%s · 点名到 B33+ISS-999=%s★\n     %s"
                  % (not ok_r3, not c3r, named3,
                     " / ".join(l.strip() for _, c, ls in res for l in ls
                                if l.strip().startswith("❌"))[:300])))
    restore()

    # ★R4 · 沙盒里把【板读结果】改成 1.27 ⇒ 重跑 ⇒ 页里的现状值【自己】跟着变 (★不是死值★) ★
    #   ★这是生成器铁律①的机器证明: 板那一趟改完 land, 重跑生成器 ⇒ 这一条的现状值自己变 1.27 ★
    board_sb = os.path.join(sb, "HW", "PCB", "demo_mainboard.kicad_pcb")
    board_real = os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb")
    shutil.copy2(board_real, board_sb)
    edit_code = "\n".join([
        "import pcbnew",
        "p = 'HW/PCB/demo_mainboard.kicad_pcb'",
        "b = pcbnew.LoadBoard(p)",
        "for r in ('J_DEBUG', 'J_UART'):",
        "    fp = [f for f in b.GetFootprints() if f.GetReference() == r][0]",
        "    pads = sorted(fp.Pads(), key=lambda q: q.GetPosition().x)",
        "    x0 = pads[0].GetPosition().x",
        "    step = pcbnew.FromMM(1.27)",
        "    for i, q in enumerate(pads):",
        "        pos = q.GetPosition(); pos.x = int(x0 + i * step); q.SetPosition(pos)",
        "pcbnew.SaveBoard(p, b)",
    ])
    pe = subprocess.run(["bash", "state/pcbnew_py.sh", "-c", edit_code], cwd=sb,
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=900)
    rc, out = run_generator()
    _, items_r4, _ = parse_page(page_sb)
    b33 = [i for i in (items_r4 or []) if i.get("id") == "B33_PIN_LAND_1P27"]
    cs = b33[0].get("current_state", "") if b33 else ""
    followed = ("pitch 1.27" in cs) and ("Δ pitch 0.00" in cs) and ("pitch 0.50 /" not in cs)
    cases.append(("R4 · 沙盒里把板读结果改成 1.27 ⇒ 重跑 ⇒ 页里的现状值【自己】变成 1.27 (★不是死值★)",
                  (pe.returncode == 0) and (rc == 0) and followed,
                  "★改板 rc=%d · 生成器 rc=%d · 板读 1.27 ⇒ 页里跟上了=%s★\n     %s"
                  % (pe.returncode, rc, followed, cs[:260])))
    shutil.copy2(board_real, board_sb)
    restore()

    # ★恢复原件后再跑一次 ⇒ 必须绿 (★闸不是永远红的★) ★
    rc, out = run_generator()
    ok_after, res = run_checks(page_sb, sb, os.path.join(SANDBOX, "after"), sources)
    cases.append(("恢复原件后 · 再跑一次 ⇒ 闸绿 (★不是永远红的闸★)", ok_after,
                  "★生成器 rc=%d · 闸全绿=%s★" % (rc, ok_after)))

    print("-" * 98)
    print("  ★反向用例 (★端到端跑真生成器★):")
    allok = True
    for name, ok, note in cases:
        allok = allok and ok
        print("  %s  %s" % ("PASS" if ok else "FAIL", name))
        for l in str(note).split("\n"):
            print("      %s" % l)
    print("-" * 98)
    if allok:
        print("  ALL TESTS PASS")
        return 0
    print("  ★自测不过 (★不许进交卷★)")
    return 1


if __name__ == "__main__":
    sys.exit(main())
