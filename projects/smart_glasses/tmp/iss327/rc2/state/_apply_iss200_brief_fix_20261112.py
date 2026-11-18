#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-200 brief 订正: 把"本单产出"路径显式声明出来 —— 2026-11-12 01:5x 队列自动派活 job

★★**为什么要有这次落盘 (★实测, 不是推测★)** ★★:
· `python3 state/check_brief_commands.py` ⇒ ★**❌ ISS-200 引用了不存在的路径/命令: `MECH/_frag_update_iss200.py`** ★
  ⇒ ★**那道闸是对的**: brief 里引用的路径必须【实测存在】, 否则子 agent 会先花一轮找文件 ★
· ★**但本单这一条是【合法例外】**: `MECH/_frag_update_iss200.py` 是 ★**本单要 agent 新建的产出物**★
  (★范式抄 `MECH/_frag_update_iss092.py`, ★那个文件实测存在★) ⇒ ★**它【本来就】在交卷后才存在** ★
· ★**闸自己给了逃生门** (★`declared_outputs()`★): brief 里 ★**显式写"★新建★ <路径>"** ⇒ 闸就豁免它
  ⇒ ★**我上一版写的是"写 `MECH/_frag_update_iss200.py`" ⇒ "写"不在闸认的关键词表里 ⇒ 被报出来** ★
  ⇒ ★**正确做法 = 把动词换成闸认的"新建", 而不是去改闸、放宽豁免** (★闸的自测里第 ⑥⑦ 条就是在管这个边界★)

★★**落盘纪律 (与项目既有范式一致)** ★★: ① flock(state/.issue_log.lock) + 锁内重读
② ★**自证: yaml.safe_dump(整份 doc) 必须与原文件逐字节相同** (width=200)
③ 原子写 (tmp → fsync → os.replace → fsync(dir)) ④ ★**只改 ISS-200 一条的 task_brief 文本, 其余一字不动** ★
⑤ ★**改完必须重跑 `state/check_brief_commands.py` ⇒ rc=0 才算过** ★

★★**边界**: 板/网表/原理图/BOM 一个字节不动 · 不改闸脚本 · 不动任何子总工的分片
"""
from __future__ import annotations

import fcntl
import os
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
WIDTH = 200

REPL = [
    ("的范式写 `MECH/_frag_update_iss200.py`",
     "的范式 ★新建 `MECH/_frag_update_iss200.py`"),
    ("+ `MECH/_frag_update_iss200.py` (你自己的分片更新脚本)",
     "+ ★**新建** `MECH/_frag_update_iss200.py` (你自己的分片更新脚本)"),
]


def atomic_write(path: str, text: str) -> None:
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".issue_log.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
        dfd = os.open(d, os.O_RDONLY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def main() -> int:
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        raw = open(LOG, encoding="utf-8").read()
        doc = yaml.safe_load(raw)

        rt = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=WIDTH)
        if rt != raw:
            print("★自证失败: yaml 往返不一致 ⇒ 拒绝写")
            return 2

        it = None
        for x in doc["issues"]:
            if x.get("id") == "ISS-200":
                it = x
                break
        if it is None:
            print("★找不到 ISS-200 ⇒ 拒绝写")
            return 2

        tb = it.get("task_brief") or ""
        new = tb
        for old, rep in REPL:
            if old not in new:
                print("★替换目标不存在 (brief 已被别人改过?) ⇒ 拒绝写: %r" % old)
                return 2
            new = new.replace(old, rep)
        if new == tb:
            print("★brief 没变化 ⇒ 拒绝写")
            return 2
        it["task_brief"] = new

        out = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=WIDTH)
        atomic_write(LOG, out)
        print("✅ ISS-200 brief 已订正 (2 处 '写' → '★新建★' ⇒ 闸的 declared_outputs 豁免生效)")
        print("   issue_log.yaml %d B → %d B" % (len(raw), len(out)))
        return 0


if __name__ == "__main__":
    sys.exit(main())
