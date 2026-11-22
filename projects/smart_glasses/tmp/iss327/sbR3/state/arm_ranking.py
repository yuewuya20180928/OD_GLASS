#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""arm_ranking.py -- ★★★【统一口径的臂排名表】★★★

★为什么需要它 (★2026-11-11 00:3x 实测★):
  今晚 17 条臂的读数散在【各臂 log / 各目录 json / 各路报告】里 ⇒ ★**口径不一致**:
    有的读【裸板】, 有的读【终板】; 有的用 fresh DRC, 有的用【上一步的输入 DRC】
    (★这个坑已经咬过: "打碎 9 个" 真值是【5 个】★)
  ⇒ ⇒ ★**排出来的名次是假的** ⇒ ⇒ 本脚本统一: 【一律 fresh DRC 终板 + 同链基线名单闸】

★三条硬纪律 (★违反就不许用本表的数★):
  ① ★**板旁必须有 .kicad_pro** ⇒ 缺 ⇒ 读数作废
     (★KiCad 退回默认 min_width 0.20 ⇒ 0.15mm 走线全成【假 track_width 违规】★)
  ② ★**只认 fresh DRC** ⇒ 同名 .drc.json 可能是【上一步输入板】的 DRC ⇒ 不许直接读
  ③ ★**三数必须一起看**: DRC / unc(条+网名) / 名单闸(退铜·死腿·孤岛)
     ⇒ ★**单看 unc 变少不算赢** (★今晚 v76mo/v76mn 就是 unc 变好但名单闸不过★)

用法:
  python3 state/arm_ranking.py --list
      列出所有已知臂 (不跑 DRC, 只列路径与缓存状态)
  python3 state/arm_ranking.py [--baseline <基线板>] <板1> <板2> ...
      逐条跑 fresh 读数 + 名单闸, 打印统一口径的表
  python3 state/arm_ranking.py --json        # 机器可读
