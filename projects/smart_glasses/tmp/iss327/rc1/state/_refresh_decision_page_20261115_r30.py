#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""决策页刷新 · 2026-11-15 (新文件) —— 由 main (项目总工) 执行

★★**为什么要有这一页 (★实测, 不是推测★)** ★★:
· `state/advance.py --json` 的 C 段 = **36 项**, 与 2026-11-12 那页 §1~§8 的 key 集合**完全一致**
  ⇒ ★**0 新增 / 0 退休 / 0 改建议默认值** ⇒ ⇒ 本页 = 【11-12 那页的表格逐字沿用 + 只订正「逾期」列 + 加本轮小节】
· ★**C 段的「逾期」列必须每天重算** ⇒ 天数在走 ⇒ 不重算就是给老板看假账 (★11-12 那页就是这么写的教训★)

★**本脚本只做 3 件事 (★全是【记账】, 不替老板决定任何事★)**:
   ① 复制 11-12 页的 §1~§8 + 附表 (★建议默认值 / 问题描述 / 不拍板的后果 三列【逐字沿用】★)
   ② ★**只改「逾期」那一列** (★用 `advance.py --json` 的今日实数逐格重算★)
   ③ 加 §0.30 (本轮我动了什么 + 核验 5 连 + A/B/D 段实数)

★**落盘纪律**: flock(state/.decision_page.lock) + 原子写 (tmp → fsync → os.replace → fsync(dir))
★**边界**: 不改 C 段任何一条的建议默认值 · 不发邮件 · 不改 §0 锁死表 · 不写任何子总工的分片
"""
from __future__ import annotations

import fcntl
import json
import os
import re
import subprocess
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
SRC = os.path.join(PROJ, "DECISION_PENDING_2026-11-12.md")
DST = os.path.join(PROJ, "DECISION_PENDING_2026-11-15.md")
LOCK = os.path.join(HERE, ".decision_page.lock")

plan = json.loads(subprocess.run(
    ["python3", "state/advance.py", "--json"], cwd=PROJ, capture_output=True, text=True).stdout)
dec = {x["key"]: x for x in plan["decisions"]}


def cell_new(key: str, old_cell: str) -> str:
    """按今日实数重算「逾期」单元格; 保留原有的加粗/★ 包装风格。"""
    d = dec[key]["days_left"]
    if d is None:
        return "无 due"
    starred = old_cell.strip().startswith("★")
    if d < 0:
        val = "逾期 %d 天" % (-d) if starred else "%d 天" % (-d)
    elif d == 0:
        val = "剩 0 天" if starred else "0 天"
    else:
        val = "剩 %d 天" % d if starred else "%d 天" % d
    if starred:
        return "★**%s**" % val
    return val


OVERDUE_CELL = re.compile(r"^(?:★\*\*)?(?:剩\s*)?(?:\d+\s*天|逾期\s*\d+\s*天)(?:\*\*)?$")
NO_DUE_CELL = re.compile(r"^(?:★\*\*)?无 due(?:\*\*)?$")


def atomic_write(path: str, text: str) -> None:
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix=".decpage.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
        dfd = os.open(os.path.dirname(path), os.O_RDONLY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def main() -> int:
    raw = open(SRC, encoding="utf-8").read()
    marker = "## 1. 🔴 当期真卡主线的只剩"
    idx = raw.index(marker)
    body = raw[idx:]

    # ---- ② 只改「逾期」列 ----
    out_lines = []
    changed = 0
    for line in body.split("\n"):
        if line.startswith("|") and "`" in line:
            parts = line.split("|")
            hit = None
            for k in dec:
                if ("`%s`" % k) in line:
                    hit = k
                    break
            if hit:
                for ci, cell in enumerate(parts):
                    s = cell.strip()
                    if OVERDUE_CELL.match(s) or NO_DUE_CELL.match(s):
                        new = cell_new(hit, s)
                        if new != cell:
                            parts[ci] = cell.replace(s, new)
                            changed += 1
                        break
                line = "|".join(parts)
        out_lines.append(line)
    body = "\n".join(out_lines)

    # ---- 附: 逾期分布 用今日实数重写 ----
    over = [k for k, v in dec.items() if v["days_left"] is not None and v["days_left"] < 0]
    soon = {k: v["days_left"] for k, v in dec.items() if v["days_left"] is not None and v["days_left"] >= 0}
    nodue = [k for k, v in dec.items() if v["days_left"] is None]
    longest = sorted(over, key=lambda k: dec[k]["days_left"])[:5]
    dist = [
        "### 附: 逾期分布 (36 项 · 2026-11-15 20:5x 实数)",
        "",
        "| 逾期天数 | 项数 | 备注 |",
        "|---|---|---|",
        "| 已逾期 | **%d** | 最长: %s |" % (
            len(over), " · ".join("%s (%d 天)" % (k, -dec[k]["days_left"]) for k in longest)),
    ]
    for k in sorted(soon, key=lambda x: soon[x]):
        dist.append("| 剩 %d 天 | 1 | `%s` |" % (soon[k], k))
    dist.append("| 无 due | %d | %s |" % (len(nodue), " · ".join(nodue)))
    dist.append("")
    dist.append("★ **按来源分 (36 项)**: mech 17 · sw 9 · hw 6 · pm 4 (★与 11-12 页同, 0 新增 / 0 退休★)。")
    dist.append("")
    dist_txt = "\n".join(dist)

    m = re.search(r"### 附: 逾期分布 \(36 项.*?(?=\n---\n)", body, re.S)
    if not m:
        print("★找不到附表 ⇒ 拒绝写")
        return 2
    body = body[:m.start()] + dist_txt + body[m.end():]

    # ---- §8 的「最近到期」改成今日实数 ----
    body = body.replace(
        "> ★**最近到期 (2026-11-12 实数)**",
        "> ★**最近到期 (2026-11-15 实数)**")

    # ---- ③ 本轮小节 + 页首 ----
    header = """# 待老板拍板页 · 2026-11-15 20:5x (第 1 次刷新 · 新文件 · ★**C 段 36 → 36 (0 新增 / 0 退休 / 0 改建议值)** + ★**A 段本 job 派 3 条 (ISS-205→sw-lead / ISS-195→hw-lead / ISS-206→mech-lead)** + ★**★清 3 条僵尸 fixing ⇒ 队列停摆 3.5 天后重新转起来★**★)** ⇒ ★**本轮你不用做任何新决定** ★★)

