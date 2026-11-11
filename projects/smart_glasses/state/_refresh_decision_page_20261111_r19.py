#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""刷新老板拍板页 DECISION_PENDING_2026-11-11.md (第 19 次刷新) —— 2026-11-11 13:2x

★**只整理 + 给建议默认值, 不代决** —— 拍板前不动任何采购 / 外发 / 改图 / 改锁死表。

★**本轮 C 段口径: 38 → 38 (0 新增 / 0 移除 / 0 改建议值)** ⇒ ★**你不用重看一遍**。
★**但本轮把 C 段【表】从 36 条补写成 38 条** (★§0.18 那 2 条 (原理图完整度目标 / 位号规范)
  正式落进 §1c ⇒ ★**这是兑现 §0.18 承诺的"第 19 次刷新"**, 不是新增决策项★)。

★**本轮实质 (全是 main 自己的记账活, 不新增你的决策负担)**:
  ① ★★**A 段从 0 条变 1 条并已派出** (★**ISS-190 → sw-lead**★) —— ★**这是 11-11 10:07 主线口径
     (原理图/网表/ERC/软件优先, PCB 布线/布局不派) 之后的第一条【真的派出去的活】**★
  ② ★**B 段 (approvals) = 0 条** —— ★**但草稿一件没少: `state/outbox/` 16 份 .md 草稿 + 1 份 README
     清单 (共 17 份 .md) + `attach/` 2 份附件 + 1 份附件 README ⇒ 一封都没发** ★
  ③ ★**C 段 38 项** ⇒ ★**下面 §1c 的 2 条是本轮唯一"表"的变化, 建议默认值一个字没改** ★
  ④ ★**核验 5 连本轮实测 rc**: merge 0 · gate_check 0 (齐备率 18/18) · issue_check 1 (违规 33 条老账)
     · stage_gate 1 (G1, 差 1 项) · daily_check 3
  ⑤ ★**GitHub: 本 job 不推** (统一由 5 小时同步 job 负责) ⇒ 本轮只落本地快照
     (`PROGRESS_SNAPSHOT.md` 已生成, 3462 B)

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
    "# 待老板拍板页 · 2026-11-11 13:2x (第 19 次刷新 · ★**C 段 38 → 38 (0 新增/0 移除/0 改建议值)** "
    "+ ★**A 段 1 条已派出 (ISS-190 → sw-lead) + C 段表补写成 38 条 (兑现 §0.18 承诺)**★)"
)

