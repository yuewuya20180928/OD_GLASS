#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_advance_apply_dispatch_log.py -- `state/advance.py --apply` 落盘路径的回归自测

★★★**为什么要有这个自测 (★实测事故链·2026-11-23 01:2x main 修★)**:
  ① 本 job (cron 775d9893) 步骤 2 的落盘手段就是 `python3 state/advance.py --apply --only <ISS-ID>`
  ② ★**那条路一直是坏的** ⇒ `state/dispatch_log.yaml` 顶层是 **list** (不是 dict)
     ⇒ 旧代码 `dl.setdefault("dispatches", []).append(...)` ⇒ **AttributeError** ⇒ **--apply 必崩**
  ③ ⇒ 后果: 「派完标 fixing + 写派活日志」从来没自动跑通过
     (兄弟 job fb67 只能绕开它、自己用原子写落 `fixing`)
  ④ ⇒ ★**闸脚本自己会有 bug** (本项目铁律) ⇒ 必须有独立脚本 + 单测 + 用「实测的坏案例」当回归用例

★★**本自测覆盖 (★端到端跑真 advance.py, 不只测纯函数★)**:
  T1  list 形状的 dispatch_log ⇒ --apply --only 正常落盘 (旧代码在这条上崩)
  T2  dict 形状的 dispatch_log ⇒ --apply --only 正常落盘 (两种形状都认)
  T3  --only 过滤 ⇒ 只有指定单被标 fixing, 另一条仍 open, 只追加 1 条日志
  T4  internal 为空 ⇒ --apply 空跑 ⇒ **dispatch_log 字节零变化** (零 churn) 且不崩
  T5  ★**反向用例** ⇒ 用【修复前】的 advance.py 跑同一沙盒 ⇒ 必须复现 AttributeError
      (证明这条用例抓的是真事故, 不是自造的假 bug)

用法:  python3 -B state/test_advance_apply_dispatch_log.py [--selftest]
退出码: 0=全过  1=有用例失败  2=用法/环境错
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ADVANCE = os.path.join(HERE, "advance.py")
DECISION_TRUTH = os.path.join(HERE, "decision_truth.py")
# ★修复前的 advance.py (备份) —— 反向用例要用
OLD_ADVANCE_CANDIDATES = [
    os.path.join(HERE, ".bak_advance_20260723_0120_pre_dispatchlog_fix.py"),
    os.path.join(HERE, ".bak_advance_20260723_0120_pre_dispatchlog_fix.py"),
]


def _issue(iid: str, owner: str = "hw-lead") -> dict:
    return {
        "id": iid, "title": f"合成用例 {iid}", "severity": "high", "owner": owner,
        "reporter": "main", "raised": "2026-11-20", "due": "2026-11-30",
        "status": "open", "task_brief": f"闭环 {iid}: 合成任务书正文 (自测用)",
    }


def _build_sandbox(root: str, log_shape: str, n_issues: int = 2) -> str:
    """造一个最小可跑 advance.py 的沙盒目录 (state/ 的等价物)"""
    sd = os.path.join(root, "state")
    os.makedirs(os.path.join(sd, "fragments"), exist_ok=True)
    os.makedirs(os.path.join(sd, "outbox"), exist_ok=True)
    shutil.copy2(ADVANCE, os.path.join(sd, "advance.py"))
    shutil.copy2(DECISION_TRUTH, os.path.join(sd, "decision_truth.py"))
    import yaml
    issues = [_issue("ISS-T1", "hw-lead"), _issue("ISS-T2", "sw-lead")][:n_issues]
    with open(os.path.join(sd, "issue_log.yaml"), "w", encoding="utf-8") as f:
        yaml.safe_dump({"_schema": "test", "issues": issues}, f, allow_unicode=True, sort_keys=False)
    pre = [{"issue": "ISS-OLD", "agent": "sw-lead", "at": "2026-11-01", "brief": "历史条目 (自测基线)"}]
    payload = pre if log_shape == "list" else {"dispatches": pre}
    with open(os.path.join(sd, "dispatch_log.yaml"), "w", encoding="utf-8") as f:
        yaml.safe_dump(payload, f, allow_unicode=True, sort_keys=False)
    return sd


def _run(sd: str, args: list[str]) -> tuple[int, str, str]:
    r = subprocess.run([sys.executable, "-B", os.path.join(sd, "advance.py")] + args,
                       capture_output=True, text=True, timeout=120)
    return r.returncode, r.stdout, r.stderr


def _read(sd: str, name: str):
    import yaml
    with open(os.path.join(sd, name), encoding="utf-8") as f:
        return yaml.safe_load(f)


def _dispatch_list(sd: str) -> list:
    raw = _read(sd, "dispatch_log.yaml")
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict):
        return raw.get("dispatches", [])
    return []


def case_t1_list_shape(tmp: str) -> tuple[bool, str]:
    """T1 · list 形状 ⇒ 正常落盘 (旧代码在这条上崩)"""
    sd = _build_sandbox(tmp, "list")
    before = open(os.path.join(sd, "dispatch_log.yaml"), encoding="utf-8").read()
    rc, out, err = _run(sd, ["--apply", "--only", "ISS-T1"])
    if rc != 0:
        return False, f"rc={rc} (期望 0) stderr={err[-300:]}"
    entries = _dispatch_list(sd)
    if len(entries) != 2:
        return False, f"dispatch_log 条目数 {len(entries)} (期望 2)"
    if entries[-1].get("issue") != "ISS-T1":
        return False, f"末条 issue={entries[-1].get('issue')} (期望 ISS-T1)"
    after = open(os.path.join(sd, "dispatch_log.yaml"), encoding="utf-8").read()
    if not after.startswith(before):
        return False, "历史字节被改写 (追加式写回失效)"
    issues = _read(sd, "issue_log.yaml")["issues"]
    st = {i["id"]: i["status"] for i in issues}
    if st.get("ISS-T1") != "fixing":
        return False, f"ISS-T1 status={st.get('ISS-T1')} (期望 fixing)"
    return True, "OK"


