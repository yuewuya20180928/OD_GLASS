#!/usr/bin/env bash
# compare_pair_tables.sh -- ★★★**两块板的差分对逐对对照 (★2026-11-09 00:3x 新增)** ★★★
#
# ★**为什么要有这个工具 (★实测事故链)**:
#   ★**"某臂救回了 2 对差分对"这句话, 如果不逐对对照, 就分不清"救回"和"换了个地方输"**
#   ★v74 实测就撞到过这个坑: 换边救回 CSI_D0_D0 两对, 但同一次运行里
#   ★**DSI_D0_CK_P/N 从"两条都有铜"变成"两条都零铜"** ⇒ ★**只看"救回几对"会漏掉回归**
#   ⇒ ★**⇒ 必须逐对列出 (哪一对变好 / 哪一对变差 / 哪些没动)**
#
# ★**用法**: `bash state/compare_pair_tables.sh <板A> <板B>` (★A 通常是候选, B 是基线)
# ★**数据源**: `state/pair_copper_table.py` (★独立实现 ⇒ 与 tools/diff_pair_audit.py 互为第二把尺子)
set -u
PROJ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
A="${1:?用法: compare_pair_tables.sh <板A> <板B>}"
B="${2:?用法: compare_pair_tables.sh <板A> <板B>}"

python3 - "$A" "$B" <<'PY'
import subprocess
import sys

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"


def table(path):
    out = subprocess.run([sys.executable, PROJ + "/state/pair_copper_table.py", path],
                         capture_output=True, text=True, check=True).stdout
    d = {}
    for ln in out.splitlines():
        key, lp, ln_ = ln.split("\t")
        d[key] = (float(lp), float(ln_))
    return d


A = table(sys.argv[1])
B = table(sys.argv[2])
print("════ A(候选): %s" % sys.argv[1])
print("════ B(基线): %s" % sys.argv[2])
print()
print("%-44s %-18s %-18s %s" % ("差分对 (P / N)", "A(候选) L_P/L_N", "B(基线) L_P/L_N", "判定"))
better = worse = same = 0
for k in list(A.keys()):
    ap, an = A[k]
    bp, bn = B.get(k, (0.0, 0.0))
    a_has = (ap > 0.0, an > 0.0)
    b_has = (bp > 0.0, bn > 0.0)
    if a_has == b_has:
        verdict = "持平 (%s)" % ("都有铜" if all(a_has) else ("单边零铜" if any(a_has) else "两条都零铜"))
        same += 1
    elif all(a_has) and not all(b_has):
        verdict = "★★变好 (基线 %s ⇒ 候选两条都有铜)" % ("单边零铜" if any(b_has) else "两条都零铜")
        better += 1
    else:
        verdict = "★★变差 (基线两条都有铜 ⇒ 候选 %s)" % ("单边零铜" if any(a_has) else "两条都零铜")
        worse += 1
    print("%-44s %-18s %-18s %s" % (k.replace("|", " / "),
                                    "%.3f/%.3f" % (ap, an), "%.3f/%.3f" % (bp, bn), verdict))
print()
print("★合计: 变好 %d · 变差 %d · 持平 %d" % (better, worse, same))
PY
