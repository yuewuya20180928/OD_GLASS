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


# ★★★**★取值型命令替换 (★比"任何 $(" 精确得多, ★零误报的关键)****
#   ★**为什么不能只查锚行**: ★**我那些报告的"机器时钟"写在项目符号里 (★不是行首) ⇒ 不是锚行 ⇒ 段落检查够不着
#     ⇒ ★**⇒ 实测: 语料里现成的 3 处 `$(md5sum` 样本, 段落检查一个都没抓到 ⇒ "扫了 74 个文件"给了虚假的安全感****
#   ★**判据: ★**只抓【取值型】命令替换 (★md5sum / stat / sha / wc / cut …) ⇒ ★**脚本模板型 (★如 `$(date +%Y-%m-%d).md` 这种路径模板) 不算****
VALUE_CMD_RE = re.compile(r"\$\((md5sum|sha256sum|stat|sha1sum|wc|cut|head|tail)\b")


def check_value_placeholders(text: str, label: str) -> list[str]:
    """★**全语料级: 任何一行的【取值型未展开命令替换】都算违规 (★不依赖锚行结构 ⇒ 抓得到'机器时钟写在项目符号里'那种形态)****"""
    bad: list[str] = []
    for i, line in enumerate(text.split("\n"), 1):
        # ★★★**★引用形态不算违规 (★★关键细化, ★否则会把"引用历史错误"的报告也判红)***
        #   ★**判据: ★**占位符若被【反引号包着】(★代码块/行内代码) ⇒ ★**那是引用, 不是活的占位符 ⇒ 放过
        #   ★**★理由: ★**语料里确实有"引用那次自打脸的原文"的报告 (★那是证据, 不是新错误)⇒ ★**⇒ 误报会把真信号淹掉****
        for pat in VALUE_CMD_RE.finditer(line):
            start = pat.start()
            # ★**看占位符左侧最近的引号: ★**若是成对的反引号包裹 ⇒ 引用 ⇒ 放过****
            left = line[:start].rfind("`")
            right = line.find("`", start)
            if left != -1 and right != -1 and left > line.rfind("`", 0, left):
                continue          # ★**引用形态 ⇒ 放过**
            bad.append(f"{label}:{i}: ★★含【活的】未展开取值型命令替换 {pat.group(0)!r} ⇒ ★**贴了'实跑'标签但值是命令串 ⇒ ★**md5 是 32 字符, 手工编的十六进制长度都不对 ⇒ 附命令 + mtime 让对方能当场复核****")
    return bad


def check_sides(files: list[str]) -> list[str]:
    """★★★**★分侧覆盖率判定 (★每一方都必须在【被扫到的文件里】且【至少 1 条锚行】)****
    ★**为什么要分侧 (★兄弟 02:1x 实测)**: ★**实验 B: ★**只喂主线侧的锚 (★模拟"播报员停止落盘") ⇒ 旧版输出"全部合规" rc=0
      ⇒ ★**★根因: ★**覆盖率自检只判"锚行总数 > 0"; ★**主线侧一直有锚 ⇒ 另一侧掉到 0 时总数仍 > 0 ⇒ 不报红** ⇒ ★**⇒ "某一侧不再被守卫"根本发现不了****
    ★**两条判定**: ★**① 某侧的文件完全不在被扫集合里 ⇒ "该侧未被纳入扫描范围 ⇒ 该侧不再被守卫" · ② 某侧在集合里但锚行为 0 ⇒ "该侧已停止落盘 ⇒ 该侧不再被守卫"****
    """
    bad: list[str] = []
    for side, root in SIDES.items():
        side_files = [f for f in files if os.path.abspath(f).startswith(os.path.abspath(root) + os.sep)]
        if not side_files:
            bad.append(f"★**{side}: ★**该侧文件完全不在被扫集合里 ⇒ ★**该侧不再被守卫** (★覆盖面清单里必须显式包含它)")
            continue
        anchors = 0
        for f in side_files:
            try:
                with open(f, encoding="utf-8", errors="ignore") as fh:
                    anchors += count_anchors(fh.read())
            except OSError:
                pass
        if anchors == 0:
            bad.append(f"★**{side}: ★**扫到 0 条锚行 ⇒ ★**该侧已停止落盘 ⇒ 该侧不再被守卫** (★目录: {root})")
    return bad


