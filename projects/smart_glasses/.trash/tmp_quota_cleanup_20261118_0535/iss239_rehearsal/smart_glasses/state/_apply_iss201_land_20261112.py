#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-201 落账: fixing → verified (★2026-11-12 02:4x 继续执行后继计划 job 落★)

★★**为什么要有这次落盘 (★实测, 不是推测★)** ★★:
· ★**ISS-201 (sw-lead) 由兄弟 job「ARS45 队列自动派活」在 02:0x 派出** (★会话 `be918818`★
  · runId `72a84ab6` · taskName `queue_iss201`★)
· ★**子会话 02:15 派出 → 02:31 结束并交卷** (★交卷页 `HANDOFF/2026-11-12_sw-lead_ISS201_台账登记重建件.md`
  17,654 B, 02:30 落盘 + 会话最后一条 = 完整交卷报告★)
· ⇒ ★**`issue_log.yaml` 里它的 status 永远停在 `fixing`** ⇒ ★**又一条僵尸 fixing (★**第 9 条**★)** ⇒
  ★**`advance.py` 的 in_flight 规则挡住 sw-lead 的名额** ⇒ ★**本 job 连续第 3 次亲手清僵尸** ★
  (★**同病复发史**: ISS-198 / ISS-136 / ISS-200 / ISS-202 / ★**本条**★ ⇒ ★**该修的是"谁派谁落账"的流程,
  不是这一条单**★)

★★**ISS-201 的交卷我逐条独立复核过 (★不采信自述★)** ★★:
· ★**`python3 SW/tools/rknn_bench.py probe` ⇒ "台账一致: True"** (★这正是本单的核心判据★
  ★**改前实测是 False**★)
· ★**两个重建件的行 C1/C2/C3 全 ✅**:
  `MOD-YOLOV5S-640-ARS45-REBUILD` ⇒ C1 文件存在 (29,365,856 B) · C2 大小一致 · C3 sha256[:16] `1e2c716bd16ed9d3` 一致
  `MOD-YOLOV5N-640-ARS45-REBUILD` ⇒ C1 文件存在 (7,931,774 B) · C2 大小一致 · C3 sha256[:16] `dfb5d060ca36fc27` 一致
· ★**交付集条目数 = 2 (★与基线一致, 未变多★)**: 实跑输出「交付集 (candidate/active): **2 条**」★
  ★**基线上限断言 `SHIP_BASELINE_MAX = 2` 在脚本里 (第 925 行) ⇒ 交付集不许变多是硬判据, 不是口号** ★
  ⇒ ★**两个重建件都落在 `licensing-hold` (★**禁入交付物**★) ⇒ ★**没有因为"文件现在能用"就进交付集** ★
· ★**原件确实丢失 (我反查过)**: 全盘搜 `20368be665f6f59a` ⇒ **0 命中** ⇒ ★**原 ID 的 state 改成
  `missing` (★**不是 `quarantined`**★) 是对的** ⇒ ★**台账不再冒充原件** ★
· ★**`missing` 状态词三处同时加** (★脚本 26 处 + 台账 3 处★) ⇒ ★**没拿 `quarantined` 顶替** ★
· ★**许可不许猜**: 两个重建件 = `unknown` [0数据] (★`license_probe.py` 实测 metadata_props 的
  license/author/version 全为 None★) ⇒ ★**没沿用原件的 AGPL-3.0 结论** ★
· ★**反向用例我亲手跑了 2 条 (★不是采信它的自述★)**:
  ① ★**把 `ONNX_MODEL_SHA16` 改回 `"20368be665f6f59a"` ⇒ `probe` 立刻打回 "台账一致: False"** ⇒ 恢复 ⇒ 打回 True
     ⇒ ★**证明它真在读磁盘文件, 不是把结果写死** ★
  ② ★**把脚本 MANIFEST 里重建件的 sha 改一位 ⇒ 该行 C3 立刻 ❌ FAIL** ⇒ 恢复 ⇒ ✅
     ⇒ ★**证明台账↔实物是真比对** ★
  ⇒ ★**两个用例跑完都恢复了, 三个文件 diff 逐字节核对一致** ★
· ★**`model_asset_check.py --selftest` ⇒ rc=0 (0 条失败)** ★
· ★**`python3 state/merge.py` ⇒ rc=0 (冲突 0)** · `python3 state/gate_check.py` ⇒ rc=0 (★**【Q1】18/18**★)
· ★**板 `611b869e` / 网表 `c78f9912` / pins `4814617e` / `.kicad_pro` 全部一字未变** ★
· ★**磁盘上那两个 `.onnx` 本体 mtime 仍是 11-02 20:41 ⇒ 没被动过** (★brief 明令不许动本体★)

★★**关于 `model_asset_check.py` 整体 rc=1 (★brief 明写"别自欺"★)** ★★:
· 实测 FAIL 10 · ★**全是别的资产的 C1「文件不存在」/ 原件缺失, 与本单无关** ★
· ⇒ ★**brief 明令: 「若整体 rc 仍为 1 ⇒ 如实列出来, 不许去改别人的行来凑 rc=0」** ★
· ⇒ ★**本单相关的行全绿 (两个重建件 C1/C2/C3 全 ✅) ⇒ 判定通过** ★

