#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
★★【本脚本已于 2026-11-22 21:5x 被自己的 assert 挡住 · 勿盲目重跑】★★
ISS-339 已由兄弟 job cron 775d9893 于 2026-11-22 21:51 签收 (fixing → verified) ⇒ 本脚本的 `assert it.get("status") == "fixing"` 当场挡住 ⇒ 零双写 · 零覆盖 · issue_log.yaml 未被本脚本碰过。
★★ 重跑本脚本 = 再被 assert 挡住 (status 已是 verified) ⇒ 无害, 但也无用。
★★ 真正的签收正文在 state/issue_log.yaml (ISS-339.verify_result) 与 state/dispatch_log.yaml (同一条签收记录)。
"""
_apply_20261122_2150_cronfb67_sign_iss339.py
================================================
cron fb67af40 (ARS45 队列自动派活) 2026-11-22 21:5x 本机实跑 ⇒ 一件事:

【清僵尸 fixing】ISS-339 交卷已完成 (子会话 `35c16b5d` / runId `b91835c0` · status=done @21:35:50)
   ⇒ 但 `state/issue_log.yaml` 里它还停在 `fixing` ⇒ ★**僵尸 fixing** ★
   ⇒ ★**危害**: `state/advance.py` 的 in_flight 规则 = "该 agent 名下已有 status==fixing ⇒ 本轮不再给它派新活"
      ⇒ hw-lead 的名额被一个【已交卷】的单永久占住 ⇒ ★**队列断线** ★
   ⇒ 本单 = 派活方按项目惯例做【签收 + 清僵尸】(★签收依据 = 本机独立复核·不抄 agent 报告★)

★**签收依据 (本机实跑, 逐条)**:
  ① `python3 HW/check_board_comparable_gate.py --selftest` ⇒ rc=0 · 末行 `ALL TESTS PASS`
     · 用例 0 常量自检 (真值 = tmp/iss337/seg_parity_selfcheck.py L59-61): SEG [2300,3200] · CU [4600,5900] · VIA [380,520] 全对
     · 用例 1 正向: 官方终板 raw=18092 norm=2649 via=433 cu=5726.9mm ⇒ 放行 (★新口径不把官方板自己判成不可比★)
     · 用例 2 决定性: 合成带外板 (norm=2/via=1/cu=6.0) ⇒ 被拦 · ★v44 实测坏臂板 (norm=2280/via=371/cu=4568.5) 三项全低于下界 ⇒ 被拦★
     · 用例 3 综合判据: v44 = 拒 (★靠可比性层直接抓, 名单层另独立命中 19 条必需零铜网 ⇒ 双保险★)
  ② `python3 HW/check_s8_target_list.py HW/PCB/demo_mainboard.kicad_pcb --baseline state/.lastgood/best_v76mg1_clrfix.kicad_pcb` ⇒ rc=0
     · N' = 45 (本板自己跑 DRC · 非照抄) · 分母口径① 全部网: 本板 21 / 参照 4 · 口径② pad≥2: 本板 24 / 参照 7
     · 两边都零铜 (pad≥2) = 3 条: CSI_D0_D0_N_SRC / CSI_D0_D2_N / CSI_D0_D3_N
  ③ `python3 state/merge.py` ⇒ rc=0 · `python3 state/gate_check.py` ⇒ rc=0 · ★**Q1 = 18/18**★ · Q2 3/3 · Q7 9/9 · hw-lead 6/6 缺: 无
  ④ 板 md5 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413` ⇒ 逐字节未动 ⇒ ★**G1 仍开, 不许投板** ★
  ⑤ 零改闸: `state/gate_check.py` `5ccdcd5f…` · `state/compare_arm_official.py` `1471bce6…` · `state/chain_gate.py` `7644a3d3…` · `state/check_pcb_drc.py` `1088fa4f…`
     ⇒ ★与 main 2026-11-22 21:16 记录的 md5 逐字同 ⇒ 闸脚本一个字节没动 ★
  ⑥ 交卷页 `HANDOFF/2026-11-22_hw-lead_ISS339_可比性前置闸与S8目标名单.md` (26,988 B @21:34) ⇒ B0~B7 八块齐全
     · 占位符/未闭合标记 grep = 0 · 页面引用 24 个路径逐个在盘 ⇒ 0 MISS (★2 处 `logs/iss339/0[12]_...txt` 是缩略写法, 同页 L56/L57/L241 有全名★)
  ⑦ 分片 `state/fragments/hw.yaml` (604,933 B @21:32 · 走 frag_write.py 原子写) ⇒ `grep -c iss339` = **16** ·
     ★sw.yaml / mech.yaml / pm.yaml 一个字节没被碰 (mtime 分别 11-19 01:42 / 11-19 01:21 / 11-22 21:16★) ⇒ 零写别人的分片

★**签字边界**: ★本单只签"agent 已交卷 + 机械门全绿" ⇒ 落 `fixing → verified` (★`verify_by: main`·★本轮由 main 的派活 cron 代签★)
★**两条 main 级 need 留给【板那一趟】开工会拍 (★不在本单签, 也不替老板拍★)**:
   · `iss339_gate_chain_mount` = 可比性前置闸要不要挂进 `state/gate_check.py` 的 EXTRA_GATES (agent 建议 ③ warning)
   · `iss339_baseline_lock` = 板那一趟参照板锁哪块 (agent 建议 `state/.lastgood/best_v76mg1_clrfix.kicad_pcb`)

边界 (一条都不破):
  ★零写板   ★零落表 (网表/脚表/BOM 不动)   ★零改闸   ★零改真生成器   ★零外发   ★不替老板拍板   ★不自签别人分片
"""
import os
import shutil
import sys
import time