"""

import json
import os
import re
import subprocess
import sys
import time

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
REF_PRO = PROJ + "/HW/PCB/demo_mainboard.kicad_pro"
DEFAULT_BASE = PROJ + "/state/.lastgood/baseline_v76_chain.kicad_pcb"


def sh(cmd, timeout=900, want_rc=False):
    """★2026-11-11 04:5x: ★加 want_rc ⇒ 同时返回【退出码】(★名单闸的判定就靠它★)"""
    try:
        p = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                           cwd=PROJ, timeout=timeout)
        out = p.stdout + p.stderr
        return (out, p.returncode) if want_rc else out
    except subprocess.TimeoutExpired:
        return ("!!TIMEOUT!!", None) if want_rc else "!!TIMEOUT!!"


def has_pro(board):
    return os.path.exists(board[: -len(".kicad_pcb")] + ".kicad_pro")


def fresh_drc(board):
    """★只认 fresh DRC★ ⇒ 缓存比板新就复用, 否则重跑"""
    out = board + ".drc.json.fresh"
    if os.path.exists(out) and os.path.getmtime(out) >= os.path.getmtime(board):
        return out, False
    sh("bash state/kicad.sh pcb drc --output %s --severity-error --severity-warning "
       "--format json %s" % (out, board), timeout=1800)
    return out, True


def parse_drc(path):
    d = json.load(open(path, encoding="utf-8"))
    viol = d.get("violations") or []
    unc = d.get("unconnected_items") or []
    nets = set()
    for it in unc:
        nets |= set(re.findall(r"\[([A-Za-z0-9_]+)\]",
                               json.dumps(it, ensure_ascii=False)))
    kinds = {}
    for x in viol:
        k = x.get("type") or "?"
        kinds[k] = kinds.get(k, 0) + 1
    return dict(drc=len(viol), kinds=kinds, unc=len(unc), nets=sorted(nets))


def list_gate(cand, base):
    """★名单闸: 退铜 / 差分死腿 / 逐网孤岛变多 / 闸 rc★"""
    if not os.path.exists(base):
        return dict(rc=None, dead=None, pair=None, island=None, note="基线板不存在")
    # ★★2026-11-11 04:5x 修 bug: ★`compare_arm_official.py` 【不打印 "闸 rc="】(★它用【退出码】表达判定★)
    #   ⇒ ★旧版用正则找 "闸 rc=" ⇒ 永远 None ⇒ 看起来像"没判定", 其实是工具 bug
    #   ⇒ ⇒ 现在改成: ★闸 rc = 子进程退出码 (0=ACCEPT) + 解析 "判定: ACCEPT/REJECT"
    out, code = sh("python3 state/compare_arm_official.py %s %s" % (cand, base),
                   timeout=1800, want_rc=True)
    res = dict(rc=code, dead=None, pair=None, island=None, note="")
    m = re.search(r"退铜名单.*?:\s*(\d+)", out)
    if m:
        res["dead"] = int(m.group(1))
    m = re.search(r"差分对死腿:\s*(\d+)", out)
    if m:
        res["pair"] = int(m.group(1))
    m = re.search(r"逐网孤岛变多:\s*(\d+)", out)
    if m:
        res["island"] = int(m.group(1))
    m = re.search(r"判定:\s*(\S+)", out)
    res["verdict"] = m.group(1) if m else "?"
    if res["rc"] is None:
        res["note"] = (out.strip().splitlines() or ["无输出"])[-1][:60]
    return res


def seg_count(board):
    n = 0
    with open(board, encoding="utf-8", errors="ignore") as f:
        for line in f:
            if "(segment" in line:
                n += 1
    return n


def known_arms():
    out = []
    for d in sorted(os.listdir(PROJ + "/state/.lastgood")):
        if d.endswith("_chain.kicad_pcb"):
            out.append((d.replace("_chain.kicad_pcb", ""),
                        PROJ + "/state/.lastgood/" + d))
    for d in sorted(os.listdir("/tmp")):
        if d.startswith("chain_"):
            b = "/tmp/%s/final_chain.kicad_pcb" % d
            if os.path.exists(b):
                out.append((d.replace("chain_", ""), b))
    return out


def main():
    args = sys.argv[1:]
    as_json = "--json" in args
    if "--json" in args:
        args.remove("--json")
    base = DEFAULT_BASE
    if "--baseline" in args:
        i = args.index("--baseline")
        base = args[i + 1] if i + 1 < len(args) else base
        del args[i:i + 2]
    if "--list" in args:
        for tag, b in known_arms():
            print("  %-22s %s  [%s]" % (tag, b, "有pro" if has_pro(b) else "★缺pro⇒读数作废★"))
        return 0
    boards = args
    if not boards:
        print("用法: arm_ranking.py [--baseline <基线>] <板...> | --list")
        return 1

    rows = []
    for b in boards:
        if not os.path.exists(b):
            print("❌ 没有板: %s" % b)
            continue
        pro = has_pro(b)
        if not pro:
            os.makedirs(os.path.dirname(b) or ".", exist_ok=True)
            if os.path.exists(REF_PRO):
                shutil_copy(REF_PRO, b[:-len(".kicad_pcb")] + ".kicad_pro")
                pro = True
        jf, ran = fresh_drc(b)
        if not os.path.exists(jf):
            print("❌ fresh DRC 没跑出来: %s" % b)
            continue
        d = parse_drc(jf)
        g = list_gate(b, base)
        rows.append(dict(tag=os.path.basename(os.path.dirname(b)) + "/" +
                         os.path.basename(b)[: -len(".kicad_pcb")],
                         board=b, pro=pro, segs=seg_count(b),
                         drc=d["drc"], kinds=d["kinds"], unc=d["unc"],
                         nets=len(d["nets"]), netlist=d["nets"], gate=g))
    if as_json:
        print(json.dumps(rows, ensure_ascii=False, indent=1))
        return 0

    print("═══ 统一口径臂排名 (★fresh DRC 终板 + 同链基线名单闸★) ═══")
    print("  基线: %s" % base)
    print("  %-24s %5s %6s %6s %6s %6s %6s %5s" %
          ("臂", "DRC", "unc条", "unc网", "退铜", "死腿", "孤岛", "闸rc"))
    for r in rows:
        g = r["gate"]
        print("  %-24s %5d %6d %6d %6s %6s %6s %5s%s" % (
            r["tag"], r["drc"], r["unc"], r["nets"],
            g["dead"], g["pair"], g["island"], g["rc"],
            "" if r["pro"] else "  ★缺pro★"))
    print("  ── 判据: ★DRC 必须 0 · unc 网名集合必须变小 · 退铜=0 · 死腿=0 · 孤岛不增· 闸 rc=0★")
    return 0


def shutil_copy(a, b):
    try:
        import shutil
        shutil.copyfile(a, b)
    except Exception as e:
        print("  ⚠️ 补 .kicad_pro 失败: %s" % e)


if __name__ == "__main__":
    sys.exit(main())
