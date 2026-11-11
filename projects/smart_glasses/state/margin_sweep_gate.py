#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★margin_sweep_gate.py —— ★**margin 扫描的晋级闸** (★2026-11-11 08:3x 落地★)

# ★★★★★**★为什么要有这个闸 (★06:24 那条播报留下的坑★)★★★★** ★★★
   ★**播报里写的是**: "margin 0.015625 + 0.0078125 ⇒ unc 45→42 ⇒ 看着是改善"
   ★**但实测**: ★**unc 变少的同时, 差分腿 `CSI_D0_D0_P` 从【已连通】退成【未连通】**
     ⇒ ★**"unc 变少"根本不代表板子变好** ⇒ ★**只看 unc 会把坏板放行** ★★
   ★★**⇒ ⇒ 本闸把这条判据【写死在扫描的出口】, 不许靠人记得** ★★

# ★★★★★**★判据的【唯一实现】是谁 (★口径纪律★)★★★★** ★★★
   ★**不复写第二份判据** ⇒ ★**直接 `import compare_arm_official` 的名单制判据** ★★
     (★那已经是 v44 / v46 / _reroute2 三次事故后的名单制版本: 退铜名单 / 差分死腿 /
      逐网孤岛 / DRC=0 / unc·零铜网·差分单边零铜不许变差★)
   ★★**⇒ "unc 变少 ≠ 板子更好" 这条不是新判据, 是【既有判据的必然推论】⇒ ⇒ 不需要第二份定义** ★★

# ★★★**铁律: 规则同源 (★11-10 14:5x 踩过★)★★★ ★★★
   ★**所有板 (官方 + 每个变体) 一律先搬到同一个临时目录, 各配【同一份 .kicad_pro】★**
     ⇒ ★**再跑 fresh DRC** ⇒ ⇒ 双方规则必须同源, 否则"基线更差"是假的 ★★
   ★★**⇒ 并且闸会断言"官方板 fresh DRC == 0" ⇒ 规则漂移当场爆炸, 不许静默** ★★

用法:
  python3 state/margin_sweep_gate.py --official <官方板> --pro <kicad_pro> \
      --label off_m0.015625=/path/a.kicad_pcb --label off_m0=/path/b.kicad_pcb \
      [--report <报告.md>]
  python3 state/margin_sweep_gate.py --self-test
