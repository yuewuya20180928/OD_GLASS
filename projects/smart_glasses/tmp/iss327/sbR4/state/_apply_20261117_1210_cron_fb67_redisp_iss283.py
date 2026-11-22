#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20261117_1210_cron_fb67_redisp_iss283.py
moli (项目总工) 2026-11-17 12:1x · job fb67af40「ARS45 队列自动派活」
★ISS-283 (hw-lead) 半落地僵尸 ⇒ 【续做】重派落账 (★status 保持 fixing · 只补留痕 + 派活日志★)

★★**本 job 自己查盘 + 读 transcript, 不抄任何兄弟 job 的报告★★:
· `python3 state/advance.py --json` ⇒ internal = [] (★hw-lead 名额被 ISS-283 (fixing) 占着 ·
  sw-lead 名额被 ISS-285 (fixing) 占着 · mech-lead 名额被 ISS-286 (fixing) 占着 ⇒ 三个名额全满★)
· ★**ISS-283 的会话是半落地僵尸**: `agent:hw-lead:subagent:eeecf73f`
  (11:42:49 → 12:07:26 · status=timeout · abortedLastRun=true) ⇒ transcript 末条 = 12:04:46
  "Successfully replaced 1 block(s) in .../HANDOFF/2026-11-17_hw-lead_ISS283_V2解锁与W4G5落表.md"
  ⇒ ★**交卷单骨架刚建完就断了**★ (★12:07:24 最后一条 exec 没等到结果★)
· ★**盘上实况 (本 job 实测 12:0x)**: 交卷单 = **3188 B 骨架** (B1 有进度 · B2/B3/⑩/⑪/③/收尾 全「⏳」) ·
  `grep -c "iss283\|ISS-283" state/fragments/hw.yaml` = **0** ⇒ **分片零写** ·
  网表 `2f17650c…` / 脚表 `6ea65fec…` / BOM `ea5f4f58…` **与 09:58 落表后完全一致** ⇒ ★**三件落表 (A3/B2/B3) 一件都没落**★ ·
  台账里**还没有 LANDING_AUTH 块** ⇒ ★**B1 的授权通道已写好但还没被用过**★ ·
  `HW/check_land_row_anchors.py` 已改 (AUTH_BLOCK_RE + T10~T16) · `state/land_v_values.py` 16.3 段已写 ·
  `logs/iss283/selftest_lv4.log` 末行 = `✅ rc=0: 落表器自测全过 (14 条) · 真盘零写入` ⇒ ★**⑩-a 已修好**★ ·
  板 `611b869e…` mtime 仍 `2026-11-06 07:07:17` ⇒ **零写板**★ · pid 740455 已不存在 ⇒ **无僵尸进程**★

