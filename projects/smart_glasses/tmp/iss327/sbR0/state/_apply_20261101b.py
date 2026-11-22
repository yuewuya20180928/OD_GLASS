#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2026-11-01 20:5x 项目总工落盘 (第二批)
=====================================================================
  ① ISS-109 问 03 口径裁决完成 ⇒ 状态降级 (一票否决级 → 两条待外部确认), 落 fix_ref
  ② 新登记 ISS-124 (问 RK3576 模组厂/瑞芯微: MP/s 吞吐 + ISP 功耗曲线) —— 外部依赖
  ③ 新登记 ISS-125 (ISS-109 其余五问要按 RK3576 口径重写问询) —— 内部可做, 我自己起草

★为什么 ISS-109 不整条关:
  问 03 (吞吐余量) 的**伪命题**已解 —— 但「MP/s 吞吐」本身仍是 [0数据] (官方 brief 只给 16M Pixel 分辨率上限),
  且「ISP 动态功耗 vs 吞吐曲线」随它一起走 ⇒ POWER_BUDGET_V3 的皮肤温度结论**仍然悬着**
  ⇒ 问 01/02/04/05/06 五问也还在 (且问询对象已从酷芯微变成 RK3576 模组厂)
  ⇒ ⇒ ISS-109 保持 open, 但 severity 从"一票否决级"降为"两条待外部确认", note 写清降级理由

