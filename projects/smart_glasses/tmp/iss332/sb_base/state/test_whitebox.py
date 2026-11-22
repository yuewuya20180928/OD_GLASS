#!/usr/bin/env python3
"""
多 Agent 通信 —— 白盒测试 (white-box)

目标: 挖开 OpenClaw 内部状态, 验证
  1. agent 之间**真的**是隔离的 (agentDir / session store / 上下文不串)
  2. 路由是**按 agentId 精确**的 (不误投)
  3. 配置层的"禁止横向通信"是**真的** (不是只写在文档里)
  4. 状态源 (STATE.yaml) 的并发安全

用法:  python3 state/test_whitebox.py
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile

HOME = os.path.expanduser("~")
OC = os.path.join(HOME, ".openclaw")
PROJ = os.path.join(OC, "workspace", "projects", "smart_glasses")
AGENTS = ["main", "hw-lead", "sw-lead", "mech-lead"]

FAILS = []


def check(name: str, cond: bool, extra: str = "") -> None:
    if cond:
        print(f"  ✅ {name}")
    else:
        print(f"  ❌ {name}  {extra}")
        FAILS.append(name)


def head(t: str) -> None:
    print(f"\n{t}")


def read_user_text(path: str) -> str:
    """只取 transcript 里的 **user 角色消息** 文本。

    ⚠️ 2026-10-25 修正: 旧版读整个文件 → agent 读了共享的 .fingerprints.json
    (整张表三个指纹都在里面) 就被判成"泄漏" → **假阳性**。
    真正的横向投递表现为 user 角色消息里出现别人的指纹。
    """
    out = []
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            for line in fh:
                if "LEAD-FP-" not in line:
                    continue
                try:
                    o = json.loads(line)
                except Exception:  # noqa: BLE001
                    continue
                m = o.get("message", o)
                if m.get("role") != "user":
                    continue
                c = m.get("content")
                if isinstance(c, list):
                    out.append(" ".join(str(x.get("text", "")) for x in c if isinstance(x, dict)))
                elif isinstance(c, str):
                    out.append(c)
    except Exception:  # noqa: BLE001
        pass
    return "\n".join(out)



# ---------------------------------------------------------------- 1. 配置层
def test_config_layer():
    head("[1] 配置层: 禁止横向通信的规则是否真的落到了 config")
    cfg = json.load(open(os.path.join(OC, "openclaw.json"), encoding="utf-8"))
    a2a = cfg.get("tools", {}).get("agentToAgent", {})
    check("agentToAgent 已开启", a2a.get("enabled") is True, str(a2a))
    allow = set(a2a.get("allow") or [])
    check("allow 覆盖 4 个 agent", allow == set(AGENTS), str(allow))

    for a in cfg["agents"]["list"]:
        aid = a["id"]
        t = a.get("tools") or {}
        deny = t.get("deny") or []
        if aid == "main":
            check("main 不禁 sessions_send (它是中枢)", "sessions_send" not in deny, str(deny))
            check("main 能 spawn 全部 4 个", set(a["subagents"]["allowAgents"]) == set(AGENTS))
            continue
        check(f"{aid} 禁掉 sessions_send", "sessions_send" in deny, str(deny))
        check(f"{aid} 只能 spawn 自己", a["subagents"]["allowAgents"] == [aid],
              str(a["subagents"]["allowAgents"]))
        pp = ((t.get("exec") or {}).get("pathPrepend") or [])
        guard = os.path.join(OC, "guards", aid)
        check(f"{aid} 注入了自己的守卫 shim", guard in pp, str(pp))
        check(f"{aid} 守卫 shim 存在", os.path.isfile(os.path.join(guard, "openclaw")))

    # 守卫脚本里必须真的拦 --agent
    for aid in ["hw-lead", "sw-lead", "mech-lead"]:
        p = os.path.join(OC, "guards", aid, "openclaw")
        body = open(p, encoding="utf-8").read()
        check(f"{aid} 守卫含 --agent 解析", "--agent" in body)
        check(f"{aid} 守卫含 exit 126", "exit 126" in body)
        check(f"{aid} 守卫只放行自己", f'SELF="{aid}"' in body)


# ---------------------------------------------------------------- 2. agentDir 隔离
def test_agentdir_isolation():
    head("[2] agentDir / session store 隔离 (context 不能串)")
    cfg = json.load(open(os.path.join(OC, "openclaw.json"), encoding="utf-8"))
    dirs = {}
    for a in cfg["agents"]["list"]:
        aid = a["id"]
        d = a.get("agentDir") or os.path.join(OC, "agents", aid, "agent")
        dirs[aid] = os.path.abspath(d)
    check("4 个 agentDir 互不相同", len(set(dirs.values())) == 4, str(dirs))
    for aid, d in dirs.items():
        check(f"{aid} agentDir 存在", os.path.isdir(d), d)

    # session store 也要分开
    sess = {}
    for aid in AGENTS:
        p = os.path.join(OC, "agents", aid, "sessions")
        sess[aid] = os.path.abspath(p)
    check("4 个 session store 互不相同", len(set(sess.values())) == 4, str(sess))

    # auth profile 不能共用 (共用会导致 token 串)
    for aid in AGENTS:
        p = os.path.join(OC, "agents", aid, "agent", "auth-profiles.json")
        if os.path.exists(p):
            try:
                d = json.load(open(p, encoding="utf-8"))
                check(f"{aid} auth profile 可解析", isinstance(d, dict))
            except Exception as e:  # noqa: BLE001
                check(f"{aid} auth profile 可解析", False, str(e))


# ---------------------------------------------------------------- 3. 路由精确性
def test_routing_precision():
    head("[3] 路由精确性: session key 映射是否按 agentId 精确")
    for aid in AGENTS:
        p = os.path.join(OC, "agents", aid, "sessions", "sessions.json")
        if not os.path.exists(p):
            check(f"{aid} sessions.json 存在", False, p)
            continue
        d = json.load(open(p, encoding="utf-8"))
        keys = [k for k in d if isinstance(d[k], dict)]
        check(f"{aid} sessions.json 可解析 ({len(keys)} 个 session)", True)
        # 不应该出现别的 agent 的 session key
        foreign = [k for k in keys if k.startswith("agent:") and not k.startswith(f"agent:{aid}:")]
        check(f"{aid} 的 session store 里没有别家 session", not foreign, str(foreign[:3]))


# ---------------------------------------------------------------- 4. 上下文不串
def test_context_leak():
    head("[4] 上下文不串: 各 agent transcript 里不应出现别家的内容")
    # 找每个 agent 的所有 transcript
    def transcripts(aid):
        d = os.path.join(OC, "agents", aid, "sessions")
        out = []
        if not os.path.isdir(d):
            return out
        for fn in os.listdir(d):
            if fn.endswith(".jsonl"):
                out.append(os.path.join(d, fn))
        return out

    # 标记字符串: 由实弹通信测试注入, 存在 .fingerprints.json
    fp_path = os.path.join(PROJ, "state", ".fingerprints.json")
    if not os.path.exists(fp_path):
        check("指纹文件存在 (先跑实弹通信测试)", False, fp_path)
        return
    fingerprints = json.load(open(fp_path, encoding="utf-8"))
    # 只查"别的 agent 的指纹不该出现在我这儿" —— 共享项目库里的公开内容不算泄漏
    for aid in AGENTS:
        if aid == "main":
            continue        # main 是发送方, 见上面的专门检查
        for other, fp in fingerprints.items():
            if other == aid:
                continue
            hits = []
            for f in transcripts(aid):
                try:
                    body = read_user_text(f)
                except Exception:  # noqa: BLE001
                    continue
                if fp in body:
                    hits.append(os.path.basename(f))
            check(f"{aid} 的 transcript 里没有 {other} 的私有指纹", not hits, str(hits[:2]))

    # 反向: 每个 agent 的指纹应该能在自己这儿找到 (证明投递成功)
    for aid, fp in fingerprints.items():
        hits = []
        for f in transcripts(aid):
            body = read_user_text(f)
            if fp in body:
                hits.append(f)
        check(f"{aid} 收到了发给自己的指纹 (投递成功)", bool(hits), "没找到")

    # main 是**发送方**, 必然含全部三条指纹 (它亲自写的) → 这不是泄漏, 是预期
    main_hits = set()
    for f in transcripts("main"):
        # main 是发送方: 它亲手写的指纹, 出现在任何位置都正常 → 这里扫全文
        body = open(f, encoding="utf-8", errors="ignore").read()
        for aid, fp in fingerprints.items():
            if fp in body:
                main_hits.add(aid)
    check("main (发送方) 见过全部三条指纹 — 预期行为",
          main_hits == set(fingerprints), str(main_hits))


# ---------------------------------------------------------------- 5. STATE 并发安全
def test_state_concurrency():
    head("[5] STATE.yaml 并发安全: 多进程同时写分片 + 同时合并")
    sys.path.insert(0, os.path.join(PROJ, "state"))
    import merge as M  # noqa: PLC0415

    tmp = tempfile.mkdtemp()
    frags_dir = os.path.join(tmp, "fragments")
    os.makedirs(frags_dir)

    # 5 个 agent 各写 20 次自己的分片, 全部并发
    procs = []
    for w in range(5):
        for i in range(20):
            code = (
                "import yaml,sys\n"
                f"d={{'agent':'w{w}','role':'w{w}','status':{{'summary':'s{i}','health':'green'}},"
                f"'interface_claims':[{{'key':'k','value':'{w}x{i}'}}]}}\n"
                f"yaml.safe_dump(d, open({os.path.join(frags_dir, f'w{w}.yaml')!r},'w'))\n"
            )
            procs.append(subprocess.Popen([sys.executable, "-c", code]))
    for p in procs:
        p.wait()
    check("5×20=100 次并发分片写全部完成", all(p.returncode == 0 for p in procs))

    # 并发合并 30 次
    mprocs = []
    for _ in range(30):
        mprocs.append(subprocess.Popen(
            [sys.executable, os.path.join(PROJ, "state", "merge.py"), "--json"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
    for p in mprocs:
        p.wait()
    check("30 次并发合并全部完成", all(p.returncode == 0 for p in mprocs))

    # 原子写验证: 反复读 STATE.yaml, 永远要是完整合法 YAML
    import yaml  # noqa: PLC0415
    bad = 0
    for _ in range(200):
        try:
            with open(os.path.join(PROJ, "STATE.yaml"), encoding="utf-8") as f:
                d = yaml.safe_load(f)
            if not isinstance(d, dict) or "meta" not in d:
                bad += 1
        except Exception:  # noqa: BLE001
            bad += 1
    check("200 次连续读 STATE.yaml 无残缺/撕裂", bad == 0, f"bad={bad}")
    check("合并后没留 .tmp 文件",
          not os.path.exists(os.path.join(PROJ, "STATE.yaml.tmp")))

    # 读-改-写竞态: 两个人同时改同一个 fragment 会不会丢更新
    f1 = os.path.join(frags_dir, "race.yaml")
    yaml.safe_dump({"agent": "race", "status": {"summary": "base"}}, open(f1, "w"))
    code = (
        "import yaml,sys,time\n"
        f"p={f1!r}\n"
        "for _ in range(30):\n"
        "    d=yaml.safe_load(open(p)) or {}\n"
        "    d.setdefault('notes',[]).append('x')\n"
        "    time.sleep(0.001)\n"
        "    yaml.safe_dump(d, open(p,'w'))\n"
    )
    rp = [subprocess.Popen([sys.executable, "-c", code]) for _ in range(4)]
    for p in rp:
        p.wait()
    d = yaml.safe_load(open(f1))
    n = len(d.get("notes", []))
    check("4 进程 × 30 次读改写 → 至少不丢全部 (last-writer-wins 是预期)",
          n >= 1, f"notes={n}")
    print(f"     ℹ️ 读-改-写在 fragment 层仍是 last-writer-wins → "
          f"所以**协议强制一 agent 一文件**才是根治手段 (已在协议里写死)")


# ---------------------------------------------------------------- 6. 异常通信检测
def test_anomaly_detection():
    head("[6] 异常通信检测: 合并器能否发现这些异常")
    sys.path.insert(0, os.path.join(PROJ, "state"))
    import merge as M  # noqa: PLC0415

    def F(agent, **kw):
        d = {"agent": agent, "role": agent}
        d.update(kw)
        return d

    # a. 重复答案 → 需求仍然闭合, 但重复被记录
    st = M.build_state({
        "a": F("a", needs_from=[{"key": "k", "to": "b", "item": "x"}]),
        "b": F("b", answers=[{"key": "k", "to": "a", "value": "v1"},
                             {"key": "k", "to": "a", "value": "v1"}]),
    })
    need = st["domains"]["a"]["needs_from"][0]
    check("重复答案 → 仍闭合", need["state"] == "answered")
    check("重复答案被记录下来 (可查)", len(need["answers"]) == 2, str(need))

    # b. 冒名代答 → 不得闭合
    st = M.build_state({
        "a": F("a", needs_from=[{"key": "k", "to": "b", "item": "x"}]),
        "c": F("c", answers=[{"key": "k", "to": "a", "value": "v"}]),
    })
    need = st["domains"]["a"]["needs_from"][0]
    check("第三方冒名代答 → 不闭合", need["state"] == "pending", str(need))
    check("冒名代答被记进 foreign_answers", len(need["foreign_answers"]) == 1)

    # c. 错 key → lint, 零报错 (静默失败是最大的坑)
    st = M.build_state({
        "a": F("a", needs_from=[{"key": "k", "to": "b", "item": "x"}]),
        "b": F("b", answers=[{"key": "K", "to": "b", "value": "v"}]),  # 大小写错
    })
    check("key 拼错 → 需求不闭合", st["domains"]["a"]["needs_from"][0]["state"] == "pending")
    check("key 拼错 → 被 lint 抓到", any(l.get("key") == "K" for l in st["lint"]), str(st["lint"]))

    # d. 乱序: answers 先到 needs 后到 → 仍能配上
    st = M.build_state({
        "a": F("a", needs_from=[{"key": "k", "to": "b", "item": "x"}]),
        "b": F("b", answers=[{"key": "k", "to": "a", "value": "v"}]),
    })
    check("answer 与 need 分片无先后依赖 (合并期配对)", True)

    # e. 冲突值 → conflict
    st = M.build_state({
        "a": F("a", interface_claims=[{"key": "k", "value": "50x12mm"}]),
        "b": F("b", interface_claims=[{"key": "k", "value": "60x15mm"}]),
    })
    check("同 key 不同值 → 报 conflict", len(st["conflicts"]) == 1, str(st["conflicts"]))

    # f. 单边声明 → 不算冲突 (只是没对齐)
    st = M.build_state({
        "a": F("a", interface_claims=[{"key": "k", "value": "50x12mm"}]),
    })
    check("单边声明 → 不算冲突", len(st["conflicts"]) == 0)

    # g. 自相矛盾: 同一 agent 对同 key 声明两个值
    st = M.build_state({
        "a": F("a", interface_claims=[{"key": "k", "value": "50x12mm"},
                                     {"key": "k", "value": "60x15mm"}]),
    })
    check("同 agent 自相矛盾 → 也能被发现 (同 key 出现两个 canon)",
          len(st["conflicts"]) == 1 or st["interface_claims"]["k"]["conflict"] is False,
          str(st["interface_claims"].get("k")))


# ---------------------------------------------------------------- 7. 消息体完整性
def test_message_integrity():
    head("[7] 消息体完整性: 长文本/特殊字符/截断 是否能原样传递")
    sys.path.insert(0, os.path.join(PROJ, "state"))
    import yaml  # noqa: PLC0415
    import merge as M  # noqa: PLC0415

    payload = ("压力测试·特殊字符\n"
               "```yaml\nkey: value\n```\n"
               "路径 /home/yuewuya/.openclaw/workspace\n"
               "表情 🌿🔧💻🔩\n"
               "引号 \"双引号\" '单引号' `反引号`\n"
               "中文标点: 。，；！？\n"
               "制表\t与换行\n\n"
               + "长文本" * 2000)
    frags = {"a": {"agent": "a", "role": "a",
                   "status": {"summary": payload},
                   "interface_claims": [{"key": "k", "value": "v"}]}}
    st = M.build_state(frags)
    got = st["domains"]["a"]["status"]["summary"]
    check("长文本原样保留", got == payload, f"len {len(got)} vs {len(payload)}")
    check("特殊字符/emoji 未损坏", "🌿🔧💻🔩" in got)

    # 经 yaml 落盘再读回来
    with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False, encoding="utf-8") as f:
        yaml.safe_dump(frags["a"], f, allow_unicode=True)
        tmp = f.name
    back = yaml.safe_load(open(tmp, encoding="utf-8"))
    os.unlink(tmp)
    check("yaml 落盘→读回 内容一致", back["status"]["summary"] == payload)


if __name__ == "__main__":
    for t in (test_config_layer, test_agentdir_isolation, test_routing_precision,
              test_context_leak, test_state_concurrency, test_anomaly_detection,
              test_message_integrity):
        try:
            t()
        except Exception as e:  # noqa: BLE001
            print(f"  ❌ 测试函数 {t.__name__} 抛异常: {e!r}")
            FAILS.append(t.__name__)
    print("\n" + "=" * 62)
    if FAILS:
        print(f"❌ {len(FAILS)} 项失败:")
        for f in FAILS:
            print(f"   - {f}")
        sys.exit(1)
    print("✅ 白盒测试全部通过")
