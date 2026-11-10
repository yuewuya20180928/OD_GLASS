#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""刷新老板拍板页 DECISION_PENDING_2026-11-11.md (第 11 次刷新) —— 2026-11-11 05:4x

★**只整理 + 给建议默认值, 不代决** —— 拍板前不动任何采购 / 外发 / 改图 / 改锁死表。
★**本轮 C 段口径: 35 → 35 (0 新增 / 0 移除 / 0 改建议值)** ⇒ ★**你不用重看一遍, 除非你想改建议默认值**。

★**本轮实质**: ① ISS-187 (护栏两个洞) 落账 verified (sw-lead 签字 + 我独立复核)
   ② 同批订正 sw-lead 报的 1 条非阻塞瑕疵 (护栏⑨ 注释出处指针指错门)
   ③ A 段仍 0 条可派 —— 但★**原因变了**: 现在 hw-lead 名下确实有 1 条 open (ISS-186),
      卡在铁律上 (ISS-181 blocker 在飞) 而不是"没活"
   ④ 跑核验 5 连 ⑤ 刷新这一页 ⑥ GitHub 同步 + blob SHA 逐个校验
"""
import os
import sys

P = "DECISION_PENDING_2026-11-11.md"
s = open(P, encoding="utf-8").read()
lines = s.split("\n")

NEW_TITLE = (
    "# 待老板拍板页 · 2026-11-11 05:4x (第 11 次刷新 · ★C 段口径 0 变化 (35 → 35) "
    "+ ★**ISS-187 已落账 verified (护栏从「关系型」升级成「值型」)** + ★**护栏⑨ 注释指错门已订正** "
    "+ ★**A 段仍 0 可派, 但原因变了 (hw-lead 名下确有 1 条 open, 卡在 ISS-181 在飞)**★)"
)

NEW_WHAT = (
    "> ★ **本轮我自己动了什么**: ①派活核算 (internal=0, 无可派, ★**但原因变了**: hw-lead 名下现在确有 1 条 open "
    "(ISS-186) ⇒ 卡在铁律上 (ISS-181 blocker 在飞), 见 §0.7) "
    "②★**ISS-187 落账 verified** (sw-lead 复验 = pass ⇒ ★**我自己独立复核后才落的**: selftest rc=0 且护栏 7→10 条全过 / "
    "demo_timing_check rc=0 / 5 个交付物 md5 与 sw-lead 实测值逐字节相同 / ★**stdout 10908 B 与「加护栏前」真基线 6ced111 逐字节相同**) "
    "③★**同批订正 1 条非阻塞瑕疵** (护栏⑨ 注释的出处指针 `§(1.56)` → `SW/DEMO_OD_TIMING_SPEC.md` §3.3.1 + `PROJECT_TRACKER.md:2099`; "
    "issue_log ISS-187 的 `desc` 同一处指针一并订正 ⇒ ★**只改注释/指针, 值没动, 护栏行为不变, stdout 逐字节不变**) "
    "④★**M8 洞如实报仍未堵** (`T_PANEL` 5.00→4.00 变异体 selftest 仍全绿 ⇒ ★**基线就有的性质, 非本单引入** ⇒ 建议后续加护栏⑪) "
    "⑤跑核验 5 连 ⑥刷新这一页 ⑦GitHub 同步 + blob SHA 逐个校验。"
)

NEW_SEC = """## 0.11 ★★★ 本轮: **ISS-187 闭环 (护栏从「关系型」升级成「值型」)** ⇒ ★**C 段 35 项一个字没动**

> ★**这一节全是已完成的工程活, 不是要你拍板的事** ⇒ ★**你今天不必为它做任何决定**。

### 0.11.1 ★ ISS-187 落账 verified ⇒ ★**老板那条生死线数字 (合成段只剩 2.32ms) 从此改不动了**

