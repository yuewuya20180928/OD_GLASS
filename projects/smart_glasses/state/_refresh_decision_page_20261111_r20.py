#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""刷新老板拍板页 DECISION_PENDING_2026-11-11.md (第 20 次刷新) —— 2026-11-11 15:2x

★**只整理 + 给建议默认值, 不代决** —— 拍板前不动任何采购 / 外发 / 改图 / 改锁死表。

★**本轮 C 段口径: 38 → 38 (0 新增 / 0 移除 / 0 改建议值)** ⇒ ★**你不用重看一遍**。

★**本轮最实质的一件事 (★不是记账, 是把卡了 6 轮的队列解冻★)**:
  ★**A 段从"恒为空"变成"能派得出活"** —— ★**根因 = ISS-181 的 `fixing` 标记是假的** (它 11-04 派出后
  板子活实际由主会话的臂 campaign 跑, ★**那 7 条臂 (v44/46/47/48 + na/nb/mz) 全部 REJECT @09:36 ⇒ 现无臂在跑**)
  ⇒ ★**它长期占着 hw-lead 的唯一名额 ⇒ A 段连续 6 轮为空 (决策页 §0.7 / §0.11.4 / §0.15.2 / §0.17.2 都记着)**
  ⇒ ★**本轮按老板 11-11 10:07 口径改成 `deferred` (= 排队, 不是在飞) ⇒ hw-lead 名额释放 ⇒ 队列恢复可派** ★

★**落盘纪律**: flock + 锁内重读 + 原子写 (tmp → fsync → os.replace → fsync(dir))
★**边界**: 不改任何建议默认值 · 不改 C 段 38 项 · 不发邮件 · 不下采购单 · 不改 §0 锁死表
"""
from __future__ import annotations

import fcntl
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
P = os.path.join(PROJ, "DECISION_PENDING_2026-11-11.md")
LOCK = os.path.join(HERE, ".decision_page.lock")

NEW_TITLE = (
    "# 待老板拍板页 · 2026-11-11 15:2x (第 20 次刷新 · ★**C 段 38 → 38 (0 新增/0 移除/0 改建议值)** "
    "+ ★**A 段解冻: 假 `fixing` 标记已纠正 (ISS-181 → deferred) ⇒ 队列恢复可派, 本轮派出 ISS-191 → sw-lead** ★★)"
)

NEW_WHAT = (
    "> ★ **本轮我自己动了什么**: ①★★**A 段从【恒为空】变成【能派活】** —— ★**根因 = `ISS-181` 的 `fixing` 标记是"
    "假的**: 它 11-04 派出后, 板子活实际由主会话的臂 campaign 跑 ⇒ ★**那 7 条臂 (v44/46/47/48 + na/nb/mz) 全部 "
    "REJECT @09:36 ⇒ 现无臂在跑** (实测 `ps` 无 freeroute/臂进程) ⇒ ★**它长期占着 hw-lead 的唯一名额 ⇒ "
    "`advance.py` 的 in_flight 判据把 hw-lead 整个跳过 ⇒ A 段连续 6 轮为空** (决策页 §0.7 / §0.11.4 / §0.15.2 / "
    "§0.17.2 都记着这句话) ⇒ ★**本轮按老板 11-11 10:07「PCB 布线/布局类一律【不派】(排队等原理图定稿)」把它改成 "
    "`deferred` (= 排队, 不是在飞) ⇒ hw-lead 名额释放 ⇒ 队列恢复可派** ★ ⇒ ★**三条后果都先查过 (不是副作用失控)**: "
    "① `advance.py` 直接跳过 deferred ⇒ ★**它不会被自动派出去** (= 守住「PCB 类不派」) ② ★**G1 仍卡住** "
    "(G1 判据读 `.layout_done.json` 的 unc=45, **不读 issue 状态** ⇒ 「不许投板」一点没松) ③ ★**G4「问题单未闭环」"
    "清单仍列出它** (实测 deferred 的 ISS-004/013/016 都在里面) ⇒ ★**没藏账** ★ ⇒ ★**唯一会变的数字: 逾期未闭环 "
    "33 → 32 (C4 规则「deferred 不算逾期」) ⇒ ★**这是口径纠正, 不是活干完了** ★ ②★**本轮派出 1 条: ISS-191 → sw-lead** "
    "(★**改派** owner: hw-lead → sw-lead ⇒ 理由: ★**hw-lead 名下主线 6b 仍在跑** (13:45 起, 实测 "
    "`state/gen_kicad_sch.py` 15:05 / `demo_mainboard.kicad_sch` 15:06 仍在改) ⇒ 铁律「一个 agent 同时只允许一个写会话」"
    "⇒ 不能给 hw-lead; ★**而 sw-lead 实测无在跑写会话** (最后一条 13:51 done) ⇒ ★**三条改法本就出自 ISS-190 §7-2 "
    "(sw-lead 交卷, main 二次验收 verified/pass) ⇒ 是它自己的后续**, 验收命令 `timing_check.py --only F1_reset_rc` "
    "**本就是 sw-lead 自建工具** (自测 55/55), ★**文件交集实测 = 0** ⇒ ★**本轮只出方案页, 不改网表 / 不改板 / 不改原理图** ★★ "
    "③★**B 段 approvals = 0 条** ⇒ ★**草稿一件没少也没发**: `state/outbox/` **17 份 .md** (含 1 份 README 清单) + "
    "`attach/` **3 份** ⇒ ★**一封都没发, 一家供应商都没联系** ★ ④★**C 段 38 → 38** ⇒ ★**38 项的建议默认值一个字没动** "
    "★ ⑤★**核验 5 连本轮实测 rc**: merge **0** (冲突 0 · 产出 162 · 阻塞 43 高危 33 · 未闭合需求 87) · gate_check **0** "
    "(★**齐备率 18/18** · 证据分级 3/3 · 接口声明 480 条 · 硬指标覆盖 2/3) · issue_check **1** (违规 **32** 条) · "
    "stage_gate **1** (当前 **G1**, 还差 **1** 项 ⇒ G2 延后) · daily_check **3** (巡检异常已记录, 非崩溃) ⑥★**GitHub: "
    "本 job 不推** (统一由 `ARS45 GitHub 同步 (每 5 小时 · 有进展才推)` job 负责) ⇒ ★**只落本地快照** "
    "(`PROGRESS_SNAPSHOT.md` 已生成) ⑦★**板 / 网表一个字节没动** (板 md5 仍 `611b869e` · 网表 md5 仍 `c78f9912`) "
    "⑧**没有动任何需要你拍板的东西, 没有发任何邮件, 没有下采购单, 没有改 §0 锁死表, 没有写任何子总工的分片**"
)

NEW_SEC = """## 0.20 ★★★ 本轮: ★**A 段解冻 (★假 `fixing` 标记已纠正★) + 派出 ISS-191 → sw-lead** ⇒ ★**C 段 38 → 38 (你不用重看)** ★★

