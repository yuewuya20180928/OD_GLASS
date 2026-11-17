import sys, pcbnew
def refs(p):
    b = pcbnew.LoadBoard(p)
    return {f.GetReference(): (f.GetFPIDAsString(), f.GetValue(), f.GetPosition().x/1e6, f.GetPosition().y/1e6) for f in b.GetFootprints()}
a = refs(sys.argv[1]); b = refs(sys.argv[2])
print("官方盘脚位数 =", len(a), " 沙盒生成板 =", len(b))
print("只在官方板 =", sorted(set(a)-set(b)))
print("只在生成板 =", sorted(set(b)-set(a)))
for r in sorted(set(a)&set(b)):
    if a[r][:2] != b[r][:2]:
        print("  值/封装不同:", r, a[r][:2], "->", b[r][:2])