import yaml

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
LOG = os.path.join(PROJ, "state/issue_log.yaml")
DLOG = os.path.join(PROJ, "state/dispatch_log.yaml")
STAMP = time.strftime("%Y%m%d_%H%M")

VERIFY = (
    "✅ verified (★main 2026-11-22 21:48~21:52 本机独立复核·不抄 agent 报告★ · "
    "★由派活 cron fb67af40 代签 (★清僵尸 fixing·★签收依据 = 本机实跑·非 agent 自证★)★) "
    "⇒ 交卷物在盘: · 交卷页 `HANDOFF/2026-11-22_hw-lead_ISS339_可比性前置闸与S8目标名单.md` (26,988 B @2026-11-22 21:34 · B0~B7 八块齐全) · "
    "闸脚本 `HW/check_board_comparable_gate.py` (25,924 B @21:31) + `HW/check_s8_target_list.py` (21,381 B @21:29) · "
    "口径页 `HW/PCB/S8_TARGET_LIST_AND_COMPARABILITY.md` (14,435 B @21:31) · 证据 `logs/iss339/` (5 份原文) · "
    "分片 `state/fragments/hw.yaml` (604,933 B @21:32 · `grep -c iss339` = **16** · 零重复 key) ★ "
    "★**main 本机独立复跑 (21:48~21:52)**★: "
    "① `python3 HW/check_board_comparable_gate.py --selftest` ⇒ rc=0 · 末行 `ALL TESTS PASS` "
    "(★用例 0 常量自检对 `tmp/iss337/seg_parity_selfcheck.py` L59-61 真值: SEG [2300,3200] · CU [4600,5900] · VIA [380,520]; "
    "用例 1 官方终板 18092/2649/433/5726.9 放行; ★用例 2 v44 实测坏臂板 norm=2280/via=371/cu=4568.5 三项全低于下界 ⇒ 被可比性层直接拦; "
    "用例 3 v44 综合判据 = 拒 (★名单层另独立命中 19 条必需零铜网 ⇒ 双保险★)★) "
    "② `python3 HW/check_s8_target_list.py HW/PCB/demo_mainboard.kicad_pcb --baseline state/.lastgood/best_v76mg1_clrfix.kicad_pcb` ⇒ rc=0 "
    "(★N'=45 本板自己跑 DRC 非照抄 · 口径① 全部网 本板 21/参照 4 · 口径② pad≥2 本板 24/参照 7 · 两边都零铜 3 条: CSI_D0_D0_N_SRC / CSI_D0_D2_N / CSI_D0_D3_N★) "
    "③ `state/merge.py` rc=0 (产出 712 · 阻塞 43 高危 33 · 未闭合 340 · 冲突 0) · `state/gate_check.py` rc=0 (★Q1 **18/18** · Q2 3/3 · Q7 9/9 · hw-lead 6/6 缺: 无★) "
    "④ 板 md5 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413` 逐字节未动 ⇒ **G1 仍开, 不许投板** "
    "⑤ 零改闸: `gate_check.py` `5ccdcd5f…` · `compare_arm_official.py` `1471bce6…` · `chain_gate.py` `7644a3d3…` · `check_pcb_drc.py` `1088fa4f…` "
    "⇒ 与 main 21:16 记录逐字同 ⇒ 闸脚本一个字节没动 "
    "⑥ 交卷页 B0~B7 八块齐全 · 占位符/未闭合标记 grep = **0** · 页面引用 24 个路径逐个在盘 ⇒ **0 MISS** "
    "★ **★★agent 三处偏差如实保留 (★签收不抹掉·不代它解释★)★★★**: "
    "① D1 写完没立刻跑 selftest, 先起了后台 `--prime-cache` 预热 (归一化 18092 段要 1~2 分钟), 预热完 selftest 只跑 1 次 ⇒ 判据本体仍被完整自测覆盖 (main 自己复跑 rc=0) "
    "② D2 跑了 2 次 (第 2 次是改解析器后的回归, 24/21/45/3 条/分级逐字不变才往下走) "
    "③ 清理 `HW/__pycache__` 时把 11-18 就存在的字节码缓存目录删了 (纯编译缓存·不影响任何闸·main 复跑全绿) ★ "
    "★**★签字边界★**: 本单只签「agent 已交卷 + 机械门全绿」⇒ 落 `fixing → verified` (★`verify_by: main`·由 main 的派活 cron 代签★); "
    "★**两条 main 级 need 留给【板那一趟】开工会拍 (★不在本单签·不替老板拍★)**: `iss339_gate_chain_mount` (可比性前置闸要不要挂进 gate_check.py 的 EXTRA_GATES · agent 建议 ③ warning) · "
    "`iss339_baseline_lock` (板那一趟参照板锁哪块 · agent 建议 `state/.lastgood/best_v76mg1_clrfix.kicad_pcb`) ★"
)

