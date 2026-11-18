#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-203 落账: fixing → verified (★2026-11-12 02:5x 继续执行后继计划 job 落★)

★★**为什么要有这次落盘 (★实测, 不是推测★)** ★★:
· ★**ISS-203 (mech-lead) 由本 job 02:4x 派出** (★会话 `99dbdd7a` / runId `c4d75bc5` / taskName `advance_iss203`★)
· ★**子会话 02:4x 派出 → 02:47 结束并交卷** (★交卷页 `HANDOFF/2026-11-12_mech-lead_ISS203_两个机械复核器pcb_w迁30mm.md`
  20,441 B, 02:46 落盘★)
· ⇒ ★**如果现在不落账, 就是第 10 条僵尸 fixing** ⇒ ★**mech-lead 名额又被永久占住 ⇒ A 段又空** ★
  ⇒ ★**⇒ 本 job 连续第 4 次亲手清僵尸** (★**自己派的活, 自己必须在下一轮 cron 之前清掉**★)

★★**ISS-203 的交卷我逐条独立复核过 (★不采信自述★)** ★★:
· ★**两个脚本的 `pcb_w` 确实迁到 30.00**: `MECH/hw_cross_review_check.py:60` ⇒ `"pcb_w": 30.00` ·
  `MECH/service_port_check.py:51` ⇒ `"pcb_w": 30.00` ⇒ ★**旧注释「老板拍板 15mm / [决策 10-27]」也一并改掉**
  (★**grep 已验证: 那两句现在 0 命中** ⇒ ★**下一个人照注释走不回 15mm**★)
· ★**阈值一字未动 (★brief 明令「不许为了变绿而放宽」★)**: `judge = 0.60` (★`hw_cross_review_check.py:54★) ·
  `cav_v = 38.00` · `duct_v = 6.00` (★`service_port_check.py:37/53★) ⇒ ★**我逐条 grep 核对过, 全是原值** ★
· ★**★反向用例我亲手跑了 (★不是采信它的自述★)**: ★**把文件里的常量真的改回 15.00 跑一遍** ⇒
  ★**逐项数值真的回到迁移前** (缺 20.50 / 余 2.50 / 余 +5.00 / 超出 20.50) ⇒ ★**恢复 30.00 ⇒ 数值回到迁移后**
  (缺 5.50 / 余 17.50 / 余 -4.50 / 余 +20.00) ⇒ ★**⇒ 证明它真在读这个常量, 不是把结果写死** ★
  ⇒ ★**★而且它【如实说明了】为什么汇总计数两态相同**: ★**没有任何一条绿/红判定会因 15→30 而翻转**
  (★变的只是数值★) ⇒ ★**⇒ 反向用例的判据落在【逐项数值】上, 不是汇总计数上** ★ ⇒ ★**这一点我核对无误, 没有藏** ★
  ⇒ ★**脚本内建 `--self-test` 也过**: 两个脚本的 `--self-test` 末行都打「与迁移前基准 一致 ✅」 ★
· ★**两条真 FAIL 如实保留 (★没降级成 WARN 凑绿★)**: STK-FANOUT (FAIL→FAIL, 缺 5.50) ·
  MRG-54P (FAIL→FAIL, 余 -4.50) ⇒ ★**绿/红一条都没翻, 但也没为了好看去动它** ★
· ★**它推翻并订正了 ISS-197 的一个算错 (★值得记★)**: ISS-197 写「30mm 下全合并 54p 座体 30.00 vs 板宽 30.00 = 刚好放下」
  ⇒ ★**实测网表总 pin = 63p (CONN_CAM 31 + CONN_LIGHT 22 + J_CHG 10 + CONN_USB 0), 不是 54p** ⇒
  ★**座体 Y 向 = 34.50mm > 30.00 ⇒ 仍放不下 (余 -4.50)** ⇒ ★**它把该项标题里写死的「(54p@0.5mm)」改成
  「(63p@0.5mm · 网表实读)」** ⇒ ★**⇒ 下一个人不会再按 54p 算错** ★
· ★**它只报不改的 5 条 need 全部登记给 main** (★含 ISS-197 L1 那两条板长 claim 69mm/76mm 与现行 60.00mm
  不一致 ★**按指令只报不改值**★) ⇒ ★**没藏账** ★
· `python3 state/merge.py` ⇒ **rc=0** (★冲突 0★) · `python3 state/gate_check.py` ⇒ **rc=0** (★**【Q1】18/18**★)
· ★**板 `611b869e` / 网表 `c78f9912` / pins `4814617e` / `.kicad_pro` 全部一字未变** ★

★★**落账纪律 (与项目既有范式一致)** ★★: ① flock(state/.issue_log.lock) + 锁内重读
② ★**自证: yaml.safe_dump(整份 doc, width=200) 必须与原文件逐字节相同** ★
③ 原子写 (tmp → fsync → os.replace → fsync(dir)) ④ ★**只改 ISS-203 一条** ★
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
STAMP = "2026-11-12 02:5x"
WIDTH = 200  # ★实测: 当前 issue_log.yaml 就是 advance.py --apply 用 width=200 写的★

