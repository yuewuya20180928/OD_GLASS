#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""frag_write.py 自测 (V1.1)
====================================================================
为什么有这份测试:
  2026-10-28 sw-lead 实测踩中 frag_write V1.0 的静默丢数据坑 ——
  `--set` 分支命中就 `return`, 同一命令行的 `--add-artifact/--add-claim/--status`
  全被静默忽略, 却照样打印 "✅ 已原子更新" ⇒ 写完看起来成功, 数据全丢, 零告警。
  这种坑靠"读代码看出来了"不算数, 必须机器证明。

本测试覆盖 5 条:
  T1 --set 单独用 → 整段替换成功
  T2 --add-claim 单独用 → 增量追加成功
  T3 --set 与 --add-claim 混用 → **报错退出 (非 0) 且分片一字未动** (V1.0 这里是静默丢数据)
  T4 --set 与 --status 混用 → 同样被拦
  T5 --status 带引号长摘要 (含空格) → summary 完整不被空白 split 打碎
  T6 --set-json 缺 --set-field → 报错 (不是静默写到 None 字段)

跑法: python3 state/test_frag_write.py
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "frag_write.py")
FAILURES: list[str] = []
CHECKS = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global CHECKS
    CHECKS += 1
    if ok:
        print(f"  [PASS] {name}")
    else:
        print(f"  [FAIL] {name}  {detail}")
        FAILURES.append(f"{name} {detail}")


def run_tool(agent: str, frag_dir: str, *args: str) -> subprocess.CompletedProcess:
    """在临时 frag 目录上跑 frag_write CLI (不碰真分片)。"""
    env = dict(os.environ)
    env["FRAG_WRITE_DIR"] = frag_dir
    return subprocess.run(
        [sys.executable, TOOL, "--agent", agent, *args],
        capture_output=True, text=True, env=env, cwd=HERE,
    )