NOTE_ADD = (
    "\n★**2026-11-22 21:5x · cron fb67af40 (队列自动派活) 清僵尸 fixing + 代签收 (★main 本机独立复核·不抄 agent 报告★)** ★\n"
    "★**背景**: 本单由 cron 775d9893 于 2026-11-22 21:30 派出 (子会话 `35c16b5d` / runId `b91835c0`) ⇒ "
    "该子会话于 **21:35:50 status=done 交卷完成** ⇒ ★但本条状态还停在 `fixing` ⇒ 僵尸 fixing ⇒ "
    "★**危害**: `state/advance.py` 的 in_flight 规则 (该 agent 名下有 fixing ⇒ 本轮不派新活) 会让 hw-lead 的名额被一个【已交卷】的单永久占住 ⇒ **队列断线** ★\n"
    "★**处置**: ★**不是回滚成 open** (★agent 已交卷·回滚重派 = 重复劳动·且会覆盖已落盘的闸★) ⇒ ★**按项目惯例签 `fixing → verified`** ★\n"
    "★**本轮 A 段派活结果**: `python3 state/advance.py --json` ⇒ **internal = []** ⇒ ★**无单可派** ★ "
    "⇒ 原因 = ★**issue_log 里 16 条 open 全是 boss(5)/main(11) 自留·三个总工名下零 open** ★ (★hw-lead 的 `fixing` 槽位被本单占着·本轮清掉后仍无 open 单★) ⇒ "
    "★**派活方不开新单** (★开新单是 cron 775d9893 的地界·且『板只改一次』那一趟还卡着 7 条老板决策 + 板厚/层数/U-1 三件前置★) ★\n"
    "★**留给下一轮 (★派活方 + 775d 两边都要接★)**: "
    "① ★**hw-lead 名额已释放** (本条 verified ⇒ 下轮 advance.py 能给它派新单) ★ "
    "② 两条 main 级 need (`iss339_gate_chain_mount` / `iss339_baseline_lock`) 在【板那一趟】开工会拍 "
    "③ ★**板那一趟开工前仍必须**: ① 在真实基线板上重读 unc 分母 (N' ≠ 45) ② 7 条老板决策 ③ `q3_storage_and_audio` (外挂 eMMC 须在开工前进网表·否则板 md5 变第二次) ★\n"
)


def atomic_write(path: str, text: str) -> None:
    tmp = path + ".tmp_%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
    dfd = os.open(os.path.dirname(path), os.O_RDONLY)
    try:
        os.fsync(dfd)
    finally:
        os.close(dfd)


