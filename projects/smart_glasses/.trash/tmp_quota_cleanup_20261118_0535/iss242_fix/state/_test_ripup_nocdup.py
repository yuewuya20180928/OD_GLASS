# -*- coding: utf-8 -*-
"""★_test_ripup_nocdup.py -- v49 (c) 单测: 重布前清本网旧铜, 失败时原样还原

★★★**为什么必须测**: `route_net()` 体内 **0 处**碰 `self.tracks`/`self.vias`
   ⇒ ★**它从零再画** ⇒ ⇒ 不清旧铜 ⇒ ★**同一段铜画两遍** ⇒ ⇒ **重复铜 ⇒ DRC 爆**
   ⇒ ★**这是"只修守卫"会踩到的雷** ⇒ 必须有单测挡住

★★**测的是真实代码路径** (★和 `_test_ripup_alive.py` 同一套路)
"""
import ast, types, re, os

src = open("state/gen_pcb_routing.py", encoding="utf-8").read()
ast.parse(src)

# ★**源码级前置断言**
assert "own_t[_n] = [s for s in self.tracks if s[0] == _n and s not in rip_set]" in src, "★缺 own_t 备份"
assert "keep = [s for s in self.tracks if s not in rip_set and s[0] not in affected]" in src, "★keep 没排除受影响网"
assert "keep_v = [v for v in self.vias if v[0] not in affected]" in src, "★keep_v 没排除受影响网"
assert "self.tracks = self.tracks + own_t.get(rn, [])" in src, "★缺 rn 还原"
assert "[s for s in ripped if s[0] == _n]" in src, "★失败时没还原被拆的线"
# ★**第二轮 rip-up 必须在"其余网"之后**
_i_rest = src.index('print("  [REST] 其余 %d 个网已布" % len(rest))')
_i_rip2 = src.index('[RIPUP] 第二轮 (其余网之后)')
assert _i_rip2 > _i_rest, "★第二轮 rip-up 必须排在'其余网'之后"

m = re.search(r"\n    def ripup_and_reroute\(self, nets.*?\n        return ok\n", src, re.S)
assert m, "★抠不出 ripup_and_reroute"
method_src = m.group(0)


def make_router(fail_nets, net_own_tracks=0):
    r = types.SimpleNamespace()
    r.routed = set()
    r.routed_ok = set()
    # ★**失败网自己已经有的铜** (★模拟"布了一半")
    r.tracks = [("NET_A", 1.0, 1.0, 2.0, 1.0, 0, 0.25) for _ in range(net_own_tracks)]
    r.tracks += [("GND", 0.0, 0.0, 10.0, 0.0, 0, 0.3)]
    r.vias = [("NET_A", 5.0, 5.0)] * net_own_tracks
    r.calls = []

    def route_net(net, width=0.25, **kw):
        r.calls.append(net)
        ok = net not in fail_nets
        # ★模拟 route_net 真实行为: ★**它不碰 self.tracks** ⇒ 画完这里也不加
        #   (★由被测代码自己管清/还原)
        r.routed.add(net)
        if ok:
            r.routed_ok.add(net)
        return {"ok": ok, "fail": 0 if ok else 1, "net": net}

    r.route_net = route_net
    r.rebuild_halo = lambda: None
    r._net_start_cells = lambda net: [(0, 1)]
    r._blockers_for = lambda net, cells, k: [(0, s) for s in r.tracks if s[0] == "GND"]
    return r


def run_ripup(r, nets, alive=True):
    ns = {"RIPUP_ALIVE": alive, "W_SIG": 0.25, "_pt_seg_dist": lambda *a: 0.0}
    exec("class _R:\n" + method_src, ns)
    inst = ns["_R"]()
    inst.__dict__.update(r.__dict__)
    out = inst.ripup_and_reroute(nets, rip_per_net=6, verbose=False)
    r.__dict__.update(inst.__dict__)
    return out


# ════════ 测试 1: ★重布前本网旧铜必须被清掉 (★不许画重复铜) ════════
r1 = make_router(fail_nets=set(), net_own_tracks=3)
n = run_ripup(r1, ["NET_A"])
assert n == 1, "★重布应成功"
own_left = [s for s in r1.tracks if s[0] == "NET_A"]
assert len(own_left) == 0, "★重布前必须清掉本网旧铜, 实际还剩 %d 段 (⇒ 会画重复铜)" % len(own_left)
own_v = [v for v in r1.vias if v[0] == "NET_A"]
assert len(own_v) == 0, "★重布前必须清掉本网旧孔, 实际还剩 %d 个" % len(own_v)
print("✔ 重布前清掉了本网旧铜 (%d 段旧铜 + 旧孔) ⇒ 不会画重复铜" % 3)

# ════════ 测试 2: ★重布失败 ⇒ 本网旧铜原样还原 (★不许丢已布好的腿) ════════
r2 = make_router(fail_nets={"NET_A"}, net_own_tracks=3)
before = [s for s in r2.tracks if s[0] == "NET_A"]
n = run_ripup(r2, ["NET_A"])
assert n == 0, "★重布失败数应为 0"
after = [s for s in r2.tracks if s[0] == "NET_A"]
assert len(after) == len(before), "★重布失败必须还原本网旧铜: %d -> %d" % (len(before), len(after))
assert len([v for v in r2.vias if v[0] == "NET_A"]) == 3, "★重布失败必须还原本网旧孔"
print("✔ 重布失败 ⇒ 本网旧铜 + 旧孔原样还原 (不丢已布好的腿)")

# ════════ 测试 3: ★被拆的挡路线也要还原 (★板子不能少铜) ════════
r3 = make_router(fail_nets={"NET_A"}, net_own_tracks=1)
gnd_before = [s for s in r3.tracks if s[0] == "GND"]
n = run_ripup(r3, ["NET_A"])
assert n == 0
gnd_after = [s for s in r3.tracks if s[0] == "GND"]
assert len(gnd_after) == len(gnd_before), "★被拆的 GND 线必须还原: %d -> %d" % (len(gnd_before), len(gnd_after))
print("✔ 被拆的挡路 GND 线还原 (板子不少铜)")

print("ALL TESTS PASS")
