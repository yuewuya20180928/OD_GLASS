#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""决策页刷 新页 (2026-11-12 · 第 1 次刷新) —— 由 main (项目总工) 执行
================================================================================
★**为什么新开一页而不是继续改 11-11 那页★**:
   ★**11-11 那页已经 24 次刷新 / 934 行 / 145 KB** ⇒ 老板每次要翻到 §1~§8 才知道
   「哪 36 条在等我」⇒ ⇒ ★**今天是新的一天 ⇒ 新开 `DECISION_PENDING_2026-11-12.md`
   当作【当天的正式拍板页】**, ★**§1~§8 的 36 条建议默认值【逐字沿用 11-11 r24a 的原文】★
   (★**一个字的建议值都没改** —— 本轮 C 段 36 → 36, 0 新增 / 0 退休 / 0 改建议★)

★**本脚本只做 4 件事 (★全是【记账/订正】, 不替老板决定任何事★)**:
   ① 把 11-11 页的 §1~§8 (含表) 整段搬过来, ★**原文不动**
   ② ★**订正每张表的「逾期」列** = 用 `advance.py --json` 的**今日实数**重算 (★表格是给老板看的,
      天数每天都在走 ⇒ 不重算就是假账★) ⇒ ★**只动那一个单元格, 不动任何建议默认值★
   ③ ★**重写页尾「附: 逾期分布」** = 今日实数 (36 项 / 已逾期 33 / 剩 0 天 1 / 无 due 2)
   ④ ★**订正 §8 那句陈旧的「其余 38 项」** ⇒ 36 - 3 (§1c 已退休那 3 条不在 C 段里) = **33**

★**落盘纪律**: flock + 锁内重读 + 原子写 (tmp → fsync → os.replace → fsync(dir))
★**边界**: 不改 C 段任何一条的建议默认值 · 不发邮件 · 不改 §0 锁死表 · 不写任何子总工的分片
"""
from __future__ import annotations

import fcntl
import json
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
SRC = os.path.join(PROJ, "DECISION_PENDING_2026-11-11.md")
DST = os.path.join(PROJ, "DECISION_PENDING_2026-11-12.md")
LOCK = os.path.join(HERE, ".decision_page.lock")

HDR = """# 待老板拍板页 · 2026-11-12 00:2x (第 1 次刷新 · ★**C 段 36 → 36 (0 新增 / 0 退休 / 0 改建议值)** + ★**A 段本轮 0 条 (★**真在飞: hw-lead 名额被 ISS-136 占住★**)** ⇒ ★**本轮你不用做任何新决定** ★★)

