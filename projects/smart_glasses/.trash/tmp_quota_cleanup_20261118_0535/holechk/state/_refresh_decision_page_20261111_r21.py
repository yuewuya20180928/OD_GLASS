#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""刷新老板拍板页 DECISION_PENDING_2026-11-11.md (第 21 次刷新) —— 2026-11-11 16:5x

★**只整理 + 给建议默认值, 不代决** —— 拍板前不动任何采购 / 外发 / 改图 / 改锁死表。

★**本轮 C 段口径: 38 → 39 (1 新增 / 0 移除 / 0 改建议值)** ⇒ ★**新增的那 1 条是【今天新冒出来的】,
   不是翻旧账 ⇒ ★**只有这一条需要你看, 其余 38 条一个字没动**。

★**本轮最实质的三件事 (★都是"记账/派活/核验"类 ⇒ 不需要你做任何新决定★)**:
  ★**① ISS-191 交卷并经 main 独立验收签字 (verified/pass)** ⇒ 方案页 `HW/PCB/RESET_P0_FIX_PLAN.md`
    已被我自己重跑 8 条闸 + ★**自己造反向用例** 证实 ⇒ ★**它给了你一条【新的、要拍的口径】** (= 下面新增的第 39 条)
    ⇒ ★**注意: 签字只覆盖【方案页交付】, 不覆盖【P0 实体修复】⇒ 首台板现在仍然起不来** ⇒ 未藏账。
  ★**② ISS-192 (mech-lead) 上一轮被 60 分钟上限掐断, 交零 ⇒ 假 `fixing` 标记 = ISS-181 同病第 2 次出现
    ⇒ ★**已复位成 `open` 并重派** (结构类, 不在老板 10:07 的【PCB 布线/布局 不派】名单里)。
  ★**③ A 段从 0 条变回 1 条** (ISS-192 → mech-lead) ⇒ ★**队列重新能派活了**。

★**落盘纪律**: flock + 锁内重读 + 原子写 (tmp → fsync → os.replace → fsync(dir))
★**边界**: 不改任何建议默认值 · 不改 C 段其余 38 项 · 不发邮件 · 不下采购单 · 不改 §0 锁死表
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
    "# 待老板拍板页 · 2026-11-11 16:5x (第 21 次刷新 · ★**C 段 38 → 39 (1 新增: ISS-191 复位 P0 落表口径)** "
    "+ ★**ISS-191 已交卷并经 main 独立验收签字 (verified/pass)** + ★**ISS-192 交零 ⇒ 已复位重派 (队列恢复可派)** ★★)"
)

