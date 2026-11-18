#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20261116_1945_zombie_continue_249_250_251.py —— ★★三条被 runTimeout 掐死的单: 记录事实 + 续做重派留痕★★

★★为什么做 (★main 2026-11-16 19:4x 实测★)★★
  ★**兄弟 job fb67af40 在 19:19 派出的 ISS-249 / ISS-250 / ISS-251 三条, 全部在 ~19:29 被 runTimeout 掐断** ★
  (★runtime 分别 617s / 608s / 596s · transcript 末条 = 「Now writing the landing ledger §17」/「gather the hard evidence」/「Aborted」★)
  ⇒ ★**盘上实况 (main 自己实跑, 不抄会话)**: ISS-249 = ★**F1 已落表 + 台账 §17 已写, 缺交卷单/分片/反向自证输出** ★ ·
    ISS-250 = ★**零产出** ★ · ISS-251 = ★**改了 2 处半文档 (A/C 已落, B 早于 ISS-219 已落), 缺新门禁/交卷单/分片** ★
  ⇒ ★**本 job 19:4x 续做重派 (runTimeout 5400s) ⇒ 每个 agent 1 个写会话, 三个 agent 各 1 个, 无重复** ★
  ⇒ ★**status 保持 `fixing`** (★⇒ 下一轮 cron 的 in_flight 规则会跳过这 3 个 agent ⇒ 不撞车★)

★★本脚本只做两件事 (★台账与派活日志是 main 的地界★)** ★★
  ① `state/issue_log.yaml`: 三条的 `note` 追加事实段 + `dispatched_at` 更新成【本轮续做的确切时刻】(★status 一个都不改★)
  ② `state/dispatch_log.yaml`: 追加 3 条续做派活记录 (含真 session_key / run_id / task_name)

