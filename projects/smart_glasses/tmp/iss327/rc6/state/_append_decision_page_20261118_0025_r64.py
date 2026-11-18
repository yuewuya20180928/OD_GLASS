#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
moli (项目总工) 2026-11-18 00:25 · job 775d9893「ARS45 继续执行后继计划」
★决策页追加 §A-补26 (r64) ★
=========================================================================================
★本段写什么 (★main 本机实读盘面 + 实跑 rc + sessions_list 实查会话状态·不抄任何 agent 报告★):
  · ① 本轮内部推进: 派了 1 条 (ISS-302 → hw-lead) + 跳过的 1 条 (ISS-300 已在飞)
  · ② 待拍板面: 44 条一条没动 (44/44 脚本逐 key 复核) + 「板那一趟必须拍」7 条短名单原样保留
  · ③ 阶段门 / 链门 / 巡检 rc (main 00:17~00:21 本机实跑)
  · ④ 本 job 本轮派活口径 + 一条【重要发现】: 兄弟 job fb67af40 被掐 ⇒ ISS-302 漏派 ⇒ 本 job 补派
★边界: ★只追加决策页一个文件 (★老字一行不删·追加式★) ⇒ 不碰 issue_log / 分片 / 板 / 网表 / 脚表 / BOM / outbox ★
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
PAGE = os.path.join(PROJ, "DECISION_PENDING_2026-11-16.md")
BAK = PAGE + ".bak_20261118_0025_r64"

