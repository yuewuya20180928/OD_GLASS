#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
moli (项目总工) 2026-11-18 02:0x · job fb67af40「ARS45 队列自动派活」
★ISS-305 (hw-lead) 僵尸 fixing 重派 cont1 + ISS-306 (sw-lead) 新开并派出
=========================================================================================
★**本 job 本轮实测依据 (★自己查盘 + 读会话, 不抄兄弟 job 的报告★)**:
· ★**ISS-305 = 僵尸 fixing** ★ —— 子会话 `agent:hw-lead:subagent:596715d6`
  (sessionId 76409e80) 01:34:40 → 01:57:20 · runtime 1360 s · status=`failed` · abortedLastRun=false
  ⇒ ★**死在「A~F 判决写到一半、交卷单还没建」那一刻** ⇒ status 卡在 fixing ⇒ hw-lead 整个被挡
  ⇒ ★**但主体【已经做了一半】(main 02:0x 本机实跑盘面核对)**:
    - `logs/iss305/01_placeholder_scan.log` (交付页占位符 0 · ★实测 8,863 B ≠ 任务书写的 6,007 B★)
    - `logs/iss305/02_crosscheck_rk3572_caliber.log` (★交叉核对脚本 rc=0 · 球位号 11/11 逐条 ball 行★)
    - `logs/iss305/03_zero_write_BEFORE/AFTER.log` (★md5 + mtime 前后逐字节一致★)
    - `logs/iss305/04_official_verbatim.log` (★4 条官方逐字带行号★)
    - `logs/iss305/05_gate_regression.log` (★全闸回归·问题闭环门全过·rc=0★)
    - `logs/iss305/06_independent_strict_ball_check.log` (★★关键★★: ① 脚本的「±3 行窗口」判据【不排他】
      ⇒ 同一窗口里躺着 3~7 个候选信号名 ⇒ 「11/11 逐条一致」比它看起来弱 ② 严格同行绑定 11/11=False
      (★因 datasheet 球位表是多列+折行排版★) ③ 严格 token 级绑定只过 1/11 (★唯一过的 = P2 pin45/AM32/CAM_CLK0_OUT_M0★)
      ⇒ ⇒ ★**「球位号 11/11」这条【还没被真判别式证明过】⇒ 这正是 ISS-305 该挑的 over-claim★)
  ⇒ ★**只差 3 件 paperwork: ① 交卷单 (B0~B6 七块) ② A~F 六条逐条判决 ③ 分片 (grep -c iss305 现 = 0)★**
· ★**ISS-306 (sw-lead) = 新开 (★本 job 02:0x 本机实跑测出来的病灶★)**:
  - `python3 state/check_stage_g1a.py` ⇒ ❌ **还差 2 条: G1a-4 (落表已清零) + G1a-8 (关机语义+负载开关已决)**
  - `python3 HW/check_netlist_selfconsistency.py --expect-resolved` ⇒ rc=1 · ★**自己列了 4 条未落表**★:
    ① R3 板封装 U_EN_SW 的 Value 属性还是脚级功能串 ⇒ 板文件也要同趟改
    ② R4 板上仍然没有任何 ESD 位号挂在 D− 那条网 (USB_D_N_SRC / NET_USB_D_N_TYPEC) ⇒ D− 仍然裸奔
    ③ R4 D_ESD_USB_D 仍然只有 2 个焊盘 (D+ + GND) ⇒ 仍不是双通道
    ④ R9 D_ESD_USB_D → J_USB_C 板面距离 = 47.99 mm > 3.0 mm ⇒ ESD 还是不在接口旁边
  - ★**关键矛盾 (★本单第一问★)**: 老板 11-17 09:49 已拍 **A3 架构轴 = V-2 = 1 (2 脚单通道)** ⇒
    ⇒ 判据里「仍不是双通道」这句**期望值**跟老板已拍口径**可能冲突** ⇒ ★**判据过期 还是 真缺口?**
  - ⇒ ★**G1a-8 的代理判据 = ISS-097/ISS-172 status ∈ {verified, closed}; 现状 ISS-097 = `fixed` (owner/verify_by=boss)**
    ⇒ ★**是「等老板验签」还是「代理判据状态集选错」?★**
  - ⇒ ★**本单 = 逐条归类 + 交「板那一趟开工前老板还差 N 个字母」的清单 (★N 必须是具体数字★)★**
