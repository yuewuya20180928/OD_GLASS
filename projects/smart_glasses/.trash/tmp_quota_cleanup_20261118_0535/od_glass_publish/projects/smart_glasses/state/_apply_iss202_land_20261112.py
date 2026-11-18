#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-202 落账: fixing → verified (★2026-11-12 02:4x 继续执行后继计划 job 落★)

★★**为什么要有这次落盘 (★实测, 不是推测★)** ★★:
· 本 job 02:2x 派 ISS-202 → mech-lead (★会话 `dc839eb5` / runId `6931153a`★)
· ★**子会话 02:26 派出 → 02:35 交卷完成** (★交卷页 `HANDOFF/2026-11-12_mech-lead_ISS202_J_CHG旧口径收尾.md`
  16,331 B, 02:34 落盘 + 会话最后一条 = 完整交卷报告★)
· ⇒ ★**如果现在不落账, 就会变成第 8 条僵尸 fixing** ⇒ ★**mech-lead 名额又被永久占住 ⇒ A 段又空**
  (★**同一个病第 8 次复发**★ ⇒ ★**这已经是本 job 连续第 2 次亲手清僵尸 (ISS-200 是第 7 次)★**)

★★**ISS-202 的交卷我逐条独立复核过 (★不采信自述★)** ★★:
· ★**逐脚真源自己复算**: `HW/netlist_v1.csv` J_CHG 逐脚 = pin1/2=BAT_CHG · pin3/4=GND ·
  pin5=CHG_STAT · pin6=PWR_GOOD · **pin7=NC** · **pin8=TS_BAT** · **pin9/10=HINGE_RSV**
  ⇒ 与它写进分片的两条 claim (`j_chg_pin_map` + `mech_j_chg_pins`) **逐脚一致** ★
· ★**`grep -c TS_RTN HW/netlist_v1.csv` ⇒ 0** (★这个网在网表里已完全不存在★)
· ★**claim key 唯一性**: `grep -c "^- key: j_chg_pin_map"` ⇒ **1** ·
  `grep -c "^- key: mech_j_chg_pins"` ⇒ **1** ⇒ ★**无 key 重复★**
· ★**§5.1 表 J_CHG 行已改**: 现值 = `10 (1×10 @0.5)` / 用到 **10** / 必装 **7** / DNP **3** /
  触点区宽 **3.5 mm (@0.5)** / 座体宽 **5.5 mm** (★**旧值是 `6 (1×6 @1.27)` / 5 / 0 / 6.35 / 8.35**★)
· ★**`MECH/USB_HINGE_STRUCTURE.md` 里 TS_RTN = 0 行** (★当前口径断言里一条都没有★);
  ★**`state/fragments/mech.yaml` 里 TS_RTN = 6 行, 我逐行看过 ⇒ 全部属于【变更说明 / 只报不改的残留报告 /
  历史沿革 / 已订正注记】四类 ⇒ 当前口径断言 0 条** ★
· ★**claims 总数 186 → 186 未变** (★没多写一条, 也没少一条★)
· ★**板 `611b869e` / 网表 `c78f9912` / pins `4814617e` / `.kicad_pro` `3e504d2b` 全部一字未变** ★
· `python3 state/merge.py` ⇒ **rc=0** (★冲突 0★) · `python3 state/gate_check.py` ⇒ **rc=0**
  (★**【Q1 交付齐备率】18/18**★ + ★**mech-lead 6/6, 交接单已换成它这份**★)

★★**它报的残留 (★已登记 need 给 main, 不在本单验收范围★)** ★★:
· ★**`iss202_mech_doc_residual_jchg_old_6pin`** (本文件还剩 11 处老 6 脚/8p 口径, ★**含 §5.1 L-1 行
  与 §2 的 C-3/C-6 两条表** ★) ⇒ ★**这正是 ISS-202 单子本身划出去的那 4 处之外的** ★
· ★**`iss202_mech_c4_stack_arith_pending`** (§5.3 C-4 的堆叠算式按哪套重算 —— ★**属几何数字变更**★)
· ★**`iss202_mech_script_recommended_pins_jchg_8`** (`MECH/hinge_usb_check.py` 的 `RECOMMENDED_PINS["J_CHG"]=8`
  ⇒ ★**24.0 mm 那条链的根**★)
· ★**`iss202_mech_other_docs_jchg_old_pinmap`** (FPC_FAB_NOTES / RELIABILITY_TEST_PLAN / STRUCT_REVIEW_ISS065 三份文档)
· ★**`iss202_mech_frag_old_needs_stale`** (本分片 2 条老 need 口径已过期)
⇒ ★**5 条全部 `to: main` + due 11-14 ⇒ 已进 C 段/待裁清单, 没藏账** ★

★★**落账纪律 (与项目既有范式一致)** ★★: ① flock(state/.issue_log.lock) + 锁内重读
② ★**自证: yaml.safe_dump(整份 doc, width=200) 必须与原文件逐字节相同** ★
③ 原子写 (tmp → fsync → os.replace → fsync(dir)) ④ ★**只改 ISS-202 一条** ★
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
STAMP = "2026-11-12 02:4x"
WIDTH = 200  # ★实测: 当前 issue_log.yaml 就是 advance.py --apply 用 width=200 写的★

