#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
state/_apply_iss302_landing_ledger.py —— ★★ISS-302 落表台账追加 (hw-lead · 2026-11-18)★★
================================================================================
★**做什么**: 向 `HW/SCHEMATIC_LANDING_V1_LANDED.md` **append-only** 追加一条落表链 ★
    ★**这一条链 = 机器闸 `HW/landing_md5.py` 的判决源** ⇒
    `latest_chain()` 取【台账里最后一条 `##` 链】⇒ ★**本条必须落在文件最末尾** ★

★**必须带的 6 项 (★ISS-302 任务书 §⑦③ 逐字要求★)**:
    ★**单号 ISS-302 / 文件名 / 旧 md5 / 新 md5 / 落表时刻 / 台账行号** ★

★**机器读得懂的形状 (★一个字都不许自创★)**:
    · 链头 `## ... ISS-302 ...` (★`_ISSUE_RE` 从链头行抽单号★)
    · 链内**恰好一张** `### ... 16.2 · 新旧 md5 ...` 表 (★`_SEC162_RE` + `_ROW_RE`★)
    · 表行形状 = `| ★**`文件名`** ★ | `旧 md5` | `新 md5` | 变了? |`
      (★`_ROW_RE` 逐字吃这个形状 ⇒ 少一个反引号就断链★)

★**板两件必须【前后同值】登记** (★零写板 ⇒ 板 md5 一个字节没变★)
    ⇒ ★**不许**在 §16.2 里给板写一个新值 (★那等于伪造一次改板★)

用法:  python3 state/_apply_iss302_landing_ledger.py           # 追加
       python3 state/_apply_iss302_landing_ledger.py --verify  # 只校验 (rc=0/1)
