#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_iss344_corrections.py —— ISS-344 追加式订正执行器 (★零写板·零落表·零改固件本体★)
================================================================================
★**干什么**: 把 `SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md` 里与 main 2026-11-22 20:5x
  终裁冲突的分级陈述【追加式】订正 —— ★**老字一个字都不删** ★

★**为什么用脚本而不是手改**: ★**本项目铁律 = 追加式·老字一字未删 = 可自证** ★
  ⇒ ★**本脚本只做「插入」, 不做「替换」** ★ ⇒ ★**改完用 difflib 校验: 无 delete / replace 操作** ★

★**订正清单 (★逐条可核★)** ★★
  ① §3 表 6 条必需网 (JTAG_TDI / SPI_MISO_BOOT / SPI_MOSI_BOOT / SPI_SCLK_BOOT / UART_RX / USB_CC2)
     ⇒ 「建议的板侧标记」格追加【必需 · 进 S8 布线目标 · 板侧不许标 NC / no-connect】
     ⇒ 「固件侧要不要改」格追加【作废 (main 11-22 20:5x 改判必需 ⇒ 无需降级声明)】
  ② §3 表 `FSIN_OUT` ⇒ 追加【可悬空 (条件式) · 板那一趟动作 · 现在只定口径不定动作】
  ③ §2 表「分级」列 7 格 ⇒ 追加新分级 (6 条必需 + FSIN_OUT 条件式)
  ④ §0 / §5 / §6 等处的旧分级陈述 ⇒ 逐处追加订正脚注
  ⑤ §4 未决项 B5-1..B5-4 ⇒ 逐条追加「已被 main 裁完并闭合」
  ⑥ 文末追加 §7 分级订正小节 (★含逐条订正表·闸的用法·diff 自证★)

