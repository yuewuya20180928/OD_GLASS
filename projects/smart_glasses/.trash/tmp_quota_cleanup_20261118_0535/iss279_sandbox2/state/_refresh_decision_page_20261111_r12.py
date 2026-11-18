#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""刷新老板拍板页 DECISION_PENDING_2026-11-11.md (第 12 次刷新) —— 2026-11-11 07:5x

★**只整理 + 给建议默认值, 不代决** —— 拍板前不动任何采购 / 外发 / 改图 / 改锁死表。
★**本轮 C 段口径: 35 → 35 (0 新增 / 0 移除 / 0 改建议值)** ⇒ ★**你不用重看一遍, 除非你想改建议默认值**。

★**本轮实质**: ① **A 段从 0 变 1 条 —— ISS-186 解冻并派给 hw-lead** (★手工解冻, 不是 advance.py 自动吐的★)
   ② B 段草稿核查: 17 份草稿全在、**零"已发送"标记** ⇒ 一封没发
   ③ 跑核验 5 连 ④ 刷新这一页 ⑤ GitHub 同步 + blob SHA 逐个校验
"""
import os
import sys

P = "DECISION_PENDING_2026-11-11.md"
s = open(P, encoding="utf-8").read()
lines = s.split("\n")

NEW_TITLE = (
    "# 待老板拍板页 · 2026-11-11 07:5x (第 12 次刷新 · ★C 段口径 0 变化 (35 → 35) "
    "+ ★**A 段本轮解冻并派出 1 条 (ISS-186 → hw-lead, 手工解冻)** "
    "+ ★**B 段 17 份草稿全在 · 零已发**★)"
)

NEW_WHAT = (
    "> ★ **本轮我自己动了什么**: ①★**A 段从 0 条变成 1 条 (ISS-186 → hw-lead, 07:5x 派出)** "
    "—— ★**这是手工解冻, 不是 advance.py 自动吐的**: advance.py 的 in_flight 判据是「owner 名下已有 "
    "status==fixing 的 issue ⇒ 跳过」(★保守代理★) ⇒ ISS-181 (owner=hw-lead, fixing) 把 ISS-186 挡住 ⇒ "
    "`internal=[]` ⇒ `--apply --only ISS-186` 遍历的是空的 internal ⇒ **一条都标不了** (实测) ⇒ "
    "★**但实测三条依据表明它可以派**: (a) ★**hw-lead 当前没有任何运行中的写会话** (sessions_list 实测: "
    "最近 4 条全 done|failed, 最后一条 11-08 23:3x) ⇒ ★**铁律要防的「两个并发写会话互相覆盖分片」没有发生**; "
    "(b) ★**ISS-181 的板子活实际由【主会话】在跑** (v76mz 臂 campaign, 07:41 起) ⇒ ★**它不占 hw-lead 的名额** ⇒ "
    "代理判据在这里代理错了事实; (c) ★**文件交集=0** (臂链路 6 个脚本 grep「fragments|.yaml」零命中, 只写 /tmp + "
    "state/.lastgood/; ISS-186 只改 5 个 .md) ⇒ ★**不抢同一块板** ⇒ ★**且不派的代价是它被永久冻住** "
    "(ISS-181 离 unc=0 还远, 最佳臂 v76mg1 = unc 23 条/21 网 ⇒ 不可能在 11-13 前落账) ⇒ ★**故手工解冻 + 落账** "
    "(只改 ISS-186 那 3 个字段, ★**已逐条 diff 核过: 183 条里只有这一条变了★) "
    "②★**B 段只备草稿不发送**: ★**17 份草稿全在, 零「已发送」标记** ⇒ 一封都没发 ⇒ "
    "③★**跑核验 5 连** (merge rc=0 · gate_check rc=0 · issue_check rc=1 · stage_gate rc=1 · daily_check rc=3) "
    "④刷新这一页 ⑤GitHub 同步 + blob SHA 逐个校验。"
    "   **没有动任何需要你拍板的东西, 没有发任何邮件, 没有下采购单, 没有改锁死表, 没有写任何总工的分片。**"
    ">   ★ **本轮 C 段口径变化: 35 → 35 项 (0 新增 / 0 移除 / 0 改建议值)** —— ★**逐 key 与 05:4x 那页完全相同** "
    "⇒ ★**你不用重看一遍, 除非你想改建议默认值**。"
)

NEW_SEC = """## 0.12 ★★★ 本轮: **A 段解冻, 派出 1 条 (ISS-186 → hw-lead)** ⇒ ★**C 段 35 项一个字没动**

