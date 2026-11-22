#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-326 cont5 brief 追加 (★status 保持 fixing★) · cron fb67af40 · 2026-11-18 17:08

★**为什么又续做**: cont4 (16:59:47→17:06:14, 6m28s) 死于 `This operation was aborted` ⇒ ★**它读了 6 分钟, 一个字节都没写** ★
★**⇒ 「先落骨架再干活」的第一动作必须是【写】而不是【读】** ⇒ ★**cont5 的第一动作 = write (★B6 实际输出·★不许先读文件★)★ ★
★**好消息**: cont3 已经把 B1 的 12 类硬指标表写完了 ⇒ ★**cont5 不用再补数字, 只补「哪条判据脚本的哪一行产出它」那一列 + B6 实际输出 + 最终回复** ★
"""
from __future__ import annotations
import fcntl, os, shutil, tempfile, yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
DL = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
NOW = "2026-11-18"
STAMP = "20261118_1708"
MARK = "★派活标记=CONT-20261118-1708★"
ISS = "ISS-326"
AGENT = "mech-lead"
FN = "ISS-326_mech_s1_rename_safety_audit_cont5.md"


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
            print("· %s task_brief += cont5 全文 (★原 brief 全文保留★) · status 保持 fixing" % ISS)
        target["dispatched_at"] = NOW
        target["note"] = (target.get("note") or "") + (
            "\n★**2026-11-18 17:08 · cron fb67af40 续做重派 (cont5)★** "
            "★**cont4 (6m28s) 死于 `This operation was aborted` ⇒ 它读了 6 分钟一个字节都没写** "
            "⇒ ★**⇒ 打法第三版: 第一动作 = write (B6 实际输出), 读只在写完之后补** ★ "
            "★**cont3 已把 B1 的 12 类硬指标表写完 ⇒ cont5 不用补数字, 只补「哪条判据脚本的哪一行产出它」那一列 + B6 实际输出 + 最终回复** ★ "
            "★**不许重跑沙盒用例** ★")

        out = dict(log); out["issues"] = issues
        shutil.copy2(LOG, LOG + ".bak_cronfb67_%s_cont_326_c5" % STAMP)
        atomic_write(LOG, yaml.safe_dump(out, allow_unicode=True, sort_keys=False, width=100000))

        dl = yaml.safe_load(open(DL, encoding="utf-8")) or {}
        disp = dl.get("dispatches") or []
        if not any(isinstance(d, dict) and d.get("issue") == ISS and MARK in str(d.get("brief")) for d in disp):
            disp.append({
                "issue": ISS, "agent": AGENT, "at": NOW,
                "brief": MARK + " ★**cont4 读了 6 分钟零输出 ⇒ cont5 第一动作 = write (B6 实际输出) · 只补「判据脚本+行号+复算命令」一列 + 最终回复** ★",
                "job": ("cron fb67af40 (ARS45 队列自动派活) · ★派活时刻 2026-11-18 17:08 · "
                        "★**续做重派 (status 保持 fixing ⇒ 无 open 窗口·兄弟 job 775d9893 不会重复派)** ★"),
            })
            print("· dispatch_log 追加 %s cont5" % ISS)
        dl["dispatches"] = disp
        shutil.copy2(DL, DL + ".bak_cronfb67_%s_cont_326_c5" % STAMP)
        atomic_write(DL, yaml.safe_dump(dl, allow_unicode=True, sort_keys=False, width=100000))
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
