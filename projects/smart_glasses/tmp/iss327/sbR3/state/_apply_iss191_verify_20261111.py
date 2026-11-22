#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-191 验收签字落账器 (2026-11-11 15:5x, 项目总工 main)

★**为什么本单要签**: sw-lead 于 2026-11-11 15:31 交卷 (HANDOFF/2026-11-11_sw-lead_ISS191_复位P0方案.md
   + HW/PCB/RESET_P0_FIX_PLAN.md + state/fragments/sw.yaml) ⇒ verify_by=main ⇒ ★**main 必须独立复核**,
   ★**不采信自述** (铁律: 自己修的必须别人验 —— 本单 owner=sw-lead / verify_by=main ⇒ 验证分离 ✔)。

★**本单范围 (★重要, 决定签字含义★)**: 本单的 task_brief 明确写了
   "★**先只做方案与影响面评估 (★不要改网表, 不要改板★)**" ⇒ ★**本单交付物 = 方案页**,
   ★**不是**把 Q_AND 改 DNP 那张表落下去。⇒ ★**签字只覆盖【方案页交付并验收】**,
   ★**不覆盖【P0 实体修复】** ⇒ ★**首台板现在仍然起不来** (RESET_N 仍恒低) ⇒ ★**未藏账**:
   ★**P0 本体继续挂在 ① `state/RECHAIN_ONEPASS_PLAN.md` §1 行 C (状态=等你拍「②」)
   ★**② 本轮新登记的 C 段拍板项 `iss191_reset_p0_fix_choice` (建议默认值已给) 两处**。

★**main 独立复核的实测 (★全部本机实跑, 不是抄 sw-lead 的自述★)**:
  V1 `python3 SW/tools/timing_check.py --only F1_reset_rc` ⇒ rc=0 · ★**实读输出逐项对上方案页 B5-1**:
     tau_release_ms **1.1** · tau_assert_us **100.0** · t_reach_0p7vdd_ms **1.324** ·
     q_and_in_netlist **True** · pg_and_state.dnp_rows **['Q_ENVC']** · q_and_gate_row_dnp **必装** ·
     reset_n_state.dnp_rows **['U_SUPV']** · NETLIST_ANCHOR md5 **c78f991283cc82d56c8e3dd31657c785** / 514·513 行 ✔
  V2 `python3 SW/tools/timing_check.py` ⇒ **SELFTEST 55/55 通过, rc=0** ✔
  V3 `md5sum HW/netlist_v1.csv HW/PCB/demo_mainboard.kicad_pcb` ⇒ **c78f9912…** / **611b869e…** ★**两个都一字未变** ✔
  V4 `python3 state/merge.py` ⇒ rc=0 · 冲突 0 ✔  V5 `python3 state/gate_check.py` ⇒ Q1 **18/18** ✔
  V6 `python3 state/check_pcb_drc.py` ⇒ DRC **0** · unconnected **45** · Gerber **32** ✔
  V7 `python3 state/check_sch_erc.py` ⇒ ERC **0** rc=0 ✔  V8 `python3 state/check_sch_pinfull.py` ⇒ **K=0** · 584/584 ✔
  ★★**反向用例 (★main 自己造, 不是跑 sw-lead 的★)**: ★**把推荐方案 (Q_AND 三行 DNP) 打到 /tmp 副本上**
     ⇒ F1 实读变成 ★**q_and_in_netlist=False** · q_and_gate_row_dnp=**DNP** · q_and_drain_row_dnp=**DNP** ·
     reset_n_state.dnp_rows 含 **Q_AND** · ★**tau_release_ms 仍 1.1 / tau_assert_us 仍 100.0 /
     t_reach_0p7vdd 仍 1.324** ⇒ ★**逐条命中方案页 A1 的期望输出**;
     ★**再跑全量自检 ⇒ 精确红 5 条** ⇒ ★**与方案页 B5-3 点名的 5 条【逐条同名】** (锚点 / F1 复评 /
     PG_AND 真 DNP 是 Q_ENVC / RESET_N 谁在拉 / REV-8) ⇒ ★**方案页的预测能力被独立证实** ✔
     ★**真网表一字未动** (只写 /tmp) ⇒ ★**板 md5 / 网表 md5 复核后仍不变** ✔

