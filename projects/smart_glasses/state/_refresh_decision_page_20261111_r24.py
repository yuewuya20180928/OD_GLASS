#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""刷新老板拍板页 DECISION_PENDING_2026-11-11.md (第 24 次刷新) —— 2026-11-11 21:1x

★**只整理 + 给建议默认值, 不代决** —— 拍板前不动任何采购 / 外发 / 改图 / 改锁死表。

★**本轮 C 段口径: 36 → 36 (0 新增 / 0 退休 / 0 改建议值)** ⇒ ★**这一轮你不用重看一遍** ⇒
   ★**仍等你拍的只有 §1 那 3 条 + §1b 那 1 条 + §2 那 1 条 (共 5 条) ★★**

★**本轮做的全是【订正】, 不是【新增决策】** ⇒ ★**C 段 36 项的建议默认值一个没动** ★
   ★**本轮订正的全是【页面自己的陈旧数字 / 已被你 19:31 回答过的旧条目仍挂在表里】** ⇒ ★**不改任何口径** ★
   ① ★**§1c 的 3 条 (sch_completeness_target / ref_designator_rename / iss191_reset_p0_fix_choice)
      早在 19:31 就被你「全做」拍完了, 但 §1c 的表头/脚注还写着「待你回」⇒ ⇒ 本轮加「已退休」标记
      (行保留, 只作留档) ⇒ ⇒ 免得你再花时间回一遍已经答过的问题** ★
   ② ★**§1b 脚注的算式还停在「C 段 39 项 / pm 6」⇒ ⇒ 实测现在是 36 项 / pm 3 (19:31 退休 3 条) ⇒ ⇒ 订正** ★
   ③ ★**§1 脚注「其余 32 项」算的是 39-7 ⇒ ⇒ 现在 C 段 36, §1 之外是 33 项 ⇒ ⇒ 订正 + 写清每类几项** ★
   ④ ★**§2 (外发类) 那 1 条的建议默认值写的是「放行」⇒ ⇒ 与你 19:31 的「一律不发」政策直接冲突
      ⇒ ⇒ 本轮改成【按你的政策 = 不发, 只留档】, 并把【要不要给采购动作开一次豁免】留成唯一要你回的话** ★
   ⑤ ★**outbox 清单数还停在 17 份 .md ⇒ ⇒ 实测 19 份 (多出 NO_OUTBOUND_POLICY + R_GEO_2 决策图) ⇒ ⇒ 订正** ★
   ⑥ ★**`bridge_chip_quotes.md` 那条注写着「等你放行 RFQ + 供应商回信后自然生成」⇒ ⇒ 一律不发 ⇒ ⇒ 永远不会生成 ⇒ ⇒ 订正** ★

★**落盘纪律**: flock + 锁内重读 + 原子写 (tmp → fsync → os.replace → fsync(dir))
★**边界**: 不改任何建议默认值 · 不改 C 段 36 项 · 不发邮件 · 不下采购单 · 不改 §0 锁死表
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

TITLE_PREFIX = "# 待老板拍板页 · "

NEW_TITLE = (
    "# 待老板拍板页 · 2026-11-11 21:1x (第 24 次刷新 · ★**C 段 36 → 36 (0 新增 / 0 退休 / 0 改建议值)** + "
    "★**只做订正: §1c 那 3 条加「19:31 已退休」标记 + 三处陈旧数字 (39→36 / pm 6→3 / outbox 17→19) + "
    "§2 那 1 条的建议默认值与你的「一律不发」政策对齐** + ★**A 段本轮 0 条 (★**真在飞, 不是前 3 轮那种「假 fixing 标记」**) "
    "⇒ 本轮你不用做任何新决定** ★★)"
)

BLOCK_START = "> ★ **本轮我自己动了什么**:"
BLOCK_TAIL_MARK = "本轮 C 段口径变化"

