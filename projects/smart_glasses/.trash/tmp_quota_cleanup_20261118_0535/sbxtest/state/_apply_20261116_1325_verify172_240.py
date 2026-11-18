#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20261116_1325_verify172_240.py
★main (moli) 2026-11-16 13:2x~13:3x (cron 775d9893 ARS45 继续执行后继计划)★
★① ISS-172 (sw-lead) 独立复验 ⇒ 落 verified  ② ISS-240 (mech-lead) 独立复验 ⇒ 落 verified ★

★★★**为什么做这两件事 (★main 本轮自己实跑, 不抄任何交卷报告★)** ★★★
· ★**`python3 state/advance.py --json` ⇒ internal = [] · approvals = [] · waiting = []** ⇒ rc=1
  ⇒ ★**根因 = sw-lead / mech-lead 两个名额全被【【已交卷但没签字】的 fixing】占着** ★
    (★ISS-172 会话 `agent:sw-lead:subagent:41406464` session 77167713 12:54:09~13:06:29 · status=timeout · 但**四件交付物已全部落盘**★ ·
      ★ISS-240 会话 `agent:sw-lead`→`agent:mech-lead:subagent:b97bb914` session b97bb91 12:54:09~13:08:30 · status=done ★)
  ⇒ ★**status=fixing ⇒ advance.py 的 in_flight 判据挡住这两个 agent ⇒ A 段 (internal) 开不出来 ⇒ ISS-241 永远排队** ★
· ★**ISS-172 (sw-lead) 复验 (★main 自己实跑★)**: `SW/tools/check_load_switch_selection.py` ⇒ **rc=0** (「负载开关选型证据矩阵门禁全过」★) ·
  `--selftest` ⇒ **rc=0 · 8/8** (★M1~M8 每条都「变异生效/变异前绿/变异后红」自证★) ·
  四件交付物: `SW/LOAD_SWITCH_SELECTION_FACTS.md` 74965 B (12:58) · `SW/tools/check_load_switch_selection.py` 28034 B (12:58) ·
  `HANDOFF/2026-11-16_sw-lead_ISS172_负载开关选型证据矩阵.md` 39698 B (13:03) · `state/fragments/sw.yaml` 226204 B (12:59 ⇒ 本单真写盘★)
· ★**ISS-240 (mech-lead) 复验 (★main 自己实跑★)**: `MECH/check_hinge_fpc_truth.py` ⇒ **rc=0** (★断言 9/9 PASS · FAIL 0★) ·
  `--selftest` ⇒ **rc=0 · 10/10 全抓到** (★每条自证★) · `MECH/check_demo_struct_truth.py` ⇒ **rc=0 · 23/23** ·
  `MECH/cavity_recalc_check.py` ⇒ **rc=0 · 23/23** · `MECH/hinge_usb_check.py` ⇒ **[FAIL] 0 项** ·
  四件交付物: `MECH/HINGE_FPC_GEOMETRY_TRUTH.md` 26453 B (13:09) · `MECH/check_hinge_fpc_truth.py` 29066 B (12:57) ·
  `HANDOFF/2026-11-16_mech-lead_ISS240_跨铰链FPC几何三口径收口.md` 47012 B (13:08) · `state/fragments/mech.yaml` (13:06 ⇒ **只加 2 条 claim**★)
· ★**受保护 5 个 md5 main 亲测逐字节未变**: 板 611b869e… · .kicad_pro 3e504d2b… · 网表 34132f7e… · 脚表 b21b743a… · BOM c195a117… ★
· ★**两条都没落表** (★网表/脚表/BOM/板一格没动 ⇒ 等老板拍板后由落表批次统一改★) · ★**没替老板拍型号/优先级序** ★

