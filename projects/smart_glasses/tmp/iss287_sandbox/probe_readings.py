#!/usr/bin/env python3
# ISS-287 沙盒读数探针 (★只读: 只 LoadBoard + 打印, 不 SaveBoard★)
# 用法: bash state/pcbnew_py.sh probe_readings.py <板文件>
import sys
import pcbnew


def probe(path):
    b = pcbnew.LoadBoard(path)
    if b is None:
        print("❌ LoadBoard 失败: %s" % path)
        return 1
    fps = list(b.GetFootprints())
    bb = b.GetBoardEdgesBoundingBox()
    # DNP 标记 (exclude_from_bom / exclude_from_pos_files)
    dnp = []
    for f in fps:
        try:
            if (f.GetAttributes() & pcbnew.FP_EXCLUDE_FROM_BOM) or \
               (f.GetAttributes() & pcbnew.FP_EXCLUDE_FROM_POS_FILES) or \
               f.IsDNP():
                dnp.append(f.GetReference())
        except Exception:
            pass
    try:
        b.BuildConnectivity()
        unc = int(b.GetConnectivity().GetUnconnectedCount(False))
    except Exception as e:
        unc = -1
        print("  ⚠️ unconnected 取不到: %s" % e)
    refs = sorted(f.GetReference() for f in fps)
    dup = sorted({r for r in refs if refs.count(r) > 1})
    print("=== %s" % path)
    print("  封装数(footprints)      = %d" % len(fps))
    print("  位号数                  = %d   (带 _1 后缀 = %d)"
          % (len(refs), len([r for r in refs if r.endswith("_1")])))
    print("  重复位号                = %s" % (dup[:5] if dup else "无"))
    print("  铜层数                  = %d" % b.GetCopperLayerCount())
    print("  板框 Edge.Cuts bbox     = %.1f x %.1f mm  (x %.2f..%.2f, y %.2f..%.2f)"
          % (bb.GetWidth() / 1e6, bb.GetHeight() / 1e6,
             bb.GetX() / 1e6, (bb.GetX() + bb.GetWidth()) / 1e6,
             bb.GetY() / 1e6, (bb.GetY() + bb.GetHeight()) / 1e6))
    print("  DNP/不贴标记位号数       = %d" % len(dnp))
    print("  unconnected             = %d" % unc)
    return 0


if __name__ == "__main__":
    rc = 0
    for p in sys.argv[1:]:
        rc |= probe(p)
    sys.exit(rc)
