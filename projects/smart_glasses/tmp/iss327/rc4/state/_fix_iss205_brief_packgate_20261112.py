#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_fix_iss205_brief_packgate_20261112.py —— ★★给 ISS-205 的 brief 补两条 (★改派后必须补的两处★)★★

★★为什么要补 (★main 2026-11-12 03:3x 独立复核改派后实测到的★)★★:
  ★**① 漏了【投产包会立刻变旧 ⇒ chain_gate 会红】这条** ★★
    ⇒ `state/chain_gate.py` 的 `check_sch_src_pack()` 校【投产包 doc/sch_src/ 里每个文件的 md5 == 源文件 md5】
    ⇒ ★**ISS-205 一改原理图 ⇒ 源变新 · 投产包还是旧 ⇒ chain_gate rc=1** ★★
    ⇒ ★**★这正是 MEMORY 里那条铁律「子 agent 在飞时改了原理图 ⇒ 投产包立刻变旧」的第三次撞上★**
    ⇒ ⇒ ★**必须在 brief 里写清: 要么本单一并重出投产包, 要么明确写"这是预期中间态·main 来重出" ⇒ 不许 sw-lead 以为是自己没做完★★**

  ★**② 漏了【sw-lead 是软件总工, 但 `gen_kicad_sch.py` 是硬件生成器】这个地界提醒** ★★
    ⇒ ★**该文件历史上一直是 hw-lead 在改 (★hw.yaml 里 440 行提到它★)**
    ⇒ ⇒ ★**改派本身是对的 (★hw-lead 名额被 ISS-195 占着 + 文件交集实测=0 + sw-lead 空闲★) ⇒ 但必须补一句地界提醒:
      ★★sw-lead 只许按 brief 的字面指令改 (★答案我已算好全塞在 brief 里了★), 不许自己重新设计位号规则 / 不许顺手改别的生成器逻辑★★**

★纪律: ★只改 ISS-205 一条的 `task_brief` 字段 ★ · flock + 锁内重读 + 原子写 + yaml 往返自检 + 逐条 diff 实测
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
BAK = LOG + ".bak_iss205_brief_20261112"
IID = "ISS-205"

ADD_1 = (
    "\n\n★**★★⑦ ★★本单交卷时【投产包一定会变旧】⇒ 这是【预期中间态】, 不是你没做完★★** ★★\n"
    "★**实测依据**: `state/chain_gate.py` 的 `check_sch_src_pack()` 校【投产包 `doc/sch_src/` 里每个文件的 md5 "
    "== 源文件 md5】⇒ ★**你一改原理图 ⇒ 源变新 · 投产包还是旧 ⇒ `chain_gate.py` rc=1** ★★\n"
    "★**★所以交卷时照下面二选一 (★别自己去纠结 rc★)** ★★:\n"
    "  ★**(A)【推荐】本单一并重出投产包**: 跑 `bash state/gen_production_pack.sh` ⇒ ★**然后 `chain_gate.py` 必须 rc=0** "
    "(★**注意**: 这个脚本会 `rm -rf` 整个 `HW/PCB/production/` ⇒ ★**跑之前确认没人在飞别的单碰投产包★)**\n"
    "  ★**(B) 或者: 不跑, 但在交卷报告里明写【投产包已变旧, 待 main 重出】** ⇒ ★**main 验收时会替你重出** ★★\n"
    "★**★★无论 (A) 还是 (B), 交卷报告都必须写一句: 「投产包 sch_src 与新原理图的 md5 是否已同步」★★**"
)

ADD_2 = (
    "\n\n★**★★⑧ ★★地界提醒 (★你是软件总工, 但这单改的是硬件生成器★)★★** ★★\n"
    "★**`state/gen_kicad_sch.py` 历史上一直是 hw-lead 在改 (★`state/fragments/hw.yaml` 里 440 行提到它★)** ⇒ "
    "★**本单改派给你是因为【hw-lead 名额被 ISS-195 占着 + 文件交集实测 = 0 + 你空闲】⇒ 改派是对的** ★★\n"
    "★**★但你只许【按本 brief 的字面指令改】**: ★**答案(main 03:0x 实测)已经全算好塞在上面的判据里了** ⇒ "
    "★**不许自己重新设计位号规则** (★别去改 `RAIL_*`/`NET_*` 的保留口径★) · ★**不许顺手改别的生成器逻辑** "
    "(★`gen_bom.py` / `gen_netlist.py` / `gen_pcb_netlist_board.py` 一律不许碰★) · "
    "★**不许把\"顺手改一下\"当改进** (★本单只求【问号清零 + 三条闸绿 + md5 不变】三个判据, 别的都不许动★) ★★"
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
        width = width or 200
        print("★当前排版 width = %d" % width)
        hit = None
        for it in items:
            if str(it.get("id")) == IID:
                hit = it
                break
        if hit is None:
            print("❌ %s 不在 issue_log.yaml 里" % IID)
            return 1
        brief = str(hit.get("task_brief") or "")
        if "⑦ ★★本单交卷时【投产包一定会变旧】" in brief:
            print("ℹ️ brief 已含 ⑦⑧ ⇒ 不动")
            return 0
        shutil.copy2(LOG, BAK)
        hit["task_brief"] = brief + ADD_1 + ADD_2
        a = yaml.safe_load(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, default_flow_style=False, width=width))
        b = yaml.safe_load(yaml.safe_dump(a, allow_unicode=True, sort_keys=False, default_flow_style=False, width=width))
        if yaml.safe_dump(a, allow_unicode=True, sort_keys=False, default_flow_style=False, width=width) != \
           yaml.safe_dump(b, allow_unicode=True, sort_keys=False, default_flow_style=False, width=width):
            print("❌ yaml 往返不一致 ⇒ 放弃写")
            return 1
        dump_atomic(doc, LOG, width)
        print("✅ ISS-205.task_brief 已补 ⑦ (投产包会变旧·预期中间态) + ⑧ (地界提醒) (★备份 %s★)" % os.path.basename(BAK))
    return 0


if __name__ == "__main__":
    sys.exit(main())
