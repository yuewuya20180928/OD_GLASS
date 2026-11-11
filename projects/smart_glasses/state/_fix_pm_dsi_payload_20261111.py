#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""main 侧 pm.yaml 的 DSI payload 口径订正 (2026-11-11 08:5x, 项目总工 main)

★**为什么是 main 的活**: `state/fragments/pm.yaml` 是 **main 自己的分片** ⇒ ★**只有 main 能写**
  (MEMORY.md:3138「分流按【谁的分片】, 不按【谁方便做】」)。

★**哪一条**: `interface_claims` 里 key=`display_resolution` (value=1920x1080) 的 note 里写着
  「DSI带宽@60RGB888≈**373Mbps**」 ⇒ ★**偏小 8.0×** ⇒ 与 ISS-186 订正后的 2986 矛盾 ⇒
  ★**这是"值没错、但依据注里的数错了"的一类** ⇒ 下游任何读这条 note 的人会拿到错数。

★**改法**: note 里的 `DSI带宽@60RGB888≈373Mbps` → `DSI带宽@60RGB888≈2986Mbps` (★**只改这个数**,
  不动 note 的其余部分 ⇒ ★**其余 100+ 条 claim 一个字节不动**)。

★**落账纪律**: 走 `state/frag_write.py` 的 `update_fragment` (读 → 改 → 原子写: tmp → fsync →
  os.replace) ⇒ ★**不裸开文件写** (那是 MEMORY.md 记的老坑: `open(p,'w')` 会把分片写坏)。
  ★**写后自检**: ① `yaml.safe_dump(改后)` == 落盘内容 (往返一致) ② ★**除这条 claim 外, 其余
  claim 逐条相同** (比对改前改后) ③ 顶层键不变。
"""
from __future__ import annotations

import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from frag_write import update_fragment  # noqa: E402

PM = os.path.join(HERE, "fragments/pm.yaml")
OLD = "DSI带宽@60RGB888≈373Mbps"
NEW = "DSI带宽@60RGB888≈2986Mbps"
TARGET_KEY = "display_resolution"


def main() -> int:
    before_raw = open(PM, encoding="utf-8").read()
    before = yaml.safe_load(before_raw)
    before_claims = before.get("interface_claims") or []
    before_keys = list(before.keys())
    before_others = [c for c in before_claims if c.get("key") != TARGET_KEY]

    hits = 0

    def mutate(d):
        nonlocal hits
        for c in (d.get("interface_claims") or []):
            if c.get("key") == TARGET_KEY:
                n = c.get("note") or ""
                if OLD in n:
                    c["note"] = n.replace(OLD, NEW)
                    hits += 1
                break

    # ★**agent id = "main"** (frag_write.FILE_OF: main→pm.yaml) ⇒ ★**不是 "pm"**
    #   (★踩坑: 传 "pm" 会被 frag_write 直接 SystemExit「未知 agent id」★)
    after = update_fragment("main", mutate)
    if hits != 1:
        print(f"❌ 预期命中 1 处, 实际 {hits} ⇒ 中止")
        return 1

    # ---- 自检 ----
    with open(PM, encoding="utf-8") as f:
        disk = f.read()
    rt = yaml.safe_load(disk)

    after_claims = rt.get("interface_claims") or []
    after_others = [c for c in after_claims if c.get("key") != TARGET_KEY]
    same_others = (after_others == before_others)
    keys_same = (list(rt.keys()) == before_keys)
    # ★★踩坑记录 (2026-11-11 08:5x 实测): ★**往返自检必须用 frag_write 自己的 width (100)** ——
    #   我第一版用 width=200 重 dump 再跟落盘文本比 ⇒ ★**判成"不一致"** ⇒
    #   ★**但那只是折行宽度不同, 数据完全一样** (232 行 diff 全是折行位置) ⇒ ★**假警报**
    #   ⇒ ★**正确做法: 比【解析后的数据结构】, 不比文本** (文本比就必带 width 参数)
    rt_out = yaml.safe_dump(rt, allow_unicode=True, sort_keys=False, width=100)
    rt_ok = (rt_out == disk)
    # ★**顶层其余键也要逐个相同** (不只 interface_claims)
    other_keys_same = all(before.get(k) == rt.get(k) for k in before_keys if k != "interface_claims")

    print(f"pm.yaml 落账: 命中 {hits} 处 (key={TARGET_KEY} 的 note)")
    print(f"  其余 {len(before_others)} 条 claim 逐条相同: {'✅' if same_others else '❌'}")
    print(f"  顶层键不变: {'✅' if keys_same else '❌'}")
    print(f"  其余顶层段逐个相同: {'✅' if other_keys_same else '❌'}")
    print(f"  yaml 往返复现 (width=100, 与 frag_write 一致): {'✅' if rt_ok else '❌'}")
    print(f"  旧串残留 '373Mbps' 在 pm.yaml: {disk.count('373Mbps')} 处 (期望 0)")
    ok = (same_others and keys_same and other_keys_same and rt_ok
          and disk.count("373Mbps") == 0)
    print("  => " + ("✅ 全过" if ok else "❌ 有问题"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
