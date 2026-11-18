#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-200 落账: fixing → verified (★2026-11-12 02:2x 继续执行后继计划 job 落★)

★★**为什么要有这次落盘 (★实测, 不是推测★)** ★★:
· `python3 state/advance.py --json` 的 A 段 (internal) = **0 条** ⇒ 三个总工全被挡住
· ★**根因 = 又一条【僵尸 fixing 标记】 (★同一个病第 7 次复发★)**:
  - ISS-200 (mech-lead): 子会话 `0ef5e479` **01:48 派出 → 01:58 结束并交卷**
    (★交卷页 `HANDOFF/2026-11-12_mech-lead_ISS200_J_CHG接口契约收敛.md` (17,177 B, 01:57 落盘)
      + 会话最后一条 = 完整交卷报告★)
  - 派它的是**兄弟 job「ARS45 队列自动派活」** (`fb67af40`) ⇒ ★**子 agent 的完成事件投给了已收场的会话
    ⇒ 没人落账** ★ (★与 ISS-136 / ISS-198 同病★)
  - ⇒ `issue_log.yaml` 里 ISS-200 的 status 永远停在 `fixing` ⇒ ★**`advance.py` 的 in_flight 规则
    ("该 agent 正在干别的, 本轮跳过") ⇒ mech-lead 名额被永久占住 ⇒ A 段恒空** ★
  - ★**兄弟 job 自己在 02:0x 的交卷里已经点破这件事并"排好队等收口释放"** ⇒ ★**释放是 main 的活** ★

★★**ISS-200 的交卷我逐条独立复核过 (★不采信自述★)** ★★:
· ★**网表逐脚真源** (`HW/netlist_v1.csv`, 我自己 grep 出来的, 没照抄题单):
  pin1/2=BAT_CHG (行 15/16/17/76/497) · pin3/4=GND (行 22/23) · pin5=CHG_STAT (行 189/482) ·
  pin6=PWR_GOOD (行 61/192/481) · **pin7=NC** (行 433) · **pin8=TS_BAT** (行 42/478) ·
  **pin9/10=HINGE_RSV** (行 20/21) ⇒ ★**与它写进分片的 `j_chg_pin_map` 逐字一致** ★
· ★**`grep -c "TS_RTN" HW/netlist_v1.csv` ⇒ 0** (★这个网在网表里已完全不存在★)
· ★**`grep -c "^- key: j_chg_pin_map" state/fragments/mech.yaml` ⇒ 1** (★无 key 重复★)
· ★**`MECH/USB_HINGE_STRUCTURE.md` 里 TS_RTN 只剩【历史沿革/作废说明】的提及, 当前口径断言 0 条** ★
· ★**claims 总数 186 → 186 未变** (★没多写一条, 也没少一条★)
· ★**板 `611b869e` / 网表 `c78f9912` / pins `4814617e` / `.kicad_pro` `3e504d2b` 全部一字未变** ★
· `python3 state/merge.py` ⇒ **rc=0** (★冲突 0★ · 产出 179 · 未闭合需求 106)
· `python3 state/gate_check.py` ⇒ **rc=0** (★**【Q1 交付齐备率】18/18**★)

★★**它报的残留 (★已另开单, 不在本单验收范围★)** ★★:
· ★**结构侧剩 5 处** (`MECH/USB_HINGE_STRUCTURE.md` §5.1 表 / §5.3 C-4 / §5.3 C-1 尾巴 / F-5·F-6
  + `state/fragments/mech.yaml` 的另一条 claim `mech_j_chg_pins` 的 note)
  ⇒ ★**已另开 ISS-202 (mech-lead)** ★ (★我 02:2x 实测确认那 5 处确实还在: §5.1 表仍写
  「6 (1×6 @1.27) / 触点区宽 6.35 mm」· §5.3 C-4 仍写「J_CHG → 8p @0.5」· §5.3 C-1 尾巴仍写
  「SYS 单触点载流下降 → 2 脚并联」⇒ ★**ISS-202 不是空单**★)
· ★**HW 侧 4 处** (`HW/CHARGE_BOARD_SPEC.md` §5.1 / §7 P10 镜像块 / `HW/J_CHG_SELECTION.md` ×2 /
  `HW/POWER_SHUTDOWN_V3.md` 第 129 行) ⇒ ★**已另开 ISS-199 (hw-lead)** ★

★★**落账纪律 (与项目既有范式一致)** ★★: ① flock(state/.issue_log.lock) + 锁内重读
② ★**自证: yaml.safe_dump(整份 doc, width=200) 必须与原文件逐字节相同** (★实测当前文件就是
width=200 写的 ⇒ 除本脚本要改的那一条外, 一个字节都不许动★)
③ 原子写 (tmp → fsync → os.replace → fsync(dir)) ④ ★**只改 ISS-200 一条** ★
⑤ ★**status 不是 fixing 就拒绝写** (防覆盖别人的落盘) ⑥ 不动任何子总工的分片

