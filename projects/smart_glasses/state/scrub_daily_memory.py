#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scrub_daily_memory.py —— 日记同步的**脱敏过滤**
================================================================================
为什么需要它 (实测事故 2026-11-05 09:58):
  发布脚本新增了"把 $WS/memory/*.md 同步进发布树"这一步 (公开仓的日记原本停在 11-02),
  第一次跑就被发布脚本自带的真值反查闸门拦下:
    ❌ 命中: ('config/agents/main/memory/2026-06-06.md', 'VALUE_SHAPE:wechat-openid (o9cq80...)')
  ⇒⇒ 闸门**正确拦住了推送** (rc=1, 一个字节都没推上去) ⇒⇒ 这是闸门在干活, 不是故障。
  但"整份日记不发布"太粗 ⇒⇒ 本脚本做**细粒度过滤**: 命中的文件跳过, 干净的文件照发。

两条纪律:
  ① 过滤规则必须与发布闸门 (publish_github.sh 里的真值反查) **同一套** ⇒
     这里过的文件, 闸门那里不会再拦 (口径不一致 = 反复卡)
  ② 默认只发布**近 N 天**的日记 (--days, 默认 14) ⇒
     不把半年的聊天流水一次性倒进公开仓 (仓库是公开的)

用法:
  python3 state/scrub_daily_memory.py <源目录> <目标目录> [--days 14] [--apply] [--dry-run]
退出码: 0 = 正常 (含"有文件被跳过"的情形; 跳过清单打在 stdout) · 1 = 参数/IO 错
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import sys

