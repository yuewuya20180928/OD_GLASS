#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent 配置审计 (Config Audit) —— 判定"当前 agent 配置是否满足项目开工条件"
================================================================================
老板 10-25 19:07: "确认当前各个 agent 的配置是否已经满足项目继续执行开工的条件"

注意: 这个问题和 19:02 问的**不是同一件事** ——
  · readiness.py 答的是"组织与流程是否就绪" (人/机制)
  · 本脚本答的是"**配置**是否就绪" (openclaw.json / workspace / skill / 守卫 / 运行时能力)
  · 两者都绿才叫"能开工"

判据分 7 组 (全部机械可判, 不靠印象):
  A 配置本身: openclaw.json 合法 + 关键键在
  B Agent 定义: 4 个 agent 的 name/workspace/agentDir/model
  C Workspace 基础设施: 目录 + projects 软链 + 7 个启动文件 + skills 目录
  D Skill 加载: 真的 list 得出来 + ready 数 + U+FFFD / BOM / CRLF 扫描 (ClawHub 发布事故)
  E 通信拓扑: agentToAgent.allow / sessions.visibility / subagents.allowAgents / deny / pathPrepend
  F 三层守卫: PATH shim 可执行 + CLI 入口包装器 + 审计日志
  G 运行时能力: cron 巡检 + 原子写工具 + 共享库 + 各门脚本可跑

用法:  python3 state/agent_config_check.py [--json]
退出码: 0=满足开工条件  1=有配置项不满足  2=审计器自身出错
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

HOME = os.path.expanduser("~")
OC = os.path.join(HOME, ".openclaw")
CFG = os.path.join(OC, "openclaw.json")
AGENT_DIR = {"main": "main",
             "hw-lead": "hw-lead", "sw-lead": "sw-lead", "mech-lead": "mech-lead"}
WS = {"main": os.path.join(OC, "workspace"),
      "hw-lead": os.path.join(OC, "workspace-hw"),
      "sw-lead": os.path.join(OC, "workspace-sw"),
      "mech-lead": os.path.join(OC, "workspace-mech")}
NAME = {"main": "项目总工", "hw-lead": "硬件总工", "sw-lead": "软件总工", "mech-lead": "结构总工(带散热)"}
BOOT_FILES = ["AGENTS.md", "SOUL.md", "IDENTITY.md", "USER.md", "HEARTBEAT.md", "MEMORY.md"]
SHARED_LIB = os.path.join(OC, "workspace", "projects", "smart_glasses")

R: list[dict] = []


def chk(group: str, name: str, ok: bool, detail: str = "", fix: str = "") -> None:
    R.append({"group": group, "name": name, "ok": bool(ok), "detail": detail, "fix": fix})


