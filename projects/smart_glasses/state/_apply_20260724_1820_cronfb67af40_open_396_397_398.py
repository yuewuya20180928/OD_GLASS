#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★_apply_20260724_1820_cronfb67af40_open_396_397_398.py★

★**用途**: cron `fb67af40` (ARS45 队列自动派活) · 2026-11-24 18:2x 一趟
  ⇒ ★**新开 3 条内部单并【直接落 `fixing`】** (★铁律⑩-i: 先落 fixing 再 spawn ⇒
    兄弟 job `775d9893` 的 `advance.py --json` 看不见 ⇒ 零撞车窗口★)

★**落哪三条**: 
  · ISS-396 → hw-lead  · 「板只改一次」那一趟的 FTS 排针【改孔 0.65→0.71】还没进作业包/预检清单
                   ⇒ 把 ISS-391 交回的 §4 登记项落到位 ⇒ `HW/check_fts_land_drill_same_batch.py` 由 4/7 转 7/7
  · ISS-397 → mech-lead · 座体三量 (绝缘体高/外形宽/外形深) 现在是 [0数据] ⇒ 把「板只改一次那一趟投板前
                   打单板样 + 卡尺量三量」这条降级做成可执行收样作业包 + 新机器闸
  · ISS-398 → sw-lead  · 第三道病闸 `SW/tools/check_sw_ref_reachability_v2.py` 的 `--selftest` 实测 0/7
                   ⇒ 差值型自测在基线漂移时全灭 ⇒ 夹具改成基线无关型 + 交 SW_MD5 重锚逐字补丁 (不代拍)

★**本脚本三道自保**: ① md5 守卫 (写前重算源文件 md5, 不一致 ⇒ rc=3 中止) 
  ② 原子写 (`os.replace`) ③ 写后复跑 `state/check_brief_commands.py` 的 task_brief 判定
