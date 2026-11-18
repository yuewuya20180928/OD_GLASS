#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
r68 (2026-11-18 09:5x · cron 775d9893 · 项目总工 moli)
================================================================================
CURRENT_TASK.md 更新 = ★**播报源**★ (state/board_progress.py 读它)

★**改法 (★留痕纪律★)**:
  ① 第 1 行 = 【当前在做】⇒ 换成本轮实跑事实 (主线口径不变 = 绘制 PCB 图)
  ② 老第 1 行 = 退成历史块 (★原字保留★)
  ③ 待办清单 (①..⑥) = 换成【本轮实读的真待办】
     ⇒ ★**老待办整块降级成注释行** (★`#` 前缀 ⇒ board_progress.py 过滤掉, 但字还在文件里★)
  ④ 其余行一个字不动

★**纪律**: 零外发 · 零写板 · 零落表 · 不改 PROJECT_TRACKER.md §0 · 不写别的 agent 的分片 · 不替老板拍板
"""

import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
TASK = os.path.join(PROJ, "state", "CURRENT_TASK.md")
BAK = TASK + ".bak_20261118_0950_r68"

NEW_HEAD = (
    "★[状态] ★★**★主线 = 绘制 PCB 图 (★老板 2026-11-17 00:43 指令★)** ★★ ⇒ ★**PCB 布线 / 布局类 ISS 现在【可派】** ★★ "
    "⇒ ★**但「板只改一次」铁律仍在: 所有会改板的动作必须一次做完 (位号改名 + 板侧同步 B-1~B-8 + 布局修正 + 布线 45→0 + Gerber/投产包重出 同一趟做完)** ★★ "
    "⇒ ★★**【2026-11-18 09:5x (cron 775d9893 本机实跑) · 本轮三件实事】★★** "
    "⇒ ★**① A 段 internal = 0 条 (★`advance.py --json` 实读: internal [] · approvals [] · decisions 39 · waiting []★) ⇒ 根因 = 三个总工名下 open 全为 0 (真真空) + 各自各有 1 个 fixing 在飞 ⇒ 铁律「一个 agent 同时只能一个写会话」⇒ 本 job 不重复派**★ "
    "⇒ ★**② 决策页已追加式订正 `DECISION_INDEX_2026-11-18.md` §F (r68 · 8,901 B · 老字逐字未变 + 备份)**: §F-1 计数订正 (待拍板面 **44 → 39** 条 · 5 条已退休 · 附逐条退休依据) + §F-2 **今日新增 4 条板级轴** (★全部 `to=main` ⇒ advance.py 的 decisions 段读不到 ⇒ 老板在队列里看不到 ⇒ 本节提到台面上★) + §F-3 本轮巡检读数与零写板双证** ★ "
    "⇒ ★**③ 核验 5 连 rc**: merge **0** · gate_check **0** (Q1 18/18 · Q7 钉板 md5 闸链 **9/9 道绿**) · issue_check **0** (316 条 · 逾期 0 · 违规 0) · stage_gate **1** (当前 **G1** · 还差 **1** 项) · daily_check **3** (★巡检异常已记录, 非崩溃★) ⇒ **板面零变化**: 板 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413` 逐字节不变 · 网表 `6aee500e` · 脚表 `9174309d` · BOM `5b999399` (★mtime 11-18 00:21 = ISS-302 合法落表, 不是本 job 写的★) ⇒ **G1 仍开, 不许投板** ★★ "
    "★★**【在飞 3 条 (★兄弟 job fb67af40 于 09:16~09:17 派出 · 三个 agent 各 1 个 running 写会话 · 真在飞不是僵尸★)】★★** "
    "⇒ ★**ISS-317 → hw-lead** (★S1 位号改名「三侧同口径」可执行清单 + NC 白名单撞死的三选项 + BOM 证据回填兜底判据 · 纯分析/作业包/判据设计类 · 零写板★) "
    "· ★**ISS-318 → sw-lead** (★SW 侧 95 处位号引用做成机器可判的重命名影响面闸 + ISS-315/312/309 四道闸的挂链前体检 · 判据新建类 · 零写板★) "
    "· ★**ISS-320 → mech-lead** (★电芯型号订正【实做】47 行里的 33 行 (MECH 域 19 文件) · 只换型号名 `ICP582035PR-01`→`ICP422339PR` · 尺寸常量一个不许动 · 11 行留证行一行不许碰 · 受限文本订正类 · 零写板★) ★ "
    "⇒ ★**本 job 不重复派** (★铁律: 一个 agent 同时只能一个写会话 · 两个 job 同时派同一 agent = 撞 R18 · 分片合并丢 12%~38%★) ★★ "
    "★★**【GitHub: 本 job 不推】★★** (★老板 2026-11-11 09:5x 口径 · 统一由独立 job `ARS45 GitHub 同步 (每 5 小时 · 有进展才推)` 负责★) ⇒ ★**只落本地快照 `PROGRESS_SNAPSHOT.md`** ★★ "
    "★★**【待拍板面 = 39 条 (★`advance.py --json` 实读·不是估的★)】★★** ⇒ ★**其中 4 个字母卡「板那一趟」开工: W-2 (D− 侧补不补 ESD) · W-1c (D+ 那颗 ESD 的 OPN) · A4 (关机语义签收 C+A) · A5 (负载开关 `TPS22991RAA` 追认) ⇒ 一页 = `DECISION_INDEX_2026-11-18.md` (§A = 4 个字母 · §E-1 = 板框 U-1 的 36 档机器实跑 · §F-2 = 今日新增 4 条板级轴) ⇒ ★**建议默认值都在页上, main 不代拍** ★"
)

NEW_TODOS = [
    "① ★**老板拍板: 「板只改一次」那一趟的 4 个字母 + 板框 U-1 三选一** ⇒ ★**W-2** (USB D− 侧补不补 ESD · 现状 D− 侧 ESD 位号数 = **0** ⇒ 裸奔) · ★**W-1c** (D+ 那颗 ESD 的真 OPN · 候选 C1 `TPD2EUSB30DRTR` / C2 `TPD2E2U06DCKR` / C3 `ESD752DCKR` / C4 `CM1218-02S7`) · ★**A4** (关机语义签收 C+A) · ★**A5** (负载开关 `TPS22991RAA` 追认) ★ ⇒ 一页 = `DECISION_INDEX_2026-11-18.md` ⇒ ★**W-2 + A4 卡 G1a-4 / G1a-8 ⇒ 不拍 ⇒ G1a 永远红 ⇒ G1 关不开** ★",
    "② ★**老板拍板: 板框 U-1 三选一 (★卡「对着哪个框画」★)** ⇒ ★**① B160x100 台架板 (160.00×100.00 / 8 层) / ② F30A 产品板 (60.00×30.00 / 6 层 / 板厚 ≤1.00) / ③ P60x15 (60.00×15.00)★** ⇒ ★**main 本机实跑 36 档 (3 框 × 板厚 4 × 层数 3)**: ① **36 档全红** (V 链 −68.00 / L 链 −85.50 · 与板厚无关 · 板重 47.36 g = 整机质量预算 65~97%) · ② 板厚 0.80/1.00 **两档全绿** (内腔 4.90/4.70 · V 链 +2.00/+1.40) · ③ **整档作废** (套 A 四孔在 15 mm 板上不成立) ⇒ ★**建议默认值 = ② 60×30 + 板厚 ≤1.00 (★唯一在结构判据上全绿的一档·代价见 §E-1★) ⇒ 不代拍** ★",
    "③ ★**老板拍板: 今日新增的 2 条板级轴 (★都挂在 `to=main` ⇒ advance.py 的 decisions 段读不到★)** ⇒ ★**D-1-7 =「板只改一次」这句话约束哪块板 (现役 B160x100 还是产品板 F30A) · D-2-9 = 电芯采购型号最终选哪颗 (`ICP422339PR` 4.6 mm vs `ICP582035PR-01` 6.4 mm)★** ⇒ ★**D-2-9 不拍 ⇒ 照现型号买 ⇒ 到货厚 6.40 mm ⇒ 装不进 7.30 mm 镜脚 ⇒ 电芯段 H 链最坏 −1.10 mm ⇒ 这笔损失远大于任何文档订正本身** ★",
    "④ ★**G1 仍开, 不许投板 (★阶段门实跑★)】** ⇒ ★**当前 G1 · 还差 1 项**: PCB 布线 unconnected **45 → 0** (DRC 违规 **0** 已达标 · ISS-181) ⇒ ★**G1a 还差 2 条**: G1a-4 (落表已清零 · 翻面口径) + G1a-8 (关机语义 + 负载开关选型已决) ⇒ ★**巡检 rc=3 的两条老账**: `check_pcb_nets` rc=1 (网表 480 / 板上 482 · 多余 2 · 同号异网 3 ⇒ 板是旧网表的板) + `chain_gate` rc=1 (③ PCB 准入 + ⑤ 投产包准入 ⇒ 投板用的是旧板 Gerber) ⇒ ★**两条都是「板那一趟」本体, 板重出时一起清** ★",
    "⑤ ★**在飞 3 条 (★2026-11-18 09:16~09:17 实测 · 兄弟 job fb67af40 派出 · 三个 agent 各 1 个 running 写会话 · 真在飞不是僵尸★)】** ⇒ ★**① ISS-317 → hw-lead** (S1 位号改名三侧同口径可执行清单 + NC 白名单三选项 + BOM 证据回填判据 · 零写板) · ★**② ISS-318 → sw-lead** (SW 侧位号引用影响面闸 + 挂链前体检 · 零写板) · ★**③ ISS-320 → mech-lead** (电芯型号订正实做 33 行 · 受限文本订正 · 零写板) ★ ⇒ ★**A 段 internal = 0 的根因 = 三总工名下 open 全 0 (真空) + 各自 1 个 fixing 在飞 ⇒ 本 job 不重复派 (铁律)** ★",
    "⑥ ★**待拍板面 = 39 条 (★`advance.py --json` 实读★) · 本 job 一封信没发 · 没推 GitHub** ⇒ ★**approvals 段恒空** (★老板 2026-11-12 02:02「不再发信, 全靠自己查资料」· `state/outbox/` 19 份 .md + 3 份 attach 一律只留档不发★) ⇒ ★**5 条今日退休** (★iss091_rilim_decision / iss091_worn_while_charging / iss100_board_length / iss099_poka_yoke_decision / iss099_rilim_300_dead · mech-lead ISS-313 于 06:13 处置 · 退休依据见 §F-1★) ⇒ ★**另有 11 条 boss-facing need 在 `decision_truth` 里已判过 ⇒ 不再重复问** ⇒ ★**只落本地快照 `PROGRESS_SNAPSHOT.md` (09:32 rc=0) · GitHub 由 5 小时同步 job 负责** ★",
]


def main() -> int:
    txt = open(TASK, encoding="utf-8").read()
    lines = txt.split("\n")

    # 找老待办块 (① .. ⑥ 开头的那几行)
    idx_todo = []
    for i, l in enumerate(lines):
        s = l.strip()
        if s[:1] in ("①", "②", "③", "④", "⑤", "⑥") and len(s) > 1:
            idx_todo.append(i)
    if not idx_todo:
        print("★找不到待办块 ⇒ 不动")
        return 2
    lo, hi = min(idx_todo), max(idx_todo)
    # 待办块必须连续
    assert list(range(lo, hi + 1)) == idx_todo, "★待办块不连续 ⇒ 停手"

    shutil.copy2(TASK, BAK)

    old_head = lines[0]
    old_todo = lines[lo:hi + 1]

    new_lines = []
    new_lines.append(NEW_HEAD)
    new_lines.append("★★**【2026-11-18 01:1x (cron 775d9893 本机实跑) · 本轮两件实事】★★** ⇒ ★**① ISS-302 (C_SYS/SYS_CHG 必装落表) = main 独立复验通过 → `verified`** (★交卷单 38,212 B · 占位符 0 · 分片 12 条 · 板 md5+mtime 双证零写板·★但「验签 ≠ 现在就绿」⇒ 钉板闸⑥ 仍红★) ⇒ ★**② 派了 ISS-304 → hw-lead** (★钉板闸⑥ 作业包现状值重锚·零写板·零落表·先落 fixing 再 spawn·会话 advance_iss304 running★) ⇒ ★★**【板那一趟开工前的【机器前置】(★本 job 01:0x 实跑★)】★★ ⇒ ★**Q7 钉板 md5 闸链 = 8/9 ⇒ 红的钉板闸⑥ (ISS-304) 必须先回绿 ⇒ 那是已派出去的内部活·不用你管** ⇒ ★★**【还卡在你手上的 = 决策页 §A-补22 ② 那 7 条 (★原样保留·本轮一个字没改★)】** ⇒ ★**本轮待拍板面 44 条一条没动 (★44/44 逐 key 核过·脚本跑★) ⇒ 你不用做任何新决定** ⇒ ★**其中 `iss206_...scheme_choice` 与 `boss_dled_g_expose_decision_20261117` 今天是 due 11-18**★ ⇒ ★★**【在飞 2 条】** ⇒ ★**ISS-304 → hw-lead** (★钉板闸⑥ 重锚★) · ★**ISS-303 → mech-lead** (★MECH 侧 N6 只认硬基线不认合法落表跳·01:0x 已转绿待交卷★) ⇒ ★★**【板面零变化】**: 板 `611b869e…` · `.kicad_pro` `3e504d2b…` ⇒ **G1 仍开, 不许投板** ★★")
    # 老第 1 行原字保留 (留痕) —— 已含 01:1x 块, 故上面那行是显式留痕副本
    new_lines.append(old_head)
    new_lines.extend(lines[1:lo])
    # 老待办降级成注释 (留痕, board_progress.py 会过滤 '#' 开头的行)
    for l in old_todo:
        new_lines.append("# ★★[留痕 · r68 之前的待办块 (★2026-11-12 ~ 11-18 01:1x · 原字保留·已过期·★不要照着做★)]★★ " + l)
    new_lines.extend(NEW_TODOS)
    new_lines.extend(lines[hi + 1:])

    out = "\n".join(new_lines)
    with open(TASK, "w", encoding="utf-8") as f:
        f.write(out)

    # 自证: 跑一遍 board_progress.py 的解析口径
    ls = [l.strip() for l in out.splitlines() if l.strip() and not l.strip().startswith("#")]
    cur = ls[0]
    todos = [l for l in ls[1:] if not l.startswith("★")]
    print("✅ state/CURRENT_TASK.md 已更新 (r68)")
    print("   当前在做 (第 1 行) = %d 字" % len(cur))
    print("   待办清单 = %d 条" % len(todos))
    for i, t in enumerate(todos, 1):
        print("     %d) %s" % (i, t[:46]))
    print("   老待办块已降级为注释 (留痕) = %d 行" % len(old_todo))
    print("   备份 = %s" % os.path.basename(BAK))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
