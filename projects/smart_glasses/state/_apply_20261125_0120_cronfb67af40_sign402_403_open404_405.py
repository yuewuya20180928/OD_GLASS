#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★_apply_20261125_0120_cronfb67af40_sign402_403_open404_405.py★

★**用途**: cron `fb67af40` (ARS45 队列自动派活) · 2026-11-25 01:2x 一趟
  ① ★**签收** ISS-402 (hw-lead) / ISS-403 (mech-lead) ⇒ status `fixing` → `verified`
     (★main 独立复核 · 不抄任何 agent 报告 · 实跑读数见 VERIFY★)
  ② ★**新开 2 条内部单** (ISS-404 → hw-lead / ISS-405 → mech-lead) 并【直接落 `fixing`】
     (★铁律⑩-i: 先落 fixing 再 spawn ⇒ 兄弟 job `775d9893` 的 `advance.py --json`
       看不见本单 ⇒ 零撞车窗口★)

★**为什么这轮开单 (★本机实读 + 本机实算, 零抄任何 agent 报告★)**:
  · `python3 state/advance.py --json` ⇒ `internal: []` (台账 open 的 owner 全是 boss/main
    ⇒ 不在三个总工可派域)
  · 三个槽位实检: hw-lead `7ed253f7` (ISS-402) done @23:57:43 ·
    mech-lead `fbf81e21` (ISS-403) done @00:59 · sw-lead `d35b8dd2` (ISS-398 cont2) done @22:59
    ⇒ **三条会话全部收工 ⇒ 三个槽位实际都空**
  · ★**但台账里 ISS-402 / ISS-403 仍写 `fixing` ⇒ advance.py 的 in_flight 规则会把这两个 agent
    永远挡在派活之外 ⇒ 队列断线** ⇒ ★**本脚本先做 main 的签收 (把两条落 `verified` ⇒ 释放槽位),
    再开新单** ★
  · ★**本轮的题 (main 本机实测, 逐条可复现)★**:
      ★① **门禁链 `state/gate_check.py` 只挂 18 道闸** (`EXTRA_GATES` 7 + `PINNED_MD5_GATES` 10
         + HW pinout 闸 1) ★**仓内闸脚本共 105 道** (HW 45 / MECH 29 / SW 31) ⇒ **87 道零挂链**
      ★② ★**「板那一趟」的预检清单 `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 点名 12 道闸, 其中 8 道未挂链;
         作业包 `BOARD_ONEPASS_WORKPACKET.md` 点名 18 道, 其中 12 道未挂链; 提交顺序页点名的
         `check_board_frame_caliber.py` 也未挂链** ★ ⇒ 未挂链里最命门的是
         ★**`state/check_pcb_nets.py` (C1 缺失/多余焊盘 · 今天就是红的) 与 `state/check_pcb_drc.py`
         (DRC + C6 生产文件齐)** ★
      ★③ ★**既有覆盖度闸 `HW/check_onepass_preflight_coverage.py` (已挂在钉板闸④) 的 P3 只判
         「清单引用的脚本在本机存在」⇒ 它查存在, 不查挂链** ★ ⇒ **本缺口至今零机器闸覆盖**
      ★④ ★**SW 域已有同款 (ISS-392 `SW/tools/check_sw_gate_chain_coverage.py` + ISS-388
         `SW/tools/check_sw_gate_health.py`) ⇒ HW / MECH 两域至今没有** ★
      ★⑤ ⇒ ISS-404 = HW 域这格; ISS-405 = MECH 域这格 (25 道零挂链, 含 7 道判决链闸 +
         准出汇总闸 `check_onepass_mech_release.py` + ISS-400/403 两道新闸)
         ★**ISS-405 附带一条 already-open need** `iss384_jchg_10p_dims_geometry` (to: mech-lead,
         due 2026-11-26) ★
  · sw-lead 本轮跳过 (★SW 域已有 ISS-392/ISS-388 两道同款覆盖闸 ⇒ 不重复派★)

★**本脚本三道自保**: ① **幂等** (ISS-404/405 已存在 ⇒ 不写盘)
  ② **CAS 守卫** (写前重算 `issue_log.yaml` md5, 与读时不一致 ⇒ rc=3 中止)
  ③ **原子写 + 写后回读自检** (条数 / ISS 在位 / status / 旧条目条数不变 ⇒ 不满足即回滚)

★**零外发 · 零写板 · 零落表 · 零改既有闸 · 零改既有页正文 · 零挂链 · 不写任何 agent 的分片**
"""
import hashlib
import io
import os
import shutil
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
DLOG = os.path.join(HERE, "dispatch_log.yaml")
BRIEFS = os.path.join(HERE, "dispatch_briefs")
BACKUP = os.path.join(HERE, "issue_log.yaml.bak_20261125_0120_cronfb67af40_sign402_403_open404_405")
DLOG_BACKUP = os.path.join(HERE, "dispatch_log.yaml.bak_20261125_0120_cronfb67af40_sign402_403_open404_405")

RUN_ID = "cron_fb67af40_20261125_0120"

# ── ① 签收 (★main 本机实跑读数 · 不抄 agent 报告★) ──
SIGN = {
    "ISS-402": {
        "verify_result": (
            "✅ verified (★main 2026-11-25 01:1x 本机独立复核 · 不抄任何 agent 报告★) ⇒ "
            "★**新闸 `HW/check_generator_value_drift_closed.py` 裸跑 rc=0 (D1~D7 全绿) + "
            "`--selftest` rc=0 · 末行逐字 `ALL TESTS PASS` (正向 1 + 反向 9 = 10 条)** ★ ⇒ "
            "★**「板那一趟」重跑生成器的 26 处 Value 漂移 + `C_VBUS_GND` 掉板机理 ⇒ 已有逐条台账 + "
            "fail-closed 闸** ★ ⇒ ★**板 md5 `611b869e13518c3c023fb178f91a0075` / size 4940213 / "
            "mtime 2026-11-06 07:07:17.362193413 三证逐字节未动 (18 天) + 网表 `6aee500e…` / "
            "脚表 `9174309d…` / BOM `5b999399…` 未变 ⇒ 零写板 · 零落表 · 零挂链 · 零外发** ★ ⇒ "
            "★**交卷页在盘 (61,136 B · 2026-11-24_hw-lead_ISS402_生成器重跑Value漂移26处清账与闸.md) + "
            "`state/fragments/hw.yaml` 已登记 16 处** ★"
        ),
        "fix_ref": (
            "main 2026-11-25 01:1x 独立复核签收 (★零写板·零落表·零改既有闸判据·零改既有页面正文·"
            "零挂链·零外发·未代老板拍板★)"
        ),
        "addendum": (
            "★★2026-11-25 01:1x cron fb67af40 (ARS45 队列自动派活) · main 独立复核签收 "
            "(★追加式·老字一字未删★)★★\n"
            "★本机实跑读数 (★不抄任何 agent 报告★)★: "
            "`python3 HW/check_generator_value_drift_closed.py` ⇒ **rc=0** (D1~D7 全绿) · "
            "`python3 HW/check_generator_value_drift_closed.py --selftest` ⇒ **rc=0** · 末行逐字 "
            "`ALL TESTS PASS` (正向 1 条 + 反向 9 条 = 10 条) · `python3 state/merge.py` ⇒ rc=0 · "
            "`python3 state/gate_check.py` ⇒ rc=0 (全部检查项通过 · 【Q7 钉板 md5 闸链】10/10 道绿) · "
            "`md5sum` 板/网表/脚表/BOM ⇒ `611b869e…` / `6aee500e…` / `9174309d…` / `5b999399…` "
            "(与基线逐字相同) · 板 mtime 2026-11-06 07:07:17.362193413 / size 4940213 (逐字未动)\n"
            "★**签名理由**: ★**「板那一趟」开工前的沉默地雷 (26 处 Value 漂移 + `C_VBUS_GND` 重跑即掉板) "
            "从今天起有逐条台账 + 一道 fail-closed 闸** ⇒ ★**板 md5 全生命周期变更次数 ≤1 这条纪律, "
            "第一次有了机器守卫** ★\n"
            "★**签收后**: ★hw-lead 槽位**已释放** (★台账 status fixing → verified ⇒ advance.py 的 "
            "in_flight 规则不再挡它★) ⇒ 下一轮本 job 可给 hw-lead 派活"
        ),
    },
    "ISS-403": {
        "verify_result": (
            "✅ verified (★main 2026-11-25 01:1x 本机独立复核 · 不抄任何 agent 报告★) ⇒ "
            "★**新闸 `MECH/check_pad_size_coupling_closed.py` 裸跑 rc=0 (8/8 条判据通过) + "
            "`--selftest` rc=0 · 末行逐字 `ALL TESTS PASS` (正向 1 + 反向 14)** ★ ⇒ "
            "★**「焊盘从 1.000 放大 ⇒ MECH 判决链 7 个数全作废 ⇒ 7 道 MECH 闸里 5 道对它完全盲」"
            "这条坏结局, 今天第一次有了逐条台账 + fail-closed 闸** ★ ⇒ ★**板 md5 "
            "`611b869e13518c3c023fb178f91a0075` / size 4940213 / mtime 2026-11-06 07:07:17.362193413 "
            "三证逐字节未动 (18 天) ⇒ 零写板 · 零落表 · 零挂链 · 零外发** ★ ⇒ "
            "★**交卷页在盘 (46,749 B · 2026-11-25_mech-lead_ISS403_焊盘尺寸耦合盲区清账与闸.md) + "
            "`state/fragments/mech.yaml` 已登记 14 处** ★"
        ),
        "fix_ref": (
            "main 2026-11-25 01:1x 独立复核签收 (★零写板·零落表·零改既有闸判据·零改既有页面正文·"
            "零挂链·零外发·未代老板拍板★)"
        ),
        "addendum": (
            "★★2026-11-25 01:1x cron fb67af40 (ARS45 队列自动派活) · main 独立复核签收 "
            "(★追加式·老字一字未删★)★★\n"
            "★本机实跑读数 (★不抄任何 agent 报告★)★: "
            "`python3 MECH/check_pad_size_coupling_closed.py` ⇒ **rc=0** (8/8 条判据通过) · "
            "`python3 MECH/check_pad_size_coupling_closed.py --selftest` ⇒ **rc=0** · 末行逐字 "
            "`ALL TESTS PASS` (反向 14 条 + 正向 1 条) · `python3 state/merge.py` ⇒ rc=0 · "
            "`python3 state/gate_check.py` ⇒ rc=0 (全部检查项通过) · 板/网表/脚表/BOM md5 与基线逐字相同 · "
            "板 mtime/size 未动\n"
            "★**签名理由**: ★**「板只改一次」那趟一旦放大焊盘, 结构侧 7 个数全作废而 5 道闸全盲** ⇒ "
            "★**本单把这条沉默地雷做成台账 + 闸 ⇒ 板 md5 变更次数 ≤1 这条纪律, 结构侧第一次有了机器守卫** ★\n"
            "★**签收后**: ★mech-lead 槽位**已释放** (★台账 status fixing → verified★) ⇒ 下一轮本 job 可给 "
            "mech-lead 派活"
        ),
    },
}

# ── ② 新开两单 ──
NEW = [
    {
        "id": "ISS-404",
        "agent": "hw-lead",
        "brief_rel": "ISS-404_hw_gate_hook_coverage_audit.md",
        "severity": "high",
        "need_keys": [
            "iss404_gate_hook_coverage_ledger",
            "iss404_unhooked_gate_classification",
            "iss404_hook_suggestion_rows",
        ],
        "title": (
            "★★[★新主线·PCB 线·HW 侧·纯查证+纯分析+新建真相页+新建机器闸·零写板·零落表] "
            "「板那一趟」预检清单/作业包点名的闸 ⇒ 【门禁链只挂 18 道 · 仓内 105 道 ⇒ 87 道零挂链】·"
            "其中投板前命门的 `check_pcb_drc.py` / `check_pcb_nets.py` 只活在人工清单里 ⇒ "
            "fail-closed 链不跑它们 ⇒ 漏跑 = 没人知道 (★main 本机实读·逐条可复现★) ★★"
        ),
        "note": (
            "★**2026-11-25 01:2x cron fb67af40 (ARS45 队列自动派活) 新开并【直接落 fixing】** "
            "(★铁律⑩-i: 先落 fixing 再 spawn ⇒ 兄弟 job 775d9893 的 `advance.py --json` 看不见本单 ⇒ "
            "零撞车窗口★)\n"
            "★**开单依据 (本机实读 + 本机实算, 零抄报告)★**: ① `state/advance.py --json` ⇒ internal 0 "
            "(台账 open 的 owner 全是 boss/main ⇒ 不在三个总工可派域); ② 三个槽位会话全部收工 "
            "(hw-lead ISS-402 done @23:57:43 / mech-lead ISS-403 done @00:59 / sw-lead ISS-398 cont2 "
            "done @22:59) ⇒ 槽位实际都空, ★**但台账里 ISS-402/ISS-403 仍写 fixing ⇒ in_flight 规则会把 "
            "这两个 agent 永远挡住 ⇒ 本脚本先签收释放槽位**; ③ ★**本单的题 = 门禁链覆盖率** "
            "(★main 实测: 链上 18 道 / 仓内 105 道 ⇒ 87 道零挂链; 预检清单点名的 12 道闸里 8 道未挂链; "
            "作业包点名的 18 道里 12 道未挂链; 其中 `check_pcb_drc.py` 与 `check_pcb_nets.py` 是投板前命门, "
            "且 `check_pcb_nets.py` 今天就是红的★); ④ ★**既有覆盖度闸 `HW/check_onepass_preflight_coverage.py` "
            "的 P3 只判「脚本存在」不判「挂链」⇒ 这格至今零机器闸覆盖**; ⑤ ★**SW 域已有 ISS-392/ISS-388 两道同款 "
            "⇒ HW/MECH 两域没有** ⇒ 本单补 HW 域那一半, ISS-405 补 MECH 域那一半。\n"
            "★**本单是纯查证/纯分析类** ⇒ 零写板 · 零落表 · 零改既有闸 · 零改既有页正文 · 零挂链 · 零外发 ⇒ "
            "合「板只改一次」纪律 ① ⇒ 真动板那一趟不受本单影响。"
        ),
    },
    {
        "id": "ISS-405",
        "agent": "mech-lead",
        "brief_rel": "ISS-405_mech_gate_hook_coverage_and_jchg10p.md",
        "severity": "high",
        "need_keys": [
            "iss405_mech_gate_hook_coverage_ledger",
            "iss405_mech_mandatory_gate_set",
            "iss405_jchg_10p_geometry_answer",
        ],
        "title": (
            "★★[★新主线·PCB 线·MECH 侧·纯查证+纯分析+新建真相页+新建机器闸·零写板·零落表] "
            "MECH 域 29 道闸 ⇒ 【门禁链只挂 4 道 ⇒ 25 道零挂链】(含 7 道判决链闸 + 准出汇总闸 "
            "`check_onepass_mech_release.py` + ISS-400/403 两道新闸) ⇒ 结构侧护栏整片不在自动链上 "
            "★＋ 附带一条已开的 open need (J_CHG 10p 座体几何 · due 2026-11-26) ★★"
        ),
        "note": (
            "★**2026-11-25 01:2x cron fb67af40 (ARS45 队列自动派活) 新开并【直接落 fixing】** "
            "(★铁律⑩-i: 先落 fixing 再 spawn ⇒ 零撞车窗口★)\n"
            "★**开单依据 (本机实读 + 本机实算, 零抄报告)★**: ① `state/advance.py --json` ⇒ internal 0; "
            "② 三个槽位会话全部收工 ⇒ 槽位实际都空 (★ISS-402/ISS-403 由本脚本先签收释放★); "
            "③ ★**本单的题 = MECH 域闸挂链覆盖率** (★main 实测: MECH 域闸 29 道, 链上只有 4 道 ⇒ 25 道零挂链; "
            "7 道判决链闸 (含 201 条判据的 `check_debug_seat_3d_fit.py`) + 准出汇总闸 "
            "`check_onepass_mech_release.py` + ISS-400/403 两道新闸 全都不在链上 ⇒ 「板那一趟」当天结构侧零自动防线★); "
            "④ ★**附带一条 already-open need** `iss384_jchg_10p_dims_geometry` (to: mech-lead, status open, "
            "due 2026-11-26 · Hirose [FH12] 10p 官网尺寸 A=4.5/B=8.1/C=9.1/D=5.57 [官网]) ⇒ 一并交给本单回, "
            "免得挂在 needs_from 里过期。\n"
            "★**本单是纯查证/纯分析类** ⇒ 零写板 · 零落表 · 零改既有闸 · 零改既有页正文 · 零挂链 · 零外发 ⇒ "
            "合「板只改一次」纪律 ①。"
        ),
    },
]


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def read_yaml(p):
    with io.open(p, encoding="utf-8") as f:
        return yaml.safe_load(f)


def atomic_write(path, text):
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_iss404405_")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def main():
    if not os.path.exists(LOG):
        sys.exit("★issue_log.yaml 不存在 ⇒ 拒绝跑")

    before_md5 = md5(LOG)
    log = read_yaml(LOG)
    issues = log.get("issues") or []
    n_before = len(issues)

    by_id = {it.get("id"): it for it in issues if isinstance(it, dict)}

    # ── 幂等守卫 ──
    for spec in NEW:
        if spec["id"] in by_id:
            sys.stderr.write("★%s 已存在 (status=%s) ⇒ 幂等跳过, 不写盘\n"
                             % (spec["id"], by_id[spec["id"]].get("status")))
            print("IDEMPOTENT_NO_WRITE")
            return 0

    # ── brief 必须先在盘 ──
    briefs = {}
    for spec in NEW:
        bp = os.path.join(BRIEFS, spec["brief_rel"])
        if not os.path.exists(bp):
            sys.exit("★brief 不存在 ⇒ 拒绝跑: %s" % bp)
        with io.open(bp, encoding="utf-8") as f:
            briefs[spec["id"]] = f.read()

    # ── ① 签收 ISS-402 / ISS-403 ──
    signed = []
    for iss_id, rec in SIGN.items():
        it = by_id.get(iss_id)
        if not it:
            sys.stderr.write("★%s 不在台账里 ⇒ 拒绝签收\n" % iss_id)
            return 2
        if it.get("status") == "verified":
            print("★%s 已是 verified ⇒ 跳过签收 (幂等)\n" % iss_id)
            continue
        it["status"] = "verified"
        it["verify_result"] = rec["verify_result"]
        it["verify_date"] = "2026-11-25 01:1x"
        it["fix_ref"] = rec["fix_ref"]
        na = it.get("note_addendum")
        if not isinstance(na, list):
            na = []
        na.append({"at": "2026-11-25 01:1x", "by": "main", "text": rec["addendum"]})
        it["note_addendum"] = na
        signed.append(iss_id)

    # ── ② 新开两单 (直接落 fixing) ──
    for spec in NEW:
        issues.append({
            "id": spec["id"],
            "title": spec["title"],
            "severity": spec["severity"],
            "source_blocker": None,
            "desc": briefs[spec["id"]],
            "owner": spec["agent"],
            "need_keys": spec["need_keys"],
            "task_brief": briefs[spec["id"]],
            "note": spec["note"],
            "source_agent": "main",
            "verify_by": "main",
            "reporter": "main",
            "raised": "2026-11-25",
            "due": "2026-11-27",
            "status": "fixing",
            "external": False,
            "dispatched_at": "2026-11-25",
        })
    log["issues"] = issues

    # ── CAS 守卫 ──
    now_md5 = md5(LOG)
    if now_md5 != before_md5:
        sys.stderr.write("★CAS 守卫命中: issue_log.yaml 在读后被改 (%s → %s) ⇒ 中止, 不写盘\n"
                         % (before_md5, now_md5))
        return 3

    shutil.copy2(LOG, BACKUP)
    text = yaml.safe_dump(log, allow_unicode=True, sort_keys=False, width=100)
    atomic_write(LOG, text)

    # ── 写后回读自检 ──
    chk = read_yaml(LOG)
    chk_issues = chk.get("issues") or []
    ids = [it.get("id") for it in chk_issues]
    problems = []
    if len(chk_issues) != n_before + len(NEW):
        problems.append("条数 %d ≠ 期望 %d" % (len(chk_issues), n_before + len(NEW)))
    for spec in NEW:
        if ids.count(spec["id"]) != 1:
            problems.append("%s 出现 %d 次" % (spec["id"], ids.count(spec["id"])))
        got = [it for it in chk_issues if it.get("id") == spec["id"]]
        if not got or got[0].get("status") != "fixing" or got[0].get("owner") != spec["agent"]:
            problems.append("%s status/owner 不对" % spec["id"])
        if not got or len(str(got[0].get("task_brief") or "")) < 2000:
            problems.append("%s task_brief 没落进去" % spec["id"])
    for iss_id in SIGN:
        got = [it for it in chk_issues if it.get("id") == iss_id]
        if not got or got[0].get("status") != "verified":
            problems.append("%s 未落 verified" % iss_id)
    if problems:
        sys.stderr.write("★写后自检失败: %s ⇒ 回滚\n" % " | ".join(problems))
        shutil.copy2(BACKUP, LOG)
        return 2
    print("ISSUE_LOG_OK: %d → %d 条 | 签收 %s | 新开 %s (status=fixing) | md5 %s → %s"
          % (n_before, len(chk_issues), signed or "(已签)",
             [s["id"] for s in NEW], before_md5, md5(LOG)))

    # ── dispatch_log (追加式) ──
    if os.path.exists(DLOG):
        raw = read_yaml(DLOG)
        dl_list = raw if isinstance(raw, list) else (raw or {}).get("dispatches", [])
        n_dl = len(dl_list)
        entries = [{
            "issue": s["id"],
            "agent": s["agent"],
            "at": "2026-11-25 01:2x",
            "brief": s["brief_rel"],
            "job": ("cron fb67af40 (ARS45 队列自动派活) · ★2026-11-25 01:2x · ★**先落 fixing 再 spawn "
                    "(★铁律⑩-i ⇒ 零撞车窗口★) · ★**命令存在性守卫 "
                    "`python3 state/check_brief_commands.py --brief-file` rc=0** ★ · ★**纯查证/纯分析/"
                    "新建真相页 + 新建机器闸类 (零写板·零落表·零改既有闸·零改既有页正文·零挂链·零外发·不代拍) "
                    "⇒ 合「板只改一次」纪律 ①** ★"),
            "status_note": ("★台账 status 直接落 fixing ⇒ advance.py 的 in_flight 规则继续挡住任何 job 再给该 "
                            "agent 派活 ⇒ 零撞车窗口★"),
            "task_name": "queue_%s" % s["id"].lower(),
            "dispatched_at": "2026-11-25 01:2x",
            "run_id": RUN_ID,
        } for s in NEW]
        shutil.copy2(DLOG, DLOG_BACKUP)
        with io.open(DLOG, "a", encoding="utf-8") as f:
            f.write(yaml.safe_dump(entries, allow_unicode=True, sort_keys=False, width=200))
        chk_dl = read_yaml(DLOG)
        chk_list = chk_dl if isinstance(chk_dl, list) else (chk_dl or {}).get("dispatches", [])
        if len(chk_list) != n_dl + len(entries):
            sys.stderr.write("★dispatch_log 自检失败 ⇒ 回滚\n")
            shutil.copy2(DLOG_BACKUP, DLOG)
            return 2
        print("DISPATCH_LOG_OK: %d → %d 条" % (n_dl, len(chk_list)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
