#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20261124_0435_cronfb67_redisp_iss379_cont1.py
=====================================================
main (项目总工 / moli) · cron fb67af40 「ARS45 队列自动派活」· 2026-11-24 04:3x
★★【僵尸 fixing 重派 cont1】★★ ISS-379 (hw-lead) ★★

★**为什么本 job 要做这件事 (★本机实读 + 实算, 不抄任何 agent 报告★)**:
  ① `python3 state/advance.py --json` 实读 (04:1x) ⇒ ★**`internal: []`** (★三个总工名下零 open 可派★)
  ② ★**ISS-379 (hw-lead) = `fixing`, 但它的子会话已于 04:09:44 【失败】退出** ⇒ ★**死因 = 会话失败, 不是超时墙**
     · 子会话 `agent:hw-lead:subagent:41aa8bc6-a590-483f-ab92-9a09b7e06d81` / sessionId `89756ed5-f579-4d9e-a6b6-3c328c2119b3`
     · `sessions_list` 实读: status=**failed** · startedAt 03:41:20 · endedAt 04:09:44 · runtimeMs 1,494,447 ≈ 24.9 分钟
     · transcript 在盘 1,326,515 B @04:09:41 ⇒ ★**不是空壳** ★
  ③ ★**三件交付物已在盘** (★部分交付★): 真相页 `HW/PCB/BOARD_ONEPASS_JUART_LAND_FIT.md` (41,954 B @04:09)
     + 新闸 `HW/check_juart_land_fit.py` (52,919 B @04:08) + 交卷页 `HANDOFF/2026-11-24_hw-lead_ISS379_JUART排针换land落位可行性.md` (28,352 B @04:04)
  ④ ★**但新闸是红的** (★main 本机实跑 rc=1★): `K2 FAIL: rot 90 格 (7.4000,75.8000) 余量 证据=3.1266 闸算=3.1267`
     ⇒ `--selftest` 也红 (基线必须全绿, 但红了: ['K2']) ⇒ ★**交不了卷** ★
     ⇒ ★**⇒ 这是一条"活着但红"的单: 槽位被僵尸 fixing 占着, 产物也差最后一步 ⇒ 必须续派, 不许让它烂在 fixing 上** ★
  ⑤ ★**上一趟死前最后一句 (transcript 末行实读)** = "Now let me fix the RULES netclass block and the §1.4 hole-clearance wording in the page, then check the re-run."
     ⇒ ★**它正要改页时死了** ⇒ ★**`RULES` 块实测已对齐盘面 (K1 PASS) · §1.4 冲突表已在盘 (K3 PASS) ⇒ 本单正题只有 K2** ★
  ⑥ ★**扫描孤儿进程已在 04:18:33 跑完并落盘** (`logs/iss379/scan_land_fit.json` · elapsed_s 566.8 ⇒ 起跑 ≈04:08:47 ⇒ ★**死在会话之后·产物还在**★)
     ⇒ ★**重跑产物与 modeA 同值 (3.1266) ⇒ 那次重跑没有修掉差值** ★
  ⑦ ★**hw-lead 槽位可回收的实测依据 (★按 `state/ZOMBIE_FIXING_WATCHLIST.md` 的"三与判据"逐条跑★)**:
     | 单 | ① transcript 在盘 | ② 末行 timestamp | ③ 产物 mtime 在动 | 判定 |
     |---|---|---|---|---|
     | ISS-376 会话 (hw-lead) | ✔ 199,663 B @04:21:59 | 静默 (最后一条 = 交卷摘要) | ✘ hw 侧最后一次写盘 04:21:30 | ★**已交卷·僵尸登记★** (★main 03:29~04:14 已签收 verified★) |
     | ISS-379 会话 (hw-lead) | ✔ 1,326,515 B @04:09:41 | 已结束 (status=failed) | ✘ logs/iss379/ 最新 04:18:33 (★孤儿扫描★) | ★**已死★** |
     ⇒ ★**hw-lead 名下没有任何活着的写会话 ⇒ 槽位可回收** ★
     (★对照: mech-lead 会话 04:23 仍在写 · sw-lead 四条会话 04:23~04:33 仍在写 (含 `state/fragments/sw.yaml` @04:27) ⇒ ★**两个槽位真在飞, 本单不碰★** ★)

