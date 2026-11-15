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
  R6  受保护文件 md5 逐字节未变 (板 / 网表 / 脚表 / .kicad_pro)

用法:
    python3 SW/tools/check_demo_panel_spec.py                # 核对 (rc=0 = 全过)
    python3 SW/tools/check_demo_panel_spec.py --selftest      # 自检 (反向用例必须全红)
    python3 SW/tools/check_demo_panel_spec.py --json          # 机读输出
    python3 SW/tools/check_demo_panel_spec.py --skip-md5      # 跳过 R6 (hw-lead 合法改板后用)
"""
from __future__ import annotations

import argparse
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

# ★R6: 受保护文件 (交卷前后必须逐字节不变)
PROTECTED_MD5 = {
    os.path.join("HW", "PCB", "demo_mainboard.kicad_pcb"): "611b869e13518c3c023fb178f91a0075",
    os.path.join("HW", "netlist_v1.csv"): "c78f991283cc82d56c8e3dd31657c785",
    os.path.join("HW", "netlist_v1_pins.csv"): "4814617e22b567d76164e56bc5e39dc8",
    os.path.join("HW", "PCB", "demo_mainboard.kicad_pro"): "3e504d2be83152e337949723e909be1b",
}


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


# ---------------------------------------------------------------- R6
def check_r6_protected_md5(root: str) -> list[str]:
    fails = []
    for rel, want in PROTECTED_MD5.items():
        path = os.path.join(root, rel)
        if not os.path.exists(path):
            fails.append("R6 受保护文件不存在: %s" % rel)
            continue
        got = md5_of(root, rel)
        if got != want:
            fails.append("R6 受保护文件 md5 变了: %s (%s ≠ %s)" % (rel, got, want))
    return fails


def run_all(root: str, skip_md5: bool = False) -> list[str]:
    fails: list[str] = []
    fails += check_r1_demo_spec_core(root)
    fails += check_r2_no_active_legacy(root)
    fails += check_r3_pipeline_reanchored(root)
    fails += check_r4_整机_placeholder_kept(root)
    fails += check_r5_triage_table(root)
    if not skip_md5:
        fails += check_r6_protected_md5(root)
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
    print("--- SELFTEST %d/%d 通过 ---" % (passed, passed + failed))
    return 0 if failed == 0 else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="ISS-212 demo 显示侧口径门禁")
    ap.add_argument("--selftest", action="store_true", help="只跑反向自检")
    ap.add_argument("--json", action="store_true", help="机读输出")
    ap.add_argument("--skip-md5", action="store_true", help="跳过 R6 受保护文件 md5 校验")
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
            print("   R6 受保护文件 md5 逐字节未变 ✅")
        return 0

    print("❌ ISS-212 demo 显示侧口径门禁: %d 项不通过" % len(fails))
    for f in fails:
        print("   - %s" % f)
    return 1


if __name__ == "__main__":
    sys.exit(main())
