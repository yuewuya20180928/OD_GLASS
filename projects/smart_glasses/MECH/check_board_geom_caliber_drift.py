#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MECH/check_board_geom_caliber_drift.py —— 结构侧口径漂移只读检测闸 (ISS-342)

★**性质**: 只读检测闸 · ★**零写任何文件 / 零改任何既有脚本 / 零碰板 / 零碰网表 / 零落表** ★
★**派活**: 项目总工 (main / moli) · ISS-342 · 2026-11-22 · 交卷人 = 结构总工 (mech-lead) ★
★**关联**: `MECH/BOARD_GEOM_CALIBER_STATUS.md` (漂移清单页) · `MECH/BOARD_GEOM_30MM.md` (表头追加式订正) ★

────────────────────────────────────────────────────────────────────────
【作用】
  扫 MECH 域 (跳过 `.bak` / `__pycache__` / `.git` / `*.pyc`) 里**仍然把
  `RK3576` / `60×30` / `PCB_W=15.00` / 旧板宽 12mm·15mm 当成【现行口径】** 出现的行
  ⇒ 输出 `文件:行号 + 原文 + 漂移类型`。

  ★**不是无脑 grep**: 一行同时满足 ①命中【过期口径词】(stale) ②命中【现行口径词】(current)
  ③【不含】任何【已声明历史/已作废/不可混用】标记 (historical) 才算漂移。
  ⇒ 纯历史留档行 (例: "与 BOARD_GEOM_30MM.md 的 RK3576 老基线 —— 只引用, 一个字不改")
  **不报** —— 反向用例 §--selftest 用例 ② 证明这一点。

────────────────────────────────────────────────────────────────────────
【rc 语义】
  0 = 未发现未声明的漂移 (所有命中都在白名单段内)
  2 = 有漂移 (白名单段之外的命中, 逐条列出)
  1 = 运行错误 (IO / 参数错误 / 内部异常)

