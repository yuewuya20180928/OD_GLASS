#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R_ILIM 300Ω → 390Ω 统一 (2026-10-28 08:2x, 项目总工)
====================================================================
为什么必须做:
  老板 10-28 拍板 "边戴边充不允许" ⇒ 皮肤温度不再是充电时硬约束 ⇒ R_ILIM 470Ω → **390Ω**
  (IINMAX 1.00A / ICHG 0.82A / 单 pin 0.411A / 充电 ~29min); 300Ω 档**正式判死**
  (单 pin 0.534A > 0.5mm pitch ZIF 的 0.5A 触点天花板)。
  但库内还有 3 处写 300Ω ⇒ **同一份网表内部自相矛盾** (P1 第 44/45 行写 390Ω,
  P10 第 484/494 行写 300Ω) —— 投板前必须清零。

本脚本只改 3 个文件 (充电板侧, 与在跑的 hw-lead ISS-049 / mech-lead ISS-089 不重叠):
  ① state/p10_rows.json   (P10 页数据源)
  ② HW/CHARGE_BOARD_SPEC.md (充电板规格)
  ③ HW/netlist_v1.csv      (由 gen_netlist.py 从 p10_rows.json 生成 —— 本脚本不直接改,
                              改完 p10_rows.json 后重跑 gen_netlist.py 重新生成)

★纪律: 档位对比表里的 300Ω 行**保留并标"判死"** (留变更痕迹), 不删。
  只把"当前取值/当前推荐/封顶链/公式代入"改成 390Ω。
