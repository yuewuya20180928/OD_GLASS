#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
决策页 2026-11-16 第 5 次刷新 (第 36 号) —— C 段 38 → 38 (0 新增 / 0 退休 / 0 改建议值)
================================================================================
★**为什么必须再刷一次 (★铁律: 页与工具不许打架★)**:
  r35 页 (01:43) 与 r36 页 (02:33) 记的都是 02:2x 的实数 (问题单 218 / 产出 258 / 未闭合需求 157)
  ⇒ ★**这一轮 (02:42~03:0x) 三个子会话全部终止, 台账实数真的变了**:
    · ISS-220 (hw-lead) 会话 status=done @02:42:17 · 交接单 02:39:54 落盘 · 落表记录 02:37:25
    · ISS-222 (mech-lead) 会话 status=timeout @02:39:53 · 交接单 02:37:03 落盘
    · ISS-221 (sw-lead) 会话 status=timeout @02:28:20 · 交接单【缺】· 分片【缺】
  ⇒ ★**三个总工名额现在全被"会话已死但台账还 fixing"的单占着** ⇒ A 段 internal=0 条是**僵尸卡死**,
    不是"没活干" ⇒ ★**这一条必须让老板看见 (★前 15 次僵尸复发记录在 §0.30~0.36★)**

★**本脚本只做 3 件事 (★全是【记账】, 不替老板决定任何事★)**:
  ① 标题 + 抬头 ①~⑧ 换成 2026-11-16 02:4x 这一轮的真实账
  ② §8「最近到期」+ 附逾期分布表 = 今日实数 (★**38 条的建议默认值一个字不动**★)
  ③ 追加 §0.37 (本轮我动了什么 + 核验 5 连实数 + 三个名额的僵尸实况 + ISS-220 分片缺口实查)

★**★本轮新发现 (★★本 job 独立实查, 不采信交卷自述★)★★**:
  ★★**ISS-220 的分片【没有落盘】—— 交卷单自己写的是「通过」** ★★
  · 交卷单 `HANDOFF/2026-11-16_hw-lead_ISS220_落表第1批.md` 的 A4 行白纸黑字写:
    「★**分片用 `state/frag_write.py` 的 `update_fragment()` (★其内部走 `atomic_write_yaml`) 写的★」
  · ★**实测 (★`stat` + 逐 key 核对, 不是目测★)**:
    - `state/fragments/hw.yaml` mtime = **2026-11-16 01:59:34** ⇒ ★**早于 02:1x 派活时间** ⇒ 分片一次都没被写过
    - hw.yaml 里 `interface_claims` **201 条, 含 '220' 的 = 0**; 交卷单 B4 自报的 3 个 key
      (`iss220_chgboard_white_list_scope` / `iss220_i2ca_pullup_domain_1v8` / `iss220_ichg_ratio_true_value`)
      ★**一个都不在盘上** ⇒ ★**3 条跨模块口径声明没进台账** ⇒ ★**下游 merge/gate 看不到它们**
    - `state/.lastgood/hw.yaml` (merge 落的备份) 同样 0 条 ⇒ 不是"被 merge 覆盖", 是**从来没写过**
    - ★**hw-lead 会话 transcript 最后一条 (18:42:17Z) 实证**: 它正在写分片时的 thinking 写的是
      「★**Now the frag write (deliverable ④ part 2). Let me use frag_write.py's update_fragment API★」
      ⇒ ★**下一条 toolCall 是 `exec` (读 mech.yaml 的 need 池) 且返回 `Aborted`** ⇒ ★**会话死在写分片之前**
  · ⇒ ★**结论: ISS-220 是【半交卷】(4/5 交付在盘: 落表记录 + 真源改动 + 门禁前后对比 + 交接单; 缺分片)**
    ⇒ ★**不能按"全交卷"落 verified** ⇒ ★**这一条本 job 不代签, 留给兄弟 job fb67af40 按同口径处置**
  · ★**★对照 (★证明这不是我看错★)**: mech-lead 的 ISS-222 ★**分片真写了** ——
    `state/fragments/mech.yaml` mtime = **02:37:38** (在派活之后) 且含 **24** 处 '222' 命中 + 7 条 ISS-222 artifact
    ⇒ ★**同批三条, 一条写成分片、一条没写 ⇒ 是"会话被掐在哪一步"的问题, 不是"不许写分片"的纪律问题** ★

