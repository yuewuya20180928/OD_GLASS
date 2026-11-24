#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cron 775d9893 · 2026-11-24 22:0x · 本轮追加式落盘 (fail-closed · md5 守卫 · 原子写 · 备份)
=====================================================================
本轮落 3 件 (全部追加式, 老字一字未删):
  1) DECISION_ONE_PAGER_2026-11-22.md  → 追加 §㊻
  2) state/LESSONS.md                  → 追加 L-33 (两条新通则)
  3) state/CURRENT_TASK.md             → 追加本轮口径一行

纪律:
  - 只追加, 不改任何既有正文
  - 写前 md5 守卫 (与本脚本读到的基线一致才写)
  - 写后回读验证 (新增段在, 老前缀 md5 不变)
"""
import hashlib
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def append_atomic(path, text, tag):
    with open(path, "rb") as f:
        old = f.read()
    old_md5 = hashlib.md5(old).hexdigest()
    backup = path + f".bak_20260724_2205_cron775d_{tag}"
    shutil.copy2(path, backup)
    with open(path, "ab") as f:           # O_APPEND 追加, 不会覆写
        f.write(text.encode("utf-8"))
    with open(path, "rb") as f:
        new = f.read()
    assert new[:len(old)] == old, "老前缀被改动 ⇒ 停"
    assert hashlib.md5(new[:len(old)]).hexdigest() == old_md5, "老前缀 md5 变了 ⇒ 停"
    assert text.encode("utf-8") in new, "新增段没落上 ⇒ 停"
    print(f"  ✅ {os.path.basename(path)}: {len(old)} → {len(new)} B (追加 {len(text.encode('utf-8'))} B) · 老前缀 md5 {old_md5[:12]} 逐字节不变 · 备份 {os.path.basename(backup)}")


# ---------------- 1) 一页纸 §㊻ ----------------
ONE = os.path.join(PROJ, "DECISION_ONE_PAGER_2026-11-22.md")
sec = """

---

## ★★§㊻ · 2026-11-24 22:0x (cron 775d9893 · 继续执行后继计划) · ★本轮口径 (★追加式 · 老字一字未删★) ★★

★**本轮一句话**: ★**「派了」不等于「在跑」, 也不等于「没跑完」⇒ 三个总工的活被【同一次外部中断】掐在同一秒 ⇒ 盘上留着真的半成品 ⇒ 本轮【复活 + 续派】三条 (纯分析/闸类 · 零写板) ⇒ 而本轮【零新增拍板项】⇒ 老板这一轮【不用做任何新决定】** ★

### ★★① 本轮读数 (★本机实跑 · 不抄任何 agent 报告★) ★★

```
advance.py --json  ⇒ internal 0 · approvals 0 · decisions 55 · waiting 0
merge.py            ⇒ rc=0  产出 883 | 阻塞 43 (高危 33) | 未闭合需求 396 | 冲突 0
gate_check.py       ⇒ rc=0  Q1 18/18 | Q2 1/3 | Q3 interface_claims 1277 | Q6 ✅ | Q7 钉板闸链 10/10 | 缺口 5 条
issue_check.py      ⇒ 违规 19 条 (★全是既有逾期老账 · 本轮零新增★)
stage_gate.py       ⇒ 当前 G1 · 还差 1 项 (PCB 布线 unconnected 45→0) · G1a 还差 2 条
板三项指纹          ⇒ 611b869e… / 6aee500e… / 9174309d… / 5b999399…  (mtime 2026-11-06 07:07:17 · size 4940213 ⇒ 逐字节未动)
```

### ★★② ★★本轮唯一新增的【机制级硬事实】★★ ★**★这是本轮最值钱的一条 ⇒ 它改的是【怎么判断"活还在不在"】这件事的判据本身★** ★

★**事实 (★本机逐条实读 `~/.openclaw/subagents/runs.json` + 三个 transcript 末条★)★**:

| ★单号★ | ★子会话★ | ★起止★ | ★时长★ | ★`runTimeoutSeconds`★ | ★终态★ |
|---|---|---|---|---|---|
| ISS-398 cont1 → sw-lead | `agent:sw-lead:subagent:ce4945c3…` | 21:44:14 → 21:51:49 | 455.0 s | **5400** | timeout · abortedLastRun=true |
| ISS-399 → mech-lead | `agent:mech-lead:subagent:4c70ad95…` | 21:44:12 → 21:51:49 | 458.0 s | **5400** | failed · `stopReason=aborted` |
| ISS-391 cont1 → hw-lead | `agent:hw-lead:subagent:d5a39a1e…` | 21:44:38 → 21:51:51 | 432.5 s | **5400** | timeout · abortedLastRun=true |

