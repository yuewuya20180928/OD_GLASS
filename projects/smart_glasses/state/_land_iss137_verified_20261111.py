#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""落账 ISS-137 → verified (2026-11-11 04:3x, 项目总工 main)

★**为什么现在能落**: sw-lead 的 **rev3 复验 (2026-11-11 03:3x) = pass** (F5 已闭合)
   ⇒ sw-lead 在 `state/fragments/sw.yaml` 的 `iss137_verify_result` = 'pass'
   ⇒ HANDOFF/2026-11-11_sw-lead_ISS137_rev3_验证.md §9.4「签字条件已全部满足」

★**本单是"别人验"结构** (owner=main / verify_by=sw-lead) ⇒ 铁律满足:
   修复人 (main) 不能自验, 由 sw-lead 独立复核 ⇒ ⇒ 签字已到手才落账。

★**我没有采信 sw-lead 的自证, 自己也重跑了** (落账前):
   - `python3 HW/e2e_budget_rk3572.py --selftest` ⇒ rc=0 (原 4 条已发布数字 + 拆分护栏 7 条全过)
   - `python3 SW/tools/demo_timing_check.py` ⇒ rc=0 (20/20)
   - 4 个交付物 md5 = sw-lead rev3 基线逐字节相同:
       0e622d56… / 71f0c913… / 62026429… / 661f43c7…
   - note 里 F5 旧断言整句 count=0 / 新断言整句 count=1; 四个数 (−2.69/10.09/16.65/2.32/−10.46/8.87) 全在位且归属正确
   - 实跑复核两个函数: display_out_max_for/compose_max_for = −2.685/−10.461 · 10.095/2.319 · 16.650/8.874,
     tx_min_ms(1920,1080)=7.776 ⇒ 三个 S5 差值都恰 7.776

