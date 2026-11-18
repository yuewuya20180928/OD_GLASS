#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
决策页 2026-11-16 第 7 次刷新 (第 38 号) —— C 段 38 → 38 (0 新增 / 0 退休 / 0 改建议值)
                   + 追加 §0.39 (★本 job 2026-11-16 04:19~04:2x 这轮★)
================================================================================
★**本脚本只做 2 件事 (★全是【记账】, 不替老板决定任何事★)**:
  ① 追加 §0.39: 本轮 A 段派 0 条的**真实原因** (★不是僵尸 fixing, 是【两个会话真的在跑】★)
     + 核验 5 连实数 + B 段恒空 + C 段机器核对 + 快照
  ② 抬头第 1 行实数栏刷新 (问题单 221 · 产出 270 · 未闭合 158 · 违规 26 · 逾期 25)

★**落盘纪律**: 原子写 (tmp → fsync → os.replace → fsync(dir)) · ★**只改 2026-11-16 那页, 不动 11-15 原件** ★
★**本脚本一个字节都不碰**: `state/issue_log.yaml` (★落账归落账的人, 避两写者冲突★) · 各总工分片 ·
  `PROJECT_TRACKER.md` §0 锁死表 · 板 / 网表 / 脚表 / `.kicad_pro` · `state/outbox/` ★
★**零外发** ★
"""
import os
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
DST = os.path.join(PROJ, "DECISION_PENDING_2026-11-16.md")


def atomic_write(path: str, data: str):
    d = os.path.dirname(path) or "."
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".dp_", suffix=".tmp")
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


NEW_HEADER = (
    "# 待老板拍板页 · 2026-11-16 04:2x (第 7 次刷新 · ★**C 段 38 → 38 (0 新增 / 0 退休 / 0 改建议值)** + "
    "★**A 段本 job 派 0 条 (★真实原因 = 【两个总工名额被【正在真跑的会话】占住】: hw-lead ISS-223 (会话 359d0e98 · "
    "running) + sw-lead ISS-225 (会话 b2423369 · running, 兄弟 job 04:07 派) · mech-lead 名额空但队列里 0 条 open "
    "⇒ 20 条 open 全是 owner=main 15 / owner=boss 5★)** + ★**B 段恒空 0 条** + "
    "★**核验 5 连: merge 0 / gate 0 / issue 1 / stage 1 / daily 3**★)** ⇒ ★**38 条的建议默认值一个字没动** ★★)"
)

SEC039 = r"""
---

## 0.39 ★★★ 本轮 (2026-11-16 04:19 ~ 04:2x): ★**A 段派 0 条 (★真实原因 = 会话真在跑, 不是僵尸★) + B 段恒空 + C 段 38 → 38 (0 新增/0 退休/0 改建议默认值) + 核验 5 连** ★★★

> ★**这一节全部是【我这边记账 / 核验】的活 ⇒ ★**不需要你做任何新决定** ⇒ ★**C 段 38 项的建议默认值一个没动** ⇒
> ★**仍等你拍的当期要紧项 = §1 那 3 条 + §1b 那 1 条 + §9 的 V-2 / V-4** ⇒ ★**其余当期都不卡 demo 板 → G1 → 可下单** ★

### 0.39.1 ★★★ A 段: ★**为什么这轮没派活 (★跟前面几轮的【僵尸 fixing】不是同一回事★)** ★★★

| agent | 本轮实况 (★main 实查 `sessions_list` + 台账 `status`★) | 本轮处置 |
|---|---|---|
| `hw-lead` | ★**ISS-223 = `fixing`, 会话真在跑** (★`subagent:359d0e98` status=**running** · 04:19 实查 runtime 1680s+★) ⇒ ★**铁律「一个 agent 同时只能有一个写会话」⇒ 不重派** ★ | ★**不派** ★ |
| `sw-lead` | ★**ISS-225 = `fixing`, 会话真在跑** (★`subagent:b2423369` status=**running** · 04:07 由兄弟 job「队列自动派活」派出★) ⇒ ★**不重派 (★也不撞车★)** ★ | ★**不派** ★ |
| `mech-lead` | ★**名额空** (★上一条 ISS-224 已交卷验收落 `verified` @03:5x★) ⇒ ★**但队列里 0 条 open 单** ★ | ★**无活可派** ★ |

