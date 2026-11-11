#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_fix_iss198_blocker_ref_20261111.py —— ★修 ISS-198 的幻觉 blocker 引用★

★为什么 (★main 2026-11-11 23:5x 巡检当场抓到★):
  `state/issue_check.py` 报 `ISS-198: source_blocker=HW-PCB-ERC 在 STATE.yaml 里不存在 (幻觉引用)`
  ⇒ ★**HW-PCB-ERC 是我 23:2x 开单时自己编的 ID** (★STATE.yaml 里根本没有它★)
  ⇒ ★**反幻觉判据当场把我自己的幻觉抓出来了** ⇒ 这条闸有效 ⇒ 修数据, 不修判据★

★怎么修 (★最小改动★):
  ISS-198 是 ISS-193 的**直接续单** (ISS-193 = BOM 口径那半 → verified; ISS-198 = [0数据] 那半)
  ⇒ ★**继承 ISS-193 的 source_blocker = `SW-TIM-B1`** (★STATE.yaml 里真实存在★)
  ⇒ ★**改后 C5 反向覆盖集合不变** (★SW-TIM-B1 本来就被覆盖★) ⇒ ★**不会新增"STATE 阻塞未登记 issue"★

★落账纪律 (★与项目既有范式一致★):
  ① flock(state/.issue_log.lock) + **锁内重读**
  ② **只改目标条目** (★ISS-198 一条 · 只动 source_blocker 一个字段★)
  ③ 原子写 (tmp → fsync → os.replace → fsync(dir))
  ④ **yaml 往返复现自检** (★load → dump → load 三次一致★)
  ⑤ **逐条 diff 实测** (★只应有 ISS-198 一处变化★)
"""
import os
import sys
import fcntl
import shutil
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
BAK = LOG + ".bak_iss198_blkref_20261111"

TARGET = "ISS-198"
OLD = "HW-PCB-ERC"
NEW = "SW-TIM-B1"


def load(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def items_of(d):
    if isinstance(d, list):
        return d, None
    for k in ("issues", "items"):
        if isinstance(d.get(k), list):
            return d[k], k
    raise SystemExit("★issue_log.yaml 结构不认识 (既不是 list 也没有 issues/items)")


def dump_atomic(obj, path):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        yaml.safe_dump(obj, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
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
        d = load(LOG)                       # ★锁内重读
        items, _key = items_of(d)
        hit = None
        for it in items:
            if str(it.get("id")) == TARGET:
                hit = it
                break
        if hit is None:
            print("❌ %s 不在 issue_log.yaml 里 ⇒ 不动" % TARGET)
            return 1
        cur = hit.get("source_blocker")
        if cur != OLD:
            print("ℹ️ %s 的 source_blocker 已经是 %r (不是 %r) ⇒ 无需改" % (TARGET, cur, OLD))
            return 0
        # ★STATE 里必须真有 NEW (自检: 别再制造第二个幻觉)
        state = load(os.path.join(PROJ, "STATE.yaml"))
        real = set()
        for dom in (state.get("domains") or {}).values():
            for b in (dom.get("blockers") or []):
                if isinstance(b, dict) and b.get("id"):
                    real.add(b["id"])
        for b in (state.get("blockers") or []):
            if isinstance(b, dict) and b.get("id"):
                real.add(b["id"])
        if NEW not in real:
            print("❌ %s 在 STATE.yaml 里也不存在 ⇒ 拒绝写 (防再制造幻觉)" % NEW)
            return 1
        shutil.copy2(LOG, BAK)
        hit["source_blocker"] = NEW
        # ★yaml 往返自检
        a = yaml.safe_load(yaml.safe_dump(d, allow_unicode=True, sort_keys=False))
        b = yaml.safe_load(yaml.safe_dump(a, allow_unicode=True, sort_keys=False))
        if yaml.safe_dump(a, allow_unicode=True, sort_keys=False) != yaml.safe_dump(b, allow_unicode=True, sort_keys=False):
            print("❌ yaml 往返不一致 ⇒ 放弃写")
            return 1
        dump_atomic(d, LOG)
        print("✅ %s.source_blocker: %s → %s (★STATE.yaml 实测存在★ · 备份 %s)"
              % (TARGET, OLD, NEW, os.path.basename(BAK)))
        return 0


if __name__ == "__main__":
    sys.exit(main())
