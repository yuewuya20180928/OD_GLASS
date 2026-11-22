#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SW/tools/check_demo_panel_spec.py — ISS-212 demo 显示侧口径门禁 (Waveshare 2.8")
=====================================================================
目的: 机械判定"demo 显示侧口径有没有被重锚到 Waveshare 2.8inch (SKU 22028) 480×640",
      防止 `SW/DEMO_OD_PIPELINE_SPEC.md` 悄悄回退到视涯 0.49" 1920×1080 口径
      (★2026-11-04 01:19 boss 已拍板 demo 屏换屏, 而 SW 侧当时零提及)。

★铁律 (SOUL.md):
  1. 本脚本 **不编板端时延数字** —— 它只核对**文档口径与自洽性**;
     所有被核对的数字 (60.85 Hz / 448.6 Mbps / 2.304 ms / 170px ...) 来自
     `SW/DEMO_PANEL_WAVESHARE_2P8_SPEC.md`, 本脚本只验"在位 / 不在位"。
  2. 退出码 0 = 全过; 1 = 有项不通过; 2 = 用法错误。

★判据 (四组 + 两道保护):
  R1  demo 屏规格真源: 480×640 / 2-lane / 无 DCS / I2C_B ≤100kHz 四条 + 附属必填项在位
  R2  demo 屏规格里 **不许** 把「视涯 / 1920×1080 / init code」当成 demo 活动口径
      (出现在整机路线·暂缓 / 历史 / 降级 段落里是允许的)
  R3  `SW/DEMO_OD_PIPELINE_SPEC.md` 里被定性表判成 demo 活动口径的那几处, 确实已经改掉
  R4  整机路线占位**不许被一把删掉** (视涯 0.49" 仍是整机屏 ⇒ 必须还在且带「整机路线·暂缓」)
  R5  逐处定性表本身完整 (22 处 grep 命中 + 16 处关联活动口径)
  R6  ★★【ISS-225】受保护真源三方对账 (锚点 ↔ 落表台账 ↔ 盘上真源, 一致才过) ★★
      机制照抄 `MECH/check_demo_struct_truth.py` 的 C21 (★只读参照, MECH/ 一个字节没碰★)
      锚点住在 `SW/SW_MD5_BASELINE_LEDGER.md` §1 (机器可读 YAML 块) ⇒ 不是脚本里的硬编码常量
      ① 网表 / 脚表 = 落表台账管理的真源 (锚点 ↔ 落表台账 ↔ 盘上, 三方必须一致)
      ② 板 / .kicad_pro = 落表明令不许碰 ⇒ 纯 md5 硬保护
      ⇒ ★只改锚点不落表 = 悄悄换真源 = 红; 改了真源不落表 = 悄悄换真源 = 红
  R7  ★★【ISS-225】已修复 (留痕) 必须在场 (删节 / 删行 / 抹 md5 / 抹判别标记 ⇒ 红) ★★

★★【ISS-225 重锚说明 (2026-11-16, sw-lead)】★★
  ★**这次红 = 【锚点过期】, 不是【红灯被调没】**: hw-lead 的 **ISS-220 落表
  (2026-11-16 02:32)** 真改了 `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv`
  (md5 `c78f9912…`→`13f59a43…` / `4814617e…`→`a600afae…`), 而本脚本的 R6 锚点还钉在
  落表前的旧 md5 ⇒ ★**门禁读旧数 = 假红** ⇒ 判别证据: ★**本脚本 mtime =
  2026-11-15 23:59 早于落表 02:32 ⇒ 脚本一个字节没被碰过** ★
  ⇒ ★**但"只把锚点里的 md5 换成新值" = 把门禁再废一次** ⇒ 所以升级成【台账驱动 +
  三方对账】(见 R6) ⇒ ★**锚点会再次过期 (ISS-223 落表后), 但台账对账机制会自动红,
  这是设计** ★ ⇒ 留痕账 = `SW/SW_MD5_BASELINE_LEDGER.md` §3

用法:
    python3 SW/tools/check_demo_panel_spec.py                # 核对 (rc=0 = 全过)
    python3 SW/tools/check_demo_panel_spec.py --selftest      # 自检 (反向用例必须全红)
    python3 SW/tools/check_demo_panel_spec.py --json          # 机读输出
    python3 SW/tools/check_demo_panel_spec.py --skip-md5      # 跳过 R6/R7 (hw-lead 合法改板后用; 默认不许跳过)
"""
from __future__ import annotations

import argparse
import copy
import glob
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))          # .../SW/tools
PROJ = os.path.dirname(os.path.dirname(HERE))              # .../<项目库根>

DEMO_SPEC = os.path.join("SW", "DEMO_PANEL_WAVESHARE_2P8_SPEC.md")
TRIAGE = os.path.join("SW", "DEMO_PANEL_SPEC_TRIAGE.md")
PIPELINE = os.path.join("SW", "DEMO_OD_PIPELINE_SPEC.md")

# ★整机路线占位区标记 (demo 屏规格里唯一允许出现整机口径的地方)
BLOCK_BEGIN = "<!-- BEGIN 整机路线占位区"
BLOCK_END = "<!-- END 整机路线占位区"

# ★"整机口径" token —— demo 活动口径里出现即判不合格 (除非带豁免标记)
LEGACY_TOKENS = ["视涯", "SeeYA", "1920×1080", "1920x1080", "init code"]
# ★豁免标记: 该行只要带其一, 说明它是整机路线占位 / 历史 / 降级说明 ⇒ 允许
EXEMPT_MARKERS = ["整机路线", "整机屏", "历史", "降级", "作废"]

# ★R1: demo 屏规格真源必含项 (每组至少命中一个)
R1_GROUPS = [
    ("分辨率 480×640", ["480×640", "480x640"]),
    ("DSI 2-lane", ["2-lane", "dsi,lanes = <2>"]),
    ("无 DCS init 序列", ["不需要任何 DCS init 序列", "零 DSI 写", "不需要任何 DCS"]),
    ("I2C_B ≤100kHz 硬上限", ["100 kHz", "100kHz"]),
    ("I2C 面板控制序列 0xC0/0xC2/0xAC", ["0xC0", "0xc0"]),
    ("I2C 面板控制序列 0xAD", ["0xAD", "0xad"]),
    ("I2C 背光 0xAB+0xAA", ["0xAB", "0xab"]),
    ("面板 I2C 地址 0x45", ["0x45"]),
    ("触摸 GT911 0x14", ["0x14"]),
    ("dts panel-timing 片段", ["panel-timing"]),
    ("Rockchip ST7701 GIP 参照件", ["ST7701", "st7701"]),
    ("板端 30 分钟验证清单", ["30 分钟"]),
    ("官方驱动出处", ["panel-waveshare-dsi.c", "d8e5eb49991de6b8fa9231532a11036e24aa84de"]),
    ("官方 compatible", ["waveshare,2.8inch-panel"]),
    ("DSC 结论 (RK3572 无 DSC 编码器)", ["DSC 编码器", "没有 DSC"]),
]

# ★R3: pipeline spec 里被定性表判成 demo 活动口径的那些行 —— (旧串必须消失, 新串必须出现)
R3_PAIRS = [
    ("面板 1920×1080", "demo 面板 480×640"),
    ("等比 letterbox 到 1920×1080", "等比 letterbox 到 ★**480×640"),
    ("视涯 1920×1080 (16:9)", "demo 面板 480×640 (3:4 竖屏"),
    ("k = min(1920/1920, 1080/1200) = 0.9", "k = min(480/1920, 640/1200) = 0.25"),
    ("左右各 96px", "上下各 170px"),
    ("左右各 240px", "上下各 140px"),
    ("左右各 96px (P1) / 240px (P2)", "上下各 170px (P1) / 140px (P2)"),
    ("drmModeAddFB (1920×1080", "drmModeAddFB (★**480×640**"),
    ("CRTC:  1920×1080@60", "480×640@60.85"),
    ("CRTC 有 1920×1080@60", "CRTC 有 480×640@60.85"),
    ("| 面板 mode | 1920×1080@60 | 1920×1080@60 |", "480×640@60.85 (2-lane)"),
    ("整块 1920×1080 buffer", "480×640 buffer"),
    ("压扁 1.111×", "压扁 2.13×"),
    ("含 CPU 侧 1920×1080 生成", "含 CPU 侧 ★**480×640** 生成"),
    ("左右各 96px (判据 ④)", "上下各 170px (P1) / 140px (P2)"),
    ('"display":  { "width": 1920, "height": 1080', '"display":  { "width": 480, "height": 640'),
    ('"line_px": 3', '"line_px": 8'),
    ("1px 在 0.49\" 高密度面板上几乎不可见", "P1 = **8 px**"),
    ("P2 路径的账 (640×480 → 1920×1080)", "P2 路径的账 (640×480 → 480×640)"),
    ("显示侧分两阶段", "显示侧不再分两阶段"),
    ("问询函外发比选 sensor 路径更紧急", "显示通路已无外部依赖"),
    ("面板 init code / 时序 | ★**未拿到**", "不需要任何 DCS init 序列"),
    ("把 `state/outbox/visionox_display_inquiry.md` 发出去", "一律不发"),
    ("先把 `state/outbox/visionox_display_inquiry.md` 发出去", "屏到手即按 30 分钟验证清单走"),
    ("RK3572 DSI + 视涯面板", "RK3572 DSI + ★**demo 屏 Waveshare 2.8\""),
    ("letterbox / 缩放 → 1920×1080 + DRM/KMS", "letterbox / 缩放 → ★**480×640** + DRM/KMS"),
    ("DSI TX + 面板 init code (I2C)", "面板 I2C 控制 (0x45, 不用 DCS init code)"),
]

# ★★【ISS-225】SW 侧 md5 基线台账 (★锚点住这儿, 不是硬编码常量★)
#   ★ 机制照抄 `MECH/check_demo_struct_truth.py` 的 C21 (★只读参照, MECH/ 一个字节没碰★)
#   ★ 锚点 = `SW/SW_MD5_BASELINE_LEDGER.md` §1 的机器可读 YAML 块 (改它 = 改判据 ⇒ 门禁会红)
LEDGER_DOC = os.path.join("SW", "SW_MD5_BASELINE_LEDGER.md")
ANCHOR_BEGIN = "# BEGIN SW_MD5_ANCHORS"
ANCHOR_END = "# END SW_MD5_ANCHORS"

# ★★【ISS-225】落表台账里必须能查到的四项 (缺一 ⇒ 查不到出处 ⇒ 红):
#   ① 落表单号 (`by`) ② 文件名 (`file`) ③ 新 md5 (`md5`) ④ 旧 md5 (`prev_md5`)
#   ★ 台账来源 = `HW/SCHEMATIC_LANDING_V1_LANDED.md` (ISS-220 落表记录) 或
#     `HANDOFF/2026-11-16_hw-lead_ISS223_*.md` (ISS-223 落表第 2 批) —— 两者都在锚点里登记
LEDGER_REQUIRED_ITEMS = ("by", "file", "md5", "prev_md5")


def read_text(root: str, rel: str) -> str:
    path = os.path.join(root, rel)
    if not os.path.exists(path):
        raise FileNotFoundError("文件不存在: %s" % path)
    with open(path, encoding="utf-8") as f:
        return f.read()


def md5_of(root: str, rel: str) -> str:
    h = hashlib.md5()
    with open(os.path.join(root, rel), "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------- ISS-225 台账对账工具
def load_sw_anchor(root: str):
    """读 SW 侧 md5 基线台账 §1 的机器可读锚点。★读不到 ⇒ (None, 原因) ⇒ 门禁 fail-closed 红★"""
    path = os.path.join(root, LEDGER_DOC)
    if not os.path.exists(path):
        return None, "SW 侧 md5 基线台账不存在: %s" % LEDGER_DOC
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except OSError as exc:
        return None, "SW 侧 md5 基线台账读不了: %s (%s)" % (LEDGER_DOC, exc)
    m = re.search(re.escape(ANCHOR_BEGIN) + r"(.*?)" + re.escape(ANCHOR_END), text, re.S)
    if not m:
        return None, "台账里找不到锚点块 (%s ... %s)" % (ANCHOR_BEGIN, ANCHOR_END)
    try:
        import yaml
    except ImportError as exc:
        return None, "PyYAML 不可用, 读不了锚点块 (%s)" % exc
    try:
        data = yaml.safe_load(m.group(1))
    except Exception as exc:                       # ★解析失败 ⇒ fail-closed 红, 不许当"没锚点就跳过"★
        return None, "锚点块 YAML 解析失败: %s" % exc
    anchors = (data or {}).get("anchors")
    if not isinstance(anchors, dict):
        return None, "锚点块里没有 anchors 段 (或格式不对)"
    return anchors, ""


def load_ledger_records(root: str, anchors: dict) -> list:
    """把锚点里登记的落表台账位置逐个读出来 (支持 `*` 通配)。"""
    recs = []
    specs = ((anchors.get("source_ledger") or {}).get("landing_records")) or []
    for spec in specs:
        if not spec:
            continue
        p = os.path.join(root, spec)
        if os.path.isfile(p):
            recs.append((spec, read_text(root, spec)))
            continue
        d = os.path.dirname(spec) or "."
        b = os.path.basename(spec)
        for hit in sorted(glob.glob(os.path.join(root, d, b))):
            rel = os.path.relpath(hit, root)
            recs.append((rel, read_text(root, rel)))
    return recs


def md5_seen(text: str, value: str) -> bool:
    """落表台账里是不是出现了这个 md5 (全文或 12 位前缀 —— 落表记录用的是前缀)。"""
    if not value:
        return False
    return value in text or value[:12] in text


def ledger_row_has(text: str, fname: str, new_md5: str, prev_md5: str) -> bool:
    """落表台账里有没有**同一行**同时写着 文件名 + 新 md5 + 旧 md5 (四项缺一 ⇒ 不算查到)。"""
    for line in text.split("\n"):
        if fname and fname not in line:
            continue
        if not md5_seen(line, new_md5):
            continue
        if prev_md5 and not md5_seen(line, prev_md5):
            continue
        return True
    return False


def block_mask(text: str) -> list[bool]:
    """返回每行是否落在「整机路线占位区」块内。"""
    mask = []
    inside = False
    for line in text.split("\n"):
        if BLOCK_BEGIN in line:
            inside = True
            mask.append(True)
            continue
        if BLOCK_END in line:
            inside = False
            mask.append(True)
            continue
        mask.append(inside)
    return mask


# ---------------------------------------------------------------- R1
def check_r1_demo_spec_core(root: str) -> list[str]:
    fails = []
    try:
        text = read_text(root, DEMO_SPEC)
    except FileNotFoundError as exc:
        return ["R1 读不到 %s (%s)" % (DEMO_SPEC, exc)]
    for label, alts in R1_GROUPS:
        if not any(alt in text for alt in alts):
            fails.append("R1 demo 屏规格缺 %s (期望其中之一: %s)" % (label, " / ".join(alts)))
    return fails


# ---------------------------------------------------------------- R2
def check_r2_no_active_legacy(root: str) -> list[str]:
    fails = []
    try:
        text = read_text(root, DEMO_SPEC)
    except FileNotFoundError as exc:
        return ["R2 读不到 %s (%s)" % (DEMO_SPEC, exc)]
    mask = block_mask(text)
    if BLOCK_BEGIN not in text or BLOCK_END not in text:
        fails.append("R2 demo 屏规格缺少「整机路线占位区」标记块 (%s / %s)" % (BLOCK_BEGIN, BLOCK_END))
    for idx, line in enumerate(text.split("\n")):
        if not any(tok in line for tok in LEGACY_TOKENS):
            continue
        if mask[idx]:
            continue                                   # 在占位区块内 ⇒ 允许
        if any(mark in line for mark in EXEMPT_MARKERS):
            continue                                   # 带「整机路线/整机屏/历史/降级/作废」标注 ⇒ 允许
        fails.append("R2 demo 屏规格第 %d 行把整机口径当 demo 活动口径: %s"
                     % (idx + 1, line.strip()[:90]))
    return fails


# ---------------------------------------------------------------- R3
def check_r3_pipeline_reanchored(root: str) -> list[str]:
    fails = []
    try:
        text = read_text(root, PIPELINE)
    except FileNotFoundError as exc:
        return ["R3 读不到 %s (%s)" % (PIPELINE, exc)]
    for old, new in R3_PAIRS:
        if old in text:
            fails.append("R3 pipeline spec 仍留旧 demo 口径: %r (定性表已判为 demo 活动口径, 必须改掉)" % old)
        if new not in text:
            fails.append("R3 pipeline spec 缺新口径: %r (定性表要求的现行写法)" % new)
    return fails


# ---------------------------------------------------------------- R4
def check_r4_整机_placeholder_kept(root: str) -> list[str]:
    fails = []
    try:
        text = read_text(root, PIPELINE)
    except FileNotFoundError as exc:
        return ["R4 读不到 %s (%s)" % (PIPELINE, exc)]
    if "视涯" not in text:
        fails.append("R4 整机路线占位被删掉了 —— 视涯 0.49\" 仍是整机屏 (整机路线·暂缓), 不许一把删掉")
    n = text.count("整机路线·暂缓")
    if n < 5:
        fails.append("R4 pipeline spec 的「整机路线·暂缓」标注只有 %d 处 (<5) ⇒ 整机占位没标全" % n)
    try:
        demo = read_text(root, DEMO_SPEC)
    except FileNotFoundError as exc:
        return fails + ["R4 读不到 %s (%s)" % (DEMO_SPEC, exc)]
    if "整机路线" not in demo:
        fails.append("R4 demo 屏规格里没有「整机路线」占位段 ⇒ 整机屏口径被抹掉了")
    return fails


# ---------------------------------------------------------------- R5
def check_r5_triage_table(root: str) -> list[str]:
    fails = []
    try:
        text = read_text(root, TRIAGE)
    except FileNotFoundError as exc:
        return ["R5 读不到 %s (%s)" % (TRIAGE, exc)]
    missing = [f"L-{i:02d}" for i in range(1, 23) if f"L-{i:02d}" not in text]
    missing += [f"X-{i:02d}" for i in range(1, 17) if f"X-{i:02d}" not in text]
    if missing:
        fails.append("R5 逐处定性表缺条目: %s" % ", ".join(missing))
    for need in ("22 处", "16 处", "38 处"):
        if need not in text:
            fails.append("R5 逐处定性表缺统计口径 %r (22 grep 命中 + 16 关联活动口径 = 38 处)" % need)
    if "整机路线·暂缓" not in text:
        fails.append("R5 逐处定性表缺「整机路线·暂缓」分类口径")
    return fails


# ====================================================================== 落表台账判决源 (ISS-275)
#  ★★【ISS-275 · 2026-11-17 · sw-lead】★★ R6 的【判决源】从「域侧锚点副本」换成
#    「落表台账里该受管真源的最新落表记录 (链头)」:
#      · 机制照抄 `MECH/check_demo_struct_truth.py` 的 C21 (★只读参照, MECH/ 一个字节没碰★
#        ★但本文件【自己写】, 不许 import MECH 的脚本 —— 那是别人地界★)
#      · 落表记录 = 落表台账里该文件的【改前 md5 → 改后 md5】表格行 (★行内第一个 md5 = 前驱,
#        最后一个 = 改后★)
#      · 链头 = 「不是任何记录的前驱」的那个改后 md5 ⇒ ★**判最新靠【图】不靠【行序】** ★
#        ⇒ 台账行序被打乱 / 小节顺序变了, 都不影响取哪一条
#      · ★判决源台账 = `HW/SCHEMATIC_LANDING_V1_LANDED.md` (★只读★; ★只读这一份 ——
#        把交接单里的零散 md5 行混进来会把链打断 ⇒ 假红★)
#      · ★域侧锚点副本 (`SW/SW_MD5_BASELINE_LEDGER.md` §1 `entries[]`) 降级为【历史留痕】:
#        允许停在历史值, 但不许胡说 (md5 必须在台账链上 + 落表单号必须与台账对得上)
LEDGER_CANON = os.path.join("HW", "SCHEMATIC_LANDING_V1_LANDED.md")
LEDGER_MD_RE = re.compile(r"\b[0-9a-f]{32}\b|\b[0-9a-f]{12}\b")
# ★受管真源的【文件名】(★不是 md5 值★ —— md5 值 100% 来自落表台账, 脚本里不许再写死一个 md5★)
LEDGER_REQUIRED = ("HW/netlist_v1.csv", "HW/netlist_v1_pins.csv")


def sw_ledger_records(text: str, rel: str) -> list:
    """从落表台账文本里抽出 rel 的落表记录 ⇒ [{'prev','new','iss','sec','row'}] (★行序无关★)。

    ★口径 (照 MECH C21, 但本文件自己写)★: 只认表格行 (行首 `|`) · 一行里必须有
      【文件名】+【至少两个 md5】(第一个 = 改前, 最后一个 = 改后) · 落表单号取行内 `ISS-xxx`,
      行内没写就继承最近的带单号小节标题。
    """
    out: list = []
    ctx_iss = None              # ★最近的带单号标题 ⇒ 批次单号 (行里没写单号时继承它)
    sec = "(文首)"
    base = os.path.basename(rel)
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("#"):
            sec = s
            hit = re.findall(r"ISS-\d+", s)
            if hit:
                ctx_iss = hit[0]
            continue
        if not s.startswith("|"):
            continue
        if rel not in s and base not in s:
            continue
        toks = LEDGER_MD_RE.findall(s)
        if len(toks) < 2:
            continue              # ★只有一个 md5 ⇒ 不是「改前→改后」记录行★
        row_iss = re.findall(r"ISS-\d+", s)
        out.append({"prev": toks[0][:12], "new": toks[-1][:12],
                    "iss": row_iss[0] if row_iss else ctx_iss,
                    "sec": sec, "row": s[:160]})
    return out


def sw_ledger_state(rel: str, text: str, recs=None) -> dict:
    """算该受管真源在落表台账里的链头 / 链 / 产出单号表 (★取不准 ⇒ head=None ⇒ 判红★)。

    ★【ISS-284】`recs` 可外传 ⇒ 硬保护段用【只含改前≠改后的变更行】算链 (★受管真源的读数一字未变★)。
    """
    if recs is None:
        recs = sw_ledger_records(text, rel)
    new_keys = {r["new"] for r in recs}
    prev_keys = {r["prev"] for r in recs}
    heads = sorted(new_keys - prev_keys)
    producer: dict = {}
    for r in recs:
        producer.setdefault(r["new"], set())
        if r["iss"]:
            producer[r["new"]].add(r["iss"])
    why = ""
    head = None
    if not recs:
        why = "台账里一条记录都没有"
    elif not heads:
        why = "没有链头 (每条记录都是别人的前驱 ⇒ 台账不成链)"
    elif len(heads) > 1:
        why = "链头不唯一 = %s (取不准 ⇒ 不许判绿)" % (heads,)
    else:
        head = heads[0]
    chain: list = []
    if head:
        by_new: dict = {}
        for r in recs:
            by_new.setdefault(r["new"], []).append(r)
        cur, seen = head, {head}
        chain = [head]
        while True:
            rs = by_new.get(cur) or []
            if not rs:
                break                 # 链尾 (起源值, 没有产出记录)
            prevs = {r["prev"] for r in rs if r["prev"] != r["new"]}
            if len(prevs) != 1:
                why = why or "链上 %s 的前驱不唯一 = %s" % (cur, sorted(prevs))
                chain = []
                break
            p = prevs.pop()
            if p in seen:
                why = why or "链成环 (%s)" % p
                chain = []
                break
            cur = p
            seen.add(cur)
            chain.append(cur)
    return {"records": recs, "head": head, "chain": chain, "producer": producer,
            "why": why, "head_iss": sorted(producer.get(head, set())) if head else [],
            "known": new_keys | prev_keys}


def sw_ledger_canonical_text(root: str, anchors: dict) -> tuple:
    """取判决源台账文本 + 它的 spec 名 (★默认 HW/SCHEMATIC_LANDING_V1_LANDED.md, ★只读★)。"""
    if os.path.isfile(os.path.join(root, LEDGER_CANON)):
        return read_text(root, LEDGER_CANON), LEDGER_CANON
    for name, text in load_ledger_records(root, anchors):
        return text, name
    return "", LEDGER_CANON


# ★★【ISS-284 · 2026-11-17 · sw-lead】★★ ★硬保护件 (板 / .kicad_pro) 的【合法改板】机制★
#   ★ 老板 2026-11-17 09:49 拍板「按照你的建议执行」⇒ P10 = 方案 ②:
#     保留纯 md5 硬保护, 但把「合法改板」做成一个【显式的、由单号背书的动作】★
#   ★ 一条合法改板记录 = 【单号 by + 文件名 file + 改前 md5 prev_md5 + 改后 md5 md5】四件
#     捆在锚点 `hard_protected[].reboard` 这**一个原子映射**里
#     (★不许拆成两个可各自独立编辑的字段 —— 那就是 ISS-279 点名的缝★)
#   ★ 同一份四项必须能在落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` 的【同一行】里查到
#     (★台账是 append-only 的信任边界; 锚点自己不能说了算★)
#   ★ 判据方向不许变: 盘上 ≠ 台账链头 ⇒ 红 (★合法改板只是让【链头前移】, 不是把判据放松★)
#   ★ fail-closed 三条一条不许动: 链头不唯一 / 链断 / 链头无单号 ⇒ 红
REBOARD_FIELDS = ("by", "file", "prev_md5", "md5")


def m12(value) -> str:
    """md5 归一到 12 位小写前缀 (★落表台账里落表记录用的就是前缀★)。"""
    return str(value or "").strip().lower()[:12]


def sw_ledger_cover_rows(text: str, rel: str) -> list:
    """落表台账里提到 rel 的【覆盖行】(表格行 + 至少一个 md5) ⇒ [{'md5s','iss','sec','row'}]。

    ★口径与 `sw_ledger_records` 同源 (只认表格行 · 文件名同行 · 单号取行内 ISS-xxx 或最近带单号小节)★
    ★与 `sw_ledger_records` 的差别: 允许【只有一个 md5】的行 (★「逐字节不变」声明行就是这么写的★)★
    """
    out: list = []
    ctx_iss = None
    sec = "(文首)"
    base = os.path.basename(rel)
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("#"):
            sec = s
            hit = re.findall(r"ISS-\d+", s)
            if hit:
                ctx_iss = hit[0]
            continue
        if not s.startswith("|"):
            continue
        if rel not in s and base not in s:
            continue
        toks = LEDGER_MD_RE.findall(s)
        if not toks:
            continue
        row_iss = re.findall(r"ISS-\d+", s)
        out.append({"md5s": [m12(t) for t in toks],
                    "iss": row_iss[0] if row_iss else ctx_iss,
                    "sec": sec, "row": s[:160], "full": s})
    return out


def sw_ledger_change_rows(text: str, rel: str, exclude_aliases=()) -> list:
    """落表台账里 rel 的【变更行】(★改前 md5 ≠ 改后 md5★) ⇒ 合法改板只认这种行。

    ★`exclude_aliases` = 同组其它受保护件的名字别名 ⇒ ★一行两件两值 = 歧义行 ⇒ 不算变更行★
      (★例: 落表台账里有一行同时写了板与 `.kicad_pro` 的两个 md5 ⇒ 那不是「板改过」的记录★)
    """
    out: list = []
    for r in sw_ledger_cover_rows(text, rel):
        toks = r["md5s"]
        if len(toks) < 2:
            continue
        prev, new = toks[0], toks[-1]
        if prev == new:
            continue
        if any(a and a in r["full"] for a in exclude_aliases):
            continue
        out.append({"prev": prev, "new": new, "iss": r["iss"],
                    "sec": r["sec"], "row": r["row"]})
    return out


def sw_ledger_change_state(rel: str, text: str, exclude_aliases=()) -> dict:
    """变更行上的链头 / 链 / 产出单号表 (★只认改前≠改后的行★; 取不准 ⇒ head=None ⇒ 判红★)。"""
    return sw_ledger_state(rel, text,
                            recs=sw_ledger_change_rows(text, rel, exclude_aliases))


# ★★【ISS-312 · 2026-11-18 · sw-lead】★★ 链头落表单号的【交叉核对】(★修法 A + B★)
#   ★**病灶 (ISS-309 已 verified · main 05:4x 本机复跑)**: 判据对【链头落表单号】**只有「非空」一道检查**
#     ⇒ 单号被改坏 (假号 / 多个号 / 与真源不一致) **一律判绿** ⇒ ★那是漏放 (假绿)★
#   ★**修法 A (治「台账自相矛盾」)**: 链头产出单号必须【唯一】⇒ 同一个 md5 被两个不同单号声称产出
#     ⇒ 台账自相矛盾 ⇒ fail-closed 判红 (★与已有的「链头不唯一 ⇒ 红」同款语义★)
#   ★**修法 B (治「台账自洽但单号是假的」)**: 链头单号必须与【独立信源】对上
#     ⇒ ★**独立信源 = `state/issue_log.yaml`** (★main 维护 · 只读 · 与被测对象无关 ⇒ 不是自证★)
#        ① 该单号在 issue_log 里【存在】 ⇒ 假单号 (ISS-9900 之类) 当场露馅
#        ② 该单在 issue_log 里的留痕必须提到【这个文件】+【这个链头 md5】
#           ⇒ 真实存在但对不上的单号 (★换了另一个真 ISS 号★) 也露馅
#   ★**纪律**: ★不许拿「桶名拼写」当反向用例 · 不许拿判据自己判自己 · 不许拿同一份台账的两个副本互证★
ISSUE_LOG_REL = os.path.join("state", "issue_log.yaml")
_ISSUE_LOG_CACHE: dict = {}


def sw_issue_log_path(root: str) -> str:
    """独立信源 issue_log 的路径 (★树里有自己的就用自己的; 没有就退回本仓的 (★只读★)★)。

    ★为什么要这个退回★: 反向用例在临时树上跑 (★临时树只拷被测的那几个文件★)
      ⇒ 树里没有 `state/issue_log.yaml` ⇒ 退回本仓那份 ⇒ ★信源仍然是【真 issue_log】(★独立于被测对象★)
      ⇒ ★真盘跑的时候 root == PROJ ⇒ 两条路径指向同一个文件, 口径一致★ ★[实测]
    """
    p = os.path.join(root, ISSUE_LOG_REL)
    if os.path.isfile(p):
        return p
    return os.path.join(PROJ, ISSUE_LOG_REL)


def sw_issue_log_entries(root: str) -> dict:
    """把独立信源 issue_log 切成 {ISS-xxx: 那一整条的原文} (★按文本切, 不用 yaml 解析★)。

    ★为什么按文本切★: `state/issue_log.yaml` 有 3 MB / 309 条 ⇒ yaml.safe_load 要 1 秒多
      ⇒ ★本判据每次跑都要读它 ⇒ 按文本切只按行扫, 几十毫秒★ ★[实测]
    ★切法★: `issues:` 之后、列 0 的 `- ` 开头的行 = 一条 issue 的开始
      (★注意: 有些条的 `id:` 写在条目的【末尾】(★例 ISS-081★) ⇒ 不能拿 `id:` 行切, 要拿 `- ` 行切★)
    """
    path = sw_issue_log_path(root)
    key = os.path.abspath(path)
    hit = _ISSUE_LOG_CACHE.get(key)
    if hit is not None:
        return hit
    out: dict = {}
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except OSError:
        _ISSUE_LOG_CACHE[key] = out
        return out
    i = text.find("\nissues:")
    if i >= 0:
        chunks: list = []
        cur: list = []
        for line in text[i:].splitlines():
            if line.startswith("- "):
                if cur:
                    chunks.append("\n".join(cur))
                cur = [line]
            elif cur:
                cur.append(line)
        if cur:
            chunks.append("\n".join(cur))
        for ch in chunks:
            # ★`id:` 行有两种写法: 条目首行的 `- id: ISS-xxx` (★多数★) 与条目末尾的 `  id: ISS-xxx` (★例 ISS-081★)
            m = re.search(r"^\s*(?:-\s*)?id:\s*['\"]?(ISS-\d+)['\"]?\s*$", ch, re.M)
            if m:
                out[m.group(1)] = ch
    _ISSUE_LOG_CACHE[key] = out
    return out


def sw_chain_head_iss_check(root: str, rel: str, head: str, head_iss, tag: str,
                            cross_check_source: bool = True) -> list[str]:
    """★【ISS-312】链头落表单号的【交叉核对】(★修法 A + B★) ⇒ 红项列表 (★绿 = 空列表★)。

    ★`tag` = 报错前缀 (★"R6 台账链" / "R6 硬保护"★) ⇒ 两处判决点用同一套口径 ★
    ★`cross_check_source` = 做不做【修法 B】(★与独立信源 issue_log 对账★):
      · True  ⇒ ★两条路径都做 (★落表真源 `check_r6_three_way` + 硬保护 `check_r6_hard_protected`★)
      · False ⇒ ★只判 A (★保留这个开关: 判据方向一条不许改, 只是 ISS-315 起没人用它了★)
        ★★【ISS-315 · 2026-11-18 · sw-lead】★★ 硬保护那条路径【原来只判 A】⇒ ★ISS-312 收回了 B★
          ⇒ ★ISS-315 先【修夹具】(★`SW/tools/check_onepass_sw_sync.py` 的 ⑮ 与本文件自己的 REV-21
            两个合法改板正向用例都补上了【独立信源】输入★)⇒ ★然后把 B 铺到硬保护路径★
          ⇒ ★ISS-312 当时写的两条理由, 现在这样收口★:
            ① 「夹具不在可写范围」⇒ ★已解★ (夹具本单可写 ⇒ 假伤修在夹具上, 判据本体只【加】不【改】★)
            ② 「硬保护那条路径的票 = 合法改板票 ⇒ 加 B 等于给板那一趟加一条新义务」⇒ ★已解★
              (★那条义务 = 【落表单必须在 issue_log 里留【文件名 + 新 md5】】★ ⇒ ★ISS-315 同单
               把它做成了机器可判的新闸 `SW/tools/check_landing_trace_obligation.py`★ ⇒ ★义务落地, 不再是口号★)
    ★「缺单号」不归本函数管 (★由原有的「缺落表单号」红项负责★) ⇒ 本函数只管【有单号但单号不对】★
    """
    fails: list[str] = []
    head_iss = list(head_iss or [])
    # ---- 修法 A: 链头产出单号必须唯一 (⇒ 治「台账自相矛盾」) ----
    if len(head_iss) > 1:
        fails.append("%s: %s 台账最新记录 (%s) 的落表单号不唯一 = %s ⇒ 同一条落表记了 %d 个单号 "
                     "(★台账自相矛盾 ⇒ 判红★)" % (tag, rel, head, head_iss, len(head_iss)))
        return fails            # ★单号本身都不可信了 ⇒ 下面那个独立信源对账没有意义 (★不多报噪声红★)
    if not head_iss:
        return fails            # ★没单号 ⇒ 走原有的「缺落表单号」红项★
    if not cross_check_source:
        return fails            # ★这条路径只判 A (★理由见上面的 docstring★)★
    iss = head_iss[0]
    # ---- 修法 B: 链头单号必须与【独立信源 issue_log】对上 ----
    entries = sw_issue_log_entries(root)
    if not entries:
        fails.append("%s: %s 台账最新记录 (%s) 的落表单号 %s 在独立信源 (%s) 里查不到任何条目 "
                     "⇒ 无从对账 (fail-closed ⇒ 判红)" % (tag, rel, head, iss, ISSUE_LOG_REL))
        return fails
    ch = entries.get(iss)
    if not ch:
        fails.append("%s: %s 台账最新记录 (%s) 的落表单号 %s 在独立信源 (%s) 里查不到 "
                     "⇒ 单号是假的 (★判红★)" % (tag, rel, head, iss, ISSUE_LOG_REL))
        return fails
    base = os.path.basename(rel)
    if base not in ch:
        fails.append("%s: %s 台账最新记录 (%s) 的落表单号 %s 在独立信源里没有 %s 的落表留痕 "
                     "⇒ 单号与真源对不上 (★判红★)" % (tag, rel, head, iss, base))
        return fails
    if not (head[:12] in ch or head[:8] in ch):
        fails.append("%s: %s 台账最新记录 (%s) 的落表单号 %s 在独立信源里没有 %s 的留痕 "
                     "(独立信源只认得旧 md5 ⇒ 挂错单 ⇒ 判红★)" % (tag, rel, head, iss, head[:12]))
    return fails


# ★★【ISS-315 · 2026-11-18 · sw-lead】★★ 沙盒夹具的【独立信源】输入 (★假伤修夹具 · 判据本体不动★)
def sw_current_landing_ticket(root: str) -> str:
    """★当前【真】落表单号 (★动态取自落表台账链头 ⇒ 一个单号都不许硬编码★)。

    ★口径 (★判决源口径 · ISS-275★)★: 落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` 里
      【网表】的链头产出单号 ⇒ ★**不是**锚点副本里的历史单号 (★那是历史留痕, 不是当前落表单★)
    ★取不到 ⇒ 返回 "" (★调用方自己判: 夹具坏了 ⇒ 断言失败, 不许猜一个单号★)
    """
    try:
        led = read_text(root, LEDGER_CANON)
    except OSError:
        return ""
    st = sw_ledger_state(LEDGER_REQUIRED[0], led)
    iss = sorted(st.get("head_iss") or [])
    return iss[0] if iss else ""


def sw_fresh_hard_ticket(root: str) -> str:
    """★一个【真单号】(★在 issue_log 真条目里查得到★) 且【从没落过任何硬保护件】的单号 ★

    ★★为什么要「从没落过硬保护件」★★: 硬保护段第 ④ 条 = 【同一次合法改板必须覆盖同组全部件】
      ⇒ ★落表台账里 ISS-220 / 233 / 243 / 249 / 257 / 236 / 283 / 302 都落过 .kicad_pro★
      ⇒ ★拿这其中任何一个当夹具单号 ⇒ 「只改板不动 .kicad_pro」那条用例 (REV-20 / ⑭)
        会被判绿 (★因为那个单号在旧台账里已经落过 .kicad_pro 了★) ⇒ ★用例自己就废了★
      ⇒ ★夹具必须用一个【对硬保护件来说是新的】真单号★
    ★挑法★: 真 issue_log 里【编号最大】且【没落过硬保护件】的那个单号
      (★动态取 ⇒ 一个单号都不许硬编码★ · ★口径会自己跟着盘面走: 哪天它落了硬保护件, 就换下一个★)
    ★取不到 ⇒ 返回 "" (★调用方自己判: 夹具坏了 ⇒ 断言失败, 不许猜一个单号★)
    """
    try:
        led = read_text(root, LEDGER_CANON)
    except OSError:
        led = ""
    issuers = set()
    for rel in (BOARD_REL, PRO_REL):
        for r in sw_ledger_cover_rows(led, rel):
            if r["iss"]:
                issuers.add(r["iss"])
    for iss in sorted(sw_issue_log_entries(root).keys(), reverse=True):
        if iss not in issuers:
            return iss
    return ""


def sw_sandbox_issue_log(dst_path: str, ticket: str, traces) -> str:
    """把【真 issue_log】拷成沙盒件, 并在【真单号 ticket】的条目里补上【落表留痕行】。

    ★★为什么必须有这个 (★ISS-315 病灶①★)★★:
      ISS-315 把【修法 B】(链头单号 ↔ 独立信源交叉核对) 铺到【硬保护路径】之后
      ⇒ 「合法改板 ⇒ 放行」的正向用例 (★ISS-298 闸的第 ⑮ 条 + 本文件自己的 REV-21★)
        少了【独立信源】这一份输入 ⇒ 假红 (★红在【夹具缺输入】, 不在【判据方向】★)
      ⇒ ★按 ISS-309 铁律: 假伤修夹具, 不许改判据★ ⇒ ★这里【只补输入】★
    ★补的是什么★: ★**真** issue_log 的拷件 + 【真单号】条目里的一行【落表留痕】
      (★文件名 + 改前 md5 + 改后 md5★) ★⇒ ★这正是 main 落表时会写的那一行★
    ★真盘一个字节都不动★: 写的是沙盒路径 (dst_path) ⇒ ★`state/issue_log.yaml` 真身只读★
    ★`traces` = [(相对路径, 改前 md5, 改后 md5), ...] ★
    """
    src = sw_issue_log_path(PROJ)
    with open(src, encoding="utf-8") as f:
        text = f.read()
    marker = "\nissues:"
    i = text.find(marker)
    if i < 0:
        raise AssertionError("真 issue_log %s 里找不到 issues: 段" % src)
    rest = text[i + len(marker):]
    lines = rest.splitlines(keepends=True)
    pre: list = []
    pos = 0
    for line in lines:
        if line.startswith("- "):
            break
        pre.append(line)
        pos += 1
    blocks: list = []
    cur: list = []
    for line in lines[pos:]:
        if line.startswith("- "):
            if cur:
                blocks.append("".join(cur))
            cur = [line]
        elif cur:
            cur.append(line)
    if cur:
        blocks.append("".join(cur))
    payload = "ISS-315 夹具补输入: 落表留痕 " + " ; ".join(
        "%s prev=%s new=%s" % (rel, str(prev)[:12], str(new)[:12]) for rel, prev, new in traces)
    trace_line = "  landing_trace_iss315: '%s'\n" % payload
    hit = 0
    for idx, ch in enumerate(blocks):
        m = re.search(r"^\s*(?:-\s*)?id:\s*['\"]?(ISS-\d+)['\"]?\s*$", ch, re.M)
        if not (m and m.group(1) == ticket):
            continue
        lines2 = ch.splitlines(keepends=True)
        blocks[idx] = "".join(lines2[:1]) + trace_line + "".join(lines2[1:])
        hit += 1
        break
    if not hit:
        raise AssertionError("真单号 %s 在真 issue_log (%s) 里查不到 ⇒ 夹具自己坏了" % (ticket, src))
    os.makedirs(os.path.dirname(os.path.abspath(dst_path)), exist_ok=True)
    with open(dst_path, "w", encoding="utf-8") as f:
        f.write(text[:i] + marker + "".join(pre) + "".join(blocks))
    return dst_path


def check_r6_hard_protected(root: str, anchors: dict, led_text: str, led_spec: str) -> list[str]:
    """R6 硬保护段 (板 / .kicad_pro): ★【ISS-284 · P10 = 方案 ②】合法改板机制★。

    ★★判据 (逐条; ★fail-closed: 取不准一律判红★)★★
      ① ★保护基线自证★: 锚点里的基线 md5 必须能在落表台账里与该文件【同行】查到
         ⇒ ★只改锚点里的 md5 而台账没记 ⇒ 红★ (★这就是「挖坑」那条路, 必须堵死★)
      ② ★台账里该文件没有变更行★ ⇒ 不许有 reboard 记录; 且 盘上 md5 必须 == 基线 (★纯 md5 硬保护★)
      ③ ★台账里有变更行★ ⇒ 链头必须唯一 / 链不断 / 链头有单号 (★fail-closed 三条一条不许动★)
         ⇒ 锚点必须带 reboard 原子记录 (★四项缺一 ⇒ 红★) ⇒ 且四项必须与台账链头逐字对上
         ⇒ 保护基线必须留在链尾 (★不许把基线偷偷前移★)
         ⇒ 盘上 md5 必须 == 台账链头 (★判据方向不许变: 合法改板只是让链头前移★)
      ④ ★同组受保护件覆盖★: 一次合法改板必须覆盖同组全部件 (★只来一条记录 ⇒ 红★)
    """
    fails: list[str] = []
    hard = list(anchors.get("hard_protected") or [])
    if not hard:
        return ["R6 硬保护: 锚点里没有 hard_protected 段 (板 / .kicad_pro 失保护)"]

    group: list = []
    # ★同组受保护件的名字别名 (★用于剔「一行两件两值」的歧义行★)
    aliases: dict = {}
    for e in hard:
        r0 = str(e.get("file") or "")
        if not r0:
            continue
        b0 = os.path.basename(r0)
        aliases[r0] = {r0, b0, os.path.splitext(b0)[1]}
    for e in hard:
        rel = str(e.get("file") or "")
        base = str(e.get("md5") or "")
        rec = e.get("reboard")
        if not rel or not base:
            fails.append("R6 硬保护: hard_protected 条目缺 file/md5: %r" % (e,))
            continue
        if not os.path.exists(os.path.join(root, rel)):
            fails.append("R6 硬保护: 受保护文件不存在: %s" % rel)
            continue
        got = md5_of(root, rel)
        excl = set()
        for other, al in aliases.items():
            if other != rel:
                excl |= al
        covers = sw_ledger_cover_rows(led_text, rel) if led_text else []
        chg = sw_ledger_change_rows(led_text, rel, excl) if led_text else []
        group.append({"rel": rel, "base": base, "rec": rec, "got": got,
                      "covers": covers, "chg": chg, "excl": excl})
        # ① 保护基线自证 (★只改锚点里的 md5 而台账没记 ⇒ 红★)
        if led_text and not any(m12(base) in r["md5s"] for r in covers):
            fails.append("R6 硬保护: %s 的保护基线 md5 %s 在落表台账 (%s) 里查不到 ⇒ "
                         "锚点被单独改了 (★只改 md5 不落表 = 悄悄换真源 = 红★)"
                         % (rel, m12(base), led_spec))

    if not led_text:
        fails.append("R6 硬保护: 判决源落表台账读不到 (%s) ⇒ 无从对账 (fail-closed)" % led_spec)
        return fails

    heads: dict = {}
    for g in group:
        rel, base, rec, got = g["rel"], g["base"], g["rec"], g["got"]
        chg = g["chg"]
        if not chg:
            # ② 台账里没有变更行 ⇒ 不许有 reboard 记录; 盘上必须还是基线
            if rec not in (None, "", {}, []):
                fails.append("R6 硬保护: %s 锚点里有合法改板记录 (reboard) 但落表台账里查不到任何变更行 "
                             "⇒ 单号背书落不了地 = 红" % rel)
            if got[:12] != m12(base):
                fails.append("R6 硬保护: 受保护文件 md5 变了: %s (%s ≠ %s)" % (rel, got, base))
            continue
        # ③ 台账里有变更行 ⇒ 走【合法改板】路径
        st = sw_ledger_change_state(rel, led_text, g["excl"])
        head = st.get("head")
        if not head:
            fails.append("R6 硬保护: %s 台账最新记录取不准 (%s) ⇒ 取错记录可能假绿 ⇒ 判红"
                         % (rel, st.get("why")))
            continue
        heads[rel] = head
        if not st.get("head_iss"):
            fails.append("R6 硬保护: %s 台账最新记录 (%s) 缺落表单号 (字段缺失)" % (rel, head))
        # ★★【ISS-312】链头落表单号的【交叉核对 · 修法 A】⇒ 治「同一个 md5 被两个单号抢」★
        # ★★【ISS-315 · 2026-11-18 · sw-lead】★★ 修法 B (与独立信源 issue_log 对账) 【铺到这条路径】★
        #   ⇒ ★硬保护路径上的链头单号也必须是【真单号 + 真留痕 (文件名 + 链头 md5)】★
        #   ⇒ ★否则【板 md5 合法变更时, 这条路径会漏放假单号】★ (★那正是「板只改一次」那一趟★
        #     要用的判据 ⇒ ★ISS-315 的来由★)
        #   ★夹具已先修好 (★`check_onepass_sw_sync.py` 的 ⑮ 与本文件的 REV-21 都补了【独立信源】输入★)
        #     ⇒ ★判据方向一条没改 · fail-closed 三条一条没动 ★ (★只【加】不【改】★)
        fails += sw_chain_head_iss_check(root, rel, head, st.get("head_iss"),
                                          "R6 硬保护", cross_check_source=True)
        if not st.get("chain"):
            fails.append("R6 硬保护: %s 台账链断了 / 不唯一 (%s)" % (rel, st.get("why")))
        else:
            orphan = sorted({r["new"] for r in chg} - set(st.get("chain") or []))
            if orphan:
                fails.append("R6 硬保护: %s 台账里有记录不在链上 = %s" % (rel, orphan))
        # ③-1 锚点必须带【原子 reboard 记录】(四项缺一 ⇒ 红)
        if not isinstance(rec, dict):
            fails.append("R6 硬保护: %s 台账里有合法改板记录, 但锚点没有 reboard 记录 "
                         "(单号/文件名/改前 md5/改后 md5 四项不齐) ⇒ 判红" % rel)
            continue
        missing = [k for k in REBOARD_FIELDS if not str(rec.get(k) or "").strip()]
        if missing:
            fails.append("R6 硬保护: %s 的 reboard 记录四项不齐: 缺 %s ⇒ 判红"
                         % (rel, ",".join(missing)))
            continue
        rfile = str(rec.get("file")).strip()
        rprev = m12(rec.get("prev_md5"))
        rmd5 = m12(rec.get("md5"))
        rby = str(rec.get("by")).strip()
        if rfile != rel:
            fails.append("R6 硬保护: %s 的 reboard 记录写的是 %s (≠ 条目文件名) ⇒ 判红" % (rel, rfile))
        if rmd5 != head:
            fails.append("R6 硬保护: %s 的 reboard 改后 md5 %s 与台账链头 %s 不一致 ⇒ "
                         "★单号与 md5 不许各自独立编辑 = 红★" % (rel, rmd5, head))
        head_prevs = sorted({r["prev"] for r in chg if r["new"] == head})
        if len(head_prevs) == 1 and rprev != head_prevs[0]:
            fails.append("R6 硬保护: %s 的 reboard 改前 md5 %s 与台账链头那一行的改前 %s 不一致 "
                         "(链断) ⇒ 判红" % (rel, rprev, head_prevs[0]))
        if rby not in (st.get("producer") or {}).get(head, set()):
            fails.append("R6 硬保护: %s 的 reboard 单号 %s 与台账产出该 md5 的单号对不上 "
                         "(台账 = %s) ⇒ 判红" % (rel, rby or "(空)",
                                                 sorted((st.get("producer") or {}).get(head, []))))
        chain = st.get("chain") or []
        if chain and m12(base) != chain[-1][:12]:
            fails.append("R6 硬保护: %s 的保护基线 %s 不在台账链尾 (链尾 = %s) ⇒ "
                         "★基线被偷偷前移 = 红★" % (rel, m12(base), chain[-1][:12]))
        # ③-2 ★盘上必须 == 台账链头★ (★判据方向不许变★)
        if got[:12] != head:
            fails.append("R6 硬保护: %s 盘上 md5 %s ≠ 台账链头 %s (真源被换了或台账没更新)"
                         % (rel, got[:12], head))

    # ④ 同组受保护件: 一次合法改板必须覆盖同组全部件 (★只来一条记录 ⇒ 红★)
    trip_iss = set()
    for g in group:
        for r in g["chg"]:
            if r["iss"]:
                trip_iss.add(r["iss"])
    if trip_iss:
        for g in group:
            rel = g["rel"]
            expect = heads.get(rel, m12(g["base"]))
            covered = [r for r in g["covers"]
                       if r["iss"] in trip_iss and expect in r["md5s"]]
            if not covered:
                fails.append("R6 硬保护: %s 没有被同一次合法改板 (%s) 覆盖 (记录只来一条 ⇒ 判红)"
                             % (rel, "/".join(sorted(trip_iss))))
    return fails


# ---------------------------------------------------------------- R6 (ISS-225 三方对账 / ISS-275 判决源换源)
def check_r6_three_way(root: str, anchors=None) -> list[str]:
    """R6: ★落表台账最新记录 (链头) ↔ 盘上真源, 一致★ (不许悄悄换真源)。

    ★★【ISS-275 · 2026-11-17】★★ 判决源 = 【落表台账链头】, 不是【域侧锚点副本】:
      ① 盘上真源的 md5 == 落表台账里该文件的【链头】(改前 md5 → 改后 md5 有向链的链头)
      ② 链头取不准 (不唯一 / 链断 / 有记录不在链上 / 链头没落表单号) ⇒ ★一律判红★
      ③ 域侧锚点副本 (§1 `entries[]`) 降级为【历史留痕】: 允许停在历史值,
         但不许胡说 (md5 必须在台账链上 + 落表单号必须与台账产出该 md5 的单号对得上)
    ⇒ 合法落表不再红 (链头自动前移); 悄悄换真源照样红 (盘上 ≠ 链头)
    """
    fails: list[str] = []
    if anchors is None:
        anchors, err = load_sw_anchor(root)
        if anchors is None:
            return ["R6 读不到 SW 侧 md5 基线台账锚点 ⇒ 门禁 fail-closed: %s" % err]

    # ★判决源台账 (★ISS-275 起 = 落表台账链头★; ★ISS-284 起硬保护段也读它★)
    led_text, led_spec = sw_ledger_canonical_text(root, anchors)

    # ---- ① 硬保护 (板 / .kicad_pro): ★★【ISS-284 · P10 = 方案 ②】合法改板机制★★ ----
    #   ★ 判据方向一字未变: 盘上 ≠ 判决源 ⇒ 红; 合法改板只让【链头前移】, 不放宽判据 ★
    #   ★ fail-closed 三条 (链头不唯一 / 链断 / 链头无单号) 一条不许动 ★
    fails += check_r6_hard_protected(root, anchors, led_text, led_spec)

    # ---- ② 台账管理的真源 (网表 / 脚表): 落表台账链头 ↔ 盘上 (★ISS-275 判决源★) ----
    ledger = anchors.get("source_ledger") or {}
    entries = list(ledger.get("entries") or [])
    if not entries:
        fails.append("R6 台账链: 锚点里没有 source_ledger.entries (受管真源失台账对账)")
    if not led_text:
        fails.append("R6 台账链: 判决源落表台账读不到 (%s) ⇒ 无从对账 (fail-closed)" % led_spec)
    for e in entries:
        rel = str(e.get("file") or "")
        by = str(e.get("by") or "")
        want = str(e.get("md5") or "")
        prev = str(e.get("prev_md5") or "")
        if not rel:
            fails.append("R6 台账链: source_ledger.entries 里有空 file")
            continue
        # ②-0 盘上真源必须存在 (判决源换了也一样)
        if not os.path.exists(os.path.join(root, rel)):
            fails.append("R6 台账链: 盘上真源不存在: %s" % rel)
            continue
        got = md5_of(root, rel)
        # ②-1 台账链头 (★判决源★): 取不准 ⇒ 一律判红 (★不许放宽★)
        st = sw_ledger_state(rel, led_text)
        recs = st.get("records") or []
        head = st.get("head")
        if not recs:
            fails.append("R6 台账链: %s 落表台账 (%s) 里查不到任何落表记录 ⇒ 台账没记这次落表?"
                         % (rel, led_spec))
            continue
        if not head:
            fails.append("R6 台账链: %s 台账最新记录取不准 (%s) ⇒ 取错记录可能假绿 ⇒ 判红"
                         % (rel, st.get("why")))
            continue
        if not st.get("head_iss"):
            fails.append("R6 台账链: %s 台账最新记录 (%s) 缺落表单号 (字段缺失)" % (rel, head))
        # ★★【ISS-312】链头落表单号的【交叉核对 · 修法 A + B】⇒ 治「单号被改坏 ⇒ 判绿」★★
        #   ★★ ISS-309 实测的洞就在这条路径上 (★落表真源 = 网表 / 脚表★) ★★
        fails += sw_chain_head_iss_check(root, rel, head, st.get("head_iss"), "R6 台账链")
        if not st.get("chain"):
            fails.append("R6 台账链: %s 台账链断了 / 不唯一 (%s)" % (rel, st.get("why")))
        else:
            orphan = sorted({r["new"] for r in recs} - set(st.get("chain") or []))
            if orphan:
                fails.append("R6 台账链: %s 台账里有记录不在链上 = %s" % (rel, orphan))
        # ②-2 ★盘上真源 vs 台账链头★ (★悄悄换真源判据: 不许为了不红就删★)
        if got[:12] != head:
            fails.append("R6 台账链: 盘上真源 md5 %s = %s ≠ 台账最新记录 %s "
                         "(真源被换了或台账没更新)" % (rel, got[:12], head))
        # ②-3 域侧锚点副本 = 【历史留痕】: 允许停在历史值, 但不许胡说
        if not want:
            fails.append("R6 台账链: 锚点里 %s 没登记 md5 (查不到出处的基线不许当基线)" % rel)
            continue
        am = want[:12]
        if am not in (st.get("known") or set()):
            fails.append("R6 台账链: %s 锚点副本 md5 %s 台账链里查不到 (锚点胡说?)"
                         % (rel, am or "(空)"))
        elif by and by not in (st.get("producer") or {}).get(am, set()):
            fails.append("R6 台账链: %s 锚点副本落表单号 %s 与台账对不上 (台账产出该 md5 的单号 = %s)"
                         % (rel, by or "(空)",
                            sorted((st.get("producer") or {}).get(am, []))))
        # ②-4 锚点副本的旧 md5 也必须还在台账链上 (历史留痕不许断)
        if prev:
            pm = prev[:12]
            if pm not in (st.get("known") or set()):
                fails.append("R6 台账链: %s 锚点副本旧 md5 %s 台账链里查不到 (历史留痕断了?)"
                             % (rel, pm))
    return fails


# ---------------------------------------------------------------- R7 (ISS-225 留痕在场)
def check_r7_trace_present(root: str, anchors=None) -> list[str]:
    """R7: 已修复 (留痕) 必须在场 ⇒ ★删节 / 删行 / 抹 md5 / 抹判别标记 ⇒ 红★"""
    fails: list[str] = []
    try:
        text = read_text(root, LEDGER_DOC)
    except FileNotFoundError as exc:
        return ["R7 读不到留痕账 %s (%s)" % (LEDGER_DOC, exc)]
    m = re.search(r"^##[^\n]*已修复[^\n]*留痕[^\n]*$", text, re.M)
    if not m:
        return ["R7 留痕账里没有「已修复 (留痕)」那一节 (删了 ⇒ 一次真变更被从账上抹了)"]
    tail = text[m.end():]
    nxt = re.search(r"^##\s", tail, re.M)
    sec = text[m.start(): m.end() + (nxt.start() if nxt else len(tail))]
    for lit, why in (("ISS-220", "落表单号"),
                     ("c78f991283cc82d56c8e3dd31657c785", "旧 md5"),
                     ("13f59a43dbd35dc6cb16e897c8c891ab", "新 md5"),
                     ("锚点过期", "判别标记 (是锚点过期)"),
                     ("红灯被调没", "判别标记 (不是红灯被调没)")):
        if lit not in sec:
            fails.append("R7 留痕节的「%s」没了 (%s) ⇒ 一次真变更被从账上抹了" % (lit, why))
    return fails


def run_all(root: str, skip_md5: bool = False, anchor=None) -> list[str]:
    fails: list[str] = []
    fails += check_r1_demo_spec_core(root)
    fails += check_r2_no_active_legacy(root)
    fails += check_r3_pipeline_reanchored(root)
    fails += check_r4_整机_placeholder_kept(root)
    fails += check_r5_triage_table(root)
    if not skip_md5:
        if anchor is None:
            anchor, err = load_sw_anchor(root)
            if anchor is None:
                fails.append("R6 读不到 SW 侧 md5 基线台账锚点 ⇒ 门禁 fail-closed: %s" % err)
                anchor = {}
        fails += check_r6_three_way(root, anchor)
        fails += check_r7_trace_present(root, anchor)
    return fails


# ---------------------------------------------------------------- selftest
SELFTEST_CASES = [
    # (用例名, 相对文件, 破坏动作, 期望失败的规则前缀)
    ("REV-1 把 pipeline 的 demo 口径塞回 1920×1080", PIPELINE,
     lambda t: t.replace("CRTC:  ★**480×640@60.85 Hz**", "CRTC:  1920×1080@60"), "R3"),
    ("REV-2 把 pipeline 的 480×640 buffer 塞回 1920×1080 buffer", PIPELINE,
     lambda t: t.replace("一块 480×640 buffer", "一块 1920×1080 buffer"), "R3"),
    ("REV-3 把 demo 规格的 480×640 删掉", DEMO_SPEC,
     lambda t: t.replace("480×640", "1920×1080").replace("480x640", "1920x1080"), "R1"),
    ("REV-4 把 demo 规格的 2-lane 删掉", DEMO_SPEC,
     lambda t: t.replace("2-lane", "4-lane").replace("dsi,lanes = <2>", "dsi,lanes = <4>"), "R1"),
    ("REV-5 把 demo 规格的「无 DCS」结论删掉", DEMO_SPEC,
     lambda t: (t.replace("不需要任何 DCS init 序列", "需要面板厂给 init 序列")
                 .replace("不需要任何 DCS", "需要 DCS")
                 .replace("零 DSI 写", "官方会下发 DSI 写")), "R1"),
    ("REV-6 把 demo 规格的 I2C ≤100kHz 上限删掉", DEMO_SPEC,
     lambda t: t.replace("100 kHz", "400 kHz").replace("100kHz", "400kHz"), "R1"),
    ("REV-7 把整机口径塞到 demo 规格的占位区块外", DEMO_SPEC,
     lambda t: t.replace(BLOCK_BEGIN,
                         '★demo 活动口径: 面板 = 视涯 0.49" 1920×1080 (还没定)\n\n' + BLOCK_BEGIN), "R2"),
    ("REV-8 把定性表的 L-22 行删掉", TRIAGE,
     lambda t: t.replace("L-22", "L-XX"), "R5"),
]


# ★★【ISS-225 新增】台账对账反向用例 (跑**带 md5 校验**的 run_all ⇒ 需在临时目录搭一棵完整的树)
#  ★ 要拷进临时树的文件 (板 4.9MB ⇒ 走硬链接, 省时省空间; 本组用例不改它 ⇒ 不会污染真盘)
R6_TREE_FILES = (
    DEMO_SPEC,
    TRIAGE,
    PIPELINE,
    LEDGER_DOC,
    os.path.join("HW", "SCHEMATIC_LANDING_V1_LANDED.md"),
    os.path.join("HW", "netlist_v1.csv"),
    os.path.join("HW", "netlist_v1_pins.csv"),
    os.path.join("HW", "PCB", "demo_mainboard.kicad_pcb"),
    os.path.join("HW", "PCB", "demo_mainboard.kicad_pro"),
)
# ★ 大文件走硬链接 (只读不改 ⇒ 安全); 跨文件系统失败 ⇒ 回退拷贝
R6_HARDLINK = (os.path.join("HW", "PCB", "demo_mainboard.kicad_pcb"),)

# ---------------------------------------------------------------- selftest 落表单号改坏工具
# ★★【ISS-235】必须定义在 R6_SELFTEST_CASES **之前** (模块级列表求值顺序) ★★
def _break_current_landing_ticket(path: str, bogus: str = "ISS-999") -> None:
    """★把落表台账里【当前的】落表单号改坏 ⇒ R6 必须红 (★ISS-235★)。

    ★**不许硬编码任何单号** (★ISS-235 的根因: 原来这里写死 `"ISS-220"` ⇒ ISS-233 落表
      (2026-11-16 06:48:38) 之后锚点单号已变成 ISS-233 ⇒ 改坏 ISS-220 不再影响判据 ④
      ⇒ 这条自证就废了 (实测: selftest 15/16, 红的就是它)★)
    ⇒ 当前单号从 **§1 锚点块** (`source_ledger.entries[].by`) **动态读出** ★
    ⇒ ★**自带「我确实改到了目标」的断言** ★:
      ① 锚点里登记的单号读得到 (读不到 ⇒ 用例本身坏了 ⇒ 直接失败)
      ② 伪造单号不与锚点登记的单号撞 (撞了 ⇒ 用例本身坏了)
      ③ 改坏后台账里**不再有**原单号 (⇒ 改坏真的生效)
      ④ 改坏后台账里**有**伪造单号 (⇒ 改到的确实是那个单号)
      ⑤ **锚点里登记的那个单号** == 被改掉的那个单号 (⇒ 不是随便拿一个 ISS-xxx 去改)
    ⇒ ★锚点登记的【全部】落表台账位置都改 (★R6 是「任一处查到即算查到」⇒ 只改一处可能白改★)
    """
    work = os.path.dirname(os.path.dirname(os.path.abspath(path)))      # ← 临时树根
    anchors, err = load_sw_anchor(work)
    if anchors is None:
        raise AssertionError("临时树读不到 SW 侧锚点 ⇒ 定位不到当前落表单号 (%s)" % err)
    ledger_cfg = anchors.get("source_ledger") or {}
    entries = list(ledger_cfg.get("entries") or [])
    bys = sorted({str(e.get("by") or "") for e in entries if e.get("by")})
    if not bys:
        raise AssertionError("锚点 source_ledger.entries 里没有登记落表单号 (by) ⇒ 定位不到当前落表单号")
    if bogus in bys:
        raise AssertionError("伪造单号 %s 与锚点登记的单号 %s 撞了 ⇒ 用例本身坏了" % (bogus, bys))

    # ---- 要改坏的落表台账位置: 锚点登记的**全部**位置 ----
    targets: list[str] = []
    for spec in (ledger_cfg.get("landing_records") or []):
        if not spec:
            continue
        cand = os.path.join(work, spec)
        if os.path.isfile(cand):
            targets.append(cand)
            continue
        d = os.path.dirname(spec) or "."
        b = os.path.basename(spec)
        for hit in sorted(glob.glob(os.path.join(work, d, b))):
            targets.append(hit)
    if os.path.abspath(path) not in [os.path.abspath(t) for t in targets]:
        targets.append(path)

    hit_any = False
    for tgt in targets:
        with open(tgt, encoding="utf-8") as f:
            text = f.read()
        broken = text
        for by in bys:
            broken = broken.replace(by, bogus)
        if broken == text:
            continue
        hit_any = True
        with open(tgt, "w", encoding="utf-8") as f:
            f.write(broken)
        # ---- 自证: 我确实改到了目标 ----
        with open(tgt, encoding="utf-8") as f:
            after = f.read()
        for by in bys:
            if by in after:
                raise AssertionError("改坏没生效: 原单号 %s 还在 %s 里" % (by, tgt))
        if bogus not in after:
            raise AssertionError("改坏没生效: 伪造单号 %s 不在 %s 里" % (bogus, tgt))
    if not hit_any:
        raise AssertionError("改坏动作没生效: 锚点登记的落表单号 %s 不在任何一个落表台账位置里 (%s)"
                             % ("/".join(bys), ", ".join(targets)))


# (用例名, 期望变红的规则前缀, 要改的盘上文件 (None = 不改盘), 文件改法, 锚点改法)
R6_SELFTEST_CASES = [
    ("REV-9 盘上真源被换掉而锚点没换", "R6",
     os.path.join("HW", "netlist_v1.csv"),
     lambda p: _append_text(p, "\n# ISS-225 selftest: 盘上真源被换掉\n"), None),
    ("REV-10 锚点改成台账里查不到的哈希", "R6", None, None,
     lambda a: a["source_ledger"]["entries"][0].__setitem__(
         "md5", "deadbeefdeadbeefdeadbeefdeadbeef")),
    ("REV-11 锚点里的落表单号被改坏 (⇒ 当前值 → ISS-999)", "R6", None, None,
     lambda a: a["source_ledger"]["entries"][0].__setitem__("by", "ISS-999")),
    ("REV-12 落表台账里的【当前】落表单号被改坏 (★动态取自 §1 锚点块 ⇒ 不许硬编码任何单号★)", "R6",
     os.path.join("HW", "SCHEMATIC_LANDING_V1_LANDED.md"),
     _break_current_landing_ticket, None),
    ("REV-13 把落表台账里那两行删掉", "R6",
     os.path.join("HW", "SCHEMATIC_LANDING_V1_LANDED.md"),
     lambda p: _drop_lines(p, "HW/netlist_v1.csv"), None),
    ("REV-14 把锚点块整个删掉 (fail-closed)", "R6",
     LEDGER_DOC, lambda p: _drop_block(p, ANCHOR_BEGIN, ANCHOR_END), None),
    ("REV-15 把「已修复 (留痕)」那一节删掉", "R7",
     LEDGER_DOC, lambda p: _drop_section(p, r"^##[^\n]*已修复[^\n]*留痕[^\n]*$"), None),
]


# ★★【ISS-284 · 2026-11-17 · sw-lead】★★ 合法改板机制 (P10 = 方案 ②) 的用例
#   ★ 机制: 一条合法改板 = 【单号 + 文件名 + 改前 md5 + 改后 md5】四件捆在锚点【一个原子映射】里
#     + 同一份四项必须能在落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` 的【同一行】里查到 ★
BOARD_REL = os.path.join("HW", "PCB", "demo_mainboard.kicad_pcb")
PRO_REL = os.path.join("HW", "PCB", "demo_mainboard.kicad_pro")
# ★★【ISS-315 · 2026-11-18 · sw-lead】★★ ★**夹具的单号改成【真单号】** (★动态取·不许硬编码★)
#   ★原来这里写的是假单号 `ISS-9901` (★"不许硬编码任何真单号"那句是说【不许把真单号写死在这】★)
#   ★**为什么必须换**★: 修法 B (链头单号 ↔ 独立信源 `state/issue_log.yaml` 交叉核对) 铺到
#     【硬保护路径】之后 ⇒ 「合法改板 ⇒ 放行」的正向用例 (REV-21) 必须拿得出【真单号 + 真留痕】
#     ⇒ 用假单号 ⇒ 【独立信源里查不到】⇒ 假红 (★红在夹具缺输入, 不在判据方向★)
#   ★**修法** (★ISS-309 铁律: 假伤修夹具, 不许改判据★)★: 夹具改用【真单号】
#     (★`sw_fresh_hard_ticket()` 动态取: 真单号 + 对硬保护件来说是新的★) ⇒ ★判据本体一个字没动★
#   ★注意★: ★**不许**拿落表台账里那八个已经落过 .kicad_pro 的老单号 (ISS-220/233/243/249/
#     257/236/283/302) 来当夹具单号 ⇒ 那样 REV-20「只改板不动 .kicad_pro」会被判绿 ⇒ 用例废了★
TICKET_FALLBACK = "ISS-9901"   # ★取不到真单号时的兼底 (★正常路径永远走不到★)
TICKET_B = "ISS-9902"      # ★「第二个头」用的对照单号 (★那个场景链头不唯一 ⇒ 不触发修法 B★)


def _tree_root(path: str) -> str:
    """从临时树里任意文件路径反推树根 (★往上找到同时有 HW/ 与 SW/ 的那一层★)。"""
    d = os.path.dirname(os.path.abspath(path))
    for _ in range(8):
        if os.path.isdir(os.path.join(d, "HW")) and os.path.isdir(os.path.join(d, "SW")):
            return d
        d = os.path.dirname(d)
    raise AssertionError("临时树根找不到 (path=%s)" % path)


def _bump_file_copy(path: str) -> str:
    """★先把硬链接换成真拷贝再改 (★绝不许改到真盘上的板★) ⇒ 返回改后的 md5★。

    ★`os.replace` 换的是 inode ⇒ 真盘上那份硬链接一个字节都不受影响★
    """
    tmp = path + ".iss284_tmp"
    shutil.copy2(path, tmp)
    os.replace(tmp, path)
    with open(path, "a", encoding="utf-8") as f:
        f.write("\n# ISS-284 selftest: 合法改板 (只存在于临时树)\n")
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _rewrite_anchor_block(root: str, fn) -> None:
    """★只用于 selftest 临时树★: 改 §1 锚点块 (★真盘的锚点块不许这样整块重写★)。"""
    import yaml as _yaml
    path = os.path.join(root, LEDGER_DOC)
    with open(path, encoding="utf-8") as f:
        text = f.read()
    m = re.search(re.escape(ANCHOR_BEGIN) + r"(.*?)" + re.escape(ANCHOR_END), text, re.S)
    if not m:
        raise AssertionError("临时树里找不到锚点块")
    data = _yaml.safe_load(m.group(1)) or {}
    fn(data)
    block = (ANCHOR_BEGIN + "\n"
             + _yaml.safe_dump(data, allow_unicode=True, sort_keys=False, default_flow_style=False)
             + ANCHOR_END)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text[:m.start()] + block + text[m.end():])


