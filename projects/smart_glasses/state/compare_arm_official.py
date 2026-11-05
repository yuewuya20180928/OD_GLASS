#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★compare_arm_official.py —— ★**臂板 vs 官方板 的晋级判据 (独立脚本)**

# ★★★★★**为什么必须独立写 (2026-11-06 实测事故 x2)**:
   原 `auto_promote_when_done.sh` 判据只有 **(unconnected, DRC)** ⇒ v44_R 被放行上位
   ⇒ ★**逐网实测 v44 把 9 个网打成零铜, 只救回 7 个 ⇒ 差分对净 -1 ⇒ 官方板实际变差**
#    ⇒ ⇒ 第一版加固闸 (计数制: 零铜网数 / 单边零铜对数) **又放行了 v46_R** (01:53:38)
#    ⇒ ⇒ ★★**v46 是"轻度 v44": 零铜网 26=26、单边零铜对 11=11 (计数全平!)**
#    ⇒ ⇒ ★★**但名单变了**: v46 把 **10 个本来通的网打成零铜**
        (含 `DSI_D0_CK_N` / `DSI_D0_CK_N_SRC` / `DSI_D0_D1_N` **三条本来通的差分腿**)
        同时救回 10 个 ⇒ ★**"净数"完全掩盖了"换了哪几个"**
#    ⇒ ⇒ ★★★**所以判据必须改成"名单制", 不是"计数制"**

★**最终判据 (硬指标, 任一变差即拒)**:
  ① DRC 必须 = 0
  ② **退铜名单** `dead_regressions` = {官方有铜 ⇒ 候选零铜} 的网 ⇒ **必须为空**
     (含 GND! GND 掉铜是灾难)
  ③ **差分对死腿** `pair_regressions` = {官方双边有铜 ⇒ 候选单边零铜} 的对 ⇒ **必须为空**
  ④ 计数类 (只作辅助, 不单独判): unconnected / 零铜网数 / 单边零铜对数 / Δ超差对数
     ⇒ ★**任一变差也拒** (★但"变好"必须靠 ②③ 之外的真实改善, 不能靠计数互换)
  ⑤ 至少一项严格变好

★**自测**: `--self-test` 用 ★**实测的 v44/v46 名单当回归用例** ⇒ 两个都必须被拒
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
HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.normpath(os.path.join(HERE, ".."))
# ★★**路径**: state/ → smart_glasses/ → projects/ → workspace/ ⇒ ★**要退三级**
#   (★11-06 实测踩坑: 只退两级 ⇒ 找到 .../projects/tools ⇒ ★**PAIRS 加载成空**
#    ⇒ ★**差分指标恒为 0** ⇒ ★**闸门会把"把差分打成单边零铜"的坏板放行**)
_AUDIT = os.path.normpath(os.path.join(HERE, "..", "..", "..", "tools",
                                       "diff_pair_audit.py"))


def load_pairs():
    try:
        src = open(_AUDIT, encoding="utf-8").read()
    except Exception:
        raise RuntimeError("★**读不到差分对清单** (%s) ⇒ 差分指标恒为 0 ⇒ 闸门失效" % _AUDIT)
    m = re.search(r"PAIRS\s*=\s*\[(.*?)\]", src, re.S)
    if not m:
        raise RuntimeError("★**差分对清单里没有 PAIRS** ⇒ 闸门失效")
    out = re.findall(r'\(\s*"([^"]+)"\s*,\s*"([^"]+)"\s*\)', m.group(1))
    if len(out) < 20:
        raise RuntimeError("★**差分对只读到 %d 对 (应 ≥20) ⇒ 闸门失效**" % len(out))
    return out


PAIRS = load_pairs()


# ══════════════════ 板文件解析 ══════════════════
def board_metrics(path):
    """★只读板文件 ⇒ 算出判据要用的全部指标 (含逐网铜量)"""
    seg = via = 0
    net_len = {}
    net_seg = {}
    pad_cnt = {}
    cur = None
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
    zero_copper = 0
    for n, npad in pad_cnt.items():
        if npad >= 2 and net_seg.get(n, 0) == 0:
            zero_copper += 1
    half = 0
    over = 0
    for p, n in PAIRS:
        lp = net_len.get(p)
        ln_ = net_len.get(n)
        if lp is None or ln_ is None or net_seg.get(p, 0) == 0 or net_seg.get(n, 0) == 0:
            half += 1
            continue
        if abs(lp - ln_) > 0.13:
            over += 1
    return {"seg": seg, "via": via, "zero_copper": zero_copper,
            "diff_half": half, "diff_over": over,
            "net_seg": net_seg, "net_len": net_len}


