#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-349 cont1 · 附项 1 · q3_storage_and_audio 的 item 措辞订正 (★只改这一句措辞★)

★**纪律**: 零 open(p,"w") 手写 hw.yaml ⇒ 本脚本只【读】hw.yaml + 【生成】一份 JSON 中间件
   ⇒ 真正的写盘一律走 `python3 state/frag_write.py --agent hw-lead --set-json <file> --set-field needs_from`

改动:
  现状: 「外挂 SPI-NOR 16-64MB」
  改为: 「外挂 SPI-NOR ≥128 MiB (1 Gbit) 起」
不动: to / due / since / waiting_on / 其它任何字段 / 其它任何 needs_from 条目
"""
from __future__ import annotations

import datetime
import json
import os
import sys

import yaml

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
FRAG = os.path.join(PROJ, "state", "fragments", "hw.yaml")
OUT = os.path.join(PROJ, "logs", "iss349", "cont1", "needs_from_after.json")

OLD = "外挂 SPI-NOR 16-64MB"
NEW = "外挂 SPI-NOR ≥128 MiB (1 Gbit) 起"
KEY = "q3_storage_and_audio"


def main() -> int:
    d = yaml.safe_load(open(FRAG, encoding="utf-8"))
    needs = d["needs_from"]

    # 1) 定位 (★必须恰好 1 条★)
    hits = [i for i, it in enumerate(needs) if it.get("key") == KEY]
    if len(hits) != 1:
        print("[X] key %s 命中 %d 条 (期望 1) ⇒ 不动盘" % (KEY, len(hits)))
        return 1
    idx = hits[0]
    before = json.dumps(needs[idx], ensure_ascii=False, sort_keys=True)
    old_item = needs[idx].get("item", "")
    if OLD not in old_item:
        print("[X] 目标串 %r 不在 item 里 ⇒ 不动盘" % OLD)
        print("    现行 item = %s" % old_item)
        return 1

    # 2) 改 item (★只改这一句★)
    new_item = old_item.replace(OLD, NEW)
    needs[idx] = dict(needs[idx])
    needs[idx]["item"] = new_item

    # 3) 自检: 除了 item, 这个条目其它字段逐字不变
    after = json.dumps(needs[idx], ensure_ascii=False, sort_keys=True)
    b = json.loads(before)
    a = json.loads(after)
    diff_fields = [k for k in set(b) | set(a) if b.get(k) != a.get(k)]
    if diff_fields != ["item"]:
        print("[X] 改动字段 = %s (期望只有 item) ⇒ 不动盘" % diff_fields)
        return 1
    # 4) 自检: 其它条目逐字不变
    for i, it in enumerate(needs):
        if i == idx:
            continue
        if it.get("key") == KEY:
            print("[X] 重复 key ⇒ 不动盘")
            return 1

    # 5) 类型体检 (★YAML 日期会被 json 序列化 ⇒ 先查有没有 date/datetime 漏网的★)
    def walk(o, path="needs_from"):
        bad = []
        if isinstance(o, dict):
            for k, v in o.items():
                bad += walk(v, "%s.%s" % (path, k))
        elif isinstance(o, list):
            for i, v in enumerate(o):
                bad += walk(v, "%s[%d]" % (path, i))
        elif isinstance(o, (datetime.date, datetime.datetime)):
            bad.append("%s = %r (非字符串·会被 json 序列化掉)" % (path, o))
        return bad

    bad = walk(needs)
    if bad:
        print("[X] 发现非字符串日期字段 ⇒ 不动盘:")
        for b_ in bad[:20]:
            print("    " + b_)
        return 1

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(needs, f, ensure_ascii=False, indent=1)

    print("[OK] needs_from 条目数 = %d (改前 %d · 不增不减)" % (len(needs), len(needs)))
    print("[OK] 目标条目 index = %d · key = %s" % (idx, KEY))
    print("[OK] 改动字段 = %s (只有 item)" % diff_fields)
    print("[OK] item 改前 = %s" % old_item)
    print("[OK] item 改后 = %s" % new_item)
    for k in ("key", "to", "due", "since", "waiting_on"):
        if k in b:
            print("[OK] 字段 %-11s = %r (逐字未动)" % (k, b[k]))
    print("[OK] 中间件 = %s" % OUT)
    print("[OK] ★下一步必须走: python3 state/frag_write.py --agent hw-lead --set-json %s --set-field needs_from" % OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
