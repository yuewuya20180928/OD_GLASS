#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-281 · S10 投产包 md5 清单 (MANIFEST.md5) 机器闸
=================================================================================================
派活: 项目总工 (main / moli) 2026-11-17 09:0x (job cron 775d9893)

★**本闸守的是「投产包有没有一份【自证文件】说清『这一包是这一版板出的』」** ⇒ ★**零写板 · 零落表 · 零改网表/脚表/BOM** ★
★**不执行 S1~S13 任何一步 (★尤其【不许跑 `state/gen_production_pack.sh`】—— 那是 `rm -rf "$OUT"` 后重建★) ★**

★**它补的是哪个洞 (★main 08:5x 实查★)**:
  · `state/chain_gate.py` (S11)            ⇒ 判「产物不比板新」(★mtime 口径★) ⇒ ★**判不了「产物是不是这一版板出的」** ★
  · `HW/check_onepass_commit_order.py` (ISS-280 · D5/D6) ⇒ 判「板 md5 变了几次」+「改了必须留证绑定」★
    ⇒ ★**D6 要的就是「产物绑定到哪一版板」, 而盘上【没有一个文件能声明这件事】** ★
  · `HW/PCB/production/doc/board-stats.txt` ⇒ ★**KiCad 统计报告, `grep -ci md5` = 0 ⇒ 作业包 §3-S10 说的
    「板统计里的 md5」这个字段【盘上不存在】⇒ S10 的量化判据落不了地** ★
⇒ ★**本闸就是那一份「盘上不存在的字段」的替身: 投产包清单 `HW/PCB/production/MANIFEST.md5`** ★

★**格式契约 (★权威 = HW/PCB/BOARD_ONEPASS_S10_MANIFEST_SPEC.md★)**:
  · 数据行: `<相对路径> | <md5 32hex> | <字节数>` (★相对 `HW/PCB/production/`★)
  · 末尾三行: `BOARD_MD5 | <md5> | -` / `GENERATED_AT | <ISO8601> | -` / `FILE_COUNT | <n> | -`
  · ★`FILE_COUNT` = 投产包内文件总数 (★含清单自身★) = 数据行数 + 1★

四条判据 (★★全是【内容级】, 不是 mtime★★):
  M1  清单在盘 + 三个头字段齐全 + 每个数据行 md5/字节数格式合法 + 路径合法
  M2  清单里的 BOARD_MD5 == 盘上板 md5        ⇒ ★**产物不是这一版板出的** ★
  M3  清单里列的每个文件, 盘上 md5 与清单逐字相同 ⇒ ★**产物被偷换/被改/缺件** ★
  M4  清单文件数 == 盘上实际文件数, 且路径集合双向相等 ⇒ ★**有文件偷渡出清单** ★

★★**本闸【不生成】清单 (★生成器归 S10 那一趟 = `state/gen_production_pack.sh`★)**
   ⇒ 本文件里那个 `build_manifest()` 只在【沙盒/自测/演示】里用, 绝不写真盘★★

退出码: 0 = 全过 · 1 = 有不通过项 · 2 = 用法错
用法:
  python3 HW/check_onepass_s10_manifest.py             # 主模式 (★只读★)
  python3 HW/check_onepass_s10_manifest.py --selftest   # 反向用例 (★端到端跑真盘沙盒副本★)
  python3 HW/check_onepass_s10_manifest.py --demo-sandbox  # ★沙盒里造一份合规清单 ⇒ 证明闸不是恒红★
  ★自检用 env 覆盖★: ONEPASS_PRODUCTION / ONEPASS_S10_MANIFEST / ONEPASS_PCB + --root
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)

# ★默认相对路径 (★相对 --root★)
REL = {
    "production": "HW/PCB/production",
    "manifest":   "HW/PCB/production/MANIFEST.md5",
    "pcb":        "HW/PCB/demo_mainboard.kicad_pcb",
    "spec":       "HW/PCB/BOARD_ONEPASS_S10_MANIFEST_SPEC.md",
}

# ★env 覆盖 (★--selftest / --demo-sandbox 用它把闸指向沙盒副本★)
ENV = {
    "production": "ONEPASS_PRODUCTION",
    "manifest":   "ONEPASS_S10_MANIFEST",
    "pcb":        "ONEPASS_PCB",
    "spec":       "ONEPASS_S10_MANIFEST_SPEC",
}

