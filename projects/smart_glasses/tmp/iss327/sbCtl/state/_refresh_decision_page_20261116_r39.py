#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
决策页 2026-11-16 第 9 次刷新 (第 39 号) —— C 段 38 → 38 (0 新增 / 0 退休 / 0 改建议值)
                   + 追加 §0.41 (★cron 775d9893「继续执行后继计划」2026-11-16 05:16 ~ 05:2x 这轮★)
================================================================================
★**本脚本只做 2 件事 (★全是【记账】, 不替老板决定任何事★)**:
  ① 追加 §0.41: 本轮 A 段派 1 条 (ISS-228 → sw-lead) 的**真实原因**
     (★上一轮 internal=0 = 【sw-lead 名额被一条【已交卷但会话被平台中止】的僵尸 fixing 占住】★)
     + 清僵尸落账 1 条 (ISS-226 → verified) + 核验 5 连实数 + B 段恒空 + C 段机器核对 + 快照
  ② 抬头第 1 行实数栏刷新 (问题单 224 · 产出 282 · 未闭合 159 · 违规 26 · 逾期 25)

★**落盘纪律**: 原子写 (tmp → fsync → os.replace → fsync(dir)) · ★**只改 2026-11-16 那页, 不动 11-15 原件** ★
★**本脚本一个字节都不碰**: `state/issue_log.yaml` · 各总工分片 · `PROJECT_TRACKER.md` §0 锁死表 ·
  板 / 网表 / 脚表 / `.kicad_pro` · `state/outbox/` ★
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
    "# 待老板拍板页 · 2026-11-16 05:2x (第 9 次刷新 · ★**C 段 38 → 38 (0 新增 / 0 退休 / 0 改建议值)** + "
    "★**A 段本 job 派 1 条 (ISS-228 → sw-lead · RK3572 GPIO0→VCCIO 官方映射自查 · ★真实原因 = 上一轮 internal=0 是"
    "【sw-lead 名额被一条【已交卷但交卷正文被平台中止】的僵尸 fixing 占住】: ISS-226 会话 timeout@05:16:32 ⇒ "
    "但成果 4/4 全绿 ⇒ main 独立验收落 verified ⇒ 名额放出 ⇒ 新开 ISS-228 派出★0 条 PCB 类★)** + "
    "★**B 段恒空 0 条** + ★**核验 5 连: merge 0 / gate 0 / issue 1 / stage 1 / daily 3**★)** ⇒ "
    "★**38 条的建议默认值一个字没动** ★★)"
)

