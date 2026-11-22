#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
moli (项目总工) 2026-11-18 01:1x · job fb67af40「ARS45 队列自动派活」
★ISS-302 (hw-lead) 僵尸 fixing 重派 cont1 + ISS-300 (mech-lead) main 验签 + ISS-303/ISS-304 新开单★
=========================================================================================
★**本 job 本轮实测依据 (★自己查盘 + 读会话, 不抄兄弟 job 的报告★)**:
· ★**ISS-302 = 僵尸 fixing** ★ —— 子会话 `agent:hw-lead:subagent:ae23ed17` (sessionId c3e684e9)
  00:16:54 → **00:26:26** · runtime 568 s · status=timeout · abortedLastRun=true
  ⇒ ★**死在「交卷单刚建好 778 B 骨架、还没填」那一刻** ⇒ status 卡在 fixing ⇒ ★**hw-lead 整个被挡** ★
· ★**但主体【已经做完了】(main 00:4x~00:5x 本机实跑)**:
  - `state/_apply_iss302_csys_landing.py` (11,811 B · mtime 00:21) ★
  - 网表 L498/L499/L500 三行 DNP→必装 + 追加式订正 (★老字逐字留痕 + PM 老裁决标已作废 +
    换成 TI bq25896 SLUSC76C §7 逐字『Connect a 20uF closely to the SYS pin.』★)
  - BOM `HW/BOM_v1.csv` L48 = `C_SYS` · 1 · 20µF X7R 6.3V · 必装
  - 三件产物 00:21:08 重生成: 网表 37f62ac3→6aee500e / 脚表 a4270120→9174309d / BOM 5d02bce→5b999399
  - 落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` §19 (L1437 起) + `<!--ISS302_ROWS-->` L1451~L1455
  - ★**板零变化**: `HW/PCB/demo_mainboard.kicad_pcb` = 611b869e… · mtime 仍 2026-11-06 07:07:17.362193413 ★
  ⇒ ★**只差 paperwork: 交卷单 778 B 骨架 (7 个块全是「(待填)」) + 分片 `grep -c iss302` = 0 + 闸复跑 rc 没落盘** ★
· ★**ISS-300 (mech-lead) = 已交卷, 等 main 签字** ★ —— 会话 `agent:mech-lead:subagent:9fc3d633`
  (sessionId 273ed919) 22:35:09 → 22:43:50 · status=done ⇒ ★**不是僵尸, 是【待验签】** ★
  ⇒ 交卷单 25,996 B · `grep -cE "🔄|待填"` = 0 · B0+B1~B6 六块齐全 · 分片 `grep -c iss300` = 12
  ⇒ ★**main 验签口径要诚实**: ★**22:4x 交付时 `MECH/check_onepass_mech_release.py` rc=0 (绿 6/红 0)** ★
  ⇒ ★**但 00:21 ISS-302 合法落表后, 该汇总闸现在 rc=1 (红的那道 = MECH 侧 N6 判据只认硬基线)**
  ⇒ ⇒ ★**这不推翻 ISS-300 的交付物 (汇总闸本体 + 交卷单 + 分片 都齐), 但必须把「现在红」如实记进验签 note
    + 另开 ISS-303 去修那个洞** ★
· ★**★本 job 00:5x 实跑 18 道闸 (原样 rc, 全在 /tmp/gate_sweep_iss302.log)**:
  - ★**红的 4 道**: ① `HW/check_pin_function_labels.py` rc=1 (★15 条既有缺陷基线 · md5 那段 ✔ ⇒ **不许动**★)
    ② `HW/check_workpack_state_values.py` rc=1 (★4 条 md5 现值漂 ⇒ **ISS-304**★)
    ③ `MECH/check_onepass_struct_crosscheck.py` rc=1 (★N6 受保护件被改 3 条 ⇒ **ISS-303**★)
    ④ `MECH/check_onepass_mech_release.py` rc=1 (★汇总 绿5/红1 = 上面第 ③ 道⇒ **ISS-303**★)
    ⑤ `state/gate_check.py` rc=1 (★Q1 18/18 ✔ · **Q7 钉板 md5 闸链 8/9** ⇒ 红的是「钉板闸⑥ 作业包现状值闸」⇒ **ISS-304**★)
  - 其余 13 道全绿 (含 `HW/check_onepass_preflight_coverage.py` / `SW/tools/check_demo_panel_spec.py` /
    `SW/tools/timing_check.py` / `SW/tools/check_onepass_sw_sync.py` / `MECH/check_mech_verdict_freshness.py` 等)
  ⇒ ★**⇒ 「板只改一次」那一趟现在被这 2 个洞挡住 (ISS-303 / ISS-304) ⇒ 本 job 必须把这两个单开出来** ★
· ★**盘面 ≠ 名单 (★老坑★)**: ★**本 job 的 `advance.py --json` 此刻 `internal: []`**
  ⇒ ★**17 条 open 全是 owner=boss(6) / owner=main(11); 三个总工名下唯一能动的两条都在 fixing** ★
· ★**处置**:
  - ISS-302: fixing → open → fixing ★**同一个锁内原子完成** ⇒ ★**中间不留 open 窗口 ⇒ 兄弟 job 775d9893 不会撞车** ★
  - ISS-300: ★**main 验签 (fixing → verified)· 带诚实 note (现在红的那道已另开 ISS-303)** ★
  - ISS-303: ★**新开单 (owner=mech-lead · 直接落 fixing ⇒ 兄弟 job 的 advance.py 看不见 open)** ★
  - ISS-304: ★**新开单 (owner=hw-lead · status=open ⇒ 排队等 hw-lead 名额: ISS-302 cont1 交卷后才派)** ★
★**铁律**: 干活的人不许自签 ⇒ verify_by=main
★**不碰**: 任何真源文件 / 任何分片 / 板 / 网表 / 脚表 / BOM / 落表台账 / 决策页 / outbox / 兄弟 job 的任何单
"""
import fcntl
import os
import shutil

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
LOG = os.path.join(HERE, "issue_log.yaml")
DL = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
TODAY = "2026-11-18"

# ---------------------------------------------------------------- ISS-302 cont1
ISS302_CONT1_FILE = "state/dispatch_briefs/ISS-302_hw_c_sys_landing_cont1.md"
ISS302_NOTE = (
    "★**cont1 续做 (★2026-11-18 01:1x · cron fb67af40 重派僵尸 fixing★)** ★**依据 = main 00:4x~00:5x 本机实跑★** "
    "⇒ ★**上一趟子会话 `agent:hw-lead:subagent:ae23ed17` (sessionId c3e684e9) 00:16:54 → 00:26:26 · runtime 568s · "
    "status=timeout / abortedLastRun=true ⇒ 死在「交卷单刚建 778 B 骨架、还没填」那一刻★** ⇒ ★**僵尸 fixing ⇒ hw-lead 被挡★** "
    "⇒ ★**主体【已做完】(落表脚本 11,811 B · 网表 L498/L499/L500 DNP→必装 + 追加式订正 · BOM L48 C_SYS 必装 20µF · "
    "三件产物 00:21:08 重生成 37f62ac3→6aee500e / a4270120→9174309d / 5d02bece→5b999399 · 台账 §19 + ISS302_ROWS L1451~L1455 · "
    "板 611b869e… mtime 仍 2026-11-06 07:07:17) ⇒ 本轮只派【3 件 paperwork: ① 交卷单 7 个块填实 (grep -cE '🔄|待填' 必须 = 0) "
    "② 分片 hw.yaml 写 claim/answer/artifact (grep -c iss302 目标 ≥ 5) ③ 闸复跑原样 rc 落 logs/iss302/ 并贴进 B4】★** "
    "⇒ ★**落表已完成 ⇒ 本单是收尾单: 网表/脚表/BOM/台账/p10_rows.json 一个字节不许再动 (★再跑生成器也不行★) · "
    "板零变化 · 零外发** ★ ⇒ ★**另外 4 道红闸不许在本单里改判据去消红 (HW/check_pin_function_labels.py = 既有缺陷基线不许动 · "
    "HW/check_workpack_state_values.py = ISS-304 · MECH/check_onepass_struct_crosscheck.py + MECH/check_onepass_mech_release.py = ISS-303)★** "
    "★ ⇒ ★**真判据是 `grep -cE \"🔄|待填\"` 必须 = 0 (★`state/check_report_placeholders.py` 抓不到这种形态★)** ★"
)

