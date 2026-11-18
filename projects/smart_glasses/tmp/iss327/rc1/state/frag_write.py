#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分片原子写工具 — 修 "并发写分片 → 合并器读到半截 → 数据静默消失"
=====================================================================
老板 10-25 压测实测缺陷: 分片用普通 open(w) 写, 合并器正好读到写了一半的 YAML →
  ① 解析失败 → 该 agent 整份数据从快照消失 (而且快照无标记)
  ② 更阴: 截断中途的 YAML **有时仍是合法 YAML** → 合并器读到"合法但残缺"的
    分片 → 零告警 → 数据静默丢

所以: **写分片必须用本工具的原子写** (tmp + os.replace, 读者永远看到完整文件)。

用法 (python 调用):
    from frag_write import update_fragment
    update_fragment("hw-lead", lambda d: d.setdefault("needs_from", []).append({...}))

用法 (命令行):
    python3 state/frag_write.py --agent hw-lead --add-need key=K1 to=sw-lead item="..."
    python3 state/frag_write.py --agent hw-lead --add-answer key=K1 to=main value="..." ref="..."
    python3 state/frag_write.py --agent hw-lead --add-artifact path=... summary="..."
    python3 state/frag_write.py --agent hw-lead --show

纪律: 只能写**自己**的分片 (--agent 必须是本 agent id)。
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
# 分片目录: 默认 state/fragments; FRAG_WRITE_DIR 仅供自动化测试指向临时目录 (防自测写坏真分片)
FRAG_DIR = os.environ.get("FRAG_WRITE_DIR") or os.path.join(HERE, "fragments")
# agent id → 分片文件名 (与现有分片保持一致)
FILE_OF = {
    "main": "pm.yaml",
    "hw-lead": "hw.yaml",
    "sw-lead": "sw.yaml",
    "mech-lead": "mech.yaml",
}
# 文件名 → agent id (反向)
AGENT_OF = {v: k for k, v in FILE_OF.items()}


def frag_path(agent: str) -> str:
    if agent not in FILE_OF:
        raise SystemExit(f"[frag_write] 未知 agent id: {agent} (可用: {list(FILE_OF)})")
    return os.path.join(FRAG_DIR, FILE_OF[agent])


def atomic_write_yaml(path: str, data: dict) -> None:
    """原子写: 唯一 tmp + fsync + os.replace → 读者永远看到完整文件。"""
    text = yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=100)
    d = os.path.dirname(path) or "."
    fd, tmp = tempfile.mkstemp(prefix=os.path.basename(path) + ".", suffix=".tmp", dir=d)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def load_fragment(agent: str) -> dict:
    p = frag_path(agent)
    if not os.path.exists(p):
        raise SystemExit(f"[frag_write] 分片不存在: {p}")
    with open(p, "r", encoding="utf-8") as f:
        d = yaml.safe_load(f)
    if not isinstance(d, dict):
        raise SystemExit(f"[frag_write] 分片格式不对 (顶层不是 dict): {p}")
    return d


def update_fragment(agent: str, mutate) -> dict:
    """读 → 改 → 原子写回。返回改后的分片。"""
    d = load_fragment(agent)
    mutate(d)
    atomic_write_yaml(frag_path(agent), d)
    return d


def _kv(arg: str) -> tuple[str, str]:
    if "=" not in arg:
        raise SystemExit(f"[frag_write] 参数要写成 key=value: {arg}")
    k, v = arg.split("=", 1)
    return k.strip(), v.strip()


