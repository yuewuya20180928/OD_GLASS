#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-199 落 fixed + 放行 hw-lead 名额 (2026-11-15 21:4x, 项目总工 main)

★★**为什么要有这次落盘 (★实测, 不是推测★)** ★★:
· `state/advance.py --json` 的 A 段 (internal) = **0 条** ⇒ 队列对三个总工全是空的
· ★**根因 = ISS-199 的【僵尸 fixing 标记】**(★同病第 14 次复发★):
  子会话 `agent:hw-lead:subagent:7fbe16e2` (sessionId `34e0e98b`) 2026-11-15 21:29:48 结束,
  status=**done** ⇒ ★**交卷已投递、文件已落盘** ⇒ 但 ★**brief 明写「不许碰 state/issue_log.yaml
  (改 issue 状态是 main 的活)」⇒ 子 agent 没落账 ⇒ status 停在 `fixing`** ★
· ⇒ ★**`advance.py` 的 in_flight 规则 (★"该 agent 正在干别的, 本轮跳过"★) ⇒ hw-lead 名额被永久占住
  ⇒ ★**hw-lead 唯一一条 open 的主线内部活 ISS-204 (`J_SOM_P2.pin7` pinmux 合法性) 本轮派不出去** ★
· ★**这是结构性病因, 不是偶发**: ★**brief 不许子 agent 改 issue_log ⇒ 每一单交卷后必然停在 `fixing`
  ⇒ 必须由 main 每次巡检时人工验+落账⇒ 忘了就停摆** ★

★★**三条交卷我逐份独立复核过 (★不采信自述, 只看盘上实物★)** ★★:
· ISS-199 ⇒ ★**真交卷** ★:
  ✅ 子会话 status=**done** (2026-11-15 21:29:48 结束, runtimeMs 576361)
  ✅ `HANDOFF/2026-11-15_hw-lead_ISS199_J_CHG_pinmap_第2口径收敛.md` mtime **2026-11-15 21:28** (18,236 B)
  ✅ `python3 HW/check_bq25896_pinout.py` **rc=0** (★检查项 ⑦ 实读 §5.2 表逐脚对拍网表, PASS=11 FAIL=0★)
  ✅ md5 三件一字未变: 网表 `c78f991283cc82d56c8e3dd31657c785` · 板 `611b869e13518c3c023fb178f91a0075`
     · `state/p10_rows.json` `c2dc73fe1e9fbd8edec68828dec81c36`
  ✅ 4 处逐处 spot check (main 自己读盘, 不看自述):
     `HW/CHARGE_BOARD_SPEC.md` §5.1 表 (第 3/4/5/8/9 行全部带「★已按网表真源订正 (ISS-199 · 2026-11-12)★」)
     · §5.1 第 400 行那条订正注记 (已重写, 逐脚列现行口径)
     · `HW/CHARGE_BOARD_SPEC.md` §7 P10 csv 镜像块第 567 行 (J_CHG pin10 → HINGE_RSV, 带订正注记)
     · `HW/J_CHG_SELECTION.md` 第 30 行 + 第 196 行 (pin7=NC / pin8=TS_BAT / pin9-10=HINGE_RSV)
     · `HW/POWER_SHUTDOWN_V3.md` 第 129 行 (TS 专用回流「已撤除」)
  ✅ `grep -n TS_RTN` 剩 6 处 ⇒ ★**逐行定性: 全部是【历史沿革】或【已订正注记】(第 400/424/426/441/567 行)
     或【§2.2 超地界只报不改 (第 144 行)】⇒ 【当前口径断言】0 处** ★
⇒ ★**处置 = 落 `fixed` (★不是 closed★ ⇒ 留给 QA/verify 环节) ⇒ 放出 hw-lead 名额** ★

★★**落账纪律 (与项目既有范式一致) (★照 `state/_apply_zombiefix_20261115.py` 的同一套★)** ★★:
① flock(state/.issue_log.lock) + 锁内重读
② ★**自证: yaml.safe_dump(整份 doc) 必须与原文件逐字节相同** (★实测本文件往返一致 = True★)
③ 原子写 (tmp → fsync → os.replace → fsync(dir))
④ ★**只改 ISS-199 一条** (status/fix_ref/note), 不动任何其它 issue

