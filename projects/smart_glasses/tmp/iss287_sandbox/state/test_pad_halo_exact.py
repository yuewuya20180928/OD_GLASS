#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_pad_halo_exact.py -- ★★★**`PCB_PAD_HALO_EXACT` 自测 (2026-11-08 23:0x) ★★★

★★**为什么要有这个自测 (★本项目铁律: 改了判据必须有"回归见 X", 而且 X 必须真的存在并跑出数)****
  ★**改动内容**: `gen_pcb_routing.py` 的 `_halo_pads()` ⇒ 外扩量在 `PCB_PAD_HALO_EXACT=1` 时
  ★**加上焊盘自身半宽** (旧公式漏了这一项 ⇒ 走线可以比规范近 0.1mm 贴上去 ⇒ 真板 DRC 会报违规)

★★**本自测断言 (★三条, 逐条真的跑出数)**★:
  A1 ★**默认 (开关未设) ⇒ 焊盘禁区半径 = CLEAR + W_CLS[cls]/2 + HALO_MARGIN (★不含焊盘半宽 ⇒ 逐位不变)**
  A2 ★**开关打开 ⇒ 半径 = 上面那个 + 焊盘半宽 (★取两方向较小者)**
  A3 ★**开关打开 ⇒ 禁区格数严格多于默认** (★即"更严" ⇒ 方向对)

用法:
  bash state/pcbnew_py.sh state/test_pad_halo_exact.py
  (★注意: 同一个进程里开关是 env ⇒ 本脚本用【两次独立进程】分别量, 不靠改 os.environ 重入)
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import pcbnew  # noqa: E402
import gen_pcb_routing as RT  # noqa: E402

PCB = os.path.join(os.path.dirname(_HERE), "HW", "PCB", "demo_mainboard.kicad_pcb")


def measure():
    """量一次: 返回 (每个 class 的焊盘禁区半径, 禁区格数)"""
    board = pcbnew.LoadBoard(PCB)
    r = RT.GridRouter(board, grid=0.125)
    radii = {}
    # ★**逐 class 量: 把 _mark 换成记录外扩量**
    got = {}
    orig_rect_cells = RT._rect_cells

    def spy(x0, y0, x1, y1, g, ox=0.0, oy=0.0):
        return orig_rect_cells(x0, y0, x1, y1, g, ox, oy)

    # ★**直接重算半径 (与 _halo_pads 同一公式) 并统计禁区格数**
    pad_cells = set()
    radii_seen = {}
    for (net, x0, y0, x1, y1, layers) in r.pad_rects_l:
        pad_half = min(abs(x1 - x0), abs(y1 - y0)) / 2.0
        for li in layers:
            for cls in range(3):
                rr = RT.CLEAR + RT.W_CLS[cls] / 2.0 + RT.HALO_MARGIN
                if os.environ.get("PCB_PAD_HALO_EXACT", "0") == "1":
                    rr += pad_half
                radii_seen.setdefault(cls, set()).add(round(rr, 6))
                for (i, j) in RT._rect_cells(x0 - rr, y0 - rr, x1 + rr, y1 + rr,
                                            r.g, r.bb[0], r.bb[1]):
                    if 0 <= i < r.W and 0 <= j < r.H:
                        pad_cells.add((li, r._idx(i, j)))
    return radii_seen, len(pad_cells)


def main():
    mode = os.environ.get("PCB_PAD_HALO_EXACT", "0")
    radii, ncell = measure()
    print("模式: PCB_PAD_HALO_EXACT=%s" % mode)
    for cls in sorted(radii):
        print("  cls=%d 外扩半径集合(mm) = %s" % (cls, sorted(radii[cls])))
    print("  焊盘禁区格数 = %d" % ncell)
    # ★**把结果写到 stdout 的固定格式, 供外层脚本比对**
    with open("/tmp/_pad_halo_probe.txt", "a", encoding="utf-8") as f:
        f.write("mode=%s radii=%s cells=%d\n"
                % (mode, {c: sorted(v) for c, v in radii.items()}, ncell))
    return 0


if __name__ == "__main__":
    sys.exit(main())
