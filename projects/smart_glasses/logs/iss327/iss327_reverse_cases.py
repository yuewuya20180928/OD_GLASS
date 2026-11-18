#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iss327_reverse_cases.py —— ISS-327 cont1 · 「真隐患不许被 --freeze-registry 洗白」反向用例 (★≥5 条★)

★★每条用例都是【先故意把真隐患改坏 ⇒ 再重建注册表 ⇒ 看闸还抓不抓得到】★★
★每条贴「期望红/绿」+「实际红/绿」★

★边界: 只写 tmp/iss327/rc*/ + logs/iss327/20_reverse_cases.txt (★真件一个字节都不动★) ★
★纪律: 沙盒零软链 (tar 解包) · 写前 assert not islink ★
"""
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(HERE))
SB = os.path.join(PROJ, "tmp", "iss327")
LOG = os.path.join(PROJ, "logs", "iss327", "20_reverse_cases.txt")

spec = importlib.util.spec_from_file_location("sbm", os.path.join(HERE, "iss327_sb_make.py"))
SBM = importlib.util.module_from_spec(spec)
spec.loader.exec_module(SBM)

MAP = json.load(open(SBM.MAPJSON, encoding="utf-8"))["rename"]
OUT = []


def A(s):
    OUT.append(s)
    print(s)


def gate(root, *args):
    r = subprocess.run([sys.executable, "SW/tools/check_sw_ref_reachability.py"] + list(args),
                       cwd=root, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def stats(txt):
    out = {}
    for cls in ("DESIGNATOR_OK", "DESIGNATOR_DRIFT", "DESIGNATOR_MISSING"):
        m = re.search(r"^\s+%s\s+(\d+)\s*$" % cls, txt, re.M)
        out[cls] = int(m.group(1)) if m else -1
    m = re.search(r"允许上限 = (\d+) 条", txt)
    out["limit"] = int(m.group(1)) if m else -1
    out["missing_list"] = re.findall(r"DESIGNATOR_MISSING\s+C14\s+(\S+)", txt)
    return out


def fresh(root):
    if os.path.isdir(root):
        shutil.rmtree(root)
    os.makedirs(root)
    subprocess.run(["tar", "-C", root, "-xf", SBM.TPL], check=True, capture_output=True)
    SBM.rename_board(os.path.join(root, SBM.BOARD_REL), MAP)
    for rel in SBM.CSV_SIDES:
        SBM.rename_csv(os.path.join(root, rel), MAP)
    SBM.rename_schematics(root, MAP)
    SBM.rename_sw_docs(root, MAP)
    os.makedirs(os.path.join(root, "tmp"), exist_ok=True)
    return root


def rebuild_registry(root, tag):
    rc, txt = gate(root, "--freeze-registry")
    p = os.path.join(PROJ, "logs", "iss327", "21_freeze_%s.txt" % tag)
    open(p, "w", encoding="utf-8").write(txt)
    r = subprocess.run([sys.executable, os.path.join(HERE, "iss327_apply_registry.py"), root, p],
                       capture_output=True, text=True)
    return r.stdout.strip()


def doc_token_replace(root, rel, old, new):
    p = os.path.join(root, rel)
    txt = open(p, encoding="utf-8", errors="replace").read()
    n = txt.count(old)
    txt = txt.replace(old, new)
    if os.path.islink(p):
        raise RuntimeError("★[ABORT] 软链 ⇒ 拒绝写穿")
    open(p, "w", encoding="utf-8", errors="replace").write(txt)
    return n


def main():
    A("=" * 100)
    A("ISS-327 cont1 · 「真隐患不许被 --freeze-registry 洗白」反向用例 (★每条都是实跑读数★)")
    A("=" * 100)
    A("")

    results = []

    # ── RC-1/2/3: 三个建闸日真隐患, 各改成【新的、从来不存在过的位号形状】, 重建注册表后必须仍被抓住 ──
    for i, (old, new, rel) in enumerate([("TP_TEMP", "TP_GHOST_X9", "SW/SW_TIMING_REVIEW.md"),
                                         ("TP_INT", "TP_PHANTOM_Q1", "SW/BOARD_ONEPASS_SW_SYNC.md"),
                                         ("CONN_USB", "CONN_PHANTOM_7", "SW/SW_TIMING_REVIEW.md")], start=1):
        root = fresh(os.path.join(SB, "rc%d" % i))
        n = doc_token_replace(root, rel, old, new)
        if n <= 0:
            A("── RC-%d · ★[ABORT] 故障注入没生效 (%s 里找不到 `%s`·替换 0 处) ⇒ 本条作废·不许报成判据缺陷★"
              % (i, rel, old))
            A("")
            results.append(("RC-%d" % i, "真隐患 `%s`→新形状 `%s`" % (old, new),
                            "红 (MISSING 4 > 3)", "★作废(注入未生效)", "ABORT"))
            continue
        rc0, t0 = gate(root)
        s0 = stats(t0)
        reg = rebuild_registry(root, "rc%d" % i)
        rc1, t1 = gate(root)
        s1 = stats(t1)
        A("── RC-%d · 真隐患 `%s` 改成新形状 `%s` (★文档里替换 %d 处★) ──" % (i, old, new, n))
        A("   重建前 : rc=%d · OK=%d DRIFT=%d MISSING=%d (上限 %d) · MISSING名单=%s"
          % (rc0, s0["DESIGNATOR_OK"], s0["DESIGNATOR_DRIFT"], s0["DESIGNATOR_MISSING"],
             s0["limit"], s0["missing_list"]))
        A("   重建后 : rc=%d · OK=%d DRIFT=%d MISSING=%d (上限 %d) · MISSING名单=%s"
          % (rc1, s1["DESIGNATOR_OK"], s1["DESIGNATOR_DRIFT"], s1["DESIGNATOR_MISSING"],
             s1["limit"], s1["missing_list"]))
        caught = (new in s1["missing_list"]) and rc1 != 0
        A("   ⇒ 期望: 【红】(重建后 `%s` 仍必须被 C14 抓住 · MISSING 4 > 上限 3) · 实际: %s"
          % (new, "【红】✓ 没被洗白" if caught else "【绿】✗ 被洗白了 ⇒ 判据缺陷"))
        A("")
        results.append(("RC-%d" % i, "真隐患 `%s`→新形状 `%s`" % (old, new),
                        "红 (MISSING 4 > 3)", "红" if rc1 != 0 else "绿", "PASS" if caught else "FAIL"))

    # ── RC-4: 反向次序 —「文档没同批改名」时重建注册表 ⇒ 漂移被洗成真隐患 (红得更凶) ──
    root = fresh(os.path.join(SB, "rc4"))
    # 把 SW 文档改回【旧名】= 模拟「文档没同批改名」
    d = os.path.join(root, "SW")
    for name in sorted(os.listdir(d)):
        if not name.endswith(".md"):
            continue
        p = os.path.join(d, name)
        txt = open(p, encoding="utf-8", errors="replace").read()
        for old in sorted(MAP.keys(), key=len, reverse=True):
            pat = re.compile(r"(?<![A-Za-z0-9_])" + re.escape(MAP[old]) + r"(?![A-Za-z0-9_])")
            txt = pat.sub(old, txt)
        if os.path.islink(p):
            raise RuntimeError("★[ABORT] 软链 ⇒ 拒绝写穿")
        open(p, "w", encoding="utf-8", errors="replace").write(txt)
    rc0, t0 = gate(root)
    s0 = stats(t0)
    rebuild_registry(root, "rc4")
    rc1, t1 = gate(root)
    s1 = stats(t1)
    A("── RC-4 · 反向次序: SW 文档【没同批改名】时重建注册表 ──")
    A("   重建前 : rc=%d · OK=%d DRIFT=%d MISSING=%d (上限 %d)"
      % (rc0, s0["DESIGNATOR_OK"], s0["DESIGNATOR_DRIFT"], s0["DESIGNATOR_MISSING"], s0["limit"]))
    A("   重建后 : rc=%d · OK=%d DRIFT=%d MISSING=%d (上限 %d)"
      % (rc1, s1["DESIGNATOR_OK"], s1["DESIGNATOR_DRIFT"], s1["DESIGNATOR_MISSING"], s1["limit"]))
    A("   ⇒ 期望: 【红】(漂移 58 → MISSING 56 ⇒ 假红变真红) · 实际: %s"
      % ("【红】✓ 实测 DRIFT 58→0 · MISSING 5→56" if (rc1 != 0 and s0["DESIGNATOR_DRIFT"] == 58
         and s1["DESIGNATOR_DRIFT"] == 0 and s1["DESIGNATOR_MISSING"] == 56) else "★与预期不符"))
    A("")
    results.append(("RC-4", "反向次序 (文档未同批改名) 重建注册表", "红 (且 58→56 更凶)",
                    "红" if rc1 != 0 else "绿", "PASS" if rc1 != 0 else "FAIL"))

    # ── RC-5: 正向回归 — 文档同批改名 + 重建注册表 ⇒ 必须绿 (MISSING 仍 3) ──
    root = fresh(os.path.join(SB, "rc5"))
    rc0, t0 = gate(root)
    s0 = stats(t0)
    rebuild_registry(root, "rc5")
    rc1, t1 = gate(root)
    s1 = stats(t1)
    A("── RC-5 · 正向回归: 文档同批改名 + 重建注册表 ──")
    A("   重建前 : rc=%d · OK=%d DRIFT=%d MISSING=%d (上限 %d)"
      % (rc0, s0["DESIGNATOR_OK"], s0["DESIGNATOR_DRIFT"], s0["DESIGNATOR_MISSING"], s0["limit"]))
    A("   重建后 : rc=%d · OK=%d DRIFT=%d MISSING=%d (上限 %d)"
      % (rc1, s1["DESIGNATOR_OK"], s1["DESIGNATOR_DRIFT"], s1["DESIGNATOR_MISSING"], s1["limit"]))
    ok5 = (rc1 == 0 and s1["DESIGNATOR_DRIFT"] == 0 and s1["DESIGNATOR_MISSING"] == 3)
    A("   ⇒ 期望: 【绿】(rc=0 · DRIFT 0 · MISSING 3) · 实际: %s"
      % ("【绿】✓" if ok5 else "★与预期不符"))
    A("")
    results.append(("RC-5", "正向回归 (文档同批改名 + 重建注册表)", "绿 (rc=0 · DRIFT 0 · MISSING 3)",
                    "绿" if rc1 == 0 else "红", "PASS" if ok5 else "FAIL"))

    # ── RC-6: 判据跟盘面走 — 把真隐患位号补到板文件里 ⇒ 它必须从 MISSING 变 OK ──
    root = fresh(os.path.join(SB, "rc6"))
    bp = os.path.join(root, SBM.BOARD_REL)
    txt = open(bp, encoding="utf-8", errors="replace").read()
    txt += '\n  (property "Reference" "TP_GHOST_X9" "TP_GHOST_X9")\n'
    if os.path.islink(bp):
        raise RuntimeError("★[ABORT] 软链 ⇒ 拒绝写穿")
    open(bp, "w", encoding="utf-8", errors="replace").write(txt)
    rebuild_registry(root, "rc6")
    rc1, t1 = gate(root)
    s1 = stats(t1)
    A("── RC-6 · 判据跟盘面走: 把 `TP_GHOST_X9` 补进板文件 ⇒ 它必须从 MISSING 变 OK ──")
    A("   重建后 : rc=%d · OK=%d DRIFT=%d MISSING=%d (上限 %d) · MISSING名单=%s"
      % (rc1, s1["DESIGNATOR_OK"], s1["DESIGNATOR_DRIFT"], s1["DESIGNATOR_MISSING"],
         s1["limit"], s1["missing_list"]))
    ok6 = ("TP_GHOST_X9" not in s1["missing_list"]) and rc1 == 0
    A("   ⇒ 期望: 【绿】(它变成板上的真位号 ⇒ OK · MISSING 回到 3) · 实际: %s"
      % ("【绿】✓ 判据跟盘面走 (不是写死名单)" if ok6 else "★与预期不符"))
    A("")
    results.append(("RC-6", "真位号补进板 ⇒ 从 MISSING 变 OK", "绿 (MISSING 回 3)", 
                    "绿" if rc1 == 0 else "红", "PASS" if ok6 else "FAIL"))

    A("=" * 100)
    A("★反向用例汇总表 (★每条都有期望 + 实跑读数★)")
    A("=" * 100)
    A("%-8s %-44s %-26s %-8s %-8s" % ("用例", "场景", "期望", "实际", "判定"))
    for r in results:
        A("%-8s %-44s %-26s %-8s %-8s" % r)
    A("")
    A("★总判定: %d 条 · PASS %d · FAIL %d"
      % (len(results), len([r for r in results if r[4] == "PASS"]), len([r for r in results if r[4] == "FAIL"])))
    open(LOG, "w", encoding="utf-8").write("\n".join(OUT) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