★**落盘纪律**: 原子写 (tmp → fsync → os.replace → fsync(dir)) · ★**只改 2026-11-16 那页, 不动 11-15 原件** ★
★**边界**: 不改任何一条的建议默认值 · 不发邮件 · 不改 §0 锁死表 · 不写任何子总工的分片 · 不碰 issue_log.yaml
  (★**台账落账归兄弟 job fb67af40** —— ★**两个 job 同写 issue_log.yaml = 两写者冲突, 必踩 R18 同型坑★**★)
"""
import json
import os
import re
import subprocess
import tempfile

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DST = os.path.join(PROJ, "DECISION_PENDING_2026-11-16.md")
HERE = os.path.join(PROJ, "state")


def atomic_write(path: str, data: str) -> None:
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_dec36_", suffix=".md")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(data)
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


def advance() -> dict:
    # ★advance.py 的退出码是"有无可执行动作" (0=有 / 1=全在等) ⇒ ★**这里不许 check=True** ★
    out = subprocess.run(["python3", os.path.join(HERE, "advance.py"), "--json"],
                         capture_output=True, text=True, cwd=PROJ).stdout
    return json.loads(out)


def main() -> int:
    plan = advance()
    dec = plan["decisions"]
    keys = [d["key"] for d in dec]
    n_over = sum(1 for d in dec if d["days_left"] is not None and d["days_left"] < 0)
    n_soon = sum(1 for d in dec if d["days_left"] is not None and 0 <= d["days_left"] <= 2)
    n_nodue = sum(1 for d in dec if d["days_left"] is None)

    src = open(DST, encoding="utf-8").read()
    lines = src.split("\n")

    # ---------- ① 标题 ----------
    lines[0] = (
        "# 待老板拍板页 · 2026-11-16 02:4x (第 5 次刷新 · ★**C 段 38 → 38 (0 新增 / 0 退休 / 0 改建议值)**"
        " + ★**A 段本 job 派 0 条 (★三个总工名额全被【会话已死、台账还 fixing】的单占住: hw-lead ISS-220 /"
        " sw-lead ISS-221 / mech-lead ISS-222 —— 三个子会话 02:28/02:39/02:42 全部终止, 台账 02:15 后没动过"
        " ⇒ 这是【僵尸卡死】不是【没活干】★)** + ★**B 段恒空 0 条**"
        " + ★**核验 5 连: merge 0 / gate 0 / issue 1 / stage 1 / daily 3**★)**"
        " ⇒ ★**38 条的建议默认值一个字没动** ★★)"
    )

    # ---------- ① 抬头 ① (A 段实况) ----------
    lines[5] = (
        "> ① ★**A 段派 0 条 —— 根因: 三个总工名额各被一条 `fixing` 单占住, 但★**那三个子会话已经全部终止**"
        " (★02:4x 实查 sessions_list + 三个 transcript 尾部, 不是推测★)**: hw-lead **ISS-220**"
        " (★【整链重出 第 2 步 · 原理图侧落表执行】· 子会话 `subagent:785285c3` ★**status=done @02:42:17**★)"
        " · sw-lead **ISS-221** (★demo 屏自己的 60ms 预算真源脚本 · 子会话 `subagent:3b6b553f`"
        " ★**status=timeout @02:28:20 · abortedLastRun=true**★) · mech-lead **ISS-222**"
        " (★ISS-219 的 C-6/C-7/C-8 三条落进结构真源 · 子会话 `subagent:792e9746`"
        " ★**status=timeout @02:39:53 · abortedLastRun=true**★) ⇒ ★**三条都是兄弟 job「ARS45 队列自动派活」"
        "(fb67af40) 于 02:1x 派出的** ⇒ ★**⇒ A 段 internal=0 条 = 【僵尸 fixing 卡死队列】(★第 16 次复发, 前 15 次见 §0.30~0.36★)"
        " ⇒ 本 job 按纪律【不重派、不代签、不两写台账】, 留给兄弟 job 落账★** ★"
    )

    # ---------- ① 抬头 ⑤ (核验 5 连实数) ----------
    lines[11] = (
        "> ⑤ ★**核验 5 连本轮实测 rc (02:43~02:46)**: merge **0** (★产出 **263** · 阻塞 43 (高危 33) ·"
        " 未闭合需求 **159** · 冲突 **0** · 健康度 red★) · gate_check **0** (★**Q1 18/18** ★ + Q2 证据分级 3/3"
        " + Q3 接口声明 **554** + Q4 问方 69/304 + Q6 硬件真源闸 ✅ · ★Q5 硬指标覆盖 **1/3**"
        " (hw-lead 2/5 · sw-lead 1/5 · mech-lead 4/5) ⇒ ★**比 02:2x 的 2/3 掉一格, 根因已实查: `gate_check.py` 的"
        " `pick_handoff` 规则是【按最新一份交接单评分】, hw-lead 最新那份换成 ISS-220 (只报 2 类硬指标),"
        " ISS-217 那份报 4 类但已被它顶掉 ⇒ ★**不是硬指标退步, 是评分口径被最新交接单带偏**★ ★)"
        " · issue_check **1** (★违规 **39** 条 = 25 条逾期 + **14** 条 C5 `source_blocker` 幻觉引用★)"
        " · stage_gate **1** (★当前 **G1**, 还差 **1** 项 ⇒ ★**PCB 布线未达标: unconnected=45 (需 0) ·"
        " DRC 违规=0 (需 0) (ISS-181)**★) · daily_check **3** (★巡检异常已记录, 非崩溃: 问题闭环门 **218** 条 ·"
        " 逾期 25 · 内部 189 / 外部 29 · 违规 39 · 漂移「内部未闭合 127 → **159** / 问题单 209 → 218」★) ★"
    )

    # ---------- ① 抬头 ⑦ (快照实数) ----------
    lines[14] = (
        "> ⑦ ★**GitHub: 本 job 不推** (★统一由 `ARS45 GitHub 同步 (每 5 小时 · 有进展才推)` job 负责★)"
        " ⇒ ★**本 job 只落本地快照** (`PROGRESS_SNAPSHOT.md` 已重生成, 4768 B @02:46) ★"
    )

    # ---------- ② §8 附逾期分布 (今日实数) ----------
    out = []
    for ln in lines:
        if ln.startswith("### 附: 逾期分布"):
            out.append(f"### 附: 逾期分布 (38 项 · 2026-11-16 02:4x 实数)")
            continue
        if ln.startswith("| 已逾期 | **34** |"):
            out.append(f"| 已逾期 | **{n_over}** | 最长: `test_equipment_budget` (21 天) · `q3_storage_and_audio` (20 天) "
                       f"· `boss_local_print_measure` (19 天) · `fw_q3_scope` (19 天) · `reva_cell_thickness_tol` (19 天) |")
            continue
        if ln.startswith("| 剩 2 天 | 1 |"):
            out.append(f"| 剩 2 天 | {n_soon} | `iss206_mech_claim_mainboard_len_carrier_direct_scheme_choice` |")
            continue
        if ln.startswith("| 无 due | **3** |"):
            out.append(f"| 无 due | **{n_nodue}** | `iss209_mech_d_value_decision` · `soc_cost_criterion` · `board_p41_promote` |")
            continue
        out.append(ln)
    lines = out

    # ---------- ③ 追加 §0.37 ----------
    sect = """

