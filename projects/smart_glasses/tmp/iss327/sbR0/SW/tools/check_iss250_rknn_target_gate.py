#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_iss250_rknn_target_gate.py — ISS-250 机器门禁 (查证表 / 降级方案 / 判据口径)
=====================================================================
判据 (三条, 全部机器可判):
  G1 查证表**每一条**都带证据等级, 且等级只能是五级之一:
     [官网] / [实测] / [媒体] / [推算] / [0数据]
  G2 查证表**至少覆盖任务书点名的 4 条命题**:
     ① rknn-toolkit2 各版本 target 列表里有没有 rk3572
     ② 有没有「rk3576 转出来的 .rknn 在 RK3572 上跑得动」的官方说明/已知结论
     ③ RK3572 的 NPU 与 RK3576 的差异
     ④ 官方 model zoo 有没有 RK3572 预编译模型
  G3 **降级方案 ≥ 2 条**, 且**每条**都带「代价 / 启用前提 / 谁拍」三要素
  G4 ★**判据不许写「等回信」类话** ★ (老板 2026-11-11 19:31 + 2026-11-12 02:02:
     不再发信, 全靠自己查资料 ⇒ 缺口一律【自己查的结果 + 证据等级 + 降级方案】)

用法:
    python3 SW/tools/check_iss250_rknn_target_gate.py            # 查真实文件
    python3 SW/tools/check_iss250_rknn_target_gate.py --selftest  # 反向用例
    python3 SW/tools/check_iss250_rknn_target_gate.py --file <path>

★本脚本只读, 不改任何被检文件。
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))
DEFAULT_FILE = os.path.join(
    PROJ, "SW", "research", "ISS250_rknn_toolkit2_target_查证表.md"
)

EVIDENCE_TAGS = ["[官网]", "[实测]", "[媒体]", "[推算]", "[0数据]"]
# 任务书点名的 4 条命题 (每条给一组关键词, 命中任一即算覆盖)
PROPOSITIONS = {
    "P1_target_list_has_rk3572": [
        "RK3572 是否在 target 列表中", "target_platform='rk3572'", "合法 target",
    ],
    "P2_official_cross_chip_statement": [
        "官方有没有说", "rk3576 转出来的 .rknn 能否在 RK3572 上跑通",
        "rk3576 转出来的 .rknn 能在 RK3572 上跑通",
    ],
    "P3_npu_diff_3572_vs_3576": [
        "RK3572 与 RK3576 的 NPU 差异", "RK3572 与 RK3576 的 NPU 算力差", "TOPS",
    ],
    "P4_model_zoo_prebuilt": [
        "官方 model zoo 里有没有 RK3572 预编译模型", "model zoo",
    ],
}
# 判据里禁止出现的「等外部回复」类话
BANNED = [
    "等回信", "等原厂回信", "待原厂确认", "等原厂确认", "等外部确认",
    "待外部回复", "等回复", "pending vendor", "await vendor",
]


def _rows(text: str, prefix: str):
    """取表格里以 | **prefix 开头的行 (查证表行 / 降级方案行)。"""
    out = []
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("| **" + prefix):
            out.append(s)
    return out


def check_text(text: str) -> dict:
    res = {}

    # ---- G1 每条查证行都有证据等级
    ev_rows = _rows(text, "E-")
    bad = []
    for r in ev_rows:
        if not any(t in r for t in EVIDENCE_TAGS):
            m = re.match(r"\|\s*\*\*(E-[0-9a-zA-Z]+)\*\*", r)
            bad.append(m.group(1) if m else r[:40])
    res["G1_evidence_per_row"] = {
        "ok": bool(ev_rows) and not bad,
        "rows": len(ev_rows),
        "bad": bad,
        "msg": f"查证行 {len(ev_rows)} 条, 缺证据等级 {len(bad)} 条" + (f" ({bad})" if bad else ""),
    }

    # ---- G2 4 条命题覆盖
    miss = []
    for name, kws in PROPOSITIONS.items():
        if not any(k in text for k in kws):
            miss.append(name)
    res["G2_four_propositions"] = {
        "ok": not miss,
        "miss": miss,
        "msg": f"4 条必答命题缺 {len(miss)} 条" + (f" ({miss})" if miss else " ⇒ 全覆盖"),
    }

    # ---- G3 降级方案 ≥2 条 且每条带代价/前提/谁拍
    dg_rows = _rows(text, "C") + _rows(text, "R")
    dg_rows = [r for r in dg_rows if "|" in r and len(r) > 20]

    def _cells(row: str):
        return [c.strip() for c in row.strip().strip("|").split("|")]

    # 列位: 0=编号 1=方案 2=判定 3=技术依据 4=量化代价 5=启用前提 6=谁拍
    no_cost, no_owner, no_cond = [], [], []
    for r in dg_rows:
        cs = _cells(r)
        if len(cs) < 7:
            no_cost.append(r[:40]); no_owner.append(r[:40]); no_cond.append(r[:40]); continue
        if not cs[4] or cs[4] in {"—", "-", "无"}:
            no_cost.append(r[:40])
        if not cs[5] or cs[5] in {"—", "-"}:
            no_cond.append(r[:40])
        if not cs[6] or cs[6] in {"—", "-"}:
            no_owner.append(r[:40])
    res["G3_downgrade_ge2"] = {
        "ok": len(dg_rows) >= 2,
        "rows": len(dg_rows),
        "msg": f"降级方案 {len(dg_rows)} 条 (要求 ≥2)",
    }
    res["G3b_downgrade_has_cost"] = {
        "ok": bool(dg_rows) and not no_cost,
        "bad": no_cost,
        "msg": f"『量化代价』列为空 {len(no_cost)} 条",
    }
    res["G3c_downgrade_has_owner"] = {
        "ok": bool(dg_rows) and not no_owner,
        "bad": no_owner,
        "msg": f"『谁拍』列为空 {len(no_owner)} 条",
    }
    res["G3d_downgrade_has_condition"] = {
        "ok": bool(dg_rows) and not no_cond,
        "bad": no_cond,
        "msg": f"『启用前提』列为空 {len(no_cond)} 条",
    }

    # ---- G4 判据不许写「等回信」
    hits = []
    for b in BANNED:
        for i, line in enumerate(text.splitlines(), 1):
            if b in line:
                hits.append((b, i))
    res["G4_no_wait_for_reply"] = {
        "ok": not hits,
        "bad": hits,
        "msg": f"『等回信』类措辞 {len(hits)} 处" + (f" ({hits})" if hits else " ⇒ 无"),
    }

    # ---- 板端判据必须存在 (不许把板端清单删掉)
    res["G5_board_checklist_present"] = {
        "ok": ("N1" in text and "N3" in text and "板端可达时的执行清单" in text),
        "msg": "板端执行清单 (N1~N5) 在位" if "板端可达时的执行清单" in text else "缺板端执行清单",
    }
    return res


