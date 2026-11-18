#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-107 (owner=mech-lead) —— 把分片 interface_claims.pcb_mounting 旧取值改成 PIN-SET-2。

★写分片铁律: 必须走 state/frag_write.py 的原子写 (tmp + os.replace), 禁止 open(p,"w")。
   本脚本 **不自己写文件**, 只调 frag_write.update_fragment()。

【为什么值写 "2x⌀2.0H7+2x⌀1.4" 而不是直接抄 hw-lead 的 "PIN-SET-2:2x⌀2.0H7+2x⌀1.4"】
  state/merge.py 的冲突判定比的是 **canon** (规范值), 而 canon_of() 只做
  「去括号注释 / 去空白分隔符 / lower / ×→x」四件事 —— **它不去 "PIN-SET-2:" 这个方案名前缀**。
  实测 (merge.py canon_of):
      'PIN-SET-2:2x⌀2.0H7+2x⌀1.4' → 'pin-set-2:2x⌀2.0h7+2x⌀1.4'
      '2x⌀2.0H7+2x⌀1.4'             → '2x⌀2.0h7+2x⌀1.4'      ← 两者不等 ⇒ 仍会判冲突
  所以要么把值抄成与 hw-lead 逐字节相同, 要么**显式给 canon 字段**。
  本项目已有先例: hw-lead 的 skeleton_extent 就是靠 `canon: 止于PCB段后缘` 与 mech 的值对齐的
  (state/fragments/hw.yaml:682)。⇒ 本脚本沿用同一机制:
      value = '2x⌀2.0H7+2x⌀1.4'      (内容口径 = PM 任务书写的那个串)
      canon = 'pin-set-2:2x⌀2.0h7+2x⌀1.4'   (与 hw-lead 的 canon_of 输出逐字节相等)
  这样两边 comparable canon 相等 ⇒ uniq=1 ⇒ **冲突消**。

用法: python3 MECH/_frag_update_iss107.py [--dry-run]
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(PROJ, "state"))

from frag_write import update_fragment, load_fragment  # noqa: E402

AGENT = "mech-lead"

NEW_VALUE = "2x⌀2.0H7+2x⌀1.4"
NEW_CANON = "pin-set-2:2x⌀2.0h7+2x⌀1.4"
NEW_NOTE = (
    "★PIN-SET-2 定版 (采纳 hw-lead ISS-049 定版, 结构侧独立复算 31 项 FAIL 0 / WARN 3): "
    "2x⌀2.0H7 定位销孔 + 2x⌀1.4 压紧孔 —— 板坐标 (原点左下角, X=板长 0→60 铰链端在 X=0, Y=板宽 0→15): "
    "P1(8.00,7.50) 配骨架压装 ⌀2.0 h6 圆销=全基准(X+Y+θz) / P2(52.00,7.50) 配 ⌀2.0 菱形销(对边1.94)=只定Y⇒消过定位 / "
    "S1(8.00,2.50) / S2(52.00,12.50) 为 ⌀1.4 过孔 (M1.2 螺钉径向间隙 0.10/边, 纯压紧零定位); "
    "老口径 2xM1.2+1x⌀2.0H7 @孔心到板边2.50 在 15mm 板下按最有利假设仍 3/3 孔压 SoC 逃线带 "
    "(M1.2 压 Y 0.50mm; ⌀2.0 压 2.00x2.00mm) ⇒ 加宽不解, 已机械判死作废; "
    "PIN-SET-2 4/4 孔与逃线带 X[20.20,31.80]xY[2.70,12.30] 的 2D 重叠 = 0.000mm²; "
    "定位重复性 ≤0.046mm (骨架铣削面≤5µm + H7销≤0.010), 打印件只让过不定位"
)
NEW_REF = "MECH/PCB_MOUNT_PIN_SET2.md"

# 老 answer 里那句 "我这边的值已按 ISS-105 定版保持 (2xM1.2 + 1x⌀2.0H7)" 已过期 → 追加更正, 不抹掉历史记录
ANSWER_KEY = "iss105_pcb_outline_sync_60x15"
ANSWER_TAIL = (
    " || ★2026-10-29 ISS-107 更正: 上句 '我这边的值已按 ISS-105 定版保持 (2xM1.2 + 1x⌀2.0H7)' "
    "**已作废** —— mech 侧的 pcb_mounting 已于 2026-10-29 改成 PIN-SET-2 = '2x⌀2.0H7+2x⌀1.4' "
    "(与 hw-lead ISS-049 定版一致, 合并器冲突已消)。老口径 2xM1.2+1x⌀2.0H7 @边距2.50 在 15mm 板下 "
    "3/3 孔压 SoC 逃线带 ⇒ 机械判死。"
)


def main() -> int:
    dry = "--dry-run" in sys.argv
    before = load_fragment(AGENT)

    old = None
    for c in before.get("interface_claims") or []:
        if c.get("key") == "pcb_mounting":
            old = dict(c)
    if old is None:
        print("❌ 分片里找不到 interface_claims.pcb_mounting, 中止")
        return 2
    print(f"[before] pcb_mounting = {old.get('value')!r} canon={old.get('canon')!r}")
    if dry:
        print("[dry-run] 未落盘")
        return 0

    hits = {}

    def mutate(d: dict) -> None:
        claims = d.get("interface_claims") or []
        for c in claims:
            if c.get("key") == "pcb_mounting":
                hits["claim"] = True
                c["value"] = NEW_VALUE
                c["canon"] = NEW_CANON
                c["note"] = NEW_NOTE
                c["ref"] = NEW_REF
        if not hits.get("claim"):
            raise SystemExit("❌ mutate 时找不到 pcb_mounting claim, 中止 (分片保持原样)")

        for a in d.get("answers") or []:
            if a.get("key") == ANSWER_KEY:
                hits["answer"] = True
                if ANSWER_TAIL.strip() not in (a.get("value") or ""):
                    a["value"] = (a.get("value") or "") + ANSWER_TAIL

    after = update_fragment(AGENT, mutate)
    print(f"[frag_write] ✅ {AGENT}.yaml 已原子更新 (claim={hits.get('claim')}, answer={hits.get('answer', False)})")
    for c in after.get("interface_claims") or []:
        if c.get("key") == "pcb_mounting":
            print(f"[after]  value = {c.get('value')!r}")
            print(f"[after]  canon = {c.get('canon')!r}")
            print(f"[after]  ref   = {c.get('ref')!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
