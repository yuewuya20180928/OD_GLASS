#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iss327_sb_make.py —— ISS-327 cont1 · 「改名后 SW 侧闸链」沙盒造场 (★零软链 · 真拷贝版★)

★★★【为什么重写这个脚本】★★★ ★★上一趟 (2026-11-18 14:21~14:30) 出了真事故★ ★★
  · 上一趟的第 ② 步把 `SW/*.md` 全部 `os.symlink()` 软链到真件
  · 随后第 ⑤ 步 `build_sw_docs()` 用 `open(root/SW/<name>.md, "w")` 直接写那个软链路径
  ⇒ 写穿到真件 ⇒ 真件 42 份 SW 文档里 11 份被改成「改名后」位号 (781 处) ⇒ 闸红 rc=1
  ⇒ 事故现场留证: `logs/iss327/iss327_sb_make.py.orig_accident_ver` (★本脚本改之前的逐字原件★)

★★★【本版 5 条硬规矩 (★cont1 任务书 §2★)】★★★ ★★★
  ① 沙盒里凡要【写】的文件 ⇒ 一律真拷贝 (shutil.copyfile / tar 解包) · ★软链一个都不许有★
  ② 写之前 `assert not os.path.islink(path)` ⇒ 软链当场炸
  ③ 真件 `SW/*.md` 一律不许改名 ⇒ 「改名后闸链全绿」只在真拷贝沙盒里验
  ④ 沙盒跑完必查真件 mtime 漂移 = 0 (★由 `iss327_run_gates.sh` + 交卷页负责★)
  ⑤ 闸脚本副本也要是真拷贝 (★tar 解包 ⇒ 天然是真文件★)
  ★验收: `find <沙盒root> -type l` 必须是空 ★

