#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-211 / 212 / 213 / 199 / 025 落 verified (2026-11-16 00:2x, 项目总工 main)

★★**为什么要有这次落盘 (★实测, 不是推测★)** ★★
· `state/advance.py --json` 的 A 段 (internal) = **0 条** ⇒ 三个总工全被挡住
· ★**根因 = 三条【僵尸 fixing 标记】** (★同病第 16 次复发, 本轮 3 条★):
  子会话 `agent:hw-lead:subagent:0d265be5` (sessionId `b72ab61d`) **23:59:59 结束, status=done**
  · `agent:sw-lead:subagent:7dc28258` (sessionId `95c3eb34`) **00:02:51 结束, status=done**
  · `agent:mech-lead:subagent:3d52360d` (sessionId `e53c34a3`) **00:00:26 结束, status=done**
  ⇒ ★**三份交卷单已落盘 (HANDOFF/2026-11-15_*_ISS211/212/213_*.md) · 三套机器门禁全绿**
  ⇒ ★**但 brief 明写「不许碰 state/issue_log.yaml (改 issue 状态是 main 的活)」⇒ 子 agent 没落账**
  ⇒ ★**status 停在 `fixing`** ⇒ ★**`advance.py` 的 in_flight 规则 ⇒ 三个总工的名额全被占住**
  ⇒ ★**⇒ 队列彻底断线 (A 段 0 条) —— 这就是本轮"没活可派"的真原因, 不是没活** ★
· ★**`state/alignment_check.py` 实测同步报了这三张僵尸**: "ISS-211 处于 fixing 超过 24.2 小时仍无 fix_ref"
  ⇒ 三个总工各占 24.2 小时 ⇒ ★**同一个病第三次同时发作在三个 agent 上** ★

★★**另外两条 `fixed` 卡住闸门 (★对齐检查第 3 条实测点名★)** ★★
· ISS-199 (hw-lead) `fixed` + 有交卷单 ⇒ 对齐检查报 "有交卷单但台账未 verified/closed"
· ISS-025 (mech-lead) `fixed` + 有交卷单 ⇒ 同上
  ⇒ ★**两条的交付物与门禁本轮都实测过 ⇒ 一并落 `verified` (★落 `verified` 不是 `closed`★)** ★

★★**交卷我独立复核过 (★不采信自述, 只看盘上实物 + 自己跑门禁★)** ★★
★**ISS-211 (hw-lead)**: `python3 HW/check_netlist_selfconsistency.py` → **rc=0** (★自述"门禁是现状守卫不是合格证",
  4 条缺陷仍在 ⇒ rc=0 是预期状态★) · `--selftest` → **9/9** (用例1 改坏 L167 value ⇒ 红 / 用例2 改坏 L182 dnp ⇒ 红 /
  用例4 改坏 BOM L208 type ⇒ 红 / 用例5 改坏 SPEC.json B-01.level ⇒ 红 / 用例6 改坏板封装 Value ⇒ 红) ·
  `--expect-resolved` → **rc=1** (★翻面口径现状就该红, 缺陷尚未落表★)
★**ISS-212 (sw-lead)**: `python3 SW/tools/check_demo_panel_spec.py` → **rc=0** (R1~R6 全过) · `--selftest` → **8/8**
  (REV-1 把 pipeline 的 demo 口径塞回 1920×1080 ⇒ R3 红 / REV-5 删掉"无 DCS"结论 ⇒ R1 红 / REV-8 删定性表 L-22 ⇒ R5 红)
★**ISS-213 (mech-lead)**: `python3 MECH/check_demo_struct_truth.py` → **rc=0 (20/20 组检查全过, FAIL 0 组)** ·
  `--selftest` → **8/8 反向用例全被抓** (板宽 30→15 ⇒ G4/G4b 红 / 判据 CRIT 0.60→0.30 ⇒ G2.4+G5 红 /
  排队表删 FRM-SUM ⇒ G3 红 / FAIL 名单删 NET-LED ⇒ G1b 红)