def main() -> int:
    # ---- 备份 ----
    b1 = LOG + ".bak_%s_cronfb67_sign_iss339" % STAMP
    b2 = DLOG + ".bak_%s_cronfb67_sign_iss339" % STAMP
    shutil.copy2(LOG, b1)
    shutil.copy2(DLOG, b2)
    print("backup:", os.path.basename(b1))
    print("backup:", os.path.basename(b2))

    # ---- issue_log: ISS-339 fixing -> verified ----
    with open(LOG, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    hit = 0
    for it in data.get("issues", []):
        if it.get("id") == "ISS-339":
            assert it.get("status") == "fixing", "ISS-339 不是 fixing, 拒绝盲签: %r" % it.get("status")
            it["status"] = "verified"
            it["verify_by"] = "main"
            it["verify_result"] = VERIFY
            it["verify_date"] = "2026-11-22"
            it["fix_ref"] = (
                "HW/check_board_comparable_gate.py · HW/check_s8_target_list.py · "
                "HW/PCB/S8_TARGET_LIST_AND_COMPARABILITY.md · "
                "HANDOFF/2026-11-22_hw-lead_ISS339_可比性前置闸与S8目标名单.md · logs/iss339/"
            )
            it["note"] = (it.get("note") or "") + NOTE_ADD
            hit += 1
    assert hit == 1, "ISS-339 命中数异常: %d" % hit
    atomic_write(LOG, yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=10 ** 6))
    print("issue_log: ISS-339 -> verified")

    # ---- dispatch_log: 记一条签收 ----
    with open(DLOG, encoding="utf-8") as f:
        dlog = yaml.safe_load(f)
    if not isinstance(dlog, list):
        dlog = dlog.get("dispatches", []) if isinstance(dlog, dict) else []
    dlog.append({
        "issue": "ISS-339",
        "agent": "hw-lead",
        "at": "2026-11-22 21:5x",
        "brief": (
            "★2026-11-22 21:5x 项目总工签收 (★cron fb67af40 代签·★本机独立复核·不抄 agent 报告★): "
            "★**清僵尸 fixing** (★子会话 `35c16b5d` / runId `b91835c0` 21:35:50 status=done 已交卷, 但 issue_log 里还停在 `fixing` ⇒ "
            "★`advance.py` 的 in_flight 规则会永久占住 hw-lead 名额 ⇒ 队列断线★) ⇒ 落 `fixing → verified` (★**不回滚成 open**: agent 已交卷·回滚重派=重复劳动★) ★ "
            "★**复核 7 项 (本机实跑)**: ① `HW/check_board_comparable_gate.py --selftest` rc=0 末行 `ALL TESTS PASS` "
            "(★v44 实测坏臂板 norm=2280/via=371/cu=4568.5 三项全低于下界 ⇒ 被可比性层直接拦★) "
            "② `HW/check_s8_target_list.py <板> --baseline <v76mg1>` rc=0 ⇒ N'=45 · 口径② 本板 24/参照 7 · 两边都零铜 3 条 "
            "③ `merge.py` rc=0 · `gate_check.py` rc=0 ★**Q1 18/18**★ · Q7 9/9 · hw-lead 6/6 缺: 无 "
            "④ 板 md5 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413` 逐字节未动 ⇒ **G1 仍开, 不许投板** "
            "⑤ 零改闸 (4 个闸脚本 md5 与 main 21:16 记录逐字同) ⑥ 交卷页 26,988 B · B0~B7 八块齐全 · 占位符 0 · 引用 24 路径 0 MISS "
            "⑦ 分片只写 hw.yaml (`grep -c iss339`=16) · sw/mech/pm 三个分片一个字节没被碰 ★ "
            "★**本轮 A 段派活 = 0 条** (★`advance.py --json` ⇒ internal=[] ⇒ issue_log 里 16 条 open 全是 boss(5)/main(11) 自留·三个总工名下零 open★) "
            "★**两条 main 级 need 留给【板那一趟】开工会拍** (`iss339_gate_chain_mount` / `iss339_baseline_lock`) · ★零外发 · 不替老板拍板 ★"
        ),
    })
    atomic_write(DLOG, yaml.safe_dump(dlog, allow_unicode=True, sort_keys=False, width=10 ** 6))
    print("dispatch_log: +1 条签收记录")
    return 0


if __name__ == "__main__":
    sys.exit(main())
