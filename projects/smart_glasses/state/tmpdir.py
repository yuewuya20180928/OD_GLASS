#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tmpdir.py —— ★**闸门临时目录统一入口** (2026-11-23 04:5x · ISS-348)

★**为什么必须有它 (★实测踩过·别删★)**:
  `/tmp` 是带 **userquota** 的 tmpfs (7.5G) ⇒ ★**用户配额被打满时, 连 1 MB 写都失败 (EDQUOT)** ★
  ⇒ ★**后果不是「闸红」, 是「闸崩」**: 闸脚本把中间产物写 `/tmp` ⇒ 写失败 ⇒
    ★**KiCad 导出报 `Disk quota exceeded` ⇒ 闸拿到 rc=2 ⇒ 被误读成「原理图坏了」** ★
  ⇒ ★**2026-11-23 04:4x 实测**: `/tmp` 配额打满时 `check_sch_pinfull.py` rc=2 (报网表导出失败)
    而 `TMPDIR=$PWD/tmp` 下同一条命令 **rc=0 全绿** ⇒ ★**是环境问题, 不是图纸问题** ★
  ⇒ ★**判据方向不许改** (★那是闸的地界★) ⇒ ★**只能把「闸往哪写临时文件」这件事修对** ★

★**本模块做的事 (★只做这一件★)**:
  给闸脚本一个**项目盘**的临时目录 ⇒ ★**优先用环境变量 `TMPDIR` (若它指向可写的项目盘)★**,
  否则用 `<项目盘>/tmp/gate_tmp/` ⇒ ★**绝不落 `/tmp`** ★

★**为什么不是简单地 `TMPDIR=/tmp` 默认值**:
  ★`tempfile` 模块**认 `TMPDIR` 环境变量** ⇒ 但 `TMPDIR` 默认指向 `/tmp` ⇒
  ★**配额一打满 ⇒ 整个闸链全线假红** ⇒ ★**必须给一个"一定可写"的目录** ★

用法:
    from tmpdir import gate_tmpdir      # 在 state/ 下的脚本里: sys.path 处理见各脚本
    d = gate_tmpdir()                    # ⇒ 返回一个一定可写的目录 (会自动 mkdir)
"""
from __future__ import annotations

import os
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)


def _usable(d: str) -> bool:
    """★这个目录现在真能写吗 (★不只看存在·要真写一下★)"""
    if not d or not os.path.isdir(d):
        return False
    try:
        fd, p = tempfile.mkstemp(prefix="_wtest_", dir=d)
        os.close(fd)
        os.unlink(p)
        return True
    except Exception:  # noqa: BLE001
        return False


def gate_tmpdir() -> str:
    """★返回一个【一定可写】的临时目录 (★**优先项目盘**·绝不主动落 /tmp★)"""
    # ① ★**项目盘第一** (★本仓惯例: $PWD/tmp/★ · ★项目盘 468G 常年有 385G 空★ ⇒ 配额打不到★)
    cands = [os.path.join(PROJ, "tmp", "gate_tmp")]
    # ② 环境变量 TMPDIR (★★但【排除 /tmp 本身】★ ⇒ ★本机 TMPDIR 预设就是 /tmp,
    #    所以「先看 env」会把闸又带回配额打爆的 /tmp ⇒ ★**必须项目盘优先**★)
    env = os.environ.get("TMPDIR")
    if env and os.path.abspath(env) not in ("/tmp", "/var/tmp"):
        cands.append(env)
    # ③ 系统临时目录 (**只在前两个都不可用时兜底** ⇒ 配额打满时它也会失败 ⇒ 那就如实报错**)
    cands.append(tempfile.gettempdir())

    for d in cands:
        try:
            os.makedirs(d, exist_ok=True)
        except Exception:  # noqa: BLE001
            continue
        if _usable(d):
            return d
    raise RuntimeError(
        "★gate_tmpdir(): 找不到可写的临时目录 (试过: %s) ⇒ "
        "★**这是环境问题, 不是闸红** ⇒ 请清理磁盘/配额后重跑" % ", ".join(map(str, cands))
    )


if __name__ == "__main__":
    d = gate_tmpdir()
    print(d)
    print("usable:", _usable(d))