VERIFY_RESULT = (
    "pass · 2026-11-12 02:4x 项目总工独立复核 (★不采信自述★)。\n"
    "★**达成**: ★**逐脚真源我自己复算** (`HW/netlist_v1.csv`): pin1/2=BAT_CHG · pin3/4=GND · "
    "pin5=CHG_STAT · pin6=PWR_GOOD · **pin7=NC** · **pin8=TS_BAT** · **pin9/10=HINGE_RSV** ⇒ "
    "★**与它写进分片的两条 claim (`j_chg_pin_map` + `mech_j_chg_pins`) 逐脚一致**★ · "
    "★**`grep -c TS_RTN HW/netlist_v1.csv` ⇒ 0**★ · "
    "★**claim key 唯一: `j_chg_pin_map` 计数 = 1 · `mech_j_chg_pins` 计数 = 1** (★无 key 重复★) · "
    "★**§5.1 表 J_CHG 行已改**: 现值 `10 (1×10 @0.5)` / 用到 **10** / 必装 **7** / DNP **3** / "
    "触点区宽 **3.5 mm (@0.5)** / 座体宽 **5.5 mm** (★**旧值 `6 (1×6 @1.27)` / 5 / 0 / 6.35 / 8.35**★) · "
    "★**`MECH/USB_HINGE_STRUCTURE.md` 里 TS_RTN = 0 行** (★当前口径断言里一条都没有★) · "
    "★**`state/fragments/mech.yaml` 里 TS_RTN = 6 行, 我逐行看过 ⇒ 全部属于【变更说明 / 只报不改的残留报告 / "
    "历史沿革 / 已订正注记】四类 ⇒ 当前口径断言 0 条**★ · "
    "★**claims 总数 186 → 186 未变**★ · "
    "★**板 `611b869e` / 网表 `c78f9912` / pins `4814617e` / `.kicad_pro` `3e504d2b` 全部一字未变**★ · "
    "`python3 state/merge.py` **rc=0** (★冲突 0★) · `python3 state/gate_check.py` **rc=0** "
    "(★**【Q1 交付齐备率】18/18**★ + ★**mech-lead 6/6, 交接单已换成它这份**★)\n"
    "★**它的写法纪律守住了 (值得记)**: ★**`state/frag_write.py --add-claim` 是【追加】不是【改写】** ⇒ "
    "★**它照 `MECH/_frag_update_iss200.py` 的范式新建 `MECH/_frag_update_iss202.py` (按 key 定位后替换那一条 + 原子写)** ⇒ "
    "★**交卷后两条 claim 各仍只有 1 条 (无 key 重复)**★ ⇒ ★**合并器冲突 0** ★\n"
    "★**它按纪律【只报不改】, 5 条残留全部登记成 need 给 main (★**都 `to: main` + due 11-14 ⇒ 已进待裁清单, 没藏账**★)**: "
    "★**① `iss202_mech_doc_residual_jchg_old_6pin`** (本文件还剩 11 处老 6 脚/8p 口径, 含 §5.1 L-1 行与 §2 的 C-3/C-6) · "
    "★**② `iss202_mech_c4_stack_arith_pending`** (§5.3 C-4 堆叠算式按哪套重算 —— ★**属几何数字变更**★) · "
    "★**③ `iss202_mech_script_recommended_pins_jchg_8`** (`MECH/hinge_usb_check.py` 的 `RECOMMENDED_PINS[\"J_CHG\"]=8` "
    "⇒ ★**24.0 mm 那条链的根**★) · ★**④ `iss202_mech_other_docs_jchg_old_pinmap`** (另外三份文档) · "
    "★**⑤ `iss202_mech_frag_old_needs_stale`** (本分片 2 条老 need 口径已过期) ★"
)

NOTE_EXTRA = (
    "\n★**2026-11-12 02:4x 继续执行后继计划 job 落账**: 本条 02:35 交卷 ⇒ ★**本 job 立即独立复核并签字** ★ "
    "(★**没等下一轮 cron** ⇒ ★**避免变成第 8 条僵尸 fixing** ⇒ ★**这是本 job 连续第 2 次亲手清僵尸 "
    "(ISS-200 是第 7 次, 本条若不落就是第 8 次)★**★)"
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
            if x.get("id") == "ISS-202":
                it = x
                break
        if it is None:
            print("★找不到 ISS-202 ⇒ 拒绝写")
            return 2
        if it.get("status") != "fixing":
            print("★ISS-202 当前 status=%s (不是 fixing) ⇒ 状态已变 ⇒ 拒绝写 (防覆盖别人的落盘)"
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
        print("✅ ISS-202 fixing → verified (★main 独立复核签字: 逐脚对拍一致 · TS_RTN 网表 0 次 · "
              "两条 claim 各 1 条无重复 · §5.1 表已改 10p · 文档 TS_RTN 0 行 · claims 186 未变 · "
              "板/网表/pins/.kicad_pro 一字未变 · merge rc=0 · Q1 18/18★)")
        print("   issue_log.yaml %d B → %d B" % (len(raw), len(out)))
        return 0


if __name__ == "__main__":
    sys.exit(main())