★**落盘纪律 (★铁律⑩-i / ⑩-k①★)**:
  - ★**status 保持 `fixing` 不动** ⇒ ★**不落 open** ⇒ ★**兄弟 job 775d9893 的 `advance.py --json` 看不见 ⇒ 撞车窗口 = 0** ★
  - ★**先落盘 (dispatch_log + issue_log note) 再 spawn** ⇒ ★**spawn 失败也不留空壳日志** ★
  - ★**零写板** (板 md5 / mtime / size 三项开工前后各打一次) ★
  - ★**不改 `PROJECT_TRACKER.md` §0** · ★**不写别的 agent 的分片** (★只改 main 自己的 issue_log + dispatch_log★) · ★**零外发** · ★**不代老板拍板** ★
  - ★**issue_log 用【原文拼接】写 ⇒ 4.7 MB 台账除目标段外逐字节不动 (零 churn)** ★

用法:
  python3 state/_apply_20261124_0435_cronfb67_redisp_iss379_cont1.py --pre      # ★spawn 前落盘★
  python3 state/_apply_20261124_0435_cronfb67_redisp_iss379_cont1.py --post     # ★spawn 后回填 session_key★
  python3 state/_apply_20261124_0435_cronfb67_redisp_iss379_cont1.py --check    # ★只读自检★
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

IID = "ISS-379"
AGENT = "hw-lead"
BRIEF = "state/dispatch_briefs/ISS-379_hw_juart_land_fit_cont1.md"
PREV_SESS = "agent:hw-lead:subagent:41aa8bc6-a590-483f-ab92-9a09b7e06d81"
PREV_SID = "89756ed5-f579-4d9e-a6b6-3c328c2119b3"

DEATH = ("★**status=failed** (★不是 timeout 墙·不是 abortedLastRun·externalAbort 未置位·★会话自己失败退出★) · "
         "startedAt 2026-11-24 03:41:20 · endedAt 04:09:44 · runtimeMs 1,494,447 ≈ 24.9 分钟 · "
         "★transcript 在盘 1,326,515 B @04:09:41 (★不是空壳·★有 tool_use 记录★)★")

PARTIAL = ("★**三件交付物已在盘 (★部分交付★)**: 真相页 `HW/PCB/BOARD_ONEPASS_JUART_LAND_FIT.md` (41,954 B @04:09) + "
           "新闸 `HW/check_juart_land_fit.py` (52,919 B @04:08) + 交卷页 "
           "`HANDOFF/2026-11-24_hw-lead_ISS379_JUART排针换land落位可行性.md` (28,352 B @04:04) + "
           "扫描脚本 `tmp/iss379/tools/scan_land_fit.py` (823 行 @04:09) + 证据 JSON `logs/iss379/scan_land_fit_modeA.json` "
           "(8,450,292 B @04:07) + 孤儿扫描产物 `logs/iss379/scan_land_fit.json` (8,450,311 B @04:18:33) ⇒ "
           "★**零缺口 = 闸红**★ ⇒ ★**新闸 K2 红 (rc=1)**: `rot 90 格 (7.4000,75.8000) 余量 证据=3.1266 闸算=3.1267` · "
           "`--selftest` 基线红 (['K2']) ⇒ ★**交不了卷**★")

JOB_TAG = ("cron fb67af40 (ARS45 队列自动派活) · ★ISS-379 cont1 续派时刻 2026-11-24 04:3x · "
           "★**status 保持 fixing 不动** (★铁律⑩-k①: 不落 open ⇒ 兄弟 job 的 advance.py --json 看不见 ⇒ 撞车窗口 0★) · "
           "★**死因 = 上一子会话 `{sess}` (sessionId {sid}) 于 2026-11-24 04:09:44 【失败】退出** (★{death}★) · "
           "★**上一趟留下的活**: {partial}★ · "
           "★**本趟 = 从已落的活续做 (★不是从零★): 正题只有 K2 一条红**★ · "
           "★**任务书全文**: `{brief}` (★命令存在性守卫 `state/check_brief_commands.py --brief-file` rc=0★) · "
           "★**零写板 · 零落表 · 零外发 · 不代拍** ★")


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
    anchor = "\n  dispatched_at:"
    k = seg.find(anchor)
    if k < 0:
        raise SystemExit("★%s 段里找不到 dispatched_at ⇒ 中止★" % iid)
    add = ("\n  note_addendum: '%s'\n" % new_note.replace("'", "''"))
    return src[:i] + seg[:k] + add + seg[k:] + src[j:]