· ★**盘面 (★本 job 02:0x 实跑★)**: `state/gate_check.py` rc=0 (★Q1 18/18 · Q7 钉板 md5 闸链 9/9 全绿★) ·
  `MECH/check_onepass_mech_release.py` rc=0 (★绿 6 / 红 0★) ⇒ ★**板那一趟的机器前置已清, 剩下的红全在 G1a 这两条上** ★
· ★**三个总工名额**: hw-lead 被 ISS-305 占 (★僵尸重派★) · sw-lead 空 (★派 ISS-306★) · mech-lead 空且名下无 open 单
  (★MECH 6 道闸全绿 ⇒ ★**没有可派的红闸·不硬造活**★) ★
★**铁律**: 干活的人不许自签 ⇒ verify_by=main
★**不碰**: 任何真源文件 / 任何分片 / 板 / 网表 / 脚表 / BOM / 落表台账 / 决策页 / outbox / 兄弟 job 的任何单
★**纪律**: ISS-305 全程 fixing ⇒ 中间不留 open 窗口 ⇒ 兄弟 job 775d9893 不会撞车
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

ISS305_CONT1_FILE = "state/dispatch_briefs/ISS-305_hw_verify_iss131_cont1.md"
ISS306_FILE = "state/dispatch_briefs/ISS-306_sw_g1a_reds_rootcause.md"

ISS305_NOTE = (
    "★**cont1 续做 (★2026-11-18 02:0x · cron fb67af40 重派僵尸 fixing★)** ★**依据 = main 02:0x 本机实跑盘面 + 读子会话 transcript★** "
    "⇒ ★**上一趟子会话 `agent:hw-lead:subagent:596715d6` (sessionId 76409e80) 01:34:40 → 01:57:20 · runtime 1360s · "
    "status=failed · abortedLastRun=false ⇒ 死在「A~F 判决写到一半、交卷单还没建」那一刻★** ⇒ ★**僵尸 fixing ⇒ hw-lead 被挡★** "
    "⇒ ★**主体【已做一半】(logs/iss305/ 01~06 六份日志全在盘) ⇒ 本轮只派【3 件 paperwork: ① 交卷单 B0~B6 七块填实 "
    "(grep -cE \"🔄 待填\" 必须 = 0) ② A~F 六条逐条判决 (★对/不对/有条件 + 依据 + 行号★) ③ 分片 hw.yaml (grep -c iss305 ≥ 5)】★** "
    "⇒ ★**★但 §2 才是本单真正的价值: `logs/iss305/06_independent_strict_ball_check.log` 实测 ⇒ 复验脚本用的「±3 行窗口」判据"
    "【不排他】(同一窗口里躺着 3~7 个候选信号名 ⇒ 换成相邻球位的信号名也会被判通过) ⇒ 且 datasheet 球位表是多列+折行排版 ⇒ "
    "「严格同行绑定」11/11=False、「严格 token 级绑定」只过 1/11 ⇒ ⇒ 「球位号 11/11 与官方逐条对上」这条【还没被真判别式证明过】★** "
    "⇒ ★**本轮要求 hw-lead 建【真判别式 (ball → 该球位全部 pin 名集合) 解析】并用它把 11 条重判一遍 ⇒ 这是本单要挑的 over-claim★** "
    "⇒ ★**零写板 · 零落表 · 零改闸 (★`state/_iss131_crosscheck_rk3572_caliber.py` 是被复验对象, 不许改★) · 零外发 · 不自签 issue_log** ★"
)

