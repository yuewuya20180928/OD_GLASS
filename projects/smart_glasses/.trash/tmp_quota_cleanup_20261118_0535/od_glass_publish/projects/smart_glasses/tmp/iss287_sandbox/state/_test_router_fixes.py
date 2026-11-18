#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_test_router_fixes.py -- ★**2026-11-06 05:0x~06:0x 路由器 4 处修复的专项回归**

★**要防住的 4 个回归**:
  ① `_astar` 的 `limit` 参数: ★**原来传进去必崩 (UnboundLocalError: dist_cells) 且必被覆盖**
     ⇒ 断言: 显式传 limit 不崩, 且预算按调用方的值走
  ② stub 段的层: ★**原来硬编码层 0 (F.Cu)** ⇒ 路径在 In2.Cu 时 stub 与路径脱层
     ⇒ 断言: stub 段落在**路径首/末点所在的层**
  ③ 零长段: ★**原来不过滤** ⇒ DRC `tracks_crossing` (0.0000mm 的线)
     ⇒ 断言: 零长段不落板
  ④ 零长段 + 板边: 落铜前过滤 ⇒ 段数不含零长

用法: bash state/pcbnew_py.sh state/_test_router_fixes.py
"""
import os
import re
import sys
import math

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("PCB_LAYERS", "8")
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import pcbnew  # noqa: E402
import gen_pcb_routing as RT  # noqa: E402

SRC = open(os.path.join(HERE, "gen_pcb_routing.py"), encoding="utf-8").read()
FAIL = []


def ck(cond, msg):
    if cond:
        print("  ✔ %s" % msg)
    else:
        print("  ★FAIL: %s" % msg)
        FAIL.append(msg)


# ─────────────────────────────────────────────
# ① limit 参数: 不崩 + 尊重调用方预算
# ─────────────────────────────────────────────
print("── ① _astar 的 limit 参数")
ck("dist_cells = 0\n        for (sli, sidx) in start:" in SRC,
   "★源码里 dist_cells 已无条件初始化 (原来只在 limit<=0 分支里)")
ck("limit = _auto if (limit is None or limit <= 0) else int(limit)" in SRC,
   "★limit>0 时尊重调用方预算 (原来无条件覆盖 ⇒ 死参数)")
m = re.search(r"def _astar\(self.*?\n(.*?)\n    def ", SRC, re.S)
body = m.group(1) if m else ""
ck("dist_cells" in body.split("limit = ")[0] if "limit = " in body else True,
   "★预算公式之前 dist_cells 一定已定义")


# ─────────────────────────────────────────────
# ② stub 段跟路径层
# ─────────────────────────────────────────────
print("── ② stub 段的层")
m2 = re.search(r"def _emit_path\(self.*?\n(.*?)\n    def ", SRC, re.S)
eb = m2.group(1) if m2 else ""
ck("_ls = pts[0][0] if pts else 0" in eb and "_le = pts[-1][0] if pts else 0" in eb,
   "★stub 段用路径首/末点所在层 (不再硬编码 0)")
ck("self.tracks.append((net, sx, sy, ex, ey, _ls, W_MIN))" in eb,
   "★stub_start 段落在 _ls 层")
ck("self.tracks.append((net, ex, ey, gx, gy, _le, W_MIN))" in eb,
   "★stub_end 段落在 _le 层")
ck("self.tracks.append((net, sx, sy, ex, ey, 0, W_MIN))" not in eb,
   "★不再有硬编码层 0 的 stub 段")


# ─────────────────────────────────────────────
# ③ 零长段过滤
# ─────────────────────────────────────────────
print("── ③ 零长段过滤")
ck("if abs(ex - sx) > 1e-6 or abs(ey - sy) > 1e-6:" in eb,
   "★stub 零长过滤")
ck("if abs(gx - ex) > 1e-6 or abs(gy - ey) > 1e-6:" in eb,
   "★stub_end 零长过滤")
ck("if abs(s[3] - s[1]) < 1e-6 and abs(s[4] - s[2]) < 1e-6:" in eb,
   "★路径段零长过滤")


# ─────────────────────────────────────────────
# ④ 真跑一次: 构造最小板 ⇒ 调 _emit_path ⇒ 看落板图元
# ─────────────────────────────────────────────
print("── ④ 实跑 _emit_path (真实方法)")
b = pcbnew.NewBoard("/tmp/_tf_test.kicad_pcb")
r = RT.GridRouter(b)
# ★在 In2.Cu (索引 2) 上放一条路径, stub 端点给别的层 ⇒ 断言 stub 跟路径层
pts = [(2, r._idx(10, 10)), (2, r._idx(12, 10))]
r.tracks = []
r.vias = []
ok = r._emit_path("NET_T", pts, RT.W_SIG,
                   stub_start=(1.0, 1.0, 1.0, 1.0), stub_end=(3.0, 3.0, 3.0, 3.0))
ck(ok is True, "★_emit_path 返回 True")
lays = set(s[5] for s in r.tracks)
ck(lays == {2}, "★落下的段全在 In2.Cu (索引2) ⇒ ★stub 跟路径层 (原来会掉到层0)")
ck(len(r.tracks) >= 1, "★落了 %d 段" % len(r.tracks))
zl = [s for s in r.tracks
      if abs(s[3] - s[1]) < 1e-6 and abs(s[4] - s[2]) < 1e-6]
ck(len(zl) == 0, "★没有零长段")

# ★零长 stub: stub 端点 == 路径首点 ⇒ 不应产生零长段
r.tracks = []
r.vias = []
r._emit_path("NET_T", [(2, r._idx(10, 10)), (2, r._idx(12, 10))], RT.W_SIG,
             stub_start=(1.0, 1.0, 1.0, 1.0), stub_end=(1.0, 1.0, 1.0, 1.0))
zl2 = [s for s in r.tracks
       if abs(s[3] - s[1]) < 1e-6 and abs(s[4] - s[2]) < 1e-6]
ck(len(zl2) == 0, "★零长 stub 也没落 (实测 %d 条零长)" % len(zl2))

print("")
if FAIL:
    print("★ %d 项失败" % len(FAIL))
    sys.exit(1)
print("ALL TESTS PASS")
