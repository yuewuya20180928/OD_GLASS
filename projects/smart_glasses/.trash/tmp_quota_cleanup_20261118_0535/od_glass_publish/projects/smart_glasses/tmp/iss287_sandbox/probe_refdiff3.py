#!/usr/bin/env python3
# ISS-287 cont2 · 只读探针: 官方板 vs 沙盒生成板 的位号差集/重复/后缀/DNP
# ★只 LoadBoard + 打印, 不 SaveBoard, 不写真盘任何文件★
import sys, pcbnew


def load(p):
    b = pcbnew.LoadBoard(p)
    out = {}
    for f in b.GetFootprints():
        ref = f.GetReference()
        dnp = False
        try:
            dnp = bool((f.GetAttributes() & pcbnew.FP_EXCLUDE_FROM_BOM)
                       or (f.GetAttributes() & pcbnew.FP_EXCLUDE_FROM_POS_FILES)
                       or f.IsDNP())
        except Exception:
            pass
        out.setdefault(ref, []).append(
            (f.GetFPIDAsString(), f.GetValue(), dnp, f.GetPosition().x / 1e6, f.GetPosition().y / 1e6))
    return b, out


b1, off = load(sys.argv[1])   # 官方板
b2, gen = load(sys.argv[2])   # 沙盒生成板

print("官方板 封装数 = %d / 唯一位号 = %d" % (sum(len(v) for v in off.values()), len(off)))
print("生成板 封装数 = %d / 唯一位号 = %d" % (sum(len(v) for v in gen.values()), len(gen)))

only_off = sorted(set(off) - set(gen))
only_gen = sorted(set(gen) - set(off))
print("只在官方板 = %d %s" % (len(only_off), only_off))
print("只在生成板 = %d %s" % (len(only_gen), only_gen))

for r in only_off:
    for item in off[r]:
        print("   官方板独有: %s  fp=%s  value=%s  dnp=%s  pos=(%.2f,%.2f)"
              % (r, item[0], item[1], item[2], item[3], item[4]))

dup_off = sorted([r for r, v in off.items() if len(v) > 1])
print("官方板重复位号 = %s" % (dup_off or "无"))

suf = sorted([r for r in off if r.endswith("_1")])
print("官方板带 _1 后缀位号 = %d %s" % (len(suf), suf))

dnp_off = sorted([r for r, v in off.items() if any(i[2] for i in v)])
dnp_gen = sorted([r for r, v in gen.items() if any(i[2] for i in v)])
print("官方板 DNP 标记位号 = %d" % len(dnp_off))
print("生成板 DNP 标记位号 = %d" % len(dnp_gen))
print("生成板 DNP 但官方板没标 = %s" % sorted(set(dnp_gen) - set(dnp_off)))
print("官方板标了但生成板没标 = %s" % sorted(set(dnp_off) - set(dnp_gen)))
