#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 3 份派活任务书 (2026-11-15 20:5x, main) —— brief 原文逐字取自 advance.py --json

★**为什么用文件而不是把全文塞进 spawn 参数** ★:
· brief 原文 (ISS-205 4282 B / ISS-195 2142 B / ISS-206 6485 B) 手工转录必错 ⇒ ★**逐字从 advance.py 的 JSON 取, 零转录★**
· 任务书同时当【派活留档】(★可被下一个 cron / 老板复核★)
★**边界**: 不改 issue_log / 分片 / 项目文件; 只在 state/tasks/ 下新建 3 个 .md
"""
from __future__ import annotations

import json
import os
import subprocess

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
OUT = os.path.join(PROJ, "state", "tasks")
os.makedirs(OUT, exist_ok=True)

# ★**注意**: 本脚本跑的时候这 3 条已经被 `--apply` 标成 fixing ⇒ advance.py 的 A 段会变成空
# ⇒ ★**brief 从【标 fixing 之前】的那份 JSON 快照取** (★state/tasks/advance_plan_20261115.json★)
SNAP = os.path.join(OUT, "advance_plan_20261115.json")
plan = json.load(open(SNAP, encoding="utf-8"))
briefs = {a["issue"]: a for a in plan["internal"]}

ROLE = {"hw-lead": "硬件总工", "sw-lead": "软件总工", "mech-lead": "结构总工"}

FACTS = {
    "ISS-195": """★★**本单的真实状态 (★main 2026-11-15 20:5x 逐个文件实测, 不是推测★)** ★★:
★**① 上一次派活 (2026-11-12 03:2x) 的会话已死 (status=failed), 交卷没人落账 ⇒ 停在 `fixing` 3.5 天 (★同病第 11~13 次复发★)**
★**② 半交卷 —— 产物已经在盘上, 别重做**:
  · ✅ `HW/iss121_mic_magnet_check.py` mtime **2026-11-12 03:43:43** (★第 171~173 行已写「PIN-SET-2 孔位 = 现行 60×30 板 /
    套 A (ISS-194 仲裁定版)」★ · 第 189 行「J_CHG 座体 keep-out (现行 60×30 板)」★)
  · ✅ `HW/iss121_mic_magnet_check.json` mtime **2026-11-12 03:43:07**
★**③ 你这单真正缺的 (★只做这些★)**:
  · ❌ **`HW/ISS121_MIC_MAGNET_POSITION.md` mtime 2026-11-01 23:50 = 一字未动 ⇒ 三处 15mm 老口径还在** ⇒ 本单的三处里【文档那处】没做
  · ❌ 没有交卷报告 (`HANDOFF/` 里没有 ISS-195 的单子) ⇒ ❌ `state/fragments/hw.yaml` 没登记本单
  · ❌ 没有跑三闸自证 / 没写 PASS-FAIL-余量数字的结论段
★**④ 你要交的形状**: ★**脚本侧已按套A 改过 ⇒ 你要做的是【核对脚本算出来的数字 + 把结论写进 .md + 交卷 + 登记】** ★
★**⑤ 一条硬要求**: ★**你自己重跑一遍 `python3 HW/iss121_mic_magnet_check.py` 看它现在的读数 (★别照抄 main 的转述★)**,
★**读数若与脚本里写的不一致 ⇒ 以你实跑的为准, 并在交卷报告里点出来** ★""",

    "ISS-205": """★★**本单的真实状态 (★main 2026-11-15 20:5x 逐个文件实测, 不是推测★)** ★★:
★**① 上一次派活 (2026-11-12 03:2x) 的会话已死 (status=failed), 交卷没人落账 ⇒ 停在 `fixing` 3.5 天 (★同病第 11~13 次复发★)**
★**② 半交卷 —— 核心产出已经在盘上, 别重做**:
  · ✅ `state/gen_kicad_sch.py` mtime **2026-11-12 03:36:22** (★第 280~287 行 = 位号加 `_1` 后缀的生成逻辑★ ·
    第 553 行 = 图↔表 ref 的精确映射★)
  · ✅ `HW/PCB/demo_mainboard.kicad_sch` + `demo_mainboard_p1..p10.kicad_sch` **11 个文件全部 mtime 2026-11-12 03:36**
  · ✅ ★**实测图上位号**: `(property "Reference" ...)` 共 **218** 个, 其中带 `_1` 后缀 **187** 个
  · ✅ ★**实测 sheet_instances**: 根页 + 10 个子页 **11/11 都有** (★原缺件已补上★)
