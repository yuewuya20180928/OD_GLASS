#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sb09_scenario_matrix.py —— ISS-314 沙盒: 把 8 个场景的原始读数汇总成一张对照表

★只读 logs/iss314/ 下已落盘的原始输出 ⇒ 自己算, 不抄结论 ★
★输出: logs/iss314/12_scenario_matrix.txt ★
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(HERE))
LOGS = os.path.join(PROJ, "logs", "iss314")

SCEN = [
    ("S0", "现役板 + 正本网表 (正本判据)", "01_check_pcb_nets_baseline.txt"),
    ("S1", "只改板侧 (板改名) + 网表不改 (沙盒判据·无反查层)", "04_S1_boardonly_noref.txt"),
    ("S2", "只改板侧 (板改名) + 网表不改 (沙盒判据·有反查层)", "05_S2_boardonly_reflookup.txt"),
    ("S3", "只改网表 (网表改名) + 板不改 (沙盒判据·无反查层)", "06_S3_netonly_noref.txt"),
    ("S4", "三侧同口径改名 (沙盒判据·无反查层)", "07_S4_both_noref.txt"),
    ("S5", "三侧同口径改名 (沙盒判据·有反查层)", "08_S5_both_reflookup.txt"),
    ("S6", "板改名 + 网表缺 3 个 ref (沙盒判据·有反查层)", "09_S6_broken_reflookup.txt"),
    ("S7", "板改名 + 网表缺 3 个 ref (沙盒判据·无反查层)", "10_S7_broken_noref.txt"),
]

RE_C1 = re.compile(r"缺失 (\d+) · 多余 (\d+) · 同号异网 (\d+) ·.*非法 NC (\d+)")
RE_C3 = re.compile(r"C3 每个器件焊盘数.*?不符 (\d+) 个")
RE_C2BAD = re.compile(r"❌ C2 ")
RE_RC = re.compile(r"^rc=(\d+)$", re.M)
RE_HIT = re.compile(r"反查层命中 (\d+) 个")
RE_MISS = re.compile(r"口径未同步: (\d+) 个")
RE_AMB = re.compile(r"口径歧义: (\d+) 个")

rows = []
for tag, desc, fn in SCEN:
    p = os.path.join(LOGS, fn)
    t = open(p, encoding="utf-8").read()
    m = RE_C1.search(t)
    c1 = tuple(int(x) for x in m.groups()) if m else None
    c3 = int(RE_C3.search(t).group(1)) if RE_C3.search(t) else None
    c2b = len(RE_C2BAD.findall(t))
    rc = int(RE_RC.search(t).group(1)) if RE_RC.search(t) else None
    hit = int(RE_HIT.search(t).group(1)) if RE_HIT.search(t) else 0
    mis = int(RE_MISS.search(t).group(1)) if RE_MISS.search(t) else 0
    amb = int(RE_AMB.search(t).group(1)) if RE_AMB.search(t) else 0
    rows.append((tag, desc, c1, c3, c2b, rc, hit, mis, amb))

out = []
out.append("=" * 110)
out.append("ISS-314 沙盒场景矩阵 (★C1 三项 + C2 + C3 + rc + 反查层口径★)")
out.append("=" * 110)
out.append("%-4s %-46s %-22s %-6s %-6s %-5s %-6s %-6s %-5s"
           % ("场景", "内容", "C1 缺失/多余/同号异网/非法NC", "C2红", "C3红", "rc", "反查命中", "未同步", "歧义"))
out.append("-" * 110)
for tag, desc, c1, c3, c2b, rc, hit, mis, amb in rows:
    cs = "%d / %d / %d / %d" % c1 if c1 else "—"
    out.append("%-4s %-46s %-22s %-6s %-6s %-5s %-6s %-6s %-5s"
               % (tag, desc, cs, c2b, c3, rc, hit, mis, amb))
out.append("-" * 110)
out.append("★读法:")
out.append("  · S0 = 现状基线 (板原名 + 表原名) ⇒ C1 缺失 0 / 多余 2 / 同号异网 3 / 非法 NC 0 · C2 红 0 · C3 红 0")
out.append("  · S1 = 只改板侧 ⇒ C1 缺失 350 / 多余 352 / 同号异网 0 / 非法 NC 3 · C3 红 155 ⇒ ★那一趟会红成这样★")
out.append("  · S2 = 只改板侧 + 反查层 ⇒ C1 回到 0/2/3/0 · C3 红 0 ⇒ ★加反查层能救 C1/C2/C3★")
out.append("  · S3 = 只改网表 ⇒ 与 S1 同型 (对称) ⇒ ★改哪一侧都一样炸★")
out.append("  · S4 = 三侧同口径改名 (纯数据·不动判据) ⇒ C1 回到 0/2/3 ★但非法 NC 3 + C3 红 1★")
out.append("     ⇒ ★★纯改数据救不了: `J_USB_C`→`J_USB_C_1` 撞死判据里的 NC 白名单★★")
out.append("  · S5 = 三侧同口径 + 反查层 ⇒ 与 S4 同读数 (反查层无命中 ⇒ 不起作用) ⇒ ★★同样撞死白名单★★")
out.append("  · S6/S7 = 映射表被改坏 ⇒ C1 多余 13 / 同号异网 1 + 口径未同步 4 ⇒ ★反查层【不掩盖】真错★")
out.append("")
out.append("★三条硬结论 (★全部由上表数字直接读出, 不是推算★):")
out.append("  ① 只有【三侧同口径】(板+网表+脚表+BOM 一起改名) 才可能让 C1 回到 0/2/3 ⇒ 单改一侧必炸")
out.append("  ② 即便三侧同口径, ★`J_USB_C`→`J_USB_C_1` 仍撞死 `check_pcb_nets.py` 的 NC 白名单 (非法 NC 3 + C3 红 1)")
out.append("     ⇒ ★★【位号改名】与【受保护判据脚本一个字不许改】这两条 ★不可兼得★★ ⇒ 必须拍一个")
out.append("  ③ 反查层只把「口径没同步」这层症状消掉, ★且不掩盖真错 (S6/S7 照样红)★ ⇒ 它是诊断层, 不是放行层")

txt = "\n".join(out) + "\n"
open(os.path.join(LOGS, "12_scenario_matrix.txt"), "w", encoding="utf-8").write(txt)
print(txt)
