#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
state/_hw_verify_20261108.py — hw-lead 独立验证 23 条 fixed issue (2026-11-08)

================================================================================
纪律 (项目铁律, 违反=本轮作废)
---------------------------------------------------------------------------------
① **flock** (state/.issue_log.lock) + **锁内重读** + **原子写** (tmp + fsync + os.replace)
   —— 禁止 open(path,"w") 覆盖: 并发下读者会读到半截 YAML ⇒ 整张表从检查里消失
② **只碰下面这 23 个 id 的行** —— 别人的行一行都不许动 (脚本逐条断言 owner/verify_by)
③ **verify_result / verify_date 只有验证方能写** ⇒ 本单我 (hw-lead) 就是验证方
   —— 对 3 条 "verify_by==owner==main" 的 (ISS-165/167/182) ⇒ **先把 verify_by 改成 hw-lead 再验**
④ 关单必须满足 C3: verify_result=='pass' 且 **verify_by != owner** 且有 fix_ref
   —— ISS-165/167/182 的 owner=main, verify_by=hw-lead ⇒ C3 成立
   —— 其余 20 条 owner=main, verify_by=hw-lead ⇒ C3 成立
⑤ 收尾跑 `python3 state/issue_check.py` 确认这批不再计入"逾期未闭环"

用法:
  python3 state/_hw_verify_20261108.py --dry-run     # 只看要改什么, 不落盘
  python3 state/_hw_verify_20261108.py               # 落盘
================================================================================
"""
from __future__ import annotations

import fcntl
import json
import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
VERDICTS = os.path.join(HERE, "_hw_verify_20261108_verdicts.json")

# ★★本单只碰这 23 个 id —— 别人的行一行都不许动
SCOPE = [
    # ---- 原 verify_by=hw-lead 的 20 条 ----
    "ISS-082", "ISS-086", "ISS-094", "ISS-096", "ISS-098", "ISS-140",
    "ISS-148", "ISS-149", "ISS-150", "ISS-157", "ISS-158", "ISS-162",
    "ISS-166", "ISS-168", "ISS-171", "ISS-175", "ISS-176", "ISS-178",
    "ISS-183", "ISS-184",
    # ---- 违反 C3 (verify_by==owner==main), 本次接手 ----
    "ISS-165", "ISS-167", "ISS-182",
]
# ★这 3 条原本 verify_by=main 且 owner 也是 main ⇒ 违反 C3 (修复人自验)
#   ⇒ 本单先把 verify_by 改成 hw-lead (接手), 再独立验证
TAKEOVER = {"ISS-165", "ISS-167", "ISS-182"}

VERIFIER = "hw-lead"
VERIFY_DATE = "2026-11-08"


def atomic_write(path: str, text: str) -> None:
    """原子写: 唯一 tmp 文件名 + fsync + os.replace ⇒ 读者永远看到完整快照"""
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
    with open(VERDICTS, encoding="utf-8") as f:
        verdicts = json.load(f)

    missing = [i for i in SCOPE if i not in verdicts]
    extra = [i for i in verdicts if i not in SCOPE]
    if extra:
        print(f"❌ 判决表里有本单范围外的 id: {extra} —— 拒绝执行")
        return 1
    if missing:
        print(f"❌ 判决表缺 {len(missing)} 条: {missing}")
        return 1

    lock_fd = os.open(LOCK, os.O_RDWR | os.O_CREAT, 0o666)
    fcntl.flock(lock_fd, fcntl.LOCK_EX)
    try:
        # ---------- 锁内重读 ----------
        with open(LOG, encoding="utf-8") as f:
            doc = yaml.safe_load(f)
        issues = doc["issues"]
        before_n = len(issues)
        before_bytes = os.path.getsize(LOG)
        by_id = {i.get("id"): i for i in issues}

        plan = []
        for iid in SCOPE:
            v = verdicts[iid]
            it = by_id.get(iid)
            if it is None:
                print(f"❌ {iid} 不在表里")
                return 1
            # ★纪律②: 只碰这 23 条; 且它们的 owner 必须是 main (修复人), 验证人不得是 owner
            assert it.get("owner") == "main", f"{iid} owner={it.get('owner')} 不是 main, 别乱动"
            assert it.get("status") in ("fixed", "verified"), \
                f"{iid} status={it.get('status')} 不是 fixed/verified, 别乱动"
            assert it.get("fix_ref"), f"{iid} 没有 fix_ref, 不能关单"
            vb = it.get("verify_by")
            if iid in TAKEOVER:
                assert vb == "main", f"{iid} 预期 verify_by==main (待接手), 实际 {vb}"
            else:
                assert vb == VERIFIER, f"{iid} verify_by={vb} 不是 {VERIFIER}, 别乱动"

            ok = v["result"] == "pass"
            new_status = "closed" if (ok and v.get("close", True)) else (
                "verified" if ok else "fixing")
            plan.append({
                "id": iid,
                "owner": it.get("owner"),
                "verify_by_before": vb,
                "status_before": it.get("status"),
                "status_after": new_status,
                "result": v["result"],
                "verify_by_after": VERIFIER,
                "verify_date_before": it.get("verify_date"),
                "verify_date_after": VERIFY_DATE,
                "due_before": it.get("due"),
                "due_after": v.get("new_due"),
                "takeover": iid in TAKEOVER,
            })

        print("=" * 100)
        print("★ 计划改动 (只碰这 23 条)")
        print("=" * 100)
        for p in plan:
            flag = "✋接手" if p["takeover"] else "  "
            print(f"  {flag} {p['id']:<9} {p['status_before']:<9} → {p['status_after']:<9} "
                  f"verify_by {p['verify_by_before']}→{p['verify_by_after']}  "
                  f"result={p['result']}  due {p['due_before']}→{p['due_after']}")
        print(f"\n  条数 {before_n} (不变) | 体积 {before_bytes} B")

        if dry:
            print("\n[dry-run] 未落盘")
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
            return 0

        # ---------- 落盘 ----------
        for iid in SCOPE:
            v = verdicts[iid]
            it = by_id[iid]
            ok = v["result"] == "pass"
            # ③ verify_by: 接手的三条改成 hw-lead (本来就要改); 其余本来就是 hw-lead
            it["verify_by"] = VERIFIER
            # ③ verify_result / verify_date: 只有验证方能写 ⇒ 我写
            it["verify_result"] = v["result"]
            it["verify_date"] = VERIFY_DATE
            # ④ 状态机: fixed → verified → closed (C3 满足: verify_by != owner)
            it["status"] = "closed" if (ok and v.get("close", True)) else (
                "verified" if ok else "fixing")
            if v.get("new_due"):
                it["due"] = v["new_due"]
            # note 追加验证结论 (不覆盖原文)
            note = str(it.get("note") or "").rstrip()
            tag = "★2026-11-08 hw-lead 独立验证 (接手 verify_by=main→hw-lead): " \
                if iid in TAKEOVER else "★2026-11-08 hw-lead 独立验证: "
            it["note"] = (note + "\n" + tag + v["note"]).strip()

        text = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=4096)
        atomic_write(LOG, text)

        after_n = len(doc["issues"])
        after_bytes = os.path.getsize(LOG)
        print(f"\n✅ 落盘完成: 条数 {before_n} → {after_n} | 体积 {before_bytes} → {after_bytes} B")
        if after_n != before_n:
            print("❌ 条数变了 —— 异常")
            return 1
        if after_bytes < before_bytes * 0.95:
            print("❌ 体积掉 5% 以上 —— 疑似截断")
            return 1
        return 0
    finally:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        os.close(lock_fd)


if __name__ == "__main__":
    sys.exit(main())