NEW_WHAT = (
    "> ★ **本轮我自己动了什么**: ①★★**A 段从 0 条变 1 条, 并且真的派出去了** —— ★**ISS-190 → sw-lead** "
    "(★**主线口径下的第一条派活**: 「SW 侧时序/电源评审与机械复核器口径漂移」⇒ `SW/SW_TIMING_REVIEW.md` "
    "锚在 **476 行旧网表** 而现网表已是 **513 行 (514 行含表头)** ⇒ ★**F4/F8 两条结论已被现网表推翻** "
    "(`U_PWR_SW` 不含 `LOAD|LOADSW|U_LS` 任一子串 ⇒ 老复现命令永远是 0 = 假阴性) · `SW/tools/timing_check.py` "
    "**从不打开网表** ⇒ F8 段写死 `False` 而自测把 `is False` 当 PASS ⇒ ★**假绿**★) ⇒ ★**main 的派活前三查 (实测)**: "
    "`sessions_list` ⇒ sw-lead **无在跑写会话** (最后一个 sw-lead 会话文件 mtime 08:44) ✔ · ★**文件交集实测 = 空** "
    "(hw-lead 11:38 起的会话只动 `demo_mainboard*.kicad_sch` + 生成器 + `state/check_sch_pinfull.py`; "
    "本单只动 `SW/**` + `HANDOFF/` + `state/fragments/sw.yaml`) ✔ · ★**网表两边都不许改** (本单只读) ✔ ⇒ "
    "`sessions_spawn` (taskName=`advance_iss190`) + `advance.py --apply --only ISS-190` ⇒ **status=fixing** ★★ "
    "②★**B 段 approvals = 0 条** ⇒ ★**草稿一件没少也没发**: `state/outbox/` **16 份 .md 草稿 + 1 份 README 清单** "
    "(共 17 份 .md) + `attach/` **2 份附件 + 1 份附件 README** ⇒ ★**一封都没发, 一家供应商都没联系** ★ ③★**C 段 38 → 38** "
    "⇒ ★**§0.18 那 2 条 (原理图完整度目标 / 位号规范) 正式落进 §1c 表** ⇒ ★**这是兑现上轮承诺, 不是新增决策项; "
    "38 条的建议默认值一个字没动** ★ ④★**核验 5 连实测 rc**: merge 0 (冲突 0 · 产出 161 · 未闭合需求 80) · "
    "gate_check 0 (★**齐备率 18/18** · 证据分级 3/3 · 接口声明 480 条) · issue_check 1 (违规 **33** 条老账) · "
    "stage_gate 1 (当前 **G1**, 还差 **1** 项 ⇒ G2 延后) · daily_check 3 (巡检异常已记录, 非崩溃) ⑤★**GitHub 本 job 不推** "
    "(统一由 `ARS45 GitHub 同步 (每 5 小时 · 有进展才推)` job 负责) ⇒ ★**只落本地快照** (`PROGRESS_SNAPSHOT.md` 已生成) "
    "⑥**没有动任何需要你拍板的东西, 没有发任何邮件, 没有下采购单, 没有改 §0 锁死表, 没有写任何子总工的分片**"
)

