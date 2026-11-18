#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""pair_copper_table.py -- ★★★**逐对"铜长度表" (2026-11-09 00:3x) ★★★

★★**为什么要另写一份 (★而不是直接用 tools/diff_pair_audit.py 的输出)****
  ★**`diff_pair_audit.py` 的主表只在【两条腿都有铜】时填数字**, 单边零铜的配对打印成 "-/-"
    ⇒ ★**机器读的时候没法直接判断"哪条腿有铜"** ⇒ ★**只能靠人眼看那行 ★单边零铜: XXX 的提示**
  ★★**⇒ 这份表【直接按 net 从板文件里算每条腿的铜长】⇒ 单边零铜也能落成数字 (0.00) ⇒ 可机器比****
  ★★**而且它是一份【独立实现】⇒ 和 diff_pair_audit.py 互为第二把尺子 (★同源出错就抓不到了)****

用法: `python3 state/pair_copper_table.py <板>` ⇒ 打印 "PAIR_NAME\tL_P\tL_N"
"""
import math
import re
import sys

PAIRS = [
    ("NET_USB_D_P_TYPEC", "NET_USB_D_N_TYPEC"),
    ("USB_D_P_SRC", "USB_D_N_SRC"),
    ("CSI_D0_CK_P_SRC", "CSI_D0_CK_N_SRC"), ("CSI_D0_CK_P", "CSI_D0_CK_N"),
    ("CSI_D0_D0_P_SRC", "CSI_D0_D0_N_SRC"), ("CSI_D0_D0_P", "CSI_D0_D0_N"),
    ("CSI_D0_D1_P_SRC", "CSI_D0_D1_N_SRC"), ("CSI_D0_D1_P", "CSI_D0_D1_N"),
    ("CSI_D0_D2_P_SRC", "CSI_D0_D2_N_SRC"), ("CSI_D0_D2_P", "CSI_D0_D2_N"),
    ("CSI_D0_D3_P_SRC", "CSI_D0_D3_N_SRC"), ("CSI_D0_D3_P", "CSI_D0_D3_N"),
    ("DSI_D0_CK_P_SRC", "DSI_D0_CK_N_SRC"), ("DSI_D0_CK_P", "DSI_D0_CK_N"),
    ("DSI_D0_D0_P_SRC", "DSI_D0_D0_N_SRC"), ("DSI_D0_D0_P", "DSI_D0_D0_N"),
    ("DSI_D0_D1_P_SRC", "DSI_D0_D1_N_SRC"), ("DSI_D0_D1_P", "DSI_D0_D1_N"),
    ("DSI_D0_D2_P_SRC", "DSI_D0_D2_N_SRC"), ("DSI_D0_D2_P", "DSI_D0_D2_N"),
    ("DSI_D0_D3_P_SRC", "DSI_D0_D3_N_SRC"), ("DSI_D0_D3_P", "DSI_D0_D3_N"),
]


def main():
    pcb = sys.argv[1]
    lengths = {}
    inseg = False
    net = None
    x1 = y1 = x2 = y2 = None
    with open(pcb, encoding="utf-8", errors="ignore") as f:
        for ln in f:
            s = ln.strip()
            if s == "(segment":
                inseg = True
                net = None
                x1 = y1 = x2 = y2 = None
                continue
            if inseg:
                m = re.match(r"\(start ([-\d.]+) ([-\d.]+)\)", s)
                if m:
                    x1, y1 = float(m.group(1)), float(m.group(2))
                m = re.match(r"\(end ([-\d.]+) ([-\d.]+)\)", s)
                if m:
                    x2, y2 = float(m.group(1)), float(m.group(2))
                m = re.match(r'\(net "([^"]+)"\)', s)
                if m:
                    net = m.group(1)
                if s == ")":
                    inseg = False
                    if net is not None and x1 is not None and x2 is not None:
                        lengths[net] = lengths.get(net, 0.0) + math.hypot(x2 - x1, y2 - y1)
    for (p, n) in PAIRS:
        print("%s|%s\t%.3f\t%.3f" % (p, n, lengths.get(p, 0.0), lengths.get(n, 0.0)))


if __name__ == "__main__":
    main()