NEW_WHAT = (
    "> ★ **本轮我自己动了什么**: ①★**ISS-191 交卷了, 我已独立验收签字 (verified/pass)** —— sw-lead 15:31 交卷 "
    "(`HW/PCB/RESET_P0_FIX_PLAN.md` + `HANDOFF/2026-11-11_sw-lead_ISS191_复位P0方案.md` + `state/fragments/sw.yaml`) "
    "⇒ ★**我把它给的 8 条验收命令全自己重跑了一遍 (不是采信自述)**: timing_check F1 rc=0 且**逐项对上方案页 B5-1** · "
    "SELFTEST 55/55 · ★**网表 md5 `c78f9912…` + 板 md5 `611b869e…` 一字未变** · merge rc=0 冲突 0 · Q1 18/18 · "
    "DRC 0/unc 45 · ERC 0 · pinfull K=0 ⇒ ★**并且我自己造了反向用例 (把推荐方案打到 /tmp)**: F1 实读变成 "
    "q_and_in_netlist=**False**/栅极漏极均 DNP ⇒ **逐条命中方案页 A1** ⇒ 全量自测**精确红 5 条** ⇒ "
    "**与方案页 B5-3 点名的 5 条逐条同名** ⇒ ★**方案页的预测能力被独立证实** ⇒ ★**签字通过**。"
    "★**但签字只覆盖【方案页交付并验收】, 【不】覆盖 P0 实体修复** ⇒ ★**首台板现在仍然起不来** (RESET_N 仍恒低) "
    "⇒ ★**未藏账**: P0 继续挂在 ① `state/RECHAIN_ONEPASS_PLAN.md` §1 行 C (等你拍「②」) ② ★**本轮新增的第 39 条 C 段拍板项** 两处。"
    "②★**C 段 38 → 39 (1 新增 / 0 移除 / 0 改建议值)** ⇒ ★**新增的那 1 条是今天新冒出来的 (ISS-191 的落表口径)** ⇒ "
    "★**其余 38 项的建议默认值一个字没动 ⇒ 你不用重看一遍**。"
    "③★**ISS-192 (mech-lead) 上一轮被【60 分钟上限】掐断, 交零** (实测末条 = `openclaw:prompt-error: request timed out`; "
    "runtimeMs=3600005 ≈ 整 60 分钟) ⇒ ★**它只落了 1/7** (只有 `MECH/pinset2_mech_check.json` 15:02) ⇒ "
    "★**没有** `MECH/BOARD_GEOM_30MM.md` · **没有** `HANDOFF/…ISS192_*.md` · **没有**写 `fragments/mech.yaml` (mtime 仍 Nov 6) "
    "⇒ ★**`status=fixing` 成了【假标记】= ISS-181 同一个病的第 2 次出现** ⇒ ★**mech-lead 的名额被一条死单永久占住** ⇒ "
    "★**A 段会一直派不出活** ⇒ ★**本轮已把它复位成 `open` 并重派** (★**为什么重派而不像 ISS-181 那样改 deferred**: "
    "ISS-181 是 ★**PCB 布线/布局类** ⇒ 按老板 10:07【一律不派】; ★**但 ISS-192 是结构 (MECH) 类 + 孔位仲裁** ⇒ "
    "★**不在【不派】名单里** ⇒ 它是本该干完的活, 且有★**真实现物理后果**: 打印包 (Rev B 笼 + 量测清单) 已按【套 A】做出, "
    "而 `HW/pcb60x30_check.py/.json` 发的是【套 B】⇒ ★**两套互斥口径差 7.50mm** ⇒ ★**若 PCB 按套 B 钻 ⇒ 螺钉与笼差 7.50mm ⇒ "
    "板装不进骨架** ⇒ ★**这是真缺陷不是记账问题**) ⇒ ★**本轮派出 1 条: ISS-192 → mech-lead** (★**给了它【逐件落盘, "
    "宁可交一半也不要交零】的交卷方式** ⇒ 这正是上一轮交零的根因)。"
    "④★**B 段 approvals = 0 条** ⇒ ★**草稿一件没少也没发**: `state/outbox/` **17 份 .md** (含 1 份 README 清单) + "
    "`attach/` **3 份** ⇒ ★**一封都没发, 一家供应商都没联系**。"
    "⑤★**核验 5 连本轮实测 rc**: merge **0** (冲突 0 · 产出 164 · 阻塞 43 高危 33 · 未闭合需求 93) · gate_check **0** "
    "(★**齐备率 18/18** · 证据分级 3/3 · 接口声明 484 条 · 硬指标覆盖 2/3 · **对账 ✅**) · issue_check **1** (违规 **32** 条) · "
    "stage_gate **1** (当前 **G1**, 还差 **1** 项 ⇒ G2 延后) · daily_check **3** (巡检异常已记录, 非崩溃)。"
    "⑥★**GitHub: 本 job 不推** (统一由 `ARS45 GitHub 同步 (每 5 小时 · 有进展才推)` job 负责) ⇒ ★**只落本地快照**。"
    "⑦★**板 / 网表一个字节没动** (板 md5 仍 `611b869e` · 网表 md5 仍 `c78f9912` · `.kicad_pro` 仍 `3e504d2b`)。"
    "⑧**没有动任何需要你拍板的东西, 没有发任何邮件, 没有下采购单, 没有改 §0 锁死表, 没有写任何子总工的分片**>"
    "   ★ **本轮 C 段口径变化: 38 → 39 项 (1 新增 / 0 移除 / 0 改建议值)** —— ★**只有新增的那 1 条需要你看, 其余 38 条一个字没动** ★★"
)

