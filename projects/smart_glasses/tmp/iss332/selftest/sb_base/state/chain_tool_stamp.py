#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""chain_tool_stamp.py —— ★★给 `<终板>.chain.json` 补上【工具指纹】+【时间戳】★★

★★★**★为什么要有它 (★2026-11-10 02:5x 实测踩出来的★)**★★★:
  ★**"跨臂不可比"的根因有两个, 不止一个** ★★
    · ① `--from-drc` 输入不同 ⇒ 预留串的目标清单不同
    · ② ★★【**工具版本**不同 ⇒ 同一输入也出不同预留串★】★★
      ⇒ ★**实测**: `v76rv` 与 `v76rw` 的 `--from-drc` 输入【完全相同】,
        但臂脚本里写的是【工具版次】(★错开平移 / 跨层★) ⇒ 预留串不同 ⇒ 臂仍不可比
  ⇒ ★★**⇒ "单变量臂" 至今一直是【两变量: 工具版本 + 预留串】★★
  ⇒ ★**⇒ 工具版本必须进【产物凭据】** (★`chain.json` 是下游唯一能验的东西★)
    ⇒ ★**只在脚本 stdout 打印 sha256 不够** (★stdout 没人存★)

★★★**★口径 (★别读错★)** ★★★:
  · ★**sha256 = 工具【内容】指纹** ⇒ 改了内容就变
  · ★**mtime = 工具【文件】时间** ⇒ 改内容必变, 但也记下"什么时候动过"
  · ★**generated_at = 这份凭据【什么时候生成】的** ⇒ 与工具 mtime 分开, 便于排时序
  · ★**这个脚本【只加字段, 不改已有字段】** ⇒ 不会破坏 `compare_arm_baseline.sh` 的读法 ★★★

用法:
  python3 state/chain_tool_stamp.py <chain.json> [--write] [--reserve-file <预留串文件>]
      ⇒ 默认只打印 (★dry-run★) · 加 `--write` 才落盘
  ⇒ rc=0 成功 · rc=1 读不到 chain.json

★★**★建议: 把下面这段直接内嵌进 `state/replay_patch_chain.sh` 写凭据的那段 (★L183 起★)★★**:
    import hashlib, json, os, time
    def _sha(p):
        h = hashlib.sha256()
        with open(p, "rb") as f:
            for c in iter(lambda: f.read(1 << 20), b""):
                h.update(c)
        return h.hexdigest()
    _tools = {}
    for _t in ("patch_astar_nostub.py", "fix_straight_links.py", "check_pcb_drc.py",
               "gen_pcb_netlist_board.py", "plan_route_reserve.py"):
        _p = os.path.join(os.path.dirname(os.path.abspath(__file__)), _t)
        if os.path.exists(_p):
            _tools[_t] = {"sha256": _sha(_p), "mtime": time.strftime("%Y-%m-%d %H:%M:%S",
                                                                        time.localtime(os.path.getmtime(_p)))}
    info["tools"] = _tools
    info["generated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
"""
import hashlib
import json
import os
import sys
import time

STATE = os.path.dirname(os.path.abspath(__file__))
TOOLS = (
    "patch_astar_nostub.py",
    "fix_straight_links.py",
    "check_pcb_drc.py",
    "gen_pcb_netlist_board.py",
    "plan_route_reserve.py",
)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def stamp_tools():
    out = {}
    for t in TOOLS:
        p = os.path.join(STATE, t)
        if not os.path.exists(p):
            continue
        out[t] = {
            "sha256": sha256(p),
            "mtime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(p))),
        }
    return out


def main():
    argv = sys.argv[1:]
    if not argv or argv[0].startswith("-"):
        print(__doc__)
        return 1
    chain_json = argv[0]
    write = "--write" in argv
    reserve_file = None
    if "--reserve-file" in argv:
        i = argv.index("--reserve-file")
        if i + 1 < len(argv):
            reserve_file = argv[i + 1]
    if not os.path.exists(chain_json):
        print("❌ 找不到 %s" % chain_json)
        return 1
    info = json.load(open(chain_json, encoding="utf-8"))
    info["tools"] = stamp_tools()
    info["generated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    if reserve_file and os.path.exists(reserve_file):
        info["reserve_file"] = os.path.abspath(reserve_file)
        info["reserve_sha256"] = sha256(reserve_file)
    print("★凭据: %s" % chain_json)
    print("★tag=%s · segments=%s" % (info.get("tag"), info.get("output_segments")))
    for k, v in info["tools"].items():
        print("   ★%-28s sha256=%s  mtime=%s" % (k, v["sha256"][:16], v["mtime"]))
    print("★generated_at = %s" % info["generated_at"])
    if write:
        json.dump(info, open(chain_json, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print("✅ 已写入 (★只加字段, 原有字段没动★)")
    else:
        print("★(dry-run: 加 --write 才落盘)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
