#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_correction_sections.py —— ISS-295 辅助: 生成并追加两页的【ISS-295 订正覆盖节】

★为什么用生成器而不是手写★:
  1) 【现状句】必须在两页逐字一致 (F5) ⇒ 从闸文件里 import 出来用, 手抄必出错
  2) 【逐字锚点】必须与 MANIFEST 逐字一致 ⇒ 同上
  3) 幂等: 已存在则不重复追加

★只追加 (老字一字不删不改) ⇒ 遵守 ISS-290/ISS-294 的追加式纪律★
"""
import importlib.util
import os
import sys

PROJ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
GATE = os.path.join(PROJ, "MECH", "check_mech_verdict_freshness.py")

spec = importlib.util.spec_from_file_location("iss295_gate", GATE)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

MARKER = "ISS-295-订正覆盖表"

HEAD = """
## ★★§ISS-295-订正覆盖表 · 「板只改一次」结构侧输入认领全表同步 (★帧: `B160x100` · mech-lead · 2026-11-17 · ISS-295★)★★

> ★**本节是【追加】**: ★**本页 §1~§6 / ISS-290 追加段 / ISS-294 追加段 / ISS-278 续做追加段 的老字一个字没删、没改、没动** ★
> ★**本节干什么**: ★**ISS-295 给「板只改一次」那一趟发了一份结构侧输入认领全表 (`MECH/BOARD_ONEPASS_MECH_CLAIMS.md`); 本节把本页里【已被 ISS-294 推翻的老结论】逐条列出并【逐字】覆盖 ⇒ 防止有人只 grep 老行就拿走错结论** ★
> ★**闸**: ★**`python3 MECH/check_mech_verdict_freshness.py` ⇒ rc=0** ★ (★判据 = 逐字短语命中, 零行号依赖★)

★**现状句 (★两页必须逐字一致·不许各写各的★)**:

★**{canon}** ★

★**老结论逐条覆盖表 (★老字保留作历史留痕; 每一处都必须被本节逐字引用; ★本表只是【引用】, 不许当成现状★)**:

