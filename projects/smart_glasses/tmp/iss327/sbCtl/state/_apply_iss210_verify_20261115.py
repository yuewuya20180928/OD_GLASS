#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-210 落 verified + 放行 sw-lead 名额 (2026-11-15 22:4x, 项目总工 main)

★★**为什么要有这次落盘 (★实测, 不是推测★)** ★★:
· `state/advance.py --json` 的 A 段 (internal) = **0 条** ⇒ 三个总工全被挡住
· ★**根因 = ISS-210 的【僵尸 fixing 标记】**(★同病第 15 次复发, 本轮第 3 条★):
  子会话 `agent:sw-lead:subagent:b37f1504` (sessionId `067b4580`) **2026-11-15 22:40:19 结束,
  status=done** ⇒ ★**交卷已投递、文件已落盘** ⇒ 但 ★**brief 明写「不许碰 state/issue_log.yaml
  (改 issue 状态是 main 的活)」⇒ 子 agent 没落账 ⇒ status 停在 `fixing`** ★
· ★**注意时序**: 22:4x 本轮先落 ISS-174 / ISS-209 时, ISS-210 会话**仍在跑** ⇒ ★**当时显式 assert
  「ISS-210 状态必须是 fixing」⇒ 不碰它** ⇒ ★**它 22:40:19 才交卷 ⇒ 本脚本单独收尾** ★

★★**交卷我独立复核过 (★不采信自述, 只看盘上实物 + 自己跑门禁★)** ★★:
· ✅ 交付物 5 件 + 连带件 1 件:
  `SW/DEMO_OD_TIMING_SPEC.md` (25,578 B · 22:28 · ★v1.2 新增**段 12 = ISP**★)
  · `SW/DEMO_BOARD_60MS_VERDICT_PLAN.md` (24,577 B · 22:35)
  · `HANDOFF/2026-11-15_sw-lead_ISS210_60ms判据链.md` (3,834 B · 22:39)
  · `SW/tools/timing_check.py` (87,578 B · 22:30 · ★新增 F9_isp_budget 判据★)
  · `SW/tools/demo_timing_check.py` (12,492 B · 22:34 · ★连带件: 段表/CSV 表头机械核对器★)
  · `state/fragments/sw.yaml` (★+5 artifact / +2 claim / +1 answer, 未动别人的 key★)
· ✅ `python3 SW/tools/timing_check.py` **rc=0** (★SELFTEST **68/68** 通过; 含反向用例:
  ★"ISP avg = 15.11 ms ⇒ 必须 FAIL (超 15.10 必被抓)" · "15.10 ms ⇒ 恰好 PASS" ·
  "现占位 8.00 ms ⇒ 余量 +7.09 ms" · "p95 = 18.00 ms ⇒ 模式B 上限 17.33 FAIL"★)
· ✅ `python3 SW/tools/demo_timing_check.py` **rc=0** (★时序接力表 = **12 段** (段号 1..12, 含段 12 = ISP) ·
  ★"本单未编造板端时延数字" · ★板端 = [0数据] (无板)★)
· ✅ `python3 SW/tools/isp_budget_solve.py` **rc=0** (★SELFTEST **11/11**; 敏感性带最保守端 γ=0.8
  满载仍全部超 43°C ⇒ 结论对插值形状不敏感★)
· ✅ 规格逐字抽查 [实测]: `SW/DEMO_OD_TIMING_SPEC.md:66` (v1.2 公告) · `:77` (段 12 = ISP 行全文)
  · `:86` (段 10 汇总含段 12) · `:110` (三时间戳 `ts_isp_in` / `ts_isp_hw_start` / `ts_isp_out`)
· ✅ md5 两件一字未变: 网表 `c78f991283cc82d56c8e3dd31657c785` · 板 `611b869e13518c3c023fb178f91a0075`
· ★**口径纪律**: 判定线取 ISS-124 的发布值 **15.10 / 17.33 ms** (精确反解 15.095) ⇒ ★**60 ms 与 15.10
  均未调松**; ★**板端一切 = [0数据], 本单 0 条板端 [实测]** ★
⇒ ★**处置 = 落 `verified` (★不是 closed★) ⇒ 放出 sw-lead 名额** ★

★★**落账纪律 (照 `state/_apply_iss199_fixed_20261115.py` 的同一套) ★★:
① flock(state/.issue_log.lock) + 锁内重读 ② ★**yaml 往返逐字节自证** ③ 原子写 ④ ★**只改 ISS-210 一条** ★

★**边界**: 不改 `PROJECT_TRACKER.md` §0 锁死表 · 不写任何子总工的分片 · 不发邮件 / 不联系供应商 /
不下采购单 · 板 / 网表 / 原理图 / BOM 一个字节不动 · ★**只落 issue 状态, 不改任何设计产物** ★
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
BAK = LOG + ".bak_20261115_2245_verify_210"