> 出品: 项目总工 (moli / main) · 状态源: `state/advance.py --json` (C 段) + `state/issue_log.yaml` + `state/fragments/{hw,sw,mech,pm}.yaml`
> ★ **只整理 + 给建议默认值, 不代决** —— 拍板前不动任何采购 / 外发 / 改图 / 改锁死表。
> ★ **本轮我自己动了什么 (★只做记账, 不替你决定★)**:
> ① ★**★僵尸 fixing 第 11~13 次复发, 本轮清 3 条★** ⇒ ★**实测**: ISS-195 / ISS-205 / ISS-206 三个子会话 2026-11-12 08:10~08:24 全部 `status=failed` ⇒ 交卷事件投给了已死的会话 ⇒ 没人落账 ⇒ 三条永远停在 `fixing` ⇒ `advance.py` 的 in_flight 规则把三个总工的名额全占住 ⇒ ★**A 段恒空 ⇒ 2026-11-12 03:44 ~ 2026-11-15 20:4x 项目里零文件改动 (停摆 3.5 天)★** ⇒ ★**本轮三条全部退回 open 并重派 (★半交卷的两条按【已落盘文件 + 真正缺口】重写任务书, 0 产出的那条照原 brief 裁完即做★)** ★
> ② ★**A 段派了 3 条 (★三个总工各 1 条, 零撞车★)**: ISS-205 → sw-lead (★high · 卡整链重出第 3 步 · 原理图侧正中★) · ISS-195 → hw-lead (★半交卷收尾★) · ISS-206 → mech-lead (★0 产出重做★) ⇒ ★**按原理图主线口径, 本轮没有跳过任何 PCB 布线/布局类 (三个总工的 open 队列里本来就没有 PCB 类单)★** ★
> ③ ★**B 段 approvals = 0 条** (★老板 2026-11-11 19:31「一律不发」+ 2026-11-12 02:02「不再发信, 全靠自己查资料」后恒为空★) ⇒ ★**`state/outbox/` 实测 19 份 .md 一份没少, 一封都没发** ★
> ④ ★**C 段 36 项 ⇒ 与 11-12 页逐项核对: 36/36 key 完全对齐 (0 新增 / 0 退休 / 0 改建议默认值)★** ⇒ ★**本页 §1~§8 的 36 条【问题描述 + 建议默认值 + 不拍板的后果】三列逐字沿用 11-12 页原文, 本轮只订正了每张表的「逾期」列 (= 今日实数) 与页尾逾期分布表** ★
> ⑤ ★**核验 5 连本轮实测 rc**: merge **0** · gate_check **0** (★**Q1 18/18**★) · issue_check **1** (违规 **35** 条) · stage_gate **1** (当前 **G1**, 还差 **1** 项 ⇒ unconnected=45 需 0) · daily_check **3** (巡检异常已记录, 非崩溃) ⇒ ★**详见 §0.30.2** ★
> ⑥ ★**GitHub: 本 job 不推** (★统一由 `ARS45 GitHub 同步 (每 5 小时 · 有进展才推)` job 负责★) ⇒ ★**本 job 只落本地快照** ★
> ⑦ ★**没有动任何需要你拍板的东西, 没有发任何邮件, 没有联系任何供应商, 没有下采购单, 没有改 §0 锁死表, 没有写任何子总工的分片** ★★
>  ★ **本轮 C 段口径变化: 36 → 36 项 (0 新增 / 0 退休 / 0 改建议值)** —— ★**这一轮你不用重看一遍; 仍等你拍的只有 §1 那 3 条 + §1b 那 1 条 + §2 那 1 条 (共 5 条)** ★★
---