★**ISS-199 (hw-lead)**: `python3 HW/check_bq25896_pinout.py` → **rc=0 (11/11 PASS, 0 FAIL)** ·
  逐处实读: `HW/CHARGE_BOARD_SPEC.md` §5.1 表 + §5.1 订正注记 + §7 P10 csv 镜像块 · `HW/J_CHG_SELECTION.md` ×2 ·
  `HW/POWER_SHUTDOWN_V3.md` §129 (已标"已撤除 (2026-11-03)") ★**全部已是新口径 (pin7=NC / pin8=TS_BAT / pin9-10=HINGE_RSV)**
★**ISS-025 (mech-lead)**: `python3 MECH/dfm_check.py` → **rc=0** · 交付物 `MECH/DFM_REVIEW.md` (61,650 B) +
  `MECH/dfm_check.py` + `HANDOFF/2026-11-01_mech-lead_ISS025_结构DFM评审.md` (24,328 B) 三件俱在
★**受保护文件 md5 逐字节未变 (★本轮开工前后同值★)**: 网表 `c78f991283cc82d56c8e3dd31657c785` ·
  脚表 `4814617e22b567d76164e56bc5e39dc8` · 板 `611b869e13518c3c023fb178f91a0075` ·
  `.kicad_pro` `3e504d2be83152e337949723e909be1b`

★★**落账纪律 (照 `state/_apply_iss210_verify_20261115.py` 的同一套) ★★:
① flock(state/.issue_log.lock) + 锁内重读 ② ★**yaml 往返逐字节自证** ③ 原子写 ④ ★**只改这 5 条** ★

