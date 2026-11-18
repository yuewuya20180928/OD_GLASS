#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
moli (项目总工) 2026-11-17 19:0x · job fb67af40「ARS45 队列自动派活」
★★★ISS-295 cont2 / ISS-297 cont1 / ISS-298 cont1 三条【续做重派】★★★
=========================================================================================
★**为什么有这一趟 (★main 19:0x~19:2x 本机实查盘面 + 读会话, 不抄任何交卷报告★)**:
  · ★**三个 agent 的会话在 18:28~18:47 之间【全部超时死掉】** ★ (★不是被 kill, 是 runtime 到顶 / Aborted★):
      - `agent:mech-lead:subagent:f0b68fcc` (sessionId 4d2565ef) 18:13:48 → 18:28:32 · runtime 881s · status=timeout/abortedLastRun=true
        ⇒ transcript 末行 = assistant「Backing up the two pages before the append-only edit, then generating the correction sections:」
          → toolResult「[openclaw] missing tool result in session history…」⇒ ★**死在「两页追加订正节」之后、「填交卷单 + 写分片」之前** ★
      - `agent:hw-lead:subagent:51b84574` (sessionId 64aaa9ad) 18:30:18 → 18:47:28 · runtime 1026s · status=timeout/abortedLastRun=true
        ⇒ transcript 末行 = assistant「Confirmed: those 2 legacy cases were already failing before my change (stale fixture vs ISS-283's newer md5).
          Let me fix the stale fixtures to be dynamic:」→ toolResult「Aborted」⇒ ★**死在「修 2 条过期 fixture」那一刻** ★
      - `agent:sw-lead:subagent:eefd6258` (sessionId 68654eaf) 18:30:17 → 18:47:28 · runtime 1026s · status=timeout/abortedLastRun=true
        ⇒ transcript 末行 = assistant「Now let me gather key facts before implementing…」→ toolResult「Aborted」⇒ ★**死在「还没动手改闸」那一刻** ★
  · ⇒ ★**本 job 的 `advance.py --json` 此刻 `internal: []`** (★三个 owner 名额全被 `fixing` 占着★) ⇒ ★**但盘面 ≠ 名单 (★老坑, 第六次了★)** ★
    ⇒ ★**三个 `fixing` 全是【僵尸 fixing】(★会话已死, 活儿没干完★) ⇒ 不重派就【永远卡死在 fixing】** ★
  · ⇒ ★**本趟做三件事**: ①ISS-295 cont2 续做重派 (★两页订正节已追加好 + CLAIMS 页已写好 + 新闸已写好但跑不通★)
    ②ISS-297 cont1 续做重派 (★`HW/board_reboard.py` + `HW/PCB/BOARD_ONEPASS_MD5_LEDGER.md` + 第 1 道闸已做好★)
    ③ISS-298 cont1 续做重派 (★交卷单骨架已建, 闸本体一个字没改★)
★**★铁律**: 干活的人不许自签 ⇒ verify_by=main · ★**零写板 · 零落表** ★
★**★零外发** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★) ⇒ ★**本 job 不发任何邮件/询价/采购** ★
★**边界**: ★**只写 `state/issue_log.yaml` + `state/dispatch_log.yaml` 两个文件** ⇒ ★**不碰任何 agent 的分片**
  (★`state/fragments/*.yaml` 是三个总工的, main 不写★) · 不碰板 / 网表 / 脚表 / BOM / 决策页 / outbox / 任何闸脚本★
★**★status 全程保持 `fixing` ⇒ 无 open 窗口 ⇒ 兄弟 job 775d9893 不会重复派** ★
★**★另修 2 处 brief 路径笔误 (★`state/check_brief_commands.py` 本 job 开跑时点出来的★)**:
  · `state/fragments/hw-lead.yaml` 【不存在】⇒ 真身是 `state/fragments/hw.yaml`
  · `state/fragments/sw-lead.yaml` 【不存在】⇒ 真身是 `state/fragments/sw.yaml`
  ⇒ ★**两处都在 ISS-297 / ISS-298 的 task_brief 里, 且兄弟 job 18:3x 派活时已在【下发文本】里临时纠过 (★"任务书更正"抬头★)
    ⇒ ★**但 issue_log 里存的原文仍是错路径 ⇒ 下一轮任何 job 照抄 task_brief 都会再踩 ⇒ 本趟把【存稿本身】改对** ★
