#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20260723_0530_main_open_iss352.py —— main 开 ISS-352 (mech-lead · MECH 双口径第 2 批)"""
import os
import shutil
import sys
import time

import yaml

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
LOG = os.path.join(PROJ, "state/issue_log.yaml")
STAMP = time.strftime("%Y%m%d_%H%M")

TITLE = ("★★[★新主线·PCB 线·MECH 域判定脚本迁双口径·第 2 批·零写板] ★★【ISS-345 cont1 (第 1 批 2 脚本) 已由 main "
         "2026-11-23 04:0x 签收 ⇒ 第 2 批 = 交卷页 §B5-2 自己列的那张清单: ① `fit_check_v3_30mm.py` / `fit_check.py` 二选一 "
         "说清 ② `cross_review_check.py` 迁双口径 (默认档逐字节不变) ③ 新建闸 `MECH/check_mech_dual_caliber_gate.py` (含反向用例) "
         "④ `BOARD_GEOM_CALIBER_STATUS.md` scope A/B 追加式订正 ⑤ 漂移闸迁后重跑回填 + 三个既有帧表脚本核对结论】★★ "
         "★**板那一趟开工前还差「MECH 域 8 个判定脚本迁双口径」这一件 ⇒ 本单就是它的下半程**★")

DESC = ("★**main 2026-11-23 05:3x 本机实读 (不抄任何 agent 报告)★** ⇒ ★**① 上游**: ISS-345 cont1 已签收 (★验收线 24 条全绿 + "
        "自测 4/4★) ⇒ 第 1 批读数: 默认档 (F30A 60×30) 迁移前后输出**逐字节相同** (diff 两文件均 0 B ⇒ 判据方向一字未改) + "
        "第二档 B160x100 读数在盘 (每条数都有出处) + selftest 6/6 + compat rc=0 + 漂移闸 107 处/33 文件与迁移前基线完全一致 ⇒ "
        "★**第 2 批的题面直接来自交卷页 §B5-2, 不许扩项**★ ⇒ ★**② 为什么急**: 板那一趟开工前还差「MECH 域 8 个判定脚本迁双口径」"
        "这一件 (★老板那 9 件拍板之外的最后一件内部前置★) ⇒ ★**③ 关键判据 (★不许违反★)**: 默认档输出必须与迁移前**逐字节相同** ⇒ "
        "diff 文件必须是 0 字节 ⇒ ★**「靶更小」不等于「板子更好」**★ ⇒ ★**不许改判据方向或数字, 只许「迁档位表 / 加档位标识」**★ ⇒ "
        "★**④ 第 2 批里最容易出事的一处**: `fit_check_v3_30mm.py` 与 `fit_check.py` 自报作废 ⇒ 必须**说清留谁退谁** ⇒ 不许两个都留也不许都删 ⇒ "
        "★**⑤ 边界**: 零写板 (板 md5 `611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17.362193413` 必须逐字节不变) · "
        "零落表 · 不许改判据方向或数字 · 只写 MECH 域 + 交卷页 + logs/iss352/ · 不写别人的分片 · 零外发 · 零新增拍板项 ★")