★★**边界**: 不改 `PROJECT_TRACKER.md` §0 锁死表 · 不写任何子总工的分片 · 不发邮件 / 不联系供应商 /
不下采购单 · 板 / 网表 / 脚表 / 原理图 / BOM 一个字节不动 · ★**只落 issue 状态, 不改任何设计产物** ★
"""
from __future__ import annotations

import fcntl
import os
import shutil
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
BAK = LOG + ".bak_20260716_0030_verify_211_212_213_199_025"

VDATE = "2026-11-16 00:3x"

RES = {
    "ISS-211": (
        "pass · 2026-11-16 00:3x 项目总工独立复核 (★不采信自述, 只看盘上实物 + 自己跑门禁★)\n"
        "★**① 交付物 3 件** [实测]: `HW/NETLIST_SELF_CONSISTENCY_SPEC.md` · `HW/check_netlist_selfconsistency.py` · "
        "`HANDOFF/2026-11-15_hw-lead_ISS211_网表自身一致性4处.md` (5,751 B, 23:58 落盘)\n"
        "★**② 机器门禁实跑** [实测]: `python3 HW/check_netlist_selfconsistency.py` → **rc=0** (★门禁是【现状守卫】"
        "不是【合格证】⇒ 4 条缺陷★仍在★⇒ rc=0 是预期状态★) · `--selftest` → **9/9 通过** "
        "(用例1 改坏 L167 value ⇒ 红 / 用例2 改坏 L182 dnp ⇒ 红 / 用例3 删 L169『已作废』⇒ 红 / 用例4 改坏 BOM L208 type ⇒ 红 / "
        "用例5 改坏 SPEC.json B-01.level ⇒ 红 / 用例6 改坏板封装 U_EN_SW Value ⇒ 红 / 用例8 删 L417 Forlinx 规矩引用 ⇒ 红) · "
        "`--expect-resolved` → **rc=1** (★翻面口径现状就该红★)\n"
        "★**③ 受保护文件 md5 逐字节未变** [实测]: 网表 `c78f991283cc82d56c8e3dd31657c785` · 脚表 `4814617e22b567d76164e56bc5e39dc8` · "
        "板 `611b869e13518c3c023fb178f91a0075` · `.kicad_pro` `3e504d2be83152e337949723e909be1b`\n"
        "★**④ 未决**: 4 条缺陷须随整链重出第 1 步落表 (★参数侧缺口已开 **ISS-214** 承接★)"
    ),
    "ISS-212": (
        "pass · 2026-11-16 00:3x 项目总工独立复核 (★不采信自述★)\n"
        "★**① 交付物 4 件** [实测]: `SW/DEMO_PANEL_WAVESHARE_2P8_SPEC.md` · `SW/DEMO_PANEL_SPEC_TRIAGE.md` · "
        "`SW/tools/check_demo_panel_spec.py` · `HANDOFF/2026-11-15_sw-lead_ISS212_demo显示侧重锚Waveshare.md` (6,589 B, 00:01 落盘)\n"
        "★**② 机器门禁实跑** [实测]: `python3 SW/tools/check_demo_panel_spec.py` → **rc=0** (R1 demo 屏真源 / R2 整机口径只在占位区 / "
        "R3 pipeline demo 活动口径已重锚 / R4 整机占位带标注 / R5 逐处定性表 38 处完整 / R6 受保护文件 md5 未变 全过) · "
        "`--selftest` → **8/8 通过** (REV-1 塞回 1920×1080 ⇒ R3 红 / REV-3 删 480×640 ⇒ R1 红 / REV-5 删『无 DCS』⇒ R1 红 / "
        "REV-6 删 ≤100 kHz ⇒ R1 红 / REV-8 删定性表 L-22 ⇒ R5 红)\n"
        "★**③ 口径纪律**: 显示侧不宽判 (TX 2.304ms / 合成段余量 7.79ms 均带 [推算] 与同口径出处) · 60ms 与 15.10ms 未调松 · "
        "板端一切 = [0数据]\n"
        "★**④ ★★未决 (★本轮实测发现, 已开 ISS-215 承接★)**: ★**ISS-212 重锚了 demo 屏口径, 但它明确不碰的 4 个下游文件"
        "(§3.3.1 60ms 判据表 / VERDICT_PLAN / rknn_bench S9 注记 / demo_timing_check) 仍全是退役的 1920×1080 口径** ⇒ "
        "★**demo 的 60ms 生死判定基础仍是旧显示几何** ⇒ ★**已在 ISS-215 立单, 本单不越界改它** ★"
    ),
    "ISS-213": (
        "pass · 2026-11-16 00:3x 项目总工独立复核 (★不采信自述★)\n"
        "★**① 交付物 4 件** [实测]: `MECH/HW_CROSS_REVIEW_TRIAGE.md` (308 行 · 54 项逐条定性 + 17 条 FAIL 去处表) · "
        "`MECH/check_demo_struct_truth.py` · `HANDOFF/2026-11-15_mech-lead_ISS213_结构54项定性表与demo真缺陷收口.md` (8,482 B, 23:58 落盘) · "
        "`state/fragments/mech.yaml` (走 frag_write 原子写)\n"
        "★**② 机器门禁实跑** [实测]: `python3 MECH/check_demo_struct_truth.py` → **rc=0 (20/20 组检查全过, FAIL 0 组)** · "
        "`--selftest` → **8/8 反向用例全被抓** (板宽 30→15 ⇒ G4/G4b 红 / 判据 CRIT 0.60→0.30 ⇒ G2.4+G5 红 / 新开孔退回 9.50 ⇒ G2.2 红 / "
        "FAIL 名单删 NET-LED ⇒ G1b 红 / 排队表删 FRM-SUM ⇒ G3 红 / cavity_req 4.50→5.00 ⇒ G5 红)\n"
        "★**③ ★★判据纪律 (★关键★)**: 17 条 FAIL **仍然是 FAIL** (★排队等原理图定稿, 是【正确状态】不是缺陷★) · "
        "判据阈值一个没松 (cavity_req 4.50 / CRIT 0.60 / cav_v 38.00 / duct_v 6.00) · 6 个 PCB 类 id 仍排队 · "
        "板框四数 60.00/30.00/1.00/3.33g 未变 · ★**实物 [实测] = 0 条** ★\n"
        "★**④ 受保护文件 md5 逐字节未变** [实测]: 8 个受保护文件 (板/网表/脚表/.kicad_pro + 4 个 check 脚本) 全部一致\n"
        "★**⑤ 未决**: 6 条新 need 交 main (★其中『充电耗散口径 0.8W→buck』已在 **ISS-216** 立项★)"
    ),
    "ISS-199": (
        "pass · 2026-11-16 00:3x 项目总工独立复核 (★不采信自述★)\n"
        "★**① 交付物**: `HANDOFF/2026-11-15_hw-lead_ISS199_J_CHG_pinmap_第2口径收敛.md` (18,236 B)\n"
        "★**② 机器门禁实跑** [实测]: `python3 HW/check_bq25896_pinout.py` → **rc=0 (11/11 PASS, 0 FAIL)** (含检查项⑦ 实读 §5.2 表逐脚对拍网表)\n"
        "★**③ 逐处实读确认已改净** [实测]: `HW/CHARGE_BOARD_SPEC.md` §5.1 表 + §5.1 订正注记 + §7 P10 csv 镜像块 · "
        "`HW/J_CHG_SELECTION.md` ×2 (C-2 行 + L196 行) · `HW/POWER_SHUTDOWN_V3.md` §129 (已标『TS 专用回流 —— 已撤除 (2026-11-03)』) "
        "★**全部已是新口径 (pin7=NC / pin8=TS_BAT / pin9-10=HINGE_RSV) 且带『已按网表真源订正 (ISS-199 · 2026-11-12)』标记** ★\n"
        "★**④ ★★遗留 (★不判本单失败, 已开 ISS-214 承接★)**: `HW/CHARGE_STATUS_READBACK.md:43` 仍是第 5 套旧口径 "
        "(pin7=VBUS_DET / pin8=TS / pin9-10=预留) ⇒ ★**hw-lead 交卷时已自己登记 need `iss199_jchg_pinmap_residual_5th_vocab` 给 main** "
        "⇒ ★**本单范围是 4 处, 第 5 处超出本单范围 ⇒ 本单判 pass, 第 5 处转 ISS-214** ★"
    ),
    "ISS-025": (
        "pass · 2026-11-16 00:3x 项目总工独立复核 (★不采信自述★)\n"
        "★**① 交付物 3 件** [实测]: `MECH/DFM_REVIEW.md` (61,650 B · 脱模斜度逐面统计 + 注塑/压铸可行性判据 + 量产架构建议 + 收缩敏感性) · "
        "`MECH/dfm_check.py` (19,721 B) · `HANDOFF/2026-11-01_mech-lead_ISS025_结构DFM评审.md` (24,328 B)\n"
        "★**② 机器门禁实跑** [实测]: `python3 MECH/dfm_check.py` → **rc=0** · 核心结论复现: 注塑 ±0.20 比 FDM ±0.30 紧 ⇒ "
        "V/H/L 三链最坏值改善 (1.40→1.60 / 0.65→0.75 / 13.60→13.90) · 双面 1° ⇒ 内腔横截面窄端少 1.327mm ⇒ "
        "镜脚 H 链最坏 0.75 − 1.327 = **−0.577 ⇒ 几何上做不出来** ⇒ 量产架构必须延续『打印件负责造型 + 金属件承担定位/承力』\n"
        "★**③ 交叉印证**: 同一 −0.577mm 结论已被 **ISS-127 (verified)** 独立复算确认 ⇒ ★**本单结论与已验收单一致, 不是孤证** ★\n"
        "★**④ 口径纪律**: 全文 [推算] 标注, 未冒充实测; 量产后外形件几何 0 数据点由 MECH-B-DFM-1 继续挂账"
    ),
}

NOTE = (
    "\n★**2026-11-16 00:3x 项目总工 (main) 落 `verified` (★清僵尸 fixing 第 16 次复发·本轮 3 条同时发作★)**:\n"
    "★**实测**: 子会话 `agent:hw-lead:subagent:0d265be5` (b72ab61d) 23:59:59 done · "
    "`agent:sw-lead:subagent:7dc28258` (95c3eb34) 00:02:51 done · `agent:mech-lead:subagent:3d52360d` (e53c34a3) 00:00:26 done "
    "⇒ ★**交卷已投递、文件已落盘** ⇒ ★**但 brief 不许子 agent 改 issue_log ⇒ status 停在 `fixing`** ⇒ "
    "★**`advance.py` 的 in_flight 规则 ⇒ 三个总工名额全被占住 ⇒ A 段 0 条 ⇒ 队列断线** ⇒ "
    "★**main 独立复核 (只看盘上实物 + 自己跑门禁) 通过 ⇒ 落 `verified` (★不是 closed★) ⇒ 放出三个名额** ★\n"
    "★**边界**: 不改 §0 锁死表 · 不写任何子总工的分片 · 不发信 · 板/网表/脚表/原理图/BOM 一个字节未动 ★\n"
)

FIX_REF = {
    "ISS-211": "HANDOFF/2026-11-15_hw-lead_ISS211_网表自身一致性4处.md",
    "ISS-212": "HANDOFF/2026-11-15_sw-lead_ISS212_demo显示侧重锚Waveshare.md",
    "ISS-213": "HANDOFF/2026-11-15_mech-lead_ISS213_结构54项定性表与demo真缺陷收口.md",
    "ISS-199": "HANDOFF/2026-11-15_hw-lead_ISS199_J_CHG_pinmap_第2口径收敛.md",
    "ISS-025": ("MECH/DFM_REVIEW.md (结构 DFM 评审: 脱模斜度逐面统计 + 注塑/压铸可行性判据 + 量产架构建议 + 收缩敏感性) + "
                "MECH/dfm_check.py (自证脚本 rc=0) + HANDOFF/2026-11-01_mech-lead_ISS025_结构DFM评审.md"),
}

EXPECT = {"ISS-211": "fixing", "ISS-212": "fixing", "ISS-213": "fixing",
          "ISS-199": "fixed", "ISS-025": "fixed"}


def atomic_write(path: str, data: str) -> None:
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".issue_log.", suffix=".tmp")
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
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def main() -> int:
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        with open(LOG, encoding="utf-8") as f:
            raw = f.read()
        log = yaml.safe_load(raw)

        rt = yaml.safe_dump(log, allow_unicode=True, sort_keys=False, width=200)
        if rt != raw:
            print("❌ yaml 往返不一致 ⇒ 拒绝落盘")
            return 2
        print("✅ yaml 往返逐字节一致 (自证通过)")

        issues = log.get("issues") or []
        by_id = {i.get("id"): i for i in issues}

        for iid, want in EXPECT.items():
            it = by_id.get(iid)
            assert it is not None, "%s 不存在" % iid
            assert it.get("status") == want, "%s status=%s 非 %s" % (iid, it.get("status"), want)
            assert it.get("owner") != "main", "%s owner=main 不能自验" % iid
            assert it.get("verify_by") == "main", "%s verify_by=%s 非 main" % (iid, it.get("verify_by"))
            it["status"] = "verified"
            it["verify_by"] = "main"
            it["verify_result"] = RES[iid]
            it["verify_date"] = VDATE
            it["fixed_at"] = "2026-11-16"
            it["fix_ref"] = FIX_REF[iid]
            it["note"] = (it.get("note") or "") + NOTE

        log["issues"] = issues
        shutil.copy2(LOG, BAK)
        atomic_write(LOG, yaml.safe_dump(log, allow_unicode=True, sort_keys=False, width=200))
        print("备份:", BAK)
        for iid in EXPECT:
            print(" - %s (%s) → verified (main 独立复核)" % (iid, by_id[iid].get("owner")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
