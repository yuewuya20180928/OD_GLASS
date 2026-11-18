#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20261116_1145_redispatch_iss172_zombie.py
★main (moli) 2026-11-16 11:4x (cron fb67af40 ARS45 队列自动派活)★
★ISS-172 (sw-lead) 僵尸 fixing 复活 + 重派★

★★**为什么做这件事 (★main 本轮 11:38~11:4x 自己实跑, 不抄任何交卷报告★)** ★★
· ★**`python3 state/advance.py --json` ⇒ internal = [] · approvals = [] · waiting = []** ⇒ rc=1
  ⇒ ★**根因 = sw-lead 名额被【僵尸 fixing】占着**: ISS-172 status = fixing, 但它的会话刚刚死了
· ★**main 11:38 实测 sessions_list**: `agent:sw-lead:subagent:e3c7a91c` (session 3bd4d3a6)
  ★**11:22:47 起 · 11:38:54 止 · runtime 952s · status=done · abortedLastRun=true** ★
  ⇒ ★**死因 = 会话接管/中止类** (★transcript 最后一条 = `openclaw:prompt-error ... This operation was aborted`★)
  ⇒ ★**注意: 这不是上一轮那个 600s 默认 run timeout** (★上一轮 runtime 594s★, 这轮 952s ⇒ 是被中止, 不是超时★)
· ★**本轮与上一轮的差别 = 这轮【不是零交付物】** ★★ (★main 11:4x 逐文件实跑 ls★):
    · `SW/LOAD_SWITCH_SELECTION_FACTS.md` ★**在盘但只有骨架** (1162 B · mtime 11:25 · 只到 §1 判据原文, §2 矩阵是空的) ★
    · `SW/tools/check_load_switch_selection.py` ★**在盘 25374 B (mtime 11:32)** ★ ⇒ ★**实跑 rc 判定 = FAIL: C0「找不到选型证据基准块」** ★
    · `HANDOFF/2026-11-16_sw-lead_ISS172_负载开关选型证据矩阵.md` ★**不在盘** ★ ⇒ ★**交卷单缺** ★
    · `state/fragments/sw.yaml` ★**mtime 08:39 (本轮没写)** ⇒ ★**分片缺** ★
  ⇒ ★**⇒ 这是一条【半落地僵尸】: 门禁脚本写完了 (25 KB), 但它现在自测是红的 (C0), 矩阵正文空, 交卷单与分片都没有** ★
  ⇒ ★**⇒ 占着 sw-lead 名额却没人干活, 而 sw-lead 名额本该干活 ⇒ 这就是 advance.py internal 段吃空的直接原因** ★
· ★**处置**: 重派 sw-lead (taskName=queue_iss172 · ★**runTimeout=5400s**★) ⇒ ★**status 保持 fixing** ★
  ⇒ ★**续做要点写进派活抬头 (★不是改 brief 正文★): 门禁脚本已在盘 (25 KB, 自测红在 C0) · facts doc 只有骨架 → 只补 §2 矩阵 + §3 RCB + §4 建议 + §5 降级 + §6 出处表 + 交卷单 + 分片** ★

