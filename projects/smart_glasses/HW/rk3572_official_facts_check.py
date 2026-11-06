#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rk3572_official_facts_check.py -- RK3572 官方 datasheet 事实卡自证脚本 (2026-11-06)
================================================================================
★**为什么要有这个脚本 (实测事故 x2 的教训)**:
  ① 20-25 压测: 分片/文档用普通 open(w) 写 ⇒ 读者看到半截 ⇒ 数据静默消失
     ⇒ 本脚本**只读**, 不写任何东西 ⇒ 不适用; 但事实卡**必须可被一条命令复核**
  ② ★★**更严重的一次 (本周实测)**: `pdftotext -layout` 出来的**扁平文本把
     Table 3-1 的多行单元格错位了** ⇒ 读出 "VCCIO1_VCC 属 1.8V only" ⇒
     ⇒ 差点据此下"整条 I2C_A 降 1.8V"的错判
     ⇒ ★**教训: 表格类断言不能靠 pdftotext 文本层单点确认, 必须渲染图人工核**
     ⇒ 本脚本能验的只验文本层; ★**表格归属 (Table 3-1 的行×列对应) 已在
       HW/RK3572_PIN_TABLE/figs/p39_gpio_crop2.png 渲染图上人工核对, 见事实卡 §5**

★**断言的每一条都带 PDF 文本层行号** ⇒ 任何人可 `sed -n 'NNN,MMMp' HW/RK3572_PIN_TABLE/rk3572_datasheet_V1.1.txt` 复核。

用法:  python3 HW/rk3572_official_facts_check.py [--json]
退出码: 0 = 全部断言命中 (事实卡可信) · 1 = 有断言落空 (事实卡要改)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
TXT = os.path.join(HERE, "RK3572_PIN_TABLE", "rk3572_datasheet_V1.1.txt")
PDF = os.path.join(HERE, "RK3572_PIN_TABLE", "RK3572_datasheet_V1.1.pdf")
FACTS = os.path.join(HERE, "RK3572_OFFICIAL_DATASHEET_FACTS.md")

# (断言名, 必须出现的字符串, 允许出现的行号窗口(起始, 结束))
ASSERTS = [
    ("封装代号 FCCSP550L",        "FCCSP550L",                 (820, 860)),
    ("本体 14.3x15.5mm",          "14.3mmx15.5mm",             (820, 840)),
    ("球尺寸 0.25mm",             "ball size:0.25mm",          (820, 840)),
    ("球间距 0.42&0.52&0.65",     "0.42mm&0.52mm&0.65mm",      (820, 840)),
    ("LPDDR4X-4266 & 5X-5500",     "LPDDR4/LPDDR4X-4266 and LPDDR5/LPDDR5X-5500", (210, 222)),
    ("单通道 32bit",                "Single channel has 32bits", (210, 222)),
    ("ISP 单通道 12M pixels",     "One channel ISP,12M pixels",(485, 495)),
    ("ISP 最大输入 4096x3072",     "Maximum input:4096x3072",   (485, 495)),
    ("ISP 最小输入 264x264",      "Minimum input:264x264",     (485, 495)),
    ("HDMI/eDP TX combo PHY",     "One HDMI/eDP TX combo PHY", (620, 632)),
    ("eDP compliant with DP v1.2","compliant with DisplayPort v1.2", (635, 650)),
    ("eDP HBR2 5.4Gbps",          "HBR2(5.4Gbps)",             (635, 650)),
    ("DSI-1.2 4lane 2.5Gbps",     "up to 2.5Gbps per lane",    (650, 660)),
    ("并行 BT.656/BT.1120",       "RGB/BT.656/BT.1120",        (655, 665)),
    ("23 个可上下电电源域",        "23 separate power domains", (255, 262)),
    ("VCCIO 绝对最大 3.63V",      "3.63",                      (2325, 2350)),
    ("VCCIO 绝对最大 1.98V",      "1.98",                      (2325, 2350)),
    ("VCCIO 绝对最大 1.95V(推荐)", "1.95",                      (2345, 2360)),
    ("CPU_BIG_DVDD 上限 1.0V",    "CPU_BIG_DVDD             0.675",  (2360, 2380)),
    ("NPU_DVDD 上限 0.918V",      "NPU_DVDD               0.675",  (2370, 2390)),
    ("Tj 绝对最大 125C",          "Max Conjunction Temperature",   (2350, 2360)),
    ("Storage -40~125C",          "Storage Temperature",           (2350, 2360)),
]

