#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
r70 (2026-11-18 13:25 · cron 775d9893 · 项目总工 moli)
================================================================================
DECISION_INDEX_2026-11-18.md 的【追加式订正 §H】

★**追加式 —— §A / §B / §C / §D / §E / §F / §G 的老字一个字未删未改** ★
★**只补两件**: ① §H-1 新增的 §A 级卡点 `iss324_d_led_g_placement_decision`
                (★MECH ISS-324 交卷 ⇒ 落位口径已给 ⇒ 只剩老板拍板★)
              ② §H-2 本轮台账更新 (decisions 39→40 · §B 已拍掉 5 条)
              ③ §H-3 本轮自检读数 + 零写板双证

★**纪律**: 零外发 · 零写板 · 零落表 · 不改 PROJECT_TRACKER.md §0 · 不写别的 agent 的分片 · 不替老板拍板
"""

import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
PAGE = os.path.join(PROJ, "DECISION_INDEX_2026-11-18.md")

TS = "20261118_1325"
BAK = PAGE + ".bak_" + TS + "_r70"

SECTION = r"""

---

## §H · ★★【r70 · 2026-11-18 13:25 · 追加式订正】★★ · ★**新增 1 个 §A 级卡点 (MECH ISS-324 交卷带来的落位拍板) + §B 已拍掉 5 条** ★★

> ★**追加时刻**: 2026-11-18 13:25 · ★**追加人**: 项目总工 (moli) · cron `775d9893` · ★**依据**: `advance.py --json` (13:14 实跑) + `state/fragments/mech.yaml` 本机实读 (★不抄任何 agent 报告★) · ★**本节追加时 §A~§G 的老字一个字未删未改** ★
> ★**性质**: ★**只加台面 + 只更新台账, 不改任何一条建议默认值, 不替老板拍任何一条** ★

### ★H-1 · ★★【新增 §A 级卡点: `D_LED_G` 落位拍板 (MECH ISS-324 交卷带来)】★★ ★**(★今天 13:0x 唯一新增的老板级项·due 2026-11-18 = 剩0天★)** ★★

★**为什么它是 §A 级 (卡「板只改一次」那一趟开工)**: ★**MECH 侧落位口径 (候选 C1~C6 + 判据 D1~D7 + 9 条反向用例) 已由 mech-lead 在 ISS-324 交付完 ⇒ 技术面不缺料, 只缺老板一句拍板 ⇒ ★**它是「板只改一次」那一趟的开工前提之一, 不是可以慢慢拍的队列项** ★**

| 编号 | need key (★回这个★) | 挂在哪 | 要拍什么 | 建议默认值 (★建议·不是已决定★) | 不拍的后果 | 卡不卡 G1a 转绿 |
|---|---|---|---|---|---|---|
| **W-3** | `iss324_d_led_g_placement_decision` | mech.yaml · `to=boss` · `waiting_on=boss` · due **2026-11-18** (剩0天) | ★**`D_LED_G` 落在板上哪个点 + 亮度档已拍后是否还要动器件位置** ★ —— ★**只问落位点与是否挪位, 不重复问「外露/光孔有无」**(★那是 `boss_dled_g_expose_decision_20261117`, 同一条决策链的另一半★) ★ | ★**假设 B (无结构光孔 / 位置不动 ⇒ 零板面动作 ⇒ 不触发第二次改板)** ★ —— ★**MECH 侧首选是封装原点 (8.420, 64.200) ⇒ `LED_G_D` 从 93.492727 mm 压到 1.477 mm (缩短 92.016 mm / 98.42%)· 排序 C3 首选 → C2 (8.050,63.900) 次选 → C5 (8.250,66.000) 备选 → C6 (2.500,60.000) 仅假设 B 专属 · C1/C4 实测淘汰(净距 0.000 mm < netclass 0.20 ⇒ 板 DRC 必红)★** ★ | ★**`LED_G_D` 93.49 mm 这条 + `LED_G` 净距那条布不了 ⇒ S8 归不了零 ⇒ G1 开不了** ★ | ★**不直接卡 G1a (G1a-4/8 是 R4/R9 + ISS-097 签字)★** ★**但卡 G1 (PCB 布线归零)** ★ |

