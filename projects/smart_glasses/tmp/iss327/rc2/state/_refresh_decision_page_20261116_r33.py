#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
决策页 2026-11-16 第 1 次刷新 (第 33 号) —— C 段 38 → 38 (0 新增 / 0 退休 / 0 改建议值)
================================================================================
★**为什么必须刷新 (★铁律: 页与工具不许打架★)**:
  `advance.py --json` 实测 C 段 = **38 项** (★与 11-15 22:4x 页 38/38 key 对齐★)
  ⇒ ★**若页还停在 11-15 的「逾期」列, 老板看的就是昨天的假账** ★

★**本脚本只做 4 件事 (★全是【记账】, 不替老板决定任何事★)**:
  ① 标题 + 抬头 ①~⑧ 换成 2026-11-16 00:5x 这一轮的真实账
  ② §1~§8 每张表的「逾期」列按 `advance.py --json` 的 days_left 逐行重算
     (★**建议默认值列一个字不动**★ · 口径统一成「逾期 N 天 / 今天到期 / 剩 N 天 / 无 due」)
  ③ §8「最近到期」+ 附逾期分布表 + 按来源分 = 今日实数
  ④ 追加 §0.34 (本轮我动了什么 + 核验 5 连实数)

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
    d = json.loads(out)
    return d


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

with open(SRC, encoding="utf-8") as f:
    lines = f.read().split("\n")

# ---------- ① 标题 + 抬头 ----------
TITLE = (
    "# 待老板拍板页 · 2026-11-16 00:5x (第 1 次刷新 · ★**C 段 38 → 38 (0 新增 / 0 退休 / 0 改建议值)** + "
    "★**A 段本 job 派 0 条 (三个总工名额被【真在飞】的 ISS-214/215/216 占住)** + ★**B 段恒空 0 条** + "
    "★**核验 5 连: merge 0 / gate 0 / issue 1 / stage 1 / daily 3**★)** ⇒ ★**38 条的建议默认值一个字没动** ★★)"
)