def sh(cmd: list[str], cwd: str | None = None, timeout: int = 90) -> tuple[int, str]:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, timeout=timeout)
        return p.returncode, p.stdout + p.stderr
    except Exception as e:  # noqa: BLE001
        return 255, str(e)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    # ---------- A 配置本身 ----------
    cfg = None
    try:
        with open(CFG, encoding="utf-8") as f:
            cfg = json.load(f)
        chk("A 配置本身", "openclaw.json 可解析", True, CFG)
    except Exception as e:  # noqa: BLE001
        chk("A 配置本身", "openclaw.json 可解析", False, f"{e}", "配置坏了 → 全部 agent 起不来")
        cfg = {}
    chk("A 配置本身", "无 BOM (否则 schema 解析失败)", not open(CFG, "rb").read(3).startswith(b"\xef\xbb\xbf"),
        "openclaw.json 头 3 字节")
    tools = cfg.get("tools") or {}
    ag = cfg.get("agents") or {}
    _def = ag.get("defaults") or {}
    lst = {a.get("id"): a for a in (ag.get("list") or [])}
    def eff(aid: str) -> dict:
        """有效配置 = defaults 继承 + list 覆盖 (main 没有自己的 workspace/model, 靠 defaults)"""
        a = dict(lst.get(aid) or {})
        for k in ("workspace", "model", "agentDir", "name"):
            if not a.get(k):
                a[k] = _def.get(k)
        if not a.get("workspace"):
            a["workspace"] = os.path.join(OC, "workspace")
        if not a.get("agentDir"):
            a["agentDir"] = os.path.join(OC, "agents", aid)
        if not a.get("model"):
            a["model"] = ((_def.get("model") or {}).get("primary")
                          or (cfg.get("model") or {}).get("primary"))
        return a

    # ---------- B Agent 定义 ----------
    for aid, nm in NAME.items():
        inlist = aid in lst
        a = eff(aid)
        chk("B Agent 定义", f"{aid} ({nm}) 已定义", inlist, f"agents.list 里的 id={aid}")
        chk("B Agent 定义", f"{aid} 名字正确", a.get("name") == nm, f"实际: {a.get('name')}")
        chk("B Agent 定义", f"{aid} workspace 指向独立目录",
            a.get("workspace") == WS[aid] and os.path.isdir(WS[aid]),
            f"{a.get('workspace')}")
        chk("B Agent 定义", f"{aid} agentDir 存在", os.path.isdir(a.get("agentDir") or ""), str(a.get("agentDir")))
        chk("B Agent 定义", f"{aid} model 已指定", bool(a.get("model")), str(a.get("model")))

    # ---------- C Workspace 基础设施 ----------
    for aid in NAME:
        w = WS[aid]
        miss = [f for f in BOOT_FILES if not os.path.exists(os.path.join(w, f))]
        chk("C Workspace", f"{aid} 启动文件齐全 (6 个)", not miss,
            "AGENTS/SOUL/IDENTITY/USER/HEARTBEAT/MEMORY" if not miss else f"缺: {miss}",
            "缺 AGENTS.md → 该 agent 每次启动读不到自己的岗位说明书")
        sk = os.path.join(w, "skills")
        n = len(os.listdir(sk)) if os.path.isdir(sk) else 0
        chk("C Workspace", f"{aid} 专属 skill 目录非空", n > 0, f"{n} 个")
        if aid != "main":
            link = os.path.join(w, "projects")
            chk("C Workspace", f"{aid} projects 软链指向共享库",
                os.path.islink(link) and os.path.realpath(link) == os.path.realpath(os.path.join(OC, "workspace", "projects")),
                f"{link} → {os.path.realpath(link) if os.path.exists(link) else '不存在'}")
    chk("C Workspace", "共享项目库存在", os.path.isdir(SHARED_LIB), SHARED_LIB)

    # ---------- D Skill 加载 ----------
    for aid in NAME:
        rc, out = sh(["openclaw", "skills", "list", "--agent", aid])
        n_ready = out.count("ready") + out.count("✓")
        chk("D Skill 加载", f"{aid} skills list 跑得通", rc == 0, f"rc={rc}, ready≈{n_ready}")
        chk("D Skill 加载", f"{aid} 有可用 skill (≥8)", n_ready >= 8, f"ready≈{n_ready}")
        # U+FFFD / BOM / CRLF 扫描 (10-25 ClawHub 发布事故: 装了但不加载)
        bad = []
        sk = os.path.join(WS[aid], "skills")
        for root, _d, files in os.walk(sk):
            for fn in files:
                if not fn.endswith(".md"):
                    continue
                p = os.path.join(root, fn)
                try:
                    raw = open(p, "rb").read()
                    if raw.startswith(b"\xef\xbb\xbf"):
                        bad.append(f"{os.path.relpath(p, sk)}:BOM")
                    elif b"\r\n" in raw:
                        bad.append(f"{os.path.relpath(p, sk)}:CRLF")
                    elif "�" in raw.decode("utf-8", "ignore"):
                        bad.append(f"{os.path.relpath(p, sk)}:U+FFFD")
                except Exception:  # noqa: BLE001
                    pass
        chk("D Skill 加载", f"{aid} skill 正文无损坏 (BOM/CRLF/U+FFFD)", not bad,
            "全部干净" if not bad else f"损坏: {bad[:4]}",
            "U+FFFD = 发布方编码错, 信息已丢, 该 skill 直接弃用")

    # ---------- E 通信拓扑 ----------
    a2a = tools.get("agentToAgent") or {}
    chk("E 通信拓扑", "agentToAgent 开启", a2a.get("enabled") is True)
    chk("E 通信拓扑", "agentToAgent.allow 含 4 个", set(a2a.get("allow") or []) >= set(NAME),
        str(a2a.get("allow")))
    chk("E 通信拓扑", "sessions.visibility=all (跨 agent 可见)",
        (tools.get("sessions") or {}).get("visibility") == "all")
    def_allow = set(((ag.get("defaults") or {}).get("subagents") or {}).get("allowAgents") or [])
    chk("E 通信拓扑", "defaults.subagents.allowAgents 含 4 个", def_allow >= set(NAME), str(sorted(def_allow)))
    for aid in ("hw-lead", "sw-lead", "mech-lead"):
        a = lst.get(aid) or {}
        deny = (a.get("tools") or {}).get("deny") or []
        chk("E 通信拓扑", f"{aid} 禁 sessions_send (星型第 1 层)", "sessions_send" in deny, str(deny))
        sa = set((a.get("subagents") or {}).get("allowAgents") or [])
        chk("E 通信拓扑", f"{aid} 只能 spawn 自己", sa == {aid}, str(sorted(sa)))
        pp = ((a.get("tools") or {}).get("exec") or {}).get("pathPrepend") or []
        chk("E 通信拓扑", f"{aid} exec.pathPrepend 指向自己 shim (第 2 层)",
            any(f"/guards/{aid}" in p for p in pp), str(pp))

    # ---------- F 三层守卫 ----------
    for aid in ("hw-lead", "sw-lead", "mech-lead"):
        shim = os.path.join(OC, "guards", aid, "openclaw")
        ok = os.path.exists(shim) and os.access(shim, os.X_OK)
        chk("F 三层守卫", f"{aid} PATH shim 可执行", ok, shim)
        if ok:
            txt = open(shim, encoding="utf-8", errors="ignore").read()
            chk("F 三层守卫", f"{aid} shim 注入调用方身份", "OPENCLAW_CALLER_AGENT" in txt, "")
    cli = os.path.join(HOME, ".npm-global", "bin", "openclaw")
    is_wrap = os.path.exists(cli) and "星型拓扑守卫" in open(cli, encoding="utf-8", errors="ignore").read()
    chk("F 三层守卫", "CLI 入口是守卫包装器 (第 3 层)", is_wrap, cli,
        "被还原成裸二进制 → 绝对路径可绕过守卫, 消息真投递")
    log = os.path.join(OC, "guards", "star-topology.log")
    chk("F 三层守卫", "守卫审计日志存在", os.path.exists(log), log)

    # ---------- G 运行时能力 ----------
    cron_rc, cron_out = sh(["openclaw", "cron", "list", "--json"])
    njobs = 0
    if cron_rc == 0:
        try:
            njobs = len(json.loads(cron_out).get("jobs") or json.loads(cron_out))
        except Exception:  # noqa: BLE001
            njobs = 0
    chk("G 运行时能力", "cron 巡检/推进任务在位 (≥3)", njobs >= 3, f"{njobs} 个",
        "缺 → 每日巡检与周交付窗口不会自动跑")
    for sc in ("frag_write.py", "merge.py", "gate_check.py", "issue_check.py",
               "stage_gate.py", "daily_check.py", "advance.py", "status.py", "readiness.py"):
        chk("G 运行时能力", f"{sc} 存在", os.path.exists(os.path.join(SHARED_LIB, "state", sc)))
    fw = os.path.join(SHARED_LIB, "state", "frag_write.py")
    rc_fw, _ = sh([sys.executable, fw, "--show", "--agent", "main"])
    chk("G 运行时能力", "frag_write 原子写可跑", rc_fw == 0, "分片唯一合法写入口")
    for sc in ("merge.py", "gate_check.py", "issue_check.py"):
        rc_s, _ = sh([sys.executable, os.path.join(SHARED_LIB, "state", sc)])
        chk("G 运行时能力", f"{sc} 可跑", rc_s in (0, 1, 2), f"rc={rc_s}")

    # ---------- 输出 ----------
    bad = [r for r in R if not r["ok"]]
    groups = []
    for g in dict.fromkeys(r["group"] for r in R):
        rows = [r for r in R if r["group"] == g]
        groups.append({"group": g, "ok": all(r["ok"] for r in rows),
                       "n": len(rows), "bad": [r["name"] for r in rows if not r["ok"]]})

    if args.json:
        print(json.dumps({"total": len(R), "passed": len(R) - len(bad), "failed": len(bad),
                          "groups": groups, "criteria": R}, ensure_ascii=False, indent=2))
        return 1 if bad else 0

    print("=" * 78)
    print("  Agent 配置审计 · 能否开工")
    print("=" * 78)
    for g in groups:
        mark = "✅" if g["ok"] else "❌"
        print(f"\n【{g['group']}】{mark} {g['n'] - len(g['bad'])}/{g['n']} 通过")
        for r in [x for x in R if x["group"] == g["group"]]:
            if not r["ok"]:
                print(f"   ❌ {r['name']}")
                print(f"        {r['detail']}")
                if r["fix"]:
                    print(f"        → 修法: {r['fix']}")
    print()
    if bad:
        print(f"❌ 结论: **有 {len(bad)} 项配置不满足开工条件** —— 先修上面标 ❌ 的, 否则开工会卡")
        for r in bad:
            print(f"   · {r['group']} / {r['name']}" + (f" → {r['fix']}" if r["fix"] else ""))
    else:
        print(f"✅ 结论: **{len(R)}/{len(R)} 项配置全部满足开工条件**")
        print("   4 个 agent 可正常 spawn / 读 skill / 写分片 / 跑门禁; 三层守卫在位; 巡检与推进 cron 在位。")
    print("=" * 78)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
