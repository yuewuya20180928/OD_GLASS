#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-136 落账: fixing → verified (★2026-11-12 01:4x 队列自动派活 job 落★)

★★**为什么要有这次落盘 (★实测, 不是推测★)** ★★:
· `state/advance.py --json` 的 A 段 (internal) = **0 条** ⇒ 三个总工全被挡住
· ★**根因 = 又一条【僵尸 fixing 标记】 (★同一个病第 6 次复发★)**:
  - ISS-136 (hw-lead): 子会话 `824ac5a1` **00:18 派出 → 00:55 结束并交卷**
    (★交卷页 `HANDOFF/2026-11-12_hw-lead_ISS136_*.md` + 会话最后一条 = 完整交卷报告★)
  - 派它的是**本 job 自己** (父会话 `2893aa09`) ⇒ ★**子 agent 的完成事件投给了已收场的上一轮 cron 会话 ⇒ 没人落账** ★
    (★与 ISS-198 同病: 兄弟 cron `37f347cc` 在子 agent 交卷前 20 分钟就收场★)
  - ⇒ `issue_log.yaml` 里 ISS-136 的 status 永远停在 `fixing` ⇒ ★**`advance.py` 的 in_flight 规则
    ("该 agent 正在干别的, 本轮跳过") ⇒ hw-lead 名额被永久占住 ⇒ A 段恒空** ★

★★**ISS-136 的交卷我逐条独立复核过 (★不采信自述★)** ★★:
· `python3 HW/check_bq25896_pinout.py` **rc=0** (★PASS=11 / FAIL=0★)
· `python3 state/gate_check.py` **rc=0** ⇒ ★**【Q1 交付齐备率】18/18**★ + ★**【Q6 硬件真源闸】✅ 通过 (rc=0)**
  (★Q6 = 本单新接进门禁链的那一项 ⇒ 证明"接进去了"不是自述★)
· ★**板 `611b869e` / 网表 `c78f9912` / pins `4814617e` 全部一字未变** ★
· ★**§5.2 那张 pin map 表我逐脚对拍过网表**: pin1/2=BAT_CHG · pin3/4=GND · pin5=CHG_STAT ·
  pin6=PWR_GOOD · **pin7=NC** · **pin8=TS_BAT** · **pin9/10=HINGE_RSV** ⇒ ★**与 `HW/netlist_v1.csv` 逐脚一致** ★
  ⇒ ★**"网的表是唯一真源, 文档是镜像" 这条口径已经落地, 不是口号** ★

★★**它报的残留 (★已另开单, 不在本单验收范围★)** ★★:
· ★**HW 侧**: `HW/CHARGE_BOARD_SPEC.md` §5.1 过铰链线表 + §7 的 P10 csv 镜像块 ·
  `HW/J_CHG_SELECTION.md` (C-2 行 + §196 行) · `HW/POWER_SHUTDOWN_V3.md` (第 129 行) ⇒ ★**另开 ISS-199 (hw-lead)★**
· ★**结构侧**: `MECH/USB_HINGE_STRUCTURE.md` §5.x 那张**更老的 6 脚 pin map** (pin1=SYS/2=VBUS_DET/…)
  + `state/fragments/mech.yaml` 的 `interface_claims.j_chg_pin_map` (7=VBUS_DET/8=TS/9=RSV/10=TS_RTN)
  ⇒ ★**另开 ISS-200 (mech-lead)★** (★hw-lead 不许代改 mech 地界★)
· ★**结构侧 `interface_claims` 的 4 脚旧值** hw-lead 已按纪律登记成 need `iss136_spec_residual_sections_sync` (★在 `state/fragments/hw.yaml`★)

★★**落账纪律 (与项目既有范式一致)** ★★: ① flock(state/.issue_log.lock) + 锁内重读
② ★**自证: yaml.safe_dump(整份 doc) 必须与原文件逐字节相同** (⇒ 除本脚本要改的那一条外, 一个字节都不许动★)
③ 原子写 (tmp → fsync → os.replace → fsync(dir)) ④ 只改 ISS-136 一条 ⑤ 不动任何子总工的分片

★★**★为什么 width=200 (★实测出来的, 不是拍脑袋★)** ★★:
· ★**当前 `state/issue_log.yaml` 是 `advance.py --apply` 用 width=200 写出来的**
  (★实测: `yaml.safe_dump(doc, width=200)` 与原文【逐字节相同】(612218 B), width=80 差 16689 B★)
· ⇒ ★**本脚本用 width=200 往返自证 ⇒ 别的字节一个都不动** ★