ISS306 = {
    "id": "ISS-306",
    "title": (
        "★★[主线内·开工前置·溯源类·内部活] ★★【板那一趟开工前置: G1a 剩下两条红 (G1a-4 落表未清零 + G1a-8 关机语义已决) "
        "到底卡在老板身上 还是 卡在过期判据身上?】★★ ⇒ ★**本单 = 把这 2 条红逐条归类 (R3/R4×2/R9 + ISS-097 代理判据) "
        "+ 交一份「板那一趟开工前老板还差 N 个字母 (N 必须是具体数字) + 每条卡在哪一步 + 不拍的后果」的清单★★ "
        "⇒ 纯分析/溯源 · 零写板 · 零落表 · 零改闸 · 零外发 · 不替老板拍板** ★"
    ),
    "severity": "high",
    "owner": "sw-lead",
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
        "★**2026-11-18 02:0x · cron fb67af40 (ARS45 队列自动派活) 新开并直接派出 (★status 直接落 fixing ⇒ 兄弟 job 775d9893 "
        "的 advance.py 看不见 open 窗口 ⇒ 不会重复派同一个 agent★)** ★ ⇒ ★**依据 = main 02:0x 本机实跑 (不抄任何 agent 报告)★** "
        "⇒ `python3 state/check_stage_g1a.py` ⇒ ❌ **还差 2 条: G1a-4 (落表已清零·翻面口径) + G1a-8 (关机语义+负载开关已决)**** "
        "⇒ `python3 HW/check_netlist_selfconsistency.py --expect-resolved` ⇒ rc=1 · ★**它自己列了 4 条未落表**★: "
        "① **R3** 板封装 U_EN_SW 的 Value 属性还是脚级功能串 ⇒ 板文件也要同趟改 · "
        "② **R4** 板上仍然没有任何 ESD 位号挂在 D− 那条网 (USB_D_N_SRC / NET_USB_D_N_TYPEC) ⇒ **D− 仍然裸奔** · "
        "③ **R4** D_ESD_USB_D 仍然只有 2 个焊盘 (D+ + GND) ⇒ **仍不是双通道** · "
        "④ **R9** D_ESD_USB_D → J_USB_C 板面距离 = 47.99 mm > 3.0 mm ⇒ ESD 还是不在接口旁边 ★ "
        "⇒ ★**★第一问 (本单最要紧)**: 老板 11-17 09:49 已把 **A3 架构轴拍成 V-2 = 1 (2 脚单通道)** ⇒ "
        "⇒ 判据里「仍不是双通道」那句**期望值**与老板已拍口径**可能冲突** ⇒ ★**是判据过期 还是 真缺口?** (★两者都有也要分开写清★) ★ "
        "⇒ ★**第二问**: G1a-8 的代理判据 = ISS-097/ISS-172 status ∈ {verified, closed}; 现状 **ISS-097 = `fixed`** "
        "(owner=boss · verify_by=boss · 产物 `HW/POWER_SHUTDOWN_V3.md` 20,677 B 在盘 · mtime 2026-11-17 23:17) ⇒ "
        "★**是「等老板验签」(按 11-12 02:02 口径不许外发, 只能催拍) 还是「代理判据的状态集选错了」?** ★ "
        "⇒ ★**★本单唯一目标 = 交出「板那一趟开工前, 老板还差 N 个字母 (N 必须是具体数字) + 每条卡在哪一步 + 不拍的后果」的清单** ★ "
        "⇒ ★**盘面 (main 02:0x 实跑)**: `state/gate_check.py` rc=0 (★Q1 18/18 · Q7 钉板 md5 闸链 **9/9 全绿**★) · "
        "`MECH/check_onepass_mech_release.py` rc=0 (★绿 6/红 0★) ⇒ ★**板那一趟的机器前置已清, 剩下的红全压在这两条 G1a 上** ★ "
        "⇒ ★**★若结论是「N = 0」⇒ 那是本单最有价值的结论, 不许为了凑数硬找卡点**★ ★"
    ),
    "task_brief": None,
}


def read(rel):
    with open(os.path.join(PROJ, rel), encoding="utf-8") as f:
        return f.read()