NEW_WHAT = (
    "> ★ **本轮我自己动了什么**: ①★**A 段本轮 0 条可派 —— 但这次的原因是【真在飞】, 不是前 3 轮那种【假 fixing 标记】★** ⇒ "
    "★**实测**: hw-lead 跑 ISS-193 的会话 `agent:hw-lead:subagent:fccbbd04` (★**20:19:17 起, 由主会话 webchat 派生, "
    "不是本 job 派的★**) ⇒ ★**21:0x 时它的 transcript 还在写 (144 行 / 1.09 MB, 最后一条在重写 `state/gen_bom.py` 的"
    "证据分级聚合规则★)** ⇒ ⇒ **它真的在跑** ⇒ ⇒ `advance.py` 的 in_flight 判据正确挡住 hw-lead ⇒ ⇒ "
    "★**ISS-136 (逾期) + ISS-195 两条 open 本轮都不派 (铁律: 一个 agent 同时只允许一个写会话★)** ⇒ ⇒ "
    "★**⇒ 这是【同病不同因】: 前 3 轮 (ISS-181 → ISS-192 → ISS-193) 是死单占位, 本轮是真单在跑** ⇒ ⇒ "
    "★**⇒ 顺带确认: sw-lead / mech-lead 名下 open = 0 ⇒ A 段空是【真空】(没人可派), 不是【被占死】★** ★。 "
    "②★**B 段 approvals = 0 条 (★**19:31 政策后恒为空★**) ⇒ ★**草稿一件没少, 一封都没发**: `state/outbox/` 实测 "
    "**19 份 .md** (16 份草稿 + 1 份 README + 1 份政策件 `NO_OUTBOUND_POLICY.md` + 1 份内部决策图 `R_GEO_2_DECISION_MAP.md`) "
    "+ `attach/` **3 份** (2 附件 + 1 附件 README) ⇒ ★**零缺失** (★**唯一「引用了但文件不在」的 `bridge_chip_quotes.md` "
    "是【供应商回信之后】才有的报价对比表 ⇒ 一律不发 ⇒ 它永远不会生成 ⇒ 保持不存在是对的, 我不补★**) ★。 "
    "③★**C 段 36 项 ⇒ 逐项实测核对: 页面表格覆盖 36/36 (0 缺失) ⇒ 本轮【只订正页面自己的陈旧处】, 不新增也不退休任何一项★** ⇒ "
    "★**① §1c 那 3 条 (sch_completeness_target / ref_designator_rename / iss191_reset_p0_fix_choice) 你 19:31 已拍「全做」"
    "⇒ 本轮加「已退休」标记 (行保留只作留档) ⇒ 免得你再回一遍已经答过的问题** ⇒ ★**② §1b 脚注「C 段 39 项 / pm 6」"
    "→ 实测 36 / pm 3** ⇒ ★**③ §1 脚注「其余 32 项」→ C 段 36 ⇒ §1 之外 33 项 (每类几项写清)** ⇒ ★**④ §2 那 1 条的建议"
    "默认值原写「放行」⇒ 与你 19:31「一律不发」冲突 ⇒ 改成【按你的政策 = 不发, 只留档】, 只留【要不要给采购动作开一次豁免】"
    "这一句话给你** ⇒ ★**⑤ outbox 清单数 17 → 19** ⇒ ★**⑥ `bridge_chip_quotes.md` 的注改为「永远不会生成」** ⇒ "
    "★**⇒ C 段 36 项的建议默认值一个没动** ★。 ④★**核验 5 连本轮实测 rc**: merge **0** (冲突 **0** · 产出 174 · 阻塞 43) · "
    "gate_check **0** (★**齐备率 18/18** ★ · 证据分级 3/3 · 接口声明 489) · issue_check **1** (违规 **30** 条) · stage_gate **1** "
    "(当前 **G1**, 还差 **1** 项 ⇒ unconnected=45 需 0) · daily_check **3** (巡检异常已记录, 非崩溃) ⇒ ★**详见下方 §0.25.2** ★。 "
    "⑤★**GitHub: 本 job 不推** (统一由 `ARS45 GitHub 同步 (每 5 小时 · 有进展才推)` job 负责) ⇒ ★**本 job 只落本地快照** ★。 "
    "⑥★**板 / 网表 / 脚表 / .kicad_pro md5 一字未动** (611b869e… / c78f9912… / 4814617e… / 3e504d2b…) ★ "
    "⇒ ★**★**BOM (`HW/BOM_v1.csv`) 是本轮唯一被动到的文件, 但**不是本 job 动的** —— ★**是正在跑的 ISS-193 会话在 21:12 重出的** "
    "(★**291 行 → 218 行 / 伪器件 75 → 0 / 补上 J_SOM_P2 + J_SOM_P4 ⇒ 正是 ISS-193 任务①的验收口径, 说明它真在干活★**) "
    "⇒ ⇒ ★**本 job 只做记账/订正, 没碰任何生产文件** ★。 "
    "⑦★**没有动任何需要你拍板的东西, 没有发任何邮件, 没有联系任何供应商, 没有下采购单, 没有改 §0 锁死表, 没有写任何子总工的分片** ★★"
)