★★**边界**: 板/网表/原理图/BOM 一个字节不动 · 不发邮件 · 不联系供应商/原厂 · 不替老板拍板
"""
from __future__ import annotations

import fcntl
import os
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
TODAY = "2026-11-12"
STAMP = "2026-11-12 01:4x"
WIDTH = 200  # ★实测: 当前文件就是 advance.py --apply 用 width=200 写的★

VERIFY_RESULT = (
    "pass · 2026-11-12 01:4x 项目总工独立复核 (★不采信自述★)。\n"
    "★**达成**: `python3 HW/check_bq25896_pinout.py` **rc=0** (PASS=11 / FAIL=0★) · "
    "`python3 state/gate_check.py` **rc=0** (★【Q1 交付齐备率】18/18★ + ★**【Q6 硬件真源闸】✅ 通过 (rc=0)★"
    "⇒ 证明本单新接进门禁链的那一项【真在跑】, 不是装饰★) · "
    "★**板 `611b869e` / 网表 `c78f9912` / pins `4814617e` 全部一字未变**★\n"
    "★**§5.2 pin map 表我逐脚对拍过网表**: pin1/2=BAT_CHG · pin3/4=GND · pin5=CHG_STAT · pin6=PWR_GOOD · "
    "**pin7=NC** · **pin8=TS_BAT** · **pin9/10=HINGE_RSV** ⇒ ★**与 `HW/netlist_v1.csv` 逐脚一致**★ ⇒ "
    "★**\"网表是唯一真源, 文档是它的镜像\" 这条口径已落地**★\n"
    "★**它挖到的根因比题单深一层 (★值得记★)**: 旧检查项 ⑦ 比的是\"脚本硬编快照 vs 网表\", ★**规格表 §5.2 根本不在判定里**★ ⇒ "
    "换掉规格表内容后结论一字不变 ⇒ ★**它那句\"规格 §5.2 提案 == 网表实际\"是假话**★ ⇒ ★**只对齐快照修不好, 明天再漂一次照样绿**★ ⇒ "
    "本单把 ⑦ 改成**实读规格表逐脚对拍** (并加 ⑦a 同脚多网防护) ⇒ ★**漂移 = 闸红**★\n"
    "★**残留已另开单 (不在本单范围)**: HW 侧 §5.1 表 + §7 P10 镜像块 + `HW/J_CHG_SELECTION.md` + `HW/POWER_SHUTDOWN_V3.md` ⇒ **ISS-199 (hw-lead)**; "
    "结构侧 `MECH/USB_HINGE_STRUCTURE.md` 的老 6 脚 map + `state/fragments/mech.yaml` 的 `j_chg_pin_map` ⇒ **ISS-200 (mech-lead)**"
)

NOTE_EXTRA = (
    "\n★**2026-11-12 01:4x 队列自动派活 job 落账**: 本条 00:55 交卷后一直停在 `fixing` "
    "(★僵尸标记 ⇒ 挡住 hw-lead 名额 ⇒ `advance.py` 的 A 段连续空★) ⇒ ★**根因**: 派它的**本 job 上一轮会话 "
    "`2893aa09` 在子 agent 交卷前就收场 ⇒ 完成事件投给了已死的会话 ⇒ 没人落账 ★ ⇒ "
    "★**main 独立复核通过后在此签字** ★"
)


def atomic_write(path: str, text: str) -> None:
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".issue_log.", suffix=".tmp")
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
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def main() -> int:
    os.makedirs(os.path.dirname(LOCK), exist_ok=True)
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        raw = open(LOG, encoding="utf-8").read()
        doc = yaml.safe_load(raw)
        issues = doc["issues"]

        # ---- 自证: yaml 往返必须逐字节相同 (除本脚本要改的, 一个字节都不许动) ----
        rt = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=WIDTH)
        if rt != raw:
            print("★自证失败: yaml.safe_dump(整份 doc, width=%d) 与原文件不一致 ⇒ 拒绝写 (防口径漂移)" % WIDTH)
            print("   原文件 %d B / 往返 %d B" % (len(raw), len(rt)))
            return 2

        it = None
        for x in issues:
            if x.get("id") == "ISS-136":
                it = x
                break
        if it is None:
            print("★找不到 ISS-136 ⇒ 拒绝写")
            return 2
        if it.get("status") != "fixing":
            print("★ISS-136 当前 status=%s (不是 fixing) ⇒ 状态已变 ⇒ 拒绝写 (防覆盖别人的落盘)" % it.get("status"))
            return 2

        it["status"] = "verified"
        it["verify_by"] = "main"
        it["verify_date"] = STAMP
        it["verify_result"] = VERIFY_RESULT
        it["fixed_at"] = TODAY
        it["note"] = (it.get("note") or "") + NOTE_EXTRA

        out = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=WIDTH)
        atomic_write(LOG, out)
        print("✅ ISS-136 fixing → verified (★main 独立复核签字: 闸 rc=0 · Q1 18/18 · Q6 真源闸在跑 · §5.2 逐脚对拍网表一致 · 板/网表/pins 一字未变★)")
        print("   issue_log.yaml %d B → %d B" % (len(raw), len(out)))
        return 0


if __name__ == "__main__":
    sys.exit(main())