"""
from __future__ import annotations

import json
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)

# ---------------- ① state/p10_rows.json ----------------
P10 = os.path.join(HERE, "p10_rows.json")
with open(P10, encoding="utf-8") as f:
    rows = json.load(f)

p10_repl = [
    # I2C_CHG_SCL 行 note: "充电电流安全链不受影响 (R_ILIM 300Ω 硬件封顶)"
    ("充电电流安全链不受影响 (R_ILIM 300Ω 硬件封顶)",
     "充电电流安全链不受影响 (R_ILIM 390Ω 硬件封顶: IINMAX 1.00A / ICHG 0.82A)"),
    # IINLIM 行 note: 整条 300Ω
    ("★pin10 ILIM: R_ILIM = 300Ω ±1% 必装 (已在主网表 P1 第 39/40 行画出, 本行不重复画电阻, 只登记引脚归属); "
     "IINMAX = KILIM/RILIM (KILIM 320/355/390 AΩ) = 1.07-1.30A 硬件上限; "
     "ILIM 脚稳在 0.8V ⇒ 电阻功耗 0.8²/300 = 2.1mW; "
     "★即使 I2C 不跨铰链、ICHG 寄存器停在复位默认 2048mA, 充电电流仍被这颗电阻压在 ~1.0A (铰链安全链兜底)",
     "★pin10 ILIM: R_ILIM = 390Ω ±1% 必装 (已在主网表 P1 第 44/45 行画出, 本行不重复画电阻, 只登记引脚归属); "
     "IINMAX = KILIM/RILIM (KILIM 320/355/390 AΩ) = 0.82-1.00A 硬件上限 (max 档 IINMAX=1.00A); "
     "ILIM 脚稳在 0.8V ⇒ 电阻功耗 0.8²/390 = 1.64mW; "
     "★即使 I2C 不跨铰链、ICHG 寄存器停在复位默认 2048mA, 充电电流仍被这颗电阻压在 ~1.0A (铰链安全链兜底)。"
     "★★V1.9 (老板 10-28 拍板『边戴边充不允许』): 皮肤温度不再是充电时硬约束 ⇒ 充电电流可提速 ⇒ **定 390Ω** "
     "(V1.7/V1.8 的 470Ω 口径作废; 300Ω 档**正式判死**: 单 pin 0.534A > 0.5mm pitch ZIF 的 0.5A 触点天花板)。"
     "触点额定判据收紧到 **≥0.5A/触点** 且工况写明『只有 pin1/pin2 载流, 其余 ≤1mA』"),
]
hit = 0
for r in rows:
    n = r.get("note") or ""
    for old, new in p10_repl:
        if old in n:
            r["note"] = n.replace(old, new)
            n = r["note"]
            hit += 1
if hit != len(p10_repl):
    print(f"❌ p10_rows.json 只替换了 {hit}/{len(p10_repl)} 条 —— 预期字符串可能已变, 不落盘")
    sys.exit(1)

text = json.dumps(rows, ensure_ascii=False, indent=2)
fd, tmp = tempfile.mkstemp(prefix="p10_rows.json.", suffix=".tmp", dir=HERE)
try:
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, P10)
except BaseException:
    try:
        os.unlink(tmp)
    except OSError:
        pass
    raise
print(f"✅ ① state/p10_rows.json: {hit} 条 note 已改 (300Ω → 390Ω)")

# ---------------- ② HW/CHARGE_BOARD_SPEC.md ----------------
SPEC = os.path.join(PROJ, "HW", "CHARGE_BOARD_SPEC.md")
with open(SPEC, encoding="utf-8") as f:
    spec = f.read()

spec_repl = [
    # §2.1 引脚表第 10 行 ILIM
    ("| **10** | ILIM | AI | `R_ILIM` → PGND | **300Ω ±1% (0402)** |",
     "| **10** | ILIM | AI | `R_ILIM` → PGND | **390Ω ±1% (0402)** |"),
    # §2.4 档位表: 推荐值行
    ("| **300Ω ±1%** | 1.07 / 1.18 / 1.30 A | 0.88 / 0.97 / **1.07 A** | **~1.0 A** | "
     "★**本规格推荐值** (对齐 §3.1.3 \"推荐充电电流 1.0A\") |",
     "| **390Ω ±1%** | 0.82 / 0.91 / **1.00 A** | 0.67 / 0.75 / **0.82 A** | **~0.75 A** | "
     "★★**本规格推荐值** (V1.9, 老板 10-28 拍板『边戴边充不允许』⇒ 皮肤温度不再是充电时硬约束 ⇒ 充电电流可提速; "
     "单 pin 0.411A ≤ 0.5A 触点天花板, 余量 1.22×) |"),
    # 档位表里 390Ω 那一行 (原来是"ISS-091 判定…时换这颗")
    ("| 390Ω ±1% | 0.82 / 0.91 / 1.00 A | 0.67 / 0.75 / 0.82 A | ~0.75 A | "
     "ISS-091 判定铰链只能过 1.0A 时换这颗 (**换料不换板**) |",
     "| 300Ω ±1% | 1.07 / 1.18 / 1.30 A | 0.88 / 0.97 / 1.07 A | ~1.0 A | "
     "❌ **300Ω 档正式判死** (V1.9): 单 pin 0.534A > 任何 0.5mm pitch FPC ZIF 的 0.5A 触点天花板 "
     "(只能靠 1.0mm pitch, 而铰链区装不下) ⇒ **不可选** |"),
    # §2.4 电阻功耗
    ("> ★**电阻功耗不是问题**: ILIM 脚被稳在 0.8V → P = 0.8²/300 = **2.1 mW** → 0402 足够 (不需要大功率电阻)。",
     "> ★**电阻功耗不是问题**: ILIM 脚被稳在 0.8V → P = 0.8²/390 = **1.64 mW** → 0402 足够 (不需要大功率电阻)。"),
    # §2.8 封顶链
    ("| **本规格的封顶链** | ILIM 脚 `R_ILIM` = 300Ω → **1.07-1.30A 硬件上限**, 与寄存器无关 | [官方] |",
     "| **本规格的封顶链** | ILIM 脚 `R_ILIM` = 390Ω → **0.82-1.00A 硬件上限**, 与寄存器无关 | [官方] |"),
    # §3.1.3 补丁2
    ("- `R_ILIM` = 300Ω (→ 输入 1.07-1.30A, CC 段电池电流 ~0.88-1.07A)。",
     "- `R_ILIM` = 390Ω (→ 输入 0.82-1.00A, CC 段电池电流 ~0.67-0.82A)。"),
    ("⇒ **`R_ILIM` = 300Ω 是\"无软件依赖\"的基线; 有软件时 SoC 按 BC1.2 结果写 REG00 (IINLIM) 来精确贴合源能力。**",
     "⇒ **`R_ILIM` = 390Ω 是\"无软件依赖\"的基线; 有软件时 SoC 按 BC1.2 结果写 REG00 (IINLIM) 来精确贴合源能力。**"),
    # §3.4 场景表 ①②③ 里的 300Ω → 390Ω
    ("| ① Rd-only + 常见 Rp=56k 充电器 | 500 mA | 300Ω | 0.5A (源封顶) | **~0.41 A** | **3.7×** |",
     "| ① Rd-only + 常见 Rp=56k 充电器 | 500 mA | 390Ω | 0.5A (源封顶) | **~0.41 A** | **3.7×** |"),
    ("| ② Rd-only + Rp=22k 充电器 | 1.5 A | 300Ω | 1.07-1.30A | **~0.88-1.07 A** | **1.4-1.7×** |",
     "| ② Rd-only + Rp=22k 充电器 | 1.5 A | 390Ω | 0.82-1.00A | **~0.67-0.82 A** | **1.8-2.2×** |"),
    ("| ③ 加 PD 5V/2A + `R_ILIM`=300Ω | 2 A | 300Ω | 1.07-1.30A | **~0.88-1.07 A** | **1.4-1.7×** |",
     "| ③ 加 PD 5V/2A + `R_ILIM`=390Ω | 2 A | 390Ω | 0.82-1.00A | **~0.67-0.82 A** | **1.8-2.2×** |"),
    ("| ④ 加 PD 5V/2A + `R_ILIM`=390Ω (保守) | 2 A | 390Ω | 0.82-1.00A | **~0.67-0.82 A** | **1.8-2.2×** |",
     "| ④ 加 PD 5V/2A + `R_ILIM`=260Ω (更激进) | 2 A | 260Ω | 1.23-1.50A | **~1.01-1.23 A** | **1.2-1.5×** |"),
    ("| ⑤ 加 PD 5V/2A + `R_ILIM`=260Ω | 2 A | 260Ω | 1.23-1.50A | **~1.01-1.23 A** | **1.2-1.5×** |",
     "| ⑤ 加 PD 5V/2A + `R_ILIM`=300Ω ❌ | 2 A | 300Ω | 1.07-1.30A | **~0.88-1.07 A** | "
     "❌ **判死**: 单 pin 0.534A > 0.5A 触点天花板 |"),
    # §3.4 场景⑥ 结论
    ("只要 `R_ILIM` 装上, 场景 ⑥ 被硬件压回 ~1.0A; **`R_ILIM` 不装 = 铰链过 2.05A**。",
     "只要 `R_ILIM` 装上, 场景 ⑥ 被硬件压回 ~1.0A (390Ω 档 max 1.00A); **`R_ILIM` 不装 = 铰链过 2.05A**。"),
    # 提交问题那条
    ("- 若**接受** → 按本规格出 P10, `R_ILIM`=300Ω, J_CHG pin9/pin10 留空给未来的 I2C。",
     "- 若**接受** → 按本规格出 P10, `R_ILIM`=390Ω, J_CHG pin9/pin10 留空给未来的 I2C。"),
    # §8 待复算-1
    ("| **待复算-1** | **ISS-091**: 铰链段 1.5A 载流 / 压降 / 发热核算 (0.5mm pitch FPC 每 pin 载流) | **结构总工** | 投板前 | "
     "§2.4 (`R_ILIM` 选 300Ω 还是 390Ω) |",
     "| ~~待复算-1~~ ✅ | **ISS-091** 已闭环 (10-28): 铰链段载流/压降/发热核算完成 → **定 390Ω**, 300Ω 判死 | "
     "**结构总工** | 已闭环 | §2.4 (`R_ILIM` = 390Ω) |"),
    # §3.5 B6 复现行
    ("| `R_ILIM` = 300Ω → IIN 1.07-1.30A → ICHG ~0.88-1.07A | **[推算·可复算]** | 公式见 §2.4 / §3.4, B6 可复现 |",
     "| `R_ILIM` = 390Ω → IIN 0.82-1.00A → ICHG ~0.67-0.82A | **[推算·可复算]** | 公式见 §2.4 / §3.4, B6 可复现 |"),
    # 规格附录里的网表行 (3 行)
    ("P10,VBUS_5V,J_TYPE_C A4+A9+B4+B9,D_ESD_TC,RAIL_VBUS_5V,5.0V ±5%,RAIL,必装,[推算],,"
     "电源域: 5.0V ±5% / 输入电流硬件上限 1.07-1.30A (R_ILIM=300Ω) / 充电链整条在充电板(镜框); "
     "SoC 侧球位号 TBD-01,C-01,CHG_BOARD",
     "P10,VBUS_5V,J_TYPE_C A4+A9+B4+B9,D_ESD_TC,RAIL_VBUS_5V,5.0V ±5%,RAIL,必装,[推算],,"
     "电源域: 5.0V ±5% / 输入电流硬件上限 0.82-1.00A (R_ILIM=390Ω) / 充电链整条在充电板(镜框); "
     "SoC 侧球位号 TBD-01,C-01,CHG_BOARD"),
    ("P10,ILIM,U_CHG pin10,R_ILIM,R_ILIM,300Ω ±1% (0402),R,必装,[官方],,"
     "\"★输入电流硬件上限: IINMAX=KILIM/RILIM (KILIM 320/355/390 AΩ) → 1.07-1.30A; "
     "CC 段电池电流 ~0.88-1.07A; ILIM 脚稳在 0.8V, 功耗 0.8²/300=2.1mW; "
     "**必装件** (不装 → REG04 复位默认 ICHG=2048mA 会让铰链过 2.05A); "
     "ISS-091 若判定铰链只能 1.0A 则换 390Ω (换料不换板)\",C-01,CHG_BOARD",
     "P10,ILIM,U_CHG pin10,R_ILIM,R_ILIM,390Ω ±1% (0402),R,必装,[官方],,"
     "\"★输入电流硬件上限: IINMAX=KILIM/RILIM (KILIM 320/355/390 AΩ) → 0.82-1.00A; "
     "CC 段电池电流 ~0.67-0.82A; ILIM 脚稳在 0.8V, 功耗 0.8²/390=1.64mW; "
     "**必装件** (不装 → REG04 复位默认 ICHG=2048mA 会让铰链过 2.05A); "
     "★★V1.9 (老板 10-28): 定 390Ω (单 pin 0.411A, 触点 ≥0.5A 余量 1.22×); 300Ω 档判死 (单 pin 0.534A > 0.5A 天花板)\",C-01,CHG_BOARD"),
    ("P10,PGND,R_ILIM,PGND,R_ILIM,300Ω ±1% (0402),R,必装,[官方],,ILIM 电阻 地端,C-01,CHG_BOARD",
     "P10,PGND,R_ILIM,PGND,R_ILIM,390Ω ±1% (0402),R,必装,[官方],,ILIM 电阻 地端,C-01,CHG_BOARD"),
]

miss = []
for old, new in spec_repl:
    if old not in spec:
        miss.append(old[:80])
        continue
    spec = spec.replace(old, new)
if miss:
    print(f"❌ CHARGE_BOARD_SPEC.md 有 {len(miss)} 条没匹配上, 不落盘:")
    for m in miss:
        print("   -", m)
    sys.exit(1)

fd, tmp = tempfile.mkstemp(prefix="CHARGE_BOARD_SPEC.md.", suffix=".tmp", dir=os.path.dirname(SPEC))
try:
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(spec)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, SPEC)
except BaseException:
    try:
        os.unlink(tmp)
    except OSError:
        pass
    raise
print(f"✅ ② HW/CHARGE_BOARD_SPEC.md: {len(spec_repl)} 处已改")