★**边界**: 不改 `PROJECT_TRACKER.md` §0 锁死表 · 不写任何子总工的分片 · 不发邮件 / 不联系供应商 /
不下采购单 · 板 / 网表 / 原理图 / BOM 一个字节不动 · ★**只落 issue 状态, 不改任何设计产物** ★
"""
from __future__ import annotations

import fcntl
import os
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")

IID = "ISS-199"
FIX_REF = "HANDOFF/2026-11-15_hw-lead_ISS199_J_CHG_pinmap_第2口径收敛.md"

NOTE = (
    "\n★**2026-11-15 21:4x 项目总工 (main) 落 `fixed` (★清第 14 次僵尸 fixing★)**:\n"
    "★**实测**: 子会话 `agent:hw-lead:subagent:7fbe16e2` (sessionId `34e0e98b`) 2026-11-15 21:29:48 结束, "
    "status=**done** ⇒ ★**交卷已投递、文件已落盘** ⇒ 但 ★**brief 明写「不许碰 state/issue_log.yaml "
    "(改 issue 状态是 main 的活)」⇒ 子 agent 没落账 ⇒ status 停在 `fixing`** ★\n"
    "★**⇒ 后果**: `advance.py` 的 in_flight 规则 ⇒ hw-lead 名额被永久占住 ⇒ A 段 (internal) 恒空 ⇒ "
    "★**hw-lead 唯一一条 open 的主线内部活 ISS-204 派不出去** ★\n"
    "★**main 独立复核 (★只看盘上实物, 不采信自述★)**:\n"
    "  ✅ `python3 HW/check_bq25896_pinout.py` **rc=0** (检查项 ⑦ 实读 §5.2 表逐脚对拍网表)\n"
    "  ✅ md5 三件一字未变: 网表 `c78f991283cc82d56c8e3dd31657c785` · 板 `611b869e13518c3c023fb178f91a0075` · "
    "`state/p10_rows.json` `c2dc73fe1e9fbd8edec68828dec81c36`\n"
    "  ✅ 4 处 spot check 全部带「★已按网表真源订正 (ISS-199 · 2026-11-12)★」注记 "
    "(§5.1 表 + §5.1 第 400 行注记 + §7 P10 csv 镜像块 + `J_CHG_SELECTION.md` ×2 + `POWER_SHUTDOWN_V3.md` ×1)\n"
    "  ✅ `grep -n TS_RTN` 剩 6 处 ⇒ 逐行定性全部是【历史沿革】/【已订正注记】/【§2.2 超地界只报不改】⇒ "
    "★**【当前口径断言】0 处** ★\n"
    "⇒ ★**处置 = 落 `fixed` (★不是 closed★) ⇒ 放出 hw-lead 名额 ⇒ 下一轮可派 ISS-204** ★\n"
    "★**★结构性病因 (★第 14 次复发, 根因不在子 agent★)**: ★**brief 不许子 agent 改 issue_log "
    "⇒ 每一单交卷后必然停在 `fixing` ⇒ 必须由 main 每次巡检时验+落账 ⇒ 忘了就停摆** ★\n"
)


def atomic_write(path: str, text: str) -> None:
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix=".iss199fixed.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
        dfd = os.open(os.path.dirname(path), os.O_RDONLY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def main() -> int:
    os.makedirs(os.path.dirname(LOCK), exist_ok=True)
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        raw = open(LOG, encoding="utf-8").read()
        doc = yaml.safe_load(raw)
        issues = doc["issues"]

        # ---- 自证: yaml 往返必须逐字节相同 (除本脚本要改的, 一个字节都不许动) ----
        rt = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=200)
        if rt != raw:
            print("★自证失败: yaml.safe_dump(整份 doc) 与原文件不一致 ⇒ 拒绝写 (防口径漂移)")
            print("   原文件 %d B / 往返 %d B" % (len(raw), len(rt)))
            return 2

        by_id = {i["id"]: i for i in issues}
        it = by_id.get(IID)
        if not it:
            print("★找不到 %s ⇒ 拒绝写" % IID)
            return 2
        if it.get("status") != "fixing":
            print("★%s 的 status 不是 fixing (是 %r) ⇒ 拒绝写" % (IID, it.get("status")))
            return 2
        if it.get("owner") != "hw-lead":
            print("★%s 的 owner 不是 hw-lead ⇒ 拒绝写" % IID)
            return 2

        it["status"] = "fixed"
        it["fix_ref"] = FIX_REF
        it["verify_by"] = "main"
        it["note"] = ((it.get("note") or "") + NOTE).lstrip("\n")

        out = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=200)
        atomic_write(LOG, out)
        print("★%s 已落 fixed (fix_ref=%s, verify_by=main)" % (IID, FIX_REF))
        print("★issue_log.yaml %d B → %d B (只改这 1 条的 status/fix_ref/verify_by/note)" % (len(raw), len(out)))
        return 0


if __name__ == "__main__":
    sys.exit(main())
