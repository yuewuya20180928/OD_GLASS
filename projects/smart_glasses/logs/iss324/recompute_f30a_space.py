#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-324 · mech-lead · 双板框坐标空间独立推导 (READ-ONLY)

口径:
  假设 1 (现役) = 帧 B160x100 (160.00 x 100.00 台架板) —— 盘上实测坐标
  假设 2 (产品) = 帧 F30A (60.00 x 30.00 套 A) —— MECH/BOARD_GEOM_30MM.md §1/§2/§3
★两个假设的坐标口径不同, 不许互相代入:
  B160x100 = 【封装原点窗口】口径 (器件铜箔外框不越界)
  F30A     = 【器件中心窗口】口径 (器件占位 2.70 x 1.60 的中心)
★零写板★: 本脚本只算, 不写任何文件。
用法: python3 logs/iss324/recompute_f30a_space.py
"""
import math

# ---------------------------------------------------------------- F30A 常量 (出处逐条标注)
PCB_L, PCB_W = 60.00, 30.00          # MECH/BOARD_GEOM_30MM.md §1
EDGE_KEEPOUT = 0.80                  # MECH/BOARD_GEOM_30MM.md §1 (器件边距带)
LED_BBOX_X, LED_BBOX_Y = 2.70, 1.60  # 0805 占位 fab bbox (HW/PART_SELECTION_GAPS_CLOSEOUT.md:76)
SOC_POS = (15.00, 32.20, 6.95, 23.05)        # BOARD_GEOM_30MM.md §2 SoC 封装体占位
SOC_ESCAPE = (14.20, 33.00, 6.15, 23.85)     # BOARD_GEOM_30MM.md §2 逃线带 (MECH 0.80/边口径)
JCHG_KEEPOUT = (0.00, 3.00, 11.75, 18.25)    # BOARD_GEOM_30MM.md §2 J_CHG 座体 keep-out
PIN_SET_A = {"P1": (8.00, 15.00, 2.00), "P2": (52.00, 15.00, 2.00),
             "S1": (8.00, 10.00, 1.40), "S2": (52.00, 20.00, 1.40)}  # BOARD_GEOM_30MM.md §3 套 A
CRIT = 0.60                           # 2 x TOL['fdm_part'] (MECH/service_port_check.py CRIT)
COVER_FLANGE = 1.50                   # 盖板搭边 (service_port_check.py BASE['cover_flange'])
OPEN_X0, OPEN_X1 = 49.21, 59.41       # 检修口开口 (jd_x0=50.50 / 2x5 / content 7.62 / cl 1.29)
CLR_SWEEP = (0.0, 0.10, 0.20, 0.50)


def bands_f30a(clr=0.0):
    """轴对齐矩形差集 ⇒ 可放行带 (器件中心坐标口径)。自写实现。"""
    hx, hy = LED_BBOX_X / 2.0, LED_BBOX_Y / 2.0
    win_x = (EDGE_KEEPOUT + hx, PCB_L - EDGE_KEEPOUT - hx)
    win_y = (EDGE_KEEPOUT + hy, PCB_W - EDGE_KEEPOUT - hy)
    port_x = (OPEN_X0 - COVER_FLANGE, min(PCB_L, OPEN_X1 + COVER_FLANGE))
    blocks = [
        ("SoC 逃线带 (0.80/边)", SOC_ESCAPE),
        ("SoC 封装体占位", SOC_POS),
        ("J_CHG 座体 keep-out", JCHG_KEEPOUT),
        ("检修口开口 + 盖板搭边", (port_x[0], port_x[1], 0.0, PCB_W)),
    ]
    holes = []
    for tag, (hx_, hy_, hd) in PIN_SET_A.items():
        r = hd / 2.0 + CRIT
        holes.append((tag, (hx_ - r, hx_ + r, hy_ - r, hy_ + r)))
    objs = [(n, (b[0] - clr, b[1] + clr, b[2] - clr, b[3] + clr)) for n, b in blocks]
    objs += [(n, (b[0] - clr, b[1] + clr, b[2] - clr, b[3] + clr)) for n, b in holes]

    cuts = sorted({win_x[0], win_x[1]}
                  | {b[0] for _, b in objs} | {b[1] for _, b in objs})
    out = []
    for a, b in zip(cuts[:-1], cuts[1:]):
        if b - a <= 1e-9:
            continue
        xc = (a + b) / 2.0
        if not (win_x[0] <= xc <= win_x[1]):
            continue
        ys = [(win_y[0], win_y[1])]
        for _, (bx0, bx1, by0, by1) in objs:
            if not (bx0 <= xc <= bx1):
                continue
            nxt = []
            for (y0, y1) in ys:
                if by1 <= y0 or by0 >= y1:
                    nxt.append((y0, y1))
                    continue
                if by0 > y0:
                    nxt.append((y0, by0))
                if by1 < y1:
                    nxt.append((by1, y1))
            ys = nxt
        for (y0, y1) in ys:
            if y1 - y0 <= 1e-9:
                continue
            out.append({"x0": a, "x1": b, "y0": y0, "y1": y1, "w": b - a, "h": y1 - y0})
    merged = []
    for bd in out:
        if merged and abs(merged[-1]["x1"] - bd["x0"]) < 1e-9 \
                and abs(merged[-1]["y0"] - bd["y0"]) < 1e-9 \
                and abs(merged[-1]["y1"] - bd["y1"]) < 1e-9:
            merged[-1]["x1"] = bd["x1"]
            merged[-1]["w"] = merged[-1]["x1"] - merged[-1]["x0"]
        else:
            merged.append(dict(bd))
    full = [b for b in merged
            if abs(b["y0"] - win_y[0]) < 1e-6 and abs(b["y1"] - win_y[1]) < 1e-6]
    return {"clr": clr, "win_x": win_x, "win_y": win_y, "bands": merged,
            "full": full, "port_x": port_x}


def main():
    print("=" * 80)
    print("ISS-324 recompute_f30a_space.py · 帧 F30A (60x30 套 A) 独立推导")
    print("=" * 80)
    print("\n[A] 常量与出处")
    print("    板 60.00 x 30.00 · 器件边距带 0.80 · LED 占位 bbox %.2f x %.2f (中心口径)"
          % (LED_BBOX_X, LED_BBOX_Y))
    print("    检修口开口 X %.2f..%.2f (盖板搭边 %.2f ⇒ 抢位 X %.2f..%.2f)"
          % (OPEN_X0, OPEN_X1, COVER_FLANGE, OPEN_X0 - COVER_FLANGE,
             min(PCB_L, OPEN_X1 + COVER_FLANGE)))
    print("    避让矩形 = SoC 逃线带 %s + SoC 封装体 %s + J_CHG keep-out %s + 套A 四孔(加 CRIT %.2f 保护区)"
          % (SOC_ESCAPE, SOC_POS, JCHG_KEEPOUT, CRIT))

    print("\n[B] 净距敏感度 (F30A · 器件中心口径)")
    for clr in CLR_SWEEP:
        r = bands_f30a(clr)
        print("    clr %.2f ⇒ 可放行带 %d 条 · 整高带 %d 条" % (clr, len(r["bands"]), len(r["full"])))
        for f in r["full"]:
            print("            整高带 X %.3f..%.3f (宽 %.3f)  Y %.3f..%.3f"
                  % (f["x0"], f["x1"], f["w"], f["y0"], f["y1"]))

    r0 = bands_f30a(0.0)
    print("\n[C] clr=0.00 全部可放行带 (X 段 × Y 段)")
    for b in r0["bands"]:
        print("      X %7.3f..%7.3f (w %6.3f)  ×  Y %6.3f..%6.3f (h %6.3f)"
              % (b["x0"], b["x1"], b["w"], b["y0"], b["y1"], b["h"]))

    print("\n[D] 首选块 (整高最宽) 的可用面积")
    for f in sorted(r0["full"], key=lambda b: -b["w"]):
        print("      X %.3f..%.3f (宽 %.3f) × Y %.3f..%.3f (高 %.3f) ⇒ 面积 %.2f mm²"
              % (f["x0"], f["x1"], f["w"], f["y0"], f["y1"], f["h"], f["w"] * f["h"]))

    print("\n[E] 与现役板 (B160x100) 的口径差异 (不许混用)")
    print("      F30A 本表 = 器件【中心】坐标; B160x100 表 = 封装【原点】坐标")
    print("      ⇒ 同一颗 D_LED_G (占位 2.70 x 1.60) 在 F30A 上中心 X 至少要比原点 X 小 1.35")
    print("      ⇒ 两套坐标的数【不可互相代入】(MECH/BOARD_ONEPASS_MECH_SYNC.md §1 帧声明同口径)")

    print("\n[END] F30A 独立推导完 · 只算不写")


if __name__ == "__main__":
    main()
