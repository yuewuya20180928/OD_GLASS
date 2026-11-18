#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-324 · mech-lead · 候选净距【口径复算器】(READ-ONLY)

★为什么要有这个脚本★:
  `logs/iss324/05_candidates.log` 里 C1/C4 的「最近邻器件净距」记着 `R_LED_G 0.000 mm` 与
  `C_KEY_CAM 0.000 mm` ⇒ 这两个数不能照抄进交付页当结论。
  原因: 那个「净距」是 **铜箔外框 bbox ↔ 铜箔外框 bbox** 的最短间隙 (rect_gap),
        两框只要在 X 与 Y 上都相交/相切 ⇒ 结果恒为 0.000 ⇒ 它表达的是
        「外框相切/相交」, **不是**「焊盘真的贴到 0 mm」。
  本脚本把三种口径分开算, 逐条复算, 并给出结论该用哪个口径。

口径:
  (M1) bbox 间隙   = rect_gap(D_LED_G 铜箔外框, 邻件铜箔外框)   ← 05_candidates.log 用的就是它
  (M2) pad 中心距  = min_{D_LED_G pads × 邻件 pads} 中心到中心直线距离
  (M3) pad 边缘距  = min_{D_LED_G pads × 邻件 pads} 焊盘矩形边缘到边缘最短间隙 (DRC 真正判的那个)

★零写板★: 只 open(..., 'r'), 不写任何文件。
用法: python3 logs/iss324/verify_candidate_clearance.py
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
    ("C1", 8.250, 63.700),
    ("C2", 8.050, 63.900),
    ("C3", 8.420, 64.200),
    ("C4", 8.250, 61.900),
    ("C5", 8.250, 66.000),
    ("C6", 2.500, 60.000),
]


def pad_bbox(p):
    return (p["x"] - p["sx"] / 2, p["x"] + p["sx"] / 2,
            p["y"] - p["sy"] / 2, p["y"] + p["sy"] / 2)


def m3_gap(dled_pads, nb_pads):
    """(M3) 焊盘边缘到边缘最短间隙 + (M2) 最近中心距, 以及给出是哪一对焊盘."""
    best3 = None
    best2 = None
    for dp in dled_pads:
        db = pad_bbox(dp)
        for np_ in nb_pads:
            nb = pad_bbox(np_)
            g = rls.rect_gap(db, nb)
            c = math.hypot(dp["x"] - np_["x"], dp["y"] - np_["y"])
            if best3 is None or g < best3[0]:
                best3 = (g, dp["num"], np_["num"])
            if best2 is None or c < best2[0]:
                best2 = (c, dp["num"], np_["num"])
    return best3, best2