NEW_SEC = """## 0.19 ★★★ 本轮: ★**A 段真的派出去了 (ISS-190 → sw-lead)** + ★**C 段表补写成 38 条** ⇒ ★**C 段 38 → 38 (你不用重看)** ★★

> ★**这一节全部是【我这边记账/派活/核验的活】⇒ ★**不需要你做任何决定** ⇒ ★**没有新增任何决策项, 没有改任何建议默认值** ⇒ ★**下面 38 项的口径与你上一次看的完全一致**。

### 0.19.1 ★★ 本轮唯一的实质事件: ★**A 段从 0 条变 1 条, 并派出去了**

| | |
|---|---|
| ★**派了什么** | ★**ISS-190 → sw-lead** (severity=high · due 2026-11-13) —— ★**标题**: 「★SW 侧时序/电源评审与机械复核器口径漂移 ⇒ `SW_TIMING_REVIEW` 锚在 476 行旧网表 (现行 513 行) ⇒ F4/F8 结论已被现网表推翻 ⇒ `timing_check.py` 实读网表 (现为手抄常量 + 假绿自测)」 |
| ★**为什么它配得上"主线"** | ★**老板 11-11 10:07 口径 = 「先解决原理图绘制的问题」** ⇒ ★**本单是【网表 / 评审 / 软件工具】类, 在优先派活范围内; ★**它不是 PCB 布线/布局类** ⇒ **不违反"PCB 类一律不派"** ★★ |
| ★**它要修的是什么 (实测, 不是推测)** | ① ★**口径漂移**: `SW/SW_TIMING_REVIEW.md` 声明评审对象 = 476 行网表, ★**现网表 = 513 行数据 (514 行含表头) / md5 `c78f991283cc82d56c8e3dd31657c785`** ② ★**F4 已被推翻 (部分)**: 老文记 `grep -cE ",(EN|SS|CT|MR)[, ]"` = 0, ★**main 实跑 = 11** ③ ★**F8 是假阴性**: 老文记 `grep -cE "LOAD\\|LOADSW\\|U_LS"` = 0, ★**实跑也是 0 —— 但真负载开关叫 `U_PWR_SW`** ⇒ ★**那个 pattern 永远看不见它** ⇒ F8 的"关机只能靠软件深睡"**对现网表是错的** ④ ★**`timing_check.py` 是假绿**: 它**从不打开网表**, F8 段写死 `load_switch_in_netlist: False`, 自测却把 `is False` 当 PASS ⇒ ★**网表变了它照样绿**; 同类 `R_I2C_PULL` 写死 4700, ★**现网表 I2C_A 上拉是 2.2k / 1.8V** ⇒ ★**F3 的 300pF 上限判据会从 ❌ 翻成 ✅** ★★ |
| ★**派活前三查 (实测, 不是想当然)** | ① `sessions_list` ⇒ ★**sw-lead 无在跑写会话** (最后一个 sw-lead 会话文件 mtime 08:44) ✔ ② ★**文件交集 = 空** (hw-lead 11:38 起在跑的那条只动 `demo_mainboard*.kicad_sch` + 生成器; ★**本单只动 `SW/**` + `HANDOFF/` + `state/fragments/sw.yaml`**) ✔ ③ ★**网表两边都不许改** (本单只读; hw-lead 那条也不许改) ⇒ **零写冲突** ★★ |
| ★**落账纪律** | ★**`sessions_spawn(agentId=sw-lead, mode=run, taskName=advance_iss190)` + `advance.py --apply --only ISS-190`** ⇒ ★**status=fixing / 派活日志已写** ⇒ ★**本单 verify_by=main ⇒ sw-lead 交卷后由 main 独立重跑复现命令 + 跑反向用例 + 签字, 不采信自述** ★★ |
| ★**对你的影响** | ★**零** —— ★**它只改文档 + 一个自查脚本, 不碰板、不碰网表、不碰锁死表** ⇒ ★**板 md5 `611b869e` 与网表 md5 `c78f9912` 都必须一字不变** (★**main 验收时会实测对拍**★) ★★ |

### 0.19.2 ★★ B 段: ★**approvals = 0 条, 草稿一件没少, 一封都没发**

| | |
|---|---|
| ★**实测** | `state/outbox/` = ★**16 份 .md 草稿 + 1 份 README 清单 (共 17 份 .md)** + `attach/` = ★**2 份附件 + 1 份附件 README** ⇒ ★**零缺失** |
| ★**发了没有** | ★**一封都没发, 一家供应商都没联系** —— ★**外发一律等你一句"可以发"** (★**本轮 `advance.py --json` 的 B 段 = 0 条**) ★★ |

### 0.19.3 ★★ C 段: ★**表补写成 38 条** (★**兑现 §0.18 的承诺, 不是新增决策★)

| | |
|---|---|
| ★**§0.18 说过什么** | ★**「第 19 次刷新 (半小时内自动跑) 会把 C 段表重写成 38 条」** ⇒ ★**本轮就是第 19 次刷新 ⇒ 兑现** ★★ |
| ★**本轮改了什么** | ★**§1 新增 §1c (原理图主线类), 把 2 条正式落表: `sch_completeness_target` (原理图完整度目标三选一) + `ref_designator_rename` (位号规范)** ⇒ ★**建议默认值与 §0.18 逐字一致, 一个字没改** ★★ |
| ★**38 项的构成 (实测)** | mech **17** · sw **9** · hw **7** · pm **5** ⇒ ★**逾期 33 · 剩 1 天 1 · 无 due 4** ⇒ ★**当期真卡主线的仍是 §1 那 3 项 (一条没多)** ★★ |
| ★**对你的影响** | ★**零** —— ★**这 2 条的建议默认值 = §0.18 里你已经看过的两行; ★**其中 `sch_completeness_target` 的建议 (② 表内全量) 已经在跑 (主线第六件), `ref_designator_rename` 的建议 (先评审完再一次性改名) 本来就是"不急"** ⇒ ★**不回也不卡当期** ★★ |

### 0.19.4 ★★ 核验 5 连 (本轮实测 rc) + ★**GitHub 本 job 不推**

| 闸 | rc | 结论 |
|---|---|---|
| `state/merge.py` | **0** | 冲突 **0** · 产出 161 · 阻塞 43 (高危 33) · 未闭合需求 **80** |
| `state/gate_check.py` | **0** | ★**齐备率 18/18** · 证据分级 3/3 · 接口声明 480 条 · 硬指标覆盖 1/3 |
| `state/issue_check.py` | **1** | 违规 **33** 条 (★**老账: 全部是「逾期未闭环」, 与上轮逐条相同, 本轮没新增**★) |
| `state/stage_gate.py` | **1** | 当前 **G1** (原理图/PCB 定稿), 还差 **1** 项 (unconnected=45 需 0) ⇒ G2 延后 |
| `state/daily_check.py` | **3** | 巡检异常已记录 (非崩溃): 问题闭环门违规 33 条 · 漂移 = 内部未闭合 72→80 / 问题单 181→186 |
| 本地快照 | **0** | ★**`PROGRESS_SNAPSHOT.md` 已生成 (3462 B)** ⇒ ★**只落本地, 随时能看** ★★ |
| GitHub | — | ★**本 job 不推** (★老板 11-11 10:07 口径 ⇒ 统一由 `ARS45 GitHub 同步 (每 5 小时 · 有进展才推)` job 负责★) ★★ |

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
            if l.startswith("# 待老板拍板页 · 2026-11-11 11:4x (第 18 次刷新"):
                lines[i] = NEW_TITLE
                hit = True
                break
        if not hit:
            print("❌ 找不到标题行 (第 18 次刷新) ⇒ 中止")
            fcntl.flock(lf, fcntl.LOCK_UN)
            return 2
        s = "\n".join(lines)

        # ---- 2. 插入 §0.19 (在 §0.18 之前) ----
        anchor = "## 0.18 ★★★ 本页新增"
        idx = s.find(anchor)
        if idx < 0:
            print("❌ 找不到 §0.18 锚点 ⇒ 中止")
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

        # ---- 4. C 段口径尾标: 36 → 38 ----
        old_tail = ">   ★ **本轮 C 段口径变化: 36 → 36 项 (0 新增 / 0 移除 / 0 改建议值)** —— ★**你不用重看一遍** ★★"
        new_tail = ">   ★ **本轮 C 段口径变化: 38 → 38 项 (0 新增 / 0 移除 / 0 改建议值)** —— ★**你不用重看一遍** ★★"
        if old_tail not in s:
            print("❌ 找不到 C 段口径尾标 ⇒ 中止")
            fcntl.flock(lf, fcntl.LOCK_UN)
            return 2
        s = s.replace(old_tail, new_tail, 1)

        # ---- 5. §0.18 尾注: 兑现承诺 ----
        old_018 = "> ★**其余 36 条口径一个字没动** (★**你上次看的 36 条仍然有效★**) ⇒ ★**本节只加了上面 2 条** ⇒ ★**第 19 次刷新 (半小时内自动跑) 会把 C 段表重写成 38 条** ★★"
        new_018 = "> ★**其余 36 条口径一个字没动** (★**你上次看的 36 条仍然有效★**) ⇒ ★**本节只加了上面 2 条** ⇒ ★**★第 19 次刷新 (13:2x) 已兑现这条承诺: C 段表已重写成 38 条 (见 §1c)★★** ★★"
        if old_018 not in s:
            print("❌ 找不到 §0.18 尾注 ⇒ 中止")
            fcntl.flock(lf, fcntl.LOCK_UN)
            return 2
        s = s.replace(old_018, new_018, 1)

        # ---- 6. §1b 尾注: C 段 36 → 38 + 其余 32 → 32 (不变) ----
        old_1b = "★ **§1 的 3 项 + 本节 1 项 = C 段 36 项 (★其余 32 项属整机/量产阶段 (G2 已于 11-02 19:25 延后) 或方法论 ⇒ 不必今天回★)。**"
        new_1b = "★ **§1 的 3 项 + 本节 1 项 + §1c 的 2 项 = C 段 38 项 (★其余 32 项属整机/量产阶段 (G2 已于 11-02 19:25 延后) 或方法论 ⇒ 不必今天回★)。**"
        if old_1b not in s:
            print("❌ 找不到 §1b 尾注 ⇒ 中止")
            fcntl.flock(lf, fcntl.LOCK_UN)
            return 2
        s = s.replace(old_1b, new_1b, 1)

        # ---- 7. 新增 §1c (原理图主线类) —— 插在 §2 之前 ----
        sec_1c = """## 1c. ⚪ 原理图主线类 (★**当期【不】卡主线 —— 但它是今天的主线本身, 建议默认值已按现状推进**★)

