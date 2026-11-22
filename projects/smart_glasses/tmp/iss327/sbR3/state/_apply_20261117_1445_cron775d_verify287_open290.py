#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
moli (项目总工) 2026-11-17 14:4x · job 775d9893「ARS45 继续执行后继计划」
★ISS-287 落 verified (main 独立复验) + ISS-288 追加 cont1 说明 + 新开 ISS-290 (owner=mech-lead)★
=========================================================================================
★**ISS-287 复验依据 (★main 14:3x~14:4x 本机实跑, 不抄交卷报告★)**:
  · 板 md5 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17` ⇒ **逐字节未变** ✔
  · `state/gen_pcb_netlist_board.py:536` ⇒ **写死 `out = "/tmp/_layout_done_drc.json"`** ✔ (S-1 漏网点坐实)
  · 板读 (pcbnew 只读): **官方板封装数 = 186 / 唯一位号 = 186** ✔ · `C_VBUS_GND` value=[待选型] 100µF
    @ (107.70, 42.50) ✔ · **带 `_1` 后缀位号 = 1 个 (`R_BAT_DET_1`)** ✔ ⇒ 交卷单 B3 读数表逐条对得上
  · `python3 HW/check_netlist_contradiction_r3.py` ⇒ **R3-A4: 在板上 40 颗 / 零标记 40 颗** ✔
    ⇒ **DNP 目标是 40, 不是 43 (43 = 12:30 落表前的旧数)** ✔
  · `state/merge.py` rc=0 · `state/gate_check.py` rc=0 (Q1 18/18) ⇒ 两道总闸全绿
  · 交卷单 25582 B + 沙盒 README 8956 B + `state/fragments/hw.yaml` 里 `iss287` key = 9 条 ⇒ 交付物齐
★**ISS-288 判定**: 补丁本体已落盘 (md5 `68c4becf…` = ISS-285 设计里写死的期望值) 且
  `python3 SW/tools/timing_check.py` ⇒ **SELFTEST 72/72 rc=0** (开工前 rc=1 · 68/71) ⇒
  **机器证据齐, 但交卷单 §1~§8 全是「待写」+ 分片 claim 不足** ⇒ **不重做, 只补交卷** ⇒ cont1
★**ISS-290 (本 job 新开, owner=mech-lead)**: 「板只改一次」那一趟的【结构侧最后一道交叉核对】
  ⇒ ★**ISS-289 已被并发 main 会话占用 (owner=hw-lead · 作业包现状值型判据对回盘面实测)** ⇒ 本单改号 290
★**纪律**: verify_by=main (干活的人不许自签) · ★不碰: 任何真源文件 / 任何分片 / 板 / 网表 / 脚表 /
  BOM / 决策页 / outbox / 兄弟 job 的 ISS-289 / ISS-287 / ISS-288
"""
import fcntl
import os
import shutil

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
BAK = LOG + ".bak_20261117_1445_cron775d_verify287_open290"
BRIEF = os.path.join(HERE, "dispatch_briefs", "ISS-290_mech_onpass_struct_crosscheck.md")
TODAY = "2026-11-17"

VERIFY_287 = (
    "★main 2026-11-17 14:3x~14:4x 本机独立复验 (不抄交卷报告)★ ⇒ 板 md5 `611b869e13518c3c023fb178f91a0075` "
    "+ mtime `2026-11-06 07:07:17` **逐字节未变** · `state/gen_pcb_netlist_board.py:536` **写死 "
    "`out = \"/tmp/_layout_done_drc.json\"`** 坐实 (S-1 沙盒写穿漏网点) · 板读 (pcbnew 只读) "
    "**官方板封装数 = 186 / 唯一位号 = 186** · `C_VBUS_GND` value=[待选型] 100µF @ (107.70,42.50) · "
    "**带 `_1` 后缀位号 = 1 个 (`R_BAT_DET_1`)** ⇒ 与交卷单 B3 读数表逐条一致 · "
    "`python3 HW/check_netlist_contradiction_r3.py` ⇒ **R3-A4 在板上 40 颗 / 零标记 40 颗** ⇒ "
    "**DNP 目标 = 40 (43 是 12:30 落表前旧数)** · `state/merge.py` rc=0 · `state/gate_check.py` rc=0 (Q1 18/18) · "
    "交卷单 `HANDOFF/2026-11-17_hw-lead_ISS287_沙盒干跑可行性探针.md` 25582 B + 沙盒 README 8956 B + "
    "`state/fragments/hw.yaml` 里 `iss287` key = 9 条 ⇒ **交卷物齐, 本条闭环** ⇒ "
    "★**S-2/S-3 (重跑生成器 ≠ 官方板: 26 处 Value 不同 + `C_VBUS_GND` 会掉) 与 S-4 (186/186 封装 FPID 全空) "
    "已进「板那一趟」任务书口径, 归 main 裁决路线甲/乙** ★"
)