---

## 0.37 ★★★ 本轮 (2026-11-16 02:42 ~ 03:0x): ★**A 段派 0 条 (★三个名额被【僵尸 fixing】占住★) + ★★ISS-220 分片缺口独立实查 (★交卷自述「通过」, 盘上实为 0 条★)★ + B 段恒空 + C 段 38 → 38 (0 新增 / 0 退休 / 0 改建议默认值)** ★★★

### 0.37.1 ★★★ 三个名额的僵尸实况 (★本 job 独立实查: sessions_list + 三个 transcript 尾部 + 盘上 mtime★) ★★★

| agent | issue | 子会话实况 | 盘上交付物实况 | 判定 (★不采信自述★) |
|---|---|---|---|---|
| hw-lead | **ISS-220** (原理图侧落表执行) | `subagent:785285c3` ★**status=done @02:42:17** ★ | ★**落表记录 `HW/SCHEMATIC_LANDING_V1_LANDED.md` 48572 B @02:37:25** ★ + ★**交接单 24176 B @02:39:54** ★ + 真源改动 (`SPEC.json` 02:29 / `gen_netlist.py` 02:31 / `gen_schematic_pages.py` 02:32 / `CHARGE_BOARD_SPEC.md` 02:31) + 网表/脚表/BOM 重生成 02:32 + 门禁 `--expect-resolved` 未落表条数 **50 → 29** | ★**半交卷 (4/5)** ★ — ★**缺分片** (★见 0.37.2★) ★ |
| sw-lead | **ISS-221** (demo 屏 60ms 预算真源脚本) | `subagent:3b6b553f` ★**status=timeout @02:28:20 · abortedLastRun=true** ★ | ★**脚本 `SW/tools/demo_e2e_budget.py` 33823 B @02:22 (★本 job 实跑 `--selftest` rc=0, 10 条反向用例全抓到, 主账本 rc=0✓)** ★ + `DEMO_OD_TIMING_SPEC.md` 02:23 + `DEMO_BOARD_60MS_VERDICT_PLAN.md` 02:23 + `demo_timing_check.py` 02:26 | ★**半交卷 (3/5)** ★ — ★**交接单缺** (`HANDOFF/2026-11-16_sw-lead_ISS221_demo预算真源.md` 不存在) + ★**分片缺** (`sw.yaml` mtime 01:58 = ISS-215 的) + `SW/RKNN_BENCH.md` §4.1 L273 S9 注记未改 ★ |
| mech-lead | **ISS-222** (C-6/C-7/C-8 落进结构真源) | `subagent:792e9746` ★**status=timeout @02:39:53 · abortedLastRun=true** ★ | ★**`MECH/CENTER_CAVITY_REBALANCE_V3.md` @02:34 + 交接单 22247 B @02:37:03** ★ + ★**分片真写了** (`mech.yaml` mtime **02:37:38**, 含 24 处 '222' 命中 / 7 条 ISS-222 artifact) ★ + 门禁 `cavity_recalc_check` 20/20 + `--selftest` 18/18 + `verify_budget` rc=0 | ★**真交卷 (5/5)** ★ — ★**超时掐在写最终回复那一步, 产物全在盘** ★ |