| ★hit id★ | ★老结论所在小节 (帧 `B160x100`)★ | ★逐字锚点 (★留痕原样·不许改写★)★ | ★老结论说过什么 (★逐字·已过期·不再作数★)★ | ★处理 (★ISS-295 做了什么★)★ |
|---|---|---|---|---|
"""

ROWS = {
    "MSYNC": [
        ("MS-1", "§10.3 另两条会改板的口径",
         "现有 MECH 规格 (检修口 / 调试口两条) 里没有这条边开口",
         "「`J_USB_C` 边开口缺口 … 现有 MECH 规格 (检修口 / 调试口两条) 里没有这条边开口」",
         "★**已过期** ⇒ ISS-294 已补第三条开口 `PORT_OPEN_USBC` (X 132.995..147.005 @ 板边 Y = 0 · 必须清空区 X 133.895..146.105); 老字保留作历史留痕 ⇒ **引用本节, 不引用本行** ★"),
        ("MS-2", "ISS-294 追加段 · 来由",
         "`J_USB_C` 缺一条结构边开口规格 (ISS-290 做不了、也没做)",
         "「`J_USB_C` 缺一条结构边开口规格 (ISS-290 做不了、也没做) ⇒ 本单接 E-6 的 MECH 那一半」",
         "★**已过期** ⇒ E-6 的 MECH 半边已由 ISS-294 做完 (规格 + 两道闸的 id 集合断言); 本行是【当时来做这件事的来由】, 不是现状 ★"),
        ("MS-3", "§11.5 归 main → 老板拍的四条 · 第 4 条",
         "verdict 仍写「可装 / 结构侧缺一条边开口规格」",
         "「`J_USB_C` 行 verdict 仍写「可装 / 结构侧缺一条边开口规格」 ⇒ 两页口径分叉」",
         "★**已过期** ⇒ CROSSCHECK 那页已由本节的覆盖表 + 该页自己的 ISS-295 订正覆盖节覆盖 ⇒ **两页现状句现在逐字一致**; 本行保留作【分叉曾经存在过】的留痕 ★"),
    ],
    "XCHK": [
        ("XC-1", "§2 MECH 侧保留区全集 · `USB-C-BODY` 行",
         "现有 MECH 规格里【没有】这一条 ⇒ 本单登记为缺口",
         "「结构件在这条边上必须有开口; 现有 MECH 规格里【没有】这一条 ⇒ 本单登记为缺口」",
         "★**已过期** ⇒ ISS-294 已补 `PORT_OPEN_USBC`; 本行保留作历史留痕 ⇒ **引用本节, 不引用本行** ★"),
        ("XC-2", "§4 座体类器件三方对照表 · `J_USB_C` 行",
         "可装 (三方一致) / ★结构侧缺一条边开口规格 (缺口)",
         "「结构件必须有边开口 (现有 MECH 规格里【没有】这一条) · 开孔 = 缺口, 待登记」",
         "★**已过期** ⇒ 现状 = 三方一致 (3 个座体: `J_SOM_P2` / `J_SOM_P4` / `J_USB_C`); 开口规格见 `MECH/BOARD_ONEPASS_MECH_CLAIMS.md` C-OPEN-3 ★"),
        ("XC-3", "§4.1 §4 小结",
         "但结构侧缺一条边开口规格",
         "「1 个: `J_USB_C` (16p @0.50 + 2×Ø0.65 对上, 但结构侧缺一条边开口规格)」",
         "★**已过期** ⇒ 同 XC-2; 本行保留作历史留痕 ★"),
        ("XC-4", "§7 机器可读 JSON 块 · `J_USB_C` 行 verdict",
         '"verdict": "可装 (三方一致) / 结构侧缺一条边开口规格",',
         "「可装 (三方一致) / 结构侧缺一条边开口规格」",
         "★**已过期** ⇒ ★**机器块不许动** (ISS-290 的交卷物, `openings[]` / `rect` / `tiers` 一个字节不许改) ⇒ 老字保留; 机器读本块的人请同时读本节 ★"),
        ("XC-5", "§5.6 「必须在那一趟一起改」清单 · E-6",
         "缺一条结构边开口规格 (★缺口, 不改板★)",
         "「E-6 · `J_USB_C` 缺一条结构边开口规格 (★缺口, 不改板★)」",
         "★**已过期** ⇒ E-6 的 MECH 半边已由 ISS-294 做完; 余下的只有【尺寸三口径待 main→老板 拍】(见 CLAIMS 页 §5) ★"),
        ("XC-6", "§5.6 「必须在那一趟一起改」清单 · E-6 · 现状",
         "里【没有】这条边开口",
         "「现有 MECH 规格 (检修口 / 调试口两条) 里【没有】这条边开口」",
         "★**已过期** ⇒ 同 XC-5; 本行保留作历史留痕 ★"),
    ],
}

TAIL = """
★**★本节的纪律 (★自证口径★)**:

| 项 | 口径 |
|---|---|
| ★**追加式** ★ | ★**老字一个字没删、没改、没动; 本节只【追加】** ★ |
| ★**机器块不许动** ★ | ★**§7 机器块的 `openings[]` / `rect` / `tiers` / `verdict` 一个字节不许改; XC-4 的老字是【机器块里的历史留痕】** ★ |
| ★**不代拍** ★ | ★**开口尺寸 / Z 向窗口 / 立柱外径 / 座体真实高 h = 只列事实与代价, 归 main→老板** ★ |
| ★**闸** ★ | ★**`python3 MECH/check_mech_verdict_freshness.py` ⇒ rc=0; `--selftest` ⇒ rc=0 (★反向用例 ≥4 条·沙盒副本上跑★)** ★ |
| ★**实物 `[实测]` = 0 条** ★ | ★**本机无板、无量具、无打印机 ⇒ 一切「实测」= 文件实读 + 脚本实跑** ★ |
"""


def build(page_key: str) -> str:
    rows = []
    for hid, where, anchor, old, act in ROWS[page_key]:
        rows.append("| ★%s★ | ★%s★ | %s | ★%s★ | ★%s★ |\n"
                    % (hid, where, anchor, old, act))
    return (HEAD.replace("{canon}", gate.CANON) + "".join(rows) + TAIL)


def main() -> int:
    rc = 0
    for key, rel in gate.PAGES:
        p = os.path.join(PROJ, rel)
        text = open(p, encoding="utf-8").read()
        if MARKER in text:
            print("[skip] %s 已有 %s ⇒ 不重复追加" % (rel, MARKER))
            continue
        sec = build(key)
        if not text.endswith("\n"):
            text += "\n"
        text += sec
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(text)
        print("[ok] %s += %s (%d B)" % (rel, MARKER, len(sec.encode("utf-8"))))
    return rc


if __name__ == "__main__":
    sys.exit(main())