# ★**新增的第 39 条 = ISS-191 落表口径 ⇒ 落在 §1c (原理图主线类) 后面, 作为第 3 条**
NEW_ROW_1C = (
    "| **3** | `iss191_reset_p0_fix_choice` | ★**ISS-191 复位 P0 落表口径: 走哪条?** ⇒ ★**推荐 ② = 把 `Q_AND` 整颗改 DNP** "
    "(网表表A L65/L66/L67 + 表B `Q_AND.1/.2/.3` **三行同改**) ⇒ `RESET_N` 上**无条件常拉低 = 0 个** ⇒ 首台板能启动 "
    "⇒ ★**同批建议**: `Q_ENVC` 三行**统一 DNP** (消 BOM 口径差) · `R_PG_PULL` **先不动** (省 180µA 但 [0数据] 风险) "
    "⇒ ★**代价**: 复位回到纯 RC+按键 (释放 τ=1.1ms / 越过 0.7VDD 1.324ms, **RC 参数一个都没动**) "
    "⇒ ★**落表时机 = 随「一次整链重出」一起做** (`state/RECHAIN_ONEPASS_PLAN.md` §5 答「②」) "
    "⇒ ★**本项单独回「②」即可** | ★**②** (★**已实测 + main 已独立验收签字**: 方案页 `HW/PCB/RESET_P0_FIX_PLAN.md` "
    "verified/pass ⇒ ★**8 条闸全过 + 自己造的反向用例逐条命中 A1 + 全量自测精确红 5 条**) | 无 due "
    "| ★**不回 = 首台板仍然起不来** (RESET_N 恒低) ⇒ ★**这是【能开机】的问题, 不是【排期】问题** ★★ |\n"
)