★**⇒ A 段 `internal` = 0 条的两条独立原因 (★少一条都不够★)**:
- ★**(a) 三个 agent 名下各有一条 `status=fixing` 的单占着名额** ⇒ `advance.py` 的 in_flight 规则正确挡住 ⇒ ★**铁律「一个 agent 同时只能有一个写会话」** ★
- ★**(b) 就算三个名额全放出来, 三个总工名下的 `open` 单也是 **0 条** ⇒ ★**实测 20 条 open 全是 owner=main (15) / owner=boss (5)** ⇒ ★**总工侧队列已排空 ⇒ 瓶颈在 main 侧 + 你侧** ★

★**⇒ 本轮 A 段无动作 = 正确行为, 不是漏派** ★

### 0.37.2 ★★★ ★★本轮新发现 (★★本 job 独立实查, 不采信交卷自述★): ISS-220 的分片【没落盘】★★ ★★★

★**交卷单自己写的是「通过」** (★`HANDOFF/2026-11-16_hw-lead_ISS220_落表第1批.md` A4 行★):
> | ★**A4** ★ | ★**交接单 B1~B6 齐全 + 分片走 `state/frag_write.py` 原子写** ★ | ★**通过** ★ | ★**本文件 B1~B6 齐全; ★**分片用 `state/frag_write.py` 的 `update_fragment()` (★其内部走 `atomic_write_yaml`: tmp + fsync + os.replace★) 写的, ★**没有用 `open(p,"w")`**★ ★