★**机器核对 (★不是目测★)**: `state/issue_log.yaml` 全库 status 分布 = `closed 97 / verified 81 / open 20 / deferred 15 / fixed 6 / fixing 2` ⇒ ★**`fixing` 恰好 2 条 = 上面那两个正在跑的 (⇒ 【不是僵尸】, 是【真在干活】)★** ⇒ ★**20 条 `open` 实测 owner 全是 `main` (15) / `boss` (5) ⇒ 总工侧队列已排空 ⇒ 瓶颈在 main 侧 + 你侧** ★

★**⇒ 本轮 A 段 0 派 = 正确行为, 不是漏派** ★ (★纪律: 「已标 fixing 的不重复派」 + 「一个 agent 同时只能有一个写会话」★)

★**按原理图主线口径 (老板 2026-11-11 10:07) 本轮跳过 / 压着的 PCB 类** ★:
· ★**派出 0 条 PCB 类** (★三个总工的队列里本来就没有 PCB 布线/布局类单★)
· ★**owner=main/boss 的板级 open 单继续压着不派**: `ISS-160` (demo 板图纸链/DRC 门禁 · blocker) · `ISS-169` (demo 板可制造性) · `ISS-126` (板厚档位) · `ISS-128` (板面积账 + 逃线层数) · `ISS-155` (rknn target · blocker) · `ISS-156` (主板三件前置选型) + ★**`ISS-181` (PCB 布线主线 · `deferred`)**
· ★**没藏账** (★它们仍列在 G4 未闭环清单 · `stage_gate` rc=1 / G1 仍开 ⇒ **不许投板没松**★) ★

### 0.39.2 ★★★ B 段: 恒空 0 条 + 草稿一份没少 + 一封没发 ★★★

· ★**`advance.py --json` 的 `approvals` = 0 条** ⇒ ★**符合 2026-11-11 19:31「一律不发」+ 2026-11-12 02:02「不再发信, 全靠自己查资料」的新口径 ⇒ 本 job 【不发任何邮件 / 不联系任何供应商 / 不下采购单】★**
· ★**`state/outbox/` 实测 19 份 .md + `attach/` 3 个附件, 一份没少** ⇒ ★**今日 outbox 零改动 (`find -newermt "2026-11-16 00:00"` 实测为空)★**
· ★**⇒ 本轮 B 段 = 0 动作 (★外发段恒空 ⇒ 没有「补写草稿」这回事★)** ★

### 0.39.3 ★★★ C 段: ★**38 → 38 (0 新增 / 0 退休 / 0 改建议默认值) —— 机器逐 key 核对** ★★★

· ★**`advance.py --json` 的 `decisions` 实测 38 个 key** ⇒ ★**逐个在本页表格里查: 命中 38 / 缺失 0** ★
· ★**页内另有的 3 个 key (`sch_completeness_target` / `ref_designator_rename` / `iss191_reset_p0_fix_choice`) = §1c 已退休留档 (老板 2026-11-11 19:31 拍「全做」) ⇒ 本就不在 C 段 38 项里** ★
· ★**⇒ §1 ~ §9 的建议默认值原文一字未动** ★ ★

### 0.39.4 ★★★ 核验 5 连 (★本轮实测 rc★) + 原理图侧尺子 + GitHub + 快照 ★★★

