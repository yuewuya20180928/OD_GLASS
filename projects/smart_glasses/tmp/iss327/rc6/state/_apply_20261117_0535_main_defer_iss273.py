#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""main (moli) 2026-11-17 05:3x · job 775d9893「ARS45 继续执行后继计划」
★把 ISS-273 改成 `deferred` (★等 mech-lead 名额空出再激活·★防止第三个并发写会话★)★
★**只动 state/issue_log.yaml 一个文件 (就地把 status 行换掉 + 块尾追加 note)★★
★**不碰真源 / 分片 / 板 / 网表 / 脚表 / BOM / 任何门禁脚本 / 任务书正文**★
"""
import json
import os
import shutil

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
BAK = LOG + ".bak_20261117_0535_main_defer_iss273"
IID = "ISS-273"


def q(v) -> str:
    return json.dumps(v, ensure_ascii=False)


EXTRA = (
    " ★**2026-11-17 05:3x 追加 (main)**: 本单状态 `open` → **`deferred`** ★ ⇒ ★**原因 = 名额, 不是活没准备好**★: "
    "★**本机实测 (sessions_list, 05:2x) = mech-lead 名下有两条会话还在跑** (ISS-264 `de31bc94` / ISS-251 `6348eece` ⇒ status=running) "
    "⇒ ★**铁律: 同一 agent 同时只允许一个在飞写会话** (★两个写会话会互相覆盖 `state/fragments/mech.yaml`, ★★本轮 05:0x 已实测发生过一次 "
    "lost-update: ISS-253 写的 3 条 claim 被同秒并发写整段盖掉, 靠「写 → grep 校验 → 重试」才补回来★)★ ⇒ ★**不许现在派第三个**★ "
    "⇒ ★**恢复条件 (★由 main 改回 `open` 再派★)**: ① mech-lead 名下**无** status=fixing 的 issue ② 且**无** running 会话 "
    "(★用 `sessions_list` 实测, 别凭印象★) ⇒ ★**恢复时必须先自己 `md5sum HW/netlist_v1.csv HW/netlist_v1_pins.csv` 取盘上现值** "
    "(★任务书里写的锚点现值是 05:2x 的快照★) ⇒ ★**本单不占「板只改一次」那一趟的任何一步 (不碰板) ⇒ 恢复优先级 = 中**★"
)


def main() -> int:
    shutil.copy2(LOG, BAK)
    lines = open(LOG, encoding="utf-8").read().split("\n")
    start = end = None
    for i, ln in enumerate(lines):
        if ln.startswith("- id: "):
            if start is not None:
                end = i
                break
            if ln[len("- id: "):].strip() == IID:
                start = i
    if start is None:
        print("❌ 找不到 %s" % IID)
        return 2
    if end is None:
        end = len(lines)
    blk = lines[start:end]
    hit = False
    for j, ln in enumerate(blk):
        if ln.strip() in ('status: open', 'status: "open"'):
            blk[j] = '  status: "deferred"'
            hit = True
    if not hit:
        print("❌ 没找到 status: open 行 (可能已被人改过) ⇒ 不动")
        return 2
    while blk and blk[-1].strip() == "":
        blk.pop()
    blk.append("  defer_note: %s" % q(EXTRA))
    lines[start:end] = blk
    open(LOG, "w", encoding="utf-8").write("\n".join(lines))

    d2 = yaml.safe_load(open(LOG, encoding="utf-8")) or {}
    ids = {it["id"]: it for it in d2["issues"]}
    it = ids[IID]
    print("  %s -> %s owner=%s due=%s" % (IID, it["status"], it["owner"], it["due"]))
    print("  defer_note len =", len(it.get("defer_note") or ""))
    print("  task_brief bytes =", len(it.get("task_brief") or ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