def _anchor_base(root: str, rel: str) -> str:
    anchors, err = load_sw_anchor(root)
    if anchors is None:
        raise AssertionError("临时树读不到锚点 (%s)" % err)
    for e in (anchors.get("hard_protected") or []):
        if str(e.get("file") or "") == rel:
            return str(e.get("md5") or "")
    raise AssertionError("锚点里没有 %s 的保护基线" % rel)


def _append_ledger_rows(root: str, rows: list) -> None:
    """★只用于 selftest 临时树★: 往落表台账末尾追加行 (★真盘的落表台账本单不许碰★)。"""
    path = os.path.join(root, LEDGER_CANON)
    with open(path, "a", encoding="utf-8") as f:
        f.write("\n" + "\n".join(rows) + "\n")


def _row(ticket, rel, prev, new, note="★**是** ★"):
    """★落表台账行 (★格式契约: 单号 | 文件名 | 改前 md5 | 改后 md5 四项同行★)。"""
    return "| %s | `%s` | `%s` | `%s` | %s |" % (ticket, rel, prev, new, note)


def _reboard_in_tree(root: str, rows_fn=None, anchor_prev=None,
                     ticket=None, set_md5_only=False) -> str:
    """临时树里做一次「合法改板」: ① 板文件改一个字节 ② 锚点写原子 reboard 记录 ③ 台账追加行。

    ★`set_md5_only=True` ⇒ 模拟「只改了锚点里的板 md5, 单号字段没写」(★挖坑那条路★)★
    ★★【ISS-315】`ticket` 缺省 ⇒ 取【真单号】(★`sw_fresh_hard_ticket()`★) ⇒ ★不许硬编码★
    """
    board = os.path.join(root, BOARD_REL)
    newmd5 = _bump_file_copy(board)
    base = _anchor_base(root, BOARD_REL)
    prev = base if anchor_prev is None else anchor_prev
    if not ticket:
        ticket = sw_fresh_hard_ticket(PROJ) or TICKET_FALLBACK

    def _fn(data):
        for e in data["anchors"]["hard_protected"]:
            if e.get("file") != BOARD_REL:
                continue
            if set_md5_only:
                e["md5"] = newmd5                      # ★只改 md5, 不写单号 ⇒ 挖坑★
            else:
                e["reboard"] = {"by": ticket, "file": BOARD_REL,
                                "prev_md5": prev, "md5": newmd5}
    _rewrite_anchor_block(root, _fn)
    if rows_fn is not None:
        _append_ledger_rows(root, rows_fn(root, base, newmd5, ticket))
    return newmd5