────────────────────────────────────────────────────────────────────────
【白名单机制】
  · 白名单 = **按文件 + 行段**, **不许整文件豁免**。
  · 默认白名单 = `MECH/BOARD_GEOM_30MM.md` 里 ISS-342 追加的「本表口径状态」声明段
    (★行段由标记行自动定位, 不是写死的行号, 也不是整文件★)
  · 命令行可追加 / 覆盖:
      --whitelist "MECH/FOO.md:10-20"        (可重复)
      --whitelist "MECH/FOO.md:10-20,30-40"  (同一文件多段)
      --whitelist-file <PATH>                (文件里一行一个 spec, # 开头为注释)
  · ★**白名单只允许掉【已声明】的那一段; 其余命中一律要报** ★

【用法】
  python3 MECH/check_board_geom_caliber_drift.py                 # 裸跑 (扫 MECH/)
  python3 MECH/check_board_geom_caliber_drift.py --root MECH      # 指定域
  python3 MECH/check_board_geom_caliber_drift.py --json           # 机器可读
  python3 MECH/check_board_geom_caliber_drift.py --selftest       # ≥3 条自检 (末行 ALL TESTS PASS)
"""

import argparse
import json
import os
import re
import sys

# ─────────────────────────────────────────────────────────────────────
# 常量
# ─────────────────────────────────────────────────────────────────────

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
DEFAULT_ROOT = "MECH"

# ★ISS-342 追加声明段的定位标记 (行段自动定位, 不写死行号) ★
ISS342_BLOCK_FILE = "MECH/BOARD_GEOM_30MM.md"
ISS342_BLOCK_MARKER = "本表口径状态"
ISS342_BLOCK_TAG = "ISS-342"

SKIP_DIR_NAMES = ("__pycache__", ".git", ".svn", ".hg")
SKIP_EXT = (".pyc", ".pyo", ".o", ".so")

# ─────────────────────────────────────────────────────────────────────
# 规则表
# ─────────────────────────────────────────────────────────────────────

# ①【过期口径词】stale —— 命中即说明这行提到了一套【已经不是现役】的口径
STALE_RULES = (
    ("②绑RK3576", re.compile(r"RK3576")),
    ("③绑60×30", re.compile(r"60\s*[×xX]\s*30")),
    ("④绑旧板宽15", re.compile(r"60\s*[×xX]\s*15")),
    ("④绑旧板宽12/15", re.compile(r"PCB_W\s*=\s*1[25](?:\.0+)?(?![0-9.])")),
    ("④绑旧板宽12/15", re.compile(r"pcb_w\"?\s*[:=]\s*1[25](?:\.0+)?(?![0-9.])")),
    ("④绑旧板宽12/15", re.compile(r"板宽\s*1[25](?:\.0+)?\s*mm")),
)

# 同行的「板宽 30 … 板长 60」也是 60×30 口径 (板框写法不总是 60×30 连写)
COMPOUND_60x30 = re.compile(r"板宽\s*30(?:\.0+)?\s*mm?[^一-鿿\n]{0,20}板长\s*60(?:\.0+)?")

# ②【现行口径词】current —— 这行把上面那套东西说成是「现在在用的」
CURRENT_MARKERS = (
    "现行", "现役", "当前", "权威", "唯一", "默认", "基线",
    "最新", "现状", "在用", "正在用", "唯一权威",
)

# ③【已声明历史 / 作废 / 不可混用】historical —— 命中则这行【已经声明过自己过期】, 不算漂移
HISTORICAL_MARKERS = (
    "历史", "作废", "老口径", "老基线", "留档", "已迁", "已废弃", "已废弃",
    "不是现行", "不是现役", "过期", "标作历史", "口径状态", "判死",
    "不得", "不许", "不可", "死值", "不成立", "不成立",
    "另一种物理产品", "另一个物理产品", "迁版", "不一致",
    "已订正", "作废值", "换架构", "废掉", "不可互相代入", "不可混用",
    "不得与", "另一个物理产品", "另两套", "两种物理产品",
)


def is_skipped_path(path):
    """★路径跳过判定: `.bak` / `__pycache__` / `.git` / `*.pyc` 一律跳过★"""
    norm = path.replace("\\", "/")
    parts = norm.split("/")
    for p in parts:
        if p in SKIP_DIR_NAMES:
            return True
    base = parts[-1] if parts else norm
    if ".bak" in base:                      # 覆盖 .bak / .bak_20261117_1813_iss295
        return True
    if base.endswith(SKIP_EXT):
        return True
    return False


def classify_line(line):
    """→ (是否漂移, 类型列表)。stale ∧ current ∧ ¬historical 才算漂移。"""
    stale = []
    for tag, rx in STALE_RULES:
        if rx.search(line):
            if tag not in stale:
                stale.append(tag)
    if COMPOUND_60x30.search(line) and "③绑60×30" not in stale:
        stale.append("③绑60×30")
    if not stale:
        return False, []

    has_current = any(m in line for m in CURRENT_MARKERS)
    if not has_current:
        return False, []

    has_hist = any(m in line for m in HISTORICAL_MARKERS)
    if has_hist:
        return False, []

    if "①" not in "".join(stale):
        # ①自称现行板框 —— 只有当这行同时把「现行」与「板框/板/权威口径」绑在一起才算
        if any(k in line for k in ("板框", "权威", "唯一", "板")):
            stale.insert(0, "①自称现行板框")
    return True, stale


# ─────────────────────────────────────────────────────────────────────
# 白名单
# ─────────────────────────────────────────────────────────────────────

def parse_whitelist_spec(spec, root=None):
    """`FILE:START-END[,START-END]` → [(relpath, start, end)]  ★relpath 一律以项目根 (PROJ) 为基准★"""
    spec = spec.strip()
    if not spec:
        return []
    if ":" not in spec:
        # 整文件形式 —— 允许, 但【不是默认】, 且会被打印成告警
        return [(_norm(spec), 1, 10 ** 9)]
    path, rng = spec.rsplit(":", 1)
    out = []
    for part in rng.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            try:
                s, e = int(a), int(b)
            except ValueError:
                raise ValueError("白名单行段格式错: %r" % part)
        else:
            try:
                s = e = int(part)
            except ValueError:
                raise ValueError("白名单行段格式错: %r" % part)
        out.append((_norm(path), s, e))
    return out


def _norm(path):
    """→ 项目根 (PROJ) 相对路径, 与扫描输出的 file 字段同基准"""
    p = path.replace("\\", "/").strip()
    if os.path.isabs(p):
        try:
            p = os.path.relpath(p, PROJ)
        except ValueError:
            pass
    if p.startswith("./"):
        p = p[2:]
    return p


def auto_whitelist(root=None):
    """★自动定位 ISS-342 追加声明段 (按文件 + 行段) —— 不是整文件豁免★
    ★路径基准 = 项目根 (PROJ), 与扫描输出的 file 字段同基准★
    """
    p = os.path.join(PROJ, ISS342_BLOCK_FILE)
    if not os.path.isfile(p):
        return []
    try:
        with open(p, encoding="utf-8", errors="ignore") as f:
            lines = f.read().splitlines()
    except OSError:
        return []
    for i, ln in enumerate(lines, 1):
        if ISS342_BLOCK_MARKER in ln and ISS342_BLOCK_TAG in ln:
            end = len(lines)
            for j in range(i, len(lines) + 1):
                if lines[j - 1].strip() == "---":
                    end = j
                    break
            return [(ISS342_BLOCK_FILE, i, end)]
    return []


def wl_hit(wl, path, lineno):
    for (p, s, e) in wl:
        if p == path and s <= lineno <= e:
            return True
    return False


# ─────────────────────────────────────────────────────────────────────
# 扫描
# ─────────────────────────────────────────────────────────────────────

def read_items(root):
    """→ [(relpath, lines)] (跳过 .bak / __pycache__ / .git / 二进制)
    ★relpath 一律以项目根 (PROJ) 为基准 ⇒ 输出 `MECH/xxx.md` 形式★"""
    items = []
    base = PROJ if os.path.abspath(root).startswith(os.path.abspath(PROJ)) else root
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIR_NAMES)
        for fn in sorted(filenames):
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, base).replace("\\", "/")
            if is_skipped_path(rel):
                continue
            try:
                with open(full, encoding="utf-8", errors="ignore") as f:
                    txt = f.read()
            except OSError:
                continue
            if "\x00" in txt[:4096]:
                continue
            items.append((rel, txt.splitlines()))
    return items


def scan_items(items, wl):
    """→ [hit dict]"""
    hits = []
    for rel, lines in items:
        if is_skipped_path(rel):
            continue
        for n, ln in enumerate(lines, 1):
            ok, types = classify_line(ln)
            if not ok:
                continue
            if wl_hit(wl, rel, n):
                continue
            hits.append({
                "file": rel,
                "line": n,
                "types": types,
                "text": ln.strip()[:200],
            })
    return hits


# ─────────────────────────────────────────────────────────────────────
# 自检 (★全程零文件系统写入 —— 用例全在内存里跑★)
# ─────────────────────────────────────────────────────────────────────

def selftest():
    fails = []

    def check(name, cond, detail=""):
        if cond:
            print("  [PASS] %s" % name)
        else:
            print("  [FAIL] %s %s" % (name, detail))
            fails.append(name)

    print("== ISS-342 漂移检测闸 selftest ==")

    # ── 用例 ① 正向: 含 RK3576 + 60×30 的合成文本 ⇒ 必须被检出 ──
    synth_drift = [
        "MECH/demo_synth.md",
        [
            "# 合成用例",
            "- 板宽 30mm / 板长 60mm / 板厚 1.00mm (6 层) —— 现行板框;",
            "- 主控 RK3576 (FCCSP698L, 17.20×16.10mm) —— 现行 SoC;",
            "本表是结构侧对 60×30mm 现行板的唯一权威几何口径。",
        ],
    ]
    h = scan_items([synth_drift], [])
    check("用例①正向: RK3576 + 60×30 合成文本被检出", len(h) == 3,
          "实际命中 %d 条" % len(h))
    check("用例①正向: 类型标签含 ①/②/③",
          any("①自称现行板框" in x["types"] for x in h)
          and any("②绑RK3576" in x["types"] for x in h)
          and any("③绑60×30" in x["types"] for x in h),
          str([x["types"] for x in h]))

    # ── 用例 ② 反向: 干净的合成文本 ⇒ 必须 0 命中 (证明不是无脑 grep) ──
    synth_clean = [
        "MECH/demo_clean.md",
        [
            "# 合成用例 (干净)",
            "- 板宽 30mm / 板长 60mm / RK3576 —— 已标作历史口径, 留档用;",
            "现役板 = 160×100mm / 8 铜层 / 1.60mm / 186 封装 / 主控 RK3572 (SoM 直插)。",
            "板框真值 = HW/PCB/BOARD_FRAME_CALIBER.md",
            "与 BOARD_GEOM_30MM.md 的 RK3576 老基线 —— 本页只引用, 一个字不改。",
        ],
    ]
    h2 = scan_items([synth_clean], [])
    check("用例②反向: 干净/已声明历史的合成文本 0 命中", len(h2) == 0,
          "实际命中 %d 条: %s" % (len(h2), [x["text"][:40] for x in h2]))

    # ── 用例 ③ .bak / __pycache__ 路径 ⇒ 必须被跳过 ──
    synth_skip = [
        ("MECH/keep_me.md.bak_20261117_1813_iss295", ["主控 RK3576 —— 现行 SoC; 板 60×30 现行板框"]),
        ("MECH/__pycache__/fit_check_v3_30mm.cpython-314.pyc", ["主控 RK3576 —— 现行 SoC;"]),
        ("MECH/.git/config", ["RK3576 60×30 现行板框"]),
        ("MECH/real_hit.md", ["主控 RK3576 —— 现行 SoC;"]),
    ]
    h3 = scan_items(synth_skip, [])
    skipped_ok = all(not x["file"].endswith(".bak_20261117_1813_iss295")
                     and "__pycache__" not in x["file"]
                     and ".git" not in x["file"] for x in h3)
    check("用例③: .bak / __pycache__ / .git 路径被跳过", skipped_ok,
          str([x["file"] for x in h3]))
    check("用例③: 非跳过文件仍被检出", len(h3) == 1 and h3[0]["file"] == "MECH/real_hit.md",
          str([x["file"] for x in h3]))

    # ── 用例 ④ 白名单按文件+行段生效, 且不是整文件豁免 ──
    wl = parse_whitelist_spec("MECH/demo_synth.md:2-3")
    h4 = scan_items([synth_drift], wl)
    check("用例④: 白名单行段 2-3 生效 (剩 1 条)", len(h4) == 1 and h4[0]["line"] == 4,
          str([(x["file"], x["line"]) for x in h4]))
    h4b = scan_items([synth_drift], parse_whitelist_spec("MECH/demo_synth.md:1-99"))
    check("用例④: 白名单只按行段, 不会误伤别的文件", len(h4b) == 0)

    # ── 用例 ⑤ 真实盘面: BOARD_GEOM_30MM.md 的 ISS-342 声明段被自动白名单掉 ──
    auto = auto_whitelist(PROJ)
    ok_auto = bool(auto) and auto[0][0] == ISS342_BLOCK_FILE and auto[0][1] >= 2
    check("用例⑤: ISS-342 声明段自动定位成功 (按文件+行段)", ok_auto, str(auto))

    # ── 用例 ⑥ 现有权威表: 老字行仍被检出 (证明闸没被白名单整文件豁免掉) ──
    real_items = []
    p = os.path.join(PROJ, ISS342_BLOCK_FILE)
    if os.path.isfile(p):
        with open(p, encoding="utf-8", errors="ignore") as f:
            real_items = [(ISS342_BLOCK_FILE, f.read().splitlines())]
        hh = scan_items(real_items, auto)
        lines = [x["line"] for x in hh]
        check("用例⑥: 权威表老正文行仍被检出, 且声明段被白名单掉",
              (17 in lines) and all(l < auto[0][1] or l > auto[0][2] for l in lines),
              "命中行号=%s 白名单段=%s" % (lines, auto))

    print("== selftest 结束 ==")
    if fails:
        print("SELFTEST FAILED: %d 条" % len(fails))
        return False
    print("ALL TESTS PASS")
    return True


# ─────────────────────────────────────────────────────────────────────
# main
# ─────────────────────────────────────────────────────────────────────

def main(argv=None):
    ap = argparse.ArgumentParser(
        description="结构侧口径漂移只读检测闸 (ISS-342) · 零写板 · 零改文件")
    ap.add_argument("--root", default=DEFAULT_ROOT,
                    help="扫描域 (相对项目根), 默认 MECH")
    ap.add_argument("--whitelist", action="append", default=[],
                    help="白名单 spec: FILE:START-END[,START-END] (可重复)")
    ap.add_argument("--whitelist-file", default=None,
                    help="白名单文件: 一行一个 spec, # 开头为注释")
    ap.add_argument("--selftest", action="store_true", help="跑自检 (末行 ALL TESTS PASS)")
    ap.add_argument("--json", action="store_true", help="机器可读输出")
    ap.add_argument("--quiet", action="store_true", help="只出汇总")
    args = ap.parse_args(argv)

    if args.selftest:
        try:
            return 0 if selftest() else 1
        except Exception as e:                      # noqa: BLE001
            print("SELFTEST ERROR: %r" % (e,), file=sys.stderr)
            return 1

    try:
        root = args.root if os.path.isabs(args.root) else os.path.join(PROJ, args.root)
        if not os.path.isdir(root):
            print("!! 扫描域不存在: %s" % root, file=sys.stderr)
            return 1

        wl = list(auto_whitelist(root))
        for spec in args.whitelist:
            wl.extend(parse_whitelist_spec(spec, root))
        if args.whitelist_file:
            with open(args.whitelist_file, encoding="utf-8", errors="ignore") as f:
                for ln in f:
                    ln = ln.strip()
                    if not ln or ln.startswith("#"):
                        continue
                    wl.extend(parse_whitelist_spec(ln, root))

        items = read_items(root)
        hits = scan_items(items, wl)

        if args.json:
            print(json.dumps({
                "root": os.path.relpath(root, PROJ),
                "whitelist": [{"file": p, "start": s, "end": e} for (p, s, e) in wl],
                "scanned_files": len(items),
                "hit_count": len(hits),
                "hits": hits,
                "rc": 2 if hits else 0,
            }, ensure_ascii=False, indent=2))
            return 2 if hits else 0

        if not args.quiet:
            print("== 结构侧口径漂移检测闸 (ISS-342 · 只读) ==")
            print("扫描域: %s  |  扫描文件数: %d  |  白名单段: %d"
                  % (os.path.relpath(root, PROJ), len(items), len(wl)))
            for (p, s, e) in wl:
                print("  白名单: %s:%d-%d  (%s)" % (p, s, e, "整文件豁免" if e > 10 ** 8 else "行段豁免"))
            if hits:
                print("-- 漂移命中 (白名单之外, 一律要报) --")
                for x in hits:
                    print("%s:%d | %s | %s" % (x["file"], x["line"],
                                               "+".join(x["types"]), x["text"]))
        print("[DRIFT] 未声明口径漂移: %d 处 / %d 个文件"
              % (len(hits), len(set(x["file"] for x in hits))))
        return 2 if hits else 0

    except Exception as e:                          # noqa: BLE001
        print("!! 运行错误: %r" % (e,), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
