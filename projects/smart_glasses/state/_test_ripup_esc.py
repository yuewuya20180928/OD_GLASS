# -*- coding: utf-8 -*-
"""★_test_ripup_esc.py -- v52 "出脚走廊感知的 rip-up" 单测

★★★**验的是真实代码路径**: ★**抠出源里的真方法** (`_escape_blockers` / `ripup_and_reroute`)
   放进一个最小假 router 上真跑一遍 ⇒ ★**真的拆线/重布/还原** ⇒ ★不是 grep 字符串

★**要证的命题** (2026-11-06 03:0x 实测背景):
   61 条 A* 失败里 **42 条起脚在密集焊盘阵** ⇒ `escape_stub` 的出脚直道被别的网已布的铜封死
   ⇒ ★**旧 rip-up (`_blockers_for`) 只查起步格附近 ⇒ 拆不到封死出脚走廊的那条**
   ⇒ ★**实测 19 个候选网一根线都没拆**

★**四条断言**:
   ① env 旋钮存在且默认关
   ② 真实的 `_blockers_for` 在这个场景里 **返回空** (证明旧 rip-up 确实看不见)
   ③ 真实的 `_escape_blockers` **找到了封堵者**
   ④ `RIPUP_ESC=1` 时 ripup **真的拆了那根线并重布成功**; `RIPUP_ESC=0` 时 **一根都不拆** (老行为不变)
"""
import ast, types, sys, os, re

SRC = 'state/gen_pcb_routing.py'
src = open(SRC, encoding='utf-8').read()
ast.parse(src)

# ★**源码级前置断言**
assert 'RIPUP_ESC = os.environ.get("PCB_RIPUP_ESC", "0") == "1"' in src, '★缺 env 旋钮'
assert 'os.environ.get("PCB_RIPUP_ESC", "0")' in src, '★默认值不是关'
assert 'def _escape_blockers(self, net, maxn=6):' in src, '★缺 _escape_blockers 方法'
assert 'if not bl and RIPUP_ESC:' in src, '★ripup 里没接上出脚走廊兜底'

# ── 真方法抠出来 ──
m_esc = re.search(r"\n    def _escape_blockers\(self, net, maxn=6\):.*?\n        return res\[:maxn\]\n", src, re.S)
assert m_esc, '★抠不出 _escape_blockers'
m_blk = re.search(r"\n    def _blockers_for\(self, net, cells, maxn=6\):.*?\n        return out\[:maxn\]\n", src, re.S)
assert m_blk, '★抠不出 _blockers_for'
m_rip = re.search(r"\n    def ripup_and_reroute\(self, nets.*?\n        return ok\n", src, re.S)
assert m_rip, '★抠不出 ripup_and_reroute'

# ── 模块级常量/函数 (从源码里取真值, 不复刻) ──
def _grab(name):
    mm = re.search(r'^%s = .*$' % re.escape(name), src, re.M)
    assert mm, '★缺常量 ' + name
    return eval(mm.group(0).split('=', 1)[1].strip(), {}, {})

CLEAR = _grab('CLEAR')
ESC_LENS = _grab('ESC_LENS')
W_MIN = _grab('W_MIN')
W_SIG = _grab('W_SIG')

# ★直接从源码抠两个距离函数 (不复刻)
ns2 = {'math': __import__('math')}
# ★★边界必须只认**顶格** def/class ⇒ ★否则会把 _seg_seg_dist 内部的嵌套 def cross 当成函数结尾
m_pt = re.search(r"\ndef _pt_seg_dist\(.*?(?=\n(?:def |class ))", src, re.S)
m_ss = re.search(r"\ndef _seg_seg_dist\(.*?(?=\n(?:def |class ))", src, re.S)
assert m_pt and m_ss, '★抠不出距离函数'
exec(compile(m_pt.group(0), '<a>', 'exec'), ns2)
exec(compile(m_ss.group(0), '<b>', 'exec'), ns2)
_pt_seg_dist = ns2['_pt_seg_dist']
_seg_seg_dist = ns2['_seg_seg_dist']


