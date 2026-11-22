#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
moli (项目总工) 2026-11-17 16:0x · job 775d9893「ARS45 继续执行后继计划」
★ISS-289 落 verified (main 独立复验) + 新开 ISS-292 (owner=hw-lead)★
=========================================================================================
★**ISS-289 复验依据 (★main 15:5x~16:0x 本机实跑, 不抄交卷报告★)**:
  · 交卷单 `HANDOFF/2026-11-17_hw-lead_ISS289_作业包现状值对回盘面.md` = **628 行 / 76908 B** · B0~B6 七段齐
    (★占位符 grep 4 处命中全是「0 处残留」这句自述, 无真实未完成标记★)
  · 新闸 `python3 HW/check_workpack_state_values.py` ⇒ **rc=0** · `--selftest` ⇒ **rc=0 · 反向用例 10/10 通过**
  · `HW/check_onepass_preflight_coverage.py` ⇒ rc=0 · `HW/check_board_frame_caliber.py` ⇒ rc=0 ·
    `HW/check_netlist_contradiction_r3.py` ⇒ rc=1 (★现状读数, FINDINGS=2 = F2+F3, R3-A4 零标记 40★) ⇒ 与交卷单自评一致
  · 受保护 5 件逐字节未变: 板 `611b869e13518c3c023fb178f91a0075` (mtime 仍 `2026-11-06 07:07:17`) ·
    `.kicad_pro` `3e504d2be83152e337949723e909be1b` (mtime `2026-11-04 23:47:30`) · 网表 `37f62ac3…` ·
    脚表 `a4270120…` · BOM `5d02bece…` ⇒ **零写板 · 零落表 成立**
  · `state/fragments/hw.yaml` ⇒ `grep -c iss289` = **11** (★交卷单自报 11, 一致★) ⇒ 交付物齐
  · `state/merge.py` rc=0 · `state/gate_check.py` rc=0 (Q1 18/18, 按本单计分不再回退旧交接单) · `state/issue_check.py` rc=0
  · main 本机复验 hw-lead 的三问: ① 差的那 1 件 = `C_VBUS_GND` (★网表 L10/L12 的 board 列 = `CHG_BOARD`★ main 实读确认)
    ② 156 = 板侧要改名的位号数 / 1 = 板上已带 `_1` 的 ⇒ 改完 157 (S2 下掉 C_VBUS_GND ⇒ 156) ③ 29 条登记里 4 条走台账口径、
    25 条写死 ⇒ 收工必须同一次重锚
★**ISS-292 (本 job 新开, owner=hw-lead)**: 清单页生成器 `state/_iss277_build_preflight.py` 与盘面页脱钩
  ⇒ 跑一次 = 把 ISS-283/ISS-289 的订正全冲掉 (★卡「板只改一次」那一趟开工★) ⇒ 本单 = 生成器对齐 + 作业包 §3-S1
  指针订正 + 收工重锚强制项 ⇒ **零写板 · 零落表**
★**纪律**: verify_by=main (干活的人不许自签) · ★不碰: 任何真源文件 / 任何分片 (★hw.yaml 是 hw-lead 的, main 不写★) /
  板 / 网表 / 脚表 / BOM / 决策页 / outbox / 兄弟 job 的 ISS-290 / ISS-291
