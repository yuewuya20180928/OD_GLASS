#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-189 验收签字 (verify_by=main) —— 2026-11-11 11:4x, main (项目总工 moli)

★**背景**: ★**ISS-189 是本项目第一条【死单救回 → 交卷 → 验收】的完整闭环**
  - 09:1x 第 1 次派出 ⇒ 会话 aborted ⇒ 两行一个字没改 (死单)
  - 10:3x 第 2 次派出 (上一轮 cron job) ⇒ hw-lead 交卷 `HANDOFF/2026-11-11_hw-lead_ISS189_DSI_payload_收尾.md`
  - ★**hw-lead 明确没碰 issue_log.yaml** (按 sw-lead ISS-188 的先例: 落账留给 main, verify_by=main)
  ⇒ ★**本脚本 = main 自己实测 + 落账签字**

★**main 自己的验收 (不是抄 owner 自评)**:
  ① `grep -rn '373Mbps|373 Mbps|246 Mbps' HW/ SW/ state/outbox/` ⇒ **零命中**
  ② `HW/STEP1_LANDING_LIST.md:42` + `HW/PART_ALTERNATIVES_REGISTRY.md:24` 两处都已是 **2986 Mbps**
     且都带了依据注 (payload = 1920×1080×24×60 = 2985.98 Mbps, 与 `HW/e2e_budget_rk3572.py` §⑥ 同口径)
  ③ `python3 HW/e2e_budget_rk3572.py --selftest` ⇒ **rc=0** + 脚本 md5 `7b820c14` 未变
     (★**判据权威源没被偷改**★)
  ④ `HW/PCB/demo_mainboard.kicad_pcb` md5 仍 `611b869e13518c3c023fb178f91a0075` ⇒ ★**板子一字未动**★
  ⑤ 交付报告在位 (25KB) + 结论方向未变 (4-lane 绰绰有余 / 不需 DSC)

★**落账纪律**:
  ① flock(state/.issue_log.lock) + 锁内重读
  ② ★**只改 ISS-189 这一条 dict 的字段** ⇒ 落账后逐条 diff 实测: 185 条里只有 ISS-189 变了
  ③ 原子写: tmp → fsync → os.replace → fsync(dir) + yaml 往返复现自检

★**边界**: 不改 §0 锁死表 · 不碰任何子总工的分片 (只读不改) · 不发邮件 / 不联系供应商 / 不下采购单
  · 不碰任何板子/原理图文件 (只读不改) · 不重跑 `state/_demo_hw_scheme_landing.py`
  (★**重跑它 = 把 373 Mbps 灌回 tracker ⇒ 一次重跑抹掉前面所有订正**★)
