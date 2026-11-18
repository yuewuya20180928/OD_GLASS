#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iss311_frag_write.py —— ISS-311 交卷 · 分片写入驱动 (hw-lead)
★★**唯一写入口 = `python3 state/frag_write.py --agent hw-lead …` (★原子写·禁 open(p,"w")★)** ★★
★本脚本**只负责把 spec 组装成 argv** ⇒ 真正的落盘仍由 `state/frag_write.py` 做 (★原子 tmp + os.replace★) ★
★**只写自己那一份** (`state/fragments/hw.yaml`) ★

★为什么用 subprocess 而不是直接 import: ★**纪律要求「用 frag_write.py 原子写」⇒ 走它的 CLI 才是同一口径** ★
★shlex 兼容性处理: ★**spec 文本里禁止出现双引号 / 反斜杠** (★shlex 会把它们当语法★) ⇒ 落盘前统一替换成「」/／ ★
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))
SPEC = os.path.join(HERE, "iss311_frag_spec.json")


def sanitize(s: str) -> str:
    s = str(s)
    s = s.replace('"', "「").replace("\\", "／")
    s = s.replace("`", "'")
    return s


def spec_for(**kw):
    """把 dict 组装成 `key=v ...` 的单个 spec 串 (★值含空格 ⇒ 用双引号包住★)"""
    parts = []
    for k, v in kw.items():
        v = sanitize(v)
        parts.append(f'{k}="{v}"')
    return " ".join(parts)


def main():
    with open(SPEC, encoding="utf-8") as f:
        spec = json.load(f)
    argv = [sys.executable, os.path.join(PROJ, "state", "frag_write.py"), "--agent", "hw-lead"]
    for a in spec.get("artifacts", []):
        argv += ["--add-artifact", spec_for(
            path=a["path"], kind=a.get("kind", "note"),
            version=a.get("version", "iss311-v1"),
            updated_at=a.get("updated_at", "2026-11-18"),
            summary=a["summary"])]
    for n in spec.get("needs", []):
        argv += ["--add-need", spec_for(
            key=n["key"], to=n["to"], item=n["item"], since=n.get("since", "2026-11-18"))]
    r = subprocess.run(argv, cwd=PROJ, capture_output=True, text=True)
    print(r.stdout)
    if r.stderr:
        print(r.stderr, file=sys.stderr)
    print(f"rc={r.returncode}")
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
