#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_test_clrfix.py —— ★★【★防回归自测: 【边际净距修复】工具 (★`state/fix_clearance_width.py`★)★】★★

★★★**★为什么要有这个守卫 (★2026-11-11 04:0x-04:3x 实测踩到的三件事★)★★★ ★★★
  ① ★★**收窄必须迭代**: ★一个过孔周围有多条【等距】的铜 ⇒ ★**修一条, DRC 就把下一条报出来**
    ⇒ ⇒ 【"修一次就干净"是错的】⇒ ⇒ 工具必须能被【反复调用】⇒ ⇒ 且【每轮都重跑 DRC】★★
  ② ★★**差分腿不许收窄**: ★**板里 `diff_pair_dimensions = []` ⇒ KiCad 没有任何差分对规则生效**
    ⇒ ⇒ **DRC 不会报**差分宽度不匹配 ⇒ ⇒ **收窄 MIPI 的 N 腿 ⇒ DRC 全绿但板子是错的**
    ⇒ ⇒ 工具必须自己按网名认差分腿并拒绝 ★★
  ③ ★★**过孔不许收窄**: ★**过孔盘直径受【最小钻孔 0.30mm】硬约束** ⇒ ⇒ 只能动走线 ★★
  ④ ★★**去重键不能是 `id(obj)`**: ★**pcbnew 每次迭代给的是新 wrapper ⇒ 同一段会被收窄两次** ★★
  ⑤ ★★**净距"单调"性是工具安全性的全部依据**: ★**收窄 ⇒ 铜边内缩 ⇒ 净距只增不减 ⇒ 不可能新增违规** ★★

★★★**★本守卫怎么做到"真" (★不是纸面推理★)★★★ ★★★
  · ★**自己造一块真板** (★pcbnew 建板 + 写 .kicad_pro★) ⇒ ★**故意造 3 类违规** ★
  · ★**跑真 KiCad DRC** ⇒ ★**取回真违规清单** ⇒ ★**把它喂给工具** ⇒ ★**再跑一次真 DRC** ★
  · ★**断言**: ★① 该修的被修了 ★② 端点没动 (零连通性风险) ★③ 差分腿没被动 ★④ 过孔没被动 ★⑤ 宽度不破地板 ★⑥ DRC 违规数下降 ★★
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
TOOL = os.path.join(HERE, "fix_clearance_width.py")
KC = os.path.join(HERE, "kicad.sh")
MIN_W = 0.15
FLOOR = 0.152

ok = 0
fail = 0


def check(name, cond, extra=""):
    global ok, fail
    if cond:
        ok += 1
        print("  ✓ %s%s" % (name, (" — " + extra) if extra else ""))
    else:
        fail += 1
        print("  ✗ %s%s" % (name, (" — " + extra) if extra else ""))


def nm(x):
    return pcbnew.FromMM(x)


