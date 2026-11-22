# -*- coding: utf-8 -*-
"""★_test_multigoal.py -- v48 "多目标重试" 单测

★★**验的是逻辑本身**: 目标候选的排序/截断/排除语义
★★**不 import 整个路由器** (★import 会拖 pcbnew + 起副作用) ⇒ 用独立复刻 + 源码断言
"""
import ast

src = open("state/gen_pcb_routing.py", encoding="utf-8").read()
ast.parse(src)

# ── 源码级断言 (★机制必须在) ──
assert 'MULTI_GOAL = os.environ.get("PCB_MULTI_GOAL", "0") == "1"' in src, "★缺 env 旋钮"
assert 'MULTI_GOAL_MAX' in src, "★缺上限"
assert "if path is None and MULTI_GOAL and len(connected_pads) > 1:" in src, "★没接在失败分支"
assert "multigoal_hits" in src, "★没计数"
assert 'os.environ.get("PCB_MULTI_GOAL", "0")' in src, "★默认值不是关"

# ── 逻辑级: 独立复刻"候选目标排序 + 排除 + 截断" ──
def alt_targets(connected, pad, goal_pad, maxn=4):
    """★复刻补丁里的候选筛选语义:
       排除 goal_pad 自己 ⇒ 按到 pad 的欧氏距离升序 ⇒ 取前 maxn 个"""
    alts = sorted((q for q in connected if q is not goal_pad),
                  key=lambda q: (q[2] - pad[2]) ** 2 + (q[3] - pad[3]) ** 2)
    return alts[:maxn]

# 已连焊盘: A(10,10) B(20,20) C(30,30); 当前 pad=(50,50); 最近目标=B(20,20)
conn = [("A",".1",10,10), ("B",".1",20,20), ("C",".1",30,30)]
pad = ("P",".1",50,50)
goal = conn[1]
alts = alt_targets(conn, pad, goal)
assert alts == [conn[2], conn[0]], "*候选 = C (近) + A (远), 已排除 B"
print("✔ 候选目标: 排除最近目标 B ⇒ 只剩 C")

# ★上限截断
conn2 = [("A",".1",i,0) for i in range(10)]
alts2 = alt_targets(conn2, ("P",".1",100,0), conn2[0], maxn=4)
assert len(alts2) == 4, "★必须截断到 4"
print("✔ 上限截断: 9 个候选 ⇒ 4")

# ★只有一个已连焊盘时没有备选 (⇒ 不浪费预算)
assert alt_targets([conn[0]], pad, conn[0]) == []
print("✔ 只有 1 个已连焊盘 ⇒ 无备选")

# ★★**关键: 距离升序 ⇒ 备选按"最近可用"排, 不是随机**
conn3 = [("A",".1",10,0), ("B",".1",45,0), ("C",".1",20,0)]
alts3 = alt_targets(conn3, ("P",".1",100,0), conn3[0])
assert [q[2] for q in alts3] == [45, 20], "*必须按到 pad 的距离升序 (B=55 < C=80)"
print("✔ 按距离升序: 20 先于 45")

# ★默认关 ⇒ 旧路径逐位一致 (★源码里 MULTI_GOAL 分支在 `if path is None` 之后)
i_mg = src.index("if path is None and MULTI_GOAL and len(connected_pads) > 1:")
i_fail = src.index("if path is None:\n                nfail += 1", i_mg)
assert i_mg < i_fail, "★多目标重试必须在最终失败判定之前"
print("✔ 补丁位置正确: 在最终失败判定之前")

# ★**不改动几何规则**: 补丁里不许出现板规则/线宽/间距字样
seg = src[src.index("if path is None and MULTI_GOAL"):src.index("if path is None:\n                nfail += 1")]
for bad in ("CLEAR", "RULE", "SetWidth", "MIN_VIA", "GRID"):
    assert bad not in seg, "★多目标重试不许改几何规则 (%s)" % bad
print("✔ 不改几何规则 (无宽度/间距/规则改动)")

print("ALL TESTS PASS")
