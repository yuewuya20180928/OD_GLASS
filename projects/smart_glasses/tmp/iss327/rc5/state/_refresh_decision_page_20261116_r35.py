#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
决策页 2026-11-16 第 3 次刷新 (第 35 号) —— C 段 38 → 38 (0 新增 / 0 退休 / 0 改建议值)
================================================================================
★**为什么必须再刷一次 (★铁律: 页与工具不许打架★)**:
  r34 页 (01:5x) 记的是 01:40 的实数 (问题单 214 / 违规 35) ⇒ ★**兄弟 job「队列自动派活」
  (fb67af40) 在 01:4x~01:5x 并发改了台账** ⇒ ★**ISS-217 清僵尸 + 重派 · ISS-218 已被本 job
  落 verified ⇒ 它顺势新开并派出 ISS-219 · ISS-215 的子会话 01:49:50 断且 0 交付 ⇒ 问题单 214→215,
  违规 35→36** ⇒ ★**老板看的必须是 01:44 的实数, 不许看 01:40 的** ⇒ ★**本脚本只订正【实数栏】,
  一条建议默认值都不动** ★

★**本脚本只做 4 件事 (★全是【记账】, 不替老板决定任何事★)**:
  ① 标题 + 抬头 ①~⑧ 换成 2026-11-16 01:44 这一轮的真实账
  ② §1~§8 每张表的「逾期」列按 `advance.py --json` 的 days_left 逐行重算 (★建议默认值列一个字不动★)
  ③ §8「最近到期」+ 附逾期分布表 + 按来源分 = 今日实数
  ④ 追加 §0.35 (本轮我动了什么 + 核验 5 连实数 + ISS-218 独立复核实数 + 三个名额实况)

