#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
delivery_truth.py -- ★★【投递真相 · 唯一真源】★★ (★2026-11-10 11:2x 新增★)

★★★**★为什么要有这个 (★今天实测踩到的口径坑★)** ★★★
  ★**2026-11-10 10:52 那条播报说: "微信 outbound 今天 0 成功 / 18 失败" ⇒ "你大概率从 09:03 起就没收到过播报"**
  ⇒ ★★**这个口径是错的** ★★ (★实测: 播报 job 的 run 记录里 08:52 / 09:18 / 09:25 / 09:48 / 09:56 / 10:11 / 10:28
    **七轮全是 delivery.delivered = true** ⇒ ★**那七条老板手机上是收到了的**★)
  ⇒ ★★**错的根源**: ★**"失败队列" (`~/.openclaw/delivery-queue/*.json`) 只存失败的条目 ⇒ 只数它 ⇒ 必然"0 成功"** ★★
  ⇒ ★★★**⇒ 所以本脚本把【两个口径并排打出来】, 任何一方都不许单独引用** ★★★

【三个口径 (★并列, 不许混用★)】:
  ① **cron announce 口径 (★真源 = `cron/runs/<jobId>.jsonl` 的 `delivery.delivered`★)**
     ⇒ 每轮 run 有明确结论: delivered=true (★送到老板手上★) / delivered=false (★没送到★) /
        status=error (★这一轮压根没跑成, 无播报★) / mode=none (★推送本来就没开, 不算故障★)
  ② **微信 outbound 失败队列口径 (★`delivery-queue/*.json` ⇒ 【只记失败】★)**
     ⇒ 只能当"失败侧"读数用 ⇒ ★**绝不可单独拿它说"0 成功"**★
  ③ **实时探测 (★`--probe` ⇒ 真打一次 sendMessage★)**
     ⇒ 通道此刻通不通 ⇒ ★**会真发一条测试消息到老板微信** ⇒ 默认关★

用法:
  python3 state/delivery_truth.py            # 人看
  python3 state/delivery_truth.py --json     # 机器读
  python3 state/delivery_truth.py --probe    # ★会真发一条测试消息★
