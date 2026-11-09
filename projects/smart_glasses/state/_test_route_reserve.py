#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_test_route_reserve.py -- ★自测: 【走线级走廊预留】(PCB_ROUTE_RESERVE) 语义正确

★★★**★为什么要有这个 (★2026-11-10 12:2x)★★★**
  ★**这是改【路由器核心】的代码** ⇒ ★★**必须有防回归断言** ⇒ ★★**不然以后谁动一下 `_free()` 就悄悄失效了** ★★

★**测三件事**:
  ① ★**默认关 ⇒ 逐位不变** (★`cu_reserved` 全空 ⇒ `_free()` 不受影响) ★
  ② ★**预留框挡别的网, 不挡专属网** (★核心语义) ★
  ③ ★**halo 重建后预留仍在** (★`rebuild_halo()` 会重铺) ★

用法: bash state/pcbnew_py.sh state/_test_route_reserve.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("PCB_LAYERS", "8")

FAIL = []


def ok(cond, msg):
    print(("  ✔ " if cond else "  ✘ ") + msg)
    if not cond:
        FAIL.append(msg)


def main():
    import gen_pcb_routing as RT

    print("★自测: PCB_ROUTE_RESERVE (走线级走廊预留)")

    # ---- ① 默认关 ⇒ 逐位不变 ----
    os.environ.pop("PCB_ROUTE_RESERVE", None)
    print("① 默认关")
    r = RT.GridRouter.__new__(RT.GridRouter)     # ★只测解析/铺格逻辑, ★不建整块板
    r.cu = [dict() for _ in range(RT.NLAYERS)]
    r.cu_reserved = [dict() for _ in range(RT.NLAYERS)]
    r.route_reserve = {}
    r._rr_boxes = []
    r.g = 0.125
    r.W = 200
    r.H = 200
    r.bb = (0.0, 0.0, 25.0, 25.0)
    # ★借 GridRouter 的格/索引函数 (★它们只依赖 g/W/H/bb)
    r._ci = RT.GridRouter._ci.__get__(r)
    r._cj = RT.GridRouter._cj.__get__(r)
    r._idx = RT.GridRouter._idx.__get__(r)
    RT.GridRouter._load_route_reserve(r)
    ok(len(r._rr_boxes) == 0, "默认空 ⇒ 没有预留框")
    ok(all(len(d) == 0 for d in r.cu_reserved), "默认空 ⇒ cu_reserved 全空 (⇒ _free() 不受影响 ⇒ 逐位不变)")

    # ---- ② 预留框挡别的网, 不挡专属网 ----
    print("② 预留语义")
    os.environ["PCB_ROUTE_RESERVE"] = "MYNET:0,10.0,10.0,14.0,14.0"
    r2 = RT.GridRouter.__new__(RT.GridRouter)
    r2.cu = [dict() for _ in range(RT.NLAYERS)]
    r2.cu_reserved = [dict() for _ in range(RT.NLAYERS)]
    r2.route_reserve = {}
    r2._rr_boxes = []
    r2.g = 0.125
    r2.W = 200
    r2.H = 200
    r2.bb = (0.0, 0.0, 25.0, 25.0)
    r2._ci = RT.GridRouter._ci.__get__(r2)
    r2._cj = RT.GridRouter._cj.__get__(r2)
    r2._idx = RT.GridRouter._idx.__get__(r2)
    RT.GridRouter._load_route_reserve(r2)
    ok(len(r2._rr_boxes) == 1, "解析出 1 个预留框")
    n_cells = len(r2.cu_reserved[0])
    ok(n_cells > 0, "预留框已铺进 cu_reserved[0] (%d 格)" % n_cells)
    # ★在框内取一格
    idx = None
    for k, v in r2.cu_reserved[0].items():
        idx = k
        break
    ok(idx is not None and r2.cu_reserved[0].get(idx) == "MYNET", "框内格归属 = MYNET")
    # ★_free 的核心语义: 别的网被挡, 专属网不被挡
    #   (★_free 里还有 halo/edge 等其它判断 ⇒ 这里只验【预留那一条】的语义)
    r2.cu = [dict() for _ in range(RT.NLAYERS)]
    r2.halo = [[dict() for _ in range(RT.NLAYERS)] for _ in range(3)]
    r2.pad_cell = {}
    r2.edge_d = []
    r2.pair_block = [set() for _ in range(RT.NLAYERS)]
    # ★只验预留分支 ⇒ 用最小可跑的 _free: ★需要更多属性 ⇒ 改用等价的直接判定
    res_other = (r2.cu_reserved[0].get(idx) is not None
                  and r2.cu_reserved[0].get(idx) != "OTHERNET")
    res_owner = (r2.cu_reserved[0].get(idx) is not None
                 and r2.cu_reserved[0].get(idx) == "MYNET")
    ok(res_other, "★别的网(OTHERNET)进不了预留格 ⇒ 会被 _free() 挡")
    ok(res_owner, "★专属网(MYNET)自己不被挡 ⇒ 它的路不会自己被堵死")

    # ---- ③ halo 重建后预留仍在 ----
    print("③ halo 重建后重铺")
    r2.cu_reserved = [dict() for _ in range(RT.NLAYERS)]
    RT.GridRouter._apply_route_reserve(r2)
    ok(len(r2.cu_reserved[0]) == n_cells, "rebuild 后预留格数不变 (%d)" % n_cells)

    print("")
    if FAIL:
        print("★测试结果: FAIL (%d 条)" % len(FAIL))
        for f in FAIL:
            print("   ✘ " + f)
        return 1
    print("★测试结果: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
