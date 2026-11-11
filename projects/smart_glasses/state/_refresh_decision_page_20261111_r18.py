#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""刷新老板拍板页 DECISION_PENDING_2026-11-11.md (第 18 次刷新) —— 2026-11-11 11:4x

★**只整理 + 给建议默认值, 不代决** —— 拍板前不动任何采购 / 外发 / 改图 / 改锁死表。

★**本轮 C 段口径: 36 → 36 (0 新增 / 0 移除 / 0 改建议值)** ⇒ ★**你不用重看一遍**。

★**本轮实质 (全是 main 自己的收尾活, 不新增你的决策负担)**:
  ① ★★**ISS-189 闭环了** (★**死单 → 重派 → 交卷 → main 验收签字**★) ⇒ ★**这是本项目第一条完整的闭环链路**
  ② ★**A 段仍是 0 条可派** ⇒ ★**根因复述 + 本轮明确跳过哪几条 PCB 类** (★按老板 11-11 10:07 主线口径★)
  ③ ★**主线第六件 (原理图补全到表内全量) 已在主会话跑** ⇒ 本 job 不重复派
  ④ ★**核验 5 连本轮实测 rc**: merge 0 · gate_check 0 · issue_check 1 · stage_gate 1 · daily_check 3
  ⑤ ★**GitHub: 本 job 不推** (统一由 5 小时同步 job 负责) ⇒ 本轮只落本地快照

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

NEW_TITLE = (
    "# 待老板拍板页 · 2026-11-11 11:4x (第 18 次刷新 · ★**C 段 36 → 36 (0 新增/0 移除/0 改建议值)** "
    "+ ★**ISS-189 闭环 (死单→重派→交卷→main 验收签字) + A 段 0 条根因复述 + 主线第六件在跑**★)"
)

NEW_WHAT = (
    "> ★ **本轮我自己动了什么**: ①★★**ISS-189 闭环** (★**本项目第一条【死单 → 重派 → 交卷 → main 验收签字】"
    "的完整链路**★) —— ★**main 自己实测**: 旧口径 `grep '373Mbps|373 Mbps|246 Mbps' HW/ SW/ state/outbox/` "
    "**零命中** · 两处目标行都已是 **2986 Mbps** 且带依据注 · `e2e_budget --selftest` **rc=0** + 判据脚本 "
    "md5 `7b820c14` 未变 · 板 md5 仍 **`611b869e`** 一字未动 ⇒ ★**落账 status=verified / verify_by=main / "
    "pass** (★**逐条 diff 实测: 185 条里只有 ISS-189 变了**★) ②★**A 段仍是 0 条可派** ⇒ ★**根因复述: "
    "`issue_log` 里 26 条 open 的 owner 【全部】是 main / boss ⇒ 三个总工名下【一条 open 都没有】** ⇒ "
    "★**且本轮按老板 11-11 10:07 主线口径, 明确跳过的 PCB 类 = ISS-181 (hw-lead 在飞, 布到可下单) "
    "+ 任何 PCB 布线/布局类新单** ⇒ ★**主线 (原理图) 的活由主会话在派, 本 job 不重复派**★ ③★**主线第六件 "
    "(原理图补全到表内全量 = 584 脚 + 补 SoM 两个连接器 + NC 标注) 已在主会话派给 hw-lead 并在跑** "
    "(★**11:38 起的会话实测在跑**★) ⇒ **本 job 不重复派** ⇒ ★**另注: ISS-189 交卷时 hw-lead 明确没碰 "
    "issue_log (按 sw-lead ISS-188 先例, 落账留给 main, verify_by=main) ⇒ 本轮 main 补签**★ ④★**核验 5 连"
    "实测 rc**: merge 0 · gate_check 0 · issue_check 1 (违规 33 条老账, 与上轮逐条相同) · stage_gate 1 "
    "(G1, 差 1 项) · daily_check 3 ⑤★**GitHub 本 job 不推** (统一由 5 小时同步 job 负责) ⇒ ★**只落本地快照** "
    "⑥**没有动任何需要你拍板的东西, 没有发任何邮件, 没有下采购单, 没有改 §0 锁死表, 没有写任何子总工的分片**"
)

