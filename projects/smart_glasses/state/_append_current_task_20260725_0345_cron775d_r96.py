#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
moli (项目总工) 2026-11-25 03:4x · job 775d9893「ARS45 继续执行后继计划」
★追加本轮口径到 state/CURRENT_TASK.md (★追加式·老字一字未删★) ★
"""
import os
import shutil
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
CT = os.path.join(HERE, "CURRENT_TASK.md")

BLOCK = """
★★**【本 job · cron 775d9893 · 2026-11-25 03:26~03:4x r96 · 本轮口径 (★追加式·老字一字未删★)】★★** ★**`state/advance.py --json` = internal **0** / approvals **0** / decisions **39** / waiting **0** (★rc=1 = 「无可派内部活」的正常信号·`advance.py:334` 实读★) ⇒ 本轮 **派 1 条 + 签收 1 条** ★ ⇒ ★**① 【派 1 条 · ISS-411 cont2 → sw-lead】** ★**`internal: []` 的真根因 = ★**台账 16 条 open 的 owner = boss 5 + main 11 ⇒ 全在可派域之外 ⇒ 队列真空·不是被占位挡住** ★ ⇒ ⇒ 走【复活僵尸 + 断点续做】路径 (★**不开新单**·开单归兄弟 job `fb67af40` 的地界·两 job 同开 = 撞 R18★) ⇒ ★**三与判据实读**: 已落盘 (真相页 66,293 B @03:16 + 新闸 39,727 B @03:17 selftest ALL TESTS PASS + `logs/iss411/`) + 会话已死 (★endedAt 03:21:21·status=timeout·abortedLastRun=true·runTimeoutSeconds=5400 未到 ⇒ ★**共因中断**★·与 03:03:28 同型) + 交卷页不在盘 ⇒ ★**⇒ 续做, 不是重开** ★ ⇒ ★**只补 4 件**: 分片 `sw.yaml` (★cont1 被掐在写分片那一步·它自己 transcript 末条逐字「The fragment write was rejected (rc=2, file untouched — atomic)…」★) + 交卷页 + ★**把链上那道闸修回绿**★ + 交卷报告 ⇒ ★**brief 守卫 `check_brief_commands.py --brief-file` rc=0 (本轮亲跑) · spawn 后 `subagents list` 恰好 1 条 running (queue_iss411_cont2·sw-lead·零重复)·childSessionKey `agent:sw-lead:subagent:3b33439b…`·runId `502ea21d…`★** ★ ★**② 【签收 1 条 · ISS-410 (mech-lead) → verified】** ★**main 本机独立复核 (不抄任何 agent 报告)**: 新闸 `--selftest` rc=0 · 末行逐字 `ALL TESTS PASS` (★正向 1 + 反向 19★) · 裸跑 rc=1 (★红的是现状: T1 四来源不一致 / T2 板面是 SMD 占位 land / T3 档位没拍板★) · 交卷页 43,539 B @03:16 + 真相页 89,707 B + 新闸 40,949 B + `mech.yaml` 命中 37 + `logs/iss410/` 7 件 · 板三证 19 天未动 ⇒ ★**落账走独立脚本 + CAS 守卫 (其余 405 条逐条 md5 未变·实测 ✔)★** ⇒ ★**③ 【★本轮新红 = gate_check 0 → 1·已派回 sw-lead★】** ★**main 03:28 / 03:35 两采样读数一致 (★L-33-c 两采样法·真相页 mtime 03:16·owner 已停手 ⇒ 不是瞬时★)**: 红项逐字 = ★**`TP_INT_ISSX` / `TP_TEMP_ISSX` / `U_TEMP_1` @ `SW/BOARD_ONEPASS_SW_MUSTCHANGE_FACE_IMPACT.md:119` ⇒ 「真隐患条数 6 > 基线上限 3」** ★ ⇒ 根因 = 链上的 `SW/tools/check_sw_ref_reachability.py` 扫全仓位号形状 token ⇒ ★**真相页把三个沙盒合成 token 原样写了出来** ★ ⇒ 处置写进 cont2 brief = ★**只许改自己真相页的写法 (写成 `TP_INT_ISS<X>` 之类·语义不丢·实跑该闸必须 rc=0)·不许放宽 BASELINE_COUNT·不许往 BASELINE_TOKENS 塞 token·不许改那道闸的判据·不许单独擦** ★ ⇒ ★**对账: 该红与本轮签收的 ISS-410 (MECH 域) 零交集 (逐条读过 FAIL 行·无 MECH 文件) ⇒ 按 L-26 不扣 ISS-410 的分** ★ ⇒ ★**④ 【跳过 1 条 · ISS-409 (hw-lead)】** ★**真在飞 (transcript 923,017 B @03:32:56 仍写·status=running) ⇒ 一个 agent 同时只允许一个写会话 ⇒ 不重复派** ★ ⇒ ★**⑤ 【B 段 approvals 恒空 ⇒ `state/outbox/` 递归 22 份·今日新增 0·零发送·未发任何信】** ★ ⇒ ★**⑥ 【C 段 39 条 · 一页 18 + 索引 30 ⇒ 并集 39/39 零漏项 ⇒ 一件没新增拍板项·一件没改建议值·一件没代拍 ⇒ 老板这一轮不用做任何新决定】** ★ ⇒ ★**⑦ 【核验 5 连本轮实测 rc】** ★**merge 0** (★冲突 0·等外部 25·等总工 473★) · ★**gate_check 1** (★Q1 18/18·Q2 3/3·Q6 ✅·★Q7 钉板闸链 10/10★·缺口 4 条 = 1 条新红 + 3 条「等另一个总工」★) · ★**issue_check 1** (★违规 19 条·全是既有逾期老账·本轮零新增★) · ★**stage_gate 1** (★当前 **G1**·还差 **1** 项 = 布线 unconnected 45→0·**G1a 还差 2 条** G1a-4/G1a-8★) · ★**daily_check 3** (★三条老账: 问题闭环门 19 / `check_pcb_nets` rc=1 / `chain_gate` rc=1 ⇒ **后两条就是板那一趟本体·不许单独擦**★) ★ ⇒ ★**⑧ 【板面零变化 (三证)】** ★**板 `611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17.362193413` / size 4940213 ⇒ 19 天 ⇒ **G1 仍开, 不许投板** ★ ⇒ ★**⑨ 【落盘 8 件】** 落账脚本 (新) · `state/issue_log.yaml` (★签收 1·CAS 守卫·备份★) · `state/dispatch_log.yaml` (+1·备份★) · cont2 brief (新) · `state/.verify/20261125_0328*.out` + `20261125_0334*.out` (★两采样留证★) · `PROGRESS_SNAPSHOT.md` (★本地快照 rc=0★) · 本 round log (新) · 本行 (★备份 `.bak_20260725_0345_cron775d_r96`★) ⇒ **零外发 · 零写板 · 零落表 (除 issue_log 自身状态) · 零改既有闸判据 · 零改既有脚本 · 零改既有页正文 · 零挂链 · 零写别的 agent 的分片 · 未替老板拍板 · 不改 PROJECT_TRACKER §0** ★ ⇒ ★**GitHub: 本 job 不推 (★由 5 小时同步 job 负责★) ⇒ 只落本地快照** ★ ★ ⇒ ★★**【下一轮 (04:0x) 盯】** ★**① ISS-411 cont2 交卷 ⇒ main 独立复核签字 (★查杀点: 交卷页在盘 + `sw.yaml` 命中 ≥5 + ★**`python3 SW/tools/check_sw_ref_reachability.py` rc=0** + `state/gate_check.py` rc=0·Q1 18/18 + 板三证未动 + merge rc=0★)** ★**② ISS-409 交卷 ⇒ main 独立复核签字 (★新闸 selftest 末行 ALL TESTS PASS + 裸跑 rc=1 (红的是现状) + 交卷页在盘 + `hw.yaml` 命中 ≥5 + 板三证未动★)** ★**③ 那两条红不许单独擦 (板那一趟本体)** ★**④ 三道新闸 (409/410/411) 都写死零挂链 ⇒ 挂链是 main 的地界 ⇒ 下一轮要么挂、要么写清为什么不挂** ★**⑤ 板框第一问仍未答 (甲 B160×100 台架板 vs 乙 F30A 60×30 ⇒ 上位问题 `boss_u1_upper_axis_board_trip_physical_product`·回函先跑 `state/board_decision_reply_mapper.py` 撞码当场拒收★) ⇒ 本 job 不代拍** ★**⑥ C 段 39 条一条没动 ⇒ 老板这一轮不用做任何新决定** ★**⑦ 本 job 不发任何信** ★ ★
"""


def atomic_write(path, content):
    d = os.path.dirname(path) or "."
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_", suffix=".part")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def main():
    with open(CT, encoding="utf-8") as f:
        old = f.read()
    bak = CT + ".bak_20260725_0345_cron775d_r96"
    shutil.copy2(CT, bak)
    atomic_write(CT, old.rstrip("\n") + "\n" + BLOCK)
    with open(CT, encoding="utf-8") as f:
        new = f.read()
    assert new.startswith(old.rstrip("\n")), "★老字被改动 ⇒ 中止"
    print("★ CURRENT_TASK.md: %d -> %d B (bak: %s)" % (len(old), len(new), os.path.basename(bak)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
