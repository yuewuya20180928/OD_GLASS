#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-325 cont1 dispatch_log 补记 (★上一版 dedupe 被前一条的『下一轮再派 cont1』字样误命中★)"""
from __future__ import annotations
import fcntl, os, shutil, tempfile, yaml

HERE = os.path.dirname(os.path.abspath(__file__))
DL = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
STAMP = "20261118_1426"
MARK = "★派活标记=ISS325-CONT1-20261118-1426★"   # ★唯一标记★


def atomic_write(path, text):
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_", suffix=".yaml")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text); f.flush(); os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def main() -> int:
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        dl = yaml.safe_load(open(DL, encoding="utf-8")) or {}
        disp = dl.get("dispatches") or []
        if any(isinstance(d, dict) and MARK in str(d.get("brief")) for d in disp):
            print("· 已存在 (跳过)")
            return 0
        disp.append({
            "issue": "ISS-325", "agent": "hw-lead", "at": "2026-11-18",
            "brief": (MARK + " ★**cont1 续做 (★上一趟 13:35 被父 run 连带 abort · 但两条沙盒臂【还在后台真跑】 "
                      "PID 1043798 / 1044628 · 已跑 1h20m★)** ★ "
                      "★**绝对不许重跑那两条臂** ⇒ 等它们跑完 → 收割读数 → 填 4 处 `__XXX__` 占位符 "
                      "(★标准占位符扫描对 `__XXX__` 无效·本项目闸有盲区★) + 补 §9 + 补交卷页 B1/B2/B4/B5 "
                      "(★gate_check Q1 现在 15/18·缺的就是这 3 格★) + 写分片 (★hw.yaml 里 `iss325` 命中 = 0★)** ★ "
                      "★**先做与臂无关的 4 件, 再收割臂** ⇒ ★**这样就算又被 abort, 本单也已经从「4 处占位符 + "
                      "缺 §9 + 缺 B1/B2/B4/B5 + 分片未写」推进到「只差臂的读数」** ★ "
                      "★**如实登记**: 本单的臂经 `replay_patch_chain.sh` → `check_pcb_drc.py` → `gen_kicad_project.py` "
                      "重写了 `HW/PCB/` 下 4 个生成器产物 (`STACKUP.md` / `LAYOUT_RULES.md` / `GEN_SELF_CHECK.txt` / "
                      "`_frame_reference.kicad_pcb`) ⇒ ★**除时间戳外内容逐字相同**(已实测 diff) ⇒ **板/网表/脚表/BOM 一个字节未动** ★ "
                      "★**status 全程保持 fixing ⇒ 无 open 窗口 ⇒ 兄弟 job 775d9893 不会重复派** ★"),
            "job": ("cron fb67af40 (ARS45 队列自动派活) · ★派活时刻 2026-11-18 14:2x · "
                    "★**status 全程 fixing ⇒ 无 open 窗口 ⇒ 兄弟 job 775d9893 不会重复派** ★"),
        })
        dl["dispatches"] = disp
        shutil.copy2(DL, DL + ".bak_cronfb67_%s_iss325_cont1_log" % STAMP)
        atomic_write(DL, yaml.safe_dump(dl, allow_unicode=True, sort_keys=False, width=100000))
        print("· dispatch_log 追加 ISS-325 cont1 (★带唯一标记★)")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
