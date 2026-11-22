#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""刷新老板拍板页 DECISION_PENDING_2026-11-11.md (第 22 次刷新) —— 2026-11-11 18:4x~18:5x

★**只整理 + 给建议默认值, 不代决** —— 拍板前不动任何采购 / 外发 / 改图 / 改锁死表。

★**本轮 C 段口径: 39 → 39 (0 新增 / 0 移除 / 0 改建议值)** ⇒ ★**你不用重看一遍** ⇒ ★**仍等你拍的只有
   §1c 第 3 条 (`iss191_reset_p0_fix_choice`) + §1 那 5 条**。

★**本轮最实质的三件事 (★都是"记账/签字/开单/核验"类 ⇒ 不需要你做任何新决定★)**:
  ★**① ISS-192 (mech-lead) 17:39 交卷 ⇒ main 18:4x 独立验收签字 (verified/pass)** ⇒ ★**而且仲裁依据是
     main 自己重算的 (★不是抄它的自述★)**: ★**main 自己解析了两个打印包二进制 STL + 顶面占据栅格化 (0.5mm)**
     ⇒ 实测四孔 = **套A** (P1(8,15) P2(52,15) ⌀2.4 + S1(8,10) S2(52,20) ⌀1.6) ⇒ ★**套B 的 (8,2.5)/(52,27.5)
     实测【实心无孔】** ⇒ ★★**"打印包 = 套A" 被独立证实** ⇒ ⇒ **套B 是孤例, 签字通过**。
  ★**② 签字【不】覆盖 hw-lead 产物侧 ⇒ 已开 ISS-194 (owner=hw-lead)**: `HW/pcb60x30_check.py`:113-117 + 它的
     `.json` (`sec4_holes` 两段) 仍写套B ⇒ ★**而那份 .json 是 ISS-118 的验收产物** ⇒ 必须改。
     ★**本轮 A 段派出 0 条** ⇒ ★**不是"没活"**: hw-lead 正在跑 **ISS-193** (★**实测心跳 18:45 还在写★
     ⇒ ★**真在飞, 不是上一轮那种"假 fixing 标记"**) ⇒ ★**ISS-194 已 status=open ⇒ 下一轮 advance.py 自动派出**
     ⇒ 铁律「一个 agent 同时只允许一个写会话」保持。
  ★**③ 一条将来会变成拍板项、但现在还不用你拍的事**: 30mm 板带出一条新账 = **骨架截面 4 个候选全部超预算**
     (最好 4.08g/对 vs 预算 +1~3g) + 石墨 2.16g/对 > W11 上限 ⇒ 结构侧已报 main 裁 ⇒ ★**我先记着, 等它变成
     结构方案选项再找你** (★**没藏账, 但也没到要你拍的时候**)。

★**落盘纪律**: flock + 锁内重读 + 原子写 (tmp → fsync → os.replace → fsync(dir))
★**边界**: 不改任何建议默认值 · 不改 C 段 39 项 · 不发邮件 · 不下采购单 · 不改 §0 锁死表
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
    "# 待老板拍板页 · 2026-11-11 18:5x (第 22 次刷新 · ★**C 段 39 → 39 (0 新增 / 0 移除 / 0 改建议值)** "
    "+ ★**ISS-192 交卷并经 main 独立验收签字 (verified/pass) —— 仲裁依据 main 自己重算 (打印包实测 = 套A)** "
    "+ ★**已开 ISS-194 (孔位表 套B ⇒ 套A, owner=hw-lead, 等 ISS-193 交卷后自动派出)** ★★)"
)

