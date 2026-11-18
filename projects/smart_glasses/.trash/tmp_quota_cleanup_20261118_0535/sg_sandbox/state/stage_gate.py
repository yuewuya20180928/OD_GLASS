# -*- coding: utf-8 -*-
"""
阶段门 (Stage Gate) —— 从"纸面推算"到"样机交付"的唯一推进依据
================================================================================
老板 10-25 12:01: "在所有前置的阻塞点解决之后, 如何确保整体项目有序开展直至整个项目完美结束?"

问题: 阻塞点解完不等于能往下走 —— 常见翻车是"纸面都齐了 → 画完原理图 → 打印件装不上 → 板子回来发现
      电源域不对 → 全套返工"。所以每一关必须**有准出判据**, 且判据必须是机械可判的 (数字/状态),
      不能是"感觉差不多了"。

本脚本判定:
  - 当前在第几关 (第一个未通过的关卡)
  - 每关还缺什么 (具体到 issue / 决策 / 实测项)
  - 距进入下一阶段还差几项

准出判据三类 (全部可复现):
  A. issue_closed  —— 该关相关的所有问题单必须 verified/closed (状态见 issue_log.yaml)
  B. decision      —— 老板的拍板项必须在 pm.yaml 里已 answered
  C. measurement   —— 该关要求的**实测数据**必须已登记 (measurements.yaml, 推算值不算数)

用法:  python3 state/stage_gate.py [--json]
退出码: 0=当前关已通过  1=当前关未通过 (正常)  2=文件错
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)

# ---------------------------------------------------------------- 阶段定义
GATES = [
    {
        "id": "G0", "name": "纸面冻结 (需求/口径/方案定型)",
        "why": "所有数字还停在推算层; 这一关锁死口径, 后面才不会整体返工",
        "issues": ["ISS-002", "ISS-012", "ISS-014"],          # 老板拍板三项 + 散热方案
        "decisions": ["q1_latency_scope", "q4_battery_scope", "q17_display_fps", "q16_aspect_ratio"],
        "measurements": [],
    },
    {
        "id": "G1", "name": "原理图 / PCB 定稿",
        "why": "ARS45 纸面资料必须齐全, 否则画出来是废纸 (pitch 装不下 = 直接否决选型)",
        "issues": ["ISS-001", "ISS-003", "ISS-005", "ISS-006", "ISS-007", "ISS-008", "ISS-011", "ISS-015"],
        "decisions": [],
        "measurements": [],
        # ★2026-11-04 19:1x 老板: 自研开发主板 = 当前最高优先级 ⇒ **G1 必须真过"可下单"**
        #   之前 G1 只看问题单, 结果**板子一根线都没布 (unconnected 353) 也显示"通过"** ⇒ 假绿
        #   ⇒ 判据: 布线完成留证文件 `HW/PCB/.layout_done.json` 里 unconnected == 0 且 DRC 违规 == 0
        "routing_required": True,
    },
    {
        "id": "G2", "name": "结构样机装配 (打印件 + 电池 + 光机位姿)",
        "why": "镜框/镜脚装不装得下, 只有打出来才知道; 0 件实测 = 这一关不能过",
        # ★2026-11-04 10:09 老板指示「打印环境暂时不需要」+ 11-02 19:25「硬件优先, 结构不考虑」
        # ⇒ 结构整关挪到整机阶段 ⇒ **当期阶段门直接走 G3 (板级上电联调)**
        "deferred": True,
        "deferred_note": ("老板 11-02 19:25「硬件优先, **结构不考虑**」(结构单冻结不投人; demo 形态 = 一块主板 + sensor 模组 + 屏幕模组 + 板内 FPC, "
                          "跨铰链取消, 不装电池) + 11-04 10:09「打印环境暂时不需要」⇒ ★**整关挪到整机阶段**; "
                          "触发重开: ① 波导/光机/镜框路线定下来 ② 老板重新要结构样机"),
        "issues": ["ISS-004", "ISS-013", "ISS-016", "ISS-017"],
        "decisions": [],
        "measurements": ["M-PRINT", "M-FIT", "M-WEIGHT"],
    },
    {
        "id": "G3", "name": "上电联调 + 硬指标实测",
        "why": "两个硬指标 (端到端 60ms / 皮肤 43°C) 至今 0 实测; 这一关不过, 项目没有交付物",
        "issues": ["ISS-009", "ISS-010"],
        "decisions": [],
        # ★2026-11-04 09:57 老板: 当前 demo 板不考虑温度 (热电偶不需要) ⇒ M-SKIN/M-CHRG 移出当期验收范围;
        # ★10-25 19:23 老板: 光机延迟改主观 ⇒ M-OPTIC 由 M-DIZZY 替代 ⇒ **当期只留 5 项**
        "measurements": ["M-NPU", "M-E2E", "M-POWER", "M-BATT", "M-DIZZY"],
    },
    {
        "id": "G4", "name": "体验验收 (DoD 全过)",
        "why": "所有问题单关闭 + 质量门全绿 + DoD 清单逐条签",
        "issues": [],            # G4 要求: 全部 issue 都关
        "all_issues_closed": True,
        "decisions": [],
        "measurements": [],
        "dod": True,
    },
]


# ★**延后到整机/量产阶段的实测项** (不是删, 是挪阶段 —— 挪了就必须写清触发重开条件)
# ★2026-11-04 09:57 老板: 「当前 demo 板不考虑温度, 热电偶不需要」 ⇒ 皮肤热学不进当期验收
# ★2026-10-25 19:23 老板: 光机延迟不外部测设备, 改主观验收 ⇒ M-OPTIC 由 M-DIZZY 顶替
DEFERRED_MEASUREMENTS = {
    "M-SKIN": "整机/量产阶段做贴皮肤稳态温度 (43°C 是 ISO 13732-1 烧伤红线) —— 触发: 整机样机贴皮肤测试",
    "M-CHRG": "整机/量产阶段做充电场景皮肤温度 (推算 75.1°C 属烫伤风险) —— 触发: 同上",
    "M-OPTIC": "光机逐帧延迟绝对值 —— 老板 10-25 决定不采购高速相机/示波器, 改由 M-DIZZY (主观) 替代",
}


def _load_layout_stamp():
    """读 `HW/PCB/.layout_done.json` (布线完成留证: unconnected / DRC 违规 / 时间戳)
    ★缺失或读不出来 ⇒ 视为"未布线" (宁可红, 不可假绿)"""
    p = os.path.join(PROJ, "HW", "PCB", ".layout_done.json")
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def load_yaml(path: str):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def decision_done(pm: dict, key: str) -> bool:
    """老板决策是否已答。★两条判据 (与 merge.py 同源, 2026-10-28 修):
    ① 需求带 `decision` 字段 = 老板已拍板 (原话), 由项目总工代录 → 直接算已答
    ② needs_from 的 key 被 pm.yaml 的 answers 闭合 (answer 的 by == 需求的 to)
    ★旧实现只有 ② ⇒ 老板 10-25 19:16 拍过板的 Q1/Q4/Q16/Q17 在 pm.yaml 里有 decision 字段,
      但配对不上 -> G0 被 4 个**已答**问题假性卡死 (2026-10-28 08:1x 实测发现)。
    ★★本函数是模块级的 (判据唯一真源) —— 自测 state/test_stage_gate_decisions.py
       直接 import 它, 不再复制一份 (复制 = 必然漂移 = 测试变成摆设)。
    """
    ans_by_key: dict[str, list] = {}
    for a in (pm.get("answers") or []):
        if a.get("key"):
            ans_by_key.setdefault(a["key"], []).append(a.get("by"))
    pm_needs = {n.get("key"): n for n in (pm.get("needs_from") or [])}
    n = pm_needs.get(key)
    if not n:
        return False
    # ① 老板决策已代录 (★空白/纯空格不算决策, 防空壳字段蒙混过关)
    if str(n.get("decision") or "").strip():
        return True
    # ② answers 配对
    to = n.get("to")
    return bool(to) and to in (ans_by_key.get(key) or [])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    log_p = os.path.join(HERE, "issue_log.yaml")
    meas_p = os.path.join(HERE, "measurements.yaml")
    state_p = os.path.join(PROJ, "STATE.yaml")
    pm_p = os.path.join(HERE, "fragments", "pm.yaml")
    for p in (log_p, meas_p, state_p, pm_p):
        if not os.path.exists(p):
            print(f"❌ 找不到 {p}")
            return 2

    log = load_yaml(log_p) or {}
    issues = {i.get("id"): i for i in (log.get("issues") or [])}
    meas = load_yaml(meas_p) or {}
    needed = {m["id"]: m for m in (meas.get("needed") or [])}
    have = {m.get("id"): m for m in (meas.get("measurements") or []) if m.get("id")}
    state = load_yaml(state_p) or {}
    pm = load_yaml(pm_p) or {}

    # 老板决策是否已答 (pm.yaml 里 needs_from 的 key 被 answers 闭合)
    ans_by_key = {}
    for a in (pm.get("answers") or []):
        if a.get("key"):
            ans_by_key.setdefault(a["key"], []).append(a.get("by"))
    pm_needs = {n.get("key"): n for n in (pm.get("needs_from") or [])}

    def _decision_done(key: str) -> bool:
        return decision_done(pm, key)

    def issue_done(iid: str) -> bool:
        it = issues.get(iid)
        return bool(it) and it.get("status") in ("verified", "closed")

    def meas_done(mid: str) -> bool:
        m = have.get(mid)
        # ★ 推算值不算实测: kind 必须是 实测
        return bool(m) and str(m.get("kind")) == "实测" and m.get("value") not in (None, "")

    results = []
    for g in GATES:
        miss_issue, miss_dec, miss_meas = [], [], []
        for iid in g.get("issues", []):
            if not issue_done(iid):
                it = issues.get(iid) or {}
                miss_issue.append(f"{iid} [{it.get('status', '缺失')}] {str(it.get('title'))[:40]}")
        if g.get("all_issues_closed"):
            for iid, it in issues.items():
                if it.get("status") not in ("verified", "closed"):
                    miss_issue.append(f"{iid} [{it.get('status')}] {str(it.get('title'))[:40]}")
        for k in g.get("decisions", []):
            if not _decision_done(k):
                n = pm_needs.get(k) or {}
                miss_dec.append(f"{k} (waiting_on={n.get('waiting_on', 'agent')}, due={n.get('due', '-')})")
        # ★routing 判据 (G1): 板子必须**真的布完线**才算定稿
        if g.get("routing_required"):
            lay = _load_layout_stamp()
            if not lay:
                miss_meas.append("PCB **未布线** (unconnected=353 → 需 0) ⇒ 这份 Gerber 不能下单 (ISS-181)")
            elif lay.get("unconnected", 1) != 0 or lay.get("drc_violations", 1) != 0:
                miss_meas.append("PCB 布线未达标: unconnected=%s (需 0) · DRC 违规=%s (需 0) (ISS-181)"
                                 % (lay.get("unconnected"), lay.get("drc_violations")))
        defer_meas = []
        for mid in g.get("measurements", []):
            m = needed.get(mid) or {}
            # ★2026-11-04: measurements.yaml 里标了 deferred 的项 **不进当期门禁** (挪到整机阶段)
            if m.get("deferred"):
                defer_meas.append(f"{mid} {m.get('name','')} → 延后: {m.get('deferred_to') or m.get('note','')[:60]}")
                continue
            if not meas_done(mid):
                have_m = have.get(mid)
                if have_m and str(have_m.get("kind")) != "实测":
                    miss_meas.append(f"{mid} 只有[{have_m.get('kind')}]值, 必须实测")
                else:
                    miss_meas.append(f"{mid} {m.get('name', '')} ({m.get('unit', '')})")
        total = len(miss_issue) + len(miss_dec) + len(miss_meas)
        results.append({"gate": g, "miss_issue": miss_issue, "miss_dec": miss_dec,
                        "miss_meas": miss_meas, "defer_meas": defer_meas,
                        "missing": total, "passed": total == 0})

    # ★deferred 的关不参与"当前关"判定 (当期路线直接跨过去) —— 但缺口照样列出来
    cur = next((r for r in results if not r["passed"] and not r["gate"].get("deferred")), None)
    passed = [r["gate"]["id"] for r in results if r["passed"]]
    nxt = None
    if cur:
        i = [g["id"] for g in GATES].index(cur["gate"]["id"])
        nxt = GATES[i + 1] if i + 1 < len(GATES) else None

    if args.json:
        print(json.dumps({
            "current_gate": cur["gate"]["id"] if cur else "G4-done",
            "passed_gates": passed,
            "results": [{"gate": r["gate"]["id"], "name": r["gate"]["name"], "passed": r["passed"],
                         "deferred": bool(r["gate"].get("deferred")),
                         "deferred_note": r["gate"].get("deferred_note"),
                         "missing": r["missing"], "miss_issue": r["miss_issue"],
                         "miss_dec": r["miss_dec"], "miss_meas": r["miss_meas"],
                         "defer_meas": r.get("defer_meas") or []} for r in results],
        }, ensure_ascii=False, indent=2))
        return 0 if cur is None else 1

    print("=" * 74)
    print("阶段门 · Stage Gate —— 项目有序推进的唯一依据")
    print("=" * 74)
    for r in results:
        g = r["gate"]
        if r["gate"].get("deferred"):
            mark = "⏸️  已延后 (当期不做)"
        elif r["passed"]:
            mark = "✅ 通过"
        else:
            mark = "⏸️  当前关" if r is cur else "⏳ 未到"
        print(f"\n【{g['id']}】{g['name']}  —  {mark}   缺 {r['missing']} 项")
        print(f"      为什么要这一关: {g['why']}")
        if r["gate"].get("deferred"):
            print(f"      ★延后理由: {r['gate'].get('deferred_note')}")
        if r["miss_issue"]:
            print(f"      ▸ 问题单未闭环 ({len(r['miss_issue'])}):")
            for x in r["miss_issue"][:8]:
                print(f"          - {x}")
            if len(r["miss_issue"]) > 8:
                print(f"          ... 另 {len(r['miss_issue'])-8} 条")
        if r["miss_dec"]:
            print(f"      ▸ 老板拍板项未答 ({len(r['miss_dec'])}):")
            for x in r["miss_dec"]:
                print(f"          - {x}")
        if r["miss_meas"]:
            print(f"      ▸ 缺实测数据 ({len(r['miss_meas'])}):")
            for x in r["miss_meas"]:
                print(f"          - {x}")
        if r.get("defer_meas"):
            print(f"      ▸ 本关内已延后的实测项 ({len(r['defer_meas'])}):")
            for x in r["defer_meas"]:
                print(f"          - {x}")
    if DEFERRED_MEASUREMENTS:
        print("\n⏸  延后到整机/量产阶段的实测项 (**没删, 只是不在当期验收范围**):")
        for k, v in DEFERRED_MEASUREMENTS.items():
            print(f"    - {k}: {v}")
    print()
    skipped = [r["gate"]["id"] for r in results if r["gate"].get("deferred")]
    if cur:
        print(f"▶ 当前在 **{cur['gate']['id']} {cur['gate']['name']}**, 还差 **{cur['missing']}** 项才能进下一关"
              + (f" ({nxt['id']} {nxt['name']})" if nxt else "")
              + (f"\n   ★**已跳过延后关**: {', '.join(skipped)} (当期不做, 缺口 {sum(r['missing'] for r in results if r['gate'].get('deferred'))} 项留着, 到整机阶段回来)" if skipped else ""))
    else:
        print("▶ 全部阶段门已通过 → 进入最终交付")
    return 0 if cur is None else 1


if __name__ == "__main__":
    sys.exit(main())
