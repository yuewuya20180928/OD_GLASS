#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_refresh_decision_page_20261116_r41.py
★main (moli) 决策页 r41 · 2026-11-16 11:5x (cron 775d9893 继续执行后继计划)★
★补 1 条待拍 (ISS-237 的整机屏版本) + 给 A6 加「demo 口径已被 ISS-237 裁定取代」标注 (★旧字一个不删★)★

★★**为什么加这一条 (★main 本轮 11:4x 实跑, 不是推测★)** ★★
· ★**`advance.py --json` ⇒ decisions = 40 条**; ★**main 逐 key 比对 `DECISION_PENDING_2026-11-16.md` (09:47 版) ⇒ 39 条在页上, 缺 1 条: `iss237_product_screen_version`** ★
· ★**那条的内容**: ★**「整机阶段的屏版本 (1920x1080 全彩 vs 单色绿 vs 视涯 0.49 inch SiOLED) 请拍; ISS-237 只收死了 demo 板口径, 不代拍整机屏版本」** ★
  ⇒ ★**它 11:0x 才由 ISS-237 (P2 屏口径收死) 交卷时带出来 ⇒ 09:47 那版页当然没有** ★
· ★**同时要订正一处**: 页上 **A6 = 「demo 显示件用哪一版」(ISS-132 · 视涯 0.49" 三版)** ⇒ ★**demo 板口径已被 ISS-237 (2026-11-16) 收死 = Waveshare 2.8inch DSI LCD (SKU 22028) · 22p/0.5mm (FH12-22S-0.5SH(55)) · 板上不做 12V BOOST** ★
  ⇒ ★**⇒ A6 现在只对【整机屏版本】有意义 ⇒ 整机那条单列为 `iss237_product_screen_version`; A6 原字保留 + 加「demo 口径已作废」标注 (★不删★)** ★

★★**本脚本做的事 (★幂等·只加不改★)** ★★
· ★**① §B 表里追加一行 `iss237_product_screen_version`** ⇒ §B 22 → 23 条 ★
· ★**② A6 行尾追加一段「★demo 口径已被 ISS-237 取代★」标注** (★原字一字不删★) ★
· ★**③ 页头计数与口径句同步 (22 → 23)** ★
· ★**不碰 §0 锁死表 / 不碰其它节 / 不改任何已写条目的数字** ★
"""
import os
import shutil
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
DST = os.path.join(PROJ, "DECISION_PENDING_2026-11-16.md")

MARK_ROW = "`iss237_product_screen_version`"
MARK_A6 = "★**demo 口径已被 ISS-237 取代**★"

NEW_ROW = (
    "| `iss237_product_screen_version` | ★**整机阶段的屏版本** (★**ISS-237 只收死了 demo 板口径 = Waveshare 2.8inch DSI LCD (SKU 22028) · 22p/0.5mm · 板上不做 12V BOOST; 整机屏版本 ISS-237 明写「不代拍」★)<br>选项: **1920x1080 全彩** / **单色绿** / **视涯 0.49\" SiOLED** | ★**视涯 0.49\" SiOLED 全彩版 (3000nits Full RGB)** (★**理由: 结构侧腔体真源已经按它算的** —— `MECH/CENTER_CAVITY_RECALC.md` §1.1 面板有效面积 10.783×6.065 = 65.40 mm² = 视涯 0.49\" ⇒ 眼盒 62 mm² 硬约束与分光件 11×11×1.5 平板/9×9×5 棱镜 全是按它推的 ⇒ ★**换屏 = 结构/光学/重量账全重算**★; ★**代价 = DSC 3:1 解码要 RK3572 侧验证 (demo 用的 2.8\" LCD 无 DSC) ⇒ 这条风险要到整机阶段才暴露**★) ⇒ ★**不拍的后果**: 整机阶段的镜框腔体 / 分光件 / 整机重量账 / 出瞳亮度账 全部按「屏未定」算, 结构侧无法收口 ★ |\n"
)

A6_NOTE = (
    " · ★★**【2026-11-16 11:5x 补注 · demo 板口径已被 ISS-237 裁定取代】**★★ ★**demo 板屏幕 = Waveshare 2.8inch DSI LCD (SKU 22028) · 主板 display 座 22p/0.5mm (FH12-22S-0.5SH(55)) · 板上不做 12V BOOST 背光链** (★依据: `HW/STEP1_PARTS_SPEC.md` §0 裁定块 `RULING=A` · `HW/check_step1_parts_spec.py` rc=0 8/8★) ⇒ ★**本行 (A6) 的 demo 部分已被取代, 现在只剩【整机屏版本】有意义 ⇒ 整机那条单列为 `iss237_product_screen_version` (见 §B)· A6 原字保留作留痕** ★"
)


def atomic_write(path, text):
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def main():
    with open(DST, encoding="utf-8") as f:
        txt = f.read()

    if MARK_ROW in txt:
        print("already refreshed (row present) -> skip")
        return 0

    backup = DST + ".bak_20261116_1150_r41"
    shutil.copy2(DST, backup)

    # ① A6 行尾追加标注 (原字不删) —— 定位 A6 行末尾的 " |"
    lines = txt.split("\n")
    a6_idx = None
    for i, ln in enumerate(lines):
        if ln.startswith("| **A6** |"):
            a6_idx = i
            break
    if a6_idx is None:
        print("!! 找不到 A6 行 -> 不写")
        return 2
    if MARK_A6 not in lines[a6_idx]:
        lines[a6_idx] = lines[a6_idx].rstrip() + A6_NOTE

    txt = "\n".join(lines)

    # ② §B 表尾追加一行 (在 §C 标题之前)
    c_idx = txt.find("\n## §C ·")
    if c_idx == -1:
        print("!! 找不到 §C 标题 -> 不写")
        return 2
    txt = txt[:c_idx] + "\n" + NEW_ROW.rstrip("\n") + txt[c_idx:]

    # ③ 页头计数同步
    txt = txt.replace(
        "★**下面 §A 的 9 条卡主线, §B 的 22 条不卡 demo (整机/结构阶段), §C 的 7 条疑似已被后续拍板覆盖 (请确认后清账)** ★",
        "★**下面 §A 的 9 条卡主线, §B 的 23 条不卡 demo (整机/结构阶段 · ★11:5x 新增 1 条: 整机屏版本 ISS-237★), §C 的 7 条疑似已被后续拍板覆盖 (请确认后清账)** ★",
    )
    txt = txt.replace(
        "## §B · 不卡 demo 主线 (22 条 · 建议归期到「原理图定稿后 / 整机阶段」)",
        "## §B · 不卡 demo 主线 (23 条 · 建议归期到「原理图定稿后 / 整机阶段」)",
    )
    txt = txt.replace(
        "> **出页人**: 项目总工 (main / moli) · **时间**: 2026-11-16 07:5x",
        "> **出页人**: 项目总工 (main / moli) · **时间**: 2026-11-16 11:5x (★r41: 补 ISS-237 整机屏版本 1 条 + A6 加 demo 口径已取代标注★)",
    )

    atomic_write(DST, txt)
    print("r41 written: §B 22→23 · A6 标注已加 · backup=" + os.path.basename(backup))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