★**③ 你这单真正缺的 (★只做这些★)**:
  · ❌ **问号归零没有实测**: 投产包 BOM `HW/PCB/production/doc/demo_mainboard-kicad-bom.xml` 仍是 11-11 17:25 的旧件,
    带 `?` 的行 **186** ⇒ ★**这是 brief ⑦ 说的「投产包变旧 = 预期中间态」, 不是你没做完★** ⇒
    ★**你要做的是: 重新导出一次 BOM 并实测「带 `?` 的行数 = 0」, 把那个数字贴进交卷报告** ★
  · ❌ 三条闸 (ERC / pinfull / loadable) 的实测输出没贴
  · ❌ 受保护文件 md5 的实测对照没贴 (板 / 网表 / 脚表 / `.kicad_pro`)
  · ❌ 没有交卷报告 ⇒ ❌ `state/fragments/sw.yaml` 没登记本单
★**④ 一条硬要求**: ★**你必须自己跑一遍导出/校验, 不许拿 main 的转述当结论** ★""",

    "ISS-206": """★★**本单的真实状态 (★main 2026-11-15 20:5x 逐个文件实测, 不是推测★)** ★★:
★**① 上一次派活 (2026-11-12 03:2x) 的会话已死 (status=failed), 交卷没人落账 ⇒ 停在 `fixing` 3.5 天 (★同病第 11~13 次复发★)**
★**② 骨架级 0 产出 —— 上一次一个字都没动**:
  · ❌ `state/fragments/mech.yaml` mtime **2026-11-12 02:46:55** (★**早于** 03:2x 的派活时间 ⇒ 本单没写过它★)
  · ❌ ★**实测第 3 套 pin map 还在**: `state/fragments/mech.yaml` 第 1362 行仍写着「§9 `mech_j_chg_pins` 行仍写
    value = `8p@0.5mm`」⇒ ★**本单一个字都没动**★
★**③ ⇒ 你这单是从头做, 但【裁决已裁完】**: ★**brief 里【main 裁决】段就是裁完的结果 ⇒ 你不用再等下一轮, 照做即可** ★
★**④ 硬要求**: ★**你自己按网表逐脚复算一遍 (★别照抄 main 的转述★)** ⇒ 与 brief 里的真源不一致 ⇒ 以你实算的为准,
★并在交卷报告里点出来** ★""",
}

DISC = """★**纪律 (★一条都不许破★)** ★★:
① ★**写分片必须走 `state/frag_write.py`** (★禁止 `open(p,"w")`★)
② ★**只写本单允许的文件, 不碰别人的分片** (★hw.yaml / sw.yaml / mech.yaml 各归各的★)
③ ★**证据分级必标**: `[官网]` / `[实测]` / `[媒体]` / `[推算]` / `[0数据]` ⇒ ★**查不到就写 `[0数据]` + 降级方案, 不许编** ★
④ ★**不许外发任何邮件 / 询价 / 问询 / 采购** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★)
   ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ⇒ ★**没有「批一句可以发」这个选项** ★
⑤ ★**交卷前跑**: `python3 state/merge.py` (★rc 必须 0★) && `python3 state/gate_check.py` (★【Q1】必须 18/18★)
   ⇒ ★**把输出原样贴进回复** ★
⑥ ★**不许改 `state/issue_log.yaml` 的 status** (★那是 main 的活★) · ★**不许改 `PROJECT_TRACKER.md` §0 锁死表** ★
⑦ ★**主线口径 (★老板 2026-11-11 10:07★)**: 当前主线 = ★**硬件原理图 demo 绘制** ★ ⇒
   ★**不许碰 PCB 布线 / 布局 / 逃线 / 层数** ★
⑧ ★**不许整文件读大文件** (★只许 `grep` / `sed -n` 取你要改的那几行★) ★
⑨ ★**交卷 ≤ 25 行** (★结论先行 + 逐条复现命令输出 + 缺口清单★) ★
"""

for iid in ("ISS-205", "ISS-195", "ISS-206"):
    a = briefs[iid]
    agent = a["agent"]
    head = (
        "【项目总工派活 · 后继计划 · 闭环 %s】你是%s (agent=`%s`)。\n\n"
        "★★**第一步 (★不许跳过★)**: ★**本文件往下第 ★★`任务书原文 (advance.py 给的 brief 全文)`★★ 那一段, "
        "就是 `state/advance.py --json` 给你这单的 brief 原文, ★**一字未改★** ⇒ ★**照它做, 不要自己另写一套** ★★\n\n"
        "%s\n\n%s\n\n"
        "================== `任务书原文 (advance.py 给的 brief 全文)` ==================\n\n"
        "%s\n"
        % (iid, ROLE[agent], agent, FACTS[iid], DISC, a["brief"])
    )
    p = os.path.join(OUT, "advance_%s.md" % iid.lower().replace("iss-", "iss"))
    with open(p, "w", encoding="utf-8") as f:
        f.write(head)
    print("★wrote %s (%d B)" % (p, os.path.getsize(p)))
