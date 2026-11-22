#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""main 把 ISS-327 交回的 4 条 need 逐条拍板并落进【main 自己的分片】(pm.yaml)

★**为什么现在落 (★改在产生点★)**: ★**ISS-327 交卷页 B5-1 明写「这 3 条 need 只交 need + 建议默认值 + 不拍的后果·不代拍」⇒ 拍板权在 main ⇒
★★**但 19:1x 那轮 round log 只把裁决写进了日志, 没进台账** ⇒ ★**⇒ 合并器/巡检/老板清单都读不到这条裁决 ⇒ 会重复问一遍** ★
⇒ 本脚本补记 4 条 answer (★第 4 条 = cont2 那条 C1/C7/C8/C13 洗白面·★前 3 条 = 15:35 那轮已拍但没落★)

★**纪律**: 只写 main 自己的分片 (pm.yaml) · 走 `state/frag_write.py` 原子写 · 零写板 · 零落表 · 零改闸 · 零外发 · 不替老板拍板
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from frag_write import update_fragment  # noqa: E402

import yaml  # noqa: E402

ANSWERS = [
    {
        "key": "iss327_decide_registry_rebuild_trigger",
        "to": "sw-lead",
        "value": (
            "★★【main 裁 (2026-11-18 19:2x · ★机制地界裁决 · 不占老板拍板面★)】★★ "
            "★**采纳甲 (你给的建议默认值)**: ★**「--freeze-registry」的触发条件 = 【盘面改过位号】, 不是【闸红了就重建】** ★ "
            "★**落地方式 = 固化进「板那一趟」的改名固定清单 (它已经是第 1 件 ⇒ 零新增流程) + 重建前的登记义务挂在落表单号上 (★复用 ISS-312 既有口径: ★登记文件名 + 新 md5 + 条数★·不新建流程) ★ "
            "★**你的实测就是裁决依据**: ① 对第 8 道闸, 重建【既非必要也非充分】 (文档同批改名 ⇒ 旧注册表本就 rc=0 / OK 78 / DRIFT 0 / MISSING 3; 文档不同步时重建 ⇒ 58 条漂移/假红被洗成 56 条真隐患/真红 ⇒ 一样红而且更凶) "
            "② 对另外 9 道, 重建【一件都不影响】 (它们不读注册表) ③ 改名后真正还红的 7 道【没有一道】是注册表能修的 ⇒ ⇒ **拿它当清红手段 = 把真隐患基线污染** ⇒ "
            "★**次序写死 (★你实测的那条真陷阱★)**: ★**重建必须晚于 SW 文档同批改名** ⇒ ★**「先重建、后同步文档」这个次序会把假红洗成真红 ⇒ 明令不许** ★ "
            "★**落点 (main 自己去落, 不派给 agent)**: `HW/PCB/ONETRIP_S1_THREE_SIDE_RENAME_LIST.md` (ISS-317 交卷的改名固定清单) 的「依赖顺序」段 ⇒ ★**归 main 的机制地界, 不动 agent 的文件** ★ "
            "★★**证据等级**: 重建的必要性/充分性/洗白面 = ★**[实测]** (你两套独立沙盒逐字相同) · 假红→真红次序风险 = ★**[实测]** (58→56) · 「假红与真红的处置完全相反」= ★**[实测]** ★"
        ),
        "ref": ("HANDOFF/2026-11-18_sw-lead_ISS327_改名后SW闸链复活验证.md §B0-1/§B1-3/§B4-1/§B5-1 · "
                "SW/ONETRIP_SW_POSTRENAME_GATE_SOP.md §4 (回滚三档) · logs/iss327/02_postrename_gate_table.md"),
    },
    {
        "key": "iss327_decide_missing_baseline_mechanism",
        "to": "sw-lead",
        "value": (
            "★★【main 裁 (2026-11-18 19:2x · ★机制地界裁决 · 不占老板拍板面★)】★★ "
            "★**采纳甲 (你给的建议默认值)**: ★**`DESIGNATOR_MISSING` 的上限保持魔法数 3, 这一轮一个字都不改** ★ "
            "★**依据 (★你的实测★)**: ★**文档同批改名 ⇒ 基线稳在 3 ⇒ 一字不用改** ⇒ ★**反过来, 文档不同步时 MISSING 漂到 5, 重建次序错时漂到 56 ⇒ "
            "⇒ 「魔法数过期」这个风险是真的, 但它的触发条件是【流程被破坏】, 不是【基线自然漂移】⇒ ⇒ 这一轮转台账式 (ISS-275/284 同款链头式) 是【为还没发生的事付今天的复杂度】⇒ 不转 ★ "
            "★**裁决附一条硬边界 (★防「魔法数被慢慢挪大」★)**: ★**上限只许收紧不许放宽 (★同 SW 那道闸 BASELINE_COUNT 的规矩★) ⇒ "
            "⇒ 真出第 4 条真隐患时, 走【带单号的登记台账】(登记单号 + 文件名 + 新 md5 + 条数), 不许直接把 3 改成 4 ★ "
            "★**复核触发条件 (★写清楚, 省得下次又来问★)**: ★**只要还满足「文档同批改名 ⇒ MISSING 稳在 3」, 这条裁决一直有效; 一旦实测出现第 4 条真隐患 ⇒ 立即重开本裁决** ★ "
            "★★**证据等级**: 基线稳在 3 / 漂到 5 / 漂到 56 = ★**[实测]** (ISS-327 沙盒读数) · 「转台账式是提前付复杂度」= ★**[推算]** (main 的口径判断·非实测) ★"
        ),
        "ref": ("HANDOFF/2026-11-18_sw-lead_ISS327_改名后SW闸链复活验证.md §B5-1 第 2 条 · "
                "logs/iss327/02_postrename_gate_table.md §2/§3 · SW/tools/check_sw_ref_reachability.py (BASELINE_COUNT / BASELINE_TOKENS)"),
    },
    {
        "key": "iss327_decide_drift_class_semantics",
        "to": "sw-lead",
        "value": (
            "★★【main 裁 (2026-11-18 19:2x · ★机制地界裁决 · 不占老板拍板面★)】★★ "
            "★**采纳甲 (你给的建议默认值)**: ★**`DESIGNATOR_DRIFT` 保留, 但语义写死成「文档与盘面不同步告警」+ 把「重建次序」写进护栏** ★ "
            "★**不退役 (★理由: 退役 = 改闸 = 受保护资产, 且退役会把这道闸唯一能告诉你「文档与盘面不同步」的那条信号删掉★) ★ "
            "★**语义写死的三条 (★照抄即可, 不许自己发挥★)**: "
            "① ★**`DESIGNATOR_DRIFT` = 【文档里出现的老位号, 盘面已不存在】⇒ 它的唯一含义是「文档与盘面不同步」⇒ 不是「拼写错」★ "
            "② ★**它是【告警】不是【放行理由】**: ★**判绿之前必须先确认「同批改名已完成」, 否则漂移数大 = 真的不同步, 不许拿它当免责★ ★ "
            "③ ★**与 `DESIGNATOR_MISSING` 的处置完全相反**: ★**DRIFT 大 ⇒ 先查次序/同步; MISSING 大 ⇒ 先查真隐患基线** ⇒ ★**判错一次就把假红当真红** ★ "
            "★**护栏内容 (★写进 SOP, 零改闸★)**: ★**「重建注册表」必须在「SW 文档同批改名」之后 ⇒ 先重建后同步 = 把假红洗成真红** ★ "
            "★★**证据等级**: 「改名后 DRIFT 是死代码 (老名一个都不在文档里)」= ★**[实测]** · 「漂移 58 vs 真隐患 56 两种红的处置完全相反」= ★**[实测]** · 「退役会删掉唯一的不同步信号」= ★**[推算]** (main 的口径判断) ★"
        ),
        "ref": ("HANDOFF/2026-11-18_sw-lead_ISS327_改名后SW闸链复活验证.md §B5-1 第 3 条 · "
                "SW/ONETRIP_SW_POSTRENAME_GATE_SOP.md §2/§3 · SW/tools/check_sw_ref_reachability.py (classify / C14 分支)"),
    },
    {
        "key": "iss327_report_c1_c7_c8_c13_launder_faces",
        "to": "sw-lead",
        "value": (
            "★★【main 裁 (2026-11-18 19:2x · ★机制地界裁决 · 不占老板拍板面★)】★★ "
            "★**要收紧 + 收紧方向 = 「真隐患 token 必须在 `BASELINE_TOKENS` 里登记过才算白名单」** ★ "
            "★**为什么必须收紧 (★你的实测本身就是判据★)**: ★**四条洗白面 (RT-5 live 位号名 / RT-6 含小写 / RT-7 SW_ 前缀 / RT-8 以 _ 结尾) 全都在【重建注册表之前就已经绿】⇒ 与 freeze 无关 ⇒ ⇒ "
            "★**这道闸对「真隐患」只有形状检查、没有语义检查 ⇒ 永远只能抓「拼写错」抓不到「指错对象」⇒ ⇒ 「SW 侧引用的位号全部可达」这句话今天是半假的** ★ "
            "★**但改真件闸不是你的活 (★地界★)**: ★**真件 `SW/tools/check_sw_ref_reachability.py` 一个字节都不许你改 · `state/gate_check.py` 也不许你碰** ⇒ "
            "⇒ ★**main 已开 ISS-332 (owner=sw-lead, status=fixing, 19:2x 派出) ⇒ 你交的是: ① 沙盒里把 4 条洗白面 + 3 条「真隐患变形状」对照复现出来 ② 收紧版新文件 `SW/tools/check_sw_ref_reachability_v2.py` + `--selftest` ③ 切闸/挂闸写法 ⇒ ★**切不切由 main 拍** ★ "
            "★**顺带带进去的一条 (★你 11-18 16:3x 自踩的坑·已经写进 ISS-332 的边界★)**: ★**方案类文档写进 `SW/` 会把闸带红 ⇒ 收紧版的交卷文档一律写进 `logs/iss332/`** ★ "
            "★★**证据等级**: 4 条洗白面 = ★**[实测]** (ISS-327 cont2) · 「与 freeze 无关」= ★**[实测]** · 「判据只有形状检查没有语义检查」= ★**[推算]** (main 的口径判断) ★"
        ),
        "ref": ("HANDOFF/2026-11-18_sw-lead_ISS327_改名后SW闸链复活验证.md §B5-1 第 4 条 (cont2) · "
                "logs/iss327/30_rev_RT9_launder_path.txt · logs/iss327/32_launder_run.log · "
                "state/dispatch_briefs/ISS-332_sw_ref_reach_launder_reverse_cases.md"),
    },
]


