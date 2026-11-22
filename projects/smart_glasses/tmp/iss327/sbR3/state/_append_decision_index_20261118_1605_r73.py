#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r73 · 2026-11-18 16:05 · DECISION_INDEX_2026-11-18.md 追加 §L (追加式 · 只加读数与事实)
纪律: 老字一个字未删未改 (追加前逐字校验前 548 行不变)
"""
import hashlib, io, os, sys

P = "DECISION_INDEX_2026-11-18.md"
BAK = "DECISION_INDEX_2026-11-18.md.bak_20261118_1605_r73"

before = open(P, encoding="utf-8").read()
before_lines = before.split("\n")
before_md5 = hashlib.md5(before.encode("utf-8")).hexdigest()

SEC = """
## §L · ★★【r73 · 2026-11-18 15:53~16:05 · 追加式】★★ · ★★**本 job (cron 775d9893) 15:53 这一轮的实跑读数 (★拍板面 40 条一条未动 + 门禁原样 rc + 本轮新增的 1 条事实)★★** ★★

> ★**追加时刻**: 2026-11-18 15:53~16:05 · ★**追加人**: 项目总工 (moli) · cron `775d9893`
> ★**依据**: ★**本机实跑 `state/advance.py --json` / `state/merge.py` / `state/gate_check.py` / `state/issue_check.py` / `state/stage_gate.py` / `state/daily_check.py` / `state/gen_progress_snapshot.py` + `sessions_list` + `md5sum`/`stat` (★全部 15:53~16:05 本机实读★) ★
> ★**本节追加时 §A~§K 的老字一个字未删未改** ★
> ★**性质**: ★**只加读数与事实 · 不新增待拍项 · 不改任何一条建议默认值 · 不替老板拍任何一条** ★

### ★L-1 · 拍板面复核 (★15:53 本机实跑 `advance.py --json`★)

| 段 | 15:2x (§K-1) | ★**15:53 本轮复读** ★ | 结论 |
|---|---|---|---|
| internal (A 段可派) | 0 | ★**0** ★ | ⇒ ★**三条 `fixing` 占位把队列占满 (ISS-325 / ISS-326 / ISS-327) ⇒ 本 job 派 0 条 (★见 §L-2★)** ★ |
| approvals (B 段外发草稿) | 0 | ★**0** ★ | ⇒ ★**与老板 2026-11-12 02:02「不再发信, 全靠自己查资料」口径一致 (★外发政策: 一律不发·缺口自己上网查 + 标证据等级★)** ★ |
| decisions (C 段待拍) | 40 | ★**40** ★ | ⇒ ★**逐条同 key ⇒ §A~§K 的拍板面仍然有效, 无新增无减少** ★ |
| waiting (D 段纯等待) | 0 | ★**0** ★ | — |

★**机器交叉校验 (★本轮新增的一遍自证★)**: 本轮另跑一遍 need-key 覆盖校验 ⇒ ★**40/40 个 key 在 `DECISION_INDEX_2026-11-18.md` 命中 (漏 0)** ★ · ★**40/40 个 key 在 `DECISION_PENDING_2026-11-16.md` 命中 (漏 0)** ★ ⇒ ★**「决策页一条没漏」这个自证, 本轮是机器验的, 不是人眼看的** ★
★**注**: ★**本页顶部那行「decisions 段 44 条」是 02:54 的历史读数 (已被 §F-1 订正到 39 → §H-2 订正到 40) ⇒ 本页老字一个字未改, 订正一律写在追加节里** ★

★**今日到期 (剩 0 天) 仍为 3 条** (★只提醒·不代拍★): ★`iss324_d_led_g_placement_decision` (★`D_LED_G` 落位·建议默认 = 假设 B「无光孔·位置不动·零板面动作」★) · ★`iss206_mech_claim_mainboard_len_carrier_direct_scheme_choice` (★SoM 载板形态★) · ★`boss_dled_g_expose_decision_20261117` (★`D_LED_G` 要不要对外暴露·即「板那一趟」第二个阻塞项★) ★

### ★L-2 · ★★【队列归属】本 job 派 0 条 —— 原因说死, 免得老板以为没人干活 ★★

★**`advance.py` 的 internal 段为空 = 三条 `fixing` 占位把队列占满了 (★一条 `fixing` = 已被兄弟 job `fb67af40` 派出去、正在跑★)**:

| issue | owner | 本 job 15:53 实读状态 (`sessions_list`) | 备注 |
|---|---|---|---|
| ★**ISS-325** (★S8 左上布局沙盒预演·零写板★) | hw-lead | ★**在跑** ★ (★cont1 / cont2 / cont3 / cont4 四条会话并存, 最近一条 cont4 15:36 起 · status=running·runtimeMs≈1,475s★) | ★**hw-lead 不空闲** ★ |
| ★**ISS-326** (★S1 改名 MECH 侧安全性体检·零写板★) | mech-lead | ★**在跑** ★ (★status=running·正在跑最终核验轮★) | — |
| ★**ISS-327** (★改名后 SW 闸链复活验证·零写板★) | sw-lead | ★**在跑** ★ (★status=running·正在核闸链读数★) | — |