# ---------------------------------------------------------------- ISS-303 新开
ISS303_FILE = "state/dispatch_briefs/ISS-303_mech_n6_ledger_jump.md"
ISS303 = {
    "id": "ISS-303",
    "title": (
        "★★[主线内·MECH 侧·闸机制类·内部活] ★★【MECH 侧 N6 只认【硬基线】不认【合法落表跳】⇒ 00:21 ISS-302 合法落表一次 ⇒ "
        "MECH 侧准出汇总闸当场转红 ⇒ 「板只改一次」那一趟的结构侧准出被一个假红挡住 ⇒ 现场极可能误读成「板改坏了」】★★ "
        "⇒ ★**本单 = 把 N6 的判决源从【硬基线常量】换成【硬基线 ∪ 落表台账登记值】(★只读台账, 不许把新 md5 写死★) + "
        "fail-closed 三条不许动 + 反向用例 ≥ 5 条 (★纯 MECH 侧·零写板·零落表·零改网表★)** ★"
    ),
    "severity": "high",
    "owner": "mech-lead",
    "reporter": "main",
    "raised": TODAY,
    "due": "2026-11-20",
    "status": "fixing",
    "external": False,
    "need_keys": [],
    "fix_ref": None,
    "verify_by": "main",
    "verify_result": None,
    "verify_date": None,
    "dispatched_at": TODAY,
    "note": (
        "★**2026-11-18 01:1x · cron fb67af40 (ARS45 队列自动派活) 新开并直接派出 (★status 直接落 fixing ⇒ 兄弟 job 775d9893 "
        "的 advance.py 看不见 open 窗口 ⇒ 不会重复派同一个 agent★)** ★ ⇒ ★**依据 = main 00:5x 本机实跑 18 道闸★** "
        "⇒ `MECH/check_onepass_struct_crosscheck.py` rc=1 · ★**N6 受保护件被改 3 条**★ (网表 37f62ac3→6aee500e / "
        "脚表 a4270120→9174309d / BOM 5d02bece→5b999399 ★**全是 ISS-302 的合法落表★**) ⇒ "
        "`MECH/check_onepass_mech_release.py` rc=1 (★汇总 绿5/红1, 红的那道就是它★) ⇒ ★**板那一趟的结构侧准出被挡住**★ "
        "⇒ ★**根因**: 该闸 `PROTECTED_LEDGER_MD5` (L66~L67) 是 ISS-290 任务书的硬基线常量 ⇒ 分不出「合法落表」与「有人手改」★ "
        "⇒ ★**口径 = HW 侧已跑通的那套 (HW/check_workpack_state_values.py 的 V6 段: 盘上 md5 == 落表台账登记 ⇒ 未被绕过改动)** ★ "
        "⇒ ★**本单不许放宽判据方向 / 不许动 fail-closed 三条 / 不许动 ISS-296 已接好的合法改板通道 / 不许改 HW·SW 任何文件** ★"
    ),
    "task_brief": None,   # ★下面从 brief 文件读入★
}

