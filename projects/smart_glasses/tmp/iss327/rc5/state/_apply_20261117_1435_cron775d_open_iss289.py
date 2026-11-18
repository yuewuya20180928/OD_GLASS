#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
moli (项目总工) 2026-11-17 14:3x · job 775d9893「ARS45 继续执行后继计划」
★新开 ISS-289 (owner=mech-lead) —— 「板只改一次」那一趟的【结构侧最后一道交叉核对】★
=========================================================================================
★**开单依据 (★main 本机实读 + 实跑, 不抄任何交卷报告★)**:
· ★**hw-lead 侧**: `HW/PCB/BOARD_FRAME_CALIBER.md` 的 `cal:S6_TARGETS` JSON 块 = 20 个
  distinct ref, 每条带 `frame` 字段且全部 = `B160x100` ⇒ `HW/check_board_frame_caliber.py`
  查的是【帧标签齐 / 与文档串逐字一致 / 缺位 0 / 重叠 0 / 出界 0】⇒ ★**不查结构保留区** ★
· ★**MECH 侧**: `MECH/BOARD_ONEPASS_MECH_SYNC.md` §1/§5 + `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md`
  §3b/§4b/§6b/§7b 已给 SoM 承载区 / 两条开口 / 两条必须清空区 / LED 两假设 / 连接器对照表
  ⇒ ★**`MECH/check_onepass_mech_sync.py` 的 M1~M5 不碰 S6 目标落位** ★
  ⇒ ★**⇒ 两边各自绿, 合起来可能撞 = 「板只改一次」最怕的那种撞** ★
· ★**座体 pitch 冲突 (★mech-lead 自己 ISS-278 §7b.2 查出来的, main 本机复核过★)**:
  `J_DEBUG` / `J_UART` ⇒ BOM/网表写 1.27 mm 排针 (BOM_v1.csv:71 / :77) ⇒ 板读 land pattern
  是 0.50 mm ⇒ Δ 0.77 ⇒ ★**实物排针落不进 ⇒ 改板 or 改选型, 两条路都会动到那一趟** ★
· ★**corner_radius**: params 3.0 vs Edge.Cuts 实读 0.0 (4 条直角 gr_line) ⇒ 贴角 keep-out 口径失真
· ★**受保护 5 件本 job 14:3x 实测**: 板 611b869e… (mtime 2026-11-06 07:07:17) ·
  .kicad_pro 3e504d2b… · 网表 37f62ac3… · 脚表 a4270120… · BOM 5d02bece… ⇒ 零写板 · 零落表 成立 ★
★**为何派 mech-lead (★不是 hw-lead★)**: hw-lead 名下的 ISS-287 正在飞 (★子会话
  `agent:hw-lead:subagent:45238da5` status=running★) ⇒ ★**一个 agent 同时只能有一个写会话**
  ⇒ 本轮只有 mech-lead 名额可用 ⇒ 且 §1.2 的结构后果 (改 land 到 1.27 后开口/必清空区/净距
  怎么变) 本来就是 MECH 侧的活 ⇒ **不抢 hw-lead 的地界** ★
★**纪律**: 干活的人不许自签 ⇒ verify_by=main · ★不碰: 任何真源文件 / 任何分片 / 板 /
  网表 / 脚表 / BOM / 决策页 / outbox / 兄弟 job 的 ISS-287 · ISS-288 ★