★边界: 零写板 · 零落表 · 零改闸 (真件 `SW/tools/*.py` 一个字节都不许改) · 沙盒只写 `tmp/iss327/` ★
"""
import csv
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))          # logs/iss327/
PROJ = os.path.dirname(os.path.dirname(HERE))              # 项目根
SB = os.environ.get("ISS327_SB", os.path.join(PROJ, "tmp", "iss327"))   # ★可被环境变量改到假目录·先试跑★
TPL = os.path.join(SB, "tree_template.tar")
MAPJSON = os.path.join(PROJ, "tmp", "iss327", "rename_map_iss327.json")   # ★输入·永远是真件那份·只读★

PSEUDO = ("RAIL_", "NET_")
REF_RE = re.compile(r'\(property\s+"Reference"\s+"([^"]*)"')
NODE_RE = re.compile(r"^([A-Za-z_0-9]+)(\s+.*)?$")

# ★★tar 解包时的排除表 (★只排【与 10 道闸的读数无关】的体积大户·不排任何闸会读的面★)★★
TAR_EXCLUDES = [
    "./.trash", "./.openclaw", "./tmp", "./logs",
    "*.onnx", "__pycache__", "./state/*.bak_*", "*/.bak_*",
    "./state/.lastgood", "./state/.cache_*", "./state/_os_snapshots",
    "./state/.gen_*", "./state/.router_src_*",
    "./SW/artifacts",
    "./HW/PCB/production", "./HW/PCB/gerbers", "./HW/PCB/_tmp_pi5",
]

# ★★要改名的 5 个面 (★板 + 网表 + 脚表 + BOM + 原理图·★ISS-317 的五侧口径★)★★
CSV_SIDES = ("HW/netlist_v1.csv", "HW/netlist_v1_pins.csv", "HW/BOM_v1.csv")
BOARD_REL = "HW/PCB/demo_mainboard.kicad_pcb"
SCH_DIR = "HW/PCB"


# ════════════════════════════════════════════════════════════════════
# §GUARD · 写前守卫 (★cont1 规矩 ②★)
# ════════════════════════════════════════════════════════════════════
def guard_write(path, what=""):
    """★写任何文件之前必须过这一关★"""
    p = os.path.abspath(path)
    if os.path.islink(p):
        raise RuntimeError("★[ABORT] 要写的路径是软链 ⇒ 拒绝写穿: %s (%s)" % (p, what))
    return p


def assert_no_symlink_in(root):
    """★验收: 沙盒里一个软链都不许有 (★cont1 规矩 ① + 任务书 §2 实操验收★)"""
    bad = []
    for dirpath, dirnames, filenames in os.walk(root):
        for n in list(dirnames) + list(filenames):
            p = os.path.join(dirpath, n)
            if os.path.islink(p):
                bad.append(p)
    return bad


# ════════════════════════════════════════════════════════════════════
# §TREE · 真拷贝整棵树 (★tar 解包 ⇒ 天然真文件·零软链★)
# ════════════════════════════════════════════════════════════════════
def build_template():
    os.makedirs(SB, exist_ok=True)
    cmd = ["tar", "-C", PROJ, "-cf", TPL]
    for e in TAR_EXCLUDES:
        cmd += ["--exclude=" + e]
    cmd.append(".")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("[FAIL] tar 造模板失败 rc=%d\n%s" % (r.returncode, r.stderr[-2000:]))
        return None
    return TPL


def extract_tree(root):
    if os.path.isdir(root):
        shutil.rmtree(root)
    os.makedirs(root)
    r = subprocess.run(["tar", "-C", root, "-xf", TPL], capture_output=True, text=True)
    if r.returncode != 0:
        print("[FAIL] tar 解包失败 rc=%d\n%s" % (r.returncode, r.stderr[-2000:]))
        return False
    return True


# ════════════════════════════════════════════════════════════════════
# §RENAME · 改名 (★只改沙盒副本★)
# ════════════════════════════════════════════════════════════════════
def rename_ref(tok, mapping):
    tok = (tok or "").strip()
    if not tok or tok.startswith(PSEUDO):
        return tok
    return mapping.get(tok, tok)


def rename_node(node, mapping):
    node = (node or "").strip()
    if not node:
        return node
    m = NODE_RE.match(node)
    if not m:
        return node
    comp = m.group(1)
    if comp.startswith(PSEUDO):
        return node
    return rename_ref(comp, mapping) + (m.group(2) or "")


def rename_board(path, mapping):
    txt = open(path, encoding="utf-8", errors="replace").read()
    n = 0
    out, last = [], 0
    for m in REF_RE.finditer(txt):
        old = m.group(1)
        new = rename_ref(old, mapping)
        if new != old:
            n += 1
        out.append(txt[last:m.start(1)])
        out.append(new)
        last = m.end(1)
    out.append(txt[last:])
    guard_write(path, "board")
    open(path, "w", encoding="utf-8", errors="replace").write("".join(out))
    return n


def rename_csv(path, mapping):
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    flds = list(rows[0].keys())
    n = 0
    out = []
    for r in rows:
        r2 = dict(r)
        ref = (r2.get("ref") or "").strip()
        if ref and not ref.startswith(PSEUDO):
            new = rename_ref(ref, mapping)
            if new != ref:
                n += 1
            r2["ref"] = new
        if "node1" in r2:
            r2["node1"] = rename_node(r2.get("node1") or "", mapping)
        if "node2" in r2:
            r2["node2"] = rename_node(r2.get("node2") or "", mapping)
        if "pin_id" in r2:
            pid = r2.get("pin_id") or ""
            if ref and pid.startswith(ref + "."):
                r2["pin_id"] = rename_ref(ref, mapping) + pid[len(ref):]
        out.append(r2)
    guard_write(path, "csv")
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=flds)
        w.writeheader()
        for r in out:
            w.writerow(r)
    return n


def rename_schematics(root, mapping):
    d = os.path.join(root, SCH_DIR)
    tot = 0
    files = 0
    for name in sorted(os.listdir(d)):
        if not name.endswith(".kicad_sch"):
            continue
        p = os.path.join(d, name)
        txt = open(p, encoding="utf-8", errors="replace").read()
        n = 0
        out, last = [], 0
        for m in REF_RE.finditer(txt):
            old = m.group(1)
            new = rename_ref(old, mapping)
            if new != old:
                n += 1
            out.append(txt[last:m.start(1)])
            out.append(new)
            last = m.end(1)
        out.append(txt[last:])
        guard_write(p, "schematic")
        open(p, "w", encoding="utf-8", errors="replace").write("".join(out))
        tot += n
        files += 1
    return files, tot


def rename_sw_docs(root, mapping):
    """★SW/*.md 位号字面量同步 (★第 7 件的机器化改法·★与 logs/iss323/iss323_rename_sw_docs.py 同算法★)★"""
    d = os.path.join(root, "SW")
    keys = sorted(mapping.keys(), key=len, reverse=True)
    n_files = n_hits = 0
    for name in sorted(os.listdir(d)):
        if not name.endswith(".md"):
            continue
        p = os.path.join(d, name)
        txt = open(p, encoding="utf-8", errors="replace").read()
        hits = 0
        for old in keys:
            new = mapping[old]
            pat = re.compile(r"(?<![A-Za-z0-9_])" + re.escape(old) + r"(?![A-Za-z0-9_])")
            txt, c = pat.subn(new, txt)
            hits += c
        guard_write(p, "sw doc")
        open(p, "w", encoding="utf-8", errors="replace").write(txt)
        n_files += 1
        n_hits += hits
    return n_files, n_hits


# ════════════════════════════════════════════════════════════════════
# §BUILD · 造场
# ════════════════════════════════════════════════════════════════════
def build_root(root, mapping, rename_docs, tag, rename_hw=True):
    if not extract_tree(root):
        return None
    nb = 0
    ncsvs = [0, 0, 0]
    nsf = nsn = 0
    if rename_hw:
        # ① HW 五侧改名 (板 + 网表 + 脚表 + BOM + 原理图)
        nb = rename_board(os.path.join(root, BOARD_REL), mapping)
        ncsvs = []
        for rel in CSV_SIDES:
            ncsvs.append(rename_csv(os.path.join(root, rel), mapping))
        nsf, nsn = rename_schematics(root, mapping)
    # ② SW 文档改名 (★第 7 件★)
    ndocs = nhits = 0
    if rename_docs:
        ndocs, nhits = rename_sw_docs(root, mapping)
    # ②b 沙盒里也要有 tmp/ (★check_landing_trace_obligation.py --selftest 要 tempfile.mkdtemp(dir=PROJ/tmp)★)
    os.makedirs(os.path.join(root, "tmp"), exist_ok=True)
    # ③ 验收: 零软链
    bad = assert_no_symlink_in(root)
    if bad:
        print("  ★[FAIL] 沙盒 %s 里有 %d 个软链 (★规矩 ① 破了★): %s" % (tag, len(bad), bad[:5]))
        return None
    print("  ★沙盒 %-8s 板改 %3d · 网表 %3d · 脚表 %3d · BOM %3d · 原理图 %d 份/%4d 处 · SW文档 %d 份/%4d 处 · 软链 0"
          % (tag, nb, ncsvs[0], ncsvs[1], ncsvs[2], nsf, nsn, ndocs, nhits))
    return root


def main():
    os.makedirs(SB, exist_ok=True)

    # ── 起点自证: 板 / 网表 / 脚表 / BOM 四 md5 必须还是基线值 (★零写板前置★) ──
    import hashlib

    def md5(p):
        h = hashlib.md5()
        with open(p, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()

    expect = {
        "HW/PCB/demo_mainboard.kicad_pcb": "611b869e13518c3c023fb178f91a0075",
        "HW/netlist_v1.csv": "6aee500e60ba0732f83a9cf557ba90ab",
        "HW/netlist_v1_pins.csv": "9174309df1ec9411ac8e8d9e80ee386a",
        "HW/BOM_v1.csv": "5b9993992405904a60ac96a020b375d8",
    }
    for rel, want in expect.items():
        got = md5(os.path.join(PROJ, rel))
        if got != want:
            print("[FAIL] 真件 %s md5 = %s ≠ 基线 %s ⇒ abort (★零写板前置不成立★)" % (rel, got, want))
            return 2
    print("★起点自证: 板 / 网表 / 脚表 / BOM 四 md5 与基线逐字相同 ⇒ 零写板前置成立")

    # ── 改名映射: 读上一趟已生成的那份 (★不许重算·不许手抄★) ──
    if not os.path.isfile(MAPJSON):
        print("[FAIL] 改名映射读不到: %s" % MAPJSON)
        return 2
    d = json.load(open(MAPJSON, encoding="utf-8"))
    mapping = d["rename"]
    print("★改名映射: %d 条 (★期望 186★) · 全表 %d 条 (★期望 218★)"
          % (len(mapping), len(d["map"])))
    if len(mapping) != 186 or len(d["map"]) != 218:
        print("[FAIL] 改名映射条数不符 ⇒ abort")
        return 2

    # ── 模板 (★tar 解包 ⇒ 零软链★) ──
    print("")
    print("★造模板 (tar 排除表 %d 条) ..." % len(TAR_EXCLUDES))
    if build_template() is None:
        return 2
    print("  ★模板落 %s (%.1f MB)" % (TPL, os.path.getsize(TPL) / 1e6))

    # ── 造场 ──
    print("")
    build_root(os.path.join(SB, "sbCtl"), mapping, False, "sbCtl", rename_hw=False)
    build_root(os.path.join(SB, "sbR0"), mapping, False, "sbR0")
    build_root(os.path.join(SB, "sbR3"), mapping, True, "sbR3")

    print("")
    print("★沙盒造场完成 (只写 tmp/iss327/)")
    print("  sbCtl = 对照组 (★整树真拷贝·零改名·闸副本真文件★)")
    print("  sbR0  = 五侧改名 + SW 文档【未】同步 + 旧注册表")
    print("  sbR3  = 五侧改名 + SW 文档【已】同步 + 旧注册表")
    print("  sbR1/sbR2 = 在 sbR0/sbR3 上重建注册表后得到 (★由 iss327_apply_registry.py 就地贴★)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