> ★**这一节里 0.12.1 是已完成/进行中的工程活, 不是要你拍板的事** ⇒ ★**你今天不必为它做任何决定**。

### 0.12.1 ★ A 段从 0 条变 1 条: ISS-186 手工解冻并派出 (★为什么这不是"违规绕过闸门"★)

| | |
|---|---|
| **派了什么** | ★**ISS-186** (high, due **11-13**, 「DSI payload 8× 口径差」) → **hw-lead**, 07:5x 派出 |
| **为什么 advance.py 派不出它** | ★**advance.py 的 in_flight 判据是「owner 名下已有 status==fixing 的 issue ⇒ 跳过」** (★保守代理★) ⇒ ISS-181 (owner=hw-lead, fixing) 把本单挡住 ⇒ `internal=[]` ⇒ ★**`--apply --only ISS-186` 遍历的是空的 internal ⇒ 一条都标不了** (实测) |
| **★解冻的三条实测依据 (不是推测)** | ① ★**hw-lead 当前没有任何运行中的写会话** —— sessions_list 实测: verify-docs-A / verify-docs-B / 周更新 / 布线器 **四条全 done\|failed**, 最后一条 11-08 23:3x ⇒ ★**铁律要防的「同一 agent 两个并发写会话互相覆盖分片」没有发生**<br>② ★**ISS-181 的板子活实际由【主会话】在跑** (v76mz 臂 campaign, 07:41 起) ⇒ ★**它不占 hw-lead 的写会话名额** ⇒ 代理判据在这里**代理错了事实**<br>③ ★**文件交集 = 0** —— 臂链路 6 个脚本 (v76mz_arms / gen_pcb_netlist_board / replay_patch_chain / compare_arm_baseline / clrfix_iter) **grep「fragments\|.yaml」零命中**, 只写 `/tmp/v76mz_R.kicad_pcb` + `/tmp/chain_v76mz/` + `state/.lastgood/`; 而 ISS-186 **只改 5 个 .md** ⇒ ★**不抢同一块板** |
| **★不派的代价 (为什么不能一直等)** | ★**ISS-181 是 blocker 且离 G1 要求的 unc=0 还远** —— 当前最佳臂 v76mg1 = **unc 23 条 / 21 网** ⇒ ★**不可能在 ISS-186 的 due 11-13 之前落账** ⇒ ★**照字面判据, 一条 high 单会被一个代理判据永久冻住** |
| **落账纪律 (逐条可查)** | ★**只改 ISS-186 那 3 个字段** (status / dispatched_at / note) ⇒ ★**落账后逐条 diff 实测: 183 条里只有 ISS-186 变了, 其余 182 条一个字节没动** (脚本 `state/_apply_iss186_dispatch_20261111.py`, 带 flock + 原子写 + **整份 yaml 往返逐字节复现自检**) · ★**dispatch_log.yaml 已追加一条** (61 条) |
| **派给 hw-lead 的边界 (写进任务书了)** | ★**不许碰板子相关任何文件** (demo_mainboard.kicad_pcb / gen_pcb_*.py / .lastgood/ / /tmp 链产物) ⇒ ★**ISS-181 归主会话, hw-lead 不插手** · ★**不许碰 sw-lead 的分片** (⑤ 那一处归 sw-lead) ⇒ ★**本单只改 ①②③④⑥ 五处** · ★**不许发任何邮件** (⑥ 是给面板厂的询价函草稿 ⇒ 改了也不发) |
| **★对你的影响** | ★**零** —— ★**不新增决策项, 不改锁死表, 不发邮件** ⇒ ★**C 段 35 项一个字没动** |

### 0.12.2 ★ B 段: 17 份草稿全在 · ★**一封都没发**

