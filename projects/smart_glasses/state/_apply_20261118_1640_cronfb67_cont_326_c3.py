#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-326 cont3 brief 追加 (★status 保持 fixing★) · cron fb67af40 · 2026-11-18 16:40

★**为什么又续做**: cont2 (16:26:04→16:32:33, 6m1s, 72k tokens) 死于
  ★**`LLM idle timeout (120s): no response from model`** (★provider 侧抖动·同刻 sw/hw 两个会话都正常⇒ 不是任务的问题★)
  ⇒ ★**但它一个字节都没落盘** (★交卷页 1,593 B · 交付页 4,868 B · 三件证据目录不存在 · 分片 iss326 命中 0·它当时在读 SW 闸源码★)
  ⇒ ★★⇒ cont3 的打法改了: ★**第一动作 = 落骨架 (交卷页六块 + 交付页骨架 + 一条分片), 然后才允许读源码** ★★
  ⇒ ★**这样再挂也留得下一个闸链认的骨架 ⇒ 下一趟不是从零开始** ★

★**另两件的现场读数 (main 16:33 实跑)★**:
  · gate_check.py **rc=1 (红)**: Q7 行下挂「新闸红: SW 侧位号引用可达性闸 (ISS-318)」⇒
    命中 `SW/ONETRIP_SW_POSTRENAME_GATE_SOP.md:535~539` 的反向测试夹具假位号
    (TP_TEMP_ISSX / TP_TEMP_ISSX2 / CONN_USB_ISSX / U_TEMP_1) ⇒ 真隐患 8 > 基线 3
    ⇒ ★**红在 SW 侧 (sw-lead cont3 正在写的 SOP 中间态) ⇒ 不在 mech 侧 ⇒ cont3 只贴读数 + 说明, 不许去改 SW 文档/闸** ★
  · **Q5 硬指标覆盖 0/3** ⇒ ★**mech 的交卷页必须给出 ≥3 类带数字的硬指标, 写成一张小表放在 B1/B2** ★
  · Q1 = 14/18 (hw 6/6 · sw 6/6 · **mech 2/6 缺 B2/B3/B4/B5**) · Q3 interface_claims 976 条
"""
from __future__ import annotations
import fcntl, os, shutil, tempfile, yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
DL = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
NOW = "2026-11-18"
STAMP = "20261118_1640"
MARK = "★派活标记=CONT-20261118-1640★"
ISS = "ISS-326"
AGENT = "mech-lead"
FN = "ISS-326_mech_s1_rename_safety_audit_cont3.md"


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
        target = None
        for i in issues:
            if i.get("id") == ISS:
                target = i
        if target is None:
            print("· %s 不存在 (★异常★)" % ISS)
            return 2
        tb = target.get("task_brief") or ""
        if MARK in tb:
            print("· %s %s 已在 brief 里 (跳过)" % (ISS, MARK))
        else:
            body = open(os.path.join(HERE, "dispatch_briefs", FN), encoding="utf-8").read()
            target["task_brief"] = tb + "\n\n---\n\n" + MARK + "\n\n" + body
            print("· %s task_brief += cont3 全文 (★原 brief 全文保留★) · status 保持 fixing" % ISS)
        target["dispatched_at"] = NOW
        target["note"] = (target.get("note") or "") + (
            "\n★**2026-11-18 16:40 · cron fb67af40 续做重派 (cont3)★** "
            "★**cont2 (16:26→16:32) 死于 provider 侧 `LLM idle timeout (120s)` ⇒ 一个字节都没落盘★** "
            "⇒ ★**cont3 打法改了: 第一动作 = 落骨架 (交卷页六块 + 交付页骨架 + 一条分片), 之后才允许读源码★** "
            "⇒ ★**再挂也留得下一个闸链认的骨架 ⇒ 下一趟不从零开始★** "
            "★另: main 16:33 实跑 gate rc=1 (红在 SW 侧 SOP 里的反向测试夹具假位号·与 mech 无关·不许去改) + Q5 硬指标覆盖 0/3 (⇒ mech 交卷页必须给 ≥3 类带数字的硬指标, 写成小表)★")

        out = dict(log); out["issues"] = issues
        shutil.copy2(LOG, LOG + ".bak_cronfb67_%s_cont_326_c3" % STAMP)
        atomic_write(LOG, yaml.safe_dump(out, allow_unicode=True, sort_keys=False, width=100000))

        dl = yaml.safe_load(open(DL, encoding="utf-8")) or {}
        disp = dl.get("dispatches") or []
        if not any(isinstance(d, dict) and d.get("issue") == ISS and MARK in str(d.get("brief")) for d in disp):
            disp.append({
                "issue": ISS, "agent": AGENT, "at": NOW,
                "brief": MARK + " ★**cont2 死于 provider idle timeout (未落盘) ⇒ cont3 = 先落骨架再干活** ★"
                          "★**交卷页六块必须齐全 (Q1 14/18 → 目标 18/18) · Q5 必须给 ≥3 类带数字硬指标 · "
                          "gate 当前 rc=1 是红在 SW 侧 (SOP 里的夹具假位号), 不许去动 SW 文档/闸** ★",
                "job": ("cron fb67af40 (ARS45 队列自动派活) · ★派活时刻 2026-11-18 16:40 · "
                        "★**续做重派 (cont2 死于 provider 侧 idle timeout·本轮从零落骨架·status 保持 fixing "
                        "⇒ 无 open 窗口·兄弟 job 775d9893 不会重复派)** ★"),
            })
            print("· dispatch_log 追加 %s cont3" % ISS)
        dl["dispatches"] = disp
        shutil.copy2(DL, DL + ".bak_cronfb67_%s_cont_326_c3" % STAMP)
        atomic_write(DL, yaml.safe_dump(dl, allow_unicode=True, sort_keys=False, width=100000))
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