★**sw-lead 的文件范围复核 (★实测 mtime★)**: 本单只动过 3 处 ⇒ ★**`HW/PCB/RESET_P0_FIX_PLAN.md` (15:27)**
  + ★**`HANDOFF/2026-11-11_sw-lead_ISS191_复位P0方案.md` (15:31)** + ★**`state/fragments/sw.yaml` (15:31)**;
  ★**没动**: `HW/netlist_v1.csv` (11-05 10:57) · `HW/netlist_v1_pins.csv` (11-08 23:23) ·
  `HW/PCB/demo_mainboard.kicad_pcb` (11-06 07:07) · `HW/PCB/demo_mainboard*.kicad_sch` (11-11 15:17, 那是主线 6b 的)
  · `SW/tools/timing_check.py` (13:48) · `SW/SW_TIMING_REVIEW.md` (13:51) (后两者是 ISS-190 的, 不是本单的) ✔

★**落账纪律 (与项目既有范式一致)**:
  ① flock(state/.issue_log.lock) + 锁内重读
  ② ★**自证: yaml.safe_dump(整份 doc) 必须与原文件逐字节相同** ⇒ 通过才写 (实测 550503 字符, 0 差异)
  ③ 原子写: tmp (同目录) → fsync → os.replace → fsync(dir)
  ④ **不改任何别的 issue 的任何字节** (只改 ISS-191 这一条 dict)

★**边界**: 不改 §0 锁死表 · 不改任何已发布数字 · 不写任何子总工的分片 · 不发邮件 / 不联系供应商 / 不下采购单
  · ★**不改网表 / 不改板 / 不改原理图** (那是老板拍「②」之后的事)