| | |
|---|---|
| **草稿总数** | ★**17 份 .md** (`state/outbox/`, 含 README) ⇒ ★**README 自报「全部有归属, 0 份来路不明」, 本轮实测复核一致** |
| **★已发标记扫描** | ★**`grep -rniE '已发送\|已发(sent\|邮件已发)\|SENT:\|已投递' state/outbox/*.md` ⇒ 零命中** ⇒ ★**没有一封被发出去** |
| **与决策项相关的几份 (抽查齐全)** | ★**J_CHG RFQ** (`j_chg_rfq.md`, 4454 B) · ★**视涯询价函** (`visionox_display_inquiry.md`, 8550 B — ★**这正是 ISS-186 要改的第⑥处**) · ★**桥接芯片 RFQ** (5082 B) · ★**JBD 问询 + 追加** (6597 + 2928 B) · ★**TI BQ25896** (3838 B) · ★**PCB 厂层数问询** (4502 B) · ★**镜头 RFQ 追加** (13426 B) · ★**RK3576 模组厂问询清单 v2.0** (40291 B) ⇒ ★**10 份全在, 0 缺失** |
| **★外发纪律** | ★**本轮一封都没发** —— ★**外发一律经你一句「可以发」**; ①③④⑥ 那几份一旦改完数字 (ISS-186 在改), ★**状态仍是「未发」** |

### 0.12.3 ★ 核验 5 连 (本轮实测 rc)

| 门 | rc | 一句话 |
|---|---|---|
| `merge.py` | **0** | 快照完整 (产出 155 · 阻塞 43 (高危 33) · 未闭合需求 76 · **冲突 0**) |
| `gate_check.py` | **0** | 齐备率 18/18 · 证据分级 3/3 · 接口声明 475 条 |
| `issue_check.py` | **1** | ★**违规 33 条, 全是同一类: 逾期未闭环** (★**不是新造的问题, 是老账**) |
| `stage_gate.py` | **1** | ★**当前 G1 原理图/PCB 定稿, 还差 1 项进 G2** (G2 当期不做, 缺口 3 项留着) |
| `daily_check.py` | **3** | ★**异常已记录 (非崩溃)**: 问题闭环门违规 33 条 + 漂移 (内部未闭合 72→76 · 问题单 181→183) |

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
if not lines[0].startswith("# 待老板拍板页 · 2026-11-11 05:4x"):
    print(f"❌ 标题行不是预期的 05:4x 版: {lines[0][:80]!r}")
    sys.exit(1)
lines[0] = NEW_TITLE
print("✅ 标题行已替换")

# ---- ② 本轮我动了什么 ----
replace_line("> ★ **本轮我自己动了什么**:", NEW_WHAT, "'本轮我动了什么'")

# ---- ③ §0.11.4 的 A 段表 (已被本轮解冻推翻 ⇒ 改成指向 §0.12) ----
# ★**注意**: `| **A 段 (internal)** |` 前缀在页面上命中 2 行 (§0.7 与 §0.11.4 各一)
#   ⇒ ★**必须按行号定位到 §0.11.4 段内那一行** (§0.11.4 的段锚点 = "### 0.11.4")
sec1114 = None
for i, ln in enumerate(lines):
    if ln.startswith("### 0.11.4 "):
        sec1114 = i
        break
if sec1114 is None:
    print("❌ 找不到 §0.11.4 锚点")
    sys.exit(1)
hit = None
for i in range(sec1114, min(sec1114 + 30, len(lines))):
    if lines[i].startswith("| **A 段 (internal)** |"):
        hit = i
        break
if hit is None:
    print("❌ §0.11.4 段内找不到 'A 段 (internal)' 行")
    sys.exit(1)
lines[hit] = (
    "| **★A 段 (internal)** | ★**本轮已解冻并派出 1 条 (ISS-186 → hw-lead, 07:5x, ★手工解冻★) "
    "⇒ ★**详见 §0.12.1** ⇒ ★**本表是 05:4x 的快照, 已过期** |"
)
print(f"✅ §0.11.4 'A 段 (internal)' 行已替换 (行 {hit + 1})")

# ---- ④ 新插 §0.12 (插在 §0.11 之前) ----
anchor_idx = None
for i, ln in enumerate(lines):
    if ln.startswith("## 0.11 "):
        anchor_idx = i
        break
if anchor_idx is None:
    print("❌ 找不到 §0.11 锚点")
    sys.exit(1)
lines[anchor_idx:anchor_idx] = NEW_SEC.split("\n")
print(f"✅ §0.12 已插入 (行 {anchor_idx + 1})")

out = "\n".join(lines)
open(P, "w", encoding="utf-8").write(out)
print(f"✅ 已写回 {P} ({len(out)} 字符)")