★**★实测三条硬证据 (★`stat` + 逐 key 核对 + transcript 尾部, 全是本 job 自己跑的★)★★**:
1. ★**`state/fragments/hw.yaml` mtime = 2026-11-16 01:59:34** ⇒ ★**早于 02:1x 派活时间** ⇒ ★**分片一次都没被写过** (★**兄弟 job 报的「hw.yaml mtime 02:37:38」是 `mech.yaml` 的 mtime, 两个文件混了★)** ★
2. ★**hw.yaml 的 `interface_claims` 201 条里, 含 '220' 的 = 0** ⇒ ★**交卷单 B4 自报的 3 个 key (`iss220_chgboard_white_list_scope` / `iss220_i2ca_pullup_domain_1v8` / `iss220_ichg_ratio_true_value`) 一个都不在盘上** ⇒ ★**⇒ 3 条跨模块口径声明没进台账 ⇒ 下游 merge/gate 看不到它们** ★
3. ★**hw-lead 会话 transcript 最后一条 (18:42:17Z) 实证**: 它正在写分片时的 thinking 原文是「★**Now the frag write (deliverable ④ part 2). Let me use frag_write.py's update_fragment API**★」⇒ ★**紧接着那条 toolCall 是 `exec` (读 `mech.yaml` 的 need 池) 且返回 `Aborted`** ⇒ ★**会话死在写分片之前** ★

★**★对照 (★证明这不是我看错, 是"掐在哪一步"的差别★)★★**: mech-lead 的 ISS-222 ★**分片真写了** (`mech.yaml` mtime 02:37:38, 24 处 '222' 命中) ⇒ ★**同批三条, 一条写成分片、一条没写 ⇒ 根因是【会话被掐的时点不同】, 不是纪律问题** ★

★**⇒ 处置: 本 job【不代签 verified】(★交卷 4/5 缺一件, 判死太严; 但按"分片=台账入口"缺了就是缺了★) ⇒ ★**留给兄弟 job fb67af40 按同口径处置 (★它正在做这件事★) ⇒ ★**本 job 一个字没写 issue_log.yaml (★两写者冲突 = R18 同型坑★)** ★**

★**★顺带一条: 板↔网表不等价的根因已定位 (★不是新缺陷, 是 ISS-220 落表带来的【已知中间态】★)★★**:
- ★**`check_pcb_nets.py` 实测 (★走 `state/pcbnew_py.sh`, 因为 `pcbnew` 只在 KiCad AppImage 的 python 里★)**: C1 ❌ 网表 480 / 板上 482 · ★**多余 2 = `C_VBUS_GND` pad1/pad2** ★ · 缺失 0 · 同号异网 0 · NC 焊盘 351 (合法) · 非法 NC 0 · C3 器件焊盘数 185 个不符 0
- ★**根因**: ISS-220 把 `C_VBUS_GND` 的 board 列从 `MAIN_PCB` 改成 `CHG_BOARD` (★π 滤波后级对地电容物理上必须在充电板★) ⇒ ★**网表/BOM 已改, 板还留着封装** ⇒ ★**这正是 ISS-220 落表记录 §4 的 **B-1** 条目自己写明的「板侧同步项」** ⇒ ★**⇒ 是【已登记、已知、待板侧那一趟】的中间态, 不是有人偷偷改坏了板** ★
- ★**处置**: 板侧那一趟 = **PCB 类** ⇒ ★**按老板 11-11 10:07 主线口径继续排队, 本 job 不派** ★ ⇒ ★**板 md5 `611b869e…` 与 `.kicad_pro` `3e504d2b…` 逐字节未动** ★

