#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_sch_loadable.py —— ★原理图"KiCad 真能打开"门禁 (2026-11-04 19:4x 新增)

★为什么必须有它 (实测踩过):
  我们的原理图是**脚本生成**的 (`state/gen_kicad_sch.py`) ⇒ 生成器少写一个右括号, KiCad 就直接
  "Failed to load schematic" ⇒ **PDF/SVG/网表/BOM 全导不出来** ⇒ 而生成器自己的自检 (C1~C6)
  **只查语义 (符号数/引脚数/网名集合), 不查 s-表达式的括号平衡** ⇒ ★**盲区**。
  ★实测: 2026-10-27 第一次生成原理图起, 隐藏属性行少一个 ")" ⇒ 296×3=888 层不闭合 ⇒
  **原理图一直是坏的**, 直到 2026-11-04 19:4x 老板要"尽快看到原理图" 才暴露出来。

判据 (全过才 rc=0):
  C1 s-表达式括号平衡: 扫全文 (跳过字符串内容) ⇒ 最终深度必须 == 0
  C2 KiCad 真能加载: `kicad-cli sch export netlist` 必须 rc=0 (走 state/kicad.sh, 免 root AppImage)
  C3 KiCad 能出 PDF: `kicad-cli sch export pdf` 必须 rc=0 且文件非空
  C4 引脚/网名自检: `state/gen_kicad_sch.py` 自带 C1~C6 (由 gen_sch 自检脚本或调用方保证)

用法: python3 state/check_sch_loadable.py
退出码: 0=全过; 1=有问题
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
SCH = os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_sch")
KC = os.path.join(HERE, "kicad.sh")


def paren_balance(path):
    """★扫 s-表达式括号平衡 (跳过字符串; 支持 \\ 转义)"""
    depth = 0
    instr = False
    esc = False
    worst = 0
    with open(path, encoding="utf-8") as f:
        for ch in f.read():
            if instr:
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == '"':
                    instr = False
                continue
            if ch == '"':
                instr = True
            elif ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                worst = min(worst, depth)
    return depth, worst, instr


def run(cmd):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=600, cwd=PROJ)
        return r.returncode, (r.stdout + r.stderr)[-400:]
    except Exception as e:
        return 99, str(e)


def main():
    print("=" * 74)
    print("原理图可加载门禁 · check_sch_loadable (★KiCad 真能打开才算过)")
    print("=" * 74)
    fails = 0
    if not os.path.exists(SCH):
        print(f"❌ C0 原理图不存在: {SCH}")
        return 1

    depth, worst, unclosed = paren_balance(SCH)
    ok1 = (depth == 0 and not unclosed)
    print(f"  {'✅' if ok1 else '❌'} C1 s-表达式括号平衡: 最终深度={depth} (需 0) · 最低点={worst} · 字符串未闭合={unclosed}")
    if not ok1:
        fails += 1
        print("      ★修法: `state/gen_kicad_sch.py` 里少写了右括号 ⇒ 重新生成原理图")

    net_out = "/tmp/_sch_loadable.net"
    rc, msg = run(["bash", KC, "sch", "export", "netlist", "-o", net_out, SCH])
    ok2 = rc == 0 and os.path.exists(net_out) and os.path.getsize(net_out) > 1000
    print(f"  {'✅' if ok2 else '❌'} C2 KiCad 能加载并导出网表: rc={rc}"
          + (f" · {os.path.getsize(net_out)} B" if os.path.exists(net_out) else ""))
    if not ok2:
        fails += 1
        print(f"      ★KiCad 报错: {msg.strip()[:200]}")

    pdf_out = "/tmp/_sch_loadable.pdf"
    rc, msg = run(["bash", KC, "sch", "export", "pdf", "-o", pdf_out, SCH])
    ok3 = rc == 0 and os.path.exists(pdf_out) and os.path.getsize(pdf_out) > 1000
    print(f"  {'✅' if ok3 else '❌'} C3 KiCad 能导出原理图 PDF: rc={rc}"
          + (f" · {os.path.getsize(pdf_out)} B" if os.path.exists(pdf_out) else ""))
    if not ok3:
        fails += 1
        print(f"      ★KiCad 报错: {msg.strip()[:200]}")

    print("-" * 74)
    if fails:
        print(f"❌ 原理图门禁: {fails} 项不通过 —— ★**这张图不能当交付物**")
        return 1
    print("✅ 全过 —— 原理图是 KiCad 真能打开、能导出 PDF/网表/BOM 的图纸")
    return 0


if __name__ == "__main__":
    sys.exit(main())