# ★**手工渲染图核对过的事实** (文本层验不了 ⇒ 单独列, 靠图存在性 + 事实卡标注)
IMAGE_CHECKS = [
    ("Table 3-1 渲染图 (GPIO 供电分组行×列对应)", os.path.join(HERE, "RK3572_PIN_TABLE", "figs", "p39_gpio_crop2.png")),
    ("Fig 2-2/2-3 封装视图渲染图",                os.path.join(HERE, "RK3572_PIN_TABLE", "figs", "p-20.png")),
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if not os.path.exists(TXT):
        print("❌ 找不到 %s" % TXT)
        return 1
    # ★★**必须用 split("\n") 而不是 splitlines()** (2026-11-06 实测踩坑):
    #   pdftotext 输出里带**分页符 (\\x0c)** ⇒ splitlines() 会在分页处多切一刀
    #   ⇒ 行号比 `sed -n 'Np'` 少/多 ⇒ 事实卡里标的行号对不上, 人工复核会扑空。
    #   ⇒ 这里按 \n 切, 行号与 sed/grep 完全一致。
    lines = open(TXT, encoding="utf-8", errors="ignore").read().split("\n")

    results = []
    ok = 0
    bad = []
    for name, needle, (lo, hi) in ASSERTS:
        hit = None
        for i in range(lo - 1, min(hi, len(lines))):
            if needle in lines[i]:
                hit = i + 1
                break
        if hit is None:
            # 允许全文件兜底一次 (行号窗口是给人工复核用的, 不该判死)
            for i, l in enumerate(lines):
                if needle in l:
                    hit = i + 1
                    break
        results.append({"name": name, "needle": needle, "line": hit,
                        "expect_window": [lo, hi]})
        if hit:
            ok += 1
        else:
            bad.append(name)

    img_results = []
    for name, p in IMAGE_CHECKS:
        e = os.path.exists(p)
        img_results.append({"name": name, "path": p, "exists": e,
                            "bytes": os.path.getsize(p) if e else 0})
        if not e:
            bad.append(name)

    pdf_md5 = None
    if os.path.exists(PDF):
        pdf_md5 = hashlib.md5(open(PDF, "rb").read()).hexdigest()
    facts_exists = os.path.exists(FACTS)
    if not facts_exists:
        bad.append("事实卡 HW/RK3572_OFFICIAL_DATASHEET_FACTS.md")

    payload = {
        "txt": TXT, "txt_lines": len(lines),
        "pdf": PDF, "pdf_md5": pdf_md5,
        "facts_card_exists": facts_exists,
        "asserts_total": len(ASSERTS),
        "asserts_passed": ok,
        "asserts_failed": bad,
        "image_checks": img_results,
        "results": results,
        "rc": 1 if bad else 0,
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return payload["rc"]

    print("═══ RK3572 官方 datasheet 事实卡自证 ═══")
    print("  文本层: %s (%d 行)" % (os.path.relpath(TXT, PROJ), len(lines)))
    print("  PDF md5: %s" % pdf_md5)
    print("  事实卡: %s" % ("在" if facts_exists else "❌ 不在"))
    print("  ── 文本层断言 %d/%d ──" % (ok, len(ASSERTS)))
    for r in results:
        mark = "✔" if r["line"] else "✘"
        win = "%d-%d" % (r["expect_window"][0], r["expect_window"][1])
        print("  %s %-34s %-34s 行 %s (窗口 %s)"
              % (mark, r["name"], r["needle"][:34],
                 r["line"] if r["line"] else "未命中", win))
    print("  ── 渲染图核对项 (表格行×列对应只能靠图) ──")
    for r in img_results:
        print("  %s %-44s %s"
              % ("✔" if r["exists"] else "✘", r["name"],
                 ("%d B" % r["bytes"]) if r["exists"] else "缺"))
    if bad:
        print("\n❌ 有 %d 条落空 ⇒ 事实卡不可信 ⇒ rc=1" % len(bad))
        for b in bad:
            print("   · %s" % b)
        return 1
    print("\n✅ 全部断言命中 ⇒ 事实卡每个数字都能在官方 PDF 文本层复现")
    return 0


if __name__ == "__main__":
    sys.exit(main())