★★**本脚本做的事 (边界写死)★★:
· ★**只写 `state/issue_log.yaml` + `state/dispatch_log.yaml` (flock + 锁内重读 + tmp/os.replace 原子写)★★
· ISS-283: ★**status 保持 fixing** (★续做重派不是新单★) + note 追加僵尸实况 + dispatched_at 刷新
· dispatch_log: 追加一条 ISS-283 / hw-lead 的【续做重派】条目 (★brief 指向 cont1 任务书★)
· ★**不碰板 / 网表 / 脚表 / BOM / 任何 agent 的分片 / 决策页 / outbox / 别人的 issue****
· ★**零外发 · 零采购 · 不替老板拍板****
"""
import fcntl
import os
import shutil
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
IL = os.path.join(HERE, "issue_log.yaml")
DL = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
TODAY = "2026-11-17"

NOTE = (
    "\n\n★**2026-11-17 12:1x (cron fb67af40 队列自动派活) 半落地僵尸 ⇒ 【续做】重派 (★不是新单·status 保持 fixing★)** ★\n"
    "· ★**僵尸实况 (本 job 自己查盘 + 读 transcript)**: 子会话 `agent:hw-lead:subagent:eeecf73f` "
    "(11:42:49 → 12:07:26 · status=timeout · abortedLastRun=true) ⇒ transcript 末条 = 12:04:46 "
    "\"Successfully replaced 1 block(s) in .../HANDOFF/2026-11-17_hw-lead_ISS283_V2解锁与W4G5落表.md\" "
    "⇒ ★**交卷单骨架刚建完就断了**★ ⇒ ★**pid 740455 已不存在 ⇒ 无僵尸进程在改盘**★\n"
    "· ★**盘面半成品 (本 job 实测 12:0x)**: 交卷单 = **3188 B 骨架** (B1 有进度 / B2·B3·⑩·⑪·③·收尾·自检 全「⏳」) · "
    "`grep -c \"iss283\\|ISS-283\" state/fragments/hw.yaml` = **0** ⇒ **分片零写** · "
    "网表 `2f17650c…` / 脚表 `6ea65fec…` / BOM `ea5f4f58…` **与 09:58 落表后完全一致** ⇒ "
    "★**三件落表 (A3 / B2 / B3) 一件都没落**★ · 台账里**还没有 LANDING_AUTH 块** ⇒ "
    "★**B1 授权通道已写好但还没被用过**★ · `HW/check_land_row_anchors.py` 已改 (AUTH_BLOCK_RE + T10~T16) · "
    "`state/land_v_values.py` 16.3 授权段已写 · `logs/iss283/selftest_lv4.log` 末行 = "
    "`✅ rc=0: 落表器自测全过 (14 条) · 真盘零写入` ⇒ **⑩-a 已修好**★ · "
    "板 `611b869e…` mtime 仍 `2026-11-06 07:07:17` ⇒ **零写板**★\n"
    "· ★**续做任务书** = `state/dispatch_briefs/ISS-283_hw_v2_unlock_w4_g5_landing_cont1.md` "
    "(10413 B · ★派活前已过 `python3 state/check_brief_commands.py --brief-file …` ⇒ rc=0 零告警★) ⇒ "
    "★**第一件事 cat 全文 (含原任务书全文路径 + ⑪ 追加块原样抄录)****\n"
    "· ★**★不许重做已落盘的两件**: ★**B1 守卫授权通道 (`HW/check_land_row_anchors.py`)· "
    "落表器授权块写入 (`state/land_v_values.py` §16.3)· ⑩-a 已落过判定 (用例 12 改判红)**★ ⇒ "
    "★**本单真正剩下的是: A3 真落 + B2 + B3 + ⑩-b + ⑪ (HW 侧 C6 台账化·★不许用 `--update-baseline` 消红★) + "
    "③ 板侧清单三条 + 收尾 rc (★必须落表之后才跑★) + 交卷单填满 + 分片**★\n"
    "· ★**本 job 同轮还查到**: ISS-285 (sw-lead) 会话 `a2da41cd` 12:00:36 **done** (★交卷已完成·情形一·等 ISS-283 落 verified★) "
    "⇒ ★**sw-lead 名额空着但本单无 open 待办 ⇒ 本轮不派**★ · "
    "ISS-286 (mech-lead) 会话 `a6a8ca76` 11:41 起 **running** ⇒ ★**mech-lead 名额被占 ⇒ 本轮不派**★ ⇒ "
    "★**一个 agent 同时只派 1 条的纪律不变**★\n"
)

BRIEF_HEAD = (
    "★**续做重派 (★11:42~12:07 那一趟会话被掐 ⇒ 盘上已有半成品: 交卷单 3188 B 骨架 + B1 守卫授权通道已改 + "
    "落表器 §16.3 授权块已写 + ⑩-a 落表器自测已 rc=0 ⇒ 【三件落表一件没落】⇒ 从盘上现状继续, 不要从零重做★)** ⇒ "
    "★**完整续做任务书全文 = `state/dispatch_briefs/ISS-283_hw_v2_unlock_w4_g5_landing_cont1.md` (10413 B) ⇒ 第一件事先 cat 全文**★\n"
    "★**原任务书全文** = `state/dispatch_briefs/ISS-283_hw_v2_unlock_w4_g5_landing.md` (14346 B · §①~§⑦ + ⑩ 追加块) ⇒ 也 cat 一遍★\n"
    "★**★不许重做已落盘的两件**: B1 守卫授权通道 (`HW/check_land_row_anchors.py` · T10~T16) · "
    "落表器授权块写入 (`state/land_v_values.py` §16.3) · ⑩-a 已落过判定 (用例 12 改判红)★\n"
    "★**★剩下的是**: A3 真落 (`--decision V-2=1 --apply`) → B2 (Q_PG pad1↔pad3) → B3 (68Ω/55Ω) → "
    "⑩-b (preflight P5/P6 + commit_order D0) → ⑪ (HW 侧 C6 改「落表台账为准」· ★不许 `--update-baseline`★) → "
    "③ 板侧清单三条 → 收尾 rc (★必须落表之后才跑★) → 交卷单填满 (★骨架已在, 直接填★) → 分片 (★现在 grep = 0★)**★\n"
)


def atomic_write(path: str, data) -> None:
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix="." + os.path.basename(path) + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False, width=200)
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def main() -> int:
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        il = yaml.safe_load(open(IL, encoding="utf-8")) or {}
        dl = yaml.safe_load(open(DL, encoding="utf-8")) or {}
        shutil.copy2(IL, IL + ".bak_20261117_1210_cron_fb67_redisp_iss283")
        shutil.copy2(DL, DL + ".bak_20261117_1210_cron_fb67_redisp_iss283")

        hit = 0
        for it in il.get("issues") or []:
            if it.get("id") != "ISS-283":
                continue
            hit += 1
            if it.get("status") != "fixing":
                raise SystemExit("★ISS-283 status 不是 fixing (=%s) ⇒ 拒绝落账" % it.get("status"))
            it["note"] = (it.get("note") or "") + NOTE
            it["dispatched_at"] = TODAY
            it["task_brief"] = BRIEF_HEAD + (it.get("task_brief") or "")
        if hit != 1:
            raise SystemExit("★ISS-283 不唯一 (命中 %d 条) ⇒ 拒绝落账" % hit)

        dl.setdefault("dispatches", []).append({
            "issue": "ISS-283",
            "agent": "hw-lead",
            "at": TODAY,
            "brief": BRIEF_HEAD.strip(),
            "job": ("★派活方 = cron fb67af40 (ARS45 队列自动派活) 于 12:1x 派出 · ★上一趟 "
                    "(agent:hw-lead:subagent:eeecf73f · 11:42:49→12:07:26 · timeout/aborted) 是半落地僵尸★ "
                    "⇒ 本条为【续做重派第 1 次】★"),
        })

        atomic_write(IL, il)
        atomic_write(DL, dl)
    print("★落账 OK: ISS-283 保持 fixing + note 追加 + dispatched_at 刷新 + dispatch_log 追加 1 条 (续做重派)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