def do_pre():
    md5, mtime, size = board_fingerprint()
    assert md5 == BOARD_MD5, "★板 md5 已变 (★%s) ⇒ 中止★" % md5
    assert size == BOARD_SIZE, "★板 size 已变 ⇒ 中止★"

    # ---- 1) issue_log: 原文拼接 (零 churn) ----
    src = open(LOG, encoding="utf-8").read()
    before_md5 = hashlib.md5(src.encode("utf-8")).hexdigest()
    tag = ("★2026-11-24 04:3x cron fb67af40 【僵尸 fixing 重派 cont1】★★ "
           "★**死因**: 上一子会话 `{sess}` (sessionId {sid}) 于 04:09:44 【失败】退出 (★{death}★)★ · "
           "★**上一趟留下的活**: {partial}★ · "
           "★**本趟正题 = 把新闸 K2 那条红修绿 (★rot 0 逐格一致 ⇒ 问题只在 rot 90 的几何路径·★不许放宽 1e-6 容差·★不许手工改证据 JSON 的数·★修在产生点★)★** · "
           "★**任务书全文**: `{brief}` (★命令存在性守卫 rc=0★)★ · "
           "★**status 保持 fixing 不动** (★铁律⑩-k①: 不落 open ⇒ 兄弟 job 的 advance.py --json 看不见 ⇒ 撞车窗口 0★)★ · "
           "★**hw-lead 槽位可回收依据 (三与判据)**: ISS-376 会话末行 04:21:59 = 交卷摘要 + hw 侧最后一次写盘 04:21:30 ⇒ 已交卷僵尸登记; "
           "ISS-379 会话 status=failed ⇒ 已死 ⇒ ★**hw-lead 名下零活会话 ⇒ 槽位可回收**★ · "
           "★**零写板 · 零落表 · 零外发 · 不代老板拍板**★").format(
        sess=PREV_SESS, sid=PREV_SID, death=DEATH, partial=PARTIAL, brief=BRIEF)
    new_src = splice_log(src, IID, tag)
    bak = LOG + ".bak_%s_cronfb67_redisp_iss379_cont1" % STAMP
    shutil.copy2(LOG, bak)
    tmp = LOG + ".tmp_%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(new_src)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, LOG)
    after_src = open(LOG, encoding="utf-8").read()
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
    assert i1[IID].get("status") == "fixing", "★%s status 被改了 ⇒ 中止★" % IID

    # ---- 2) dispatch_log: 追加式 (历史字节不动) ----
    raw = load(DL)
    assert isinstance(raw, list), "★dispatch_log 顶层不是 list ⇒ 中止★"
    before = len(raw)
    with open(os.path.join(PROJ, BRIEF), encoding="utf-8") as fh:
        brief_text = fh.read()
    entry = {
        "issue": IID,
        "agent": AGENT,
        "at": "2026-11-24",
        "brief": brief_text[:300],
        "brief_file": BRIEF,
        "job": JOB_TAG.format(sess=PREV_SESS, sid=PREV_SID, death=DEATH, partial=PARTIAL, brief=BRIEF),
        "session_key": None,
        "run_id": None,
        "task_name": None,
        "dispatched_at": "2026-11-24 04:3x",
        "prev_session_key": PREV_SESS,
        "redispatch_zombie": "True",
        "partial_delivery": ("★**上一趟留下的活**: " + PARTIAL),
        "status_note": ("★台账 status 保持 fixing (未改) ⇒ advance.py in_flight 规则继续挡住任何 job "
                        "给 %s 再派活 ⇒ 零撞车窗口★" % AGENT),
    }
    dl_bak = DL + ".bak_%s_cronfb67_redisp_iss379_cont1" % STAMP
    shutil.copy2(DL, dl_bak)
    chunk = yaml.safe_dump([entry], allow_unicode=True, sort_keys=False, width=200)
    with open(DL, "a", encoding="utf-8") as fh:
        with open(DL, "rb") as rf:
            rf.seek(-1, os.SEEK_END)
            if rf.read(1) != b"\n":
                chunk = "\n" + chunk
        fh.write(chunk)
    after = load(DL)
    assert isinstance(after, list) and len(after) == before + 1, "★dispatch_log 条目数不对 ⇒ 中止★"
    assert after[-1]["issue"] == IID, "★dispatch_log 末条不对 ⇒ 中止★"

    md5b, _, sizeb = board_fingerprint()
    assert (md5b, sizeb) == (BOARD_MD5, BOARD_SIZE), "★板被写了 ⇒ 中止★"
    print("★PRE 落盘 OK ★")
    print("   issue_log: md5 %s → %s (★除本条 note_addendum 外逐字节不变★) · 备份 %s" %
          (before_md5[:12], hashlib.md5(after_src.encode('utf-8')).hexdigest()[:12], os.path.basename(bak)))
    print("   dispatch_log: %d → %d 条 (★历史字节不动·追加式★) · 备份 %s" %
          (before, before + 1, os.path.basename(dl_bak)))
    print("   板指纹: md5 %s · size %d · mtime %s ⇒ OK" % (md5b, sizeb, mtime))
    return 0


