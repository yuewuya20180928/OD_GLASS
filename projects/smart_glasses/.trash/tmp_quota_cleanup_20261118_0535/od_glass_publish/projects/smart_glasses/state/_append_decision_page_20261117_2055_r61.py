#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
moli (项目总工) 2026-11-17 20:5x · job 775d9893「ARS45 继续执行后继计划」
★决策页追加 §A-补23 (r61) ★
=========================================================================================
★**本段写什么 (★main 本机实读盘面 + 实跑 rc · 不抄任何 agent 报告★)**:
  · ① 本轮内部推进 (★internal 段本轮为空 ⇒ 派 0 条 · 两条 fixing 单的会话状态实查★)
  · ② 待拍板面: 44 条一条没动 (44/44 全覆盖) + ★**本轮新发现: 9 道板 md5 闸只有 1 道在门禁链上**★
  · ③ 阶段门 / 链门 / 巡检 rc (main 20:4x 本机实跑)
  · ④ 本 job 派活口径 + 零外发 + GitHub 不推
★**边界**: ★**只追加决策页一个文件** (★老字一行不删·追加式★) ⇒ 不碰 issue_log / 分片 (★except 已单独
  用 frag_write 原子写登记 1 条 main need·那是有意的·见 §A-补23 ②★) / 板 / 网表 / 脚表 / BOM / outbox ★
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
PAGE = os.path.join(PROJ, "DECISION_PENDING_2026-11-16.md")
BAK = PAGE + ".bak_20261117_2055_r61"