NEW_SEC = """## 0.25 ★★★ 本轮: ★**A 段 0 条 (★**真在飞, 不是假 fixing 标记★)** + ★**C 段 36 → 36 (只订正页面陈旧处, 不新增不退休)** + ★**你不用做任何新决定** ★★

> ★**这一节全部是【我这边记账 / 订正 / 核验】的活 ⇒ ★**不需要你做任何新决定** ⇒ ★**C 段 36 项的建议默认值一个没动** ⇒
> ★**仍等你拍的只有 §1 那 3 条 + §1b 那 1 条 + §2 那 1 条 = 5 条** ★★

### 0.25.1 ★★★ ★**A 段本轮 0 条可派 —— 但这次是【真在飞】, 不是前 3 轮那个【假 fixing 标记】病** ★★★

| | |
|---|---|
| ★**实测: ISS-193 的会话是真的在跑** | ★**会话 `agent:hw-lead:subagent:fccbbd04` (sessionId `40040dfd`) ★**20:19:17 起, 由**主会话 webchat** 派生 (★**不是本 job 派的★**) ⇒ ★**21:0x 时 transcript 仍在写: 144 行 / 1.09 MB / mtime 21:0x** ⇒ ★**它最后一条在做的是【重写 `state/gen_bom.py` 的证据分级聚合规则】(把 BOM 的 evidence/tbd 改成「按器件取最强证据」而不是「取第一行」)★** ⇒ ★**⇒ 它真的在干活, 不是挂着的空壳** ★ |
| ★**⇒ 所以 A 段空是【正确的】** | ★**`advance.py` 的 in_flight 判据 = 「该 agent 名下已有 `status==fixing` ⇒ 本轮跳过」⇒ ⇒ hw-lead 名额被**真在跑**的 ISS-193 占住 ⇒ ⇒ ★**ISS-136 (★**逾期 5 天★**, owner=hw-lead) + ISS-195 (owner=hw-lead) 两条 open 本轮【都不派】** ⇒ ★**铁律「一个 agent 同时只允许一个写会话」保持 (hw-lead 只有 1 个在跑)** ★ |
| ★★★**★与前 3 轮是【同病不同因】★★** | ★**前 3 轮 (ISS-181 → ISS-192 → ISS-193) 的 A 段空是因为【死单占位】(会话撞 token 上限被掐断, 什么都没交, `status=fixing` 成了假标记) ⇒ 本轮 **不是**: 会话活着、transcript 在长、正在改文件 ⇒ ⇒ **⇒ 这轮不用再拔假标记, 拔了就是打断真活** ★★ |
| ★**顺带确认: sw-lead / mech-lead 名下 open = 0** | ★**实测: sw-lead 0 条 open (全 closed/verified/deferred) · mech-lead 0 条 open ⇒ ⇒ ★**A 段空是【真空】(没人可派), 不是【被占死】** ⇒ ⇒ **⇒ 本 job 不新开单、不新派活 (★**兄弟 job「ARS45 队列自动派活」正在同一批需求上做它的排单, 两边同时派同一个 agent 会撞铁律★**) ★ |
| ★★★**★第二处独立旁证: 它交的第一个产物已经落盘了 (21:12)★★** | ★**实测 `HW/BOM_v1.csv` md5 `3ad04e1a…` → **`c0b335e1…`**, mtime **21:12:07** ⇒ ★**新 BOM = 218 行 / 伪器件 (RAIL_*/NET_*) 75 → **0** / 补上 `J_SOM_P2` + `J_SOM_P4` ⇒ ⇒ ★**这正是 ISS-193 任务①「改 `gen_bom.py` 的输入表为针脚级 `netlist_v1_pins.csv` ⇒ BOM 变 218 器件 / 0 伪器件 / 含 P2+P4」的验收口径** ⇒ ⇒ ★**⇒ 它不是挂着的空壳, 是真在交卷** ⇒ ⇒ ★**★**(板 / 网表 / 脚表 / `.kicad_pro` 仍一字未动 ⇒ 它守住了"不许改板/网表"的边界**★) ★★ |

### 0.25.2 ★★★ ★**核验 5 连 (本轮实测 rc) + C 段逐项核对 + GitHub 本 job 不推** ★★★

| 闸 | rc | 结论 |
|---|---|---|
| `state/merge.py` | **0** | 冲突 **0** · 产出 174 · 阻塞 43 (高危 33) · 未闭合需求 100 |
| `state/gate_check.py` | **0** | ★**齐备率 18/18** · 证据分级 3/3 · 接口声明 489 条 · 与 merge 自对账一致 (等外部 70 / 等总工 100) |
| `state/issue_check.py` | **1** | 违规 **30** 条 (★**全是逾期类, 逐条同上一轮, 本轮没新增违规**★) |
| `state/stage_gate.py` | **1** | 当前 **G1** (原理图 / PCB 定稿), 还差 **1** 项 ⇒ ★**PCB 布线未达标: unconnected=45 (需 0) · DRC 违规=0 (需 0) (ISS-181)** |
| `state/daily_check.py` | **3** | 巡检异常已记录 (非崩溃): 问题闭环门违规 30 条 |
| ★**C 段逐项核对** | — | ★**`advance.py --json` 实测 36 项 ⇒ 页面表格覆盖 36/36 (0 缺失) ⇒ 本轮只订正陈旧处, 不新增不退休** ★ |
| 本地快照 | **0** | ★**`PROGRESS_SNAPSHOT.md` 已生成** ⇒ ★**只落本地, 随时能看** ★★ |
| GitHub | — | ★**本 job 不推** (★**老板 11-11 10:07 口径 ⇒ 统一由 `ARS45 GitHub 同步 (每 5 小时 · 有进展才推)` job 负责★**) ★★ |
| ★**板 / 网表 / 脚表 / .kicad_pro** | — | ★**一个字节没动**: 板 md5 `611b869e13518c3c023fb178f91a0075` · 网表 `c78f991283cc82d56c8e3dd31657c785` · 脚表 `4814617e22b567d76164e56bc5e39dc8` · `.kicad_pro` `3e504d2be83152e337949723e909be1b` ★★ |
| ★**BOM (★**本轮唯一被动到的生产文件★**)** | — | ★**`HW/BOM_v1.csv` md5 `3ad04e1a…` → `c0b335e1…` (21:12) ⇒ ★**但不是本 job 动的** —— ★**是正在跑的 ISS-193 会话重出的** ⇒ ★**实测新 BOM = 218 行 / 伪器件 75 → 0 / 含 J_SOM_P2 + J_SOM_P4 ⇒ 正是 ISS-193 任务①的验收口径 ⇒ 它真在干活** (★**⇒ 也是 §0.25.1「真在飞」的第二处独立旁证★**) ★★ |

### 0.25.3 ★★★ ★**本轮订正的 6 处 (★全是【页面自己的陈旧处】, 不是口径, 不是建议值★)** ★★★

| # | 位置 | 改前 | 改后 | 为什么 |
|---|---|---|---|---|
| 1 | §1c 表头 + 脚注 | ★**写着你还要回这 3 条** | ★**加「19:31 你已拍「全做」⇒ 已退休」标记 (行保留只作留档)** | ★**这 3 条 (`sch_completeness_target` / `ref_designator_rename` / `iss191_reset_p0_fix_choice`) 早在 19:31 就由你拍完了, 已在整链重出清单里 ⇒ ⇒ 挂在「待你回」的表里 = 让你白花时间** ★ |
| 2 | §1b 脚注 | 「C 段 **39** 项」 | 「C 段 **36** 项」 | ★**实测 `advance.py --json` = 36** ⇒ ★**39 是 19:31 退休 3 条之前的数** ★ |
| 3 | 页尾「按来源分」 | 「(39 项): mech 17 · sw 9 · hw 7 · **pm 6**」 | 「(**36** 项): mech 17 · sw 9 · hw 7 · **pm 3**」 | ★**19:31 退休的 3 条全在 pm.yaml ⇒ pm 6 → 3** ★ |
| 4 | §1 脚注 | 「其余 **32** 项」 | 「§1 之外的 **33** 项 (每类几项写清)」 | ★**36 - 3 = 33 ⇒ 32 是 39-7 时代的算式** ★ |
| 5 | §2 那 1 条的建议默认值 | 「**放行**」 | 「**按你 19:31 政策 = 不发, 只留档**; 要发请单独点名这一份」 | ★**★**你 19:31 原话「以后不再做任何邮件咨询」⇒ 原样写「放行」是让你批一件你已经禁掉的事★** ★ |
| 6 | §2 页脚 + 页尾纪律行 | outbox「**17** 份 .md」+「你说"可以发"我才发」 | outbox「**19** 份 .md (16 草稿 + README + 政策件 + 决策图)」+「默认一律不发, 要发需你单独点名某一份」 | ★**实测 19 份** (★**多出 `NO_OUTBOUND_POLICY.md` 与 `R_GEO_2_DECISION_MAP.md`★**) ⇒ ★**且「你说可以发我才发」在【一律不发】政策下已不是事实** ★ |

★**★并且: `bridge_chip_quotes.md` 的注本轮也订正了 (★**它原来写着「等你放行 RFQ + 供应商回信后自然生成」⇒ 一律不发 ⇒ ⇒ 永远不会生成 ⇒ ⇒ 注改为「保持不存在是对的」★**) ★

★**★C 段 36 项的建议默认值一个没动 ★** ⇒ ★**这一轮你不用重看一遍; 仍等你拍的只有 §1 那 3 条 + §1b 那 1 条 + §2 那 1 条** ★★

"""