def _rows_full_legal(root, base, new, ticket):
    """★合法改板的样子: 板一行变更 + `.kicad_pro` 一行「逐字节不变」, 同一单号★。"""
    pro = _anchor_base(root, PRO_REL)
    return [
        _row(ticket, BOARD_REL, base, new, "★**是 (★合法改板·板只改一次★)** ★"),
        _row(ticket, PRO_REL, pro, pro, "★**否 (★逐字节不变★)** ★"),
    ]


def _rows_two_heads(root, base, new, ticket):
    """★两条合法改板记录指向同一个文件 ⇒ 链头不唯一★。"""
    pro = _anchor_base(root, PRO_REL)
    return [
        _row(ticket, BOARD_REL, base, new, "★**是 (★合法改板★)** ★"),
        _row(TICKET_B, BOARD_REL, base, "deadbeefdeadbeefdeadbeefdeadbeef", "★**是 (★第二跳·另一个头★)** ★"),
        _row(ticket, PRO_REL, pro, pro, "★**否 (★逐字节不变★)** ★"),
    ]


def _rows_broken_chain(root, base, new, ticket):
    """★链断: 台账记的是 (base→中间→链头), 而锚点写的改前 md5 是 base (★对不上上一次改后★)。"""
    pro = _anchor_base(root, PRO_REL)
    mid = "0123456789abcdef0123456789abcdef"
    return [
        _row(ticket, BOARD_REL, base, mid, "★**是 (★上一跳★)** ★"),
        _row(ticket, BOARD_REL, mid, new, "★**是 (★本跳·链头★)** ★"),
        _row(ticket, PRO_REL, pro, pro, "★**否 (★逐字节不变★)** ★"),
    ]


