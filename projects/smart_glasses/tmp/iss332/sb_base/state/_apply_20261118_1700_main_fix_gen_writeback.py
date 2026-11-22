#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""main 修【产生点】: state/gen_kicad_project.py 的 4 处无条件写盘 → 改成【内容等价就不写】

★★**为什么这是产生点 (★不在产物上擦★)** ★★
★**根因链 (★2026-11-18 本机实读★)**: ★
  `state/check_pcb_drc.py` L156~L159 (C5 生成器自检) → **无条件** `run([sys.executable, "gen_kicad_project.py"])`
  → `state/gen_kicad_project.py` L255/L286/L303/L369 → **无条件** `open(...,'w').write(...)`
  ⇒ ⇒ **任何跑 check_pcb_drc.py 的动作** (★臂跑链 / daily_check / chain_gate★) 都改这 4 个文件的 mtime+md5
  ⇒ ⇒ 同型缺陷 ISS-280 (2026-11-17 08:50) 已披露过一次, 至今未修 ⇒ **复发型缺陷**

★★**本脚本改什么 (★只有一处·最小★)** ★★
★ ① 新增 `PCB_DOC_OUT` 环境变量 ⇒ **产物输出目录可重定向** (默认 = PCB_DIR ⇒ **行为逐字不变**)
★ ② 新增 `_write_if_changed()` ⇒ **写盘前做内容比对 (归一化 uuid + 时间戳)** ⇒ 内容等价 ⇒ **不写** ⇒ mtime/md5 不动
★ ③ C7 交叉校验的文档清单跟着走 (STACKUP.md 取自产物目录 · STACKUP_IMPEDANCE.md 是只读输入 ⇒ 留在 PCB_DIR)
★ **不动**: 板本体 / 网表 / 脚表 / BOM / 任何闸的判据逻辑 / rc 语义

