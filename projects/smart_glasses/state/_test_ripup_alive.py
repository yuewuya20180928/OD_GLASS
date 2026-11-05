# -*- coding: utf-8 -*-
"""★_test_ripup_alive.py -- v49 "rip-up 复活" 单测

★★★**验的是真实代码路径**: 用一个 ★**最小假的 router 对象** 跑 `ripup_and_reroute`
   ⇒ ★**真的走一遍守卫/拆线/重布/还原** ⇒ ★而不是只 grep 字符串

★**为什么要这样**: ★这次的 bug 就是"看起来有代码, 实际一行都没执行"
   ⇒ ★**只测字符串会重犯同样的错** ⇒ ★**必须让代码真跑一遍**
"""
import ast, types, sys, os

src = open("state/gen_pcb_routing.py", encoding="utf-8").read()
ast.parse(src)

# ★**源码级前置断言**
assert 'RIPUP_ALIVE = os.environ.get("PCB_RIPUP_ALIVE", "0") == "1"' in src, "★缺 env 旋钮"
assert "self.routed_ok = set()" in src, "★缺 routed_ok"
assert "if ok and RIPUP_ALIVE:" in src, "★成功才记 routed_ok 的分支不在"
assert "_skip = (net in self.routed_ok) if RIPUP_ALIVE else (net in self.routed)" in src, "★守卫没改"
# ★**默认关时逐位一致**
assert 'os.environ.get("PCB_RIPUP_ALIVE", "0")' in src, "★默认值不是关"

# ── 把 route_net / rebuild_halo / _net_start_cells / _blockers_for 抽出来做假实现 ──
def make_router(fail_nets, routed_mode):
    """routed_mode='old' ⇒ 失败网也进 routed (旧行为)
       routed_mode='new' ⇒ 只有成功网进 routed, 失败网只进 routed (新行为: 守卫看 routed_ok)"""
    r = types.SimpleNamespace()
    r.routed = set()
    r.routed_ok = set()
    r.tracks = [("GND", 0.0, 0.0, 10.0, 0.0, 0, 0.3),   # 挡路的别人的线
                ("GND", 0.0, 0.0, 0.0, 10.0, 0, 0.3)]
    r.vias = []
    r.calls = []
    r.ripped_total = 0

    def route_net(net, width=0.25, **kw):
        r.calls.append(net)
        ok = net not in fail_nets
        # ★模拟真实 route_net 的记账语义
        r.routed.add(net)
        if ok and routed_mode == "new":
            r.routed_ok.add(net)
        return {"ok": ok, "fail": 0 if ok else 1, "net": net}

    r.route_net = route_net
    r.rebuild_halo = lambda: None
    r._net_start_cells = lambda net: [(0, 1)]
    r._blockers_for = lambda net, cells, k: [(0, r.tracks[0]), (0, r.tracks[1])]
    return r

# ★把方法从源码里抠出来执行 (★用真实实现, 不用复刻)
import re
m = re.search(r"\n    def ripup_and_reroute\(self, nets.*?\n        return ok\n", src, re.S)
assert m, "★抠不出 ripup_and_reroute"
method_src = m.group(0)

def run_ripup(r, nets, alive):
    """★把方法体绑到假 router 上真跑一遍
       ★alive 独立注入 ⇒ 同一进程里能对比"旧守卫"和"新守卫"两种行为"""
    ns = {"RIPUP_ALIVE": alive,
          "W_SIG": 0.25, "_pt_seg_dist": lambda *a: 0.0}
    exec("class _R:\n" + method_src, ns)
    inst = ns["_R"]()
    inst.__dict__.update(r.__dict__)
    out = inst.ripup_and_reroute(nets, rip_per_net=6, verbose=False)
    r.__dict__.update(inst.__dict__)
    return out

# ════════ 测试 1: ★旧行为 = 失败网一次都不会被试 ════════
r_old = make_router(fail_nets={"NET_A"}, routed_mode="old")
r_old.routed.add("NET_A")          # ★旧行为: 失败网已在 routed
n = run_ripup(r_old, ["NET_A"], alive=False)   # ★旧守卫
assert r_old.calls == [], "★旧守卫下不该调用 route_net (失败网在 routed 里被跳过)"
assert n == 0, "★旧行为重布成功数=0"
print("✔ 旧行为复现: 失败网在 routed 里 ⇒ route_net 一次都没被调 (★这正是 v37 日志的现象)")

# ════════ 测试 2: ★新行为 = 失败网真的会被拆线重布 ════════
r_new = make_router(fail_nets=set(), routed_mode="new")
r_new.routed.add("NET_A")          # ★失败网在 routed (和 route_net 的记账一致)
assert "NET_A" not in r_new.routed_ok
n = run_ripup(r_new, ["NET_A"], alive=True)    # ★新守卫
assert r_new.calls and r_new.calls[0] == "NET_A", "★新守卫必须真的调 route_net"
assert n == 1, "★新行为重布成功数应为 1, 实际 %d" % n
print("✔ 新行为: 失败网 (在 routed 但不在 routed_ok) ⇒ 真的被拆线重布 ⇒ 成功")

# ════════ 测试 3: ★已经成功的网仍然要跳过 (不许重复布) ════════
r_new2 = make_router(fail_nets=set(), routed_mode="new")
r_new2.routed.add("NET_B"); r_new2.routed_ok.add("NET_B")
n = run_ripup(r_new2, ["NET_B"], alive=True)
assert r_new2.calls == [], "★成功的网必须跳过"
assert n == 0
print("✔ 成功的网仍被跳过 (不会重复布线)")

# ════════ 测试 4: ★重布失败 ⇒ 线要还原 (不许丢铜) ════════
r_new3 = make_router(fail_nets={"NET_C"}, routed_mode="new")
r_new3.routed.add("NET_C")
n_before = len(r_new3.tracks)
n = run_ripup(r_new3, ["NET_C"], alive=True)
assert n == 0, "★重布失败数应为 0"
assert len(r_new3.tracks) == n_before, "★重布失败必须还原被拆的线 (%d -> %d)" % (n_before, len(r_new3.tracks))
print("✔ 重布失败 ⇒ 被拆的线全部还原 (板子上不会少铜)")

print("ALL TESTS PASS")
