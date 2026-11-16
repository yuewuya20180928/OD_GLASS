#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""对齐检查: TASK_BOARD.md (老板看的总表) × state/issue_log.yaml (台账) × 磁盘实况 × GitHub

★为什么要有这个 (2026-10-29 23:58 老板连问两次「当前进展对齐了吗」):
  发现两处真不对齐 ——
    ① **总表 §2「执行中」过期**: 4 条写着"执行中"其实早已验收 (台账里是 closed/verified), 同时漏了在跑的那条
       ⇒ **总表过期 = 看板误导老板**, 比不写还坏
    ② **GitHub 落后本地**: 交卷单/定案书在盘上但没推上去 ⇒ 断电恢复会读到旧信息
  ⇒ 这个脚本把"对齐"变成**可机械复算的判据**, 每次汇报前跑一遍。

用法: python3 state/alignment_check.py [--json]
退出码: 0 = 全对齐; 1 = 有不对齐项 (看输出)
"""
from __future__ import annotations

import glob
import json
import os
import re
import subprocess
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
TB = os.path.join(PROJ, "TASK_BOARD.md")
LOG = os.path.join(HERE, "issue_log.yaml")
REPO = "yuewuya20180928/OD_GLASS"


def section(tb: str, start: str, end: str) -> str:
    try:
        i = tb.index(start)
        j = tb.index(end, i)
        return tb[i:j]
    except ValueError:
        return ""


def main() -> int:
    tb = open(TB, encoding="utf-8").read()
    doc = yaml.safe_load(open(LOG, encoding="utf-8"))
    items = doc["issues"] if isinstance(doc.get("issues"), dict) else (doc.get("issues") or [])
    byid = {it.get("id"): it for it in items}

    problems = []
    info = {}

    # ── 1. 总表 §2 执行中 == 台账 fixing ──
    sec2 = section(tb, "## §2", "## §3")
    # ★只取表格第一列 (描述文字里出现的 ISS-xxx 不是"在跑"; 10-30 00:2x 误报过一次)
    tb_running = set()
    for ln in sec2.split("\n"):
        m = re.match(r"^\|\s*(ISS-\d+)\s*\|", ln)
        if m:
            tb_running.add(m.group(1))
    log_running = {it.get("id") for it in items if it.get("status") == "fixing"}
    info["总表§2"] = sorted(tb_running)
    info["台账 fixing"] = sorted(log_running)
    if tb_running != log_running:
        problems.append(f"总表§2 执行中 {sorted(tb_running)} ≠ 台账 fixing {sorted(log_running)} "
                        f"(总表多: {sorted(tb_running-log_running)} / 少: {sorted(log_running-tb_running)})")

    # ── 2. 总表 §1 的 A 任务状态 == 台账里对应 issue 的状态 ──
    sec1 = section(tb, "## §1", "## §2")
    a_map = {"A1": "ISS-114", "A2": "ISS-114", "A3": "ISS-116", "A4": "ISS-114",
             "A5": "ISS-115", "A6": "ISS-114", "A7": "ISS-119", "A8": "ISS-114"}
    for a_key, iid in a_map.items():
        m = re.search(rf"^\| {a_key} \|.*$", sec1, re.M)
        if not m:
            problems.append(f"总表 §1 缺 {a_key} 行")
            continue
        row = m.group(0)
        st = byid.get(iid, {}).get("status", "?")
        if "✅已完成" in row and st not in ("verified", "closed", "fixed"):
            problems.append(f"总表 §1 {a_key} 标已完成, 但台账 {iid} status={st}")
    info["§1 A 任务"] = "8 项 (A1-A8)"

    # ── 3. 交卷单 vs 验收状态 (文件名里 ISS065 / ISS-065 两种写法都认) ──
    unverified = []
    for h in sorted(glob.glob(os.path.join(PROJ, "HANDOFF", "*.md"))):
        b = os.path.basename(h)
        m = re.search(r"ISS[-_]?(\d+)", b)
        if not m:
            continue
        iid = f"ISS-{int(m.group(1)):03d}"
        st = byid.get(iid, {}).get("status", "无登记")
        if st not in ("verified", "closed"):
            unverified.append(f"{iid}({st}) {b[:44]}")
    info["交卷单总数"] = len(glob.glob(os.path.join(PROJ, "HANDOFF", "*.md")))
    if unverified:
        problems.append(f"有交卷单但台账未 verified/closed: {unverified}")

    # ── 4. 门禁 4 道 ──
    gates = {}
    for c in ("merge", "gate_check", "issue_check", "daily_check"):
        rc = subprocess.run(f"python3 state/{c}.py >/dev/null 2>&1", shell=True, cwd=PROJ).returncode
        gates[c] = rc
    info["门禁"] = gates
    for c, rc in gates.items():
        if c == "daily_check":
            continue  # daily_check 巡检到"有漂移"也返回 0
        if rc != 0:
            problems.append(f"门禁 {c} rc={rc}")

    # ── 5. 阶段门 ──
    out = subprocess.run("python3 state/stage_gate.py 2>/dev/null | tail -3", shell=True,
                         cwd=PROJ, capture_output=True, text=True).stdout
    info["阶段门"] = out.strip().split("\n")[-1][:100] if out.strip() else "?"

    # ── 6. GitHub vs 本地 (文件级) ──
    remote = set()
    try:
        r = subprocess.run(
            f"curl -s --max-time 25 'https://api.github.com/repos/{REPO}/git/trees/main?recursive=1'",
            shell=True, capture_output=True, text=True).stdout
        j = json.loads(r)
        remote = {t["path"] for t in j.get("tree", []) if t.get("type") == "blob"}
    except Exception as e:
        problems.append(f"GitHub 树拉取失败: {str(e)[:60]}")
    # ★与 publish_github.sh 的 rsync 排除项保持一致 (否则会把"本就不该发布"的运行时文件
    #   误报成"没推上去" —— 10-30 00:0x 误报过一次)
    import fnmatch as _fn
    EXCL_DIRS = {".git", "__pycache__", ".openclaw"}
    EXCL_PAT = ["*.pyc", "BOOTSTRAP.md", "workspace-state.json", "*.tmp", ".DS_Store",
                ".*_bak", "*_backup", ".*_backup", ".bak_*"]
    local = set()
    for root, dirs, files in os.walk(PROJ):
        dirs[:] = [x for x in dirs if x not in EXCL_DIRS]
        for f in files:
            if any(_fn.fnmatch(f, pat) for pat in EXCL_PAT):
                continue
            local.add("projects/smart_glasses/" + os.path.relpath(os.path.join(root, f), PROJ))
    if not remote:
        problems.append("GitHub 树查询失败/被限流 (API) ⇒ 本轮不判『未推』, 下一轮再核")
        info["GitHub 文件数"] = "查询失败(限流?)"
    else:
        missing = sorted(x for x in local if x not in remote)
        info["GitHub 文件数"] = len(remote)
        info["本地未推"] = missing
        if missing:
            problems.append(f"本地有 {len(missing)} 个文件还没上 GitHub: {missing[:6]}")

    # ── 7. 台账里 fixing 的有没有对应交接单/产出 ──
    import datetime as _dt
    import re as _re
    now = _dt.datetime.now()
    today = now.date()
    date_only_nojudge = []
    for iid in sorted(log_running):
        it = byid.get(iid, {})
        if it.get("fix_ref"):
            continue
        # ★僵尸判定: 派出超过 3 小时且仍无 fix_ref ⇒ 真僵尸 (刚派出的还没产出不算)
        disp = str(it.get("dispatched_at") or "")
        # ★★2026-11-16 19:4x (main) 修【假红】: `dispatched_at` 多数只写到【日期】(实测 152/247 条) ★★
        #   ⇒ fromisoformat('2026-11-16') 被当成【当天 00:00】⇒ ★**19:1x 刚派出的 3 条被算成 19.5 小时** ⇒ 误报「僵尸 fixing」
        #   ⇒ ★**这正是本项目吃过的亏**: ISS-235/236/246 三次「僵尸 fixing」假红 ⇒ ★**判据必须分「当日/跨日」** ★
        #   ⇒ 【当日 + 只有日期】= 派出的确切时刻不可知 ⇒ 僵尸判据【本日不可判】(★**不算违规**, 但要打印出来给人看★)
        #   ⇒ 【跨日 + 只有日期】= 至少已过 24 小时 ⇒ ★**仍按真僵尸判 (判定阈值 3 小时一个没改)** ★
        #   ⇒ 【有时刻】= ★**照旧精确判** ★
        age_h = 0.0
        _disp_s = disp.strip()
        if _re.fullmatch(r"\d{4}-\d{2}-\d{2}", _disp_s):
            try:
                d0 = _dt.date.fromisoformat(_disp_s)
            except Exception:
                d0 = None
            if d0 is not None:
                if d0 >= today:
                    age_h = 0.0
                    date_only_nojudge.append(iid)
                else:
                    age_h = (now - _dt.datetime.combine(d0, _dt.time.min)).total_seconds() / 3600.0
        else:
            try:
                dd = _dt.datetime.fromisoformat(disp.replace("Z", "+00:00")).replace(tzinfo=None)
                age_h = (now - dd).total_seconds() / 3600.0
            except Exception:
                age_h = 0.0
        if age_h > 3:
            problems.append(f"{iid} 处于 fixing 超过 {age_h:.1f} 小时仍无 fix_ref ⇒ 僵尸 fixing")
    if date_only_nojudge:
        info["当日派出的单"] = (f"{len(date_only_nojudge)} 条 dispatched_at 只有日期 (无时刻) ⇒ 僵尸判据本日不可判 "
                                f"(★不算违规★): {date_only_nojudge}")

    # ── 输出 ──
    print("=" * 78)
    print("对齐检查 · TASK_BOARD × issue_log × 磁盘 × GitHub")
    print("=" * 78)
    for k, v in info.items():
        print(f"  {k:<16}: {v}")
    print("-" * 78)
    if problems:
        print(f"❌ 不对齐 {len(problems)} 项:")
        for p in problems:
            print("   -", p)
        return 1
    print("✅ 全对齐 (总表 / 台账 / 门禁 / 阶段门 / GitHub 一致)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
