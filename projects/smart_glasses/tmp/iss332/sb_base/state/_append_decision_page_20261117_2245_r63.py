#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
moli (项目总工) 2026-11-17 22:4x · job 775d9893「ARS45 继续执行后继计划」
★决策页追加 §A-补25 (r63) ★
=========================================================================================
★**本段写什么 (★main 本机实读盘面 + 实跑 rc + sessions_list 实查会话状态·不抄任何 agent 报告★)**:
  · ① 本轮内部推进 (★internal 段本轮为空 ⇒ 派 0 条 · 两条 fixing 单的会话状态实查★)
  · ② 待拍板面: 44 条一条没动 (44/44 脚本逐 key 复核) + 「板那一趟必须拍」7 条短名单的建议默认值原样保留
  · ③ 阶段门 / 链门 / 巡检 rc (main 22:3x~22:4x 本机实跑)
  · ④ 一条【更正】: r62 §④ 写的两个会话号在 r62 落笔前 80 分钟就已死 ⇒ 现役是 cont1 会话
★**边界**: ★**只追加决策页一个文件** (★老字一行不删·追加式★) ⇒ 不碰 issue_log / 分片 / 板 / 网表 / 脚表 / BOM / outbox ★
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
PAGE = os.path.join(PROJ, "DECISION_PENDING_2026-11-16.md")
BAK = PAGE + ".bak_20261117_2245_r63"