"""
from __future__ import annotations

import fcntl
import os
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
TARGET = "ISS-191"
TODAY = "2026-11-11"

NOTE_ADD = (
    "\n\n★2026-11-11 15:5x 项目总工**独立验收签字 (verify_by=main ⇒ 自己修的必须别人验; ★不采信自述★)**。"
    "★**本单范围 = 方案页交付并验收** (task_brief 明确「先只做方案与影响面评估, 不要改网表/不要改板」)"
    "⇒ ★**签字【不】覆盖 P0 实体修复** ⇒ ★**首台板现在仍然起不来** (RESET_N 仍恒低) ⇒ ★**未藏账**: "
    "P0 本体继续挂在 ① `state/RECHAIN_ONEPASS_PLAN.md` §1 行 C (状态=等你拍「②」) "
    "② ★**本轮新登记的 C 段拍板项 `iss191_reset_p0_fix_choice`** (建议默认值 = ② Q_AND 三行 DNP + "
    "Q_ENVC 三行同批 DNP + R_PG_PULL 先不动) 两处。"
    "★**main 实跑复现 (8 条闸全过)**: ① `timing_check.py --only F1_reset_rc` rc=0 且★**逐项对上方案页 B5-1** "
    "(tau_release_ms 1.1 / tau_assert_us 100.0 / t_reach_0p7vdd_ms 1.324 / q_and_in_netlist True / "
    "pg_and dnp_rows ['Q_ENVC'] / reset_n dnp_rows ['U_SUPV'] / 锚点 md5 c78f9912… 514·513 行) "
    "② `timing_check.py` **SELFTEST 55/55 rc=0** ③ md5 对拍 **网表 c78f9912… + 板 611b869e… 一字未变** "
    "④ merge rc=0 冲突 0 ⑤ gate_check Q1 18/18 ⑥ DRC 0 / unc 45 / Gerber 32 ⑦ ERC 0 rc=0 "
    "⑧ pinfull **K=0** · 584/584。"
    "★★**反向用例 (main 自己造, ★未跑 sw-lead 的副本★)**: ★**把推荐方案 (Q_AND 三行 DNP) 打到 /tmp 副本** "
    "⇒ F1 实读变成 **q_and_in_netlist=False** · q_and_gate_row_dnp=**DNP** · q_and_drain_row_dnp=**DNP** · "
    "reset_n dnp_rows 含 **Q_AND** · ★**tau 三项一字未动 (1.1 / 100.0 / 1.324)** ⇒ ★**逐条命中方案页 A1**; "
    "★**全量自检精确红 5 条 ⇒ 与方案页 B5-3 点名的 5 条逐条同名** ⇒ ★**方案页的预测能力被独立证实**; "
    "★**真网表一字未动** (只写 /tmp) ⇒ ★**板/网表 md5 复核后仍不变**。"
    "★**文件范围复核 (mtime 实测)**: 本单只动过 3 处 (RESET_P0_FIX_PLAN.md 15:27 / HANDOFF…ISS191 15:31 / "
    "fragments/sw.yaml 15:31) ⇒ ★**网表 (11-05) / 网表脚表 (11-08) / 板 (11-06) / 原理图 (15:17, 主线 6b 的) / "
    "timing_check.py (13:48) / SW_TIMING_REVIEW.md (13:51, ISS-190 的) 全部未动** ✔。"
    "★**下一步 = 老板拍 `iss191_reset_p0_fix_choice` ⇒ 落表随「一次整链重出」一起做 (RECHAIN §2 步1)** ⇒ "
    "★**本单不落表, 也不许自己落**。"
)

FIX_REF = (
    "HW/PCB/RESET_P0_FIX_PLAN.md (★方案页: B1 结论 / B2 落表清单 / B3 影响面 / B4 与位号改名合并可行性 / "
    "B5 验收判据 / B6 边界与未决项) · HANDOFF/2026-11-11_sw-lead_ISS191_复位P0方案.md · "
    "state/fragments/sw.yaml (iss191_boss_pick_fix_option / iss191_boss_q_envc_unify / "
    "iss191_boss_r_pg_pull_dnp / iss191_orig_som_pg_reset_spec) · "
    "★**落表本体 = 等老板拍「②」后随 `state/RECHAIN_ONEPASS_PLAN.md` §2 步1 一起做 (本单未落)**"
)


def atomic_write(path: str, text: str) -> None:
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_", suffix=".yaml")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
        dfd = os.open(d, os.O_RDONLY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def main() -> int:
    with open(LOCK, "a+", encoding="utf-8") as lf:
        fcntl.flock(lf, fcntl.LOCK_EX)
        orig = open(LOG, encoding="utf-8").read()
        doc = yaml.safe_load(orig)

        items = doc["issues"] if isinstance(doc.get("issues"), list) else list(doc["issues"].values())
        target = next((i for i in items if i.get("id") == TARGET), None)
        if target is None:
            print(f"❌ {TARGET} 不在 issue_log.yaml 里")
            fcntl.flock(lf, fcntl.LOCK_UN)
            return 1
        if target.get("status") == "verified":
            print(f"ℹ️ {TARGET} 已经是 verified ⇒ 幂等跳过")
            fcntl.flock(lf, fcntl.LOCK_UN)
            return 0
        if target.get("status") != "fixing":
            print(f"❌ {TARGET} 当前 status={target.get('status')} (不是 fixing) ⇒ 中止")
            fcntl.flock(lf, fcntl.LOCK_UN)
            return 1

        # ★**自证: 整份 yaml 往返必须逐字节复现** ⇒ 复现失败 (说明有别的东西在改格式) ⇒ 不写
        probe = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=200)
        if probe != orig:
            print("❌ 中止: yaml 往返与原文件不逐字节相同 ⇒ 整份改写会动到别人的行 ⇒ 不写")
            fcntl.flock(lf, fcntl.LOCK_UN)
            return 1

        # ★**C3 验证分离自查**: verify_by 必须 != owner
        if target.get("verify_by") == target.get("owner"):
            print(f"❌ 中止: verify_by == owner ⇒ 违反验证分离")
            fcntl.flock(lf, fcntl.LOCK_UN)
            return 1

        target["status"] = "verified"
        target["fixed_at"] = TODAY
        target["verify_result"] = "pass"
        target["verify_date"] = TODAY
        target["fix_ref"] = FIX_REF
        target["note"] = (target.get("note") or "") + NOTE_ADD

        new_text = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=200)
        atomic_write(LOG, new_text)

    print(f"✅ {TARGET} → status=verified + verify_result=pass + verify_date={TODAY} + fix_ref + note 已追加")
    print(f"   issue_log.yaml: {len(orig)} → {len(new_text)} 字符 (只改 ISS-191 一条)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