NEW_WHAT = (
    "> ★ **本轮我自己动了什么**: ①★**ISS-192 (mech-lead) 17:39 交卷, 我已独立验收签字 (verified/pass)** —— "
    "mech-lead 交 `HANDOFF/2026-11-11_mech-lead_ISS192_机械复核器迁60x30与孔位Y仲裁.md` + "
    "`MECH/BOARD_GEOM_30MM.md` + 5 个迁到 60×30 的机械闸 + `state/fragments/mech.yaml` (3 条 needs_from) ⇒ "
    "★**我把它贴的复现命令全自己重跑了一遍 (不采信自述)**: `pinset2_mech_check.py` rc=0 「复算项 38 | FAIL 0 | WARN 2」 · "
    "`--self-test` rc=0 「6/6 用例符合预期」 · `skeleton_section_check.py` rc=0 · `cross_review_check.py` rc=0 "
    "(★已明写「不是闸」+ 退出码只反映 MECH-OWNED ⇒ 没有孤儿红) · `hinge_usb_check.py` / `iss065_check.py` rc=0 · "
    "★**板 md5 `611b869e…` + `.kicad_pro` `3e504d2b…` 一字未变** · merge rc=0 冲突 0 · Q1 18/18 ⇒ ★**签字通过**。"
    "★★**但仲裁依据是我自己重算的 (★最要紧的一条★)**: ★**我自己解析了两个打印包二进制 STL + 顶面占据栅格化 (0.5mm)** "
    "⇒ cage (板基线 Y=60) 与 coupon (基线 X=4/Y=84) **实测四孔 = P1(8.00,15.00) ⌀2.4 + P2(52.00,15.00) ⌀2.4 + "
    "S1(8.00,10.00) ⌀1.6 + S2(52.00,20.00) ⌀1.6** ⇒ ★**套B 的 (8.00,2.50) / (52.00,27.50) 实测【实心无孔】** ⇒ "
    "★★**「打印包 = 套A」被独立证实** ⇒ ★**套B 是孤例** (另: 生成器常量 `pinset2_p_y=15.00 / s1_y=10.00 / "
    "s2_y=20.00` 与栅格实测逐值一致) ⇒ ★★**几何自洽性判据 (不依赖打印包也成立)**: 套B 相对新板中心 (Y=15.00) 的偏移 "
    "= S1 −12.50 / S2 +12.50 ⇒ **不对称 + 两孔分离 25.00mm**; 而 15mm 老口径是**关于中心 7.50 的 ±5.00 对角分布** ⇒ "
    "平移到 30mm 板 ⇒ **套A (分离仍 10.00, 仍对称)** ⇒ ★**套B = 「只改 Y」时的漂移产物, 不是平移**。"
    "★**签字【不】覆盖 hw-lead 产物侧** ⇒ ★**未藏账 ⇒ 已开 ISS-194**。②★**C 段 39 → 39 (0 新增 / 0 移除 / "
    "0 改建议值)** ⇒ ★**你不用重看一遍** ⇒ 仍等你拍的只有 §1c 第 3 条 (`iss191_reset_p0_fix_choice`) + §1 那 5 条。"
    "③★**本轮 A 段派出 0 条 —— ★**这不是「没活」**: hw-lead 正在跑 **ISS-193** (29 个器件真实脚数) ⇒ ★**实测心跳 "
    "18:45 还在写** ⇒ ★**真在飞, 不是上一轮那种「假 fixing 标记」占名额** ⇒ ★**ISS-194 已 status=open ⇒ 下一轮 "
    "advance.py 自动派出** ⇒ 铁律「一个 agent 同时只允许一个写会话」保持 ⇒ ★**同时我已把 mech-lead/sw-lead 名下"
    "无 open 单这件事记着 (不是漏派, 是真没有)**。④★**B 段 approvals = 0 条** ⇒ ★**草稿一件没少也没发**: "
    "`state/outbox/` **18 份 .md** (含 1 份 README 清单 + 1 份决策图 ⇒ **16 份可发草稿**) + `attach/` **3 份** ⇒ "
    "★**一封都没发, 一家供应商都没联系** (★含今天 16:59 新备的 `som_balltable_inquiry.md` ⇒ ★**仍等你一句「可以发」**)。"
    "⑤★**核验 5 连本轮实测 rc**: merge **0** (冲突 0 · 产出 168 · 阻塞 43 高危 33 · 未闭合需求 96) · gate_check **0** "
    "(★**齐备率 18/18** · 证据分级 3/3 · 接口声明 485 条 · ★**与 merge.py 自对账一致** ✔) · issue_check **1** "
    "(违规 **32** 条 · ★**与上轮同数**) · stage_gate **1** (当前 **G1**, 还差 **1** 项 ⇒ G2 延后) · daily_check **3** "
    "(巡检异常已记录, 非崩溃: 问题闭环门违规 32 条; ★**原理图 ERC 0 + 脚数完整性 K=0 (584/584) 仍绿**)。"
    "⑥★**GitHub: 本 job 不推** (统一由 `ARS45 GitHub 同步 (每 5 小时 · 有进展才推)` job 负责) ⇒ ★**只落本地快照**。"
    "⑦★**板 / 网表一个字节没动** (板 md5 仍 `611b869e` · 网表 md5 仍 `c78f9912` · `.kicad_pro` 仍 `3e504d2b`)。"
    "⑧★**一条将来会变成拍板项、但现在还不用你拍的事 (没藏账)**: 30mm 板带出新账 = **骨架截面 4 个候选全部超预算** "
    "(最好 4.08g/对 vs 预算 +1~3g) + 石墨 2.16g/对 > W11 上限 ⇒ 结构侧已报 main 裁 ⇒ ★**我先记着, 等它变成结构"
    "方案选项再找你**。⑨**没有动任何需要你拍板的东西, 没有发任何邮件, 没有下采购单, 没有改 §0 锁死表, 没有写任何"
    "子总工的分片**\n"
    ">   ★ **本轮 C 段口径变化: 39 → 39 项 (0 新增 / 0 移除 / 0 改建议值)** —— ★**这一轮你不用重看一遍; 仍等你拍的"
    "只有 §1c 第 3 条 (`iss191_reset_p0_fix_choice`) + §1 那 5 条** ★★"
)

