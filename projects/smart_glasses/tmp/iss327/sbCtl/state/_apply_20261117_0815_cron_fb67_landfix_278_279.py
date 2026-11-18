#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cron fb67af40 (ARS45 队列自动派活) 2026-11-17 08:1x
★**先落 fixing, 再 spawn** (★硬规则: 反过来会留一个窗口让下一轮 cron 重复派同一个 agent★)
★ISS-278 → mech-lead · ISS-279 → sw-lead
★**纪律**: flock(state/.issue_log.lock) + ★**锁内重读** + ★**原子写** (tmp + fsync + os.replace)
★**只碰这两条的 status (open → fixing) + dispatched_at + dispatch_log 追加** ⇒ 其余字段逐字段比对, 变了就回滚
★**不碰**: 真源 / 分片 / 板 / 网表 / 脚表 / BOM / 任何门禁脚本 / 任何交卷单
"""
import fcntl
import json
import os
import shutil
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
DL = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
BAK = LOG + ".bak_20261117_0815_cron_fb67_landfix_278_279"
TODAY = "2026-11-17"
TARGETS = {"ISS-278": "mech-lead", "ISS-279": "sw-lead"}


def atomic_write(path: str, text: str) -> None:
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix=".tmp_")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def main() -> int:
    os.makedirs(os.path.dirname(LOCK), exist_ok=True)
    with open(LOCK, "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        try:
            # ---------- 锁内重读 ----------
            with open(LOG, encoding="utf-8") as f:
                log = yaml.safe_load(f) or {}
            issues = log.get("issues") or []
            before = {i.get("id"): dict(i) for i in issues}

            dl = {}
            if os.path.exists(DL):
                with open(DL, encoding="utf-8") as f:
                    dl = yaml.safe_load(f) or {}

            changed = []
            for iid, owner in TARGETS.items():
                it = next((x for x in issues if x.get("id") == iid), None)
                if it is None:
                    print("❌ 找不到 %s" % iid)
                    return 2
                if it.get("owner") != owner:
                    print("❌ %s owner=%s ≠ %s ⇒ 中止" % (iid, it.get("owner"), owner))
                    return 2
                st = it.get("status")
                if st == "fixing":
                    print("⚠ %s 已是 fixing ⇒ 跳过 (幂等)" % iid)
                    continue
                if st != "open":
                    print("❌ %s status=%s ≠ open ⇒ 中止 (只派 open)" % (iid, st))
                    return 2
                it["status"] = "fixing"
                it["dispatched_at"] = TODAY
                changed.append(iid)
                dl.setdefault("dispatches", []).append({
                    "issue": iid, "agent": owner, "at": TODAY,
                    "brief": (it.get("task_brief") or "")[:300],
                    "job": "cron fb67af40 (ARS45 队列自动派活)",
                })

            if not changed:
                print("⚠ 无变化, 不落盘")
                return 0

            shutil.copy2(LOG, BAK)
            atomic_write(DL, yaml.safe_dump(dl, allow_unicode=True, sort_keys=False, width=200))
            atomic_write(LOG, yaml.safe_dump(log, allow_unicode=True, sort_keys=False, width=200))

            # ---------- 自检: 只这两条变了 ----------
            with open(LOG, encoding="utf-8") as f:
                after = yaml.safe_load(f) or {}
            aiss = {i.get("id"): i for i in (after.get("issues") or [])}
            drift = []
            for iid, it0 in before.items():
                it1 = aiss.get(iid)
                if it1 is None:
                    drift.append("%s 消失" % iid)
                    continue
                if iid in TARGETS:
                    continue
                if {k: v for k, v in it0.items() if k not in ("status", "dispatched_at")} != \
                   {k: v for k, v in it1.items() if k not in ("status", "dispatched_at")}:
                    drift.append(iid)
            for iid in TARGETS:
                it = aiss.get(iid) or {}
                print("  %s -> %-9s owner=%-9s dispatched_at=%s" % (
                    iid, it.get("status"), it.get("owner"), it.get("dispatched_at")))
            print("  漂移条数 =", len(drift), drift[:5])
            if drift:
                print("❌ 有漂移 ⇒ 回滚")
                shutil.copy2(BAK, LOG)
                return 3
            print("✅ 落盘 OK (锁内重读 + 原子写 + 逐字段比对)")
            return 0
        finally:
            fcntl.flock(lk, fcntl.LOCK_UN)


if __name__ == "__main__":
    raise SystemExit(main())