"""
import fcntl
import os
import shutil

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
BAK = LOG + ".bak_20261117_1435_cron775d_open_iss289"
BRIEF = os.path.join(HERE, "dispatch_briefs", "ISS-289_mech_onpass_struct_crosscheck.md")

TITLE = (
    "★★[主线内·MECH 侧·板那一趟·结构侧交叉核对·内部活] ★★【「板只改一次」那一趟: "
    "① S6 的 20 个目标落位 × MECH 保留区 逐个交叉核对 + ② 座体类器件 (J_DEBUG/J_UART/J_USB_C/"
    "J_CHG/J_SOM_P1..P4) 的【选型 ↔ land pattern ↔ 结构占位】三方对照 (★重点: 排针 pitch "
    "1.27 mm vs 板读 0.50 mm ⇒ 实物排针落不进★) + ③ `corner_radius` 3.0 vs 0.0 的贴角 keep-out 口径】★★ "
    "⇒ ★**零写板 · 零落表 · 零改 `HW/` · 零改既有 MECH 判据脚本**★ ⇒ ★**产出 = 一份交叉核对表 + "
    "一道机器闸 + 一份「必须在那一趟一起改」的清单 (★清单要能直接进 `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md`★)**★"
)

DESC = (
    "★main 2026-11-17 14:3x 本机实读 + 实跑 (不抄交卷报告)★\n"
    "★**① 病灶 (S6 落位 × 结构保留区 从来没交叉验过)**: `HW/PCB/BOARD_FRAME_CALIBER.md` 的 "
    "`cal:S6_TARGETS` = 20 个 distinct ref (逐个带 frame=B160x100) ⇒ `HW/check_board_frame_caliber.py` "
    "只查【帧标签齐 / 与文档串一致 / 缺位 0 / 重叠 0 / 出界 0】⇒ ★**不查结构保留区** ★; 而 MECH 侧 "
    "`MECH/BOARD_ONEPASS_MECH_SYNC.md` §5 机器块 + `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` "
    "§3b/§4b/§6b 已给 SoM 承载区 (焊盘实体 53.80×46.78 / 封装外形 56.70×46.78) / 两条开口 / "
    "两条座体必须清空区 / LED 两假设 ⇒ ★**`MECH/check_onepass_mech_sync.py` 的 M1~M5 不碰 S6 目标落位** ★ "
    "⇒ ★**⇒ 两边各自绿, 合起来可能撞 ⇒ 那一趟 S6 一跑就撞 ⇒ 板 md5 变第二次 ⇒ Gerber/投产包/留证链/"
    "盖章/发布全白跑** ★\n"
    "★**② 病灶 (座体 pitch 冲突 = 装不进)**: `J_DEBUG` / `J_UART` ⇒ BOM/网表写 **1.27 mm 排针** "
    "(`HW/BOM_v1.csv:71` / `:77`; 网表 P8 行规格串「1×4 1.27mm 排针 (JTAG)」/「1×2 1.27mm 排针 (UART)」) "
    "⇒ 板读 land pattern 是 **0.50 mm** ⇒ Δ 0.77 ⇒ ★**实物排针落不进 ⇒ 要么改板 (land 改 1.27 ⇒ "
    "座体占位变 ⇒ 开口宽度/必须清空区/净距全要重算 ⇒ 这是 MECH 侧的活) 要么改选型 (⇒ 改 BOM + 网表)** ★\n"
    "★**③ 口径缺陷**: `board.corner_radius_mm` MECH 期望 3.0 / 落表板实读 0.00 (Edge.Cuts = 4 条直角 "
    "`gr_line`) ⇒ Δ 3.000 ⇒ 贴角 keep-out 算出来的可用区失真\n"
    "★**④ 为什么现在做**: 「板只改一次」那一趟现在只被老板 2 条拍板卡住 (★W-2 `D_LED_G` 外露 + A4/A5 "
    "关机语义/负载开关追认★) ⇒ ★**老板点头之前, 必须把结构侧最后两个没人验过的接口验完** ⇒ "
    "否则点头之后开那一趟 ⇒ 撞 ⇒ 板改第二次** ★\n"
    "★**⑤ 名额理由**: hw-lead 名下 ISS-287 在飞 (★子会话 `agent:hw-lead:subagent:45238da5` status=running★) "
    "⇒ ★**一个 agent 同时只能有一个写会话** ⇒ 本轮只有 mech-lead 名额 ⇒ ★**且 §② 的结构后果本属 MECH 侧 "
    "⇒ 不抢别人的地界** ★"
)

NOTE = (
    "2026-11-17 14:3x (cron 775d9893 继续执行后继计划) 新开 ★**依据 = main 14:3x 本机实读 "
    "`HW/PCB/BOARD_FRAME_CALIBER.md` / `MECH/BOARD_ONEPASS_MECH_SYNC.md` / `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` "
    "+ 实跑 `HW/check_board_frame_caliber.py` / `MECH/check_onepass_mech_sync.py` (★两边各自绿, 合起来没人验★)** ★\n"
    "⇒ ★**任务书全文 = `state/dispatch_briefs/ISS-289_mech_onpass_struct_crosscheck.md` (★已过 "
    "`python3 state/check_brief_commands.py --brief-file` ⇒ rc=0★)** ★\n"
    "⇒ ★**口径**: ★**纯分析 + 规格页 + 机器闸 · 零写板 · 零落表 · 零改 `HW/` · 零改既有 MECH 判据脚本** ★ "
    "⇒ ★**符合老板 2026-11-17 00:43「PCB 类先派纯分析/作业包类」纪律** ★\n"
    "⇒ ★**交付要含「必须在那一趟一起改」的清单 (可直接进 `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md`) ⇒ 转 main 转 hw-lead** ★\n"
    "⇒ ★**受保护 5 件本 job 14:3x 实测**: 板 611b869e… (mtime 2026-11-06 07:07:17) · .kicad_pro 3e504d2b… · "
    "网表 37f62ac3… · 脚表 a4270120… · BOM 5d02bece… ⇒ 零写板 · 零落表 成立 ★"
)


def main():
    with open(BRIEF, encoding="utf-8") as f:
        brief_text = f.read()
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        with open(LOG, encoding="utf-8") as f:
            log = yaml.safe_load(f)
        issues = log["issues"]
        if any(i.get("id") == "ISS-289" for i in issues):
            print("⚠ ISS-289 已存在 ⇒ 幂等跳过")
            fcntl.flock(lk, fcntl.LOCK_UN)
            return
        issues.append({
            "id": "ISS-289",
            "title": TITLE,
            "severity": "high",
            "source_blocker": None,
            "source_agent": "main",
            "desc": DESC,
            "owner": "mech-lead",
            "reporter": "main",
            "raised": "2026-11-17",
            "due": "2026-11-20",
            "status": "open",
            "external": False,
            "need_keys": [],
            "fix_ref": "",
            "verify_by": "main",
            "verify_result": "",
            "verify_date": "",
            "note": NOTE,
            "dispatched_at": "",
            "task_brief": brief_text,
        })
        shutil.copy2(LOG, BAK)
        tmp = LOG + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)
        os.replace(tmp, LOG)
        fcntl.flock(lk, fcntl.LOCK_UN)
    print("备份: %s" % BAK)
    print("issue_log 已追加 ISS-289 (owner=mech-lead, status=open, due=2026-11-20)")


if __name__ == "__main__":
    main()
