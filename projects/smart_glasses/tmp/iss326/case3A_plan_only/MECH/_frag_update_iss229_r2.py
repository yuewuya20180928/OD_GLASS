#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-229 分片原子写脚本 · 第 2 跳 —— MECH 闸锚点跟【并发落表 ISS-233】再重锚一次

★**为什么有第 2 跳**: 上一跳 (ISS-223) 重锚完成后, hw-lead 的 ★**ISS-233 第 3 批落表**★
(★**不是 ISS-232** —— ISS-232 交接单 §10 明写「本单网表侧一条都没改 ⇒ 网表 md5 `3215020b…` 不变」★)
在 2026-11-16 06:48:38 又改了网表 L442 一行 + 脚表 L531 一行:
    HW/netlist_v1.csv      3215020b6d4120e1b7728227effdc6d3 → 34132f7e40a241e1fae1476be0eafbd5
    HW/netlist_v1_pins.csv a600afae493f5a7a6c55f46ad35ac89c → b21b743a7702d30729f0d653c15392df
⇒ MECH 侧锚点又落后 ⇒ 门禁 `MECH/check_demo_struct_truth.py` 的 **G5b + C21 双红 (rc=2, 21/23)** ⇒
按 ★**ISS-224 建立的 H-1 流程**做【第 2 跳】重锚 (md5 = 交卷那一刻盘上实测 · prev_md5 = 上一跳真值 ·
by = 落表单号 · landed_at = 落表时刻) ⇒ 门禁回到 ★**rc=0 (23/23)**★