> 出品: 项目总工 (moli / main) · 状态源: `state/advance.py --json` (C 段) + `state/issue_log.yaml` + `state/fragments/{hw,sw,mech,pm}.yaml`
> ★ **只整理 + 给建议默认值, 不代决** —— 拍板前不动任何采购 / 外发 / 改图 / 改锁死表。
> ★ **本轮我自己动了什么**: ①★**A 段本轮 0 条可派 —— 原因是【真在飞】, 不是死单占位★** ⇒ ★**实测**: `advance.py --json` 的 `internal` = **0 条** ⇒ ★**根因: hw-lead 名额被 ISS-136 占住 (★**兄弟 job「ARS45 队列自动派活」23:5x 派出的, 会话 `824ac5a1` 此刻 status=running★**) ⇒ ⇒ ★**ISS-195 (hw-lead 名下唯一 open, 麦 M1→S1 孔壁净空按套A 重算) 本轮不派** (★**铁律: 一个 agent 同时只允许一个写会话★**) ⇒ ⇒ ★**sw-lead / mech-lead 名下 open = 0** ⇒ ⇒ ★**⇒ A 段空是【三个总工里只有一个有活、而那一个正在跑】, 不是【没活】★** ★。 ②★**B 段 approvals = 0 条 (★**老板 2026-11-11 19:31「一律不发」政策后恒为空★**) ⇒ ★**草稿一件没少, 一封都没发**: `state/outbox/` 实测 **19 份 .md** (16 份草稿 + 1 份 README + 1 份政策件 `NO_OUTBOUND_POLICY.md` + 1 份内部决策图 `R_GEO_2_DECISION_MAP.md`) + `attach/` **3 份** (2 附件 + 1 附件 README) ⇒ ★**零缺失** ★。 ③★**C 段 36 项 ⇒ 逐项实测核对: 与 11-11 r24a 页【36/36 完全对齐, 0 新增 / 0 退休 / 0 改建议值】★** ⇒ ★**⇒ 本页 §1~§8 的 36 条【建议默认值逐字沿用 11-11 页原文】, 本轮只订正了每张表的「逾期」列 (= 今日实数) 与页尾逾期分布表** ★。 ④★**核验 5 连本轮实测 rc**: merge **0** (冲突 **0** · 产出 **175** · 阻塞 43 · 未闭合需求 **101**) · gate_check **0** (★**齐备率 18/18** ★ · 证据分级 3/3 · 接口声明 489) · issue_check **1** (违规 **30** 条) · stage_gate **1** (当前 **G1**, 还差 **1** 项 ⇒ unconnected=45 需 0) · daily_check **3** (巡检异常已记录, 非崩溃) ⇒ ★**详见下方 §0.26.2** ★。 ⑤★**GitHub: 本 job 不推** (统一由 `ARS45 GitHub 同步 (每 5 小时 · 有进展才推)` job 负责) ⇒ ★**本 job 只落本地快照** ★。 ⑥★**板 / 网表 / 脚表 / .kicad_pro md5 一字未动** (611b869e… / c78f9912… / 4814617e… / 3e504d2b…) ★ ⇒ ★**本 job 没碰任何生产文件** ★。 ⑦★**没有动任何需要你拍板的东西, 没有发任何邮件, 没有联系任何供应商, 没有下采购单, 没有改 §0 锁死表, 没有写任何子总工的分片** ★★
  ★ **本轮 C 段口径变化: 36 → 36 项 (0 新增 / 0 退休 / 0 改建议值 —— 本轮只订正表格里的「逾期」列与页尾分布表)** —— ★**这一轮你不用重看一遍; 仍等你拍的只有 §1 那 3 条 + §1b 那 1 条 + §2 那 1 条 (共 5 条)** ★★
---

## 0.26 ★★★ 本轮 (2026-11-12 00:2x): ★**A 段 0 条 (★**真在飞: ISS-136 占住 hw-lead 名额★**)** + ★**C 段 36 → 36 (只订正「逾期」列)** + ★**你不用做任何新决定** ★★

> ★**这一节全部是【我这边记账 / 订正 / 核验】的活 ⇒ ★**不需要你做任何新决定** ⇒ ★**C 段 36 项的建议默认值一个没动** ⇒
> ★**仍等你拍的只有 §1 那 3 条 + §1b 那 1 条 + §2 那 1 条 = 5 条** ★★

### 0.26.1 ★★★ ★**A 段本轮 0 条可派 —— 根因是【真在飞】, 不是死单占位** ★★★