NOTE_288 = (
    "\n\n★**2026-11-17 14:4x (cron 775d9893 继续执行后继计划) · cont1 续做 (★不是重做★)** ★\n"
    "⇒ ★**main 14:4x 本机实跑判定**: 子会话 `agent:sw-lead:subagent:b330509e` (14:25:45→14:39:47 · runtime 840s · "
    "status=timeout · abortedLastRun=true) **死在超时, 但活已干完** ★ ⇒ ★**补丁本体已落盘**: "
    "`SW/tools/timing_check.py` md5 = `68c4becffe6bcd708e388dba9d18a505` (★= ISS-285 交卷单里写死的"
    "「套用后期望 md5」逐字一致★) ⇒ ★**补丁效果已实跑**: `python3 SW/tools/timing_check.py` ⇒ 末行 "
    "**`SELFTEST 72/72 通过, rc=0`** (★开工前 rc=1 · 68/71 三条红★) ⇒ ★**⇒ 机器证据齐, 账目没入** ★\n"
    "⇒ ★**差的是**: 交卷单 `HANDOFF/2026-11-17_sw-lead_ISS288_timing_check补丁落地.md` = 1787 B · "
    "§1~§8 全是「★(填: 待写)★」⇒ **本趟只把已经跑出来的东西写成交卷单 + 补分片 claim** ★ ⇒ "
    "★**不许再改 `SW/tools/timing_check.py` 一个字节 (它已经是对的)★** ★\n"
    "⇒ ★**任务书 cont1 = `state/dispatch_briefs/ISS-288_sw_timing_check_patch_land_cont1.md` (4094 B · "
    "`check_brief_commands --brief-file` rc=0)** ★"
)

TITLE_290 = (
    "★★[主线内·MECH 侧·板那一趟·结构侧交叉核对·内部活] ★★【「板只改一次」那一趟: "
    "① S6 的 20 个目标落位 × MECH 保留区 逐个交叉核对 + ② 座体类器件 (J_DEBUG/J_UART/J_USB_C/"
    "J_CHG/J_SOM_P1..P4) 的【选型 ↔ land pattern ↔ 结构占位】三方对照 (★重点: 排针 pitch "
    "1.27 mm vs 板读 0.50 mm ⇒ 实物排针落不进★) + ③ `corner_radius` 3.0 vs 0.0 的贴角 keep-out 口径】★★ "
    "⇒ ★**零写板 · 零落表 · 零改 `HW/` · 零改既有 MECH 判据脚本**★ ⇒ ★**产出 = 一份交叉核对表 + "
    "一道机器闸 + 一份「必须在那一趟一起改」的清单 (★可直接进 `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md`★)**★"
)

DESC_290 = (
    "★main 2026-11-17 14:3x 本机实读 + 实跑 (不抄交卷报告)★\n"
    "★**① 病灶 (S6 落位 × 结构保留区 从来没交叉验过)**: `HW/PCB/BOARD_FRAME_CALIBER.md` 的 "
    "`cal:S6_TARGETS` = 20 个 distinct ref (逐个带 frame=B160x100) ⇒ `HW/check_board_frame_caliber.py` "
    "只查【帧标签齐 / 与文档串一致 / 缺位 0 / 重叠 0 / 出界 0】⇒ **不查结构保留区**; 而 MECH 侧 "
    "`MECH/BOARD_ONEPASS_MECH_SYNC.md` §5 机器块 + `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` "
    "§3b/§4b/§6b 已给 SoM 承载区 (焊盘实体 53.80×46.78 / 封装外形 56.70×46.78) / 两条开口 / "
    "两条座体必须清空区 / LED 两假设 ⇒ **`MECH/check_onepass_mech_sync.py` 的 M1~M5 不碰 S6 目标落位** ⇒ "
    "**⇒ 两边各自绿, 合起来可能撞 ⇒ 那一趟 S6 一跑就撞 ⇒ 板 md5 变第二次 ⇒ Gerber/投产包/留证链/"
    "盖章/发布全白跑** ★\n"
    "★**② 病灶 (座体 pitch 冲突 = 装不进)**: `J_DEBUG` / `J_UART` ⇒ BOM/网表写 **1.27 mm 排针** "
    "(`HW/BOM_v1.csv:71` / `:77`; 网表 P8 行规格串「1×4 1.27mm 排针 (JTAG)」/「1×2 1.27mm 排针 (UART)」) "
    "⇒ 板读 land pattern 是 **0.50 mm** ⇒ Δ 0.77 ⇒ **实物排针落不进 ⇒ 要么改板 (land 改 1.27 ⇒ "
    "座体占位变 ⇒ 开口宽度/必须清空区/净距全要重算 ⇒ 这是 MECH 侧的活) 要么改选型 (⇒ 改 BOM + 网表)** ★\n"
    "★**③ 口径缺陷**: `board.corner_radius_mm` MECH 期望 3.0 / 落表板实读 0.00 (Edge.Cuts = 4 条直角 "
    "`gr_line`) ⇒ Δ 3.000 ⇒ 贴角 keep-out 算出来的可用区失真 ★\n"
    "★**④ 为什么现在做**: 「板只改一次」那一趟现在只被老板 2 条拍板卡住 (★W-2 `D_LED_G` 外露 + A4/A5 "
    "关机语义/负载开关追认★) ⇒ **老板点头之前, 必须把结构侧最后两个没人验过的接口验完** ★\n"
    "★**⑤ 名额理由**: hw-lead 名下 ISS-287 已由 main 复验落 verified ⇒ hw-lead 名额已释放 (但 ISS-289 "
    "已占) ⇒ **本单只派 mech-lead (唯一空闲总工)** ⇒ 且 §② 的结构后果本属 MECH 侧 ⇒ 不抢别人的地界 ★"
)