★**落盘纪律**: 原子写 (tmp → fsync → os.replace → fsync(dir)) · **不改 11-15 那页 (原件留着)**
★**边界**: 不改任何一条的建议默认值 · 不发邮件 · 不改 §0 锁死表 · 不写任何子总工的分片
"""
import json
import os
import re
import subprocess
import tempfile

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(PROJ, "DECISION_PENDING_2026-11-15.md")
DST = os.path.join(PROJ, "DECISION_PENDING_2026-11-16.md")


def atomic_write(path: str, data: str) -> None:
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_dec_", suffix=".md")
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


def load_decisions():
    out = subprocess.run(
        ["python3", "state/advance.py", "--json"],
        cwd=PROJ, capture_output=True, text=True, check=False,
    ).stdout
    return json.loads(out)


def overdue_cell(days_left):
    if days_left is None:
        return "无 due"
    if days_left < 0:
        return "逾期 %d 天" % (-days_left)
    if days_left == 0:
        return "今天到期"
    return "剩 %d 天" % days_left


D = load_decisions()
DEC = {x["key"]: x for x in D["decisions"]}
assert len(DEC) == 38, "C 段数量与预期不符: %d" % len(DEC)
assert not D["internal"], "★A 段非空 ⇒ 本脚本这一轮的记账前提变了 ⇒ 停下来人工看"

with open(SRC, encoding="utf-8") as f:
    lines = f.read().split("\n")

# ---------- ① 标题 + 抬头 ----------
TITLE = (
    "# 待老板拍板页 · 2026-11-16 01:44 (第 3 次刷新 · ★**C 段 38 → 38 (0 新增 / 0 退休 / 0 改建议值)** + "
    "★**A 段本 job 派 0 条 (★三个总工名额: hw-lead ISS-217 已由兄弟 job 清僵尸并重派 · mech-lead ISS-219 已由兄弟 job 新开并派出 "
    "(★靠本 job 落 ISS-218 `verified` 放出的名额★) · sw-lead ISS-215 子会话 01:49:50 断且 0 交付 ⇒ 僵尸, 待兄弟 job 清★)** + "
    "★**B 段恒空 0 条** + ★**核验 5 连: merge 0 / gate 0 / issue 1 / stage 1 / daily 3**★)** ⇒ ★**38 条的建议默认值一个字没动** ★★)"
)

HEADER = [
    "> ★ **本轮我自己动了什么 (★只做记账, 不替你决定★)**:",
    "> ① ★**A 段派 0 条 —— 根因有两条, 不止一条★**:",
    ">   ★**(a) 三个总工名额各被一条 `fixing` 单占住 (★01:44 实测三张表, 每一张都查过子会话★)**: "
    "hw-lead **ISS-217** (★兄弟 job fb67af40 于 01:4x 实测首派子会话 `subagent:67ddec52` **aborted** 且**盘上交付物 0 件** ⇒ "
    "已把 status 回滚 open 并**重派**★) · mech-lead **ISS-219** (★兄弟 job 01:5x **新开并派出** —— ★**依据 = ISS-209 交卷里 3 条「只报不改」的 need "
    "(C-6 / C-7 / C-C+X-3) + ISS-218 交卷 need `iss218_mech_alu_k_201_vs_237`; ★**它能开这条, 正是因为本 job 把 ISS-218 落了 `verified` 把名额放出来**★) · "
    "sw-lead **ISS-215** (★子会话 `subagent:580cc849` **01:49:50 结束, 跑了 74 分钟, 盘上交付物 0 件** —— `SW/DEMO_OD_TIMING_SPEC.md` / "
    "`SW/DEMO_BOARD_60MS_VERDICT_PLAN.md` mtime 仍停在 11-15 22:28/22:35 ⇒ ★**僵尸 fixing** ⇒ ★**留给兄弟 job 清, 本 job 不动**★) ★",
    ">   ★**(b) 就算三个名额全放出来, 三个总工名下的 `open` 单也是 0 条** ⇒ ★**20 条 open 全是 owner=main (15) / owner=boss (5) ⇒ 总工侧队列已排空 ⇒ 瓶颈在 main 侧 + 你侧** ★",
    ">   ★**纪律**: 本 job 的规矩是「只处理 status 仍是 open 的, 已标 fixing 的不重复派」⇒ ★**ISS-215 / ISS-217 / ISS-219 我一条都不重派** ★ ⇒ "
    "★**僵尸清理由兄弟 job「ARS45 队列自动派活」(fb67af40) 负责** ⇒ ★**铁律「一个 agent 同时只允许一个写会话」⇒ 两个 job 同时派同一个 agent = 撞 R18 (分片合并丢 12%~38%)** ★",
    "> ② ★**按原理图主线口径 (老板 11-11 10:07), 本轮跳过 PCB 布线/布局类 = 0 条派出** (★三个总工的队列里本来就没有 PCB 类单★) ⇒ "
    "★**而 owner=main/boss 的板级 open 单继续压着不派: ISS-160 (demo 板图纸链/DRC 门禁 · blocker) · ISS-169 (demo 板可制造性) · ISS-126 (板厚档位) · "
    "ISS-128 (板面积账 + 逃线层数) · ISS-155 (rknn target · blocker) · ISS-156 (主板三件前置选型)** + ★**ISS-181 (PCB 布线主线 · deferred)** ⇒ "
    "★**没藏账 (★仍列在 G4 未闭环清单 · `stage_gate` rc=1 / G1 仍开 ⇒ 不许投板没松★)** ★",
    "> ③ ★**B 段 approvals = 0 条** (★老板 2026-11-11 19:31「一律不发」+ 2026-11-12 02:02「不再发信, 全靠自己查资料」后恒为空★) ⇒ "
    "★**`state/outbox/` 实测 19 份 .md + `attach/` 3 个附件, 一份没少, 一封都没发** ★",
    "> ④ ★**C 段 38 项 ⇒ 与 11-15 22:4x 那一页逐项核对: 38/38 key 对齐 (★**0 新增 / 0 退休 / 0 改建议默认值**★)** ⇒ "
    "★**38 条的建议默认值逐字沿用 11-15 原文; 本轮只订正了每张表的「逾期」列 (= 今日实数 · 口径统一成「逾期 N 天 / 今天到期 / 剩 N 天 / 无 due」) 与页尾逾期分布表 + 抬头实数** ★",
    "> ⑤ ★**核验 5 连本轮实测 rc (01:44, 兄弟 job 并发改完台账之后跑的)**: merge **0** (★产出 **244** · 阻塞 43 (高危 33) · 未闭合需求 **150** · 冲突 **0** · 健康度 red★) · "
    "gate_check **0** (★**Q1 18/18** ★ + Q2 证据分级 3/3 + Q3 接口声明 **537** + Q6 硬件真源闸 ✅ · ★Q5 硬指标覆盖 **1/3** (hw-lead 2/5 · sw-lead 3/5 · mech-lead 2/5) ⇒ 比 00:5x 的 2/3 退了一格, 已登记待查★) · "
    "issue_check **1** (★违规 **36** 条 = 25 条逾期 + **11** 条 C5 `source_blocker` 幻觉引用★) · "
    "stage_gate **1** (★当前 **G1**, 还差 **1** 项 ⇒ ★**PCB 布线未达标: unconnected=45 (需 0) · DRC 违规=0 (需 0) (ISS-181)**★) · "
    "daily_check **3** (★巡检异常已记录, 非崩溃: 问题闭环门 **215** 条 · 逾期 25 · 内部 186 / 外部 29 · 漂移「内部未闭合 127 → 150 / 问题单 209 → 215」= 本轮前后新开 ISS-211~219 的必然结果★) ★",
    "> ⑤b ★**本轮新发现 (登记, 不改门禁)**: issue_check 那 11 条「幻觉引用」★**实测是口径错、不是幻觉** ★ —— "
    "`state/issue_check.py:154` 只认 STATE.yaml **`blockers` 段**的 blocker id, 而项目一直拿 **issue id** 填 `source_blocker` ⇒ "
    "★**ISS-213 / ISS-214 / ISS-155 / ISS-190 实测都真实存在于 STATE.yaml** ⇒ ⇒ ★**真修法两条 (① 改检查口径让它也认 issue id · ② 改台账字段让它填 blocker id), "
    "本 job 一条都不动** (★判据不许放松 + 改门禁脚本要单独开单带自测★) ⇒ ★**已登记成待派专项, 不藏账** ★",
    "> ⑥ ★**原理图侧尺子 (顺带复跑, 全绿)**: ERC **0 条** (实测 2026-11-15T21:16:29+08:00) · 脚数完整性 **K=0** (图上 584 脚 = 表里 584 脚 · 218 器件/153 网) ★",
    "> ⑦ ★**GitHub: 本 job 不推** (★统一由 `ARS45 GitHub 同步 (每 5 小时 · 有进展才推)` job 负责★) ⇒ ★**本 job 只落本地快照** (`PROGRESS_SNAPSHOT.md` 已重生成, 2738 B @01:42) ★",
    "> ⑧ ★**没有动任何需要你拍板的东西, 没有发任何邮件, 没有联系任何供应商, 没有下采购单, 没有改 §0 锁死表, 没有写任何子总工的分片** ★★",
    ">  ★ **本轮 C 段口径变化: 38 → 38 项 (0 新增 / 0 退休 / 0 改建议值)** —— ★**你不用重看 38 条的正文; 变的只是每张表的「逾期」列 (今日实数) 与抬头/页尾的实数栏** ★★",
    ">  ★ **仍等你拍的当期要紧项 = 4 条** (★§1 那 3 条 + §1b 那 1 条 (板子基线 p41) ★ · §2 外发类已因「不再发信」政策归零★) ⇒ ★**其余 34 条当期都不卡 demo 板 → G1 → 可下单** ★",
]

start_i = next(i for i, l in enumerate(lines) if l.startswith("> ★ **本轮我自己动了什么"))
end_i = next(i for i, l in enumerate(lines) if l.startswith(">  ★ **本轮 C 段口径变化"))
new_lines = lines[:start_i] + HEADER + lines[end_i + 1:]
new_lines[0] = TITLE

# ---------- ② §1~§8 区间内的「逾期」列重算 ----------
tbl_start = next(i for i, l in enumerate(new_lines) if l.startswith("## 1. "))
tbl_end = next(i for i, l in enumerate(new_lines) if l.startswith("★ **按来源分"))


def _norm(c: str) -> str:
    s = c.strip()
    s = s.strip("★").strip()
    s = s.strip("*").strip()
    return s


RE_OD = re.compile(r"^(逾期\s*)?(剩\s*)?\d+\s*天$")
RE_NONE = re.compile(r"^无 due$")
KEY_RE = re.compile(r"`([a-z0-9_]+)`")

changed_rows = 0
for i in range(tbl_start, tbl_end):
    l = new_lines[i]
    if not l.startswith("|"):
        continue
    cells = l.split("|")
    if len(cells) < 5:
        continue
    key = None
    for c in cells[1:5]:
        m = KEY_RE.search(c)
        if m and m.group(1) in DEC:
            key = m.group(1)
            break
    if not key:
        continue
    for j, c in enumerate(cells):
        if RE_OD.match(_norm(c)) or RE_NONE.match(_norm(c)):
            cells[j] = " " + overdue_cell(DEC[key]["days_left"]) + " "
            changed_rows += 1
            break
    new_lines[i] = "|".join(cells)

# ---------- ③ §8「最近到期」+ 附分布表 + 按来源分 ----------
overdue = sorted(
    [(k, -v["days_left"]) for k, v in DEC.items() if v["days_left"] is not None and v["days_left"] < 0],
    key=lambda x: -x[1],
)
future = sorted(
    [(k, v["days_left"]) for k, v in DEC.items() if v["days_left"] is not None and v["days_left"] >= 0],
    key=lambda x: x[1],
)
no_due = [k for k, v in DEC.items() if v["days_left"] is None]
src_cnt = {}
for v in DEC.values():
    s = v.get("_from", "?").replace(".yaml", "")
    src_cnt[s] = src_cnt.get(s, 0) + 1

near = []
for k, dl in future[:3]:
    near.append("`%s` (%s)" % (k, overdue_cell(dl)))
for k, dl in overdue[:3]:
    near.append("`%s` (逾期 %d 天)" % (k, dl))
near_txt = " · ".join(near) if near else "★无★"

new_lines = [
    re.sub(r"^> ★\*\*最近到期 \(.*?\)\*\*: .*$",
           "> ★**最近到期 (2026-11-16 实数)**: %s —— 都只是「按我的假设推进」一句话, 不回也不卡当期。" % near_txt,
           l)
    for l in new_lines
]

dist_start = next(i for i, l in enumerate(new_lines) if l.startswith("### 附: 逾期分布"))
dist_end = next(i for i, l in enumerate(new_lines) if l.startswith("★ **按来源分"))
top5 = " · ".join("`%s` (%d 天)" % (k, d) for k, d in overdue[:5])
buckets = {}
for k, dl in future:
    buckets[dl] = buckets.get(dl, 0) + 1
bucket_rows = []
for dl in sorted(buckets):
    keys = [k for k, v in DEC.items() if v["days_left"] == dl]
    bucket_rows.append("| 剩 %d 天 | %d | %s |" % (dl, buckets[dl], " · ".join("`%s`" % k for k in keys)))
dist_block = [
    "### 附: 逾期分布 (38 项 · 2026-11-16 01:44 实数)",
    "",
    "| 逾期天数 | 项数 | 备注 |",
    "|---|---|---|",
    "| 已逾期 | **%d** | 最长: %s |" % (len(overdue), top5),
] + bucket_rows + [
    "| 无 due | **%d** | %s |" % (len(no_due), " · ".join("`%s`" % k for k in no_due)),
    "",
    "★ **按来源分 (38 项)**: ★**mech %d** · sw %d · hw %d · pm %d (★**0 新增 / 0 退休 / 0 改建议默认值**★)。"
    % (src_cnt.get("mech", 0), src_cnt.get("sw", 0), src_cnt.get("hw", 0), src_cnt.get("pm", 0)),
]
new_lines = new_lines[:dist_start] + dist_block + new_lines[dist_end + 1:]

# ---------- ④ 追加 §0.35 ----------
sec = """
## 0.35 ★★★ 本轮 (2026-11-16 01:39 ~ 01:44): ★**A 段派 0 条 (三个名额实况 + 总工队列已排空) + ISS-218 经 main 独立复核落 `verified` (★直接换来 ISS-219 的派出★) + B 段恒空 + C 段 38 → 38 (0 新增 / 0 退休 / 0 改建议默认值)** ★★★

