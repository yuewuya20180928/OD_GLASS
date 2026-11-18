#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★ISS-309 (sw-lead) 僵尸 fixing 续做重派 cont1 + ISS-310 (mech-lead) 新开直接派出
   · cron fb67af40 (ARS45 队列自动派活) · 2026-11-18 05:3x★

★**为什么有本脚本** (★main 05:3x 本机实跑, 不抄任何 agent 报告★):
  · 兄弟 job fb67af40 于 04:5x 派出 ISS-309 (taskName `queue_iss309`)
  · 该子会话 `agent:sw-lead:subagent:4f1fbe6b` 于 05:05:48 死:
      status=timeout · abortedLastRun=true · runtimeMs=624507
  · ⇒ ★**根因 = 父 run 结束时子会话被连带 abort (★与 ISS-308 第一趟同一个死法★)**
  · ★**0 件交付物落地** (★交卷单不存在 · `grep -c iss309 state/fragments/sw.yaml` = 0★)
  · ⇒ ★**僵尸 fixing ⇒ sw-lead 整个被挡** (★advance.py 的 in_flight 规则★)
  · ★**但上一趟的分析成果在盘上**: `logs/iss309/01_before_r6_selftest.txt` /
    `02_md5_before.txt` / `03_probe_r5a_r4_scenarios.txt` (★5 个场景 A~E 的 judge 判定★)
    ⇒ ⇒ **本轮按【续做, 不是从零重做】处理**

★**本脚本只做四件事 (★全部原子, 不留 open 窗口★)**:
  ① issue_log.yaml: ISS-309 的 status 保持 fixing (★fixing → open → fixing 同一把锁内完成★)
     + task_brief 追加 cont1 续做说明 (★原 brief 全文保留, 不删一个字★) + note 追加本轮事实
  ② issue_log.yaml: ★**新开 ISS-310 (owner=mech-lead · status 直接落 fixing = 立即派出)** ★
     ⇒ ★**理由**: 队列排空时让内部待办不断线 = 本 job 的存在意义; 且
       `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` §7 排序依据第 3 条 ★**自己点名**「C1/C2 的答案在
       mech 手上 (镜腿宽度能容几层 / 多宽) ⇒ 建议先把这个问题交给 mech」★
  ③ dispatch_log.yaml: 追加 2 条派活登记
  ④ 不碰任何别的文件 (不碰 HW/ MECH/ SW/ 的任何工程文件 · 不碰板)