# ---------------------------------------------------------------- ISS-304 新开
ISS304_FILE = "state/dispatch_briefs/ISS-304_hw_workpack_state_values_reanchor.md"
ISS304 = {
    "id": "ISS-304",
    "title": (
        "★★[主线内·HW 侧·现状值重锚类·内部活] ★★【钉板闸⑥ 作业包现状值闸: 00:21 ISS-302 合法落表一次 ⇒ 页面里那 4 条 md5 现值没跟上 "
        "⇒ Q7 钉板 md5 闸链 8/9 ⇒ 「板只改一次」那一趟不许开工】★★ ⇒ ★**本单 = 让那 4 条 `fresh` 原句跟上盘面 + 幂等不许破 "
        "(★重跑生成器 ⇒ 页 md5 相同★) + 口径「走落表台账为准, 不写死」(★ISS-283 ⑩-b 早就定过★) · 纯文档/闸侧 · 零写板 · 零落表** ★"
    ),
    "severity": "high",
    "owner": "hw-lead",
    "reporter": "main",
    "raised": TODAY,
    "due": "2026-11-20",
    "status": "open",
    "external": False,
    "need_keys": [],
    "fix_ref": None,
    "verify_by": "main",
    "verify_result": None,
    "verify_date": None,
    "dispatched_at": None,
    "note": (
        "★**2026-11-18 01:1x · cron fb67af40 (ARS45 队列自动派活) 新开 · status=open 排队 (★hw-lead 名额被 ISS-302 cont1 占着 ⇒ "
        "下一轮 hw-lead 空出来就派★)** ★ ⇒ ★**依据 = main 00:5x 本机实跑★** ⇒ `HW/check_workpack_state_values.py` rc=1 · "
        "★**V4 现状值==盘面实测 4 条红**★ (W10_MD5_NETLIST / W10B_MD5_PINS / W10C_MD5_BOM / C07_B26_MD5_LEDGER) ⇒ "
        "`state/gate_check.py` rc=1 · ★**Q7 钉板 md5 闸链 8/9 绿 ⇒ 板那一趟不许开工**★ ⇒ ★**根因 = 两份页面里那 4 条 `fresh` 原句 "
        "停在 ISS-283 那一跳 (37f62ac3 / a4270120 / 5d02bece) ⇒ 而 sidecar `state/_iss277_preflight_appendix.md` 里也是同一批旧值** ★ "
        "⇒ ★**那 4 条自己的 note 就写着「基线走落表台账为准, 不写死」⇒ 口径早就定过, 只是链没跟上** ★ "
        "⇒ ★**不许改闸的判定逻辑 (它是钉板闸⑥) · 不许手改生成器产物 (清单页是 `state/_iss277_build_preflight.py` 的产物) · "
        "老字 29 条 anchor 逐字不许删 (V2 追加式自证)** ★"
    ),
    "task_brief": None,
}