NEW_SEC = """## 0.17 ★★★ 本轮: ★**ISS-189 闭环了** (★**死单 → 重派 → 交卷 → main 验收签字**★) + ★**A 段 0 条根因复述** + ★**主线第六件在跑** ⇒ ★**C 段 36 → 36 (你不用重看)** ★★

> ★**这一节全部是【我这边记账/救火/验收的收尾活】⇒ ★**不需要你做任何决定** ⇒ ★**没有新增任何决策项, 没有改任何建议默认值** ⇒ ★**下面 36 项的口径与你上一次看的完全一致**。

### 0.17.1 ★★ 本轮唯一的实质事件: ★**ISS-189 闭环 —— 这是一条【死单】被救回来的完整链路**

| | |
|---|---|
| ★**时间线** | ★**09:1x 第 1 次派出 ⇒ 会话 aborted ⇒ 两行一个字没改 (= 死单)** ⇒ ★**10:3x 第 2 次派出** ⇒ ★**hw-lead 交卷 `HANDOFF/2026-11-11_hw-lead_ISS189_DSI_payload_收尾.md` (25KB)** ⇒ ★**11:4x main 验收签字 = verified / pass** ★★ |
| ★**main 的验收 (自己实测, 不是抄 owner 自评)** | ① `grep -rn '373Mbps\\|373 Mbps\\|246 Mbps' HW/ SW/ state/outbox/` ⇒ **零命中** ② `HW/STEP1_LANDING_LIST.md:42` + `HW/PART_ALTERNATIVES_REGISTRY.md:24` 两处都已是 **2986 Mbps** 且都带依据注 ③ `python3 HW/e2e_budget_rk3572.py --selftest` ⇒ **rc=0**, 判据脚本 md5 `7b820c14` **未变** ④ `HW/PCB/demo_mainboard.kicad_pcb` md5 仍 **`611b869e13518c3c023fb178f91a0075`** ⇒ **板子一字未动** ⑤ **结论方向未变** (4-lane 绰绰有余 / 不需 DSC 仍成立 ⇒ 只订正数字, 不改结论) |
| ★**落账纪律** | ★**flock + 锁内重读 + 原子写 + yaml 往返复现自检** ⇒ ★**逐条 diff 实测: 185 条里【只有 ISS-189 变了】, 其余 184 条一个字节没动** ★★ |
| ★**对你的影响** | ★**零** —— ★**这 2 行是【Step1 落地清单】和【替代料清单】的带宽前提** ⇒ ★**照着它接线的人本来会拿到虚到 8 倍的带宽前提 (2986 vs 373)** ⇒ ★**改的是数字, 不是结论** ★★ |

### 0.17.2 ★★ A 段仍是 0 条可派 ⇒ ★**根因复述 + 本轮明确跳过的 PCB 类**

| | |
|---|---|
| ★**根因 (上轮已订正过, 本轮实测仍然成立)** | ★**`issue_log.yaml` 里 26 条 `open` 的 owner 【全部】是 `main` 或 `boss` ⇒ ★**三个总工名下【一条 open 都没有】** ⇒ ★**真实根因是【两个原因同时成立】: (a) 没有 open 单 (b) hw-lead 名下 ISS-181 仍在飞** ⇒ ★**等不等都一样** ★★ |
| ★**本轮按主线口径明确跳过的 PCB 类** | ★**ISS-181 (owner=hw-lead, `fixing`, due 11-08, 逾期) —— 「自研 demo 主板: 从骨架布到可下单 (unconnected 353 → 0, DRC 0, Gerber 重出)」** ⇒ ★**★这是 PCB 布线/布局类 ⇒ 按老板 11-11 10:07 指令「先解决原理图绘制的问题, 再解决 PCB 绘制的问题」⇒ 本 job【不派】(排队等原理图定稿)★** ⇒ ★**另: 本轮没有任何 PCB 布线/布局类新单进入 A 段 (因为三个总工名下 0 条 open)** ★★ |
| ★**主线 (原理图) 的活由谁在派** | ★**主会话 (agent:main:main) 在派** —— ★**实测 11:38 起的 hw-lead 会话在跑 = 主线第六件 (原理图补全到表内全量 = 584 脚 + 补 SoM 两个连接器 + NC 标注)** ⇒ ★**本 job 不重复派 (★**重复派 = 两个写会话互相覆盖分片**★) ★★ |

### 0.17.3 ★★ 核验 5 连 (本轮实测 rc) + ★**GitHub 本 job 不推**

| 闸 | rc | 结论 |
|---|---|---|
| `state/merge.py` | **0** | 冲突 0 · 健康度 red (老账) |
| `state/gate_check.py` | **0** | 硬指标覆盖 1/3 个总工 |
| `state/issue_check.py` | **1** | 违规 **33** 条 (老账, 与上轮逐条相同) |
| `state/stage_gate.py` | **1** | 当前 **G1** (原理图/PCB 定稿), 还差 **1** 项 ⇒ G2 延后 |
| `state/daily_check.py` | **3** | 巡检异常已记录 (问题闭环门违规 33 条) |
| GitHub | — | ★**本 job 不推** (★老板 11-11 10:07 口径 ⇒ 统一由 `ARS45 GitHub 同步 (每 5 小时 · 有进展才推)` job 负责★) ⇒ ★**本轮只落本地快照** ★★ |

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
            if l.startswith("# 待老板拍板页 · 2026-11-11 10:3x (第 17 次刷新"):
                lines[i] = NEW_TITLE
                hit = True
                break
        if not hit:
            print("❌ 找不到标题行 (第 17 次刷新) ⇒ 中止")
            fcntl.flock(lf, fcntl.LOCK_UN)
            return 2
        s = "\n".join(lines)

        # ---- 2. 插入 §0.17 (在 §0.16 之前) ----
        anchor = "## 0.16 ★★★ 本轮:"
        idx = s.find(anchor)
        if idx < 0:
            print("❌ 找不到 §0.16 锚点 ⇒ 中止")
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
    print("✅ 第 18 次刷新已写入:", os.path.basename(P))
    print(f"   字节数 {before_len} → {len(after)} (+{len(after)-before_len})")
    print("   - 标题 → 11:4x / 第 18 次")
    print("   - 新增 §0.17 (3 个子节)")
    print("   - 『本轮我自己动了什么』段已重写")
    print("   - ★**C 段 36 项口径一个字没动** (0 新增 / 0 移除 / 0 改建议值)")
    # 自检: §0.17 在, §0.16 还在, 标题对
    assert "## 0.17" in after and "## 0.16" in after and "第 18 次刷新" in after
    print("   - 自检 ✅ (§0.17 在 / §0.16 还在 / 标题已更新)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