def _rows_board_only(root, base, new, ticket):
    """★只改板不动 `.kicad_pro` ⇒ 两件的记录只来一条★。"""
    return [_row(ticket, BOARD_REL, base, new, "★**是 (★合法改板★)** ★")]


# (用例名, 期望绿(True)/期望红(False), 破坏动作)
R6_REBOARD_CASES = [
    ("REV-16 只改锚点里的板 md5, 单号字段没写 (★挖坑★)", False,
     lambda p: _reboard_in_tree(_tree_root(p), set_md5_only=True)),
    ("REV-17 锚点写了单号, 但落表台账里查不到那一行", False,
     lambda p: _reboard_in_tree(_tree_root(p))),
    ("REV-18 台账里两条合法改板记录指向同一个文件 (链头不唯一)", False,
     lambda p: _reboard_in_tree(_tree_root(p), rows_fn=_rows_two_heads)),
    ("REV-19 链断 (改前 md5 对不上台账记的上一次改后 md5)", False,
     lambda p: _reboard_in_tree(_tree_root(p), rows_fn=_rows_broken_chain)),
    ("REV-20 只改板不动 .kicad_pro (两件记录只来一条)", False,
     lambda p: _reboard_in_tree(_tree_root(p), rows_fn=_rows_board_only)),
    ("REV-21 合法改板: 台账四项齐全 + 锚点原子记录 ⇒ 放行 (★正向★)", True,
     lambda p: _reboard_in_tree(_tree_root(p), rows_fn=_rows_full_legal)),
]