原子写 (tmp + os.replace), 禁 open(p,"w") 覆盖。
"""
import os
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
TODAY = "2026-11-11"

NOTE_ADD = (
    "\n★2026-11-11 04:3x 项目总工落账 **verified** (verify_result=pass, verify_by=sw-lead, verify_date=2026-11-11)\n"
    "【签字来源】sw-lead **rev3 复验 = pass** (2026-11-11 03:3x) ⇒ 报告 "
    "`HANDOFF/2026-11-11_sw-lead_ISS137_rev3_验证.md` §9.4「签字条件已全部满足」· "
    "分片 `state/fragments/sw.yaml` 的 `iss137_verify_result` = 'pass' ⇒ ★**别人验**成立 (owner=main / verify_by=sw-lead)。\n"
    "【★我没有采信 sw-lead 的自证, 落账前自己重跑了一遍】:\n"
    "  ① `python3 HW/e2e_budget_rk3572.py --selftest` ⇒ **rc=0** (原 4 条已发布数字 + ★拆分护栏 7 条全过) "
    "⇒ 含「TX 在账里: 同一合成值下 加/不加 TX 差 7.776 ms」★**这个 7.776 恰等于 TX 物理下限**。\n"
    "  ② `python3 SW/tools/demo_timing_check.py` ⇒ **rc=0 (20/20)**。\n"
    "  ③ ★**4 个交付物 md5 与 sw-lead rev3 基线逐字节相同** ⇒ 交付物自 rev2 复验以来一个字节没动: "
    "`0e622d56…` (HW/e2e_budget_rk3572.py) / `71f0c913…` (SW/DEMO_OD_TIMING_SPEC.md) / "
    "`62026429…` (SW/RKNN_BENCH.md) / `661f43c7…` (SW/tools/demo_timing_check.py)。\n"
    "  ④ ★**F5 独立复核**: note 里旧断言整句 count=**0** / 新断言整句 count=**1** ⇒ 旧句是**整句消失**不是 token 缺席 ⇒ "
    "note 里 compose_max_for 出现 10 处、display_out_max_for 7 处 ⇒ ★**真歧义行 = 0** ⇒ 归属全对。\n"
    "  ⑤ ★**实跑复核两个函数** (不照抄报告的数): display_out_max_for / compose_max_for = "
    "−2.685 / −10.461 (S5=26.085) · 10.095 / 2.319 (S5=13.305) · 16.650 / 8.874 (S5=6.750) · "
    "tx_min_ms(1920,1080) = 7.776 ⇒ 三个 S5 的差值都**恰好 7.776** ⇒ 与 note 逐位对上 ⇒ ★**F5 成立**。\n"
    "【本单对项目的作用 (不改, 只记)】60ms 从「推算」变成「可测」: 板端打第7段合成 + 第8段上屏两个点 ⇒ "
    "`python3 HW/e2e_budget_rk3572.py --t-compose-ms <实测值>` 一行出结论。★**但那 2.32ms 现在仍是 [0数据] 的假人** "
    "(板还没到) ⇒ ★**板端合成段超 2.32ms ⇒ yolov5n@640 方案A 直接判死**。\n"
    "【★遗留 (sw-lead rev3 §9.3 如实报的「未做」项, 不藏)】① 护栏 2 个洞 (M2 默认参数踢 TX / M3 无护栏钉 TX 绝对值) "
    "⇒ 需加护栏⑧⑨⑩; ② DSI payload 8× 口径差 6 处 (373/246 Mbps ⇒ 真值 2986/1475 Mbps); "
    "③ 4 处下游旧口径残留 (PROJECT_TRACKER.md:2098 / SW/DEMO_OD_PIPELINE_SPEC.md:447 / "
    "SW/DEMO_OD_TIMING_SPEC.md:194 / SW/tools/rknn_bench.py:257·261)。⇒ ★**这三条已另开 ISS-186 承接** "
    "(owner=main / verify_by=sw-lead), ★**不在本单偷偷带过**。\n"
    "【边界】★**没有改 §0 锁死表** · ★**没有改任何交付物** (md5 已验) · ★**没有动其他 agent 的分片** · "
    "★**没有发任何邮件/外联** · ★**没有下采购单**。"
)

with open(LOG, encoding="utf-8") as f:
    doc = yaml.safe_load(f)

issues = doc.get("issues")
items = list(issues.values()) if isinstance(issues, dict) else list(issues or [])

hit = None
for it in items:
    if it.get("id") == "ISS-137":
        hit = it
        break

if hit is None:
    print("❌ issue_log 里找不到 ISS-137")
    sys.exit(1)

before = (hit.get("status"), hit.get("verify_result"), hit.get("verify_date"), hit.get("verify_by"))

if before[1] == "pass" and before[0] == "verified":
    print("ℹ️ 已经是 verified/pass, 无需再落 (幂等)")
    sys.exit(0)

if before[3] != "sw-lead":
    print(f"❌ verify_by={before[3]!r} ≠ 'sw-lead' ⇒ 拒绝落账 (结构不符)")
    sys.exit(2)

note = hit.get("note") or ""
if "2026-11-11 04:3x 项目总工落账" not in note:
    hit["note"] = note + NOTE_ADD

hit["status"] = "verified"
hit["verify_result"] = "pass"
hit["verify_date"] = TODAY
hit["verify_by"] = "sw-lead"

fd, tmp = tempfile.mkstemp(dir=HERE, prefix=".issue_log.", suffix=".tmp")
try:
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        yaml.safe_dump(doc, f, allow_unicode=True, sort_keys=False, width=200)
    os.replace(tmp, LOG)
except Exception:
    if os.path.exists(tmp):
        os.unlink(tmp)
    raise

print("✅ ISS-137 已原子落账:")
print(f"   status       {before[0]} → verified")
print(f"   verify_result {before[1]} → pass")
print(f"   verify_date   {before[2]} → {TODAY}")
print(f"   verify_by     {before[3]} (未变)")
print("   note 已追加 (落账依据 + 我自己的独立复核 + 遗留三条)")
