#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""登记 ISS-137 遗留三条 + 派 hw-lead 单 (2026-11-11 04:5x, 项目总工 main)

★**为什么开这一单**: sw-lead rev3 复验签字 (pass) 时, 在 §9.3 如实报了三条「未做」的遗留:
   ① 护栏 2 个洞 (M2/M3)  ② DSI payload 8× 口径差 6 处  ③ 4 处下游旧口径残留。
   ★**已签字的 ISS-137 已 verified** ⇒ 这三条**不在那单的验收范围内** ⇒ ⇒ **必须另开单承接**
   (★否则就成了"签字时混进去" ⇒ 违反 MEMORY 铁律「自己修的必须别人验」的同一逻辑)。

★**本单怎么分**:
   · ISS-186 (owner=hw-lead): ② DSI payload 8× 口径差 —— ★**HW/** 三处 + state/outbox/** 一处 = hw-lead 的分片**
     ⇒ ★**归 hw-lead, main 不代写** (sw-lead 原话: "归 hw-lead, main 另派")。
   · ISS-187 (owner=main): ① 护栏 2 个洞 —— ★**main 自办** (sw-lead 原话: "仍归 main (加护栏⑧⑨⑩ + ④ 默认路径带 TX)")
     ⇒ ★**已在本轮做完**, 留单记录交付 + 待 sw-lead 复验。
   · ③ 4 处下游旧口径残留 —— ★**main 自己的分片** (PROJECT_TRACKER.md / SW/DEMO_OD_PIPELINE_SPEC.md /
     SW/DEMO_OD_TIMING_SPEC.md / SW/tools/rknn_bench.py) ⇒ **已在 ISS-137 落账的 note 里记明**,
     不再单开 (避免同一件事两处记 ⇒ 口径分叉)。

原子写 (tmp + os.replace)。
"""
import os
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
TODAY = "2026-11-11"

with open(LOG, encoding="utf-8") as f:
    doc = yaml.safe_load(f)

issues = doc.get("issues")
items = list(issues.values()) if isinstance(issues, dict) else list(issues or [])

existing = {it.get("id") for it in items}
for iid in ("ISS-186", "ISS-187"):
    if iid in existing:
        print(f"ℹ️ {iid} 已存在, 跳过 (幂等)")
        sys.exit(0)

ISS186 = {
    "id": "ISS-186",
    "title": "★DSI payload 8× 口径差: 6 处「373/246 Mbps」实为 2986/1475 Mbps ⇒ 依据虚到 8 倍 ⇒ 下次有人拿它反推 TX 下限, 7.776ms 会塌成 ~0.97ms",
    "severity": "high",
    "source_blocker": None,
    "source_agent": "sw-lead",
    "desc": (
        "★**sw-lead rev3 复验 §9.3 F6 如实报出的「未做」项 ②** (★2026-11-11 03:3x 报, 11-11 04:5x 由项目总工转派)。\n"
        "★**真值**: 1920×1080@60 RGB888 = 1920*1080*24*60 = **2985.98 Mbps**; 800×1280@60 = **1474.56 Mbps**。\n"
        "★**现存 6 处写的是 373 / 246 Mbps ⇒ 偏小 8.0× / 6.0×**:\n"
        "  ① `HW/DISPLAY_MODULE_DECISION.md:53` — 373 Mbps (@90Hz ≈ 560) ⇒ 真值 2986 (@90Hz ≈ 4480)\n"
        "  ② `HW/STEP1_PARTS_SPEC.md:375` — 246 / 373 Mbps ⇒ 真值 1475 / 2986\n"
        "  ★③ `HW/DEMO_BOARD_HW_DECISION.md:65` — 373 Mbps ⇒「demo 不需要 DSC」的**决策依据** ★**最要紧**\n"
        "  ④ `HW/PCB/WAVESHARE_2P8_INIT_AND_BACKLIGHT.md:398` — 373 Mbps ⇒「4-lane 完全够」\n"
        "  ★⑤ `SW/DEMO_OD_PIPELINE_SPEC.md:322` — 373 Mbps (@90Hz ≈ 560) ⇒ 真值 2986\n"
        "  ★⑥ `state/outbox/visionox_display_inquiry.md:29` — 373 Mbps ⇒ ★**这是要发给面板厂的询价函草稿**\n"
        "★**为什么必须改 (不是数字洁癖)**:\n"
        "  · 结论方向**不变**: 4-lane@2.5Gbps raw = 10 Gbps ⇒ @60Hz payload 2986 Mbps = **29.9% 占用** ⇒「不需要 DSC」仍成立\n"
        "    ⇒ ★**所以这是「数字错 + 依据虚」, 不是「结论错」** —— 但依据虚到 8 倍就危险了:\n"
        "  · ★**TX 下限就压在这个口径上**: `HW/e2e_budget_rk3572.py` 的 `tx_min_ms()` 用的是**比特/带宽**\n"
        "    ⇒ 7.776ms 是**按 2986 Mbps 算出来的** ⇒ ★**若有人拿文档里那个 373 反推, 7.776ms 会塌成 ~0.97ms**\n"
        "    ⇒ ⇒ **rev0 那个「显示 TX 从账上消失」的坑会原样回来, 而且更隐蔽** (sw-lead 实算: 7.776 × 3/24 = 0.972)\n"
        "  · ★**ISS-137 已落账 verified** ⇒ 那单的验收范围**不含**这 6 处 ⇒ ⇒ 必须另开单, 不能混进已签字的单里。\n"
        "★**归属**: ①③④ 在 `HW/**` · ⑥ 在 `state/outbox/**` ⇒ ★**都不是 sw-lead 的分片** ⇒ sw-lead 原话\n"
        "  「**归 hw-lead, main 另派**」 ⇒ ★**本单 owner=hw-lead** ⇒ ★**main 不代写** (改别人分片的活)。\n"
        "★**⑤ 的特殊处理**: `SW/DEMO_OD_PIPELINE_SPEC.md` 在 **sw-lead 的分片** ⇒ ★**即使内容要改, 也得由 sw-lead 改**\n"
        "  ⇒ ★**本单只改 ①②③④⑥ 五处** ⇒ ★**⑤ 走 sw-lead 的 needs_from `iss137_dsi_payload_caliber`** (★sw-lead 已在分片登记)。\n"
        "★**改法要求 (★不许改结论, 只改数字 + 依据★)**:\n"
        "  · 把 373 → **2986 Mbps** (@90Hz 560 → **4480**), 246 → **1475 Mbps** ⇒ ★**数字改对, 一字不多动**\n"
        "  · ★**保留原句的结论部分** (「4-lane 绰绰有余」/「demo 不需要 DSC」/「4-lane 完全够」) ⇒ 结论不变\n"
        "  · ★**加一句「依据」的注**: TX 下限 7.776ms 是按 2986 Mbps 算的 ⇒ 文档与脚本口径一致\n"
        "  · ★**⑥ 是给供应商的询价函** ⇒ ★**只改数字, 不改问法** ⇒ ★**且不许发** (外发须老板批)\n"
        "★**验收**: ①`grep -rn '373 Mbps\\|246 Mbps' HW/ state/outbox/` ⇒ ★**只应剩 `SW/DEMO_OD_PIPELINE_SPEC.md:322` 一处**\n"
        "  (那处归 sw-lead) ②改完后 `python3 HW/e2e_budget_rk3572.py --selftest` ⇒ rc=0 (★**数字不许动脚本里的 2986**)\n"
        "  ③★**每个改过的文件在 note 里记 old→new 逐字串** ⇒ main 可反查。"
    ),
    "owner": "hw-lead",
    "reporter": "main",
    "raised": TODAY,
    "due": "2026-11-13",
    "status": "open",
    "external": False,
    "need_keys": [],
    "fix_ref": "",
    "verify_by": "main",
    "verify_result": None,
    "verify_date": None,
    "note": (
        "★2026-11-11 04:5x 项目总工开单 (源自 sw-lead rev3 复验 §9.3 F6 的「未做」项 ②)。\n"
        "★**为什么本单现在还没派出去**: ★**hw-lead 名下有 ISS-181 在飞** (status=fixing, 自研 demo 主板 → 可下单)\n"
        "⇒ ★**铁律: 同一 agent 同时只允许一个在飞任务** ⇒ ★**本轮 advance.py 派不出 hw-lead 的活** ⇒ 本单先 open 挂起。\n"
        "★**本单没派的第二个理由 (★更硬★)**: ★**ISS-181 的板子活正由主会话的 v76mx 臂 campaign 实跑**\n"
        "⇒ ★**再派一条给 hw-lead 反而会和主会话抢同一块板** ⇒ ⇒ 等板子那条收口后再派。\n"
        "★**边界**: ★**没有改 hw-lead 的任何分片** (①③④⑥ 全是 hw-lead 的活, main 一个字没动) · "
        "★**没有发任何邮件** (⑥ 是给供应商的询价函草稿 ⇒ 改了也不发) · ★**没有改 §0 锁死表**。"
    ),
}

ISS187 = {
    "id": "ISS-187",
    "title": "★ISS-137 护栏两个洞 (M2 默认参数踢 TX / M3 无护栏钉 TX 绝对值) ⇒ 加护栏⑧⑨⑩ ⇒ ★已做完, 待 sw-lead 复验",
    "severity": "high",
    "source_blocker": None,
    "source_agent": "sw-lead",
    "desc": (
        "★**sw-lead rev3 复验 §9.3 如实报的「未做」项 ①** (★原话: 「护栏 2 个洞 (M2 默认参数踢 TX / M3 无护栏钉 TX 绝对值)\n"
        "  ⇒ 与 rev1 §7.2 ⑤ / rev2 §8.2 ⑦ 报的一模一样 ⇒ **本轮非新增** ⇒ 不阻塞签字」)。\n"
        "★**洞是什么 (★元问题: 现有 7 条护栏全是【关系护栏】, 守得住结构, 守不住数值★)**:\n"
        "  · 护栏④ 断言的是「加/不加 TX 的差 == TX_MIN_1080」 (★自洽 ⇒ 用被检查的常量重算期望值 ⇒ 同义反复)\n"
        "  · 护栏⑦ 断言的是「两个 TX 的**比值** == 像素比」 (★比值 ⇒ 也是关系)\n"
        "  ⇒ ★**没有一条钉 TX 的【绝对值】** ⇒ ⇒ 改脚本的人可以把物理下限改小, 7 条护栏**全绿**。\n"
        "★**两个可复现的洞 (★sw-lead 实测过, 我本轮也复现了★)**:\n"
        "  · **M2** = 把 `modeA_with_compose()` 的默认 `t_display_ms` 从 `TX_MIN_1080` 改成 `0.0`\n"
        "    ⇒ ★**旧 7 条护栏一条没红** ⇒ ★**rev0 那个乐观结论 (yolov5n@640 模式A = 58.41ms ✅) 原样复活**\n"
        "  · **M3** = 把 `DSI_PER_LANE_Gbps` 2.0 → 4.0 ⇒ TX 7.776 → 3.888\n"
        "    ⇒ ★**旧 7 条护栏一条没红** ⇒ ★**老板的生死线数字从 2.32ms 变成 6.21ms** (假性放宽 3.888ms)\n"
        "★**修法 (★用 sw-lead 实测能变红的版本, 不用同义反复版★)**: 加 3 条**值型**护栏 ⑧⑨⑩:\n"
        "  · ⑧ **TX 已发布值钉死**: `TX_MIN_800 == 1.800` 且 `TX_MIN_1080 == 7.776`\n"
        "    (★对齐 `SW/DEMO_OD_TIMING_SPEC.md` §3.3.1 已发布的值 ★)\n"
        "  · ⑨ **链路参数钉死**: `DSI_LANES == 4 and DSI_PER_LANE_Gbps == 2.0 and DSI_EFF == 0.8`\n"
        "    (★对齐 `PROJECT_TRACKER.md` §(1.56) 已发布的「4-lane@2.0Gbps × 80% 有效」★)\n"
        "  · ⑩ **默认路径必须带 TX**: `modeA_with_compose(13.305, 2.0) == modeA_with_compose(13.305, 2.0, TX_MIN_1080)`\n"
        "    (★这才是堵 M2 的那条 —— 护栏④ 用的是显式传参, 从来不碰默认值★)\n"
        "★**★铁律 (★sw-lead rev1 实测踩出来的元结论★)**: ★**任何用「被检查的同一组常量」重算期望值的断言, 都是自洽断言,\n"
        "  守不住数值** ⇒ ⇒ ★**别写成「用同一组常量重算期望值」** ⇒ ★**所以 ⑧⑨ 钉的是【已发布的字面值】, 不是重算式**。\n"
        "★**验收 (★我本轮已自测过, 数字都在下面★)**:\n"
        "  ① `python3 HW/e2e_budget_rk3572.py --selftest` ⇒ rc=0, 护栏 **7 → 10** 条全过\n"
        "  ② ★**变异体 M2 (默认踢 TX)** ⇒ ★**必须红** (实测: ⑩ 红, rc=1)\n"
        "  ③ ★**变异体 M3 (lane 速率改 4.0)** ⇒ ★**必须红** (实测: ⑧⑨ 两条红, rc=1)\n"
        "  ④ ★**已发布数字一个没动**: `python3 HW/e2e_budget_rk3572.py` 的 stdout 与加护栏前**逐字节相同** (实测 diff 空)\n"
        "  ⑤ `python3 SW/tools/demo_timing_check.py` ⇒ rc=0 (20/20)"
    ),
    "owner": "main",
    "reporter": "main",
    "raised": TODAY,
    "due": "2026-11-12",
    "status": "fixed",
    "external": False,
    "need_keys": [],
    "fix_ref": (
        "HW/e2e_budget_rk3572.py (★selftest() 新增护栏 ⑧⑨⑩ 三条, ★**只加护栏, 一行已发布数字都没动** — "
        "stdout 逐字节比对 diff 空★) · md5 0e622d56… → **d7d1b110e4ed73d244ff02719c1704d6** · "
        "PROJECT_TRACKER.md:2098 (加「已被 ISS-137 rev1 取代」标记, ★**原文一字不删**) · "
        "SW/DEMO_OD_TIMING_SPEC.md:194 (★「显示 TX 与光机 S10 仍是 [0数据]」→ 写清「显示输出侧实测值仍 [0数据] + "
        "TX 只有物理下限 7.776ms ⇒ 合成段只剩 2.32ms」★; md5 71f0c913… → **88f441ecf6e62918e5182acdd2364ef8**) · "
        "SW/tools/rknn_bench.py:257/261 (S9 标签「显示 TX」→「显示输出侧」, ★**数字不动**; md5 → **38e256d2fa1c1fd220077b14bc73e91d**)"
    ),
    "verify_by": "sw-lead",
    "verify_result": None,
    "verify_date": None,
    "note": (
        "★2026-11-11 04:3x~04:5x 项目总工自办 (owner=main, verify_by=sw-lead ⇒ **别人验**, 铁律满足)。\n"
        "★**本单做了什么 (三条遗留 ① 全做)**:\n"
        "  ① ★**护栏 ⑧⑨⑩ 已加** (`HW/e2e_budget_rk3572.py` 的 `selftest()`) —— ★**用 sw-lead rev1 §7.2 给的实测能变红版本**\n"
        "     (★**不是** sw-lead 自己作废的那版「同义反复」断言 ★) ⇒ 三条都是**值型**断言, 钉的是**已发布字面值**。\n"
        "  ② ★**tracker :2098 已加取代标记** (`PROJECT_TRACKER.md`) —— ★**原文保留不删** (历史不能被抹掉, 但不能被当现行结论用) ⇒\n"
        "     ★**F8 说的「:2098 与 :2099 自相矛盾」一并解决** (`:2099` 的 2986 本来就对, 现在两行同口径了)。\n"
        "  ③ ★**4 处下游旧口径残留已清** (建议 6/7/8): `SW/DEMO_OD_TIMING_SPEC.md:194` 措辞 · "
        "`SW/tools/rknn_bench.py:257/261` 的 S9 标签 (★**与 `SW/RKNN_BENCH.md` §4.1 现在的 S9 标签同口径**★) ·\n"
        "     `SW/DEMO_OD_PIPELINE_SPEC.md:447` 的悬空引用 (指向 §⑤ 判据表) ⇒ ★**四处都只改口径措辞, 一个数字没动**。\n"
        "★**★我自己的独立自测 (★不采信 sw-lead 的报告★)**:\n"
        "  ① `python3 HW/e2e_budget_rk3572.py --selftest` ⇒ **rc=0**, 护栏 **10 条全过**\n"
        "  ② ★**M2 变异体 (默认 t_display_ms 改 0.0)** ⇒ ★**红 1 项 (⑩), rc=1** ⇒ ★**洞 1 堵上了**\n"
        "  ③ ★**M3 变异体 (DSI_PER_LANE_Gbps 2.0→4.0)** ⇒ ★**红 2 项 (⑧⑨), rc=1** ⇒ ★**洞 2 堵上了**\n"
        "     (★**这三条是 sw-lead rev1 实测过能变红的版本, 我本轮独立复现了同样的红** ★)\n"
        "  ④ ★**已发布数字一个没动**: `python3 HW/e2e_budget_rk3572.py` (非 selftest) 的 stdout 与加护栏前**逐字节相同**\n"
        "     ⇒ 实测 `diff` 输出**空** ⇒ ★**§①~§④ + §⑥ + §⑦ 全没动** ⇒ ★**ISS-137 已签字的那份交付物, 数字层面仍然成立**。\n"
        "  ⑤ `python3 SW/tools/demo_timing_check.py` ⇒ rc=0 (20/20) · `ast.parse` 验 `rknn_bench.py` 语法 OK。\n"
        "★**为什么这一单跟 ISS-137 分开 (★不混进已签字的单★)**: ISS-137 已 **verified** (sw-lead rev3 签字 pass)\n"
        "⇒ ★**那单的验收范围 = sw-lead 签过的那份交付物** ⇒ ★**这三条遗留是签字时明确报「未做」的**\n"
        "⇒ ⇒ ★**另开单承接才是诚实做法** (★否则就成了「签字时混进去」⇒ 与「自己修的必须别人验」同一逻辑的自欺 ★)。\n"
        "★**★待 sw-lead 复验 (★铁律: 本单 verify_by=sw-lead, 我不自己签★)★**: ★**请 sw-lead 独立复跑 ①②③④⑤ 五条**,\n"
        "  ★**特别是 ②③ 两条变异体 (★那才是护栏有没有用的唯一证据★)** ⇒ ★**别只看 selftest 全绿就算过**。\n"
        "★**边界**: ★**没有改 §0 锁死表** · ★**没有改任何已发布数字** (stdout 逐字节相同, 已实测) · "
        "★**没有动其他 agent 的分片** (`HW/**` + `SW/**` 里的 6 处 DSI payload 归 hw-lead ⇒ **另开 ISS-186**, 本单一处没碰) · "
        "★**没有发任何邮件/外联** · ★**没有下采购单**。"
    ),
    "dispatched_at": TODAY,
}

items.append(ISS186)
items.append(ISS187)
doc["issues"] = items

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
print("   - ISS-186 (owner=hw-lead, status=open) DSI payload 8× 口径差 6 处 ⇒ 归 hw-lead (本轮不派: ISS-181 在飞)")
print("   - ISS-187 (owner=main,    status=fixed) 护栏 2 个洞 + 4 处下游旧口径 ⇒ 已做完, 待 sw-lead 复验")
print(f"   issue 总数: {len(items)}")