# ---------------------------------------------------------------- selftest 文本改坏工具
def _append_text(path: str, blob: str) -> None:
    with open(path, "a", encoding="utf-8") as f:
        f.write(blob)


def _replace_text(path: str, old: str, new: str) -> None:
    with open(path, encoding="utf-8") as f:
        t = f.read()
    if old not in t:
        raise AssertionError("改坏动作没生效: %r 不在 %s" % (old, path))
    with open(path, "w", encoding="utf-8") as f:
        f.write(t.replace(old, new))


def _drop_lines(path: str, needle: str) -> None:
    with open(path, encoding="utf-8") as f:
        t = f.read()
    kept = [ln for ln in t.split("\n") if needle not in ln]
    if len(kept) == len(t.split("\n")):
        raise AssertionError("改坏动作没生效: %r 不在 %s" % (needle, path))
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(kept))


def _drop_block(path: str, begin: str, end: str) -> None:
    with open(path, encoding="utf-8") as f:
        t = f.read()
    out = re.sub(re.escape(begin) + r".*?" + re.escape(end), "", t, flags=re.S)
    if out == t:
        raise AssertionError("改坏动作没生效: %s 块不在 %s" % (begin, path))
    with open(path, "w", encoding="utf-8") as f:
        f.write(out)


def _drop_section(path: str, head_re: str) -> None:
    with open(path, encoding="utf-8") as f:
        t = f.read()
    m = re.search(head_re, t, re.M)
    if not m:
        raise AssertionError("改坏动作没生效: 标题 %r 不在 %s" % (head_re, path))
    tail = t[m.end():]
    nxt = re.search(r"^##\s", tail, re.M)
    cut = m.end() + (nxt.start() if nxt else len(tail))
    with open(path, "w", encoding="utf-8") as f:
        f.write(t[:m.start()] + t[cut:])


