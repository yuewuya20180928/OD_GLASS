#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20261122_2330_cronfb67_open_iss342.py
================================================================================
cron fb67af40 (ARS45 队列自动派活) · 2026-11-22 23:3x
--------------------------------------------------------------------
开单: ISS-342 (mech-lead) = ISS-341 交回 main 的卡点表 C6
      「MECH/BOARD_GEOM_30MM.md 的 RK3576 口径漂移要不要修」

★**为什么直接落 `fixing` 而不是 `open`**:
  ★**兄弟 job (cron 775d9893) 每 30 分钟跑一次, 它也会读 `state/advance.py --json`**
  ★**⇒ 若本单留一个 `open` 窗口 ⇒ 兄弟 job 会把同一条当自己的货派给 mech-lead ⇒ 撞车**
  ★**⇒ 按 ISS-339 的先例 (main 2026-11-22 21:3x 原话: 「status 直接落 fixing ⇒ 兄弟 job 的 advance.py 看不见 open 窗口 ⇒ 不会重复派」) ★**

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
BRIEF = os.path.join(HERE, "dispatch_briefs", "ISS-342_mech_board_geom_stale_chip_caliber.md")
BAK = LOG + ".bak_20261122_2330_cronfb67_open_iss342"

ISS342 = {
    "id": "ISS-342",
    "title": (
        "★★[★新主线·PCB 线·结构侧口径漂移·纯分析+文档订正+机器闸类·零写板] ★★"
        "【C6: `MECH/BOARD_GEOM_30MM.md` 自称「结构侧对 60×30mm 现行板的唯一权威几何口径」"
        "(60×30 / 6 层 / 1.00mm / 主控 RK3576 FCCSP698L), 而现役板 = 160×100mm / 8 铜层 / 1.60mm / 186 封装 / "
        "主控 RK3572-SOM 直插 (承载区 53.80×46.78mm ⇒ 60×30 装不下, 高差 −16.78) ⇒ 该表已被 ISS-341 机器判决判为"
        "「重画一块新板」那一档的口径 ⇒ 它继续自称「唯一权威」= 整条链的静默投毒源 (★主板线 = 绘制 PCB 图, "
        "「板只改一次」那一趟开工前每个 agent 都可能去读它★) ⇒ 交付: ① 漂移清单页 (MECH 域 21 个 RK3576 命中文件逐行定性) "
        "② `MECH/BOARD_GEOM_30MM.md` 表头【追加式】订正 (老字一字不删) ③ 只读漂移检测闸 (含 --selftest) ④ 交卷页 B0~B7 ★★"
    ),
    "severity": "high",
    "source_blocker": "ISS-341",
    "source_agent": "mech-lead",
    "desc": (
        "★**main 2026-11-22 23:3x 本机实读 (不抄任何 agent 报告)★** ⇒ "
        "★**① `MECH/BOARD_GEOM_30MM.md` 第 4 行原文: 「本表是结构侧 (MECH) 对 60×30mm 现行板的唯一权威几何口径」 "
        "⇒ 凡本域其它文档/脚本/分片与本表冲突 ⇒ 以本表为准** ★ (mtime 2026-11-11 21:22 ⇒ 比现役板 11-06 还新 ⇒ "
        "新人先读它必被带偏) ★**② §0 默认口径三条 = 板宽 30 / 板长 60 / 板厚 1.00 (6 层) + 主控 RK3576 (FCCSP698L 17.20×16.10) + 套 A** ★ "
        "★**③ 现役真值 = 160×100mm / 8 铜层 / 1.60mm / 186 封装 / 主控 RK3572-SOM 直插 (J_SOM_P1..P4 承载区 53.80×46.78mm)** ★ "
        "★**④ 漂移范围 = `grep -rln RK3576 MECH/` 实跑 21 个文件 (含 .bak 与 __pycache__, 真要判的是文档与脚本)** ★ "
        "★**⑤ 本单不依赖老板那两问 (第一问 = 台架板/产品内板, 第二问 = RK3572-SOM/RK3576-SoC) ⇒ 「60×30/RK3576 = 现行板框」"
        "这句话无论第一问答哪个都是错的 ⇒ 口径状态声明 + 漂移清单现在就能做, 不许把待拍答案挂成阻塞项** ★"
    ),
    "owner": "mech-lead",
    "reporter": "main",
    "raised": "2026-11-22",
    "due": "2026-11-23",
    "status": "fixing",
    "external": False,
    "need_keys": [
        "iss310_main_board_frame_u1_decision",
        "iss342_board_geom_stale_chip_caliber",
    ],
    "task_brief": "",  # 下面从 brief 文件读
    "dispatched_at": "2026-11-22",
    "verify_by": "main",
    "verify_result": None,
    "note": (
        "★★2026-11-22 23:3x · cron fb67af40 (ARS45 队列自动派活) 开单并派出 (★项目总工 main★) ★★ "
        "★**开单依据 (main 本机实读·不抄任何 agent 报告)★**: ① `python3 state/advance.py --json` ⇒ internal=[] / approvals=[] / waiting=0 / decisions=41 ⇒ "
        "**队列真空** ⇒ 按「开新单」处理 ② ★**来源 = ISS-341 交回 main 的卡点表 C6 (★`HANDOFF/2026-11-22_mech-lead_ISS341_板那一趟画哪块板相容性判定.md` §B5-1 第 6 行: "
        "「结构侧权威表 `MECH/BOARD_GEOM_30MM.md` 的 RK3576 口径漂移要不要修」· 本单只登记·不改 · 需要谁回答 = mech-lead (自己) · 下一单★)★** "
        "③ ★**mech-lead 名额已释放** (ISS-341 于 22:36~23:25 由 main 签收 fixing→verified) ★ "
        "★**④ ★status 直接落 `fixing` (不经过 `open` 窗口) ⇒ 兄弟 job (cron 775d9893) 的 `advance.py --json` 看不见本单 ⇒ 不会重复派 mech-lead★** ★ "
        "★**⑤ 任务书 = `state/dispatch_briefs/ISS-342_mech_board_geom_stale_chip_caliber.md` (★`check_brief_commands.py --brief-file` rc=0★) ★**"
    ),
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
    if any(i.get("id") == "ISS-342" for i in issues):
        print("★ISS-342 已存在 ⇒ 幂等退出 (不重复开单)")
        return 0
    brief = open(BRIEF, encoding="utf-8").read()
    ISS342["task_brief"] = brief
    issues.append(ISS342)
    doc["issues"] = issues
    out = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=100)
    if not os.path.exists(BAK):
        shutil.copy2(LOG, BAK)
        print("★备份 ->", os.path.basename(BAK))
    atomic_write(LOG, out)
    # 自检: 回读 + 零重复 id
    doc2 = yaml.safe_load(open(LOG, encoding="utf-8").read())
    ids = [i.get("id") for i in doc2["issues"]]
    dup = {x for x in ids if ids.count(x) > 1}
    hit = [i for i in doc2["issues"] if i.get("id") == "ISS-342"]
    print("★issues 条数 =", len(ids), "· 重复 id =", sorted(dup) or "无")
    print("★ISS-342 落表 =", bool(hit), "· status =", hit[0].get("status") if hit else None,
          "· owner =", hit[0].get("owner") if hit else None,
          "· task_brief =", len(hit[0].get("task_brief", "")) if hit else 0, "chars")
    return 0 if (hit and not dup) else 1


if __name__ == "__main__":
    sys.exit(main())