NEW_SEC = """## 0.22 ★★★ 本轮: ★**ISS-191 交卷并经我独立验收签字 (verified/pass)** + ★**ISS-192 交零 ⇒ 已复位重派 (队列恢复可派)** ⇒ ★**C 段 38 → 39 (新增 1 条: ISS-191 落表口径)** ★★

> ★**这一节绝大部分是【我这边记账/派活/核验的活】⇒ ★**不需要你做任何新决定** ⇒ ★**38 项老建议一个字没动** ⇒
> ★**只有下面 §1c 新增的**第 3 条** (`iss191_reset_p0_fix_choice`) 需要你看 (★**它本来就是你迟早要拍的** ——
> 复位 P0 决定首台板能不能开机, ★**不能拖到投板那天才拍**) ★★

### 0.22.1 ★★★ ISS-191 交卷了 ⇒ ★**我独立验收签字 (verified/pass)** ⇒ ★**它给了你一条新的落表口径**

| | |
|---|---|
| ★**交的是什么** | sw-lead 15:31 交卷 (`HANDOFF/2026-11-11_sw-lead_ISS191_复位P0方案.md` + `HW/PCB/RESET_P0_FIX_PLAN.md` 34KB + `state/fragments/sw.yaml`) ⇒ ★**只出方案, 一行网表/一行板都没改** (task_brief 明确「先只做方案与影响面评估」) |
| ★**★我做了什么复核 (★不是采信自述★)** | ① **8 条验收命令我自己全跑了一遍**: timing_check F1 rc=0 且★**逐项对上方案页 B5-1** (τ_release 1.1ms / τ_assert 100µs / 越 0.7VDD 1.324ms / `q_and_in_netlist=True` / `PG_AND` 真 DNP 是 `Q_ENVC` / `RESET_N` 上 DNP 是 `U_SUPV` / 锚点 md5 `c78f9912…` 514·513 行) · SELFTEST **55/55 rc=0** · ★**网表 md5 `c78f9912…` + 板 md5 `611b869e…` 一字未变** · merge rc=0 冲突 0 · Q1 **18/18** · DRC **0** / unc **45** / Gerber **32** · ERC **0** rc=0 · pinfull **K=0** 584/584 ② ★**我自己造了反向用例** (把推荐方案打到 `/tmp` 副本, ★**不是跑 sw-lead 的**): F1 实读变成 `q_and_in_netlist=**False**` / 栅极漏极**均 DNP** / `RESET_N` 的 DNP 集合含 `Q_AND` ⇒ ★**逐条命中方案页 A1** ⇒ ★**再跑全量自测 ⇒ 精确红 5 条 ⇒ 与方案页 B5-3 点名的 5 条逐条同名** ⇒ ★**方案页的预测能力被独立证实** ③ ★**文件范围 mtime 复核**: 本单只动过 3 处 ⇒ 网表(11-05)/脚表(11-08)/板(11-06)/原理图(15:17, 那是主线 6b 的)/timing_check.py(13:48)/SW_TIMING_REVIEW.md(13:51, 那是 ISS-190 的) **全部未动** ✔ |
| ★**★签字覆盖什么 / 不覆盖什么 (★别误读★)** | ★**覆盖 = 【方案页交付并验收】** (B1~B6 齐全 · 判据可复现 · 预测被独立证实) ⇒ ★**【不】覆盖【P0 实体修复】** ⇒ ★**首台板现在仍然起不来** (RESET_N 仍恒低) ⇒ ★**未藏账**: P0 继续挂在 ① `state/RECHAIN_ONEPASS_PLAN.md` §1 行 C (等你拍「②」) ② §1c 新增的第 3 条 |
| ★**它给你的那条口径 (★就是 §1c 新增的第 3 条★)** | ★**推荐 ② = 把 `Q_AND` 整颗改 DNP** (表A L65/L66/L67 + 表B `Q_AND.1/.2/.3` **三行必须同改**) ⇒ `RESET_N` 上**无条件常拉低 = 0 个** ⇒ 首台板能启动; ★**同批建议** `Q_ENVC` 三行**统一 DNP** (消 BOM 口径差) · `R_PG_PULL` **先不动**; ★**代价**: 复位回到纯 RC+按键 (τ 1.1ms / 1.324ms, **RC 参数一个都没动**) ⇒ ★**落表时机 = 随「一次整链重出」一起做** ⇒ ★**你回「②」即可** |
| ★**为什么值得你现在拍 (★不是拖★)** | ① ★**它决定首台板能不能开机** (P0, 不是排期问题) ② ★**它和你的【位号改名】同表 ⇒ 合并成一次整链重出 = 只付一次代价** (板 md5 只换一批, 不换两批) ③ ★**方案页已经验完了 ⇒ 你拍完就能直接落表, 没有中间步骤** |

### 0.22.2 ★★★ ISS-192 交零 ⇒ ★**假 `fixing` 标记 (ISS-181 同病第 2 次) ⇒ 已复位重派**

| | |
|---|---|
| ★**实测事实** | 上一轮 mech-lead 会话 14:30→15:30 ⇒ ★**撞 60 分钟上限被掐断** (末条 = `openclaw:prompt-error: request timed out`; runtimeMs **3600005** ≈ 整 60 分钟; `abortedLastRun=true`) ⇒ ★**它交零**: 只落了 `MECH/pinset2_mech_check.json` (15:02) ⇒ ★**没有** `MECH/BOARD_GEOM_30MM.md` · **没有** `HANDOFF/…ISS192_*.md` · **没有**写 `fragments/mech.yaml` (mtime 仍 **Nov 6 11:17**) ⇒ ★**交付物只完成 1/7** |
| ★**为什么这是必须修的账 (★不是记账洁癖★)** | `advance.py` 的 in_flight 代理判据 = 「owner 名下已有 `status==fixing` ⇒ 本轮跳过该 agent」⇒ ★**一条已经死掉的单把 mech-lead 的名额永久占住 ⇒ A 段会一直派不出活** ⇒ ★**实测本轮开跑时 `advance.py --json` 的 `internal=[]` 就有它一份** ⇒ ★**这与 ISS-181 是同一个病 (第 2 次出现)** |
| ★**本轮处置 (★病同因不同药★)** | ★**ISS-181 是 PCB 布线/布局类 ⇒ 按老板 10:07【一律不派】⇒ 改 `deferred` 正确; ★**但 ISS-192 是结构 (MECH) 类 + 孔位仲裁 ⇒ 不在【不派】名单里** ⇒ ★**它是本该干完的活** ⇒ ★**处置 = `fixing → open` 复位 + 重派** (★**状态机允许 `fixing→open`**, issue_check 的 ALLOWED_NEXT 里有) ⇒ ★**本轮派出 1 条: ISS-192 → mech-lead** |
| ★**为什么它值得干 (★真缺陷, 不是记账问题★)** | 打印包 (Rev B 笼 + 量测清单) 已按【**套 A**】做出, 而 `HW/pcb60x30_check.py/.json` 发的是【**套 B**】⇒ ★**两套互斥口径差 7.50mm** ⇒ ★**若 PCB 按套 B 钻 ⇒ 螺钉与笼差 7.50mm ⇒ 板装不进骨架**; 反之若 PCB 按套 A 而那份 JSON 仍发套 B ⇒ ★**它是 ISS-118 的验收产物 ⇒ 下游按它做就错** ⇒ ★**而且 `pinset2_mech_check.py` 现在是【在一块已经不存在的板子上亮绿灯】(假绿)** |
| ★**重派时我加的唯一一条 (★任务书一字未改★)** | ★**【逐件落盘, 宁可交一半也不要交零】** ⇒ ★**最低可交线 = A (权威表) + B (假绿修掉 + `--self-test`) + G (影响面登记)** ⇒ ★**这正是上一轮交零的根因 (只落 1/7)** |

### 0.22.3 ★★★ 核验 5 连 (本轮实测 rc) + GitHub 本 job 不推

| 闸 | rc | 结论 |
|---|---|---|
| `state/merge.py` | **0** | 冲突 **0** · 产出 164 · 阻塞 43 (高危 33) · 未闭合需求 **93** |
| `state/gate_check.py` | **0** | ★**齐备率 18/18** · 证据分级 3/3 · 接口声明 484 条 · 硬指标覆盖 2/3 · ★**与 merge.py 自对账一致** ✔ |
| `state/issue_check.py` | **1** | 违规 **32** 条 (★**与上轮同数** — 本轮新增/关闭的都是非逾期项 ⇒ 数字没动是正常的, 不是没干活) |
| `state/stage_gate.py` | **1** | 当前 **G1** (原理图/PCB 定稿), 还差 **1** 项 (unconnected=45 需 0) ⇒ G2 延后 |
| `state/daily_check.py` | **3** | 巡检异常已记录 (非崩溃): 问题闭环门违规 32 条 |
| 本地快照 | **0** | ★**`PROGRESS_SNAPSHOT.md` 已生成** ⇒ ★**只落本地, 随时能看** ★★ |
| GitHub | — | ★**本 job 不推** (★老板 11-11 10:07 口径 ⇒ 统一由 `ARS45 GitHub 同步 (每 5 小时 · 有进展才推)` job 负责★) ★★ |
| ★**板 / 网表** | — | ★**一个字节没动**: 板 md5 仍 `611b869e13518c3c023fb178f91a0075` · 网表 md5 仍 `c78f991283cc82d56c8e3dd31657c785` · `.kicad_pro` 仍 `3e504d2b` ★★ |

"""