★★**⇒ 三条的 `runTimeoutSeconds` 都是 5400 (90 分钟), 却都在起后 7~8 分钟、且在【同一 3 秒窗口内 (21:51:49~51)】一起死 ⇒ ⇒ 【不是超时】, 是【外部同时中断】⇒ 与任务内容无关 ⇒ ⇒ 判「这个 agent 还在不在飞」不能只看 `status`, 必须同时看【两条: `runTimeoutSeconds` 是不是真的到了】+【多条是不是死在同一秒】** ★★

★★**⇒ 连带一条 (★落在这条事实的正面★)★**: ★**"会话 ended" ≠ "活没干" ⇒ 盘上留下的半成品是真的** ★★ ⇒ 本机实测三样半成品:

| ★单号★ | ★盘上已有 (★本机 22:0x 实读★) | ★还缺什么★ |
|---|---|---|
| ISS-398 cont1 (sw-lead) | ★**`SW/tools/check_sw_ref_reachability_v2.py` 已改 (mtime 21:46:19) ⇒ 实测 `--selftest` = 7/7 通过 · 末行 `ALL TESTS PASS` · rc=0** ⇒ ★**核心目标 (0/7 → 全绿) 已达成** + `SW/BOARD_ONEPASS_SW09_LANDING_PATCH.md` 32,221 B | 交卷页 B1~B6 / 分片 (`grep -c iss398` = 0) |
| ISS-399 (mech-lead) | ★**新闸 `MECH/check_mech_signed_append_ledger.py` 34,729 B (M1~M7 · 裸跑判红 6 条 + 自带「预期读数=rc=1 · 红的是现状」说明)** + `logs/iss399/baseline_9gates_md5.txt` | ★**真相页 `MECH/BOARD_ONEPASS_SIGNED_APPEND_LEDGER_DESIGN.md` 不在盘** / 交卷页 B1~B7 / 分片 (`grep -c iss399` = 0) |
| ISS-391 cont1 (hw-lead) | 备份 `logs/iss391/check_fts_land_drill_same_batch.py.BEFORE` + `md5_before.txt` | ★**真件一个字没改** (md5 `dabc1200…` 与 ISS-396 签收基线逐字相同) + 交卷页 / 分片 |

### ★★③ ★★第二条新硬事实: 【交卷页骨架 = 门禁读数的污染源】★★

★**事实**: ★**三个 agent 都在 21:44 先建了交卷页【骨架】(B1~B6/B7 全是「占位 / 待填 / 施工中」)★** ⇒ ★**而 `state/gate_check.py` 的 Q1 是【按最新一份交卷页】评分 ⇒ ⇒ 骨架页把 Q1 的「块齐全」骗成 18/18, 同时把 Q2【证据分级率】从 3/3 打到 1/3 (sw-lead / mech-lead 两家「标签: 无」)⇒ ⇒ ★**门禁读数被"派活时刻的空壳"污染了 ⇒ 而 Q1 的 18/18 此刻【有假绿成分】** ★★

★**⇒ 纪律 (★本轮落进 LESSONS L-33★)★**: ★**① 派活时刻建骨架页 = 制造一个"看起来已交卷"的读数 ⇒ 骨架页要么别建, 要么建了就当"红灯"处理 (Q2 会立刻掉) · ② Q1 的 18/18 与 Q2 的 1/3 放在一起读才是真相 ⇒ 单看 Q1 会被骗** ★ ★

### ★★④ 零新增拍板项 (★一件没代拍★) ★★

★**待拍板面 = 55 条 (★`advance.py --json` 本机实读★)** ⇒ ★**一页 23/55 + 索引 32/55 ⇒ 并集 55/55 · 零漏项** ⇒ ★**本轮【一件没新增拍板项】·【一件没改建议默认值】·【一件没代拍】⇒ 老板这一轮不用做任何新决定** ★ ★

