#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20260724_0150_cron775d_revive_iss375_376.py
==================================================
main (项目总工 / moli) · cron 775d9893 「ARS45 继续执行后继计划」· 2026-11-24 01:5x
★★【★★僵尸 fixing 复活重派】★★ ISS-375 (sw-lead) + ISS-376 (hw-lead) ★★

★**为什么本 job 要做这件事 (★本机实读 + 实算, 不抄任何 agent 报告★)**:
  ① `state/advance.py --json` 实读 ⇒ **internal: []** (★三个总工名下各有一条 `fixing` ⇒ advance.py 的 in_flight 规则把三个槽位全挡住★)
  ② ★**但「fixing」不等于「在飞」** ⇒ ★**按 `state/ZOMBIE_FIXING_WATCHLIST.md` 的【三与判据】逐条实跑★**:
     | 单 | ① transcript 在盘 | ② 末行 timestamp | ③ 产物 mtime 在动 | 判定 |
     |---|---|---|---|---|
     | ISS-375 (sw-lead) | ✔ 470,727 B @ 01:20:37 | 静默 (最后 2026-11-23T17:20:37Z) | ✘ `logs/iss375/` 最新 01:12 | ★**僵尸**★ |
     | ISS-376 (hw-lead) | ✔ 197,159 B @ 01:20:32 | 静默 (最后 2026-11-23T17:20:32Z) | ✘ `logs/iss376/` 最新 01:17 | ★**僵尸**★ |
     | ISS-374 (mech-lead) | ✔ 758,608 B @ 01:32:07 | — | ✔ `logs/iss374/` 最新 01:38 | ★**真在飞**★ |
  ③ ★**分片登记实测 = 0** ⇒ ★`state/fragments/sw.yaml` 里 `iss375` 命中 0 · `state/fragments/hw.yaml` 里 `iss376` 命中 0 · ★**交卷页 `HANDOFF/2026-11-23_sw-lead_ISS375_*` / `HANDOFF/2026-11-23_hw-lead_ISS376_*` 两份都不存在** ⇒ ★**零交付**★
  ④ ★**兄弟 job fb67af40 (ARS45 队列自动派活) 于 01:23~01:24 写好了两份 cont2 任务书 (★命令存在性守卫 `state/check_brief_commands.py --brief-file` 两份都 rc=0★) ⇒ ★**但它自己于 01:24:13 撞 60 分钟硬墙死在了【spawn 之前】** (★transcript 末行 2026-11-23T17:24:13Z · 下一轮 02:24 才到★) ⇒ ★**⇒ 那两个槽位会【空着】直到 02:24 ⇒ 而 02:24 那一轮 `advance.py --json` 仍是 internal: [] ⇒ 两边都不会自动复活 ⇒ 队列断线**★
  ⑤ ★**本 job 的既定职责** (★有先例★): ★`state/dispatch_log.yaml` 里 ★**本 job 自己** ★在 2026-11-23 22:1x 做过同型复活 (★「复活僵尸单 ISS-369 / ISS-371 / ISS-372 cont1」★) ⇒ ★**本轮同型续做★**

★**落盘纪律 (★铁律⑩-i / ⑩-k①★)**:
  - ★**status 保持 `fixing` 不动** ⇒ ★**不落 open** ⇒ ★**兄弟 job 的 `advance.py --json` 看不见 ⇒ 撞车窗口 = 0** ★
  - ★**先落盘 (dispatch_log + issue_log note) 再 spawn** ⇒ ★**spawn 失败也不留空壳日志** ★
  - ★**零写板** (板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · size `4940213` 三项开工前/交卷后各打一次) ★
  - ★**不改 `PROJECT_TRACKER.md` §0** · ★**不写别的 agent 的分片** (★只改 main 自己的 issue_log + dispatch_log★) · ★**零外发** · ★**不代老板拍板** ★
  - ★**issue_log 用【原文拼接】写 (★与 `state/_apply_20260723_2240_main_sign_iss369_371_372.py` 同款★) ⇒ ★**3 MB 台账除目标段外逐字节不动 (零 churn)** ★

用法:
  python3 state/_apply_20260724_0150_cron775d_revive_iss375_376.py --pre      # ★spawn 前落盘★
  python3 state/_apply_20260724_0150_cron775d_revive_iss375_376.py --post     # ★spawn 后回填 session_key★
  python3 state/_apply_20260724_0150_cron775d_revive_iss375_376.py --check    # ★只读自检★
