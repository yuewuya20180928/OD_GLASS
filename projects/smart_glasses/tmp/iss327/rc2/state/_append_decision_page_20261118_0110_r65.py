#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
state/_append_decision_page_20261118_0110_r65.py
================================================================================
★**决策页追加 §A-补27 · r65 · 2026-11-18 01:1x · cron 775d9893 本机实跑** ★
★**追加式铁律: 老字一字不删 · 新段追加在文末** ★
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
PAGE = os.path.join(PROJ, "DECISION_PENDING_2026-11-16.md")

SECTION = """

---

## §A-补27 · ★★r65 · 2026-11-18 01:1x · ★★★**本轮派了 1 条 (ISS-304 → hw-lead · 钉板闸⑥ 作业包现状值重锚) + 验签 1 条 (ISS-302 → verified) + 待拍板面 44 条一条没动 (44/44 脚本复核) + ★★一条【发现】: 本轮扫出【落表跳假红】第 2 个洞 (ISS-304) ⇒ 「板只改一次」那一趟开工前必须先把闸修回绿**★★★ (★cron 775d9893 本机实跑★)

### ★① 本轮内部推进 (★main 01:0x~01:1x 本机实查盘面 + `sessions_list` / `subagents list` 实查会话状态, 不抄任何 agent 报告★)

★| 单号 | owner | 状态 | 本轮发生了什么 | ★
|---|---|---|---|---|
| ★**ISS-304** ★ | hw-lead | ★**fixing (本轮新派)** ★ | ★**钉板闸⑥ 作业包现状值闸重锚** ⇒ 会话 `agent:hw-lead:subagent:15263ad3` (★taskName `advance_iss304` · 01:1x 起 · status=**running**·已实测在跑★) ⇒ ★**纯文档/闸侧 · 零写板 · 零落表 · 不改判据** ★ ⇒ ★**先落 fixing 再 spawn (★同一个 flock 内原子完成·中间不留 open 窗口⇒兄弟 job fb67af40 不会重复派★)** ★ |
| ★**ISS-302** ★ | hw-lead | ★**verified (本轮验签)** ★ | ★**C_SYS / SYS_CHG 必装落表** (★TI bq25896 SLUSC76C §7 逐字『Connect a 20uF closely to the SYS pin.』★) ⇒ ★**cont1 于 01:03 交卷 (交卷单 38,212 B) ⇒ main 01:0x 独立复验通过 ⇒ 01:1x 落 verified** ★ ⇒ ★**★这就是 hw-lead 名额释放的原因 ⇒ 才有 ISS-304 可派★** ★ |
| ★**ISS-303** ★ | mech-lead | **fixing (兄弟 job 01:1x 已派, 本 job 不重复派)** | ★**MECH 侧 N6 只认硬基线·不认合法落表跳** ⇒ 会话 `agent:mech-lead:subagent:9d1a4f90` (★status=**running**★) ⇒ ★**main 01:0x 复跑已转绿 rc=0 (★是 ISS-303 那侧动的·不是别的单★)★** ★ |
| ★**ISS-300** ★ | mech-lead | **verified (兄弟 job 01:1x 已验签)** | ★**MECH 侧准出汇总闸** ⇒ ★**main 复核: 交卷单 25,996 B · 占位符 0 · B0~B6 齐全 · 分片 12 条 · `--selftest` rc=0** ★ |
| ★**sw-lead** ★ | sw-lead | **队列真空** | ★**名下 open = 0 · fixing = 0** ⇒ 无活可派 ★ |

★**★派活口径 (★板块归类·★老板 2026-11-17 00:43「PCB 类先派【纯分析 / 作业包 / 门禁机制】类」纪律★)★**: ★**本轮派的 1 条 = `ISS-304` ⇒ 归类 = 【现状值重锚类 · 纯文档/闸侧 · 零写板 · 零落表】⇒ 不属「真动板那一趟」⇒ 符合纪律** ★ ★**本轮验签的 1 条 = `ISS-302` ⇒ 归类 = 【落表链侧 · 零写板 (CHG_BOARD 无 PCB 文件)】⇒ 同样不构成「板改第二次」** ★

### ★② ★★待拍板面: 44 条一条没动 (★44/44 脚本逐 key 复核·不是目测★)★★

- ★**`state/advance.py --json` 实跑 ⇒ `decisions` = **44** 条 (★与 r61 / r62 / r63 / r64 完全一致·0 新增 / 0 退休 / 0 改建议默认值★)** ★
- ★**44/44 覆盖**: ★**本 job 01:1x 脚本逐 key 在本页正文里查命中 ⇒ 命中 44 / 缺失 0** ★
- ★**分布 (★本 job 01:1x 实测★)**: ★**逾期 33 条 · 剩 0~2 天 2 条 (★`iss206_mech_claim_mainboard_len_carrier_direct_scheme_choice` + `boss_dled_g_expose_decision_20261117` · due 11-18★) · 无 due 9 条** ★ · ★**来源分片: hw 8 / mech 18 / pm 10 / sw 8** ★
- ★**「板那一趟」开工前【必须拍】的 7 条短名单: ★**仍在 §A-补22 ② · 原样保留 · 本轮一个字没改** ★
  ★**建议默认值 (★main 给·只列选项与代价·老板一句话确认·不代拍★)** ★
  1. ★`boss_esd_model_axis_pending_20261117` ★ ⇒ ★**D− 侧补 ⇒ 双通道 (2 脚 → 3 脚)** ★
  2. ★`boss_c_vbus_gnd_reserve_pad_20261117` ★ ⇒ ★**(a) 下板** (★板↔网表等价闸「多余 2」自动清零★) ★
  3. ★`boss_dled_g_expose_decision_20261117` ★ ⇒ ★**(b) 不外露** (★代价最小·不压 SoM★) ★
  4. ★`boss_shutdown_semantics_and_loadswitch_20261117` ★ ⇒ ★**照建议: A4 = C + A · A5 = 追认 `TPS22991RAA`** ★
  5. ★`board_p41_promote` ★ ⇒ ★**(a) 不换** (★换的收益是 4 条 unc·代价是全基线重锚★) ★
  6. ★`iss100_board_length` ★ ⇒ ★**(a) 60** ★
  7. ★**作业包 §7 的 P7 (板框/层数/放行 C1~C4)** ★ ⇒ ★**(a) C4** (★若时间窗只够拍一个·C4 是唯一能让这一趟【不白跑】的选项★) ★
- ★**★不替老板拍板**: ★**44 条待拍板项一条没动 · 只给选项 / 代价 / 建议默认值** ★

### ★③ 阶段门 / 链门 / 巡检 (★main 01:0x 本机实跑·原样 rc★)

| 项 | rc | 读数 |
|---|---|---|
| ★`state/merge.py` ★ | ★**0** ★ | ★STATE.yaml 刷新 (★01:0x★) · 产出 552 · 阻塞 43 (高危 33) · 未闭合需求 316 · 冲突 0 · 健康度 red ★ |
| ★`state/gate_check.py` ★ | ★**1** ★ | ★Q1 交付齐备率 **18/18** · ★**Q7 钉板 md5 闸链 8/9 绿** ⇒ ★**红 = 钉板闸⑥ 作业包现状值闸 (★归 ISS-304·本轮已派出·不是别的单★)⇒ 板那一趟不许开工**★ · Q6 硬件真源闸 ✅ · 接口声明 857 条 ★ |
| ★`state/issue_check.py` ★ | ★**0** ★ | ★问题闭环门全过 (★300 条 · 逾期 0 · 违规 0★) ★ |
| ★`state/stage_gate.py` ★ | ★**1** ★ | ★当前 **G1 原理图 / PCB 定稿** · 还差 **1** 项 (★PCB 布线 unconnected 45 → 0★) · ★**G1a 独立闸还差 2 条: G1a-4 / G1a-8**★ ★ |
| ★`state/daily_check.py` ★ | ★**3** ★ | ★异常 2 条 (★老账★): ① **PCB↔网表逐焊盘等价没过** (`check_pcb_nets` rc=1 · ★网表 480 / 板上 482 · 缺失 0 · 多余 2 · 同号异网 3★) ② **生产链准入/准出没过** (★chain_gate: 环 ③ PCB 准入红 ⇒ 环 ⑤ 连带红★) · 漂移: 问题单 297 → 300 ★ |
| ★板 md5 / mtime ★ | — | ★**`611b869e13518c3c023fb178f91a0075` · mtime 仍 `2026-11-06 07:07:17` ⇒ 零写板仍成立** (★`.kicad_pro` `3e504d2b…`★) ★ |
| ★本 job 落地快照 ★ | **0** | ★`PROGRESS_SNAPSHOT.md` (★01:03 重出·本地·不推★) ★ |

### ★④ ★★本轮挖出的【落表跳假红】第 2 个洞 ⇒ 「板只改一次」那一趟开工前必须先把闸修回绿★★ (★main 01:0x 本机实跑·原样 rc★)

★**2026-11-18 00:21 的 ISS-302 是【合法落表跳】(网表/脚表/BOM 三个 md5 变) ⇒ 凡是【只认硬基线】的闸都会当场假红** ★ ⇒ ★**本轮 3 处假红的分家 (★main 逐条实跑·不是抄任何 agent 报告★)★**:

| 闸 | rc | 红的成因 | 归属 |
|---|---|---|---|
| ★`HW/check_workpack_state_values.py` ★ | **1** | ★V4 4 条 `fresh` 原句停在 ISS-283 那一跳 (37f62ac3 / a4270120 / 5d02bce) ⇒ 没跟上 6aee500e / 9174309d / 5b999399★ | ★**ISS-304 (hw-lead · 本轮已派)** ★ |
| ★`MECH/check_onepass_struct_crosscheck.py` ★ | **1→0** | ★N6 只认 `PROTECTED_LEDGER_MD5` 硬基线常量 ⇒ 分不出「合法落表」与「有人手改」★ | ★**ISS-303 (mech-lead · 兄弟 job 已派·01:0x 已转绿)** ★ |
| ★`MECH/check_onepass_mech_release.py` (汇总) ★ | **1** | ★汇总 绿 5 / 红 1 ⇒ 红的那道就是上面那条 ⇒ 结构侧准出闸被假红挡住★ | ★**随 ISS-303 回绿** ★ |

★**★⇒ 一句话给老板**: ★**你不用做任何新决定 (★44/44 一条没动★) ⇒ 但【板那一趟】现在多了一道【机器前置】: 钉板闸⑥ 必须先回绿 (ISS-304 交卷) ⇒ 那是本 job 已派出去的内部活, 不用你管** ★ ★**⇒ 而真正还卡在你手上的, 仍是 §A-补22 ② 那 7 条 (★其中 `iss206_...scheme_choice` 与 `boss_dled_g_expose_decision_20261117` 今天是 due 11-18★)** ★

### ★⑤ 本 job 本轮口径 (★纪律自检★)

- ★**零外发**: ★**本 job 全程没发任何邮件 / 询价 / 问询 / 采购 / 联系供应商** (★老板 2026-11-11 19:31 + 2026-11-12 02:02 政策★) ⇒ ★**`approvals` 段本轮恒为空 (0 条·与政策一致) ⇒ outbox 19 份 .md 一份没少 (★3 份 policy/README/决策图 + 真外发草稿 16 份·只备不发·`NO_OUTBOUND_POLICY.md` 在位★)** ★
- ★**不写别的 agent 的分片**: ★**本 job 只写 `state/issue_log.yaml` (★验签 + 派活标记·同一个 flock 内原子完成★) + `state/dispatch_log.yaml` + 决策页 + 本地快照 ⇒ `hw.yaml` / `mech.yaml` / `sw.yaml` / `pm.yaml` 一个字节没碰** ★
- ★**GitHub**: ★**本 job 不推 (★老板 2026-11-11 09:5x 口径 ⇒ 由独立 job `ARS45 GitHub 同步 (每 5 小时 · 有进展才推)` 负责★) ⇒ 本 job 只落本地快照 `PROGRESS_SNAPSHOT.md` (01:03)** ★
- ★**不替老板拍板**: ★**44 条待拍板项一条没动** ★
- ★**一个 agent 同时只能一个写会话**: ★**派前 `sessions_list` + `subagents list` 实查 ⇒ hw-lead 名下无 running 写会话 (★上一条 01:03 status=done★) ⇒ 才派** ★ ★**派后 `subagents list` 复核 ⇒ 1 条 running (advance_iss304)· 一个 agent 一条· 无重复** ★
"""


def main() -> int:
    with open(PAGE, encoding="utf-8") as f:
        old = f.read()
    if "§A-补27" in old:
        print("★§A-补27 已在页内 ⇒ 幂等跳过")
        return 0
    bak = PAGE + ".bak_20261118_0110_r65"
    with open(bak, "w", encoding="utf-8") as f:
        f.write(old)
    with open(PAGE, "w", encoding="utf-8") as f:
        f.write(old.rstrip("\n") + "\n" + SECTION)
    print("✅ §A-补27 已追加 (老字 %d B → 新 %d B · 备份 %s)" % (len(old), len(old) + len(SECTION), os.path.basename(bak)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