def do_post():
    """spawn 后回填 session_key / run_id / task_name 到 dispatch_log 末条 (★原文拼接, 历史字节不动★)"""
    if len(sys.argv) < 3:
        raise SystemExit("★用法: --post <session_key> <run_id> [task_name]★")
    sk, rid = sys.argv[2], sys.argv[3]
    tn = sys.argv[4] if len(sys.argv) > 4 else None
    src = open(DL, encoding="utf-8").read()
    i = src.rfind("- issue: %s" % IID)
    if i < 0:
        raise SystemExit("★dispatch_log 末条没定位到 ⇒ 中止★")
    j = src.find("\n- issue: ", i + 10)
    seg = src[i:j] if j > 0 else src[i:]
    old = ("  session_key: null\n  run_id: null\n  task_name: null\n")
    if old not in seg:
        raise SystemExit("★dispatch_log 末条没有 null 占位 ⇒ 中止★")
    new = ("  session_key: '%s'\n  run_id: '%s'\n  task_name: '%s'\n" % (sk, rid, tn or ""))
    new_src = src[:i] + seg.replace(old, new) + (src[j:] if j > 0 else "")
    bak = DL + ".bak_%s_cronfb67_redisp_iss379_post" % STAMP
    shutil.copy2(DL, bak)
    tmp = DL + ".tmp_%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(new_src)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, DL)
    after = load(DL)
    assert len(after) == len(load(bak)), "★dispatch_log 条目数变了 ⇒ 中止★"
    print("★POST 回填 OK ★ 末条 session_key=%s run_id=%s task_name=%s" % (sk, rid, tn))
    return 0


def do_check():
    raw = load(DL)
    log = load(LOG)
    iss = {x.get("id"): x for x in (log.get("issues", log) if isinstance(log, dict) else log)}
    md5, mtime, size = board_fingerprint()
    print("dispatch_log 条目数:", len(raw))
    print("末条:", raw[-1].get("issue"), raw[-1].get("agent"), raw[-1].get("brief_file"),
          "| session_key:", raw[-1].get("session_key"))
    print("%s: status=%s · dispatched_at=%s · note_addendum=%s" %
          (IID, iss[IID].get("status"), iss[IID].get("dispatched_at"),
           ("有" if iss[IID].get("note_addendum") else "无")))
    print("板指纹: md5 %s · mtime %s · size %d" % (md5, mtime, size))
    return 0


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "--check"
    if mode == "--pre":
        sys.exit(do_pre())
    if mode == "--post":
        sys.exit(do_post())
    if mode == "--check":
        sys.exit(do_check())
    raise SystemExit("★未知参数 %s★" % mode)
