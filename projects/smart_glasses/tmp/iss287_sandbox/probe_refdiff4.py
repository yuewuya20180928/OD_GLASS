#!/usr/bin/env python3
# ISS-287 cont2 · 只读探针4: 官方板 vs 沙盒生成板 的 26 处 值/封装 差异明细
import sys, pcbnew


def load(p):
    b = pcbnew.LoadBoard(p)
    d = {}
    for f in b.GetFootprints():
        d[f.GetReference()] = (f.GetFPIDAsString(), f.GetValue())
    return d


off = load(sys.argv[1])
gen = load(sys.argv[2])
common = sorted(set(off) & set(gen))
diff = [r for r in common if off[r] != gen[r]]
fp_only = [r for r in diff if off[r][0] != gen[r][0]]
val_only = [r for r in diff if off[r][0] == gen[r][0]]
print("共同位号 = %d / 差异 = %d / 封装名不同 = %d / 仅值不同 = %d"
      % (len(common), len(diff), len(fp_only), len(val_only)))
print("--- 封装名不同 (%d) ---" % len(fp_only))
for r in fp_only:
    print("  %-22s gen_fp=%r  off_fp=%r" % (r, gen[r][0], off[r][0]))
print("--- 仅 Value 不同 (%d) ---" % len(val_only))
for r in val_only:
    print("  %-22s gen=%-46s off=%s" % (r, gen[r][1][:46], off[r][1][:46]))
empt_gen = sorted([r for r in gen if not gen[r][0]])
empt_off = sorted([r for r in off if not off[r][0]])
print("生成板 空封装名 = %d / 官方板 空封装名 = %d" % (len(empt_gen), len(empt_off)))
