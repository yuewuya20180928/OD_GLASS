#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bcast_delivery_check.py -- ★★【播报员的"回读确认落地"步骤】★★ (★2026-11-10 11:3x 新增★)

★★★**★为什么要有这个 (★老板 11-10 10:52 播报里提的要求: "播报必须加'发完回读 transcript 确认落地'这一步, 不能再拿 accepted 当送达"★)** ★★★
  ★**实测的关键事实 (★今天 11:0x 挖出来的★)**:
    ① **announce 投递发生在本轮 agent 跑完之后** ⇒ ★**本轮的 agent 自己看不到自己那条消息送没送到** ⇒
       ★**"发完立刻回读"在物理上做不到** ⇒ ★**唯一可行的做法 = 【下一轮开跑时先回读上一轮】** ★★
    ② **送达状态的唯一真源 = `~/.openclaw/cron/runs/<jobId>.jsonl` 里那一轮的 `delivery.delivered`** ★★
       (★`~/.openclaw/delivery-queue/*.json` **只记失败** ⇒ 拿它数成功数必然错 ⇒ 见 state/delivery_truth.py★)
    ③ ★**微信 outbound 现在是【时好时坏】** (★实测今天 12 轮里 7 轮 delivered=true, 失败的都是 `ret=-2 prepare failed`★)
       ⇒ ★**所以【补发】必须有 ⇒ 而不是只报"送没送到"** ★★

★它做什么:
  · 找到【播报 job】最近一轮【有播报正文】的 run ⇒ 打印它的送达结论
  · ★**没送到 ⇒ 打印"★请本轮补发这段" + 那一轮的播报原文** ⇒ 播报员把它并进本轮
  · 送到 ⇒ 只打印一行状态 ⇒ 播报员正常按节奏走

用法:
  python3 state/bcast_delivery_check.py            # 人看
  python3 state/bcast_delivery_check.py --json     # 机器读
退出码: 0 = 上一轮送达 (或没有上一轮); 1 = ★上一轮没送到 (⇒ 需要补发)
"""
import json
import os
import sys
import time

HOME = os.path.expanduser("~")
CRON_DIR = os.path.join(HOME, ".openclaw", "cron")
RUNS_DIR = os.path.join(CRON_DIR, "runs")
JOBS = os.path.join(CRON_DIR, "jobs.json")
JOB_NAME = "ARS45 10 分钟进展播报 + 落盘自检放行 (自研主板)"


def _load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def job_id():
    jb = _load(JOBS)
    jl = jb.get("jobs") if isinstance(jb, dict) else jb
    if isinstance(jl, dict):
        jl = list(jl.values())
    for j in (jl or []):
        if (j.get("name") or "") == JOB_NAME:
            return j.get("id")
    return None


def last_broadcast_run(n_scan=12):
    """★最近一轮【有播报正文】的 run (★往前扫 n_scan 轮, 跳过没有 summary 的空轮★)"""
    jid = job_id()
    if not jid:
        return None
    p = os.path.join(RUNS_DIR, "%s.jsonl" % jid)
    rows = []
    try:
        with open(p, encoding="utf-8") as f:
            for ln in f:
                ln = ln.strip()
                if not ln:
                    continue
                try:
                    r = json.loads(ln)
                except Exception:
                    continue
                if r.get("action") == "finished":
                    rows.append(r)
    except Exception:
        return None
    rows = rows[-n_scan:]
    for r in reversed(rows):
        s = (r.get("summary") or "").strip()
        if not s or s.upper().startswith("NO_REPLY"):
            continue
        dl = r.get("delivery") or {}
        # ★★"本轮判定无变化 ⇒ 故意不发消息" (正文带 NO_REPLY) ⇒ ★**不是投递故障** ⇒ 不要求补发
        #   (★实测: 11-10 10:32 那轮 delivery.delivered=false, 但那一轮本来就【不发消息】⇒ 补发是错动作★)
        if "NO_REPLY" in s.upper():
            return {
                "ts": r.get("ts") or 0,
                "time": time.strftime("%m-%d %H:%M", time.localtime((r.get("ts") or 0) / 1000)),
                "status": r.get("status"),
                "delivered": None,
                "deliveryStatus": "intentional_no_message",
                "text": "",
                "no_message": True,
            }
        return {
            "ts": r.get("ts") or 0,
            "time": time.strftime("%m-%d %H:%M", time.localtime((r.get("ts") or 0) / 1000)),
            "status": r.get("status"),
            "delivered": dl.get("delivered"),
            "deliveryStatus": r.get("deliveryStatus"),
            "text": s,
        }
    return None


def main():
    as_json = "--json" in sys.argv
    r = last_broadcast_run()
    if r is None:
        msg = "★没有上一轮播报记录 (⇒ 本轮正常发即可)"
        if as_json:
            print(json.dumps({"ok": True, "reason": "no_previous_broadcast"}, ensure_ascii=False))
        else:
            print(msg)
        return 0

    delivered = r["delivered"] is True
    no_message = bool(r.get("no_message"))
    out = {
        "ok": delivered or no_message,
        "time": r["time"],
        "status": r["status"],
        "delivered": r["delivered"],
        "deliveryStatus": r["deliveryStatus"],
        "text": r["text"],
        "no_message": no_message,
        "need_resend": (not delivered) and (not no_message),
    }
    if as_json:
        print(json.dumps(out, ensure_ascii=False, indent=1))
    else:
        if no_message:
            print("★上一轮 (%s) 播报: ➖ 本轮判定【无变化 ⇒ 故意不发消息】(★不是投递故障★) ⇒ 本轮正常发" % r["time"])
        elif delivered:
            print("★上一轮 (%s) 播报: ✅ 已送达老板 ⇒ 本轮正常发" % r["time"])
        else:
            print("★上一轮 (%s) 播报: ❌ **没送到老板** (delivery.delivered=%s, status=%s)"
                  % (r["time"], r["delivered"], r["status"]))
            print("⇒ ★**本轮必须补发下面这段** (★补发 = 把下面正文并进本轮播报, 再走 4a + 4b 两路★):")
            print("---8<--- 上一轮原文 (补发用) ---8<---")
            print(r["text"])
            print("---8<--- 补发结束 ---8<---")
    return 0 if (delivered or no_message) else 1


if __name__ == "__main__":
    sys.exit(main())
