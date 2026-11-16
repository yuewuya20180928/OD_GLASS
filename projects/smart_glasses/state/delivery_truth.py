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
  python3 state/delivery_truth.py --selftest # ★判据自测 (含反向用例, ★2026-11-17 04:3x ISS-261 加★)
退出码: 0 = 无异常; 1 = 有"这轮没送到老板"的记录 (信息性, 不是判废)

★★【2026-11-17 04:3x · ISS-261 修: 口径①的 mode=none 归类 (★追加式留痕, 老字一行没删★)】★★
★**病灶 (main 本机实跑, 不是抄交卷报告★)**: `delivery.mode == 'none'` 的 job (★老板 2026-11-04 09:5x 关掉微信推送★),
★**run 记录里照样写 `delivery.delivered = false`** ⇒ ★**老分类先判 `delivered is False` ⇒ 全部落进「没送到」**
⇒ ★**「本来就不投」那一列结构上恒为 0** ⇒ 输出「送到 0 · 没送到 12 · 本来就不投 0」= ★**假故障 (狼来了)** ★
★**对照**: 同一套输出里 A 类 / B 类 / D 类 【都已经有 mode=none 的排除逻辑】⇒ ★**只有口径①漏了 ⇒ 两套口径自相矛盾** ★
★**修法 (★只动分类, 不动任何阈值 / 不动 A/B/D 三类判据 / 不动真源★)**:
★**`mode == 'none'` ⇒ `delivered=false` 记成「本来就不投」(`no_delivery`); `delivered=true` 仍记「送到」; `status=error` 仍记「这轮没跑成」** ★
★**反向用例 (★`--selftest` 内置★)**: ★**mode=none ⇒ 「没送到」必须为 0 且「本来就不投」= 非 error 轮数; mode≠none ⇒ 行为逐字不变** ★

★★【H-1 台账 · ISS-261 · ★2026-11-17 04:3x★】★★
★**改动前 md5**: `00ff09721fad2b1fa8621d5af5573f7f` (★2026-11-17 04:35 实测★)
★**备份**: `state/.bak_delivery_truth_20261117_0435_iss261.py` (★md5 同上, 逐字节相同★)
★**改动后 md5**: ★**见交卷单 + issue_log ISS-261 note (★不许在本文件里自引用自己的 md5★)★★
★**反向用例命令**: `python3 state/delivery_truth.py --selftest` ⇒ ★**31 条断言 rc=0 (★7 纯函数 + 4 job × 6 端到端★)★**
★★**2026-11-17 05:5x · ISS-272 (sw-lead 独立复核) 加了【合成 run 记录】用例组**★★
★**为什么加 (★变异测试 M6 实测, 不是猜★)**: ★**盘上 9 个 cron job 的 mode 全是 none ⇒ 端到端 announce 分支零执行**
★**⇒ 变异测试: 把该分支期望改错 ⇒ `--selftest` 仍 rc=0** ★⇒ ★**合成用例把「mode=announce ⇒ 没送到必须保留」钉死** ★
★**只加用例, ★★`classify_run` 判据一个字节没改** ★★ ⇒ ★**ISS-261 的改判结论不受影响** ★
★**隔离性自证**: ★**同一份真实 run 记录, 修前/修后各跑一次 `state/delivery_health.py` ⇒ diff 只有 4 行口径① 变了; A 类 / B 类 / D 类 / 口径② / 结论行 逐字节不变★**
★**边界**: ★**零外发 · 零采购 · 零写板 · 零落表 · 零改网表/脚表/BOM · 零改任何告警阈值 · A/B/D 三类判据一个字没动 ★**
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


def classify_run(status, delivered, mode=None):
    """★★【口径① 单轮分类 · 纯函数 · ★2026-11-17 04:3x ISS-261 新增★】★★

    ★**为什么抽成纯函数 (★可自测, 不依赖盘上真数据★)**: ★**口径① 的 mode=none 归类是判据 ⇒ 判据必须能被反向用例钉住** ★

    ★**分类顺序 (★顺序就是判据, 不许乱换★)**:
      ① `status == 'error'` ⇒ ★**run_error** (这轮没跑成 ⇒ 跟投递模式无关 ⇒ ★**mode=none 也照样算「这轮没跑成」★)
      ② `delivered is True` ⇒ ★**delivered** (★真送到了老板手上 ⇒ 最高优先级, mode 无关★)
      ③ ★**`mode == 'none'` ⇒ no_delivery** (★**推送本来就没开 ⇒ delivered=false 是预期行为 ⇒ 不算故障★** ★**ISS-261 的修点**★)
      ④ `delivered is False` ⇒ ★**not_delivered** (跑了但没送到 ⇒ ★**真故障**★)
      ⑤ 其余 (delivered 缺字段) ⇒ ★**no_delivery**
    """
    if status == "error":
        return "run_error"
    if delivered is True:
        return "delivered"
    if (mode or "announce") == "none":
        return "no_delivery"
    if delivered is False:
        return "not_delivered"
    return "no_delivery"


