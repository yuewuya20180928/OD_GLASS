#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""决策页 2026-11-12 · 第 2 次刷新 (r26) —— 由 main (项目总工) 执行
================================================================================
★**本轮 (01:41~01:55) C 段口径变化 = 0★**: `advance.py --json` 实测 `decisions` = **36**
   ⇒ ★**0 新增 / 0 退休 / 0 改建议默认值** ⇒ ★**本脚本一个字都不改 §1~§8 的建议默认值** ★

★**本脚本只做 2 件事 (★全是【记账】, 不替老板决定任何事★)**:
   ① 在页首插一节 **§0.27** = 本轮后继计划的事实记账 (A 段 0 派 / B 段恒空 / C 段 36→36 /
      核验 5 连 rc / ISS-136 验收签字 / ISS-199+ISS-200 新开并已派 / 板面零变化 / 本 job 不推 GitHub)
   ② 订正页首标题行 = 把「A 段本轮 0 条 (★真在飞: hw-lead 名额被 ISS-136 占住★)」改成
      本轮的真实原因 (★**兄弟 job「ARS45 队列自动派活」已把三个名额全占满** ⇒ 本 job 不重复派★)

★**§1~§8 的 36 条 (问题描述 / 建议默认值 / 不拍板的后果 / 逾期列) 一字不动** ★
★**实测依据**: 本轮已逐条核对 36 条的「逾期」列 vs `advance.py --json` 今日实数 ⇒ **0 条不一致** ★

★**落盘纪律**: flock + 锁内重读 + 原子写 (tmp → fsync → os.replace → fsync(dir))
★**边界**: 不改 C 段任何一条的建议默认值 · 不发邮件 · 不改 §0 锁死表 · 不写任何子总工的分片
"""
from __future__ import annotations

import fcntl
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
PAGE = os.path.join(PROJ, "DECISION_PENDING_2026-11-12.md")
LOCK = os.path.join(HERE, ".decision_page.lock")

OLD_TITLE = ("# 待老板拍板页 · 2026-11-12 00:2x (第 1 次刷新 · ★**C 段 36 → 36 "
             "(0 新增 / 0 退休 / 0 改建议值)** + ★**A 段本轮 0 条 (★**真在飞: hw-lead 名额被 ISS-136 占住★**)**")
NEW_TITLE = ("# 待老板拍板页 · 2026-11-12 01:5x (第 2 次刷新 · ★**C 段 36 → 36 "
             "(0 新增 / 0 退休 / 0 改建议值)** + ★**A 段本 job 派 0 条 (★**兄弟 job「ARS45 队列自动派活」"
             "已把 hw-lead / mech-lead 两个名额占满 + 第三个 (ISS-199) 在排队★**)**")

SEC_027 = """## 0.27 ★★★ 本轮 (2026-11-12 01:4x ~ 01:5x): ★**C 段 36 → 36 (0 新增 / 0 退休 / 0 改建议值)** + ★**本 job 不重复派活 (★**兄弟 job 已占满名额★**)** ★★

> ★**这一节全部是【我这边记账 / 独立复核 / 核验】的活 ⇒ ★**不需要你做任何新决定** ⇒ ★**C 段 36 项的建议默认值一个没动** ⇒
> ★**仍等你拍的只有 §1 那 3 条 + §1b 那 1 条 + §2 那 1 条 = 5 条** (★**与 00:2x 那轮完全一样★**) ★★

### 0.27.1 ★★★ ★**A 段: 本 job 派了 0 条 —— 原因 = 【兄弟 job 已把名额占满】, 不是【没活】** ★★★

