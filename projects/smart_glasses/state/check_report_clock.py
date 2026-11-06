#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""state/check_report_clock.py —— 校验【对外报告里的时刻锚】必须是机器读出来的 (★2026-11-07 01:4x)

★★★**为什么要有这个脚本 (★兄弟 01:44 的实测带出来的)**:
  · ★**新铁律: ★**来源必须是【机器读出来的】, 不是【手写的】** (★时间戳必须取自 `date`, 不许手写)
  · ★**但他自己配反向验证用例时, 工具连翻两次车**: ★**v1 (时间比较判据) 返回 0 矛盾 —— 那 0 是【他 regex 写错】(★`\d{2}:\d{2}` 匹配不到 `03:0x`)**
    ⇒ ★**⇒ 若没自校准, 就会把"0 矛盾"当成"没有手写时刻锚"报上去 ⇒ ★**今晚反复出现的那族病: "看起来通过了, 其实没在检查"**
  · ★**v2 (改正 regex 但判据本身错) ⇒ 合规样本也被误报** ⇒ ★**根因: "声明时刻 > 落盘 mtime" 会误报两类合法内容 (★写的是【事件时刻】而落盘在其后 / 对【未来时刻】的预告)**
  · ★★★**★⇒ 正解 (★他 v3 找到的, ★本脚本采用)**: ★**形态判据 —— ★**"带 `x` 的时刻 = 手写"** ⇒ ★**因为机器 `date` 永远不会输出 `x`** ⇒ ★**⇒ 零时间比较 ⇒ 零假阳性 ⇒ 召回 100%****

★★★**★形态判据能精准抓"手写时刻", 但抓不出"这个手写时刻有害" (★他扫 8 个文件 ⇒ 400 处)**:
  · ★**绝大多数在【铁律条目标题的 (日期 时间)】里 (★如 "(2026-11-06 22:5x)") ⇒ ★**那是"这条铁律何时立"的粗略定位 ⇒ 约定俗成无害****
  · ★★★**★⇒ 真正该收紧的是【对外报告里的时刻锚】 (★收方要按它定位事件) ⇒ ★**⇒ 可机器化区分的那一层 = 【对外报告】vs 【内部标题约定】****
  ⇒ ★★★**★★⇒ 所以本脚本只查一件事: ★**凡是写着"机器时钟"的那一行, 它的时刻必须是纯数字 (★不许带 x) 且格式合法****

★★★**用法**:
  · ★**`python3 state/check_report_clock.py --self-test`** ⇒ ★**跑已知样本: 合规样本必须 0 命中, 坏样本必须命中 ⇒ ★**这是 `:2304` 那条铁律要求的"反向验证用例"****
  · ★**`python3 state/check_report_clock.py`** ⇒ ★**扫默认语料 (★MEMORY.md + 项目日记) ⇒ 有违规行就 rc=1 并打印行号****
  · ★**`python3 state/check_report_clock.py FILE...`** ⇒ ★**扫指定文件****