★**⇒ 本 job (cron 775d9893) 本轮派 0 条, 跳过 0 条 (★internal 段本来就空·无「派不动」的情况★)** ★
★**⇒ 重派权归兄弟 job `fb67af40` (★它持队列·本 job 不抢·一个 agent 同时只能有一个写会话★)** ★
★**⇒ ★★板面双证 (★本 job 16:0x `md5sum` + `stat` 实读★)★★**: ★板 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413` ⇒ ★**逐字节未变 (12 天零变化)** ★ ⇒ ★**G1 仍开, 不许投板** ★

### ★L-3 · 本轮门禁读数 (★15:53~16:0x 本机实跑·原样 rc★)

| 项 | rc | 读数 |
|---|---|---|
| `merge.py` | ★**0** ★ | 完整, 无回退 (★产出 664 · 阻塞 43 (高危 33) · 未闭合需求 334 · 冲突 0 · 健康度 red★) |
| `gate_check.py` | ★**0** ★ | ★**Q1 11/18** (★hw 3/6 缺 B2/B4/B5 · sw 6/6 · mech 2/6 缺 B2/B3/B4/B5★) · ★**Q2 2/3** (★mech 无证据分级标签★) · ★**Q3 接口声明 968 条** ★ (hw 367 / sw 284 / mech 317) · ★**Q4 问方 89/478 · 内部未闭合 334 · 等外部 50** ★ · ★**Q7 钉板 md5 闸链 9/9 全绿** ★ · 缺口清单 11 条 |
| `issue_check.py` | ★**0** ★ | 问题闭环门全过 |
| `stage_gate.py` | ★**1** ★ | ★**当前 G1 · 还差 1 项 (PCB 布线 unconnected=45 需 0)** ★ · G1a 还差 2 条 (G1a-4 / G1a-8 ⇒ 与 §A 的 W-2 / A4 同一件事) ★ |
| `daily_check.py` | ★**3** ★ | ★**巡检异常已记录 (非崩溃)**: ① `check_pcb_nets` rc=1 (板↔网表逐焊盘等价没过 ⇒ 已知基线 C1 缺失 0 / 多余 2 / 同号异网 3) ② `chain_gate` rc=1 (已知基线) ③ 漂移检测有漂移 (★Q1 18/18→14/18 · 问题单 297→323 · 内部未闭合 316→334 · 未闭环 blocker 10 条★) ★ |
| ★**`gen_progress_snapshot.py`** | ★**0** ★ | ★**`PROGRESS_SNAPSHOT.md` 已生成 (★16:02★) ⇒ ★**只落本地快照, 本 job 不推 GitHub (★由 5 小时同步 job 负责★)** ★ |

### ★L-4 · ★★【本轮新增的一条【事实】】Q1 11/18 不是【质量回退】, 是【两条交卷页还在写】★★

- ★**hw-lead 的 `2026-11-18_hw-lead_ISS325_左上布局沙盒预演.md` 缺 B2/B4/B5** + ★**mech-lead 的 `2026-11-18_mech-lead_ISS326_S1改名MECH侧安全性体检.md` 缺 B2/B3/B4/B5** ⇒ ★**这两个 agent 的会话 15:5x 实读都还在跑** (★hw-lead cont4 15:36 起 · mech-lead 正在跑最终核验·runtimeMs≈1,993s★) ⇒ ★**⇒ 这两张交接单是【半成品】, 不是【交了但不合格】** ★
- ⇒ ★**Q1 11/18 的性质 = 【未完工】(★与 §K-2 的 15:2x 读数同值 ⇒ 这一轮没有新的质量塌方★)** ★ ⇒ ★**[推算]** 两条收尾后这两块会自己补齐, Q1 随之上抬 ★
- ★**sw-lead 6/6 满块** (★ISS-327 交卷页 B0~B7 完整★) ⇒ ★**SW 侧这一趟已经交卷** ★
- ★**板面双证 (★16:0x 实读★)**: ★板 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413` ⇒ 逐字节未变 (12 天) ★ · ★网表 `b1be1937a683cb6f0fb3714a683684ef` (`demo_mainboard_sch.net`) · 脚表 `67340a0b707095fc4c0755a4c79ea8b6` (`FET3572C_PIN_TABLE.csv`) · `84b1b478e69df374351f8cb65ce89ffb` (`FET3576C_PIN_TABLE.csv`) ⇒ 全未变 ★
- ★**本 job 步骤 6 纪律**: ★**只落本地快照** (`PROGRESS_SNAPSHOT.md` rc=0) · ★**未** rsync `/tmp/od_glass_publish` · ★**未** git commit/push · ★**未**跑真值反查 (★全归 5 小时同步 job★) ★
"""

after = before + SEC
with io.open(P, "w", encoding="utf-8") as f:
    f.write(after)

# ---- 校验: 老字逐字未改 ----
now = open(P, encoding="utf-8").read()
now_lines = now.split("\n")
assert now_lines[: len(before_lines)] == before_lines, "★老字被改了★"
assert now.startswith(before), "★前缀不一致★"
print("✅ 老字逐字未改校验通过 (前 %d 行 + 末尾换行 %d 行原样)" % (len(before_lines), len(now_lines)))
print("   before md5 =", before_md5)
print("   after  md5 =", hashlib.md5(now.encode("utf-8")).hexdigest())
print("   before lines =", len(before_lines), " after lines =", len(now_lines), " (+%d)" % (len(now_lines) - len(before_lines)))
print("   backup =", BAK, os.path.exists(BAK))
