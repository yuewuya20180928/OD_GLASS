#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""plan_part_moves.py -- ★★把【布局冲突清单】变成【可直接用的 PCB_PART_POS 钉位串】★★

★★★**★2026-11-09 19:5x 改版 (★兄弟 session 10:40 派的活)★★★**
  ★**原版只读官方板坐标 ⇒ ★★**臂上不能用** (★官方板与臂的布局基础不同: ★`R_SEL_*` 全家等 16 个器件位置不一致)
  ⇒ ★**现在支持: ★板路径 + DRC 路径 + [可选] 另一块板(★用于校验"位置一致"才可套用)** ★★
  ⇒ ★★**⇒ 用法: ★在【臂的板】上算, 才能出【能贴到那个臂的】钉位串** ★★

★★★**★修掉的两个坑 (★原版)★★★★** ★★★
  · ★**坑①**: ★**同一 ref 在一批里可能出现两次** (★如 `C_KEY_CAM` 的 0.3右 与 1.0右 两条记录) ⇒ ★★**钉位串里同一个 ref 只能出现一次 ⇒ ★★**现在按"同 ref 取位移最小"去重** ★★★
  · ★**坑②**: ★**器件原点的偏移算错** (★第一版把"目标焊盘位置"直接当"器件原点") ⇒ ★★**现在: 新原点 = 目标焊盘位置 + (器件原点 − 该焊盘原位置)** ★★★

★★★**★附加校验 (★新)★★★** ★★★
  · ★★**【两板位置一致】才允许套用** (★用 --against <另一块板> 传入) ⇒ ★★**避免"拿 A 板的位移挪 B 板"** ★★ ★★★
  · ★**钉位串按位移升序** ⇒ ★**最小改动优先** ★★

用法:
  bash state/pcbnew_py.sh state/plan_part_moves.py --board <板> --drc <drc.json> \
        [--against <另一块板>] [--max-d 0.8] [--limit 12] [--out <txt>]
