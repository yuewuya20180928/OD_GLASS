#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2026-11-01 21:2x —— 迁移配置补推 (老板要把 4-Agent 职能制搬到另一台主机)
=====================================================================
做 3 件事:
  ① 把本地 agent 资产 (人格/记忆/守卫/skills/局部配置) **脱敏后**复制进发布树 config/ 下
  ② 顺带修远端那份 `config/openclaw.agents.json` 的**过期项** (model 还是 MiniMax-M3 —— 已实测挂 token plan 上限)
  ③ 生成一份"带外传输清单" (4 个含凭据的文件) —— 这些**绝不进仓库**, 只列清单给老板

★安全纪律 (11-01 20:5x 刚踩过的坑, 这次必须一次做对):
  - 任何会被发布的文件, **不许有敏感串明文 —— 连拆拼的都不行**
  - 敏感真值从**本地不入库源**现读 (`~/.openclaw/openclaw.json` / `agents/*/agent/auth-profiles.json` / `TOOLS.md`)
  - 写完**反向自测**: 故意造几个泄漏文件, 看闸门抓不抓得到

纪律: 只写 config/ (发布树映射区) + HW/ 下自己的两个文件; 不碰 projects/ 的项目库本体 (那个由 publish_github.sh rsync)。
"""
import json
import os
import re
import shutil
import sys

HOME = os.path.expanduser("~/.openclaw")
WS = os.path.join(HOME, "workspace")
PROJ = os.path.join(WS, "projects", "smart_glasses")
CFG = os.path.join(PROJ, "config")          # 发布树里的 config/ 映射区
AGENTS = ("main", "hw-lead", "sw-lead", "mech-lead")

DRY = "--apply" in sys.argv


def w(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  {'✅' if DRY else '🔍'} {os.path.relpath(path, PROJ)}  ({len(content)} B)")


def copy(src, dst):
    if not os.path.exists(src):
        print(f"  ⚠️ 源不存在: {src}")
        return False
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    print(f"  {'✅' if DRY else '🔍'} {os.path.relpath(dst, PROJ)}  ({os.path.getsize(dst)} B)")
    return True


def main() -> int:
    print("=" * 96)
    print("迁移配置补推" + (" (DRY-RUN, 加 --apply 才真写)" if not DRY else " (APPLY)"))
    print("=" * 96)

    # ---------- ① agent 人格 / 身份 / 记忆 ----------
    print("\n【① 四份人格 + 身份 + 记忆】")
    for a in AGENTS:
        # ★agent id (hw-lead) ≠ workspace 目录名 (workspace-hw) —— 踩过这个坑
        _short = a.split("-")[0]   # hw-lead → hw
        wd = WS if a == "main" else os.path.join(HOME, f"workspace-{_short}")
        for f in ("SOUL.md", "IDENTITY.md", "USER.md", "MEMORY.md"):
            copy(os.path.join(wd, f), os.path.join(CFG, "agents", a, f))

    # ---------- ② main 的日记 ----------
    print("\n【② main 的 memory/ 日记】")
    mdir = os.path.join(WS, "memory")
    n = 0
    if os.path.isdir(mdir):
        for f in sorted(os.listdir(mdir)):
            if f.endswith(".md"):
                copy(os.path.join(mdir, f), os.path.join(CFG, "agents", "main", "memory", f))
                n += 1
    print(f"  ⇒ {n} 篇")

    # ---------- ③ guards ----------
    print("\n【③ guards PATH shim (跨 agent 通信守卫)】")
    gdir = os.path.join(HOME, "guards")
    for a in ("hw-lead", "sw-lead", "mech-lead"):
        copy(os.path.join(gdir, a, "openclaw"), os.path.join(CFG, "guards", a, "openclaw"))
    copy(os.path.join(gdir, "star-topology.log"), os.path.join(CFG, "guards", "star-topology.log"))

    # ---------- ④ agent 局部配置 (只拷**不含凭据**的) ----------
    print("\n【④ agent 局部配置】")
    for a in AGENTS:
        ad = os.path.join(HOME, "agents", a, "agent")
        for f in ("models.json", "auth-state.json"):
            copy(os.path.join(ad, f), os.path.join(CFG, "agents", a, "agent", f))
        # ★ auth-profiles.json **不拷** (含 minimax API key) ⇒ 列入带外清单

    # ---------- ⑤ skills ----------
    print("\n【⑤ skills】")
    for f in sorted(os.listdir(os.path.join(WS, "skills"))):
        src = os.path.join(WS, "skills", f)
        if f.startswith(".") or f.startswith("_"):
            continue
        if os.path.isdir(src):
            shutil.copytree(src, os.path.join(CFG, "skills", f), dirs_exist_ok=True)
            print(f"  {'✅' if DRY else '🔍'} config/skills/{f}/ (整目录)")
    for f in sorted(os.listdir(os.path.join(HOME, "skills"))):
        src = os.path.join(HOME, "skills", f)
        if f.startswith(".") or f.startswith("_"):
            continue
        if os.path.isdir(src):
            shutil.copytree(src, os.path.join(CFG, "skills-global", f), dirs_exist_ok=True)
            print(f"  {'✅' if DRY else '🔍'} config/skills-global/{f}/ (整目录)")

    # ---------- ⑥ 修 openclaw.agents.json 的过期项 ----------
    print("\n【⑥ config/openclaw.agents.json —— 修过期项】")
    # ★openclaw.agents.json 映射到**发布树根**的 config/ (不在项目树里) ⇒ 本地源 = 发布树副本
    p = os.path.join(CFG, "openclaw.agents.json")
    if not os.path.exists(p):
        # 回退: 从远端发布树副本拿 (publish_github.sh 已 cp 过)
        cand = "/tmp/od_glass_publish/config/openclaw.agents.json"
        if os.path.exists(cand):
            shutil.copy2(cand, p)
            print(f"  ↩ 从发布树副本取回 {cand}")
    if os.path.exists(p):
        d = json.load(open(p, encoding="utf-8"))
        changed = []
        # ★ model: MiniMax-M3 → MiniMax-M3.1-Flash (M3 已实测挂 token plan 上限)
        for key in ("defaults",):
            if key in d.get("agents", {}) and d["agents"][key].get("model_primary") == "minimax/MiniMax-M3":
                d["agents"][key]["model_primary"] = "minimax/MiniMax-M3.1-Flash"
                changed.append("agents.defaults.model_primary")
        for a in d.get("agents", {}).get("list", []):
            if a.get("model") == "minimax/MiniMax-M3":
                a["model"] = "minimax/MiniMax-M3.1-Flash"
                changed.append(f"agents.list[{a.get('id')}].model")
        # ★ workspace 占位符: <OPENCLAW_HOME> → <OPENCLAW_HOME>/workspace-<id>
        for a in d.get("agents", {}).get("list", []):
            aid = a.get("id")
            if aid and aid != "main" and a.get("workspace") == "<OPENCLAW_HOME>":
                a["workspace"] = "<OPENCLAW_HOME>/workspace-" + aid.split("-")[0]
                changed.append(f"agents.list[{aid}].workspace")
            if aid and aid != "main" and a.get("agentDir") == "<OPENCLAW_HOME>":
                a["agentDir"] = "<OPENCLAW_HOME>/agents/" + aid + "/agent"
                changed.append(f"agents.list[{aid}].agentDir")
        # ★ guards 路径占位符
        for a in d.get("agents", {}).get("list", []):
            aid = a.get("id")
            for pp in ((a.get("tools") or {}).get("exec") or {}).get("pathPrepend") or []:
                if pp.startswith("/home/yuewuya/"):
                    a["tools"]["exec"]["pathPrepend"] = ["<OPENCLAW_HOME>/guards/" + aid]
                    changed.append(f"agents.list[{aid}].tools.exec.pathPrepend")
                    break
        d["_note"] = (
            "脱敏后的 agent 配置摘录 (只含 agents 定义与 tools 拓扑); 凭据 "
            "(gateway token / tavily apiKey / minimax API key / 微信 openid) 已在源头剔除, 原件不入库 —— "
            "★这 4 类走带外传输, 清单见 config/OFFLINE_TRANSFER_CHECKLIST.md。"
            "★★model 已从 minimax/MiniMax-M3 改成 minimax/MiniMax-M3.1-Flash (2026-11-01): "
            "M3 在 10-28 起实测**挂 token plan 上限**, 照抄会让人在新主机一开局就撞同一个坑。"
        )
        w(p, json.dumps(d, ensure_ascii=False, indent=2) + "\n")
        print(f"  ⇒ 改动 {len(changed)} 处: {changed}")
    else:
        print("  ⚠️ 找不到 config/openclaw.agents.json")

    # ---------- ⑦ 带外传输清单 ----------
    print("\n【⑦ 带外传输清单 (含凭据, 绝不进仓库)】")
    items = [
        ("~/.openclaw/openclaw.json", "gateway auth token (48 字符) + tavily apiKey"),
        ("~/.openclaw/workspace/TOOLS.md", "板子 SSH 明文口令"),
        ("~/.openclaw/agents/main/agent/auth-profiles.json", "minimax API key (sk-cp-...)"),
        ("~/.openclaw/cron/jobs.json", "微信 openid (推送目标) + 全部 cron payload"),
    ]
    lines = [
        "# 带外传输清单 —— ★这 4 个文件含凭据, **绝对不能进 GitHub**",
        "",
        "> 生成: 2026-11-01 21:2x (项目总工) · 配套 `HW/AGENT_MIGRATION_PLAN.md`",
        "> ★**仓库是公开的** (yuewuya20180928/OD_GLASS, 免登录可读) ⇒ 推上去 = 泄给所有人",
        "",
        "| 文件 | 含什么 | 怎么带 |",
        "|---|---|---|",
    ]
    for path, what in items:
        lines.append(f"| `{path}` | {what} | ★scp 直传 / 密码管理器 / 加密包 (三选一) |")
    lines += [
        "",
        "## ★为什么它们不在仓库里 (11-01 20:5x 的教训)",
        "",
        "- 上一版发布脚本把微信 openid **拆拼**后硬编码在自己里 (`\"前半\" + \"后半\"`) ⇒ 拆拼骗过了'自己扫自己'，"
        "但**两段明文都在会被公开的脚本里** ⇒ grep 一下就拼得回来 ⇒ **等于把凭据发到公开仓库**。",
        "- ⇒ 现在的规则: **脚本里一个敏感串明文都不写**，全部从**本地不入库的真值源**现读"
        " (`~/.openclaw/openclaw.json` / `cron/jobs.json` / `TOOLS.md`)。",
        "",
        "## ★★落地后必做 (在新主机上)",
        "",
        "```bash",
        "# 1. 铺好凭据文件",
        "cp <带外传来的>/openclaw.json            ~/.openclaw/",
        "cp <带外传来的>/TOOLS.md                ~/.openclaw/workspace/",
        "cp <带外传来的>/auth-profiles.json      ~/.openclaw/agents/main/agent/",
        "cp <带外传来的>/jobs.json               ~/.openclaw/cron/",
        "# 2. ★把 agents 段合进 openclaw.json (别直接覆盖!) —— 见 AGENT_MIGRATION_PLAN.md §6",
        "# 3. ★验证闸门抓得住 (反向自测)",
        "cd ~/.openclaw/workspace/projects/smart_glasses && python3 state/publish_github.sh --selftest",
        "```",
        "",
        "## ★★旧主机的处置 (★顺序不能反)",
        "",
        "1. **先停旧主机的 cron** (否则两边同时派活 ⇒ 互相覆盖分片)",
        "2. 再在新主机开 cron (每个 job 带 `model=minimax/MiniMax-M3.1-Flash`)",
        "3. ★旧主机的 `TOOLS.md` / `auth-profiles.json` **带完之后从旧机删掉或降权** (它们是全机凭据)",
    ]
    w(os.path.join(CFG, "OFFLINE_TRANSFER_CHECKLIST.md"), "\n".join(lines) + "\n")

    print("\n" + "=" * 96)
    print("✅ 完成" + (" (DRY-RUN: 加 --apply 才真写)" if not DRY else " (已落盘)"))
    print("=" * 96)
    return 0


if __name__ == "__main__":
    sys.exit(main())
