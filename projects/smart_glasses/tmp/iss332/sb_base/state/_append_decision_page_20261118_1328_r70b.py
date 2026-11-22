#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
r70b (2026-11-18 13:28 · cron 775d9893 · 项目总工 moli)
================================================================================
DECISION_INDEX_2026-11-18.md 的【追加式订正 §H-4】

★**追加式 —— §A~§H-3 的老字一个字未删未改** ★
★**只补一条**: §H-3 里 gate_check 的 Q1 读数订正
                (★18/18 → 15/18 ⇒ **不是本 job 的动作, 是在飞的 hw-lead ISS-325 交卷页写到一半★)

★**纪律**: 零外发 · 零写板 · 零落表 · 不改 PROJECT_TRACKER.md §0 · 不写别的 agent 的分片 · 不替老板拍板
"""

import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
PAGE = os.path.join(PROJ, "DECISION_INDEX_2026-11-18.md")

TS = "20261118_1328"
BAK = PAGE + ".bak_" + TS + "_r70b"

SECTION = r"""

### ★H-4 · ★§H-3 表里 gate_check 的 Q1 读数【即时订正】★★ ★**(★13:2x 实跑·本 job 追加决策页之后★)** ★★

★**§H-3 记的是 13:1x 的读数 (Q1 = 18/18)⇒ ★**13:2x 复跑变成 15/18** ★ ⇒ ★**先归因, 不许把瞬时读数当成回退报给老板** ★

| 项 | 读数 |
|---|---|
| 现象 | ★**Q1 交付齐备率 18/18 → 15/18** ★ —— ★**只有 hw-lead 一家掉: `3/6 缺 [B2, B4, B5]`** ★ (★sw-lead 6/6 缺无 · mech-lead 6/6 缺无★) |
| ★**归因 (★本机实读·不是推测★)** ★ | ★**hw-lead 的交接单指针已切到 `HANDOFF/2026-11-18_hw-lead_ISS325_左上布局沙盒预演.md` (★mtime **2026-11-18 13:24** · 9135 B·此刻只有 B0 / B3 / B6 三段, B1/B2/B4/B5 还没写★)** ★ ⇒ ★**gate_check 读到的是【写到一半的交卷页】⇒ 缺 B2/B4/B5 是【还没写】, 不是【写错】或【漏交】** ★ |
| ★**在飞证据 (★进程实读★)** ★ | ★**ISS-325 的 4 条沙盒臂仍在跑**: `state/iss325_s8_leftupper_arms.sh` + `state/iss325_s8_control_v76mz_arms.sh` · ★**4 个 `gen_pcb_netlist_board.py` 进程 (25:57 / 20:21 已跑) ⇒ 重 A* 路由搜索中, 没卡死** ★ · ★**⇒ 交卷页自然还没写完** ★ |
| ★**结论 (★必须写清·不许含糊★)** ★ | ★**① 这不是本 job 的动作造成的** ★ (★本 job 本轮只写: `DECISION_INDEX_2026-11-18.md` (追加 §H) + `PROGRESS_SNAPSHOT.md` + 本脚本 + 1 份备份 · ★**零写板 · 零落表 · 零改任何 agent 的分片**★) ★ **② 这是并发在飞 agent 的【中间态】, 不是质量回退** ★ **③ 它会自己转绿**: ★**hw-lead 交卷页写完 B1/B2/B4/B5 ⇒ Q1 回 18/18** ★ ⇒ ★**下一次跑本 job 或兄弟 job 时应复核这一项是否已回绿** ★ |
| 顺带一条口径 | ★**缺口清单条数 3 → 6**: ★**新增的 3 条全是 `hw-lead: 交接单缺 [B2]/[B4]/[B5]` (即上一行同一件事的机器化表述) ⇒ 与上面同一根因, 不另算问题** ★ |

★**⇒ 对老板的意义: 无。** ★**§A / §H-1 的 6 个待拍字母一条没变, 一条没多一条没少。**
"""


def main() -> int:
    if not os.path.exists(PAGE):
        print("★page missing: %s" % PAGE)
        return 2
    old = open(PAGE, encoding="utf-8").read()
    if "### ★H-4 ·" in old:
        print("★已存在 §H-4 ⇒ 不重复追加")
        return 0
    shutil.copy2(PAGE, BAK)
    with open(PAGE, "a", encoding="utf-8") as f:
        f.write(SECTION)
    new = open(PAGE, encoding="utf-8").read()
    assert new.startswith(old), "★追加式违规: 老字被改动"
    print("✅ DECISION_INDEX_2026-11-18.md 已追加 §H-4 (r70b)")
    print("   老字节 = %d → 新字节 = %d (追加 %d)" % (len(old), len(new), len(new) - len(old)))
    print("   备份 = %s" % os.path.basename(BAK))
    print("   追加式自证: 老字逐字前缀未变 = True")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
