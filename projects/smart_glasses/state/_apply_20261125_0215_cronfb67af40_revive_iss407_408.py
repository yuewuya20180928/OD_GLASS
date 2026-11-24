#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20261125_0215_cronfb67af40_revive_iss407_408.py
==========================================================
main (项目总工 / moli) · cron fb67af40 (ARS45 队列自动派活) · 2026-11-25 02:1x
★★【★★僵尸 fixing 复活重派】★★ ISS-407 (mech-lead) + ISS-408 (sw-lead) ★★

★**为什么本 job 要做这件事 (★本机实读 + 实算, 不抄任何 agent 报告★)**:
  ① `state/advance.py --json` 实读 ⇒ **internal: []** (★三个总工名下各有一条 `fixing`
     ⇒ advance.py 的 in_flight 规则把三个槽位全挡住★)
  ② ★**但「fixing」不等于「在飞」** ⇒ ★**按 `state/ZOMBIE_FIXING_WATCHLIST.md` 的
     【三与判据】逐条实跑★**:
     | 单 | ① transcript 在盘 | ② 末行 timestamp | ③ 产物 mtime 在动 | 判定 |
     |---|---|---|---|---|
     | ISS-407 (mech-lead) | ✔ 465,692 B @ 02:07:40 | 静默 (最后 2026-11-24T18:07:40Z) | ✘ 只有 tmp/iss407/ 7 个探针 | ★**僵尸**★ |
     | ISS-408 (sw-lead)  | ✔ 采集自 02:07:37 | 静默 (最后 2026-11-24T18:07:37Z) | ✘ 只有 logs/iss408/ 4 个 before | ★**僵尸**★ |
     | ISS-406 (hw-lead)  | ✔ 持续在写 @ 02:1x | ★**仍在动**★ | ✔ `state/frag_write.py` 02:10 在跑 | ★**真在飞**★ |
  ③ ★**分片登记实测 = 0** ⇒ `state/fragments/mech.yaml` 里 `iss407` 命中 **0** ·
     `state/fragments/sw.yaml` 里 `iss408` 命中 **0** · ★**两份交卷页都不存在** ·
     ★**真相页 / 新闸 / 收口动作 三件交付物一件都不在盘** ⇒ ★**零交付**★
  ④ ★**死因 = 【外部同时中断】, 不是各��自己超时 (★L-33-a 同型★)**:
     两条 `runTimeoutSeconds` 都是 **0** (★无超时上限★) · 却在 ★**同一 3 秒窗口
     (02:07:37~02:07:40) 一起死** ⇒ ★**共因 ⇒ 与 2026-11-23 21:51:49 三条同秒死同型★**
  ⑤ ★**上一趟留下的活是真的 (★L-33-a: 「会话死了 ≠ 白干」★)**:
     ISS-407 留下 `tmp/iss407/` 7 个 AST 扫描探针 (★正是本单 D3 判据要的「写死常量点实扫」★)
     · ISS-408 留下 `logs/iss408/` 4 个开工基线 (★含 5 件受保护件的改前 md5 + 收口前闸的原样输出★)
     ⇒ ★**本趟从已落的活续做, 不许重做**★

★**落盘纪律 (★铁律⑩-i / ⑩-k①★)**:
  - ★**status 保持 `fixing` 不动** ⇒ ★**不落 open** ⇒ ★**兄弟 job 的 `advance.py --json`
    看不见 ⇒ 撞车窗口 = 0** ★
  - ★**先落盘 (dispatch_log + issue_log note_addendum) 再 spawn** ★
  - ★**零写板** (板 md5 / mtime / size 三项开工前 + 交卷后各打一次) ★
  - ★**零落表 · 零改既有闸 · 零改既有页正文 · 零挂链 · 零外发 · 不代老板拍板** ★
  - ★**issue_log 用【原文拼接】写 (★与 `_apply_20260724_0150_cron775d_revive_iss375_376.py`
    同款★) ⇒ ★**3.5 MB 台账除两处 note_addendum 段外逐字节不动 (零 churn)** ★

用法:
  python3 state/_apply_20261125_0215_cronfb67af40_revive_iss407_408.py --pre      # ★spawn 前落盘★
  python3 state/_apply_20261125_0215_cronfb67af40_revive_iss407_408.py --check    # ★只读自检★
