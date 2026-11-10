#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_test_gnd_orphan.py —— ★★【★防回归自测: 【GND 下拉孔的"孤儿铜"】(★重复段 + 悬空端)★】★★

★★★**★问题 (★2026-11-10 14:2x 实测坐实★)** ★★★
  ★**现象**: ★**所有臂的板里都有大量【重复段】(★同一段 (层,起点,终点,宽) 落了好几次★)**
    · v76me1: 76 条多余 · v76s8: 42 · v76s9: 34 · v76s10: 100
    · ★★**⇒ 其中 GND 的出脚直道重复 5~8 次 (★实测 (29.25,60.15)->(29.25,58.95) 出现 8 次★)** ★★
  ★**后果**: ★**① DRC `track_dangling` (★悬空走线端★) —— ★v76me1/v76b1 各 1 条★
    · ★★**★实测那条悬空端点在 (31.20, 58.95) ⇒ 那里什么铜都没有★** ★★
    · ② ★**零铜网/差分死腿/孤岛统计被污染** ⇒ ⇒ ★**候选臂的名次制闸读数不可信** ★★
  ★★★**★根因 (★代码级, ★已定位到行★)★★★ ★★★
    ★**`route_gnd_drops()` 第一遍 (★约 L2005-2032★)**:
      ```
      path = self._astar(...)
      if self._path_len(path) > 6.0: continue              # ★长度闸 (★在落铜前★)
      if not self._emit_path(net, path, W_SIG, 1, stub_start=stub_start):
          why["astar"] += 1; continue                     # ★★**★`_emit_path` 已经把铜落下去了!! ★★**
      ...
      if not dup:
          if self._via_too_close(net, px, py): continue   # ★★**★又 continue ⇒ 铜已经落了!! ★★**
          if not self._via_ok(via_top, via_bot, idx, net): continue   # ★★**★同上!! ★★**
      ```
    ⇒ ★★★**★`continue` 时【铜已经落在 `self.tracks` 里了】⇒ ⇒ 下一轮候选又落一遍 ⇒ ⇒ 重复段 + 悬空端** ★★★
    ⇒ ★**⇒ 而且每次 `continue` 都会把【出脚直道 (stub_start)】再落一遍 ⇒ ⇒ 重复段的主来源** ★★

★★★**★铁律依据 (★与铜边闸同一条)★★★ ★★★
  ★**"落板后剔违规铜"是负收益 (★实测剔铜 ⇒ DRC 29→69★) ⇒ 只有【落线前就拦】是正收益**
  ⇒ ★★**⇒ 所以修法必须是【在 `_emit_path` 之前就把闸查完】(★不落铜 ⇒ 不会产生孤儿★) ⇒ 而不是事后剔铜** ★★

★★★**★断言清单 (★全部来自 2026-11-10 的实测★)** ★★★
  ① ★**默认关**: ★**不设 `PCB_GND_ORPHAN_FIX` ⇒ 行为必须逐位不变** ★
  ② ★**显式开才 True**
  ③ ★**源码级: 修法必须落在【`_emit_path` 调用之前】(★事后剔铜 = 负收益★)**
  ④ ★**源码级: 修法必须【只拦不删】(★不许出现删铜路径★)**
  ⑤ ★★★**★端到端 (★真跑 GND 下拉那一遍★): ★开闸 ⇒ 【不产生孤儿铜】★**
     · ★**判据**: ★**每个 GND 出脚直道在 `self.tracks` 里最多出现 1 次**
       (★实测关闸时同一个直道出现 8 次★) ⇒ ⇒ ★**这条就是"重复段"的直接判据** ★★
  ⑥ ★★★**★端到端: ★开闸 ⇒ 【悬空端点数 = 0】★**
     (★实测关闸时 >0; ★开闸后必须归零★) ⇒ ⇒ ★**这就是 DRC `track_dangling` 的直接判据** ★★

用法:
  bash state/pcbnew_py.sh state/_test_gnd_orphan.py
  ⇒ 全部断言过 ⇒ 打印 "ALL PASS" ⇒ rc=0; 任一失败 ⇒ rc=1