★★**边界 (本脚本)★★ ★★
· ★**只写 `state/dispatch_log.yaml` (追加一条续派记录) + `state/issue_log.yaml` (ISS-172 只追加 note, status 不动)** ★
· ★**不改任何交付物文件** · ★**不碰 PROJECT_TRACKER.md §0** · ★**不写任何 agent 的分片** ★
· ★**不碰板 / 布线 / 布局 / 网表 / 脚表 / BOM** · ★**零外发** · ★**未替老板拍型号或优先级序** ★
"""
import fcntl
import os
import shutil
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
DL = os.path.join(HERE, "dispatch_log.yaml")
IL = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".dispatch_log.lock")
TODAY = "2026-11-16"

DISPATCH_172 = (
    "★**续做派活 (★main 2026-11-16 11:4x 实测: 上一轮 11:22 的 spawn 在 11:38:54 被中止 (runtime 952s · abortedLastRun=true · "
    "prompt-error 'This operation was aborted') ⇒ ★**半落地僵尸**: 门禁脚本已在盘 25 KB (但自测红在 C0「找不到选型证据基准块」) + "
    "facts doc 只有 1.1 KB 骨架 (§2 矩阵空) + 交卷单与分片都没有★ ⇒ 本轮重派 · runTimeout 5400s · "
    "★**续做不是从零开始: 门禁脚本别重写, 补矩阵正文 + 交卷单 + 分片即可**★)** ★"
)

NOTE_172 = (
    "\n\n★2026-11-16 11:4x (cron fb67af40 队列自动派活) ★**僵尸 fixing 复活 + 重派 (半落地)** ★\n"
    "· ★**上一轮会话**: `agent:sw-lead:subagent:e3c7a91c` (session 3bd4d3a6) ★**11:22:47 起 · 11:38:54 止 · "
    "runtime 952s · status=done · abortedLastRun=true** ⇒ ★**死因 = 会话接管/中止类 (prompt-error 'This operation was aborted')** ★\n"
    "· ★**main 11:4x 实测 ≠ 零交付物 (★与上一轮 10:5x 那次不同★)**: `SW/LOAD_SWITCH_SELECTION_FACTS.md` 在盘但只有 1162 B 骨架 (mtime 11:25, §2 矩阵空) · "
    "`SW/tools/check_load_switch_selection.py` 在盘 25374 B (mtime 11:32, ★**实跑 FAIL: C0 找不到选型证据基准块**★) · "
    "★**交卷单不在盘** ★ · ★**分片 sw.yaml 未写 (mtime 08:39)** ★\n"
    "· ★**处置**: 重派 sw-lead (taskName=queue_iss172 · ★**runTimeout=5400s 绕开 600s 默认超时**★) ⇒ ★**status 保持 fixing** ★\n"
    "· ★**续做范围写进抬头 (★不改 brief 正文★)**: 门禁脚本已在盘 (★**别重写, 按它现在的判据把矩阵正文补齐★**) · facts doc 只补 §2 候选矩阵 / §3 RCB 专项 / §4 建议 / §5 降级方案 / §6 出处表 · "
    "★**新建交卷单 + 补分片** ★ ⇒ ★**四件交付物才算齐** ★\n"
    "· ★**零外发** · ★**未替老板拍型号/优先级序 (★决策页 §A5: 老板先拍优先级序, 不是拍型号★)** ★"
)


def _atomic_write(path: str, data: str) -> None:
    fd, tmp = tempfile.mkstemp(dir=HERE, prefix=".tmp_write.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(data)
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def main() -> int:
    shutil.copy2(DL, DL + ".bak_20261116_1145_iss172_redispatch_zombie")
    shutil.copy2(IL, IL + ".bak_20261116_1145_iss172_redispatch_zombie")

    lock_fh = open(LOCK, "a+")
    try:
        fcntl.flock(lock_fh, fcntl.LOCK_EX)

        # ---- dispatch_log: 追加一条续派记录 ----
        dl = yaml.safe_load(open(DL, encoding="utf-8")) if os.path.exists(DL) else {"dispatches": []}
        dl.setdefault("dispatches", []).append({
            "issue": "ISS-172", "agent": "sw-lead", "at": TODAY,
            "brief": DISPATCH_172, "redispatch": True,
            "reason": "★上一轮 status=done/aborted (runtime 952s, 'This operation was aborted') ⇒ 半落地僵尸: "
                      "门禁脚本在盘但 C0 红 + facts doc 只有骨架 + 交卷单/分片缺 ⇒ 仍无交卷★",
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

        # ---- issue_log: ISS-172 只追加 note (status 不动, 保持 fixing) ----
        il = yaml.safe_load(open(IL, encoding="utf-8"))
        hit = 0
        for it in il.get("issues") or []:
            if it.get("id") == "ISS-172":
                it["note"] = (it.get("note") or "") + NOTE_172
                it["dispatched_at"] = TODAY
                hit += 1
        if hit != 1:
            raise SystemExit("★ISS-172 命中数 = %s ⇒ 中止" % hit)
        _atomic_write(IL, yaml.safe_dump(il, allow_unicode=True, sort_keys=False, width=100000))
    finally:
        fcntl.flock(lock_fh, fcntl.LOCK_UN)
        lock_fh.close()

    chk = yaml.safe_load(open(IL, encoding="utf-8"))
    for iid in ("ISS-172", "ISS-239"):
        st = [i.get("status") for i in chk["issues"] if i.get("id") == iid][0]
        print("   %s status = %s" % (iid, st))
    print("✅ dispatch_log.yaml 已原子写: 追加 ISS-172 → sw-lead 续派记录 (redispatch=True)")
    print("✅ issue_log.yaml 已原子写: ISS-172 note 追加 (status 保持 fixing)")
    print("★**零外发 · 未替老板拍板 · 不碰 PCB 布线/布局/板/网表 · 不写别人的分片** ★")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
