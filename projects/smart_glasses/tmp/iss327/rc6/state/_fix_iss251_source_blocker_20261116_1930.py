#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_fix_iss251_source_blocker_20261116_1930.py —— ★★修 issue_check C5 的唯一违规: ISS-251 的 source_blocker 幻觉引用★★

★★为什么是这条 (★main 2026-11-16 19:3x 实跑 issue_check 抓到·rc=1·违规 1 条★)★★
  ★**ISS-251 的 `source_blocker` 写成了 `MECH-CALIBER`** —— ★**这不是台账里的 issue id, 也不是 STATE 的 blocker id**
  ⇒ ★**`issue_check` C5 判它「幻觉引用」= 真红 (不是假红)★**
  ⇒ ★**真因**: ★**开单时把【MECH 域的判据名】误填进了【上一条问题单的 id】这个字段** ★
  ⇒ ★**修在产生点 (台账字段本身)**, ★**不碰任何判据 / 不碰任何 agent 的分片 / 不碰 brief 正文** ★

★★改法 (★最小改动·只动 1 个字段 + 追加 1 句 note★)★★
  ★**`source_blocker`: `MECH-CALIBER` → `ISS-213`** ★
  ★**为什么是 ISS-213**: ★**本单三处老账的 need key 与来源 issue 的对应关系 (★本单 brief ①A/①B/①C 自己写明★)**:
      · 【A】充电耗散口径 ⇒ need `iss213_mech_mech_budget_charge_caliber_text` ⇒ ★**来源 ISS-213** ★
      · 【B】铝 k 201 保守侧 ⇒ need `iss218_mech_alu_k_201_vs_237` ⇒ 来源 ISS-218
      · 【C】检修口 15mm→60×30 ⇒ need `iss203_mech_service_port_doc_15mm_margin` ⇒ 来源 ISS-203
  ⇒ ★**字段只能填一个 ⇒ 填主源 ISS-213; 另两条 (ISS-218 / ISS-203) 一并写进 note ⇒ 一条不丢** ★
  ⇒ ★**副作用核查 (★main 实跑过★)**: ★**ISS-213 / ISS-218 / ISS-203 都不在 STATE.yaml 的 `domains.*.blockers` 里**
    ⇒ ★**C5 反向检查 (STATE 里每个 high/blocker 阻塞都必须有 issue 登记) 的口径一个数都不变** ★

★★落账纪律 (★项目既有范式★)**: flock + 锁内重读 + 只改 1 个字段 + 原子写 + yaml 往返自检 + 逐条 diff 实测
"""
import fcntl
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import yaml  # noqa: E402

LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
BAK = LOG + ".bak_20261116_1930_fix_iss251_sb"
IID = "ISS-251"
OLD_SB = "MECH-CALIBER"
NEW_SB = "ISS-213"

NOTE_ADD = (
    "\n★2026-11-16 19:3x (cron 775d9893 继续执行后继计划) ★**main 修本单 `source_blocker` 幻觉引用** "
    "(★`issue_check` C5 实跑 rc=1 · 违规 1 条★): ★**`MECH-CALIBER` → `ISS-213`** "
    "(★真因 = 开单时把【MECH 域判据名】误填进了【上一条问题单 id】字段★) ⇒ ★**本单三处老账的来源对应关系 "
    "(★brief ①A/①B/①C 已写明★)**: ★**【A】充电耗散口径 ⇒ need `iss213_mech_mech_budget_charge_caliber_text` ⇒ ISS-213** ★ · "
    "★**【B】铝 k 201 保守侧 ⇒ need `iss218_mech_alu_k_201_vs_237` ⇒ ISS-218** ★ · "
    "★**【C】检修口文档口径 ⇒ need `iss203_mech_service_port_doc_15mm_margin` ⇒ ISS-203** ★ "
    "⇒ ★**字段只容一个 ⇒ 填主源 ISS-213, 另两条写在本 note 里, 一条不丢** ★ "
    "⇒ ★**C5 反向检查 (STATE high/blocker 阻塞必须有 issue) 一个数都没变** (★三个 id 都不在 STATE blockers 里★) ★"
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

        target = None
        for it in items:
            if str(it.get("id")) == IID:
                target = it
                break
        if target is None:
            print("❌ %s 不在台账 ⇒ 放弃" % IID)
            return 1
        if target.get("source_blocker") != OLD_SB:
            print("ℹ️ %s 的 source_blocker 已是 %r (≠ %r) ⇒ 不动" % (IID, target.get("source_blocker"), OLD_SB))
            return 0

        shutil.copy2(LOG, BAK)
        target["source_blocker"] = NEW_SB
        note = target.get("note") or ""
        if "19:3x (cron 775d9893 继续执行后继计划) ★**main 修本单" not in note:
            target["note"] = note + NOTE_ADD

        a = yaml.safe_load(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, default_flow_style=False, width=width))
        b = yaml.safe_load(yaml.safe_dump(a, allow_unicode=True, sort_keys=False, default_flow_style=False, width=width))
        if yaml.safe_dump(a, allow_unicode=True, sort_keys=False, default_flow_style=False, width=width) != \
           yaml.safe_dump(b, allow_unicode=True, sort_keys=False, default_flow_style=False, width=width):
            print("❌ yaml 往返不一致 ⇒ 放弃写")
            return 1
        dump_atomic(doc, LOG, width)
        print("✅ 已原子写 issue_log.yaml: %s.source_blocker %s → %s (★备份 %s★)" % (IID, OLD_SB, NEW_SB, os.path.basename(BAK)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
