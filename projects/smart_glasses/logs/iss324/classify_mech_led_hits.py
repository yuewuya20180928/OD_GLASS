#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-324 · mech-lead · MECH 域 `D_LED_G` 命中分类器 (READ-ONLY)

★为什么要有这个★: 上一趟把它笼统写成「结构侧 [0数据]」是不准确的 ——
  `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` 确实登记了 `D_LED_G` 首选窗口
  ⇒ 【不是 0数据】, 是【有登记, 但要分清哪条适用哪块板】。
  本脚本把 MECH 域每一条 `D_LED_G` 命中按【性质】+【帧归属】分桶, 逐条可查。

分桶 (按优先级, 一行只进一个主桶):
  A 真位置规定   —— 该行本身给出/约束 `D_LED_G` 的落位坐标或落位条件
  B 引述/转述    —— 该行只是引述作业包 / 另一份文档 / 另一个 issue 的原话
  C 实测读数     —— 该行报的是板读出来的坐标 / 网长 / 器件值
  D 口径结论     —— 该行是「有没有规定 / 归谁拍 / [0数据]」这类结论句
  E 闸脚本代码   —— 该行在 .py 里 (判据代码或代码注释)

帧归属 (独立统计, 可与主桶并存):
  F30A   —— 该行带 F30A / 60×30 / 套A 帧标
  B160   —— 该行带 B160x100 / 160×100 / 台架板 帧标
  NONE   —— 该行没有帧标

用法: python3 logs/iss324/classify_mech_led_hits.py
"""
import os
import re
import sys

ROOT = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
LOG = ROOT + "/logs/iss324/04a_grep_mech_led.log"

PRIORITY = ["A", "B", "C", "D", "E"]

F30A_RE = re.compile(r"F30A|60\s*[×xX*]\s*30|60×30|套\s*A|legacy_", re.I)
B160_RE = re.compile(r"B160x100|160\s*[×xX*]\s*100|160×100|台架板|现役", re.I)

# 主桶判定规则 (先命中先算)
RULES = [
    ("E", lambda ln, fp: fp.endswith(".py")),
    ("A", lambda ln, fp: bool(re.search(
        r"(首选窗口|落位窗口|落位带|可放行带|整高自由带|最近落位|窗口\s*['\"]?led_window|"
        r"covers\s*:|宜与\s*`?R_LED_G|落位空间|候选位置的可放行|LED_G\s*窗口)", ln))),
    ("B", lambda ln, fp: bool(re.search(
        r"(S8 卡点原文|作业包|引述|转述|ISS-267 文件自己|自引|来源\s*[:：]|"
        r"见\s*`|详见|参见|出处|锚点|台账)", ln))),
    ("C", lambda ln, fp: bool(re.search(
        r"(\d+\.\d{3,}|\d+\.\d+\s*mm|焊盘|封装原点|铜箔|原点|net\s|网长|走线|"
        r"pad\d|\bat\s*\(|\(实测\)|\[实测\])", ln))),
    ("D", lambda ln, fp: bool(re.search(
        r"(\[0数据\]|0数据|没有|不存在|归谁|不代拍|不拍|⇒.*没有|一律)", ln))),
]


def main():
    with open(LOG, encoding="utf-8") as fh:
        lines = fh.read().split("\n")

    rows = []
    for i, raw in enumerate(lines, 1):
        ln = raw.strip()
        if not ln.startswith("MECH/"):
            continue
        m = re.match(r"^(MECH/\S+?):(\d+):(.*)$", ln)
        if not m:
            continue
        fp, lineno, body = m.group(1), int(m.group(2)), m.group(3)
        bucket = None
        for b, fn in RULES:
            if fn(body, fp):
                bucket = b
                break
        if bucket is None:
            bucket = "D"
        frame = "NONE"
        if F30A_RE.search(body):
            frame = "F30A"
        elif B160_RE.search(body):
            frame = "B160"
        rows.append((i, fp, lineno, bucket, frame, body))

    print("=" * 110)
    print("ISS-324 · MECH 域 `D_LED_G` / `D_LED_R` / `D_LED_B` 命中分类 (★实读 logs/iss324/04a_grep_mech_led.log★)")
    print("=" * 110)
    print("总命中行数 (以 `MECH/` 开头的 grep 结果行) = %d" % len(rows))

    print("\n[1] 按【性质】主桶统计")
    cnt = {b: 0 for b in PRIORITY}
    for r in rows:
        cnt[r[3]] += 1
    NAMES = {
        "A": "A 真位置规定 (给出/约束落位坐标或条件)",
        "B": "B 引述/转述 (引作业包或别的文档原话)",
        "C": "C 实测读数 (板读坐标/网长/器件值)",
        "D": "D 口径结论 (有没有规定/归谁拍/[0数据])",
        "E": "E 闸脚本代码 (.py 里的判据代码或注释)",
    }
    for b in PRIORITY:
        print("  %-3s %-56s %4d 行  (%5.1f%%)" % (b, NAMES[b], cnt[b], cnt[b] * 100.0 / max(len(rows), 1)))

    print("\n[2] 按【帧归属】统计 (独立于主桶)")
    fcnt = {}
    for r in rows:
        fcnt[r[4]] = fcnt.get(r[4], 0) + 1
    for k in ("F30A", "B160", "NONE"):
        print("  %-5s %4d 行" % (k, fcnt.get(k, 0)))
    print("  ⇒ ★F30A 帧的命中 = 只对 60×30 套A 产品板有效, 不可当现役 B160x100 台架板坐标用★")
    print("  ⇒ ★NONE (无帧标) 的命中 = 【必须逐条判适用性】, 不许默认套到任一块板★")

    print("\n[3] A 类 (真位置规定) 逐条 (★这是本单要交给 hw-lead 的部分★)")
    for r in rows:
        if r[3] != "A":
            continue
        print("  %s:%d  帧=%-5s  %s" % (r[1], r[2], r[4], r[5][:150]))

    print("\n[4] 按文件 × 主桶 交叉表")
    files = {}
    for r in rows:
        files.setdefault(r[1], {}).setdefault(r[3], 0)
        files[r[1]][r[3]] += 1
    print("  %-46s %5s %5s %5s %5s %5s  %s" % ("文件", "A", "B", "C", "D", "E", "合计"))
    for fp in sorted(files, key=lambda f: -sum(files[f].values())):
        c = files[fp]
        tot = sum(c.values())
        print("  %-46s %5d %5d %5d %5d %5d  %5d" % (fp, c.get("A", 0), c.get("B", 0), c.get("C", 0),
                                                    c.get("D", 0), c.get("E", 0), tot))
    print("  %-46s %5d %5d %5d %5d %5d  %5d" % ("合计", cnt["A"], cnt["B"], cnt["C"], cnt["D"], cnt["E"], len(rows)))

    print("\n[END] 分类完 · 只读")
    return 0


if __name__ == "__main__":
    sys.exit(main())