def report(res: dict, path: str) -> int:
    ok = True
    print("=" * 74)
    print("ISS-250 · rknn target 查证门禁")
    print(f"被检文件: {path}")
    print("=" * 74)
    for k, v in res.items():
        good = v["ok"]
        ok = ok and good
        print(f"{'✅' if good else '❌'} {k:34s} {v['msg']}")
    print("-" * 74)
    print(f"{'PASS' if ok else 'FAIL'} (rc={'0' if ok else '1'})")
    return 0 if ok else 1


def selftest() -> int:
    """反向用例: 故意造 4 种坏文件, 门禁必须**分别**报红 (证明它真在读内容, 不是演常量)。"""
    base = open(DEFAULT_FILE, encoding="utf-8").read()
    cases = []

    # ① 抽掉一行证据等级 ⇒ G1 必须红
    lines = base.splitlines()
    bad1 = []
    for ln in lines:
        if ln.strip().startswith("| **E-") and "[实测]" in ln:
            ln = re.sub(r"★`?\[实测\]`?★?", "", ln)
        bad1.append(ln)
    cases.append(("G1 抽掉一条证据等级", "\n".join(bad1), "G1_evidence_per_row"))

    # ② 删掉降级方案行 ⇒ G3 必须红
    bad2 = [ln for ln in lines
            if not (ln.strip().startswith("| **C") or ln.strip().startswith("| **R"))]
    cases.append(("G3 删光降级方案", "\n".join(bad2), "G3_downgrade_ge2"))

    # ③ 插入「等回信」⇒ G4 必须红
    bad3 = base + "\n\n★待外部确认: 等原厂回信后再定★\n"
    cases.append(("G4 插入等原厂回信", bad3, "G4_no_wait_for_reply"))

    # ④ 删掉命题② 那行 ⇒ G2 必须红
    bad4 = [ln for ln in lines if "官方有没有说" not in ln]
    cases.append(("G2 删掉命题② 行", "\n".join(bad4), "G2_four_propositions"))

    passed = 0
    total = len(cases)
    print("=" * 74)
    print("ISS-250 · 门禁反向自测 (--selftest)")
    print("=" * 74)
    for name, content, expect_key in cases:
        res = check_text(content)
        bad = res[expect_key]["ok"] is False
        print(f"{'✅' if bad else '❌'} {name:34s} 期望 {expect_key}=FAIL ⇒ "
              f"实测 {'FAIL (符合预期)' if bad else 'PASS (门禁没抓到!)'}")
        if bad:
            passed += 1
    # 正向: 真文件必须全绿
    res = check_text(base)
    allok = all(v["ok"] for v in res.values())
    print(f"{'✅' if allok else '❌'} {'正向: 真查证表必须全绿':34s} "
          f"{'全绿' if allok else '有红项: ' + str([k for k, v in res.items() if not v['ok']])}")
    if allok:
        passed += 1
    total += 1
    print("-" * 74)
    print(f"SELFTEST {passed}/{total} 通过, rc={'0' if passed == total else '1'}")
    return 0 if passed == total else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default=DEFAULT_FILE)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    path = os.path.abspath(args.file)
    if not os.path.exists(path):
        print(f"❌ 文件不存在: {path}")
        return 2
    with open(path, encoding="utf-8", errors="ignore") as f:
        return report(check_text(f.read()), path)


if __name__ == "__main__":
    sys.exit(main())
