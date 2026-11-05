#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
delivery_health.py —— ★投递健康自检 (2026-11-04 新增)

★为什么有这个脚本 (实测踩过):
  `ARS45 状态速报 (每小时推微信)` 从 11-03 09:09 起 **连挂 24 次**, 错误固定
  `OutboundDeliveryError: sendMessage ret=-2 errmsg=prepare failed`
  ⇒ **老板手机上看不到任何状态, 我这边却"一切正常"** ⇒ 23 小时后他一句"分析结果如何"才发现。
  ⇒ ★**主动推送 = 唯一一路状态源 = 单点故障** ⇒ 必须有自检。

★它做什么:
  1. 读 `~/.openclaw/cron/jobs-state.json` + `jobs.json`
  2. 找出 **consecutiveErrors >= 阈值** 且 **delivery 目标是微信** 的 job
  3. 找出 **所有** delivery 目标指向同一个坏通道的 job (通道级故障 ⇒ 不止一个 job 受影响)
  4. ★**告警去重**: 同一场故障只提醒一次, 之后每 RE_ALERT_HOURS 小时才再提醒一次
     (去重状态写在 state/.delivery_health_alerted.json)

判据:
  C1 通道级故障: 有 job 的 consecutiveErrors >= THRESHOLD 且其 delivery.channel == 目标通道
  C2 job 级故障: 有 job 的 consecutiveErrors >= THRESHOLD 且 delivery 通道不是目标通道
  C3 去重: 同一 (通道, job, lastError) 指纹已告警且未超 RE_ALERT_HOURS ⇒ 不再提醒

用法:
  python3 state/delivery_health.py            # 人看 / 脚本看
  python3 state/delivery_health.py --quiet    # 没毛病就啥都不输出 (给 cron/心跳用)
退出码: 0 = 健康; 1 = 有故障(且该提醒)
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
CRON_DIR = os.path.expanduser("~/.openclaw/cron")
JOBS_STATE = os.path.join(CRON_DIR, "jobs-state.json")
JOBS = os.path.join(CRON_DIR, "jobs.json")
ALERT_STATE = os.path.join(HERE, ".delivery_health_alerted.json")

THRESHOLD = 3               # 连挂几次算故障
RE_ALERT_HOURS = 6          # 同一故障多久之后再提醒一次
# ★B 类 (运行收场报错) 的提醒间隔: 24h
#   理由 (2026-11-04 16:2x 决定): B 类是**运行时收场 flake** —— 活照干、产出照交,
#   且该 job 的推送已关 (mode=none) ⇒ **对老板零影响** ⇒ 每 6 小时报一次纯属噪音 ⇒ 放宽到 24h。
#   ★若某个 B 类 job 的推送是开着的 (mode=announce) ⇒ 仍走 6h, 因为那才会真的挡住通知。
RE_ALERT_HOURS_B = 24
WATCH_CHANNEL = "openclaw-weixin"   # ★老板手机上看状态的那一路 (最脆)

# ★★2026-11-04 09:5x 实测加的分类 (两类故障必须分开, 否则噪音掩盖真问题)
#   A 类 = **通道发不出去** ⇒ 老板手机上真的看不到 ⇒ 必须报
#   B 类 = **运行收场报错** (session 锁被抢 / 网关在重启 / 超时) ⇒ ★**不代表活没干**
#          (实测: 11-04 09:30 那轮 advance 报 EmbeddedAttemptSessionTakeoverError,
#           但报告、派活、门禁刷新全都干完了) ⇒ 单独一栏, 措辞不同
A_CLASS = ("outbounddeliveryerror", "sendmessage", "prepare failed", "delivery failed")
B_CLASS = ("embeddedattemptsessiontakeovererror", "gatewaydrainingerror",
           "job execution timed out", "fallbacksummaryerror")


def classify(err):
    e = (err or "").lower()
    if any(k in e for k in A_CLASS):
        return "A"
    if any(k in e for k in B_CLASS):
        return "B"
    return "A"   # 认不出来 ⇒ 按真故障处理 (宁可吵, 不可漏)


def _load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _run_channel(job_id):
    """★从 cron/runs/<jobId>.jsonl 的最后一条 run 记录里取**实际解析到的投递通道**
    (jobs.json 的 delivery 里没有 channel 字段 ⇒ 通道是在运行时解析的)"""
    p = os.path.join(CRON_DIR, "runs", "%s.jsonl" % job_id)
    try:
        with open(p, encoding="utf-8") as f:
            lines = [ln for ln in f if ln.strip()]
        if not lines:
            return None
        rec = json.loads(lines[-1])
        dl = rec.get("delivery") or {}
        return (dl.get("resolved") or {}).get("channel") or (dl.get("intended") or {}).get("channel")
    except Exception:
        return None