> ★**这一节全部是【我这边记账 / 核验 / 独立复核】的活 ⇒ ★**不需要你做任何新决定** ⇒ ★**C 段 38 项的建议默认值一个没动** ★

### 0.35.1 ★★★ A 段: 本轮 0 条 —— ★**三个总工名额的实况表 (★每个都实测过子会话, 不是推测★)** ★★★

| 总工 | 名额上的单 | 子会话实测 | 本 job 处置 |
|---|---|---|---|
| hw-lead | ISS-217 (12 组网表/规格矛盾 ⇒ 原理图侧落表作业包 v1) | `subagent:67ddec52` **aborted** · 盘上 **0 件交付** (`HW/SCHEMATIC_LANDING_WORKPACKET_V1.md` 不存在) | ★**不重复派** ⇒ ★**兄弟 job 01:4x 已回滚 open 并重派** ★ |
| sw-lead | ISS-215 (demo 60ms 判据链显示侧重锚) | `subagent:580cc849` 00:35:53 起 · **01:49:50 结束 · 74 分钟 · 盘上 0 件交付** (SW 两个目标文件 mtime 仍是 11-15 22:28/22:35) ⇒ ★**僵尸 fixing** | ★**不重复派** ⇒ ★**留给兄弟 job 清僵尸 + 重派** ★ |
| mech-lead | ISS-219 (镜框正中区第 2 轮重排 · 兄弟 job 01:5x 新开并派出) | ★**派出前, mech-lead 名额是本 job 把 ISS-218 落 `verified` 放出来的** ★ | ★**不重复派** (★已在飞★) ★ |