| # | key | 一句话问题 | 建议默认值 (我的口径) | 逾期 | 不拍板的后果 |
|---|---|---|---|---|---|
| **1** | `sch_completeness_target` | ★**demo 原理图的【完整度目标】三选一**: ① 最小集 (★现状 ⇒ 只画用到的脚 ⇒ 接口对边【永不可评审】★) ② 【表内全量】(★`netlist_v1_pins.csv` 的 584 脚全画 + 补 `J_SOM_P2/P4` + NC 标注 ⇒ ★**可评审对边**★) ③ 真实器件全貌 (★USB-C 24脚 / SoM 400球 ⇒ 那就不是 demo 板, 是产品级设计, 要 datasheet/官方库★) | ★**② 表内全量** ★ (★**已在主线第六件跑** ★) ⇒ ③ 另立 | 无 due | ★**不选 = 评审清单的 R1 永远无解, 这张图永远只能看电源阻容** ★★ |
| **2** | `ref_designator_rename` | ★**位号规范: 要不要把带下划线的位号改掉** (★实测: KiCad BOM 里 **255/291** 个位号带字面量问号 ⇒ KiCad 判未标注 ⇒ 板厂看到的位号与丝印对不上★) ⇒ ★**改它 ⇒ netlist表 → BOM → 原理图 11 页 → 板里 186 个封装位号 → 丝印/CPL/装配/IPC-2581/3D/D356 全套 ⇒ 【板 md5 必变】⇒ 留证链/Gerber/投产包全要重出** (★一个位号平均散在 19~112 个文件★) | ★**先过完原理图评审, 再一次性改名 + 整链重出** (★别在评审中途让 KiCad 偷偷改★) ⇒ ★**`RAIL_*`/`NET_*` 保留** (★单点汇流位, 改了 BOM 里会多假料号★) | 无 due | ★**不改 = 交给板厂的 BOM 位号带问号 (装配/CPL 会错位) ⇒ 投板前必须解决** ★★ |