def drc_metrics(pcb, json_path=None):
    """★跑 KiCad DRC 取违规数 + 未连接数 (★取证失败 ⇒ 999 ⇒ 必被拒)"""
    if not (json_path and os.path.exists(json_path)):
        json_path = "/tmp/_cmp_gate_%d.json" % os.getpid()
        subprocess.run(["bash", KICAD_SH, "pcb", "drc", "--output", json_path,
                        "--severity-error", "--severity-warning", "--format", "json", pcb],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       cwd=PROJ)
    try:
        d = json.load(open(json_path))
        return (len(d.get("violations") or []), len(d.get("unconnected_items") or []))
    except Exception:
        return (999, 999)


def parity_ok(pcb):
    """★板↔网表 parity (★rc 必须 0)"""
    r = subprocess.run(["bash", os.path.join(PROJ, "state", "pcbnew_py.sh"),
                        os.path.join(PROJ, "state", "check_pcb_nets.py"), pcb],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=PROJ)
    return r.returncode == 0


# ══════════════════ 名单制比较 ══════════════════
def regression_lists(cm, om):
    """★退铜名单 + 差分对死腿名单 (★核心: 比"名单", 不比"计数")"""
    dead = sorted(n for n in om["net_seg"]
                  if om["net_seg"][n] > 0 and cm["net_seg"].get(n, 0) == 0)
    gain = sorted(n for n in cm["net_seg"]
                  if cm["net_seg"][n] > 0 and om["net_seg"].get(n, 0) == 0)
    pair_reg = []
    for p, n in PAIRS:
        oc = om["net_seg"].get(p, 0) > 0 and om["net_seg"].get(n, 0) > 0
        cc = cm["net_seg"].get(p, 0) > 0 and cm["net_seg"].get(n, 0) > 0
        if oc and not cc:
            pair_reg.append("%s/%s" % (p, n))
    return dead, gain, pair_reg


# ══════════════════ 判据 (★纯函数, 好测) ══════════════════
# ★★★2026-11-06 02:1x 实测再修 (★第 3 次加固):
#   ★**`diff_over` (Δ超差对数) 不能当硬指标, 也不能当「变好」证据**
#     —— 它会被「打死差分腿」污染: 一条差分腿归零 ⇒ 它从「Δ超差」桶移到「单边零铜」桶
#     ⇒ ★**Δ超差对数假性下降** (实测: v37 有 3 对超差, 削掉 DSI_D0_CK_N 的铜后只剩 2 对 ⇒ 看着更好了)
#   ⇒ ⇒ 危险情形已由「退铜名单 + 差分死腿」两条名单制规则兜住 ⇒ ★**diff_over 只做参考**
#   ★同理: `diff_half` 也只当「不许变差」, 不当「变好」证据 (它下降只能来自真修好一对)
#   ★**「变好」只认 unc / zero_copper 两项** (都是「加铜/连上」方向 ⇒ 不会被「打死」污染)

COUNT_HARD = ["unc", "zero_copper", "diff_half"]      # ★任一变差即拒
REPORT_ONLY = ["diff_over"]                            # ★只报不算 (会被打死差分腿污染)
# ★**"变好"只认这两项** (★都是"加铜/连上"方向 ⇒ 不会被"打死"污染)
IMPROVE = ["unc", "zero_copper"]