"""
from __future__ import annotations

import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
LEDGER = os.path.join(PROJ, "HW", "SCHEMATIC_LANDING_V1_LANDED.md")

ISSUE = "ISS-302"
STAMP = "2026-11-18 00:3x"          # ★落表时刻 (Asia/Shanghai)★

# ★**新旧 md5 (★改前 = ISS-283 落表后真盘实测值 · 改后 = 本单重生成后真盘实测值★)** ★
ROWS = [
    ("HW/netlist_v1.csv", "37f62ac3f0b81d92ca7d48fdea717f07", "6aee500e60ba0732f83a9cf557ba90ab", True),
    ("HW/netlist_v1_pins.csv", "a4270120454aedf7a23c92cd8985c8a6", "9174309df1ec9411ac8e8d9e80ee386a", True),
    ("HW/BOM_v1.csv", "5d02bece9477ffce5fbe0193c7d5cce4", "5b9993992405904a60ac96a020b375d8", True),
    ("HW/PCB/demo_mainboard.kicad_pcb", "611b869e13518c3c023fb178f91a0075", "611b869e13518c3c023fb178f91a0075", False),
    ("HW/PCB/demo_mainboard.kicad_pro", "3e504d2be83152e337949723e909be1b", "3e504d2be83152e337949723e909be1b", False),
]

HEAD = (
    "\n## ★★19 · ★★ISS-302 落表链 (★C_SYS / SYS_CHG 必装 · 硬件总工 (hw-lead) · 2026-11-18 · "
    "★TI bq25896 datasheet SLUSC76C §7 逐字『Connect a 20uF closely to the SYS pin.』★) ★★\n"
    "\n"
    "### ★★19.1 · 一句话结论 ★★\n"
    "\n"
    "★**`SYS_CHG` / `C_SYS` 由 DNP 改为必装 (★TI §7 明令 SYS 必挂 20 µF 到地★) · "
    "note 追加式订正 (★老字逐字留痕 + 过期 PM 裁决『VSYS 脚不接 (NC)』标为已作废 + 换成 "
    "★SYS 必接 20 µF (TI §7); 不跨铰链引系统轨★ + 板面数 25×10mm 板面 → ≈8 mm² (0805/1206)★) · "
    "BOM CHG_BOARD 加 1 颗 20 µF 6.3 V X7R/X5R** ★\n"
    "\n"
    "★**真源** = `state/p10_rows.json` (★P10 充电板页器件级行数据 = `state/gen_netlist.py` 的唯一输入★) ★\n"
    "★**落表脚本** = `state/_apply_iss302_csys_landing.py` (★改真源, 不手改产物★) ★\n"
    "★**产物一律重生成** = `gen_netlist` → `gen_kicad_net` → `gen_netlist_pins` → `gen_bom` → "
    "`gen_schematic_pages` → `gen_kicad_sch` ★\n"
    "\n"
    "### ★★16.2 · 新旧 md5 前后对照 (★供 SW / MECH 两边走 H-1 重锚★) ★★\n"
    "\n"
    "| 文件 | 前 | 后 | 变了? |\n"
    "|---|---|---|---|\n"
)

BODY = (
    "\n"
    "★**受保护的两个必须逐字节不变**: `HW/PCB/demo_mainboard.kicad_pcb` = `611b869e13518c3c023fb178f91a0075` · "
    "`HW/PCB/demo_mainboard.kicad_pro` = `3e504d2be83152e337949723e909be1b` ★\n"
    "\n"
    "★**零写板自证 (★md5 + mtime 双重★)**: `HW/PCB/demo_mainboard.kicad_pcb` mtime 仍 `2026-11-06 07:07:17.362193413` "
    "(★自 11-06 07:07 未动★) ★\n"
    "\n"
    "### ★★19.3 · 逐条登记 (★单号 + 文件名 + 旧 md5 + 新 md5 + 落表时刻 + 台账行号★) ★★\n"
    "\n"
    "| 台账行号 | 文件名 | 旧 md5 | 新 md5 | 落表时刻 | 单号 |\n"
    "|---|---|---|---|---|---|\n"
    "<!--ISS302_ROWS:BEGIN-->\n"
    "<!--ISS302_ROWS:END-->\n"
)

FOOT = (
    "\n"
    "★**本批【没落】的东西 (★逐条 + 卡在谁★)**:\n"
    "\n"
    "| 条目 | 归因 | 卡在谁 |\n"
    "|---|---|---|\n"
    "| `HW/CHARGE_BOARD_SPEC.md` L128 / L229 / L545 / L546 / L612 仍写「`C_SYS` 焊盘位 (DNP)」 | ★**规格页没跟落表**★ | "
    "★**项目总工 (main)** ★ ⇒ 本单只落 4 条动作 (ISS-301 §B5-① 原文), 规格页属额外面 ⇒ ★**未擅自扩范围**★ ★\n"
    "| `HW/calc_chg_board_area.py` L78 / L120 把 `C_SYS` 算成「20uF 1206 (DNP 不装)」并放进 `T3_DELETE` (★面积账少算 ≈8 mm²★) | "
    "★**面积账要重算**★ | ★**硬件总工 (下一趟·充电板布局那一趟)** ★ |\n"
    "| `HW/CHG_BOARD_AREA_RECHECK.md` §3 的面积缺口结论 (★基于「C_SYS 删掉」★) | ★**同上**★ | ★**硬件总工 (下一趟)** ★ |\n"
    "| `C_SYS` 的 footprint / OPN | ★**选型未做**★ | ★**待选型 (询价经项目总工)★ ⇒ BOM 仍留『待定』, ★**不编造**★ |\n"
    "\n"
    "### ★★19.4 · 复现命令 (★B6 自证★) ★★\n"
    "\n"
    "```bash\n"
    "cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses\n"
    "python3 state/_apply_iss302_csys_landing.py            # ★改真源 state/p10_rows.json★\n"
    "python3 state/gen_netlist.py && python3 state/gen_kicad_net.py && \\\n"
    "python3 state/gen_netlist_pins.py && python3 state/gen_bom.py && \\\n"
    "python3 state/gen_schematic_pages.py && python3 state/gen_kicad_sch.py\n"
    "python3 HW/check_netlist_selfconsistency.py                    # rc=0\n"
    "python3 HW/check_netlist_selfconsistency.py --expect-resolved   # rc=1 (★预期: 4 条缺陷仍在, 与本单无关★)\n"
    "python3 HW/check_land_row_anchors.py                           # rc=0\n"
    "python3 HW/check_onepass_preflight_coverage.py                 # rc=0\n"
    "python3 HW/check_pin_function_labels.py --expect-known         # rc=0 (★H-1 重锚第 3 跳之后★)\n"
    "python3 HW/check_onepass_commit_order.py                       # rc=0\n"
    "python3 state/merge.py && python3 state/gate_check.py && python3 state/issue_check.py\n"
    "md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro\n"
    "```\n"
    "\n"
    "---\n"
)


def build_section():
    out = [HEAD]
    for fn, old, new, changed in ROWS:
        out.append("| ★**`%s`** ★ | `%s` | `%s` | %s |\n" % (
            fn, old, new, "★**是**★" if changed else "否"))
    out.append(BODY)
    return out


def verify() -> int:
    txt = io.open(LEDGER, encoding="utf-8").read()
    bad = []
    if "ISS-302" not in txt:
        bad.append("台账里查不到 ISS-302")
    for fn, old, new, _c in ROWS:
        if new not in txt:
            bad.append("台账里查不到 %s 的新 md5 %s" % (fn, new))
    sys.path.insert(0, os.path.join(PROJ, "HW"))
    import landing_md5
    chain, problems = landing_md5.latest_chain(PROJ)
    if chain is None or problems:
        bad.append("landing_md5.latest_chain: %s" % (problems or ["空链"]))
    else:
        if chain["issue"] != ISSUE:
            bad.append("最新链的单号 = %r (期望 %r)" % (chain["issue"], ISSUE))
        if chain["n_sec162"] != 1:
            bad.append("最新链的 16.2 表数 = %d (期望 1)" % chain["n_sec162"])
        for fn, _o, new, _c in ROWS:
            if fn not in chain["rows"]:
                bad.append("最新链里查不到 %s 的登记" % fn)
            elif chain["rows"][fn][1] != new:
                bad.append("最新链里 %s 的新 md5 = %r (期望 %r)" % (fn, chain["rows"][fn][1], new))
    if bad:
        print("❌ ISS-302 台账校验未过:")
        for b in bad:
            print("   ·", b)
        return 1
    print("✅ ISS-302 台账校验通过 (单号 / 5 件文件名 / 新旧 md5 / 最新链指向 ISS-302)")
    return 0


def main() -> int:
    if "--verify" in sys.argv:
        return verify()

    txt = io.open(LEDGER, encoding="utf-8").read()
    if ISSUE in txt:
        print("★ 台账里已经有 %s ⇒ 不重复追加 (幂等) ★" % ISSUE)
        return verify()

    with io.open(LEDGER, "a", encoding="utf-8") as fh:
        fh.write("".join(build_section()))
    print("★ 台账已追加 %s 落表链 (append-only) ★" % ISSUE)

    # ── 回填「台账行号」那一栏 (★追加完才知道行号★) ──
    #   ★★注意: §16.2 表的行【一个字节都不许动】 —— 机器闸 `_ROW_RE` 吃的就是那个形状
    #     (★文件名必须在第 1 列·行号另起一张表登记·行号那列不许加反引号·不然会被误认成文件名★)★★
    lines = io.open(LEDGER, encoding="utf-8").read().split("\n")
    row_line = {}
    for i, l in enumerate(lines):
        for fn, old, new, _c in ROWS:
            if l.startswith("| ★**`%s`** ★ | `%s` | `%s` |" % (fn, old, new)):
                row_line[fn] = i + 1
    if len(row_line) != len(ROWS):
        print("❌ 没能定位全部 5 行的行号: %r" % row_line)
        return 1
    rows_txt = []
    for fn, o, n, _c in ROWS:
        ln = row_line[fn]
        rows_txt.append("| L%d | %s | `%s` | `%s` | ★**%s** ★ | ★**%s** ★ |" % (ln, fn, o, n, STAMP, ISSUE))
    blk = "<!--ISS302_ROWS:BEGIN-->\n" + "\n".join(rows_txt) + "\n<!--ISS302_ROWS:END-->"
    txt2 = "\n".join(lines)
    if "<!--ISS302_ROWS:BEGIN-->\n" not in txt2:
        print("❌ 找不到回填锚点")
        return 1
    txt2 = txt2.replace("<!--ISS302_ROWS:BEGIN-->\n<!--ISS302_ROWS:END-->", blk, 1)
    with io.open(LEDGER, "w", encoding="utf-8") as fh:
        fh.write(txt2)
    print("★ 台账行号已回填: %s ★" % ", ".join("%s=L%d" % (k, v) for k, v in sorted(row_line.items(), key=lambda kv: kv[1])))
    return verify()


if __name__ == "__main__":
    sys.exit(main())