★**关键**: ★**就算三个名额全放出来, 三个总工名下的 `open` 单也是 0 条** ⇒ ★**20 条 open 全是 owner=main (15) / owner=boss (5)** ⇒
★**总工侧队列已排空 ⇒ 真正的瓶颈在 main 侧 (我自己 15 条) + 你侧 (5 条)** ⇒ ★**这不是「派少了」, 是「能派的都派完了」** ★

### 0.35.2 ★★★ 本轮 main 对 ISS-218 的独立复核 (★只看盘上实物 + 自己跑门禁 + 自己 md5, 不采信子 agent 自报★) ★★★

| 复核项 | 实跑结果 |
|---|---|
| `python3 MECH/print/verify_pack_revb.py` | **rc=0** · 尺寸判据 100% 一致 + STL 与规格逐点互验 100% 一致 |
| `python3 MECH/print/verify_pack_revb.py --selftest` | **rc=0** · ★**反向用例 8/8 抓到** ⇒ 门禁不是假绿 ★ |
| `python3 MECH/print/verify_pack.py` (Rev A 基线) | **rc=0** · 46/46 · 未变红 |
| `python3 MECH/verify_budget.py` | **rc=0** · 充电耗散 = buck 口径 (没被改回线性 0.8W) |
| `python3 MECH/check_demo_struct_truth.py` | **rc=0** · 20/20 |
| md5 逐字节未变 | 网表 `c78f991283cc82d56c8e3dd31657c785` · 板 `611b869e13518c3c023fb178f91a0075` · `.kicad_pro` `3e504d2be83152e337949723e909be1b` |
| HANDOFF 结构 | B1~B6 六块齐全 (grep 实测 6 个二级标题) |

