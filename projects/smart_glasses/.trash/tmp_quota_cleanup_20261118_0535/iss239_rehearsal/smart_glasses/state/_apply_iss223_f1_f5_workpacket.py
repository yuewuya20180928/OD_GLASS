#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-223 · 修作业包 F-1~F-5 (★精确串替换·每条必须唯一命中★)"""
import sys

P = "HW/SCHEMATIC_LANDING_WORKPACKET_V1.md"
s = open(P, encoding="utf-8").read()
orig_len = len(s)

EDITS = []


def E(old, new, tag):
    EDITS.append((old, new, tag))


# ═══════════════════════════════════════════════════════════════ F-1 (d2 真源)
E(
    "④ 真修法在哪个真源: ★**`state/gen_netlist.py`** ★**BAT_DET 段的 4 条 `add()`** "
    "(★`R_BAT_DET_1` / `R_BAT_DET_2` / `C_DET_BAT` ×2 行: 改 `dnp` + `value` + `note`★) + "
    "★**`state/gen_netlist_pins.py`** ★**同 4 行的 `dnp` + `J_SOM_P1.pin38` 那行的 `note`** ⇒ "
    "★**★注意: d2 与 d1 不同 —— 分压比是写死在生成器里的, 不在 `HW/SCHEMATIC_V1_SPEC.json` 里 ⇒ "
    "真源 = 生成器, 不是 SPEC.json★**",

    "④ 真修法在哪个真源: ★**`state/gen_netlist.py`** ★**BAT_DET 段的 4 条 `add()`** "
    "(★`R_BAT_DET_1` / `R_BAT_DET_2` / `C_DET_BAT` ×2 行: 改 `value` + `note`★) + "
    "★**★★★F-1 订正 (ISS-223 · 2026-11-16): `dnp` 这一列的真源是 `state/gen_netlist.py` 的 "
    "`DEMO_DNP` 白名单 (L315-L322), 【不是】那几条 `add()` 的 dnp 参数** —— "
    "`add()` 末尾会拿白名单【无条件覆盖】`dnp=\"DNP\"` 并往 note 前缀 `★DNP: <理由> | `; "
    "而 `R_BAT_DET_1` / `R_BAT_DET_2` / `C_DET_BAT` 三颗【全在】白名单里 ⇒ "
    "★★只改 `add()` 的 dnp 参数 = 改了等于没改 (重跑生成器会被打回 DNP)★★****★ + "
    "★**`state/gen_netlist_pins.py`** ★**`J_SOM_P1.pin38` 那行的 `note`** "
    "(★F-1 订正: 脚表的 `dnp` 列是从网表 CSV 派生的 (`state/gen_netlist_pins.py` L230 "
    "`\"dnp\": cell(m, \"dnp\")`) ⇒ 不用单独改, 网表 CSV 一重生成就跟着变★) ⇒ "
    "★**★注意: d2 与 d1 不同 —— 分压比是写死在生成器里的, 不在 `HW/SCHEMATIC_V1_SPEC.json` 里 ⇒ "
    "真源 = 生成器, 不是 SPEC.json★**",
    "F-1/§2.2④",
)

