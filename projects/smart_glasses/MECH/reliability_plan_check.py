#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MECH/reliability_plan_check.py —— 可靠性测试方案的**机械自检**
=====================================================================
目的: 让"这份方案是否满足验收标准"变成可复核的判定, 而不是"读起来觉得行"。

它检查的是 **ISS-026 的验收①②③** + 三条铁律:
  ① ≥8 类用例, 且 8 类必选 (跌落/扭转/弯折/拉力/汗液/化妆品/酒精/UV) 全覆盖
  ② 每类用例都有 样品数 / 次数 / 判据 三要素
  ③ 明确区分 "1 台样机阶段" 与 "后续批次"
  铁律A: 全文不得出现把未测写成已通过的措辞 (已通过/测试通过/实测通过/...)
  铁律B: 证据分级四标签齐全 (实测/官方/推算/0数据), 且本文声明 [实测] 条数 = 0
  铁律C: 每张用例卡都要写"1 台可行性" (✅/⚠️/❌) —— 否则单台/批次的边界不清

用法:
    python3 MECH/reliability_plan_check.py          # 人读报告
    python3 MECH/reliability_plan_check.py --json   # 机读

退出码: 0 = 全过 ; 1 = 有不合格项
=====================================================================
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
PLAN = os.path.join(HERE, "RELIABILITY_TEST_PLAN.md")

# 8 类必选用例 → 期望的用例标题关键词 (任一命中即可)
MANDATORY = [
    ("跌落", ["跌落"]),
    ("扭转", ["扭转"]),
    ("弯折(镜腿反复开合)", ["弯折", "开合"]),
    ("镜腿拉力", ["拉力"]),
    ("汗液浸泡", ["汗液"]),
    ("化妆品", ["化妆品"]),
    ("酒精擦拭", ["酒精"]),
    ("UV老化", ["UV"]),
]

# 用例卡必备栏位
REQUIRED_FIELDS = ["样品数", "次数", "判据", "1 台可行性"]

# 把"没测的写成已通过"判死的措辞
FORBIDDEN = [
    r"已通过", r"测试通过", r"实测通过", r"全部通过", r"检验通过",
    r"验证通过", r"已判定通过", r"结果[:：]\s*通过", r"结论[:：]\s*通过",
    r"通过率\s*\d", r"已符合", r"符合标准",
]
# 否定/免责语境 → 允许出现上述词
NEGATION = ["不许", "不得", "不能", "禁", "未", "无", "不是", "不做", "避免", "零",
            "勿", "非", "别", "拒绝", "不合格"]

EVIDENCE_TAGS = ["[实测]", "[官方]", "[推算]", "[0数据]"]
# 标签族 (接受 "[官方-厂商页]" "[官方-项目内]" "[0数据-同类通用]" 这类带后缀的写法)
EVIDENCE_FAMILIES = {
    "实测": r"\[实测",
    "官方": r"\[官方",
    "推算": r"\[推算",
    "0数据": r"\[0数据",
}

CASE_RE = re.compile(r"^###\s+(T-\d+)\s+(.*)$")


def load_plan() -> str:
    if not os.path.exists(PLAN):
        print(f"[FAIL] 找不到方案文件: {PLAN}")
        sys.exit(1)
    with open(PLAN, encoding="utf-8") as f:
        return f.read()


def split_cases(text: str) -> list:
    """把 '### T-xx' 段落切成 dict: {id, title, body, line_no}"""
    lines = text.splitlines()
    cases, cur = [], None
    for i, ln in enumerate(lines):
        m = CASE_RE.match(ln)
        if m:
            if cur:
                cur["body"].append("")     # 段尾空行 → 便于判字段
                cases.append(cur)
            cur = {"id": m.group(1), "title": m.group(2), "line_no": i + 1,
                   "body": [ln]}
        elif cur is not None:
            cur["body"].append(ln)
    if cur:
        cur["body"].append("")
        cases.append(cur)
    for c in cases:
        c["text"] = "\n".join(c["body"])
    return cases