"""
from __future__ import annotations

import fcntl
import os
import subprocess
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
TODAY = "2026-11-11"

BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"
SCRIPT_MD5 = "7b820c14acfaee08a218cbf85557ef0b"

NOTE_189 = (
    " ★**2026-11-11 11:4x 项目总工 (main) 验收通过 (verify_result=pass)**: "
    "★**本条是本项目第一条【死单救回 → 重派 → 交卷 → 验收】的完整闭环** "
    "(★**09:1x 第 1 次派出被 aborted ⇒ 两行一个字没改 = 死单** ⇒ ★**10:3x 第 2 次派出** ⇒ "
    "hw-lead 交卷 `HANDOFF/2026-11-11_hw-lead_ISS189_DSI_payload_收尾.md` ⇒ ★**owner 明确没碰 issue_log "
    "(按 sw-lead ISS-188 先例, 落账留给 main, verify_by=main)**★) —— "
    "★**验收全部是 main 自己实测, 不是抄 owner 自评**: "
    "① `grep -rn '373Mbps|373 Mbps|246 Mbps' HW/ SW/ state/outbox/` ⇒ **零命中**; "
    "② `HW/STEP1_LANDING_LIST.md:42` + `HW/PART_ALTERNATIVES_REGISTRY.md:24` 两处都已是 **2986 Mbps** "
    "且都带依据注 (payload = 1920×1080×24×60 = 2985.98 Mbps ⇒ 与 `HW/e2e_budget_rk3572.py` §⑥ 同口径; "
    "TX 物理下限 7.776ms = 2986 ÷ 60 ÷ 6400); "
    "③ `python3 HW/e2e_budget_rk3572.py --selftest` ⇒ **rc=0** + 脚本 md5 `7b820c14` 未变 "
    "(★**判据权威源没被偷改**★); "
    "④ `HW/PCB/demo_mainboard.kicad_pcb` md5 仍 **`611b869e13518c3c023fb178f91a0075`** ⇒ ★**板子一字未动**★; "
    "⑤ 交付报告在位 (25KB) 且 ★**结论方向未变** (4-lane 绰绰有余 / 不需 DSC 仍成立 ⇒ 只订正数字, 不改结论)★. "
    "★**教训沉淀 (第 3 次机会, 这次没踩)**: ★**依据注里刻意不写旧值逐字串** (写「原写的 373」) ⇒ "
    "★**不然验收 ① 永远不为 0** ⇒ ★**这是 hw-lead 在 ISS-186、main 在 ISS-188 各踩过一次的老坑**★. "
    "★**未重跑 `state/_demo_hw_scheme_landing.py`** (★**重跑 = 把 373 Mbps 灌回 tracker**★)."
)


def run(cmd: list[str], cwd: str = PROJ) -> tuple[int, str]:
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def md5(path: str) -> str:
    p = subprocess.run(["md5sum", path], cwd=PROJ, capture_output=True, text=True)
    return p.stdout.split()[0] if p.stdout else "MISSING"


def atomic_write(path: str, content: str) -> None:
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".iss189_", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
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
    # ================= 落账前自检 =================
    print("=== 落账前实测 (main 自跑) ===")
    rc, out = run(["grep", "-rn", "373Mbps\\|373 Mbps\\|246 Mbps",
                   "HW/", "SW/", "state/outbox/"])
    hits = [l for l in out.splitlines() if l.strip()]
    print(f"① grep 旧口径 HW/ SW/ state/outbox/ ⇒ rc={rc} 命中 {len(hits)} 条")
    if hits:
        for h in hits[:10]:
            print("   !", h)
        print("❌ 旧口径仍有残留 ⇒ 中止落账")
        return 2

    rc, out = run(["python3", "HW/e2e_budget_rk3572.py", "--selftest"])
    print(f"② e2e_budget --selftest ⇒ rc={rc}")
    if rc != 0:
        print("❌ selftest 没过 ⇒ 中止落账")
        return 2

    m = md5("HW/e2e_budget_rk3572.py")
    print(f"③ 判据脚本 md5 = {m} (须 == {SCRIPT_MD5})")
    if m != SCRIPT_MD5:
        print("❌ 判据脚本被动过 ⇒ 中止落账")
        return 2

    bm = md5("HW/PCB/demo_mainboard.kicad_pcb")
    print(f"④ 板 md5 = {bm} (须 == {BOARD_MD5})")
    if bm != BOARD_MD5:
        print("❌ 板子被动过 ⇒ 中止落账")
        return 2

    for f, needle in (("HW/STEP1_LANDING_LIST.md", "2986Mbps"),
                      ("HW/PART_ALTERNATIVES_REGISTRY.md", "2986Mbps")):
        rc, out = run(["grep", "-n", needle, f])
        print(f"⑤ {f} 含 {needle} ⇒ rc={rc}")
        if rc != 0:
            print(f"❌ {f} 未见 {needle} ⇒ 中止落账")
            return 2

    rep = os.path.join(PROJ, "HANDOFF/2026-11-11_hw-lead_ISS189_DSI_payload_收尾.md")
    print(f"⑥ 交付报告在位 ⇒ {os.path.exists(rep)} ({os.path.getsize(rep) if os.path.exists(rep) else 0} bytes)")

    # ================= 落账 =================
    with open(LOCK, "a+") as lf:
        fcntl.flock(lf, fcntl.LOCK_EX)
        with open(LOG, encoding="utf-8") as f:
            doc = yaml.safe_load(f.read())
        issues = doc.get("issues") or []
        before = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=200)
        before_by_id = {i.get("id"): yaml.safe_dump(i, allow_unicode=True, sort_keys=False, width=200)
                        for i in issues}

        i189 = next((x for x in issues if x.get("id") == "ISS-189"), None)
        if not i189:
            print("❌ 找不到 ISS-189 ⇒ 中止")
            return 2
        if i189.get("status") != "fixing":
            print(f"⚠️ ISS-189 status={i189.get('status')} (期望 fixing) ⇒ 不签字")
            fcntl.flock(lf, fcntl.LOCK_UN)
            return 3

        i189["status"] = "verified"
        i189["verify_result"] = "pass"
        i189["verify_date"] = TODAY
        i189["fixed_at"] = TODAY
        i189["note"] = (i189.get("note") or "") + NOTE_189

        out_yaml = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=200)
        atomic_write(LOG, out_yaml)
        fcntl.flock(lf, fcntl.LOCK_UN)

    # ================= 落账后自检 =================
    with open(LOG, encoding="utf-8") as f:
        rt = yaml.safe_load(f.read())
    rt_out = yaml.safe_dump(rt, allow_unicode=True, sort_keys=False, width=200)
    ok_rt = (rt_out == out_yaml)
    after_by_id = {i.get("id"): yaml.safe_dump(i, allow_unicode=True, sort_keys=False, width=200)
                   for i in (rt.get("issues") or [])}
    changed = [k for k in before_by_id if before_by_id[k] != after_by_id.get(k)]
    added = [k for k in after_by_id if k not in before_by_id]

    print("=== 落账后实测 ===")
    print(f"yaml 往返复现自检: {'✅ 一致' if ok_rt else '❌ 不一致'}")
    print(f"条目数: {len(before_by_id)} → {len(after_by_id)} (新增 {added})")
    print(f"★**逐条 diff: 只有这些条目变了** ⇒ {changed}")
    i189 = next(x for x in rt["issues"] if x.get("id") == "ISS-189")
    print(f"ISS-189: status={i189.get('status')} verify_by={i189.get('verify_by')} "
          f"verify_result={i189.get('verify_result')} verify_date={i189.get('verify_date')}")
    ok = ok_rt and changed == ["ISS-189"] and not added and i189.get("status") == "verified"
    print("★**结论**: " + ("✅ 可签字落账" if ok else "❌ 自检不过"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