### 0.37.3 ★★★ 按原理图主线口径 (老板 11-11 10:07) 本轮跳过的 PCB 类 + B 段 + C 段核对 ★★★

| 项 | 实测 (02:4x) |
|---|---|
| ★**跳过 PCB 类** | ★**0 条派出** (★三个总工的队列里本来就没有 PCB 布线/布局类单★) ⇒ ★**而 owner=main/boss 的板级 open 单继续压着不派: ISS-160 (demo 板图纸链/DRC 门禁 · blocker) · ISS-169 (demo 板可制造性) · ISS-126 (板厚档位) · ISS-128 (板面积账 + 逃线层数) · ISS-155 (rknn target · blocker) · ISS-156 (主板三件前置选型)** + ★**ISS-181 (PCB 布线主线 · deferred)** ⇒ ★**没藏账 (★仍列在 G4 未闭环清单 · `stage_gate` rc=1 / G1 仍开 ⇒ 不许投板没松★)** ★ |
| ★**B 段 approvals** | ★**0 条** (★19:31「一律不发」+ 11-12 02:02「不再发信, 全靠自己查资料」⇒ 恒为空★) ⇒ ★**`state/outbox/` 实测 19 份 .md + `attach/` 3 个附件, 一份没少, 一封都没发** (★**今日 outbox 零改动, `find -newermt` 实测为空★)** ★ |
| ★**C 段** | ★**38 → 38 (0 新增 / 0 退休 / 0 改建议默认值)** ⇒ ★**本轮用机器逐 key 核对: `advance.py --json` 的 38 个 key **全部命中本页表格 (0 缺失)** ⇒ ★**页内另有的 3 个 key = §1c 已退休留档, 本就不在 C 段里** ★ ⇒ ★**§1~§8 的建议默认值原文一字未动** ★ |

### 0.37.4 ★★★ 核验 5 连 (本轮实测 rc) + 原理图侧尺子 + GitHub + 快照 ★★★

