#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-198 落账: fixing → verified (★2026-11-12 00:1x 队列自动派活 job 落★)

★★**为什么要有这次落盘 (★实测, 不是推测★)** ★★:
· `state/advance.py --json` 的 A 段 (internal) = **0 条** ⇒ 三个总工全被挡住
· ★**根因 = 又一条【僵尸 fixing 标记】 (★同一个病第 5 次复发★)**:
  - ISS-198 (hw-lead): 子会话 `bc24a9a4` **23:37 派出 → 23:58 结束并交卷** (★交卷页 `HANDOFF/2026-11-11_hw-lead_ISS198_查找表补全.md`★)
  - 派它的是兄弟 cron `ARS45 继续执行后继计划` (会话 `37f347cc`) ⇒ ★**该会话的 transcript 在 23:38:37 之后再无写入**
    (★最后一行 = "merge rc=0 gate_check rc=0 issue_check rc=1 stage_gate rc=1 daily_check rc=3"★)
    ⇒ ★**它在子 agent 交卷前 20 分钟就收场了 ⇒ 子 agent 的完成事件投递给了已死的会话 ⇒ 没人落账** ★
  - ⇒ `issue_log.yaml` 里 ISS-198 的 status 永远停在 `fixing` ⇒ ★**`advance.py` 的 in_flight 规则
    ("该 agent 正在干别的, 本轮跳过") ⇒ hw-lead 名额被永久占住 ⇒ A 段恒空** ★
· ★**本单落完, A 段恢复 ⇒ ISS-136 / ISS-195 可以继续派** ★

★★**ISS-198 的交卷我逐条独立复核过 (★不采信自述★)** ★★:
· `python3 state/gen_kicad_sch.py --pin-gap` **rc=0** ⇒ **218 器件 / 真实脚数可查 215 / 查不到 3**
  (★那 3 个全是非器件: `BT_432243` 电池座待选型 / `CHG_GND_STAR` 汇流位 / `X1` 晶振焊盘位★)
  ⇒ ★**`PIN_REALITY_GAP.md` 器件级 `[0数据]` 29 → 3 (★下限, 达成单目标★)** ★
· `python3 state/check_sch_pinfull.py` **rc=0** (★图上 584 脚 / 表里 584 脚 · K=0 · 逐器件全相等★)
· `python3 state/check_sch_erc.py` **rc=0** (★ERC 违规 0★)
· `python3 state/merge.py` **rc=0** (★产出 175 · 冲突 0★) · `python3 state/gate_check.py` **rc=0**
  (★【Q1 交付齐备率】18/18★)
· ★**板 `611b869e` / 网表 `c78f9912` / pins `4814617e` / `.kicad_pro` `3e504d2b` 全部一字未变** ★
· ★**它报的 5 条硬件发现 (封装与器件不自洽) 已由它自己登记成 need `iss198_pkg_vs_device_mismatch_5`
  (★`state/fragments/hw.yaml` 72 条 needs 里在★) ⇒ ★**已入账, 不再另开单** ★

★★**它报的 2 处偏离 (★留给 main, 不在本单验收范围★)** ★★:
· `Q1`/`Q2` 用了 `CSD16301Q2` (★同厂牌同封装代理 Texas_DQK · 实测 8 脚★) 而不是 BOM 里的 `CSD16406Q3`
  ⇒ ★**是【符号代理】不是改 BOM** (★`HW/BOM_v1.csv` 里 Q1/Q2 的 opn 仍是 `CSD16406Q3`★) ⇒ 脚数口径一致 (★8 脚★) ★
· `D_ESD_CAM/DEMO/LIGHT/USB_D` 用 `TPD1E05U06DPY` (★2 脚★) 而不是 4 脚阵列 (★板上只有 2 焊盘, 4 脚装不上★)

★★**落账纪律 (与项目既有范式一致)** ★★: ① flock(state/.issue_log.lock) + 锁内重读
② ★**自证: yaml.safe_dump(整份 doc) 必须与原文件逐字节相同** (⇒ 除本脚本要改的那一条外, 一个字节都不许动★)
③ 原子写 (tmp → fsync → os.replace → fsync(dir)) ④ 只改 ISS-198 一条 ⑤ 不动任何子总工的分片

★★**★为什么 width=80 (★实测出来的, 不是拍脑袋★)** ★★:
· ★**当前 `state/issue_log.yaml` 是 hw-lead 在 23:58 (★它交卷那一刻★) 用默认 width 写出来的** (★实测: max 行长 228,
  `yaml.safe_dump(doc, width=80)` 与原文【逐字节相同】, width=200 则差 16,689 B★)
· ⇒ ★**本脚本必须用 width=80 往返自证 ⇒ 否则自证必然失败 ⇒ 别的字节一个都不动** ★
· ⇒ ★**注意**: `state/advance.py --apply` 用的是 width=200 ⇒ ★**它下一次 --apply 会把整份文件重新折行 (★纯排版, 数据一字不变★)** ★

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
STAMP = "2026-11-12 00:1x"

