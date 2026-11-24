#!/usr/bin/env python3
"""ISS-384 (hw-lead) · 追加式订正块写入器 · 2026-11-24
★只 append, 不改任何既有行 (老字一行未删)★
★每份文档一个 ISS-384 订正块, 附在文件末尾 (既有行号不位移)★
"""
import io, os, re, sys

ROOT = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"

MARK = "## ★★ ISS-384 充电电流活值订正块 (2026-11-24 · hw-lead)"

HEADER = """

{mark}
> ★★★**一句话**: 本页的【充电电流活值】仍停在旧的 `0.822` 倒数方向系数上 ⇒ ★**活值已作废**; ★**板端真值 = `R_ILIM` 680Ω (V-4 裁定 2026-11-16 · 网表/脚表/BOM 均已落表)** ⇒ **ICHG 0.697A / 单 pin 0.349A / 触点余量 1.43×**; ★**本块只把文档追平到已落表的真值, 网表一个字没动** ★★★
> ★★**当前口径系数 (必读 · ISS-384 订正口径)**: `ICHG = IINMAX × η·(Vbus/Vbat)` = **1.216 @3.70V** (最坏档) / **1.071 @4.20V** (CV 段末端); ★**旧值 0.822 = (Vbat/Vbus)/η = 1.216 的精确倒数 ⇒ 方向反了 ⇒ 旧表电流偏小 ⇒ 触点天花板判据失效** ★★
> ★★**订正方式**: ★**追加式订正块 · 老字一行未删** ★★ (ISS-230 的作废标记 L151 / L193 原样保留); ★**下表逐处给出 旧值 → 新值**, 下表所列行号的旧值一律视为【历史留痕】, ★**本块之外的同款旧值即为活值 ⇒ 由 `HW/check_charge_current_live_value.py` 判红** ★★
> ★★**零落表声明 (ISS-384)**: 本单 = 纯文档口径单 ⇒ `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` / `HW/PCB/demo_mainboard.kicad_pcb` **逐字节未动**; ★**网表 L47/L48 里那 2 处 `0.822` 是【合法的历史说明】(「旧口径写的 (VBAT/VBUS)/η = 0.822 是它的倒数」) ⇒ 一个字都不许动** ★★
> ★**唯一权威源 (只读 · 已签收)**: `MECH/HINGE_POWER_CALC.md` §0-A / §0-A.1 对照表 + `MECH/hinge_power_calc.json` 的 `rilim_table` (ISS-229 · mech-lead · 已 verified) ⇒ 复现 `python3 MECH/hinge_power_calc.py --json` (rc=0) ★
"""

ROWS_HEAD = """
### 逐处订正表 (★行号 = 本块追加前的原页行号; 锚点列 = 机器闸用的旧值 token 码★)

| 行号 | 档位 / 上下文 | 旧值 (逐字) | 锚点 (闸用) | 新值 (逐字) | 权威出处 | 证据 |
|---|---|---|---|---|---|---|
"""

ROWS_TAIL = """
> ★★**本块的读法**: ★**行号 = 原文位置**; ★**锚点列的 token 码 = 该行里出现的旧值 token** (`HW/check_charge_current_live_value.py` 按它判「这行是否已被订正」); ★**若某行出现锚点表之外的旧值 token ⇒ 闸判红** ★★
> ★★**L151 / L193 = ISS-230 留下的作废标记 (历史留痕) ⇒ 不进本表, 一个字不删** ★★
"""