★**★这一条与 §G-1-b 的 G12 (`iss322_s8_d_led_g_pos`) 是同一件事, ★**不重复拍** ★** —— ⇒ ★**§G 的 G12 行已被 MECH 侧实测答案覆盖 (候选 C3 = 封装原点) ⇒ ★**老板只要回 W-3 这一个 key, G12 就跟着定了** ★**
★**★依赖顺序提醒 (★main 自己理的, 不代拍★)**: ★**W-3 落位 与 G-5 (`boss_dled_g_expose_decision_20261117` 外露/光孔有无) 是两件独立的事** ★** —— ★**改亮度档只改器件值, 不改器件位置 ⇒ 落位与亮度档可以分开拍; 但若 G-5 拍「有光孔」⇒ 光孔中心 X 必须 = `D_LED_G` 铜箔中心 X, 且中心 Y 落在最近落位带 Y 63.700..67.900 内 ⇒ ★**光孔那张牌会反过来约束落位候选** ★**
★**⇒ 拍板面变化**: ★**§A 的卡点从 4 个字母 (2 个 need key) ⇒ 5 个字母 (3 个 need key) = W-2 / W-1b / W-1c / A4 / A5 + W-3** ★**

### ★H-2 · ★★【§B 台账更新: decisions 39 → 40 · 已拍掉 5 条】★★

| 项 | 读数 (★13:14 本机实跑 `advance.py --json`★) |
|---|---|
| decisions 总数 | ★**40 条** (★§G 记的 39 条 ⇒ +1 = §H-1 的 W-3★) |
| ★**§B 里已不再待拍的 5 条** ★ | ★**`iss091_rilim_decision` · `iss091_worn_while_charging` · `iss100_board_length` · `iss099_poka_yoke_decision` · `iss099_rilim_300_dead`** ★ —— ★**机器实读确认: 5 个 key 全部已在 `state/decision_truth.py` 的已拍集合里 ⇒ `advance.py` 按口径自动过滤掉 ⇒ ★**它们不再占老板的拍板面, 本页 §B 表里保留老字作留痕 (★追加式纪律: 不删老字★)** ★ |
| ★**口径复核 (★防漏报·本轮自查★)** ★ | ★**分片里 `waiting_on=boss` 的 need 共 42 条, advance.py 报 40 条 ⇒ 差的 2 条是 `q4_battery_scope` / `q16_aspect_ratio` 这类【同一 key 在 hw/mech/pm/sw 四份分片里重复登记】⇒ 机器按 key 去重 ⇒ 40 是权威数, 无缺口** ★ ★**另核: 那 10 条「页面上找不到 / 未进 decisions」的 need 实读 = 全部已在 decision_truth (已拍) ⇒ ★**不是漏项** ★ |
| 机检覆盖 | ★**当前 40 条待拍 ⇒ 本页覆盖 40/40** (★§A 表含 W-2 / W-1b / W-1c / A4 / A5 + §H-1 的 W-3 = 6 行 3 个 key · §B 表含其余 37 条 · ★**§G-1 的 12 条板级轴是 `to=main` ⇒ 不在 advance.py 队列里, 但已在本页台面上★)** ★ |

### ★H-3 · ★§H 自检数据 (★本 job 13:14~13:25 本机实跑★)★★

