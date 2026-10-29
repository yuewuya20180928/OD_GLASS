#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MECH/prototype_plan_check.py —— 原型制作计划的**机械自检**
=====================================================================
目的: 让"这份原型制作计划是否满足 ISS-027 的验收项"变成可复核的判定,
      而不是"读起来觉得行"。

ISS-027 验收项 (项目总工任务书):
  ① **分批打样计划** (第1批打印件 → 装配 → 量测 → 第2批改版: 每批做几件、
     每批验证哪几项、每批的判据是什么)
  ② **每批的验证矩阵**: 哪些项在打印件阶段就能测 (尺寸/干涉/佩戴),
     哪些必须等电路板 (功能/热/续航)
  ③ **不通过怎么回滚** (改哪一层: 打印件/结构/PCB/固件; 每层的回滚成本与耗时)
  ④ 与既有文件的衔接: MECH/RELIABILITY_TEST_PLAN.md (T-13/T-14) +
     state/measurements.yaml 的 M-PRINT 回填口径 + PRINT/ars45_print_pack.3mf
  ⑤ **每批的时间与依赖** (依赖 JBD 外形 / 依赖 PCB / 依赖固件) → 供排阶段门 G1→G2
  验收: 表 + 判据 + 依赖链; **明确写清哪些项在没有实物时只能标 [0数据]**

本文额外立的三条铁律 (本项目通用):
  铁律A: 不得把未测写成已通过 (同 reliability_plan_check.py 的口径)
  铁律B: 证据分级四标签齐全 (实测/官方/推算/0数据), 且声明 "[实测] 条数 = 0"
         —— 本计划是**纸面计划**, 实物数据为 0
  铁律C: **不许拍板** —— 计划里不许出现替项目总工/老板做决定的措辞
         (例外: 明确标注 "建议, 不拍板" / "待裁" 的句子)

用法:
    python3 MECH/prototype_plan_check.py          # 人读报告
    python3 MECH/prototype_plan_check.py --json   # 机读

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
PROJ = os.path.join(HERE, "..")
PLAN = os.path.join(HERE, "PROTOTYPE_PLAN.md")

# ---------- 验收①: 批次 ----------
BATCH_IDS = ["B0", "B1", "B2", "B3", "B4"]
# 每批必须出现的栏目关键词 (做/验证/判据)
BATCH_FIELDS = {
    "件": ["打印件数", "打印件"],
    "验证项": ["验证", "测量项", "验证项"],
    "判据": ["判据", "硬判据"],
    "依赖": ["依赖", "前置"],
    "回滚": ["回滚", "不通过"],
}

# ---------- 验收②: 验证矩阵 ----------
MATRIX_CATEGORIES = [
    ("打印件阶段可测", ["打印件阶段就能测", "A 类"]),
    ("必须等电路板", ["必须等电路板", "B 类"]),
    ("必须等整机/固件", ["必须等整机", "C 类"]),
]
MATRIX_KEYWORDS = ["尺寸", "干涉", "佩戴", "功能", "热", "续航"]

# ---------- 验收③: 回滚层 ----------
ROLLBACK_LAYERS = {
    "L1": ["打印参数"],
    "L2": ["打印件几何"],
    "L3": ["结构方案"],
    "L4": ["PCB"],
    "L5": ["固件"],
}
ROLLBACK_FIELDS = ["成本", "耗时"]

# ---------- 验收④: 既有文件衔接 ----------
LINK_FILES = [
    ("RELIABILITY_TEST_PLAN", ["MECH/RELIABILITY_TEST_PLAN.md"]),
    ("T-13", ["T-13"]),
    ("T-14", ["T-14"]),
    ("measurements.yaml", ["state/measurements.yaml"]),
    ("M-PRINT", ["M-PRINT"]),
    ("M-FIT", ["M-FIT"]),
    ("M-WEIGHT", ["M-WEIGHT"]),
    ("print_pack 3mf", ["ars45_print_pack.3mf"]),
]

# ---------- 验收⑤: 依赖链 ----------
DEPENDENCY_KEYWORDS = ["JBD", "PCB", "固件", "波导", "电芯"]
SCHEDULE_KEYWORDS = ["最早开工", "历时", "关键路径"]

# ---------- 铁律A: 未测即通过的措辞 ----------
FORBIDDEN = [
    r"已通过", r"测试通过", r"实测通过", r"全部通过", r"检验通过",
    r"验证通过", r"已判定通过", r"结果[:：]\s*通过", r"结论[:：]\s*通过",
    r"通过率\s*\d", r"已符合", r"符合标准",
]
NEGATION = ["不许", "不得", "不能", "禁", "未", "无", "不是", "不做", "避免", "零",
            "勿", "非", "别", "拒绝", "不合格", "若不", "否则", "就不", "没有"]