def collect():
    """→ [(job_name, channel, consecutiveErrors, lastError, lastRunAtMs)]"""
    st = _load(JOBS_STATE)
    jb = _load(JOBS)
    name_by_id, delivery_by_id = {}, {}
    # jobs.json 可能是顶层 list, 也可能是 {"jobs": [...]} ⇒ 两种都吃
    jl = jb.get("jobs") if isinstance(jb, dict) else jb
    if isinstance(jl, dict):
        jl = list(jl.values())
    for j in (jl or []):
        name_by_id[j.get("id")] = j.get("name") or j.get("id")
        delivery_by_id[j.get("id")] = j.get("delivery") or {}

    out = []
    for jid, v in (st.get("jobs") or {}).items():
        s = v.get("state") or {}
        ce = s.get("consecutiveErrors") or 0
        if not ce:
            continue
        d = delivery_by_id.get(jid) or {}
        out.append({
            "id": jid,
            "name": name_by_id.get(jid, jid),
            "mode": d.get("mode") or "announce",
            "channel": d.get("channel") or _run_channel(jid) or "?",
            "to": d.get("to") or "?",
            "errors": ce,
            "lastError": s.get("lastError") or "(无)",
            "lastRunAtMs": s.get("lastRunAtMs") or 0,
            "lastDeliveryStatus": s.get("lastDeliveryStatus") or "?",
        })
    out.sort(key=lambda x: -x["errors"])
    return out


def _recent_runs(job_id, n=3):
    """★取最后 n 条 run 记录 (★新增: 用于查"run 状态 ok 但 delivered:false")"""
    p = os.path.join(CRON_DIR, "runs", "%s.jsonl" % job_id)
    out = []
    try:
        with open(p, encoding="utf-8") as f:
            lines = [ln for ln in f if ln.strip()]
        for ln in lines[-n:]:
            try:
                out.append(json.loads(ln))
            except Exception:
                pass
    except Exception:
        pass
    return out


def collect_silent_fail(n=3):
    """★★D 类 (2026-11-05 12:00 新增): **run 状态 = ok, 但 delivered:false**
    ⇒ ★**agent 活干完了, 但推送没到老板手上** ⇒ 而 run 状态看起来是"成功" ⇒ 老判据看不见
    ⇒ ★**实测**: `ARS45 状态速报 (每小时推微信)` 的 run 记录连着好几轮都是
       `status: ok` + `delivery.delivered: false` ⇒ 老板手机上根本没收到, 而我一直报"一切正常"
    ⇒ 判据: 目标通道 = 微信 且**最近 n 轮全部 delivered:false 且有 summary**(⇒ agent 确实产出了内容)
    """
    jb = _load(JOBS)
    jl = jb.get("jobs") if isinstance(jb, dict) else jb
    if isinstance(jl, dict):
        jl = list(jl.values())
    out = []
    for j in (jl or []):
        jid = j.get("id")
        d = j.get("delivery") or {}
        ch = d.get("channel") or ""
        runs = _recent_runs(jid, n)
        if not runs:
            continue
        # ★通道来源: ①job 的 delivery.channel ②run 记录里 resolved/intended 的通道
        #   (★老板的"状态速报" job 用的是 mode=none + to/accountId ⇒ jobs.json 里没有 channel 字段)
        for r in runs:
            dl = r.get("delivery") or {}
            ch = ch or (dl.get("resolved") or {}).get("channel") or (dl.get("intended") or {}).get("channel") or ""
        if ch != WATCH_CHANNEL:
            continue
        if len(runs) < 2:
            continue
        flags = [(r.get("delivery") or {}).get("delivered") for r in runs]
        if all(f is False for f in flags) and any(r.get("summary") for r in runs):
            out.append({
                "id": jid,
                "name": j.get("name") or jid,
                "channel": ch,
                "to": d.get("to") or "?",
                "runs": len(runs),
                "lastRunAtMs": runs[-1].get("ts") or 0,
                "lastError": "run status=ok 但 delivered=false (推送没到老板手上)",
            })
    return out


def fingerprint(bad):
    """★指纹**不含**连续失败次数 (每次跑都会 +1 ⇒ 含它就永远去重不掉)
    ★**按故障类别分开算指纹** (A 类通道故障 / B 类收场报错) ⇒ 否则多一个 B 类 job
      就会把 A 类的指纹也改掉 ⇒ 已告警过的通道故障被反复重报 (11-04 09:45 实测踩到)"""
    parts = []
    for b in bad:
        parts.append("%s::%s::%s" % (b["channel"], b["name"], b["lastError"][:120]))
    return "|".join(parts)