E(
    "⑤ 改法 (逐字值): ★**`state/gen_netlist.py`** BAT_DET 段: `R_BAT_DET_1` 那条 `add()` 的 `dnp` 由 "
    "`\"DNP\"` → ★`\"必装\"`★、`value` 由 `\"1M ±1%\"` → ★`\"2.0M ±1%\"`★ "
    "(★按 V-3 裁决; 若裁 D 档则 `\"2.0M ±1%\"` 不变、下臂改 `\"1.0M ±1%\"`★) · "
    "`R_BAT_DET_2` 那条 `add()` 的 `dnp` → ★`\"必装\"`★、`value` 由 `\"1M ±1%\"` → ★`\"1.2M ±1%\"`★ · "
    "`C_DET_BAT` 两条 `add()` 的 `dnp` → ★`\"必装\"`★ (★两只一起改, 不许只改一半★) · "
    "4 条的 `note` 里 `\"★DNP: 同上\"` → 写全的句子",

    "⑤ 改法 (逐字值): ★**★★★F-1 订正 (ISS-223 · 2026-11-16) —— 改法分两层, `dnp` 与 `value` "
    "的真源不是同一个地方, 照旧改法【落不了地】****★ "
    "★**第 1 层 (`dnp` 列 · 唯一能让 DNP 变成必装的改法)**: ★**改 `state/gen_netlist.py` 的 "
    "`DEMO_DNP` 白名单 (L315-L322)**: ★**把 `\"R_BAT_DET_1\"` / `\"R_BAT_DET_2\"` / "
    "`\"C_DET_BAT\"` 三个条目从白名单里删掉** (★或把覆盖逻辑改成\"只有当 `add()` 没显式给 dnp "
    "时才套白名单\"★) ⇒ ★★只改 `add()` 的 dnp 参数会被 `add()` 末尾的白名单覆盖打回 DNP★★ ★ "
    "★**第 2 层 (`value` / `note` · 仍在 `add()` 里 · 原改法有效)**: ★**`state/gen_netlist.py`** "
    "BAT_DET 段: `R_BAT_DET_1` 那条 `add()` 的 `value` 由 `\"1M ±1%\"` → ★`\"2.0M ±1%\"`★ "
    "(★按 V-3 裁决; 若裁 D 档则 `\"2.0M ±1%\"` 不变、下臂改 `\"1.0M ±1%\"`★) · "
    "`R_BAT_DET_2` 那条 `add()` 的 `value` 由 `\"1M ±1%\"` → ★`\"1.2M ±1%\"`★ · "
    "`C_DET_BAT` 两条 `add()` 的 `value` 保持 `\"100nF ±10%\"` 不动 (★只跟着第 1 层改 dnp, "
    "两只一起改, 不许只改一半★) · 4 条的 `note` 写全的句子 "
    "(★F-1 订正: 那个 `★DNP: 同上 | ` 前缀是 `DEMO_DNP` 白名单拼上去的 "
    "(★`add()` 末尾 `note = f\"[{ref}] ★DNP: {DEMO_DNP[ref]} | \" + note`★) ⇒ 第 1 层改完它自动消失, "
    "句子写进 `add()` 的 note 本体里★)",

    "F-1/§2.2⑤",
)

E(
    "⇒ ★**`state/gen_netlist_pins.py`**: 同 4 行 `dnp` 由 `\"DNP\"` → ★`\"必装\"`★; "
    "★**`J_SOM_P1.pin38` 那行的 `note` 由",
    "⇒ ★**`state/gen_netlist_pins.py`**: ★**F-1 订正: 脚表的 `dnp` 列是从网表 CSV 派生的 "
    "(`state/gen_netlist_pins.py` L230 `\"dnp\": cell(m, \"dnp\")`) ⇒ 不用单独改, "
    "网表 CSV 一重生成就跟着变★**; 只改 ★**`J_SOM_P1.pin38` 那行的 `note` 由",
    "F-1/§2.2⑤-pins",
)