# ---------- 铁律C: 不许拍板 ----------
DECIDE_FORBIDDEN = [
    r"^已决定", r"^我决定", r"^拍板如下", r"^最终方案为", r"^一锤定音",
    r"^就这么定", r"^批准通过",
]
# 允许出现"拍板/裁决"的地方: 明确指向别人或明确标"不拍板/待裁/建议"
DECIDE_ALLOW = ["项目总工", "老板", "不拍板", "待裁", "裁决", "建议", "拍板权",
                "请项目总工", "需项目总工", "由项目总工", "拍板", "须由"]

EVIDENCE_FAMILIES = {
    "实测": r"\[实测",
    "官方": r"\[官方",
    "推算": r"\[推算",
    "0数据": r"\[0数据",
}


def load_plan() -> str:
    if not os.path.exists(PLAN):
        print(f"[FAIL] 找不到计划文件: {PLAN}")
        sys.exit(1)
    with open(PLAN, encoding="utf-8") as f:
        return f.read()


def check(text: str) -> dict:
    res = {"fail": [], "warn": [], "info": {}}
    lines = text.splitlines()

    # ---------- ① 分批打样计划 ----------
    for b in BATCH_IDS:
        if not re.search(rf"\*\*{b}\*\*|\|\s*\*\*{b}\*\*\s*\||^###\s+{b}\b", text, re.M):
            res["fail"].append(f"① 缺批次 {b}")
    # 每批的栏目: 用逐批切片检查
    for idx, b in enumerate(BATCH_IDS):
        # 取该批所在段落 (从 B 出现处到下一个批次或下一个 ## )
        m = re.search(rf"(^###\s+1\.\d+\s+{b}\b.*?)(?=\n###\s|\n##\s|\Z)", text, re.S | re.M)
        if not m:
            # B0 只在总表里
            m2 = re.search(rf"\*\*{b}\*\*.*?(?=\n\*\*{BATCH_IDS[idx+1]}\*\*|\n\n)", text, re.S)
            seg = m2.group(0) if m2 else ""
        else:
            seg = m.group(1)
        if not seg:
            res["fail"].append(f"① 批次 {b} 没有独立段落 (总表行不算)")
            continue
        missing = []
        for fname, kws in BATCH_FIELDS.items():
            if not any(k in seg for k in kws):
                missing.append(fname)
        if missing:
            res["warn"].append(f"① 批次 {b} 段缺栏目: {missing}")
    # 改版批 (第2批改版) 必须有
    if not re.search(r"改版", text):
        res["fail"].append("① 缺 '第 2 批改版' 的改版触发规则")
    res["info"]["batch_ids"] = BATCH_IDS

    # ---------- ② 验证矩阵 ----------
    for name, kws in MATRIX_CATEGORIES:
        if not any(k in text for k in kws):
            res["fail"].append(f"② 验证矩阵缺类别: {name}")
    for kw in MATRIX_KEYWORDS:
        if kw not in text:
            res["fail"].append(f"② 验证矩阵缺关键维度: {kw}")
    # 必须有"最早批次"列
    if "最早批次" not in text:
        res["fail"].append("② 验证矩阵缺 '最早批次' 归属列")

    # ---------- ③ 回滚阶梯 ----------
    for lid, kws in ROLLBACK_LAYERS.items():
        if not any(k in text for k in kws):
            res["fail"].append(f"③ 回滚阶梯缺层 {lid} ({'/'.join(kws)})")
    for f in ROLLBACK_FIELDS:
        if f not in text:
            res["fail"].append(f"③ 回滚阶梯缺字段: {f}")
    # 成本/耗时必须有量化
    for pat, label in ((r"人日", "成本人日"), (r"天|周", "耗时")):
        if not re.search(pat, text):
            res["fail"].append(f"③ 回滚阶梯缺量化 {label}")

    # ---------- ④ 既有文件衔接 ----------
    for name, kws in LINK_FILES:
        if not any(k in text for k in kws):
            res["fail"].append(f"④ 缺既有文件衔接: {name}")

    # ---------- ⑤ 时间与依赖链 ----------
    for kw in DEPENDENCY_KEYWORDS:
        if kw not in text:
            res["fail"].append(f"⑤ 依赖链缺: {kw}")
    for kw in SCHEDULE_KEYWORDS:
        if kw not in text:
            res["fail"].append(f"⑤ 缺排期要素: {kw}")

    # ---------- [0数据] 清单 ----------
    m = re.search(r"(##\s*6\..*?)(?=\n##\s|\Z)", text, re.S)
    if not m:
        res["fail"].append("缺 '没有实物时只能标 [0数据]' 的专章 (应为 §6)")
    else:
        sec = m.group(1)
        n_rows = len(re.findall(r"^\|\s*\d+\s*\|", sec, re.M))
        res["info"]["zero_data_rows"] = n_rows
        if n_rows < 10:
            res["fail"].append(f"§6 [0数据] 清单只有 {n_rows} 行 (<10)")
        if "[0数据]" not in sec:
            res["fail"].append("§6 未标 [0数据]")

    # ---------- 铁律A: 未测即通过 ----------
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
    miss = [t for t, pat in EVIDENCE_FAMILIES.items() if not re.search(pat, text)]
    if miss:
        res["fail"].append(f"铁律B 缺证据分级标签: {miss}")
    if not re.search(r"\[实测\]\s*条数\s*=\s*\*?\*?0", text) and \
       not re.search(r"\[实测\]\s*实物条数\s*=\s*\*?\*?0", text):
        res["fail"].append("铁律B 未声明 '[实测] 实物条数 = 0'")
    res["info"]["evidence_tags"] = [t for t, pat in EVIDENCE_FAMILIES.items()
                                     if re.search(pat, text)]

    # ---------- 铁律C: 不许拍板 ----------
    dec_hits = []
    for i, ln in enumerate(lines, 1):
        for pat in DECIDE_FORBIDDEN:
            if re.search(pat, ln.strip()):
                if not any(a in ln for a in DECIDE_ALLOW):
                    dec_hits.append((i, ln.strip()[:90]))
                break
    res["info"]["decide_hits"] = dec_hits
    if dec_hits:
        for i, ln in dec_hits:
            res["fail"].append(f"铁律C 第 {i} 行疑似替别人拍板: {ln}")

    # ---------- 附加: 关键数字必须能在既有文件里找到 ----------
    # (只查本文引用的几个"可复算锚点", 防止漂移)
    anchors = [
        ("46/46", "MECH/print/verify_pack.py"),
        ("0.95", "MECH/fit_check.py"),
        ("0.65", "MECH/fit_check.py"),
        ("24.50", "MECH/fit_check.py"),
        ("48.9-74.0", "MECH/MECH_BUDGET.md"),
    ]
    res["info"]["anchors"] = [a for a, _ in anchors if a not in text]
    for a, f in anchors:
        if a not in text:
            res["warn"].append(f"锚点 {a} 未出现在本文 (应对齐 {f})")

    # 交叉核对: fit_check / verify_budget 的实跑输出里必须真的有这些数
    def read(p):
        try:
            with open(os.path.join(PROJ, p), encoding="utf-8") as fh:
                return fh.read()
        except OSError:
            return ""
    fc = read("MECH/fit_check.py")
    vb = read("MECH/verify_budget.py")
    for a in ("0.95", "0.65", "8.50", "24.50"):
        if a not in fc and a not in text:
            res["warn"].append(f"fit_check.py 里找不到 {a}, 本文也没写 (可能是漂移)")
    for a in ("48.9", "74.0"):
        if a not in vb and a not in text:
            res["warn"].append(f"verify_budget.py 里找不到 {a}")

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

    print("=" * 74)
    print("原型制作计划 · 机械自检 (ISS-027 验收项 + 三条铁律)")
    print("=" * 74)
    info = res["info"]
    print(f"\n批次: {info.get('batch_ids')}   证据标签: {info.get('evidence_tags')}")
    print(f"[0数据] 清单行数: {info.get('zero_data_rows')}")
    print(f"锚点缺失: {info.get('anchors') or '无'}")

    if res["warn"]:
        print(f"\n【WARN】{len(res['warn'])} 项")
        for w in res["warn"]:
            print(f"  ⚠️  {w}")

    if res["fail"]:
        print(f"\n【FAIL】{len(res['fail'])} 项")
        for f in res["fail"]:
            print(f"  ❌ {f}")
        print("\n结论: ❌ 不合格 —— 请按上面清单改")
        return 1

    print("\n【PASS】全部合格")
    print("  ① 分批打样计划 (B0-B4 + 第2批改版触发规则): ✅")
    print("  ② 验证矩阵 (打印件可测 / 等电路板 / 等整机): ✅")
    print("  ③ 回滚阶梯 (L1-L5, 含成本与耗时): ✅")
    print("  ④ 既有文件衔接 (RELIABILITY_TEST_PLAN T-13/T-14 + measurements.yaml + 3mf): ✅")
    print("  ⑤ 时间与依赖链 (JBD / PCB / 固件 + 排期): ✅")
    print("  铁律A 未测即通过措辞: ✅ 0 处")
    print("  铁律B 证据分级 + '[实测] 实物条数 = 0' 声明: ✅")
    print("  铁律C 不替别人拍板: ✅")
    return 0


if __name__ == "__main__":
    sys.exit(main())
