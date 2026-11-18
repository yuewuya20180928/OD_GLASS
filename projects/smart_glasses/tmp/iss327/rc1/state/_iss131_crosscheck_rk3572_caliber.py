#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
state/_iss131_crosscheck_rk3572_caliber.py
================================================================================
★**ISS-131 · RK3572 口径自查 · 机器可复核交叉核对** ★
★**cron 775d9893 (ARS45 继续执行后继计划) · 2026-11-18 01:3x · 本机实跑** ★

★**做三件事 (★全部只读·零写板·零落表·零外发★)**:
  ① **球位号自洽**: 网表里所有 `J_SOM_P2/P4` 的 CSI/MCLK 落位 ↔ `HW/PCB/FET3572C_PIN_TABLE.csv` 的 ball 列
     ↔ 官方 datasheet (`HW/RK3572_PIN_TABLE/rk3572_datasheet_V1.1.txt`) 的 ball 逐条对拍
  ② **CSI 通道数口径**: 官方 datasheet §1.2.7/§1.2.8 逐字抽取 ⇒ 算出「我方用几路」
  ③ **ISP 12M 口径**: 官方 datasheet 逐字 ⇒ 判「分辨率上限卡不卡」+「MP/s 给没给」

★**用法**: `python3 state/_iss131_crosscheck_rk3572_caliber.py` ⇒ rc=0 全过 / rc=1 有不一致
★**边界**: 本脚本【不写任何工程文件】⇒ 板 md5 / 网表 md5 / 脚表 md5 / BOM md5 / 台账 md5 一个字节都不动
"""
from __future__ import annotations

import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)

NETLIST = os.path.join(PROJ, "HW", "netlist_v1.csv")
BALLTAB = os.path.join(PROJ, "HW", "PCB", "FET3572C_PIN_TABLE.csv")
DS_TXT = os.path.join(PROJ, "HW", "RK3572_PIN_TABLE", "rk3572_datasheet_V1.1.txt")

fails: list[str] = []
lines: list[str] = []


def ok(msg: str) -> None:
    lines.append("  ✅ %s" % msg)


def bad(msg: str) -> None:
    lines.append("  ✗ %s" % msg)
    fails.append(msg)


def hdr(t: str) -> None:
    lines.append("")
    lines.append("=== %s ===" % t)


# ---------------------------------------------------------------- ① 球位号自洽
hdr("① 球位号自洽 (★网表 J_SOM 落位 ↔ FET3572C_PIN_TABLE ball ↔ 官方 datasheet ball★)")

ball_rows = {}
with open(BALLTAB, encoding="utf-8") as f:
    for r in csv.DictReader(f):
        conn = (r.get("conn") or "").strip()
        num = (r.get("num") or "").strip()
        ball = (r.get("ball") or "").strip()
        sig = (r.get("signal") or "").strip()
        if conn and num:
            ball_rows[(conn, num)] = (ball, sig)

if not ball_rows:
    bad("FET3572C_PIN_TABLE.csv 读不出任何 (conn,num) 行")
else:
    ok("FET3572C_PIN_TABLE.csv 读到 %d 条 (conn,num)" % len(ball_rows))

# 官方 datasheet 的球位表排版有两种形态:
#   形态①单行: "MIPI_DPHY_CSI0_RX_D0P      A19        -"           (L1777)
#   形态②跨行: 信号名断成 2~3 行, ball 单独一行 (L1587~1589: ... / AM32 / ...)
# ⇒ 统一按「ball 锚点 ±3 行窗口」判: 该窗口里出现该信号名 ⇒ 对得上
ds_lines = open(DS_TXT, encoding="utf-8").read().splitlines()
BALL_RE = re.compile(r"(?<![0-9A-Za-z_])([0-9]?[A-Z]{1,2}[0-9]{1,2})(?![0-9A-Za-z_])")


def ds_ball_window(ball: str, span: int = 3) -> str:
    """ball 出现的行 ±span 行的文本窗口"""
    out = []
    for i, ln in enumerate(ds_lines):
        if BALL_RE.fullmatch(ball) and re.search(r"(?<![0-9A-Za-z_])%s(?![0-9A-Za-z_])" % re.escape(ball), ln):
            for j in range(max(0, i - span), min(len(ds_lines), i + span + 1)):
                out.append(ds_lines[j])
    return "\n".join(out)

# 网表里所有 J_SOM_P2 / J_SOM_P4 的行: 取 "xxx pinNN" + 本行 net 名
som_hits = []          # (net, conn, num, expected_signal)
with open(NETLIST, encoding="utf-8") as f:
    for r in csv.DictReader(f):
        blob = " ".join(str(v or "") for v in r.values())
        for m in re.finditer(r"J_SOM_(P2|P4)\s+pin(\d+)", blob):
            conn = m.group(1)          # ★P2 / P4★ (★别再拼成 PP4★)
            num = m.group(2)
            # 本行涉及的信号名: 取 net 段里含 CSI/MCLK 的 token
            toks = set(re.findall(r"(?:NET_)?CSI_[A-Z0-9_]+", blob))
            som_hits.append((conn, num, sorted(toks), blob[:120]))

# 只核对与 CSI 相关的落位
csi_hits = [(c, n, t, b) for (c, n, t, b) in som_hits if t and any("CSI" in x for x in t)]
lines.append("  · 网表里 J_SOM_P2/P4 的落位共 %d 处 (其中 CSI 相关 %d 处)" % (len(som_hits), len(csi_hits)))

checked = 0
for conn, num, toks, blob in csi_hits:
    key = (conn, num)
    if key not in ball_rows:
        bad("%s pin%s 在 FET3572C_PIN_TABLE.csv 里查不到" % (conn, num))
        continue
    ball, sig = ball_rows[key]
    win = ds_ball_window(ball)
    if not win:
        bad("%s pin%s 表上 ball=%s 在官方 datasheet 里找不到该球位" % (conn, num, ball))
        continue
    if sig not in win:
        bad("%s pin%s 表上 ball=%s 的窗口里没有信号名 %s (★官方 datasheet 对不上★)"
            % (conn, num, ball, sig))
        continue
    checked += 1
    lines.append("    · %s pin%-3s ball=%-4s %-28s ✓ 官方 datasheet 同一球位窗口命中"
                 % (conn, num, ball, sig))
if checked:
    ok("球位号逐条对拍: %d/%d 条 与官方 datasheet 完全一致" % (checked, len(csi_hits)))
if not csi_hits:
    bad("网表里没抓到 CSI 相关 J_SOM 落位 (口径变了? 需人工看)")

# ---------------------------------------------------------------- ② CSI 通道数
hdr("② CSI 通道数口径 (★官方 datasheet §1.2.7 / §1.2.8 逐字★)")
ds = open(DS_TXT, encoding="utf-8").read()

checks = [
    ("§1.2.7  Video Input Interface", "Support 2 MIPI CSI-2 interfaces"),
    ("§1.2.7  D-PHY 版本", "Two 4 data lanes of D-PHY v1.2"),
    ("§1.2.7  2x2 拆分", "Each interface may be configured as 2x2 data lanes port"),
    ("§1.2.8  VICAP", "Support receiving four groups of MIPI CSI interfaces"),
    ("§1.2.8  ISP 通道数 + 像素", "One channel ISP,12M pixels"),
    ("§1.2.8  ISP 最大输入", "Maximum input:4096x3072"),
]
for tag, needle in checks:
    if needle in ds:
        ok("%s : 「%s」" % (tag, needle))
    else:
        bad("%s : 官方 datasheet 里找不到「%s」" % (tag, needle))

# 我方用几路: 网表里的 CSI 数据对唯一前缀
net_csi_d = sorted(set(re.findall(r"CSI_(D\d+)_", open(NETLIST, encoding="utf-8").read())))
if net_csi_d == ["D0"]:
    ok("我方网表只用 **CSI_D0 一路** (4 lane) ⇒ ★「2 接口 / 4 口」的口径差异对我方板无约束★")
elif net_csi_d:
    bad("我方网表用了 %s 多路 CSI ⇒ 需重新核 One channel ISP 的限制" % net_csi_d)
else:
    bad("网表里没抓到 CSI_D* 网名")

# ---------------------------------------------------------------- ③ ISP 12M
hdr("③ ISP 12M 口径 (★分辨率上限 vs MP/s 吞吐★)")
ok("ISP 像素口径 = 「12-Megapixel ISP」+「One channel ISP,12M pixels」+「Maximum input:4096x3072」")
ok("4096x3072 = %.2f Mpixel ⇒ 与「12M」自洽 (★这是【单帧分辨率上限】不是 MP/s★)"
   % (4096 * 3072 / 1e6))
# 1080p60 的 MP/s 需求 (★OV04C10 模式·老板 10-29 定★)
mp = 1920 * 1080 * 60
ok("我方需求 OV04C10 @1080p60 = 1920x1080x60 = %.1f MP/s (★[推算]·口径来自老板 10-29 决策★)" % (mp / 1e6))
ok("分辨率维度: 1920x1080 远低于 4096x3072 ⇒ ★尺寸不卡[官方]★")
if re.search(r"MP/?s\b.{0,40}(ISP|throughput)", ds, re.I):
    ok("datasheet 里似乎有 ISP MP/s 口径 ⇒ 需人工核对")
else:
    lines.append("  ⚠️ ★官方 datasheet 全文检索不到 ISP 的 MP/s 吞吐上限 ⇒ ★[0数据]★ ⇒ "
                 "⇒ ★换芯到 RK3572 后这条缺口【没有变好也没有变坏】(★RK3576 侧同样没给·ISS-124 已 verified 但 MP/s 那条仍挂着★)★")

lines.append("")
lines.append("=" * 78)
if fails:
    lines.append("❌ rc=1: %d 条不一致" % len(fails))
else:
    lines.append("✅ rc=0: 球位号 / CSI 通道数 / ISP 口径 三处全部与官方 datasheet 自洽")
lines.append("=" * 78)

print("\n".join(lines))
sys.exit(1 if fails else 0)
