#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20261116_1158_correction_iss240_rootcause.py
★main (moli) 2026-11-16 11:58 (cron 775d9893 继续执行后继计划)★
★把 ISS-240 任务书的【根因订正】留痕进台账 (note + task_brief 追加段·不删原文)★

★★**为什么要订正 (★main 本轮 11:5x 逐条实查, 不猜★)** ★★
· ★**main 派完 ISS-240 之后, 又去读 `PROJECT_TRACKER.md` §0 锁死表 ⇒ 撞到第 44 行 (老板 2026-11-02 19:25 指示②·已定不是待拍板)** ★
  ⇒ ★**「demo 硬件形态: 主板 = 一块板; sensor 画成模组; 屏幕驱动板也画成模组; sensor 模组与屏幕模组各用 FPC 软排连到主板上 ⇒ ★跨铰链取消★ (不做结构 ⇒ 相机 FPC 与屏 FFC 都短距) ⇒ 连带: 原 CONN_CAM/CONN_LIGHT 的跨铰链属性要去掉, 充电板 (J_CHG) 要并进主板或 demo 直接 USB 供电」** ★
· ★**main 实跑 `HW/netlist_v1.csv` 的 board 栏复核**: ★`J_CHG` = **HINGE** (充电板↔主 PCB·跨铰链载流)★ · `CONN_CAM` = MAIN_PCB · `CONN_LIGHT` = MAIN_PCB · `J_USB_C` = MAIN_PCB · `J_TYPE_C` = CHG_BOARD ⇒ ★**全表 board 分布 = MAIN_PCB 404 / CHG_BOARD 94 / HINGE 15** ★
  ⇒ ★★★**⇒ 真实跨铰链链路 = 1 条 (J_CHG) ⇒ `MECH/hinge_usb_check.py` 的 `CROSS_LINKS` 里后三条 (CONN_USB / CONN_CAM / CONN_LIGHT) 按现网表【都不跨铰链】** ★★★
· ★★★**⇒ 真正的根因不是「三套口径打架」, 而是【跨铰链架构对 demo 板已经变了 ⇒ 铰链区 FPC 几何账整块对 demo 板不适用 ⇒ 25.00 (按 4 条链算) 与 31.5 (按 4 条链 + camera 误用 0.5mm) 都不是 demo 板现行值 ⇒ `check_demo_struct_truth.py` G7 把 25.00 当现行值钉死 = 钉着一个已被老板 11-02 指示② + 网表落表作废的架构 ⇒ 假绿】** ★★★
  ⇒ ★**demo 板真跨铰链口径 (只有 J_CHG)**: 高度占位 = 10p × 0.5 = **5.0 mm** (vs 镜脚净高 38.0 ⇒ 余量 33.0) · 径向占位 = R_min 3.0 + 1×(0.2+0.15) = **3.35 mm** (vs 铰链段前后内净空 5.4 ⇒ 余量 2.05) ★
· ★**⇒ 已在 11:56 用 subagents steer 把订正送进在跑的 mech-lead 会话 (mode=restart·任务书带订正重启)** ⇒ ★**本脚本只做台账留痕 (note + task_brief 追加一段, ★旧文字一个不删★)** ★

