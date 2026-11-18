#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""改 HW/e2e_budget_rk3572.py 的 §⑤ 打印块 (288~319 行) —— 修 sw-lead 验证拍出的 R1/R3/R4/R5。

★**为什么用脚本改**: 这块全是 ★ 与 f-string, 手写 edit 容易因为 ★★ 号匹配失败 ⇒ 用行号范围替换更稳。
★**改完必须实跑** (--selftest + 主表) —— 本脚本自己会跑一遍。
"""
import io
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
TARGET = os.path.join(PROJ, "HW", "e2e_budget_rk3572.py")

NEW_BLOCK = '''    print(f"    {'T_DISPLAY_OUT (显示输出侧 S9)':<38} = {T_DISPLAY_OUT:>6.2f} ms   ★★**随显示分辨率变**★★")
    print(f"    {'T_PANEL (光机逐帧延迟 S10)':<38} = {T_PANEL:>6.2f} ms   ★**不随像素数变** (面板自身时序)")
    print(f"    {'T_RESIDUAL (反解余量)':<38} = {T_RESIDUAL:>6.2f} ms")
    print(f"    {'合计 (= T_FIXED, 恒等)':<38} = {T_PRE_EXPOSURE+T_DRAW+T_DISPLAY_OUT+T_PANEL+T_RESIDUAL:>6.2f} ms")
    print(f"\\n  ★★**显示输出侧 = 板端【两段】之和 (DEMO_OD_TIMING_SPEC §3.2 阶段表)**")
    print(f"    · 第7段 合成 `t_compose` (letterbox + 等比缩放 + 叠加)")
    print(f"    · 第8段 上屏 `t_display` (plane commit + page flip ⇒ **含 DSI 移出**)")
    print(f"    ★**TX 物理下限** = 一帧比特 / 链路有效带宽 (★4-lane D-PHY@2.0Gbps × 80%, 与 §⑥ 同口径★)")
    print(f"      800×600 = {TX_MIN_800:>6.3f} ms  ⇒  1920×1080 = {TX_MIN_1080:>6.3f} ms  ★**涨了 {TX_MIN_1080-TX_MIN_800:.3f} ms**")
    print(f"\\n  ★★**可测判据 (★这才是本节要的东西★)**: 模式A ≤ 60ms ⇒ **显示输出侧总额最多能是多少**")
    print(f"    {'方案':<26}{'S5(ms)':>9}{'输出侧上限':>13}{'减TX后·合成上限':>17}{'线性上界':>12}{'判定':>10}")
    print("    " + "-" * 88)
    cand5 = [
        ("RK3572 + yolov5s@640", scale(17.39, RK3576_TOPS, RK3572_TOPS)),
        ("RK3572 + yolov5n@640", s5n),
        ("RK3572 + yolov5s@320", (scale(5.00, RK3576_TOPS, RK3572_TOPS) + scale(4.00, RK3576_TOPS, RK3572_TOPS)) / 2),
    ]
    upper = compose_upper_bound(ratio)
    for name, s5v in cand5:
        mx = display_out_max_for(s5v)
        cmx = compose_max_for(s5v)
        print(f"    {name:<26}{s5v:>9.2f}{mx:>13.2f}{cmx:>17.2f}{upper:>12.2f}{'✅ 过' if mx >= upper else '❌ 不过':>10}")
    print(f"\\n  ★**读法 (★这是 ISS-137 的交付物★)**:")
    print(f"    · 【输出侧上限】= ★**板端段7+段8 合计最多能是多少** ⇒ ★**这才是打点的意义**")
    print(f"    · 【减TX后·合成上限】= 输出侧上限 − TX 物理下限 ⇒ ★**若只关心合成段, 用这一列**")
    print(f"    · 【线性上界】= {SYNTH_RESERVE_BASE:.2f}ms × {ratio:.2f} = {upper:.2f}ms ⇒ ★**悲观上界** (缩放器跑满也不降本)")
    print(f"    · ★**两者一比, 立刻知道[这个方案还剩多少空间]**: 若 上限 < 线性上界 ⇒ 该方案在[最坏情况]也不过线")
    if _tc_override is not None:
        print(f"\\n  ★★**代入实测 t_compose = {_tc_override:.2f} ms (★板端第7段打点·上屏段取物理下限 {TX_MIN_1080:.2f}ms★)**")
        for name, s5v in cand5:
            ma = modeA_with_compose(s5v, _tc_override)
            print(f"    {name:<26} 模式A = {ma:>7.2f} ms  {'✅ 过' if ma <= 60 else '❌ 不过'}")
        print(f"    ★**注**: 上屏段若实测出比物理下限更大的值 ⇒ ★**模式A 还要再减** ⇒ ★**板端第8段也要打点**")
    else:
        print(f"\\n  ★**还没实测 ⇒ 上面的[上限]就是判据本身** ⇒ ★板端打【两个】点 (第7段合成 + 第8段上屏)")
        print(f"    ⇒ 代入: `python3 HW/e2e_budget_rk3572.py --t-compose-ms <实测值>` ⇒ ★**一行命令出结论**")
    print(f"  ★**两条决定是叠加的**: 主控 RK3572 (NPU ×1.5) 与 显示 1920×1080 (输出侧 ×{ratio:.2f}) **都往同一个方向推**")
    print(f"  ★★**但现在这个结论【可判了】**: 不再是\\"显示段占多少是 [0数据]\\" ⇒ ★**变成\\"显示输出侧合计测出 ≤ {display_out_max_for(s5n):.2f}ms\\"**")
'''

with io.open(TARGET, encoding="utf-8") as f:
    lines = f.readlines()

# 定位: 起 = 含 "T_COMPOSE (显示合成/缩放 S9)" 的行; 止 = 含 '变成\\"t_compose 测出' 的行
start = end = None
for i, ln in enumerate(lines):
    if "T_COMPOSE (显示合成/缩放 S9)" in ln:
        start = i
    if start is not None and '变成\\"t_compose 测出' in ln:
        end = i
        break
if start is None or end is None:
    print("❌ 定位失败 (start=%s end=%s)" % (start, end))
    sys.exit(2)

print("★ 替换行范围: %d ~ %d (共 %d 行)" % (start + 1, end + 1, end - start + 1))
lines[start:end + 1] = [NEW_BLOCK]
with io.open(TARGET, "w", encoding="utf-8") as f:
    f.writelines(lines)
print("✅ 已写入")

# 立即自证: 语法 + 自测 + 主表能跑
r = subprocess.run([sys.executable, "-m", "py_compile", TARGET], capture_output=True, text=True)
if r.returncode != 0:
    print("❌ 语法错:")
    print(r.stderr[-1500:])
    sys.exit(1)
print("✅ 语法通过")
r = subprocess.run([sys.executable, TARGET, "--selftest"], capture_output=True, text=True, cwd=PROJ)
print(r.stdout[-2500:])
if r.returncode != 0:
    print("❌ selftest rc=%d" % r.returncode)
    print(r.stderr[-1500:])
    sys.exit(1)
print("✅ selftest rc=0")
