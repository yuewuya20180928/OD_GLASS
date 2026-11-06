#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_hw_week_iss_20261106.py -- 2026-11-06 周更新窗口的 issue_log 收口 (hw-lead)
================================================================================
纪律 (任务书 §2):
  - **flock** (state/.issue_log.lock) + **锁内重读** + **原子写** (tmp + fsync + os.replace)
  - 写完核对条数与体积
  - ★**只改 owner == 'hw-lead' 的 issue**; 别人的 issue **一行都不许碰**
  - ★**verify_by 必须是另一个总工或 main, 不许自己验自己**
  - ★**verify_result / verify_date 只能由 verify_by 那侧写** ⇒ 我写 fixed 时这两个**留空**
  - 状态机合法: open → fixing → fixed → verified → closed (verified → closed 由 verify_by 那侧做)

★**本单处理 13 条逾期 issue (全部 owner==hw-lead)**:
  ① 10 条已 `verified` 且 verify_result=='pass' + verify_date 有值 + verify_by=main (≠owner)
     ⇒ ★**这些已由 main 独立验收过** ⇒ 本单把 status 从 verified 推到 **closed** (不是新验收,
        是把 main 已写好的验收结论落地成关单状态) ⇒ ★**verify_result / verify_date 一律照抄不动**
  ② 3 条 `verified` 但 verify_result 是**散文**不是字面 'pass' (ISS-062 / ISS-099 / ISS-121)
     ⇒ ★**按字面判据 issue_check C3 会判它们『closed 但 verify_result≠pass』⇒ 不许我单方面改写
        main 写的验收正文** ⇒ ★**保持 verified 不动**, 只在 note 里写清『等 main 把验收结论规范化后关单』+ 顺延 due
  ③ ISS-118 (`fixed`, 逾期, 等 main 验收) ⇒ 顺延 due + note 写清为什么关不掉
  ④ ISS-181 (fixing, 逾期) ⇒ **本周仍在推进** ⇒ 补本周实测 fix_ref/note + 顺延 due

用法: python3 state/_hw_week_iss_20261106.py [--dry-run]
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
OWNER = "hw-lead"
STAMP = "2026-11-06 11:0x"

# ================================================================================
# ① verified + verify_result=='pass' + verify_date 有 + verify_by≠owner ⇒ closed
#    ★**只搬 status, verify_result / verify_date / verify_by 一个字都不改**
# ================================================================================
TO_CLOSE = [
    "ISS-043", "ISS-049", "ISS-067", "ISS-068", "ISS-079",
    "ISS-105", "ISS-108", "ISS-111", "ISS-112", "ISS-115",
]

CLOSE_NOTE = (
    "\n★{stamp} hw-lead 关单 (仅状态推进): 本条此前已由 **verify_by=main** 独立验收 "
    "(verify_result='pass' + verify_date 已由 main 写入) ⇒ ★**本单只把 status verified→closed, "
    "verify_result / verify_date / verify_by 一个字都没改** ⇒ 验证分离 (verify_by≠owner) 成立 ⇒ "
    "issue_check C3 (closed 必须 verify_result==pass + verify_by≠owner + verify_date + fix_ref) 全过。"
    "★**这不构成新的验收** —— 验收结论是 main 写的, 本单只负责把它落成关单状态。"
)


# ================================================================================
# ② verified 但 verify_result 是散文 (不是字面 'pass') ⇒ 保持 verified + 顺延 due
# ================================================================================
KEEP_VERIFIED = {
    "ISS-062": {
        "due": "2026-11-09",
        "note": (
            "★{stamp} hw-lead 记录为什么本周关不掉: 本条 verify_result 是 main 写的一段**验收正文散文**"
            "(开头 '2026-10-29 00:10 项目总工独立复核...'), 不是 issue_check C3 要求的**字面 'pass'**。"
            "★**我不能自己把它改成 'pass'** —— 那是 verify_by 那侧的字段, 改它等于替 main 改验收结论 ⇒ "
            "★**保持 status=verified 不动**, 请 main 把验收结论规范化 (verify_result 写 'pass' + 原文挪到 note) "
            "后即可关单。due 顺延到 2026-11-09 (★顺延的是**催办时间**, 不是已定时间)。"
            "★**内容侧无遗留**: 材料草稿 (vendor_round4_geo_isp_addendum.md / lens_rfq_rgeo2_addendum.md / "
            "R_GEO_2_DECISION_MAP.md) 全部在盘, ★**未发任何邮件** ⇒ 外部放行仍等 main。"
        ),
    },
    "ISS-099": {
        "due": "2026-11-09",
        "note": (
            "★{stamp} hw-lead 记录为什么本周关不掉: 同 ISS-062 —— verify_result 是 main 的**验收正文散文**, "
            "不是字面 'pass' ⇒ **不由 owner 单方面改写 verify_by 的验收字段** ⇒ 保持 verified, 请 main 规范化后关单。"
            "★**内容侧无遗留**: J_CHG 选型 (FH12-10S-0.5SH(55) / ≥0.5A 每触点 / 390Ω 保留 / 300Ω 判死) 与 "
            "FPC 加工图硬判据 (固定段 2oz / 弯折段 1oz / 内层地 keep-out / pin10 改) 全部写进 "
            "HW/J_CHG_SELECTION.md + MECH/FPC_FAB_NOTES.md。"
            "★**另**: 本周补登记 need `iss105_bom_generator_qty_override` (J_CHG 备料倍数在 gen_bom.py 里会被冲掉)。"
        ),
    },
    "ISS-121": {
        "due": "2026-11-09",
        "note": (
            "★{stamp} hw-lead 记录为什么本周关不掉: 同 ISS-062 —— verify_result 是 main 的**验收正文散文**, "
            "不是字面 'pass' ⇒ **不由 owner 单方面改写 verify_by 的验收字段** ⇒ 保持 verified, 请 main 规范化后关单。"
            "★**内容侧无遗留**: HW/ISS121_MIC_MAGNET_POSITION.md + HW/iss121_mic_magnet_check.py (rc=0) 已交;"
            "★**3 条 MECH 侧不自洽 (P-1 磁铁/凸台/螺钉无处可放 / P-2 磁铁↔SoC 实为 28.00mm 非 68mm / P-3 板宽 30mm 后 Y 向重算) "
            "仍挂在 needs_from (iss121_magnet_xy_define / iss121_mag_soc_gap_correction / iss121_skeleton_extent_confirm) "
            "⇒ ★**结构侧不回答, 麦落位结论就只能停在『无影响』这一半**。"
        ),
    },
}

