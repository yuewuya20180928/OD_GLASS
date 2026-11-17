import sys, pcbnew
def refs(p):
    b = pcbnew.LoadBoard(p)
    return {f.GetReference(): (f.GetFPIDAsString(), f.GetValue()) for f in b.GetFootprints()}
a = refs(sys.argv[1]); b = refs(sys.argv[2])
diff = [r for r in sorted(set(a)&set(b)) if a[r] != b[r]]
print("共同位号 =", len(set(a)&set(b)), " 值/封装不同 =", len(diff))
r_only = sorted(set(a)-set(b)); print("只在官方板 =", r_only)
import collections
bykind = collections.Counter()
for r in diff:
    bykind[r.rstrip("0123456789").split("_")[0]] += 1
print("按前缀:", dict(bykind))
print("电阻类差异:")
for r in diff:
    if r.startswith("R_") or r.startswith("FB_"):
        print("   ", r, a[r][1], "->", b[r][1])