PCB_ROWS = [
 ("20", "摘要表 第 3 行 (充电电流档位)",
  "充电电流档位 = R_ILIM 390Ω (IINMAX ≈1.00A / ICHG ≈0.82A / 单 pin 0.411A / 充电 ~29min); 300Ω 档正式判死 (单 pin 0.534A)",
  "T082A / T0411 / T0534 / T29M2",
  "充电电流档位 = R_ILIM 680Ω (V-4 已落表 2026-11-16) (IINMAX ≈0.57A / ICHG ≈0.697A / 单 pin 0.349A / 充电 ~34min); 390Ω 档正式判死 (单 pin 0.608A 超 0.5A 触点上限 21.6%); 300Ω 档正式判死 (单 pin 0.790A)",
  "MECH/HINGE_POWER_CALC.md §0-A.1 对照表 + rilim_table (680Ω max 行)", "[实测]"),
 ("23", "摘要表 第 6 行 ③ (电芯内阻发热)",
  "电芯内阻发热 (0.10Ω · 114mW @1.07A / ~45mW @0.82A) 贴皮肤侧",
  "T082A / T107A",
  "电芯内阻发热 (0.10Ω · 48.6mW @0.697A) 贴皮肤侧 (680Ω 档 max)",
  "MECH/HINGE_POWER_CALC.md §0-A.1 对照表 (680Ω 档 max 行: 电芯发热 48.6 mW)", "[实测]"),
 ("132", "§3.4 C-2b 工况声明",
  "0.411A/触点 余量 1.22×",
  "T0411 / T122X",
  "0.349A/触点 余量 1.43× (680Ω 档真值; 390Ω 档 0.608A 超 0.5A 上限 21.6% ⇒ 判死)",
  "MECH/HINGE_POWER_CALC.md §0-A.1 + rilim_table (680Ω max 行)", "[实测]"),
 ("143", "§3.4 表 300Ω 行",
  "1.07 A · 0.534A · ❌ 正式判死 (单 pin > 0.5A 天花板)",
  "T0534 / T107A",
  "ICHG 1.581 A · 单 pin 0.790 A · ❌ 正式判死 (超 0.5A 天花板 58%)",
  "MECH/HINGE_POWER_CALC.json rilim_table (300Ω max 行)", "[实测]"),
 ("144", "§3.4 表 390Ω 行 (原标「本单定版」)",
  "0.82 / 0.91 / 1.00 A · 0.82A · 0.411A · ✅ 余量 1.22× (对 0.5A 触点)",
  "T082A / T0411 / T122X",
  "0.82 / 0.91 / 1.00 A (IINMAX 不变) · ICHG 1.216 A · 单 pin 0.608 A · ❌ 余量 0.82× (超 0.5A 触点上限 21.6%) ⇒ 390Ω 档判死",
  "MECH/HINGE_POWER_CALC.md §0-A.1 + rilim_table (390Ω max 行)", "[实测]"),
 ("146", "§3.4 表 680Ω 行",
  "0.47 / 0.52 / 0.57 A · 0.47 A · 0.236A · ✅ 余量最大, 充电 ~51min",
  "T047A / T0236 / T51M",
  "0.47 / 0.52 / 0.57 A (IINMAX 不变) · ICHG 0.697 A · 单 pin 0.349A · ✅ 余量 1.43× · 充电 ~34min",
  "MECH/HINGE_POWER_CALC.json rilim_table (680Ω max 行)", "[实测]"),
 ("149", "§3.4 口径纪律段 (充电时间)",
  "390Ω max 档充电 ~29.20min / 典型 32.08min",
  "T29M1 / T3208",
  "680Ω max 档充电 ~34.41min / 典型 37.81min (390Ω 档 max 19.74min / 典型 21.68min, 但该档已判死)",
  "MECH/HINGE_POWER_CALC.json rilim_table t_charge_min (400mAh 口径)", "[实测]"),
 ("154", "§3.4 为什么 390Ω 能提速",
  "电流可以从 470Ω 提到 390Ω (充电 ~29min)",
  "T29M2",
  "该提速叙事作废 (390Ω 档已判死 · 单 pin 0.608A); 现行档位 = 680Ω (充电 ~34min)",
  "MECH/HINGE_POWER_CALC.md §0-A.1 + rilim_table", "[实测]"),
 ("178", "§4.2 O-4 行 (TS 参考地被回流抬高)",
  "TS 参考地被 1A 回流抬高 14-32mV = 0.44-0.99°C 停充门限偏差",
  "TTSMV / TTSC",
  "TS 参考地被 0.697A 回流抬高 20.9mV = 0.65°C 停充门限偏差 (680Ω 档 max)",
  "MECH/HINGE_POWER_CALC.md §M-4 表 (680Ω 行)", "[实测]"),
 ("234", "§6 计算脚本 代码块 (方向反了的公式)",
  "iin = (320/r, 355/r, 390/r); ichg = tuple(v*0.822 for v in iin)",
  "T0822",
  "iin = (320/r, 355/r, 390/r); ichg = tuple(v*1.216 for v in iin)   # ISS-384 订正: 旧系数 0.822 是 1.216 的倒数 (方向反了) ⇒ 作废; 1.216@3.70V / 1.071@4.20V",
  "MECH/HINGE_POWER_CALC.md §0-A + HW/CHARGE_BOARD_SPEC.md §2.4", "[实测]"),
 ("276", "§8 证据表 行 1",
  "R_ILIM 390Ω → IINMAX 0.82/0.91/1.00A, ICHG 0.82A, 单 pin 0.411A · [推算] (×0.822 换算)",
  "T0822 / T082A / T0411",
  "R_ILIM 680Ω → IINMAX 0.47/0.52/0.57A, ICHG 0.697A, 单 pin 0.349A · [实测] (×1.216 换算)",
  "MECH/HINGE_POWER_CALC.md §0-A.1 + rilim_table", "[实测]"),
 ("277", "§8 证据表 行 2",
  "300Ω 档判死 (单 pin 0.534A > 0.5A)",
  "T0534",
  "300Ω 档判死 (单 pin 0.790A > 0.5A · 超 58%)",
  "MECH/HINGE_POWER_CALC.json rilim_table (300Ω max 行)", "[实测]"),
 ("280", "§8 证据表 行 3 (触点余量)",
  "390Ω 档的 ICHG 触点余量 1.22× · 0.5A ÷ 0.411A",
  "T0411 / T122X",
  "680Ω 档的 ICHG 触点余量 1.43× · 0.5A ÷ 0.349A",
  "MECH/HINGE_POWER_CALC.json rilim_table (680Ω max 行)", "[实测]"),
 ("283", "§8 证据表 行 4 (电芯发热)",
  "电芯内阻 0.10Ω / 发热 45mW@0.82A",
  "T082A",
  "电芯内阻 0.10Ω / 发热 48.6mW@0.697A",
  "MECH/HINGE_POWER_CALC.md §0-A.1 (680Ω 档 max 行)", "[实测]"),
]

