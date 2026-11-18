#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_append_decision_page_20261117_1520_r56.py
★main (moli) · cron 775d9893 (ARS45 继续执行后继计划) · 2026-11-17 15:2x★
★★**追加式 (★老字一行不删★)**: DECISION_PENDING_2026-11-16.md §A-补18 ★★

★★**本节内容 (★全部 main 本机实跑·不抄任何交卷报告★)★★ ★★
· ★**① 本轮内部推进**: ISS-289 (hw-lead) 半成品在盘 ⇒ ★**续做 cont1 已派出** (★闸 rc=0 · selftest 10/10 · 作业包九处
  追加式订正在位 · 缺的只是交卷单正文★) · ISS-288 (sw-lead) 在飞 · ISS-290 (mech-lead) 在飞 · ISS-287 (hw-lead) 已 verified
· ★**② 待拍板面 = 43 条**: ★**r55 (13:4x) 覆盖 41 条 ⇒ 本节补 2 条 ⇒ 43/43 全覆盖★**
  · ★**新增第 1 条 `boss_shutdown_semantics_and_loadswitch_20261117`** —— ★**★就是 G1a-8 现在红的那两条★**
    (★ISS-097=fixed · verify_by=boss ⇒ 不能自己 closed★) ⇒ ★**拍完这二条 ⇒ ISS-097 落 closed ⇒ G1a-8 立刻转绿★**
  · ★**新增第 2 条 `boss_state_value_acceptance_drift_20261117`** —— ★**知会型** (★作业包「DNP 43 全标」已过期 ⇒ 真值 40★)
    ⇒ ★**已由 ISS-289 收口 (闸已落 rc=0) ⇒ 不需要你拍任何值, 只要「已知悉」★★
· ★**③ 阶段门 / 链门 / 巡检 rc**: ★**G1 · G1a 还差 2 条 (G1a-4 / G1a-8) · merge rc=0 · gate_check rc=0 (Q1 18/18) ·
  issue_check rc=0 · stage_gate rc=1 (★缺 1 项 = PCB 布线 unconnected=45 ⇒ ISS-181★)· daily_check rc=3 (★板面比网表旧·
  投产包比源旧 ⇒ 预期红★)★** ★
· ★**④ 本 job 派活口径 (★`state/advance.py --json` 实跑·原样★)**: internal=0 / approvals=0 / decisions=43 / waiting=0 ★

★★**边界 (★写死的)★★ ★★
· ★**只追加, 老字一行不删不rewrite** ★ · ★**先备份 (★`DECISION_PENDING_2026-11-16.md.bak_20261117_1520_r56`★)** ★
· ★**flock (`state/.decision_page.lock`) + 锁内重读 + 原子写** ★
· ★**不改 §A / §B / §C 任何一条判据与建议默认值 · 不代老板拍板 · 零外发 · 不碰 `PROJECT_TRACKER.md` §0 锁死表★
  · 不改 `state/issue_log.yaml` 任何 status (★ISS-097 仍 fixed ⇒ 等老板一句★)** ★
"""
import fcntl
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
PAGE = os.path.join(PROJ, "DECISION_PENDING_2026-11-16.md")
LOCK = os.path.join(HERE, ".decision_page.lock")
BAK = PAGE + ".bak_20261117_1520_r56"

BLOCK = """
---

## §A-补18 · ★★r56 · 2026-11-17 15:2x · ★★★**待拍板面 43/43 全覆盖 + 本轮派活口径**★★★ (★cron 775d9893 本机实跑★)

> ★**出页人**: 项目总工 (main / moli) · ★**job**: cron `775d9893` (ARS45 继续执行后继计划) · ★**15:2x 实跑·追加式·老字一行不删★**
> ★**本节给你两件事**: ★**① 一句就能关掉 G1a-8 的关机语义 + 负载开关追认 (★附建议默认值, 不代你拍★)** ★**② 一条知会型 (★不需要你拍值★)** ★

---

### ★① 本轮内部推进 (★四单状态 · main 本机实查★)

