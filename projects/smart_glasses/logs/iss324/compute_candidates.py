#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-324 · mech-lead · 候选落位点终表 (只读, 复用 recompute_led_space 的空间推导)

每个候选给 7 项 (交卷页 §6 逐字要的):
  ① 封装原点坐标  ② 焊盘绝对坐标 (pad1/pad2)  ③ 到 R_LED_G.2 的直线距离 (pad-to-pad 真网长)
  ④ 到最近邻器件的净距  ⑤ 对 §3 坐标空间的落位 (哪条带)  ⑥ 改板 md5 的影响 (动/不动)
  ⑦ 距板边 / 距两条开口窗口的余量
★零写板★
用法: python3 logs/iss324/compute_candidates.py
"""
import importlib.util
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"

spec = importlib.util.spec_from_file_location("rls", os.path.join(HERE, "recompute_led_space.py"))
rls = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rls)

CANDIDATES = [
    ("C1", 8.250, 63.700, "clr 0.00 (板 DRC min_clearance 硬极限) 下最近落位原点 · 上半带"),
    ("C2", 8.050, 63.900, "clr 0.20 (板内网络类默认 clearance) 下最近落位原点 · 上半带"),
    ("C3", 8.420, 64.200, "clr 0.50 (板 zones.min_clearance) 下最近落位原点 · 上半带第二块"),
    ("C4", 8.250, 61.900, "clr 0.00 下最近落位原点 · ★下半带★ (既有 MECH 文档未登记)"),
    ("C5", 8.250, 66.000, "最近落位带内 Y 偏上 (给结构光孔留高度余量)"),
    ("C6", 2.500, 60.000, "整高自由带 X 1.550..3.450 内 (假设 B 无光孔口径)"),
]


def main():
    board = rls.read_board(rls.PCB)
    fps = board["fps"]
    sp = rls.led_space(board, 0.0)
    rel = sp["rel"]
    r2 = [p for p in fps["R_LED_G"]["pads"] if p["num"] == "2"][0]
    d1 = [p for p in fps["D_LED_G"]["pads"] if p["num"] == "1"][0]
    cur = math.hypot(d1["x"] - r2["x"], d1["y"] - r2["y"])

    edge = board["edge"]
    openings = {}
    for nm, ref, bw in (("调试口开口", "J_DEBUG",
                          rls.copper_bbox(fps["J_DEBUG"])[1] - rls.copper_bbox(fps["J_DEBUG"])[0]),
                         ("检修口开口", "J_UART", 2.54)):
        openings[nm] = rls.opening_rect(fps[ref], bw)

    print("=" * 96)
    print("ISS-324 候选落位点终表 (帧 B160x100 · 现役台架板)")
    print("=" * 96)
    print("现状 `LED_G_D` pad-to-pad 直线长 = %.6f mm (R_LED_G.2 %.2f,%.2f ↔ D_LED_G.1 %.2f,%.2f)"
          % (cur, r2["x"], r2["y"], d1["x"], d1["y"]))
    print("D_LED_G 铜箔相对封装原点 = X %+.2f..%+.2f  Y %+.2f..%+.2f"
          % (rel[0], rel[1], rel[2], rel[3]))

    for name, ox, oy, why in CANDIDATES:
        pad1 = (ox + rel[0] + 0.30, oy + rel[2] + 0.45)
        pad2 = (ox + rel[0] + 2.30, oy + rel[2] + 0.45)
        net = math.hypot(pad1[0] - r2["x"], pad1[1] - r2["y"])
        proxy = math.hypot(ox + rel[0] - r2["x"], oy + rel[2] - r2["y"])
        newbox = (ox + rel[0], ox + rel[1], oy + rel[2], oy + rel[3])
        gaps = []
        for ref, f in fps.items():
            if ref == "D_LED_G":
                continue
            b = rls.copper_bbox(f)
            if b:
                gaps.append((rls.rect_gap(newbox, b), ref,
                             ",".join(sorted({p["net"] for p in f["pads"]}))))
        gaps.sort()
        inb = rls.band_of(sp, ox, oy)
        full = any(b["ox0"] - 1e-9 <= ox <= b["ox1"] + 1e-9 for b in sp["full_height_bands"])
        edge_gap = min(newbox[0] - edge["x0"], edge["x1"] - newbox[1],
                       newbox[2] - edge["y0"], edge["y1"] - newbox[3])
        print("\n" + "-" * 96)
        print("%s  封装原点 = (%.3f, %.3f)   %s" % (name, ox, oy, why))
        print("  ① 封装原点坐标        = (%.3f, %.3f)   (落在带 X %.3f..%.3f × Y %.3f..%.3f)"
              % (ox, oy, inb["ox0"], inb["ox1"], inb["oy0"], inb["oy1"]) if inb else
              "  ① 封装原点坐标        = (%.3f, %.3f)   ★不在可放行空间内★" % (ox, oy))
        print("  ② 焊盘绝对坐标        = pad1 (%.2f, %.2f) [net LED_G_D] · pad2 (%.2f, %.2f) [net GND]"
              % (pad1[0], pad1[1], pad2[0], pad2[1]))
        print("  ③ 到 R_LED_G.2 直線   = %.3f mm (pad-to-pad 真网长) · 既有闸代理量 %.3f mm · "
              "现状 %.6f ⇒ 缩短 %.3f mm (%.2f%%)"
              % (net, proxy, cur, cur - net, (cur - net) / cur * 100))
        print("  ④ 最近邻器件净距      = %s %.3f mm (net %s) · %s %.3f mm (net %s) · %s %.3f mm (net %s)"
              % (gaps[0][1], gaps[0][0], gaps[0][2],
                 gaps[1][1], gaps[1][0], gaps[1][2],
                 gaps[2][1], gaps[2][0], gaps[2][2]))
        print("  ⑤ 对 §3 坐标空间落位  = %s"
              % (("可放行带 X %.3f..%.3f × Y %.3f..%.3f" %
                  (inb["ox0"], inb["ox1"], inb["oy0"], inb["oy1"])) if inb else "★无★"))
        print("     整高自由带成员?     = %s" % ("是" if full else "否"))
        print("  ⑥ 改板 md5 影响       = ★动★ (改 D_LED_G 封装原点 ⇒ HW/PCB/demo_mainboard.kicad_pcb md5 变)")
        print("  ⑦ 余量                = 距板边 %.3f mm (判据 ≥ 0.80) · 距调试口开口 %.3f mm · 距检修口开口 %.3f mm"
              % (edge_gap,
                 rls.rect_gap(newbox, openings["调试口开口"]),
                 rls.rect_gap(newbox, openings["检修口开口"])))

    print("\n" + "=" * 96)
    print("[END] 候选终表跑完 · 只读")


if __name__ == "__main__":
    sys.exit(main())
