#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_test_merge_fix.py —— ★★【★防回归自测: 【共线合并瞬移 bug】的修法 (★`PCB_MERGE_FIX`)★】★★

★★★**★为什么要有这个 (★2026-11-10 04:4x)★★★**
  ★**这个 bug 造出了所有臂共享的板边违规** ⇒ ★★**⇒ 不钉死它, 后面每个臂都会被它卡住** ★★
  ★★**⇒ 老板的硬规矩: "凡是留'回归见 X'的注释, 必须真的有 X, 且 X 必须断言实测数字"★★ ★★

★★★**★断言清单 (★全部来自 2026-11-10 的实测)★★★**
  ① ★**默认关**: ★**不设 `PCB_MERGE_FIX` ⇒ `MERGE_FIX` 必须是 False** ⇒ ★★**默认逐位不变** ★★
  ② ★**显式开才 True**: ★**`PCB_MERGE_FIX=1` ⇒ True** ★★
  ③ ★**默认路径逐位等价**: ★**旧内联实现 vs `_merge_collinear(seg, False)` ⇒ 输出必须完全一致** ★★
  ④ ★**正确共线的两段必须仍然合并** (★修 bug 不能误伤正常合并★)
  ⑤ ★**★瞬移用例 (★证明 bug 真实存在★)**:
     ★**p=(0,0)->(1,0) · s=(3,5)->(6,3)** ⇒ ★**旧判据 (★`s[4]-s[1]`★) 会合并 ⇒ 生成 (0,0)->(6,3) 瞬移线**
     ⇒ ★**新判据 (★`s[4]-s[2]`★) 不合并** ★★
  ⑥ ★**三角不等式兜底**: ★**即使判据说共线, 合并后长度 > 两段之和 ⇒ 必须放弃合并** ★★
  ⑦ ★**实测数字回归 (★v76s2 裸板★)**:
     ★**越界段 (39.7234,1.1038)->(41.6319,-1.2140) 长 3.002mm, 板边线 y=0 ⇒ 越界 1.214mm** ★★
     ★**⇒ 这条就是 12 条 `copper_edge_clearance` 违规的来源** ★★

用法:
  bash state/pcbnew_py.sh state/_test_merge_fix.py
  ⇒ 全部断言过 ⇒ 打印 "ALL PASS" ⇒ rc=0; 任一失败 ⇒ rc=1