SEC041 = r"""
---

## 0.41 ★★★ 本轮 (2026-11-16 05:16 ~ 05:2x): ★**清 1 条僵尸 fixing (ISS-226 → `verified`) + A 段派 1 条 (ISS-228 → sw-lead · ★0 条 PCB 类★) + B 段恒空 + C 段 38 → 38 (0 新增/0 退休/0 改建议默认值) + 核验 5 连** ★★★

> ★**这一节全部是【我这边记账 / 派活 / 核验】的活 ⇒ ★**不需要你做任何新决定** ⇒ ★**C 段 38 项的建议默认值一个没动** ★
> ★**仍等你拍的当期要紧项 = §1 那 3 条 + §1b 那 1 条 + §9 的 V-2 / V-4** ⇒ ★**其余当期都不卡 demo 板 → G1 → 可下单** ★

### 0.41.1 ★★★ A 段: ★**派 1 条 (★上一轮 internal=0 的真实原因 = 【1 条僵尸 fixing 占着 1 个名额】★)** ★★★

| agent | issue | 本轮依据 (★main 05:1x~05:2x 实查★) | 会话 |
|---|---|---|---|
| `sw-lead` | ★**ISS-228 (新开)** ★ | ★**`state/fragments/hw.yaml` 里本来就挂着一条没人接的跨域 need**: `iss148_rk3572_gpio0_vccio_domain_check` (to=sw-lead, since 2026-11-02, due 2026-11-03 ⇒ ★**已逾期 13 天**★) ⇒ ★**它卡的是原理图主线**: I2C0_SCL = ★**GPIO0_B0 (球 1K21)**★ / I2C0_SDA = ★**GPIO0_B1 (球 U32)**★ ⇒ 这两根脚挂哪个 VCCIO 组 ⇒ ★**I2C_A 上拉最终是 1.8V / 2.8V / 3.3V**★ ⇒ 决定 ★**ISS-211 缺陷① + d1 组怎么落表**★ ⇒ ★**落表定稿前不核, d1 只能悬着** ★ ⇒ 落点: 官方口径自查 (datasheet p.39 渲染图已定「VCCIO1~6 可上 3.3V (max 3.63V)」, ★**但 datasheet 没有 GPIO bank → VCCIO 组对应表 ⇒ GPIO0_B0/B1 归属仍是 [0数据]**★) + 给 hw-lead 的可落表判据串 + 机器门禁 + 反向用例 | `subagent:4930b32a` (★05:26 派出, running★) |
| `hw-lead` | ★**ISS-223 (在飞, 不重派)** ★ | ★**会话 `subagent:684f3e4b` status=**running** (05:13 兄弟 job 派出, 05:19 transcript 仍在写盘)** ★ ⇒ ★**铁律「一个 agent 同时只能有一个写会话」⇒ 不重派、不撞车** ★ | `subagent:684f3e4b` |
| `mech-lead` | ★**ISS-227 (在飞, 不重派)** ★ | ★**会话 `subagent:5997cb10` status=**running** (05:13 兄弟 job 派出, 05:19 transcript 仍在写盘)** ★ ⇒ ★**不重派** ★ | `subagent:5997cb10` |

★**机器核对 (★不是目测★)**: `state/issue_log.yaml` 全库 status = `closed 97 / verified 83 / open 20 / deferred 15 / fixed 6 / fixing 3` ⇒ ★**`fixing` 恰好 3 条 = 上面三个 (⇒ 每个总工正好一个在飞)** ★ ⇒ ★**`open` 20 条实测 owner 全是 `main` (15) / `boss` (5)** ⇒ ★**总工侧队列靠本轮新开的 ISS-228 转起来** ★
★**⇒ 本轮 A 段 = 1 派 (sw-lead), hw-lead / mech-lead 各 1 条真在飞不重派** ★

★**按原理图主线口径 (老板 2026-11-11 10:07) 本轮跳过 / 压着的 PCB 类** ★:
· ★**派出 1 条里 0 条是 PCB 布线/布局类** ★ (⇒ 是硬件选型/官方口径侧: 原理图主线的前置判据)
· ★**owner=main/boss 的板级 open 单继续压着不派**: `ISS-160` (demo 板图纸链/DRC 门禁 · blocker) · `ISS-169` (demo 板可制造性) · `ISS-126` (板厚档位) · `ISS-128` (板面积账 + 逃线层数) · `ISS-155` (rknn target · blocker) · `ISS-156` (主板三件前置选型) + ★**`ISS-181` (PCB 布线主线 · `deferred`)**
· ★**没藏账** (★它们仍列在 G4 未闭环清单 · `stage_gate` rc=1 / G1 仍开 ⇒ **不许投板没松**★) ★

### 0.41.2 ★★★ 落账 1 条: ISS-226 → `verified` (★main 05:2x 独立复核, 非抄交卷报告★) ★★★

· ★**为什么它是【僵尸 fixing】**: sw-lead 的子会话 ★**`subagent:dcd4e764` 于 2026-11-16 05:16:32 status=timeout**★ (★abortedLastRun=true · 最后两次 `edit` 的 toolResult = "Aborted"★) ⇒ ★**但成果已经全部落盘并全绿** ⇒ ★**不是"半成品僵尸", 是"【已交卷但交卷正文被平台砍掉】"** ★
· ★**main 自测 4/4 交付物在盘** ★: `SW/SW_BRIGHTNESS_CONTROL_POLICY.md` (17302 B · 05:04:32) · `SW/BRIGHTNESS_API_BLUE_RATIO.md` (14098 B · 05:07:37) · `SW/tools/check_brightness_biosafety.py` (26811 B · 05:10:34) · `HANDOFF/2026-11-16_sw-lead_ISS226_蓝光通道占比上限与亮度API.md` (39863 B · 05:14:09 · 402 行 · ★**B1~B6 六块齐全**★)
· ★**main 自己实跑门禁** ★: `python3 SW/tools/check_brightness_biosafety.py` → ★**rc=0**★ (C1 判据数值锁定 25% / 8.26% / Y三值 / 1500 cd/m² · C2 越限后果链 · C3 API 蓝通道占比量 · C4 跨域只读对账 · C5 不许编造实测值 · C6 降级方案 ⇒ 全过) ; ★**`--selftest` → rc=0 (13/13 反向用例全抓到)** ★
· ★**分片真落盘** ★: `state/fragments/sw.yaml` (mtime **05:12:52**) ⇒ artifact×3 + answer×1 (回 mech-lead 的 `iss134_sw_blue_drive_ratio_cap`) + interface_claim×2 (`sw_brightness_api_blue_ratio_field` / `..._board_state` = `null/uncalibrated`) + need×1 (`iss226_land_verified_and_reanchor` to=main)
· ★**中止留下的缺口已自查**: 交接单里 ★**零悬空引用** (A-28 那次编辑被中止 ⇒ 该行压根没写进去 ⇒ 没有任何地方引用 A-28)★ ⇒ ★**文件 402 行、尾部「阻塞: 无阻塞」段完整 ⇒ 不构成交付缺口, 不需要续做** ★
· ★**⇒ 落 verified 同时清掉僵尸占位 (★它占着 sw-lead 名额 ⇒ `advance.py` 的 in_flight 规则会让 sw-lead 永远拿不到新活★)** ★

### 0.41.3 ★★★ ★★ 本轮实测到的一条主线进展 + 一条必读预警 ★★ ★★★

· ★**主线进展 (★main 实跑, 不是推测★)**: ★**ISS-223 (hw-lead) 已落表第 2 批的前半段** ★ ⇒ ★**`HW/netlist_v1.csv` 于 05:18:41 重生成 (md5 `13f59a43…` → `3215020b…`) · `HW/netlist_v1_pins.csv` 于 05:18:56 重生成 (`a600afae…`) ⇒ 落表翻面口径「未落表条数」★**29 → 21**★ (★`HW/check_netlist_selfconsistency.py --expect-resolved` 实测★) ⇒ ★**这是原理图主线第一次真正往前走** ★
· ★**⚠ 必读预警 (★按设计会红, 不是新缺陷★)**: ★**两盏「锚点过期」的红被落表触发** ★ ——
  ① ★**`SW/tools/check_demo_panel_spec.py` 的 R6** (★盘上网表 `3215020b…` ≠ 台账锚点 `13f59a43…`★)
  ② ★**`MECH/check_demo_struct_truth.py` 的 G5b + C21** (★同一根因: MECH 台账锚点过期★) ⇒ ★**23 组检查里 2 组红 ⇒ 「21/23 通过」** ★
  ⇒ ★**这两盏正是 ISS-225 / ISS-224 建的三方对账机制在干活 (「只改 md5 锚点 = 悄悄换真源 = 红」)** ★ ⇒ ★**下一轮要另派 2 条重锚单 (SW 走 `SW/SW_MD5_BASELINE_LEDGER.md` §4 H-1 · MECH 走 `MECH/HW_CROSS_REVIEW_TRIAGE.md` §1)** ★ ⇒ ★**不许为了让它变绿去调判据** ★

### 0.41.4 ★★★ B 段: ★**恒空 0 条 + 19 份草稿一份没少 + 一封没发** ★★★

· ★**`advance.py --json` 的 `approvals` = 0 条** ⇒ ★**符合 2026-11-11 19:31「一律不发」+ 2026-11-12 02:02「不再发信, 全靠自己查资料」的新口径 ⇒ 本 job 【不发任何邮件 / 不联系任何供应商 / 不下采购单】★** ★
· ★**`state/outbox/` 实测 19 份 .md + `attach/` 3 个附件, 一份没少; `find -newermt "2026-11-16 00:00"` 实测 0 改动** ⇒ ★**今日 outbox 一个字节没动** ★
· ★**⇒ 本轮 B 段 = 0 动作 (★外发段恒空 ⇒ 没有「补写草稿」这回事★)** ★

### 0.41.5 ★★★ C 段: ★**38 → 38 (0 新增 / 0 退休 / 0 改建议默认值) —— 机器逐 key 核对** ★★★

· ★**`advance.py --json` 的 `decisions` 实测 38 个 key** ⇒ ★**逐个在本页里查: 命中 38 / 缺失 0** ★ (★机器跑, 不是目测★) ★
· ★**页内另有的 3 个 key (`sch_completeness_target` / `ref_designator_rename` / `iss191_reset_p0_fix_choice`) = §1c 已退休留档 ⇒ 本就不在 C 段 38 项里** ★
· ★**⇒ §1 ~ §9 的建议默认值原文一字未动** ★ ★

### 0.41.6 ★★★ 核验 5 连 (★本轮实测 rc★) + 原理图侧尺子 + GitHub + 快照 ★★★

| 项 | rc | 实测 |
|---|---|---|
| `state/merge.py` | ★**0** ★ | ★STATE.yaml 已刷新 (05:27:47) · 产出 **282** · 阻塞 **43** (高危 33) · 未闭合需求 **159** · 冲突 **0** · 健康度 red★ |
| `state/gate_check.py` | ★**0** ★ | ★【Q1 交付齐备率】**18/18** ★ · Q2 证据分级 3/3 · Q3 接口声明 **575** 条 · Q4 问方 **73/308** · ★**Q5 硬指标覆盖 2/3** (hw 2/5 · sw 3/5 · mech 4/5)★ · ★**Q6 硬件真源闸 ✅**★ |
| `state/issue_check.py` | ★**1** ★ | ★**224** 条问题单 · 内部 **195** / 外部 **29** · 逾期 **25** · ★**违规 26 条** (★25 逾期 + 1 条真幻觉引用 `source_blocker=MECH-JCHG-PINMAP-3SET`★)★ |
| `state/stage_gate.py` | ★**1** ★ | ★当前 **G1 原理图 / PCB 定稿** · 已过 ['G0'] · ★**还差 1 项**才能进 G2 (★G2 当期不做, 缺口 3 项留着★) ★ ⇒ ★**缺的那 1 项 = PCB 布线未达标: unconnected=45 (需 0) · DRC 违规=0 (需 0)** (ISS-181) ★ |
| `state/daily_check.py` | ★**3** ★ | ★巡检异常已记录 (快照已生成, 非崩溃) · ★**问题闭环门违规 26 条** · ★**PCB↔网表逐焊盘等价没过 (`check_pcb_nets` rc=1) ⇒ 板子与网表不一致, 不许投板**★ · ★**生产链准入/准出没过 (chain_gate) ⇒ 产物比源旧或缺件**★ · 原理图 ERC ✅ 0 条 (05:19:31) · 脚数完整性 ✅ 584/584 K=0 · 实测 0/4 项 · 漂移「内部未闭合 **127 → 159** / 问题单 **209 → 223**」★ |
| ★**原理图侧尺子** | ★**ERC 0 条 + 脚数 K=0** ★ | ★图上 **584** 脚 = 表里 **584** 脚 · 218 器件 / 153 网★ |
| GitHub | ★**本 job 不推** ★ | ★★老板 2026-11-11 09:5x 口径 ⇒ 统一由独立 job「ARS45 GitHub 同步 (每 5 小时 · 有进展才推)」负责★ ⇒ ★**本 job 只落本地快照, 没 rsync / 没 git commit / 没 git push / 没跑真值反查** ★ |
| 本地快照 | ★**已生成** ★ | ★`PROGRESS_SNAPSHOT.md` (4760 B · 05:26) ⇒ 只落本地, 随时能看★ |
| ★**本 job 动过的文件 (★全部是【记账 / 快照 / 派活台账】类, 无一是项目真源★)** | | ★**`DECISION_PENDING_2026-11-16.md`** (本页追加 §0.41) + ★**`PROGRESS_SNAPSHOT.md`** (快照脚本生成) + ★**`STATE.yaml`** (★`merge.py` / `daily_check.py` 自带刷新★) + ★**`state/gate_snapshots/2026-11-16_daily.json`** (★daily_check 自带★) + ★**`state/issue_log.yaml`** (★落账 ISS-226 verified + 新开 ISS-228 + 标 ISS-228 fixing★) + ★**`state/dispatch_log.yaml`** (★`advance.py --apply --only` 写的派活日志★) + ★**`state/_apply_20261116_0525_verify226_open228.py`** (记账脚本, 新建★) ⇒ ★**各总工分片我没写 · 板/网表/脚表/`.kicad_pro` 一个字节没动 (板 `611b869e…` · 网表 `3215020b…` · 脚表 `a600afae…` — 网表/脚表的 md5 变化是 ★hw-lead 的 ISS-223 会话在写, 不是我★) · `state/outbox/` 一个字节没动** ★ |

### 0.41.7 ★★ 本轮仍未替你决定任何一条 ★★

> ★**没有发任何邮件, 没有联系任何供应商, 没有下采购单, 没有改 §0 锁死表, 没有写任何子总工的分片, 没有动任何板/网表/脚表文件** ★★
> ★**C 段 38 条的建议默认值一个字没动** ⇒ ★**仍等你拍: §1 那 3 条 + §1b 那 1 条 (板子基线 p41) + §9 的 `V-2` (ESD 选型) + `V-4` (R_ILIM 档位) ⇒ 其余当期都不卡 demo 板 → G1 → 可下单** ★★
> ★**下一步**: 等 ISS-223 (hw-lead · 落表第 2 批 + F-1~F-5 + V-3 可判化) / ISS-227 (mech-lead · C-7b 集热面口径) / ISS-228 (sw-lead · GPIO0→VCCIO 官方映射) 交卷 → main 独立验收 → 名额释放 ⇒ ★**ISS-223 落表后另派 2 条重锚单 (SW 闸 R6 走台账 §4 H-1 · MECH 闸 G5b+C21)** ★

---

> ★ **本轮 C 段口径变化: 38 → 38 项 (0 新增 / 0 退休 / 0 改建议值)** —— ★**你不用重看 38 条的正文; 变的只是抬头/页尾的实数栏** ★★
> ★ **仍等你拍的当期要紧项 = §1 那 3 条 + §1b 那 1 条 + §9 的 V-2 / V-4** ⇒ ★**其余当期都不卡 demo 板 → G1 → 可下单** ★
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

    # ---- ② 追加 §0.41 ----
    src = open(DST, encoding="utf-8").read()
    if "## 0.41 ★★★" in src:
        print("⚠ §0.41 已在 ⇒ 幂等跳过")
    else:
        src = src.rstrip("\n") + "\n" + SEC041
        atomic_write(DST, src)
        print("✅ §0.41 已追加")

    print("页大小: %d B" % os.path.getsize(DST))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