IID = "ISS-210"
FIX_REF = "HANDOFF/2026-11-15_sw-lead_ISS210_60ms判据链.md"

RES = (
    "pass · 2026-11-15 22:4x 项目总工独立复核 (★不采信自述★)\n"
    "★**① 交付物 5 件 + 连带件 1 件** [实测]: `SW/DEMO_OD_TIMING_SPEC.md` (25,578 B · 22:28 · ★v1.2 新增段 12 = ISP★) · "
    "`SW/DEMO_BOARD_60MS_VERDICT_PLAN.md` (24,577 B · 22:35) · "
    "`HANDOFF/2026-11-15_sw-lead_ISS210_60ms判据链.md` (3,834 B · 22:39) · "
    "`SW/tools/timing_check.py` (87,578 B · 22:30 · ★新增 F9_isp_budget 判据★) · "
    "`SW/tools/demo_timing_check.py` (12,492 B · 22:34 · ★连带件·段表/CSV 表头核对器★) · "
    "`state/fragments/sw.yaml` (★+5 artifact / +2 claim / +1 answer, 未动别人的 key★)\n"
    "★**② 机器门禁** [实测]: `python3 SW/tools/timing_check.py` **rc=0** (★SELFTEST **68/68**; 含反向: "
    "ISP avg = 15.11 ms ⇒ 必须 FAIL · 15.10 ms ⇒ 恰好 PASS · 现占位 8.00 ms ⇒ 余量 +7.09 ms · "
    "p95 = 18.00 ms ⇒ 模式B 上限 17.33 FAIL★) · `python3 SW/tools/demo_timing_check.py` **rc=0** "
    "(★时序接力表 = **12 段** (1..12, 含段 12 = ISP) · ★未编造板端时延数字★ · ★板端 = [0数据]★) · "
    "`python3 SW/tools/isp_budget_solve.py` **rc=0** (★SELFTEST **11/11**; γ=0.8 最保守端满载仍全部超 43°C★)\n"
    "★**③ 规格逐字抽查** [实测]: `SW/DEMO_OD_TIMING_SPEC.md:66` (v1.2 公告) · `:77` (段 12 = ISP 行) · "
    "`:86` (段 10 汇总含段 12) · `:110` (三时间戳 `ts_isp_in` / `ts_isp_hw_start` / `ts_isp_out`)\n"
    "★**④ 受保护文件 md5 一字未变** [实测]: 网表 `c78f991283cc82d56c8e3dd31657c785` · "
    "板 `611b869e13518c3c023fb178f91a0075`\n"
    "★**⑤ 口径纪律**: 判定线取 ISS-124 发布值 **15.10 / 17.33 ms** (精确反解 15.095) ⇒ ★**60 ms 与 15.10 均未调松**; "
    "★**板端一切 = [0数据], 本单 0 条板端 [实测]** ★"
)

NOTE = (
    "\n★**2026-11-15 22:4x 项目总工 (main) 落 `verified` (★清僵尸 fixing 第 15 次复发·本轮第 3 条★)**:\n"
    "★**实测**: 子会话 `agent:sw-lead:subagent:b37f1504` (sessionId `067b4580`) **22:40:19 结束, status=done** "
    "⇒ ★**交卷已投递、文件已落盘** ⇒ 但 ★**brief 不许子 agent 改 issue_log ⇒ status 停在 `fixing`** ⇒ "
    "★**`advance.py` 的 in_flight 规则 ⇒ sw-lead 名额被占住** ⇒ ★**main 独立复核 (只看盘上实物 + 自己跑门禁) "
    "通过 ⇒ 本单转 `verified`** ★\n"
    "★**时序说明**: 22:4x 落 ISS-174 / ISS-209 时本单会话**仍在跑** ⇒ ★**当时显式 assert 不碰它** ⇒ "
    "★**22:40:19 交卷后本脚本单独收尾** ★\n"
    "★**边界**: 不改 §0 锁死表 · 不写别人的分片 · 不发信 · 板/网表/原理图/BOM 一个字节未动 ★\n"
)


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
        it = by_id.get(IID)
        assert it is not None, "%s 不存在" % IID
        assert it.get("status") == "fixing", "%s status=%s 非 fixing" % (IID, it.get("status"))
        assert it.get("owner") != "main", "%s owner=main 不能自验" % IID
        it["status"] = "verified"
        it["verify_by"] = "main"
        it["verify_result"] = RES
        it["verify_date"] = "2026-11-15 22:4x"
        it["fixed_at"] = "2026-11-15"
        it["fix_ref"] = FIX_REF
        it["note"] = (it.get("note") or "") + NOTE

        log["issues"] = issues
        shutil.copy2(LOG, BAK)
        atomic_write(LOG, yaml.safe_dump(log, allow_unicode=True, sort_keys=False, width=200))
        print("备份:", BAK)
        print(" - %s (%s) → verified (main 独立复核)" % (IID, it.get("owner")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