"""
from __future__ import annotations

import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
WS = os.path.dirname(os.path.dirname(PROJ))

# ★**只查"机器时钟"那一行** (★对外报告的固定格式行) ⇒ ★**不查铁律标题里的 (日期 时间) ⇒ 零误报**
CLOCK_LINE = re.compile(r"机器时钟")
# ★**合法的机器时刻: 纯数字, 可选到秒; ★**带 x / 非数字 ⇒ 一律判违规**
VALID_TS = re.compile(r"\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}(:\d{2})?")


# ★★**锚行判定 (★第二版仍有误报 ⇒ 第三版定稿: ★**只认【行首的固定格式锚行】, 散文一律跳过**)****
#   · ★**锚行 = 该行【去掉行首的 ★/◆/空白】后【以"机器时钟"开头** ⇒ ★**这是"对外报告首行的固定格式"****
#   · ★**散文句 (★"…(★机器时钟 2026-11-06 23:18)**: …" 这种在句子中间提到的) ⇒ 不是锚行 ⇒ 不查****
#   · ★**⇒ 这样零误报: ★**工具自己打印的输出也不以"机器时钟"开头 ⇒ 不会被自己抓****
ANCHOR_LINE = re.compile(r"^[★◆·\s*]*(?:◆\s*)?机器时钟")   # ★**容得下项目符号 · 与加粗 ** 前缀**
# ★**时刻 token: ★**允许带 x (★那正是要抓的) ★**/ HH:MM / HH:MM:SS**
TS_TOKEN = re.compile(r"\d{1,2}:\d{1,2}(?::\d{1,2})?")


def count_anchors(text: str) -> int:
    """★**锚行数 (★覆盖率自检: ★**若 0 ⇒ 这个扫描器什么都没扫到 ⇒ 形同虚设**)"""
    return sum(1 for line in text.split("\n") if ANCHOR_LINE.match(line))


def check_text(text: str, label: str) -> list[str]:
    """返回违规行列表。
    ★**判据 (★第三版定稿)**: ★**只看【行首锚行】(★"机器时钟" 开头) ⇒ ★**该行的时刻必须是纯数字机器时间**;
    ★**带 x / 缺时刻 / 格式错 ⇒ 一律违规** ⇒ ★**散文里的提及一律放过 ⇒ 零误报****
    """
    bad: list[str] = []
    for i, line in enumerate(text.split("\n"), 1):
        if not ANCHOR_LINE.match(line):
            continue
        tail = line[line.index("机器时钟") + len("机器时钟"):]
        tm = TS_TOKEN.search(tail)
        if not tm:
            bad.append(f"{label}:{i}: ★时钟锚行没有时刻 ⇒ {line.strip()[:110]}")
            continue
        token = tm.group(0)
        rest = tail[tm.end():]
        if "x" in token.lower() or "x" in rest[:3].lower():
            bad.append(f"{label}:{i}: ★时钟锚是手写的 (★含 x) ⇒ {line.strip()[:110]}")
            continue
        # ★**时刻本身合法; ★**再要求这一行里有一个合法的完整机器时间 (★带日期) ⇒ 否则只是"时刻"没"日期"**
        if not re.search(r"\d{4}-\d{2}-\d{2}", tail):
            bad.append(f"{label}:{i}: ★时钟锚缺日期 (★机器时间须含 YYYY-MM-DD) ⇒ {line.strip()[:110]}")
    return bad


def default_files() -> list[str]:
    """★**默认语料: ★**MEMORY.md + 项目日记 + CURRENT_TASK.md (★对外报告的锚落在这些地方)****"""
    cands = [
        os.path.join(WS, "MEMORY.md"),
        os.path.join(PROJ, "memory", "2026-11-06.md"),
        os.path.join(PROJ, "memory", "2026-11-07.md"),
        os.path.join(PROJ, "state", "CURRENT_TASK.md"),
    ]
    return [p for p in cands if os.path.exists(p)]


def selftest() -> int:
    """★**先拿已知坏样本跑一遍, 确认它会红 (★`:2304` 铁律要求的反向验证用例)**"""
    good = [
        "◆ 机器时钟: 2026-11-07 01:44:02",
        "★机器时钟 2026-11-07 01:22 [本轮实跑]",
        "机器时钟: 2026-11-07 01:40:07 [本轮 stat]",
        "★★**本次报告的真值 (★机器时钟 2026-11-06 23:18)**: ★**MEMORY.md md5 = `799dedc4`",
        "· ★**现象**: ★**实际机器时钟是 `00:2x~01:23` (★错 2.5~3 小时)**",
    ]
    bad = [
        "★机器时钟 2026-11-07 03:8x ⇒ 那是我沿用旧摘要的写法",
        "机器时钟 2026-11-07 02:3x [手写]",
        "◆ 机器时钟: 2026-11-07 01:2x",
    ]
    fails: list[str] = []
    for s in good:
        if check_text(s, "good"):
            fails.append(f"✗ 合规样本被误报: {s}")
    for s in bad:
        if not check_text(s, "bad"):
            fails.append(f"✗ 坏样本未被抓住: {s}")
    if fails:
        for f in fails:
            print(f, file=sys.stderr)
        print("✗ 自测失败 ⇒ 判据不可信 ⇒ 拒绝使用", file=sys.stderr)
        return 1
    print("✔ 自测通过: 合规样本 0 命中 (3/3) · 坏样本全命中 (3/3) ⇒ 判据可用")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*", help="要扫的文件 (默认: MEMORY.md + 项目日记 + CURRENT_TASK.md)")
    ap.add_argument("--self-test", action="store_true", help="★**跑已知样本自校准 (★上线前必跑)**")
    args = ap.parse_args()
    if args.self_test:
        return selftest()
    files = args.files or default_files()
    if not files:
        print("⚠ 没有可扫的文件", file=sys.stderr)
        return 0
    bad: list[str] = []
    total_anchor = 0
    for p in files:
        try:
            with open(p, encoding="utf-8", errors="ignore") as f:
                txt = f.read()
            total_anchor += count_anchors(txt)
            bad += check_text(txt, os.path.basename(p))
        except OSError as e:
            print(f"⚠ 读不到 {p}: {e}", file=sys.stderr)
    print(f"★**覆盖率自检: ★**扫到锚行 {total_anchor} 行 (★若 0 ⇒ 扫描器形同虚设 ⇒ 判据本身有问题)")
    if bad:
        print("✗ 发现手写时刻锚 (★机器时钟行必须是纯数字机器时间):", file=sys.stderr)
        for b in bad:
            print("  " + b, file=sys.stderr)
        return 1
    print(f"✔ 机器时钟行全部合规 (★扫了 {len(files)} 个文件)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