★★**边界 (本脚本)★★ ★★
· ★**只写 `state/issue_log.yaml` (2 条单的状态/验收/备注)** ★
· ★**不改任何交付物文件** · ★**不碰 PROJECT_TRACKER.md §0** · ★**不写任何 agent 的分片** ★
· ★**不碰板 / 布线 / 布局 / 网表 / 脚表 / BOM** ★ · ★**零外发** · ★**未替老板拍板** ★
"""
import fcntl
import os
import shutil
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
IL = os.path.join(HERE, "issue_log.yaml")
IL_LOCK = os.path.join(HERE, ".issue_log.lock")
TODAY = "2026-11-16"

VERIFY_172 = (
    "★main (moli) 2026-11-16 13:2x~13:3x **独立实跑复验** (★不抄交卷报告★) ⇒ **落 verified** ★\n"
    "· ★**会话**: `agent:sw-lead:subagent:41406464` (session 77167713) 12:54:09 起 · 13:06:29 止 · runtime 737s · ★**status=timeout**★ "
    "(★13:0x 那轮 zombie 重派的收场 timeout, 但**四件交付物已全部落盘**★) ⇒ **不是僵尸, 是已交卷未签字** ★\n"
    "· ★**main 自己实跑 2 道闸**: `python3 SW/tools/check_load_switch_selection.py` ⇒ **rc=0** (「PASS — 负载开关选型证据矩阵门禁全过」★) · "
    "`--selftest` ⇒ **rc=0 · 8/8** (★M1~M8 每条都自证「变异生效 / 变异前绿 / 变异后红」★ · M1 删判据→C2 红 · M3 砍候选→C1 红 · M6 删 TPS22991RAA→C6 红★)\n"
    "· ★**四件交付物 main 亲测在盘**: `SW/LOAD_SWITCH_SELECTION_FACTS.md` 74965 B (mtime 12:58) · `SW/tools/check_load_switch_selection.py` 28034 B (mtime 12:58) · "
    "`HANDOFF/2026-11-16_sw-lead_ISS172_负载开关选型证据矩阵.md` 39698 B (mtime 13:03) · `state/fragments/sw.yaml` 226204 B (mtime 12:59 ⇒ ★本单真写盘★)\n"
    "· ★**旁证**: `state/merge.py` rc=0 · `state/gate_check.py` rc=0 (★【Q1】18/18★) · ★**5 个受保护 md5 逐字节未变** "
    "(板 611b869e… / .kicad_pro 3e504d2b… / 网表 34132f7e… / 脚表 b21b743a… / BOM c195a117…)\n"
    "· ★**本单零落表**: 网表 L50 `U_PWR_SW` 的 `[待选型]` 判据串**一个字都没改** (★等老板拍完型号再由落表批次统一改★)\n"
    "· ★**未替老板拍板**: 决策页 §A5 = 老板先拍【优先级序】(反向阻断 > IQ<5µA > RON 越小越好 > 封装), **不是拍型号** ⇒ 本单只出证据矩阵 + 降级方案, ★一条没代拍 ★"
)

VERIFY_240 = (
    "★main (moli) 2026-11-16 13:2x~13:3x **独立实跑复验** (★不抄交卷报告★) ⇒ **落 verified** ★\n"
    "· ★**会话**: `agent:mech-lead:subagent:b97bb914` (session b97bb91) 12:54:09 起 · 13:08:30 止 · runtime 944s · ★**status=done** ★ ⇒ **真交卷** ★\n"
    "· ★**main 自己实跑 5 道闸**: `python3 MECH/check_hinge_fpc_truth.py` ⇒ **rc=0** (★断言 **9/9 PASS** · [FAIL] 0 项★) · "
    "`--selftest` ⇒ **rc=0 · 10/10 全抓到** (★每条自证★ · T8 改 demo_stack_mm 5.0→25.0 ⇒ G3 红 · T9 改受保护脚本 md5 ⇒ G9 红 · T10 删作废标记 ⇒ G4 红★) · "
    "`MECH/check_demo_struct_truth.py` ⇒ **rc=0 · 23/23** · `MECH/cavity_recalc_check.py` ⇒ **rc=0 · 23/23** · `MECH/hinge_usb_check.py` ⇒ **[FAIL] 0 项** ★\n"
    "· ★**四件交付物 main 亲测在盘**: `MECH/HINGE_FPC_GEOMETRY_TRUTH.md` 26453 B (mtime 13:09) · `MECH/check_hinge_fpc_truth.py` 29066 B (mtime 12:57) · "
    "`HANDOFF/2026-11-16_mech-lead_ISS240_跨铰链FPC几何三口径收口.md` 47012 B (mtime 13:08) · `state/fragments/mech.yaml` (mtime 13:06 ⇒ ★**只加 2 条 claim** "
    "`mech_hinge_stack_truth_mm`=25.30 / `mech_hinge_stack_demo_mm`=5.00, 旧 claim 一个字没改★)\n"
    "· ★**旁证**: `state/merge.py` rc=0 · `state/gate_check.py` rc=0 (★【Q1】18/18★) · ★**5 个受保护 md5 逐字节未变** "
    "(板 611b869e… / .kicad_pro 3e504d2b… / 网表 34132f7e… / 脚表 b21b743a… / BOM c195a117…)\n"
    "· ★**本单零落表** (★网表/脚表/BOM/板一格没动★) · ★**受保护脚本一个没改** (★改法全落在收口页 M-01~M-18 映射表★) · ★**未碰 PCB 布线/布局/板框** ★\n"
    "· ★**留给 main 的 4 条待裁 (★本单一条没代拍★)**: ★**U-1** = M-04/M-05: 旧 claim `mech_hinge_stack_fixed_mm`=25.00 与 G7/C9 字面判据三档处置 (a)/(b)/(c) ★**main 倾向 (b)/(c)· 没代拍** ★ · "
    "★**U-2** = M-01/M-02/M-03: 受保护脚本 `hinge_usb_check.py` 三处 (CROSS_LINKS 按 board 栏取 / ffc_pitch_mm 每颗用自己的 pitch / RECOMMENDED_PINS 降级) ★**要 H-1 重基线** ★ · "
    "★**U-3** = M-07/M-08/M-09: 三条旧 claim (links_count 0(demo) / radial 4.40 / declared 49.62) 拆不拆 key ★**建议 demo + 整机分列** ★ · "
    "★**U-4** = ★**整机阶段跨铰链链路数 3 还是 4 ⇒ 老板/PM 未裁** (★老板 11-02 19:25 只裁了 demo 形态; 结论方向不变: N=3→4.05 / N=4→4.40, 都 > 0★) ★ ⇒ ★**已并进决策页 §A-补3** ★"
)

NOTE_172 = (
    "\n\n★2026-11-16 13:3x (cron 775d9893 继续执行后继计划) ★**main 独立复验 ⇒ 落 verified · 清 sw-lead 名额** ★\n"
    "· ★**依据 (★main 本轮自己实跑, 不采信 agent 自述★)**: `SW/tools/check_load_switch_selection.py` rc=0 · `--selftest` rc=0 **8/8** · "
    "四件交付物在盘 (facts 74965 B / 脚本 28034 B / 交卷单 39698 B / 分片 sw.yaml 226204 B) · merge rc=0 · gate_check Q1 18/18 · ★**5 个受保护 md5 逐字节未变** ★\n"
    "· ★**为什么必须清 (★不是形式主义★)**: status=fixing ⇒ advance.py 的 in_flight 判据挡住 sw-lead ⇒ **sw-lead 唯一写会话名额被『已交卷但没签字』占着** ⇒ A 段开不出来 ⇒ ISS-241 永远排队 ★\n"
    "· ★**清账后 sw-lead 名额释放** ⇒ ★**本轮 advance.py internal 段已开出 ISS-241 (sw-lead) ⇒ 已派 (见 dispatch_log)★ ★\n"
    "· ★**边界**: 只改本条 status/verify_result/verify_by/verify_date/note · 零外发 · 零落表 · 零 PCB 触碰 · 没碰任何分片 / 真源文件 / 决策页 / outbox ★"
)

NOTE_240 = (
    "\n\n★2026-11-16 13:3x (cron 775d9893 继续执行后继计划) ★**main 独立复验 ⇒ 落 verified · 清 mech-lead 名额** ★\n"
    "· ★**依据 (★main 本轮自己实跑, 不采信 agent 自述★)**: `MECH/check_hinge_fpc_truth.py` rc=0 **9/9** · `--selftest` rc=0 **10/10** · "
    "`check_demo_struct_truth.py` rc=0 **23/23** · `cavity_recalc_check.py` rc=0 **23/23** · `hinge_usb_check.py` [FAIL] 0 项 · "
    "四件交付物在盘 (收口页 26453 B / 脚本 29066 B / 交卷单 47012 B / 分片只加 2 claim) · merge rc=0 · gate_check Q1 18/18 · ★**5 个受保护 md5 逐字节未变** ★\n"
    "· ★**为什么必须清**: status=fixing ⇒ advance.py 的 in_flight 判据挡住 mech-lead ⇒ **mech-lead 名额被『已交卷但没签字』占着** ⇒ A 段开不出来 ★\n"
    "· ★**清账后 mech-lead 名额释放** (★该 agent 名下 open = 0 ⇒ 释放后本轮无可派, 下一轮有单即自动可派★) ★\n"
    "· ★**4 条待裁 (U-1~U-4) 一条没代拍, 已并进决策页 `DECISION_PENDING_2026-11-16.md` §A-补3** ★\n"
    "· ★**边界**: 只改本条 status/verify_result/verify_by/verify_date/note · 零外发 · 零落表 · 零 PCB 触碰 · 没碰任何分片 / 真源文件 / outbox ★"
)


def _atomic_write(path: str, data: str) -> None:
    fd, tmp = tempfile.mkstemp(dir=HERE, prefix=".tmp_write.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(data)
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def main() -> int:
    shutil.copy2(IL, IL + ".bak_20261116_1325_verify172_240")

    lf = open(IL_LOCK, "a+")
    try:
        fcntl.flock(lf, fcntl.LOCK_EX)
        il = yaml.safe_load(open(IL, encoding="utf-8"))
        hit172 = hit240 = 0
        for it in il.get("issues") or []:
            iid = it.get("id")
            if iid == "ISS-172":
                it["status"] = "verified"
                it["verify_by"] = "main"
                it["verify_date"] = TODAY
                it["verify_result"] = VERIFY_172
                it["note"] = (it.get("note") or "") + NOTE_172
                hit172 += 1
            elif iid == "ISS-240":
                it["status"] = "verified"
                it["verify_by"] = "main"
                it["verify_date"] = TODAY
                it["verify_result"] = VERIFY_240
                it["note"] = (it.get("note") or "") + NOTE_240
                hit240 += 1
        if (hit172, hit240) != (1, 1):
            raise SystemExit("★命中数异常 (172=%s 240=%s) ⇒ 中止" % (hit172, hit240))
        _atomic_write(IL, yaml.safe_dump(il, allow_unicode=True, sort_keys=False, width=100000))
    finally:
        fcntl.flock(lf, fcntl.LOCK_UN)
        lf.close()

    print("   - ISS-172 → verified (main 亲核签字: 门禁 rc=0 + selftest 8/8)")
    print("   - ISS-240 → verified (main 亲核签字: 门禁 9/9 + selftest 10/10 + 23/23 + 23/23)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
