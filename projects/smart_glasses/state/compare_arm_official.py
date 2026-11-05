#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★compare_arm_official.py —— ★**臂板 vs 官方板 的晋级判据 (独立脚本)**

★★★★★**为什么必须独立写 (2026-11-06 01:4x 实测事故)**:
   原 `auto_promote_when_done.sh` 的判据只有 **(unconnected, DRC)** 两项
   ⇒ ⇒ v44_R (unconn 55 < 57, DRC 0 == 0) 被判"更好" ⇒ ★**晋级成了官方板**
   ⇒ ⇒ 但实测: v44 把 **9 个网打成零铜** (含 4 条差分 _SRC 腿), 只救回 7 个
      ⇒ ★★**差分对净 -1 / 普通信号网净 -2** ⇒ ★**官方板实际变差了**
   ⇒ ⇒ ★**"只看 ratsnest 数量"会被"把有铜的腿砍成零铜"骗**
   ⇒ ⇒ **Δ 数字也会骗**: v44 的 "DSI_D0_D0 Δ 从 76.197 降到 1.612" 是
      ★**把配平铜砍掉、让一侧归零换来的** (审计器不算零铜对 ⇒ 数字变好, 板子更烂)

★**判据 (★故意严格)**: 候选板必须
  ① DRC 必须为 0
  ② 在 {unconnected, 零铜网数(≥2焊盘), 差分单边零铜对数, 差分Δ超差对数} 上
     ★**任何一项都不得比官方板差**
  ③ 且至少一项严格变好
⇒ ★**"拿 Δ 超差换 ratsnest 减少"这种交易会被直接拒掉**

用法:
  python3 state/compare_arm_official.py <候选板> <官方板> [--drc-json 候选.json 官方.json]
  python3 state/compare_arm_official.py --self-test
