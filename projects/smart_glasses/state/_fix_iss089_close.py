#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""队列解堵: 关 ISS-089 (mech-lead 已交卷但状态卡在 fixing) + 登记 mech 侧 pcb_mounting 冲突更正单
—— 2026-10-28 18:3x 项目总工 cron (队列自动派活)

★为什么要做:
  1) ISS-089 (owner=mech-lead) 08:56 已交卷 (HANDOFF 20.8KB B1-B6 + MECH/HW_CROSS_REVIEW.md 30KB
     + hw_cross_review_check.py 54 项机器判定 rc=0), 但 issue_log 里 status 一直挂 **fixing**。
     ★advance.py 的 in_flight 规则 = "同一 agent 名下只要有 status==fixing 的 issue, 该 agent 本轮不再派新活"
     ⇒ 这条僵尸 fixing **把 mech-lead 名下 11 条 open 待办全挡住了** (队列断线, 正是本 cron 要治的病)。
  2) 合并器长期报 `pcb_mounting` 冲突 (hw-lead PIN-SET-2 vs mech-lead 旧值 2xM1.2+1x⌀2.0H7)。
     上轮 cron 已对 boss 承诺"下一轮直接派" ⇒ 现登记为正式 issue (ISS-107), 走 advance.py 正常派活路径。