def main() -> int:
    pm = yaml.safe_load(open(os.path.join(HERE, "fragments", "pm.yaml"), encoding="utf-8")) or {}
    have = {a.get("key") for a in (pm.get("answers") or [])}
    todo = [a for a in ANSWERS if a["key"] not in have]
    if not todo:
        print("★ 4 条 answer 已在 pm.yaml (⇒ 不重复写)")
        return 0

    def mutate(d):
        ans = d.setdefault("answers", [])
        for a in todo:
            ans.append({"key": a["key"], "to": a["to"], "value": a["value"], "ref": a["ref"]})

    update_fragment("main", mutate)

    pm2 = yaml.safe_load(open(os.path.join(HERE, "fragments", "pm.yaml"), encoding="utf-8")) or {}
    ok = 0
    for a in ANSWERS:
        hit = [x for x in (pm2.get("answers") or []) if x.get("key") == a["key"]]
        if len(hit) == 1 and hit[0].get("to") == "sw-lead":
            ok += 1
            print("✅ %-52s to=%s 字数=%d" % (a["key"], hit[0].get("to"), len(hit[0].get("value", ""))))
        else:
            print("❌ %-52s 命中=%d" % (a["key"], len(hit)))
    print("→ 落记 %d / %d 条" % (ok, len(ANSWERS)))
    return 0 if ok == len(ANSWERS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