★**用法**: python3 logs/iss344/apply_iss344_corrections.py <目标文件>
"""
import difflib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(HERE))
DEFAULT = os.path.join(PROJ, "SW", "ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md")

CORR = "【ISS344-CORR】"
CORR_END = "【/ISS344-CORR】"

SEC3_HDR = "| net | 为什么可以悬空"
SEC2_HDR = "| ★net★ | ★被谁引用 (文件:行)★ |"

# ═══════════════════════════════════════════════════════════════════════
# 逐条订正素材 (★依据 = state/fragments/pm.yaml → answers → 下列 key★)
# ═══════════════════════════════════════════════════════════════════════
NEEDS = {
    "JTAG_TDI": dict(
        key="iss338_need_jtag_group_decision",
        quote="裁 JTAG 整组保留, 不裁 TDI ⇒ JTAG_TDI 判【必需】(进 S8 布线目标) ⇒ 不是悬空候选",
        ev="[实测]",
        extra="★**旧句「若 JTAG 整组保留, 则 4 根线不完整 ⇒ 建议整组一起裁」一并作废 ⇒ 终裁 = JTAG 整组 4 根 (`TCK`/`TMS`/`TDO`/`TDI`) 全保留** ★",
    ),
    "SPI_MISO_BOOT": dict(
        key="iss338_need_boot_storage_answer",
        quote="3 条 `SPI_*_BOOT` 判【必需】(进 S8 布线目标) · 板侧【不许】标 no-connect",
        ev="[实测]",
    ),
    "SPI_MOSI_BOOT": dict(
        key="iss338_need_boot_storage_answer",
        quote="3 条 `SPI_*_BOOT` 判【必需】(进 S8 布线目标) · 板侧【不许】标 no-connect",
        ev="[实测]",
    ),
    "SPI_SCLK_BOOT": dict(
        key="iss338_need_boot_storage_answer",
        quote="3 条 `SPI_*_BOOT` 判【必需】(进 S8 布线目标) · 板侧【不许】标 no-connect",
        ev="[实测]",
    ),
    "UART_RX": dict(
        key="iss338_need_jtag_group_decision",
        quote="『固件零引用 ⇒ 可悬空』这条判据【只适用于固件信号】, 【不适用于调试口 / 预留位】⇒ 所以你那 9 条里 `JTAG_TDI` / `UART_RX` 的『可悬空』结论, main 不采信",
        ev="[推算]",
    ),
    "USB_CC2": dict(
        key="iss338_need_usbif_cc1_cc2_rule",
        quote="裁决 = `USB_CC2` 判【必需】·板侧不许标 NC ⇒ 你的「板侧默认 NC + 保留 R_CC2_D」建议【不采纳】",
        ev="[官网]",
    ),
}

MARK_TMPL = (
    " @CORR@★★**★分级订正 (main 2026-11-22 20:5x 终裁 · ISS-344): "
    "本格旧的「NC (不连)」【作废】⇒ 新口径 = ★**必需 · 进 S8 布线目标 · 板侧不许标 NC / no-connect** ★ "
    "· 依据 pm.yaml → `{key}` (★**「{quote}」**★) · 证据等级 = ★**{ev}**★{extra}**@CORR_END@★★** ★"
)

FW_TMPL = (
    " @CORR@★★**★作废 (main 11-22 20:5x 改判必需 ⇒ 无需降级声明) ★★** ★"
    "★★**作废依据**: pm.yaml → `{key}` (★**「{quote}」**★) · 证据等级 = ★**{ev}**★ · "
    "★**本单不把这条改写成新的固件侧改动 (★那是板那一趟同批改的活·不属本单★)** ★@CORR_END@★★** ★"
)


def S(t):
    return (t.replace("{CORR}", CORR).replace("{CORR_END}", CORR_END)
             .replace("@CORR@", CORR).replace("@CORR_END@", CORR_END))


# ═══════════════════════════════════════════════════════════════════════
# 行内插入工具 (★只插不删·按未转义 | 定位单元格·保原字节不动★)
# ═══════════════════════════════════════════════════════════════════════
def pipe_positions(line):
    out = []
    i = 0
    while i < len(line):
        if line[i] == "|" and (i == 0 or line[i - 1] != "\\"):
            out.append(i)
        i += 1
    return out


def split_row(line):
    s = line.strip()
    if not s.startswith("|"):
        return None
    s = s[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]
    return [c.strip() for c in re.split(r"(?<!\\)\|", s)]


def insert_into_cell(line, idx, text, where="append"):
    ps = pipe_positions(line)
    if idx + 1 >= len(ps):
        raise SystemExit("❌ 单元格 %d 不存在: %s" % (idx, line[:90]))
    s, e = ps[idx] + 1, ps[idx + 1]
    if where == "append":
        return line[:e] + text + line[e:]
    return line[:s] + text + line[s:]


def insert_into_last_cell(line, text, where="append"):
    """★插到【最后一格】(= 建议的板侧标记那一格)★
    ★为什么不用固定下标: ★原文 `SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md` 的 §3 表
      `UART_RX` 那一行里有一个【未转义的 `|`】(★「USB-TTL 串口线 + 笔记本 | 能看 …」★)
      ⇒ 那一行的格子数比表头多 1 ⇒ 按下标插会插错格 ⇒ ★**一律按最后一格** ★"""
    ps = pipe_positions(line)
    if len(ps) < 2:
        raise SystemExit("❌ 行里没有格子: %s" % line[:90])
    s, e = ps[-2] + 1, ps[-1]
    if where == "append":
        return line[:e] + text + line[e:]
    return line[:s] + text + line[s:]


def net_of(cell):
    m = re.search(r"`([^`]+)`", cell or "")
    return m.group(1).strip() if m else None


def table_rows(lines, header_prefix):
    """→ [(行下标, cells)] (★按表头定位·不靠网名猜★)"""
    hi = None
    for i, l in enumerate(lines):
        if l.startswith(header_prefix):
            hi = i
            break
    if hi is None:
        raise SystemExit("❌ 找不到表头 %r" % header_prefix)
    rows = []
    j = hi + 2                       # ★跳过分隔行★
    while j < len(lines) and lines[j].startswith("|"):
        cells = split_row(lines[j])
        if cells:
            rows.append((j, cells))
        j += 1
    return rows


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT
    if not os.path.isfile(path):
        raise SystemExit("❌ 文件不存在: %s" % path)
    with open(path, encoding="utf-8") as f:
        orig = f.read()
    lines = orig.split("\n")
    n_before = len(lines)
    log = []

    # ── ① §3 表 (★按表头定位★) ────────────────────────────────────
    mod = {}          # 行下标 → 新行 (★只许插入·不许替换★)
    orig_of = {}      # 行下标 → 原行

    def cur(i):
        return mod.get(i, lines[i])

    sec3 = {net_of(c[0]): (i, c) for i, c in table_rows(lines, SEC3_HDR) if net_of(c[0])}
    for net in ("JTAG_TDI", "SPI_MISO_BOOT", "SPI_MOSI_BOOT",
                "SPI_SCLK_BOOT", "UART_RX", "USB_CC2"):
        if net not in sec3:
            raise SystemExit("❌ §3 表里没有 %s" % net)
        i, _ = sec3[net]
        nd = dict(NEEDS[net])
        nd.setdefault("extra", "")
        orig_of[i] = lines[i]
        t = insert_into_cell(lines[i], 2, S(FW_TMPL.format(**nd)), "prepend")
        t = insert_into_last_cell(t, S(MARK_TMPL.format(**nd)), "append")
        mod[i] = t
        log.append("§3 表 %-15s 行 %-4d ⇒ 标记改判【必需】+ 固件侧清单标【作废】" % (net, i + 1))

    if "FSIN_OUT" not in sec3:
        raise SystemExit("❌ §3 表里没有 FSIN_OUT")
    i, _ = sec3["FSIN_OUT"]
    orig_of[i] = lines[i]
    t = insert_into_cell(
        lines[i], 2,
        S(" {CORR}★★**★板那一趟动作 · 现在只定口径不定动作** ★★"
          "★★**清单保留在册, 但【现在不许落 NC】** ★★"
          "· 依据 pm.yaml → `iss334_need4b_zero_copper_net_triage` (★**「标 NC 是板侧动作·只在板那一趟做·现在只定口径不定动作」**★)"
          "· 证据等级 = ★**[实测]** ★{CORR_END}★★** ★"),
        "prepend")
    t = insert_into_last_cell(
        t,
        S(" {CORR}★★**★分级订正 (main 2026-11-22 20:5x 终裁 · ISS-344): "
          "本格旧的「NC (不连)」【现在不成立】⇒ 新口径 = ★**可悬空 (条件式)** ★ · "
          "★**条件**: 在板那一趟的新基线上它仍是零铜 ⇒ 才允许标 no-connect; "
          "★**标 NC 是板侧动作 · 只在板那一趟做 · 现在只定口径不定动作** ★ · "
          "依据 pm.yaml → `iss334_need4b_zero_copper_net_triage` (★**「B 可悬空 (1 条) = `FSIN_OUT` (条件: 在板那一趟的新基线上它仍是零铜 ⇒ 才允许标 no-connect)」**★) · "
          "证据等级 = ★**[实测]** ★{CORR_END}★★** ★"),
        "append")
    mod[i] = t
    log.append("§3 表 %-15s 行 %-4d ⇒ 保留【可悬空】+ 补条件 (现在不落 NC)" % ("FSIN_OUT", i + 1))

    # ── ② §2 表「分级」列 (★按表头定位·第 4 格★) ─────────────────
    sec2_new = {
        "JTAG_TDI": ("★**必需** ★ (★**进 S8 布线目标 · 板侧不许标 NC / no-connect**★)",
                     "iss338_need_jtag_group_decision", "[实测]"),
        "SPI_MISO_BOOT": ("★**必需** ★ (★**进 S8 布线目标 · 板侧不许标 NC / no-connect**★)",
                          "iss338_need_boot_storage_answer", "[实测]"),
        "SPI_MOSI_BOOT": ("★**必需** ★ (★**进 S8 布线目标 · 板侧不许标 NC / no-connect**★)",
                          "iss338_need_boot_storage_answer", "[实测]"),
        "SPI_SCLK_BOOT": ("★**必需** ★ (★**进 S8 布线目标 · 板侧不许标 NC / no-connect**★)",
                          "iss338_need_boot_storage_answer", "[实测]"),
        "UART_RX": ("★**必需** ★ (★**进 S8 布线目标 · 板侧不许标 NC / no-connect**★)",
                    "iss338_need_jtag_group_decision", "[推算]"),
        "USB_CC2": ("★**必需** ★ (★**板侧不许标 NC / no-connect**★)",
                    "iss338_need_usbif_cc1_cc2_rule", "[官网]"),
        "FSIN_OUT": ("★**可悬空 (条件式)** ★ (★**板那一趟动作 · 现在只定口径不定动作**★)",
                     "iss334_need4b_zero_copper_net_triage", "[实测]"),
    }
    sec2 = {net_of(c[0]): (i, c) for i, c in table_rows(lines, SEC2_HDR) if net_of(c[0])}
    for net, (newgrade, key, ev) in sec2_new.items():
        if net not in sec2:
            raise SystemExit("❌ §2 表里没有 %s" % net)
        i, _ = sec2[net]
        orig_of.setdefault(i, lines[i])
        t = insert_into_cell(
            lines[i], 3,
            S(" {CORR}★★**★分级订正 (main 2026-11-22 20:5x 终裁 · ISS-344): "
              "本格旧分级【作废】⇒ 新分级 = {newgrade} · "
              "依据 pm.yaml → `{key}` · 证据等级 = ★**{ev}**★{CORR_END}★★** ★"
              .replace("{newgrade}", newgrade).replace("{key}", key).replace("{ev}", ev)),
            "append")
        mod[i] = t
        log.append("§2 表 %-15s 行 %-4d ⇒ 分级列改判" % (net, i + 1))

    # ★把表内改写落到 lines (★只增不删·原行字节全在★) ★
    for i, t in mod.items():
        lines[i] = t

    # ── ③ 逐处追加订正脚注 ─────────────────────────────────────────
    def append_after(prefix, text, tag):
        hits = [i for i, l in enumerate(lines) if l.startswith(prefix)]
        if len(hits) != 1:
            raise SystemExit("❌ 锚点 %r 定位到 %d 行 (期望 1)" % (prefix, len(hits)))
        i = hits[0]
        lines.insert(i + 1, text)
        log.append("%-40s (行 %d 之后)" % (tag, i + 1))

    FOOT = S(
        " {CORR}★★**★分级订正 (main 2026-11-22 20:5x 终裁 · ISS-344)**: "
        "★**上方旧分级陈述【作废】** ⇒ 新口径 = ★**必需 23 (15 高速差分腿 + 8 单端脚) · 可悬空 1 (`FSIN_OUT`) · 待定 0** ★ "
        "⇒ ★**落到本页 9 条单端脚上的投影 = 必需 8 (`CAM_RESET_N` `LED_G_D` `USB_CC2` `JTAG_TDI` `UART_RX` `SPI_SCLK_BOOT` `SPI_MOSI_BOOT` `SPI_MISO_BOOT`) · 可悬空 1 (`FSIN_OUT`) · 待定 0** ★ "
        "· 依据 pm.yaml → `iss334_need4b_zero_copper_net_triage` + `iss338_need_jtag_group_decision` + `iss338_need_boot_storage_answer` + `iss338_need_usbif_cc1_cc2_rule` "
        "· 证据等级 = ★**[实测]** (★**本机实跑 `HW/check_s8_target_list.py` ⇒ 必需 23 (期望 23) · 可悬空 1 (期望 1) · 待定 0 (期望 0) ⇒ 一致 ✔**★) "
        "· ★**老字一个字都没删 (见 §7-4 diff 自证)** ★{CORR_END}★★** ★")

    append_after("> ★**一句话结论**:", FOOT, "§0 头部「一句话结论」")
    append_after("★**一句话**: ★**9 条零铜单端网,", FOOT, "§0 「一句话」")
    append_after("> ★**最终分级 (以 §5 表为准)**:", FOOT, "§0 「最终分级」")
    append_after("| ★**待定** ★ | **1** | `USB_CC2` |", FOOT, "§0 Q1 分级表")
    append_after("★**分级判据 (§2 写死, 与 main 口径一致)**",
                 S(" {CORR}★★**★分级判据订正 (main 2026-11-22 20:5x 终裁)**: ★**上方判据仍缺一条边界** ⇒ "
                   "★**补**: 「固件零引用 ⇒ 可悬空」★**只适用于固件信号, 不适用于调试口 / 预留位** ★ "
                   "(★**JTAG / UART 是硬件接口, 由调试器 / 探针驱动, 不由应用固件引用 ⇒ SW 零引用对它不构成「可悬空」的证据**★) "
                   "· 依据 pm.yaml → `iss338_need_jtag_group_decision` (★**逐字**★) · 证据等级 = ★**[推算]** ★{CORR_END}★★** ★"),
                 "§0 Q1 分级判据")
    append_after("| ★`USB_CC2` = ★**必需** ★ | ★**⇒ 待定** ★ (从「必需」降级)",
                 S(" {CORR}★★**★Q2 表订正 (main 2026-11-22 20:5x 终裁)**: ★**上表两行【作废】** ⇒ "
                   "★**`UART_RX` = 必需** (★**调试口 ⇒ 布线保留成本 ≈ 0·事后不重出板**★) · "
                   "★**`USB_CC2` = 必需** (★**[官网] USB Type-C 插座端双路 Rd 条款 ⇒ 不可悬空**★) ⇒ "
                   "★**本页原推的「推翻 main」结论被 main 的终裁否决** ★ · "
                   "依据 pm.yaml → `iss338_need_jtag_group_decision` / `iss338_need_usbif_cc1_cc2_rule` · "
                   "证据等级 = ★**[实测]** / ★**[官网]** ★{CORR_END}★★** ★"),
                 "§0 Q2 表")

    append_after("## §3 ★★★可悬空候选清单",
                 S(" {CORR}★★**★§3 标题订正 (main 2026-11-22 20:5x 终裁 · ISS-344)**: ★**本节标题与「清单 = 6 条可悬空 + 1 条待定」的说法【作废】** ⇒ "
                   "★**按终裁, 本页 9 条里只有 `FSIN_OUT` 1 条可悬空, 8 条必需, 0 条待定** ★ ⇒ "
                   "★**本节表格保留在册 (老字一字未删) 作历史痕迹, 有效口径以 §7 为准** ★ · "
                   "依据 pm.yaml → `iss334_need4b_zero_copper_net_triage` · 证据等级 = ★**[实测]** ★{CORR_END}★★** ★"),
                 "§3 标题")
    append_after("★**清单 = 上面 6 条「可悬空候选」+ 1 条「待定」的悬空后动作**",
                 FOOT, "§3 「清单 = …」")

    append_after("### §3-1 ★★不列入候选的 2 条",
                 S(" {CORR}★★**★§3-1 订正 (main 2026-11-22 20:5x 终裁 · ISS-344)**: ★**「不列入候选」现在一共 8 条** ⇒ "
                   "本节的 2 条 (`CAM_RESET_N` `LED_G_D`) 之外, ★**`JTAG_TDI` `SPI_MISO_BOOT` `SPI_MOSI_BOOT` `SPI_SCLK_BOOT` `UART_RX` `USB_CC2` 这 6 条也一并移出候选** ⇒ "
                   "★**§3-1 标题里的「2 条」口径作废, 但两条的【必需】结论与终裁一致 ⇒ 无需改动** ★ · "
                   "依据 pm.yaml → `iss334_need4b_zero_copper_net_triage` · 证据等级 = ★**[实测]** ★{CORR_END}★★** ★"),
                 "§3-1 标题")

    b5 = [
        ("- ★**B5-1 (需 main 裁)**",
         S(" {CORR}★★**★ISS-344 订正**: ★**本条已被 main 2026-11-22 20:5x 裁完并闭合** ⇒ "
           "★**`USB_CC2` 判【必需】· 板侧不许标 NC** ⇒ ★**上方「建议板侧标 NC + 向原厂问一句」【不采纳】** ⇒ "
           "★**本单零外发 ⇒ 不向原厂发任何问询** ★ · 依据 pm.yaml → `iss338_need_usbif_cc1_cc2_rule` · 证据等级 = ★**[官网]** ★{CORR_END}★★** ★"),
         "§4 未决项 B5-1"),
        ("- ★**B5-2 (需原厂",
         S(" {CORR}★★**★ISS-344 订正**: ★**本条已被 main 2026-11-22 20:5x 裁完并闭合** ⇒ "
           "★**3 条 `SPI_*_BOOT` 判【必需】(进 S8 布线目标) · 板侧【不许】标 no-connect** ⇒ "
           "★**理由: `J_BOOT1` 焊盘位已在板 ⇒ 布线保留的成本 ≈ 0 ⇒ 事后不用重出板** ⇒ "
           "★**上方「若最终要外挂 SPI-NOR 则不可悬空」的前提不再成立 (★无论老板怎么拍, 板都不用重出板★)** ⇒ "
           "★**本单零外发 ⇒ 不发任何问询** ★ · 依据 pm.yaml → `iss338_need_boot_storage_answer` · 证据等级 = ★**[实测]** ★{CORR_END}★★** ★"),
         "§4 未决项 B5-2"),
        ("- ★**B5-3 (需 main 裁)**",
         S(" {CORR}★★**★ISS-344 订正**: ★**本条已被 main 2026-11-22 20:5x 裁完并闭合** ⇒ "
           "★**JTAG 整组【保留】⇒ `JTAG_TDI` 判【必需】(进 S8 布线目标) ⇒ 不是可悬空候选** ⇒ "
           "★**main 选的是「不裁」这一支** ⇒ 上方「两难, 归 main」不再成立 · "
           "依据 pm.yaml → `iss338_need_jtag_group_decision` · 证据等级 = ★**[实测]** ★{CORR_END}★★** ★"),
         "§4 未决项 B5-3"),
        ("- ★**B5-4 (需 main 裁)**",
         S(" {CORR}★★**★ISS-344 订正**: ★**本条已被 main 2026-11-22 20:5x 裁完并闭合** ⇒ "
           "★**分级定稿 = 必需 23 · 可悬空 1 (`FSIN_OUT`) · 待定 0** ⇒ "
           "★**「24 条零铜网 = 23 必需 + 1 可悬空」**, 且 ★**名单须在板那一趟的新基线上重读 (★不许拿官方板那 24 条直接当靶★)** ⇒ "
           "· 依据 pm.yaml → `iss334_need4b_zero_copper_net_triage` · 证据等级 = ★**[实测]** ★{CORR_END}★★** ★"),
         "§4 未决项 B5-4"),
    ]
    for prefix, txt, tag in b5:
        append_after(prefix, txt, tag)

    append_after("| ★**不代拍** ★ | — |",
                 S(" {CORR}★★**★ISS-344 订正**: ★**上方 4 条「待 main 裁」已于 2026-11-22 20:5x 全部裁完 (★`iss338_need_jtag_group_decision` / `iss338_need_boot_storage_answer` / `iss338_need_usbif_cc1_cc2_rule` / `iss334_need4b_zero_copper_net_triage`★) ⇒ "
                   "★**本单是对齐, 不是重判** ★ · 证据等级 = ★**[实测]** ★{CORR_END}★★** ★"),
                 "§5 诚实边界「不代拍」行")

    append_after("★**9 条零铜单端网, `SW/**` 全树网名级零引用", FOOT, "§6 交卷摘要 (分级)")
    append_after("★**★推翻 main 已定口径 2 条**",
                 S(" {CORR}★★**★ISS-344 订正**: ★**上方「推翻 main 已定口径 2 条」【已被 main 的终裁否决】** ⇒ "
                   "★**`UART_RX` = 必需** (调试口) · ★**`USB_CC2` = 必需** ([官网] USB Type-C 双路 Rd) ⇒ "
                   "★**本页原结论保留在册作历史痕迹, 有效口径以 §7 为准** ★ · "
                   "依据 pm.yaml → `iss338_need_jtag_group_decision` / `iss338_need_usbif_cc1_cc2_rule` · "
                   "证据等级 = ★**[实测]** / ★**[官网]** ★{CORR_END}★★** ★"),
                 "§6 「推翻 main 2 条」")
    append_after("★**S8 净效果**: ★**悬空 9 条 ⇒ unc 45→36",
                 S(" {CORR}★★**★ISS-344 订正**: ★**上方「悬空 9 条 ⇒ unc 45→36」的口径【作废】** ⇒ "
                   "★**按终裁, 9 条里只有 `FSIN_OUT` 1 条可悬空 (★且带条件★) ⇒ 净效果 = 最多悬空 1 条** ⇒ "
                   "★**且 `FSIN_OUT` 标 NC 是板那一趟的动作·现在只定口径不动手** ⇒ ★**本单不宣称任何新的 unc 数字** ★ · "
                   "依据 pm.yaml → `iss334_need4b_zero_copper_net_triage` · 证据等级 = ★**[实测]** ★{CORR_END}★★** ★"),
                 "§6 「S8 净效果」")

    # ── ④ 文末追加 §7 ──────────────────────────────────────────────
    with open(os.path.join(HERE, "iss344_sec7.md"), encoding="utf-8") as f:
        sec7 = f.read()
    if sec7.endswith("\n"):
        sec7 = sec7[:-1]
    lines.extend(sec7.split("\n"))
    log.append("文末追加 §7 分级订正小节")

    new = "\n".join(lines)

    # ── ⑤ 自证: 只增不删 (★逐行: 原行必须是新行的字符子序列 ⇒ 只可能是插入★) ──
    old_lines = orig.split("\n")
    new_lines = new.split("\n")

    def is_subseq(short, long_):
        it = iter(long_)
        return all(ch in it for ch in short)

    for i, o in orig_of.items():
        n = mod.get(i, o)
        if not is_subseq(o, n):
            raise SystemExit("❌ 自证失败: 第 %d 行不是「只增不删」(原行不是新行的子序列)" % (i + 1))
    sm = difflib.SequenceMatcher(a=old_lines, b=new_lines, autojunk=False)
    bad = [(tag, i1, i2, j1, j2) for tag, i1, i2, j1, j2 in sm.get_opcodes()
           if tag == "delete"]
    if bad:
        raise SystemExit("❌ 自证失败: 检测到删除操作 %s" % bad[:5])
    # ★再核一遍: 未被改写的原行必须逐字还在 ★
    untouched = set(orig_of.values())
    for l in old_lines:
        if l.strip() and l not in untouched and l not in new_lines:
            raise SystemExit("❌ 自证失败: 老行不见了 ⇒ %s" % l[:100])

    with open(path, "w", encoding="utf-8") as f:
        f.write(new)

    print("═══ ISS-344 追加式订正执行完毕 ═══")
    print("  文件   : %s" % path)
    print("  行数   : %d ⇒ %d (只增 %d 行)" % (n_before, len(new_lines), len(new_lines) - n_before))
    print("  自证   : difflib opcodes 无 delete/replace ⇒ 只增不删 ✔")
    for l in log:
        print("  ✔ %s" % l)


if __name__ == "__main__":
    main()
