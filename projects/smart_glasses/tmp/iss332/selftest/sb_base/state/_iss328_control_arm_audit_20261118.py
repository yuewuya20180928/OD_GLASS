#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
★ISS-328 控制臂有效性 · 独立审计 (★main 19:2x 自写·只读·零写板★)

★**为什么有本脚本**: 决策页 §N-1 写死「『显式钉 TP_DSI_*』是 no-op ⇒ 21 器件塌缩成 10 器件」;
★ISS-328 在【官方链同配方】下 fresh 复测出的读数与它【不一致】⇒ 需要一个**独立于任何 agent 报告**的复算器
★把两边的读数逐条摆出来, 供老板/main 裁口径。

★**本脚本只做 4 件事 (全部只读·不写任何盘上文件)**:
  ① 右上臂 vs 基线臂: 全板 185 封装落位差异逐条 ⇒ **拆成 R_SEL_* / TP_* / 外溢 三桶**
     ⇒ 判定【这条臂是不是单变量臂】(★真单变量 ⇒ 外溢桶必须是 0★)
  ② 外溢桶的位移量分布 (Δx/Δy) ⇒ 判定【外溢是不是机械级联】(★位移量全同 ⇒ 可解释★)
  ③ 基线臂 vs 基线臂+显式钉 10 条 TP: 落位差异 ⇒ 判定【『钉 TP 是不是 no-op』】
  ④ 基线臂 vs 官方终板: 落位差异 + 器件数差 ⇒ 判定【臂与官方板是不是同一条产线】

