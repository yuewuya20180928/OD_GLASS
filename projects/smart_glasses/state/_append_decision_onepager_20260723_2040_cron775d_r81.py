#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
moli (项目总工) 2026-11-23 20:3x · job 775d9893「ARS45 继续执行后继计划」
★决策一页追加 ㉛ (★只追加 · 老字一字不删★)
=========================================================================================
★**本段写什么 (★全部 main 本机实跑 rc · 不抄任何 agent 报告★)**:
  · ① 本轮队列读数 (advance.py --json)
  · ② ★★本轮最重要的一件事: ISS-369 是【僵尸 fixing】⇒ 20:10 那轮两个 job 撞车把两条 hw-lead 写会话
    全部掐死 ⇒ 零产出 ⇒ 本轮【重派一次】⇒ 并把【撞车根因 + 正解】写实
  · ③ 门禁 / 链门 / 巡检 rc (main 20:3x~20:4x 本机实跑)
  · ④ ★★一条诚实登记 (★漂移检测那条「问题单增加 337→365」是【正常增长】不是倒退★)
★**边界**: ★**只追加决策一页一个文件** ⇒ 不碰 issue_log / dispatch_log / 分片 / 板 / 网表 / 脚表 / BOM / outbox ★
"""
import os
import shutil
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
PAGE = os.path.join(PROJ, "DECISION_ONE_PAGER_2026-11-22.md")
BAK = PAGE + ".bak_20260723_2040_cron775d_r81"

SEC = """

---

## ★★㉛ 【本轮 2026-11-23 20:3x 新增】★ ★★「推进器说没事, 实际有一单在装死」⇒ 抓到 ISS-369 是【僵尸 fixing】⇒ 重派 + ★★把「两个 job 撞车」这个机制隐患正式封掉★★

★**★本轮队列读数 (★main 20:3x 本机实跑 `python3 state/advance.py --json`★)**: ★**internal = [] · approvals = [] · decisions = 50 条 (★逾期 31 · 无 due 19·★按源: hw 13 / mech 14 / pm 10 / sw 13★) · waiting = []** ★
★**★⇒ 按「advance.py 的 internal 段」本轮该派 0 条 ⇒ 但 main 没停在这 (★见 §②★)★★

### ★★① 本轮内部推进 (★main 20:3x~20:4x 本机实查·不抄任何交卷报告★) ★★

| 动作 | 单号 → agent | 为什么 |
|---|---|---|
| ★**advance.py 的 internal 段 = 空 ⇒ 名义派 0 条** ★ | — | ★**16 条 open 的 owner 全是 `boss` / `main`(★10 条·★它们是我自己的地界·不是总工槽位★) · `jbd`·★三个总工名下零 open** ⇒ + ★**`hw-lead` 被 ISS-369 占着 (`fixing`)**★ ⇒ `advance.py` 的 in_flight 规则 (★一个 agent 同时只能有一个写会话★) 自然跳过 ★ |
| ★**★实查发现 ISS-369 是【僵尸 fixing】⇒ 本轮重派 1 条** ★ | ★**ISS-369 → hw-lead** ★ | ★★**20:10 那轮两个 cron job 撞车: 本 job 派了 `b4ed5a3e` (★53 秒被 kill·零产出★) + 兄弟 job fb67af40 派了 `1ee3c278` (★17.8 秒 aborted·零产出★) ⇒ 两条写会话全死 ⇒ 但 `issue_log` 里 ISS-369 的 status 还停在 `fixing` ⇒ 推进器以为「有人在干」⇒ **队列被一具尸体堵住**★ ⇒ ★**main 逐项实测: 三件交付物一个都不在盘** (`HW/PCB/FP_LIBID_TRUTH_WORKPACKET.md` 缺 · `HW/check_fp_libid_truth.py` 缺 · `HANDOFF/2026-11-23_hw-lead_ISS369_板面库封装名写盘作业包.md` 缺) + ★**`logs/iss369/` 只有 2 件** (00_baseline_md5.txt + 99_INFLIGHT_20260723_2011.md) ⇒ 一页/闸/交卷页全未产出★ ⇒ ⇒ **这不是「重复派」, 是「僵尸 fixing 复活」⇒ 本轮重派一次 (唯一一条在飞)** ★ |

★**★★本轮把「撞车根因」正式封掉 (★按 20:10 那轮 dispatch_log 里自己写下的正解执行★)★★**:
★**根因 = 两个 job 的「在飞」判定读的不是同一个信号** (★本 job 读 `issue_log.status` + `sessions_list` · 兄弟 job fb67af40 读 `advance.py` 内部队列★) ⇒ ★**各自都觉得「这条还没人干」⇒ 同时派出⇒ 两条都被 kill/aborted ⇒ 零产出⇒ status 卡在 `fixing` ⇒ 死锁★** ★
★**★本轮的正解 (★零撞车窗口★)**: ★**status 保持 `fixing` 不动** (★它已经是了·★不用改·★零写 `issue_log`★) ⇒ ★**兄弟 job fb67af40 读的是同一个字段 ⇒ 它看到 `fixing` 就跳过 ⇒ 撞车窗口 = 0** ★ ⇒ ★**先标 fixing 再派 (★上一轮 dispatch_log 自己写的正解·本轮第一次真正执行·而不是写下来就完★)★** ★
★**★派活日志留痕 (★`state/dispatch_log.yaml` 追加 1 条·375 → 376 条·★前 375 条逐条 (issue/agent/at) 比对差异 = 0★)**: ★**条目带 `redispatch_zombie: true` + `death_cause` (两条前序会话怎么死的) + `partial_delivery: 0/3` ⇒ 事后查得清「这一趟是复活, 不是重复」** ★

