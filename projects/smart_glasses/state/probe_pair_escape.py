#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
probe_pair_escape.py —— ★★差分对 N 侧"出脚豁免"探针 (2026-11-05 09:50)

★**干什么**: 只在**排版板 (无布线)** 上, 单独布几对差分对, 量 N 侧能不能出脚
  ⇒ ★**不用等 1.5 小时整板布线** 就能验证 `PCB_PAIR_ESCAPE_EXEMPT` 有没有用

★**判据**: N 侧段数 > 0 ⇒ 出脚解封 (★原来全是 0 段)

用法:
    PCB_PAIR_ESCAPE_EXEMPT=0|1 python3 state/probe_pair_escape.py <排版板.kicad_pcb>
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import pcbnew  # noqa: E402
import gen_pcb_routing as RT  # noqa: E402

PAIRS = [
    ("USB_D_P_SRC", "USB_D_N_SRC"),
    ("CSI_D0_CK_P_SRC", "CSI_D0_CK_N_SRC"),
    ("CSI_D0_D0_P_SRC", "CSI_D0_D0_N_SRC"),
    ("CSI_D0_D1_P_SRC", "CSI_D0_D1_N_SRC"),
    ("CSI_D0_D2_P_SRC", "CSI_D0_D2_N_SRC"),
    ("DSI_D0_CK_P_SRC", "DSI_D0_CK_N_SRC"),
    ("NET_USB_D_P_TYPEC", "NET_USB_D_N_TYPEC"),
]


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "/tmp/probe_pair.kicad_pcb"
    flag = os.environ.get("PCB_PAIR_ESCAPE_EXEMPT", "0")
    print("═══ 出脚豁免探针 ═══ 板=%s  PCB_PAIR_ESCAPE_EXEMPT=%s" % (path, flag))
    board = pcbnew.LoadBoard(path)
    board.BuildListOfNets()
    RT.add_gnd_planes(board, layers=None, fill=False)
    r = RT.GridRouter(board)
    tot_n_ok = 0
    for (p, n) in PAIRS:
        if p not in r.net_pads or n not in r.net_pads:
            print("  %-18s/%-18s 跳过 (网不在板上)" % (p, n))
            continue
        nseg_before = len([t for t in r.tracks if t[0] == n])
        res = RT.route_diff_pair(r, p, n)
        nseg = len([t for t in r.tracks if t[0] == n])
        tot_n_ok += 1 if nseg > nseg_before else 0
        print("  %-18s / %-18s  P_ok=%-5s N_ok=%-5s  N段=%-4d  Δ=%.3fmm  ring=%s"
              % (p, n, res.get("p_ok"), res.get("n_ok"), nseg,
                 res.get("delta", 0), res.get("ring")))
    print("─── 汇总: N 侧有铜的对 = %d / %d" % (tot_n_ok, len(PAIRS)))


if __name__ == "__main__":
    main()