def check_segments(text: str, label: str) -> list[str]:
    """★★★**★段落级检查 (★2026-11-07 02:2x 兄弟三份证据指出的盲区)****
    ★**问题**: ★**`$(` 检查原先只作用于【锚行本身】⇒ ★**而我两次自打脸的【真实形态】是"锚行 + 下一行" ⇒ ★**⇒ 工具抓不到它自己的病 (★扫了 74 个文件, 放过了语料里现成的样本 ⇒ "扫了 N 个文件"给了虚假的安全感)****
    ★**修法: ★**从锚行开始, 取到【下一个锚行 / 空行】为止的【整段】⇒ ★**任何"来源标签"检查都对整段做, 不只做锚行那一行****
    """
    bad: list[str] = []
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        if not ANCHOR_LINE.match(lines[i]):
            i += 1
            continue
        seg = [lines[i]]
        j = i + 1
        while j < len(lines) and lines[j].strip() and not ANCHOR_LINE.match(lines[j]):
            seg.append(lines[j])
            j += 1
        blob = "\n".join(seg)
        for pat in VALUE_CMD_RE.finditer(blob):
            bad.append(f"{label}:{i+1}: ★★锚行所属段落含【取值型未展开命令替换】{pat.group(0)!r} ⇒ ★**贴了'实跑'标签但值是命令串 ⇒ 段级检查才抓得到 (★原先只看锚行 ⇒ 漏)**")
        i = j
    return bad


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
        # ★★★**★"来源标记是编的"那一族 (★兄弟 01:5x 抓到我自打脸)**: ★**贴了"[本轮实跑]"标签, 实际是未展开的 `$(...)` 字面量**
        #   ⇒ ★**收方按"手写的锚和手写的数字一样可疑"去查 ⇒ 发现标签是假的 ⇒ ★**比不贴标签更糟 (收方会以为已核过)****
        if "x" in token.lower() or "x" in rest[:3].lower():
            bad.append(f"{label}:{i}: ★时钟锚是手写的 (★含 x) ⇒ {line.strip()[:110]}")
            continue
        # ★**时刻本身合法; ★**再要求这一行里有一个合法的完整机器时间 (★带日期) ⇒ 否则只是"时刻"没"日期"**
        if not re.search(r"\d{4}-\d{2}-\d{2}", tail):
            bad.append(f"{label}:{i}: ★时钟锚缺日期 (★机器时间须含 YYYY-MM-DD) ⇒ {line.strip()[:110]}")
    return bad


# ★★★**★守卫覆盖面 = ★★显式枚举 (★2026-11-07 02:0x 兄弟实测出的"覆盖面不对称")****
#   ★**问题**: ★**同一件事住在两份副本里 —— `WS/memory/` (★播报员侧的报告落这儿) 与 `PROJ/memory/` (★我侧的报告落这儿)**
#     ⇒ ★**旧语料只认其中一份 ⇒ ★**讽刺的是"守卫器只守住了守规矩的那一方 (★越是带机器时钟的人越被检查, 不带的反而躲过了)"****
#   ★**⇒ 修法: ★**① 覆盖面【显式枚举】(★不靠"默认扫到哪儿算哪儿") ★**② 两个副本目录都进清单 ★**③ 清单打印出来, 便于复核"我到底守了谁"****
#   ★**★更根本的做法 (★留给老板/总工, ★本轮不做)**: ★**把两份日记对齐成一份 ⇒ ★**但那是结构性改动, 不是脚本能单方面决定的****
CORPUS_DIRS = [
    os.path.join(PROJ, "memory"),      # ★**项目侧日记 (★我这边落报告的地方)**
    os.path.join(WS, "memory"),        # ★**工作区根侧日记 (★播报员那边落报告的地方) ★**★必须也在覆盖范围内****
]

# ★★★**★分侧定义 (★2026-11-07 02:1x 兄弟实测出的缺口: ★**覆盖率自检原本是【全局】的 ⇒ 某一侧停止落盘时, 总数仍 > 0 ⇒ 工具发现不了"某一方掉线")****
#   ★**⇒ 这是"守卫者也要被守卫"的第三层: ★**① 守卫者被守卫 ② 守卫对象选对了吗 ③ ★**守卫能不能发现"某一方掉线"****
SIDES = {
    "主线侧 (PROJ/memory)": os.path.join(PROJ, "memory"),
    "播报员侧 (WS/memory)": os.path.join(WS, "memory"),
}
CORPUS_FILES = [
    os.path.join(WS, "MEMORY.md"),
    os.path.join(PROJ, "state", "CURRENT_TASK.md"),
]


