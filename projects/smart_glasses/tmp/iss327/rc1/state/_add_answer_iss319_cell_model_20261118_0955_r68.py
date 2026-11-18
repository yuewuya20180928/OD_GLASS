#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
r68 (2026-11-18 09:5x · cron 775d9893 · 项目总工 moli)
================================================================================
补记 main 已裁但没落台账的一条 answer: `iss319_cell_model_rename_scope`

★**为什么补 (★台账漂移·改在产生点★)**:
  ISS-320 的任务书 §② 白纸黑字写着「★**main 已拍板 (需求 `iss319_cell_model_rename_scope` ⇒ 现在就做**★】」
  ⇒ ★**但 `state/fragments/pm.yaml` 的 `answers` 里查无此 key** ⇒ ★**决策在任务书里, 不在台账里**
  ⇒ ★**⇒ 后果: 下一次合并器 / 巡检 / 老板清单都读不到这条裁决 ⇒ 会重复问一遍** ★

★**纪律**: 零写板 · 零落表 · 零重生成 · 零改闸 · 零外发 · 只写 main 自己的分片 (pm.yaml) · 不替老板拍采购型号
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from frag_write import update_fragment  # noqa: E402

KEY = "iss319_cell_model_rename_scope"

VALUE = (
    "★★【main 裁 (2026-11-18 09:5x · ★口径裁决 · 不占老板拍板面 · ★这是 main 级范围裁, 不是老板采购拍板★)】★★ "
    "★**范围 = 按 ISS-319 实测的 47 行 / 22 个活文件全表落字, 但严格分三类处理**: "
    "① ★**可改行 36 行** (★口径行 26 行 + 脚本行 10 行) ⇒ ★**改** ★ "
    "(★脚本行只许改型号名那 5 个字, 逻辑常量 4.60 / 23.50 / 40.50 一处都不许动★); "
    "② ★**留证/对照行 11 行** ⇒ ★**一行都不许动** "
    "(★两型号并置 ⇒ 语义上是证据; 改了就毁掉「官网实读到底哪个型号是多厚」这个证据★); "
    "③ ★**HW 域那 3 行** (★`HW/POWER_BUDGET_V3.md` L27/L259 + `HW/NETLIST_SELF_CONSISTENCY_SPEC.md` L1046★) "
    "⇒ ★**main 自己改** (★本机实读: 这两个文件没有被任何 md5 闸钉住 ⇒ 可安全改★) ★ "
    "⇒ ★**本裁决只定【范围与边界】, 不定【采购型号】**: 采购是老板的桶 (★D-2-9, 见 `iss316_mech_diff_ownership`★) "
    "⇒ ★**main 的判据只有一条: 文档口径必须与官网实读一致** "
    "(★Renata `ICP422339PR` = 340 mAh / 4.6 mm / 23.5×40.5 · `ICP582035PR-01` = 340 mAh / 6.4 mm / 20.5×37·[官网]★) "
    "⇒ ★**这跟买哪颗是两件事** ★ ⇒ "
    "★**打印包 (★`gen_print_pack_revb.py` / `MEASURE_CHECKLIST.md`★) ★**不跟板那一趟同批重出** ★ "
    "(★实测更正: 该脚本只写 4 个 .stl ⇒ 「重出时会带上新型号名」只对 stdout 成立, 产物里不带型号名 ⇒ 重出对型号订正无收益 ⇒ 不排期★) ⇒ "
    "★**判定「改对了」的机器判据 = 替换后基线扫描命中行数 = 11 (只剩留证行) + 11 行留证行逐条与改前逐字节相同 + 每个改后文件 == 「改前内容做一次全量替换」的期望版本 (逐字节) "
    "⇒ ★**36 行可改行的数字指纹改前改后逐位相同** ⇒ 「几何与重量结论零变化」是机器判的, 不是人说的** ★ ⇒ "
    "★**另注**: `MECH/ONETRIP_MECH_DIFF_OWNERSHIP.md` 与本单自己的交卷页必须排除在扫描之外 "
    "(★ISS-319 已实测过这个坑: 不排除命中数会从 11 变成 119★) ★ "
    "★★**证据等级**: 型号规格 = ★**[官网]** renata.com (★ISS-313 已核 · 零外发★) · 影响面 47 行/22 文件 = ★**[实测]** (ISS-319 机器生成) · 范围划分 = ★**[实测]** (36 行数字指纹逐位相同) ★ "
    "★★**零写板 · 零落表 · 零重生成 · 零改闸 · 零外发 · 不替老板拍采购型号** ★"
)

REF = (
    "HANDOFF/2026-11-18_mech-lead_ISS319_差集归属与电芯订正影响面.md §2-2 "
    "+ MECH/ONETRIP_CELL_MODEL_RENAME_APPLY.md "
    "+ state/dispatch_briefs/ISS-320_mech_cell_model_rename_apply.md §② "
    "+ DECISION_INDEX_2026-11-18.md §F-2"
)


def main() -> int:
    # 先查: 别重复写
    import yaml
    pm = yaml.safe_load(open(os.path.join(HERE, "fragments", "pm.yaml"), encoding="utf-8")) or {}
    for a in (pm.get("answers") or []):
        if a.get("key") == KEY:
            print("★已存在 answer (%s) ⇒ 不重复写" % KEY)
            return 0

    def mutate(d):
        ans = d.setdefault("answers", [])
        ans.append({"key": KEY, "to": "mech-lead", "value": VALUE, "ref": REF})

    update_fragment("main", mutate)

    # 自证
    pm2 = yaml.safe_load(open(os.path.join(HERE, "fragments", "pm.yaml"), encoding="utf-8")) or {}
    hit = [a for a in (pm2.get("answers") or []) if a.get("key") == KEY]
    print("✅ pm.yaml 已补记 answer: %s" % KEY)
    print("   命中条数 = %d | to = %s | value 字数 = %d" % (len(hit), hit[0].get("to"), len(hit[0].get("value", ""))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