| 项 | 读数 (★2026-11-18 13:14~13:25 实跑★) |
|---|---|
| `advance.py --json` | ★**internal 0 条 · approvals 0 条 · decisions 40 条 · waiting 0 条** ★ (★approvals 恒空 = 老板 2026-11-12 02:02「不再发信」政策★) |
| ★**internal 为什么是 0** ★ | ★**机器实读 `state/issue_log.yaml`: 三个总工名下 0 条 `open`** ★ —— ★**hw-lead / sw-lead / mech-lead 各有 1 条 `fixing` (ISS-325 / ISS-323 / ISS-324) ⇒ advance.py 的「一个 agent 同时一个在飞任务」判据把三个都挡住 ⇒ ★**本 job 派活 0 条 = 正确行为, 不是漏派** ★ |
| 在飞会话实况 (`sessions_list`) | ★**hw-lead ISS-325 (S8 左上布局 21 器件钉位沙盒预演) = `running`** (★两个 router 都在 99.8% CPU · 重 A* 搜索, 没卡死★) · ★**sw-lead ISS-323 cont1 = `done` (12:58~13:05 交卷完成)** · ★**mech-lead ISS-324 cont1 = `done` (交卷完成)** ★ ⇒ ★**后两条已交卷但台账仍是 `fixing` ⇒ 等 main 签收转 `verified`, 本 job 不重复派** ★ |
| ★**本 job 派活** ★ | ★**0 条** ★ —— ★**兄弟 job `fb67af40` (队列自动派活) 在管派活, 本 job 不重复派 (★铁律: 一个 agent 同时只能一个写会话★)** ★ |
| 核验 5 连 rc | ★**merge 0** (★13:15 实跑: 产出 **660** · 阻塞 43 (高危 33) · 未闭合需求 **330** · 冲突 0 · 健康度 red★) · ★**gate_check 0** (★13:1x 实跑: Q1 齐备率 **18/18** · Q7 钉板 md5 闸链 **9/9 道绿** · 缺口清单 **3** 条: hw 170 / sw 91 / mech 66★) · ★**issue_check 0** (★登记 **321** 条 · 内部 290 / 外部 31 · 逾期 0 · 违规 0 · 全过★) · ★**stage_gate 1** (★当前 **G1** · 还差 **1** 项 (PCB 布线 unconnected=**45** 需 0 · DRC 违规 0 已达标) · **G1a 还差 2 条**) · ★**daily_check 3** (★巡检异常已记录, 非崩溃★) |
| ★**G1a 差哪 2 条** ★ | ★**G1a-4 落表已清零 (翻面口径)**: ★**R4 未落表 (`D_ESD_USB_D` 仍只有 2 个焊盘 D+ + GND ⇒ 仍不是双通道) + R9 未落表 (`D_ESD_USB_D` → `J_USB_C` 板面距离)** ★ · ★**G1a-8 关机语义 + 负载开关选型已决**: ★**ISS-097=fixed · ISS-172=verified ⇒ 差 ISS-097 的签字 (main 的活, 子 agent 不得自签)** ★ ⇒ ★**★这两条与 §A 的 W-2 / A4 是同一件事 ⇒ §A 拍完 ⇒ G1a 才可能全绿** ★ |
| 漂移检测 (★daily_check 本轮读数★) | ★**内部未闭合 316 → 330 · 问题单 297 → 321 (未闭环 blocker 10 条)** ★ ⇒ ★**漂移方向 = 本周连续开工的正常累积 (12 条板级轴带出的新 need 已登记), 不是回退** ★ |
| 巡检异常 (★2 条, 同型老账★) | ★**① `check_pcb_nets` rc=1** (★板子与网表不一致, 不许投板★) · ★**② `chain_gate` rc=1** (★PCB 准入红 = 板是旧网表的板 · 投产包准入红 = 投产包比原理图旧 ⇒ 投板用的是旧板 Gerber★) ⇒ ★**这两条都是「板那一趟」本体, 板重出时一起清** ★ |
| 板面零变化 (双证) | ★**板 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413` 逐字节不变** ★ (★13:2x 本机实跑 `md5sum` + `stat`★) · ★**网表 `6aee500e` · 脚表 `9174309d` · BOM `5b999399`** (★与 §G 记的同值 ⇒ 同样未变★) |
| 本 job 落盘 | ★**2 件**: `DECISION_INDEX_2026-11-18.md` (+§H 追加式 · +1 份备份) + `PROGRESS_SNAPSHOT.md` (★13:20 生成★) ⇒ ★**零外发 · 零写板 · 零落表 · 不改 PROJECT_TRACKER.md §0 · 不写别的 agent 的分片 · 不替老板拍板** ★ |
| GitHub | ★**本 job 不推** (★统一由独立 job `ARS45 GitHub 同步 (每 5 小时 · 有进展才推)` 负责★) ⇒ ★**只落本地快照** `PROGRESS_SNAPSHOT.md` ★ |
"""


def main() -> int:
    if not os.path.exists(PAGE):
        print("★page missing: %s" % PAGE)
        return 2
    old = open(PAGE, encoding="utf-8").read()
    if "## §H · ★★【r70" in old:
        print("★已存在 §H (r70) ⇒ 不重复追加")
        return 0
    shutil.copy2(PAGE, BAK)
    with open(PAGE, "a", encoding="utf-8") as f:
        f.write(SECTION)
    new = open(PAGE, encoding="utf-8").read()
    assert new.startswith(old), "★追加式违规: 老字被改动"
    print("✅ DECISION_INDEX_2026-11-18.md 已追加 §H (r70)")
    print("   老字节 = %d → 新字节 = %d (追加 %d)" % (len(old), len(new), len(new) - len(old)))
    print("   备份 = %s" % os.path.basename(BAK))
    print("   追加式自证: 老字逐字前缀未变 = True")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
