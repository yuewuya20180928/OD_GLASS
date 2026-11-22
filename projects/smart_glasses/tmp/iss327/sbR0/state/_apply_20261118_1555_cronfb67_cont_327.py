#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-327 cont3 brief 追加 (★status 保持 fixing★) · cron fb67af40 · 2026-11-18 15:55

★**为什么又续做**: cont2 (15:12 起跑) 的子会话在 **15:51:05 被 abort 打断**
  (★最后一条 assistant 消息 stopReason=aborted · errorMessage="This operation was aborted"·
  最后一句话 = "Now I have everything. Let me write the main deliverable — the SOP:"★)
  ⇒ ★**它的 write 工具调用发出去了但文件没落地** ⇒ ★**这一趟是纯写型: 读数全在盘上, 只做归并 + 落字 + 分片 + 自证** ★

★**main 15:5x 本机实读 (不抄 agent 报告)**:
  · SW/ONETRIP_SW_POSTRENAME_GATE_SOP.md      → **不存在**
  · logs/iss327/02_postrename_gate_table.md   → **不存在**
  · HANDOFF/2026-11-18_sw-lead_ISS327_*.md    → **1,646 B · mtime 15:24 · 只有 B0~B9 标题骨架**
  · state/fragments/sw.yaml 里 iss327 命中    → **0**
  · find tmp/iss327 -type l | wc -l           → **0** (★事故根因修掉的代码级证据·可直接引用★)
"""
from __future__ import annotations
import fcntl, os, shutil, tempfile, yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
DL = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
NOW = "2026-11-18"
STAMP = "20261118_1555"
MARK = "★派活标记=CONT3-20261118-1555★"
ISS = "ISS-327"
AGENT = "sw-lead"
BRIEF_FN = "ISS-327_sw_postrename_gate_sop_cont3.md"
NOTE = (
    "★**15:55 · cron fb67af40 续做重派 (cont3)** ★ cont2 的子会话在 15:51:05 被 abort 打断 "
    "(★最后一句 = 「Now I have everything. Let me write the main deliverable — the SOP:」·"
    "write 调用发出但文件没落地★) ⇒ 本趟是【纯写型】: "
    "① 先填交卷页 B0~B9 九块正文 (★交卷页优先于交付页正文·项目反复踩的坑★) "
    "② 写 SW/ONETRIP_SW_POSTRENAME_GATE_SOP.md (★不存在★) "
    "③ 写 logs/iss327/02_postrename_gate_table.md (★不存在★) "
    "④ 分片 (frag_write.py) + merge rc=0 + gate_check Q1 18/18 "
    "★**事实源全在盘上, 不许重跑任何闸**: logs/iss327/24_four_arm_measure.txt (15:46 · 四臂 rc 表 + rc=2 逐闸语义) "
    "· 25_control_validity.txt (15:48 · 逐臂唯一变量 + 软链数) · 23_rev_selftest_run.log (15:43 · 反向用例: "
    "注入新真隐患 TP_TEMP_ISSX ⇒ 重建注册表前后 rc 都 = 1 ⇒ **没被 --freeze-registry 洗白**) "
    "★**main 已核到一处必须如实写的真发现**: 24 号文件 §② 里 sbCtl 的「改名后位号命中」也是 797 处 / 12 份 "
    "(与 BASELINE 相同) ⇒ 该判据口径是【全量】不是【增量】⇒ 对照臂干净的判据口径要么改成增量 (臂内 − BASELINE) "
    "要么在 §B7 明写它不能作为对照臂干净的证据 ⇒ **不许把 797 写成 0 · 不许改数据迁就判据**"
)


def atomic_write(path, text):
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_", suffix=".yaml")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text); f.flush(); os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def main() -> int:
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        log = yaml.safe_load(open(LOG, encoding="utf-8")) or {}
        issues = log.get("issues") or []
        idx = {i.get("id"): i for i in issues}
        applied = []
        it = idx.get(ISS)
        if not it:
            print("· %s 不存在 (★异常★)" % ISS)
            return 1
        body = open(os.path.join(HERE, "dispatch_briefs", BRIEF_FN), encoding="utf-8").read()
        tb = it.get("task_brief") or ""
        if MARK not in tb:
            it["task_brief"] = tb + "\n\n---\n\n" + body
            applied.append("%s task_brief += %s (★原 brief 全文保留★) · status 保持 fixing" % (ISS, MARK))
        else:
            applied.append("%s %s 已在 brief 里 (跳过)" % (ISS, MARK))
        it["dispatched_at"] = NOW
        it["note"] = (it.get("note") or "") + ("\n" + NOTE)
        out = dict(log); out["issues"] = issues
        shutil.copy2(LOG, LOG + ".bak_cronfb67_%s_cont_327" % STAMP)
        atomic_write(LOG, yaml.safe_dump(out, allow_unicode=True, sort_keys=False, width=100000))

        dl = yaml.safe_load(open(DL, encoding="utf-8")) or {}
        disp = dl.get("dispatches") or []
        if not any(isinstance(d, dict) and d.get("issue") == ISS and MARK in str(d.get("brief")) for d in disp):
            disp.append({
                "issue": ISS, "agent": AGENT, "at": NOW,
                "brief": MARK + " " + NOTE,
                "job": ("cron fb67af40 (ARS45 队列自动派活) · ★派活时刻 2026-11-18 15:55 · "
                        "★**续做重派 (★cont2 子会话 15:51:05 被 abort·已落不少盘·本轮从已完成位置续·"
                        "status 保持 fixing ⇒ 无 open 窗口·兄弟 job 775d9893 不会重复派★)** ★"),
            })
            applied.append("dispatch_log 追加 %s cont3" % ISS)
        dl["dispatches"] = disp
        shutil.copy2(DL, DL + ".bak_cronfb67_%s_cont_327" % STAMP)
        atomic_write(DL, yaml.safe_dump(dl, allow_unicode=True, sort_keys=False, width=100000))
        for a in applied:
            print("· %s" % a)
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