"""
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("PCB_LAYERS", "8")
import pcbnew  # noqa: E402

MM = 1000000.0


def cross(a, b, c, d):
    def o(p, q, r):
        v = (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
        return 0 if abs(v) < 1e-12 else (1 if v > 0 else -1)
    o1, o2 = o(a, b, c), o(a, b, d)
    o3, o4 = o(c, d, a), o(c, d, b)
    return o1 != o2 and o3 != o4


def load_board(path):
    b = pcbnew.LoadBoard(path)
    if b is None:
        raise SystemExit("★板读不出来: %s" % path)
    return b


def collect(b):
    pads = {}
    fpinfo = {}
    fp_by_ref = {}
    for fp in b.GetFootprints():
        ref = fp.GetReference()
        pos = fp.GetPosition()
        fpinfo[ref] = (pos.x / MM, pos.y / MM)
        fp_by_ref[ref] = fp
        for p in fp.Pads():
            if p.GetNetname():
                pads.setdefault(p.GetNetname(), []).append(
                    (ref, p.GetNumber(), p.GetPosition().x / MM, p.GetPosition().y / MM))
    tracks = []
    for t in b.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T:
            continue
        s, e = t.GetStart(), t.GetEnd()
        tracks.append((t.GetNetname(), (s.x / MM, s.y / MM), (e.x / MM, e.y / MM)))
    return pads, fpinfo, fp_by_ref, tracks


def npads_of(fp):
    return len([p for p in fp.Pads() if p.GetNetname()])


def main():
    boardp = "HW/PCB/demo_mainboard.kicad_pcb"
    drcp = "/tmp/_drc45.json"
    against = None
    max_d = 0.8
    limit = 12
    outp = None
    a = sys.argv[1:]
    for i, x in enumerate(a):
        if x == "--board" and i + 1 < len(a):
            boardp = a[i + 1]
        if x == "--drc" and i + 1 < len(a):
            drcp = a[i + 1]
        if x == "--against" and i + 1 < len(a):
            against = a[i + 1]
        if x == "--max-d" and i + 1 < len(a):
            max_d = float(a[i + 1])
        if x == "--limit" and i + 1 < len(a):
            limit = int(a[i + 1])
        if x == "--out" and i + 1 < len(a):
            outp = a[i + 1]

    b = load_board(boardp)
    pads, fpinfo, fp_by_ref, tracks = collect(b)
    d = json.load(open(drcp, encoding="utf-8"))
    unc_nets = set()
    for it in (d.get("unconnected_items") or []):
        for m in re.finditer(r"\[([A-Za-z0-9_]+)\]", json.dumps(it, ensure_ascii=False)):
            unc_nets.add(m.group(1))

    # ★另一块板的位置 (★用于"位置一致"校验)
    apos = None
    if against:
        ab = load_board(against)
        _, apos, _, _ = collect(ab)

    # ★候选: 走廊被横穿 ⇒ 求最小可行垂直位移
    cands = []
    for net in sorted(unc_nets):
        pl = pads.get(net) or []
        if len(pl) < 2:
            continue
        for i in range(len(pl)):
            for j in range(i + 1, len(pl)):
                (ra, na, ax, ay), (rb, nb_, bx, by) = pl[i], pl[j]
                if math.hypot(bx - ax, by - ay) < 1.0:
                    continue
                hit = [(tn, s, e) for (tn, s, e) in tracks if tn != net and cross((ax, ay), (bx, by), s, e)]
                if not hit:
                    continue
                vx, vy = bx - ax, by - ay
                L = math.hypot(vx, vy)
                nx, ny = -vy / L, vx / L
                for dd in (0.3, 0.5, 0.8, 1.0, 1.5, 2.0, 3.0):
                    if dd > max_d:
                        break
                    for sgn in (1, -1):
                        tgt = (bx + sgn * dd * nx, by + sgn * dd * ny)
                        if not any(cross((ax, ay), tgt, s2, e2) for (_tn, s2, e2) in hit):
                            cands.append(dict(net=net, a=(ra, na, ax, ay), b=(rb, nb_, bx, by),
                                              d=dd, sgn=sgn, tgt=tgt,
                                              hit=sorted(set(h[0] for h in hit))))
                            break
                    else:
                        continue
                    break

    # ★挑被挪的器件 (★哪一端是"可动的那端")
    out = []
    for c in cands:
        movers = []
        for end in ("a", "b"):
            ref = c[end][0]
            fp = fp_by_ref.get(ref)
            if fp is None:
                continue
            n = npads_of(fp)
            if n > 2:
                continue
            if apos is not None:
                pa, pb = apos.get(ref), fpinfo.get(ref)
                if not pa or not pb or abs(pa[0] - pb[0]) > 0.01 or abs(pa[1] - pb[1]) > 0.01:
                    continue     # ★★**位置不一致 ⇒ 不可套用** ★★
            movers.append((end, ref, n))
        if not movers:
            continue
        # ★优先挪"焊盘对里更可动"的一端 (★若两端都可动, 取位移小的那端 ⇒ 此处同 d, 取先遇到的那个)
        end, ref, n = movers[0]
        # ★★**新原点 = 目标焊盘位置 + (器件原点 − 该焊盘原位置)** (★修坑②) ★★
        ox, oy = fpinfo[ref]
        if end == "b":
            padx, pady = c["b"][2], c["b"][3]
        else:
            padx, pady = c["a"][2], c["a"][3]
        offx = ox - padx
        offy = oy - pady
        npos = (c["tgt"][0] + offx, c["tgt"][1] + offy)
        out.append(dict(net=c["net"], ref=ref, n=n, d=c["d"], sgn=c["sgn"],
                        pos=npos, hit=c["hit"], end=end))

    # ★去重: 同一 ref 只保留位移最小的 (★修坑①)
    best = {}
    for o in sorted(out, key=lambda z: z["d"]):
        if o["ref"] not in best:
            best[o["ref"]] = o
    out = sorted(best.values(), key=lambda z: (z["d"], z["ref"]))[:limit]

    L = ["★第一批可执行的钉位 (★按位移升序 · ★同 ref 已去重 · ★只含 ≤2 焊盘小器件 ⇒ 挪器件≈挪焊盘)★",
         "★板: %s" % boardp]
    if against:
        L.append("★位置一致性校验: 对照 %s (★位置不一致的器件已剔除)" % against)
    L += ["",
          "%-16s %-18s %-5s %-7s %-8s %-20s %s" % ("网", "被挪器件", "焊盘数", "位移", "方向", "新器件原点", "横穿它的网")]
    pins = []
    for o in out:
        L.append("%-16s %-18s %-5d %-7.1f %-8s (%.3f, %.3f)%s %s"
                 % (o["net"], o["ref"], o["n"], o["d"], "左" if o["sgn"] > 0 else "右",
                    o["pos"][0], o["pos"][1], " " * 4, ",".join(o["hit"][:2])))
        pins.append("%s:%.3f,%.3f" % (o["ref"], o["pos"][0], o["pos"][1]))
    L += ["",
          "★PCB_PART_POS 串 (★可直接贴进 arm 脚本的 env; ★与臂原有的钉位【合并】而不是替换!)★:",
          '  PCB_PART_POS="%s"' % ";".join(pins),
          "",
          "★★★**★⚠️ 三条必做** ★★★",
          "★★★**★① 挪完【在臂的板上】重跑 `state/probe_lane_conflicts.py` ⇒ 确认【冲突总数没变大】⇒ ★★**否则就是你占掉了别人的走廊 (★v56 教训)** ★★★",
          "★★★**★② 出臂 ⇒ 套已校准链 ⇒ vs `baseline_v76_chain` ⇒ ★★**看端到端读数, 不看[某条通了]这种局部读数** ★★★",
          "★★★**★③ 若臂脚本已有 `PCB_PART_POS` (★v76 有 R_SEL_* 的钉位) ⇒ ★★**必须【合并】而非覆盖** ⇒ ★★**否则 R_SEL 会跳回排版器自动位置 ⇒ ★★**布局基础就变了 (★今晚刚证过: 两边位置本就不同)** ★★★",
          ""]
    text = "\n".join(L)
    if outp:
        open(outp, "w", encoding="utf-8").write(text)
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
