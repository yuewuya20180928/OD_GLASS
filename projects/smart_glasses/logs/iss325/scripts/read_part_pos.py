#!/usr/bin/env python3
# read_part_pos.py -- ISS-325 目标坐标机器读取器 (★零手抄★)
#
# ★**做什么**: 从 .kicad_pcb 里逐个 footprint 块读出 (property "Reference" <ref>) 与 (at x y ...)
#   ⇒ 只输出 ref 以 R_SEL_ / TP_DSI_ 开头的器件 ⇒ 出 TSV
# ★**为什么不许手抄**: ISS-322 §3-8 的处方是「21 器件挪到左上 x 5.50..38.35」⇒ 坐标一旦抄错
#   ⇒ 整条臂就变成「另一个变量」⇒ 实测结论全部作废 ⇒ ⇒ 必须机器读
#
# 用法: python3 read_part_pos.py <board.kicad_pcb> [out.tsv]
import re
import sys

RE_REF = re.compile(r'\(property\s+"Reference"\s+"([^"]+)"')
RE_AT = re.compile(r'^\s*\(at\s+([-\d.]+)\s+([-\d.]+)(?:\s+([-\d.]+))?\s*\)')


def read_refs(path):
    """返回 {ref: (x, y, rot)} —— 逐 footprint 块扫"""
    out = {}
    cur_ref = None
    cur_at = None

    def flush():
        nonlocal cur_ref, cur_at
        if cur_ref is not None and cur_at is not None:
            out.setdefault(cur_ref, cur_at)
        cur_ref = None
        cur_at = None

    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            s = line.strip()
            if s.startswith("(footprint "):
                flush()          # ★上一个块结束 ⇒ 先落账, 再开新块
            m = RE_REF.search(s)
            if m and cur_ref is None:
                cur_ref = m.group(1)
            m2 = RE_AT.match(s)
            if m2 and cur_at is None and cur_ref is not None:
                cur_at = (float(m2.group(1)), float(m2.group(2)),
                          float(m2.group(3)) if m2.group(3) else 0.0)
    flush()
    return out


def main():
    board = sys.argv[1]
    outp = sys.argv[2] if len(sys.argv) > 2 else None
    refs = read_refs(board)
    sel = {k: v for k, v in refs.items()
           if k.startswith("R_SEL_") or k.startswith("TP_DSI_")}
    rows = sorted(sel.items(), key=lambda kv: (kv[0].split("_")[0], kv[0]))
    lines = ["# ISS-325 目标坐标机器读取 TSV",
             "# board=%s" % board,
             "# fields: ref\tx\ty\trot"]
    for k, v in rows:
        lines.append("%s\t%.2f\t%.2f\t%.1f" % (k, v[0], v[1], v[2]))
    # PCB_PART_POS 串 (按 ref 排序稳定输出)
    pp = ";".join("%s:%.2f,%.2f" % (k, v[0], v[1]) for k, v in rows)
    lines.append("# PCB_PART_POS = %s" % pp)
    txt = "\n".join(lines) + "\n"
    sys.stdout.write(txt)
    if outp:
        with open(outp, "w", encoding="utf-8") as f:
            f.write(txt)
        with open(outp + ".partpos.txt", "w", encoding="utf-8") as f:
            f.write(pp + "\n")


if __name__ == "__main__":
    main()