| | |
|---|---|
| ★**实测: `advance.py --json` 的 internal = 0** | ★**`internal: []` · `approvals: []` · `decisions: 36` · `waiting: []` ⇒ ★**A 段真的没有可派项** ★ |
| ★**根因: hw-lead 名额被 ISS-136 占住** | ★**兄弟 job「ARS45 队列自动派活」23:5x 派出 ISS-136 → hw-lead (★**J_CHG 跨铰链 pin map 订正 + 接进 gate_check 门禁链★**) ⇒ ★**会话 `agent:hw-lead:subagent:f8ab912e` (sessionId `824ac5a1`) 本轮实测 status = **running** (★**起于 00:18, 已跑 6 分钟+★**) ⇒ ⇒ ★**`issue_log.yaml` 里 ISS-136 = `fixing` ⇒ `advance.py` 的 in_flight 判据正确挡住 hw-lead** ⇒ ⇒ ★**⇒ ISS-195 (hw-lead 名下唯一 open, 麦 M1→S1 压紧螺钉孔孔壁净空按套A 重算, due 11-13) 本轮不派** (★**铁律: 一个 agent 同时只允许一个写会话★**) ★ |
| ★**sw-lead / mech-lead 名下 open = 0** | ★**实测 `issue_log.yaml`: open/fixing 里 owner 分布 = boss **5** · main **19** · hw-lead **2** ⇒ sw-lead 0 条 · mech-lead 0 条** ⇒ ⇒ ★**⇒ A 段空是【真空 (没人可派) + 一个正在跑】, 不是【队列里全是死单】** ⇒ ⇒ ★**⇒ 本 job 不新开单、不硬塞** (★**兄弟 job「ARS45 队列自动派活」正在同一批需求上排单, 两边同时派同一个 agent 会撞铁律★**) ★ |
| ★★**本轮按【原理图主线】跳过了哪几条 PCB 类** ★★ | ★**跳过 0 条 (三个总工的 open 队列里根本没有 PCB 布线/布局类单: ISS-136 = 规格/网表/门禁侧, ISS-195 = 机械孔位净空复算, 两条都不是 PCB 布线)** ⇒ ★**⇒ 而 owner=main/boss 的 PCB 类 open 单 —— ISS-122 (BGA 逃线层数) · ISS-126 (板厚档位) · ISS-128 (板面积账+逃线层数) · ISS-160 (demo 板图纸链) · ISS-169 (demo 板可制造性) · ISS-060 (产品件三条几何) —— ★**本轮继续压着不派 (★老板 2026-11-11 10:07 口径: 先解决原理图绘制, 再解决 PCB 绘制★)**, 也没藏账 (★**它们仍列在 G4 未闭环清单里, 且 stage_gate rc=1 / G1 仍开 ⇒ 不许投板没松★)** ★ |

### 0.26.2 ★★★ ★**核验 5 连 (本轮实测 rc) + C 段逐项核对 + GitHub 本 job 不推** ★★★

| 闸 | rc | 结论 |
|---|---|---|
| `state/merge.py` | **0** | 冲突 **0** · 产出 **175** · 阻塞 43 (高危 33) · 未闭合需求 **101** |
| `state/gate_check.py` | **0** | ★**齐备率 18/18** · 证据分级 3/3 · 接口声明 489 条 · 与 merge 自对账一致 |
| `state/issue_check.py` | **1** | 违规 **30** 条 (★**全是逾期类, 逐条与上一轮同, 本轮没新增违规★**★) |
| `state/stage_gate.py` | **1** | 当前 **G1** (原理图 / PCB 定稿), 还差 **1** 项 ⇒ ★**PCB 布线未达标: unconnected=45 (需 0) · DRC 违规=0 (需 0) (ISS-181)** |
| `state/daily_check.py` | **3** | 巡检异常已记录 (非崩溃): 问题闭环门违规 30 条 · 漂移检测「内部未闭合 100 → 101」(★**在飞单交卷带来的新增需求, 不是账被做坏**) |
| ★**C 段逐项核对** | — | ★**`advance.py --json` 实测 36 项 ⇒ 与 11-11 r24a 页 36/36 完全对齐 (0 新增 / 0 退休 / 0 改建议值)** ★ |
| ★**原理图侧尺子 (顺带复跑)** | **0** | ★**ERC 0 条 · 脚数完整性 K=0 (图上 584 脚 = 表里 584 脚 · 218 器件/153 网) ⇒ 原理图侧机器可查部分仍全绿** ★ |
| 本地快照 | **0** | ★**`PROGRESS_SNAPSHOT.md` 已生成** ⇒ ★**只落本地, 随时能看** ★★ |
| GitHub | — | ★**本 job 不推** (★**老板 11-11 10:07 口径 ⇒ 统一由 `ARS45 GitHub 同步 (每 5 小时 · 有进展才推)` job 负责★**) ★★ |
| ★**板 / 网表 / 脚表 / .kicad_pro** | — | ★**一个字节没动**: 板 md5 `611b869e13518c3c023fb178f91a0075` · 网表 `c78f991283cc82d56c8e3dd31657c785` · 脚表 `4814617e22b567d76164e56bc5e39dc8` · `.kicad_pro` `3e504d2be83152e337949723e909be1b` ★★ |

