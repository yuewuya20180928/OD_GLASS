#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20261123_0010_cronfb67_open_iss343_344_345.py
================================================================================
cron fb67af40 (ARS45 队列自动派活) · 2026-11-23 00:1x
--------------------------------------------------------------------
开单 3 条 (ISS-343 hw-lead / ISS-344 sw-lead / ISS-345 mech-lead)

★**为什么直接落 `fixing` 而不是 `open`**:
  ★**兄弟 job (cron 775d9893 「继续执行后继计划」) 每 30 分钟跑一次, 它也会读
  ★`state/advance.py --json`** ⇒ ★**若本单留一个 `open` 窗口 ⇒ 兄弟 job 会把
  ★同一条当自己的货派给同一个 agent ⇒ 撞车 (★两个 agent 写会话同时写一个分片 ⇒
  ★分片合并丢 12%~38%★)** ⇒ ★**本单直接落 `fixing` ⇒ 兄弟 job 的
  ★`advance.py --json` 看不见这三条 ⇒ 不会重复派**
  ★ (★与 2026-11-22 23:30 开 ISS-342 的同一手法★)

★**三条的来源 (★都是 main 自己已裁 / 已签收的结论, 不是本 job 造的口径★)**:
  ★ISS-343 (hw-lead)  ← main 2026-11-17 18:45 拍死的 E-1 排针 land 项
  ★                     (pm.yaml `main_e1_e2_board_side_rulings_20261117`)
  ★                     + 全集页 32 条里【没有这一项】的实测漏项
  ★ISS-344 (sw-lead)  ← main 2026-11-22 20:5x 的 24 条零铜网分级定裁
  ★                     (pm.yaml `iss334_need4b_zero_copper_net_triage`
  ★                     + iss338_need_* 三条)
  ★                     + SW 页 §3 表把 6 条必需网判 NC 的实测分叉
  ★ISS-345 (mech-lead)← main 2026-11-23 00:1x 裁「MECH 8 脚本迁双口径」
  ★                     (pm.yaml `iss342_geom_caliber_downstream_audit`)