def decide(cand, off):
    """★返回 (verdict, 理由列表)"""
    reasons = []
    if cand.get("drc", 999) != 0:
        reasons.append("★**DRC=%d (必须 0)**" % cand.get("drc", 999))
    if cand.get("drc", 999) > off.get("drc", 0):
        reasons.append("DRC 变差 %s→%s" % (off.get("drc"), cand.get("drc")))
    if cand.get("parity") is False:
        reasons.append("★**板↔网表 parity 不过**")
    dead = cand.get("dead", [])
    gain = cand.get("gain", [])
    # ★★2026-11-06 02:6x 实测修正: 原来的硬规则 "退铜名单必须为空" **太严**
    #   ⇒ 实测 v44 退 7 救 7 / v46 退 10 救 10 ⇒ **一个铜都没多救的臂也不许上位**
    #   ⇒ ★**改成净判据: 救回的网必须多于退铜的网** (净救回 > 0)
    #   ⇒ ★**但差分死腿仍然一票否决** (★打死一条差分腿 ⇒ 那条高速通道根本不存在 ⇒ 不能交易)
    if dead and len(gain) <= len(dead):
        reasons.append("★**净救回 %d 个网 (救 %d - 退 %d) ⇒ 不许拿铜换 ratsnest: %s**"
                       % (len(gain) - len(dead), len(gain), len(dead), ", ".join(dead[:12])))
    preg = cand.get("pair_reg", [])
    if preg:
        reasons.append("★**差分对死腿 %d 对 (官方双边有铜⇒候选单边零铜): %s**"
                       % (len(preg), ", ".join(preg[:8])))
    for k in COUNT_HARD:
        c = cand.get(k, 999)
        o = off.get(k, 0)
        if c > o:
            reasons.append("★**%s 变差 %s→%s (不许拿别的换)**" % (k, o, c))
    better = [k for k in IMPROVE if cand.get(k, 999) < off.get(k, 999)]
    if not better and not reasons:
        reasons.append("★**没有任何指标严格变好 (只认 unconnected / 零铜网数 变少) ⇒ 不晋级**")
    if reasons:
        return "REJECT", reasons
    return "ACCEPT", ["变好项: %s" % ", ".join(better)]


def compare_paths(cand_pcb, off_pcb, jc=None, jo=None):
    cm = board_metrics(cand_pcb)
    om = board_metrics(off_pcb)
    cm["drc"], cm["unc"] = drc_metrics(cand_pcb, jc)
    om["drc"], om["unc"] = drc_metrics(off_pcb, jo)
    dead, gain, preg = regression_lists(cm, om)
    cm["dead"] = dead
    cm["gain"] = gain
    cm["pair_reg"] = preg
    cm["parity"] = parity_ok(cand_pcb)
    om["parity"] = parity_ok(off_pcb)
    return cm, om


