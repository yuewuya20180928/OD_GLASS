#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""落账 ISS-187 → verified (2026-11-11 05:4x, 项目总工 main)

★**为什么现在能落**: sw-lead 的 **ISS-187 复验 = pass** (2026-11-11 05:10)
   ⇒ `state/fragments/sw.yaml` 的 `iss187_verify_result` = 'pass'
   ⇒ HANDOFF/2026-11-11_sw-lead_ISS187_验证.md §8.1「我签了」+ §8.2 落账指令

★**本单是「别人验」结构** (owner=main / verify_by=sw-lead) ⇒ 铁律满足:
   修复人 (main) 不能自验, 由 sw-lead 独立复核 ⇒ ⇒ 签字已到手才落账。

★**我没有采信 sw-lead 的自证, 落账前自己重跑了**:
   - `python3 HW/e2e_budget_rk3572.py --selftest` ⇒ rc=0 (护栏 7 → 10 条全过, 含 ⑧⑨⑩ 值型)
   - `python3 SW/tools/demo_timing_check.py` ⇒ rc=0
   - 5 个交付物 md5 = sw-lead 实测值逐字节相同:
       d7d1b110… (HW/e2e_budget_rk3572.py, 落账前) / 88f441ec… (SW/DEMO_OD_TIMING_SPEC.md)
       / 38e256d2… (SW/tools/rknn_bench.py) / 2fe3be4c… (SW/DEMO_OD_PIPELINE_SPEC.md)
       / 085a2ed1… (PROJECT_TRACKER.md)
   - ★**stdout 与「加护栏前」真基线 6ced111 逐字节相同** (10908 B, diff 空) ⇒ 已发布数字一个没动
   - sw-lead 报的 §7.1 非阻塞瑕疵 (护栏⑨ 注释出处指针写错) ⇒ ★**同批订正** (值不动, 只改注释指针)

