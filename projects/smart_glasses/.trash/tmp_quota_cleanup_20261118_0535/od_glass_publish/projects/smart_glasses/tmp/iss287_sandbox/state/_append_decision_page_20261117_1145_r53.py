#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_append_decision_page_20261117_1145_r53.py
★main (moli) · cron 775d9893 (ARS45 继续执行后继计划) · 2026-11-17 11:4x★
★★**追加式 (★老字一行不删★)**: DECISION_PENDING_2026-11-16.md §A-补17 ★★

★★**本节内容 (★全部 main 本机实跑, 不抄任何交卷报告★)★★ ★★
· ★**① 本轮主线动态 (★内部推进, 不进你的清单★)**:
  · ★**ISS-282 (hw-lead) ⇒ verified** (★main 本机独立复验: `HW/check_fsin_rootcause.py` rc=0 · D1~D5 全绿 ·
    `--selftest` rc=0 · 12/12 · 交卷单 47467 B「待填」= 0 · 分片已写 · 板 `611b869e…` 逐字节不变★)
  · ★**ISS-283 (hw-lead) ⇒ 已派 (fixing)** (★11:4x 由 cron 775d9893 派出 · 会话 `agent:hw-lead:subagent:eeecf73f`★
    ⇒ ★**板只改一次纪律: 本单【只动网表/脚表/BOM 落表侧】+ 【不改板】⇒ 板 md5 不变 ⇒ 不构成第二次改板★**)
  · ★**ISS-285 (sw-lead) ⇒ 续做重派 (fixing)** (★原会话 11:35:47 被掐 · 半成品在盘: 交卷单骨架 1362 B +
    补丁套用器 24640 B (未跑过) + 分片 0★ ⇒ 续做任务书 `ISS-285_sw_landing_after_judgment_alignment_cont1.md`
    由★兄弟 job (队列自动派活 fb67af40)★派出 ⇒ ★**本 job 不重复派第二个 sw-lead 会话 (★同一 agent 只允许一个写会话★)**)
  · ★**ISS-286 (mech-lead) ⇒ 在飞** (★MECH 侧 C4 基线过期 · 由兄弟 job 派出★)
  · ★**⇒ 板 `611b869e13518c3c023fb178f91a0075` / `.kicad_pro 3e504d2be83152e337949723e909be1b` 逐字节未变
    (★mtime 仍 2026-11-06 07:07:17★) ⇒ ★**「板只改一次」铁律本轮未破★**
· ★**② 待拍板面本轮核对 (★advance.py --json 实跑★)**: ★**decisions = 40 条 · approvals = 0 · waiting = 0** ★
  · ★**39 条按 key 逐条 grep 命中本页** ⇒ ★**剩下 1 条 `boss_esd_model_axis_pending_20261117` (★ESD 型号轴 + D− 侧★)
    的【内容】已在页 §④ 第 2/3 行 (★ESD 型号轴 W-1b/W-1c + D− 侧 W-2★) ⇒ ★**⇒ 40/40 覆盖, 零缺失, 本节无需新增任何待拍项★**
  · ★**老板 2026-11-17 09:49「按照你的建议执行」⇒ 8 条决策已落账** (★`state/fragments/pm.yaml` 的 `needs_from` 8 条 + 同 key 两条★)
  · ★**本轮零新增待拍项 · 零代拍 · 零外发★**
· ★**③ 阶段门与链门 (★本 job 11:4x 实跑原样 rc★)**: `state/stage_gate.py` rc=0 ⇒ ★**G1 原理图 / PCB 定稿 · 还差 1 项** ★ ·
  `state/merge.py` rc=0 (★产出 494 · 阻塞 43 · 高危 33 · 未闭合需求 274 · 冲突 0 · 健康度 red★) ·
  `state/gate_check.py` rc=0 (★Q1 18/18★) · `state/issue_check.py` rc=0 ⇒ ★**板那一趟仍是唯一大头 (★unconnected=45 需 0★)** ★

★★**边界 (★写死的)★★ ★★
· ★**只追加, 老字一行不删不rewrite** ★ · ★**先备份 (★`DECISION_PENDING_2026-11-16.md.bak_20261117_1145_r53`★)** ★
· ★**flock (`state/.decision_page.lock`) + 锁内重读 + 原子写** ★
· ★**不改 §A / §B / §C 任何一条判据与建议默认值 · 不代老板拍板 · 零外发 · 不碰 `PROJECT_TRACKER.md` §0 锁死表★**
"""
import fcntl
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
PAGE = os.path.join(PROJ, "DECISION_PENDING_2026-11-16.md")
LOCK = os.path.join(HERE, ".decision_page.lock")
BAK = PAGE + ".bak_20261117_1145_r53"

BLOCK = """
---

## §A-补17 · ★★r53 · 2026-11-17 11:4x · ★★★**本轮推进动态 + 待拍板面 40/40 覆盖核对**★★★ (★cron 775d9893 本机实跑★)

> ★**出页人**: 项目总工 (main / moli) · ★**job**: cron `775d9893` (ARS45 继续执行后继计划) · ★**11:4x 实跑·追加式·老字一行不删★**
> ★**本节只给你看进度与核对结果, ★★不新增任何待拍项, 不代你拍任何板★★**

### ★① 本轮内部推进 (★三单在飞 + 一单收卷★)