"""
from __future__ import annotations

import fcntl
import os
import shutil

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
LOG = os.path.join(HERE, "issue_log.yaml")
DL = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
BAK_SUF = ".bak_20261118_0530_cronfb67_iss309_cont1_iss310"

ISS309_CONT1_FILE = "state/dispatch_briefs/ISS-309_sw_r6_selftest_5of7_cont1.md"
ISS310_FILE = "state/dispatch_briefs/ISS-310_mech_board_frame_decision_input.md"
TODAY = "2026-11-18"

ISS309_NOTE = (
    "★**2026-11-18 05:3x · cron fb67af40 (ARS45 队列自动派活) 僵尸 fixing 续做重派 cont1** ★ "
    "★**上一趟子会话 `agent:sw-lead:subagent:4f1fbe6b` (taskName `queue_iss309`) 04:55:25 起 · 05:05:48 死 · "
    "runtimeMs=624507 · status=timeout · abortedLastRun=true ⇒ ★**根因 = 父 run 结束时子会话被连带 abort "
    "(★与 ISS-308 第一趟同一个死法★) ⇒ 不是 sw-lead 的错** ★ "
    "★**0 件交付物落地** (★main 05:3x 实读★): `HANDOFF/2026-11-18_sw-lead_ISS309_R6反向用例5of7归因.md` 不存在 · "
    "`state/fragments/sw.yaml` 里 `grep -c iss309` = 0 ⇒ ⇒ **僵尸 fixing ⇒ sw-lead 整个被挡** ★ "
    "★**★但上一趟的分析成果【已经在盘上】(★main 05:3x 实读核对★)**: "
    "`logs/iss309/01_before_r6_selftest.txt` (修前基线快照) · `logs/iss309/02_md5_before.txt` (10 件 md5 前值) · "
    "`logs/iss309/03_probe_r5a_r4_scenarios.txt` (★5 个场景 A~E 的 judge 判定★) "
    "⇒ ⇒ **本轮按【续做, 不是从零重做】处理** ★ "
    "★**★main 05:3x 读 `03_probe` 得到的一条【关键实测】(★已写进 cont1 任务书, 仍要 sw-lead 独立复核★)**: "
    "★**场景 A (只把链头那一行的【显式】单号 ISS-302 改成 ISS-999) ⇒ `head_iss=['ISS-302','ISS-999']` ⇒ "
    "judge 判定 = ★绿 (无红项)★** ★ · ★**场景 B (台账里所有 ISS-302 改成 ISS-999) ⇒ `head_iss=['ISS-999']` ⇒ "
    "judge 判定 = ★绿 (无红项)★** ★ ⇒ ⇒ **链头的落表单号被改坏之后 judge 自己没有判红 ⇒ "
    "R5a 大概率是【真判据缺陷 (漏放)】而不是夹具假伤** ⇒ ★**这正是原任务书 §1-② 点名的「最要紧的一问」, "
    "现在有实测证据了** ★ ⇒ ★**但 ★★边界: `SW/tools/check_demo_panel_spec.py` 的 `check_r6_hard_protected()` "
    "是权威判据, 本单不许动 ⇒ 修法只能落在反向用例脚本自己的夹具/断言侧; 要动权威判据 ⇒ 出 need 给 main** ★ "
    "★**★板零写板 (★main 05:3x 实跑★)**: 板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17` "
    "一字未动 ⇒ ★本单全程不许碰板★ ★ "
    "★**cont1 任务书全文**: `state/dispatch_briefs/ISS-309_sw_r6_selftest_5of7_cont1.md` "
    "(5,919 B · `check_brief_commands.py --brief-file` rc=0) ★"
)

ISS310_NOTE = (
    "★**2026-11-18 05:3x · cron fb67af40 (ARS45 队列自动派活) 新开并直接派出 (★status 直接落 fixing ⇒ "
    "兄弟 job 775d9893 的 advance.py 看不见 open 窗口 ⇒ 不会重复派同一个 agent★)** ★ "
    "★**开单依据 (★main 05:2x~05:3x 本机实跑, 不抄任何 agent 报告★)** ★ "
    "★**① 队列已排空**: `state/advance.py --json` ⇒ `internal: []` · `approvals: []` · `waiting: []` "
    "⇒ ★**三个总工名下 open=0** (★open 的 16 条全在 boss(5)+main(11)⇒ AGENT_ROLE 过滤后必空★) ⇒ "
    "★**本轮按「开新单」处理 (队列排空时让内部待办不断线 = 本 job 的存在意义)★** ★ "
    "★**② mech-lead 名下空**: `state/issue_log.yaml` 实读 305 条 ⇒ mech-lead 名下 `open=0` · `fixing=0` "
    "(★全部 = closed 14 / verified 46 / deferred 3★) ⇒ ★**没有在飞单 ⇒ 名额可用** ★ "
    "★**③ mech-lead 自己的闸全绿**: `MECH/service_port_check.py` rc=0 (57/57) · "
    "`MECH/check_onepass_struct_crosscheck.py` rc=0 · `MECH/check_onepass_mech_sync.py` rc=0 · "
    "`MECH/check_board_frame_coords.py` rc=0 · `MECH/check_mech_verdict_freshness.py` rc=0 ⇒ "
    "★`state/gate_check.py` rc=0 ⇒ Q7 钉板 md5 闸链 **9/9 道绿** ⇒ ⇒ **MECH 侧不缺闸, 缺的是【两套框口径的对照表】** ★ "
    "★**④ 机检指出的真缺口 (★main 05:2x 实跑★)**: `state/gate_check.py` 【缺口清单】4 条 ⇒ "
    "★**mech-lead 104 条需求确实还没人答 (等另一个总工)** ★ ⇒ ★**但「等谁答」这件事本身没人管** ⇒ "
    "★**⇒ 而「板那一趟画在哪个框上」这个问题, 恰好是 MECH 域自己的两套口径在打架, 且 HW 作业包自己点名要交给 mech** ★ "
    "★**⑤ 本单是【纯分析 / 作业包类】**: ★**零写板 · 零落表 · 零改闸 · 零改既有文档正文 · 零外发 · 不替老板拍板** ★ "
    "★**⑥ 与主线的关系**: 老板 2026-11-17 00:43「接下来的目标是绘制 PCB 图」⇒ ★**板只改一次 ⇒ "
    "这一趟画在哪个框上, 是最贵的那个未裁分歧** ⇒ 本单交的是【代价对照书 + 机器可判的可行域表】★ ★"
)


def read(rel: str) -> str:
    with open(os.path.join(PROJ, rel), encoding="utf-8") as f:
        return f.read()


def main() -> int:
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)

        with open(LOG, encoding="utf-8") as f:
            log = yaml.safe_load(f)
        issues = log["issues"]
        by_id = {it["id"]: it for it in issues}

        # ---------------- ① ISS-309 · 僵尸 fixing → 续做重派 (status 全程 fixing) ----------------
        it309 = by_id.get("ISS-309")
        if it309 is None:
            print("⚠ ISS-309 不存在 ⇒ 中止")
            return 1
        if it309.get("status") != "fixing":
            print(f"ℹ ISS-309 status={it309.get('status')} (不是 fixing) ⇒ 幂等跳过 (不重复改)")
        else:
            cont1 = read(ISS309_CONT1_FILE)
            # ★★fixing → open → fixing 同一把锁内完成 ⇒ 外部永远观察不到 open ⇒ 兄弟 job 不会撞车★★
            it309["status"] = "open"
            it309["status"] = "fixing"
            it309["dispatched_at"] = TODAY
            it309["note"] = (it309.get("note") or "") + "\n\n★" + ISS309_NOTE
            it309["task_brief"] = (
                (it309.get("task_brief") or "")
                + "\n\n\n" + ("=" * 78) + "\n\n★**★cont1 续做说明 (★2026-11-18 05:3x · cron fb67af40 僵尸重派★)** ★\n\n"
                + cont1
            )
            print("✅ ISS-309: fixing→open→fixing 原子完成 + cont1 续做说明已并入 task_brief (原 brief 全文保留)")

        # ---------------- ② ISS-310 新开 (owner=mech-lead · 直接落 fixing = 立即派出) ----------------
        if "ISS-310" in by_id:
            print("ℹ ISS-310 已存在 ⇒ 幂等跳过 (不重复开单)")
        else:
            issues.append({
                "id": "ISS-310",
                "title": (
                    "★★[主线内·MECH 侧·板框口径对照类·内部活] ★★【板框口径「两套并存」的代价对照 + 机器可判的可行域表 "
                    "⇒ 交 main/老板一次拍 U-1 / P7】★★ ⇒ ★**纯分析/作业包类 · 零写板 · 零落表 · 零改闸 · "
                    "零改既有文档正文 · 零外发 · 不替老板拍板** ★"
                ),
                "severity": "high",
                "owner": "mech-lead",
                "reporter": "main",
                "raised": TODAY,
                "due": "2026-11-19",
                "status": "fixing",
                "external": False,
                "need_keys": [],
                "fix_ref": None,
                "verify_by": "main",
                "verify_result": None,
                "verify_date": None,
                "dispatched_at": TODAY,
                "note": ISS310_NOTE,
                "task_brief": read(ISS310_FILE),
            })
            print("✅ ISS-310 新开 (owner=mech-lead · status=fixing ⇒ 直接派出)")

        shutil.copy2(LOG, LOG + BAK_SUF)
        tmp = LOG + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)
        os.replace(tmp, LOG)

        # ---------------- ③ 派活日志 ----------------
        with open(DL, encoding="utf-8") as f:
            dl = yaml.safe_load(f) or {}
        dl.setdefault("entries", [])
        if not any(
            isinstance(e, dict) and e.get("issue") == "ISS-309" and "cont1" in str(e.get("job", ""))
            for e in dl["entries"]
        ):
            dl["entries"].append({
                "issue": "ISS-309",
                "agent": "sw-lead",
                "at": TODAY,
                "brief": (
                    "★**ISS-309 cont1 续做 (★僵尸 fixing 重派·不是从零重做★)** ★ "
                    "★**上一趟 `agent:sw-lead:subagent:4f1fbe6b` 04:55:25→05:05:48 死 "
                    "(★status=timeout · abortedLastRun=true · runtimeMs=624507·父 run 结束连带 abort★) "
                    "⇒ 0 交付物落地 ⇒ 僵尸 fixing ⇒ sw-lead 被挡** ★ "
                    "★**在盘可用的成果**: `logs/iss309/01_before_r6_selftest.txt` + `02_md5_before.txt` + "
                    "`03_probe_r5a_r4_scenarios.txt` (★5 场景 A~E 的 judge 判定★) ⇒ **不许重做基线/重想那 5 个场景** ★ "
                    "★**★main 05:3x 读 03_probe 的关键实测**: 场景 A/B ⇒ 链头单号被改坏 ⇒ **judge 判绿** ⇒ "
                    "⇒ **R5a 大概率是【真判据缺陷 (漏放)】而不是夹具假伤** ⇒ ★**这正是原 brief §1-② 点名的最要紧一问** ★ "
                    "★**任务书全文**: `state/dispatch_briefs/ISS-309_sw_r6_selftest_5of7_cont1.md` "
                    "(5,919 B · `check_brief_commands.py --brief-file` rc=0) ★ "
                    "★**边界**: 零写板 · 零落表 · 零改权威判据 · 零改 `state/gate_check.py` · 零外发 · "
                    "不替老板拍板 · 不自签 issue_log · 只写自己的分片 + SW/ + HANDOFF/ + logs/iss309/ ★"
                ),
                "job": (
                    "cron fb67af40 (ARS45 队列自动派活) · ★派活时刻 2026-11-18 05:3x · "
                    "★**僵尸 fixing 续做重派 (cont1)** ★ · "
                    "★**status 全程 fixing ⇒ 无 open 窗口 ⇒ 兄弟 job 775d9893 不会重复派** ★ · "
                    "★**★根因写进 dispatch_log: 子会话随父 run 结束被连带 abort "
                    "(★与 ISS-308 第一趟同一个死法★) ⇒ ⇒ **本趟用 sessions_yield 等子会话交卷, 不许直接结束父 run** ★"
                ),
            })
        if not any(
            isinstance(e, dict) and e.get("issue") == "ISS-310" for e in dl["entries"]
        ):
            dl["entries"].append({
                "issue": "ISS-310",
                "agent": "mech-lead",
                "at": TODAY,
                "brief": (
                    "★**ISS-310 新开 (★纯分析 / 作业包类★): 板框口径「两套并存」的代价对照 + 机器可判的可行域表** ★ "
                    "★**病灶**: MECH 域自己两套框口径打架 (`BOARD_PORT_OPENING_S6_WORKPACKET.md` §3.2 判台架板三处判红 "
                    "⇒ 「推荐本趟对着产品板 60×30 画」 vs `BOARD_ONEPASS_MECH_CLAIMS.md` §1~§3 全部坐标钉在 B160x100 "
                    "⇒ U-1「不许合并」待拍) ★ 而 `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` §7 排序依据第 3 条 **自己点名** "
                    "「C1/C2 的答案在 mech 手上 (镜腿宽度能容几层/多宽) ⇒ 建议先交给 mech」 ⇒ 且那一行引的「产品板 (60×15)」"
                    "**已是作废板宽** (现行 60×30 · ISS-118) ★ "
                    "★**交付**: `MECH/board_frame_feasibility.py` (三套框 × 板厚档 × 层数 · 带 --selftest 反向用例) + "
                    "`MECH/BOARD_FRAME_DECISION_INPUT.md` (两套口径逐字并列 + 冲突点 + 两条路线代价 + 三句话建议·不代拍) + "
                    "`HANDOFF/2026-11-18_mech-lead_ISS310_板框口径代价对照.md` + `logs/iss310/` + mech 分片 ★ "
                    "★**任务书全文**: `state/dispatch_briefs/ISS-310_mech_board_frame_decision_input.md` "
                    "(10,143 B · `check_brief_commands.py --brief-file` rc=0) ★ "
                    "★**边界**: 零写板 · 零落表 · 零改闸 · 零改既有文档正文 · 不碰 HW/ 与 SW/ · 零外发 · "
                    "不替老板拍板 · 不自签 issue_log · 只写自己的分片 ★"
                ),
                "job": (
                    "cron fb67af40 (ARS45 队列自动派活) · ★派活时刻 2026-11-18 05:3x · "
                    "★**新开单 + 直接派出 (status 直接落 fixing)** ★ · "
                    "★**依据: 队列排空 (internal=[]) + mech-lead 名下 open=0/fixing=0 + MECH 侧 6 道闸全绿 + "
                    "机检缺口清单指 mech-lead 104 条需求没人答 + HW 作业包 §7 自己点名把「C1/C2 产品板口径」交给 mech** ★"
                ),
            })

        shutil.copy2(DL, DL + BAK_SUF)
        tmp_dl = DL + ".tmp"
        with open(tmp_dl, "w", encoding="utf-8") as f:
            yaml.safe_dump(dl, f, allow_unicode=True, sort_keys=False, width=200)
        os.replace(tmp_dl, DL)

        # ---------------- ④ 回读校验 ----------------
        with open(LOG, encoding="utf-8") as f:
            chk = yaml.safe_load(f)
        by2 = {it["id"]: it for it in chk["issues"]}
        print(f"   ISS-309 status = {by2['ISS-309'].get('status')} owner={by2['ISS-309'].get('owner')}  (★期望 fixing / sw-lead★)")
        print(f"   ISS-309 task_brief 长度 = {len(by2['ISS-309'].get('task_brief') or '')}  (★原 brief + cont1★)")
        print(f"   ISS-310 status = {by2['ISS-310'].get('status')} owner={by2['ISS-310'].get('owner')}  (★期望 fixing / mech-lead★)")
        print(f"   ISS-310 task_brief 长度 = {len(by2['ISS-310'].get('task_brief') or '')}")
        print(f"   issues 总数 = {len(chk['issues'])}")
        print(f"   备份 = {os.path.basename(LOG + BAK_SUF)} / {os.path.basename(DL + BAK_SUF)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