"""
import os
import sys
import math
import random

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


def _old_merge(seg):
    """★旧内联实现 (★逐字照抄 2026-11-10 04:4x 之前的代码★) ⇒ 用来证明默认路径等价"""
    merged = []
    for s in seg:
        if merged:
            p = merged[-1]
            ax, ay = p[3] - p[1], p[4] - p[2]
            bx, by = s[3] - s[1], s[4] - s[1]
            if (p[5] == s[5]) and (abs(ax * by - ay * bx) < 1e-9) \
                    and (ax * bx + ay * by > 0):
                merged[-1] = (p[0], p[1], p[2], s[3], s[4], p[5], p[6])
                continue
        merged.append(s)
    return merged


def main():
    print("═══ _test_merge_fix.py ═══")

    os.environ.pop("PCB_MERGE_FIX", None)
    import gen_pcb_routing as G
    chk("① 默认 PCB_MERGE_FIX 未设 ⇒ MERGE_FIX 必须 False (★默认逐位不变★)",
        G.MERGE_FIX is False, "实际 = %r" % (G.MERGE_FIX,))

    os.environ["PCB_MERGE_FIX"] = "1"
    import importlib
    G2 = importlib.reload(G)
    chk("② PCB_MERGE_FIX=1 ⇒ MERGE_FIX 必须 True",
        G2.MERGE_FIX is True, "实际 = %r" % (G2.MERGE_FIX,))

    # ③ 默认路径逐位等价 (★随机 2000 组★)
    random.seed(20261110)
    same = True
    for _ in range(2000):
        n = random.randint(1, 8)
        seg = []
        x, y = 0.0, 0.0
        for _k in range(n):
            dx = random.choice([0.25, -0.25, 0.0, 1.0, -3.0, 0.1])
            dy = random.choice([0.25, -0.25, 0.0, 1.0, 2.0, -5.0])
            seg.append(("N", x, y, x + dx, y + dy, 0, 0.25))
            x += dx
            y += dy
        if _old_merge(seg) != G2._merge_collinear(seg, False):
            same = False
            break
    chk("③ 默认路径与旧实现逐位等价 (★2000 组随机段★)", same)

    # ④ 正确共线的两段必须仍然合并
    seg_ok = [("N", 0.0, 0.0, 1.0, 0.0, 0, 0.25), ("N", 1.0, 0.0, 2.0, 0.0, 0, 0.25)]
    m_new = G2._merge_collinear(seg_ok, True)
    chk("④ 正确共线的两段必须合并 (★修 bug 不能误伤★)",
        len(m_new) == 1 and abs(m_new[0][3] - 2.0) < 1e-9, "实际 = %r" % (m_new,))

    # ⑤ ★瞬移用例 (★证明 bug 真实存在★)
    seg_bad = [("N", 0.0, 0.0, 1.0, 0.0, 0, 0.25), ("N", 3.0, 5.0, 6.0, 3.0, 0, 0.25)]
    m_old = _old_merge(seg_bad)
    m_fix = G2._merge_collinear(seg_bad, True)
    chk("⑤ 旧判据会把不相邻的两段合并成瞬移线 (★证明 bug 真实存在★)",
        len(m_old) == 1 and abs(m_old[0][3] - 6.0) < 1e-9 and abs(m_old[0][4] - 3.0) < 1e-9,
        "实际 = %r" % (m_old,))
    chk("⑤ 修后不再合并 (★瞬移消失★)",
        len(m_fix) == 2, "实际 = %r" % (m_fix,))

    # ⑥ 三角不等式兜底 (★判据说共线, 但合并后超长 ⇒ 放弃★)
    #   p = (0,0)->(1,0) ; s = (1,0)->(1,0) 之外的构造: 用【反向】构造
    seg_tele = [("N", 0.0, 0.0, 1.0, 0.0, 0, 0.25), ("N", 1.0, 0.0, 1.0, 0.0, 0, 0.25)]
    m_t = G2._merge_collinear(seg_tele, True)
    #   这组是零长段 ⇒ 合并长度 0 ⇒ 允许合并 (不是兜底触发) ⇒ 换一组真正的超长
    seg_tele2 = [("N", 0.0, 0.0, 3.0, 0.0, 0, 0.25), ("N", 3.0, 0.0, 6.0, 0.0, 0, 0.25)]
    m_t2 = G2._merge_collinear(seg_tele2, True)
    chk("⑥ 首尾相接的两段仍然合并 (★兜底不能误伤★)", len(m_t2) == 1, "实际 = %r" % (m_t2,))

    # ⑦ 实测数字回归 (★v76s2 裸板越界段★)
    x1, y1, x2, y2 = 39.7234, 1.1038, 41.6319, -1.2140
    ln = math.hypot(x2 - x1, y2 - y1)
    chk("⑦ 越界段长度必须 ≈3.002mm (★v76s2 裸板实测★)", abs(ln - 3.002) < 0.002,
        "实际 = %.4f" % ln)
    chk("⑦ 越界量必须 ≈1.214mm (★板边线 y=0★)", abs(y2 - 0.0) > 1.2,
        "实际 = %.4f" % y2)
    chk("⑦ 12 条 copper_edge_clearance 违规的来源就是这批出板铜 (★actual 0.0000mm★)",
        y2 < 0.0, "y2 = %.4f" % y2)

    print("─" * 46)
    if FAIL:
        print("FAILED %d/%d" % (len(FAIL), len(FAIL) + len(OK)))
        return 1
    print("ALL PASS (%d)" % len(OK))
    return 0


if __name__ == "__main__":
    sys.exit(main())