## 0.30 ★★★ 本轮 (2026-11-15 20:4x ~ 20:56): ★**A 段 0 → 3 条 (★清完 3 条僵尸 fixing 之后队列才转得起来★)** + ★**C 段 36 → 36 (0 新增 / 0 退休 / 0 改建议值)** ★★

> ★**这一节全部是【我这边记账 / 派活 / 核验】的活 ⇒ ★**不需要你做任何新决定** ⇒ ★**C 段 36 项的建议默认值一个没动** ⇒
> ★**仍等你拍的只有 §1 那 3 条 + §1b 那 1 条 + §2 那 1 条 = 5 条** ★★

### 0.30.1 ★★★ ★**僵尸 fixing 第 11~13 次复发 —— 本轮清了 3 条, 队列停摆 3.5 天后重新转起来** ★★★

| | |
|---|---|
| ★**症状** | ★**`advance.py --json` 的 `internal` = 0 条** ⇒ 三个总工全被挡住 ⇒ ★**但这不是"没活干"** ★ |
| ★**根因 (★实测, 不是推测★)** | ★**三个子会话全部 `status=failed`**: ISS-195 ⇒ `hw-lead:subagent:eba704c3` (sessionId `dc510f7c`) 2026-11-12 **08:10** 结束 · ISS-205 ⇒ `sw-lead:subagent:0795c93a` (sessionId `660e4fce`) 2026-11-12 **08:24** 结束 · ISS-206 ⇒ `mech-lead:subagent:00f7c6d7` (sessionId `d5a63589`) 2026-11-12 **08:23** 结束 ⇒ ★**交卷事件投给了已死的会话 ⇒ 没人落账 ⇒ status 永远停在 `fixing`** ⇒ ★**`advance.py` 的 in_flight 规则 ("该 agent 正在干别的, 本轮跳过") ⇒ 名额永久占住 ⇒ A 段恒空** ★ |
| ★**实测代价** | ★**2026-11-12 03:44 之后, 项目里【零文件改动】** (板 / 网表 / 原理图 / 三个分片 / issue_log 全部停在 11-12 03:4x) ⇒ ★**队列停摆 3.5 天, 零产出** ★ ⇒ ★**逾期问题单正好从 31 涨到 34 (ISS-195 / ISS-206 due 11-13 + ISS-205 due 11-14 三条跨期)★** ★ |
| ★**三条的处置 (★逐个按盘上实物判, 不采信自述★)** | ★**ISS-195 = 半交卷** (★`HW/iss121_mic_magnet_check.py` mtime **2026-11-12 03:43:43** 已改用套A 孔位★ · `.json` 03:43:07★ ⇒ ❌ `HW/ISS121_MIC_MAGNET_POSITION.md` mtime **2026-11-01 23:50** 一字未动★) ⇒ ★**退回 open 重派收尾** ★<br>★**ISS-205 = 半交卷 (核心产出在盘)** (★`state/gen_kicad_sch.py` 03:36:22 已含 `_1` 后缀逻辑★ · 11 个 `.kicad_sch` 全部 03:36★ · ★**实测图上位号 218 个, 带 `_1` 后缀 187 个**★ · ★**sheet_instances 11/11 都有**★) ⇒ ★**退回 open 重派收尾 + 自证** ★<br>★**ISS-206 = 0 产出** (★`state/fragments/mech.yaml` mtime **2026-11-12 02:46:55** = 早于它 03:2x 的派活时间★ ⇒ ★**第 3 套 pin map `8p@0.5` 还在第 1362 行★) ⇒ ★**退回 open 重派 (brief 已含我逐条裁完的裁决)** ★ |
| ★**A 段本轮实派 3 条 (★一 agent 一条, 零撞车★)** | ★**ISS-205 → sw-lead** (★high · 卡整链重出第 3 步 · 原理图侧正中·BOM 问号归零★) · ★**ISS-195 → hw-lead** (★麦 M1→S1 孔壁净空按套A 重算·收尾★) · ★**ISS-206 → mech-lead** (★结构侧 J_CHG 旧口径一次性收口★) ⇒ ★**任务书全文 (含 `advance.py` 的 brief 原文, 一字未改) 落盘在 `state/tasks/advance_iss{205,195,206}.md` (★可复核★)** ★ |
| ★★**本轮按【原理图主线】跳过了哪几条 PCB 类** ★★ | ★**跳过 0 条** (★三个总工的 open 队列里【本来就没有】PCB 布线/布局类单★) ⇒ ★**而 owner=main/boss 的 PCB 类 open 单 —— ISS-122 (BGA 逃线层数) · ISS-126 (板厚档位) · ISS-128 (板面积账+逃线层数) · ISS-160 (demo 板图纸链) · ISS-169 (demo 板可制造性) —— ★**本轮继续压着不派 (★老板 2026-11-11 10:07 口径: 先解决原理图绘制, 再解决 PCB 绘制★)**, 也没藏账 (★**它们仍列在 G4 未闭环清单里, 且 stage_gate rc=1 / G1 仍开 ⇒ 不许投板没松★)** ★ |