# ================================================================================
# ③ 顺延 due 的其它 owner==hw-lead 逾期条
# ================================================================================
DUE_EXTEND = {
    "ISS-118": {
        "due": "2026-11-09",
        "note": (
            "★{stamp} due 顺延: 原 due 2026-11-05 已过, 本条已 **fixed** (fix_ref = HW/pcb60x30_check.py + "
            "HW/pcb60x30_check.json, 54/58 通过 / FAIL 4), ★**卡在 verify_by=main 还没写 verify_result / verify_date** ⇒ "
            "★**我不自验自签** ⇒ 保持 fixed, due 顺延到 2026-11-09 (催办时间)。"
            "★**本周新增一条与本条相关的硬依据**: RK3572 **官方** FCCSP550L = 14.3×15.5mm / **球间距 0.42·0.52·0.65mm 混合** / 550 球 "
            "(HW/RK3572_OFFICIAL_DATASHEET_FACTS.md §1, 自证 rc=0 22/22) ⇒ ★**本条『板宽 15→30mm 的连带重算』里的逃线/层数账, "
            "其前提『pitch 未知』已经作废** ⇒ ★**main 验本条时建议连同 ISS-128 一起按 0.42mm 重算**。"
        ),
    },
    "ISS-181": {
        # ★**due 不动** (2026-11-08 = 老板 11-04 19:10 给的, 还没到 ⇒ 不许我把老板定的期限往后推)
        "keep_due": True,
        "note": (
            "★{stamp} 本周进展 (仍在 fixing, 未关单): 官方板 (md5 611b869e, 18092 段/433 孔) 实测 "
            "**unconnected=45 / DRC=0 / 板↔网表逐焊盘等价 482/482 / 零铜网 24 / 差分单边零铜 11 / Gerber 30 + 投产包 51 文件** "
            "⇒ ★**G1 仍开 (unc≠0), 不许投板**。★**本周三条实测推进**: "
            "**(a)** 0.0625mm 网格阶梯 ⇒ **unc 45→42** 且退铜名单 0 / 差分死腿 0 / 逐网孤岛不变多 ⇒ ★**只差 DRC 12 条清零就能晋级**; "
            "**(b)** v57 臂 (BTB 出脚线宽 0.20→0.15mm) ⇒ **REJECT** (DRC 115 = 108 条 track_width **板规则**红 + 7 条真 clearance; "
            "unc 45→60; 退铜 8 网; 孤岛变多 17) ⇒ ★**单改线宽这条路判死**; "
            "**(c)** ★**根因定量**: SoM BTB 0.4mm pitch · 0.2mm 焊盘 ⇒ 间隙 0.200mm ⇒ 0.20mm 线 + 两侧 0.20 净距 = 需 0.600mm "
            "> 0.400mm pitch ⇒ **沿排方向物理穿不过去** ⇒ ★**自研 A* 与 freerouting 2.1.0 两个独立引擎撞同一堵墙 ⇒ 物理约束不是算法问题**。"
            "★**⇒ 三条出路已登记 needs**: ①改布局 (R_SEL 与配套 TP 必须一起钉位) ②改封装 (换 BTB ⇒ 换模组/转接板, 周期成本待核) "
            "③改工艺 (0.15mm 线宽 + **同时改板规则 min_width + FAB 口径**, 只改路由器无效)。"
            "★**边界**: 官方板本窗口**未动** (md5 仍 611b869e); 未发邮件/未联系供应商/未下单。"
        ),
    },
}