NOTE_290 = (
    "2026-11-17 14:4x (cron 775d9893 继续执行后继计划) 新开 ★**依据 = main 14:3x 本机实读 "
    "`HW/PCB/BOARD_FRAME_CALIBER.md` (cal:S6_TARGETS) / `MECH/BOARD_ONEPASS_MECH_SYNC.md` / "
    "`MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` §3b/§7b + 实跑 `HW/check_board_frame_caliber.py` / "
    "`MECH/check_onepass_mech_sync.py` (★两边各自绿, 合起来没人验★)** ★\n"
    "⇒ ★**任务书全文 = `state/dispatch_briefs/ISS-290_mech_onpass_struct_crosscheck.md` (★已过 "
    "`python3 state/check_brief_commands.py --brief-file` ⇒ rc=0★)** ★\n"
    "⇒ ★**口径**: **纯分析 + 规格页 + 机器闸 · 零写板 · 零落表 · 零改 `HW/` · 零改既有 MECH 判据脚本** ⇒ "
    "★**符合老板 2026-11-17 00:43「PCB 类先派纯分析/作业包类」纪律** ★\n"
    "⇒ ★**交付要含「必须在那一趟一起改」的清单 ⇒ 转 main 转 hw-lead 并进 `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md`** ★\n"
    "⇒ ★**编号说明**: 本单原拟 ISS-289, 但 14:3x 有并发 main 会话把 ISS-289 用掉 (owner=hw-lead · "
    "「作业包现状值型判据对回盘面实测」· 任务书 `state/dispatch_briefs/ISS-289_hw_workpack_state_values_reconcile.md`) "
    "⇒ **本单改号 ISS-290, 零撞号** ★\n"
    "⇒ ★**受保护 5 件本 job 14:4x 实测**: 板 611b869e… (mtime 2026-11-06 07:07:17) · .kicad_pro 3e504d2b… · "
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
        by_id = {i.get("id"): i for i in issues}

        # ── ISS-287: fixing → verified (main 独立复验) ──
        i287 = by_id.get("ISS-287")
        if i287 is None:
            print("⚠ ISS-287 不存在")
        elif i287.get("status") == "verified":
            print("· ISS-287 已是 verified ⇒ 幂等跳过")
        else:
            i287["status"] = "verified"
            i287["verify_by"] = "main"
            i287["verify_result"] = "pass"
            i287["verify_date"] = TODAY
            i287["fix_ref"] = "HANDOFF/2026-11-17_hw-lead_ISS287_沙盒干跑可行性探针.md"
            i287["note"] = (i287.get("note") or "") + "\n\n★★ **main 2026-11-17 14:4x 复验落 verified** ★\n" + VERIFY_287
            print("· ISS-287 fixing → verified (main 独立复验)")

        # ── ISS-288: 追加 cont1 说明 (状态保持 fixing, 续做) ──
        i288 = by_id.get("ISS-288")
        if i288 is None:
            print("⚠ ISS-288 不存在")
        else:
            i288["note"] = (i288.get("note") or "") + NOTE_288
            print("· ISS-288 追加 cont1 说明 (状态仍 fixing)")

        # ── ISS-290: 新开 (owner=mech-lead) ──
        if "ISS-290" in by_id:
            print("⚠ ISS-290 已存在 ⇒ 幂等跳过")
        else:
            issues.append({
                "id": "ISS-290",
                "title": TITLE_290,
                "severity": "high",
                "source_blocker": None,
                "source_agent": "main",
                "desc": DESC_290,
                "owner": "mech-lead",
                "reporter": "main",
                "raised": TODAY,
                "due": "2026-11-20",
                "status": "open",
                "external": False,
                "need_keys": [],
                "fix_ref": "",
                "verify_by": "main",
                "verify_result": "",
                "verify_date": "",
                "note": NOTE_290,
                "dispatched_at": "",
                "task_brief": brief_text,
            })
            print("· ISS-290 已开 (owner=mech-lead, status=open, due=2026-11-20)")

        shutil.copy2(LOG, BAK)
        tmp = LOG + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)
        os.replace(tmp, LOG)
        fcntl.flock(lk, fcntl.LOCK_UN)
    print("备份: %s" % BAK)


if __name__ == "__main__":
    main()