# ═══════════════════════════════════════════════════════════════ F-2 (J_CHG 行真源)
E(
    "| ★**`state/gen_netlist.py` 的 `J_CHG` 那条 `add()` 的 `note`** ★ | `每 pin ≤0.75A` | "
    "★`每 pin **额定 0.75A / 降额后工作上限 0.50A** (ISS-099 FH12-10S-0.5SH(55)); "
    "载流 pin = pin1/pin2 (或裁决后 pin1/2/9/10)`★ |",

    "| ★**★★★F-2 订正 (ISS-223 · 2026-11-16): `J_CHG` 那条 NET 行 (表A L497, `net=BAT_CHG`, "
    "`node1=U_CHG pin14`, `node2=J_CHG pin1`) 的真源【不是】`state/gen_netlist.py` 的 `add()`, "
    "而是 ★`state/p10_rows.json`★ (★`gen_netlist.py` L1366-L1370 逐字: 「充电板整页的行数据由 "
    "`state/p10_rows.json` 提供」⇒ 改 `gen_netlist.py` 对这行【完全无效】★★) ⇒ "
    "★**而且第 2 栏的字面值已经过期: ISS-220 已把 `p10_rows.json` 这条的 note 改成 1.216 真值口径 "
    "⇒ 照第 2 栏改 = 把已落的真值改回去****★ "
    "★**`state/p10_rows.json`** 里 `ref=J_CHG` 且 `net=BAT_CHG` 那条的 `note`** ★ | "
    "★(旧) `每 pin ≤0.75A` ⇒ ★**现状已是 `每 pin 额定 0.75A / 工作上限 0.50A "
    "(ISS-099 FH12-10S-0.5SH(55)); 按 ICHG/IIN = 1.216 真值, 390Ω 档单 pin = 0.608A > 0.50A "
    "工作上限 21.6% ⇒ 档位待 V-4 裁决` (★ISS-220 已落 · 见 `HW/SCHEMATIC_LANDING_V1_LANDED.md` "
    "§1.4★) ⇒ ★**剩余待改只有【裁决后把 390Ω 换成终值档 + 载流 pin 列表】**★ ★ |",

    "F-2/§2.10⑤",
)

# ═══════════════════════════════════════════════════════════════ F-3 (判据 5 同趟改)
E(
    "| 8 | ★`HW/check_netlist_selfconsistency.py`★ | `EXPECT` 的 `d1_spec_b01_imp` / "
    "`d1_spec_b02_imp` | ★**落表那趟按 d1 改成 2.2k/1.8V 口径 (★与字段拆分互不冲突★) ★** |",

    "| 8 | ★`HW/check_netlist_selfconsistency.py`★ | `EXPECT` 的 `d1_spec_b01_imp` / "
    "`d1_spec_b02_imp` | ★**落表那趟按 d1 改成 2.2k/1.8V 口径 (★与字段拆分互不冲突★) ★** |\n"
    "| ★**9** ★ | ★**`state/check_netlist.py`**★ | ★**判据 5** (★`spec_imp = {c[\"id\"]: "
    "(c.get(\"imp\") or c.get(\"z_diff\") or \"\") for c in spec[\"connections\"]}`★) | "
    "★**★★★F-3 订正 (ISS-223 · 2026-11-16): 第 1/2 行把 A 组 20 条的 `imp` 清空【必须】同趟改这一行"
    "****★ ⇒ ★**只清空 `imp` 不改判据 5 ⇒ `want` 变空 ⇒ 那 20 行被 `continue` 跳过 ⇒ "
    "判据覆盖从 20 行【静默掉到 0 行】(判据被悄悄废掉, 而门禁仍然是绿的)★** ⇒ "
    "★**改成 `imp or z_diff` 之后覆盖行数一条没少 (仍按 A 组 NET 行逐条对照)★★ "
    "★**已落: ISS-223 落表第 2 批已把判据 5 的比对源改成 `imp or z_diff` (实测 `check_netlist.py` "
    "判据 5 输出仍是 \"A 组阻抗逐条对照规格 (20 条 net)\" ⇒ 覆盖 20 行没少)★ ★** |",

    "F-3/§4.A⑤表-第9行",
)

E(
    "| ★`python3 state/check_netlist.py`★ | ★**0** ★ | ★**\"✅ 全过 — 原理图 V1.1 可进交叉评审\"** ★ | "
    "★**该脚本的判据 5 是 \"A 组阻抗必须与规格逐字一致\" ⇒ A 组 20 条 NET 行的 value 仍是 "
    "`100Ω ±10%`, 与 `z_diff` 逐字一致 ⇒ 判据仍成立 (★拆字段不改变任何 A 组产物★) ★** |",

    "| ★`python3 state/check_netlist.py`★ | ★**0** ★ | ★**\"✅ 全过 — 原理图 V1.1 可进交叉评审\"** ★ | "
    "★**该脚本的判据 5 是 \"A 组阻抗必须与规格逐字一致\" ⇒ A 组 20 条 NET 行的 value 仍是 "
    "`100Ω ±10%` (★产物逐字节不变★) ⇒ ★★但判据 5 的【比对源】必须同趟从\"只读 `imp`\"改成 "
    "\"读 `imp` 或 `z_diff`\" (★见上表第 9 行 · F-3★) ⇒ 否则 `want` 变空、那 20 行被 `continue` "
    "跳过 ⇒ ★**判据覆盖 20 行 → 0 行, 而门禁仍然是绿的 (静默失效)★★ ★",

    "F-3/§4.A⑤表-结果表",
)

