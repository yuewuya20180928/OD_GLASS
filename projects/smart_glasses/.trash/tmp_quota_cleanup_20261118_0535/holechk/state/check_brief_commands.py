#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_brief_commands.py —— ★★【派活前的"命令存在性"守卫】★★ (★2026-11-11 17:2x 新建★)

★★★**★为什么要有这道闸 (★今天我又犯了一次 MEMORY 里已记的铁律★)★★★:
  ★**MEMORY 里那条**: 「任务书里引用的【脚本路径/命令】必须在派活前实测存在 ⇒ 否则子 agent 会【先花一轮找文件】再干活, 预算白烧」
  ★**今天的实例 (★我又犯了★)**: ★**ISS-193 的 task_brief 里写了验收命令 `state/gen_pin_reality_gap.py` ⇒ ★**那个文件根本不存在** ★★
    ⇒ ★**真命令是 `python3 state/gen_kicad_sch.py --pin-gap` (★gap 生成器折在生成器里★)**
    ⇒ ★**⇒ 派出去之后 hw-lead 白花时间找文件 ⇒ ⇒ 所以光"人记住"不够 ⇒ 必须有机器闸** ★★★

★**判据**: ★**把 brief 文本里所有像"路径/命令"的片段抠出来 ⇒ 逐个实测存在 ⇒ 有一个不存在 ⇒ rc=1 并点名是哪个 ★**
  ★**不做的事**: ★**不判断命令【对不对】(★那要人验★) ⇒ 只判断【引用的文件在不在】(★客观可测★) ★**

用法:
  python3 state/check_brief_commands.py                     # 查 issue_log 里所有 open/fixing 单的 task_brief
  python3 state/check_brief_commands.py --brief-file <f>    # 查一个文本文件 (★派活前把 brief 存下来再查★)
  python3 state/check_brief_commands.py --text "..."         # 查一段文本
  python3 state/check_brief_commands.py --self-test         # 自测 (★含反向用例★)
"""
from __future__ import annotations

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.normpath(os.path.join(HERE, ".."))

# ★★**候选路径的识别口径** ★★
#   1) `state/xxx.py` / `HW/PCB/xxx.md` 这类【带目录的相对路径】⇒ 直接按 PROJ 拼
#   2) `xxx.py` / `xxx.sh` 这种【裸文件名】⇒ 在 state/ 与项目根各找一次
#   3) `HW/PCB/demo_mainboard.kicad_sch` 这种【真实存在的文件】⇒ 跳过 (它不是"待查的脚本")
_PATH_RE = re.compile(r"(?<![\w/.-])((?:state|HW|SW|MECH|REQ|HANDOFF|config|tools)/[\w./+-]+\.(?:py|sh|md|csv|json|yaml|txt|kicad_\w+|net|bom|xml))")
_BARE_RE = re.compile(r"(?<![\w/.-])([\w-]+\.(?:py|sh))(?=[\s`'\"),;:；。]|$)")
# ★★**命令行里常见、但不是文件的片段 (★免得误报★) ★★
_SKIP = {
    "state.py", "setup.py", "config.py", "main.py", "merge.py", "frag_write.py",
    "readme.py", "index.py",
}


_SKIP_DIRS = (".git", "__pycache__", "node_modules", "production", ".lastgood", ".venv", "venv")


def _exists(rel: str) -> bool:
    """★rel 存在吗 ⇒ ★【候选位置全试一遍】(★踩坑: 裸文件名散在 MECH/print/ 等子目录里★)"""
    p = os.path.join(PROJ, rel)
    if os.path.exists(p):
        return True
    base = os.path.basename(rel)
    # ★裸文件名 ⇒ 在项目内【递归找一遍】(★跳过重目录★) ⇒ 这才兜得住 MECH/print/xxx.py 这种★
    for root, dirs, files in os.walk(PROJ):
        dirs[:] = [d for d in dirs if d not in _SKIP_DIRS]
        if base in files:
            return True
        # ★别无限深走★
        if root.count(os.sep) - PROJ.count(os.sep) > 4:
            dirs[:] = []
    return False


def find_refs(text: str) -> list[str]:
    refs = set()
    for m in _PATH_RE.finditer(text):
        refs.add(m.group(1))
    for m in _BARE_RE.finditer(text):
        b = m.group(1)
        if b in _SKIP:
            continue
        refs.add(b)
    return sorted(refs)


def check_text(text: str, label: str) -> tuple[int, list[str]]:
    missing = []
    for r in find_refs(text):
        if not _exists(r):
            missing.append(r)
    if missing:
        print("❌ %s: 引用了不存在的路径/命令 (%d 个)" % (label, len(missing)))
        for r in missing:
            print("   · %s" % r)
    return (1 if missing else 0), missing


def self_test() -> int:
    fails = []
    good = "跑 `python3 state/check_sch_erc.py` 与 `python3 state/merge.py`, 产物写 HW/PCB/REVIEW_CHECKLIST_P2.md"
    bad = "跑 `python3 state/gen_pin_reality_gap.py` 重跑, 再 `bash state/nonexistent_thing.sh`"
    rc1, m1 = check_text(good, "good")
    rc2, m2 = check_text(bad, "bad")
    if rc1 != 0:
        fails.append("① 正常 brief 被误判 (缺 %s)" % m1)
    if rc2 != 1 or "state/gen_pin_reality_gap.py" not in m2:
        fails.append("② 坏 brief 没被抓到 (rc=%s, missing=%s)" % (rc2, m2))
    # ★反向用例: 把"存在性检查"改弱成"永远通过" ⇒ 必须被反向用例抓到 ⇒
    #   模拟: 若 find_refs 恒返空 ⇒ good/bad 都 rc=0 ⇒ ② 必然红 ⇒ 断言点在 ②
    if find_refs(bad) == []:
        fails.append("③ 反向用例失效: 坏 brief 一个都没抠出来")
    if fails:
        for f in fails:
            print("❌", f)
        print("SELFTEST FAILED")
        return 1
    print("ALL TESTS PASS (3 条: 正常brief不误报 / 坏brief被抓 / 反向用例)")
    return 0


def main() -> int:
    args = sys.argv[1:]
    if "--self-test" in args:
        return self_test()
    if "--brief-file" in args:
        p = args[args.index("--brief-file") + 1]
        text = open(p, encoding="utf-8").read()
        rc, _ = check_text(text, p)
        return rc
    if "--text" in args:
        t = args[args.index("--text") + 1]
        rc, _ = check_text(t, "--text")
        return rc
    # 默认: 查 issue_log 里所有待办单的 task_brief
    import yaml
    log = os.path.join(HERE, "issue_log.yaml")
    doc = yaml.safe_load(open(log, encoding="utf-8").read())
    bad = 0
    checked = 0
    for i in (doc.get("issues") or []):
        if i.get("status") not in ("open", "fixing"):
            continue
        tb = i.get("task_brief") or ""
        if not tb:
            continue
        checked += 1
        rc, miss = check_text(tb, i.get("id"))
        if rc:
            bad += 1
    print("── 查了 %d 条待办单的 task_brief, 有问题的 %d 条" % (checked, bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
