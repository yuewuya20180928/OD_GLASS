#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""追加式 · DECISION_INDEX_2026-11-18.md ← §K (r72 · 2026-11-18 15:2x)

★**只追加, 老字一个字不删不改** ★
★**目的**: ★**把本 job (cron 775d9893) 15:2x 这一轮实跑的读数摆到老板台面上** ★
   —— ★**不新增待拍项 / 不改任何一条建议默认值 / 不替老板拍任何一条** ★
★**纪律**: ★**零写板 · 零落表 · 零改闸 · 零改 `state/issue_log.yaml` (★兄弟 job fb67af40 正在签 ISS-323/324·不抢写★) · 零改别的 agent 的分片** ★
"""
import os
import shutil

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
PAGE = os.path.join(PROJ, "DECISION_INDEX_2026-11-18.md")
BAK = PAGE + ".bak_20261118_1528_r72"

SECTION = r"""

## §K · ★★【r72 · 2026-11-18 15:2x · 追加式】★★ · ★★**本 job (cron 775d9893) 15:2x 这一轮的实跑读数 (★拍板面一条未动 + 队列归属说死 + 门禁原样 rc★)** ★★

> ★**追加时刻**: 2026-11-18 15:2x~15:3x · ★**追加人**: 项目总工 (moli) · cron `775d9893`
> ★**依据**: ★**本机实跑 `state/advance.py --json` / `state/merge.py` / `state/gate_check.py` / `state/issue_check.py` / `state/stage_gate.py` / `state/daily_check.py` / `state/gen_progress_snapshot.py` + `sessions_list` + `md5sum`/`stat` (★全部 15:2x~15:3x 本机实读, 原始输出落在 `/tmp/ars45_step5_1524.log`★) ★
> ★**本节追加时 §A~§J 的老字一个字未删未改** ★
> ★**性质**: ★**只加读数与事实 · 不新增待拍项 · 不改任何一条建议默认值 · 不替老板拍任何一条** ★

### ★K-1 · 拍板面复核 (★15:2x 本机实跑 `advance.py --json`★)

| 段 | 14:3x (§J-1) | ★**15:2x 本轮复读** ★ | 结论 |
|---|---|---|---|
| internal (A 段可派) | 0 | ★**0** ★ | ⇒ ★**三个总工各 1 条 `fixing` 占位 (ISS-325 / ISS-326 / ISS-327) ⇒ 本 job 派 0 条 (★不重复派·见 §K-2★)** ★ |
| approvals (B 段外发草稿) | 0 | ★**0** ★ | ⇒ ★**与老板 2026-11-12 02:02「不再发信, 全靠自己查资料」口径一致 (★外发政策: 一律不发·缺口自己上网查 + 标证据等级★)** ★ |
| decisions (C 段待拍) | 40 | ★**40** ★ | ⇒ ★**逐条同 key ⇒ §A~§J 的拍板面仍然有效, 无新增无减少 ⇒ 40 条待拍板项一条未动** ★ |
| waiting (D 段纯等待) | 0 | ★**0** ★ | — |

★**今日到期 (剩 0 天) 仍为 3 条** (★只提醒·不代拍★): ★`iss324_d_led_g_placement_decision` (★`D_LED_G` 落位·建议默认 = 假设 B「无光孔·位置不动·零板面动作」★) · ★`iss206_mech_claim_mainboard_len_carrier_direct_scheme_choice` (★SoM 载板形态★) · ★`boss_dled_g_expose_decision_20261117` (★`D_LED_G` 要不要对外暴露·即「板那一趟」第二个阻塞项★) ★

### ★K-2 · ★★【队列归属】本 job 派 0 条 —— 原因说死, 免得老板以为没人干活 ★★

★**`advance.py` 的 internal 段为空 = 三条 `fixing` 占位把队列占满了 (★一条 `fixing` = 已被兄弟 job `fb67af40` 派出去、正在跑★)**:

| issue | owner | 本 job 15:2x 实读状态 | 备注 |
|---|---|---|---|
| ★**ISS-325** (★S8 左上布局沙盒预演·零写板★) | hw-lead | ★**会话被掐** ★ (★`agent:hw-lead:subagent:0482dd39…` · status=timeout · abortedLastRun=true · runtimeMs ≈ 418s · 15:19 结束★) ⇒ ★**hw-lead 现空闲** ★ | ★**重派归兄弟 job `fb67af40` (★它持队列·本 job 不抢·一个 agent 同时只能有一个写会话★)** ★ |
| ★**ISS-326** (★S1 改名 MECH 侧安全性体检·零写板★) | mech-lead | ★**在跑** ★ (★status=running·runtimeMs ≈ 1,993s★) | — |
| ★**ISS-327** (★改名后 SW 闸链复活验证·零写板★) | sw-lead | ★**在跑** ★ (★status=running·runtimeMs ≈ 547s★) | — |

★**⇒ 本 job (cron 775d9893) 本轮派 0 条, 跳过 0 条 (★internal 段本来就空·无「派不动」的情况★)** ★
★**⇒ ★★板面双证 (★本 job 15:2x `md5sum` + `stat` 实读★)★★**: ★板 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413` ⇒ ★**逐字节未变 (12 天零变化)** ★ ⇒ ★**G1 仍开, 不许投板** ★

### ★K-3 · 本轮门禁读数 (★15:2x~15:3x 本机实跑·原样 rc★)

| 项 | rc | 读数 |
|---|---|---|
| `merge.py` | ★**0** ★ | 完整, 无回退 |
| `gate_check.py` | ★**0** ★ | ★**Q1 11/18** (★hw 3/6 缺 B2/B4/B5 · sw 6/6 ★按 ISS-323 回退计分★ · mech 2/6 缺 B2/B3/B4/B5★) · ★**Q2 2/3** (★mech 无证据分级标签★) · ★**Q3 接口声明 968 条** ★ · ★**Q4 问方 89/478 · 内部未闭合 334 · 等外部 50** ★ · ★**Q7 钉板 md5 闸链 9/9 全绿** ★ · 缺口清单 11 条 |
| `issue_check.py` | ★**0** ★ | 问题闭环门全过 |
| `stage_gate.py` | ★**1** ★ | ★**当前 G1 · 还差 1 项 (PCB 布线 unconnected=45 需 0)** ★ · ★**G1a 还差 2 条 (G1a-4 / G1a-8 ⇒ 与 §A 的 W-2 / A4 同一件事)** ★ |
| `daily_check.py` | ★**3** ★ | ★**巡检异常已记录 (非崩溃)**: ① `check_pcb_nets` rc=1 (板↔网表逐焊盘等价没过 ⇒ 已知基线 C1 缺失 0 / 多余 2 / 同号异网 3) ② `chain_gate` rc=1 (已知基线) ③ 漂移检测有漂移 (★Q1 18/18→11/18 · 问题单 297→323 · 内部未闭合 316→334 · 未闭环 blocker 10 条★) ★ |
| ★**`gen_progress_snapshot.py`** | ★**0** ★ | ★**`PROGRESS_SNAPSHOT.md` 已生成 (3099 B · 15:28) ★ ⇒ ★**只落本地快照, 本 job 不推 GitHub (★由 5 小时同步 job 负责·上次推送 2026-11-18T05:26:21★)** ★ |
"""

if not os.path.exists(BAK):
    shutil.copy2(PAGE, BAK)
    print("★备份:", BAK)

with open(PAGE, "a", encoding="utf-8") as f:
    f.write(SECTION)

print("★追加完成: %s (mtime %s)" % (PAGE, os.path.getmtime(PAGE)))