SEC = """

---

## §A-补23 · ★★r61 · 2026-11-17 20:5x · ★★★**本轮 internal 段为空 (派 0 条) + 待拍板面 44 条一条没动 + ★★本轮新发现: 「9 道钉板 md5 闸」代码级通道 9/9 已齐, 但【门禁链挂载只有 1/9】⇒ 那 8 道闸漂了每日巡检一个字都不会报**★★★ (★cron 775d9893 本机实跑★)

### ★① 本轮内部推进 (★main 20:4x~20:5x 本机实查盘面, 不抄任何交卷报告★)

★| 单号 | owner | 状态 | 本轮发生了什么 | ★
|---|---|---|---|---|
| ★**ISS-296** ★ | mech-lead | **fixing (会话 20:38:18 timeout ⇒ 僵尸)** | ★**MECH 侧 2 道闸接「合法改板」通道**: 会话 `e8cb142c` (run `57f0c72f`) · 交卷单 `HANDOFF/2026-11-17_mech-lead_ISS296_合法改板机制与收工重锚.md` **仍是 1197 B 骨架 (★6 件交付物全标 ⏳ / 正文「待填」★)** ⇒ ★**本 job 不派 (★已标 fixing 的不重复派 + 一个 agent 同时只能有一个写会话★) ⇒ 续做归兄弟 job fb67af40 的复验/续做轮** ★ | ★
| ★**ISS-297** ★ | hw-lead | **fixing (会话 20:38:18 timeout ⇒ 僵尸)** | ★**HW 侧 6 道闸接「合法改板」通道**: 会话 `b469ae7e` (run `57f0c72f`) · 交卷单 `HANDOFF/2026-11-17_hw-lead_ISS297_合法改板通道.md` **22542 B (★已填满·B1~B5 齐全★)** ⇒ ★**本 job 不派 (同上·兄弟 job 已接管僵尸续做轮)** ★ | ★
| ★**ISS-298** ★ | sw-lead | **verified** | ★**SW 侧 1 道闸**已交卷 + 已由 main 复验 → ★**`SW/tools/check_onepass_sw_sync.py` 是这 9 道里【唯一一道真挂在门禁链上】的 (★见 §A-补23 ②★)** ★ | ★

★**★本轮 `state/advance.py --json` 实跑 ⇒ `internal: []` (★空★) ⇒ ★**本 job 净派活 = 0 条** ★**
⇒ ★**原因不是没活, 是【名额被两个 fixing 单占着】+ 两条的会话同时 20:38:18 timeout ⇒ 僵尸 ⇒ 复验/续做归兄弟 job fb67af40 (★20:3x 那轮已在接管★) ⇒ ★**本 job 若此刻再派 = 同一个 agent 两个写会话并发 ⇒ 分片互相覆盖 (★本项目 R18 已知风险★) ⇒ 纪律上不许** ★

### ★② ★★待拍板面: 44 条一条没动 (★44/44 全覆盖·本 job 20:4x 逐 key 核过·脚本跑·不是目测★)★★

★**★`python3 state/advance.py --json` ⇒ `decisions` = **44** 条 (★与 r60 完全一致·一条没动·一条没删★) ★**
★**★决策页覆盖核对 (★main 20:4x 逐 key 脚本核★): 44 条里【44 条命中】决策页, 【0 条未命中】★** ★

★★**★★本轮新发现 (★main 本机实跑 + 逐文件读源码·不是抄任何 agent 报告★): 「9 道钉板 md5 闸」代码级通道 9/9 已建齐, 但【门禁链挂载只有 1/9】★★** ★

★★**★这 9 道闸 = 「板只改一次」那一趟 (S1~S13) 合法改板当天会【一起红】的那 9 道 (★机器生成清单: `state/board_md5_pinned_gates.md` + `.json` · 生成脚本 `state/_gen_board_md5_pinned_gates.py` · ★本 job 重跑生成器 ⇒ 与盘上【逐字节相同】⇒ 清单是准的★) ★** ★

| 项 | 本 job 实跑读数 |
|---|---|
| ★**代码级通道** ★ | ★**9/9 都有** (★`board_md5_pinned_gates.json` 的 `cls` 字段逐条 = 「★已有 reboard 通道★」★) ★ |
| ★**主模式实跑 rc** ★ | ★**8 道 rc=0 · 第 5 道 rc=1** (★HW 6: fsin_rootcause/g1a7_selection_landed/onepass_commit_order/onepass_preflight_coverage/**pin_function_labels rc=1**/workpack_state_values · MECH 2: board_frame_coords/demo_struct_truth · SW 1: onepass_sw_sync★) ★ |
| ★**★`state/gate_check.py` 的 `EXTRA_GATES` 实跑** ★ | ★**只有 2 条**: `MECH/check_mech_verdict_freshness.py` (★ISS-295★) + `SW/tools/check_onepass_sw_sync.py` (★ISS-298★) ⇒ ★**9 道板 md5 闸里【只有 SW 那 1 道】在链上★** ★ |
| ★**★`state/daily_check.py` 直接跑的 15 个脚本** ★ | ★**一道都不是这 9 道** (★chain_gate/check_pcb_drc/check_pcb_nets/check_sch_erc/check_sch_pinfull/check_stage_g1a/compare_arm_official/decision_truth/gate_check/issue_check/margin_sweep_gate/merge/readiness/stage_gate/daily_check★) ⇒ ★**⇒ 那 8 道闸漂了/坏了, 每日巡检【一个字都不会报】★** ★ |
| ★**`state/land_v_values.py` 的 `ALL_GATES` (落表后全闸扫描)** ★ | ★**只有 3 道**是这 9 道 (★onepass_commit_order / onepass_preflight_coverage / MECH check_board_frame_coords★) ⇒ ★**其余 6 道也不在落表扫描里★** ★ |

★★**★⇒ 这正是 MEMORY 铁律④「第 N+1 次复现」**: ★**「新闸交卷后第一件事不是『验收通过』, 是【挂进门禁链 + 让它真的跑一次】」—— 20:0x 挂过 2 条 (ISS-295 / ISS-298) · 这 8 条漏挂★** ⇒ ★**⇒ 已经登记成 main 自己的 need (key 逐字 `main_9gates_not_in_gate_chain_20261117` · 写在 `state/fragments/pm.yaml` · 走 frag_write 原子写) ★** ★

★★**★★但【这一条不许被当成「main 挂一下就完了」】★★** ★
★**第 5 道 `HW/check_pin_function_labels.py` 现在主模式 rc=1** (★18 条既有缺陷基线 = 15 条脚表功能缺陷 + 3 条 md5 台账对账 · `--expect-known` 也 rc=1 · 成因 = `PROTECTED_MD5` 里网表/脚表/BOM 三个基线还停在 ISS-257 时的旧值, 而 ISS-283 于 11-17 12:30 落表后真盘已是新值★)
⇒ ★**⇒ 它一挂进门禁链, 链当场红 ⇒ ⇒ 这是【要带「已知红基线豁免」一起做】的改动 (★判据不许松: 只豁免【已登记的既有缺陷条数】·其余仍红★), 或先修那 3 条 md5 基线 (★ISS-297 交卷单 B5 已把这条列为未决并明写「留给 main 拍板」★)** ★
⇒ ★**★⇒ 这条属于【main 自己裁决】, 不属老板拍板面 (★上面 44 条一条没动·本条不进老板清单★) ⇒ 本 job 只登记 + 汇报, 不代做★** ★

### ★③ 阶段门 / 链门 / 巡检 (★main 20:4x 本机实跑·原样 rc★)

| 项 | rc | 读数 |
|---|---|---|
| ★`state/merge.py` ★ | ★**0** ★ | ★STATE.yaml 已刷新 (20:42:46) · 产出 540 · 阻塞 43 (高危 33) · 未闭合需求 305 · 冲突 0 · 健康度 red ★ |
| ★`state/gate_check.py` ★ | ★**0** ★ | ★Q1 交付齐备率 18/18 · 缺口清单 3 条 (★hw 133 / sw 75 / mech 96 条需求还没人答★) · ★**extra_gates 只有 2 条 (见 §A-补23 ②)★** ★ |
| ★`state/issue_check.py` ★ | ★**0** ★ | ★问题闭环门全过 (★294 条 · 逾期 0 · 违规 0·内部 263 / 外部 31★) ★ |
| ★`state/stage_gate.py` ★ | ★**1** ★ | ★当前 **G1 原理图 / PCB 定稿** · 还差 **1** 项才能进 G2 (★G1 缺口 = PCB 布线 unconnected 45 → 0 (ISS-181)· ★★G1a 独立闸还差 2 条: G1a-4 / G1a-8★★★) ★ |
| ★`state/daily_check.py` ★ | ★**3** ★ | ★异常 2 条: ① **PCB↔网表逐焊盘等价没过** (★`check_pcb_nets` rc=1 · 走 `state/pcbnew_py.sh` 实跑: ★C1 红 = 网表 480 / 板上 482 · 缺失 0 · 多余 2 · 同号异网 3 · C2 全绿★) ② **生产链准入/准出没过** (★chain_gate: ③ PCB 准入红 (板与网表不等价) + ⑤ 投产包比原理图旧 + `doc/sch_src/` 与 `HW/PCB/` 不一一对应 (11 个内容不一致)★) ★ |
| ★板 md5 / mtime ★ | — | ★**`611b869e13518c3c023fb178f91a0075` · mtime 仍 `2026-11-06 07:07:17` ⇒ 零写板仍成立** ★ |

★★**★环境坑一条 (★本 job 实测踩到·已写进 need★)**: ★**`state/check_pcb_nets.py` 必须走 `bash state/pcbnew_py.sh`** —— 直跑 `python3 state/check_pcb_nets.py` 报 `ModuleNotFoundError: No module named 'pcbnew'` ⇒ ★**⇒ 「rc=1」有两种含义 (★真红 vs 环境缺模块★) ⇒ 以后谁报这条异常, 必须先确认走没走 pcbnew_py.sh★** ★

### ★④ 本 job 本轮派活口径 (★`state/advance.py --json` 实跑 + 会话实查★)

- ★**20:4x `advance.py --json` ⇒ `internal: []` / `approvals: []` / `decisions: 44` / `waiting: []` ★**
- ★**★⇒ 本 job 本轮净派活 = 0 条 ★** (★原因: 两个 agent 名额都被 `fixing` 单占着 (ISS-296 / ISS-297) ⇒ advance.py 的 `in_flight` 逻辑本就压住新派; 且两条会话 20:38:18 同时 timeout ⇒ 僵尸 ⇒ 复验/续做归兄弟 job fb67af40 ⇒ ★**本 job 不重复派 (★一个 agent 同时只能有一个写会话★)★** ★
- ★**★板块归类 (★老板 2026-11-17 00:43「PCB 类先派【纯分析 / 作业包】类」纪律★)**: ★**本轮【零派活】⇒ 本轮无新增 PCB 类任务** ★
  ★**当前在飞的 PCB 线两条 (★本 job 只汇报·不重复派★)**: ★**ISS-296** (★MECH 侧 2 道闸接合法改板通道 · 属【PCB 线·门禁机制类】· 零写板 · 零落表 · 不改网表真源★) + ★**ISS-297** (★HW 侧 6 道闸接合法改板通道 · 同款属性★) ⇒ ★**两条都【不属于】"真动板那一趟" ⇒ 符合纪律★** ★
- ★**★零外发**: ★**本 job 全程没发任何邮件 / 询价 / 采购 / 联系供应商** (★老板 2026-11-11 19:31 + 2026-11-12 02:02 政策★) ⇒ ★**`approvals` 段本轮恒为空 (★实跑 0 条·与政策一致★) ⇒ outbox 19 份草稿只备不发 (★`NO_OUTBOUND_POLICY.md` 在位★)★ ★
- ★**★GitHub**: ★**本 job 不推 (★老板 2026-11-11 09:5x 口径: 间隔 5 小时且有进展才推 ⇒ 由独立 job `ARS45 GitHub 同步 (每 5 小时 · 有进展才推)` 负责★) ⇒ 本 job 只落本地快照 `PROGRESS_SNAPSHOT.md` (★3076 B · 20:44★) ★**
- ★**★不替老板拍板**: ★**44 条待拍板项一条没动 · 只给选项/代价/建议默认值 (★其中「板那一趟开工前必须拍」的 7 条短名单在 §A-补22 ②, 本轮原样保留·未改一字★)** ★
"""


def main() -> int:
    if not os.path.exists(PAGE):
        print("⚠ 缺决策页: %s ⇒ 中止" % PAGE)
        return 1
    with open(PAGE, encoding="utf-8") as f:
        old = f.read()
    if "§A-补23" in old:
        print("· §A-补23 已存在 ⇒ 幂等跳过")
        return 0
    shutil.copy2(PAGE, BAK)
    with open(PAGE, "a", encoding="utf-8") as f:
        f.write(SEC)
    with open(PAGE, encoding="utf-8") as f:
        new = f.read()
    print("· 决策页追加 §A-补23 (r61): %d B → %d B (老字一字未删)" % (len(old), len(new)))
    print("· 备份: %s" % os.path.basename(BAK))
    print("· 老段完整性: 前 %d B 逐字节相同 = %s" % (len(old), new.startswith(old)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