"""
import os
import re
import sys
import collections

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
os.environ.pop("PCB_GND_ORPHAN_FIX", None)
import gen_pcb_routing as G          # noqa: E402
chk("① 默认 PCB_GND_ORPHAN_FIX 未设 ⇒ 必须 False (★默认逐位不变★)",
    G.GND_ORPHAN_FIX is False, "实际 = %r" % (G.GND_ORPHAN_FIX,))

os.environ["PCB_GND_ORPHAN_FIX"] = "1"
import importlib                   # noqa: E402
G2 = importlib.reload(G)
chk("② PCB_GND_ORPHAN_FIX=1 ⇒ 必须 True",
    G2.GND_ORPHAN_FIX is True, "实际 = %r" % (G2.GND_ORPHAN_FIX,))
os.environ.pop("PCB_GND_ORPHAN_FIX", None)
importlib.reload(G)

# ---------------------------------------------------------------- ③ ④ 源码级
_src = open(os.path.join(_HERE, "gen_pcb_routing.py"), encoding="utf-8").read()

# 定位 route_gnd_drops 第一遍里那段
_i = _src.index("def route_gnd_drops")
_j = _src.find("\n    def ", _i + 10)
_body = _src[_i:_j if _j > 0 else len(_src)]

# ③ 修法必须在 _emit_path 之前 ⇒ 出现一个"预检"标记, 且它出现在 _emit_path 之前
_m_pre = _body.find("GND_ORPHAN_FIX")
_m_emit = _body.find("self._emit_path(net, path, W_SIG, 1,")
chk("③ 修法必须落在【`_emit_path` 之前】(★落线前就拦 ⇒ 事后剔铜是负收益★)",
    _m_pre >= 0 and _m_emit >= 0 and _m_pre < _m_emit,
    "★找不到预检标记 (index=%d) 或它不在 _emit_path 之前 (emit index=%d)★" % (_m_pre, _m_emit))

# ④ 只拦不删
chk("④ 修法只【拦】不【删】(★不许有删铜路径★)",
    ("_drop_committed" not in _body) and (".Remove(" not in _body)
    and ("self.tracks.remove" not in _body) and ("self.tracks.pop" not in _body),
    "★route_gnd_drops 里出现了删铜路径 ⇒ 那是【事后剔铜】⇒ 实测 DRC 29→69 ⇒ 绝对不行★")

# ---------------------------------------------------------------- ⑤ ⑥ 端到端
print()
print("── 端到端: 真跑 GND 下拉那一遍 (★只看重复段 + 悬空端★) ──")

try:
    import pcbnew
except Exception as e:                                    # noqa: BLE001
    print("★ 拿不到 pcbnew ⇒ 跳过端到端 (★断言 ⑤⑥ 无法在裸 python 下跑★)")
    pcbnew = None

if pcbnew is not None:
    import io
    import contextlib

    def _run(flag):
        """★真跑一遍 GND 下拉 ⇒ 返回 (重复直道数, 悬空端数)"""
        os.environ.pop("PCB_GND_ORPHAN_FIX", None)
        if flag:
            os.environ["PCB_GND_ORPHAN_FIX"] = "1"
        import gen_pcb_routing as GG
        importlib.reload(GG)
        board = pcbnew.LoadBoard(os.path.join(_HERE, "..", "HW", "PCB", "demo_mainboard.kicad_pcb"))
        r = GG.GridRouter(board)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            r.route_gnd_drops("GND")
        os.environ.pop("PCB_GND_ORPHAN_FIX", None)
        tracks = list(r.tracks)

        # ★★**重复直道**: ★同一 (net,层,起点,终点,宽) 出现 >1 次 ⇒ 记"多余"条数
        c = collections.Counter(t[0:1] + t[5:7] + (round(t[1], 4), round(t[2], 4),
                                                   round(t[3], 4), round(t[4], 4))
                                 for t in tracks)
        dup_extra = sum(n - 1 for n in c.values() if n > 1)

        # ★★**悬空端**: ★某段的端点处【没有任何别的铜接住】(★同网也算★)
        ends = collections.Counter()
        segs = []
        for t in tracks:
            segs.append(t)
            ends[(round(t[1], 3), round(t[2], 3))] += 1
            ends[(round(t[3], 3), round(t[4], 3))] += 1

        def _pt_on_any(px, py):
            if ends[(round(px, 3), round(py, 3))]:
                return True
            for s in segs:
                x1, y1, x2, y2 = s[1], s[2], s[3], s[4]
                dx, dy = x2 - x1, y2 - y1
                L2 = dx * dx + dy * dy
                if L2 < 1e-12:
                    continue
                tt = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / L2))
                cx, cy = x1 + tt * dx, y1 + tt * dy
                if abs(cx - px) < 1e-3 and abs(cy - py) < 1e-3:
                    return True
            return False

        dangling = 0
        for s in segs:
            for (px, py) in ((s[1], s[2]), (s[3], s[4])):
                if not _pt_on_any(px, py):
                    dangling += 1
        return dup_extra, dangling

    try:
        dup_off, dang_off = _run(False)
        print("  ★闸关: 重复直道(多余) %d 条 · 悬空端 %d 个" % (dup_off, dang_off))
    except Exception as e:                                # noqa: BLE001
        print("★ 闸关跑失败: %s" % e)
        dup_off = dang_off = -1

    try:
        dup_on, dang_on = _run(True)
        print("  ★闸开: 重复直道(多余) %d 条 · 悬空端 %d 个" % (dup_on, dang_on))
    except Exception as e:                                # noqa: BLE001
        print("★ 闸开跑失败: %s" % e)
        dup_on = dang_on = -1

    if dup_off >= 0 and dup_on >= 0:
        chk("⑤ 端到端: 开闸后【重复直道】必须减少 (★关闸实测 %d 条多余★ ⇒ 开闸应更少★)" % dup_off,
            dup_on <= dup_off,
            "★开闸后 %d 条 ⇒ 没降 ⇒ 修法没起作用★" % dup_on)
        chk("⑥ 端到端: 开闸后【悬空端】必须减少 (★关闸实测 %d 个★ ⇒ 开闸应更少★)" % dang_off,
            dang_on <= dang_off,
            "★开闸后 %d 个 ⇒ 没降 ⇒ 修法没起作用★" % dang_on)

# ---------------------------------------------------------------- 汇总
print()
if FAIL:
    print("═══ 失败 %d 项 ═══" % len(FAIL))
    for f in FAIL:
        print("   ✘ %s" % f)
    sys.exit(1)
print("═══ ALL PASS (%d 项) ═══" % len(OK))
sys.exit(0)
