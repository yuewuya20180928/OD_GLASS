#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-218 (mech-lead) 交卷独立复核 ⇒ 落 `verified` (清僵尸 fixing)
================================================================================
★**为什么是现在 (★main 2026-11-16 01:4x 实测★)**:
  · 子会话 mech-lead bd1e28db 已 **done** (01:01:11→01:17:09) ⇒ 交付物已落盘
    (HANDOFF/2026-11-16_mech-lead_ISS218_*.md @01:28 · PRINT_COUPON_TIER3_SPEC.md ·
     ENDPOINT_METAL_PATH_MASS_TEMPLATE.md · frame_typec_coupon_tier3_revb.stl)
  · 但 brief 不许子 agent 改 issue_log ⇒ status 停在 `fixing` ⇒ `advance.py` 的
    in_flight 规则 ⇒ 名额被占住 ⇒ A 段 0 条 ⇒ **队列断线 (第 18 次复发)**

★**main 独立复核 (自己跑门禁 + 自己 md5 + 自己读盘上实物, 不看子 agent 自报)**:
  · `python3 MECH/print/verify_pack_revb.py`           → rc=0 (尺寸判据 100% 一致 + STL 逐点互验)
  · `python3 MECH/print/verify_pack_revb.py --selftest`→ rc=0 (**反向用例 8/8 抓到** ⇒ 不是假绿)
  · `python3 MECH/print/verify_pack.py`                → rc=0 (46/46 · Rev A 基线未变红)
  · `python3 MECH/verify_budget.py`                    → rc=0 (buck 口径没被改回线性 0.8W)
  · `python3 MECH/check_demo_struct_truth.py`          → rc=0 (20/20)
  · md5 逐字节未变: 网表 c78f991283cc82d56c8e3dd31657c785 · 板 611b869e13518c3c023fb178f91a0075
    · .kicad_pro 3e504d2be83152e337949723e909be1b
  · HANDOFF B1~B6 六块齐全 (grep 实测 6 个二级标题)

★**边界**: 不改 §0 锁死表 · 不写任何子总工的分片 · 不发信 · 不碰网表/脚表/板/原理图/BOM
  · **不动 ISS-215 (sw-lead 仍在跑, 01:39 实测 status=running)** · **不动 ISS-217 (hw-lead 会话 aborted)**
    ⇒ ★那两条按「fixing 不重复派」纪律留给队列自动派活 job (fb67af40) 处理★
"""
import fcntl
import os
import shutil
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
BAK = os.path.join(HERE, "issue_log.yaml.bak_20260716_0145_verify_iss218")

IID = "ISS-218"
FIX_REF = "HANDOFF/2026-11-16_mech-lead_ISS218_打印包第三档与热路重量模板.md"

VERIFY = (
    "★main 独立复核通过 (★2026-11-16 01:4x, 只看盘上实物 + 自己跑门禁 + 自己 md5★):\n"
    "  · verify_pack_revb.py → rc=0 (尺寸判据 100% 一致 + STL 逐点互验 100% 一致)\n"
    "  · verify_pack_revb.py --selftest → rc=0 (反向用例 8/8 抓到 ⇒ 门禁不是假绿)\n"
    "  · verify_pack.py (Rev A 基线) → rc=0 (46/46 · 未变红)\n"
    "  · verify_budget.py → rc=0 (充电耗散 = buck 口径, 没被改回线性 0.8W)\n"
    "  · check_demo_struct_truth.py → rc=0 (20/20)\n"
    "  · md5 逐字节未变: 网表 c78f991283cc82d56c8e3dd31657c785 · 板 611b869e13518c3c023fb178f91a0075 "
    "· .kicad_pro 3e504d2be83152e337949723e909be1b\n"
    "  · HANDOFF B1~B6 六块齐全\n"
    "★**实物 [实测] = 0 条** (本机跨网段不可达 / 无切片器 / 无量具) ⇒ M-PRINT 仍是 0 数据, "
    "第三档只是【可下片试样 + 机器门禁】, 不是实测结论 ★\n"
    "★**三条硬结论 (main 已复核)**: ① 第三档两档最坏单边 0.63/0.62 ≥ 判据 0.60 (机器钉住) "
    "②『热路是铝的』不自动满足 R ≤ 70 K/W ⇒ 反解 A ≥ 4.98 mm² (2.0×2.0 铝条 R=87.1 ❌) "
    "③ 项目内 k=237 比 6063-T6 官方 201 乐观 18% ⇒ 方向不变, 只报不改★"
)


def atomic_write(path: str, data: str) -> None:
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_log_", suffix=".yaml")
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
        it = next((x for x in issues if x.get("id") == IID), None)
        if it is None:
            print("❌ %s 不存在 ⇒ 中止" % IID)
            return 2
        if it.get("status") != "fixing":
            print("⚠ %s status=%s (不是 fixing) ⇒ 幂等跳过, 不重复落账" % (IID, it.get("status")))
            return 0

        it["status"] = "verified"
        it["fixed_at"] = "2026-11-16"
        it["verify_date"] = "2026-11-16 01:4x"
        it["verify_result"] = VERIFY
        it["fix_ref"] = FIX_REF
        it["note"] = (it.get("note") or "") + (
            "\n★**2026-11-16 01:4x 继续执行后继计划 job (775d9893) 落 `verified` (★清僵尸 fixing·第 18 次复发★)**:\n"
            "★**实测**: mech-lead 子会话 bd1e28db **done** (01:17:09 结束) ⇒ 交付物已落盘 ⇒ "
            "★**但 brief 不许子 agent 改 issue_log ⇒ status 停在 `fixing` ⇒ `advance.py` 的 in_flight 规则 ⇒ "
            "名额被占住 ⇒ A 段 0 条 ⇒ 队列断线★**\n"
            "★**main 独立复核通过 ⇒ 落 `verified` (★不是 closed★) ⇒ 放出 mech-lead 名额★**\n"
            "★**边界**: 不改 §0 锁死表 · 不写任何子总工的分片 · 不发信 · 网表/脚表/板/原理图/BOM 一个字节未动 ★\n"
        )
        print(" - %s fixing → verified (main 独立复核通过)" % IID)

        log["issues"] = issues
        shutil.copy2(LOG, BAK)
        atomic_write(LOG, yaml.safe_dump(log, allow_unicode=True, sort_keys=False, width=200))
        print("备份:", os.path.basename(BAK))
        print("issues 总数:", len(issues))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