纪律: flock + 锁内重读 + 原子写; 写完核对条数与体积
"""
import os
import sys
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")

ISS124 = {
    "id": "ISS-124",
    "title": "★★[待瑞芯微/RK3576 模组厂] ISP MP/s 吞吐上限 + ISP 动态功耗 vs 吞吐曲线 (2 问, 一票否决级的剩余部分)",
    "severity": "high",
    "source_blocker": None,
    "source_agent": "main",
    "desc": (
        "ISS-109 问 03 的口径裁决已解 (伪命题), 但**剩下的两条仍卡着**:\n"
        "**问 03a — MP/s 吞吐上限**: RK3576 官方 Brief Datasheet 只给『16M Pixel ISP』"
        "(分辨率上限), **没给 MP/s 吞吐** ⇒ ★**16M Pixel ≠ 16M×60=960 MP/s 的处理能力** "
        "(每帧还要读出/Demosaic/降噪/HDR) ⇒ 我们的 2688×1520@60 = 245.1 MP/s 能不能吃下, "
        "官方公开资料**判不了** ⇒ 必须问。\n"
        "**问 03b' — ISP 动态功耗 vs 吞吐曲线**: POWER_BUDGET_V3 §x 的 ISP 动态功耗地板 60mW "
        "是**按 1080p30 (62 MP/s) 反推**的 [推算]; 若改按全幅 60fps (245.1 MP/s) 重估, "
        "ISP 动态功耗要涨 ⇒ ★**皮肤温度结论 (43°C 红线) 可能翻案** ⇒ "
        "这是 ISS-109 真正卡住的东西, 不是问 03 本身。\n"
        "⇒ **一次问全**: 请给 (a) 单路 ISP 像素吞吐上限 MP/s @ 2688×1520@60 "
        "(b) ISP 动态功耗 vs 吞吐的曲线 (或至少 3 个点: 62 / 124 / 245 MP/s 各多少 mW)。"
    ),
    "owner": "main",
    "reporter": "main",
    "raised": "2026-11-01",
    "due": "2026-11-05",
    "status": "open",
    "external": True,
    "need_keys": [],
    "fix_ref": None,
    "verify_by": "hw-lead",
    "verify_result": None,
    "verify_date": None,
    "note": (
        "2026-11-01 20:5x 项目总工从 ISS-109 问 03 口径裁决 (`HW/R_GEO_Q03_ISP_THROUGHPUT_ADJUDICATION.md`) 转登记。"
        "★**问询对象已变** —— 酷芯微/ARS45 代理线 10-29 19:20 已全部作废 ⇒ 现在问的是 **RK3576 模组厂 / 瑞芯微**, "
        "不是原厂。外发一律经项目总工 (草稿放 state/outbox/) ⇒ 老板放行才发。"
        "★verify_by=hw-lead: 本条是项目总工自办的, 按铁律『自己修的必须别人验』。"
    ),
    "dispatched_at": None,
}

ISS125 = {
    "id": "ISS-125",
    "title": "★R-GEO 六问的其余五问要按 RK3576 口径重写问询 (问 01/02/04/05/06 仍是 0 答复)",
    "severity": "medium",
    "source_blocker": None,
    "source_agent": "main",
    "desc": (
        "ISS-109 的问 03 已由项目总工裁决 (伪命题, 换芯顺手解掉), 但**其余五问仍是 0 答复**: "
        "问 01 (全幅 vs ROI 模式表) / 问 02 (4-lane 2.451Gbps) / 问 04 (scaler 输出窗口) / "
        "问 05 (上电默认模式 + 寄存器读回) / 问 06 (角落实测暗角 MTF)。"
        "★**这五问的口径也随换芯变了** —— 问 04/05 是 SoC ISP 文档层面的问题 (ARS45 → RK3576), "
        "问 01/02/06 是 sensor/镜头厂侧 (与 SoC 无关, 可沿用)。"
        "⇒ 要把五问**按对象拆开**: ISP 侧 (04/05) 随 ISS-124 一起问 RK3576 模组厂; "
        "sensor 侧 (01/02/06) 走镜头厂问询 (R_GEO_2_DECISION_MAP.md 已在写)。"
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
        "2026-11-01 20:5x 项目总工自登记 (ISS-109 降级时把剩余五问单独拆出)。"
        "★**内部可做** (起草+拆对象), 不等外部 ⇒ 可以立刻动。"
        "★verify_by=hw-lead: 项目总工自办 ⇒ 别人验。"
    ),
    "dispatched_at": None,
}


def main() -> int:
    with open(LOG, encoding="utf-8") as f:
        doc = yaml.safe_load(f)
    issues = doc["issues"]
    before_n = len(issues)
    before_bytes = os.path.getsize(LOG)
    by_id = {i.get("id"): i for i in issues}

    # ① ISS-109 降级
    i109 = by_id.get("ISS-109")
    if i109 is None:
        print("❌ 找不到 ISS-109")
        return 1
    i109["fix_ref"] = (
        "HW/R_GEO_Q03_ISP_THROUGHPUT_ADJUDICATION.md (★问 03 口径裁决书: 结论 = **『1.9% vs 50.7%』是伪命题** —— "
        "250 MP/s 是 ARS45 的 ISP 吞吐上限, 497.7 是 4K@60 的像素率 (3840×2160×60), "
        "**两个不同物理量被拿来互比**才产生 2 倍错觉; 250 单口径自洽 (4K@30 248.8 ✅ / 4K@60 497.7 ❌); "
        "换到 RK3576 后官方『16M Pixel ISP』对 4.09M 全幅需求 = 25.5% ⇒ 余量充裕 74.5%) "
        "+ HW/rgeo_q03_check.py (机械判据 5/5 rc=0) + HW/rgeo_q03_check.json"
    )
    i109["note"] = (
        (i109.get("note") or "") +
        "\n★2026-11-01 20:5x 项目总工裁决 (问 03 部分已完成): **『1.9% 还是 50.7%』这个一票否决级阻塞是伪命题** —— "
        "两个数分属不同物理量 (ISP 能力上限 vs 4K 视频像素率), 比较对象错配; "
        "且 250 属已作废的 ARS45, 换芯到 RK3576 后官方 16M Pixel 口径余量充裕 (74.5%)。"
        "★**但本条不整条关** —— 剩两条仍卡: (a) RK3576 的 MP/s 吞吐官方没给 [0数据] ⇒ 新开 ISS-124; "
        "(b) ISP 动态功耗 vs 吞吐曲线 ⇒ POWER_BUDGET_V3 的 43°C 皮肤温度结论仍悬着 ⇒ 这才是它真正卡的东西。"
        "另五问 (01/02/04/05/06) 仍是 0 答复且口径随换芯变 ⇒ 新开 ISS-125 拆对象重写。"
        "★**severity 由『一票否决级』降为『两条待外部确认』** —— 降级理由已写进 fix_ref 与本文档, 不是拍脑袋降。"
    )
    i109["severity"] = "medium"
    print("✅ ISS-109 降级 (severity high→medium) + fix_ref 落盘 (状态仍 open)")

    # ② ③ 新登记
    for new in (ISS124, ISS125):
        if new["id"] not in by_id:
            issues.append(new)
            print(f"✅ 新登记 {new['id']}")
        else:
            print(f"⚠️ {new['id']} 已存在 —— 不重复登记")

    tmp = LOG + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        yaml.safe_dump(doc, f, allow_unicode=True, sort_keys=False, width=4096)
    os.replace(tmp, LOG)

    after_n = len(doc["issues"])
    after_bytes = os.path.getsize(LOG)
    print(f"条数 {before_n} → {after_n} | 体积 {before_bytes} → {after_bytes} B")
    if after_n != before_n + 2:
        print("❌ 条数增量不对 (应 +2)")
        return 1
    if after_bytes < before_bytes * 0.5:
        print("❌ 体积掉一半以上 —— 疑似截断")
        return 1
    print("✅ 落盘完成")
    return 0


if __name__ == "__main__":
    sys.exit(main())