★★落账纪律 (★项目既有范式★)**: flock + 锁内重读 + 原子写 + yaml 往返自检 + 逐条 diff 实测
"""
import fcntl
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import yaml  # noqa: E402

LOG = os.path.join(HERE, "issue_log.yaml")
DLOG = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
DLOG_LOCK = os.path.join(HERE, ".dispatch_log.lock")
BAK = LOG + ".bak_20261116_1945_zombie_continue"
DBAK = DLOG + ".bak_20261116_1945_zombie_continue"

AT = "2026-11-16 19:45"

# ★**每条 = (id, owner, 上一轮会话, 死法, 盘上实况, 缺口, 新 session_key, run_id, task_name)★**
CONT = {
    "ISS-249": {
        "owner": "hw-lead",
        "prev": "agent:hw-lead:subagent:8f4758a2-03c2-42ce-9802-761005f0ca84",
        "death": "19:19:21 起 · 19:29:40 被 runTimeout 掐断 (runtime 617s) · 末条 transcript = 「Now writing the landing ledger §17:」",
        "disk": ("★**核心落表已完成**: `state/gen_netlist.py` L381/L391 两行 node2 已落 (grep 实读) · "
                 "`HW/check_iss247_f1_landed.py` rc=0 「✅ F1 已落表」 · 网表 md5 `16ac89f7…` (已变 = F1 已落) · "
                 "板 `611b869e…` / `.kicad_pro` `3e504d2b…` 逐字节未变 · `HW/SCHEMATIC_LANDING_V1_LANDED.md` §17 已写 (L704 起) ★"),
        "gap": ("★**交卷单缺** (`HANDOFF/2026-11-16_hw-lead_ISS249_*.md` 不存在) · "
                "★**分片缺** (`state/fragments/hw.yaml` mtime 18:46 = 开单前) · "
                "★**反向自证只有配方没有已跑输出** (§17 里写了配方, 但没有执行结果) ★"),
        "session_key": "agent:hw-lead:subagent:638b25cd-da78-4388-8959-3aa3e14a511f",
        "run_id": "12dfa19f-81da-494f-852e-673965a93198",
        "task_name": "advance_iss249_continue",
    },
    "ISS-250": {
        "owner": "sw-lead",
        "prev": "agent:sw-lead:subagent:83050de2-1b37-4abd-93a6-a102cfbab1cf",
        "death": "19:19:31 起 · 19:29:41 被 runTimeout 掐断 (runtime 608s · abortedLastRun=true) · 末条 = 「Toolchain confirmed present locally (2.3.2). Now let me gather the hard evidence in parallel.」",
        "disk": "★**零产出** (`HANDOFF/` 无 ISS250 交卷单 · `SW/` 无新文件 · `state/fragments/sw.yaml` mtime 18:38 = 开单前) ★",
        "gap": ("★**查证表缺** · ★**降级方案缺** · ★**板可达时的执行清单缺** · ★**交卷单缺** · ★**分片缺** ★ ⇒ "
                "★**根因 = 上一轮 10 分钟全花在内存里, 一次 timeout 全丢** ★"),
        "session_key": "agent:sw-lead:subagent:0f477d0f-f3f9-4fff-adf1-dfd080d3b2c3",
        "run_id": "186f3879-d229-4aea-9408-ed4f36c3e6d5",
        "task_name": "advance_iss250_continue",
    },
    "ISS-251": {
        "owner": "mech-lead",
        "prev": "agent:mech-lead:subagent:6348eece-d633-4f6b-ac60-8d88a2d18591",
        "death": "19:19:42 起 · 19:29:40 被 runTimeout 掐断 (runtime 596s · abortedLastRun=true) · transcript 末条 = exec 返回 「Aborted」",
        "disk": ("★**三处老账已落 2 处半**: 【A】充电耗散口径 = `MECH/verify_budget.py` 已是 buck 口径 (`P_CHARGE=0.50` · 区间 0.45-0.57) 且实跑 rc=0「✅ 门禁绿」· "
                 "`MECH/MECH_BUDGET.md` L604-605 已把旧 0.8 W 线性口径标为判死 · 【B】铝 k 201 = ★**早已落 (ISS-219 落的, 不是本单)**: `MECH_BUDGET.md` L519 + `verify_budget.py` L111 `K_AL_6063_T6=201.0` · "
                 "【C】检修口文档 = `MECH/SERVICE_PORT_ISS092.md` 已改 (mtime 19:25:58 · L5 范围声明 + L19/L200/L201 需求 36.00/余 +2.00 + L22/L281/L322 换 30mm 板套 A 基准) ★"),
        "gap": ("★**新门禁 `MECH/check_budget_caliber.py` 缺** (不存在) · ★**三处逐条订正表缺** · "
                "★**交卷单缺** (`HANDOFF/2026-11-16_mech-lead_ISS251_*.md` 不存在) · ★**分片缺** (`mech.yaml` mtime 18:47 = 开单前) ★"),
        "session_key": "agent:mech-lead:subagent:29892e26-9b8e-4056-bbe0-732da6a9c9de",
        "run_id": "86c1c4dc-9166-45a2-8ae0-43c8c4eb2f4b",
        "task_name": "advance_iss251_continue",
    },
}


def note_add(iid, c):
    return (
        "\n★2026-11-16 19:4x (cron 775d9893 继续执行后继计划) ★**续做重派** (★上一轮会话被 runTimeout 掐死★)\n"
        "· ★**上一轮怎么死的**: %s\n"
        "· ★**盘上实况 (main 自己实跑, 不抄会话)**: %s\n"
        "· ★**缺口**: %s\n"
        "· ★**本轮动作**: ★**续做重派** (taskName=`%s` · session `%s` · runTimeout **5400s (90 分钟)** ⇒ ★**别再攒在内存里★) ★\n"
        "· ★**status 保持 `fixing`** (★⇒ 下一轮 cron 的 in_flight 规则会跳过这个 agent ⇒ 不撞车★) ★\n"
        "· ★**brief 全文**: `state/dispatch_briefs/%s_continue.md` ★\n"
        % (c["death"], c["disk"], c["gap"], c["task_name"], c["session_key"], iid)
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


def probe_width(doc, raw):
    for w in (60, 80, 100, 120, 200):
        if yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, default_flow_style=False, width=w) == raw:
            return w
    return 200


def roundtrip_ok(doc, width):
    a = yaml.safe_load(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, default_flow_style=False, width=width))
    b = yaml.safe_load(yaml.safe_dump(a, allow_unicode=True, sort_keys=False, default_flow_style=False, width=width))
    return yaml.safe_dump(a, allow_unicode=True, sort_keys=False, default_flow_style=False, width=width) == \
           yaml.safe_dump(b, allow_unicode=True, sort_keys=False, default_flow_style=False, width=width)


def main():
    # ---------- ① issue_log ----------
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        raw = open(LOG, encoding="utf-8").read()
        doc = yaml.safe_load(raw)
        items = doc if isinstance(doc, list) else doc.get("issues")
        width = probe_width(doc, raw)
        shutil.copy2(LOG, BAK)
        for it in items:
            iid = str(it.get("id"))
            if iid not in CONT:
                continue
            c = CONT[iid]
            it["dispatched_at"] = AT
            note = it.get("note") or ""
            if "19:4x (cron 775d9893 继续执行后继计划) ★**续做重派**" not in note:
                it["note"] = note + note_add(iid, c)
            print("✅ %s note 已追加 + dispatched_at → %s (status 保持 %s)" % (iid, AT, it.get("status")))
        if not roundtrip_ok(doc, width):
            print("❌ yaml 往返不一致 ⇒ 放弃写 issue_log")
            return 1
        dump_atomic(doc, LOG, width)
        print("★备份 %s" % os.path.basename(BAK))

    # ---------- ② dispatch_log ----------
    with open(DLOG_LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        raw2 = open(DLOG, encoding="utf-8").read()
        doc2 = yaml.safe_load(raw2)
        width2 = probe_width(doc2, raw2)
        shutil.copy2(DLOG, DBAK)
        for iid, c in CONT.items():
            doc2.setdefault("dispatches", []).append({
                "issue": iid,
                "agent": c["owner"],
                "at": "2026-11-16",
                "brief": "★**续做重派** (★上一轮会话 %s 被 runTimeout 掐死·盘上实况见台账 note★) ⇒ ★**只补缺口, 不许重做已落的部分** ⇒ 缺口: %s ⇒ brief 全文 `state/dispatch_briefs/%s_continue.md`"
                         % (c["prev"], c["gap"], iid),
                "reason": "★main 19:4x 实测: 上一轮会话 runtime ~600s 被 runTimeout 掐死 ⇒ ★**盘上零产出/半落地** ⇒ 本 job 续做重派 (runTimeout 5400s ⇒ 90 分钟, 别再攒在内存里) · ★**status 保持 fixing ⇒ 下一轮 cron 的 in_flight 规则不撞车** · ★**零外发 · 不替老板拍板** ★",
                "session_key": c["session_key"],
                "run_id": c["run_id"],
                "task_name": c["task_name"],
                "run_timeout_s": 5400,
                "spawned_by": "775d9893(本 job)",
                "status_at_spawn": "fixing (先落 fixing 再 spawn ⇒ 不撞车)",
                "prev_session": c["prev"],
            })
            print("✅ dispatch_log 追加 %s → %s" % (iid, c["owner"]))
        if not roundtrip_ok(doc2, width2):
            print("❌ yaml 往返不一致 ⇒ 放弃写 dispatch_log")
            return 1
        dump_atomic(doc2, DLOG, width2)
        print("★备份 %s" % os.path.basename(DBAK))
    return 0


if __name__ == "__main__":
    sys.exit(main())