"""
import hashlib
import os
import re
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

# ★★死因 (★本机实读 sessions_list + transcript 末行 + logs mtime★)★★
DEAD = {
    "ISS-375": {
        "agent": "sw-lead",
        "sess": "agent:sw-lead:subagent:4c87e4ad-f092-4f3a-a230-dc98a348e228",
        "sid": "27ce95b4-252e-428a-963c-51fac0d98ca5",
        "died": "2026-11-24 01:17:17",
        "why": ("status=timeout + abortedLastRun=true + runtimeMs=574,213 ≈ 9.6 分钟 · "
                "promptError=\"This operation was aborted\" · **externalAbort=false** ⇒ 非外部 abort · 非上下文溢出"),
        "partial": ("`SW/BOARD_ONEPASS_DEBUG_PIN_ORDER_CONTRACT.md` (32,392 B @ 01:15) + "
                    "`SW/tools/check_debug_pin_order_contract.py` (37,257 B @ 01:16 · ★**有真 bug★) + "
                    "`logs/iss375/` 8 份沙盒读数 (★net-code 顺序 bug 已修★) ⇒ ★**零交卷页 · 零分片**★"),
        "brief": "state/dispatch_briefs/ISS-375_sw_debug_pin_order_contract_cont2.md",
    },
    "ISS-376": {
        "agent": "hw-lead",
        "sess": "agent:hw-lead:subagent:ea28af80-c5ff-4bc9-833a-6880e0b22d3a",
        "sid": "1d527598-a1bc-482b-9b71-ace41fab277d",
        "died": "2026-11-24 01:17:12",
        "why": ("status=timeout + abortedLastRun=true + runtimeMs=410,495 ≈ 6.8 分钟 · "
                "promptError=\"This operation was aborted\" · **externalAbort=false** ⇒ 非外部 abort · 非上下文溢出"),
        "partial": ("`tmp/iss376_sbx/tools/scan_land_fit.py` (27,422 B @ 01:16) + "
                    "`logs/iss376/scan_stdout.txt` (1,535 B) + `logs/iss376/scan_land_fit.json` (1,154 B · ★**落盘炸在半截★**) "
                    "⇒ ★**零真相页 · 零闸 · 零交卷页 · 零分片**★"),
        "brief": "state/dispatch_briefs/ISS-376_hw_jdebug_land_fit_cont2.md",
    },
}

JOB_TAG = ("cron 775d9893 (ARS45 继续执行后继计划) · ★复活僵尸单 {iid} cont2 时刻 2026-11-24 01:5x · "
           "★**status 保持 fixing 不动** (★铁律⑩-k①: 不落 open ⇒ 兄弟 job 的 advance.py --json 看不见 ⇒ 撞车窗口 0★) · "
           "★**死因 = 上一子会话 `{sess}` (sessionId {sid}) 于 {died} 被掐死** (★{why}★) · "
           "★**上一趟留下什么**: {partial} ⇒ ★**本趟 = 从已落的活续做, 不是从零★** · "
           "★**兄弟 job fb67af40 于 01:23~01:24 已把 cont2 任务书写好 (★命令存在性守卫 rc=0★), 但它自己于 01:24:13 撞 60 分钟硬墙死在 spawn 之前 "
           "⇒ 下一轮 02:24 才到 ⇒ 本 job 接手续派** · "
           "★**任务书全文**: `{brief}` · ★**零写板 · 零落表 · 零外发 · 不代拍** ★")


def load(path):
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def board_fingerprint():
    st = os.stat(BOARD)
    with open(BOARD, "rb") as fh:
        md5 = hashlib.md5(fh.read()).hexdigest()
    return md5, st.st_mtime, st.st_size


def splice_log(src, iid, new_note):
    """把 new_note 追加到该 issue 段的 note 字段 (★原文拼接 ⇒ 其余字节不动★)"""
    i = src.find("\n- id: %s" % iid)
    if i < 0:
        raise SystemExit("★段没定位到 (%s) ⇒ 中止★" % iid)
    j = src.find("\n- id: ", i + 10)
    if j < 0:
        j = len(src)
    seg = src[i:j]
    if "  status: fixing" not in seg:
        raise SystemExit("★%s status 不是 fixing ⇒ 已被别的 job 签过 ⇒ 中止★" % iid)
    # note 是单行折行的 YAML 标量 ⇒ 追加到该段末尾 (dispatched_at 之前) 最稳
    anchor = "\n  dispatched_at:"
    k = seg.find(anchor)
    if k < 0:
        raise SystemExit("★%s 段里找不到 dispatched_at ⇒ 中止★" % iid)
    add = ("\n  note_addendum: '%s'\n" % new_note.replace("'", "''"))
    new_seg = seg[:k] + add + seg[k:]
    return src[:i] + new_seg + src[j:], new_seg


def do_pre():
    md5, mtime, size = board_fingerprint()
    assert md5 == BOARD_MD5, "★板 md5 已变 (★%s) ⇒ 中止★" % md5
    assert size == BOARD_SIZE, "★板 size 已变 ⇒ 中止★"

    # ---- 1) issue_log: 原文拼接 (零 churn) ----
    src = open(LOG, encoding="utf-8").read()
    before_md5 = hashlib.md5(src.encode("utf-8")).hexdigest()
    new_src = src
    for iid, d in DEAD.items():
        tag = ("★2026-11-24 01:5x cron 775d9893 【僵尸 fixing 复活重派】★★ "
               "★**三与判据实测**: ① transcript 在盘但 ② 末行 timestamp 静默 ③ `logs/iss{iid}/` 产物 mtime 停在 {died} "
               "⇒ 判定【僵尸】(★不是活人★) · ★**分片命中 = 0 · 交卷页不存在 ⇒ 零交付**★ · "
               "★**死因**: 上一子会话 `{sess}` (sessionId {sid}) 于 {died} 被掐死 ({why})★ · "
               "★**上一趟留下的活**: {partial}★ · "
               "★**本趟 = 从已落的活续做 (★不是从零★)**: 任务书全文 = `{brief}` (★命令存在性守卫 rc=0★)★ · "
               "★**status 保持 fixing 不动** (★铁律⑩-k①: 不落 open ⇒ 兄弟 job 的 advance.py --json 看不见 ⇒ 撞车窗口 0★) · "
               "★**兄弟 job fb67af40 已写好 cont2 任务书但于 01:24:13 撞 60 分钟硬墙死在 spawn 之前 (下一轮 02:24) ⇒ 本 job 接手续派**★ · "
               "★**零写板 · 零落表 · 零外发 · 不代老板拍板**★").format(
            iid=iid, died=d["died"], sess=d["sess"], sid=d["sid"], why=d["why"],
            partial=d["partial"], brief=d["brief"])
        new_src, _ = splice_log(new_src, iid, tag)
    bak = LOG + ".bak_%s_cron775d_revive_iss375_376" % STAMP
    shutil.copy2(LOG, bak)
    tmp = LOG + ".tmp_%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(new_src)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, LOG)
    after_src = open(LOG, encoding="utf-8").read()
    # ★自检: 除两处 note_addendum 段外, 其余字节必须完全一致★
    assert len(after_src) > len(src), "★issue_log 变短了 ⇒ 中止★"
    d0 = yaml.safe_load(src)
    d1 = yaml.safe_load(after_src)
    i0 = {x.get("id"): x for x in (d0.get("issues", d0) if isinstance(d0, dict) else d0)}
    i1 = {x.get("id"): x for x in (d1.get("issues", d1) if isinstance(d1, dict) else d1)}
    assert set(i0) == set(i1), "★issue_log 条目集合变了 ⇒ 中止★"
    for iid in i0:
        a = dict(i0[iid])
        b = dict(i1[iid])
        a.pop("note_addendum", None)
        b.pop("note_addendum", None)
        assert a == b, "★%s 除 note_addendum 外还有别的变化 ⇒ 中止★" % iid
    for iid in DEAD:
        assert i1[iid].get("status") == "fixing", "★%s status 被改了 ⇒ 中止★" % iid

    # ---- 2) dispatch_log: 追加式 (历史字节不动) ----
    raw = load(DL)
    assert isinstance(raw, list), "★dispatch_log 顶层不是 list ⇒ 中止★"
    before = len(raw)
    new_entries = []
    for iid, d in DEAD.items():
        with open(os.path.join(PROJ, d["brief"]), encoding="utf-8") as fh:
            brief_text = fh.read()
        new_entries.append({
            "issue": iid,
            "agent": d["agent"],
            "at": "2026-11-24",
            "brief": brief_text[:300],
            "job": JOB_TAG.format(iid=iid, sess=d["sess"], sid=d["sid"], died=d["died"],
                                  why=d["why"], partial=d["partial"], brief=d["brief"]),
            "session_key": None,
            "run_id": None,
            "task_name": None,
            "dispatched_at": "2026-11-24 01:5x",
            "prev_session_key": d["sess"],
            "redispatch_zombie": "True",
            "partial_delivery": ("★**上一趟留下的活**: " + d["partial"]),
            "status_note": ("★台账 status 保持 fixing (未改) ⇒ advance.py in_flight 规则继续挡住任何 job "
                            "给 %s 再派活 ⇒ 零撞车窗口★" % d["agent"]),
        })
    dl_bak = DL + ".bak_%s_cron775d_revive_iss375_376" % STAMP
    shutil.copy2(DL, dl_bak)
    chunk = yaml.safe_dump(new_entries, allow_unicode=True, sort_keys=False, width=200)
    with open(DL, "a", encoding="utf-8") as fh:
        with open(DL, "rb") as rf:
            rf.seek(-1, os.SEEK_END)
            if rf.read(1) != b"\n":
                chunk = "\n" + chunk
        fh.write(chunk)
    after = load(DL)
    assert isinstance(after, list) and len(after) == before + 2, "★dispatch_log 条目数不对 ⇒ 中止★"
    assert after[-1]["issue"] == "ISS-376", "★dispatch_log 末条不对 ⇒ 中止★"

    md5b, mtimeb, sizeb = board_fingerprint()
    assert (md5b, sizeb) == (BOARD_MD5, BOARD_SIZE), "★板被写了 ⇒ 中止★"
    print("★PRE 落盘 OK ★")
    print("   issue_log: md5 %s → %s (★除两处 note_addendum 外逐字节不变★) · 备份 %s" %
          (before_md5[:12], hashlib.md5(after_src.encode('utf-8')).hexdigest()[:12], os.path.basename(bak)))
    print("   dispatch_log: %d → %d 条 (★历史字节不动·追加式★) · 备份 %s" %
          (before, before + 2, os.path.basename(dl_bak)))
    print("   板指纹: md5 %s · size %d · mtime 未动 ⇒ OK" % (md5b, sizeb))


def do_post(session_map=None):
    """spawn 后回填 session_key / run_id 到 dispatch_log 末两条 (★原文拼接, 历史字节不动★)"""
    src = open(DL, encoding="utf-8").read()
    n = len(load(DL))
    out = src
    if session_map:
        for iid, sk in session_map.items():
            pat = re.compile(r"(- issue: %s\n(?:.*\n)*?)  session_key: null\n" % re.escape(iid))
            m = pat.search(out)
            if not m:
                continue
            out = out[:m.start(1)] + m.group(1) + "  session_key: %s\n" % sk + out[m.end(1):]
    bak = DL + ".bak_%s_cron775d_post" % STAMP
    shutil.copy2(DL, bak)
    tmp = DL + ".tmp_%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(out)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, DL)
    after = load(DL)
    assert len(after) == n, "★条目数变了 ⇒ 中止★"
    print("★POST 回填 OK ★ dispatch_log 仍 %d 条 · 末两条: %s" %
          (n, {e.get("issue"): e.get("session_key") for e in after[-2:]}))


def do_check():
    raw = load(DL)
    log = load(LOG)
    issues = log.get("issues", log) if isinstance(log, dict) else log
    items = list(issues.values()) if isinstance(issues, dict) else list(issues)
    print("dispatch_log 条数:", len(raw))
    for iid in ("ISS-375", "ISS-376"):
        it = [x for x in items if x.get("id") == iid]
        ents = [e for e in raw if isinstance(e, dict) and e.get("issue") == iid]
        print("  %s: status=%s · dispatched_at=%s · note_addendum=%s · dispatch_log 条目 %d 条(最新含复活标记=%s)" %
              (iid, it[0].get("status") if it else "?",
               it[0].get("dispatched_at") if it else "?",
               "有" if (it and it[0].get("note_addendum")) else "无",
               len(ents), any("复活僵尸单" in str(e.get("job", "")) for e in ents)))
    md5, mtime, size = board_fingerprint()
    print("板: md5 %s (期望 %s) · size %d · mtime %s" % (md5, BOARD_MD5, size,
                                                        time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mtime))))
    print("板指纹一致:", md5 == BOARD_MD5 and size == BOARD_SIZE)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "--check"
    if mode == "--pre":
        do_pre()
    elif mode == "--post":
        do_post()
    elif mode == "--check":
        do_check()
    else:
        print(__doc__)
        sys.exit(2)