★★**为什么加 PCB_DOC_OUT (★不是多余★)** ★★
★ **自测不许碰真件**: 守卫脚本要在【沙盒目录】里真跑一遍生成器 (两次 ⇒ 第二次必须不写) ⇒ 需要能重定向输出目录
★ ⇒ 沙盒自测 = **一个字节都不碰 HW/PCB/**

★**退出码**: 0 = 补丁已落 (或已存在 ⇒ 幂等跳过); 1 = 断言失败 (一个字都没改)
"""
from __future__ import annotations

import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, "gen_kicad_project.py")
BAK = TARGET + ".bak_20261118_1700_main_writeback_guard"

# ★★ 补丁块 1: 顶部加 re import + DOC_OUT/_norm/_write_if_changed 三件套 ★★
ANCHOR1 = """import json
import os
import sys
from datetime import datetime
"""
BLOCK1 = """import json
import os
import re
import sys
from datetime import datetime

# ★★2026-11-18 17:0x (★main·ISS-280 同型复发修复★) ★★ **产物输出目录可重定向** ★★
#   ★**为什么**: 守卫脚本要在【沙盒】里真跑生成器两次 (验证"内容等价就不写") ⇒ 必须能重定向输出目录
#   ★**默认 = PCB_DIR ⇒ 行为逐字不变** (不设这个变量时与改前完全一致)
DOC_OUT = os.environ.get("PCB_DOC_OUT") or None   # ★None = 用 PCB_DIR

# ★★2026-11-18 17:0x (★main·ISS-280 同型复发修复★) ★★ **写盘前内容比对: 等价就不写** ★★
#   ★**病根**: 之前 4 处 `open(...,'w').write(...)` 是【无条件】的 ⇒ 任何跑 check_pcb_drc.py 的动作
#   ★           (臂跑链 / daily_check / chain_gate) 都改这 4 个文件的 mtime+md5
#   ★           ⇒ ① 任何用 mtime 判"有没有被改过"的判据【永久失效】 ② 每次生成器自检都制造一次假变更
#   ★**修法 (★修在产生点, 不是擦产物★)**: 写盘前把【易变部分】归一化 (随机 uuid + 生成时刻) 再比
#   ★           ⇒ 内容等价 ⇒ **不写** (mtime/md5 不动) ⇒ 语义改动时**照写** (不漏更新)
#   ★**归一化只吃两样东西 (★都是【天生每次都变】的★)**: `(uuid "...")` + `YYYY-MM-DDTHH:MM:SS`
#   ★           ⇒ 真实内容变化 (层数/阻抗/自检结论) 一定不归一化 ⇒ 不会被误判成"等价"
_VOLATILE_RE = re.compile(
    r"\\(uuid \\\"[0-9a-fA-F-]{36}\\\"\\)|\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}")


def _norm(text: str) -> str:
    \"\"\"★把【每次生成必变】的部分归一化 ⇒ 只比真实内容★\"\"\"
    return _VOLATILE_RE.sub("<VOLATILE>", text)


def _write_if_changed(path: str, content: str) -> bool:
    \"\"\"★内容等价 ⇒ 不写 (★返回 False★); 真变了 ⇒ 照写 (★返回 True★)\"\"\"
    try:
        with open(path, encoding="utf-8") as f:
            old = f.read()
    except Exception:
        old = None
    if old is not None and _norm(old) == _norm(content):
        return False
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return True
"""

# ★★ 补丁块 2: main() 里 4 处写盘 + makedirs + C7 文档清单 ★★
ANCHOR2 = """def main():
    os.makedirs(PCB_DIR, exist_ok=True)
    P = json.load(open(PARAMS, encoding="utf-8"))
"""
BLOCK2 = """def main():
    os.makedirs(PCB_DIR, exist_ok=True)
    out_dir = DOC_OUT or PCB_DIR
    os.makedirs(out_dir, exist_ok=True)
    P = json.load(open(PARAMS, encoding="utf-8"))
"""

ANCHOR3 = """    out_pcb = os.path.join(PCB_DIR, "_frame_reference.kicad_pcb")
    open(out_pcb, "w", encoding="utf-8").write(pcb + "\\n")
"""
BLOCK3 = """    out_pcb = os.path.join(out_dir, "_frame_reference.kicad_pcb")
    _write_if_changed(out_pcb, pcb + "\\n")
"""

ANCHOR4 = """    open(os.path.join(PCB_DIR, "STACKUP.md"), "w", encoding="utf-8").write(stackup_md)
"""
BLOCK4 = """    _write_if_changed(os.path.join(out_dir, "STACKUP.md"), stackup_md)
"""

ANCHOR5 = """    open(os.path.join(PCB_DIR, "LAYOUT_RULES.md"), "w", encoding="utf-8").write(rules_md)
"""
BLOCK5 = """    _write_if_changed(os.path.join(out_dir, "LAYOUT_RULES.md"), rules_md)
"""

ANCHOR6 = """    open(os.path.join(PCB_DIR, "GEN_SELF_CHECK.txt"), "w", encoding="utf-8").write("\\n".join(rep) + "\\n")
"""
BLOCK6 = """    _write_if_changed(os.path.join(out_dir, "GEN_SELF_CHECK.txt"), "\\n".join(rep) + "\\n")
"""

ANCHOR7 = """        _ok3, _bad3 = _cd(os.path.join(PCB_DIR, "demo_mainboard.kicad_pcb"),
                          [os.path.join(PCB_DIR, "STACKUP.md"),
                           os.path.join(PCB_DIR, "STACKUP_IMPEDANCE.md")])
"""
BLOCK7 = """        # ★★STACKUP.md = 本次生成的产物 (取自 out_dir) · STACKUP_IMPEDANCE.md = 只读输入 (留在 PCB_DIR)★★
        _ok3, _bad3 = _cd(os.path.join(PCB_DIR, "demo_mainboard.kicad_pcb"),
                          [os.path.join(out_dir, "STACKUP.md"),
                           os.path.join(PCB_DIR, "STACKUP_IMPEDANCE.md")])
"""

PATCHES = [
    (ANCHOR1, BLOCK1),
    (ANCHOR2, BLOCK2),
    (ANCHOR3, BLOCK3),
    (ANCHOR4, BLOCK4),
    (ANCHOR5, BLOCK5),
    (ANCHOR6, BLOCK6),
    (ANCHOR7, BLOCK7),
]


def main() -> int:
    src = open(TARGET, encoding="utf-8").read()
    if "_write_if_changed" in src and "PCB_DOC_OUT" in src:
        print("· 已是修好的版本 (幂等跳过)")
        return 0
    for i, (a, b) in enumerate(PATCHES, 1):
        n = src.count(a)
        if n != 1:
            print("❌ 锚点 %d 命中 %d 次 (期望 1) ⇒ 一个字都没改" % (i, n))
            return 1
    new = src
    for a, b in PATCHES:
        new = new.replace(a, b, 1)
    # ★语法自检: 改完先能编译, 才落盘 ★
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
    print("   · 新增 PCB_DOC_OUT (默认 = PCB_DIR ⇒ 行为不变)")
    print("   · 4 处无条件写盘 → _write_if_changed (内容等价 ⇒ 不写)")
    print("   · C7 交叉校验: STACKUP.md 取自 out_dir · STACKUP_IMPEDANCE.md 仍读 PCB_DIR")
    return 0


if __name__ == "__main__":
    sys.exit(main())
