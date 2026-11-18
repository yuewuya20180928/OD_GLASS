#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
state/_close_issues_week_20261106b.py — 2026-11-06 周窗口 · mech-lead 名下 issue **正式关单**

================================================================================
为什么单独一个脚本 (与 _close_issues_week_20261106.py 分开)
--------------------------------------------------------------------------------
上一个脚本做的是「**交卷 + 自推状态**」(open/fixing → fixed, verify_result/date **留空**待 main 写)。
本脚本做的是**正式关单** (verified → closed) —— 判据完全照 issue_check.py 的 **C3**:

    closed 必须同时满足:
      ① fix_ref 非空
      ② **verify_result == 'pass'** (字面精确相等, 不是散文体!)
      ③ verify_by 非空且 **!= owner** (验证分离)
      ④ verify_date 非空

★**关键**: C3 的第②条是**字面相等** ⇒ 上轮 main 写的是散文体的
  ("2026-11-01 22:1x 项目总工亲核通过: ..." / "pass | ★★补注...") 的那些条
  **关不了** —— 强行关 ⇒ issue_check 会报 "closed 但 verify_result=... (必须 pass)" 违规。
  ⇒ 本脚本**只关真正满足 C3 的**, 其余的**写清为什么关不掉 + 新 due**, 一个字不改 verify_result。