| | |
|---|---|
| ★**实测 `advance.py --json` (01:41 首跑)** | ★**`internal: []` · `approvals: []` · `decisions: 36` · `waiting: []`** ⇒ ★**A 段本 job 手上确实没有可派项** ★ |
| ★**01:47 复跑 (兄弟 job 派活后)** | ★**ISS-195 (hw-lead) = `fixing` · ISS-200 (mech-lead) = `fixing` ⇒ 两个会话实测 status=**running** (`dc510f7c` / `0ef5e479`, 均 01:48 起) ⇒ ⇒ ★**`advance.py` 的 in_flight 判据正确挡住重复派活** ★ ⇒ ★**⇒ 本 job 不重复派 (★**两个 job 同时派同一个 agent = 撞 R18「一个 agent 同时一个写会话」铁律**★)** ★ |
| ★**本轮实际发生的派活 (由兄弟 job「ARS45 队列自动派活」执行, 不是本 job)** | ★**① ISS-195 → hw-lead** (麦 M1→S1 压紧螺钉孔孔壁净空按套A 重算 · due 11-13) · ★**② ISS-200 → mech-lead** (结构侧 J_CHG pin map 旧口径收敛 · due 11-13) · ★**③ ISS-199 → hw-lead 排队中** (HW 侧 J_CHG pin map 剩 4 处第二口径 · due 11-14 · ★**hw-lead 名额被 ISS-195 占着 ⇒ 等它交卷★**) ⇒ ★**`state/dispatch_log.yaml` 已落 3 条派活记录** ★ |
| ★**ISS-136 (hw-lead) 本轮收口 = main 验收签字** | ★**hw-lead 00:2x 交卷 ⇒ 兄弟 job 已落 `verified` / `verify_result=pass` / `verify_by=main`; ★**我本轮独立复核 (不采信自述)** ★★: `python3 HW/check_bq25896_pinout.py` ⇒ **rc=0** (PASS **11** / FAIL **0**) · `python3 state/gate_check.py` ⇒ **rc=0** (★**【Q1 18/18** ★ + ★**【Q6 硬件真源闸】✅ 通过 (rc=0)★ ⇒ 证明它真在门禁链里跑**) · ★**反向用例 (真在读规格的证据)**: 副本上把 §5.2 pin7 改回 `PWR_GOOD` ⇒ **rc=1 且只有 ⑦ 一项 FAIL** (其余 10 项仍 PASS ⇒ 精确定位漂移点) ⇒ 恢复 ⇒ **rc=0** ⇒ ★**"规格漂移 = 闸红" 这条机制是真的** ★ |
| ★★**本轮按【原理图主线】跳过了哪几条 PCB 类** ★★ | ★**跳过 0 条** (★**三个总工的 open 队列里没有 PCB 布线/布局类单: ISS-195 = 机械孔位净空复算 · ISS-199 = HW 侧 pin map 文档口径 · ISS-200 = 结构侧 pin map 口径 ⇒ 三条都不是 PCB 布线★**) ⇒ ★**⇒ 而 owner=main/boss 的 PCB / 几何类 open 单 —— ISS-122 (BGA 逃线层数) · ISS-126 (板厚档位) · ISS-128 (板面积账+逃线层数) · ISS-160 (demo 板图纸链) · ISS-169 (demo 板可制造性) · ISS-060 (产品件三条几何) —— ★**共 6 条继续压着不派** (★**老板 2026-11-11 10:07 口径: 先解决原理图绘制, 再解决 PCB 绘制★**), ★**也没藏账** (★**它们仍列在 G4 未闭环清单里, 且 stage_gate rc=1 / G1 仍开 ⇒ 不许投板没松★**) ★ |

### 0.27.2 ★★★ ★**核验 5 连 (本轮实测 rc) + B 段恒空 + 板面零变化 + 本 job 不推 GitHub** ★★★

| 闸 | rc | 结论 |
|---|---|---|
| `state/merge.py` | **0** | 冲突 **0** · 产出 **177** · 阻塞 43 (高危 33) · 未闭合需求 **102** (★**比上轮 101 多 1 ⇒ 是 ISS-136 交卷带出的新增需求, 不是账做坏★**) |
| `state/gate_check.py` | **0** | ★**齐备率 18/18** · ★**【Q6 硬件真源闸】✅ 通过** · 与 merge 自对账一致 |
| `state/issue_check.py` | **1** | 违规 **29** 条 (★**比上轮 30 少 1 ⇒ ISS-136 落 verified 关掉一条, ★**没新造违规★**) ★**全是逾期类** ★ |
| `state/stage_gate.py` | **1** | 当前 **G1** (原理图 / PCB 定稿), 还差 **1** 项 ⇒ ★**PCB 布线未达标: unconnected=45 (需 0) · DRC 违规=0 (需 0) (ISS-181)** |
| `state/daily_check.py` | **3** | 巡检异常已记录 (非崩溃): 问题闭环门违规 29 条 · 内部未闭合 100 → **102** · 问题单 194 → **196** (★**ISS-199/200 新开, 是记账不是爆雷★**) |
| ★**B 段 approvals** | — | ★**= 0 (★**老板 2026-11-11 19:31「一律不发」政策后恒为空★**) ⇒ ★**草稿一件没少, 一封都没发**: `state/outbox/` 实测 **19 份 .md** (16 草稿 + README + 政策件 `NO_OUTBOUND_POLICY.md` + 内部决策图 `R_GEO_2_DECISION_MAP.md`) + `attach/` **3 份** ⇒ ★**零缺失** ★ |
| ★**C 段逐条核对** | — | ★**`advance.py --json` 实测 36 项 ⇒ 0 新增 / 0 退休 / 0 改建议默认值; ★**且逐条核对每张表的「逾期」列 vs 今日实数 ⇒ 0 条不一致** (★**今天没改页里任何一个数字, 因为今天与 00:2x 那轮是同一天 ⇒ 天数没走★**) ★ |
| 本地快照 | **0** | ★**`PROGRESS_SNAPSHOT.md` 已生成 (01:52)** ⇒ ★**只落本地, 随时能看** ★★ |
| GitHub | — | ★**本 job 不推** (★**统一由 `ARS45 GitHub 同步 (每 5 小时 · 有进展才推)` job 负责★**) ⇒ 上次推送 **2026-11-12T00:26:07** ★★ |
| ★**板 / 网表 / 脚表 / .kicad_pro** | — | ★**一个字节没动**: 板 md5 `611b869e13518c3c023fb178f91a0075` · 网表 `c78f991283cc82d56c8e3dd31657c785` · 脚表 `4814617e22b567d76164e56bc5e39dc8` · `.kicad_pro` `3e504d2be83152e337949723e909be1b` ★★ |