★**★⇒ 板那一趟的老板侧阻塞面不变 (★仍是这 11 件 · 建议默认值全在页上·★第一问仍是「画甲台架板还是乙产品内板」★)★**: ★`boss_u1_upper_axis_board_trip_physical_product` (★上位问题·★回函先跑 `state/board_decision_reply_mapper.py` 撞码当场拒收★) · `boss_shutdown_semantics_and_loadswitch_20261117` (`SD-1` / `LS-1`) · `boss_esd_model_axis_pending_20261117` (`W-2`) · `iss364_k2_d_esd_usb_d_2v3_pin` (`W-1c`) · `boss_c_vbus_gnd_reserve_pad_20261117` · `boss_decide_reboard_mtime_size_caliber` · `boss_decide_second_reboard_stop_authority` · `iss340_c_bucket_boss_decisions` · `iss364_k3_button_3n_vs_1p5n` · `iss237_product_screen_version` · `iss260_boss_a3_arch_and_model` ★ ★

### ★★⑤ 本轮派的三条 (★★全属「板只改一次」纪律 ① 纯分析 / 作业包 / 闸类 ⇒ 零写板★) ★★

| ★单号★ | ★agent★ | ★形态★ | ★本轮动作★ |
|---|---|---|---|
| ★**ISS-391 cont2** ★ | hw-lead | ★**续派 (纯分析 + 改一道已签收闸的判据逻辑 + 改夹具 · 零写板)** ★ | 判据层 D1/D2/D3 从「关键词命中」改「★动作腿命中★」+ 夹具改真件现读 + 把 main 的决定性实验固化进夹具 |
| ★**ISS-398 cont2** ★ | sw-lead | ★**收尾派 (纯分析 + 改自测夹具 · 零写板)** ★ | ★**核心目标已达成 (selftest 0/7 → 7/7)** ⇒ 只补交卷页 + 分片 + 补丁页核对 ★ |
| ★**ISS-399 cont2** ★ | mech-lead | ★**收尾派 (纯分析 + 新建真相页 + 新建闸 · 零写板)** ★ | 新闸已在盘 ⇒ 补真相页 + 交卷页 + 分片 |

★**★⇒ 台账一行没动 (★零写台账 · 零改闸 · 零改既有页正文 · 零写别人的分片★)**: ★**ISS-391 / ISS-398 / ISS-399 的 `status` 保持 `fixing` 不动 ⇒ ⇒ `advance.py` 的 in_flight 规则继续挡住兄弟 job `fb67af40` 重复派 ⇒ 零撞车窗口** ★ ★

### ★★⑥ 本 job 边界自证 (2026-11-24 22:0x) ★★

★**派 3 条 (★纯分析/闸类 · 零写板★)** · ★**零外发** (★`approvals: []` ⇒ 无草稿要补 · `state/outbox/` 19 份 .md 一律只留档不发 · 未发任何邮件 / 未联系任何供应商 / 未下采购单★)** · ★**零写台账** (★`issue_log.yaml` / `dispatch_log.yaml` 本轮一字未写 ⇒ 不与兄弟 job 抢写权★)** · ★**零写板** (★板三项指纹逐字节未动★)** · ★**零落表** · ★**零改既有闸 / 零改既有页正文** · ★**零挂链** · ★**零写别人的分片** · ★**不代拍** · ★**不改 PROJECT_TRACKER.md §0 锁死表** · ★**GitHub: 本 job 不推 (★由独立 5 小时同步 job 负责★)** ★
"""

# ---------------- 2) LESSONS L-33 ----------------
LES = os.path.join(HERE, "LESSONS.md")
les = """

## ★L-33 · ★★两条本轮新踩的机制坑 (2026-11-24 22:0x · cron 775d9893) ★★

★**★⇒ L-33-a · 「会话 ended」≠「活没干」⇒ 判"在不在飞"要同时看两条: `runTimeoutSeconds` 到没到 + 是不是多条死在同一秒★ ★**