VERIFY_RESULT = (
    "pass · 2026-11-12 00:1x 项目总工独立复核 (★不采信自述★)。\n"
    "★**达成**: `python3 state/gen_kicad_sch.py --pin-gap` **rc=0** ⇒ **218 器件 / 真实脚数可查 215 / 查不到 3** "
    "(★那 3 个全是非器件: `BT_432243` 电池座待选型 / `CHG_GND_STAR` 汇流位 / `X1` 晶振焊盘位★) "
    "⇒ ★**`HW/PCB/PIN_REALITY_GAP.md` 器件级 `[0数据]` 29 → 3 (★达成单目标的下限★)**★ · "
    "`python3 state/check_sch_pinfull.py` **rc=0** (★图上 584 脚 / 表里 584 脚 · K=0★) · "
    "`python3 state/check_sch_erc.py` **rc=0** (★ERC 违规 0★) · `python3 state/merge.py` **rc=0** (★产出 175 · 冲突 0★) · "
    "`python3 state/gate_check.py` **rc=0** (★【Q1 交付齐备率】18/18★) · "
    "★**板 `611b869e` / 网表 `c78f9912` / pins `4814617e` / `.kicad_pro` `3e504d2b` 全部一字未变**★ ⇒ "
    "★**三张查找表真补上了 (★老板【选项③ 真实器件全貌】的内部那一半输入已攒齐★)**★\n"
    "★**它报的 2 处偏离 (★留给 main, 不在本单验收范围★)**: ① `Q1`/`Q2` 用 `CSD16301Q2` (★同厂牌同封装代理 Texas_DQK · "
    "实测 8 脚★) 代替 BOM 里的 `CSD16406Q3` ⇒ ★**是【符号代理】不是改 BOM** (★BOM 里 Q1/Q2 的 opn 仍是 `CSD16406Q3`★) "
    "⇒ 脚数口径一致 ② `D_ESD_CAM/DEMO/LIGHT/USB_D` 用 `TPD1E05U06DPY` (★2 脚★) 而不是 4 脚阵列 (★板上只有 2 焊盘★)\n"
    "★**它报的 5 条硬件发现 (封装与器件不自洽: `U_SUPV` 缺 GND/MR · `U_LDO_S28` 缺 EN · `Q1/Q2` 5 焊盘且外形≠SON-8 · "
    "`D_ESD_USB_D` 标双通道但板上单通道 · `U_BATPROT` 焊盘编号 2..7≠1..6★) 已由它自己登记成 need "
    "`iss198_pkg_vs_device_mismatch_5` (★`state/fragments/hw.yaml`★) ⇒ ★**已入账, 不另开单**★ ⇒ "
    "★**全是 DNP/待选型件, 没炸板, 但【转必装 = 改板级 (2-4 周)】⇒ 选型前必须核**★"
)

NOTE_EXTRA = (
    "\n★**2026-11-12 00:1x 队列自动派活 job 落账**: 本条 23:58 交卷后一直停在 `fixing` "
    "(★僵尸标记 ⇒ 挡住 hw-lead 名额 ⇒ `advance.py` 的 A 段连续空★) ⇒ ★**根因**: 派它的兄弟 cron "
    "`ARS45 继续执行后继计划` (会话 `37f347cc`) 在 **23:38:37 就收场** (★子 agent 23:58 才交卷 ⇒ 完成事件投给了已死的会话★) "
    "⇒ ★**main 独立复核通过后在此签字** ★"
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
        # ★width=80 = 当前文件的真实排版 (★实测往返逐字节相同★) ⇒ 换成 200 会把整份文件重折行 ⇒ 不许
        rt = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=80)
        if rt != raw:
            print("★自证失败: yaml.safe_dump(整份 doc) 与原文件不一致 ⇒ 拒绝写 (防口径漂移)")
            print("   原文件 %d B / 往返 %d B" % (len(raw), len(rt)))
            return 2

        it = None
        for x in issues:
            if x.get("id") == "ISS-198":
                it = x
                break
        if it is None:
            print("★找不到 ISS-198 ⇒ 拒绝写")
            return 2
        if it.get("status") != "fixing":
            print("★ISS-198 当前 status=%s (不是 fixing) ⇒ 状态已变 ⇒ 拒绝写 (防覆盖别人的落盘)" % it.get("status"))
            return 2

        it["status"] = "verified"
        it["verify_by"] = "main"
        it["verify_date"] = STAMP
        it["verify_result"] = VERIFY_RESULT
        it["fixed_at"] = TODAY
        it["note"] = (it.get("note") or "") + NOTE_EXTRA

        out = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=80)
        atomic_write(LOG, out)
        print("✅ ISS-198 fixing → verified (★main 独立复核签字: [0数据] 29→3 · 闸全 rc=0 · 板/网表/pins 一字未变★)")
        print("   issue_log.yaml %d B → %d B" % (len(raw), len(out)))
        return 0


if __name__ == "__main__":
    sys.exit(main())