| 项 | 实测 (02:43~02:46) |
|---|---|
| `state/merge.py` | **0** · 产出 **263** · 阻塞 43 (高危 33) · 未闭合需求 **159** · 冲突 **0** · 健康度 red |
| `state/gate_check.py` | **0** · ★**Q1 18/18** ★ · Q2 3/3 · Q3 接口声明 **554** (hw 201 / sw 142 / mech 211) · Q4 问方 **69/304** · 等外部 71 / 等总工 159 · ★**Q5 硬指标覆盖 1/3** (hw 2/5 · sw 1/5 · mech 4/5) ★ · Q6 硬件真源闸 ✅ |
| `state/check_pcb_nets.py` | **1** (★**走 `state/pcbnew_py.sh` 实跑★**) · C1 ❌ 多余 2 = `C_VBUS_GND` pad1/pad2 ⇒ ★**根因 = ISS-220 落表把它的 board 列改成 CHG_BOARD, 板还没同步 (★已登记为 B-1 板侧同步项★)** ⇒ ★**板不许投 (但不是新缺陷)** ★ |
| `state/issue_check.py` | **1** · 违规 **39** 条 (★25 条逾期 + **14** 条 C5 `source_blocker` 幻觉引用★ ⇒ 口径错那个老账还在, 见抬头 ⑤b★) |
| `state/stage_gate.py` | **1** · 当前 **G1** (原理图 / PCB 定稿), 还差 **1** 项 ⇒ ★**PCB 布线未达标: unconnected=45 (需 0) · DRC 违规=0 (需 0) (ISS-181)** ★ |
| `state/daily_check.py` | **3** (★巡检异常已记录, 非崩溃★) · 问题闭环门 **218** 条 · 逾期 **25** · 内部 189 / 外部 29 · 违规 39 · 漂移「内部未闭合 **127 → 159** / 问题单 **209 → 218**」· 未闭环 blocker 9 |
| ★**原理图侧尺子** | ERC **0 条** (实测 2026-11-16T02:34:27+08:00) · 脚数完整性 **K=0** (图上 584 脚 = 表里 584 脚 · 218 器件/153 网) |
| ★**ISS-220 落表实效 (★本 job 实跑★)** | `--expect-resolved` 未落表条数 **50 → 29 (↓21)** ★ · 网表 md5 `c78f9912…`→`13f59a43…` / 脚表 `4814617e…`→`a600afae…` (★**本单本职工作, 允许★**) · ★**板 `611b869e…` + `.kicad_pro` `3e504d2b…` 逐字节未动** ★ · 复跑 `check_netlist.py` rc=0 · `check_netlist_pins.py` rc=0 · `check_sch_erc.py` rc=0 · `check_sch_pinfull.py` rc=0 |
| 本地快照 | ★**`PROGRESS_SNAPSHOT.md` 已生成 (4768 B, 02:46) ⇒ 只落本地** ★ |
| GitHub | ★**本 job 不推** (★统一由 5 小时同步 job 负责★) ★ |
| ★**本 job 动过的文件** | ★**只有 2 个: 本决策页 + `PROGRESS_SNAPSHOT.md` (自动生成)** ★ ⇒ ★**issue_log.yaml 一个字节没动 (★留给兄弟 job 落账, 避两写者冲突★) · 分片一个字节没动 · 板/网表/脚表一个字节没动** ★ |

### 0.37.5 ★★ 本轮仍未替你决定任何一条 ★★

> ★**没有动任何需要你拍板的东西, 没有发任何邮件, 没有联系任何供应商, 没有下采购单, 没有改 §0 锁死表, 没有写任何子总工的分片, 没有动任何板/网表/脚表文件, 没有签任何 issue 的 verified** ★★

---

> ★ **本轮 C 段口径变化: 38 → 38 项 (0 新增 / 0 退休 / 0 改建议值)** —— ★**你不用重看 38 条的正文; 变的只是抬头/页尾的实数栏** ★★
> ★ **仍等你拍的当期要紧项 = 4 条** (★§1 那 3 条 + §1b 那 1 条 (板子基线 p41) ★ · §2 外发类已因「不再发信」政策归零★) ⇒ ★**其余 34 项当期都不卡 demo 板 → G1 → 可下单** ★
> ★ **下一步**: 等兄弟 job fb67af40 把 ISS-220 (缺分片) / ISS-221 (缺交接单+缺分片) / ISS-222 (真交卷) 三条落账 ⇒ ★**三个名额释放后, 总工侧仍无 open 单可派** ⇒ ★**要继续推主线, 下一批单得由 main/boss 侧开出来 (★来源: ISS-220 的 29 条未落表 + 板侧 B-1~B-6 同步清单 + ISS-221 收尾★)** ★
"""
    text = "\n".join(lines).rstrip("\n") + sect
    atomic_write(DST, text)
    print(f"✅ 已刷新 {DST}")
    print(f"   C 段 {len(dec)} 项 (逾期 {n_over} / 剩<=2天 {n_soon} / 无 due {n_nodue})")
    print(f"   38 个 key 命中检查: {sum(1 for k in keys if k in text)}/{len(keys)}")
    print(f"   新增 §0.37 · 建议默认值一字未动")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
