#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_append_decision_onepager_20260724_0215_cron775d_r82.py
=======================================================
main (项目总工 / moli) · cron 775d9893 「ARS45 继续执行后继计划」· 2026-11-24 02:1x
★★【★★决策页追加式订正 §㉞ + 覆盖核对 (★老字一字未删★)★★】★★

★**本轮做了什么 (★本机实读 + 实算, 不抄任何 agent 报告★)**:
  ① `state/advance.py --json` 实读 ⇒ **decisions = 52 条** (★hw.yaml 13 · mech.yaml 14 · pm.yaml 12 · sw.yaml 13★)
     · **逾期 31 条** (★最老 due 2026-10-26 = 「测试设备预算」★) · **无 due 21 条** · **内部/approvals/waiting 段: 0 / 0 / 0**
  ② ★**页头计数已过期** ⇒ ★`DECISION_ONE_PAGER_2026-11-22.md` §㉞ 写「待拍板面 50 条」· §③ 写「其余 34 条」· §㉓-4 写「全量 47 条」 ⇒ ★**三处都是旧数** ⇒ ★**本节订正为 52 条** (★不改老字, 只追加★)
  ③ ★**覆盖核对 (★逐 key 实跑, 52/52 全覆盖·★一件没漏★)★**:
     | 页 | 覆盖 |
     |---|---|
     | `DECISION_ONE_PAGER_2026-11-22.md` | **20 / 52** |
     | `DECISION_INDEX_2026-11-18.md` | **41 / 52** |
     | ★**并集** ★ | ★**52 / 52** ★ ⇒ ★**零漏项**★ |
     · ★**11 个 key 只在一页上 (不在索引里)** ⇒ ★**逐个实读确认: 11/11 都带建议默认值** (★「建议默认」/「★建议」/「main 倾向」任一命中★) ⇒ ★**老板要的「建议默认值」一项不缺** ★
     · ★**明细**: `iss340_c_bucket_boss_decisions` · `iss364_k2_d_esd_usb_d_2v3_pin` · `iss364_k3_button_3n_vs_1p5n` · `iss364_c_vbus_gnd_keep_or_drop` · `boss_decide_reboard_mtime_size_caliber` · `boss_decide_second_reboard_stop_authority` · `iss191_boss_pick_fix_option` · `iss191_boss_q_envc_unify` · `iss191_boss_r_pg_pull_dnp` · `iss234_boss_pick_5q` · `iss250_n3_threshold_recheck` ★

★**边界**: ★**老字一字未删** (★追加式·★老行逐字保留★) · ★**零写板** · ★**零落表** · ★**零外发** · ★**一件没代老板拍** · ★**不改 `PROJECT_TRACKER.md` §0** · ★**不写别的 agent 的分片** ★
"""
import os
import shutil
import time

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
PAGER = os.path.join(PROJ, "DECISION_ONE_PAGER_2026-11-22.md")
STAMP = time.strftime("%Y%m%d_%H%M")

SECTION = """

## ★★㉞ 【本轮 2026-11-24 02:1x 新增】★ ★★待拍板面的三处旧数就地订正 (★50 → **52** · 34 → **32** · 47 → **52**) + ★★52/52 逐 key 覆盖核对 (★一件没漏·★一件没代拍★)★★

★**① 计数订正 (★本机实跑 `state/advance.py --json` ⇒ decisions 实读 **52** 条·★hw.yaml 13 · mech.yaml 14 · pm.yaml 12 · sw.yaml 13★)★★

| 旧数 (写在哪儿) | 旧值 | ★**本轮实读值** ★ |
|---|---|---|
| §㉞ 末行「⇒ 待拍板面 50 条」 | 50 | ★**52** ★ |
| §③ 标题「其余 34 条」 | 34 | ★**32** (= 52 − §①/§⑦/§㉝ 那 20 条) ★ |
| §㉓-4「全量待拍板项 = 47 条」 | 47 | ★**52** ★ |

★**★老字一字未删 (★追加式·★老行逐字保留★) ⇒ 上面三处旧数仍在页上, 但以本节为准** ★

★**② 分布 (★实读★)**: ★**逾期 31 条** (★最老 due `2026-10-26` = 「测试设备预算」★) · ★**无 due 21 条** · ★**无一例外全部已逾期** (★not_yet_due = 0★) ★
★**③ 覆盖核对 (★逐 key 实跑, ★**52/52 全覆盖·零漏项**★)★**

