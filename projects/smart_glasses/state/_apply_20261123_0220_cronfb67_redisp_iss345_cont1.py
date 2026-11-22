#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20261123_0220_cronfb67_redisp_iss345_cont1.py
================================================================================
cron fb67af40 (ARS45 队列自动派活) · 2026-11-23 02:2x
--------------------------------------------------------------------
【重派】ISS-345 (mech-lead) —— 把一条【被 abort 掐死的僵尸 fixing 单】救回来

★★为什么必须重派 (★main 02:1x 本机实读, 不猜★)★★:
  ★**上一轮 mech-lead 会话 `03afe97e-e265-42bd-8da7-36ec76ab97cb` (01:03→01:55) 被 abort**
    (★transcript 末行 `openclaw:prompt-error` = "This operation was aborted"·
      `abortedLastRun: true`·`status: timeout`★
  ★⇒ **它 52 分钟全耗在探索上, 真件 8 个脚本一个字节都没改**
    (★main 实测: `MECH/pinset2_mech_check.py` 与 `tmp/iss345_base/pinset2_mech_check.py`
      `diff` = IDENTICAL · `grep -c B160x100` = 0 · mtime 仍是 11-11 17:26★)
  ★⇒ **但它把「半成品」留在了盘上** (★这正是「先落盘, 后填内容」铁律的价值★):
    · `logs/iss345/00_drift_PRE.txt` + `base_pinset2_mech_check.txt`
      + `base_skeleton_section_check.txt` + 其余 3 个 base_*.txt  (★迁移前基线输出★)
    · `tmp/iss345_base/` (★5 个脚本的迁移前副本 + mech_md5_pre.txt + pj_before.json
      + probe_som*.py 板面探针★)
    · `HANDOFF/2026-11-23_mech-lead_ISS345_8脚本迁双口径.md` (★949 B · B1~B6 六块骨架★)
  ★⇒ 台账上 ISS-345 仍挂 `fixing` ⇒ **advance.py 的 in_flight 规则会永远挡住 mech-lead**
    ⇒ **僵尸 fixing ⇒ 队列静默停摆** ⇒ 必须本轮救回来

★★为什么切成第 1 批 (★不是偷懒, 是实测★)★★:
  ★**上一轮 = 单轮扛 8 个脚本 ⇒ 实测 52 分钟 0 字节改动 ⇒ 再派同样的活还是同样的结果**
  ★⇒ 本轮只扛【2 个脚本 + 对照证据 + 交卷页 + 分片】⇒ 保证单轮真正落地
  ★⇒ 剩余 3 个脚本 + 新闸 + 清单页订正 = 第 2 批 (交卷页 §B5 逐条写明)

★★status 保持 `fixing` (不落 `open`)★★:
  ★**兄弟 job (cron 775d9893「继续执行后继计划」) 也会读 `advance.py --json`**
  ★⇒ 若本单开一个 `open` 窗口 ⇒ 兄弟 job 会把同一条当自己的货派给 mech-lead
  ★⇒ **撞车 = 两个写会话同时写 `state/fragments/mech.yaml` ⇒ 分片合并丢 12%~38%** (★本仓已实测过★)
  ★⇒ 保持 `fixing` ⇒ 兄弟 job 看不见 ⇒ 不重复派

★**原子写 + 带 .bak + 幂等** ★
"""
from __future__ import annotations

import os
import shutil
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
BAK = LOG + ".bak_20261123_0220_cronfb67_redisp_iss345_cont1"
DL = os.path.join(HERE, "dispatch_log.yaml")
DL_BAK = DL + ".bak_20261123_0220_cronfb67_redisp_iss345_cont1"
BRIEF_DIR = os.path.join(HERE, "dispatch_briefs")

IID = "ISS-345"
OWNER = "mech-lead"
ORIG_BRIEF = "ISS-345_mech_8脚本迁双口径.md"
CONT_BRIEF = "ISS-345_mech_8脚本迁双口径_cont1.md"
NOW = "2026-11-23 02:2x"

NOTE_ADD = (
    " ★★★[2026-11-23 02:2x · cron fb67af40 重派 cont1]★★★ "
    "★**上一轮 mech-lead 会话 `03afe97e-e265-42bd-8da7-36ec76ab97cb` (01:03→01:55) 被 abort "
    "(★transcript 末行 `openclaw:prompt-error` = 'This operation was aborted'·abortedLastRun=true·status=timeout★) "
    "⇒ 52 分钟全耗在探索上, ★**真件 8 个脚本一个字节都没改** (★main 实测 diff=IDENTICAL·grep B160x100=0·mtime 仍 11-11 17:26★) "
    "⇒ 台账挂 fixing ⇒ 僵尸 fixing ⇒ advance.py 的 in_flight 规则会永远挡住 mech-lead ⇒ 队列静默停摆 ★ "
    "★**它留下的半成品在盘 (★先落盘后填内容铁律救回来的★)**: `logs/iss345/00_drift_PRE.txt` + 5 份 `base_*.txt` (迁移前基线输出) "
    "+ `tmp/iss345_base/` (5 个脚本迁移前副本 + mech_md5_pre.txt + pj_before.json + probe_som*.py 板面探针) "
    "+ `HANDOFF/2026-11-23_mech-lead_ISS345_8脚本迁双口径.md` (949 B · B1~B6 骨架) ★ "
    "★**⇒ 本轮重派并【切成第 1 批 = 2 个脚本 (pinset2_mech_check.py + skeleton_section_check.py) + 对照证据 + 交卷页 + 分片】★ "
    "⇒ ★**单轮扛 8 个脚本已实测失败 (52 分钟 0 字节) ⇒ 宁可只交 2 个脚本, 也不许零产出** ★ "
    "★**第 2 批 (交卷页 §B5 写明)**: fit_check_v3_30mm.py / fit_check.py / cross_review_check.py + 新建 MECH/check_mech_dual_caliber_gate.py "
    "+ MECH/BOARD_GEOM_CALIBER_STATUS.md 的 scope A/B 真数追加式订正 + 漂移闸迁后重跑 ★ "
    "★**任务书 (cont1)**: `state/dispatch_briefs/%s` (★权威仍是原任务书 `%s`, cont1 只是切批 + 断点交接 + 铁律★) "
    "(★check_brief_commands.py --brief-file rc=0★) ★ "
    "★**status 保持 `fixing` (不落 open) ⇒ 兄弟 job 775d9893 看不见 ⇒ 不重复派** ★"
    % (CONT_BRIEF, ORIG_BRIEF)
)


def atomic_write(path: str, text: str) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def main() -> int:
    cont_path = os.path.join(BRIEF_DIR, CONT_BRIEF)
    cont = open(cont_path, encoding="utf-8").read()

    # ---------- issue_log ----------
    doc = yaml.safe_load(open(LOG, encoding="utf-8").read()) or {}
    issues = doc.get("issues") or []
    hit = [i for i in issues if i.get("id") == IID]
    if not hit:
        print("★%s 不在台账 ⇒ 中止 (不该发生)" % IID)
        return 2
    h = hit[0]
    before = (h.get("status"), h.get("dispatched_at"), len(h.get("task_brief") or ""))
    h["task_brief"] = cont
    h["dispatched_at"] = NOW
    h["status"] = "fixing"          # ★保持 fixing ⇒ 兄弟 job 看不见 ⇒ 不重复派★
    h["note"] = (h.get("note") or "") + NOTE_ADD
    out = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=100)
    if not os.path.exists(BAK):
        shutil.copy2(LOG, BAK)
        print("★备份 ->", os.path.basename(BAK))
    atomic_write(LOG, out)
    print("★%s 已重派 (status=%s·dispatched_at=%s·brief %d→%d chars)"
          % (IID, h["status"], h["dispatched_at"], before[2], len(cont)))

    # ---------- dispatch_log (顶层是 list ⇒ 追加式写回, 历史字节零改动) ----------
    dl = yaml.safe_load(open(DL, encoding="utf-8").read()) if os.path.exists(DL) else []
    if isinstance(dl, dict):
        dl_list = dl.setdefault("dispatches", [])
        shape = "dict"
    elif isinstance(dl, list):
        dl_list = dl
        shape = "list"
    else:
        dl_list, shape = [], "list"
    tag = "%s@cont1@%s" % (IID, NOW)
    if any(str(e.get("brief", ""))[:80].find(tag) >= 0 or e.get("at") == NOW for e in dl_list):
        print("★dispatch_log 已有本次重派记录 ⇒ 跳过")
    else:
        entry = {
            "issue": IID,
            "agent": OWNER,
            "at": NOW,
            "brief": ("[重派 cont1] " + tag + " · 上一轮会话被 abort 掐死 (52 分钟 0 字节改动) ⇒ "
                      "僵尸 fixing 救回 ⇒ 切成第 1 批 = 2 个脚本 (pinset2_mech_check.py + skeleton_section_check.py) "
                      "+ 对照证据 + 交卷页 + 分片 · 任务书 state/dispatch_briefs/" + CONT_BRIEF
                      + " (权威仍是原任务书 " + ORIG_BRIEF + ")"),
            "job": ("cron fb67af40 (ARS45 队列自动派活) · ★重派时刻 2026-11-23 02:2x · "
                    "★**status 保持 fixing ⇒ 兄弟 job 775d9893 的 advance.py --json 看不见本单 ⇒ 不会重复派**"),
        }
        if not os.path.exists(DL_BAK):
            shutil.copy2(DL, DL_BAK)
        with open(DL, "a", encoding="utf-8") as f:
            if shape == "list":
                f.write(yaml.safe_dump([entry], allow_unicode=True, sort_keys=False, width=200))
        if shape == "dict":
            atomic_write(DL, yaml.safe_dump(dl, allow_unicode=True, sort_keys=False, width=200))
        print("★dispatch_log 已追加 1 条 (%s cont1)" % IID)

    # ---------- 自检 ----------
    doc2 = yaml.safe_load(open(LOG, encoding="utf-8").read())
    ids = [i.get("id") for i in doc2["issues"]]
    dup = sorted({x for x in ids if ids.count(x) > 1})
    print("★issues 条数 =", len(ids), "· 重复 id =", dup or "无")
    hh = [i for i in doc2["issues"] if i.get("id") == IID][0]
    print("★%s status=%s owner=%s due=%s brief=%d chars verify_by=%s"
          % (IID, hh.get("status"), hh.get("owner"), hh.get("due"),
             len(hh.get("task_brief") or ""), hh.get("verify_by")))
    dl2 = yaml.safe_load(open(DL, encoding="utf-8").read())
    dl2_list = dl2 if isinstance(dl2, list) else (dl2 or {}).get("dispatches", [])
    print("★dispatch_log 条数 =", len(dl2_list), "· 末条 =", dl2_list[-1].get("issue"))
    return 0 if not dup else 1


if __name__ == "__main__":
    sys.exit(main())