| 项 | 实测 (2026-11-16 04:19~04:21) |
|---|---|
| `state/merge.py` | **0** · 产出 **270** · 阻塞 **43** (高危 33) · 未闭合需求 **158** · 冲突 **0** · 健康度 red |
| `state/gate_check.py` | **0** · ★**Q1 交付齐备率 18/18** ★ · Q2 证据分级 3/3 · Q3 接口声明 **559** · Q4 问方 **72/306** · 等外部 71 / 等总工 158 · ★**Q5 硬指标覆盖 1/3** (hw 2/5 · sw 1/5 · mech 4/5) ★ · ★**Q6 硬件真源闸 ✅** ★ |
| `state/issue_check.py` | **1** · 违规 **26** 条 (★25 条逾期 + **1** 条真幻觉引用 `source_blocker=MECH-JCHG-PINMAP-3SET`★) |
| `state/stage_gate.py` | **1** · 当前 **G1** (原理图 / PCB 定稿), 还差 **1** 项 ⇒ ★**PCB 布线未达标: unconnected=45 (需 0) · DRC 违规=0 (需 0)** (ISS-181) ★ |
| `state/daily_check.py` | **3** (★巡检异常已记录, 非崩溃★) · 问题闭环门 **221** 条 · 逾期 **25** · 内部 **192** / 外部 29 · 违规 26 · 漂移「内部未闭合 **127 → 158** / 问题单 **209 → 221**」· 未闭环 blocker **9** · ★**check_pcb_nets rc=1** (★板侧同步项 B-1 的已知中间态 ⇒ 板不许投, 不是新缺陷★) · ★**chain_gate 未过** (★投产包比原理图旧★) ★ |
| ★**原理图侧尺子** | ERC **0 条** (实测 2026-11-16T03:43:27+08:00) · 脚数完整性 **K=0** (图上 **584** 脚 = 表里 **584** 脚 · 218 器件 / 153 网) ★ |
| GitHub | ★**本 job 不推** (★老板 2026-11-11 09:5x 口径 ⇒ 统一由 `ARS45 GitHub 同步 (每 5 小时 · 有进展才推)` 负责★) ★ |
| 本地快照 | ★**`PROGRESS_SNAPSHOT.md` 已生成 (4560 B, 04:21) ⇒ 只落本地, 随时能看** ★ |
| ★**本 job 动过的文件** | ★**只有 2 个: 本决策页 + `PROGRESS_SNAPSHOT.md` (脚本自动生成)★** ⇒ ★**`issue_log.yaml` 一个字节没动 · 各总工分片一个字节没动 · 板/网表/脚表/`.kicad_pro` 一个字节没动 · `state/outbox/` 一个字节没动** ★ |

### 0.39.5 ★★ 本轮仍未替你决定任何一条 ★★

> ★**没有发任何邮件, 没有联系任何供应商, 没有下采购单, 没有改 §0 锁死表, 没有写任何子总工的分片, 没有动任何板/网表/脚表文件, 没有签任何 issue 的 verified** ★★
> ★**C 段 38 条的建议默认值一个字没动** ⇒ ★**仍等你拍: §1 那 3 条 + §1b 那 1 条 (板子基线 p41) + §9 的 `V-2` (ESD 选型) + `V-4` (R_ILIM 档位) ⇒ 其余当期都不卡 demo 板 → G1 → 可下单** ★★

---

> ★ **本轮 C 段口径变化: 38 → 38 项 (0 新增 / 0 退休 / 0 改建议值)** —— ★**你不用重看 38 条的正文; 变的只是抬头/页尾的实数栏** ★★
> ★ **仍等你拍的当期要紧项 = §1 那 3 条 + §1b 那 1 条 + §9 的 V-2 / V-4** ⇒ ★**其余当期都不卡 demo 板 → G1 → 可下单** ★
> ★ **下一步**: 等 ISS-223 (hw-lead · 落表第 2 批 + V-3 可判化) 与 ISS-225 (sw-lead · md5 台账化) 交卷 → main 独立验收 → 名额释放 ⇒ ★**总工侧队列已排空 ⇒ 下一轮要靠 main/boss 侧的 20 条 open 开新单, 否则 A 段又会空** ★
"""


def main():
    src = open(DST, encoding="utf-8").read()

    # ---- ① 抬头第 1 行刷新 ----
    lines = src.split("\n")
    if lines and lines[0].startswith("# 待老板拍板页 · 2026-11-16"):
        if lines[0] != NEW_HEADER:
            lines[0] = NEW_HEADER
            src = "\n".join(lines)
            atomic_write(DST, src)
            print("✅ 抬头实数栏已刷新")
        else:
            print("⚠ 抬头已是最新 ⇒ 幂等跳过")
    else:
        print("❌ 抬头没认出来 ⇒ 不写 (拒绝盲写)")
        return 2

    # ---- ② 追加 §0.39 ----
    src = open(DST, encoding="utf-8").read()
    if "## 0.39 ★★★" in src:
        print("⚠ §0.39 已在 ⇒ 幂等跳过")
    else:
        src = src.rstrip("\n") + "\n" + SEC039
        atomic_write(DST, src)
        print("✅ §0.39 已追加")

    print("页大小: %d B" % os.path.getsize(DST))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