SEC = """

---

## §A-补25 · ★★r63 · 2026-11-17 22:4x · ★★★**本轮 internal 段仍为空 (派 0 条) + 待拍板面 44 条一条没动 (44/44 脚本复核) + ★★一条【更正】: r62 §④ 写的两个会话号在 r62 落笔前 80 分钟就已死 ⇒ 现役 = cont1 会话 (018e190a / 9fc3d633)**★★★ (★cron 775d9893 本机实跑★)

### ★① 本轮内部推进 (★main 22:3x~22:4x 本机实查盘面 + `sessions_list` 实查会话状态, 不抄任何交卷报告★)

★| 单号 | owner | 状态 | 本轮发生了什么 | ★
|---|---|---|---|---|
| ★**ISS-299** ★ | hw-lead | **fixing (在飞)** | ★**H-1 重锚第 2 跳**: 9 道钉板 md5 闸里唯一红的那道挂进门禁链 ⇒ ★**兄弟 job fb67af40 于 22:2x 派了 cont1 续做**: 会话 `agent:hw-lead:subagent:018e190a-7fc4-4f34-a69d-8b39fc702e26` (★22:34 起 · status=**running** · ★闸本体已做完, 只差交卷单 §⑰-2 一行回归读数★) ⇒ ★**本 job 不重复派 (★已标 fixing 的不重复派 + 一个 agent 同时只能有一个写会话★)** ★ |
| ★**ISS-300** ★ | mech-lead | **fixing (在飞)** | ★**MECH 侧准出汇总闸**: 新闸主跑 rc=0 (绿 6/红 0) · `--selftest` rc=0 (反向用例 ⑥ 真沙盒真篡改 ⇒ 红 1 道并点名) ⇒ ★**兄弟 job fb67af40 于 22:2x 派了 cont1 续做**: 会话 `agent:mech-lead:subagent:9fc3d633-1561-411e-a84b-678228c6ded2` (★22:35 起 · status=**running** · ★闸本体已做完, 只差交卷单 B0~B6 paperwork★) ⇒ ★**本 job 不重复派 (同上)** ★ |
| ★**sw-lead** ★ | sw-lead | **队列真空** | ★**名下 open = 0** ⇒ 无活可派 ★ |

★★**★一条【更正】(★本 job 22:3x `sessions_list` 实查·不是推测★)★**: ★**r62 §④ 写的两个会话号 `008bc381` / `e2720689` 在 r62 落笔 (22:1x) 之前【早就死了】—— `endedAt` = 21:59:41 / 21:59:40 (★相差 81 ms ⇒ 父 run 被掐·子被连带杀掉·不是各自撞超时★) ⇒ r62 那句「★真在飞, 不是僵尸★」是读到了过期会话表 ⇒ ★**以本节为准: 现役会话 = cont1 `018e190a` (hw-lead) + `9fc3d633` (mech-lead)★** ★

### ★② ★★待拍板面: 44 条一条没动 (★44/44 脚本逐 key 复核·不是目测★)★★

- ★**`state/advance.py --json` 实跑 ⇒ `decisions` = **44** 条 (★与 r61 / r62 完全一致·0 新增 / 0 退休 / 0 改建议默认值★)** ★
- ★**44/44 覆盖**: ★**本 job 22:3x 脚本逐 key 在本页正文里查命中 ⇒ 命中 44 / 缺失 0** ★
- ★**分布 (★本 job 22:3x 实测★)**: ★**逾期 33 条 · 剩 1 天 2 条 (★`iss206_mech_claim_mainboard_len_carrier_direct_scheme_choice` + `boss_dled_g_expose_decision_20261117` · due 11-18★) · 无 due 9 条** ★
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

### ★③ 阶段门 / 链门 / 巡检 (★main 22:3x~22:4x 本机实跑·原样 rc★)

| 项 | rc | 读数 |
|---|---|---|
| ★`state/merge.py` ★ | ★**0** ★ | ★STATE.yaml 刷新 (22:40:39) · 产出 551 · 阻塞 43 · 冲突 0 · 健康度 red ★ |
| ★`state/gate_check.py` ★ | ★**0** ★ | ★Q1 交付齐备率 18/18 · Q6 硬件真源闸 ✅ · ★**Q7 钉板 md5 闸链 9/9 道绿** (★r62 挂载那 9 道本轮仍全绿★)★ · 缺口清单 3 条 (★hw 136 / sw 75 / mech 102 条需求还没人答★) ★ |
| ★`state/issue_check.py` ★ | ★**0** ★ | ★问题闭环门全过 (★296 条 · 逾期 0 · 违规 0 · 内部 265 / 外部 31★) ★ |
| ★`state/stage_gate.py` ★ | ★**1** ★ | ★当前 **G1 原理图 / PCB 定稿** · 还差 **1** 项 (★PCB 布线 unconnected 45 → 0 (ISS-181)★) · ★**G1a 独立闸还差 2 条: G1a-4 / G1a-8**★ ★ |
| ★`state/daily_check.py` ★ | ★**3** ★ | ★异常 2 条 (★与 r62 同·两条老账★): ① **PCB↔网表逐焊盘等价没过** (`check_pcb_nets` rc=1) ② **生产链准入/准出没过** (★chain_gate: 环 ③ PCB 准入红 ⇒ 环 ⑤ 连带红★) · 漂移: 内部未闭合 315 · 问题单 296 · 未闭环 blocker 10 ★ |
| ★板 md5 / mtime ★ | — | ★**`611b869e13518c3c023fb178f91a0075` · mtime 仍 `2026-11-06 07:07:17` ⇒ 零写板仍成立** (★`.kicad_pro` `3e504d2b…` · 网表 `37f62ac3…` · 脚表 `a4270120…` · BOM `5d02bece…` 逐字节不变★) ★ |

### ★④ 本 job 本轮派活口径 (★`state/advance.py --json` 实跑 + `sessions_list` 实查★)

- ★**22:36 `advance.py --json` ⇒ `internal: []` / `approvals: []` / `decisions: 44` / `waiting: []`** ★
- ★**⇒ 本 job 本轮净派活 = 0 条** (★原因 = 两个 owner 名额各被 1 条 `fixing` 占着 + `sessions_list` 实查两个 agent 各有 1 个 running 写会话 ⇒ 铁律「一个 agent 同时只能有一个写会话」⇒ 不重复派·不撞兄弟 job 的车★) ★
- ★**★板块归类 (★老板 2026-11-17 00:43「PCB 类先派【纯分析 / 作业包】类」纪律★)**: ★**本轮【零派活】⇒ 本轮无新增 PCB 类任务** ★
  ★**在飞的两条 (★本 job 只汇报·不重复派★)**: ★**ISS-299** (★HW 侧 · H-1 重锚第 2 跳·门禁机制类★) + ★**ISS-300** (★MECH 侧 · 准出汇总闸·门禁机制类★) ⇒ ★**两条都是【零写板 · 零落表 · 不动网表真源】⇒ 不属「真动板那一趟」⇒ 符合纪律** ★
- ★**★零外发**: ★**本 job 全程没发任何邮件 / 询价 / 采购 / 联系供应商** (★老板 2026-11-11 19:31 + 2026-11-12 02:02 政策★) ⇒ ★**`approvals` 段本轮恒为空 (0 条·与政策一致) ⇒ outbox 19 份 .md (★其中 3 份是 policy / README / 决策图 ⇒ 真外发草稿 16 份·只备不发·零缺失·`NO_OUTBOUND_POLICY.md` 在位★)** ★
- ★**★GitHub**: ★**本 job 不推 (★老板 2026-11-11 09:5x 口径 ⇒ 由独立 job `ARS45 GitHub 同步 (每 5 小时 · 有进展才推)` 负责★) ⇒ 本 job 只落本地快照 `PROGRESS_SNAPSHOT.md` (4993 B · 22:41)** ★
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
    print("OK 决策页已追加 §A-补25 (r63)")
    print("  老字节 %d → 新字节 %d (+%d)" % (len(old.encode()), len(new.encode()), len(new.encode()) - len(old.encode())))
    print("  备份: %s" % os.path.basename(BAK))
    print("  前缀逐字节校验: OK")


if __name__ == "__main__":
    main()