纪律:
  * 只写自己 (mech-lead) 的分片; 别人的分片一个字节都不碰
  * ★**`HW/` 一个字节都没改** —— 本脚本只写 `state/fragments/mech.yaml``
  * ★**没去卡住 / 等待 / 干预另一个 agent 的单** (ISS-233 是 hw-lead 的活, 本单只跟锚点)
  * issue 状态 / owner 是 main 的活, 本脚本不碰 `state/issue_log.yaml`
  * 走 `state/frag_write.py` 的 `update_fragment` (tmp + fsync + os.replace), 全程零 `open(p,"w")`
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, "state"))

from frag_write import update_fragment  # noqa: E402

AGENT = "mech-lead"
SINCE = "2026-11-16"

# ---- 落表后真值 (本机交卷那一刻 md5sum 实测) ----
NET_MD5 = "34132f7e40a241e1fae1476be0eafbd5"
NET_PREV = "3215020b6d4120e1b7728227effdc6d3"
PINS_MD5 = "b21b743a7702d30729f0d653c15392df"
PINS_PREV = "a600afae493f5a7a6c55f46ad35ac89c"
LANDED_AT = "2026-11-16 06:48:38"
BY = "ISS-233"

# ---- claim: 老 key 改名 + 改值 (旧值在 note 里留痕, 不删历史) ----
CLAIM_OLD_KEY = "mech_netlist_md5_anchor_iss223"
CLAIM_NEW_KEY = "mech_netlist_md5_anchor_iss233"
CLAIM_VALUE = (
    f"★**网表 `HW/netlist_v1.csv` = `{NET_MD5}`** (落表单 **{BY}** 第 3 批, 落表时刻 {LANDED_AT}; "
    f"上一跳 `{NET_PREV}` = ISS-223 第 2 批) · "
    f"★**脚表 `HW/netlist_v1_pins.csv` = `{PINS_MD5}`** (落表单 **{BY}**, 落表时刻 {LANDED_AT}; "
    f"上一跳 `{PINS_PREV}` = ISS-220)"
)
CLAIM_NOTE = (
    f"★**这是 MECH 闸 §1 `source_ledger` 锚点的现行真值 (交卷那一刻盘上 md5sum 实测)** ⇒ "
    f"★**md5 链**: 网表 `13f59a43dbd35dc6cb16e897c8c891ab` (ISS-220) → `{NET_PREV}` (ISS-223) → `{NET_MD5}` ({BY}); "
    f"脚表 `4814617e22b567d76164e56bc5e39dc8` (ISS-220) → `{PINS_PREV}` (ISS-220) → `{PINS_MD5}` ({BY}) ⇒ "
    f"★**每次落表都要同步 MECH 侧锚点 (H-1 流程), 不然门禁 C21 立刻红** ★ ⇒ "
    f"★**留痕**: `MECH/HW_CROSS_REVIEW_TRIAGE.md` §3.1 **R-02** (ISS-223 跳) + **R-03** ({BY} 并发跳) ★ ⇒ "
    f"★**门禁 G5b + C21: FAIL → [OK]** (rc=2 21/23 → rc=0 23/23; `--selftest` 14/14) ⇒ "
    f"★**注意: 触发第 2 跳的是 {BY} (第 3 批落表), 不是 ISS-232** (★ISS-232 交接单 §10 明写「本单网表侧一条都没改」★) ★ "
    f"★[实测] (本机 md5sum + 盘上 mtime + 门禁实跑前后对照)"
)
CLAIM_REF = "MECH/HW_CROSS_REVIEW_TRIAGE.md §1 source_ledger + §3.1 R-02 (ISS-223 跳) + R-03 (ISS-233 跳)"

# ---- 新增 artifact (第 2 跳重锚的机器留痕) ----
ARTIFACT = {
    "path": "MECH/HW_CROSS_REVIEW_TRIAGE.md",
    "kind": "doc",
    "version": "v2.1",
    "updated_at": SINCE,
    "summary": (
        f"ISS-229 MECH 闸重锚【第 2 跳】: §1 `source_ledger.entries` 跟 **ISS-233 第 3 批并发落表** 再重锚一次 —— "
        f"网表 `{NET_PREV}` → `{NET_MD5}` (by={BY}, landed_at {LANDED_AT}) · 脚表 `{PINS_PREV}` → `{PINS_MD5}` "
        f"(by={BY}, landed_at {LANDED_AT}) ⇒ §3.1 新增 **R-03** 行 (谁改的 / 哪个单号 / 新旧 md5 / 复现命令) · "
        f"§0 Q-10 与 §7 注同步 ⇒ ★**门禁 G5b + C21 由 FAIL 回到 [OK] (rc=2 21/23 → rc=0 23/23)**, "
        f"`--selftest` **14/14** 反向用例一条没删 (门禁脚本 md5 `fa9b59e5…` 未变 ⇒ 判据没被改软) · "
        f"★**HW/ 一个字节没改** (本单只重锚 MECH 侧锚点 + 留痕) · ★**没卡住/等待/干预另一个 agent 的单**"
    ),
}

# ---- 新增 answer (回给 main: V-4 更新包 + 并发落表的处理) ----
ANSWER = {
    "key": "iss229_mech_v4_update_package_and_gate_reanchor",
    "to": "main",
    "value": (
        "★**ISS-229 收口 (4 件交付物全齐)** ⇒ ① 系数改正 (0.822 倒数方向 → **1.216 @3.70V / 1.071 @4.20V**, "
        "取最坏 1.216) + 三张表重出 (rilim_table 15 / copper_vs_rilim 10 / rilim_full_grid 30 行) ⇒ "
        "★**max 档 1oz 皮肤侧: 300Ω 61.4 ❌ / 390Ω 50.6 ❌ (超 43 °C 红线 7.6 °C) / 470Ω 45.8 ❌ / "
        "680Ω 40.1 ✅ (余 2.9 °C) / 1.2kΩ 36.7 ✅** ⇒ 单 pin max 0.790 / 0.608 / 0.505 / 0.349 / 0.198 A ⇒ "
        "TS 偏移 1.46 / 1.13 / 0.93 / 0.65 / 0.37 °C ⇒ 充电 (400 mAh 仅 CC 段) 15/20/24/34/61 min ⇒ "
        "★**活档 = 680Ω / 1.2kΩ** (★**V-4 待 main/老板拍, 本单不代拍, 一句「建议选 X」都没写**★) ⇒ "
        "★**原 42.14 °C / 47.07 °C 判为无有效数字** (按作废的 0.822 算) ★ "
        "★② 文档 `MECH/HINGE_POWER_CALC.md` §0-A + §0-A.1 口径订正留痕 (旧值→新值对照 22 行, 旧数一个没删) ★ "
        "★③ V-4 更新包 = 30 行全网格 (每档 × min/typ/max × 1oz/2oz: 新皮肤侧 + pass_43 + 充电时间 + "
        "单 pin vs 0.5 A 触点额定) + 「充电时皮肤侧是否仍是硬约束」的现状说明 (老板 10-28 已拍「边戴边充不允许」"
        "⇒ 充电时眼镜不在皮肤上 ⇒ 皮肤侧 43 °C 在产品语义上不是硬约束; ★**但铰链段温升 / TS 停充门限 / "
        "单 pin 触点额定这 3 条与佩戴无关, 依然成立**★; 只作说明, 未改老板已拍口径) ★ "
        "★④ MECH 闸重锚: **两跳** (第 1 跳 ISS-223 `13f59a43…`→`3215020b…`; ★**第 2 跳 = 交卷期间 "
        "hw-lead 的 ISS-233 第 3 批并发落表 (06:48:38) 改了网表 L442 + 脚表 L531 ⇒ 再跟到 `34132f7e…` / "
        "`b21b743a…`**★) ⇒ §3.1 **R-02 + R-03** 两行留痕 ⇒ ★**门禁 rc=2 (21/23) → rc=0 (23/23)**, "
        "`--selftest` **14/14** 一条没删 ★ ⇒ ★**HW/ 一个字节没改** (并发落表是 hw-lead 的活, 本单只跟 MECH 锚点; "
        "没卡住/等待/干预另一个 agent 的单) ★ ⇒ 板端 [实测] = 0 条 · 零外发 · 未自签 issue_log · "
        "★**与 main 本轮独立推算逐条一致** (390Ω max 50.6 / 470Ω max 45.8 / 680Ω max 40.1, ICHG / P / ΔT 全同值)"
    ),
    "ref": "HANDOFF/2026-11-16_mech-lead_ISS229_充电皮肤温度重算与MECH闸重锚.md (B1~B6) + MECH/HINGE_POWER_CALC.md §0-A",
}

# ---- 新增 need (给 hw-lead: 落表必须同步 MECH 锚点 + 这次的并发实况) ----
NEED = {
    "key": "iss229_hw_landing_must_sync_mech_anchor_iss233",
    "to": "hw-lead",
    "item": (
        "★**ISS-233 第 3 批落表 (2026-11-16 06:48:38) 改了网表 L442 + 脚表 L531** ⇒ MECH 闸 "
        "`MECH/check_demo_struct_truth.py` 的 **G5b + C21 双红 (rc=2, 21/23)** ⇒ ★**我已按 H-1 流程把 MECH 侧锚点 "
        f"跟过去** (网表 `{NET_MD5}` / 脚表 `{PINS_MD5}`, by=ISS-233, landed_at {LANDED_AT}, 留痕在 "
        "`MECH/HW_CROSS_REVIEW_TRIAGE.md` §3.1 R-03) ⇒ 门禁回 rc=0 (23/23) ★ ⇒ ★**但下次落表请直接同步 MECH 侧锚点** "
        "(§1 `source_ledger.entries` 的 `md5` / `prev_md5` / `by` / `landed_at` 四个字段), 别等我这边红了一遍再补 ⇒ "
        "★**落表记录里必须能查到【落表单号 + 该文件名 + 新 md5 + 旧 md5】四项** (C21 逐项对账) ⇒ "
        "★**注意: ISS-232 本身没改网表** (其交接单 §10 明写「网表 md5 `3215020b…` 不变」) ⇒ 真正触发重锚的是 ISS-233"
    ),
    "since": SINCE,
}

STATUS = {
    "phase": "P3",
    "progress_pct": "99",
    "health": "yellow",
    "summary": (
        "2026-11-16 ISS-229 (充电皮肤温度按改正系数 1.216 重算 + MECH 闸 G5b/C21 重锚【两跳】): "
        "★**根因 = 换算系数方向反了** —— buck 功率守恒 ICHG/IIN = η·Vbus/Vbat = 0.90×5.0/3.70 = **1.216** "
        "(@4.20V ⇒ 1.071), 旧 **0.822** = (Vbat/Vbus)/η = 1.216 的**精确倒数** ⇒ 系数偏小 ⇒ 电流偏小 ⇒ "
        "温度偏乐观 ⇒ 旧表 rilim_table / copper_vs_rilim / rilim_full_grid **全部作废 (逐字留痕, 不删)** ⇒ "
        "新数 (max 档 1oz): 皮肤侧 300Ω **61.4** ❌ / 390Ω **50.6** ❌ (超 43 °C 红线 7.6 °C) / 470Ω **45.8** ❌ / "
        "**680Ω 40.1** ✅ (余 2.9 °C) / **1.2kΩ 36.7** ✅; 单 pin max 0.790 / **0.608** ❌ / 0.505 / 0.349 / 0.198 A; "
        "TS 偏移 1.46 / **1.13** / 0.93 / **0.65** ✅ / 0.37 °C (留 1 °C 裕量只在 680Ω/1.2kΩ 成立); "
        "充电时间 (400 mAh 仅 CC 段) 15/20/24/34/61 min ⇒ **活档 = 680Ω / 1.2kΩ** "
        "(V-4 待 main/老板拍, **本单不代拍**); 原 42.14 °C / 47.07 °C **无有效数字**。"
        "★**MECH 闸重锚【两跳】**: 第 1 跳 = ISS-223 第 2 批落表 (13f59a43…→3215020b…) + §3.1 **R-02** 留痕; "
        f"★**第 2 跳 = 交卷期间 hw-lead 的 ISS-233 第 3 批并发落表 (06:48:38) 改了网表 L442 + 脚表 L531** "
        f"(3215020b…→{NET_MD5} / a600afae…→{PINS_MD5}) ⇒ 按 H-1 再重锚 + §3.1 **R-03** 留痕 ⇒ "
        "⇒ 门禁 **G5b + C21 由 FAIL 回到 [OK] (rc=2 21/23 → rc=0 23/23)**, `--selftest` **14/14** 反向用例一条没删 "
        "(门禁脚本 md5 `fa9b59e5…` 未变 ⇒ 判据没被改软); ★**HW/ 一个字节没改** (并发落表是 hw-lead 的活, 本单只跟 MECH 锚点; "
        "没卡住/等待/干预另一个 agent 的单); ★**触发的第 2 跳是 ISS-233 不是 ISS-232** (ISS-232 交接单 §10 明写它没改网表)。"
        "★**三道门禁实跑全绿**: check_demo_struct_truth **23/23** + cavity_recalc **22/22** + verify_budget 绿。"
        "★阈值一个不许动 (皮肤 43 °C / 端件 60 °C / cavity_req 4.50 / CRIT 0.60 / cav_v 38.00 / duct_v 6.00) · "
        "零外发 · 板端 [实测] = 0 条 · **不自签 issue_log** (status 留给 main 落 verified) · 未碰 HW/ SW/ PROJECT_TRACKER §0。"
    ),
}


def mutate(d: dict) -> None:
    # ---- artifact: 已有则更新 version/summary, 没有则追加 (幂等) ----
    arts = d.setdefault("artifacts", [])
    for a in arts:
        if a.get("path") == ARTIFACT["path"] and a.get("version") == "v2.0":
            a["version"] = ARTIFACT["version"]
            a["summary"] = ARTIFACT["summary"]
            a["updated_at"] = SINCE
            break
    else:
        arts.append(dict(ARTIFACT))

    # ---- interface_claim: 老 key 改名 + 改值 (旧值在 note 里留痕) ----
    claims = d.setdefault("interface_claims", [])
    for c in claims:
        if c.get("key") == CLAIM_OLD_KEY:
            c["key"] = CLAIM_NEW_KEY
            c["value"] = CLAIM_VALUE
            c["note"] = CLAIM_NOTE
            c["ref"] = CLAIM_REF
            break
    else:
        claims.append({"key": CLAIM_NEW_KEY, "value": CLAIM_VALUE, "note": CLAIM_NOTE, "ref": CLAIM_REF})

    # ---- answer / need: 幂等追加 ----
    answers = d.setdefault("answers", [])
    if not any(a.get("key") == ANSWER["key"] for a in answers):
        answers.append(dict(ANSWER))

    needs = d.setdefault("needs_from", [])
    if not any(n.get("key") == NEED["key"] for n in needs):
        needs.append(dict(NEED))

    # ---- 既有 need 只追加订正说明 (历史条目不删不改值) ----
    for n in needs:
        if n.get("key") == "iss224_hw_landing_must_update_gate_ledger":
            add = (
                " ★**【ISS-229 实测补注】** 2026-11-16 交卷期间又发生一次并发落表: "
                f"**ISS-233 第 3 批** (06:48:38) 改了网表 L442 + 脚表 L531 ⇒ 锚点又落后 ⇒ 门禁 C21 双红 ⇒ "
                f"**我已按 H-1 再重锚到 `{NET_MD5}` / `{PINS_MD5}` (by=ISS-233), 留痕在 "
                "`MECH/HW_CROSS_REVIEW_TRIAGE.md` §3.1 R-03** ⇒ ★**请以后落表时直接同步 MECH 侧锚点, "
                "别等门禁红了一遍再补** ★"
            )
            if add not in (n.get("item") or ""):
                n["item"] = (n.get("item") or "") + add

    d.setdefault("status", {}).update(STATUS)


def main() -> int:
    d = update_fragment(AGENT, mutate)
    print(f"[frag_update_iss229_r2] ✅ {AGENT} 分片已原子更新 "
          f"(artifact {len(d.get('artifacts') or [])} / claim {len(d.get('interface_claims') or [])} / "
          f"answer {len(d.get('answers') or [])} / need {len(d.get('needs_from') or [])}) "
          f"⇒ 再跑 python3 state/merge.py")
    print(f"[frag_update_iss229_r2] ★claim {CLAIM_OLD_KEY} → {CLAIM_NEW_KEY} (旧值留痕在 note)")
    print(f"[frag_update_iss229_r2] ★网表 {NET_PREV} → {NET_MD5} · 脚表 {PINS_PREV} → {PINS_MD5} (by={BY})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