### 0.27.3 ★★★ ★**本轮对页面的唯一改动 = 加一节 §0.27 (★建议默认值一个没动★)** ★★★

| # | 改什么 | 为什么 |
|---|---|---|
| 1 | ★**页首插一节 §0.27** (本轮事实记账: A 段 0 派 + 真实原因 / ISS-136 独立验收 / 核验 5 连 rc / B 段恒空 / 板面零变化 / 本 job 不推 GitHub) | ★**老板翻页第一眼要看到的是【今天到底发生了什么】, 而不是重复读同一张 36 条表** ★ |
| 2 | ★**页首标题行改写** (把「A 段 0 条 = hw-lead 名额被 ISS-136 占住」改成「本 job 派 0 条 = 兄弟 job 已占满名额」) | ★**旧句已经过期** (ISS-136 本轮已 verified) ⇒ ★**留着就是给老板看假账** ★ |

★**★除此之外: §1~§8 的 36 条【问题描述 + 建议默认值 + 不拍板的后果 + 逾期】四列【一字未改】, 页尾逾期分布表 (36 项 / 已逾期 33 / 剩 0 天 1 / 无 due 2) 也与今日实数一致 ⇒ 未动 ★★**

---
"""

ANCHOR = "## 1. 🔴 当期真卡主线的只剩 **3 项**"


def main() -> int:
    os.makedirs(os.path.dirname(LOCK), exist_ok=True)
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        raw = open(PAGE, encoding="utf-8").read()

        if "## 0.27 ★★★" in raw:
            print("ℹ️ 已有 §0.27 ⇒ 幂等, 不重复写 (rc=0)")
            return 0

        if OLD_TITLE not in raw:
            print(f"❌ 页首标题行没找到预期串 ⇒ 拒绝改 (防误伤)")
            return 2

        out = raw.replace(OLD_TITLE, NEW_TITLE, 1)

        if ANCHOR not in out:
            print("❌ 没找到插入锚点 §1 ⇒ 拒绝改")
            return 2
        out = out.replace(ANCHOR, SEC_027 + "\n" + ANCHOR, 1)

        fd, tmp = tempfile.mkstemp(dir=os.path.dirname(PAGE), prefix=".DECISION_PENDING.", suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(out)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, PAGE)
            dfd = os.open(os.path.dirname(PAGE), os.O_RDONLY)
            try:
                os.fsync(dfd)
            finally:
                os.close(dfd)
        except Exception:
            if os.path.exists(tmp):
                os.unlink(tmp)
            raise

    print(f"✅ 决策页已原子落盘: {PAGE}")
    print(f"   行数 {raw.count(chr(10)) + 1} → {out.count(chr(10)) + 1} (+{out.count(chr(10)) - raw.count(chr(10))})")
    print("   §1~§8 的 36 条建议默认值 / 逾期列 一字未动")
    print("   页首标题行已订正为「本 job 派 0 条 = 兄弟 job 已占满名额」")
    return 0


if __name__ == "__main__":
    sys.exit(main())
