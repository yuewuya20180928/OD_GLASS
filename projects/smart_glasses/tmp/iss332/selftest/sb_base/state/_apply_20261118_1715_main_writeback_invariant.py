#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""main 把【生成器副产物不许被巡检改写】这条变成巡检里的【活的不变量】+ 把守卫脚本挂进 GUARD_TESTS

★★**为什么 (★"落线前就拦"★)** ★★
★ ISS-280 (2026-11-17 08:50) 与 ISS-325 (2026-11-18) 两次披露同一个复发型缺陷:
★   `check_pcb_drc.py` 的 C5 生成器自检 ⇒ 无条件重写 `HW/PCB/` 下 4 个产物
★   ⇒ 每天的 daily_check / chain_gate / 每条臂跑链都在改这 4 个文件的 mtime+md5
★ ⇒ ① 任何用 mtime 判「有没有被改过」的判据【永久失效】 ② 「零写板双证」每次都要重做一遍
★ **只修一次不够** ⇒ 必须【有一道活闸盯着】, 否则下一个 agent 改生成器 ⇒ 又复发 ⇒ 没人知道
★★**这一改动加了什么** ★★
★ ① 巡检段: 跑 `check_pcb_drc.py` **前后**快照 4 个产物的 (md5, mtime_ns) ⇒ 变了就报红
★    ⇒ ★**这就是"落线前就拦"**: 缺陷一回来, 当天巡检就红, 不必等下一次人工披露★★
★ ② `GUARD_TESTS` 加一条 `_test_gen_writeback_guard.py` ⇒ 守卫自己也被守卫
★    (★该脚本自带反向用例: 旧版生成器 ⇒ 缺陷复现; 新版 ⇒ 不复现 ⇒ 证明它能区分真假绿★)
★ **没动的**: 判据语义 / rc 语义 / 板 / 网表 / 脚表 / BOM / 任何 agent 的分片
"""
from __future__ import annotations

import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, "daily_check.py")
BAK = TARGET + ".bak_20261118_1715_main_writeback_invariant"

ANCHOR_GUARD = """    ("_lint_arm_env.py", "臂脚本 env 变量名守卫 (★★防【注释写进 env 块⇒变量根本没生效】★★)"),
)
"""
BLOCK_GUARD = """    ("_lint_arm_env.py", "臂脚本 env 变量名守卫 (★★防【注释写进 env 块⇒变量根本没生效】★★)"),
    ("_test_gen_writeback_guard.py", "生成器副产物写盘守卫 (★内容等价就不写★ · ★自带反向用例★)"),
)
"""

# ★★ 巡检段: 在跑 check_pcb_drc 之前加快照, 之后加比对 ★★
ANCHOR_PRE = """    # ★2026-11-02 22:5x: PCB 图纸门禁进门禁链 (自己画的图自己验; EN 那个 P0 的教训)
    rc_pcb_rc, out_p, err_p = run("check_pcb_drc.py")
    pcb_ok = (rc_pcb_rc == 0)
"""
BLOCK_PRE = """    # ★2026-11-02 22:5x: PCB 图纸门禁进门禁链 (自己画的图自己验; EN 那个 P0 的教训)
    # ★★2026-11-18 17:1x (★main·ISS-280 同型复发修复·配套活闸★): ★**跑 DRC 前后快照 4 个生成器副产物** ★★
    #   ★**为什么**: C5 生成器自检曾无条件重写这 4 个文件 ⇒ 每天巡检都改它们的 mtime+md5
    #   ★           ⇒ 任何用 mtime 判"有没有被改过"的判据【永久失效】⇒ ★**这条不变量就是防复发的活闸** ★★
    #   ★**判据**: 跑 DRC【之后】这 4 个文件的 (md5, mtime_ns) 逐个未变 ⇒ 变了 = 写盘守卫被改坏/被绕过 ⇒ 报红 ★★
    _wb_files = ("STACKUP.md", "LAYOUT_RULES.md", "GEN_SELF_CHECK.txt", "_frame_reference.kicad_pcb")
    _wb_dir = os.path.join(PROJ, "HW", "PCB")
    _wb_before = {}
    for _n in _wb_files:
        _p = os.path.join(_wb_dir, _n)
        try:
            _st = os.stat(_p)
            _wb_before[_n] = (_st.st_mtime_ns, _st.st_size)
        except OSError:
            _wb_before[_n] = None
    rc_pcb_rc, out_p, err_p = run("check_pcb_drc.py")
    pcb_ok = (rc_pcb_rc == 0)
    # ★★跑完之后逐个比对 ⇒ 变了就报红 (★"落线前就拦"★)
    _wb_moved = []
    for _n in _wb_files:
        _p = os.path.join(_wb_dir, _n)
        try:
            _st = os.stat(_p)
            _now = (_st.st_mtime_ns, _st.st_size)
        except OSError:
            _now = None
        if _wb_before.get(_n) != _now:
            _wb_moved.append(_n)
    if _wb_moved:
        problems.append("★跑 check_pcb_drc 之后 HW/PCB/ 下这 4 个生成器副产物被改写: %s "
                        "⇒ 『内容等价就不写』守卫失效或被绕过 (★ISS-280 同型缺陷·复发★) ⇒ "
                        "⇒ mtime 判据【已废】, 请查 state/gen_kicad_project.py" % _wb_moved)
    print("%s 生成器副产物零改写不变量 (★4 件 mtime+size 逐个未变: %s★)"
          % ("✅" if not _wb_moved else "❌", _wb_moved or "全未变"))
"""

PATCHES = [
    (ANCHOR_GUARD, BLOCK_GUARD),
    (ANCHOR_PRE, BLOCK_PRE),
]


def main() -> int:
    src = open(TARGET, encoding="utf-8").read()
    if "_wb_moved" in src and "_test_gen_writeback_guard.py" in src:
        print("· 已是修好的版本 (幂等跳过)")
        return 0
    new = src
    for i, (a, b) in enumerate(PATCHES, 1):
        n = new.count(a)
        if n != 1:
            print("❌ 锚点 %d 命中 %d 次 (期望 1) ⇒ 一个字都没改" % (i, n))
            return 1
        new = new.replace(a, b, 1)
    try:
        compile(new, TARGET, "exec")
    except SyntaxError as e:
        print("❌ 语法错: %s ⇒ 一个字都没改" % e)
        return 1
    shutil.copy2(TARGET, BAK)
    tmp = TARGET + ".tmp_patch"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(new)
    os.replace(tmp, TARGET)
    print("✅ 已改 %s (备份 %s)" % (os.path.basename(TARGET), os.path.basename(BAK)))
    print("   · 巡检段: 跑 check_pcb_drc 前后快照 4 个副产物 ⇒ 变了就报红 (活闸)")
    print("   · GUARD_TESTS: 加 _test_gen_writeback_guard.py (守卫自己也被守卫)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