def fp_of(bad, cls):
    parts = []
    for b in bad:
        if classify(b["lastError"]) == cls:
            parts.append("%s::%s::%s" % (b["channel"], b["name"], b["lastError"][:120]))
    return "|".join(parts)


def _read_alerted():
    try:
        with open(ALERT_STATE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _write_alerted(obj):
    tmp = ALERT_STATE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, ALERT_STATE)


def main():
    quiet = "--quiet" in sys.argv
    bad = [b for b in collect() if b["errors"] >= THRESHOLD]
    silent = collect_silent_fail()   # ★★D 类: run=ok 但 delivered=false (★2026-11-05 12:00 新增)
    if not bad and not silent:
        if not quiet:
            print("✅ 投递健康: 所有 cron job 无连续失败 (阈值 %d)" % THRESHOLD)
        return 0

    alerted = _read_alerted()
    now = time.time()
    clsA = [b for b in bad if classify(b["lastError"]) == "A"]
    clsB = [b for b in bad if classify(b["lastError"]) == "B"]
    fpA, fpB = fp_of(bad, "A"), fp_of(bad, "B")
    # ★★D 类的指纹 (★单独一个 key ⇒ 不影响 A/B 的去重)
    fpD = "|".join("%s::%s::%s" % (s["channel"], s["name"], s["lastError"][:80]) for s in silent)

    # ★B 类里"推送已关 (mode=none)"的那些 = 对老板零影响 ⇒ 用 24h 窗口
    b_impact = [b for b in clsB if b.get("mode") != "none"]
    b_fp_impact = "|".join("%s::%s::%s" % (b["channel"], b["name"], b["lastError"][:120]) for b in b_impact)
    b_fp_noimpact = "|".join("%s::%s::%s" % (b["channel"], b["name"], b["lastError"][:120])
                             for b in clsB if b.get("mode") == "none")

    def _rep(key, fp, window=RE_ALERT_HOURS):
        """该类别是否已告警过且还在提醒窗口内"""
        st = alerted.get(key) or {}
        return st.get("fingerprint") == fp and (now - (st.get("at", 0) or 0)) < window * 3600

    # ★没有 A 类故障时, A 类算"无待提醒" (否则 repeat 永远 False ⇒ 每半小时都吵一次)
    repeatA = (not clsA) or _rep("A", fpA)
    # B 类分两把尺: 有推送的用 6h; 推送已关的用 24h (零影响, 别吵老板)
    repeatB = (_rep("B", fpB) and _rep("B_imp", b_fp_impact)) if b_impact else _rep("B_noimp", b_fp_noimpact, RE_ALERT_HOURS_B)
    repeatD = (not silent) or _rep("D", fpD)
    repeat = repeatA and repeatB and repeatD

    if repeat and quiet:
        return 0

    lines = []
    chans = sorted({b["channel"] for b in clsA})
    # ★2026-11-04 10:45 修: 老板 09:5x 已把微信推送全关 (delivery.mode=none) ⇒ A 类为空时 chans 未定义 ⇒ UnboundLocalError
    #   ⇒ chans 一律先算; 且**处置建议按"这一路现在还推不推"分两种说法** (不再让老板去扫码刷新一个他已关掉的通道)
    watch_still_pushing = any(b["channel"] == WATCH_CHANNEL and b.get("mode") != "none" for b in clsA)
    if clsA:
        lines.append("⚠️ 投递健康自检: %d 个 cron job 连挂 ≥%d 次 (★通道发不出去类)" % (len(clsA), THRESHOLD))
        lines.append("  受影响通道: %s" % ", ".join(chans))
        for b in clsA:
            t = time.strftime("%m-%d %H:%M", time.localtime(b["lastRunAtMs"] / 1000)) if b["lastRunAtMs"] else "?"
            lines.append("  · [%s] %s 连挂 %d 次 | 末次投递=%s | 最后跑 %s"
                         % (b["channel"], b["name"], b["errors"], b["lastDeliveryStatus"], t))
            lines.append("      错误: %s" % b["lastError"][:160])
    if clsB:
        lines.append("⚠️ 另有 %d 个 cron job 连挂 ≥%d 次 (★运行收场报错类 — **不代表活没干**)" % (len(clsB), THRESHOLD))
        for b in clsB:
            t = time.strftime("%m-%d %H:%M", time.localtime(b["lastRunAtMs"] / 1000)) if b["lastRunAtMs"] else "?"
            lines.append("  · [%s] %s 连挂 %d 次 | 最后跑 %s"
                         % (b["channel"], b["name"], b["errors"], t))
            lines.append("      错误: %s" % b["lastError"][:160])
            if b.get("mode") == "none":
                lines.append("      ★判据: 按铁律 **看产出 (文件 mtime / 报告内容)**, 不看 run 状态 ⇒ 这一类只是 **run 状态显示 error**;"
                             "★**该 job 的推送已关 (mode=none) ⇒ announce 本来就不发 ⇒ 对老板无影响**")
    if silent:
        lines.append("⚠️ ★★D 类: %d 个 job **run 状态 ok 但 delivered:false** (★agent 干了活, 但推送没到老板手上)" % len(silent))
        for s in silent:
            t = time.strftime("%m-%d %H:%M", time.localtime(s["lastRunAtMs"] / 1000)) if s["lastRunAtMs"] else "?"
            lines.append("  · [%s] %s | 最近 %d 轮全部未送达 | 最后跑 %s" % (s["channel"], s["name"], s["runs"], t))
            lines.append("      ★**这条以前被判成\"正常\"** (run 状态是 ok) ⇒ 老板手机上看不到, 我却报\"一切正常\"")
            lines.append("      ★处置: ★**要老板动手** (给 bot 发一条消息刷新会话 / 重扫授权) ⇒ 我不自己乱修通道")
    if WATCH_CHANNEL in chans:
        if watch_still_pushing:
            lines.append("  ★处置: %s 这一路发不出去 ⇒ 老板手机上看不到状态 ⇒ "
                         "①请老板在微信里给机器人发一条消息刷新会话, 或 `openclaw channels login --channel openclaw-weixin` 重新扫码; "
                         "②同时看 GitHub / 本地 STATUS_DIGEST.md 兜底" % WATCH_CHANNEL)
        else:
            lines.append("  ★说明: %s 上的失败任务**推送已被关闭** (delivery.mode=none, 老板 2026-11-04 09:5x 指示) ⇒ "
                         "不影响状态送达 (状态仍落 GitHub / 本地 STATUS_DIGEST.md); 若以后要恢复这一路推送, 才需要处理会话刷新" % WATCH_CHANNEL)
    if repeatA:
        lines.append("  (A 类故障已于 %s 告警过, %dh 内不重复提醒)" % (
            time.strftime("%m-%d %H:%M", time.localtime((alerted.get("A") or {}).get("at", 0))), RE_ALERT_HOURS))
    if repeatB:
        lines.append("  (B 类故障已于 %s 告警过, %dh 内不重复提醒)" % (
            time.strftime("%m-%d %H:%M", time.localtime((alerted.get("B") or {}).get("at", 0))), RE_ALERT_HOURS))
    if repeatD and (alerted.get("D") or {}).get("at"):
        lines.append("  (D 类故障已于 %s 告警过, %dh 内不重复提醒)" % (
            time.strftime("%m-%d %H:%M", time.localtime((alerted.get("D") or {}).get("at", 0))), RE_ALERT_HOURS))
    new_alert = dict(alerted)
    if not repeatA:
        new_alert["A"] = {"fingerprint": fpA, "at": now,
                          "jobs": [{"name": b["name"], "errors": b["errors"]} for b in clsA]}
    if not repeatB:
        new_alert["B"] = {"fingerprint": fpB, "at": now,
                          "jobs": [{"name": b["name"], "errors": b["errors"]} for b in clsB]}
        if b_impact:
            new_alert["B_imp"] = {"fingerprint": b_fp_impact, "at": now,
                                  "jobs": [{"name": b["name"], "errors": b["errors"]} for b in b_impact]}
        else:
            new_alert["B_noimp"] = {"fingerprint": b_fp_noimpact, "at": now,
                                    "jobs": [{"name": b["name"], "errors": b["errors"]} for b in clsB]}
    if not repeatD:
        new_alert["D"] = {"fingerprint": fpD, "at": now,
                          "jobs": [{"name": s["name"], "runs": s["runs"]} for s in silent]}
    new_alert["fingerprint"] = fingerprint(bad)
    new_alert["fingerprint"] = fingerprint(bad)
    new_alert["at"] = now
    new_alert["jobs"] = [{"name": b["name"], "errors": b["errors"]} for b in bad]
    _write_alerted(new_alert)
    text = "\n".join(lines)
    if quiet:
        sys.stdout.write(text + "\n")
    else:
        print(text)
    return 1


if __name__ == "__main__":
    sys.exit(main())