> ★**这一节全部是【我这边记账/派活/核验的活】⇒ ★**不需要你做任何决定** ⇒ ★**没有新增任何决策项, 没有改任何建议默认值** ⇒ ★**下面 38 项的口径与你上一次看的完全一致**。

### 0.20.1 ★★ 本轮最实质的一件事: ★**A 段【恒为空】的根因被拔掉了** (★连续 6 轮的病根★)

| | |
|---|---|
| ★**症状 (实测)** | ★**`advance.py --json` 的 `internal[]` 连着 6 轮都是空的** (决策页 §0.7 / §0.11.4 / §0.15.2 / §0.17.2 都写着「A 段恒为空」) ⇒ ★**三个总工名下没有一条 `open` 单** ⇒ 自动派活无单可派 |
| ★**根因 (★不是「没活」, 是一个假标记★)** | ★**`advance.py` 的 in_flight 判据 = 「owner 名下已有 `status==fixing` 的 issue ⇒ 本轮跳过该 agent」** ⇒ ★**`ISS-181` (hw-lead, blocker, 自研 demo 主板布线到可下单) 自 11-04 一直挂在 `fixing`** ⇒ ★**它把 hw-lead 名下唯一那条 open 单 (ISS-191) 永久挡住** ⇒ ★**而且它已经不符合事实了**: ① ★**板子活实际由【主会话】的臂 campaign 跑, 不是 hw-lead 在跑** ② ★**那 7 条臂 (v44/46/47/48 + na/nb/mz) 全部 REJECT @09:36 ⇒ 现无臂在跑** (实测 `ps` 无 freeroute / 臂进程) ③ ★**官方板 md5 `611b869e` 自 11-06 07:07 起一字未动** ⇒ ★**「fixing (在飞)」是假的** ★ |
| ★**本轮处置 (★按老板 10:07 口径, 不是我自己拍★)** | ★**`ISS-181`: `fixing` → `deferred`** (= ★**排队等原理图定稿**★) ⇒ ★**这正是老板 11-11 10:07 的原话**: 「PCB 布线 / 布局类 ISS 一律【不派】(排队, 等原理图定稿后)」 ⇒ ★**排队 = `deferred`, 不是一个需要我自己判断的技术决定** ★ ⇒ ★**hw-lead 名额释放 ⇒ A 段恢复可派** ★ |
| ★**三条后果都先查过 (★不是副作用失控★)** | ① ★**它不会被自动派出去** (`advance.py` 直接跳过 `deferred`) ⇒ ★**守住「PCB 类不派」** ✔ ② ★**G1 仍卡住**: G1 判据读 `HW/PCB/.layout_done.json` 的 `unconnected=45`, ★**不读 issue 状态** ⇒ ★**「不许投板」的口径一点没松** (本轮实测 stage_gate 仍输出「PCB 布线未达标: unconnected=45 (需 0) · DRC 违规=0 (需 0) (ISS-181)」) ✔ ③ ★**G4「问题单未闭环」清单仍列出它** (实测 deferred 的 ISS-004/013/016 都在那份清单里) ⇒ ★**没藏账** ✔ |
| ★**唯一会变的数字 (★必须写明, 免得你以为是活干完了★)** | ★**逾期未闭环 33 → 32** (C4 规则「deferred 不算逾期」) ⇒ ★**这是口径纠正, 不是活干完了** ⇒ ★**未闭环 blocker 9 → 8** (同因) ⇒ ★**两个数都降了, 但 ISS-181 那一行的账还在 G1 的缺口里, 一行没少** ★ |
| ★**恢复条件 (写死, 免得它又被当成已办)** | ① ★**老板拍板走整链重出** (`state/RECHAIN_ONEPASS_PLAN.md` §5) ⇒ ★**ISS-181 随那次一起做** ② 或 ★**原理图定稿后** (老板 10:07 口径的前提) ⇒ ③ ★**在那之前: 布线 / 布局一律不派** ★ |