def read(path):
    with open(os.path.join(PROJ, path), encoding="utf-8") as f:
        return f.read()


def main() -> int:
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        with open(LOG, encoding="utf-8") as f:
            log = yaml.safe_load(f)
        issues = log["issues"]
        by_id = {it["id"]: it for it in issues}

        # ---------------- ① ISS-300 · main 验签 (幂等) ----------------
        it300 = by_id.get("ISS-300")
        if it300 is None:
            print("⚠ ISS-300 不存在 ⇒ 中止")
            return 1
        if it300.get("status") == "fixing":
            it300["status"] = "verified"
            it300["fix_ref"] = (
                "HANDOFF/2026-11-17_mech-lead_ISS300_结构侧准出汇总闸.md (25,996 B · B0+B1~B6 六块齐全 · "
                "grep -cE '🔄|待填' = 0) · MECH/check_onepass_mech_release.py (21,227 B · 汇总闸本体) · "
                "state/fragments/mech.yaml (grep -c iss300 = 12)"
            )
            it300["verify_by"] = "main"
            it300["verify_result"] = "pass"
            it300["verify_date"] = TODAY
            it300["note"] = (it300.get("note") or "") + (
                "\n\n★**main 2026-11-18 01:1x 验签 (cron fb67af40 本机实跑, 不抄 agent 报告)** ★"
                "⇒ ★**交付物验收通过**: 交卷单 25,996 B · `grep -cE \"🔄|待填\"` = 0 · B0 + B1~B6 六块齐全 · "
                "分片 `grep -c iss300` = 12 (claims 5 / needs 2 / artifacts 3 / status delivered·100·绿)★ "
                "⇒ ★**交付时刻 (22:4x) `MECH/check_onepass_mech_release.py` rc=0 (绿 6 / 红 0) + `--selftest` rc=0 + `--json` ok=True n_green=6** ★"
                "⇒ ★**★但 2026-11-18 00:21 ISS-302 合法落表后, 该汇总闸【现在】rc=1 (绿 5 / 红 1) ⇒ 红的那道 = "
                "`MECH/check_onepass_struct_crosscheck.py` 的 N6 (它只认硬基线, 不认合法落表跳)★ ⇒ "
                "★**这不是 ISS-300 的交付物缺陷 (汇总闸本体没问题) ⇒ 已另开 ISS-303 (mech-lead) 去修那个洞** ★ ⇒ "
                "★**板那一趟开工前必须先看 MECH 汇总闸 rc=0 ⇒ ISS-303 交卷并回绿才算数** ★ ⇒ "
                "★**验签不等于「结构侧现在就能出 Gerber」★**"
            )
            print("✅ ISS-300: fixing → verified (main 验签 · 带「现在红 ⇒ 归 ISS-303」的诚实 note)")
        else:
            print("ℹ ISS-300 status=%s ⇒ 幂等跳过 (不重复落账)" % it300.get("status"))

        # ---------------- ② ISS-302 · fixing → open → fixing (原子) + cont1 ----------------
        it302 = by_id.get("ISS-302")
        if it302 is None:
            print("⚠ ISS-302 不存在 ⇒ 中止")
            return 1
        if it302.get("status") != "fixing":
            print("⚠ ISS-302 status=%s (不是 fixing) ⇒ 幂等跳过" % it302.get("status"))
        else:
            cont1 = read(ISS302_CONT1_FILE)
            it302["status"] = "open"
            it302["status"] = "fixing"
            it302["dispatched_at"] = TODAY
            it302["note"] = (it302.get("note") or "") + "\n\n★" + ISS302_NOTE
            it302["task_brief"] = (it302.get("task_brief") or "") + "\n\n\n" + ("=" * 78) + "\n\n" + cont1
            print("✅ ISS-302: fixing→open→fixing 原子完成 + cont1 续做说明已并入 task_brief")

        # ---------------- ③ ISS-303 新开 (直接落 fixing) ----------------
        if "ISS-303" in by_id:
            print("ℹ ISS-303 已存在 ⇒ 幂等跳过 (不重复开单)")
        else:
            ISS303["task_brief"] = read(ISS303_FILE)
            issues.append(ISS303)
            print("✅ ISS-303 新开 (owner=mech-lead · status=fixing ⇒ 直接派出)")

        # ---------------- ④ ISS-304 新开 (status=open 排队) ----------------
        if "ISS-304" in by_id:
            print("ℹ ISS-304 已存在 ⇒ 幂等跳过 (不重复开单)")
        else:
            ISS304["task_brief"] = read(ISS304_FILE)
            issues.append(ISS304)
            print("✅ ISS-304 新开 (owner=hw-lead · status=open ⇒ 排队等 hw-lead 名额)")

        shutil.copy2(LOG, LOG + ".bak_20261118_0110_cronfb67_zombie302_verify300_open303_304")
        tmp = LOG + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)
        os.replace(tmp, LOG)

        # ---------------- 派活日志 ----------------
        with open(DL, encoding="utf-8") as f:
            dl = yaml.safe_load(f) or {}
        disp = dl.setdefault("dispatches", [])
        disp.append({
            "issue": "ISS-302",
            "agent": "hw-lead",
            "at": TODAY,
            "brief": (
                "★派活方 = cron fb67af40 (ARS45 队列自动派活) 于 01:1x · ★**僵尸 fixing 重派 = cont1 续做 (★不是从零重做★)** ★ · "
                "★**依据 = main 00:4x~00:5x 本机实跑 (不抄任何 agent 报告)** ★ · ★**上一趟子会话被掐 (status=timeout / "
                "abortedLastRun=true) ⇒ 主体已做完, 只差 paperwork** ★ · ★**status 全程 fixing ⇒ 无 open 窗口 ⇒ "
                "兄弟 job 775d9893 不会重复派** ★ · ★**brief = issue_log 里 ISS-302 的 task_brief (★= 原任务书全文 + "
                "`%s` 全文·已过命令存在性闸 `python3 state/check_brief_commands.py --brief-file` ⇒ rc=0★)** ★" % ISS302_CONT1_FILE
            ),
            "note": ISS302_NOTE,
        })
        disp.append({
            "issue": "ISS-303",
            "agent": "mech-lead",
            "at": TODAY,
            "brief": (
                "★派活方 = cron fb67af40 (ARS45 队列自动派活) 于 01:1x · ★**新开单** ★ · ★**依据 = main 00:5x 本机实跑 18 道闸 "
                "(原样 rc 在 /tmp/gate_sweep_iss302.log)** ★ · ★**status 直接落 fixing ⇒ 兄弟 job 看不见 open 窗口** ★ · "
                "★**brief = `%s` 全文 · 已过命令存在性闸 ⇒ rc=0** ★" % ISS303_FILE
            ),
            "note": ISS303["note"],
        })
        disp.append({
            "issue": "ISS-304",
            "agent": "hw-lead",
            "at": TODAY,
            "brief": (
                "★派活方 = cron fb67af40 (ARS45 队列自动派活) 于 01:1x · ★**新开单 · status=open 排队 (★hw-lead 名额被 ISS-302 "
                "cont1 占着 ⇒ 下一轮空出来就派·advance.py 的 in_flight 规则会自动挡住, 不会重复派)** ★ · "
                "★**brief = `%s` 全文 · 已过命令存在性闸 ⇒ rc=0** ★" % ISS304_FILE
            ),
            "note": ISS304["note"],
        })
        disp.append({
            "issue": "ISS-300",
            "agent": "mech-lead",
            "at": TODAY,
            "brief": (
                "★**main 验签 (verify_by=main) 于 01:1x** ★ ⇒ fixing → verified ⇒ ★**诚实 note: 交付时 (22:4x) 汇总闸 rc=0 全绿, "
                "但 00:21 ISS-302 合法落表后 MECH 侧 N6 转红 ⇒ 汇总闸现在 rc=1 ⇒ ★**已另开 ISS-303 跟** ⇒ "
                "★**验签 ≠ 结构侧现在就能出 Gerber** ★"
            ),
            "note": "★main 验签 (本机实跑: 交卷单 25,996 B · 占位符 0 · 分片 12 条 · 交付时 rc=0/绿6)★",
        })
        tmp_dl = DL + ".tmp"
        with open(tmp_dl, "w", encoding="utf-8") as f:
            yaml.safe_dump(dl, f, allow_unicode=True, sort_keys=False, width=200)
        os.replace(tmp_dl, DL)
        print("✅ dispatch_log 已写 4 条")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