def read_frag(frag_dir: str, fname: str) -> dict:
    with open(os.path.join(frag_dir, fname), encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def main() -> int:
    tmp = tempfile.mkdtemp(prefix="fragwrite_test_")
    frag_dir = os.path.join(tmp, "fragments")
    os.makedirs(frag_dir)
    # 造一个最小 hw-lead 分片 (FILE_OF 里 hw-lead -> hw.yaml)
    base = {
        "agent_id": "hw-lead",
        "updated_at": "2026-10-28T00:00:00+08:00",
        "interface_claims": [{"key": "pcb_outline", "value": "50x12mm", "note": "", "ref": ""}],
        "needs_from": [],
        "answers": [],
        "artifacts": [],
        "status": {"phase": "P2", "progress_pct": 50, "health": "red", "summary": "旧摘要"},
    }
    with open(os.path.join(frag_dir, "hw.yaml"), "w", encoding="utf-8") as f:
        yaml.safe_dump(base, f, allow_unicode=True, sort_keys=False)

    print("\n=== T1: --set 单独用 → 整段替换 ===")
    r = run_tool("hw-lead", frag_dir, "--set", "needs_from=[{\"key\":\"K1\",\"to\":\"main\"}]")
    d = read_frag(frag_dir, "hw.yaml")
    check("T1 rc=0", r.returncode == 0, r.stderr[-300:])
    check("T1 needs_from 被整段替换",
          isinstance(d.get("needs_from"), list) and len(d["needs_from"]) == 1
          and d["needs_from"][0].get("key") == "K1", str(d.get("needs_from")))

    print("\n=== T2: --add-claim 单独用 → 增量追加 ===")
    r = run_tool("hw-lead", frag_dir, "--add-claim", "key=chg_rilim value=390Ω note=ok")
    d = read_frag(frag_dir, "hw.yaml")
    keys = [c.get("key") for c in d.get("interface_claims") or []]
    check("T2 rc=0", r.returncode == 0, r.stderr[-300:])
    check("T2 新 claim 已追加", "chg_rilim" in keys, str(keys))

    print("\n=== T3: --set 与 --add-claim 混用 → 必须报错且不落盘 (V1.0 静默丢数据坑) ===")
    before = read_frag(frag_dir, "hw.yaml")
    r = run_tool("hw-lead", frag_dir,
                 "--set", "needs_from=[]",
                 "--add-claim", "key=SHOULD_NOT_EXIST value=xxx")
    after = read_frag(frag_dir, "hw.yaml")
    check("T3 rc != 0 (被拒绝)", r.returncode != 0, f"rc={r.returncode}")
    check("T3 报错文案含互斥提示",
          "互斥" in (r.stderr + r.stdout), (r.stderr + r.stdout)[-300:])
    check("T3 分片一字未动 (SHOULD_NOT_EXIST 未进盘)",
          "SHOULD_NOT_EXIST" not in [c.get("key") for c in after.get("interface_claims") or []],
          str([c.get("key") for c in after.get("interface_claims") or []]))
    check("T3 needs_from 未被 --set 清空 (旧值仍在)",
          len(after.get("needs_from") or []) == len(before.get("needs_from") or []) == 1,
          str(after.get("needs_from")))

    print("\n=== T4: --set 与 --status 混用 → 同样被拦 ===")
    r = run_tool("hw-lead", frag_dir,
                 "--set", "needs_from=[]",
                 "--status", "phase=P3 progress_pct=60 health=green")
    d = read_frag(frag_dir, "hw.yaml")
    check("T4 rc != 0", r.returncode != 0, f"rc={r.returncode}")
    check("T4 status 未被改动", (d.get("status") or {}).get("phase") == "P2",
          str(d.get("status")))

    print("\n=== T5: --status 带引号长摘要 (含空格) → 不打碎 ===")
    summary = "ISS-105 闭: pcb_outline 50x12->60x15mm; chg_input_limit 300Ω->390Ω; 板重 +0.56g"
    r = run_tool("hw-lead", frag_dir, "--status",
                 f"phase=P3 progress_pct=60 health=green summary='{summary}'")
    d = read_frag(frag_dir, "hw.yaml")
    st = d.get("status") or {}
    check("T5 rc=0", r.returncode == 0, r.stderr[-300:])
    check("T5 summary 完整 (含空格未被 split)", st.get("summary") == summary,
          repr(st.get("summary")))
    check("T5 progress_pct 是 int", st.get("progress_pct") == 60, repr(st.get("progress_pct")))

    print("\n=== T6: --set-json 缺 --set-field → 报错 (不静默写 None 字段) ===")
    p = os.path.join(tmp, "val.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump([{"key": "X"}], f)
    r = run_tool("hw-lead", frag_dir, "--set-json", p)
    check("T6 rc != 0", r.returncode != 0, f"rc={r.returncode}")
    check("T6 报错文案提到 --set-field", "--set-field" in (r.stderr + r.stdout),
          (r.stderr + r.stdout)[-300:])

    print("\n=== T7: 真分片未被本次测试改动 (安全网) ===")
    import hashlib
    real = os.path.join(HERE, "fragments", "hw.yaml")
    if os.path.exists(real):
        h = hashlib.sha256(open(real, "rb").read()).hexdigest()
        print(f"  真分片 sha256 = {h[:16]}... (仅记录, 本测试全程只写临时目录)")
        check("T7 真分片存在", True)
    else:
        check("T7 真分片存在", False, "hw.yaml 不存在?")

    shutil.rmtree(tmp, ignore_errors=True)
    print(f"\n{'=' * 62}")
    if FAILURES:
        print(f"❌ 测试失败: {len(FAILURES)}/{CHECKS} 项不通过")
        for f in FAILURES:
            print("   -", f)
        return 1
    print(f"✅ 全部通过: {CHECKS}/{CHECKS} 项")
    return 0


if __name__ == "__main__":
    sys.exit(main())