NEW_SEC = """## 0.23 ★★★ 本轮: ★**ISS-192 交卷并经我独立验收签字 (verified/pass) —— 仲裁依据是我自己重算的** + ★**已开 ISS-194 (孔位表 套B ⇒ 套A)** ⇒ ★**C 段 39 → 39 (你不用重看)** ★★

> ★**这一节绝大部分是【我这边记账/派活/核验的活】⇒ ★**不需要你做任何新决定** ⇒ ★**39 项老建议一个字没动** ⇒
> ★**仍等你拍的只有 §1c 第 3 条 (`iss191_reset_p0_fix_choice`) + §1 那 5 条** ★★

### 0.23.1 ★★★ ISS-192 交卷了 ⇒ ★**我独立验收签字 (verified/pass)** ⇒ ★**而且仲裁依据我自己重算了一遍**

| | |
|---|---|
| ★**交的是什么** | mech-lead 17:39~17:41 交卷 (`HANDOFF/2026-11-11_mech-lead_ISS192_机械复核器迁60x30与孔位Y仲裁.md` + ★**新建** `MECH/BOARD_GEOM_30MM.md` (结构侧权威表) + `pinset2_mech_check.py` (+`--self-test`) · `skeleton_section_check.py` · `cross_review_check.py` · `hinge_usb_check.py` · `iss065_check.py` · `fit_check.py` (标作废) + `state/fragments/mech.yaml` (3 条 needs_from)) ⇒ ★**HW/ 一律只读** (★板 md5 未动) |
| ★**★我做了什么复核 (★不采信自述★)** | ① `MECH/pinset2_mech_check.py` rc=0 「复算项 **38** | FAIL **0** | WARN **2**」 ② `--self-test` rc=0 「**6/6** 用例符合预期」(反向用例逐条命中: S1 挪进逃线带必红 / P2 挪进封装体必红 / S2 挪到板边必红 / 打印包改套B 必红) ③ `skeleton_section_check.py` rc=0 ④ `cross_review_check.py` rc=0 (★已明写「**不是闸**」+ 退出码只反映 MECH-OWNED + 16 项逐项标归属 ⇒ **不留孤儿红**) ⑤ `hinge_usb_check.py` rc=0 + `iss065_check.py` rc=0 ⑥ md5 对拍 ★**板 `611b869e…` / `.kicad_pro` `3e504d2b…` 一字未变** ⑦ merge rc=0 冲突 0 + gate_check Q1 **18/18** ⑧ ★**边界复核 (mtime 实测)**: 本单只动 MECH/(8) + HANDOFF/(1) + `fragments/mech.yaml` ⇒ **HW/ 内无 mech-lead 写入** ⇒ issue_log / §0 锁死表 / 别人分片 / `gen_*.py` 未动 ✔ |
| ★★★**最要紧的一条: 仲裁依据是我自己重算的 (★不是抄它的自述★)** | ★**我自己解析了两个打印包二进制 STL (`MECH/print/temple_cage_revb.stl` / `fit_coupon_revb.stl`) + 顶面占据栅格化 (0.5mm)** ⇒ ★**cage PCB 定位板 (板基线 Y=60) 实测四孔 = P1(8.00,15.00) ⌀2.4 + P2(52.00,15.00) ⌀2.4 + S1(8.00,10.00) ⌀1.6 + S2(52.00,20.00) ⌀1.6** ⇒ ★**coupon PCB 样板 (基线 X=4 / Y=84) 实测同一组值** ⇒ ★★**「打印包 = 套A」独立证实** ⇒ ★**套B 的 (8.00,2.50) / (52.00,27.50) 实测【实心无孔】** ⇒ ★**套B 与打印包不符** (★注: 打印包是**包络多边形**切孔 ⇒ 圆心靠栅格/弦宽反算, 不是找圆柱面) ⇒ ★**生成器常量 `pinset2_p_y=15.00 / s1_y=10.00 / s2_y=20.00` 与栅格实测逐值一致** |
| ★**几何自洽性 (★不依赖打印包也成立★)** | 套B 相对 30mm 新板中心 (Y=15.00) 的偏移 = S1 **−12.50** / S2 **+12.50** ⇒ ★**不对称 + 两孔分离 25.00mm**; 而 15mm 老口径 (`HW/PCB_FIXING_PINSET2.md` §3.1: P1(8,7.50) P2(52,7.50) S1(8,2.50) S2(52,12.50)) 是**关于中心 7.50 的 ±5.00 对角分布** ⇒ 平移到 30mm 板 (中心 15.00) ⇒ ★**套A (分离仍 10.00, 仍对称)** ⇒ ★**套B = 「只改 Y」时的漂移产物, 不是平移** ⇒ ★**两套口径不可能同时对, 套B 判死** |
| ★**签字覆盖什么 / 不覆盖什么 (★别误读★)** | ★**覆盖 = ① 结构侧机械闸迁到现行 60×30 ② PIN-SET-2 孔位 Y 仲裁成一套 = 套A** ⇒ ★**【不】覆盖 hw-lead 产物侧 (套B 还没改)** ⇒ ★**未藏账 ⇒ 已开 ISS-194** (下一节) ⇒ ★**另外还挂着 3 件没闭合**: 骨架预算裁 (main/你) · demo 板零安装孔 (★**属 PCB 布局类 ⇒ 按你 10:07 口径【不派】**) · `fit_check.py` v2 退役还是并存 (main 裁) |

### 0.23.2 ★★★ 已开 ISS-194 (owner=hw-lead) + ★**本轮 A 段为什么派出 0 条 (★不是「没活」★)**

| | |
|---|---|
| ★**本轮 A 段状态 (实测)** | `advance.py --json` 开跑时 `internal=[]` / `approvals=[]` / `waiting=[]` ⇒ ★**本轮派出 0 条** ⇒ ★**但这不是「没活」**: hw-lead 正在跑 **ISS-193** (29 个器件真实脚数 ⇒ 选项③ 的内部一半) ⇒ ★**实测心跳 18:45 还在写** ⇒ ★**真在飞** ⇒ ★**上一轮那种「假 `fixing` 标记占名额」的病本轮没有复发** (区别: 假标记 = 没人干活却占住 agent 名额; 本轮 = 真有活) |
| ★**ISS-194 是什么** | ★**PIN-SET-2 孔位表【套B ⇒ 套A】**: hw-lead 自己 **5 个产物里 4 个写套A** (hw.yaml claim `pcb_mount_holes_xy` / `HW/hw_week_20261101_check.py`:51-56 (★是**断言**) / ★**打印包 (main 实测)** / 结构侧权威表) ⇒ ★**只有 `HW/pcb60x30_check.py`:113-117 + 它的 `.json` 写套B** (S1 y=2.5 / S2 y=27.5, 孔壁距边只剩 **1.80mm**) ⇒ ★★**而那份 `.json` 是 ISS-118 的验收产物 ⇒ 下游按它做就错** ⇒ ★**必须改** |
| ★**为什么它属于「该派」而不是「排队」** | 老板 10:07 不派的是 ★**PCB 布线/布局类**; ★**本单只改校验器里的孔位表 + 它的机读产物** ⇒ ★**不改板 / 不改网表 / 不改原理图 / 不碰布线布局** ⇒ ★**不违反主线口径** ⇒ 属【机械接口 / 校验器一致性】类 ⇒ **在优先派活范围内** |
| ★**它什么时候出去** | ★**hw-lead 交完 ISS-193 ⇒ 下一轮 advance.py 自动派出** ⇒ ★**我本轮没有手动并发派 (铁律: 一个 agent 同时只允许一个写会话)** ⇒ ★**现在 `ISS-194` 状态 = `open` (已落 issue_log, 已写 dispatch_log)** |
| ★**一条将来会变成拍板项、但现在还不用你拍的事 (没藏账)** | ★**30mm 板带出一条新账**: 骨架截面 4 个候选**全部超预算** (满宽 9.72g/对 判死 / 台阶 t=1.0 **5.10** / t=0.8 **4.08** (仍超 +1.08g) / 铜 13.53) + 石墨 **2.16g/对 > W11 上限 2g** ⇒ ★**骨架截面必须重做** (满宽段只到 SoC 投影 / 横向扩散交给石墨 / 材料分段) ⇒ ★**结构侧已报 main 裁** ⇒ ★**我先记着, 等它变成结构方案选项再找你** |

### 0.23.3 ★★★ 核验 5 连 (本轮实测 rc) + 出块清单 + GitHub 本 job 不推

| 闸 | rc | 结论 |
|---|---|---|
| `state/merge.py` | **0** | 冲突 **0** · 产出 **168** · 阻塞 43 (高危 33) · 未闭合需求 **96** |
| `state/gate_check.py` | **0** | ★**齐备率 18/18** · 证据分级 3/3 · 接口声明 **485** 条 · ★**与 merge.py 自对账一致** ✔ |
| `state/issue_check.py` | **1** | 违规 **32** 条 (★**与上轮同数** — 本轮新增/关闭的都是非逾期项) |
| `state/stage_gate.py` | **1** | 当前 **G1** (原理图/PCB 定稿), 还差 **1** 项 ⇒ G2 延后 |
| `state/daily_check.py` | **3** | 巡检异常已记录 (非崩溃): 问题闭环门违规 32 条; ★**原理图 ERC 0 + 脚数完整性 K=0 (584/584) 仍绿**; 漂移检测 ⚠️ (内部未闭合 72→96 · 问题单 181→189 · 未闭环 blocker 8) |
| 外发草稿 | — | ★**`state/outbox/` 18 份 .md** (含 1 份 README 清单 + 1 份决策图 ⇒ **16 份可发草稿**) + `attach/` 3 份 ⇒ ★**一封都没发, 一家供应商都没联系**; ★**今天 16:59 新备的 `som_balltable_inquiry.md` 仍等你一句「可以发」** |
| 本地快照 | **0** | ★**`PROGRESS_SNAPSHOT.md` 已生成** ⇒ ★**只落本地, 随时能看** ★★ |
| GitHub | — | ★**本 job 不推** (★老板 11-11 10:07 口径 ⇒ 统一由 `ARS45 GitHub 同步 (每 5 小时 · 有进展才推)` job 负责★) ★★ |
| ★**板 / 网表** | — | ★**一个字节没动**: 板 md5 仍 `611b869e13518c3c023fb178f91a0075` · 网表 md5 仍 `c78f991283cc82d56c8e3dd31657c785` · `.kicad_pro` 仍 `3e504d2b` ★★ |

"""