JCHG_ROWS = [
 ("15", "§1 表 第 2 行 (FH12 70% 降额条款)",
  "只有 pin1/pin2 载流 (0.411A) · 0.5A 可用, 余量 1.22×",
  "T0411 / T122X",
  "只有 pin1/pin2 载流 (0.349A) · 0.5A 可用, 余量 1.43× (680Ω 档真值)",
  "MECH/HINGE_POWER_CALC.md §0-A.1 + rilim_table (680Ω max 行)", "[实测]"),
 ("16", "§1 表 第 3 行 (选型判据)",
  "390Ω 档的单 pin 0.411A 就不合格, 会被迫退到 680Ω (充电 51min) · 0.411A > 0.35A",
  "T0411 / T51M",
  "680Ω 档的单 pin 0.349A 合格 (充电 ~34min) · 0.349A < 0.35A (680Ω 档单 pin 0.349A vs 0.5A)",
  "MECH/HINGE_POWER_CALC.md §0-A.1 + rilim_table (680Ω max 行)", "[实测]"),
 ("17", "§1 表 第 4 行 (300Ω 封死)",
  "单 pin 0.534A 超过任何 0.5mm pitch FPC ZIF 的 0.5A 额定上限",
  "T0534",
  "单 pin 0.790A 超过任何 0.5mm pitch FPC ZIF 的 0.5A 额定上限",
  "MECH/HINGE_POWER_CALC.json rilim_table (300Ω max 行)", "[实测]"),
 ("32", "§2 表 C-4 (充电电流档)",
  "R_ILIM = 390Ω → ICHG 0.822A (max) → 单 pin 0.411A",
  "T0822 / T0411",
  "R_ILIM = 680Ω (V-4 裁定 2026-11-16) → ICHG 0.697A (max) → 单 pin 0.349A",
  "网表 R_ILIM 行 (V1.9) + MECH/HINGE_POWER_CALC.md §0-A.1", "[实测]"),
 ("89", "§2 换算表 行 1 (公式)",
  "ICHG = IINMAX × 0.822 → 0.822 A",
  "T0822",
  "ICHG = IINMAX × 1.216 (η·Vbus/Vbat @VBAT=3.70V) → 0.697 A",
  "MECH/HINGE_POWER_CALC.md §0-A + HW/CHARGE_BOARD_SPEC.md §2.4", "[实测]"),
 ("90", "§2 换算表 行 2 (单 pin)",
  "单 pin (pin1 / pin2 并联) → 0.411 A",
  "T0411",
  "单 pin (pin1 / pin2 并联) → 0.349 A",
  "MECH/HINGE_POWER_CALC.json rilim_table (680Ω max 行)", "[实测]"),
 ("91", "§2 换算表 行 3 (双 pin 合计)",
  "双 pin 合计 → 0.822 A",
  "T0822",
  "双 pin 合计 → 0.697 A",
  "MECH/HINGE_POWER_CALC.json rilim_table (680Ω max 行)", "[实测]"),
 ("99", "§3.2 表 头 (档位列)",
  "390Ω 档 (0.411A) \\| 300Ω 档 (0.534A)",
  "T0411 / T0534",
  "680Ω 档 (0.349A) | 390Ω 档 (0.608A)",
  "MECH/HINGE_POWER_CALC.md §0-A.1 对照表", "[实测]"),
 ("101", "§3.2 保守读法行",
  "❌ 0.411 > 0.35 不合格",
  "T0411",
  "✅ 0.349 < 0.35 合格",
  "MECH/HINGE_POWER_CALC.json rilim_table (680Ω max 行)", "[实测]"),
 ("102", "§3.2 实际工况读法行",
  "只有 pin1/pin2 载流 0.411A, pin3/4 回流 0.411A ... ✅ 0.411 < 0.5, 余量 1.22× · ❌ 0.534 > 0.5",
  "T0411 / T0534 / T122X",
  "只有 pin1/pin2 载流 0.349A, pin3/4 回流 0.349A ... ✅ 0.349 < 0.5, 余量 1.43× · ❌ 0.790 > 0.5",
  "MECH/HINGE_POWER_CALC.md §0-A.1 + rilim_table (680Ω max 行)", "[实测]"),
 ("103", "§3.2 300Ω 档讨论行",
  "R_ILIM 300Ω → ICHG 1.069A → 单 pin 0.534A",
  "T0534 / T1069",
  "R_ILIM 300Ω → ICHG 1.581A → 单 pin 0.790A",
  "MECH/HINGE_POWER_CALC.json rilim_table (300Ω max 行)", "[实测]"),
 ("108", "§3.3 结论 1 (降额条款读法)",
  "390Ω 档就自动不合格 → 会被迫退到 680Ω (充电 51min, 而 390Ω 是 29min)",
  "T51M / T29M2",
  "680Ω 档单 pin 0.349A 合格 (充电 ~34min) ⇒ 两种读法都过, 没有解释空间",
  "MECH/HINGE_POWER_CALC.md §0-A.1 + rilim_table", "[实测]"),
 ("110", "§3.3 结论 2 (300Ω 封死)",
  "单 pin 0.534A 超过 0.5mm pitch FPC ZIF 的 0.5A 额定上限",
  "T0534",
  "单 pin 0.790A 超过 0.5mm pitch FPC ZIF 的 0.5A 额定上限",
  "MECH/HINGE_POWER_CALC.json rilim_table (300Ω max 行)", "[实测]"),
 ("161", "§J-2 (70% 降额条款)",
  "0.5A → 70% → 0.35A, 而我们的单 pin 是 0.411A —— 恰好夹在中间",
  "T0411",
  "0.5A → 70% → 0.35A, 而我们的单 pin 是 0.349A —— 在 0.35A 之上, 不夹中间",
  "MECH/HINGE_POWER_CALC.json rilim_table (680Ω max 行)", "[实测]"),
 ("168", "§J-2 减害段",
  "300Ω 档 (单 pin 0.534A) 在 0.5mm pitch 下无解",
  "T0534",
  "300Ω 档 (单 pin 0.790A) 在 0.5mm pitch 下无解",
  "MECH/HINGE_POWER_CALC.json rilim_table (300Ω max 行)", "[实测]"),
 ("197", "§9 汇总表",
  "R_ILIM = 390Ω → ICHG 0.822A → 单 pin 0.411A",
  "T0822 / T0411",
  "R_ILIM = 680Ω → ICHG 0.697A → 单 pin 0.349A",
  "网表 R_ILIM 行 (V1.9) + MECH/HINGE_POWER_CALC.md §0-A.1", "[实测]"),
]