# --status 的 key=value 解析: value 可带引号 (含空格), 也可裸写 (无空格)
_STATUS_KV_RE = re.compile(r'(?P<k>\w+)=(?P<v>"[^"]*"|\'[^\']*\'|\S+)')


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", required=True)
    ap.add_argument("--add-need", action="append", default=[],
                    help='key=... to=... item="..." [since=...]')
    ap.add_argument("--add-answer", action="append", default=[],
                    help='key=... to=... value="..." [ref=...]')
    ap.add_argument("--add-artifact", action="append", default=[],
                    help='path=... summary="..." [kind=...] [version=...]')
    ap.add_argument("--add-claim", action="append", default=[],
                    help='key=... value="..." [note=...]')
    ap.add_argument("--status", action="append", default=[],
                    help='phase=... progress_pct=N health=... summary="..."')
    ap.add_argument("--set", dest="set_arg", default=None,
                    help="整段替换某个列表字段: --set <field>=<JSON数组> (如 --set 'answers=[{...}]')")
    ap.add_argument("--set-json", dest="set_json", default=None,
                    help="同上, JSON 从文件读 (配合 --set-field)")
    ap.add_argument("--set-field", dest="set_field_name", default=None,
                    help="配合 --set-json: 要替换的字段名")
    ap.add_argument("--show", action="store_true")
    args = ap.parse_args()

    if args.show:
        print(yaml.safe_dump(load_fragment(args.agent), allow_unicode=True, sort_keys=False))
        return 0

    # ---- 互斥检查 (V1.1 修复: --set 分支静默吞掉其余参数, 2026-10-28 sw-lead 实测踩中) ----
    # 旧行为: --set/--set-json 命中就 `return`, 同一命令行的 --add-*/--status 全被忽略,
    #          却照样打印 "✅ 已原子更新" => 分片看着写成功了, 实际数据全丢, 零告警。
    # 新行为: --set 与增量类参数互斥; 混用直接报错退出 (非 0), 不落盘。
    set_mode = bool(args.set_arg or args.set_json)
    incr_mode = bool(args.add_need or args.add_answer or args.add_artifact
                     or args.add_claim or args.status)
    if set_mode and incr_mode:
        raise SystemExit(
            "[frag_write] X --set/--set-json 与 --add-*/--status 互斥, 不能同命令行混用。\n"
            "  --set 会**整段替换**某个列表字段; 混用会让增量被静默丢弃 (V1.0 实测坑)。\n"
            "  请拆成两条命令: 先 --set 落整段, 再 --add-* 追加。\n"
            "  (本次未落盘, 分片保持原样)"
        )
    if args.set_json and not args.set_field_name:
        raise SystemExit("[frag_write] X --set-json 必须配 --set-field <字段名>")

    def mutate(d: dict):
        if set_mode:
            if args.set_json:
                field = args.set_field_name
                with open(args.set_json, encoding="utf-8") as f:
                    val = json.load(f)
            else:
                field, _, raw = args.set_arg.partition("=")
                val = json.loads(raw)
            if not isinstance(val, list):
                raise SystemExit("[frag_write] --set 的值必须是 JSON 数组")
            d[field] = val
            return
        for spec in args.add_need:
            kv = dict(_kv(x) for x in shlex.split(spec))
            d.setdefault("needs_from", []).append({
                "key": kv.get("key"),
                "to": kv.get("to"),
                "item": kv.get("item", ""),
                "since": kv.get("since", "2026-10-25"),
            })
        for spec in args.add_answer:
            kv = dict(_kv(x) for x in shlex.split(spec))
            d.setdefault("answers", []).append({
                "key": kv.get("key"),
                "to": kv.get("to"),
                "value": kv.get("value", ""),
                "ref": kv.get("ref", ""),
            })
        for spec in args.add_artifact:
            kv = dict(_kv(x) for x in shlex.split(spec))
            d.setdefault("artifacts", []).append({
                "path": kv.get("path", ""),
                "kind": kv.get("kind", "note"),
                "version": kv.get("version", "1.0"),
                "updated_at": kv.get("updated_at", "2026-10-25"),
                "summary": kv.get("summary", ""),
            })
        for spec in args.add_claim:
            kv = dict(_kv(x) for x in shlex.split(spec))
            d.setdefault("interface_claims", []).append({
                "key": kv.get("key"),
                "value": kv.get("value", ""),
                "note": kv.get("note", ""),
                "ref": kv.get("ref", ""),
            })
        if args.status:
            kv = {}
            for m in _STATUS_KV_RE.finditer(" ".join(args.status)):
                v = m.group("v")
                if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
                    v = v[1:-1]          # 去掉包裹引号, 保留内部空格
                kv[m.group("k")] = v
            st = d.setdefault("status", {})
            for k in ("phase", "progress_pct", "health", "summary"):
                if k in kv:
                    st[k] = int(kv[k]) if k == "progress_pct" else kv[k]

    update_fragment(args.agent, mutate)
    print(f"[frag_write] ✅ {FILE_OF[args.agent]} 已原子更新 → 再跑 python3 state/merge.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