BRIEF = (
    "★**题**: ISS-345 cont1 (第 1 批 2 脚本) 已由 main 2026-11-23 04:0x 签收 (★验收线 24 条全绿 + 自测 4/4★) ⇒ ★**第 2 批 = "
    "交卷页 §B5-2 自己列的那张清单 (★题面直接来自那张表·不许扩项★)**★ "
    "★**做 5 件**: ① `MECH/fit_check_v3_30mm.py` 与 `MECH/fit_check.py` 自报作废 ⇒ ★**二选一说清留谁退谁·不许两个都留也不许都删**★ "
    "(★先实读自报状态给机器判定·不许含糊★) ② `MECH/cross_review_check.py` 迁双口径 (★默认档 F30A 输出必须与迁移前逐字节相同 ⇒ "
    "diff 文件 0 字节·第二档 B160x100 有读数且每条数都有出处·三源取值: BOARD_FRAME_CALIBER.md + demo_mainboard_params.json + 板文件实读★) "
    "③ 新建闸 `MECH/check_mech_dual_caliber_gate.py` (★断言: 扫这 8 个脚本每个都含 60×30 与 160×100 两种档位标识 · 默认档 = F30A · "
    "`MECH/hw_cross_review_check.py` md5 仍 = e521387b87b0fcdf9f22d56f14199967 · ★**反向用例必须有**: tmp/ 副本删掉某脚本的 160×100 标识 ⇒ "
    "闸必须判红并点名该脚本 ⇒ 恢复判绿 · `--selftest` 末行 ALL TESTS PASS★) ④ `MECH/BOARD_GEOM_CALIBER_STATUS.md` scope A/B 追加式订正 "
    "(★只许插入·老字一字未删·计数页改完必须重跑生成器验一次★) ⑤ 漂移闸迁后重跑回填 (★命中数必须与迁移前基线一致·零新增·否则当场判红★) + "
    "三个既有帧表脚本逐个给结论 (★不许含糊★) ★**纪律**: 零写板 · 零落表 (不改网表/脚表/BOM/原理图/作业包数值) · ★**不许改判据方向或数字**★ · "
    "只写 MECH 域 + 交卷页 `HANDOFF/2026-11-23_mech-lead_ISS352_MECH双口径第2批.md` (★B0~B7 + 引用 MISS=0 + 板指纹前后双证 + §B6-2 逐条 diff★) + "
    "logs/iss352/ · 不写别人的分片 · ★**零外发**★ · 证据分级必标 · 不替老板拍板 · 不新增拍板项 · 写分片只用 frag_write.py ★**必跑**: "
    "`python3 state/merge.py` (rc=0) && `python3 state/gate_check.py` (★Q1 必须 18/18 · Q7 必须 10/10★) && "
    "`python3 MECH/check_mech_dual_caliber_gate.py --selftest` (末行 ALL TESTS PASS) && `md5sum HW/PCB/demo_mainboard.kicad_pcb` "
    "(必须 611b869e13518c3c023fb178f91a0075) ★ ★**任务书全文**: `state/dispatch_briefs/ISS-352_mech_dual_caliber_batch2.md` "
    "(★check_brief_commands.py --brief-file rc=0★) ★")

NOTE = ("★★2026-11-23 · cron 775d9893 (ARS45 继续执行后继计划) 开单并派出 (★项目总工 main★) ★★ ★**开单依据**: ISS-345 cont1 交卷页 "
        "§B5-2 自列的第 2 批清单 ⇒ main 直接转成派活单 (★题面未扩项★) · ★**判定**: PCB 线 · 纯脚本改造 + 新建机器闸 · 零写板 · 零落表 "
        "(★符合「板只改一次」纪律: 先派纯分析/作业包类★) · ★**它就是「板那一趟开工前还差的那一件」的下半程**★ · 派活时刻 2026-11-23 05:3x · "
        "★**status 落 fixing ⇒ 兄弟 job fb67af40 的 advance.py --json 看不见本单 ⇒ 不会重复派** ★")

ENTRY = {
    "id": "ISS-352",
    "title": TITLE,
    "severity": "high",
    "source_blocker": "ISS-345",
    "source_agent": "main",
    "desc": DESC,
    "owner": "mech-lead",
    "reporter": "main",
    "raised": "2026-11-23",
    "due": "2026-11-25",
    "status": "open",
    "external": "false",
    "task_brief": BRIEF,
    "dispatched_at": None,
    "verify_by": "main",
    "verify_result": None,
    "note": NOTE,
}


def main():
    src = open(LOG, encoding="utf-8").read()
    if "\n- id: ISS-352" in src:
        print("★ISS-352 已在台账 ⇒ 不重复开单")
        return 0
    chunk = yaml.safe_dump([ENTRY], allow_unicode=True, sort_keys=False, width=200)
    if not src.endswith("\n"):
        chunk = "\n" + chunk
    shutil.copy2(LOG, LOG + ".bak_%s_main_open_iss352" % STAMP)
    tmp = LOG + ".tmp_%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(src + chunk)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, LOG)
    d = yaml.safe_load(open(LOG, encoding="utf-8"))
    items = d if isinstance(d, list) else d.get("issues", d)
    if isinstance(items, dict):
        items = list(items.values())
    ids = [i.get("id") for i in items]
    print("台账条数 = %d · ISS-352 在盘 = %s · 零重复 id = %s"
          % (len(ids), "ISS-352" in ids, len(ids) == len(set(ids))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