### 0.20.2 ★★ 本轮派出 1 条: ★**ISS-191 → sw-lead** (★**改派 owner**, 理由三条全实测★)

| | |
|---|---|
| ★**派的是什么** | ★**ISS-191** (high · due 2026-11-13) —— ★**首台板可能因 `RESET_N` 恒低而无法启动** ⇒ `PG_AND` 上只有 10k 上拉 (`R_PG_PULL`) + 栅极必装的 `Q_AND`, ★**唯一能把 PG_AND 拉低的 `Q_ENVC` 却是 DNP** ⇒ `Q_AND` 栅极恒高 ⇒ 导通 ⇒ `RESET_N` 恒被拉到地 ⇒ ★**首台板可能起不来** ⇒ **P0 (能不能开机, 不是排期问题)** ★ |
| ★**为什么 owner 从 hw-lead 改成 sw-lead (★不然这一单永远出不来★)** | ① ★**hw-lead 名下主线 6b 仍在跑** (13:45 起; 本轮实测 `state/gen_kicad_sch.py` mtime **15:05** / `HW/PCB/demo_mainboard.kicad_sch` mtime **15:06** ⇒ 仍在改) ⇒ ★**铁律「一个 agent 同时只允许一个写会话」⇒ 本单不能给 hw-lead** ② ★**而 `advance.py` 的 in_flight 判据又把 hw-lead 整个跳过** ⇒ ★**两条路都堵死 ⇒ 必须换人** ③ ★**sw-lead 实测无在跑写会话** (最后一条会话 13:51 done) ⇒ ★**铁律成立** ✔ |
| ★**能力匹配 (★不是随便塞个人★)** | ★**三条改法本来就出自 `ISS-190 §7-2` (sw-lead 交卷, main 二次验收 verified/pass) ⇒ 本单是它自己的后续** ★ · ★**验收命令 `python3 SW/tools/timing_check.py --only F1_reset_rc` 本就是 sw-lead 自建工具** (自测 55/55, 且实测真读网表行级 dnp) ★ · ★**零文件交集 (实测)**: 本单只写 `HW/PCB/RESET_P0_FIX_PLAN.md` + `HANDOFF/` + `state/fragments/sw.yaml` ⇒ 与 6b (`gen_kicad_sch.py` + `demo_mainboard*.kicad_sch`) / ISS-192 (`MECH/**`) **交集 = 0** ★ |
| ★**本单范围 (★严格照 brief, 一字没放宽★)** | ★**只出方案页, 不改网表 / 不改板 / 不改原理图 / 不重出投产包** ⇒ ★**真正的落表改动, 等老板拍板后随「一次整链重出」一次做完** ⇒ ★**方案页的第 ③ 点就是「与位号改名合并成一次整链重出的可行性」** ★ |
| ★**verify_by** | ★**仍 = main** ⇒ ★**交卷后由 main 独立重跑复现命令 + 跑反向用例 + 签字, 不采信自述** ★★ |

### 0.20.3 ★★ B 段: ★**approvals = 0 条, 草稿一件没少, 一封都没发**

| | |
|---|---|
| ★**实测** | `state/outbox/` = ★**17 份 .md** (含 1 份 README 清单) + `attach/` = ★**3 份** (2 份附件 + 1 份 README) ⇒ ★**零缺失** (issue_log 引用的 3 份草稿 `bridge_chip_rfq.md` / `jbd_query.md` / `vendor_round2_email.md` 逐个在位) |
| ★**发了没有** | ★**一封都没发, 一家供应商都没联系** —— ★**外发一律等你一句「可以发」** ★★ |