NEW_TAIL = (
    "★ **§1c 这 3 条 = 11-11 12:0x 由 main 补登进 C 段 (源头: `state/fragments/pm.yaml` 的 `needs_from`) ⇒ "
    "★**建议默认值与 §0.18 逐字一致, 本轮一个字没改**★ ⇒ ★**不回也不卡当期** (★**`sch_completeness_target` 的建议已经在跑; "
    "`ref_designator_rename` 的建议本来就是\"不急\"; ★**第 3 条 `iss191_reset_p0_fix_choice` 是 11-11 16:5x 新增** "
    "(ISS-191 方案页验收签字后冒出来的口径) ⇒ ★**它决定首台板能不能开机 ⇒ 建议与「②」一起回** ★★)。**"
)

NEW_DIST = "★ **按来源分 (39 项)**: mech 17 · sw 9 · hw 7 · pm 6。\n"

NEW_OVERDUE_HEAD = "### 附: 逾期分布 (39 项 · 今日实数)\n"

NEW_SUMMARY_LINE = (
    "> ★**新增 1 条 (ISS-191 复位 P0 落表口径, §1c 第 3 条): 它决定【首台板能不能开机】⇒ "
    "★**建议与整链重出的「②」一起回** ⇒ ★**其余 38 项一个字没动** ★★\n"
)


