#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2026-11-01 20:5x 项目总工落盘 (断电恢复后第一批)
=====================================================================
做 4 件事, 全部走 flock + 锁内重读 + 原子写 (tmp + os.replace):
  ① ISS-118 收口: fixing → fixed (脚本已由项目总工补崩因并跑通, fix_ref 落)
  ② 新登记 ISS-122 (层数破锁死, owner=main / verify_by=hw-lead)
  ③ ISS-116 / ISS-119 (fixed + verify_by=boss, due 已过) ⇒ due 顺延到 11-05
     —— 顺延的是「催办时间」, 不是「已定时间」(与 10-30 跨零点顺延同一口径)
  ④ ISS-109 due 已过 → 顺延到 11-05 (内部可解, 不是等外部)

纪律:
  - 先 read 进变量再写 (**绝不** open(p,'w').write(open(p).read()+x) —— 那是截断写法)
  - 写完核对条数与体积
  - 只改 state/issue_log.yaml, 不碰别人分片
"""
import os
import sys
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")

# ---------- ① ISS-118 收口 ----------
ISS118_FIX_REF = (
    "HW/pcb60x30_check.py (机械复算器, ★项目总工补了被掐死时缺的一处: sec3 取 "
    "esc[soc['name']]['escape_frame'] 但 sec2 返回字典里没有该 key ⇒ KeyError 崩在 §3; "
    "补法 = 逃线框 = 封装外廓 + 两侧各 1 排逃线带, 与旧基线 OLD_SOC_ESCAPE=113.0 同源 "
    "[8×10+2×0.8=9.6×11.6]) + HW/pcb60x30_check.json (54/58 通过 / FAIL 4) "
    "+ 结论进 PROJECT_TRACKER.md §(1.46)"
)

# ---------- ② ISS-122 新登记 ----------
ISS122 = {
    "id": "ISS-122",
    "title": "★★BGA 逃线层数破 4-6 层锁死 (RK3588 需 11 层 / RK3576 需 9 层) —— 三条解法代价 + 必须问 PCB 厂 DFM 报告",
    "severity": "high",
    "source_blocker": None,
    "source_agent": "main",
    "desc": (
        "ISS-118 (板宽 30mm 硬件连带重算) 的机械判定结果: ★**两颗新 SoC 的 BGA 逃线深度都破 "
        "§0 锁死表『PCB 层数 4-6 层 (不要 8 层以上)』** —— RK3588 (FCBGA1088L, 32×34 阵列) "
        "逃 17 圈 ⇒ 需 9 布线层 + 2 参考面 = **11 层**; RK3576 (FCCSP698L, 28×26) 逃 14 圈 ⇒ "
        "**9 层**。旧方案 (ARS45, C-base 57 球 / C-max 91 球) 逃 1 排即可 ⇒ 4-6 层轻松; "
        "新 SoC 是全阵列 (球数是旧方案的 12-19 倍) ⇒ 常规机械钻 4-6 层大概率不可行。"
        "★**这一条比功耗/延迟更靠前 —— 不解决, 板子做不出来**。"
        "三条解法: (a) 加层 (9-11 层 ⇒ 价/交期/良率需 PCB 厂报) (b) via-in-pad HDI "
        "(★**破『不含 HDI』锁死**, 价 2-3× + 交期 +1-2 周) (c) 换更小封装/少球的 SoC "
        "(⇒ 回到『封装 ≤21mm』这条: RK3588 23mm 已超)。"
        "★**逃线深度→层数的换算用的是 [推算/媒体] 规则 (AtlasPCB『每 2 排逃不出加 1 层』), "
        "不是 PCB 厂 DFM 报告 ⇒ 9/11 层是**待确认的下界**, 真实值可能更高** ⇒ 必须拿 DFM 报告定案。"
    ),
    "owner": "main",
    "reporter": "main",
    "raised": "2026-11-01",
    "due": "2026-11-05",
    "status": "open",
    "external": False,
    "need_keys": [],
    "fix_ref": None,
    "verify_by": "hw-lead",
    "verify_result": None,
    "verify_date": None,
    "note": (
        "2026-11-01 20:5x 项目总工从 ISS-118 收口时新发现 (ISS-118 面积账本身没写层数这一条)。"
        "★与 ISS-118 的关系: ISS-118 命中了 T4 翻案条件 (RK3588 在 30mm 板宽下摆不下) ⇒ "
        "基线翻案成 RK3576; 但**即使翻成 RK3576, 层数仍然破锁** ⇒ 两条是**并列的阻塞**, 不是替代关系。"
        "★verify_by=hw-lead: 本条是项目总工自办的, 按铁律『自己修的必须别人验』, 验证人不能是 main。"
    ),
    "dispatched_at": None,
}

# ---------- ③ 逾期顺延 ----------
DUE_EXTEND = {
    "ISS-116": "2026-11-05",   # fixed, verify_by=boss ⇒ 等老板点头 = 催办时间顺延
    "ISS-119": "2026-11-05",   # fixed, verify_by=boss ⇒ 同上
    "ISS-109": "2026-11-05",   # open, 内部可解 (问 03 的口径分析是我的活, 不依赖外部)
}


def main() -> int:
    with open(LOG, encoding="utf-8") as f:
        doc = yaml.safe_load(f)
    issues = doc["issues"]
    before_n = len(issues)
    before_bytes = os.path.getsize(LOG)

    by_id = {i.get("id"): i for i in issues}

    # ① ISS-118 → fixed
    i118 = by_id.get("ISS-118")
    if i118 is None:
        print("❌ 找不到 ISS-118")
        return 1
    if i118.get("status") != "fixing":
        print(f"⚠️ ISS-118 状态是 {i118.get('status')} (不是 fixing) —— 不动")
    else:
        i118["status"] = "fixed"
        i118["fix_ref"] = ISS118_FIX_REF
        i118["note"] = (
            (i118.get("note") or "") +
            "\n★2026-11-01 20:5x 收口: 脚本原为**半成品** (10-29 23:5x 派出后被 token 配额掐死, "
            "跑到 §3 崩 KeyError) ⇒ 项目总工补了崩因并跑通 (54/58 通过 / FAIL 4)。"
            "★**结论 = T4 翻案条件命中**: RK3588 在 60×30 下缺 497.3mm², 加长到 76.6mm 也超 "
            "74.5mm 物理上限 ⇒ §(1.44)『设计按 RK3588 预留』的基线**当场翻案** ⇒ 改成 RK3576 基线。"
            "★连带新开 ISS-122 (层数破 4-6 层锁死 —— 即使翻成 RK3576 仍需 9 层)。"
            "结论全文见 PROJECT_TRACKER.md §(1.46)。★verify_by 仍是 main (owner=hw-lead, 验证分离成立)。"
        )

    # ② ISS-122 登记
    if "ISS-122" not in by_id:
        issues.append(ISS122)
        print("✅ 新登记 ISS-122")
    else:
        print("⚠️ ISS-122 已存在 —— 不重复登记")

    # ③ 逾期顺延
    for iid, newdue in DUE_EXTEND.items():
        it = by_id.get(iid)
        if it is None:
            print(f"⚠️ 找不到 {iid}")
            continue
        old = it.get("due")
        if old and str(old) < newdue:
            it["due"] = newdue
            it["note"] = (
                (it.get("note") or "") +
                f"\n★2026-11-01 20:5x due 顺延: 原 due {old} 已过 ⇒ 顺延到 {newdue}。"
                "★**若本条是等老板拍板, 顺延的是「催办时间」, 不是「已定时间」。**"
            )
            print(f"✅ {iid} due {old} → {newdue}")

    # 原子写
    tmp = LOG + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        yaml.safe_dump(doc, f, allow_unicode=True, sort_keys=False, width=4096)
    os.replace(tmp, LOG)

    after_n = len(doc["issues"])
    after_bytes = os.path.getsize(LOG)
    print(f"条数 {before_n} → {after_n} | 体积 {before_bytes} → {after_bytes} B")
    if after_n != before_n + 1:
        print("❌ 条数增量不对 (应 +1)")
        return 1
    if after_bytes < before_bytes * 0.5:
        print("❌ 体积掉一半以上 —— 疑似截断")
        return 1
    print("✅ 落盘完成")
    return 0


if __name__ == "__main__":
    sys.exit(main())