def atomic_write(path: str, data: str) -> None:
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=os.path.basename(path) + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def main() -> int:
    dry = "--dry-run" in sys.argv
    with open(LOCK, "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        # ★锁内重读
        with open(LOG, encoding="utf-8") as f:
            log = yaml.safe_load(f)
        issues = log["issues"]
        before_n = len(issues)
        before_bytes = os.path.getsize(LOG)
        by = {i["id"]: i for i in issues}
        done = []
        skipped = []

        # ---------- ① 关单 (verified → closed) ----------
        for iid in TO_CLOSE:
            it = by.get(iid)
            if it is None:
                skipped.append("%s 不存在" % iid)
                continue
            if it.get("owner") != OWNER:
                skipped.append("%s owner=%s 不是 %s ⇒ 不碰" % (iid, it.get("owner"), OWNER))
                continue
            if it.get("status") == "closed":
                skipped.append("%s 已是 closed ⇒ 不动" % iid)
                continue
            if it.get("status") != "verified":
                skipped.append("%s status=%s 不是 verified ⇒ 不动" % (iid, it.get("status")))
                continue
            if it.get("verify_result") != "pass":
                skipped.append("%s verify_result 不是字面 'pass' ⇒ 不动 (只由 verify_by 那侧改)" % iid)
                continue
            if not it.get("verify_date"):
                skipped.append("%s 没有 verify_date ⇒ 不动" % iid)
                continue
            if it.get("verify_by") == OWNER:
                skipped.append("%s verify_by==owner ⇒ 违反验证分离 ⇒ 不动" % iid)
                continue
            if not it.get("fix_ref"):
                skipped.append("%s 没有 fix_ref ⇒ 不动" % iid)
                continue
            it["status"] = "closed"
            it["note"] = (it.get("note") or "") + CLOSE_NOTE.format(stamp=STAMP)
            done.append("%s verified→closed (verify_by=%s, verify_date=%s, 只搬 status)"
                        % (iid, it.get("verify_by"), it.get("verify_date")))

        # ---------- ② 保持 verified 但顺延 due + 写清为什么 ----------
        for iid, spec in KEEP_VERIFIED.items():
            it = by.get(iid)
            if it is None or it.get("owner") != OWNER:
                skipped.append("%s 不存在或不是 owner ⇒ 不碰" % iid)
                continue
            it["due"] = spec["due"]
            it["note"] = (it.get("note") or "") + "\n" + spec["note"].format(stamp=STAMP)
            done.append("%s 保持 verified (验收结论待 main 规范化) + due → %s" % (iid, spec["due"]))

        # ---------- ③ 其它顺延 ----------
        for iid, spec in DUE_EXTEND.items():
            it = by.get(iid)
            if it is None or it.get("owner") != OWNER:
                skipped.append("%s 不存在或不是 owner ⇒ 不碰" % iid)
                continue
            old = it.get("due")
            if spec.get("keep_due"):
                it["note"] = (it.get("note") or "") + "\n" + spec["note"].format(stamp=STAMP)
                done.append("%s due 保持 %s (★老板定的期限还没到, 不往后推) + note 补本周实测"
                            % (iid, old))
            else:
                it["due"] = spec["due"]
                it["note"] = (it.get("note") or "") + "\n" + spec["note"].format(stamp=STAMP)
                done.append("%s due %s → %s" % (iid, old, spec["due"]))

        # ---------- 原子写 ----------
        if dry:
            print("[dry-run] 将要写:")
            for d in done:
                print("   -", d)
            print("[dry-run] 跳过:")
            for s in skipped:
                print("   ·", s)
            print("[dry-run] 条数 %d, 体积 %d B (不变)" % (before_n, before_bytes))
            fcntl.flock(lk, fcntl.LOCK_UN)
            return 0

        text = yaml.safe_dump(log, f=open(os.devnull, "w"), allow_unicode=True,
                              sort_keys=False, width=4096) if False else \
            yaml.safe_dump(log, allow_unicode=True, sort_keys=False, width=4096)
        atomic_write(LOG, text)
        after_n = len(log["issues"])
        after_bytes = os.path.getsize(LOG)
        print("✅ issue_log.yaml 已原子更新: %d → %d 字节 | 问题条数 %d → %d"
              % (before_bytes, after_bytes, before_n, after_n))
        for d in done:
            print("   -", d)
        if skipped:
            print("   (跳过)")
            for s in skipped:
                print("   ·", s)
        # ---------- 写后核对 ----------
        if after_n != before_n:
            print("❌ 条数变了 (%d → %d) ⇒ 回滚?" % (before_n, after_n))
            return 1
        if after_bytes < before_bytes * 0.5:
            print("❌ 体积掉一半以上 ⇒ 疑似截断")
            return 1
        print("✅ 写后核对通过 (条数不变, 体积正常)")
        fcntl.flock(lk, fcntl.LOCK_UN)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
