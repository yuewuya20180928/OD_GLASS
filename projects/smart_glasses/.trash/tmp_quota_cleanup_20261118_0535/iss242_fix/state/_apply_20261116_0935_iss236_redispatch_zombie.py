#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20261116_0935_iss236_redispatch_zombie.py
★main (moli) 派活落账 · 2026-11-16 09:35 (cron 775d9893 继续执行后继计划)★

★★**为什么做这件事 (★本轮自己实跑, 不是抄任何交卷报告★)★★ ★★
· ★**`python3 state/advance.py --json` ⇒ internal = []** (★本轮 advance.py 自己算出来是空的★)
· ★**原因 = 僵尸 fixing**: ★**ISS-236 (hw-lead) status=fixing, 但它的会话已经死了** ★
  · 08:45:56 → 08:53:57 那轮 = ★**被默认 8 分钟 spawn 超时掐死** (status=timeout) ★
  · 09:13 兄弟 job (cron fb67af40 队列自动派活) 写了续做 brief (`state/dispatch_briefs/ISS-236_task.txt`, 10550 B)
    ⇒ ★**但它的 sessions_spawn 被中止** (★父会话 01:16:41 toolResult = "Aborted", 零写盘★)
  · ⇒ ★**main 09:33 实测: `~/.openclaw/agents/hw-lead/sessions/` 下没有任何 09:1x 之后的新会话文件
    ⇒ 那个 spawn 根本没起来 ⇒ ISS-236 = 僵尸 fixing (★占着 hw-lead 名额, 却没人干活★)** ★
· ★**后果 (★main 实跑 advance.py 内部逻辑复现★)**: ★**in_flight 规则 = "该 agent 名下已有 fixing 的 issue ⇒ 本轮不再给它派新活"**
  ⇒ ★**hw-lead 名额被僵尸占着 ⇒ ISS-237 (open, hw-lead, due 11-19) 也派不出去** ★ ⇒ ★**两条主线单同时僵住** ★
· ★**处置**: ★**本轮把 ISS-236 重新派出去 (taskName=advance_iss236, runTimeout=5400s ⇒ 90 分钟, 绕开 8 分钟默认超时)** ★
  ⇒ ★**session = agent:hw-lead:subagent:8718cb66-7ab9-414b-a80e-6576a40d7526 (★09:33 起 status=running, 实测在盘★)** ★
  ⇒ ★**ISS-236 status 保持 fixing (★本来就是 fixing, 本轮不重复标★) ★**
  ⇒ ★**ISS-237 (open, hw-lead) 继续排队 ★** (★hw-lead 名额被 ISS-236 占着 ⇒ 按铁律「一个 agent 同时只有一个写会话」不并行派★)

★★**本轮派活前 main 自己实跑验证过的事实 (★不是抄任何交卷报告★)★★ ★★
· ★**`state/land_v_values.py`** ⇒ 83266 B / mtime 08:24 · `py_compile` **rc=0** · `--help` **rc=0**
  · `--decision V-3=E` (dry-run) ⇒ **rc=0** + 逐字输出「✅ rc=0: DRY-RUN 完成 · 零写盘 · 盘上 5 个 md5 逐字节不变」 ★
  · `--decision V-3=E2` (非法值) ⇒ **rc=2** + 逐字输出「非法取值 V-3=E2 ⇒ 白名单里只有 {A, D, DEG4, E} … 零写盘」 ★
  ⇒ ★**交付物① 已达标 ⇒ 派活书里明写「不许重写这 83KB / 1414 行」** ★
· ★**受保护 5 个 md5 (main 09:3x 实测)**: 网表 `34132f7e40a241e1fae1476be0eafbd5` · 脚表 `b21b743a7702d30729f0d653c15392df`
  · BOM `c195a117ff17490d4d1e1a5b8f1995a7` · 板 `611b869e13518c3c023fb178f91a0075` · `.kicad_pro` `3e504d2be83152e337949723e909be1b` ★