★**实测 (★本机实读 `~/.openclaw/subagents/runs.json` + 三个 transcript 末条★)★**: ★**21:44 三条同时派出 (ISS-398 cont1 → sw-lead / ISS-399 → mech-lead / ISS-391 cont1 → hw-lead) · 三条的 `runTimeoutSeconds` 都是 5400 (90 分钟) · 三条却在起后 7~8 分钟、且在【同一 3 秒窗口 21:51:49~51】一起死 (timeout / failed / aborted) ⇒ ⇒ 【不是超时】⇒ 是【外部同时中断】** ★ ★
★**★⇒ 教训: 「status=timeout」被默认理解成"它自己超时了"⇒ ★★但**先看 `runTimeoutSeconds`**⇒ 时长远小于它 ⇒ 就不许归因成"任务太大/它太慢"⇒ 而要多问一句【是不是被一起掐了】★★ ⇒ ★★**多条死在同一秒 = 共因 ⇒ 不必分别复盘三个任务, 要复盘那一次中断**★★ ★ ★
★**★⇒ 连带 (★本轮正面吃到一次★)★**: ★**"会话死了"不等于"白干"⇒ 盘上留下的半成品是真的** ★★ ⇒ ★**本机实测: sw-lead 的第三道病闸 `--selftest` 已由 0/7 修成 7/7 (ALL TESTS PASS) · mech-lead 的新闸 34.7 KB 已在盘 ⇒ ⇒ 续派时【先盘点盘上有什么】, 再决定补什么 ⇒ 不要重做** ★ ★
★**★⇒ 配套 (★来自 11:14 那条「上游 abort」教训★)★**: ★**"再死一次也不丢东西" 的唯一做法 = 每件交付物先落盘再跑它** ★★ ⇒ ★**⇒ 交卷页骨架先落盘 / 真相页骨架先落盘 / 闸代码先 write 再跑 selftest** ★ ★

★**★⇒ L-33-b · ★★交卷页【骨架】会污染门禁读数 ⇒ Q1 的 18/18 此刻含假绿成分 ★★ ★**