def check(text: str) -> dict:
    res = {"fail": [], "warn": [], "info": {}}
    lines = text.splitlines()

    # ---------- ① 用例数与必选覆盖 ----------
    cases = split_cases(text)
    res["info"]["case_count"] = len(cases)
    if len(cases) < 8:
        res["fail"].append(f"① 用例数 {len(cases)} < 8 (验收要求至少 8 类)")

    covered = {}
    for name, kws in MANDATORY:
        hit = None
        for c in cases:
            if any(k in c["title"] for k in kws):
                hit = c
                break
        covered[name] = hit["id"] if hit else None
        if hit is None:
            res["fail"].append(f"① 必选用例缺失: {name}")
    res["info"]["mandatory_coverage"] = covered

    # ---------- ② 每类三要素 ----------
    for c in cases:
        missing = [f for f in REQUIRED_FIELDS if f not in c["text"]]
        if missing:
            res["fail"].append(f"② {c['id']} ({c['title']}) 缺字段: {missing}")

    # ---------- ③ 单台 vs 批次 分配 ----------
    if "1 台样机阶段" not in text or "后续批次" not in text:
        res["fail"].append("③ 缺 '1 台样机阶段' / '后续批次' 的分配表述")
    alloc = [c["id"] for c in cases if c["id"] in text.split("### B3.2")[1].split("###")[0]
             if "### B3.2" in text]
    if not alloc:
        # B3.2 标题可能带装饰字符 → 用宽松匹配再试一次
        m = re.search(r"###\s*B3\.2(.*?)(?=\n###\s|\n##\s)", text, re.S)
        if m:
            alloc = [c["id"] for c in cases if c["id"] in m.group(1)]
    res["info"]["allocation_cases"] = alloc
    missing_alloc = [c["id"] for c in cases if c["id"] not in alloc]
    if missing_alloc:
        res["fail"].append(f"③ 分配表 §B3.2 未覆盖用例: {missing_alloc}")

    # ---------- 铁律A: 不得把未测写成已通过 ----------
    hits = []
    for i, ln in enumerate(lines, 1):
        for pat in FORBIDDEN:
            if re.search(pat, ln):
                if not any(n in ln for n in NEGATION):
                    hits.append((i, pat, ln.strip()[:90]))
                break
    res["info"]["forbidden_hits"] = hits
    if hits:
        for i, pat, ln in hits:
            res["fail"].append(f"铁律A 第 {i} 行出现未测即通过措辞 [{pat}]: {ln}")

    # ---------- 铁律B: 证据分级 ----------
    miss_tags = [t for t, pat in EVIDENCE_FAMILIES.items()
                 if not re.search(pat, text)]
    if miss_tags:
        res["fail"].append(f"铁律B 缺证据分级标签: {miss_tags}")
    if not re.search(r"\[实测\]\s*条数\s*=\s*0", text):
        res["fail"].append("铁律B 未声明 '[实测] 条数 = 0'")
    res["info"]["evidence_tags"] = [t for t, pat in EVIDENCE_FAMILIES.items()
                                     if re.search(pat, text)]

    # ---------- 铁律C: 每卡都要有单台可行性判定 ----------
    for c in cases:
        m = re.search(r"\*\*1 台可行性\*\*\s*\|\s*([✅⚠️❌])", c["text"])
        if not m:
            # 表格里也可能是 '| ✅ |' 形式
            if not re.search(r"\*\*1 台可行性\*\*.*[✅⚠️❌]", c["text"]):
                res["fail"].append(f"铁律C {c['id']} 的 '1 台可行性' 没有 ✅/⚠️/❌ 判定")
            else:
                res["info"].setdefault("feasibility", {})[c["id"]] = "表内"
        else:
            res["info"].setdefault("feasibility", {})[c["id"]] = m.group(1)

    # ---------- 附加: 判据要可量化 ----------
    for c in cases:
        if "判据" in c["text"] and not re.search(r"[≤≥<>=]\s*[+\-±]?\s*\d", c["text"]):
            res["warn"].append(f"{c['id']} 判据里没找到量化阈值 (可能不可复核)")

    return res


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    text = load_plan()
    res = check(text)

    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2, default=str))
        return 1 if res["fail"] else 0

    info = res["info"]
    print("=" * 70)
    print("MECH/RELIABILITY_TEST_PLAN.md 机械自检")
    print("=" * 70)
    print(f"用例数            : {info.get('case_count')} (要求 ≥8)")
    print("必选覆盖          : " + ", ".join(f"{k}={v}" for k, v in (info.get("mandatory_coverage") or {}).items()))
    print(f"每卡三要素         : 样品数 / 次数 / 判据 / 1 台可行性  → 已逐卡检查")
    print(f"分配表 §B3.2 覆盖 : {len(info.get('allocation_cases') or [])} 个用例")
    print(f"证据分级标签       : {info.get('evidence_tags')}")
    print(f"单台可行性判定     : {info.get('feasibility')}")
    print(f"禁用措辞命中       : {len(info.get('forbidden_hits') or [])} 处 (期望 0)")
    if res["warn"]:
        print("\n[WARN]")
        for w in res["warn"]:
            print(f"  · {w}")
    if res["fail"]:
        print("\n[FAIL]")
        for f in res["fail"]:
            print(f"  · {f}")
        print("\n结论: ❌ 不合格")
        return 1
    print("\n结论: ✅ 全部通过 (方案齐备性检查, 不代表任何实测已通过)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