退出码: 0 = 没有变体够格晋级 (★正常: 扫描白扫★) · 10 = 有变体通过闸 (★要人工接手★) · 2 = 用法错
"""
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

import compare_arm_official as CAO  # ★**判据的唯一实现**


def fresh_drc(pcb, out_json, cwd=PROJ):
    """★跑一次 fresh DRC (★severity error+warning★) ⇒ 返回 (viol, unc, rc)"""
    if os.path.exists(out_json):
        os.remove(out_json)
    rc = subprocess.run(
        ["bash", "state/kicad.sh", "pcb", "drc", "--output", out_json,
         "--severity-error", "--severity-warning", "--format", "json", pcb],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=cwd).returncode
    try:
        d = json.load(open(out_json, encoding="utf-8"))
    except Exception:
        return 999, 999, rc
    return len(d.get("violations") or []), len(d.get("unconnected_items") or []), rc


def stage(src, dstdir, pro, name="board.kicad_pcb"):
    """★把板 + 【同一份 .kicad_pro】搬到临时目录 ⇒ DRC 规则同源 ★"""
    os.makedirs(dstdir, exist_ok=True)
    dst = os.path.join(dstdir, name)
    shutil.copyfile(src, dst)
    if pro and os.path.exists(pro):
        shutil.copyfile(pro, os.path.join(dstdir, "board.kicad_pro"))
    return dst


def judge_one(label, src, off_staged, off_json, pro, workdir):
    """★判一个变体 ⇒ 返回 dict (含判据全部指标 + 名单)"""
    d = os.path.join(workdir, "cand_%s" % label)
    dst = stage(src, d, pro)
    j = os.path.join(d, "board.drc.json")
    dv, du, _ = fresh_drc(dst, j)
    cm, om = CAO.compare_paths(dst, off_staged, j, off_json)
    verdict, why = CAO.decide(cm, om)
    # ★★**"unc 变少 ≠ 板子更好" 的直接证据: 哪些网【断了】(官方 0 项 ⇒ 候选 >0 项)★★
    broken = sorted(n for n in set(cm.get("net_unc", {})) | set(om.get("net_unc", {}))
                    if cm.get("net_unc", {}).get(n, 0) > om.get("net_unc", {}).get(n, 0))
    # ★★**哪些网【新连上了】(候选 0 项 ⇒ 官方 >0 项)★★
    newly = sorted(n for n in set(cm.get("net_unc", {})) | set(om.get("net_unc", {}))
                   if cm.get("net_unc", {}).get(n, 0) == 0 and om.get("net_unc", {}).get(n, 0) > 0)
    return {
        "label": label, "src": src, "seg": cm.get("seg"), "via": cm.get("via"),
        "drc": cm.get("drc"), "unc": cm.get("unc"),
        "zero_copper": cm.get("zero_copper"), "diff_half": cm.get("diff_half"),
        "diff_over": cm.get("diff_over"), "parity": cm.get("parity"),
        "dead": cm.get("dead", []), "gain": cm.get("gain", []),
        "pair_reg": cm.get("pair_reg", []), "island_reg": cm.get("island_reg", []),
        "broken_nets": broken, "newly_connected": newly,
        "verdict": verdict, "why": why,
        "official": {"seg": om.get("seg"), "via": om.get("via"), "drc": om.get("drc"),
                     "unc": om.get("unc"), "zero_copper": om.get("zero_copper"),
                     "diff_half": om.get("diff_half")},
    }


def print_table(rows):
    print("═══ margin 扫描晋级闸 (★名单制判据 · 唯一实现 = compare_arm_official.py★) ═══")
    hdr = ("%-18s %8s %6s %6s %9s %10s %10s %8s %8s"
           % ("变体", "段", "DRC", "unc", "零铜网", "差分单边", "退铜网", "死腿对", "孤岛增"))
    print(hdr)
    for r in rows:
        print("%-18s %8s %6s %6s %9s %10s %10s %8s %8s"
              % (r["label"], r["seg"], r["drc"], r["unc"], r["zero_copper"],
                 r["diff_half"], len(r["dead"]), len(r["pair_reg"]),
                 len(r["island_reg"])))
    for r in rows:
        print("── %s ⇒ ★**%s**" % (r["label"], r["verdict"]))
        print("   ★新连上 %d 网: %s" % (len(r["newly_connected"]),
                                        ", ".join(r["newly_connected"][:14]) or "-"))
        print("   ★★断腿 %d 网: %s" % (len(r["broken_nets"]),
                                       ", ".join(r["broken_nets"][:14]) or "-"))
        if r["dead"]:
            print("   ★退铜名单: %s" % ", ".join(r["dead"][:14]))
        if r["pair_reg"]:
            print("   ★★差分死腿: %s" % ", ".join(r["pair_reg"][:10]))
        if r["island_reg"]:
            print("   ★逐网孤岛变多: %s" % ", ".join(r["island_reg"][:14]))
        for w in r["why"]:
            print("     · %s" % w)


def write_report(rows, path, official):
    with open(path, "w", encoding="utf-8") as f:
        f.write("# margin 扫描晋级闸报告 (%s)\n\n" % time.strftime("%F %T"))
        f.write("- 官方板: `%s`\n" % official)
        f.write("- 判据: `state/compare_arm_official.py` (★名单制 · 唯一实现★)\n")
        f.write("- ★**unc 变少 ≠ 板子更好 ⇒ 断腿名单 / 差分死腿 / 逐网孤岛 三条硬指标同时看**\n\n")
        f.write("| 变体 | 段 | DRC | unc | 零铜网 | 差分单边零铜 | 退铜网 | 差分死腿 | 孤岛变多 | 判定 |\n")
        f.write("|---|---|---|---|---|---|---|---|---|---|\n")
        for r in rows:
            f.write("| %s | %s | %s | %s | %s | %s | %s | %s | %s | **%s** |\n"
                    % (r["label"], r["seg"], r["drc"], r["unc"], r["zero_copper"],
                       r["diff_half"], len(r["dead"]), len(r["pair_reg"]),
                       len(r["island_reg"]), r["verdict"]))
        f.write("\n")
        for r in rows:
            f.write("## %s ⇒ %s\n\n" % (r["label"], r["verdict"]))
            f.write("- 新连上: %s\n" % (", ".join(r["newly_connected"]) or "-"))
            f.write("- ★★断腿: %s\n" % (", ".join(r["broken_nets"]) or "-"))
            f.write("- 退铜名单: %s\n" % (", ".join(r["dead"]) or "-"))
            f.write("- 差分死腿: %s\n" % (", ".join(r["pair_reg"]) or "-"))
            f.write("- 逐网孤岛变多: %s\n" % (", ".join(r["island_reg"]) or "-"))
            for w in r["why"]:
                f.write("- 理由: %s\n" % w)
            f.write("\n")


# ══════════════════ 自测 (★必须带【故意改坏 ⇒ 必须被抓到】的反向用例★) ══════════════════
def self_test(fast=False):
    assert len(CAO.PAIRS) >= 20, "★差分对清单只加载到 %d 对 ⇒ 闸失效" % len(CAO.PAIRS)
    print("✔ 差分对清单加载到 %d 对" % len(CAO.PAIRS))
    OFF = dict(seg=18092, via=433, drc=0, unc=45, zero_copper=24, diff_half=11,
               diff_over=0, dead=[], gain=[], pair_reg=[], island_reg=[], parity=True)
    # ① ★**unc 变少 + 零铜网变少, 但打死一条差分腿 ⇒ 必须拒** (★就是 m0.015625 的形态★)
    FAKE = dict(OFF, unc=42, zero_copper=23, dead=["FSIN_OUT"],
                pair_reg=["CSI_D0_D0_P/CSI_D0_D0_N"], island_reg=["CSI_D0_D0_P"])
    v, why = CAO.decide(FAKE, OFF)
    assert v == "REJECT", "★★unc 变少但打死差分腿 ⇒ 必须被拒"
    assert any("差分" in w or "孤岛" in w for w in why), "★理由要点名差分/孤岛: %s" % why
    print("✔ unc 45→42 但打死差分腿 ⇒ 拒 (★这就是'unc 变少≠板子更好'★)")
    # ② ★**纯 unc 变好 + DRC 非 0 ⇒ 必须拒**
    v, why = CAO.decide(dict(OFF, unc=42, zero_copper=23, drc=16), OFF)
    assert v == "REJECT", "★DRC≠0 必须拒"
    print("✔ unc 变少但 DRC=16 ⇒ 拒")
    # ③ ★**真变好 (退铜0 / 死腿0 / 孤岛0 / DRC0 / unc 变少) ⇒ 必须放行** (★不许把好板也拒了★)
    GOOD = dict(OFF, unc=42, zero_copper=23, dead=[], gain=["JTAG_TDI"],
                pair_reg=[], island_reg=[], net_unc={})
    v, why = CAO.decide(GOOD, OFF)
    assert v == "ACCEPT", "★真变好必须放行: %s" % why
    print("✔ 真变好 ⇒ 放行 (★闸不许只会拒★)")
    # ④ ★**端到端: 实测坏案例 (m0.015625 变体) 必须被拒, 且必须点名 CSI_D0_D0_P** ★
    #    ★★**--self-test-fast 跳过本项** (★它要跑 fresh DRC ⇒ 慢 ⇒ 不适合进每日巡检★)
    if fast:
        print("★ --self-test-fast ⇒ 跳过端到端 (★要 fresh DRC★)")
        print("ALL TESTS PASS")
        return
    bad = "/tmp/snapfix/out_off_m0.015625_s0.kicad_pcb"
    off = os.path.join(PROJ, "state", ".lastgood",
                        "board_nostub_loose_unc45_20261106_0705.kicad_pcb")
    if os.path.exists(bad) and os.path.exists(off):
        wd = "/tmp/_msgate_selftest"
        shutil.rmtree(wd, ignore_errors=True)
        os.makedirs(wd, exist_ok=True)
        pro = "/tmp/snapfix/offboard_in.kicad_pro"
        off_staged = stage(off, os.path.join(wd, "official"), pro)
        oj = os.path.join(wd, "official", "board.drc.json")
        fresh_drc(off_staged, oj)
        r = judge_one("off_m0.015625", bad, off_staged, oj, pro, wd)
        assert r["verdict"] == "REJECT", "★★实测坏案例 m0.015625 必须被拒: %s" % r["why"]
        blob = " ".join(r["dead"] + r["pair_reg"] + r["island_reg"] + r["broken_nets"])
        assert "CSI_D0_D0_P" in blob, "★必须点名 CSI_D0_D0_P: %s" % blob
        print("✔ 端到端: 实测坏案例 m0.015625 被拒 (断腿 %s)"
              % ", ".join(r["broken_nets"][:6]))
        print("   ★unc %s→%s · DRC %s · 退铜 %s · 死腿 %s"
              % (r["official"]["unc"], r["unc"], r["drc"], len(r["dead"]),
                 len(r["pair_reg"])))
    else:
        print("⚠️ 实测坏案例不在 /tmp/snapfix ⇒ 跳过端到端 (板子已清?)")
    print("ALL TESTS PASS")


def main():
    a = sys.argv[1:]
    if a and a[0] == "--self-test":
        self_test()
        return 0
    if a and a[0] == "--self-test-fast":
        self_test(fast=True)
        return 0
    official = None
    pro = None
    report = None
    pairs = []
    i = 0
    while i < len(a):
        if a[i] == "--official":
            official = a[i + 1]; i += 2
        elif a[i] == "--pro":
            pro = a[i + 1]; i += 2
        elif a[i] == "--report":
            report = a[i + 1]; i += 2
        elif a[i] == "--label":
            pairs.append(a[i + 1]); i += 2
        else:
            print("❌ 未知参数: %s" % a[i]); return 2
    if not official or not pairs:
        print(__doc__)
        return 2
    workdir = "/tmp/_margin_gate_%d" % os.getpid()
    os.makedirs(workdir, exist_ok=True)
    off_staged = stage(official, os.path.join(workdir, "official"), pro)
    oj = os.path.join(workdir, "official", "board.drc.json")
    dv, du, _ = fresh_drc(off_staged, oj)
    if dv != 0:
        print("★★**官方板 fresh DRC = %d (必须 0) ⇒ 规则没同源 / 基线已脏 ⇒ 闸门拒绝工作**"
              % dv)
        print("   (★11-10 铁律: 归档板必须连 .kicad_pro 一起存★)")
        return 2
    print("✔ 官方板 fresh DRC = 0 · unc %s (规则同源已确认)" % du)
    rows = []
    for spec in pairs:
        label, _, path = spec.partition("=")
        if not path:
            label, path = os.path.basename(spec), spec
        if not os.path.exists(path):
            print("⚠️ 变体不存在: %s (%s) ⇒ 跳过" % (label, path))
            continue
        rows.append(judge_one(label, path, off_staged, oj, pro, workdir))
    if not rows:
        print("❌ 没有可判的变体")
        return 2
    print_table(rows)
    if report:
        write_report(rows, report, official)
        print("\n★ 报告: %s" % report)
    jsonout = os.path.join(workdir, "rows.json")
    with open(jsonout, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=1)
    print("★ 机读结果: %s" % jsonout)
    acc = [r for r in rows if r["verdict"] == "ACCEPT"]
    if acc:
        print("★★**有变体过闸: %s ⇒ 要人工接手**" % ", ".join(r["label"] for r in acc))
        return 10
    print("★ 没有变体够格晋级 (★扫描白扫: margin 这个杠杆到此为止★)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