PB_ROWS = [
 ("360", "§7.2 限流链 表头 (CC 段电池电流列)",
  "CC 段电池电流 (×Vbat/Vbus/η ≈ 0.822)",
  "T0822",
  "CC 段电池电流 (×η·Vbus/Vbat = 1.216 @3.70V / 1.071 @4.20V)",
  "MECH/HINGE_POWER_CALC.md §0-A + HW/CHARGE_BOARD_SPEC.md §2.4", "[实测]"),
 ("362", "§7.2 限流链 表 300Ω 行",
  "1.07 / 1.18 / 1.30 A \u00b7 0.88 / 0.97 / 1.07 A",
  "T107A",
  "CC 段电池电流 1.298 / 1.437 / 1.581 A (300Ω 档 ❌ 判死 · 单 pin 0.790A)",
  "MECH/HINGE_POWER_CALC.json rilim_table (300Ω 行)", "[实测]"),
 ("363", "§7.2 限流链 表 390Ω 行",
  "0.82 / 0.91 / 1.00 A \u00b7 0.67 / 0.75 / 0.82 A",
  "T082A",
  "CC 段电池电流 0.997 / 1.107 / 1.216 A (390Ω 档 ❌ 判死 · 单 pin 0.608A 超 21.6%)",
  "MECH/HINGE_POWER_CALC.json rilim_table (390Ω 行)", "[实测]"),
 ("477", "§9 证据表 R_ILIM 行 (★数值不变 · 说明行★)",
  "R_ILIM 300Ω / 390Ω → IINMAX 1.07/1.18/1.30 A / 0.82/0.91/1.00 A",
  "—",
  "不变 (IINMAX = KILIM/R_ILIM 是官方输入电流上限, 与 ICHG 口径无关); 补: 现行档位 = 680Ω → IINMAX 0.47/0.52/0.57 A",
  "BQ25896 datasheet KILIM 320/355/390 AΩ [官方]", "[实测]"),
 ("524", "§10 复现脚本 打印串",
  "R_ILIM=300R->IINMAX 1.07/1.18/1.30A, CC 0.88-1.07A; 390R->0.82/0.91/1.00A, CC 0.67-0.82A",
  "T082A / T107A",
  "R_ILIM=300R->IINMAX 1.07/1.18/1.30A, CC 1.30-1.58A; 680R->0.47/0.52/0.57A, CC 0.57-0.70A",
  "MECH/HINGE_POWER_CALC.json rilim_table", "[实测]"),
]