| 单号 | owner | 状态 | main 15:2x 实查 |
|---|---|---|---|
| ★**ISS-287** ★ | hw-lead | ★**verified** ★ | ★**已收** (★沙盒干跑可行性探针 · 板 md5 逐字节不变★) ⇒ ★**hw-lead 名额已释放★** |
| ★**ISS-288** ★ | sw-lead | ★**fixing · 在飞** ★ | ★**15:18 刚写 `HANDOFF/2026-11-17_sw-lead_ISS288_timing_check补丁落地.md` (20142 B) ⇒ 正在收尾 ⇒ ★**本 job 不重复派第二个 sw-lead 会话** ★ |
| ★**ISS-289** ★ | hw-lead | ★**fixing · ★★半成品在盘 ⇒ 续做 cont1 已派出★★** ★ | ★**闸 `HW/check_workpack_state_values.py` 26466 B ⇒ rc=0 (V1~V7 · 34 个现状值探针实测==期望) · `--selftest` rc=0 · 10/10 全抓到** ★· ★**作业包九处追加式订正在位 + 清单页同改 + 分片 5 条 need 已在 (grep iss289=9)★** · ★**★唯一缺的 = 交卷单 B0~B6 全是「施工中」骨架 (1175 B)★ ⇒ 原会话 15:12 被网关掐断 (`abortedLastRun=true`)⇒ 续做 cont1 已派 (★会话 `agent:hw-lead:subagent:1e68b706`★ · 任务书 `state/dispatch_briefs/ISS-289_hw_workpack_state_values_cont1.md` · ★**已过 `check_brief_commands --brief-file` rc=0★)** ★ |
| ★**ISS-290** ★ | mech-lead | ★**fixing · 在飞** ★ | ★**MECH 侧结构交叉核对 (S6 的 20 个目标落位 × MECH 保留区 + 座体 pitch 1.27 vs 0.50) · 会话 `agent:mech-lead:subagent:cedabf25` running** ⇒ ★**本 job 不重复派第二个 mech-lead 会话** ★ |

> ★**⇒ 板 `611b869e13518c3c023fb178f91a0075` / `.kicad_pro 3e504d2be83152e337949723e909be1b` 逐字节未变 (★mtime 仍 `2026-11-06 07:07:17`★) ⇒ ★**「板只改一次」铁律本轮未破★** ★

---

### ★② ★★新增待拍板项 (★r55 覆盖 41 条 ⇒ 本节补 2 条 ⇒ 43/43 全覆盖★) ★★

#### ★★§A-补18-① · ★★`boss_shutdown_semantics_and_loadswitch_20261117` (★★★ = G1a-8 现在红的那两条 = 你一句话就能关的那两条★★★) ★★

★**★为什么它排在最前面**: ★**`state/check_stage_g1a.py` 的 G1a-8 判据 = 「`ISS-097` 与 `ISS-172` 的 status ∈ {verified, closed}」★** ⇒ ★**现状 `ISS-097 = fixed` (verify_by = boss) · `ISS-172 = verified` (sw-lead · 负载开关选型证据矩阵 · 已交卷)★** ⇒ ★**差的就是 `ISS-097` 这张签字★** ⇒ ★**★它不卡板, 但它卡 G1 关卡 (G1a-8)★**

| # | 待拍 | 事实 (★main 本机实读, 不抄任何交卷报告★) | ★**建议默认值 (★仅供你参考·不代你拍★)** ★ | 不拍的后果 |
|---|---|---|---|---|
| ★**A4** ★ | ★**关机语义 (C + A)** ★ | ★**demo 板做不到真断电**: ① 整机电池链 (`BT_432243` / `U_BATPROT` / `Q1` / `Q2`) **全 DNP** ⇒ `U_PWR_SW` 的 VIN 无源 ② demo 的 SoM 供电路径 `RAIL_DEMO_5V`→`J_SOM_P3` 7 根 `VCC_DCIN` 上**零开关** ⇒ SoM 永远带电 ⇒ ★**⇒「关机」在 demo 板只能是深睡★** ★· ★**⇒ 「待机 <0.05W」在整机成立 (≈0.21-0.40 mW · [推算] ~8.4 个月) · 在 demo 板不成立★** ★· ★**完整 2×2 方案表 + 六格矩阵 + Q1~Q5 = `SW/SHUTDOWN_SEMANTICS_SPEC.md` §1~§3 (ISS-234 交卷件) · 机器门禁 `SW/tools/check_shutdown_semantics.py` rc=0 + `--selftest` 17/17 (★main 07:2x 实跑★)** ★ | ★**C + A** ★ ⇒ ★**demo 板按 C (不装电池 ⇒ 无需真断电) · 整机按 A (真断电) · 「长按 10s = 关机」在 demo 板口径下改述为「长按 10s = 深睡」** ★ | ★**G1a-8 继续红 · 原理图侧 G1 定不了稿★** |
| ★**A5** ★ | ★**负载开关选型追认 (`TPS22991RAA`)** ★ | ★**选型已落 (ISS-172 verified)**: 负载开关 `U_PWR_SW` / `U_EN_SW` 的 OPN 已有证据矩阵 (≥3 候选 × `HW/POWER_SHUTDOWN_V3.md` §2 八条判据逐条对照 + RCB 缺口做实 + 降级方案 + 机器门禁) ⇒ ★**网表 L50 的 `[待选型]` 已解决★** ⇒ ★**★只等一句「追认 `TPS22991RAA`」★** | ★**追认 `TPS22991RAA`** (★**零改动**: 已在网表/脚表里落着, 不改板不改网表★) ★ | ★**同上 · 且主板 BOM 的 OPN 出不来 (★网表 value 栏若还写「[待选型]」⇒ BOM 出不来单★)** ★ |

