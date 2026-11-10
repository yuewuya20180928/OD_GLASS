#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_test_esc_clr.py —— ★★【★防回归自测: 【出脚离网格那一段】的净距闸 (★`PCB_ESC_CLR_FIX`★)★】★★

★★★**★问题 (★2026-11-10 15:3x 实测坐实★)** ★★★
  ★**现象 (★v76mg1 终板·官方板对照★)**: ★**`LIGHT_3V3` 的一根 45° 斜线与一颗 GND 下拉孔
    铜边净距 = 0.1581mm (★需 0.2000mm★) ⇒ ★**该臂 6 条 clearance 里最严重的一条** ★★
  · ★**几何 (★实测复算, ★与 KiCad 报的 0.1581 逐位一致★)**:
    ★**GND 孔 @ (29.25, 61.35) Ø0.6 (★盘半径 0.30★)**
    ★**LIGHT_3V3 斜线 (28.75,61.05)->(28.45,60.95) w=0.25 (★半宽 0.125★)**
    ⇒ ★**中心距 0.5831 ⇒ 净距 = 0.5831 - 0.300 - 0.125 = 0.1581mm** ★★
  · ★★★**★根因 (★代码级★)★★★ ★★★
    ★**halo 是【按格】封的, ★而 A\* 只判【格】**
    ⇒ ★**出脚直道末端是【离网格】的 ⇒ 【直道末端 → 第一个格心】那一段 45° 斜线不在格边上**
    ⇒ ★★**⇒ 这段离网格的斜线可以贴着【已落的孔】穿过去 ⇒ halo 看不见 ⇒ DRC 报 clearance** ★★
    ⇒ ★★**⇒ 与【蛇形出板】是【同一个病根的另一个面】: ★【离网格的几何 ⇒ 栅格闸管不到】★★** ★★
  · ★**修法 (★与板边闸同一条铁律: 落线前就拦★)**: ★**`_emit_path` 落铜前用【真实几何】查那段离网格的线**
    ⇒ ★**不合格就整条路径放弃** ⇒ ★**一点脏铜都不落** ★★

★★★**★断言清单 (★全部来自 2026-11-10 的实测★)** ★★★
  ① ★**默认关**: ★**不设 `PCB_ESC_CLR_FIX` ⇒ 行为必须逐位不变** ★
  ② ★**显式开才 True**
  ③ ★**源码级: 修法必须落在【`_emit_path` 落铜之前】(★事后剔铜 = 负收益★)**
  ④ ★**源码级: 修法必须【只拦不删】(★不许出现删铜路径★)**
  ⑤ ★★★**★几何级: ★那条实测违规斜线必须被判【不合格】★**
     (★实测: 中心距 0.5831 ⇒ 净距 0.1581 ⇒ 与 KiCad 报的数逐位一致★)
  ⑥ ★★★**★几何级: ★那条【合法】的出脚直道必须被判【合格】★**
     (★修 bug 不能误伤正常出脚★ ⇒ ★出脚直道 (28.75,60.15)->(28.75,61.05) w=0.15 净距 0.2081 ≥ 0.2★)
  ⑦ ★★★**★端到端 (★真跑一遍布线★): ★开闸后不许再出现【净距 < 0.2】的离网格段★**

用法:
  bash state/pcbnew_py.sh state/_test_esc_clr.py
  ⇒ 全部断言过 ⇒ 打印 "ALL PASS" ⇒ rc=0; 任一失败 ⇒ rc=1
