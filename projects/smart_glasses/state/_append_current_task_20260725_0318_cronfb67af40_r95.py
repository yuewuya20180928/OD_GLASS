#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
moli (项目总工) 2026-11-25 03:18 · job fb67af40「ARS45 队列自动派活」
★追加本轮口径到 state/CURRENT_TASK.md (★追加式·老字一字未删★) ★
"""
import os
import shutil
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
CT = os.path.join(HERE, "CURRENT_TASK.md")

BLOCK = """
★★**【本 job · cron fb67af40 (队列自动派活) · 2026-11-25 03:09~03:18 r95 · 本轮口径 (★追加式·老字一字未删★)]★★** ★**`state/advance.py --json` = internal **0** / approvals **0** / decisions **39** / waiting **0** ⇒ 本轮 **派 3 条 (全是 cont1 续派·不是新开)** ★ ⇒ ★**① 【★本轮的真发现 = 上一轮的三条不是空壳, 是被【共因掐死】★★★】** ★**本机实读 `~/.openclaw/subagents/runs.json`**: 上一轮 (02:51~03:03) 派出的 ISS-409/410/411 三条 run 的 `runTimeoutSeconds` **都是 5400 (90 分钟)·根本没到** ⇒ ★**⇒ 死因不是自己超时, 是外部共因中断 (★三条死在【同一 1.2 秒窗口 03:03:28.846~03:03:29.972】·与 2026-11-23 21:51:49、2026-11-25 02:07:37~02:07:40 同型★)** ⇒ ★**⇒ 处置 = cont1 断点续做 (★不是重开·不是僵尸复活·不许推倒重写已在盘的成果★)** ★ ⇒ ★**② 【★三条的落盘状态 (main 本机实测·不抄任何 agent 报告★)】** ★**ISS-409 (hw-lead)**: 真相页 `HW/PCB/BOARD_ONEPASS_RELEASE_CHAIN_TEETH_AUDIT.md` 58,163 B ✔ + 新闸 `HW/check_onepass_release_chain_teeth.py` 58,081 B ✔ (★裸跑 rc=1·红的是现状★) + `state/fragments/hw.yaml` 命中 17 ✔ ⇒ ★**缺 交卷页 + gate_check 终跑记录 + 交卷报告** ★ · ★**ISS-410 (mech-lead)**: 真相页 `MECH/BOARD_ONEPASS_PREMISE_TIER_DECISION_TABLE.md` 84,024 B ✔ + 新闸 `MECH/check_premise_tier_decision.py` 40,949 B ✔ (★裸跑 rc=1·红的是现状: T1 四来源不一致 / T2 板面是 SMD 占位 / T3 档位没拍板★) ⇒ ★**缺 `state/fragments/mech.yaml` (★命中 0·根本没写★) + 交卷页 + 交卷报告** ★ · ★**ISS-411 (sw-lead)**: 新闸 `SW/tools/check_sw_mustchange_face_impact.py` 38,714 B ✔ (★裸跑 rc=1·2/9·命门=链上跑的 `check_onepass_sw_sync.py`(20 处) + `check_sw_ref_reachability.py`(55 处) 两道都在链上且都硬编位号★) ⇒ ★**缺 真相页 `SW/BOARD_ONEPASS_SW_MUSTCHANGE_FACE_IMPACT.md` (★文件不存在·本趟最大的一件★) + `state/fragments/sw.yaml` (★命中 0★) + 交卷页 + 交卷报告** ★ ⇒ ★**③ 【★本轮新增一条派活纪律 (★写在 brief 头上, 不只是写在这里★)】** ★**①【先落盘, 后汇报】(★每完成一件交付物立刻写盘·别攒到最后★) ②【交卷页 + 自有分片 优先】(★这两个才是 main 签收的凭据·先写完★) ③【时间紧就交「交卷页 + 分片 + 短报告」, 剩下的写进交卷页的「未完成」段·不许交半份然后什么都不留】** ⇒ ★**理由: 子会话随时可能被共因掐死 ⇒ 产物必须先落盘才活得下来 (★L-18 同款)** ★ ⇒ ★**④ 【落盘纪律】** ★**`state/issue_log.yaml` 一行没写 (★三条 status 保持 `fixing` ⇒ advance.py 的 in_flight 继续挡住任何 job 重复派 ⇒ 零撞车窗口★) · `state/dispatch_log.yaml` 原子追加 3 条 (★带 `redispatch_zombie: true` + `death_cause` 记共因死因·备份 `dispatch_log.yaml.bak_20260725_0315_cronfb67af40_cont1_409_410_411`★) · 三份 cont1 brief (★断点续做头 + 原 brief 全文·派活前逐份过 `check_brief_commands.py` ★全 rc=0★) · spawn 后 `subagents list` 核对 (★恰好 3 条 running·每 agent 各 1·零重复★)** ★ ⇒ ★**⑤ 【板面零变化】** ★**板 `611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17.362193413` / size 4940213 ⇒ 逐字节未动 (19 天) ⇒ G1 仍开, 不许投板** ★ ⇒ ★**⑥ 【本轮 PCB 类 = 3 条, 全是纪律 ① 的纯查证/纯分析/新建真相页+新建机器闸类·零写板·零落表·零挂链·零外发】** ★ ⇒ ★**落盘 5 件**: 本轮 round log (新) · `state/dispatch_log.yaml` (+3) · 三份 cont1 brief (新) · 本行 (★备份 `.bak_20260725_0318_cronfb67af40_r95`★) ⇒ **零外发 · 零写板 · 零落表 · 零写台账 (不与兄弟 job 抢写权) · 零改既有闸判据 · 零改既有页正文 · 零挂链 · 零写别人的分片 · 未替老板拍板** ★ ⇒ ★★**【下一轮 (03:4x) 盯】** ★**① 三条 cont1 交卷 ⇒ main 独立复核签字 (★新闸 `--selftest` 末行 `ALL TESTS PASS` + 裸跑 rc=1 (红的是现状) + 交卷页在盘 + 分片命中 ≥5 + 板四指纹未动 + merge/gate_check rc=0·Q1 18/18★)** ★ **② ★**若又被共因掐死 ⇒ cont2 (★已落盘的继续用·只补缺口·不许推倒重写★)★** ★ **③ 三道新闸都写死零挂链 ⇒ 挂链是 main 的地界 ⇒ 下一轮 main 要么挂、要么写清为什么不挂** ★ **④ 巡检那两条红 (`check_pcb_nets` rc=1 / `chain_gate` rc=1) = 板那一趟本体·不许单独擦** ★ **⑤ C 段 39 条一条没动 ⇒ 老板这一轮不用做任何新决定** ★ **⑥ 本 job 不发任何信** ★ ★
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
    bak = CT + ".bak_20260725_0318_cronfb67af40_r95"
    shutil.copy2(CT, bak)
    atomic_write(CT, old.rstrip("\n") + "\n" + BLOCK)
    with open(CT, encoding="utf-8") as f:
        new = f.read()
    assert new.startswith(old.rstrip("\n")), "★老字被改动 ⇒ 中止"
    print("★ CURRENT_TASK.md: %d -> %d B (bak: %s)" % (len(old), len(new), os.path.basename(bak)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
