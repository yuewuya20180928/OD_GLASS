#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_pair_swap_retry.py -- ★★★**`PCB_PAIR_SWAP_RETRY` 自测 (2026-11-08 23:5x) ★★★

★★**这个开关解决什么 (★机制依据: `state/PAIR_AWARE_ROUTING_PLAN.md` §3.2)****
  ★**"P 通 N 不通" 是【顺序依赖】**: 先布的那条腿占住走廊 ⇒ 后布的那条腿出不来
  ⇒ ★**⇒ 修法: 跟腿彻底没布出来时, 把主腿的铜摘掉, 换边重跑整对**
  ⇒ ★**换边用同一套机制递归调用自己 (只换主/跟顺序) ⇒ 不新增算法**

★★**本自测用【假路由器】跑真函数** (★mock ⇒ 快, 且能精确摆出"主腿通/跟腿不通"的局面)★★
  A1 ★**默认 (开关未设) ⇒ 不发生换边** (★调用次数与结果逐位不变 ⇒ 既有臂可复现)
  A2 ★**开关打开 + 换边后两条腿都通 ⇒ 采纳换边** (★res["swapped"]=True · 跟腿 ok=True)
  A3 ★**开关打开 + 换边后还是不通 ⇒ 原样恢复** (★★**tracks/vias 必须与调用前逐条相同** ⇒ 不制造更差的板)
  A4 ★**开关打开 + 跟腿本来就通 ⇒ 根本不触发换边** (★省掉不必要的重跑)

用法: `python3 state/test_pair_swap_retry.py`
(★注意: 开关是 env ⇒ 【默认档】与【开启档】要分两次进程跑 ⇒ 本脚本用 --on 参数切档, 由外层 shell 调两次)
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import gen_pcb_routing as RT  # noqa: E402


class MockRouter:
    """★假路由器: 用【逐次调用脚本】摆出想要的局面, 并记录调用"""
    def __init__(self, script):
        # ★script = [(ok, len), ...] ⇒ 第 1 次 = 主腿, 第 2 次 = 耦合跟腿, 第 3 次 = 兵底跟腿(普通网),
        # ★          第 4/5 次 = 换边后的新主腿/新跟腿
        self.script = list(script)
        self.calls = []          # 每次 route_net 的网名
        self.tracks = [("NET_A", 0.0, 0.0, 1.0, 0.0, 0, 0.25)]
        self.vias = [("NET_A", 2.0, 0.0, 0, 7)]
        self.rebuilds = 0
        # ★路由框架需要的最小属性集
        self.g = 0.125
        self.bb = (0.0, 0.0)
        self.W = 100
        self.H = 100
        self.net_pads = {}
        self.pair_partner = None
        self.pair_block = set()
        self.pair_block_narrow = set()
        self.esc_avoid = set()
        self.esc_used_dirs = {}

    def rebuild_halo(self):
        self.rebuilds += 1

    def route_net(self, net, width=None, allow_via=True, trunk=None,
                  profiles=None, alpha=0.0, **kw):
        i = len(self.calls)
        self.calls.append(net)
        if i < len(self.script):
            ok, ln = self.script[i]
        else:
            ok, ln = False, 0.0
        return {"ok": ok, "len": ln, "fail": 0 if ok else 1, "ring": 2}

    def build_pair_block(self, net_p, min_c=0.5, exempt_net=None, exempt_r=1.2):
        return set(), set()

    def build_pair_guide(self, net_p, ring=3):
        return {}, 0

    def net_length(self, net):
        return sum(1 for t in self.tracks if t[0] == net) * 1.0

    def add_meander_v3(self, net, extra_mm, **kw):
        return extra_mm

    def add_meander_v2(self, net, extra_mm, **kw):
        return extra_mm


def snapshot(r):
    return (list(r.tracks), list(r.vias))


