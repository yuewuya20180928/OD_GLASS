#!/usr/bin/env python3
# ★★★★★★2026-11-11 05:5x 【★臂溯源侧车: ★臂跑完写 `<板>.routersrc.json`★】★★★★★★
#   ★**为什么必须有 (★实测踩到★)**: ★★
#     ★**现状**: 臂脚本只在日志里打印一次 `gen_pcb_routing.py sha256 = ...` ⇒ 链凭据里只能记【当前源码的 sha】★
#       ⇒ ★★**⇒ 源码一漂 (★实测: 0bd649b8 → 5a5ce4b4★) ⇒ 凭据就在撒谎 ⇒ ★照凭据复现会得到另一块板** ★★
#     ★★**⇒ ⇒ 【配方 = 路由器源码 + env + 链参数】⇒ 三样都得钉在【产物旁边】★** ★★
#   ★**为什么不动路由器源码 (★重要★)**: ★**改路由器 ⇒ sha 变 ⇒ 所有老臂读数都要重新标定**★
#     ⇒ ★★**⇒ 侧车写在【臂脚本】里 ⇒ 路由器 sha 不变 ⇒ 老臂读数继续有效** ★★
#   ★**用法**: ★`python3 state/arm_provenance.py <板路径> --arm <臂名> [--router-src <快照.py>]` ★
import hashlib
import json
import os
import subprocess
import sys
import time


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def main():
    if len(sys.argv) < 2:
        print("用法: python3 state/arm_provenance.py <板路径> --arm <臂名> [--router-src <快照.py>]")
        return 2
    board = os.path.abspath(sys.argv[1])
    arm = ""
    router_src = ""
    argv = sys.argv[2:]
    for i, a in enumerate(argv):
        if a == "--arm" and i + 1 < len(argv):
            arm = argv[i + 1]
        if a == "--router-src" and i + 1 < len(argv):
            router_src = argv[i + 1]
    if not os.path.exists(board):
        print("❌ 板不存在: %s" % board)
        return 3

    here = os.path.dirname(os.path.abspath(__file__))
    live = os.path.join(here, "gen_pcb_routing.py")
    used = router_src if router_src else live
    used_abs = os.path.abspath(used)
    if not os.path.exists(used_abs):
        print("❌ 路由器快照不存在: %s" % used_abs)
        return 3

    info = {
        "arm": arm,
        "board": board,
        "board_md5": hashlib.md5(open(board, "rb").read()).hexdigest(),
        "router_src_file": os.path.basename(used_abs),
        "router_src_path": used_abs,
        "router_src_sha256": sha256(used_abs),
        "live_router_sha256": sha256(live),
        "key_env": {k: v for k, v in os.environ.items() if k.startswith("PCB_")},
        "written_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "note": "★**这块板是【路由器产物】⇒ 配方 = 本文件 + 链凭据 ⇒ ★源码漂了也认这份**",
    }
    out = board + ".routersrc.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)
    print("  ✅ 臂溯源侧车: %s" % out)
    print("     路由器源码 %s sha=%s" % (info["router_src_file"], info["router_src_sha256"][:16]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