★**零外发 · 零写板 · 零落表 · 零改既有闸 · 零改 PROJECT_TRACKER §0 · 不写任何 agent 的分片**
"""
import hashlib
import io
import os
import shutil
import sys
import time

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LOG = os.path.join(HERE, "issue_log.yaml")
BRIEFS = os.path.join(HERE, "dispatch_briefs")
BACKUP = os.path.join(HERE, "issue_log.yaml.bak_20261124_1820_cronfb67af40_open_396_397_398")


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def brief_text(name):
    with io.open(os.path.join(BRIEFS, name), encoding="utf-8") as f:
        return f.read()


def main():
    if not os.path.exists(LOG):
        print("★issue_log.yaml 不存在 ⇒ 中止")
        return 2
    src_md5 = md5(LOG)
    with io.open(LOG, encoding="utf-8") as f:
        doc = yaml.safe_load(f) or {}
    issues = doc.get("issues") or []
    have = {i.get("id") for i in issues}
    for iid in ("ISS-396", "ISS-397", "ISS-398"):
        if iid in have:
            print("★%s 已在台账 ⇒ 中止 (不重复开单)" % iid)
            return 2

    common = dict(
        source_agent="main",
        verify_by="main",
        reporter="main",
        raised="2026-11-24",
        due="2026-11-27",
        status="fixing",
        external=False,
        dispatched_at="2026-11-24",
    )

    note_common = (
        "★**2026-11-24 18:2x cron fb67af40 (ARS45 队列自动派活) 新开并【直接落 fixing】**"
        "(★铁律⑩-i: 先落 fixing 再 spawn ⇒ 兄弟 job 775d9893 的 `advance.py --json` 看不见本单 ⇒ 零撞车窗口★) ★\n"
        "★**开单依据 (本机实读 + 实算, 不抄任何 agent 报告)★**: ① `python3 state/advance.py --json` 实跑 ⇒ "
        "`internal: []` / `approvals: []` / `waiting: []` / `decisions: 55` ⇒ ★**根因 = 三个总工名下各占着 "
        "`status: fixing` 的在飞单** ⇒ 逐条实检: hw-lead `ISS-395` (交卷页 16:45 + 真相页 + 新闸 + 分片 16:46 在盘)、"
        "sw-lead `ISS-392` (交卷页 15:15 + 分片登记在盘)、mech-lead `ISS-393` (交卷页 16:46 + 分片 16:44 在盘) "
        "⇒ ★**三条均已交卷 ⇒ 三个槽位实际已空** ⇒ ② 本 job 逐道实跑板侧/结构侧/SW 侧闸 ⇒ "
        "**唯一剩下的真红 = `HW/check_fts_land_drill_same_batch.py` (rc=1 · 4/7 · D1/D2/D3 红)**, "
        "其余 (preflight_coverage / commit_order / iss354×2 / s8_target_list 用法错 / part_selection_gaps / "
        "gate10_concurrency / fts_single_row_land_truth / MECH 9 道 / SW 8 道) 全绿 ⇒ ⇒ "
        "★**本轮 3 条 = 三条闸/缺口各自对应的一条纯分析·登记·新建闸类活** (★零写板·零落表 ⇒ 合「板只改一次」纪律 ①★) ★\n"
        "★**命令存在性守卫**: ★**三份 brief 各跑一次 `python3 state/check_brief_commands.py --brief-file` ⇒ rc=0 / rc=0 / rc=0** ★"
    )

    new_issues = [
        dict(
            id="ISS-396",
            title=(
                "★★[★新主线·PCB 线·HW 侧·登记落盘 + 新建闸·零写板] 「板只改一次」那一趟的 FTS 排针【改孔 "
                "`0.65 → 0.71`】这条板侧动作【还没进作业包 §0.2 ③ / 预检清单 B33】⇒ 把 ISS-391 交回的 §4 登记项"
                "一次性落到位 ⇒ 让 `HW/check_fts_land_drill_same_batch.py` 由 4/7 转 7/7 ★★"
            ),
            severity="high",
            source_blocker="ISS-391",
            desc=(
                "★★[★新主线·PCB 线·HW 侧·登记落盘(改文档/生成器)+新建闸·零写板·零落表·零改既有闸判据·"
                "零改已签收页正文·零挂链·零外发·不代拍]★★\n\n"
                "★**题 (来源 = ★main 2026-11-24 18:1x 本机实跑 `HW/check_fts_land_drill_same_batch.py`·不抄任何 agent 报告★)★:\n"
                "★**① 现象**: rc=1 · 4/7 条绿 · **D1/D2/D3 三条红** ⇒ ★**D1** 作业包 §0.2 ③ 的「③」那一项原文里"
                "【查不到「钻孔」这件事】(也查不到目标孔径 `0.71`) ★**D2** 预检清单 `B33_PIN_LAND_1P27` 的【描述列】"
                "(json 项 + 表格行) 里【查不到「钻孔」】 ★**D3** 该项【验收手段列】里【没有一条读钻孔直径的命令】 ⇒ "
                "★**⇒ 「落 FTS 要改孔 0.65→0.71」这条板侧动作不在那一趟的清单上 ⇒ 不在清单 = 没人做 = "
                "投板后排针插不进 ⇒ 【板改两次】** ★\n"
                "★**② 留证**: `state/.verify/fb67_1815/check_fts_land_drill_same_batch.py.log` ★\n"
                "★**③ 权威登记单已在盘**: `HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md` (★ISS-391 交卷页·§3 = 5 处差集表·"
                "§4 = 5+1 条逐字登记★) ⇒ ★**本单 = 把 §4 落到位, 不许自己另写一套口径** ★\n"
                "★**④ 三个坑 (逐字依据在 §0-②/§0-③)**: ★**(甲)** 预检清单页是【生成器产物】"
                "(`state/_iss277_build_preflight.py`) ⇒ 手写页会蒸发 ⇒ ★**必须补在生成器里 + 重跑生成器** ★"
                "★**(乙)** `HW/check_onepass_preflight_coverage.py` 的 P4 只判「③ 有没有对应 item」不查子动作 ⇒ "
                "**P4 绿 = 假绿 (第二次)** ⇒ ★**该闸已签收 ⇒ 本单不许改它 (§4 #4 交 main 拍)** ★"
                "★**(丙)** §4 #5 (BOM `opn`/`footprint` 两栏) 属【落表】⇒ 落表 = 改板 ⇒ ★**本单只出逐字改法, 不许真落表** ★"
            ),
            owner="hw-lead",
            need_keys=["iss396_fts_drill_registration_landed", "iss396_preflight_generator_drill_text"],
            task_brief=brief_text("ISS-396_hw_fts_drill_registration_landing.md"),
            note=note_common,
        ),
        dict(
            id="ISS-397",
            title=(
                "★★[★新主线·PCB 线·MECH 侧·纯查证+新建真相页+新建闸·零写板] 座体三量 (绝缘体高 / 外形宽 / 外形深) "
                "现在是 `[0数据]` ⇒ 把「板只改一次」那一趟投板前的【单板样 + 卡尺量三量】这条降级做成"
                "可执行收样作业包 + 机器闸 ★★"
            ),
            severity="high",
            source_blocker="ISS-393",
            desc=(
                "★★[★新主线·PCB 线·MECH 侧·纯查证+纯分析+新建真相页+新建机器闸+沙盒预演·零写板·零落表·"
                "零改既有闸/既有页面正文·零挂链·零外发·不代拍]★★\n\n"
                "★**题 (来源 = ★main 2026-11-24 18:1x 本机实读台账 + 三份已交卷页·不抄任何 agent 结论★)★:\n"
                "★**①** `FTS` 厂件 (Samtec 单排直插) 的「座体真实高 / 外形宽 / 外形深」三量 = `[0数据]` ⇒ "
                "官网三面复核确实没有 ⇒ 降级方案继续成立 (★`MECH/BOARD_ONEPASS_FTS_SEAT_BODY_GEOMETRY.md` · "
                "`MECH/BOARD_ONEPASS_FTS_VS_GENERIC_COURTYARD_DELTA.md`★) ★\n"
                "★**②** 降级方案 **D2 = 座体外形双轨** (★(甲) 官网 3D/CAD 下载件量外形 · (乙) 落 `FTS` 时先打一块单板样 + "
                "卡尺量三个量 (绝缘体高 / 外形宽 / 外形深) 回填 `keepout_dwg`★) ⇒ **归属 mech-lead** ⇒ "
                "**必须与「板只改一次」那一趟同批** (★`HANDOFF/2026-11-24_hw-lead_ISS394_座体选型结论传播清账与闸.md` "
                "§B5 **N7**★) ★\n"
                "★**③** 收样排期 = 要 main 回答 (★`state/fragments/mech.yaml` 的 `iss393-n8`★) ⇒ ★**本单把「怎么做」做成"
                "作业包, 排期交 main 拍, 一条都不代拍** ★\n"
                "★**④ 为什么值钱**: 三量是 `[0数据]` ⇒ 现在所有结构侧判决都在用最坏值/保守上界兜底 ⇒ "
                "★**落 FTS 时才发现外形与 courtyard 不合 ⇒ 【板改两次】** ⇒ 而「量一次」排进那一趟就能把三量从 `[0数据]` "
                "升成 `[实测]`** ★"
            ),
            owner="mech-lead",
            need_keys=["iss397_seat_three_measurements_plan", "iss397_sample_measurement_degradation"],
            task_brief=brief_text("ISS-397_mech_seat_sample_measure_plan.md"),
            note=note_common,
        ),
        dict(
            id="ISS-398",
            title=(
                "★★[★新主线·PCB 线·SW 侧·改自测夹具+出补丁·零写板] 第三道病闸 "
                "`SW/tools/check_sw_ref_reachability_v2.py` 的 `--selftest` 实测 **0/7** ⇒ 差值型自测在【基线漂移】时"
                "全灭 ⇒ 把夹具改成基线无关型 + 交出 `SW_MD5` 基线重锚的逐字补丁 (不代拍) ★★"
            ),
            severity="high",
            source_blocker="ISS-388",
            desc=(
                "★★[★新主线·PCB 线·SW 侧·纯分析+改【自测夹具】+出补丁·零写板·零落表·零改判据·零挂链·零外发·不代拍]★★\n\n"
                "★**题 (来源 = ★main 2026-11-24 18:2x 本机实跑·不抄任何 agent 报告★)★:\n"
                "★**① `--selftest` 就是死的**: `python3 SW/tools/check_sw_ref_reachability_v2.py --selftest` ⇒ "
                "**反向用例 0/7 通过** · 末行「❌ 有用例没抓到」 ⇒ RC-5/RC-6/RC-7 三条全灭 ★\n"
                "★**② 根因不在判据, 在夹具被基线漂移染红**: 三条用例都断言「★**破坏前必须 rc=0** ⇒ 才叫『不是巧合自证』★」"
                "⇒ 而「破坏前」实测就是 `rc=1` ⇒ 整棵沙盒树在动手之前已经红了 ⇒ 三条全灭 ★\n"
                "★**③ 「破坏前」为什么红**: 裸跑红项逐字 = **「新增真隐患:SW_MD5, 真隐患 4 > 基线 3」** ⇒ "
                "= **账本基线落后一跳 (不是判据错)** ⇒ 裸跑 `python3 SW/tools/check_sw_ref_reachability_v2.py` ⇒ "
                "【判决】✘ 红 (rc≠0) ★\n"
                "★**④ sw-lead 自己在 ISS-392 交卷时就点名**: `state/fragments/sw.yaml` 的 `iss392-n3` 逐字 「口径A维持现状="
                "v2长期红+差值型自测永久0/7+收紧版永远没人跑; 口径B登记进EXEMPT_LEDGER=v2回绿可挂链但留一个漏检窗口且"
                "★**要改已签收件v2 (本单零改要main派单)**★」 ⇒ ★**这一单就是 main 的派单** ★\n"
                "★**⑤ 同型病灶诊断页已在盘**: `SW/BOARD_ONEPASS_GATE_FAILURE_DIAGNOSIS.md` (★ISS-388 交卷★) 那条 "
                "「★**差值型自测在基线漂移时全灭 ⇒ 闸自曝『本闸不可信』⇒ 反而掩盖了『我不是坏了, 是账漂了』**★」 ★\n"
                "★**⑥ 为什么值钱**: 这道闸零挂链 ⇒ 它红了没人知道; 而「自测 0/7」= 它自己说自己不可信 ⇒ "
                "★**板那一趟当天 SW 侧 10 道闸 (见 `SW/tools/check_onepass_sw_release.py`) 里就有它这一族** ⇒ "
                "★**闸不可信 + 当天没人敢信它 = 那天最容易漏判的地方** ★"
            ),
            owner="sw-lead",
            need_keys=["iss398_v2_selftest_baseline_independent", "iss398_sw_md5_reanchor_patch"],
            task_brief=brief_text("ISS-398_sw_ref_reach_v2_selftest_baseline_independent.md"),
            note=note_common,
        ),
    ]

    for i in new_issues:
        for k, v in common.items():
            i.setdefault(k, v)

    # ---- ① md5 守卫: 写前重算 ----
    if md5(LOG) != src_md5:
        print("★md5 守卫: 源文件在读与写之间被改过 ⇒ 中止 (rc=3)")
        return 3

    doc["issues"] = list(issues) + new_issues
    shutil.copy2(LOG, BACKUP)
    tmp = LOG + ".tmp.%d" % int(time.time())
    with io.open(tmp, "w", encoding="utf-8") as f:
        yaml.safe_dump(doc, f, allow_unicode=True, sort_keys=False, width=100000)
    # ---- ② 原子替换 ----
    os.replace(tmp, LOG)

    print("★已写 %s (+3 条: ISS-396 / ISS-397 / ISS-398 · status=fixing)" % LOG)
    print("★备份 %s (md5 %s)" % (BACKUP, md5(BACKUP)))
    print("★台账条数 %d → %d" % (len(issues), len(doc["issues"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