| | |
|---|---|
| **签字** | ★**sw-lead 复验 = pass** (2026-11-11 05:10) ⇒ `state/issue_log.yaml` ISS-187 已 **status=verified / verify_result=pass / verify_by=sw-lead / verify_date=2026-11-11** (★**owner=main / verify_by=sw-lead ⇒ 「别人验」结构成立**) |
| **★病根 (元问题)** | ★**原有 7 条护栏全是【关系护栏】** —— ④断言「加/不加 TX 的**差** == TX_MIN_1080」(★自洽★) · ⑦断言「两个 TX 的**比值** == 像素比」(★比值★) ⇒ ★**没有一条钉 TX 的【绝对值】** ⇒ ⇒ 改脚本的人可以把物理下限改小, **7 条全绿** |
| **★sw-lead 的元结论 (我照做)** | ★**任何用「被检查的同一组常量」重算期望值的断言, 都是自洽断言, 守不住数值** ⇒ ⇒ 新护栏钉的是**已发布的字面值** |
| **新加 3 条 (值型)** | ⑧ **TX 已发布值钉死** (`TX_MIN_800 == 1.800` 且 `TX_MIN_1080 == 7.776`) · ⑨ **链路参数钉死** (`4-lane @ 2.0Gbps × 0.8`) · ⑩ **默认路径必须带 TX** (★**这条才是堵 M2 的**★) |
| **★我没有采信自证, 落账前自己重跑了一遍** | ① `HW/e2e_budget_rk3572.py --selftest` ⇒ **rc=0, 护栏 7 → 10 条全过** (我实跑看到的输出行: ⑧ 钉 1.800/7.776 · ⑨ 钉 4-lane@2.0Gbps×0.8 · ⑩ 默认值 == 显式传 TX 的 59.6810) ② `SW/tools/demo_timing_check.py` ⇒ **rc=0** ③ ★**5 个交付物 md5 与 sw-lead 实测值逐字节相同** (`d7d1b110…`/`88f441ec…`/`38e256d2…`/`2fe3be4c…`/`085a2ed1…`) ④ ★**stdout 与「加护栏前」真基线 `6ced111` (md5 `0e622d56…`) 逐字节相同 ⇒ 10908 B, `diff` 空** ⇒ ★**已发布数字一个没动** |
| **★对你的影响** | **零** —— ★**不新增决策项, 不改锁死表, 不发邮件** ⇒ ★**C 段 35 项一个字没动** |

### 0.11.2 ★ 同批订正了 sw-lead 报的 1 条非阻塞瑕疵 (值对、指针错)

- **病** = 护栏⑨ 的 `#` 注释写「对齐 `PROJECT_TRACKER.md §(1.56)` 已发布的 4-lane@2.0Gbps × 80% 有效」⇒ ★**`§(1.56)` 是 sensor 拍板 (onsemi AR0234CS), 与 DSI 无关**; ★**且「× 80% 有效」这个系数 PROJECT_TRACKER 全篇零命中** (真出处是 `SW/DEMO_OD_TIMING_SPEC.md` §3.3.1 `:181`)。
- **已订正** (★**只改注释, 值没动**★) ⇒ 护栏行为不变 (M3 变异体照样红) ⇒ ★**stdout 仍 10908 B 逐字节相同** ⇒ `HW/e2e_budget_rk3572.py` md5 `d7d1b110…` → **`7b820c14acfaee08a218cbf85557ef0b`** (★已记进 ISS-187 的 `fix_ref`★) ⇒ `state/issue_log.yaml` ISS-187 的 `desc` 同一处指针一并订正。
- ★**为什么记这一条**: 这一单的核心卖点就是「⑧⑨ 钉的是**已发布的字面值**」⇒ **出处指针指错门, 下一个读脚本的人就会一头雾水** ⇒ ★**口径纪律要防的正是这个**。

### 0.11.3 ★ 如实报: ★**还有一个洞没堵 (M8)**, 且★**不是我这一单引入的**

| 变异体 | 改什么 | selftest | 判定 |
|---|---|---|---|
| **M8** | `T_PANEL` 5.00 → 4.00 | ★**rc=0 (全绿)** | ★**基线就有的性质** (sw-lead 用加护栏前的基线实跑同样全绿) ⇒ ★**不是本单引入的回归**; 但 stdout 会变 ⇒ 被验收项④抓到 ⇒ ★**建议后续加护栏⑪** |

### 0.11.4 ★ A 段本轮仍 0 条可派, ★**但原因变了** (不是"没活", 是"卡在铁律上")