def build_board(path):
    b = pcbnew.NewBoard(path)
    ds = b.GetDesignSettings()
    ds.m_TrackMinWidth = int(MIN_W * 1e6)
    ds.m_MinClearance = int(0.20 * 1e6)
    # 板框
    pts = [(0, 0), (100, 0), (100, 60), (0, 60)]
    for i in range(4):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % 4]
        seg = pcbnew.PCB_SHAPE(b)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetStart(pcbnew.VECTOR2I(nm(x1), nm(y1)))
        seg.SetEnd(pcbnew.VECTOR2I(nm(x2), nm(y2)))
        seg.SetLayer(pcbnew.Edge_Cuts)
        seg.SetWidth(nm(0.1))
        b.Add(seg)
    # 网
    nets = {}
    for name in ("NET_A", "NET_B", "GND", "CSI_TEST_P", "CSI_TEST_N"):
        ni = pcbnew.NETINFO_ITEM(b, name)
        b.Add(ni)
        nets[name] = ni

    def add_track(net, x1, y1, x2, y2, w=0.25):
        t = pcbnew.PCB_TRACK(b)
        t.SetStart(pcbnew.VECTOR2I(nm(x1), nm(y1)))
        t.SetEnd(pcbnew.VECTOR2I(nm(x2), nm(y2)))
        t.SetWidth(nm(w))
        t.SetLayer(pcbnew.F_Cu)
        t.SetNet(nets[net])
        b.Add(t)
        return t

    # ① 普通违规对 (★边际: 净距 0.185 ⇒ 差 0.015 ⇒ 该修★)
    add_track("NET_A", 20, 20, 60, 20)
    add_track("NET_B", 20, 20.435, 60, 20.435)
    # ② 差分腿违规对 ⇒ 不许动
    add_track("CSI_TEST_P", 20, 40, 60, 40)
    add_track("CSI_TEST_N", 20, 40.40, 60, 40.40)
    # ③ 过孔 vs 走线 (★边际★) ⇒ 只许动走线
    v = pcbnew.PCB_VIA(b)
    v.SetPosition(pcbnew.VECTOR2I(nm(80), nm(20.45)))
    v.SetWidth(nm(0.6))
    v.SetDrill(nm(0.3))
    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    v.SetNet(nets["GND"])
    b.Add(v)
    add_track("NET_B", 70, 21.06, 90, 21.06)
    # ④ ★【修不动】的狠违规 (净距 0.10 ⇒ 需收窄 0.21 ⇒ 跌破 0.15 地板) ⇒ 工具必须【拒绝并报出来】★
    add_track("NET_A", 20, 50, 60, 50)
    add_track("NET_B", 20, 50.35, 60, 50.35)
    b.Save(path)
    return b


def write_pro(path):
    """★板旁必须有 .kicad_pro ⇒ 否则规则回落默认 min_width 0.20 ⇒ 假违规★"""
    src = None
    for cand in ("/tmp/chain_v76mv0/final_chain.kicad_pro",
                 os.path.join(PROJ, "HW/PCB/demo_mainboard.kicad_pro")):
        if os.path.exists(cand):
            src = cand
            break
    if src is None:
        return False
    shutil.copyfile(src, path)
    return True


def run_drc(board, out):
    subprocess.run(["bash", KC, "pcb", "drc", "--output", out,
                    "--severity-error", "--severity-warning", "--format", "json", board],
                   capture_output=True, text=True, cwd=PROJ)
    if not os.path.exists(out):
        return None
    with open(out, encoding="utf-8") as f:
        return json.load(f)


def track_by(board, netname, x1, y1, x2, y2):
    for t in board.GetTracks():
        if t.GetClass() != "PCB_TRACK":
            continue
        if t.GetNetname() != netname:
            continue
        s, e = t.GetStart(), t.GetEnd()
        if (abs(s.x / 1e6 - x1) < 1e-3 and abs(s.y / 1e6 - y1) < 1e-3
                and abs(e.x / 1e6 - x2) < 1e-3 and abs(e.y / 1e6 - y2) < 1e-3):
            return t
    return None