E(
    "⇒ ★**★\"字段真的拆开了\"这一条目前没有独立 R# ⇒ 落表那趟建议在 "
    "`state/check_netlist.py` 加一条\"A 组 20 条必须有 `z_diff` 且 `imp` 为空\"的断言 "
    "(★归落表那趟, 本单不改 check_netlist.py★)★★**",

    "⇒ ★**★\"字段真的拆开了\"这一条目前没有独立 R# ⇒ ★**ISS-223 落表第 2 批已把 "
    "`state/check_netlist.py` 判据 5 的比对源改成 `imp or z_diff` (★F-3 的同趟改 · 已落 · 见 "
    "`HW/SCHEMATIC_LANDING_V1_LANDED.md` §1.2★) ⇒ 实测覆盖行数仍是 20 条 net, 一条没少 ★** ⇒ "
    "★**仍缺一条【加强型】独立断言: \"A 组 20 条必须 `z_diff` 非空 且 `imp` 为空\" ⇒ 留给第 3 批 "
    "(★本单不加: 它与 §4.A 的字段基建一起定, 免得把这一批的 diff 搅大★)★★**",

    "F-3/§4.A⑦",
)

# 同批订正: §4.A ⑤ 表第 3/4 行的 B-21/B-22 imp 目标值 (与 V-1 裁定值对齐)
E(
    "| 3 | ★`HW/SCHEMATIC_V1_SPEC.json`★ | `connections[40]` (B-21) | ★`imp` → "
    "`\"22Ω 串阻 (源端匹配; 差分线 90Ω±15% 受控阻抗)\"`; 新增 "
    "`\"z_diff\": \"90Ω ±15% 受控阻抗\"` ★ |",
    "| 3 | ★`HW/SCHEMATIC_V1_SPEC.json`★ | `connections[40]` (B-21) | ★**同批订正 "
    "(ISS-223 · 2026-11-16)**: 原文写的 `\"22Ω 串阻 (源端匹配; 差分线 90Ω±15% 受控阻抗)\"` "
    "与 V-1 裁定值不一致 ⇒ NET 行会与器件行 L431 的 `22Ω ±1%` 对不上 ⇒ ★**改成 `\"22Ω ±1%\"` "
    "(与器件行逐字一致 = \"同一颗器件两个阻值\"这条缺陷的正解)★**; `z_diff` = "
    "`\"90Ω ±15% 受控阻抗\"` (★**已落** · ISS-220 建字段 + ISS-223 落值★) ★ |",
    "同批订正/§4.A⑤表-第3行",
)

E(
    "| 4 | ★`HW/SCHEMATIC_V1_SPEC.json`★ | `connections[41]` (B-22) | ★同上 ★ |",
    "| 4 | ★`HW/SCHEMATIC_V1_SPEC.json`★ | `connections[41]` (B-22) | ★同上 "
    "(★`imp` → `\"22Ω ±1%\"`★) ★ |",
    "同批订正/§4.A⑤表-第4行",
)