退出码: 0 = 可晋级 · 1 = 不可晋级
"""
import json
import math
import os
import re
import subprocess
import sys

KICAD_SH = "state/kicad.sh"

# ★★**差分对清单从 diff_pair_audit.py 里现抠** ⇒ ★**两边永不走样**
# ★★**路径**: state/ → smart_glasses/ → projects/ → workspace/ ⇒ ★**要退三级**
#   (★11-06 01:5x 实测踩坑: 只退两级 ⇒ 找到 .../projects/tools ⇒ ★**PAIRS 加载成空**
#    ⇒ ★**差分指标恒为 0** ⇒ ★**闸门会把"把差分打成单边零铜"的坏板放行** ⇒ ⇒ 必须有断言)
_AUDIT = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "..", "..", "tools", "diff_pair_audit.py"))


def load_pairs():
    try:
        src = open(_AUDIT, encoding="utf-8").read()
    except Exception as e:
        raise RuntimeError("★**读不到差分对清单** (%s) ⇒ 差分指标会恒为 0 ⇒ 闸门失效" % _AUDIT)
    m = re.search(r"PAIRS\s*=\s*\[(.*?)\]", src, re.S)
    if not m:
        raise RuntimeError("★**差分对清单里没有 PAIRS** ⇒ 差分指标会恒为 0 ⇒ 闸门失效")
    out = re.findall(r'\(\s*"([^"]+)"\s*,\s*"([^"]+)"\s*\)', m.group(1))
    if len(out) < 20:
        raise RuntimeError("★**差分对只读到 %d 对 (应 ≥20) ⇒ 闸门失效**" % len(out))
    return out


PAIRS = load_pairs()


# ══════════════════ 板文件解析 ══════════════════
def board_metrics(path):
    """★只读板文件 ⇒ 算出晋级判据要用的全部指标"""
    seg = 0
    via = 0
    net_len = {}          # 网名 -> 走线总长 mm
    net_seg = {}          # 网名 -> 段数
    pad_cnt = {}          # 网名 -> 焊盘数
    all_nets = set()
    cur = None            # 'seg' | 'via' | 'pad' | None
    cur_net = None
    x1 = y1 = x2 = y2 = None
    for ln in open(path, encoding="utf-8", errors="ignore"):
        s = ln.strip()
        if s == "(segment":
            cur = "seg"; cur_net = None
            x1 = y1 = x2 = y2 = None
            continue
        if s == "(via":
            cur = "via"; cur_net = None
            continue
        if s.startswith("(pad ") or s == "(pad":
            cur = "pad"; cur_net = None
            continue
        if cur:
            if s == ")":
                if cur == "seg":
                    seg += 1
                    if cur_net:
                        net_seg[cur_net] = net_seg.get(cur_net, 0) + 1
                        if None not in (x1, y1, x2, y2):
                            net_len[cur_net] = net_len.get(cur_net, 0.0) + \
                                math.hypot(x2 - x1, y2 - y1)
                elif cur == "via":
                    via += 1
                cur = None
                continue
            m = re.match(r'\(net "([^"]+)"\)', s)
            if m:
                cur_net = m.group(1)
                all_nets.add(cur_net)
                if cur == "pad":
                    pad_cnt[cur_net] = pad_cnt.get(cur_net, 0) + 1
                continue
            if cur == "seg":
                m = re.match(r"\(start ([-\d.]+) ([-\d.]+)\)", s)
                if m:
                    x1, y1 = float(m.group(1)), float(m.group(2))
                m = re.match(r"\(end ([-\d.]+) ([-\d.]+)\)", s)
                if m:
                    x2, y2 = float(m.group(1)), float(m.group(2))
    # ★零铜网: ★**只算 ≥2 焊盘的** (★单点网如 NC_* / PGND 本来就不该有铜)
    zero_copper = 0
    for n, npad in pad_cnt.items():
        if npad >= 2 and net_seg.get(n, 0) == 0:
            zero_copper += 1
    # ★差分对统计
    half = 0     # ★单边零铜 (只布了一半) 的对数
    over = 0     # ★双边有铜但 Δ>0.13mm 的对数
    for p, n in PAIRS:
        lp = net_len.get(p)
        ln_ = net_len.get(n)
        if lp is None or ln_ is None or net_seg.get(p, 0) == 0 or net_seg.get(n, 0) == 0:
            half += 1
            continue
        if abs(lp - ln_) > 0.13:
            over += 1
    return {"seg": seg, "via": via, "zero_copper": zero_copper,
            "diff_half": half, "diff_over": over}


def drc_metrics(pcb, json_path=None):
    """★跑 KiCad DRC 取违规数 + 未连接数 (★取证失败 ⇒ 999 ⇒ 必被拒)"""
    if json_path and os.path.exists(json_path):
        pass
    else:
        json_path = "/tmp/_cmp_gate_%d.json" % os.getpid()
        subprocess.run(["bash", KICAD_SH, "pcb", "drc", "--output", json_path,
                        "--severity-error", "--severity-warning", "--format", "json", pcb],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        d = json.load(open(json_path))
        return (len(d.get("violations") or []), len(d.get("unconnected_items") or []))
    except Exception:
        return (999, 999)


# ══════════════════ 判据 (★纯函数, 好测) ══════════════════
# ★**越大越好的指标** (候选不得变差, 且至少一项变好)
HARD = ["unc", "zero_copper", "diff_half", "diff_over"]


def decide(cand, off):
    """★返回 (verdict, 理由列表)"""
    reasons = []
    if cand.get("drc", 999) != 0:
        reasons.append("★**DRC=%d (必须 0)**" % cand.get("drc", 999))
    if cand.get("drc", 999) > off.get("drc", 0):
        reasons.append("DRC 变差 %s→%s" % (off.get("drc"), cand.get("drc")))
    for k in HARD:
        c = cand.get(k, 999)
        o = off.get(k, 0)
        if c > o:
            reasons.append("★**%s 变差 %s→%s (不许拿别的换)**" % (k, o, c))
    better = [k for k in ("unc", "zero_copper", "diff_half", "diff_over", "drc")
              if cand.get(k, 999) < off.get(k, 999)]
    if not better and not reasons:
        reasons.append("★**没有任何指标严格变好 ⇒ 不晋级**")
    if reasons:
        return "REJECT", reasons
    return "ACCEPT", ["变好项: %s" % ", ".join(better)]


# ══════════════════ 自测 (★用 2026-11-06 实测的真实数据) ══════════════════
def self_test():
    # ★★**先断言 PAIRS 真的加载到了** (★否则差分指标恒 0 ⇒ 闸门形同虚设)
    assert len(PAIRS) >= 20, "★**PAIRS 只加载到 %d 对 ⇒ 差分指标恒 0**" % len(PAIRS)
    print("✔ 差分对清单加载到 %d 对 (来自 %s)" % (len(PAIRS), os.path.basename(_AUDIT)))
    # ★★**v37_R (老官方) vs v44_R (差点被放行的那块)** —— ★实测值
    V37 = {"seg": 17018, "via": 408, "drc": 0, "unc": 57,
           "zero_copper": 26, "diff_half": 11, "diff_over": 3}
    V44 = {"seg": 13407, "via": 371, "drc": 0, "unc": 55,
           "zero_copper": 26, "diff_half": 12, "diff_over": 1}
    v, why = decide(V44, V37)
    assert v == "REJECT", "★★**v44 必须被拒** (它把差分对打成单边零铜), 实得 %s" % v
    print("✔ v44 被拒 (差分单边零铜 11→12 ⇒ ★拿 Δ 数字换 ratsnest 的交易被挡住): %s" % "; ".join(why))
    # 真变好 ⇒ 放行
    GOOD = dict(V37); GOOD["unc"] = 40; GOOD["zero_copper"] = 20
    v, why = decide(GOOD, V37)
    assert v == "ACCEPT", "★真变好必须放行, 实得 %s %s" % (v, why)
    print("✔ 真变好 ⇒ 放行")
    # 完全没变好 ⇒ 不放行
    v, why = decide(dict(V37), V37)
    assert v == "REJECT", "★无改善必须拒"
    print("✔ 无改善 ⇒ 拒")
    # DRC 非 0 ⇒ 拒
    B = dict(GOOD); B["drc"] = 3
    v, why = decide(B, V37)
    assert v == "REJECT", "★DRC 非 0 必须拒"
    print("✔ DRC≠0 ⇒ 拒")
    # 变差 ⇒ 拒
    W = dict(GOOD); W["unc"] = 99
    v, why = decide(W, V37)
    assert v == "REJECT", "★变差必须拒"
    print("✔ 任一硬指标变差 ⇒ 拒")
    print("ALL TESTS PASS")


def main():
    a = sys.argv[1:]
    if a and a[0] == "--self-test":
        self_test()
        return 0
    if len(a) < 2:
        print(__doc__)
        return 2
    cand_pcb, off_pcb = a[0], a[1]
    jc = jo = None
    if "--drc-json" in a:
        i = a.index("--drc-json")
        jc = a[i + 1] if len(a) > i + 1 else None
        jo = a[i + 2] if len(a) > i + 2 else None
    cm = board_metrics(cand_pcb)
    om = board_metrics(off_pcb)
    cm["drc"], cm["unc"] = drc_metrics(cand_pcb, jc)
    om["drc"], om["unc"] = drc_metrics(off_pcb, jo)
    verdict, why = decide(cm, om)
    print("═══ 臂板 vs 官方板 ═══")
    print("  %-14s %10s %10s" % ("指标", "候选", "官方"))
    for k, lbl in [("drc", "DRC违规"), ("unc", "unconnected"),
                   ("zero_copper", "零铜网(≥2焊盘)"), ("diff_half", "差分单边零铜"),
                   ("diff_over", "差分Δ超差"), ("seg", "走线段"), ("via", "过孔")]:
        print("  %-14s %10s %10s" % (lbl, cm.get(k), om.get(k)))
    print("  ── 判定: %s" % verdict)
    for w in why:
        print("     · %s" % w)
    return 0 if verdict == "ACCEPT" else 1


if __name__ == "__main__":
    sys.exit(main())
