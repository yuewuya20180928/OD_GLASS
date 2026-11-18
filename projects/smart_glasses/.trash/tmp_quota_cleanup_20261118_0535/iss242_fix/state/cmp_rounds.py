#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cmp_rounds.py —— ★两轮布线结果横向对比 (2026-11-05 05:35)

用法:
    python3 state/cmp_rounds.py <板A.kicad_pcb> [<板B.kicad_pcb> ...]
    python3 state/cmp_rounds.py --logs /tmp/gen_v21.log /tmp/gen_v22_8l.log

输出 (每行都是机器读出的事实, 不含判断):
  · 文件 mtime / 大小 / 走线段数 / 过孔数 / 铜皮填充块数 (filled_polygon)
  · 单边零铜对数 (差分对只布了一半) / Δ>0.13mm 的对数 + 明细
  · 若给 --logs: 从各轮日志里抽 [SUM] / [FAIL] / 用时

★为什么要有这个: 6层×预算6 vs 8层×预算3 是两个方向的对比 ⇒ 必须用**同一口径**读数,
  否则会出现"这轮数字更好"但其实是口径不同的情况。
"""
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(PROJ))   # ★工作区根 (工具在 <root>/tools/)
AUDIT = os.path.join(ROOT, "tools", "diff_pair_audit.py")


def pcb_facts(path):
    d = {"path": path, "exists": os.path.exists(path)}
    if not d["exists"]:
        return d
    st = os.stat(path)
    d["mtime"] = time.strftime("%m-%d %H:%M:%S", time.localtime(st.st_mtime))
    d["mb"] = st.st_size / 1e6
    seg = via = fill = 0
    with open(path, encoding="utf-8", errors="ignore") as f:
        for line in f:
            s = line.lstrip()
            if s.startswith("(segment"):
                seg += 1
            elif s.startswith("(via"):
                via += 1
            elif "filled_polygon" in s:
                fill += 1
    d["tracks"], d["vias"], d["fill"] = seg, via, fill
    return d


def audit_facts(path):
    if not (os.path.exists(path) and os.path.exists(AUDIT)):
        return {}
    try:
        out = subprocess.run([sys.executable, AUDIT, path], capture_output=True,
                             text=True, timeout=900).stdout
    except Exception as e:
        return {"error": str(e)}
    res = {}
    m = re.search(r"★ 单边零铜 \(差分对只布了一半\): (\d+) 对", out)
    res["half"] = int(m.group(1)) if m else None
    m = re.search(r"★ 双边都有铜但 Δ>0\.13mm: (\d+) 对", out)
    res["over"] = int(m.group(1)) if m else None
    res["over_detail"] = re.findall(r"^   (\S+) / (\S+)\s+Δ=([\d.]+)mm", out, re.M)
    # 表头之后的差分对明细 (P / N / L_P / L_N / Δ / maxseg / 判定)
    rows = []
    for line in out.splitlines():
        m = re.match(r"^(\S+)\s+(\S+)\s+([\d.-]+)\s+([\d.-]+)\s+([\d.-]+)\s+([\d.-]+)\s+(.*)$", line)
        if m and not line.startswith("P "):
            rows.append(m.groups())
    res["rows"] = rows
    return res


def log_facts(path):
    if not os.path.exists(path):
        return {}
    txt = open(path, encoding="utf-8", errors="ignore").read()
    d = {}
    m = re.search(r"\[SUM \].*", txt)
    if m:
        d["sum"] = m.group(0).strip()
    m = re.search(r"布不动的脚 (\d+) 个.*?预算耗尽\*\* (\d+) 个 / 真被堵死 (\d+) 个", txt)
    if m:
        d["fail"], d["budget"], d["blocked"] = int(m.group(1)), int(m.group(2)), int(m.group(3))
    m = re.search(r"用时 (\d+)s", txt)
    if m:
        d["used_s"] = int(m.group(1))
    m = re.search(r"EXIT=(\d+)", txt)
    if m:
        d["exit"] = int(m.group(1))
    m = re.search(r"判定: (.*)", txt)
    if m:
        d["verdict"] = m.group(1).strip()
    m = re.search(r"已原子替换正式板", txt)
    d["landed"] = bool(m)
    d["failnets"] = re.findall(r"^\s{9}(\S+)\s+(\d+) 脚 \(预算耗尽 (\d+)\)", txt, re.M)
    return d


def main():
    args = sys.argv[1:]
    logs = []
    if "--logs" in args:          # ★标志可以出现在任意位置
        logs = [a for a in args if a != "--logs" and not a.endswith(".kicad_pcb")]
        args = [a for a in args if a != "--logs" and a.endswith(".kicad_pcb")]
    for p in args:
        f = pcb_facts(p)
        print("=== 板: %s" % p)
        if not f.get("exists"):
            print("    ★不存在 (还没落盘?)")
            continue
        print("    mtime %s · %.2fMB · 走线 %d 段 · 过孔 %d · 铜皮填充块 %d"
              % (f["mtime"], f["mb"], f["tracks"], f["vias"], f["fill"]))
        a = audit_facts(p)
        if a:
            print("    差分对: 单边零铜 %s 对 / Δ>0.13mm %s 对"
                  % (a.get("half"), a.get("over")))
            for (pp, nn, dd) in a.get("over_detail", []):
                print("      ★Δ 超限: %s / %s  Δ=%smm" % (pp, nn, dd))
    for lp in logs:
        d = log_facts(lp)
        print("=== 日志: %s" % lp)
        if not d:
            print("    ★无内容/还没写")
            continue
        print("    落盘=%s · EXIT=%s · 判定=%s" % (d.get("landed"), d.get("exit"), d.get("verdict")))
        if "sum" in d:
            print("    %s" % d["sum"])
        if "fail" in d:
            print("    布不动的脚 %d (预算耗尽 %d / 真堵死 %d) · 用时 %ss"
                  % (d["fail"], d["budget"], d["blocked"], d.get("used_s")))
            for (n, c, b) in d.get("failnets", [])[:12]:
                print("      %s %s脚 (预算耗尽 %s)" % (n, c, b))


if __name__ == "__main__":
    main()
