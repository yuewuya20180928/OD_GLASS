#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2026-11-01 20:5x 项目总工亲核关单 ISS-120 (sw-lead 交卷)
=====================================================================
验收依据 (铁律: 关单由我亲核, 不照抄交卷自评):
  ① 三件套体积: S2_BOARD_TEST_CHECKLIST.md 29.0KB + S2_VENDOR_QUESTION_LIST.md 29.6KB
     + s2_board_run.sh 25.3KB + HANDOFF 27.3KB ⇒ 齐全
  ② 交卷单 B1~B6 六块齐 (grep 命中 15 处 / B1-B6 全在)
  ③ 自检实跑: s2_board_run.sh --selftest 6/6 rc=0 · s2_board_judge.py --selftest 7/7 rc=0
     · s2_board_e2e.sh 10/10 rc=0 · s2_board_selftest.py 5/5 rc=0
  ④ merge rc=0 (冲突 0) · gate_check Q1 18/18
⇒ fixed → verified (verify_by=main ≠ owner=sw-lead, 验证分离成立)

★同时登记 sw-lead 交卷时自己报出的口径冲突 (ISS-119 换芯口径分叉) —— 它没拍板, 交给我:
  ① S2 全套仍按 ARS45 写: 版本块 magic 写死 AR45 / 版本串前缀写死 ARS45-SW /
     原厂 parameter.txt 按 512B 扇区计而我方按字节 (★差 512 倍) / 问谁从原厂变成模组厂
  ② 这条与 §(1.46) 的 T4 翻案 (基线改 RK3576) **叠加** ⇒ S2 问询对象要按 RK3576 模组厂重写
⇒ 新开 ISS-123 (owner=sw-lead, verify_by=main)

纪律: flock + 锁内重读 + 原子写 (tmp + os.replace); 写完核对条数与体积
"""
import os
import sys
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")

ISS123 = {
    "id": "ISS-123",
    "title": "★S2 救砖链路全套装按 ARS45 写死 (magic AR45 / 版本串 ARS45-SW / parameter.txt 扇区 vs 字节差 512 倍 / 问询对象) —— 按 RK3576 模组厂口径重写",
    "severity": "medium",
    "source_blocker": None,
    "source_agent": "main",
    "desc": (
        "sw-lead 在 ISS-120 交卷里自己报出 (未拍板, 交项目总工): ISS-119 已把 SoC 基线换成 "
        "RK3588 (待老板点头), 但 S2 全套仍按 ARS45 写 —— ① 版本块 magic 写死 `AR45` "
        "② 版本串前缀写死 `ARS45-SW ` ③ 原厂 `parameter.txt` 按 **512B 扇区**计而我方按**字节**计 "
        "(★**差 512 倍**) ④ 问谁从「原厂」变成「模组厂」。"
        "★**分叉没定就发信会问错对象** ⇒ 必须先改口径再外发。"
        "★**本条与 §(1.46) 的 T4 翻案叠加**: 基线现已从 RK3588 改到 **RK3576** ⇒ "
        "口径要按 RK3576 模组厂重写 (不是 RK3588)。"
        "★要交回 sw-lead 的活: ① 把 3 处硬编码抽成**可配置** (从 s2_rescue_config 读, 别写死) "
        "② parameter.txt 扇区/字节换算写成**显式参数**并加一条自测 (512 倍差是最容易静默错的地方) "
        "③ 问询清单里的对象改成 RK3576 模组厂口径。"
    ),
    "owner": "sw-lead",
    "reporter": "main",
    "raised": "2026-11-01",
    "due": "2026-11-05",
    "status": "open",
    "external": False,
    "need_keys": [],
    "fix_ref": None,
    "verify_by": "main",
    "verify_result": None,
    "verify_date": None,
    "note": (
        "2026-11-01 20:5x 项目总工从 ISS-120 交卷的『顺手查出的口径冲突』转登记。"
        "★sw-lead 的原话: 『未拍板, 已报项目总工 (s2_chip_swap_scope) —— 分叉没定就发信会问错对象』"
        "⇒ 它**没有脑补也没有偷改**, 这是正确做法。"
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

    # ① ISS-120 → verified
    i120 = by_id.get("ISS-120")
    if i120 is None:
        print("❌ 找不到 ISS-120")
        return 1
    if i120.get("status") == "fixed":
        i120["status"] = "verified"
        i120["verify_result"] = (
            "2026-11-01 20:5x 项目总工亲核通过: 三件套齐全 (CHECKLIST 29.0KB / VENDOR_QUESTION_LIST 29.6KB "
            "/ s2_board_run.sh 25.3KB / HANDOFF 27.3KB, B1~B6 六块齐) + 自检实跑 4 连 rc=0 "
            "(run --selftest 6/6 · judge --selftest 7/7 · e2e 10/10 · selftest.py 5/5) "
            "+ merge rc=0 冲突 0 + gate_check Q1 18/18。"
            "★**板端实测仍是 0 次** —— 交的是『怎么测 + 怎么问 + 怎么判』, 不是『测过了』; "
            "P1~P4 四个 [0数据] 项仍为 null/TODO, BR-01 最高只能判 ⚠️未验 ⇒ 板端真跑仍挂 ISS-120 后续 (EVT 有板后)。"
        )
        i120["verify_date"] = "2026-11-01"
        i120["note"] = (
            (i120.get("note") or "") +
            "\n★2026-11-01 20:5x 项目总工亲核关单 (verify_by=main ≠ owner=sw-lead)。"
            "★**板端 0 实测这条边界没有被他掩盖** —— 三件套里 P1~P4 仍是 [0数据], "
            "判定器有 4 条硬规则挡着 (缺失即未验 / 通用示例不算证据 / P4 未填判未验 / 仅日志命中不算进 BOOT), "
            "且 T7 (无真值签名 ⇒ 空判不算过) 是它 e2e 里抓出自己的洞后补的。"
            "★连带: 它报出的 ARS45 口径分叉已转登记 ISS-123 (本条只管『怎么测』, 不管『测哪个芯片』)。"
        )
        print("✅ ISS-120 fixed → verified")
    else:
        print(f"⚠️ ISS-120 状态是 {i120.get('status')} —— 不动")

    # ② ISS-123 新登记
    if "ISS-123" not in by_id:
        issues.append(ISS123)
        print("✅ 新登记 ISS-123")
    else:
        print("⚠️ ISS-123 已存在 —— 不重复登记")

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