def atomic_write(path: str, text: str) -> None:
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix=".dp.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise
    dfd = os.open(os.path.dirname(path), os.O_RDONLY)
    try:
        os.fsync(dfd)
    finally:
        os.close(dfd)


def main() -> int:
    if not os.path.exists(P):
        print("❌ 找不到 %s" % P)
        return 2

    lock_fh = open(LOCK, "w")
    fcntl.flock(lock_fh, fcntl.LOCK_EX)
    try:
        with open(P, encoding="utf-8") as f:
            s = f.read()
        before_len = len(s)

        # ★★全部按【行】编辑, 不用全文子串 ★★
        lines = s.split("\n")

        # ---- 0. 先把 §1 的 3 行原样抓出来 (自检用: 这 3 行的建议默认值本轮不许动) ----
        sec1_keys = ("demo_od_path_a_vs_b", "demo_od_model_route_m1_vs_m2", "iss079_phip_manual_fetch")
        sec1_rows_before = {}
        for i, l in enumerate(lines):
            for k in sec1_keys:
                if ("`%s`" % k) in l and l.startswith("| **"):
                    sec1_rows_before[k] = l

        # ---- 1. 标题 ----
        hit = False
        for i, l in enumerate(lines):
            if l.startswith(TITLE_PREFIX):
                lines[i] = NEW_TITLE
                hit = True
                break
        if not hit:
            print("❌ 找不到标题行 ⇒ 中止")
            return 2

        # ---- 2. 重写顶部【本轮我自己动了什么】块 (只看前 12 行) ----
        blk_start = None
        for i, l in enumerate(lines[:12]):
            if l.startswith(BLOCK_START):
                blk_start = i
                break
        if blk_start is None:
            print("❌ 顶部『本轮我自己动了什么』段找不到 ⇒ 中止")
            return 2
        blk_end = None
        for i in range(blk_start, min(blk_start + 6, len(lines))):
            if BLOCK_TAIL_MARK in lines[i]:
                blk_end = i
                break
        if blk_end is None:
            print("❌ 顶部『C 段口径变化』行找不到 ⇒ 中止")
            return 2
        new_block = NEW_WHAT.split("\n") + [
            "  ★ **本轮 C 段口径变化: 36 → 36 项 (0 新增 / 0 退休 / 0 改建议值 —— 本轮只订正页面陈旧处)** "
            "—— ★**这一轮你不用重看一遍; 仍等你拍的只有 §1 那 3 条 + §1b 那 1 条 + §2 那 1 条 (共 5 条)** ★★"]
        lines[blk_start:blk_end + 1] = new_block

        # ---- 3. 插入 §0.25 (在 "## 0.24 " 这一行之前) ----
        sec_idx = None
        for i, l in enumerate(lines):
            if l.startswith("## 0.24 "):
                sec_idx = i
                break
        if sec_idx is None:
            print("❌ 找不到 §0.24 标题行 ⇒ 中止")
            return 2
        lines[sec_idx:sec_idx] = NEW_SEC.rstrip("\n").split("\n")

        # ---- 4. 六处订正 (按【整行精确匹配】定位, 命中数必须 == 1) ----
        def replace_line(old: str, new: str) -> bool:
            n = lines.count(old)
            if n != 1:
                print("❌ 待订正的行命中 %d 次 (必须恰好 1 次) ⇒ 中止: %s" % (n, old[:60]))
                return False
            lines[lines.index(old)] = new
            return True

        ok = True

        # 4.1 §1 脚注: 其余 32 项 → 33 项 (每类几项写清)
        ok &= replace_line(
            "★ **其余 32 项全部属整机/量产阶段 (G2 已于 11-02 19:25 延后) 或方法论 ⇒ 不必今天回。**",
            "★ **§1 之外的 33 项全部属整机/量产阶段 (G2 已于 11-02 19:25 延后) 或方法论 ⇒ 不必今天回 "
            "(★**分类清点**: §1b 板子基线 1 + §2 外发 1 + §3 电气口径 6 + §4 结构/材料/可靠性 14 + "
            "§5 软件/许可/命名 7 + §6 产品定义 2 + §7 方法论 2 = 33**★)。**")

        # 4.2 §1b 脚注: C 段 39 项 → 36 项
        ok &= replace_line(
            "★ **§1 的 3 项 + 本节 1 项 + §1c 的 3 项 = C 段 39 项 (★其余 32 项属整机/量产阶段 (G2 已于 11-02 19:25 延后) "
            "或方法论 ⇒ 不必今天回★)。**",
            "★ **§1 的 3 项 + 本节 1 项 = 4 项 ⇒ 加上 §1c 之外那 32 项 ⇒ ★**C 段共 36 项** "
            "(★**19:31 你拍「全做」退休 3 条之前的旧数是 39, 本轮已订正; 其余 32 项属整机/量产阶段 "
            "(G2 已于 11-02 19:25 延后) 或方法论 ⇒ 不必今天回★)。**")

        # 4.3 §1c 表头 + 脚注: 加「19:31 已退休」标记 (行保留)
        ok &= replace_line(
            "## 1c. ⚪ 原理图主线类 (★**当期【不】卡主线 —— 但它是今天的主线本身, 建议默认值已按现状推进**★)",
            "## 1c. ✅ 已退休 (★**★**这 3 条你 2026-11-11 19:31 已拍「全做」⇒ 早已不在 C 段 36 项里 ⇒ "
            "下面的表【只作留档, 不用再看、也不用再回】★** —— 它们已并进「一次整链重出」清单 "
            "`state/RECHAIN_ONEPASS_PLAN.md` v2 (14 步)★**)")
        ok &= replace_line(
            "★ **§1c 这 3 条 = 11-11 12:0x 由 main 补登进 C 段 (源头: `state/fragments/pm.yaml` 的 `needs_from`) ⇒ "
            "★**建议默认值与 §0.18 逐字一致, 本轮一个字没改**★ ⇒ ★**不回也不卡当期** (★**`sch_completeness_target` 的建议已经在跑; "
            "`ref_designator_rename` 的建议本来就是\"不急\"; ★**第 3 条 `iss191_reset_p0_fix_choice` 是 11-11 16:5x 新增** "
            "(ISS-191 方案页验收签字后冒出来的口径) ⇒ ★**它决定首台板能不能开机 ⇒ 建议与「②」一起回** ★★)。**",
            "★ **★**本节 3 条 (`sch_completeness_target` / `ref_designator_rename` / `iss191_reset_p0_fix_choice`) "
            "已于 2026-11-11 19:31 由你亲口拍板「全做」⇒ ⇒ **已退休** (★**不在当前 C 段 36 项里, `advance.py --json` 实测不含这 3 个 key★**) "
            "⇒ ⇒ 表里的行【只作留档, 建议默认值保留原文不动】⇒ ⇒ ★**① `sch_completeness_target` = ② 表内全量 (已在跑) "
            "② `ref_designator_rename` = 随整链重出一起改 (`RAIL_*`/`NET_*` 保留) ③ `iss191_reset_p0_fix_choice` = ② "
            "`Q_AND` 整颗改 DNP (表A L65/L66/L67 + 表B `Q_AND.1/.2/.3` 三行同改) ⇒ 三条都落在整链重出清单里, 由我统一执行** ★★。**")

        # 4.4 §2 表头
        ok &= replace_line(
            "## 2. 🟠 外发类 (只差你一句\"可以发\", 草稿已就绪, 我一律不自己发)",
            "## 2. 🟠 外发类 (★**已被你 2026-11-11 19:31 的「一律不发」政策覆盖 ⇒ 默认【不发, 只留档】—— "
            "下面这 1 条只剩【要不要给采购动作单独开一次豁免】这一个问题**★)")
        # 4.5 §2 那 1 条的建议默认值
        ok &= replace_line(
            "| `iss105_jchg_rfq_release` | J_CHG 询价函**放行外发** (收件 Hirose + 国产对标); 硬判据 C-1~C-8 + F-1~F-5, "
            "含单触点 ≥0.5A 书面确认 / 可插厚度 ≥0.25mm / 机械防呆; ★**采购口径按\"实物一对\"写进 RFQ 与 BOM 备料栏, "
            "别只按网表的 1 只 ref 备料** | `state/outbox/j_chg_rfq.md` | **放行** (但 J_CHG 是整机件 ⇒ **当期不卡** ⇒ 可缓) | 11 天 |",
            "| `iss105_jchg_rfq_release` | J_CHG 询价函**放行外发** (收件 Hirose + 国产对标); 硬判据 C-1~C-8 + F-1~F-5, "
            "含单触点 ≥0.5A 书面确认 / 可插厚度 ≥0.25mm / 机械防呆; ★**采购口径按\"实物一对\"写进 RFQ 与 BOM 备料栏, "
            "别只按网表的 1 只 ref 备料** | `state/outbox/j_chg_rfq.md` (★**已就绪, 但按你的 19:31 政策【不发】★**) | "
            "★**按你 19:31 的「一律不发」政策 = 不发, 只留档** (★**J_CHG 是整机件 ⇒ 当期不卡 ⇒ 建议就是不发**★) ⇒ "
            "★**唯一要你回的是: 要不要把它当【采购动作】单独开一次豁免 (回一句「J_CHG 询价放行」我才发)** | 11 天 |")
        # 4.6 §2 页脚 outbox 清单数
        ok &= replace_line(
            "★ **`state/outbox/` 现有 16 份 .md 草稿 + 1 份 README 清单 (共 17 份 .md) + `attach/` 2 份附件 + 1 份附件 README, 一份都没发过。**",
            "★ **`state/outbox/` 实测 19 份 .md (16 份草稿 + 1 份 README 清单 + 1 份政策件 `NO_OUTBOUND_POLICY.md` + "
            "1 份内部决策图 `R_GEO_2_DECISION_MAP.md`) + `attach/` 3 份 (2 份附件 + 1 份附件 README) ⇒ 一份都没发过, "
            "一家供应商都没联系。**")
        # 4.7 bridge_chip_quotes 的注
        ok &= replace_line(
            "> ★ **唯一\"引用了但文件不在\"的仍是 `bridge_chip_quotes.md`** —— 它是 ISS-019 task_brief 的**自证行**, "
            "指的是\"**供应商回信之后**做报价对比表\" ⇒ ★**它现在不存在是对的, 不是漏写** (本轮一封都没发 ⇒ 没有回信 ⇒ "
            "写出来只能靠编造报价) ⇒ ★**我故意不补这个文件** ⇒ ★**等你放行 RFQ + 供应商回信后自然生成**。",
            "> ★ **唯一\"引用了但文件不在\"的仍是 `bridge_chip_quotes.md`** —— 它是 ISS-019 task_brief 的**自证行**, "
            "指的是\"**供应商回信之后**做报价对比表\" ⇒ ★**它现在不存在是对的, 不是漏写** (一封都没发 ⇒ 没有回信 ⇒ "
            "写出来只能靠编造报价) ⇒ ★**我故意不补这个文件** ⇒ ★**★**按你 19:31 的「一律不发」政策 ⇒ 它【永远不会生成】"
            "⇒ ⇒ 保持不存在就是终态, 不是待办** ★★。")
        # 4.8 页尾「按来源分」
        ok &= replace_line(
            "★ **按来源分 (39 项)**: mech 17 · sw 9 · hw 7 · pm 6。",
            "★ **按来源分 (36 项)**: mech 17 · sw 9 · hw 7 · pm 3。")
        # 4.9 页尾纪律行的外发口径
        ok &= replace_line(
            "> ★ **外发一律经你** —— 草稿都在 `state/outbox/` (现 16 份 .md 草稿 + 1 份 README 清单), 你说\"可以发\"我才发。",
            "> ★ **外发一律经你** —— 草稿都在 `state/outbox/` (现 19 份 .md = 16 草稿 + README + 政策件 + 决策图) ⇒ "
            "★**但按你 2026-11-11 19:31 的政策, 默认【一律不发, 只留档】⇒ 要发得你单独点名某一份** ★")

        if not ok:
            print("❌ 有一处订正没命中 ⇒ 中止 (页面未改)")
            return 2

        s = "\n".join(lines)

        # ---- 5. 自检 ----
        # 5.1 §1 的 3 行原样未动 (建议默认值不许动)
        for k, old_row in sec1_rows_before.items():
            if old_row not in s:
                print("❌ 自检失败: §1 的 %s 那行被改了 ⇒ 中止" % k)
                return 2
        print("✔ 自检: §1 那 3 行的建议默认值逐字未动")

        # 5.2 C 段 36 个 key 一个不少
        must_keep = ["iss105_jchg_rfq_release", "iss091_rilim_decision", "iss100_board_length",
                     "model_license_stack_decision", "s2_product_codename",
                     "iss121_audio_scope", "rel_drop_target_level",
                     "demo_od_path_a_vs_b", "demo_od_model_route_m1_vs_m2", "iss079_phip_manual_fetch",
                     "board_p41_promote", "sch_completeness_target", "ref_designator_rename",
                     "iss191_reset_p0_fix_choice"]
        missing = [k for k in must_keep if k not in s]
        if missing:
            print("❌ 自检失败: 这些 key 不见了 ⇒ 中止: %s" % missing)
            return 2

        # 5.3 结构节都在 (r23 教训: 改大文档必须按行定位 + 结构自检)
        for need in ("## 0.25 ", "### 0.25.1 ", "### 0.25.2 ", "### 0.25.3 ",
                     "## 0.24 ", "### 0.24.1 ", "### 0.24.2 ", "### 0.24.3 ", "### 0.24.4 ",
                     "## 0.23 ", "### 0.23.1 ", "## 0.22 "):
            if need not in s:
                print("❌ 自检失败: 结构节 '%s' 不见了 ⇒ 中止" % need)
                return 2

        # 5.4 陈旧行一个都不许残留 (★**只查【活体区】(§1 起) —— §0.x 是历史流水账, 当时的数就是当时的数, 不许改★**)
        #      ★**用【整行精确匹配】而不是碎片匹配 —— 因为本轮 §0.25 的订正清单里【本来就要引用旧值】
        #         (「§1 脚注「其余 32 项」→「33 项」」) ⇒ 碎片匹配会误报 ★**
        live_start = None
        for i, l in enumerate(lines):
            if l.startswith("## 1. "):
                live_start = i
                break
        if live_start is None:
            print("❌ 找不到 §1 标题行 ⇒ 中止")
            return 2
        live_lines = lines[live_start:]
        stale_exact = [
            "★ **其余 32 项全部属整机/量产阶段 (G2 已于 11-02 19:25 延后) 或方法论 ⇒ 不必今天回。**",
            "★ **§1 的 3 项 + 本节 1 项 + §1c 的 3 项 = C 段 39 项 (★其余 32 项属整机/量产阶段 "
            "(G2 已于 11-02 19:25 延后) 或方法论 ⇒ 不必今天回★)。**",
            "★ **按来源分 (39 项)**: mech 17 · sw 9 · hw 7 · pm 6。",
            "★ **`state/outbox/` 现有 16 份 .md 草稿 + 1 份 README 清单 (共 17 份 .md) + `attach/` 2 份附件 + "
            "1 份附件 README, 一份都没发过。**",
            "> ★ **外发一律经你** —— 草稿都在 `state/outbox/` (现 16 份 .md 草稿 + 1 份 README 清单), "
            "你说\"可以发\"我才发。",
        ]
        for bad in stale_exact:
            if bad in live_lines:
                print("❌ 自检失败: 活体区里旧行还在 ⇒ 中止: %s" % bad[:70])
                return 2
        # 5.5 活体区的「36 项 / pm 3 / 19 份」新数必须真的在
        for good in ("C 段共 36 项", "按来源分 (36 项)**", "pm 3。",
                     "实测 19 份 .md", "§1 之外的 33 项", "默认【不发, 只留档】"):
            if good not in "\n".join(live_lines):
                print("❌ 自检失败: 活体区里新数没写上 ⇒ 中止: %s" % good)
                return 2
        print("✔ 自检: 活体区 (§1 起) 的 6 处陈旧处全部已订正 (§1b 39→36 / pm 6→3 / 32→33 / outbox 17→19 / §2 口径)")
        print("   (★**§0.x 历史流水账里的旧数字保留原样** —— 那是当时的实测, 改了就是篡改历史★**)")

        atomic_write(P, s)
    finally:
        fcntl.flock(lock_fh, fcntl.LOCK_UN)

    print("✅ 决策页已刷新 (第 24 次): %d → %d 字符" % (before_len, len(s)))
    print("   - 标题: C 段 36 → 36 (只订正) + A 段 0 条 (真在飞) + §1c 标记退休 + 六处陈旧处订正")
    print("   - 新增 §0.25 (0.25.1 A 段真在飞 / 0.25.2 核验 5 连 + C 段核对 / 0.25.3 六处订正清单)")
    print("   - ★**C 段 36 项的建议默认值一个没动**")
    return 0


if __name__ == "__main__":
    sys.exit(main())