· ★**`HW/SCHEMATIC_FINALIZATION_CLOSEOUT.md` 仍不在盘 (★交付物② 未交★)** ⇒ ★**ISS-236 不能落 verified** ★
· ★**`/tmp/iss236_root` (300M) 在盘, 且落地必需的 8 个文件全在** ⇒ ★**派活书里明写「直接用它, 不许再 cp -a 整棵树」** ★
· ★**`state/check_brief_commands.py` ⇒ rc=0, 「查了 8 条待办单的 task_brief, 有问题的 0 条」** ★
· ★**派活书全文核过**: ★**issue_log 里 ISS-236 的 task_brief 42 行里 40 行逐字在派活文件里** ★
  (★另 2 行是同义改写: 「18 条构成」那句 + 「两个必须写进去的坑」那句 —— 坑本身逐字在文件里: DEMO_DNP 3 行 + 生成顺序★)

★★**边界 (本脚本)★★ ★★
· ★**只写 `state/dispatch_log.yaml` (追加一条派活记录, 可追溯)** ★
· ★**不改 `state/issue_log.yaml` 的 status (★ISS-236 本来就是 fixing★)** ★
· ★**不碰 `PROJECT_TRACKER.md` §0** · ★**不写任何 agent 的分片** · ★**不碰板 / 布线 / 布局** ★
· ★**零外发** · ★**不替老板拍板** (★V-2 / V-3 / V-4 一个值都不落★) ★
"""
import fcntl
import os
import shutil
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
DL = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".dispatch_log.lock")
TODAY = "2026-11-16"

BRIEF = (
    "★**续做派活 (★main 2026-11-16 09:3x 实测: 上一轮 09:13 的 spawn 被中止 ⇒ ISS-236 是僵尸 fixing·"
    "本轮重派·runTimeout 5400s 绕开 8 分钟默认超时★)** ★\n"
    "★**交付物① `state/land_v_values.py` 已在盘且能跑 (main 09:3x 实测: py_compile rc=0 · --help rc=0 · "
    "dry-run V-3=E rc=0 零写盘 · 非法值 V-3=E2 rc=2 零写盘) ⇒ 不许重写那 83KB / 1414 行★** ★\n"
    "★**本轮主战场 = 交付物② `HW/SCHEMATIC_FINALIZATION_CLOSEOUT.md` (★现在不在盘★) + 交卷单 "
    "`HANDOFF/2026-11-16_hw-lead_ISS236_一键落表器与定稿收口清单.md` + 分片 `state/fragments/hw.yaml` (走 frag_write.py)★** ★\n"
    "★**顺序纪律: 先写盘 → 再补自证输出 → 最后跑 8 条验收命令 (★上一轮就是死在「先验证后写盘」★)★** ★\n"
    "★**session = agent:hw-lead:subagent:8718cb66-7ab9-414b-a80e-6576a40d7526 (taskName advance_iss236, 09:33 起 running)★** ★"
)


def main() -> int:
    shutil.copy2(DL, DL + ".bak_20261116_0935_iss236_redispatch")
    lock_fh = open(LOCK, "a+")
    try:
        fcntl.flock(lock_fh, fcntl.LOCK_EX)
        dl = yaml.safe_load(open(DL, encoding="utf-8")) if os.path.exists(DL) else {"dispatches": []}
        dl.setdefault("dispatches", []).append({
            "issue": "ISS-236", "agent": "hw-lead", "at": TODAY, "brief": BRIEF[:300],
        })
        fd, tmp2 = tempfile.mkstemp(dir=HERE, prefix=".dispatch_log.", suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                yaml.safe_dump(dl, f, allow_unicode=True, sort_keys=False, width=200)
            os.replace(tmp2, DL)
        except Exception:
            if os.path.exists(tmp2):
                os.unlink(tmp2)
            raise
    finally:
        fcntl.flock(lock_fh, fcntl.LOCK_UN)
        lock_fh.close()

    chk = yaml.safe_load(open(DL, encoding="utf-8"))
    print("✅ dispatch_log.yaml 已原子写 (flock + 锁内重读 + tmp/os.replace):")
    print(f"   - 追加 ISS-236 → hw-lead 派活记录 (★2026-11-16 09:3x 重派·僵尸 fixing 复活★)")
    print(f"   - dispatch 总条数: {len(chk['dispatches'])}")
    print(f"   - 备份: {os.path.basename(DL)}.bak_20261116_0935_iss236_redispatch")
    print("   ★**ISS-236 status 保持 fixing (本来就是 fixing, 本轮不重复标)** ★")
    print("   ★**ISS-237 (open, hw-lead) 继续排队 —— hw-lead 名额被 ISS-236 占着** ★")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
