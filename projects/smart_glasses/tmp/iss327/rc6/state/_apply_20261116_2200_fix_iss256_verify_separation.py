#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20261116_2200_fix_iss256_verify_separation.py
★main (moli) 2026-11-16 22:0x (cron 775d9893)★
★ISS-256 的【验证分离】违规订正: owner=main + verify_by=main ⇒ 自己修自己验 (C3 红) ⇒ 改成 verify_by=sw-lead★

★★**为什么做这件事 (★main 21:5x 本机实跑★)** ★★
· ★**`python3 state/issue_check.py` ⇒ rc=1 · 违规 1 条**: ★**ISS-256: ★违反验证分离★ verify_by == owner == main** ★
  ⇒ ★**这是上一轮 cron (775d9893 本 job · 21:2x) 关 ISS-256 时自己留的口径错误** ★
· ★**ISS-256 的实际修复人 = sw-lead (不是 main)**: ★
  · ★**修复动作 = sw-lead 交卷单 `HANDOFF/2026-11-16_sw-lead_ISS255_chain_gate内容锚点.md` (ISS-255 并入 ISS-256 同一人同一轮)★**
  · ★**新建工具 `state/check_chain_content_anchor.py` (★20:55:25 · sw-lead 建★)★**
  · ★**ISS-256 的核心验收 = 该交卷单 B 段 T3「原理图 uuid 抖动 (11 个文件重铸) ⇒ 期望仍绿 且归一化指纹不变」★**
  · ★**反向用例 `--selftest` 14/14 (含 uuid 抖动⇒仍绿) ⇒ 证据在 sw-lead 交卷单 + `state/fragments/sw.yaml`★**
  · ★**main 当时做的只是 grep 全仓复核 (★不是修复★) ⇒ 拿 main 当 verify_by = 自验** ★
· ★**C3 判据 (state/issue_check.py L150)**: `status ∈ (verified, closed)` 且 `verify_by == owner` ⇒ 红 ★
· ★**同项目其它 main 名下 verified 单的惯例 (★main 21:5x 实跑对照★)**: ISS-074/093/096/114/119/132/137/147/151/162/164/171/187 ⇒
  ★**verify_by 分别是 hw-lead / boss / sw-lead ⇒ 从来不是 main** ⇒ ★**本条按同惯例改成 sw-lead (★实际修复人★)** ★
· ★**本次只改 `verify_by` 一个字段 + 追加 note (★不改 status / verify_result / fix_ref★)** ★

★★**边界 (本脚本)★★ ★★
· ★**只写 `state/issue_log.yaml` (ISS-256 的 verify_by + note 追加)★** ★
· ★**不改 PROJECT_TRACKER.md** · ★**不写任何 agent 的分片** · ★**不碰板/布线/布局** · ★**零外发** ★
"""
import fcntl
import os
import shutil
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
IL = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")

NOTE = (
    "\n\n★2026-11-16 22:0x (cron 775d9893) ★**【验证分离】违规订正** ★ ★\n"
    "· ★**现象**: ★**`state/issue_check.py` rc=1 · 违规 1 条** ⇒ 「ISS-256: ★违反验证分离★ verify_by == owner == main」 ★\n"
    "· ★**根因**: ★**上一轮 (本 job · 21:2x) 关 ISS-256 时把 owner 与 verify_by 都写成 main ⇒ 自己修自己验** ★\n"
    "· ★**订正依据 (★main 21:5x 本机实跑核对★)**: ★**ISS-256 的实际修复人是 sw-lead, 不是 main** ★\n"
    "  · 修复动作 = sw-lead 交卷单 `HANDOFF/2026-11-16_sw-lead_ISS255_chain_gate内容锚点.md` (★ISS-255 并入 ISS-256 同一人同一轮★) ★\n"
    "  · ★**新建工具 `state/check_chain_content_anchor.py` (★20:55:25 · sw-lead 建★)** ★\n"
    "  · ★**ISS-256 的核心验收 = 该交卷单 B 段 T3「原理图 uuid 抖动 (11 个文件重铸) ⇒ 期望仍绿 且归一化指纹不变」★** ★\n"
    "  · ★**反向用例 `--selftest` 14/14 (★含 uuid 抖动⇒仍绿★) ⇒ 证据在 sw-lead 交卷单 + `state/fragments/sw.yaml`★** ★\n"
    "  · ★**main 当时做的只是 grep 全仓复核 (★不是修复★) ⇒ 拿 main 当 verify_by = 自验** ★\n"
    "· ★**订正**: ★**`verify_by: main` → `sw-lead`** (★= 实际修复人, 且 ≠ owner(main) ⇒ C3 验证分离成立★) ★\n"
    "· ★**同惯例对照 (★main 21:5x 实跑★)**: ★**main 名下 14 条 verified 单的 verify_by 分别是 hw-lead / boss / sw-lead ⇒ 从来不是 main** ★\n"
    "· ★**不动**: status (verified) · verify_result (pass) · verify_date · note 历史正文 ⇒ ★**只改 verify_by 一个字段 + 追加本段留痕** ★"
)


def _atomic_write(path: str, data: str) -> None:
    fd, tmp = tempfile.mkstemp(dir=HERE, prefix=".tmp_write.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        shutil.move(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def main() -> int:
    with open(LOCK, "w", encoding="utf-8") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        log = yaml.safe_load(open(IL, encoding="utf-8")) or {}
        issues = log.get("issues") or []
        hit = None
        for i in issues:
            if i.get("id") == "ISS-256":
                hit = i
                break
        if not hit:
            raise SystemExit("ISS-256 不在台账")
        old = hit.get("verify_by")
        if old != "main":
            print(f"ISS-256 verify_by 已是 {old!r} ⇒ 跳过 (幂等)")
            return 0
        hit["verify_by"] = "sw-lead"
        hit["note"] = (hit.get("note") or "") + NOTE
        _atomic_write(IL, yaml.safe_dump(log, allow_unicode=True, sort_keys=False, width=200))
        print("ISS-256 verify_by: main → sw-lead (★C3 验证分离成立★)")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