def make_router(blocker_present):
    r = types.SimpleNamespace()
    r.routed = set()
    r.routed_ok = set()
    r.tracks = []
    r.vias = []
    # ★**封堵者**: 别人的 GND 线, 压在焊盘正上方 0.6mm ⇒ 出脚直道 (0,1) 方向必被挡
    r.BLOCKER = ("GND", 10.0, 10.6, 20.0, 10.6, 0, 0.25)
    if blocker_present:
        r.tracks = [r.BLOCKER]
    r.net_pads = {"NET_X": [("U1", "1", 10.0, 10.0, (0,))]}
    r.ripped = []
    r.calls = []

    def route_net(net, width=W_SIG, **kw):
        r.calls.append(net)
        # ★模拟真实语义: 封堵者还在 ⇒ 还是布不通; 被拆了 ⇒ 通
        ok = r.BLOCKER not in r.tracks
        r.routed.add(net)
        if ok:
            r.routed_ok.add(net)
        return {"ok": ok, "fail": 0 if ok else 1, "net": net}

    r.route_net = route_net
    r.rebuild_halo = lambda: None
    r._net_start_cells = lambda net: [(0, 1)]
    # ★**网格几何** (给真的 _blockers_for 用): 起步格在 (0.25,0.25) ⇒ 离封堵者很远
    r.W = 100
    r.g = 0.25
    r.bb = (0.0, 0.0)
    r._cx = lambda i: i * r.g + r.bb[0]
    r._cj = lambda j: j * r.g + r.bb[1]
    r._idx = lambda i, j: j * r.W + i
    return r


def load_methods(r, ripup_esc):
    g = {
        'RIPUP_ESC': ripup_esc,
        'RIPUP_ALIVE': True,
        'CLEAR': CLEAR,
        'ESC_LENS': ESC_LENS,
        'W_MIN': W_MIN,
        'W_SIG': W_SIG,
        'HALO_MARGIN': 0.20,   # ★测试里取默认值 (源码是 float(os.environ.get(...)))
        '_pt_seg_dist': _pt_seg_dist,
        '_seg_seg_dist': _seg_seg_dist,
        'math': __import__('math'),
    }
    # ★抠出来的是"类方法"(带 4 空格缩进) ⇒ 用 class 壳包一层再 exec
    cls_src = 'class _R:\n' + m_esc.group(0) + m_blk.group(0) + m_rip.group(0)
    cg = {}
    exec(compile(cls_src, '<cls>', 'exec'), g, cg)
    R = cg['_R']
    r._escape_blockers = R._escape_blockers.__get__(r)
    r._blockers_for = R._blockers_for.__get__(r)
    r.ripup_and_reroute = R.ripup_and_reroute.__get__(r)
    return g


# ── ② 真的 _blockers_for 在这个场景返回空 ──
r = make_router(True)
load_methods(r, False)
bl = r._blockers_for("NET_X", r._net_start_cells("NET_X"), 6)
assert bl == [], '★前提不成立: 旧 _blockers_for 本该看不见封堵者, 却看见了 %r' % (bl,)
print('  ✔ 旧 _blockers_for 看不见出脚走廊的封堵 (返回空) ⇒ 证明旧 rip-up 拆不到它')

# ── ③ 真的 _escape_blockers 找到了封堵者 ──
r2 = make_router(True)
load_methods(r2, True)
eb = r2._escape_blockers("NET_X", 6)
assert eb, '★_escape_blockers 没找到封堵者'
assert eb[0][1] == r2.BLOCKER, '★找到的不是封堵者: %r' % (eb[0],)
print('  ✔ _escape_blockers 找到封堵者: %s' % (eb[0][1],))

# ── ④ RIPUP_ESC=1 ⇒ 真的拆了并重布成功 ──
r3 = make_router(True)
load_methods(r3, True)
n = r3.ripup_and_reroute(["NET_X"], rip_per_net=6, verbose=True)
assert n == 1, '★ripup 没救回来 (n=%r)' % n
assert r3.BLOCKER not in r3.tracks, '★封堵者没被拆'
assert "NET_X" in r3.calls, '★没重布'
print('  ✔ RIPUP_ESC=1 ⇒ 拆掉封堵者并重布成功')

# ── ④b RIPUP_ESC=0 ⇒ 一根都不拆 (老行为不变) ──
r4 = make_router(True)
load_methods(r4, False)
n2 = r4.ripup_and_reroute(["NET_X"], rip_per_net=6, verbose=False)
assert n2 == 0, '★默认关时竟然救回来了 (n=%r) ⇒ 默认行为被改了' % n2
assert r4.BLOCKER in r4.tracks, '★默认关时竟然拆了铜 ⇒ 老行为被改了'
print('  ✔ RIPUP_ESC=0 (默认) ⇒ 旧行为逐位不变 (不拆线, 不救回)')

print('ALL TESTS PASS')
