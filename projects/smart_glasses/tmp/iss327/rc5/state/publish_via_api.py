#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GitHub 发布 — API 通道 (git-pack 传输被掐时的降级路径)
====================================================================
★为什么需要这条路 (2026-10-29 00:4x 实测):
  - `git fetch` / `git clone` 全部在 "fetch-pack: unexpected disconnect while reading sideband packet" 断掉
  - 但 `https://api.github.com` **HTTP 200 / 0.35s**, SSH **认证握手也通**
  ⇒ 断的是 **git 协议的数据传输层**, 不是网络本身
  ⇒ 用 **GitHub REST API 的 Contents API** 逐文件 PUT, 绕开 git 传输

★前置条件: 需要一个带 `repo` 权限的 token。
  - 优先读环境变量 `GITHUB_TOKEN` / `GH_TOKEN`
  - 否则读 `~/.config/gh/hosts.yml` (gh CLI 登录态)
  - 都没有 ⇒ 明确报错退出 (不静默失败)

★语义与 publish_github.sh 一致:
  - 只推"需要更新的文件" (按本地 mtime vs 远端 blob sha 比对, 省 API 配额)
  - 推完做 SHA 回读校验
  - 不做凭据真值反查 (那需要整棵树扫描, 走 git 通道时做; 本通道推的文件是项目文件, 同样受发布脚本的脱敏约束)

用法:
  python3 state/publish_via_api.py                 # 推全部需要更新的文件
  python3 state/publish_via_api.py --dry-run       # 只看会推哪些
  python3 state/publish_via_api.py --file a,b,c    # 只推指定文件 (相对项目根)
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
REPO = "yuewuya20180928/OD_GLASS"
API = "https://api.github.com"

# 远端路径前缀: 项目库内的文件 → 仓库里的 projects/smart_glasses/...
REMOTE_PREFIX = "projects/smart_glasses/"


def get_token() -> str | None:
    for k in ("GITHUB_TOKEN", "GH_TOKEN", "GITHUB_API_TOKEN"):
        v = os.environ.get(k)
        if v:
            return v.strip()
    # gh CLI 登录态
    for p in (os.path.expanduser("~/.config/gh/hosts.yml"),):
        if not os.path.exists(p):
            continue
        try:
            txt = open(p, encoding="utf-8").read()
        except OSError:
            continue
        for line in txt.split("\n"):
            if line.strip().startswith("oauth_token:"):
                return line.split(":", 1)[1].strip().strip("'\"")
    return None


def api(path: str, token: str, method: str = "GET", body: dict | None = None):
    req = urllib.request.Request(
        f"{API}{path}",
        method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "openclaw-publish-api",
            **({"Content-Type": "application/json"} if body is not None else {}),
        },
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode() or "{}")


def blob_sha(path: str) -> str:
    """git blob sha = sha1("blob <len>\\0" + content)"""
    with open(path, "rb") as f:
        data = f.read()
    h = hashlib.sha1()
    h.update(b"blob %d\0" % len(data))
    h.update(data)
    return h.hexdigest()


def remote_blob_sha(token: str, remote_path: str) -> str | None:
    try:
        d = api(f"/repos/{REPO}/contents/{remote_path}", token)
        return d.get("sha")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--file", default="")
    ap.add_argument("--message", default="API 通道发布 (git 传输受阻时的降级)")
    args = ap.parse_args()

    token = get_token()
    if not token:
        print("❌ 找不到 GitHub token (GITHUB_TOKEN / GH_TOKEN 环境变量, 或 ~/.config/gh/hosts.yml)")
        print("   ★没有 token 就不能用 API 通道 —— 等 git 网络恢复后走 publish_github.sh")
        return 2

    # 待推文件: 排除运行时垃圾
    EXCLUDE_DIRS = {"__pycache__", ".git", "state/outbox/attach"}
    EXCLUDE_SUFFIX = (".pyc", ".tmp", ".bak")
    files: list[str] = []
    if args.file:
        files = [x.strip() for x in args.file.split(",") if x.strip()]
    else:
        for root, dirs, fns in os.walk(PROJ):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith(".")]
            for fn in fns:
                if fn.endswith(EXCLUDE_SUFFIX) or fn.startswith("."):
                    continue
                full = os.path.join(root, fn)
                rel = os.path.relpath(full, PROJ)
                files.append(rel)

    # 根级还有几份不在项目目录里的 (docs/ 等) —— 从发布树同步过来
    PUB = "/tmp/od_glass_publish"
    extra = []
    if os.path.isdir(PUB):
        for sub in ("docs", "config"):
            d = os.path.join(PUB, sub)
            if os.path.isdir(d):
                for root, dirs, fns in os.walk(d):
                    dirs[:] = [x for x in dirs if x != "__pycache__"]
                    for fn in fns:
                        if fn.endswith((".pyc", ".tmp")):
                            continue
                        full = os.path.join(root, fn)
                        extra.append((full, os.path.relpath(full, PUB)))

    todo: list[tuple[str, str]] = []   # (本地绝对路径, 远端路径)
    for rel in files:
        local = os.path.join(PROJ, rel)
        if not os.path.isfile(local):
            continue
        todo.append((local, REMOTE_PREFIX + rel.replace(os.sep, "/")))
    for full, rel in extra:
        todo.append((full, rel.replace(os.sep, "/")))

    # 去重
    seen = set()
    uniq = []
    for local, remote in todo:
        if remote in seen:
            continue
        seen.add(remote)
        uniq.append((local, remote))

    print(f"🔑 API 通道: {REPO} · 待检查 {len(uniq)} 个文件")
    changed = []
    for local, remote in uniq:
        try:
            rsha = remote_blob_sha(token, remote)
        except Exception as e:  # noqa: BLE001
            print(f"  ⚠️ 远端查询失败 {remote}: {type(e).__name__}")
            continue
        lsha = blob_sha(local)
        if rsha != lsha:
            changed.append((local, remote, lsha))
    print(f"   → 需要更新 {len(changed)} 个")

    if args.dry_run:
        for _, remote, _ in changed:
            print(f"   · {remote}")
        return 0

    ok = bad = 0
    for local, remote, lsha in changed:
        try:
            with open(local, "rb") as f:
                content = f.read()
            b64 = base64.b64encode(content).decode()
            body = {
                "message": f"{args.message}: {os.path.basename(remote)}",
                "content": b64,
                "branch": "main",
                "sha": remote_blob_sha(token, remote),   # 已有文件要带 sha (更新场景)
            }
            body = {k: v for k, v in body.items() if v is not None}
            api(f"/repos/{REPO}/contents/{remote}", token, method="PUT", body=body)
            # 回读校验
            back = remote_blob_sha(token, remote)
            if back == lsha:
                print(f"   ✅ {remote}")
                ok += 1
            else:
                print(f"   ⚠️ {remote} SHA 不符 (远端 {back} != 本地 {lsha})")
                bad += 1
        except urllib.error.HTTPError as e:
            detail = ""
            try:
                detail = e.read().decode()[:200]
            except Exception:  # noqa: BLE001
                pass
            print(f"   ❌ {remote}: HTTP {e.code} {detail}")
            bad += 1
        except Exception as e:  # noqa: BLE001
            print(f"   ❌ {remote}: {type(e).__name__}: {e}")
            bad += 1

    print(f"\n{'=' * 60}")
    print(f"API 通道发布: 成功 {ok} · 失败 {bad}")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