★★**落账纪律 (与项目既有范式一致)** ★★: ① flock(state/.issue_log.lock) + 锁内重读
② ★**自证: yaml.safe_dump(整份 doc, width=200) 必须与原文件逐字节相同** ★
③ 原子写 (tmp → fsync → os.replace → fsync(dir)) ④ ★**只改 ISS-201 一条** ★
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
    "★**核心判据达成**: ★**`python3 SW/tools/rknn_bench.py probe` ⇒ 「台账一致: True」** (★**改前实测是 False**★) ★\n"
    "★**两个重建件的行 C1/C2/C3 全 ✅**: `MOD-YOLOV5S-640-ARS45-REBUILD` (C1 文件存在 29,365,856 B · C2 大小一致 · "
    "C3 sha256[:16] `1e2c716bd16ed9d3` 一致) · `MOD-YOLOV5N-640-ARS45-REBUILD` (C1 7,931,774 B · C2 一致 · "
    "C3 `dfb5d060ca36fc27` 一致) ★\n"
    "★**交付集口径 (本单的命门)**: 实跑「交付集 (candidate/active): **2 条**」⇒ ★**与基线一致, 未变多**★ ⇒ "
    "★**两个重建件都落在 `licensing-hold` (禁入交付物) ⇒ 没有因为\"文件现在能用\"就进交付集**★ ⇒ "
    "★**基线上限 `SHIP_BASELINE_MAX = 2` 是脚本里的硬断言 (第 925 行), 不是口号**★ ★\n"
    "★**台账不再冒充原件**: ★**我反查过 —— 全盘搜 `20368be665f6f59a` ⇒ 0 命中 ⇒ 原件确实丢失** ★ ⇒ "
    "★**原 ID 的 state 改成 `missing` (不是 `quarantined`) 是对的** ★ ⇒ ★**`missing` 状态词三处同时加** "
    "(脚本 26 处 + 台账 3 处) ⇒ ★**没拿 `quarantined` 顶替** ★\n"
    "★**许可不许猜**: 两个重建件 = `unknown` [0数据] (★`license_probe.py` 实测 metadata_props 的 "
    "license/author/version 全为 None★) ⇒ ★**没沿用原件的 AGPL-3.0 结论** ★\n"
    "★**反向用例我亲手跑了 2 条 (★不是采信它的自述★)**: ① ★**把 `ONNX_MODEL_SHA16` 改回 `\"20368be665f6f59a\"` ⇒ "
    "`probe` 立刻打回「台账一致: False」⇒ 恢复 ⇒ 打回 True ⇒ ★**证明它真在读磁盘文件, 不是把结果写死** ★ "
    "② ★**把脚本 MANIFEST 里重建件的 sha 改一位 ⇒ 该行 C3 立刻 ❌ FAIL ⇒ 恢复 ⇒ ✅ ⇒ "
    "★**证明台账↔实物是真比对** ★ ⇒ ★**两个用例跑完都恢复了, 三个文件 diff 逐字节核对一致** ★\n"
    "★**其余**: `model_asset_check.py --selftest` ⇒ **rc=0 (0 条失败)** · `state/merge.py` ⇒ **rc=0 (冲突 0)** · "
    "`state/gate_check.py` ⇒ **rc=0 (【Q1】18/18)** · ★**板 `611b869e` / 网表 `c78f9912` / pins `4814617e` / "
    "`.kicad_pro` 一字未变** ★ · ★**磁盘上那两个 `.onnx` 本体 mtime 仍是 11-02 20:41 ⇒ 没被动过** ★\n"
    "★**关于 `model_asset_check.py` 整体 rc=1 (★brief 明写「别自欺」★)**: 实测 FAIL 10 ⇒ ★**全是别的资产的 "
    "C1「文件不存在」/ 原件缺失, 与本单无关** ★ ⇒ ★**brief 明令: 不许去改别人的行来凑 rc=0** ⇒ "
    "★**本单相关的行全绿 ⇒ 判定通过** ★\n"
    "★**它报的残留已登记 need 给 main (★许可未判定 ⇒ `iss201_rebuild_model_license`★)** ⇒ ★**没藏账** ★"
)

NOTE_EXTRA = (
    "\n★**2026-11-12 02:4x 继续执行后继计划 job 落账**: 本条 02:31 交卷 ⇒ ★**本 job 立即独立复核并签字** ★ "
    "(★**没等下一轮 cron** ⇒ ★**避免变成第 9 条僵尸 fixing** ⇒ ★**这是本 job 连续第 3 次亲手清僵尸** ★ "
    "★**同病复发史: ISS-198 / ISS-136 / ISS-200 / ISS-202 / 本条 ⇒ 该修的是「谁派谁落账」的流程, 不是这一条单** ★)"
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
            if x.get("id") == "ISS-201":
                it = x
                break
        if it is None:
            print("★找不到 ISS-201 ⇒ 拒绝写")
            return 2
        if it.get("status") != "fixing":
            print("★ISS-201 当前 status=%s (不是 fixing) ⇒ 状态已变 ⇒ 拒绝写 (防覆盖别人的落盘)"
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
        print("✅ ISS-201 fixing → verified (★main 独立复核签字: probe 台账一致 True · 两个重建件 C1/C2/C3 全绿 · "
              "交付集 2 条未变多 · 原件确实丢失 · missing 词三处同加 · 2 条反向用例亲跑 · merge rc=0 · Q1 18/18 ★)")
        print("   issue_log.yaml %d B → %d B" % (len(raw), len(out)))
        return 0


if __name__ == "__main__":
    sys.exit(main())
