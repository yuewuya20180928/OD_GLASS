#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20261124_0720_cronfb67_addend_381_382.py
=================================================
cron fb67af40 (ARS45 队列自动派活) · 2026-11-24 07:2x
★**给 ISS-381 / ISS-382 追加 `note_addendum` (cont1 续派留痕)· status 保持 fixing 不动★**

★**为什么单独一个脚本★**: 前一个脚本 `_apply_20261124_0715_cronfb67_cont1_381_382_open_383.py`
  的 `dump_field()` 把 `yaml.safe_dump` 的【唯一一行】当成了 "issues:" 那样的头部给丢掉了
  ⇒ ★**实际一行都没插进去** ⇒ 脚本在自己的断言处停下 (rc=1) ⇒ ★**ISS-383 已落, 但两条 note_addendum 缺失**
  ⇒ ★**本脚本把缺的那两块补上** (★ISS-383 不重复开·★已在盘★) ★
★**并发写盘护栏**: `os.replace` 前重算 md5, 与开读时不一致 ⇒ 中止 (rc=3)
"""
import hashlib
import os
import shutil
import sys
import time

import yaml

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
LOG = os.path.join(PROJ, "state", "issue_log.yaml")
STAMP = time.strftime("%Y%m%d_%H%M")

BRIEF_381_C = "state/dispatch_briefs/ISS-381_sw_zero_false_connectivity_gate_cont1.md"
BRIEF_382_C = "state/dispatch_briefs/ISS-382_mech_jdebug_arrangement_truth_cont1.md"

NOTE_381_ADD = (
    "★2026-11-24 07:1x cron fb67af40 【cont1 续派 (★不是重做·★)】★★ ★**死因 (本机实读)★**: "
    "上一子会话 `agent:sw-lead:subagent:b55663b5-2cc8-4f58-9e22-00e692911b66` "
    "(sessionId `fb908701-f453-48d6-babb-7035b69be1ac`) 于 06:56:17 【掐死】(★`status=timeout` + "
    "`abortedLastRun=true` + startedAt 06:43:57 + runtimeMs 737,696 ≈ 12.3 分钟·★transcript 571,250 B @06:56 "
    "在盘·★不是空壳·★有 tool_use 记录★)★ ⇒ ★**四件交付物零落盘** (`SW/BOARD_ONEPASS_ZERO_FALSE_CONNECTIVITY.md` 无 · "
    "`SW/tools/check_sw_false_connectivity_gate.py` 无 · 交卷页 无 · `state/fragments/sw.yaml` 里 `iss381` 命中 0) ★ "
    "⇒ ★**死因 = 重活与交付物放同一趟 (12 分钟全花在读资料 + 跑探针上·最后一步才开始写) ⇒ 墙一到 ⇒ 什么都没留下 "
    "(★项目硬规矩 L-13 的第二种形态★)** ★ ★**但上一趟的重活【已经在盘】★**: `tmp/iss381_sbx/probe_pads.py` (自写 s-expr 解析器) · "
    "`tmp/iss381_sbx/board_nets.json` (43,364 B · 每网 `cu` 铜长 mm / `seg` 铜段数 / `pads` 焊盘集合) · "
    "`tmp/iss381_sbx/board_nets_pcbnew.json` (25,867 B · pcbnew 口径对照) · `tmp/iss381_sbx/probe_pcbnew.py` · "
    "`logs/iss381/baseline_fingerprints.txt` (板 + 三张表 + 5 个既有闸 + 1 个既有页的 md5 基线) ⇒ "
    "★**cont1 = 落盘趟: 读数已在盘·不许重跑·第一个动作就是写交付物·每完成一件立刻落盘** ★ "
    "★**续做任务书全文**: `" + BRIEF_381_C + "` (★命令存在性守卫 `state/check_brief_commands.py --brief-file` rc=0★) ★ "
    "★**status 保持 fixing 不动** (★铁律⑩-k①: 不落 open ⇒ 兄弟 job 的 advance.py 看不见 ⇒ 撞车窗口 0★) ★"
)

NOTE_382_ADD = (
    "★2026-11-24 07:1x cron fb67af40 【cont1 续派 (★不是重做·★)】★★ ★**死因 (本机实读)★**: "
    "上一子会话 `agent:mech-lead:subagent:0fa8bb52-63c9-44f2-ae07-472831cac2f0` "
    "(sessionId `166fef77-ac5b-46f1-8eb2-115f121a9b5b`) 于 06:56:16 【掐死】(★`status=timeout` + "
    "`abortedLastRun=true` + startedAt 06:44:18 + runtimeMs 716,511 ≈ 12.0 分钟·★transcript 497,757 B @06:56 在盘★)★ ⇒ "
    "★**真相页 / 交卷页 / 分片三件零落盘** ⇒ ★**但闸本体已在盘**: `MECH/check_jdebug_arrangement_truth.py` "
    "(53,040 B @06:51) ⇒ ★**main 本机实跑 `python3 MECH/check_jdebug_arrangement_truth.py --selftest` ⇒ 报 "
    "`✗ 正向对照直接 IO 失败: 文件不在盘: …/MECH/BOARD_ONEPASS_JDEBUG_ARRANGEMENT_TRUTH.md` ⇒ ★★【闸本身没坏·只差页】★★ "
    "⇒ ★**cont1 = 收尾趟: 闸就是页的规格书 ⇒ 读它 → 照它写页 → 闸立刻就绿** ★ "
    "★**另一份重活也已在盘**: `tmp/iss382_sbx/ledger.json` (1,554 B · 已签收页里全部「几列×几行 / 2x2 / 2×2」表述的逐处清单 "
    "file/line/surface/cols/rows/staggered/proposed) · `tmp/iss382_sbx/gen_ledger.py` · `tmp/iss382_sbx/probe_claims.py` / "
    "`probe_claims2.py` · `logs/iss382/before_check_connector_caliber.log` (★K7 本来就红 2 条·★是基线不是要修的★) · "
    "`logs/iss382/before_check_jdebug_1p27.log` ⇒ ★**不许重扫整页** ★ "
    "★**续做任务书全文**: `" + BRIEF_382_C + "` (★命令存在性守卫 rc=0★) ★ "
    "★**status 保持 fixing 不动** (★铁律⑩-k①★) ★"
)


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def dump_field(name, value, indent="  "):
    """★dump 成【一个列表项里的映射字段】⇒ 缩进 2 空格·★不丢首行★"""
    txt = yaml.safe_dump({name: value}, allow_unicode=True, sort_keys=False,
                          default_flow_style=False, width=100000)
    lines = [l for l in txt.rstrip("\n").split("\n") if l.strip()]
    assert lines and lines[0].startswith(name + ":"), lines[0]
    return "\n".join(indent + l for l in lines) + "\n"


def insert_field(raw, issue_id, field, value):
    lines = raw.split("\n")
    start = None
    for i, ln in enumerate(lines):
        if ln.startswith("- id: %s" % issue_id):
            start = i
            break
    if start is None:
        raise SystemExit("★★找不到条目 %s" % issue_id)
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("- id: "):
            end = j
            break
    k = end
    while k > start + 1 and lines[k - 1].strip() == "":
        k -= 1
    add = dump_field(field, value).rstrip("\n").split("\n")
    return "\n".join(lines[:k] + add + lines[k:]) + "\n"


def main():
    raw = open(LOG, encoding="utf-8").read()
    md5_before = md5(LOG)
    doc = yaml.safe_load(raw)
    issues = doc.get("issues") or []
    ids = {i.get("id") for i in issues}
    assert "ISS-383" in ids, "ISS-383 不在盘 (先跑开单脚本)"
    for iid in ("ISS-381", "ISS-382"):
        it = [x for x in issues if x.get("id") == iid][0]
        assert it.get("status") == "fixing", (iid, it.get("status"))
        assert not it.get("note_addendum"), "%s 已有 note_addendum ⇒ 不重复写" % iid
    print("★ 开读时: issue_log md5=%s · 条数=%d" % (md5_before, len(issues)))

    raw2 = insert_field(raw, "ISS-381", "note_addendum", NOTE_381_ADD)
    raw2 = insert_field(raw2, "ISS-382", "note_addendum", NOTE_382_ADD)

    # ★先验证 YAML 仍可解析 + 条数不变 + 两条 note_addendum 都在★ (写在真件之前)
    probe = yaml.safe_load(raw2)
    pids = [i.get("id") for i in (probe.get("issues") or [])]
    assert len(pids) == len(issues), ("条数变了", len(pids), len(issues))
    for iid in ("ISS-381", "ISS-382"):
        it = [x for x in probe["issues"] if x.get("id") == iid][0]
        assert it.get("note_addendum") and it.get("status") == "fixing", iid
    assert set(pids) == {i.get("id") for i in issues}, "id 集合变了"

    bak = LOG + ".bak_%s_cronfb67_addend" % STAMP
    shutil.copy2(LOG, bak)
    tmp = LOG + ".tmp_%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(raw2)
        f.flush()
        os.fsync(f.fileno())
    md5_now = md5(LOG)
    if md5_now != md5_before:
        os.unlink(tmp)
        print("★★中止 (rc=3): issue_log 在本脚本开读之后被改过 (md5 %s → %s) ⇒ 不写, 请重跑"
              % (md5_before, md5_now))
        return 3
    os.replace(tmp, LOG)
    doc2 = yaml.safe_load(open(LOG, encoding="utf-8").read())
    got = {i.get("id"): i.get("status") for i in (doc2.get("issues") or [])}
    for iid in ("ISS-381", "ISS-382", "ISS-383"):
        assert got.get(iid) == "fixing", (iid, got.get(iid))
    assert len(doc2.get("issues") or []) == len(issues)
    print("★ issue_log 已落: ISS-381 + ISS-382 追加 note_addendum (status 仍 fixing) · ISS-383=fixing "
          "(条数 %d · 备份 %s · 新 md5=%s)" % (len(issues), os.path.basename(bak), md5(LOG)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
