#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RK3572 Datasheet §2.6 Pin Number List 解析器
================================================================================
★背景 (2026-11-02): 老板指示「发邮件问厂商没用, 所有信息自己去网上找」⇒ 改走开源/公开渠道。
  找到一手源: Rockchip 官方 RK3572 Datasheet V1.1 PDF
  (https://rockchip.fr/RK3572%20datasheet%20V1.1.pdf, 2.4MB / 47 页 / 2026-04-14)
  §2.6 Pin Number List 在第 22-38 页。

★PDF 表格结构 (pdftotext -layout 提取后):
  三列 —— [引脚名(可折行)] [球位号] [GPIO 缩写]
  引脚名一行放不下时会**折行**, 折行的续行以**更靠右的缩进**出现, 且续行末尾不带球位号。
  ⇒ 解析要按"球位号出现的那一行才是记录起点"来重组, 不能按行简单切。

★输出: JSON + CSV (球位号 / 完整引脚名 / GPIO 缩写 / 功能分类)
★证据等级: [官方] —— Rockchip 原厂 datasheet 书面
"""
from __future__ import annotations

import csv
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TXT = os.path.join(HERE, "rk3572_datasheet_V1.1.txt")
OUT_JSON = os.path.join(HERE, "rk3572_pins.json")
OUT_CSV = os.path.join(HERE, "rk3572_pins.csv")

# 球位号格式 (FCCSP 行列式命名):
#   AN1 / A19 / AT27 / 1AE15 / 2K1 / 1AB20
# ⇒ 可选行首 1-2 位数字 + 1-3 位字母 + **至少 1 位**结尾数字
# ★关键: 结尾必须有数字 ⇒ 否则 "GND" / "RFU3" / "Chapter" 会被误当球位
BALL_RE = re.compile(r"^([0-9]{0,2}[A-Z]{1,3}[0-9]{1,3})$")
# 纯字母或纯字母+数字但不是球位的常见 token (用于反证)
_NOT_BALL = {"GND", "RFU3", "RFU1", "RFU2", "Chapter", "Abbr", "Pin", "Name", "Copyright"}

SKIP_LINE_RE = re.compile(
    r"(Chapter|Copyright|RK3572 Datasheet|Rev 1\.1|Pin Number List|Table 2-|"
    r"^\s*Pin Name\s+Pin\s+Abbr\s*$|^\s*$)"
)


def parse(text: str) -> list[dict]:
    i = text.find("2.6 Pin Number List", 40000)
    j = text.find("3.1 Absolute Ratings", 40000)
    if i < 0 or j < 0:
        raise SystemExit("❌ 定位不到 §2.6 区间 (PDF 结构变了?)")
    sec = text[i:j]

    rows: list[dict] = []
    pending_name: list[str] = []
    for raw in sec.splitlines():
        line = raw.rstrip()
        if not line.strip():
            # ★空行 = 记录边界: 攒着的折行名到此为止, 不许串到下一条
            #   (不这么做的后果: DSI_TX_CLKP 被算到 1AE15 那行上 —— 球位号全错)
            pending_name = []
            continue
        if SKIP_LINE_RE.search(line):
            continue
        # 拆成列: 连续 2 个以上空格 = 列分隔
        cols = [c.strip() for c in re.split(r"\s{2,}", line.strip()) if c.strip()]
        if not cols:
            continue

        # 情况 A: 有一列正好是球位号 ⇒ 这是记录起点
        ball_idx = None
        for k, c in enumerate(cols):
            if BALL_RE.match(c) and c not in _NOT_BALL:
                ball_idx = k
                break
        if ball_idx is not None:
            name_parts = [c for c in (pending_name + cols[:ball_idx]) if c != "Pin Name"]
            pending_name = []
            ball = cols[ball_idx]
            abbr = cols[ball_idx + 1] if len(cols) > ball_idx + 1 else ""
            rows.append({
                "ball": ball,
                "name": "/".join(name_parts) if len(name_parts) > 1 else (name_parts[0] if name_parts else ""),
                "gpio": abbr,
            })
            # 同一行可能还挂着续行 (名称在球位号之后 —— 罕见, 记录下来)
            if len(cols) > ball_idx + 2:
                pending_name = [cols[ball_idx + 2]]
            # ★页眉表头 "Pin Name Pin Abbr" 已被 SKIP 过滤, 但跨页时表头与首行可能粘连
            #   ⇒ 若 cols[0] 恰是 "Pin Name", 把它从名字里剥掉
        else:
            # 情况 B: 折行续行 —— 攒起来, 等下一个带球位号的行
            pending_name.append(cols[0])
    return rows


def classify(name: str) -> str:
    u = name.upper()
    for k, v in [
        ("DSI_TX", "DSI"), ("MIPI_DPHY_DSI", "DSI"), ("MIPI_DPHY_CSI", "CSI"),
        ("USB_DRD", "USB"), ("USB", "USB"), ("I2C", "I2C"), ("I3C", "I3C"),
        ("UART", "UART"), ("SPI", "SPI"), ("FSPI", "SPI"), ("PWM", "PWM"),
        ("SARADC", "ADC"), ("JTAG", "JTAG"), ("FSIN", "FSIN"),
        ("BOOT", "BOOT"), ("RESET", "RESET"), ("OSC", "XTAL"),
        ("GPIO", "GPIO"), ("VSS", "GND"), ("AVSS", "GND"), ("TVSS", "GND"),
        ("VCC", "PWR"), ("DDR", "DDR"), ("PCIE", "PCIE"), ("SATA", "SATA"),
        ("UFS", "UFS"), ("HDMI", "HDMI"), ("CAN", "CAN"), ("GMAC", "ETH"),
        ("ETH", "ETH"), ("SAI", "I2S"), ("PDM", "I2S"), ("VO_LCDC", "RGB"),
        ("EBC", "EINK"), ("DSMC", "DSMC"), ("PMU", "PMU"), ("PLL", "PLL"),
    ]:
        if k in u:
            return v
    return "OTHER"


def main() -> int:
    if not os.path.exists(TXT):
        print(f"❌ 缺 {TXT}", file=sys.stderr)
        return 2
    text = open(TXT, encoding="utf-8", errors="ignore").read()
    rows = parse(text)
    for r in rows:
        r["func"] = classify(r["name"])
    balls = [r["ball"] for r in rows]
    dup = {b for b in balls if balls.count(b) > 1}
    if dup:
        print(f"⚠️ 重复球位 {sorted(dup)[:10]}", file=sys.stderr)

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=1)
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["ball", "gpio", "func", "name"])
        w.writeheader()
        w.writerows(rows)

    import collections
    cnt = collections.Counter(r["func"] for r in rows)
    print(f"✅ 解析 {len(rows)} 个球位 → {os.path.basename(OUT_JSON)} / {os.path.basename(OUT_CSV)}")
    print("   功能分布:", dict(cnt.most_common()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
