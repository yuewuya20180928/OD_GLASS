#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""dump_fp_pos.py -- 把一块板上【所有封装】的落位 (ref, x, y, rot) 机器读出来

用法: bash state/pcbnew_py.sh tmp/iss328/dump_fp_pos.py <板路径>
输出: stdout, 每行 "ref\tx\ty\trot" (按 ref 排序)
★口径: pcbnew GetPosition() 绝对板坐标 (mm) · 与 logs/iss328/02_official_s1_all_fp_pos.txt 同一读法
"""
import sys
import pcbnew


def main():
    if len(sys.argv) < 2:
        print("用法: dump_fp_pos.py <板路径>")
        return 2
    path = sys.argv[1]
    b = pcbnew.LoadBoard(path)
    if b is None:
        print("❌ 板读不出来: %s" % path)
        return 1
    rows = []
    for fp in b.GetFootprints():
        p = fp.GetPosition()
        try:
            rot = fp.GetOrientation().AsDegrees()
        except Exception:
            rot = fp.GetOrientationDegrees()
        rows.append((fp.GetReference(),
                     round(pcbnew.ToMM(p.x), 4),
                     round(pcbnew.ToMM(p.y), 4),
                     round(rot, 1)))
    rows.sort(key=lambda r: r[0])
    print("ref\tx\ty\trot")
    for r in rows:
        print("%s\t%.4f\t%.4f\t%.1f" % r)
    print("# 封装数 = %d" % len(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