"""
import fcntl
import os
import shutil

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
DL = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
TODAY = "2026-11-17"

# ★(issue, owner, brief 文件名, ⑭/⑮ 节标题, 续做说明正文, 盘面摘要, dispatch_log 摘要)★
CONT = [
    ("ISS-295", "mech-lead",
     "ISS-295_mech_verdict_freshness_cont2.md",
     "⑮ · ISS-295 cont2 续做说明",
     "★**上一趟子会话 `agent:mech-lead:subagent:f0b68fcc` (sessionId 4d2565ef) 18:13:48 → 18:28:32 · runtime 881s · status=timeout/abortedLastRun=true "
     "⇒ transcript 末行 = assistant「Backing up the two pages before the append-only edit, then generating the correction sections:」"
     "→ toolResult「[openclaw] missing tool result in session history…」⇒ **死在「两页追加订正节」之后、「填交卷单 + 写分片」之前** ★",
     "★**盘面实况 (main 19:1x 实测)**: ① `MECH/BOARD_ONEPASS_MECH_CLAIMS.md` 37114 B · §0~§8 齐全 ⇒ **不许重做** · "
     "② `MECH/check_mech_verdict_freshness.py` 21330 B **存在但跑不通** (★主模式 L437 `for k, r in res[\"detail\"]` 按 2-元组解包 dict ⇒ ValueError; "
     "F2 锚点 XC-3 (12 字) / XC-6 (10 字) 违反该闸自己写的「≥14 字」规则 ⇒ 现状被判红; `--selftest` 6/7, 唯一失败的 ④ 是上面那条的连带★) "
     "③ **两页订正节已追加好 (mtime 18:25) + 两页现状句逐字一致 ⇒ 不许再追加一遍** · "
     "④ 交卷单 5368 B · B0~B6 标题在但 B3-1/B4/B5/B6 是占位 · ⑤ 分片 `grep -c iss295` = 0 ★",
     "★**【cont2 续做】重派 (★不是从零做★)★**: 会话 4d2565ef 18:13:48 → 18:28:32 · runtime 881s · status=timeout ⇒ 死在「两页追加订正节」之后 ⇒ "
     "★**盘上已有: CLAIMS 页 37114 B (完整) + 两页订正节 (mtime 18:25, 两页现状句逐字一致) + 新闸 21330 B (但主模式 L437 解包崩 + F2 锚点 XC-3/XC-6 长度 <14 判红 + selftest 6/7)** ★ "
     "⇒ ★**本趟只做 4 件**: ① 修 L437 解包 ② 换 2 条 ≥14 字锚点 (★main 已量好候选: XC-3 → `1 个: `J_USB_C` (16p @0.50 + 2×Ø0.65 对上, ` 40 字 / "
     "XC-6 → `现有 MECH 规格 (检修口 / 调试口两条` 23 字★) ⇒ 闸 rc=0 + selftest 7/7 ③ 填满交卷单 B3-1/B4/B5/B6 ④ 写分片 (grep -c iss295 ≥ 4) ★"),

    ("ISS-297", "hw-lead",
     "ISS-297_hw_legal_reboard_channel_cont1.md",
     "⑭ · ISS-297 cont1 续做说明",
     "★**上一趟子会话 `agent:hw-lead:subagent:51b84574` (sessionId 64aaa9ad) 18:30:18 → 18:47:28 · runtime 1026s · status=timeout/abortedLastRun=true "
     "⇒ transcript 末行 = assistant「Confirmed: those 2 legacy cases were already failing before my change (stale fixture vs ISS-283's newer md5). "
     "Let me fix the stale fixtures to be dynamic:」→ toolResult「Aborted」⇒ **死在「修 2 条过期 fixture」那一刻** ★",
     "★**盘面实况 (main 19:1x 实测)**: ① **新建** `HW/board_reboard.py` 35661 B (★HW 域 6 道闸共用判决库: check_pair / check_file / load_anchor / chain_state / "
     "row_has_four / CASES 10 条 / run_cases / build_sandbox / make_legal★) · ② **新建** `HW/PCB/BOARD_ONEPASS_MD5_LEDGER.md` 9216 B (★§5 锚点块已写好, 含 2 件 md5 + reboard: null★) · "
     "③ **改完 1 道闸** `HW/check_fsin_rootcause.py` rc=0 (★D5 已分两层 + import board_reboard + check_pair + run_cases; --selftest 已含 ⑯a~⑯c/⑯d/④/⑤a~⑤c★) · "
     "④ **5 道闸还没接通道** (★仍硬钉 611b869e★): check_g1a7_selection_landed L89/L90 · check_onepass_commit_order L101/L102 · "
     "check_onepass_preflight_coverage L60 · check_pin_function_labels L145/L146 · check_workpack_state_values L62 · "
     "⑤ `--selftest` 23/25 ⇒ 2 条红是 ⑭/⑮ 两条过期 fixture (★旧 md5 e06c1dd6… 已被 ISS-283 合法落表前移到 37f62ac3…★) ⇒ **不许删用例** · "
     "⑥ 交卷单不存在 ⇒ **新建** · ⑦ 分片 grep -c iss297 = 0 ★",
     "★**【cont1 续做】重派 (★不是从零做★)★**: 会话 64aaa9ad 18:30:18 → 18:47:28 · runtime 1026s · status=timeout ⇒ 死在「修 2 条过期 fixture」那一刻 ⇒ "
     "★**盘上已有: `HW/board_reboard.py` 35661 B (共用判决库) + `HW/PCB/BOARD_ONEPASS_MD5_LEDGER.md` 9216 B (§5 锚点块) + `HW/check_fsin_rootcause.py` 已改完 rc=0** ★ "
     "⇒ ★**本趟只做 4 件**: ① 修 2 条过期 fixture ⇒ selftest 25/25 ② 把 5 道闸接到通道上 (★判据方向不许变 + fail-closed 三条不许动 + reboard: null 仍纯 md5 硬保护★) "
     "③ 每道闸补 ≥4 条沙盒反向用例 ④ 新建交卷单 + 写分片 (grep -c iss297 ≥ 4) ★"),

    ("ISS-298", "sw-lead",
     "ISS-298_sw_legal_reboard_channel_cont1.md",
     "⑭ · ISS-298 cont1 续做说明",
     "★**上一趟子会话 `agent:sw-lead:subagent:eefd6258` (sessionId 68654eaf) 18:30:17 → 18:47:28 · runtime 1026s · status=timeout/abortedLastRun=true "
     "⇒ transcript 末行 = assistant「Now let me gather key facts before implementing: the ledger's change rows for the board, and the state gate scripts' behavior.」"
     "→ toolResult「Aborted」⇒ **死在「还没动手改闸」那一刻** ★",
     "★**盘面实况 (main 19:1x 实测)**: ① 交卷单骨架已建 `HANDOFF/2026-11-17_sw-lead_ISS298_合法改板通道.md` 2306 B (★B0 + 交付物清单已写, B1~B8 全是「★待填★」★) · "
     "② **闸本体一个字都没改** (`SW/tools/check_onepass_sw_sync.py` mtime = 17:51) ⇒ 仍硬钉板 md5 (★L84-85 ANCHOR_MD5 + L105-107 protected_map() 两行★) · "
     "③ **参考实现已跑通** = `SW/tools/check_demo_panel_spec.py` 的 `check_r6_hard_protected()` (★L522 起★) + `SW/SW_MD5_BASELINE_LEDGER.md` §1 `hard_protected:` 段 (★L54~L65★) "
     "已写好 2 件的 md5 + reboard: null ⇒ ★**照它改, 不许自创一套** ★ · ④ 分片 grep -c iss298 = 0 ★",
     "★**【cont1 续做】重派 (★不是从零做★)★**: 会话 68654eaf 18:30:17 → 18:47:28 · runtime 1026s · status=timeout ⇒ 死在「还没动手改闸」那一刻 ⇒ "
     "★**盘上已有: 交卷单骨架 2306 B (B0 + 交付物清单已写)★ ⇒ ★**本趟只做 3 件**: ① 把 `SW/tools/check_onepass_sw_sync.py` 的「板 / `.kicad_pro` 两件」接到合法改板通道上 "
     "(★照 `check_r6_hard_protected()` 四条判据: ① 基线自证 ② 无变更行⇒纯 md5 硬保护 ③ 有变更行⇒链头唯一/链不断/链头有单号 + 四项原子记录逐字对上 + 基线留链尾 + 盘上==链头 ④ 同组覆盖★) "
     "② 补 ≥4 条沙盒反向用例 ③ 填满交卷单 B1~B8 + 写分片 (grep -c iss298 ≥ 4) ★"),
]

# ★★brief 路径笔误修正 (★`state/check_brief_commands.py` 点出来的★) ★
PATH_FIX = [
    ("state/fragments/hw-lead.yaml", "state/fragments/hw.yaml"),
    ("state/fragments/sw-lead.yaml", "state/fragments/sw.yaml"),
]


def main() -> int:
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        with open(LOG, encoding="utf-8") as f:
            log = yaml.safe_load(f)
        issues = log["issues"]
        by_id = {it["id"]: it for it in issues}

        # ---------- ① brief 路径笔误修正 (只在 task_brief / note 里改, 判据与别的字段一个字不动) ----------
        nfix = 0
        for it in issues:
            tb = it.get("task_brief") or ""
            nt = it.get("note") or ""
            new_tb, new_nt = tb, nt
            for bad, good in PATH_FIX:
                if bad in new_tb:
                    new_tb = new_tb.replace(bad, good)
                    nfix += 1
                if bad in new_nt:
                    new_nt = new_nt.replace(bad, good)
            if new_tb != tb:
                it["task_brief"] = new_tb
            if new_nt != nt:
                it["note"] = new_nt
        print("✔ brief 路径笔误修正: %d 处 (hw-lead.yaml→hw.yaml / sw-lead.yaml→sw.yaml)" % nfix)

        # ---------- ② 三条续做说明追加进 task_brief (status 全程 fixing) ----------
        for iid, owner, fn, heading, why, disk, dl_sum in CONT:
            it = by_id.get(iid)
            if it is None:
                print("⚠ %s 不存在 ⇒ 中止" % iid)
                return 1
            brief_path = os.path.join(HERE, "dispatch_briefs", fn)
            if not os.path.exists(brief_path):
                print("⚠ 缺 brief 文件: %s ⇒ 中止" % brief_path)
                return 1
            with open(brief_path, encoding="utf-8") as f:
                cont_text = f.read()
            tb = it.get("task_brief") or ""
            if heading not in tb:
                it["task_brief"] = tb + "\n\n---\n\n" + cont_text
            it["status"] = "fixing"          # ★★全程 fixing ⇒ 无 open 窗口 ⇒ 兄弟 job 不会重复派★★
            it["dispatched_at"] = TODAY
            it["note"] = (it.get("note") or "") + (
                "\n★★2026-11-17 19:0x 队列自动派活 job (fb67af40) 【%s】重派 (★不是从零重做★) ★★: %s ⇒ %s ⇒ "
                "★**本趟只补盘上缺的那几件, 已做好的不许重做** ★ ⇒ ★**续做任务书全文 = `state/dispatch_briefs/%s`** "
                "(★已过 `python3 state/check_brief_commands.py --brief-file` ⇒ rc=0★) ⇒ ★**status 全程 fixing ⇒ 无 open 窗口 ⇒ "
                "兄弟 job 775d9893 不会重复派** ★" % (heading.split("·")[1].strip(), why, disk, fn))
            print("✅ %s (%s) 续做说明已追加 (status 保持 fixing)" % (iid, owner))

        shutil.copy2(LOG, LOG + ".bak_20261117_1900_cronfb67_cont295_297_298")
        tmp = LOG + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)
        os.replace(tmp, LOG)

        # ---------- ③ 派活日志 ----------
        with open(DL, encoding="utf-8") as f:
            dl = yaml.safe_load(f) or {}
        for iid, owner, fn, heading, why, disk, dl_sum in CONT:
            dl.setdefault("dispatches", []).append({
                "issue": iid,
                "agent": owner,
                "at": TODAY,
                "brief": dl_sum,
                "job": ("★派活方 = cron fb67af40 (ARS45 队列自动派活) 于 19:0x 续做重派 ★ · ★**三个 agent 会话在 18:28~18:47 "
                        "全部超时死掉 ⇒ 三个 `fixing` 全是僵尸 fixing ⇒ 不重派就永远卡死** ★ · ★**status 全程保持 fixing ⇒ "
                        "无 open 窗口 ⇒ 兄弟 job 775d9893 不会重复派** ★ · ★**brief = issue_log 里 %s 的 task_brief "
                        "(★已含本 job 追加的续做节★) ⇒ ★完整续做任务书 = `state/dispatch_briefs/%s` ★" % (iid, fn)),
            })
        tmp_dl = DL + ".tmp"
        with open(tmp_dl, "w", encoding="utf-8") as f:
            yaml.safe_dump(dl, f, allow_unicode=True, sort_keys=False, width=200)
        os.replace(tmp_dl, DL)
        print("✅ dispatch_log 已写 %d 条" % len(CONT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
