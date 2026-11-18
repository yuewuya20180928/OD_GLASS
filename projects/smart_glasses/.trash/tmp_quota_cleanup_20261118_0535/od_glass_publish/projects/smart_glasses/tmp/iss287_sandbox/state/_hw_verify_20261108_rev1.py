#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
state/_hw_verify_20261108_rev1.py — hw-lead 独立验证 **第二轮交叉复核后的翻案/订正** (2026-11-08)

================================================================================
为什么有 rev1:
---------------------------------------------------------------------------------
第一轮 23 条我已全部独立验证并落盘 (21 closed + 2 verified)。随后跑了**第二轮交叉复核**
(另一名独立验证员, 与我独立), 它在 4 条上给出与我不同的发现 —— 我**逐条亲自复测**, 结论:

  ★ ISS-162  **由 closed 退回 verified** (新 due 2026-11-13)
      实测: `HW/PCB/FPC_PIN_TABLES.md` camera 31 针表只印到 pin30, **缺 pin31 (VCC5V)**
            → 导出脚本 off-by-one (`state/_iss162a1_spec.py:78-79` `range(1,31,2)` 应为 `range(1,32,2)`)
            → 网表/板/门禁三者 31/31 一致 (电气真值对, demo 投板无风险), 但**交付物没达「逐针 31/31」**
            → 另有 netlist_v1.csv:290 的 INVENTORY note 留旧自拟针号 + desc ⑤ 的 1080p60 未进网表
  ★ ISS-171  **由 closed 退回 verified** (新 due 2026-11-13)
      实测: 本单 desc ② 说「BAT_GATE 两管共栅 ⇒ 已拆」, 但**板上仍在短**
            (netlist_v1.csv:35 / pcbnew: Q1.pad2 = Q2.pad2 = BAT_GATE), 且网表自身 note 写着
            「原厂要求两管不可共栅」 ⇒ 自相矛盾 ⇒ 整链 DNP 故 demo 无影响, 但充电板阶段是真缺陷
            + U_SUPV 的 GND(pin2)/MR(pin3) 未补 + U_LDO_S28 缺 pin3(EN) + BQ2970 V-(pin6) 未画
            + 网表只带上 13/18 的 footprint/OPN
  ★ ISS-176  **维持 closed**, 但**订正我自己上一段的说法**:
            我先前把 verify_display_fpc.py 报的「7 个器件外框重叠」当 courtyard 打架上报 ——
            实测那 8 个器件**全部 has_courtyard=False** ⇒ 那是 **bbox(含 Fab/Silk 文字) 相交, 不是真冲突**,
            DRC=0 佐证物理无冲突 ⇒ 我的原话**说重了**, 此处订正; 但脚本「只 print 不 fail」是真缺陷
  ★ ISS-168  **维持 closed**, 补一条**诚实边界** (「12/12 载板原理图互证」没落文档, 对照源 PDF 不在仓)
  ★ ISS-183  **维持 closed**, 补一条**残留清单** (RAIL_SOM_DCIN 只落在历史件, 现行产物零命中)

纪律 (同第一轮, 一条不放松):
  ① flock(state/.issue_log.lock) + **锁内重读** + **原子写** (tmp + fsync + os.replace)
  ② **只碰下面这 5 个 id 的行** —— 别人的行一行都不许动
  ③ verify_result / verify_date **不改** (仍是第一轮我写的 'pass' / 2026-11-08) —— 本轮只改
     status / due / note
  ④ 不碰 STATE.yaml / STATUS_DIGEST / 其他 issue

用法:
  python3 state/_hw_verify_20261108_rev1.py --dry-run
  python3 state/_hw_verify_20261108_rev1.py
