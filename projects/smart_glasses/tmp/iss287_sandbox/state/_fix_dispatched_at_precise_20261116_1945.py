#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_fix_dispatched_at_precise_20261116_1945.py —— ★★把在飞 3 条的 `dispatched_at` 从【日期】补成【日期+时刻】★★

★★为什么修 (★main 2026-11-16 19:4x 实测★)★★
  ★**台账里 152/247 条 `dispatched_at` 只写到日期** (★`"2026-11-16"`★) ⇒ ★**派活时刻丢失** ★
  ⇒ ★**下游判据 `alignment_check` 的僵尸判定把日期当【当天 00:00】⇒ 19:19 刚派出的 3 条被算成「19.5 小时」⇒ 假红** ★
  ⇒ ★**本单只给【当前在飞且已知确切派活时刻】的 3 条补上真实时刻 (★不是编的: 取自 `sessions_list` 的 startedAt 毫秒时间戳★)** ★
  ⇒ ★**其余 149 条历史记录 【一字不改】** (★历史派活时刻已不可知 ⇒ 编一个就是造假★) ★

★★真实时刻来源 (★可复核★)★★
  ★**ISS-249 → hw-lead**: session `agent:hw-lead:subagent:8f4758a2-...` startedAt `1794827961479` ⇒ **2026-11-16 19:19:21** ★
  ★**ISS-250 → sw-lead**: session `agent:sw-lead:subagent:83050de2-...` startedAt `1794827971464` ⇒ **2026-11-16 19:19:31** ★
  ★**ISS-251 → mech-lead**: session `agent:mech-lead:subagent:6348eece-...` startedAt `1794827982497` ⇒ **2026-11-16 19:19:42** ★
  ⇒ ★**与 `state/dispatch_log.yaml` 里这 3 条的 `at: '2026-11-16'` 一致 (★同日★) ⇒ 自洽** ★

★★落账纪律 (★项目既有范式★)**: flock + 锁内重读 + 只改 3 个字段 + 原子写 + yaml 往返自检 + 逐条 diff 实测
"""
import datetime as _dt
import fcntl
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import yaml  # noqa: E402

LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
BAK = LOG + ".bak_20261116_1945_fix_dispatched_at"

# ★**派活时刻 = sessions_list startedAt (★毫秒时间戳 → 本地时区★) ★**
DISPATCHED = {
    "ISS-249": "2026-11-16 19:19",
    "ISS-250": "2026-11-16 19:19",
    "ISS-251": "2026-11-16 19:19",
}

NOTE_ADD = (
    "\n★2026-11-16 19:4x (cron 775d9893 继续执行后继计划) ★**main 补本单 `dispatched_at` 的派活时刻** "
    "(★原值只有日期 `2026-11-16` ⇒ 派活时刻丢失 ⇒ `alignment_check` 僵尸判定把【日期】当【当天 00:00】"
    "⇒ 刚派出 4 分钟的单被误报成「19.5 小时僵尸 fixing」= 假红★): ★**新值 `2026-11-16 19:19` "
    "(★来源 = 该子会话 `sessions_list` 的 startedAt 毫秒时间戳实测, 非编造★)** ★ ⇒ ★**判据侧同步修在 `alignment_check.py` "
    "(★当日 + 只有日期 ⇒ 僵尸判据本日不可判, 不算违规★)** ★"
)


def dump_atomic(obj, path, width):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        yaml.safe_dump(obj, f, allow_unicode=True, sort_keys=False, default_flow_style=False, width=width)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
    dfd = os.open(os.path.dirname(path), os.O_RDONLY)
    try:
        os.fsync(dfd)
    finally:
        os.close(dfd)


def main():
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        raw = open(LOG, encoding="utf-8").read()
        doc = yaml.safe_load(raw)
        items = doc if isinstance(doc, list) else doc.get("issues")
        width = None
        for w in (60, 80, 100, 120, 200):
            if yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, default_flow_style=False, width=w) == raw:
                width = w
                break
        print("★当前排版 width = %s" % (width or "探不到 (★用 200 兜底★)"))
        width = width or 200

        touched = []
        for it in items:
            iid = str(it.get("id"))
            if iid not in DISPATCHED:
                continue
            old = str(it.get("dispatched_at") or "")
            new = DISPATCHED[iid]
            if old == new:
                continue
            if old and len(old.strip()) != 10:
                print("ℹ️ %s 的 dispatched_at 已是带时刻的值 %r ⇒ 不动" % (iid, old))
                continue
            shutil.copy2(LOG, BAK)
            it["dispatched_at"] = new
            note = it.get("note") or ""
            if "19:4x (cron 775d9893 继续执行后继计划) ★**main 补本单 `dispatched_at`" not in note:
                it["note"] = note + NOTE_ADD
            touched.append((iid, old, new))

        if not touched:
            print("ℹ️ 无需改动")
            return 0

        a = yaml.safe_load(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, default_flow_style=False, width=width))
        b = yaml.safe_load(yaml.safe_dump(a, allow_unicode=True, sort_keys=False, default_flow_style=False, width=width))
        if yaml.safe_dump(a, allow_unicode=True, sort_keys=False, default_flow_style=False, width=width) != \
           yaml.safe_dump(b, allow_unicode=True, sort_keys=False, default_flow_style=False, width=width):
            print("❌ yaml 往返不一致 ⇒ 放弃写")
            return 1
        dump_atomic(doc, LOG, width)
        for iid, old, new in touched:
            print("✅ %s.dispatched_at %r → %r" % (iid, old, new))
        print("★备份 %s" % os.path.basename(BAK))
    return 0


if __name__ == "__main__":
    sys.exit(main())