def main():
    tmp = tempfile.mkdtemp(prefix="_clrfix_guard_")
    pcb = os.path.join(tmp, "t.kicad_pcb")
    pro = os.path.join(tmp, "t.kicad_pro")
    print("── 造板 (%s)" % pcb)
    build_board(pcb)
    if not write_pro(pro):
        print("  ✗ 找不到 .kicad_pro 模板 ⇒ 收工")
        return 1
    drc1 = os.path.join(tmp, "drc1.json")
    d1 = run_drc(pcb, drc1)
    if not d1:
        print("  ✗ DRC 没跑出来")
        return 1
    v1 = d1.get("violations") or []
    print("── 造出来的违规: %d 条" % len(v1))
    for x in v1:
        for it in x.get("items", []):
            print("     ·", it.get("description", "")[:80])

    out = os.path.join(tmp, "fixed.kicad_pcb")
    r = subprocess.run(["bash", os.path.join(HERE, "pcbnew_py.sh"), TOOL, pcb, drc1,
                        "--out", out], capture_output=True, text=True, cwd=PROJ)
    print("── 工具 rc=%d" % r.returncode)
    if r.returncode != 0:
        print(r.stdout[-800:], r.stderr[-400:])
        return 1
    shutil.copyfile(pro, os.path.join(tmp, "fixed.kicad_pro"))
    drc2 = os.path.join(tmp, "drc2.json")
    d2 = run_drc(out, drc2)
    v2 = (d2.get("violations") or []) if d2 else []
    print("── 修完 DRC: %d 条" % len(v2))
    for x in v2:
        for it in x.get("items", []):
            print("     ·", it.get("description", "")[:80])

    b = pcbnew.LoadBoard(out)
    ta = track_by(b, "NET_A", 20, 20, 60, 20)
    tb = track_by(b, "NET_B", 20, 20.435, 60, 20.435)
    tp = track_by(b, "CSI_TEST_P", 20, 40, 60, 40)
    tn = track_by(b, "CSI_TEST_N", 20, 40.40, 60, 40.40)
    tv = track_by(b, "NET_B", 70, 21.06, 90, 21.06)

    # ① 该修的修了: NET_A↔NET_B 净距 ≥ 0.20
    if ta and tb:
        gap = 0.435 - (ta.GetWidth() / 1e6 + tb.GetWidth() / 1e6) / 2
        check("① 普通违规对被修好 (净距 %.4f ≥ 0.2000)" % gap, gap >= 0.20 - 1e-6)
        # ② 端点没动 (零连通性风险)
        s, e = ta.GetStart(), ta.GetEnd()
        check("② 端点没动 (NET_A 仍是 (20,20)->(60,20))",
              abs(s.x / 1e6 - 20) < 1e-3 and abs(e.x / 1e6 - 60) < 1e-3)
    else:
        check("① 找得到 NET_A/NET_B 走线", False)

    # ③ 差分腿没被动
    if tp and tn:
        wp, wn = tp.GetWidth() / 1e6, tn.GetWidth() / 1e6
        check("③ 差分腿没被收窄 (P=%.3f N=%.3f, 应仍 0.250)" % (wp, wn),
              abs(wp - 0.25) < 1e-6 and abs(wn - 0.25) < 1e-6)
    else:
        check("③ 找得到差分腿走线", False)

    # ④ 过孔没被动
    via_ok = True
    for t in b.GetTracks():
        if t.GetClass() == "PCB_VIA":
            via_ok = abs(t.GetWidth(pcbnew.F_Cu) / 1e6 - 0.6) < 1e-6
    check("④ 过孔盘直径没被改 (仍 0.600)", via_ok)

    # ⑤ 宽度不破地板
    floors = [t.GetWidth() / 1e6 for t in b.GetTracks()
              if t.GetClass() == "PCB_TRACK"]
    check("⑤ 所有走线宽度 ≥ %.3f (最小实测 %.3f)" % (FLOOR, min(floors) if floors else 0),
          bool(floors) and min(floors) >= FLOOR - 1e-6)

    # ⑥ DRC 违规数下降
    check("⑥ DRC 违规数下降 (%d → %d)" % (len(v1), len(v2)), len(v2) < len(v1))
    # ⑦ 差分腿那条违规仍在 (证明护栏是"不改"而不是"顺手改了别的")
    remain_diff = any("CSI_TEST" in (it.get("description", "") or "")
                      for x in v2 for it in x.get("items", []))
    check("⑦ 差分腿那条违规【仍在】(护栏没偷偷修它)", remain_diff)

    print("── 断言: %d 过 / %d 失" % (ok, fail))
    shutil.rmtree(tmp, ignore_errors=True)
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
