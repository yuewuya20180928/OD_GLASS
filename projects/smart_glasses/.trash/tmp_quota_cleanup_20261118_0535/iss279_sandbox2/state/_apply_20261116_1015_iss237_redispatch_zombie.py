#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20261116_1015_iss237_redispatch_zombie.py
★main (moli) 派活落账 · 2026-11-16 10:15 (cron fb67af40 队列自动派活)★

★★**为什么做这件事 (★本轮自己实跑, 不是抄任何交卷报告★)★★ ★★
· ★**`python3 state/advance.py --json` ⇒ internal = []** (★本轮 advance.py 自己算出来是空的★)
· ★**原因 = 僵尸 fixing**: ★**ISS-237 (hw-lead) status=fixing, 但它的会话已经死了** ★
  · 09:50:25 → 09:54:25 那轮 = ★**被上游 529 过载掐死** (★连着 4 条 `overloaded_error (2064)/(529)·stopReason=error★)
  · ★**main 10:1x 逐条数过那份 transcript: 22 条 assistant 消息, 全部是只读 (ls / md5sum / grep / 官网 fetch)⇒ tool_use 里【没有一个写操作】★**
  · ★**main 10:1x 逐字节复核交付物: `HW/check_step1_parts_spec.py` 不在盘 · `HANDOFF/*ISS237*` 不在盘
    · `HW/STEP1_PARTS_SPEC.md` mtime 仍 Nov 11 19:33 · `HW/PART_ALTERNATIVES_REGISTRY.md` mtime 仍 Nov 11 10:35
    ⇒ 那一轮【一个字都没写盘】⇒ ISS-237 = 僵尸 fixing (★占着 hw-lead 名额, 却没人干活★)** ★
  · ★**父 job 也没救回来**: ★**派它的 cron 775d9893 父会话自己在 09:53:51 就死于同一波 529 (transcript 最后三条全是 error)★**
    ⇒ ★**没有任何在跑的会话会接手 ISS-237 ⇒ 只能由本 job 重派** ★
· ★**后果 (★main 实跑 advance.py 内部逻辑复现★)**: ★**in_flight 规则 = "该 agent 名下已有 fixing 的 issue ⇒ 本轮不再给它派新活"**
  ⇒ ★**hw-lead 名额被僵尸占着 ⇒ 本轮 internal 段空 ⇒ 主线队列静默停摆** ★
· ★**处置**: ★**本轮把 ISS-237 重新派出去 (taskName=queue_iss237, runTimeout=5400s ⇒ 90 分钟, 绕开 8 分钟默认超时★)★**
  ⇒ ★**ISS-237 status 保持 fixing (★本来就是 fixing, 本轮不重复标★) ★**

★★**本轮派活前 main 自己实跑验证过的事实 (★不是抄任何交卷报告★)★★ ★★
· ★**受保护 5 个 md5 (main 10:1x 实测)**: 网表 `34132f7e40a241e1fae1476be0eafbd5` · 脚表 `b21b743a7702d30729f0d653c15392df`
  · BOM `c195a117ff17490d4d1e1a5b8f1995a7` · 板 `611b869e13518c3c023fb178f91a0075` · `.kicad_pro` `3e504d2be83152e337949723e909be1b` ★
  ⇒ ★**与 ISS-237 brief 里写的基线逐字一致 ⇒ 上一轮没偷偷改过盘** ★
· ★**ISS-236 的两个交付物已在盘** (★`HW/SCHEMATIC_FINALIZATION_CLOSEOUT.md` 20470 B mtime 09:36 · `state/land_v_values.py` 84185 B mtime 09:38★)
  ⇒ ★**⇒ 派活书里明写「ISS-236 已交卷落 verified, 本单不许落表」** ★
· ★**`state/check_brief_commands.py --brief-file state/tasks/advance_iss237.md` ⇒ rc=0** ★
· ★**sw-lead / mech-lead 名下【一条 open 都没有】** (★sw-lead: closed 10 + verified 32 · mech-lead: closed 14 + verified 27 + deferred 3★)
  ⇒ ★**⇒ 本轮只派 hw-lead 一条** ★

★★**边界 (本脚本)★★ ★★
· ★**只写 `state/dispatch_log.yaml` (追加一条派活记录, 可追溯) + `state/issue_log.yaml` 里 ISS-237 的 note (追加一段续派记录)★** ★
· ★**不改 `state/issue_log.yaml` 的 status (★ISS-237 本来就是 fixing★)** ★
· ★**不碰 `PROJECT_TRACKER.md` §0** · ★**不写任何 agent 的分片** · ★**不碰板 / 布线 / 布局** ★
· ★**零外发** · ★**不替老板拍板** (★P2 屏版本是 main 级选型待签, 本单只给并列候选 + 推荐★) ★
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

BRIEF = (
    "★**续做派活 (★main 2026-11-16 10:1x 实测: 上一轮 09:50 的 spawn 被【上游 529 过载】掐死 ⇒ ISS-237 是僵尸 fixing·"
    "本轮重派·runTimeout 5400s 绕开 8 分钟默认超时★)** ★\n"
    "★**上一轮零写盘 (main 10:1x 逐字节复核): `HW/check_step1_parts_spec.py` 不在盘 · `HANDOFF/*ISS237*` 不在盘 · "
    "`HW/STEP1_PARTS_SPEC.md` mtime 仍 Nov 11 19:33 ⇒ 本单等于从零开始★** ★\n"
    "★**受保护 5 个 md5 (main 10:1x 实测) = 网表 34132f7e… · 脚表 b21b743a… · BOM c195a117… · 板 611b869e… · "
    ".kicad_pro 3e504d2b… ⇒ 交卷时逐字节不变★** ★\n"
    "★**顺序纪律: 先写盘 → 再补自证输出 → 最后跑验收命令 (★上一轮就死在「只读侦察没写盘」★)★** ★\n"
    "★**抗 529 纪律: 撞上 overloaded_error 就原地重试, 且每拿到一个结论立刻写盘 (别攒到最后一起写)★** ★"
)

NOTE = (
    "\n\n★2026-11-16 10:1x (cron fb67af40 队列自动派活) 续派记录 ★\n"
    "· ★**上一轮 ISS-237 会话 = 僵尸 fixing**: 09:50:25→09:54:25 (`agent:hw-lead:subagent:da6572a5` / 88c14231) "
    "连撞 4 条 `overloaded_error (2064)/(529)` ⇒ status=failed, runtime 242s ⇒ ★**零写盘 (main 逐条数过 transcript: "
    "全是只读 ls/md5sum/grep/官网 fetch)★** ⇒ ★**父 job cron 775d9893 自己 09:53:51 也死于同一波 529 ⇒ 无人接手★** ★\n"
    "· ★**main 10:1x 逐字节复核**: `HW/check_step1_parts_spec.py` 不在盘 · `HANDOFF/*ISS237*` 不在盘 · "
    "`HW/STEP1_PARTS_SPEC.md` mtime 仍 Nov 11 19:33 · 受保护 5 md5 与基线逐字一致 (⇒ 没被偷偷改过)★ ★\n"
    "· ★**本轮处置**: 重派 hw-lead (taskName=queue_iss237 · runTimeout=5400s) ⇒ ★**status 保持 fixing** ★\n"
    "· ★**ISS-236 已于 09:47 落 verified (main 自己实跑 8 道闸全绿) ⇒ 本单不许落表, 只做口径收死 + 清账 + 对账表 + 门禁★** ★\n"
    "· ★**sw-lead / mech-lead 名下无任何 open ⇒ 本轮只派 hw-lead 一条** ★ ★\n"
    "· ★**零外发** · ★**未替老板拍 P2 屏版本 (main 级选型待签)** ★"
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
    shutil.copy2(DL, DL + ".bak_20261116_1015_iss237_redispatch")
    shutil.copy2(IL, IL + ".bak_20261116_1015_iss237_redispatch")

    lock_fh = open(LOCK, "a+")
    try:
        fcntl.flock(lock_fh, fcntl.LOCK_EX)

        # ---- dispatch_log: 追加一条派活记录 ----
        dl = yaml.safe_load(open(DL, encoding="utf-8")) if os.path.exists(DL) else {"dispatches": []}
        dl.setdefault("dispatches", []).append({
            "issue": "ISS-237", "agent": "hw-lead", "at": TODAY, "brief": BRIEF[:300],
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

        # ---- issue_log: ISS-237 的 note 追加一段 (status 不动) ----
        il = yaml.safe_load(open(IL, encoding="utf-8"))
        hit = 0
        for it in il.get("issues") or []:
            if it.get("id") == "ISS-237":
                it["note"] = (it.get("note") or "") + NOTE
                it["dispatched_at"] = TODAY
                hit += 1
        if hit != 1:
            raise SystemExit(f"★ISS-237 命中数异常 = {hit} ⇒ 中止")
        _atomic_write(IL, yaml.safe_dump(il, allow_unicode=True, sort_keys=False, width=200))
    finally:
        fcntl.flock(lock_fh, fcntl.LOCK_UN)
        lock_fh.close()

    chk = yaml.safe_load(open(DL, encoding="utf-8"))
    chk_i = yaml.safe_load(open(IL, encoding="utf-8"))
    st = [i.get("status") for i in chk_i["issues"] if i.get("id") == "ISS-237"][0]
    print("✅ dispatch_log.yaml 已原子写 (flock + 锁内重读 + tmp/os.replace):")
    print(f"   - 追加 ISS-237 → hw-lead 续派记录 (★2026-11-16 10:1x·僵尸 fixing 复活·529 过载死因★)")
    print(f"   - dispatch 总条数: {len(chk['dispatches'])}")
    print("✅ issue_log.yaml 已原子写: ISS-237 note 追加续派记录")
    print(f"   - ISS-237 status = {st} (★保持 fixing, 本轮不重复标★)")
    print("   ★**零外发 · 未替老板拍板 · 不碰 PCB 布线/布局** ★")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
