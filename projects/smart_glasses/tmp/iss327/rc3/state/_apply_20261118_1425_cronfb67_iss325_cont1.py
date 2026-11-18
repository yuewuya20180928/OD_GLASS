#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-325 cont1 brief 追加 (★status 保持 fixing★) · cron fb67af40 · 2026-11-18 14:2x"""
from __future__ import annotations
import fcntl, os, shutil, tempfile, yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
DL = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
NOW = "2026-11-18"
STAMP = "20261118_1425"

CONT = open(os.path.join(HERE, "dispatch_briefs",
                         "ISS-325_hw_s8_leftupper_layout_rehearsal_cont1.md"), encoding="utf-8").read()


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
        i325 = idx.get("ISS-325")
        if not i325:
            print("· ISS-325 不存在 (★异常★)"); return 1
        tb = i325.get("task_brief") or ""
        if "ISS-325 · hw-lead · ★★cont1 续做" not in tb:
            i325["task_brief"] = tb + "\n\n---\n\n" + CONT
            applied.append("ISS-325 task_brief += cont1 (★原 brief 全文保留★) · status 保持 fixing")
        else:
            applied.append("ISS-325 cont1 已在 brief 里 (跳过)")
        i325["dispatched_at"] = NOW
        out = dict(log); out["issues"] = issues
        shutil.copy2(LOG, LOG + ".bak_cronfb67_%s_iss325_cont1" % STAMP)
        atomic_write(LOG, yaml.safe_dump(out, allow_unicode=True, sort_keys=False, width=100000))

        dl = yaml.safe_load(open(DL, encoding="utf-8")) or {}
        disp = dl.get("dispatches") or []
        if not any(isinstance(d, dict) and d.get("issue") == "ISS-325" and "cont1" in str(d.get("brief"))
                   for d in disp):
            disp.append({
                "issue": "ISS-325", "agent": "hw-lead", "at": NOW,
                "brief": ("★**cont1 续做 (★上一趟 13:35 被父 run 连带 abort·但两条沙盒臂【还在后台真跑】"
                          "PID 1043798/1044628·已跑 1h20m★)** ★ "
                          "★**绝对不许重跑那两条臂** ⇒ 等它们跑完 → 收割读数 → 填 4 处 `__XXX__` 占位符 + 补 §9 "
                          "+ 补交卷页 B1/B2/B4/B5 (★gate_check Q1 现在 15/18·缺的就是这 3 格★) + 写分片 "
                          "(★hw.yaml 里 `iss325` 命中 = 0★)** ★ "
                          "★**先做与臂无关的 4 件, 再收割臂** ⇒ ★**这样就算又被 abort, 本单也已经从「4 处占位符 + "
                          "缺 §9 + 缺 B1/B2/B4/B5 + 分片未写」推进到「只差臂的读数」** ★ "
                          "★**status 全程保持 fixing ⇒ 无 open 窗口 ⇒ 兄弟 job 775d9893 不会重复派** ★"),
                "job": ("cron fb67af40 (ARS45 队列自动派活) · ★派活时刻 2026-11-18 14:2x · "
                        "★**status 全程 fixing ⇒ 无 open 窗口 ⇒ 兄弟 job 775d9893 不会重复派** ★"),
            })
            applied.append("dispatch_log 追加 ISS-325 cont1")
        dl["dispatches"] = disp
        shutil.copy2(DL, DL + ".bak_cronfb67_%s_iss325_cont1" % STAMP)
        atomic_write(DL, yaml.safe_dump(dl, allow_unicode=True, sort_keys=False, width=100000))
        for a in applied:
            print("· %s" % a)
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