# ═══════════════════════════════════════════════════════════════ F-4 (皮肤温度结论作废)
E(
    "| ★**`state/gen_netlist.py` 的 `R_ILIM` 那条 `add()` 的 `note`** ★ | "
    "`★★V1.7 按 ISS-091 结构核算定 **470Ω**` | ★删掉该句 (或明确标 \"已作废\")★ "
    "(★见 #8★)★ |",

    "| ★**`state/gen_netlist.py` 的 `R_ILIM` 那条 `add()` 的 `note`** ★ | "
    "★`★★V1.7 按 ISS-091 结构核算定 **470Ω**` ★ | ★删掉该句 (或明确标 \"已作废\")★ "
    "(★见 #8★)★ |\n"
    "| ★**`HW/PCB_OUTLINE_60x15.md` L149 / L190 + `MECH/hinge_power_calc.json` 的 `rilim_table`** ★ | "
    "★**`皮肤温度保守口径 42.14°C (<43°C 红线)` + `42.14°C 只剩 0.86°C 余量 ⇒ 不能同时再抬电流`** ★ | "
    "★**★★★F-4 订正 (ISS-223 · 2026-11-16): 这条结论是按【错的 0.822 系数】算的 ⇒ 方向修正后"
    "【作废】, 那个温度数必须重算****★: 按 1.216 系数, 电芯内阻发热从 114mW 升到 **148mW** "
    "(0.10Ω × 1.216²) ⇒ ★**\"42.14°C\" 现在是\"无有效数字\", 不是\"还有 0.86°C 余量\"**★ ⇒ "
    "★**本单不编新温度数 (没有 MECH 的热模型就不许编) ⇒ 已派给 mech-lead 用 "
    "`MECH/HINGE_POWER_CALC.md` 重算 (ISS-091 地界) · 见 `HW/SCHEMATIC_LANDING_V1_LANDED.md` §1.4 "
    "与交接单 B5 第 8 条 ★** ⇒ ★**网表侧已经在 `state/gen_netlist.py` 的 `R_ILIM` note 里写了"
    "\"该温度数不可信\"的作废标记 (ISS-220 已落) ⇒ 这两处是【同一件事的两个副本】, 必须一起改 ★ |",

    "F-4/§2.10⑤",
)

# ═══════════════════════════════════════════════════════════════ F-5 (白名单↔§7 对账)
E(
    "★**② 落表那趟跑一次双向对账 (★人工, 但要有结论写进交卷★)**: ★**§7 清单里的每一行都必须 "
    "board=CHG_BOARD** (★现状 `CHARGE_BOARD_SPEC.md` §7 的清单每一行 `board` 列都写 `CHG_BOARD`, "
    "★共 80 行, ★但 §7.1 的对账表里\"现行网表引用 80 行\"已过期 —— 见 #6★)★**; "
    "★**网表里 board=CHG_BOARD 的每一颗都必须在 §7 清单里** ⇒ ★**③ 可选加固",

    "★**② ★★★F-5 订正 (ISS-223 · 2026-11-16): 双向对账【在现状下不可能过】, "
    "不许把它当本批的落表判据 ★**★ —— ★**[实测] 今日复算 (`HW/CHARGE_BOARD_SPEC.md` §7 的 CSV 块 "
    "× `HW/netlist_v1.csv` 逐行对拍)**: §7 共 80 行, `board` 分布 = CHG_BOARD **64** / HINGE 11 / "
    "MAIN_PCB 4 / **1 行解析错位** (★`U_CHG` 那行的 note 里有未加引号的逗号 ⇒ board 列被解析成 "
    "`\" 0.8mm max height\"` ⇒ §7 这个 CSV 块【本身就不是合法 CSV】★) ⇒ "
    "★**§7 里有而网表里没有的位号 = 16 个** (★9 个 §7 侧 CHG_BOARD: `C_VBUS_BULK` / `NC` / `R_TS1` "
    "/ `R_VDET_TOP` / `R_VDET_BOT` / `USB_CC1` / `USB_CC2` / `USB_D_P_CHG` / `USB_D_N_CHG`; "
    "+ 7 个 §7 侧 HINGE/MAIN_PCB/错位: `BAT_CHG` / `J_CHG` / `R_TS2` / `R_NTC_BAT` / `CHG_STAT` / "
    "`PWR_GOOD` / `U_CHG`★) ⇒ ★**网表里有而 §7 里没有的 CHG_BOARD 位号 = 15 个** (★`C_VBUS_GND` / "
    "`C_VBUS_OUT` / `D_CHG_LED` / `D_TVS_VBUS` / `NET_BAT_PROT` / `NET_CHG_STAT` / `NET_PWR_GOOD` / "
    "`NET_TS_BAT` / `NET_USB_CC1` / `NET_USB_CC2` / `Q_CHG_LED` / `R_CHG_LED` / `R_PU_CHG_STAT` / "
    "`R_TS_TOP` / `TP_CHG_STAT`★) ⇒ ★**⇒ §7 与网表是两个版本, 对账的起点就不成立 ⇒ 本批【不做】"
    "对账, 归 #6/补差C 的【充电板整页】那一趟 (★那一趟要同时把 §7 的 CSV 块修成合法 CSV + "
    "把 §7 整体对齐到网表★)**★ ⇒ ★**所以 §7 清单里的每一行都必须 board=CHG_BOARD** (★现状 "
    "`CHARGE_BOARD_SPEC.md` §7 的清单每一行 `board` 列都写 `CHG_BOARD`, ★共 80 行, ★但 §7.1 的"
    "对账表里\"现行网表引用 80 行\"已过期 —— 见 #6★)★**; ★**网表里 board=CHG_BOARD 的每一颗都必须在 "
    "§7 清单里** (★★这一句【只作第 3 批充电板整页的验收项】, 不是本批的翻面判据★★) ⇒ ★**③ 可选加固",

    "F-5/§3.5⑤",
)