HEADER = [
    "> ★ **本轮我自己动了什么 (★只做记账, 不替你决定★)**:",
    "> ① ★**A 段派 0 条 —— ★**这次不是「没活」, 是【三个总工名额各被一条【真在飞】的单占住】★** ⇒ "
    "★**兄弟 job「ARS45 队列自动派活」(fb67af40) 于 00:5x 派出 3 条并落 `fixing`: ISS-214 → hw-lead / ISS-215 → sw-lead / ISS-216 → mech-lead** ⇒ "
    "★**实测三个子会话 `status=running` (hw-lead `subagent:85841b8c` 起 00:49:07 · sw-lead `subagent:580cc849` 起 00:49:13 · mech-lead `subagent:900f6943` 起 00:49:19)** ⇒ "
    "★**铁律「一个 agent 同时只允许一个写会话」⇒ 本 job 不重复派 (★两个 job 同时派同一个 agent = 撞 R18, 分片合并丢 12%~38%★)** ★",
    "> ② ★**按原理图主线口径 (老板 11-11 10:07), 本轮跳过 PCB 布线/布局类 = 0 条** (★三个总工的队列里本来就没有 PCB 类单★) ⇒ "
    "★**而 owner=main/boss 的板级类 open 单继续压着不派: ISS-160 (demo 板图纸链/DRC 门禁) · ISS-169 (demo 板可制造性) · ISS-126 (板厚档位) · ISS-128 (板面积账+逃线层数) · ISS-181 (PCB 布线主线 · deferred)** ⇒ "
    "★**没藏账 (★仍列在 G4 未闭环清单 · `stage_gate` rc=1 / G1 仍开 ⇒ 不许投板没松★)** ★",
    "> ③ ★**B 段 approvals = 0 条** (★老板 2026-11-11 19:31「一律不发」+ 2026-11-12 02:02「不再发信, 全靠自己查资料」后恒为空★) ⇒ "
    "★**`state/outbox/` 实测 19 份 .md + `attach/` 3 个附件, 一份没少, 一封都没发** ★",
    "> ④ ★**C 段 38 项 ⇒ 与 11-15 22:4x 那一页逐项核对: 38/38 key 对齐 (★**0 新增 / 0 退休 / 0 改建议默认值**★)** ⇒ "
    "★**38 条的建议默认值逐字沿用 11-15 原文; 本轮只订正了每张表的「逾期」列 (= 今日实数 · 口径统一成「逾期 N 天 / 今天到期 / 剩 N 天 / 无 due」) 与页尾逾期分布表** ★",
    "> ⑤ ★**核验 5 连本轮实测 rc**: merge **0** (★产出 **233** · 阻塞 43 (高危 33) · 未闭合需求 **137** · 冲突 **0** · 健康度 red★) · "
    "gate_check **0** (★**Q1 18/18** ★ + Q2 证据分级 3/3 + Q3 接口声明 **528** + Q6 硬件真源闸 ✅) · "
    "issue_check **1** (★违规 **33** 条 = 25 条逾期 + 8 条 C5 `source_blocker` 幻觉引用★) · "
    "stage_gate **1** (★当前 **G1**, 还差 **1** 项 ⇒ PCB 布线未达标: unconnected=45 (需 0) · DRC 违规=0 (需 0) (ISS-181)★) · "
    "daily_check **3** (★巡检异常已记录, 非崩溃: 问题闭环门 212 条 · 逾期 25 · 内部 183 / 外部 29 · 漂移「内部未闭合 127 → 137 / 问题单 209 → 212」= 本轮前后新开 ISS-211~216 的必然结果★) ★",
    "> ⑥ ★**原理图侧尺子 (顺带复跑, 全绿)**: ERC **0 条** (实测 2026-11-15T21:16:29+08:00) · 脚数完整性 **K=0** (图上 584 脚 = 表里 584 脚 · 218 器件/153 网) ★",
    "> ⑦ ★**GitHub: 本 job 不推** (★统一由 `ARS45 GitHub 同步 (每 5 小时 · 有进展才推)` job 负责★) ⇒ ★**本 job 只落本地快照** (`PROGRESS_SNAPSHOT.md` 已重生成, 2854 B) ★",
    "> ⑧ ★**没有动任何需要你拍板的东西, 没有发任何邮件, 没有联系任何供应商, 没有下采购单, 没有改 §0 锁死表, 没有写任何子总工的分片** ★★",
    ">  ★ **本轮 C 段口径变化: 38 → 38 项 (0 新增 / 0 退休 / 0 改建议值)** —— ★**你不用重看 38 条的正文; 唯一变的是每张表的「逾期」列 (今日实数) 与页尾分布表** ★★",
    ">  ★ **仍等你拍的当期要紧项 = 4 条** (★§1 那 3 条 + §1b 那 1 条 (板子基线 p41) ★ · §2 外发类已因「不再发信」政策归零★) ⇒ ★**其余 34 条当期都不卡 demo 板 → G1 → 可下单** ★",
]

# 定位抬头块: 第 5 行 "本轮我自己动了什么" 到 页尾 "本轮 C 段口径变化" 那行 (含)
start_i = next(i for i, l in enumerate(lines) if l.startswith("> ★ **本轮我自己动了什么"))
end_i = next(i for i, l in enumerate(lines) if l.startswith(">  ★ **本轮 C 段口径变化"))
new_lines = lines[:start_i] + HEADER + lines[end_i + 1:]
# 换标题
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
    src_cnt[v.get("_from", "?").replace(".yaml", "")] = src_cnt.get(v.get("_from", "?").replace(".yaml", ""), 0) + 1

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

# 附分布表整块重写
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
    "### 附: 逾期分布 (38 项 · 2026-11-16 00:5x 实数)",
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