★**三条硬结论 (main 已复核)**: ① 第三档两档最坏单边 **0.63 / 0.62 ≥ 判据 0.60** (机器钉住) · ② ★**「热路是铝的」不自动满足 R ≤ 70 K/W** ⇒ 反解 **A ≥ 4.98 mm²** (2.0×2.0 铝条 R=87.1 ❌) · ③ 项目内 k=237 比 6063-T6 官方 201 乐观 18% ⇒ 方向不变, 只报不改 ★
★**实物 [实测] = 0 条** (本机跨网段不可达 / 无切片器 / 无量具) ⇒ M-PRINT 仍是 0 数据 ⇒ ★**第三档只是【可下片试样 + 机器门禁】, 不是实测结论** ★
★**本单的直接收益**: ★**mech-lead 名额空出来 ⇒ 兄弟 job 才能开出 ISS-219 (镜框正中区第 2 轮重排 · C-6 分光件 / C-7 面板 468mW vs 腔体 / C-C+X-3 + k=237→201 口径统一) ⇒ 本 job 的独立复核直接换来了下一条结构侧主线** ★

### 0.35.3 ★★★ B 段 / C 段 / 核验 5 连 / GitHub / 快照 ★★★

| 项 | 实测 (01:44) |
|---|---|
| ★**B 段 approvals** | ★**0 条** (★19:31「一律不发」+ 11-12 02:02「不再发信, 全靠自己查资料」⇒ 恒为空★) ⇒ ★**`state/outbox/` 19 份 .md + `attach/` 3 个附件, 一份没少, 一封都没发** ★ |
| ★**C 段** | ★**38 → 38 (0 新增 / 0 退休 / 0 改建议默认值) ⇒ 与 11-15 22:4x 页 38/38 key 对齐** ★ ⇒ ★**本轮只订正「逾期」列 (今日实数) + 页尾分布表 + 抬头实数** ★ |
| `state/merge.py` | **0** · 产出 **244** · 阻塞 43 (高危 33) · 未闭合需求 **150** · 冲突 **0** · 健康度 red |
| `state/gate_check.py` | **0** · ★**Q1 18/18** ★ · Q2 3/3 · Q3 接口声明 **537** · Q6 硬件真源闸 ✅ · ★Q5 硬指标覆盖 **1/3** (hw 2/5 · sw 3/5 · mech 2/5) ⇒ 比 00:5x 的 2/3 退一格, 已登记待查★ |
| `state/issue_check.py` | **1** · 违规 **36** 条 (★25 条逾期 + **11** 条 C5 `source_blocker` 幻觉引用★ ⇒ ★**实测是口径错不是幻觉, 见抬头 ⑤b★) |
| `state/stage_gate.py` | **1** · 当前 **G1** (原理图 / PCB 定稿), 还差 **1** 项 ⇒ ★**PCB 布线未达标: unconnected=45 (需 0) · DRC 违规=0 (需 0) (ISS-181)** ★ |
| `state/daily_check.py` | **3** (★巡检异常已记录, 非崩溃★) · 问题闭环门 **215** 条 · 逾期 **25** · 内部 186 / 外部 29 · 漂移「内部未闭合 127→150 / 问题单 209→215」= 本轮前后新开 ISS-211~219 的必然结果 |
| ★**原理图侧尺子** | ERC **0 条** · 脚数完整性 **K=0** (图上 584 脚 = 表里 584 脚 · 218 器件/153 网) |
| 本地快照 | ★**`PROGRESS_SNAPSHOT.md` 已生成 (2738 B, 01:42) ⇒ 只落本地** ★ |
| GitHub | ★**本 job 不推** (★统一由 5 小时同步 job 负责★) ★ |
| ★**板 / 网表 / 脚表 / .kicad_pro** | ★**本 job 一个字节没动** ★ |

### 0.35.4 ★★ 本轮仍未替你决定任何一条 ★★
"""
new_lines += sec.split("\n")

atomic_write(DST, "\n".join(new_lines))
print("✅ DECISION_PENDING_2026-11-16.md 已生成 (%d 行 · 逾期列重算 %d 行 · C 段 %d 项)"
      % (len(new_lines), changed_rows, len(DEC)))
print("   逾期 %d 项 / 未来 %d 项 / 无 due %d 项" % (len(overdue), len(future), len(no_due)))
print("   按来源: %s" % src_cnt)