★★**边界 (本脚本)★★ ★★
★只往 `state/issue_log.yaml` 的 ISS-240 一条追加 note + task_brief 订正段 (★不改 status / owner / verify_* / fix_ref★) · ★不改 PROJECT_TRACKER.md §0 · ★不写任何 agent 的分片 · ★不碰板 / 布线 / 布局 · ★零外发 ★
"""
import os
import shutil
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")

CORRECTION = (
    "\n\n★★★2026-11-16 11:58 (cron 775d9893 继续执行后继计划) ★**main 派完单之后追加的根因订正 (★前面给的事实一条都不推翻, 旧文字按纪律留痕不删★) ★★★\n"
    "· ★**订正**: 本单原写的病灶「三套几何口径互相打架 ⇒ 收成一套」⇒ ★**更深的根因是【跨铰链架构对 demo 板已经变了】** ⇒ ★**收口目标不是「三选一」, 而是「★跨铰链这个架构对 demo 板不成立 ⇒ 铰链区 FPC 几何账整块对 demo 板不适用 ⇒ 25.00 与 31.5 都不是 demo 板现行值★」** ★\n"
    "· ★**新证据 (main 本轮 11:5x 实查)**: ★\n"
    "  ① ★**`PROJECT_TRACKER.md` §0 锁死表第 44 行 (老板 2026-11-02 19:25 指示②·已定不是待拍板)**: ★**「demo 硬件形态: 主板 = 一块板; sensor 画成模组; 屏幕驱动板也画成模组; sensor 模组与屏幕模组各用 FPC 软排连到主板上 ⇒ ★跨铰链取消★ (相机 FPC 与屏 FFC 都短距) ⇒ 连带: 原 CONN_CAM/CONN_LIGHT 的跨铰链属性要去掉, 充电板 (J_CHG) 要并进主板或 demo 直接 USB 供电」** ★\n"
    "  ② ★**网表 board 栏实跑复核**: ★`J_CHG` = **HINGE** (跨铰链载流) · `CONN_CAM` = MAIN_PCB · `CONN_LIGHT` = MAIN_PCB · `J_USB_C` = MAIN_PCB · `J_TYPE_C` = CHG_BOARD ⇒ ★**全表 board 分布 = MAIN_PCB 404 / CHG_BOARD 94 / HINGE 15** ★\n"
    "  ⇒ ★★★**真实跨铰链链路 = 1 条 (J_CHG) ⇒ `CROSS_LINKS` 里后三条按现网表都不跨铰链** ★★★\n"
    "  ③ ★**demo 板真跨铰链口径 (只有 J_CHG)**: 高度占位 = 10p × 0.5 = **5.0 mm** (vs 镜脚净高 38.0 ⇒ 余量 33.0) · 径向占位 = R_min 3.0 + 1×(0.2+0.15) = **3.35 mm** (vs 净空 5.4 ⇒ 余量 2.05) ⇒ ★**⇒ G7 钉死 25.00 = 钉着一个已被作废的架构 ⇒ 假绿, 不是小偏差** ★\n"
    "· ★**⇒ T3 改法映射里 `mech_hinge_stack_fixed_mm` 必须给三档处置选项 (★只报不改, 一票交 main★)**: (a) claim + G7 改成「demo 口径 = J_CHG 单链 (高度 5.0 / 径向 3.35)」 · (b) 保留 25.00 但标明 = 整机阶段旧架构口径, demo 不适用 · (c) 两个都留 (demo 口径 + 整机口径分列, 需拆 claim key) ⇒ ★**main 倾向 (c) (25.00 对整机阶段仍可能有效, 直接删会丢留痕) ⇒ 但改 G7 判据要 H-1 重基线 ⇒ 不许自己改 G7 / 不许改 claim 值** ★\n"
    "· ★**⇒ 新门禁第 ① 条改成「★CROSS_LINKS 里每个 ref 必须与网表 board 栏一致 (board == HINGE 才算跨铰链)★」**(而不是「ref 必须在网表里存在」—— CONN_CAM/CONN_LIGHT 在网表里存在, 但 board = MAIN_PCB ⇒ 不跨铰链) ★\n"
    "· ★**另注**: 老板 2026-11-02 19:25 指示① (锁死表第 43 行) 说「结构问题直接不考虑」⇒ ★**本单属【结构侧判据/文档口径】(不做结构设计), 收的是 demo 硬件真相 (网表 board 栏) ⇒ 与主线 (原理图 demo) 同向** ★\n"
    "· ★**已在 11:56 用 subagents steer 把本订正送进在跑的 mech-lead 会话 (mode=restart·带订正重启) ⇒ 不必等它自己撞上** ★"
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
    with open(LOG, encoding="utf-8") as f:
        log = yaml.safe_load(f) or {}
    issues = log.get("issues") or []
    backup = LOG + ".bak_20261116_1158_correction_240"
    shutil.copy2(LOG, backup)

    hit = 0
    for it in issues:
        if it.get("id") != "ISS-240":
            continue
        hit += 1
        it["note"] = (it.get("note") or "") + CORRECTION
        it["task_brief"] = (it.get("task_brief") or "") + CORRECTION
    if not hit:
        print("!! 找不到 ISS-240 -> 不写")
        return 2

    log["issues"] = issues
    atomic_write(LOG, yaml.safe_dump(log, allow_unicode=True, sort_keys=False, width=100000))
    print("ISS-240 订正留痕已写入 (note + task_brief 各追加一段) · backup=" + os.path.basename(backup))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
