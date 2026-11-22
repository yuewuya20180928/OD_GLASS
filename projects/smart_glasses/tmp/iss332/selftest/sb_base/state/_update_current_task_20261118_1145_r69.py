#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
r69 (2026-11-18 11:4x · cron 775d9893 · 项目总工 moli)
================================================================================
state/CURRENT_TASK.md 的【首行播报源更新 · r69】

★**纪律**: 只在首行前面加本轮播报行 · 老行逐字保留作留痕 · 零外发 · 零写板 · 零落表
★**不改 PROJECT_TRACKER.md §0 · 不写别的 agent 的分片 · 不替老板拍板**
"""

import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
TASK = os.path.join(os.path.dirname(HERE), "state", "CURRENT_TASK.md")
TS = "20261118_1145"
BAK = TASK + ".bak_" + TS + "_r69"

LINE = (
    "★[状态] ★★**★主线 = 绘制 PCB 图 (★老板 2026-11-17 00:43 指令★)** ★★ ⇒ ★**PCB 布线 / 布局类 ISS 现在【可派】** ★★ "
    "⇒ ★**但「板只改一次」铁律仍在: 所有会改板的动作必须一次做完 (位号改名 + 板侧同步 B-1~B-8 + 布局修正 + 布线 45→0 + Gerber/投产包重出 同一趟做完)** ★★ "
    "⇒ ★★**【2026-11-18 11:2x~11:4x (cron 775d9893 本机实跑) · 本轮两件实事】★★** "
    "⇒ ★**① A 段 internal = 0 条 ⇒ 本 job 派 0 条 (★`advance.py --json` 实读 11:20: internal [] · approvals [] · decisions 39 · waiting []★) "
    "⇒ 根因 = 三个总工名下各 1 条 `fixing` 占位 ⇒ `advance.py` 的 in_flight 判据把三条全挡住 (★hw-lead ISS-322 会话 status=running 真在飞 · sw-lead ISS-321 11:14:32 已交卷待落地 · "
    "mech-lead ISS-320 11:29:56 已交卷待落地★) ⇒ ★**铁律「一个 agent 同时只能一个写会话」⇒ 本 job 不重复派; 落地签字由兄弟 job `fb67af40` 11:3x 那轮做** ★** "
    "⇒ ★**② 决策页出【追加式 §G】(★`DECISION_INDEX_2026-11-18.md` +8,961 B·备份 `.bak_20261118_1150_r69`·老字 §A~§F 逐字前缀未变 = True★)**: "
    "★**ISS-317 / ISS-321 / ISS-322 三单交卷一次性带出 12 条【板级轴】(全部 `to=main` ⇒ `advance.py` 的 decisions 段读不到 ⇒ 老板在队列里一条都看不到 ⇒ 本轮提到台面上)** ★ "
    "⇒ ★**§G-1-a = ISS-321 带出 5 条 (SW 侧「板只改一次」同批范围) · §G-1-b = ISS-322 带出 7 条 (S8 布线归零 45→0 的 7 个死结)** ★ "
    "⇒ ★**STATE.yaml 本机实读: 12 条 = 11 条 pending + 1 条 answered (★`iss318_sw_ref_baseline3_disposition` = main 10:1x 已裁 ⇒ 不占老板拍板面★)** ★ "
    "⇒ ★**§G-2 = §F-2 #1 的口径订正 (★「三侧同口径」→「五侧同口径」★表侧 218 里 186 个要改 · 板侧只动 156 个; NC 白名单丙-① 裸前缀实测会放过真错 ⇒ 不推荐; 判据解封是两行不是一行)** ★ "
    "⇒ ★**机检: `advance.py --json` 的 39 条 decisions 逐 key 命中决策页 = 39/39 · 13 个板级轴 key 命中 = 13/13** ★ "
    "⇒ ★**其中 4 条 (G9 BAT_DET 终点 / G10 ESD 架构 / G11 PWR_GOOD 极性 / G12 D_LED_G 落位) 技术上 main 能代答 (现状网表 + 候选集已给) ⇒ ★**不代拍** ★ "
    "⇒ ★**建议老板在这 11 条上只回一句「按建议默认值」** ★ "
    "⇒ ★★**【核验 5 连本轮实测 rc】**★★ ⇒ ★**merge 0** (★11:21 实跑: 产出 652 · 阻塞 43 (高危 33) · 未闭合需求 323 · 冲突 0 · 健康度 red★) · "
    "★**gate_check 0** (★11:22 实跑: Q1 齐备率 18/18 · Q7 钉板 md5 闸链 9/9 道绿 · 缺口清单 3 条★) · ★**issue_check 0** (★318 条 · 内部 287 / 外部 31 · 逾期 0 · 违规 0·全过★) · "
    "★**stage_gate 1** (★当前 **G1** · 还差 **1** 项 (PCB 布线 unconnected=45 需 0 · DRC 违规 0 已达标)·**G1a 还差 2 条**) · ★**daily_check 3** (★巡检异常已记录·非崩溃★) "
    "⇒ ★**G1a 差哪 2 条 (`check_stage_g1a.py` rc=1 实读)**: ★**G1a-4 落表已清零 (R4 未落表: `D_ESD_USB_D` 仍 2 焊盘 ⇒ 仍不是双通道 + R9 板面距离) + G1a-8 关机语义+负载开关选型已决 (ISS-097=fixed 待 main 签字)** ★ "
    "⇒ ★**这两条与决策页 §A 的 W-2 / A4 是同一件事 ⇒ §A 拍完 ⇒ G1a 才可能全绿** ★ "
    "⇒ ★★**【板面零变化 (双证 · 11:3x 本机实跑)】**★★ ⇒ ★**板 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413` 逐字节不变** ★ · ★**网表 `6aee500e` · 脚表 `9174309d`** ★ "
    "⇒ ★**本 job 落盘 2 件**: `DECISION_INDEX_2026-11-18.md` (+§G 追加式·+1 份备份) + `state/CURRENT_TASK.md` (本行·老行保留作留痕) + `PROGRESS_SNAPSHOT.md` (本地快照) ⇒ "
    "**零外发 · 零写板 · 零落表 · 不改 PROJECT_TRACKER.md §0 · 不写别的 agent 的分片 · 不替老板拍板** ★ "
    "⇒ ★**GitHub: 本 job 不推 (★统一由独立 job `ARS45 GitHub 同步 (每 5 小时 · 有进展才推)` 负责★) ⇒ 只落本地快照 `PROGRESS_SNAPSHOT.md`** ★ "
    "⇒ ★★**【下一轮 (cron 775d9893 12:0x / fb67af40 11:3x) 要做的事】**★★ ⇒ ★**① fb67af40 落地 ISS-320 / ISS-321 / ISS-322 三单 → 三个总工名额释放** ★ "
    "⇒ ★**② 队列会空 (open 0) ⇒ main 需新开单, 下一批候选 (★纯分析/作业包类·零写板★): sw-lead = 「板只改一次」那一趟的 SW 侧 7 件同批改动可执行清单 (★ISS-321 的交卷是【发现+改法】, 缺【像 ISS-317 那样的可执行清单】★) · "
    "hw-lead = 「左上布局」方案可行性预演 (★沙盒实跑 hw-lead 自己给的修法 ⇒ 看 unc 45 能降到多少 + DRC + 差分配平·这是老板 G7 决定的唯一验证手段★) · "
    "mech-lead = `D_LED_G` 落位 (★G12 的前置·ISS-320 已交卷 ⇒ 机位空出来了★)** ★ "
    "⇒ ★**③ 盯 `gate_check.py` rc 保持 0 (★ISS-321 交卷后 SW 侧闸已回绿★)** ★ ⇒ ★**④ 本 job 不发任何信** ★"
)


def main() -> int:
    old = open(TASK, encoding="utf-8").read()
    if "2026-11-18 11:2x~11:4x (cron 775d9893 本机实跑)" in old:
        print("★r69 播报行已在 ⇒ 不重复写")
        return 0
    shutil.copy2(TASK, BAK)
    with open(TASK, "w", encoding="utf-8") as f:
        f.write(LINE + "\n" + old)
    new = open(TASK, encoding="utf-8").read()
    assert new.endswith(old), "★老块未逐字保留"
    print("✅ state/CURRENT_TASK.md 首行已更新 (r69)")
    print("   老字节 = %d → 新字节 = %d (新增 %d)" % (len(old), len(new), len(new) - len(old)))
    print("   老块逐字保留 = True")
    print("   备份 = %s" % os.path.basename(BAK))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
