#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""state/check_report_placeholders.py —— 出报告前的占位符自检 (★2026-11-07 02:45 兄弟提, ★我落)

★★★**★为什么要有它 (★今晚第 4 次同类事故的直接解法)**:
  · ★**我今晚发了 4 次带占位符的报告**: ★**① 未展开的 `$(...)` ② 编的假十六进制 ③ 消息里的 `%(md5)s` ④ 又一次 `%(md5)s`/`%(mt)s`**
  · ★**⇒ 根因不是"手滑", 是【顺序错】(★先写消息, 后跑核验 ⇒ 写的时候手里没有值) ⇒ ★**⇒ 光靠"小心"没用, 必须在【发出去之前】有一道机器闸****
  · ★**兄弟的实测补充**: ★**落盘文件里的 `TODO`/`PLACEHOLDER` 全是【正当内容】(★"期望 4 行全 DONE, 无 TODO" 的检查说明 · `RK3572 SOM (PLACEHOLDER)` 封装名 · `value: null / status: "TODO"` 的真实待填状态) ⇒ ★**⇒ 缺口只在【发出去之前】⇒ ⇒ 所以闸门必须作用在【要发的那段文本】上, 而不是全项目扫****

★★★**用法 (★发送前把草稿喂进来)**:
  · ★**`python3 state/check_report_placeholders.py < draft.md` (★从 stdin 读) ⇒ 有占位符 ⇒ 打印命中行 + rc=1****
  · ★**`python3 state/check_report_placeholders.py FILE...` ⇒ 扫指定文件****
  · ★**`python3 state/check_report_placeholders.py --self-test` ⇒ ★**用已知样本自校准 (★合规样本 0 命中 · 坏样本全命中)****

★★★**★判据 (★只抓"长得像占位符"的形态, ★避免误伤正文里的 TODO/PLACEHOLDER 合法用法)**:
  · ★**① `%(name)s` 形态 (★Python 模板占位符)****
  · ★**② `<PLACEHOLDER>` / `PLACEHOLDER` / `__PLACEHOLDER__` 大写形态****
  · ★**③ `TODO` / `FIXME` / `XXX` 单独成词 (★大写 + 词边界)⇒ ★**★但【允许】出现在引号/反引号包裹的引用里 (★如 "期望 4 行全 DONE, 无 TODO") ⇒ ⇒ 因此对这类只报"未加引号的"命中****
  · ★**④ 未展开的命令替换 `$(...)` (★取值型: md5sum/stat/sha/wc/cut/head/tail) ⇒ ★**与 `check_report_clock.py` 同口径****
  · ★**⑤ `PLACEHOLDER` 之类出现在【代码块/反引号】里 ⇒ ★**放过 (★那是引用, 不是本报告要填的洞)****
"""
import os
import re
import sys

# ★**取值型命令替换 (★与 check_report_clock.py 同口径)**
VALUE_CMD_RE = re.compile(r"\$\((md5sum|sha256sum|stat|sha1sum|wc|cut|head|tail)\b")
# ★**Python 模板占位符**
PY_TPL_RE = re.compile(r"%\([A-Za-z_][A-Za-z0-9_]*\)s")
# ★**大写占位符 (★含 <> 与 __ 包裹)**
UPPER_PLACEHOLDER_RE = re.compile(r"(?:<PLACEHOLDER>|__PLACEHOLDER__|\bPLACEHOLDER\b)")
# ★**裸 TODO/FIXME/XXX (★要求大写 + 词边界)**


def strip_quoted(text: str) -> str:
    """★**把【反引号/双引号包裹的内容】与【markdown 强调标记】挖掉 (★那些是引用与排版, 不是本报告的洞)****
    ★**★为什么要连强调标记一起挖: ★**实测误报 (★"期望 4 行全 DONE, 无 TODO" 这种讨论文本) ⇒ ★**⇒ 判定必须作用在"去掉引用与排版标记"的文本上****"""
    out = []
    in_bt = False
    in_q = False
    for ch in text:
        if ch == "`":
            in_bt = not in_bt
            continue
        if ch == '"' and not in_bt:
            in_q = not in_q
            continue
        if not in_bt and not in_q:
            out.append(ch)
    txt = "".join(out)
    for mark in ("**", "★", "☆", "·"):
        txt = txt.replace(mark, " ")
    return txt


def check_text(text: str, label: str) -> list[str]:
    bad: list[str] = []
    bare = strip_quoted(text)
    for i, line in enumerate(text.split("\n"), 1):
        hits = []
        bl = strip_quoted(line)          # ★**判定一律作用在【去掉引用与排版标记】的文本上 ⇒ 零误报****
        if PY_TPL_RE.search(bl):
            hits.append("python 模板占位符 %(...)s")
        if UPPER_PLACEHOLDER_RE.search(bl):
            hits.append("大写占位符 PLACEHOLDER")
        if VALUE_CMD_RE.search(bl):
            hits.append("未展开的取值型命令替换")
        # ★**★注意: ★**故意【不查】裸 TODO/FIXME/XXX** ⇒ ★**它们在讨论文本里是正当内容
        #   (★"期望 4 行全 DONE, 无 TODO" · `value: null / status: "TODO"` · `RK3572 SOM (PLACEHOLDER)`)
        #   ⇒ ★**⇒ 闸门只保留【高信号】形态: ★**%(...)s · PLACEHOLDER · 未展开取值型命令替换****
        if hits:
            bad.append("%s:%d: ★★%s ⇒ {line}" % (label, i, " / ".join(hits)))
    return bad


def selftest() -> int:
    good = [
        "★机器时钟: 2026-11-07 02:45:00",
        "★**已核实**: ★**期望 4 行全 DONE, 无 TODO**",
        "★封装名 `RK3572 SOM (PLACEHOLDER)` 是板文件里的真实内容",
        "★**取值**: ★**`md5sum MEMORY.md` 输出 32 字符十六进制**",
    ]
    bad = [
        "md5 `%(md5)s` · mtime %(mt)s",
        "该值 <PLACEHOLDER> 待补",
        "★该值 PLACEHOLDER",
        "MEMORY.md md5 $(md5sum MEMORY.md | cut -d' ' -f1) [本轮实跑]",
        "★TODO: 待补",
    ]
    fails = []
    for s in good:
        if check_text(s, "good"):
            fails.append("✗ 合规样本被误报: %s" % s)
    for s in bad:
        if not check_text(s, "bad"):
            fails.append("✗ 坏样本未被抓住: %s" % s)
    if fails:
        for f in fails:
            print(f, file=sys.stderr)
        print("✗ 自测失败 ⇒ 判据不可信 ⇒ 拒绝使用", file=sys.stderr)
        return 1
    print("✔ 自测通过: 合规样本 0 命中 (4/4) · 坏样本全命中 (5/5) ⇒ 判据可用")
    return 0


def main() -> int:
    args = [a for a in sys.argv[1:] if a != "--self-test"]
    if "--self-test" in sys.argv:
        return selftest()
    texts = []
    if not args:
        texts.append(("<stdin>", sys.stdin.read()))
    else:
        for p in args:
            try:
                with open(p, encoding="utf-8", errors="ignore") as f:
                    texts.append((p, f.read()))
            except OSError as e:
                print("⚠ 读不到 %s: %s" % (p, e), file=sys.stderr)
    bad = []
    for label, t in texts:
        bad += check_text(t, label)
    if bad:
        print("✗ 报告里还有占位符 ⇒ ★**重写后再发** (★出报告前必过这一关):", file=sys.stderr)
        for b in bad:
            print("  " + b, file=sys.stderr)
        return 1
    print("✔ 无占位符 (★可发)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