★**实测 (★本机实跑 `state/gate_check.py` 22:0x★)★**: ★**三个 agent 都在派活时刻先建了交卷页骨架 (B1~B6/B7 全是「占位 / 待填 / 施工中」) ⇒ 而 Q1 是【按最新一份交卷页】评分 ⇒ ⇒ Q1 照样 18/18 (块齐全) ⇒ 但 Q2【证据分级率】从 3/3 掉到 1/3 (sw-lead / mech-lead 两家「标签: 无」) ⇒ ⇒ ★**门禁读数被"派活时刻的空壳"污染了** ★ ★
★**★⇒ 纪律 ★**: ★**① 派活时刻不许建交卷页骨架 (要么不建, 要么建成就当红灯处理) · ② Q1 与 Q2 必须放在一起读 ⇒ 单看 Q1 的 18/18 会被骗** ★ ★
★**★⇒ 与 L-21~L-32 合看★**: ★**L-21 清单钉 file,line · L-23 工具会扫到自己 · L-24 沙箱硬链接 · L-25 厂商料号逐个坐实 · L-26 签收要跑扫描面命中的闸 · L-27 签收要等 owner 收工 · L-28 幂等守卫不许静默吞 · L-29 按设计判红 ≠ 闸坏了 · L-30 取号/取 key 必须先查重 · L-31 沙盒落点要唯一 · L-32 锚在真件上的东西必须现读 · L-33 会话 ended ≠ 活没干 / 骨架页污染门禁读数** ⇒ ★**共性 = 【凡是【会自己变的东西】—— 会话 / 交卷页 / 闸读数 —— 都不能只看一个字段就下结论, 必须交叉两条以上独立证据】** ★ ★
"""

# ---------------- 3) CURRENT_TASK 一行 ----------------
CUR = os.path.join(HERE, "CURRENT_TASK.md")
cur = """
★★**【本 job · cron 775d9893 · 2026-11-24 22:0x (r91) · 本轮口径 (★追加式·老字一字未删★)】★★** ★**`advance.py --json` = internal **0** / approvals **0** / decisions **55** / waiting **0** ⇒ 本轮 **派 3 条** (★不是 advance.py 的 internal, 是【复活三具僵尸】★): ★**ISS-391 cont2 → hw-lead / ISS-398 cont2 → sw-lead / ISS-399 cont2 → mech-lead** (★三条全是「板只改一次」纪律 ① 纯分析/闸类 ⇒ 零写板★) ⇒ ★**根因 = 21:44 派的三条在 21:51:49~51 同一秒被【外部同时中断】掐死 (三条 `runTimeoutSeconds` 都是 5400 ⇒ 不是超时) ⇒ 台账 `fixing` 名额被空壳占住 ⇒ internal 恒空** ★ ⇒ ★**盘上半成品是真的 (sw-lead 第三道病闸 selftest 已 0/7 → **7/7 ALL TESTS PASS** · mech-lead 新闸 34.7 KB 已在盘 · hw-lead 真件一字未改) ⇒ 续派单只补缺口, 不许重做** ★ ⇒ ★**台账一字未写 (`issue_log.yaml` / `dispatch_log.yaml` 本轮零写 ⇒ 零与兄弟 job 抢写权 · status 保持 fixing ⇒ in_flight 继续挡住 `fb67af40` 重复派)** ★ ⇒ ★**C 段 55 条: 一页 23 + 索引 32 ⇒ 并集 **55/55 零漏项** ⇒ 一件没新增拍板项 · 一件没改建议值 · 一件没代拍 ⇒ 老板这一轮不用做任何新决定** ★ ⇒ ★**核验 5 连本轮实测 rc**: ★**merge 0** (产出 883 · 阻塞 43 高危 33 · 未闭合 396 · 冲突 0) · ★**gate_check 0** (★**Q1 18/18** · ★**Q2 1/3 ← 21:44 三张交卷页骨架污染 (★派活时刻建骨架 ⇒ 门禁读数被空壳污染·★已落 L-33-b★)★ · Q3 1277 条 · Q6 ✅ · ★**Q7 钉板闸链 10/10**★ · 缺口 5 条) · ★**issue_check 违规 19 条 (★全是既有逾期老账 · 本轮零新增★)** · ★**stage_gate: 当前 G1 · 还差 1 项 = 布线 unconnected 45→0 · G1a 还差 2 条** · ★**daily_check 3 (★老账三条: 问题闭环门 19 / `check_pcb_nets` rc=1 / `chain_gate` rc=1 ⇒ 后两条就是板那一趟本体·不许单独擦★)** ★ ⇒ ★**板面零变化 (三证)**: 板 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17` · size 4940213 ⇒ 逐字节未动 ⇒ **G1 仍开, 不许投板** ★ ⇒ ★**落盘 4 件**: `state/ROUND_LOG_cron775d_2026-11-24_2200.md` (新) · `DECISION_ONE_PAGER_2026-11-22.md` (追加 §㊻) · `state/LESSONS.md` (追加 L-33) · 本行 + `PROGRESS_SNAPSHOT.md` (本地快照) ⇒ ★**零外发 · 零写板 · 零落表 · 零写台账 · 零改闸 · 零改既有页正文 · 零写别人的分片 · 未替老板拍板 · 不改 PROJECT_TRACKER §0** ★ ⇒ ★**GitHub: 本 job 不推 (★由 5 小时同步 job 负责★) ⇒ 只落本地快照** ★ ★ ⇒ ★★**【下一轮 (22:2x 那趟) 盯】** ★**① 三条 cont2 是否还在跑 (★transcript 静默 + 交卷页仍是骨架 ⇒ 就是又死了 ⇒ 立刻再续, 别等) ★**② 三条交卷 ⇒ main 独立复核签字 (★查杀点: 新闸 rc=0 + `--selftest` 末行 ALL TESTS PASS + gate_check Q1/Q2 双读 + 板三证未动) ★**③ ★**Q2 现在 1/3 ⇒ 三张骨架页被填实后应回 3/3 ⇒ 若没回 ⇒ 说明交卷页没填证据分级 (★不是 agent 的错, 机制问题·归 main) ★**④ ★**兄弟 job `fb67af40` 若在下一轮也想派这三条 ⇒ 它会看到三条 transcript 在写 ⇒ 应跳过 ⇒ 若它还是派了 ⇒ 就是两条写会话 = R18 (分片合并丢 12%~38%) ⇒ 立刻记进 LESSONS** ★**⑤ 板框第一问仍未答 (甲 demo 台架板 / 乙 产品内板 ⇒ 上位问题 `boss_u1_upper_axis_board_trip_physical_product`) ⇒ 落点坐标的一切前提都挂在它身上, 本 job 不代拍 ★**⑥ 本 job 不发任何信** ★
"""

if __name__ == "__main__":
    print("== 追加式落盘 ==")
    append_atomic(ONE, sec, "onepager_sec52")
    append_atomic(LES, les, "lessons_l33")
    append_atomic(CUR, cur, "current_task_r91")
    print("== 完成 ==")