# ★与发布闸门同一套值形态规则 (wechat-openid / 各家 API key / AWS AKIA)
VALUE_PATTERNS = [
    ("sk-cp-", re.compile(r"sk-cp-[A-Za-z0-9_\-]{20,}")),
    ("sk-ant-", re.compile(r"sk-ant-[A-Za-z0-9_\-]{20,}")),
    ("tvly-", re.compile(r"tvly-[A-Za-z0-9_\-]{20,}")),
    ("ghp_", re.compile(r"ghp_[A-Za-z0-9]{20,}")),
    ("github_pat_", re.compile(r"github_pat_[A-Za-z0-9_]{20,}")),
    ("sk-proj-", re.compile(r"sk-proj-[A-Za-z0-9_\-]{20,}")),
    ("AKIA", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("wechat-openid", re.compile(r"o9cq[0-9A-Za-z]{12,}")),
]


def credential_truths() -> list[str]:
    """从 openclaw.json + 各 agent 的 auth-profiles/models.json 现读凭据真值。
    ★不在脚本里写任何明文 (自指悖论)。"""
    out: list[str] = []
    cfgp = os.path.expanduser("~/.openclaw/openclaw.json")
    try:
        with open(cfgp, encoding="utf-8") as f:
            cfg = json.load(f)

        def walk(o, p=""):
            if isinstance(o, dict):
                for k, v in o.items():
                    if isinstance(v, str) and len(v) >= 20 and re.search(r"(key|token|secret|password)", k, re.I):
                        out.append(v)
                    else:
                        walk(v, f"{p}/{k}")
            elif isinstance(o, list):
                for i, v in enumerate(o):
                    walk(v, f"{p}[{i}]")

        walk(cfg)
    except Exception:
        pass
    import glob
    for p in sorted(glob.glob(os.path.expanduser("~/.openclaw/agents/*/agent/auth-profiles.json"))) + \
             sorted(glob.glob(os.path.expanduser("~/.openclaw/agents/*/agent/models.json"))):
        try:
            with open(p, encoding="utf-8") as f:
                d = json.load(f)

            def w2(o):
                if isinstance(o, dict):
                    for k, v in o.items():
                        if isinstance(v, str) and len(v) >= 20 and re.search(r"(key|token|secret)", k, re.I):
                            out.append(v)
                        else:
                            w2(v)
                elif isinstance(o, list):
                    for v in o:
                        w2(v)

            w2(d)
        except Exception:
            pass
    return sorted({v for v in out if v})


def device_passwords() -> list[str]:
    """从 TOOLS.md / MEMORY.md 现读设备口令 (低熵) —— 走**上下文**匹配, 光出现不算。"""
    out: set[str] = set()
    for p in (os.path.expanduser("~/.openclaw/workspace/TOOLS.md"),
              os.path.expanduser("~/.openclaw/workspace/MEMORY.md")):
        try:
            with open(p, encoding="utf-8") as f:
                s = f.read()
        except Exception:
            continue
        pat = (r"(?i)(?:sshpass\s+-p\s+|密码\s*[:：]\s*|pass(?:word|wd)?\s*[:=]\s*)"
               r"[\s*`\"']*([A-Za-z0-9_@!#$%^&*.-]{3,24})[\s*`\"']*")
        for m in re.finditer(pat, s):
            out.add(m.group(1))
    return sorted(out)


def _pw_rules(pw: str) -> list[re.Pattern]:
    """★与发布闸门 (publish_github.sh 的 EXTRA_RE) **逐条一致**的口令上下文规则。
    ★★口径提醒 (发布闸门注释里写过同一个坑): 设备口令与板子品牌名 **Radxa 同形**
    ⇒ 硬件文档里满篇 "Board: radxa" ⇒ ★**不能**用"任意 key: value"这种松规则
    ⇒ 这里只保留收紧后的 6 条 (口令语义键 / 引号定界 / URL userinfo / sshpass / 密码: / password:)"""
    e = re.escape(pw)
    ctx = r"[\s*`\"]*"
    boundary = r"(?![-_/A-Za-z0-9])(?!\.[A-Za-z])(?!\s+[A-Za-z0-9])"
    kwd = (r"(?:pwd|pw|pass(?:[_-]?(?:word|wd))?|passphrase|secret(?:[_-]?key)?|token|"
           r"api[_-]?key|apikey|access[_-]?key|client[_-]?secret|private[_-]?key|auth(?:[_-]?token)?|"
           r"keys?|credential|cred|login|signin|sign[_-]?in|ssh[_-]?pass|user(?:[_-]?name)?|"
           r"密码|密碼|口令|账号|帐号|账户|用户|密钥|授权码|校验码)")
    return [
        re.compile(r"sshpass\s+-p\s+['\"]?" + e + r"\b"),
        re.compile(r"(?i)(?<![A-Za-z0-9])pass(?:[_-]?(?:word|wd))?(?![A-Za-z0-9])" + ctx
                   + r"(?:[:=：]|\|)" + ctx + r"['\"]?" + e + boundary),
        re.compile(r"(?i)密码" + ctx + r"(?:[:=：]|\|)" + ctx + r"['\"]?" + e + boundary),
        re.compile(r"(?i)(?<![A-Za-z0-9])" + kwd + r"(?![A-Za-z0-9])" + ctx
                   + r"(?:[:=：]|\|)" + ctx + r"['\"]?" + e + boundary),
        re.compile(r"(?i)" + ctx + r"[:=：]" + ctx + r"['\"`]" + e + r"['\"`]"),
        re.compile(r"(?i)" + ctx + r"[:=：]" + ctx + r"['\"]?" + e + r"@"),
    ]


def scan(path: str) -> list[str]:
    """返回该文件命中的敏感标签 (空 = 干净)"""
    try:
        with open(path, "rb") as f:
            data = f.read().decode("utf-8", "ignore")
    except Exception:
        return ["unreadable"]
    hits = []
    for t in credential_truths():
        if t and t in data:
            hits.append("CRED_TRUTH")
            break
    for tag, rx in VALUE_PATTERNS:
        if rx.search(data):
            hits.append(f"VALUE_SHAPE:{tag}")
    for pw in device_passwords():
        for rx in _pw_rules(pw):
            if rx.search(data):
                hits.append("DEVICE_PWD")
                break
        if "DEVICE_PWD" in hits:
            break
    return sorted(set(hits))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--days", type=int, default=14)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not os.path.isdir(args.src):
        print(f"❌ 源目录不存在: {args.src}")
        return 1

    cutoff = dt.date.today() - dt.timedelta(days=args.days)
    copied, skipped, out_of_window = [], [], 0

    for name in sorted(os.listdir(args.src)):
        if not name.endswith(".md"):
            continue
        sp = os.path.join(args.src, name)
        if not os.path.isfile(sp):
            continue
        # 时间窗: 文件名是 YYYY-MM-DD.md ⇒ 按名字判; 不是日期名的按 mtime 判
        m = re.match(r"^(\d{4}-\d{2}-\d{2})\.md$", name)
        if m:
            try:
                d = dt.date.fromisoformat(m.group(1))
            except Exception:
                d = None
        else:
            d = None
        if d is None:
            d = dt.date.fromtimestamp(os.path.getmtime(sp))
        if d < cutoff:
            out_of_window += 1
            continue
        hits = scan(sp)
        if hits:
            skipped.append((name, hits))
            continue
        if args.apply and not args.dry_run:
            os.makedirs(args.dst, exist_ok=True)
            shutil.copy2(sp, os.path.join(args.dst, name))
        copied.append(name)

    print(f"日记脱敏过滤: 窗口={cutoff} 起 (--days {args.days}) · 干净可发 {len(copied)} 份 · "
          f"★敏感跳过 {len(skipped)} 份 · 窗口外 {out_of_window} 份")
    for n, h in skipped:
        print(f"   ⛔ 跳过 {n}  ({', '.join(h)})")

    # ★★自愈: **清掉目标目录里已经落地的脏文件**
    #   起因 (实测 2026-11-05 10:05): 第一次没加过滤直接 rsync 全量日记 ⇒
    #   脏文件 2026-06-06.md 已经进了项目树 ⇒ 闸门每次都拦 ⇒ 推不出去。
    #   ⇒⇒ 光"不复制"不够, 必须**把已落地的脏文件删掉**。
    purged = []
    if os.path.isdir(args.dst):
        for name in sorted(os.listdir(args.dst)):
            if not name.endswith(".md"):
                continue
            dp = os.path.join(args.dst, name)
            if not os.path.isfile(dp):
                continue
            hits = scan(dp)
            if hits:
                purged.append((name, hits))
                if args.apply and not args.dry_run:
                    os.remove(dp)
    if purged:
        print(f"   ★已清掉目标目录里的脏文件 {len(purged)} 份: "
              + ", ".join(f"{n}({','.join(h)})" for n, h in purged))

    # ★★注意: **不做窗口剪枝** —— 发布树里**本来就跟踪了 50+ 份 6/7 月的日记**
    #   (实测 git ls-files config/agents/main/memory/ 有 2026-06-11 … 2026-11-02)
    #   ⇒⇒ 删它们 = 擅自改老板仓库里已有的内容 ⇒⇒ 不做
    #   ⇒ 只做两件事: ① 脏文件清掉 ② 近 14 天的补进来
    if args.dry_run:
        print("   (dry-run: 没真复制)")
    elif not args.apply:
        print("   (未加 --apply: 没真复制)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
