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


def sw_ledger_state(rel: str, text: str) -> dict:
    """算该受管真源在落表台账里的链头 / 链 / 产出单号表 (★取不准 ⇒ head=None ⇒ 判红★)。"""
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

    # ---- ① 硬保护 (板 / .kicad_pro): 落表明令不许碰 ⇒ 纯 md5 比对 (★判据/阈值一字未动★) ----
    hard = list(anchors.get("hard_protected") or [])
    if not hard:
        fails.append("R6 硬保护: 锚点里没有 hard_protected 段 (板 / .kicad_pro 失保护)")
    for e in hard:
        rel = str(e.get("file") or "")
        want = str(e.get("md5") or "")
        if not rel or not want:
            fails.append("R6 硬保护: hard_protected 条目缺 file/md5: %r" % (e,))
            continue
        if not os.path.exists(os.path.join(root, rel)):
            fails.append("R6 硬保护: 受保护文件不存在: %s" % rel)
            continue
        got = md5_of(root, rel)
        if got != want:
            fails.append("R6 硬保护: 受保护文件 md5 变了: %s (%s ≠ %s)" % (rel, got, want))

    # ---- ② 台账管理的真源 (网表 / 脚表): 落表台账链头 ↔ 盘上 (★ISS-275 判决源★) ----
    ledger = anchors.get("source_ledger") or {}
    entries = list(ledger.get("entries") or [])
    if not entries:
        fails.append("R6 台账链: 锚点里没有 source_ledger.entries (受管真源失台账对账)")
    led_text, led_spec = sw_ledger_canonical_text(root, anchors)
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