退出码: 0 = 无异常; 1 = 有"这轮没送到老板"的记录 (信息性, 不是判废)
"""
import glob
import json
import os
import subprocess
import sys
import time

HOME = os.path.expanduser("~")
CRON_DIR = os.path.join(HOME, ".openclaw", "cron")
RUNS_DIR = os.path.join(CRON_DIR, "runs")
JOBS = os.path.join(CRON_DIR, "jobs.json")
QUEUE_DIR = os.path.join(HOME, ".openclaw", "delivery-queue")

DEFAULT_JOBS = [
    "ARS45 10 分钟进展播报 + 落盘自检放行 (自研主板)",
    "ARS45 状态速报 (每小时推微信, 老板手机上看状态)",
    "ARS45 项目每日巡检",
    "ARS45 继续执行后继计划",
]
TAIL = 12          # 每个 job 看最近几轮
TODAY = time.strftime("%Y-%m-%d")


def _load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def jobs_list():
    jb = _load(JOBS)
    jl = jb.get("jobs") if isinstance(jb, dict) else jb
    if isinstance(jl, dict):
        jl = list(jl.values())
    return jl or []


def job_id_by_name(name):
    for j in jobs_list():
        if (j.get("name") or "") == name:
            return j.get("id")
    return None


def recent_runs(job_id, n=TAIL):
    p = os.path.join(RUNS_DIR, "%s.jsonl" % job_id)
    out = []
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
                    out.append(r)
    except Exception:
        pass
    return out[-n:]


def runs_view(job_id, n=TAIL):
    """★把 run 记录压成"这一轮送没送到"的结论"""
    view = []
    for r in recent_runs(job_id, n):
        ts = r.get("ts") or 0
        dl = r.get("delivery") or {}
        delivered = dl.get("delivered")
        status = r.get("status")
        if status == "error":
            verdict = "run_error"          # ★这轮没跑成 ⇒ 没有任何播报★
        elif delivered is True:
            verdict = "delivered"         # ★真送到了老板手上★
        elif delivered is False:
            verdict = "not_delivered"      # ★跑了但没送到★
        else:
            verdict = "no_delivery"        # ★mode=none / not-requested ⇒ 本来就不投★
        view.append({
            "ts": ts,
            "time": time.strftime("%m-%d %H:%M", time.localtime(ts / 1000)) if ts else "?",
            "status": status,
            "deliveryStatus": r.get("deliveryStatus"),
            "delivered": delivered,
            "verdict": verdict,
            "error": (r.get("error") or "")[:140],
            "has_summary": bool(r.get("summary")),
        })
    return view


def queue_failures(since_ms=None):
    """★口径②: 失败队列 (★只记失败★)"""
    out = []
    for f in glob.glob(os.path.join(QUEUE_DIR, "*.json")):
        try:
            d = _load(f)
        except Exception:
            continue
        if not isinstance(d, dict):
            continue
        out.append({
            "id": d.get("id"),
            "ts": d.get("enqueuedAt") or 0,
            "channel": d.get("channel"),
            "accountId": d.get("accountId"),
            "recoveryState": d.get("recoveryState"),
            "lastError": (d.get("lastError") or "")[:120],
            "file": os.path.basename(f),
        })
    out.sort(key=lambda x: x["ts"])
    if since_ms:
        out = [o for o in out if o["ts"] >= since_ms]
    return out


def probe_weixin():
    """★口径③: 实时探测 (★会真发一条测试消息到老板微信★)"""
    plug = os.path.join(HOME, ".openclaw", "npm", "node_modules",
                        "@tencent-weixin", "openclaw-weixin", "dist", "src", "messaging", "send.js")
    acct = os.path.join(HOME, ".openclaw", "openclaw-weixin", "accounts", "6332e0dbe2b1-im-bot.json")
    if not (os.path.exists(plug) and os.path.exists(acct)):
        return {"ok": False, "error": "插件或账号文件不在 (找不到 %s)" % plug}
    code = (
        "import json,os;"
        "SEND=%r;ACC=%r;" % (plug, acct) +
        "acc=json.load(open(ACC,encoding='utf-8'));"
        "m=await import(SEND);"
        "r=await m.sendMessageWeixin({to:acc['userId'],text:'【自检】投递通道探测',"
        "opts:{baseUrl:acc['baseUrl'],token:acc['token']}});"
        "print('OK '+json.dumps(r,ensure_ascii=False))"
    )
    try:
        p = subprocess.run(["node", "--input-type=module", "-e", code],
                           capture_output=True, text=True, timeout=40)
        out = (p.stdout or "").strip()
        if p.returncode == 0 and out.startswith("OK"):
            return {"ok": True, "detail": out[3:]}
        return {"ok": False, "error": ((p.stderr or out) or "?").strip().splitlines()[-1][:200]}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}


def collect(do_probe=False):
    jobs = jobs_list()
    out = {"today": TODAY, "jobs": [], "queue": [], "probe": None}

    names = [j.get("name") for j in jobs if j.get("name") in DEFAULT_JOBS]
    for name in DEFAULT_JOBS:
        if name not in names:
            continue
        jid = job_id_by_name(name)
        if not jid:
            continue
        j = next(x for x in jobs if x.get("id") == jid)
        d = j.get("delivery") or {}
        view = runs_view(jid)
        cnt = {"delivered": 0, "not_delivered": 0, "run_error": 0, "no_delivery": 0}
        for v in view:
            cnt[v["verdict"]] = cnt.get(v["verdict"], 0) + 1
        out["jobs"].append({
            "id": jid,
            "name": name,
            "deliveryMode": d.get("mode"),
            "to": d.get("to"),
            "counts": cnt,
            "runs": view,
        })

    day_start = time.mktime(time.strptime(TODAY, "%Y-%m-%d")) * 1000
    q = queue_failures(day_start)
    out["queue"] = q
    out["queue_count_today"] = len(q)

    if do_probe:
        out["probe"] = probe_weixin()
    return out


def render(data):
    L = []
    L.append("══════ 投递真相 (★两个口径并排, 不许只引一边★) ══════")
    L.append("【口径①】cron announce (★真源 = run 记录里的 delivery.delivered★)")
    for j in data["jobs"]:
        c = j["counts"]
        L.append("  · %s" % j["name"])
        L.append("      最近 %d 轮: ★送到 %d · 没送到 %d · ★这轮没跑成 %d · 本来就不投 %d (delivery.mode=%s)"
                 % (len(j["runs"]), c["delivered"], c["not_delivered"], c["run_error"], c["no_delivery"],
                    j["deliveryMode"]))
        for v in j["runs"][-6:]:
            L.append("        %s  %-14s status=%-7s %s"
                     % (v["time"], v["verdict"], v["status"], (v["error"] or "")[:90]))
    L.append("【口径②】微信 outbound 失败队列 (★★只记失败 ⇒ 【单独看它必然得出「0 成功」的错觉】★★)")
    L.append("  今日失败条目 = %d" % data.get("queue_count_today", 0))
    errs = {}
    for q in data["queue"]:
        errs[q["lastError"]] = errs.get(q["lastError"], 0) + 1
    for e, n in sorted(errs.items(), key=lambda kv: -kv[1])[:5]:
        L.append("    ×%d  %s" % (n, e))
    if data.get("probe"):
        p = data["probe"]
        L.append("【口径③】微信通道实时探测: %s" % ("✅ 通 (%s)" % p.get("detail") if p.get("ok") else "❌ 不通 (%s)" % p.get("error")))
    L.append("══════ 结论: ★★「老板手机上看没看到」必须用【口径①】的 delivered 计数 ★★ =====")
    return "\n".join(L)


def main():
    as_json = "--json" in sys.argv
    do_probe = "--probe" in sys.argv
    data = collect(do_probe=do_probe)
    if as_json:
        print(json.dumps(data, ensure_ascii=False, indent=1))
    else:
        print(render(data))
    # 退出码只反映"最近一轮有没有没送到"; 纯信息性
    worst = 0
    for j in data["jobs"]:
        if j["runs"]:
            worst = max(worst, 1 if j["runs"][-1]["verdict"] in ("not_delivered", "run_error") else 0)
    return worst


if __name__ == "__main__":
    sys.exit(main())