原子写 (tmp + os.replace), 禁 open(p,"w") 覆盖。
"""
import os
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
TODAY = "2026-11-11"

# ★**订正 1: desc 里的 §(1.56) 指针** (sw-lead §7.1 报的精确位置)
OLD_DESC = (
    "    (★对齐 `PROJECT_TRACKER.md` §(1.56) 已发布的「4-lane@2.0Gbps × 80% 有效」★)"
)
NEW_DESC = (
    "    (★对齐 `SW/DEMO_OD_TIMING_SPEC.md` §3.3.1 已发布的「4-lane D-PHY@2.0Gbps × 80%」"
    "+ `PROJECT_TRACKER.md:2099` 的「4-lane@2.0Gbps」★)"
)

NOTE_ADD = (
    "\n★2026-11-11 05:4x 项目总工落账 **verified** (verify_result=pass, verify_by=sw-lead, verify_date=2026-11-11)\n"
    "【签字来源】sw-lead **ISS-187 复验 = pass** (2026-11-11 05:10) ⇒ 报告 "
    "`HANDOFF/2026-11-11_sw-lead_ISS187_验证.md` §8.1「我签了」· "
    "分片 `state/fragments/sw.yaml` 的 `iss187_verify_result` = 'pass' ⇒ ★**别人验**成立 (owner=main / verify_by=sw-lead)。\n"
    "【★我没有采信 sw-lead 的自证, 落账前自己重跑了一遍】:\n"
    "  ① `python3 HW/e2e_budget_rk3572.py --selftest` ⇒ **rc=0** (护栏 7 → **10 条全过**, 含 ⑧⑨⑩ 三条**值型**护栏) ⇒ "
    "⑧ 钉 TX_MIN_800=1.800 / TX_MIN_1080=7.776 · ⑨ 钉 4-lane@2.0Gbps×0.8 · ⑩ 钉默认值必须带 TX。\n"
    "  ② `python3 SW/tools/demo_timing_check.py` ⇒ **rc=0**。\n"
    "  ③ ★**5 个交付物 md5 与 sw-lead 实测值逐字节相同**: `d7d1b110…` (HW/e2e_budget_rk3572.py) / "
    "`88f441ec…` (SW/DEMO_OD_TIMING_SPEC.md) / `38e256d2…` (SW/tools/rknn_bench.py) / "
    "`2fe3be4c…` (SW/DEMO_OD_PIPELINE_SPEC.md) / `085a2ed1…` (PROJECT_TRACKER.md)。\n"
    "  ④ ★**stdout 与「加护栏前」真基线 6ced111 (md5 0e622d56…) 逐字节相同** ⇒ 10908 B, `diff` 空 ⇒ "
    "★**已发布数字一个没动** (★别拿 `git show HEAD:` 对拍 —— 发布树 HEAD 已含本单改动, 对拍恒等什么也证明不了★)。\n"
    "  ⑤ ★**sw-lead §7.1 报的 1 条非阻塞瑕疵已同批订正**: 护栏⑨ 注释的出处指针 `§(1.56)` (sensor 拍板) → "
    "`SW/DEMO_OD_TIMING_SPEC.md` §3.3.1 + `PROJECT_TRACKER.md:2099` ⇒ ★**只改注释, 值没动, 护栏行为不受影响, "
    "stdout 仍 10908 B 逐字节相同** ⇒ `HW/e2e_budget_rk3572.py` md5 `d7d1b110…` → **`7b820c14acfaee08a218cbf85557ef0b`**。\n"
    "【本单对项目的作用 (不改, 只记)】★**护栏从「关系型」升级成「值型」** ⇒ 以前改脚本的人可以把 TX 物理下限改小而 7 条护栏全绿; "
    "现在 ⑧⑨⑩ 钉的是**已发布字面值** ⇒ M2 (默认值踢 TX) / M3 (lane 速率偷偷加倍) **现在会真变红** ⇒ "
    "★**老板那条生死线数字 (合成段只剩 2.32ms) 不会再被悄悄改宽**。\n"
    "【★遗留 (sw-lead 如实报的「未做」项, 不藏)】① DSI payload 8× 口径差 6 处 (373/246 Mbps ⇒ 真值 2986/1475 Mbps) "
    "⇒ ★**归 hw-lead 的分片, 已在 ISS-186 承接** (★本轮未派: ISS-181 在飞 ⇒ 一个 agent 同时只允许一个写会话★) "
    "② ★**M8 变异体 (`T_PANEL` 5.00→4.00) selftest 仍全绿** ⇒ ★**基线就有的性质, 非本单引入** ⇒ 建议后续加护栏⑪。\n"
    "【边界】★**没有改 §0 锁死表** · ★**没有改任何已发布数字** (stdout 逐字节已验) · ★**没有动其他 agent 的分片** · "
    "★**没有发任何邮件/外联** · ★**没有下采购单**。"
)

FIX_REF_ADD = (
    "\n  ⑤ ★**2026-11-11 05:4x 落账时同批订正 (sw-lead §7.1 非阻塞瑕疵)**: `HW/e2e_budget_rk3572.py:248` "
    "护栏⑨ 的 `#` 注释出处指针 `§(1.56)` → `SW/DEMO_OD_TIMING_SPEC.md` §3.3.1 + `PROJECT_TRACKER.md:2099` "
    "⇒ ★**只改注释, 值没动, 护栏行为不变, stdout 仍 10908 B 逐字节相同** ⇒ md5 `d7d1b110…` → "
    "**`7b820c14acfaee08a218cbf85557ef0b`** (★落账后新 md5, 供下次对拍★)"
)

with open(LOG, encoding="utf-8") as f:
    doc = yaml.safe_load(f)

issues = doc.get("issues")
items = list(issues.values()) if isinstance(issues, dict) else list(issues or [])

hit = None
for it in items:
    if it.get("id") == "ISS-187":
        hit = it
        break

if hit is None:
    print("❌ issue_log 里找不到 ISS-187")
    sys.exit(1)

before = (hit.get("status"), hit.get("verify_result"), hit.get("verify_date"), hit.get("verify_by"))

if before[1] == "pass" and before[0] == "verified":
    print("ℹ️ 已经是 verified/pass, 无需再落 (幂等)")
    sys.exit(0)

if before[3] != "sw-lead":
    print(f"❌ verify_by={before[3]!r} ≠ 'sw-lead' ⇒ 拒绝落账 (结构不符)")
    sys.exit(2)

desc = hit.get("desc") or ""
if OLD_DESC in desc:
    hit["desc"] = desc.replace(OLD_DESC, NEW_DESC)
    print("✅ desc 指针已订正 (§(1.56) → DEMO_OD_TIMING_SPEC §3.3.1 + tracker:2099)")
else:
    print("ℹ️ desc 里没找到待订正的指针串 (可能已被订正) — 跳过")

fr = hit.get("fix_ref") or ""
if "7b820c14acfaee08a218cbf85557ef0b" not in fr:
    hit["fix_ref"] = fr + FIX_REF_ADD

note = hit.get("note") or ""
if "2026-11-11 05:4x 项目总工落账" not in note:
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

print("✅ ISS-187 已原子落账:")
print(f"   status        {before[0]} → verified")
print(f"   verify_result {before[1]} → pass")
print(f"   verify_date   {before[2]} → {TODAY}")
print(f"   verify_by     {before[3]} (未变)")
print("   desc 指针已订正 + fix_ref 追加新 md5 + note 已追加 (落账依据 + 我自己的独立复核 + 遗留两条)")