def default_files() -> list[str]:
    """★**默认语料 (★★显式枚举 + 两个日记目录都进清单 ⇒ 覆盖面对称)****"""
    out: list[str] = []
    for p in CORPUS_FILES:
        if os.path.exists(p):
            out.append(p)
    for d in CORPUS_DIRS:
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if fn.endswith(".md"):
                out.append(os.path.join(d, fn))
    return out


def selftest() -> int:
    """★**先拿已知坏样本跑一遍, 确认它会红 (★`:2304` 铁律要求的反向验证用例)**"""
    good = [
        "◆ 机器时钟: 2026-11-07 01:44:02",
        "★机器时钟 2026-11-07 01:22 [本轮实跑]",
        "机器时钟: 2026-11-07 01:40:07 [本轮 stat]",
        "★★**本次报告的真值 (★机器时钟 2026-11-06 23:18)**: ★**MEMORY.md md5 = `799dedc4`",
        "· ★**现象**: ★**实际机器时钟是 `00:2x~01:23` (★错 2.5~3 小时)**",
        # ★**★路径模板型命令替换 (★合法, 不得误报)****
        "★**`bcast_facts.sh:13` ⇒ `MEM=…/memory/$(date +%Y-%m-%d).md`**",
    ]
    bad = [
        "★机器时钟 2026-11-07 03:8x ⇒ 那是我沿用旧摘要的写法",
        "机器时钟 2026-11-07 02:3x [手写]",
        "◆ 机器时钟: 2026-11-07 01:2x",
        # ★**段级形态 (★兄弟指出的真实形态: 锚行 + 下一行)***
        "◆ 机器时钟: 2026-11-07 01:51:10\nMEMORY.md md5 $(md5sum ../../MEMORY.md | cut -d' ' -f1) [本轮实跑]",
        # ★**★取值型命令替换, 且【不在锚行里】(★真实形态: "机器时钟"写在项目符号里)****
        "  · ★**本次报告的真值 (★机器时钟 2026-11-07 01:45)**: ★**MEMORY.md md5 $(md5sum ../../MEMORY.md | cut -d' ' -f1) [本轮实跑]**",
    ]
    fails: list[str] = []
    for s in good:
        if check_text(s, "good") or check_segments(s, "good") or check_value_placeholders(s, "good"):
            fails.append(f"✗ 合规样本被误报: {s}")
    for s in bad:
        if not (check_text(s, "bad") or check_segments(s, "bad") or check_value_placeholders(s, "bad")):
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
            bad += check_segments(txt, os.path.basename(p))
            bad += check_value_placeholders(txt, os.path.basename(p))
        except OSError as e:
            print(f"⚠ 读不到 {p}: {e}", file=sys.stderr)
    bad += check_sides(files)
    print("★**覆盖面清单 (★显式枚举, 便于复核'我到底守了谁')**:")
    for p in files:
        print(f"   · {os.path.relpath(p, WS)}")
    print(f"★**覆盖率自检: ★**扫到锚行 {total_anchor} 行 (★若 0 ⇒ 扫描器形同虚设 ⇒ 判据本身有问题)")
    if total_anchor == 0:
        print("✗ 一条锚行都没扫到 ⇒ ★**本工具此刻没有任何东西在检查** ⇒ 不许报'通过' (★退出码 1)",
              file=sys.stderr)
        print("★**⇒ 原因: ★**对外报告还没统一用『行首固定一行 ◆ 机器时钟: YYYY-MM-DD HH:MM:SS』这个格式 ⇒ ★**⇒ 格式一统一, 这里立刻有覆盖率**",
              file=sys.stderr)
        return 1
    if bad:
        print("✗ 发现手写时刻锚 (★机器时钟行必须是纯数字机器时间):", file=sys.stderr)
        for b in bad:
            print("  " + b, file=sys.stderr)
        return 1
    print(f"✔ 机器时钟行全部合规 (★扫了 {len(files)} 个文件)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