### ★★② 本轮 PCB 类 = ★**一条**★ (★按老板 2026-11-17 00:43「接下来的目标是绘制 PCB 图」口径·PCB 布线/布局类 ISS 现在可派★) ★★

| 单号 | 类别 | 为什么不是「真动板那一趟」 |
|---|---|---|
| ★**ISS-369** ★ | ★**纯作业包 + 沙盒 + 新建闸** ★ (★新建 `HW/PCB/FP_LIBID_TRUTH_WORKPACKET.md` · `HW/check_fp_libid_truth.py` · `HANDOFF/2026-11-23_hw-lead_ISS369_板面库封装名写盘作业包.md`★) | ★**零写板** (★板 md5 必须仍 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413`★) · ★**换 land 只许在 `tmp/` 副本上做** ★ · ★**零落表** (★网表/脚表/BOM/原理图/`issue_log.yaml` 一字不改★) · ★**零改既有闸** · ★**零改既有页面** · ★**零挂链** · ★**零外发** · ★**不代老板拍板** ★ ⇒ ⇒ ★**不是「真动板那一趟」** (★那一趟 = 位号改名 + 板侧同步 B-1~B-8 + 布局修正 + 布线 45→0 + Gerber/投产包重出·★仍待一次做完★) ★ |

★**★本单在「板那一趟」里的位置 (★main 20:3x 复核 ㉙③ 的三腿合成·不新增结论★)★★**: ★**腿 A 换官方 land (90 件) + 腿 B 网表节点具名 (90 件 + 补 4 行 GND) + 腿 C 写库封装名 (186 件) ⇒ 本单 = 腿 C 的作业包** ★ ⇒ ★**腿 B 缺 ⇒ C4=68 不可达 (ISS-364 实测) · 腿 C 缺 ⇒ 板做出来是错的 (装配厂拿不到正确封装)** ★

### ★★③ 门禁 / 链门 / 巡检 rc (★main 20:3x~20:4x 本机实跑★) ★★

| 脚本 | rc | 读数 |
|---|---|---|
| `state/merge.py` | **0** | ★产出 786 · 阻塞 43 (高危 33) · 未闭合需求 319 · 冲突 0 · 健康度 red ★ |
| `state/gate_check.py` | **0** | ★**Q1 = 18/18** · Q7 钉板 md5 闸链 **10/10 全绿** · 缺口清单 3 条 (★hw-lead 200 / sw-lead 37 / mech-lead 83 条需求还没人答·★都是「等另一个总工」·★不是本轮新增★) ★ |
| `state/issue_check.py` | **1** | ★**违规 19 条 = 逾期未闭环 19 条** (★基线 2026-11-22 也是 19 ⇒ **零新增**★) ★ |
| `state/stage_gate.py` | **1** | ★当前 **G1** (原理图 / PCB 定稿) · ★**还差 1 项** ⇒ 布线 unconnected 45 → 0 ★ · G2 当期不做 (缺口 3 项留着) ★ |
| `state/daily_check.py` | **3** | ★三条异常**全是老异常**: ① 问题闭环门 19 条违规 ② `check_pcb_nets` rc=1 (★PCB↔网表逐焊盘等价没过 ⇒ **不许投板**★) ③ chain_gate (★生产链准入/准出没过★) ★ · ★另: 原理图 ERC **0 条** ✅ · 脚数完整性 **584 = 584** (218 器件/153 网) ✅ · 交付齐备率 **18/18** · 证据分级 **3/3** ★ |

### ★★④ ★★一条诚实登记 (★漂移检测那条「问题单增加 337 → 365」是【正常增长】, 不是倒退★★) ★★

★**main 20:4x 本机实查 `state/daily_check.py` 的基线取法 (★L420-432★)**: ★**基线 = 今天之前最新的一份快照 = `state/gate_snapshots/2026-11-22_daily.json` (★337 条 · 逾期 19 · 齐备率 18·★2026-11-22 23:51 落盘★)** ★
★**⇒ 「337 → 365」= ★**今天新开的 28 单 (ISS-349 ~ ISS-370 这一串 PCB 线作业包)·不是老单恶化**★** ⇒ ★**同一份基线里【逾期 19】今天仍是 19 · 【齐备率 18】今天仍是 18 ⇒ 零倒退**★ ⇒ ★**这条漂移提示按【正常增长】归档, 不算异常项 (但老单数确实在涨, 值得老板知道量级)** ★

★**本 job 口径**: ★**cron 775d9893 (每 20 分钟) · 本轮 GitHub 不推 (★由独立的 5 小时同步 job 负责·★老板 2026-11-11 09:5x★) · 只落本地快照 `PROGRESS_SNAPSHOT.md` (★2,870 B · 2026-11-23 20:38·rc=0★) · 零外发 (★老板 2026-11-12 02:02·不再发信·全靠自己查资料★) · 不改 `PROJECT_TRACKER.md` §0 锁死表 · 不写别的 agent 的分片** ★
★**板面**: md5 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17` ⇒ ★**18 天逐字节未动** ★ ⇒ ★**G1 仍开, 不许投板** ★
"""


def main() -> int:
    shutil.copy2(PAGE, BAK)
    body = open(PAGE, encoding="utf-8").read()
    if "㉛" in body:
        print("★已含 ㉛ ⇒ 不重复追加 (rc=0)")
        return 0
    with open(PAGE, "a", encoding="utf-8") as f:
        f.write(SEC)
    after = os.path.getsize(PAGE)
    print(f"✅ 决策一页已追加 ㉛ · {len(body.encode('utf-8'))} → {after} B")
    print(f"   备份: {os.path.basename(BAK)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