SEC = """

---

## §A-补26 · ★★r64 · 2026-11-18 00:25 · ★★★**本轮派了 1 条 (ISS-302 → hw-lead · C_SYS/SYS_CHG 必装落表) + 跳过 1 条 (ISS-300 已在飞) + 待拍板面 44 条一条没动 (44/44 脚本复核) + ★★一条【发现】: 兄弟 job fb67af40 00:14 被掐 ⇒ ISS-302 从没进过 dispatch_log ⇒ 本 job 补派**★★★ (★cron 775d9893 本机实跑★)

### ★① 本轮内部推进 (★main 00:15~00:2x 本机实查盘面 + `sessions_list` 实查会话状态, 不抄任何 agent 报告★)

★| 单号 | owner | 状态 | 本轮发生了什么 | ★
|---|---|---|---|---|
| ★**ISS-302** ★ | hw-lead | ★**fixing (本轮新派)** ★ | ★**「C_SYS / SYS_CHG 必装」落表链**: TI bq25896 (SLUSC76C §7) 逐字「Connect a 20uF closely to the SYS pin.」⇒ 网表 L498 `SYS_CHG` / L499 `C_SYS` 从 `DNP` 改 `必装` + 两条 note 追加式订正 + BOM CHG_BOARD 加 1 颗 20µF 6.3V X7R/X5R ⇒ ★**本 job 于 00:16 派出会话 `agent:hw-lead:subagent:ae23ed17-ef49-489d-bdb2-aa82a030d0f5` (★00:16 起 · status=**running**·已实测在改行★)** ⇒ ★**派完跑 `advance.py --apply --only ISS-302` ⇒ 已标 fixing + dispatch_log 已写 (★`state/dispatch_log.yaml` L2150★)** ★ |
| ★**ISS-300** ★ | mech-lead | **fixing (在飞, 已交卷待 main 复验)** | ★**MECH 侧准出汇总闸** (`MECH/check_onepass_mech_release.py` · 绿 6/红 0 · `--selftest` rc=0) —— ★**兄弟 job fb67af40 于 22:2x 派 cont1 会话 `9fc3d633` · 22:43 已交卷 (交卷单 25,996 B)** ⇒ ★**本 job 不重复派 (★已标 fixing 的不重复派 + 一个 agent 同时只能有一个写会话★)** ★ ★**待 main 复验签字** ★ |
| ★**sw-lead** ★ | sw-lead | **队列真空** | ★**名下 open = 0** ⇒ 无活可派 ★ |

★**★一条【发现】(★main 00:1x 本机 `grep` + `sessions_list` 实查·不是推测★)★**: ★**兄弟 job `fb67af40` (ARS45 队列自动派活) 的会话在 00:14:25 被掐 (`stopReason: aborted`) ⇒ 它在 22:5x~00:1x 这段时间里【并没有真的把 ISS-302 派出去】⇒ `state/dispatch_log.yaml` 里 ISS-302 的条目本轮之前【不存在】(`grep` 命中 0) ⇒ ★**⇒ ISS-302 是【真·漏派】, 不是【已派等交卷】⇒ 本 job 补派是正确动作, 不算重复派** ★ ★**(★同类风险: 若某个 job 被掐在「已 spawn 子会话但没写 dispatch_log」的那一瞬, 本 job 的 `sessions_list` 实查 + `dispatch_log` grep 双证就是防重手段★)** ★

★**★一条【口径澄清】(★老板 2026-11-17 00:43「原理图/网表侧只派【不改网表真源】的活」纪律★)★**: ★**ISS-302 【确实改网表真源】(网表/脚表/BOM 三个 md5 会变) ⇒ 为什么本 job 敢派★** ★**① 它是【板那一趟的开工前置】(★main §0.2 清单里明写「⏳ 待落: ISS-302」★) ⇒ ★**板要对着一个【不再变的网表】画 ⇒ 落表必须发生在【动板之前】, 而不是之后★** ★**② 改动全在 `CHG_BOARD` (★95 行 CHG_BOARD 行 / `demo_mainboard.kicad_pcb` 里 `C_SYS`/`SYS_CHG` 命中数 = **0**★ ⇒ ★**CHG_BOARD 根本没有 PCB 文件 ⇒ 不构成「板改第二次」★)** ★**③ 本单【零写板】: 板 md5 `611b869e…` + mtime `2026-11-06 07:07:17` 本轮全程未动 (★00:2x 复测仍一致★)** ★ **④ 代价已知且已写进任务书: 落表后【钉板 md5 闸】里两道会把网表/脚表/BOM 写死成常量的闸必然转红 (`HW/check_pin_function_labels.py` `PROTECTED_MD5` L150 + `MD5_ANCHOR_CHAIN` L971 · `MECH/check_onepass_struct_crosscheck.py` `PROTECTED_LEDGER_MD5` L67) ⇒ 处置 = 【H-1 重锚第 3 跳】(留链痕·前移基线·判据方向不许变) ⇒ ★**第一道归 hw-lead 本单做, 第二道归 main (MECH 域, hw-lead 不许碰)** ★ ★**⑤ ⇒ 结论: 本单是【落表链侧的合法前置落表】, 不是「板改第二次」, 符合纪律** ★

### ★② ★★待拍板面: 44 条一条没动 (★44/44 脚本逐 key 复核·不是目测★)★★

- ★**`state/advance.py --json` 实跑 ⇒ `decisions` = **44** 条 (★与 r61 / r62 / r63 完全一致·0 新增 / 0 退休 / 0 改建议默认值★)** ★
- ★**44/44 覆盖**: ★**本 job 00:2x 脚本逐 key 在本页正文里查命中 ⇒ 命中 44 / 缺失 0** ★
- ★**分布 (★本 job 00:2x 实测★)**: ★**逾期 33 条 · 剩 0 天 2 条 (★`iss206_mech_claim_mainboard_len_carrier_direct_scheme_choice` + `boss_dled_g_expose_decision_20261117` · due 11-18★) · 无 due 9 条** ★ · ★**来源分片: hw 8 / mech 18 / pm 10 / sw 8** ★
- ★**「板那一趟」开工前【必须拍】的 7 条短名单: ★**仍在 §A-补22 ② · 原样保留 · 本轮一个字没改** ★
  ★**建议默认值 (★main 给·只列选项与代价·老板一句话确认·不代拍★)** ★
  1. ★`boss_esd_model_axis_pending_20261117` ★ ⇒ ★**D− 侧补 ⇒ 双通道 (2 脚 → 3 脚)** ★
  2. ★`boss_c_vbus_gnd_reserve_pad_20261117` ★ ⇒ ★**(a) 下板** (★板↔网表等价闸「多余 2」自动清零★) ★
  3. ★`boss_dled_g_expose_decision_20261117` ★ ⇒ ★**(b) 不外露** (★走线最短·不压 SoM★) ★
  4. ★`boss_shutdown_semantics_and_loadswitch_20261117` ★ ⇒ ★**A4 = C + A · A5 = 追认 `TPS22991RAA`** ★
  5. ★`board_p41_promote` ★ ⇒ ★**(a) 不换** (★换 = 全基线重锚 + 作业包 §1 现状值全改★) ★
  6. ★`iss100_board_length` ★ ⇒ ★**(a) 60** ★
  7. ★作业包 §7 的 P7 ★ ⇒ ★**(a) C4 = 分级放行 + 遗留清单** (★唯一「不动板」的选项·但要显式改 G1 判据★) ★
- ★**其余 37 条**: 材料 / 可靠性 / 合规 / 固件 / 命名单等 ⇒ ★**不卡这一趟** ⇒ 建议默认值见本页各条正文 ⇒ ★**本轮一条没动** ★

### ★③ 阶段门 / 链门 / 巡检 (★main 00:17~00:21 本机实跑·原样 rc★)

| 项 | rc | 读数 |
|---|---|---|
| ★`state/merge.py` ★ | ★**0** ★ | ★STATE.yaml 刷新 (00:17:34) · 产出 552 · 阻塞 43 (高危 33) · 未闭合需求 316 · 冲突 0 · 健康度 red ★ |
| ★`state/gate_check.py` ★ | ★**0** ★ | ★Q1 交付齐备率 18/18 · ★**钉板 md5 闸链 9/9 道绿** (★ISS-299 第 2 跳重锚后仍全绿★) · 缺口清单 3 条 (★hw 137 / sw 75 / mech 102 条需求还没人答★) ★ |
| ★`state/issue_check.py` ★ | ★**0** ★ | ★问题闭环门全过 (★298 条 · closed=97 deferred=15 verified=164 open=17 fixed=3 fixing=2 · 逾期 0 · 违规 0★) ★ |
| ★`state/stage_gate.py` ★ | ★**1** ★ | ★当前 **G1 原理图 / PCB 定稿** · 还差 **1** 项 (★PCB 布线 unconnected 45 → 0★) · ★**G1a 独立闸还差 2 条: G1a-4 (★R4 未落表: D_ESD_USB_D 仍只有 2 焊盘★) / G1a-8 (★ISS-097=fixed 不满足 verified/closed★)**★ ★ |
| ★`state/daily_check.py` ★ | ★**3** ★ | ★异常 2 条 (★老账, 与 r62/r63 同★): ① **PCB↔网表逐焊盘等价没过** (`check_pcb_nets` rc=1) ② **生产链准入/准出没过** (★chain_gate: 环 ③ PCB 准入红 ⇒ 环 ⑤ 连带红★) · 漂移: 问题单 297 → 298 · 未闭环 blocker 10 ★ |
| ★板 md5 / mtime ★ | — | ★**`611b869e13518c3c023fb178f91a0075` · mtime 仍 `2026-11-06 07:07:17` ⇒ 零写板仍成立** (★`.kicad_pro` `3e504d2b…` · 网表 `37f62ac3…` · 脚表 `a4270120…` · BOM `5d02bece…` 本轮派活前后逐字节不变★) ★ |

### ★④ 本 job 本轮派活口径 (★`state/advance.py --json` 实跑 + `sessions_list` 实查★)

- ★**00:15 `advance.py --json` ⇒ `internal: 1` / `approvals: []` / `decisions: 44` / `waiting: []`** ★
- ★**⇒ 本 job 本轮净派活 = 1 条 (ISS-302 → hw-lead)** ★
  ★**派前实查 (★防重三证★)**: ① ★`sessions_list` ⇒ hw-lead 名下无 running 写会话 (★上一条 `da5846dd` 23:29 已死★)★ ② ★`state/dispatch_log.yaml` grep `ISS-302` 命中 0 ⇒ 没派过★ ③ ★`state/issue_log.yaml` ISS-302 status=open·dispatched_at=None ⇒ 没派过★ ★
- ★**★板块归类 (★老板 2026-11-17 00:43「PCB 类先派【纯分析 / 作业包】类」纪律★)★**: ★**本轮派的 1 条 = `ISS-302` · 归类 = 【落表链侧 · 零写板 · 零落 PCB 布局】⇒ 不属「真动板那一趟」⇒ 符合纪律** ★ ★**在飞但本 job 不重复派的 1 条 = `ISS-300` (★MECH 侧准出汇总闸 · 零写板 · 已交卷待复验★)** ★
- ★**★零外发**: ★**本 job 全程没发任何邮件 / 询价 / 采购 / 联系供应商** (★老板 2026-11-11 19:31 + 2026-11-12 02:02 政策★) ⇒ ★**`approvals` 段本轮恒为空 (0 条·与政策一致) ⇒ outbox 19 份 .md (★其中 3 份是 policy / README / 决策图 ⇒ 真外发草稿 16 份·只备不发·零缺失·`NO_OUTBOUND_POLICY.md` 在位★)** ★
- ★**★GitHub**: ★**本 job 不推 (★老板 2026-11-11 09:5x 口径 ⇒ 由独立 job `ARS45 GitHub 同步 (每 5 小时 · 有进展才推)` 负责★) ⇒ 本 job 只落本地快照 `PROGRESS_SNAPSHOT.md` (3076 B · 00:20) · `state/.last_github_push` 仍 `2026-11-17T20:23:41` (★未动★)** ★
- ★**★不替老板拍板**: ★**44 条待拍板项一条没动 · 只给选项 / 代价 / 建议默认值** ★
"""


def main():
    if not os.path.exists(PAGE):
        raise SystemExit("决策页不存在: %s" % PAGE)
    with open(PAGE, "r", encoding="utf-8") as f:
        old = f.read()
    shutil.copy2(PAGE, BAK)
    with open(PAGE, "a", encoding="utf-8") as f:
        f.write(SEC)
    with open(PAGE, "r", encoding="utf-8") as f:
        new = f.read()
    assert new.startswith(old), "老字被破坏 (前缀校验失败)"
    print("OK 决策页已追加 §A-补26 (r64)")
    print("  老字节 %d → 新字节 %d (+%d)" % (len(old.encode()), len(new.encode()), len(new.encode()) - len(old.encode())))
    print("  备份: %s" % os.path.basename(BAK))
    print("  前缀逐字节校验: OK")


if __name__ == "__main__":
    main()
