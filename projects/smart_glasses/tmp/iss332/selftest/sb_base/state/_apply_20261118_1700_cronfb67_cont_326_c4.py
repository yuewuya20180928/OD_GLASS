#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-326 cont4 brief 追加 (★status 保持 fixing★) · cron fb67af40 · 2026-11-18 17:00

★**为什么又续做**: cont3 (16:39:09→16:57:2x, 18m14s) 死于 `timed out`, 但它 ★**三件活其实全做完了**★:
  · `logs/iss326/sandbox/` 14 个文件 (RESULTS.md 8,885 B · results.json 5,103 B · case1A/1B/1C/1D · case2 · case3A/3B · case4)
    ⇒ ★**四组反向用例全跑完, 每条有「期望 / 实际 / 判决」** ★
  · `logs/iss326/mech_ref_disposition.tsv` 572,549 B (★处置表★)
  · `logs/iss326/gate_design/GATE_DESIGN.md` 13,443 B + `mech_gate_baseline.json` 22,472 B (★闸设计稿★)
  · 交卷页 17,292 B (B0~B6 六块齐全 · B1 带硬指标表 · B2 带「未验 (故意不做)」诚实项 · 占位符 0)
  · 交付页 27,395 B · 占位符 0 · 分片 iss326 = 2
★**它死前最后一句 = "Adding the hard-indicator→judgment-script mapping (substantive, with real numbers):" ⇒ 这一段没写完**
★⇒ ★**cont4 = 纯收尾三件: ① 补完硬指标→判据脚本映射 ② B6 贴实际输出 ③ 最终回复** ★
★**★不许重跑沙盒用例 (★证据全在盘上·重跑 = 白烧一小时 + 有把读数跑歪的风险★)★**
"""
from __future__ import annotations
import fcntl, os, shutil, tempfile, yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
DL = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
NOW = "2026-11-18"
STAMP = "20261118_1700"
MARK = "★派活标记=CONT-20261118-1700★"
ISS = "ISS-326"
AGENT = "mech-lead"
FN = "ISS-326_mech_s1_rename_safety_audit_cont4.md"


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
        log = yaml.safe_load(open(LOG, encoding="utf-8")) or {}
        issues = log.get("issues") or []
        target = next((i for i in issues if i.get("id") == ISS), None)
        if target is None:
            print("· %s 不存在 (★异常★)" % ISS)
            return 2
        tb = target.get("task_brief") or ""
        if MARK in tb:
            print("· %s %s 已在 brief 里 (跳过)" % (ISS, MARK))
        else:
            body = open(os.path.join(HERE, "dispatch_briefs", FN), encoding="utf-8").read()
            target["task_brief"] = tb + "\n\n---\n\n" + MARK + "\n\n" + body
            print("· %s task_brief += cont4 全文 (★原 brief 全文保留★) · status 保持 fixing" % ISS)
        target["dispatched_at"] = NOW
        target["note"] = (target.get("note") or "") + (
            "\n★**2026-11-18 17:00 · cron fb67af40 续做重派 (cont4)★** "
            "★**cont3 (18m14s) 死于 timed out, 但三件活其实全做完了 (沙盒 14 文件 / 处置表 572 KB / 闸设计稿 13 KB+22 KB / "
            "交卷页 17 KB 六块齐 / 交付页 27 KB / 分片 2 条) ⇒ 死前最后一句停在「补硬指标→判据脚本映射」** "
            "⇒ ★**cont4 = 纯收尾: ① 补完映射 (交卷页 B1 硬指标表加「产出它的判据脚本+行号+复算命令」一列) ② B6 贴实际输出 "
            "(merge/gate/issue_check 三份 + 板 md5 双证 + 占位符 + 软链数) ③ 最终回复 (含假绿/崩/半改必红/注释无影响 四条已实证结论)** "
            "★**不许重跑沙盒用例** ★")

        out = dict(log); out["issues"] = issues
        shutil.copy2(LOG, LOG + ".bak_cronfb67_%s_cont_326_c4" % STAMP)
        atomic_write(LOG, yaml.safe_dump(out, allow_unicode=True, sort_keys=False, width=100000))

        dl = yaml.safe_load(open(DL, encoding="utf-8")) or {}
        disp = dl.get("dispatches") or []
        if not any(isinstance(d, dict) and d.get("issue") == ISS and MARK in str(d.get("brief")) for d in disp):
            disp.append({
                "issue": ISS, "agent": AGENT, "at": NOW,
                "brief": MARK + " ★**cont3 三件活全做完但死在「补硬指标→判据脚本映射」⇒ cont4 = 纯收尾 (映射 + B6 实际输出 + 最终回复) · 不许重跑沙盒** ★",
                "job": ("cron fb67af40 (ARS45 队列自动派活) · ★派活时刻 2026-11-18 17:00 · "
                        "★**续做重派 (status 保持 fixing ⇒ 无 open 窗口·兄弟 job 775d9893 不会重复派)** ★"),
            })
            print("· dispatch_log 追加 %s cont4" % ISS)
        dl["dispatches"] = disp
        shutil.copy2(DL, DL + ".bak_cronfb67_%s_cont_326_c4" % STAMP)
        atomic_write(DL, yaml.safe_dump(dl, allow_unicode=True, sort_keys=False, width=100000))
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