# ═══════════════════════════════════════════════════════════════ §9 修订记录 (追加)
E(
    "## 8. ★★落表状态 (★ISS-220 第 1 批 · 2026-11-16 · 硬件总工执行★) ★★",
    """## 8. ★★落表状态 (★ISS-220 第 1 批 · 2026-11-16 · 硬件总工执行★) ★★""",
    "anchor-§8",
)


# ── F-2 同批补: §2.10 d10 与 §4.C 补差C 的 ④ 栏 (J_CHG 那条 add() 的 note 归属) ──
E(
    "⇒ ★**网表侧 `state/gen_netlist.py` 的 `R_ILIM` 两条 `add()` 的 `value` + `J_CHG` 那条 `add()` 的 `note`** ⇒",
    "⇒ ★**网表侧 `state/gen_netlist.py` 的 `R_ILIM` 两条 `add()` 的 `value` + "
    "★**★★★F-2 订正 (ISS-223 · 2026-11-16): `J_CHG` 那条 NET 行的 `note` 【不在】`state/gen_netlist.py` "
    "的 `add()` 里, 而在 ★`state/p10_rows.json`★ (★`gen_netlist.py` L1366-L1370 逐字: 「充电板整页的行数据由 "
    "`state/p10_rows.json` 提供」⇒ 改 `gen_netlist.py` 对这行【完全无效】★★)****★ ⇒",
    "F-2/§2.10④",
)

E(
    "⇒ ★**② `state/gen_netlist.py`** ★**`R_ILIM` 两条 `add()` 的 `value` + `J_CHG` 那条 `add()` 的 `note` (载流 pin 集合)★** ⇒",
    "⇒ ★**② `state/gen_netlist.py`** ★**`R_ILIM` 两条 `add()` 的 `value`** + "
    "★**★★F-2 订正 (ISS-223 · 2026-11-16): `J_CHG` 那条 NET 行 (载流 pin 集合写在它的 `note` 里) 的真源是 "
    "★`state/p10_rows.json`★, 【不是】`state/gen_netlist.py` 的 `add()` (★`gen_netlist.py` L1366-L1370 逐字: "
    "「充电板整页的行数据由 `state/p10_rows.json` 提供」⇒ 改 `gen_netlist.py` 对这行【完全无效】★★)****★ ⇒",
    "F-2/§4.C④",
)

fails = []
for old, new, tag in EDITS:
    n = s.count(old)
    if n != 1:
        fails.append((tag, n))
        print(f"✗ [{tag}] 命中 {n} 次 (要求恰好 1)")
        continue
    s = s.replace(old, new, 1)
    print(f"✅ [{tag}] 替换成功")

if fails:
    print("\n★★有替换未唯一命中, 未落盘 ★★")
    sys.exit(1)

open(P, "w", encoding="utf-8").write(s)
print(f"\n✅ 已写 {P} · {orig_len} → {len(s)} 字节")