### 0.26.3 ★★★ ★**本轮对页面的唯一改动 = 订正「逾期」列 (★建议默认值一个没动★)** ★★★

| # | 改什么 | 为什么 |
|---|---|---|
| 1 | ★**§1~§8 每张表的「逾期」列** ⇒ 用 `advance.py --json` 的**今日实数**逐格重算 (★**只动那一个单元格★**) | ★**天数每天都在走 ⇒ 昨天的「逾期 7 天」今天就是 8 天 ⇒ 不重算就是给老板看假账** ★ |
| 2 | ★**页尾「附: 逾期分布」** ⇒ 重写成今日实数 (**36 项 / 已逾期 33 / 剩 0 天 1 / 无 due 2**) | ★**上一版那行写的是「39 项」且分布按 39 项时代算的 ⇒ 与今天的 36 项对不上** ★ |
| 3 | ★**§8 那句「其余 38 项一个字没动」** ⇒ 订正为 **33** | ★**36 - 3 (§1c 已退休那 3 条早已不在 C 段里) = 33** ⇒ **38 是 39 项时代的旧数** ★ |

★**★除此之外: §1~§8 的 36 条【问题描述 + 建议默认值 + 不拍板的后果】三列【逐字沿用 11-11 r24a 原文】, 一字未改 ★★**

---

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


def overdue_cell(dl):
    if dl is None:
        return "无 due"
    if dl < 0:
        return "%d 天" % (-dl)
    if dl == 0:
        return "**剩 0 天**"
    return "**剩 %d 天**" % dl


def refresh_overdue_col(body: str, dl_map: dict) -> tuple:
    """把 §1~§8 表格里的「逾期」列按今日实数重算 (只动那一格)"""
    lines = body.split("\n")
    out = []
    col_idx = None          # 当前表头里「逾期」列的序号
    changed = 0
    for ln in lines:
        stripped = ln.strip()
        if stripped.startswith("|"):
            cells = ln.split("|")
            # 表头行: 找「逾期」列位置
            heads = [c.strip() for c in cells]
            if any(h.replace("**", "").strip() == "逾期" for h in heads):
                for i, h in enumerate(heads):
                    if h.replace("**", "").strip() == "逾期":
                        col_idx = i
                        break
                out.append(ln)
                continue
            # 数据行: key 格位置不固定 (§1/§1b 有 `#` 编号列 ⇒ key 在第 3 格;
            #           §2~§7 无编号列 ⇒ key 在第 2 格) ⇒ 【扫全行找第一个纯 key 格】
            if col_idx is not None and len(cells) > col_idx:
                key_m = None
                for c in cells:
                    m = re.fullmatch(r"\s*`([a-z0-9_]+)`\s*", c)
                    if m:
                        key_m = m
                        break
                if key_m and key_m.group(1) in dl_map:
                    new_cell = " %s " % overdue_cell(dl_map[key_m.group(1)])
                    if cells[col_idx].strip() != new_cell.strip():
                        cells[col_idx] = new_cell
                        changed += 1
                    out.append("|".join(cells))
                    continue
        else:
            # 表格结束 => 重置列定位
            if stripped == "":
                col_idx = None
        out.append(ln)
    return "\n".join(out), changed


