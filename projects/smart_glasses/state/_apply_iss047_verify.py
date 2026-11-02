#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-047 验收落盘 (项目总工 = main 独立验收 mech-lead 的交卷)
================================================================================
★铁律 (C3 验证分离): owner=mech-lead, verify_by=main ⇒ 我不是修复人, 我是验收人 ⇒ 合法。
★验收依据 (全部机械复算, 不看回执):
  ① `python3 MECH/iss047_fov_table.py` → rc=0, FAIL 0 / WARN 0 (自检 10 条全过)
  ② `python3 MECH/iss047_doc_check.py` → 220 条 / 220 一致 / 0 不一致, rc=0
  ③ 文件 mtime 全部晚于派活时刻 (09:33) ⇒ 真交卷, 不是空回执
★状态机 (C2): open→fixing→fixed→verified→closed ⇒ 从 fixed 推到 verified (不许跳级到 closed)
★写入用 yaml.safe_dump + tmp+os.replace 原子写 (MEMORY: YAML 一律 safe_dump)
"""
from __future__ import annotations

import os
import sys

import yaml

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
LOG = f"{PROJ}/state/issue_log.yaml"

VERIFY_RESULT = (
    "2026-11-02 18:4x 项目总工独立验收通过 (verify_by=main, owner=mech-lead, 验证分离成立)。\n"
    "★验收依据全部机械复算, 不看交卷回执:\n"
    "  ① `python3 MECH/iss047_fov_table.py` → rc=0, FAIL 0 / WARN 0 (自检 10 条全过, 含「现行定案俯角30° 名义+1.80 但扣遮挡后-0.11 ⇒ 正前方被镜框上沿遮掉」这条新发现); \n"
    "  ② `python3 MECH/iss047_doc_check.py` → 220 条 / 220 一致 / 0 不一致, rc=0 (文档里的数不许靠人眼核对);\n"
    "  ③ 文件 mtime: MECH/ISS047_FOV_TABLE.md 09:57 / MECH_BUDGET.md 09:56 / HANDOFF/2026-11-02_mech-lead_ISS047_FOV俯角表复核.md 09:56 / state/fragments/mech.yaml 09:54 ⇒ 全部晚于派活时刻 09:33 ⇒ 真交卷。\n"
    "★验收结论: hw-lead 的指摘成立, 旧表整表作废 —— 且比它指出的更糟, 旧表错三处 (①主错: 拿对角半角判垂直俯角, 直行口径16:9对角100°下垂直半视场只有30.30°, 旧结论40°高估9.70° ②垂直俯角与水平偏置混在同一列比 ③对角FOV不带投影模型, 直行vs等距差10.75°)。\n"
    "★基线已按老板 11-02 09:41「使用D」重算: AR0234CS 1920x1200@60 整幅不裁剪 + 等距120° ⇒ f=3.2432mm / 垂直半视场31.80° / 水平半视场50.88° (与 SW fov_scale_check.py + hw-lead 分片三方一致)。\n"
    "★口径已由项目总工裁决 (判据 B', 见 pm.yaml answer key=iss047_margin_criterion_decision): 有效余量>=4° ⇒ 俯角上限<=25.89°, 设计点25°, h_max(d=30/32/35)=13.99/14.92/16.32mm ⇒ ★结构基线不变, 换 sensor 不推翻结构, 只多给2.27°造型自由度。\n"
    "★诚实边界: 本单 [实测] 条数 = 0 (0件打印件 / 0片镜头样片 / 镜头未下单), 遮挡角1.91°是几何推算 ⇒ 打印件出来后必须实测复核。\n"
    "★两条上游口径不一致已登记 (需 hw-lead 回写, 不卡本单): ① HW/DISPLAY_SENSOR_CHAIN.md 路线C 的 f=1.2704mm 是直行口径(等距需2.1015mm)且垂直半视场29.53°取自全幅(裁切窗口应29.42°) ② 路线D 旧写116.75°/28.62° 是裁切口径, 现行整幅应为120.00°/31.80°。"
)

NOTE_APPEND = (
    "\n\n★2026-11-02 18:4x 项目总工独立验收 (verify_by=main ≠ owner=mech-lead) ⇒ "
    "状态 fixed→verified。★验收依据 = `MECH/iss047_fov_table.py` rc=0 FAIL0/WARN0 + "
    "`MECH/iss047_doc_check.py` 220/220 一致 rc=0 + 文件 mtime 全部晚于派活时刻(真交卷)。"
    "★口径裁决已落 pm.yaml answer (key=iss047_margin_criterion_decision): 判据 B' 有效余量>=4° ⇒ "
    "俯角上限 <=25.89°, 设计点 25°, h_max(d=30/32/35)=13.99/14.92/16.32mm ⇒ 结构基线不变。"
    "★[实测] 条数仍 = 0 (0件打印件/0片镜头样片) ⇒ 遮挡角1.91° 是几何推算, 打印件出来后必须实测复核。"
    "★两条上游口径不一致 (DISPLAY_SENSOR_CHAIN 路线C 三数混两口径 / 路线D 旧裁切口径) 已登记待 hw-lead 回写。"
)


def main() -> int:
    with open(LOG, encoding="utf-8") as f:
        log = yaml.safe_load(f) or {}
    issues = log.get("issues") or []
    hit = 0
    for it in issues:
        if it.get("id") != "ISS-047":
            continue
        hit += 1
        if it.get("status") not in ("fixed", "verified"):
            print(f"⚠️ ISS-047 当前 status={it.get('status')} —— 非 fixed/verified, 不动", file=sys.stderr)
            return 1
        it["status"] = "verified"
        it["verify_result"] = VERIFY_RESULT
        it["verify_date"] = "2026-11-02"
        it["verify_by"] = "main"
        it["note"] = (it.get("note") or "") + NOTE_APPEND
    if hit != 1:
        print(f"❌ 找到 {hit} 条 ISS-047, 期望 1 条", file=sys.stderr)
        return 1

    tmp = LOG + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, LOG)
    print("✅ ISS-047 → verified (verify_by=main, verify_date=2026-11-02), issue_log.yaml 原子写完成")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