VERIFY_RESULT = (
    "pass · 2026-11-12 02:5x 项目总工独立复核 (★不采信自述★)。\n"
    "★**达成**: ★**两个脚本的 `pcb_w` 确实迁到 30.00** (`hw_cross_review_check.py:60` / `service_port_check.py:51`) · "
    "★**旧注释「老板拍板 15mm / [决策 10-27]」一并改掉 (grep 验证那两句现在 0 命中 ⇒ 下一个人照注释走不回 15mm)** ★\n"
    "★**阈值一字未动 (★brief 明令「不许为了变绿而放宽」★)**: ★**`judge = 0.60`** · ★**`cav_v = 38.00`** · "
    "★**`duct_v = 6.00`** ⇒ ★**我逐条 grep 核对过, 全是原值** ★ ⇒ ★**两条真 FAIL (STK-FANOUT / MRG-54P) "
    "如实保留, 没降级成 WARN 凑绿** ★\n"
    "★**★反向用例我亲手跑了 (★不是采信它的自述★)**: ★**把文件里的常量真的改回 15.00 跑一遍 ⇒ 逐项数值真的回到迁移前** "
    "(缺 20.50 / 余 2.50 / 余 +5.00 / 超出 20.50) ⇒ ★**恢复 30.00 ⇒ 数值回到迁移后** (缺 5.50 / 余 17.50 / "
    "余 -4.50 / 余 +20.00) ⇒ ★**⇒ 证明它真在读这个常量, 不是把结果写死** ★ ⇒ ★**且它【如实说明了】为什么汇总计数两态相同**: "
    "★**没有任何一条绿/红判定会因 15→30 而翻转 (变的只是数值) ⇒ 反向用例的判据落在【逐项数值】上, 不是汇总计数上** ★ "
    "⇒ ★**这一点我核对无误, 没有藏** ★ ⇒ ★**两个脚本内建的 `--self-test` 也都过 (末行「与迁移前基准 一致 ✅」)** ★\n"
    "★**★它推翻并订正了 ISS-197 的一个算错 (★值得记★)**: ★**ISS-197 写「30mm 下全合并 54p 座体 30.00 vs 板宽 30.00 "
    "= 刚好放下」⇒ 实测网表总 pin = 63p (CONN_CAM 31 + CONN_LIGHT 22 + J_CHG 10 + CONN_USB 0), 不是 54p** ⇒ "
    "★**座体 Y 向 = 34.50mm > 30.00 ⇒ 仍放不下 (余 -4.50)** ⇒ ★**它把该项标题里写死的「(54p@0.5mm)」改成 "
    "「(63p@0.5mm · 网表实读)」** ⇒ ★**⇒ 下一个人不会再按 54p 算错** ★\n"
    "★**它只报不改的 5 条 need 全部登记给 main** (★**含 ISS-197 L1 那两条板长 claim 69mm/76mm 与现行 60.00mm 不一致 "
    "⇒ 按指令只报不改值**★) ⇒ ★**没藏账** ★\n"
    "★**其余**: `state/merge.py` ⇒ **rc=0** (冲突 0) · `state/gate_check.py` ⇒ **rc=0** (【Q1】18/18) · "
    "★**板 `611b869e` / 网表 `c78f9912` / pins `4814617e` / `.kicad_pro` 一字未变** ★"
)

NOTE_EXTRA = (
    "\n★**2026-11-12 02:5x 继续执行后继计划 job 落账**: 本条 02:47 交卷 ⇒ ★**本 job 立即独立复核并签字** ★ "
    "(★**没等下一轮 cron** ⇒ ★**避免变成第 10 条僵尸 fixing** ⇒ ★**这是本 job 连续第 4 次亲手清僵尸** ★ "
    "★**同病复发史: ISS-198 / ISS-136 / ISS-200 / ISS-202 / ISS-201 / 本条 ⇒ 第 5~10 次** ★ "
    "★**⇒ 该修的是【谁派谁落账】的流程, 不是这一条单** ★)"
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
            if x.get("id") == "ISS-203":
                it = x
                break
        if it is None:
            print("★找不到 ISS-203 ⇒ 拒绝写")
            return 2
        if it.get("status") != "fixing":
            print("★ISS-203 当前 status=%s (不是 fixing) ⇒ 状态已变 ⇒ 拒绝写 (防覆盖别人的落盘)"
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
        print("✅ ISS-203 fixing → verified (★main 独立复核签字: pcb_w 两脚本均迁 30.00 · 旧注释已改 · "
              "阈值 judge/cav_v/duct_v 一字未动 · 反向用例亲跑 (数值真变) · 两条真 FAIL 保留 · "
              "63p 算错已订正 · merge rc=0 · Q1 18/18 ★)")
        print("   issue_log.yaml %d B → %d B" % (len(raw), len(out)))
        return 0


if __name__ == "__main__":
    sys.exit(main())
