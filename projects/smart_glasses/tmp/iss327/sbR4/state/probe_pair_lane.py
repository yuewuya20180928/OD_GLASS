#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
★ 差分对【车道几何】探针 (★2026-11-10 03:2x 新写★)
=================================================================
★ 目的: 量清 【"P 通 N 不通"】到底是【物理不可能】还是【被已通的 P 腿堵在车道里】
★ 方法:
  ★ 1) 读 v76ru 的预留串 (★车道框★)
  ★ 2) 读 v76ru 终板, 找每条差分腿在【车道框内】有没有铜
  ★ 3) 对【一腿有铜 / 另一腿无铜】的车道:
       - 量已通腿铜在【横向】(垂直于出脚方向) 的 X/Y 范围
       - 量未通腿焊盘的横向坐标
       - 算【未通腿从焊盘直出】到【已通腿铜边缘】的真实净距
       - 算【车道框】在横向的宽度, 以及已通腿铜两侧各剩多少空
★ 判据:
  ★ · 横向可走宽度 = 框宽 - 已通腿铜宽 - 两侧余量
  ★ · 若【直出净距 < 0.20】⇒ 物理不可能 ⇒ 【必须侧移】
  ★ · 若【侧移后仍无空】⇒ 车道太窄 ⇒ 【加宽车道才有用】
★ 用法: bash state/pcbnew_py.sh state/probe_pair_lane.py [板文件] [预留串文件]
"""
import sys, os, re

MM = 1e6
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

BOARD = sys.argv[1] if len(sys.argv) > 1 else "/tmp/chain_v76ru/final_chain.kicad_pcb"
RESF = sys.argv[2] if len(sys.argv) > 2 else "/tmp/v76ru_reserve.txt"

CLR = 0.20          # ★板规则最小净距 (mm)
W_SIG = 0.25        # ★信号线宽 (mm)
HALF = W_SIG / 2.0


def mm(v):
    return v / MM


def load_reserve(path):
    out = []
    with open(path) as f:
        txt = f.read().strip()
    for item in txt.split(";"):
        item = item.strip()
        if not item or ":" not in item:
            continue
        nets, rect = item.rsplit(":", 1)
        p = [float(x) for x in rect.split(",")]
        if len(p) < 5:
            continue
        out.append((nets.split("+"), p[1], p[2], p[3], p[4]))   # layer, x0,y0,x1,y1
    return out


def main():
    import pcbnew
    bd = pcbnew.LoadBoard(BOARD)

    # ---- 收集所有铜 (走线+过孔) 与焊盘 ----
    tracks = []
    for t in bd.GetTracks():
        nn = t.GetNetname()
        if not nn:
            continue
        if t.GetClass() != "PCB_TRACK":
            continue          # ★只算走线 (★过孔 GetWidth 需层参数, 且不参与"车道被占"判断★)
        tracks.append((nn, mm(t.GetStart().x), mm(t.GetStart().y),
                       mm(t.GetEnd().x), mm(t.GetEnd().y), mm(t.GetWidth())))
    pads = []
    for fp in bd.GetFootprints():
        for pd in fp.Pads():
            nn = pd.GetNetname()
            if not nn:
                continue
            pos = pd.GetPosition()
            pads.append((nn, mm(pos.x), mm(pos.y),
                         pd.GetPadName(), fp.GetReference()))
    print("== 板: %s" % BOARD)
    print("   走线/过孔 = %d · 焊盘 = %d" % (len(tracks), len(pads)))

    boxes = load_reserve(RESF)
    print("== 预留框 = %d\n" % len(boxes))

    rows = []
    for nets, x0, y0, x1, y1 in boxes:
        if len(nets) < 2:
            continue
        w = x1 - x0
        h = y1 - y0
        # ★出脚方向: 框是"长条", 长轴=行进方向, 短轴=横向(两腿并排方向)
        lateral_is_x = (w <= h)
        lat_lo, lat_hi = (x0, x1) if lateral_is_x else (y0, y1)
        long_lo, long_hi = (y0, y1) if lateral_is_x else (x0, x1)
        # 纵向范围要跟车道重叠才算
        for net in nets:
            # 该网在车道内的铜
            seg = []
            for nn, sx, sy, ex, ey, wdt in tracks:
                if nn != net:
                    continue
                # ★★铜必须【完全落在车道框内】才算"占住车道" ★★
                if (min(sx, ex) < x0 - 1e-6 or max(sx, ex) > x1 + 1e-6 or
                        min(sy, ey) < y0 - 1e-6 or max(sy, ey) > y1 + 1e-6):
                    continue
                seg.append((sx, sy, ex, ey, wdt))
            if not seg:
                continue
            # 横向范围(含半宽)
            lat_min = 1e9
            lat_max = -1e9
            for sx, sy, ex, ey, wdt in seg:
                a = sx if lateral_is_x else sy
                b = ex if lateral_is_x else ey
                lo = min(a, b) - wdt / 2.0
                hi = max(a, b) + wdt / 2.0
                lat_min = min(lat_min, lo)
                lat_max = max(lat_max, hi)
            rows.append((net, nets, lat_min, lat_max, lat_lo, lat_hi,
                         long_lo, long_hi, lateral_is_x, w, h, len(seg)))

    # ---- 汇总: 每个车道里【有铜的腿】对【没铜的腿】的挤压 ----
    print("%-22s %-22s %-8s %-8s %-8s %-8s %s" %
          ("车道(网集)", "已通腿", "铜横min", "铜横max", "框横min", "框横max", "判定"))
    print("-" * 110)
    by_box = {}
    for net, nets, lmin, lmax, blo, bhi, glo, ghi, latx, w, h, n in rows:
        by_box.setdefault(tuple(nets), []).append((net, lmin, lmax, blo, bhi, glo, ghi, latx))
    n_pair_single = 0
    for nets, items in sorted(by_box.items()):
        if len(items) < 1:
            continue
        for net, lmin, lmax, blo, bhi, glo, ghi, latx in items:
            # 找同车道里没铜的腿
            missing = [n2 for n2 in nets
                       if n2 != net and n2 not in [i[0] for i in items]]
            if not missing:
                continue
            n_pair_single += 1
            # 未通腿焊盘的横向坐标
            pad_lat = None
            for pn, px, py, padn, ref in pads:
                if pn in missing:
                    pad_lat = px if latx else py
                    break
            # 已通腿铜离框边的空隙
            gap_lo = lmin - blo
            gap_hi = bhi - lmax
            if pad_lat is not None:
                # 未通腿从焊盘直出 ⇒ 与已通腿铜边缘的净距
                if pad_lat < lmin:
                    d = lmin - pad_lat - HALF
                elif pad_lat > lmax:
                    d = pad_lat - lmax - HALF
                else:
                    d = -999
                direct = "直出净距%.3f%s" % (d, "" if d >= 0 else " ★负★")
            else:
                direct = "无焊盘?"
            # 车道横向可用空隙(不含已通腿)
            free = (lmax - lmin)
            verdict = ""
            if gap_lo < CLR + HALF and gap_hi < CLR + HALF:
                verdict = "★两侧都不够⇒框太窄★"
            print("%-22s %-22s %-8.3f %-8.3f %-8.3f %-8.3f %s | 空左%.3f 空右%.3f %s" %
                  ("+".join(nets)[:22], net[:22], lmin, lmax, blo, bhi,
                   direct, gap_lo, gap_hi, verdict))
    print("\n== 有铜腿压在车道里的车道数 = %d" % n_pair_single)


if __name__ == "__main__":
    main()