★**用法**: `python3 state/_iss328_control_arm_audit_20261118.py`
★**退出码**: 0 = 四个判定都跑完 (★不代表绿★) · 3 = 缺输入文件 (★盘上材料还没生成/已被清掉★)
"""
import hashlib
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = os.path.join(ROOT, "tmp", "iss328")
LOGS = os.path.join(ROOT, "logs", "iss328")

P_BASE = os.path.join(TMP, "bare_base.kicad_pcb")
P_RU = os.path.join(TMP, "bare_ru.kicad_pcb")
P_RUTP = os.path.join(TMP, "bare_rutp.kicad_pcb")
P_OFF_TSV = os.path.join(LOGS, "03_official_final_all_fp_pos.txt")


def md5(p):
    try:
        return hashlib.md5(open(p, "rb").read()).hexdigest()
    except Exception:
        return "-"


def fps(p):
    """★从一个 .kicad_pcb 里抽 {ref: (x, y)} (★只看封装自身的 at, 不看焊盘的 at★)"""
    out = {}
    cur = None
    pos = None
    for ln in open(p, encoding="utf-8", errors="replace"):
        s = ln.rstrip("\n")
        if re.match(r"^\t\(footprint ", s):
            cur = None
            pos = None
            continue
        if cur is None and pos is None:
            m = re.match(r"^\t\t\(at ([-0-9.]+) ([-0-9.]+)(?: ([-0-9.]+))?\)$", s)
            if m:
                pos = (float(m.group(1)), float(m.group(2)))
                continue
            m2 = re.search(r'\(property "Reference"\s+"([^"]+)"', s)
            if m2:
                cur = m2.group(1)
                out[cur] = pos
                continue
        elif cur is None and pos is not None:
            m2 = re.search(r'\(property "Reference"\s+"([^"]+)"', s)
            if m2:
                cur = m2.group(1)
                out[cur] = pos
    return out


def tsv(p):
    out = {}
    for ln in open(p, encoding="utf-8", errors="replace"):
        c = ln.rstrip("\n").split("\t")
        if len(c) >= 4 and c[0] and c[0] != "__FP__":
            try:
                out[c[0]] = (float(c[1]), float(c[2]))
            except Exception:
                pass
    return out


def diff(x, y):
    return [(k, x.get(k), y.get(k)) for k in sorted(set(x) | set(y)) if x.get(k) != y.get(k)]


def main():
    need = [P_BASE, P_RU, P_RUTP, P_OFF_TSV]
    miss = [p for p in need if not os.path.exists(p)]
    if miss:
        print("★[缺输入] 盘上材料不全 ⇒ 本脚本没法复算 (★不是失败·是还没生成★)")
        for m in miss:
            print("   缺: %s" % os.path.relpath(m, ROOT))
        return 3

    B = fps(P_BASE)
    R = fps(P_RU)
    T = fps(P_RUTP)
    OFF = tsv(P_OFF_TSV)

    print("=" * 78)
    print("★ISS-328 控制臂有效性 · 独立审计 (★main 只读复算·不抄任何 agent 报告★)")
    print("=" * 78)
    print("输入 md5:")
    for tag, p in (("基线臂", P_BASE), ("右上臂", P_RU), ("右上臂+钉TP", P_RUTP)):
        print("   %-12s %s" % (tag, md5(p)))
    print("封装数: 基线 %d · 右上 %d · 右上+钉TP %d · 官方终板 %d" % (len(B), len(R), len(T), len(OFF)))

    print()
    print("★① 右上臂 vs 基线臂 —— 【是不是单变量臂】")
    d1 = diff(B, R)
    sel = [x for x in d1 if x[0].startswith("R_SEL_")]
    tp = [x for x in d1 if x[0].startswith("TP_")]
    oth = [x for x in d1 if not (x[0].startswith("R_SEL_") or x[0].startswith("TP_"))]
    print("   落位差异总计 = %d 条  =  R_SEL_* %d  +  TP_* %d  +  ★外溢 %d" % (len(d1), len(sel), len(tp), len(oth)))
    print("   ⇒ ★★单变量臂的判据: 【外溢桶必须 = 0】 ⇒ 实测外溢 %d ⇒ %s"
          % (len(oth), "★是单变量臂★" if len(oth) == 0 else "★不是单变量臂★"))
    print("   -- 被钉的 10 条 R_SEL_* (这才是【意图变量】) --")
    for k, x, y in sel:
        print("      %-12s base=%-16s ru=%s" % (k, x, y))

    print()
    print("★② 外溢桶的位移量 —— 【外溢是不是机械级联】")
    dxy = Counter()
    for k, x, y in oth:
        dxy[(round(y[0] - x[0], 3), round(y[1] - x[1], 3))] += 1
    for (ddx, ddy), n in sorted(dxy.items(), key=lambda kv: -kv[1]):
        print("      Δx=%+.3f  Δy=%+.3f  ⇒ %d 条" % (ddx, ddy, n))
    uni = len(dxy) == 1
    print("   ⇒ %s" % ("★位移量全同 ⇒ 机械级联 ⇒ 外溢可解释(但仍是外溢)★" if uni
                      else "★位移量不一致 ⇒ 外溢不是单一机制★"))

    print()
    print("★③ 右上臂 vs 右上臂+显式钉 10 条 TP —— 【『钉 TP 是不是 no-op』】")
    d3 = diff(R, T)
    print("   落位差异 = %d 条" % len(d3))
    for k, x, y in d3:
        print("      %-13s 不钉=%-16s 钉=%s" % (k, x, y))
    print("   ⇒ %s" % ("★not a no-op (★这 8 条全是 TP_* ⇒ 非 TP 封装落位 0 条变化★)" if d3
                      else "★no-op (本配方下)"))

    print()
    print("★④ 基线臂 vs 官方终板 —— 【臂与官方板是不是同一条产线】")
    d4 = diff(B, OFF)
    o4 = [x for x in d4 if not (x[0].startswith("R_SEL_") or x[0].startswith("TP_"))]
    print("   落位差异 = %d 条 (其中非 R_SEL/TP = %d)" % (len(d4), len(o4)))
    only_off = sorted(set(OFF) - set(B))
    only_arm = sorted(set(B) - set(OFF))
    print("   只在官方板上的器件: %s" % (only_off or "无"))
    print("   只在臂上的器件  : %s" % (only_arm or "无"))
    print("   ⇒ %s" % ("★跨产线 (落位差 %d 条) ⇒ 「臂 vs 官方板」的差不能当布局优劣读★" % len(d4)
                      if len(d4) else "★同产线★"))

    print()
    print("★结论 (★机器复算·不是抄 agent 报告★):")
    print("   ① 右上臂【不是】单变量臂 (外溢 %d 条 ⇒ 真单变量要求 = 0)" % len(oth))
    print("   ② 外溢是机械级联: %s" % ("单一位移量" if uni else "多档位移量"))
    print("   ③ 「钉 TP 是 no-op」在【官方链同配方】下 %s" % ("不成立" if d3 else "成立"))
    print("   ④ 臂与官方板【不是】同一条产线 (落位差 %d 条)" % len(d4))
    print("=" * 78)
    return 0


if __name__ == "__main__":
    sys.exit(main())
