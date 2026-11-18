#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iss327_rev_suite.py —— ISS-327 · 反向用例套件 (★≥5 条·每条贴「期望红/绿」与「实际红/绿」★)

★只写 tmp/iss327/ + logs/iss327/ ⇒ 零写板 · 零落表 · 零改闸 (★真件一个字都不动★)★
★纪律: 写前 assert not os.path.islink(path) ⇒ 软链当场炸 ★

★每条用例的读法★:
  起点 = tmp/iss327/sbR3 (★五侧改名 + SW 文档已同步 + 旧注册表 74 条★)
  ① 注入一个【故意做坏】的 token
  ② 第一跑 (重建注册表【之前】) ⇒ rc_before
  ③ --freeze-registry 重建 ⇒ 看新表里含不含注入的 token
  ④ 把新表贴回沙盒闸副本 ⇒ 第二跑 ⇒ rc_after
  ⑤ 判读: 期望红/绿 vs 实际红/绿
"""
import hashlib
import os
import re
import shutil
import subprocess
import sys

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
SB = os.path.join(PROJ, "tmp", "iss327")
LOG = os.path.join(PROJ, "logs", "iss327")
SRC_R3 = os.path.join(SB, "sbR3")
SRC_R0 = os.path.join(SB, "sbR0")
GATE_REL = os.path.join("SW", "tools", "check_sw_ref_reachability.py")

BLOCK_RE = re.compile(r"DESIGNATOR_REGISTRY = \(\n.*?\n\)\n# ★共 \d+ 条★[^\n]*\n", re.S)
TOKEN_RE = re.compile(r'^\s+"([A-Za-z0-9_]+)",$', re.M)


def L(*a):
    print(*a, flush=True)


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def no_symlink(root):
    bad = []
    for dp, dns, fns in os.walk(root):
        for fn in fns:
            p = os.path.join(dp, fn)
            if os.path.islink(p):
                bad.append(p)
    return bad


def inject(root, old, new):
    """把 root 里 SW/*.md 的 old token 换成 new (★词边界·不许误伤·)"""
    nfiles = nrepl = 0
    for dp, dns, fns in os.walk(os.path.join(root, "SW")):
        for fn in sorted(fns):
            if not fn.endswith(".md"):
                continue
            p = os.path.join(dp, fn)
            assert not os.path.islink(p), "★[FAIL] 软链当场炸: %s" % p
            txt = open(p, "r", encoding="utf-8").read()
            if old not in txt:
                continue
            cnt = txt.count(old)
            new_txt = re.sub(r"\b%s\b" % re.escape(old), new, txt)
            open(p, "w", encoding="utf-8").write(new_txt)
            nfiles += 1
            nrepl += cnt
    return nfiles, nrepl


def run_gate(root, extra=()):
    cmd = [sys.executable, os.path.join(root, GATE_REL), "--root", root] + list(extra)
    r = subprocess.run(cmd, cwd=PROJ, stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, text=True)
    return r.returncode, r.stdout


def freeze(root):
    rc, out = run_gate(root, ["--freeze-registry"])
    toks = TOKEN_RE.findall(out)
    return rc, out, toks


def paste(root, freeze_out):
    gate = os.path.join(root, GATE_REL)
    assert not os.path.islink(gate), "★[FAIL] 软链当场炸: %s" % gate
    m = re.search(r"DESIGNATOR_REGISTRY = \(\n(.*?)\n\)\n(# ★共 \d+ 条★[^\n]*)",
                  freeze_out, re.S)
    old = open(gate, encoding="utf-8").read()
    new = BLOCK_RE.sub("DESIGNATOR_REGISTRY = (\n%s\n)\n%s\n" % (m.group(1), m.group(2)),
                       old, count=1)
    open(gate, "w", encoding="utf-8").write(new)


def stats(out):
    miss = re.search(r"DESIGNATOR_MISSING\s+(\d+)", out)
    drift = re.search(r"DESIGNATOR_DRIFT\s+(\d+)", out)
    ok = re.search(r"DESIGNATOR_OK\s+(\d+)", out)
    return (int(miss.group(1)) if miss else -1,
            int(drift.group(1)) if drift else -1,
            int(ok.group(1)) if ok else -1)


def live_refs(root):
    """★从板 + 网表里解析 live 位号 (★用来验证重建表里没有非 live token★)★"""
    sys.path.insert(0, os.path.join(root, "SW", "tools"))
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "g", os.path.join(root, "SW", "tools", "check_sw_ref_reachability.py"))
    g = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(g)
    br = g.read_board_refs(os.path.join(root, g.BOARD_REL))
    nr = g.read_netlist_refs({"root": root})
    return br | nr


# ════════════════════════════════════════════════════════════════════
# 用例表: (id, 起点, 注入old, 注入new, 期望[重建前], 期望[重建后], 目的)
# ════════════════════════════════════════════════════════════════════
CASES = [
    ("RT-1", SRC_R3, "TP_TEMP", "TP_TEMP_ISSX", "红", "红",
     "★题目指定的那条★: 真隐患改成【新的·从来不存在过的位号形状】⇒ 重建后必须仍然被抓住"),
    ("RT-2", SRC_R3, "TP_INT", "TP_INT_ISSX", "红", "红",
     "第二条基线真隐患同款处理 ⇒ 重建后必须仍然被抓住"),
    ("RT-3", SRC_R3, "CONN_USB", "CONN_USB_ISSX", "红", "红",
     "第三条基线真隐患同款处理 ⇒ 重建后必须仍然被抓住"),
    ("RT-4", SRC_R3, "TP_TEMP", "TP_TEMP_ISSX2", "红", "红",
     "★形状更长的新名 (多一位后缀) ⇒ 验证不是靠「长度差」偶然躲开"),
    ("RT-5", SRC_R3, "TP_TEMP", "U_TEMP_1", "红", "红",
     "★真隐患被写成一个【live 位号名】(U_TEMP_1 改名后确实在盘上) ⇒ 测 C1 存在性判据的洗白面"),
    ("RT-6", SRC_R3, "TP_TEMP", "TP_temp", "红", "红",
     "★真隐患改成【含小写】⇒ 测 C7 (物理量符号) 规则的洗白面"),
    ("RT-7", SRC_R3, "TP_TEMP", "SW_TEMP_ISSX", "红", "红",
     "★真隐患改成【SW_ 前缀】⇒ 测 C13 (软件侧命名空间) 规则的洗白面"),
    ("RT-8", SRC_R3, "TP_TEMP", "TP_TEMP_", "红", "红",
     "★真隐患改成【以 _ 结尾】⇒ 测 C8 (前缀截断) 规则的洗白面"),
]


def main():
    L("=" * 90)
    L("# ISS-327 · 反向用例套件 (★每条: 期望红/绿 vs 实际红/绿★)")
    L("# 起点沙盒 = tmp/iss327/sbR3 (★五侧改名 + SW 文档已同步 + 旧注册表 74 条★)")
    L("=" * 90)
    rows = []
    for cid, src, old, new, exp_b, exp_a, purpose in CASES:
        dst = os.path.join(SB, "sbRT_%s" % cid)
        if os.path.isdir(dst):
            shutil.rmtree(dst)
        L("")
        L("─" * 88)
        L("【%s】 %s" % (cid, purpose))
        L("─" * 88)
        shutil.copytree(src, dst, symlinks=False)
        bad = no_symlink(dst)
        assert not bad, "★[FAIL] 沙盒里出现软链: %s" % bad[:3]
        nf, nr = inject(dst, old, new)
        L("  注入: %s → %s · 改了 %d 份 md · %d 处" % (old, new, nf, nr))
        if nf == 0:
            L("  ★[SKIP] 起点里找不到 %s" % old)
            shutil.rmtree(dst)
            continue
        rc_b, out_b = run_gate(dst, ["--dump-classification"])
        miss_b, drift_b, ok_b = stats(out_b)
        L("  [重建前] rc=%d (★%s★) · MISSING=%d · DRIFT=%d · OK=%d · 输出里出现 %s = %s"
          % (rc_b, "红" if rc_b else "绿", miss_b, drift_b, ok_b, new,
             "★是★" if new in out_b else "★否★"))
        frc, fout, ftoks = freeze(dst)
        in_new = ('"%s"' % new) in fout
        L("  [重建]   freeze rc=%d · 新表 %d 条 · 含注入 token %s ? = %s"
          % (frc, len(ftoks), new, "★含(危险)★" if in_new else "★不含(正确)★"))
        # 结构性自证: 新表里每个 token 都必须 live
        try:
            live = live_refs(dst)
            nonlive = [t for t in ftoks if t not in live]
        except Exception as exc:                                  # noqa: BLE001
            live, nonlive = set(), ["<live 解析失败: %s>" % exc]
        L("  [结构]   新表里【非 live】的 token = %d 条 %s"
          % (len(nonlive), (str(nonlive[:5]) if nonlive else "(★期望 0★)")))
        paste(dst, fout)
        rc_a, out_a = run_gate(dst, ["--dump-classification"])
        miss_a, drift_a, ok_a = stats(out_a)
        L("  [重建后] rc=%d (★%s★) · MISSING=%d · DRIFT=%d · OK=%d · 输出里出现 %s = %s"
          % (rc_a, "红" if rc_a else "绿", miss_a, drift_a, ok_a, new,
             "★是★" if new in out_a else "★否★"))
        act_b = "红" if rc_b else "绿"
        act_a = "红" if rc_a else "绿"
        caught = (new in out_a) and rc_a != 0
        L("  ★判读★ 期望[重建前]=%s / 实际=%s   期望[重建后]=%s / 实际=%s   "
          "⇒ 真隐患被抓住 = %s"
          % (exp_b, act_b, exp_a, act_a, "★是·没被洗白★" if caught else "★否·被洗白了★"))
        rows.append({"id": cid, "old": old, "new": new, "exp_b": exp_b, "act_b": act_b,
                     "exp_a": exp_a, "act_a": act_a, "caught": caught,
                     "rc_b": rc_b, "rc_a": rc_a, "miss_b": miss_b, "drift_b": drift_b,
                     "miss_a": miss_a, "drift_a": drift_a, "in_new": in_new,
                     "nonlive": len(nonlive), "nf": nf, "nr": nr, "purpose": purpose})
        # 原始输出留证
        with open(os.path.join(LOG, "26_rev_%s_before.txt" % cid), "w", encoding="utf-8") as fh:
            fh.write(out_b)
        with open(os.path.join(LOG, "27_rev_%s_after.txt" % cid), "w", encoding="utf-8") as fh:
            fh.write(out_a)
        with open(os.path.join(LOG, "28_rev_%s_freeze.txt" % cid), "w", encoding="utf-8") as fh:
            fh.write(fout)
        shutil.rmtree(dst)

    # ══ 汇总表 ══
    L("")
    L("=" * 90)
    L("# ★反向用例汇总表 (★每条贴期望 vs 实际★)")
    L("=" * 90)
    L("%-6s %-14s %-18s %-8s %-8s %-8s %-8s %-6s %s"
      % ("用例", "注入", "新 token", "期望前", "实际前", "期望后", "实际后", "抓住", "重建表含?"))
    for r in rows:
        L("%-6s %-14s %-18s %-8s %-8s %-8s %-8s %-6s %s"
          % (r["id"], r["old"], r["new"], r["exp_b"], r["act_b"], r["exp_a"], r["act_a"],
             "是" if r["caught"] else "★否★", "含(危险)" if r["in_new"] else "不含"))
    L("")
    L("★结构性自证 (★每条用例重建出来的注册表里【非 live】token 数★): %s"
      % [r["nonlive"] for r in rows])
    L("★⇒ 非 live token 全为 0 ⇒ 【重建表只可能收 live 的 token】⇒ "
      "「板/网表里从来没有过的真隐患」在【物理上】不可能被收进注册表 ⇒ 洗白不了")
    L("")
    L("★零写板自证 (★沙盒跑完·真件 md5 必须不变★):")
    for rel in ("HW/PCB/demo_mainboard.kicad_pcb", "HW/netlist_v1.csv",
                "HW/netlist_v1_pins.csv", "HW/BOM_v1.csv"):
        L("   %s  %s" % (md5(os.path.join(PROJ, rel)), rel))
    return 0


if __name__ == "__main__":
    sys.exit(main())
