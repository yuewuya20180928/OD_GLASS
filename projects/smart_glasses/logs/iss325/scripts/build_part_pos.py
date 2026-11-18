#!/usr/bin/env python3
# build_part_pos.py -- ISS-325 PCB_PART_POS 串生成器 (★零手抄★)
#
# ★**设计原则 (★"唯一变量"必须字面可见★)**:
#   · R_SEL_* 那 10 个条目 = **从 state/v76mz_arms.sh 里逐字节抽出来** (顺序也照抄)
#     ⇒ ⇒ 我的 PCB_PART_POS 与 v76mz 的 diff = **只有末尾追加的 10 个 TP_DSI_*** ⇒ 天然单变量
#   · TP_DSI_* 那 10 个条目 = **从 state/.lastgood/best_unc23_clrfix.kicad_pcb 机器读出来**
#     ⇒ ⇒ 不手抄 ⇒ 不抄错
#   · 校验: 机器读到的 10 个 R_SEL_* 坐标必须与 v76mz 的逐条相等 (★不等就红★)
#
# 用法: python3 build_part_pos.py <target.tsv.partpos.txt> <v76mz_arms.sh> <out.txt>
import re
import sys

tsv_partpos, v76mz_sh, outp = sys.argv[1], sys.argv[2], sys.argv[3]

# ① 机器读到的目标坐标 (ref -> x,y)
machine = {}
raw = open(tsv_partpos, encoding="utf-8").read().strip()
for tok in raw.split(";"):
    tok = tok.strip()
    if not tok or ":" not in tok:
        continue
    r, v = tok.split(":", 1)
    x, y = v.split(",")
    machine[r.strip()] = (float(x), float(y))

# ② v76mz 的 PCB_PART_POS 串 (逐字节抽)
src = open(v76mz_sh, encoding="utf-8").read()
m = re.search(r'PCB_PART_POS="([^"]+)"', src)
if not m:
    print("❌ 没在 %s 里找到 PCB_PART_POS" % v76mz_sh)
    sys.exit(2)
v76mz_pp = m.group(1)
v76mz_map = {}
for tok in v76mz_pp.split(";"):
    r, v = tok.split(":", 1)
    x, y = v.split(",")
    v76mz_map[r.strip()] = (float(x), float(y))

# ③ 校验: 机器读的 10 个 R_SEL_* 必须与 v76mz 的相等
fail = 0
rsels = [r for r in machine if r.startswith("R_SEL_")]
for r in sorted(rsels):
    if r not in v76mz_map:
        print("❌ %s 在 v76mz 里没有" % r)
        fail = 1
    elif v76mz_map[r] != machine[r]:
        print("❌ %s 机器读=%s ≠ v76mz=%s" % (r, machine[r], v76mz_map[r]))
        fail = 1
if fail:
    print("❌ R_SEL_* 基线对不上 ⇒ 收工")
    sys.exit(3)

# ④ 生成: v76mz 的 R_SEL_* 顺序逐字节照抄 + 机器读的 10 个 TP_DSI_*
tp = sorted([r for r in machine if r.startswith("TP_DSI_")])
if len(tp) != 10:
    print("❌ 机器读到的 TP_DSI_* 不是 10 个 (是 %d 个)" % len(tp))
    sys.exit(4)
out_pp = v76mz_pp + ";" + ";".join("%s:%.2f,%.2f" % (r, machine[r][0], machine[r][1]) for r in tp)

with open(outp, "w", encoding="utf-8") as f:
    f.write(out_pp + "\n")

print("OK  R_SEL_* 条目 = %d (逐字节同 v76mz)  +  TP_DSI_* 条目 = %d (机器读)" % (len(v76mz_map), len(tp)))
print("OUT %s" % outp)
print("---")
print(out_pp)