★**原子写 + 带 .bak + 幂等** ★
"""
from __future__ import annotations

import datetime as dt
import os
import shutil
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
LOG = os.path.join(HERE, "issue_log.yaml")
BAK = LOG + ".bak_20261123_0010_cronfb67_open_iss343_344_345"
BRIEF_DIR = os.path.join(HERE, "dispatch_briefs")

TODAY = "2026-11-23"

SPECS = [
    ("ISS-343", "hw-lead", "ISS-343_hw_preflight_排针land漏项_补齐.md"),
    ("ISS-344", "sw-lead", "ISS-344_sw_零铜网分级_口径对账.md"),
    ("ISS-345", "mech-lead", "ISS-345_mech_8脚本迁双口径.md"),
]

META = {
    "ISS-343": {
        "severity": "high",
        "source_blocker": "ISS-290",
        "title": (
            "★★[★新主线·PCB 线·板侧项全集漏项·纯分析+文档订正+机器闸·零写板] ★★"
            "【E-1 排针 land 0.50→1.27mm 补进「板侧项全集」页 + 作业包两处过期待拍状态订正 "
            "+ 覆盖度闸补「作业包板改清单逐项对照」判据】★★ "
            "★**E-1 = main 2026-11-17 18:45 已拍死 (归 main 不归老板) = 按 1.27mm 排针定 + 板 land 并进那一趟重画; "
            "但 `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 的 32 条板侧项里【没有这一条】(main 实跑: 1.27/pitch/排针/E-1/0.50 五个 marker 全不在 items 块里) "
            "⇒ 覆盖度闸 P4 只查「位号在不在清单里」⇒ 这类【同一 J_DEBUG/J_UART 的 land pitch 改】天生查不出 ⇒ P4 绿灯 = 假绿 "
            "⇒ 那一趟做完实物排针照样装不进 ⇒ 补做 = 板 md5 变第二次 = 留证链/Gerber/投产包/盖章全白跑一遍**★"
        ),
        "desc": (
            "★**main 本机实读 + 实跑 (不抄任何 agent 报告)★** ⇒ "
            "★**① E-1 已由 main 2026-11-17 18:45 拍死** (pm.yaml `main_e1_e2_board_side_rulings_20261117` 的 `decision` 逐字: "
            "「E-1 = 按 1.27mm 排针定 + 板 land 并进那一趟重画」+ 板改清单 7 项里含「E-1 排针 land 重画」) ★ "
            "★**② 作业包 §0.2 ③ 已写它** (HW/PCB/BOARD_ONEPASS_WORKPACKET.md:47) ★ "
            "★**③ 全集页 32 条里没有它** (main 实跑: items 块里 1.27/pitch/排针/E-1/0.50 五个 marker 全不在) ★ "
            "★**④ 覆盖度闸 P4 抓不到** (MARKERS 是位号级; J_DEBUG/J_UART 已被 B15/B16 命中 ⇒ 灯绿假绿) ★ "
            "★**⑤ 同一缺陷在作业包里的第二个影子**: :332 / :348 两处仍写「待 main→老板 (E-1 三选一)」+「待拍 (会改板)」 "
            "⇒ 而 main 已拍死 ⇒ 过期状态, 会把已决项重新挂回老板拍板面 ★ "
            "★**⑥ 板面实测**: J_DEBUG 板读 pitch 0.50/4脚/铜箔 X 142.0625..143.8375×Y 56.1500..57.0500; "
            "J_UART 板读 pitch 0.50/2脚/铜箔 X 18.5025..19.2775×Y 68.1500..69.0500; BOM/网表写 1.27mm ⇒ Δ pitch 0.77 ⇒ 实物落不进 ★ "
            "★**⑦ 结构侧后果 MECH 已交付** (作业包 :326/:342): J_DEBUG 改 land ⇒ 清空区 X 1.7750⇒4.0850, 单边间隙 4.2125⇒3.0575 "
            "(最坏 2.7575 ≥ CRIT 0.60), 开口 X/Y 一字不变, 三档 h 全过; J_UART 改 land ⇒ 结构侧零连带改动 ★ "
            "★**⑧ 本条不依赖老板拍板** ⇒ E-1 是【已由 main 拍死的规格事实】, 现在就能做 (只做清单补齐+状态订正+机器闸, 不动板) ★"
        ),
        "need_keys": ["main_e1_e2_board_side_rulings_20261117"],
    },
    "ISS-344": {
        "severity": "high",
        "source_blocker": "ISS-338",
        "title": (
            "★★[★新主线·PCB 线·固件侧分级口径对账·纯分析+文档订正+机器闸·零写板] ★★"
            "【ISS-338 §3 表的 6 条「NC (不连)」与 main 2026-11-22 20:5x 终裁逐条对账 + 订正 SW 页分级陈述 "
            "+ 建「SW 分级 vs 板侧真值不许分叉」机器闸】★★ "
            "★**终裁 = 必需 23 (含 8 条单端脚) / 可悬空 1 (FSIN_OUT) / 待定 0; 而 SW 页 §3 表仍把 JTAG_TDI / SPI_MISO_BOOT / "
            "SPI_MOSI_BOOT / SPI_SCLK_BOOT / UART_RX / USB_CC2 六条判成「NC (不连)」(main 实跑判定) ⇒ 这 6 条会带着矛盾进板那一趟**★"
        ),
        "desc": (
            "★**main 本机实读 + 实跑 (不抄任何 agent 报告)★** ⇒ "
            "★**① ISS-338 §B5-6 自己把这条挂给 main**: 「9 条的固件侧降级声明由谁落笔 | main (派给 sw-lead 下一单) | "
            "本单【不许改固件本体】⇒ §3 只写清「改哪一行」, 一行未动 | 下一单照 §3 的行号清单改」 ⇒ 那本下一单一直在等 main 先裁分级 ★ "
            "★**② main 已于 2026-11-22 20:5x 逐条裁完** (pm.yaml answers): iss338_need_jtag_group_decision = 「裁 JTAG 整组保留, 不裁 TDI ⇒ JTAG_TDI 判【必需】」; "
            "iss338_need_boot_storage_answer = 「3 条 SPI_*_BOOT 判【必需】·板侧【不许】标 no-connect」(理由: J_BOOT1 焊盘位已在板 ⇒ 布线保留成本≈0); "
            "iss338_need_usbif_cc1_cc2_rule = 「USB_CC2 判【必需】·板侧不许标 NC」([官网] USB Type-C 插座端双路 Rd); "
            "iss334_need4b_zero_copper_net_triage = 分级定稿 A 必需 23 (15 差分腿 + 8 单端脚) / B 可悬空 1 (FSIN_OUT, 条件: 板那一趟新基线上仍零铜才允许标 NC, 现在只定口径不动手) ★ "
            "★**③ 机器真值 = HW/check_s8_target_list.py**: REQUIRED_SINGLE = [CAM_RESET_N, LED_G_D, USB_CC2, JTAG_TDI, UART_RX, SPI_SCLK_BOOT, SPI_MOSI_BOOT, SPI_MISO_BOOT], "
            "FLOAT_OK = [FSIN_OUT], EXPECT_REQUIRED=23 / EXPECT_FLOAT=1 / EXPECT_TBD=0 ⇒ main 实跑该闸 rc=0 且「分级自检 一致 ✔」★ "
            "★**④ main 实跑 SW 页 §3 表逐行解析** ⇒ 判 NC 的 7 条 = FSIN_OUT / JTAG_TDI / SPI_MISO_BOOT / SPI_MOSI_BOOT / SPI_SCLK_BOOT / UART_RX / USB_CC2 "
            "⇒ 与终裁冲突的 6 条 = JTAG_TDI / SPI_*_BOOT ×3 / UART_RX / USB_CC2; 一致的只有 FSIN_OUT (且终裁带条件) ★ "
            "★**⑤ 同一份文件里 §0/§2/§5 还有多处旧分级陈述** (第 6/12/15/24~25/235 行附近) ⇒ 只改 §3 表会留下自相矛盾 ★ "
            "★**⑥ 每条冲突都踩一个具体的坑**: JTAG_TDI 标 NC ⇒ JTAG 四线缺一 ⇒ 调试口成摆设 (终裁已裁「整组保留」); "
            "SPI_*_BOOT 标 NC ⇒ 将来老板拍外挂 SPI-NOR ⇒ 板必须重出 ⇒ 破「板只改一次」; UART_RX 标 NC ⇒ main 明确不采信 (调试口布线保留成本≈0); "
            "USB_CC2 标 NC ⇒ 违 USB-IF 双路 Rd 条款 ★ "
            "★**⑦ 本条不依赖老板拍板** ⇒ 这 6 条分级 main 已逐条裁完 (机制地界·不占老板拍板面) ⇒ 现在就能做 (只对账+订正+机器闸, 不动固件本体不动板) ★"
        ),
        "need_keys": [
            "iss338_need_jtag_group_decision",
            "iss338_need_boot_storage_answer",
            "iss338_need_usbif_cc1_cc2_rule",
            "iss334_need4b_zero_copper_net_triage",
        ],
    },
    "ISS-345": {
        "severity": "high",
        "source_blocker": "ISS-342",
        "title": (
            "★★[★新主线·PCB 线·MECH 域判据迁双口径·纯脚本改造+文档订正+机器闸·零写板] ★★"
            "【8 个 MECH 判定脚本迁【双口径】(60×30/RK3576 与 160×100/RK3572 两档都留, 默认档保持 60×30 不动) "
            "+ 迁完 scope A/B 真数重读并追加式订正清单页 + 建「单口径脚本进不了板那一趟」机器闸】★★ "
            "★**main 2026-11-23 00:1x 已裁「迁, 但迁法必须是双口径, 不许删 60×30 档, 默认档由 U-1 定, 必须赶在板那一趟开工前」; "
            "而现在 8 个脚本里有 5 个只认 60×30 一档 (main 实读: pinset2_mech_check / skeleton_section_check / fit_check_v3_30mm / fit_check / cross_review_check 的 160×100 命中全为 0)**★"
        ),
        "desc": (
            "★**main 本机实读 + 实跑 (不抄任何 agent 报告)★** ⇒ "
            "★**① main 2026-11-23 00:1x 裁决原文** (pm.yaml `iss342_geom_caliber_downstream_audit`): 「① 下游 8 个脚本迁不迁? ⇒ 迁 ... "
            "⇒ 但迁法必须是【双口径】: 每个脚本同时支持 60×30/RK3576 与 160×100/RK3572 两档 (默认档由 U-1 定) ⇒ 不许把 60×30 档删掉」★ "
            "★**② 时限**: 「必须赶在板那一趟开工前 (板那一趟里不许临时改脚本——判据在板那一趟期间必须冻结)」★ "
            "★**③ 为什么不能单档化**: 「若现在就把脚本改成 160×100 单档, 老板一旦拍『画产品内板 60×30』, 脚本就又得改一遍 ⇒ 判据就变了 ⇒ "
            "板那一趟的读数全部作废 ⇒ 直接违『板只改一次』⇒ 双口径一次做完, 老板拍完只切默认档, 不动判据本体」★ "
            "★**④ 现状 (main 实读每个脚本的常量定义)**: "
            "pinset2_mech_check.py:61-62 (PCB_L=60.00/PCB_W=30.00) · skeleton_section_check.py:53-55 (60.00/30.00/1.00) · "
            "fit_check_v3_30mm.py:4/11/89/105/303 (全文按 30mm/RK3576 基线) · fit_check.py (★自己第 6 行写着「基线已作废·现行版是 fit_check_v3_30mm.py」★) · "
            "cross_review_check.py:26-29/68 (board_w=30.0) ⇒ 这 5 个 grep B160x100 全 0 命中; "
            "而 board_frame_feasibility.py:100-130 / board_port_opening_s6_check.py:389-395 / jd_y0_feasibility.py:166-182 【已有 FRAMES 三档表】★ "
            "★**⑤ 下游消费者 (改脚本会连带影响这些闸的读数)**: check_board_frame_candidate_compat_gate.py:902-903 (调 board_frame_feasibility + pinset2_mech_check) · "
            "check_board_frame_coords.py:84 (S6_PATH → board_port_opening_s6_check) · check_onepass_mech_release.py:59/69 (跑 board_port_opening_s6_check) · "
            "check_demo_struct_truth.py:165 + check_hinge_fpc_truth.py (读 hw_cross_review_check.py — ★另一个文件, 被 md5 钉住 e521387b87b0fcdf9f22d56f14199967, 不许碰★)· "
            "check_board_geom_caliber_drift.py (ISS-342 建的漂移闸, 扫 fit_check_v3_30mm 等 ⇒ 迁完命中数必变) ★ "
            "★**⑥ 漂移闸当前读数 (main 实跑)**: 裸跑 rc=2 (有漂移=预期) 末行「[DRIFT] 未声明口径漂移: 107 处 / 33 个文件」; --selftest rc=0 末行 ALL TESTS PASS (6 用例) ★ "
            "★**⑦ 计数口径老坑 (main 00:1x 原文)**: 「扫描命中数会被【扫描器自己】污染」+「__pycache__ 混进扫描口径本项目已踩两次」⇒ 迁完必须【重读】计数, 不许沿用 00:1x 那组 (24/5/19 · 107 处 33 文件), 且扫描口径要显式排除 .pyc + .bak ★ "
            "★**⑧ 本条不依赖老板拍板** ⇒ 「迁」与「迁法=双口径」main 已裁完; 默认档留哪个由 U-1 定, 但两档都备好现在就能做 ★"
        ),
        "need_keys": ["iss342_geom_caliber_downstream_audit"],
    },
}


def atomic_write(path: str, text: str) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def main() -> int:
    doc = yaml.safe_load(open(LOG, encoding="utf-8").read()) or {}
    issues = doc.get("issues") or []
    existing = {i.get("id") for i in issues}

    added = []
    for iid, owner, brief_name in SPECS:
        if iid in existing:
            print("★%s 已存在 ⇒ 跳过" % iid)
            continue
        meta = META[iid]
        brief_path = os.path.join(BRIEF_DIR, brief_name)
        brief = open(brief_path, encoding="utf-8").read()
        issues.append({
            "id": iid,
            "title": meta["title"],
            "severity": meta["severity"],
            "source_blocker": meta["source_blocker"],
            "source_agent": "main",
            "desc": meta["desc"],
            "owner": owner,
            "reporter": "main",
            "raised": TODAY,
            "due": "2026-11-24",
            "status": "fixing",
            "external": False,
            "need_keys": meta["need_keys"],
            "task_brief": brief,
            "dispatched_at": TODAY,
            "verify_by": "main",
            "verify_result": None,
            "note": (
                "★★%s · cron fb67af40 (ARS45 队列自动派活) 开单并派出 (★项目总工 main★) ★★ "
                "★**开单依据**: advance.py --json 实读 internal=[] / approvals=[] / waiting=0 (★队列排空: 337 条里 open 16 条全是老板拍板面, "
                "hw-lead/sw-lead/mech-lead 名下 open=0★) ⇒ 按「开新单」处理; "
                "★**来源 = main 自己已裁/已签收的结论** (★不是本 job 造的口径★): %s ★ "
                "★**★status 直接落 `fixing` (不经过 `open` 窗口) ⇒ 兄弟 job (cron 775d9893) 的 `advance.py --json` 看不见本单 ⇒ 不会重复派同一个 agent** ★★ "
                "★**任务书全文**: `state/dispatch_briefs/%s` (★check_brief_commands.py --brief-file rc=0★) ★"
                % (TODAY, meta["source_blocker"], brief_name)
            ),
        })
        added.append(iid)

    doc["issues"] = issues
    out = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=100)
    if not os.path.exists(BAK):
        shutil.copy2(LOG, BAK)
        print("★备份 ->", os.path.basename(BAK))
    atomic_write(LOG, out)

    doc2 = yaml.safe_load(open(LOG, encoding="utf-8").read())
    ids = [i.get("id") for i in doc2["issues"]]
    dup = sorted({x for x in ids if ids.count(x) > 1})
    print("★issues 条数 =", len(ids), "· 重复 id =", dup or "无")
    for iid in SPECS:
        hit = [i for i in doc2["issues"] if i.get("id") == iid]
        if hit:
            h = hit[0]
            print("★%s status=%s owner=%s brief=%d chars verify_by=%s"
                  % (iid, h.get("status"), h.get("owner"),
                     len(h.get("task_brief") or ""), h.get("verify_by")))
    return 0 if not dup else 1


if __name__ == "__main__":
    sys.exit(main())