"""
import fcntl
import os
import shutil

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
BAK = LOG + ".bak_20261117_1600_cron775d_verify289_open292"
BRIEF = os.path.join(HERE, "dispatch_briefs", "ISS-292_hw_preflight_generator_realign.md")
TODAY = "2026-11-17"

VERIFY_289 = (
    "★main 2026-11-17 15:5x~16:0x 本机独立复验 (不抄交卷报告)★ ⇒ 交卷单 "
    "`HANDOFF/2026-11-17_hw-lead_ISS289_作业包现状值对回盘面.md` = **628 行 / 76908 B** · B0~B6 七段齐 (★占位符 grep "
    "4 处命中全是「0 处残留」这句自述, 无真实未完成标记★) ⇒ 新闸 `python3 HW/check_workpack_state_values.py` **rc=0** · "
    "`--selftest` **rc=0 · 反向用例 10/10 通过** ⇒ `HW/check_onepass_preflight_coverage.py` rc=0 · "
    "`HW/check_board_frame_caliber.py` rc=0 · `HW/check_netlist_contradiction_r3.py` rc=1 (★现状读数, FINDINGS=2 = "
    "F2+F3, R3-A4 零标记 **40**★) ⇒ **与交卷单自评逐条一致** ⇒ 受保护 5 件逐字节未变 (板 `611b869e…` mtime 仍 "
    "`2026-11-06 07:07:17` · `.kicad_pro` `3e504d2b…` mtime `2026-11-04 23:47:30` · 网表 `37f62ac3…` · 脚表 "
    "`a4270120…` · BOM `5d02bece…`) ⇒ **零写板 · 零落表 成立** ⇒ `state/fragments/hw.yaml` `grep -c iss289` = **11** "
    "(★与交卷单自报一致★) ⇒ `state/merge.py` rc=0 · `state/gate_check.py` rc=0 (Q1 18/18 · 按本单计分不再回退旧交接单) · "
    "`state/issue_check.py` rc=0 ⇒ 三道总闸全绿 ⇒ **本条闭环** ★\n"
    "★**main 本机复验 hw-lead 的三个问题 (★不采信口头, 自己查★)★**: ① **差的那 1 件 = `C_VBUS_GND`** ⇒ main 实读 "
    "`HW/netlist_v1.csv:10` 与 `:12` ⇒ 该位号两行的 board 列 = **`CHG_BOARD`** ⇒ 生成器 `BOARD_FILTER=\"MAIN_PCB\"` "
    "把它剔掉, 而官方板上有实物封装 ⇒ **单边差集 = 板级归属差, 不是漏数** ⇒ ★**动板那趟按「开工前 186 / 收工后 185」走** "
    "★ ② **156 与 1 不是一回事** ⇒ 156 = 板侧**要改名**的位号数 · 1 = 板上**已带** `_1` 的 (`R_BAT_DET_1`) ⇒ 改完 = 157 "
    "(S2 下掉 `C_VBUS_GND` ⇒ 156) ⇒ 两个数都已进闸 (`W12`/`C03` 与 `W18`, 类别 `ref_suffix`) ★ ③ **写死现状值 = 25 条** ⇒ "
    "29 条登记里只有 4 条走台账口径 ⇒ **收工必须同一次重锚** (→ 已开 ISS-292 把「收工后重锚」写成收工清单强制项) ★\n"
    "★**给老板/PM 的 4 条拍板项 (★hw-lead 只列事实与代价, 不代拍★)**: P1 那一趟任务书封装数写几个 (★main 口径 = 写两个数 "
    "186→185 并注明差的那 1 件是谁, 不用老板拍★) · P2 `C_VBUS_GND` 预留位留不留 (★老板/PM 域★) · P3 「收工后重锚」要不要设"
    "硬门 (★main 口径 = 设, 写进收工清单强制项, 不用老板拍★) · P4 清单页生成器谁对齐 (★→ 已开 ISS-292 派 hw-lead★) ★"
)

TITLE_292 = (
    "★★[主线内·PCB 线·纯生成器对齐+作业包指针订正类·内部活] ★★【清单页生成器 `state/_iss277_build_preflight.py` "
    "与盘面页脱钩 ⇒ 跑一次 = 把 ISS-283/ISS-289 的订正全冲掉】★★ ⇒ ★**生成器仍写 R3-A4「54/43/43」+ 脚表「15 条缺陷」"
    "+ 缺 `B32_V2_NET_RENAME`, 而盘面页已是 51/40/40 + 18 条**★** ⇒ ★**本单 = 生成器改成从真源读 (★不许再写死★) + 重跑幂等 "
    "硬判据 (★重跑后盘面页要么零变化, 要么只多 B32 一条且九处订正 anchor 一处不少★) + 作业包 §3-S1 位号真源指针改对 "
    "(`SCHEMATIC_V1_SPEC.json` 无 devices 段 ⇒ 真源 = `HW/netlist_v1_pins.csv`) + 「收工后重锚」写成收工清单强制项**★ "
    "⇒ ★**零写板 · 零落表**★"
)

DESC_292 = (
    "★main 2026-11-17 16:0x 本机实读 (不抄交卷报告)★\n"
    "★**① 生成器与盘面页同源关系断了 (★卡「板只改一次」那一趟开工★)**: `state/_iss277_build_preflight.py:110` 逐字 "
    "`\"[实测] R3-A4: MAIN_PCB且DNP 54 颗 · 在板上 43 颗 · 零标记 43 颗\"` ⇒ 而盘面 "
    "`HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 已被 ISS-289 手工订正成 **51 / 40 / 40** (★三次合法落表 09:58 · 12:16 · "
    "12:30 把 `BAT_DET` 三颗改成必装★); 同文件 `:26` 仍写「脚表 15 条缺陷」而盘面是 **18 条**; 且 ★**生成器里没有 "
    "`B32_V2_NET_RENAME`** (★ISS-283 落的 V-2 网改名条目, 盘面页已有★) ⇒ ★**⇒ 跑一次生成器 = 页回退到过期值 = 把 "
    "ISS-283/ISS-289 的订正全冲掉 ⇒ 新闸 `HW/check_workpack_state_values.py` 当场红 (★闸在正常工作★) ⇒ ★**⇒ 而这个红会"
    "出现在【动板那趟已经开工之后】⇒ 那时有人会去「改板凑绿」⇒ 代价 2-4 周 + ¥4-8K** ★\n"
    "★**② 条目 id `B17_DNP_43` 名字里带 43**: ★**不许改名 (★被别处引用★) ⇒ 只许订正它的【值】+ 旁注「id 是历史命名, 值已按"
    "落表链头前移」★ ★\n"
    "★**③ 作业包 §3-S1 的位号真源指针失效 (★ISS-289 need `iss289_s1_specjson_devices_missing` 的事实, main 已复验★)**: "
    "§3-S1 写「器件位号真源 = `HW/SCHEMATIC_V1_SPEC.json` (devices 段的 186 个 ref)」⇒ ★**盘上该 JSON 顶层只有 meta / "
    "counts / connections / power_rails / display_select / testpoints / undrawable 七个键, 没有 `devices`** ⇒ 照字面实现找不到"
    "真源 ⇒ ★实际真源 = `HW/netlist_v1_pins.csv` (218 器件)★ ⇒ 本单只订正指针, 不拍板 ★\n"
    "★**④ 「动板那趟收工后重锚」还没进任何清单 (★need `iss289_state_baseline_reanchor_after_board_run`★)**: 29 条登记里只有 "
    "4 条走台账口径, 其余 **25 条写死** ⇒ 落表/动板后必然一批红 ⇒ ★**必须把「收工后同一次重锚 + 新闸跑绿」写成那一趟收工"
    "清单里的强制项** ⇒ 最危险三条: `W11`/`C04` (封装 186 ⇒ 185) · `W09_SAME_PAD_NET` (同号异网 3 ⇒ 0) · `W12`/`C03` "
    "(156 ⇒ 155 或 156) + `W18` (1 ⇒ 156 或 157) ⇒ ★**并写明「不许为让闸绿而把 `C_VBUS_GND` 装回板上」** ★\n"
    "★**⑤ 名额理由**: ISS-289 已由 main 复验落 verified ⇒ hw-lead 名额空出; sw-lead 被 ISS-291 占 (在飞) · mech-lead 被 "
    "ISS-290 占 (在飞) ⇒ ★**本单是此刻唯一能合法派给 hw-lead 的活** ★"
)

NOTE_292 = (
    "2026-11-17 16:0x (cron 775d9893 继续执行后继计划) 新开 ★**依据 = main 15:5x~16:0x 本机实读 "
    "`state/_iss277_build_preflight.py:26/:108/:110` + `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` (盘面 51/40/40 · 18 条) + "
    "`HW/netlist_v1.csv:10/:12` (C_VBUS_GND board=CHG_BOARD) + `HW/SCHEMATIC_V1_SPEC.json` 顶层键盘点 + 交卷单 §B6.4 的 "
    "4 条拍板项 (★P4 = 本单★)★** ★\n"
    "⇒ ★**任务书全文 = `state/dispatch_briefs/ISS-292_hw_preflight_generator_realign.md` (★已过 "
    "`python3 state/check_brief_commands.py --brief-file` ⇒ rc=0★)** ★\n"
    "⇒ ★**口径**: **纯生成器对齐 + 作业包文本订正 · 零写板 (★md5+mtime 双重自证★) · 零落表** ⇒ ★**符合老板 2026-11-17 "
    "00:43「PCB 类先派纯分析/作业包类」纪律** ★\n"
    "⇒ ★**本单不许碰 `HW/check_workpack_state_values.py` (★ISS-289 的闸★)** ★\n"
    "⇒ ★**受保护 5 件本 job 16:0x 实测**: 板 611b869e… (mtime 2026-11-06 07:07:17) · .kicad_pro 3e504d2b… · 网表 "
    "37f62ac3… · 脚表 a4270120… · BOM 5d02bece… ⇒ 零写板 · 零落表 成立 ★"
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

        # ── ISS-289: fixing → verified (main 独立复验) ──
        i289 = by_id.get("ISS-289")
        if i289 is None:
            print("⚠ ISS-289 不存在")
        elif i289.get("status") == "verified":
            print("· ISS-289 已是 verified ⇒ 幂等跳过")
        else:
            i289["status"] = "verified"
            i289["verify_by"] = "main"
            i289["verify_result"] = "pass"
            i289["verify_date"] = TODAY
            i289["fix_ref"] = "HANDOFF/2026-11-17_hw-lead_ISS289_作业包现状值对回盘面.md"
            i289["note"] = (i289.get("note") or "") + "\n\n★★ **main 2026-11-17 16:0x 复验落 verified** ★\n" + VERIFY_289
            print("· ISS-289 fixing → verified (main 独立复验)")

        # ── ISS-292: 新开 (owner=hw-lead) ──
        if "ISS-292" in by_id:
            print("⚠ ISS-292 已存在 ⇒ 幂等跳过")
        else:
            issues.append({
                "id": "ISS-292",
                "title": TITLE_292,
                "severity": "high",
                "source_blocker": None,
                "source_agent": "main",
                "desc": DESC_292,
                "owner": "hw-lead",
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
                "note": NOTE_292,
                "dispatched_at": "",
                "task_brief": brief_text,
            })
            print("· ISS-292 已开 (owner=hw-lead, status=open, due=2026-11-20)")

        shutil.copy2(LOG, BAK)
        tmp = LOG + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)
        os.replace(tmp, LOG)
        fcntl.flock(lk, fcntl.LOCK_UN)
    print("备份: %s" % BAK)


if __name__ == "__main__":
    main()