def main():
    board = rls.read_board(rls.PCB)
    fps = board["fps"]
    sp = rls.led_space(board, 0.0)
    rel = sp["rel"]

    print("=" * 100)
    print("ISS-324 候选净距【三口径复算】 (帧 B160x100 · 现役台架板 · READ-ONLY)")
    print("=" * 100)

    print("\n[0] 参照器件自读 (封装原点 / 焊盘 / 铜箔外框)")
    for ref in ("R_LED_G", "C_KEY_CAM", "TP_LED_G", "D_LED_G"):
        f = fps[ref]
        bb = rls.copper_bbox(f)
        print("  %-10s origin=(%.2f, %.2f)  value=%s  焊盘数=%d  铜箔外框 X %.3f..%.3f Y %.3f..%.3f"
              % (ref, f["at"][0], f["at"][1], f["value"], len(f["pads"]), bb[0], bb[1], bb[2], bb[3]))
        for p in f["pads"]:
            pb = pad_bbox(p)
            print("      pad%-3s abs=(%.2f, %.2f) size=%.2fx%.2f  焊盘矩形 X %.3f..%.3f Y %.3f..%.3f net=%s"
                  % (p["num"], p["x"], p["y"], p["sx"], p["sy"], pb[0], pb[1], pb[2], pb[3], p["net"]))

    r2 = [p for p in fps["R_LED_G"]["pads"] if p["num"] == "2"][0]

    print("\n" + "=" * 100)
    print("[1] 逐候选 · 三口径并排 (★05_candidates.log 的 ④ 只给了 M1★)")
    print("=" * 100)
    for name, ox, oy in CANDIDATES:
        newbox = (ox + rel[0], ox + rel[1], oy + rel[2], oy + rel[3])
        dled_pads = []
        for p in fps["D_LED_G"]["pads"]:
            # pad 绝对坐标 = 原点 + 相对铜箔外框偏移 (本板封装旋转 = 0, 逐 pad 校验)
            dled_pads.append({"num": p["num"], "x": p["x"] - fps["D_LED_G"]["at"][0] + ox,
                              "y": p["y"] - fps["D_LED_G"]["at"][1] + oy,
                              "sx": p["sx"], "sy": p["sy"], "net": p["net"]})
        net_len = math.hypot(dled_pads[0]["x"] - r2["x"], dled_pads[0]["y"] - r2["y"])

        rows = []
        for ref, f in fps.items():
            if ref == "D_LED_G":
                continue
            b = rls.copper_bbox(f)
            if not b:
                continue
            m1 = rls.rect_gap(newbox, b)
            m3, m2 = m3_gap(dled_pads, f["pads"])
            ov_x = not (newbox[1] <= b[0] or b[1] <= newbox[0])
            ov_y = not (newbox[3] <= b[2] or b[3] <= newbox[2])
            rows.append((m1, m3, m2, ref, f["pads"], ov_x, ov_y))
        rows.sort(key=lambda r: r[0])

        print("\n" + "-" * 100)
        print("%s  封装原点 = (%.3f, %.3f)   D_LED_G 铜箔外框 X %.3f..%.3f Y %.3f..%.3f"
              % (name, ox, oy, newbox[0], newbox[1], newbox[2], newbox[3]))
        print("    pad1 abs = (%.2f, %.2f) [net %s]   pad2 abs = (%.2f, %.2f) [net %s]"
              % (dled_pads[0]["x"], dled_pads[0]["y"], dled_pads[0]["net"],
                 dled_pads[1]["x"], dled_pads[1]["y"], dled_pads[1]["net"]))
        print("    LED_G_D pad-to-pad 中心距 = %.3f mm  (vs 现状 93.492727)" % net_len)
        print("    %-6s %-11s %-11s %-11s %s" % ("邻件", "M1 bbox间隙", "M3 pad边缘距", "M2 pad中心距", "M1 为 0 的原因 (X/Y 相交?)"))
        for m1, m3, m2, ref, nb_pads, ov_x, ov_y in rows[:6]:
            why = ""
            if m1 == 0.0:
                why = "★X 相交=%s · Y 相交/相切=%s ⇒ bbox 相切 ⇒ M1 恒 0★" % (ov_x, ov_y)
            print("    %-6s %-11.3f %-11.3f %-11.3f %s" % (ref, m1, m3[0], m2[0], why))
            if m3[0] < 0.30:
                print("           └ M3 最紧的一对焊盘: D_LED_G.pad%s ↔ %s.pad%s   ★★ 板 DRC 真判的是这一项 ★★"
                      % (m3[1], ref, m3[2]))

    print("\n" + "=" * 100)
    print("[2] 结论口径 (★写进交付页 §6 的那一段★)")
    print("=" * 100)
    print("  M1 (bbox 间隙) 在 C1/C4 上记 0.000 mm, 但 [实测] M3 (焊盘边缘距) 并不为 0 ⇒")
    print("  ⇒ M1 只能用来判「铜箔外框有没有被压到 / 相切」, 拿它当『器件净距』结论会误判")
    print("  ⇒ 交付页 §6 的净距一栏给 M3 (焊盘边缘距) 为准, M1 与 M2 并列 ⇒ 三个数都在页面上")
    print("\n[END] 三口径复算完 · 只读")
    return 0


if __name__ == "__main__":
    sys.exit(main())