"""
from __future__ import annotations

import fcntl
import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
NOTES = os.path.join(HERE, "_hw_verify_20261108_rev1_notes.py")

VERIFIER = "hw-lead"
VERIFY_DATE = "2026-11-08"
NEW_DUE = "2026-11-13"

# ★本轮只碰这 5 条
REOPEN = {"ISS-162": NEW_DUE, "ISS-171": NEW_DUE}   # closed → verified + 新 due
NOTE_ONLY = ["ISS-176", "ISS-168", "ISS-183"]         # 维持 closed, 只追加订正/边界
SCOPE = list(REOPEN.keys()) + NOTE_ONLY


def atomic_write(path: str, text: str) -> None:
    tmp = f"{path}.tmp.{os.getpid()}"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def main() -> int:
    dry = "--dry-run" in sys.argv
    ns = {}
    with open(NOTES, encoding="utf-8") as f:
        exec(compile(f.read(), NOTES, "exec"), ns)
    notes = ns["NOTES"]

    missing = [i for i in SCOPE if i not in notes]
    extra = [i for i in notes if i not in SCOPE]
    if extra:
        print(f"❌ 备注表里有本轮范围外的 id: {extra} —— 拒绝执行")
        return 1
    if missing:
        print(f"❌ 备注表缺 {missing}")
        return 1

    lock_fd = os.open(LOCK, os.O_RDWR | os.O_CREAT, 0o666)
    fcntl.flock(lock_fd, fcntl.LOCK_EX)
    try:
        with open(LOG, encoding="utf-8") as f:          # ← 锁内重读
            doc = yaml.safe_load(f)
        issues = doc["issues"]
        before_n, before_bytes = len(issues), os.path.getsize(LOG)
        by_id = {i.get("id"): i for i in issues}

        plan = []
        for iid in SCOPE:
            it = by_id.get(iid)
            if it is None:
                print(f"❌ {iid} 不在表里")
                return 1
            # ★纪律②: 范围外不许动; 这 5 条必须是我第一轮签过的
            assert it.get("owner") == "main", f"{iid} owner={it.get('owner')} 不是 main"
            assert it.get("verify_by") == VERIFIER, f"{iid} verify_by={it.get('verify_by')} 不是 {VERIFIER}"
            assert it.get("verify_result") == "pass", f"{iid} verify_result={it.get('verify_result')}"
            assert it.get("verify_date") == VERIFY_DATE, f"{iid} verify_date={it.get('verify_date')}"
            assert it.get("status") in ("closed", "verified"), f"{iid} status={it.get('status')}"
            assert it.get("fix_ref"), f"{iid} 没有 fix_ref"
            new_status = "verified" if iid in REOPEN else it["status"]
            new_due = REOPEN.get(iid)
            plan.append((iid, it["status"], new_status, it.get("due"), new_due))

        print("=" * 100)
        print("★ rev1 计划改动 (只碰这 5 条; verify_result/verify_date 一个字都不改)")
        print("=" * 100)
        for iid, sb, sa, db, da in plan:
            flag = "↩️ 退回" if iid in REOPEN else "📝 补注"
            print(f"  {flag} {iid:<9} {sb:<9} → {sa:<9}  due {db}→{da}")

        if dry:
            print("\n[dry-run] 未落盘")
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
            return 0

        for iid in SCOPE:
            it = by_id[iid]
            if iid in REOPEN:
                it["status"] = "verified"
                it["due"] = REOPEN[iid]
            note = str(it.get("note") or "").rstrip()
            tag = "★2026-11-08 hw-lead 独立验证 · 第二轮交叉复核补充: "
            it["note"] = (note + "\n" + tag + notes[iid]).strip()
            # ★verify_result / verify_date / verify_by 本轮不写

        text = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=4096)
        atomic_write(LOG, text)

        after_n, after_bytes = len(doc["issues"]), os.path.getsize(LOG)
        print(f"\n✅ 落盘完成: 条数 {before_n} → {after_n} | 体积 {before_bytes} → {after_bytes} B")
        if after_n != before_n:
            print("❌ 条数变了")
            return 1
        if after_bytes < before_bytes * 0.95:
            print("❌ 体积掉 5% 以上")
            return 1
        return 0
    finally:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        os.close(lock_fd)


if __name__ == "__main__":
    sys.exit(main())
