#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PM 裁决落盘 (ISS-047) —— 把项目总工 2026-11-02 的「俯角余量口径」裁决写成 pm 分片的一条 answer
================================================================================
★踩坑记录 (2026-11-02 18:4x, 本文件就是这么修的):
  `frag_write.py --add-answer` 的**每个 flag 是一次独立追加**, 不是同一条的多个字段。
  我第一次写成 `--add-answer key=K --add-answer to=mech-lead --add-answer value="..." --add-answer ref="..."`
  ⇒ 结果追加了 **4 条残缺条目** (key 有但 to/value/ref 全空, 或 key 为 null)。
  ⇒ 合并器立刻报「answers 条目缺字段 ['key'] → 已忽略」+ 快照不完整 —— **这正是它该做的**。
  ★正确用法: `--add-answer 'key=K to=mech-lead value="..." ref="..."'` —— **一个 flag, 内部空格分隔**。
  本脚本用 `--set answers=<JSON 数组>` 整段替换, 先剔掉残缺条目再补完整条目 ⇒ 幂等, 可重跑。
"""
from __future__ import annotations

import json
import subprocess
import sys

import yaml

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
FRAG = f"{PROJ}/state/fragments/pm.yaml"

KEY = "iss047_margin_criterion_decision"
VALUE = (
    "判据B' (有效余量>=4deg, 即扣掉边框遮挡角1.91deg) => 俯角上限<=25.89deg, 设计点25deg; "
    "h_max(d=30/32/35)=13.99/14.92/16.32mm"
)
REF = (
    "PM 裁决 2026-11-02 18:4x (项目总工): "
    "①理由=遮挡是实物必然(凹进0也要占窗口座沉孔0.35mm), 名义余量留不住; "
    "②与 HW/LENS_SELECTION.md B6.3「推荐按<=25deg设计」一致; "
    "③机械复算 MECH/iss047_fov_table.py rc=0 FAIL0 WARN0 (含硬上限29.89deg/h_max16.99mm 判据B'分支) "
    "+ MECH/iss047_doc_check.py 220/220 一致; "
    "④★口径 = 名义余量4deg(B) / 有效余量4deg(B') / 名义余量10deg(C) 三选一, 统一按 B' 写进 MECH_BUDGET; "
    "⑤★结构基线不变(俯角25deg, h_max 13.99/14.92/16.32mm) —— 换 sensor 不推翻结构, 只多给 2.27deg 造型自由度"
)


def main() -> int:
    with open(FRAG, encoding="utf-8") as f:
        d = yaml.safe_load(f) or {}
    answers = d.get("answers") or []

    # 剔掉残缺条目 (key 缺 / 空) 与本键的旧版本 (保证幂等)
    kept = [a for a in answers if a.get("key") and a.get("key") != KEY]
    kept.append({"key": KEY, "to": "mech-lead", "value": VALUE, "ref": REF})
    removed = len(answers) - len(kept) + 1

    cmd = [
        sys.executable, "state/frag_write.py",
        "--agent", "main",
        "--set", "answers=" + json.dumps(kept, ensure_ascii=False),
    ]
    r = subprocess.run(cmd, cwd=PROJ, capture_output=True, text=True)
    sys.stdout.write(r.stdout)
    sys.stderr.write(r.stderr)
    if r.returncode != 0:
        print(f"❌ frag_write rc={r.returncode}", file=sys.stderr)
        return r.returncode
    print(f"✅ pm.yaml answers 整段替换完成: 剔残缺 {removed} 条, 写入本键 1 条 (共 {len(kept)} 条)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