HEAD_KEYS = ("BOARD_MD5", "GENERATED_AT", "FILE_COUNT")

HEX32 = re.compile(r"^[0-9a-f]{32}$")
ISO8601 = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:[+-]\d{2}:\d{2}|Z)$")
CN_TZ = timezone(timedelta(hours=8))


# ── 小工具 ────────────────────────────────────────────────────────────────
def md5_of(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def resolve(root: str, key: str, override: str | None) -> str:
    """★相对路径一律相对 --root; env/CLI 给的绝对路径直接用★"""
    if override:
        return os.path.abspath(override)
    env_val = os.environ.get(ENV[key])
    if env_val:
        return env_val if os.path.isabs(env_val) else os.path.join(root, env_val)
    return os.path.join(root, REL[key])


def prod_files(prod_dir: str) -> list[str]:
    """★投产包内全部普通文件的相对路径 (★相对 prod_dir★, 排序) ★"""
    out: list[str] = []
    if not os.path.isdir(prod_dir):
        return out
    for dirpath, dirnames, filenames in os.walk(prod_dir):
        dirnames.sort()
        for fn in filenames:
            full = os.path.join(dirpath, fn)
            if os.path.isfile(full) and not os.path.islink(full):
                out.append(os.path.relpath(full, prod_dir))
    out.sort()
    return out


# ── 清单解析 (★严格按格式契约★) ──────────────────────────────────────────
def parse_manifest(text: str):
    """★返回 (rows, heads, errors)★
       rows  = [{path, md5, size}, ...]  (数据行)
       heads = {BOARD_MD5:..., GENERATED_AT:..., FILE_COUNT:...}
       errors= [格式错误描述, ...]"""
    errors: list[str] = []
    rows: list[dict] = []
    heads: dict[str, str] = {}
    seen_paths: set[str] = set()
    seen_head = False
    head_order: list[str] = []
    n = 0

    for raw in text.splitlines():
        n += 1
        line = raw.rstrip("\r")
        s = line.strip()
        if not s or s.startswith("#"):
            continue                                   # ★注释行/空行: 整行跳过★
        if line.count("|") != 2:
            errors.append("第 %d 行字段数不对 (★要 3 段 = 2 个竖线★): %r" % (n, s[:120]))
            continue
        f0, f1, f2 = (x.strip() for x in line.split("|"))

        if f0 in HEAD_KEYS:                             # ★头字段行★
            seen_head = True
            if f0 in heads:
                errors.append("头字段 %s 重复出现 (★各只许一次★)" % f0)
            else:
                idx = len(head_order)
                if idx < len(HEAD_KEYS) and HEAD_KEYS[idx] != f0:
                    errors.append("第 %d 行: 头字段顺序错 (★末尾三行须依次为 %s★)"
                                  % (n, " / ".join(HEAD_KEYS)))
                head_order.append(f0)
                heads[f0] = f1
            if f2 != "-":
                errors.append("第 %d 行: 头字段 %s 的第 3 段应为 '-' (★实为 %r★)" % (n, f0, f2))
            continue

        if seen_head:
            errors.append("第 %d 行: 数据行出现在头字段之后 (★头字段必须在末尾三行★)" % n)

        # ── 数据行校验 (★M1 的格式层★) ──
        if not f0:
            errors.append("第 %d 行: 路径为空" % n)
        elif f0.startswith("/"):
            errors.append("第 %d 行: 路径必须相对 (★不许以 '/' 开头★): %r" % (n, f0))
        elif ".." in f0.split("/"):
            errors.append("第 %d 行: 路径不许含 '..' (★防越界★): %r" % (n, f0))
        elif f0 in seen_paths:
            errors.append("第 %d 行: 路径重复: %r" % (n, f0))
        else:
            seen_paths.add(f0)
        if not HEX32.match(f1):
            errors.append("第 %d 行: md5 不是 32 位小写 hex: %r" % (n, f1))
        if not f2.isdigit():
            errors.append("第 %d 行: 字节数不是非负整数: %r" % (n, f2))
        rows.append({"path": f0, "md5": f1, "size": int(f2) if f2.isdigit() else -1})

    return rows, heads, errors


# ── 判据 (★ok = True 过 / False 红 / None 不可判定★) ─────────────────────
def judge_m1(paths: dict, rows: list, heads: dict, errors: list):
    """★M1: 清单在盘 + 头字段齐全 + 数据行格式合法 + 路径合法 + 清单在投产包内★"""
    msgs: list[str] = []
    ok = True

    man = paths["manifest"]
    prod = paths["production"]

    if not os.path.isdir(prod):
        return False, "找不到投产包目录 %s" % prod
    if not os.path.isfile(man):
        return False, ("★清单文件不在盘上: %s★ ⇒ ★**S10 那一趟还没生成清单 (★这正是 ISS-281 的病灶本身★)** ★" % man)

    # ★清单必须在投产包内 (★契约 §1: 放外面 = 描述旧包的僵尸清单★) ★
    man_abs = os.path.abspath(man)
    prod_abs = os.path.abspath(prod)
    if not (man_abs == prod_abs or man_abs.startswith(prod_abs + os.sep)):
        ok = False
        msgs.append("★清单不在投产包内 (%s 不在 %s 下) ⇒ 违反契约 §1 (★放外面会被 `rm -rf` 后的旧内容冒充★)" % (man, prod))

    if errors:
        ok = False
        msgs.append("清单格式错误 %d 处: %s" % (len(errors), "; ".join(errors[:5])))

    missing = [k for k in HEAD_KEYS if k not in heads]
    if missing:
        ok = False
        msgs.append("缺头字段: %s (★三个头字段各只许一次★)" % ", ".join(missing))
    else:
        msgs.append("三个头字段齐全 (BOARD_MD5 / GENERATED_AT / FILE_COUNT)")

    if "GENERATED_AT" in heads and not ISO8601.match(heads["GENERATED_AT"]):
        ok = False
        msgs.append("GENERATED_AT 不是 ISO8601 (★要带时区偏移★): %r" % heads["GENERATED_AT"])
    if "FILE_COUNT" in heads and not heads["FILE_COUNT"].isdigit():
        ok = False
        msgs.append("FILE_COUNT 不是整数: %r" % heads["FILE_COUNT"])

    if rows:
        msgs.append("数据行 %d 行 (★每行都有 md5 + 字节数★)" % len(rows))
    else:
        ok = False
        msgs.append("清单里一个数据行都没有")

    return (True if ok else False), " · ".join(msgs)


def judge_m2(paths: dict, heads: dict):
    """★M2: 清单里的 BOARD_MD5 == 盘上板 md5 ⇒ 「产物不是这一版板出的」★"""
    if "BOARD_MD5" not in heads:
        return None, "清单里没有 BOARD_MD5 ⇒ 不可判定 (★依赖 M1★)"
    pcb = paths["pcb"]
    if not os.path.isfile(pcb):
        return False, "找不到板文件 %s" % pcb
    cur = md5_of(pcb)
    rec = heads["BOARD_MD5"]
    if cur == rec:
        return True, "清单 BOARD_MD5 %s == 盘上板 md5 ⇒ 这一包确实是【这一版板】出的" % cur
    return False, ("★清单 BOARD_MD5 = %s ≠ 盘上板 md5 = %s ⇒ 这一包【不是这一版板】出的 (★旧货冒充新货★)" % (rec, cur))


def judge_m3(paths: dict, rows: list):
    """★M3: 清单里列的每个文件, 盘上 md5 与清单逐字相同 ⇒ 「产物被偷换」★"""
    prod = paths["production"]
    bad: list[str] = []
    checked = 0
    for r in rows:
        full = os.path.join(prod, r["path"])
        if not os.path.isfile(full):
            bad.append("%s (★清单列了但盘上没有★)" % r["path"])
            continue
        cur = md5_of(full)
        if cur != r["md5"]:
            bad.append("%s (★盘上 md5 %s ≠ 清单 %s★)" % (r["path"], cur, r["md5"]))
            continue
        size = os.path.getsize(full)
        if r["size"] >= 0 and size != r["size"]:
            bad.append("%s (★盘上 %d B ≠ 清单 %d B★)" % (r["path"], size, r["size"]))
            continue
        checked += 1
    if bad:
        return False, ("清单列的 %d 个文件里 %d 个对不上: %s" % (len(rows), len(bad), "; ".join(bad[:5])))
    return True, "清单列的 %d 个文件 md5 与字节数逐字相同 ⇒ 投产包一个字节没被动过" % checked


def judge_m4(paths: dict, rows: list, heads: dict):
    """★M4: 文件数 == 盘上实际文件数 + 路径集合双向相等 ⇒ 「有文件偷渡出清单」★"""
    prod = paths["production"]
    man_abs = os.path.abspath(paths["manifest"])
    on_disk = prod_files(prod)
    total = len(on_disk)                              # ★含清单自身 (★清单在包内时它就是一个文件★) ★
    listed = [r["path"] for r in rows]

    msgs: list[str] = []
    ok = True
    evaluable = True

    if "FILE_COUNT" not in heads:
        evaluable = False
        ok = False
        msgs.append("清单里没有 FILE_COUNT ⇒ 无法判文件数 (★不可判定★)")
    else:
        fc = int(heads["FILE_COUNT"]) if heads["FILE_COUNT"].isdigit() else -1
        if fc != total:
            ok = False
            msgs.append("★FILE_COUNT = %d ≠ 盘上实际文件数 = %d (★`find HW/PCB/production -type f | wc -l`★)" % (fc, total))
        else:
            msgs.append("FILE_COUNT = %d == 盘上实际文件数 %d (★含清单自身★)" % (fc, total))

    # ★集合双向相等 (★清单自身不在数据行里 ⇒ 从盘面集合里剔掉★) ★
    disk_set = set(on_disk)
    man_rel = os.path.relpath(man_abs, os.path.abspath(prod))
    if not man_rel.startswith(".."):
        disk_set.discard(man_rel)
    list_set = set(listed)
    missing = sorted(disk_set - list_set)             # ★盘上有、清单没列 ⇒ 偷渡件★ ★
    ghost = sorted(list_set - disk_set)               # ★清单列了、盘上没有 ⇒ 幽灵★ ★
    if missing:
        ok = False
        msgs.append("★盘上有 %d 个文件没进清单 (★偷渡件★): %s" % (len(missing), ", ".join(missing[:5])))
    if ghost:
        ok = False
        msgs.append("★清单列了 %d 个盘上不存在的文件 (★幽灵★): %s" % (len(ghost), ", ".join(ghost[:5])))
    if not missing and not ghost:
        msgs.append("清单路径集合 == 盘面文件集合 (双向相等, 无偷渡件)")

    if len(set(listed)) != len(listed):
        ok = False
        msgs.append("清单里有重复路径")

    if not evaluable:
        return None, " · ".join(msgs)
    return (True if ok else False), " · ".join(msgs)


def evaluate(root: str, paths: dict):
    """★返回 [(判据号, 通过?(True/False/None), 说明), ...]★"""
    prod = paths["production"]
    man = paths["manifest"]

    if not os.path.isdir(prod):
        return [(k, False, "找不到投产包目录 %s" % prod) for k in ("M1", "M2", "M3", "M4")]

    if not os.path.isfile(man):
        return [("M1", False,
                 "★清单文件不在盘上: %s★ ⇒ ★**S10 那一趟还没生成清单 (★这正是 ISS-281 的病灶本身★)** ★" % man),
                ("M2", None, "不可判定 (★依赖 M1: 清单不在盘上★)"),
                ("M3", None, "不可判定 (★依赖 M1: 清单不在盘上★)"),
                ("M4", None, "不可判定 (★依赖 M1: 清单不在盘上★)")]

    rows, heads, errors = parse_manifest(read_text(man))
    res = []
    res.append(("M1",) + judge_m1(paths, rows, heads, errors))
    res.append(("M2",) + judge_m2(paths, heads))
    res.append(("M3",) + judge_m3(paths, rows))
    res.append(("M4",) + judge_m4(paths, rows, heads))
    return res


def report(results, title="主模式"):
    print("=" * 78)
    print("  ISS-281 · S10 投产包 md5 清单 (MANIFEST.md5) 机器闸  (★%s★)" % title)
    print("=" * 78)
    bad = 0
    for code, ok, msg in results:
        if ok is None:
            mark = "⏭ "
        elif ok:
            mark = "✅"
        else:
            mark = "❌"
            bad += 1
        print("  %s %-4s %s" % (mark, code, msg))
    print("-" * 78)
    if bad:
        print("  ❌ %d 项不通过" % bad)
    else:
        print("  ✅ 全部通过")
    return bad


# ── 沙盒用的清单生成器 (★★仅供沙盒/自测/演示★★ 真盘生成器归 S10 那一趟★) ──
def build_manifest(prod_dir: str, board_path: str, out_path: str,
                   generated_at: str | None = None) -> str:
    """★按 ISS-281 格式契约造一份清单 (★只往 out_path 写★) ★"""
    if generated_at is None:
        generated_at = datetime.now(CN_TZ).replace(microsecond=0).isoformat()
    out_rel = os.path.relpath(os.path.abspath(out_path), os.path.abspath(prod_dir))
    files = [f for f in prod_files(prod_dir) if f != out_rel]

    lines = [
        "# ARS45 · S10 投产包 md5 清单",
        "# ★格式契约: HW/PCB/BOARD_ONEPASS_S10_MANIFEST_SPEC.md (ISS-281) ★",
        "# ★生成器: state/gen_production_pack.sh (★rm -rf 重建【之后】写★) ★",
        "# ★板源: HW/PCB/demo_mainboard.kicad_pcb ★",
        "# ★数据行: <相对路径> | <md5 32hex> | <字节数> ★",
    ]
    for rel in files:
        full = os.path.join(prod_dir, rel)
        lines.append("%s | %s | %d" % (rel, md5_of(full), os.path.getsize(full)))
    lines.append("BOARD_MD5 | %s | -" % md5_of(board_path))
    lines.append("GENERATED_AT | %s | -" % generated_at)
    lines.append("FILE_COUNT | %d | -" % (len(files) + 1))     # ★+1 = 清单自身★

    d = os.path.dirname(os.path.abspath(out_path))
    if d:
        os.makedirs(d, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return out_path


# ── 沙盒构造 (★真盘原件一个字节不动★) ───────────────────────────────────
def make_sandbox(src_root: str, dst_root: str, copy_pack: bool = True):
    """★把真盘的投产包 + 板复制成沙盒副本★"""
    os.makedirs(dst_root, exist_ok=True)
    src_prod = os.path.join(src_root, REL["production"])
    dst_prod = os.path.join(dst_root, REL["production"])
    if copy_pack and os.path.isdir(src_prod):
        shutil.copytree(src_prod, dst_prod)
    src_pcb = os.path.join(src_root, REL["pcb"])
    dst_pcb = os.path.join(dst_root, REL["pcb"])
    os.makedirs(os.path.dirname(dst_pcb), exist_ok=True)
    shutil.copy2(src_pcb, dst_pcb)
    return {
        "__root__":    dst_root,
        "production": dst_prod,
        "manifest":   os.path.join(dst_prod, os.path.basename(REL["manifest"])),
        "pcb":        dst_pcb,
        "spec":       os.path.join(dst_root, REL["spec"]),
    }


def run_gate(root: str):
    """★真跑本闸 (子进程) ⇒ (rc, 输出) ★"""
    env = {k: v for k, v in os.environ.items() if k not in ENV.values()}
    cmd = [sys.executable, os.path.abspath(__file__), "--root", root]
    p = subprocess.run(cmd, capture_output=True, text=True, env=env)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def _flip_one_char(s: str) -> str:
    """★把 32 位 hex 的第一位改掉 (★改错一位★) ★"""
    if not s:
        return "0" * 32
    return ("0" if s[0] != "0" else "1") + s[1:]


# ── --selftest (★端到端跑真盘沙盒副本★) ───────────────────────────────────
def selftest(root: str, verbose: bool = True):
    cases: list[tuple] = []
    tmp_root = tempfile.mkdtemp(prefix="iss281_sandbox_")
    tpl = os.path.join(tmp_root, "_template")
    ok_all = True

    try:
        make_sandbox(root, tpl)

        def fresh(name: str) -> dict:
            """★每个用例一份全新沙盒副本 (★从模板拷★) ★"""
            d = os.path.join(tmp_root, name)
            shutil.rmtree(d, ignore_errors=True)
            return make_sandbox(tpl, d, copy_pack=True)

        def expect(sb: dict, want_red: list[str], label: str):
            """★跑闸并核对: 期望红的判据必须红, 其余必须绿/不可判定★"""
            nonlocal ok_all
            rc, out = run_gate(sb["__root__"])
            red = set()
            for line in out.splitlines():
                s = line.strip()
                if s.startswith("❌"):
                    m = re.match(r"❌\s+(M\d)\b", s)
                    if m:
                        red.add(m.group(1))
            bad = []
            for c in want_red:
                if c not in red:
                    bad.append("期望 %s 红但它绿了" % c)
            for c in ("M1", "M2", "M3", "M4"):
                if c not in want_red and c in red:
                    bad.append("期望 %s 绿但它红了" % c)
            good = (not bad) and ((rc == 1) if want_red else (rc == 0))
            if not good:
                ok_all = False
            cases.append((label, rc, sorted(red), good))
            if verbose:
                mark = "✅" if good else "❌"
                print("  %s %-44s rc=%d  红判据=%s%s"
                      % (mark, label, rc, (",".join(sorted(red)) or "无"),
                         ("  ★%s★" % "; ".join(bad)) if bad else ""))
            if not good and verbose:
                print("      ---- 闸输出 ----")
                for ln in out.splitlines():
                    print("      " + ln)
            return rc, out

        # ── ⑥ 正向对照: 清单与盘面完全一致 ⇒ rc=0 (★证明 M1~M4 不是恒红★) ──
        sb = fresh("c6_ok")
        build_manifest(sb["production"], sb["pcb"], sb["manifest"])
        expect(sb, [], "⑥ 正向对照 (清单与盘面完全一致)")

        # ── ① 清单里板 md5 改错一位 ⇒ M2 红 ──
        sb = fresh("c1_boardmd5")
        build_manifest(sb["production"], sb["pcb"], sb["manifest"])
        t = read_text(sb["manifest"])
        t = re.sub(r"^BOARD_MD5 \| [0-9a-f]{32} \| -$",
                   "BOARD_MD5 | %s | -" % _flip_one_char(md5_of(sb["pcb"])), t, flags=re.M)
        with open(sb["manifest"], "w", encoding="utf-8") as f:
            f.write(t)
        expect(sb, ["M2"], "① 清单里板 md5 改错一位")

        # ── ② 清单里某个文件的 md5 改错一位 ⇒ M3 红 ──
        sb = fresh("c2_filemd5")
        build_manifest(sb["production"], sb["pcb"], sb["manifest"])
        lines = read_text(sb["manifest"]).splitlines()
        for i, ln in enumerate(lines):
            if "|" in ln and not ln.startswith("#") and not ln.startswith(("BOARD_MD5", "GENERATED_AT", "FILE_COUNT")):
                parts = ln.split("|")
                parts[1] = " " + _flip_one_char(parts[1].strip())
                lines[i] = "|".join(parts)
                break
        with open(sb["manifest"], "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        expect(sb, ["M3"], "② 清单里某个文件的 md5 改错一位")

        # ── ③ 从投产包里删一个文件 ⇒ M3/M4 红 ──
        sb = fresh("c3_del")
        build_manifest(sb["production"], sb["pcb"], sb["manifest"])
        os.remove(os.path.join(sb["production"], "gerbers", "demo_mainboard-F_Cu.gtl"))
        expect(sb, ["M3", "M4"], "③ 从投产包里删一个文件")

        # ── ④ 往投产包里加一个清单没列的文件 ⇒ M4 红 ──
        sb = fresh("c4_add")
        build_manifest(sb["production"], sb["pcb"], sb["manifest"])
        with open(os.path.join(sb["production"], "gerbers", "smuggled.gbr"), "w") as f:
            f.write("G04 偷渡件*\n")
        expect(sb, ["M4"], "④ 往投产包里加一个清单没列的文件")

        # ── ⑤ 清单少一个头字段 ⇒ M1 红 (★三个头字段各测一次★) ──
        for miss in HEAD_KEYS:
            sb = fresh("c5_missing_%s" % miss)
            build_manifest(sb["production"], sb["pcb"], sb["manifest"])
            lines = [ln for ln in read_text(sb["manifest"]).splitlines()
                     if not ln.startswith(miss + " |")]
            with open(sb["manifest"], "w", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")
            expect(sb, ["M1"], "⑤ 清单少头字段 %s" % miss)

        # ── ⑦ 历史对照: 用 ISS-280 之前的盘面 (★今天这个没有清单的投产包★) ⇒ M1 红 ──
        sb = fresh("c7_hist")
        if os.path.exists(sb["manifest"]):
            os.remove(sb["manifest"])               # ★沙盒里也不放清单 = 复现「今天的盘面」★
        expect(sb, ["M1"], "⑦ 历史对照 (盘上没有清单)")

        # ── ⑧ 追加: 板在清单生成之后又改了 ⇒ M2 红 (★「旧货冒充新货」核心场景★) ──
        sb = fresh("c8_boardchanged")
        build_manifest(sb["production"], sb["pcb"], sb["manifest"])
        with open(sb["pcb"], "ab") as f:
            f.write("\n# 板在清单生成之后又被人改了一笔\n".encode("utf-8"))
        expect(sb, ["M2"], "⑧ 板在清单生成之后又改了 (旧货冒充新货)")

    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)

    n_red = len([c for c in cases if c[3] and c[2]])
    print("-" * 78)
    print("  用例 %d 条 (★判红 %d 条 + 正向对照 1 条★) · 沙盒根 (★已清理★): %s" % (len(cases), n_red, tmp_root))
    if ok_all:
        print("  ✅ selftest 全过")
        return 0
    print("  ❌ selftest 有用例没过")
    return 1


# ── --demo-sandbox (★证明闸不是恒红★) ─────────────────────────────────────
def demo_sandbox(root: str):
    tmp_root = tempfile.mkdtemp(prefix="iss281_sandbox_")
    try:
        sb = make_sandbox(root, tmp_root, copy_pack=True)
        build_manifest(sb["production"], sb["pcb"], sb["manifest"])
        paths = {
            "production": os.path.join(tmp_root, REL["production"]),
            "manifest":   os.path.join(tmp_root, REL["manifest"]),
            "pcb":        os.path.join(tmp_root, REL["pcb"]),
            "spec":       os.path.join(tmp_root, REL["spec"]),
        }
        print("★沙盒路径 (★真盘一个字节没动★): %s" % tmp_root)
        print("★沙盒清单: %s" % paths["manifest"])
        results = evaluate(tmp_root, paths)
        bad = report(results, "沙盒演示模式")
        return 1 if bad else 0
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)


# ── main ──────────────────────────────────────────────────────────────────
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="ISS-281 · S10 投产包 md5 清单机器闸")
    ap.add_argument("--root", default=PROJ, help="★相对路径的根 (★默认 = 仓库根★)")
    ap.add_argument("--production", default=None, help="投产包目录 (★相对 --root★)")
    ap.add_argument("--manifest", default=None, help="清单文件 (★相对 --root★)")
    ap.add_argument("--pcb", default=None, help="板文件 (★相对 --root★)")
    ap.add_argument("--selftest", action="store_true", help="★反向用例 (★沙盒副本★) ★")
    ap.add_argument("--demo-sandbox", action="store_true",
                    help="★沙盒里造一份合规清单并判 ⇒ 证明闸不是恒红★")
    args = ap.parse_args(argv)

    root = os.path.abspath(args.root)
    paths = {
        "production": resolve(root, "production", args.production),
        "manifest":   resolve(root, "manifest", args.manifest),
        "pcb":        resolve(root, "pcb", args.pcb),
        "spec":       resolve(root, "spec", None),
    }

    if args.selftest:
        return selftest(root)

    if args.demo_sandbox:
        return demo_sandbox(root)

    # ★信息行 (★不参与判定★): 规格页在不在 ★
    if os.path.isfile(paths["spec"]):
        print("  ℹ 规格页在盘: %s" % paths["spec"])
    else:
        print("  ℹ 规格页不在盘 (★不影响判定★): %s" % paths["spec"])

    results = evaluate(root, paths)
    bad = report(results, "主模式")
    if bad:
        print("  ⇒ ★**当前盘面就是 ISS-281 的病灶本身: 投产包没有自证清单 ⇒ S10 无判可依** ★")
        print("  ⇒ ★**S10 那一趟 (`state/gen_production_pack.sh`) 按作业包 §3-S10 追加块生成了 MANIFEST.md5 之后, 本闸才会转绿** ★")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
