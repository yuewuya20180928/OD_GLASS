#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""plan_route_reserve.py -- ★★算给 A1 那 5 条 N 腿预留【出脚走廊】的框 (★产出 PCB_ROUTE_RESERVE 串)★★

★★★**★为什么要有这个 (★2026-11-10 12:3x)★★★**
  ★**实测机制**: ★**A1 那 5 条的 N 腿, 它的【反向】出脚道都被【别的网的铜】占着**
  ⇒ ★★**⇒ 出脚级成对规划走不通 ⇒ ⇒ 真正要的是【走线级走廊预留】(★`PCB_ROUTE_RESERVE`) ★★
  ⇒ ★★**⇒ 而"预留哪个框"必须【按实测铜占位】算, 不能拍脑袋** ⇒ ★★**本脚本就是算这个** ★★

★**算法 (★全几何, ★无猜测)** ★★★
  ① 对每个 N 腿的 BTB 焊盘, 找【同排方向】的两个垂直方向 (★垂直于排针行)
  ② 对每个方向, 沿该方向检查【出脚直道长度 ESC_LEN=1.2mm】的走廊上有没有【别的网】的铜
     (★同层铜 + 异层铜都要查, ★因为 halo 是分层的)
  ③ 选【净距最大】的那个方向 = ★N 应该走的路 ⇒ ★★**把它预留下来 (★框 = 该走廊的矩形) ★★
  ④ 框的宽度 = ★线宽 + 两侧净距 (★0.25 + 2×0.20 = 0.65mm ⇒ 取 0.9mm 宽, ★留余量) ★★
  ⇒ ★**输出: 可直接贴进臂脚本的 `PCB_ROUTE_RESERVE="..."` 串** ★★

用法: bash state/pcbnew_py.sh state/plan_route_reserve.py [板] [--out <txt>]
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("PCB_LAYERS", "8")
import pcbnew  # noqa: E402

MM = 1000000.0
ESC_LEN = 1.20          # ★与 gen_pcb_routing.ESC_LEN 对齐
HALO_CLEAR = 0.20       # ★CLEAR
BOX_W = 0.90            # ★预留框宽度 (0.25 线 + 2×0.20 净距 = 0.65 ⇒ 取 0.9 留余量)

# ★A1 桶 5 条: (N 腿网, N 腿在 BTB 上的焊盘 ref, x, y)
A1 = [
    ("CSI_D0_D0_N_SRC", "J_SOM_P4.65", 22.000, 50.960),
    ("CSI_D0_D1_N_SRC", "J_SOM_P4.71", 20.800, 50.960),
    ("CSI_D0_D3_N_SRC", "J_SOM_P4.89", 17.200, 50.960),
    ("DSI_D0_D2_N_SRC", "J_SOM_P3.75", 20.000, 7.960),
    ("DSI_D0_D3_N_SRC", "J_SOM_P3.81", 18.800, 7.960),
]