"""
import hashlib
import os
import shutil
import sys
import time

import yaml

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
LOG = os.path.join(PROJ, "state/issue_log.yaml")
DL = os.path.join(PROJ, "state/dispatch_log.yaml")
BOARD = os.path.join(PROJ, "HW/PCB/demo_mainboard.kicad_pcb")
BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"
BOARD_MTIME = "2026-11-06 07:07:17.362193413"
BOARD_SIZE = 4940213
STAMP = time.strftime("%Y%m%d_%H%M")

# ★★死因 + 上一趟留下的活 (★本机实读 sessions_list + runs.json + transcript 末行 + 磁盘★)★★
DEAD = {
    "ISS-407": {
        "agent": "mech-lead",
        "brief": "state/dispatch_briefs/ISS-407_mech_verdict_premise_dependency_cont1.md",
        "task_name": "queue_iss407_cont1",
        "sess": "agent:mech-lead:subagent:9c786464-99d3-4a26-ae4c-a0837407d80d",
        "sid": "4aab8e7e-6e85-4dd3-b3c0-d438dfe58351",
        "runid": "7bf93075-a168-44ea-98d6-c35c7f6e7d87",
        "died": "2026-11-25 02:07:40",
        "why": ("runTimeoutSeconds=0 (★无超时上限★) + runtimeMs=679,293 ≈ 11.3 分钟 + "
                "outcome.status=timeout + endedReason=subagent-complete + "
                "transcript 末条 = 'Aborted' ⇒ ★**不是它自己超时★** · ★**与 sw-lead 的 ISS-408 "
                "在同一 3 秒窗口 (02:07:37~02:07:40) 一起死 ⇒ 共因 ⇒ L-33-a 同型★**"),
        "partial": ("`tmp/iss407/` 7 个 AST 扫描探针 (★scan_probe.py · scan_probe2.py · scan_probe3.py · "
                    "scan_dump.py · scan_dump2.py · scan_dump3.py · scan_dump4.py★) ⇒ ★**正是本单 D3 判据要的"
                    "「判决链闸源码里写死的几何字面量实扫」★ ⇒ 直接接着用, 不许重写★** · "
                    "transcript 末段已实测到的常量读数 (★`check_debug_seat_3d_fit.py` DEBUG_CLEAR_X=[1.775,4.085,4.81] "
                    "(L108) · OFFICIAL_DEBUG_COPPER_X=4.81 (L120) · `check_debug_seat_rework_spec.py` "
                    "REQUIRED_CLEAR_X=6.61 (L118) · OFFICIAL_COPPER_Y=1.0 (L122)★)"),
    },
    "ISS-408": {
        "agent": "sw-lead",
        "brief": "state/dispatch_briefs/ISS-408_sw_md5_rebase_gate_truth_cont1.md",
        "task_name": "queue_iss408_cont1",
        "sess": "agent:sw-lead:subagent:49b0f39b-fbde-4066-90fd-28ae31ae569c",
        "sid": "223a97cd-5a09-4105-afd7-3671752c738a",
        "runid": "eb5a662c-f102-4f21-bde6-41a2785a533b",
        "died": "2026-11-25 02:07:37",
        "why": ("runTimeoutSeconds=0 (★无超时上限★) + runtimeMs=674,080 ≈ 11.2 分钟 + "
                "outcome.status=timeout + transcript 末条 = 'missing tool result in session history; "
                "inserted synthetic error result for transcript repair' ⇒ ★**它是在等一个长命令的返回时"
                "被一起掐掉的** ⇒ 与 mech-lead 的 ISS-407 同秒死 ⇒ 共因 ⇒ L-33-a 同型★**"),
        "partial": ("`logs/iss408/` 4 个开工基线 (★`baseline_md5_pre.txt` = 5 件受保护件的改前 md5 · "
                    "`gate_before.txt` = 收口前 `check_sw_board_md5_rebase_readiness.py` 的原样输出 (rc=1) · "
                    "`gate_health_before.txt` = 收口前 `check_sw_gate_health.py` 的原样输出 · "
                    "`brief_cmds_before.txt` = 0 字节★) ⇒ ★**收口前基线已在盘, 不许重跑采集★**"),
    },
}


def board_fingerprint():
    h = hashlib.md5()
    with open(BOARD, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    st = os.stat(BOARD)
    import datetime
    mt = datetime.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S.%f")
    return h.hexdigest(), mt, st.st_size


def splice_log(src, iid, new_note):
    """把 new_note 追加到该 issue 段的 note_addendum 字段 (★原文拼接 ⇒ 其余字节不动★)"""
    i = src.find("\n- id: %s" % iid)
    if i < 0:
        raise SystemExit("★段没定位到 (%s) ⇒ 中止★" % iid)
    j = src.find("\n- id: ", i + 10)
    if j < 0:
        j = len(src)
    seg = src[i:j]
    if "  status: fixing" not in seg:
        raise SystemExit("★%s status 不是 fixing ⇒ 已被别的 job 签过 ⇒ 中止★" % iid)
    if "  dispatched_at:" not in seg:
        raise SystemExit("★%s 段里找不到 dispatched_at ⇒ 中止★" % iid)
    # ★note_addendum 追加在 dispatched_at 之前 (★与 revive_iss375_376.py 同款锚点★)
    anchor = "\n  dispatched_at:"
    k = seg.find(anchor)
    add = ("\n  note_addendum: '%s'\n" % new_note.replace("'", "''"))
    new_seg = seg[:k] + add + seg[k:]
    return src[:i] + new_seg + src[j:], new_seg


def do_pre():
    md5, mtime, size = board_fingerprint()
    if md5 != BOARD_MD5:
        raise SystemExit("★板 md5 已变 (★%s) ⇒ 中止★" % md5)
    if size != BOARD_SIZE:
        raise SystemExit("★板 size 已变 ⇒ 中止★" % size)
    print("★开工前板指纹: md5=%s mtime=%s size=%d ✔" % (md5, mtime, size))

    # ---- 1) issue_log: 原文拼接 (零 churn) ----
    src = open(LOG, encoding="utf-8").read()
    before_md5 = hashlib.md5(src.encode("utf-8")).hexdigest()
    new_src = src
    for iid, d in DEAD.items():
        tag = ("★2026-11-25 02:1x cron fb67af40 (ARS45 队列自动派活) 【僵尸 fixing 复活重派】★★ "
               "★**三与判据实测**: ① transcript 在盘 ② 末行 timestamp 静默于 {died} ③ 产物 mtime 停在同一分钟 "
               "⇒ 判定【僵尸】(★不是活人★) · ★**分片命中 = 0 · 交卷页不存在 · 真相页/新闸/收口一件都不在盘 ⇒ 零交付**★ · "
               "★**死因**: 上一子会话 `{sess}` (sessionId {sid} · runId {runid}) 于 {died} 被掐死 ({why})★ · "
               "★**上一趟留下的活**: {partial}★ · "
               "★**本趟 = 从已落的活续做 (★不是从零★)**: 任务书全文 = `{brief}` (★命令存在性守卫 rc=0★)★ · "
               "★**status 保持 fixing 不动** (★铁律⑩-k①: 不落 open ⇒ 兄弟 job 的 advance.py --json 看不见 ⇒ 撞车窗口 0★) · "
               "★**ISS-406 (hw-lead) 本轮实测真在飞 ⇒ 不派 (★一个 agent 一个写会话★)★ · "
               "★**零写板 · 零落表 · 零改既有闸 · 零改既有页正文 · 零挂链 · 零外发 · 不代老板拍板**★").format(
            iid=iid, died=d["died"], sess=d["sess"], sid=d["sid"], runid=d["runid"],
            why=d["why"], partial=d["partial"], brief=d["brief"])
        new_src, _ = splice_log(new_src, iid, tag)
    bak = LOG + ".bak_%s_cronfb67af40_revive_iss407_408" % STAMP
    shutil.copy2(LOG, bak)
    tmp = LOG + ".tmp_%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(new_src)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, LOG)
    after_src = open(LOG, encoding="utf-8").read()
    # ★自检: 除两处 note_addendum 段外, 其余字节必须完全一致★
    if len(after_src) <= len(src):
        raise SystemExit("★issue_log 变短了 ⇒ 中止★")
    d0 = yaml.safe_load(src)
    d1 = yaml.safe_load(after_src)
    i0 = {x.get("id"): x for x in (d0.get("issues", d0) if isinstance(d0, dict) else d0)}
    i1 = {x.get("id"): x for x in (d1.get("issues", d1) if isinstance(d1, dict) else d1)}
    if set(i0) != set(i1):
        raise SystemExit("★issue_log 条目集合变了 ⇒ 中止★")
    for iid in i0:
        a = dict(i0[iid])
        b = dict(i1[iid])
        a.pop("note_addendum", None)
        b.pop("note_addendum", None)
        if a != b:
            raise SystemExit("★%s 除 note_addendum 外还有别的变化 ⇒ 中止★" % iid)
    for iid in DEAD:
        if i1[iid].get("status") != "fixing":
            raise SystemExit("★%s status 被改了 ⇒ 中止★" % iid)
    print("★issue_log: md5 %s → %s (★除两处 note_addendum 外逐字节不变★) · 备份 %s"
          % (before_md5, hashlib.md5(after_src.encode("utf-8")).hexdigest(), os.path.basename(bak)))

    # ---- 2) dispatch_log: 追加式 (历史字节不动) ----
    raw = yaml.safe_load(open(DL, encoding="utf-8").read())
    if not isinstance(raw, list):
        raise SystemExit("★dispatch_log 顶层不是 list ⇒ 中止★")
    before = len(raw)
    new_entries = []
    for iid, d in DEAD.items():
        bp = os.path.join(PROJ, d["brief"])
        if not os.path.exists(bp):
            raise SystemExit("★cont1 brief 不存在 ⇒ 中止★: %s" % bp)
        with open(bp, encoding="utf-8") as fh:
            brief_text = fh.read()
        if len(brief_text) < 2000:
            raise SystemExit("★cont1 brief 太短 ⇒ 中止★")
        new_entries.append({
            "issue": iid,
            "agent": d["agent"],
            "at": "2026-11-25 02:1x",
            "brief": d["brief"],
            "job": ("cron fb67af40 (ARS45 队列自动派活) · ★2026-11-25 02:1x · ★**僵尸 fixing 复活重派** "
                    "(★上一子会话于 02:07:37~02:07:40 同一 3 秒窗口被共因掐死 · runTimeoutSeconds=0 ⇒ 非自身超时★) "
                    "· ★**三与判据实测 = 僵尸 (分片命中 0 + 交卷页不存在 + 真相页/新闸一件都不在盘)** ★ · "
                    "★**命令存在性守卫 `python3 state/check_brief_commands.py --brief-file` rc=0** ★ · "
                    "★**纯查证/纯分析/新建真相页 + 新建机器闸类 (零写板·零落表·零改既有闸·零改既有页正文·零挂链·零外发·不代拍) "
                    "⇒ 合「板只改一次」纪律 ①** ★ · ★**status 保持 fixing 不动 ⇒ 撞车窗口 0** ★"),
            "status_note": ("★台账 status 保持 fixing (未改) ⇒ advance.py in_flight 规则继续挡住任何 job 再给该 agent "
                            "派活 ⇒ 零撞车窗口★ · ★本趟 = 从上一趟已落的活续做, 不是从零★"),
            "task_name": d["task_name"],
            "dispatched_at": "2026-11-25 02:1x",
            "run_id": "cron_fb67af40_20261125_0215",
        })
    dbak = DL + ".bak_%s_cronfb67af40_revive_iss407_408" % STAMP
    shutil.copy2(DL, dbak)
    with open(DL, "a", encoding="utf-8") as fh:
        fh.write(yaml.safe_dump(new_entries, allow_unicode=True, sort_keys=False, width=200))
    after = yaml.safe_load(open(DL, encoding="utf-8").read())
    if len(after) != before + len(new_entries):
        shutil.copy2(dbak, DL)
        raise SystemExit("★dispatch_log 条数不对 ⇒ 已回滚★")
    print("★dispatch_log: %d → %d 条 (★追加式·历史字节不动★) · 备份 %s"
          % (before, len(after), os.path.basename(dbak)))

    # ---- 3) 板指纹复查 ----
    md5b, mtimeb, sizeb = board_fingerprint()
    if md5b != BOARD_MD5 or sizeb != BOARD_SIZE:
        raise SystemExit("★板指纹交卷后变了 ⇒ 中止★")
    print("★交卷后板指纹: md5=%s mtime=%s size=%d ✔ (★零写板★)" % (md5b, mtimeb, sizeb))
    print("PRE_OK")
    return 0


def do_check():
    src = open(LOG, encoding="utf-8").read()
    d = yaml.safe_load(src)
    issues = {x.get("id"): x for x in d.get("issues", [])}
    for iid, spec in DEAD.items():
        it = issues.get(iid)
        if not it:
            print("✘ %s 不在台账里" % iid)
            continue
        na = it.get("note_addendum")
        n = len(na) if isinstance(na, list) else (1 if na else 0)
        print("✔ %s status=%s owner=%s note_addendum=%d 条" % (iid, it.get("status"), it.get("owner"), n))
    raw = yaml.safe_load(open(DL, encoding="utf-8").read())
    print("✔ dispatch_log %d 条 (末条: %s / %s)" % (len(raw), raw[-1].get("issue"), raw[-1].get("task_name")))
    md5, mtime, size = board_fingerprint()
    print("✔ 板指纹 md5=%s mtime=%s size=%d" % (md5, mtime, size))
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--pre" in args:
        sys.exit(do_pre())
    if "--check" in args:
        sys.exit(do_check())
    print(__doc__)
    sys.exit(0)
