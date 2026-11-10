#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""关单脚本: ISS-137 (项目总工自办 —— 显示合成段从 T_FIXED 里单独打点) —— 2026-11-10 23:5x

★**为什么是"项目总工自办"**: issue_log 里 ISS-137 的 verify_by=sw-lead, note 写明
   "项目总工自办 ⇒ 别人验 (铁律)" ⇒ ⇒ 本单由项目总工 (moli/main) 实施, 交 sw-lead 复核。

原子写 issue_log.yaml (tmp + os.replace), 禁止 open(p,"w") 覆盖。
"""
import os
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")

with open(LOG, encoding="utf-8") as f:
    doc = yaml.safe_load(f)

issues = doc.get("issues")
if isinstance(issues, dict):
    items = list(issues.values())
else:
    items = issues

TODAY = "2026-11-10"
CLOSES = {
    "ISS-137": {
        "fix_ref": "HW/e2e_budget_rk3572.py (T_FIXED 五段拆分 + compose_max_for/compose_upper_bound + --t-compose-ms) + SW/DEMO_OD_TIMING_SPEC.md §3.3.1",
        "note": (
            "★2026-11-10 23:5x 项目总工自办 (owner=main, verify_by=sw-lead 复核) ⇒ 本单闭环。\n"
            "【为什么必须做】这单是**当前唯一能把 60ms 从[推算]变成[实测]的内部动作**, 且**不依赖任何外部回复** ⇒ "
            "板子还没到、供应商还没回, 它就能做。due 11-06 逾期 4 天 ⇒ 本轮补。\n"
            "【病根】T_FIXED = 34.00 是个**黑箱** (曝光→OD输入就绪 + 显示输出段 混在一起) ⇒ "
            "\"显示合成段占 T_FIXED 多少\" 永远是 [0数据] ⇒ §⑤ 只能做 0~60% 的**盲扫** ⇒ "
            "★**盲扫的毛病: 它回答不了\"板端到底要测出多少才算过\" ⇒ 板端测完了还是不知道算不算过 ⇒ 等于没测**。\n"
            "【交付】① `HW/e2e_budget_rk3572.py`: T_FIXED 按 RKNN_BENCH §4.1 的 S1~S10 明细**拆成五段** ⇒ "
            "T_PRE_EXPOSURE 24.67 (曝光块 E+R+S3) + T_DRAW 1.00 (S8 画框, 画的是采集帧 640×640 ⇒ 不随显示分辨率变) + "
            "T_COMPOSE 3.00 (S9 显示合成/缩放, ★**唯一随显示像素数变的一段**) + T_PANEL 5.00 (S10 光机逐帧延迟, 面板自身时序) + "
            "T_RESIDUAL 0.33 (反解余量) ⇒ **拆分恒等还原 34.00** (自测断言 < 1e-9) ⇒ ★**已发布的数字一个没动**。\n"
            "② 新增 compose_max_for(S5) ⇒ **可测判据**: 模式A ≤ 60ms ⇒ t_compose 测出 ≤ 多少才算过。\n"
            "   RK3572+yolov5s@640: 上限 **−2.69ms** (负数 ⇒ 不用测, 必不过) · RK3572+yolov5n@640: 上限 **10.09ms** · RK3572+yolov5s@320: 上限 **17.65ms**。\n"
            "③ 新增 --t-compose-ms <实测值> ⇒ ★**板端打一个点 ⇒ 一行命令出结论** (不用再自己算)。\n"
            "④ `SW/DEMO_OD_TIMING_SPEC.md` §3.3.1: 把判据表 + 测法 (阶段表第7段 wall clock, ★建议测 800×600 与 1920×1080 **两档** ⇒ 直接得缩放律) 写进板端照抄的位置。\n"
            "【★为什么 yolov5n 那行必须实测】线性上界 = 3.00ms × 4.32 = 12.96ms > 判据 10.09ms ⇒ "
            "★**最坏情况(缩放器跑满也不降本)不过线** ⇒ ⇒ **只有实测能区分** ⇒ ★**这正是本单存在的理由: 把\"不知道\"变成\"要测这一个数\"**。\n"
            "【★口径纪律】板端阶段表第7段 `t_compose` 的定义 (画完框的帧 → 显示帧就绪) 与 RKNN_BENCH §4.1 的 S9 标签"
            " (原文写\"显示 TX\") **不完全一致** (合成 vs TX) ⇒ ★**本单按 DEMO_OD_TIMING_SPEC §3.3 的映射 (t_compose ↔ S9) 对齐**, "
            "⇒ 板端实测值**直接代入、无需换算** ⇒ ★**不制造新的口径分叉** (MEMORY 铁律: 口径混用比数字错更贵)。\n"
            "【自证】`python3 HW/e2e_budget_rk3572.py --selftest` ⇒ rc=0 (原 4 条已发布数字复现 + ★**新增 6 条拆分护栏**: "
            "拆分恒等 / 判据↔算账互逆@4个S5 / 代入T_COMPOSE与旧模型逐位一致 / 线性上界>判据 ⇒ 真需要实测)。\n"
            "`python3 SW/tools/demo_timing_check.py` ⇒ rc=0 (20/20 全过, 规格结构未被本改动破坏)。\n"
            "【★边界】★**没有改 §0 锁死表** · ★**没有改任何已发布数字** (拆分恒等 ⇒ 旧模型逐位不变) · "
            "★**没有动其他 agent 的分片** (只写本单 fix_ref/note) · ★**没有发任何邮件/外联**。"
        ),
    },
}

changed = []
for it in items:
    iid = it.get("id")
    if iid in CLOSES:
        c = CLOSES[iid]
        if it.get("status") not in ("closed", "verified", "fixed"):
            it["status"] = "fixed"
            changed.append(f"{iid}: status → fixed")
        it["fix_ref"] = c["fix_ref"]
        it["note"] = (it.get("note", "") or "") + "\n" + c["note"]
        it["fixed_at"] = TODAY
        changed.append(f"{iid}: fix_ref + note 已写")

if not changed:
    print("⚠️ 没有匹配到要关闭的 issue (可能被别的会话先关了)")
    sys.exit(0)

# 原子写
fd, tmp = tempfile.mkstemp(dir=HERE, prefix=".issue_log.", suffix=".tmp")
try:
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        yaml.safe_dump(doc, f, allow_unicode=True, sort_keys=False, width=200)
    os.replace(tmp, LOG)
except Exception:
    if os.path.exists(tmp):
        os.unlink(tmp)
    raise

print("✅ 已原子写 issue_log.yaml:")
for c in changed:
    print("   -", c)
