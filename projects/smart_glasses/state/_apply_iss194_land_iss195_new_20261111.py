#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-194 (hw-lead) 交卷 ⇒ main 独立验收签字 (2026-11-11 20:2x, 项目总工 main)

★**为什么这一单要【单独落账】而不是等下一轮**: hw-lead 在 20:1x 交卷了, 但 ★**会话在 20:09 结束前
   status 仍是 `fixing`** ⇒ ★**如果不等它落账就结束本轮, hw-lead 的唯一名额又被一条【已经干完】的单占住
   ⇒ 下一轮 advance.py 照样跳过它** ⇒ ★**这正是本轮开头查出来的那个病的【轻症版】(ISS-181/192/193 同族)**
   ⇒ ★**⇒ 交卷即落账, 不留假标记** ★

★**我独立重跑 (★不采信自述★)**:
  ① `python3 HW/pcb60x30_check.py` ⇒ 54/58 通过 · **FAIL 4** · WARN 0
     ★**且这 4 个 FAIL 与孔位【无关】—— 我做了对照实验**: ★**把孔位退回套B (S1 2.50 / S2 27.50) 重跑
       ⇒ 同样 54/58 · FAIL 4 · 同 4 条** (RK3588 需 11 层 / RK3576 需 9 层 / RK3588 面积缺 497.3mm² /
       板长加到上限仍装不下) ⇒ ★**⇒ 改前就是红, 改后还是同样红, 一条没多一条没少 ⇒ 改孔位没有引入任何新红**
       ⇒ ★**它【没有为了让闸变绿而降级判据】(★降级等于伪造验收★) ⇒ 这一点是对的** ★
  ② ★**孔位相关的 10 个检查项全过** (★我逐条读的★): RK3588/RK3576 各 P1/P2/S1/S2 孔心距边 8.00mm ·
     ★**S1/S2 孔壁距边 1.80 → 7.30mm** (★这正是本单要修的那个数★) · 孔间最小中心距 5.00mm / 孔壁间距 3.30mm
     ⇒ ★**与 brief 的验收数一致: S1/S2 的 y = 10.0 / 20.0 · edge_wall 7.30 · edge_to_center 8.00** ★
  ③ `python3 HW/hw_week_20261101_check.py` ⇒ 45 项 | PASS 41 | FAIL 4 ⇒ ★**与套B 版同数 ⇒ 同上, 与孔位无关** ★
  ④ `python3 MECH/pinset2_mech_check.py` ⇒ **rc=0** (★结构侧闸: 硬件侧孔位口径与结构侧定版一致 · 38 项 FAIL 0★)
  ⑤ `python3 state/merge.py` ⇒ rc=0 (冲突 0) · `python3 state/gate_check.py` ⇒ rc=0 (Q1 18/18)
  ⑥ ★**它自己独立复核了仲裁依据** (★不是抄我的自述★): ★**它自己解析两个二进制 STL + 0.5mm 顶面栅格化
     ⇒ 得出四孔心 = (8,10)/(8,15)/(52,15)/(52,20) ⇒ 套B 的 (8,2.5)/(52,27.5) 实心无孔** ⇒ ★**与我 18:4x
     的独立结论一致** ★

★**它顺手在同一个文件里修的 2 处同源套B 派生值 (★我核过, 认可★)**:
  · `checks[47]` 原名/note 称"Y 力臂 10→25mm、抗扭几何更好、+5.48mm" ⇒ ★**套A 下实为 45.12 vs 45.12,
    力臂变化 +0.00mm = 持平无增益** (★与 `MECH/BOARD_GEOM_30MM.md` §4.2 一致★) ⇒ ★**不改 = 留一句假账** ★
  · `checks[48]` note "骨架件不用重新开孔" ⇒ 改为 ★**"X 向不用重开、Y 向需平移 +7.50"** (★原话是错的★)
  ⇒ ★**这两处是【同一个套B 漂移的派生值】, 在同一个文件里 ⇒ 改它是本单范围内的 (不是越界)★**

★**★它报上来的一条【真影响】的漂移 (★我独立复算坐实了★) ⇒ 我开单跟, 不让它顺手改★**:
  ★**`HW/iss121_mic_magnet_check.py`:171 + `.json`:189 + `ISS121_MIC_MAGNET_POSITION.md`:161 三处引 15mm 孔位** ⇒
  ★**我按它的公式复算**: 麦 M1 封装 2.90×1.60 中心 (5.00,12.00) ⇒ 到 S1 孔心的净空:
  套B (S1 y=2.50) ⇒ dy=9.50 ⇒ 净空 ≈ 8.14mm · 套A (S1 y=10.00) ⇒ dy=2.00 ⇒ ★**净空 ≈ 1.26mm** ★
  ⇒ ★**⇒ 它的 "3.01→1.26mm" 数字我实测坐实 (★我独立算得 1.26mm, 与它一致★)** ⇒ ★**余量掉了一大截但
  仍不重叠、结论方向不变** ⇒ ★**⇒ 属"要重算的另一张单", 不是本单的锅 ⇒ ★**已开 ISS-195 跟, 不许它顺手改**
  (★那个文件是 ISS-121 的地界★)** ★