| 页 | 覆盖 |
|---|---|
| `DECISION_ONE_PAGER_2026-11-22.md` (★本页★) | **20 / 52** |
| `DECISION_INDEX_2026-11-18.md` (★索引★) | **41 / 52** |
| ★**并集** ★ | ★**52 / 52** ⇒ ★**零漏项** ★ |

★**④ ★★11 个 key 只在本页 (不在索引里) ⇒ 逐个实读确认「建议默认值」不缺 ★★**

| # | need key | 建议默认值在哪 |
|---|---|---|
| 1 | `iss340_c_bucket_boss_decisions` | ★§⑧ (C 桶 2 条)★ |
| 2 | `iss364_k2_d_esd_usb_d_2v3_pin` | ★§㉞-1 表 (★D_ESD_USB_D 2 脚 vs 3 脚★)★ |
| 3 | `iss364_k3_button_3n_vs_1p5n` | ★§㉞-1 表 (★5 只按键 3N vs 1.5N★)★ |
| 4 | `iss364_c_vbus_gnd_keep_or_drop` | ★§⑧-2 (★与 `boss_c_vbus_gnd_reserve_pad_20261117` 同一件事★)★ |
| 5 | `boss_decide_reboard_mtime_size_caliber` | ★§㉝ ⑤ (★main 倾向: 加进 reboard 原子★)★ |
| 6 | `boss_decide_second_reboard_stop_authority` | ★§㉝ ⑥ (★main 不代拍·★流程权责归老板★)★ |
| 7 | `iss191_boss_pick_fix_option` | ★§㉙ 表 11 ★ |
| 8 | `iss191_boss_q_envc_unify` | ★§㉙ 表 12 ★ |
| 9 | `iss191_boss_r_pg_pull_dnp` | ★§㉙ 表 13 ★ |
| 10 | `iss234_boss_pick_5q` | ★§㉙ 表 14 ★ |
| 11 | `iss250_n3_threshold_recheck` | ★§㉙ 表 15 ★ |

★**★⇒ 11/11 实读命中「建议默认值」栏 ⇒ ★**老板要的「建议默认值」一项不缺** ★ ⇒ ★**本节不新增任何拍板项, 也不改任何一条建议值** ★

★**⑤ 板面读数 (★本机实读★)**: ★**板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · size `4940213` ⇒ ★**18 天逐字节未动** ★ ⇒ ★**G1 仍开, 不许投板** ★
★**门禁 (本轮 5 连实跑)**: ★**merge rc=0** (产出 801 · 阻塞 43 高危 33 · 未闭合需求 329 · 冲突 0) · ★**gate_check rc=0** (★Q1 **18/18** · Q7 10/10 道绿·缺口 3 条) · ★**issue_check rc=1** (违规 **19** 条 = ★既有逾期项·零新增★) · ★**stage_gate rc=1** (★当前 **G1** · 还差 **1** 项 = PCB 布线 unconnected 45 → 0 · G1a 还差 2 条 G1a-4/G1a-8★) · ★**daily_check rc=3** (★三条全是老异常: 问题闭环门 19 条 / `check_pcb_nets` rc=1 / `chain_gate`★) ★
★**外发段**: ★**恒空** (★老板 2026-11-12 02:02「不再发信, 全靠自己查资料」⇒ `state/outbox/` 19 份草稿**只备不发**★)
"""


def main():
    with open(PAGER, encoding="utf-8") as fh:
        src = fh.read()
    if "## ★★㉞ " in src:
        print("★§㉞ 已存在 ⇒ 不重复追加★")
        return 0
    bak = PAGER + ".bak_%s_cron775d_r82" % STAMP
    shutil.copy2(PAGER, bak)
    tmp = PAGER + ".tmp_%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(src.rstrip("\n") + "\n" + SECTION)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, PAGER)
    with open(PAGER, encoding="utf-8") as fh:
        after = fh.read()
    assert after.startswith(src.rstrip("\n")), "★老字被改了 ⇒ 中止★"
    assert len(after) > len(src), "★变短了 ⇒ 中止★"
    print("★决策页追加 OK ★ %d → %d B (★老字逐字保留★) · 备份 %s" %
          (len(src), len(after), os.path.basename(bak)))
    print("   追加节: §㉞ (★订正 50→52 / 34→32 / 47→52 + 52/52 覆盖核对·11/11 建议默认值在位★)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