def main():
    on = "--on" in sys.argv
    if on:
        os.environ["PCB_PAIR_SWAP_RETRY"] = "1"
    else:
        os.environ.pop("PCB_PAIR_SWAP_RETRY", None)
    # ★**注意: RT 模块在 import 时读 env ⇒ 必须重载模块**
    import importlib
    RT2 = importlib.reload(RT)
    assert RT2.PAIR_SWAP_RETRY == (True if on else False), \
        "开关没读进来 (on=%s)" % on

    ok_all = True

    # ---- A1: 默认档 ⇒ 不换边 (只调 3 次: 主腿 + 耦合跟腿 + 兵底跟腿) ----
    # ★开启档下同场景会【试一次换边】(第 4 次调用 = 换边后的新主腿 ⇒ 失败 ⇒ 放弃并恢复) ⇒ 所以 A1 分两档断言
    r = MockRouter([(True, 10.0), (False, 0.0), (False, 0.0)])
    before = snapshot(r)
    res = RT2.route_diff_pair(r, "NET_P", "NET_N")
    after = snapshot(r)
    want_calls = 4 if on else 3
    if len(r.calls) != want_calls:
        print("❌ A1 失败: 调用次数 = %d (应 %d)" % (len(r.calls), want_calls)); ok_all = False
    elif res.get("swapped"):
        print("❌ A1 失败: 居然采纳了换边"); ok_all = False
    elif before[0] != after[0] or before[1] != after[1]:
        print("❌ A1 失败: 铜被改了 (tracks/vias 未恢复)"); ok_all = False
    else:
        print("✅ A1 %s (调用 %d 次 · 铜逐条未变 · 没采纳换边)"
              % ("开启档: 试了换边但放弃并恢复" if on else "默认档: 根本不换边", len(r.calls)))

    if on:
        # ---- A2: 开启档 + 换边后两条腿都通 ⇒ 采纳 ----
        r = MockRouter([(True, 10.0), (False, 0.0), (False, 0.0), (True, 8.0), (True, 9.0)])
        res = RT2.route_diff_pair(r, "NET_P", "NET_N")
        if not res.get("swapped"):
            print("❌ A2 失败: 没采纳换边 (res=%s)" % res); ok_all = False
        elif not res.get("n_ok") or not res.get("p_ok"):
            print("❌ A2 失败: 换边后腿没都通 (p_ok=%s n_ok=%s)" % (res.get("p_ok"), res.get("n_ok"))); ok_all = False
        elif len(r.calls) != 5:
            print("❌ A2 失败: 调用次数 = %d (应 5)" % len(r.calls)); ok_all = False
        else:
            print("✅ A2 采纳换边 (swapped=True · 两条腿都通 · 调用 5 次)")

        # ---- A3: 开启档 + 换边没赢 ⇒ 原样恢复 ----
        r = MockRouter([(True, 10.0), (False, 0.0), (False, 0.0), (True, 8.0), (False, 0.0)])
        before = snapshot(r)
        res = RT2.route_diff_pair(r, "NET_P", "NET_N")
        after = snapshot(r)
        if res.get("swapped"):
            print("❌ A3 失败: 换边没赢却采纳了"); ok_all = False
        elif before[0] != after[0] or before[1] != after[1]:
            print("❌ A3 失败: 没赢却改了铜 (tracks/vias 未恢复)"); ok_all = False
        else:
            print("✅ A3 没赢就原样恢复 (tracks/vias 逐条相同)")

        # ---- A4: 跟腿本来就通 ⇒ 不触发换边 ----
        r = MockRouter([(True, 10.0), (True, 10.0)])
        res = RT2.route_diff_pair(r, "NET_P", "NET_N")
        if len(r.calls) != 2 or res.get("swapped"):
            print("❌ A4 失败: 跟腿本来就通却做了换边 (calls=%d)" % len(r.calls)); ok_all = False
        else:
            print("✅ A4 跟腿本来就通 ⇒ 不换边 (调用 2 次)")
    else:
        print("— (A2/A3/A4 只在开启档跑)")

    print("SELFTEST %s" % ("ALL TESTS PASS" if ok_all else "FAIL"))
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