def main():
    boardp = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else \
        "HW/PCB/demo_mainboard.kicad_pcb"
    outp = None
    if "--out" in sys.argv:
        outp = sys.argv[sys.argv.index("--out") + 1]

    b = pcbnew.LoadBoard(boardp)
    if b is None:
        print("★板读不出来: %s" % boardp)
        return 2

    # ★★★**★2026-11-09 21:5x 【成对预留】: 把【0.4mm pitch 的伙伴焊盘】也找出来** ★★★
    #   ★**为什么**: ★**实测 (★v76rr 臂)** ⇒ 预留框 0.9mm 宽 ⇒ 必盖住同排相邻 0.4mm 的【伙伴焊盘】
    #   ⇒ ★**单网预留 ⇒ 伙伴腿的出脚格被"预留给别人"⇒ 伙伴腿直接 0 铜**
    #   ⇒ ★**`CSI_D0_D3_P_SRC` 实测: 基线 46 段 ⇒ v76rr 臂 0 段** ★★
    #   ⇒ ★**⇒ 预留必须成对: 一个框同时留给 N 腿和它的 P 伙伴** ★★
    #   ★**几何**: 伙伴焊盘与 N 焊盘【同排】(★y 相同) 且【x 相差 0.4mm】 ⇒ 在板面找得到 ★★
    pads = []
    for p in b.GetPads():
        pos = p.GetPosition()
        try:
            ref = p.GetParent().GetReference()
        except Exception:
            try:
                ref = p.GetParentFootprint().GetReference()
            except Exception:
                ref = "?"
        pads.append((p.GetNetname(), ref, p.GetNumber(), pos.x / MM, pos.y / MM))

    def partner_of(net, x, y):
        """找【同排相邻 0.4mm】的伙伴焊盘 ⇒ 返回它的网名 (★找不到返回 None)

        ★**优先认【成对的伙伴】(★`_N`↔`_P` 互换) ⇒ 避免认错成邻座的另一条腿** ★
        """
        cands = []
        for (pn, pref, pnum, px, py) in pads:
            if pn == net or not pn:
                continue
            if abs(py - y) > 0.01:
                continue
            d = px - x
            if 0.3 <= abs(d) <= 0.5:
                cands.append((abs(d), pn, pref, pnum, d))
        if not cands:
            return None
        # ★★**★2026-11-10 00:1x 【修: ★伙伴【只认真差分配对】(★相邻排针不算伙伴)】★★** ★★★
        #   ★**实测理由**: ★**0.5mm pitch 的排针上, `JTAG_TDO` 的"伙伴"被认成相邻的 `JTAG_TDI`**
        #     ⇒ ★**成对预留把 TDO 的道也开放给 TDI ⇒ ⇒ 正是【互相挡死】的成因 ⇒ ⇒ 错** ★★
        #   ⇒ ★**⇒ 只认 `_N`↔`_P` 名字对; ★认不到就【不成对】(★单网独占预留, ★反而更对)** ★★
        for _pfx, _sfx in (("_N", "_P"), ("_P", "_N")):
            cand = [c for c in cands if c[1].replace(_pfx, _sfx, 1) == net]
            if cand:
                cand.sort()
                return (cand[0][0], cand[0][1], cand[0][2], cand[0][3])
        # ★★**★不做【任意相邻】兜底 (★那会把相邻排针误当伙伴)** ★★
        return None

    # ★铜图元 (走线 / 过孔), 按层
    copper = []
    for t in b.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T:
            p = t.GetPosition()
            copper.append((t.GetNetname(), None, "VIA", p.x / MM, p.y / MM, 0.0, 0.0, 0.6))
        else:
            s, e = t.GetStart(), t.GetEnd()
            copper.append((t.GetNetname(), b.GetLayerName(t.GetLayer()), "TRK",
                           s.x / MM, s.y / MM, e.x / MM, e.y / MM, t.GetWidth() / MM))

    def worst_clearance(net, x, y, dx, dy):
        """沿 (dx,dy) 从 (x,y) 走 ESC_LEN, 与【别的网】铜的最小净距 (★同层算铜边距; 异层按 0.2 净距算)"""
        worst = 99.0
        who = "-"
        for (bn, lay, kind, cx, cy, ex, ey, w) in copper:
            if bn == net:
                continue
            if kind == "VIA":
                for k in range(25):
                    t = k / 24.0
                    px, py = x + dx * ESC_LEN * t, y + dy * ESC_LEN * t
                    d = math.hypot(px - cx, py - cy) - w / 2.0 - 0.125
                    if d < worst:
                        worst, who = d, "%s[VIA]" % bn
                continue
            dx2, dy2 = ex - cx, ey - cy
            L2 = dx2 * dx2 + dy2 * dy2
            for k in range(25):
                t = k / 24.0
                px, py = x + dx * ESC_LEN * t, y + dy * ESC_LEN * t
                if L2 == 0:
                    d = math.hypot(px - cx, py - cy) - w / 2.0 - 0.125
                else:
                    u = max(0.0, min(1.0, ((px - cx) * dx2 + (py - cy) * dy2) / L2))
                    qx, qy = cx + u * dx2, cy + u * dy2
                    d = math.hypot(px - qx, py - qy) - w / 2.0 - 0.125
                if d < worst:
                    worst, who = d, "%s[%s]" % (bn, lay)
        return worst, who


    # ★★★★**★2026-11-10 00:0x 【泛化: ★任意网都能算走廊 + ★自动判断排针行方向】★★★★** ★★★
    def fp_pads(ref):
        """取某封装的所有焊盘坐标 (★用来判断【排针行方向】)"""
        out = []
        for p in b.GetPads():
            try:
                r = p.GetParent().GetReference()
            except Exception:
                try:
                    r = p.GetParentFootprint().GetReference()
                except Exception:
                    r = "?"
            if r == ref:
                pos = p.GetPosition()
                out.append((pos.x / MM, pos.y / MM))
        return out

    def escape_dirs(ref, x, y):
        """★判断【这个焊盘的出脚方向】(★垂直于排针行)⇒ 返回 [(dx,dy,tag), ...]"""
        pts = fp_pads(ref)
        if len(pts) >= 2:
            sx = max(q[0] for q in pts) - min(q[0] for q in pts)
            sy = max(q[1] for q in pts) - min(q[1] for q in pts)
            # ★**排针行是"跨度大"的那个方向 ⇒ 出脚方向 = 垂直于它** ★★
            if sx >= sy:
                return [(0.0, 1.0, "+y"), (0.0, -1.0, "-y")]
            return [(1.0, 0.0, "+x"), (-1.0, 0.0, "-x")]
        return [(0.0, 1.0, "+y"), (0.0, -1.0, "-y")]

    def nets_of(name):
        """★按【网名】找它所有焊盘 (★供 --nets 用)"""
        out = []
        for p in b.GetPads():
            if p.GetNetname() != name:
                continue
            pos = p.GetPosition()
            try:
                ref = p.GetParent().GetReference()
            except Exception:
                try:
                    ref = p.GetParentFootprint().GetReference()
                except Exception:
                    ref = "?"
            out.append((name, ref, p.GetNumber(), pos.x / MM, pos.y / MM))
        return out


    # ★★★★**★2026-11-10 01:2x 【★--from-drc 模式: ★给【每个未连接端点所在焊盘】留一条道】★★★★** ★★★
    #   ★**为什么**: ★**"给网留最好的道"是错的 ⇒ ★**真正卡住的是【某个具体焊盘】出不来**
    #     ⇒ ★★**⇒ 直接读 DRC 的 unconnected_items, ★取其中【没连上那一侧】的焊盘 ⇒ ★给它留道** ★★
    #   ★**⇒ 这比"按网名猜"精确得多: ★★**每一条未连接都有确定的焊盘** ★★
    def unc_pads(drc_path):
        """从 DRC json 里取【未连接的焊盘端】⇒ [(net, ref.pad, x, y), ...]"""
        import json
        import re as _re
        d = json.load(open(drc_path, encoding="utf-8"))
        out = []
        for it in (d.get("unconnected_items") or []):
            for sub in (it.get("items") or []):
                desc = sub.get("description", "")
                m = _re.match(r"Pad (\d+) \[([^\]]+)\] of (\S+) on", desc)
                if not m:
                    continue
                pnum, net, ref = m.group(1), m.group(2), m.group(3)
                # ★★**★要带【焊盘号】(★否则同封装的多个焊盘会被当成一个 ⇒ ★★**漏掉真正卡住的那个**)★★★ ★★
                ref = "%s.%s" % (ref, pnum)
                pos = sub.get("pos") or {}
                out.append((net, ref, float(pos.get("x", 0)), float(pos.get("y", 0))))
        return out

    boxes = []
    _boxrec = []   # ★[x0,y0,x1,y1,允许网集合] ★★**★用于重叠合并** ★★
    lines = ["★给 A1 那 5 条 N 腿预留的出脚走廊 (★全几何算出)★", ""]
    # ★★**【--from-drc: ★按 DRC 的未连接端点逐个留道 (★最精确)】★★** ★★★
    _extra = []
    _from_drc = False
    if "--from-drc" in sys.argv:
        _dp = sys.argv[sys.argv.index("--from-drc") + 1]
        _ups = unc_pads(_dp)
        _seen_up = set()
        for (_n, _r, _x, _y) in _ups:
            if (_n, _r) in _seen_up:
                continue
            _seen_up.add((_n, _r))
            _extra.append((_n, _r, _x, _y))
        _from_drc = True
        lines = ["★按 DRC 未连接端点逐个留道 (★%s)★" % _dp, ""]
    # ★★**【--nets: ★额外要留道的网 (★按网名自动找焊盘 + 自动判方向)】★★** ★★★
    _extra2 = []
    if "--nets" in sys.argv:
        _want = [t.strip() for t in sys.argv[sys.argv.index("--nets") + 1].split(",") if t.strip()]
        for _n in _want:
            _pin = None
            if "@" in _n:            # ★★**NET@REF.PAD** ⇒ ★只认这个焊盘 (★出脚点) ★★
                _n, _pin = _n.split("@", 1)
            _ps = nets_of(_n)
            if not _ps:
                lines.append("★ ⚠️ %s 在板上找不到焊盘 ⇒ 跳过" % _n)
                continue
            for (_pn, _pref, _pnum, _px, _py) in _ps:
                _full = "%s.%s" % (_pref, _pnum)
                if _pin is not None and _full != _pin:
                    continue
                _extra2.append((_pn, _full, _px, _py))
            if _pin is not None and not any("%s.%s" % (r, n) == _pin for (_pn, r, n, _x, _y) in nets_of(_n)):
                lines.append("★ ⚠️ %s 上没有焊盘 %s ⇒ 跳过" % (_n, _pin))
        lines.append("★ 额外留道网 (★--nets): %s" % (", ".join(_want)))
        lines.append("")

    # ★★★★**★2026-11-10 00:2x 【★每网只留【最好的一条】道 (★跨该网所有焊盘取最优)】★★★★** ★★★
    #   ★**为什么**: ★**一个网常有好几个焊盘 (★如 `JTAG_TDO` = J_DEBUG.4 + R_JTAG_TDO.2)**
    #     ⇒ ★**真正的出脚点只有一个 (★排针那个) ⇒ ★别的焊盘那边本就走不了 (★净距 −0.25)** ★★
    #     ⇒ ★**⇒ 留多个框 = 把【别人能用的道】封死 ⇒ ⇒ 反而有害** ★★
    #   ⇒ ★**⇒ 每个网: ★【跨所有焊盘 × 所有方向】取净距最大的一条 ⇒ ★只留那一个框** ★★
    #   ★★**★【★不按净距正负取舍★】**: ★**负净距是【在已布好的板上】量的 (★P 的铜已经占着道)**
    #     ⇒ ★★**那正是我们要解决的拥堵 ⇒ ⇒ 负净距恰恰是【最该留道】的地方** ★★ ★★★
    _cand_by_net = {}
    for (net, ref, x, y) in (A1 + _extra + _extra2):
        for (dx, dy, tag) in escape_dirs(ref, x, y):
            w, who = worst_clearance(net, x, y, dx, dy)
            # ★★**★--from-drc 模式下【按焊盘分候选】(★每个未连接焊盘各要一条道)★★★ ★★
            #   ★**否则同一网的多个焊盘会被合并成一条 ⇒ ★★**恰好漏掉那些真正卡住的焊盘** ★★
            _key = (net, ref) if _from_drc else net
            _c = (w, tag, dx, dy, who, ref, x, y)
            if _key not in _cand_by_net or w > _cand_by_net[_key][0]:
                _cand_by_net[_key] = _c

    # ★★★**★2026-11-10 00:3x 【修: ★每个网只打印一次】★★★ ★★
    #   ★**为什么**: ★**`--nets` 的网常有好几个焊盘 (★`UART_TX` = J_UART.1 + TP_UART.1 + J_SOM_P2.7)
    #     ⇒ 旧循环按【焊盘】遍历 ⇒ 同一个网的日志重复 N 次 (★读数时容易误以为有多个候选) ★**
    #   ★**注意**: ★**框的生成逻辑逐位不变 (★框本来就是按【网的最优候选】算的) ⇒ 只改打印 ★★
    _net_order = []
    for (_n, _r, _x, _y) in A1 + _extra:
        if _n not in _net_order:
            _net_order.append(_n)

    for net in _net_order:
        # ★只对这个网【最好的那条】候选打日志 (★其余焊盘/方向只做诊断)
        _c = _cand_by_net.get((net, ref) if _from_drc else net)
        if _c is None:
            continue
        best = (_c[0], _c[1], _c[2], _c[3], _c[4])
        _bref, _bx, _by = _c[5], _c[6], _c[7]
        lines.append("★ %s @ %s (%.3f, %.3f)" % (net, _bref, _bx, _by))
        lines.append("    ⇒ ★★**留 %s 方向 (净距 %+.3fmm, 最近 %s) —— 该网所有焊盘里最好的一条** ★★"
                     % (best[1], best[0], best[4]))
        # ★框: 沿方向的走廊 + 宽度
        if best[2] == 0.0 and best[3] > 0:       # ★+y
            x0, x1 = _bx - BOX_W / 2.0, _bx + BOX_W / 2.0
            y0, y1 = _by, _by + ESC_LEN + 0.2
        elif best[2] == 0.0:                      # ★-y
            x0, x1 = _bx - BOX_W / 2.0, _bx + BOX_W / 2.0
            y0, y1 = _by - ESC_LEN - 0.2, _by
        elif best[2] > 0:                        # ★+x
            x0, x1 = _bx, _bx + ESC_LEN + 0.2
            y0, y1 = _by - BOX_W / 2.0, _by + BOX_W / 2.0
        else:                                    # ★-x
            x0, x1 = _bx - ESC_LEN - 0.2, _bx
            y0, y1 = _by - BOX_W / 2.0, _by + BOX_W / 2.0
        # ★★★**★成对预留**: 框里同时留 N 腿 + 它的【真差分】P 伙伴 (★否则伙伴腿被预留打死) ★★★
        _pt = partner_of(net, _bx, _by)
        _allow = net if _pt is None else "%s+%s" % (net, _pt[1])
        if _pt is not None:
            lines.append("    ★成对预留: 伙伴 = %s (%s.%s · Δx=%.3fmm) ⇒ 同一框留给 %s"
                         % (_pt[1], _pt[2], _pt[3], _pt[0], _allow))
        else:
            lines.append("    ★单网独占预留 (★无真差分伙伴)")
        # ★★★★**★2026-11-10 01:3x 【★重叠框合并 (★否则框互相封死 ⇒ 自己打自己)】★★★★** ★★★
        #   ★**实测**: ★**`--from-drc` 模式下多个未连接焊盘挨得很近 ⇒ 框互相重叠**
        #     ⇒ ★**A 的框会盖掉 B 的框 ⇒ ⇒ B 的"专属道"根本用不了** ★★
        #   ⇒ ★★**⇒ 重叠时: ★【合并成一个多网框】(★机制本来就支持一格存【允许网集合】) ★★
        #     ⇒ ★**⇒ 两个网都有机会用它 (★比互相封死好) ★★
        _hit = None
        for _i, _b in enumerate(_boxrec):
            if not (x1 <= _b[0] or x0 >= _b[2] or y1 <= _b[1] or y0 >= _b[3]):
                _hit = _i
                break
        if _hit is None:
            _boxrec.append([x0, y0, x1, y1, set(_allow.split("+"))])
        else:
            # ★★**★只合并【允许网集合】, ★★**不动几何** ★★
            #   ★**理由**: ★**若把矩形也合并放大 ⇒ ★会【传递性吞并】(★实测: 30 个框塌成 1 个)**
            #     ⇒ ★**⇒ 保留首个框的几何, ★把后来的网也加进它的允许集合** ★★
            #   ⇒ ★**⇒ 这两个网【共享】这段走廊 (★比互相封死好, ★也不炸面积)** ★★
            _b = _boxrec[_hit]
            _b[4].update(_allow.split("+"))
            lines.append("    ★★**⇒ 与已有框重叠 ⇒ 【共享该走廊】(★允许网集合 += %s) ★★" % _allow)
        lines.append("")

    for _b in _boxrec:
        _allow_s = "+".join(sorted(_b[4]))
        boxes.append("%s:0,%.3f,%.3f,%.3f,%.3f" % (_allow_s, _b[0], _b[1], _b[2], _b[3]))
    lines.append("★PCB_ROUTE_RESERVE 串 (★可直接贴进臂脚本):")
    lines.append('  PCB_ROUTE_RESERVE="%s"' % ";".join(boxes))
    text = "\n".join(lines)
    if outp:
        open(outp, "w", encoding="utf-8").write(text)
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
