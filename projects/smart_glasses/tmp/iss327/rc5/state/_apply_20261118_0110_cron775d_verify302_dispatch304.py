#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
state/_apply_20261118_0110_cron775d_verify302_dispatch304.py
================================================================================
★**cron 775d9893 (ARS45 继续执行后继计划) · 2026-11-18 01:1x · 本机实跑** ★

本脚本做两件事 (★全部在同一个 flock 内原子完成 ⇒ 兄弟 job fb67af40 不会撞车★):

  ① **ISS-302 验签**: `fixing` → `verified` (★verify_by=main = 本 job 的活★)
     ⇒ ★**依据 = main 01:0x 本机实跑, 不抄 agent 报告★**
     ⇒ ★**验签 note 按 MEMORY 新铁律② 写全三样: 交付时读数 + 现在读数 + 归属单★**

  ② **ISS-304 派活标记**: `open` → `fixing` (★先落 fixing 再 spawn ⇒ 兄弟 job 的
     advance.py 看不见 open 窗口 ⇒ 不会重复派同一个 agent★) + 写 dispatch_log

★**边界**: 零写板 · 零落表 · 零改网表/脚表/BOM · 零外发 · 不替老板拍板 · 不自签别的单★
"""
from __future__ import annotations

import fcntl
import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
LOG = os.path.join(HERE, "issue_log.yaml")
DL = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")

TODAY = "2026-11-18"

VERIFY_NOTE_302 = (
    "★**main 2026-11-18 01:1x 验签 (cron 775d9893 本机实跑, 不抄 agent 报告)** ★\n"
    "⇒ ★**交付物验收通过**: 交卷单 `HANDOFF/2026-11-18_hw-lead_ISS302_CSYS落表.md` = **38,212 B** (★骨架 778 B → 填实★) · "
    "★**真判据 `grep -cE \"🔄|待填\"` = 0** ✔ (★注: `state/check_report_placeholders.py` 抓不到 `🔄 待填` 这种形态 ⇒ 真判据必须是那条正则★) · "
    "B1/B2/B3/B4/B5/B6 + §⑦ + 「交卷前必跑」+ 给 main 的 answer 段 = **七块齐全** ★ · "
    "分片 `grep -c iss302 state/fragments/hw.yaml` = **12** (claims 2 / answers 2 / artifact 1 / status delivered·100·绿) ★\n"
    "⇒ ★**落表四条的落点 main 自己核过 (★不抄交卷单★)**: "
    "① 网表 `SYS_CHG`/`C_SYS` 行 dnp = **必装** (★原 DNP★) · value = `20µF X7R 6.3V` ★ · "
    "note 追加式订正在位 (★老字逐字留痕 + PM 老裁决『VSYS 脚不接 (NC)』标已作废 + 换成 TI bq25896 SLUSC76C §7 逐字 "
    "『Connect a 20uF closely to the SYS pin.』★) ★ · "
    "② BOM `HW/BOM_v1.csv` L48 = `C_SYS` · 1 · `20µF X7R 6.3V` · 必装 ✔ · "
    "③ 落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` §19 (L1437 起) + `<!--ISS302_ROWS-->` **5 行六项齐全** (行号/文件名/旧 md5/新 md5/落表时刻/单号) ✔ · "
    "④ 落表脚本 `state/_apply_iss302_csys_landing.py --verify` = **rc=0** (dnp/note/value/老字留痕 4 项全对) ✔\n"
    "⇒ ★**main 独立复跑的闸 (★01:0x 实跑·原样 rc★)**: `HW/check_netlist_selfconsistency.py` **0** · "
    "`HW/check_land_row_anchors.py` **0** (★落表台账锚点链绿 ⇒ 落表没把锚链打断★) · "
    "`HW/check_onepass_preflight_coverage.py` **0** · `SW/tools/check_demo_panel_spec.py` **0** ★\n"
    "⇒ ★**★板零变化 (md5 + mtime 双证)★**: 板 `611b869e13518c3c023fb178f91a0075` · mtime 仍 `2026-11-06 07:07:17.362193413` · "
    "`.kicad_pro` `3e504d2be83152e337949723e909be1b` ⇒ ★**本单零写板成立** ★\n"
    "⇒ ★**★但【验签 ≠ 现在就绿】(★MEMORY 新铁律②: 验签 note 必须同时写「交付时读数 + 现在读数 + 归属单」★)★**:\n"
    "  · 交付时刻 (00:53~00:58 复跑) `state/gate_check.py` rc=1 · ★**Q7 钉板 md5 闸链 8/9** ⇒ 红 = 钉板闸⑥ 作业包现状值闸 (★`HW/check_workpack_state_values.py` V4 4 条红: W10_MD5_NETLIST / W10B_MD5_PINS / W10C_MD5_BOM / C07_B26_MD5_LEDGER★) ⇒ ★**归属 ISS-304 (hw-lead · 本 job 01:1x 已派出)★**\n"
    "  · 交付时刻 `MECH/check_onepass_mech_release.py` rc=1 (★汇总 绿 5 / 红 1★) ⇒ 红的那道 = `MECH/check_onepass_struct_crosscheck.py` N6 (★只认硬基线·不认合法落表跳★) ⇒ ★**归属 ISS-303 (mech-lead · 兄弟 job 01:1x 已派出)★** ⇒ ★**main 01:0x 复跑已转绿 rc=0 (★ISS-303 那侧动的·不是本单★)★**\n"
    "  · ★**结论: ISS-302 本体交付合格 (★落表四件全对 + 零写板 + 台账齐全★) ⇒ 落 verified; 但「板那一趟不许开工」这条结论没解除 ⇒ "
    "★**钉板闸⑥ (ISS-304) 交卷并回绿之前, G1 仍不许投板**★**\n"
    "⇒ ★**不替老板拍板**: 本单只是落表链侧的一条已定动作 (★TI 官网逐字 + 老板 09:49 已拍 A1/A2/A3·V-4 的那批里的一条·不新增裁决★) ★"
)

DISPATCH_NOTE_304 = (
    "★**2026-11-18 01:1x · cron 775d9893 (ARS45 继续执行后继计划) 派出 (★先落 fixing 再 spawn ⇒ 兄弟 job 775d9893/fb67af40 的 "
    "advance.py 看不见 open 窗口 ⇒ 不会重复派同一个 agent★)** ★ ⇒ ★**依据 = main 01:0x 本机实跑 + 00:5x 18 道闸全扫★** ⇒ "
    "`HW/check_workpack_state_values.py` rc=1 · ★**V4 现状值==盘面实测 4 条红**★ (W10_MD5_NETLIST / W10B_MD5_PINS / W10C_MD5_BOM / "
    "C07_B26_MD5_LEDGER · ★实测值 6aee500e / 9174309d / 5b999399 不在 fresh 原句里★) ⇒ `state/gate_check.py` rc=1 · "
    "★**Q7 钉板 md5 闸链 8/9 绿 ⇒ 板那一趟不许开工**★ ⇒ ★**根因 = 两份页面里那 4 条 `fresh` 原句停在 ISS-283 那一跳 "
    "(37f62ac3 / a4270120 / 5d02bce) ⇒ 而 sidecar `state/_iss277_preflight_appendix.md` 里也是同一批旧值**★ ⇒ "
    "★**那 4 条自己的 note 就写着「基线走落表台账为准, 不写死」⇒ 口径早就定过, 只是链没跟上**★ ⇒ "
    "★**不许改闸的判定逻辑 (它是钉板闸⑥) · 不许手改生成器产物 (清单页是 `state/_iss277_build_preflight.py` 的产物) · "
    "不许改 `HW/check_pin_function_labels.py` (ISS-299 重锚成果) · 零写板 · 零落表 · 零外发**★ ★"
    "★**前置**: ISS-302 已于本 job 01:1x 落 verified (★hw-lead 名额释放·这是本单能派出来的原因★) ★"
)


def main() -> int:
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)

        with open(LOG, encoding="utf-8") as f:
            log = yaml.safe_load(f) or {}
        issues = log.get("issues") or []

        # ---- ① ISS-302 验签 (★只在 status=='fixing' 时才签 ⇒ 幂等·兄弟 job 先签了就跳过★) ----
        signed_302 = False
        for it in issues:
            if it.get("id") != "ISS-302":
                continue
            if it.get("status") == "verified":
                print("★ISS-302 已是 verified ⇒ 本 job 跳过 (幂等)")
                break
            if it.get("status") != "fixing":
                print("★ISS-302 status=%s ≠ fixing ⇒ 不签" % it.get("status"))
                break
            it["status"] = "verified"
            it["verify_result"] = "pass"
            it["verify_date"] = TODAY
            it["note"] = (it.get("note") or "") + "\n\n" + VERIFY_NOTE_302
            signed_302 = True
            print("✅ ISS-302 fixing → verified (verify_result=pass, verify_date=%s)" % TODAY)
            break

        # ---- ② ISS-304 派活标记 (★只在 status=='open' 时才标 ⇒ 幂等★) ----
        marked_304 = False
        brief_304 = ""
        for it in issues:
            if it.get("id") != "ISS-304":
                continue
            if it.get("status") != "open":
                print("★ISS-304 status=%s ≠ open ⇒ 不重复派" % it.get("status"))
                break
            it["status"] = "fixing"
            it["dispatched_at"] = TODAY
            it["note"] = (it.get("note") or "") + "\n\n" + DISPATCH_NOTE_304
            brief_304 = it.get("task_brief") or ""
            marked_304 = True
            print("✅ ISS-304 open → fixing (dispatched_at=%s) · task_brief %d B" % (TODAY, len(brief_304)))
            break

        if signed_302 or marked_304:
            tmp = LOG + ".tmp.%d" % os.getpid()
            with open(tmp, "w", encoding="utf-8") as f:
                yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)
            os.replace(tmp, LOG)

        # ---- dispatch_log ----
        if marked_304:
            with open(DL, encoding="utf-8") as f:
                dl = yaml.safe_load(f) or {"dispatches": []}
            dl.setdefault("dispatches", []).append({
                "issue": "ISS-304",
                "agent": "hw-lead",
                "at": TODAY,
                "brief": brief_304[:300],
                "job": "cron 775d9893 (ARS45 继续执行后继计划) · 派出 (★先落 fixing 再 spawn·零写板·零落表·纯文档/闸侧重锚类★)",
            })
            tmp = DL + ".tmp.%d" % os.getpid()
            with open(tmp, "w", encoding="utf-8") as f:
                yaml.safe_dump(dl, f, allow_unicode=True, sort_keys=False, width=200)
            os.replace(tmp, DL)
            print("✅ dispatch_log 已写 ISS-304 → hw-lead")

        fcntl.flock(lk, fcntl.LOCK_UN)

    # 把 brief 全文落到一个临时文件, 供 spawn 时原样引用
    if marked_304 and brief_304:
        out = os.path.join(HERE, "dispatch_briefs", "ISS-304_hw_workpack_state_values_reanchor.md")
        with open(out, "w", encoding="utf-8") as f:
            f.write(brief_304)
        print("✅ brief 全文已落盘 ⇒ %s (%d B)" % (out, len(brief_304)))

    return 0


if __name__ == "__main__":
    sys.exit(main())