| | |
|---|---|
| **A 段 (internal)** | **0 条可派** (`state/advance.py --json` ⇒ `internal: []`) |
| **★为什么** | ★**hw-lead 名下现在确实有 1 条 `open`** —— **ISS-186** (high, due 11-13, DSI payload 8× 口径差 6 处) ⇒ ★**但 ISS-181 (blocker, 自研 demo 主板 → 可下单) 仍在 `fixing`** ⇒ ★**铁律「一个 agent 同时只允许一个在飞任务」⇒ 本轮不派给它** ⇒ ★**下一轮 ISS-181 一落账, ISS-186 立刻就是第一个该派的** |
| **sw-lead / mech-lead** | ★**两人都没有 `open` 单** (sw-lead 10 closed / 2 fixed / 13 verified · mech-lead 14 closed / 3 deferred / 2 fixed / 7 verified) ⇒ ★**派活的前提 (有活) 不成立** |
| **★你自己的单也没忘** | ★**21 条 `main` 单 (owner=项目总工) 全在推进**: ISS-139 / ISS-155 / ISS-160 三条 blocker 是 ISS-181 的前置 ⇒ ★**这些单不需要你拍板** |

"""


def replace_line(prefix, new_line, tag):
    global lines
    hits = [i for i, ln in enumerate(lines) if ln.startswith(prefix)]
    if len(hits) != 1:
        print(f"❌ {tag}: 前缀匹配到 {len(hits)} 行 (期望 1)")
        sys.exit(1)
    lines[hits[0]] = new_line
    print(f"✅ {tag} 已替换 (行 {hits[0] + 1})")


# ---- ① 标题行 ----
if not lines[0].startswith("# 待老板拍板页 · 2026-11-11 05:0x"):
    print(f"❌ 标题行不是预期的 05:0x 版: {lines[0][:80]!r}")
    sys.exit(1)
lines[0] = NEW_TITLE
print("✅ 标题行已替换")

# ---- ② 本轮我动了什么 ----
replace_line("> ★ **本轮我自己动了什么**:", NEW_WHAT, "'本轮我动了什么'")

# ---- ③ §0.7 的两条已过期陈述 (sw-lead 会话已结束 / "没有 open 单" 已不成立) ----
replace_line(
    "| **为什么不派** |",
    "| **★为什么不派 (★本轮已改写: 原因从「没活」变成「卡在铁律上」★)** | ★**hw-lead 名下现在确实有 1 条 `open`** —— "
    "**ISS-186** (high, due 11-13, DSI payload 8× 口径差 6 处) ⇒ ★**但 ISS-181 (blocker) 仍在 `fixing`** ⇒ "
    "★**铁律「一个 agent 同时只允许一个在飞任务」⇒ 本轮不派给它** ⇒ ★**ISS-181 一落账, ISS-186 立刻是第一个该派的** · "
    "sw-lead 10 closed / 2 fixed / 13 verified / **0 open** · mech-lead 14 closed / 3 deferred / 2 fixed / 7 verified / **0 open** ⇒ "
    "★**这两个是真「没活」** |",
    "§0.7 '为什么不派'",
)
replace_line(
    "| **★还有一个\"在飞\"** |",
    "| **★sw-lead 那个写会话已结束** | ★**ISS-137 rev3 复验 (03:1x 派出) 与 ISS-187 复验 (04:5x 派出) 都已交卷** "
    "(最新: ISS-187 复验 = pass, 05:10) ⇒ ★**sw-lead 现在没有在跑的写会话**, 但 ★**它名下也没有 `open` 单** ⇒ ★**仍 0 条可派** |",
    "§0.7 '在飞' 行",
)

# ---- ④ 新插 §0.11 (插在 §0.10 之前) ----
anchor_idx = None
for i, ln in enumerate(lines):
    if ln.startswith("## 0.10 "):
        anchor_idx = i
        break
if anchor_idx is None:
    print("❌ 找不到 §0.10 锚点")
    sys.exit(1)
lines[anchor_idx:anchor_idx] = NEW_SEC.split("\n")
print(f"✅ §0.11 已插入 (行 {anchor_idx + 1})")

out = "\n".join(lines)
open(P, "w", encoding="utf-8").write(out)
print(f"✅ 已写回 {P} ({len(out)} 字符)")