def _build_r6_tree(tmp: str, root: str, name: str) -> str:
    work = os.path.join(tmp, name)
    for rel in R6_TREE_FILES:
        src = os.path.join(root, rel)
        dst = os.path.join(work, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if rel in R6_HARDLINK:
            try:
                os.link(src, dst)
                continue
            except OSError:
                pass
        shutil.copy2(src, dst)
    return work


def selftest(root: str) -> int:
    print("=== SELFTEST (反向用例: 每条都必须在被破坏后变红) ===")
    passed = 0
    failed = 0
    with tempfile.TemporaryDirectory(prefix="iss212_gate_") as tmp:
        for name, rel, mutate, expect_rule in SELFTEST_CASES:
            work = os.path.join(tmp, "case_%02d" % passed)
            # ★只拷被核对的 3 份 SW 文件 (HW 受保护文件不参与反向用例 ⇒ 跳过 md5 校验)
            for f in (DEMO_SPEC, TRIAGE, PIPELINE):
                dst = os.path.join(work, f)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(os.path.join(root, f), dst)
            path = os.path.join(work, rel)
            try:
                with open(path, encoding="utf-8") as f:
                    text = f.read()
            except FileNotFoundError:
                print("  ❌ %-52s ⇒ 找不到 %s" % (name, rel))
                failed += 1
                continue
            broken = mutate(text)
            if broken == text:
                print("  ❌ %-52s ⇒ 破坏动作没生效 (用例本身坏了)" % name)
                failed += 1
                continue
            with open(path, "w", encoding="utf-8") as f:
                f.write(broken)
            fails = run_all(work, skip_md5=True)
            hit = [f for f in fails if f.startswith(expect_rule)]
            if hit:
                print("  ✅ %-52s ⇒ %s 变红 (%s)" % (name, expect_rule, hit[0][:70]))
                passed += 1
            else:
                print("  ❌ %-52s ⇒ %s 没变红 (期望它红) — 实得失败项: %s"
                      % (name, expect_rule, fails[:2]))
                failed += 1

        # ---------------- ISS-225 新增: R6 三方对账 + R7 留痕在场 ----------------
        print("--- ISS-225 台账对账反向用例 (R6/R7) ---")
        base_work = _build_r6_tree(tmp, root, "base")
        base_fails = run_all(base_work, skip_md5=False)
        if base_fails:
            print("  ❌ 基线就不绿: %s ⇒ 台账对账自测不成立" % base_fails[:3])
            failed += 1
        else:
            print("  ✅ 基线全绿 (R1~R7 在临时树上全过)")
            passed += 1
        for idx, (name, expect_rule, rel, fmut, amut) in enumerate(R6_SELFTEST_CASES):
            work = _build_r6_tree(tmp, root, "r6_%02d" % idx)
            anchor = None
            if amut is not None:
                anch, err = load_sw_anchor(work)
                if anch is None:
                    print("  ❌ %-52s ⇒ 临时树读不到锚点 (%s)" % (name, err))
                    failed += 1
                    continue
                anchor = copy.deepcopy(anch)
                amut(anchor)
            if fmut is not None:
                try:
                    fmut(os.path.join(work, rel))
                except AssertionError as exc:
                    print("  ❌ %-52s ⇒ %s" % (name, exc))
                    failed += 1
                    continue
            fails = run_all(work, skip_md5=False, anchor=anchor)
            hit = [f for f in fails if f.startswith(expect_rule)]
            if hit:
                print("  ✅ %-52s ⇒ %s 变红 (%s)" % (name, expect_rule, hit[0][:70]))
                passed += 1
            else:
                print("  ❌ %-52s ⇒ %s 没变红 (期望它红) — 实得失败项: %s"
                      % (name, expect_rule, fails[:2]))
                failed += 1

        # ---------------- ISS-284 新增: 合法改板 (P10 = 方案 ②) 正向/反向用例 ----------------
        print("--- ISS-284 合法改板机制用例 (P10 = 方案 ② · 硬保护两件) ---")
        for idx, (name, expect_green, fmut) in enumerate(R6_REBOARD_CASES):
            work = _build_r6_tree(tmp, root, "rb_%02d" % idx)
            try:
                # ★★【ISS-315】改坏之前先把【保护基线】读出来 (★REV-16 会改锚点里的 md5★)
                base = _anchor_base(work, BOARD_REL)
                pro_base = _anchor_base(work, PRO_REL)
                fmut(os.path.join(work, BOARD_REL))
            except AssertionError as exc:
                print("  ❌ %-52s ⇒ %s" % (name, exc))
                failed += 1
                continue
            # ★★【ISS-315 · 2026-11-18 · sw-lead】★★ 给夹具补上【独立信源】的输入 ★
            #   ★病灶: 修法 B (链头单号 ↔ 独立信源交叉核对) 铺到【硬保护路径】后 ★
            #     「合法改板 ⇒ 放行」这个正向用例 (REV-21) 少了【独立信源】⇒ 假红 ★
            #   ★修法: ★假伤修夹具, 不许改判据★ ⇒ 这里只【补输入】: 把真 issue_log 拷进临时树,
            #     并在【真单号】的条目里写上【文件名 + 改后 md5】的留痕行 ★
            #   ★真盘一个字节都不动★ (★写的是临时树里的 state/issue_log.yaml★)
            try:
                newmd5 = md5_of(work, BOARD_REL)
                ticket = sw_fresh_hard_ticket(root)
                if not ticket:
                    raise AssertionError("取不到真单号 ⇒ 夹具自己坏了")
                sw_sandbox_issue_log(os.path.join(work, ISSUE_LOG_REL), ticket,
                                     [(BOARD_REL, base, newmd5),
                                      (PRO_REL, pro_base, pro_base)])
            except AssertionError as exc:
                print("  ❌ %-52s ⇒ %s" % (name, exc))
                failed += 1
                continue
            fails = run_all(work, skip_md5=False)
            hit = [f for f in fails if f.startswith("R6")]
            if expect_green:
                if not hit:
                    print("  ✅ %-52s ⇒ R6 仍绿 (★合法改板四项齐全 = 放行★)" % name)
                    passed += 1
                else:
                    print("  ❌ %-52s ⇒ 期望绿却红了: %s" % (name, hit[0][:70]))
                    failed += 1
            else:
                if hit:
                    print("  ✅ %-52s ⇒ %s 变红 (%s)" % (name, "R6", hit[0][:70]))
                    passed += 1
                else:
                    print("  ❌ %-52s ⇒ R6 没变红 (期望它红) — 实得失败项: %s"
                          % (name, fails[:2]))
                    failed += 1
    print("--- SELFTEST %d/%d 通过 ---" % (passed, passed + failed))
    return 0 if failed == 0 else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="ISS-212 demo 显示侧口径门禁")
    ap.add_argument("--selftest", action="store_true", help="只跑反向自检")
    ap.add_argument("--json", action="store_true", help="机读输出")
    ap.add_argument("--skip-md5", action="store_true",
                    help="跳过 R6/R7 台账对账与留痕检查 (★既有逃生舱; 默认必须仍校★)")
    ap.add_argument("--root", default=PROJ, help="项目根目录 (默认: 脚本所在项目根)")
    args = ap.parse_args()

    root = os.path.abspath(args.root)
    if args.selftest:
        return selftest(root)

    fails = run_all(root, skip_md5=args.skip_md5)
    if args.json:
        print(json.dumps({"root": root, "failures": fails, "ok": not fails},
                         ensure_ascii=False, indent=2))
        return 0 if not fails else 1

    if not fails:
        print("✅ ISS-212 demo 显示侧口径门禁: 全过")
        print("   R1 demo 屏规格真源 (480×640 / 2-lane / 无 DCS / I2C_B ≤100kHz + 附属必填项) ✅")
        print("   R2 demo 规格里整机口径只在「整机路线占位区」内 ✅")
        print("   R3 pipeline spec 的 demo 活动口径已重锚 ✅")
        print("   R4 整机路线占位仍在且带「整机路线·暂缓」 ✅")
        print("   R5 逐处定性表 (22 + 16 = 38 处) 完整 ✅")
        if not args.skip_md5:
            print("   R6 受保护真源三方对账 (锚点 ↔ 落表台账 ↔ 盘上真源) 一致 ✅")
            print("   R7 已修复 (留痕) 在场 (ISS-220 落表锚点过期, 不是红灯被调没) ✅")
        return 0

    print("❌ ISS-212 demo 显示侧口径门禁: %d 项不通过" % len(fails))
    for f in fails:
        print("   - %s" % f)
    return 1


if __name__ == "__main__":
    sys.exit(main())