★ **§1c 这 2 条 = 11-11 12:0x 由 main 补登进 C 段 (源头: `state/fragments/pm.yaml` 的 `needs_from`) ⇒ ★**建议默认值与 §0.18 逐字一致, 本轮一个字没改**★ ⇒ ★**不回也不卡当期** (★**`sch_completeness_target` 的建议已经在跑; `ref_designator_rename` 的建议本来就是"不急"**★)。**

---

"""
        anchor2 = "## 2. 🟠 外发类"
        idx2 = s.find(anchor2)
        if idx2 < 0:
            print("❌ 找不到 §2 锚点 ⇒ 中止")
            fcntl.flock(lf, fcntl.LOCK_UN)
            return 2
        s = s[:idx2] + sec_1c + s[idx2:]

        # ---- 8. §2 草稿计数口径订正 (实测 16 份草稿 + README, 不是 17 份草稿 + README) ----
        old_draft = "★ **`state/outbox/` 现有 17 份 .md 草稿 + 1 份 README 清单 + `attach/` 3 份附件, 一份都没发过。**"
        new_draft = "★ **`state/outbox/` 现有 16 份 .md 草稿 + 1 份 README 清单 (共 17 份 .md) + `attach/` 2 份附件 + 1 份附件 README, 一份都没发过。**"
        if old_draft not in s:
            print("❌ 找不到 §2 草稿计数行 ⇒ 中止")
            fcntl.flock(lf, fcntl.LOCK_UN)
            return 2
        s = s.replace(old_draft, new_draft, 1)

        # ---- 9. 逾期分布: 36 项 → 38 项, 无 due 2 → 4, pm 3 → 5 ----
        old_over = "### 附: 逾期分布 (36 项 · 今日实数)"
        new_over = "### 附: 逾期分布 (38 项 · 今日实数)"
        if old_over not in s:
            print("❌ 找不到逾期分布小节 ⇒ 中止")
            fcntl.flock(lf, fcntl.LOCK_UN)
            return 2
        s = s.replace(old_over, new_over, 1)

        old_nodue = "| 无 due | 2 | `soc_cost_criterion` · ★`board_p41_promote` (★新项无 due★) |"
        new_nodue = "| 无 due | 4 | `soc_cost_criterion` · ★`board_p41_promote` (★新项无 due★) · ★`sch_completeness_target` · ★`ref_designator_rename` (★§1c 两条, 无 due★) |"
        if old_nodue not in s:
            print("❌ 找不到『无 due』行 ⇒ 中止")
            fcntl.flock(lf, fcntl.LOCK_UN)
            return 2
        s = s.replace(old_nodue, new_nodue, 1)

        old_by = "★ **按来源分 (36 项)**: mech 17 · sw 9 · hw 7 · pm 3。"
        new_by = "★ **按来源分 (38 项)**: mech 17 · sw 9 · hw 7 · pm 5。"
        if old_by not in s:
            print("❌ 找不到『按来源分』行 ⇒ 中止")
            fcntl.flock(lf, fcntl.LOCK_UN)
            return 2
        s = s.replace(old_by, new_by, 1)

        # ---- 10. 尾声明: 草稿份数 ----
        old_tail2 = "> ★ **外发一律经你** —— 草稿都在 `state/outbox/` (现 17 份 .md), 你说\"可以发\"我才发。"
        new_tail2 = "> ★ **外发一律经你** —— 草稿都在 `state/outbox/` (现 16 份 .md 草稿 + 1 份 README 清单), 你说\"可以发\"我才发。"
        if old_tail2 not in s:
            print("❌ 找不到尾声明 ⇒ 中止")
            fcntl.flock(lf, fcntl.LOCK_UN)
            return 2
        s = s.replace(old_tail2, new_tail2, 1)

        atomic_write(P, s)
        fcntl.flock(lf, fcntl.LOCK_UN)

    after = open(P, encoding="utf-8").read()
    print("✅ 第 19 次刷新已写入:", os.path.basename(P))
    print(f"   字节数 {before_len} → {len(after)} (+{len(after)-before_len})")
    print("   - 标题 → 13:2x / 第 19 次")
    print("   - 新增 §0.19 (4 个子节) + §1c (2 条落表)")
    print("   - 『本轮我自己动了什么』段已重写")
    print("   - C 段口径尾标 36 → 38; 逾期分布 36 → 38; 无 due 2 → 4; pm 3 → 5")
    print("   - ★**C 段 38 项的建议默认值一个字没动** (0 新增 / 0 移除 / 0 改建议值)")
    # 自检
    assert "## 0.19" in after and "## 0.18" in after and "第 19 次刷新" in after
    assert "## 1c. ⚪ 原理图主线类" in after
    assert "`sch_completeness_target`" in after and "`ref_designator_rename`" in after
    assert "C 段口径变化: 38 → 38 项" in after
    assert "按来源分 (38 项)" in after
    assert "无 due | 4" in after
    print("   - 自检 ✅ (§0.19 在 / §0.18 还在 / §1c 在 / 38 项口径一致)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
