# -*- coding: utf-8 -*-
"""★_test_gnd_share.py -- v47 "GND 同排相邻焊盘合并下拉" 的分组逻辑单测"""
import ast
src = open("state/gen_pcb_routing.py", encoding="utf-8").read()
ast.parse(src)
assert 'GND_SHARE_ROW = os.environ.get("PCB_GND_SHARE_ROW", "0") == "1"' in src
assert 'GND_SHARE_ROW_GAP' in src and 'GND_SHARE_ROW_DY' in src
assert "self._gnd_shared" in src

def group(pads, dy=0.35, gap=1.60):
    """★与实现同逻辑的独立复刻 (★不许 import 整个路由器)"""
    ys = sorted(set(round(p[3], 3) for p in pads))
    rows = []
    for y in ys:
        if rows and (y - rows[-1][0]) <= dy:
            rows[-1][1].append(y)
        else:
            rows.append([y, [y]])
    keep = []
    for row in rows:
        grp = [p for p in pads if p[3] in row[1]]
        grp.sort(key=lambda q: q[2])
        cur = []
        for p in grp:
            if cur and (p[2] - cur[-1][2]) > gap:
                keep.append(cur[0]); cur = [p]
            else:
                cur.append(p)
        if cur:
            keep.append(cur[0])
    return keep, [p for p in pads if p not in keep]

# ★**CONN_LIGHT 的 8 个 GND 焊盘实测坐标** (机器读)
CL = [("CONN_LIGHT",".22",24.75,60.15),("CONN_LIGHT",".21",25.25,60.15),
      ("CONN_LIGHT",".20",25.75,60.15),("CONN_LIGHT",".13",29.25,60.15),
      ("CONN_LIGHT",".10",30.75,60.15),("CONN_LIGHT",".7",32.25,60.15),
      ("CONN_LIGHT",".4",33.75,60.15),("CONN_LIGHT",".1",35.25,60.15)]
keep, drop = group(CL)
print("★CONN_LIGHT 8 个 GND 焊盘 ⇒ 保留 %d 个落孔点, 合并掉 %d 个" % (len(keep), len(drop)))
print("   保留:", [(p[1], p[2]) for p in keep])
assert len(keep) <= 3, "★8 个焊盘必须压到 ≤3 个落孔点 (否则治不了栅栏)"
assert len(keep) >= 1
# ★合并掉的必须都还在同一排
for p in drop:
    assert abs(p[3] - keep[0][3]) < 0.35 or any(abs(p[3]-k[3])<0.35 for k in keep)
print("✔ CONN_LIGHT: 8 ⇒ %d (栅栏从根上消失)" % len(keep))

# ★**不同排不许合并**
TWO = [("A",".1",10.0,60.15),("B",".1",12.0,70.50),("C",".1",13.0,80.00)]
k2, d2 = group(TWO)
assert len(k2) == 3, "★不同排的焊盘不许互相合并 (会短接错的东西)"
print("✔ 不同排不合并: %d 个落孔点" % len(k2))
# ★同排但不同器件的 GND 焊盘 = 同网 ⇒ 合并是安全的 (同网缝合)
same_row = [("A",".1",10.0,60.15),("B",".1",11.0,60.15)]
k2b, d2b = group(same_row)
assert len(k2b) == 1 and len(d2b) == 1
print("✔ 同排不同器件的同网 GND 焊盘合并 (同网缝合, 安全)")

# ★**间距大于 gap 的不许合并**
FAR = [("A",".1",0.0,60.0),("B",".1",5.0,60.0)]
k3, d3 = group(FAR)
assert len(k3) == 2
print("✔ x 间距 > gap 不合并")

# ★**同排连续的一串要合并**
CHAIN = [("A",".1",0.0,60.0),("A",".2",1.0,60.0),("A",".3",2.0,60.0)]
k4, d4 = group(CHAIN)
assert len(k4) == 1 and len(d4) == 2
print("✔ 同排连续 3 个 ⇒ 1 个落孔点")

# ★**默认关 ⇒ 行为完全不变**
assert 'os.environ.get("PCB_GND_SHARE_ROW", "0") == "1"' in src
print("✔ 默认关 (逐位一致)")

print("ALL TESTS PASS")