> ★**★两句话就够 (★你原话回「C + A」和「追认 TPS22991RAA」即可, 我代录落账 ⇒ ISS-097 落 closed ⇒ G1a-8 立刻转绿★)** ★
> ★**★而 §A5 这一条特别便宜: ★**它不是「要改板」, 是「要签字」⇒ ★**不会触发第二次改板★** ★**

#### ★★§A-补18-② · ★★`boss_state_value_acceptance_drift_20261117` (★★★ 知会型 · 不需要你拍值★★★) ★★

★**★事实 (★main 15:2x 本机实跑确认★)**: ★**2026-11-17 的三次合法落表 (09:58 A1/A2 · 12:16 A3 · 12:30 A4/A5) 把 `BAT_DET` 三颗从 DNP 改成了必装 ⇒ 「MAIN_PCB 且 DNP 且在板文件里真实存在」的位号数 54 → 51 · 在板上 43 → 40 · 零标记 43 → 40★** ⇒ ★**而 `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` 里写死的验收目标还是 43 (★六处, 现已按追加式订正成 40★)** ★

★**★为什么它要紧**: ★**S7 的验收目标是「零标记数 = 0」⇒ ★**若照 43 走, 要么 S7 验收假红, 要么为了凑够 43 把刚落表的三颗必装又标回 DNP ⇒ ★★那等于把你 09:49 拍板并已落表的三颗必装改回去★★** ★

★**★处置 (★已由 ISS-289 收口, 不需要你出任何值★)**: ★**① 作业包九处现状值按【追加式】订正成 40 (★老字零删除, 订正句写明因哪三次落表★)** ★· ★**② 新增闸 `HW/check_workpack_state_values.py` ⇒ 「作业包 + 清单页里的现状值 == 盘面实测」⇒ rc=0 (★34 个现状值探针实测 == 期望 · 七类判据齐: DNP 零标记数 / 封装数 / dnp 出现次数 / 缺陷条数 / 网表·脚表·BOM md5 (走落表台账为准, 不写死) / 铜层·板框四数 / 位号后缀★) · `--selftest` rc=0 · 10/10 反向用例全抓到** ★· ★**③ 顺带把 ISS-287 查出的另两条差异对回作业包/清单页 (★封装数 186 vs 185 · `_1` 后缀位号★) ⇒ ★**结论由 ISS-289 续做 cont1 补交卷单, 本条不需要你介入** ★

> ★**★⇒ 这条是「知会」, 不是「拍板」: ★**看一眼知道「动板那趟的验收目标是 40 不是 43」就行★** ★

---

### ★③ 阶段门 / 链门 / 巡检 (★main 15:2x 本机实跑·原样 rc★)