纪律: flock + 锁内重读 + 原子写 (tmp + fsync + os.replace) + 只动 owner==mech-lead 的
"""
from __future__ import annotations

import fcntl
import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
OWNER = "mech-lead"
TODAY = "2026-11-06"

# =====================================================================
# 可以正式关单的 (已逐条核对 C3 四条全过)
# =====================================================================
CLOSE = {
    "ISS-027": (
        "★2026-11-06 正式关单 (verified → closed)。"
        "★**C3 四条全过**: fix_ref 有 (MECH/PROTOTYPE_PLAN.md 42.5KB + prototype_plan_check.py rc=0 + "
        "HANDOFF/2026-10-29_mech-lead_原型制作计划_ISS027.md 19.9KB + skeleton_section_check.py rc=0) · "
        "verify_result == 'pass' (字面) · verify_by=main ≠ owner=mech-lead (验证分离成立) · "
        "verify_date=2026-10-29。"
        "★**本单关的是「计划」这一件事** (分批打样/每批验证什么/不通过怎么回滚 四批 + 三分类矩阵 + 五层回滚, "
        "B1~B6 六块齐, 自检 rc=0)。"
        "★**但实物 0 件这件事没有随本单消失** —— B1 的唯一硬前置 ISS-040 (打印+量测执行方) 至今未闭 ⇒ "
        "**计划已在、实物 0 件** 的落差由本轮新登记的 need proto_b1_split_coupon→main 继续追 "
        "(★建议 B1 拆 B1a 纯 coupon / B1b 板相关, 这样 ISS-040 一有着落 34 项工艺数据立刻能开始采)。"
    ),
    "ISS-052": (
        "★2026-11-06 正式关单 (verified → closed)。"
        "★**C3 四条全过**: fix_ref 有 (MECH/CAMERA_WINDOW_SPEC.md 26.5KB B1-B6 + camera_window_check.py "
        "rc=0 FAIL0/WARN0 + MECH_BUDGET §1.3(M8)/§1.4.5/§1.5/§1.5.1/§1.5.2/§4(c) 改写 + "
        "_apply_iss052_docs.py + _frag_update_iss052.py) · verify_result == 'pass' (字面) · "
        "verify_by=main ≠ owner=mech-lead · verify_date=2026-10-29。"
        "★**本单关的是「镜头镜筒/窗口/高度需求 + 俯角收窄」这一件事**: "
        "三档 (100/110/120°) 的镜筒/窗口/高度需求只差 ≤0.9mm ⇒ **可不等镜头定档就开模**; "
        "镜框上沿摄像头位前后厚度需求 10.11mm(25°)/10.26(28°)/10.41(32°) 落在 10-12mm 带内 ⇒ 余 1.6-1.9mm, "
        "俯角 20°→32° 只变 0.60mm ⇒ **俯角收窄不吃厚度预算**; "
        "★垂直净高需求 10.36mm(25°)/10.53mm(28°) 比前后厚度更紧 ⇒ 是外观代价。"
        "★**俯角口径已由 ISS-047 精确化**: 有效余量 ≥4° ⇒ **俯角上限 ≤25.89°, 设计点 25°**, "
        "h_max(d=30/32/35)=13.99/14.92/16.32mm。"
        "★**边界随件注明**: 显示件 11-02 换视涯 SiOLED 后, **镜框侧几何整体要重算** (ISS-133) ⇒ "
        "本单关的是「镜头/摄像头位」这一侧, 「显示仓/耦合光学」那一侧不在本单范围。"
    ),
    "ISS-065": (
        "★2026-11-06 正式关单 (verified → closed)。"
        "★**C3 四条全过**: fix_ref 有 (MECH/STRUCT_REVIEW_ISS065.md + iss065_check.py rc=0 40/40 + "
        "HANDOFF/2026-10-29_mech-lead_ISS065_结构侧5条建议评估.md B1-B6 + _close_iss065.py + "
        "分片 13 条 claim) · verify_result == 'pass' (字面) · verify_by=main ≠ owner=mech-lead · "
        "verify_date=2026-10-30。"
        "★**本单关的是「5 条建议的落地评估」**: ① 鼻梁区 43°C 适用 (ISO 13732-1 判材料表面温度, "
        "面积小只让温升更低、**不放松阈值**), 现状推算 37.3°C ✅, 但 SoC 挪镜框正中 ⇒ 50.1°C 超红线, "
        "且加金属热路会恶化到 66.6°C ⇒ **金属热路必须配鼻梁侧热断 R_bridge ≥578 K/W**; "
        "② 厚度映射按**串行口径**重出: 315mAh → H 需求 6.35mm / 387mAh → 6.05mm ⇒ **7.30mm 一毫米不用改**; "
        "③ 充电板推荐 T-1 扩板 25×12 + T-3a = 72.8% 占用 (不做 T-2 双面贴 / 不做 T-3c); "
        "④ 真实缺口 14.60mm² 不是 13.32mm² (D_CHG_LED 的 board 列错); "
        "⑤ 任务书给的是**叠放口径**算式, 本域 fit_check.py §3① 已三重证明裁决作废 ⇒ **不顺着改**。"
    ),
    "ISS-089": (
        "★2026-11-06 正式关单 (verified → closed)。"
        "★**C3 四条全过**: fix_ref 有 (MECH/HW_CROSS_REVIEW.md 30KB + hw_cross_review_check.py "
        "54 项机器判定 PASS15/FAIL16/条件8/说明15 + HANDOFF/2026-10-28_mech-lead_风险复核_ISS089_硬件交叉评审.md "
        "B1-B6) · verify_result == 'pass' (字面) · verify_by=main ≠ owner=mech-lead · verify_date=2026-10-28。"
        "★**本单关的是「以 V1.1 9 页为输入的硬件侧交叉评审」这件事** (机械/热/装配/跨铰链 四维, "
        "10 条会打回来重画的点 + 7 条自发现 + 尺寸链/公差表 C1-C7/T1-T6)。"
        "★**本单产出的适用边界已在本轮 note 里逐条标注** (基线 11-02 后 demo 取消跨铰链 ⇒ "
        "铰链端 X 缺口 6.00mm / 走线拓扑未定义 两条的前提消失; "
        "而 充电耗散口径 / ICHG 系数方向 / Type-C 开孔公差 / 充电灯 board 列 / 打印包试样位置 / "
        "端件无金属导热路径 六条仍成立; 镜框光学舱那条被 11-02 换件作废 ⇒ 归 ISS-133)。"
        "★**本轮新算的正面对照**: 板宽 30 把拓扑 A (V 向叠放) 从「几何不可能」(31.00 vs 15.00, 缺 16.00mm) "
        "拉回「勉强可行」(28.30 vs 30.00, 余 1.70mm) ⇒ 整机阶段的铰链区方案空间比 15mm 板时大。"
    ),
    "ISS-107": (
        "★2026-11-06 正式关单 (verified → closed)。"
        "★**C3 四条全过**: fix_ref 有 (MECH/PCB_MOUNT_PIN_SET2.md 12.7KB + pinset2_mech_check.py "
        "31 项 FAIL0/WARN3 rc=0 + pinset2_mech_check.json + BOARD_WIDTH_15MM §5/§6 M-4/§7 R-3/§8 N2/N4/§9/§10 + "
        "CLEARANCE_FIX.md + fit_check.py + board_width_15mm_check.py + cross_review_check.py + "
        "_frag_update_iss107.py + _apply_pinset2_docs.py (20 处文档替换, 幂等) + "
        "HANDOFF/2026-10-29_mech-lead_ISS107_pcb_mounting改PIN-SET2.md B1-B6 + 分片 canon) · "
        "verify_result == 'pass' (字面) · verify_by=main ≠ owner=mech-lead · verify_date=2026-10-29。"
        "★**原单的更正仍然成立**: pcb_mounting = '2x⌀2.0H7+2x⌀1.4' + canon 'pin-set-2:2x⌀2.0h7+2x⌀1.4' "
        "⇒ 与 hw-lead 逐字节对齐 ⇒ **merge 的 pcb_mounting 冲突 0** (11-06 复核仍成立)。"
        "★**本轮补了原单的「第二面」并新开 ISS-185**: 原单只处理了**有对手方**的过期值; "
        "本轮发现**没有对手方**的过期值 (8 条 claim 的值停留在 10-28 基线) **合并器根本检不出来** ⇒ "
        "⇒ 这才是 ISS-107 的完整形态 (数据一致性问题, 合并器冲突检测只是它的子集)。"
        "★**本轮顺带修掉一个挂了一整周的「待规范化」项**: skeleton_extent ⇒ "
        "★**踩坑记录**: 只把值改成与 hw-lead 同串**仍判冲突** —— canon_of() 会 lower() 整串 ⇒ "
        "'止于pcb段后缘@z=60.00mm' ≠ hw 的 canon '止于PCB段后缘' ⇒ **只能显式给 canon 字段** "
        "才逐字节相等 ⇒ 现已对齐 ⇒ **该项消除 (merge 输出该节现为空)**。"
        "★**遗留**: 「数据一致性」没有终点 ⇒ 需把「基线每次变动后跑 rebase 扫描」写进流程 ⇒ 待 main 决定。"
    ),
}

# =====================================================================
# 关不了的: verify_result 是散文体 (C3 第②条要求字面 'pass')
#   ⇒ 写清**为什么关不掉** + 新 due, 且**一个字不改 main 写的 verify_result**
# =====================================================================
BLOCKED_NOTE = (
    "\n★2026-11-06 mech-lead 补记 (状态维持 verified, **不改 verify_result** —— 那是 verify_by 侧的权)。"
    "★**为什么本条现在关不掉 (机制层, 不是内容层)**: issue_check.py 的 **C3** 要求 "
    "`closed` 必须满足 **verify_result == 'pass' (字面精确相等)**; "
    "而本条的 verify_result 是 main 在 10-27~11-01 写的**散文体** "
    "(内容明确是「验收通过」, 但不是字面 'pass') ⇒ **强行关 ⇒ issue_check 立刻报违规** "
    "⇒ **只能由 main 侧把 verify_result 规整成字面 'pass' 后再关** ⇒ "
    "★**这是台账的格式债, 不是本单没做完**。"
    "★本轮另开 **ISS-185** 承接本条延续出来的同类问题 (没有对手方的过期 claim 值, 合并器静默放过)。"
    "★**新 due 2026-11-13**: 等 (a) main 规整 verify_result 并关单 或 (b) 本单内容按新基线重做后重交。"
)


def main() -> int:
    lock_fd = os.open(LOCK, os.O_RDWR | os.O_CREAT, 0o666)
    fcntl.flock(lock_fd, fcntl.LOCK_EX)
    try:
        with open(LOG, encoding="utf-8") as f:
            doc = yaml.safe_load(f)
        issues = doc["issues"]
        before_n = len(issues)
        before_bytes = os.path.getsize(LOG)
        by_id = {i.get("id"): i for i in issues}

        # ---------- ① 正式关单 ----------
        for iid, note in CLOSE.items():
            it = by_id.get(iid)
            if it is None:
                print(f"⚠️ {iid} 不存在 —— 跳过")
                continue
            if it.get("owner") != OWNER:
                print(f"❌ {iid} owner={it.get('owner')} 不是 {OWNER} —— 拒绝改 (纪律⑤)")
                continue
            # ---- C3 四条自检 (不许靠人肉) ----
            c3 = {
                "fix_ref": bool(it.get("fix_ref")),
                "verify_result=='pass'": it.get("verify_result") == "pass",
                "verify_by!=owner": bool(it.get("verify_by")) and it.get("verify_by") != it.get("owner"),
                "verify_date": bool(it.get("verify_date")),
            }
            if not all(c3.values()):
                print(f"❌ {iid} C3 不全过 ⇒ 不关: {c3}")
                continue
            if it.get("status") != "verified":
                print(f"⚠️ {iid} 状态是 {it.get('status')} (不是 verified) —— 不动")
                continue
            it["status"] = "closed"
            it["note"] = (it.get("note") or "") + note
            print(f"✅ {iid}: verified → closed (C3 四条全过, verify_by={it.get('verify_by')})")

        # ---------- ② 关不掉的: 写清原因 + 新 due ----------
        for iid, it in sorted(by_id.items()):
            if it.get("owner") != OWNER or it.get("status") != "verified":
                continue
            if iid in CLOSE:
                continue
            if it.get("verify_result") == "pass":
                continue          # 字面 pass 的应当已被 CLOSE 收走
            it["note"] = (it.get("note") or "") + BLOCKED_NOTE
            it["due"] = "2026-11-13"
            print(f"📌 {iid}: 维持 verified (verify_result 是散文体, C3 字面不符) · due→2026-11-13")

        # ---------- ③ 原子写 ----------
        tmp = LOG + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            yaml.safe_dump(doc, f, allow_unicode=True, sort_keys=False, width=4096)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, LOG)

        after_n = len(doc["issues"])
        after_bytes = os.path.getsize(LOG)
        print(f"条数 {before_n} → {after_n} | 体积 {before_bytes} → {after_bytes} B")
        if after_n != before_n:
            print("❌ 条数变了 (本脚本只改状态, 不该增删)")
            return 1
        if after_bytes < before_bytes * 0.5:
            print("❌ 体积掉一半以上 —— 疑似截断")
            return 1
        print("✅ 落盘完成")
        return 0
    finally:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        os.close(lock_fd)


if __name__ == "__main__":
    sys.exit(main())