def main() -> int:
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        with open(LOG, encoding="utf-8") as f:
            log = yaml.safe_load(f)
        issues = log["issues"]
        by_id = {it["id"]: it for it in issues}

        # ---------------- ① ISS-305 · fixing → open → fixing (原子) + cont1 ----------------
        it305 = by_id.get("ISS-305")
        if it305 is None:
            print("⚠ ISS-305 不存在 ⇒ 中止")
            return 1
        if it305.get("status") != "fixing":
            print("⚠ ISS-305 status=%s (不是 fixing) ⇒ 幂等跳过" % it305.get("status"))
        else:
            cont1 = read(ISS305_CONT1_FILE)
            it305["status"] = "open"
            it305["status"] = "fixing"
            it305["dispatched_at"] = TODAY
            it305["note"] = (it305.get("note") or "") + "\n\n★" + ISS305_NOTE
            it305["task_brief"] = (it305.get("task_brief") or "") + "\n\n\n" + ("=" * 78) + "\n\n" + cont1
            print("✅ ISS-305: fixing→open→fixing 原子完成 + cont1 续做说明已并入 task_brief (原 brief 保留)")

        # ---------------- ② ISS-306 新开 (owner=sw-lead · 直接落 fixing = 立即派出) ----------------
        if "ISS-306" in by_id:
            print("ℹ ISS-306 已存在 ⇒ 幂等跳过 (不重复开单)")
        else:
            ISS306["task_brief"] = read(ISS306_FILE)
            issues.append(ISS306)
            print("✅ ISS-306 新开 (owner=sw-lead · status=fixing ⇒ 直接派出)")

        shutil.copy2(LOG, LOG + ".bak_20261118_0210_cronfb67_iss305cont1_iss306")
        tmp = LOG + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)
        os.replace(tmp, LOG)

        # ---------------- 派活日志 ----------------
        with open(DL, encoding="utf-8") as f:
            dl = yaml.safe_load(f) or {}
        disp = dl.setdefault("dispatches", [])
        disp.append({
            "issue": "ISS-305",
            "agent": "hw-lead",
            "at": TODAY,
            "brief": (
                "★派活方 = cron fb67af40 (ARS45 队列自动派活) 于 02:0x · ★**僵尸 fixing 重派 = cont1 续做 (★不是从零重做★)** ★ · "
                "★**依据 = main 02:0x 本机实跑盘面 + 读子会话 transcript (不抄任何 agent 报告)** ★ · ★**上一趟 status=failed "
                "⇒ 主体已做一半 (logs/iss305/ 01~06 全在) ⇒ 只差 3 件 paperwork + 「球位号 11/11」的真判别式重判** ★ · "
                "★**status 全程 fixing ⇒ 无 open 窗口 ⇒ 兄弟 job 775d9893 不会重复派** ★ · ★**brief = issue_log 里 ISS-305 的 "
                "task_brief (★= 原任务书全文 + `%s` 全文·已过命令存在性闸 `python3 state/check_brief_commands.py --brief-file` "
                "⇒ rc=0★)** ★" % ISS305_CONT1_FILE
            ),
            "note": ISS305_NOTE,
        })
        disp.append({
            "issue": "ISS-306",
            "agent": "sw-lead",
            "at": TODAY,
            "brief": (
                "★派活方 = cron fb67af40 (ARS45 队列自动派活) 于 02:0x · ★**新开单 + 直接派出 (status 直接落 fixing ⇒ "
                "兄弟 job 看不见 open 窗口)** ★ · ★**依据 = main 02:0x 本机实跑 (`state/check_stage_g1a.py` 2 条红 + "
                "`HW/check_netlist_selfconsistency.py --expect-resolved` 4 条未落表 + `state/gate_check.py` rc=0 Q7 9/9 + "
                "`MECH/check_onepass_mech_release.py` rc=0)★** ★ · ★**brief = `%s` 全文 · 已过命令存在性闸 ⇒ rc=0** ★" % ISS306_FILE
            ),
            "note": ISS306["note"],
        })
        tmp_dl = DL + ".tmp"
        with open(tmp_dl, "w", encoding="utf-8") as f:
            yaml.safe_dump(dl, f, allow_unicode=True, sort_keys=False, width=200)
        os.replace(tmp_dl, DL)
        print("✅ dispatch_log 已写 2 条")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