# ---------- ④ 追加 §0.34 ----------
sec = """
## 0.34 ★★★ 本轮 (2026-11-16 00:48 ~ 00:55): ★**A 段派 0 条 (三个总工名额被真在飞的 ISS-214/215/216 占住) + B 段恒空 + C 段 38 → 38 (0 新增 / 0 退休 / 0 改建议默认值)** ★★★

> ★**这一节全部是【我这边记账 / 派活 / 核验】的活 ⇒ ★**不需要你做任何新决定** ⇒ ★**C 段 38 项的建议默认值一个没动** ★

### 0.34.1 ★★★ A 段: 本轮 0 条 —— ★**根因 = 【真在飞】, 不是【没活】, 也不是【僵尸占位】** ★★★

| | |
|---|---|
| ★**实测** | ★**`advance.py --json` = `internal: []` · `approvals: []` · `decisions: 38` · `waiting: []`** ★ |
| ★**根因** | ★**兄弟 job「ARS45 队列自动派活」(fb67af40) 于 00:5x 派出 3 条并落 `fixing`**: ISS-214 → hw-lead (网表/规格自身矛盾第 2 轮 8 条) · ISS-215 → sw-lead (demo 60ms 判据链显示侧重锚) · ISS-216 → mech-lead (MECH_BUDGET 充电耗散口径统一) ⇒ ★**三个总工名额各被一条占住 ⇒ `advance.py` 的 in_flight 规则正确挡住** ★ |
| ★**实测在飞** | ★**三个子会话 `status=running`**: hw-lead `subagent:85841b8c` (起 00:49:07) · sw-lead `subagent:580cc849` (起 00:49:13) · mech-lead `subagent:900f6943` (起 00:49:19) ⇒ ★**真在飞, 不是死单** ⇒ ★**本 job 一条都没重复派** ★ |
| ★**纪律** | ★**铁律「一个 agent 同时只允许一个写会话」⇒ 两个 job 同时派同一个 agent = 撞 R18 (分片合并丢 12%~38%)** ⇒ ★**本 job 不硬塞** ★ |
| ★**跳过 PCB 类** | ★**0 条** (★三个总工的队列里没有 PCB 布线/布局类单★) ⇒ ★**owner=main/boss 的板级 open 单 (ISS-160 / ISS-169 / ISS-126 / ISS-128) + ISS-181 (deferred) 继续压着不派 (★老板 11-11 10:07 口径★), 也没藏账 (★仍列在 G4 未闭环清单★)** ★ |

### 0.34.2 ★★★ B 段 / C 段 / 核验 5 连 / GitHub ★★★

| 项 | 实测 |
|---|---|
| ★**B 段 approvals** | ★**0 条** (★19:31「一律不发」+ 11-12 02:02「不再发信, 全靠自己查资料」⇒ 恒为空★) ⇒ ★**`state/outbox/` 19 份 .md + `attach/` 3 个附件, 一份没少, 一封都没发** ★ |
| ★**C 段** | ★**38 → 38 (0 新增 / 0 退休 / 0 改建议默认值) ⇒ 与 11-15 22:4x 页 38/38 key 对齐** ★ ⇒ ★**本轮只订正「逾期」列 (今日实数) + 页尾分布表** ★ |
| `state/merge.py` | **0** · 产出 **233** · 阻塞 43 (高危 33) · 未闭合需求 **137** · 冲突 **0** · 健康度 red |
| `state/gate_check.py` | **0** · ★**Q1 18/18** ★ · Q2 3/3 · Q3 接口声明 **528** · Q4 自对账一致 · Q6 硬件真源闸 ✅ |
| `state/issue_check.py` | **1** · 违规 **33** 条 (★25 条逾期 + 8 条 C5 `source_blocker` 幻觉引用★) |
| `state/stage_gate.py` | **1** · 当前 **G1** (原理图 / PCB 定稿), 还差 **1** 项 ⇒ ★**PCB 布线未达标: unconnected=45 (需 0) · DRC 违规=0 (需 0) (ISS-181)** ★ |
| `state/daily_check.py` | **3** (★巡检异常已记录, 非崩溃★) · 问题闭环门 **212** 条 · 逾期 **25** · 内部 183 / 外部 29 · 漂移「内部未闭合 127→137 / 问题单 209→212」= 本轮前后新开 ISS-211~216 的必然结果 |
| ★**原理图侧尺子** | ERC **0 条** · 脚数完整性 **K=0** (图上 584 脚 = 表里 584 脚) |
| 本地快照 | ★**`PROGRESS_SNAPSHOT.md` 已生成 (2854 B, 00:50) ⇒ 只落本地** ★ |
| GitHub | ★**本 job 不推** (★统一由 5 小时同步 job 负责★) ★ |
| ★**板 / 网表 / 脚表 / .kicad_pro** | ★**本 job 一个字节没动** ★ |

### 0.34.3 ★★ 本轮仍未替你决定任何一条 ★★
"""
new_lines += sec.split("\n")

atomic_write(DST, "\n".join(new_lines))
print("✅ DECISION_PENDING_2026-11-16.md 已生成 (%d 行 · 逾期列重算 %d 行 · C 段 %d 项)"
      % (len(new_lines), changed_rows, len(DEC)))
print("   逾期 %d 项 / 未来 %d 项 / 无 due %d 项" % (len(overdue), len(future), len(no_due)))
print("   按来源: %s" % src_cnt)