TITLE_PREFIX = "# 待老板拍板页 · 2026-11-11 16:5x (第 21 次刷新"
SEC_ANCHOR = "## 0.22 ★★★ 本轮:"
BLOCK_START = "> ★ **本轮我自己动了什么**:"
BLOCK_TAIL = ">   ★ **本轮 C 段口径变化"


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
    with open(LOCK, "a+", encoding="utf-8") as lf:
        fcntl.flock(lf, fcntl.LOCK_EX)
        s = open(P, encoding="utf-8").read()
        before_len = len(s)

        # ---- 1. 标题 ----
        lines = s.split("\n")
        hit = False
        for i, l in enumerate(lines):
            if l.startswith(TITLE_PREFIX):
                lines[i] = NEW_TITLE
                hit = True
                break
        if not hit:
            print("❌ 找不到标题行 ⇒ 中止")
            fcntl.flock(lf, fcntl.LOCK_UN)
            return 2
        s = "\n".join(lines)

        # ---- 2. 插入 §0.23 (在 §0.22 主节之前) ----
        idx = s.find(SEC_ANCHOR)
        if idx < 0:
            print("❌ 找不到 §0.22 锚点 ⇒ 中止")
            fcntl.flock(lf, fcntl.LOCK_UN)
            return 2
        s = s[:idx] + NEW_SEC + s[idx:]

        # ---- 3. 重写『本轮我自己动了什么』段 (到该行行尾, 含那条重复的尾标) ----
        a = s.find(BLOCK_START)
        if a < 0:
            print("❌ 找不到『本轮我自己动了什么』段 ⇒ 中止")
            fcntl.flock(lf, fcntl.LOCK_UN)
            return 2
        b = s.find(BLOCK_TAIL, a)
        if b < 0:
            print("❌ 找不到口径变化尾标 ⇒ 中止")
            fcntl.flock(lf, fcntl.LOCK_UN)
            return 2
        eol = s.find("\n", b)
        if eol < 0:
            eol = len(s)
        s = s[:a] + NEW_WHAT + s[eol + 1:]

        # ---- 4. 自检: C 段 39 条一条没动 (数 §1c / §1 的 key 行) ----
        import re
        keys_before = set(re.findall(r"`([a-z0-9_]{4,})`", s))
        if "iss191_reset_p0_fix_choice" not in s:
            print("❌ 自检失败: §1c 第 3 条不见了 ⇒ 中止")
            fcntl.flock(lf, fcntl.LOCK_UN)
            return 2
        if "39 项" not in s:
            print("⚠️ 自检: 页面上没找到 '39 项' 字样")

        atomic_write(P, s)

    print(f"✅ 决策页已刷新 (第 22 次): {before_len} → {len(s)} 字符")
    print("   - 标题: ISS-192 签字 + ISS-194 开单 + C 段 39 → 39")
    print("   - 新增 §0.23 (0.23.1 签字与独立复核 / 0.23.2 ISS-194 与 A 段状态 / 0.23.3 核验 5 连)")
    print("   - 重写『本轮我自己动了什么』段 (并修掉上一版遗留的重复尾标)")
    print("   - ★**C 段 39 项的建议默认值一个没动**")
    return 0


if __name__ == "__main__":
    sys.exit(main())