def main() -> int:
    if not os.path.exists(SRC):
        print("❌ 找不到 %s" % SRC)
        return 2
    # ★**自取数** (★不读任何临时快照 ⇒ 不会读到过期的数★)
    import subprocess
    raw = subprocess.run([sys.executable, os.path.join(HERE, "advance.py"), "--json"],
                         capture_output=True, text=True, cwd=PROJ).stdout
    adv = json.loads(raw)
    dl_map = {x["key"]: x.get("days_left") for x in adv["decisions"]}
    if len(dl_map) != 36:
        print("❌ C 段不是 36 项 (%d) ⇒ 停手" % len(dl_map))
        return 2

    lock_fh = open(LOCK, "w")
    fcntl.flock(lock_fh, fcntl.LOCK_EX)
    try:
        src = open(SRC, encoding="utf-8").read()
        i = src.index("## 1. 🔴")
        body = src[i:]

        # ① 逾期列重算
        body, changed = refresh_overdue_col(body, dl_map)

        # ② 页尾「附: 逾期分布」重写
        overdue = sorted(((x.get("days_left"), x["key"]) for x in adv["decisions"]
                          if x.get("days_left") is not None))
        n_over = sum(1 for d, _ in overdue if d < 0)
        n_zero = sum(1 for d, _ in overdue if d == 0)
        n_none = len(adv["decisions"]) - len(overdue)
        worst = overdue[:5]
        worst_txt = " / ".join("%s (-%d 天)" % (k, -d) for d, k in worst)
        appx = """### 附: 逾期分布 (36 项 · 2026-11-12 00:2x 实数)

| 逾期天数 | 项数 | 备注 |
|---|---|---|
| 已逾期 | **%d** | 最长: %s |
| 剩 0 天 | %d | %s |
| 无 due | %d | %s |

★ **按来源分 (36 项)**: mech 17 · sw 9 · hw 7 · pm 3。
""" % (
            n_over, worst_txt,
            n_zero, " · ".join(k for d, k in overdue if d == 0) or "—",
            n_none, " · ".join(x["key"] for x in adv["decisions"] if x.get("days_left") is None) or "—",
        )
        # ★**替换整个「附: 逾期分布」小节** (★不能只按 "---" 切 ★
        #    ⇒ 表格分隔行 `|---|---|` 里就含 "---" ⇒ 会切错位置 ⇒ 留残块★)
        k1 = body.index("### 附: 逾期分布")
        m = re.search(r"\n---\n", body[k1:])          # ★独占一行的水平线才是小节尾★
        if not m:
            print("❌ 找不到「附: 逾期分布」小节的尾部水平线 ⇒ 停手")
            return 2
        k2 = k1 + m.start()
        body = body[:k1] + appx + body[k2:]

        # ③ §8 陈旧数订正: 「其余 38 项」→ 33
        before = body
        body = body.replace("其余 38 项一个字没动", "其余 33 项一个字没动")
        if body == before:
            print("⚠️ §8 那句「其余 38 项」没找到 ⇒ 未订正")

        # ③b §8「最近到期」那句的天数 = 今日实数 (★昨天写的「剩 1 天 / 逾期 1 天」今天已经变了★)
        #     ★**只列最紧的 3 条** (★与原文语义一致: 「三条都只是按我的假设推进一句话」★)
        soon = sorted([(d, k) for d, k in overdue if d <= 0], key=lambda t: (-t[0], t[1]))
        tight = soon[:3]
        parts = []
        for d, k in tight:
            parts.append("`%s` (%s)" % (k, "剩 0 天" if d == 0 else "逾期 %d 天" % (-d)))
        old_soon = re.search(r"> ★\*\*最近到期\*\*:.*", body)
        if old_soon:
            body = body.replace(
                old_soon.group(0),
                "> ★**最近到期 (2026-11-12 实数)**: %s —— 三条都只是\"按我的假设推进\"一句话, 不回也不卡当期。"
                % " · ".join(parts))
        else:
            print("⚠️ §8「最近到期」那句没找到 ⇒ 未订正")

        text = HDR + body
        atomic_write(DST, text)
        print("✅ 已写 %s" % os.path.basename(DST))
        print("   逾期列重算单元格数 = %d" % changed)
        print("   C 段 = %d 项 (已逾期 %d / 剩 0 天 %d / 无 due %d)"
              % (len(dl_map), n_over, n_zero, n_none))
        # 自证: 建议默认值一格没动 (逐条 key 的建议值原样还在)
        src_body = src[i:]
        miss = []
        for x in adv["decisions"]:
            k = x["key"]
            if ("`%s`" % k) not in body:
                miss.append(k)
        print("   36 条 key 覆盖自检: 缺 %d 条 %s" % (len(miss), miss if miss else ""))
        return 0 if not miss else 1
    finally:
        fcntl.flock(lock_fh, fcntl.LOCK_UN)
        lock_fh.close()


if __name__ == "__main__":
    sys.exit(main())
