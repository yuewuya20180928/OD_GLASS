#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_probe_grid_fidelity.py —— ★★【★板面走线【网格保真度】探针 (★瞬移段的检出器★)★★】★★

★★★**★为什么要有 (★2026-11-10 04:4x)★★★**
  ★**路由器只走【正交】或【45°】方向 (★8 邻域网格★)** ⇒ ⇒ 板面上任何
  ★**既不正交、也不是 45°** 的走线 ⇒ ★★**它不可能是 A* 走出来的 ⇒ 必然是"合并瞬移"的产物** ★★
  ★★**⇒ 这就是"共线合并 bug"的【独立检出器】(★不依赖路由器日志, ★只看板面★)** ★★
  ★★**⇒ 它可以直接当【板面质量闸】: 瞬移段 = 假铜 = 出板铜 + 断头 + 拆碎网** ★★

用法:
  bash state/pcbnew_py.sh state/_probe_grid_fidelity.py <板文件> [<板文件> ...]
  ⇒ 每个板打印: 总段数 / 正交段 / 45°段 / **★非网格段(瞬移嫌疑)★** / 最长嫌疑段
  ⇒ rc=0 (★本脚本只报告, 不做判定★)
"""
import sys
import math


def _is_gridish(dx, dy, tol=1e-3):
    """★正交 (|dx|=0 或 |dy|=0) 或 45° (|dx|=|dy|) ⇒ True★"""
    ax, ay = abs(dx), abs(dy)
    if ax < tol or ay < tol:
        return True
    if abs(ax - ay) < tol:
        return True
    return False


def _len_is_gridish(dx, dy, g=0.25, tol=1e-3):
    """★长度必须落在网格步长上 (★正交: k·g ; 45°: k·g·√2★)★"""
    L = math.hypot(dx, dy)
    if L < 1e-6:
        return True
    ax, ay = abs(dx), abs(dy)
    if ax < 1e-6 or ay < 1e-6:
        k = L / g
    else:
        k = L / (g * math.sqrt(2.0))
    return abs(k - round(k)) < 1e-3


def probe(path):
    txt = open(path, encoding="utf-8", errors="ignore").read().split("\n")
    cur = None
    segs = []
    for l in txt:
        if "(segment" in l:
            cur = {"pts": [], "net": None, "layer": None, "w": None}
            continue
        if cur is not None:
            import re
            m = re.search(r'\((?:start|end) ([-0-9.]+) ([-0-9.]+)\)', l)
            if m:
                cur["pts"].append((float(m.group(1)), float(m.group(2))))
            m = re.search(r'\(net (\d+)\)', l)
            if m:
                cur["net"] = m.group(1)
            m = re.search(r'\(layer "([^"]+)"\)', l)
            if m:
                cur["layer"] = m.group(1)
            m = re.search(r'\(width ([0-9.]+)\)', l)
            if m:
                cur["w"] = float(m.group(1))
            if l.strip() == ")":
                if len(cur["pts"]) == 2:
                    segs.append((cur["net"], cur["layer"], cur["w"], cur["pts"][0], cur["pts"][1]))
                cur = None
    n = len(segs)
    ortho = diag = bad = 0
    badl = []
    offboard = []
    dupmap = {}
    for (net, lay, w, a, b) in segs:
        dx, dy = b[0] - a[0], b[1] - a[1]
        # ★★**出板检测 (★硬失败信号★)**: ★端点落在 Edge.Cuts 包围盒之外★★
        if min(a[0], b[0]) < -0.06 or min(a[1], b[1]) < -0.06 \
                or max(a[0], b[0]) > 160.06 or max(a[1], b[1]) > 100.06:
            offboard.append((net, lay, a, b))
        # ★**重复段检测 (★瞬移 bug 的另一个指纹★)**
        _k = (net, tuple(sorted([a, b])))
        dupmap[_k] = dupmap.get(_k, 0) + 1
        if abs(dx) < 1e-6 or abs(dy) < 1e-6:
            ortho += 1
            ok = _len_is_gridish(dx, dy)
        elif abs(abs(dx) - abs(dy)) < 1e-3:
            diag += 1
            ok = _len_is_gridish(dx, dy)
        else:
            bad += 1
            ok = False
            badl.append((math.hypot(dx, dy), net, lay, a, b))
        if ok is False and (abs(dx) < 1e-6 or abs(dy) < 1e-6 or abs(abs(dx) - abs(dy)) < 1e-3):
            # 方向对但长度不在网格上 ⇒ 也是可疑 (★合并把两段接起来时长度会变★)
            bad += 1
            badl.append((math.hypot(dx, dy), net, lay, a, b))
    ndup = sum(v - 1 for v in dupmap.values() if v > 1)
    print("── %s" % path.split("/")[-1])
    print("   总段=%d  正交=%d  45°=%d  ★重复段=%d★  ★非网格段(参考)=%d (%.2f%%)★"
          % (n, ortho, diag, ndup, bad, (100.0 * bad / n) if n else 0.0))
    if offboard:
        print("   ★★**出板段 = %d (★硬失败: 必然是假铜★)**★★" % len(offboard))
        for (net, lay, a, b) in offboard[:4]:
            print("     ★ %-14s %-8s (%.3f,%.3f)->(%.3f,%.3f)"
                  % (net, lay, a[0], a[1], b[0], b[1]))
    if badl:
        badl.sort(reverse=True)
        for (L, net, lay, a, b) in badl[:2]:
            print("     参考 len=%.4f net=%s %s (%.3f,%.3f)->(%.3f,%.3f)"
                  % (L, net, lay, a[0], a[1], b[0], b[1]))
    return n, len(offboard)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not args:
        print(__doc__)
        return 1
    for p in args:
        try:
            probe(p)
        except Exception as e:
            print("── %s  ERR %s" % (p, e))
    return 0


if __name__ == "__main__":
    sys.exit(main())
