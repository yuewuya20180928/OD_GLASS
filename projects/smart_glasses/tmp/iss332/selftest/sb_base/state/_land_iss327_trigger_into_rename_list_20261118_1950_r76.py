#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""main 把 ISS-327 need#1 的裁决【真的落进它自己指定的落点】(改在产生点)

★**为什么现在落 (★不是「台账漂移」, 是「落点还没写」★)**: ★**ISS-327 交回的 4 条 need 由 main 在 19:2x 逐条拍板并落进了 `state/fragments/pm.yaml`** ★
⇒ ★**但那条 need 的 answer 里写着「落点 (main 自己去落, 不派给 agent): `HW/PCB/ONETRIP_S1_THREE_SIDE_RENAME_LIST.md` 的「依赖顺序」段」** ★
⇒ ★**⇒ 19:2x~19:4x 那一轮只把裁决写进了 pm.yaml + round log, 【落点本身一个字都还没写】** ⇒ ⇒ ★**下一轮读那份清单的人看不到「重建必须晚于 SW 文档同批改名」这条次序 ⇒ 那个次序就会再被踩一次** ★
⇒ 本脚本: ① 先确认落点文件已含 `BATCH-4` (main 19:5x 已用定点 edit 写进去) ② 把「已落盘」的事实【追加回那条 answer 自己的 value 里】(★改在产生点·不许只写日志★) ★

★**纪律**: 只写 main 自己的分片 (pm.yaml) · 走 `state/frag_write.py::update_fragment` 原子写 · 零写板 · 零落表 · 零改闸 · 零外发 · 不替老板拍板
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)   # ★项目根 (state/ 的上一级·★别把 state/ 当根★)
sys.path.insert(0, HERE)

from frag_write import update_fragment  # noqa: E402

import yaml  # noqa: E402

KEY = "iss327_decide_registry_rebuild_trigger"
RENAME_LIST = os.path.join(ROOT, "HW", "PCB", "ONETRIP_S1_THREE_SIDE_RENAME_LIST.md")

LANDED_NOTE = (
    " ★ ★**【已落盘 · main 2026-11-18 19:5x 本机落盘 (★不是只写日志★)】**: ★**本裁决的「落点」现在真的写进 `HW/PCB/ONETRIP_S1_THREE_SIDE_RENAME_LIST.md` §1-3「依赖顺序」段 ⇒ 新增 `BATCH-4` (★触发条件 = 位号宇宙改过·不是「闸红了就重建」+ 「重建必须晚于 SW 文档同批改名」的次序写死 + `BASELINE_COUNT=3` 硬边界 + `DESIGNATOR_DRIFT` 语义 + 登记义务挂落表单号·★ISS-312 既有口径★)** ★ "
    "⇒ ★**落盘后本机复跑 `python3 SW/tools/check_sw_ref_reachability.py` rc=0 仍绿 (★改前 rc=0 / 改后 rc=0·逐字一致★ ⇒ 该文件在 SW 位号可达性闸的 `AUX_MD_DIRS`(HW) 扫描面内·所以改它必须复跑这道闸·★本轮已复跑并留证★)** ★ "
    "⇒ ★**零写板双证不变**: 板 md5 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413` 逐字节未动 ★"
)


def main() -> int:
    # ---- ① 先自证落点文件真的有 BATCH-4 (没有就 abort ·不许记账说已落) ----
    txt = open(RENAME_LIST, encoding="utf-8").read()
    if "BATCH-4" not in txt:
        print("❌ 落点文件里没有 BATCH-4 ⇒ 本脚本 abort (不许记账说已落)")
        return 1
    if "先重建注册表、后同步文档" not in txt:
        print("❌ 落点文件里没有次序写死那一行 ⇒ abort")
        return 1
    print("✅ 落点自证: BATCH-4 在 (★次序写死那一行也在★)")

    # ---- ② 把「已落盘」追加回那条 answer 自己的 value (改在产生点) ----
    pm = yaml.safe_load(open(os.path.join(HERE, "fragments", "pm.yaml"), encoding="utf-8")) or {}
    hits = [a for a in (pm.get("answers") or []) if a.get("key") == KEY]
    if len(hits) != 1:
        print("❌ pm.yaml 里 %s 命中 %d 条 (≠1) ⇒ abort" % (KEY, len(hits)))
        return 1
    if "【已落盘 · main 2026-11-18 19:5x" in (hits[0].get("value") or ""):
        print("★ 落记已在 (⇒ 不重复写)")
        return 0

    def mutate(d):
        for a in (d.get("answers") or []):
            if a.get("key") == KEY:
                a["value"] = (a.get("value") or "") + LANDED_NOTE

    update_fragment("main", mutate)

    pm2 = yaml.safe_load(open(os.path.join(HERE, "fragments", "pm.yaml"), encoding="utf-8")) or {}
    hit2 = [a for a in (pm2.get("answers") or []) if a.get("key") == KEY]
    ok = len(hit2) == 1 and "【已落盘 · main 2026-11-18 19:5x" in (hit2[0].get("value") or "")
    print(("✅" if ok else "❌") + " 落记复检: 命中=%d · 追加成功=%s" % (len(hit2), ok))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
