#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cron fb67af40 (ARS45 队列自动派活) · 2026-11-18 19:2x · 项目总工 moli

★**本轮三件事 (★一件都不能少★)**:
  ① ★**ISS-327 落地 (fixing → verified)** — sw-lead 16:57 交卷, 交卷物在盘, main 本机独立复核过 ⇒ 签名放人
  ② ★**ISS-328 cont1 重派** — hw-lead 那一趟 17:0x~17:2x 中途断线, 但★成果已在盘上★(第 ② 件 TP no-op 已答完 + 硬前置 diff=102 已过) ⇒ 续做不是从零
  ③ ★**新开 ISS-332 (sw-lead) + ISS-333 (mech-lead)** — 两个总工名下的队列是真空 ⇒ 不开单就断线

★**纪律**: 零写板 · 零落表 · 零改闸 · 零外发 · 只写 main 自己的分片(另脚本) · 不替老板拍板
"""
from __future__ import annotations

import fcntl
import os
import shutil
import tempfile
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
DL = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
NOW = "2026-11-18"
STAMP = "20261118_1920"

BRIEF_328_CONT = open(os.path.join(
    HERE, "dispatch_briefs", "ISS-328_hw_rightupper_control_arm_cont1.md"), encoding="utf-8").read()
BRIEF_332 = open(os.path.join(
    HERE, "dispatch_briefs", "ISS-332_sw_ref_reach_launder_reverse_cases.md"), encoding="utf-8").read()
BRIEF_333 = open(os.path.join(
    HERE, "dispatch_briefs", "ISS-333_mech_designator_gate_hook_prep.md"), encoding="utf-8").read()


def atomic_write(path: str, text: str) -> None:
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_", suffix=".yaml")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


VERIFY_327 = (
    "✅ verified (★main 2026-11-18 19:2x 本机独立复核·不抄 agent 报告★) ⇒ 交卷物在盘: "
    "· 交卷页 `HANDOFF/2026-11-18_sw-lead_ISS327_改名后SW闸链复活验证.md` (34,552 B · B0~B8 八块齐全 · §B1-3「重建注册表能不能全绿」逐字回答=不能 · §B5-1 三条 need 逐条登记) "
    "· 主交付页 `SW/ONETRIP_SW_POSTRENAME_GATE_SOP.md` (51,995 B · §0~§9 一节不缺 · 占位符扫描 0) "
    "· `logs/iss327/` (含 24_gate_chain_final.txt · 32_launder_run.log · 30_rev_RT9_launder_path.txt 等 30+ 件原始输出 + 沙盒脚本) "
    "· 分片 `state/fragments/sw.yaml` (iss327 命中 11 条 · 4 条 need 已登记) "
    "★**main 本机实跑复核 (19:1x~19:2x)**: `merge.py` rc=0 (产出 670 · 阻塞 43 · 冲突 0) · `gate_check.py` rc=0 (★**Q1 18/18** · Q2 3/3 · Q3 977 · Q6 ✅ · **Q7 钉板 md5 闸链 9/9**★) · `issue_check.py` rc=0 "
    "⇒ ★**SW 侧 5 道闸本机逐道复跑全绿**: `check_sw_ref_reachability.py` rc=0 (✔ 绿 · 「SW 侧引用的位号全部可达, 真隐患在基线内」) · `check_onepass_sw_sync.py` rc=0 (八条一条不缺且现状值与盘面一致) · "
    "`check_demo_panel_spec.py` rc=0 · `check_landing_trace_obligation.py` rc=0 (每条落表义务都有【文件名+新 md5】) · `check_shutdown_semantics.py` rc=0 (R1~R7 全过) "
    "★**零写板双证**: 板 md5 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413` 逐字节未动 ⇒ **G1 仍开, 不许投板** "
    "★**核心结论 (main 已复核逻辑, 采信它的读数)**: ①「重建注册表」对改名后 SW 闸链**既非必要也非充分** (文档同批改名 ⇒ 旧注册表本就 rc=0/OK 78·DRIFT 0·MISSING 3; 文档不同步时重建 ⇒ 58 条漂移/假红被洗成 56 条真隐患/真红 ⇒ 一样红且更凶) "
    "②「--freeze-registry」**不会**把真隐患洗白 (3 条反向用例: 真隐患改成【从未存在过的新位号形状】⇒ 重建后仍被 C14 抓住 ⇒ MISSING 4 > 上限 3 ⇒ 仍红) "
    "③ 真陷阱 = 【先重建注册表、后同步文档】这个次序 ⇒ **重建时机判据必须晚于 SW 文档同批改名** "
    "★**main 已就它的 3 条 need 逐条拍板并落进 main 自己的分片 (state/fragments/pm.yaml)**: `iss327_decide_registry_rebuild_trigger` = 采纳甲 (固化进改名那一趟固定清单 + 登记义务挂落表单号·ISS-312 既有口径) · "
    "`iss327_decide_missing_baseline_mechanism` = 采纳甲 (保持魔法数 3 · 等真出第 4 条真隐患再转台账式) · `iss327_decide_drift_class_semantics` = 采纳甲 (保留 + 语义写死成「文档与盘面不同步告警」+ 把重建次序写进护栏 · 零改闸) "
    "★**第 4 条 need (`iss327_report_c1_c7_c8_c13_launder_faces`) = C1/C7/C8/C13 四条洗白面 ⇒ 已开 ISS-332 (sw-lead) 交【收紧版闸 + 自测 + 挂闸写法】, 真件闸一个字节不许 agent 改 ⇒ 切不切由 main 拍** "
    "★**并发写入留痕 (必记)**: 本单交卷页在 16:2x~16:43 被一个【并行兄弟 job】的 sw-lead 会话写过 (16:28 那次覆盖把 11 份 `SW/*.md` 改了 ⇒ MISSING 8 > 3 ⇒ 闸 rc=1) ⇒ ★**main 签字时刻 (19:2x) 已确认无并发写者** "
    "(三个总工最新会话 mtime: sw-lead 16:57:24 / hw-lead 17:22:26 / mech-lead 17:21:09 ⇒ 距签字均 ≥ 2 小时) ⇒ **文件已静止, 签字有效** ★"
)

NEW_332 = {
    "id": "ISS-332",
    "title": "★★[主线内·SW 侧·判据收紧类·内部活] 第 8 道闸 (SW 位号引用可达性) 的 C1/C7/C8/C13 四条【洗白面】· 复现 + 收紧方案 (★零改真件闸★)",
    "severity": "high",
    "source_blocker": "ISS-327",
    "source_agent": "sw-lead",
    "desc": ("ISS-327 cont2 实测出第 8 道闸 `SW/tools/check_sw_ref_reachability.py` 的 C1/C7/C8/C13 四条规则各有一条洗白面: "
             "把真隐患 TP_TEMP 改成一个 live 位号名 (RT-5) / 改成含小写 (RT-6) / 改成 SW_ 前缀 (RT-7) / 改成以 _ 结尾 (RT-8) ⇒ 四条都判绿 ⇒ "
             "⇒ 判据对真隐患只有形状检查、没有语义检查 ⇒ 「SW 侧引用的位号全部可达」这句话今天是半假的 ⇒ "
             "⇒ 本单: ① 在沙盒复现 4 条洗白面 + 3 条「真隐患变形状」对照 (证明判据没被洗白) ② 落收紧版闸 `SW/tools/check_sw_ref_reachability_v2.py` + `--selftest` (收紧方向 = 真隐患 token 必须在 BASELINE_TOKENS 里登记过才算白名单) "
             "③ 交 main 切闸/挂闸写法 (★改真件闸与改 state/gate_check.py 都是 main 的机制地界★)"),
    "owner": "sw-lead",
    "reporter": "main",
    "raised": "2026-11-18",
    "due": "2026-11-20",
    "status": "fixing",
    "external": False,
    "need_keys": [],
    "task_brief": BRIEF_332,
    "fix_ref": ("SW/tools/check_sw_ref_reachability_v2.py (★新建★) · SW/tools/check_sw_ref_reachability_v2_selftest.py (★新建★) · "
                "HANDOFF/2026-11-18_sw-lead_ISS332_SW位号可达性闸4条洗白面收紧.md (★新建★) · logs/iss333 之外的 logs/iss332/ (★新建★)"),
    "verify_by": "main",
    "verify_result": None,
    "verify_date": None,
    "note": ("★2026-11-18 19:2x 项目总工登记: ISS-327 落地时把它交回的第 4 条 need (`iss327_report_c1_c7_c8_c13_launder_faces`) 转成执行单 ⇒ "
             "★**main 已拍板: 要收紧 + 收紧方向 = 「真隐患 token 必须在 BASELINE_TOKENS 里登记过才算白名单」+ 但真件 `SW/tools/check_sw_ref_reachability.py` 一行都不许 agent 改** ⇒ "
             "⇒ 本单只交【收紧版新文件 + 自测 + 切闸/挂闸写法】, main 执行切换 ⇒ "
             "★**新开即派出 (status 直接落 fixing ⇒ 无 open 窗口 ⇒ 兄弟 job 775d9893 不会重复派)** ★"),
    "dispatched_at": NOW,
}

NEW_333 = {
    "id": "ISS-333",
    "title": "★★[主线内·MECH 侧·闸实现类·内部活] MECH 侧位号可达性闸 · 从【设计稿】到【可直接挂的闸】的实现单 (★零改 state/gate_check.py·★挂闸由 main 执行★)",
    "severity": "high",
    "source_blocker": "ISS-326",
    "source_agent": "mech-lead",
    "desc": ("ISS-326 (verified) 交卷的设计稿 `logs/iss326/gate_design/GATE_DESIGN.md` (13,443 B) + 基线 `mech_gate_baseline.json` (22,472 B) + 原型 `mech_gate_proto.py` (9,032 B) "
             "⇒ ★**只到设计稿, 那道闸至今还没挂进门禁链** ⇒ MECH 域的位号引用漂移今天仍抓不到 ⇒ "
             "⇒ 本单: ① 把原型变成真闸 `MECH/tools/check_mech_ref_reachability.py` (自带 --selftest) ② 自己 fresh 复现建闸日基线 (ISS-326 实测 16 · SW 侧是 3 · 不许抄) + 反向用例 ≥5 (含假绿那条) ③ 交 main 挂闸写法 (EXTRA_GATES 第几位/行号/自检期望) ⇒ main 执行挂闸 (ISS-330 owner=main)"),
    "owner": "mech-lead",
    "reporter": "main",
    "raised": "2026-11-18",
    "due": "2026-11-20",
    "status": "fixing",
    "external": False,
    "need_keys": [],
    "task_brief": BRIEF_333,
    "fix_ref": ("MECH/tools/check_mech_ref_reachability.py (★新建★) · "
                "HANDOFF/2026-11-18_mech-lead_ISS333_MECH侧位号可达性闸实现.md (★新建★) · logs/iss333/ (★新建★)"),
    "verify_by": "main",
    "verify_result": None,
    "verify_date": None,
    "note": ("★2026-11-18 19:2x 项目总工登记: ISS-326 落地时发现它的设计稿【还没挂进门禁链】⇒ "
             "★**main 已拍板: 挂闸是 main 的机制地界 (ISS-330 owner=main) ⇒ 本单只出【可挂的闸脚本 + 自测 + 挂闸写法】, agent 一个字节都不许改 `state/gate_check.py`** ★ "
             "★**main 已定死的硬要求 (全部来自 ISS-326 实测, 一条都不许放宽)**: fail-closed 三条 · 基线必须 MECH 侧自己 fresh 测 (16, 不许抄 SW 的 3) · 反向用例 ≥5 (必须含假绿那条) · 扫描面 MECH/**/*.py + MECH/**/*.md 递归 · 基线只许收紧不许放宽 "
             "★**新开即派出 (status 直接落 fixing ⇒ 无 open 窗口 ⇒ 兄弟 job 775d9893 不会重复派)** ★"),
    "dispatched_at": NOW,
}


def main() -> int:
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        log = yaml.safe_load(open(LOG, encoding="utf-8")) or {}
        issues = log.get("issues") or []
        idx = {i.get("id"): i for i in issues}
        applied = []

        # ① ISS-327 落地
        i327 = idx.get("ISS-327")
        if not i327:
            print("· ISS-327 不存在 (异常)")
            return 1
        if i327.get("status") != "verified":
            i327["status"] = "verified"
            i327["verify_result"] = VERIFY_327
            i327["verify_date"] = NOW
            i327["verify_by"] = "main"
            applied.append("ISS-327 fixing → verified (★main 19:2x 本机独立复核★)")
        else:
            applied.append("ISS-327 已是 verified (跳过)")

        # ② ISS-328 cont1 重派 (status 保持 fixing)
        i328 = idx.get("ISS-328")
        if not i328:
            print("· ISS-328 不存在 (异常)")
            return 1
        tb = i328.get("task_brief") or ""
        if "ISS-328 · hw-lead · ★★cont1 续做" not in tb:
            i328["task_brief"] = tb + "\n\n---\n\n" + BRIEF_328_CONT
            applied.append("ISS-328 task_brief += cont1 (★原 brief 全文保留★) · status 保持 fixing")
        else:
            applied.append("ISS-328 cont1 已在 brief 里 (跳过)")
        i328["dispatched_at"] = NOW
        i328["note"] = (str(i328.get("note") or "") + " ★★2026-11-18 19:2x · cron fb67af40 重派 cont1★★ "
                        "★**上一趟 17:0x~17:2x 中途断线 (★子会话最后一条 17:22 停在写右上臂 PCB_PART_POS 脚本★) ⇒ "
                        "★**但成果已在盘上**: 第 ② 件 TP no-op 复测【已答完】(官方链排版阶段实测: 钉 vs 不钉 10 条 TP_DSI_* 落位【不一样】·差异行数 = 16 ⇒ ⇒ **不是 no-op** ⇒ main 的 P-1「20 条串删回 10 条」维持【一条都不许删】) "
                        "+ 第 ① 件的硬前置【已过】(右上臂 vs 基线臂 全板 185 封装落位 diff = 102 ⇒ ≠ 0 ⇒ 对照有效) + 三块排版阶段板 + 两条臂脚本 (tmp/iss328/run_ru_arm.sh 等) 全在盘 ⇒ "
                        "★**⇒ 本单 = 续做 (起链跑右上臂 + 收读数 + 写两页交付物 + 写分片), 不是从零重做**★").strip()

        # ③ 新开 ISS-332 / ISS-333 (直接落 fixing ⇒ 立刻派出)
        for new in (NEW_332, NEW_333):
            if new["id"] in idx:
                applied.append("%s 已存在 (跳过)" % new["id"])
                continue
            issues.append(new)
            idx[new["id"]] = new
            applied.append("%s 已登记 (owner=%s · status=fixing · 新开即派出)" % (new["id"], new["owner"]))

        out = dict(log)
        out["issues"] = issues
        shutil.copy2(LOG, LOG + ".bak_cronfb67_%s_land327_open332_333" % STAMP)
        atomic_write(LOG, yaml.safe_dump(out, allow_unicode=True, sort_keys=False, width=100000))

        # ④ dispatch_log
        dl = yaml.safe_load(open(DL, encoding="utf-8")) or {}
        disp = dl.get("dispatches") or []
        tag = "★**19:2x cont1 重派 (★上一趟 17:0x~17:2x 中途断线·成果已在盘·续做不是从零★)** ★"
        if not any(isinstance(d, dict) and d.get("issue") == "ISS-328" and "19:2x cont1" in str(d.get("brief")) for d in disp):
            disp.append({
                "issue": "ISS-328", "agent": "hw-lead", "at": NOW,
                "brief": tag + "★**成果已在盘**: 第 ② 件 TP no-op 已答完 (官方链排版阶段: 钉 vs 不钉 10 条 TP_DSI_* 落位 diff = 16 ⇒ **不是 no-op** ⇒ P-1 的 20 条串一条都不许删) + 硬前置 diff = 102 已过 + 三块排版板 + 两条臂脚本 ⇒ ★**只剩: 起链跑右上臂 + 收读数 + 写两页 + 写分片** ★ "
                          "★**任务书全文**: `state/dispatch_briefs/ISS-328_hw_rightupper_control_arm_cont1.md` (5,788 B · `check_brief_commands.py --brief-file` rc=0) ★ "
                          "★**边界**: 零写板 (板 md5 611b869e… + mtime 2026-11-06 07:07:17.362193413) · 零落表 · 零改闸 · 零改生成器 · 沙盒只写 tmp/iss328 + logs/iss328 · 只写 state/fragments/hw.yaml · 零外发 · 不替老板拍板 ★",
                "job": "cron fb67af40 (ARS45 队列自动派活) · ★派活时刻 2026-11-18 19:2x · ★**status 全程 fixing ⇒ 无 open 窗口 ⇒ 兄弟 job 775d9893 不会重复派** ★",
            })
        if not any(isinstance(d, dict) and d.get("issue") == "ISS-332" for d in disp):
            disp.append({
                "issue": "ISS-332", "agent": "sw-lead", "at": NOW,
                "brief": "★**新开单 + 直接派出 (status 直接落 fixing)** ★ ★**开单依据**: ISS-327 落地时它交回的第 4 条 need (`iss327_report_c1_c7_c8_c13_launder_faces`) ⇒ 第 8 道闸的 C1/C7/C8/C13 各有一条洗白面 (RT-5/RT-6/RT-7/RT-8) ⇒ 判据对真隐患只有形状检查没有语义检查 ⇒ main 已拍板「要收紧 + 方向 = 真隐患 token 必须在 BASELINE_TOKENS 登记过才算白名单」★ ★**任务书全文**: `state/dispatch_briefs/ISS-332_sw_ref_reach_launder_reverse_cases.md` (6,001 B · `check_brief_commands.py --brief-file` rc=0) ★ ★**边界**: 零写板 · 零落表 · **零改真件 `SW/tools/check_sw_ref_reachability.py`** (只出 v2 新文件) · 零改 `state/gate_check.py` · 零改既有 SW 文档正文 · 沙盒只写 tmp/iss332 + logs/iss332 · 只写 state/fragments/sw.yaml · 零外发 · 不替老板拍板 ★",
                "job": "cron fb67af40 (ARS45 队列自动派活) · ★派活时刻 2026-11-18 19:2x · ★**status 全程 fixing ⇒ 无 open 窗口** ★",
            })
        if not any(isinstance(d, dict) and d.get("issue") == "ISS-333" for d in disp):
            disp.append({
                "issue": "ISS-333", "agent": "mech-lead", "at": NOW,
                "brief": "★**新开单 + 直接派出 (status 直接落 fixing)** ★ ★**开单依据**: ISS-326 (verified) 的设计稿 + 基线 + 原型全在盘, 但那道 MECH 侧位号可达性闸【还没挂进门禁链】⇒ MECH 域位号引用漂移今天仍抓不到 ⇒ ★**挂闸是 main 的机制地界 (ISS-330 owner=main) ⇒ 本单只出【可挂的闸脚本 + 自测 + 挂闸写法】** ★ ★**任务书全文**: `state/dispatch_briefs/ISS-333_mech_designator_gate_hook_prep.md` (6,208 B · `check_brief_commands.py --brief-file` rc=0) ★ ★**边界**: 零写板 · 零落表 · 零改 `state/gate_check.py` · 零改 `SW/tools/check_sw_ref_reachability.py` (只读 import) · 零改既有 MECH/*.md 与 MECH/*.py · 零改 logs/iss326 (已落证据) · 沙盒只写 tmp/iss333 + logs/iss333 · 只写 state/fragments/mech.yaml · 零外发 · 不替老板拍板 ★",
                "job": "cron fb67af40 (ARS45 队列自动派活) · ★派活时刻 2026-11-18 19:2x · ★**status 全程 fixing ⇒ 无 open 窗口** ★",
            })
        out2 = dict(dl)
        out2["dispatches"] = disp
        shutil.copy2(DL, DL + ".bak_cronfb67_%s_land327_open332_333" % STAMP)
        atomic_write(DL, yaml.safe_dump(out2, allow_unicode=True, sort_keys=False, width=100000))

        for a in applied:
            print("· " + a)
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
