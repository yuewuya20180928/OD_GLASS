#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_test_rownorm2.py —— ★★【★防回归自测: 【排法线约束在有出脚直道时也要生效】(★`PCB_ESC_ROWNORM2`★)★】★★

★★★**★问题 (★2026-11-10 16:6x 实测坐实★)** ★★★
  ★**现象 (★v76mg1 / v76mj1 终板·★那两条臂都只剩这一条 clearance★)**:
    ★**`ID_DETECT_0` ↔ `BOOT_N` 净距 0.1813mm (★需 0.2000★) ⇒ ★**差 0.0187mm** ★★
  · ★**几何 (★实测★)**: ★**两脚在 J_SOM_P1 同排 (y=11.040), 出脚直道【同向平行】(x=62.800 / 63.600)**
    ⇒ ★**出脚后【第一步就朝相反 y 方向转弯】⇒ 两条 45° 斜线交错 ⇒ 中心线只差 0.4313mm**
    ⇒ ★**净距 = 0.4313 - 0.125 - 0.125 = 0.1813mm < 0.2000mm** ★★
  · ★★★★**★根因 (★代码级, ★★讽刺的一条★)★★★ ★★★
    ★**`ESC_ROWNORM` 这个机制【本来就是照着这条 DRC 写的】(★见 `_row_normal()` 的注释★)**
    ⇒ ★**但它【对它最该生效的那两个焊盘完全生效】★**
    ⇒ ★★★**★原因: `anchor()` 里 `if st: ... return` 提前返回 ⇒ 【ROWNORM 分支永远走不到】**
      · ★**实测: `ID_DETECT_0` / `BOOT_N` 两脚的 `_nearest_other_pad` = 0.3000 < 0.45
        ⇒ `escape_stub()` **返回直道** ⇒ ⇒ `st` 非 None ⇒ ⇒ **提前返回** ⇒ ⇒ ROWNORM 失效** ★★
    ⇒ ★★**⇒ 这条 DRC 用 `ESC_ROWNORM` 消不掉 (★机制本身失效了★)** ★★
  · ★**修法 (★env 门控 `PCB_ESC_ROWNORM2`, ★默认关⇒逐位不变★)**:
    ★**有出脚直道时【也】把【排法线】方向登记进 `_esc_start_dir` (★且只在与直道方向不冲突时★)**
    ⇒ ★**⇒ 相邻脚的扇出不交错 ⇒ ⇒ 那条 DRC 的根因就没了** ★★

★★★**★断言清单 (★全部来自 2026-11-10 的实测★)** ★★★
  ① ★**默认关**: ★**不设 `PCB_ESC_ROWNORM2` ⇒ 行为必须逐位不变** ★
  ② ★**显式开才 True**
  ③ ★**源码级: 修法必须落在【`anchor()` 的 `if st:` 之前】(★否则还是提前返回⇒ 白写★)**
  ④ ★★★**★实测: ★`ID_DETECT_0` / `BOOT_N` 两脚【都必须有出脚直道】(★这是 ROWNORM 失效的前提★)** ★★
    ⇒ ★★**⇒ 若哪天这两脚没有直道了, ★ROWNORM 就会自然生效 ⇒ ★⇒ 断言④ 就是"防这个前提被悄悄改掉"的钉子** ★★
  ⑤ ★★★**★实测: ★`_row_normal()` 必须给得出排法线 (★(0,1) = 垂直于那一排★)** ★★
  ⑥ ★★★**★实测: ★排法线方向必须与出脚直道方向【兼容】(★不冲突★)⇒ ⇒ 新机制才敢用** ★★
  ⑦ ★★**★源码级: ★修法必须【只登记约束, 不改几何】(★不许出现删铜/改铜路径★)** ★★

用法:
  bash state/pcbnew_py.sh state/_test_rownorm2.py
  ⇒ 全部断言过 ⇒ 打印 "ALL PASS" ⇒ rc=0; 任一失败 ⇒ rc=1