def build_block(rows, lineno_map=None):
    out = [HEADER.format(mark=MARK), ROWS_HEAD]
    for i, r in enumerate(rows):
        r = list(r)
        if lineno_map is not None:
            r[0] = str(lineno_map[i])
        out.append("| " + " | ".join(r) + " |\n")
    out.append(ROWS_TAIL)
    return "".join(out)


def _norm(s):
    """归一化: 去掉 markdown 粗体标记与转义竖线 ⇒ 「旧值逐字」里带 ** 也能定位"""
    s = s.replace("*", "").replace("`", "").replace("\\|", "|")
    s = s.replace("|", " ").replace("\u00b7", " ").replace("\u00a0", " ")
    return re.sub(r"\s+", " ", s)


def locate_rows(rel, rows, text):
    """★按【旧值逐字】在原页里定位行号 ⇒ 前面插了内容也不会错位★"""
    lines = text.split("\n")
    nlines = [_norm(x) for x in lines]
    m = {}
    for i, r in enumerate(rows):
        if r[3] == "—":
            m[i] = r[0]
            continue
        core = _norm(r[2].lstrip("| ").strip())
        hit = None
        try:
            if core[:18] in nlines[int(r[0]) - 1]:
                hit = int(r[0])
        except (ValueError, IndexError):
            hit = None
        if hit is None:
            for L in range(len(core), 5, -1):
                pr = core[:L]
                hits = [n + 1 for n, x in enumerate(nlines) if pr in x]
                if len(hits) == 1:
                    hit = hits[0]
                    break
                if len(hits) > 1:
                    continue          # 太短不唯一 ⇒ 再缩短
        if hit is None:
            raise SystemExit("★[ISS-384] 行号定位失败 (%s row %s): core=%r"
                             % (rel, i, core[:40]))
        m[i] = hit
    return m



def main():
    targets = [
        ("HW/PCB_OUTLINE_60x15.md", PCB_ROWS),
        ("HW/J_CHG_SELECTION.md", JCHG_ROWS),
        ("HW/POWER_BUDGET_V3.md", PB_ROWS),
    ]
    line_map = {}
    for rel, rows in targets:
        p = os.path.join(ROOT, rel)
        with io.open(p, "r", encoding="utf-8") as f:
            txt = f.read()
        if MARK in txt:
            print("SKIP (已存在 ISS-384 块): %s" % rel)
            continue
        if not txt.endswith("\n"):
            txt += "\n"
            with io.open(p, "w", encoding="utf-8") as f:
                f.write(txt)
        lm = locate_rows(rel, rows, txt)
        line_map[rel] = lm
        blk = build_block(rows, lm)
        with io.open(p, "a", encoding="utf-8") as f:
            f.write(blk)
        print("APPENDED: %s  (+%d chars, %d rows)" % (rel, len(blk), len(rows)))
    mp = os.path.join(ROOT, "logs/iss384/row_lines.json")
    os.makedirs(os.path.dirname(mp), exist_ok=True)
    import json as _json
    with io.open(mp, "w", encoding="utf-8") as f:
        _json.dump(line_map, f, ensure_ascii=False, indent=1)
    print("WROTE: %s" % mp)
    return 0


if __name__ == "__main__":
    sys.exit(main())
