#!/usr/bin/env python3
# read_part_pos_pcbnew.py -- ISS-325 目标坐标机器读取器 (★pcbnew 权威读法★)
#
# ★**为什么用 pcbnew 而不是纯文本解析**: 纯文本解析会抓到 (property "Reference" ...) 内部嵌套的
#   `(at 0 -1.43 90)` (★那是丝印层文字偏移, 不是封装原点★) ⇒ 上一次纯文本跑出来全是 0.00
#   ⇒ ⇒ 必须用 pcbnew 的 GetPosition() (封装原点, 权威)
#
# 用法: bash state/pcbnew_py.sh logs/iss325/scripts/read_part_pos_pcbnew.py <board.kicad_pcb> [out.tsv]
import sys
import pcbnew

board_path = sys.argv[1]
outp = sys.argv[2] if len(sys.argv) > 2 else None

b = pcbnew.LoadBoard(board_path)
if b is None:
    print("❌ 板读不出来: %s" % board_path)
    sys.exit(1)

sel = []
for fp in b.GetFootprints():
    ref = fp.GetReference()
    if ref.startswith("R_SEL_") or ref.startswith("TP_DSI_"):
        p = fp.GetPosition()
        # pcbnew 内部单位 = nm ⇒ 转 mm
        x = round(pcbnew.ToMM(p.x), 4)
        y = round(pcbnew.ToMM(p.y), 4)
        rot = round(fp.GetOrientationDegrees(), 1)
        sel.append((ref, x, y, rot))

# ★排序: 先按前缀 (R_SEL_ / TP_DSI_), 再按 ref 名 ⇒ 输出稳定可比
sel.sort(key=lambda r: (0 if r[0].startswith("R_SEL_") else 1, r[0]))

lines = []
lines.append("# ISS-325 目标坐标机器读取 TSV (★pcbnew GetPosition 权威读法★)")
lines.append("# board=%s" % board_path)
lines.append("# board_md5 (见同名 .md5 文件)")
lines.append("# fields: ref\tx\ty\trot")
for ref, x, y, rot in sel:
    lines.append("%s\t%.2f\t%.2f\t%.1f" % (ref, x, y, rot))

# PCB_PART_POS 串 —— ★逐字节进臂脚本, 不许手抄★
pp = ";".join("%s:%.2f,%.2f" % (ref, x, y) for ref, x, y, rot in sel)
lines.append("# PCB_PART_POS = %s" % pp)

txt = "\n".join(lines) + "\n"
sys.stdout.write(txt)
if outp:
    with open(outp, "w", encoding="utf-8") as f:
        f.write(txt)
    with open(outp + ".partpos.txt", "w", encoding="utf-8") as f:
        f.write(pp + "\n")
print("__PCBNEW_OK__ footprints_selected=%d" % len(sel))