"""
import os
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
os.environ.pop("PCB_ESC_ROWNORM2", None)
import gen_pcb_routing as G          # noqa: E402
chk("① 默认 PCB_ESC_ROWNORM2 未设 ⇒ 必须 False (★默认逐位不变★)",
    G.ESC_ROWNORM2 is False, "实际 = %r" % (G.ESC_ROWNORM2,))

os.environ["PCB_ESC_ROWNORM2"] = "1"
import importlib                   # noqa: E402
G2 = importlib.reload(G)
chk("② PCB_ESC_ROWNORM2=1 ⇒ 必须 True",
    G2.ESC_ROWNORM2 is True, "实际 = %r" % (G2.ESC_ROWNORM2,))
os.environ.pop("PCB_ESC_ROWNORM2", None)
importlib.reload(G)

# ---------------------------------------------------------------- ③ ⑦ 源码级
_src = open(os.path.join(_HERE, "gen_pcb_routing.py"), encoding="utf-8").read()
_i = _src.index("def anchor(pad):")
# ★★**必须按【缩进】切函数体 (★否则会串到后面的函数里, ★导致断言 ⑦ 假阳性★)★★
_j = _src.find("\n    def ", _i + 10)
_body = _src[_i:_j if _j > 0 else len(_src)]

_m_fix = _body.find("ESC_ROWNORM2")
_m_st = _body.find("if st:")
chk("③ 修法必须落在【`anchor()` 的 `if st:` 之前】(★否则提前返回 ⇒ 白写★)",
    _m_fix >= 0 and _m_st >= 0 and _m_fix < _m_st,
    "★找不到修法 (index=%d) 或它在 `if st:` 之后 (index=%d)★" % (_m_fix, _m_st))

chk("⑦ 修法只【登记约束】不改几何 (★不许出现删铜/改铜路径★)",
    ("_drop_committed" not in _body) and (".Remove(" not in _body)
    and ("self.tracks.remove" not in _body) and ("self.tracks.pop" not in _body),
    "★anchor() 里出现了删铜路径★")

# ---------------------------------------------------------------- ④⑤⑥ 实测
print()
print("── 实测: ROWNORM 失效的前提与可行性 ──")
try:
    import pcbnew                # noqa: E402
except Exception:                # noqa: BLE001
    pcbnew = None

if pcbnew is not None:
    board = pcbnew.LoadBoard(os.path.join(_HERE, "..", "HW", "PCB",
                                          "demo_mainboard.kicad_pcb"))
    r = G.GridRouter(board)
    _pads = []
    for _net in ("ID_DETECT_0", "BOOT_N"):
        for _p in (r.net_pads.get(_net) or []):
            if abs(_p[2] - 63.0) < 0.9 and abs(_p[3] - 11.04) < 0.5:
                _pads.append((_net, _p))

    chk("④ 实测: 那两个焊盘必须【都有出脚直道】(★这是 ROWNORM 失效的前提★)",
        len(_pads) == 2 and all(r.escape_stub(n, p) is not None for n, p in _pads),
        "★前提变了 (焊盘数=%d 或有脚没直道) ⇒ ROWNORM 会自然生效 ⇒ 断言要更新★" % len(_pads))

    _dns = []
    for _n, _p in _pads:
        try:
            _dn = r._row_normal(_n, _p[2], _p[3])
        except Exception:
            _dn = None
        _dns.append(_dn)
        print("  ★%s (%.2f,%.2f): _row_normal = %s" % (_n, _p[2], _p[3], _dn))

    chk("⑤ 实测: `_row_normal()` 必须给得出排法线 (★(0,1) = 垂直于那一排★)",
        all(d is not None and (d[0] == 0 or d[1] == 0) for d in _dns),
        "★拿不到排法线 ⇒ 新机制无从谈起★")

    # ⑥ 排法线方向 vs 出脚直道方向
    _ok_compat = True
    for (_n, _p), _dn in zip(_pads, _dns):
        _st = r.escape_stub(_n, _p)
        if _st is None or _dn is None:
            continue
        _sx, _sy = _st[0] - _p[2], _st[1] - _p[3]
        _same = (abs(_sx) < 1e-9 and abs(_dn[0]) < 1e-9) or \
                (abs(_sy) < 1e-9 and abs(_dn[1]) < 1e-9)
        print("  ★%s: 出脚直道方向 (%.2f,%.2f) · 排法线 %s ⇒ 同轴=%s" % (_n, _sx, _sy, _dn, _same))
        if not _same:
            _ok_compat = False
    chk("⑥ 实测: 排法线方向必须与出脚直道方向【兼容】(★不冲突 ⇒ 新机制才敢用★)",
        _ok_compat,
        "★方向冲突 ⇒ 新机制会让直道与约束矛盾 ⇒ 不能用★")
else:
    chk("④⑤⑥ 实测断言 (★拿不到 pcbnew★)", False, "★pcbnew 不可用★")

# ---------------------------------------------------------------- 汇总
print()
if FAIL:
    print("═══ 失败 %d 项 ═══" % len(FAIL))
    for f in FAIL:
        print("   ✘ %s" % f)
    sys.exit(1)
print("═══ ALL PASS (%d 项) ═══" % len(OK))
sys.exit(0)
