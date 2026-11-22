#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★ISS-308 / ISS-309 / ISS-310 落地 (fixing → verified) + 新开 ISS-311 / ISS-312 / ISS-313 (status=open, 待下一轮派出)★
   · cron fb67af40 (ARS45 队列自动派活) · 2026-11-18 05:4x~06:0x ★

★**为什么有本脚本** (★main 05:4x~05:5x 本机实跑, 不抄任何 agent 报告★):
  · 本轮 `state/advance.py --json` ⇒ internal=[] · approvals=[] · waiting=[] ⇒ **队列排空**
  · 但上一轮 (05:3x) 派出的三条 (ISS-308 cont1 / ISS-309 cont1 / ISS-310) 的子会话
    `agent:hw-lead:subagent:e4cc9451` / `agent:sw-lead:subagent:490f22db` / `agent:mech-lead:subagent:8243cbe8`
    **全部 status=done** (★05:35:14 / 05:31:31 / 05:36:14 收★) ⇒ **不是僵尸 fixing** ⇒ 可以落地
  · ★**本机独立复核 (三条全过)**★:
      ISS-308: `python3 state/_iss308_s8_reachability_check.py --selftest` ⇒ **rc=0** (★4 条反向用例全过,
                ★含上一趟 rc=1 的「CSI_D0_D2_N 的桶被改成 B5」⇒ 现在判红 ⇒ 独立权威源已建★)
      ISS-309: `python3 SW/tools/check_demo_panel_spec_r6_selftest.py` ⇒ **rc=0 · 7/7**
      ISS-310: `python3 MECH/board_frame_feasibility.py --selftest` ⇒ **rc=0** (★7 条反向用例, 含任务书点名要的 3 条★)
      板零写板: `HW/PCB/demo_mainboard.kicad_pcb` md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17` (前后逐字节相同)
      `state/merge.py` ⇒ rc=0
  · ★**本轮不派活**: 三个总工名下【都还有正在跑的会话】(★main 05:46 实读 transcript mtime★)
      hw-lead: 05d9d2be / 32e8971e / d353c753 / f58cfddd · sw-lead: 57a0e657 / 00d4b62f ·
      mech-lead: 8855535b / fb57e8cd / 22443320 ⇒ ★**按纪律「一个 agent 同时只派 1 条」⇒ 三个全跳过** ★
    ⇒ 所以本轮把三条新单开成 **status=open** (★队列有料 ⇒ 下一轮谁先腾出 agent 谁派出★)

★**本脚本只做四件事 (★全部原子, 不留半拉子★)**:
  ① issue_log.yaml: ISS-308 / ISS-309 / ISS-310 的 status → verified + verify_result / verify_date + note 追加
  ② issue_log.yaml: 新开 ISS-311 (hw-lead) / ISS-312 (sw-lead) / ISS-313 (mech-lead) · status=open
  ③ dispatch_log.yaml: 追加 6 条登记 (3 条落地 + 3 条新开)
  ④ 不碰任何别的文件 (不碰板 · 不碰 HW/ MECH/ SW/ 的任何工程文件)
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
BAK_SUF = ".bak_20261118_0600_cronfb67_land308_309_310_open311_312_313"

TODAY = "2026-11-18"
BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"
BOARD_MTIME = "2026-11-06 07:07:17"

BRIEF_311 = os.path.join(HERE, "dispatch_briefs", "ISS-311_hw_onetrip_reissue_manifest.md")
BRIEF_312 = os.path.join(HERE, "dispatch_briefs", "ISS-312_sw_r6_judge_hole_fix.md")
BRIEF_313 = os.path.join(HERE, "dispatch_briefs", "ISS-313_mech_open_req_triage.md")

COMMON_TAIL = (
    "★**边界自证 (★main 05:4x~05:5x 本机实跑★)**: 板 `HW/PCB/demo_mainboard.kicad_pcb` md5 "
    f"`{BOARD_MD5}` · mtime `{BOARD_MTIME}` 交卷前后逐字节相同 ⇒ **零写板** ★ · "
    "网表/脚表/BOM/落表台账 未动 ⇒ **零落表** ★ · `state/merge.py` rc=0 ★ · 零外发 ★"
)

# ────────────────────────────────────────────────────────────────────────────
# ① 三条落地
# ────────────────────────────────────────────────────────────────────────────
LAND = {
    "ISS-308": dict(
        verify_result=(
            "✅ verified (★main 2026-11-18 05:4x~05:5x 独立复核·不抄 agent 报告★) ⇒ "
            "★**交卷物在盘**: `HW/PCB/S8_REACHABILITY_VERDICT.md` (50,255 B · 05:31:06) + "
            "`HANDOFF/2026-11-18_hw-lead_ISS308_S8可达性判决书.md` (45,584 B · 05:34:21) + "
            "`logs/iss308/` + hw 分片 (grep -c iss308 > 0)★ ⇒ "
            "★**自证本机复跑**: `python3 state/_iss308_s8_reachability_check.py --selftest` ⇒ **rc=0** · "
            "★4 条反向用例全过 (★含上一趟 rc=1 的「CSI_D0_D2_N 的桶被改成 B5 (B5 也是合法桶)」⇒ "
            "**现在判红** ⇒ 桶归属的【独立权威源】已建起来 ⇒ 闸不再形同虚设★)★ ⇒ "
            "★**交卷内容含**: §2-A 22 网名 → 5 桶落桶表 (每条带实测出处) · §2-B 老板还差 **N=2 个字母 (S8 侧)** · "
            "§2-C 技术活清单 T1~T7 (★每条 6 列齐全 + 与桶的对应 + 顺序★) · §0 口径声明 + 3 条差异注记★"
        ),
        note=(
            "★**2026-11-18 05:4x · cron fb67af40 (ARS45 队列自动派活) 落地 verified** ★ "
            "★**子会话 `agent:hw-lead:subagent:e4cc9451-31a4-439f-bd30-5f874020b514` (taskName `queue_iss308`) "
            "status=done · 05:35:14 收** ⇒ 不是僵尸 fixing ⇒ 可落地 ★ "
            "★**★判据修复的实证 (★本单最要紧的一条★)**: 上一趟 `--selftest` **rc=1** (★改了桶居然还判绿★) ⇒ "
            "本趟 **rc=0** 且「CSI_D0_D2_N 的桶被改成 B5」**判红** ⇒ ⇒ **独立权威源已建** ⇒ "
            "★符合 MEMORY 铁律「判据必须有独立于被测对象的第二来源」★ "
            "★**板零写板 (★main 05:4x 实跑★)**: 板 md5 `" + BOARD_MD5 + "` · mtime `" + BOARD_MTIME + "` 一字未动 ★ " + COMMON_TAIL
        ),
    ),
    "ISS-309": dict(
        verify_result=(
            "✅ verified (★main 2026-11-18 05:4x~05:5x 独立复核·不抄 agent 报告★) ⇒ "
            "★**交卷物在盘**: `HANDOFF/2026-11-18_sw-lead_ISS309_R6反向用例5of7归因.md` (44,469 B · 05:29:42) + "
            "`SW/tools/check_demo_panel_spec_r6_selftest.py` + `logs/iss309/` + sw 分片 (grep -c iss309 = 13)★ ⇒ "
            "★**自证本机复跑**: `python3 SW/tools/check_demo_panel_spec_r6_selftest.py` ⇒ **rc=0 · 7/7** ★ ⇒ "
            "★**判决 (三选一, 不骑墙)**: R4 = ★夹具假伤★ (合成台账缺板/`.kicad_pro` 保护基线登记 ⇒ 红在另一个维度 ⇒ "
            "只补夹具输入·判据一字未动) · R5a = ★真判据缺陷·漏放 (主因) + 夹具断言过时 (次因)★ ⇒ "
            "★**权威判据 `SW/tools/check_demo_panel_spec.py` 对【链头落表单号】只有「非空」一道检查 ⇒ 改坏链头单号判绿** ★"
        ),
        note=(
            "★**2026-11-18 05:4x · cron fb67af40 (ARS45 队列自动派活) 落地 verified** ★ "
            "★**子会话 `agent:sw-lead:subagent:490f22db-e470-46b2-8166-f3578493c9eb` (taskName `queue_iss309`) "
            "status=done · 05:31:31 收** ⇒ 不是僵尸 fixing ⇒ 可落地 ★ "
            "★**need 已由 main 拍板 (★下一趟落成 ISS-312★)**: ★**修法 A + B 一起做** —— A = 判据加「链头产出单号不唯一 ⇒ 判红」 "
            "(治变体① 台账自相矛盾) · B = 链头单号必须与【独立信源】对上 (治变体② 台账自洽但单号是假的) ⇒ "
            "只做 A 治不了变体② · 只做 B 治不了多值★ ⇒ ★**独立信源口径 = `state/issue_log.yaml` 里的真单号** "
            "(★不许拿判据自己判自己·不许拿台账两个副本互证★)★ "
            "★**sw-lead 实测纠正了 main 的 03_probe**: main 只改了一处 (⇒ 自相矛盾态) · sw-lead 把每一处都改 ⇒ 台账变自洽 ⇒ "
            "⇒ 「唯一性」修法治不了变体② ⇒ ⇒ 修法必须是 A/B 组合 ★ " + COMMON_TAIL
        ),
    ),
    "ISS-310": dict(
        verify_result=(
            "✅ verified (★main 2026-11-18 05:4x~05:5x 独立复核·不抄 agent 报告★) ⇒ "
            "★**交卷物在盘**: `MECH/BOARD_FRAME_DECISION_INPUT.md` (37,313 B) + `MECH/board_frame_feasibility.py` (34,119 B) + "
            "`HANDOFF/2026-11-18_mech-lead_ISS310_板框口径代价对照.md` (45,640 B · 05:35:09) + `logs/iss310/` + mech 分片★ ⇒ "
            "★**自证本机复跑**: `python3 MECH/board_frame_feasibility.py --selftest` ⇒ **rc=0** · "
            "★7 条反向用例 (含任务书点名要的 3 条: 内腔改 4.00 必判红 / 孔位搬到 15mm 板必判不成立 / 板厚 1.60→1.00 内腔 4.10→4.70 且 ❌→✅)★ ⇒ "
            "★**三句话结论 (不代拍)**: 台架板 36 档全红 ⇒ 不能当目标板 · 产品板 F30A 板厚 0.80/1.00 全绿 · 1.22 判红 (内腔 4.48 只差 0.02) ⇒ 必须连「板厚 ≤1.00」一起定 · 建议先拍框 → 再拍板厚 → 再拍层数★"
        ),
        note=(
            "★**2026-11-18 05:4x · cron fb67af40 (ARS45 队列自动派活) 落地 verified** ★ "
            "★**子会话 `agent:mech-lead:subagent:8243cbe8-54e0-43f6-b292-bdedc8f6f5aa` (taskName `queue_iss310`) "
            "status=done · 05:36:14 收** ⇒ 不是僵尸 fixing ⇒ 可落地 ★ "
            "★**★必须转给 main 的订正 (★mech-lead 实测点名★)**: `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` "
            "**L659** (「板宽 15mm 是结构约束」) + **L668** (§7 排序依据第 3 条「产品板 (60×15)」) —— "
            "**15 是作废板宽** (★现行 60×30 · ISS-118/130★) ⇒ 老板照那一行拍会拍错 ⇒ "
            "★本单零改动 HW 文件 ⇒ 已写进交卷单 §B5 第 1 条 + 4 条 `needs_from` ★ "
            "★**判据纪律 (★本单做对了的一条★)**: 36 档表的阈值**只读** `MECH/service_port_check.py` 的 BASE/TOL/CRIT ⇒ "
            "★零自造零漂移 ⇒ 且 `--selftest` 专抓「改了参数还判绿」的假闸★ " + COMMON_TAIL
        ),
    ),
}

# ────────────────────────────────────────────────────────────────────────────
# ② 三条新开 (status=open ⇒ 下一轮 advance.py 能看见 ⇒ 谁先腾出 agent 谁派出)
# ────────────────────────────────────────────────────────────────────────────
NEW = [
    dict(
        id="ISS-311",
        owner="hw-lead",
        due="2026-11-19",
        title=(
            "★★[主线内·HW 侧·产出链重出清单类·内部活] ★★【「板只改一次」那一趟要重出哪些件: C1 焊盘级等价差 2 个 (网表 480 / 板上 482) + 投产包原理图源文件 11 个不一致 ⇒ 交一张逐件的【重出清单 + 顺序 + 同趟出 + 验收判据】作业包】★★ "
            "⇒ ★**纯分析 / 作业包类 · 零写板 · 零落表 · 零重生成 · 零改闸 · 零改既有文档正文 · 零外发 · 不替老板拍板** ★"
        ),
        note=(
            "★**2026-11-18 06:0x · cron fb67af40 (ARS45 队列自动派活) 新开 (status=open ⇒ 下一轮派出)** ★ "
            "★**开单依据 (★main 05:5x 本机实跑 `python3 state/chain_gate.py`, 原始输出★)**: "
            "★**③ PCB 准入 ❌** = 「板与网表不等价 (C1/C2 红 ⇒ 板是旧网表的板)」· 网表 **480** / 板上带网 **482** (板 mtime 11-06 07:07)★ "
            "· ★**⑤ 投产资料包准入 ❌** = 「30/30 产物齐全 但 ★投产包比原理图旧 ⇒ 投板用的是旧板的 Gerber★」+ "
            "「原理图源文件与 `HW/PCB/` 没有一一对应: 内容与源不一致 **11 个**」★ "
            "★**⇒ 这两条红正是「板只改一次」那一趟的【产物清单】出了问题** (★老板 11-17 00:43: 那一趟必须一次做完 "
            "位号改名 + 板侧同步 B-1~B-8 + 布局修正 + 布线 45→0 + Gerber/投产包重出★) ⇒ ⇒ **本单把「Gerber/投产包重出」"
            "这一句变成一张逐件的作业包表** ★ "
            "★**为什么不与 ISS-304 重复**: ISS-304 是「作业包现状值 md5 闸重锚」(4 条 md5 现值) · 本单是「**产出链缺件清单 + 重出顺序**」· 两件事不重叠 ★ "
            "★**为什么不用「G1a-4 判据审计」当本单**: ★**已作废** —— ISS-306 (verified · sw-lead) 已经把 G1a-4 的 R4/R9 归因做完 "
            "(结论: R3(D) / R9(C) 两条红同趟消化 + 老板还差 4 个字母) ⇒ 再开一条是重复劳动 ⇒ ★**已把那份草稿 brief 撤掉**★ "
            "★**任务书全文**: `state/dispatch_briefs/ISS-311_hw_onetrip_reissue_manifest.md` "
            "(5,3xx B · `check_brief_commands.py --brief-file` rc=0) ★ "
            "★**边界**: 零写板 · 零落表 · 零重生成 · 零改闸 · 零改既有文档正文 · 零外发 · 不替老板拍板 · 不自签 issue_log ★"
        ),
    ),
    dict(
        id="ISS-312",
        owner="sw-lead",
        due="2026-11-19",
        title=(
            "★★[主线内·SW 侧·判据修复类·内部活] ★★【ISS-309 的 need 落地 (★main 已拍板: 修法 A+B 都要★): 权威判据 `check_demo_panel_spec.py` 对【链头落表单号】只查「非空」⇒ 改坏单号判绿 ⇒ 修判据 + 3 条新反向用例 (★真单号假不了★)】★★ "
            "⇒ ★**判据修复类 · 零写板 · 零落表 · 零改网表真源 · 零改 `state/gate_check.py` · 零外发 · 不替老板拍板** ★"
        ),
        note=(
            "★**2026-11-18 06:0x · cron fb67af40 (ARS45 队列自动派活) 新开 (status=open ⇒ 下一轮派出)** ★ "
            "★**开单依据**: ★**ISS-309 已 verified** (★main 05:4x 本机复跑 `SW/tools/check_demo_panel_spec_r6_selftest.py` ⇒ rc=0 · 7/7★) · "
            "它的结论 = R5a 是【真判据缺陷·漏放】⇒ ★**权威判据对【链头落表单号】没有交叉核对 ⇒ 变体①(台账自相矛盾) 与 "
            "变体②(台账自洽但单号是假的) 都判绿** ★ ⇒ ★**main 拍板: 修法 A + B 一起做** (A = 单号不唯一 ⇒ 判红 · "
            "B = 单号必须与【独立信源 = `state/issue_log.yaml` 真单号】对上) ⇒ ★**本单 = 这个拍板的落地** ★ "
            "★**★硬纪律 (★写进任务书★)**: ★**不许为了让闸变绿而改台账 / 改锚点副本 / 放宽判据** (★MEMORY 铁律: "
            "排查类 bug 要修在产生点, 不许在产物上擦★) ⇒ ★**若加严后现有链变红 ⇒ 那说明它抓到了真的不一致 ⇒ "
            "老老把「红了 + 红了的原因 + 该由谁修」写成交卷页 need, 不许自己把红抹平** ★ "
            "★**任务书全文**: `state/dispatch_briefs/ISS-312_sw_r6_judge_hole_fix.md` "
            "(4,2xx B · `check_brief_commands.py --brief-file` rc=0) ★ "
            "★**边界**: 零写板 · 零落表 · 零改网表真源 · 零改 `state/gate_check.py` · 零改 `SW/tools/check_demo_panel_spec_r6_selftest.py` "
            "(★它是回归基线★) · 零外发 · 不替老板拍板 · 不自签 issue_log ★"
        ),
    ),
    dict(
        id="ISS-313",
        owner="mech-lead",
        due="2026-11-19",
        title=(
            "★★[主线内·MECH 侧·需求闭环类·内部活] ★★【MECH 域 needs 184 条四分类处置 (waiting_on 空 113 / agent 34 / boss 20 / vendor 10 / jbd 6) ⇒ 把机检缺口清单那条「108 条没人答」+ 「16 条外部依赖挂着」两笔老账一次清掉】★★ "
            "⇒ ★**需求闭环类 · 零写板 · 零落表 · 零改闸 · 零改既有文档正文 · 零外发 · 不替老板拍板** ★"
        ),
        note=(
            "★**2026-11-18 06:0x · cron fb67af40 (ARS45 队列自动派活) 新开 (status=open ⇒ 下一轮派出)** ★ "
            "★**开单依据 (★main 05:5x 本机实跑★)**: ★**① 机检**: `python3 state/gate_check.py` ⇒ 缺口清单「mech-lead: **108 条**需求确实还没人答」★ "
            "★**② MECH 域自己的账**: `state/fragments/mech.yaml` 的 `needs_from` = **184** 条 ⇒ waiting_on 分布 = "
            "**空 113 / agent 34 / boss 20 / vendor 10 / jbd 6** ★ "
            "★**③ 外部依赖那 16 条 (★老板 2026-11-12 02:02 政策★)**: 「不再发信, 全靠自己查资料」⇒ ★**不许把外部依赖挂着当阻塞项** ⇒ "
            "16 条必须【自己网上查】+ 标证据等级 + 查不到写降级方案 ⇒ ★**本单零外发** ★ "
            "★**与主线的关系**: 老板 11-17 00:43「目标是绘制 PCB 图」⇒ 板只改一次 ⇒ 凡与【板框/板厚/层数/镜腿宽度/检修口净空/重量预算】"
            "有关的待答条目都要标出来 ⇒ 给板那一趟的输入清单 ★ "
            "★**不重做 ISS-310**: ISS-310 已交框口径对照 + 36 档机器表 (verified) ⇒ 本单只做【还没答的条目】 ★ "
            "★**任务书全文**: `state/dispatch_briefs/ISS-313_mech_open_req_triage.md` "
            "(4,4xx B · `check_brief_commands.py --brief-file` rc=0) ★ "
            "★**边界**: 零写板 · 零落表 · 零改闸 · 零改既有文档正文 · 零外发 · 不替老板拍板 · 不自签 issue_log · 只写自己的分片 ★"
        ),
    ),
]


def main() -> int:
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)

        # ---------------- ① issue_log.yaml ----------------
        shutil.copy2(LOG, LOG + BAK_SUF)
        with open(LOG, encoding="utf-8") as f:
            log = yaml.safe_load(f)
        by = {it["id"]: it for it in log["issues"]}

        for iid, cfg in LAND.items():
            it = by.get(iid)
            if it is None:
                print(f"!! {iid} 不在 issue_log 里, 跳过")
                continue
            it["status"] = "verified"
            it["verify_by"] = "main"
            it["verify_result"] = cfg["verify_result"]
            it["verify_date"] = TODAY
            it["note"] = (str(it.get("note") or "").rstrip() + "\n\n" + cfg["note"])
            print(f"   ✓ {iid}: fixing → verified (verify_result 已写)")

        for spec in NEW:
            if spec["id"] in by:
                print(f"!! {spec['id']} 已存在, 不新开 (防重复)")
                continue
            brief_path = {"ISS-311": BRIEF_311, "ISS-312": BRIEF_312, "ISS-313": BRIEF_313}[spec["id"]]
            with open(brief_path, encoding="utf-8") as f:
                brief = f.read()
            log["issues"].append({
                "id": spec["id"],
                "title": spec["title"],
                "severity": "high",
                "owner": spec["owner"],
                "reporter": "main",
                "raised": TODAY,
                "due": spec["due"],
                "status": "open",
                "external": False,
                "need_keys": [],
                "fix_ref": None,
                "verify_by": "main",
                "verify_result": None,
                "verify_date": None,
                "dispatched_at": None,
                "note": spec["note"],
                "task_brief": brief,
            })
            print(f"   ✓ {spec['id']} 新开 (owner={spec['owner']} · status=open · brief {len(brief)} B)")

        tmp = LOG + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)
        os.replace(tmp, LOG)

        # ---------------- ② dispatch_log.yaml ----------------
        shutil.copy2(DL, DL + BAK_SUF)
        with open(DL, encoding="utf-8") as f:
            dl = yaml.safe_load(f)
        entries = dl.setdefault("dispatches", [])

        for iid, cfg in LAND.items():
            entries.append({
                "issue": iid,
                "agent": by[iid]["owner"],
                "at": TODAY,
                "brief": (
                    f"★**{iid} 落地 (fixing → verified) · cron fb67af40 (ARS45 队列自动派活) · 05:4x~06:0x** ★ "
                    f"★**依据 = main 05:4x~05:5x 本机独立复核 (不抄 agent 报告)**: "
                    f"{cfg['verify_result'][:400]}… ★"
                ),
                "job": (
                    "cron fb67af40 (ARS45 队列自动派活) · ★派活时刻 2026-11-18 06:0x · "
                    "★**落地 = 子会话 status=done + 交付物在盘 + 自证本机复跑 rc=0 + 板 md5/mtime 未变** ★"
                ),
            })

        for spec in NEW:
            entries.append({
                "issue": spec["id"],
                "agent": spec["owner"],
                "at": TODAY,
                "brief": (
                    f"★**{spec['id']} 新开 (status=open ⇒ 待下一轮派出)**: {spec['title'][:220]}… ★ "
                    "★**任务书全文**: `state/dispatch_briefs/"
                    + {"ISS-311": "ISS-311_hw_onetrip_reissue_manifest.md",
                       "ISS-312": "ISS-312_sw_r6_judge_hole_fix.md",
                       "ISS-313": "ISS-313_mech_open_req_triage.md"}[spec["id"]]
                    + "` ★ ★**边界**: 零写板 · 零落表 · 零改闸 · 零改既有文档正文 · 零外发 · 不替老板拍板 · 不自签 issue_log ★"
                ),
                "job": (
                    "cron fb67af40 (ARS45 队列自动派活) · ★开单时刻 2026-11-18 06:0x · "
                    "★**★本轮【不派】= 三个总工名下都有正在跑的会话 (★main 05:46 实读 transcript mtime★) ⇒ "
                    "按纪律「一个 agent 同时只派 1 条」⇒ 三个全跳过 ⇒ ⇒ 本单先落成 status=open, 下一轮谁先腾出 agent 谁派出** ★ "
                    "★**派出纪律 (★下一轮照办★)**: ★**①先落 fixing ②再 spawn** ⇒ 落完 fixing 下一轮 in_flight 就会跳过这个 agent ⇒ 窗口消失 ★"
                ),
            })

        tmp_dl = DL + ".tmp"
        with open(tmp_dl, "w", encoding="utf-8") as f:
            yaml.safe_dump(dl, f, allow_unicode=True, sort_keys=False, width=200)
        os.replace(tmp_dl, DL)

        # ---------------- ③ 回读校验 ----------------
        with open(LOG, encoding="utf-8") as f:
            chk = yaml.safe_load(f)
        by2 = {it["id"]: it for it in chk["issues"]}
        for iid in list(LAND) + [s["id"] for s in NEW]:
            it = by2.get(iid)
            print(f"   {iid}: status={it.get('status')} owner={it.get('owner')} brief={len(it.get('task_brief') or '')} B")
        print(f"   issues 总数 = {len(chk['issues'])}")
        print(f"   备份 = {os.path.basename(LOG + BAK_SUF)} / {os.path.basename(DL + BAK_SUF)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