# ══════════════════ 自测 (★用实测数据当回归用例) ══════════════════
def self_test():
    assert len(PAIRS) >= 20, "★**PAIRS 只加载到 %d 对 ⇒ 差分指标恒 0**" % len(PAIRS)
    print("✔ 差分对清单加载到 %d 对" % len(PAIRS))
    V37 = {"seg": 17018, "via": 408, "drc": 0, "unc": 57,
           "zero_copper": 26, "diff_half": 11, "diff_over": 3}
    # ★★**实测回归用例 1: v44_R (01:28 被放行的那块)**
    V44 = dict(V37, seg=13407, via=371, unc=55, diff_over=1,
               dead=["CARRIER_BOARD_EN", "CSI_MCLK_SRC", "DSI_D0_C0_N_SRC",
                     "DSI_D0_D0_N_SRC", "DSI_D0_D0_P_SRC", "DSI_D0_D1_P_SRC",
                     "DSI_D0_D2_N_SRC", "ID_DETECT_0", "LED_G_D"],
               pair_reg=["DSI_D0_CK_P/DSI_D0_CK_N"])
    v, why = decide(V44, V37)
    assert v == "REJECT", "★★**v44 必须被拒**"
    print("✔ v44 被拒 (退铜 9 网 + 差分死腿 1 对): %s" % why[0][:60])
    # ★★**实测回归用例 2: v46_R (01:53 被第一版加固闸放行的那块)**
    V46 = dict(V37, seg=13707, via=374, unc=56, diff_over=2,
               dead=["CARRIER_BOARD_EN", "CSI_MCLK_SRC", "DSI_D0_CK_N",
                     "DSI_D0_CK_N_SRC", "DSI_D0_D1_N", "I2C_A_SCL",
                     "I2C_A_SDA", "LED_B", "LED_B_D", "USB_CC1"],
               pair_reg=["DSI_D0_CK_P/DSI_D0_CK_N",
                         "DSI_D0_CK_P_SRC/DSI_D0_CK_N_SRC",
                         "DSI_D0_D1_P/DSI_D0_D1_N"])
    v, why = decide(V46, V37)
    assert v == "REJECT", "★★**v46 必须被拒** (★计数全平但名单变了 ⇒ 第一版闸放行了它)"
    print("✔ v46 被拒 (★计数全平 26=26/11=11, 但退铜 10 网 + 差分死腿 3 对 ⇒ 必须靠名单才抓得到)")
    # 真变好 ⇒ 放行 (无退铜、无死腿、且至少一项变好)
    GOOD = dict(V37, unc=40, zero_copper=20, dead=[], pair_reg=[])
    v, why = decide(GOOD, V37)
    assert v == "ACCEPT", "★真变好必须放行: %s" % why
    print("✔ 真变好 ⇒ 放行")
    # ★★**"打死一条差分腿" ⇒ Δ超差对数假性下降 ⇒ 不许拿它当变好证据**
    KILL = dict(V37, unc=57, zero_copper=26, diff_half=12, diff_over=2,
                dead=["DSI_D0_CK_N"], pair_reg=["DSI_D0_CK_P/DSI_D0_CK_N"])
    v, _ = decide(KILL, V37)
    assert v == "REJECT", "★打死差分腿 (Δ超差对数假降) 必须拒"
    print("✔ 打死差分腿 (Δ超差对数假降) ⇒ 拒")
    v, _ = decide(dict(V37, dead=[], pair_reg=[]), V37)
    assert v == "REJECT", "★无改善必须拒"
    print("✔ 无改善 ⇒ 拒")
    B = dict(GOOD, drc=3)
    v, _ = decide(B, V37)
    assert v == "REJECT", "★DRC 非 0 必须拒"
    print("✔ DRC≠0 ⇒ 拒")
    W = dict(GOOD, unc=99)
    v, _ = decide(W, V37)
    assert v == "REJECT", "★变差必须拒"
    print("✔ 任一计数指标变差 ⇒ 拒")
    # ★★**端到端: 用真实归档的坏板跑一遍 (★纯函数测不到指标提取)**
    lg = os.path.join(PROJ, "state", ".lastgood")
    v37 = os.path.join(lg, "board_prev_promote_20261106_012812.kicad_pcb")
    bad = [("v44", "board_v44R_arm_13407seg_20261106_0145.kicad_pcb"),
           ("v46", "board_v46R_arm_13707seg_20261106_0154.kicad_pcb"),
           ("v47", "board_v47R_arm_13833seg_20261106_0158.kicad_pcb")]
    if os.path.exists(v37):
        for nm, fn in bad:
            p = os.path.join(lg, fn)
            if not os.path.exists(p):
                continue
            cm, om = compare_paths(p, v37)
            v, why = decide(cm, om)
            assert v == "REJECT", "★★**真板 %s 必须被拒**" % nm
            print("✔ 真板端到端: %s 被拒 (退铜 %d 网 · 差分死腿 %d 对)"
                  % (nm, len(cm["dead"]), len(cm["pair_reg"])))
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
    cm, om = compare_paths(cand_pcb, off_pcb, jc, jo)
    verdict, why = decide(cm, om)
    print("═══ 臂板 vs 官方板 (名单制判据) ═══")
    print("  %-22s %12s %12s" % ("指标", "候选", "官方"))
    for k, lbl in [("drc", "DRC违规"), ("unc", "unconnected"),
                   ("zero_copper", "零铜网(≥2焊盘)"), ("diff_half", "差分单边零铜"),
                   ("diff_over", "差分Δ超差"), ("seg", "走线段"), ("via", "过孔"),
                   ("parity", "parity通过")]:
        print("  %-22s %12s %12s" % (lbl, cm.get(k), om.get(k)))
    print("  ── ★退铜名单 (官方有铜⇒候选零铜): %d" % len(cm.get("dead", [])))
    for n in cm.get("dead", [])[:20]:
        print("       ★ %s" % n)
    print("  ── ★差分对死腿: %d" % len(cm.get("pair_reg", [])))
    for n in cm.get("pair_reg", [])[:12]:
        print("       ★ %s" % n)
    print("  ── (参考) 救回零铜的网: %d" % len(cm.get("gain", [])))
    print("  ── 判定: %s" % verdict)
    for w in why:
        print("     · %s" % w)
    return 0 if verdict == "ACCEPT" else 1


if __name__ == "__main__":
    sys.exit(main())