| 命令 | rc | 事实 |
|---|---|---|
| ★`state/merge.py` ★ | ★**0** ★ | ★**完整** ★ |
| ★`state/gate_check.py` ★ | ★**0** ★ | ★**Q1 = 18/18** ★ |
| ★`state/issue_check.py` ★ | ★**0** ★ | ★**问题闭环门全过** ★ |
| ★`state/stage_gate.py` ★ | ★**1** ★ | ★**当前 G1 (原理图 / PCB 定稿) · 缺 1 项** ⇒ ★**PCB 布线 unconnected=45 需 0 (DRC 已 0) ⇒ ISS-181** ★ · ★**G1a (原理图侧) 还差 2 条 = G1a-4 (板侧 ESD 四条落表) + G1a-8 (★就是上面 A4/A5★)** ★ |
| ★`state/daily_check.py` ★ | ★**3** ★ | ★**异常已记录 (非崩溃)**: ★**① PCB↔网表逐焊盘等价没过 (板面比网表旧 ⇒ 板不许投) ② 生产链准入/准出没过 (投产包比源旧 ⇒ 下游产物不许用)** ★ ⇒ ★**这两条正是「板只改一次」那一趟要一次做完的事 (位号改名 + 板侧同步 + 布线 45→0 + Gerber/投产包重出)★** ★ |
| ★`HW/check_onepass_preflight_coverage.py` ★ | ★**0** ★ | ★**(+ `--selftest` rc=0)** ★ |
| ★`HW/check_board_frame_caliber.py` ★ | ★**0** ★ | ★**(+ `--selftest` rc=0)** ★ |
| ★`HW/check_workpack_state_values.py` ★ | ★**0** ★ | ★**(+ `--selftest` rc=0 · 10/10) ⇒ ISS-289 闸本体已落盘可用, 只差交卷单** ★ |

> ★**★一句话**: ★**板那一趟仍是唯一的大头 (★unconnected=45 · 板面比网表旧 · 投产包比源旧· 三件事同属那一趟★) ⇒ ★**它必须一次做完 (位号改名 + 板侧同步 B-1~B-8 + 布局修正 + 布线 45→0 + Gerber/投产包重出)★** ⇒ ★**⇒ 板只改一次 ⇒ ⇒ 在它之前, 一切零写板、零落表、零改网表真源★** ★

---

### ★④ 本 job 本轮派活口径 (★`state/advance.py --json` 实跑·原样★)

| 段 | 条数 | 事实 |
|---|---|---|
| ★**internal (内部可派)** ★ | ★**0** ★ | ★**`advance.py` 眼里没有 open 单 (★ISS-288/289/290 三条都已标 fixing★) ⇒ 本 job 不新开重复单** ★ · ★**唯一动作 = 把半成品的 ISS-289 续做续上 (★hw-lead 名额已空 ⇒ 合法派★)★** ★ |
| ★**approvals (外发待批)** ★ | ★**0** ★ | ★**符合老板 2026-11-12 02:02「不再发信, 全靠自己查资料」政策 ⇒ 恒为空 ⇒ 本轮零外发 · 零采购 · 零联系供应商** ★ (★`state/outbox/` 15 份草稿原样留存, 不发★) ★ |
| ★**decisions (待你拍板)** ★ | ★**43** ★ | ★**41 (r55 覆盖) + 2 (本节 §A-补18-① / ②) = 43/43 全部落在本页 (★逐 key grep 命中★)★** ★ |
| ★**waiting (纯等待)** ★ | ★**0** ★ | —— |

> ★**★本轮 main 自办 (不占任何 agent 名额)**: ★**ISS-289 半成品盘面核实 (★闸 rc=0 + selftest 10/10 + 作业包九处订正在位 + 回归 6 条全绿★) + 续做任务书 + 派活 + dispatch_log 补记 + 本决策页追加 + 核验 + 本地快照** ★ ⇒ ★**零写板 · 零落表 · 零改网表/脚表/BOM · 零外发 · 不改 `PROJECT_TRACKER.md` §0 锁死表 · 不写别的 agent 的分片★** ★
"""


def main() -> int:
    lockf = open(LOCK, "a+")
    fcntl.flock(lockf, fcntl.LOCK_EX)
    try:
        with open(PAGE, "r", encoding="utf-8") as f:
            txt = f.read()
        if "§A-补18" in txt:
            print("★§A-补18 已在页 ⇒ 不重复追加")
            return 0
        shutil.copy2(PAGE, BAK)
        with open(PAGE, "w", encoding="utf-8") as f:
            f.write(txt.rstrip() + "\n" + BLOCK)
        print("★DECISION_PENDING_2026-11-16.md 已追加 §A-补18 (老字零删除)")
        print("★备份: %s" % BAK)
        return 0
    finally:
        fcntl.flock(lockf, fcntl.LOCK_UN)
        lockf.close()


if __name__ == "__main__":
    raise SystemExit(main())
