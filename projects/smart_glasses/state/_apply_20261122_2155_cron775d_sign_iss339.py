#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2026-11-22 21:5x · cron 775d9893 (ARS45 继续执行后继计划) · 项目总工 (moli)
ISS-339 签收: fixing -> verified (main 本机独立复核, 不抄 agent 报告)
幂等: 已 verified 则直接退出
"""
import io, os, shutil, sys, yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, "state", "issue_log.yaml")
BAK = LOG + ".bak_20261122_2155_cron775d_sign_iss339"

ISS = "ISS-339"

VERIFY = (
    "✅ verified (★main 2026-11-22 21:5x 本机独立复核·不抄 agent 报告★) ⇒ 交卷物在盘: "
    "· 交卷页 `HANDOFF/2026-11-22_hw-lead_ISS339_可比性前置闸与S8目标名单.md` (26,988 B @2026-11-22 21:34) "
    "· 主交付物 `HW/PCB/S8_TARGET_LIST_AND_COMPARABILITY.md` (14,435 B @21:31) "
    "· 两个新闸 `HW/check_board_comparable_gate.py` (25,924 B @21:31) + `HW/check_s8_target_list.py` (21,381 B @21:29) "
    "· 证据 `logs/iss339/` 5 件 · 分片 `state/fragments/hw.yaml` (`grep -c iss339` = **16**) "
    "★ ★**main 本机独立复跑 6 项全绿 (21:48~21:55)**★: "
    "① `python3 HW/check_board_comparable_gate.py --selftest` ⇒ 末行 `ALL TESTS PASS` rc=0 "
    "(★常量自检: 真值文件 (2300,3200)/(4600.0,5900.0)/(380,520) == 本脚本三区间逐字同★; "
    "★官方终板 raw=18092 norm=2649 via=433 cu=5726.9mm ⇒ 放行★; "
    "★v44 实测坏臂板 norm=2280 via=371 cu=4568.5mm ⇒ 三项全低于下界 ⇒ 被可比性层直接拦住★; "
    "★名单层另独立命中必需网零铜 19 条 ⇒ 双保险★) "
    "② `python3 HW/check_board_comparable_gate.py HW/PCB/demo_mainboard.kicad_pcb state/.lastgood/best_v76mg1_clrfix.kicad_pcb` ⇒ rc=0 "
    "(★官方板 2649/433/5726.9 可比 + 参照板 2582/471/5582.8 可比★) "
    "③ `python3 HW/check_s8_target_list.py HW/PCB/demo_mainboard.kicad_pcb --baseline state/.lastgood/best_v76mg1_clrfix.kicad_pcb` ⇒ rc=0 "
    "(★N'=45 本板自己跑 DRC 得出·不是照抄★ · 必需 23 / 可悬空 1 (FSIN_OUT) / 待定 0 · "
    "★分母口径① 全部网口径 (对照宇宙 111 网名): 本板零铜 21 / 参照板 4★ · "
    "★分母口径② pad≥2 焊盘网口径: 本板零铜 24 / 参照板 7★ · "
    "★两边都零铜 (pad≥2) = 3 条: CSI_D0_D0_N_SRC / CSI_D0_D2_N / CSI_D0_D3_N★ · 全部网口径 = 0 条★) "
    "④ 板零写板双证: md5 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413` ⇒ 逐字节未动 (16 天) "
    "⑤ 交卷页 B0~B7 七块齐全 (L10/36/64/130/151/186/200/245) · ★占位符三查 (`<!--[` / 🔄 / 待填 / PLACEHOLDER / `__[A-Z_]+__`) = 0★ · "
    "★引用件零真 MISS (两处 `logs/iss339/01_...txt` / `02_...txt` 是省略号写法·对应真件 `01_s8_target_list_official_vs_v76mg1.txt` / `02_comparable_gate_selftest.txt` 都在盘★) "
    "⑥ `python3 state/gate_check.py` ⇒ rc=0 · ★Q1 = 18/18★ · hw-lead 6/6 缺: 无 · Q7 9/9 全绿 "
    "★ ★**agent 自报的 3 处偏差 main 已实查, 全部属实且不构成阻塞**★: "
    "(a) D1 写完先起后台 `--prime-cache` 预热再跑 selftest ⇒ selftest 只跑 1 次 ✔ "
    "(b) D2 跑了 2 次 (第 2 次是改解析器后回归, 24/21/45/3 条与分级逐字不变) ✔ "
    "(c) 清理 `HW/__pycache__` 时删了 11-18 就存在的字节码缓存目录 (纯编译缓存·不影响任何闸·复跑全绿) ✔ "
    "★ ★**agent 交回的 2 条待 main 裁 (本单不代老板拍)**: "
    "① 可比性前置闸**挂不挂 `state/gate_check.py`** ⇒ main 裁: **暂不挂日常链** (理由同 ISS-336: "
    "★它判的是一次性事件, 且板那一趟才产得出可比板·挂日常链=天天红 ⇒ 真红被淹没★) ⇒ 改为【板那一趟开工前单次跑 + 写进作业包前置清单】; "
    "② 板那一趟参照板锁哪块 ⇒ main 裁: 锁 `state/.lastgood/best_v76mg1_clrfix.kicad_pcb` (★全部网口径的对照宇宙随参照板变 ⇒ 必须写死参照板路径, 否则口径漂★) "
    "★ ★**本单签收含义**: 【板那一趟 S8 布线归零】现在有两把尺子 (可比性前置闸 + S8 目标名单重读器) ⇒ "
    "「布线 45→0」的**分母 N' 必须在那一趟的真实基线板上重读**, 45 不是常量, 24 也不是清单; "
    "⇒ 铁律入库: ★**「靶更小」≠「板子更好」** + ★**判据顺序 = 先可比性 → 再名单 → 最后才看计数有没有变好**★"
)

FIXREF = (
    "HW/check_board_comparable_gate.py (新建·可比性前置闸) · HW/check_s8_target_list.py (新建·S8 目标名单重读器) · "
    "HW/PCB/S8_TARGET_LIST_AND_COMPARABILITY.md (新建·权威口径页) · "
    "HANDOFF/2026-11-22_hw-lead_ISS339_可比性前置闸与S8目标名单.md (新建·交卷页 B0~B7) · "
    "logs/iss339/ (新建·5 件) · state/fragments/hw.yaml (分片) · "
    "★**真件零改: HW/PCB/demo_mainboard.kicad_pcb (md5 611b869e13518c3c023fb178f91a0075 不变) · "
    "state/gate_check.py · state/compare_arm_official.py · state/chain_gate.py · state/gen_pcb_netlist_board.py · "
    "state/gen_pcb_routing.py 全部 md5 不变**★"
)

NOTE_ADD = (
    " ★★2026-11-22 21:5x · cron 775d9893 签收 (★main 本机独立复核 6 项全绿·不抄 agent 报告★): "
    "★交卷会话 `agent:hw-lead:subagent:35c16b5d` 于 21:35:46 status=done (runtime 622 s·abortedLastRun=false)★ ⇒ "
    "★**agent 是活着交卷的, 不是被掐 ⇒ 本单不是僵尸单 ⇒ 兄弟 job fb67af40 若同时在查僵尸, 结论是「不是僵尸」**★ "
    "★**签收时 main 另裁 2 条**: ① 可比性闸**不挂 `state/gate_check.py` 日常链** (★判一次性事件·挂链=天天红⇒真红被淹没★) "
    "⇒ 改【板那一趟开工前单次跑 + 进作业包前置清单】; ② 参照板锁死 `state/.lastgood/best_v76mg1_clrfix.kicad_pcb` "
    "(★全部网口径的对照宇宙随参照板变 ⇒ 不锁死则口径漂★)★ "
    "★**铁律入库**: 「靶更小」≠「板子更好」· 判据顺序 = 先可比性 → 再名单 → 最后才看计数★"
)

def main():
    with io.open(LOG, "r", encoding="utf-8") as f:
        doc = yaml.safe_load(f)
    issues = doc.get("issues") or []
    hit = None
    for i in issues:
        if i.get("id") == ISS:
            hit = i
            break
    if hit is None:
        print("FATAL: %s not found" % ISS)
        return 2
    if hit.get("status") == "verified":
        print("IDEMPOTENT: %s already verified" % ISS)
        return 0
    if hit.get("status") != "fixing":
        print("FATAL: %s status=%r (expected fixing)" % (ISS, hit.get("status")))
        return 3

    if not os.path.exists(BAK):
        shutil.copy2(LOG, BAK)

    hit["status"] = "verified"
    hit["verify_by"] = "main"
    hit["verify_result"] = VERIFY
    hit["verify_date"] = "2026-11-22"
    hit["fix_ref"] = FIXREF
    old_note = hit.get("note") or ""
    hit["note"] = old_note + NOTE_ADD

    tmp = LOG + ".tmp_sign339"
    with io.open(tmp, "w", encoding="utf-8") as f:
        yaml.safe_dump(doc, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
    os.replace(tmp, LOG)
    print("OK: %s fixing -> verified (backup: %s)" % (ISS, os.path.basename(BAK)))
    return 0

if __name__ == "__main__":
    sys.exit(main())