★★**边界**: 板/网表/原理图/BOM 一个字节不动 · 不发邮件 · 不联系供应商 · 不替老板拍板
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
STAMP = "2026-11-12 02:2x"
WIDTH = 200  # ★实测: 当前 issue_log.yaml 就是 advance.py --apply 用 width=200 写的★

VERIFY_RESULT = (
    "pass · 2026-11-12 02:2x 项目总工独立复核 (★不采信自述★)。\n"
    "★**达成**: ★**网表逐脚真源我自己 grep 过** (`HW/netlist_v1.csv`): pin1/2=BAT_CHG (行 15/16/17/76/497) · "
    "pin3/4=GND (行 22/23) · pin5=CHG_STAT (行 189/482) · pin6=PWR_GOOD (行 61/192/481) · "
    "**pin7=NC** (行 433) · **pin8=TS_BAT** (行 42/478) · **pin9/10=HINGE_RSV** (行 20/21) "
    "⇒ ★**与它写进分片的 `j_chg_pin_map` 逐字一致**★ · "
    "★**`grep -c \"TS_RTN\" HW/netlist_v1.csv` ⇒ 0** (★这个网在网表里已完全不存在★) · "
    "★**`grep -c \"^- key: j_chg_pin_map\" state/fragments/mech.yaml` ⇒ 1** (★无 key 重复★) · "
    "★**`MECH/USB_HINGE_STRUCTURE.md` 里 TS_RTN 只剩【历史沿革/作废说明】的提及, 当前口径断言 0 条**★ · "
    "★**claims 总数 186 → 186 未变**★ · "
    "★**板 `611b869e` / 网表 `c78f9912` / pins `4814617e` / `.kicad_pro` `3e504d2b` 全部一字未变**★ · "
    "`python3 state/merge.py` **rc=0** (★冲突 0★ · 产出 179 · 未闭合需求 106) · "
    "`python3 state/gate_check.py` **rc=0** (★**【Q1 交付齐备率】18/18**★)\n"
    "★**它挖到的根因比题单深一层 (★值得记★)**: ★**防呆结论本身没变, 变的是【理由】**★ —— "
    "老 6 脚口径下「反插 = SYS 直短 GND ⇒ 烧 MOS」; ★**现行 10p map 下 180° 翻转 = pin i ↔ pin 11-i "
    "⇒ BAT_CHG 落到 HINGE_RSV = 断路不短接**★ ⇒ ★**真实风险变成 GND(pin3)↔TS_BAT(pin8) 短 + "
    "CHG_STAT(pin5)↔PWR_GOOD(pin6) 短**★ ⇒ ★**\"机械防呆仍必需\" 结论不变, 论证必须换**★ "
    "(★这条已登记给 ISS-199 / ISS-202 一起改, 不许留着一份错的论证★)\n"
    "★**它按纪律【只报不改】, 残留已全部另开单 (不在本单验收范围)**: ★**结构侧剩 5 处 ⇒ ISS-202 (mech-lead)** "
    "(★我 02:2x 实测确认那 5 处确实还在 ⇒ 不是空单★) · ★**HW 侧 4 处 ⇒ ISS-199 (hw-lead)**★"
)

NOTE_EXTRA = (
    "\n★**2026-11-12 02:2x 继续执行后继计划 job 落账**: 本条 01:58 交卷后一直停在 `fixing` "
    "(★僵尸标记 ⇒ 挡住 mech-lead 名额 ⇒ `advance.py` 的 A 段连续空★) ⇒ ★**根因**: 派它的**兄弟 job "
    "「ARS45 队列自动派活」在子 agent 交卷前就收场 ⇒ 完成事件投给了已死的会话 ⇒ 没人落账 ★ ⇒ "
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
            if x.get("id") == "ISS-200":
                it = x
                break
        if it is None:
            print("★找不到 ISS-200 ⇒ 拒绝写")
            return 2
        if it.get("status") != "fixing":
            print("★ISS-200 当前 status=%s (不是 fixing) ⇒ 状态已变 ⇒ 拒绝写 (防覆盖别人的落盘)"
                  % it.get("status"))
            return 2

        it["status"] = "verified"
        it["verify_by"] = "main"
        it["verify_date"] = STAMP
        it["verify_result"] = VERIFY_RESULT
        it["fixed_at"] = TODAY
        it["note"] = (it.get("note") or "") + NOTE_EXTRA

        out = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=WIDTH)
        atomic_write(LOG, out)
        print("✅ ISS-200 fixing → verified (★main 独立复核签字: 网表逐脚对拍一致 · TS_RTN 网表 0 次 · "
              "claim key 无重复 · claims 186 未变 · 板/网表/pins/.kicad_pro 一字未变 · merge rc=0 · Q1 18/18★)")
        print("   issue_log.yaml %d B → %d B" % (len(raw), len(out)))
        return 0


if __name__ == "__main__":
    sys.exit(main())