★原子写 (tmp + os.replace), 禁止 open(p,"w") 覆盖 (AGENTS.md 写文件铁律)。
"""
import os
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
TODAY = "2026-10-28"

with open(LOG, encoding="utf-8") as f:
    doc = yaml.safe_load(f)

issues = doc.get("issues")
if isinstance(issues, dict):
    items = list(issues.values())
else:
    items = list(issues)

# ---------------- 1) 关 ISS-089 (fixing -> verified) ----------------
# 验收依据 (项目总工亲自核过, 不是照抄交卷自评):
#   - HANDOFF/2026-10-28_mech-lead_风险复核_ISS089_硬件交叉评审.md = 20803 B, B1~B6 六块齐全
#   - MECH/HW_CROSS_REVIEW.md = 30104 B / MECH/hw_cross_review_check.py = 28374 B
#   - python3 MECH/hw_cross_review_check.py -> rc=0, 汇总 PASS 15 / FAIL 16 / 条件通过 8 / 说明 15 (共 54 项)
#   - state/fragments/mech.yaml 有 6 条 ISS-089 相关 needs_from + 产出/claims 齐全
#   - merge rc=0 (产出 70 | 阻塞 31/高危 25 | 冲突 1) / gate_check Q1 18/18 (mech-lead 6/6)
# ★注意 FAIL 16 项是"按现在的图纸做出来会出问题", 不是"交卷不合格" —— 交卷本身就是挑出这些点的。
CLOSE_NOTE = (
    "★2026-10-28 18:3x 项目总工 cron 解堵验收关单 (不是新活, 是补上 owner 漏掉的状态推进)。\n"
    "【为什么现在关】mech-lead 08:56 已交卷 (HANDOFF 20.8KB B1-B6 + MECH/HW_CROSS_REVIEW.md 30KB + "
    "hw_cross_review_check.py 54 项机器判定 rc=0), 但 issue_log 里 status 一直卡在 **fixing** —— 而 "
    "**advance.py 的 in_flight 规则规定「同一 agent 名下只要有 status==fixing 的 issue, 该 agent 本轮就不再派新活」** "
    "⇒ 这条僵尸 fixing 实际把 mech-lead 名下 **11 条 open 待办全挡在队列外** (ISS-017/024/025/027/047/052/065/066/076/092/103), "
    "队列断线。现按项目总工验收 (verify_by=main ≠ owner=mech-lead, 验证分离成立) 置 verified。\n"
    "【验收依据 (项目总工亲核, 非照抄交卷自评)】HANDOFF/2026-10-28_mech-lead_风险复核_ISS089_硬件交叉评审.md = 20803 B 且 B1~B6 六块齐全; "
    "MECH/HW_CROSS_REVIEW.md = 30104 B; MECH/hw_cross_review_check.py = 28374 B; "
    "实跑 `python3 MECH/hw_cross_review_check.py` → rc=0, 汇总 **PASS 15 / FAIL 16 / 条件通过 8 / 说明 15 (共 54 项)**; "
    "state/fragments/mech.yaml 已落 6 条 ISS-089 相关 needs_from + 产出/claims; merge rc=0 (产出 70 | 阻塞 31/高危 25 | 冲突 1); "
    "gate_check Q1 18/18 (mech-lead 6/6)。\n"
    "【交卷要点 (供后续拍板, 不重复展开)】① 跨铰链 4 组通道腔体本身放得下 (V 向余 7.00mm / 径向余 1.25mm / 面积 900 vs 909.72mm² 已闭合), "
    "但 **P9 页堆叠数自相矛盾 (26.5/27.0/31.00 三数并存) + 漏 4×2×0.50mm 走线边距 + 净高分母用已作废的 37.00 (现行 38.00)** "
    "⇒ 报的余量偏乐观 3.50mm (A-5 判不通过)。② **全合并成 1 个连接器 = 几何否决** (54p 座体 Y 30.00 > 板宽 15.00 + 接触排沿 V 被竖直铰链轴物理锁死), "
    "部分合并 14p 结构可行但 X 缺口仍 0.50mm ⇒ **建议不合并**。③ Type-C 座开孔单边 Y 向仅 0.17mm, FDM ±0.30 吃掉 0.13, 与 M-15 的 ±0.10 差 3.0× "
    "⇒ 建议开口放大到 10.0×4.2mm 或改金属嵌件 (A-7 判不通过)。④ **ICHG=IIN×0.822 方向反了** (buck 功率守恒是 Pout=η·Pin ⇒ 系数 1.216), "
    "连带 390Ω 档单 pin 0.50-0.61A **超 0.5A 额定** ⇒ 判据要重算。⑤ 充电灯 D_CHG_LED/Q_CHG_LED/R_CHG_LED board 列标 MAIN_PCB, "
    "但 VBUS_5V_CHG 只存在于充电板 ⇒ **board 列标错** (BOM 备料/装配/ISS-103 导光孔位置会跟着做错)。⑥ 打印包 temple_cage_340.stl 的 Type-C 试样还挂在镜脚检具上 "
    "(充电板已按 ISS-014 决策 5 挪镜框)。⑦ 端件沿臂导热阻 ≈1944 K/W (打印件 k=0.2) ⇒ 端件无金属导热路径。\n"
    "【诚实边界】实物类 [实测] = 0; 4 项 [0数据] 未编造 (u8 镜框截面 / Type-C 插拔力规格 / 厂商尺寸图 / 对手请求项); "
    "自评 ✅通过 10 / ⚠️条件通过 6 / ❌不通过 2 (A-5 / A-7 已在 §5 给处置路线, 走项目总工与 hw-lead 决策); "
    "其中 u8 镜框截面已请求升为阻塞级 (框侧要同时装 充电板 25×10 + Type-C 沉板 + 铝屏蔽罩 + 铰链件 + 4 条跨铰链 FPC 固定段, "
    "合计 V 向带宽 31.00mm, 而 u8 截面未给 ⇒ 镜框端件装不下与否**仍未知**)。"
)

# ---------------- 2) 登记 ISS-107 (mech 侧 pcb_mounting 冲突更正) ----------------
NEW_ISSUE = {
    "id": "ISS-107",
    "title": "★更正 mech-lead 分片 pcb_mounting 旧取值 (2xM1.2+1x⌀2.0H7 → PIN-SET-2: 2x⌀2.0H7+2x⌀1.4) —— 合并器长期报冲突",
    "severity": "high",
    "source_blocker": None,
    "source_agent": "main",
    "desc": (
        "合并器 (`state/merge.py`) 长期报唯一 1 条冲突: `pcb_mounting` = {hw-lead: 'PIN-SET-2:2x⌀2.0H7+2x⌀1.4', "
        "mech-lead: '2xM1.2+1x⌀2.0H7'}。\n"
        "【为什么必须改 mech 侧 (不是 hw 侧)】hw-lead 已在 ISS-049 交卷里把老口径 **机械判死**: "
        "在 15mm 板宽下老口径 3/3 孔压带 (M1.2 压 Y 0.50mm; ⌀2.0 压 2.00×2.00mm) ⇒ 加宽不解, 必须沿板长移出 SoC 逃线带 "
        "X[20.20, 31.80]。定版 PIN-SET-2 = P1 主定位销孔 ⌀2.0 H7 @ (8.00, 7.50) / P2 副定位销孔 ⌀2.0 H7 @ (52.00, 7.50) "
        "(菱形销, 只定 Y 消过定位) / S1 S2 压紧螺钉孔 ⌀1.4 @ (8.00, 2.50) 与 (52.00, 12.50), "
        "4/4 孔与逃线带 2D 重叠 = 0.000mm² (36 项复算 rc=0)。**hw-lead 的值是新的, mech 的值是旧的** ⇒ 改 mech 侧。\n"
        "【代价】不改 ⇒ merge 一直红 (冲突 1) ⇒ gate_check/daily_check 都被这条脏数据挂着, 合并器的冲突检测能力形同虚设。\n"
        "【边界】只改 mech-lead 自己的分片取值 (state/fragments/mech.yaml) + MECH/ 里引用老口径的那处文档; "
        "不改 hw-lead 的 HW/ 任何文件; 不改 netlist/BOM/生成器 (那是 hw-lead 的地界)。"
    ),
    "owner": "mech-lead",
    "reporter": "main",
    "raised": TODAY,
    "due": "2026-10-29",
    "status": "open",
    "external": False,
    "need_keys": [],
    "task_brief": (
        "把 mech-lead 分片里的 `pcb_mounting` 旧取值 **2xM1.2+1x⌀2.0H7** 改成 **hw-lead 已定版的 PIN-SET-2** = "
        "`2x⌀2.0H7+2x⌀1.4`, 让合并器的 `pcb_mounting` 冲突消掉 (现在它是唯一 1 条冲突)。\n"
        "【定版依据 (hw-lead ISS-049, 36 项复算 rc=0)】P1 主定位销孔 ⌀2.0 H7 @ (8.00, 7.50) (配压装 ⌀2.0 h6 圆销, 定 X+Y+θz); "
        "P2 副定位销孔 ⌀2.0 H7 @ (52.00, 7.50) (配压装 ⌀2.0 菱形销, 对边 1.94, 只定 Y ⇒ 消过定位); "
        "S1/S2 压紧螺钉孔 ⌀1.4 @ (8.00, 2.50) / (52.00, 12.50) (纯压紧, 零定位); "
        "板坐标 = 原点左下角, X=板长 0→60 (铰链端在 X=0), Y=板宽 0→15。\n"
        "【为什么老口径必须废掉】老口径 2×M1.2 @边距2.50 + 1×⌀2.0 H7 在 15mm 板宽下 **3/3 孔压带** "
        "(M1.2 压 Y 0.50mm; ⌀2.0 压 2.00×2.00mm) ⇒ 加宽不解, 必须沿板长移出 SoC 逃线带 X[20.20, 31.80]; "
        "PIN-SET-2 的 4/4 孔与逃线带 2D 重叠 = **0.000mm²**。\n"
        "【你要做的】① state/fragments/mech.yaml 里 `pcb_mounting` 改成 PIN-SET-2 (走 state/frag_write.py 原子写, 禁止 open(p,\"w\")); "
        "② 顺带核一遍 MECH/ 里还有没有别处引用老口径 (2xM1.2 / 1x⌀2.0H7 / 边距2.50), 有就一并更正; "
        "③ **只写你自己的文件** (MECH/ + state/fragments/mech.yaml + 你的 HANDOFF 交接单), 不碰 HW/、不改 netlist/BOM/生成器、"
        "不改别人的分片; ④ 交卷时把这条冲突的处置写进交接单, 并让 `python3 state/merge.py` 输出里的 **冲突数从 1 变 0** (贴输出)。\n"
        "★不要顺手改别的: 你自己 ISS-089 交卷里的 6 条 needs_from (u8 镜框截面升阻塞级 / 打印包改版授权 / DECISIONS 口径更正 等) "
        "走项目总工拍板, 不在本单范围。"
    ),
    "fix_ref": None,
    "verify_by": "main",
    "verify_result": None,
    "verify_date": None,
    "note": (
        "★2026-10-28 18:3x 项目总工 cron 登记 (解冲突 + 兑现上轮对 boss 的承诺: "
        "\"pcb_mounting 那条冲突要 mech-lead 把旧口径更新成 PIN-SET-2, 否则合并器一直报红 —— 这条我下一轮可以直接派\")。\n"
        "★背景: 本条与 ISS-089 解堵同批处理 —— ISS-089 卡在 fixing 把 mech-lead 名下 11 条 open 待办全挡住, "
        "解堵后本条是 mech-lead 名下**到期最早 + severity 最高**的一条, 由 advance.py 正常派发。"
    ),
    "dispatched_at": None,
}

changed = []
seen_ids = {i.get("id") for i in items}

for it in items:
    iid = it.get("id")
    if iid != "ISS-089":
        continue
    if it.get("status") not in ("fixing", "fixed"):
        print(f"⚠️ ISS-089 状态是 {it.get('status')}, 不是 fixing/fixed, 不动")
        break
    it["fix_ref"] = (
        "MECH/HW_CROSS_REVIEW.md + MECH/hw_cross_review_check.py + "
        "HANDOFF/2026-10-28_mech-lead_风险复核_ISS089_硬件交叉评审.md"
    )
    it["status"] = "verified"       # fixing -> fixed -> verified; owner 漏推 fixed, 本次由 main 补齐并验收
    it["verify_by"] = "main"        # ★验证分离: owner=mech-lead ≠ verify_by=main
    it["verify_result"] = "pass"
    it["verify_date"] = TODAY
    it["note"] = (it.get("note") or "") + "\n" + CLOSE_NOTE
    changed.append(iid)

if "ISS-107" not in seen_ids:
    items.append(NEW_ISSUE)
    changed.append("ISS-107 (new, open → mech-lead)")

if not changed:
    print("❌ 没有可改的条目")
    sys.exit(1)

doc["issues"] = items
text = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=120)
fd, tmp = tempfile.mkstemp(prefix="issue_log.yaml.", suffix=".tmp", dir=HERE)
try:
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, LOG)
except BaseException:
    try:
        os.unlink(tmp)
    except OSError:
        pass
    raise

print(f"✅ 已处理: {changed}")
print("   ISS-089 -> verified (verify_by=main, verify_result=pass, fix_ref 已落)")
print("   ISS-107 -> open, owner=mech-lead (pcb_mounting 冲突更正, due 2026-10-29)")