### 0.20.4 ★★ 核验 5 连 (本轮实测 rc) + ★**GitHub 本 job 不推**

| 闸 | rc | 结论 |
|---|---|---|
| `state/merge.py` | **0** | 冲突 **0** · 产出 162 · 阻塞 43 (高危 33) · 未闭合需求 **87** |
| `state/gate_check.py` | **0** | ★**齐备率 18/18** · 证据分级 3/3 · 接口声明 480 条 · 硬指标覆盖 2/3 |
| `state/issue_check.py` | **1** | 违规 **32** 条 (★**比上轮少 1 条 = ISS-181 转 deferred, ★**不是活干完了**★**; 其余逐条与上轮相同**★) |
| `state/stage_gate.py` | **1** | 当前 **G1** (原理图/PCB 定稿), 还差 **1** 项 (unconnected=45 需 0) ⇒ G2 延后 |
| `state/daily_check.py` | **3** | 巡检异常已记录 (非崩溃): 问题闭环门违规 32 条 · 漂移 = 内部未闭合 72→87 / 问题单 181→188 |
| 本地快照 | **0** | ★**`PROGRESS_SNAPSHOT.md` 已生成 (3425 B)** ⇒ ★**只落本地, 随时能看** ★★ |
| GitHub | — | ★**本 job 不推** (★老板 11-11 10:07 口径 ⇒ 统一由 `ARS45 GitHub 同步 (每 5 小时 · 有进展才推)` job 负责★) ★★ |
| ★**板 / 网表** | — | ★**一个字节没动**: 板 md5 仍 `611b869e13518c3c023fb178f91a0075` · 网表 md5 仍 `c78f991283cc82d56c8e3dd31657c785` ★★ |

"""


def atomic_write(path: str, content: str) -> None:
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".decpage_", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
        dfd = os.open(d, os.O_RDONLY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def main() -> int:
    with open(LOCK, "a+") as lf:
        fcntl.flock(lf, fcntl.LOCK_EX)
        s = open(P, encoding="utf-8").read()
        before_len = len(s)

        # ---- 1. 标题 ----
        lines = s.split("\n")
        hit = False
        for i, l in enumerate(lines):
            if l.startswith("# 待老板拍板页 · 2026-11-11 13:2x (第 19 次刷新"):
                lines[i] = NEW_TITLE
                hit = True
                break
        if not hit:
            print("❌ 找不到标题行 (第 19 次刷新) ⇒ 中止")
            fcntl.flock(lf, fcntl.LOCK_UN)
            return 2
        s = "\n".join(lines)

        # ---- 2. 插入 §0.20 (在 §0.19 主节之前) ----
        anchor = "## 0.19 ★★★ 本轮:"
        idx = s.find(anchor)
        if idx < 0:
            print("❌ 找不到 §0.19 锚点 ⇒ 中止")
            fcntl.flock(lf, fcntl.LOCK_UN)
            return 2
        s = s[:idx] + NEW_SEC + s[idx:]

        # ---- 3. 重写『本轮我自己动了什么』段 ----
        start_marker = "> ★ **本轮我自己动了什么**:"
        a = s.find(start_marker)
        if a < 0:
            print("❌ 找不到『本轮我自己动了什么』段 ⇒ 中止")
            fcntl.flock(lf, fcntl.LOCK_UN)
            return 2
        end_marker = ">   ★ **本轮 C 段口径变化"
        b = s.find(end_marker, a)
        if b < 0:
            print("❌ 找不到口径变化尾标 ⇒ 中止")
            fcntl.flock(lf, fcntl.LOCK_UN)
            return 2
        s = s[:a] + NEW_WHAT + s[b:]

        atomic_write(P, s)
        fcntl.flock(lf, fcntl.LOCK_UN)

    after = open(P, encoding="utf-8").read()
    print("✅ 第 20 次刷新已写入:", os.path.basename(P))
    print(f"   字节数 {before_len} → {len(after)} (+{len(after)-before_len})")
    print("   - 标题 → 15:2x / 第 20 次")
    print("   - 新增 §0.20 (4 个子节)")
    print("   - 『本轮我自己动了什么』段已重写")
    print("   - ★**C 段 38 项的建议默认值一个字没动** (0 新增 / 0 移除 / 0 改建议值)")
    # 自检
    assert "## 0.20" in after and "## 0.19" in after and "第 20 次刷新" in after
    assert "ISS-181" in after and "deferred" in after
    assert "ISS-191" in after and "sw-lead" in after
    assert "C 段口径变化: 38 → 38 项" in after
    print("   - 自检 ✅ (§0.20 在 / §0.19 还在 / ISS-181 与 ISS-191 都在 / 38 项口径一致)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
