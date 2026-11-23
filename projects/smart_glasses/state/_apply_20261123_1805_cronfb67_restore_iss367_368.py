#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
★**cron fb67af40 (ARS45 队列自动派活) · 2026-11-23 18:0x · 撤回本 job 对兄弟 job ISS-367/368 的 task_brief/note 覆盖** ★

★**事故 (★本机实读·不推责任·先修★)**:
  ★**兄弟 job 775d9893 在同一分钟 (17:5x) 新开并直接派出 ISS-367 (mech-lead · MECH E-9 LED 窗口规格同趟重算) + ISS-368 (sw-lead · SW09 三处同批落地补丁)** ★
  ⇒ ★**而本 job 18:0x 也想开 ISS-367 (sw-lead · 腿 B) + ISS-368 (mech-lead · E-9) ⇒ ID 撞车** ★
  ⇒ ★**本 job 的开单脚本走的是「已存在 ⇒ status→fixing + brief/note 刷新」那条幂等分支 ⇒ ★★把兄弟 job 那两条的 `task_brief` 与 `note` 覆盖成了本 job 的版本★★** ★
  ⇒ ★★⇒ 后果: 台账里 ISS-367/368 指向的【任务书文件】与【兄弟 job 已经派出去、agent 正在跑的那份】对不上 ⇒ ★★兄弟 job 的签收闸会按台账里的任务书路径/大小判 ⇒ 假红 ⇒ 交卷页判错★★ ★
  ⇒ ★**⇒ 本脚本把这两个字段从本 job 落盘前的备份逐字还原 (★title/desc/owner/status 本 job 没碰·只碰了 task_brief/note★)** ★
  ⇒ ★**★同时: 本 job 不再新开这两个 ID (★兄弟 job 已经派出去了·两个 agent 会话正在跑·★再派一遍 = 同一 agent 两个写会话 = 撞 R18 分片合并丢 12%~38%★)★** ★

★**零写板 · 零落表 · 零改别人的分片 · 不改兄弟 job 的 title/desc/owner/status · 零外发**
"""
from __future__ import annotations

import fcntl
import os
import shutil
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
BAK = os.path.join(HERE, "issue_log.yaml.bak_20261123_1800_cronfb67_open_iss367_368")
STAMP = "20261123_1805_cronfb67_restore_iss367_368"
TARGETS = ("ISS-367", "ISS-368")


def atomic_write(path: str, text: str) -> None:
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_", suffix=".yaml")
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
    applied = []
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)

        cur = yaml.safe_load(open(LOG, encoding="utf-8")) or {}
        old = yaml.safe_load(open(BAK, encoding="utf-8")) or {}
        cur_idx = {i.get("id"): i for i in (cur.get("issues") or [])}
        old_idx = {i.get("id"): i for i in (old.get("issues") or [])}

        shutil.copy2(LOG, LOG + ".bak_" + STAMP)

        for iid in TARGETS:
            c = cur_idx.get(iid)
            o = old_idx.get(iid)
            if not c or not o:
                applied.append("★%s 在当前台账/备份里有一边缺失 ⇒ 不动 (fail-closed)" % iid)
                continue
            changed = []
            for field in ("task_brief", "note"):
                if c.get(field) != o.get(field):
                    c[field] = o.get(field)
                    changed.append(field)
            applied.append("★%s ⇒ 还原 %s (★兄弟 job 的原件·★title/desc/owner/status 本 job 未碰·保持原样★)"
                           % (iid, ("+".join(changed) if changed else "本就一致·无需改")))

        cur["issues"] = list(cur_idx.values())
        atomic_write(LOG, yaml.safe_dump(cur, allow_unicode=True, sort_keys=False, width=10**6))

    for a in applied:
        print("·", a)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