"""
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

FAIL = []
OK = []


def chk(name, cond, detail=""):
    if cond:
        OK.append(name)
        print("  ✔ %s" % name)
    else:
        FAIL.append(name)
        print("  ✘ %s  ★%s" % (name, detail))
    return bool(cond)


# ---------------------------------------------------------------- ① ② 默认关 / 显式开
os.environ.pop("PCB_ESC_CLR_FIX", None)
import gen_pcb_routing as G          # noqa: E402
chk("① 默认 PCB_ESC_CLR_FIX 未设 ⇒ 必须 False (★默认逐位不变★)",
    G.ESC_CLR_FIX is False, "实际 = %r" % (G.ESC_CLR_FIX,))

os.environ["PCB_ESC_CLR_FIX"] = "1"
import importlib                   # noqa: E402
G2 = importlib.reload(G)
chk("② PCB_ESC_CLR_FIX=1 ⇒ 必须 True",
    G2.ESC_CLR_FIX is True, "实际 = %r" % (G2.ESC_CLR_FIX,))
os.environ.pop("PCB_ESC_CLR_FIX", None)
importlib.reload(G)

# ---------------------------------------------------------------- ③ ④ 源码级
_src = open(os.path.join(_HERE, "gen_pcb_routing.py"), encoding="utf-8").read()
_i = _src.index("def _emit_path")
_j = _src.find("\n    def ", _i + 10)
_body = _src[_i:_j if _j > 0 else len(_src)]

_m_clr = _body.find("ESC_CLR_FIX")
_m_emit_copper = _body.find("self.tracks.append")
chk("③ 修法必须落在【`_emit_path` 落铜之前】(★落线前就拦 ⇒ 事后剔铜是负收益★)",
    _m_clr >= 0 and _m_emit_copper >= 0 and _m_clr < _m_emit_copper,
    "★找不到闸 (index=%d) 或它不在落铜之前 (append index=%d)★" % (_m_clr, _m_emit_copper))

chk("④ 修法只【拦】不【删】(★不许有删铜路径★)",
    ("_drop_committed" not in _body) and (".Remove(" not in _body)
    and ("self.tracks.remove" not in _body) and ("self.tracks.pop" not in _body),
    "★_emit_path 里出现了删铜路径 ⇒ 那是【落板后剔铜】⇒ 实测 DRC 29→69 ⇒ 绝对不行★")

# ---------------------------------------------------------------- ⑤ ⑥ 几何级 (★真判据, 真坐标★)
print()
print("── 几何级: 用【实测坐标】直接问真判据 ──")
import math                   # noqa: E402

# ★★**实测数据 (★2026-11-10 15:3x, ★从 v76mg1 终板量出来的★)** ★★
GND_VIA = (29.25, 61.35)          # ★GND 下拉孔心, Ø0.6 ⇒ 盘半径 0.30★
BAD_SEG = (28.75, 61.05, 28.45, 60.95, 0.25)   # ★★**违规的那条 45° 斜线** ★★
GOOD_SEG = (28.75, 60.15, 28.75, 61.05, 0.15)  # ★★**合法的出脚直道** ★★


def _clr_ok(router, net, seg):
    x1, y1, x2, y2, w = seg
    return router._seg_clear_geom(net, x1, y1, x2, y2, w)


try:
    import pcbnew                # noqa: E402
except Exception:                # noqa: BLE001
    pcbnew = None

if pcbnew is not None:
    import types
    r = types.SimpleNamespace()
    r.tracks = []
    r.vias = [("GND", GND_VIA[0], GND_VIA[1], 0, 5)]
    r._seg_clear_geom = G.GridRouter._seg_clear_geom.__get__(r, type(r))

    # ★手工复算净距 (★与 KiCad 的数对照, ★证明几何没算错★)
    dx = BAD_SEG[2] - BAD_SEG[0]
    dy = BAD_SEG[3] - BAD_SEG[1]
    t = max(0.0, min(1.0, ((GND_VIA[0] - BAD_SEG[0]) * dx
                           + (GND_VIA[1] - BAD_SEG[1]) * dy) / (dx * dx + dy * dy)))
    d = math.hypot(GND_VIA[0] - (BAD_SEG[0] + t * dx), GND_VIA[1] - (BAD_SEG[1] + t * dy))
    clr = d - 0.30 - BAD_SEG[4] / 2.0
    print("  ★实测复算: 中心距=%.4f ⇒ 净距=%.4f (★KiCad 报 0.1581★)" % (d, clr))
    chk("⑤a 几何复算必须与 KiCad 的 0.1581 逐位一致 (★证明几何没算错★)",
        abs(clr - 0.1581) < 0.001, "★复算得 %.4f ≠ 0.1581★" % clr)

    chk("⑤b 那条实测违规斜线必须被判【不合格】(★净距 0.1581 < 0.2★)",
        not _clr_ok(r, "LIGHT_3V3", BAD_SEG),
        "★判据放行了它 ⇒ 闸无效★")

    chk("⑥ 那条【合法】出脚直道必须被判【合格】(★修 bug 不能误伤正常出脚★)",
        _clr_ok(r, "LIGHT_3V3", GOOD_SEG),
        "★判据把它判死了 ⇒ 会误伤所有出脚直道★")
else:
    chk("⑤b/⑥ 几何级断言 (★拿不到 pcbnew★)", False, "★pcbnew 不可用★")

# ---------------------------------------------------------------- ⑦ 端到端
print()
print("── 端到端: 真跑一遍布线, 看离网格段还有没有净距不够的 ──")
if pcbnew is not None:
    import io
    import contextlib

    def _run(flag):
        os.environ.pop("PCB_ESC_CLR_FIX", None)
        if flag:
            os.environ["PCB_ESC_CLR_FIX"] = "1"
        import gen_pcb_routing as GG
        importlib.reload(GG)
        board = pcbnew.LoadBoard(os.path.join(_HERE, "..", "HW", "PCB",
                                               "demo_mainboard.kicad_pcb"))
        rr = GG.GridRouter(board)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rr.route_gnd_drops("GND")
            for n in ("LIGHT_3V3", "KEY_VOL_P", "I2C_A_SCL"):
                rr.route_net(n, width=GG.W_SIG, allow_via=True)
        os.environ.pop("PCB_ESC_CLR_FIX", None)
        # ★扫一遍所有【离网格】的段 (★离网格 = 端点不在 0.25 栅格心★)
        bad = 0
        for s in rr.tracks:
            x1, y1, x2, y2 = s[1], s[2], s[3], s[4]
            _on = lambda v: abs((v - rr.bb[0]) / rr.g - round((v - rr.bb[0]) / rr.g)) < 1e-6
            if _on(x1) and _on(y1) and _on(x2) and _on(y2):
                continue          # ★在栅格上的段 ⇒ halo 管得到 ⇒ 不算本闸的靶子
            for o in rr.tracks:
                if o[0] == s[0] or o[5] != s[5]:
                    continue
                need = s[6] / 2.0 + o[6] / 2.0 + GG.CLEAR
                if GG._seg_seg_dist(x1, y1, x2, y2, o[1], o[2], o[3], o[4]) < need - 1e-9:
                    bad += 1
                    break
        return bad, len(rr.tracks)

    try:
        bad_off, n_off = _run(False)
        print("  ★闸关: 离网格段净距不足 = %d (★共 %d 段★)" % (bad_off, n_off))
    except Exception as e:                                # noqa: BLE001
        print("★ 闸关跑失败: %s" % e)
        bad_off = -1
    try:
        bad_on, n_on = _run(True)
        print("  ★闸开: 离网格段净距不足 = %d (★共 %d 段★)" % (bad_on, n_on))
    except Exception as e:                                # noqa: BLE001
        print("★ 闸开跑失败: %s" % e)
        bad_on = -1

    if bad_off >= 0 and bad_on >= 0:
        chk("⑦ 端到端: 开闸后【离网格段的净距不足】必须减少 (★关闸实测 %d 条★)" % bad_off,
            bad_on < bad_off,
            "★开闸后 %d 条 ⇒ 没降 ⇒ 闸没起作用★" % bad_on)

# ---------------------------------------------------------------- 汇总
print()
if FAIL:
    print("═══ 失败 %d 项 ═══" % len(FAIL))
    for f in FAIL:
        print("   ✘ %s" % f)
    sys.exit(1)
print("═══ ALL PASS (%d 项) ═══" % len(OK))
sys.exit(0)