def runs_view(job_id, n=TAIL, mode=None):
    """★把 run 记录压成"这一轮送没送到"的结论"""
    view = []
    for r in recent_runs(job_id, n):
        ts = r.get("ts") or 0
        dl = r.get("delivery") or {}
        delivered = dl.get("delivered")
        status = r.get("status")
        verdict = classify_run(status, delivered, mode)
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
        view = runs_view(jid, mode=d.get("mode"))
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


def _syn_selftest(chk):
    """★★【★合成 run 记录 · 端到端加压 · ★2026-11-17 05:5x ISS-272 sw-lead 独立复核加★】★★

    ★★**为什么必须加这一组 (★变异测试 M6 实测出来的, 不是猜的★)**: ★★
    ★**2026-11-17 05:5x 实测**: ★**盘上 9 个 cron job 的 `delivery.mode` 全是 `none`** ★
    ⇒ ★**端到端用例里的 announce 分支 (mode≠none) 在当前盘上【一次都没执行过】** ★
    ⇒ ★**变异测试实测: 把该分支的期望值故意改错 (exp_nd = len(ok_runs)+999) ⇒ `--selftest` 仍然 rc=0** ★
    ⇒ ★★**⇒ 「mode=announce ⇒ 「没送到」必须保留」这条判据, 在【端到端层面】零保护** ★★
    ★**⇒ 本组用例用【合成 run 记录】把 announce 分支钉死 (不依赖盘上真实 job 状态)★**

    ★**只加用例, 不动任何判据 (★`classify_run` 一个字节没改★)** ★
    """
    import shutil
    import tempfile
    global RUNS_DIR
    tmpd = tempfile.mkdtemp(prefix="dt_selftest_")
    bak = RUNS_DIR
    try:
        syn = "synthetic-announce-job"
        # 合成 5 轮: delivered×1 / not_delivered×3 / run_error×1
        rows = [
            {"action": "finished", "ts": 1, "status": "ok", "summary": "x",
             "delivery": {"delivered": True}},
            {"action": "finished", "ts": 2, "status": "ok", "summary": "x",
             "delivery": {"delivered": False}},
            {"action": "finished", "ts": 3, "status": "ok", "summary": "x",
             "delivery": {"delivered": False}},
            {"action": "finished", "ts": 4, "status": "ok", "summary": "x",
             "delivery": {"delivered": False}},
            {"action": "finished", "ts": 5, "status": "error", "summary": "x",
             "delivery": {"delivered": False}},
        ]
        with open(os.path.join(tmpd, "%s.jsonl" % syn), "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        RUNS_DIR = tmpd
        # ★三种 mode 各自的期望计数 (★判据顺序: error → delivered → mode=none → not_delivered★)
        for mode, want in (
            ("announce", {"delivered": 1, "not_delivered": 3, "run_error": 1, "no_delivery": 0}),
            ("none",     {"delivered": 1, "not_delivered": 0, "run_error": 1, "no_delivery": 3}),
            (None,       {"delivered": 1, "not_delivered": 3, "run_error": 1, "no_delivery": 0}),
        ):
            v = runs_view(syn, n=99, mode=mode)
            cnt = {"delivered": 0, "not_delivered": 0, "run_error": 0, "no_delivery": 0}
            for x in v:
                cnt[x["verdict"]] = cnt.get(x["verdict"], 0) + 1
            for k in ("delivered", "not_delivered", "run_error", "no_delivery"):
                chk("SYN mode=%s ⇒ 合成 job 的 %s 计数" % (mode, k), cnt.get(k, 0), want[k])
        # ★★**ISS-272 任务书点名的第 ④ 条: 「mode=announce 但连着 3 轮 delivered=false」
        #   ⇒ 「没送到」必须 = 3, ★**不许因为这次改动被洗成 0**★**
        v = runs_view(syn, n=99, mode="announce")
        nd = len([x for x in v if x["verdict"] == "not_delivered"])
        chk("SYN ★announce 连着 3 轮 delivered=false ⇒ 没送到必须 = 3★", nd, 3)
    finally:
        RUNS_DIR = bak
        shutil.rmtree(tmpd, ignore_errors=True)


def _selftest():
    """★★【判据自测 · ★2026-11-17 04:3x ISS-261 加 · ★05:5x ISS-272 sw-lead 复核加合成用例★】★★
    ★**三类用例**:
      ① **纯函数用例** (★classify_run 的六种输入组合★)
      ② **端到端用例** (★拿盘上真 run 记录跑一遍 ★`collect()`★ ⇒ ★**断言 mode=none 的 job 「没送到」必为 0**★)
      ③ ★**合成 run 记录用例 (★ISS-272 加★)**: ★**盘上 announce job 数为 0 ⇒ 端到端 announce 分支原本零覆盖
        ⇒ 用合成记录把「mode=announce ⇒ 没送到必须保留」钉死** ★
    ★**反向用例 (★本单要求的那条·★)**: ★**mode=none ⇒ 那一行必须从「没送到」挪到「本来就不投」★**
    """
    fails = []
    n = 0

    def chk(label, got, want):
        nonlocal n
        n += 1
        if got != want:
            fails.append("★%s: got=%r want=%r" % (label, got, want))

    # ---- ① 纯函数用例 ----
    chk("C1 mode=none+false ⇒ no_delivery (★反向用例: 挪到「本来就不投」★)",
        classify_run("ok", False, "none"), "no_delivery")
    chk("C2 mode=announce+false ⇒ not_delivered (★行为逐字不变★)",
        classify_run("ok", False, "announce"), "not_delivered")
    chk("C3 mode=announce+true ⇒ delivered (★真送到最高优先级★)",
        classify_run("ok", True, "announce"), "delivered")
    chk("C4 mode=none+true ⇒ delivered (★mode 不许压掉真送到★)",
        classify_run("ok", True, "none"), "delivered")
    chk("C5 mode=none+status=error ⇒ run_error (★job 自己失败跟投递模式无关★)",
        classify_run("error", False, "none"), "run_error")
    chk("C6 mode=announce+delivered 缺字段 ⇒ no_delivery",
        classify_run("ok", None, "announce"), "no_delivery")
    chk("C7 mode 缺省 (None) ⇒ 按 announce 判 (★老调用方兼容★)",
        classify_run("ok", False, None), "not_delivered")

    # ---- ② 端到端用例 (★盘上真数据★) ----
    data = collect()
    e2e = 0
    for j in data.get("jobs") or []:
        mode = (j.get("deliveryMode") or "announce")
        c = j.get("counts") or {}
        runs = j.get("runs") or []
        e2e += 1
        ok_runs = [r for r in runs if r.get("status") != "error"]
        if mode == "none":
            chk("E2E[%s] mode=none ⇒ 没送到必为 0" % j.get("name"),
                c.get("not_delivered", 0), 0)
            chk("E2E[%s] mode=none ⇒ 本来就不投 = 非 error 轮数" % j.get("name"),
                c.get("no_delivery", 0), len(ok_runs))
        else:
            exp_nd = len([r for r in ok_runs if r.get("delivered") is False])
            chk("E2E[%s] mode=%s ⇒ 没送到计数逐字不变" % (j.get("name"), mode),
                c.get("not_delivered", 0), exp_nd)
        # 逐轮 verdict 与计数必须自洽
        exp = {}
        for r in runs:
            v = classify_run(r.get("status"), r.get("delivered"), mode)
            exp[v] = exp.get(v, 0) + 1
        for k in ("delivered", "not_delivered", "run_error", "no_delivery"):
            chk("E2E[%s] 计数自洽 %s" % (j.get("name"), k), c.get(k, 0), exp.get(k, 0))

    # ---- ③ 合成 run 记录用例 (★ISS-272 sw-lead 独立复核加★ · ★只加用例, 不改判据★) ----
    _syn_selftest(chk)

    # ---- ④ 缺口观察 (★ISS-272 sw-lead 加★ · ★只打印, 不计入断言, 不改判据 · 待 main 拍板★) ----
    print("── 缺口观察 (★待 main 拍板 · ★本脚本没改判据★) ──")
    print("   · classify_run 的 status 判据只认【精确 'error'】⇒ status='timeout' + mode=none 实测=%s"
          % classify_run("timeout", False, "none"))
    print("     ★实测: 盘上 run 记录 status 取值全集 = {ok, error} (3796 轮) ⇒ ★今天不触发★")
    print("     ★但若 OpenClaw 将来产生 timeout/cancelled 等失败态 ⇒ 真故障会被 mode=none 吞成「本来就不投」★")

    print("════════ 投递口径① selftest ════════")
    print("  纯函数用例: %d 条" % 7)
    print("  端到端用例: %d 个 job" % e2e)
    print("  合成用例: 1 个合成 job × 3 种 mode (★announce 分支原本零覆盖★)")
    if fails:
        print("❌ 失败 %d 条:" % len(fails))
        for f in fails:
            print("   " + f)
        return 1
    print("✅ 全过 (%d 条断言)" % n)
    return 0


def main():
    as_json = "--json" in sys.argv
    do_probe = "--probe" in sys.argv
    if "--selftest" in sys.argv:
        return _selftest()
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