def atomic_write(path: str, text: str) -> None:
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_", suffix=".md")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
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
            if l.startswith("# 待老板拍板页 · 2026-11-11 15:2x (第 20 次刷新"):
                lines[i] = NEW_TITLE
                hit = True
                break
        if not hit:
            print("❌ 找不到标题行 (第 20 次刷新) ⇒ 中止")
            fcntl.flock(lf, fcntl.LOCK_UN)
            return 2
        s = "\n".join(lines)

        # ---- 2. 插入 §0.22 (在 §0.20 主节之前) ----
        anchor = "## 0.20 ★★★ 本轮:"
        idx = s.find(anchor)
        if idx < 0:
            print("❌ 找不到 §0.20 锚点 ⇒ 中止")
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

        # ---- 4. §1c 表: 插入第 3 行 ----
        row_anchor = "| **2** | `ref_designator_rename` |"
        ridx = s.find(row_anchor)
        if ridx < 0:
            print("❌ 找不到 §1c 的 ref_designator_rename 行 ⇒ 中止")
            fcntl.flock(lf, fcntl.LOCK_UN)
            return 2
        eol = s.find("\n", ridx)
        s = s[:eol + 1] + NEW_ROW_1C + s[eol + 1:]

        # ---- 5. §1c 小结行 (2 条 → 3 条) ----
        tail_old = "★ **§1c 这 2 条 = 11-11 12:0x"
        tidx = s.find(tail_old)
        if tidx < 0:
            print("❌ 找不到 §1c 小结行 ⇒ 中止")
            fcntl.flock(lf, fcntl.LOCK_UN)
            return 2
        tend = s.find("\n", tidx)
        s = s[:tidx] + NEW_TAIL + s[tend:]

        # ---- 6. C 段计数 38 → 39 (三处) ----
        s = s.replace(
            "★ **§1 的 3 项 + 本节 1 项 + §1c 的 2 项 = C 段 38 项 (★其余 32 项属整机/量产阶段",
            "★ **§1 的 3 项 + 本节 1 项 + §1c 的 3 项 = C 段 39 项 (★其余 32 项属整机/量产阶段",
        )
        s = s.replace("### 附: 逾期分布 (38 项 · 今日实数)", NEW_OVERDUE_HEAD.rstrip("\n"))
        s = s.replace("★ **按来源分 (38 项)**: mech 17 · sw 9 · hw 7 · pm 5。\n", NEW_DIST)

        # ---- 7. §8 汇总: 加一行 ----
        sum_anchor = "> ★**新增 1 条 (板子基线 p41, §1b):"
        sidx = s.find(sum_anchor)
        if sidx < 0:
            print("❌ 找不到 §8 汇总锚点 ⇒ 中止")
            fcntl.flock(lf, fcntl.LOCK_UN)
            return 2
        seol = s.find("\n", sidx)
        s = s[:seol + 1] + NEW_SUMMARY_LINE + s[seol + 1:]

        atomic_write(P, s)
        fcntl.flock(lf, fcntl.LOCK_UN)

    after = open(P, encoding="utf-8").read()
    print("✅ 第 21 次刷新已写入:", os.path.basename(P))
    print(f"   字节数 {before_len} → {len(after)} (+{len(after)-before_len})")
    print("   - 标题 → 16:5x / 第 21 次")
    print("   - 新增 §0.22 (3 个子节)")
    print("   - 『本轮我自己动了什么』段已重写")
    print("   - §1c 新增第 3 行 (iss191_reset_p0_fix_choice) + 小结行改 3 条")
    print("   - C 段计数 38 → 39 (三处)")
    # 自检
    assert "## 0.22" in after and "## 0.20" in after and "第 21 次刷新" in after
    assert "iss191_reset_p0_fix_choice" in after
    assert "C 段 39 项" in after
    assert "C 段口径变化: 38 → 39 项" in after
    assert "ISS-192" in after and "60 分钟" in after
    print("   - 自检 ✅ (§0.22 在 / ISS-191 在 / C 段 39 一致 / ISS-192 重派 在)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