★**边界核查 (★我实测 mtime + md5★)**: 本轮它只写了 `HW/pcb60x30_check.py` + `HW/pcb60x30_check.json`
  (★`state/fragments/hw.yaml` 未动 ✔ —— 它说得对: claim 本来就是套A, note 本来就写 "S ±5.00 不变" ⇒ 无需回填★)
  ⇒ ★**板 611b869e… / 网表 c78f9912… / pins 4814617e… / BOM 3ad04e1a… / .kicad_pro 3e504d2b… 一字未动** ✔
  ⇒ ★**`HW/PCB/STACKUP.md` / `LAYOUT_RULES.md` / `GEN_SELF_CHECK.txt` / `_frame_reference.kicad_pcb` 的 mtime 变了
  ⇒ ★**但 git diff 实测【除时间戳行外零内容差异】⇒ 是巡检连带重出的已知副作用, 不是它改的** ★

★**落账纪律**: flock(state/.issue_log.lock) + 锁内重读 + yaml 往返逐字节自证 + 原子写 (tmp→fsync→replace→fsync(dir))
★**边界**: 不改 §0 锁死表 · 不写任何子总工的分片 · 不发邮件 / 不联系供应商 / 不下采购单
"""
from __future__ import annotations

import fcntl
import os
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")

V194 = (
    "2026-11-11 20:2x 项目总工亲核通过 (verify_by=main ≠ owner=hw-lead)。★**目标达成**: PIN-SET-2 孔位表"
    "【套B ⇒ 套A】已改完: `HW/pcb60x30_check.py`:116-117 的 S1 **(8.00,10.00)** / S2 **(52.00,20.00)**"
    "(★P1/P2 ⌀2.00 一律未动★) + `HW/pcb60x30_check.json` 已重生成 ⇒ ★**实测两段 sec4_holes 都是 "
    "{P1:(8,15,7.0) P2:(52,15,7.0) S1:(8,10,7.3) S2:(52,20,7.3)}** ⇒ ★**S1/S2 的 y = 10.0/20.0 · "
    "edge_wall 1.80 → 7.30 · edge_to_center 全 8.00 · ov_escape_band / ov_pkg / ov_jchg_keepout 全 0.0** "
    "⇒ 与 brief 的验收数逐项一致。★**我独立重跑 (不采信自述)**: `HW/pcb60x30_check.py` 54/58 · FAIL 4 · WARN 0 · "
    "★**且这 4 个 FAIL 与孔位无关 —— 我做了对照实验**: 把孔位退回套B (S1 2.50 / S2 27.50) 重跑 ⇒ **同样 54/58 · "
    "FAIL 4 · 同 4 条** (RK3588 需 11 层 / RK3576 需 9 层 / RK3588 面积缺 497.3mm² / 板长加到上限仍装不下) ⇒ "
    "⇒ **改前就是红, 改后还是同样红, 一条没多一条没少 ⇒ 改孔位没有引入任何新红** ⇒ ★**它【没有为了让闸变绿而"
    "降级判据】(★降级等于伪造验收★) ⇒ 这一点是对的** ★ · 孔位相关 **10 项全过** (RK3588/RK3576 各 P1/P2/S1/S2 "
    "孔心距边 8.00mm · S1/S2 孔壁 7.30mm · 孔间最小中心距 5.00mm / 孔壁间距 3.30mm) · "
    "`HW/hw_week_20261101_check.py` 45 项 PASS 41 FAIL 4 (★与套B 版同数 ⇒ 同上★) · "
    "`MECH/pinset2_mech_check.py` rc=0 (★结构侧闸: 硬件侧孔位口径与结构侧定版一致 · 38 项 FAIL 0★) · "
    "`state/merge.py` rc=0 (冲突 0) · `state/gate_check.py` rc=0 (Q1 18/18) ⇒ ★**全绿** ★。★**它自己独立复核了"
    "仲裁依据 (不是抄我的自述)**: ★**它自己解析两个二进制 STL + 0.5mm 顶面栅格化 ⇒ 四孔心 = (8,10)/(8,15)/(52,15)/"
    "(52,20) ⇒ 套B 的 (8,2.5)/(52,27.5) 实心无孔** ⇒ ★**与我 18:4x 的独立结论一致** ★。★**它顺手在同一文件里修了"
    "2 处同源套B 派生值 (我核过, 认可)**: `checks[47]` 原称「Y 力臂 10→25mm、抗扭几何更好、+5.48mm」⇒ 套A 下实为 "
    "**45.12 vs 45.12, 力臂变化 +0.00mm = 持平无增益** (★与 `MECH/BOARD_GEOM_30MM.md` §4.2 一致★) ⇒ 不改 = 留一句假账; "
    "`checks[48]` note「骨架件不用重新开孔」⇒ 改为「**X 向不用重开、Y 向需平移 +7.50**」⇒ 原话是错的 ⇒ ★**这两处"
    "是同一个套B 漂移的派生值, 在同一文件里 ⇒ 属本单范围, 不算越界** ★。★**★它报上来的一条【真影响】的漂移 "
    "(我独立复算坐实了) ⇒ 已开 ISS-195 跟, 不许它顺手改★**: `HW/iss121_mic_magnet_check.py`:171 + `.json`:189 + "
    "`ISS121_MIC_MAGNET_POSITION.md`:161 三处引 15mm 孔位 ⇒ ★**我按它的公式独立复算**: 麦 M1 封装 2.90×1.60 中心 "
    "(5.00,12.00) ⇒ 到 S1 孔心净空: 套B (S1 y=2.50) ⇒ dy=9.50 ⇒ **≈8.14mm** · 套A (S1 y=10.00) ⇒ dy=2.00 ⇒ "
    "**≈1.26mm** ⇒ ★**它的「3.01→1.26mm」我实测坐实 (我独立算得 1.26mm, 与它一致) ⇒ 余量掉一大截但仍不重叠、"
    "结论方向不变** ⇒ 属「要重算的另一张单」(★那个文件是 ISS-121 的地界★) ⇒ ★**已开 ISS-195** ★。★**边界核查 "
    "(我实测 mtime + md5)**: 本轮只写了 `HW/pcb60x30_check.py` + `HW/pcb60x30_check.json` (★`state/fragments/hw.yaml` "
    "未动 ✔ —— claim 本就是套A、note 本就写「S ±5.00 不变」⇒ 无需回填★) ⇒ ★**板 611b869e… / 网表 c78f9912… / "
    "pins 4814617e… / BOM 3ad04e1a… / .kicad_pro 3e504d2b… 一字未动** ✔ ⇒ ★**`HW/PCB/STACKUP.md` / `LAYOUT_RULES.md` "
    "/ `GEN_SELF_CHECK.txt` / `_frame_reference.kicad_pcb` 的 mtime 变了 ⇒ 但 git diff 实测【除时间戳行外零内容差异】⇒ "
    "是巡检连带重出的已知副作用, 不是它改的** ★ ⇒ ★**签字通过** ★"
)

NOTE_195 = (
    "\n\n★2026-11-11 20:2x 项目总工**开单 (ISS-195)** —— ★**ISS-194 (hw-lead) 交卷时扫出的一条【真影响】的"
    "同源孔位漂移: 麦 (M1) 到 S1 压紧螺钉孔的孔壁净空, 随套B ⇒ 套A 从 ≈8.14mm 掉到 ≈1.26mm** ★\n"
    "★**实测依据 (main 独立复算, 不采信自述)**: 麦 M1 封装 **2.90 × 1.60mm**, 中心 **(5.00, 12.00)**;\n"
    "  套B (S1 y=2.50) ⇒ 孔心距麦中心 dy=**9.50** ⇒ 净空 ≈ **8.14mm**;\n"
    "  套A (S1 y=10.00) ⇒ dy=**2.00** ⇒ 净空 ≈ **1.26mm** (★与 hw-lead 自报的 3.01→1.26 末值一致★)\n"
    "⇒ ★**结论: 仍不重叠、结论方向不变, 但余量掉了一大截 ⇒ 该单要重算, 不能沿用 15mm 老口径** ★\n"
    "★**为什么另开单而不是让 ISS-194 顺手改**: ★**`HW/iss121_mic_magnet_check.py` / `HW/iss121_mic_magnet_check.json` "
    "/ `HW/ISS121_MIC_MAGNET_POSITION.md` 是【ISS-121 的地界】** ⇒ ★**ISS-194 的 brief 明确「只写 "
    "`HW/pcb60x30_check.py` + `.json`」⇒ 越界 ⇒ ★**另开单跟** ★\n"
    "★**三处引 15mm 孔位的位置 (★hw-lead 扫出来的★)**: `HW/iss121_mic_magnet_check.py`:171 · "
    "`HW/iss121_mic_magnet_check.json`:189 · `HW/ISS121_MIC_MAGNET_POSITION.md`:161\n"
    "★**判据要求**: 按现行 60×30 板 + 套A 孔位重算麦克风磁体/麦克风的孔壁净空与最小间距, 给出 PASS/FAIL 与"
    "余量数字; ★**若 FAIL ⇒ 报 main 裁决 (不许自行改孔位或改判据)** ★\n"
    "★**边界**: ★**只写 `HW/iss121_mic_magnet_check.py` + `.json` + `HW/ISS121_MIC_MAGNET_POSITION.md` + HANDOFF 报告** "
    "⇒ ★**不许碰 `HW/pcb60x30_check.*` (那是 ISS-194 的地界, 已定版) · 不许碰板/网表/原理图/任何 `state/gen_*.py`** "
    "⇒ ★**不许联系供应商/原厂** ★"
)

NEW_195 = {
    "id": "ISS-195",
    "title": ("★【ISS-194 的连带账·真影响】麦 M1 到 S1 压紧螺钉孔的孔壁净空随套A 从 ≈8.14mm 掉到 ≈1.26mm "
              "⇒ `HW/iss121_mic_magnet_check.*` 三处仍引 15mm 老口径 ⇒ 要按现行孔位重算"),
    "severity": "medium",
    "owner": "hw-lead",
    "verify_by": "main",
    "reporter": "main",
    "raised": "2026-11-11",
    "due": "2026-11-13",
    "status": "open",
    "task_brief": (
        "★**目标**: 把 `HW/iss121_mic_magnet_check.py` / `.json` / `HW/ISS121_MIC_MAGNET_POSITION.md` 里"
        "★**引 15mm 老口径孔位**的三处, ★**按现行 60×30 板 + 套A 孔位重算** ⇒ 给出麦克风磁体/麦克风的孔壁净空"
        "与最小间距的 PASS/FAIL 与余量数字。\n\n"
        "★**为什么现在做 (★main 2026-11-11 20:2x 独立复算, 不是推测★)**:\n"
        "· ISS-194 (孔位表 套B ⇒ 套A) 交卷后, 扫出三处仍引 15mm 老口径: "
        "`HW/iss121_mic_magnet_check.py`:171 · `HW/iss121_mic_magnet_check.json`:189 · "
        "`HW/ISS121_MIC_MAGNET_POSITION.md`:161\n"
        "· ★**main 独立复算**: 麦 M1 封装 **2.90 × 1.60mm**, 中心 **(5.00, 12.00)** ⇒ 到 S1 压紧螺钉孔的孔壁净空:\n"
        "  套B (S1 y=2.50) ⇒ dy=9.50 ⇒ **≈8.14mm** · 套A (S1 y=10.00) ⇒ dy=2.00 ⇒ **≈1.26mm**\n"
        "  ⇒ ★**余量掉了一大截, 但仍不重叠、结论方向不变** ⇒ ★**结论要按现行孔位重算, 不能沿用 15mm 老口径** ★\n"
        "· ★**为什么不在 ISS-194 里顺手改**: ★**那三个文件是 ISS-121 的地界** ⇒ ISS-194 的 brief 明确只写 "
        "`HW/pcb60x30_check.py` + `.json` ⇒ 越界 ⇒ ★**另开本单** ★\n\n"
        "★**做法**: ① ★**先读 `MECH/BOARD_GEOM_30MM.md` §4 (结构侧定版孔位, main 已验收签字)** + "
        "`HW/pcb60x30_check.py` 的 HOLES 表 (★套A: S1 (8.00,10.00) ⌀1.40 / S2 (52.00,20.00) ⌀1.40 / "
        "P1 (8.00,15.00) ⌀2.00 / P2 (52.00,15.00) ⌀2.00★) ⇒ ★**别用 15mm 老口径** ★② ★**按那个脚本自己的公式** "
        "重算麦 M1 封装与孔的孔壁净空 + 与其它件的最小间距 ③ ★**改这三处** (★只改引用/数字, 不许改判据阈值★) "
        "④ 重跑该脚本, 给出 PASS/FAIL 与余量数字\n\n"
        "★**验收自证 (交卷前跑, 把输出贴进回复)**\n"
        "```\n"
        "python3 HW/iss121_mic_magnet_check.py     # rc 与输出贴出来 (★新旧净空两个数都要给★)\n"
        "python3 state/merge.py                     # rc 必须 0 (冲突 0)\n"
        "python3 state/gate_check.py                # Q1 必须 18/18\n"
        "md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv   # 必须一字未变 (611b869e…)\n"
        "```\n"
        "★**交卷 ≤ 15 行** (结论先行; ★**明确写 PASS 还是 FAIL + 余量多少 mm★; ★**若 FAIL ⇒ 只报给 main 裁决, "
        "不许自行改孔位或改判据** ★)\n\n"
        "★**边界 (不许越)**\n"
        "· ★**只写**: `HW/iss121_mic_magnet_check.py` + `HW/iss121_mic_magnet_check.json` + "
        "`HW/ISS121_MIC_MAGNET_POSITION.md` + `HANDOFF/` 下交卷报告 + ★**必要时** `state/fragments/hw.yaml` "
        "(走 `state/frag_write.py`; ★**只许新增/订正本单相关条目★)\n"
        "· ★**不许碰**: `HW/pcb60x30_check.py` / `HW/pcb60x30_check.json` (★那是 ISS-194 的地界, 已定版★) · "
        "`HW/netlist_v1.csv` · `HW/netlist_v1_pins.csv` · `HW/PCB/demo_mainboard.kicad_pcb` · "
        "`HW/PCB/demo_mainboard*.kicad_sch` · 任何 `state/gen_*.py` · `PROJECT_TRACKER.md` §0 · **别人的分片** · "
        "`state/issue_log.yaml` (★**改 issue 状态是 main 的活**)\n"
        "· ★**不许联系供应商/原厂** (外发一律经项目总工) · ★**证据分级** [实测]/[官方]/[推算]/[0数据] 必标\n"
        "· ★**不许改判据阈值来让自己变绿** (★降级等于伪造验收★)"
    ),
}


def main() -> int:
    lock_fh = open(LOCK, "w")
    fcntl.flock(lock_fh, fcntl.LOCK_EX)
    try:
        with open(LOG, encoding="utf-8") as f:
            raw = f.read()
        doc = yaml.safe_load(raw)
        items = list(doc.get("issues") or [])
        before = {it.get("id"): dict(it) for it in items}

        # ---- 自证 ①: yaml 往返必须逐字节相同 ----
        if yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=200) != raw:
            print("❌ yaml 往返不一致 ⇒ 放弃写盘")
            return 2

        # ---- ① ISS-194 ⇒ verified ----
        done = False
        for it in items:
            if it.get("id") == "ISS-194":
                it["status"] = "verified"
                it["verify_result"] = V194
                it["verify_at"] = "2026-11-11 20:2x"
                it["verify_by"] = "main"
                it["fix_ref"] = "HW/pcb60x30_check.py (套A 孔位表) + HW/pcb60x30_check.json (sec4_holes 两段)"
                done = True
        if not done:
            print("❌ 找不到 ISS-194 ⇒ 放弃写盘")
            return 2

        # ---- ② 新开 ISS-195 ----
        if not any(it.get("id") == "ISS-195" for it in items):
            items.append(dict(NEW_195))
        else:
            print("❌ ISS-195 已存在 ⇒ 放弃写盘 (防重复开单)")
            return 2

        doc["issues"] = items

        # ---- 自证 ②: 非目标 issue 逐字段不变 ----
        after = {it.get("id"): it for it in items}
        if len(after) != len(before) + 1:
            print("❌ issue 总数不对 ⇒ 放弃写盘")
            return 2
        for k, b in before.items():
            if k == "ISS-194":
                continue
            if after[k] != b:
                print("❌ 非目标 issue 发生变化: %s ⇒ 放弃写盘" % k)
                return 2

        # ---- 原子写 ----
        fd, tmp = tempfile.mkstemp(dir=HERE, prefix=".issue_log.", suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                yaml.safe_dump(doc, f, allow_unicode=True, sort_keys=False, width=200)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, LOG)
        except Exception:
            if os.path.exists(tmp):
                os.unlink(tmp)
            raise
        dfd = os.open(HERE, os.O_RDONLY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)

        print("✅ issue_log.yaml 已落盘 (原子写, 锁内重读)")
        print("   - ISS-194 → verified (main 亲核签字; ★**含对照实验: 套B 版 FAIL 数相同 ⇒ 4 个 FAIL 与孔位无关**)")
        print("   - ISS-195 新开 (麦 M1→S1 孔壁净空 8.14→1.26mm 连带账, owner=hw-lead, verify_by=main)")
        print("   - 别的 %d 条 issue 一个字节未动 ✔" % (len(before) - 1))
        return 0
    finally:
        fcntl.flock(lock_fh, fcntl.LOCK_UN)


if __name__ == "__main__":
    sys.exit(main())