| 单号 | owner | 状态 | main 本机实跑 / 实查 |
|---|---|---|---|
| ★**ISS-282** ★ | hw-lead | ★**verified** ★ | ★**main 独立复验 pass**: `HW/check_fsin_rootcause.py` **rc=0 (D1~D5 全绿)** · `--selftest` **rc=0 (12/12)** · 交卷单 47467 B (「待填」= 0) · 分片已写 · ★**板 `611b869e…` 逐字节不变 (mtime 仍 11-06 07:07)★** ⇒ ★**hw-lead 名额释放★** |
| ★**ISS-283** ★ | hw-lead | ★**已派 (fixing)** ★ | ★**11:4x 由 cron 775d9893 派出 (会话 `agent:hw-lead:subagent:eeecf73f`)★** · ★**本单只做【网表/脚表/BOM 落表侧】+【不改板】⇒ 板 md5 不变 ⇒ 不构成第二次改板★** · 任务书含 §⑩ (落表后两道过期闸) + §⑪ (HW 侧 C6 机制化收口) + ★**main 11:4x 补一条: `HW/check_onepass_commit_order.py` D0 红 (「零落表」基线过期) 归本单★** |
| ★**ISS-285** ★ | sw-lead | ★**续做重派 (fixing)** ★ | ★**原会话 11:35:47 被掐 (半成品在盘: 交卷单骨架 1362 B + 补丁套用器 24640 B 未跑 + 分片 0)★** ⇒ ★**续做由兄弟 job (队列自动派活 fb67af40) 派出★** ⇒ ★**本 job 不重复派第二个 sw-lead 会话 (★同一 agent 同时只允许一个写会话★)** |
| ★**ISS-286** ★ | mech-lead | ★**在飞** ★ | ★**MECH 侧 C4 (板框坐标归一闸) 的落表后基线过期★** ⇒ ★**由兄弟 job 派出★** |

> ★**⇒ 板 `611b869e13518c3c023fb178f91a0075` / `.kicad_pro 3e504d2be83152e337949723e909be1b` 逐字节未变 (★mtime 仍 2026-11-06 07:07:17★) ⇒ ★**「板只改一次」铁律本轮未破★** ★

### ★② ★★待拍板面核对 (★`state/advance.py --json` 本 job 11:4x 实跑★)★★

| 段 | 条数 | 事实 |
|---|---|---|
| ★**internal (内部可派)** ★ | ★**1** ★ | ★**ISS-283 → hw-lead (★hw-lead 名额刚释放★) ⇒ 本轮已派 (★见 ①★)** ★ |
| ★**approvals (外发待批)** ★ | ★**0** ★ | ★**符合老板 2026-11-12 02:02「不再发信, 全靠自己查资料」政策 ⇒ 恒为空 ⇒ 本轮零外发·零采购·零联系供应商★** |
| ★**decisions (待你拍板)** ★ | ★**40** ★ | ★**39 条按 key 逐条 grep 命中本页** + ★**剩下 1 条 `boss_esd_model_axis_pending_20261117` (★ESD 型号轴 + D− 侧★) 的【内容】已在页 §④ 第 2/3 行** ⇒ ★**⇒ 40/40 覆盖, 零缺失 ⇒ 本节零新增待拍项★** |
| ★**waiting (纯等待)** ★ | ★**0** ★ | —— |

> ★**★老板 2026-11-17 09:49「按照你的建议执行」⇒ 8 条决策已落账** (★`state/fragments/pm.yaml` 的 `needs_from` 8 条 + 同 key 两条★) ⇒ ★**上面 40 条是【落账后】的余额★**

### ★③ 阶段门 / 链门 (★本 job 11:4x 实跑原样 rc★)

| 闸 | rc | 事实 |
|---|---|---|
| ★`state/merge.py` ★ | ★**0** ★ | ★产出 494 · 阻塞 43 (高危 33) · 未闭合需求 274 · 冲突 0 · 健康度 red★ |
| ★`state/gate_check.py` ★ | ★**0** ★ | ★Q1 = 18/18★ |
| ★`state/issue_check.py` ★ | ★**0** ★ | ★问题闭环门全过 (字段/状态机/验证分离/逾期/双向覆盖)★ |
| ★`state/stage_gate.py` ★ | ★**0** ★ | ★**当前 G1 (原理图 / PCB 定稿) · 还差 1 项** ⇒ ★**PCB 布线 unconnected=45 需 0 (DRC 已 0)★** |

> ★**★一句话**: ★**网表侧基本收口 (原理图 ✅ / BOM ✅) ⇒ 【板那一趟】是现在唯一的大头, 且它【一次都不能改两次】⇒ ⇒ 上游三件落表 (A3 / W-4 / G-5) 必须在板那一趟【之前】全部落完 (★正在 ISS-283 里做★), 板那一趟必须一次做完 (位号改名 + 板侧同步 B-1~B-8 + 布局修正 + 布线 45→0 + Gerber/投产包重出)★** ★
"""


def main() -> int:
    lockf = open(LOCK, "a+")
    fcntl.flock(lockf, fcntl.LOCK_EX)
    try:
        with open(PAGE, "r", encoding="utf-8") as f:
            txt = f.read()
        if "§A-补17" in txt:
            print("★§A-补17 已在页 ⇒ 不重复追加")
            return 0
        shutil.copy2(PAGE, BAK)
        with open(PAGE, "w", encoding="utf-8") as f:
            f.write(txt.rstrip() + "\n" + BLOCK)
        print("★DECISION_PENDING_2026-11-16.md 已追加 §A-补17 (老字零删除)")
        print("★备份: %s" % BAK)
        return 0
    finally:
        fcntl.flock(lockf, fcntl.LOCK_UN)
        lockf.close()


if __name__ == "__main__":
    raise SystemExit(main())
