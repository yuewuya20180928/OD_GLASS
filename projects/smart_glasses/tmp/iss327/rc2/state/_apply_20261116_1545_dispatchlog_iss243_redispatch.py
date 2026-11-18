#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20261116_1545_dispatchlog_iss243_redispatch.py
★main (moli) 2026-11-16 15:4x (cron 775d9893 ARS45 继续执行后继计划)★
★**只往 `state/dispatch_log.yaml` 补一条 ISS-243 的【续做重派】记录** ★
★(ISS-243 那条首派已由 `state/advance.py --apply --only ISS-243` 写入 ⇒ 本脚本不重复写★)
"""
import fcntl
import os
import shutil
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
DL = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
TODAY = "2026-11-16"

BRIEF_243_HEAD = (
    "★**续做派活 (★main 2026-11-16 15:4x 实测: 上一轮会话 15:15:04~15:24:10 撞 timeout (runtime 546s · abortedLastRun=true · status=timeout) "
    "⇒ ISS-243 是【零产出僵尸】★) ⇒ ★**本轮重派 · runTimeout 5400s** ★** "
    "★**盘上零产出 (MOS_PAD_PIN_MAPPING.md / 交卷单 / 门禁 三件一件没落 · 网表脚表 BOM 板 4 个 md5 逐字节未变) ⇒ 上一轮 9 分钟全卡在『Murata 官方在售型号抓不到』(curl 长跑) ⇒ "
    "本轮要求: 先落盘骨架再填内容 · L1 落表 (不依赖联网) 先做 · OPN/L4 查不到就写 [0数据] + 降级方案, 不许死磕** ★"
)


def _atomic_write(path: str, data: str) -> None:
    fd, tmp = tempfile.mkstemp(dir=HERE, prefix=".tmp_dl.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(data)
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def main() -> int:
    shutil.copy2(DL, DL + ".bak_20261116_1545_cron_iss243_redispatch")
    lf = open(LOCK, "a+")
    try:
        fcntl.flock(lf, fcntl.LOCK_EX)
        dl = yaml.safe_load(open(DL, encoding="utf-8")) or {"dispatches": []}
        disp = dl.setdefault("dispatches", [])
        if any(d.get("issue") == "ISS-243" and d.get("redispatch") for d in disp):
            print("   - dispatch_log 里已有 ISS-243 重派记录 ⇒ 不重复写")
            return 0
        disp.append({
            "issue": "ISS-243",
            "agent": "hw-lead",
            "at": TODAY,
            "brief": BRIEF_243_HEAD,
            "redispatch": True,
            "reason": (
                "★上一轮 status=timeout/aborted (runtime 546s · abortedLastRun=true · session bdf0ab5c) ⇒ 零产出僵尸: "
                "HW/MOS_PAD_PIN_MAPPING.md 不存在 · HANDOFF/2026-11-16_hw-lead_ISS243_*.md 不存在 · "
                "网表/脚表/BOM/板 4 个 md5 与 15:1x 基线逐字节相同 (34132f7e / b21b743a / c195a117 / 611b869e) ⇒ L1 落表也没发生 ⇒ 仍无交卷 ★"
            ),
            "session_key": "agent:hw-lead:subagent:8f42d87e-22c6-404c-9fd7-81be77ece276",
            "run_id": "9685960b-4335-49f7-b860-4eb49d326bd0",
            "task_name": "advance_iss243",
            "run_timeout_s": 5400,
        })
        _atomic_write(DL, yaml.safe_dump(dl, allow_unicode=True, sort_keys=False, width=100000))
    finally:
        fcntl.flock(lf, fcntl.LOCK_UN)
        lf.close()
    print("   - dispatch_log 补记 ISS-243 续做重派 (session 8f42d87e / run 9685960b)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