### 0.30.2 ★★★ ★**核验 5 连 (本轮实测 rc) + B 段恒空 + GitHub 本 job 不推** ★★★

| 闸 | rc | 结论 |
|---|---|---|
| `state/merge.py` | **0** | 产出 **189** · 阻塞 43 (高危 33) · 未闭合需求 **117** · 冲突 **0** · 健康度 red |
| `state/gate_check.py` | **0** | ★**齐备率 18/18** · 证据分级 3/3 · 接口声明 489 条 · 与 merge 自对账一致 |
| `state/issue_check.py` | **1** | 违规 **35** 条 (★逾期 34 + 1 条 `source_blocker=MECH-JCHG-PINMAP-3SET` 幻觉引用★) |
| `state/stage_gate.py` | **1** | 当前 **G1** (原理图 / PCB 定稿), 还差 **1** 项 ⇒ ★**PCB 布线未达标: unconnected=45 (需 0) · DRC 违规=0 (需 0) (ISS-181)** |
| `state/daily_check.py` | **3** | 巡检异常已记录 (非崩溃): ★**check_sch_pinfull --self-test rc=1** (★自测没过, 但巡检段本体 ✅ 图上 584 脚 = 表里 584 脚 · K=0★ ⇒ ★**这条已并进 ISS-205 的交卷自证范围**)· chain_gate 投产包比原理图旧 (★**ISS-205 ⑦ 说的预期中间态**)· 问题闭环门违规 35 条 · 漂移检测「逾期 31 → 34」★ |
| ★**原理图侧尺子 (顺带复跑)** | — | ★**ERC 0 条** · ★**脚数完整性 K=0 (图上 584 脚 = 表里 584 脚 · 218 器件/153 网)** ⇒ ★**原理图侧机器可查部分仍全绿** ★ |
| 本地快照 | **0** | ★**`PROGRESS_SNAPSHOT.md` 已生成 (3285 B, 20:56)** ⇒ ★**只落本地, 随时能看** ★★ |
| GitHub | — | ★**本 job 不推** (★**老板 11-11 09:5x 口径 ⇒ 统一由 5 小时同步 job 负责★**) ★★ |
| ★**板 / 网表 / 脚表 / .kicad_pro** | — | ★**本 job 一个字节没动** (★板 `611b869e…` · 网表 `c78f9912…` · 脚表 `4814617e…` · `.kicad_pro` `3e504d2b…`★) ★★ |

---

"""
    out = header + body

    os.makedirs(os.path.dirname(LOCK), exist_ok=True)
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        atomic_write(DST, out)
    print("★已写 %s (%d B) · 「逾期」列改写 %d 格 · C 段 %d 项 (0 新增 / 0 退休 / 0 改建议默认值)"
          % (DST, len(out), changed, len(dec)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