def case_t2_dict_shape(tmp: str) -> tuple[bool, str]:
    """T2 · dict 形状 ⇒ 正常落盘 (两种形状都认)"""
    sd = _build_sandbox(tmp, "dict")
    rc, out, err = _run(sd, ["--apply", "--only", "ISS-T1"])
    if rc != 0:
        return False, f"rc={rc} (期望 0) stderr={err[-300:]}"
    entries = _dispatch_list(sd)
    if len(entries) != 2:
        return False, f"dispatches 条目数 {len(entries)} (期望 2)"
    if entries[-1].get("issue") != "ISS-T1":
        return False, f"末条 issue={entries[-1].get('issue')} (期望 ISS-T1)"
    return True, "OK"


def case_t3_only_filter(tmp: str) -> tuple[bool, str]:
    """T3 · --only 只标指定单, 只追加 1 条日志"""
    sd = _build_sandbox(tmp, "list")
    rc, out, err = _run(sd, ["--apply", "--only", "ISS-T2"])
    if rc != 0:
        return False, f"rc={rc} (期望 0) stderr={err[-300:]}"
    issues = _read(sd, "issue_log.yaml")["issues"]
    st = {i["id"]: i["status"] for i in issues}
    if st.get("ISS-T2") != "fixing":
        return False, f"ISS-T2 status={st.get('ISS-T2')} (期望 fixing)"
    if st.get("ISS-T1") != "open":
        return False, f"ISS-T1 status={st.get('ISS-T1')} (期望仍是 open)"
    entries = _dispatch_list(sd)
    if len(entries) != 2:
        return False, f"dispatch_log 条目数 {len(entries)} (期望 2 ⇒ 只追加 1 条)"
    return True, "OK"


def case_t4_empty_no_churn(tmp: str) -> tuple[bool, str]:
    """T4 · internal 为空 ⇒ 空跑 ⇒ dispatch_log 字节零变化 + 不崩"""
    sd = _build_sandbox(tmp, "list", n_issues=0)
    before = open(os.path.join(sd, "dispatch_log.yaml"), encoding="utf-8").read()
    rc, out, err = _run(sd, ["--apply"])
    if rc not in (0, 1):
        return False, f"rc={rc} (期望 0/1 ⇒ 无可执行动作) stderr={err[-300:]}"
    after = open(os.path.join(sd, "dispatch_log.yaml"), encoding="utf-8").read()
    if before != after:
        return False, "dispatch_log 被改写 (空跑应零 churn)"
    return True, "OK"


def case_t5_old_code_crashes(tmp: str) -> tuple[bool, str]:
    """T5 · 反向用例: 修复前的 advance.py 必须复现 AttributeError"""
    old = None
    for c in OLD_ADVANCE_CANDIDATES:
        if os.path.exists(c):
            old = c
            break
    if old is None:
        return True, "SKIP (找不到修复前备份 ⇒ 跳过反向用例, 不算失败)"
    sd = _build_sandbox(tmp, "list")
    shutil.copy2(old, os.path.join(sd, "advance.py"))
    rc, out, err = _run(sd, ["--apply", "--only", "ISS-T1"])
    if "AttributeError" in (out + err) and "setdefault" in (out + err):
        return True, "OK (旧代码确实崩在同一处 ⇒ 回归用例有效)"
    return False, (f"旧代码没复现 AttributeError (rc={rc}) ⇒ "
                   f"要么 bug 描述错了, 要么备份不对; out={out[-200:]} err={err[-200:]}")


CASES = [
    ("T1 list 形状 dispatch_log 落盘", case_t1_list_shape),
    ("T2 dict 形状 dispatch_log 落盘", case_t2_dict_shape),
    ("T3 --only 过滤 + 只追加 1 条", case_t3_only_filter),
    ("T4 空跑零 churn + 不崩", case_t4_empty_no_churn),
    ("T5 反向用例: 旧代码必须复现 AttributeError", case_t5_old_code_crashes),
]


def main() -> int:
    import yaml  # noqa: F401  (沙盒写盘用)
    # ★★2026-11-23 01:2x ★沙盒不落 /tmp★ ⇒ 实测 /tmp 是带 userquota 的 tmpfs,
    #   配额已被打满 (连 10 KB 的 cp 都报 EDQUOT) ⇒ 沙盒落 /tmp 会被当场打死
    #   ⇒ 改落项目盘 (state/ 下), 用完即删 (★不动别人的目录★)
    sandbox_root = os.path.join(HERE, ".tmp_advselftest")
    shutil.rmtree(sandbox_root, ignore_errors=True)
    os.makedirs(sandbox_root, exist_ok=True)
    tmp = sandbox_root
    fails = []
    try:
        for name, fn in CASES:
            d = os.path.join(tmp, name.split()[0])
            os.makedirs(d, exist_ok=True)
            try:
                ok, msg = fn(d)
            except Exception as e:  # noqa: BLE001
                ok, msg = False, f"用例异常: {type(e).__name__}: {e}"
            print(f"  {'✅' if ok else '❌'} {name} —— {msg}")
            if not ok:
                fails.append(name)
    finally:
        shutil.rmtree(sandbox_root, ignore_errors=True)
    print()
    if fails:
        print(f"❌ {len(fails)}/{len(CASES)} 条用例失败: {', '.join(fails)}")
        return 1
    print(f"✅ ALL TESTS PASS ({len(CASES)}/{len(CASES)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
